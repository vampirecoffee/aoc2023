"""Part 1 of Day 16."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from enum import Enum


class Dir(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


def go(row: int, col: int, in_dir: Dir) -> tuple[int, int]:
    """Coordinates that are one step in `in_dir` from the given row/col index pair."""
    if in_dir == Dir.RIGHT:
        return (row, col + 1)
    elif in_dir == Dir.LEFT:
        return (row, col - 1)
    elif in_dir == Dir.UP:
        return (row - 1, col)
    elif in_dir == Dir.DOWN:
        return (row + 1, col)
    else:
        raise ValueError(f"Unrecognized direction {in_dir}")


class CellType(Enum):
    EMPTY = "."
    MIRROR_TILT_RIGHT = "/"
    MIRROR_TILT_LEFT = "\\"
    SPLITTER_VERT = "|"
    SPLITTER_HORIZ = "-"


def _mirror_tilt_right(travel_dir: Dir) -> Dir:
    """Beam enters a / mirror traveling in a direction. How does it bounce?"""
    if travel_dir == Dir.RIGHT:
        return Dir.UP
    elif travel_dir == Dir.DOWN:
        return Dir.LEFT
    elif travel_dir == Dir.LEFT:
        return Dir.DOWN
    elif travel_dir == Dir.UP:
        return Dir.RIGHT
    else:
        raise ValueError(f"Unrecognized direction {travel_dir}")


def _mirror_tilt_left(travel_dir: Dir) -> Dir:
    """Beam enters a \\ mirror traveling in a direction. How does it bounce?"""
    if travel_dir == Dir.RIGHT:
        return Dir.DOWN
    elif travel_dir == Dir.DOWN:
        return Dir.RIGHT
    elif travel_dir == Dir.LEFT:
        return Dir.UP
    elif travel_dir == Dir.UP:
        return Dir.LEFT
    else:
        raise ValueError(f"Unrecognized direction {travel_dir}")


@dataclass
class Cell:
    """One cell on the floor."""

    contents: CellType
    energized_from: dict[Dir, bool] = field(
        default_factory=lambda: {d: False for d in list(Dir)}
    )

    @property
    def energized(self) -> bool:
        """Is this cell energized?"""
        return any(en for en in self.energized_from.values())

    def beam(self, travel_dir: Dir) -> list[Dir]:
        """Beam travels in - where does it go?"""
        if self.energized_from[travel_dir]:
            return []
        self.energized_from[travel_dir] = True

        if self.contents == CellType.EMPTY:
            return [travel_dir]

        elif self.contents == CellType.MIRROR_TILT_RIGHT:
            return [_mirror_tilt_right(travel_dir)]

        elif self.contents == CellType.MIRROR_TILT_LEFT:
            return [_mirror_tilt_left(travel_dir)]

        elif self.contents == CellType.SPLITTER_VERT:
            if travel_dir in (Dir.UP, Dir.DOWN):
                return [travel_dir]
            else:
                return [Dir.UP, Dir.DOWN]

        elif self.contents == CellType.SPLITTER_HORIZ:
            if travel_dir in (Dir.LEFT, Dir.RIGHT):
                return [travel_dir]
            else:
                return [Dir.LEFT, Dir.RIGHT]

        else:
            raise ValueError(f"Unrecognized travel dir {travel_dir}")


@dataclass(frozen=True)
class Beam:
    row: int
    col: int
    going: Dir


@dataclass
class Floor:
    """The entire floor, as a list."""

    tiles: list[list[Cell]] = field(default_factory=list)

    def add_row(self, row: str) -> None:
        """Add a row."""
        row = row.strip()
        cell_types = [CellType(char) for char in row]
        cell_row = [Cell(ct) for ct in cell_types]
        self.tiles.append(cell_row)
        return

    def valid_indexes(self, row: int, col: int) -> bool:
        """Are these valid indexes for this floor?"""
        return all(
            (
                row in range(0, len(self.tiles)),
                col in range(0, len(self.tiles[0])),
            )
        )

    def pew(self) -> None:
        """Send a beam of light to the right from the top-left tile."""
        beam_queue = [Beam(0, 0, Dir.RIGHT)]

        while beam_queue:
            beam = beam_queue.pop()
            new_dirs = self.tiles[beam.row][beam.col].beam(beam.going)
            for nd in new_dirs:
                new_row, new_col = go(beam.row, beam.col, nd)
                if self.valid_indexes(new_row, new_col):
                    beam_queue.append(Beam(new_row, new_col, nd))

    def count_energized(self) -> int:
        """Count how many tiles are energized."""
        self.pew()
        row_sums = [sum(cell.energized for cell in row) for row in self.tiles]
        return sum(row_sums)


def parse_file(filename: str) -> int:
    """Parse file, solve problem."""
    floor = Floor()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                floor.add_row(line)
    return floor.count_energized()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
