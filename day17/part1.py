"""Crucible problem."""

from __future__ import annotations
from copy import deepcopy
import functools
from typing import Optional
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
import math
import itertools
import enum
import argparse

# I have these library stubs installed but ale can't find them??? lol
from tqdm import tqdm  # type: ignore[import-untyped]


@enum.unique
class Dir(enum.Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

    def as_char(self) -> str:
        """Return this direction as a character: >, <, ^, or v."""
        if self == Dir.LEFT:
            return "<"
        elif self == Dir.RIGHT:
            return ">"
        elif self == Dir.UP:
            return "^"
        elif self == Dir.DOWN:
            return "v"
        else:
            raise ValueError(f"Unrecognized direction {self}")

    def reverse(self) -> Dir:
        """Return the opposite of this direction."""
        if self == Dir.LEFT:
            return Dir.RIGHT
        elif self == Dir.RIGHT:
            return Dir.LEFT
        elif self == Dir.UP:
            return Dir.DOWN
        elif self == Dir.DOWN:
            return Dir.UP
        else:
            raise ValueError(f"Unrecognized direction {self}")


@functools.cache
def take_step(row: int, col: int, step_dir: Dir) -> tuple[int, int]:
    """Take one step in the given direction, and you go to ... where?"""
    if step_dir == Dir.LEFT:
        return (row, col - 1)
    elif step_dir == Dir.RIGHT:
        return (row, col + 1)
    elif step_dir == Dir.UP:
        return (row - 1, col)
    elif step_dir == Dir.DOWN:
        return (row + 1, col)
    else:
        raise ValueError(f"Unrecognized direction {step_dir}")


@dataclass(frozen=True)
class PathIsh:
    prev: Optional[Dir]
    prev2: Optional[Dir]
    prev3: Optional[Dir]

    @property
    def valid(self) -> bool:
        """True iff this PathIsh is valid.

        It's not valid to double back on yourself.

        It's not valid to have None as a step *after* a non-None step.
        """
        if self.prev is not None and self.prev.reverse() == self.prev2:
            return False

        if self.prev2 is not None:
            if any(
                (
                    self.prev is None,
                    self.prev2.reverse() == self.prev3,
                )
            ):
                return False
        if self.prev3 is not None:
            if any(
                (
                    self.prev is None,
                    self.prev2 is None,
                ),
            ):
                return False

        return True

    @classmethod
    def first(cls) -> PathIsh:
        """The starting 'path-ish'."""
        return PathIsh(None, None, None)

    @property
    def prev1(self) -> Optional[Dir]:
        """Odds I type this by mistake: 100%."""
        return self.prev

    @property
    def consec_steps(self) -> int:
        """How many consecutive steps we've taken in this direction.

        It'll be greater than 0, unless everything is None.
        """
        if self.prev is None:
            return 0
        steps = 1
        if self.prev == self.prev2:
            steps += 1
            if self.prev == self.prev3:
                steps += 1
        return steps

    @property
    def at_max_consec_steps(self) -> bool:
        """Is this showing the maximum number of consecutive steps?"""
        return all(
            (
                self.prev is not None,
                self.prev2 is not None,
                self.prev3 is not None,
                self.prev == self.prev2,
                self.prev == self.prev3,
            )
        )

    @property
    def valid_next_dirs(self) -> list[Dir]:
        """Return a list of valid next directions to go."""
        out = list(Dir)
        if self.prev is not None:
            if self.at_max_consec_steps:
                out.remove(self.prev)
            out.remove(self.prev.reverse())
        return out

    def take_step(self, step: Dir) -> PathIsh:
        """If you take a step in a direction, what's that step's PathIsh?"""
        if self.prev == step:
            assert not self.at_max_consec_steps
        return PathIsh(step, self.prev, self.prev2)

    @property
    def valid_next_paths(self) -> list[PathIsh]:
        """Which paths are valid next, given this one?"""
        next_dirs = self.valid_next_dirs
        return [self.take_step(d) for d in next_dirs]


@functools.cache
def _all_path_ish() -> list[PathIsh]:
    """Get a list of all possible PathIsh-es.

    Does NOT include the ones with None. Just fyi."""
    out: list[PathIsh] = []
    for a, b, c in itertools.product(list(Dir), repeat=3):
        path = PathIsh(a, b, c)
        if path.valid:
            out.append(path)
    return out


# You're supposed to set maximum distance to "infinity" in all these graph problems
# but this is close enough
_inf = 99999999999999999999999999999999999999999999999

_max_row = _inf
_max_col = _inf


@functools.cache
def _paths_from_origin() -> dict[tuple[int, int], list[PathIsh]]:
    """Follow all paths from the origin.

    This *includes* the ones with None.
    """
    dir_opts: list[Optional[Dir]] = list(Dir)
    dir_opts.append(None)
    out: dict[tuple[int, int], list[PathIsh]] = {
        (row, col): [] for row, col in itertools.product(list(range(0, 4)), repeat=2)
    }
    for a, b, c in itertools.product(dir_opts, repeat=3):
        path = PathIsh(c, b, a)
        if not path.valid:
            continue
        row, col = 0, 0
        for step in [a, b, c]:
            if step is None:
                break
            row, col = take_step(row, col, step)
            if row < 0 or col < 0:
                break  # if we go off the grid, that's not valid
        if row < 0 or col < 0:
            continue
        out[(row, col)].append(path)

    return out


@functools.cache
def _only_valid_paths(
    row: int, col: int, max_row=_max_row, max_col=_max_col
) -> list[PathIsh]:
    everything = set(_all_path_ish())
    to_remove: set[PathIsh] = set()
    for row in range(0, 3):
        # row 0: can't get here by going down (at all)
        # row 1: can't get here by going down 2 or 3 steps
        # row 2: can't get here by going down 3 steps
        for pi in everything:
            if pi.prev == Dir.DOWN and pi.consec_steps in range(row, 4):
                to_remove.add(pi)
    for row in range(max_row, max_row - 3, -1):
        # max_row: can't get here by going up (at all)
        # max_row - 1: can't get here by going up 2 or 3 steps
        # max_row - 2: can't get here by going up 3 steps
        start_range = row - (max_row - 3)
        for pi in everything:
            if pi.prev == Dir.UP and pi.consec_steps in range(start_range, 4):
                to_remove.add(pi)
    for col in range(0, 3):
        # col 0: can't get here by going right (at all)
        # etc
        for pi in everything:
            if pi.prev == Dir.RIGHT and pi.consec_steps in range(col, 4):
                to_remove.add(pi)
    for col in range(max_col, max_col - 3, -1):
        # max_col: can't get here by going left (at all)
        # etc
        start_range = col - (max_col - 3)
        for pi in everything:
            if pi.prev == Dir.LEFT and pi.consec_steps in range(start_range, 4):
                to_remove.add(pi)

    # Special cases for the top-left corner
    if row in range(0, 4) and col in range(0, 4):
        special: list[PathIsh] = _paths_from_origin()[(row, col)]
        for pi in special:
            everything.add(pi)

    out = everything - to_remove
    return list(out)


@dataclass
class Block:
    """One block in our lava city."""

    cost: int  # How much does it cost to cross this block?
    row: int
    col: int
    dist_by_path: defaultdict[PathIsh, int] = field(
        default_factory=lambda: defaultdict(lambda: _inf)
    )
    best_path: PathIsh = PathIsh.first()

    def __hash__(self) -> int:
        """Return the hash for this block."""
        fs = frozenset((k, v) for k, v in self.dist_by_path.items())
        return sum(
            [
                hash(self.cost),
                hash(self.row),
                hash(self.col),
                hash(fs),
            ]
        )

    @property
    def valid_paths(self) -> list[PathIsh]:
        """Return all the valid paths to get here."""
        valid_paths = _only_valid_paths(self.row, self.col)
        return valid_paths

    @property
    @functools.cache
    def fully_visited(self) -> bool:
        """Return True if we've fully visited this block."""
        return all(path in self.dist_by_path for path in self.valid_paths)

    @property
    @functools.cache
    def distance_from_origin(self) -> int:
        """How far is this block from the origin?"""
        if not self.dist_by_path:
            return _inf
        return min(v for v in self.dist_by_path.values())

    def visit_from(self, path: PathIsh, dist: int) -> None:
        """Visit from a given path, which is `dist` away from origin."""
        self.dist_by_path[path] = min(self.dist_by_path[path], dist)

    @property
    @functools.cache
    def _best_path(self) -> PathIsh:
        """Return the 'best' path to this block."""
        if self.distance_from_origin == _inf:
            raise RuntimeError("you gotta, like, set a path first, bro")
        best_path: PathIsh
        best_dist: int = _inf
        for path, dist in self.dist_by_path.items():
            if dist < best_dist:
                best_dist = dist
                best_path = path
        return best_path

    @property
    @functools.cache
    def best_path_str(self) -> str:
        """Return a string showing the best path on this cell."""
        bp = self._best_path
        if bp.prev is not None:
            return bp.prev.as_char()
        return str(self.cost)

    @property
    @functools.cache
    def prev(self) -> tuple[int, int]:
        """Return the coordinates of the previous block.

        Uses the 'best' path.
        """
        bp = self._best_path
        if bp.prev is not None:
            backwards = bp.prev.reverse()
            return take_step(self.row, self.col, backwards)
        return (self.row, self.col)


# I'm only making this class so I don't lose track of my tuples
@dataclass(frozen=True)
class VisitPlan:
    path: PathIsh
    row: int
    col: int
    distance: int

    @classmethod
    def first(cls) -> VisitPlan:
        """The visit plan you should start with, every time."""
        return VisitPlan(
            path=PathIsh.first(),
            row=0,
            col=0,
            distance=0,
        )

    def worse_than(self, other: VisitPlan) -> bool:
        """Return True if this visit plan is exactly like other, but worse.

        That is: they have the same paths, rows, and columns,
        but this plan's distance is greater than (or equal to) other's.
        """
        return all(
            (
                self.path == other.path,
                self.row == other.row,
                self.col == other.col,
                self.distance >= other.distance,
            )
        )


@dataclass
class City:
    blocks: list[list[Block]] = field(default_factory=list)

    def pretty(self) -> str:
        """Print the city."""
        return "\n".join(
            "".join([str(block.cost) for block in row]) for row in self.blocks
        )

    def path(self) -> list[tuple[int, int]]:
        """The nodes used as the path through the city."""
        end_block = self.blocks[-1][-1]
        path_nodes = [(end_block.row, end_block.col)]
        row = end_block.row
        col = end_block.col
        while not all((row == 0, col == 0)):
            if row == 0:
                print("best path to", row, col)
                print(self.blocks[row][col]._best_path)
            row, col = self.blocks[row][col].prev
            path_nodes.append((row, col))
        return path_nodes

    def pretty_path(self) -> str:
        """Print the path through the city."""
        path_nodes = self.path()
        out_rows: list[str] = []
        for i in range(len(self.blocks)):
            row: list[str] = []
            for j in range(len(self.blocks[0])):
                block = self.blocks[i][j]
                if (i, j) in path_nodes:
                    row.append(block.best_path_str)
                else:
                    row.append(str(block.cost))
            out_rows.append("".join(row))
        return "\n".join(out_rows)

    def __hash__(self) -> int:
        """Hash function.

        Helps out functools' caching.
        """
        block_tuple = tuple(tuple(row) for row in self.blocks)
        return hash(block_tuple)

    def add_row(self, row: str) -> None:
        """Add a row (represented as a string)."""
        row = row.strip()
        if not row:
            return
        row_idx = len(self.blocks)
        block_row = [
            Block(int(char), row_idx, col_idx) for col_idx, char in enumerate(row)
        ]
        self.blocks.append(block_row)
        self._set_max()

    def _set_max(self) -> None:
        """Set _max_row and _max_col."""
        global _max_row
        global _max_char
        _max_row = len(self.blocks) - 1
        _max_col = len(self.blocks[0]) - 1

    def valid_coords(self, row_idx: int, col_idx: int) -> bool:
        """Are these valid coordinates for this city?"""
        return all(
            (
                row_idx in range(0, len(self.blocks)),
                col_idx in range(0, len(self.blocks[0])),
            )
        )

    def visit(self, vp: VisitPlan) -> list[VisitPlan]:
        """Visit a block and return a list of new visits to plan."""
        block = self.blocks[vp.row][vp.col]
        if block.fully_visited and block.distance_from_origin <= vp.distance:
            return []
        # Visit
        block.visit_from(vp.path, vp.distance)
        self.blocks[vp.row][vp.col] = block
        # Where/how to go next?

        next_dist = vp.distance + block.cost
        next_paths = vp.path.valid_next_paths
        new_plans: list[VisitPlan] = []
        for path in next_paths:
            new_row, new_col = take_step(vp.row, vp.col, path.prev)
            if self.valid_coords(new_row, new_col):
                new_vp = VisitPlan(
                    path=path,
                    row=new_row,
                    col=new_col,
                    distance=next_dist,
                )
                new_plans.append(new_vp)
        return new_plans

    def walk(self) -> int:
        """Walk the graph, get shortest path."""
        plans: list[VisitPlan] = [VisitPlan.first()]

        # Total possible number of plans:
        # number of rows
        # times number of columns
        # times 5*5*5 (3 prev directions, 5 directions: r/l/d/u/None)
        max_plan_count = math.prod(
            [
                len(self.blocks),
                len(self.blocks[0]),
                5 * 5 * 5,
            ]
        )
        print("max plan count", max_plan_count)
        plans_executed: set[VisitPlan] = set()
        with tqdm(total=max_plan_count) as pbar:
            while plans:
                vp = plans.pop(0)
                new_plans = self.visit(vp)
                plans_executed.add(vp)
                pbar.update(1)
                for new_vp in new_plans:
                    if all(
                        (
                            not new_vp in plans_executed,
                            not any(new_vp.worse_than(p) for p in plans_executed),
                        )
                    ):
                        plans.append(new_vp)

        print()
        print(self.pretty())
        print()
        print(self.pretty_path())
        print()

        return self.blocks[-1][-1].distance_from_origin


def parse_file(filename: str) -> int:
    """Parse file, do the thing."""
    city = City()
    with open(filename) as f:
        for line in f:
            city.add_row(line)
    return city.walk()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
