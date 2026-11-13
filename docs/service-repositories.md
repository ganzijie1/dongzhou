# Dongzhou service repositories

The four AI repositories are pinned Git submodules under `services/`:

| Directory | GitHub repository | Branch | Role |
| --- | --- | --- | --- |
| `services/knowledge-jizhan` | `ganzijie1/knowledge-jizhan` | `dev-gzj` | Dongzhou source material and retrieval service |
| `services/ainpc` | `ganzijie1/ainpc` | `dev-gzj` | NPC state, schedules, dialogue, and durable answer delivery |
| `services/orgFlowEngine` | `ganzijie1/orgFlowEngine` | `dev-gzj` | Office hierarchy and durable virtual tasks |
| `services/NexusKernel` | `ganzijie1/NexusKernel` | `dev-gzj` | Embedded gateway runtime |

## Clone and update

Use `--recurse-submodules` for a fresh clone. For an existing checkout:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
python tools/verify-service-submodules.py
```

To advance a service deliberately, fetch its sanitized GitHub branch, check out the reviewed commit inside that service directory, run its tests, then commit the changed gitlink in Dongzhou. The parent repository must continue to pin an exact commit; do not leave a submodule merely following an unreviewed branch tip.

The internal GitLab repositories are not configured as submodule remotes and must never be push targets from this repository.

Current AINPC pin: `633a0b653` (`dev-gzj`). Its adviser answer delivery recovery, large-player feedback fix, knowledge recall budget, and live acceptance are recorded in [2026-11-13-ainpc-adviser-delivery-recovery.md](2026-11-13-ainpc-adviser-delivery-recovery.md).

Current orgFlowEngine pin: `bdd432c` (`dev-gzj`). Deterministic private-chat failures now converge instead of remaining indefinitely queued. Follow-up messages owned by an AINPC-created original chat reach `FAILED/npc_original_chat_owned` in dependency order, while genuinely transient states such as `WAITING_ACTIVE` remain retryable. Live task `866d1e9c-7ecd-507d-badb-24161e91222d` confirmed its `END` and `ACTION_PROMPT` messages both converged without creating a duplicate private chat.
