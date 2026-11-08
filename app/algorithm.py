from datetime import date, timedelta
from dataclasses import dataclass

@dataclass
class StartTime:
    """
    The start date of when the service had started.

    Used in payment_for_month.

    Parameters
    - Year: int
    - Month: int (The integer representation of the month eg. 1 for January)
    - Day: int
    """
    Year: int
    Month: int
    Day: int

def payment_for_month(startTime: StartTime, year: int, month: int, frequency: int, expense: float):
    start = date(startTime.Year, startTime.Month, startTime.Day)

    target_month_start = date(year, month, 1)
    next_month_from_target = date(year + (month == 12), month % 12 + 1, 1)
    target_month_end = next_month_from_target - timedelta(days=1)

    start_days = start.toordinal()
    target_start_days = target_month_start.toordinal()
    target_end_days = target_month_end.toordinal()

    if target_end_days < target_start_days: raise AssertionError("The start of the month is greater than the end of the month!")

    # Just a formula of calculating the how many should I pay quickly
    # Formula: start + k * N, where N is the frequency and k is multiplier of the frequency
    k0 = max(0, -(-(target_start_days - start_days) // frequency))
    k1 = (target_end_days - start_days) // frequency
    count = max(0, k1 - k0 + 1)

    first_payment = date.fromordinal(start_days + k0 * frequency)
    next_month_payment = date.fromordinal(start_days + (k1 + 1) * frequency)

    total_cost = expense * count

    return __formatter(count, total_cost, first_payment, next_month_payment)

def __formatter(count, cost, first_payment, next_payment):
    response = {"count": count, "total_cost": cost, "first_payment": first_payment, "next_month_payment": next_payment}

    return response

if __name__ == "__main__":
    start: StartTime = StartTime(2026, 1, 17)
    print(payment_for_month(start, 2026, 4, 3, 2.0))
    print(payment_for_month(start, 2026, 2, 3, 2.0))

