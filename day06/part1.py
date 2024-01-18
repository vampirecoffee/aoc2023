"""Solution for part 1 of day 6."""

import argparse
import string
from dataclasses import dataclass


@dataclass
class Race:
    """One boat race (with a given time and distance)."""

    time: int
    distance: int

    def ways_to_beat(self) -> int:
        """How many ways are there to beat the record?"""
        shortest = self._shortest_hold()
        longest = self._longest_hold()
        return longest - shortest + 1

    def _shortest_hold(self) -> int:
        """Shortest hold that beats the record."""
        for hold in range(0, self.time + 1):
            if self.hold_time_beats(hold):
                return hold
        raise ValueError(f"race {self} is unbeatable!")

    def _longest_hold(self) -> int:
        """Longest hold that beats the record."""
        for hold in range(self.time, -1, -1):
            if self.hold_time_beats(hold):
                return hold
        raise RuntimeError(f"race {self} is unbeatable!")

    def distance_with_hold(self, hold: int) -> int:
        """How far will you travel if you hold the button for `hold` ms?"""
        speed = hold
        time_left = self.time - hold
        return speed * time_left

    def hold_time_beats(self, hold: int) -> int:
        """Will you beat the record if you hold the button this long?"""
        return self.distance_with_hold(hold) > self.distance


def races_from_file(filename: str) -> list[Race]:
    """Read races from file."""
    lines: list[str] = []
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2
    times_strs = [e for e in lines[0].split() if any(d in e for d in string.digits)]
    distances_strs = [e for e in lines[1].split() if any(d in e for d in string.digits)]
    times = [int(e) for e in times_strs]
    distances = [int(e) for e in distances_strs]
    races = [Race(t, d) for t, d in zip(times, distances)]
    return races


def ways_to_beat_all(races: list[Race]) -> int:
    """How many ways to beat all these races?"""
    ways = 1
    for r in races:
        ways *= r.ways_to_beat()
    return ways


def parse_file(filename: str) -> int:
    """Do the thing."""
    races = races_from_file(filename)
    return ways_to_beat_all(races)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
