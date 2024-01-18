"""Part 1 of the Pipe Maze problem."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    """Compass direction."""

    NORTH = 1
    WEST = 2
    EAST = 3
    SOUTH = 4


@dataclass
class Cell:
    """One cell in our map/grid/graph/thing."""

    shape: str
    is_start: bool = False
    reachable_from_start: bool = False

    def is_pipe(self) -> bool:
        """Is this a pipe, or empty ground?"""
        return self.shape != "."

    def goes_north(self) -> bool:
        """Does this pipe connect to the north?"""
        return self.shape in ("|", "L", "J")

    def goes_west(self) -> bool:
        """Does this pipe connect to the west?"""
        return self.shape in ("-", "J", "7")

    def goes_east(self) -> bool:
        """Does this pipe connect to the east?"""
        return self.shape in ("-", "L", "F")

    def goes_south(self) -> bool:
        """Does this pipe connect to the south?"""
        return self.shape in ("|", "7", "F")

    def next_dir(self, came_from: Direction) -> Direction:
        """If you came in from X, where do you go out?"""
        if self.goes_north() and came_from != Direction.NORTH:
            return Direction.NORTH
        if self.goes_west() and came_from != Direction.WEST:
            return Direction.WEST
        if self.goes_east() and came_from != Direction.EAST:
            return Direction.EAST
        if self.goes_south() and came_from != Direction.SOUTH:
            return Direction.SOUTH
        raise RuntimeError(
            f"Not sure how to leave cell of shape {self.shape} when entering from"
            f" {came_from}"
        )

    @classmethod
    def from_char(cls, char: str) -> Cell:
        """Create a cell from a character.

        If the character is S, S will be the 'shape' too.
        """
        if len(char) != 1:
            raise ValueError("pass in precisely one character")
        if char not in ("|", "-", "L", "J", "7", "F", ".", "S"):
            raise ValueError(f"unrecognized cell character {char}")
        is_start = char == "S"
        return cls(shape=char, is_start=is_start, reachable_from_start=is_start)

    def reachable_char(self) -> str:
        """Print a character depending on reachability."""
        if self.shape == ".":
            return "."
        if self.reachable_from_start:
            return "T"
        return "F"


@dataclass
class Maze:
    """A maze: cells + start coordinates."""

    cells: list[list[Cell]]
    start_row: int
    start_col: int

    @classmethod
    def from_strs(cls, rows: list[str]) -> Maze:
        """Create a pipe maze from a list of strings."""
        start_row = 0
        start_col = 0
        cells: list[list[Cell]] = []
        for i, row in enumerate(rows):
            cell_row: list[Cell] = []
            stripped_row = row.strip()
            for j, char in enumerate(stripped_row):
                new_cell = Cell.from_char(char)
                cell_row.append(new_cell)
                if new_cell.is_start:
                    start_row = i
                    start_col = j
            cells.append(cell_row)
        return cls(cells, start_row, start_col)

    def print_pipes(self) -> None:
        """Print the pipes."""
        for row in self.cells:
            out_row = "".join([c.shape for c in row])
            print(out_row)

    def print_reachability(self) -> None:
        """Print the reachability status."""
        for row in self.cells:
            out_row = "".join([c.reachable_char() for c in row])
            print(out_row)

    def find_start_shape(self) -> str:
        """Find the shape of the starting pipe."""
        goes_north: bool = False
        goes_south: bool = False
        goes_west: bool = False
        goes_east: bool = False
        if (
            self.start_row != 0
            and self.cells[self.start_row - 1][self.start_col].goes_south()
        ):
            goes_north = True
        if (self.start_row < (len(self.cells) - 1)) and self.cells[self.start_row + 1][
            self.start_col
        ].goes_north():
            goes_south = True
        if (self.start_col != 0) and self.cells[self.start_row][
            self.start_col - 1
        ].goes_east():
            goes_west = True
        if (self.start_col < (len(self.cells[0]) - 1)) and self.cells[self.start_row][
            self.start_col + 1
        ].goes_west():
            goes_east = True
        if goes_north and goes_south:
            return "|"
        if goes_east and goes_west:
            return "-"
        if goes_north and goes_east:
            return "L"
        if goes_north and goes_west:
            return "J"
        if goes_south and goes_west:
            return "7"
        if goes_south and goes_east:
            return "F"
        raise RuntimeError("not sure what to do with this pipe")

    def set_start_shape(self) -> None:
        """Set the shape of the starting pipe."""
        start_shape = self.find_start_shape()
        self.cells[self.start_row][self.start_col].shape = start_shape

    def walk_tiles(self) -> None:
        """Walk the tiles and set them as reachable."""
        self.print_pipes()
        self.set_start_shape()
        cur_row = self.start_row
        cur_col = self.start_col
        # print("starting at", cur_row, cur_col)
        self._visit(cur_row, cur_col)
        start_cell = self.cells[cur_row][cur_col]
        cur_dir: Direction
        if start_cell.goes_north():
            cur_dir = Direction.NORTH
        elif start_cell.goes_west():
            cur_dir = Direction.WEST
        elif start_cell.goes_east():
            cur_dir = Direction.EAST
        elif start_cell.goes_south():
            cur_dir = Direction.SOUTH
        else:
            raise RuntimeError("starting cell does not seem to go anywhere")
        cur_row, cur_col, cur_dir = self._next_idx(cur_row, cur_col, cur_dir)
        # print(cur_row, cur_col, cur_dir)
        while not (cur_row == self.start_row and cur_col == self.start_col):
            # print("visiting", cur_row, cur_col)
            self._visit(cur_row, cur_col)
            cur_row, cur_col, cur_dir = self._next_idx(cur_row, cur_col, cur_dir)
            # print("next up:", cur_row, cur_col, cur_dir)
        # print("all done!")
        self.print_reachability()

    def count_reachable_tiles(self) -> int:
        """Count how many tiles are reachable from the start."""
        self.walk_tiles()
        reachable = 0
        for cell_row in self.cells:
            reachable += sum(c.reachable_from_start for c in cell_row)
        return reachable

    def _visit(self, row_idx: int, col_idx: int) -> None:
        """Visit a tile."""
        self.cells[row_idx][col_idx].reachable_from_start = True

    def _next_idx(
        self, row_idx: int, col_idx: int, in_dir: Direction
    ) -> tuple[int, int, Direction]:
        """Get indexes, and direction, of the next cell to visit."""
        next_dir = self.cells[row_idx][col_idx].next_dir(in_dir)
        if next_dir == Direction.NORTH:
            # If you go north, you actually "enter" a cell from the south
            return (row_idx - 1, col_idx, Direction.SOUTH)
        if next_dir == Direction.WEST:
            return (row_idx, col_idx - 1, Direction.EAST)
        if next_dir == Direction.EAST:
            return (row_idx, col_idx + 1, Direction.WEST)
        if next_dir == Direction.SOUTH:
            return (row_idx + 1, col_idx, Direction.NORTH)
        raise RuntimeError(f"Unrecognized direction {next_dir}")


def parse_file(filename: str) -> int:
    """Turn file into maze, return the farthest distance from start."""
    lines: list[str]
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    maze = Maze.from_strs(lines)
    reachable_count = maze.count_reachable_tiles()
    return int(reachable_count / 2)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
