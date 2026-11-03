"use strict";

const assert = require("node:assert/strict");
const systems = require("../web-game/game-systems.js");

const stages = Array.from({ length: 12 }, (_, index) => ({ id: `stage-${index + 1}`, index: index + 1 }));
const migrated = systems.normalizeProfile({ completed: ["stage-1", "stage-2", "stage-3", "stage-4", "stage-5", "stage-6"] }, stages);
assert.equal(migrated.schemaVersion, 7);
assert.equal(migrated.armyRank, 3);
assert.equal(systems.isStageUnlocked(stages[6], migrated, stages), true);
assert.equal(systems.isStageUnlocked(stages[7], migrated, stages), false);

let profile = systems.normalizeProfile({}, stages);
for (let index = 0; index < 6; index++) {
  profile = systems.completeBattle(profile, stages[index], {
    stages, won: true, turns: 8, turnLimit: 18, totalOwn: 4, ownLosses: 1, supplies: 1,
    difficulty: "medium", timestamp: index + 1, ownHeroes: ["DuBo1"]
  }).profile;
}
assert.equal(profile.armyRank, 3);
assert.equal(profile.armyXp, 0);
assert.equal(profile.battleHistory.length, 6);
assert.ok(profile.coins > 240);
assert.equal(profile.heroMastery.DuBo.level, 4);
assert.equal(profile.heroMastery.DuBo.xp, 300);
assert.equal(systems.heroLevelCap(profile.armyRank), 5);
assert.equal(systems.recommendedStageLevel(1), 1);
assert.equal(systems.recommendedStageLevel(7), 3);
assert.equal(systems.recommendedStageLevel(168), 58);
assert.equal(systems.recommendedStageLevel(169), 58);
assert.equal(systems.recommendedStageLevel(172), 60);
assert.equal(systems.armyRankForClears(169), 59);
assert.equal(systems.armyRankForClears(171), 60);
assert.equal(systems.armyRankForClears(172), 60);
assert.deepEqual(systems.unitGrowthBonuses(5), { power: 6, defense: 3.2 });
assert.equal(systems.difficultyPreset("easy").enemyLevelOffset, -2);
assert.equal(systems.difficultyPreset("hard").enemyLevelOffset, 2);
assert.equal(systems.effectiveTurnLimit(20, "easy"), 25);
assert.equal(systems.effectiveTurnLimit(20, "hard"), 20);
assert.equal(systems.effectiveTurnLimit(99, "easy"), 99);
assert.deepEqual(systems.unitDifficultyModifiers("own", "hard"), { hp: 1, power: 1, defense: 1 });
assert.deepEqual(systems.unitDifficultyModifiers("enemy", "hard"), { hp: 1.12, power: 1.12, defense: 1.08 });
assert.ok(systems.effectiveUnitLevel(1, "enemy", profile, 30, "easy")
  < systems.effectiveUnitLevel(1, "enemy", profile, 30, "medium"));
assert.ok(systems.effectiveUnitLevel(1, "enemy", profile, 30, "medium")
  < systems.effectiveUnitLevel(1, "enemy", profile, 30, "hard"));

for (let index = 0; index < 50; index++) {
  profile = systems.completeBattle(profile, stages[0], {
    stages, won: true, turns: 5, turnLimit: 18, totalOwn: 4, ownLosses: 0,
    difficulty: "medium", ownHeroes: ["DuBo1"]
  }).profile;
}
assert.equal(profile.heroMastery.DuBo.level, 5);
assert.equal(profile.heroMastery.DuBo.xp, 499);

const legacyMastery = systems.normalizeProfile({
  schemaVersion: 6, armyRank: 2, completed: stages.slice(0, 3).map((stage) => stage.id), heroMastery: { DuBo: { level: 4, xp: 0 } }
}, stages);
assert.deepEqual(legacyMastery.heroMastery.DuBo, { level: 4, xp: 300 });
assert.ok(systems.availableEquipment(profile).some((item) => item.id === "war_horse"));
const purchase = systems.buyEquipment(profile, "bronze_halberd");
assert.equal(purchase.ok, true);
assert.equal(purchase.profile.equipped.weapon, "bronze_halberd");
assert.equal(systems.equipmentBonuses(purchase.profile).power, 4);
const supply = systems.buySupply(purchase.profile, "medicine");
assert.equal(supply.ok, true);
assert.equal(supply.profile.inventory.medicine, purchase.profile.inventory.medicine + 1);
const replayResult = systems.completeBattle(supply.profile, { id: "pcgrl", index: 0, isProcedural: true }, {
  stages, won: false, difficulty: "medium", turns: 20, turnLimit: 20, totalOwn: 4,
  storySkipped: true, durationMs: 12000, eventCounts: { move: 2 }, replay: { events: [{ type: "move" }] }
});
assert.equal(replayResult.profile.replays.length, 1);
assert.equal(replayResult.record.story_skipped, true);
assert.equal(replayResult.profile.replays[0].schema_version, systems.REPLAY_SCHEMA);

const normalized = systems.normalizeProfile({ settings: { battleDifficulty: "nightmare" } }, stages);
assert.equal(normalized.settings.battleDifficulty, "medium");
assert.equal(normalized.settings.mapDetail, "balanced");
assert.equal(normalized.settings.voiceEnabled, true);
assert.equal(normalized.settings.voiceVolume, 0.85);
assert.equal(systems.normalizeProfile({ settings: { voiceEnabled: false, voiceVolume: 2 } }, stages).settings.voiceEnabled, false);
assert.equal(systems.normalizeProfile({ settings: { voiceVolume: 2 } }, stages).settings.voiceVolume, 1);
assert.equal(systems.normalizeProfile({ settings: { mapDetail: "calm" } }, stages).settings.mapDetail, "calm");
assert.equal(systems.normalizeProfile({ settings: { mapDetail: "invalid" } }, stages).settings.mapDetail, "balanced");
assert.equal(systems.mapDetailProfile("balanced", true).scale, 0.58);
assert.equal(systems.mapDetailProfile("original", true).scale, 1);
assert.equal(systems.isStructuralTerrain("W"), true);
assert.equal(systems.isStructuralTerrain("G"), true);
assert.equal(systems.isStructuralTerrain("f"), false);
assert.equal(systems.isStructuralTerrain("i"), false);
assert.equal(systems.preservesMapDetail("W"), true);
assert.equal(systems.preservesMapDetail("r"), false);
assert.equal(systems.isBarrierTerrain("r"), true);
assert.equal(systems.isBarrierTerrain("~"), true);
const privateProfile = systems.normalizeProfile({ settings: { telemetryEnabled: false }, difficultyBandit: { enabled: false } }, stages);
assert.equal(systems.normalizeProfile({ settings: { telemetryEnabled: false } }, stages).difficultyBandit.enabled, false);
const privateResult = systems.completeBattle(privateProfile, { id: "pcgrl", index: 0, isProcedural: true }, {
  stages, won: true, difficulty: "hard", turns: 4, turnLimit: 20, totalOwn: 4
});
assert.equal(privateResult.profile.battleHistory.length, 0);
assert.equal(privateResult.profile.difficultyBandit.arms.hard.count, 0);

const exploit = systems.selectDifficulty(profile, "auto", 0.5);
assert.ok(systems.DIFFICULTIES.includes(exploit.difficulty));
assert.ok(exploit.behaviorProbability > 0 && exploit.behaviorProbability <= 1);
assert.equal(systems.selectDifficulty(profile, "hard", 0).behaviorProbability, 1);

const calibrationHistory = [];
for (let index = 0; index < 20; index++) {
  calibrationHistory.push({ difficulty: "easy", won: index < 18, turns: 10, turn_limit: 20 });
  calibrationHistory.push({ difficulty: "medium", won: index < 12, turns: 12, turn_limit: 20 });
  calibrationHistory.push({ difficulty: "hard", won: index < 8, turns: 15, turn_limit: 20 });
}
const calibration = systems.difficultyCalibration({ battleHistory: calibrationHistory });
assert.equal(calibration.easy.status, "in-range");
assert.equal(calibration.medium.status, "in-range");
assert.equal(calibration.hard.status, "in-range");
assert.equal(calibration.medium.winRate, 0.6);
assert.ok(calibration.medium.ci95[0] < calibration.medium.winRate && calibration.medium.ci95[1] > calibration.medium.winRate);

for (const classId of Object.keys(systems.SKILLS)) {
  const actor = { id: `${classId}-1`, classId, team: "own", x: 1, y: 1, hp: 80, maxHp: 100, mp: 30, level: 5, power: 40, defense: 20, effects: [] };
  const skill = systems.skillForUnit(actor);
  const target = skill.target === "enemy"
    ? { id: "enemy", team: "enemy", x: 2, y: 1, hp: 100, maxHp: 100, defense: 15, effects: [] }
    : skill.target === "self" ? actor
      : { id: "ally", team: "own", x: 2, y: 1, hp: 50, maxHp: 100, defense: 15, effects: [] };
  assert.equal(systems.skillTargetValid(actor, target, skill), true, `${classId} target contract`);
  const result = systems.applySkill(actor, target, skill);
  assert.equal(result.ok, true, `${classId} skill application`);
  assert.equal(actor.mp, 30 - skill.cost);
}

const story = systems.normalizeStoryEntries([
  { speaker: "原著", text: "第一句用于说明战役发生之前的历史背景和人物关系，并且应该保持完整。第二句继续交代双方兵力、行军路线以及将领决策，用于验证长文本能够稳定切分。" },
  { speaker: "原著", text: "第一句用于说明战役发生之前的历史背景和人物关系，并且应该保持完整。第二句继续交代双方兵力、行军路线以及将领决策，用于验证长文本能够稳定切分。" },
  { speaker: "", text: "旁白内容。" }
], 20);
assert.ok(story.length >= 3);
assert.equal(story[0].speaker, "史官");
assert.equal(story.at(-1).speaker, "旁白");
assert.equal(new Set(story.map((entry) => `${entry.speaker}:${entry.text}`)).size, story.length);

const voiceManifest = systems.normalizeVoiceManifest({ entries: [
  { id: "line-1", speaker: "杜伯", text: "白矢在此！", file: "audio/dialogue/line-1.ogg", duration: 1.5, voice: "Dylan", sha256: "a".repeat(64) },
  { id: "unsafe", speaker: "旁白", text: "越界", file: "../private.ogg" }
] });
assert.equal(voiceManifest.entries.length, 1);
assert.equal(voiceManifest.lookup.size, 1);
assert.equal(voiceManifest.entries[0].sha256, "a".repeat(64));
assert.equal(systems.resolveStoryVoice(voiceManifest, "杜伯", "白矢在此！").id, "line-1");
assert.equal(systems.resolveStoryVoice(voiceManifest, "周宣王", "白矢在此！"), null);

const storyEventContext = {
  turn: 3,
  claimedSites: ["west_gate"],
  units: [
    { heroId: "HeroA", team: "own", hp: 30, maxHp: 100 },
    { heroId: "EnemyA", team: "enemy", hp: 0, maxHp: 100 },
    { heroId: "EnemyB", team: "enemy", hp: 40, maxHp: 100 }
  ]
};
assert.equal(systems.storyEventMatches({ runtime: true, trigger: "turn", turn: 2 }, storyEventContext), true);
assert.equal(systems.storyEventMatches({ runtime: true, trigger: "unit_defeated", unit: "EnemyA" }, storyEventContext), true);
assert.equal(systems.storyEventMatches({ runtime: true, trigger: "unit_hp_below", unit: "HeroA", hp_percent: 0.5 }, storyEventContext), true);
assert.equal(systems.storyEventMatches({ runtime: true, trigger: "enemy_remaining", count: 1 }, storyEventContext), true);
assert.equal(systems.storyEventMatches({ runtime: true, trigger: "site_claimed", site: "west_gate" }, storyEventContext), true);
assert.equal(systems.storyEventMatches({ runtime: false, trigger: "turn", turn: 1 }, storyEventContext), false);

console.log(JSON.stringify({
  result: "PASS",
  profileVersion: systems.PROFILE_VERSION,
  mapDetailModes: systems.MAP_DETAIL_MODES.length,
  equipment: Object.keys(systems.EQUIPMENT).length,
  skills: Object.keys(systems.SKILLS).length,
  history: profile.battleHistory.length,
  storyEntries: story.length
}, null, 2));
