"""P12 graph signals, dynamic networks, and constrained matching.

The routines in this module are deliberately finite and auditable.  They do
not infer missing observations: callers must provide graph weights, block
memberships, preferences, utilities, and operational constraints explicitly.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


Key = Hashable


class GraphSignalProcessor:
    """Spectral signal processing on a finite undirected weighted graph."""

    def __init__(
        self, adjacency: Sequence[Sequence[float]], *, normalized: bool = False
    ) -> None:
        weights = np.asarray(adjacency, dtype=np.float64)
        if (
            weights.ndim != 2
            or weights.shape[0] == 0
            or weights.shape[0] != weights.shape[1]
            or np.any(~np.isfinite(weights))
            or np.any(weights < 0.0)
            or not np.allclose(weights, weights.T, atol=1e-10)
            or not np.allclose(np.diag(weights), 0.0, atol=1e-10)
        ):
            raise ValueError(
                "adjacency must be finite, symmetric, non-negative, and loop-free"
            )
        self.adjacency = weights.copy()
        self.degree = weights.sum(axis=1)
        laplacian = np.diag(self.degree) - weights
        if normalized:
            inverse = np.zeros_like(self.degree)
            positive = self.degree > 0.0
            inverse[positive] = 1.0 / np.sqrt(self.degree[positive])
            laplacian = inverse[:, None] * laplacian * inverse[None, :]
        self.normalized = bool(normalized)
        self.laplacian = laplacian
        self.eigenvalues, self.eigenvectors = np.linalg.eigh(laplacian)

    def _signal(self, signal: Sequence[float]) -> np.ndarray:
        value = np.asarray(signal, dtype=np.float64)
        if value.shape != (self.adjacency.shape[0],) or np.any(~np.isfinite(value)):
            raise ValueError("graph signal must have one finite value per vertex")
        return value

    def fourier_transform(self, signal: Sequence[float]) -> np.ndarray:
        return self.eigenvectors.T @ self._signal(signal)

    def inverse_fourier_transform(self, coefficients: Sequence[float]) -> np.ndarray:
        value = np.asarray(coefficients, dtype=np.float64)
        if value.shape != self.eigenvalues.shape or np.any(~np.isfinite(value)):
            raise ValueError("graph Fourier coefficients have invalid shape or values")
        return self.eigenvectors @ value

    def spectral_filter(
        self, signal: Sequence[float], response: Sequence[float]
    ) -> np.ndarray:
        transfer = np.asarray(response, dtype=np.float64)
        if transfer.shape != self.eigenvalues.shape or np.any(~np.isfinite(transfer)):
            raise ValueError("spectral response must match the graph spectrum")
        return self.inverse_fourier_transform(transfer * self.fourier_transform(signal))

    def heat_filter(self, signal: Sequence[float], *, time: float) -> np.ndarray:
        if not isfinite(time) or time < 0.0:
            raise ValueError("heat-filter time must be finite and non-negative")
        return self.spectral_filter(signal, np.exp(-time * self.eigenvalues))

    def wavelet_coefficients(
        self, signal: Sequence[float], *, scale: float
    ) -> np.ndarray:
        """Mexican-hat-like graph wavelet g(s lambda)=s lambda exp(-s lambda)."""
        if not isfinite(scale) or scale <= 0.0:
            raise ValueError("graph-wavelet scale must be positive and finite")
        argument = scale * self.eigenvalues
        return self.spectral_filter(signal, argument * np.exp(-argument))

    def total_variation(self, signal: Sequence[float]) -> float:
        value = self._signal(signal)
        return float(value @ self.laplacian @ value)


@dataclass(frozen=True)
class DynamicSBMSample:
    memberships: np.ndarray
    adjacencies: np.ndarray


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if (
        result.ndim != 1
        or result.size == 0
        or np.any(~np.isfinite(result))
        or np.any(result < 0.0)
        or not np.isclose(result.sum(), 1.0, atol=1e-9)
    ):
        raise ValueError(f"{name} must be a finite probability vector")
    return result


def simulate_dynamic_sbm(
    node_count: int,
    steps: int,
    block_probabilities: Sequence[Sequence[float]],
    transition: Sequence[Sequence[float]],
    initial_probabilities: Sequence[float],
    *,
    seed: int | None = None,
) -> DynamicSBMSample:
    """Simulate Markov memberships and conditionally independent graph snapshots."""
    block = np.asarray(block_probabilities, dtype=np.float64)
    initial = _probability_vector(initial_probabilities, "initial block probabilities")
    transition_value = np.asarray(transition, dtype=np.float64)
    groups = initial.size
    if (
        node_count <= 0
        or steps <= 0
        or block.shape != (groups, groups)
        or transition_value.shape != (groups, groups)
        or np.any(~np.isfinite(block))
        or np.any((block < 0.0) | (block > 1.0))
        or not np.allclose(block, block.T, atol=1e-10)
    ):
        raise ValueError("dynamic SBM dimensions or block probabilities are invalid")
    for row in transition_value:
        _probability_vector(row, "membership transition row")
    random = np.random.default_rng(seed)
    memberships = np.empty((steps, node_count), dtype=np.int64)
    memberships[0] = random.choice(groups, size=node_count, p=initial)
    for time in range(1, steps):
        memberships[time] = [
            random.choice(groups, p=transition_value[previous])
            for previous in memberships[time - 1]
        ]
    adjacencies = np.zeros((steps, node_count, node_count), dtype=np.int8)
    for time in range(steps):
        for left in range(node_count):
            for right in range(left + 1, node_count):
                probability = block[memberships[time, left], memberships[time, right]]
                edge = int(random.random() < probability)
                adjacencies[time, left, right] = edge
                adjacencies[time, right, left] = edge
    return DynamicSBMSample(memberships, adjacencies)


def estimate_dynamic_sbm(
    memberships: Sequence[Sequence[int]],
    adjacencies: Sequence[Sequence[Sequence[float]]],
    *,
    group_count: int | None = None,
    smoothing: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate block and membership-transition probabilities from known labels."""
    labels = np.asarray(memberships, dtype=np.int64)
    graphs = np.asarray(adjacencies, dtype=np.float64)
    if (
        labels.ndim != 2
        or labels.size == 0
        or graphs.shape != (labels.shape[0], labels.shape[1], labels.shape[1])
        or np.any(labels < 0)
        or np.any(~np.isfinite(graphs))
        or np.any((graphs < 0.0) | (graphs > 1.0))
        or not np.allclose(graphs, graphs.transpose(0, 2, 1), atol=1e-10)
        or not isfinite(smoothing)
        or smoothing < 0.0
    ):
        raise ValueError("dynamic SBM observations are invalid")
    groups = int(group_count if group_count is not None else labels.max() + 1)
    if groups <= int(labels.max()):
        raise ValueError("group_count does not cover observed memberships")
    edge_counts = np.zeros((groups, groups))
    pair_counts = np.zeros((groups, groups))
    for time, graph in enumerate(graphs):
        for left in range(labels.shape[1]):
            for right in range(left + 1, labels.shape[1]):
                a, b = labels[time, left], labels[time, right]
                edge_counts[a, b] += graph[left, right]
                pair_counts[a, b] += 1.0
                if a != b:
                    edge_counts[b, a] += graph[left, right]
                    pair_counts[b, a] += 1.0
    denominator = pair_counts + 2.0 * smoothing
    block = np.divide(
        edge_counts + smoothing,
        denominator,
        out=np.full_like(edge_counts, 0.5),
        where=denominator > 0.0,
    )
    transition_counts = np.full((groups, groups), smoothing)
    for previous, current in zip(labels[:-1], labels[1:]):
        for left, right in zip(previous, current):
            transition_counts[left, right] += 1.0
    row_sums = transition_counts.sum(axis=1, keepdims=True)
    transition = np.divide(
        transition_counts,
        row_sums,
        out=np.full_like(transition_counts, 1.0 / groups),
        where=row_sums > 0.0,
    )
    return block, transition


def dynamic_sbm_log_likelihood(
    sample: DynamicSBMSample,
    block_probabilities: Sequence[Sequence[float]],
    transition: Sequence[Sequence[float]],
    initial_probabilities: Sequence[float],
    *,
    epsilon: float = 1e-12,
) -> float:
    labels = np.asarray(sample.memberships, dtype=np.int64)
    graphs = np.asarray(sample.adjacencies, dtype=np.float64)
    initial = _probability_vector(initial_probabilities, "initial block probabilities")
    block = np.asarray(block_probabilities, dtype=np.float64)
    transition_value = np.asarray(transition, dtype=np.float64)
    groups = initial.size
    if (
        labels.ndim != 2
        or graphs.shape != (labels.shape[0], labels.shape[1], labels.shape[1])
        or block.shape != (groups, groups)
        or transition_value.shape != (groups, groups)
        or np.any(~np.isfinite(block))
        or np.any((block < 0.0) | (block > 1.0))
        or not np.allclose(block, block.T, atol=1e-10)
        or np.any(~np.isfinite(transition_value))
        or np.any(transition_value < 0.0)
        or not np.allclose(transition_value.sum(axis=1), 1.0, atol=1e-9)
        or np.any(labels < 0)
        or np.any(labels >= groups)
        or np.any(~np.isfinite(graphs))
        or np.any((graphs < 0.0) | (graphs > 1.0))
        or not np.allclose(graphs, graphs.transpose(0, 2, 1), atol=1e-10)
        or not np.allclose(np.diagonal(graphs, axis1=1, axis2=2), 0.0, atol=1e-10)
        or epsilon <= 0.0
    ):
        raise ValueError("dynamic SBM likelihood inputs are invalid")
    clipped_block = np.clip(block, epsilon, 1.0 - epsilon)
    clipped_transition = np.clip(transition_value, epsilon, 1.0)
    value = float(np.log(np.clip(initial[labels[0]], epsilon, 1.0)).sum())
    for previous, current in zip(labels[:-1], labels[1:]):
        value += float(np.log(clipped_transition[previous, current]).sum())
    for time, graph in enumerate(graphs):
        for left in range(labels.shape[1]):
            for right in range(left + 1, labels.shape[1]):
                probability = clipped_block[labels[time, left], labels[time, right]]
                value += float(graph[left, right] * np.log(probability))
                value += float((1.0 - graph[left, right]) * np.log(1.0 - probability))
    return value


def _all_pairs_shortest_paths(
    nodes: tuple[Key, ...], edges: frozenset[frozenset[Key]]
) -> dict[Key, dict[Key, int]]:
    adjacency = {node: set() for node in nodes}
    for edge in edges:
        left, right = tuple(edge)
        adjacency[left].add(right)
        adjacency[right].add(left)
    distances: dict[Key, dict[Key, int]] = {}
    for source in nodes:
        found = {source: 0}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in found:
                    found[neighbor] = found[current] + 1
                    queue.append(neighbor)
        distances[source] = found
    return distances


class ConnectionsNetwork:
    """Jackson-Wolinsky connections model with distance-decay benefits."""

    def __init__(self, nodes: Sequence[Key], *, decay: float, link_cost: float) -> None:
        self.nodes = tuple(dict.fromkeys(nodes))
        if (
            len(self.nodes) < 2
            or not isfinite(decay)
            or not 0.0 < decay < 1.0
            or not isfinite(link_cost)
            or link_cost < 0.0
        ):
            raise ValueError("connections-model nodes or parameters are invalid")
        self.decay = float(decay)
        self.link_cost = float(link_cost)

    def _edges(self, edges: Sequence[Sequence[Key]]) -> frozenset[frozenset[Key]]:
        node_set = set(self.nodes)
        result = set()
        for value in edges:
            if (
                len(value) != 2
                or value[0] == value[1]
                or value[0] not in node_set
                or value[1] not in node_set
            ):
                raise ValueError("network edge is invalid")
            result.add(frozenset(value))
        return frozenset(result)

    def utilities(self, edges: Sequence[Sequence[Key]]) -> dict[Key, float]:
        edge_set = self._edges(edges)
        distances = _all_pairs_shortest_paths(self.nodes, edge_set)
        degree = {node: 0 for node in self.nodes}
        for edge in edge_set:
            for node in edge:
                degree[node] += 1
        return {
            node: sum(
                self.decay**distance
                for target, distance in distances[node].items()
                if target != node
            )
            - self.link_cost * degree[node]
            for node in self.nodes
        }

    def pairwise_stability_violations(
        self, edges: Sequence[Sequence[Key]], *, tolerance: float = 1e-10
    ) -> tuple[tuple[str, Key, Key], ...]:
        edge_set = self._edges(edges)
        baseline = self.utilities([tuple(edge) for edge in edge_set])
        violations = []
        for left_index, left in enumerate(self.nodes):
            for right in self.nodes[left_index + 1 :]:
                edge = frozenset((left, right))
                candidate = set(edge_set)
                if edge in edge_set:
                    candidate.remove(edge)
                    changed = self.utilities([tuple(item) for item in candidate])
                    for node in (left, right):
                        if changed[node] > baseline[node] + tolerance:
                            violations.append(
                                ("delete", node, right if node == left else left)
                            )
                else:
                    candidate.add(edge)
                    changed = self.utilities([tuple(item) for item in candidate])
                    gains = (
                        changed[left] - baseline[left],
                        changed[right] - baseline[right],
                    )
                    if min(gains) >= -tolerance and max(gains) > tolerance:
                        violations.append(("add", left, right))
        return tuple(violations)


@dataclass(frozen=True)
class StableMatchingResult:
    assignments: Mapping[Key, Key]
    receiver_assignments: Mapping[Key, tuple[Key, ...]]


def deferred_acceptance(
    proposer_preferences: Mapping[Key, Sequence[Key]],
    receiver_preferences: Mapping[Key, Sequence[Key]],
    *,
    capacities: Mapping[Key, int] | None = None,
) -> StableMatchingResult:
    """Proposer-optimal Gale-Shapley matching with incomplete preference lists."""
    proposers = tuple(proposer_preferences)
    receivers = tuple(receiver_preferences)
    receiver_set = set(receivers)
    proposer_set = set(proposers)
    if not proposers or not receivers:
        return StableMatchingResult({}, {receiver: () for receiver in receivers})
    if any(
        len(set(values)) != len(values)
        or any(value not in receiver_set for value in values)
        for values in proposer_preferences.values()
    ):
        raise ValueError("proposer preferences contain duplicates or unknown receivers")
    if any(
        len(set(values)) != len(values)
        or any(value not in proposer_set for value in values)
        for values in receiver_preferences.values()
    ):
        raise ValueError("receiver preferences contain duplicates or unknown proposers")
    limits = {
        receiver: int((capacities or {}).get(receiver, 1)) for receiver in receivers
    }
    if any(value <= 0 for value in limits.values()):
        raise ValueError("matching capacities must be positive")
    ranks = {
        receiver: {
            proposer: rank
            for rank, proposer in enumerate(receiver_preferences[receiver])
        }
        for receiver in receivers
    }
    held: dict[Key, list[Key]] = {receiver: [] for receiver in receivers}
    next_choice = {proposer: 0 for proposer in proposers}
    free = deque(proposers)
    while free:
        proposer = free.popleft()
        preferences = proposer_preferences[proposer]
        while next_choice[proposer] < len(preferences):
            receiver = preferences[next_choice[proposer]]
            next_choice[proposer] += 1
            if proposer not in ranks[receiver]:
                continue
            candidates = held[receiver] + [proposer]
            candidates.sort(key=lambda value: (ranks[receiver][value], repr(value)))
            accepted = candidates[: limits[receiver]]
            rejected = candidates[limits[receiver] :]
            held[receiver] = accepted
            if proposer in accepted:
                free.extend(
                    value
                    for value in rejected
                    if next_choice[value] < len(proposer_preferences[value])
                )
                break
        # Exhausted proposers remain unmatched.
    assignments = {
        proposer: receiver for receiver, values in held.items() for proposer in values
    }
    return StableMatchingResult(
        assignments, {receiver: tuple(values) for receiver, values in held.items()}
    )


def blocking_pairs(
    matching: StableMatchingResult,
    proposer_preferences: Mapping[Key, Sequence[Key]],
    receiver_preferences: Mapping[Key, Sequence[Key]],
    *,
    capacities: Mapping[Key, int] | None = None,
) -> tuple[tuple[Key, Key], ...]:
    receiver_set = set(receiver_preferences)
    result = []
    for proposer, preferences in proposer_preferences.items():
        current = matching.assignments.get(proposer)
        acceptable = list(preferences)
        cutoff = acceptable.index(current) if current in acceptable else len(acceptable)
        for receiver in acceptable[:cutoff]:
            if (
                receiver not in receiver_set
                or proposer not in receiver_preferences[receiver]
            ):
                continue
            held = list(matching.receiver_assignments.get(receiver, ()))
            capacity = int((capacities or {}).get(receiver, 1))
            ranks = {
                value: rank for rank, value in enumerate(receiver_preferences[receiver])
            }
            if len(held) < capacity or any(
                ranks[proposer] < ranks[value] for value in held
            ):
                result.append((proposer, receiver))
    return tuple(result)


@dataclass(frozen=True)
class TeamRoleAssignment:
    slots: Mapping[tuple[int, Key], Key]
    objective: float
    team_skill: tuple[float, float]


def optimize_two_team_roles(
    players: Sequence[Key],
    roles: Sequence[Key],
    skill: Mapping[tuple[Key, Key], float],
    *,
    parties: Sequence[Sequence[Key]] = (),
    pair_synergy: Mapping[tuple[Key, Key], float] | None = None,
    max_role_gap: float | None = None,
) -> TeamRoleAssignment:
    """Assign one player to each role on two teams with party and synergy rules."""
    player_values = tuple(dict.fromkeys(players))
    role_values = tuple(dict.fromkeys(roles))
    if len(player_values) < 2 * len(role_values) or not role_values:
        raise ValueError("two-team assignment needs at least two players per role")
    player_index = {value: index for index, value in enumerate(player_values)}
    role_index = {value: index for index, value in enumerate(role_values)}
    x_count = len(player_values) * 2 * len(role_values)
    synergy_pairs = []
    for pair, value in (pair_synergy or {}).items():
        if (
            len(pair) != 2
            or pair[0] == pair[1]
            or pair[0] not in player_index
            or pair[1] not in player_index
            or not isfinite(float(value))
        ):
            raise ValueError("pair synergy is invalid")
        synergy_pairs.append((pair[0], pair[1], float(value)))
    variable_count = x_count + 2 * len(synergy_pairs)

    def x(player: Key, team: int, role: Key) -> int:
        return (player_index[player] * 2 + team) * len(role_values) + role_index[role]

    def y(pair_index: int, team: int) -> int:
        return x_count + pair_index * 2 + team

    objective = np.zeros(variable_count)
    for player in player_values:
        for team in range(2):
            for role in role_values:
                value = float(skill.get((player, role), 0.0))
                if not isfinite(value):
                    raise ValueError("player-role skills must be finite")
                objective[x(player, team, role)] = -value
    for pair_position, (_, _, value) in enumerate(synergy_pairs):
        objective[y(pair_position, 0)] = -value
        objective[y(pair_position, 1)] = -value
    rows, lower, upper = [], [], []
    for team in range(2):
        for role in role_values:
            row = np.zeros(variable_count)
            for player in player_values:
                row[x(player, team, role)] = 1.0
            rows.append(row)
            lower.append(1.0)
            upper.append(1.0)
    for player in player_values:
        row = np.zeros(variable_count)
        for team in range(2):
            for role in role_values:
                row[x(player, team, role)] = 1.0
        rows.append(row)
        lower.append(0.0)
        upper.append(1.0)
    for party in parties:
        members = tuple(dict.fromkeys(party))
        if len(members) < 2 or any(member not in player_index for member in members):
            raise ValueError("party members are invalid")
        anchor = members[0]
        for member in members[1:]:
            for team in range(2):
                row = np.zeros(variable_count)
                for role in role_values:
                    row[x(anchor, team, role)] += 1.0
                    row[x(member, team, role)] -= 1.0
                rows.append(row)
                lower.append(0.0)
                upper.append(0.0)
    for pair_position, (left, right, _) in enumerate(synergy_pairs):
        for team in range(2):
            left_membership = np.zeros(variable_count)
            right_membership = np.zeros(variable_count)
            for role in role_values:
                left_membership[x(left, team, role)] = 1.0
                right_membership[x(right, team, role)] = 1.0
            row = np.zeros(variable_count)
            row[y(pair_position, team)] = 1.0
            row -= left_membership
            rows.append(row)
            lower.append(-np.inf)
            upper.append(0.0)
            row = np.zeros(variable_count)
            row[y(pair_position, team)] = 1.0
            row -= right_membership
            rows.append(row)
            lower.append(-np.inf)
            upper.append(0.0)
            row = np.zeros(variable_count)
            row[y(pair_position, team)] = 1.0
            row -= left_membership
            row -= right_membership
            rows.append(row)
            lower.append(-1.0)
            upper.append(np.inf)
    if max_role_gap is not None:
        if not isfinite(max_role_gap) or max_role_gap < 0.0:
            raise ValueError("role fairness gap must be finite and non-negative")
        for role in role_values:
            row = np.zeros(variable_count)
            for player in player_values:
                value = float(skill.get((player, role), 0.0))
                row[x(player, 0, role)] = value
                row[x(player, 1, role)] = -value
            rows.append(row)
            lower.append(-max_role_gap)
            upper.append(max_role_gap)
    constraints = LinearConstraint(
        np.asarray(rows), np.asarray(lower), np.asarray(upper)
    )
    solved = milp(
        objective,
        integrality=np.ones(variable_count),
        bounds=Bounds(0.0, 1.0),
        constraints=constraints,
    )
    if not solved.success:
        raise RuntimeError(f"two-team role assignment failed: {solved.message}")
    slots = {}
    team_skill = [0.0, 0.0]
    for team in range(2):
        for role in role_values:
            selected = max(
                player_values, key=lambda player: solved.x[x(player, team, role)]
            )
            slots[(team, role)] = selected
            team_skill[team] += float(skill.get((selected, role), 0.0))
    return TeamRoleAssignment(slots, float(-solved.fun), (team_skill[0], team_skill[1]))


@dataclass(frozen=True)
class HeroLineup:
    selections: Mapping[Key, Key]
    objective: float
    coverage: Mapping[Key, float]


def optimize_hero_lineup(
    players: Sequence[Key],
    heroes: Sequence[Key],
    player_hero_value: Mapping[tuple[Key, Key], float],
    *,
    banned_heroes: Sequence[Key] = (),
    allowed_heroes: Mapping[Key, Sequence[Key]] | None = None,
    pair_synergy: Mapping[tuple[Key, Key], float] | None = None,
    hero_coverage: Mapping[tuple[Key, Key], float] | None = None,
    minimum_coverage: Mapping[Key, float] | None = None,
) -> HeroLineup:
    """Select a unique hero per player under bans, pools, coverage, and synergy."""
    player_values = tuple(dict.fromkeys(players))
    hero_values = tuple(dict.fromkeys(heroes))
    player_index = {value: index for index, value in enumerate(player_values)}
    hero_index = {value: index for index, value in enumerate(hero_values)}
    banned = set(banned_heroes)
    if (
        not player_values
        or len(hero_values) < len(player_values)
        or not banned.issubset(hero_index)
    ):
        raise ValueError("hero-lineup players, heroes, or bans are invalid")
    allowed = {}
    for player in player_values:
        pool = set((allowed_heroes or {}).get(player, hero_values))
        if not pool.issubset(hero_index) or not (pool - banned):
            raise ValueError("each player needs at least one valid allowed hero")
        allowed[player] = pool - banned
    x_count = len(player_values) * len(hero_values)
    synergy_pairs = []
    for pair, raw_value in (pair_synergy or {}).items():
        if (
            len(pair) != 2
            or pair[0] == pair[1]
            or pair[0] not in hero_index
            or pair[1] not in hero_index
            or not isfinite(float(raw_value))
        ):
            raise ValueError("hero-pair synergy is invalid")
        synergy_pairs.append((pair[0], pair[1], float(raw_value)))
    variable_count = x_count + len(synergy_pairs)

    def x(player: Key, hero: Key) -> int:
        return player_index[player] * len(hero_values) + hero_index[hero]

    def y(pair_position: int) -> int:
        return x_count + pair_position

    objective = np.zeros(variable_count)
    upper_bounds = np.ones(variable_count)
    for player in player_values:
        for hero in hero_values:
            value = float(player_hero_value.get((player, hero), 0.0))
            if not isfinite(value):
                raise ValueError("player-hero values must be finite")
            objective[x(player, hero)] = -value
            if hero not in allowed[player]:
                upper_bounds[x(player, hero)] = 0.0
    for pair_position, (_, _, value) in enumerate(synergy_pairs):
        objective[y(pair_position)] = -value
    rows, lower, upper = [], [], []
    for player in player_values:
        row = np.zeros(variable_count)
        for hero in hero_values:
            row[x(player, hero)] = 1.0
        rows.append(row)
        lower.append(1.0)
        upper.append(1.0)
    for hero in hero_values:
        row = np.zeros(variable_count)
        for player in player_values:
            row[x(player, hero)] = 1.0
        rows.append(row)
        lower.append(0.0)
        upper.append(1.0)
    for pair_position, (left, right, _) in enumerate(synergy_pairs):
        left_selected = np.zeros(variable_count)
        right_selected = np.zeros(variable_count)
        for player in player_values:
            left_selected[x(player, left)] = 1.0
            right_selected[x(player, right)] = 1.0
        row = np.zeros(variable_count)
        row[y(pair_position)] = 1.0
        row -= left_selected
        rows.append(row)
        lower.append(-np.inf)
        upper.append(0.0)
        row = np.zeros(variable_count)
        row[y(pair_position)] = 1.0
        row -= right_selected
        rows.append(row)
        lower.append(-np.inf)
        upper.append(0.0)
        row = np.zeros(variable_count)
        row[y(pair_position)] = 1.0
        row -= left_selected
        row -= right_selected
        rows.append(row)
        lower.append(-1.0)
        upper.append(np.inf)
    coverage_values = hero_coverage or {}
    requirements = minimum_coverage or {}
    for responsibility, raw_minimum in requirements.items():
        minimum = float(raw_minimum)
        if not isfinite(minimum) or minimum < 0.0:
            raise ValueError("minimum hero coverage must be finite and non-negative")
        row = np.zeros(variable_count)
        for player in player_values:
            for hero in hero_values:
                value = float(coverage_values.get((hero, responsibility), 0.0))
                if not isfinite(value) or value < 0.0:
                    raise ValueError("hero coverage must be finite and non-negative")
                row[x(player, hero)] = value
        rows.append(row)
        lower.append(minimum)
        upper.append(np.inf)
    constraints = LinearConstraint(
        np.asarray(rows), np.asarray(lower), np.asarray(upper)
    )
    solved = milp(
        objective,
        integrality=np.ones(variable_count),
        bounds=Bounds(np.zeros(variable_count), upper_bounds),
        constraints=constraints,
    )
    if not solved.success:
        raise RuntimeError(f"hero lineup optimization failed: {solved.message}")
    selections = {
        player: max(hero_values, key=lambda hero: solved.x[x(player, hero)])
        for player in player_values
    }
    achieved = {
        responsibility: sum(
            float(coverage_values.get((hero, responsibility), 0.0))
            for hero in selections.values()
        )
        for responsibility in requirements
    }
    return HeroLineup(selections, float(-solved.fun), achieved)


@dataclass(frozen=True)
class DynamicTaskAssignment:
    assignments: tuple[Mapping[Key, Key | None], ...]
    objective: float
    switch_count: int


def optimize_dynamic_tasks(
    agents: Sequence[Key],
    tasks: Sequence[Key],
    utilities: Sequence[Mapping[tuple[Key, Key], float]],
    minimum_staffing: Sequence[Mapping[Key, int]],
    maximum_staffing: Sequence[Mapping[Key, int]],
    *,
    switch_cost: float = 0.0,
) -> DynamicTaskAssignment:
    """Time-expanded assignment MILP with idle states and assignment-switch costs."""
    agent_values = tuple(dict.fromkeys(agents))
    task_values = tuple(dict.fromkeys(tasks))
    horizon = len(utilities)
    if (
        not agent_values
        or not task_values
        or horizon == 0
        or len(minimum_staffing) != horizon
        or len(maximum_staffing) != horizon
        or not isfinite(switch_cost)
        or switch_cost < 0.0
    ):
        raise ValueError("dynamic task assignment inputs are invalid")
    states: tuple[Key | None, ...] = (*task_values, None)
    agent_index = {value: index for index, value in enumerate(agent_values)}
    state_index = {value: index for index, value in enumerate(states)}
    x_count = horizon * len(agent_values) * len(states)
    switch_count = max(0, horizon - 1) * len(agent_values)
    variable_count = x_count + switch_count

    def x(time: int, agent: Key, state: Key | None) -> int:
        return (time * len(agent_values) + agent_index[agent]) * len(
            states
        ) + state_index[state]

    def switched(time: int, agent: Key) -> int:
        return x_count + (time - 1) * len(agent_values) + agent_index[agent]

    objective = np.zeros(variable_count)
    for time in range(horizon):
        for agent in agent_values:
            for task in task_values:
                value = float(utilities[time].get((agent, task), 0.0))
                if not isfinite(value):
                    raise ValueError("dynamic assignment utilities must be finite")
                objective[x(time, agent, task)] = -value
    objective[x_count:] = switch_cost
    rows, lower, upper = [], [], []
    for time in range(horizon):
        for agent in agent_values:
            row = np.zeros(variable_count)
            for state in states:
                row[x(time, agent, state)] = 1.0
            rows.append(row)
            lower.append(1.0)
            upper.append(1.0)
        for task in task_values:
            minimum = int(minimum_staffing[time].get(task, 0))
            maximum = int(maximum_staffing[time].get(task, len(agent_values)))
            if minimum < 0 or maximum < minimum:
                raise ValueError("dynamic staffing bounds are invalid")
            row = np.zeros(variable_count)
            for agent in agent_values:
                row[x(time, agent, task)] = 1.0
            rows.append(row)
            lower.append(float(minimum))
            upper.append(float(maximum))
    for time in range(1, horizon):
        for agent in agent_values:
            for state in states:
                row = np.zeros(variable_count)
                row[x(time - 1, agent, state)] = 1.0
                row[x(time, agent, state)] = -1.0
                row[switched(time, agent)] = -1.0
                rows.append(row)
                lower.append(-np.inf)
                upper.append(0.0)
    constraints = LinearConstraint(
        np.asarray(rows), np.asarray(lower), np.asarray(upper)
    )
    solved = milp(
        objective,
        integrality=np.ones(variable_count),
        bounds=Bounds(0.0, 1.0),
        constraints=constraints,
    )
    if not solved.success:
        raise RuntimeError(f"dynamic task assignment failed: {solved.message}")
    assignments = []
    for time in range(horizon):
        current = {}
        for agent in agent_values:
            state = max(states, key=lambda value: solved.x[x(time, agent, value)])
            if state is not None:
                current[agent] = state
        assignments.append(current)
    changed = sum(
        assignments[time - 1].get(agent) != assignments[time].get(agent)
        for time in range(1, horizon)
        for agent in agent_values
    )
    utility = sum(
        float(utilities[time].get((agent, task), 0.0))
        for time, assignment in enumerate(assignments)
        for agent, task in assignment.items()
    )
    return DynamicTaskAssignment(
        tuple(assignments), utility - switch_cost * changed, int(changed)
    )
