import math

import numpy as np
import pytest

from rl.advanced_lattice_geometry import (
    DiscreteFieldCalculus,
    anisotropic_geodesic_distance,
    lattice_topology_signature,
    morphological_reconstruction,
    signed_euclidean_distance,
    solve_lattice_poisson,
    topology_preserving_thinning,
)
from rl.lattice_geometry import LatticeRegion


def test_discrete_calculus_on_affine_and_impulse_fields():
    affine = {(x, y): 2.0 * x - 3.0 * y for x in range(3) for y in range(3)}
    gradient = DiscreteFieldCalculus.gradient(affine)
    assert gradient[(1, 1)] == (2.0, -3.0)
    assert math.isclose(
        DiscreteFieldCalculus.graph_laplacian(affine)[(1, 1)], 0.0
    )
    constant = {cell: 4.0 for cell in affine}
    assert DiscreteFieldCalculus.dirichlet_energy(constant) == 0.0


def test_lattice_poisson_respects_boundary_and_residual():
    result = solve_lattice_poisson(
        {(0, 0), (1, 0), (2, 0)},
        {(1, 0): 1.0},
        {(0, 0): 0.0, (2, 0): 0.0},
    )
    assert math.isclose(result.values[(1, 0)], 0.5)
    assert result.maximum_residual < 1e-12
    with pytest.raises(ValueError, match="every Poisson connected component"):
        solve_lattice_poisson(
            {(0, 0), (1, 0), (8, 0)},
            {},
            {(0, 0): 0.0},
        )


def test_anisotropic_geodesic_uses_metric_and_recovers_path():
    domain = {(x, y) for x in range(3) for y in range(2)}
    metrics = {cell: np.diag([4.0, 1.0]) for cell in domain}
    result = anisotropic_geodesic_distance(domain, {(0, 0)}, metrics, connectivity=4)
    assert math.isclose(result.distances[(2, 0)], 4.0)
    assert result.path_to((2, 0)) == ((0, 0), (1, 0), (2, 0))


def test_signed_distance_and_morphological_reconstruction():
    domain = {(x, 0) for x in range(6)}
    signed = signed_euclidean_distance(domain, {(1, 0), (2, 0)})
    assert signed[(1, 0)] == 1.0
    assert signed[(0, 0)] == -1.0
    mask = {(0, 0), (1, 0), (2, 0), (8, 0), (9, 0)}
    assert morphological_reconstruction({(0, 0)}, mask) == frozenset({(0, 0), (1, 0), (2, 0)})


def test_thinning_reduces_region_without_changing_component_count():
    block = {(x, y) for x in range(7) for y in range(5)}
    skeleton = topology_preserving_thinning(block)
    assert 0 < len(skeleton) < len(block)
    assert len(LatticeRegion.connected_components(skeleton, 8)) == 1


def test_lattice_topology_signature_detects_hole():
    ring = {(x, y) for x in range(3) for y in range(3)} - {(1, 1)}
    signature = lattice_topology_signature(ring)
    assert signature.area == 8
    assert signature.perimeter == 16
    assert signature.components == 1
    assert signature.holes == 1
    assert signature.euler_characteristic == 0
