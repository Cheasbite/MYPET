"""
=================================
    clear.py
================================

It just clears the terminal.
"""

import subprocess
import sys

clear = lambda: subprocess.call("cls" if sys.platform == "win32" else "clear", shell=True)

