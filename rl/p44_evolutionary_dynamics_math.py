"""P44 replicator/logit dynamics, ESS diagnostics, and resistance trees."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Sequence

import numpy as np


def _simplex(strategy: Sequence[float]) -> np.ndarray:
    value = np.asarray(strategy, dtype=np.float64)
    if value.ndim != 1 or value.size == 0 or np.any(~np.isfinite(value)) or np.any(value < 0.0) or not np.isclose(value.sum(), 1.0):
        raise ValueError("strategy must lie on the simplex")
    return value


def replicator_rhs(strategy: Sequence[float], payoff_matrix: Sequence) -> np.ndarray:
    state = _simplex(strategy)
    payoff = np.asarray(payoff_matrix, dtype=np.float64)
    if payoff.shape != (state.size, state.size) or np.any(~np.isfinite(payoff)):
        raise ValueError("payoff matrix is invalid")
    fitness = payoff @ state
    return state * (fitness - float(state @ fitness))


def replicator_mutator_rhs(
    strategy: Sequence[float], payoff_matrix: Sequence, mutation_matrix: Sequence
) -> np.ndarray:
    state = _simplex(strategy)
    payoff = np.asarray(payoff_matrix, dtype=np.float64)
    mutation = np.asarray(mutation_matrix, dtype=np.float64)
    if (
        payoff.shape != (state.size, state.size)
        or mutation.shape != payoff.shape
        or np.any(~np.isfinite(payoff))
        or np.any(mutation < 0.0)
        or not np.allclose(mutation.sum(axis=1), 1.0)
    ):
        raise ValueError("replicator-mutator inputs are invalid")
    fitness = payoff @ state
    births = (state * fitness) @ mutation
    return births - state * float(state @ fitness)


def logit_response(payoffs: Sequence[float], *, temperature: float) -> np.ndarray:
    values = np.asarray(payoffs, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or not isfinite(temperature) or temperature <= 0.0:
        raise ValueError("logit inputs are invalid")
    scaled = values / temperature
    weights = np.exp(scaled - np.max(scaled))
    return weights / weights.sum()


@dataclass(frozen=True)
class ESSDiagnostic:
    is_nash: bool
    is_ess: bool
    invasion_margins: np.ndarray


def pure_ess_diagnostic(payoff_matrix: Sequence, strategy: int, *, tolerance: float = 1e-10) -> ESSDiagnostic:
    payoff = np.asarray(payoff_matrix, dtype=np.float64)
    if payoff.ndim != 2 or payoff.shape[0] != payoff.shape[1] or np.any(~np.isfinite(payoff)) or not 0 <= strategy < payoff.shape[0]:
        raise ValueError("ESS inputs are invalid")
    margins = np.empty(payoff.shape[0])
    is_nash = True
    is_ess = True
    for mutant in range(payoff.shape[0]):
        if mutant == strategy:
            margins[mutant] = 0.0
            continue
        first = payoff[strategy, strategy] - payoff[mutant, strategy]
        if first < -tolerance:
            is_nash = is_ess = False
            margins[mutant] = first
        elif first > tolerance:
            margins[mutant] = first
        else:
            second = payoff[strategy, mutant] - payoff[mutant, mutant]
            margins[mutant] = second
            if second <= tolerance:
                is_ess = False
    return ESSDiagnostic(is_nash, is_ess, margins)


def stationary_distribution(transition: Sequence) -> np.ndarray:
    matrix = np.asarray(transition, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0) or not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError("transition matrix is invalid")
    system = np.vstack((matrix.T - np.eye(matrix.shape[0]), np.ones(matrix.shape[0])))
    target = np.append(np.zeros(matrix.shape[0]), 1.0)
    solution, *_ = np.linalg.lstsq(system, target, rcond=None)
    solution = np.maximum(solution, 0.0)
    return solution / solution.sum()


def resistance_tree_potentials(resistances: Sequence) -> np.ndarray:
    """Minimum directed in-tree resistance for each root; intended for small state sets."""

    matrix = np.asarray(resistances, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or matrix.shape[0] == 0
        or matrix.shape[0] > 8
        or np.any(np.isnan(matrix))
        or np.any(matrix < 0.0)
    ):
        raise ValueError("resistance matrix is invalid")
    states = matrix.shape[0]
    potentials = np.full(states, np.inf)
    for root in range(states):
        nodes = [node for node in range(states) if node != root]
        choices = [[parent for parent in range(states) if parent != node and np.isfinite(matrix[node, parent])] for node in nodes]
        if any(not choice for choice in choices):
            continue
        for parents in product(*choices):
            mapping = dict(zip(nodes, parents))
            valid = True
            for node in nodes:
                seen = set()
                cursor = node
                while cursor != root:
                    if cursor in seen or cursor not in mapping:
                        valid = False
                        break
                    seen.add(cursor)
                    cursor = mapping[cursor]
                if not valid:
                    break
            if valid:
                potentials[root] = min(potentials[root], sum(matrix[node, mapping[node]] for node in nodes))
    return potentials


def stochastically_stable_states(resistances: Sequence, *, tolerance: float = 1e-10) -> np.ndarray:
    potentials = resistance_tree_potentials(resistances)
    if np.all(~np.isfinite(potentials)):
        return np.array([], dtype=int)
    return np.flatnonzero(potentials <= np.nanmin(potentials) + tolerance)
