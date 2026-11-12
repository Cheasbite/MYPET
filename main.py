# This is where our main program will be that wrap the entire system
# Basically it's the central hub to run the entire system
from app import checkdb
from app.types import *
from util import colors, selector, table

# run this once on run
checkdb.check_db_exists()

colors.cprint("""
___  ____   _______ _____ _____
|  \\/  \\ \\ / / ___ \\  ___|_   _|
| .  . |\\ V /| |_/ / |__   | |
| |\\/| | \\ / |  __/|  __|  | |
| |  | | | | | |   | |___  | |
\\_|  |_/ \\_/ \\_|   \\____/  \\_/
""", 'RED')
colors.cprint(" MY Personal Expense Tracker", "YELLOW")

# Tasks start here
while True:
    # Always initially checking for whether the database has values
    # Might not be true, be sure to update this when you ADD or DELETE
    db_has_value = checkdb.check_db_has_values()
    try:
        name = input("What a larper: ")
        result = selector.arrow_selector(["Utility", "Sub", "Other"])
        result1 = selector.arrow_selector(["Daily", "Weekly", "Monthly", "Other"])
    except KeyboardInterrupt:
        exit(0)

