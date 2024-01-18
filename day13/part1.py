"""Part 1 of the reflection problem."""

from __future__ import annotations

import argparse
import functools


@functools.cache
def is_vert_reflection(rows: tuple[str, ...], col_idx: int) -> bool:
    """Can you make a valid reflection at this column?"""
    col_idx += 1
    # Assume that all rows have the same length
    max_len = min(len(rows[0][:col_idx]), len(rows[0][col_idx:]))
    # print("max len is", max_len, "for column index", col_idx)
    if max_len == 0:
        return False
    for row in rows:
        left = row[:col_idx]
        right = row[col_idx:]
        # print("row is", row)
        # print("split at column looks like:")
        # print(left, "|", right)
        left = left[::-1]  # reverse the left side
        left = left[:max_len]
        right = right[:max_len]
        # print("comparing reversed left", left, "to right", right)
        if left != right:
            return False
    return True


@functools.cache
def is_horiz_reflection(rows: tuple[str, ...], row_idx: int) -> bool:
    """Can you make a valid reflection at this row?"""
    top_idx = row_idx
    bottom_idx = row_idx + 1
    if bottom_idx == len(rows):
        return False
    while top_idx >= 0 and bottom_idx < len(rows):
        # print("comparing row", top_idx, "to row", bottom_idx)
        top_row = rows[top_idx]
        bottom_row = rows[bottom_idx]
        # print(top_row, "is equal to?", bottom_row)
        if top_row != bottom_row:
            return False
        top_idx -= 1
        bottom_idx += 1
    return True


@functools.cache
def summarize(pattern: tuple[str, ...]) -> int:
    """Summarize pattern (by finding horizontal and vertical reflections)."""
    for i in range(0, len(pattern)):
        # print()
        # print("row", i)
        if is_horiz_reflection(pattern, i):
            # print(i, "is the horizontal reflection row")
            return 100 * (i + 1)

    for i in range(0, len(pattern[0])):
        if is_vert_reflection(pattern, i):
            return i + 1
    return 0


def flip_char(char: str) -> str:
    """Flip one character."""
    if char == ".":
        return "#"
    return "."


def flip(pattern: tuple[str, ...], row: int, col: int) -> tuple[str, ...]:
    """Flip the character in row i and column j."""
    new_pattern: list[str] = []
    for row_idx, row_str in enumerate(pattern):
        if row_idx != row:
            new_pattern.append(row_str)
        else:
            row_str = row_str[:col] + flip_char(row_str[col]) + row_str[col + 1 :]
    return tuple(e for e in new_pattern)


@functools.cache
def summarize_with_smudge(pattern: tuple[str, ...]) -> int:
    """Find the smudge and summarize."""
    for i in range(0, len(pattern)):
        for j in range(0, len(pattern[0])):
            smudged_pattern = flip(pattern, i, j)
            maybe_summary = summarize(smudged_pattern)
            if maybe_summary:
                return maybe_summary
    raise RuntimeError("no reflection found")


def parse_file(filename: str) -> int:
    """Parse input file and return answer."""
    total = 0
    with open(filename) as f:
        pattern: list[str] = []
        for line in f:
            line = line.strip()
            if line:
                pattern.append(line)
                continue
            print("summarizing pattern with", len(pattern), "rows")
            total += summarize(tuple(e for e in pattern))
            # print("new total:", total)
            pattern = []
    if pattern:
        # print("last pattern")
        to_add = summarize(tuple(e for e in pattern))
        # print("last pattern has score", to_add)
        total += to_add
    return total


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
