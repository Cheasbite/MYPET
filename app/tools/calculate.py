from datetime import date, timedelta, datetime
import sqlite3
from ..checkdb import db_ro_mode

def payment_per_month_for_service(startYear: int, startMonth: int, startDay: int, year: int, month: int, frequency: int, expense: float):
    '''
    payment_for_month(startYear, startMonth, startDay, year, month, frequency, expense)

    Calculate recurring-payment details for a single service within a target calendar month.

    Given the date a recurring payment started, a fixed payment interval (in days), and the
    cost per payment, this works out how many payments fall inside the target month, the
    total cost for that month, the date of the first payment due in the month, and the date
    of the next payment after the month ends (useful for forecasting the following month).

    Parameters:
    - startYear, startMonth, startDay (int): the date the recurring payments began.
    - year, month (int): the target calendar month to calculate payments for.
    - frequency (int): days between consecutive payments. Must be > 0.
    - expense (float): cost of each individual payment. Must be >= 0.

    Returns:
    A dict with:
    - count (int): number of payments due in the target month. None on error.
    - total_cost (float): total expense for the month (expense × count). None on error.
    - first_payment (date): date of the first payment within the target month. None on error.
    - next_month_payment (date): date of the next payment after the target month ends. None on error.
    - message (str | None): error description if something went wrong; None on success.
      Always check this field before using the other values.

    Errors are returned as data (not raised) so the caller can read the message and
    correct its inputs instead of being interrupted by an exception.
    '''

    if frequency <= 0:
        return __formatter(None, None, None, None, "Frequency must be greater than 0!")

    if expense < 0:
        return __formatter(None, None, None, None, "Expense cannot be less than 0!")

    start = date(startYear, startMonth, startDay)
    target_month_start, target_month_end = __get_days_of_month(year=year, month=month)

    start_days = start.toordinal()
    target_start_days = target_month_start.toordinal()
    target_end_days = target_month_end.toordinal()

    if target_end_days < target_start_days:
        return __formatter(None, None, None, None, "The start of the month is greater than the end of the month!")

    k0 = max(0, -(-(target_start_days - start_days) // frequency))
    k1 = (target_end_days - start_days) // frequency
    count = max(0, k1 - k0 + 1)

    first_payment = date.fromordinal(start_days + k0 * frequency)
    next_month_payment = date.fromordinal(start_days + (k1 + 1) * frequency)

    total_cost = expense * count

    return __formatter(count, total_cost, first_payment, next_month_payment)

def payment_per_month(target_year: int, target_month: int):
    '''
    payment_per_month(target_year, target_month)

    Calculate the total expense for a target calendar month, broken down by expense type.

    This is the whole-database counterpart to payment_per_month_for_service: it reads every row
    of the Records table, converts each row's stored frequency label (e.g. "Once", "Daily",
    "Weekly", "Monthly") into an interval in days, and hands the row to
    payment_per_month_for_service to count how many payments fall inside the target month.
    Recurring rows (Weekly/Monthly) are therefore charged as often as they actually occur, and
    each row's cost is added to the running total of its type.

    The result holds the month's grand total plus one entry per expense type present in the
    database, so "how much did I spend this month?" and "how much on Grocery this month?" are
    both answered by a single call.

    Parameters:
    - target_year (int): year of the target calendar month.
    - target_month (int): month of the target calendar month (1-12).

    Returns:
    A flat dict:
    - total_cost (float): grand total for the target month, i.e. the sum of every type entry.
      None when the database query failed.
    - <type> (float): total for that expense type, keyed by the Records.type value exactly as
      stored (e.g. "Grocery", "Subscriptions"). A type whose rows have no payment due in the
      month appears as 0.0 instead of being omitted.
    - message (str): present only on failure, in which case total_cost is None. Check for this
      key before using the values.

    Notes:
    - Amounts are rounded to 2 decimal places, so total_cost equals the sum of the type entries.
    - A month-based frequency is converted using the number of days in the target month.
    - Errors are returned as data, not raised.
    - The database is opened read-only and always closed before returning.
    '''
    con = sqlite3.connect(db_ro_mode, uri=True)

    _, month = __get_days_of_month(target_year, target_month)
    target_month_days = month.day

    services = {}

    try:
        cursor = con.cursor()

        cursor.execute("SELECT type, expense, frequency, started_at FROM Records")

        for service, expense, label, started_at in cursor.fetchall():
            frequency = __frequency_to_days(label, target_month_days)

            format_date = datetime.strptime(started_at, '%Y-%m-%d %H:%M:%S')

            call = payment_per_month_for_service(
                startYear=format_date.year,
                startMonth=format_date.month,
                startDay=format_date.day,
                year=target_year,
                month=target_month,
                frequency=frequency,
                expense=expense,
            )

            cost = call.get("total_cost")

            if cost is None:
                return {"total_cost": None, "message": f"Could not calculate '{service}': {call.get('message')}"}

            services[service] = round(services.get(service, 0) + cost, 2)

    except sqlite3.Error as e:
        return {"total_cost": None, "message": f"Database error: {e}"}

    finally:
        if con: con.close()

    result = dict(services)
    result["total_cost"] = round(sum(services.values()), 2)

    return result

def __frequency_to_days(label: str, target_month_days: int) -> int:
    # Frequency labels look like "Once", "Daily", "3 Weekly" or "Monthly": digits are summed
    # and unit letters become days. "month" uses the target month's length, since that is the
    # month being totalled.
    frequency = 0
    for part in label.lower().split():
        if part.isdecimal(): frequency += int(part)
        if part.startswith("d", 0, 1) or part.startswith("o", 0, 1): frequency = frequency + 1 if frequency == 0 else frequency * 1
        if part.startswith("w", 0, 1): frequency = frequency + 7 if frequency == 0 else frequency * 7
        if part.startswith("m", 0, 1): frequency += target_month_days

    return frequency

def __get_days_of_month(year, month):
    target_month_start = date(year, month, 1)
    next_month_from_target = date(year + (month == 12), month % 12 + 1, 1)
    target_month_end = next_month_from_target - timedelta(days=1)

    return target_month_start, target_month_end

def __formatter(count, cost, first_payment, next_payment, message = None):
    response = {"count": count, "total_cost": cost, "first_payment": first_payment, "next_month_payment": next_payment, "message": message}

    return response

if __name__ == "__main__":
    res1 = payment_per_month_for_service(2026, 1, 17, 2026, 4, 3, 2.50)
    res2 = payment_per_month_for_service(2026, 1, 1, 2026, 8, 10, 10.50)

    res = payment_per_month(2026, 12)
    print(res)

