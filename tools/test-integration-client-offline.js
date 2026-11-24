"use strict";

const assert = require("assert");

const values = new Map();
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
global.fetch = async (url) => ({
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

  console.log(JSON.stringify({ result: "PASS", entries: codex.results.length, compact: true, localQuiz: true }));
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
