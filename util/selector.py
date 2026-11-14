"""
=================================
    selector.py
================================

Allow the user to use the arrow key to select from list of options in the terminal.

Example:
 > Add a new record (Note: This would be highlighted cyan)
   Search records
   Summarize your records
   Delete records
   Exit
"""

import sys
from .colors import COLORS

def arrow_selector(options: list[str] | tuple[str, ...]) -> str:
    """
    Arrow Selection option

    Use this to format the output as a selection of option.
    """
    total_opts = len(options)
    curr = 0

    # Initially spaced the options out correctly
    for _ in range(total_opts):
        print()

    try:
        while True:
            # Continuosly re-spaced them
            sys.stdout.write(f'\033[{total_opts}A')

            for i, opt in enumerate(options):
                if i == curr:
                    sys.stdout.write(f' {COLORS["CYAN"]}> {opt}{COLORS["RESET"]}\n')
                else:
                    sys.stdout.write(f'   {opt}\n')

            key = __get_key_pressed()
            if key == "UP": curr = (curr - 1) % total_opts
            if key == "DOWN": curr = (curr + 1) % total_opts
            if key == "INTERRUPT": raise KeyboardInterrupt()
            if key == "ENTER": return options[curr]
    except KeyboardInterrupt:
        sys.exit(0)

def __get_key_pressed():
    if sys.platform == 'win32':
        import msvcrt # for window support
        ch = msvcrt.getch()

        if ch in (b'\x00', b'\xe0'):
             ch1 = msvcrt.getch()

             if ch1 == b'H': return "UP"
             if ch1 == b'P': return "DOWN"
             elif ch == b'\r': return "ENTER"

        # best guess to capture CTRL+C in window
        if ord(msvcrt.getch()) == 3: return "INTERRUPT"
    else:
        import termios
        import tty
        # access the stdin 0
        fd = sys.stdin.fileno()

        # to reset the terminal mode
        old_settings = termios.tcgetattr(fd)

        try:
            # go lower to capture the raw input
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            if ch == '\x1b':
                ch1 = sys.stdin.read(1)
                ch2 = sys.stdin.read(1)

                if ch1 == '[':
                    if ch2 == "A": return "UP"
                    if ch2 == "B": return "DOWN"
            elif ch in ['\r', '\n']: return "ENTER"
            elif ch == '\x03': return "INTERRUPT"
        finally:
            # Error prevention
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

