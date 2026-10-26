"""P57 timed-automaton traces, Petri nets, and stochastic transition races."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class TimedEdge:
    source: str
    target: str
    label: str
    lower_bounds: Mapping[str, float]
    upper_bounds: Mapping[str, float]
    resets: tuple[str, ...] = ()


@dataclass(frozen=True)
class TimedTraceResult:
    location: str
    clocks: dict[str, float]


def run_timed_trace(
    initial_location: str,
    clock_names: Sequence[str],
    invariants: Mapping[str, Mapping[str, float]],
    edges: Sequence[TimedEdge],
    timed_actions: Sequence[tuple[float, str]],
) -> TimedTraceResult:
    names = tuple(clock_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("clock names must be unique")
    clocks = {name: 0.0 for name in names}
    location = initial_location
    for delay, label in timed_actions:
        if not isfinite(delay) or delay < 0.0:
            raise ValueError("delays must be finite and non-negative")
        advanced = {name: value + delay for name, value in clocks.items()}
        for name, upper in invariants.get(location, {}).items():
            if name not in clocks or advanced[name] > upper + 1e-12:
                raise ValueError("location invariant was violated")
        candidates = []
        for edge in edges:
            if edge.source != location or edge.label != label:
                continue
            lower_ok = all(advanced.get(name, float("-inf")) >= bound - 1e-12 for name, bound in edge.lower_bounds.items())
            upper_ok = all(advanced.get(name, float("inf")) <= bound + 1e-12 for name, bound in edge.upper_bounds.items())
            if lower_ok and upper_ok:
                candidates.append(edge)
        if len(candidates) != 1:
            raise ValueError("timed action must select exactly one enabled edge")
        edge = candidates[0]
        if any(name not in clocks for name in edge.resets):
            raise ValueError("edge resets an unknown clock")
        clocks = advanced
        for name in edge.resets:
            clocks[name] = 0.0
        location = edge.target
        for name, upper in invariants.get(location, {}).items():
            if name not in clocks or clocks[name] > upper + 1e-12:
                raise ValueError("target invariant was violated")
    return TimedTraceResult(location, clocks)


@dataclass(frozen=True)
class PetriNet:
    pre: np.ndarray
    post: np.ndarray

    @classmethod
    def create(cls, pre: Sequence, post: Sequence) -> "PetriNet":
        inputs = np.asarray(pre)
        outputs = np.asarray(post)
        if inputs.ndim != 2 or inputs.shape[0] == 0 or inputs.shape[1] == 0 or outputs.shape != inputs.shape or np.any(inputs != np.floor(inputs)) or np.any(outputs != np.floor(outputs)) or np.any(inputs < 0) or np.any(outputs < 0):
            raise ValueError("Petri incidence matrices are invalid")
        return cls(inputs.astype(int), outputs.astype(int))

    @property
    def incidence(self) -> np.ndarray:
        return self.post - self.pre

    def enabled(self, marking: Sequence[int]) -> np.ndarray:
        value = np.asarray(marking)
        if value.shape != (self.pre.shape[0],) or np.any(value != np.floor(value)) or np.any(value < 0):
            raise ValueError("marking is invalid")
        return np.all(value[:, None] >= self.pre, axis=0)

    def fire(self, marking: Sequence[int], transition: int) -> np.ndarray:
        value = np.asarray(marking, dtype=int)
        enabled = self.enabled(value)
        if transition < 0 or transition >= self.pre.shape[1] or not enabled[transition]:
            raise ValueError("transition is not enabled")
        return value + self.incidence[:, transition]

    def reachable_markings(self, initial: Sequence[int], *, max_markings: int = 10_000) -> tuple[tuple[int, ...], ...]:
        start = tuple(np.asarray(initial, dtype=int).tolist())
        self.enabled(start)
        discovered = {start}
        queue = deque([start])
        while queue:
            marking = np.asarray(queue.popleft(), dtype=int)
            for transition in np.flatnonzero(self.enabled(marking)):
                following = tuple(self.fire(marking, int(transition)).tolist())
                if following not in discovered:
                    if len(discovered) >= max_markings:
                        raise RuntimeError("Petri reachability exceeded max_markings")
                    discovered.add(following)
                    queue.append(following)
        return tuple(sorted(discovered))

    def deadlocks(self, initial: Sequence[int], *, terminal_markings: Sequence[Sequence[int]] = ()) -> tuple[tuple[int, ...], ...]:
        terminal = {tuple(np.asarray(marking, dtype=int).tolist()) for marking in terminal_markings}
        return tuple(marking for marking in self.reachable_markings(initial) if marking not in terminal and not np.any(self.enabled(marking)))


def p_invariant_residual(net: PetriNet, weights: Sequence[float]) -> np.ndarray:
    vector = np.asarray(weights, dtype=np.float64)
    if vector.shape != (net.pre.shape[0],) or np.any(~np.isfinite(vector)):
        raise ValueError("P-invariant weights are invalid")
    return vector @ net.incidence


def timed_transition_available(age: float, interval: tuple[float, float]) -> bool:
    lower, upper = interval
    if not isfinite(age) or age < 0.0 or not isfinite(lower) or lower < 0.0 or upper < lower:
        raise ValueError("timed-transition inputs are invalid")
    return lower <= age <= upper


def stochastic_race(rates: Sequence[float], rng: np.random.Generator) -> tuple[float, int]:
    values = np.asarray(rates, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or np.any(values < 0.0) or values.sum() <= 0.0:
        raise ValueError("stochastic race rates are invalid")
    total = float(values.sum())
    wait = float(rng.exponential(1.0 / total))
    transition = int(rng.choice(values.size, p=values / total))
    return wait, transition
