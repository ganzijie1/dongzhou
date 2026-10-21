import math

import numpy as np

from rl.p6_structure_math import (
    CellularSheaf,
    categorical_fisher_information,
    categorical_natural_gradient_step,
    discrete_morse_critical_points,
    discrete_reeb_graph,
    fisher_rao_distance,
    kl_divergence,
    matroid_greedy,
    max_plus_cycle_mean,
    max_plus_power,
    partition_matroid_oracle,
    schrodinger_bridge,
    submodular_matroid_greedy,
)


def test_cellular_sheaf_detects_and_diffuses_inconsistency():
    edge = ("left", "right")
    sheaf = CellularSheaf(
        {"left": 1, "right": 1},
        {edge: 1},
        {("left", edge): [[1.0]], ("right", edge): [[1.0]]},
    )
    assert np.allclose(sheaf.laplacian(), [[1.0, -1.0], [-1.0, 1.0]])
    assert sheaf.consistency_energy({"left": [2.0], "right": [2.0]}) == 0.0
    assert sheaf.global_sections().shape == (2, 1)
    before = sheaf.consistency_energy({"left": [0.0], "right": [2.0]})
    after_values = sheaf.diffuse({"left": [0.0], "right": [2.0]}, time=0.5)
    assert sheaf.consistency_energy(after_values) < before


def test_discrete_morse_and_reeb_graphs():
    adjacency = {
        "center": ("low-a", "low-b", "high-a", "high-b"),
        "low-a": ("center",),
        "low-b": ("center",),
        "high-a": ("center",),
        "high-b": ("center",),
    }
    values = {"low-a": 0.0, "low-b": 1.0, "center": 2.0, "high-a": 3.0, "high-b": 4.0}
    critical = {point.vertex: point for point in discrete_morse_critical_points(adjacency, values)}
    assert critical["center"].kind == "saddle"
    assert critical["center"].lower_components == 2
    assert critical["center"].upper_components == 2

    line = {"a": ("b",), "b": ("a", "c"), "c": ("b",)}
    reeb = discrete_reeb_graph(line, {"a": 0.0, "b": 0.0, "c": 1.0})
    assert len(reeb.nodes) == 2
    assert reeb.vertex_to_node["a"] == reeb.vertex_to_node["b"]
    assert reeb.edges == ((0, 1),)


def test_schrodinger_bridge_matches_both_marginals():
    result = schrodinger_bridge([0.6, 0.4], [0.3, 0.7], [[2.0, 1.0], [1.0, 3.0]])
    assert np.allclose(result.coupling.sum(axis=1), [0.6, 0.4])
    assert np.allclose(result.coupling.sum(axis=0), [0.3, 0.7])
    assert np.allclose(result.transition.sum(axis=1), 1.0)


def test_information_geometry_primitives():
    fisher = categorical_fisher_information([0.2, 0.3, 0.5])
    assert np.allclose(fisher.sum(axis=1), 0.0)
    assert math.isclose(fisher_rao_distance([0.2, 0.8], [0.2, 0.8]), 0.0, abs_tol=1e-12)
    assert math.isclose(kl_divergence([0.2, 0.8], [0.2, 0.8]), 0.0, abs_tol=1e-12)
    updated = categorical_natural_gradient_step([0.5, 0.5], [2.0, 0.0])
    assert updated[0] > updated[1]


def test_max_plus_cycle_and_power():
    matrix = np.array([[-np.inf, 1.0], [2.0, -np.inf]])
    assert np.allclose(np.diag(max_plus_power(matrix, 2)), 3.0)
    assert math.isclose(max_plus_cycle_mean(matrix), 1.5)


def test_weighted_and_submodular_matroid_greedy():
    items = ("a", "b", "c", "d")
    independent = partition_matroid_oracle(
        {"a": "front", "b": "front", "c": "rear", "d": "rear"},
        {"front": 1, "rear": 1},
    )
    weighted = matroid_greedy(items, {"a": 2.0, "b": 1.0, "c": 4.0, "d": 3.0}, independent)
    assert set(weighted.selected) == {"a", "c"}
    assert weighted.value == 6.0

    coverage = {"a": {1, 2}, "b": {2, 3}, "c": {3, 4}, "d": {4}}
    result = submodular_matroid_greedy(
        items,
        lambda chosen: float(len(set().union(*(coverage[item] for item in chosen))) if chosen else 0),
        independent,
    )
    assert independent(frozenset(result.selected))
    assert result.value >= 3.0
