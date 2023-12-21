"""Basic direction/graph stuff."""

from __future__ import annotations
from dataclasses import dataclass
import math
from enum import Enum


class Dir(Enum):
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


@dataclass(frozen=True)
class Point:
    row: int
    col: int

    def go(self, direction: Dir, n=1) -> Point:
        """From this point, go in a direction."""
        if direction == Dir.LEFT:
            return Point(self.row, self.col - n)
        elif direction == Dir.RIGHT:
            return Point(self.row, self.col + n)
        elif direction == Dir.UP:
            return Point(self.row - n, self.col)
        elif direction == Dir.DOWN:
            return Point(self.row + n, self.col)

    def valid(self, max_height: int, max_width: int) -> bool:
        """Is this point valid for a graph with the given max height+width?"""
        return all(
            (
                self.row >= 0,
                self.row <= max_height,
                self.col >= 0,
                self.col <= max_height,
            )
        )

    def determinant(self, other: Point) -> int:
        """Return the determinant of a 2x2 matrix of this and other.

        Used for shoelace theorem stuff.
        """
        return (self.row * other.col) - (self.col * other.row)

    def distance(self, other: Point) -> float:
        """Distance between two points."""
        row_diff_squared = (self.row - other.row) ** 2
        col_diff_squared = (self.col - other.col) ** 2
        return math.sqrt(row_diff_squared + col_diff_squared)


def edges(polygon: list[Point]) -> list[tuple[Point, Point]]:
    """Given a list of points in the polygon, get a list of edges."""
    polygon = polygon + [polygon[0]]
    return [(polygon[i], polygon[i + 1]) for i in range(len(polygon) - 1)]


def enclosed_area(polygon: list[Point]) -> float:
    """Find the enclosed area of this polygon."""
    matrix_sum = sum(p1.determinant(p2) for p1, p2 in edges(polygon))
    # The original formula is only valid going in one direction,
    # and produces a negative result in the other.
    # We could determine which way is counterclockwise ...
    # or we could just calculate it twice lol
    if matrix_sum < 0:
        return enclosed_area(list(reversed(polygon)))
    return matrix_sum / 2


def count_enclosed_points(polygon: list[Point]) -> int:
    """Count the number of integer points enclosed.

    See: Pick's theorem.
    """
    area = enclosed_area(polygon)
    boundary_points = len(polygon)
    return int(area + 1 - (boundary_points / 2))


def perimeter(polygon: list[Point]) -> float:
    """Find the length of the perimeter of a polygon."""
    return sum(p1.distance(p2) for p1, p2 in edges(polygon))
