"""Part 2 of the Mirage problem."""

from __future__ import annotations

import argparse


def gen_next_value(seq: list[int]) -> int:
    """Generate the next value from the 'history' list."""
    diffs = [seq[i + 1] - seq[i] for i in range(0, len(seq) - 1)]
    if not all(e == 0 for e in diffs):
        next_diff_value = gen_next_value(diffs)
        diffs.insert(0, next_diff_value)
    return seq[0] - diffs[0]


def parse_file(filename: str) -> int:
    """Generate next value from each line, then sum those."""
    next_val_sum = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            as_ints = [int(e) for e in line.split()]
            incr_by = gen_next_value(as_ints)
            next_val_sum += incr_by
    return next_val_sum


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
