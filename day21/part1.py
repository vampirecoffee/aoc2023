"""Step counter problem."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from tqdm import tqdm  # type: ignore[import-untyped]

from aoc_tools.graph import Point

INFINITY = 999999999999999999999999999999999999999  # basically infinity.

MAX_STEPS = 64


class Type(Enum):
    """Type of cell on our map/graph/thing."""

    START = "S"
    PLOT = "."
    ROCK = "#"


@dataclass
class Cell:
    """One cell on our map/graph/thing."""

    pt: Point
    contents: Type
    done: bool = False
    min_dist: int = INFINITY

    def __post_init__(self) -> None:
        """Post init."""
        if self.contents == Type.ROCK:
            self.done = True

    @property
    def row(self) -> int:
        """Row for this cell."""
        return self.pt.row

    @property
    def col(self) -> int:
        """Column for this cell."""
        return self.pt.col

    @property
    def reachable(self) -> bool:
        """Can you reach this cell, given where we have walked so far?"""
        return all(
            (
                self.contents != Type.ROCK,
                self.min_dist <= MAX_STEPS,
            ),
        )

    def reachable_in(self, steps: int = MAX_STEPS) -> bool:
        """Can you reach this cell in *precisely* N steps?"""
        if steps < self.min_dist:
            return False
        return ((steps - self.min_dist) % 2) == 0

    def consider(self, dist: int) -> bool:
        """Go to this node from a neighbor, possibly setting a new distance.

        Returns True if we should add this cell to our state queue,
        and False otherwise.
        """
        if self.contents == Type.ROCK:
            return False
        if dist >= self.min_dist:
            return False
        self.min_dist = dist
        return True

    @property
    def neighbors(self) -> list[Point]:
        """Return a list of neighbors.

        These neighbors might not be valid graph points.
        """
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]


@dataclass
class Map:
    """Our map, with all its cells."""

    grid: list[list[Cell]] = field(default_factory=list)
    height: int = 0
    width: int = 0
    max_row: int = 0
    max_col: int = 0
    # Cost -> points to visit
    queues_by_cost: defaultdict[int, list[Point]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_row(self, s: str) -> None:
        """Add a row to the map."""
        s = s.strip()
        row_idx = self.height
        cells = [Cell(Point(row_idx, i), Type(char)) for i, char in enumerate(s)]
        self.grid.append(cells)
        self._set_max()

    def _set_max(self) -> None:
        """Set height, width, that kind of thing."""
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.max_row = self.height - 1
        self.max_col = self.width - 1
        self.queues_by_cost = defaultdict(list)

    def _find_start(self) -> Point:
        """Find the starting point in the grid."""
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell.contents == Type.START:
                    return Point(i, j)
        raise ValueError("no start point in grid")

    def wrap(self, pt: Point) -> Point:
        """Wrap this point around."""
        return Point(
            row=pt.row % self.height,
            col=pt.col % self.width,
        )

    def visit(self, pt: Point, cost: int) -> None:
        """Visit a point w/ the given cost."""
        cell = self.grid[pt.row][pt.col]
        cost += 1
        if cost > MAX_STEPS:
            return
        for neighbor_pt in cell.neighbors:
            neighbor_pt = self.wrap(neighbor_pt)
            neighbor_cell = self.grid[neighbor_pt.row][neighbor_pt.col]
            if neighbor_cell.contents == Type.ROCK:
                continue
            should_add = neighbor_cell.consider(cost)
            if should_add:
                self.queues_by_cost[cost].append(neighbor_cell.pt)
            self.grid[neighbor_pt.row][neighbor_pt.col] = neighbor_cell
        self.grid[pt.row][pt.col] = cell

    def walk(self) -> None:
        """Walk through the map until we can't walk anymore."""
        start = self._find_start()
        self._set_max()
        self.visit(start, 0)

        max_possible_states = self.height * self.width * MAX_STEPS
        with tqdm(total=max_possible_states) as pbar:
            while self.queues_by_cost:
                cur_cost = min(self.queues_by_cost.keys())
                if cur_cost > MAX_STEPS:
                    return
                to_visit = self.queues_by_cost.pop(cur_cost)
                for pt in to_visit:
                    self.visit(pt, cur_cost)
                    pbar.update(1)

    def prettyprint(self) -> None:
        """Pretty-print the map."""

        def pretty(cell: Cell) -> str:
            if cell.reachable_in(MAX_STEPS):
                return "O"
            return cell.contents.value

        self._print_rows_by_cellfunc(pretty)

    def _print_rows_by_cellfunc(self, cell_func: Callable[[Cell], str]) -> None:
        """Print the map, using cell_func to turn cells into strs."""
        out: list[str] = []
        for row in self.grid:
            out_row = [cell_func(cell) for cell in row]
            out.append("".join(out_row))
        print("\n".join(out))

    def count_reachable(self) -> int:
        """Count number of reachable cells."""
        self.walk()
        return sum(sum(cell.reachable for cell in row) for row in self.grid)

    def count_reachable_in(self) -> int:
        """Count number of cells reachable in precisely max steps."""
        self.walk()
        return sum(
            sum(cell.reachable_in(MAX_STEPS) for cell in row) for row in self.grid
        )


def parse_file(filename: str) -> int:
    """Parse file and solve problem."""
    # This is kinda ugly but. I don't care.
    if "sample_input" in filename:
        global MAX_STEPS  # pylint: disable=global-statement
        MAX_STEPS = 10
    m = Map()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m.add_row(line)
    c = m.count_reachable_in()
    print()
    return c


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
