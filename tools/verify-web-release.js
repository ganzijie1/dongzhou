"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const WEB = path.join(ROOT, "web-game");
const campaign = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "campaign.json"), "utf8"));
const config = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "config.json"), "utf8"));
const mapIndex = JSON.parse(fs.readFileSync(path.join(WEB, "assets", "maps", "index.json"), "utf8"));
const pcgrlTemplate = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "pcgrl-masui.json"), "utf8"));
const mapElitesTemplate = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "map-elites-chuisha.json"), "utf8"));
const mapElitesArchive = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "map-elites-chuisha.archive.json"), "utf8"));
const difficultyProfiles = JSON.parse(fs.readFileSync(path.join(WEB, "scenario", "difficulty-profiles.json"), "utf8"));
const mapElitesRuntime = require(path.join(WEB, "map-elites.js"));
const densityReport = JSON.parse(fs.readFileSync(path.join(ROOT, "docs", "map-visual-density-report.json"), "utf8"));
const gameSystems = require(path.join(WEB, "game-systems.js"));
const voiceManifest = JSON.parse(fs.readFileSync(path.join(WEB, "audio", "dialogue-manifest.json"), "utf8"));
const errors = [];
const warnings = [];

const asArray = (value) => Array.isArray(value) ? value : Object.values(value || {});
const fail = (message) => errors.push(message);

function folderFiles(folder) {
  const files = [];
  for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
    const file = path.join(folder, entry.name);
    if (entry.isDirectory()) files.push(...folderFiles(file));
    else files.push(file);
  }
  return files;
}

if (campaign.sourceStageCount !== 172 || campaign.stageCount !== 172 || campaign.stages.length !== 172) {
  fail(`关卡数量不符：${campaign.stageCount}/${campaign.sourceStageCount}/${campaign.stages.length}`);
}
if (campaign.failures.length) fail(`导出失败 ${campaign.failures.length} 关`);
if (campaign.missingMaps.length) fail(`缺失地图 ${campaign.missingMaps.length} 张`);
if (mapIndex.sourceCount !== 169) fail(`地图数量不符：${mapIndex.sourceCount}`);
if (campaign.stages.some((record) => record.id === pcgrlTemplate.id)) fail("PCGRL 演武错误注册为主线关卡");
if (campaign.stages.some((record) => record.id === mapElitesTemplate.id)) fail("MAP-Elites 演武错误注册为主线关卡");
if (pcgrlTemplate.stage?.map?.size?.[0] !== 19 || pcgrlTemplate.stage?.map?.size?.[1] !== 14) fail("PCGRL 演武尺寸不是 19x14");
if (!pcgrlTemplate.isProcedural || !String(pcgrlTemplate.chapter).includes("非主线")) fail("PCGRL 演武缺少非主线标记");
if (!asArray(pcgrlTemplate.story?.intro).some((entry) => String(entry.text).includes("不作为史实结论"))) fail("PCGRL 演武缺少生成内容史实边界说明");
if (!mapElitesTemplate.isProcedural || !String(mapElitesTemplate.chapter).includes("非主线")) fail("MAP-Elites 演武缺少非主线标记");
if (!asArray(mapElitesTemplate.story?.intro).some((entry) => String(entry.text).includes("不是史实复原"))) fail("MAP-Elites 演武缺少史实边界说明");
if (mapElitesArchive.entries?.length !== 25) fail(`MAP-Elites 档案不是 5x5：${mapElitesArchive.entries?.length}`);
if (asArray(mapElitesArchive.entries).some((entry) => !mapElitesRuntime.validate(entry).valid)) fail("MAP-Elites 档案存在未通过硬校验的精英");
if (Object.keys(gameSystems.SKILLS).length !== 7) fail("七职业战技契约不完整");
if (gameSystems.PROFILE_VERSION < 5) fail("存档未升级到地图细节设置契约 v5");
if (Object.keys(gameSystems.EQUIPMENT).length < 7) fail("前十二章装备成长契约不完整");
if (Object.keys(difficultyProfiles.profiles || {}).length !== 172) fail("运行时难度画像不是 172 关");
if (gameSystems.effectiveUnitLevel(1, "enemy", { armyRank: 60 }, 172, "hard") !== gameSystems.PROGRESSION.maxLevel) fail("最终关敌军等级未达到成长上限");
for (const stageProfile of Object.values(difficultyProfiles.profiles || {})) {
  if (stageProfile.objectiveType === "narrative") continue;
  const player = gameSystems.normalizeProfile({ armyRank: stageProfile.recommendedLevel }, []);
  const easy = gameSystems.stageDifficultyAssessment(stageProfile, player, "easy").riskScore;
  const medium = gameSystems.stageDifficultyAssessment(stageProfile, player, "medium").riskScore;
  const hard = gameSystems.stageDifficultyAssessment(stageProfile, player, "hard").riskScore;
  if (!(easy < medium && medium < hard)) fail(`${stageProfile.id} 三档难度风险不单调：${easy}/${medium}/${hard}`);
}
if (!gameSystems.REPLAY_SCHEMA) fail("缺少版本化战斗回放契约");
if (gameSystems.MAP_DETAIL_MODES.length !== 3) fail("地图细节三档契约不完整");
if (!["W", "G", "P", "C", "~", "r"].every((char) => gameSystems.isStructuralTerrain(char))) fail("结构地形保真契约不完整");
if (["f", "g", "F", "w", "m", "i"].some((char) => gameSystems.isStructuralTerrain(char))) fail("自然地表错误进入结构保真层");
if (densityReport.result !== "PASS" || densityReport.summary?.stages !== 172 || densityReport.summary?.maps !== 169) fail("地图纹理密度发布门禁未通过");
if (densityReport.summary?.minimum_structural_fidelity < densityReport.thresholds?.structural_fidelity_min) fail("结构地物保真率低于门禁");

const heroIds = new Set(asArray(config.heroes).map((hero) => hero.id));
const stageIds = new Set();
let dialogueCount = 0;
let runtimeDialogueCount = 0;
let generatedUnits = 0;

for (const record of campaign.stages) {
  if (stageIds.has(record.id)) fail(`重复关卡 ID：${record.id}`);
  stageIds.add(record.id);
  const luaFile = path.join(WEB, "scenario", "stage", record.file);
  if (!fs.existsSync(luaFile)) fail(`${record.id} 缺少 Lua 文件`);
  const mapFile = path.join(WEB, "assets", "maps", record.mapAsset.replace(/\.[^.]+$/, ".webp"));
  if (!fs.existsSync(mapFile) || fs.statSync(mapFile).size === 0) fail(`${record.id} 缺少 WebP 地图`);
  const size = asArray(record.stage?.map?.size).map(Number);
  const rows = asArray(record.stage?.map?.terrain);
  if (size.length !== 2 || size.some((value) => !Number.isFinite(value) || value <= 0)) fail(`${record.id} 地图尺寸无效`);
  if (rows.length !== size[1] || rows.some((row) => [...row].length !== size[0])) fail(`${record.id} 地形矩阵与尺寸不符`);
  for (const unit of record.smoke?.generatedUnits || []) {
    generatedUnits++;
    const [x, y] = unit.position;
    if (x < 0 || x >= size[0] || y < 0 || y >= size[1]) fail(`${record.id} 出生点越界：${unit.hero}@${x},${y}`);
    if (!heroIds.has(unit.hero)) warnings.push(`${record.id} 使用后备单位配置：${unit.hero}`);
  }
  dialogueCount += asArray(record.story?.intro).length + asArray(record.story?.victory).length + asArray(record.story?.defeat).length;
  for (const section of [record.story?.intro, record.story?.victory, record.story?.defeat]) {
    const normalized = gameSystems.normalizeStoryEntries(asArray(section), 110);
    runtimeDialogueCount += normalized.length;
    if (normalized.some((entry) => entry.speaker === "原著" || entry.text.length > 110)) fail(`${record.id} 剧情运行时清洗失败`);
  }
  if (!record.title || !record.battleTitle || !record.objective) fail(`${record.id} 缺少标题或目标`);
  if (!record.smoke || record.smoke.initialEndCondition == null) fail(`${record.id} 缺少首轮结束条件结果`);
}

for (const required of ["index.html", "styles.css", "game.js", "game-systems.js", "runtime.js", "pcgrl.js", "map-elites.js", "scenario/difficulty-profiles.json", "scenario/pcgrl-masui.json", "scenario/stage/pcgrl_masui.lua", "scenario/map-elites-chuisha.json", "scenario/map-elites-chuisha.archive.json", "scenario/stage/map_elites_chuisha.lua", "vendor/fengari-web.js", "vendor/LICENSE"]) {
  if (!fs.existsSync(path.join(WEB, required))) fail(`缺少发布文件：${required}`);
}

const releaseFiles = new Set();
for (const relative of ["index.html", "styles.css", "game.js", "game-systems.js", "runtime.js", "pcgrl.js", "map-elites.js", "README.md", "audio/dialogue-manifest.json"]) {
  releaseFiles.add(path.join(WEB, relative));
}
for (const folder of ["assets", "scenario", "vendor"]) {
  for (const file of folderFiles(path.join(WEB, folder))) releaseFiles.add(file);
}
const normalizedVoiceManifest = gameSystems.normalizeVoiceManifest(voiceManifest);
if (normalizedVoiceManifest.entries.length !== asArray(voiceManifest.entries).length) fail("配音清单包含不安全或无效路径");
for (const entry of normalizedVoiceManifest.entries) {
  const file = path.resolve(WEB, entry.file);
  if (!file.startsWith(`${WEB}${path.sep}`) || !fs.existsSync(file)) fail(`配音发布文件缺失：${entry.file}`);
  else releaseFiles.add(file);
}
const bytes = [...releaseFiles].reduce((sum, file) => sum + fs.statSync(file).size, 0);
const uploadLimit = 200 * 1024 * 1024;
if (bytes >= uploadLimit) fail(`发布目录超过 200 MB：${(bytes / 1024 / 1024).toFixed(2)} MB`);

const summary = {
  stages: campaign.stages.length,
  maps: mapIndex.sourceCount,
  heroes: heroIds.size,
  generatedUnits,
  dialogueCount,
  runtimeDialogueCount,
  classSkills: Object.keys(gameSystems.SKILLS).length,
  equipment: Object.keys(gameSystems.EQUIPMENT).length,
  difficultyProfiles: Object.keys(difficultyProfiles.profiles || {}).length,
  replaySchema: gameSystems.REPLAY_SCHEMA,
  profileVersion: gameSystems.PROFILE_VERSION,
  mapDensity: densityReport.summary,
  mapElitesArchiveCells: mapElitesArchive.entries.length,
  releaseBytes: bytes,
  releaseFiles: releaseFiles.size,
  releaseMiB: Number((bytes / 1024 / 1024).toFixed(2)),
  warnings: [...new Set(warnings)].length,
  errors: errors.length,
  result: errors.length ? "FAIL" : "PASS"
};

console.log(JSON.stringify(summary, null, 2));
if (errors.length) {
  console.error(errors.slice(0, 50).join("\n"));
  process.exitCode = 1;
}
