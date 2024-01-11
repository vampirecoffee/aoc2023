from __future__ import annotations

import argparse
from functools import cache
from dataclasses import dataclass, field
from typing import Any
import sys
import math
from enum import Enum
import functools

from tqdm import tqdm  # type: ignore[import-untyped]

from graph import Dir, Point

sys.setrecursionlimit(100000)


class Tile(Enum):
    PATH = "."
    FOREST = "#"
    UP = "^"
    LEFT = "<"
    RIGHT = ">"
    DOWN = "v"

    def valid_dirs(self) -> list[Dir]:
        """Valid directions to go from here."""
        if self == Tile.FOREST:
            return []
        else:
            return [Dir.LEFT, Dir.RIGHT, Dir.UP, Dir.DOWN]

    @property
    def visitable(self) -> bool:
        """Are you allowed to go to this tile?"""
        return self != Tile.FOREST


@dataclass(frozen=True)
class State:
    at: Point
    cost: int
    visited: frozenset[Point]


@dataclass(frozen=True)
class CacheKey:
    at: Point
    visited: frozenset[Point]


@dataclass
class Map:
    """Map. It has tiles."""

    tiles: list[list[Tile]] = field(default_factory=list)
    max_row: int = 0
    max_col: int = 0
    start_row: int = 0
    start_col: int = 0
    end_row: int = 0
    end_col: int = 0

    def add_row(self, s: str) -> None:
        """Add a row to this map."""
        s = s.strip()
        tiles = [Tile(char) for char in s]
        self.tiles.append(tiles)
        self._set_max()

    def _set_max(self) -> None:
        """Set max row/col."""
        self.max_row = len(self.tiles) - 1
        self.max_col = len(self.tiles[0]) - 1

        top_row = self.tiles[0]
        for col_idx, tile in enumerate(top_row):
            if tile == Tile.PATH:
                self.start_row = 0
                self.start_col = col_idx
                break

        bottom_row = self.tiles[-1]
        if tile.PATH in bottom_row:
            for col_idx, tile in enumerate(bottom_row):
                if tile == Tile.PATH:
                    self.end_row = self.max_row
                    self.end_col = col_idx

    @property
    def possible_path_count(self) -> int:
        """Number of paths that might exist.

        This is definitively bigger than the number of paths that 'make sense'.
        """
        sum_ok_tiles = sum(sum(t != Tile.FOREST for t in row) for row in self.tiles)
        n = sum_ok_tiles
        # sum_possible_combinations = sum(
        #    math.factorial(n) / (math.factorial(k) * math.factorial(n - k))
        #    for k in range(2, sum_ok_tiles)
        # )
        # return int(sum_possible_combinations)
        return int(4**n)

    @property
    def start_point(self) -> Point:
        """Point where we start our walk."""
        return Point(self.start_row, self.start_col)

    @property
    def end_point(self) -> Point:
        """Point where we end our walk."""
        return Point(self.end_row, self.end_col)

    def is_valid(self, point: Point) -> bool:
        """Is this a valid *and visitable* point on this map?"""
        if not point.valid(self.max_row, self.max_col):
            return False
        t = self.tiles[point.row][point.col]
        return t.visitable

    def neighbors(self, point: Point) -> set[Point]:
        """Get valid neighbors for a point."""
        new_points: set[Point] = set()
        new_dirs = self.tiles[point.row][point.col].valid_dirs()
        for d in new_dirs:
            neighbor = point.go(d)
            if self.is_valid(neighbor):
                new_points.add(neighbor)
        return new_points

    def visit(
        self, point: Point, path: set[Point], cost: int, pbar: Any
    ) -> tuple[int, set[Point]]:
        """Visit the given point, returning 'best' cost and path used."""
        assert self.is_valid(point)
        if point == self.end_point:
            return (cost, path)
        max_cost = -1
        best_path = path
        point_neighbors = self.neighbors(point)
        pbar.update(4 - len(point_neighbors))
        for neighbor in self.neighbors(point):
            if neighbor in path:
                continue  # can't visit the same point twice
            new_path = set(path)
            new_path.add(neighbor)
            neighbor_cost, neighbor_path = self.visit(
                neighbor, new_path, cost + 1, pbar
            )
            pbar.update(1)
            if neighbor_cost > max_cost:
                best_path = neighbor_path
                max_cost = neighbor_cost
        return max_cost, best_path

    def old_take_a_hike(self, debug=False) -> int:
        """Take a hike and return the longest path."""
        path = frozenset([self.start_point])
        tiles_as_tuple = tuple(tuple(t for t in row) for row in self.tiles)
        cost, best_path = cacheable_visit(
            tiles_as_tuple,
            self.start_point,
            path,
            cost=0,
            max_row=self.max_row,
            max_col=self.max_col,
            end_point=self.end_point,
        )
        if debug:
            self.print_path(set(best_path))
        return cost

    def take_a_hike(self, debug=False) -> int:
        """Take a hike and return the longest path."""
        cache: dict[CacheKey, int] = {}
        longest_path = -1
        visited = set()
        visited.add(self.start_point)
        state = State(
            self.start_point,
            0,
            frozenset(visited),
        )
        queue = [state]
        while len(queue) > 0:
            state = queue.pop()
            if state.at == end:
                if state.cost > longest_path:
                    print(state.cost)
                    longest_path = state.cost
                continue

    def print_path(self, path: set[Point]) -> None:
        """Print the path taken."""
        start_point = self.start_point
        end_point = self.end_point
        for row_idx, row in enumerate(self.tiles):
            row_out: list[str] = []
            for col_idx, tile in enumerate(row):
                pt = Point(row_idx, col_idx)
                if pt == start_point:
                    row_out.append("S")
                elif pt == end_point:
                    row_out.append("E")
                elif pt in path:
                    row_out.append("O")
                else:
                    row_out.append(tile.value)
            print("".join(row_out))


@functools.cache
def cacheable_visit(
    tiles: tuple[tuple[Tile]],
    point: Point,
    path: frozenset[Point],
    cost: int,
    max_row: int,
    max_col: int,
    end_point: Point,
) -> tuple[int, frozenset[Point]]:
    """The visit function ... but cacheable."""
    if point == end_point:
        return (cost, path)
    max_cost = -1
    best_path = frozenset(path)
    point_neighbors = cacheable_neighbors(tiles, point, max_row, max_col)
    for neighbor in point_neighbors:
        if neighbor in path:
            continue
        new_path = frozenset(path | set([neighbor]))
        neighbor_cost, neighbor_path = cacheable_visit(
            tiles, neighbor, new_path, cost + 1, max_row, max_col, end_point
        )
        if neighbor_cost > max_cost:
            best_path = neighbor_path
            max_cost = neighbor_cost
    return max_cost, best_path


@functools.cache
def cacheable_valid_checker(
    tiles: tuple[tuple[Tile]],
    point: Point,
    max_row: int,
    max_col: int,
) -> bool:
    """Validity checker ... but cacheable."""
    if not point.valid(max_row, max_col):
        return False
    t = tiles[point.row][point.col]
    return t.visitable


@functools.cache
def cacheable_neighbors(
    tiles: tuple[tuple[Tile]],
    point: Point,
    max_row: int,
    max_col: int,
) -> frozenset[Point]:
    """Neighbors function, but cacheable."""
    new_points: set[Point] = set()
    new_dirs = tiles[point.row][point.col].valid_dirs()
    for d in new_dirs:
        neighbor = point.go(d)
        if cacheable_valid_checker(tiles, point, max_row, max_col):
            new_points.add(neighbor)
    return frozenset(new_points)


def parse_file(filename) -> int:
    """Parse file and solve problem."""
    m = Map()
    with open(filename) as f:
        for line in f:
            if line.strip():
                m.add_row(line)
    return m.take_a_hike(debug=False)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
