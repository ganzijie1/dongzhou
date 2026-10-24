"""P26 factor-graph inference, DCOP Max-Sum, junction trees, and ADMM."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite, sqrt
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class DiscreteFactor:
    scope: tuple[int, ...]
    values: np.ndarray


def _validate_factors(
    cardinalities: Sequence[int],
    factors: Sequence[DiscreteFactor],
) -> tuple[tuple[int, ...], tuple[DiscreteFactor, ...], list[list[int]]]:
    cards = tuple(int(value) for value in cardinalities)
    if not cards or any(value < 1 for value in cards) or not factors:
        raise ValueError("factor graph needs variables, cardinalities, and factors")
    normalized = []
    neighbors = [[] for _ in cards]
    for factor_index, factor in enumerate(factors):
        scope = tuple(int(value) for value in factor.scope)
        values = np.asarray(factor.values, dtype=np.float64)
        if (
            not scope
            or len(set(scope)) != len(scope)
            or any(not 0 <= variable < len(cards) for variable in scope)
            or values.shape != tuple(cards[variable] for variable in scope)
            or np.any(~np.isfinite(values))
        ):
            raise ValueError("factor scope or table is invalid")
        normalized.append(DiscreteFactor(scope, values))
        for variable in scope:
            neighbors[variable].append(factor_index)
    if any(not adjacent for adjacent in neighbors):
        raise ValueError("every variable must occur in at least one factor")
    return cards, tuple(normalized), neighbors


def _normalize_probability(message: np.ndarray) -> np.ndarray:
    message = np.maximum(np.asarray(message, dtype=np.float64), 0.0)
    total = float(message.sum())
    if total <= 0.0 or not isfinite(total):
        raise ValueError("belief-propagation message has zero or invalid mass")
    return message / total


def _broadcast_message(
    message: np.ndarray,
    variable: int,
    scope: tuple[int, ...],
) -> np.ndarray:
    shape = [1] * len(scope)
    shape[scope.index(variable)] = message.size
    return message.reshape(shape)


@dataclass(frozen=True)
class BeliefPropagationResult:
    variable_beliefs: tuple[np.ndarray, ...]
    factor_beliefs: tuple[np.ndarray, ...]
    residual: float
    iterations: int
    converged: bool


def loopy_belief_propagation(
    cardinalities: Sequence[int],
    factors: Sequence[DiscreteFactor],
    *,
    max_iterations: int = 500,
    tolerance: float = 1e-10,
    damping: float = 1.0,
) -> BeliefPropagationResult:
    """Sum-product BP; exact on trees and diagnosed approximation on loopy graphs."""

    cards, factor_list, variable_neighbors = _validate_factors(
        cardinalities, factors
    )
    if (
        max_iterations < 1
        or tolerance <= 0.0
        or not isfinite(damping)
        or not 0.0 < damping <= 1.0
        or any(np.any(factor.values < 0.0) for factor in factor_list)
    ):
        raise ValueError("sum-product settings or potentials are invalid")
    variable_to_factor = {
        (variable, factor): np.full(cards[variable], 1.0 / cards[variable])
        for variable, adjacent in enumerate(variable_neighbors)
        for factor in adjacent
    }
    factor_to_variable = {
        (factor_index, variable): np.full(cards[variable], 1.0 / cards[variable])
        for factor_index, factor in enumerate(factor_list)
        for variable in factor.scope
    }
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        new_factor = {}
        for factor_index, factor in enumerate(factor_list):
            for variable in factor.scope:
                table = factor.values.copy()
                for other in factor.scope:
                    if other != variable:
                        table *= _broadcast_message(
                            variable_to_factor[(other, factor_index)],
                            other,
                            factor.scope,
                        )
                axes = tuple(
                    axis
                    for axis, scoped_variable in enumerate(factor.scope)
                    if scoped_variable != variable
                )
                message = table.sum(axis=axes) if axes else table
                proposed = _normalize_probability(message)
                old = factor_to_variable[(factor_index, variable)]
                new_factor[(factor_index, variable)] = _normalize_probability(
                    (1.0 - damping) * old + damping * proposed
                )
        new_variable = {}
        for variable, adjacent in enumerate(variable_neighbors):
            for factor_index in adjacent:
                message = np.ones(cards[variable])
                for other_factor in adjacent:
                    if other_factor != factor_index:
                        message *= new_factor[(other_factor, variable)]
                proposed = _normalize_probability(message)
                old = variable_to_factor[(variable, factor_index)]
                new_variable[(variable, factor_index)] = _normalize_probability(
                    (1.0 - damping) * old + damping * proposed
                )
        differences = [
            np.max(np.abs(new_factor[key] - factor_to_variable[key]))
            for key in new_factor
        ] + [
            np.max(np.abs(new_variable[key] - variable_to_factor[key]))
            for key in new_variable
        ]
        residual = float(max(differences, default=0.0))
        factor_to_variable = new_factor
        variable_to_factor = new_variable
        if residual <= tolerance:
            break
    variable_beliefs = []
    for variable, adjacent in enumerate(variable_neighbors):
        belief = np.ones(cards[variable])
        for factor_index in adjacent:
            belief *= factor_to_variable[(factor_index, variable)]
        variable_beliefs.append(_normalize_probability(belief))
    factor_beliefs = []
    for factor_index, factor in enumerate(factor_list):
        belief = factor.values.copy()
        for variable in factor.scope:
            belief *= _broadcast_message(
                variable_to_factor[(variable, factor_index)],
                variable,
                factor.scope,
            )
        factor_beliefs.append(_normalize_probability(belief))
    return BeliefPropagationResult(
        tuple(variable_beliefs),
        tuple(factor_beliefs),
        residual,
        iteration,
        residual <= tolerance,
    )


def _factor_graph_is_tree(
    variable_neighbors: Sequence[Sequence[int]],
    factors: Sequence[DiscreteFactor],
) -> bool:
    variable_count = len(variable_neighbors)
    factor_count = len(factors)
    total_nodes = variable_count + factor_count
    edge_count = sum(len(factor.scope) for factor in factors)
    if edge_count != total_nodes - 1:
        return False
    seen = {0}
    stack = [("v", 0)]
    while stack:
        kind, index = stack.pop()
        if kind == "v":
            adjacent = [variable_count + value for value in variable_neighbors[index]]
        else:
            adjacent = list(factors[index].scope)
        for node in adjacent:
            unified = node
            if unified not in seen:
                seen.add(unified)
                stack.append(
                    ("f", unified - variable_count)
                    if unified >= variable_count
                    else ("v", unified)
                )
    return len(seen) == total_nodes


def _objective(assignment: Sequence[int], factors: Sequence[DiscreteFactor]) -> float:
    return float(
        sum(factor.values[tuple(assignment[v] for v in factor.scope)] for factor in factors)
    )


@dataclass(frozen=True)
class MaxSumResult:
    assignment: tuple[int, ...]
    objective: float
    local_assignment: tuple[int, ...]
    residual: float
    iterations: int
    converged: bool
    exact_tree: bool


def max_sum_dcop(
    cardinalities: Sequence[int],
    factors: Sequence[DiscreteFactor],
    *,
    max_iterations: int = 500,
    tolerance: float = 1e-10,
    damping: float = 1.0,
    maximum_exact_assignments: int = 1_000_000,
) -> MaxSumResult:
    """Max-Sum messages with exact tree decoding and loopy diagnostics."""

    cards, factor_list, variable_neighbors = _validate_factors(
        cardinalities, factors
    )
    if (
        max_iterations < 1
        or tolerance <= 0.0
        or not 0.0 < damping <= 1.0
    ):
        raise ValueError("Max-Sum settings are invalid")
    variable_to_factor = {
        (variable, factor): np.zeros(cards[variable])
        for variable, adjacent in enumerate(variable_neighbors)
        for factor in adjacent
    }
    factor_to_variable = {
        (factor_index, variable): np.zeros(cards[variable])
        for factor_index, factor in enumerate(factor_list)
        for variable in factor.scope
    }
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        new_factor = {}
        for factor_index, factor in enumerate(factor_list):
            for variable in factor.scope:
                table = factor.values.copy()
                for other in factor.scope:
                    if other != variable:
                        table += _broadcast_message(
                            variable_to_factor[(other, factor_index)],
                            other,
                            factor.scope,
                        )
                axes = tuple(
                    axis
                    for axis, scoped_variable in enumerate(factor.scope)
                    if scoped_variable != variable
                )
                proposed = table.max(axis=axes) if axes else table
                proposed = proposed - np.max(proposed)
                old = factor_to_variable[(factor_index, variable)]
                mixed = (1.0 - damping) * old + damping * proposed
                new_factor[(factor_index, variable)] = mixed - np.max(mixed)
        new_variable = {}
        for variable, adjacent in enumerate(variable_neighbors):
            for factor_index in adjacent:
                proposed = sum(
                    (
                        new_factor[(other_factor, variable)]
                        for other_factor in adjacent
                        if other_factor != factor_index
                    ),
                    np.zeros(cards[variable]),
                )
                proposed -= np.max(proposed)
                old = variable_to_factor[(variable, factor_index)]
                mixed = (1.0 - damping) * old + damping * proposed
                new_variable[(variable, factor_index)] = mixed - np.max(mixed)
        differences = [
            np.max(np.abs(new_factor[key] - factor_to_variable[key]))
            for key in new_factor
        ] + [
            np.max(np.abs(new_variable[key] - variable_to_factor[key]))
            for key in new_variable
        ]
        residual = float(max(differences, default=0.0))
        factor_to_variable = new_factor
        variable_to_factor = new_variable
        if residual <= tolerance:
            break
    scores = []
    for variable, adjacent in enumerate(variable_neighbors):
        scores.append(
            sum(
                (factor_to_variable[(factor, variable)] for factor in adjacent),
                np.zeros(cards[variable]),
            )
        )
    local_assignment = tuple(int(np.argmax(value)) for value in scores)
    exact_tree = _factor_graph_is_tree(variable_neighbors, factor_list)
    assignment = local_assignment
    if exact_tree:
        count = int(np.prod(cards))
        if count > maximum_exact_assignments:
            raise ValueError("exact tree decoding exceeds maximum_exact_assignments")
        # Exhaustive decoding resolves tied local maxima consistently and audits messages.
        assignment = max(
            product(*(range(cardinality) for cardinality in cards)),
            key=lambda value: _objective(value, factor_list),
        )
    return MaxSumResult(
        tuple(assignment),
        _objective(assignment, factor_list),
        local_assignment,
        residual,
        iteration,
        residual <= tolerance,
        exact_tree,
    )


def _tree_edges(node_count: int, edges: Sequence[tuple[int, int]]) -> list[list[int]]:
    adjacency = [[] for _ in range(node_count)]
    if len(edges) != node_count - 1:
        raise ValueError("junction graph must contain exactly clique_count - 1 edges")
    for left, right in edges:
        if (
            not 0 <= left < node_count
            or not 0 <= right < node_count
            or left == right
        ):
            raise ValueError("junction-tree edge is invalid")
        adjacency[left].append(right)
        adjacency[right].append(left)
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    if len(seen) != node_count:
        raise ValueError("junction graph must be connected")
    return adjacency


@dataclass(frozen=True)
class JunctionTreeResult:
    clique_beliefs: tuple[np.ndarray, ...]
    variable_beliefs: tuple[np.ndarray, ...]
    separator_residual: float


def junction_tree_calibrate(
    cardinalities: Sequence[int],
    cliques: Sequence[Sequence[int]],
    clique_potentials: Sequence,
    edges: Sequence[tuple[int, int]],
) -> JunctionTreeResult:
    """Calibrate a caller-supplied valid clique tree by sum-product messages."""

    cards = tuple(int(value) for value in cardinalities)
    clique_list = tuple(tuple(int(v) for v in clique) for clique in cliques)
    potentials = tuple(np.asarray(value, dtype=np.float64) for value in clique_potentials)
    if (
        not cards
        or not clique_list
        or len(clique_list) != len(potentials)
        or any(value < 1 for value in cards)
    ):
        raise ValueError("junction-tree inputs are empty or inconsistent")
    for clique, potential in zip(clique_list, potentials):
        if (
            not clique
            or len(set(clique)) != len(clique)
            or any(not 0 <= variable < len(cards) for variable in clique)
            or potential.shape != tuple(cards[variable] for variable in clique)
            or np.any(~np.isfinite(potential))
            or np.any(potential < 0.0)
        ):
            raise ValueError("clique potential is invalid")
    adjacency = _tree_edges(len(clique_list), edges)
    for variable in range(len(cards)):
        containing = {i for i, clique in enumerate(clique_list) if variable in clique}
        if not containing:
            raise ValueError("every variable must occur in a clique")
        reached = {next(iter(containing))}
        stack = list(reached)
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor in containing and neighbor not in reached:
                    reached.add(neighbor)
                    stack.append(neighbor)
        if reached != containing:
            raise ValueError("cliques violate the running-intersection property")

    messages: dict[tuple[int, int], tuple[tuple[int, ...], np.ndarray]] = {}

    def expand(message: np.ndarray, separator: tuple[int, ...], clique: tuple[int, ...]):
        shape = [1] * len(clique)
        for axis, variable in enumerate(separator):
            shape[clique.index(variable)] = message.shape[axis]
        order = sorted(range(len(separator)), key=lambda axis: clique.index(separator[axis]))
        aligned = np.transpose(message, order) if len(order) > 1 else message
        ordered_separator = tuple(separator[axis] for axis in order)
        shape = [1] * len(clique)
        for axis, variable in enumerate(ordered_separator):
            shape[clique.index(variable)] = aligned.shape[axis]
        return aligned.reshape(shape)

    def compute(source: int, target: int):
        if (source, target) in messages:
            return messages[(source, target)]
        table = potentials[source].copy()
        for neighbor in adjacency[source]:
            if neighbor == target:
                continue
            separator, incoming = compute(neighbor, source)
            table *= expand(incoming, separator, clique_list[source])
        separator = tuple(sorted(set(clique_list[source]) & set(clique_list[target])))
        axes = tuple(
            axis
            for axis, variable in enumerate(clique_list[source])
            if variable not in separator
        )
        message = table.sum(axis=axes) if axes else table
        remaining = tuple(v for v in clique_list[source] if v in separator)
        if remaining != separator and len(separator) > 1:
            message = np.transpose(message, [remaining.index(v) for v in separator])
        message = _normalize_probability(message)
        messages[(source, target)] = (separator, message)
        return separator, message

    for left, right in edges:
        compute(left, right)
        compute(right, left)
    beliefs = []
    for clique_index, clique in enumerate(clique_list):
        belief = potentials[clique_index].copy()
        for neighbor in adjacency[clique_index]:
            separator, message = messages[(neighbor, clique_index)]
            belief *= expand(message, separator, clique)
        beliefs.append(_normalize_probability(belief))
    variable_beliefs = []
    for variable in range(len(cards)):
        clique_index = next(i for i, clique in enumerate(clique_list) if variable in clique)
        clique = clique_list[clique_index]
        axes = tuple(axis for axis, value in enumerate(clique) if value != variable)
        marginal = beliefs[clique_index].sum(axis=axes) if axes else beliefs[clique_index]
        variable_beliefs.append(_normalize_probability(marginal))
    separator_residual = 0.0
    for left, right in edges:
        separator = tuple(sorted(set(clique_list[left]) & set(clique_list[right])))
        marginals = []
        for clique_index in (left, right):
            clique = clique_list[clique_index]
            axes = tuple(
                axis for axis, variable in enumerate(clique) if variable not in separator
            )
            marginal = beliefs[clique_index].sum(axis=axes) if axes else beliefs[clique_index]
            remaining = tuple(v for v in clique if v in separator)
            if remaining != separator and len(separator) > 1:
                marginal = np.transpose(marginal, [remaining.index(v) for v in separator])
            marginals.append(_normalize_probability(marginal))
        separator_residual = max(
            separator_residual, float(np.max(np.abs(marginals[0] - marginals[1])))
        )
    return JunctionTreeResult(
        tuple(beliefs), tuple(variable_beliefs), separator_residual
    )


@dataclass(frozen=True)
class ConsensusADMMResult:
    local_values: tuple[np.ndarray, ...]
    consensus: np.ndarray
    dual_values: tuple[np.ndarray, ...]
    primal_residuals: tuple[float, ...]
    dual_residuals: tuple[float, ...]
    rho_history: tuple[float, ...]
    converged: bool
    iterations: int


def consensus_admm(
    proximal_operators: Sequence[Callable[[np.ndarray, float], np.ndarray]],
    initial_consensus: Sequence[float],
    *,
    rho: float = 1.0,
    absolute_tolerance: float = 1e-6,
    relative_tolerance: float = 1e-5,
    max_iterations: int = 10_000,
    adaptive_rho: bool = True,
    residual_ratio: float = 10.0,
    rho_scale: float = 2.0,
) -> ConsensusADMMResult:
    """Generic scaled consensus ADMM from caller-provided proximal operators."""

    z = np.asarray(initial_consensus, dtype=np.float64)
    if (
        not proximal_operators
        or z.ndim != 1
        or z.size == 0
        or np.any(~np.isfinite(z))
        or not isfinite(rho)
        or rho <= 0.0
        or absolute_tolerance <= 0.0
        or relative_tolerance <= 0.0
        or max_iterations < 1
        or residual_ratio <= 1.0
        or rho_scale <= 1.0
    ):
        raise ValueError("ADMM settings are invalid")
    count = len(proximal_operators)
    local = [z.copy() for _ in range(count)]
    dual = [np.zeros_like(z) for _ in range(count)]
    primal_history = []
    dual_history = []
    rho_history = []
    converged = False
    for iteration in range(1, max_iterations + 1):
        for index, operator in enumerate(proximal_operators):
            value = np.asarray(operator(z - dual[index], rho), dtype=np.float64)
            if value.shape != z.shape or np.any(~np.isfinite(value)):
                raise ValueError("proximal operator returned an invalid value")
            local[index] = value
        previous = z.copy()
        z = np.mean(
            np.stack([local[i] + dual[i] for i in range(count)]), axis=0
        )
        for index in range(count):
            dual[index] = dual[index] + local[index] - z
        primal = sqrt(sum(float(np.sum((value - z) ** 2)) for value in local))
        dual_residual = sqrt(count) * rho * float(np.linalg.norm(z - previous))
        primal_history.append(primal)
        dual_history.append(dual_residual)
        rho_history.append(rho)
        norm_local = sqrt(sum(float(np.sum(value**2)) for value in local))
        norm_consensus = sqrt(count) * float(np.linalg.norm(z))
        eps_primal = sqrt(count * z.size) * absolute_tolerance + relative_tolerance * max(
            norm_local, norm_consensus
        )
        norm_dual = sqrt(sum(float(np.sum((rho * value) ** 2)) for value in dual))
        eps_dual = sqrt(count * z.size) * absolute_tolerance + relative_tolerance * norm_dual
        if primal <= eps_primal and dual_residual <= eps_dual:
            converged = True
            break
        if adaptive_rho:
            old_rho = rho
            if primal > residual_ratio * dual_residual:
                rho *= rho_scale
            elif dual_residual > residual_ratio * primal:
                rho /= rho_scale
            if rho != old_rho:
                scale = old_rho / rho
                dual = [value * scale for value in dual]
    return ConsensusADMMResult(
        tuple(value.copy() for value in local),
        z.copy(),
        tuple(value.copy() for value in dual),
        tuple(primal_history),
        tuple(dual_history),
        tuple(rho_history),
        converged,
        iteration,
    )
