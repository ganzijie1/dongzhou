import numpy as np

from rl.p45_congestion_wardrop_poa_math import (
    price_of_anarchy,
    rosenthal_potential,
    social_optimum_parallel_affine,
    wardrop_parallel_affine,
)


def test_parallel_affine_wardrop_equalizes_used_route_latency():
    result = wardrop_parallel_affine([1.0, 2.0], [0.0, 0.0], 3.0)
    assert np.allclose(result.flows, [2.0, 1.0])
    assert np.allclose(result.latencies, [2.0, 2.0])
    assert result.variational_gap < 1e-10


def test_social_optimum_uses_marginal_cost_and_improves_asymmetric_network():
    equilibrium = wardrop_parallel_affine([1.0, 0.01], [0.0, 1.0], 1.0)
    optimum = social_optimum_parallel_affine([1.0, 0.01], [0.0, 1.0], 1.0)
    assert optimum.total_cost <= equilibrium.total_cost + 1e-12
    assert price_of_anarchy(equilibrium.total_cost, optimum.total_cost) >= 1.0


def test_rosenthal_potential_sums_incremental_resource_costs():
    table = [[0.0, 1.0, 3.0], [0.0, 2.0, 5.0]]
    assert np.isclose(rosenthal_potential([2, 1], table), 6.0)
