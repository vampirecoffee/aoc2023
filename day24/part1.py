from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable
import itertools
from functools import cached_property


@dataclass(frozen=True)
class Point2D:
    x: int
    y: int


@dataclass(frozen=True)
class Velocity:
    x: int
    y: int


@dataclass(frozen=True)
class Hailstone:
    """Class representing a hailstone."""

    pos: Point2D
    vel: Velocity

    @classmethod
    def from_str(cls, s: str) -> Hailstone:
        """from a string"""
        pos_part, vel_part = s.split("@")
        pos_x, pos_y, _ = (int(e.strip()) for e in pos_part.split(","))
        vel_x, vel_y, _ = (int(e.strip()) for e in vel_part.split(","))
        pos = Point2D(pos_x, pos_y)
        vel = Velocity(vel_x, vel_y)
        return cls(pos, vel)

    @cached_property
    def next_pos(self) -> Point2D:
        """Return the next point in the path of this hailstone."""
        next_pos = Point2D(
            self.pos.x + self.vel.x,
            self.pos.y + self.vel.y,
        )
        return next_pos

    def _denom(self, other) -> float:
        """Get the denominator of the equation used to determine intersection coordinates."""
        # Normalizing to the names used by wikipedia. lol, lmao, etc
        # see: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        x1 = self.pos.x
        y1 = self.pos.y
        x2 = self.next_pos.x
        y2 = self.next_pos.y
        x3 = other.pos.x
        y3 = other.pos.y
        x4 = other.next_pos.x
        y4 = other.next_pos.y
        # This is long and complicated so i'm gonna do it in 2 parts
        part1 = (x1 - x2) * (y3 - y4)
        part2 = (y1 - y2) * (x3 - x4)
        return part1 - part2

    def intersects_with_path(self, other: Hailstone) -> bool:
        """Will this hailstone's path intersect with another's?"""
        return self._denom(other) != 0

    def in_the_past(self, x: float, y: float) -> bool:
        """Is this point in the *past* for this hailstone?"""
        if self.vel.x > 0:
            return x < self.pos.x
        else:
            return x > self.pos.x

    def intersect_coords(self, other: Hailstone) -> tuple[float, float]:
        """What are the x,y coordinates where these two hailstones intersect?"""

        denom = self._denom(other)
        if not self.intersects_with_path(other):
            raise ValueError("These two hailstones do not intersect!")
        if denom == 0:
            raise ValueError("wat")
        x1 = self.pos.x
        y1 = self.pos.y
        x2 = self.next_pos.x
        y2 = self.next_pos.y
        x3 = other.pos.x
        y3 = other.pos.y
        x4 = other.next_pos.x
        y4 = other.next_pos.y

        # Part 1 of the numerator for the x-coordinate
        x_num_1 = (x1 * y2 - y1 * x2) * (x3 - x4)
        # Part 2 of the numerator for the x-coordinate
        x_num_2 = (x1 - x2) * (x3 * y4 - y3 * x4)

        # Part 1 of the numerator for the y-coordinate
        y_num_1 = (x1 * y2 - y1 * x2) * (y3 - y4)
        y_num_2 = (y1 - y2) * (x3 * y4 - y3 * x4)

        x = (x_num_1 - x_num_2) / denom
        y = (y_num_1 - y_num_2) / denom
        return x, y


def count_intersections_in_test_area(
    stones: Iterable[Hailstone], min_pos: int, max_pos: int
) -> int:
    """Count how many intersections will occur in the test area."""
    count = 0
    for h1, h2 in itertools.combinations(stones, 2):
        if h1.intersects_with_path(h2):
            x, y = h1.intersect_coords(h2)
            if all(
                (
                    not h1.in_the_past(x, y),
                    not h2.in_the_past(x, y),
                    min_pos <= x,
                    min_pos <= y,
                    x <= max_pos,
                    y <= max_pos,
                )
            ):
                count += 1
    return count


def parse_file(filename: str) -> int:
    """Parse file and return answer."""
    stones: list[Hailstone] = []
    with open(filename) as file:
        for line in file:
            stones.append(Hailstone.from_str(line.strip()))
    min_pos = 200000000000000
    max_pos = 400000000000000
    if "sample" in filename:
        min_pos = 7
        max_pos = 27
    return count_intersections_in_test_area(stones, min_pos, max_pos)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
