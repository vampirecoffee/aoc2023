"""Basic direction/graph stuff."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Dir(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


@dataclass(frozen=True)
class Point:
    row: int
    col: int

    def go(self, direction: Dir) -> Point:
        """From this point, go in a direction."""
        if direction == Dir.LEFT:
            return Point(self.row, self.col - 1)
        elif direction == Dir.RIGHT:
            return Point(self.row, self.col + 1)
        elif direction == Dir.UP:
            return Point(self.row - 1, self.col)
        elif direction == Dir.DOWN:
            return Point(self.row + 1, self.col)
