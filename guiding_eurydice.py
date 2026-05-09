import argparse
import pathlib

from src.level import TextLevel

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
    args = parse_args()

    json_path = pathlib.Path("levels/level1.json")
    lvl1 = TextLevel.from_json(json_path, args.debug, args.seed)
    lvl1.run()

if __name__ == "__main__":
    main()