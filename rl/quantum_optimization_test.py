"""Tests for QUBO compilation, solver fallback, and sample validation."""

from __future__ import annotations

from rl.quantum_optimization import (
    QUBOAction,
    QuantumOptimizationConfig,
    SampledQUBOSolver,
    TacticalQUBOCompiler,
    TacticalQUBOOptimizer,
)


def _actions() -> list[QUBOAction]:
    return [
        QUBOAction(0, 1, 10.0, ((0, 0), (1, 0))),
        QUBOAction(1, 1, 9.0, ((0, 0), (0, 1))),
        QUBOAction(2, 2, 10.0, ((2, 0), (1, 0))),
        QUBOAction(3, 2, 0.0, ((2, 0), (2, 1))),
    ]


def test_compiler_encodes_one_hot_and_space_time_conflicts() -> None:
    model = TacticalQUBOCompiler().compile(_actions())
    assert model.variable_count == 4
    assert model.combination_count == 4
    assert (0, 2) in model.conflicts
    assert model.is_feasible((1, 2))
    assert not model.is_feasible((0, 2))
    assert not model.is_feasible((0, 1, 3))
    assert model.energy((1, 2)) < model.energy((0, 2))


def test_exact_qubo_finds_global_non_conflicting_combination() -> None:
    solution = TacticalQUBOOptimizer().solve(_actions())
    assert solution.backend == "qubo-exact"
    assert solution.selected_actions == (1, 2)
    assert not solution.used_fallback
    assert solution.evaluated_states == 4


def test_invalid_qaoa_sample_falls_back_to_verified_exact_solution() -> None:
    external = SampledQUBOSolver(lambda model: {0: 1, 2: 1}, name="qaoa-mock")
    solution = TacticalQUBOOptimizer(external_solver=external).solve(_actions())
    assert solution.backend == "qubo-exact"
    assert solution.selected_actions == (1, 2)
    assert solution.used_fallback
    assert "no feasible sample" in (solution.backend_error or "")


def test_valid_quantum_sample_is_accepted_without_changing_native_actions() -> None:
    external = SampledQUBOSolver(
        lambda model: [{0: 1, 3: 1}, {1: 1, 2: 1}],
        name="qaoa-mock",
    )
    solution = TacticalQUBOOptimizer(external_solver=external).solve(_actions())
    assert solution.backend == "qubo-qaoa-mock"
    assert solution.selected_actions == (1, 2)
    assert not solution.used_fallback


def test_large_problem_uses_bounded_classical_backend() -> None:
    config = QuantumOptimizationConfig(exact_variable_limit=1)
    solution = TacticalQUBOOptimizer(config).solve(_actions())
    assert solution.backend == "qubo-bounded"
    assert solution.selected_actions == (1, 2)
