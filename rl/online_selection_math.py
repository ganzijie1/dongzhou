"""Submodular selection, online change detection, bandits, and temporal logic."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, sqrt
from typing import Callable, Hashable, Mapping, Sequence


Item = Hashable
Arm = Hashable


@dataclass(frozen=True)
class SubmodularResult:
    selected: tuple[Item, ...]
    value: float
    marginal_gains: tuple[float, ...]
    approximation_bound: float


def greedy_submodular_maximize(
    items: Sequence[Item],
    value: Callable[[frozenset[Item]], float],
    *,
    cardinality: int,
    tolerance: float = 1e-12,
) -> SubmodularResult:
    """Greedy monotone submodular maximization under a cardinality constraint."""

    candidates = tuple(dict.fromkeys(items))
    if cardinality < 0:
        raise ValueError("submodular cardinality must be non-negative")
    selected: set[Item] = set()
    current = float(value(frozenset()))
    if not isfinite(current):
        raise ValueError("submodular values must be finite")
    gains = []
    order = []
    for _ in range(min(cardinality, len(candidates))):
        ranked = []
        for item in candidates:
            if item in selected:
                continue
            updated = float(value(frozenset(selected | {item})))
            if not isfinite(updated):
                raise ValueError("submodular values must be finite")
            ranked.append((updated - current, item, updated))
        if not ranked:
            break
        gain, item, updated = max(ranked, key=lambda entry: entry[0])
        if gain < -tolerance:
            raise ValueError("greedy guarantee requires a monotone objective")
        if gain <= tolerance:
            break
        selected.add(item)
        order.append(item)
        gains.append(gain)
        current = updated
    return SubmodularResult(tuple(order), current, tuple(gains), 1.0 - 1.0 / 2.718281828459045)


def weighted_coverage_value(
    selected: frozenset[Item],
    coverage: Mapping[Item, Mapping[Hashable, float]],
    weights: Mapping[Hashable, float] | None = None,
) -> float:
    """Independent-detection coverage, a monotone submodular objective."""

    targets = {target for item in selected for target in coverage.get(item, {})}
    total = 0.0
    for target in targets:
        miss = 1.0
        for item in selected:
            probability = float(coverage.get(item, {}).get(target, 0.0))
            if not 0.0 <= probability <= 1.0:
                raise ValueError("coverage probabilities must be in [0, 1]")
            miss *= 1.0 - probability
        weight = float((weights or {}).get(target, 1.0))
        if not isfinite(weight) or weight < 0.0:
            raise ValueError("coverage weights must be finite and non-negative")
        total += weight * (1.0 - miss)
    return total


@dataclass(frozen=True)
class ChangePointStatus:
    changed: bool
    direction: str | None
    positive_score: float
    negative_score: float


class CUSUMChangeDetector:
    """Two-sided online CUSUM detector around a fixed reference level."""

    def __init__(
        self,
        reference: float,
        *,
        drift: float,
        threshold: float,
        reset_on_change: bool = True,
    ) -> None:
        if not all(isfinite(value) for value in (reference, drift, threshold)):
            raise ValueError("CUSUM parameters must be finite")
        if drift < 0.0 or threshold <= 0.0:
            raise ValueError("CUSUM drift must be non-negative and threshold positive")
        self.reference = float(reference)
        self.drift = float(drift)
        self.threshold = float(threshold)
        self.reset_on_change = bool(reset_on_change)
        self.positive = 0.0
        self.negative = 0.0

    def reset(self) -> None:
        self.positive = 0.0
        self.negative = 0.0

    def update(self, observation: float) -> ChangePointStatus:
        value = float(observation)
        if not isfinite(value):
            raise ValueError("CUSUM observation must be finite")
        centered = value - self.reference
        self.positive = max(0.0, self.positive + centered - self.drift)
        self.negative = max(0.0, self.negative - centered - self.drift)
        direction = None
        if self.positive >= self.threshold:
            direction = "increase"
        elif self.negative >= self.threshold:
            direction = "decrease"
        status = ChangePointStatus(
            direction is not None,
            direction,
            self.positive,
            self.negative,
        )
        if status.changed and self.reset_on_change:
            self.reset()
        return status


class UCB1Bandit:
    """Deterministic UCB1 strategy selector with incremental reward means."""

    def __init__(self, arms: Sequence[Arm], *, exploration: float = 2.0) -> None:
        self.arms = tuple(dict.fromkeys(arms))
        if not self.arms or not isfinite(exploration) or exploration < 0.0:
            raise ValueError("UCB1 needs arms and non-negative exploration")
        self.exploration = float(exploration)
        self.counts = {arm: 0 for arm in self.arms}
        self.means = {arm: 0.0 for arm in self.arms}

    def select(self) -> Arm:
        for arm in self.arms:
            if self.counts[arm] == 0:
                return arm
        total = sum(self.counts.values())
        return max(
            self.arms,
            key=lambda arm: (
                self.means[arm]
                + sqrt(self.exploration * log(total) / self.counts[arm]),
                repr(arm),
            ),
        )

    def update(self, arm: Arm, reward: float) -> None:
        if arm not in self.counts:
            raise ValueError(f"unknown bandit arm: {arm!r}")
        value = float(reward)
        if not isfinite(value):
            raise ValueError("bandit reward must be finite")
        count = self.counts[arm] + 1
        self.means[arm] += (value - self.means[arm]) / count
        self.counts[arm] = count


def stl_always(values: Sequence[float], start: int = 0, end: int | None = None) -> float:
    window = tuple(float(value) for value in values[start:end])
    if not window or any(not isfinite(value) for value in window):
        raise ValueError("STL always needs a finite non-empty window")
    return min(window)


def stl_eventually(values: Sequence[float], start: int = 0, end: int | None = None) -> float:
    window = tuple(float(value) for value in values[start:end])
    if not window or any(not isfinite(value) for value in window):
        raise ValueError("STL eventually needs a finite non-empty window")
    return max(window)


def stl_until(
    left: Sequence[float],
    right: Sequence[float],
    start: int = 0,
    end: int | None = None,
) -> float:
    """Robust bounded-until semantics: max_t min(right[t], min_{k<=t} left[k])."""

    stop = len(left) if end is None else int(end)
    if len(left) != len(right) or not 0 <= start < stop <= len(left):
        raise ValueError("STL until traces or interval are invalid")
    prefix = float("inf")
    robustness = -float("inf")
    for index in range(start, stop):
        lhs = float(left[index])
        rhs = float(right[index])
        if not isfinite(lhs) or not isfinite(rhs):
            raise ValueError("STL traces must be finite")
        prefix = min(prefix, lhs)
        robustness = max(robustness, min(prefix, rhs))
    return robustness


@dataclass(frozen=True)
class TemporalRequirement:
    operator: str
    start: int = 0
    end: int | None = None

    def robustness(
        self,
        primary: Sequence[float],
        secondary: Sequence[float] | None = None,
    ) -> float:
        if self.operator == "always":
            return stl_always(primary, self.start, self.end)
        if self.operator == "eventually":
            return stl_eventually(primary, self.start, self.end)
        if self.operator == "until" and secondary is not None:
            return stl_until(primary, secondary, self.start, self.end)
        raise ValueError("unknown or incomplete temporal requirement")

    def satisfied(
        self,
        primary: Sequence[float],
        secondary: Sequence[float] | None = None,
    ) -> bool:
        return self.robustness(primary, secondary) >= 0.0
