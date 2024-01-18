"""Part 1 of solution for day 14."""

from __future__ import annotations

import argparse


def read_input(filename: str) -> list[list[str]]:
    """Read the input, returning a list of columns."""
    out: list[list[str]] = []
    with open(filename) as f:
        for line in f:
            if not out:
                # List does not exist, make it
                for char in line:
                    out.append([char])
            else:
                for i, char in enumerate(line):
                    out[i].append(char)
    return out


def score_tilted_segment(seg: list[str], largest_idx: int) -> int:
    """Score a pre-tilted segment."""
    count_rocks = seg.count("O")
    return sum(i for i in range(largest_idx, largest_idx - count_rocks, -1))


def tilt(column: list[str]) -> int:
    """Tilt a column and return its score."""
    cube_indexes: list[int] = []
    for _ in range(0, column.count("#")):
        if not cube_indexes:
            last_index = -1
        else:
            last_index = cube_indexes[-1]
        cube_indexes.append(column.index("#", last_index + 1))

    if not cube_indexes:
        return score_tilted_segment(column, len(column))
    # Otherwise ...
    out = 0
    cube_indexes.append(len(column) + 2)
    cube_indexes = [-1] + cube_indexes

    for i in range(len(cube_indexes) - 1):
        start_idx = cube_indexes[i]
        end_idx = cube_indexes[i + 1]
        if start_idx == -1:
            substr = column[0:end_idx]
        else:
            substr = column[start_idx:end_idx]
        largest_idx_in_segment = len(column) - start_idx - 1
        out += score_tilted_segment(substr, largest_idx_in_segment)

    return out


def parse_file(filename: str) -> int:
    """Parse file and solve problem."""
    platform = read_input(filename)
    out = 0
    for col in platform:
        t = tilt(col)
        print("col", "".join(col), "sum", t)
        out += t
    return out


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
