import numpy as np

from rl.p31_variational_stochastic_optimization_math import (
    affine_proximal_point,
    borkar_meyn_stability_diagnostic,
    extragradient,
    mirror_descent_simplex,
    polyak_ruppert_average,
    project_simplex,
    robbins_monro,
    two_timescale_stochastic_approximation,
    variational_inequality_gap,
)


def test_simplex_projection_and_mirror_descent_select_low_cost_action():
    assert np.allclose(project_simplex([-1.0, 2.0, 0.0]), [0.0, 1.0, 0.0])
    result = mirror_descent_simplex(
        [0.5, 0.5], lambda _: np.array([0.0, 1.0]), np.full(80, 0.2)
    )
    assert result.point[0] > 0.999
    assert np.isclose(result.point.sum(), 1.0)


def test_extragradient_stabilizes_bilinear_saddle_operator():
    result = extragradient(
        lambda value: np.array([value[1], -value[0]]),
        [1.0, 1.0],
        step_size=0.2,
        iterations=400,
        tolerance=1e-8,
    )
    assert np.linalg.norm(result.point) < 1e-3


def test_vi_gap_and_affine_proximal_point_find_root():
    def operator(value):
        return value - np.array([0.25, 0.75])

    candidates = np.eye(2)
    gap = variational_inequality_gap(operator, [0.25, 0.75], candidates)
    assert gap.stampacchia == 0.0
    result = affine_proximal_point(
        np.eye(2), [-1.0, 2.0], [5.0, 5.0], step_size=1.0, iterations=80
    )
    assert np.allclose(result.point, [1.0, -2.0], atol=1e-8)


def test_robbins_monro_and_polyak_average():
    path = robbins_monro(
        [0.0], lambda _index, point: point - 2.0, 1.0 / np.arange(1, 501)
    )
    assert np.isclose(path[-1, 0], 2.0, atol=1e-10)
    average = polyak_ruppert_average(path, burn_in=250)
    assert np.isclose(average[0], 2.0, atol=1e-8)


def test_two_timescale_fast_variable_tracks_slow_target():
    result = two_timescale_stochastic_approximation(
        [0.0],
        [4.0],
        lambda _index, slow, _fast: slow - 1.0,
        lambda _index, slow, fast: fast - slow,
        0.1 / np.sqrt(np.arange(1, 2001)),
        0.4 / np.power(np.arange(1, 2001), 0.6),
        average_burn_in=1000,
    )
    assert np.isclose(result.slow_path[-1, 0], 1.0, atol=2e-3)
    assert np.isclose(result.fast_path[-1, 0], 1.0, atol=2e-3)


def test_borkar_meyn_diagnostic_requires_inward_outer_drift():
    points = np.array([[0.1, 0.0], [2.0, 0.0], [0.0, -3.0]])
    result = borkar_meyn_stability_diagnostic(points, -points, radius=1.0)
    assert result.stable_outside_radius
    assert result.maximum_outer_drift < 0.0
