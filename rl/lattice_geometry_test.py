"""Boundary and integration tests for the shared lattice-geometry contract."""

from __future__ import annotations

from math import isclose, pi, sqrt

from rl.lattice_geometry import (
    DiagonalPolicy,
    LatticeCoordinate,
    LatticeRay,
    LatticeRegion,
    LatticeShape,
    SpaceTimeGrid,
    weighted_shortest_path,
)


def test_coordinate_conversion_and_metrics() -> None:
    assert LatticeCoordinate.world_to_cell((-0.01, -1.0)) == (-1, -1)
    assert LatticeCoordinate.world_to_cell((12.9, 8.1), (2.0, 2.0), (10.0, 4.0)) == (1, 2)
    assert LatticeCoordinate.cell_center((1, 2), (2.0, 2.0), (10.0, 4.0)) == (13.0, 9.0)
    assert LatticeCoordinate.manhattan((0, 0), (2, 3)) == 5
    assert LatticeCoordinate.chebyshev((0, 0), (2, 3)) == 3
    assert isclose(LatticeCoordinate.euclidean((0, 0), (3, 4)), 5.0)
    assert isclose(LatticeCoordinate.octile((0, 0), (2, 3)), 1 + 2 * sqrt(2))
    assert LatticeCoordinate.primitive_direction((1, 1), (7, 4)) == (2, 1)
    assert LatticeCoordinate.segment_lattice_points((1, 1), (7, 4)) == (
        (1, 1),
        (3, 2),
        (5, 3),
        (7, 4),
    )


def test_diagonal_corner_policy() -> None:
    blocked = {(1, 0)}

    def passable(cell: tuple[int, int]) -> bool:
        return cell not in blocked

    strict = LatticeCoordinate.neighbors8(
        (0, 0), passable, DiagonalPolicy.BOTH_CLEAR
    )
    loose = LatticeCoordinate.neighbors8(
        (0, 0), passable, DiagonalPolicy.ONE_CLEAR
    )
    assert (1, 1) not in strict
    assert (1, 1) in loose
    assert (1, 0) not in loose


def test_shape_transforms_morphology_and_footprints() -> None:
    assert len(LatticeShape.manhattan_ball(2).cells) == 13
    assert len(LatticeShape.chebyshev_ball(2).cells) == 25
    assert len(LatticeShape.euclidean_ball(1).cells) == 5
    ring = LatticeShape.ring(1, 2)
    assert (0, 0) not in ring.cells and (1, 0) in ring.cells

    shape = LatticeShape.from_cells(((0, 0), (1, 0)))
    assert shape.rotate_quarter().cells == frozenset(((0, 0), (0, 1)))
    assert shape.translate((2, 3)).cells == frozenset(((2, 3), (3, 3)))
    assert shape.occupied((4, 5)) == frozenset(((4, 5), (5, 5)))
    assert shape.overlaps((4, 5), {(5, 5)})

    forbidden = LatticeShape.configuration_obstacles({(3, 0)}, shape)
    assert forbidden.cells == frozenset(((2, 0), (3, 0)))
    square = LatticeShape.chebyshev_ball(1)
    assert square.erode(LatticeShape.manhattan_ball(1)).cells == frozenset({(0, 0)})
    cross = LatticeShape.manhattan_ball(1)
    noisy = cross.union(LatticeShape.from_cells({(5, 5)}))
    assert noisy.opening(cross) == cross
    gapped = LatticeShape.from_cells({(0, 0), (2, 0)})
    horizontal = LatticeShape.from_cells({(0, 0), (1, 0)})
    assert gapped.closing(horizontal).cells == frozenset({(0, 0), (1, 0), (2, 0)})
    assert (0, 0) not in square.morphological_gradient(cross).cells
    east = LatticeShape.sector(2, (1.0, 0.0), 45)
    assert (2, 0) in east.cells and (-1, 0) not in east.cells


def test_rays_use_conservative_supercover() -> None:
    assert LatticeRay.bresenham((0, 0), (3, 1)) == ((0, 0), (1, 0), (2, 1), (3, 1))
    diagonal = LatticeRay.supercover((0, 0), (1, 1))
    assert set(diagonal) == {(0, 0), (1, 0), (0, 1), (1, 1)}
    assert not LatticeRay.line_of_sight((0, 0), (1, 1), lambda cell: cell == (1, 0))
    assert LatticeRay.line_of_sight(
        (0, 0), (1, 1), lambda cell: cell == (1, 1), include_end=False
    )
    heights = {(0, 0): 1.0, (1, 0): 2.0, (2, 0): 1.0}
    assert not LatticeRay.height_visible((0, 0), (2, 0), heights.__getitem__)


def test_regions_pick_ehrhart_and_clearance() -> None:
    cells = {(0, 0), (1, 0), (1, 1), (8, 8)}
    components = LatticeRegion.connected_components(cells)
    assert {len(component) for component in components} == {1, 3}
    block = {(x, y) for x in range(3) for y in range(3)}
    assert LatticeRegion.perimeter(block) == 12
    assert isclose(LatticeRegion.compactness(block), pi / 4)
    transform = LatticeRegion.distance_transform(block, LatticeRegion.boundary(block))
    assert transform[(1, 1)] == 1

    polygon = ((0, 0), (2, 0), (2, 2), (0, 2))
    assert LatticeRegion.convex_hull(polygon + ((1, 1),)) == polygon
    assert LatticeRegion.polygon_double_area(polygon) == 8
    assert LatticeRegion.polygon_boundary_points(polygon) == 8
    assert LatticeRegion.pick_interior_points(polygon) == 1
    assert LatticeRegion.ehrhart_count(polygon, 2) == 25


def test_space_time_reservations_reject_vertex_swap_and_late_arrival() -> None:
    grid = SpaceTimeGrid()
    assert grid.reserve_path(((0, 0), (1, 0), (2, 0)), 1, 4)
    assert grid.path_conflict(((0, 1), (1, 0), (1, 1)), 2, 4)

    swap = SpaceTimeGrid()
    assert swap.reserve_path(((0, 0), (1, 0)), 1, 2)
    assert swap.path_conflict(((1, 0), (0, 0)), 2, 2)
    assert swap.path_conflict(((2, 0), (2, 0), (1, 0)), 2, 2)
    assert not swap.reserve_path(((1, 0), (0, 0)), 2, 2)
    assert swap.copy().vertices == swap.vertices


def test_weighted_shortest_path_uses_shared_four_neighbors() -> None:
    costs = [1, 10, 1, 1, 1, 1]
    path = weighted_shortest_path((0, 0), (2, 0), 3, 2, costs)
    assert path == ((0, 0), (0, 1), (1, 1), (2, 1), (2, 0))
    assert weighted_shortest_path((0, 0), (2, 0), 3, 1, (1, 255, 1)) == ()


def main() -> None:
    test_coordinate_conversion_and_metrics()
    test_diagonal_corner_policy()
    test_shape_transforms_morphology_and_footprints()
    test_rays_use_conservative_supercover()
    test_regions_pick_ehrhart_and_clearance()
    test_space_time_reservations_reject_vertex_swap_and_late_arrival()
    test_weighted_shortest_path_uses_shared_four_neighbors()
    print("lattice geometry ok: coordinates, shapes, rays, regions, and space-time")


if __name__ == "__main__":
    main()
