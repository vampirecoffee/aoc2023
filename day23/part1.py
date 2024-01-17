"""Part 1 of the solution for day 23."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from enum import Enum

from aoc_tools.graph import Dir, Point

sys.setrecursionlimit(100000)


class Tile(Enum):
    """One tile on our graph/map/thing."""

    PATH = "."
    FOREST = "#"
    UP = "^"
    LEFT = "<"
    RIGHT = ">"
    DOWN = "v"

    def valid_dirs(self) -> list[Dir]:
        """Valid directions to go from here."""
        if self == Tile.PATH:
            return [Dir.LEFT, Dir.RIGHT, Dir.UP, Dir.DOWN]
        if self == Tile.FOREST:
            return []
        if self == Tile.UP:
            return [Dir.UP]
        if self == Tile.LEFT:
            return [Dir.LEFT]
        if self == Tile.RIGHT:
            return [Dir.RIGHT]
        if self == Tile.DOWN:
            return [Dir.DOWN]
        raise ValueError(f"Unrecognized tile {self}")

    @property
    def visitable(self) -> bool:
        """Are you allowed to go to this tile?"""
        return self != Tile.FOREST


@dataclass
class Map:
    """Map. It has tiles."""

    tiles: list[list[Tile]] = field(default_factory=list)
    max_row: int = 0
    max_col: int = 0

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

    @property
    def start_point(self) -> Point:
        """Point where we start our walk."""
        top_row = self.tiles[0]
        for col_idx, tile in enumerate(top_row):
            if tile == Tile.PATH:
                return Point(0, col_idx)
        raise RuntimeError("there's no start tile in there")

    @property
    def end_point(self) -> Point:
        """Point where we end our walk."""
        return Point(self.max_row, self.max_col)

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

    def visit(self, point: Point, path: set[Point], cost: int) -> int:
        """Visit the given point."""
        assert self.is_valid(point)
        if point == self.end_point:
            return cost
        max_cost = cost
        for neighbor in self.neighbors(point):
            if neighbor in path:
                continue  # can't visit the same point twice
            new_path = set(path)
            new_path.add(neighbor)
            neighbor_cost = self.visit(neighbor, new_path, cost + 1)
            max_cost = max(max_cost, neighbor_cost)
        return max_cost

    def take_a_hike(self) -> int:
        """Take a hike and return the longest path."""
        path = set([self.start_point])
        return self.visit(self.start_point, path, 0)


def parse_file(filename) -> int:
    """Parse file and solve problem."""
    m = Map()
    with open(filename) as f:
        for line in f:
            if line.strip():
                m.add_row(line)
    return m.take_a_hike()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
