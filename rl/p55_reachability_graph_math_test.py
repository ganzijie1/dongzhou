import numpy as np

from rl.p55_reachability_graph_math import (
    adversarial_attractor,
    maximum_reach_probability,
    reachable_set,
    shortest_reach_avoid_path,
    strongly_connected_components,
)


def test_reachable_set_and_safe_shortest_path():
    adjacency = [[0, 1, 1, 0], [0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 0]]
    assert reachable_set(adjacency, [0]).tolist() == [True, True, True, True]
    costs = [[0.0, 1.0, 1.0, np.inf], [np.inf, 0.0, np.inf, 1.0], [np.inf, np.inf, 0.0, 0.2], [np.inf, np.inf, np.inf, 0.0]]
    path = shortest_reach_avoid_path(costs, 0, [3], [2])
    assert path.path == (0, 1, 3)
    assert np.isclose(path.cost, 2.0)


def test_scc_and_adversarial_attractor_identify_cycles_and_forced_reachability():
    adjacency = [[0, 1, 0], [1, 0, 1], [0, 0, 1]]
    assert strongly_connected_components(adjacency) == ((0, 1), (2,))
    successors = np.array([[[1, 1]], [[2, 2]], [[2, 2]]])
    attractor = adversarial_attractor(successors, [2])
    assert attractor.winning.tolist() == [True, True, True]
    assert attractor.rank.tolist() == [2, 1, 0]


def test_maximum_reach_probability_selects_better_action():
    transitions = np.array(
        [
            [[0.0, 0.5, 0.5], [0.0, 1.0, 0.0]],
            [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    values, policy = maximum_reach_probability(transitions, [1], [2])
    assert np.isclose(values[0], 1.0)
    assert policy[0] == 1
