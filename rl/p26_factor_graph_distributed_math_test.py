import numpy as np

from rl.p26_factor_graph_distributed_math import (
    DiscreteFactor,
    consensus_admm,
    junction_tree_calibrate,
    loopy_belief_propagation,
    max_sum_dcop,
)


def test_sum_product_is_exact_on_a_binary_chain():
    factors = [
        DiscreteFactor((0,), np.array([0.8, 0.2])),
        DiscreteFactor((0, 1), np.array([[3.0, 1.0], [1.0, 3.0]])),
        DiscreteFactor((1,), np.array([0.4, 0.6])),
    ]
    result = loopy_belief_propagation([2, 2], factors)
    joint = (
        factors[0].values[:, None]
        * factors[1].values
        * factors[2].values[None, :]
    )
    joint /= joint.sum()
    assert result.converged
    assert np.allclose(result.variable_beliefs[0], joint.sum(axis=1))
    assert np.allclose(result.variable_beliefs[1], joint.sum(axis=0))


def test_loopy_bp_reports_a_normalized_fixed_point():
    pair = np.array([[2.0, 1.0], [1.0, 2.0]])
    factors = [
        DiscreteFactor((0, 1), pair),
        DiscreteFactor((1, 2), pair),
        DiscreteFactor((2, 0), pair),
    ]
    result = loopy_belief_propagation(
        [2, 2, 2], factors, damping=0.5, max_iterations=100
    )
    assert result.converged
    assert all(np.isclose(belief.sum(), 1.0) for belief in result.variable_beliefs)


def test_max_sum_decodes_tree_dcop_global_optimum():
    factors = [
        DiscreteFactor((0,), np.array([1.0, 0.0])),
        DiscreteFactor((0, 1), np.array([[2.0, 0.0], [0.0, 3.0]])),
        DiscreteFactor((1,), np.array([0.0, 2.0])),
    ]
    result = max_sum_dcop([2, 2], factors)
    assert result.exact_tree
    assert result.assignment == (1, 1)
    assert np.isclose(result.objective, 5.0)


def test_junction_tree_matches_direct_three_variable_marginals():
    pair01 = np.array([[3.0, 1.0], [1.0, 2.0]])
    pair12 = np.array([[2.0, 1.0], [1.0, 4.0]])
    result = junction_tree_calibrate(
        [2, 2, 2],
        [(0, 1), (1, 2)],
        [pair01, pair12],
        [(0, 1)],
    )
    joint = pair01[:, :, None] * pair12[None, :, :]
    joint /= joint.sum()
    assert np.allclose(result.variable_beliefs[0], joint.sum(axis=(1, 2)))
    assert np.allclose(result.variable_beliefs[1], joint.sum(axis=(0, 2)))
    assert np.allclose(result.variable_beliefs[2], joint.sum(axis=(0, 1)))
    assert result.separator_residual < 1e-12


def test_consensus_admm_solves_weighted_quadratic_consensus():
    centers = [np.array([0.0, 2.0]), np.array([4.0, 0.0])]
    weights = [1.0, 3.0]

    def operator(center, weight):
        return lambda value, rho: (weight * center + rho * value) / (weight + rho)

    result = consensus_admm(
        [operator(center, weight) for center, weight in zip(centers, weights)],
        [0.0, 0.0],
        rho=1.0,
    )
    expected = (weights[0] * centers[0] + weights[1] * centers[1]) / sum(weights)
    assert result.converged
    assert np.allclose(result.consensus, expected, atol=2e-4)
    assert result.primal_residuals[-1] < 1e-4
