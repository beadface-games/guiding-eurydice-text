import argparse
import os
import sys

from src.menu import ProfileMenu
from src._utils import TextUtility

import os
import sys



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

def main() -> None:
    TextUtility.fix_formatting()
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