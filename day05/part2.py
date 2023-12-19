"""Solution for part 2 of day 05."""
from __future__ import annotations

from copy import deepcopy
import argparse
import string
from collections import defaultdict
from dataclasses import dataclass, field
import re

from tqdm import tqdm  # type: ignore[import-untyped]


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
        assert (
            src_n in self.source_range()
        ), f"{src_n} is not in range that starts at {self.src_start} with length {self.length}"
        delta = src_n - self.src_start
        return self.dest_start + delta

    def source_range(self) -> range:
        """Return the range of sources that are in this map."""
        return range(self.src_start, self.src_start + self.length)

    def convert_range(self, start_n: int, size: int) -> tuple[int, int]:
        """Convert an entire range in this map."""
        assert start_n in self.source_range()
        assert start_n + size - 1 in self.source_range()
        return (self.convert(start_n), size)

    @property
    def source_end(self) -> int:
        return self.src_start + self.length - 1

    @property
    def range_end(self) -> int:
        return self.src_start + self.length


@dataclass
class Map:
    """Map an entire category from source to destination."""

    src_cat: str = ""  # source category
    dest_cat: str = ""  # destination category
    ranges: list[MapRange] = field(default_factory=list)

    def __post_init__(self):
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

    def convert_range(self, start_n: int, size: int) -> list[tuple[int, int]]:
        """Convert a range to output ranges."""
        mrs = deepcopy(self.ranges)
        mrs.sort(key=lambda r: r.src_start)
        end_n = start_n + size
        ranges_out: list[tuple[int, int]] = []
        for mr in mrs:
            if size == 0:
                break
            if start_n > mr.source_end:
                continue
            if start_n < mr.src_start:
                missing_start = start_n
                missing_size = min(mr.src_start - missing_start, size)
                ranges_out.append((missing_start, missing_size))
                start_n = mr.src_start
                size -= missing_size
                if size == 0:
                    break
            want_size = size
            if start_n + want_size > mr.range_end:
                want_size = mr.range_end - start_n
            got_range = mr.convert_range(start_n, want_size)
            ranges_out.append(got_range)
            size -= want_size
            start_n += want_size
        if size != 0:
            ranges_out.append((start_n, size))
        return ranges_out

    def convert_ranges(self, ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Convert a list of input ranges to a list of output ranges."""
        ranges_out: list[tuple[int, int]] = []
        for start_n, size in tqdm(ranges):
            ranges_out += self.convert_range(start_n, size)
        return ranges_out


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

    seed_ranges: list[tuple[int, int]]
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

    def seed_range_to_min_location(self, start: int, size: int) -> int:
        """Turn a seed range into a minimum location."""
        cur = [(start, size)]
        for keyword in tqdm(_seed_to_location):
            m = self.maps_by_source[keyword]
            cur = m.convert_ranges(cur)
        locations = [e[0] for e in cur]
        return min(locations)

    def lowest_loc_in_range(self, start: int, size: int) -> int:
        return min(self.seed_to_location(s) for s in tqdm(range(start, start + size)))

    def lowest_location(self):
        """Get lowest location."""
        return min(
            self.seed_range_to_min_location(start, size)
            for start, size in tqdm(self.seed_ranges)
        )

    def lowest_location_bad(self) -> int:
        return min(
            self.lowest_loc_in_range(start, size)
            for start, size in tqdm(self.seed_ranges)
        )


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
    seeds_ranges = list(zip(seeds[::2], seeds[1::2]))
    almanac = Almanac(seeds_ranges)
    for map_start, map_end in map_ranges(almanac_lines):
        almanac.add_map(Map.from_lines(almanac_lines[map_start:map_end]))
    return almanac.lowest_location()


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
