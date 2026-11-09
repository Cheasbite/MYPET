from datetime import date, timedelta

def payment_for_month(startYear: int, startMonth: int, startDay: int, year: int, month: int, frequency: int, expense: float):
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

    try:
        start = date(startYear, startMonth, startDay)
        target_month_start = date(year, month, 1)
    except ValueError as e:
        return __formatter(None, None, None, None, f"Invalid date provided: {e}")

    next_month_from_target = date(year + (month == 12), month % 12 + 1, 1)
    target_month_end = next_month_from_target - timedelta(days=1)

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

def __formatter(count, cost, first_payment, next_payment, message = None):
    response = {"count": count, "total_cost": cost, "first_payment": first_payment, "next_month_payment": next_payment, "message": message}

    return response

if __name__ == "__main__":
    print(payment_for_month(2026, 1, 17, 2026, 4, -3, 2.50))

