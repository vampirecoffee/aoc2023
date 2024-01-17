"""Part 1 of Day 7."""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum

card_order = ["J"] + list(str(e) for e in range(2, 10)) + ["T", "Q", "K", "A"]
not_joker_cards = deepcopy(card_order)
not_joker_cards.remove("J")


def card_beats(first_card: str, second_card: str) -> bool:
    """Does the first card beat the second card?"""
    return card_order.index(first_card) > card_order.index(second_card)


class HandType(Enum):
    """Type of a hand in a game of Camel Cards."""

    HIGH_CARD = 0
    ONE_PAIR = 10
    TWO_PAIR = 20
    THREE = 30  # 3 of a kind
    FULL_HOUSE = 35
    FOUR = 40
    FIVE = 50

    def beats(self, other: HandType) -> bool:
        """Does this card beat the other one?"""
        return self.value > other.value


@dataclass
class Hand:
    """One hand in a game of CamelCards, with accompanying bet."""

    cards: str
    bid: int = 0

    @classmethod
    def from_str(cls, s: str) -> Hand:
        """Create a hand from a line in the input file."""
        parts = s.split()
        assert len(parts) == 2
        cards = parts[0].strip()
        assert all(c in card_order for c in cards)
        bid = int(parts[1])
        return cls(cards=cards, bid=bid)

    @property
    def hand_type(self) -> HandType:  # pylint: disable=too-many-return-statements
        """What type of hand is this?"""
        if "J" in self.cards:
            could_be_cards = [self.cards.replace("J", c) for c in not_joker_cards]
            could_be_hands = [Hand(cards) for cards in could_be_cards]
            could_be_types = [h.hand_type for h in could_be_hands]
            return max(could_be_types, key=lambda ht: ht.value)
        card_count: defaultdict[str, int] = defaultdict(int)
        for c in self.cards:
            card_count[c] += 1
        # What is the highest number of 'same cards'?
        mostest = max(card_count.values())
        if mostest == 5:
            return HandType.FIVE
        if mostest == 4:
            return HandType.FOUR
        if mostest == 3:
            if sorted(list(card_count.values())) == [2, 3]:
                return HandType.FULL_HOUSE
            return HandType.THREE
        if mostest == 2:
            if sorted(list(card_count.values())) == [1, 2, 2]:
                return HandType.TWO_PAIR
            return HandType.ONE_PAIR
        return HandType.HIGH_CARD

    def beats(self, other: Hand) -> bool:
        """Does this hand beat Other?"""
        if self.hand_type != other.hand_type:
            return self.hand_type.beats(other.hand_type)
        for i in range(0, 5):
            self_card = self.cards[i]
            other_card = other.cards[i]
            if self_card != other_card:
                return card_beats(self_card, other_card)
        raise RuntimeError(f"{self} and {other} are the same cards dude")

    def score(self) -> int:
        """Give this hand a 'score'.

        Hand type is worth 1 trillion * hand type value.

        Then each card contributes 2 digits.
        """
        hand_type_score = 1000000000000 * self.hand_type.value
        card_indexes = [card_order.index(c) for c in self.cards]
        card_score_list = [f"{i:02}" for i in card_indexes]
        card_score_str = "".join(card_score_list)
        card_score_str = card_score_str.lstrip("0")
        if card_score_str == "":
            card_score_str = "0"
        card_score = int(card_score_str)
        return hand_type_score + card_score

    def wins(self, rank: int) -> int:
        """How much does this hand win? (Bid * rank)"""
        return self.bid * rank


def create_hands(filename: str) -> list[Hand]:
    """Create hands from file."""
    with open(filename, encoding="utf-8") as f:
        return [Hand.from_str(line) for line in f]


def parse_file(filename: str) -> int:
    """Parse the whole file, do the puzzle, etc."""
    hands = create_hands(filename)
    hands.sort(key=lambda h: h.score())
    return sum(h.wins(i + 1) for i, h in enumerate(hands))


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
