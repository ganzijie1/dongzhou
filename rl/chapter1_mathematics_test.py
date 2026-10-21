import math

import numpy as np
import pytest

from rl.chapter1_planning_math import (
    FinitePOSG,
    fast_marching,
    simulate_event_triggered_control,
    stochastic_shortest_path,
)
from rl.chapter1_reliability_rare_math import (
    analyze_absorbing_markov_chain,
    bernoulli_chernoff_bound,
    bernoulli_large_deviation_rate,
    discrete_renewal_process,
    k_out_of_n_reliability,
    normal_tail_importance_sampling,
    parallel_reliability,
    series_reliability,
    solve_finite_constraints,
)
from rl.chapter1_structure_fields import (
    allen_cahn_phase_field,
    artificial_potential_force,
    equivariance_error,
    equivariant_linear_projection,
    gray_scott_reaction_diffusion,
    invariant_group_average,
    normalized_hypergraph_laplacian,
    permutation_representation,
)


def test_stochastic_shortest_path_finds_proper_low_cost_route():
    transitions = np.zeros((3, 2, 3))
    transitions[0, 0, 2] = 1.0
    transitions[0, 1, 1] = 1.0
    transitions[1, 0, 2] = 1.0
    transitions[1, 1, 1] = 1.0
    transitions[2, :, 2] = 1.0
    result = stochastic_shortest_path(
        transitions,
        [[2.0, 0.5], [0.5, 3.0], [0.0, 0.0]],
        [2],
    )

    assert result.values == pytest.approx([1.0, 0.5, 0.0])
    assert result.policy.tolist() == [1, 0, -1]
    assert result.residual < 1e-9


def test_stochastic_shortest_path_rejects_improper_problem():
    with pytest.raises(ValueError, match="finite proper solution"):
        stochastic_shortest_path([[[1.0, 0.0]], [[0.0, 1.0]]], [[1.0], [0.0]], [1])


def test_posg_updates_belief_and_solves_bayesian_stage_game():
    transitions = np.zeros((2, 2, 2, 2))
    transitions[:, :, :, :] = np.eye(2)[:, None, None, :]
    observations = np.empty((2, 2, 2, 2))
    observations[:, :, 0, :] = [0.8, 0.2]
    observations[:, :, 1, :] = [0.2, 0.8]
    payoffs = np.asarray(
        [
            [[2.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [2.0, 0.0]],
        ]
    )
    game = FinitePOSG(transitions, observations, payoffs)

    update = game.update_belief([0.5, 0.5], 0, 0, 0)
    solution = game.solve_stage(update.belief)

    assert update.observation_probability == pytest.approx(0.5)
    assert update.belief == pytest.approx((0.8, 0.2))
    assert sum(solution.row_strategy) == pytest.approx(1.0)
    assert solution.duality_gap < 1e-8


def test_event_triggered_controller_holds_last_transmitted_state():
    result = simulate_event_triggered_control(
        [[1.0]],
        [[1.0]],
        [[0.5]],
        [4.0],
        steps=3,
        relative_threshold=1.0,
    )

    assert result.triggered == (True, False, True)
    assert result.controls[:, 0] == pytest.approx([-2.0, -2.0, 0.0])
    assert result.states[:, 0] == pytest.approx([4.0, 2.0, 0.0, 0.0])


def test_fast_marching_solves_eikonal_and_respects_obstacles():
    speed = np.ones((3, 3))
    speed[0, 2] = 0.0
    result = fast_marching(speed, [(1, 1)])

    assert result.arrival_times[1, 2] == pytest.approx(1.0)
    assert result.arrival_times[0, 0] == pytest.approx(1.0 + 1.0 / math.sqrt(2.0))
    assert math.isinf(result.arrival_times[0, 2])
    assert not result.accepted[0, 2]


def test_normalized_hypergraph_laplacian_has_constant_nullspace():
    geometry = normalized_hypergraph_laplacian(3, [[0, 1, 2]])

    assert geometry.incidence.shape == (3, 1)
    assert geometry.laplacian @ np.ones(3) == pytest.approx(np.zeros(3))
    assert np.linalg.eigvalsh(geometry.laplacian) == pytest.approx([0.0, 1.0, 1.0])


def test_potential_force_combines_goal_attraction_and_obstacle_repulsion():
    force = artificial_potential_force(
        [0.0, 0.0], [[2.0, 0.0]], [[-0.5, 0.0]], influence_radius=1.0
    )

    assert force[0] > 2.0
    assert force[1] == pytest.approx(0.0)


def test_reaction_diffusion_preserves_homogeneous_fixed_point():
    laplacian = np.asarray([[1.0, -1.0], [-1.0, 1.0]])
    result = gray_scott_reaction_diffusion(
        [1.0, 1.0], [0.0, 0.0], laplacian, steps=10
    )

    assert result.activator == pytest.approx([1.0, 1.0])
    assert result.inhibitor == pytest.approx([0.0, 0.0])
    assert result.activator_history.shape == (11, 2)


def test_phase_field_preserves_pure_phases():
    laplacian = np.asarray([[1.0, -1.0], [-1.0, 1.0]])
    result = allen_cahn_phase_field([1.0, 1.0], laplacian, steps=8)

    assert result.field == pytest.approx([1.0, 1.0])
    assert result.energies[-1] == pytest.approx(0.0)


def test_group_average_and_equivariant_linear_projection():
    actions = permutation_representation([[0, 1], [1, 0]])
    invariant = invariant_group_average([1.0, 3.0], actions)
    projected = equivariant_linear_projection([[1.0, 2.0], [3.0, 4.0]], actions, actions)

    assert invariant == pytest.approx([2.0, 2.0])
    assert equivariance_error(lambda vector: projected @ vector, [[1.0, 2.0]], actions, actions) < 1e-12


def test_absorbing_markov_chain_returns_odds_and_duration():
    result = analyze_absorbing_markov_chain(
        [[0.5, 0.25, 0.25], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )

    assert result.transient_states == (0,)
    assert result.absorption_probabilities[0] == pytest.approx([0.5, 0.5])
    assert result.expected_steps == pytest.approx((2.0,))


def test_discrete_renewal_equation_for_deterministic_interarrival():
    result = discrete_renewal_process([0.0, 1.0], 5)

    assert result.renewal_mass == pytest.approx((1.0, 0.0, 1.0, 0.0, 1.0, 0.0))
    assert result.expected_renewals[-1] == pytest.approx(2.0)


def test_independent_system_reliability_models():
    assert series_reliability([0.9, 0.8]) == pytest.approx(0.72)
    assert parallel_reliability([0.9, 0.8]) == pytest.approx(0.98)
    assert k_out_of_n_reliability([0.5, 0.5, 0.5], 2) == pytest.approx(0.5)


def test_importance_sampling_estimates_rare_normal_tail():
    result = normal_tail_importance_sampling(3.0, samples=30_000, seed=7)

    assert result.estimate == pytest.approx(0.0013499, rel=0.08)
    assert result.standard_error < 5e-5
    assert 0.0 < result.effective_sample_size <= result.samples


def test_large_deviation_rate_and_chernoff_bound():
    rate = bernoulli_large_deviation_rate(0.4, 0.2)
    bound = bernoulli_chernoff_bound(100, 0.4, 0.2)

    assert rate > 0.0
    assert bound == pytest.approx(math.exp(-100 * rate))
    assert bound < 0.01


def test_finite_constraint_solver_reports_sat_and_complete_unsat():
    satisfiable = solve_finite_constraints(
        {"x": range(3), "y": range(3)},
        [lambda values: values["x"] + values["y"] == 3],
    )
    unsatisfiable = solve_finite_constraints(
        {"x": range(2)}, [lambda values: values["x"] > 2]
    )

    assert satisfiable.satisfiable
    assert sum(satisfiable.solutions[0].values()) == 3
    assert not unsatisfiable.satisfiable
    assert unsatisfiable.complete
