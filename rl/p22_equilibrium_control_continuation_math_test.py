import numpy as np

from rl.p22_equilibrium_control_continuation_math import (
    average_cost_lmdp,
    classify_static_bifurcation,
    detect_dynamic_bifurcations,
    finite_distributionally_robust_nash,
    finite_distributionally_robust_stackelberg,
    finite_horizon_lmdp,
    implicit_equilibrium_sensitivity,
    pseudo_arclength_continuation,
    solve_bimatrix_logit_qre,
)


def test_finite_and_average_lmdp_preserve_passive_support():
    passive = np.array([[0.8, 0.2], [0.0, 1.0]])
    finite = finite_horizon_lmdp(
        passive,
        [[0.0, 0.2], [0.0, 0.2]],
        [0.0, 1.0],
        temperature=0.7,
    )
    assert finite.bellman_residual < 1e-12
    assert np.allclose(finite.controlled_transition.sum(axis=2), 1.0)
    assert np.all(finite.controlled_transition[:, passive == 0.0] == 0.0)
    assert finite.controlled_transition[0, 0, 0] > passive[0, 0]

    average = average_cost_lmdp(
        [[0.5, 0.5], [0.5, 0.5]], [0.0, 0.0], temperature=1.0
    )
    assert np.isclose(average.average_cost, 0.0)
    assert average.eigen_residual < 1e-12
    assert np.allclose(average.controlled_transition, 0.5)


def test_implicit_sensitivity_and_qre_use_nonsingular_local_systems():
    result = implicit_equilibrium_sensitivity(
        [[2.0, 0.0], [0.0, 4.0]], [[1.0], [2.0]]
    )
    assert np.allclose(result.sensitivity[:, 0], [-0.5, -0.5])
    assert result.linear_residual < 1e-12
    assert not result.used_pseudoinverse

    qre = solve_bimatrix_logit_qre(
        [[1.0, -1.0], [-1.0, 1.0]],
        [[-1.0, 1.0], [1.0, -1.0]],
        row_rationality=2.0,
        column_rationality=3.0,
    )
    assert qre.converged
    assert qre.residual < 1e-9
    assert np.allclose(qre.row_strategy, [0.5, 0.5])
    assert np.allclose(qre.column_strategy, [0.5, 0.5])
    assert np.allclose(qre.beta_sensitivity, 0.0, atol=1e-8)


def test_finite_distributionally_robust_nash_and_stackelberg():
    costs = np.zeros((2, 2, 2, 2))
    costs[0, :, 1, :] = 1.0
    costs[1, :, :, 1] = 1.0
    vertices = np.array([[1.0, 0.0], [0.0, 1.0]])
    nash = finite_distributionally_robust_nash(costs, vertices)
    assert nash.equilibria == ((0, 0),)

    leader = np.array(
        [
            [[2.0, 4.0], [3.0, 1.0]],
            [[2.0, 4.0], [3.0, 1.0]],
        ]
    )
    follower = np.array(
        [
            [[0.0, 1.0], [1.0, 0.0]],
            [[0.0, 1.0], [1.0, 0.0]],
        ]
    )
    stackelberg = finite_distributionally_robust_stackelberg(
        leader, follower, vertices, vertices
    )
    assert stackelberg.leader_action == 1
    assert stackelberg.follower_action == 1
    assert stackelberg.follower_best_responses == ((0,), (1,))


def test_pseudo_arclength_crosses_a_simple_fold():
    def residual(state, parameter):
        return np.array([state[0] ** 2 + parameter - 1.0])

    result = pseudo_arclength_continuation(
        residual,
        [1.0],
        0.0,
        steps=28,
        step_size=0.08,
        maximum_step=0.12,
    )
    assert result.converged
    assert np.max(result.points[:, 1]) > 0.99
    assert np.min(result.points[:, 0]) < -0.1
    assert result.fold_indices
    assert np.max(result.equilibrium_residuals) < 1e-8


def test_static_and_dynamic_bifurcation_diagnostics():
    fold = classify_static_bifurcation([[0.0]], [1.0], second_directional=[2.0])
    branch = classify_static_bifurcation([[0.0]], [0.0])
    assert fold.kind == "fold_candidate"
    assert np.isclose(fold.quadratic_coefficient, 2.0)
    assert branch.kind == "branch_candidate"

    continuous = detect_dynamic_bifurcations([[0.0, -2.0], [2.0, 0.0]])
    discrete = detect_dynamic_bifurcations(
        [[1.0, 0.0], [0.0, -1.0]], discrete_time=True
    )
    assert "hopf_candidate" in continuous.candidates
    assert "steady_state_candidate" in discrete.candidates
    assert "flip_candidate" in discrete.candidates
