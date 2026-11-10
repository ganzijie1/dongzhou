"use strict";

const assert = require("assert");
const play = require("../web-game/organization-play.js");

const stage = {
  id: "01",
  battleTitle: "东郊索命",
  stage: { deploy: { unselectables: [{ hero: "ZuoRu" }], selectables: [] } }
};

let state = play.syncMembers(null, stage, () => "左儒");
state = play.recordKnowledge(state, {
  id: "dongzhou_stage_001",
  stageId: "01",
  name: "东郊旧闻",
  summary: "杜伯蒙冤，东郊军心不稳。",
  sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }]
});
state = play.selectEvidence(state, { stageId: "01", knowledgeId: "dongzhou_stage_001", sourceIndex: 0 }).state;
const councilInput = {
  id: "00000000-0000-4000-8000-000000000001",
  stageId: "01",
  memberId: "ZuoRu",
  knowledgeId: "dongzhou_stage_001",
  evidenceSourceIndex: 0,
  question: "如何部署？\n选证：《史记·周本纪》｜史实骨架",
  options: ["固守", "强攻"],
  index: 1
};
const council = play.recordCouncil(state, councilInput);
state = council.state;

const mandate = {
  id: "dongzhou:player:00000000-0000-4000-8000-000000000002",
  stageId: "01",
  stageTitle: "东郊索命",
  heroId: "ZuoRu",
  taskType: "drill",
  evidence: { id: "dongzhou_stage_001", name: "东郊旧闻", summary: "杜伯蒙冤", source: { index: 0, work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" } },
  council: { requestId: councilInput.id, index: 1, text: "强攻" },
  assignment: { heroId: "ZuoRu", npcId: "42", runtimeState: "READY", planId: "plan-1", generationId: "gen-1", eventId: "event-drill", transactionId: 9100102, name: "检阅军阵", type: "军事", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "calm", intensity: 0, affectionCount: 0, relationshipCount: 0 } },
  kernel: { module: "dongzhou_runtime", moduleVersion: "1.0.0", nexusKernelVersion: "0.2.0", state: "READY" },
  digest: "a".repeat(64),
  state: "ISSUED"
};

const recorded = play.recordMandate(state, mandate);
state = recorded.state;
assert.strictEqual(state.mandates.length, 1);
assert.throws(() => play.recordMandate(state, { ...mandate, id: mandate.id + "-draft", state: "DRAFT" }), /尚未签发/);
assert.throws(() => play.recordMandate(state, { ...mandate, digest: "b".repeat(64) }), /冲突/);

const created = play.createTask(state, {
  type: "drill",
  assigneeId: "ZuoRu",
  stageId: "01",
  stageTitle: "东郊索命",
  knowledgeId: "dongzhou_stage_001",
  councilId: councilInput.id,
  mandateId: mandate.id
});
created.task.remoteResult = "remote-mandate-task";
assert.strictEqual(created.task.mandate.digest, mandate.digest);
assert.throws(() => play.createTask(state, {
  type: "patrol",
  assigneeId: "ZuoRu",
  stageId: "01",
  knowledgeId: "dongzhou_stage_001",
  councilId: councilInput.id,
  mandateId: mandate.id
}), /内核军令.*不匹配/);

state = play.reconcileRemoteTasks(created.state, [{
  task_id: "remote-mandate-task",
  state: "SUCCEEDED",
  final_result: "SUCCESS",
  version: 3
}]);
assert.strictEqual(state.mandates[0].state, "FULFILLED");
assert.strictEqual(state.pendingSupport[0].mandate.id, mandate.id);

const prepared = play.consumeSupport(state, "01");
assert.strictEqual(prepared.support.mandates[0].id, mandate.id);
const reported = play.recordBattleOutcome(prepared.state, {
  id: "battle:01:1",
  stageId: "01",
  stageTitle: "东郊索命",
  won: true,
  turns: 8,
  ownLosses: 1,
  terminalReason: "victory",
  support: prepared.support
});
assert.strictEqual(reported.state.mandates[0].state, "RESOLVED");
assert.deepStrictEqual(reported.state.mandates[0].outcome, { won: true, turns: 8, ownLosses: 1 });
assert.strictEqual(reported.report.mandates[0].digest, mandate.digest);
assert.ok(reported.state.archives.at(-1).text.includes("内核军令已结案"));

console.log("PASS knowledge -> NPC council -> Nexus mandate -> organization task -> battle outcome");
