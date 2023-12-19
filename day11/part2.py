"""Part 1 of the Cosmic Expansion problem."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from itertools import combinations

EXP_FACTOR = 1000000


def _sorted_range(x: int, y: int) -> range:
    if x < y:
        return range(x, y)
    else:
        return range(y, x)


@dataclass(frozen=True)
class Galaxy:
    row: int
    col: int

    def distance_to(
        self, other: Galaxy, exp_rows: list[int], exp_cols: list[int]
    ) -> int:
        dist = abs(self.row - other.row) + abs(self.col - other.col)
        for row in exp_rows:
            if row in _sorted_range(self.row, other.row):
                dist += EXP_FACTOR - 1
        for col in exp_cols:
            if col in _sorted_range(self.col, other.col):
                dist += EXP_FACTOR - 1
        return dist


@dataclass
class Universe:
    image: list[list[str]]
    exp_rows: list[int] = field(default_factory=list)
    exp_cols: list[int] = field(default_factory=list)

    def pretty(self) -> str:
        """String representation."""
        lines: list[str] = []
        for row in self.image:
            lines.append("".join(row))
        return "\n".join(lines)

    @classmethod
    def from_strs(cls, lines: list[str]) -> Universe:
        """Convert list of strings to a Universe.

        Does NOT expand.
        """
        image: list[list[str]] = []
        for line in lines:
            line = line.strip()
            as_list = [e for e in line]
            image.append(as_list)
        return cls(image)

    def expand(self) -> None:
        """Make the universe expand."""
        rows_to_expand: list[int] = []
        for i, row in enumerate(self.image):
            if all(c == "." for c in row):
                rows_to_expand.append(i)
        rows_to_expand.sort()
        self.exp_rows = rows_to_expand

        col_count = len(self.image[0])
        cols_to_expand: list[int] = []
        for i in range(col_count):
            if all(row[i] == "." for row in self.image):
                cols_to_expand.append(i)
        cols_to_expand.sort()
        self.exp_cols = cols_to_expand

    def find_galaxies(self) -> list[Galaxy]:
        """Find all the galaxies in this universe.

        Does NOT expand.
        """
        galaxies: list[Galaxy] = []
        for i, row in enumerate(self.image):
            for j, char in enumerate(row):
                if char == "#":
                    galaxies.append(Galaxy(i, j))
        return galaxies

    def expand_and_sum_shortest_path(self) -> int:
        """Expand the universe, then find sum of shortest paths."""
        print("expanding...")
        self.expand()
        galaxies = self.find_galaxies()
        return sum(
            g1.distance_to(g2, exp_rows=self.exp_rows, exp_cols=self.exp_cols)
            for g1, g2 in combinations(galaxies, r=2)
        )


def parse_file(filename: str) -> int:
    """Parse file, make galaxy, do the thing."""
    lines: list[str] = []
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    universe = Universe.from_strs(lines)
    return universe.expand_and_sum_shortest_path()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
