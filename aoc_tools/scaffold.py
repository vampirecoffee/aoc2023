"""Basic scaffold."""

from __future__ import annotations

import argparse


def parse_file(filename: str) -> int:
    """Parse the file."""
    with open(filename) as f:
        for line in f:
            print(line)
    return 0


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
