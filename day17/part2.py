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

    def turns(self) -> tuple[Dir, Dir]:
        """Return valid 'turns'."""
        if self in (Dir.LEFT, Dir.RIGHT):
            return (Dir.UP, Dir.DOWN)
        else:
            return (Dir.LEFT, Dir.RIGHT)


@functools.cache
def take_step(row: int, col: int, step_dir: Dir) -> tuple[int, int]:
    """Take one step in the given direction, and you go to ... where?"""
    assert isinstance(row, int)
    assert isinstance(col, int)
    assert isinstance(step_dir, Dir)
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
class State:
    row: int
    col: int
    going: Dir
    distance: int


@dataclass
class City:
    grid: list[list[int]] = field(default_factory=list)
    height: int = 0
    width: int = 0
    end_row: int = 0
    end_col: int = 0
    seen_cost_by_state: dict[State, int] = field(default_factory=dict)
    state_queues_by_cost: dict[int, list[State]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_row(self, row: str) -> None:
        """Add a row (represented as a string)."""
        row = row.strip()
        if not row:
            return
        cost_row = [int(char) for char in row]
        self.grid.append(cost_row)
        self._set_max()

    def _set_max(self) -> None:
        """Set max_row and max_col."""
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.end_row = self.height - 1
        self.end_col = self.width - 1
        self.seen_cost_by_state = {}
        self.state_queues_by_cost = defaultdict(list)

    def move_and_add_state(self, state: State, cost: int) -> Optional[int]:
        """Add a state.

        Return cost iff this is the end.
        """
        new_row, new_col = take_step(state.row, state.col, state.going)
        if new_row < 0 or new_col < 0:
            return None
        if new_row >= self.height or new_col >= self.width:
            return None
        new_cost = cost + self.grid[new_row][new_col]
        if all(
            (
                new_row == self.end_row,
                new_col == self.end_col,
                state.distance >= 4,
            )
        ):
            print("the end!", new_cost)
            return new_cost
        new_state = State(new_row, new_col, state.going, state.distance)
        if new_state not in self.seen_cost_by_state:
            self.state_queues_by_cost[new_cost].append(new_state)
            self.seen_cost_by_state[new_state] = new_cost
        return None

    def walk(self) -> int:
        """Walk the graph, get shortest path."""
        self.seen_cost_by_state = {}
        self.state_queues_by_cost = defaultdict(list)
        for go in (Dir.DOWN, Dir.RIGHT):
            state = State(0, 0, go, 1)
            self.move_and_add_state(state, 0)

        while True:
            cur_cost = min(self.state_queues_by_cost.keys())
            next_states = self.state_queues_by_cost.pop(cur_cost)

            for state in next_states:
                bonus_states: list[State] = []
                if state.distance >= 4:
                    turn_a, turn_b = state.going.turns()
                    bonus_states += [
                        State(state.row, state.col, turn_dir, 1)
                        for turn_dir in (turn_a, turn_b)
                    ]
                if state.distance < 10:
                    bonus_states.append(
                        State(state.row, state.col, state.going, state.distance + 1),
                    )
                for bonus_state in bonus_states:
                    res = self.move_and_add_state(
                        bonus_state,
                        cur_cost,
                    )
                    if res is not None:
                        return res


def parse_file(filename: str) -> int:
    """Parse file, do the thing."""
    city = City()
    with open(filename) as f:
        for line in f:
            city.add_row(line)
    res = city.walk()
    return res


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
