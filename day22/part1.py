from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy
import math
from collections import defaultdict
import argparse
import itertools
import string

# Important note: the "ground" is the xy plane and up/down is the z-axis
# Also important: a brick at z=1 is "on the ground"


@dataclass(frozen=True)
class Point3D:
    x: int
    y: int
    z: int

    @classmethod
    def from_str(cls, s: str) -> Point3D:
        """Create a point from a string like: x,y,z"""
        s = s.strip()
        x, y, z = (int(e) for e in s.split(","))
        return cls(x, y, z)

    def distance(self, other: Point3D) -> float:
        """Distance between 2 points."""
        x_diff = (self.x - other.x) ** 2
        y_diff = (self.y - other.y) ** 2
        z_diff = (self.z - other.z) ** 2
        return math.sqrt(x_diff + y_diff + z_diff)

    def drop(self, by=1) -> Point3D:
        """Return a new Point3D that is `by` lower (on the z-axis) than this one."""
        return Point3D(x=self.x, y=self.y, z=self.z - by)


SEPARATOR = r"~"


@dataclass(frozen=True)
class Brick:
    end1: Point3D
    end2: Point3D
    name: str = field(default_factory=str, compare=False)

    def __post_init__(self) -> None:
        """Post-init checks."""
        # Make sure that our assumptions - bricks only exist on one axis - hold
        same_x = self.end1.x == self.end2.x
        same_y = self.end1.y == self.end2.y
        same_z = self.end1.z == self.end2.z
        assert any((same_x and same_y, same_x and same_z, same_y and same_z))

    @classmethod
    def from_str(cls, s: str, name="") -> Brick:
        """Create a brick from an input string."""
        if not SEPARATOR in s:
            raise ValueError(
                f"Cannot create brick from string `{s}` that does not contain {SEPARATOR}"
            )
        end1, end2 = (Point3D.from_str(part) for part in s.split(SEPARATOR))
        return cls(end1, end2, name=name)

    @property
    def size(self) -> int:
        """Size of this brick."""
        return int(self.end1.distance(self.end2) + 1)

    @property
    def highest_x(self) -> int:
        """Highest X-coordinate of this brick."""
        return max(self.end1.x, self.end2.x)

    @property
    def lowest_x(self) -> int:
        """Lowest X-coordinate of this brick."""
        return min(self.end1.x, self.end2.x)

    @property
    def highest_y(self) -> int:
        """Highest Y-coordinate of this brick."""
        return max(self.end1.y, self.end2.y)

    @property
    def lowest_y(self) -> int:
        """Lowest Y-coordinate of this brick."""
        return min(self.end1.y, self.end2.y)

    @property
    def highest_z(self) -> int:
        """Highest Z-coordinate of this brick."""
        return max(self.end1.z, self.end2.z)

    @property
    def lowest_z(self) -> int:
        """Lowest Z-coordinate of this brick."""
        return min(self.end1.z, self.end2.z)

    @property
    def z_below(self) -> int:
        """Z-coordinate of the row *below* this brick."""
        return self.lowest_z - 1

    @property
    def z_above(self) -> int:
        """Z-coordinate of the row *above* this brick."""
        return self.highest_z + 1

    def contains(self, point: Point3D) -> bool:
        """Is this point 'inside' the brick?"""
        return all(
            (
                (self.lowest_x <= point.x and point.x <= self.highest_x),
                (self.lowest_y <= point.y and point.y <= self.highest_y),
                (self.lowest_z <= point.z and point.z <= self.highest_z),
            )
        )

    def _shares_x(self, other: Brick) -> bool:
        """Do these bricks overlap in their x-coordinates?"""
        larger_min = max(self.lowest_x, other.lowest_x)
        smaller_max = min(self.highest_x, other.highest_x)
        return larger_min <= smaller_max

    def _shares_y(self, other: Brick) -> bool:
        """Do these bricks overlap in their y-coordinates?"""
        larger_min = max(self.lowest_y, other.lowest_y)
        smaller_max = min(self.highest_y, other.highest_y)
        return larger_min <= smaller_max

    def in_row(self, z: int) -> bool:
        """Is this brick 'in' row Z?"""
        return (self.lowest_z <= z) and (z <= self.highest_z)

    def supports(self, other: Brick) -> bool:
        """Does this brick support other?"""
        if self == other:
            return False  # bricks do not support themselves. lol. lmao.
        if other.lowest_z != (self.highest_z + 1):
            return False
        if not self._shares_x(other):
            return False
        if not self._shares_y(other):
            return False
        return True

    def drop(self, by=1) -> Brick:
        """Drop this brick down N steps on the Z-axis."""
        end1 = self.end1.drop(by)
        end2 = self.end2.drop(by)
        assert min((end1.z, end2.z)) >= 1
        return Brick(end1=end1, end2=end2, name=self.name)

    def _row_below_ok(self, row_below: set[Brick]) -> bool:
        """Check that the 'row below' is actually, you know, below."""
        for brick in row_below:
            if not brick.in_row(self.z_below):
                return False
        return True

    def can_drop(self, row_below: set[Brick]) -> bool:
        """Given the bricks on the next z-level down: can we drop this brick?"""
        if self.lowest_z == 1:
            return False
        assert self._row_below_ok(row_below)
        for brick in row_below:
            if brick.supports(self):
                return False
        return True

    def find_supporters(self, row_below: set[Brick]) -> list[Brick]:
        """What bricks on the row below support this one?"""
        assert self._row_below_ok(row_below)
        supporters: list[Brick] = []
        for brick in row_below:
            if brick.supports(self):
                supporters.append(brick)
        return supporters

    def can_disintegrate(self, self_row: set[Brick], row_above: set[Brick]) -> bool:
        """Can we disintegrate this brick, given its row and the row above it?"""
        for brick_above in row_above:
            supporters = brick_above.find_supporters(self_row)
            if all((supporters, self in supporters, len(supporters) == 1)):
                # print(
                #    "Cannot disintegrate block",
                #    self.name,
                #    "as it is the only supporter for",
                #    brick_above.name,
                # )
                return False
        return True


@dataclass
class BrickColl:
    """A collection of bricks."""

    bricks_by_z: defaultdict[int, set[Brick]] = field(
        default_factory=lambda: defaultdict(set)
    )

    @property
    def names(self) -> set[str]:
        """All names of all bricks in this collection."""
        out: set[str] = set()
        for row in self.bricks_by_z.values():
            out |= set(b.name for b in row)
        return out

    def all_bricks(self) -> set[Brick]:
        """Get all bricks in this collection."""
        out: set[Brick] = set()
        for row in self.bricks_by_z.values():
            out |= row
        return out

    def _next_name(self) -> str:
        """Next name for a brick."""
        names = self.names
        for letter in string.ascii_uppercase:
            if letter not in names:
                return letter
        for try_len in range(2, 5):
            combos = itertools.product(string.ascii_uppercase, repeat=try_len)
            for try_combo in combos:
                try_name = "".join(try_combo)
                if try_name not in names:
                    return try_name
        # Give up
        name = str(len(names) + 1)
        return name

    def empty(self) -> None:
        """Empty this collection of bricks. Totally empty it out."""
        self.bricks_by_z = defaultdict(set)

    def reset(self) -> None:
        """Reset this collection to the state *before* any bricks fell."""
        before_drop = deepcopy(self._bricks_before_drop)
        self.empty()
        for brick in before_drop:
            self.add_brick(brick)

    def add_brick(self, b: Brick) -> None:
        """Add the given brick to the collection."""
        if not b.name:
            end1 = b.end1
            end2 = b.end2
            name = self._next_name()
            b = Brick(
                end1=end1,
                end2=end2,
                name=name,
            )
        if b.name in self.names:
            raise ValueError(
                f"Cannot add brick {b} to this collection because we already have a brick named {b.name}"
            )
        self.bricks_by_z[b.lowest_z].add(b)

    @property
    def max_z(self) -> int:
        """Highest Z-axis value in this collection."""
        max_by_idx: list[int] = []
        for row in self.bricks_by_z.values():
            if not row:
                continue
            max_by_idx.append(max((b.highest_z for b in row)))
        return max(max_by_idx)

    def drop_bricks(self) -> None:
        """Drop all the bricks in this collection."""
        self._bricks_before_drop = set()
        for brick_list in self.bricks_by_z.values():
            for brick in brick_list:
                self._bricks_before_drop.add(brick)

        for icount in itertools.count():
            if icount % 100:
                print("Drop count", icount)
            has_more_drops = self._drop_once()
            if not has_more_drops:
                break

    def bricks_by_highest_idx(self) -> defaultdict[int, set[Brick]]:
        """Bricks organized by their *highest* index."""
        out: defaultdict[int, set[Brick]] = defaultdict(set)
        for b in self.all_bricks():
            out[b.highest_z].add(b)
        return out

    def _drop_once(self) -> bool:
        """Run one iteration of the drop.

        The bool returned is True if *any* bricks were dropped.
        """
        bricks_to_drop: set[Brick] = set()
        bricks_by_highest_idx = self.bricks_by_highest_idx()
        for z in range(1, self.max_z + 1):
            this_row = self.bricks_by_z[z]
            row_below = self.bricks_by_z[z - 1].union(bricks_by_highest_idx[z - 1])
            for brick in this_row:
                if brick.lowest_z != z:
                    # Skip bricks if we're not at the lowest point of the brick
                    continue
                if brick.can_drop(row_below=row_below):
                    bricks_to_drop.add(brick)

        # print("we can drop:", [b.name for b in bricks_to_drop])
        if not bricks_to_drop:
            return False

        for old_brick in bricks_to_drop:
            dropped = old_brick.drop()
            self.bricks_by_z[dropped.lowest_z].add(dropped)
            self.bricks_by_z[old_brick.lowest_z].discard(old_brick)
        return True

    def bricks_to_disintegrate(self) -> set[Brick]:
        """Find all the bricks to disintegrate in self."""
        self.drop_bricks()
        zappable: set[Brick] = set()
        bricks_by_highest_idx = self.bricks_by_highest_idx()
        for brick in self.all_bricks():
            this_row = self.bricks_by_z[brick.highest_z].union(
                bricks_by_highest_idx[brick.highest_z]
            )
            row_above = self.bricks_by_z[brick.z_above]
            if brick.can_disintegrate(self_row=this_row, row_above=row_above):
                zappable.add(brick)
        return zappable

    def pretty(self) -> None:
        """Pretty-print this collection.

        It won't be very pretty if names are not all one character.
        """
        max_x = max((b.highest_x for b in self.all_bricks()))
        max_y = max((b.highest_y for b in self.all_bricks()))

        x_rows: list[str] = []
        y_rows: list[str] = []

        all_bricks = set(b for b in self.all_bricks())

        for z in range(self.max_z, 0, -1):
            this_row = set(b for b in all_bricks if b.in_row(z))
            this_row = self.bricks_by_z[z]

            # Set up view of the x axis from left to right
            x_view_strs: list[str] = []
            for x in range(0, max_x + 1):
                this_x_points = [Point3D(x, y, z) for y in range(0, max_y + 1)]
                x_view_strs.append(_char_for_view(this_row, this_x_points))

            # Set up view of the y axis from left to right
            y_view_strs: list[str] = []
            for y in range(0, max_y + 1):
                this_y_points = [Point3D(x, y, z) for x in range(0, max_x + 1)]
                y_view_strs.append(_char_for_view(this_row, this_y_points))

            row_suffix = f"   {z}"
            x_view_strs.append(row_suffix)
            y_view_strs.append(row_suffix)

            x_rows.append("".join(x_view_strs))
            y_rows.append("".join(y_view_strs))

        print()
        print("x")
        print(_n_digits(max_x))
        for x_row in x_rows:
            print(x_row)

        print()
        print("y")
        print(_n_digits(max_y))
        for y_row in y_rows:
            print(y_row)
        print()


def _char_for_view(row: set[Brick], points_in_view: list[Point3D]) -> str:
    """Return the appropriate character for this view.

    A view is something like:
        [Point3D(x, y, z) for y in range(0, max_y + 1)]
    """
    matched_name: Optional[str] = None
    for brick in row:
        if any(brick.contains(p) for p in points_in_view):
            if matched_name is not None and matched_name != brick.name:
                return "?"
            matched_name = brick.name
    if matched_name is not None:
        return matched_name
    return "."


def _n_digits(n: int) -> str:
    """String that 'counts' from 0 to n."""
    out_l: list[str] = []
    for i, c in enumerate(itertools.cycle(string.digits)):
        out_l.append(c)
        if i >= n:
            break
    return "".join(out_l)


def parse_file(filename: str) -> int:
    """Parse file and return result."""
    bc = BrickColl()
    with open(filename) as f:
        for line in f:
            if line.strip():
                brick = Brick.from_str(line)
                print(brick)
                bc.add_brick(brick)
    if len(bc.all_bricks()) < 10:
        bc.pretty()
    bc.drop_bricks()
    if len(bc.all_bricks()) < 10:
        bc.pretty()
    to_zap = bc.bricks_to_disintegrate()
    # print(to_zap)
    print(sorted(b.name for b in to_zap))
    return len(to_zap)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
