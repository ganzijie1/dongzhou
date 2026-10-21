"""Cross-backend tests for CP-SAT, MILP, and the tactical portfolio."""

from __future__ import annotations

from rl.classical_optimization import (
    CPSATActionOptimizer,
    ClassicalOptimizationConfig,
    MILPActionOptimizer,
    TacticalOptimizationPortfolio,
)
from rl.quantum_optimization import QUBOAction, TacticalQUBOOptimizer


def _actions() -> list[QUBOAction]:
    return [
        QUBOAction(0, 1, 10.0, ((0, 0), (1, 0))),
        QUBOAction(1, 1, 9.0, ((0, 0), (0, 1))),
        QUBOAction(2, 2, 10.0, ((2, 0), (1, 0))),
        QUBOAction(3, 2, 0.0, ((2, 0), (2, 1))),
    ]


def test_cp_sat_solves_the_native_action_model_to_optimality() -> None:
    solution = CPSATActionOptimizer().solve(_actions())
    assert solution.backend == "cp-sat-optimal"
    assert solution.selected_actions == (1, 2)
    assert solution.optimal
    assert solution.relative_gap == 0.0
    assert solution.solve_time_ms is not None


def test_milp_solves_the_same_model_to_the_same_optimum() -> None:
    solution = MILPActionOptimizer().solve(_actions())
    assert solution.backend == "milp-optimal"
    assert solution.selected_actions == (1, 2)
    assert solution.optimal
    assert solution.relative_gap == 0.0
    assert solution.solve_time_ms is not None


def test_cp_sat_milp_and_qubo_agree_on_actions_and_energy() -> None:
    solutions = [
        CPSATActionOptimizer().solve(_actions()),
        MILPActionOptimizer().solve(_actions()),
        TacticalQUBOOptimizer().solve(_actions()),
    ]
    assert {solution.selected_actions for solution in solutions} == {(1, 2)}
    assert len({solution.energy for solution in solutions}) == 1


class _BrokenCPSAT:
    @staticmethod
    def solve_model(model):
        raise RuntimeError("injected CP-SAT failure")


def test_auto_portfolio_falls_through_to_real_milp() -> None:
    portfolio = TacticalOptimizationPortfolio()
    portfolio.cp_sat = _BrokenCPSAT()
    solution = portfolio.solve(_actions())
    assert solution.backend == "milp-optimal"
    assert solution.selected_actions == (1, 2)
    assert solution.used_fallback
    assert "injected CP-SAT failure" in (solution.backend_error or "")


def test_backend_can_be_pinned_for_ablation() -> None:
    milp = TacticalOptimizationPortfolio(
        ClassicalOptimizationConfig(backend="milp")
    ).solve(_actions())
    qubo = TacticalOptimizationPortfolio(
        ClassicalOptimizationConfig(backend="qubo")
    ).solve(_actions())
    assert milp.backend == "milp-optimal"
    assert qubo.backend == "qubo-exact"
