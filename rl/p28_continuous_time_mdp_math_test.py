import numpy as np
from scipy.linalg import expm

from rl.p28_continuous_time_mdp_math import (
    average_reward_ctmdp,
    discounted_ctmdp_value_iteration,
    evaluate_ctmdp_policy,
    uniformize_ctmdp,
    uniformized_transient_distribution,
)


def _model():
    return np.array(
        [
            [[-1.0, 1.0], [-2.0, 2.0]],
            [[0.5, -0.5], [1.5, -1.5]],
        ]
    )


def test_uniformization_recovers_generators_and_stochastic_kernels():
    generators = _model()
    result = uniformize_ctmdp(generators, rate=2.5)
    assert np.allclose(result.transition.sum(axis=2), 1.0)
    identity = np.eye(2)[:, None, :]
    assert np.allclose(2.5 * (result.transition - identity), generators)


def test_discounted_ctmdp_matches_exact_policy_evaluation():
    generators = _model()
    rewards = np.array([[1.0, 1.4], [0.0, 0.2]])
    result = discounted_ctmdp_value_iteration(
        generators, rewards, discount_rate=0.7
    )
    exact = evaluate_ctmdp_policy(
        generators, rewards, result.policy, discount_rate=0.7
    )
    assert np.allclose(result.values, exact, atol=1e-8)
    assert result.residual < 1e-8


def test_average_reward_relative_iteration_solves_bellman_equation():
    generators = _model()
    rewards = np.array([[1.0, 1.4], [0.0, 0.2]])
    result = average_reward_ctmdp(generators, rewards)
    action = rewards + np.einsum("san,n->sa", generators, result.bias)
    assert np.allclose(np.max(action, axis=1), result.gain, atol=1e-8)
    assert result.span_residual < 1e-8


def test_uniformized_transient_matches_matrix_exponential():
    generator = np.array([[-1.2, 1.2], [0.4, -0.4]])
    initial = np.array([1.0, 0.0])
    actual, omitted, _ = uniformized_transient_distribution(
        generator, initial, 2.3
    )
    expected = initial @ expm(generator * 2.3)
    assert np.allclose(actual, expected, atol=1e-11)
    assert omitted <= 1e-13


def test_zero_generator_keeps_distribution_fixed():
    actual, omitted, terms = uniformized_transient_distribution(
        np.zeros((2, 2)), [0.3, 0.7], 10.0
    )
    assert np.allclose(actual, [0.3, 0.7])
    assert omitted == 0.0
    assert terms == 1


def test_uniformized_transient_is_stable_for_large_poisson_mean():
    generator = np.array([[-100.0, 100.0], [50.0, -50.0]])
    actual, omitted, terms = uniformized_transient_distribution(
        generator, [1.0, 0.0], 10.0
    )
    assert np.allclose(actual, [1.0 / 3.0, 2.0 / 3.0], atol=1e-10)
    assert omitted <= 1e-13
    assert terms < 1_000
