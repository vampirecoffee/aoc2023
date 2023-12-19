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

MAX_RED = 12
MAX_GREEN = 13
MAX_BLUE = 14

def is_game_possible(game: str) -> bool:
    """Given a string defining a game, is that game possible?"""
    rounds = game.split(";")
    for round_str in rounds:
        r = Round.from_str(round_str)
        if r.red > MAX_RED or r.green > MAX_GREEN or r.blue > MAX_BLUE:
            return False
    return True

_game_id_re = re.compile("Game (\d+):")
def get_game_id(game: str) -> int:
    """Get game ID from the line."""
    m = _game_id_re.search(game)
    if m is None:
        raise RuntimeError(f"Unable to find ID of game `{game}`")
    return int(m.group(1))

def sum_valid_ids_in_file(filename: str) -> int:
    sum_game_ids = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if is_game_possible(line):
                sum_game_ids += get_game_id(line)
    return sum_game_ids

def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(sum_valid_ids_in_file(args.filename))

if __name__ == "__main__":
    main()
