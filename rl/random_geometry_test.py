"""Tests for graph-aware point processes and constrained deployments."""

from __future__ import annotations

from math import inf, isclose
from random import Random

from rl.lattice_geometry import LatticeShape
from rl.mengde_env import MengdeEnv
from rl.random_geometry import (
    DeploymentError,
    LatticeGraph,
    MarkedPoint,
    RandomDeploymentGenerator,
    RandomGeometryStatistics,
    assign_marks,
    cooldown_reinforcement_intensity,
    coverage_fraction,
    coverage_multiplicity,
    delaunay_adjacency,
    deployment_metrics,
    graph_component_count,
    graph_voronoi,
    heterogeneous_matern_type_ii,
    log_linear_intensity,
    matern_type_ii,
    monte_carlo_envelope,
    random_geometric_graph,
    safe_corridor_exists,
    weighted_sample_without_replacement,
)


def test_graph_distance_respects_walls_and_directional_costs() -> None:
    graph = LatticeGraph.from_size(5, 3, blocked={(2, 1)})
    assert graph.distance((0, 1), (4, 1)) == 6
    assert graph.ball((0, 1), 1) == frozenset({(0, 0), (0, 1), (0, 2), (1, 1)})

    split = LatticeGraph.from_size(3, 2, blocked={(1, 0), (1, 1)})
    assert split.distance((0, 0), (2, 0)) == inf

    weighted = LatticeGraph(
        LatticeGraph.from_size(3, 1).cells,
        edge_costs={((0, 0), (1, 0)): 4.0},
    )
    assert weighted.distance((0, 0), (2, 0)) == 5.0
    assert weighted.distance((2, 0), (0, 0)) == 2.0


def test_weighted_sampling_and_matern_are_seed_reproducible() -> None:
    cells = {(x, 0) for x in range(8)}
    weights = {cell: (10.0 if cell == (7, 0) else 1.0) for cell in cells}
    first = weighted_sample_without_replacement(cells, weights, 4, Random(7))
    second = weighted_sample_without_replacement(cells, weights, 4, Random(7))
    assert first == second

    graph = LatticeGraph.from_size(8, 1)
    retained = matern_type_ii(cells, graph.distance, 2.0, Random(11))
    assert retained
    assert all(
        graph.distance(left, right) >= 2.0
        for index, left in enumerate(retained)
        for right in retained[index + 1 :]
    )


def test_heterogeneous_hard_core_and_joint_marks() -> None:
    graph = LatticeGraph.from_size(7, 1)
    candidates = (
        MarkedPoint((0, 0), "siege", 1.5),
        MarkedPoint((2, 0), "guard", 1.0),
        MarkedPoint((5, 0), "archer", 0.5),
    )
    retained = heterogeneous_matern_type_ii(candidates, graph.distance, None, Random(3))
    assert all(
        graph.distance(left.cell, right.cell) >= left.radius + right.radius
        for index, left in enumerate(retained)
        for right in retained[index + 1 :]
    )

    marked = assign_marks(
        tuple((x, 0) for x in range(4)),
        {"archer": 2, "guard": 2},
        {
            "archer": {(x, 0): x + 1 for x in range(4)},
            "guard": {(x, 0): 4 - x for x in range(4)},
        },
        Random(9),
        {"archer": 0.5, "guard": 1.0},
    )
    assert sum(point.mark == "archer" for point in marked) == 2
    assert sum(point.mark == "guard" for point in marked) == 2


def test_contact_k_coverage_and_safe_corridor_statistics() -> None:
    graph = LatticeGraph.from_size(5, 3)
    points = ((0, 1), (4, 1))
    summary = RandomGeometryStatistics.nearest_neighbor_summary(points, graph.distance)
    assert summary == {"minimum": 4.0, "p10": 4.0, "mean": 4.0}

    radii = (0.0, 2.0, 4.0)
    contact = RandomGeometryStatistics.contact_distribution(
        graph.cells, points, radii, graph.distance
    )
    nearest = RandomGeometryStatistics.nearest_neighbor_cdf(
        points, radii, graph.distance
    )
    j_value = RandomGeometryStatistics.j_function(contact, nearest)
    assert isclose(contact[0.0], 2 / 15)
    assert nearest[2.0] == 0.0 and nearest[4.0] == 1.0
    assert j_value[0.0] > 1.0

    ripley = RandomGeometryStatistics.ripley_k(
        points, radii, graph.distance, len(graph.cells)
    )
    cross = RandomGeometryStatistics.cross_k(
        ((0, 1),), ((4, 1),), radii, graph.distance, len(graph.cells)
    )
    assert ripley[4.0] == 15.0 and cross[4.0] == 15.0
    pair_correlation = RandomGeometryStatistics.pair_correlation(
        ((0, 1), (1, 1), (4, 1)),
        (((0, 1), (2, 1), (4, 1)),),
        (1.0, 2.0, 4.0),
        graph.distance,
    )
    assert pair_correlation[1.0] == inf
    assert pair_correlation[2.0] < 1.0

    influence = LatticeShape.manhattan_ball(1)
    coverage = coverage_multiplicity(graph.cells, ((1, 1), (3, 1)), influence)
    assert coverage[(2, 1)] == 2
    assert coverage_fraction(coverage, 2) == 1 / 15

    open_coverage = coverage_multiplicity(
        graph.cells, ((2, 1),), LatticeShape.from_cells({(0, 0)})
    )
    assert safe_corridor_exists(graph, {(0, 1)}, {(4, 1)}, open_coverage)
    blocked_coverage = coverage_multiplicity(
        graph.cells,
        ((2, 0), (2, 1), (2, 2)),
        LatticeShape.from_cells({(0, 0)}),
    )
    assert not safe_corridor_exists(graph, {(0, 1)}, {(4, 1)}, blocked_coverage)


def test_voronoi_delaunay_and_random_geometric_graph() -> None:
    graph = LatticeGraph.from_size(5, 1)
    sites = ((0, 0), (4, 0))
    regions = graph_voronoi(graph, sites)
    assert regions[(0, 0)] == frozenset({(0, 0), (1, 0), (2, 0)})
    assert regions[(4, 0)] == frozenset({(3, 0), (4, 0)})
    assert delaunay_adjacency(graph, sites) == frozenset({((0, 0), (4, 0))})

    points = ((0, 0), (2, 0), (4, 0))
    edges = random_geometric_graph(points, 2.0, graph.distance)
    assert graph_component_count(points, edges) == 1
    metrics = deployment_metrics(graph, points, 2.0)
    assert metrics.minimum_nearest_neighbor == 2.0
    assert metrics.component_count == 1
    assert isclose(metrics.mean_degree, 4 / 3)


def test_deployment_pipeline_enforces_spacing_forbidden_and_validators() -> None:
    graph = LatticeGraph.from_size(10, 3)
    weights = {cell: 1.0 + cell[0] for cell in graph.cells}

    def stays_out_of_last_column(layout: tuple[tuple[int, int], ...]) -> bool:
        return all(cell[0] < 9 for cell in layout)

    generator = RandomDeploymentGenerator(graph, 2026)
    first = generator.generate(
        5,
        weights,
        minimum_distance=2.0,
        forbidden={(0, 0), (1, 0)},
        validators=(stays_out_of_last_column,),
        max_attempts=128,
    )
    second = generator.generate(
        5,
        weights,
        minimum_distance=2.0,
        forbidden={(0, 0), (1, 0)},
        validators=(stays_out_of_last_column,),
        max_attempts=128,
    )
    assert first == second
    assert not (set(first.cells) & {(0, 0), (1, 0)})
    assert all(cell[0] < 9 for cell in first.cells)
    assert all(
        graph.distance(left, right) >= 2.0
        for index, left in enumerate(first.cells)
        for right in first.cells[index + 1 :]
    )

    try:
        RandomDeploymentGenerator(graph, 1).generate(1, {})
        raise AssertionError("empty intensity unexpectedly generated a deployment")
    except DeploymentError as error:
        assert "positive-intensity" in str(error)

    def always_reject(layout: tuple[tuple[int, int], ...]) -> bool:
        return False

    try:
        RandomDeploymentGenerator(graph, 1).generate(
            1, weights, validators=(always_reject,), max_attempts=3
        )
        raise AssertionError("rejecting validator unexpectedly accepted a deployment")
    except DeploymentError as error:
        assert "always_reject=3" in str(error)


def test_monte_carlo_intensity_and_reinforcement_cooldown() -> None:
    envelope = monte_carlo_envelope(
        (
            {"coverage": 0.1, "spacing": 2.0},
            {"coverage": 0.2, "spacing": 3.0},
            {"coverage": 0.3, "spacing": 4.0},
        ),
        0.0,
        1.0,
    )
    assert envelope["coverage"] == (0.1, 0.2, 0.3)
    intensity = log_linear_intensity(
        {(0, 0): {"road": 0.0}, (1, 0): {"road": 1.0}},
        {"road": 1.0},
    )
    assert intensity[(1, 0)] > intensity[(0, 0)]
    reinforcement = cooldown_reinforcement_intensity(
        {(0, 0): 1.0, (1, 0): 2.0},
        1.5,
        current_time=5,
        last_used={(0, 0): 4},
        cooldown=2,
    )
    assert reinforcement == {(0, 0): 0.0, (1, 0): 3.0}


def test_environment_adapter_uses_native_costs_and_current_occupancy() -> None:
    env = object.__new__(MengdeEnv)
    env.map_info = lambda: {"width": 6, "height": 2}
    env.movement_costs = lambda unit_id: [1, 1, 255, 1, 1, 1] * 2
    env.unit_info = lambda: [
        {"id": 1, "x": 0, "y": 0, "dead": False},
        {"id": 2, "x": 5, "y": 1, "dead": True},
    ]
    first = env.sample_random_deployment(
        1, 3, 17, minimum_distance=2.0, protected={(1, 0)}
    )
    second = env.sample_random_deployment(
        1, 3, 17, minimum_distance=2.0, protected={(1, 0)}
    )
    assert first == second
    assert (0, 0) not in first.cells and (1, 0) not in first.cells
    assert all(cell[0] != 2 for cell in first.cells)


def main() -> None:
    test_graph_distance_respects_walls_and_directional_costs()
    test_weighted_sampling_and_matern_are_seed_reproducible()
    test_heterogeneous_hard_core_and_joint_marks()
    test_contact_k_coverage_and_safe_corridor_statistics()
    test_voronoi_delaunay_and_random_geometric_graph()
    test_deployment_pipeline_enforces_spacing_forbidden_and_validators()
    test_monte_carlo_intensity_and_reinforcement_cooldown()
    test_environment_adapter_uses_native_costs_and_current_occupancy()
    print("random geometry ok: processes, coverage, graphs, deployment, Monte Carlo")


if __name__ == "__main__":
    main()
