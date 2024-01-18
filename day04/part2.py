"""Part 2 of the Scratchcards problem."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import re

card_re = re.compile(r"Card\s*(\d+): (.*) \| (.*)")


@dataclass
class Card:
    """A scratchcard with winning numbers and numbers that you have."""

    winning_numbers: list[int]
    you_have: list[int]
    number: int

    @classmethod
    def from_str(cls, s: str) -> Card:
        """Create a Card from a string representation."""
        m = card_re.search(s)
        if m is None:
            raise RuntimeError(f"Unable to create card from string {s}")
        winning_numbers = [int(e) for e in m.group(2).split()]
        you_have = [int(e) for e in m.group(3).split()]
        number = int(m.group(1))
        return cls(
            winning_numbers=winning_numbers, you_have=you_have, number=number
        )

    def gives_cards(self) -> list[int]:
        """If this card 'wins', what cards does it give you?"""
        have_wins = [e in self.winning_numbers for e in self.you_have]
        count_wins = sum(have_wins)
        if count_wins == 0:
            return []
        return list(range(self.number + 1, self.number + count_wins + 1))


def score_file(filename: str) -> int:
    """Score all cards in a file."""
    # Map IDs to how many extra copies we have
    extra_copies: defaultdict[int, int] = defaultdict(int)
    scratchcard_count = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            card = Card.from_str(line)
            how_many_copies = extra_copies[card.number] + 1
            scratchcard_count += how_many_copies
            for bonus_card in card.gives_cards():
                extra_copies[bonus_card] += how_many_copies
    return scratchcard_count


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(score_file(args.filename))


if __name__ == "__main__":
    main()
