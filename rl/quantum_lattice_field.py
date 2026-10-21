"""Truncated bosonic quantum fields on a tactical lattice.

This is an exact finite Fock-space implementation intended for small local
combat regions.  It supports Bose-Hubbard hopping, local interaction, gauge-link
phases, creation/annihilation filters, dephasing, and coupling to lattice MFG
density trajectories.  The explicit dimension guard prevents accidental
exponential blow-ups.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite, log, sqrt
from typing import Any, Mapping, Sequence

import numpy as np

from rl.lattice_geometry import Cell, LatticeCoordinate
from rl.lattice_mfg import LatticeMFG, LatticeMFGError, LatticeMFGResult
from rl.quantum_tactics import QuantumState


Occupation = tuple[int, ...]


class QuantumLatticeFieldError(ValueError):
    """Raised when a bosonic lattice field exceeds or violates its contract."""


@dataclass(frozen=True)
class BosonicLatticeConfig:
    max_occupancy: int = 2
    hopping: float = 1.0
    interaction: float = 0.0
    max_dimension: int = 4096

    def __post_init__(self) -> None:
        if self.max_occupancy < 1:
            raise QuantumLatticeFieldError("max occupancy must be at least one")
        if not isfinite(self.hopping) or self.hopping < 0.0:
            raise QuantumLatticeFieldError("hopping must be finite and non-negative")
        if not isfinite(self.interaction):
            raise QuantumLatticeFieldError("interaction must be finite")
        if self.max_dimension <= 0:
            raise QuantumLatticeFieldError("maximum Fock dimension must be positive")


@dataclass(frozen=True)
class CoupledLatticeResult:
    mfg: LatticeMFGResult
    quantum_occupancies: np.ndarray
    final_field: "BosonicLatticeField"
    residuals: tuple[float, ...]
    converged: bool


class BosonicLatticeField:
    """Exact truncated Bose-Hubbard field over a small set of map cells."""

    def __init__(
        self,
        cells: Sequence[Cell],
        amplitudes: Mapping[Occupation, complex],
        *,
        edges: Sequence[tuple[Cell, Cell]] | None = None,
        config: BosonicLatticeConfig | None = None,
    ) -> None:
        self.config = config or BosonicLatticeConfig()
        self.cells = tuple(cells)
        if not self.cells or len(set(self.cells)) != len(self.cells):
            raise QuantumLatticeFieldError("field cells must be non-empty and unique")
        self.index = {cell: position for position, cell in enumerate(self.cells)}
        dimension = (self.config.max_occupancy + 1) ** len(self.cells)
        if dimension > self.config.max_dimension:
            raise QuantumLatticeFieldError(
                f"Fock dimension {dimension} exceeds limit {self.config.max_dimension}"
            )
        self.fock_basis = tuple(
            product(range(self.config.max_occupancy + 1), repeat=len(self.cells))
        )
        self._basis_index = {
            occupation: position for position, occupation in enumerate(self.fock_basis)
        }
        self.edges = self._build_edges(edges)
        vector = np.zeros(len(self.fock_basis), dtype=np.complex128)
        for occupation, amplitude in amplitudes.items():
            key = tuple(int(value) for value in occupation)
            position = self._basis_index.get(key)
            if position is None:
                raise QuantumLatticeFieldError(
                    "occupation state is outside the truncated Fock basis"
                )
            vector[position] = complex(amplitude)
        norm = float(np.vdot(vector, vector).real)
        if not isfinite(norm) or norm <= 0.0:
            raise QuantumLatticeFieldError("field amplitudes need a finite non-zero norm")
        vector /= sqrt(norm)
        self.state = QuantumState(
            self.fock_basis,
            np.outer(vector, vector.conj()),
        )
        self._annihilation = tuple(
            self._build_annihilation(mode) for mode in range(len(self.cells))
        )

    @classmethod
    def vacuum(
        cls,
        cells: Sequence[Cell],
        *,
        edges: Sequence[tuple[Cell, Cell]] | None = None,
        config: BosonicLatticeConfig | None = None,
    ) -> "BosonicLatticeField":
        return cls(
            cells,
            {tuple(0 for _ in cells): 1.0 + 0.0j},
            edges=edges,
            config=config,
        )

    def copy(self) -> "BosonicLatticeField":
        duplicate = object.__new__(BosonicLatticeField)
        duplicate.config = self.config
        duplicate.cells = self.cells
        duplicate.index = dict(self.index)
        duplicate.fock_basis = self.fock_basis
        duplicate._basis_index = dict(self._basis_index)
        duplicate.edges = self.edges
        duplicate.state = self.state.copy()
        duplicate._annihilation = self._annihilation
        return duplicate

    @property
    def dimension(self) -> int:
        return len(self.fock_basis)

    def annihilation_operator(self, cell: Cell) -> np.ndarray:
        return self._annihilation[self._cell_index(cell)].copy()

    def creation_operator(self, cell: Cell) -> np.ndarray:
        return self._annihilation[self._cell_index(cell)].conj().T.copy()

    def number_operator(self, cell: Cell) -> np.ndarray:
        annihilation = self._annihilation[self._cell_index(cell)]
        return annihilation.conj().T @ annihilation

    def hamiltonian(
        self,
        *,
        potentials: Mapping[Cell, float] | None = None,
        gauge_phases: Mapping[tuple[Cell, Cell], float] | None = None,
        mfg_density: Mapping[Cell, float] | Sequence[float] | np.ndarray | None = None,
        density_coupling: float = 0.0,
    ) -> np.ndarray:
        """Build a Hermitian Bose-Hubbard Hamiltonian with Peierls phases."""
        size = self.dimension
        matrix = np.zeros((size, size), dtype=np.complex128)
        identities = np.eye(size, dtype=np.complex128)
        density = self._cell_values(mfg_density)
        for mode, cell in enumerate(self.cells):
            annihilation = self._annihilation[mode]
            number = annihilation.conj().T @ annihilation
            local_potential = float((potentials or {}).get(cell, 0.0))
            local_potential += float(density_coupling) * density[mode]
            matrix += local_potential * number
            matrix += (
                0.5
                * self.config.interaction
                * (number @ (number - identities))
            )
        for left, right in self.edges:
            left_index = self.index[left]
            right_index = self.index[right]
            left_create = self._annihilation[left_index].conj().T
            right_annihilate = self._annihilation[right_index]
            phase = float((gauge_phases or {}).get((left, right), 0.0))
            forward = np.exp(1j * phase) * (left_create @ right_annihilate)
            matrix -= self.config.hopping * (forward + forward.conj().T)
        return (matrix + matrix.conj().T) * 0.5

    def evolve(
        self,
        delta_time: float,
        *,
        potentials: Mapping[Cell, float] | None = None,
        gauge_phases: Mapping[tuple[Cell, Cell], float] | None = None,
        mfg_density: Mapping[Cell, float] | Sequence[float] | np.ndarray | None = None,
        density_coupling: float = 0.0,
        dephasing: float = 0.0,
    ) -> None:
        if not isfinite(delta_time) or delta_time < 0.0:
            raise QuantumLatticeFieldError("evolution time must be finite and non-negative")
        if delta_time:
            self.state.evolve(
                self.hamiltonian(
                    potentials=potentials,
                    gauge_phases=gauge_phases,
                    mfg_density=mfg_density,
                    density_coupling=density_coupling,
                ),
                delta_time,
            )
        if dephasing:
            self.state.dephase(dephasing)

    def create(self, cell: Cell) -> float:
        """Condition the field on one successful local creation event."""
        return self.state.apply_filter(self.creation_operator(cell))

    def annihilate(self, cell: Cell) -> float:
        """Condition the field on one successful local annihilation event."""
        return self.state.apply_filter(self.annihilation_operator(cell))

    def expected_occupations(self) -> dict[Cell, float]:
        density = self.state.density
        return {
            cell: float(np.trace(density @ self.number_operator(cell)).real)
            for cell in self.cells
        }

    @property
    def expected_particles(self) -> float:
        return sum(self.expected_occupations().values())

    def normalized_intensity(self) -> dict[Cell, float]:
        occupations = self.expected_occupations()
        total = sum(occupations.values())
        if total <= 1e-12:
            return {cell: 0.0 for cell in self.cells}
        return {cell: value / total for cell, value in occupations.items()}

    def action_priors(
        self,
        actions: Sequence[Mapping[str, Any]],
        *,
        floor: float = 1e-12,
    ) -> dict[int, float]:
        """Return centered log-intensity priors over existing legal actions."""
        intensity = self.normalized_intensity()
        grouped: dict[int, list[Mapping[str, Any]]] = {}
        for action in actions:
            grouped.setdefault(int(action["unit"]), []).append(action)
        priors: dict[int, float] = {}
        for candidates in grouped.values():
            valid = [
                action
                for action in candidates
                if (int(action["x"]), int(action["y"])) in self.index
            ]
            if not valid:
                continue
            raw = [
                log(
                    max(
                        floor,
                        intensity.get((int(action["x"]), int(action["y"])), 0.0),
                    )
                )
                for action in valid
            ]
            center = sum(raw) / len(raw)
            priors.update(
                (int(action["index"]), value - center)
                for action, value in zip(valid, raw)
            )
        return priors

    def _build_edges(
        self,
        supplied: Sequence[tuple[Cell, Cell]] | None,
    ) -> tuple[tuple[Cell, Cell], ...]:
        valid = set(self.cells)
        raw = (
            supplied
            if supplied is not None
            else [
                (cell, neighbor)
                for cell in self.cells
                for neighbor in LatticeCoordinate.neighbors4(cell)
                if neighbor in valid and self.index[cell] < self.index[neighbor]
            ]
        )
        unique: list[tuple[Cell, Cell]] = []
        seen: set[frozenset[Cell]] = set()
        for left, right in raw:
            if left not in valid or right not in valid or left == right:
                raise QuantumLatticeFieldError("field edge is invalid")
            key = frozenset((left, right))
            if key not in seen:
                seen.add(key)
                unique.append((left, right))
        return tuple(unique)

    def _build_annihilation(self, mode: int) -> np.ndarray:
        matrix = np.zeros((self.dimension, self.dimension), dtype=np.complex128)
        for column, occupation in enumerate(self.fock_basis):
            count = occupation[mode]
            if count == 0:
                continue
            target = list(occupation)
            target[mode] -= 1
            row = self._basis_index[tuple(target)]
            matrix[row, column] = sqrt(count)
        return matrix

    def _cell_index(self, cell: Cell) -> int:
        try:
            return self.index[cell]
        except KeyError as error:
            raise QuantumLatticeFieldError(f"cell {cell} is outside the field") from error

    def _cell_values(
        self,
        values: Mapping[Cell, float] | Sequence[float] | np.ndarray | None,
    ) -> np.ndarray:
        if values is None:
            return np.zeros(len(self.cells), dtype=np.float64)
        if isinstance(values, Mapping):
            result = np.asarray([float(values.get(cell, 0.0)) for cell in self.cells])
        else:
            result = np.asarray(values, dtype=np.float64)
        if result.shape != (len(self.cells),) or np.any(~np.isfinite(result)):
            raise QuantumLatticeFieldError("cell field has invalid dimensions or values")
        return result


class LatticeMFGQuantumCoupler:
    """Alternating self-consistency between crowd density and a quantum field."""

    def __init__(
        self,
        mfg: LatticeMFG,
        field: BosonicLatticeField,
        *,
        density_to_potential: float = 1.0,
        quantum_to_cost: float = 1.0,
        delta_time: float = 0.2,
        dephasing: float = 0.0,
        relaxation: float = 0.5,
        tolerance: float = 1e-6,
        max_iterations: int = 60,
    ) -> None:
        if tuple(mfg.cells) != tuple(field.cells):
            raise QuantumLatticeFieldError("MFG and quantum field must share cell order")
        if delta_time < 0.0 or not 0.0 <= dephasing <= 1.0:
            raise QuantumLatticeFieldError("invalid quantum evolution parameters")
        if not 0.0 < relaxation <= 1.0 or tolerance <= 0.0 or max_iterations <= 0:
            raise QuantumLatticeFieldError("invalid coupled solver parameters")
        self.mfg = mfg
        self.field = field.copy()
        self.density_to_potential = float(density_to_potential)
        self.quantum_to_cost = float(quantum_to_cost)
        self.delta_time = float(delta_time)
        self.dephasing = float(dephasing)
        self.relaxation = float(relaxation)
        self.tolerance = float(tolerance)
        self.max_iterations = int(max_iterations)

    def solve(
        self,
        initial_density: Mapping[Cell, float] | Sequence[float] | np.ndarray,
        terminal_cost: Mapping[Cell, float] | Sequence[float] | np.ndarray,
        *,
        base_external_costs: np.ndarray | None = None,
        potentials: Mapping[Cell, float] | None = None,
        gauge_phases: Mapping[tuple[Cell, Cell], float] | None = None,
    ) -> CoupledLatticeResult:
        initial = self.mfg._vector(initial_density, "coupled initial density")
        if float(initial.sum()) <= 0.0 or np.any(initial < 0.0):
            raise LatticeMFGError("coupled initial density is invalid")
        initial /= float(initial.sum())
        trajectory = np.repeat(
            initial[None, :], self.mfg.config.horizon + 1, axis=0
        )
        base = (
            np.zeros((self.mfg.config.horizon, self.mfg.dimension))
            if base_external_costs is None
            else np.asarray(base_external_costs, dtype=np.float64)
        )
        if base.shape != (self.mfg.config.horizon, self.mfg.dimension):
            raise QuantumLatticeFieldError("base external costs have invalid dimensions")
        residuals: list[float] = []
        result: LatticeMFGResult | None = None
        occupancies = np.zeros_like(base)
        final_field = self.field.copy()
        converged = False
        for _ in range(self.max_iterations):
            occupancies, candidate_field = self._quantum_trajectory(
                trajectory,
                potentials,
                gauge_phases,
            )
            external = base + self.quantum_to_cost * occupancies
            candidate = self.mfg.solve(
                initial,
                terminal_cost,
                external_costs=external,
                initial_guess=trajectory,
            )
            residual = float(
                np.max(np.sum(np.abs(candidate.densities - trajectory), axis=1))
            )
            residuals.append(residual)
            trajectory[1:] = (
                (1.0 - self.relaxation) * trajectory[1:]
                + self.relaxation * candidate.densities[1:]
            )
            result = candidate
            final_field = candidate_field
            if residual <= self.tolerance:
                converged = True
                break
        if result is None:
            raise QuantumLatticeFieldError("coupled solver did not execute")
        return CoupledLatticeResult(
            result,
            occupancies.copy(),
            final_field,
            tuple(residuals),
            converged,
        )

    def _quantum_trajectory(
        self,
        densities: np.ndarray,
        potentials: Mapping[Cell, float] | None,
        gauge_phases: Mapping[tuple[Cell, Cell], float] | None,
    ) -> tuple[np.ndarray, BosonicLatticeField]:
        field = self.field.copy()
        output = np.zeros((self.mfg.config.horizon, self.mfg.dimension))
        for time in range(self.mfg.config.horizon):
            field.evolve(
                self.delta_time,
                potentials=potentials,
                gauge_phases=gauge_phases,
                mfg_density=densities[time],
                density_coupling=self.density_to_potential,
                dephasing=self.dephasing,
            )
            intensity = field.normalized_intensity()
            output[time] = [intensity[cell] for cell in self.mfg.cells]
        return output, field


class LatticeFieldPolicyAdapter:
    """Expose solved MFG and quantum priors through an existing environment."""

    def __init__(
        self,
        environment: Any,
        *,
        mfg_result: LatticeMFGResult | None = None,
        quantum_field: BosonicLatticeField | None = None,
        time: int = 0,
    ) -> None:
        if mfg_result is None and quantum_field is None:
            raise QuantumLatticeFieldError("policy adapter needs an MFG or quantum field")
        self.environment = environment
        self.mfg_result = mfg_result
        self.quantum_field = quantum_field
        self.time = int(time)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.environment, name)

    def mfg_action_priors(
        self, actions: Sequence[Mapping[str, Any]]
    ) -> dict[int, float]:
        if self.mfg_result is None:
            return {}
        return self.mfg_result.action_priors(
            actions,
            self.environment.unit_info(),
            time=self.time,
        )

    def quantum_action_priors(
        self, actions: Sequence[Mapping[str, Any]]
    ) -> dict[int, float]:
        if self.quantum_field is None:
            return {}
        return self.quantum_field.action_priors(actions)
