from ..tools import calculate
from util import table, colors
from datetime import date

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

