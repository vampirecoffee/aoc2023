"""Part 1 of Day 8."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field

_node_re = re.compile(r"(...) = \((...), (...)\)")


@dataclass
class Node:
    """One node in our network."""

    name: str
    left: str
    right: str

    @classmethod
    def from_str(cls, s: str) -> Node:
        """Convert a line into a Node."""
        m = _node_re.search(s)
        if m is None:
            raise RuntimeError(f"Does not look node-shaped to me: {s}")
        return cls(
            name=m.group(1),
            left=m.group(2),
            right=m.group(3),
        )


@dataclass
class Network:
    """A network, with many nodes."""

    directions: str
    nodes: dict[str, Node] = field(default_factory=dict)

    def add_node(self, n: Node) -> None:
        """Add a node."""
        if n.name in self.nodes:
            raise ValueError(f"network already has a node named {n.name}")
        self.nodes[n.name] = n

    def walk_to_zzz(self) -> int:
        """How many steps does it take to go from AAA to ZZZ?"""
        cur = self.nodes["AAA"]
        dir_idx = 0
        steps_taken = 0
        while cur.name != "ZZZ":
            if self.directions[dir_idx] == "L":
                cur = self.nodes[cur.left]
            else:
                cur = self.nodes[cur.right]
            steps_taken += 1
            dir_idx += 1
            if dir_idx == len(self.directions):
                dir_idx = 0
        return steps_taken


def file_to_network(filename: str) -> Network:
    """Turn the input file into the network."""
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()

    directions = lines[0].strip()
    network = Network(directions)
    for l in lines[1:]:
        sl = l.strip()
        if sl:
            network.add_node(Node.from_str(sl))
    return network


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    network = file_to_network(args.filename)
    print(network.walk_to_zzz())


if __name__ == "__main__":
    main()
