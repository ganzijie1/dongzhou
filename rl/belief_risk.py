"""Bayesian grid beliefs and risk measures for partially observed tactics."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log
from typing import Iterable, Mapping, Sequence


Cell = tuple[int, int]


def _normalized(values: Mapping[Cell, float]) -> dict[Cell, float]:
    cleaned = {
        (int(cell[0]), int(cell[1])): float(value)
        for cell, value in values.items()
        if isfinite(float(value)) and float(value) > 0.0
    }
    total = sum(cleaned.values())
    if total <= 0.0:
        raise ValueError("belief distribution must contain positive finite mass")
    return {cell: value / total for cell, value in cleaned.items()}


@dataclass(frozen=True)
class DiscreteBelief:
    """A normalized probability distribution over lattice cells."""

    probabilities: Mapping[Cell, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "probabilities", _normalized(self.probabilities))

    @classmethod
    def observed(cls, cell: Cell) -> "DiscreteBelief":
        return cls({cell: 1.0})

    def predict(
        self,
        adjacency: Mapping[Cell, Sequence[Cell]],
        *,
        stay_probability: float = 0.25,
    ) -> "DiscreteBelief":
        if not 0.0 <= stay_probability <= 1.0:
            raise ValueError("stay_probability must be in [0, 1]")
        predicted: dict[Cell, float] = {}
        for cell, mass in self.probabilities.items():
            neighbors = tuple(dict.fromkeys(adjacency.get(cell, ())))
            if not neighbors:
                predicted[cell] = predicted.get(cell, 0.0) + mass
                continue
            predicted[cell] = predicted.get(cell, 0.0) + mass * stay_probability
            moving = mass * (1.0 - stay_probability) / len(neighbors)
            for neighbor in neighbors:
                predicted[neighbor] = predicted.get(neighbor, 0.0) + moving
        return DiscreteBelief(predicted)

    def condition(self, likelihood: Mapping[Cell, float]) -> "DiscreteBelief":
        posterior = {
            cell: mass * max(0.0, float(likelihood.get(cell, 0.0)))
            for cell, mass in self.probabilities.items()
        }
        return DiscreteBelief(posterior)

    def exclude(self, impossible: Iterable[Cell]) -> "DiscreteBelief":
        blocked = set(impossible)
        remaining = {
            cell: mass
            for cell, mass in self.probabilities.items()
            if cell not in blocked
        }
        if not remaining:
            return self
        return DiscreteBelief(remaining)


class BayesianGridTracker:
    """Track hidden units with prediction and positive/negative observations."""

    def __init__(self) -> None:
        self.beliefs: dict[int, DiscreteBelief] = {}

    def reset(self) -> None:
        self.beliefs.clear()

    def remove(self, unit_id: int) -> None:
        self.beliefs.pop(int(unit_id), None)

    def observe(self, unit_id: int, cell: Cell) -> None:
        self.beliefs[int(unit_id)] = DiscreteBelief.observed(cell)

    def predict(
        self,
        adjacency: Mapping[Cell, Sequence[Cell]],
        *,
        unit_ids: Iterable[int] | None = None,
        stay_probability: float = 0.25,
    ) -> None:
        selected = set(self.beliefs) if unit_ids is None else {int(v) for v in unit_ids}
        for unit_id in selected & self.beliefs.keys():
            self.beliefs[unit_id] = self.beliefs[unit_id].predict(
                adjacency, stay_probability=stay_probability
            )

    def update(
        self,
        observations: Mapping[int, Cell],
        *,
        visible_cells: Iterable[Cell] = (),
        alive_ids: Iterable[int] | None = None,
    ) -> None:
        if alive_ids is not None:
            alive = {int(value) for value in alive_ids}
            for unit_id in tuple(self.beliefs):
                if unit_id not in alive:
                    del self.beliefs[unit_id]
        observed_ids = {int(unit_id) for unit_id in observations}
        negative = set(visible_cells)
        for unit_id in self.beliefs.keys() - observed_ids:
            self.beliefs[unit_id] = self.beliefs[unit_id].exclude(negative)
        for unit_id, cell in observations.items():
            self.observe(int(unit_id), cell)

    def occupancy(self, unit_ids: Iterable[int] | None = None) -> dict[Cell, float]:
        selected = set(self.beliefs) if unit_ids is None else {int(v) for v in unit_ids}
        result: dict[Cell, float] = {}
        for unit_id in selected:
            belief = self.beliefs.get(unit_id)
            if belief is None:
                continue
            for cell, mass in belief.probabilities.items():
                result[cell] = result.get(cell, 0.0) + mass
        return result


def conditional_value_at_risk(
    losses: Sequence[float],
    alpha: float = 0.9,
    probabilities: Sequence[float] | None = None,
) -> float:
    """Return upper-tail CVaR, including fractional mass at the quantile."""

    if not losses:
        raise ValueError("CVaR needs at least one loss")
    if not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must be in [0, 1)")
    values = [float(value) for value in losses]
    if not all(isfinite(value) for value in values):
        raise ValueError("losses must be finite")
    if probabilities is None:
        weights = [1.0 / len(values)] * len(values)
    else:
        if len(probabilities) != len(values):
            raise ValueError("losses and probabilities must have equal length")
        weights = [float(value) for value in probabilities]
        if any(not isfinite(value) or value < 0.0 for value in weights):
            raise ValueError("probabilities must be finite and non-negative")
        total = sum(weights)
        if total <= 0.0:
            raise ValueError("probabilities must contain positive mass")
        weights = [value / total for value in weights]
    tail_mass = 1.0 - alpha
    remaining = tail_mass
    weighted_loss = 0.0
    for loss, probability in sorted(zip(values, weights), reverse=True):
        taken = min(remaining, probability)
        weighted_loss += loss * taken
        remaining -= taken
        if remaining <= 1e-15:
            break
    return weighted_loss / tail_mass


def entropic_risk(
    losses: Sequence[float],
    risk_aversion: float,
    probabilities: Sequence[float] | None = None,
) -> float:
    """Return log E[exp(theta L)] / theta with a stable log-sum-exp."""

    if not losses:
        raise ValueError("entropic risk needs at least one loss")
    theta = float(risk_aversion)
    if not isfinite(theta) or theta < 0.0:
        raise ValueError("risk_aversion must be finite and non-negative")
    values = [float(value) for value in losses]
    if probabilities is None:
        weights = [1.0 / len(values)] * len(values)
    else:
        if len(probabilities) != len(values):
            raise ValueError("losses and probabilities must have equal length")
        total = sum(float(value) for value in probabilities)
        if total <= 0.0:
            raise ValueError("probabilities must contain positive mass")
        weights = [float(value) / total for value in probabilities]
    if theta == 0.0:
        return sum(weight * loss for weight, loss in zip(weights, values))
    scaled = [theta * loss for loss in values]
    maximum = max(scaled)
    return (maximum + log(sum(w * exp(v - maximum) for w, v in zip(weights, scaled)))) / theta


def bernoulli_loss_distribution(
    events: Sequence[tuple[float, float]],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Convolve independent ``(probability, loss)`` events exactly."""

    distribution: dict[float, float] = {0.0: 1.0}
    for probability, loss in events:
        chance = float(probability)
        amount = float(loss)
        if not 0.0 <= chance <= 1.0 or not isfinite(amount):
            raise ValueError("event probability/loss is invalid")
        updated: dict[float, float] = {}
        for current, mass in distribution.items():
            updated[current] = updated.get(current, 0.0) + mass * (1.0 - chance)
            hit = round(current + amount, 12)
            updated[hit] = updated.get(hit, 0.0) + mass * chance
        distribution = updated
    ordered = sorted(distribution.items())
    return (
        tuple(value for value, _ in ordered),
        tuple(probability for _, probability in ordered),
    )

