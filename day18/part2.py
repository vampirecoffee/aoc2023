from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import re
from graph import Dir, Point, count_enclosed_points, perimeter


@dataclass(frozen=True)
class RGB:
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


_instr_re = re.compile(r"\w \d+ \(#(.....)(.)\)")


def _int_to_dir(i: int) -> Dir:
    """Convert an int in the input into a direction."""
    if i == 0:
        return Dir.RIGHT
    elif i == 1:
        return Dir.DOWN
    elif i == 2:
        return Dir.LEFT
    elif i == 3:
        return Dir.UP
    else:
        raise ValueError(f"{i} should be between 0 and 3 inclusive")


@dataclass(frozen=True)
class Instruction:
    direction: Dir
    n: int

    @classmethod
    def from_str(cls, s: str) -> Instruction:
        """From a string. A 'line', perhaps"""
        s = s.strip()
        match = _instr_re.search(s)
        if not match:
            raise RuntimeError(f"Could not match {s} to instruction regex")
        dir_int = int(match.group(2), 16)
        direction = _int_to_dir(dir_int)
        n = int(match.group(1), 16)
        return cls(direction, n)

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


def follow_dig_plan(plan: list[Instruction]) -> list[Point]:
    """Follow the dig plan and return a list of points in the polygon."""
    p = Point(0, 0)
    polygon = [p]
    for instr in plan:
        new_point = instr.follow(p)
        polygon.append(new_point)
        p = new_point
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


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
