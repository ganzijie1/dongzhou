"""P7 political inference, signaling, temporal networks, events, and logistics."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import exp, isfinite, log
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


Variable = Hashable
Value = Hashable
ActorType = Hashable
Message = Hashable
Action = Hashable
Node = Hashable


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 1 or result.size == 0 or np.any(~np.isfinite(result)):
        raise ValueError(f"{name} must be a finite non-empty vector")
    if np.any(result < 0.0) or float(result.sum()) <= 0.0:
        raise ValueError(f"{name} must contain non-negative positive mass")
    return result / result.sum()


@dataclass(frozen=True)
class DiscreteFactor:
    variables: tuple[Variable, ...]
    values: np.ndarray


class DiscreteFactorGraph:
    """Exact finite factor-graph inference by enumeration.

    The implementation is deliberately bounded and transparent. It is suitable for
    small political/event models, not large unrestricted graphical models.
    """

    def __init__(
        self,
        domains: Mapping[Variable, Sequence[Value]],
        factors: Sequence[DiscreteFactor],
        *,
        maximum_assignments: int = 1_000_000,
    ) -> None:
        self.variables = tuple(domains)
        self.domains = {variable: tuple(dict.fromkeys(domains[variable])) for variable in self.variables}
        if not self.variables or any(not domain for domain in self.domains.values()):
            raise ValueError("factor graph domains must be non-empty")
        if maximum_assignments <= 0:
            raise ValueError("maximum_assignments must be positive")
        assignment_count = int(np.prod([len(self.domains[v]) for v in self.variables]))
        if assignment_count > maximum_assignments:
            raise ValueError("factor graph exceeds the exact-enumeration budget")
        self._indices = {
            variable: {value: index for index, value in enumerate(self.domains[variable])}
            for variable in self.variables
        }
        checked = []
        for factor in factors:
            variables = tuple(factor.variables)
            if not variables or len(set(variables)) != len(variables):
                raise ValueError("factor variables must be non-empty and unique")
            if any(variable not in self.domains for variable in variables):
                raise ValueError("factor references an unknown variable")
            values = np.asarray(factor.values, dtype=np.float64)
            expected = tuple(len(self.domains[variable]) for variable in variables)
            if values.shape != expected or np.any(~np.isfinite(values)) or np.any(values < 0.0):
                raise ValueError("factor table has an invalid shape or value")
            checked.append(DiscreteFactor(variables, values.copy()))
        if not checked:
            raise ValueError("factor graph needs at least one factor")
        self.factors = tuple(checked)

    def marginal(
        self,
        query: Sequence[Variable],
        evidence: Mapping[Variable, Value] | None = None,
    ) -> np.ndarray:
        query_variables = tuple(query)
        observed = dict(evidence or {})
        if not query_variables or len(set(query_variables)) != len(query_variables):
            raise ValueError("query variables must be non-empty and unique")
        if any(variable not in self.domains for variable in (*query_variables, *observed)):
            raise ValueError("query or evidence references an unknown variable")
        if any(value not in self._indices[variable] for variable, value in observed.items()):
            raise ValueError("evidence value lies outside its variable domain")
        shape = tuple(len(self.domains[variable]) for variable in query_variables)
        result = np.zeros(shape, dtype=np.float64)
        for values in product(*(self.domains[variable] for variable in self.variables)):
            assignment = dict(zip(self.variables, values, strict=True))
            if any(assignment[variable] != value for variable, value in observed.items()):
                continue
            weight = 1.0
            for factor in self.factors:
                index = tuple(self._indices[v][assignment[v]] for v in factor.variables)
                weight *= float(factor.values[index])
            query_index = tuple(self._indices[v][assignment[v]] for v in query_variables)
            result[query_index] += weight
        total = float(result.sum())
        if total <= 0.0:
            raise ValueError("evidence has zero probability under the factor graph")
        return result / total


@dataclass(frozen=True)
class BayesianFilterStep:
    predictive: np.ndarray
    posterior: np.ndarray
    observation_probability: float


class FiniteDynamicBayesianFilter:
    """Finite-state DBN filter with a categorical hidden state and observation."""

    def __init__(
        self,
        states: Sequence[Hashable],
        observations: Sequence[Hashable],
        initial: Sequence[float],
        transition: Sequence[Sequence[float]],
        emission: Sequence[Sequence[float]],
    ) -> None:
        self.states = tuple(dict.fromkeys(states))
        self.observations = tuple(dict.fromkeys(observations))
        if not self.states or not self.observations:
            raise ValueError("DBN states and observations must be non-empty")
        self.transition = np.asarray(transition, dtype=np.float64)
        self.emission = np.asarray(emission, dtype=np.float64)
        if self.transition.shape != (len(self.states), len(self.states)):
            raise ValueError("DBN transition shape is invalid")
        if self.emission.shape != (len(self.states), len(self.observations)):
            raise ValueError("DBN emission shape is invalid")
        for matrix, name in ((self.transition, "transition"), (self.emission, "emission")):
            if np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0):
                raise ValueError(f"DBN {name} probabilities are invalid")
            if not np.allclose(matrix.sum(axis=1), 1.0, atol=1e-10):
                raise ValueError(f"DBN {name} rows must sum to one")
        self.belief = _probability_vector(initial, "DBN initial belief")
        if self.belief.shape != (len(self.states),):
            raise ValueError("DBN initial belief shape is invalid")
        self._observation_index = {value: index for index, value in enumerate(self.observations)}

    def predict(self) -> np.ndarray:
        return self.belief @ self.transition

    def update(self, observation: Hashable) -> BayesianFilterStep:
        if observation not in self._observation_index:
            raise ValueError("DBN observation is unknown")
        predictive = self.predict()
        likelihood = self.emission[:, self._observation_index[observation]]
        mass = float(predictive @ likelihood)
        if mass <= 0.0:
            raise ValueError("DBN observation has zero probability")
        self.belief = predictive * likelihood / mass
        return BayesianFilterStep(predictive.copy(), self.belief.copy(), mass)


@dataclass(frozen=True)
class SignalingEquilibrium:
    sender_strategy: Mapping[ActorType, Message]
    receiver_strategy: Mapping[Message, Action]
    posteriors: Mapping[Message, Mapping[ActorType, float]]


def _off_path_belief(
    chosen_action: int,
    receiver_utility: np.ndarray,
    *,
    tolerance: float,
) -> np.ndarray | None:
    type_count, action_count = receiver_utility.shape
    inequalities = []
    for alternative in range(action_count):
        if alternative == chosen_action:
            continue
        inequalities.append(
            receiver_utility[:, alternative] - receiver_utility[:, chosen_action]
        )
    solved = linprog(
        np.zeros(type_count),
        A_ub=np.asarray(inequalities) if inequalities else None,
        b_ub=np.full(len(inequalities), tolerance) if inequalities else None,
        A_eq=np.ones((1, type_count)),
        b_eq=[1.0],
        bounds=[(0.0, 1.0)] * type_count,
        method="highs",
    )
    return solved.x if solved.success else None


def pure_signaling_equilibria(
    actor_types: Sequence[ActorType],
    messages: Sequence[Message],
    actions: Sequence[Action],
    prior: Sequence[float],
    sender_payoff: Sequence[Sequence[Sequence[float]]],
    receiver_payoff: Sequence[Sequence[Sequence[float]]],
    *,
    tolerance: float = 1e-10,
    maximum_profiles: int = 500_000,
) -> tuple[SignalingEquilibrium, ...]:
    """Enumerate pure finite PBE, including supportable off-path beliefs."""

    types = tuple(dict.fromkeys(actor_types))
    message_values = tuple(dict.fromkeys(messages))
    action_values = tuple(dict.fromkeys(actions))
    probability = _probability_vector(prior, "signaling prior")
    sender = np.asarray(sender_payoff, dtype=np.float64)
    receiver = np.asarray(receiver_payoff, dtype=np.float64)
    expected_shape = (len(types), len(message_values), len(action_values))
    if not types or not message_values or not action_values or probability.shape != (len(types),):
        raise ValueError("signaling game domains are invalid")
    if sender.shape != expected_shape or receiver.shape != expected_shape:
        raise ValueError("signaling payoff tensor shape is invalid")
    if np.any(~np.isfinite(sender)) or np.any(~np.isfinite(receiver)):
        raise ValueError("signaling payoffs must be finite")
    profile_count = len(message_values) ** len(types) * len(action_values) ** len(message_values)
    if profile_count > maximum_profiles:
        raise ValueError("signaling game exceeds the pure-profile enumeration budget")

    equilibria = []
    for sender_indices in product(range(len(message_values)), repeat=len(types)):
        message_mass = np.zeros(len(message_values))
        for type_index, message_index in enumerate(sender_indices):
            message_mass[message_index] += probability[type_index]
        for receiver_indices in product(range(len(action_values)), repeat=len(message_values)):
            posteriors: dict[Message, dict[ActorType, float]] = {}
            receiver_rational = True
            for message_index, chosen_action in enumerate(receiver_indices):
                if message_mass[message_index] > tolerance:
                    posterior = np.asarray(
                        [
                            probability[type_index] / message_mass[message_index]
                            if sender_indices[type_index] == message_index
                            else 0.0
                            for type_index in range(len(types))
                        ]
                    )
                    expected = posterior @ receiver[:, message_index, :]
                    if expected[chosen_action] + tolerance < float(expected.max()):
                        receiver_rational = False
                        break
                else:
                    posterior = _off_path_belief(
                        chosen_action,
                        receiver[:, message_index, :],
                        tolerance=tolerance,
                    )
                    if posterior is None:
                        receiver_rational = False
                        break
                posteriors[message_values[message_index]] = {
                    actor_type: float(posterior[type_index])
                    for type_index, actor_type in enumerate(types)
                }
            if not receiver_rational:
                continue
            sender_rational = True
            for type_index, chosen_message in enumerate(sender_indices):
                chosen = sender[type_index, chosen_message, receiver_indices[chosen_message]]
                for alternative in range(len(message_values)):
                    deviating = sender[type_index, alternative, receiver_indices[alternative]]
                    if deviating > chosen + tolerance:
                        sender_rational = False
                        break
                if not sender_rational:
                    break
            if sender_rational:
                equilibria.append(
                    SignalingEquilibrium(
                        dict(zip(types, (message_values[i] for i in sender_indices), strict=True)),
                        dict(zip(message_values, (action_values[i] for i in receiver_indices), strict=True)),
                        posteriors,
                    )
                )
    return tuple(equilibria)


@dataclass(frozen=True)
class TemporalNetworkDiagnostics:
    aggregate_snapshots: np.ndarray
    node_strengths: np.ndarray
    volatility: np.ndarray
    spectral_radii: np.ndarray


class TemporalMultilayerNetwork:
    """A finite temporal multiplex network with explicit layer semantics."""

    def __init__(
        self,
        nodes: Sequence[Node],
        layers: Sequence[Hashable],
        adjacency: Sequence[Sequence[Sequence[Sequence[float]]]],
    ) -> None:
        self.nodes = tuple(dict.fromkeys(nodes))
        self.layers = tuple(dict.fromkeys(layers))
        self.adjacency = np.asarray(adjacency, dtype=np.float64)
        expected_tail = (len(self.layers), len(self.nodes), len(self.nodes))
        if not self.nodes or not self.layers or self.adjacency.ndim != 4:
            raise ValueError("temporal multilayer domains are invalid")
        if self.adjacency.shape[1:] != expected_tail or self.adjacency.shape[0] == 0:
            raise ValueError("temporal multilayer adjacency shape is invalid")
        if np.any(~np.isfinite(self.adjacency)):
            raise ValueError("temporal multilayer weights must be finite")

    def aggregate(self, weights: Sequence[float] | None = None) -> np.ndarray:
        layer_weights = (
            np.ones(len(self.layers), dtype=np.float64)
            if weights is None
            else np.asarray(weights, dtype=np.float64)
        )
        if layer_weights.shape != (len(self.layers),) or np.any(~np.isfinite(layer_weights)):
            raise ValueError("layer aggregation weights are invalid")
        return np.einsum("l,tlij->tij", layer_weights, self.adjacency)

    def supra_adjacency(self, time_index: int, *, coupling: float = 0.0) -> np.ndarray:
        if not 0 <= time_index < self.adjacency.shape[0]:
            raise ValueError("temporal network time index is invalid")
        if not isfinite(coupling) or coupling < 0.0:
            raise ValueError("interlayer coupling must be finite and non-negative")
        layer_count, node_count = len(self.layers), len(self.nodes)
        result = np.zeros((layer_count * node_count, layer_count * node_count))
        for layer_index in range(layer_count):
            block = slice(layer_index * node_count, (layer_index + 1) * node_count)
            result[block, block] = self.adjacency[time_index, layer_index]
        for left in range(layer_count):
            for right in range(left + 1, layer_count):
                rows = slice(left * node_count, (left + 1) * node_count)
                columns = slice(right * node_count, (right + 1) * node_count)
                result[rows, columns] = coupling * np.eye(node_count)
                result[columns, rows] = coupling * np.eye(node_count)
        return result

    def diagnostics(self, weights: Sequence[float] | None = None) -> TemporalNetworkDiagnostics:
        aggregate = self.aggregate(weights)
        strengths = np.sum(np.abs(aggregate), axis=2) + np.sum(np.abs(aggregate), axis=1)
        volatility = np.zeros(aggregate.shape[0])
        if aggregate.shape[0] > 1:
            volatility[1:] = np.linalg.norm(np.diff(aggregate, axis=0), axis=(1, 2))
        radii = np.asarray([max(abs(np.linalg.eigvals(matrix)), default=0.0) for matrix in aggregate])
        return TemporalNetworkDiagnostics(aggregate, strengths, volatility, radii.astype(float))


class ExponentialHawkesProcess:
    """Multivariate Hawkes process with a shared exponential decay rate."""

    def __init__(
        self,
        baseline: Sequence[float],
        excitation: Sequence[Sequence[float]],
        *,
        decay: float,
    ) -> None:
        self.baseline = np.asarray(baseline, dtype=np.float64)
        self.excitation = np.asarray(excitation, dtype=np.float64)
        self.decay = float(decay)
        if self.baseline.ndim != 1 or self.baseline.size == 0:
            raise ValueError("Hawkes baseline must be a non-empty vector")
        if self.excitation.shape != (self.baseline.size, self.baseline.size):
            raise ValueError("Hawkes excitation shape is invalid")
        if (
            np.any(~np.isfinite(self.baseline))
            or np.any(self.baseline <= 0.0)
            or np.any(~np.isfinite(self.excitation))
            or np.any(self.excitation < 0.0)
            or not isfinite(self.decay)
            or self.decay <= 0.0
        ):
            raise ValueError("Hawkes parameters are invalid")

    @property
    def branching_ratio(self) -> float:
        return float(max(abs(np.linalg.eigvals(self.excitation / self.decay))))

    @property
    def stable(self) -> bool:
        return self.branching_ratio < 1.0 - 1e-12

    def intensity(self, time: float, history: Sequence[tuple[float, int]]) -> np.ndarray:
        if not isfinite(time) or time < 0.0:
            raise ValueError("Hawkes time must be finite and non-negative")
        result = self.baseline.copy()
        for event_time, event_type in history:
            if not isfinite(event_time) or event_time < 0.0 or event_time >= time:
                raise ValueError("Hawkes history must contain valid past events")
            if not 0 <= int(event_type) < self.baseline.size:
                raise ValueError("Hawkes event type is invalid")
            result += self.excitation[:, int(event_type)] * exp(-self.decay * (time - event_time))
        return result

    def log_likelihood(self, history: Sequence[tuple[float, int]], horizon: float) -> float:
        events = tuple((float(time), int(kind)) for time, kind in history)
        if not isfinite(horizon) or horizon <= 0.0:
            raise ValueError("Hawkes horizon must be positive and finite")
        if any(time < 0.0 or time >= horizon for time, _kind in events):
            raise ValueError("Hawkes event lies outside the observation horizon")
        if any(events[i][0] > events[i + 1][0] for i in range(len(events) - 1)):
            raise ValueError("Hawkes events must be time ordered")
        likelihood = 0.0
        past: list[tuple[float, int]] = []
        for event_time, event_type in events:
            if not 0 <= event_type < self.baseline.size:
                raise ValueError("Hawkes event type is invalid")
            current = self.intensity(event_time, past)[event_type]
            likelihood += log(float(current))
            past.append((event_time, event_type))
        integral = float(self.baseline.sum()) * horizon
        for event_time, event_type in events:
            integral += float(self.excitation[:, event_type].sum()) * (
                1.0 - exp(-self.decay * (horizon - event_time))
            ) / self.decay
        return likelihood - integral

    def stationary_intensity(self) -> np.ndarray:
        if not self.stable:
            raise ValueError("unstable Hawkes process has no finite stationary intensity")
        return np.linalg.solve(np.eye(self.baseline.size) - self.excitation / self.decay, self.baseline)


@dataclass(frozen=True)
class InventoryPolicy:
    values: np.ndarray
    orders: np.ndarray
    expected_cost: float


def solve_stochastic_inventory(
    demand_distributions: Sequence[Mapping[int, float]],
    *,
    initial_inventory: int,
    order_capacity: int,
    holding_cost: float,
    shortage_cost: float,
    order_cost: float = 0.0,
    terminal_salvage: float = 0.0,
) -> InventoryPolicy:
    """Finite-horizon lost-sales inventory control by backward induction."""

    horizon = len(demand_distributions)
    if horizon == 0 or initial_inventory < 0 or order_capacity < 0:
        raise ValueError("inventory horizon and capacities are invalid")
    costs = (holding_cost, shortage_cost, order_cost, terminal_salvage)
    if any(not isfinite(float(value)) or float(value) < 0.0 for value in costs):
        raise ValueError("inventory costs must be finite and non-negative")
    distributions = []
    for distribution in demand_distributions:
        demands = tuple(sorted((int(demand), float(mass)) for demand, mass in distribution.items()))
        if not demands or any(demand < 0 or mass < 0.0 or not isfinite(mass) for demand, mass in demands):
            raise ValueError("inventory demand distribution is invalid")
        probability = _probability_vector([mass for _demand, mass in demands], "inventory demand")
        distributions.append(tuple((demand, float(mass)) for (demand, _), mass in zip(demands, probability)))
    max_inventory = initial_inventory + horizon * order_capacity
    values = np.zeros((horizon + 1, max_inventory + 1), dtype=np.float64)
    values[-1] = -float(terminal_salvage) * np.arange(max_inventory + 1)
    orders = np.zeros((horizon, max_inventory + 1), dtype=np.int64)
    for period in range(horizon - 1, -1, -1):
        for inventory in range(max_inventory + 1):
            candidates = []
            for order in range(min(order_capacity, max_inventory - inventory) + 1):
                expected = float(order_cost) * order
                for demand, probability in distributions[period]:
                    available = inventory + order
                    remaining = max(0, available - demand)
                    shortage = max(0, demand - available)
                    expected += probability * (
                        float(holding_cost) * remaining
                        + float(shortage_cost) * shortage
                        + values[period + 1, remaining]
                    )
                candidates.append((expected, order))
            best_cost, best_order = min(candidates, key=lambda item: (item[0], item[1]))
            values[period, inventory] = best_cost
            orders[period, inventory] = best_order
    return InventoryPolicy(values, orders, float(values[0, initial_inventory]))


@dataclass(frozen=True)
class ShippingArc:
    source: Node
    target: Node
    capacity: float
    cost: float
    travel_time: int = 1


@dataclass(frozen=True)
class DynamicFlowResult:
    inventory: Mapping[tuple[int, Node], float]
    shipments: Mapping[tuple[int, Node, Node], float]
    unmet: Mapping[tuple[int, Node], float]
    wasted: Mapping[tuple[int, Node], float]
    objective: float


def solve_dynamic_inventory_flow(
    nodes: Sequence[Node],
    periods: int,
    arcs: Sequence[ShippingArc],
    *,
    initial_inventory: Mapping[Node, float],
    supply: Mapping[tuple[int, Node], float],
    demand: Mapping[tuple[int, Node], float],
    storage_capacity: Mapping[Node, float],
    holding_cost: Mapping[Node, float] | None = None,
    shortage_penalty: Mapping[Node, float] | None = None,
) -> DynamicFlowResult:
    """Solve a deterministic time-expanded inventory and transport LP."""

    ordered_nodes = tuple(dict.fromkeys(nodes))
    node_index = {node: index for index, node in enumerate(ordered_nodes)}
    if not ordered_nodes or periods <= 0:
        raise ValueError("dynamic inventory network dimensions are invalid")
    checked_arcs = tuple(arcs)
    for arc in checked_arcs:
        if arc.source not in node_index or arc.target not in node_index or arc.source == arc.target:
            raise ValueError("shipping arc references invalid nodes")
        if (
            not isfinite(arc.capacity)
            or arc.capacity < 0.0
            or not isfinite(arc.cost)
            or arc.cost < 0.0
            or arc.travel_time <= 0
        ):
            raise ValueError("shipping arc parameters are invalid")
    for node in ordered_nodes:
        scalars = (
            initial_inventory.get(node, 0.0),
            storage_capacity.get(node, float("nan")),
            (holding_cost or {}).get(node, 0.0),
            (shortage_penalty or {}).get(node, 1_000.0),
        )
        if any(not isfinite(float(value)) or float(value) < 0.0 for value in scalars):
            raise ValueError("inventory node parameters are invalid")
    for table, name in ((supply, "supply"), (demand, "demand")):
        if any(
            not 0 <= int(time) < periods
            or node not in node_index
            or not isfinite(float(value))
            or float(value) < 0.0
            for (time, node), value in table.items()
        ):
            raise ValueError(f"dynamic inventory {name} is invalid")

    inventory_keys = [(time, node) for time in range(periods) for node in ordered_nodes]
    shipment_keys = [
        (time, arc_index)
        for time in range(periods)
        for arc_index, arc in enumerate(checked_arcs)
        if time + arc.travel_time < periods
    ]
    offset_inventory = 0
    offset_shipments = len(inventory_keys)
    offset_unmet = offset_shipments + len(shipment_keys)
    offset_waste = offset_unmet + len(inventory_keys)
    variable_count = offset_waste + len(inventory_keys)
    inventory_position = {key: offset_inventory + index for index, key in enumerate(inventory_keys)}
    shipment_position = {key: offset_shipments + index for index, key in enumerate(shipment_keys)}
    unmet_position = {key: offset_unmet + index for index, key in enumerate(inventory_keys)}
    waste_position = {key: offset_waste + index for index, key in enumerate(inventory_keys)}

    objective = np.zeros(variable_count)
    bounds: list[tuple[float, float | None]] = [(0.0, None)] * variable_count
    for key, position in inventory_position.items():
        objective[position] = float((holding_cost or {}).get(key[1], 0.0))
        bounds[position] = (0.0, float(storage_capacity[key[1]]))
        objective[unmet_position[key]] = float((shortage_penalty or {}).get(key[1], 1_000.0))
    for (time, arc_index), position in shipment_position.items():
        del time
        arc = checked_arcs[arc_index]
        objective[position] = arc.cost
        bounds[position] = (0.0, arc.capacity)

    equality = np.zeros((len(inventory_keys), variable_count))
    rhs = np.zeros(len(inventory_keys))
    for row, (time, node) in enumerate(inventory_keys):
        equality[row, inventory_position[(time, node)]] = 1.0
        if time > 0:
            equality[row, inventory_position[(time - 1, node)]] = -1.0
        for (departure, arc_index), position in shipment_position.items():
            arc = checked_arcs[arc_index]
            if departure == time and arc.source == node:
                equality[row, position] += 1.0
            if departure + arc.travel_time == time and arc.target == node:
                equality[row, position] -= 1.0
        equality[row, unmet_position[(time, node)]] = -1.0
        equality[row, waste_position[(time, node)]] = 1.0
        rhs[row] = float(supply.get((time, node), 0.0)) - float(demand.get((time, node), 0.0))
        if time == 0:
            rhs[row] += float(initial_inventory.get(node, 0.0))
    solved = linprog(objective, A_eq=equality, b_eq=rhs, bounds=bounds, method="highs")
    if not solved.success:
        raise RuntimeError(f"dynamic inventory flow failed: {solved.message}")
    shipment_result = {
        (time, checked_arcs[arc_index].source, checked_arcs[arc_index].target): float(solved.x[position])
        for (time, arc_index), position in shipment_position.items()
        if solved.x[position] > 1e-12
    }
    return DynamicFlowResult(
        {key: float(solved.x[position]) for key, position in inventory_position.items()},
        shipment_result,
        {key: float(solved.x[position]) for key, position in unmet_position.items()},
        {key: float(solved.x[position]) for key, position in waste_position.items()},
        float(solved.fun),
    )
