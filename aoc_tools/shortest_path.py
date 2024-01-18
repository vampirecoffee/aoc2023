"""Various algorithms to find the shortest path through a graph.

I haven't actually tested these yet. So they may not work right."""

import itertools
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class Path:
    """Represents a path from some start node (not shown) to this node."""

    from_node_id: Hashable
    to_node_id: Hashable
    cost: int = 1


class Node(ABC):
    """A node in a graph."""

    @property
    @abstractmethod
    def identifier(self) -> Hashable:
        """Identifier for this node.

        Used to determine if a path leads here.
        Should be hashable and unique per node.
        """

    @property
    @abstractmethod
    def paths(self) -> Iterable[Path]:
        """Paths from this node to another node."""

    def __eq__(self, other: Any) -> bool:
        """Two nodes are equal if they have the same identifier."""
        if not isinstance(other, Node):
            return False
        return self.identifier == other.identifier


class Graph(ABC):
    """Abstract graph class."""

    @abstractmethod
    def find_node(self, node_id: Hashable) -> Optional[Node]:
        """Find the given node in this graph."""

    @abstractmethod
    def node_ids(self) -> Iterable[Hashable]:
        """Get the IDs of all nodes in this graph."""

    @abstractmethod
    def paths(self) -> Iterable[Path]:
        """Get all the paths (edges) in this graph."""

    @abstractmethod
    def neighbors(self, node_id: Hashable) -> Iterable[Path]:
        """Find all neighbors of the given node in this graph."""

    @property
    @abstractmethod
    def start_id(self) -> Optional[Hashable]:
        """ID to start at."""

    @property
    @abstractmethod
    def end_id(self) -> Optional[Hashable]:
        """ID to end at."""

    def dijkstra(self) -> int:
        """Run Dijkstra's algorithm and return the cost of the shortest path."""
        assert self.start_id is not None, "must set start_id to find shortest path"
        assert self.end_id is not None, "must set end_id to find shortest path"

        min_costs: defaultdict[Hashable, int] = defaultdict(lambda: INFINITY)
        min_costs[self.start_id] = 0

        def find_next_node(
            cost_by_id: defaultdict[Hashable, int]
        ) -> tuple[Optional[Hashable], int]:
            """Find the lowest-cost unvisited node. Return its ID and its cost."""
            best_id: Optional[Hashable] = None
            best_cost = INFINITY
            for node_id, cost in cost_by_id.items():
                if cost < best_cost:
                    best_id = node_id
                    best_cost = cost
            return best_id, best_cost

        cur_id, cur_cost = find_next_node(min_costs)
        while cur_id != self.end_id and cur_id is not None:
            if cur_cost < 0:
                raise RuntimeError(
                    "Dijkstra's algorithm does not work if some costs are negative"
                )
            cur_node = self.find_node(cur_id)
            assert cur_node is not None, f"missing node {cur_id}"
            for path in cur_node.paths:
                if path.cost < 0:
                    raise RuntimeError(
                        "Dijkstra's algorithm does not work if some costs are negative"
                    )
                min_costs[path.to_node_id] = min(
                    min_costs[path.to_node_id], cur_cost + path.cost
                )
            cur_id, cur_cost = find_next_node(min_costs)
        if cur_id is None:
            return INFINITY

        return cur_cost

    def floyd_warshall(self) -> dict[tuple[Hashable, Hashable], int]:
        """Run Floyd-Warshall algorithm and return all-pairs shortest paths."""
        best_costs: defaultdict[tuple[Hashable, Hashable], int] = defaultdict(
            lambda: INFINITY
        )

        def path_to_key(p: Path) -> tuple[Hashable, Hashable]:
            """Get dict key from a path."""
            return (p.from_node_id, p.to_node_id)

        for path in self.paths():
            key = path_to_key(path)
            best_costs[key] = path.cost

        node_ids = self.node_ids()
        for node_id in node_ids:
            best_costs[(node_id, node_id)] = 0

        for id_k in node_ids:
            for id_i in node_ids:
                for id_j in node_ids:
                    ij_key = (id_i, id_j)
                    ik_key = (id_i, id_k)
                    kj_key = (id_k, id_j)
                    best_costs[ij_key] = min(
                        best_costs[ij_key], best_costs[ik_key] + best_costs[kj_key]
                    )

        for node_id in node_ids:
            if best_costs[(node_id, node_id)] < 0:
                raise RuntimeError(
                    "This graph has a negative cycle so there's no best path"
                )

        return dict(best_costs)


INFINITY = 99999999999999999999999999999999999999999999999999999999


@dataclass
class BasicGraph(Graph):
    """A graph. It has a bunch of nodes."""

    nodes: list[Node] = field(default_factory=list)
    start_id: Optional[Hashable] = None
    end_id: Optional[Hashable] = None

    def find_node(self, node_id: Hashable) -> Optional[Node]:
        """Find a node, by id."""
        for node in self.nodes:
            if node.identifier == node_id:
                return node
        return None

    def node_ids(self) -> Iterable[Hashable]:
        """Return IDs of every node in the graph."""
        return list(n.identifier for n in self.nodes)

    def paths(self) -> Iterable[Path]:
        """Return every path in the graph."""
        unflat_paths = list(n.paths for n in self.nodes)
        flat_paths = itertools.chain.from_iterable(unflat_paths)
        return flat_paths

    def add_node(self, node: Node) -> None:
        """Add a node."""
        if self.find_node(node.identifier) is not None:
            raise RuntimeError(f"Node {node.identifier} is already in this graph")
        self.nodes.append(node)

    def neighbors(self, node_id: Hashable) -> Iterable[Path]:
        """Return all neighbors of this node."""
        node = self.find_node(node_id)
        assert node is not None, f"can't find neighbors of nonexistent node {node_id}"
        return node.paths


BasicGraph()
