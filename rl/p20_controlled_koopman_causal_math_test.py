import numpy as np

from rl.p20_controlled_koopman_causal_math import (
    discounted_model_transfer_bound,
    dynamic_mode_decomposition_with_control,
    extended_dynamic_mode_decomposition_with_control,
    invariant_causal_prediction,
    koopman_mpc,
    notears_linear,
    omitted_variable_sensitivity,
    partial_correlation_test,
    pc_skeleton,
    stochastic_viability_kernel,
    ulam_transfer_operator,
)


def test_dmdc_and_edmdc_recover_controlled_linear_dynamics():
    current = np.array([[0.0, 1.0, 2.0, -1.0]])
    control = np.array([[1.0, 0.0, -1.0, 2.0]])
    future = 0.8 * current + 2.0 * control
    dmdc = dynamic_mode_decomposition_with_control(current, control, future)
    assert np.allclose(dmdc.state_matrix, [[0.8]])
    assert np.allclose(dmdc.control_matrix, [[2.0]])
    assert dmdc.relative_residual < 1e-12
    assert np.allclose(dmdc.predict([3.0], [-1.0]), [0.4])

    samples = current.T
    next_samples = future.T
    edmdc = extended_dynamic_mode_decomposition_with_control(
        samples,
        control.T,
        next_samples,
        [lambda state: state[0]],
    )
    assert np.allclose(edmdc.koopman_matrix, [[0.8]])
    assert np.allclose(edmdc.control_matrix, [[2.0]])
    assert np.allclose(edmdc.lift([3.0]), [3.0])


def test_koopman_mpc_selects_controls_that_reach_target():
    result = koopman_mpc(
        [[1.0]],
        [[1.0]],
        [2.0],
        [[-1.0], [0.0], [1.0]],
        [0.0],
        [[1.0]],
        [[0.01]],
        horizon=2,
    )
    assert np.array_equal(result.controls, [[-1.0], [-1.0]])
    assert np.allclose(result.trajectory[:, 0], [2.0, 1.0, 0.0])
    assert result.sequences_evaluated == 9


def test_ulam_operator_and_stationary_distribution():
    result = ulam_transfer_operator(
        [[0.2], [0.8], [1.2], [1.8]],
        [[1.2], [1.8], [0.2], [0.8]],
        [[0.0, 1.0, 2.0]],
    )
    assert np.allclose(result.transition_matrix, [[0.0, 1.0], [1.0, 0.0]])
    assert np.allclose(result.stationary_distribution, [0.5, 0.5])
    assert result.discarded_samples == 0


def test_stochastic_viability_removes_states_without_safe_control():
    transition = np.array(
        [
            [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    result = stochastic_viability_kernel(transition, [0, 1])
    assert result.viable_states == (0,)
    assert result.viable_actions[0] == (0,)
    assert result.viable_actions[1] == ()


def test_notears_finds_an_acyclic_dependency_candidate():
    random = np.random.default_rng(7)
    cause = random.normal(size=400)
    effect = 2.0 * cause + random.normal(scale=0.1, size=400)
    independent = random.normal(size=400)
    result = notears_linear(
        np.column_stack((cause, effect, independent)),
        l1_penalty=0.02,
        edge_threshold=0.1,
    )
    assert result.acyclicity < 1e-7
    assert result.converged
    assert abs(result.adjacency[0, 1]) > 0.5
    assert result.adjacency[1, 0] == 0.0


def test_partial_correlation_and_pc_remove_chain_shortcut():
    random = np.random.default_rng(11)
    left = random.normal(size=800)
    middle = left + random.normal(scale=0.5, size=800)
    right = middle + random.normal(scale=0.5, size=800)
    samples = np.column_stack((left, middle, right))
    marginal = partial_correlation_test(samples, 0, 2)
    conditional = partial_correlation_test(samples, 0, 2, [1])
    assert marginal.p_value < 1e-6
    assert conditional.p_value > 0.05
    skeleton = pc_skeleton(samples, significance=0.01, maximum_conditioning=1)
    assert not skeleton.adjacency[0, 2]
    assert skeleton.adjacency[0, 1]
    assert skeleton.adjacency[1, 2]


def test_invariant_causal_prediction_keeps_stable_parent():
    random = np.random.default_rng(19)
    environments = []
    for index, mean in enumerate((0.0, 2.0)):
        cause = random.normal(loc=mean, size=500)
        outcome = 3.0 * cause + random.normal(scale=0.3, size=500)
        spurious = (1.0 if index == 0 else -1.0) * outcome + random.normal(
            scale=0.3, size=500
        )
        environments.append(np.column_stack((cause, spurious, outcome)))
    result = invariant_causal_prediction(
        environments, target=2, candidate_predictors=[0, 1]
    )
    assert (0,) in result.accepted_sets
    assert result.invariant_predictors == (0,)


def test_sensitivity_and_transfer_bounds_expand_with_uncertainty():
    none = omitted_variable_sensitivity(
        2.0,
        0.2,
        100,
        treatment_confounder_partial_r2=0.0,
        outcome_confounder_partial_r2=0.0,
    )
    confounded = omitted_variable_sensitivity(
        2.0,
        0.2,
        100,
        treatment_confounder_partial_r2=0.2,
        outcome_confounder_partial_r2=0.2,
    )
    assert none.maximum_bias == 0.0
    assert confounded.maximum_bias > 0.0
    assert confounded.adjusted_estimate_interval[0] < 2.0
    assert discounted_model_transfer_bound(0.0, 0.0, 1.0, discount=0.9) == 0.0
    assert discounted_model_transfer_bound(0.1, 0.1, 1.0, discount=0.9) > 0.0
