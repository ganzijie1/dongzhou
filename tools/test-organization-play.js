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
state = play.updateBackend(state, { orgFlow: true, aiNpc: false, knowledge: true });
assert.strictEqual(state.backend.mode, "connected");

console.log(JSON.stringify({ result: "PASS", tasks: state.tasks.length, members: state.members.length, knowledge: state.knowledge.length }));
