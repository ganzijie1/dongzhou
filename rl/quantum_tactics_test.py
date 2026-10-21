"""Invariant, interference, replay, and planner tests for quantum tactics."""

from __future__ import annotations

from math import isclose, pi, sqrt

import numpy as np

from rl.joint_turn_planner import JointTurnPlanner
from rl.quantum_tactics import (
    QuantumState,
    QuantumStateError,
    QuantumTacticalSystem,
    lattice_hamiltonian,
    tunneling_probability,
)
from rl.runtime_policy import RuntimeBattlePolicy


def _unit(unit_id: int, x: int, y: int) -> dict:
    return {
        "id": unit_id,
        "force": 4,
        "class": "Infantry",
        "x": x,
        "y": y,
        "attack_offsets": ((0, -1), (0, 1), (-1, 0), (1, 0)),
        "attack_min": 1,
        "attack_max": 1,
        "move": 5,
        "hp": 100,
        "max_hp": 100,
        "atk": 100,
        "done": False,
        "dead": False,
    }


def _action(index: int, x: int, y: int) -> dict:
    return {
        "index": index,
        "unit": 1,
        "type": 1,
        "x": x,
        "y": y,
        "target": None,
        "damage": 0,
    }


def test_born_probabilities_normalize_amplitudes() -> None:
    state = QuantumState.from_amplitudes(
        {(0, 0): 3.0 + 0.0j, (1, 0): 0.0 + 4.0j}
    )
    probabilities = state.probabilities()
    assert isclose(probabilities[(0, 0)], 9.0 / 25.0)
    assert isclose(probabilities[(1, 0)], 16.0 / 25.0)
    assert isclose(sum(probabilities.values()), 1.0)
    assert isclose(state.purity, 1.0)


def test_phase_changes_interference_but_not_immediate_probabilities() -> None:
    amplitudes = {(0, 0): 1.0 / sqrt(2), (1, 0): 1.0 / sqrt(2)}
    constructive = QuantumState.from_amplitudes(amplitudes)
    destructive = QuantumState.from_amplitudes(amplitudes)
    destructive.phase_shift({(1, 0): pi})
    assert constructive.probabilities() == destructive.probabilities()

    beam_splitter = np.asarray([[1.0, 1.0], [1.0, -1.0]]) / sqrt(2)
    constructive.apply_unitary(beam_splitter)
    destructive.apply_unitary(beam_splitter)
    assert constructive.probabilities()[(0, 0)] > 1.0 - 1e-9
    assert destructive.probabilities()[(1, 0)] > 1.0 - 1e-9


def test_dephasing_preserves_position_distribution_and_reduces_coherence() -> None:
    state = QuantumState.from_amplitudes({(0, 0): 1.0, (1, 0): 1.0j})
    before = state.probabilities()
    coherence = state.coherence
    state.dephase(0.75)
    assert state.probabilities() == before
    assert isclose(state.coherence, coherence * 0.25)
    assert state.purity < 1.0


def test_kraus_channel_preserves_trace_and_applies_amplitude_damping() -> None:
    state = QuantumState.from_amplitudes({(0, 0): 0.0, (1, 0): 1.0})
    probability = 0.3
    keep = np.asarray([[1.0, 0.0], [0.0, sqrt(1.0 - probability)]])
    decay = np.asarray([[0.0, sqrt(probability)], [0.0, 0.0]])
    state.apply_channel((keep, decay))
    measured = state.probabilities()
    assert isclose(measured[(0, 0)], probability)
    assert isclose(measured[(1, 0)], 1.0 - probability)
    assert isclose(float(np.trace(state.density).real), 1.0)


def test_lattice_evolution_preserves_density_invariants() -> None:
    cells = ((0, 0), (1, 0), (2, 0))
    state = QuantumState.localized((0, 0))
    expanded = QuantumState(
        cells,
        np.diag(np.asarray([1.0, 0.0, 0.0], dtype=np.complex128)),
    )
    hamiltonian = lattice_hamiltonian(
        cells,
        coupling=0.8,
        potentials={(1, 0): 2.0},
    )
    expanded.evolve(hamiltonian, 0.5)
    assert isclose(float(np.trace(expanded.density).real), 1.0)
    assert float(np.linalg.eigvalsh(expanded.density).min()) >= -1e-9
    assert expanded.probabilities()[(1, 0)] > 0.0
    assert state.probabilities() == {(0, 0): 1.0}


def test_seeded_measurement_is_reproducible_and_collapses() -> None:
    left = QuantumTacticalSystem(seed=2026)
    right = QuantumTacticalSystem(seed=2026)
    amplitudes = {(0, 0): 1.0, (1, 0): 2.0}
    left.prepare(7, amplitudes)
    right.prepare(7, amplitudes)
    assert left.observe(7) == right.observe(7)
    assert left.state(7).purity == 1.0
    assert max(left.state(7).probabilities().values()) == 1.0
    assert left.events[-1].roll == right.events[-1].roll


def test_legal_projection_rejects_impossible_classical_resolution() -> None:
    state = QuantumState.from_amplitudes({(0, 0): 1.0, (1, 0): 1.0})
    retained = state.condition_on({(1, 0)})
    assert isclose(retained, 0.5)
    assert state.probabilities()[(1, 0)] == 1.0
    try:
        state.condition_on({(9, 9)})
    except QuantumStateError:
        pass
    else:
        raise AssertionError("zero-probability legal projection must fail")


def test_tunneling_probability_has_expected_limits() -> None:
    thin = tunneling_probability(4.0, 1.0, 0.25)
    thick = tunneling_probability(4.0, 1.0, 1.0)
    assert 0.0 < thick < thin < 1.0
    assert tunneling_probability(1.0, 2.0, 100.0) == 1.0


def test_quantum_priors_select_high_probability_legal_destination() -> None:
    system = QuantumTacticalSystem(seed=11)
    system.prepare(1, {(1, 0): 1.0, (0, 1): 3.0})
    actions = [_action(0, 1, 0), _action(1, 0, 1)]
    priors = system.action_priors(actions)
    assert priors[1] > priors[0]
    chosen = JointTurnPlanner().choose(
        actions,
        [_unit(1, 0, 0)],
        3,
        3,
        movement_costs={1: [1] * 9},
        quantum_priors=priors,
    )
    assert chosen.action_index == 1
    assert chosen.reason == "quantum-prior"


class _QuantumEnv:
    max_units = 8

    def __init__(self, system: QuantumTacticalSystem) -> None:
        self.system = system

    def unit_info(self) -> list[dict]:
        return [_unit(1, 0, 0)]

    @staticmethod
    def map_info() -> dict:
        return {"width": 3, "height": 3, "terrain": ["Plain"] * 9}

    @staticmethod
    def movement_costs(unit_id: int) -> list[int]:
        assert unit_id == 1
        return [1] * 9

    def quantum_action_priors(self, actions: list[dict]) -> dict[int, float]:
        return self.system.action_priors(actions)


def test_runtime_policy_accepts_optional_quantum_provider() -> None:
    system = QuantumTacticalSystem(seed=12)
    system.prepare(1, {(1, 0): 1.0, (0, 1): 4.0})
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
        enable_lattice_fields=False,
    )
    actions = [_action(0, 1, 0), _action(1, 0, 1)]
    selected = policy.choose(
        _QuantumEnv(system),
        actions,
        np.zeros(132, dtype=np.float32),
        3,
        3,
    )
    assert selected == 1
    assert policy.backend == "joint-mapf+quantum"
    assert policy.last_plan_reason == "quantum-prior"
