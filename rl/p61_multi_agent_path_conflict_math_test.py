import numpy as np

from rl.p61_multi_agent_path_conflict_math import (
    build_reservation_table,
    continuous_time_conflict,
    ecbs_focal_indices,
    first_discrete_conflict,
    path_violates_reservations,
)


def test_vertex_and_edge_conflicts_are_detected():
    assert first_discrete_conflict([[0, 1, 2], [2, 1, 0]]).kind == "vertex"
    conflict = first_discrete_conflict([[0, 1], [1, 0]])
    assert conflict.kind == "edge" and conflict.time == 1


def test_reservation_table_detects_reverse_edge():
    table = build_reservation_table([[0, 1, 2]])
    assert path_violates_reservations([3, 1, 0], table)
    assert not path_violates_reservations([3, 4, 5], table)


def test_ecbs_focal_and_continuous_collision():
    assert np.array_equal(ecbs_focal_indices([10, 12, 16], 10, 1.2), [0, 1])
    collided, time, distance = continuous_time_conflict([0, 0], [2, 0], [2, 0], [0, 0], radius_sum=0.1)
    assert collided and np.isclose(time, 0.5) and np.isclose(distance, 0.0)
