import numpy as np

from rl.p41_restless_bandit_index_math import (
    gittins_index,
    select_whittle_arms,
    whittle_indices,
)


def test_constant_arm_gittins_index_equals_reward():
    assert np.isclose(gittins_index([[1.0]], [3.5], 0, discount=0.9), 3.5, atol=1e-8)


def test_one_state_whittle_index_is_reward_advantage():
    result = whittle_indices(
        [[1.0]], [[1.0]], [4.0], [1.5], discount=0.8, subsidy_bounds=(-5.0, 5.0)
    )
    assert result.indexable
    assert np.isclose(result.indices[0], 2.5, atol=1e-7)


def test_whittle_selection_respects_capacity_and_order():
    assert np.array_equal(select_whittle_arms([1.0, 5.0, 3.0], 2), [1, 2])


def test_non_stochastic_kernel_is_rejected():
    try:
        gittins_index([[0.5]], [1.0], 0, discount=0.9)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid transition kernel was accepted")
