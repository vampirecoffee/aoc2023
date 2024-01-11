"""Basic direction/graph stuff."""

from __future__ import annotations
from dataclasses import dataclass
import math
from enum import Enum

import numpy  # type: ignore[import-not-found]


class Dir(Enum):
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"

    def reverse(self) -> Dir:
        if self == Dir.LEFT:
            return Dir.RIGHT
        if self == Dir.RIGHT:
            return Dir.LEFT
        if self == Dir.UP:
            return Dir.DOWN
        if self == Dir.DOWN:
            return Dir.UP
        raise RuntimeError("you forgot a case")


@dataclass(frozen=True)
class Point:
    row: int
    col: int

    @property
    def x(self) -> int:
        return self.col

    @property
    def y(self) -> int:
        return self.row

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

    def valid(self, max_row: int, max_col: int) -> bool:
        """Is this point valid for a graph with the given max_row+max_col?"""
        return all(
            (
                self.row >= 0,
                self.row <= max_row,
                self.col >= 0,
                self.col <= max_col,
            )
        )

    def determinant(self, other: Point) -> int:
        """Return the determinant of a 2x2 matrix of this and other.

        Used for shoelace theorem stuff.
        """
        return Edge(self, other).determinant()

    def distance(self, other: Point) -> float:
        """Distance between two points."""
        return Edge(self, other).distance()

    def neighbors(self) -> list[Point]:
        """Return all of this point's neighbors (up/down/left/right)."""
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]


@dataclass(frozen=True)
class Edge:
    p1: Point
    p2: Point

    def determinant(self) -> int:
        """Determinant of an edge.

        Used in the shoelace theorem.
        """
        return (self.p1.col * self.p2.row) - (self.p1.row * self.p2.col)

    def distance(self) -> float:
        """Length of this edge."""
        row_diff_squared = (self.p1.row - self.p2.row) ** 2
        col_diff_squared = (self.p1.col - self.p2.col) ** 2
        return math.sqrt(row_diff_squared + col_diff_squared)

    def integer_points(self) -> int:
        """How many integer points are along this edge?

        This includes the start point but not the end point.
        """
        row_diff = abs(self.p1.row - self.p2.row)
        col_diff = abs(self.p1.col - self.p2.col)
        return math.gcd(row_diff, col_diff)

    def collinear_with(self, point: Point) -> bool:
        """Is this point collinear with this edge?"""
        matrix = [
            [self.p1.row, self.p1.col],
            [self.p2.row, self.p2.col],
            [point.row, point.col],
        ]
        return numpy.linalg.matrix_rank(matrix) <= 1

    def intersects(self, other: Edge) -> bool:
        """Does this edge intersect with the other one?"""
        # Math!
        # This is the denominator used to calculate the intersection coordinates
        denom = (self.p1.x - self.p2.x) * (other.p1.y - other.p2.y) - (
            self.p1.y - self.p2.y
        ) * (other.p1.x - other.p2.x)
        # If it's 0, the lines are parallel
        return denom != 0

    def intersection_point(self, other: Edge) -> tuple[float, float]:
        """Return the point where these two lines intersect.

        This is returned as x,y coords - flip them around for row,col.
        """
        denom = (self.p1.x - self.p2.x) * (other.p1.y - other.p2.y) - (
            self.p1.y - self.p2.y
        ) * (other.p1.x - other.p2.x)
        x_num = (
            (self.p1.x * self.p2.y - self.p1.y * self.p2.x) * (other.p1.x - other.p2.x)
        ) - (
            (self.p1.x - self.p2.x)
            * (other.p1.x * other.p2.y - other.p1.y * other.p2.x)
        )
        y_num = (
            (self.p1.x * self.p2.y - self.p1.y * self.p2.x) * (other.p1.y - other.p2.y)
        ) - (
            (self.p1.y - self.p2.y)
            * (other.p1.x * other.p2.y - other.p1.y * other.p1.x)
        )
        return x_num / denom, y_num / denom


def get_edges(polygon: list[Point]) -> list[Edge]:
    """Given a list of points in the polygon, get a list of edges."""
    start_point = polygon[0]
    start_to_start = polygon + [start_point]
    out: list[Edge] = [
        Edge(start_to_start[i], start_to_start[i + 1]) for i in range(len(polygon))
    ]
    assert len(out) == len(polygon)
    return out


def enclosed_area(polygon: list[Point]) -> float:
    """Find the enclosed area of this polygon."""
    edges = get_edges(polygon)
    matrix_sum = sum(e.determinant() for e in edges)
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
    edges = get_edges(polygon)
    boundary_points = sum(e.integer_points() for e in edges)
    return int(area + 1 - (boundary_points / 2))


def perimeter(polygon: list[Point]) -> float:
    """Find the length of the perimeter of a polygon."""
    return sum(e.distance() for e in get_edges(polygon))
