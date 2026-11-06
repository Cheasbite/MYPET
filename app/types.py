# Values that are type safe format
# or the default options will live here

from typing import Literal
from dataclasses import dataclass
import calendar
import datetime

@dataclass
class FreqFormat:
    Time: int
    Date: Literal["Days", "Weeks"] = "Days"

NAME = str
EXPENSE = float
TYPE = Literal["Grocery", "Utility", "Subscription"] | str
FREQUENCY = Literal["Daily", "Weekly", "Monthly"] | FreqFormat

def VerifyName(Value: NAME) -> str:
    if len(Value) < 1:
        raise ValueError("Length of name needs to be greater than 0")

    if Value.find('\\'):
        raise AssertionError("No backslashes")

    return Value

def VerifyExpense(Value: EXPENSE) -> float:
    if Value < 0:
        raise ValueError("Expense cannot be negative")

    return Value

def VerifyType(Value: TYPE) -> str:
    return Value

# Best to not pass in string for type safe
def VerifyFrequency(Value: FREQUENCY | str) -> str:
    """
    Do not pass in bare str that is not defined by Literal!
    str here is for lsp to not complain.
    """
    # Current year and month
    now = datetime.datetime.now()
    total_days = calendar.monthrange(now.year, now.month)[1]

    weeks = total_days % 7

    if type(Value) is FreqFormat:
        if Value.Time < 0:
            raise ValueError("Frequency time cannot be negative")

        if Value.Time > 31 and Value.Date == "Days":
            raise ValueError("Time of Days in Frequency cannot exceeds 31")

        if Value.Time > weeks and Value.Date == "Weeks":
            raise ValueError("Time of Weeks in FREQUENCY cannot exceeds 4")

        return f"{Value.Time} {Value.Date}"

    if not Value in ["Daily", "Weekly", "Monthly"]: raise AssertionError("Pass in what is defined by literal")

    # If your lsp says this is an error, ignore it
    return Value

