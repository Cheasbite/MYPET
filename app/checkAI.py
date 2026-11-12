import os
import subprocess
import re
import json
from datetime import date
from .tools import calculate, list_record_field, search_record

__listing_fields = list_record_field.ListRecords()
AVAILABLE_TOOLS = {
    "list_record_fields": __listing_fields.list_record_field,
    "list_frequency_types": __listing_fields.list_unique_frequency,
    "list_type_types": __listing_fields.list_unique_type,
    "search_record": search_record.custom_search_records,
    "payment_per_month_for_service": calculate.payment_per_month_for_service,
    "payment_per_month": calculate.payment_per_month,
}

# Conversation history kept in memory for the life of the process. It is never
# written to disk; it only lets later prompts see earlier questions and tool results.
__conversation_history: list[dict] = []

def check_AI_exist() -> list[str]:
    return __get_providers()

def use_AI(providers: str):
    local_models = None
    if providers == "ollama":
        local_models = __get_local_model()
    else:
        print("Coming Soon!")
        return -1

    return local_models

def __get_local_model():
    result = subprocess.run(["ollama", "ls"], check=True, text=True, capture_output=True)
    local_models = re.findall(r"\n([^ ]+)", result.stdout.strip())

    return local_models

def __get_providers():
    keywords = ["ollama", "antropic", "openai", "gemini"]
    providers = []

    for key, val in os.environ.items():
        for kw in keywords:
            if kw in key.lower() or kw in val.lower():
                providers.append(kw)

    return providers

def __format_tool_function(name: str, description: str, params: object):
    tool = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": params,
            },
        }

    return tool

def __trim_history(history: list[dict], max_messages: int = 60) -> None:
    if len(history) <= max_messages:
        return

    # Always keep the system prompt at index 0 and cut on a user-message boundary
    # so an assistant tool_calls message is never separated from its tool results.
    while len(history) > max_messages:
        del history[1]

        while len(history) > 1 and history[1].get("role") != "user":
            del history[1]

def call_ollama(prompt: str, model: str = "gemma4:e4b"):
    import requests

    systemPrompt = (
        f"You are MYPET's expense assistant. Today is {date.today():%A, %d %B %Y}."

"        Workflow for questions about records:"
"        1. Call list_record_fields, list_type_types, and list_frequency_types to learn the schema."
"        2. Call search_record (or list_records) to find the relevant rows."
"        3. For a monthly total, call payment_per_month(target_year, target_month) — its result also breaks the month down per type; do not sum expense yourself,"
"           because recurring rows (Weekly/Monthly) are charged multiple times per month."
"        4. If ask for anything specific about which is the cost the most in a type, make sure to search the frequency and account for the frequency too"
"           since in a single month, those expenses can occur multiple time."

"        Rules:"
"        - Never invent dates, fields, record names, or amounts. Use the date above."
"        - Never INSERT/UPDATE/DELETE. The database is read-only."
"        - If a tool returns an error, read `message`, fix the arguments, retry once."
"        - If the data needed doesn't exist, say exactly what's missing."
"        - Plain text only (CLI), short and concise."

"        Example:"
"            1."
"                What is my montly expense for this month?"

"                Your monthly expense is $XXX, mostly contributed by Y because of the frequency spending which is twice a month costing $XX."

"                <you may ask your question here if needed but this example has none>"

"           2."
"                Can I reduce my spending in grocery and utility in this month?"

"                Those options are neccessary for everyday needs, which I cannot exactly give without additional context."
"                Checking your spending for both grocery and utility, they account towards 30% of the total spending this month. Therefore, I wouldn't suggest so."

"                If you can give me additional context about your reason and budget, I may be able to give a better recommendation or trying to find other services to reduce."
    )

    tools = [
        __format_tool_function(
            "payment_per_month_for_service",
            "SINGLE SERVICE (database not used). Given the start date, interval and cost of ONE "
            "recurring payment that you supply yourself, calculate its details in a target month: "
            "how many payments fall in that month, the total cost, the first payment date, and the "
            "next payment after the month ends. Use this for one specific service or a "
            "'what if' calculation. It does NOT read the database, so you must pass every "
            "argument from the record you already looked up. If you want the total for the whole "
            "database, use payment_per_month instead. "
            "Always check the returned `message` field "
            "before using the other values; errors come back as data, not exceptions.",
            {
                "type": "object",
                "properties": {
                    "startYear":  {"type": "integer", "description": "Year the recurring payments began."},
                    "startMonth": {"type": "integer", "description": "Month the recurring payments began (1-12)."},
                    "startDay":   {"type": "integer", "description": "Day the recurring payments began (1-31)."},
                    "year":       {"type": "integer", "description": "Target month's year."},
                    "month":      {"type": "integer", "description": "Target month (1-12)."},
                    "frequency":  {"type": "integer", "description": "Days between consecutive payments. Must be > 0."},
                    "expense":    {"type": "number",  "description": "Cost of each individual payment. Must be >= 0."},
                },
                "required": ["startYear", "startMonth", "startDay",
                             "year", "month", "frequency", "expense"],
            },
        ),
        __format_tool_function(
            "list_record_fields",
            "List the database fields of the Records table, each with its field name, SQL type, "
            "and description. Call this before searching or reading columns.",
            {"type": "object", "properties": {}},
        ),
        __format_tool_function(
            "list_frequency_types",
            "List all distinct expense frequency values (e.g. Weekly, Once, Monthly) present in the records.",
            {"type": "object", "properties": {}},
        ),
        __format_tool_function(
            "list_type_types",
            "List all distinct expense type values (e.g. Dining, Grocery, Subscriptions) present in the records.",
            {"type": "object", "properties": {}},
        ),
        __format_tool_function(
            "search_record",
            "Run a read-only SELECT-style SQL query against the expense database, with LIMIT/OFFSET "
            "appended. No semicolons allowed. Returns rows as tuples, or a single error string on failure.",
            {
                "type": "object",
                "properties": {
                    "search": {"type": "string",  "description": "The SQL query, e.g. \"SELECT * FROM Records WHERE type = 'Grocery'\". Must not contain ';'."},
                    "limit":  {"type": "integer", "description": "Maximum rows to return (default 50)."},
                    "offset": {"type": "integer", "description": "Rows to skip before returning results (default 0)."},
                },
                "required": ["search"],
            },
        ),
        __format_tool_function(
            "payment_per_month",
            "MONTHLY TOTAL BY TYPE (reads the database). Calculate spending for one calendar month: "
            "returns the grand total under \"total_cost\" plus one key per expense type with that "
            "type's own total, e.g. {\"total_cost\": 245.5, \"Grocery\": 200.0, "
            "\"Subscriptions\": 45.5}. It reads every record itself, converts each stored frequency "
            "label (Once/Daily/Weekly/Monthly) into payments inside that month, and sums them, so "
            "recurring rows are counted as often as they occur. Use it for both 'how much did I "
            "spend this month' (read total_cost) and 'how much on Grocery this month' (read that "
            "type's key) — no need to pass types. A type with no payment due that month appears as "
            "0.0; null values plus a `message` key mean an error. Amounts are rounded to 2 decimals. "
            "Do not pass service details; use payment_per_month_for_service for a single "
            "hand-supplied service.",
            {
                "type": "object",
                "properties": {
                    "target_year":  {"type": "integer", "description": "Year of the month to total."},
                    "target_month": {"type": "integer", "description": "Month to total (1-12)."},
                },
                "required": ["target_year", "target_month"],
            },
        ),
    ]

    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}

    if not __conversation_history:
        __conversation_history.append({"role": "system", "content": systemPrompt})

    __trim_history(__conversation_history)
    __conversation_history.append({"role": "user", "content": prompt})

    messages = __conversation_history
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "think": True,
        "options": { "temperature": 0 }
    }

    # Allow the model to chain a few tool calls before it must answer.
    for _ in range(20):
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return

        message = response.json().get("message", {})
        tool_calls = message.get("tool_calls") or []

        # No tool requested anymore: this is the final answer.
        if not tool_calls:
            messages.append({
                "role": "assistant",
                "content": message.get("content") or "",
            })
            print("Model Response:", message.get("content"))
            return

        # Keep the assistant turn (it carries the tool_calls) in the history.
        messages.append(message)

        for call in tool_calls:
            function = call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments") or {}

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            func = AVAILABLE_TOOLS.get(name)

            if func is None:
                result = {"error": f"Unknown tool '{name}'. Available tools: {AVAILABLE_TOOLS.keys()}"}
            else:
                try:
                    result = func(**arguments)
                except Exception as e:
                    result = {"error": f"Tool '{name}' failed: {e}"}

#            print(f"--- tool: {name} ---")
#            print(json.dumps(result, indent=2, default=str))

            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": json.dumps(result, default=str),
            })

    print("Stopped: the model kept calling tools without producing an answer.")

if __name__ == "__main__":
    while True:
        prompt = input(">>> ")

        if prompt == "exit" or prompt == "/bye": break

        call_ollama(prompt)

