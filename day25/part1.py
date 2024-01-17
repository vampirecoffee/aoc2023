"""Part 1 of solution for day 25."""
from __future__ import annotations

import argparse
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from tqdm import tqdm

INFINITY = 9999999999999999999999999999999999999999999999999999999


@dataclass(frozen=True)
class Wire:
    """Wire connecting two components."""

    left: str
    right: str

    def __post_init__(self) -> None:
        """Post-init checks."""
        assert self.left != self.right

    def __eq__(self, other: Any) -> bool:
        """Equality check."""
        if not isinstance(other, Wire):
            return False
        self_tuple = (self.left, self.right)
        other_tuple = (other.left, other.right)
        other_rev_tuple = (other.right, other.left)
        return self_tuple in (other_tuple, other_rev_tuple)


@dataclass(frozen=True)
class Edge:
    """Edge connecting 2 components with some 'weight' (aka cost)."""

    left: str
    right: str
    weight: int = 1

    def __post_init__(self) -> None:
        """Post-init checks."""
        assert self.left != self.right
        assert self.weight > 0

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        return (
            Wire(self.left, self.right) == Wire(other.left, other.right)
        ) and self.weight == other.weight

    def as_set(self) -> set[str]:
        """Return this edge as a set of its two vertexes."""
        return set([self.left, self.right])

    def to(self, node: str) -> Optional[str]:
        """Go from node to somewhere else, along this edge."""
        if node == self.left:
            return self.right
        if node == self.right:
            return self.left
        return None

    def crosses_out_of(self, graph: set[str]) -> Optional[str]:
        """If this edge crosses out of the graph, return the outside node.

        Otherwise, return None.
        """
        diff = set([self.left, self.right]) - graph
        if len(diff) == 1:
            return diff.pop()
        return None


@dataclass(frozen=True)
class Cut:
    """One 'cut' across the graph for the Stoer-Wagner algorithm."""

    s: str
    t: str
    weight: int
    cut_edges: set[Edge]


@dataclass
class Graph:
    """Graph with vertices connected by edges."""

    vertices: set[str] = field(default_factory=set)
    edges: set[Edge] = field(default_factory=set)

    def add_wire(self, w: Wire) -> None:
        """Add a wire to this graph."""
        self.add_edge(Edge(w.left, w.right, 1))

    def add_edge(self, e: Edge) -> None:
        """Add an edge to this graph."""
        self.vertices.add(e.left)
        self.vertices.add(e.right)
        to_remove: set[Edge] = set()
        for extant_edge in self.edges:
            if extant_edge.as_set() == e.as_set():
                if extant_edge.weight <= e.weight:
                    return
                to_remove.add(extant_edge)
        self.edges.add(e)
        for extant_edge in to_remove:
            self.edges.remove(extant_edge)

    def most_tightly_connected_vertex(self, vertices: set[str]) -> tuple[str, int]:
        """Find the most-tightly-connected vertex."""
        weights_by_vertex: defaultdict[str, int] = defaultdict(int)
        for edge in self.edges:
            vout = edge.crosses_out_of(vertices)
            if vout is not None:
                weights_by_vertex[vout] += edge.weight
        max_weight = -1
        best_vertex = ""
        for vertex, weight in weights_by_vertex.items():
            if weight > max_weight:
                max_weight = weight
                best_vertex = vertex
        return best_vertex, max_weight

    def reachable_from(self, s: set[str]) -> set[str]:
        """Return all nodes reachable from s."""
        curr = set(s)
        reached = set(curr)
        while len(curr) != 0 and len(reached) != len(self.vertices):
            next_nodes: set[str] = set()
            for edge in self.edges:
                if edge.left in curr and edge.right not in reached:
                    next_nodes.add(edge.right)
                if edge.right in curr and edge.left not in reached:
                    next_nodes.add(edge.left)
            reached |= next_nodes
            curr = next_nodes
        return reached

    def _try1_find_subgraphs(
        self, s: set[str], t: set[str]
    ) -> tuple[set[str], set[str]]:
        """Find subgraphs where you cut all the edges between s and t."""
        to_remove: set[Edge] = set()
        for edge in self.edges:
            if edge.left in s and edge.right in t:
                to_remove.add(edge)
            if edge.right in s and edge.left in t:
                to_remove.add(edge)
        print("removing edges...")
        for edge in to_remove:
            print(edge)
            self.edges.remove(edge)
        s_graph = self.reachable_from(s)
        t_graph = self.reachable_from(t)
        for edge in to_remove:
            self.edges.add(edge)
        return s_graph, t_graph

    def find_subgraphs(
        self, cuts: Iterable[tuple[set[str], set[str]]]
    ) -> tuple[set[str], set[str]]:
        """Find subgraphs after making the specified cuts.

        Which means that you remove all the edges connecting between the two
        parts of the tuple.
        """
        to_remove: set[Edge] = set()
        for edge in self.edges:
            for s, t in cuts:
                if edge.left in s and edge.right in t:
                    to_remove.add(edge)
                if edge.right in s and edge.left in t:
                    to_remove.add(edge)

        print("removing edges...")
        for edge in to_remove:
            print(edge)
            self.edges.remove(edge)
        start = self.vertices.pop()
        self.vertices.add(start)
        s_graph = self.reachable_from(set([start]))
        for vertex in self.vertices:
            if vertex in s_graph:
                continue
            t_graph = self.reachable_from(set([vertex]))
        return s_graph, t_graph

    def merge(self, v1: str, v2: str) -> None:
        """Merge two vertexes."""
        self.vertices.remove(v1)
        self.vertices.remove(v2)
        joined_name = f"{v1}+{v2}"
        self.vertices.add(joined_name)
        weights_in: defaultdict[str, int] = defaultdict(int)
        to_remove: set[Edge] = set()
        for edge in self.edges:
            if v1 in edge.as_set() or v2 in edge.as_set():
                to_remove.add(edge)
            if v1 in edge.as_set() and v2 in edge.as_set():
                continue
            to_v1 = edge.to(v1)
            to_v2 = edge.to(v2)
            for vtx in (to_v1, to_v2):
                if vtx is not None:
                    weights_in[vtx] += edge.weight
                    to_remove.add(edge)
        for edge in to_remove:
            self.edges.remove(edge)
        for vtx, weight in weights_in.items():
            new_edge = Edge(vtx, joined_name, weight)
            self.add_edge(new_edge)

    def stoer_wagner_alg(self) -> Cut:
        """Stoer-Wagner algorithm."""
        orig_vertices = set(self.vertices)
        orig_edges = set(self.edges)

        best_cut = Cut("", "", INFINITY, set())
        with tqdm(total=len(self.vertices)) as pbar:
            while len(self.vertices) > 1:
                cut = self.stoer_wagner_once()
                if cut.weight < best_cut.weight:
                    print(
                        "cut of weight", cut.weight, "is better than", best_cut.weight
                    )
                    best_cut = cut
                elif cut.weight == best_cut.weight:
                    if len(best_cut.cut_edges) != 3:
                        best_cut = cut
                if cut.weight == 3 and len(best_cut.cut_edges) == 3:
                    break
                self.merge(cut.s, cut.t)
                pbar.update(1)
        self.vertices = orig_vertices
        self.edges = orig_edges
        return best_cut

    def stoer_wagner_once(self) -> Cut:
        """Run one iteration of the Stoer-Wagner algorithm."""
        start = self.vertices.pop()
        self.vertices.add(start)
        subgraph = set([start])
        s = start
        t = start
        weight: int
        while subgraph < self.vertices:
            s = t
            t, weight = self.most_tightly_connected_vertex(subgraph)
            subgraph.add(t)
        cut_edges = {edge for edge in self.edges if t in edge.as_set()}
        return Cut(s, t, weight, cut_edges)


def wires_from_line(line: str) -> list[Wire]:
    """Create wires from a line in the input."""
    line = line.strip()
    left, all_right = line.split(":")
    right_as_arr = [e.strip() for e in all_right.split()]
    wires = [Wire(left, r) for r in right_as_arr]
    return wires


def get_components(wires: Iterable[Wire]) -> set[str]:
    """Get all the components in this collection of wires."""
    out: set[str] = set()
    for w in wires:
        out.add(w.left)
        out.add(w.right)
    return out


def first_that_isnt(wires: list[Wire], not_these: Iterable[Wire]) -> Wire:
    """Get the first wire that isn't that one."""
    for w in wires:
        if w not in not_these:
            return w
    raise ValueError("they're all that one")


def walk(wires: Iterable[Wire]) -> set[str]:
    """Walk through the graph and return the wires reachable from start."""
    start: Wire
    for w in wires:
        start = w
        break
    all_nodes = get_components(wires)
    curr = set([start.left, start.right])
    reached = set(curr)
    while len(curr) != 0:
        next_nodes: set[str] = set()
        for w in wires:
            if w.left in curr and w.right not in reached:
                next_nodes.add(w.right)
            if w.right in curr and w.left not in reached:
                next_nodes.add(w.left)
        reached |= next_nodes
        curr = next_nodes
        if all_nodes == reached:
            return all_nodes
    print("done!")
    return reached


def cut3(wires: list[Wire]) -> tuple[set[str], set[str]]:
    """Cut 3 wires and return subgraphs."""
    nodes = get_components(wires)
    combo_num = math.factorial(len(wires))
    combo_denom = math.factorial(3) * math.factorial(len(wires) - 3)
    num_combos = int(combo_num / combo_denom)
    with tqdm(total=num_combos) as pbar:
        for try3 in tqdm(itertools.combinations(wires, 3)):
            wires_as_set = set(wires)
            for w in try3:
                wires_as_set.remove(w)
            side1 = walk(wires_as_set)
            pbar.update(1)
            if len(side1) != len(nodes):
                side2 = nodes - side1
                return side1, side2
    raise ValueError("can't partition :(")


def parse_file(filename: str) -> int:
    """Parse file and solve problem."""
    graph = Graph()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            wires = wires_from_line(line)
            for w in wires:
                graph.add_wire(w)
    the_cut = graph.stoer_wagner_alg()
    print(the_cut)
    cuts: list[tuple[set[str], set[str]]] = []
    for edge in the_cut.cut_edges:
        s_nodes = set(e.strip() for e in edge.left.split("+"))
        t_nodes = set(e.strip() for e in edge.right.split("+"))
        print(s_nodes, "SNIP SNIP", t_nodes)
        cuts.append((s_nodes, t_nodes))
    g1, g2 = graph.find_subgraphs(cuts)
    print(g1, len(g1))
    print(g2, len(g2))
    return the_cut.weight


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    print(args.filename)
    print(parse_file(args.filename))


if __name__ == "__main__":
    main()
