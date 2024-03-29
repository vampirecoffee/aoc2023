"""Solution for part 1 of the Gear Ratios problem."""

from __future__ import annotations

import argparse
import itertools
import string
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Point:
    """One point in XY space."""

    x: int
    y: int

    def adjacent_points(self, max_x: int = 10, max_y: int = 10) -> set[Point]:
        """All points that are 'next to' this one."""
        valid_x: list[int] = [self.x]
        if self.x > 0:
            valid_x += [self.x - 1]
        if self.x < max_x:
            valid_x += [self.x + 1]
        valid_y: list[int] = [self.y]
        if self.y > 0:
            valid_y += [self.y - 1]
        if self.y < max_y:
            valid_y += [self.y + 1]
        out = set(Point(x, y) for x, y in itertools.product(valid_x, valid_y))
        out.remove(self)
        return out


@dataclass
class Number:
    """One 'number' in our schematic."""

    n: int
    start_x: int
    end_x: int
    y: int

    @classmethod
    def first_in_str(cls, s: str, y: int, incr_x_by: int = 0) -> Optional[Number]:
        """Get the first Number in a string.

        Make sure to give it the line number (y) also.
        """
        if not any(e in s for e in string.digits):
            return None
        start_x = first_digit_idx(s)
        str_n = ""
        for char in s[start_x:]:
            if not char in string.digits:
                break
            str_n += char
        end_x = start_x + len(str_n)
        if incr_x_by != 0:
            start_x += incr_x_by
            end_x += incr_x_by
        return cls(n=int(str_n), start_x=start_x, end_x=end_x, y=y)

    def adjacent_points(self, max_x: int = 10, max_y: int = 10) -> set[Point]:
        """Get all points adjacent to this number."""
        this_number_points = [Point(x, self.y) for x in range(self.start_x, self.end_x)]
        out: set[Point] = set()
        for point in this_number_points:
            out = out.union(point.adjacent_points(max_x=max_x, max_y=max_y))
        return out

    def is_adjacent_to(self, p: Point) -> bool:
        """Is this number adjacent to this point?"""
        x_coords = list(range(self.start_x - 1, self.end_x + 1))
        y_coords = [self.y - 1, self.y, self.y + 1]
        return (p.x in x_coords) and (p.y in y_coords)


def first_digit_idx(s: str) -> int:
    """Return the index of the first digit in this string."""
    digits_in_s = [d for d in string.digits if d in s]
    if not digits_in_s:
        raise RuntimeError("no digits in this line!")
    return min(s.index(d) for d in digits_in_s)


def not_symbols() -> set[str]:
    """Return a set of all the characters that are not 'symbols'."""
    out = set(e for e in string.digits)
    out.add(".")
    return out


def is_symbol(char: str) -> bool:
    """Is this character a 'symbol' or not?"""
    if len(char) != 1:
        raise RuntimeError(f"expected a single character, not `{char}`")
    if char in not_symbols():
        return False
    return True


def symbols_in_line(line: str) -> list[str]:
    """Find all the symbols in this line."""
    ns = not_symbols()
    out: list[str] = []
    for char in line:
        if char not in ns:
            out.append(char)
    return out


def find_numbers_in_line(line: str, y: int) -> list[Number]:
    """Find all the numbers in a given line."""
    numbers: list[Number] = []
    number = Number.first_in_str(line, y)
    while number is not None:
        numbers.append(number)
        incr_x_by = number.end_x
        number = Number.first_in_str(line[incr_x_by:], y, incr_x_by=incr_x_by)
    return numbers


def is_gear(char: str, p: Point, all_numbers: list[Number]) -> bool:
    """Return true iff the character at point is a gear."""
    if len(char) != 1:
        raise ValueError(f"expected a single character, not `{char}`")
    if char != "*":
        return False
    count_adjacent_numbers: int = 0
    for number in all_numbers:
        if number.is_adjacent_to(p):
            count_adjacent_numbers += 1
            if count_adjacent_numbers > 2:
                return False
    return count_adjacent_numbers == 2


def get_gear_ratio(char: str, p: Point, all_numbers: list[Number]) -> int:
    """Get the gear ratio of a given character.

    Returns 0 if this character is not a gear.
    """
    if len(char) != 1:
        raise ValueError(f"expected a single character, not `{char}`")
    if char != "*":
        return 0
    count_adjacent_numbers: int = 0
    ratio = 1
    for number in all_numbers:
        if number.is_adjacent_to(p):
            count_adjacent_numbers += 1
            ratio *= number.n
            if count_adjacent_numbers > 2:
                return 0
    if count_adjacent_numbers != 2:
        return 0
    return ratio


def parse_schematic(filename: str) -> int:
    """Parse schematic file."""
    schematic: list[str] = []
    with open(filename, encoding="utf-8") as f:
        schematic = f.readlines()
    max_x = 0  # starting value
    for line in schematic:
        line_len = len(line.strip())
        if line_len != 0 and max_x != 0 and line_len != max_x + 1:
            raise RuntimeError(
                f"this line has a length of {line_len} which is different from"
                f" {max_x+1}"
            )
        max_x = line_len - 1
    numbers_by_line: defaultdict[int, list[Number]] = defaultdict(list)
    for y, line in enumerate(schematic):
        numbers_by_line[y] = find_numbers_in_line(line, y)
    sum_of_ratios = 0
    for y, line in enumerate(schematic):
        relevant_numbers = (
            numbers_by_line[y] + numbers_by_line[y - 1] + numbers_by_line[y + 1]
        )
        for x, char in enumerate(line):
            p = Point(x, y)
            sum_of_ratios += get_gear_ratio(char, p, relevant_numbers)
    return sum_of_ratios


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_schematic(args.filename))


if __name__ == "__main__":
    main()
