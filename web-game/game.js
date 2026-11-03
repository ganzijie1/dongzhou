(() => {
  "use strict";

  const PROFILE_KEY = "dongzhou-h5-profile-v2";
  const BATTLE_KEY = "dongzhou-h5-battle-v2";
  const systems = window.DongzhouGameSystems;
  const $ = (selector) => document.querySelector(selector);
  const asList = (value) => Array.isArray(value) ? value : Object.keys(value || {}).sort((a, b) => Number(a) - Number(b)).map((key) => value[key]);
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const pointKey = (x, y) => `${x},${y}`;

  const KNOWN_NAMES = {
    DuBo: "杜伯", ZuoRu: "左儒", ZhouXuanWang: "周宣王", YinJiFu: "尹吉甫", ZhaoHu: "召虎",
    RoyalGuard: "王城卫士", ZhouYouWang: "周幽王", ZhengHuanGong: "郑桓公", ZhengZhuangGong: "郑庄公",
    ShenHou: "申侯", QuanRongLord: "犬戎主将", QuanRongWarrior: "犬戎武士", QuanRongArcher: "犬戎弓手",
    JinLiGong58: "晋厉公", LuanShu58: "栾书", ShiXie58: "士燮", HanJue48: "韩厥", XiQi58: "郤锜",
    XiZhi58: "郤至", XunYing54: "荀罃", QinHuanGongMasui: "秦桓公", ChengChaMasui: "成差",
    NvFuMasui: "不更女父", QinMasuiGuard: "秦军卫士", QinMasuiArcher: "秦军弓手"
    , KuangZhang91: "匡章", GongSunXiChuisha: "公孙喜", BaoYuanChuisha: "暴鸢", TangMieChuisha: "唐蔑"
    , QiHanWeiGuard: "联军甲士", QiHanWeiArcher: "联军弓手", ChuishaGuard: "楚军甲士", ChuishaArcher: "楚军弓手"
  };
  const CLASS_LABELS = { Lord: "君主", King: "王者", Infantry: "步兵", Cavalry: "骑兵", Archer: "弓兵", Strategist: "军师", Support: "辅臣" };
  const UNIT_IMAGES = {
    Lord: "unit-lord.png", King: "unit-lord.png", Infantry: "unit-chariot.png", Cavalry: "unit-cavalry.png",
    Archer: "unit-archer.png", Strategist: "unit-strategist.png", Support: "unit-strategist.png"
  };
  const TEAM_LABELS = { own: "我军", ally: "友军", enemy: "敌军" };

  let campaign;
  let config;
  let pcgrlTemplate;
  let mapElitesTemplate;
  let mapElitesArchive;
  let voiceManifest = { entries: [] };
  let runtime;
  let profile = readJson(PROFILE_KEY, { completed: [], lastStage: null });
  let stageRecord = null;
  let state = null;
  let heroById = new Map();
  let classById = new Map();
  let terrainByChar = new Map();
  let selectedId = null;
  let selectedSkillId = null;
  let inspectionId = null;
  let reachable = new Map();
  let mapImage = new Image();
  let mapPresentationCanvas = null;
  let mapPresentationKey = "";
  let mapZoom = 1;
  let cellPixels = 48;
  let renderQueued = false;
  let enemyRunning = false;
  let restoring = false;
  let runtimeTurnOverride = null;
  let noticeTimer = null;
  let storyEntries = [];
  let storyIndex = 0;
  let storyDone = null;
  let dragStart = null;
  let dragged = false;
  let unitSerial = 0;
  let boardCursor = null;
  let audioContext = null;
  let storyAudio = null;
  let storyAudioSerial = 0;
  const imageCache = new Map();

  const canvas = $("#battleCanvas");
  const ctx = canvas.getContext("2d");

  function readJson(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch (_) { return fallback; }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function displayName(id) {
    if (KNOWN_NAMES[id]) return KNOWN_NAMES[id];
    const base = String(id).replace(/\d+[a-z]?$/i, "").replace(/([a-z])([A-Z])/g, "$1 $2");
    return base || String(id);
  }

  function mapPath(record) {
    return `assets/maps/${record.mapAsset.replace(/\.[^.]+$/, "")}.webp`;
  }

  function getImage(name) {
    if (!imageCache.has(name)) {
      const image = new Image();
      image.src = `assets/${name}`;
      image.addEventListener("load", requestRender);
      imageCache.set(name, image);
    }
    return imageCache.get(name);
  }

  async function boot() {
    try {
      setLoading(12, "正在校验列国谱系");
      [campaign, config, pcgrlTemplate, mapElitesTemplate, mapElitesArchive, voiceManifest] = await Promise.all([
        fetch("scenario/campaign.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/config.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/pcgrl-masui.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/map-elites-chuisha.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/map-elites-chuisha.archive.json").then(checkResponse).then((response) => response.json()),
        fetch("audio/dialogue-manifest.json").then(checkResponse).then((response) => response.json())
          .catch(() => ({ schemaVersion: 1, entries: [] }))
      ]);
      voiceManifest = systems.normalizeVoiceManifest(voiceManifest);
      setLoading(54, "正在装载战役规则");
      heroById = new Map(asList(config.heroes).map((hero) => [hero.id, hero]));
      classById = new Map(asList(config.unit_classes).map((entry) => [entry.id, entry]));
      terrainByChar = new Map(asList(config.terrains).map((entry, index) => [entry.char, index]));
      profile = systems.normalizeProfile(profile, campaign.stages);
      writeJson(PROFILE_KEY, profile);
      runtime = new DongzhouLuaRuntime(campaign);
      await runtime.init();
      attachEvents();
      configureMobilePanels();
      buildRangeOptions();
      syncCampaignSettings();
      renderCampaign();
      setLoading(100, `${campaign.stageCount} 场战役就绪`);
      await sleep(180);
      $("#loadingScreen").hidden = true;
      $("#app").hidden = false;
      openCampaign();
    } catch (error) {
      console.error(error);
      $("#loadingText").textContent = `载入失败：${error.message}`;
      $("#loadingScreen").classList.add("failed");
    }
  }

  function checkResponse(response) {
    if (!response.ok) throw new Error(`${response.url} (${response.status})`);
    return response;
  }

  function setLoading(percent, text) {
    $("#loadingBar").style.width = `${percent}%`;
    $("#loadingText").textContent = text;
  }

  function buildRangeOptions() {
    const select = $("#stageRange");
    const groups = [{ value: "all", label: "全部战役" }];
    for (let start = 1; start <= campaign.stageCount; start += 25) {
      groups.push({ value: `${start}-${Math.min(start + 24, campaign.stageCount)}`, label: `第 ${start} - ${Math.min(start + 24, campaign.stageCount)} 战` });
    }
    select.innerHTML = groups.map((item) => `<option value="${item.value}">${item.label}</option>`).join("");
  }

  function renderCampaign() {
    profile = systems.normalizeProfile(profile, campaign.stages);
    const query = $("#stageSearch").value.trim().toLowerCase();
    const range = $("#stageRange").value || "all";
    const [start, end] = range === "all" ? [1, campaign.stageCount] : range.split("-").map(Number);
    const completed = new Set(profile.completed || []);
    const stages = campaign.stages.filter((record) => {
      if (record.index < start || record.index > end) return false;
      if (!query) return true;
      return [record.id, record.chapter, record.title, record.battleTitle, record.objective].join(" ").toLowerCase().includes(query);
    });
    $("#stageGrid").innerHTML = stages.map((record) => {
      const unlocked = systems.isStageUnlocked(record, profile, campaign.stages);
      const recommendedLevel = systems.recommendedStageLevel(record.index);
      const underleveled = profile.armyRank < recommendedLevel;
      const turnLimit = systems.effectiveTurnLimit(record.turnLimit, profile.settings.battleDifficulty);
      return `
      <button class="stage-card ${completed.has(record.id) ? "completed" : ""} ${unlocked ? "" : "locked"} ${underleveled ? "underleveled" : ""}" ${unlocked ? `data-stage-id="${record.id}"` : "disabled"} type="button">
        <span class="stage-thumb"><img loading="lazy" src="${mapPath(record)}" alt=""><i>${completed.has(record.id) ? "已克" : unlocked ? String(record.index).padStart(3, "0") : "未解锁"}</i></span>
        <span class="stage-copy"><small>${escapeHtml(record.chapter)} · ${turnLimit} 回合 · 建议 ${recommendedLevel} 级</small><strong>${escapeHtml(record.battleTitle)}</strong><span>${escapeHtml(record.title)}</span><em>${escapeHtml(record.objective)}</em></span>
      </button>`;
    }).join("") || '<div class="empty-search">没有符合条件的战役</div>';
    document.querySelectorAll("[data-stage-id]").forEach((button) => button.addEventListener("click", () => startStage(button.dataset.stageId)));
    const completedCount = completed.size;
    $("#progressText").textContent = `已完成 ${completedCount} / ${campaign.stageCount}`;
    $("#progressBar").style.width = `${completedCount / campaign.stageCount * 100}%`;
    $("#armyRankLabel").textContent = `军阶 ${profile.armyRank} · ${profile.armyXp}/${systems.PROGRESSION.armyXpPerLevel}`;
    const saved = readBattleSave();
    $("#resumeButton").hidden = !saved;
    renderCampaignFocus(saved, completed);
    renderQuartermaster();
    $("#campaignStats").textContent = `${campaign.stageCount} 关 · ${new Set(campaign.stages.map((item) => item.mapAsset)).size} 幅舆图`;
  }

  function renderQuartermaster() {
    $("#coinCount").textContent = profile.coins;
    $("#campaignMedicineCount").textContent = profile.inventory.medicine;
    $("#campaignSpiritCount").textContent = profile.inventory.spirit_powder;
    const bonuses = systems.equipmentBonuses(profile);
    $("#equipmentBonuses").textContent = `当前加成：攻击 +${bonuses.power} · 防御 +${bonuses.defense} · 移动 +${bonuses.move} · 谋略上限 +${bonuses.maxMp}`;
    const available = new Set(systems.availableEquipment(profile).map((item) => item.id));
    $("#equipmentList").innerHTML = Object.values(systems.EQUIPMENT).map((item) => {
      const owned = profile.ownedEquipment.includes(item.id);
      const equipped = profile.equipped[item.slot] === item.id;
      const stats = [["power", "攻"], ["defense", "防"], ["move", "移"], ["maxMp", "谋"]].filter(([key]) => item[key]).map(([key, label]) => `${label}+${item[key]}`).join(" · ");
      const action = equipped ? "已装备" : owned ? "装备" : available.has(item.id) ? `${item.cost} 钱` : `通关 ${item.unlockStage} 解锁`;
      return `<button class="equipment-item ${equipped ? "equipped" : ""}" type="button" ${available.has(item.id) || owned ? `data-equipment-id="${item.id}"` : "disabled"}>
        <span><strong>${item.name}</strong><small>${stats}</small></span><em>${action}</em></button>`;
    }).join("");
    document.querySelectorAll("[data-equipment-id]").forEach((button) => button.addEventListener("click", () => handleEquipment(button.dataset.equipmentId)));
  }

  function handleEquipment(itemId) {
    const alreadyOwned = profile.ownedEquipment.includes(itemId);
    const result = alreadyOwned ? systems.equipItem(profile, itemId) : systems.buyEquipment(profile, itemId);
    if (!result.ok) { showNotice(result.reason === "insufficient-coins" ? "铜钱不足" : "尚未解锁"); return; }
    profile = result.profile;
    writeJson(PROFILE_KEY, profile);
    renderCampaign();
    showNotice(alreadyOwned ? `${result.item.name}已装备` : `${result.item.name}已购入并装备`);
  }

  function handleSupplyPurchase(itemId) {
    const result = systems.buySupply(profile, itemId);
    if (!result.ok) { showNotice("铜钱不足"); return; }
    profile = result.profile;
    writeJson(PROFILE_KEY, profile);
    renderCampaign();
    showNotice(itemId === "medicine" ? "已补充金疮药" : "已补充清心散");
  }

  function renderCampaignFocus(saved, completed) {
    const lastIndex = campaign.stages.findIndex((record) => record.id === profile.lastStage);
    const nextIncomplete = campaign.stages.find((record) => !completed.has(record.id));
    const record = saved
      ? findStageRecord(saved.stageId)
      : nextIncomplete || campaign.stages[Math.max(0, lastIndex)] || campaign.stages[0];
    if (!record) return;
    const isSaved = saved?.stageId === record.id;
    const isCompleted = completed.has(record.id);
    $("#focusKicker").textContent = isSaved ? "战局待续" : isCompleted ? "旧战重温" : record.index === 1 ? "从这里入史" : "下一场史局";
    $("#focusBattleTitle").textContent = record.battleTitle;
    $("#focusChapter").textContent = record.chapter;
    $("#focusStory").textContent = record.title;
    $("#focusObjective").textContent = record.objective;
    $("#focusIndex").textContent = record.isProcedural ? `演武 / ${campaign.stageCount}` : `${String(record.index).padStart(3, "0")} / ${campaign.stageCount}`;
    $("#focusTurns").textContent = `${systems.effectiveTurnLimit(record.turnLimit, profile.settings.battleDifficulty)} 回合`;
    $("#focusStatus").textContent = isSaved ? `第 ${saved.turn || 1} 回合` : isCompleted ? "已克" : "未出阵";
    const recommendedLevel = systems.recommendedStageLevel(record.index);
    $("#focusRank").textContent = `当前 ${profile.armyRank} · 建议 ${recommendedLevel}`;
    $("#focusMap").src = mapPath(record);
    $("#focusMap").alt = `${record.battleTitle}战场`;
    $("#focusStageButton").textContent = isSaved ? "继续战局" : isCompleted ? "重温此战" : "出兵此战";
    $("#focusStageButton").dataset.stageId = record.id;
    $("#focusStageButton").dataset.saved = isSaved ? "true" : "false";
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]);
  }

  function openCampaign() {
    if (state && stageRecord && !state.result) saveBattle(false);
    setExerciseMenu(false);
    stopStoryVoice();
    storyDone = null;
    storyEntries = [];
    storyIndex = 0;
    $("#storyModal").hidden = true;
    $("#confirmModal").hidden = true;
    $("#campaignScreen").hidden = false;
    $("#resultModal").hidden = true;
    renderCampaign();
  }

  function findStageRecord(stageId) {
    return campaign?.stages.find((item) => item.id === stageId)
      || (pcgrlTemplate?.id === stageId ? pcgrlTemplate : null)
      || (mapElitesTemplate?.id === stageId ? mapElitesTemplate : null);
  }

  async function startStage(stageId, savedState = null, options = {}) {
    const record = findStageRecord(stageId);
    if (!record || enemyRunning) return;
    if (!record.isProcedural && !systems.isStageUnlocked(record, profile, campaign.stages)) {
      showNotice("请先完成上一场战役");
      return;
    }
    setExerciseMenu(false);
    stageRecord = record;
    $("#campaignScreen").hidden = true;
    $("#resultModal").hidden = true;
    $("#confirmModal").hidden = true;
    selectedId = null;
    selectedSkillId = null;
    inspectionId = null;
    reachable.clear();
    unitSerial = 0;
    mapZoom = 1;
    updateZoom();
    state = savedState || freshState(record);
    if (options.procedural) state.procedural = options.procedural;
    state.logs ||= [];
    state.stats ||= { attacks: 0, defeated: 0, supplies: 0, skills: 0, moves: 0, policyDecisions: 0, policyFallbacks: 0 };
    state.stats.skills ||= 0;
    state.stats.moves ||= 0;
    state.stats.policyDecisions ||= 0;
    state.stats.policyFallbacks ||= 0;
    state.policyDecisions ||= [];
    state.eventLog ||= [];
    state.eventCounts ||= {};
    state.itemsUsed ||= {};
    state.storySkipped ||= false;
    state.claimedSites ||= [];
    state.triggeredDuels ||= [];
    state.inventory ||= { ...profile.inventory };
    state.units.forEach((unit) => { unit.effects ||= []; });
    unitSerial = Math.max(0, ...state.units.map((unit) => Number(String(unit.id).match(/-(\d+)$/)?.[1] || 0)));
    setStatus("正在列阵");
    updateStageHeader();
    configureBoard();
    await runtime.loadStage(record, gameApi);
    restoring = Boolean(savedState);
    runtime.invoke("on_deploy");
    if (!savedState) {
      for (const entry of [...asList(record.stage.deploy?.unselectables), ...asList(record.stage.deploy?.selectables)]) {
        if (entry?.hero && entry?.position) spawnUnit(entry.hero, 1, "own", entry.position);
      }
    }
    runtime.invoke("on_begin");
    if (!savedState) {
      const preset = systems.difficultyPreset(battleDifficulty());
      log(`难度：${{ easy: "简单", medium: "标准", hard: "艰难" }[preset.id]}；敌军等级 ${preset.enemyLevelOffset >= 0 ? "+" : ""}${preset.enemyLevelOffset}，生命 ×${preset.enemyHpMultiplier}，攻击 ×${preset.enemyPowerMultiplier}，防御 ×${preset.enemyDefenseMultiplier}。`, "event");
    }
    if (savedState) {
      for (let turn = 1; turn <= state.turn; turn++) {
        runtimeTurnOverride = turn;
        runtime.invoke("on_update");
      }
      runtimeTurnOverride = null;
    }
    restoring = false;
    state.replayInitial ||= state.units.map((unit) => ({ id: unit.id, heroId: unit.heroId, team: unit.team, x: unit.x, y: unit.y, level: unit.level }));
    const firstOwn = activeUnits("own")[0];
    boardCursor = firstOwn ? { x: firstOwn.x, y: firstOwn.y } : { x: 0, y: 0 };
    if (state.procedural) {
      const meta = state.procedural.meta || {};
      const validation = meta.validation || {};
      if (meta.source === "constrained-map-elites") {
        log(`MAP-Elites：档案格 R${meta.routeCount}/D${Number(meta.archiveCell?.[1] || 0) + 1}；种子 ${state.procedural.seed}；质量 ${Number(meta.quality || 0).toFixed(3)}；硬校验通过。`, "event");
      } else {
        log(`端侧生成：${meta.source || "未知"}；种子 ${state.procedural.seed}；修复 ${meta.repairs || 0} 格；障碍 ${(Number(validation.blockedRatio || 0) * 100).toFixed(1)}%。`, "event");
      }
    }
    state.phase = state.result ? "ended" : "player";
    state.initialOwnCount ||= state.units.filter((unit) => unit.team === "own").length;
    state.initialEnemyCount ||= state.units.filter((unit) => unit.team === "enemy").length;
    loadStageMap();
    saveBattle(false);
    updateUI();
    $("#storyReplayButton").hidden = !asList(record.story?.intro).length;
    requestAnimationFrame(centerOnOwnArmy);
    if (!savedState) {
      const intro = asList(record.story?.intro);
      if (intro.length) openStory(intro, () => beginTutorialOrBattle());
      else beginTutorialOrBattle();
    } else if (state.result) {
      showResult();
    } else {
      showNotice(`已恢复第 ${state.turn} 回合`);
    }
  }

  async function startProceduralStage() {
    if (enemyRunning || !pcgrlTemplate || !mapElitesTemplate || !mapElitesArchive) return;
    setExerciseMenu(false);
    const button = $("#proceduralButton");
    const mode = $("#proceduralMode").value || "map-elites";
    const requestedDifficulty = $("#proceduralDifficulty").value || "auto";
    const difficultyDecision = systems.selectDifficulty(profile, requestedDifficulty, Math.random());
    const difficulty = difficultyDecision.difficulty;
    const difficultyValue = { easy: 0, medium: .5, hard: 1 }[difficulty] ?? .5;
    const randomValues = new Uint32Array(1);
    window.crypto?.getRandomValues?.(randomValues);
    const seed = (randomValues[0] || Date.now()) & 0x7fffffff;
    button.disabled = true;
    button.textContent = "正在生成";
    if (mode === "map-elites") {
      try {
        const generated = DongzhouMapElitesRuntime.selectElite(mapElitesArchive, difficulty, seed);
        await startStage(mapElitesTemplate.id, null, {
          procedural: {
            terrain: generated.rows,
            difficulty,
            seed,
            objectiveType: "historical-map-elites",
            meta: generated.meta,
            decision: difficultyDecision
          }
        });
        setStatus(`MAP-Elites 档案 R${generated.meta.routeCount}/D${generated.meta.archiveCell[1] + 1} 已通过硬校验`);
        if (requestedDifficulty === "auto") showNotice(`智能推荐：${{ easy: "简单", medium: "标准", hard: "艰难" }[difficulty]}`);
      } finally {
        button.disabled = false;
        button.textContent = "生成垂沙演武";
      }
      return;
    }
    let policyTiles = null;
    let nativeMeta = { ready: false, reason: "policy-unavailable" };
    try {
      if (window.DongzhouPcgrl?.isReady?.()) {
        const payload = JSON.parse(window.DongzhouPcgrl.generate(difficultyValue, seed) || "{}");
        if (Array.isArray(payload.tiles) && payload.tiles.length === DongzhouPcgrlRuntime.CELL_COUNT) policyTiles = payload.tiles;
        nativeMeta = payload;
      }
    } catch (error) {
      nativeMeta = { ready: false, reason: String(error?.message || error) };
    }
    const generated = DongzhouPcgrlRuntime.generate(policyTiles, pcgrlTemplate.stage.map.terrain, difficulty, seed);
    generated.meta.inferenceMs = Number(nativeMeta.inference_ms || 0);
    generated.meta.modelVersion = nativeMeta.model_version || "unavailable";
    generated.meta.modelSha256 = nativeMeta.model_sha256 || "unavailable";
    generated.meta.nativeReason = nativeMeta.reason || null;
    try {
      await startStage(pcgrlTemplate.id, null, { procedural: { terrain: generated.rows, difficulty, seed, meta: generated.meta, decision: difficultyDecision } });
      setStatus(generated.meta.fallback ? "模板回退已通过硬校验" : "PCGRL + WFC 地形已通过硬校验");
      if (requestedDifficulty === "auto") showNotice(`智能推荐：${{ easy: "简单", medium: "标准", hard: "艰难" }[difficulty]}`);
    } finally {
      button.disabled = false;
      button.textContent = "生成麻隧演武";
    }
  }

  function syncProceduralButton() {
    $("#proceduralButton").textContent = $("#proceduralMode").value === "pcgrl" ? "生成麻隧演武" : "生成垂沙演武";
  }

  function setExerciseMenu(open) {
    const expanded = Boolean(open);
    $("#exercisePanel").hidden = !expanded;
    $("#exerciseMenuButton").setAttribute("aria-expanded", String(expanded));
  }

  function freshState(record) {
    return {
      stageId: record.id,
      turn: 1,
      phase: "player",
      medicine: Number(profile.inventory.medicine || 0),
      inventory: { ...profile.inventory },
      appointed: [],
      units: [],
      claimedSites: [],
      triggeredDuels: [],
      result: null,
      stats: { attacks: 0, defeated: 0, supplies: 0, skills: 0, moves: 0, policyDecisions: 0, policyFallbacks: 0 },
      policyDecisions: [],
      eventLog: [], eventCounts: {}, itemsUsed: {}, storySkipped: false, triggeredStoryEvents: [],
      startedAt: Date.now(),
      difficulty: profile.settings.battleDifficulty,
      logs: [{ text: `${record.battleTitle}：两军列阵。`, tone: "event" }]
    };
  }

  function buildInventory(items) {
    return Object.fromEntries(asList(items).map((item) => [item.id, Number(item.initial || 0)]));
  }

  function initialMedicine(items) {
    return Number(asList(items).find((item) => item.id === "medicine")?.initial || 0);
  }

  function updateStageHeader() {
    $("#stageHeading").textContent = `${stageRecord.chapter} · ${stageRecord.battleTitle}`;
    $("#objectiveText").textContent = stageRecord.objective;
    const difficultyLabel = { easy: "简单", medium: "标准", hard: "艰难" }[battleDifficulty()] || "标准";
    $("#terrainText").textContent = state?.procedural ? `${stageRecord.battleTitle} · ${difficultyLabel}` : `${stageRecord.chapter} · ${stageRecord.battleTitle} · ${difficultyLabel}`;
  }

  function configureBoard() {
    const [width, height] = stageSize();
    cellPixels = clamp(Math.floor(3072 / Math.max(width, height)), 32, 64);
    canvas.width = width * cellPixels;
    canvas.height = height * cellPixels;
    canvas.style.width = `${canvas.width}px`;
    canvas.style.height = `${canvas.height}px`;
  }

  function loadStageMap() {
    mapImage = new Image();
    mapPresentationCanvas = null;
    mapPresentationKey = "";
    if (state?.procedural) { requestRender(); return; }
    mapImage.addEventListener("load", requestRender);
    mapImage.addEventListener("error", () => { log("舆图载入失败，已切换地形底图。", "bad"); requestRender(); });
    mapImage.src = mapPath(stageRecord);
  }

  function stageSize() {
    const size = asList(stageRecord?.stage?.map?.size);
    return [Number(size[0] || 19), Number(size[1] || 14)];
  }

  function terrainRows() {
    return asList(state?.procedural?.terrain || stageRecord?.stage?.map?.terrain);
  }

  function battleDifficulty() {
    return state?.procedural?.difficulty || state?.difficulty || profile.settings?.battleDifficulty || "medium";
  }

  function battleTurnLimit() {
    return systems.effectiveTurnLimit(stageRecord?.turnLimit || 1, battleDifficulty());
  }

  function spawnUnit(heroId, level, team, rawPosition) {
    const [x, y] = luaPoint(rawPosition);
    if (restoring) {
      const existing = state.units.find((unit) => unit.heroId === heroId && unit.x === x && unit.y === y);
      if (existing) return existing.id;
    }
    const hero = heroById.get(heroId) || { id: heroId, class: "Infantry", stat: [70, 70, 70, 70, 70], model: "infantry-1-red" };
    const unitClass = classById.get(hero.class) || classById.get("Infantry");
    level = systems.effectiveHeroLevel(level, team, profile, stageRecord.index, battleDifficulty(), heroId);
    const equipment = team === "own" ? systems.equipmentBonuses(profile) : { power: 0, defense: 0, move: 0, maxMp: 0 };
    const growth = systems.unitGrowthBonuses(level);
    const difficultyModifiers = systems.unitDifficultyModifiers(team, battleDifficulty());
    const maxHp = Math.round((Number(unitClass.hp?.[0] || 100) + Number(unitClass.hp?.[1] || 5) * Math.max(0, level - 1)) * difficultyModifiers.hp);
    const maxMp = Number(unitClass.mp?.[0] || 10) + Number(unitClass.mp?.[1] || 1) * Math.max(0, level - 1) + equipment.maxMp;
    const id = `${heroId}-${++unitSerial}`;
    state.units.push({
      id, heroId, name: displayName(heroId), team, level, classId: hero.class, x, y,
      hp: maxHp, maxHp, mp: maxMp, maxMp, move: Number(unitClass.move || 5) + equipment.move,
      power: Math.round((15.5 + Number(hero.stat?.[1] || 70) * .34 + growth.power + equipment.power) * difficultyModifiers.power),
      defense: Math.round((8 + Number(hero.stat?.[2] || 70) * .22 + growth.defense + equipment.defense) * difficultyModifiers.defense),
      attackRange: unitClass.attack_range || "Adjacent4", acted: false, moved: false,
      invulnerable: false, direction: null, effects: []
    });
    return id;
  }

  function resolveUnits(ref) {
    return state.units.filter((unit) => unit.id === ref || unit.heroId === ref);
  }

  function activeUnits(team = null) {
    return state.units.filter((unit) => unit.hp > 0 && (!team || unit.team === team));
  }

  function getUnit(id) {
    return state.units.find((unit) => unit.id === id) || null;
  }

  function unitAt(x, y, ignoreId = null) {
    return state.units.find((unit) => unit.hp > 0 && unit.id !== ignoreId && unit.x === x && unit.y === y) || null;
  }

  const gameApi = {
    appoint_hero(hero, level) {
      if (!state.appointed.some((entry) => entry.hero === hero)) state.appointed.push({ hero, level: Number(level || 1) });
      return hero;
    },
    generate_unit(hero, level, force, position) { return spawnUnit(String(hero), Number(level || 1), String(force), position); },
    has_unit(ref) { return resolveUnits(ref).some((unit) => unit.hp > 0); },
    set_unit_invulnerable(ref, value) { resolveUnits(ref).forEach((unit) => { unit.invulnerable = Boolean(value); }); },
    push_cmd_speak(ref, text) {
      if (restoring) return;
      const speaker = resolveUnits(ref)[0]?.name || "军报";
      log(`${speaker}：${text}`, "event");
      queueSpeech({ speaker, text: String(text) });
    },
    push_cmd_move(ref, position) {
      if (restoring) return;
      const [x, y] = luaPoint(position);
      const unit = resolveUnits(ref).find((item) => item.hp > 0);
      if (unit && !unitAt(x, y, unit.id)) { unit.x = x; unit.y = y; }
    },
    is_unit_within(ref, position, radius) {
      const [x, y] = luaPoint(position);
      return resolveUnits(ref).some((unit) => unit.hp > 0 && manhattan(unit, { x, y }) <= Number(radius));
    },
    are_units_within(left, right, radius) {
      return resolveUnits(left).some((a) => a.hp > 0 && resolveUnits(right).some((b) => b.hp > 0 && manhattan(a, b) <= Number(radius)));
    },
    is_force_within(force, position, radius) {
      const [x, y] = luaPoint(position);
      return activeUnits(String(force)).some((unit) => manhattan(unit, { x, y }) <= Number(radius));
    },
    get_num_commanders_alive(force) {
      const commanders = new Set(asList(stageRecord.commanders));
      return activeUnits(force ? String(force) : null).filter((unit) => commanders.has(unit.heroId)).length;
    },
    get_num_enemies_alive() { return activeUnits("enemy").length; },
    get_num_units_alive(ref) { return ref == null ? activeUnits().length : resolveUnits(String(ref)).filter((unit) => unit.hp > 0).length; },
    get_turn_current() { return runtimeTurnOverride ?? state.turn; },
    set_unit_direction(ref, direction) { resolveUnits(ref).forEach((unit) => { unit.direction = direction; }); },
    set_force_direction(force, direction) { activeUnits(String(force)).forEach((unit) => { unit.direction = direction; }); },
    is_cell_vacant(position) { const [x, y] = luaPoint(position); return !unitAt(x, y); }
  };

  function queueSpeech(entry) {
    state.pendingSpeeches ||= [];
    state.pendingSpeeches.push(entry);
  }

  function flushSpeeches() {
    if (!state?.pendingSpeeches?.length || !$("#storyModal").hidden) return;
    const entries = state.pendingSpeeches.splice(0);
    openStory(entries);
  }

  function processStoryEvents() {
    if (!state || !stageRecord) return;
    state.triggeredStoryEvents ||= [];
    const context = { turn: state.turn, units: state.units, claimedSites: state.claimedSites };
    for (const event of asList(stageRecord.story?.events)) {
      const id = String(event?.id || "");
      if (!id || state.triggeredStoryEvents.includes(id)) continue;
      if (!systems.storyEventMatches(event, context)) continue;
      state.triggeredStoryEvents.push(id);
      queueSpeech({ speaker: String(event.speaker || "军报"), text: String(event.text || "") });
      recordEvent("story_event", { id, trigger: event.trigger, turn: state.turn });
    }
  }

  function terrainCost(unit, x, y) {
    const [width, height] = stageSize();
    if (x < 0 || x >= width || y < 0 || y >= height) return 255;
    const char = terrainRows()[y]?.[x] || "f";
    const terrainIndex = terrainByChar.get(char);
    const classIndex = asList(config.unit_classes).findIndex((entry) => entry.id === unit.classId);
    const cost = asList(asList(config.terrain_movecost)[terrainIndex] || [])[classIndex];
    return Number(cost ?? 1);
  }

  function edgeBlocked(x1, y1, x2, y2) {
    return asList(stageRecord.stage.map.blocked_edges).some((edge) => {
      const from = asList(edge.from); const to = asList(edge.to);
      return (from[0] === x1 && from[1] === y1 && to[0] === x2 && to[1] === y2) ||
        (from[0] === x2 && from[1] === y2 && to[0] === x1 && to[1] === y1);
    });
  }

  function calculateReachable(unit) {
    const result = new Map([[pointKey(unit.x, unit.y), { x: unit.x, y: unit.y, cost: 0 }]]);
    const queue = [{ x: unit.x, y: unit.y, cost: 0 }];
    while (queue.length) {
      queue.sort((a, b) => a.cost - b.cost);
      const current = queue.shift();
      if (current.cost >= unit.move) continue;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const x = current.x + dx; const y = current.y + dy;
        const cost = terrainCost(unit, x, y);
        if (cost >= 255 || edgeBlocked(current.x, current.y, x, y) || unitAt(x, y, unit.id)) continue;
        const total = current.cost + cost;
        if (total > unit.move) continue;
        const key = pointKey(x, y);
        if (result.has(key) && result.get(key).cost <= total) continue;
        const next = { x, y, cost: total };
        result.set(key, next);
        queue.push(next);
      }
    }
    result.delete(pointKey(unit.x, unit.y));
    return result;
  }

  function manhattan(a, b) { return Math.abs(a.x - b.x) + Math.abs(a.y - b.y); }
  function chebyshev(a, b) { return Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)); }

  function canAttack(attacker, defender) {
    if (!attacker || !defender || attacker.hp <= 0 || defender.hp <= 0 || sameSide(attacker, defender)) return false;
    if (attacker.attackRange === "Adjacent8") return chebyshev(attacker, defender) === 1;
    if (attacker.attackRange?.startsWith("Distance")) return manhattan(attacker, defender) >= 1 && manhattan(attacker, defender) <= 2;
    return manhattan(attacker, defender) === 1;
  }

  function sameSide(a, b) {
    return a.team === b.team || (a.team !== "enemy" && b.team !== "enemy");
  }

  function selectUnit(unit) {
    inspectionId = unit.id;
    selectedSkillId = null;
    if (unit.team === "own" && state.phase === "player" && !unit.acted && !state.result && !enemyRunning) {
      selectedId = unit.id;
      reachable = unit.moved ? new Map() : calculateReachable(unit);
      setStatus(`${unit.name} · 移动 ${unit.move} · 攻击 ${unit.power}`);
      recordEvent("select", { unit: unit.heroId, x: unit.x, y: unit.y });
      advanceTutorial("select");
    }
    updateUI();
  }

  async function handleBoardClick(event) {
    if (dragged || !state || state.phase !== "player" || state.result || enemyRunning || !$("#storyModal").hidden) return;
    const rect = canvas.getBoundingClientRect();
    const [width, height] = stageSize();
    const x = Math.floor((event.clientX - rect.left) / rect.width * width);
    const y = Math.floor((event.clientY - rect.top) / rect.height * height);
    await handleBoardCell(x, y);
  }

  async function handleBoardCell(x, y) {
    if (!state || state.phase !== "player" || state.result || enemyRunning || !$("#storyModal").hidden) return;
    const clicked = unitAt(x, y);
    const selected = getUnit(selectedId);
    if (selected && selectedSkillId) {
      if (clicked) await useSelectedSkill(selected, clicked);
      else showNotice("请选择战技目标");
      return;
    }
    if (clicked?.team === "own" && !clicked.acted) { selectUnit(clicked); return; }
    if (clicked) inspectionId = clicked.id;
    if (!selected || selected.acted) { updateUI(); return; }
    if (clicked && canAttack(selected, clicked)) {
      performAttack(selected, clicked, true);
      selected.acted = true;
      state.stats.attacks++;
      recordEvent("attack", { actor: selected.heroId, target: clicked.heroId, x, y });
      advanceTutorial("action");
      feedback("attack");
      selectedId = null;
      reachable.clear();
      await runStageRules();
      saveBattle(false);
      updateUI();
      return;
    }
    const destination = reachable.get(pointKey(x, y));
    if (!clicked && destination && !selected.moved) {
      selected.x = x; selected.y = y; selected.moved = true;
      state.stats.moves++;
      recordEvent("move", { unit: selected.heroId, x, y });
      advanceTutorial("move");
      reachable.clear();
      claimSite(selected);
      log(`${selected.name}推进至（${x + 1}，${y + 1}）。`);
      setStatus(`${selected.name}已移动，可攻击或待命`);
      await runStageRules();
      saveBattle(false);
      updateUI();
    }
  }

  async function useSelectedSkill(actor, target) {
    const skill = systems.skillForUnit(actor);
    if (!skill || skill.id !== selectedSkillId) { selectedSkillId = null; updateUI(); return; }
    if (!systems.skillTargetValid(actor, target, skill)) { showNotice("目标或距离不符合战技要求"); return; }
    const result = systems.applySkill(actor, target, skill);
    if (!result.ok) { showNotice(result.reason === "insufficient-mp" ? "谋略不足" : "战技无法施放"); return; }
    actor.acted = true;
    state.stats.skills++;
    recordEvent("skill", { actor: actor.heroId, target: target.heroId, skill: skill.id, result: result.kind, amount: result.amount || 0 });
    advanceTutorial("action");
    feedback("skill");
    if (result.kind === "damage") {
      log(`${actor.name}施展${skill.name}，${target.name}损失 ${result.amount} 点兵力。`, "good");
      if (result.defeated && target.team === "enemy") state.stats.defeated++;
    } else if (result.kind === "heal") {
      log(`${actor.name}施展${skill.name}，为${target.name}恢复 ${result.amount} 点兵力。`, "good");
    } else {
      log(`${actor.name}对${target.name}施展${skill.name}，效果持续 ${result.turns} 回合。`, "event");
    }
    selectedId = null;
    selectedSkillId = null;
    reachable.clear();
    await runStageRules();
    saveBattle(false);
    updateUI();
  }

  function performAttack(attacker, defender, allowCounter) {
    const duel = asList(stageRecord.duels).find((entry) => entry.attacker === attacker.heroId && entry.defender === defender.heroId);
    const duelKey = duel ? `${duel.attacker}:${duel.defender}` : null;
    if (duel && !state.triggeredDuels.includes(duelKey)) {
      state.triggeredDuels.push(duelKey);
      defender.hp = 0;
      state.stats.defeated++;
      recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage: defender.maxHp, duel: true });
      log(duel.text || `${attacker.name}阵前击退${defender.name}。`, "event");
      queueSpeech({ speaker: attacker.name, text: duel.attacker_speech || "今日便在阵前分个胜负！" });
      if (duel.result_speech) queueSpeech({ speaker: "军报", text: duel.result_speech });
      return;
    }
    if (defender.invulnerable) {
      log(`${defender.name}尚有剧情护卫，本次攻击未能破阵。`, "event");
      recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage: 0, invulnerable: true });
      return;
    }
    const terrainGuard = terrainDefense(defender);
    const damage = Math.max(8, systems.effectivePower(attacker) - Math.round(systems.effectiveDefense(defender) * .42) - terrainGuard + randomInt(-4, 5));
    defender.hp = Math.max(0, defender.hp - damage);
    recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage, defenderHp: defender.hp });
    log(`${attacker.name}攻击${defender.name}，造成 ${damage} 点伤害。`, attacker.team === "enemy" ? "bad" : "good");
    if (defender.hp <= 0) {
      log(`${defender.name}退出战场。`, defender.team === "enemy" ? "good" : "bad");
      if (defender.team === "enemy") state.stats.defeated++;
      return;
    }
    if (allowCounter && canAttack(defender, attacker) && !attacker.invulnerable) {
      const counter = Math.max(6, Math.round(systems.effectivePower(defender) * .58 - systems.effectiveDefense(attacker) * .25 + randomInt(-3, 3)));
      attacker.hp = Math.max(0, attacker.hp - counter);
      log(`${defender.name}反击，${attacker.name}损失 ${counter} 点兵力。`, attacker.team === "own" ? "bad" : "good");
    }
  }

  function terrainDefense(unit) {
    const char = terrainRows()[unit.y]?.[unit.x];
    return ["F", "m", "r", "W", "C", "G"].includes(char) ? 5 : ["e", "c", "b"].includes(char) ? 3 : 0;
  }

  function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

  function claimSite(unit) {
    const site = asList(stageRecord.sites).find((entry) => { const position = asList(entry.position); return position[0] === unit.x && position[1] === unit.y; });
    if (!site || state.claimedSites.includes(site.id)) return;
    state.claimedSites.push(site.id);
    const before = unit.hp;
    unit.hp = Math.min(unit.maxHp, unit.hp + Number(site.restore_hp || 0));
    unit.mp = Math.min(unit.maxMp, unit.mp + Number(site.restore_mp || 0));
    for (const reward of asList(site.rewards)) {
      state.inventory[reward.item] = Number(state.inventory[reward.item] || 0) + Number(reward.amount || 0);
    }
    state.medicine = Number(state.inventory.medicine || 0);
    state.stats.supplies++;
    recordEvent("supply_site", { unit: unit.heroId, site: site.id, hp: unit.hp - before });
    log(`${unit.name}占领${site.name || "补给点"}，恢复 ${unit.hp - before} 点兵力。`, "good");
    showNotice(`${site.name || "补给点"}已占领`);
  }

  function waitSelected() {
    const unit = getUnit(selectedId);
    if (!unit || unit.acted || state.phase !== "player") return;
    unit.acted = true;
    log(`${unit.name}原地整队。`);
    recordEvent("wait", { unit: unit.heroId, x: unit.x, y: unit.y });
    advanceTutorial("action");
    selectedId = null;
    selectedSkillId = null;
    reachable.clear();
    saveBattle(false);
    updateUI();
  }

  function useMedicine() {
    const unit = getUnit(selectedId);
    if (!unit || unit.acted || state.phase !== "player" || Number(state.inventory.medicine || 0) <= 0) return;
    if (unit.hp >= unit.maxHp) { showNotice(`${unit.name}兵力已满`); return; }
    const medicine = asList(stageRecord.items).find((item) => item.id === "medicine");
    const before = unit.hp;
    unit.hp = Math.min(unit.maxHp, unit.hp + Number(medicine?.hp || 60));
    state.inventory.medicine--;
    profile.inventory.medicine = Math.min(profile.inventory.medicine, state.inventory.medicine);
    writeJson(PROFILE_KEY, profile);
    state.itemsUsed.medicine = Number(state.itemsUsed.medicine || 0) + 1;
    state.medicine = state.inventory.medicine;
    unit.acted = true;
    log(`${unit.name}使用金疮药，恢复 ${unit.hp - before} 点兵力。`, "good");
    recordEvent("item", { unit: unit.heroId, item: "medicine", amount: unit.hp - before });
    advanceTutorial("action");
    feedback("heal");
    selectedId = null;
    selectedSkillId = null;
    reachable.clear();
    saveBattle(false);
    updateUI();
  }

  function useSpiritPowder() {
    const unit = getUnit(selectedId);
    if (!unit || unit.acted || state.phase !== "player" || Number(state.inventory.spirit_powder || 0) <= 0) return;
    if (unit.mp >= unit.maxMp) { showNotice(`${unit.name}谋略已满`); return; }
    const powder = asList(stageRecord.items).find((item) => item.id === "spirit_powder");
    const before = unit.mp;
    unit.mp = Math.min(unit.maxMp, unit.mp + Number(powder?.mp || 30));
    state.inventory.spirit_powder--;
    profile.inventory.spirit_powder = Math.min(profile.inventory.spirit_powder, state.inventory.spirit_powder);
    writeJson(PROFILE_KEY, profile);
    state.itemsUsed.spirit_powder = Number(state.itemsUsed.spirit_powder || 0) + 1;
    unit.acted = true;
    log(`${unit.name}使用清心散，恢复 ${unit.mp - before} 点谋略。`, "good");
    recordEvent("item", { unit: unit.heroId, item: "spirit_powder", amount: unit.mp - before });
    advanceTutorial("action");
    feedback("heal");
    selectedId = null;
    selectedSkillId = null;
    reachable.clear();
    saveBattle(false);
    updateUI();
  }

  async function toggleSkill() {
    const unit = getUnit(selectedId);
    const skill = systems.skillForUnit(unit);
    if (!unit || !skill || unit.acted || state.phase !== "player" || unit.mp < skill.cost) return;
    if (skill.target === "self") {
      selectedSkillId = skill.id;
      await useSelectedSkill(unit, unit);
      return;
    }
    selectedSkillId = selectedSkillId === skill.id ? null : skill.id;
    if (selectedSkillId) {
      reachable.clear();
      setStatus(`${unit.name} · ${skill.name}：请选择目标`);
    } else {
      reachable = unit.moved ? new Map() : calculateReachable(unit);
      setStatus(`${unit.name} · 移动 ${unit.move} · 攻击 ${unit.power}`);
    }
    updateUI();
  }

  async function endPlayerTurn() {
    if (!state || state.phase !== "player" || state.result || enemyRunning) return;
    enemyRunning = true;
    recordEvent("end_turn", { turn: state.turn });
    advanceTutorial("end_turn");
    selectedId = null;
    reachable.clear();
    activeUnits("own").forEach((unit) => { unit.acted = true; });
    state.phase = "ally";
    updateUI();
    await runAiForce("ally");
    if (!state.result) {
      state.phase = "enemy";
      updateUI();
      await runAiForce("enemy");
    }
    if (!state.result) {
      state.turn++;
      activeUnits().forEach((unit) => systems.tickEffects(unit));
      activeUnits("own").forEach((unit) => { unit.acted = false; unit.moved = false; });
      state.phase = "player";
      await runStageRules();
      if (!state.result && state.turn > battleTurnLimit()) finish(false, `已超过 ${battleTurnLimit()} 回合限制。`);
    }
    enemyRunning = false;
    saveBattle(false);
    updateUI();
    flushSpeeches();
  }

  async function runAiForce(team) {
    const actors = [...activeUnits(team)];
    const animationDelay = actors.length > 24 ? 18 : actors.length > 12 ? 32 : 55;
    for (const actor of actors) {
      if (state.result || actor.hp <= 0) break;
      const targets = team === "enemy" ? activeUnits().filter((unit) => unit.team !== "enemy") : activeUnits("enemy");
      if (!targets.length) break;
      targets.sort((a, b) => manhattan(actor, a) - manhattan(actor, b));
      const action = team === "enemy" ? chooseHappoAction(actor, targets) : null;
      if (action) {
        actor.x = action.x;
        actor.y = action.y;
        const target = action.targetId ? getUnit(action.targetId) : null;
        if (target && canAttack(actor, target)) performAttack(actor, target, true);
      } else {
        let target = targets[0];
        if (!canAttack(actor, target)) {
          const options = [...calculateReachable(actor).values()];
          options.sort((a, b) => manhattan(a, target) - manhattan(b, target) || a.cost - b.cost);
          const destination = options[0];
          if (destination) { actor.x = destination.x; actor.y = destination.y; }
        }
        target = targets.filter((unit) => canAttack(actor, unit)).sort((a, b) => a.hp - b.hp)[0];
        if (target) performAttack(actor, target, true);
      }
      recordEvent("ai_action", { team, unit: actor.heroId, x: actor.x, y: actor.y });
      inspectionId = actor.id;
      await runStageRules();
      requestRender();
      await sleep(animationDelay);
    }
  }

  const HAPPO_ROLES = ["Lord", "King", "Infantry", "Cavalry", "Archer", "Strategist", "Support", "Artillery", "Fighter", "Bandit", "Other"];
  const TRAINED_HAPPO_ROLES = new Set(["King", "Infantry", "Cavalry", "Strategist"]);

  function chooseHappoAction(actor, targets) {
    const actions = buildHappoActions(actor, targets);
    if (!actions.length) return null;
    if (!TRAINED_HAPPO_ROLES.has(actor.classId)) {
      recordPolicyDecision(actor, actions.length, null, 1, "untrained-role");
      return null;
    }
    const policyRate = systems.difficultyPreset(battleDifficulty()).aiPolicyRate;
    if (controllerRoll(actor) >= policyRate) {
      recordPolicyDecision(actor, actions.length, null, policyRate, "difficulty-blend");
      return null;
    }
    if (!window.DongzhouHappo?.isReady?.()) {
      recordPolicyDecision(actor, actions.length, null, policyRate, "policy-unavailable");
      return null;
    }
    const local = buildHappoLocal(actor);
    const candidates = buildHappoCandidates(actor, actions, targets);
    const matchedRole = HAPPO_ROLES.indexOf(actor.classId);
    const roleIndex = matchedRole >= 0 ? matchedRole : HAPPO_ROLES.length - 1;
    try {
      const choice = Number(window.DongzhouHappo.selectAction(
        JSON.stringify(local), JSON.stringify(candidates), actions.length, roleIndex));
      if (Number.isInteger(choice) && choice >= 0 && choice < actions.length) {
        recordPolicyDecision(actor, actions.length, choice, policyRate, null);
        return actions[choice];
      }
      recordPolicyDecision(actor, actions.length, null, policyRate, "invalid-output");
      return null;
    } catch (error) {
      recordPolicyDecision(actor, actions.length, null, policyRate, String(error?.message || "inference-error"));
      return null;
    }
  }

  function controllerRoll(actor) {
    let hash = (state.turn * 2654435761) >>> 0;
    const value = `${actor.heroId}:${actor.id}`;
    for (let index = 0; index < value.length; index++) hash = Math.imul(hash ^ value.charCodeAt(index), 16777619) >>> 0;
    return (hash & 0xffff) / 0x10000;
  }

  function recordPolicyDecision(actor, availableActions, action, behaviorProbability, fallbackReason) {
    state.stats.policyDecisions++;
    if (fallbackReason) state.stats.policyFallbacks++;
    state.policyDecisions.push({
      schema_version: "happo-decision-v1",
      policy_version: systems.POLICY_VERSION,
      runtime_version: systems.RUNTIME_VERSION,
      turn: state.turn,
      actor: actor.heroId,
      role: actor.classId,
      available_actions: availableActions,
      action,
      behavior_probability: null,
      controller_probability: fallbackReason === "difficulty-blend" ? 1 - behaviorProbability : behaviorProbability,
      fallback_reason: fallbackReason
    });
    if (state.policyDecisions.length > 120) state.policyDecisions.shift();
  }

  function buildHappoActions(actor, targets) {
    const reachableOptions = [...calculateReachable(actor).values()];
    const positions = [{ x: actor.x, y: actor.y, cost: 0 }, ...reachableOptions];
    const nearest = targets[0];
    const fallbackPositions = canAttack(actor, nearest) ? positions.slice(0, 1) : [...reachableOptions]
      .sort((a, b) => manhattan(a, nearest) - manhattan(b, nearest) || a.cost - b.cost);
    const fallbackPosition = fallbackPositions[0] || positions[0];
    const fallbackTarget = targets.filter((target) => canAttackAt(actor, fallbackPosition, target))
      .sort((a, b) => a.hp - b.hp)[0];
    const actions = [{
      type: fallbackTarget ? 2 : fallbackPosition.x === actor.x && fallbackPosition.y === actor.y ? 0 : 1,
      x: fallbackPosition.x, y: fallbackPosition.y, targetId: fallbackTarget?.id || null
    }];
    const seen = new Set([happoActionKey(actions[0])]);

    for (const position of positions) {
      const attackTargets = targets.filter((target) => canAttackAt(actor, position, target));
      for (const target of attackTargets) {
        const action = { type: 2, x: position.x, y: position.y, targetId: target.id };
        const key = happoActionKey(action);
        if (!seen.has(key)) { seen.add(key); actions.push(action); }
      }
      if (position.x !== actor.x || position.y !== actor.y) {
        const action = { type: 1, x: position.x, y: position.y, targetId: null };
        const key = happoActionKey(action);
        if (!seen.has(key)) { seen.add(key); actions.push(action); }
      }
      if (actions.length >= 255) break;
    }
    const wait = { type: 0, x: actor.x, y: actor.y, targetId: null };
    if (!seen.has(happoActionKey(wait)) && actions.length < 256) actions.push(wait);
    return actions.slice(0, 256);
  }

  function happoActionKey(action) {
    return `${action.type}:${action.x}:${action.y}:${action.targetId || "-"}`;
  }

  function canAttackAt(actor, position, target) {
    return canAttack({ ...actor, x: position.x, y: position.y }, target);
  }

  function buildHappoLocal(actor) {
    const [width, height] = stageSize();
    const hero = heroById.get(actor.heroId);
    const stat = asList(hero?.stat || [70, 70, 70, 70, 70]);
    return [
      clamp(state.turn / Math.max(1, battleTurnLimit()), 0, 1), 1,
      clamp(width / 64, 0, 1), clamp(height / 64, 0, 1),
      1, 0, 0, 1, actor.hp > 0 ? 1 : 0, actor.acted ? 1 : 0,
      clamp(actor.x / Math.max(1, width - 1), 0, 1),
      clamp(actor.y / Math.max(1, height - 1), 0, 1),
      clamp(actor.hp / Math.max(1, actor.maxHp), 0, 1),
      clamp(actor.mp / Math.max(1, actor.maxMp), 0, 1),
      clamp(actor.power / 500, 0, 1), clamp(actor.defense / 500, 0, 1),
      clamp(Number(stat[2] || 0) / 500, 0, 1), clamp(Number(stat[3] || 0) / 500, 0, 1),
      clamp(Number(stat[4] || 0) / 500, 0, 1), clamp(actor.move / 20, 0, 1)
    ];
  }

  function buildHappoCandidates(actor, actions, opponents) {
    const [width, height] = stageSize();
    const attackTargets = actions.map((action) => action.targetId && getUnit(action.targetId)).filter(Boolean);
    const hpRatios = attackTargets.map((target) => target.hp / Math.max(1, target.maxHp));
    const defenses = attackTargets.map((target) => target.defense || 0);
    const spirits = attackTargets.map((target) => Number(heroById.get(target.heroId)?.stat?.[3] || 0));
    const hpMin = hpRatios.length ? Math.min(...hpRatios) : 0; const hpMax = hpRatios.length ? Math.max(...hpRatios) : 0;
    const defMin = defenses.length ? Math.min(...defenses) : 0; const defMax = defenses.length ? Math.max(...defenses) : 0;
    const spiritMin = spirits.length ? Math.min(...spirits) : 0; const spiritMax = spirits.length ? Math.max(...spirits) : 0;
    const isRanged = String(actor.attackRange || "").startsWith("Distance");
    const teamRangedShot = isRanged && actions.some((action) => action.type === 2);
    const readyRanged = activeUnits("enemy").filter((unit) => !unit.acted && String(unit.attackRange || "").startsWith("Distance"));

    return actions.flatMap((action) => {
      const target = action.targetId ? getUnit(action.targetId) : null;
      const base = Array(14).fill(0);
      base[clamp(action.type, 0, 3)] = 1;
      base[4] = action.x / Math.max(1, width - 1); base[5] = action.y / Math.max(1, height - 1);
      base[6] = manhattan(actor, action) / Math.max(1, width + height - 2);
      if (target) {
        base[7] = 1; base[8] = (target.x - action.x) / Math.max(1, width - 1);
        base[9] = (target.y - action.y) / Math.max(1, height - 1);
        base[10] = target.hp / Math.max(1, target.maxHp); base[11] = 1;
      }
      base[13] = 1;

      const tactical = Array(20).fill(0);
      tactical[clamp(action.type, 0, 3)] = 1;
      tactical[4] = target ? clamp(Math.max(0, actor.power - target.defense * .42) / 160, 0, 1) : 0;
      tactical[5] = isRanged ? 1 : 0; tactical[6] = isRanged ? 0 : 1;
      tactical[7] = actor.hp / Math.max(1, actor.maxHp);
      tactical[8] = target ? 1 - target.hp / Math.max(1, target.maxHp) : 0;
      const currentDistance = Math.min(...opponents.map((unit) => manhattan(actor, unit)));
      const destinationDistance = Math.min(...opponents.map((unit) => manhattan(action, unit)));
      const delta = (currentDistance - destinationDistance) / 12;
      tactical[9] = Math.max(0, delta); tactical[10] = Math.max(0, -delta);
      tactical[11] = opponents.some((unit) => canAttackAt(actor, action, unit)) ? 1 : 0;
      tactical[12] = teamRangedShot ? 1 : 0; tactical[13] = isRanged && action.type === 2 ? 1 : 0;
      tactical[14] = !isRanged && action.type === 2 ? 1 : 0;
      tactical[18] = readyRanged.some((unit) => unit.id !== actor.id && manhattan(actor, unit) <= 2) ? 1 : 0;
      tactical[19] = actor.hp < actor.maxHp * .35 ? 1 : 0;
      if (target) {
        const hp = target.hp / Math.max(1, target.maxHp); const defense = target.defense || 0;
        const spirit = Number(heroById.get(target.heroId)?.stat?.[3] || 0);
        tactical[6] = happoWeakness(hp, hpMin, hpMax); tactical[7] = happoWeakness(defense, defMin, defMax);
        tactical[8] = happoWeakness(spirit, spiritMin, spiritMax); tactical[12] = hp <= hpMin + 1e-6 ? 1 : 0;
        tactical[18] = defense <= defMin + 1e-6 ? 1 : 0; tactical[19] = spirit <= spiritMin + 1e-6 ? 1 : 0;
      }
      return [...base, ...tactical];
    });
  }

  function happoWeakness(value, minimum, maximum) {
    return maximum <= minimum ? .5 : (maximum - value) / (maximum - minimum);
  }

  async function runStageRules() {
    if (state.result || restoring) return;
    runtime.invoke("on_update");
    processStoryEvents();
    const status = runtime.invoke("end_condition");
    if (status === "victory") finish(true, stageRecord.story?.victory?.[0]?.text || "本关目标已经完成。");
    else if (status === "defeat") finish(false, stageRecord.story?.defeat?.[0]?.text || "我军未能完成本关目标。");
    else if (!activeUnits("enemy").length) finish(true, "敌军主力已退出战场。");
    else if (!activeUnits().some((unit) => unit.team !== "enemy")) finish(false, "我军与友军均已退出战场。");
    flushSpeeches();
  }

  function finish(won, text) {
    if (state.result) return;
    const terminalReason = classifyTerminalReason(won, text);
    state.result = { won, text, reason: terminalReason };
    state.phase = "ended";
    selectedId = null;
    selectedSkillId = null;
    reachable.clear();
    log(text, won ? "event" : "bad");
    const ownUnits = state.units.filter((unit) => unit.team === "own");
    const proceduralDecision = state.procedural?.decision;
    const progression = systems.completeBattle(profile, stageRecord, {
      stages: campaign.stages,
      won,
      turns: state.turn,
      turnLimit: battleTurnLimit(),
      totalOwn: state.initialOwnCount || ownUnits.length,
      totalEnemy: state.initialEnemyCount || state.units.filter((unit) => unit.team === "enemy").length,
      ownLosses: ownUnits.filter((unit) => unit.hp <= 0).length,
      supplies: state.stats.supplies,
      inventoryRemaining: state.inventory,
      ownHeroes: ownUnits.map((unit) => unit.heroId),
      difficulty: battleDifficulty(),
      policyDecisions: state.stats.policyDecisions,
      policyFallbacks: state.stats.policyFallbacks,
      terminalReason,
      durationMs: Date.now() - Number(state.startedAt || Date.now()),
      storySkipped: state.storySkipped,
      itemsUsed: state.itemsUsed,
      eventCounts: state.eventCounts,
      mapSeed: state.procedural?.seed,
      objectiveType: state.procedural?.objectiveType || "scripted",
      replay: {
        stage_id: stageRecord.id,
        started_at: state.startedAt,
        initial_units: state.replayInitial || [],
        events: state.eventLog || [],
        map_seed: state.procedural?.seed || null,
        difficulty: battleDifficulty()
      },
      decision: state.procedural ? {
        policyVersion: state.procedural.meta?.modelVersion || systems.POLICY_VERSION,
        action: state.procedural.difficulty,
        behaviorProbability: proceduralDecision?.behaviorProbability,
        fallbackReason: state.procedural.meta?.fallback ? state.procedural.meta?.reason || "template-fallback" : null
      } : { policyVersion: systems.POLICY_VERSION }
    });
    profile = progression.profile;
    state.result.progression = { firstClear: progression.firstClear, rankUps: progression.rankUps, reward: progression.reward, coinsEarned: progression.coinsEarned, masteryUpdates: progression.masteryUpdates };
    writeJson(PROFILE_KEY, profile);
    if (progression.rankUps) log(`军阶提升至 ${profile.armyRank}，全军基础战力提高。`, "event");
    if (progression.coinsEarned) log(`首通获得 ${progression.coinsEarned} 铜钱与军需补给。`, "event");
    for (const update of progression.masteryUpdates.filter((entry) => entry.xpEarned > 0)) {
      log(`${displayName(update.heroId)} 熟练度 +${update.xpEarned}${update.leveled ? `，升至 ${update.level} 级` : ""}`, "event");
    }
    feedback(won ? "victory" : "defeat");
    saveBattle(false);
    const ending = asList(won ? stageRecord.story?.victory : stageRecord.story?.defeat);
    if (ending.length) openStory(ending, showResult);
    else showResult();
  }

  function showResult() {
    if (!state?.result) return;
    $("#resultModal").hidden = false;
    $("#resultKicker").textContent = `${stageRecord.chapter} · ${stageRecord.battleTitle}`;
    $("#resultTitle").textContent = state.result.won ? "战役告捷" : "战局失利";
    $("#resultText").textContent = state.result.text;
    const reward = Number(state.result.progression?.reward?.total || 0);
    $("#resultStats").innerHTML = [
      ["用时", `${Math.min(state.turn, battleTurnLimit())} 回合`], ["击破", `${state.stats.defeated} 部`],
      ["战技", `${state.stats.skills} 次`], ["补给", `${state.stats.supplies} 处`],
      ["军阶", `${profile.armyRank}`], ["铜钱", `+${state.result.progression?.coinsEarned || 0}`],
      ["评估", `${Math.round(reward * 100)}`], ["难度", { easy: "简单", medium: "标准", hard: "艰难" }[battleDifficulty()] || "标准"]
    ].map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`).join("");
    const next = stageRecord.isProcedural ? null : campaign.stages[stageRecord.index];
    $("#resultNextButton").hidden = !next;
    renderCampaign();
  }

  function readBattleSave() {
    const saved = readJson(BATTLE_KEY, null);
    return saved && findStageRecord(saved.stageId) ? saved : null;
  }

  function saveBattle(announce = true) {
    if (!state || !stageRecord) return;
    writeJson(BATTLE_KEY, state);
    if (!stageRecord.isProcedural) {
      profile.lastStage = stageRecord.id;
      writeJson(PROFILE_KEY, profile);
    }
    if (announce) showNotice("战局已保存");
    $("#resumeButton").hidden = false;
  }

  function openStory(entries, onDone = null) {
    storyEntries = systems.normalizeStoryEntries(asList(entries), 110);
    if (!storyEntries.length) { onDone?.(); return; }
    storyIndex = 0;
    storyDone = onDone;
    $("#storyModal").hidden = false;
    renderStory();
  }

  function renderStory() {
    const entry = storyEntries[storyIndex];
    $("#storyChapter").textContent = stageRecord ? `${stageRecord.chapter} · ${stageRecord.title}` : "东周列国志";
    $("#storySpeaker").textContent = entry.speaker;
    $("#storyText").textContent = entry.text || "";
    $("#storyProgress").textContent = `${storyIndex + 1} / ${storyEntries.length}`;
    $("#storyNextButton").textContent = storyIndex === storyEntries.length - 1 ? "入阵" : "继续";
    $("#storyPortrait").src = `assets/${systems.portraitForSpeaker(entry.speaker)}`;
    playStoryVoice(entry);
  }

  function stopStoryVoice() {
    storyAudioSerial += 1;
    if (storyAudio) {
      storyAudio.pause();
      storyAudio.removeAttribute("src");
      storyAudio.load();
      storyAudio = null;
    }
    $("#storyVoiceReplayButton")?.classList.remove("is-playing");
  }

  function playStoryVoice(entry) {
    stopStoryVoice();
    const voice = systems.resolveStoryVoice(voiceManifest, entry?.speaker, entry?.text);
    const button = $("#storyVoiceReplayButton");
    button.hidden = !voice;
    button.disabled = !voice || !profile.settings.voiceEnabled;
    if (!voice || !profile.settings.voiceEnabled) return;

    const serial = storyAudioSerial;
    const cacheVersion = String(voice.sha256 || "").slice(0, 16);
    const audioSource = cacheVersion ? `${voice.file}?v=${cacheVersion}` : voice.file;
    const audio = new Audio(audioSource);
    storyAudio = audio;
    audio.preload = "auto";
    audio.volume = clamp(Number(profile.settings.voiceVolume ?? 0.85), 0, 1);
    button.classList.add("is-playing");
    const finish = () => {
      if (serial !== storyAudioSerial) return;
      button.classList.remove("is-playing");
      storyAudio = null;
    };
    audio.addEventListener("ended", finish, { once: true });
    audio.addEventListener("error", finish, { once: true });
    audio.play().catch(finish);
  }

  function advanceStory(skip = false) {
    if (skip && state) {
      state.storySkipped = true;
      recordEvent("story_skip", { at: storyIndex, total: storyEntries.length });
    }
    if (!skip && storyIndex < storyEntries.length - 1) { storyIndex++; renderStory(); return; }
    stopStoryVoice();
    $("#storyModal").hidden = true;
    const callback = storyDone;
    storyDone = null;
    callback?.();
  }

  function configureMobilePanels() {
    if (window.matchMedia("(max-width: 820px)").matches) {
      $("#intelPanel").classList.add("is-collapsed");
    }
    syncPanelToggle("rosterPanel", "rosterToggle", "我军阵容");
    syncPanelToggle("intelPanel", "intelToggle", "战场军情");
  }

  function togglePanel(panelId, toggleId, label) {
    $("#" + panelId).classList.toggle("is-collapsed");
    syncPanelToggle(panelId, toggleId, label);
  }

  function syncPanelToggle(panelId, toggleId, label) {
    const collapsed = $("#" + panelId).classList.contains("is-collapsed");
    const button = $("#" + toggleId);
    button.textContent = collapsed ? "＋" : "−";
    button.setAttribute("aria-expanded", String(!collapsed));
    button.setAttribute("aria-label", `${collapsed ? "展开" : "收起"}${label}`);
  }

  function updateUI() {
    if (!state || !stageRecord) return;
    $("#turnLabel").textContent = `第 ${Math.min(state.turn, battleTurnLimit())} / ${battleTurnLimit()} 回合`;
    const phaseText = { player: "我军行动", ally: "友军行动", enemy: "敌军行动", ended: "战役结束" }[state.phase] || "待命";
    $("#phaseBadge").textContent = phaseText;
    $("#phaseBadge").classList.toggle("enemy", state.phase === "enemy");
    $("#medicineCount").textContent = Number(state.inventory.medicine || 0);
    $("#spiritCount").textContent = Number(state.inventory.spirit_powder || 0);
    $("#enemyCount").textContent = `敌军 ${activeUnits("enemy").length}`;
    $("#ownCount").textContent = `${activeUnits("own").length} 部`;
    const selected = getUnit(selectedId);
    const skill = systems.skillForUnit(selected);
    $("#waitButton").disabled = !selected || selected.acted || state.phase !== "player" || enemyRunning;
    $("#medicineButton").disabled = !selected || selected.acted || state.phase !== "player" || Number(state.inventory.medicine || 0) <= 0 || enemyRunning;
    $("#spiritButton").disabled = !selected || selected.acted || state.phase !== "player" || Number(state.inventory.spirit_powder || 0) <= 0 || enemyRunning;
    $("#skillButton").disabled = !selected || !skill || selected.acted || state.phase !== "player" || enemyRunning || selected.mp < skill.cost;
    $("#skillButton").classList.toggle("active", Boolean(skill && selectedSkillId === skill.id));
    $("#skillName").textContent = skill?.name || "战技";
    $("#skillCost").textContent = skill ? `${skill.cost} 谋` : "--";
    $("#endTurnButton").disabled = state.phase !== "player" || enemyRunning || Boolean(state.result);
    renderRoster();
    renderDetail();
    renderLog();
    requestRender();
  }

  function renderRoster() {
    $("#roster").innerHTML = state.units.filter((unit) => unit.team === "own").map((unit) => {
      const ratio = Math.max(0, unit.hp / unit.maxHp);
      return `<button class="roster-card ${selectedId === unit.id ? "selected" : ""}" data-unit-id="${unit.id}" type="button" ${unit.hp <= 0 ? "disabled" : ""}>
        <img src="assets/${UNIT_IMAGES[unit.classId] || UNIT_IMAGES.Infantry}" alt=""><span><span class="roster-name"><span>${escapeHtml(unit.name)}</span><small>${unit.hp <= 0 ? "阵亡" : unit.acted ? "已行动" : CLASS_LABELS[unit.classId] || unit.classId}</small></span>
        <span class="health-track"><span class="health-fill ${ratio <= .25 ? "low" : ratio <= .5 ? "mid" : ""}" style="width:${ratio * 100}%"></span></span><span class="health-label">兵力 ${Math.max(0, unit.hp)} / ${unit.maxHp} · 谋略 ${unit.mp}/${unit.maxMp}</span></span></button>`;
    }).join("");
    document.querySelectorAll("[data-unit-id]").forEach((button) => button.addEventListener("click", () => selectUnit(getUnit(button.dataset.unitId))));
  }

  function renderDetail() {
    const unit = getUnit(inspectionId || selectedId);
    const container = $("#unitDetail");
    if (!unit) { container.className = "unit-detail empty"; container.innerHTML = '<div class="detail-placeholder">选择单位查看军情</div>'; return; }
    container.className = "unit-detail";
    const portrait = unit.classId === "King" || unit.classId === "Lord" ? "portrait-lord.png" : ["Strategist", "Support"].includes(unit.classId) ? "portrait-strategist.png" : "portrait-general.png";
    container.innerHTML = `<div class="detail-head"><img src="assets/${portrait}" alt=""><div><h3>${escapeHtml(unit.name)}</h3><p>${TEAM_LABELS[unit.team]} · ${CLASS_LABELS[unit.classId] || unit.classId}</p></div></div>
      <div class="detail-grid"><div><span>兵力</span><strong>${Math.max(0, unit.hp)} / ${unit.maxHp}</strong></div><div><span>谋略</span><strong>${unit.mp} / ${unit.maxMp}</strong></div><div><span>移动</span><strong>${unit.move}</strong></div><div><span>攻击</span><strong>${systems.effectivePower(unit)}</strong></div><div><span>防御</span><strong>${systems.effectiveDefense(unit)}</strong></div><div><span>等级</span><strong>${unit.level}</strong></div></div>`;
  }

  function renderLog() {
    $("#battleLog").innerHTML = state.logs.slice(-10).reverse().map((entry) => `<li class="${entry.tone || ""}">${escapeHtml(entry.text)}</li>`).join("");
  }

  function log(text, tone = "") {
    if (restoring || !state) return;
    state.logs.push({ text: String(text), tone });
    if (state.logs.length > 60) state.logs.shift();
  }

  function recordEvent(type, payload = {}) {
    if (!state || !profile.settings.telemetryEnabled) return;
    state.eventCounts[type] = Number(state.eventCounts[type] || 0) + 1;
    state.eventLog.push({ type, t_ms: Math.max(0, Date.now() - Number(state.startedAt || Date.now())), turn: state.turn, ...payload });
    if (state.eventLog.length > 500) state.eventLog.shift();
  }

  function classifyTerminalReason(won, text) {
    if (won) return "victory";
    if (/回合|超时|期限/.test(text)) return "turn-limit";
    if (/护送|保护|主将|不得被击退/.test(text)) return "protected-unit-lost";
    if (!activeUnits("own").length) return "army-defeated";
    return "objective-failed";
  }

  function beginTutorialOrBattle() {
    if (stageRecord?.index === 1 && !profile.tutorial.completed && !profile.tutorial.dismissed) {
      state.tutorialStep = Number(state.tutorialStep || 0);
      showNotice("演武一：选择一名我军将领");
    } else showNotice("我军回合 · 请下令");
  }

  function advanceTutorial(event) {
    if (stageRecord?.index !== 1 || profile.tutorial.completed || profile.tutorial.dismissed || !state) return;
    const step = Number(state.tutorialStep || 0);
    if (step === 0 && event === "select") { state.tutorialStep = 1; showNotice("演武二：移动，或直接攻击近旁敌军"); }
    else if (step === 1 && ["move", "action"].includes(event)) { state.tutorialStep = 2; showNotice("演武三：攻击、施放战技或使用军需"); }
    else if (step === 2 && event === "action") { state.tutorialStep = 3; showNotice("演武四：结束回合，让敌军行动"); }
    else if ((step >= 2 && event === "end_turn") || (step === 1 && event === "end_turn")) {
      profile.tutorial.completed = true;
      profile.coins += 60;
      writeJson(PROFILE_KEY, profile);
      showNotice("演武完成 · 获得 60 铜钱");
    }
  }

  function feedback(kind) {
    if (!profile.settings.feedbackEnabled) return;
    const vibrations = { attack: 24, skill: [18, 30, 36], heal: 16, victory: [25, 35, 60], defeat: [70, 40, 70] };
    try { navigator.vibrate?.(vibrations[kind] || 12); } catch (_) { /* unavailable */ }
    try {
      audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.type = kind === "defeat" ? "sawtooth" : "sine";
      oscillator.frequency.value = { attack: 150, skill: 420, heal: 560, victory: 660, defeat: 110 }[kind] || 240;
      gain.gain.setValueAtTime(.04, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(.001, audioContext.currentTime + .12);
      oscillator.connect(gain); gain.connect(audioContext.destination); oscillator.start(); oscillator.stop(audioContext.currentTime + .13);
    } catch (_) { /* feedback is optional */ }
  }

  function setStatus(text) { $("#statusText").textContent = text; }

  function showNotice(text) {
    const element = $("#floatingNotice");
    element.textContent = text;
    element.classList.add("show");
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => element.classList.remove("show"), 1800);
  }

  function requestRender() {
    if (renderQueued) return;
    renderQueued = true;
    requestAnimationFrame(() => { renderQueued = false; drawBoard(); });
  }

  function currentMapDetailProfile() {
    const compact = window.innerWidth <= 720 || cellPixels * mapZoom < 32;
    return systems.mapDetailProfile(profile.settings?.mapDetail, compact);
  }

  function drawStructuralMapDetail(target, cellW, cellH, padding, alpha) {
    let cells = 0;
    target.save();
    target.beginPath();
    terrainRows().forEach((row, y) => [...row].forEach((char, x) => {
      if (!systems.preservesMapDetail(char)) return;
      target.rect(x * cellW - padding, y * cellH - padding, cellW + padding * 2, cellH + padding * 2);
      cells++;
    }));
    if (cells) {
      target.clip();
      target.globalAlpha = alpha;
      target.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
    }
    target.restore();
  }

  function drawBarrierBoundaryDetail(target, cellW, cellH) {
    const rows = terrainRows();
    const thickness = Math.max(1, Math.min(cellW, cellH) * .075);
    let edges = 0;
    target.save();
    target.beginPath();
    rows.forEach((row, y) => [...row].forEach((char, x) => {
      if (!systems.isBarrierTerrain(char)) return;
      const neighbors = [
        [x - 1, y, x * cellW - thickness, y * cellH - thickness, thickness * 2, cellH + thickness * 2],
        [x + 1, y, (x + 1) * cellW - thickness, y * cellH - thickness, thickness * 2, cellH + thickness * 2],
        [x, y - 1, x * cellW - thickness, y * cellH - thickness, cellW + thickness * 2, thickness * 2],
        [x, y + 1, x * cellW - thickness, (y + 1) * cellH - thickness, cellW + thickness * 2, thickness * 2]
      ];
      for (const [nx, ny, rx, ry, rw, rh] of neighbors) {
        if (rows[ny]?.[nx] === char) continue;
        target.rect(rx, ry, rw, rh);
        edges++;
      }
    }));
    if (edges) {
      target.clip();
      target.globalAlpha = .55;
      target.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
    }
    target.restore();
  }

  function buildMapPresentation(detail, cellW, cellH) {
    const reduced = document.createElement("canvas");
    reduced.width = Math.max(1, Math.round(canvas.width * detail.scale));
    reduced.height = Math.max(1, Math.round(canvas.height * detail.scale));
    const reducedContext = reduced.getContext("2d");
    reducedContext.imageSmoothingEnabled = true;
    reducedContext.imageSmoothingQuality = "high";
    reducedContext.drawImage(mapImage, 0, 0, reduced.width, reduced.height);

    const composed = document.createElement("canvas");
    composed.width = canvas.width;
    composed.height = canvas.height;
    const composedContext = composed.getContext("2d");
    composedContext.imageSmoothingEnabled = true;
    composedContext.imageSmoothingQuality = "high";
    composedContext.filter = `saturate(${detail.saturation * 100}%) contrast(${detail.contrast * 100}%) brightness(${detail.brightness * 100}%)`;
    composedContext.drawImage(reduced, 0, 0, canvas.width, canvas.height);
    composedContext.filter = "none";

    drawBarrierBoundaryDetail(composedContext, cellW, cellH);
    const feather = Math.max(1, Math.min(cellW, cellH) * .035);
    drawStructuralMapDetail(composedContext, cellW, cellH, feather, .28);
    drawStructuralMapDetail(composedContext, cellW, cellH, 0, 1);
    return composed;
  }

  function drawStageMap(cellW, cellH) {
    const detail = currentMapDetailProfile();
    canvas.dataset.mapDetail = detail.mode;
    canvas.dataset.mapDetailScale = String(detail.scale);
    if (detail.mode === "original") {
      ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
      return;
    }
    const cacheKey = [stageRecord.id, canvas.width, canvas.height, detail.mode, detail.scale, detail.saturation, detail.contrast].join(":");
    if (!mapPresentationCanvas || mapPresentationKey !== cacheKey) {
      mapPresentationCanvas = buildMapPresentation(detail, cellW, cellH);
      mapPresentationKey = cacheKey;
    }
    ctx.drawImage(mapPresentationCanvas, 0, 0);
  }

  function drawBoard() {
    if (!state || !stageRecord) return;
    const [width, height] = stageSize();
    const cellW = canvas.width / width; const cellH = canvas.height / height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!state.procedural && mapImage.complete && mapImage.naturalWidth) drawStageMap(cellW, cellH);
    else { drawTerrainBase(cellW, cellH); drawTerrainSemantics(cellW, cellH); }
    drawBlockedTerrain(cellW, cellH);
    drawReachable(cellW, cellH);
    drawSites(cellW, cellH);
    drawGrid(cellW, cellH, width, height);
    drawBoardCursor(cellW, cellH);
    for (const unit of activeUnits()) drawUnit(unit, cellW, cellH);
  }

  function drawTerrainBase(cellW, cellH) {
    const colors = { f: "#7d8b58", g: "#6f8756", F: "#405d40", w: "#887857", m: "#625f50", r: "#464a43", W: "#69675e", "~": "#456f83", v: "#6f98a2", e: "#8d6840", c: "#7e664b", b: "#9a784d", i: "#8b806d", h: "#88765e", C: "#615b55", G: "#765f46", P: "#655e4e" };
    terrainRows().forEach((row, y) => [...row].forEach((char, x) => { ctx.fillStyle = colors[char] || "#77745f"; ctx.fillRect(x * cellW, y * cellH, cellW, cellH); }));
  }

  function drawTerrainSemantics(cellW, cellH) {
    ctx.save();
    terrainRows().forEach((row, y) => [...row].forEach((char, x) => {
      const cx = (x + .5) * cellW; const cy = (y + .5) * cellH;
      ctx.strokeStyle = "rgba(239,237,205,.42)"; ctx.fillStyle = "rgba(24,33,25,.42)"; ctx.lineWidth = Math.max(1, cellW * .025);
      if (["~", "v"].includes(char)) {
        ctx.beginPath(); ctx.arc(cx - cellW * .1, cy, cellW * .12, Math.PI, 0); ctx.arc(cx + cellW * .14, cy, cellW * .12, Math.PI, 0); ctx.stroke();
      } else if (["F", "g"].includes(char) && (x + y) % 2 === 0) {
        ctx.beginPath(); ctx.moveTo(cx, cy - cellH * .18); ctx.lineTo(cx - cellW * .14, cy + cellH * .12); ctx.lineTo(cx + cellW * .14, cy + cellH * .12); ctx.closePath(); ctx.fill(); ctx.stroke();
      } else if (["m", "r"].includes(char)) {
        ctx.beginPath(); ctx.moveTo(cx - cellW * .2, cy + cellH * .16); ctx.lineTo(cx, cy - cellH * .2); ctx.lineTo(cx + cellW * .2, cy + cellH * .16); ctx.stroke();
      } else if (["C", "G", "P"].includes(char)) {
        ctx.strokeRect(cx - cellW * .16, cy - cellH * .14, cellW * .32, cellH * .28);
        ctx.beginPath(); ctx.moveTo(cx, cy - cellH * .14); ctx.lineTo(cx, cy - cellH * .3); ctx.stroke();
      }
    }));
    ctx.restore();
  }

  function drawBoardCursor(cellW, cellH) {
    if (!boardCursor || document.activeElement !== canvas) return;
    ctx.save(); ctx.strokeStyle = "#fff2a8"; ctx.lineWidth = Math.max(3, cellW * .07); ctx.setLineDash([Math.max(5, cellW * .16), Math.max(3, cellW * .08)]);
    ctx.strokeRect(boardCursor.x * cellW + 3, boardCursor.y * cellH + 3, cellW - 6, cellH - 6); ctx.restore();
  }

  function announceBoardCursor() {
    if (!boardCursor) return;
    const unit = unitAt(boardCursor.x, boardCursor.y);
    const terrainNames = { f: "平地", g: "草地", F: "林地", w: "荒地", m: "山地", r: "岩地", W: "城墙", "~": "河流", v: "浅滩", C: "城池", G: "关门", P: "宫城" };
    const terrain = terrainNames[terrainRows()[boardCursor.y]?.[boardCursor.x]] || "地形";
    $("#boardAnnouncement").textContent = `第 ${boardCursor.x + 1} 列，第 ${boardCursor.y + 1} 行，${terrain}${unit ? `，${TEAM_LABELS[unit.team]}${unit.name}，兵力 ${unit.hp}` : "，空格"}`;
    requestRender();
  }

  function drawBlockedTerrain(cellW, cellH) {
    terrainRows().forEach((row, y) => [...row].forEach((char, x) => {
      if (!["r", "W", "~", "P"].includes(char)) return;
      ctx.fillStyle = "rgba(8,10,8,.2)"; ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
    }));
  }

  function drawReachable(cellW, cellH) {
    const selected = getUnit(selectedId);
    if (!selected || selected.acted || state.phase !== "player") return;
    if (selectedSkillId) {
      const skill = systems.skillForUnit(selected);
      ctx.fillStyle = "rgba(214,166,62,.45)";
      for (const unit of activeUnits().filter((target) => systems.skillTargetValid(selected, target, skill))) {
        ctx.fillRect(unit.x * cellW + 2, unit.y * cellH + 2, cellW - 4, cellH - 4);
      }
      return;
    }
    ctx.fillStyle = "rgba(54,174,92,.34)";
    for (const point of reachable.values()) ctx.fillRect(point.x * cellW + 2, point.y * cellH + 2, cellW - 4, cellH - 4);
    ctx.fillStyle = "rgba(204,55,43,.43)";
    for (const unit of activeUnits().filter((target) => canAttack(selected, target))) ctx.fillRect(unit.x * cellW + 2, unit.y * cellH + 2, cellW - 4, cellH - 4);
  }

  function drawSites(cellW, cellH) {
    for (const site of asList(stageRecord.sites)) {
      const position = asList(site.position); const claimed = state.claimedSites.includes(site.id);
      const cx = (position[0] + .5) * cellW; const cy = (position[1] + .5) * cellH; const size = Math.min(cellW, cellH) * .17;
      ctx.save(); ctx.translate(cx, cy); ctx.rotate(Math.PI / 4); ctx.fillStyle = claimed ? "#77786d" : "#dfb84a"; ctx.strokeStyle = "#fff0a6"; ctx.lineWidth = 2;
      ctx.fillRect(-size, -size, size * 2, size * 2); ctx.strokeRect(-size, -size, size * 2, size * 2); ctx.restore();
    }
  }

  function drawGrid(cellW, cellH, width, height) {
    const gridAlpha = currentMapDetailProfile().gridAlpha;
    ctx.beginPath(); ctx.strokeStyle = `rgba(255,246,207,${gridAlpha})`; ctx.lineWidth = 1;
    for (let x = 0; x <= width; x++) { ctx.moveTo(x * cellW, 0); ctx.lineTo(x * cellW, canvas.height); }
    for (let y = 0; y <= height; y++) { ctx.moveTo(0, y * cellH); ctx.lineTo(canvas.width, y * cellH); }
    ctx.stroke();
    ctx.beginPath(); ctx.strokeStyle = "rgba(44,28,18,.75)"; ctx.lineWidth = Math.max(3, cellW * .08);
    for (const edge of asList(stageRecord.stage.map.blocked_edges)) {
      const from = asList(edge.from); const to = asList(edge.to);
      const mx = (from[0] + to[0] + 1) * cellW / 2; const my = (from[1] + to[1] + 1) * cellH / 2;
      if (from[0] === to[0]) { ctx.moveTo(from[0] * cellW, my); ctx.lineTo((from[0] + 1) * cellW, my); }
      else { ctx.moveTo(mx, from[1] * cellH); ctx.lineTo(mx, (from[1] + 1) * cellH); }
    }
    ctx.stroke();
  }

  function drawUnit(unit, cellW, cellH) {
    const cx = (unit.x + .5) * cellW; const cy = (unit.y + .5) * cellH; const radius = Math.min(cellW, cellH) * .36;
    const colors = { own: ["#8f3028", "#e28b77"], ally: ["#8a6a24", "#e4c66d"], enemy: ["#2e577e", "#79a7d2"] }[unit.team];
    const haloAlpha = currentMapDetailProfile().unitHalo;
    ctx.save(); ctx.fillStyle = `rgba(246,237,205,${haloAlpha})`; ctx.strokeStyle = "rgba(18,14,9,.72)"; ctx.lineWidth = Math.max(2, radius * .09);
    ctx.beginPath(); ctx.arc(cx, cy, radius * 1.17, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = radius * .22; ctx.fillStyle = colors[0];
    ctx.strokeStyle = selectedId === unit.id ? "#ffe291" : inspectionId === unit.id ? "#fff3cc" : colors[1]; ctx.lineWidth = selectedId === unit.id ? 5 : 3;
    ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); ctx.restore();
    const image = getImage(UNIT_IMAGES[unit.classId] || UNIT_IMAGES.Infantry);
    if (image.complete && image.naturalWidth) { const size = radius * 1.38; ctx.drawImage(image, cx - size / 2, cy - size / 2, size, size); }
    const ratio = Math.max(0, unit.hp / unit.maxHp); const barW = cellW * .74; const barH = Math.max(4, cellH * .07); const barX = cx - barW / 2; const barY = (unit.y + .88) * cellH;
    ctx.fillStyle = "rgba(8,10,8,.9)"; ctx.fillRect(barX, barY, barW, barH); ctx.fillStyle = ratio > .5 ? "#6ca461" : ratio > .25 ? "#c19442" : "#b7483f"; ctx.fillRect(barX + 1, barY + 1, Math.max(0, (barW - 2) * ratio), barH - 2);
    if (cellW >= 42 || selectedId === unit.id || inspectionId === unit.id) {
      ctx.font = `700 ${Math.max(10, Math.floor(cellW * .18))}px "Microsoft YaHei", sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.lineWidth = 3; ctx.strokeStyle = "rgba(8,10,8,.85)";
      const label = unit.name.length > 6 ? unit.name.slice(0, 6) : unit.name; ctx.strokeText(label, cx, (unit.y + .12) * cellH); ctx.fillStyle = "#fff8e6"; ctx.fillText(label, cx, (unit.y + .12) * cellH);
    }
    if (unit.acted && unit.team === "own") { ctx.fillStyle = "rgba(8,10,8,.42)"; ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); }
    if (unit.invulnerable) { ctx.strokeStyle = "rgba(255,226,130,.9)"; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, radius * 1.12, 0, Math.PI * 2); ctx.stroke(); }
  }

  function updateZoom(delta = 0) {
    mapZoom = clamp(mapZoom + delta, .5, 1.6);
    canvas.style.width = `${canvas.width * mapZoom}px`;
    canvas.style.height = `${canvas.height * mapZoom}px`;
    $("#zoomLabel").textContent = `${Math.round(mapZoom * 100)}%`;
  }

  function centerOnOwnArmy() {
    const units = activeUnits("own");
    if (!units.length) return;
    const frame = $("#battleFrame"); const [width, height] = stageSize();
    const x = units.reduce((sum, unit) => sum + unit.x, 0) / units.length; const y = units.reduce((sum, unit) => sum + unit.y, 0) / units.length;
    frame.scrollLeft = x / width * canvas.clientWidth - frame.clientWidth / 2;
    frame.scrollTop = y / height * canvas.clientHeight - frame.clientHeight / 2;
  }

  function syncCampaignSettings() {
    $("#campaignDifficulty").value = profile.settings.battleDifficulty;
    $("#mapDetailSetting").value = profile.settings.mapDetail;
    $("#telemetryToggle").checked = profile.settings.telemetryEnabled && profile.difficultyBandit.enabled;
    $("#feedbackToggle").checked = profile.settings.feedbackEnabled;
    $("#voiceToggle").checked = profile.settings.voiceEnabled;
    $("#voiceVolume").value = Math.round(profile.settings.voiceVolume * 100);
  }

  function exportTelemetry() {
    const payload = {
      schema_version: systems.TELEMETRY_SCHEMA,
      exported_at: new Date().toISOString(),
      runtime_version: systems.RUNTIME_VERSION,
      policy_version: systems.POLICY_VERSION,
      difficulty_bandit: profile.difficultyBandit,
      difficulty_calibration: systems.difficultyCalibration(profile),
      battles: profile.battleHistory,
      replays: profile.replays
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `dongzhou-battle-data-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function clearLearningData() {
    if (!window.confirm("清除本机战斗记录与难度学习参数？关卡进度和军阶会保留。")) return;
    profile.battleHistory = [];
    profile.replays = [];
    delete profile.difficultyBandit;
    profile = systems.normalizeProfile(profile, campaign.stages);
    writeJson(PROFILE_KEY, profile);
    syncCampaignSettings();
    showNotice("本地学习数据已清除");
  }

  function attachEvents() {
    canvas.addEventListener("click", handleBoardClick);
    canvas.addEventListener("focus", announceBoardCursor);
    canvas.addEventListener("keydown", async (event) => {
      if (!state || !boardCursor) return;
      const [width, height] = stageSize();
      const delta = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
      if (delta) {
        event.preventDefault();
        boardCursor.x = clamp(boardCursor.x + delta[0], 0, width - 1);
        boardCursor.y = clamp(boardCursor.y + delta[1], 0, height - 1);
        announceBoardCursor();
      } else if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        await handleBoardCell(boardCursor.x, boardCursor.y);
        announceBoardCursor();
      }
    });
    canvas.addEventListener("pointerdown", (event) => { dragStart = { x: event.clientX, y: event.clientY, left: $("#battleFrame").scrollLeft, top: $("#battleFrame").scrollTop }; dragged = false; canvas.setPointerCapture(event.pointerId); });
    canvas.addEventListener("pointermove", (event) => { if (!dragStart) return; const dx = event.clientX - dragStart.x; const dy = event.clientY - dragStart.y; if (Math.abs(dx) + Math.abs(dy) > 8) dragged = true; if (dragged) { $("#battleFrame").scrollLeft = dragStart.left - dx; $("#battleFrame").scrollTop = dragStart.top - dy; } });
    canvas.addEventListener("pointerup", () => { dragStart = null; setTimeout(() => { dragged = false; }, 0); });
    $("#campaignButton").addEventListener("click", openCampaign);
    $("#homeButton").addEventListener("click", openCampaign);
    $("#stageSearch").addEventListener("input", renderCampaign);
    $("#stageRange").addEventListener("change", renderCampaign);
    $("#resumeButton").addEventListener("click", () => { const saved = readBattleSave(); if (saved) startStage(saved.stageId, saved); });
    $("#focusStageButton").addEventListener("click", (event) => {
      const saved = event.currentTarget.dataset.saved === "true" ? readBattleSave() : null;
      startStage(event.currentTarget.dataset.stageId, saved);
    });
    $("#focusArchiveButton").addEventListener("click", () => $("#campaignArchive").scrollIntoView({ behavior: "smooth", block: "start" }));
    $("#proceduralButton").addEventListener("click", startProceduralStage);
    $("#proceduralMode").addEventListener("change", syncProceduralButton);
    $("#exerciseMenuButton").addEventListener("click", () => setExerciseMenu($("#exercisePanel").hidden));
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".exercise-menu")) setExerciseMenu(false);
    });
    $("#campaignDifficulty").addEventListener("change", (event) => {
      profile.settings.battleDifficulty = event.currentTarget.value;
      writeJson(PROFILE_KEY, profile);
      renderCampaign();
    });
    $("#mapDetailSetting").addEventListener("change", (event) => {
      profile.settings.mapDetail = event.currentTarget.value;
      mapPresentationCanvas = null;
      mapPresentationKey = "";
      writeJson(PROFILE_KEY, profile);
      requestRender();
    });
    $("#telemetryToggle").addEventListener("change", (event) => {
      profile.settings.telemetryEnabled = event.currentTarget.checked;
      profile.difficultyBandit.enabled = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
    });
    $("#feedbackToggle").addEventListener("change", (event) => {
      profile.settings.feedbackEnabled = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
    });
    $("#voiceToggle").addEventListener("change", (event) => {
      profile.settings.voiceEnabled = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
      if (!profile.settings.voiceEnabled) stopStoryVoice();
      else if (!$("#storyModal").hidden) playStoryVoice(storyEntries[storyIndex]);
    });
    $("#voiceVolume").addEventListener("input", (event) => {
      profile.settings.voiceVolume = clamp(Number(event.currentTarget.value) / 100, 0, 1);
      if (storyAudio) storyAudio.volume = profile.settings.voiceVolume;
      writeJson(PROFILE_KEY, profile);
    });
    window.addEventListener("resize", () => {
      mapPresentationCanvas = null;
      mapPresentationKey = "";
      requestRender();
    });
    document.querySelectorAll("[data-buy-supply]").forEach((button) => button.addEventListener("click", () => handleSupplyPurchase(button.dataset.buySupply)));
    $("#exportTelemetryButton").addEventListener("click", exportTelemetry);
    $("#clearLearningButton").addEventListener("click", clearLearningData);
    $("#saveButton").addEventListener("click", () => saveBattle(true));
    $("#storyReplayButton").addEventListener("click", () => {
      const intro = asList(stageRecord?.story?.intro);
      if (intro.length) openStory(intro);
    });
    $("#restartButton").addEventListener("click", () => { if (state) $("#confirmModal").hidden = false; });
    $("#cancelRestartButton").addEventListener("click", () => { $("#confirmModal").hidden = true; });
    $("#confirmRestartButton").addEventListener("click", () => startStage(stageRecord.id, null, state?.procedural ? { procedural: state.procedural } : {}));
    $("#storyNextButton").addEventListener("click", () => advanceStory(false));
    $("#storySkipButton").addEventListener("click", () => advanceStory(true));
    $("#storyHomeButton").addEventListener("click", openCampaign);
    $("#storyVoiceReplayButton").addEventListener("click", () => playStoryVoice(storyEntries[storyIndex]));
    $("#medicineButton").addEventListener("click", useMedicine);
    $("#spiritButton").addEventListener("click", useSpiritPowder);
    $("#skillButton").addEventListener("click", toggleSkill);
    $("#waitButton").addEventListener("click", waitSelected);
    $("#endTurnButton").addEventListener("click", endPlayerTurn);
    $("#zoomOutButton").addEventListener("click", () => updateZoom(-.1));
    $("#zoomInButton").addEventListener("click", () => updateZoom(.1));
    $("#resultCampaignButton").addEventListener("click", openCampaign);
    $("#resultNextButton").addEventListener("click", () => { const next = stageRecord.isProcedural ? null : campaign.stages[stageRecord.index]; if (next) startStage(next.id); });
    $("#rosterToggle").addEventListener("click", () => togglePanel("rosterPanel", "rosterToggle", "我军阵容"));
    $("#intelToggle").addEventListener("click", () => togglePanel("intelPanel", "intelToggle", "战场军情"));
    window.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (!$("#exercisePanel").hidden) setExerciseMenu(false);
      else if (!$("#storyModal").hidden) advanceStory(true);
      else if (selectedSkillId) { selectedSkillId = null; updateUI(); }
    });
  }

  boot();
})();
