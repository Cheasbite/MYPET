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

    Calculate the total expense for the whole database within a target calendar month.

    Unlike payment_per_month_for_service, this function needs no service details from the
    caller: it reads every row of the Records table, converts each row's stored frequency
    label (e.g. "Once", "Daily", "Weekly", "Monthly") into an interval in days, and for each
    row delegates to payment_per_month_for_service to count how many payments fall inside the
    target month. The per-row totals are then summed, so recurring rows (Weekly/Monthly) are
    charged multiple times per month as they should be.

    Parameters:
    - target_year (int): year of the target calendar month.
    - target_month (int): month of the target calendar month (1-12).

    Returns:
    A dict with:
    - cost (float): total expense for the target month across all records. 0 when the database
      has no rows, or when no row has a payment due in that month.

    Notes:
    - A month-based frequency is converted using the number of days in the target month.
    - Database errors are printed rather than raised, and the affected rows are skipped; the
      caller therefore only ever receives the accumulated `cost` value.
    - The database is opened read-only and always closed before returning.
    '''
    con = sqlite3.connect(db_ro_mode, uri=True)
    res = []

    _, month = __get_days_of_month(target_year, target_month)
    target_month_days = month.day

    try:
        cursor = con.cursor()

        statement = "SELECT expense, frequency, started_at FROM Records"

        cursor.execute(statement)

        rows = cursor.fetchall()

        for row in rows:
            freq: list[str] = row[1].lower().split()

            frequency = 0
            for i in freq:
                if i.isdecimal(): frequency += int(i)
                if i.startswith("d", 0, 1) or i.startswith("o", 0, 1): frequency = frequency + 1 if frequency == 0 else frequency * 1
                if i.startswith("w", 0, 1): frequency = frequency + 7 if frequency == 0 else frequency * 7
                if i.startswith("m", 0, 1): frequency = frequency + target_month_days

            format_date = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            started_at = (format_date.year, format_date.month, format_date.day)

            format = {"expense": row[0], "frequency": frequency, "started_at": started_at}

            res.append(format)

    except sqlite3.Error as e:
        print(e)

    finally:
        if con: con.close()

    total_cost = 0
    for v in res:
        expense, frequency, started_at = v.get("expense"), v.get("frequency"), v.get("started_at")

        call = payment_per_month_for_service(
                startYear=started_at[0],
                startMonth=started_at[1],
                startDay=started_at[2],
                year=target_year,
                month=target_month,
                frequency=frequency,
                expense=expense,
                )

        count, cost = call.get("count"), call.get("total_cost")

        if count and cost: total_cost += count * cost

    return {"cost": total_cost}

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

