"use strict";

const assert = require("assert");

const values = new Map();
global.location = { search: "?offline=1" };
global.localStorage = {
  getItem: (key) => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
  key: (index) => [...values.keys()][index] || null,
  get length() { return values.size; },
};
global.fetch = async () => ({
  ok: true,
  json: async () => ({
    entries: [{
      id: "dongzhou_stage_001",
      index: 1,
      stageId: "01",
      name: "Chapter One",
      summary: "An archived account of the first court crisis.",
      content: "A deliberately long source body that must not enter localStorage.",
      people: ["Du Bo", "Zuo Ru"],
      keywords: ["court crisis"],
      sources: [{ work: "Dongzhou Chronicle", tier: "primary", scope: "first crisis", url: "https://example.test/source" }],
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
  assert.deepStrictEqual(codex.results[0].people, ["Du Bo", "Zuo Ru"]);
  assert.ok(values.has("dongzhou-knowledge-codex-v1"));
  console.log(JSON.stringify({ result: "PASS", entries: codex.results.length, compact: true }));
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
