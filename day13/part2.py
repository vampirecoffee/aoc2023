"""Part 1 of the reflection problem."""

from __future__ import annotations

import argparse
import functools


@functools.cache
def is_vert_reflection(
    rows: tuple[str, ...], col_idx: int, want_to_consider_col: int
) -> bool:
    """Can you make a valid reflection at this column?"""
    col_idx += 1
    # Assume that all rows have the same length
    max_len = min(len(rows[0][:col_idx]), len(rows[0][col_idx:]))
    # print("max len is", max_len, "for column index", col_idx)
    if max_len == 0:
        return False
    if (want_to_consider_col not in range(col_idx - max_len, col_idx)) and (
        want_to_consider_col not in range(col_idx, col_idx + max_len)
    ):
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
def is_horiz_reflection(
    rows: tuple[str, ...], row_idx: int, want_to_consider_row: int
) -> bool:
    """Can you make a valid reflection at this row?"""
    top_idx = row_idx
    bottom_idx = row_idx + 1
    print("starting comparison at top index", top_idx, "and bottom", bottom_idx)
    if bottom_idx == len(rows):
        return False
    while top_idx >= 0 and bottom_idx < len(rows):
        print("comparing row", top_idx, "to row", bottom_idx)
        top_row = rows[top_idx]
        bottom_row = rows[bottom_idx]
        print(top_row, "is equal to?", bottom_row)
        if top_row != bottom_row:
            return False
        top_idx -= 1
        bottom_idx += 1
    print("top idx", top_idx, "is too small; or else", bottom_idx, "is too big")
    return want_to_consider_row in range(top_idx + 1, bottom_idx)


@functools.cache
def summarize(pattern: tuple[str, ...], row: int, col: int) -> int:
    """Summarize pattern (by finding horizontal and vertical reflections).

    Only patterns that include row/col will "count".
    """
    print("considering pattern")
    print("\n".join(pattern))
    print("that was the pattern")
    print("it has", len(pattern), "rows")
    for i in range(0, len(pattern)):
        print()
        print("row", i)
        if is_horiz_reflection(pattern, i, row):
            # print(i, "is the horizontal reflection row")
            return 100 * (i + 1)

    for i in range(0, len(pattern[0])):
        if is_vert_reflection(pattern, i, col):
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
            new_pattern.append(row_str)
    return tuple(e for e in new_pattern)


@functools.cache
def summarize_with_smudge(pattern: tuple[str, ...]) -> int:
    """Find the smudge and summarize."""
    for i in range(0, len(pattern)):
        for j in range(0, len(pattern[0])):
            print("=====", "trying smudge at", i, j)
            smudged_pattern = flip(pattern, i, j)
            maybe_summary = summarize(smudged_pattern, i, j)
            if maybe_summary:
                print("smudge at", i, j, "gives value", maybe_summary)
                return maybe_summary
    raise RuntimeError("shrug emoji")


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
            total += summarize_with_smudge(tuple(e for e in pattern))
            print("new total:", total)
            pattern = []
    if pattern:
        # print("last pattern")
        to_add = summarize_with_smudge(tuple(e for e in pattern))
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
