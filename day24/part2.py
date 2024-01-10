from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable
import itertools
from functools import cached_property

import sympy as sp


@dataclass(frozen=True)
class Point3D:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class Velocity:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class Hailstone:
    """Class representing a hailstone."""

    pos: Point3D
    vel: Velocity

    @classmethod
    def from_str(cls, s: str) -> Hailstone:
        """from a string"""
        pos_part, vel_part = s.split("@")
        pos_x, pos_y, pos_z = (int(e.strip()) for e in pos_part.split(","))
        vel_x, vel_y, vel_z = (int(e.strip()) for e in vel_part.split(","))
        pos = Point3D(pos_x, pos_y, pos_z)
        vel = Velocity(vel_x, vel_y, vel_z)
        return cls(pos, vel)

    @cached_property
    def next_pos(self) -> Point3D:
        """Return the next point in the path of this hailstone."""
        next_pos = Point3D(
            self.pos.x + self.vel.x,
            self.pos.y + self.vel.y,
            self.pos.z + self.vel.z,
        )
        return next_pos


def find_rock(h1: Hailstone, h2: Hailstone, h3: Hailstone):
    """Find the position and velocity of our buddy Rock."""

    unknowns = sp.symbols("x y z dx dy dz t1 t2 t3")
    x, y, z, dx, dy, dz, t1, t2, t3 = unknowns
    time = (t1, t2, t3)
    hailstones = (h1, h2, h3)

    equations: list[sp.Eq] = []
    for t, h in zip(time, hailstones):
        # For each hailstone, there is a time t such that:
        # h.pos.x + t * h.vel.x = rock.pos.x + t * rock.vel.x
        # same for y and z
        # so we can make a system of equations from that
        equations.append(sp.Eq(x + t * dx, h.pos.x + t * h.vel.x))
        equations.append(sp.Eq(y + t * dy, h.pos.y + t * h.vel.y))
        equations.append(sp.Eq(z + t * dz, h.pos.z + t * h.vel.z))
    solution = sp.solve(equations, unknowns).pop()
    print(solution)
    rock_x = int(solution[0])
    rock_y = int(solution[1])
    rock_z = int(solution[2])
    rock_dx = int(solution[3])
    rock_dy = int(solution[4])
    rock_dz = int(solution[5])
    return Hailstone(
        Point3D(rock_x, rock_y, rock_z),
        Velocity(rock_dx, rock_dy, rock_dz),
    )


def parse_file(filename: str) -> int:
    """Parse file and return answer."""
    stones: list[Hailstone] = []
    with open(filename) as file:
        for line in file:
            stones.append(Hailstone.from_str(line.strip()))
    h1 = stones[0]
    h2 = stones[1]
    h3 = stones[2]
    rock = find_rock(h1, h2, h3)
    print(rock)
    return rock.pos.x + rock.pos.y + rock.pos.z


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
