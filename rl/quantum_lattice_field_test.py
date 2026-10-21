"""Fock-space, gauge, coupling, and planner tests for quantum lattice fields."""

from __future__ import annotations

from math import isclose, pi

import numpy as np

from rl.joint_turn_planner import JointTurnPlanner
from rl.lattice_mfg import LatticeMFG, LatticeMFGConfig
from rl.quantum_lattice_field import (
    BosonicLatticeConfig,
    BosonicLatticeField,
    LatticeFieldPolicyAdapter,
    LatticeMFGQuantumCoupler,
    QuantumLatticeFieldError,
)
from rl.runtime_policy import RuntimeBattlePolicy


def _unit() -> dict:
    return {
        "id": 1,
        "force": 4,
        "class": "Infantry",
        "x": 0,
        "y": 0,
        "attack_offsets": ((0, 1), (1, 0)),
        "attack_min": 1,
        "attack_max": 1,
        "move": 5,
        "hp": 100,
        "max_hp": 100,
        "atk": 100,
        "done": False,
        "dead": False,
    }


def _actions() -> list[dict]:
    return [
        {"index": 0, "unit": 1, "type": 1, "x": 0, "y": 0},
        {"index": 1, "unit": 1, "type": 1, "x": 1, "y": 0},
    ]


def test_fock_dimension_and_creation_annihilation() -> None:
    field = BosonicLatticeField.vacuum(
        ((0, 0), (1, 0)),
        config=BosonicLatticeConfig(max_occupancy=2),
    )
    assert field.dimension == 9
    assert field.expected_particles == 0.0
    field.create((0, 0))
    assert isclose(field.expected_occupations()[(0, 0)], 1.0)
    field.create((0, 0))
    assert isclose(field.expected_particles, 2.0)
    field.annihilate((0, 0))
    assert isclose(field.expected_particles, 1.0)


def test_bose_hubbard_evolution_conserves_particles_and_density_invariants() -> None:
    field = BosonicLatticeField(
        ((0, 0), (1, 0)),
        {(1, 0): 1.0},
        config=BosonicLatticeConfig(
            max_occupancy=2,
            hopping=1.0,
            interaction=0.5,
        ),
    )
    field.evolve(0.4)
    occupations = field.expected_occupations()
    assert occupations[(1, 0)] > 0.0
    assert isclose(sum(occupations.values()), 1.0, abs_tol=1e-9)
    assert isclose(float(np.trace(field.state.density).real), 1.0)
    assert float(np.linalg.eigvalsh(field.state.density).min()) >= -1e-9


def test_gauge_link_hamiltonian_is_hermitian_and_phase_changes_dynamics() -> None:
    cells = ((0, 0), (1, 0), (1, 1), (0, 1))
    edges = (
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (0, 1)),
        ((0, 1), (0, 0)),
    )
    config = BosonicLatticeConfig(max_occupancy=1, max_dimension=32)
    plain = BosonicLatticeField(cells, {(1, 0, 0, 0): 1.0}, edges=edges, config=config)
    flux = plain.copy()
    hamiltonian = flux.hamiltonian(gauge_phases={(edges[0]): pi / 2})
    assert np.allclose(hamiltonian, hamiltonian.conj().T)
    plain.evolve(0.8)
    flux.evolve(0.8, gauge_phases={edges[0]: pi / 2})
    assert not np.allclose(
        list(plain.expected_occupations().values()),
        list(flux.expected_occupations().values()),
    )


def test_number_basis_dephasing_reduces_coherence_without_changing_occupancy() -> None:
    field = BosonicLatticeField(
        ((0, 0), (1, 0)),
        {(1, 0): 1.0, (0, 1): 1.0j},
        config=BosonicLatticeConfig(max_occupancy=1),
    )
    before = field.expected_occupations()
    coherence = field.state.coherence
    field.evolve(0.0, dephasing=0.6)
    assert np.allclose(
        list(field.expected_occupations().values()),
        list(before.values()),
    )
    assert isclose(field.state.coherence, coherence * 0.4)


def test_dimension_guard_prevents_exponential_state_blowup() -> None:
    try:
        BosonicLatticeField.vacuum(
            tuple((x, 0) for x in range(8)),
            config=BosonicLatticeConfig(max_occupancy=2, max_dimension=1000),
        )
    except QuantumLatticeFieldError:
        pass
    else:
        raise AssertionError("oversized Fock space must fail before allocation")


def test_coupled_mfg_quantum_solver_preserves_both_invariants() -> None:
    cells = ((0, 0), (1, 0))
    mfg = LatticeMFG(
        cells,
        config=LatticeMFGConfig(
            horizon=2,
            temperature=0.5,
            congestion_weight=0.5,
            tolerance=1e-6,
        ),
    )
    field = BosonicLatticeField(
        cells,
        {(1, 0): 1.0},
        config=BosonicLatticeConfig(max_occupancy=1, hopping=0.8),
    )
    result = LatticeMFGQuantumCoupler(
        mfg,
        field,
        density_to_potential=0.5,
        quantum_to_cost=0.75,
        delta_time=0.2,
        tolerance=1e-5,
    ).solve({(0, 0): 1.0}, {(1, 0): -3.0})
    assert result.residuals
    assert result.quantum_occupancies.shape == (2, 2)
    assert np.allclose(result.mfg.densities.sum(axis=1), 1.0)
    assert np.allclose(result.quantum_occupancies.sum(axis=1), 1.0)
    assert isclose(float(np.trace(result.final_field.state.density).real), 1.0)


def test_mfg_and_quantum_priors_combine_without_creating_actions() -> None:
    actions = _actions()
    units = [_unit()]
    field = BosonicLatticeField(
        ((0, 0), (1, 0)),
        {(0, 1): 1.0},
        config=BosonicLatticeConfig(max_occupancy=1),
    )
    quantum = field.action_priors(actions)
    mfg = {0: -1.0, 1: 1.0}
    chosen = JointTurnPlanner().choose(
        actions,
        units,
        2,
        1,
        movement_costs={1: [1, 1]},
        mfg_priors=mfg,
        quantum_priors=quantum,
    )
    assert chosen.action_index == 1
    assert chosen.reason == "mfg+quantum-prior"


def test_local_field_leaves_actions_outside_its_domain_neutral() -> None:
    field = BosonicLatticeField(
        ((0, 0), (1, 0)),
        {(0, 1): 1.0},
        config=BosonicLatticeConfig(max_occupancy=1),
    )
    actions = [
        *_actions(),
        {"index": 2, "unit": 1, "type": 1, "x": 9, "y": 9},
    ]
    priors = field.action_priors(actions)
    assert set(priors) == {0, 1}
    assert 2 not in priors


class _BaseEnvironment:
    max_units = 8

    @staticmethod
    def unit_info() -> list[dict]:
        return [_unit()]

    @staticmethod
    def map_info() -> dict:
        return {"width": 2, "height": 1, "terrain": ["Plain", "Plain"]}

    @staticmethod
    def movement_costs(unit_id: int) -> list[int]:
        assert unit_id == 1
        return [1, 1]


def test_runtime_adapter_exposes_both_fields_without_mutating_environment() -> None:
    model = LatticeMFG.from_grid(
        2,
        1,
        config=LatticeMFGConfig(
            horizon=1,
            temperature=0.2,
            congestion_weight=0.0,
        ),
    )
    result = model.solve({(0, 0): 1.0}, {(1, 0): -5.0})
    field = BosonicLatticeField(
        ((0, 0), (1, 0)),
        {(0, 1): 1.0},
        config=BosonicLatticeConfig(max_occupancy=1),
    )
    base = _BaseEnvironment()
    adapter = LatticeFieldPolicyAdapter(
        base,
        mfg_result=result,
        quantum_field=field,
    )
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
    )
    selected = policy.choose(
        adapter,
        _actions(),
        np.zeros(132, dtype=np.float32),
        2,
        1,
    )
    assert selected == 1
    assert policy.backend == "joint-mapf+mfg+quantum+cp-sat-optimal"
    assert policy.last_plan_reason == "mfg+quantum-prior"
    assert not hasattr(base, "mfg_action_priors")
