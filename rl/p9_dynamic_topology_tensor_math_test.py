import math

import numpy as np

from rl.p9_dynamic_topology_tensor_math import (
    ZigzagInterval,
    forman_ricci_curvature,
    graph_h0_zigzag_persistence,
    multirelational_hosvd,
    ollivier_ricci_curvature,
)


def test_exact_h0_zigzag_decomposes_merge_then_split():
    result = graph_h0_zigzag_persistence(
        ("a", "b"),
        ((), (("a", "b"),), ()),
        ("forward", "backward"),
    )
    assert result.component_dimensions == (2, 1, 2)
    assert result.intervals.count(ZigzagInterval(0, 2)) == 1
    assert result.intervals.count(ZigzagInterval(0, 0)) == 1
    assert result.intervals.count(ZigzagInterval(2, 2)) == 1
    assert len(result.intervals) == 3


def test_graph_curvatures_identify_path_edges():
    vertices = (0, 1, 2, 3)
    edges = ((0, 1), (1, 2))
    forman = forman_ricci_curvature(vertices, edges)
    ollivier = ollivier_ricci_curvature(vertices, edges, idleness=0.5)
    assert forman[(0, 1)] == 1.0
    assert forman[(1, 2)] == 1.0
    assert math.isclose(ollivier[(0, 1)], 0.5, abs_tol=1e-9)
    assert math.isclose(ollivier[(1, 2)], 0.5, abs_tol=1e-9)


def test_multirelational_hosvd_exactly_recovers_rank_one_tensor():
    actor_left = np.array([1.0, 2.0, 3.0])
    actor_right = np.array([2.0, -1.0, 0.5])
    relation = np.array([1.0, 4.0])
    time = np.array([1.0, 0.5, 2.0])
    tensor = np.einsum("i,j,k,l->ijkl", actor_left, actor_right, relation, time)
    result = multirelational_hosvd(tensor, (1, 1, 1, 1))
    assert result.core.shape == (1, 1, 1, 1)
    assert result.relative_error < 1e-12
    assert np.allclose(result.reconstruct(), tensor)
