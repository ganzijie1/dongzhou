"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const runtime = require(path.resolve(__dirname, "..", "web-game", "map-elites.js"));

const archive = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "web-game", "scenario", "map-elites-chuisha.archive.json"), "utf8"));
assert.strictEqual(archive.entries.length, 25, "5x5 archive must be complete");
for (const entry of archive.entries) {
  const validation = runtime.validate(entry);
  assert.strictEqual(validation.valid, true, `archive cell ${entry.cell} must pass hard validation`);
  assert.strictEqual(validation.routeCount, entry.routeCount);
}
for (const difficulty of ["easy", "medium", "hard"]) {
  for (const seed of [1, 17, 77123, 20261103]) {
    const first = runtime.selectElite(archive, difficulty, seed);
    const second = runtime.selectElite(archive, difficulty, seed);
    assert.deepStrictEqual(first, second, "same seed must select the same elite");
    assert.strictEqual(first.meta.validation.valid, true);
  }
}
console.log(JSON.stringify({ result: "PASS", archiveCells: archive.entries.length, hardValid: archive.entries.length }, null, 2));
