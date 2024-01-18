"""Part 1 of solution for Day 18."""

from __future__ import annotations

import argparse
import re
from copy import deepcopy
from dataclasses import dataclass

from aoc_tools.graph import Dir, Point, count_enclosed_points, perimeter


@dataclass(frozen=True)
class RGB:
    """RGB color."""

    red: int
    green: int
    blue: int

    @classmethod
    def from_hex(cls, s: str) -> RGB:
        """Convert a six-digit hex str into RGB."""
        red = int(s[0:2], 16)
        green = int(s[2:4], 16)
        blue = int(s[4:6], 16)
        return RGB(red, green, blue)


_instr_re = re.compile(r"(\w) (\d+) \(#(......)\)")


@dataclass(frozen=True)
class Instruction:
    """One 'instruction' on what direction / how far / what color to dig."""

    direction: Dir
    n: int
    color: RGB

    @classmethod
    def from_str(cls, s: str) -> Instruction:
        """From a string. A 'line', perhaps"""
        s = s.strip()
        match = _instr_re.search(s)
        if not match:
            raise RuntimeError(f"Could not match {s} to instruction regex")
        direction = Dir(match.group(1))
        n = int(match.group(2))
        rgb = RGB.from_hex(match.group(3))
        return cls(direction, n, rgb)

    def follow(self, start_point: Point) -> Point:
        """Follow this instruction, starting from start_point."""
        return start_point.go(self.direction, n=self.n)

    def mark_grid(self, grid: list[list[str]], start_point: Point) -> list[list[str]]:
        """Follow this instruction, marking each square in the grid."""
        grid[start_point.row][start_point.col] = "#"
        at_point = start_point
        for _ in range(self.n):
            step_point = at_point.go(self.direction)
            grid[step_point.row][step_point.col] = "#"
            at_point = step_point

        return grid


def follow_dig_plan(plan: list[Instruction], debug: bool = False) -> list[Point]:
    """Follow the dig plan and return a list of points in the polygon."""
    if debug:
        grid_row = ["."] * 7
        grid: list[list[str]] = []
        for _ in range(10):
            grid.append(deepcopy(grid_row))

    p = Point(0, 0)
    polygon = [p]
    for instr in plan:
        new_point = instr.follow(p)
        if debug:
            grid = instr.mark_grid(grid, p)
        polygon.append(new_point)
        p = new_point
    if debug:
        pretty_grid = "\n".join("".join(char for char in row) for row in grid)
        print(pretty_grid)
    return polygon


def lagoon_size(polygon: list[Point]) -> int:
    """Find the size of our lagoon."""
    enclosed = count_enclosed_points(polygon)
    perim = perimeter(polygon)
    return int(enclosed) + int(perim)


def parse_file(filename: str) -> int:
    """Parse file do thing"""
    plan: list[Instruction] = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            plan.append(Instruction.from_str(line))
    polygon = follow_dig_plan(plan)
    return lagoon_size(polygon)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
