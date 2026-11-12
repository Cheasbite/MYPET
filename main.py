# This is where our main program will be that wrap the entire system
# Basically it's the central hub to run the entire system
from app import checkdb, checkAI
from app.types import *
from util import colors, selector, clear
from datetime import date
from app.funcs.summarize import basic_summary

# run this once on run
checkdb.check_db_exists()

# Does AI exist? (Local model only for now)
AI_EXIST = bool(checkAI.check_AI_exist())

# get the current date
today = date.today()

step1_statements = [
    "Add a new record",
    "Search records",
    "Summarize your records",
    "Delete records"
]

# Tasks start here
while True:
    colors.cprint("""
___  ____   _______ _____ _____
|  \\/  \\ \\ / / ___ \\  ___|_   _|
| .  . |\\ V /| |_/ / |__   | |
| |\\/| | \\ / |  __/|  __|  | |
| |  | | | | | |   | |___  | |
\\_|  |_/ \\_/ \\_|   \\____/  \\_/
    """, 'RED')
    colors.cprint(" MY Personal Expense Tracker", "YELLOW")

    print()

    # Always initially checking for whether the database has values
    # Might not be true, be sure to update this when you ADD or DELETE
    db_has_value = checkdb.check_db_has_values()
    try:
        print("Please choose an operation from below using the ", end='')
        colors.cprint("arrow key", "YELLOW")

        # The first step:
        step1 = selector.arrow_selector(step1_statements)

        # SUMMARY
        if step1 == step1_statements[2]:
            clear.clear()

            if not db_has_value:
                colors.cprint("Nothing to summarize!", "RED")
                continue

            if AI_EXIST:
                print("A local model was detected. You can choose to use them.")
                providers = [p.capitalize() for p in checkAI.check_AI_exist()]

                get_summary_opt = selector.arrow_selector([*providers, "Basic Summary"])

                if get_summary_opt == "Ollama":
                    clear.clear()

                    print("Choose a model!")
                    models = checkAI.use_AI("ollama")
                    if models == -1: continue

                    model = selector.arrow_selector(models)

                    clear.clear()

                    print("To exit, type exit or /bye")
                    while True:
                        try:
                            prompt = input(f"{colors.COLORS["GREEN"]}>>> {colors.COLORS["RESET"]}")

                            if prompt == "exit" or prompt == "/bye": break
                            if prompt == "": continue

                            checkAI.call_ollama(prompt, model)

                        except KeyboardInterrupt: exit(0)

                elif get_summary_opt == "Basic Summary":
                    clear.clear()
                    basic_summary(today=today)

            else: basic_summary(today=today)

        clear.clear()

    except KeyboardInterrupt: exit(0)

