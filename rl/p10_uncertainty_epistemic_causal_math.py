"""P10 imprecise probability, epistemic games, causality, and information value.

The implementations are deliberately finite and auditable.  They do not infer
priors, evidence reliability, epistemic accessibility, or causal graphs from
game state: callers must supply those modelling choices explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, factorial, isfinite
from typing import Callable, Hashable, Iterable, Mapping, Sequence

import numpy as np


Key = Hashable
Predicate = str | Callable[[Key, frozenset[str]], bool]


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64)
    if (
        vector.ndim != 1
        or vector.size == 0
        or np.any(~np.isfinite(vector))
        or np.any(vector < 0.0)
        or not np.isclose(float(vector.sum()), 1.0, atol=1e-9)
    ):
        raise ValueError(f"{name} must be a finite probability vector")
    return vector


def _softmax(values: np.ndarray, precision: float) -> np.ndarray:
    if precision < 0.0 or not isfinite(precision):
        raise ValueError("logit precision must be finite and non-negative")
    shifted = precision * values
    shifted -= float(np.max(shifted))
    weights = np.exp(shifted)
    return weights / float(weights.sum())


class CredalSet:
    """A finite credal set represented by probability-polytope vertices."""

    def __init__(
        self,
        outcomes: Sequence[Key],
        vertices: Sequence[Mapping[Key, float] | Sequence[float]],
    ) -> None:
        self.outcomes = tuple(outcomes)
        if not self.outcomes or len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("credal outcomes must be non-empty and unique")
        if not vertices:
            raise ValueError("credal set needs at least one vertex")
        arrays = []
        for vertex in vertices:
            values = (
                [float(vertex.get(outcome, 0.0)) for outcome in self.outcomes]
                if isinstance(vertex, Mapping)
                else list(vertex)
            )
            if len(values) != len(self.outcomes):
                raise ValueError("credal vertex dimension is invalid")
            arrays.append(_probability_vector(values, "credal vertex"))
        self.vertices = tuple(arrays)

    def expectation_interval(self, utility: Mapping[Key, float]) -> tuple[float, float]:
        values = np.asarray(
            [float(utility[outcome]) for outcome in self.outcomes], dtype=np.float64
        )
        if np.any(~np.isfinite(values)):
            raise ValueError("credal utility must be finite")
        expectations = [float(vertex @ values) for vertex in self.vertices]
        return min(expectations), max(expectations)

    def probability_interval(self, event: Iterable[Key]) -> tuple[float, float]:
        event_set = set(event)
        unknown = event_set - set(self.outcomes)
        if unknown:
            raise ValueError("credal event contains an unknown outcome")
        return self.expectation_interval(
            {outcome: float(outcome in event_set) for outcome in self.outcomes}
        )

    def maximin_action(
        self, utilities: Mapping[Key, Mapping[Key, float]]
    ) -> tuple[Key, dict[Key, float]]:
        if not utilities:
            raise ValueError("robust choice needs at least one action")
        lower = {
            action: self.expectation_interval(payoff)[0]
            for action, payoff in utilities.items()
        }
        choice = min(lower, key=lambda action: (-lower[action], repr(action)))
        return choice, lower


class MassFunction:
    """A normalized finite Dempster-Shafer basic probability assignment."""

    def __init__(
        self, frame: Iterable[Key], masses: Mapping[Iterable[Key], float]
    ) -> None:
        self.frame = frozenset(frame)
        if not self.frame:
            raise ValueError("Dempster-Shafer frame cannot be empty")
        canonical: dict[frozenset[Key], float] = {}
        for raw_focal, raw_mass in masses.items():
            focal = frozenset(raw_focal)
            mass = float(raw_mass)
            if not focal <= self.frame or not isfinite(mass) or mass < 0.0:
                raise ValueError("invalid Dempster-Shafer focal mass")
            canonical[focal] = canonical.get(focal, 0.0) + mass
        if canonical.get(frozenset(), 0.0) > 1e-12:
            raise ValueError("normalized mass cannot assign belief to the empty set")
        canonical.pop(frozenset(), None)
        if not np.isclose(sum(canonical.values()), 1.0, atol=1e-9):
            raise ValueError("Dempster-Shafer masses must sum to one")
        self.masses = canonical

    def belief(self, event: Iterable[Key]) -> float:
        target = frozenset(event)
        if not target <= self.frame:
            raise ValueError("belief event contains an unknown outcome")
        return sum(mass for focal, mass in self.masses.items() if focal <= target)

    def plausibility(self, event: Iterable[Key]) -> float:
        target = frozenset(event)
        if not target <= self.frame:
            raise ValueError("plausibility event contains an unknown outcome")
        return sum(mass for focal, mass in self.masses.items() if focal & target)

    def pignistic(self) -> dict[Key, float]:
        result = {outcome: 0.0 for outcome in self.frame}
        for focal, mass in self.masses.items():
            share = mass / len(focal)
            for outcome in focal:
                result[outcome] += share
        return result

    def combine(self, other: "MassFunction") -> tuple["MassFunction", float]:
        if self.frame != other.frame:
            raise ValueError("Dempster-Shafer frames must match")
        products: dict[frozenset[Key], float] = {}
        conflict = 0.0
        for left, left_mass in self.masses.items():
            for right, right_mass in other.masses.items():
                intersection = left & right
                value = left_mass * right_mass
                if not intersection:
                    conflict += value
                else:
                    products[intersection] = products.get(intersection, 0.0) + value
        if conflict >= 1.0 - 1e-12:
            raise ValueError("Dempster rule is undefined under total conflict")
        normalized = {
            focal: mass / (1.0 - conflict) for focal, mass in products.items()
        }
        return MassFunction(self.frame, normalized), conflict


class EpistemicModel:
    """Finite Kripke model with public-announcement DEL updates."""

    def __init__(
        self,
        worlds: Sequence[Key],
        valuations: Mapping[Key, Iterable[str]],
        accessibility: Mapping[str, Mapping[Key, Iterable[Key]]],
    ) -> None:
        self.worlds = tuple(worlds)
        world_set = set(self.worlds)
        if not self.worlds or len(world_set) != len(self.worlds):
            raise ValueError("epistemic worlds must be non-empty and unique")
        if set(valuations) != world_set:
            raise ValueError("every epistemic world needs a valuation")
        self.valuations = {world: frozenset(valuations[world]) for world in self.worlds}
        relations: dict[str, dict[Key, frozenset[Key]]] = {}
        for agent, by_world in accessibility.items():
            if set(by_world) != world_set:
                raise ValueError("every agent relation must cover every world")
            relation = {world: frozenset(by_world[world]) for world in self.worlds}
            if any(not targets <= world_set for targets in relation.values()):
                raise ValueError("epistemic relation references an unknown world")
            relations[agent] = relation
        if not relations:
            raise ValueError("epistemic model needs at least one agent")
        self.accessibility = relations

    def satisfies(self, world: Key, proposition: Predicate) -> bool:
        if world not in self.valuations:
            raise ValueError("unknown epistemic world")
        if isinstance(proposition, str):
            return proposition in self.valuations[world]
        return bool(proposition(world, self.valuations[world]))

    def knows(self, agent: str, world: Key, proposition: Predicate) -> bool:
        if agent not in self.accessibility or world not in self.valuations:
            raise ValueError("unknown epistemic agent or world")
        targets = self.accessibility[agent][world]
        return bool(targets) and all(
            self.satisfies(target, proposition) for target in targets
        )

    def common_knowledge(
        self, agents: Iterable[str], world: Key, proposition: Predicate
    ) -> bool:
        selected = tuple(agents)
        if not selected or any(agent not in self.accessibility for agent in selected):
            raise ValueError("common knowledge needs known agents")
        reached = {world}
        frontier = [world]
        while frontier:
            current = frontier.pop()
            for agent in selected:
                for target in self.accessibility[agent][current]:
                    if target not in reached:
                        reached.add(target)
                        frontier.append(target)
        return all(self.satisfies(target, proposition) for target in reached)

    def public_announcement(self, proposition: Predicate) -> "EpistemicModel":
        retained = tuple(
            world for world in self.worlds if self.satisfies(world, proposition)
        )
        if not retained:
            raise ValueError("public announcement eliminates every world")
        retained_set = set(retained)
        return EpistemicModel(
            retained,
            {world: self.valuations[world] for world in retained},
            {
                agent: {
                    world: targets & retained_set
                    for world, targets in relation.items()
                    if world in retained_set
                }
                for agent, relation in self.accessibility.items()
            },
        )


class RankedBeliefState:
    """Finite Grove-style ranking model for AGM revision and contraction."""

    def __init__(self, worlds: Sequence[Key], ranks: Mapping[Key, int]) -> None:
        self.worlds = tuple(worlds)
        if not self.worlds or len(set(self.worlds)) != len(self.worlds):
            raise ValueError("belief worlds must be non-empty and unique")
        if set(ranks) != set(self.worlds) or any(
            not isinstance(rank, int) or rank < 0 for rank in ranks.values()
        ):
            raise ValueError(
                "belief ranking must assign every world a non-negative rank"
            )
        minimum = min(ranks.values())
        self.ranks = {world: ranks[world] - minimum for world in self.worlds}

    @property
    def most_plausible(self) -> frozenset[Key]:
        return frozenset(world for world, rank in self.ranks.items() if rank == 0)

    def accepts(self, proposition: Callable[[Key], bool]) -> bool:
        return all(proposition(world) for world in self.most_plausible)

    def revise(self, proposition: Callable[[Key], bool]) -> "RankedBeliefState":
        satisfying = [world for world in self.worlds if proposition(world)]
        if not satisfying:
            raise ValueError(
                "AGM revision sentence is inconsistent with the finite language"
            )
        best = min(self.ranks[world] for world in satisfying)
        adjusted_satisfying = {world: self.ranks[world] - best for world in satisfying}
        gap = max(adjusted_satisfying.values()) + 1
        revised = {
            world: (
                adjusted_satisfying[world]
                if proposition(world)
                else self.ranks[world] + gap
            )
            for world in self.worlds
        }
        return RankedBeliefState(self.worlds, revised)

    def contract(self, proposition: Callable[[Key], bool]) -> "RankedBeliefState":
        if not self.accepts(proposition):
            return self
        countermodels = [world for world in self.worlds if not proposition(world)]
        if not countermodels:
            raise ValueError("a tautology cannot be contracted in this finite ranking")
        nearest_rank = min(self.ranks[world] for world in countermodels)
        promoted = {
            world for world in countermodels if self.ranks[world] == nearest_rank
        }
        ranks = dict(self.ranks)
        for world in promoted:
            ranks[world] = 0
        return RankedBeliefState(self.worlds, ranks)


@dataclass(frozen=True)
class QREOutcome:
    row_strategy: np.ndarray
    column_strategy: np.ndarray
    residual: float
    converged: bool
    iterations: int


def logit_qre(
    row_payoff: Sequence[Sequence[float]],
    column_payoff: Sequence[Sequence[float]],
    *,
    precision: float = 1.0,
    damping: float = 0.5,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> QREOutcome:
    """Solve a two-player logit QRE by damped fixed-point iteration."""
    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or row.shape != column.shape
        or row.size == 0
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or not 0.0 < damping <= 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("QRE game or solver configuration is invalid")
    p = np.full(row.shape[0], 1.0 / row.shape[0])
    q = np.full(row.shape[1], 1.0 / row.shape[1])
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        p_response = _softmax(row @ q, precision)
        q_response = _softmax(p @ column, precision)
        new_p = (1.0 - damping) * p + damping * p_response
        new_q = (1.0 - damping) * q + damping * q_response
        residual = max(
            float(np.max(np.abs(new_p - p))),
            float(np.max(np.abs(new_q - q))),
        )
        p, q = new_p, new_q
        if residual <= tolerance:
            return QREOutcome(p, q, residual, True, iteration)
    return QREOutcome(p, q, residual, False, max_iterations)


@dataclass(frozen=True)
class CognitiveHierarchyOutcome:
    level_weights: np.ndarray
    row_levels: tuple[np.ndarray, ...]
    column_levels: tuple[np.ndarray, ...]
    row_strategy: np.ndarray
    column_strategy: np.ndarray


def cognitive_hierarchy(
    row_payoff: Sequence[Sequence[float]],
    column_payoff: Sequence[Sequence[float]],
    *,
    mean_level: float = 1.5,
    maximum_level: int = 5,
    precision: float = 8.0,
) -> CognitiveHierarchyOutcome:
    """Finite Poisson cognitive hierarchy with logit level responses."""
    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or row.shape != column.shape
        or row.size == 0
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or mean_level < 0.0
        or not isfinite(mean_level)
        or maximum_level < 0
    ):
        raise ValueError("cognitive-hierarchy game or level model is invalid")
    raw_weights = np.asarray(
        [
            exp(-mean_level) * mean_level**level / factorial(level)
            for level in range(maximum_level + 1)
        ],
        dtype=np.float64,
    )
    weights = raw_weights / float(raw_weights.sum())
    row_levels = [np.full(row.shape[0], 1.0 / row.shape[0])]
    column_levels = [np.full(row.shape[1], 1.0 / row.shape[1])]
    for level in range(1, maximum_level + 1):
        lower = weights[:level].copy()
        lower /= float(lower.sum())
        believed_q = sum(lower[k] * column_levels[k] for k in range(level))
        believed_p = sum(lower[k] * row_levels[k] for k in range(level))
        row_levels.append(_softmax(row @ believed_q, precision))
        column_levels.append(_softmax(believed_p @ column, precision))
    aggregate_p = sum(
        weight * strategy for weight, strategy in zip(weights, row_levels)
    )
    aggregate_q = sum(
        weight * strategy for weight, strategy in zip(weights, column_levels)
    )
    return CognitiveHierarchyOutcome(
        weights,
        tuple(row_levels),
        tuple(column_levels),
        aggregate_p,
        aggregate_q,
    )


@dataclass(frozen=True)
class StructuralEquation:
    parents: tuple[str, ...]
    function: Callable[[Mapping[str, object], Mapping[str, object]], object]


class StructuralCausalModel:
    """A finite acyclic deterministic SCM with do-interventions."""

    def __init__(self, equations: Mapping[str, StructuralEquation]) -> None:
        if not equations:
            raise ValueError("SCM needs at least one endogenous equation")
        self.equations = dict(equations)
        visiting: set[str] = set()
        visited: set[str] = set()
        order: list[str] = []

        def visit(variable: str) -> None:
            if variable in visiting:
                raise ValueError("SCM endogenous graph must be acyclic")
            if variable in visited:
                return
            visiting.add(variable)
            for parent in self.equations[variable].parents:
                if parent in self.equations:
                    visit(parent)
            visiting.remove(variable)
            visited.add(variable)
            order.append(variable)

        for variable in self.equations:
            visit(variable)
        self.order = tuple(order)

    def simulate(
        self,
        exogenous: Mapping[str, object],
        interventions: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        interventions = dict(interventions or {})
        unknown = set(interventions) - set(self.equations)
        if unknown:
            raise ValueError("SCM intervention targets an unknown endogenous variable")
        values: dict[str, object] = {}
        for variable in self.order:
            if variable in interventions:
                values[variable] = interventions[variable]
                continue
            equation = self.equations[variable]
            missing = [
                parent
                for parent in equation.parents
                if parent not in values and parent not in exogenous
            ]
            if missing:
                raise ValueError(f"SCM exogenous parent is missing: {missing[0]}")
            parent_values = {
                parent: values[parent] if parent in values else exogenous[parent]
                for parent in equation.parents
            }
            values[variable] = equation.function(parent_values, exogenous)
        return values

    def counterfactual(
        self,
        exogenous: Mapping[str, object],
        interventions: Mapping[str, object],
    ) -> dict[str, object]:
        """Evaluate a counterfactual while holding the supplied exogenous unit fixed."""
        return self.simulate(exogenous, interventions)

    def average_treatment_effect(
        self,
        exogenous_samples: Sequence[Mapping[str, object]],
        *,
        treatment: str,
        control_value: object,
        treated_value: object,
        outcome: str,
    ) -> float:
        if not exogenous_samples or outcome not in self.equations:
            raise ValueError("SCM ATE needs samples and a known outcome")
        effects = []
        for sample in exogenous_samples:
            control = self.simulate(sample, {treatment: control_value})
            treated = self.simulate(sample, {treatment: treated_value})
            effects.append(float(treated[outcome]) - float(control[outcome]))
        if any(not isfinite(effect) for effect in effects):
            raise ValueError("SCM treatment effects must be finite")
        return float(np.mean(effects))


@dataclass(frozen=True)
class InformationValueResult:
    baseline_value: float
    informed_value: float
    value_of_information: float


def expected_value_of_perfect_information(
    state_probabilities: Mapping[Key, float],
    action_utilities: Mapping[Key, Mapping[Key, float]],
) -> InformationValueResult:
    states = tuple(state_probabilities)
    probabilities = _probability_vector(
        [state_probabilities[state] for state in states], "state prior"
    )
    if not action_utilities:
        raise ValueError("VOI needs at least one action")
    matrix = np.asarray(
        [
            [float(action_utilities[action][state]) for state in states]
            for action in action_utilities
        ],
        dtype=np.float64,
    )
    if np.any(~np.isfinite(matrix)):
        raise ValueError("VOI utilities must be finite")
    baseline = float(np.max(matrix @ probabilities))
    informed = float(probabilities @ np.max(matrix, axis=0))
    return InformationValueResult(baseline, informed, informed - baseline)


def expected_value_of_sample_information(
    state_probabilities: Mapping[Key, float],
    action_utilities: Mapping[Key, Mapping[Key, float]],
    observation_likelihoods: Mapping[Key, Mapping[Key, float]],
) -> InformationValueResult:
    states = tuple(state_probabilities)
    probabilities = _probability_vector(
        [state_probabilities[state] for state in states], "state prior"
    )
    actions = tuple(action_utilities)
    if not actions or not observation_likelihoods:
        raise ValueError("EVSI needs actions and possible observations")
    utility = np.asarray(
        [
            [float(action_utilities[action][state]) for state in states]
            for action in actions
        ],
        dtype=np.float64,
    )
    likelihood = np.asarray(
        [
            [float(observation_likelihoods[observation][state]) for state in states]
            for observation in observation_likelihoods
        ],
        dtype=np.float64,
    )
    if (
        np.any(~np.isfinite(utility))
        or np.any(~np.isfinite(likelihood))
        or np.any(likelihood < 0.0)
        or not np.allclose(likelihood.sum(axis=0), 1.0, atol=1e-9)
    ):
        raise ValueError("EVSI likelihoods must define a conditional distribution")
    baseline = float(np.max(utility @ probabilities))
    informed = 0.0
    for row in likelihood:
        joint = probabilities * row
        observation_probability = float(joint.sum())
        if observation_probability <= 0.0:
            continue
        posterior = joint / observation_probability
        informed += observation_probability * float(np.max(utility @ posterior))
    return InformationValueResult(baseline, informed, informed - baseline)
