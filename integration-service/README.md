# Dongzhou integration service

This package preserves the four repositories' Dongzhou contracts behind one browser-facing boundary. NexusKernel runs in-process; AINPC, orgFlowEngine and knowledge-jizhan are represented by pinned local contracts and game-owned state, never by reachable service processes.

## Local isolation

The checked-in build is permanently disconnected from the former AINPC, orgFlow and knowledge HTTP services. `Upstreams` does not create a network client and rejects every transport except `httpx.MockTransport`, which is used only by in-process contract tests. Starting the gateway cannot probe or call the configured service URLs.

The browser game remains available as an explicit standalone simulation:

```powershell
cd integration-service
uv sync --extra dev
uv run uvicorn dongzhou_integration.app:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/?offline=1`. Do not start the former four-service containers or processes.

Standalone history quizzes load only `scenario/dongzhou-knowledge.json` and `scenario/service-sources.json`. Questions omit the correct index until answered; completed receipts are recomputed and verified locally with the pinned four-repository provenance.

Standalone history commendations and recollections use the same published records after the player selects an exact source in the court. Commendations bind the local player, stage and active officer to an idempotent `dongzhou_npc_commendation 1.1.0` receipt. Recollections derive a stable local AINPC memory receipt from that published record and seal it as `dongzhou_npc_recollection 1.2.0`. Replays rebuild both receipts from source, and changed evidence or journal content is rejected without an API request.

Standalone officer thoughts and council decisions run the AINPC interaction contract in-process. The selected published source, local duty assignment, officer, stage and optional sealed memory produce a deterministic thought receipt and council proposal. The local decision journal prefers that proposal, binds the same four-repository provenance and is revalidated before the existing organization council recorder accepts it.

Every standalone non-procedural battle passes the same local four-repository gate. The browser binds the published stage knowledge, local court roster, local AINPC actor set, selected campaign route and exact battle plan into `dongzhou_battle_readiness 1.3.0` and `dongzhou_battle_deployment 1.3.0` receipts. Both receipts are journaled and reverified before a saved battle can resume. This path reads static files and browser storage only; it sends no `/api/` request and starts no service process.

Standalone battle debriefs use the sealed deployment and battle-time roster rather than any current service state. Published local knowledge, local actor memories and applied support traces are recomputed into the existing `dongzhou_battle_debrief 1.2.0` contract. Historical review therefore remains available after the court roster changes, while a changed report, deployment, source manifest or support trace is rejected.

Standalone adviser questions use those same two static files. The browser applies AINPC's published intent and guide state contract in-process, binds answers to the local `列国军府` authority, and seals accepted guide transitions with the Nexus `dongzhou_adviser_guide 1.1.0` shape. Reads, feedback, decisions, status changes and cancellation all rebuild the answer from local knowledge before accepting the journal; no `/api/` request or service process is involved.

## Legacy connected-mode notes (inactive)

The notes below describe the former connected deployment and remain only as schema and migration context. They are not current operating instructions and must not be used to restart containers, processes, callbacks, health probes, or private-network access.

- Use one gateway process per SQLite volume. The image deliberately starts one worker; scale-out requires replacing `Store` with the shared database implementation first.
- Put TLS at the ingress and set `DONGZHOU_PUBLIC_ORIGIN` to the exact public origin.
- Generate a random `DONGZHOU_SESSION_SECRET` of at least 32 characters in the secret manager.
- Issue separate tokens of at least 32 characters for AINPC and knowledge-jizhan. Production startup rejects empty tokens, local knowledge fallback, mismatched game-server IDs, credential-bearing upstream URLs, and insecure public origins. orgFlowEngine uses a 32-byte-or-longer HMAC secret with replay-protected request signatures; keep every credential out of the H5.
- Integration readiness accepts knowledge-jizhan only when its health payload reports `healthy`, Qdrant, Elasticsearch, and Neo4j are all `up`, and the published index contains every ID from `dongzhou_stage_001` through `dongzhou_stage_172`. A reachable but degraded, empty, or same-sized but incomplete knowledge process remains offline.
- Publish `config/organizations/dongzhou_court_v7.json`, provision a `dongzhou_court` organization, and map every playable hero to both its live slot and active member with `DONGZHOU_ORGFLOW_HERO_SLOTS` and `DONGZHOU_ORGFLOW_HERO_MEMBERS`. Both mappings must contain the same hero IDs so a player-selected assignee cannot be replaced by a recommendation for another member. Integration readiness also reads the signed roster and requires the configured organization ID, active state, v7 template, and the exact 13-seat court contract; a generic healthy orgFlow process is not enough.
- Set `DONGZHOU_AINPC_TASK_TOKEN` to AINPC's `ORGANIZATION_TASK_SERVICE_BEARER_TOKEN`. When a remote office task reaches its due month, the save transaction creates one durable report-dialogue event; retries reuse the same operation ID and AINPC submits the NPC's result through the normal orgFlow review path.
- NPC readiness is reconciled against AINPC's complete live actor snapshot, not only the gateway's persisted `READY` rows. The gateway retries incomplete topology snapshots, reads all pages, and reactivates missing actors every 30 seconds, so an AINPC instance restart does not require a browser refresh or manual `/npcs/sync` call. Gateway restarts preserve actors that are already online, while missing persisted actors are reactivated with their original login request ID; both paths prevent in-flight organization notifications from being invalidated by an unnecessary owner-incarnation change.
- Court mandates use AINPC V2's canonical global emergency-assessment callback before sealing. The aligned decision, score, and interrupt trace are included in the NexusKernel digest and in the orgFlow task brief; malformed or unavailable assessments leave the idempotent mandate retryable instead of silently inventing an urgency result.
- NPC state reads the canonical AINPC personality profile with `auto_initialize=false`. A task-specific fit score is calculated for supply, drill, patrol, intelligence, and diplomacy, contributes to readiness, is sealed by NexusKernel, and is copied into the orgFlow task brief. Missing profiles remain playable with a neutral factor; the gateway never creates or mutates personality data.
- `DONGZHOU_GAME_SERVER_ID` remains part of historical save identities. The former AINPC/orgFlow clock and callback configuration is retained only for schema compatibility and is not contacted by this build.
- Back up `/data/dongzhou-integration.sqlite3` with SQLite's online backup API or a volume snapshot. Do not copy a live WAL database as loose files.
- Build from the `dongzhou` repository. NexusKernel is pinned inside `services/NexusKernel` and is copied from the normal build context:

```powershell
docker build -f integration-service/Dockerfile -t dongzhou-integration:1.0.0 .
```

## Historical AINPC schema contracts

The gateway implements the AINPC private-chat transport and runtime contracts at the game-server root:

- `POST /api/v2/NDLLMChatWithPlayer` creates an idempotent private-chat session.
- `POST /api/v2/NDLLMSendPrivateMessage` persists the frozen message before returning success and emits a durable delivery callback.
- `POST /api/v2/QueryPrivateChatRuntimeState` projects persisted sessions and messages without exposing PII.
- `POST /api/v2/ResetPrivateChatRuntimeState` is an idempotent no-op because Dongzhou has no game-side pending-send or waiting-reply queue; it returns a fresh authoritative projection.
- `POST /api/v2/ValidateBTParams` strictly validates the locally supported `SleepTree`, `DongzhouDutyTree`, and runtime `Reborn` parameters; unsupported trees return `valid=false` rather than a fabricated success.
- `POST /api/v2/ExecuteBehavior` accepts only a ready NPC and the same validated parameters. A duty must carry one of the 11 authoritative Dongzhou schedule ID/name pairs; mismatched identities are rejected. `Reborn` reports its exact physical UID immediately, while rest and duty actions remain in flight for their declared duration before reporting completion. Accepted results use the SQLite outbox, so gateway restarts preserve their due time and immutable schedule context; duplicate UIDs reuse the same payload or fail on a conflict.
- Gateway startup republishes the single Dongzhou autonomous-duty action through AINPC's formal append-only catalog synchronization contract. The synchronization itself is an outbox event and is retried across gateway restarts; AINPC retains the resulting catalog in MongoDB. It never clears actions owned by another game.

Never infer delivery from an accepted chat request. Only the delivery callback proves that the game server persisted the message.

## Verification

```powershell
uv run pytest
node ..\tools\test-organization-play.js
node ..\tools\test-integration-client.js
node --check ..\web-game\integration-client.js
node --check ..\web-game\game.js
```
