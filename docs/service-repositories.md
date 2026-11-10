# Dongzhou service repositories

The four AI repositories are pinned Git submodules under `services/`:

| Directory | GitHub repository | Branch | Role |
| --- | --- | --- | --- |
| `services/knowledge-jizhan` | `ganzijie1/knowledge-jizhan` | `dev-gzj` | Dongzhou source material and retrieval service |
| `services/ainpc` | `ganzijie1/ainpc` | `dev-gzj` | NPC state, schedules, dialogue, and delivery |
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
