"""Cube Conumdrum part 1."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import re

red_re = re.compile("(\d+) red")
green_re = re.compile("(\d+) green")
blue_re = re.compile("(\d+) blue")


def _count_from_re(r: re.Pattern, s: str) -> int:
    """Use the regexes above to get the relevant count."""
    m = r.search(s)
    if m is None:
        return 0
    return int(m.group(1))


@dataclass
class Round:
    red: int
    green: int
    blue: int

    @classmethod
    def from_str(cls, s: str) -> Round:
        """Create a round from a string.

        The string might look like:
            3 red, 2 green
            5 blue, 2 red, 1 green
            7 green, 1 red
        """
        red = _count_from_re(red_re, s)
        green = _count_from_re(green_re, s)
        blue = _count_from_re(blue_re, s)
        return cls(red=red, green=green, blue=blue)


@dataclass
class Game:
    """Game, w/ minimum numbers of cubes needed."""

    min_red: int
    min_green: int
    min_blue: int

    @classmethod
    def from_str(cls, s: str) -> Game:
        """Make a game from a string."""
        min_red = 0
        min_green = 0
        min_blue = 0
        all_round_strs = s.split(";")
        for round_str in all_round_strs:
            r = Round.from_str(round_str)
            if r.red > min_red:
                min_red = r.red
            if r.green > min_green:
                min_green = r.green
            if r.blue > min_blue:
                min_blue = r.blue
        return cls(
            min_red=min_red,
            min_green=min_green,
            min_blue=min_blue,
        )

    def power(self) -> int:
        """Get the 'power' of the minimum set of cubes for this game.

        This is just red * green * blue.
        """
        return self.min_red * self.min_green * self.min_blue


def sum_game_powers_in_file(filename: str) -> int:
    sum_game_powers = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            g = Game.from_str(line)
            sum_game_powers += g.power()
    return sum_game_powers


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(sum_game_powers_in_file(args.filename))


if __name__ == "__main__":
    main()
