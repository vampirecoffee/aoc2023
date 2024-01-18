"""Solution for part 1 of day 05."""

from __future__ import annotations

import argparse
import re
import string
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapRange:
    """Covers on range of numbers that can be converted."""

    src_start: int
    dest_start: int
    length: int

    @classmethod
    def from_str(cls, s: str) -> MapRange:
        """Create a MapRange from a string."""
        numbers = s.split()
        if len(numbers) != 3:
            raise ValueError(f"Cannot convert string {s} to a MapRange")
        dest_start = int(numbers[0])
        src_start = int(numbers[1])
        length = int(numbers[2])
        return cls(src_start, dest_start, length)

    def convert(self, src_n: int) -> int:
        """Convert a source n to a destination n."""
        assert src_n in self.source_range(), (
            f"{src_n} is not in range that starts at {self.src_start} with length"
            f" {self.length}"
        )
        delta = src_n - self.src_start
        return self.dest_start + delta

    def source_range(self) -> range:
        """Return the range of sources that are in this map."""
        return range(self.src_start, self.src_start + self.length)

    @property
    def source_end(self) -> int:
        """Return the last 'source' number in this range."""
        return self.src_start + self.length - 1


@dataclass
class Map:
    """Map an entire category from source to destination."""

    src_cat: str = ""  # source category
    dest_cat: str = ""  # destination category
    ranges: list[MapRange] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Post-init."""
        self.ranges.sort(key=lambda r: r.src_start)

    @classmethod
    def from_lines(cls, lines: list[str]) -> Map:
        """Convert a list of lines to a map."""
        if not any(d in lines[-1] for d in string.digits):
            lines = lines[:-1]
        src_cat, dest_cat = src_dest_from_str(lines[0])
        ranges: list[MapRange] = []
        for line in lines[1:]:
            ranges.append(MapRange.from_str(line))
        return cls(src_cat, dest_cat, ranges)

    def convert(self, src_n: int) -> int:
        """Convert a source in to a destination n."""
        for r in self.ranges:
            if src_n in r.source_range():
                return r.convert(src_n)
        return src_n


_seed_to_location: list[str] = [
    "seed",
    "soil",
    "fertilizer",
    "water",
    "light",
    "temperature",
    "humidity",  # maps to location
]


@dataclass
class Almanac:
    """Map many categories to many other categories."""

    seeds: list[int]
    maps_by_source: dict[str, Map] = field(default_factory=dict)

    def add_map(self, m: Map) -> None:
        """Add a map to this almanac."""
        self.maps_by_source[m.src_cat] = m

    def seed_to_location(self, seed: int) -> int:
        """Convert a seed number to a location number."""
        cur = seed
        for keyword in _seed_to_location:
            m = self.maps_by_source[keyword]
            cur = m.convert(cur)
        return cur

    def lowest_location(self) -> int:
        """Return the lowest location that we can get from this set of seeds."""
        return min(self.seed_to_location(s) for s in self.seeds)


x_to_y_re = re.compile(r"(\w+)-to-(\w+) map:")


def src_dest_from_str(s: str) -> tuple[str, str]:
    """Turn x-to-y map into the tuple (x,y)."""
    m = x_to_y_re.match(s)
    if m is None:
        raise ValueError(f"Cannot find x-to-y pattern in {s}")
    return (m.group(1), m.group(2))


def map_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """List of ranges showing maps."""
    maps_start_at: list[int] = []
    for i, line in enumerate(lines):
        if "map" in line:
            maps_start_at.append(i)
    maps_end_at = deepcopy(maps_start_at[1:])
    maps_end_at.append(len(lines))
    return list(zip(maps_start_at, maps_end_at))


def parse_file(filename: str) -> int:
    """Parse almanac file and return solution."""
    almanac_lines: list[str] = []
    with open(filename, encoding="utf-8") as f:
        almanac_lines = f.readlines()
    seed_line = almanac_lines[0]
    seed_match = re.search(r"seeds.*:(.*)", seed_line)
    if seed_match is None:
        raise RuntimeError(f"Cannot make seed-line match {seed_line}")
    seeds = [int(e) for e in seed_match.group(1).split()]
    almanac = Almanac(seeds)
    for map_start, map_end in map_ranges(almanac_lines):
        almanac.add_map(Map.from_lines(almanac_lines[map_start:map_end]))
    return almanac.lowest_location()


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
