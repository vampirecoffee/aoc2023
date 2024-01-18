"""Part 1 of the hash problem."""

from __future__ import annotations

import argparse
import functools
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Lens:
    """Lens. It has a label and a focal strength."""

    label: str
    focal_length: int

    @functools.cached_property
    def box(self) -> int:
        """Box number for this lens."""
        return hash_str(self.label)


@dataclass
class Box:
    """A box. It has lenses in it."""

    lenses: list[Lens] = field(default_factory=list)

    def remove_lens(self, label: str) -> None:
        """Remove lens with given label from lenses."""
        self.lenses = [l for l in self.lenses if l.label != label]

    def add_or_replace_lens(self, label: str, focal_length: int) -> None:
        """Add or replace a lens (the = operation)."""
        lens = Lens(label=label, focal_length=focal_length)
        for i in range(0, len(self.lenses)):  # pylint: disable=consider-using-enumerate
            if self.lenses[i].label == label:
                self.lenses[i] = lens
                return
        self.lenses.append(lens)

    def focusing_power(self) -> int:
        """Get the sum of the focusing power of the lenses in this box."""
        out = 0
        for i, lens in enumerate(self.lenses):
            this_lens_power = (i + 1) * (lens.box + 1) * lens.focal_length
            out += this_lens_power
        return out


@functools.cache
def hash_char(c: str, start_at: int = 0) -> int:
    """Hash the next/first character in a string."""
    h = start_at + ord(c)
    h *= 17
    h = h % 256
    return h


def hash_str(s: str) -> int:
    """Hash a string."""
    h = 0
    for char in s:
        h = hash_char(char, h)
    return h


def run_ops(ops: list[str]) -> defaultdict[int, Box]:
    """Run all operations and return the relevant boxes."""
    boxes: defaultdict[int, Box] = defaultdict(Box)
    for op in ops:
        if "=" in op:
            label, fl_str = op.split("=")
            fl = int(fl_str)
            box_no = hash_str(label)
            boxes[box_no].add_or_replace_lens(label, fl)
        else:  # the "-" case
            label = op.split("-")[0]
            box_no = hash_str(label)
            boxes[box_no].remove_lens(label)
    return boxes


def parse_file(filename: str) -> int:
    """Parse a file."""
    with open(filename) as f:
        for line in f:
            line = line.strip()
            ops = line.split(",")
            boxes = run_ops(ops)
            return sum(b.focusing_power() for b in boxes.values())
    raise RuntimeError("how did you even get here")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
