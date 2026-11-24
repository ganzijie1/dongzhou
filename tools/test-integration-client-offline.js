"use strict";

const assert = require("assert");

const values = new Map();
const fetchedUrls = [];
const serviceSources = {
  schemaVersion: 1,
  services: {
    knowledge: { sourceBranch: "main", sourceRevision: "45afa2ffe77faea0622e8d3ed3f2b69c0cab9c56", integrationRevision: "5fd67de575113b3f1238149d971106c97eed5c9a" },
    aiNpc: { sourceBranch: "develop", sourceRevision: "82b7a7e02bccceb283563cee9929e29610d6ebf5", integrationRevision: "f2235369e1da5e1e64aa2969ce29bef553f03ee3" },
    orgFlow: { sourceBranch: "develop", sourceRevision: "8b1049e965719d31c51772dde799737e9b92e918", integrationRevision: "fbfc803b264c2c1e1dffe80c8da1bb5caa676cc3" },
    nexusKernel: { sourceBranch: "develop", sourceRevision: "190abb1fa889e40aa08dbc6efaaba6fe4940ca6d", integrationRevision: "4f1915b45eadf8608308f7131173d1d60f6c5270" },
  },
};
global.location = { search: "?offline=1" };
global.localStorage = {
  getItem: (key) => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
  key: (index) => [...values.keys()][index] || null,
  get length() { return values.size; },
};
global.fetch = async (url) => {
  fetchedUrls.push(String(url));
  return ({
  ok: true,
  json: async () => String(url).endsWith("service-sources.json") ? serviceSources : ({
    entries: [{
      id: "dongzhou_stage_001",
      index: 1,
      stageId: "01",
      name: "Chapter One",
      summary: "An archived account of the first court crisis.",
      content: "A deliberately long source body that must not enter localStorage.",
      people: ["Du Bo"],
      keywords: ["court crisis"],
      sources: [{ work: "Dongzhou Chronicle", tier: "primary", scope: "first crisis", url: "https://example.test/source" }],
      sourceDetails: [{ work: "Dongzhou Chronicle", tier: "primary", scope: "first crisis" }],
    }, {
      id: "dongzhou_stage_002", index: 2, stageId: "02", name: "Chapter Two", people: ["King You"]
    }, {
      id: "dongzhou_stage_003", index: 3, stageId: "03", name: "Chapter Three", people: ["Marquis Shen"]
    }, {
      id: "dongzhou_stage_004", index: 4, stageId: "04", name: "Chapter Four", people: ["Duke Zheng"]
    }],
  }),
  });
};

const client = require("../web-game/integration-client.js");

(async () => {
  const search = await client.searchKnowledge("court", 6, "01");
  assert.strictEqual(search.results.length, 1);
  const codex = await client.knowledgeCodex();
  assert.strictEqual(codex.mode, "offline");
  assert.strictEqual(codex.results[0].name, "Chapter One");
  assert.strictEqual(codex.results[0].content, undefined);
  assert.deepStrictEqual(codex.results[0].people, ["Du Bo"]);
  assert.ok(values.has("dongzhou-knowledge-codex-v1"));

  const questionId = "00000000-0000-4000-8000-000000000501";
  const started = await client.startKnowledgeQuiz("01", questionId);
  assert.strictEqual(started.mode, "offline");
  assert.strictEqual(started.question.options.length, 4);
  assert.ok(!JSON.stringify(started).includes("correctIndex"));
  const quizKey = [...values.keys()].find((key) => key.endsWith(questionId));
  assert.ok(quizKey);
  assert.ok(!values.get(quizKey).includes("correctIndex"));
  assert.strictEqual((await client.startKnowledgeQuiz("01", questionId)).replayed, true);
  const pendingRecord = values.get(quizKey);
  const tamperedQuestion = JSON.parse(pendingRecord);
  tamperedQuestion.ready.question.prompt = "forged prompt";
  values.set(quizKey, JSON.stringify(tamperedQuestion));
  await assert.rejects(client.startKnowledgeQuiz("01", questionId), /knowledge_quiz_source_invalid/);
  values.set(quizKey, pendingRecord);
  const correctIndex = started.question.options.indexOf("Du Bo");
  assert.ok(correctIndex >= 0);
  const answered = await client.answerKnowledgeQuiz(questionId, started.action.actionId, correctIndex);
  assert.strictEqual(answered.correct, true);
  assert.strictEqual(answered.score, 10);
  assert.strictEqual(answered.receipt.kernel.module, "dongzhou_knowledge_tournament");
  assert.strictEqual(answered.receipt.kernel.state, "SEALED");
  const verified = await client.verifyKnowledgeQuizSeal(questionId);
  assert.strictEqual(verified.verified, true);
  assert.strictEqual(verified.digest, answered.receipt.digest);
  assert.strictEqual((await client.answerKnowledgeQuiz(questionId, started.action.actionId, correctIndex)).replayed, true);
  await assert.rejects(
    client.answerKnowledgeQuiz(questionId, started.action.actionId, (correctIndex + 1) % 4),
    /knowledge_quiz_already_answered/
  );
  const completedRecord = values.get(quizKey);
  const tampered = JSON.parse(completedRecord);
  tampered.result.receipt.digest = "0".repeat(64);
  values.set(quizKey, JSON.stringify(tampered));
  await assert.rejects(client.verifyKnowledgeQuizSeal(questionId), /knowledge_quiz_seal_invalid/);
  const tamperedKernel = JSON.parse(completedRecord);
  tamperedKernel.result.receipt.kernel.state = "READY";
  values.set(quizKey, JSON.stringify(tamperedKernel));
  await assert.rejects(client.verifyKnowledgeQuizSeal(questionId), /knowledge_quiz_seal_invalid/);

  const adviser = await client.askAdviser({
    question: "Where is Du Bo?",
    stage_id: "01",
    stage_title: "Chapter One",
    stage_index: 1,
  });
  assert.strictEqual(adviser.mode, "offline");
  assert.strictEqual(adviser.state, "ANSWERED");
  assert.strictEqual(adviser.intentType, "location");
  assert.strictEqual(adviser.guide.available, true);
  assert.strictEqual(adviser.guide.target.name, "Du Bo");
  assert.strictEqual(adviser.adviser.heroId, "DuBo");
  assert.strictEqual(Object.keys(adviser.sourceProvenance.services).length, 4);
  assert.match(adviser.answerDigest, /^[0-9a-f]{64}$/);
  const adviserJournal = JSON.parse(values.get("dongzhou-adviser-question-v1"));
  const adviserId = adviserJournal.input.client_request_id;
  assert.strictEqual((await client.adviserQuestion(adviserId)).replayed, true);
  const cleanAdviserJournal = values.get("dongzhou-adviser-question-v1");
  adviserJournal.result.answer = "forged answer";
  values.set("dongzhou-adviser-question-v1", JSON.stringify(adviserJournal));
  await assert.rejects(client.adviserQuestion(adviserId), /adviser_answer_source_invalid/);
  values.set("dongzhou-adviser-question-v1", cleanAdviserJournal);

  const guide = await client.decideAdviserGuide(adviserId, "ACCEPT");
  assert.strictEqual(guide.state, "ACCEPTED");
  assert.strictEqual(guide.guide.kernel.module, "dongzhou_adviser_guide");
  assert.strictEqual(guide.guide.kernel.moduleVersion, "1.1.0");
  assert.strictEqual(guide.guide.sourceProvenance.digest, adviser.sourceProvenance.digest);
  assert.strictEqual((await client.decideAdviserGuide(adviserId, "ACCEPT")).replayed, true);
  await assert.rejects(client.decideAdviserGuide(adviserId, "REJECT"), /adviser_guide_already_decided/);
  const guideActionId = guide.guide.actionId;
  assert.strictEqual((await client.adviserGuide(guideActionId)).state, "RUNNING");
  assert.strictEqual((await client.adviserGuide(guideActionId)).state, "COMPLETED");
  const feedback = await client.feedbackAdviser(adviserId, "accurate");
  assert.strictEqual(feedback.state, "RECORDED");
  assert.strictEqual((await client.feedbackAdviser(adviserId, "accurate")).replayed, true);
  await assert.rejects(client.feedbackAdviser(adviserId, "inaccurate"), /adviser_feedback_already_recorded/);

  const cancellable = await client.askAdviser({
    question: "Where is Du Bo?",
    stage_id: "01",
    stage_title: "Chapter One",
    stage_index: 1,
  });
  const cancellableId = JSON.parse(values.get("dongzhou-adviser-question-v1")).input.client_request_id;
  const accepted = await client.decideAdviserGuide(cancellableId, "ACCEPT");
  const cancelled = await client.cancelAdviserGuide(accepted.guide.actionId, "player_changed_plan");
  assert.strictEqual(cancelled.state, "CANCELLED");
  assert.strictEqual(cancelled.guide.reason, "player_changed_plan");
  assert.strictEqual((await client.cancelAdviserGuide(accepted.guide.actionId, "player_changed_plan")).replayed, true);
  const sealedJournal = values.get("dongzhou-adviser-question-v1");
  const forgedGuide = JSON.parse(sealedJournal);
  forgedGuide.guideDecision.result.guide.digest = "0".repeat(64);
  values.set("dongzhou-adviser-question-v1", JSON.stringify(forgedGuide));
  await assert.rejects(client.adviserGuide(accepted.guide.actionId), /adviser_guide_seal_invalid/);
  values.set("dongzhou-adviser-question-v1", sealedJournal);
  await assert.rejects(client.cancelAdviserGuide(accepted.guide.actionId, "x".repeat(501)), /adviser_guide_cancel_invalid/);

  await client.askAdviser({ question: "Where is Du Bo?", stage_id: "01", stage_title: "Chapter One", stage_index: 1 });
  const rejectedId = JSON.parse(values.get("dongzhou-adviser-question-v1")).input.client_request_id;
  const rejected = await client.decideAdviserGuide(rejectedId, "REJECT");
  assert.strictEqual(rejected.state, "REJECTED");
  assert.strictEqual(rejected.guide.decision, "REJECT");
  assert.strictEqual(rejected.guide.kernel.state, "SEALED");
  assert.strictEqual(fetchedUrls.some((url) => url.includes("/api/")), false);

  console.log(JSON.stringify({ result: "PASS", entries: codex.results.length, compact: true, localQuiz: true, localAdviser: true }));
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
