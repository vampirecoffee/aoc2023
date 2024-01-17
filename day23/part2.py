"""Part 2 of solution for day 23."""
from __future__ import annotations

import argparse
import functools
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from tqdm import tqdm

from aoc_tools.graph import Dir, Point

sys.setrecursionlimit(100000)


class Tile(Enum):
    """One tile on our map/graph/thing."""

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
        return [Dir.LEFT, Dir.RIGHT, Dir.UP, Dir.DOWN]

    @property
    def visitable(self) -> bool:
        """Are you allowed to go to this tile?"""
        return self != Tile.FOREST


@dataclass(frozen=True)
class State:
    """Our state when we've taken some path to the given point."""

    at: Point
    cost: int
    visited: frozenset[Point]


@dataclass(frozen=True)
class CacheKey:
    """Key used for our cache, where we keep track of previously-calculated costs."""

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
        if Tile.PATH in bottom_row:
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

    def find_nodes(self) -> defaultdict[Point, list[tuple[Point, int]]]:
        """Find coordinates where you can take different paths
        and the distance between each node.

        shout out to:
        https://www.reddit.com/r/adventofcode/comments/18oy4pc/comment/keob34r/?utm_source=reddit&utm_medium=web2x&context=3
        """
        explored: set[tuple[Point, Dir]] = set()
        nodes: defaultdict[Point, list[tuple[Point, int]]] = defaultdict(list)
        start_point = self.start_point
        end_point = self.end_point
        queue = deque(
            [
                (start_point, Dir.DOWN),
            ]
        )
        while len(queue) > 0:
            from_node, cur_dir = queue.pop()
            if (from_node, cur_dir) in explored:
                continue
            explored.add((from_node, cur_dir))
            cur_pos = from_node
            steps = 0
            while True:
                steps += 1
                cur_pos = cur_pos.go(cur_dir)
                next_dirs = set(Dir)
                next_dirs.remove(cur_dir.reverse())
                bad_dirs: set[Dir] = set()
                for new_dir in next_dirs:
                    if not self.is_valid(cur_pos.go(new_dir)):
                        bad_dirs.add(new_dir)
                next_dirs -= bad_dirs
                if len(next_dirs) > 1 or cur_pos == end_point:
                    to_node = cur_pos
                    nodes[from_node].append((to_node, steps))
                    nodes[to_node].append((from_node, steps))
                    explored.add((to_node, cur_dir.reverse()))
                    for new_dir in next_dirs:
                        if (to_node, new_dir) not in explored:
                            queue.append((to_node, new_dir))
                    break
                cur_dir = list(next_dirs)[0]
        return nodes

    def take_a_hike(self) -> int:
        """Take a hike and return the longest path."""
        cache: dict[CacheKey, int] = {}
        longest_path = -1
        visited = set()
        start_point = self.start_point
        end_point = self.end_point
        visited.add(start_point)
        state = State(
            start_point,
            0,
            frozenset(visited),
        )
        nodes = self.find_nodes()
        queue = deque([state])
        with tqdm(total=1) as pbar:
            while len(queue) > 0:
                state = queue.popleft()
                if state.at == end_point:
                    if state.cost > longest_path:
                        longest_path = state.cost
                    pbar.update(1)
                    continue
                if cache.get(CacheKey(state.at, state.visited), -1) >= state.cost:
                    pbar.update(1)
                    continue  # we already have the same or longer path
                cache[CacheKey(state.at, state.visited)] = state.cost
                new_visited: frozenset[Point] = frozenset(
                    state.visited | set([state.at])
                )
                for next_node, steps_to_node in nodes[state.at]:
                    if next_node in new_visited:
                        continue
                    new_steps = state.cost + steps_to_node
                    if cache.get(CacheKey(next_node, new_visited), -1) >= new_steps:
                        continue  # we already have the same or longer path
                    queue.append(State(next_node, new_steps, new_visited))
                    pbar.total += 1
                pbar.update(1)
        return longest_path

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
