(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouGameSystems = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const PROFILE_VERSION = 11;
  const TELEMETRY_SCHEMA = "dongzhou-battle-v4";
  const REPLAY_SCHEMA = "dongzhou-replay-v1";
  const POLICY_VERSION = "happo-2026-11-02";
  const RUNTIME_VERSION = "dongzhou-web-0.7.0";
  const DIFFICULTIES = ["easy", "medium", "hard"];
  const DIFFICULTY_PRESETS = Object.freeze({
    easy: Object.freeze({
      id: "easy", enemyLevelOffset: -2, enemyHpMultiplier: 0.85,
      enemyPowerMultiplier: 0.88, enemyDefenseMultiplier: 0.90,
      aiPolicyRate: 0.30, turnLimitMultiplier: 1.25, rewardMultiplier: 0.85,
      structuralRiskOffset: -12
    }),
    medium: Object.freeze({
      id: "medium", enemyLevelOffset: 0, enemyHpMultiplier: 1,
      enemyPowerMultiplier: 1, enemyDefenseMultiplier: 1,
      aiPolicyRate: 0.65, turnLimitMultiplier: 1, rewardMultiplier: 1,
      structuralRiskOffset: 0
    }),
    hard: Object.freeze({
      id: "hard", enemyLevelOffset: 2, enemyHpMultiplier: 1.12,
      enemyPowerMultiplier: 1.12, enemyDefenseMultiplier: 1.08,
      aiPolicyRate: 1, turnLimitMultiplier: 1, rewardMultiplier: 1.2,
      structuralRiskOffset: 14
    })
  });
  const MAP_DETAIL_MODES = ["calm", "balanced", "original"];
  const FORMATION_PRESETS = Object.freeze({
    balanced: Object.freeze({ id: "balanced", name: "中军持衡", power: 1, defense: 1, hp: 1, move: 0, maxMp: 0 }),
    assault: Object.freeze({ id: "assault", name: "前军锐进", power: 1.08, defense: 0.94, hp: 1, move: 0, maxMp: 0 }),
    bulwark: Object.freeze({ id: "bulwark", name: "坚营固守", power: 0.95, defense: 1.1, hp: 1.06, move: 0, maxMp: 0 }),
    maneuver: Object.freeze({ id: "maneuver", name: "迂回游击", power: 1.02, defense: 0.97, hp: 1, move: 1, maxMp: 2 })
  });
  const STRUCTURE_DETAIL_TERRAINS = new Set(["W", "c", "b", "e", "G", "D", "P", "h", "C"]);
  const BARRIER_TERRAINS = new Set(["r", "~", "v"]);
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const PROGRESSION = Object.freeze({
    maxLevel: 60,
    stagesPerLevel: 3,
    campaignStageCount: 172,
    armyXpPerLevel: 600,
    heroXpPerLevel: 100,
    heroLeadCap: 2,
    firstClearHeroXp: 50,
    replayWinHeroXp: 15,
    replayLossHeroXp: 8,
    proceduralWinHeroXp: 10,
    proceduralLossHeroXp: 5
  });

  function armyRankForClears(clears) {
    const clearCount = clamp(Number(clears || 0), 0, PROGRESSION.campaignStageCount);
    return clamp(1 + Math.floor(
      clearCount * (PROGRESSION.maxLevel - 1) / (PROGRESSION.campaignStageCount - 1)
    ), 1, PROGRESSION.maxLevel);
  }

  function armyXpForClears(clears, rank = armyRankForClears(clears)) {
    if (rank >= PROGRESSION.maxLevel) return 0;
    const clearCount = clamp(Number(clears || 0), 0, PROGRESSION.campaignStageCount);
    const denominator = PROGRESSION.maxLevel - 1;
    const span = PROGRESSION.campaignStageCount - 1;
    const rankStart = Math.ceil((rank - 1) * span / denominator);
    const nextRankStart = Math.ceil(rank * span / denominator);
    return Math.floor((clearCount - rankStart) * PROGRESSION.armyXpPerLevel / Math.max(1, nextRankStart - rankStart));
  }

  function heroLevelCap(armyRank) {
    return clamp(Number(armyRank || 1) + PROGRESSION.heroLeadCap, 1, PROGRESSION.maxLevel);
  }

  function heroLevelFromXp(xp, cap = PROGRESSION.maxLevel) {
    return Math.min(clamp(Number(cap || 1), 1, PROGRESSION.maxLevel),
      1 + Math.floor(Math.max(0, Number(xp || 0)) / PROGRESSION.heroXpPerLevel));
  }

  function maxHeroXpForCap(cap) {
    const safeCap = clamp(Number(cap || 1), 1, PROGRESSION.maxLevel);
    return safeCap >= PROGRESSION.maxLevel
      ? PROGRESSION.maxLevel * PROGRESSION.heroXpPerLevel - 1
      : safeCap * PROGRESSION.heroXpPerLevel - 1;
  }

  const SKILLS = Object.freeze({
    Lord: { id: "inspire", name: "鼓舞", cost: 7, range: 3, target: "ally", kind: "buff", power: 10, turns: 2 },
    King: { id: "royal_order", name: "王命", cost: 10, range: 3, target: "ally", kind: "buff", power: 8, defense: 8, turns: 2 },
    Infantry: { id: "shield_wall", name: "坚阵", cost: 4, range: 0, target: "self", kind: "buff", defense: 12, turns: 2 },
    Cavalry: { id: "charge", name: "突击", cost: 6, range: 1, target: "enemy", kind: "damage", amount: 42 },
    Archer: { id: "volley", name: "齐射", cost: 7, range: 3, target: "enemy", kind: "damage", amount: 36 },
    Strategist: { id: "fire", name: "火计", cost: 8, range: 4, target: "enemy", kind: "damage", amount: 50 },
    Support: { id: "heal", name: "援护", cost: 8, range: 4, target: "ally", kind: "heal", amount: 52 }
  });

  const EQUIPMENT = Object.freeze({
    bronze_halberd: { id: "bronze_halberd", slot: "weapon", name: "青铜长戈", cost: 240, unlockStage: 1, power: 4 },
    iron_sword: { id: "iron_sword", slot: "weapon", name: "精铁剑", cost: 620, unlockStage: 7, power: 8 },
    hide_armor: { id: "hide_armor", slot: "armor", name: "犀皮甲", cost: 360, unlockStage: 3, defense: 4 },
    lamellar_armor: { id: "lamellar_armor", slot: "armor", name: "札甲", cost: 760, unlockStage: 10, defense: 8 },
    war_horse: { id: "war_horse", slot: "mount", name: "良驹", cost: 520, unlockStage: 6, move: 1 },
    tiger_tally: { id: "tiger_tally", slot: "talisman", name: "虎符", cost: 680, unlockStage: 9, maxMp: 6 },
    jade_tally: { id: "jade_tally", slot: "talisman", name: "玉节", cost: 920, unlockStage: 12, maxMp: 10 }
  });
  const EQUIPMENT_SLOTS = ["weapon", "armor", "mount", "talisman"];

  function normalizeBandit(raw) {
    const source = raw || {};
    const arms = {};
    for (const difficulty of DIFFICULTIES) {
      const arm = source.arms?.[difficulty] || {};
      arms[difficulty] = {
        count: Math.max(0, Number(arm.count || 0)),
        value: clamp(Number.isFinite(Number(arm.value)) ? Number(arm.value) : 0.5, 0, 1)
      };
    }
    return { enabled: source.enabled !== false, epsilon: clamp(Number(source.epsilon ?? 0.1), 0, 0.2), arms };
  }

  function normalizeKnowledgeQuiz(raw) {
    const source = raw && typeof raw === "object" ? raw : {};
    const pending = source.pending && typeof source.pending === "object"
      && source.pending.question && source.pending.action ? source.pending : null;
    return {
      score: Math.max(0, Number(source.score || 0)),
      pending,
      receipts: [...new Set(Array.isArray(source.receipts) ? source.receipts.map(String) : [])].slice(-100),
      history: Array.isArray(source.history) ? source.history.slice(-20) : []
    };
  }

  function recordKnowledgeQuizResult(rawProfile, result) {
    const profile = rawProfile && typeof rawProfile === "object" ? rawProfile : {};
    profile.knowledgeQuiz = normalizeKnowledgeQuiz(profile.knowledgeQuiz);
    const receipt = result?.receipt;
    const digest = String(receipt?.digest || "");
    const kernel = receipt?.kernel;
    const score = Number(result?.score);
    const valid = /^[0-9a-f]{64}$/.test(digest)
      && kernel?.module === "dongzhou_knowledge_tournament"
      && kernel?.state === "SEALED"
      && [0, 10].includes(score)
      && typeof result?.correct === "boolean"
      && (result.correct ? score === 10 : score === 0)
      && Number.isInteger(result?.selectedIndex)
      && Number.isInteger(result?.correctIndex)
      && ["COMPLETED", "EXPIRED"].includes(result?.state)
      && (result?.state !== "EXPIRED" || result.correct === false)
      && typeof result?.questionId === "string";
    if (!valid) return { ok: false, reason: "invalid-receipt", profile };
    if (profile.knowledgeQuiz.receipts.includes(digest)) {
      return { ok: true, replayed: true, profile };
    }
    profile.knowledgeQuiz.score += score;
    profile.knowledgeQuiz.receipts = [...profile.knowledgeQuiz.receipts, digest].slice(-100);
    profile.knowledgeQuiz.history = [...profile.knowledgeQuiz.history, result].slice(-20);
    if (profile.knowledgeQuiz.pending?.question?.id === result.questionId) {
      profile.knowledgeQuiz.pending = null;
    }
    return { ok: true, replayed: false, profile };
  }

  function normalizeProfile(raw, stages) {
    const source = raw && typeof raw === "object" ? raw : {};
    const completed = [...new Set(Array.isArray(source.completed) ? source.completed.map(String) : [])];
    const inferredClears = completed.length;
    const inferredRank = armyRankForClears(inferredClears);
    const armyRank = clamp(Math.max(Number(source.armyRank || 1), inferredRank), 1, PROGRESSION.maxLevel);
    const inferredArmyXp = armyRank === inferredRank ? armyXpForClears(inferredClears, armyRank) : Number(source.armyXp || 0);
    const battleHistory = Array.isArray(source.battleHistory) ? source.battleHistory.slice(-200) : [];
    const ownedEquipment = [...new Set(Array.isArray(source.ownedEquipment) ? source.ownedEquipment.filter((id) => EQUIPMENT[id]) : [])];
    const equipped = Object.fromEntries(EQUIPMENT_SLOTS.map((slot) => {
      const id = source.equipped?.[slot];
      return [slot, ownedEquipment.includes(id) && EQUIPMENT[id]?.slot === slot ? id : null];
    }));
    const heroMastery = {};
    for (const [heroId, value] of Object.entries(source.heroMastery || {})) {
      let xp = Math.max(0, Number(value?.xp || 0));
      if (Number(source.schemaVersion || 0) < PROFILE_VERSION) {
        xp = Math.max(xp, (clamp(Number(value?.level || 1), 1, PROGRESSION.maxLevel) - 1) * PROGRESSION.heroXpPerLevel);
      }
      const cap = heroLevelCap(armyRank);
      xp = Math.min(xp, maxHeroXpForCap(cap));
      heroMastery[canonicalHeroId(heroId)] = { xp, level: heroLevelFromXp(xp, cap) };
    }
    return {
      ...source,
      schemaVersion: PROFILE_VERSION,
      completed,
      lastStage: source.lastStage || null,
      armyRank,
      armyXp: armyRank >= PROGRESSION.maxLevel ? 0 : clamp(inferredArmyXp, 0, PROGRESSION.armyXpPerLevel - 1),
      coins: Math.max(0, Number(source.coins ?? 240)),
      inventory: {
        medicine: Math.max(0, Number(source.inventory?.medicine ?? 3)),
        spirit_powder: Math.max(0, Number(source.inventory?.spirit_powder ?? 1))
      },
      ownedEquipment,
      equipped,
      heroMastery,
      replays: Array.isArray(source.replays) ? source.replays.slice(-20) : [],
      tutorial: { completed: Boolean(source.tutorial?.completed), dismissed: Boolean(source.tutorial?.dismissed) },
      battleHistory,
      knowledgeQuiz: normalizeKnowledgeQuiz(source.knowledgeQuiz),
      routePreferences: Object.fromEntries(
        Object.entries(source.routePreferences || {}).filter(([, method]) =>
          ["campaign_progression", "fixed_point", "npc_dialog"].includes(method)
        )
      ),
      difficultyBandit: { ...normalizeBandit(source.difficultyBandit), enabled: source.settings?.telemetryEnabled !== false && source.difficultyBandit?.enabled !== false },
      formation: FORMATION_PRESETS[source.formation] ? source.formation : "balanced",
      stageVanguards: source.stageVanguards && typeof source.stageVanguards === "object" ? { ...source.stageVanguards } : {},
      stageFailures: Object.fromEntries(Object.entries(source.stageFailures || {}).map(([id, count]) => [String(id), clamp(Number(count || 0), 0, 99)])),
      woundedHeroes: Object.fromEntries(Object.entries(source.woundedHeroes || {}).map(([id, battles]) => [canonicalHeroId(id), clamp(Number(battles || 0), 0, 3)]).filter(([, battles]) => battles > 0)),
      campaignResources: {
        provisions: clamp(Number(source.campaignResources?.provisions ?? 100), 0, 200),
        morale: clamp(Number(source.campaignResources?.morale ?? 70), 0, 100)
      },
      settings: {
        ...source.settings,
        battleDifficulty: ["easy", "medium", "hard"].includes(source.settings?.battleDifficulty)
          ? source.settings.battleDifficulty : "medium",
        mapDetail: MAP_DETAIL_MODES.includes(source.settings?.mapDetail)
          ? source.settings.mapDetail : "balanced",
        telemetryEnabled: source.settings?.telemetryEnabled !== false,
        aiNpcInteractionEnabled: source.settings?.aiNpcInteractionEnabled !== false,
        feedbackEnabled: source.settings?.feedbackEnabled !== false,
        transparentAssist: source.settings?.transparentAssist !== false,
        voiceEnabled: source.settings?.voiceEnabled !== false,
        voiceVolume: clamp(Number.isFinite(Number(source.settings?.voiceVolume)) ? Number(source.settings.voiceVolume) : 0.85, 0, 1),
        musicEnabled: source.settings?.musicEnabled !== false,
        musicVolume: clamp(Number.isFinite(Number(source.settings?.musicVolume)) ? Number(source.settings.musicVolume) : 0.42, 0, 1)
      },
      unlockedThrough: unlockedThrough({ completed }, stages || [])
    };
  }

  function mapDetailProfile(mode, compact = false) {
    if (mode === "original") return { mode, scale: 1, saturation: 1, contrast: 1, brightness: 1, gridAlpha: 0.17, unitHalo: 0.12 };
    if (mode === "calm") return { mode, scale: 0.45, saturation: 0.78, contrast: 0.86, brightness: 0.98, gridAlpha: 0.09, unitHalo: 0.32 };
    return compact
      ? { mode: "balanced", scale: 0.58, saturation: 0.86, contrast: 0.9, brightness: 0.99, gridAlpha: 0.11, unitHalo: 0.28 }
      : { mode: "balanced", scale: 0.62, saturation: 0.88, contrast: 0.92, brightness: 1, gridAlpha: 0.13, unitHalo: 0.24 };
  }

  function isStructuralTerrain(char) {
    return STRUCTURE_DETAIL_TERRAINS.has(char) || BARRIER_TERRAINS.has(char);
  }

  function preservesMapDetail(char) {
    return STRUCTURE_DETAIL_TERRAINS.has(char);
  }

  function isBarrierTerrain(char) {
    return BARRIER_TERRAINS.has(char);
  }

  function unlockedThrough(profile, stages) {
    const completed = new Set(profile?.completed || []);
    let furthest = 0;
    for (const stage of stages || []) if (completed.has(stage.id)) furthest = Math.max(furthest, Number(stage.index || 0));
    return Math.max(1, Math.min((stages || []).length || 1, furthest + 1));
  }

  function isStageUnlocked(stage, profile, stages) {
    if (!stage || stage.isProcedural) return true;
    return Number(stage.index || 1) <= unlockedThrough(profile, stages);
  }

  function recommendedStageLevel(index) {
    const stageIndex = clamp(Number(index || 1), 1, PROGRESSION.campaignStageCount);
    return clamp(1 + Math.floor(
      (stageIndex - 1) * (PROGRESSION.maxLevel - 1) / (PROGRESSION.campaignStageCount - 1)
    ), 1, PROGRESSION.maxLevel);
  }

  function difficultyPreset(difficulty) {
    return DIFFICULTY_PRESETS[difficulty] || DIFFICULTY_PRESETS.medium;
  }

  function effectiveTurnLimit(baseLimit, difficulty, assistActive = false) {
    const base = Math.max(1, Number(baseLimit || 1));
    if (base >= 90) return base;
    const assistMultiplier = assistActive ? 1.15 : 1;
    return Math.max(base, Math.ceil(base * difficultyPreset(difficulty).turnLimitMultiplier * assistMultiplier));
  }

  function unitDifficultyModifiers(team, difficulty) {
    const preset = difficultyPreset(difficulty);
    if (team !== "enemy") return { hp: 1, power: 1, defense: 1 };
    return {
      hp: preset.enemyHpMultiplier,
      power: preset.enemyPowerMultiplier,
      defense: preset.enemyDefenseMultiplier
    };
  }

  function effectiveUnitLevel(scriptedLevel, team, profile, stageIndex, difficulty) {
    const base = Math.max(1, Number(scriptedLevel || 1));
    if (team === "own") return Math.max(base, Number(profile?.armyRank || 1));
    const offset = difficultyPreset(difficulty).enemyLevelOffset;
    return Math.max(base, clamp(recommendedStageLevel(stageIndex) + offset, 1, PROGRESSION.maxLevel));
  }

  function masteryForHero(profile, heroId) {
    const mastery = profile?.heroMastery?.[canonicalHeroId(heroId)] || { xp: 0, level: 1 };
    const cap = heroLevelCap(profile?.armyRank || 1);
    const xp = Math.min(Math.max(0, Number(mastery.xp || 0)), maxHeroXpForCap(cap));
    return { xp, level: heroLevelFromXp(xp, cap) };
  }

  function effectiveHeroLevel(scriptedLevel, team, profile, stageIndex, difficulty, heroId) {
    const level = effectiveUnitLevel(scriptedLevel, team, profile, stageIndex, difficulty);
    return team === "own" ? Math.max(level, Number(masteryForHero(profile, heroId).level || 1)) : level;
  }

  function equipmentBonuses(profile) {
    const bonuses = { power: 0, defense: 0, move: 0, maxMp: 0 };
    for (const slot of EQUIPMENT_SLOTS) {
      const item = EQUIPMENT[profile?.equipped?.[slot]];
      if (!item) continue;
      for (const key of Object.keys(bonuses)) bonuses[key] += Number(item[key] || 0);
    }
    return bonuses;
  }

  function unitGrowthBonuses(level) {
    const gainedLevels = clamp(Number(level || 1), 1, PROGRESSION.maxLevel) - 1;
    return { power: gainedLevels * 1.5, defense: gainedLevels * 0.8 };
  }

  function formationModifiers(profile, heroId, classId, stageId) {
    const preset = FORMATION_PRESETS[profile?.formation] || FORMATION_PRESETS.balanced;
    const morale = clamp(Number(profile?.campaignResources?.morale ?? 70), 0, 100);
    const provisions = clamp(Number(profile?.campaignResources?.provisions ?? 100), 0, 200);
    const moraleFactor = clamp(1 + (morale - 50) / 500, 0.9, 1.1);
    const provisionFactor = provisions < 40 ? clamp(0.92 + provisions / 500, 0.92, 1) : 1;
    const wounded = Number(profile?.woundedHeroes?.[canonicalHeroId(heroId)] || 0) > 0;
    const vanguard = canonicalHeroId(profile?.stageVanguards?.[String(stageId)] || "") === canonicalHeroId(heroId);
    const mobileClass = classId === "Cavalry" || classId === "Archer";
    return {
      formation: preset.id,
      power: preset.power * moraleFactor * provisionFactor * (wounded ? 0.95 : 1) * (vanguard ? 1.08 : 1),
      defense: preset.defense * moraleFactor,
      hp: preset.hp * provisionFactor * (wounded ? 0.8 : 1),
      move: preset.id === "maneuver" && mobileClass ? preset.move : 0,
      maxMp: preset.maxMp + (vanguard ? 3 : 0),
      wounded,
      vanguard,
      undersupplied: provisions < 40
    };
  }

  function heroSkillRank(level) {
    const safeLevel = clamp(Number(level || 1), 1, PROGRESSION.maxLevel);
    return safeLevel >= 40 ? 3 : safeLevel >= 20 ? 2 : 1;
  }

  function retryAssist(profile, stageId) {
    const failures = Number(profile?.stageFailures?.[String(stageId)] || 0);
    const eligible = failures >= 2;
    const active = eligible && profile?.settings?.transparentAssist !== false;
    return { eligible, active, failures, turnMultiplier: active ? 1.15 : 1, medicine: active ? 1 : 0, morale: active ? 8 : 0, rewardMultiplier: active ? 0.9 : 1 };
  }

  function restArmy(rawProfile, stages = []) {
    const profile = normalizeProfile(rawProfile, stages);
    const cost = 120;
    if (profile.coins < cost) return { ok: false, reason: "insufficient-coins", profile };
    profile.coins -= cost;
    profile.campaignResources.provisions = clamp(profile.campaignResources.provisions + 30, 0, 200);
    profile.campaignResources.morale = clamp(profile.campaignResources.morale + 20, 0, 100);
    for (const heroId of Object.keys(profile.woundedHeroes)) {
      profile.woundedHeroes[heroId] -= 1;
      if (profile.woundedHeroes[heroId] <= 0) delete profile.woundedHeroes[heroId];
    }
    return { ok: true, profile, cost };
  }

  function missionContract(objectiveType) {
    return ({
      defeat: { id: "defeat", name: "歼敌", phases: ["接敌", "破阵", "肃清"] },
      capture: { id: "capture", name: "夺隘", phases: ["开路", "夺取", "固守"] },
      defend: { id: "defend", name: "坚守", phases: ["列阵", "承压", "待援"] },
      escort: { id: "escort", name: "护送", phases: ["清道", "护行", "接应"] },
      escape: { id: "escape", name: "突围", phases: ["聚兵", "破口", "脱离"] },
      narrative: { id: "narrative", name: "史事", phases: ["见证"] },
      procedural: { id: "procedural", name: "演武", phases: ["试探", "应变", "决胜"] }
    })[objectiveType] || { id: "scripted", name: "军令", phases: ["接战", "推进", "决胜"] };
  }

  function dailyChallenge(dateValue = new Date()) {
    const date = typeof dateValue === "string" ? dateValue.slice(0, 10) : dateValue.toISOString().slice(0, 10);
    let seed = 2166136261;
    for (const char of date) { seed ^= char.charCodeAt(0); seed = Math.imul(seed, 16777619); }
    return { date, seed: seed >>> 1, difficulty: ["easy", "medium", "hard"][(seed >>> 8) % 3] };
  }

  function availableEquipment(profile) {
    const clears = Number(profile?.completed?.length || 0);
    return Object.values(EQUIPMENT).filter((item) => clears >= item.unlockStage);
  }

  function buyEquipment(rawProfile, itemId) {
    const profile = normalizeProfile(rawProfile, []);
    const item = EQUIPMENT[itemId];
    if (!item || !availableEquipment(profile).some((entry) => entry.id === itemId)) return { ok: false, reason: "locked", profile };
    if (profile.ownedEquipment.includes(itemId)) return { ok: false, reason: "owned", profile };
    if (profile.coins < item.cost) return { ok: false, reason: "insufficient-coins", profile };
    profile.coins -= item.cost;
    profile.ownedEquipment.push(itemId);
    profile.equipped[item.slot] = itemId;
    return { ok: true, profile, item };
  }

  function equipItem(rawProfile, itemId) {
    const profile = normalizeProfile(rawProfile, []);
    const item = EQUIPMENT[itemId];
    if (!item || !profile.ownedEquipment.includes(itemId)) return { ok: false, reason: "not-owned", profile };
    profile.equipped[item.slot] = itemId;
    return { ok: true, profile, item };
  }

  function buySupply(rawProfile, itemId) {
    const prices = { medicine: 90, spirit_powder: 110 };
    const profile = normalizeProfile(rawProfile, []);
    if (!prices[itemId] || profile.coins < prices[itemId]) return { ok: false, reason: "insufficient-coins", profile };
    profile.coins -= prices[itemId];
    profile.inventory[itemId] += 1;
    return { ok: true, profile, cost: prices[itemId] };
  }

  function battleReward(outcome) {
    const turns = Math.max(1, Number(outcome.turns || 1));
    const turnLimit = Math.max(turns, Number(outcome.turnLimit || turns));
    const totalOwn = Math.max(1, Number(outcome.totalOwn || 1));
    const ownLosses = clamp(Number(outcome.ownLosses || 0), 0, totalOwn);
    const components = {
      outcome: outcome.won ? 1 : 0,
      efficiency: clamp(1 - turns / turnLimit, 0, 1),
      survival: clamp(1 - ownLosses / totalOwn, 0, 1),
      supplies: clamp(Number(outcome.supplies || 0) / 4, 0, 1)
    };
    const total = 0.55 * components.outcome + 0.2 * components.efficiency
      + 0.2 * components.survival + 0.05 * components.supplies;
    return { components, total: clamp(total, 0, 1) };
  }

  function updateBandit(bandit, difficulty, reward) {
    const next = normalizeBandit(bandit);
    if (!DIFFICULTIES.includes(difficulty)) return next;
    const arm = next.arms[difficulty];
    arm.count += 1;
    arm.value += (clamp(Number(reward || 0), 0, 1) - arm.value) / arm.count;
    return next;
  }

  function selectDifficulty(profile, requested, randomValue) {
    if (DIFFICULTIES.includes(requested)) {
      return { difficulty: requested, behaviorProbability: 1, mode: "manual", explored: false };
    }
    const bandit = normalizeBandit(profile?.difficultyBandit);
    if (!bandit.enabled) return { difficulty: "medium", behaviorProbability: 1, mode: "fallback", explored: false };
    const random = clamp(Number.isFinite(randomValue) ? randomValue : 0.5, 0, 0.999999);
    const bestValue = Math.max(...DIFFICULTIES.map((key) => bandit.arms[key].value));
    const best = DIFFICULTIES.filter((key) => Math.abs(bandit.arms[key].value - bestValue) < 1e-9);
    const explore = random < bandit.epsilon;
    const scaled = explore ? random / Math.max(bandit.epsilon, 1e-9)
      : (random - bandit.epsilon) / Math.max(1 - bandit.epsilon, 1e-9);
    const pool = explore ? DIFFICULTIES : best;
    const difficulty = pool[Math.min(pool.length - 1, Math.floor(scaled * pool.length))];
    const probability = bandit.epsilon / DIFFICULTIES.length + (best.includes(difficulty) ? (1 - bandit.epsilon) / best.length : 0);
    return { difficulty, behaviorProbability: probability, mode: "epsilon-greedy", explored: explore };
  }

  function wilsonInterval(successes, total, z = 1.96) {
    if (total <= 0) return [0, 0];
    const rate = successes / total;
    const denominator = 1 + z * z / total;
    const center = (rate + z * z / (2 * total)) / denominator;
    const margin = z * Math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator;
    return [Math.max(0, center - margin), Math.min(1, center + margin)];
  }

  function difficultyCalibration(profile) {
    const targets = { easy: [0.75, 0.90], medium: [0.50, 0.70], hard: [0.30, 0.50] };
    return Object.fromEntries(DIFFICULTIES.map((difficulty) => {
      const records = (profile?.battleHistory || []).filter((record) => record.difficulty === difficulty);
      const wins = records.filter((record) => record.won).length;
      const episodes = records.length;
      const winRate = episodes ? wins / episodes : 0;
      const ci95 = wilsonInterval(wins, episodes);
      const [minimum, maximum] = targets[difficulty];
      const status = episodes < 20 ? "insufficient-data"
        : winRate < minimum ? "too-hard"
          : winRate > maximum ? "too-easy" : "in-range";
      const meanTurnUsage = episodes ? records.reduce((sum, record) =>
        sum + Number(record.turns || 0) / Math.max(1, Number(record.turn_limit || 1)), 0) / episodes : 0;
      return [difficulty, { episodes, wins, winRate, ci95, target: [minimum, maximum], meanTurnUsage, status }];
    }));
  }

  function difficultyRiskBand(score, objectiveType = "defeat") {
    if (objectiveType === "narrative") return "narrative";
    if (score < 30) return "low";
    if (score < 50) return "guarded";
    if (score < 70) return "high";
    return "severe";
  }

  function stageDifficultyAssessment(stageProfile, profile, difficulty = "medium") {
    const source = stageProfile || {};
    const objectiveType = String(source.objectiveType || "defeat");
    const stageId = String(source.id || source.stage_id || "");
    const stageIndex = Number(source.index || source.stage_index || 1);
    const recommendedLevel = Number(source.recommendedLevel || recommendedStageLevel(stageIndex));
    const armyRank = clamp(Number(profile?.armyRank || 1), 1, PROGRESSION.maxLevel);
    const levelDelta = armyRank - recommendedLevel;
    const preset = difficultyPreset(difficulty);
    const equipment = equipmentBonuses(profile);
    const equipmentMitigation = clamp(
      equipment.power * 0.35 + equipment.defense * 0.3 + equipment.move * 2 + equipment.maxMp * 0.12,
      0, 10
    );
    const recent = (profile?.battleHistory || [])
      .filter((record) => !record.procedural && record.difficulty === preset.id)
      .slice(-12);
    const recentReward = recent.length
      ? recent.reduce((sum, record) => sum + clamp(Number(record.reward_total || 0), 0, 1), 0) / recent.length
      : null;
    const formAdjustment = recentReward == null ? 0 : clamp((0.55 - recentReward) * 18, -6, 6);
    const staticRisk = objectiveType === "narrative" ? 0 : clamp(Number(source.structuralRisk || 35), 0, 100);
    const coldStartRisk = objectiveType === "narrative" ? 0 : clamp(
      staticRisk + preset.structuralRiskOffset - levelDelta * 6 - equipmentMitigation + formAdjustment,
      0, 100
    );
    const matching = (profile?.battleHistory || []).filter((record) =>
      String(record.stage_id || "") === stageId && record.difficulty === preset.id);
    const wins = matching.filter((record) => record.won).length;
    const episodes = matching.length;
    const observedSuccessRate = episodes ? (wins + 1) / (episodes + 2) : null;
    const observedRisk = observedSuccessRate == null ? null : (1 - observedSuccessRate) * 100;
    const evidenceWeight = episodes ? Math.min(0.7, episodes / 20 * 0.7) : 0;
    const riskScore = observedRisk == null
      ? coldStartRisk
      : clamp(coldStartRisk * (1 - evidenceWeight) + observedRisk * evidenceWeight, 0, 100);
    const ci95 = episodes ? wilsonInterval(wins, episodes) : [0, 1];
    const confidence = episodes >= 20 ? "calibrated" : episodes >= 5 ? "limited" : "cold-start";
    return {
      stageId,
      stageIndex,
      difficulty: preset.id,
      objectiveType,
      recommendedLevel,
      armyRank,
      levelDelta,
      staticRisk,
      coldStartRisk,
      riskScore: Number(riskScore.toFixed(1)),
      riskBand: difficultyRiskBand(riskScore, objectiveType),
      confidence,
      evidence: { episodes, wins, observedSuccessRate, ci95, recentEpisodes: recent.length, recentReward },
      adjustments: {
        difficulty: preset.structuralRiskOffset,
        level: -levelDelta * 6,
        equipment: Number((-equipmentMitigation).toFixed(1)),
        recentForm: Number(formAdjustment.toFixed(1)),
        observedWeight: Number(evidenceWeight.toFixed(3))
      },
      flags: Array.isArray(source.flags) ? [...source.flags] : []
    };
  }

  function completeBattle(rawProfile, stage, outcome) {
    const profile = normalizeProfile(rawProfile, outcome.stages || []);
    const startingArmyRank = profile.armyRank;
    const reward = battleReward(outcome);
    const firstClear = Boolean(outcome.won && !stage.isProcedural && !profile.completed.includes(stage.id));
    let rankUps = 0;
    let coinsEarned = 0;
    if (firstClear) {
      const previousRank = profile.armyRank;
      profile.completed.push(stage.id);
      profile.lastStage = stage.id;
      const clearRank = armyRankForClears(profile.completed.length);
      profile.armyRank = Math.max(profile.armyRank, clearRank);
      rankUps = Math.max(0, profile.armyRank - previousRank);
      profile.armyXp = armyXpForClears(profile.completed.length, profile.armyRank);
      const rawMoney = Number(stage?.stage?.rewards?.money || 10000);
      const difficultyMultiplier = difficultyPreset(outcome.difficulty).rewardMultiplier * (outcome.assistActive ? 0.9 : 1);
      coinsEarned = Math.round(clamp(rawMoney / 100, 80, 300) * difficultyMultiplier);
      profile.coins += coinsEarned;
      if (Number(stage.index || 0) <= 12 && Number(stage.index || 0) % 3 === 0) profile.inventory.spirit_powder += 1;
      else profile.inventory.medicine += 1;
    }
    if (outcome.inventoryRemaining) {
      profile.inventory.medicine = Math.max(0, Number(outcome.inventoryRemaining.medicine || 0));
      profile.inventory.spirit_powder = Math.max(0, Number(outcome.inventoryRemaining.spirit_powder || 0));
      if (firstClear) {
        if (Number(stage.index || 0) <= 12 && Number(stage.index || 0) % 3 === 0) profile.inventory.spirit_powder += 1;
        else profile.inventory.medicine += 1;
      }
    }
    const masteryUpdates = [];
    const masteryAward = firstClear
      ? PROGRESSION.firstClearHeroXp
      : stage.isProcedural
        ? (outcome.won ? PROGRESSION.proceduralWinHeroXp : PROGRESSION.proceduralLossHeroXp)
        : (outcome.won ? PROGRESSION.replayWinHeroXp : PROGRESSION.replayLossHeroXp);
    for (const heroId of [...new Set(outcome.ownHeroes || [])]) {
      const key = canonicalHeroId(heroId);
      const current = profile.heroMastery[key] || { xp: 0, level: 1 };
      const before = current.level;
      const beforeXp = current.xp;
      const cap = heroLevelCap(profile.armyRank);
      current.xp = Math.min(current.xp + masteryAward, maxHeroXpForCap(cap));
      current.level = heroLevelFromXp(current.xp, cap);
      profile.heroMastery[key] = current;
      masteryUpdates.push({ heroId: key, level: current.level, xp: current.xp, xpEarned: current.xp - beforeXp, cap, leveled: current.level > before });
    }
    for (const heroId of Object.keys(profile.woundedHeroes)) {
      profile.woundedHeroes[heroId] -= 1;
      if (profile.woundedHeroes[heroId] <= 0) delete profile.woundedHeroes[heroId];
    }
    for (const heroId of [...new Set(outcome.ownDefeatedHeroes || [])]) profile.woundedHeroes[canonicalHeroId(heroId)] = 2;
    if (outcome.won) profile.stageFailures[String(stage.id)] = 0;
    else profile.stageFailures[String(stage.id)] = clamp(Number(profile.stageFailures[String(stage.id)] || 0) + 1, 0, 99);
    const resourcesBefore = { ...profile.campaignResources };
    const provisionCost = Math.ceil(Math.max(1, Number(outcome.totalOwn || 1)) * 1.5 + Math.max(1, Number(outcome.turns || 1)) * 0.35);
    const provisionGain = Number(outcome.supplies || 0) * 6 + (outcome.won ? 4 : 0);
    profile.campaignResources.provisions = clamp(profile.campaignResources.provisions - provisionCost + provisionGain, 0, 200);
    const lossRatio = Number(outcome.ownLosses || 0) / Math.max(1, Number(outcome.totalOwn || 1));
    const moraleDelta = (outcome.won ? 8 : -12) - Math.round(lossRatio * 8);
    profile.campaignResources.morale = clamp(profile.campaignResources.morale + moraleDelta, 0, 100);
    const decision = outcome.decision || null;
    const record = {
      schema_version: TELEMETRY_SCHEMA,
      policy_version: decision?.policyVersion || POLICY_VERSION,
      runtime_version: RUNTIME_VERSION,
      timestamp: Number(outcome.timestamp || Date.now()),
      stage_id: stage.id,
      stage_index: Number(stage.index || 0),
      recommended_level: recommendedStageLevel(stage.index),
      army_rank: startingArmyRank,
      level_delta: startingArmyRank - recommendedStageLevel(stage.index),
      procedural: Boolean(stage.isProcedural),
      difficulty: outcome.difficulty || profile.settings.battleDifficulty,
      difficulty_parameters: {
        ...difficultyPreset(outcome.difficulty || profile.settings.battleDifficulty),
        effectiveTurnLimit: Number(outcome.turnLimit || 0)
      },
      action: decision?.action || null,
      behavior_probability: Number.isFinite(decision?.behaviorProbability) ? decision.behaviorProbability : null,
      fallback_reason: decision?.fallbackReason || null,
      won: Boolean(outcome.won),
      turns: Number(outcome.turns || 0),
      turn_limit: Number(outcome.turnLimit || 0),
      own_losses: Number(outcome.ownLosses || 0),
      total_own: Number(outcome.totalOwn || 0),
      total_enemy: Number(outcome.totalEnemy || 0),
      reward_components: reward.components,
      reward_total: reward.total,
      policy_decisions: Number(outcome.policyDecisions || 0),
      policy_fallbacks: Number(outcome.policyFallbacks || 0),
      terminal_reason: outcome.terminalReason || (outcome.won ? "victory" : "defeat")
      , duration_ms: Math.max(0, Number(outcome.durationMs || 0))
      , story_skipped: Boolean(outcome.storySkipped)
      , items_used: { ...(outcome.itemsUsed || {}) }
      , event_counts: { ...(outcome.eventCounts || {}) }
      , map_seed: Number.isFinite(Number(outcome.mapSeed)) ? Number(outcome.mapSeed) : null
      , objective_type: outcome.objectiveType || "scripted"
      , coins_earned: coinsEarned
      , preflight_assessment: outcome.difficultyAssessment || null
      , formation: profile.formation
      , vanguard: profile.stageVanguards?.[String(stage.id)] || null
      , assist_active: Boolean(outcome.assistActive)
      , campaign_resources_before: resourcesBefore
      , campaign_resources_after: { ...profile.campaignResources }
      , provision_cost: provisionCost
      , morale_delta: moraleDelta
      , wounded_heroes: [...new Set(outcome.ownDefeatedHeroes || [])].map(canonicalHeroId)
    };
    if (profile.settings.telemetryEnabled) profile.battleHistory = [...profile.battleHistory, record].slice(-200);
    if (profile.settings.telemetryEnabled && outcome.replay) {
      profile.replays = [...profile.replays, { ...outcome.replay, schema_version: REPLAY_SCHEMA, summary: record }].slice(-20);
    }
    if (stage.isProcedural && outcome.difficulty && profile.difficultyBandit.enabled) {
      profile.difficultyBandit = updateBandit(profile.difficultyBandit, outcome.difficulty, reward.total);
    }
    profile.unlockedThrough = unlockedThrough(profile, outcome.stages || []);
    return { profile, record, reward, firstClear, rankUps, coinsEarned, masteryUpdates };
  }

  function canonicalHeroId(heroId) {
    return String(heroId || "").replace(/\d+[a-z]?$/i, "") || String(heroId || "unknown");
  }

  function skillForUnit(unit) {
    const base = unit ? SKILLS[unit.classId] || null : null;
    if (!base) return null;
    const rank = clamp(Number(unit.skillRank || heroSkillRank(unit.level)), 1, 3);
    const scalar = 1 + (rank - 1) * 0.18;
    return {
      ...base,
      rank,
      name: `${base.name}${rank > 1 ? `·${["", "精", "极"][rank - 1]}` : ""}`,
      cost: Math.max(1, base.cost - (rank >= 3 ? 1 : 0)),
      amount: base.amount ? Math.round(base.amount * scalar) : base.amount,
      power: base.power ? Math.round(base.power * scalar) : base.power,
      defense: base.defense ? Math.round(base.defense * scalar) : base.defense
    };
  }

  function sameSide(left, right) {
    return left.team === right.team || (left.team !== "enemy" && right.team !== "enemy");
  }

  function skillTargetValid(actor, target, skill) {
    if (!actor || !target || !skill || actor.hp <= 0 || target.hp <= 0) return false;
    const distance = Math.abs(actor.x - target.x) + Math.abs(actor.y - target.y);
    if (distance > skill.range) return false;
    if (skill.target === "self") return actor.id === target.id;
    if (skill.target === "ally") return sameSide(actor, target);
    if (skill.target === "enemy") return !sameSide(actor, target) && !target.invulnerable;
    return false;
  }

  function effectivePower(unit) {
    return Number(unit?.power || 0) + (unit?.effects || []).reduce((sum, effect) => sum + Number(effect.power || 0), 0);
  }

  function effectiveDefense(unit) {
    return Number(unit?.defense || 0) + (unit?.effects || []).reduce((sum, effect) => sum + Number(effect.defense || 0), 0);
  }

  function applySkill(actor, target, skill) {
    if (!skillTargetValid(actor, target, skill)) return { ok: false, reason: "invalid-target" };
    if (Number(actor.mp || 0) < skill.cost) return { ok: false, reason: "insufficient-mp" };
    actor.mp -= skill.cost;
    if (skill.kind === "damage") {
      const damage = Math.max(10, Math.round(skill.amount + actor.level * 1.2 - effectiveDefense(target) * 0.18));
      target.hp = Math.max(0, target.hp - damage);
      return { ok: true, kind: "damage", amount: damage, defeated: target.hp <= 0 };
    }
    if (skill.kind === "heal") {
      const before = target.hp;
      target.hp = Math.min(target.maxHp, target.hp + skill.amount + actor.level);
      return { ok: true, kind: "heal", amount: target.hp - before };
    }
    target.effects ||= [];
    target.effects = target.effects.filter((effect) => effect.id !== skill.id);
    target.effects.push({ id: skill.id, name: skill.name, power: skill.power || 0, defense: skill.defense || 0, turns: skill.turns || 1 });
    return { ok: true, kind: "buff", amount: (skill.power || 0) + (skill.defense || 0), turns: skill.turns || 1 };
  }

  function tickEffects(unit) {
    unit.effects = (unit.effects || []).map((effect) => ({ ...effect, turns: Number(effect.turns || 0) - 1 })).filter((effect) => effect.turns > 0);
    return unit.effects;
  }

  function storyEventMatches(event, context) {
    if (!event?.runtime) return false;
    const units = Array.isArray(context?.units) ? context.units : [];
    const alive = (unit) => Number(unit?.hp || 0) > 0;
    const matchingUnits = (heroId) => units.filter((unit) => unit.heroId === heroId);
    switch (event.trigger) {
      case "turn":
        return Number(context?.turn || 0) >= Number(event.turn || 1);
      case "unit_defeated": {
        const targets = matchingUnits(event.unit);
        return targets.length > 0 && targets.every((unit) => !alive(unit));
      }
      case "unit_hp_below": {
        const threshold = Math.max(0, Math.min(1, Number(event.hp_percent ?? 0.5)));
        return matchingUnits(event.unit).some((unit) => alive(unit) && Number(unit.hp) / Math.max(1, Number(unit.maxHp || 1)) <= threshold);
      }
      case "enemy_remaining":
        return units.filter((unit) => unit.team === "enemy" && alive(unit)).length <= Number(event.count || 0);
      case "site_claimed":
        return (context?.claimedSites || []).includes(event.site);
      default:
        return false;
    }
  }

  function splitStoryText(text, maxLength) {
    const limit = Math.max(60, Number(maxLength || 110));
    const clean = String(text || "").replace(/\s+/g, " ").trim();
    if (!clean || clean.length <= limit) return clean ? [clean] : [];
    const sentences = clean.match(/[^。！？；]+[。！？；]?/g) || [clean];
    const chunks = [];
    let current = "";
    for (const sentence of sentences) {
      if (current && current.length + sentence.length > limit) { chunks.push(current); current = ""; }
      if (sentence.length > limit) {
        if (current) { chunks.push(current); current = ""; }
        for (let index = 0; index < sentence.length; index += limit) chunks.push(sentence.slice(index, index + limit));
      } else current += sentence;
    }
    if (current) chunks.push(current);
    return chunks;
  }

  function normalizeStoryEntries(entries, maxLength, storyContext = {}) {
    const output = [];
    const seen = new Set();
    const sourceEntries = Array.isArray(entries) ? entries : Object.values(entries || {});
    for (const [fallbackSourceIndex, raw] of sourceEntries.entries()) {
      const speaker = String(raw?.speaker || "").trim() === "原著" ? "史官" : String(raw?.speaker || "旁白").trim() || "旁白";
      const stageId = String(raw?.stageId ?? storyContext?.stageId ?? "");
      const section = String(raw?.section ?? storyContext?.section ?? "");
      const sourceIndex = Number.isInteger(Number(raw?.sourceIndex)) ? Number(raw.sourceIndex) : fallbackSourceIndex;
      for (const [chunkIndex, text] of splitStoryText(raw?.text, maxLength).entries()) {
        const occurrenceKey = `${stageId}\u0000${section}\u0000${sourceIndex}\u0000${chunkIndex}\u0000${speaker}\u0000${text}`;
        const key = stageId || section ? occurrenceKey : `${speaker}\u0000${text}`;
        if (seen.has(key)) continue;
        seen.add(key);
        output.push({ ...raw, speaker, text, stageId, section, sourceIndex, chunkIndex });
      }
    }
    return output;
  }

  function portraitForSpeaker(speaker) {
    const name = String(speaker || "旁白");
    if (/旁白|史官|军令|军报/.test(name)) return "portrait-strategist.png";
    if (/王|公|侯|君|主|帝|后|太子/.test(name)) return "portrait-lord.png";
    let hash = 0;
    for (let index = 0; index < name.length; index++) hash = ((hash * 31) + name.charCodeAt(index)) >>> 0;
    return ["portrait-general.png", "portrait-lord.png", "portrait-strategist.png"][hash % 3];
  }

  function normalizeVoiceManifest(raw) {
    const source = raw && typeof raw === "object" ? raw : {};
    const entries = (Array.isArray(source.entries) ? source.entries : []).filter((entry) => {
      const file = String(entry?.file || "");
      return entry?.speaker && entry?.text && file.startsWith("audio/") && !file.includes("..") && !file.includes(":");
    }).map((entry) => {
      const firstOccurrence = entry?.firstOccurrence && typeof entry.firstOccurrence === "object" ? entry.firstOccurrence : {};
      const occurrences = (Array.isArray(entry?.occurrences) ? entry.occurrences : []).filter((item) => item && typeof item === "object").map((item) => ({
        contextId: String(item.contextId || ""),
        stageId: String(item.stageId ?? ""),
        section: String(item.section ?? ""),
        sourceIndex: Number(item.sourceIndex ?? -1),
        chunkIndex: Number(item.chunkIndex ?? -1)
      }));
      return {
        id: String(entry.id || ""),
        speaker: String(entry.speaker),
        text: String(entry.text),
        file: String(entry.file),
        duration: Math.max(0, Number(entry.duration || 0)),
        voice: String(entry.voice || ""),
        sha256: /^[a-f0-9]{64}$/i.test(String(entry.sha256 || "")) ? String(entry.sha256).toLowerCase() : "",
        contextId: String(entry.contextId || ""),
        stageId: String(entry.stageId ?? firstOccurrence.stageId ?? ""),
        section: String(entry.section ?? firstOccurrence.section ?? ""),
        sourceIndex: Number(entry.sourceIndex ?? firstOccurrence.sourceIndex ?? -1),
        chunkIndex: Number(entry.chunkIndex ?? firstOccurrence.chunkIndex ?? -1),
        timelineIndex: Number(entry.timelineIndex ?? firstOccurrence.timelineIndex ?? -1),
        styleAnchor: String(entry.styleAnchor || entry.delivery?.styleAnchor || ""),
        occurrences
      };
    });
    const lookup = new Map();
    const contextLookup = new Map();
    const occurrenceLookup = new Map();
    const textLookup = new Map();
    const occurrenceKey = (entry, selector) => [
      selector.stageId, selector.section, selector.sourceIndex, selector.chunkIndex, entry.speaker, entry.text
    ].join("\u0000");
    for (const entry of entries) {
      const baseKey = `${entry.speaker}\u0000${entry.text}`;
      if (!lookup.has(baseKey)) lookup.set(baseKey, entry);
      if (!textLookup.has(entry.text)) textLookup.set(entry.text, entry);
      else if (textLookup.get(entry.text)?.id !== entry.id) textLookup.set(entry.text, null);
      if (entry.contextId) contextLookup.set(entry.contextId, entry);
      if (entry.stageId && entry.section && entry.sourceIndex >= 0 && entry.chunkIndex >= 0) {
        occurrenceLookup.set(occurrenceKey(entry, entry), entry);
      }
      for (const occurrence of entry.occurrences) {
        if (occurrence.contextId) contextLookup.set(occurrence.contextId, entry);
        if (occurrence.stageId && occurrence.section && occurrence.sourceIndex >= 0 && occurrence.chunkIndex >= 0) {
          occurrenceLookup.set(occurrenceKey(entry, occurrence), entry);
        }
      }
    }
    for (const [text, entry] of textLookup) if (!entry) textLookup.delete(text);
    return { schemaVersion: Number(source.schemaVersion || 1), model: String(source.model || ""), entries, lookup, textLookup, contextLookup, occurrenceLookup };
  }

  function resolveStoryVoice(manifest, speaker, text, context = {}) {
    const wantedSpeaker = String(speaker || "旁白").trim() || "旁白";
    const wantedText = String(text || "").trim();
    const contextId = String(context?.contextId || context?.id || "");
    if (contextId && manifest?.contextLookup?.has(contextId)) return manifest.contextLookup.get(contextId);
    const stageId = String(context?.stageId ?? "");
    const section = String(context?.section ?? "");
    const sourceIndex = Number(context?.sourceIndex ?? -1);
    const chunkIndex = Number(context?.chunkIndex ?? -1);
    if (stageId && section && sourceIndex >= 0 && chunkIndex >= 0) {
      const occurrenceKey = [stageId, section, sourceIndex, chunkIndex, wantedSpeaker, wantedText].join("\u0000");
      const exact = manifest?.occurrenceLookup?.get(occurrenceKey);
      if (exact) return exact;
    }
    const key = `${wantedSpeaker}\u0000${wantedText}`;
    return manifest?.lookup?.get(key)
      || (manifest?.entries || []).find((entry) => entry.speaker === wantedSpeaker && entry.text === wantedText)
      || manifest?.textLookup?.get(wantedText)
      || null;
  }

  function normalizeMusicManifest(raw) {
    const source = raw && typeof raw === "object" ? raw : {};
    const cues = (Array.isArray(source.cues) ? source.cues : []).filter((cue) => {
      const file = String(cue?.file || "");
      return cue?.id && cue?.stageId && file.startsWith("audio/") && !file.includes("..") && !file.includes(":");
    }).map((cue) => ({
      id: String(cue.id), stageId: String(cue.stageId), kind: String(cue.kind || ""),
      section: String(cue.section || ""), eventId: String(cue.eventId || ""), triggerText: String(cue.triggerText || ""), file: String(cue.file),
      loop: Boolean(cue.loop), duration: Math.max(0, Number(cue.duration || cue.durationTarget || 0)),
      sha256: /^[a-f0-9]{64}$/i.test(String(cue.sha256 || "")) ? String(cue.sha256).toLowerCase() : "",
      tempo: Math.max(0, Number(cue.tempo || 0)), mood: String(cue.mood || ""),
      era: String(cue.era || ""), scene: String(cue.scene || ""),
      fallbackFile: String(cue.fallbackFile || cue.file),
      fallbackSha256: /^[a-f0-9]{64}$/i.test(String(cue.fallbackSha256 || "")) ? String(cue.fallbackSha256).toLowerCase() : "",
      availableInBase: cue.availableInBase !== false, packId: String(cue.packId || "")
    }));
    const lookup = new Map();
    const textLookup = new Map();
    for (const cue of cues) {
      lookup.set([cue.stageId, cue.kind, cue.section, cue.eventId].join("\u0000"), cue);
      if (!cue.eventId) lookup.set([cue.stageId, cue.kind, cue.section, ""].join("\u0000"), cue);
      if (cue.kind === "event" && cue.triggerText) {
        const textKey = `${cue.stageId}\u0000${cue.triggerText}`;
        if (!textLookup.has(textKey)) textLookup.set(textKey, cue);
      }
    }
    return { schemaVersion: Number(source.schemaVersion || 1), generator: String(source.generator || ""), cues, lookup, textLookup };
  }

  function resolveContextMusic(manifest, context = {}) {
    const stageId = String(context.stageId || "");
    const section = String(context.section || "");
    const eventId = String(context.eventId || "");
    const text = String(context.text || "").trim();
    const kind = String(context.kind || (["events", "runtime"].includes(section) ? "event" : section || "battle"));
    const exact = manifest?.lookup?.get([stageId, kind, section || kind, eventId].join("\u0000"));
    if (exact) return exact;
    if (kind === "event" && text) {
      const byText = manifest?.textLookup?.get(`${stageId}\u0000${text}`);
      if (byText) return byText;
    }
    if (kind === "event") {
      const eventFallback = (manifest?.cues || []).find((cue) => cue.stageId === stageId && cue.kind === "event");
      if (eventFallback) return eventFallback;
    }
    const sectionFallback = manifest?.lookup?.get([stageId, kind, section || kind, ""].join("\u0000"));
    if (sectionFallback) return sectionFallback;
    return manifest?.lookup?.get([stageId, "battle", "battle", ""].join("\u0000")) || null;
  }

  return {
    PROFILE_VERSION, TELEMETRY_SCHEMA, REPLAY_SCHEMA, POLICY_VERSION, RUNTIME_VERSION, DIFFICULTIES, DIFFICULTY_PRESETS, MAP_DETAIL_MODES, FORMATION_PRESETS, SKILLS, EQUIPMENT, EQUIPMENT_SLOTS, PROGRESSION,
    normalizeProfile, normalizeKnowledgeQuiz, recordKnowledgeQuizResult, unlockedThrough, isStageUnlocked, recommendedStageLevel, effectiveUnitLevel, effectiveHeroLevel, masteryForHero,
    armyRankForClears, armyXpForClears, heroLevelCap, heroLevelFromXp, unitGrowthBonuses, formationModifiers, heroSkillRank, retryAssist, restArmy, missionContract, dailyChallenge,
    difficultyPreset, effectiveTurnLimit, unitDifficultyModifiers,
    equipmentBonuses, availableEquipment, buyEquipment, equipItem, buySupply,
    battleReward, selectDifficulty, wilsonInterval, difficultyCalibration, difficultyRiskBand, stageDifficultyAssessment, completeBattle, canonicalHeroId,
    skillForUnit, skillTargetValid, effectivePower, effectiveDefense, applySkill, tickEffects, storyEventMatches,
    splitStoryText, normalizeStoryEntries, portraitForSpeaker, normalizeVoiceManifest, resolveStoryVoice, normalizeMusicManifest, resolveContextMusic,
    mapDetailProfile, isStructuralTerrain, preservesMapDetail, isBarrierTerrain
  };
});
