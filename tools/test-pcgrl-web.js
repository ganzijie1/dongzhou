"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const runtime = require(path.resolve(__dirname, "..", "web-game", "pcgrl.js"));
const fengari = require(path.resolve(__dirname, "..", "web-game", "vendor", "fengari-web.bundle.js"));
const template = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "web-game", "scenario", "pcgrl-masui.json"), "utf8"));

fengari.load("Enum={force={own='own',enemy='enemy',ally='ally'},status={victory='victory',defeat='defeat',undecided='undecided'}}", "test-enum")();
fengari.load(fs.readFileSync(path.resolve(__dirname, "..", "web-game", "scenario", "stage", "pcgrl_masui.lua"), "utf8"), "pcgrl-masui")();

const fallback = template.stage.map.terrain;
const raw = Array.from({ length: runtime.CELL_COUNT }, (_, index) => index % 5 === 0 ? 3 : index % 7 === 0 ? 2 : index % 2);
const first = runtime.generate(raw, fallback, "medium", 77123);
const second = runtime.generate(raw, fallback, "medium", 77123);
assert.deepStrictEqual(first.rows, second.rows, "same seed must reproduce the same map");
assert.strictEqual(first.meta.validation.valid, true, "generated or fallback map must pass hard validation");
assert.strictEqual(first.meta.validation.geometryOk, true, "generated map must pass discrete geometry validation");
assert.ok(first.meta.validation.geometry.transitionRatio <= runtime.GEOMETRY_LIMITS.transitionRatio);
assert.ok(first.meta.validation.geometry.patchDensity <= runtime.GEOMETRY_LIMITS.patchDensity);
assert.ok(first.meta.validation.geometry.articulationRatio <= runtime.GEOMETRY_LIMITS.articulationRatio);
assert.strictEqual(first.rows.length, 14);
assert.ok(first.rows.every((row) => [...row].length === 19));

const missing = runtime.generate(null, fallback, "medium", 9);
assert.strictEqual(missing.meta.fallback, true);
assert.strictEqual(missing.meta.validation.valid, true);
assert.strictEqual(missing.meta.validation.geometryOk, true);

const wfc = runtime.wfcRefine(raw, "hard", 123);
assert.strictEqual(wfc.ok, true);
assert.strictEqual(runtime.validate(runtime.repair(wfc.tiles, "hard", 123).tiles, "hard").valid, true);

console.log(JSON.stringify({ result: "PASS", source: first.meta.source, repairs: first.meta.repairs, fallback_valid: missing.meta.validation.valid }, null, 2));
