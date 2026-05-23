import argparse
import os
import sys

from src.menu import ProfileMenu
from colorama import just_fix_windows_console
just_fix_windows_console()

import os
import sys

def is_probably_old_windows_console() -> bool:
    """
    Heuristic detection for old Windows console hosts.

    Returns True if we're probably running in:
    - old blue PowerShell
    - old cmd.exe host
    - legacy conhost

    Returns False for:
    - Windows Terminal
    - modern terminal environments
    - non-Windows systems
    """

    if os.name != "nt":
        return False

    # Windows Terminal sets this env var.
    if os.environ.get("WT_SESSION"):
        return False

    # VSCode terminal
    if os.environ.get("TERM_PROGRAM") == "vscode":
        return False

    # Some modern terminals expose TERM.
    term = os.environ.get("TERM", "").lower()
    if "xterm" in term or "ansi" in term:
        return False

    return True

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (will show spoilers!!)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Provide a seed for the random number generator."
    )
    return parser.parse_args()

def fix_formatting():
    just_fix_windows_console()

    if os.name == "nt":
        os.system("chcp 65001 > nul")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

def main() -> None:
    fix_formatting()

    if is_probably_old_windows_console():
        try:
            print()
            print("For best visual formatting, a modern terminal is recommended.")
            print("Windows Terminal is free from the Microsoft Store:")
            print("https://apps.microsoft.com/detail/9N0DX20HK701")
            print("After you install it, right-click GuidingEurydice.exe")
            print("and select Run with... and then select Windows Terminal.")
            print("It is NOT recommended to play on your current console.")
            print("If you proceed here, some text may be unreadable.")
            print("If you wish to proceed with your current setup, press <Enter>.")
            print("Otherwise, press Q to quit.")
            i = input("> ")
            if i.upper() == "Q":
                print("Goodbye.")
                raise SystemExit(0)
        except KeyboardInterrupt:
            raise SystemExit(0)

    args = parse_args()
    pm = ProfileMenu(debug=args.debug)

    try:
        pm.render()
    except KeyboardInterrupt:
        pm.profile.save()
        print("Goodbye")
        SystemExit(0)

if __name__ == "__main__":
    main()