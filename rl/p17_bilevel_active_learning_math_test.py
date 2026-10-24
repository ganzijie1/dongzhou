import numpy as np

from rl.p17_bilevel_active_learning_math import (
    active_irl_query,
    equality_qp_sensitivity,
    expected_information_gain,
    greedy_optimal_design,
    implicit_hypergradient,
    linear_program_active_set_sensitivity,
    linear_program_kkt_certificate,
    logistic_preference_fisher_information,
    solve_finite_bilevel_linear,
    wald_confidence_ellipsoid,
)


def test_finite_bilevel_lp_resolves_lower_ties_and_upper_choices():
    optimistic = solve_finite_bilevel_linear(
        [[1.0, 0.0], [0.0, 1.0]],
        [[0.0, 0.0], [0.0, 0.0]],
        [
            [[-1.0, 0.0], [0.0, -1.0], [1.0, 1.0]],
            [[-1.0, 0.0], [0.0, -1.0], [1.0, 1.0]],
        ],
        [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        tie_breaking="optimistic",
    )
    pessimistic = solve_finite_bilevel_linear(
        [[1.0, 0.0], [0.0, 1.0]],
        [[0.0, 0.0], [0.0, 0.0]],
        [
            [[-1.0, 0.0], [0.0, -1.0], [1.0, 1.0]],
            [[-1.0, 0.0], [0.0, -1.0], [1.0, 1.0]],
        ],
        [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        tie_breaking="pessimistic",
    )
    assert optimistic.upper_value == 0.0
    assert np.isclose(pessimistic.upper_value, 1.0)
    assert optimistic.feasible_upper_choices == (0, 1)


def test_linear_kkt_certificate_detects_exact_and_wrong_multipliers():
    exact = linear_program_kkt_certificate(
        [2.0, 1.0],
        [[-1.0, 0.0], [0.0, -1.0]],
        [0.0, 0.0],
        [0.0, 0.0],
        [2.0, 1.0],
    )
    wrong = linear_program_kkt_certificate(
        [2.0, 1.0],
        [[-1.0, 0.0], [0.0, -1.0]],
        [0.0, 0.0],
        [0.0, 0.0],
        [0.0, 0.0],
    )
    assert exact.certified
    assert not wrong.certified
    assert wrong.stationarity_residual == 2.0


def test_implicit_hypergradient_matches_quadratic_closed_form():
    # Inner optimum y*(theta)=theta for 0.5(y-theta)^2.
    result = implicit_hypergradient(
        [1.0], [3.0], [[1.0]], [[-1.0]]
    )
    assert np.allclose(result.inner_sensitivity, [[1.0]])
    assert np.allclose(result.hypergradient, [4.0])
    assert not result.used_pseudoinverse


def test_equality_qp_and_lp_active_set_sensitivities():
    # min 0.5 ||x||^2 with x0+x1=b has x=(b/2,b/2).
    result = equality_qp_sensitivity(
        np.eye(2),
        [0.0, 0.0],
        [[1.0, 1.0]],
        [2.0],
        np.zeros((2, 1)),
        [[1.0]],
    )
    assert np.allclose(result.decision, [1.0, 1.0])
    assert np.allclose(result.decision_jacobian[:, 0], [0.5, 0.5])
    assert result.kkt_residual < 1e-10
    active = linear_program_active_set_sensitivity(
        [[1.0, 0.0], [0.0, 1.0]], [[1.0], [2.0]]
    )
    assert active.unique
    assert np.allclose(active.decision_jacobian[:, 0], [1.0, 2.0])


def test_fisher_information_and_greedy_d_a_optimal_design():
    candidates = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    fisher = logistic_preference_fisher_information(candidates, [0.0, 0.0])
    assert np.all(np.linalg.eigvalsh(fisher) > 0.0)
    d_design = greedy_optimal_design(candidates, 2, criterion="d")
    a_design = greedy_optimal_design(candidates, 2, criterion="a")
    assert len(d_design.selected_indices) == 2
    assert len(a_design.selected_indices) == 2
    assert d_design.objective_history[1] >= d_design.objective_history[0]
    assert a_design.objective_history[1] >= a_design.objective_history[0]


def test_expected_information_gain_selects_discriminating_experiment():
    likelihood = np.array(
        [
            [[0.5, 0.5], [0.5, 0.5]],
            [[0.9, 0.1], [0.1, 0.9]],
        ]
    )
    result = expected_information_gain([0.5, 0.5], likelihood)
    assert result.best_experiment == 1
    assert result.information_gain[1] > result.information_gain[0]
    assert np.allclose(result.predictive_outcomes.sum(axis=1), 1.0)


def test_active_irl_query_selects_trajectory_pair_that_separates_rewards():
    result = active_irl_query(
        [[2.0, 0.0], [0.0, 2.0]],
        [[1.0, 1.0], [1.0, -1.0]],
        [0.5, 0.5],
        precision=2.0,
    )
    assert result.best_experiment == 1
    assert result.information_gain[1] > result.information_gain[0]


def test_wald_confidence_reports_rank_and_null_space():
    result = wald_confidence_ellipsoid([1.0, 2.0], [[4.0, 0.0], [0.0, 0.0]])
    assert result.rank == 1
    assert result.null_space.shape == (2, 1)
    assert result.contains([1.0, 2.0])
    assert result.contains([1.0, 200.0])
    assert not result.contains([100.0, 2.0])
