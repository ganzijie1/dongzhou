# Dongzhou integration service

This NexusKernel service is the only browser-facing boundary for Dongzhou. It owns signed player sessions, versioned saves, stable AINPC identities, discovered knowledge, idempotency records, and the translation to the formal orgFlow virtual-task API. Its readiness and integration-status responses expose NexusKernel as the embedded runtime alongside the three external services, so delivery checks prove all four repository capabilities are active.

## Local run

Initialize the pinned service repositories once from the Dongzhou root, then run the gateway from `integration-service`:

```powershell
git submodule update --init --recursive services/knowledge-jizhan services/ainpc services/orgFlowEngine services/NexusKernel
cd integration-service
uv sync --extra dev
uv run uvicorn dongzhou_integration.app:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`. Add `?offline=1` only for an explicit standalone simulation; production never silently falls back.

## Production invariants

- Use one gateway process per SQLite volume. The image deliberately starts one worker; scale-out requires replacing `Store` with the shared database implementation first.
- Put TLS at the ingress and set `DONGZHOU_PUBLIC_ORIGIN` to the exact public origin.
- Generate a random `DONGZHOU_SESSION_SECRET` of at least 32 characters in the secret manager.
- Issue separate tokens of at least 32 characters for AINPC and knowledge-jizhan. Production startup rejects empty tokens, local knowledge fallback, mismatched game-server IDs, credential-bearing upstream URLs, and insecure public origins. orgFlowEngine uses a 32-byte-or-longer HMAC secret with replay-protected request signatures; keep every credential out of the H5.
- Publish `config/organizations/dongzhou_court_v2.json`, provision a `dongzhou_court` organization, and map every playable hero to both its live slot and active member with `DONGZHOU_ORGFLOW_HERO_SLOTS` and `DONGZHOU_ORGFLOW_HERO_MEMBERS`. Both mappings must contain the same hero IDs so a player-selected assignee cannot be replaced by a recommendation for another member.
- Set `DONGZHOU_AINPC_TASK_TOKEN` to AINPC's `ORGANIZATION_TASK_SERVICE_BEARER_TOKEN`. When a remote office task reaches its due month, the save transaction creates one durable report-dialogue event; retries reuse the same operation ID and AINPC submits the NPC's result through the normal orgFlow review path.
- NPC readiness is reconciled against AINPC's complete live actor snapshot, not only the gateway's persisted `READY` rows. The gateway retries incomplete topology snapshots, reads all pages, and reactivates missing actors every 30 seconds, so an AINPC instance restart does not require a browser refresh or manual `/npcs/sync` call.
- Court mandates use AINPC V2's canonical global emergency-assessment callback before sealing. The aligned decision, score, and interrupt trace are included in the NexusKernel digest and in the orgFlow task brief; malformed or unavailable assessments leave the idempotent mandate retryable instead of silently inventing an urgency result.
- Set `DONGZHOU_GAME_SERVER_ID` to the same non-zero numeric ID used by AINPC and orgFlowEngine (`91001` by default). Configure orgFlowEngine's clock URL as `http://gateway:8765/api/v1/QueryGameTimeAndTimeScale`; the gateway exposes a monotonic, event-driven clock derived from accepted campaign saves.
- Back up `/data/dongzhou-integration.sqlite3` with SQLite's online backup API or a volume snapshot. Do not copy a live WAL database as loose files.
- Build from the `dongzhou` repository. NexusKernel is pinned inside `services/NexusKernel` and is copied from the normal build context:

```powershell
docker build -f integration-service/Dockerfile -t dongzhou-integration:1.0.0 .
```

## AINPC game-server contracts

The gateway implements the AINPC private-chat transport and runtime contracts at the game-server root:

- `POST /api/v2/NDLLMChatWithPlayer` creates an idempotent private-chat session.
- `POST /api/v2/NDLLMSendPrivateMessage` persists the frozen message before returning success and emits a durable delivery callback.
- `POST /api/v2/QueryPrivateChatRuntimeState` projects persisted sessions and messages without exposing PII.
- `POST /api/v2/ResetPrivateChatRuntimeState` is an idempotent no-op because Dongzhou has no game-side pending-send or waiting-reply queue; it returns a fresh authoritative projection.

Never infer delivery from an accepted chat request. Only the delivery callback proves that the game server persisted the message.

## Verification

```powershell
uv run pytest
node ..\tools\test-organization-play.js
node ..\tools\test-integration-client.js
node --check ..\web-game\integration-client.js
node --check ..\web-game\game.js
```
