# This is where our main program will be that wrap the entire system
# Basically it's the central hub to run the entire system
from app import checkdb

# run this once on run
checkdb.check_db_exists()

print("""
___  ____   _______ _____ _____
|  \\/  \\ \\ / / ___ \\  ___|_   _|
| .  . |\\ V /| |_/ / |__   | |
| |\\/| | \\ / |  __/|  __|  | |
| |  | | | | | |   | |___  | |
\\_|  |_/ \\_/ \\_|   \\____/  \\_/

 MY Personal Expense Tracker
""")

# Tasks start here

