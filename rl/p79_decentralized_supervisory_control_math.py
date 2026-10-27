"""P79 decentralized supervisory control, diagnosis, and opacity checks.

The routines operate on finite trace languages. They support replay analysis
and bounded-horizon audits rather than unbounded automata proofs.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from rl.p68_supervisory_control_math import natural_projection, prefix_closure


Trace = tuple[Hashable, ...]


@dataclass(frozen=True)
class CoobservabilityViolation:
    """A plant transition that no local supervisor can safely disable."""

    trace: Trace
    event: Hashable


@dataclass(frozen=True)
class OpacityResult:
    """Current-state opacity result and observations that reveal a secret."""

    opaque: bool
    leaking_observations: frozenset[Trace]


def coobservability_violations(
    specification: Iterable[Trace],
    plant: Iterable[Trace],
    local_observable_events: Sequence[set[Hashable]],
    local_controllable_events: Sequence[set[Hashable]],
) -> tuple[CoobservabilityViolation, ...]:
    """Audit conjunctive coobservability for a finite prefix-closed language."""

    if len(local_observable_events) != len(local_controllable_events):
        raise ValueError("each supervisor needs observable and controllable alphabets")
    if not local_observable_events:
        raise ValueError("at least one local supervisor is required")

    candidate = prefix_closure(specification)
    plant_closure = prefix_closure(plant)
    controllable = set().union(*local_controllable_events)
    violations: list[CoobservabilityViolation] = []

    for trace in candidate:
        for event in controllable:
            extension = trace + (event,)
            if extension not in plant_closure or extension in candidate:
                continue
            safely_disabled = False
            for observable, controlled in zip(
                local_observable_events, local_controllable_events, strict=True
            ):
                if event not in controlled:
                    continue
                observation = natural_projection(trace, observable)
                indistinguishable = (
                    word
                    for word in candidate
                    if natural_projection(word, observable) == observation
                )
                if all(word + (event,) not in candidate for word in indistinguishable):
                    safely_disabled = True
                    break
            if not safely_disabled:
                violations.append(CoobservabilityViolation(trace, event))
    return tuple(violations)


def is_coobservable(
    specification: Iterable[Trace],
    plant: Iterable[Trace],
    local_observable_events: Sequence[set[Hashable]],
    local_controllable_events: Sequence[set[Hashable]],
) -> bool:
    """Return whether the finite language passes the coobservability audit."""

    return not coobservability_violations(
        specification,
        plant,
        local_observable_events,
        local_controllable_events,
    )


def fuse_local_decisions(
    local_decisions: Sequence[Mapping[Hashable, bool]],
    *,
    architecture: str = "conjunctive",
) -> dict[Hashable, bool]:
    """Fuse explicit local votes, ignoring missing non-authoritative votes."""

    if architecture not in {"conjunctive", "disjunctive"}:
        raise ValueError("architecture must be 'conjunctive' or 'disjunctive'")
    events = set().union(*(decision.keys() for decision in local_decisions))
    fused: dict[Hashable, bool] = {}
    for event in events:
        votes = [decision[event] for decision in local_decisions if event in decision]
        fused[event] = all(votes) if architecture == "conjunctive" else any(votes)
    return fused


def diagnosis_classes(
    language: Iterable[Trace],
    observable_events: set[Hashable],
    fault_event: Hashable,
) -> dict[Trace, frozenset[bool]]:
    """Group normal/faulty hypotheses by natural projection."""

    classes: dict[Trace, set[bool]] = {}
    for trace in prefix_closure(language):
        observation = natural_projection(trace, observable_events)
        classes.setdefault(observation, set()).add(fault_event in trace)
    return {key: frozenset(statuses) for key, statuses in classes.items()}


def is_diagnosable(
    language: Iterable[Trace],
    observable_events: set[Hashable],
    fault_event: Hashable,
) -> bool:
    """Check bounded-horizon diagnosability of every observation class."""

    classes = diagnosis_classes(language, observable_events, fault_event)
    return all(len(statuses) == 1 for statuses in classes.values())


def is_codiagnosable(
    language: Iterable[Trace],
    local_observable_events: Sequence[set[Hashable]],
    fault_event: Hashable,
) -> bool:
    """Check whether some local observer diagnoses every faulty trace."""

    if not local_observable_events:
        raise ValueError("at least one local observer is required")
    traces = prefix_closure(language)
    normal = tuple(trace for trace in traces if fault_event not in trace)
    faulty = tuple(trace for trace in traces if fault_event in trace)
    return all(
        any(
            all(
                natural_projection(trace, observable)
                != natural_projection(other, observable)
                for other in normal
            )
            for observable in local_observable_events
        )
        for trace in faulty
    )


def current_state_opacity(
    final_states: Mapping[Trace, Hashable],
    secret_states: set[Hashable],
    observable_events: set[Hashable],
) -> OpacityResult:
    """Check whether every secret-ending trace has a non-secret lookalike."""

    observations: dict[Trace, set[bool]] = {}
    for trace, state in final_states.items():
        projected = natural_projection(tuple(trace), observable_events)
        observations.setdefault(projected, set()).add(state in secret_states)
    leaking = frozenset(
        observation
        for observation, statuses in observations.items()
        if statuses == {True}
    )
    return OpacityResult(not leaking, leaking)
