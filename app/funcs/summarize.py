"""
=================================
    summarize.py
================================

This file is responsible for the summary feature of the APP.

Featuring 2 summary options:
    - Basic summary: create a nice table for all expense in all category types and your total
    - Summary with AI: Use your own AI to summarize your record based on what you need

Note:
    functions that begins with __ are private function that should not be used outside this file!
"""

import requests
from typing import Literal
from ..tools import calculate
from util import table, colors, clear, selector
from datetime import date
from ..checkAI import use_AI, call_ollama, call_gemini

def summary_with_AI(provider: Literal["Gemma", "Ollama"]):
    clear.clear()

    if provider == "Ollama":
        print("Choose a model!")
        models, _ = use_AI("ollama")
        if models == -1:
            return -1

        model = selector.arrow_selector(models)

        clear.clear()

        print("To exit, type exit or /bye")

        __loop(call_ollama, model)

    if provider == "Gemini":
        print("Choose a model!")
        models, api= use_AI("gemini")

        display_models = [m.get("displayName") for m in models]
        name_models = [m.get("model") for m in models]

        model = selector.arrow_selector(display_models)

        model = name_models[display_models.index(model)]

        url = "https://generativelanguage.googleapis.com/v1beta/interactions"

        clear.clear()

        print("To exit, type exit or /bye")
        colors.cprint("Note: ", "RED", end="")
        print("Google may see your interactions and logs are stored in your AI studio!")

        __loop(call_gemini, model, api, None, url)

    clear.clear()

    return 0

def basic_summary(today: date) -> None:
    header = ["Type", "Cost"]
    expenses = calculate.payment_per_month(today.year, today.month)
    row = []
    for exp in expenses:
        dummy = ["Total" if exp == "total_cost" else exp, f"${expenses[exp]}"]
        row.append(dummy)

    # The display part
    print(f"Below are your expense this month {today}: ")
    table.format_table(header, row)

    getKey = input(f"Continue? ({colors.COLORS["GREEN"]}Y{colors.COLORS["RESET"]}/n): ")
    if getKey and getKey.lower()[0] == 'n': exit(0)

def __loop(func, model, api=None, id=None, delete_url = None):
    id = id
    api = api
    try:
        while True:
            prompt = input(f"{colors.COLORS["GREEN"]}>>> {colors.COLORS["RESET"]}")

            if prompt == "exit" or prompt == "/bye": break
            if prompt == "": continue

            if api:
                id = func(prompt, model, api, id)
            else:
                func(prompt, model)

    except KeyboardInterrupt: exit(0)
    finally:
        if delete_url:
            requests.delete(f"{delete_url}/{id}")

