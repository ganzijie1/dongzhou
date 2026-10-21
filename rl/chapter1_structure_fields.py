"""Hypergraph, battlefield-field, and finite-symmetry mathematics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class HypergraphGeometry:
    incidence: np.ndarray
    vertex_degrees: np.ndarray
    edge_degrees: np.ndarray
    laplacian: np.ndarray


def normalized_hypergraph_laplacian(
    vertex_count: int,
    hyperedges: Sequence[Sequence[int]],
    *,
    weights: Sequence[float] | None = None,
) -> HypergraphGeometry:
    """Build the Zhou normalized Laplacian of a weighted hypergraph."""

    if vertex_count <= 0:
        raise ValueError("hypergraph vertex count must be positive")
    edges = tuple(tuple(dict.fromkeys(int(vertex) for vertex in edge)) for edge in hyperedges)
    if not edges or any(not edge for edge in edges):
        raise ValueError("hypergraph edges must be non-empty")
    if any(vertex < 0 or vertex >= vertex_count for edge in edges for vertex in edge):
        raise ValueError("hypergraph edge contains an invalid vertex")
    edge_weights = np.ones(len(edges), dtype=np.float64)
    if weights is not None:
        edge_weights = np.asarray(weights, dtype=np.float64)
        if edge_weights.shape != (len(edges),):
            raise ValueError("hypergraph weights must align with edges")
    if np.any(~np.isfinite(edge_weights)) or np.any(edge_weights <= 0.0):
        raise ValueError("hypergraph weights must be positive and finite")

    incidence = np.zeros((vertex_count, len(edges)), dtype=np.float64)
    for column, edge in enumerate(edges):
        incidence[list(edge), column] = 1.0
    edge_degrees = incidence.sum(axis=0)
    vertex_degrees = incidence @ edge_weights
    inverse_vertex = np.zeros(vertex_count, dtype=np.float64)
    active = vertex_degrees > 0.0
    inverse_vertex[active] = 1.0 / np.sqrt(vertex_degrees[active])
    inverse_edge = 1.0 / edge_degrees
    diffusion = (
        inverse_vertex[:, None]
        * incidence
        * edge_weights[None, :]
        * inverse_edge[None, :]
    ) @ (incidence.T * inverse_vertex[None, :])
    laplacian = np.eye(vertex_count, dtype=np.float64) - diffusion
    # Isolated vertices have no diffusion relation and therefore zero energy.
    laplacian[~active, :] = 0.0
    laplacian[:, ~active] = 0.0
    return HypergraphGeometry(incidence, vertex_degrees, edge_degrees, laplacian)


def artificial_potential_force(
    position: Sequence[float],
    goals: Sequence[Sequence[float]],
    obstacles: Sequence[Sequence[float]],
    *,
    attraction: float = 1.0,
    repulsion: float = 1.0,
    influence_radius: float = 2.0,
) -> np.ndarray:
    """Return the negative gradient of an attractive-repulsive potential."""

    point = np.asarray(position, dtype=np.float64)
    targets = np.asarray(goals, dtype=np.float64)
    hazards = np.asarray(obstacles, dtype=np.float64)
    if point.ndim != 1 or point.size == 0:
        raise ValueError("potential-field position must be a non-empty vector")
    if targets.size == 0:
        targets = np.empty((0, point.size), dtype=np.float64)
    if hazards.size == 0:
        hazards = np.empty((0, point.size), dtype=np.float64)
    if targets.ndim != 2 or targets.shape[1] != point.size:
        raise ValueError("potential-field goals have invalid dimensions")
    if hazards.ndim != 2 or hazards.shape[1] != point.size:
        raise ValueError("potential-field obstacles have invalid dimensions")
    if any(np.any(~np.isfinite(array)) for array in (point, targets, hazards)):
        raise ValueError("potential-field coordinates must be finite")
    parameters = (attraction, repulsion, influence_radius)
    if any(not isfinite(value) or value < 0.0 for value in parameters[:2]):
        raise ValueError("potential-field gains must be finite and non-negative")
    if not isfinite(influence_radius) or influence_radius <= 0.0:
        raise ValueError("potential-field influence radius must be positive")

    force = attraction * np.sum(targets - point, axis=0)
    for obstacle in hazards:
        offset = point - obstacle
        distance = float(np.linalg.norm(offset))
        if distance <= 1e-12:
            raise ValueError("potential field is singular at an obstacle")
        if distance < influence_radius:
            force += (
                repulsion
                * (1.0 / distance - 1.0 / influence_radius)
                * offset
                / distance**3
            )
    return force


@dataclass(frozen=True)
class ReactionDiffusionResult:
    activator: np.ndarray
    inhibitor: np.ndarray
    activator_history: np.ndarray
    inhibitor_history: np.ndarray


def gray_scott_reaction_diffusion(
    initial_activator: Sequence[float],
    initial_inhibitor: Sequence[float],
    laplacian: Sequence[Sequence[float]],
    *,
    steps: int,
    time_step: float = 0.01,
    activator_diffusion: float = 0.16,
    inhibitor_diffusion: float = 0.08,
    feed_rate: float = 0.035,
    kill_rate: float = 0.065,
) -> ReactionDiffusionResult:
    """Integrate the Gray-Scott model over a graph or spatial mesh."""

    activator = np.asarray(initial_activator, dtype=np.float64).copy()
    inhibitor = np.asarray(initial_inhibitor, dtype=np.float64).copy()
    graph_laplacian = np.asarray(laplacian, dtype=np.float64)
    if activator.ndim != 1 or inhibitor.shape != activator.shape or not activator.size:
        raise ValueError("reaction-diffusion fields must be aligned vectors")
    if graph_laplacian.shape != (activator.size, activator.size):
        raise ValueError("reaction-diffusion Laplacian has invalid dimensions")
    arrays = (activator, inhibitor, graph_laplacian)
    if any(np.any(~np.isfinite(array)) for array in arrays):
        raise ValueError("reaction-diffusion inputs must be finite")
    parameters = (
        time_step,
        activator_diffusion,
        inhibitor_diffusion,
        feed_rate,
        kill_rate,
    )
    if steps < 0 or any(not isfinite(value) or value < 0.0 for value in parameters):
        raise ValueError("reaction-diffusion steps and parameters are invalid")

    activator_history = [activator.copy()]
    inhibitor_history = [inhibitor.copy()]
    for _ in range(steps):
        reaction = activator * inhibitor * inhibitor
        activator_rate = (
            -activator_diffusion * (graph_laplacian @ activator)
            - reaction
            + feed_rate * (1.0 - activator)
        )
        inhibitor_rate = (
            -inhibitor_diffusion * (graph_laplacian @ inhibitor)
            + reaction
            - (feed_rate + kill_rate) * inhibitor
        )
        activator = activator + time_step * activator_rate
        inhibitor = inhibitor + time_step * inhibitor_rate
        if np.any(~np.isfinite(activator)) or np.any(~np.isfinite(inhibitor)):
            raise FloatingPointError("reaction-diffusion integration diverged")
        activator_history.append(activator.copy())
        inhibitor_history.append(inhibitor.copy())
    return ReactionDiffusionResult(
        activator,
        inhibitor,
        np.asarray(activator_history),
        np.asarray(inhibitor_history),
    )


@dataclass(frozen=True)
class PhaseFieldResult:
    field: np.ndarray
    history: np.ndarray
    energies: tuple[float, ...]


def allen_cahn_phase_field(
    initial_field: Sequence[float],
    laplacian: Sequence[Sequence[float]],
    *,
    steps: int,
    time_step: float = 0.01,
    interface_width: float = 0.2,
) -> PhaseFieldResult:
    """Integrate an Allen-Cahn phase field over a graph or mesh."""

    field = np.asarray(initial_field, dtype=np.float64).copy()
    graph_laplacian = np.asarray(laplacian, dtype=np.float64)
    if field.ndim != 1 or not field.size:
        raise ValueError("phase field must be a non-empty vector")
    if graph_laplacian.shape != (field.size, field.size):
        raise ValueError("phase-field Laplacian has invalid dimensions")
    if np.any(~np.isfinite(field)) or np.any(~np.isfinite(graph_laplacian)):
        raise ValueError("phase-field inputs must be finite")
    if steps < 0 or time_step <= 0.0 or interface_width <= 0.0:
        raise ValueError("phase-field integration parameters are invalid")
    if not isfinite(time_step) or not isfinite(interface_width):
        raise ValueError("phase-field integration parameters must be finite")

    def energy(values: np.ndarray) -> float:
        interface = 0.5 * interface_width**2 * float(values @ graph_laplacian @ values)
        bulk = float(np.sum(0.25 * (values * values - 1.0) ** 2))
        return interface + bulk

    history = [field.copy()]
    energies = [energy(field)]
    for _ in range(steps):
        rate = -(interface_width**2) * (graph_laplacian @ field) + field - field**3
        field = field + time_step * rate
        if np.any(~np.isfinite(field)):
            raise FloatingPointError("phase-field integration diverged")
        history.append(field.copy())
        energies.append(energy(field))
    return PhaseFieldResult(field, np.asarray(history), tuple(energies))


def permutation_representation(permutations: Sequence[Sequence[int]]) -> tuple[np.ndarray, ...]:
    """Convert finite permutations into their orthogonal matrix representation."""

    if not permutations:
        raise ValueError("permutation representation needs group elements")
    size = len(permutations[0])
    expected = set(range(size))
    matrices = []
    for permutation in permutations:
        if len(permutation) != size or set(permutation) != expected:
            raise ValueError("each group element must be a full permutation")
        matrix = np.zeros((size, size), dtype=np.float64)
        for source, destination in enumerate(permutation):
            matrix[destination, source] = 1.0
        matrices.append(matrix)
    return tuple(matrices)


def invariant_group_average(
    features: Sequence[float], group_actions: Sequence[Sequence[Sequence[float]]]
) -> np.ndarray:
    """Project a feature vector onto the invariant subspace of a finite group."""

    vector = np.asarray(features, dtype=np.float64)
    actions = tuple(np.asarray(action, dtype=np.float64) for action in group_actions)
    if vector.ndim != 1 or not actions:
        raise ValueError("group average needs a vector and group actions")
    if any(action.shape != (vector.size, vector.size) for action in actions):
        raise ValueError("group action dimensions do not match the feature vector")
    if np.any(~np.isfinite(vector)) or any(np.any(~np.isfinite(action)) for action in actions):
        raise ValueError("group representation values must be finite")
    return np.mean([action @ vector for action in actions], axis=0)


def equivariant_linear_projection(
    linear_map: Sequence[Sequence[float]],
    input_actions: Sequence[Sequence[Sequence[float]]],
    output_actions: Sequence[Sequence[Sequence[float]]],
) -> np.ndarray:
    """Project a linear layer onto an equivariant finite-group representation."""

    weights = np.asarray(linear_map, dtype=np.float64)
    inputs = tuple(np.asarray(action, dtype=np.float64) for action in input_actions)
    outputs = tuple(np.asarray(action, dtype=np.float64) for action in output_actions)
    if weights.ndim != 2 or not inputs or len(inputs) != len(outputs):
        raise ValueError("equivariant projection needs paired group actions")
    output_size, input_size = weights.shape
    if any(action.shape != (input_size, input_size) for action in inputs):
        raise ValueError("input representation dimensions are invalid")
    if any(action.shape != (output_size, output_size) for action in outputs):
        raise ValueError("output representation dimensions are invalid")
    arrays = (weights,) + inputs + outputs
    if any(np.any(~np.isfinite(array)) for array in arrays):
        raise ValueError("equivariant projection inputs must be finite")
    if any(
        not np.allclose(action.T @ action, np.eye(action.shape[0]), atol=1e-9)
        for action in inputs + outputs
    ):
        raise ValueError("finite-group actions must be orthogonal representations")
    return np.mean(
        [output @ weights @ input.T for input, output in zip(inputs, outputs)],
        axis=0,
    )


def equivariance_error(
    function: Callable[[np.ndarray], Sequence[float]],
    samples: Sequence[Sequence[float]],
    input_actions: Sequence[Sequence[Sequence[float]]],
    output_actions: Sequence[Sequence[Sequence[float]]],
) -> float:
    """Measure max ||f(R_g x) - S_g f(x)|| over samples and group actions."""

    if len(input_actions) != len(output_actions) or not input_actions:
        raise ValueError("equivariance check needs paired group actions")
    worst = 0.0
    for sample in samples:
        vector = np.asarray(sample, dtype=np.float64)
        base = np.asarray(function(vector), dtype=np.float64)
        for input_action, output_action in zip(input_actions, output_actions):
            transformed = np.asarray(input_action, dtype=np.float64) @ vector
            left = np.asarray(function(transformed), dtype=np.float64)
            right = np.asarray(output_action, dtype=np.float64) @ base
            if left.shape != right.shape or np.any(~np.isfinite(left - right)):
                raise ValueError("equivariance function returned invalid values")
            worst = max(worst, float(np.linalg.norm(left - right)))
    return worst
