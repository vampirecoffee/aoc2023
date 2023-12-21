from __future__ import annotations

import argparse
from dataclasses import dataclass
import re
from graph import Dir, Point, enclosed_area, perimeter


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


_instr_re = re.compile(r"(\w) (\d) \(#(......)\)")


@dataclass(frozen=True)
class Instruction:
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
    enclosed = enclosed_area(polygon)
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
