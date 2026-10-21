"""Tests for hex grids, digital topology, formations, and tactical geometry."""

from __future__ import annotations

from math import inf, isclose

from rl.discrete_geometry import (
    FormationGeometry,
    GridGeometry,
    HexCoordinate,
    OccupancyGeometry,
    RegionAnalysis,
    TacticalGeometry,
    VisibilityGeometry,
)
from rl.lattice_geometry import LatticeShape
from rl.mengde_env import MengdeEnv
from rl.random_geometry import LatticeGraph


def test_hex_coordinates_and_multilevel_adjacency() -> None:
    assert len(HexCoordinate.neighbors((0, 0))) == 6
    assert HexCoordinate.distance((0, 0), (2, -1)) == 2
    assert len(HexCoordinate.ball((0, 0), 2)) == 19
    assert len(HexCoordinate.ring((0, 0), 2)) == 12
    cell = (2, -1)
    rotated = cell
    for _ in range(6):
        rotated = HexCoordinate.rotate_sixth(rotated)
    assert rotated == cell

    neighbors = GridGeometry.neighbors3d(
        (1, 1, 1), lambda source, target: target[2] >= source[2]
    )
    assert (1, 1, 0) not in neighbors and (1, 1, 2) in neighbors


def test_occupancy_anchors_overlap_and_maximum_empty_cells() -> None:
    domain = {(x, y) for x in range(4) for y in range(2)}
    footprint = LatticeShape.from_cells({(0, 0), (1, 0)})
    anchors = OccupancyGeometry.legal_anchors(domain, {(2, 1)}, footprint)
    assert (0, 0) in anchors and (1, 1) not in anchors and (3, 0) not in anchors
    assert OccupancyGeometry.placements_overlap((0, 0), footprint, (1, 0), footprint)
    assert not OccupancyGeometry.placements_overlap(
        (0, 0), footprint, (2, 0), footprint
    )
    square = {(x, y) for x in range(5) for y in range(5)}
    radius, centers = OccupancyGeometry.maximum_empty_cells(square, {(0, 0)})
    assert radius == 2 and centers == frozenset({(2, 2)})
    assert (
        OccupancyGeometry.maximum_empty_cells({(0, 0)}, (), include_boundary=False)[0]
        == inf
    )


def test_visibility_cover_and_directional_line_attack() -> None:
    visible = VisibilityGeometry.field_of_view(
        (0, 0),
        (1.0, 0.0),
        3,
        45,
        lambda cell: cell == (1, 0),
    )
    assert (1, 0) not in visible and (2, 0) not in visible
    assert (0, 0) in visible
    cover = VisibilityGeometry.cover_strength(
        (0, 0), (3, 0), {(1, 0): 0.5, (2, 0): 1.0}
    )
    assert cover == 1.5
    line = VisibilityGeometry.line_attack_cells((0, 0), (1.0, 0.0), 3, 0)
    assert line == frozenset({(0, 0), (1, 0), (2, 0), (3, 0)})


def test_articulation_bridges_holes_and_euler_characteristic() -> None:
    corridor = {(0, 0), (1, 0), (2, 0)}
    assert RegionAnalysis.articulation_points(corridor) == frozenset({(1, 0)})
    assert RegionAnalysis.bridges(corridor) == frozenset(
        {((0, 0), (1, 0)), ((1, 0), (2, 0))}
    )
    long_corridor = {(x, 0) for x in range(2000)}
    assert len(RegionAnalysis.articulation_points(long_corridor)) == 1998
    assert len(RegionAnalysis.bridges(long_corridor)) == 1999

    ring = {(x, y) for x in range(3) for y in range(3)} - {(1, 1)}
    holes = RegionAnalysis.holes(ring)
    assert holes == (frozenset({(1, 1)}),)
    assert RegionAnalysis.euler_characteristic(ring) == 0
    disconnected = {(0, 0), (3, 0)}
    assert RegionAnalysis.euler_characteristic(disconnected) == 2


def test_orthogonal_convexity_skeleton_width_and_chokepoints() -> None:
    rectangle = {(x, y) for x in range(5) for y in range(3)}
    assert RegionAnalysis.is_orthogonally_convex(rectangle)
    split_row = {(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)}
    assert not RegionAnalysis.is_orthogonally_convex(split_row)
    skeleton = RegionAnalysis.skeleton(rectangle)
    assert {(1, 1), (2, 1), (3, 1)} <= skeleton
    widths = RegionAnalysis.local_width(rectangle)
    assert widths[(2, 1)] == 3 and widths[(0, 0)] == 1
    assert (2, 1) in RegionAnalysis.chokepoints(rectangle, 3)


def test_weighted_voronoi_moves_control_boundary() -> None:
    graph = LatticeGraph.from_size(5, 1)
    sites = ((0, 0), (4, 0))
    regions = RegionAnalysis.weighted_voronoi(
        graph.cells, sites, graph.distance, {(4, 0): 2.0}
    )
    assert regions[(0, 0)] == frozenset({(0, 0), (1, 0)})
    assert regions[(4, 0)] == frozenset({(2, 0), (3, 0), (4, 0)})


def test_formation_descriptor_surround_and_flank() -> None:
    descriptor = FormationGeometry.describe(((-1, 0), (0, 0), (1, 0)))
    assert descriptor.centroid == (0.0, 0.0)
    assert isclose(descriptor.dispersion, 2 / 3)
    assert descriptor.principal_direction == (1.0, 0.0)
    assert descriptor.closest_distance == 1.0
    try:
        FormationGeometry.describe(((0, 0),), ())
        raise AssertionError("empty explicit weights unexpectedly used equal weights")
    except ValueError:
        pass
    assert FormationGeometry.surrounds((0, 0), ((-1, -1), (1, -1), (1, 1), (-1, 1)))
    assert not FormationGeometry.surrounds((3, 0), ((-1, -1), (1, -1), (1, 1), (-1, 1)))
    assert FormationGeometry.flank_angle((0, 0), (-1, 0), (1, 0)) == 180.0


def test_best_aoe_probability_union_and_risk_cost() -> None:
    result = TacticalGeometry.best_aoe(
        ((1, 0), (2, 0)),
        LatticeShape.manhattan_ball(1),
        {(0, 0): 1.0, (1, 0): 2.0, (2, 0): 3.0},
        {(1, 1): 10.0},
    )
    assert result is not None
    assert result.center == (2, 0) and result.score == 5.0
    combined = TacticalGeometry.combined_threat_probability(
        ({(0, 0): 0.5}, {(0, 0): 0.2}), {(0, 0), (1, 0)}
    )
    assert isclose(combined[(0, 0)], 0.6)
    assert combined[(1, 0)] == 0.0
    assert TacticalGeometry.risk_weighted_cost({(0, 0): 2.0}, combined, 3.0) == {
        (0, 0): 3.8
    }


def test_environment_adapter_analyzes_native_passability() -> None:
    env = object.__new__(MengdeEnv)
    env.map_info = lambda: {"width": 5, "height": 3}
    env.movement_costs = lambda unit_id: [1, 1, 255, 1, 1] * 3
    analysis = env.analyze_discrete_map(1)
    assert analysis["traversable_cells"] == 12
    assert analysis["component_count"] == 2
    assert analysis["hole_count"] == 0
    assert analysis["euler_characteristic"] == 2


def main() -> None:
    test_hex_coordinates_and_multilevel_adjacency()
    test_occupancy_anchors_overlap_and_maximum_empty_cells()
    test_visibility_cover_and_directional_line_attack()
    test_articulation_bridges_holes_and_euler_characteristic()
    test_orthogonal_convexity_skeleton_width_and_chokepoints()
    test_weighted_voronoi_moves_control_boundary()
    test_formation_descriptor_surround_and_flank()
    test_best_aoe_probability_union_and_risk_cost()
    test_environment_adapter_analyzes_native_passability()
    print("discrete geometry ok: topology, visibility, formations, and tactics")


if __name__ == "__main__":
    main()
