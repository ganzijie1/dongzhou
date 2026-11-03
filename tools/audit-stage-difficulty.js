"use strict";

const fs = require("node:fs");
const path = require("node:path");
const systems = require("../web-game/game-systems.js");
const pcgrl = require("../web-game/pcgrl.js");
const campaign = require("../web-game/scenario/campaign.json");
const pcgrlTemplate = require("../web-game/scenario/pcgrl-masui.json");
const happo = require("../unity-remake/Assets/Resources/Models/HappoMobile.json");
const level60SmokePath = path.join(__dirname, "..", "output", "happo_level60_smoke15.json");
const level60Smoke = fs.existsSync(level60SmokePath) ? JSON.parse(fs.readFileSync(level60SmokePath, "utf8")) : null;

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const round = (value, digits = 3) => Number(Number(value).toFixed(digits));
const percentile = (values, p) => {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return 0;
  return sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * p))];
};

function classifyObjective(stage, enemyCount) {
  const text = `${stage.objective || ""} ${stage.title || ""}`;
  if (!enemyCount || /观看|剧情|对话|过场/.test(text)) return "narrative";
  if (/护送|护卫/.test(text)) return "escort";
  if (/坚守|守住|防守|撑过|回合/.test(text)) return "defend";
  if (/突围|撤退|脱离|逃/.test(text)) return "escape";
  if (/占领|夺取|攻破|城门|营寨/.test(text)) return "capture";
  return "defeat";
}

function minimumDistance(friendlies, enemies) {
  let result = Infinity;
  for (const left of friendlies) {
    for (const right of enemies) {
      const [lx, ly] = left.position || [0, 0];
      const [rx, ry] = right.position || [0, 0];
      result = Math.min(result, Math.abs(lx - rx) + Math.abs(ly - ry));
    }
  }
  return Number.isFinite(result) ? result : 0;
}

const IMPASSABLE_TERRAINS = new Set(["r", "W", "~", "i"]);

function gridGeometry(terrain, rawBlockedEdges, friendlies, enemies) {
  const height = terrain.length;
  const width = Math.max(0, ...terrain.map((row) => row.length));
  const key = (x, y) => `${x},${y}`;
  const blockedEdges = new Set();
  for (const edge of Array.isArray(rawBlockedEdges) ? rawBlockedEdges : []) {
    const from = edge?.from || [];
    const to = edge?.to || [];
    blockedEdges.add([key(from[0], from[1]), key(to[0], to[1])].sort().join("|"));
  }
  const passable = new Set();
  let transitions = 0;
  let comparedEdges = 0;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < terrain[y].length; x++) {
      if (!IMPASSABLE_TERRAINS.has(terrain[y][x])) passable.add(key(x, y));
      for (const [dx, dy] of [[1, 0], [0, 1]]) {
        const nx = x + dx; const ny = y + dy;
        if (ny >= height || nx >= (terrain[ny]?.length || 0)) continue;
        comparedEdges += 1;
        if (terrain[y][x] !== terrain[ny][nx]) transitions += 1;
      }
    }
  }
  const neighbors = (cellKey) => {
    const [x, y] = cellKey.split(",").map(Number);
    return [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]
      .map(([nx, ny]) => key(nx, ny))
      .filter((next) => passable.has(next) && !blockedEdges.has([cellKey, next].sort().join("|")));
  };

  const componentByCell = new Map();
  let connectedComponents = 0;
  for (const start of passable) {
    if (componentByCell.has(start)) continue;
    connectedComponents += 1;
    componentByCell.set(start, connectedComponents);
    const queue = [start];
    for (let cursor = 0; cursor < queue.length; cursor++) {
      for (const next of neighbors(queue[cursor])) {
        if (componentByCell.has(next)) continue;
        componentByCell.set(next, connectedComponents);
        queue.push(next);
      }
    }
  }

  let terrainPatches = 0;
  const patchVisited = new Set();
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < terrain[y].length; x++) {
      const start = key(x, y);
      if (patchVisited.has(start)) continue;
      terrainPatches += 1;
      patchVisited.add(start);
      const label = terrain[y][x];
      const queue = [[x, y]];
      for (let cursor = 0; cursor < queue.length; cursor++) {
        const [cx, cy] = queue[cursor];
        for (const [nx, ny] of [[cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]]) {
          const next = key(nx, ny);
          if (ny < 0 || ny >= height || nx < 0 || nx >= (terrain[ny]?.length || 0) || patchVisited.has(next)) continue;
          if (terrain[ny][nx] !== label) continue;
          patchVisited.add(next);
          queue.push([nx, ny]);
        }
      }
    }
  }

  const discovery = new Map();
  const low = new Map();
  const parent = new Map();
  const articulation = new Set();
  let time = 0;
  function visit(node) {
    discovery.set(node, ++time);
    low.set(node, discovery.get(node));
    let children = 0;
    for (const next of neighbors(node)) {
      if (!discovery.has(next)) {
        parent.set(next, node);
        children += 1;
        visit(next);
        low.set(node, Math.min(low.get(node), low.get(next)));
        if (!parent.has(node) && children > 1) articulation.add(node);
        if (parent.has(node) && low.get(next) >= discovery.get(node)) articulation.add(node);
      } else if (parent.get(node) !== next) {
        low.set(node, Math.min(low.get(node), discovery.get(next)));
      }
    }
  }
  for (const node of passable) if (!discovery.has(node)) visit(node);

  const friendlyComponents = new Set(friendlies.map((unit) => componentByCell.get(key(...(unit.position || [0, 0])))).filter(Boolean));
  const enemyComponents = new Set(enemies.map((unit) => componentByCell.get(key(...(unit.position || [0, 0])))).filter(Boolean));
  const deploymentsConnected = [...friendlyComponents].some((component) => enemyComponents.has(component));
  const totalCells = Math.max(1, terrain.reduce((sum, row) => sum + row.length, 0));
  return {
    width,
    height,
    connectedComponents,
    deploymentsConnected,
    articulationPoints: articulation.size,
    articulationRatio: articulation.size / Math.max(1, passable.size),
    terrainTransitionRatio: transitions / Math.max(1, comparedEdges),
    terrainPatchDensity: terrainPatches * 100 / totalCells
  };
}

const rows = campaign.stages.map((stage) => {
  const units = (stage.smoke?.generatedUnits || []).filter((unit) => unit.alive !== false);
  const friendlies = units.filter((unit) => unit.force === "own" || unit.force === "ally");
  const enemies = units.filter((unit) => unit.force === "enemy");
  const terrain = stage.stage?.map?.terrain || [];
  const cells = terrain.reduce((sum, row) => sum + row.length, 0);
  const barriers = terrain.reduce((sum, row) => sum + [...row].filter((char) => IMPASSABLE_TERRAINS.has(char)).length, 0);
  const enemyRatio = enemies.length / Math.max(1, friendlies.length);
  const minDistance = minimumDistance(friendlies, enemies);
  const objectiveType = classifyObjective(stage, enemies.length);
  const queuedCommands = stage.smoke?.queuedCommands?.length || 0;
  const invulnerableEnemies = enemies.filter((unit) => unit.invulnerable).length;
  const sourceLevels = [...new Set(units.map((unit) => Number(unit.level || 1)))].sort((a, b) => a - b);
  const geometry = gridGeometry(terrain, stage.stage?.map?.blocked_edges, friendlies, enemies);
  const narrative = objectiveType === "narrative";
  const objectiveRisk = { defeat: 0, capture: 5, defend: 7, escort: 10, escape: 8, narrative: 0 }[objectiveType];
  const structuralRisk = narrative ? 0 : round(
    38 * clamp((enemyRatio - 0.5) / 2.5, 0, 1)
    + 18 * clamp((barriers / Math.max(1, cells)) / 0.35, 0, 1)
    + 14 * clamp(minDistance / Math.max(1, Number(stage.turnLimit || 1) * 4), 0, 1)
    + 8 * clamp(queuedCommands / 8, 0, 1)
    + 5 * clamp(invulnerableEnemies / Math.max(1, enemies.length), 0, 1)
    + 6 * clamp(geometry.articulationRatio / 0.08, 0, 1)
    + 6 * clamp((geometry.terrainTransitionRatio - 0.2) / 0.4, 0, 1)
    + objectiveRisk,
    1
  );
  return {
    index: stage.index,
    id: stage.id,
    chapter: stage.chapter,
    battleTitle: stage.battleTitle,
    objective: stage.objective,
    objectiveType,
    recommendedLevel: systems.recommendedStageLevel(stage.index),
    turnLimit: stage.turnLimit,
    ownUnits: friendlies.length,
    enemyUnits: enemies.length,
    enemyRatio: round(enemyRatio),
    minDeploymentDistance: minDistance,
    barrierRatio: round(barriers / Math.max(1, cells)),
    queuedCommands,
    invulnerableEnemies,
    sourceLevels,
    connectedComponents: geometry.connectedComponents,
    deploymentsConnected: geometry.deploymentsConnected,
    articulationPoints: geometry.articulationPoints,
    articulationRatio: round(geometry.articulationRatio),
    terrainTransitionRatio: round(geometry.terrainTransitionRatio),
    terrainPatchDensity: round(geometry.terrainPatchDensity),
    structuralRisk
  };
});

const combat = rows.filter((row) => row.objectiveType !== "narrative");
const barrierP90 = percentile(combat.map((row) => row.barrierRatio), 0.9);
const articulationP90 = percentile(combat.map((row) => row.articulationRatio), 0.9);
const transitionP90 = percentile(combat.map((row) => row.terrainTransitionRatio), 0.9);
let previousCombat = null;
for (const row of combat) {
  const flags = [];
  if (row.enemyRatio >= 2) flags.push("enemy-ratio-high");
  if (row.enemyRatio <= 0.5) flags.push("enemy-ratio-low");
  if (row.barrierRatio >= barrierP90 && row.barrierRatio > 0) flags.push("barrier-density-p90");
  if (row.articulationRatio >= articulationP90 && row.articulationRatio > 0) flags.push("bottleneck-p90");
  if (row.terrainTransitionRatio >= transitionP90 && row.terrainTransitionRatio > 0) flags.push("texture-transition-p90");
  if (!row.deploymentsConnected) flags.push("deployment-components-disconnected");
  if (row.turnLimit <= Math.ceil(row.minDeploymentDistance / 4) + 2) flags.push("turn-budget-tight");
  if (row.queuedCommands >= 8) flags.push("script-complexity-high");
  if (row.sourceLevels.some((level) => level !== 1)) flags.push("source-level-outlier");
  if (previousCombat && Math.abs(row.enemyRatio - previousCombat.enemyRatio) >= 0.75) flags.push("adjacent-force-ratio-jump");
  row.flags = flags;
  previousCombat = row;
}
for (const row of rows.filter((row) => row.objectiveType === "narrative")) row.flags = ["narrative-only"];

const objectiveDistribution = Object.fromEntries([...new Set(rows.map((row) => row.objectiveType))]
  .map((key) => [key, rows.filter((row) => row.objectiveType === key).length]));
const topRisk = [...combat].sort((a, b) => b.structuralRisk - a.structuralRisk).slice(0, 20);
const flagged = combat.filter((row) => row.flags.length).sort((a, b) => b.flags.length - a.flags.length || b.structuralRisk - a.structuralRisk);
const sourceLevelOutliers = rows.filter((row) => row.sourceLevels.some((level) => level !== 1));
const release = happo.release_evaluation;
const pcgrlGeometryValidation = { cases: 0, valid: 0, fallback: 0, worst: { transitionRatio: 0, patchDensity: 0, articulationRatio: 0 } };
for (const difficulty of systems.DIFFICULTIES) {
  for (let seed = 1; seed <= 20; seed++) {
    const raw = Array.from({ length: pcgrl.CELL_COUNT }, (_, index) => (index * 17 + seed * 13) % 4);
    const generated = pcgrl.generate(raw, pcgrlTemplate.stage.map.terrain, difficulty, seed);
    pcgrlGeometryValidation.cases++;
    if (generated.meta.validation.valid) pcgrlGeometryValidation.valid++;
    if (generated.meta.fallback) pcgrlGeometryValidation.fallback++;
    for (const key of Object.keys(pcgrlGeometryValidation.worst)) {
      pcgrlGeometryValidation.worst[key] = Math.max(
        pcgrlGeometryValidation.worst[key], Number(generated.meta.validation.geometry?.[key] || 0));
    }
  }
}
for (const key of Object.keys(pcgrlGeometryValidation.worst)) pcgrlGeometryValidation.worst[key] = round(pcgrlGeometryValidation.worst[key]);

const report = {
  generatedAt: new Date().toISOString(),
  method: "Static triage only. structuralRisk is not a player difficulty estimate.",
  methodSource: "https://my.feishu.cn/docx/AD99dmVLHoUjLIxBFEzcXl4tnZd",
  progressionContract: systems.PROGRESSION,
  battleDifficultyContract: systems.DIFFICULTY_PRESETS,
  pcgrlGeometryLimits: pcgrl.GEOMETRY_LIMITS,
  summary: {
    stages: rows.length,
    combatStages: combat.length,
    narrativeStages: rows.length - combat.length,
    flaggedCombatStages: flagged.length,
    sourceLevelOutliers: sourceLevelOutliers.length,
    enemyRatio: {
      p10: round(percentile(combat.map((row) => row.enemyRatio), 0.1)),
      p50: round(percentile(combat.map((row) => row.enemyRatio), 0.5)),
      p90: round(percentile(combat.map((row) => row.enemyRatio), 0.9)),
      max: round(Math.max(...combat.map((row) => row.enemyRatio)))
    },
    barrierRatioP90: round(barrierP90),
    articulationRatioP90: round(articulationP90),
    terrainTransitionRatioP90: round(transitionP90),
    objectiveDistribution,
    happoReleaseEvaluation: {
      stages: release.battle_stages,
      episodes: release.happo.episodes,
      enemyWinRate: release.happo.enemy_win_rate,
      enemyWinRateCi95: release.happo.enemy_win_rate_ci95,
      scriptedEnemyWinRate: release.scripted_baseline.enemy_win_rate,
      balancedAgainstScriptedPlayer: release.release_gate.balanced_against_scripted_player,
      trainedRoles: happo.trained_roles.length,
      totalRoles: happo.roles.length
    },
    level60SmokeEvaluation: level60Smoke ? {
      stages: level60Smoke.battle_stages,
      episodesPerStage: level60Smoke.episodes_per_stage,
      enemyWinRate: level60Smoke.happo.enemy_win_rate,
      enemyWinRateCi95: level60Smoke.happo.enemy_win_rate_ci95,
      scriptedEnemyWinRate: level60Smoke.scripted_baseline.enemy_win_rate,
      scriptedTimeoutRate: level60Smoke.scripted_baseline.timeout_rate,
      status: level60Smoke.release_gate.status
    } : null,
    pcgrlGeometryValidation
  },
  topRisk,
  flagged,
  sourceLevelOutliers,
  stages: rows
};

const docsDir = path.join(__dirname, "..", "docs");
fs.mkdirSync(docsDir, { recursive: true });
fs.writeFileSync(path.join(docsDir, "stage-difficulty-audit.json"), `${JSON.stringify(report, null, 2)}\n`);

const table = topRisk.slice(0, 15).map((row) =>
  `| ${row.index} | ${row.battleTitle} | ${row.recommendedLevel} | ${row.ownUnits}:${row.enemyUnits} | ${row.enemyRatio} | ${row.turnLimit} | ${row.barrierRatio} | ${row.terrainTransitionRatio} | ${row.articulationRatio} | ${row.structuralRisk} | ${row.flags.join(", ") || "-"} |`
).join("\n");
const outlierLines = sourceLevelOutliers.length
  ? sourceLevelOutliers.map((row) => `- 第 ${row.index} 关「${row.battleTitle}」：脚本等级 ${row.sourceLevels.join("/")}，运行时将按统一成长规则覆盖。`).join("\n")
  : "- 未发现脚本等级异常。";

const markdown = `# 东周列国志 172 关难度结构审计

生成时间：${report.generatedAt}

方法依据：[离散几何优化：数学模型、核心算法与工程实践](${report.methodSource})

## 结论

- 已先建立统一成长基线：主线 172 关按 1–60 级展开，军阶约每 3 个首通提升一级，最终战前达到 60 级；武将熟练度最多领先军阶 2 级。
- 三档难度已改为真实战斗参数：简单档降低敌军等级与生命/攻防并增加 25% 回合宽限；标准档保持基线；艰难档提高敌军 2 级、生命/攻击 12%、防御 8%，同时启用完整 HAPPO 概率。
- ${rows.length} 关中有 ${combat.length} 个战斗关、${rows.length - combat.length} 个纯剧情关；${flagged.length} 个战斗关至少触发一项结构风险标记。
- 敌我单位比中位数为 ${report.summary.enemyRatio.p50}，P90 为 ${report.summary.enemyRatio.p90}，最大值为 ${report.summary.enemyRatio.max}。这些只能用于排查跳变，不能直接等同于玩家难度。
- 现有 HAPPO 发布评估在 ${release.happo.episodes} 局中敌方胜率为 ${(release.happo.enemy_win_rate * 100).toFixed(0)}%，95% 区间 [${release.happo.enemy_win_rate_ci95.map((value) => value.toFixed(4)).join(", ")}]；脚本基线敌胜率为 ${(release.scripted_baseline.enemy_win_rate * 100).toFixed(0)}%。该结果证明当前验收对手失衡，不能用来证明关卡平衡。
- HAPPO 仅训练 ${happo.trained_roles.length}/${happo.roles.length} 个角色头，其余角色采用第一个合法动作，现阶段不能作为全职业难度裁判。
- 60 级新基线的 14 个战斗关单种子烟测仍为 HAPPO 敌胜率 ${(Number(level60Smoke?.happo?.enemy_win_rate || 0) * 100).toFixed(0)}%、脚本敌胜率 ${(Number(level60Smoke?.scripted_baseline?.enemy_win_rate || 0) * 100).toFixed(0)}%，脚本超时率 ${(Number(level60Smoke?.scripted_baseline?.timeout_rate || 0) * 100).toFixed(0)}%。它只验证运行契约，不作为平衡置信结论。
- 已引入离散几何的网格图指标：地形标签总变差（相邻格标签切换率）、地形斑块密度、可通行连通分量和割点比例。它们分别对应纹理过密、碎片化、不可达和单通道瓶颈风险。
- PCGRL 离散几何修复在 ${pcgrlGeometryValidation.cases} 个三档种子用例中通过 ${pcgrlGeometryValidation.valid} 个，回退 ${pcgrlGeometryValidation.fallback} 个；最坏地形切换率 ${pcgrlGeometryValidation.worst.transitionRatio}、斑块密度 ${pcgrlGeometryValidation.worst.patchDensity}、割点率 ${pcgrlGeometryValidation.worst.articulationRatio}。

## 结构风险最高的 15 关

> 结构风险分数只综合兵力比、障碍密度、接敌距离/回合预算、脚本复杂度与目标类型，用于决定测试顺序，不是通关率预测。

| 关 | 战役 | 建议等级 | 友:敌 | 敌我比 | 回合 | 障碍率 | 纹理切换 | 割点率 | 风险 | 标记 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
${table}

## 脚本等级异常

${outlierLines}

## 下一轮验收

1. 用统一等级重新跑每关至少 20 个确定性种子，记录胜率、回合、伤亡、道具消耗和终局原因。
2. 同一关使用弱、中、强三档代理，目标是胜率随代理强度单调上升，而不是让单一 HAPPO 全胜。
3. 优先人工复核上表 15 关和相邻兵力比跳变关；纯剧情关不参与战斗难度统计。
4. 真人数据进入后，以目标胜率区间和置信区间替换本报告的结构风险分数。

完整逐关数据见 \`docs/stage-difficulty-audit.json\`。
`;
fs.writeFileSync(path.join(docsDir, "stage-difficulty-audit.md"), markdown);

console.log(JSON.stringify(report.summary, null, 2));
