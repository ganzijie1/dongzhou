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

state = play.recordKnowledge(consumed.state, { id: "dongzhou_stage_001", name: "第一回", summary: "东郊索命", stageId: "01" });
assert.strictEqual(state.knowledge[0].stageId, "01");
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
state = play.reconcileRemoteTasks(remote.state, [{
  task_id: remote.task.remoteResult, state: "SUCCEEDED", final_result: "SUCCESS", version: "3"
}]);
assert.strictEqual(state.tasks.at(-1).status, "success");
assert.strictEqual(state.tasks.at(-1).remoteVersion, "3");
assert.ok(state.pendingSupport.some((entry) => entry.id === remote.task.id));

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
