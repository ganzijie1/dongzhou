"use strict";

const fs = require("fs");
const path = require("path");
const runtime = require(path.resolve(__dirname, "..", "web-game", "pcgrl.js"));
const template = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "web-game", "scenario", "pcgrl-masui.json"), "utf8"));

const fixturePath = process.argv[2];
if (!fixturePath) throw new Error("usage: node tools/evaluate-pcgrl-pipeline.js <policy-fixtures.json>");
const fixtures = JSON.parse(fs.readFileSync(path.resolve(fixturePath), "utf8"));
let passed = 0;
let fallbacks = 0;
let repairs = 0;
let wfcContradictions = 0;
const failures = [];

for (const fixture of fixtures) {
  const result = runtime.generate(fixture.tiles, template.stage.map.terrain, fixture.difficulty, fixture.seed);
  if (result.meta.validation?.valid) passed++;
  else failures.push({ difficulty: fixture.difficulty, seed: fixture.seed, meta: result.meta });
  if (result.meta.fallback) fallbacks++;
  repairs += Number(result.meta.repairs || 0);
  wfcContradictions += Number(result.meta.wfc?.contradictions || 0);
}

const summary = {
  samples: fixtures.length,
  hard_validation_pass_rate: fixtures.length ? passed / fixtures.length : 0,
  fallback_rate: fixtures.length ? fallbacks / fixtures.length : 0,
  mean_repairs: fixtures.length ? repairs / fixtures.length : 0,
  wfc_contradictions: wfcContradictions,
  failures: failures.length,
  result: fixtures.length > 0 && passed === fixtures.length ? "PASS" : "FAIL"
};
console.log(JSON.stringify(summary, null, 2));
if (summary.result !== "PASS") process.exitCode = 1;
