"use strict";

const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const overrides = JSON.parse(fs.readFileSync(path.join(ROOT, "game", "sce", "dongzhou", "story-overrides.json"), "utf8"));
const campaign = JSON.parse(fs.readFileSync(path.join(ROOT, "web-game", "scenario", "campaign.json"), "utf8"));
const stages = new Map(campaign.stages.map((stage) => [stage.id, stage]));
const expected = ["01", "02", "03", "03b", "04", "04a", "05", "06", "07", "07b", "08", "08a"];
const eventIds = new Set();
let runtimeEvents = 0;

assert.equal(overrides.schemaVersion, 1);
assert.deepEqual(Object.keys(overrides.stages), expected);
assert.ok(overrides.method.research.length >= 2);

for (const id of expected) {
  const override = overrides.stages[id];
  const stage = stages.get(id);
  assert.ok(stage, `Missing exported stage ${id}`);
  assert.deepEqual(stage.story.source_basis, override.source_basis, `${id} source metadata was not exported`);
  assert.ok(override.source_basis.length >= 2, `${id} needs historical and literary source boundaries`);
  assert.ok(override.source_basis.every((source) => /^https:\/\//.test(source.url)), `${id} has an invalid source URL`);

  const heroIds = new Set((stage.smoke?.generatedUnits || []).map((unit) => unit.hero));
  for (const event of override.events || []) {
    runtimeEvents++;
    assert.equal(event.runtime, true, `${id}/${event.id} is not a runtime event`);
    assert.ok(event.id && !eventIds.has(event.id), `Duplicate story event ${event.id}`);
    eventIds.add(event.id);
    assert.ok(event.speaker && event.text, `${id}/${event.id} has empty dialogue`);
    assert.ok(event.text.length <= 110, `${id}/${event.id} exceeds one dialogue panel`);
    if (["unit_defeated", "unit_hp_below"].includes(event.trigger)) {
      assert.ok(heroIds.has(event.unit), `${id}/${event.id} references undeployed unit ${event.unit}`);
    }
  }
}

assert.equal(runtimeEvents, 21);
assert.equal(stages.get("02").story.intro.length, 26);
assert.ok(stages.get("02").story.intro.filter((entry) => entry.speaker !== "旁白").length >= 18);
assert.ok(!stages.get("04").story.victory.some((entry) => entry.text.includes("自刎")));
assert.ok(stages.get("04").story.victory.some((entry) => entry.text.includes("《左传》只记")));

console.log(JSON.stringify({
  result: "PASS",
  enrichedStages: expected.length,
  runtimeEvents,
  chapter2Lines: stages.get("02").story.intro.length,
  sourceRecords: expected.reduce((count, id) => count + overrides.stages[id].source_basis.length, 0)
}, null, 2));
