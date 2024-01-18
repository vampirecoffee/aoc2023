"""Part 1 of the Scratchcards problem."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import re

card_re = re.compile(r'Card.*(\d+): (.*) \| (.*)')

@dataclass
class Card:
    """A scratchcard with winning numbers and numbers that you have."""
    winning_numbers: list[int]
    you_have: list[int]

    @classmethod
    def from_str(cls, s: str) -> Card:
        """Create a Card from a string representation."""
        m = card_re.search(s)
        if m is None:
            raise RuntimeError(f"Unable to create card from string {s}")
        winning_numbers = [int(e) for e in m.group(2).split()]
        you_have = [int(e) for e in m.group(3).split()]
        return cls(winning_numbers=winning_numbers, you_have=you_have)

    def score(self) -> int:
        """Score this card."""
        have_wins = [e in self.winning_numbers for e in self.you_have]
        count_wins = sum(have_wins)
        if count_wins == 0:
            return 0
        return 2**(count_wins-1)

def score_file(filename: str) -> int:
    """Score all cards in a file."""
    card_sum = 0
    with open(filename, encoding="utf-8") as f:
        for line in f:
            card = Card.from_str(line)
            card_sum += card.score()
    return card_sum


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(score_file(args.filename))

if __name__ == "__main__":
    main()
