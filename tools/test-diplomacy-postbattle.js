"use strict";
const assert = require("assert/strict");
const org = require("../web-game/organization-play.js");

let state = org.defaultState();
state.members = [{ id: "envoy", name: "行人子羽", office: "行人", loyalty: 70, fatigue: 0 }];
state = org.recordKnowledge(state, { id: "history-01", name: "本回史料", summary: "诸侯相攻", stageId: "01" });
const council = org.recordCouncil(state, { id: "council-01", stageId: "01", memberId: "envoy", knowledgeId: "history-01", question: "是否结盟", options: ["结盟", "拒盟"], index: 0 });
state = council.state;
const operation = { kind: "diplomacy", target_id: "qi", target_name: "齐国", proposal: "互通军情" };
let remoteState = org.recordMandate(state, {
  id: "dongzhou:test:diplomacy", stageId: "01", stageTitle: "东郊索命", heroId: "envoy", taskType: "diplomacy",
  evidence: { id: "history-01", name: "本回史料", summary: "诸侯相攻" },
  council: { requestId: "council-01", index: 0, text: "结盟" }, operation,
  kernel: { module: "dongzhou_runtime", moduleVersion: "1.0.0", nexusKernelVersion: "0.2.0", state: "READY" },
  digest: "d".repeat(64), state: "ISSUED"
}).state;
const remoteCreated = org.createTask(remoteState, { type: "diplomacy", assigneeId: "envoy", stageId: "01", stageTitle: "东郊索命", knowledgeId: "history-01", councilId: "council-01", mandateId: "dongzhou:test:diplomacy", operation });
remoteCreated.task.remoteResult = "00000000-0000-0000-0000-000000000077";
remoteState = org.reconcileRemoteTasks(remoteCreated.state, [{ task_id: remoteCreated.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS" }]);
assert.equal(remoteState.diplomacy.lobbying.length, 1);
assert.equal(remoteState.diplomacy.lobbying[0].targetId, "qi");
assert.equal(remoteState.diplomacy.lobbying[0].outcome, "accepted");
assert.equal(remoteState.diplomacy.lobbying[0].mandateId, "dongzhou:test:diplomacy");
assert.equal(org.reconcileRemoteTasks(remoteState, [{ task_id: remoteCreated.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS" }]).diplomacy.relations.qi, 8, "replayed remote result must not change diplomacy twice");
assert.throws(() => org.createTask(remoteState, { type: "diplomacy", assigneeId: "envoy", stageId: "01", stageTitle: "东郊索命", knowledgeId: "history-01", councilId: "council-01", mandateId: "dongzhou:test:diplomacy", operation: { ...operation, target_id: "jin" } }), /外交差事/);
const partialCreated = org.createTask(remoteState, { type: "diplomacy", assigneeId: "envoy", stageId: "01", stageTitle: "东郊索命", knowledgeId: "history-01", councilId: "council-01", mandateId: "dongzhou:test:diplomacy", operation });
partialCreated.task.remoteResult = "00000000-0000-0000-0000-000000000078";
const partialState = org.reconcileRemoteTasks(partialCreated.state, [{ task_id: partialCreated.task.remoteResult, state: "SUCCEEDED", final_result: "PARTIAL" }]);
const partialLobbying = partialState.diplomacy.lobbying.at(-1);
assert.equal(partialLobbying.outcome, "rejected", "partial orgFlow result must not authorize an alliance");
assert.throws(() => org.createAlliance(partialState, { id: "pact:partial", lobbyingId: partialLobbying.id, terms: [operation.proposal] }), /获准/);
const lobbyingInput = { id: "lobby-01", stageId: "01", targetId: "zheng", targetName: "郑国", memberId: "envoy", knowledgeId: "history-01", councilId: "council-01", proposal: "共同御敌", outcome: "accepted", decision: { type: "OPTION", index: 0 } };
const lobbying = org.recordLobbying(state, lobbyingInput);
state = lobbying.state;
assert.equal(state.diplomacy.relations.zheng, 8);
assert.equal(org.recordLobbying(state, lobbyingInput).state.diplomacy.relations.zheng, 8, "replayed lobbying must not change relations twice");
assert.throws(() => org.recordLobbying(state, { ...lobbyingInput, outcome: "rejected" }), /冲突/);

const pact = org.createAlliance(state, { id: "pact-01", lobbyingId: "lobby-01", terms: ["互通军情", "共同御敌"] });
state = pact.state;
assert.equal(state.diplomacy.relations.zheng, 20);
assert.equal(state.diplomacy.alliances[0].status, "active");
assert.throws(() => org.createAlliance(state, { id: "pact-02", lobbyingId: "lobby-01", terms: ["重复盟约"] }), /已有生效盟约/);

state = org.breakAlliance(state, { allianceId: "pact-01", stageId: "02", reason: "夺取制胜先机" }).state;
assert.equal(state.diplomacy.alliances[0].status, "broken");
assert.equal(state.diplomacy.relations.zheng, -15);
assert.throws(() => org.breakAlliance(state, { allianceId: "pact-01", stageId: "02", reason: "重复" }), /没有可背弃/);
assert.equal(org.createAlliance(state, { id: "pact-01", lobbyingId: "lobby-01", terms: ["互通军情", "共同御敌"] }).alliance.status, "broken");
const consumed = org.consumeSupport(state, "02");
assert.equal(consumed.support.attack, 0.06);
assert.equal(consumed.support.morale, -8);
assert.equal(consumed.support.alliances[0].id, "pact-01");

const reportInput = { id: "battle:02:123", stageId: "02", stageTitle: "背盟之战", won: true, turns: 8, ownLosses: 1, terminalReason: "敌军溃败", support: { ...consumed.support, councils: [council.council], orders: [{ id: "order-1", memberId: "envoy", source: "折冲诸侯" }] } };
const reported = org.recordBattleOutcome(consumed.state, reportInput);
state = reported.state;
assert.equal(reported.duplicate, false);
assert.equal(state.battleReports.length, 1);
assert.equal(state.relations.envoy, 4);
assert.equal(state.diplomacy.alliances[0].status, "resolved");
assert.equal(state.battleReports[0].betrayal.targetName, "郑国");
const replayed = org.recordBattleOutcome(state, reportInput);
assert.equal(replayed.duplicate, true);
assert.equal(replayed.state.relations.envoy, 4, "replayed result must not change relations twice");
assert.equal(replayed.state.archives.filter((entry) => entry.type === "battle").length, 1);
assert.throws(() => org.recordBattleOutcome(state, { ...reportInput, won: false }), /冲突/);

const migrated = org.normalizeState({ schemaVersion: 1, relations: null, history: [{ text: "旧档" }] });
assert.equal(migrated.schemaVersion, org.SCHEMA_VERSION);
assert.deepEqual(migrated.diplomacy, { lobbying: [], alliances: [], relations: {} });
assert.deepEqual(migrated.battleReports, []);
assert.equal(migrated.history[0].text, "旧档");

console.log(JSON.stringify({ result: "PASS", chain: ["史料", "军议", "游说", "盟约", "背盟战役", "战后回报"], relationExactlyOnce: true, legacyMigration: true }));
