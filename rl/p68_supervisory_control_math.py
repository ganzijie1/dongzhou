"""P68 finite-language Ramadge-Wonham supervisory control."""

from __future__ import annotations

from typing import Hashable, Iterable


Trace = tuple[Hashable, ...]


def prefix_closure(language: Iterable[Trace]) -> frozenset[Trace]:
    closure: set[Trace] = {()}
    for trace in language:
        trace = tuple(trace)
        closure.update(trace[:length] for length in range(len(trace) + 1))
    return frozenset(closure)


def natural_projection(trace: Trace, observable_events: set[Hashable]) -> Trace:
    return tuple(event for event in trace if event in observable_events)


def is_controllable(specification: Iterable[Trace], plant: Iterable[Trace], uncontrollable_events: set[Hashable]) -> bool:
    candidate = prefix_closure(specification)
    plant_closure = prefix_closure(plant)
    return all(trace + (event,) not in plant_closure or trace + (event,) in candidate for trace in candidate for event in uncontrollable_events)


def supremal_controllable_sublanguage(specification: Iterable[Trace], plant: Iterable[Trace], uncontrollable_events: set[Hashable]) -> frozenset[Trace]:
    candidate = set(prefix_closure(specification))
    plant_closure = prefix_closure(plant)
    while True:
        bad = {trace for trace in candidate if any(trace + (event,) in plant_closure and trace + (event,) not in candidate for event in uncontrollable_events)}
        if not bad:
            return frozenset(candidate)
        candidate = {trace for trace in candidate if not any(trace[:len(prefix)] == prefix for prefix in bad)}


def is_observable(specification: Iterable[Trace], plant: Iterable[Trace], controllable_events: set[Hashable], observable_events: set[Hashable]) -> bool:
    candidate = prefix_closure(specification)
    plant_closure = prefix_closure(plant)
    groups: dict[Trace, list[Trace]] = {}
    for trace in plant_closure:
        groups.setdefault(natural_projection(trace, observable_events), []).append(trace)
    for traces in groups.values():
        for left in traces:
            for right in traces:
                for event in controllable_events:
                    if left in candidate and left + (event,) in candidate and right in candidate and right + (event,) in plant_closure and right + (event,) not in candidate:
                        return False
    return True


def supervisor_enabled_events(trace: Trace, plant: Iterable[Trace], controlled_language: Iterable[Trace], uncontrollable_events: set[Hashable]) -> frozenset[Hashable]:
    plant_closure = prefix_closure(plant)
    candidate = prefix_closure(controlled_language)
    possible = {word[len(trace)] for word in plant_closure if len(word) == len(trace) + 1 and word[:len(trace)] == trace}
    return frozenset(event for event in possible if event in uncontrollable_events or trace + (event,) in candidate)
