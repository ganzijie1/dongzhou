"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CAMPAIGN_PATH = path.join(ROOT, "web-game", "scenario", "campaign.json");
const WEB_OUTPUT = path.join(ROOT, "web-game", "scenario", "dongzhou-knowledge.json");
const KNOWLEDGE_ROOT = process.env.DONGZHOU_KNOWLEDGE_REPO || path.resolve(ROOT, "..", "knowledge-jizhan");
const AKU_OUTPUT = path.join(KNOWLEDGE_ROOT, "AI使用的知识库", "V3", "dongzhou");
const campaign = JSON.parse(fs.readFileSync(CAMPAIGN_PATH, "utf8"));

function list(value) {
  return Array.isArray(value) ? value : Object.values(value || {});
}

function compactText(value, max = 180) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function stagePeople(stage) {
  const speakers = list(stage.story?.intro).map((entry) => entry.speaker).filter((name) => name && !["旁白", "军令"].includes(name));
  return [...new Set(speakers)].slice(0, 12);
}

function entryFor(stage) {
  const basis = list(stage.story?.source_basis);
  const people = stagePeople(stage);
  const intro = list(stage.story?.intro).filter((entry) => entry.speaker === "旁白").slice(0, 3).map((entry) => compactText(entry.text, 100));
  const sourceNote = basis.map((item) => `${item.work || "来源"}：${item.scope || ""}`).join("；");
  return {
    id: `dongzhou_stage_${String(stage.index).padStart(3, "0")}`,
    index: stage.index,
    stageId: stage.id,
    name: `${stage.chapter}·${stage.battleTitle}`,
    summary: compactText(`${stage.title}。军令：${stage.objective}`, 160),
    content: compactText(`${intro.join(" ")} ${sourceNote ? `依据：${sourceNote}` : ""}`, 420),
    objective: stage.objective,
    people,
    keywords: [...new Set([stage.chapter, stage.title, stage.battleTitle, stage.objective, ...people])].filter(Boolean),
    sources: basis.map((item) => ({ work: item.work || "", tier: item.tier || "", scope: item.scope || "", url: item.url || "" }))
  };
}

const entries = campaign.stages.map(entryFor);
fs.writeFileSync(WEB_OUTPUT, `${JSON.stringify({ schemaVersion: 1, generatedFrom: "scenario/campaign.json", entries }, null, 2)}\n`, "utf8");
fs.mkdirSync(AKU_OUTPUT, { recursive: true });

for (const entry of entries) {
  const mapId = 900000 + entry.index;
  const npcs = entry.people.map((name, index) => ({ id: mapId * 100 + index + 1, name, profession: "剧情人物", description: `${entry.name}相关人物`, pos: { map_id: mapId, x: index + 1, y: 1 } }));
  const aku = {
    version: "dongzhou_2026_v1",
    id: entry.id,
    is_valid: true,
    type: "执行攻略",
    name: entry.name,
    summary: entry.summary,
    content: `# ${entry.name}\n\n## 剧情背景\n${entry.content || "本条目仅依据游戏现有关卡资料。"}\n\n## 本战军令\n${entry.objective}\n\n## 使用边界\n仅作为关卡决策与玩家问答依据；史实、文学演绎与游戏机制以关卡来源分层为准，不补写原资料没有的结论。`,
    preconditions: [],
    rewards: [],
    entities: { npcs, items: [], monsters: [], maps: [{ id: mapId, name: entry.name, description: `东周列国志第${entry.index}战地图` }] },
    category: ["东周列国志", entry.chapter || "列国战役", "关卡攻略", `第${entry.index}战`],
    schedule_tag: { type: "列国战役", limit: `解锁第${entry.index}战后可查` },
    sources: ["dongzhou/web-game/scenario/campaign.json", ...entry.sources.map((source) => source.url || source.work).filter(Boolean)],
    usage_constraints: ["AI决策使用", "玩家问题解答"],
    keywords: entry.keywords.slice(0, 30),
    intents: ["关卡背景查询", "战前军议", "人物关系查询"],
    dependence: entry.index > 1 ? [`dongzhou_stage_${String(entry.index - 1).padStart(3, "0")}`] : []
  };
  const file = path.join(AKU_OUTPUT, `${String(entry.index).padStart(3, "0")}-${entry.stageId}.json`);
  fs.writeFileSync(file, `${JSON.stringify(aku, null, 2)}\n`, "utf8");
}

console.log(JSON.stringify({ stages: entries.length, webOutput: WEB_OUTPUT, akuOutput: AKU_OUTPUT }, null, 2));
