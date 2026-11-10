"use strict";

const assert = require("assert");
const play = require("../web-game/organization-play.js");

const stage = {
  id: "01",
  title: "周宣王闻谣轻杀 杜大夫化厉鸣冤",
  battleTitle: "东郊索命",
  stage: { deploy: { unselectables: [{ hero: "DuBo" }, { hero: "ZuoRu" }], selectables: [] } }
};
let state = play.syncMembers(null, stage, (id) => ({ DuBo: "杜伯", ZuoRu: "左儒" }[id]));
assert.deepStrictEqual(state.members.map((member) => member.name), ["杜伯", "左儒"]);

let created = play.createTask(state, { type: "drill", assigneeId: "DuBo", stageId: "01", stageTitle: "东郊索命", knowledgeId: "dongzhou_stage_001" });
assert.strictEqual(created.task.status, "active");
state = play.advanceMonth(created.state);
assert.ok(["success", "failed"].includes(state.tasks[0].status));
assert.strictEqual(state.month, 2);

state.pendingSupport.push({ id: "forced", stageId: "01", source: "校验", provisions: 20, morale: 8, attack: 0.05, defense: 0.1, recon: 1 });
const consumed = play.consumeSupport(state, "01");
assert.ok(consumed.support.provisions >= 20);
assert.ok(consumed.support.attack >= 0.05);
assert.strictEqual(consumed.state.pendingSupport.some((entry) => entry.id === "forced"), false);
assert.deepStrictEqual(play.consumeSupport(consumed.state, "01").support.sources, []);

state = play.recordKnowledge(consumed.state, { id: "dongzhou_stage_001", name: "第一回", summary: "东郊索命", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }, { work: "《东周列国志》第一回", tier: "文学演绎", scope: "杜伯索命", url: "https://zh.wikisource.org/zh-hans/东周列国志/第001回" }] });
assert.strictEqual(state.knowledge[0].stageId, "01");
assert.throws(() => play.recordCouncil(state, { id: "council-unsealed", stageId: "01", memberId: "ZuoRu", knowledgeId: "dongzhou_stage_001", question: "如何部署", options: ["守", "攻"], index: 0 }), /选定军议依据/);
const selectedEvidence = play.selectEvidence(state, { stageId: "01", knowledgeId: "dongzhou_stage_001", sourceIndex: 0 });
state = selectedEvidence.state;
assert.strictEqual(selectedEvidence.source.tier, "史实骨架");
const council = play.recordCouncil(state, { id: "council-source-1", stageId: "01", memberId: "ZuoRu", knowledgeId: "dongzhou_stage_001", knowledgeName: "第一回", evidenceSourceIndex: 0, question: "如何部署\n选证：《史记·周本纪》｜史实骨架", options: ["守", "攻"], index: 1 });
state = council.state;
assert.strictEqual(council.council.evidenceSource.work, "《史记·周本纪》");
const sealed = play.recordMandate(state, { id: "mandate-source-1", stageId: "01", stageTitle: "东郊索命", heroId: "ZuoRu", taskType: "drill", evidence: { id: "dongzhou_stage_001", name: "第一回", source: { index: 0, work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" } }, council: { requestId: "council-source-1", text: "攻" }, assignment: { heroId: "ZuoRu", npcId: "42", runtimeState: "READY", planId: "plan-1", generationId: "gen-1", eventId: "event-drill", transactionId: 9100102, name: "检阅军阵", type: "军事", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "calm", intensity: 0, affectionCount: 0, relationshipCount: 0 }, readiness: { score: 75, band: "steady", factors: { runtime: 6, duty: 7.2, emotion: 6, support: 0 } } }, kernel: { state: "READY" }, digest: "a".repeat(64), state: "ISSUED" });
state = sealed.state;
const sealedTask = play.createTask(state, { type: "drill", assigneeId: "ZuoRu", stageId: "01", stageTitle: "东郊索命", knowledgeId: "dongzhou_stage_001", councilId: "council-source-1", mandateId: "mandate-source-1" });
assert.strictEqual(sealedTask.task.mandate.evidence.source.tier, "史实骨架");
assert.strictEqual(sealedTask.task.mandate.assignment.readiness.score, 75);
state = play.updateBackend(state, { nexusKernel: true, orgFlow: true, aiNpc: true, knowledge: true });
assert.strictEqual(state.backend.mode, "connected");
state = play.updateBackend(state, { aiNpc: false });
assert.strictEqual(state.backend.mode, "local");
state = play.updateBackend(state, { aiNpc: true });

let remote = play.createTask(state, { type: "supply", assigneeId: "ZuoRu", stageId: "01", stageTitle: "东郊索命" });
remote.task.remoteResult = "00000000-0000-0000-0000-000000000010";
assert.strictEqual(play.remoteTaskReadyForAdvance({ state: "MEMBER_RESPONSE_PENDING", execution_started_game_time: null }), false);
assert.strictEqual(play.remoteTaskReadyForAdvance({ state: "IN_PROGRESS", execution_started_game_time: 24306616800 }), true);
const observed = play.reconcileRemoteTasks(remote.state, [{
  task_id: remote.task.remoteResult, state: "MEMBER_RESPONSE_PENDING", execution_started_game_time: null, version: "2"
}], { advanceMonth: false });
assert.strictEqual(observed.month, remote.state.month, "Observing a pending remote task must not advance the game clock");
assert.strictEqual(observed.tasks.at(-1).remoteState, "MEMBER_RESPONSE_PENDING");
const waiting = play.advanceMonth(remote.state, { resolveLocalTasks: false });
assert.strictEqual(waiting.tasks.at(-1).status, "active");
assert.strictEqual(waiting.pendingSupport.some((entry) => entry.id === remote.task.id), false);
const contributionBefore = remote.state.contribution;
const meritBefore = remote.state.members.find((member) => member.id === "ZuoRu").merit;
const authoritativeSettlement = {
  settlementId: "00000000-0000-0000-0000-000000000020",
  taskId: remote.task.remoteResult,
  organizationId: "00000000-0000-0000-0000-000000000001",
  memberId: "00000000-0000-0000-0000-000000000004",
  result: "SUCCESS",
  organizationDelta: 100,
  memberDelta: 75,
  source: "NPC_CONFIRMATION"
};
const closureReceipt = { state: "SEALED", digest: "c".repeat(64), settlement: authoritativeSettlement };
const pendingReview = {
  state: "REQUIRES_ACTION",
  review: { settlementId: authoritativeSettlement.settlementId, closureDigest: closureReceipt.digest, finalResult: "SUCCESS", state: "PENDING" },
  action: { actionId: "00000000-0000-4000-8000-000000000021", options: ["ACCEPT", "CENSURE"] }
};
assert.strictEqual(play.remoteTaskReadyForAdvance({ final_result: "SUCCESS", settlement: authoritativeSettlement, review: pendingReview }), false);
state = play.reconcileRemoteTasks(remote.state, [{
  task_id: remote.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3",
  settlement: authoritativeSettlement,
  closureReceipt,
  review: pendingReview,
  npcOutcome: { state: "DELIVERED", attempts: 1 }
}], { advanceMonth: false });
assert.strictEqual(state.tasks.at(-1).status, "active");
assert.strictEqual(state.pendingSupport.some((entry) => entry.id === remote.task.id), false);
const acceptedReview = { state: "ACCEPTED", review: { ...pendingReview.review, state: "ACCEPTED", decision: "ACCEPT" } };
state = play.recordTaskReview(state, { taskId: remote.task.remoteResult, review: acceptedReview }).state;
assert.strictEqual(play.remoteTaskReadyForAdvance({ final_result: "SUCCESS", settlement: authoritativeSettlement, review: acceptedReview }), true);
state = play.reconcileRemoteTasks(state, [{
  task_id: remote.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3",
  settlement: authoritativeSettlement, closureReceipt, review: acceptedReview,
  npcOutcome: { state: "DELIVERED", attempts: 1 }
}]);
assert.strictEqual(state.tasks.at(-1).status, "success");
assert.strictEqual(state.tasks.at(-1).remoteVersion, "3");
assert.strictEqual(state.tasks.at(-1).npcOutcome.state, "DELIVERED");
assert.ok(state.pendingSupport.some((entry) => entry.id === remote.task.id));
assert.strictEqual(state.contribution, contributionBefore + 100);
assert.strictEqual(state.members.find((member) => member.id === "ZuoRu").merit, meritBefore + 75);
assert.strictEqual(state.settlements.at(-1).settlementId, authoritativeSettlement.settlementId);
assert.deepStrictEqual(state.settlementIds, [authoritativeSettlement.settlementId]);
assert.strictEqual(state.tasks.at(-1).closureReceipt.digest, "c".repeat(64));

const supportBeforeCensure = state.pendingSupport.length;
const contributionBeforeCensure = state.contribution;
const censuredOrder = play.createTask(state, { type: "patrol", assigneeId: "ZuoRu", stageId: "02", stageTitle: "申斥测试" });
censuredOrder.task.remoteResult = "00000000-0000-0000-0000-000000000030";
const censuredSettlement = { ...authoritativeSettlement, settlementId: "00000000-0000-0000-0000-000000000031", taskId: censuredOrder.task.remoteResult, organizationDelta: 30, memberDelta: 10 };
const censuredClosure = { state: "SEALED", digest: "d".repeat(64), settlement: censuredSettlement };
const censuredPending = { state: "REQUIRES_ACTION", review: { settlementId: censuredSettlement.settlementId, closureDigest: censuredClosure.digest, finalResult: "SUCCESS", state: "PENDING" }, action: { actionId: "00000000-0000-4000-8000-000000000032" } };
let censuredState = play.reconcileRemoteTasks(censuredOrder.state, [{ task_id: censuredOrder.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3", settlement: censuredSettlement, closureReceipt: censuredClosure, review: censuredPending }], { advanceMonth: false });
const censuredReview = { state: "CENSURED", review: { ...censuredPending.review, state: "CENSURED", decision: "CENSURE" } };
censuredState = play.recordTaskReview(censuredState, { taskId: censuredOrder.task.remoteResult, review: censuredReview }).state;
censuredState = play.reconcileRemoteTasks(censuredState, [{ task_id: censuredOrder.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3", settlement: censuredSettlement, closureReceipt: censuredClosure, review: censuredReview }]);
assert.strictEqual(censuredState.tasks.at(-1).status, "censured");
assert.strictEqual(censuredState.contribution, contributionBeforeCensure + 30, "Authoritative org contribution must still be booked after censure");
assert.strictEqual(censuredState.pendingSupport.length, supportBeforeCensure, "Censured reports must not grant battle support");
assert.match(censuredState.history.at(-1).text, /被申斥/);

// 一位官员长时间等待外部复命时，其他官员反复办差不能把该任务挤出台账。
let campaign = play.syncMembers(null, stage, (id) => id);
const longRunning = play.createTask(campaign, { type: "intelligence", assigneeId: "DuBo", stageId: "01" });
longRunning.task.remoteResult = "remote-long-running";
campaign = longRunning.state;
const issuedIds = new Set([longRunning.task.id]);
for (let index = 0; index < 100; index += 1) {
  const order = play.createTask(campaign, { type: "supply", assigneeId: "ZuoRu", stageId: "02" });
  assert.ok(!issuedIds.has(order.task.id), "Task IDs must not repeat after history truncation");
  issuedIds.add(order.task.id);
  order.task.remoteResult = `remote-${index}`;
  campaign = play.reconcileRemoteTasks(order.state, [{ task_id: order.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3" }]);
  campaign = play.normalizeState(JSON.parse(JSON.stringify(campaign)));
}
assert.ok(campaign.tasks.some((task) => task.id === longRunning.task.id && task.status === "active"));
assert.strictEqual(campaign.tasks.filter((task) => task.status !== "active").length, 40);
assert.strictEqual(campaign.pendingSupport.length, 100, "Unspent rewards survive save/load");
assert.throws(() => play.createTask(campaign, { type: "patrol", assigneeId: "DuBo" }), /已有差事/);
const beforeReplay = campaign.pendingSupport.length;
campaign = play.reconcileRemoteTasks(campaign, [{ task_id: "remote-99", state: "SUCCEEDED", final_result: "SUCCESS", version: "3" }]);
assert.strictEqual(campaign.pendingSupport.length, beforeReplay, "Repeated final snapshots must not grant duplicate rewards");
const unrelatedBattle = play.consumeSupport(campaign, "01");
assert.strictEqual(unrelatedBattle.state.pendingSupport.length, 100);
const preparedBattle = play.consumeSupport(unrelatedBattle.state, "02");
assert.strictEqual(preparedBattle.support.provisions, 2400);
assert.strictEqual(preparedBattle.state.pendingSupport.length, 0);
assert.strictEqual(play.consumeSupport(preparedBattle.state, "02").support.provisions, 0);

// 旧存档没有计数器，迁移时仍能从已保存的编号继续，而非从短台账长度重新起算。
const legacy = JSON.parse(JSON.stringify(campaign));
delete legacy.taskSequence;
const migrated = play.createTask(legacy, { type: "supply", assigneeId: "ZuoRu", stageId: "02" });
assert.ok(!issuedIds.has(migrated.task.id));
assert.strictEqual(migrated.state.taskSequence, 102);

console.log(JSON.stringify({ result: "PASS", tasks: state.tasks.length, members: state.members.length, knowledge: state.knowledge.length, longCampaignOrders: issuedIds.size, retainedUnspentRewards: beforeReplay, legacyMigration: "PASS" }));
