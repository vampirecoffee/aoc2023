"""Utilities for things that happen in 3D space."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """A point in 3D space."""

    x: int
    y: int
    z: int

    @classmethod
    def from_str(cls, s: str) -> Point:
        """Create a point from a string that looks like: ``x,y,z``."""
        s = s.strip()
        if s.count(",") != 2:
            raise ValueError(f"string ``{s}`` does not match the format ``x,y,z``")
        ints = tuple(int(e) for e in s.split(","))
        assert len(ints) == 3
        x, y, z = ints
        return Point(x, y, z)

    def distance(self, other: Point) -> float:
        """Distance between this point and another."""
        x_diff = (self.x - other.x) ** 2
        y_diff = (self.y - other.y) ** 2
        z_diff = (self.z - other.z) ** 2
        return math.sqrt(x_diff + y_diff + z_diff)
