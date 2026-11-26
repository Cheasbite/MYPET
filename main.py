# This is where our main program will be that wrap the entire system
# Basically it's the central hub to run the entire system
from app import checkdb, checkAI
from app.types import *
from util import colors, selector, clear
from datetime import date
from app.funcs.summarize import basic_summary, summary_with_AI
import re 

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
    "Delete records",
    "Exit"
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
        #add record
        if step1 == step1_statements[0]:
            clear.clear()

            name = input("Enter Record's Name:")
            
            default_types = ["Grocery", "Utility", "Subscription", "Custom Type"]
            print("Select Record's Type")
            
            types = selector.arrow_selector(default_types)
            
            if types == "Custom Type":
                types = input("Enter Record's Type:")
                
            expense = 0
            while True:
                try: 
                    expense = float(input("Enter Record's Expense:"))
                    if expense < 0:
                        raise AssertionError
                    break
                except ValueError:
                    colors.cprint("Enter a valid number!", "RED")
                except AssertionError:
                    colors.cprint("Expense cannot be less than 0!", "RED")
                except Exception as e:
                    colors.cprint("Error", "RED")
                    
            default_frequency = ["Daily", "Weekly", "Monthly", "Custom Frequency"]        
            print("Select Record's Frequency")
            frequency = selector.arrow_selector(default_frequency)
            if frequency == "Custom Frequency":

                while True:
                    try:   
                        frequency = input("Enter Record's Frequency (integer [d or w]):")
                        if frequency == "": raise AssertionError("Frequency cannot be empty!")
                    
                        match = re.findall(r"(\d+)\s*([A-Za-z])?", frequency)
                        if not match: raise AssertionError("Please enter a valid frequency (e.g. 2 d, 3 w)!")
                        fmatch = match[0]
                        number, day= *fmatch
                        if number == "0": raise AssertionError("Frequency cannot be 0!")
                        if day not in ["d", "w", ""]: raise AssertionError("Please enter a valid frequency (e.g. 2 d, 3 w)!")
                        
                        if day == "w" :
                            frequency = number + " week"
                        if day in ["d", ""]:
                            frequency = number + " day"
                            
                    except ValueError:
                        colors.cprint("Enter a valid date!", "RED")
                    except Exception as e:
                        colors.cprint(f"Error, {e}", "RED")
        
        # SUMMARY
        if step1 == step1_statements[2]:
            clear.clear()

            if not db_has_value:
                colors.cprint("Nothing to summarize!", "RED")
                continue

            if AI_EXIST:
                print("A model provider was detected. You can choose to use them.")
                providers = [p.capitalize() for p in checkAI.check_AI_exist()]

                get_summary_opt = selector.arrow_selector([*providers, "Basic Summary"])

                if get_summary_opt != "Basic Summary":
                    s = summary_with_AI(get_summary_opt)

                    if s == -1 or s == 0: continue

                clear.clear()
                basic_summary(today=today)

            else: basic_summary(today=today)

        if step1 == "Exit": exit(0)

        clear.clear()

    except KeyboardInterrupt:
        exit(0)

