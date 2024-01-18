"""Part 1 of the hot springs problem."""

from __future__ import annotations

import argparse
import functools
from dataclasses import dataclass

from tqdm import tqdm

UNKNOWN = "?"
OPERATIONAL = "."
DAMAGED = "#"


@functools.cache
def calc(row: str, groups: tuple[int]) -> int:
    """Calculate number of ways to make the groups."""
    # No more groups left; might be valid
    if not groups:
        # If there's no more damaged springs, there's no more groups
        # (if there's unknowns in there, we can make them all .)
        if DAMAGED not in row:
            return 1
        return 0

    if not row:
        # Groups exist, but row is done. whoops!
        return 0

    next_char = row[0]
    if next_char == DAMAGED:
        return calc_damaged(row, groups)
    if next_char == OPERATIONAL:
        return calc_operational(row, groups)
    if next_char == UNKNOWN:
        return calc_damaged(row, groups) + calc_operational(row, groups)
    raise RuntimeError(f"Unrecognized character {next_char}")


@functools.cache
def calc_damaged(row: str, groups: tuple[int]) -> int:
    """Assume that the first character is a damaged spring."""
    next_group = groups[0]
    this_group = row[:next_group]
    this_group = this_group.replace(UNKNOWN, DAMAGED)

    if this_group != next_group * DAMAGED:
        return 0

    # Rest of the row is just this group
    if len(row) == next_group:
        # it's the last group. woohoo.
        if len(groups) == 1:
            return 1
        # otherwise, there are too many groups
        return 0

    # Make sure next character can be a separator
    if row[next_group] in (UNKNOWN, OPERATIONAL):
        return calc(row[next_group + 1 :], groups[1:])

    # Can't be handled; isn't possible
    return 0


@functools.cache
def calc_operational(row: str, groups: tuple[int]) -> int:
    """Assume that the first character is operational."""
    # Just skip it! look for the next interesting thing
    return calc(row[1:], groups)


@dataclass(frozen=True)
class Row:
    """One row in the input."""

    row: str
    groups: list[int]

    @classmethod
    def from_str(cls, s: str) -> Row:
        """Convert a string to a row."""
        row, groups_str = s.split()
        groups = [int(e) for e in groups_str.split(",")]
        row_list = [row] * 5
        row = "?".join(row_list)
        groups = groups * 5
        return Row(row=row, groups=groups)

    def count_arrangements(self) -> int:
        """Number of possible arrangements that make this row valid."""
        return calc(self.row, tuple(e for e in self.groups))


def parse_file(filename: str) -> int:
    """Parse file, return sum of number of combinations."""
    the_sum = 0
    with open(filename, encoding="utf-8") as f:
        for line in tqdm(f):
            r = Row.from_str(line)
            the_sum += r.count_arrangements()
    return the_sum


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
