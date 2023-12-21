"""Part 1 of Day 16."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from enum import Enum

from tqdm import tqdm


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

    def reset(self) -> None:
        """Reset this cell."""
        self.energized_from = {d: False for d in list(Dir)}


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

    def reset(self) -> None:
        """Reset the floor."""
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[0])):
                self.tiles[i][j].reset()

    def _start_dirs(self, start_row: int, start_col: int) -> list[Dir]:
        """Return valid starting dirs.

        There should only be 1 (for non-corners) or 2 (for corners)."""
        dirs: list[Dir] = []
        if start_row == 0:
            dirs.append(Dir.DOWN)
        elif start_row == len(self.tiles) - 1:
            dirs.append(Dir.UP)
        else:
            raise ValueError(f"Invalid starting row {start_row}")

        if start_col == 0:
            dirs.append(Dir.RIGHT)
        elif start_col == (len(self.tiles[0]) - 1):
            dirs.append(Dir.LEFT)
        else:
            raise ValueError(f"Invalid starting col {start_col}")
        return dirs

    def pew(self, start_row: int, start_col: int) -> int:
        """If you start from this tile, how many tiles can you energize?"""
        max_energized = 0
        for d in self._start_dirs(start_row, start_col):
            max_energized = max(max_energized, self._pew(start_row, start_col, d))
        return max_energized

    def _pew(self, start_row: int, start_col: int, start_dir: Dir) -> int:
        """How many tiles are energized with this starting beam?"""
        self.reset()
        beam_queue = [Beam(start_row, start_col, start_dir)]

        while beam_queue:
            beam = beam_queue.pop()
            new_dirs = self.tiles[beam.row][beam.col].beam(beam.going)
            for nd in new_dirs:
                new_row, new_col = go(beam.row, beam.col, nd)
                if self.valid_indexes(new_row, new_col):
                    beam_queue.append(Beam(new_row, new_col, nd))
        return self.count_energized()

    def count_energized(self) -> int:
        """Count how many tiles are energized."""
        row_sums = [sum(cell.energized for cell in row) for row in self.tiles]
        return sum(row_sums)

    def any_start(self) -> int:
        """How many cells can you energize, if you can start from any edge tile?"""
        max_energized = 0

        total_combos = (2 * len(self.tiles)) + (2 * len(self.tiles[0]))
        with tqdm(total=total_combos) as pbar:
            # Top and bottom rows
            bottom_row_idx = len(self.tiles) - 1
            for col_idx in range(len(self.tiles[0])):
                max_energized = max(max_energized, self._pew(0, col_idx, Dir.DOWN))
                pbar.update(1)
                max_energized = max(
                    max_energized, self._pew(bottom_row_idx, col_idx, Dir.UP)
                )
                pbar.update(1)

            # Left and right columns
            right_col_idx = len(self.tiles[0]) - 1
            for row_idx in range(len(self.tiles)):
                max_energized = max(max_energized, self._pew(row_idx, 0, Dir.RIGHT))
                pbar.update(1)
                max_energized = max(
                    max_energized, self._pew(row_idx, right_col_idx, Dir.LEFT)
                )
                pbar.update(1)

        return max_energized


def parse_file(filename: str) -> int:
    """Parse file, solve problem."""
    floor = Floor()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                floor.add_row(line)
    return floor.any_start()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
