"""Finite-dimensional quantum tactics for the lattice battle planner.

The module deliberately keeps quantum state local to selected units.  Classical
rules remain authoritative after measurement, so native movement legality,
occupancy, combat resolution, and replay stay deterministic and auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, sqrt
from typing import Any, Generic, Hashable, Iterable, Mapping, Sequence, TypeVar

import numpy as np

from rl.lattice_geometry import Cell, LatticeCoordinate


Basis = TypeVar("Basis", bound=Hashable)


class QuantumStateError(ValueError):
    """Raised when a state or operation violates a quantum invariant."""


@dataclass(frozen=True)
class MeasurementResult(Generic[Basis]):
    outcome: Basis
    probability: float
    roll: float


@dataclass(frozen=True)
class RegionMeasurementResult:
    detected: bool
    probability: float
    roll: float


@dataclass(frozen=True)
class QuantumReplayEvent:
    turn: int
    unit_id: int
    kind: str
    probabilities_before: tuple[tuple[Hashable, float], ...]
    probabilities_after: tuple[tuple[Hashable, float], ...]
    outcome: Hashable | bool | None = None
    roll: float | None = None


class QuantumState(Generic[Basis]):
    """Density-matrix state on a small, explicitly enumerated basis."""

    def __init__(
        self,
        basis: Sequence[Basis],
        density: np.ndarray,
        *,
        tolerance: float = 1e-9,
    ) -> None:
        self._basis = tuple(basis)
        if not self._basis:
            raise QuantumStateError("quantum basis cannot be empty")
        if len(set(self._basis)) != len(self._basis):
            raise QuantumStateError("quantum basis entries must be unique")
        self._index = {value: index for index, value in enumerate(self._basis)}
        self._tolerance = float(tolerance)
        self._density = np.asarray(density, dtype=np.complex128).copy()
        self._validate_density()

    @classmethod
    def from_amplitudes(
        cls,
        amplitudes: Mapping[Basis, complex],
        *,
        tolerance: float = 1e-9,
    ) -> "QuantumState[Basis]":
        if not amplitudes:
            raise QuantumStateError("at least one amplitude is required")
        basis = tuple(amplitudes)
        vector = np.asarray([amplitudes[value] for value in basis], dtype=np.complex128)
        norm = float(np.vdot(vector, vector).real)
        if not isfinite(norm) or norm <= tolerance:
            raise QuantumStateError("amplitudes must have a finite non-zero norm")
        vector /= sqrt(norm)
        return cls(basis, np.outer(vector, vector.conj()), tolerance=tolerance)

    @classmethod
    def localized(cls, basis_state: Basis) -> "QuantumState[Basis]":
        return cls.from_amplitudes({basis_state: 1.0 + 0.0j})

    @property
    def basis(self) -> tuple[Basis, ...]:
        return self._basis

    @property
    def density(self) -> np.ndarray:
        return self._density.copy()

    @property
    def purity(self) -> float:
        return float(np.trace(self._density @ self._density).real)

    @property
    def coherence(self) -> float:
        diagonal = np.diag(np.diag(self._density))
        return float(np.sum(np.abs(self._density - diagonal)))

    def copy(self) -> "QuantumState[Basis]":
        return QuantumState(self._basis, self._density, tolerance=self._tolerance)

    def probabilities(self) -> dict[Basis, float]:
        values = np.clip(np.diag(self._density).real, 0.0, None)
        total = float(values.sum())
        if total <= self._tolerance:
            raise QuantumStateError("state has no measurable probability")
        return {
            basis_state: float(value / total)
            for basis_state, value in zip(self._basis, values)
        }

    def expected_value(self, values: Mapping[Basis, float]) -> float:
        return sum(
            probability * float(values.get(basis_state, 0.0))
            for basis_state, probability in self.probabilities().items()
        )

    def apply_unitary(self, operator: np.ndarray) -> None:
        matrix = np.asarray(operator, dtype=np.complex128)
        dimension = len(self._basis)
        if matrix.shape != (dimension, dimension):
            raise QuantumStateError("unitary dimension does not match quantum basis")
        identity = np.eye(dimension, dtype=np.complex128)
        if not np.allclose(matrix.conj().T @ matrix, identity, atol=1e-8):
            raise QuantumStateError("operator is not unitary")
        self._density = matrix @ self._density @ matrix.conj().T
        self._stabilize()

    def apply_filter(self, operator: np.ndarray) -> float:
        """Apply and normalize a non-unitary operation, returning its probability."""
        matrix = np.asarray(operator, dtype=np.complex128)
        dimension = len(self._basis)
        if matrix.shape != (dimension, dimension):
            raise QuantumStateError("filter dimension does not match quantum basis")
        filtered = matrix @ self._density @ matrix.conj().T
        probability = float(np.trace(filtered).real)
        if not isfinite(probability) or probability <= self._tolerance:
            raise QuantumStateError("quantum filter has zero probability")
        self._density = filtered / probability
        self._stabilize()
        return probability

    def apply_channel(self, operators: Sequence[np.ndarray]) -> None:
        """Apply a completely positive trace-preserving Kraus channel."""
        if not operators:
            raise QuantumStateError("quantum channel needs at least one operator")
        dimension = len(self._basis)
        completeness = np.zeros((dimension, dimension), dtype=np.complex128)
        evolved = np.zeros_like(self._density)
        for operator in operators:
            matrix = np.asarray(operator, dtype=np.complex128)
            if matrix.shape != (dimension, dimension):
                raise QuantumStateError("channel dimension does not match quantum basis")
            completeness += matrix.conj().T @ matrix
            evolved += matrix @ self._density @ matrix.conj().T
        if not np.allclose(
            completeness, np.eye(dimension, dtype=np.complex128), atol=1e-8
        ):
            raise QuantumStateError("Kraus operators are not trace preserving")
        self._density = evolved
        self._stabilize()

    def evolve(self, hamiltonian: np.ndarray, delta_time: float = 1.0) -> None:
        matrix = np.asarray(hamiltonian, dtype=np.complex128)
        dimension = len(self._basis)
        if matrix.shape != (dimension, dimension):
            raise QuantumStateError("Hamiltonian dimension does not match quantum basis")
        if not np.allclose(matrix, matrix.conj().T, atol=1e-9):
            raise QuantumStateError("Hamiltonian must be Hermitian")
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        phases = np.exp(-1j * eigenvalues * float(delta_time))
        operator = (eigenvectors * phases) @ eigenvectors.conj().T
        self.apply_unitary(operator)

    def phase_shift(self, phases: Mapping[Basis, float]) -> None:
        diagonal = np.asarray(
            [np.exp(1j * float(phases.get(value, 0.0))) for value in self._basis],
            dtype=np.complex128,
        )
        self.apply_unitary(np.diag(diagonal))

    def dephase(self, strength: float) -> None:
        amount = float(strength)
        if not 0.0 <= amount <= 1.0:
            raise QuantumStateError("dephasing strength must be in [0, 1]")
        diagonal = np.diag(np.diag(self._density))
        self._density = (1.0 - amount) * self._density + amount * diagonal
        self._stabilize()

    def condition_on(self, allowed: Iterable[Basis]) -> float:
        """Project onto legal basis states and return the retained probability."""
        allowed_set = set(allowed)
        mask = np.asarray(
            [1.0 if value in allowed_set else 0.0 for value in self._basis],
            dtype=np.complex128,
        )
        projected = mask[:, None] * self._density * mask[None, :]
        probability = float(np.trace(projected).real)
        if probability <= self._tolerance:
            raise QuantumStateError("legal projection has zero probability")
        self._density = projected / probability
        self._stabilize()
        return probability

    def measure(self, rng: np.random.Generator) -> MeasurementResult[Basis]:
        probabilities = self.probabilities()
        values = np.asarray([probabilities[value] for value in self._basis])
        roll = float(rng.random())
        index = min(int(np.searchsorted(np.cumsum(values), roll, side="right")), len(values) - 1)
        outcome = self._basis[index]
        probability = float(values[index])
        self._density.fill(0.0)
        self._density[index, index] = 1.0
        return MeasurementResult(outcome, probability, roll)

    def measure_region(
        self,
        region: Iterable[Basis],
        rng: np.random.Generator,
    ) -> RegionMeasurementResult:
        region_set = set(region)
        mask = np.asarray(
            [1.0 if value in region_set else 0.0 for value in self._basis],
            dtype=np.complex128,
        )
        probability = float(np.sum(mask.real * np.diag(self._density).real))
        roll = float(rng.random())
        detected = roll < probability
        selected = mask if detected else 1.0 - mask
        projected = selected[:, None] * self._density * selected[None, :]
        branch_probability = probability if detected else 1.0 - probability
        if branch_probability <= self._tolerance:
            raise QuantumStateError("measurement selected a zero-probability branch")
        self._density = projected / branch_probability
        self._stabilize()
        return RegionMeasurementResult(detected, probability, roll)

    def _validate_density(self) -> None:
        dimension = len(self._basis)
        if self._density.shape != (dimension, dimension):
            raise QuantumStateError("density matrix dimension does not match basis")
        if not np.all(np.isfinite(self._density)):
            raise QuantumStateError("density matrix contains non-finite values")
        if not np.allclose(self._density, self._density.conj().T, atol=1e-8):
            raise QuantumStateError("density matrix must be Hermitian")
        trace = complex(np.trace(self._density))
        if abs(trace.imag) > 1e-8 or abs(trace.real - 1.0) > 1e-8:
            raise QuantumStateError("density matrix must have unit trace")
        if float(np.linalg.eigvalsh(self._density).min()) < -1e-8:
            raise QuantumStateError("density matrix must be positive semidefinite")

    def _stabilize(self) -> None:
        self._density = (self._density + self._density.conj().T) * 0.5
        trace = float(np.trace(self._density).real)
        if trace <= self._tolerance:
            raise QuantumStateError("quantum operation destroyed all probability")
        self._density /= trace
        self._density[np.abs(self._density) < self._tolerance] = 0.0
        self._validate_density()


def lattice_hamiltonian(
    cells: Sequence[Cell],
    *,
    coupling: float = 1.0,
    potentials: Mapping[Cell, float] | None = None,
) -> np.ndarray:
    """Build the tight-binding Hamiltonian for traversable four-neighbor cells."""
    basis = tuple(cells)
    if not basis or len(set(basis)) != len(basis):
        raise QuantumStateError("Hamiltonian cells must be non-empty and unique")
    index = {cell: position for position, cell in enumerate(basis)}
    matrix = np.zeros((len(basis), len(basis)), dtype=np.complex128)
    for cell, row in index.items():
        matrix[row, row] = float((potentials or {}).get(cell, 0.0))
        for neighbor in LatticeCoordinate.neighbors4(cell):
            column = index.get(neighbor)
            if column is not None:
                matrix[row, column] = -float(coupling)
    return (matrix + matrix.conj().T) * 0.5


def tunneling_probability(
    barrier_height: float,
    energy: float,
    width: float,
    *,
    mass: float = 1.0,
    hbar: float = 1.0,
) -> float:
    """WKB transmission estimate for a finite tactical barrier."""
    if width < 0 or mass <= 0 or hbar <= 0:
        raise ValueError("width must be non-negative and mass/hbar must be positive")
    if energy >= barrier_height:
        return 1.0
    kappa = sqrt(2.0 * mass * max(0.0, barrier_height - energy)) / hbar
    return max(0.0, min(1.0, exp(-2.0 * kappa * width)))


class QuantumTacticalSystem:
    """Own local unit states, seeded measurements, and replay evidence."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = np.random.default_rng(int(seed))
        self._states: dict[int, QuantumState[Cell]] = {}
        self._turn = 0
        self.events: list[QuantumReplayEvent] = []

    def state(self, unit_id: int) -> QuantumState[Cell]:
        try:
            return self._states[int(unit_id)]
        except KeyError as error:
            raise QuantumStateError(f"unit {unit_id} has no quantum state") from error

    def prepare(self, unit_id: int, amplitudes: Mapping[Cell, complex]) -> None:
        self._states[int(unit_id)] = QuantumState.from_amplitudes(amplitudes)
        self._record(int(unit_id), "prepare", (), self.state(unit_id).probabilities())

    def phase_shift(self, unit_id: int, phases: Mapping[Cell, float]) -> None:
        state = self.state(unit_id)
        before = state.probabilities()
        state.phase_shift(phases)
        self._record(int(unit_id), "phase", before, state.probabilities())

    def evolve(self, unit_id: int, hamiltonian: np.ndarray, delta_time: float = 1.0) -> None:
        state = self.state(unit_id)
        before = state.probabilities()
        state.evolve(hamiltonian, delta_time)
        self._record(int(unit_id), "evolve", before, state.probabilities())

    def end_turn(self, dephasing: float = 0.0) -> None:
        self._turn += 1
        if dephasing <= 0.0:
            return
        for unit_id, state in sorted(self._states.items()):
            before = state.probabilities()
            state.dephase(dephasing)
            self._record(unit_id, "dephase", before, state.probabilities())

    def observe(self, unit_id: int, legal_cells: Iterable[Cell] | None = None) -> Cell:
        state = self.state(unit_id)
        before = state.probabilities()
        if legal_cells is not None:
            state.condition_on(legal_cells)
        result = state.measure(self._rng)
        self._record(
            int(unit_id),
            "measure",
            before,
            state.probabilities(),
            outcome=result.outcome,
            roll=result.roll,
        )
        return result.outcome

    def action_priors(self, actions: Sequence[Mapping[str, Any]]) -> dict[int, float]:
        """Return centered log-Born priors without creating illegal actions."""
        grouped: dict[int, list[Mapping[str, Any]]] = {}
        for action in actions:
            unit_id = int(action["unit"])
            if unit_id in self._states:
                grouped.setdefault(unit_id, []).append(action)
        priors: dict[int, float] = {}
        for unit_id, candidates in grouped.items():
            probabilities = self._states[unit_id].probabilities()
            raw = [
                log(max(1e-12, probabilities.get((int(action["x"]), int(action["y"])), 0.0)))
                for action in candidates
            ]
            center = sum(raw) / len(raw)
            priors.update(
                (int(action["index"]), value - center)
                for action, value in zip(candidates, raw)
            )
        return priors

    def _record(
        self,
        unit_id: int,
        kind: str,
        before: Mapping[Hashable, float] | Iterable[Any],
        after: Mapping[Hashable, float],
        *,
        outcome: Hashable | bool | None = None,
        roll: float | None = None,
    ) -> None:
        before_items = tuple(before.items()) if isinstance(before, Mapping) else ()
        self.events.append(
            QuantumReplayEvent(
                self._turn,
                unit_id,
                kind,
                tuple((key, float(value)) for key, value in before_items),
                tuple((key, float(value)) for key, value in after.items()),
                outcome,
                roll,
            )
        )
