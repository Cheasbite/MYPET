"""
=================================
    colors.py
================================

COLORS that you can use anywhere.

cprint is a simple print function that allows you to print with colors.
"""

from typing import Literal

COLORS = {
    'BLACK': "\033[30m",
    'RED': "\033[31m",
    'GREEN': "\033[32m",
    'YELLOW': "\033[33m",
    'LIGHTPURPLE': "\033[34m",
    'PURPLE': "\033[35m",
    'CYAN': "\033[36m",
    'LIGHTGRAY': "\033[37m",
    'RESET': "\033[0m",
}


def cprint(text: str,
           clr: Literal['BLACK', 'RED', 'GREEN', 'YELLOW', 'LIGHTGRAY', 'PURPLE', 'CYAN', 'LIGHTGRAY'],
           end="\n"
           ) -> None:
    """
    Color Print

    A function that just prints color :)
    """
    print(f"{COLORS[clr]}{text}\033[0m", end=end)

