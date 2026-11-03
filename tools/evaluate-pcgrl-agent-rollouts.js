"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const runtime = require(path.resolve(__dirname, "..", "web-game", "pcgrl.js"));
const template = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "web-game", "scenario", "pcgrl-masui.json"), "utf8"));

const fixturePath = process.argv[2];
const outputPath = process.argv[3];
if (!fixturePath) throw new Error("usage: node tools/evaluate-pcgrl-agent-rollouts.js <policy-fixtures.json> [output.json]");
const fixtures = JSON.parse(fs.readFileSync(path.resolve(fixturePath), "utf8"));

function neighbors(index, tiles) {
  const x = index % runtime.WIDTH; const y = Math.floor(index / runtime.WIDTH); const result = [];
  for (const [dx, dy] of [[1, 0], [0, 1], [-1, 0], [0, -1]]) {
    const nx = x + dx; const ny = y + dy;
    if (nx >= 0 && nx < runtime.WIDTH && ny >= 0 && ny < runtime.HEIGHT && tiles[ny * runtime.WIDTH + nx] < 2) result.push(ny * runtime.WIDTH + nx);
  }
  return result;
}

function nextStep(tiles, start, goals, occupied) {
  const queue = [start]; const previous = new Map([[start, -1]]); let reached = -1;
  while (queue.length) {
    const current = queue.shift();
    if (goals.has(current)) { reached = current; break; }
    for (const next of neighbors(current, tiles)) {
      if (previous.has(next) || (occupied.has(next) && !goals.has(next))) continue;
      previous.set(next, current); queue.push(next);
    }
  }
  if (reached < 0) return start;
  let cursor = reached;
  while (previous.get(cursor) !== start && previous.get(cursor) !== -1) cursor = previous.get(cursor);
  return cursor === reached && goals.has(start) ? start : cursor;
}

function simulate(tiles, swap) {
  const left = runtime.SPAWNS.slice(0, 6); const right = runtime.SPAWNS.slice(7, 13);
  const ownSpawns = swap ? right : left; const enemySpawns = swap ? left : right;
  const units = [
    ...ownSpawns.map(([x, y], id) => ({ id: `o${id}`, team: "own", index: y * runtime.WIDTH + x, hp: 100, damage: 24 })),
    ...enemySpawns.map(([x, y], id) => ({ id: `e${id}`, team: "enemy", index: y * runtime.WIDTH + x, hp: 100, damage: 24 }))
  ];
  for (let turn = 1; turn <= 60; turn++) {
    for (const team of ["own", "enemy"]) {
      for (const actor of units.filter((unit) => unit.team === team && unit.hp > 0)) {
        const opponents = units.filter((unit) => unit.team !== team && unit.hp > 0);
        if (!opponents.length) return { winner: team, turns: turn, timeout: false };
        const adjacent = opponents.filter((unit) => neighbors(actor.index, tiles).includes(unit.index)).sort((a, b) => a.hp - b.hp || a.id.localeCompare(b.id));
        if (adjacent.length) adjacent[0].hp -= actor.damage;
        else {
          const goals = new Set(opponents.flatMap((unit) => neighbors(unit.index, tiles)));
          const occupied = new Set(units.filter((unit) => unit.hp > 0 && unit.id !== actor.id).map((unit) => unit.index));
          const destination = nextStep(tiles, actor.index, goals, occupied);
          if (!occupied.has(destination)) actor.index = destination;
        }
      }
      const survivingTeams = new Set(units.filter((unit) => unit.hp > 0).map((unit) => unit.team));
      if (survivingTeams.size === 1) return { winner: [...survivingTeams][0], turns: turn, timeout: false };
    }
  }
  const hp = (team) => units.filter((unit) => unit.team === team && unit.hp > 0).reduce((sum, unit) => sum + unit.hp, 0);
  return { winner: hp("own") === hp("enemy") ? "draw" : hp("own") > hp("enemy") ? "own" : "enemy", turns: 60, timeout: true };
}

const rollouts = [];
const terrainHashes = new Set();
for (const fixture of fixtures) {
  const generated = runtime.generate(fixture.tiles, template.stage.map.terrain, fixture.difficulty, fixture.seed);
  const tiles = runtime.rowsToTiles(generated.rows);
  terrainHashes.add(crypto.createHash("sha1").update(Buffer.from(tiles)).digest("hex"));
  for (const swap of [false, true]) rollouts.push({ difficulty: fixture.difficulty, seed: fixture.seed, swap, ...simulate(tiles, swap) });
}

const byDifficulty = Object.fromEntries(["easy", "medium", "hard"].map((difficulty) => {
  const rows = rollouts.filter((entry) => entry.difficulty === difficulty);
  return [difficulty, {
    games: rows.length,
    timeout_rate: rows.filter((entry) => entry.timeout).length / Math.max(1, rows.length),
    own_win_rate: rows.filter((entry) => entry.winner === "own").length / Math.max(1, rows.length),
    mean_turns: rows.reduce((sum, entry) => sum + entry.turns, 0) / Math.max(1, rows.length)
  }];
}));
const paired = fixtures.map((fixture) => rollouts.filter((entry) => entry.seed === fixture.seed && entry.difficulty === fixture.difficulty));
const mirroredDisagreement = paired.filter((pair) => pair.length === 2 && pair[0].winner !== pair[1].winner).length / Math.max(1, paired.length);
const timeoutRate = rollouts.filter((entry) => entry.timeout).length / Math.max(1, rollouts.length);
const decisiveRate = rollouts.filter((entry) => !entry.timeout && entry.winner !== "draw").length / Math.max(1, rollouts.length);
const summary = {
  evaluator: "deterministic-rule-agent-v1",
  limitation: "Rule-agent annihilation proxy; not HAPPO and not human playtest evidence.",
  maps: fixtures.length,
  games: rollouts.length,
  timeout_rate: timeoutRate,
  decisive_rate: decisiveRate,
  unique_terrain_rate: terrainHashes.size / Math.max(1, fixtures.length),
  mirrored_outcome_disagreement_rate: mirroredDisagreement,
  by_difficulty: byDifficulty,
  gates: {
    timeout_at_most_5_percent: timeoutRate <= .05,
    decisive_at_least_95_percent: decisiveRate >= .95,
    unique_terrain_at_least_90_percent: terrainHashes.size / Math.max(1, fixtures.length) >= .9,
    no_rule_agent_side_collapse: Object.values(byDifficulty).every((entry) => entry.own_win_rate >= .35 && entry.own_win_rate <= .65),
    hard_maps_take_longer_than_easy: byDifficulty.hard.mean_turns >= byDifficulty.easy.mean_turns * 1.05
  }
};
summary.result = Object.values(summary.gates).every(Boolean) ? "PASS" : "FAIL";
if (outputPath) fs.writeFileSync(path.resolve(outputPath), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
if (summary.result !== "PASS") process.exitCode = 1;
