# This is where our main program will be that wrap the entire system
# Basically it's the central hub to run the entire system
from app import checkdb, checkAI
from app.types import *
from util import colors, selector, table
from datetime import date
from app.tools.calculate import payment_per_month

# run this once on run
checkdb.check_db_exists()

# Does AI exist? (Local model only for now)
ai = bool(checkAI.check_AI_exist())

# get the current date
today = date.today()

colors.cprint("""
___  ____   _______ _____ _____
|  \\/  \\ \\ / / ___ \\  ___|_   _|
| .  . |\\ V /| |_/ / |__   | |
| |\\/| | \\ / |  __/|  __|  | |
| |  | | | | | |   | |___  | |
\\_|  |_/ \\_/ \\_|   \\____/  \\_/
""", 'RED')
colors.cprint(" MY Personal Expense Tracker", "YELLOW")

step1_statements = [
    "Add a new record",
    "Search records",
    "Summarize your records",
    "Delete records"
]

# Tasks start here
while True:
    # Always initially checking for whether the database has values
    # Might not be true, be sure to update this when you ADD or DELETE
    db_has_value = checkdb.check_db_has_values()
    try:
        print("Please choose an operation from below using the arrow key")
        # The first step:
        step1 = selector.arrow_selector(step1_statements)

        if step1 == step1_statements[2]:
            header = ["Type", "Cost"]
            expenses = payment_per_month(today.year, today.month)
            row = []
            for exp in expenses:
                dummy = ["Total" if exp == "total_cost" else exp, str(expenses[exp])]
                row.append(dummy)

            # The display part
            print(f"Below are your expense this month {today}: ")
            table.format_table(header, row)

            getKey = input("Continue? (Y/n): ")
            if getKey and getKey.lower()[0] == 'n': exit(0)

    except KeyboardInterrupt:
        exit(0)

