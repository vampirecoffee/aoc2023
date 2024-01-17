"""Step counter problem."""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum

from tqdm import tqdm  # type: ignore[import-untyped]

from aoc_tools.graph import Point

INFINITY = 999999999999999999999999999999999999999  # basically infinity.

MAX_STEPS = 26501365


class Cell(Enum):
    """One cell in our graph/map/thing."""

    START = "S"
    PLOT = "."
    ROCK = "#"


@dataclass
class Map:
    """Our map, with many cells."""

    grid: list[list[Cell]] = field(default_factory=list)
    height: int = 0
    width: int = 0
    # Cost -> points to visit
    queues_by_cost: defaultdict[int, list[Point]] = field(
        default_factory=lambda: defaultdict(list)
    )
    seen_points: set[Point] = field(default_factory=set)
    rcount: int = 0

    def add_row(self, s: str) -> None:
        """Add a row to the map."""
        s = s.strip()
        cells = [Cell(char) for char in s]
        self.grid.append(cells)
        self._set_max()

    def _set_max(self) -> None:
        """Set height, width, that kind of thing."""
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.queues_by_cost = defaultdict(list)
        self.seen_points = set()
        self.rcount = 0

    @property
    def max_row(self) -> int:
        """Maximum valid row for this map."""
        return self.height - 1

    @property
    def max_col(self) -> int:
        """Maximum valid column for this map."""
        return self.width - 1

    def _find_start(self) -> Point:
        """Find the starting point in the grid."""
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == Cell.START:
                    return Point(i, j)
        raise ValueError("no start point in grid")

    def wrap(self, pt: Point) -> Point:
        """Wrap this point around."""
        return Point(
            row=pt.row % self.height,
            col=pt.col % self.width,
        )

    def cell_is_not_rock(self, pt: Point) -> bool:
        """Return True if this point wraps around to a non-rock cell."""
        wrapped = self.wrap(pt)
        cell = self.grid[wrapped.row][wrapped.col]
        return cell != Cell.ROCK

    def visit(self, point: Point) -> set[Point]:
        """Visit a point, and get a set of new points to visit."""
        new_points: set[Point] = set()
        for neighbor in point.neighbors():
            if self.cell_is_not_rock(neighbor):
                new_points.add(neighbor)

        return new_points

    def walk_n_steps(self, remember_steps: list[int]) -> list[int]:
        """Walk N steps.

        For each of the steps 'remembered', return how many cells we could
        have walked to.
        """
        num_steps = max(remember_steps)
        start = self._find_start()
        odd_points: set[Point] = set()
        even_points: set[Point] = set([start])
        queue: set[Point] = set([start])

        out: list[int] = []
        progress = 0
        steps_remaining = num_steps
        with tqdm(total=steps_remaining, leave=True) as pbar:
            for i in range(1, num_steps + 1):
                new_points: set[Point] = set()
                pbar.reset(total=(progress + (steps_remaining * len(queue))))
                pbar.update(progress)
                for pt in queue:
                    progress += 1
                    pbar.update(1)
                    new_points |= self.visit(pt)
                if i % 2 == 0:
                    even_points |= new_points
                else:
                    odd_points |= new_points
                queue = deepcopy(new_points)
                if i in remember_steps:
                    if (i % 2) == 0:
                        out.append(len(even_points))
                    else:
                        out.append(len(odd_points))
                steps_remaining -= 1

        return out

    def part2(self) -> int:
        """Do part 2. whee."""
        self._set_max()
        # Grid is quadratic (and square)
        # We start in the middle
        # so number of cells is determined by the function
        # a*n^2 + b*n + c
        # where N is the number of times we've run off the side of the grid
        # Btw this really only works if it's a square
        assert self.height == self.width
        # We will run off the grid *once* after this many steps
        half_grid_size = int(self.height / 2)
        # Before we run off the grid, n = 0
        # Then it takes a length to go around again
        # And another length to go around again
        remember_steps = [(self.height * n) + half_grid_size for n in (0, 1, 2)]
        # Let's run all that
        walk_n_result = self.walk_n_steps(remember_steps)
        if len(walk_n_result) != 3:
            raise RuntimeError(
                "Expected walk_n_result to return a list with exactly 3 items;"
                f" instead, got {walk_n_result}"
            )
        f0 = walk_n_result[0]
        f1 = walk_n_result[1]
        f2 = walk_n_result[2]
        print(f0, f1, f2)
        # f(0) = a*0 + b*0 + c
        # so f(0) == c
        c = f0
        # f(1) = a + b + c
        # so f(1)-c == (a+b)
        # (several gaussian elimination steps later...)
        a = int((f2 - 2 * f1 + f0) / 2)
        b = f1 - f0 - a

        def polynomial(n) -> int:
            n_squared = n * n
            return sum((a * n_squared, b * n, c))

        want_n = int((MAX_STEPS - half_grid_size) / self.height)
        return polynomial(want_n)


def parse_file(filename: str) -> int:
    """Parse file and solve problem."""
    # This is kinda ugly but. I don't care.
    if "sample_input" in filename:
        global MAX_STEPS  # pylint: disable=global-statement
        MAX_STEPS = 50
    m = Map()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m.add_row(line)
    return m.part2()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
