"""Part 1 of the Cosmic Expansion problem."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Galaxy:
    """One galaxy at a given position in the universe."""

    row: int
    col: int

    def distance_to(self, other: Galaxy) -> int:
        """Distance between two galaxies."""
        return abs(self.row - other.row) + abs(self.col - other.col)


@dataclass
class Universe:
    """The universe. Many galaxies are in it."""

    image: list[list[str]]

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
            as_list = list(line)
            image.append(as_list)
        return cls(image)

    def expand(self) -> None:
        """Make the universe expand."""
        rows_to_expand: list[int] = []
        for i, row in enumerate(self.image):
            if all(c == "." for c in row):
                rows_to_expand.append(i)
        rows_to_expand.sort(reverse=True)

        col_count = len(self.image[0])
        cols_to_expand: list[int] = []
        for i in range(col_count):
            if all(row[i] == "." for row in self.image):
                cols_to_expand.append(i)
        cols_to_expand.sort(reverse=True)

        for i in rows_to_expand:
            new_row = ["."] * col_count
            self.image.insert(i, new_row)

        for i in cols_to_expand:
            for j in range(  # pylint: disable=consider-using-enumerate
                0, len(self.image)
            ):
                self.image[j].insert(i, ".")

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
        print(self.pretty())
        print("expanding...")
        self.expand()
        print(self.pretty())
        galaxies = self.find_galaxies()
        return sum(g1.distance_to(g2) for g1, g2 in combinations(galaxies, r=2))


def parse_file(filename: str) -> int:
    """Parse file, make galaxy, do the thing."""
    lines: list[str] = []
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    universe = Universe.from_strs(lines)
    return universe.expand_and_sum_shortest_path()


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
