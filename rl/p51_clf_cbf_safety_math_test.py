import numpy as np

from rl.p51_clf_cbf_safety_math import (
    affine_cbf_constraint,
    clf_cbf_safety_filter,
    high_order_barrier_chain,
)


def test_affine_cbf_builds_lower_bound_on_control():
    row, lower = affine_cbf_constraint([1.0], [0.0], [[1.0]], 0.5, alpha=2.0)
    assert np.allclose(row, [1.0])
    assert np.isclose(lower, -1.0)


def test_safety_filter_preserves_cbf_and_relaxes_conflicting_clf():
    result = clf_cbf_safety_filter(
        [-1.0],
        cbf_matrix=[[1.0]],
        cbf_lower_bounds=[0.5],
        clf_matrix=[[1.0]],
        clf_upper_bounds=[-0.2],
        lower_bounds=[-2.0],
        upper_bounds=[2.0],
    )
    assert result.control[0] >= 0.5 - 1e-7
    assert result.clf_slack >= 0.7 - 1e-6
    assert result.minimum_cbf_margin >= -1e-7
    assert result.maximum_clf_residual <= 1e-7


def test_high_order_barrier_chain_combines_supplied_derivatives():
    assert np.isclose(high_order_barrier_chain([2.0, -1.0, 0.5], [3.0, 4.0]), 2.5)
