"""Part 1 of the hot springs problem."""

from __future__ import annotations

import argparse
import itertools
from copy import deepcopy
from dataclasses import dataclass

UNKNOWN = "?"
OPERATIONAL = "."
DAMAGED = "#"


@dataclass
class Row:
    """One row in our records."""

    row: str
    groups: list[int]

    @classmethod
    def from_str(cls, s: str) -> Row:
        """Convert a string to a row."""
        row, groups_str = s.split()
        groups = [int(e) for e in groups_str.split(",")]
        return Row(row=row, groups=groups)

    def count_arrangements(self) -> int:
        """Number of possible valid arrangements in this row."""
        count = 0
        how_many_unknown = sum(c == UNKNOWN for c in self.row)
        for new_combo in itertools.product(
            [OPERATIONAL, DAMAGED], repeat=how_many_unknown
        ):
            copy_row = deepcopy(self.row)
            for e in new_combo:
                copy_row = copy_row.replace(UNKNOWN, e, 1)
            assert UNKNOWN not in copy_row
            try_groups = copy_row.split(OPERATIONAL)
            try_groups = [e for e in try_groups if len(e) != 0]
            if len(try_groups) != len(self.groups):
                # print(try_groups, "not even the right number of groups")
                continue
            if [len(e) for e in try_groups] == self.groups:
                count += 1
        return count


def parse_file(filename: str) -> int:
    """Parse file, return sum of number of combinations."""
    the_sum = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
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
