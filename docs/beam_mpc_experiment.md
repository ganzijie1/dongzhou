# Beam MPC experiment

The snapshot-driven beam planner in `rl/beam_mpc.py` supports both rule-only
candidate ordering and a HAPPO log-probability prior. It executes only the first
action and replans from the next real state. Search stops at the opponent turn
boundary so a maximizing beam never treats the opponent as cooperative.

The native restore protocol also resets a speculative victory or defeat before
rebuilding legal actions. This lets a terminal rollout return to its live root
without restarting the native process.

Run a matched comparison with an existing HAPPO checkpoint:

```powershell
python -m rl.compare_beam_mpc `
  --executable build\rl-vcpkg\game\src\rl\Release\mengde_rl.exe `
  --scenario dongzhou --happo-model <happo.pt> `
  --eval-episodes 10 --max-episode-actions 160 `
  --horizon 2 --beam-width 4 --candidates 4
```

The command evaluates pure HAPPO, pure beam MPC, and HAPPO-prior beam MPC with
the same scenario, seeds, and action limit. The report includes return, win
rate, action count, expanded nodes, and decision latency. Without a checkpoint,
`--train-steps` creates a temporary baseline. `--teacher-episodes` and
`--teacher-updates` enable beam-teacher actor pretraining before HAPPO updates.

## Short local baseline

The implementation smoke benchmark used 2,048 HAPPO environment steps, three
evaluation seeds, and an 80-action limit:

| Policy | Mean return | Win rate | Mean decision time |
|---|---:|---:|---:|
| HAPPO | -12.493 | 0% | 4.83 ms |
| Pure beam MPC | 0.247 | 0% | 73.02 ms |
| HAPPO-prior beam MPC | -1.162 | 0% | 109.53 ms |

This HAPPO baseline is clearly undertrained. The result only shows that a weak
prior can hurt hybrid search; it does not compare mature HAPPO fairly against
beam MPC. The runtime policy remains unchanged. Re-run this entry point with
the established strong checkpoint before considering deployment.

## Matched example benchmark

The original online benchmark protocol was reproduced with 4,096 HAPPO
environment steps, seed 2026, ten evaluation episodes, and a 100-action limit.
Both beam variants used horizon 2, beam width 4, and four candidates per node.

| Policy | Mean return | Win rate | Mean actions | Mean decision time |
|---|---:|---:|---:|---:|
| HAPPO | 24.222 | 100% | 22.6 | 3.34 ms |
| Pure beam MPC | 15.665 | 60% | 63.4 | 78.84 ms |
| HAPPO-prior beam MPC | 24.693 | 100% | 10.8 | 107.00 ms |

This confirms that pure search does not replace HAPPO. The HAPPO prior makes
the same search budget substantially stronger and cuts the completed battle's
action count by 52.2%, while increasing per-decision latency by about 32 times
over HAPPO alone. This is evidence for an optional teacher or difficult-state
planner, not yet for replacing the multi-stage runtime policy.
