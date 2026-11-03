"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const STAGE_ROOT = path.join(ROOT, "game", "sce", "dongzhou", "stage");
const CONFIG_FILE = path.join(ROOT, "game", "sce", "dongzhou", "config.lua");
const STORY_OVERRIDES_FILE = path.join(ROOT, "game", "sce", "dongzhou", "story-overrides.json");
const MAP_ROOT = path.join(ROOT, "assets", "lzc", "map");
const OUTPUT_ROOT = path.join(ROOT, "web-game", "scenario");
const OUTPUT_STAGE_ROOT = path.join(OUTPUT_ROOT, "stage");
const fengari = require(path.join(ROOT, "web-game", "vendor", "fengari-web.bundle.js"));

const collator = new Intl.Collator("en", { numeric: true, sensitivity: "base" });
const storyOverridesDocument = fs.existsSync(STORY_OVERRIDES_FILE)
  ? JSON.parse(fs.readFileSync(STORY_OVERRIDES_FILE, "utf8"))
  : { stages: {} };
const storyOverrides = storyOverridesDocument.stages || {};
const stageFiles = fs.readdirSync(STAGE_ROOT)
  .filter((name) => name.endsWith(".lua"))
  .sort((a, b) => collator.compare(a, b));

function lua(source, chunkName) {
  return fengari.load(source, chunkName)();
}

function getGlobal(name) {
  return fengari.load(`return ${name}`, `read:${name}`)();
}

function isLuaProxy(value) {
  return typeof value === "function" && value[Symbol.toStringTag] === "Fengari object";
}

function toPlain(value) {
  if (!isLuaProxy(value)) return value;
  const entries = [...value].map(([key, child]) => [key, toPlain(child)]);
  if (!entries.length) return {};
  const numeric = entries
    .map(([key, child]) => [Number(key), child])
    .sort((a, b) => a[0] - b[0]);
  const isArray = numeric.every(([key], index) => Number.isInteger(key) && key === index + 1);
  if (isArray) return numeric.map(([, child]) => child);
  return Object.fromEntries(entries.map(([key, child]) => [String(key), child]));
}

function tablePoint(value) {
  if (!isLuaProxy(value)) return value;
  return [Number(value.get(1)), Number(value.get(2))];
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== "object") return [];
  return Object.entries(value)
    .filter(([key]) => /^\d+$/.test(key))
    .sort((a, b) => Number(a[0]) - Number(b[0]))
    .map(([, child]) => child);
}

function discoverStageGlobals() {
  const globals = new Set([
    "gitems", "gcommanders", "gduel_enabled", "gduels", "gevents_enabled",
    "gsites", "gstage", "gstory", "gsupply_enabled", "on_deploy", "on_begin",
    "on_update", "end_condition"
  ]);
  for (const file of stageFiles) {
    const source = fs.readFileSync(path.join(STAGE_ROOT, file), "utf8");
    for (const match of source.matchAll(/^([A-Za-z_][A-Za-z0-9_]*)\s*=/gm)) globals.add(match[1]);
    for (const match of source.matchAll(/^function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/gm)) globals.add(match[1]);
  }
  return [...globals].sort();
}

const stageGlobals = discoverStageGlobals();

function resetStageGlobals() {
  lua(stageGlobals.map((name) => `${name}=nil`).join(";"), "reset-stage-globals");
}

function createSmokeGame(stage) {
  let nextId = 1;
  const units = new Map();
  const appointed = [];
  const commands = [];

  const addUnit = (hero, level, force, position) => {
    const id = `${hero}#${nextId++}`;
    units.set(id, { id, hero, level, force, position: tablePoint(position), alive: true, invulnerable: false });
    return id;
  };

  const game = {
    appoint_hero(hero, level) {
      appointed.push({ hero, level });
      return hero;
    },
    generate_unit(hero, level, force, position) {
      return addUnit(hero, level, force, position);
    },
    has_unit(ref) {
      return [...units.values()].some((unit) => unit.alive && (unit.id === ref || unit.hero === ref)) || appointed.some((unit) => unit.hero === ref);
    },
    set_unit_invulnerable(ref, value) {
      for (const unit of units.values()) if (unit.id === ref || unit.hero === ref) unit.invulnerable = Boolean(value);
    },
    push_cmd_speak(ref, text) { commands.push({ type: "speak", ref, text }); },
    push_cmd_move(ref, position) { commands.push({ type: "move", ref, position: tablePoint(position) }); },
    is_unit_within(ref, position, radius) {
      const target = tablePoint(position);
      return [...units.values()].some((unit) => unit.alive && (unit.id === ref || unit.hero === ref) && Math.abs(unit.position[0] - target[0]) + Math.abs(unit.position[1] - target[1]) <= radius);
    },
    are_units_within(left, right, radius) {
      const a = [...units.values()].find((unit) => unit.alive && (unit.id === left || unit.hero === left));
      const b = [...units.values()].find((unit) => unit.alive && (unit.id === right || unit.hero === right));
      return Boolean(a && b && Math.abs(a.position[0] - b.position[0]) + Math.abs(a.position[1] - b.position[1]) <= radius);
    },
    is_force_within(force, position, radius) {
      const target = tablePoint(position);
      return [...units.values()].some((unit) => unit.alive && unit.force === force && Math.abs(unit.position[0] - target[0]) + Math.abs(unit.position[1] - target[1]) <= radius);
    },
    get_num_commanders_alive(force) { return [...units.values()].filter((unit) => unit.alive && unit.force === force).length; },
    get_num_enemies_alive() { return [...units.values()].filter((unit) => unit.alive && unit.force === "enemy").length; },
    get_num_units_alive(ref) { return [...units.values()].filter((unit) => unit.alive && (ref == null || unit.id === ref || unit.hero === ref)).length; },
    get_turn_current() { return 1; },
    set_unit_direction() {},
    set_force_direction() {},
    is_cell_vacant(position) {
      const target = tablePoint(position);
      return ![...units.values()].some((unit) => unit.alive && unit.position[0] === target[0] && unit.position[1] === target[1]);
    }
  };

  const invoke = (name) => {
    const fn = getGlobal(name);
    if (isLuaProxy(fn)) return fn.apply(game, []);
    return undefined;
  };

  invoke("on_deploy");
  const deployed = [
    ...asArray(stage.deploy?.unselectables),
    ...asArray(stage.deploy?.selectables)
  ];
  for (const entry of deployed) {
    if (!entry?.hero || !entry?.position) continue;
    if (![...units.values()].some((unit) => unit.hero === entry.hero)) addUnit(entry.hero, 1, "own", entry.position);
  }
  invoke("on_begin");
  const updateResult = invoke("on_update");
  const endResult = invoke("end_condition");

  return {
    appointed,
    generatedUnits: [...units.values()],
    queuedCommands: commands,
    initialUpdate: updateResult ?? null,
    initialEndCondition: endResult ?? null
  };
}

fs.mkdirSync(OUTPUT_STAGE_ROOT, { recursive: true });
fs.copyFileSync(CONFIG_FILE, path.join(OUTPUT_ROOT, "config.lua"));

lua(fs.readFileSync(CONFIG_FILE, "utf8"), "dongzhou/config.lua");
lua('Enum={force={own="own",enemy="enemy",ally="ally"},status={victory="victory",defeat="defeat",undecided="undecided"}}', "web-enum");
const config = toPlain(getGlobal("gconfig"));
fs.writeFileSync(path.join(OUTPUT_ROOT, "config.json"), JSON.stringify(config), "utf8");

const stages = [];
const failures = [];
const missingMaps = [];

for (let index = 0; index < stageFiles.length; index++) {
  const file = stageFiles[index];
  const id = path.basename(file, ".lua");
  const source = fs.readFileSync(path.join(STAGE_ROOT, file), "utf8");
  try {
    resetStageGlobals();
    lua(source, `dongzhou/stage/${file}`);
    const stage = toPlain(getGlobal("gstage"));
    const baseStory = toPlain(getGlobal("gstory"));
    const story = { ...baseStory, ...(storyOverrides[id] || {}) };
    const mapAsset = story?.map_asset || null;
    if (!mapAsset || !fs.existsSync(path.join(MAP_ROOT, mapAsset))) missingMaps.push({ id, mapAsset });
    const record = {
      index: index + 1,
      id,
      file,
      chapter: story?.chapter || `第${index + 1}关`,
      title: story?.title || stage?.title_id || id,
      battleTitle: story?.battle_title || story?.title || id,
      objective: story?.objective || "完成本关历史目标",
      mapAsset,
      turnLimit: Number(stage?.turn_limit || 30),
      commanders: toPlain(getGlobal("gcommanders")) || [],
      items: toPlain(getGlobal("gitems")) || [],
      sites: toPlain(getGlobal("gsites")) || [],
      duels: toPlain(getGlobal("gduels")) || [],
      flags: {
        supply: Boolean(getGlobal("gsupply_enabled")),
        duel: Boolean(getGlobal("gduel_enabled")),
        events: Boolean(getGlobal("gevents_enabled"))
      },
      story,
      stage
    };
    record.smoke = createSmokeGame(stage);
    stages.push(record);
    fs.copyFileSync(path.join(STAGE_ROOT, file), path.join(OUTPUT_STAGE_ROOT, file));
  } catch (error) {
    failures.push({ id, file, error: String(error?.stack || error) });
  }
}

const manifest = {
  schemaVersion: 1,
  campaign: "东周列国志",
  stageCount: stages.length,
  sourceStageCount: stageFiles.length,
  stageGlobals,
  missingMaps,
  failures,
  stages
};

fs.writeFileSync(path.join(OUTPUT_ROOT, "campaign.json"), JSON.stringify(manifest), "utf8");
console.log(JSON.stringify({
  sourceStages: stageFiles.length,
  exportedStages: stages.length,
  failures: failures.length,
  missingMaps: missingMaps.length,
  heroes: Array.isArray(config.heroes) ? config.heroes.length : 0
}, null, 2));

if (failures.length || missingMaps.length || stages.length !== stageFiles.length) process.exitCode = 1;
