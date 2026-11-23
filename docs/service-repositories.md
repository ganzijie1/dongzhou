# Dongzhou service repositories

The four AI repositories are imported from the internal GitLab SSH repositories and pinned as exact Git submodule commits under `services/`:

| Directory | GitLab SSH source | Source branch | Dongzhou pin | Role |
| --- | --- | --- | --- | --- |
| `services/knowledge-jizhan` | `ssh://git@git.nd.com.cn:10022/AIGames/knowledge-jizhan.git` | `main@45afa2f` | `660d65b2` | Dongzhou source material and retrieval service |
| `services/ainpc` | `ssh://git@git.nd.com.cn:10022/AIGames/ainpc.git` | `develop@8a7b673c6` | `eb6189f93` | NPC state, schedules, dialogue, and durable answer delivery |
| `services/orgFlowEngine` | `ssh://git@git.nd.com.cn:10022/AIGames/orgFlowEngine.git` | `develop@8b1049e` | `fbfc803b` | Office hierarchy and durable virtual tasks |
| `services/NexusKernel` | `ssh://git@git.nd.com.cn:10022/AIGames/NexusKernel.git` | `develop@190abb1` | `2a68d6b` | Embedded gateway runtime |

## Clone and update

Use `--recurse-submodules` for a fresh clone. For an existing checkout:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
python tools/verify-service-submodules.py
```

The verifier also requires every service worktree to be clean. A dirty submodule means the parent gitlink cannot reproduce the code being tested, even when its checked-out `HEAD` still matches the recorded commit.

After the gateway is running, use the unified read-only check:

```powershell
python tools/verify_four_service_runtime.py
```

It verifies the four source and integration pins, regenerates the formal Dongzhou court v7 bundle into a temporary directory and compares it structurally with the tracked asset, then checks the live source seal and all required Nexus modules. Use `--skip-live` when only the checkout and generated assets are available. The command has no publish or execution mode.

To advance a service deliberately, first fast-forward the matching `E:/game/<repository>` checkout from its GitLab SSH source. Import that reviewed source commit into the service's `dev-gzj` branch, preserve the Dongzhou-specific integration commits, run its tests, then commit the changed gitlink in Dongzhou. The parent repository must continue to pin an exact commit; do not leave a submodule merely following an unreviewed branch tip.

The `.gitmodules` URLs remain the sanitized publishing mirrors. Internal GitLab repositories are read-only input sources for this workspace and are not push targets from Dongzhou.

Current AINPC pin: `eb6189f93` (`dev-gzj`), containing GitLab `develop@8a7b673c6`. Its Gateway readiness now reports that reviewed GitLab source so Dongzhou can reject an unattested runtime. Its adviser answer delivery recovery, large-player feedback fix, knowledge recall budget, and live acceptance are recorded in [2026-11-13-ainpc-adviser-delivery-recovery.md](2026-11-13-ainpc-adviser-delivery-recovery.md). AI Helper callbacks now use the configured AIFirewall HMAC filter instead of the retired DES sensitive-word endpoint. The local container reaches that service through the host loopback bridge on port `8090`; live question `1fcce851-19f7-4b8b-bc1f-7b45e4742607` confirmed both the loading and answer callbacks completed with `filter_degraded=false`.

Runtime fallback rest now always instantiates AINPC's fixed `SleepTree` chain, including when the generation snapshot is outside a core map or temporarily lacks a scene. Dongzhou implements the matching strict parameter precheck and physical execution callback contract: unsupported trees remain rejected, `Reborn` closes immediately, and `SleepTree` stays in flight for its declared duration. Callback identity and due time live in the SQLite outbox, survive a gateway restart, and reject a conflicting reuse of the same physical UID. Live deployment produced exactly 12 accepted rest chains after a clean AINPC restart, with no parameter-precheck, empty-chain, model-configuration, or premature-completion failures during the acceptance window.

The other 11 Dongzhou schedule types now use a game-specific transaction/action overlay and deterministic `DongzhouDutyTree` templates instead of the unrelated legacy-game action catalog. The gateway republishes that one action through AINPC's formal catalog callback, then requires the immutable `scheduleId/scheduleName` pair to match the Dongzhou catalog before accepting execution. Duty duration follows the committed plan and both the due callback and full schedule context are retained in the SQLite outbox. Live contract acceptance stored and delivered a three-second `巡察营垒` duty with ID `9100104`; the same ID paired with `转运军粮` was rejected with `422 / dongzhou_duty_identity_invalid`.

Completed organization chats now return an explicit terminal acknowledgement for exact late delivery receipts. The acknowledgement stops the durable authority-effect queue without claiming that stale evidence was written or changing the historical message. After deploying `v20261114-dongzhou-local-organization-delivery-terminal85`, all eight AINPC roles were healthy; five pending November 8 `npc-task-*` receipts drained once with `terminal=true`, then stopped reappearing in the following recovery interval.

Character-profile composition now projects quality-owner material into the narrower profile contract instead of forwarding the internal `value_order` field. With `v20261114-dongzhou-local-character-profile-contract86`, all eight roles were healthy, startup produced 17 successful profile reads and zero validation failures, and live queries for Du Bo, Zheng Zhuang Gong, and Guo Shifu each returned `code=200` with 12 personality and 15 quality dimensions.

Production private chat reads LoongEQ's native `guidance/v1` profile and `eq-abilities-v2` dimensions. The legacy temporary testing profile remains isolated and is not semantically remapped. A missing production profile now invokes LoongEQ's idempotent `/ensure` contract before the first chat; storage failures remain explicit and never create a fabricated local profile. Real-services browser acceptance task `playerchat-4643eac3374c36fe422a4c2b4bc3020a` produced and selected Zuo Ru's reply while preserving player isolation, the shared game clock, organization mutation counts, and mobile layout. During that acceptance LoongEQ reported `guidance_profile_storage_unavailable`, so the reply used AINPC's declared fail-open path; it is evidence for chat continuity and error handling, not evidence that EQ strategy was applied.

Durable-chat recovery now projects historical messages through LoongEQ's final private-chat contract before evaluation: only the current player/NPC pair is retained, wire message IDs are unique, the current message is excluded from history, and future timestamps are clamped to the current turn. Image `v20261114-dongzhou-local-eq-history-contract87` passed 62 focused regressions (one skipped) and all eight roles became healthy. Six live recovered fragments then passed request validation and reached the known external `503 guidance_profile_storage_unavailable` degradation with empty validation errors; no post-deployment request returned the previous body-level `422`.

Current orgFlowEngine, knowledge-jizhan, and NexusKernel pins are `fbfc803b`, `660d65b2`, and `2a68d6b`. All four service pins include the GitLab source revisions listed above plus the reviewed Dongzhou integration commits. AINPC readiness, knowledge health, and orgFlow readiness now report their reviewed GitLab source branch and revision so the gateway can distinguish runtime attestation from its own expected-source manifest. Deterministic private-chat failures now converge instead of remaining indefinitely queued. Follow-up messages owned by an AINPC-created original chat reach `FAILED/npc_original_chat_owned` in dependency order, while genuinely transient states such as `WAITING_ACTIVE` remain retryable. Live task `866d1e9c-7ecd-507d-badb-24161e91222d` confirmed its `END` and `ACTION_PROMPT` messages both converged without creating a duplicate private chat.
