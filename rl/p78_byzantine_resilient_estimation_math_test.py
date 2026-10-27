import numpy as np

from rl.p78_byzantine_resilient_estimation_math import cusum_update, geometric_median, graph_r_reachable, innovation_score, sparse_observability_audit, static_attack_residual, trimmed_mean, wmsr_scalar_step


def test_trimmed_mean_and_wmsr_reject_extremes():
    assert np.isclose(trimmed_mean([-100, 1, 2, 3, 100], 1), 2.0)
    updated, retained = wmsr_scalar_step(2.0, [-100, 1, 3, 100], 1)
    assert np.isclose(updated, 2.0) and set(retained) == {1, 2}


def test_geometric_median_resists_outlier_and_scores_innovation():
    median = geometric_median([[0, 0], [0, 0], [1, 0], [100, 100]])
    assert np.linalg.norm(median) < 1.1
    assert np.isclose(innovation_score([1.0, 2.0], np.eye(2)), 5.0)
    assert np.isclose(cusum_update(1.0, 0.2, 0.5), 0.7)


def test_attack_residual_sparse_observability_and_graph_reachability():
    residual = static_attack_residual([[1.0], [1.0]], [1.0, -1.0])
    assert np.allclose(residual, [1.0, -1.0])
    assert sparse_observability_audit([[1.0]], [[1.0], [2.0], [3.0]], 1)
    graph = np.ones((3, 3), dtype=bool)
    np.fill_diagonal(graph, False)
    assert graph_r_reachable(graph, [0], 2)
