"""Part 1 of the hash problem."""

from __future__ import annotations

import argparse
import functools


@functools.cache
def hash_char(c: str, start_at: int = 0) -> int:
    """Hash the next/first character in a string."""
    h = start_at + ord(c)
    h *= 17
    h = h % 256
    return h


def hash_str(s: str) -> int:
    """Hash a string."""
    h = 0
    for char in s:
        h = hash_char(char, h)
    return h


def parse_file(filename: str) -> int:
    """Parse a file."""
    with open(filename) as f:
        for line in f:
            line = line.strip()
            strs = line.split(",")
            return sum(hash_str(s) for s in strs)
    raise RuntimeError("how did you even get here")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
