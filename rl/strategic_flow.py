"""Capacity, cut, and multi-commodity flow models for tactical supply."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Iterable, Mapping, Sequence


Node = Hashable
Edge = tuple[Node, Node]
Cell = tuple[int, int]


@dataclass(frozen=True)
class MaxFlowResult:
    value: float
    flows: Mapping[Edge, float]
    source_side: frozenset[Node]
    sink_side: frozenset[Node]
    cut_edges: tuple[Edge, ...]


class CapacityNetwork:
    """A deterministic directed capacity graph using Edmonds-Karp."""

    def __init__(
        self,
        capacities: Mapping[Edge, float],
        costs: Mapping[Edge, float] | None = None,
    ) -> None:
        cleaned: dict[Edge, float] = {}
        for (left, right), capacity in capacities.items():
            value = float(capacity)
            if left == right or not isfinite(value) or value < 0.0:
                raise ValueError("network capacities must be finite and non-negative")
            if value > 0.0:
                cleaned[(left, right)] = value
        self.capacities = cleaned
        self.costs = {
            edge: float((costs or {}).get(edge, 0.0)) for edge in self.capacities
        }
        if any(not isfinite(value) for value in self.costs.values()):
            raise ValueError("network costs must be finite")
        self.nodes = frozenset(
            node for edge in self.capacities for node in edge
        )

    @classmethod
    def from_grid(
        cls,
        cells: Iterable[Cell],
        *,
        capacities: Mapping[Cell, float] | None = None,
        costs: Mapping[Cell, float] | None = None,
    ) -> "CapacityNetwork":
        region = set(cells)
        edges: dict[Edge, float] = {}
        edge_costs: dict[Edge, float] = {}
        for x, y in region:
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor not in region:
                    continue
                edges[((x, y), neighbor)] = max(
                    0.0, float((capacities or {}).get(neighbor, 1.0))
                )
                edge_costs[((x, y), neighbor)] = float(
                    (costs or {}).get(neighbor, 1.0)
                )
        return cls(edges, edge_costs)

    def max_flow(self, source: Node, sink: Node) -> MaxFlowResult:
        if source == sink:
            return MaxFlowResult(0.0, {}, frozenset({source}), frozenset(), ())
        nodes = set(self.nodes) | {source, sink}
        residual: dict[Edge, float] = {}
        adjacency: dict[Node, set[Node]] = {node: set() for node in nodes}
        for (left, right), capacity in self.capacities.items():
            residual[(left, right)] = residual.get((left, right), 0.0) + capacity
            residual.setdefault((right, left), 0.0)
            adjacency[left].add(right)
            adjacency[right].add(left)
        total = 0.0
        while True:
            parent: dict[Node, Node] = {}
            frontier = deque([source])
            seen = {source}
            while frontier and sink not in seen:
                left = frontier.popleft()
                for right in sorted(adjacency[left], key=repr):
                    if right in seen or residual.get((left, right), 0.0) <= 1e-12:
                        continue
                    seen.add(right)
                    parent[right] = left
                    frontier.append(right)
            if sink not in seen:
                break
            amount = float("inf")
            node = sink
            while node != source:
                previous = parent[node]
                amount = min(amount, residual[(previous, node)])
                node = previous
            node = sink
            while node != source:
                previous = parent[node]
                residual[(previous, node)] -= amount
                residual[(node, previous)] = residual.get((node, previous), 0.0) + amount
                node = previous
            total += amount
        reachable = {source}
        frontier = deque([source])
        while frontier:
            left = frontier.popleft()
            for right in adjacency[left]:
                if right not in reachable and residual.get((left, right), 0.0) > 1e-12:
                    reachable.add(right)
                    frontier.append(right)
        flows = {
            edge: max(0.0, capacity - residual.get(edge, 0.0))
            for edge, capacity in self.capacities.items()
            if capacity - residual.get(edge, 0.0) > 1e-12
        }
        cut = tuple(
            sorted(
                (
                    edge for edge in self.capacities
                    if edge[0] in reachable and edge[1] not in reachable
                ),
                key=repr,
            )
        )
        return MaxFlowResult(
            total,
            flows,
            frozenset(reachable),
            frozenset(nodes - reachable),
            cut,
        )

    def multi_source_flow(
        self,
        sources: Mapping[Node, float],
        sinks: Mapping[Node, float],
    ) -> MaxFlowResult:
        super_source = ("__super_source__", id(self))
        super_sink = ("__super_sink__", id(self))
        capacities = dict(self.capacities)
        for node, capacity in sources.items():
            capacities[(super_source, node)] = float(capacity)
        for node, capacity in sinks.items():
            capacities[(node, super_sink)] = float(capacity)
        raw = CapacityNetwork(capacities).max_flow(super_source, super_sink)
        flows = {
            edge: value
            for edge, value in raw.flows.items()
            if super_source not in edge and super_sink not in edge
        }
        cut = tuple(
            edge for edge in raw.cut_edges
            if super_source not in edge and super_sink not in edge
        )
        return MaxFlowResult(
            raw.value,
            flows,
            frozenset(node for node in raw.source_side if node != super_source),
            frozenset(node for node in raw.sink_side if node != super_sink),
            cut,
        )


@dataclass(frozen=True)
class Commodity:
    source: Node
    sink: Node
    demand: float


@dataclass(frozen=True)
class MultiCommodityFlowResult:
    flows: Mapping[tuple[int, Node, Node], float]
    delivered: tuple[float, ...]
    unmet: tuple[float, ...]
    objective: float


def solve_multi_commodity_flow(
    network: CapacityNetwork,
    commodities: Sequence[Commodity],
    *,
    unmet_penalty: float = 1000.0,
) -> MultiCommodityFlowResult:
    """Solve a fractional shared-capacity multi-commodity flow LP."""

    import numpy as np
    from scipy.optimize import linprog

    if unmet_penalty <= 0.0 or not isfinite(unmet_penalty):
        raise ValueError("unmet_penalty must be positive and finite")
    if not commodities:
        return MultiCommodityFlowResult({}, (), (), 0.0)
    if any(item.demand < 0.0 or not isfinite(item.demand) for item in commodities):
        raise ValueError("commodity demand must be finite and non-negative")
    edges = tuple(sorted(network.capacities, key=repr))
    nodes = tuple(sorted(network.nodes, key=repr))
    edge_count = len(edges)
    commodity_count = len(commodities)
    variable_count = commodity_count * edge_count + commodity_count
    objective = np.zeros(variable_count, dtype=np.float64)
    for commodity_index in range(commodity_count):
        offset = commodity_index * edge_count
        for edge_index, edge in enumerate(edges):
            objective[offset + edge_index] = network.costs.get(edge, 0.0)
        objective[commodity_count * edge_count + commodity_index] = unmet_penalty
    equality_rows = []
    equality_rhs = []
    for commodity_index, commodity in enumerate(commodities):
        offset = commodity_index * edge_count
        unmet_index = commodity_count * edge_count + commodity_index
        for node in nodes:
            row = np.zeros(variable_count, dtype=np.float64)
            for edge_index, (left, right) in enumerate(edges):
                if left == node:
                    row[offset + edge_index] += 1.0
                if right == node:
                    row[offset + edge_index] -= 1.0
            if node == commodity.source:
                row[unmet_index] += 1.0
                rhs = float(commodity.demand)
            elif node == commodity.sink:
                row[unmet_index] -= 1.0
                rhs = -float(commodity.demand)
            else:
                rhs = 0.0
            equality_rows.append(row)
            equality_rhs.append(rhs)
    capacity_rows = np.zeros((edge_count, variable_count), dtype=np.float64)
    for edge_index in range(edge_count):
        for commodity_index in range(commodity_count):
            capacity_rows[edge_index, commodity_index * edge_count + edge_index] = 1.0
    result = linprog(
        objective,
        A_ub=capacity_rows,
        b_ub=np.asarray([network.capacities[edge] for edge in edges]),
        A_eq=np.asarray(equality_rows),
        b_eq=np.asarray(equality_rhs),
        bounds=[(0.0, None)] * variable_count,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"multi-commodity flow failed: {result.message}")
    flows: dict[tuple[int, Node, Node], float] = {}
    for commodity_index in range(commodity_count):
        offset = commodity_index * edge_count
        for edge_index, (left, right) in enumerate(edges):
            value = float(result.x[offset + edge_index])
            if value > 1e-9:
                flows[(commodity_index, left, right)] = value
    unmet = tuple(
        float(result.x[commodity_count * edge_count + index])
        for index in range(commodity_count)
    )
    delivered = tuple(
        float(commodity.demand) - missing
        for commodity, missing in zip(commodities, unmet)
    )
    return MultiCommodityFlowResult(
        flows, delivered, unmet, float(result.fun)
    )

