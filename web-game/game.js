(() => {
  "use strict";

  const PROFILE_KEY = "dongzhou-h5-profile-v2";
  const BATTLE_KEY = "dongzhou-h5-battle-v2";
  const PREPARATION_JOURNAL_KEY = "dongzhou-preparation-journal-v1";
  const systems = window.DongzhouGameSystems;
  const organization = window.DongzhouOrganizationPlay;
  const integration = window.DongzhouIntegration;
  window.addEventListener("dongzhou-save-conflict", () => showNotice("云端存档已在其他页面更新，本页已停止写入以保护进度。"));
  window.addEventListener("dongzhou-save-committed", (event) => {
    if (!event.detail?.battleReceiptsChanged) return;
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    if (!$("#campaignOfficeBackdrop")?.hidden) renderOrganizationPanel();
  });
  const $ = (selector) => document.querySelector(selector);
  const asList = (value) => Array.isArray(value) ? value : Object.keys(value || {}).sort((a, b) => Number(a) - Number(b)).map((key) => value[key]);
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const pointKey = (x, y) => `${x},${y}`;

  const KNOWN_NAMES = {
    DuBo: "杜伯", ZuoRu: "左儒", ZhouXuanWang: "周宣王", YinJiFu: "尹吉甫", ZhaoHu: "召虎",
    RoyalGuard: "王城卫士", ZhouYouWang: "周幽王", GuoShiFu: "虢石父", ZhengHuanGong: "郑桓公", ZhengWuGong: "郑武公", ZhengZhuangGong: "郑庄公",
    GongZiCheng3: "公子成", GongZiLu: "公子吕", ZhengVanguard: "郑军先锋", ZhengVanguard2: "郑军先锋", QinXiangGong: "秦襄公",
    ShenHou: "申侯", QuanRongLord: "犬戎主将", QuanRongWarrior: "犬戎武士", QuanRongArcher: "犬戎弓手",
    JinLiGong58: "晋厉公", LuanShu58: "栾书", ShiXie58: "士燮", HanJue48: "韩厥", XiQi58: "郤锜",
    XiZhi58: "郤至", XunYing54: "荀罃", QinHuanGongMasui: "秦桓公", ChengChaMasui: "成差",
    NvFuMasui: "不更女父", QinMasuiGuard: "秦军卫士", QinMasuiArcher: "秦军弓手"
    , KuangZhang91: "匡章", GongSunXiChuisha: "公孙喜", BaoYuanChuisha: "暴鸢", TangMieChuisha: "唐蔑"
    , QiHanWeiGuard: "联军甲士", QiHanWeiArcher: "联军弓手", ChuishaGuard: "楚军甲士", ChuishaArcher: "楚军弓手"
  };
  const CLASS_LABELS = { Lord: "君主", King: "王者", Infantry: "步兵", Cavalry: "骑兵", Archer: "弓兵", Strategist: "军师", Support: "辅臣" };
  const UNIT_IMAGES = {
    Lord: "unit-lord.png", King: "unit-lord.png", Infantry: "unit-infantry-red.svg", Cavalry: "unit-cavalry.png",
    Archer: "unit-archer.png", Strategist: "unit-strategist.png", Support: "unit-strategist.png"
  };
  const TEAM_LABELS = { own: "我军", ally: "友军", enemy: "敌军" };

  let campaign;
  let config;
  let pcgrlTemplate;
  let mapElitesTemplate;
  let mapElitesArchive;
  let difficultyProfiles = { profiles: {} };
  let voiceManifest = { entries: [] };
  let musicManifest = { cues: [] };
  let runtime;
  let npcInteractionPreferenceState = integration.isOffline() ? "offline" : "pending";
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
  let storyMusicContext = {};
  let musicAudio = null;
  let musicCueId = "";
  let musicSerial = 0;
  let musicDucked = false;
  let replaySelection = null;
  let animationSerial = 0;
  const unitAnimations = new Map();
  const imageCache = new Map();
  const syncedNpcIds = new Set();
  const warmedNpcScheduleIds = new Set();
  const officeAssignmentSnapshots = new Map();
  const campaignRoutePlans = new Map();
  let campaignRouteSerial = 0;
  let routeStartPending = false;
  let officeNpcSyncQueue = Promise.resolve();
  let officeNpcRefreshTimer = null;
  let officeNpcRefreshSerial = 0;
  let officeMemoryView = [];
  let officeSelectedMemory = null;
  let officeInventoryView = null;
  let officeInventoryRequisitionBusy = false;
  let officeMembershipLeavePending = false;
  let officeMembershipBusy = false;
  let officeCareerBusy = false;
  let officeQuizInFlight = false;
  let officeQuizTimer = null;

  const canvas = $("#battleCanvas");
  const ctx = canvas.getContext("2d");

  function readJson(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch (_) { return fallback; }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
    if (key === PROFILE_KEY && integration) {
      const consumed = [...(value.organization?.consumedSupportTransactions || [])];
      integration.persist(value).then(() => acknowledgePreparation(consumed)).catch((error) => console.error("server save failed", error));
    }
  }

  function acknowledgePreparation(consumed) {
    const journal = readJson(PREPARATION_JOURNAL_KEY, {});
    for (const id of consumed) delete journal[id];
    localStorage.setItem(PREPARATION_JOURNAL_KEY, JSON.stringify(journal));
  }

  async function recoverPreparation() {
    const journal = readJson(PREPARATION_JOURNAL_KEY, {});
    const battle = readJson(BATTLE_KEY, null);
    const consumed = new Set(profile.organization.consumedSupportTransactions || []);
    const consumedSupportIds = new Set(profile.organization.consumedSupportIds || []);
    let pending = false;
    for (const [id, entry] of Object.entries(journal)) {
      // A prepared journal is committed only when its battle actually reached storage.
      if (!entry.committed && battle?.organizationSupportTransaction !== id) {
        delete journal[id];
        continue;
      }
      pending = true;
      if (consumed.has(id)) continue;
      const ids = new Set(entry.supportIds);
      // A second tab can journal the same preparation under another transaction ID.
      // Only rewards still present in the authoritative profile may be credited.
      const available = profile.organization.pendingSupport.filter(item => ids.has(item.id) && !consumedSupportIds.has(item.id));
      profile.organization.pendingSupport = profile.organization.pendingSupport.filter(item => !ids.has(item.id));
      profile.campaignResources.provisions = clamp(profile.campaignResources.provisions + available.reduce((sum, item) => sum + Number(item.provisions || 0), 0), 0, 200);
      profile.campaignResources.morale = clamp(profile.campaignResources.morale + available.reduce((sum, item) => sum + Number(item.morale || 0), 0), 0, 100);
      for (const supportId of ids) consumedSupportIds.add(supportId);
      consumed.add(id);
    }
    localStorage.setItem(PREPARATION_JOURNAL_KEY, JSON.stringify(journal));
    profile.organization.consumedSupportTransactions = [...consumed];
    profile.organization.consumedSupportIds = [...consumedSupportIds];
    if (pending) {
      // Do not open gameplay against a stale cloud profile when recovery cannot save.
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      await integration.persist(profile);
      acknowledgePreparation([...consumed]);
    }
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

  function unitImageFor(unit) {
    const model = String(unit?.model || heroById.get(unit?.heroId)?.model || "").toLowerCase();
    if (model.includes("infantry")) return model.endsWith("blue") ? "unit-infantry-blue.svg" : model.endsWith("red") ? "unit-infantry-red.svg" : unit?.team === "enemy" ? "unit-infantry-blue.svg" : "unit-infantry-red.svg";
    if (model.includes("cavalry")) return "unit-cavalry.png";
    if (model.includes("archer")) return "unit-archer.png";
    if (model.includes("strategist") || model.includes("support")) return "unit-strategist.png";
    if (model.includes("lord")) return "unit-lord.png";
    return UNIT_IMAGES[unit?.classId] || UNIT_IMAGES.Infantry;
  }

  async function boot() {
    try {
      setLoading(12, "正在校验列国谱系");
      [campaign, config, pcgrlTemplate, mapElitesTemplate, mapElitesArchive, voiceManifest, musicManifest, difficultyProfiles] = await Promise.all([
        fetch("scenario/campaign.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/config.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/pcgrl-masui.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/map-elites-chuisha.json").then(checkResponse).then((response) => response.json()),
        fetch("scenario/map-elites-chuisha.archive.json").then(checkResponse).then((response) => response.json()),
        fetch("audio/dialogue-manifest.json?v=20261106-context7-anchored").then(checkResponse).then((response) => response.json())
          .catch(() => ({ schemaVersion: 1, entries: [] })),
        fetch("audio/context-music-manifest.json?v=20261105-context3-diegetic").then(checkResponse).then((response) => response.json())
          .catch(() => ({ schemaVersion: 1, cues: [] })),
        fetch("scenario/difficulty-profiles.json").then(checkResponse).then((response) => response.json())
          .catch(() => ({ schemaVersion: 1, profiles: {} }))
      ]);
      voiceManifest = systems.normalizeVoiceManifest(voiceManifest);
      musicManifest = systems.normalizeMusicManifest(musicManifest);
      setLoading(54, "正在装载战役规则");
      heroById = new Map(asList(config.heroes).map((hero) => [hero.id, hero]));
      classById = new Map(asList(config.unit_classes).map((entry) => [entry.id, entry]));
      terrainByChar = new Map(asList(config.terrains).map((entry, index) => [entry.char, index]));
      profile = systems.normalizeProfile(profile, campaign.stages);
      profile.organization = organization.normalizeState(profile.organization);
      const integrated = await integration.initialize(profile);
      profile = systems.normalizeProfile(integrated.profile, campaign.stages);
      profile.organization = organization.normalizeState(profile.organization);
      await recoverOfficeInventoryRequisition();
      if (!integration.isOffline()) {
        try {
          const preference = await integration.setNpcInteractionPreference(profile.settings.aiNpcInteractionEnabled);
          if (preference.enabled !== profile.settings.aiNpcInteractionEnabled) throw new Error("NPC interaction preference was not applied");
          npcInteractionPreferenceState = "synced";
        } catch (error) {
          if (!profile.settings.aiNpcInteractionEnabled) throw error;
          npcInteractionPreferenceState = "deferred";
          console.warn("NPC interaction preference sync deferred", error);
        }
      }
      await recoverPreparation();
      writeJson(PROFILE_KEY, profile);
      runtime = new DongzhouLuaRuntime(campaign);
      await runtime.init();
      attachEvents();
      configureMobilePanels();
      buildRangeOptions();
      syncCampaignSettings();
      refreshIntegrationStatus();
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
    const groups = [
      { value: "all", label: "全部战役" },
      { value: "1-4", label: "西周余晖 · 第 1 - 4 战" },
      { value: "5-141", label: "春秋列国 · 第 5 - 141 战" },
      { value: "142-172", label: "战国风云 · 第 142 - 172 战" }
    ];
    for (let start = 1; start <= campaign.stageCount; start += 25) {
      groups.push({ value: `${start}-${Math.min(start + 24, campaign.stageCount)}`, label: `第 ${start} - ${Math.min(start + 24, campaign.stageCount)} 战` });
    }
    select.innerHTML = groups.map((item) => `<option value="${item.value}">${item.label}</option>`).join("");
  }

  function renderCampaign() {
    profile = systems.normalizeProfile(profile, campaign.stages);
    profile.organization = organization.normalizeState(profile.organization);
    const query = $("#stageSearch").value.trim().toLowerCase();
    const range = $("#stageRange").value || "all";
    const [start, end] = range === "all" ? [1, campaign.stageCount] : range.split("-").map(Number);
    const completed = new Set(profile.completed || []);
    const stages = campaign.stages.filter((record) => {
      if (record.index < start || record.index > end) return false;
      if (!query) return true;
      return [record.id, record.chapter, record.title, record.battleTitle, record.objective].join(" ").toLowerCase().includes(query);
    });
    let previousEra = "";
    $("#stageGrid").innerHTML = stages.map((record) => {
      const unlocked = systems.isStageUnlocked(record, profile, campaign.stages);
      const recommendedLevel = systems.recommendedStageLevel(record.index);
      const underleveled = profile.armyRank < recommendedLevel;
      const assist = systems.retryAssist(profile, record.id);
      const turnLimit = systems.effectiveTurnLimit(record.turnLimit, profile.settings.battleDifficulty, assist.active);
      const assessment = assessStage(record);
      const riskLabel = difficultyRiskLabel(assessment);
      const era = campaignEraFor(record.index);
      const eraOpening = era.key !== previousEra
        ? `<header class="era-divider era-${era.key}"><span aria-hidden="true">${era.glyph}</span><div><small>${era.name}</small><strong>${era.strap}</strong><em>${era.route}</em></div><i></i></header>`
        : "";
      previousEra = era.key;
      const routeSide = record.index % 2 ? "route-left" : "route-right";
      return `
      ${eraOpening}<button class="stage-card ${routeSide} era-${era.key} ${completed.has(record.id) ? "completed" : ""} ${unlocked ? "" : "locked"} ${underleveled ? "underleveled" : ""}" ${unlocked ? `data-stage-id="${record.id}"` : "disabled"} type="button">
        <span class="stage-thumb"><img loading="lazy" src="${mapPath(record)}" alt=""><i>${completed.has(record.id) ? "已克" : unlocked ? String(record.index).padStart(3, "0") : "未解锁"}</i></span>
        <span class="stage-copy"><small>${escapeHtml(record.chapter)} · ${turnLimit} 回合 · 建议 ${recommendedLevel} 级 · ${riskLabel}</small><strong>${escapeHtml(record.battleTitle)}</strong><span>${escapeHtml(record.title)}</span><em>${escapeHtml(record.objective)}</em></span>
      </button>`;
    }).join("") || '<div class="empty-search">没有符合条件的战役</div>';
    document.querySelectorAll("#stageGrid [data-stage-id]").forEach((button) => button.addEventListener("click", () => startStage(button.dataset.stageId)));
    const completedCount = completed.size;
    $("#progressText").textContent = `已完成 ${completedCount} / ${campaign.stageCount}`;
    $("#progressBar").style.width = `${completedCount / campaign.stageCount * 100}%`;
    $("#armyRankLabel").textContent = `军阶 ${profile.armyRank} · ${profile.armyXp}/${systems.PROGRESSION.armyXpPerLevel}`;
    const saved = readBattleSave();
    $("#resumeButton").hidden = !saved;
    const browsingArchive = Boolean(query) || range !== "all";
    const archiveFocus = browsingArchive ? stages.find((record) => !completed.has(record.id)) || stages[0] : null;
    renderCampaignFocus(saved, completed, archiveFocus);
    renderQuartermaster();
    renderOrganizationPanel();
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

  function campaignEraFor(index) {
    if (index <= 4) return { key: "western-zhou", name: "西周余晖", strap: "王命将倾", route: "王室气数渐衰", glyph: "鼎" };
    if (index < 142) return { key: "spring-autumn", name: "春秋列国", strap: "诸侯竞逐", route: "盟誓与征伐并起", glyph: "盟" };
    return { key: "warring-states", name: "战国风云", strap: "七雄争衡", route: "变法与兼并交迫", glyph: "兵" };
  }

  const CAMPAIGN_GEOGRAPHY = [
    { key: "zhou", name: "周", x: 49, y: 51, terms: ["周", "王室", "王畿", "镐京", "洛邑"], eras: ["western-zhou", "spring-autumn"] },
    { key: "qin", name: "秦", x: 23, y: 48, terms: ["秦", "岐", "雍"], eras: ["western-zhou", "spring-autumn", "warring-states"] },
    { key: "jin", name: "晋", x: 48, y: 29, terms: ["晋", "曲沃"], eras: ["western-zhou", "spring-autumn"] },
    { key: "zheng", name: "郑", x: 58, y: 54, terms: ["郑", "新郑"], eras: ["western-zhou", "spring-autumn"] },
    { key: "qi", name: "齐", x: 77, y: 32, terms: ["齐", "临淄"], eras: ["western-zhou", "spring-autumn", "warring-states"] },
    { key: "chu", name: "楚", x: 49, y: 73, terms: ["楚", "郢"], eras: ["western-zhou", "spring-autumn", "warring-states"] },
    { key: "wu", name: "吴", x: 74, y: 70, terms: ["吴国", "吴王", "姑苏", "阖闾", "夫差"], eras: ["spring-autumn"] },
    { key: "yue", name: "越", x: 82, y: 82, terms: ["越国", "越王", "会稽", "勾践", "句践"], eras: ["spring-autumn"] },
    { key: "yan", name: "燕", x: 76, y: 17, terms: ["燕", "蓟"], eras: ["warring-states"] },
    { key: "zhao", name: "赵", x: 52, y: 25, terms: ["赵", "邯郸", "晋阳", "襄子"], eras: ["warring-states"] },
    { key: "wei", name: "魏", x: 57, y: 43, terms: ["魏", "大梁", "魏驹"], eras: ["warring-states"] },
    { key: "han", name: "韩", x: 56, y: 59, terms: ["韩", "新郑", "韩虎"], eras: ["warring-states"] }
  ];

  function renderCampaignGeography(record, era) {
    const corpus = [record.chapter, record.title, record.battleTitle, record.objective].filter(Boolean).join(" ");
    const visible = CAMPAIGN_GEOGRAPHY.filter((state) => state.eras.includes(era.key));
    const active = visible.filter((state) => state.terms.some((term) => corpus.includes(term)));
    const markers = $("#focusGeographyMarkers");
    markers.replaceChildren();
    visible.forEach((state) => {
      const marker = document.createElement("span");
      marker.className = `geography-marker${active.includes(state) ? " is-active" : ""}`;
      marker.dataset.state = state.key;
      marker.style.left = `${state.x}%`;
      marker.style.top = `${state.y}%`;
      marker.textContent = state.name;
      markers.appendChild(marker);
    });
    $("#focusGeographyCaption").textContent = active.length ? active.map((state) => state.name).join(" · ") : era.name;
    $("#focusEraGlyph").textContent = era.glyph;
  }

  const JOURNEY_POINTS = [
    { x: 8, y: 72 }, { x: 29, y: 49 }, { x: 50, y: 63 }, { x: 70, y: 35 }, { x: 91, y: 20 }
  ];

  function renderFocusJourney(record, completed) {
    const root = $("#focusJourney");
    const currentIndex = campaign.stages.findIndex((item) => item.id === record.id);
    if (currentIndex < 0) { root.replaceChildren(); return; }
    const desired = 5;
    const start = clamp(currentIndex - 2, 0, Math.max(0, campaign.stages.length - desired));
    const nearby = campaign.stages.slice(start, start + desired);
    const legs = nearby.slice(1).map((_, index) => {
      const from = JOURNEY_POINTS[index];
      const to = JOURNEY_POINTS[index + 1];
      const dx = to.x - from.x; const dy = to.y - from.y;
      const length = Math.hypot(dx, dy);
      const angle = Math.atan2(dy, dx) * 180 / Math.PI;
      return `<i class="journey-leg" style="left:${from.x}%;top:${from.y}%;width:${length}%;transform:rotate(${angle}deg)"></i>`;
    }).join("");
    const nodes = nearby.map((item, index) => {
      const unlocked = systems.isStageUnlocked(item, profile, campaign.stages);
      const status = completed.has(item.id) ? "is-completed" : item.id === record.id ? "is-current" : unlocked ? "is-open" : "is-locked";
      const point = JOURNEY_POINTS[index];
      return `<button type="button" class="journey-node ${status}" data-journey-stage="${item.id}" style="left:${point.x}%;top:${point.y}%" aria-label="第 ${item.index} 战 ${escapeHtml(item.battleTitle)}"><b>${String(item.index).padStart(2, "0")}</b><small>${escapeHtml(item.battleTitle)}</small></button>`;
    }).join("");
    root.innerHTML = `${legs}${nodes}`;
    root.querySelectorAll("[data-journey-stage]").forEach((button) => button.addEventListener("click", () => {
      const target = findStageRecord(button.dataset.journeyStage);
      if (target) renderCampaignFocus(null, new Set(profile.completed || []), target);
    }));
  }

  function renderCampaignFocus(saved, completed, archiveFocus = null) {
    const lastIndex = campaign.stages.findIndex((record) => record.id === profile.lastStage);
    const nextIncomplete = campaign.stages.find((record) => !completed.has(record.id));
    const record = archiveFocus || (saved
      ? findStageRecord(saved.stageId)
      : nextIncomplete || campaign.stages[Math.max(0, lastIndex)] || campaign.stages[0]);
    if (!record) return;
    const isSaved = saved?.stageId === record.id;
    const isCompleted = completed.has(record.id);
    const era = campaignEraFor(record.index);
    $("#campaignScreen").dataset.era = era.key;
    document.querySelectorAll("[data-era-key]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.eraKey === era.key)));
    $("#campaignEraLabel").textContent = `${era.name} · ${era.strap}`;
    $("#focusEra").textContent = era.name;
    $("#focusRouteFill").style.width = `${Math.max(1, record.index / campaign.stageCount * 100)}%`;
    $("#focusRouteLabel").textContent = era.route;
    $("#focusKicker").textContent = isSaved ? "战局待续" : isCompleted ? "旧战重温" : record.index === 1 ? "从这里入史" : "下一场史局";
    $("#focusBattleTitle").textContent = record.battleTitle;
    $("#focusChapter").textContent = record.chapter;
    $("#focusStory").textContent = record.title;
    $("#focusObjective").textContent = record.objective;
    $("#focusIndex").textContent = record.isProcedural ? `演武 / ${campaign.stageCount}` : `${String(record.index).padStart(3, "0")} / ${campaign.stageCount}`;
    const assist = systems.retryAssist(profile, record.id);
    $("#focusTurns").textContent = `${systems.effectiveTurnLimit(record.turnLimit, profile.settings.battleDifficulty, assist.active)} 回合${assist.active ? " · 援助" : ""}`;
    $("#focusStatus").textContent = isSaved ? `第 ${saved.turn || 1} 回合` : isCompleted ? "已克" : "未出阵";
    const recommendedLevel = systems.recommendedStageLevel(record.index);
    $("#focusRank").textContent = `当前 ${profile.armyRank} · 建议 ${recommendedLevel}`;
    $("#focusEraBackdrop").src = `assets/campaign/era-${era.key}.webp`;
    $("#focusFigures").src = `assets/campaign/figures-${era.key}.webp`;
    $("#focusMap").src = mapPath(record);
    $("#focusMap").alt = `${record.battleTitle}战场`;
    renderCampaignGeography(record, era);
    renderFocusJourney(record, completed);
    const unlocked = systems.isStageUnlocked(record, profile, campaign.stages);
    $("#focusStageButton").disabled = !unlocked;
    $("#focusStageButton").textContent = !unlocked ? "尚未解锁" : isSaved ? "续写此局" : isCompleted ? "重温旧战" : "奉命出征";
    $("#focusStageButton").dataset.stageId = record.id;
    $("#focusStageButton").dataset.saved = isSaved ? "true" : "false";
    renderCampaignRouteProof(record);
    $("#focusRestartButton").hidden = !isSaved;
    $("#focusRestartButton").dataset.stageId = isSaved ? record.id : "";
    renderWarCouncil(record);
  }

  function campaignRouteInput(record, routeMethod = null) {
    const previous = campaign?.stages?.[Number(record.index) - 2];
    if (!previous || Number(record.index) !== Number(previous.index) + 1) return null;
    return {
      from_stage_id: previous.id,
      from_stage_index: Number(previous.index),
      to_stage_id: record.id,
      to_stage_index: Number(record.index),
      ...(routeMethod ? { route_method: routeMethod } : {})
    };
  }

  function loadCampaignRoute(record, force = false) {
    const input = campaignRouteInput(record);
    if (!input) return Promise.resolve({ mode: "origin", found: true, provisionCost: 0 });
    if (force) campaignRoutePlans.delete(record.id);
    if (!campaignRoutePlans.has(record.id)) {
      const pending = integration.campaignRoute(input).catch((error) => {
        campaignRoutePlans.delete(record.id);
        throw error;
      });
      campaignRoutePlans.set(record.id, pending);
    }
    return campaignRoutePlans.get(record.id);
  }

  function selectedCampaignRoute(record, response) {
    const options = Array.isArray(response?.options) ? response.options : [];
    const method = profile.routePreferences?.[record.id] || "campaign_progression";
    const selected = options.find((option) => option.method === method)
      || options.find((option) => option.method === "campaign_progression")
      || response;
    return { ...response, ...selected, options };
  }

  function verifySelectedCampaignRoute(record) {
    const method = profile.routePreferences?.[record.id] || "campaign_progression";
    const input = campaignRouteInput(record, method);
    if (!input) return Promise.resolve({ mode: "origin", found: true, provisionCost: 0 });
    return integration.campaignRoute(input);
  }

  function renderCampaignRouteProof(record) {
    const proof = $("#focusRouteProof");
    const serial = ++campaignRouteSerial;
    if (Number(record.index) <= 1) {
      proof.dataset.state = "origin";
      proof.textContent = "王畿启程 · 无行军耗粮";
      $("#focusRouteOptions").hidden = true;
      return;
    }
    proof.dataset.state = "loading";
    proof.textContent = "史料路线核验中";
    loadCampaignRoute(record).then((route) => {
      if (serial !== campaignRouteSerial || $("#focusStageButton").dataset.stageId !== record.id) return;
      const previous = campaign.stages[Number(record.index) - 2];
      const selected = selectedCampaignRoute(record, route);
      proof.dataset.state = "ready";
      proof.textContent = `${previous.battleTitle} → ${record.battleTitle} · ${selected.label || "奉诏直进"} · 军粮 ${selected.provisionCost}${selected.moraleDelta ? ` · 士气 ${selected.moraleDelta > 0 ? "+" : ""}${selected.moraleDelta}` : ""}`;
      const options = $("#focusRouteOptions");
      options.hidden = !Array.isArray(route.options) || route.options.length < 2;
      options.innerHTML = (route.options || []).map((option) =>
        `<button type="button" role="radio" aria-checked="${option.method === selected.method}" data-route-method="${option.method}"><strong>${escapeHtml(option.label)}</strong><small>${option.provisionCost} 粮${option.moraleDelta ? ` · 士气 ${option.moraleDelta > 0 ? "+" : ""}${option.moraleDelta}` : ""}${option.guideName ? ` · ${escapeHtml(option.guideName)}` : ""}</small></button>`
      ).join("");
    }).catch(() => {
      if (serial !== campaignRouteSerial || $("#focusStageButton").dataset.stageId !== record.id) return;
      proof.dataset.state = "error";
      proof.textContent = "史料路线暂不可用";
      $("#focusRouteOptions").hidden = true;
    });
  }

  function stageOwnHeroes(record) {
    const entries = [...asList(record?.stage?.deploy?.unselectables), ...asList(record?.stage?.deploy?.selectables)];
    return [...new Set(entries.filter((entry) => entry?.hero && (!entry.force || entry.force === "own")).map((entry) => String(entry.hero)))];
  }

  function renderWarCouncil(record) {
    const resources = profile.campaignResources;
    const wounded = Object.keys(profile.woundedHeroes || {}).length;
    $("#provisionsCount").textContent = `${resources.provisions} / 200`;
    $("#moraleCount").textContent = `${resources.morale} / 100`;
    $("#woundedCount").textContent = wounded;
    document.querySelectorAll("[data-formation]").forEach((button) => button.classList.toggle("active", button.dataset.formation === profile.formation));
    const candidates = stageOwnHeroes(record);
    const selected = candidates.includes(profile.stageVanguards[record.id]) ? profile.stageVanguards[record.id] : candidates[0] || "";
    if (selected) profile.stageVanguards[record.id] = selected;
    $("#vanguardSelect").innerHTML = candidates.length
      ? candidates.map((heroId) => {
        const mastery = systems.masteryForHero(profile, heroId);
        const woundedMark = profile.woundedHeroes[systems.canonicalHeroId(heroId)] ? " · 负伤" : "";
        return `<option value="${escapeHtml(heroId)}" ${heroId === selected ? "selected" : ""}>${escapeHtml(displayName(heroId))} · ${mastery.level}级${woundedMark}</option>`;
      }).join("")
      : '<option value="">本关由史实阵容出战</option>';
    $("#vanguardSelect").disabled = !candidates.length;
    const assist = systems.retryAssist(profile, record.id);
    $("#assistToggle").checked = profile.settings.transparentAssist;
    $("#assistStatus").textContent = assist.eligible
      ? `已连续失利 ${assist.failures} 次：+15% 回合、+1 金疮药、临时士气 +8，首通铜钱 -10%`
      : `已失败 ${assist.failures} 次；连续失败两次后自动生效`;
    $("#restArmyButton").disabled = profile.coins < 120 || (resources.provisions >= 200 && resources.morale >= 100 && !wounded);
    const daily = systems.dailyChallenge(new Date().toLocaleDateString("sv-SE"));
    $("#dailyChallengeMeta").textContent = `${daily.date} · 固定种子 ${daily.seed} · ${{ easy: "简单", medium: "标准", hard: "艰难" }[daily.difficulty]}`;
    renderRecentReplays();
  }

  function renderRecentReplays() {
    const recent = [...(profile.replays || [])].slice(-5).reverse();
    $("#recentReplays").innerHTML = recent.length ? recent.map((replay, index) => {
      const summary = replay.summary || {};
      const title = findStageRecord(replay.stage_id)?.battleTitle || replay.stage_id || "未名战局";
      return `<button class="replay-row" type="button" data-replay-index="${profile.replays.length - 1 - index}"><span><strong>${escapeHtml(title)}</strong><small>${summary.turns || 0} 回合 · ${escapeHtml(summary.difficulty || replay.difficulty || "medium")} · ${(replay.events || []).length} 事件</small></span><em>${summary.won ? "告捷" : "失利"}</em></button>`;
    }).join("") : '<div class="replay-empty">完成一场战斗后可在此复盘</div>';
    document.querySelectorAll("[data-replay-index]").forEach((button) => button.addEventListener("click", () => openReplay(Number(button.dataset.replayIndex))));
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]);
  }

  function difficultyProfileFor(record) {
    return difficultyProfiles?.profiles?.[record?.id] || {
      id: record?.id,
      index: record?.index,
      objectiveType: record?.isProcedural ? "procedural" : "defeat",
      recommendedLevel: systems.recommendedStageLevel(record?.index),
      structuralRisk: 35,
      flags: ["runtime-profile-missing"]
    };
  }

  function assessStage(record, difficulty = profile.settings.battleDifficulty) {
    return systems.stageDifficultyAssessment(difficultyProfileFor(record), profile, difficulty);
  }

  function difficultyRiskLabel(assessment) {
    const labels = { narrative: "剧情", low: "敌势较弱", guarded: "势均力敌", high: "敌军强盛", severe: "险战" };
    return labels[assessment?.riskBand] || "尚待探明";
  }

  function openCampaign() {
    if (state && stageRecord && !state.result) saveBattle(false);
    setExerciseMenu(false);
    setCampaignSettings(false);
    setCampaignCamp(false);
    setCampaignOffice(false);
    stopStoryVoice();
    stopContextMusic();
    storyDone = null;
    storyEntries = [];
    storyIndex = 0;
    storyMusicContext = {};
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
    if (!record || enemyRunning || routeStartPending) return;
    if (!record.isProcedural && !systems.isStageUnlocked(record, profile, campaign.stages)) {
      showNotice("请先完成上一场战役");
      return;
    }
    const requiresRoute = !savedState && !record.isProcedural && Number(record.index) > 1 && !(profile.completed || []).includes(record.id);
    let campaignRoute = null;
    if (requiresRoute) {
      const button = $("#focusStageButton");
      routeStartPending = true;
      if (button?.dataset.stageId === record.id) button.disabled = true;
      try {
        campaignRoute = await verifySelectedCampaignRoute(record);
        const cost = Number(campaignRoute?.provisionCost);
        if (!campaignRoute?.found || !Number.isInteger(cost) || cost < 0 || cost > 20) throw new Error("路线军粮配置无效");
        if (campaignRoute.mode === "connected" && campaignRoute.receipt?.kernel?.state !== "SEALED") {
          throw new Error("路线未获内核封印");
        }
        if (profile.campaignResources.provisions < cost) {
          showNotice(`行军需 ${cost} 军粮，请先在官署筹备`);
          return;
        }
      } catch (error) {
        showNotice(`史料路线核验失败，请稍后重试：${error.message}`);
        return;
      } finally {
        routeStartPending = false;
        if (button?.dataset.stageId === record.id) button.disabled = false;
      }
    }
    setExerciseMenu(false);
    setCampaignSettings(false);
    setCampaignCamp(false);
    setCampaignOffice(false);
    stageRecord = record;
    $("#campaignScreen").hidden = true;
    $("#resultModal").hidden = true;
    $("#confirmModal").hidden = true;
    selectedId = null;
    selectedSkillId = null;
    inspectionId = null;
    reachable.clear();
    unitAnimations.clear();
    unitSerial = 0;
    mapZoom = 1;
    updateZoom();
    state = savedState || freshState(record);
    if (options.procedural) state.procedural = options.procedural;
    state.assist ||= systems.retryAssist(profile, record.id);
    const objectiveType = state.procedural?.objectiveType ? "procedural" : difficultyProfileFor(record).objectiveType;
    state.mission ||= { contract: systems.missionContract(objectiveType), phaseIndex: 0, progress: 0, milestones: [] };
    state.difficultyAssessment ||= assessStage(record, state.procedural?.difficulty || state.difficulty || profile.settings.battleDifficulty);
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
    if (!savedState && state.assist.active) {
      state.assistMedicineRemaining = state.assist.medicine;
      state.inventory.medicine = Number(state.inventory.medicine || 0) + state.assist.medicine;
    }
    state.units.forEach((unit) => {
      unit.effects ||= [];
      unit.model ||= heroById.get(unit.heroId)?.model || "infantry-1-red";
    });
    unitSerial = Math.max(0, ...state.units.map((unit) => Number(String(unit.id).match(/-(\d+)$/)?.[1] || 0)));
    setStatus("正在列阵");
    updateStageHeader();
    configureBoard();
    let profileBeforeDeployment = null;
    try {
      await runtime.loadStage(record, gameApi);
      // Deployment callbacks see staged resources, but the original profile stays intact
      // until all synchronous initialization has completed successfully.
      profileBeforeDeployment = profile;
      profile = JSON.parse(JSON.stringify(profile));
    if (!savedState) {
      if (campaignRoute) {
        state.campaignRoute = campaignRoute;
        profile.campaignResources.provisions = clamp(
          profile.campaignResources.provisions - campaignRoute.provisionCost,
          0,
          200
        );
        profile.campaignResources.morale = clamp(
          profile.campaignResources.morale + Number(campaignRoute.moraleDelta || 0),
          0,
          100
        );
      }
      profile.organization = organization.syncMembers(profile.organization, record, displayName);
      const prepared = organization.consumeSupport(profile.organization, record.id);
      profile.organization = prepared.state;
      state.organizationSupport = prepared.support;
      profile.campaignResources.provisions = clamp(profile.campaignResources.provisions + prepared.support.provisions, 0, 200);
      profile.campaignResources.morale = clamp(profile.campaignResources.morale + prepared.support.morale, 0, 100);
      // saveBattle below persists the constructed battle before its consumed preparation.
    }
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
      const formation = systems.FORMATION_PRESETS[profile.formation];
      const vanguard = profile.stageVanguards[record.id];
      if (state.campaignRoute) log(`史料行军：${state.campaignRoute.label || "奉诏直进"}（${state.campaignRoute.routeId}）；军粮 -${state.campaignRoute.provisionCost}${state.campaignRoute.moraleDelta ? `，士气 ${state.campaignRoute.moraleDelta > 0 ? "+" : ""}${state.campaignRoute.moraleDelta}` : ""}。`, "event");
      log(`军议：${formation.name}${vanguard ? `；${displayName(vanguard)}任先锋` : ""}；军粮 ${profile.campaignResources.provisions}，士气 ${profile.campaignResources.morale}${profile.campaignResources.provisions < 40 ? "；缺粮导致兵力与攻击下降" : ""}。`, "event");
      if (state.assist.active) log(`连续失利援助已启用：回合上限 +15%，临时金疮药 +1、士气 +8；首通铜钱 -10%。`, "event");
      if (state.organizationSupport?.sources?.length) {
        const support = state.organizationSupport;
        log(`官署筹备已投入：${support.sources.join("、")}；军粮 +${support.provisions}，士气 +${support.morale}，攻击 +${Math.round(support.attack * 100)}%，防御 +${Math.round(support.defense * 100)}%，侦察 ${support.recon}。`, "event");
        for (const council of support.councils || []) log("军议依据：《" + council.knowledgeName + "》；" + council.memberName + "建议：" + council.text, "event");
        for (const mandate of support.mandates || []) log("内核军令：" + mandate.council.text + "；印记 " + String(mandate.digest || "").slice(0, 10) + "。", "event");
      }
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
        log(`垂沙推演：可行军路 ${meta.routeCount} 条；沙盘编号 ${state.procedural.seed}；地形可行。`, "event");
      } else {
        log(`端侧生成：${meta.source || "未知"}；种子 ${state.procedural.seed}；修复 ${meta.repairs || 0} 格；障碍 ${(Number(validation.blockedRatio || 0) * 100).toFixed(1)}%。`, "event");
      }
    }
    state.phase = state.result ? "ended" : "player";
    state.initialOwnCount ||= state.units.filter((unit) => unit.team === "own").length;
    state.initialEnemyCount ||= state.units.filter((unit) => unit.team === "enemy").length;
    state.initialAllyCount ||= state.units.filter((unit) => unit.team === "ally").length;
    loadStageMap();
    } catch (error) {
      if (profileBeforeDeployment) profile = profileBeforeDeployment;
      restoring = false;
      runtimeTurnOverride = null;
      runtime.api = null;
      runtime.loadedStage = null;
      try { runtime.resetStageGlobals(); } catch (_) { /* Next load resets again. */ }
      unitAnimations.clear();
      state = null;
      stageRecord = null;
      $("#storyModal").hidden = true;
      $("#resultModal").hidden = true;
      $("#campaignScreen").hidden = false;
      renderCampaign();
      showNotice(`战役载入失败，筹备已保留，请重试：${error.message}`);
      return;
    }
    let preparationTransaction = null;
    if (!savedState && state.organizationSupport?.sources?.length) {
      preparationTransaction = crypto.randomUUID();
      const journal = readJson(PREPARATION_JOURNAL_KEY, {});
      const remaining = new Set(profile.organization.pendingSupport.map(item => item.id));
      journal[preparationTransaction] = {
        committed: false,
        supportIds: profileBeforeDeployment.organization.pendingSupport.filter(item => !remaining.has(item.id)).map(item => item.id),
        support: state.organizationSupport
      };
      localStorage.setItem(PREPARATION_JOURNAL_KEY, JSON.stringify(journal));
      state.organizationSupportTransaction = preparationTransaction;
      profile.organization.consumedSupportTransactions = [...(profile.organization.consumedSupportTransactions || []), preparationTransaction];
      profile.organization.consumedSupportIds = [...new Set([...(profile.organization.consumedSupportIds || []), ...journal[preparationTransaction].supportIds])];
    }
    saveBattle(false);
    if (preparationTransaction) {
      const journal = readJson(PREPARATION_JOURNAL_KEY, {});
      if (journal[preparationTransaction]) journal[preparationTransaction].committed = true;
      localStorage.setItem(PREPARATION_JOURNAL_KEY, JSON.stringify(journal));
    }
    if (!savedState && record.isProcedural) writeJson(PROFILE_KEY, profile);
    updateUI();
    $("#storyReplayButton").hidden = !asList(record.story?.intro).length;
    requestAnimationFrame(centerOnOwnArmy);
    if (!savedState) {
      const intro = asList(record.story?.intro);
      if (intro.length) openStory(intro, () => beginTutorialOrBattle(), { stageId: record.id, section: "intro" });
      else beginTutorialOrBattle();
    } else if (state.result) {
      showResult();
    } else {
      playContextMusic({ stageId: record.id, kind: "battle", section: "battle" });
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
        setStatus(`垂沙沙盘已成 · 可行军路 ${generated.meta.routeCount} 条`);
        if (requestedDifficulty === "auto") showNotice(`智能推荐：${{ easy: "简单", medium: "标准", hard: "艰难" }[difficulty]}`);
      } finally {
        button.disabled = false;
        button.textContent = "推演垂沙";
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
      setStatus(generated.meta.fallback ? "麻隧旧图已备" : "麻隧沙盘已成 · 地形可行");
      if (requestedDifficulty === "auto") showNotice(`智能推荐：${{ easy: "简单", medium: "标准", hard: "艰难" }[difficulty]}`);
    } finally {
      button.disabled = false;
      button.textContent = "推演麻隧";
    }
  }

  async function startDailyChallenge() {
    if (enemyRunning || !mapElitesTemplate || !mapElitesArchive) return;
    const button = $("#dailyChallengeButton");
    const challenge = systems.dailyChallenge(new Date().toLocaleDateString("sv-SE"));
    button.disabled = true;
    button.textContent = "正在生成";
    try {
      const generated = DongzhouMapElitesRuntime.selectElite(mapElitesArchive, challenge.difficulty, challenge.seed);
      await startStage(mapElitesTemplate.id, null, {
        procedural: {
          terrain: generated.rows,
          difficulty: challenge.difficulty,
          seed: challenge.seed,
          objectiveType: "daily-map-elites",
          daily: challenge.date,
          meta: generated.meta,
          decision: { difficulty: challenge.difficulty, behaviorProbability: 1, source: "daily-fixed-seed" }
        }
      });
      showNotice(`${challenge.date} 每日演武 · 全体玩家同一种子`);
    } finally {
      button.disabled = false;
      button.textContent = "今日挑战";
    }
  }

  function syncProceduralButton() {
    $("#proceduralButton").textContent = $("#proceduralMode").value === "pcgrl" ? "推演麻隧" : "推演垂沙";
  }

  function setExerciseMenu(open) {
    const expanded = Boolean(open);
    $("#exercisePanel").hidden = !expanded;
    $("#exerciseMenuButton").setAttribute("aria-expanded", String(expanded));
  }

  function setCampaignSettings(open) {
    const expanded = Boolean(open);
    $("#campaignSettingsBackdrop").hidden = !expanded;
    $("#campaignSettingsButton").setAttribute("aria-expanded", String(expanded));
    if (expanded) {
      setExerciseMenu(false);
      requestAnimationFrame(() => $("#campaignSettingsCloseButton").focus());
    }
  }

  function setCampaignCamp(open) {
    const expanded = Boolean(open);
    $("#campaignCampBackdrop").hidden = !expanded;
    $("#campaignCampButton").setAttribute("aria-expanded", String(expanded));
    if (expanded) {
      setCampaignSettings(false);
      setExerciseMenu(false);
      requestAnimationFrame(() => $("#campaignCampCloseButton").focus());
    }
  }

  function setCampaignOffice(open) {
    const expanded = Boolean(open);
    $("#campaignOfficeBackdrop").hidden = !expanded;
    $("#campaignOfficeButton").setAttribute("aria-expanded", String(expanded));
    if (expanded) {
      setCampaignCamp(false);
      setCampaignSettings(false);
      renderOrganizationPanel();
      refreshOfficeTaskSnapshots().catch((error) => showNotice(`官署簿书暂不可达：${error.message}`));
      syncOfficeNpcs(profile.organization.members).then(() => warmCurrentOfficeNpcSchedules()).catch(() => {});
      refreshOfficeNpcState();
      requestAnimationFrame(() => $("#campaignOfficeCloseButton").focus());
    } else {
      officeNpcRefreshSerial += 1;
      clearTimeout(officeNpcRefreshTimer);
      officeNpcRefreshTimer = null;
      clearTimeout(officeQuizTimer);
      officeQuizTimer = null;
    }
  }

  function officeStage() {
    return findStageRecord($("#focusStageButton").dataset.stageId) || campaign?.stages?.[0];
  }

  function renderOfficeQuiz() {
    const panel = $("#officeQuizQuestion");
    if (!panel) return;
    clearTimeout(officeQuizTimer);
    officeQuizTimer = null;
    profile.knowledgeQuiz = systems.normalizeKnowledgeQuiz(profile.knowledgeQuiz);
    const quiz = profile.knowledgeQuiz;
    const pending = quiz.pending;
    const latest = quiz.history.at(-1);
    $("#officeQuizScore").textContent = `累计 ${quiz.score} 分`;
    $("#officeQuizStart").disabled = officeQuizInFlight || Boolean(pending);
    if (!pending) {
      panel.hidden = !latest;
      $("#officeQuizStatus").textContent = latest
        ? `${latest.correct ? "答中" : latest.state === "EXPIRED" ? "逾时" : "未中"} · 本题 ${latest.score} 分 · 累计 ${quiz.score} 分`
        : "本回可开一题，答中记 10 分。";
      $("#officeQuizSource").textContent = latest?.source?.work
        ? `据 ${latest.source.work}${latest.source.scope ? ` · ${latest.source.scope}` : ""}`
        : "";
      $("#officeQuizPrompt").textContent = latest ? `正解：${latest.correctAnswer}` : "";
      $("#officeQuizOptions").innerHTML = "";
      return;
    }
    const question = pending.question;
    const remaining = Math.max(0, Math.ceil((Date.parse(question.deadlineAt) - Date.now()) / 1000));
    panel.hidden = false;
    $("#officeQuizPrompt").textContent = question.prompt;
    $("#officeQuizOptions").innerHTML = question.options.map((option, index) =>
      `<button type="button" data-quiz-answer="${index}" ${officeQuizInFlight ? "disabled" : ""}><span>${String.fromCharCode(65 + index)}</span> ${escapeHtml(option)}</button>`
    ).join("");
    $("#officeQuizStatus").textContent = remaining > 0 ? `余 ${remaining} 秒 · 答中 10 分` : "已到时 · 交卷记 0 分";
    $("#officeQuizSource").textContent = `内核题印 ${String(question.receipt?.digest || "").slice(0, 12)}`;
    if (!$("#campaignOfficeBackdrop").hidden) officeQuizTimer = setTimeout(renderOfficeQuiz, 1000);
  }

  async function startOfficeQuiz() {
    if (officeQuizInFlight || profile.knowledgeQuiz?.pending) return;
    officeQuizInFlight = true;
    renderOfficeQuiz();
    try {
      const response = await integration.startKnowledgeQuiz(officeStage().id, crypto.randomUUID());
      profile.knowledgeQuiz = systems.normalizeKnowledgeQuiz({ ...profile.knowledgeQuiz, pending: response });
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      await integration.persist(profile);
    } catch (error) {
      showNotice(error.message === "knowledge_quiz_requires_online" ? "史官问对需连接史库" : error.message);
    } finally {
      officeQuizInFlight = false;
      renderOfficeQuiz();
    }
  }

  async function answerOfficeQuiz(answerIndex) {
    const pending = profile.knowledgeQuiz?.pending;
    if (officeQuizInFlight || !pending) return;
    officeQuizInFlight = true;
    renderOfficeQuiz();
    try {
      const result = await integration.answerKnowledgeQuiz(pending.question.id, pending.action.actionId, answerIndex);
      const recorded = systems.recordKnowledgeQuizResult(profile, result);
      if (!recorded.ok) throw new Error("问对印记未通过内核校验");
      profile = recorded.profile;
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      await integration.persist(profile);
      showNotice(result.state === "EXPIRED" ? "本题逾时，记 0 分" : result.correct ? "答中，记 10 分" : "未中，记 0 分");
    } catch (error) {
      showNotice(error.message);
    } finally {
      officeQuizInFlight = false;
      renderOfficeQuiz();
    }
  }

  function saveOrganization(next) {
    profile.organization = organization.normalizeState(next);
    writeJson(PROFILE_KEY, profile);
    renderOrganizationPanel();
  }

  function officeInventoryLabel(resourceKey) {
    return ({ "task.execution": "差事额度", "guild.capacity": "组织容量" })[resourceKey] || resourceKey.replace(/[._-]+/g, " ");
  }

  function renderOfficeInventory() {
    const accounts = Array.isArray(officeInventoryView?.accounts) ? officeInventoryView.accounts : [];
    $("#officeInventoryRevision").textContent = officeInventoryView?.error
      ? "实账暂不可达"
      : officeInventoryView
        ? `账本第 ${Number(officeInventoryView.revision || 0)} 版`
        : "等待朝议实账";
    $("#officeInventoryAccounts").innerHTML = officeInventoryView?.loading
      ? "<li>正在清点…</li>"
      : accounts.length
        ? accounts.map((account) => `<li><span>${escapeHtml(officeInventoryLabel(account.resourceKey))}</span><strong>${Number(account.balance || 0)}</strong></li>`).join("")
        : `<li>${officeInventoryView?.error ? "稍后可重新调阅" : "当前无公共库存科目"}</li>`;
    const taskCredit = accounts.find((account) => account.resourceKey === "task.execution")?.balance || 0;
    const provisions = Number(profile?.campaignResources?.provisions || 0);
    const pending = integration.pendingOrganizationInventoryRequisition();
    const pendingResult = pending?.result;
    const approval = $("#officeInventoryApproval");
    const waitingForDecision = ["REQUIRES_ACTION", "RETRYABLE"].includes(pendingResult?.state);
    approval.hidden = !waitingForDecision;
    if (waitingForDecision) {
      const requisitionDraft = pendingResult.requisition || {};
      const retrying = pending.decision === "APPROVE" || pendingResult.state === "RETRYABLE";
      $("#officeInventoryApprovalDetail").textContent = retrying
        ? `已签发，等待实账落定 · 印记 ${String(requisitionDraft.digest || "").slice(0, 10)}`
        : `调拨 ${Number(requisitionDraft.units || 0)} 点差事额度，补入 ${Number(requisitionDraft.effect?.provisions || 0)} 军粮 · 印记 ${String(requisitionDraft.digest || "").slice(0, 10)}`;
      $("#officeInventoryApprove").disabled = officeInventoryRequisitionBusy;
      $("#officeInventoryReject").disabled = officeInventoryRequisitionBusy || retrying;
    }
    const requisition = $("#officeInventoryRequisition");
    requisition.disabled = integration.isOffline()
      || officeInventoryRequisitionBusy
      || Boolean(pending)
      || !officeInventoryView
      || officeInventoryView.loading
      || officeInventoryView.error
      || taskCredit < 20
      || provisions > 188;
    $("#officeInventoryRequisitionFeedback").textContent = officeInventoryRequisitionBusy
      ? "正在核准并落账"
      : waitingForDecision
        ? pending.decision === "APPROVE" ? "签发待实账落定" : "内核草案待裁"
      : provisions > 188
        ? "军粮已接近上限"
        : taskCredit < 20 && officeInventoryView
          ? "差事额度不足 20"
          : "可补入 12 军粮";
  }

  async function applyOfficeInventoryRequisition(response, { render = true } = {}) {
    const previousOrganization = profile.organization;
    const previousResources = { ...profile.campaignResources };
    const recorded = organization.recordInventoryRequisition(profile.organization, response);
    if (recorded.applied) {
      profile.organization = recorded.state;
      profile.campaignResources = {
        ...profile.campaignResources,
        provisions: clamp(
          Number(profile.campaignResources.provisions || 0) + recorded.effect.provisions,
          0,
          200
        )
      };
      try {
        await integration.persist(profile);
      } catch (error) {
        profile.organization = previousOrganization;
        profile.campaignResources = previousResources;
        throw error;
      }
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    }
    integration.acknowledgeOrganizationInventoryRequisition(response.requestId);
    if (render) renderOrganizationPanel();
    return recorded;
  }

  async function recoverOfficeInventoryRequisition() {
    let pending = integration.pendingOrganizationInventoryRequisition();
    if (!pending || integration.isOffline()) return;
    try {
      let response = pending.result || await integration.requisitionOrganizationInventory(pending.input);
      pending = integration.pendingOrganizationInventoryRequisition();
      if (response.state === "COMPLETED") {
        await applyOfficeInventoryRequisition(response, { render: false });
        return;
      }
      if (response.state === "REJECTED") {
        integration.acknowledgeOrganizationInventoryRequisition(response.requestId);
        return;
      }
      if (pending?.decision && response.requisition?.id && response.action?.actionId) {
        response = await integration.resumeOrganizationInventoryRequisition(
          response.requisition.id,
          response.action.actionId,
          pending.decision
        );
        if (response.state === "COMPLETED") {
          await applyOfficeInventoryRequisition(response, { render: false });
        } else if (response.state === "REJECTED") {
          integration.acknowledgeOrganizationInventoryRequisition(response.requestId);
        }
      }
    } catch (error) {
      console.warn("Inventory requisition recovery deferred", error);
    }
  }

  async function requisitionOfficeInventory() {
    if (officeInventoryRequisitionBusy) return;
    const stageId = String(officeStage()?.id || "");
    if (!stageId || Number(profile.campaignResources.provisions || 0) > 188) return;
    officeInventoryRequisitionBusy = true;
    renderOfficeInventory();
    try {
      const response = await integration.requisitionOrganizationInventory({ units: 20, stage_id: stageId });
      if (response.state === "COMPLETED") {
        const recorded = await applyOfficeInventoryRequisition(response);
        await refreshOfficeInventory();
        showNotice(recorded.applied ? `已从公共库藏调拨 20 点额度，补入 ${recorded.effect.provisions} 军粮` : "军需调拨已对账，无重复扣领");
      } else if (["REQUIRES_ACTION", "RETRYABLE"].includes(response.state)) {
        renderOfficeInventory();
        showNotice(response.state === "RETRYABLE" ? "已签发的军需调拨等待实账重试" : "军需调拨草案已由内核封存，请明确签发或驳回");
      } else {
        throw new Error("军需调拨草案状态无效");
      }
    } catch (error) {
      showNotice(error.message || "军需调拨草案暂未生成");
    } finally {
      officeInventoryRequisitionBusy = false;
      renderOfficeInventory();
    }
  }

  async function decideOfficeInventoryRequisition(decision) {
    if (officeInventoryRequisitionBusy) return;
    const pending = integration.pendingOrganizationInventoryRequisition();
    const response = pending?.result;
    if (!["REQUIRES_ACTION", "RETRYABLE"].includes(response?.state) || !response.requisition?.id || !response.action?.actionId) return;
    officeInventoryRequisitionBusy = true;
    renderOfficeInventory();
    try {
      const result = await integration.resumeOrganizationInventoryRequisition(
        response.requisition.id,
        response.action.actionId,
        decision
      );
      if (result.state === "REJECTED") {
        integration.acknowledgeOrganizationInventoryRequisition(result.requestId);
        showNotice("军需调拨草案已驳回，公共库藏未支出");
      } else if (result.state === "COMPLETED") {
        const recorded = await applyOfficeInventoryRequisition(result);
        await refreshOfficeInventory();
        showNotice(recorded.applied ? `军需调拨已签发，补入 ${recorded.effect.provisions} 军粮` : "军需调拨已对账，无重复扣领");
      } else {
        throw new Error("军需调拨未能落定");
      }
    } catch (error) {
      showNotice(error.code === "organization_inventory_insufficient" ? "公共库藏差事额度不足，签发草案已保留" : error.message || "军需调拨暂未完成");
    } finally {
      officeInventoryRequisitionBusy = false;
      renderOfficeInventory();
    }
  }

  async function refreshOfficeInventory() {
    if (integration.isOffline()) {
      officeInventoryView = { error: true, accounts: [] };
      renderOfficeInventory();
      return;
    }
    officeInventoryView = { ...(officeInventoryView || {}), loading: true };
    renderOfficeInventory();
    const button = $("#officeInventoryRefresh");
    button.disabled = true;
    try {
      officeInventoryView = await integration.organizationInventory();
    } catch (_) {
      officeInventoryView = { error: true, accounts: [] };
    } finally {
      button.disabled = false;
      renderOfficeInventory();
    }
  }

  function renderOrganizationPanel() {
    if (!organization || !campaign) return;
    const record = officeStage();
    profile.organization = organization.syncMembers(profile.organization, record, displayName);
    const org = profile.organization;
    $("#officeMonth").textContent = `${org.month} 月`;
    $("#officeInfluence").textContent = org.influence;
    $("#officeContribution").textContent = org.contribution;
    $("#officeActiveTasks").textContent = org.tasks.filter((task) => task.status === "active").length;
    $("#officeSupportCount").textContent = org.pendingSupport.length;
    renderOfficeInventory();
    const serviceLabels = [["nexusKernel", "内核"], ["orgFlow", "朝议"], ["aiNpc", "属官"], ["knowledge", "史官"]];
    $("#officeServiceStatus").innerHTML = serviceLabels.map(([key, label]) => `<span class="${org.backend[key] ? "online" : "local"}"><i></i>${label}${org.backend[key] ? "通达" : "本地推演"}</span>`).join("");
    $("#officeModeText").textContent = integration.isOffline() ? "当前为显式离线演算，属官与官署结果仅保存在本机。" : org.backend.mode === "connected" ? "朝议、属官与史官已互通；远端未确认的结果不会在本地结算。" : "官署服务暂不可达，联网玩法已暂停。";
    const currentMember = $("#officeMemberSelect").value;
    const visibleMembers = [
      ...org.members.filter((member) => member.id !== "DuBo"),
      ...org.members.filter((member) => member.id === "DuBo")
    ];
    $("#officeMemberSelect").innerHTML = visibleMembers.map((member) => `<option value="${escapeHtml(member.id)}">${escapeHtml(member.name)} · ${escapeHtml(member.office)}</option>`).join("");
    if (visibleMembers.some((member) => member.id === currentMember)) $("#officeMemberSelect").value = currentMember;
    renderOfficeCouncil();
    const currentType = $("#officeTaskType").value;
    $("#officeTaskType").innerHTML = Object.entries(organization.TASK_TYPES).map(([id, task]) => `<option value="${id}" ${id === currentType ? "selected" : ""}>${task.name} · ${task.duration}月</option>`).join("");
    const roster = org.remoteRoster || { organization: null, members: [] };
    const rosterMembers = Array.isArray(roster.members) ? roster.members : [];
    const rosterByHero = new Map(rosterMembers.map((entry) => [entry.heroId, entry]));
    const rosterState = roster.organization?.state === "ACTIVE" ? "在署" : roster.organization?.state || "待核";
    $("#officeRosterSummary").textContent = roster.organization
      ? `${roster.organization.name || org.name} · ${rosterMembers.length} 席在册 · 谱系 ${roster.organization.hierarchyVersion} · ${rosterState}`
      : "尚未取得朝议实账名册";
    renderOfficeMembership(roster);
    $("#officeMembers").innerHTML = org.members.map((member) => {
      const account = rosterByHero.get(member.id);
      const manager = account?.directManagerHeroId ? displayName(account.directManagerHeroId) : null;
      const role = account ? (account.level === "owner" || account.role === "commander" ? "主官" : "属官") : null;
      const remoteLine = account
        ? `<small class="office-member-account">${escapeHtml(role)} · 可用贡献 ${account.contributionBalance} · 累计 ${account.lifetimeEarned} · 已用 ${account.lifetimeSpent}${manager ? ` · 上呈${escapeHtml(manager)}` : " · 统辖官署"}</small>`
        : "";
      return `<div data-roster-hero="${escapeHtml(member.id)}"><strong>${escapeHtml(member.name)}</strong><span>${escapeHtml(member.office)}</span><small>功绩 ${member.merit >= 0 ? "+" : ""}${member.merit}${account ? " · 官署实账" : ""} · 信任 ${member.loyalty} · 关系 ${Number(org.relations[member.id] || 0) >= 0 ? "+" : ""}${Number(org.relations[member.id] || 0)} · 劳顿 ${member.fatigue}</small>${remoteLine}</div>`;
    }).join("") || "<p>随战役推进，出阵人物会进入官署名册。</p>";
    $("#officeTaskLedger").innerHTML = [...org.tasks].reverse().slice(0, 10).map((task) => {
      const outcomeState = task.npcOutcome?.state;
      const outcomeSealed = task.npcOutcome?.receipt?.kernel?.state === "SEALED";
      const outcomeLabel = outcomeState === "DELIVERED"
        ? (outcomeSealed ? ` · 人物四项归档 · 内核封印 ${escapeHtml(String(task.npcOutcome.receipt.digest || "").slice(0, 10))}` : " · 经历已形成")
        : outcomeState === "PENDING" ? (task.npcOutcome?.lastError ? " · 经历待重试" : " · 经历回写中") : "";
      const settlementLabel = task.settlement ? ` · 军府${Number(task.settlement.organizationDelta) >= 0 ? "+" : ""}${task.settlement.organizationDelta} · 功绩${Number(task.settlement.memberDelta) >= 0 ? "+" : ""}${task.settlement.memberDelta} · 印记 ${escapeHtml(String(task.closureReceipt?.digest || "").slice(0, 10))}` : "";
      const statusLabel = task.status === "active" ? (task.pendingReview?.state === "REQUIRES_ACTION" ? "复命待裁" : `${task.dueMonth}月复命`) : task.status === "success" ? "办成" : task.status === "partial" ? "部分办成" : task.status === "censured" ? "复命被申斥" : "未成";
      const emergencyLabel = task.mandate?.emergency ? ` · ${task.mandate.emergency.urgent ? "急报" : "常报"}${Number(task.mandate.emergency.score).toFixed(3)}` : "";
      const personalityLabel = task.mandate?.assignment?.personality?.fit?.available === true ? ` · 适岗${Number(task.mandate.assignment.personality.fit.score)}` : "";
      const motivationLabel = task.mandate?.assignment?.motivation?.fit?.available === true ? ` · 意愿${Number(task.mandate.assignment.motivation.fit.score)}` : "";
      const qualityLabel = task.mandate?.assignment?.quality?.fit?.available === true ? ` · 品行${Number(task.mandate.assignment.quality.fit.score)}` : "";
      const support = Number(task.mandate?.assignment?.managerSupport?.factor);
      const supportLabel = Number.isFinite(support) ? ` · 协同${support >= 0 ? "+" : ""}${support}` : "";
      const evidenceFit = Number(task.mandate?.evidenceFit?.factor);
      const evidenceLabel = Number.isFinite(evidenceFit) ? ` · 史证${evidenceFit}/9` : "";
      return `<li class="${task.status}"><span>${escapeHtml(task.name)}${task.operation?.kind === "diplomacy" ? ` · ${escapeHtml(task.operation.target_name)}` : ""}</span><strong>${escapeHtml(task.assigneeName)}</strong><small>${statusLabel}${task.council ? ` · 据《${escapeHtml(task.council.knowledgeName)}》${escapeHtml(task.council.evidenceSource?.tier || "来源")}军议` : ""}${evidenceLabel}${task.mandate?.assignment?.name ? ` · 当值${escapeHtml(task.mandate.assignment.name)}` : ""}${Number.isFinite(Number(task.mandate?.assignment?.readiness?.score)) ? ` · 胜任${Number(task.mandate.assignment.readiness.score)}` : ""}${personalityLabel}${motivationLabel}${qualityLabel}${supportLabel}${emergencyLabel}${settlementLabel}${outcomeLabel}</small></li>`;
    }).join("") || '<li class="empty">尚无差事</li>';
    $("#officeMandateLedger").innerHTML = [...org.mandates].reverse().slice(0, 6).map((mandate) => {
      const label = mandate.state === "RESOLVED" ? (mandate.outcome?.won ? "战后告捷" : "战后失利") : mandate.state === "FULFILLED" ? "复命待战" : mandate.state === "PARTIAL" ? "部分复命" : mandate.state === "FAILED" ? "执行未成" : mandate.state === "ORDERED" ? "属官执行中" : "已签发";
      const readiness = Number(mandate.assignment?.readiness?.score);
      const personalityLabel = mandate.assignment?.personality?.fit?.available === true ? ` · 适岗${Number(mandate.assignment.personality.fit.score)}` : "";
      const motivationLabel = mandate.assignment?.motivation?.fit?.available === true ? ` · 意愿${Number(mandate.assignment.motivation.fit.score)}` : "";
      const qualityLabel = mandate.assignment?.quality?.fit?.available === true ? ` · 品行${Number(mandate.assignment.quality.fit.score)}` : "";
      const support = Number(mandate.assignment?.managerSupport?.factor);
      const supportLabel = Number.isFinite(support) ? ` · 协同${support >= 0 ? "+" : ""}${support}` : "";
      const evidenceFit = Number(mandate.evidenceFit?.factor);
      const evidenceLabel = Number.isFinite(evidenceFit) ? ` · 史证${evidenceFit}/9` : "";
      const emergency = mandate.emergency;
      const emergencyLabel = emergency ? ` · ${emergency.urgent ? "急报" : "常报"}${Number(emergency.score).toFixed(3)}` : "";
      const interruption = mandate.scheduleInterruption;
      const interruptionLabel = interruption
        ? ` · ${interruption.action === "insert_today" ? "今日插程" : interruption.action === "future" ? "后续排程" : "日程裁定 " + interruption.action}${interruption.scheduleName ? `“${escapeHtml(interruption.scheduleName)}”` : ""}`
        : "";
      return `<li class="${escapeHtml(String(mandate.state || "issued").toLowerCase())}"><span>${escapeHtml(mandate.evidence?.name || "内核军令")}</span><strong>${escapeHtml(label)}</strong><small>${escapeHtml(mandate.evidence?.source?.work || "未列出处")}${evidenceLabel} · ${escapeHtml(mandate.assignment?.date || "未定日")} ${escapeHtml(mandate.assignment?.name || "旧军令未封当值")}${Number.isFinite(readiness) ? ` · 胜任${readiness}` : ""}${personalityLabel}${motivationLabel}${qualityLabel}${supportLabel}${emergencyLabel}${interruptionLabel} · 印记 ${escapeHtml(String(mandate.digest || "").slice(0, 10))}</small></li>`;
    }).join("") || '<li class="empty">完成史料查阅与属官裁断后，可签发内核军令。</li>';
    $("#officeAllianceLedger").innerHTML = [...org.diplomacy.alliances].reverse().map((pact) => `<li class="${pact.status}"><span>${escapeHtml(pact.targetName)}盟约</span><strong>${pact.status === "active" ? "生效" : pact.status === "broken" ? "背盟待战" : "战后结案"}</strong><small>关系 ${Number(org.diplomacy.relations[pact.targetId] || 0)} · ${escapeHtml(pact.terms.join("、"))}</small></li>`).join("") || '<li class="empty">尚无盟约</li>';
    $("#officeBattleArchive").innerHTML = [...org.archives].reverse().slice(0, 12).map((entry) => `<li><strong>${escapeHtml(entry.title)}</strong><span>${escapeHtml(entry.text)} · ${escapeHtml(String(entry.stageId || "无关卡"))}</span></li>`).join("") || "<li><strong>尚无档案</strong><span>完成盟约、背盟或战役后将在此存照。</span></li>";
    const sealedBattleReport = [...org.battleReports].reverse().find((report) => report?.kernelReceipt?.kernel?.state === "SEALED");
    if (sealedBattleReport) {
      const verifiedCount = Number(sealedBattleReport.kernelReceipt.verifiedParticipants?.length || 0);
      const rejectedCount = Number(sealedBattleReport.kernelReceipt.rejectedSupport?.length || 0);
      $("#officeBattleArchive").insertAdjacentHTML(
        "afterbegin",
        `<li><strong>\u5185\u6838\u6218\u679c\u5370\u8bb0</strong><span>${escapeHtml(sealedBattleReport.stageTitle || sealedBattleReport.stageId)} \u00b7 ${escapeHtml(String(sealedBattleReport.kernelReceipt.digest || "").slice(0, 12))} \u00b7 ${escapeHtml(String(sealedBattleReport.kernelReceipt.kernel.moduleVersion || ""))} \u00b7 ${verifiedCount}\u4eba\u8ba4\u8bc1${rejectedCount ? ` \u00b7 ${rejectedCount}\u9879\u672a\u8ba4\u8bc1` : ""}</span></li>`
      );
    }
    const selectedTask = organization.TASK_TYPES[$("#officeTaskType").value] || organization.TASK_TYPES.supply;
    const leaderSelected = !integration.isOffline() && org.backend.orgFlow && $("#officeMemberSelect").value === "DuBo";
    $("#officeIssueButton").disabled = officeOrderInFlight || leaderSelected;
    $("#officeIssueButton").title = leaderSelected ? "组织负责人可供调阅，但不能向自己派单" : "";
    $("#officeOrderHint").textContent = leaderSelected
      ? "杜伯为组织负责人：可调阅状态、书问与日程，但须选择直属属官承办差事。"
      : `${record?.battleTitle || "下一战"}：${selectedTask.name}需要 ${selectedTask.cost} 份军府资源，办成后形成战前助益。`;
    if (!$("#officeKnowledgeQuery").value) $("#officeKnowledgeQuery").value = `${record?.battleTitle || ""} ${record?.objective || ""}`.trim();
    if (!$("#officeDecisionQuestion").value) $("#officeDecisionQuestion").value = `${record?.battleTitle || "下一战"}应如何部署？`;
    const decisionDefaults = ["先固军粮，稳步推进", `整军强攻，争取${record?.objective || "先机"}`, "遣使探察，再定进退"];
    document.querySelectorAll(".office-decision-option").forEach((input, index) => { if (!input.value) input.value = decisionDefaults[index]; });
    renderOfficeDiplomacyStatus();
    renderOfficeQuiz();
    renderOfficeMandateApproval();
    renderOfficeSettlementReview();
  }

  function officeMembershipPosition(value, fallback = "军府属官") {
    const raw = String(value || "").trim();
    if (!raw) return fallback;
    if (/^commander$/i.test(raw)) return "主官";
    if (/^(?:court_officer|officer_\d+)$/i.test(raw)) return "属官";
    return raw;
  }

  function renderOfficeMembership(rosterOverride) {
    const roster = rosterOverride || profile.organization.remoteRoster || {};
    const membership = roster.playerMembership;
    const vacancies = Array.isArray(roster.openPositions) ? roster.openPositions : [];
    const apply = $("#officeMembershipApply");
    const leave = $("#officeMembershipLeave");
    const confirmLeave = $("#officeMembershipLeaveConfirm");
    if (!apply || !leave || !confirmLeave) return;
    if (membership) {
      const manager = membership.directManagerHeroId ? displayName(membership.directManagerHeroId) : "军府主官";
      $("#officeMembershipState").textContent = `已入仕 · ${officeMembershipPosition(membership.office)}`;
      $("#officeMembershipDetail").textContent = `直属 ${manager} · 功绩 ${Number(membership.lifetimeEarned || 0)} · 可用贡献 ${Number(membership.contributionBalance || 0)}`;
    } else {
      $("#officeMembershipState").textContent = "尚未入仕";
      $("#officeMembershipDetail").textContent = vacancies.length
        ? `军府尚有 ${vacancies.length} 席可申请 · ${vacancies.map((entry) => officeMembershipPosition(entry.office)).join("、")}`
        : "当前没有可申请的军府席位";
      officeMembershipLeavePending = false;
    }
    apply.hidden = Boolean(membership);
    leave.hidden = !membership || officeMembershipLeavePending;
    confirmLeave.hidden = !membership || !officeMembershipLeavePending;
    apply.disabled = officeMembershipBusy || !vacancies.length;
    leave.disabled = officeMembershipBusy;
    confirmLeave.disabled = officeMembershipBusy;
    renderOfficeCareer(roster);
  }

  function renderOfficeCareer(rosterOverride) {
    const roster = rosterOverride || profile.organization.remoteRoster || {};
    const membership = roster.playerMembership;
    const panel = $("#officeCareer");
    if (!panel) return;
    panel.hidden = !membership;
    if (!membership) return;
    $("#officeCareerAccount").textContent = `可用贡献 ${Number(membership.contributionBalance || 0)} · 累计功绩 ${Number(membership.lifetimeEarned || 0)}`;
    panel.querySelectorAll("button, input").forEach((control) => { control.disabled = officeCareerBusy; });
  }

  async function requestOfficeCareer(action, detail = "") {
    if (integration.isOffline() || officeCareerBusy || !profile.organization.remoteRoster?.playerMembership) return;
    const commands = {
      options: "请列出我当前岗位可以领取的组织任务。",
      request: `我申请领取组织任务：${detail}，请现在派发给我。`,
      inbox: "请列出你与我之间已经下发、已经领取的组织任务和待办事项。",
      accept: "我接受你刚才下发给我的组织任务。",
      result: "我已完成当前组织任务，请审核我的完成成果。"
    };
    const content = action === "result"
      ? `${commands.result}完成情况：${detail}`
      : commands[action];
    if (!content) return;
    officeCareerBusy = true;
    renderOfficeCareer();
    $("#officeCareerFeedback").textContent = ({ options: "正在向杜伯查询可领差事……", request: "领差申请已送杜伯，等待派发……", inbox: "正在调阅我的任务待办……", accept: "受命回执已送杜伯……", result: "复命已送杜伯，等待审核与贡献结算……" })[action];
    try {
      await syncOfficeNpcs(profile.organization.members.filter((member) => member.id === "DuBo"));
      const accepted = await integration.sendNpcMessage("DuBo", content);
      let reply = null;
      for (let attempt = 0; attempt < 90; attempt += 1) {
        if (attempt) await sleep(1000);
        const messages = await integration.npcCorrespondence("DuBo", 20).catch(() => ({ messages: [] }));
        reply = (messages.messages || []).find((message) => message.taskId === accepted.taskId) || null;
        if (reply) break;
      }
      const roster = await integration.organizationRoster();
      profile.organization = organization.recordRemoteRoster(profile.organization, roster, displayName);
      $("#officeCareerFeedback").textContent = reply?.content || "军府已受理，权威回信稍后可在府中书问查看。";
      if (action === "request" && detail) $("#officeCareerTaskName").value = "";
      if (action === "result" && detail) $("#officeCareerResult").value = "";
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      renderOrganizationPanel();
      if ($("#officeMemberSelect").value === "DuBo") await refreshOfficeCorrespondence(profile.organization.members.find((member) => member.id === "DuBo"));
    } catch (error) {
      $("#officeCareerFeedback").textContent = error.message || "差事请求暂未送达。";
    } finally {
      officeCareerBusy = false;
      renderOfficeCareer();
    }
  }

  function submitOfficeCareerResult(event) {
    event.preventDefault();
    const summary = $("#officeCareerResult").value.trim();
    if (!summary) return;
    requestOfficeCareer("result", summary);
  }

  function submitOfficeCareerRequest(event) {
    event.preventDefault();
    const taskName = $("#officeCareerTaskName").value.trim();
    if (!taskName) return;
    requestOfficeCareer("request", taskName);
  }

  async function requestOfficeMembership(action) {
    if (integration.isOffline() || officeMembershipBusy) return;
    if (action === "leave") {
      officeMembershipLeavePending = true;
      $("#officeMembershipFeedback").textContent = "请再次确认辞仕；确认后将立即提交军府实账。";
      renderOfficeMembership();
      return;
    }
    const content = {
      join: "我明确要求你现在提交我的加入组织申请：应聘东周朝廷军府属官岗位。",
      confirmLeave: "我要退出东周朝廷。"
    }[action];
    if (!content) return;
    officeMembershipBusy = true;
    renderOfficeMembership();
    $("#officeMembershipFeedback").textContent = action === "join" ? "请仕书已送杜伯，等待裁定……" : action === "leave" ? "请辞已送杜伯，等待确认……" : "辞仕确认已送杜伯，等待实账回读……";
    try {
      await syncOfficeNpcs(profile.organization.members.filter((member) => member.id === "DuBo"));
      const accepted = await integration.sendNpcMessage("DuBo", content);
      let reply = null;
      for (let attempt = 0; attempt < 180; attempt += 1) {
        if (attempt) await sleep(1000);
        const [messages, roster] = await Promise.all([
          integration.npcCorrespondence("DuBo", 12).catch(() => ({ messages: [] })),
          integration.organizationRoster()
        ]);
        profile.organization = organization.recordRemoteRoster(profile.organization, roster, displayName);
        reply = (messages.messages || []).find((message) => message.taskId === accepted.taskId) || reply;
        const joined = Boolean(profile.organization.remoteRoster?.playerMembership);
        if ((action === "join" && joined) || (action === "confirmLeave" && !joined)) break;
      }
      const joined = Boolean(profile.organization.remoteRoster?.playerMembership);
      if (action === "join" && joined) {
        $("#officeMembershipFeedback").textContent = "杜伯已准请仕，仕籍与贡献账户已写入朝议实账。";
      } else if (action === "confirmLeave" && !joined) {
        officeMembershipLeavePending = false;
        $("#officeMembershipFeedback").textContent = "辞仕已完成，军府席位已经释放。";
      } else {
        $("#officeMembershipFeedback").textContent = reply?.content || "组织尚未变更，请稍后重试或在府中书问查看回信。";
      }
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
      renderOrganizationPanel();
    } catch (error) {
      $("#officeMembershipFeedback").textContent = error.message || "仕籍请求暂未送达。";
    } finally {
      officeMembershipBusy = false;
      renderOfficeMembership();
    }
  }

  async function refreshIntegrationStatus() {
    try {
      const response = await integration.status();
      const services = response.services || {};
      profile.organization = organization.updateBackend(profile.organization, {
        nexusKernel: Boolean(services.nexusKernel?.online), orgFlow: Boolean(services.orgFlow?.online), aiNpc: Boolean(services.aiNpc?.online), knowledge: Boolean(services.knowledge?.online), remoteId: response.organizationId || profile.organization.remoteId || ""
      });
      if (services.orgFlow?.online) {
        const roster = await integration.organizationRoster();
        profile.organization = organization.recordRemoteRoster(profile.organization, roster, displayName);
        await refreshOfficeInventory();
      }
    } catch (_) {
      profile.organization = organization.updateBackend(profile.organization, { nexusKernel: false, orgFlow: false, aiNpc: false, knowledge: false });
    }
    writeJson(PROFILE_KEY, profile);
    renderOrganizationPanel();
  }

  function scheduleOfficeNpcRefresh(memberId) {
    clearTimeout(officeNpcRefreshTimer);
    officeNpcRefreshTimer = setTimeout(() => {
      officeNpcRefreshTimer = null;
      if (!$("#campaignOfficeBackdrop").hidden && $("#officeMemberSelect").value === memberId) refreshOfficeNpcState();
    }, 5000);
  }

  function isCurrentOfficeNpcRequest(serial, memberId) {
    return serial === officeNpcRefreshSerial && !$("#campaignOfficeBackdrop").hidden && $("#officeMemberSelect").value === memberId;
  }

  let officeCorrespondenceView = [];
  let officeKnownNpcIds = {};

  function officeNpcPeerName(state, targetId) {
    const heroId = Object.entries(state.knownNpcIds || {}).find(([, npcId]) => String(npcId) === String(targetId))?.[0];
    return profile.organization.members.find((member) => member.id === heroId)?.name || "未具名人物";
  }

  function officeCanonicalMemberName(name) {
    const raw = String(name || "");
    const heroId = Object.entries(officeKnownNpcIds).find(([, npcId]) => String(npcId) === raw)?.[0] || raw;
    return profile.organization.members.find((member) => member.id === heroId)?.name || KNOWN_NAMES[heroId] || raw;
  }

  function officeAffectionText(type) {
    return ({ love: "亲爱", respect: "敬重", trust: "信赖", friendship: "亲善", hatred: "仇恨", disgust: "厌恶", fear: "畏惧" })[String(type || "").toLowerCase()] || "牵挂";
  }

  function officeRelationshipText(item) {
    if (item.title) return item.title;
    return ({ superior_subordinate: "上下级", family: "亲族", friend: "友朋", rival: "对手", organization: "同僚" })[item.relation_sub || item.relation_type] || "往来";
  }

  function officeNpcRelations(state, affection, relationships) {
    const rows = [];
    for (const item of Array.isArray(affection.items) ? affection.items : []) {
      rows.push(`<li><strong>${escapeHtml(officeNpcPeerName(state, item.target_id))}</strong><span>${escapeHtml(officeAffectionText(item.dominant_affection_type))} ${Math.round(Number(item.max_value || 0))}</span></li>`);
    }
    for (const item of Array.isArray(relationships.items) ? relationships.items.filter((entry) => entry?.is_active !== false) : []) {
      rows.push(`<li><strong>${escapeHtml(officeNpcPeerName(state, item.target_id))}</strong><span>${escapeHtml(officeRelationshipText(item))}${item.is_bilateral ? " · 相互" : ""}</span></li>`);
    }
    return rows.length ? `<div class="office-npc-relations"><span>人情簿</span><ul>${rows.slice(0, 8).join("")}</ul></div>` : "";
  }

  function renderOfficeCorrespondence(member) {
    const panel = $("#officeCorrespondence");
    if (!panel || !member) return;
    const selected = profile.organization.selectedCorrespondence?.[String(officeStage()?.id || "")];
    panel.innerHTML = officeCorrespondenceView.map((message) => {
      const isSelected = selected?.messageId === message.messageId && selected?.heroId === member.id;
      const peerName = officeCanonicalMemberName(message.speakerId === message.npcId ? message.targetName : message.speakerName);
      const speakerName = message.speakerId === message.npcId ? member.name : officeCanonicalMemberName(message.speakerName);
      return `<div class="office-correspondence-item${isSelected ? " selected" : ""}"><strong>${escapeHtml(speakerName || member.name)}</strong><button class="large-button" type="button" data-correspondence-id="${escapeHtml(message.messageId)}">${isSelected ? "已取用" : "取为线索"}</button><span>${escapeHtml(message.content)}</span><small>${escapeHtml(peerName || "府中属官")} · ${escapeHtml(message.emotion || "calm")} · 印记 ${escapeHtml(String(message.digest || "").slice(0, 10))}</small></div>`;
    }).join("") || "<p>尚未收到与该属官有关的府中耳报。</p>";
  }

  async function refreshOfficeCorrespondence(memberOverride, requestSerial) {
    const member = memberOverride || profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const panel = $("#officeCorrespondence");
    if (!panel || !member) return [];
    if (integration.isOffline()) { officeCorrespondenceView = []; panel.innerHTML = "<p>离线演算不调阅实时耳报。</p>"; return []; }
    panel.innerHTML = "<p>正在调阅府中书问…</p>";
    try {
      const response = await integration.npcCorrespondence(member.id, 12);
      if (requestSerial && !isCurrentOfficeNpcRequest(requestSerial, member.id)) return;
      officeCorrespondenceView = Array.isArray(response.messages) ? response.messages.map((message) => ({ ...message, npcId: response.npcId })) : [];
      renderOfficeCorrespondence(member);
      return officeCorrespondenceView;
    } catch (error) {
      if (requestSerial && !isCurrentOfficeNpcRequest(requestSerial, member.id)) return;
      officeCorrespondenceView = [];
      panel.innerHTML = "<p>书问暂不可达。</p>";
      return [];
    }
  }

  async function sendOfficeNpcMessage(event) {
    event.preventDefault();
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const input = $("#officeMessageInput");
    const button = event.currentTarget.querySelector("button[type=submit]");
    const content = input.value.trim();
    if (!member || !content || integration.isOffline()) return;
    button.disabled = true;
    try {
      const accepted = await integration.sendNpcMessage(member.id, content);
      input.value = "";
      showNotice(`传话已送达${member.name}`);
      for (let attempt = 0; attempt < 20; attempt += 1) {
        if (attempt) await sleep(1000);
        if ($("#campaignOfficeBackdrop").hidden || $("#officeMemberSelect").value !== member.id) return;
        const messages = await refreshOfficeCorrespondence(member);
        if (messages.some((message) => message.taskId === accepted.taskId)) {
          showNotice(`${member.name}已有回信`);
          return;
        }
      }
      showNotice("传话已受理，回信稍后可在府中书问查看");
    } catch (error) {
      showNotice(error.message || "传话暂未送达");
    } finally {
      button.disabled = false;
    }
  }

  async function selectOfficeCorrespondence(messageId) {
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const message = officeCorrespondenceView.find((entry) => entry.messageId === messageId);
    if (!member || !message) return;
    try {
      const selected = organization.selectCorrespondence(profile.organization, { stageId: String(officeStage()?.id || ""), heroId: member.id, message });
      await commitOrganizationState(selected.state);
      renderOfficeCorrespondence(member);
      renderOfficeCouncil();
      showNotice(`已取${message.speakerName || member.name}耳报为本回线索`);
    } catch (error) { showNotice(error.message); }
  }

  async function refreshOfficeNpcState() {
    const panel = $("#officeNpcState");
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    if (!panel || !member) return;
    const serial = ++officeNpcRefreshSerial;
    clearTimeout(officeNpcRefreshTimer);
    officeNpcRefreshTimer = null;
    if (integration.isOffline()) {
      panel.innerHTML = "<p>离线演算不读取属官实时状态。</p>";
      return;
    }
    panel.innerHTML = `<p>正在调阅 ${escapeHtml(member.name)} 的属官状态…</p>`;
    try {
      await syncOfficeNpcs([member]);
      const state = await integration.npcState(member.id);
      if (!isCurrentOfficeNpcRequest(serial, member.id)) return;
      officeKnownNpcIds = { ...officeKnownNpcIds, ...(state.knownNpcIds || {}) };
      const emotion = state.emotion?.data || state.emotion || {};
      const affection = state.affection?.data || state.affection || {};
      const relationships = state.relationships?.data || state.relationships || {};
      const dominant = emotion.dominant || {};
      panel.innerHTML = `<strong>${escapeHtml(member.name)} · ${escapeHtml(member.office)}</strong><dl><div><dt>心境</dt><dd>${escapeHtml(dominant.emotion_type || "calm")} ${Math.round(Number(dominant.intensity || 0))}</dd></div><div><dt>牵挂</dt><dd>${Number(affection.total || affection.items?.length || 0)}</dd></div><div><dt>人际</dt><dd>${Number(relationships.total || relationships.items?.length || 0)}</dd></div></dl>${officeNpcRelations(state, affection, relationships)}`;
      const personality = state.personality || { available: false };
      panel.querySelector("dl")?.insertAdjacentHTML("beforeend", `<div><dt>性情</dt><dd>${escapeHtml(officePersonalityText(personality))}</dd></div>`);
      const motivation = state.motivation || { available: false };
      panel.querySelector("dl")?.insertAdjacentHTML("beforeend", `<div><dt>动机</dt><dd>${escapeHtml(officeMotivationText(motivation))}</dd></div>`);
      const quality = state.quality || { available: false };
      panel.querySelector("dl")?.insertAdjacentHTML("beforeend", `<div><dt>品质</dt><dd>${escapeHtml(officeQualityText(quality))}</dd></div>`);
      officeMemoryView = Array.isArray(state.memories?.items) ? state.memories.items : [];
      if (!officeMemoryView.some((item) => item.idempotencyKey === officeSelectedMemory?.idempotencyKey)) officeSelectedMemory = null;
      renderOfficeNpcMemories(member);
      await refreshOfficeCorrespondence(member, serial);
      await refreshOfficeNpcSchedule(member, serial);
    } catch (error) {
      if (!isCurrentOfficeNpcRequest(serial, member.id)) return;
      panel.innerHTML = `<p>${escapeHtml(member.name)} 的属官服务正在恢复，恢复后将自动刷新。</p>`;
      officeMemoryView = [];
      officeSelectedMemory = null;
      renderOfficeNpcMemories(member);
      scheduleOfficeNpcRefresh(member.id);
    }
  }

  function renderOfficeNpcMemories(member) {
    const panel = $("#officeNpcMemories");
    if (!panel) return;
    if (integration.isOffline()) { panel.innerHTML = "<p>离线演算不调阅属官旧事。</p>"; return; }
    panel.innerHTML = `<div class="office-memory-heading"><strong>${escapeHtml(member?.name || "属官")}旧事</strong><small>可取一事作为本回军议依据</small></div>${officeMemoryView.slice(0, 6).map((memory) => {
      const selected = memory.idempotencyKey === officeSelectedMemory?.idempotencyKey;
      return `<div class="office-memory-item${selected ? " selected" : ""}"><span>${escapeHtml(memory.content)}</span><button class="large-button" type="button" data-memory-id="${escapeHtml(memory.idempotencyKey)}">${selected ? "已取用" : "取为旧事"}</button><small>${escapeHtml(memory.sourceType || "旧事")} · 印记 ${escapeHtml(String(memory.digest || "").slice(0, 10))}</small></div>`;
    }).join("") || "<p>尚无可引用旧事；完成一次军议后将由属官记取。</p>"}`;
  }

  function selectOfficeMemory(memoryId) {
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const memory = officeMemoryView.find((entry) => entry.idempotencyKey === memoryId);
    if (!member || !memory) return;
    officeSelectedMemory = officeSelectedMemory?.idempotencyKey === memoryId ? null : memory;
    renderOfficeNpcMemories(member);
    renderOfficeCouncil();
  }

  async function refreshOfficeNpcSchedule(memberOverride, requestSerial) {
    const panel = $("#officeNpcSchedule");
    const member = memberOverride || profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    if (!panel || !member || integration.isOffline()) return;
    panel.textContent = "正在查阅日程…";
    try {
      const response = await integration.npcSchedule(member.id);
      if (requestSerial && !isCurrentOfficeNpcRequest(requestSerial, member.id)) return;
      const plan = response.schedule?.data || response.schedule || {};
      const days = Array.isArray(plan.schedules) ? plan.schedules : [];
      const day = days[0] || null;
      const lastDay = days.at(-1) || null;
      const events = Array.isArray(day?.events) ? day.events.slice(0, 5).map((event) => event.name).filter(Boolean) : [];
      panel.innerHTML = days.length
        ? `<strong>${days.length} 日当值</strong><span>${escapeHtml(day.date || plan.start_date || "近日")} 至 ${escapeHtml(lastDay?.date || plan.end_date || "未定")}</span><small>${events.length ? `首日：${escapeHtml(events.join("、"))}` : "首日尚无定事"} · 计划 ${escapeHtml(String(plan.plan_id || plan.generation_id || "未具名").slice(0, 24))}</small>`
        : "尚无已定日程";
      await refreshOfficeNpcAssignment(member, requestSerial);
    } catch (error) {
      if (requestSerial && !isCurrentOfficeNpcRequest(requestSerial, member.id)) return;
      panel.textContent = "日程服务正在恢复，将自动重试…";
      scheduleOfficeNpcRefresh(member.id);
    }
  }

  function officeAssignmentKey(memberId, taskType, stageId) {
    return [memberId, taskType, stageId].join(":");
  }

  const OFFICE_TRAIT_LABELS = {
    calm: "沉着", dominant: "强势", smooth: "圆融", protective: "护持",
    cautious: "谨慎", impulsive: "冲动", extroverted: "外向",
    introverted: "内敛", stubborn: "固执", decisive: "果决",
    sensitive: "敏锐", steady: "稳重"
  };

  function officePersonalityText(personality) {
    if (personality?.available !== true) return "未建档";
    const traits = personality.traits || {};
    const dominant = Array.isArray(personality.dominantTraits) ? personality.dominantTraits : [];
    return dominant.map((trait) => `${OFFICE_TRAIT_LABELS[trait] || trait} ${Number(traits[trait] || 0)}`).join(" · ") || "已建档";
  }

  function officeMotivationText(motivation) {
    if (motivation?.available !== true || !Array.isArray(motivation.motives) || !motivation.motives.length) return "暂无记录";
    return motivation.motives.slice(0, 3).map((motive) => `${motive.name} ${Number(motive.score)}`).join("、");
  }

  const OFFICE_QUALITY_LABELS = {
    responsibility: "担当", integrity: "操守", trustworthiness: "信义", fairness: "公正",
    courage: "勇毅", tolerance: "宽容", humility: "谦逊", greed: "贪欲",
    selfishness: "自私", cruelty: "酷烈", hypocrisy: "虚伪", meanness: "刻薄"
  };

  function officeQualityText(quality) {
    if (quality?.available !== true || !quality.qualities) return "未建档";
    const dominant = Array.isArray(quality.dominantQualities) ? quality.dominantQualities : [];
    const names = dominant.length
      ? dominant
      : Object.entries(quality.qualities).sort((left, right) => Number(right[1]) - Number(left[1])).map(([name]) => name);
    return names.slice(0, 3)
      .map((name) => `${OFFICE_QUALITY_LABELS[name] || name} ${Number(quality.qualities[name] || 0)}`)
      .join(" · ") || "已建档";
  }

  async function refreshOfficeNpcAssignment(memberOverride, requestSerial, taskTypeOverride) {
    const panel = $("#officeNpcAssignment");
    const member = memberOverride || profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const taskType = taskTypeOverride || $("#officeTaskType").value;
    const stageId = String(officeStage()?.id || "");
    if (!panel || !member || !taskType || !stageId || integration.isOffline()) return null;
    panel.textContent = "正在核对本关当值…";
    try {
      const response = await integration.npcAssignment(member.id, taskType, stageId);
      if (requestSerial && !isCurrentOfficeNpcRequest(requestSerial, member.id)) return null;
      const assignment = response.assignment;
      if (!assignment?.planId || !assignment?.eventId) throw new Error("当值记录不完整");
      officeAssignmentSnapshots.set(officeAssignmentKey(member.id, taskType, stageId), assignment);
      const readiness = Number(assignment.readiness?.score);
      const readinessBand = { steady: "从容", watch: "审慎", strained: "吃紧" }[assignment.readiness?.band] || "待评";
      const readinessText = Number.isFinite(readiness) ? ` · 胜任 ${readiness}/100 · ${readinessBand}` : "";
      const state = assignment.state || {};
      panel.innerHTML = `<strong>本关当值</strong><span>${escapeHtml(assignment.date || "近日")} · ${escapeHtml(assignment.name || taskType)}${assignment.timeSlot ? ` · ${escapeHtml(assignment.timeSlot)}` : ""}</span><small>日程 ${escapeHtml(String(assignment.planId).slice(0, 18))} · 重要度 ${Number(assignment.importance || 0)}${readinessText}</small><small class="office-npc-readiness">情绪 ${escapeHtml(state.emotion || "calm")} ${Number(state.intensity || 0)} · 关系 ${Number(state.relationshipCount || 0)} · 好感 ${Number(state.affectionCount || 0)}</small>`;
      const fit = Number(assignment.personality?.fit?.score);
      const fitBand = { strong: "相合", steady: "可任", strained: "相冲" }[assignment.personality?.fit?.band] || "待评";
      const fitText = assignment.personality?.fit?.available === true && Number.isFinite(fit) ? `适岗 ${fit}/100 · ${fitBand}` : "适岗未建档";
      panel.insertAdjacentHTML("beforeend", `<small class="office-npc-personality">${escapeHtml(fitText)} · 性情 ${escapeHtml(officePersonalityText(assignment.personality))}</small>`);
      const willingness = Number(assignment.motivation?.fit?.score);
      const willingnessBand = { strong: "强烈", willing: "愿任", neutral: "中性", reluctant: "勉强" }[assignment.motivation?.fit?.band] || "待评";
      const willingnessText = assignment.motivation?.fit?.available === true && Number.isFinite(willingness) ? `意愿 ${willingness}/100 · ${willingnessBand}` : "意愿暂无记录";
      panel.insertAdjacentHTML("beforeend", `<small class="office-npc-motivation">${escapeHtml(willingnessText)} · 动机 ${escapeHtml(officeMotivationText(assignment.motivation))}</small>`);
      const qualityScore = Number(assignment.quality?.fit?.score);
      const qualityBand = { strong: "可信", steady: "可察", strained: "存疑" }[assignment.quality?.fit?.band] || "待评";
      const qualityText = assignment.quality?.fit?.available === true && Number.isFinite(qualityScore) ? `品行 ${qualityScore}/100 · ${qualityBand}` : "品行未建档";
      panel.insertAdjacentHTML("beforeend", `<small class="office-npc-quality">${escapeHtml(qualityText)} · 品质 ${escapeHtml(officeQualityText(assignment.quality))}</small>`);
      return assignment;
    } catch (error) {
      officeAssignmentSnapshots.delete(officeAssignmentKey(member.id, taskType, stageId));
      panel.textContent = `本关没有可核验的当值安排：${error.message}`;
      return null;
    }
  }

  async function generateOfficeNpcSchedule() {
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    if (!member) return;
    const button = $("#officeScheduleButton");
    button.disabled = true;
    $("#officeNpcSchedule").textContent = "正在拟定日程…";
    try {
      await integration.generateNpcSchedule(member.id);
      await refreshOfficeNpcSchedule(member);
    } catch (error) {
      $("#officeNpcSchedule").textContent = "日程服务正在恢复，请稍候重试。";
      scheduleOfficeNpcRefresh(member.id);
    } finally {
      button.disabled = false;
    }
  }

  function currentOfficeEvidence() {
    const stageId = String(officeStage()?.id || "");
    const source = profile.organization.selectedSources?.[stageId];
    const knowledge = source ? profile.organization.knowledge.find((entry) => entry.id === source.knowledgeId && entry.stageId === stageId) : null;
    return source && knowledge ? { source, knowledge } : null;
  }

  function currentOfficeThought() {
    const stageId = String(officeStage()?.id || "");
    const evidence = currentOfficeEvidence();
    const heroId = $("#officeMemberSelect").value;
    const taskType = $("#officeTaskType").value;
    return [...(profile.organization.thoughts || [])].reverse().find((entry) => entry.stageId === stageId && entry.heroId === heroId && entry.taskType === taskType && entry.knowledgeId === evidence?.knowledge.id && Number(entry.source?.index) === Number(evidence?.source.index));
  }

  function currentOfficeCouncil() {
    const stageId = String(officeStage()?.id || "");
    const evidence = currentOfficeEvidence();
    const heroId = $("#officeMemberSelect").value;
    const correspondence = profile.organization.selectedCorrespondence?.[stageId];
    const activeCorrespondence = correspondence?.heroId === heroId ? correspondence : null;
    return [...profile.organization.councils].reverse().find((entry) => entry.stageId === stageId && entry.memberId === heroId && entry.knowledgeId === evidence?.knowledge.id && Number(entry.evidenceSource?.index) === Number(evidence?.source.index) && (entry.correspondence?.digest || null) === (activeCorrespondence?.digest || null));
  }

  function renderOfficeCouncil() {
    const council = currentOfficeCouncil();
    const control = $("#officeUseCouncil");
    const contextKey = council ? [council.stageId, council.memberId, council.knowledgeId, council.correspondence?.digest || "", council.id].join(':') : "";
    if (control.dataset.councilContext !== contextKey) control.checked = false;
    control.dataset.councilContext = contextKey;
    control.disabled = !council;
    const evidence = currentOfficeEvidence();
    $("#officeCouncilHint").textContent = council ? "已保存：" + council.memberName + "据" + council.evidenceSource.work + (council.correspondence ? "及府中耳报" : "") + (council.thought ? "，采纳自主进言" : "") + "建议“" + council.text + "”。联网授命须勾选并由内核签发军令。" : evidence ? "已选证：" + evidence.source.work + "（" + evidence.source.tier + "）。请当前属官据此参议。" : "先查本回史料并选定出处，再请当前属官参议。";
    const thought = currentOfficeThought();
    $("#officeThoughtButton").disabled = officeThoughtInFlight || integration.isOffline() || !evidence;
    if (!officeThoughtInFlight) {
      $("#officeThoughtResult").innerHTML = thought?.thought?.hasThought
        ? `<strong>${escapeHtml(thought.heroId === $("#officeMemberSelect").value ? "属官进言" : "进言")}</strong><span>${escapeHtml(thought.thought.description)} · 重要度 ${Number(thought.thought.importance)} · 印记 ${escapeHtml(String(thought.digest || "").slice(0, 10))}</span>`
        : thought ? "当前当值与史料未引发新的进言。" : "";
    }
  }

  let officeThoughtInFlight = false;
  async function requestOfficeNpcThought() {
    if (officeThoughtInFlight || integration.isOffline()) return;
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const stage = officeStage();
    const evidence = currentOfficeEvidence();
    const taskType = $("#officeTaskType").value;
    if (!member || !stage || !evidence) {
      $("#officeThoughtResult").textContent = "请先选择属官、本回史料和出处。";
      return;
    }
    const context = [String(stage.id), member.id, taskType, evidence.knowledge.id, Number(evidence.source.index)].join(":");
    officeThoughtInFlight = true;
    $("#officeThoughtButton").disabled = true;
    $("#officeThoughtResult").textContent = `${member.name}正在据当值与史料斟酌进言…`;
    try {
      const response = await integration.npcThought(member.id, {
        stage_id: String(stage.id),
        stage_title: String(stage.battleTitle || stage.title || "未名战事"),
        knowledge_id: evidence.knowledge.id,
        evidence_source_index: Number(evidence.source.index),
        task_type: taskType
      });
      const currentEvidence = currentOfficeEvidence();
      const currentContext = [String(officeStage()?.id || ""), $("#officeMemberSelect").value, $("#officeTaskType").value, currentEvidence?.knowledge.id, Number(currentEvidence?.source.index)].join(":");
      if (context !== currentContext) throw new Error("进言期间选择已改变，请恢复原选择后重试");
      if (response.state !== "COMPLETED" || !response.thoughtReceipt) throw new Error("属官尚未形成可核验进言");
      const noted = organization.recordThought(profile.organization, response.thoughtReceipt);
      await integration.persist({ ...profile, organization: noted.state });
      profile.organization = noted.state;
      writeJson(PROFILE_KEY, profile);
      if (noted.thought.thought.hasThought) {
        const options = [...document.querySelectorAll(".office-decision-option")];
        options[2].value = noted.thought.councilProposal;
      }
    } catch (error) {
      $("#officeThoughtResult").textContent = `进言暂不可用：${error.message}`;
    } finally {
      officeThoughtInFlight = false;
      renderOfficeCouncil();
    }
  }

  let officeLobbyInFlight = false;
  function renderOfficeDiplomacyStatus() {
    const panel = $("#officeDiplomacyResult");
    if (!panel || officeLobbyInFlight || officeDiplomacyMutationInFlight) return;
    const targetId = $("#officeDiplomacyTarget").value;
    const alliance = [...profile.organization.diplomacy.alliances].reverse().find((entry) => entry.targetId === targetId && entry.status === "active");
    if (alliance) {
      panel.textContent = `与${alliance.targetName}的盟约正在生效。`;
      return;
    }
    const activeTask = [...profile.organization.tasks].reverse().find((task) => task.status === "active" && task.operation?.kind === "diplomacy" && task.operation.target_id === targetId);
    if (activeTask) {
      panel.textContent = `${activeTask.assigneeName}正奉内核军令出使${activeTask.operation.target_name}，须待 orgFlow 复命。`;
      return;
    }
    const lobbying = [...profile.organization.diplomacy.lobbying].reverse().find((entry) => entry.targetId === targetId);
    if (lobbying?.outcome === "accepted") panel.textContent = `${lobbying.targetName}已接受“${lobbying.proposal}”，可正式缔盟。`;
    else if (lobbying) panel.textContent = `${lobbying.targetName}未接受最近一次主张，须重新请领外交差事。`;
    else panel.textContent = "外交军令须引用本回史料与属官军议，并经 orgFlow 复命后方可缔盟。";
  }

  async function commitOrganizationState(next) {
    if (integration.isOffline()) {
      saveOrganization(next);
      return;
    }
    await integration.persist({ ...profile, organization: next });
    profile.organization = next;
    writeJson(PROFILE_KEY, profile);
    renderOrganizationPanel();
    if (profile.organization.backend.aiNpc) {
      await syncOfficeNpcs(profile.organization.members).then(() => warmCurrentOfficeNpcSchedules()).catch(() => {});
    }
  }

  function syncOfficeNpcs(members, force = false) {
    if (integration.isOffline()) return Promise.resolve();
    const requested = [...new Map((members || [])
      .filter((member) => member?.id && member?.name)
      .map((member) => [member.id, member])).values()];
    officeNpcSyncQueue = officeNpcSyncQueue.catch(() => {}).then(async () => {
      const pending = force ? requested : requested.filter((member) => !syncedNpcIds.has(member.id));
      if (!pending.length) return;
      await integration.syncNpcs(pending.map((member) => ({ heroId: member.id, name: member.name })));
      pending.forEach((member) => syncedNpcIds.add(member.id));
    });
    return officeNpcSyncQueue;
  }

  function warmOfficeNpcSchedules(members, force = false) {
    if (integration.isOffline()) return;
    for (const member of members || []) {
      if (!member?.id || (!force && warmedNpcScheduleIds.has(member.id))) continue;
      warmedNpcScheduleIds.add(member.id);
      // AINPC continues expired-plan regeneration after its HTTP wait budget. The
      // organization worker then retries the same frozen private-chat intent.
      integration.generateNpcSchedule(member.id).catch(() => {});
    }
  }

  function warmCurrentOfficeNpcSchedules(force = false) {
    const members = profile.organization.members;
    const manager = members.find((member) => member.id === "DuBo") || { id: "DuBo", name: displayName("DuBo") };
    const assignee = members.find((member) => member.id === $("#officeMemberSelect").value);
    warmOfficeNpcSchedules([manager, assignee], force);
  }

  function schedulePlanId(response) {
    return response?.schedule?.data?.plan_id || response?.data?.plan_id || null;
  }

  async function ensureOfficeNpcScheduleReady(member) {
    if (!member?.id) return;
    let previousPlanId = null;
    try {
      previousPlanId = schedulePlanId(await integration.npcSchedule(member.id));
    } catch (_) {}
    try {
      await integration.generateNpcSchedule(member.id);
      return;
    } catch (_) {
      // Expired-plan generation is durable and can outlive the gateway HTTP budget.
    }
    const deadline = Date.now() + 180000;
    while (Date.now() < deadline) {
      await sleep(2000);
      try {
        const currentPlanId = schedulePlanId(await integration.npcSchedule(member.id));
        if (currentPlanId && currentPlanId !== previousPlanId) return;
      } catch (_) {}
    }
    throw new Error(`${member.name || member.id}的当值日程尚未续拟完成`);
  }

  async function ensureCurrentOfficeNpcSchedulesReady() {
    const members = profile.organization.members;
    const manager = members.find((member) => member.id === "DuBo") || { id: "DuBo", name: displayName("DuBo") };
    const assignee = members.find((member) => member.id === $("#officeMemberSelect").value);
    await Promise.all([manager, assignee].filter(Boolean).map(ensureOfficeNpcScheduleReady));
  }

  async function lobbyPolity() {
    if (officeLobbyInFlight || officeCouncilInFlight || officeOrderInFlight) return;
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const stageId = String(officeStage()?.id || "");
    const evidence = currentOfficeEvidence();
    const knowledge = evidence?.knowledge;
    const council = currentOfficeCouncil();
    const target = $("#officeDiplomacyTarget");
    const targetId = target.value;
    const targetName = target.selectedOptions[0]?.textContent || targetId;
    const proposal = $("#officeDiplomacyProposal").value.trim();
    const panel = $("#officeDiplomacyResult");
    if (!member || !knowledge || !council || !proposal) { panel.textContent = "请先查本回史料并由当前使者完成军议，再提出盟约。"; return; }
    officeLobbyInFlight = true;
    $("#officeLobbyButton").disabled = true;
    panel.textContent = member.name + "正在请领外交差事…";
    try {
      if (integration.isOffline()) {
        const accepted = organization.hash([stageId, member.id, targetId, proposal, profile.organization.month].join(":")) % 100 < 65;
        const noted = organization.recordLobbying(profile.organization, { id: "lobby:offline:" + organization.hash([stageId, member.id, targetId, proposal].join(":")), stageId, targetId, targetName, memberId: member.id, knowledgeId: knowledge.id, councilId: council.id, proposal, outcome: accepted ? "accepted" : "rejected", decision: { type: "OFFLINE", index: accepted ? 0 : 1 } });
        await commitOrganizationState(noted.state);
        panel.textContent = accepted ? targetName + "已接受主张，可正式缔盟。" : targetName + "拒绝了本次主张。";
        return;
      }
      const task = await issueOfficeTask({ kind: "diplomacy", target_id: targetId, target_name: targetName, proposal });
      panel.textContent = task ? `${member.name}已奉内核军令出使${targetName}，须待 orgFlow 复命后方可缔盟。` : "外交差事未获受理，请核对军议与服务状态。";
    } catch (error) { panel.textContent = "游说暂不可用：" + error.message; }
    finally { officeLobbyInFlight = false; $("#officeLobbyButton").disabled = false; }
  }

  let officeDiplomacyMutationInFlight = false;
  async function signAlliance() {
    if (officeDiplomacyMutationInFlight) return;
    const targetId = $("#officeDiplomacyTarget").value;
    const lobbying = [...profile.organization.diplomacy.lobbying].reverse().find((entry) => entry.targetId === targetId);
    officeDiplomacyMutationInFlight = true;
    try {
      if (!lobbying || lobbying.outcome !== "accepted") throw new Error("该诸侯尚未接受最近一次游说");
      const signed = organization.createAlliance(profile.organization, { id: "pact:" + lobbying.id, lobbyingId: lobbying.id, terms: [lobbying.proposal, "共享本回军情"] });
      await commitOrganizationState(signed.state);
      $("#officeDiplomacyResult").textContent = "已与" + signed.alliance.targetName + "缔盟，盟约收入官署档案。";
    } catch (error) { $("#officeDiplomacyResult").textContent = error.message; }
    finally { officeDiplomacyMutationInFlight = false; }
  }

  async function betrayAlliance() {
    if (officeDiplomacyMutationInFlight) return;
    const targetId = $("#officeDiplomacyTarget").value;
    const alliance = profile.organization.diplomacy.alliances.find((entry) => entry.targetId === targetId && entry.status === "active");
    officeDiplomacyMutationInFlight = true;
    try {
      if (!alliance) throw new Error("该诸侯没有生效盟约");
      const broken = organization.breakAlliance(profile.organization, { allianceId: alliance.id, stageId: String(officeStage()?.id || ""), reason: $("#officeDiplomacyProposal").value.trim() || "因战局而背盟" });
      await commitOrganizationState(broken.state);
      $("#officeDiplomacyResult").textContent = "已背弃与" + alliance.targetName + "的盟约；本战获得突袭之利，但士气与邦交受损。";
    } catch (error) { $("#officeDiplomacyResult").textContent = error.message; }
    finally { officeDiplomacyMutationInFlight = false; }
  }

  let officeCouncilInFlight = false;
  async function requestOfficeNpcDecision(event) {
    event.preventDefault();
    if (officeCouncilInFlight) return;
    const member = profile.organization.members.find((entry) => entry.id === $("#officeMemberSelect").value);
    const question = $("#officeDecisionQuestion").value.trim();
    const options = [...document.querySelectorAll(".office-decision-option")].map((input) => input.value.trim()).filter(Boolean);
    if (!member || !question || options.length < 2) return;
    const panel = $("#officeDecisionResult");
    const stageId = String(officeStage()?.id || "");
    const evidence = currentOfficeEvidence();
    const knowledge = evidence?.knowledge;
    if (!knowledge || !evidence?.source) { panel.textContent = "请先查阅本回史料并选定出处，再请属官参议。"; return; }
    const sourceMarker = "选证：" + evidence.source.work + "｜" + evidence.source.tier;
    const retrievalMarker = evidence.source.searchReceipt ? "\n检索回执：" + evidence.source.searchReceipt.digest.slice(0, 12) + "\n发现路径：" + knowledgeRetrievalText(knowledge) : "";
    const correspondence = profile.organization.selectedCorrespondence?.[stageId];
    const activeCorrespondence = correspondence?.heroId === member.id ? correspondence : null;
    const correspondenceMarker = activeCorrespondence ? `\n耳报印记：${activeCorrespondence.digest.slice(0, 12)}\n耳报：${activeCorrespondence.speakerName}“${activeCorrespondence.content.slice(0, 420)}”` : "";
    const activeMemory = officeSelectedMemory;
    const memoryMarker = activeMemory ? `\n记忆印记：${activeMemory.digest.slice(0, 12)}\n旧事：${activeMemory.content.slice(0, 420)}` : "";
    const contextualQuestion = (question.slice(0, 750) + "\n史料：" + knowledge.name + "（" + knowledge.id + "）\n" + sourceMarker + retrievalMarker + correspondenceMarker + memoryMarker + "\n适用范围：" + String(evidence.source.scope || "未注明") + "\n" + String(knowledge.summary || "").slice(0, 450)).slice(0, 2000);
    officeCouncilInFlight = true;
    panel.textContent = `${member.name}正在权衡…`;
    try {
      const response = await integration.npcDecision(member.id, contextualQuestion, options, stageId, activeMemory);
      if (String(officeStage()?.id || "") !== stageId || $("#officeMemberSelect").value !== member.id || $("#officeDecisionQuestion").value.trim() !== question || JSON.stringify([...document.querySelectorAll(".office-decision-option")].map((input) => input.value.trim()).filter(Boolean)) !== JSON.stringify(options)) { panel.textContent = "选择已改变，本轮结果不用于当前派差，请重新参议。"; return; }
      const selected = response.decision?.data || response.decision || {};
      if (response.state !== "COMPLETED" || selected.type !== "OPTION") throw new Error("军议尚未返回有效方案");
      const currentEvidence = currentOfficeEvidence();
      const currentKnowledge = currentEvidence?.knowledge;
      const currentCorrespondence = profile.organization.selectedCorrespondence?.[stageId];
      if (!currentKnowledge || currentKnowledge.id !== knowledge.id || currentKnowledge.name !== knowledge.name || currentKnowledge.summary !== knowledge.summary || Number(currentEvidence?.source.index) !== Number(evidence.source.index) || (currentCorrespondence?.heroId === member.id ? currentCorrespondence.digest : null) !== (activeCorrespondence?.digest || null) || (officeSelectedMemory?.digest || null) !== (activeMemory?.digest || null)) {
        panel.textContent = "史料或选证已更新，本轮议决不落档，请重新参议。";
        return;
      }
      const thought = currentOfficeThought();
      const selectedThought = thought?.thought?.hasThought === true && thought.councilProposal === options[selected.index] ? thought : null;
      const noted = organization.recordCouncil(profile.organization, { id: response.clientRequestId, stageId, memberId: member.id, knowledgeId: knowledge.id, knowledgeName: knowledge.name, knowledgeSummary: knowledge.summary, evidenceSourceIndex: evidence.source.index, question: contextualQuestion, options, index: selected.index, dialogueReceipt: response.dialogueReceipt, ...(response.memoryReceipt ? { memory: response.memoryReceipt } : {}), ...(selectedThought ? { thoughtRequestId: selectedThought.requestId, thoughtDigest: selectedThought.digest } : {}) });
      await integration.persist({ ...profile, organization: noted.state });
      profile.organization = noted.state;
      writeJson(PROFILE_KEY, profile);
      renderOfficeCouncil();
      const text = selected.text || options[Number(selected.index)] || "未能形成裁断";
      panel.innerHTML = `<strong>${escapeHtml(member.name)}</strong><span>${escapeHtml(text)} · 对话已归档${response.memoryReceipt ? " · 旧事已核验" : ""}</span>`;
    } catch (error) {
      panel.textContent = `裁断暂不可用：${error.message}`;
    } finally {
      officeCouncilInFlight = false;
    }
  }

  function renderOfficeMandateApproval() {
    const pending = integration.pendingCourtMandate();
    const panel = $("#officeMandateApproval");
    panel.hidden = !pending;
    if (!pending) return;
    const issued = pending.result.state === "ISSUED";
    const mandate = pending.result.mandate;
    $("#officeMandateApprovalTitle").textContent = issued ? "军令已签，待下达" : "军令草案待签发";
    const emergency = mandate.emergency;
    const emergencyLabel = emergency ? ` · ${emergency.urgent ? "急报优先" : "常报"} ${Number(emergency.score).toFixed(3)}` : "";
    $("#officeMandateApprovalDetail").textContent = `${mandate.evidence?.name || "史料军令"} · ${mandate.assignment?.name || "属官当值"}${emergencyLabel} · 印记 ${String(mandate.digest || "").slice(0, 10)}`;
    $("#officeMandateApproveButton").textContent = issued ? "下达" : "签发";
    $("#officeMandateRejectButton").hidden = issued;
  }

  function renderOfficeSettlementReview() {
    const task = profile.organization.tasks.find((entry) => entry.status === "active" && entry.pendingReview?.state === "REQUIRES_ACTION");
    const panel = $("#officeSettlementReview");
    panel.hidden = !task;
    if (!task) return;
    const review = task.pendingReview.review || {};
    const settlement = task.pendingSettlement || {};
    $("#officeSettlementReviewTitle").textContent = `${task.assigneeName}复命待裁`;
    $("#officeSettlementReviewDetail").textContent = `${task.name} · ${review.finalResult || task.remoteFinalResult || "终态"} · 军府${Number(settlement.organizationDelta || 0) >= 0 ? "+" : ""}${Number(settlement.organizationDelta || 0)} · 印记 ${String(review.closureDigest || "").slice(0, 10)}`;
  }

  let officeSettlementReviewInFlight = false;
  async function resolveOfficeSettlement(decision) {
    if (officeSettlementReviewInFlight) return;
    const task = profile.organization.tasks.find((entry) => entry.status === "active" && entry.pendingReview?.state === "REQUIRES_ACTION");
    if (!task) return;
    officeSettlementReviewInFlight = true;
    $("#officeSettlementAcceptButton").disabled = true;
    $("#officeSettlementCensureButton").disabled = true;
    try {
      const response = await integration.reviewOrganizationTask(task.remoteResult, { action_id: task.pendingReview.action.actionId, decision });
      const recorded = organization.recordTaskReview(profile.organization, { taskId: task.remoteResult, review: response });
      await commitOrganizationState(recorded.state);
      if (response.inventoryReward) await refreshOfficeInventory();
      showNotice(decision === "ACCEPT"
        ? response.inventoryReward
          ? `复命已收纳，公共库藏差事额度 +${Number(response.inventoryReward.delta || 0)}，推进月令后发放战前助益。`
          : "复命已收纳，推进月令后发放战前助益。"
        : response.npcConsequence
          ? "复命已申斥，簿书功过照录且申斥已进入属官经历与好感结算，本次不发放战前助益。"
          : "复命已申斥，簿书功过照录但不发放战前助益。");
    } catch (error) {
      showNotice(error.message);
    } finally {
      officeSettlementReviewInFlight = false;
      $("#officeSettlementAcceptButton").disabled = false;
      $("#officeSettlementCensureButton").disabled = false;
    }
  }

  async function completeIssuedOfficeTask(mandateInput, issuedMandate) {
    const record = officeStage();
    const taskType = mandateInput.task_type;
    const operation = mandateInput.operation || null;
    const evidence = currentOfficeEvidence();
    const knowledge = evidence?.knowledge;
    const council = currentOfficeCouncil();
    const assigneeId = mandateInput.hero_id;
    const taskDefinition = organization.TASK_TYPES[taskType];
    if (!taskDefinition || profile.campaignResources.provisions < taskDefinition.cost) throw new Error("军粮不足，无法下达这项军令");
    if (String(record?.id || "") !== mandateInput.stage_id || $("#officeMemberSelect").value !== assigneeId || (!operation && $("#officeTaskType").value !== taskType) || knowledge?.id !== mandateInput.knowledge_id || Number(evidence?.source?.index) !== Number(mandateInput.evidence_source_index) || council?.id !== mandateInput.council_request_id) {
      throw new Error("当前关卡、属官、史料或军议已改变，请恢复原选择后再下达");
    }
    const scheduleResult = await integration.scheduleCourtMandate(issuedMandate.id, issuedMandate.digest);
    issuedMandate = { ...issuedMandate, scheduleInterruption: scheduleResult.scheduleReceipt };
    const taskBaseState = organization.recordMandate(profile.organization, issuedMandate).state;
    const created = organization.createTask(taskBaseState, {
      type: taskType, assigneeId, stageId: record?.id, stageTitle: record?.battleTitle,
      knowledgeId: knowledge.id, councilId: council.id, mandateId: issuedMandate.id, operation
    });
    const remote = await integration.createOrganizationTask({
      task_type: created.task.type,
      assignee_hero_id: created.task.assigneeId,
      stage_id: String(record?.id || "unknown"),
      stage_title: `Dongzhou stage ${record?.id || "unknown"}`,
      brief: `Dongzhou office assignment for stage ${record?.id || "unknown"}; Nexus mandate ${created.task.mandate.id}${created.task.mandate.correspondence ? `; AINPC correspondence ${created.task.mandate.correspondence.messageId}` : ""}.`,
      parameters: {
        resource_units: created.task.cost,
        assignee_name: created.task.assigneeName,
        mandate_id: created.task.mandate.id,
        mandate_digest: created.task.mandate.digest
      }
    }, created.task);
    profile.organization = organization.recordMandate(profile.organization, issuedMandate).state;
    integration.applyOrganizationOrder(profile, created.task, remote);
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    renderOrganizationPanel();
    await integration.persist(profile);
    integration.acknowledgeCourtMandate(mandateInput);
    renderOfficeMandateApproval();
    const scheduleReceipt = issuedMandate.scheduleInterruption;
    const scheduleLabel = scheduleReceipt.action === "insert_today"
      ? `，已插入今日日程“${scheduleReceipt.scheduleName}”`
      : scheduleReceipt.action === "future"
        ? `，已排入后续日程“${scheduleReceipt.scheduleName}”`
        : `，日程裁定为${scheduleReceipt.action}`;
    showNotice(`${created.task.assigneeName}已领受${created.task.name}${scheduleLabel}`);
    return created.task;
  }

  async function resolveOfficeMandate(decision) {
    if (officeOrderInFlight) return;
    const pending = integration.pendingCourtMandate();
    if (!pending) return;
    officeOrderInFlight = true;
    $("#officeMandateApproveButton").disabled = true;
    $("#officeMandateRejectButton").disabled = true;
    try {
      let result = pending.result;
      if (result.state === "REQUIRES_ACTION") {
        result = await integration.resumeCourtMandate(result.mandate.id, result.action.actionId, decision);
      }
      if (result.state === "REJECTED") {
        renderOfficeMandateApproval();
        showNotice("军令草案已驳回，未派差也未耗用军粮");
        return;
      }
      await completeIssuedOfficeTask(pending.input, result.mandate);
    } catch (error) {
      renderOfficeMandateApproval();
      showNotice(error.message);
    } finally {
      officeOrderInFlight = false;
      $("#officeMandateApproveButton").disabled = false;
      $("#officeMandateRejectButton").disabled = false;
    }
  }

  let officeOrderInFlight = false;
  async function issueOfficeTask(operation = null) {
    if (officeOrderInFlight || officeCouncilInFlight) return null;
    officeOrderInFlight = true;
    $("#officeIssueButton").disabled = true;
    const record = officeStage();
    try {
      if (!integration.isOffline() && profile.organization.backend.mode !== "connected") {
        throw new Error("史官、属官、朝议或内核尚未全部通达，联网授命已暂停");
      }
      if (!integration.isOffline() && profile.organization.backend.orgFlow && $("#officeMemberSelect").value === "DuBo") {
        showNotice("杜伯是当前组织负责人，不能向自己派单，请选择一名直属下属。");
        return null;
      }
      const taskType = operation?.kind === "diplomacy" ? "diplomacy" : $("#officeTaskType").value;
      const taskDefinition = organization.TASK_TYPES[taskType];
      if (profile.campaignResources.provisions < taskDefinition.cost) {
        showNotice("军粮不足，无法颁下这项差事");
        return null;
      }
      const evidence = currentOfficeEvidence();
      const knowledge = evidence?.knowledge;
      const council = operation ? currentOfficeCouncil() : $("#officeUseCouncil").checked ? currentOfficeCouncil() : null;
      const councilContext = council ? [council.stageId, council.memberId, council.knowledgeId, council.correspondence?.digest || "", council.id].join(':') : "";
      if ((operation || $("#officeUseCouncil").checked) && (!council || $("#officeUseCouncil").dataset.councilContext !== councilContext)) throw new Error("军议选择已变化，请重新确认引用");
      if (!integration.isOffline() && (!knowledge || !council)) throw new Error("联网授命必须引用本回史料与已保存军议");
      const assigneeId = $("#officeMemberSelect").value;
      const assignee = profile.organization.members.find((member) => member.id === assigneeId);
      const manager = profile.organization.members.find((member) => member.id === "DuBo") || { id: "DuBo", name: displayName("DuBo") };
      if (!integration.isOffline()) {
        if (!assignee) throw new Error("所选属官不在当前组织名册中");
        await syncOfficeNpcs([manager, assignee], true);
        warmOfficeNpcSchedules([manager, assignee]);
      }
      let mandateInput = null;
      let issuedMandate = null;
      let taskBaseState = profile.organization;
      if (!integration.isOffline()) {
        const assignment = await refreshOfficeNpcAssignment(assignee, null, taskType);
        if (!assignment) throw new Error("须先取得与本关差事匹配的属官当值安排");
        mandateInput = {
          stage_id: String(record?.id || "unknown"),
          stage_title: String(record?.battleTitle || record?.title || "未名战事"),
          hero_id: assigneeId,
          knowledge_id: knowledge.id,
          evidence_source_index: Number(evidence.source.index),
          schedule_plan_id: assignment.planId,
          schedule_event_id: assignment.eventId,
          council_request_id: council.id,
          decision_index: Number(council.index),
          task_type: taskType,
          ...(council.correspondence ? { correspondence_message_id: council.correspondence.messageId, correspondence_digest: council.correspondence.digest } : {}),
          ...(council.thought ? { thought_request_id: council.thought.requestId, thought_digest: council.thought.digest } : {}),
          ...(evidence.source.searchReceipt ? {
            knowledge_search_receipt_id: evidence.source.searchReceipt.id,
            knowledge_search_receipt_digest: evidence.source.searchReceipt.digest
          } : {}),
          ...(operation ? { operation } : {})
        };
        const issued = await integration.createCourtMandate(mandateInput);
        if (issued.state === "REQUIRES_ACTION") {
          renderOfficeMandateApproval();
          showNotice("军令草案已交内核封存，请明确签发或驳回");
          return null;
        }
        issuedMandate = issued.mandate;
        const operationChanged = operation && ($("#officeDiplomacyTarget").value !== operation.target_id || $("#officeDiplomacyProposal").value.trim() !== operation.proposal);
        if (String(officeStage()?.id || "") !== String(record?.id || "") || $("#officeMemberSelect").value !== assigneeId || (!operation && $("#officeTaskType").value !== taskType) || currentOfficeCouncil()?.id !== council.id || operationChanged) {
          throw new Error("授命条件已变化，请重新确认军议与差事");
        }
        return await completeIssuedOfficeTask(mandateInput, issuedMandate);
      }
      const created = organization.createTask(taskBaseState, {
        type: taskType,
        assigneeId,
        stageId: record?.id,
        stageTitle: record?.battleTitle,
        knowledgeId: knowledge?.id,
        councilId: council?.id,
        mandateId: issuedMandate?.id,
        operation
      });
      const remote = integration.isOffline() ? { state: "OFFLINE" } : await integration.createOrganizationTask({
        task_type: created.task.type,
        assignee_hero_id: created.task.assigneeId,
        stage_id: String(record?.id || "unknown"),
        // Keep the external protocol body neutral and stable. Narrative combat text and AINPC
        // output remain frozen in the signed save/task council snapshot for browser provenance.
        stage_title: `Dongzhou stage ${record?.id || "unknown"}`,
        brief: `Dongzhou office assignment for stage ${record?.id || "unknown"}${created.task.mandate ? `; Nexus mandate ${created.task.mandate.id}` : ""}${created.task.mandate?.correspondence ? `; AINPC correspondence ${created.task.mandate.correspondence.messageId}` : ""}.`,
        parameters: {
          resource_units: created.task.cost,
          assignee_name: created.task.assigneeName,
          mandate_id: created.task.mandate?.id,
          mandate_digest: created.task.mandate?.digest
        }
      }, created.task);
      if (!integration.isOffline()) {
        profile.organization = organization.recordMandate(profile.organization, issuedMandate).state;
        integration.applyOrganizationOrder(profile, created.task, remote);
        localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
        renderOrganizationPanel();
        await integration.persist(profile);
        integration.acknowledgeCourtMandate(mandateInput);
      } else {
        profile.campaignResources.provisions = clamp(profile.campaignResources.provisions - taskDefinition.cost, 0, 200);
        saveOrganization(created.state);
      }
      showNotice(`${created.task.assigneeName}已领命：${created.task.name}`);
      refreshOfficeInventory().catch(() => {});
      return created.task;
    } catch (error) {
      showNotice(error.message);
      return null;
    } finally {
      officeOrderInFlight = false;
      const leaderSelected = !integration.isOffline() && profile.organization.backend.orgFlow && $("#officeMemberSelect").value === "DuBo";
      $("#officeIssueButton").disabled = leaderSelected;
    }
  }

  let officeAdvanceInFlight = false;

  function organizationTaskSnapshot(response) {
    const snapshot = response.result?.data || response.result || null;
    return snapshot && typeof snapshot === "object"
      ? { ...snapshot, assigneeHeroId: response.assigneeHeroId || null, settlement: response.settlement || null, closureReceipt: response.closureReceipt || null, npcOutcome: response.npcOutcome || null, review: response.review || null, followUps: Array.isArray(response.followUps) ? response.followUps : [] }
      : snapshot;
  }

  async function readOrganizationTaskSnapshots(tasks) {
    const responses = await Promise.all(tasks.map((task) => integration.organizationTask(task.remoteResult)));
    return responses.map(organizationTaskSnapshot);
  }

  let officeTaskRefreshSerial = 0;

  async function refreshOfficeTaskSnapshots() {
    const serial = ++officeTaskRefreshSerial;
    const tasks = profile.organization.tasks.filter((task) => task.status === "active" && task.remoteResult);
    if (!tasks.length || integration.isOffline() || !profile.organization.backend.orgFlow) return;
    const snapshots = await readOrganizationTaskSnapshots(tasks);
    if (serial !== officeTaskRefreshSerial) return;
    await commitOrganizationState(organization.reconcileRemoteTasks(profile.organization, snapshots, { advanceMonth: false }));
  }

  async function waitForOrganizationTasksToStart(tasks, initialSnapshots) {
    let snapshots = initialSnapshots;
    const deadline = Date.now() + 30000;
    while (snapshots.some((snapshot) => !organization.remoteTaskReadyForAdvance(snapshot))) {
      if (snapshots.some((snapshot) => snapshot?.review?.state === "REQUIRES_ACTION") || Date.now() >= deadline) break;
      await sleep(1500);
      snapshots = await readOrganizationTaskSnapshots(tasks);
    }
    return snapshots;
  }

  async function advanceOfficeMonth() {
    if (officeAdvanceInFlight) return;
    officeAdvanceInFlight = true;
    $("#officeAdvanceButton").disabled = true;
    try {
    if (!integration.isOffline()) {
      if (!profile.organization.backend.orgFlow) {
        showNotice("组织流服务当前不可用，月令未推进，请稍后重试。");
        return;
      }
      try {
        await ensureCurrentOfficeNpcSchedulesReady();
      } catch (error) {
        showNotice(error.message + "，月令未推进。");
        return;
      }
      const tasks = profile.organization.tasks.filter((task) => task.status === "active" && task.remoteResult);
      try {
        const initialSnapshots = await readOrganizationTaskSnapshots(tasks);
        const snapshots = await waitForOrganizationTasksToStart(tasks, initialSnapshots);
        const waiting = snapshots.some((snapshot) => !organization.remoteTaskReadyForAdvance(snapshot));
        if (waiting) {
          await commitOrganizationState(organization.reconcileRemoteTasks(profile.organization, snapshots, { advanceMonth: false }));
          showNotice(snapshots.some((snapshot) => snapshot?.review?.state === "REQUIRES_ACTION") ? "属官已经复命，请先裁可簿书。" : "差事仍在受理，待属官确认后方可推进月令。");
          return;
        }
        await commitOrganizationState(organization.reconcileRemoteTasks(profile.organization, snapshots));
        const latest = profile.organization.history.at(-1);
        showNotice(latest?.text || "月令已进，官署差事仍在办理");
      } catch (error) {
        showNotice(`官署簿书暂不可达：${error.message}`);
      }
      return;
    }
    saveOrganization(organization.advanceMonth(profile.organization));
    const latest = profile.organization.history.at(-1);
    showNotice(latest?.text || "月令已进");
    } finally {
      officeAdvanceInFlight = false;
      $("#officeAdvanceButton").disabled = false;
    }
  }

  let officeKnowledgeRequestSerial = 0;
  let officeKnowledgeView = [];
  let officeCodexRequestSerial = 0;
  let officeCodexView = [];
  let officeCodexSelectedId = "";

  function knowledgeRetrievalText(entry) {
    const labels = { graph: "图谱牵连", entity: "实体命中", bm25: "原文命中", vector: "文义相近", category: "同类史料", schedule_tag: "时序相合" };
    const channels = Array.isArray(entry?.retrieval?.channels) ? entry.retrieval.channels : [];
    return channels.map((item) => `${labels[item.channel] || item.channel} ${Math.round(Number(item.normalizedScore || 0) * 100)}%`).join(" · ") || "本回目录";
  }

  function safeKnowledgeUrl(value) {
    try {
      const url = new URL(String(value || ""), window.location.href);
      return ["http:", "https:"].includes(url.protocol) ? url.href : "";
    } catch (_) {
      return "";
    }
  }

  function codexPeople(entry) {
    const direct = Array.isArray(entry.people) ? entry.people : [];
    const entities = Array.isArray(entry.entities?.npcs) ? entry.entities.npcs.map((item) => item?.name) : [];
    return [...new Set([...direct, ...entities].map((item) => String(item || "").trim()).filter(Boolean))];
  }

  function codexSources(entry) {
    const details = Array.isArray(entry.sourceDetails) ? entry.sourceDetails.filter((item) => item && typeof item === "object") : [];
    const legacy = Array.isArray(entry.sources) ? entry.sources.filter((item) => item && typeof item === "object") : [];
    return details.length ? details : legacy;
  }

  function renderOfficeCodex() {
    const query = $("#officeCodexFilter").value.trim().toLocaleLowerCase();
    const selectedStage = $("#officeCodexStage").value;
    const stages = [...new Set(officeCodexView.map((entry) => String(entry.stageId || "")).filter(Boolean))]
      .sort((left, right) => (findStageRecord(left)?.index || 9999) - (findStageRecord(right)?.index || 9999));
    const stageSelect = $("#officeCodexStage");
    stageSelect.innerHTML = `<option value="all">全部已发现</option>${stages.map((stageId) => `<option value="${escapeHtml(stageId)}">${escapeHtml(findStageRecord(stageId)?.battleTitle || `第 ${stageId} 战`)}</option>`).join("")}`;
    stageSelect.value = stages.includes(selectedStage) ? selectedStage : "all";
    const filtered = officeCodexView.filter((entry) => {
      if (stageSelect.value !== "all" && String(entry.stageId || "") !== stageSelect.value) return false;
      const people = codexPeople(entry);
      const sources = codexSources(entry);
      const keywords = Array.isArray(entry.keywords) ? entry.keywords : [];
      const haystack = [entry.name, entry.title, entry.summary, entry.objective, ...keywords, ...people, ...sources.flatMap((source) => [source.work, source.tier, source.scope])].join(" ").toLocaleLowerCase();
      return !query || haystack.includes(query);
    });
    if (!filtered.some((entry) => String(entry.id || entry.aku_id) === officeCodexSelectedId)) {
      officeCodexSelectedId = String(filtered[0]?.id || filtered[0]?.aku_id || "");
    }
    $("#officeCodexSummary").textContent = `已得 ${officeCodexView.length} 卷 · 当前 ${filtered.length} 卷`;
    $("#officeCodexList").innerHTML = filtered.map((entry) => {
      const id = String(entry.id || entry.aku_id || "");
      const active = id === officeCodexSelectedId;
      const stage = findStageRecord(String(entry.stageId || ""));
      return `<button type="button" role="option" aria-selected="${active}" class="${active ? "selected" : ""}" data-codex-id="${escapeHtml(id)}"><span>${escapeHtml(stage?.battleTitle || `第 ${entry.stageId || "?"} 战`)}</span><strong>${escapeHtml(entry.name || entry.title || "未名简册")}</strong><small>${escapeHtml(entry.summary || entry.objective || "尚无摘要")}</small></button>`;
    }).join("") || "<p>没有符合筛选条件的已得简册。</p>";
    const entry = filtered.find((item) => String(item.id || item.aku_id) === officeCodexSelectedId);
    if (!entry) {
      $("#officeCodexDetail").innerHTML = "<p>选择一卷简册查看人物与出处。</p>";
      return;
    }
    const people = codexPeople(entry);
    const sources = codexSources(entry);
    const sourceRows = sources.map((source) => {
      const href = safeKnowledgeUrl(source.url);
      const title = escapeHtml(source.work || "未名出处");
      return `<li><div><strong>${href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${title}</a>` : title}</strong><span>${escapeHtml(source.tier || "来源")}</span></div><p>${escapeHtml(source.scope || "未注明适用范围")}</p></li>`;
    }).join("");
    $("#officeCodexDetail").innerHTML = `<header><span>${escapeHtml(findStageRecord(String(entry.stageId || ""))?.battleTitle || `第 ${entry.stageId || "?"} 战`)}</span><h4>${escapeHtml(entry.name || entry.title || "未名简册")}</h4></header><p>${escapeHtml(entry.summary || entry.objective || "尚无摘要")}</p><div class="office-codex-trace">${escapeHtml(knowledgeRetrievalText(entry))}</div>${people.length ? `<div class="office-codex-people"><span>相关人物</span><p>${people.map(escapeHtml).join(" · ")}</p></div>` : ""}<div class="office-codex-sources"><span>刊定出处</span><ol>${sourceRows || "<li><p>此卷尚未刊定外部出处。</p></li>"}</ol></div>`;
  }

  async function refreshOfficeCodex() {
    const serial = ++officeCodexRequestSerial;
    const refresh = $("#officeCodexRefresh");
    refresh.disabled = true;
    $("#officeCodexSummary").textContent = "史官正在清点已得简册……";
    try {
      const payload = await integration.knowledgeCodex();
      if (serial !== officeCodexRequestSerial) return;
      const raw = Array.isArray(payload.results) ? payload.results : [];
      officeCodexView = raw.map((item) => item?.aku || item?.data || item).filter((item) => item?.id || item?.aku_id);
      renderOfficeCodex();
    } catch (error) {
      if (serial === officeCodexRequestSerial) $("#officeCodexSummary").textContent = `史库暂不可达：${error.message}`;
    } finally {
      if (serial === officeCodexRequestSerial) refresh.disabled = false;
    }
  }

  function setOfficeCodex(open) {
    const expanded = Boolean(open);
    $("#officeCodexPanel").hidden = !expanded;
    $("#officeCodexToggle").setAttribute("aria-expanded", String(expanded));
    if (expanded) refreshOfficeCodex();
    else officeCodexRequestSerial += 1;
  }

  function renderOfficeKnowledgeResults() {
    const panel = $("#officeKnowledgeResults");
    const stageId = String(officeStage()?.id || "");
    const selected = profile.organization.selectedSources?.[stageId];
    panel.innerHTML = officeKnowledgeView.slice(0, 6).map((entry) => {
      const sources = Array.isArray(entry.sourceDetails) ? entry.sourceDetails : [];
      const sourceButtons = sources.map((source, index) => {
        const active = selected?.knowledgeId === String(entry.id) && Number(selected.index) === index;
        const eligible = String(entry.stageId || "") === stageId;
        return `<button type="button" class="office-source-choice${active ? " selected" : ""}" data-knowledge-id="${escapeHtml(String(entry.id))}" data-source-index="${index}" ${eligible ? "" : "disabled"}><strong>${escapeHtml(String(source.work || "未名出处"))}</strong><span>${escapeHtml(String(source.tier || "来源"))}</span><small>${escapeHtml(String(source.scope || "未注明适用范围"))}</small><b>${active ? "已取为据" : eligible ? "取此为据" : "非本回史料"}</b></button>`;
      }).join("");
      return `<article class="${selected?.knowledgeId === String(entry.id) ? "selected" : ""}"><strong>${escapeHtml(entry.name || entry.title || "史官条目")}</strong><div class="office-retrieval-trace">${escapeHtml(knowledgeRetrievalText(entry))}</div><p>${escapeHtml(entry.summary || entry.content || "")}</p><div class="office-source-choices">${sourceButtons || "<small>此条尚未发布可选出处。</small>"}</div></article>`;
    }).join("") || "<p>简册中未查到相关记载。</p>";
  }

  function selectOfficeEvidence(event) {
    const button = event.target.closest("[data-knowledge-id][data-source-index]");
    if (!button || button.disabled) return;
    try {
      const selected = organization.selectEvidence(profile.organization, {
        stageId: String(officeStage()?.id || ""), knowledgeId: button.dataset.knowledgeId,
        sourceIndex: Number(button.dataset.sourceIndex)
      });
      saveOrganization(selected.state);
      renderOfficeKnowledgeResults();
      showNotice(`已取${selected.source.work}为本回军议依据`);
    } catch (error) {
      showNotice(error.message);
    }
  }

  function showOfficeKnowledge(payload, context) {
    if (context && (context.serial !== officeKnowledgeRequestSerial || String(officeStage()?.id || "") !== context.stageId || (context.query != null && $("#officeKnowledgeQuery").value.trim() !== context.query))) return false;
    const raw = Array.isArray(payload.results) ? payload.results : Object.values(payload.results || {}).flat().filter((item) => item && typeof item === "object");
    const results = raw.map((item) => item.aku || item.data || item).filter((item) => item?.id);
    for (const entry of results) profile.organization = organization.recordKnowledge(profile.organization, entry);
    writeJson(PROFILE_KEY, profile);
    renderOfficeCouncil();
    officeKnowledgeView = results;
    renderOfficeKnowledgeResults();
    if (!$("#officeCodexPanel").hidden) refreshOfficeCodex();
    return true;
  }

  async function loadOfficeStageKnowledge() {
    const stageId = officeStage()?.id;
    if (!stageId) return;
    const context = { serial: ++officeKnowledgeRequestSerial, stageId: String(stageId) };
    const button = $("#officeStageKnowledgeButton");
    button.disabled = true;
    $("#officeKnowledgeResults").textContent = "史官正在取阅本回简册……";
    try {
      showOfficeKnowledge(await integration.stageKnowledge(String(stageId)), context);
    } catch (_) {
      $("#officeKnowledgeResults").textContent = "本回史料暂不可达，请稍后再查。";
    } finally {
      button.disabled = false;
    }
  }

  async function searchOfficeKnowledge(event) {
    event.preventDefault();
    const query = $("#officeKnowledgeQuery").value.trim();
    if (!query) return;
    const context = { serial: ++officeKnowledgeRequestSerial, stageId: String(officeStage()?.id || ""), query };
    $("#officeKnowledgeResults").innerHTML = "<p>史官正在检索简册……</p>";
    try {
      const payload = await integration.searchKnowledge(query, 6, officeStage()?.id);
      showOfficeKnowledge(payload, context);
    } catch (_) {
      $("#officeKnowledgeResults").innerHTML = "<p>史官简册暂不可达，请稍后再查。</p>";
    }
  }

  function freshState(record) {
    const assist = systems.retryAssist(profile, record.id);
    const contract = systems.missionContract(difficultyProfileFor(record).objectiveType);
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
      assist,
      assistMedicineRemaining: 0,
      mission: { contract, phaseIndex: 0, progress: 0, milestones: [] },
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
    updateMissionDisplay();
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
    return systems.effectiveTurnLimit(stageRecord?.turnLimit || 1, battleDifficulty(), state?.assist?.active);
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
    const battleProfile = state.assist?.active
      ? { ...profile, campaignResources: { ...profile.campaignResources, morale: Math.min(100, profile.campaignResources.morale + state.assist.morale) } }
      : profile;
    const formation = team === "own" ? systems.formationModifiers(battleProfile, heroId, hero.class, stageRecord.id) : { hp: 1, power: 1, defense: 1, move: 0, maxMp: 0, wounded: false, vanguard: false };
    const officeSupport = state.organizationSupport || {};
    const supportDefense = team === "own" ? 1 + Number(officeSupport.defense || 0) : 1;
    const supportAttack = team === "own" ? 1 + Number(officeSupport.attack || 0) : Math.max(.75, 1 - Number(officeSupport.recon || 0) * .04);
    const maxHp = Math.round((Number(unitClass.hp?.[0] || 100) + Number(unitClass.hp?.[1] || 5) * Math.max(0, level - 1)) * difficultyModifiers.hp * formation.hp * supportDefense);
    const maxMp = Number(unitClass.mp?.[0] || 10) + Number(unitClass.mp?.[1] || 1) * Math.max(0, level - 1) + equipment.maxMp + formation.maxMp;
    const id = `${heroId}-${++unitSerial}`;
    state.units.push({
      id, heroId, name: displayName(heroId), team, level, classId: hero.class, model: hero.model || "infantry-1-red", x, y,
      hp: maxHp, maxHp, mp: maxMp, maxMp, move: Number(unitClass.move || 5) + equipment.move + formation.move,
      power: Math.round((15.5 + Number(hero.stat?.[1] || 70) * .34 + growth.power + equipment.power) * difficultyModifiers.power * formation.power * supportAttack),
      defense: Math.round((8 + Number(hero.stat?.[2] || 70) * .22 + growth.defense + equipment.defense) * difficultyModifiers.defense * formation.defense * supportDefense),
      attackRange: unitClass.attack_range || "Adjacent4", acted: false, moved: false,
      invulnerable: false, direction: null, effects: [], wounded: formation.wounded, vanguard: formation.vanguard, undersupplied: formation.undersupplied,
      skillRank: systems.heroSkillRank(level)
    });
    return id;
  }

  function resolveUnits(ref) {
    if (Number.isInteger(Number(ref)) && String(ref).trim() !== "") {
      const heroId = asList(stageRecord?.commanders)[Number(ref)];
      if (heroId) return state.units.filter((unit) => unit.heroId === heroId);
    }
    return state.units.filter((unit) => unit.id === ref || unit.heroId === ref);
  }

  function activeUnits(team = null) {
    return state.units.filter((unit) => unit.hp > 0 && (!team || unit.team === team));
  }

  function getUnit(id) {
    return state.units.find((unit) => unit.id === id) || null;
  }

  function playUnitAnimation(unit, type, duration = 240, payload = {}) {
    if (!unit || window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return Promise.resolve();
    const previous = unitAnimations.get(unit.id);
    if (previous) previous.resolve?.();
    const id = ++animationSerial;
    return new Promise((resolve) => {
      const animation = { id, type, start: performance.now(), duration, progress: 0, resolve, ...payload };
      unitAnimations.set(unit.id, animation);
      const tick = (now) => {
        const current = unitAnimations.get(unit.id);
        if (!current || current.id !== id) { resolve(); return; }
        current.progress = clamp((now - current.start) / Math.max(1, current.duration), 0, 1);
        requestRender();
        if (current.progress < 1) requestAnimationFrame(tick);
        else {
          unitAnimations.delete(unit.id);
          requestRender();
          resolve();
        }
      };
      requestAnimationFrame(tick);
    });
  }

  function moveUnitAnimated(unit, x, y, duration = 260) {
    const fromX = unit.x; const fromY = unit.y;
    unit.x = x; unit.y = y;
    if (fromX === x && fromY === y) return Promise.resolve();
    return playUnitAnimation(unit, "move", duration, { fromX, fromY, toX: x, toY: y });
  }

  function attackAnimation(unit, target, type = "attack") {
    return playUnitAnimation(unit, type, type === "skill" ? 320 : 220, { targetX: target?.x ?? unit.x, targetY: target?.y ?? unit.y });
  }

  function reactionAnimation(unit, defeated = false, healed = false) {
    return playUnitAnimation(unit, defeated ? "defeat" : healed ? "heal" : "hit", defeated ? 360 : 240);
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
      const spokenText = String(text);
      const runtimeSpeaker = resolveUnits(ref)[0]?.name || "军报";
      const voice = systems.resolveStoryVoice(voiceManifest, runtimeSpeaker, spokenText, {
        stageId: stageRecord?.id || "",
        section: "runtime"
      });
      const speaker = voice?.speaker || runtimeSpeaker;
      log(`${speaker}：${spokenText}`, "event");
      queueSpeech({ speaker, text: spokenText, stageId: stageRecord?.id || "", section: "runtime" });
    },
    push_cmd_move(ref, position) {
      if (restoring) return;
      const [x, y] = luaPoint(position);
      const unit = resolveUnits(ref).find((item) => item.hp > 0);
      if (unit && !unitAt(x, y, unit.id)) void moveUnitAnimated(unit, x, y, 300);
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
    openStory(entries, null, { stageId: stageRecord?.id || "", section: "events" });
  }

  function processStoryEvents() {
    if (!state || !stageRecord) return;
    state.triggeredStoryEvents ||= [];
    const context = { turn: state.turn, units: state.units, claimedSites: state.claimedSites };
    for (const [sourceIndex, event] of asList(stageRecord.story?.events).entries()) {
      const id = String(event?.id || "");
      if (!id || state.triggeredStoryEvents.includes(id)) continue;
      if (!systems.storyEventMatches(event, context)) continue;
      state.triggeredStoryEvents.push(id);
      queueSpeech({
        speaker: String(event.speaker || "军报"),
        text: String(event.text || ""),
        stageId: stageRecord.id,
        section: "events",
        eventId: id,
        sourceIndex
      });
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
      await performAttack(selected, clicked, true);
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
      await moveUnitAnimated(selected, x, y);
      selected.moved = true;
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
    await attackAnimation(actor, target, "skill");
    const result = systems.applySkill(actor, target, skill);
    if (!result.ok) { showNotice(result.reason === "insufficient-mp" ? "谋略不足" : "战技无法施放"); return; }
    await reactionAnimation(target, Boolean(result.defeated), result.kind === "heal" || result.kind === "buff");
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

  async function performAttack(attacker, defender, allowCounter) {
    const duel = asList(stageRecord.duels).find((entry) => entry.attacker === attacker.heroId && entry.defender === defender.heroId);
    const duelKey = duel ? `${duel.attacker}:${duel.defender}` : null;
    if (duel && !state.triggeredDuels.includes(duelKey)) {
      state.triggeredDuels.push(duelKey);
      await attackAnimation(attacker, defender);
      defender.hp = 0;
      await reactionAnimation(defender, true);
      state.stats.defeated++;
      recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage: defender.maxHp, duel: true });
      log(duel.text || `${attacker.name}阵前击退${defender.name}。`, "event");
      queueSpeech({ speaker: attacker.name, text: duel.attacker_speech || "今日便在阵前分个胜负！" });
      if (duel.result_speech) queueSpeech({ speaker: "军报", text: duel.result_speech });
      return;
    }
    if (defender.invulnerable) {
      await attackAnimation(attacker, defender);
      await reactionAnimation(defender);
      log(`${defender.name}尚有剧情护卫，本次攻击未能破阵。`, "event");
      recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage: 0, invulnerable: true });
      return;
    }
    const terrainGuard = terrainDefense(defender);
    const terrainAttack = terrainAttackBonus(attacker);
    await attackAnimation(attacker, defender);
    const damage = Math.max(8, systems.effectivePower(attacker) + terrainAttack - Math.round(systems.effectiveDefense(defender) * .42) - terrainGuard + randomInt(-4, 5));
    defender.hp = Math.max(0, defender.hp - damage);
    await reactionAnimation(defender, defender.hp <= 0);
    recordEvent("combat", { actor: attacker.heroId, target: defender.heroId, damage, defenderHp: defender.hp });
    log(`${attacker.name}攻击${defender.name}，造成 ${damage} 点伤害。`, attacker.team === "enemy" ? "bad" : "good");
    if (defender.hp <= 0) {
      log(`${defender.name}退出战场。`, defender.team === "enemy" ? "good" : "bad");
      if (defender.team === "enemy") state.stats.defeated++;
      return;
    }
    if (allowCounter && canAttack(defender, attacker) && !attacker.invulnerable) {
      await attackAnimation(defender, attacker);
      const counter = Math.max(6, Math.round(systems.effectivePower(defender) * .58 - systems.effectiveDefense(attacker) * .25 + randomInt(-3, 3)));
      attacker.hp = Math.max(0, attacker.hp - counter);
      await reactionAnimation(attacker, attacker.hp <= 0);
      log(`${defender.name}反击，${attacker.name}损失 ${counter} 点兵力。`, attacker.team === "own" ? "bad" : "good");
    }
  }

  function terrainDefense(unit) {
    const char = terrainRows()[unit.y]?.[unit.x];
    return ["F", "m", "r", "W", "C", "G"].includes(char) ? 5 : ["e", "c", "b"].includes(char) ? 3 : 0;
  }

  function terrainAttackBonus(unit) {
    const char = terrainRows()[unit.y]?.[unit.x];
    if (unit.classId === "Archer" && ["m", "G", "W"].includes(char)) return 4;
    if (unit.classId === "Cavalry" && ["r", "~"].includes(char)) return -5;
    return 0;
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
    if (Number(state.assistMedicineRemaining || 0) > 0) state.assistMedicineRemaining--;
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
        await moveUnitAnimated(actor, action.x, action.y, 220);
        const target = action.targetId ? getUnit(action.targetId) : null;
        if (target && canAttack(actor, target)) await performAttack(actor, target, true);
      } else {
        let target = targets[0];
        if (!canAttack(actor, target)) {
          const options = [...calculateReachable(actor).values()];
          options.sort((a, b) => manhattan(a, target) - manhattan(b, target) || a.cost - b.cost);
          const destination = options[0];
          if (destination) await moveUnitAnimated(actor, destination.x, destination.y, 220);
        }
        target = targets.filter((unit) => canAttack(actor, unit)).sort((a, b) => a.hp - b.hp)[0];
        if (target) await performAttack(actor, target, true);
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
      ownDefeatedHeroes: ownUnits.filter((unit) => unit.hp <= 0).map((unit) => unit.heroId),
      supplies: state.stats.supplies,
      inventoryRemaining: { ...state.inventory, medicine: Math.max(0, Number(state.inventory.medicine || 0) - Number(state.assistMedicineRemaining || 0)) },
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
      objectiveType: state.mission?.contract?.id || state.procedural?.objectiveType || "scripted",
      assistActive: Boolean(state.assist?.active),
      difficultyAssessment: state.difficultyAssessment,
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
    profile.organization = organization.advanceMonth(profile.organization, { resolveLocalTasks: integration.isOffline() });
    const officeReport = organization.recordBattleOutcome(profile.organization, {
      id: "battle:" + stageRecord.id + ":" + String(state.startedAt || Date.now()),
      stageId: String(stageRecord.id), stageTitle: stageRecord.battleTitle, won, turns: state.turn,
      ownLosses: ownUnits.filter((unit) => unit.hp <= 0).length, terminalReason,
      support: state.organizationSupport || {}
    });
    profile.organization = officeReport.state;
    profile.organization.history.push({ month: profile.organization.month, tone: won ? "good" : "bad", text: `${stageRecord.battleTitle}${won ? "告捷" : "失利"}，战后回报已收入官署档案。` });
    state.result.progression = { firstClear: progression.firstClear, rankUps: progression.rankUps, reward: progression.reward, coinsEarned: progression.coinsEarned, masteryUpdates: progression.masteryUpdates };
    state.result.officeReportId = officeReport.report.id;
    writeJson(PROFILE_KEY, profile);
    if (progression.rankUps) log(`军阶提升至 ${profile.armyRank}，全军基础战力提高。`, "event");
    if (progression.coinsEarned) log(`首通获得 ${progression.coinsEarned} 铜钱与军需补给。`, "event");
    log(`军势结算：军粮 ${profile.campaignResources.provisions}，士气 ${profile.campaignResources.morale}，伤兵 ${Object.keys(profile.woundedHeroes).length}。`, "event");
    for (const update of progression.masteryUpdates.filter((entry) => entry.xpEarned > 0)) {
      log(`${displayName(update.heroId)} 熟练度 +${update.xpEarned}${update.leveled ? `，升至 ${update.level} 级` : ""}`, "event");
    }
    feedback(won ? "victory" : "defeat");
    saveBattle(false);
    const ending = asList(won ? stageRecord.story?.victory : stageRecord.story?.defeat);
    if (ending.length) openStory(ending, showResult, { stageId: stageRecord.id, section: won ? "victory" : "defeat" });
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
      ["评估", `${Math.round(reward * 100)}`], ["难度", { easy: "简单", medium: "标准", hard: "艰难" }[battleDifficulty()] || "标准"],
      ["军粮", `${profile.campaignResources.provisions}`], ["士气", `${profile.campaignResources.morale}`], ["伤兵", `${Object.keys(profile.woundedHeroes).length}`],
      ["官署", state.result.officeReportId ? "战报存档" : "待归档"]
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

  function openStory(entries, onDone = null, storyContext = {}) {
    storyEntries = systems.normalizeStoryEntries(asList(entries), 110, storyContext);
    if (!storyEntries.length) { onDone?.(); return; }
    storyIndex = 0;
    storyDone = onDone;
    storyMusicContext = { ...storyContext };
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
    playContextMusic({
      stageId: entry.stageId || storyMusicContext.stageId || stageRecord?.id || "",
      section: entry.section || storyMusicContext.section || "intro",
      eventId: entry.eventId || storyMusicContext.eventId || "",
      text: entry.text || ""
    });
    playStoryVoice(entry);
  }

  function musicVolume() {
    const base = clamp(Number(profile.settings.musicVolume ?? 0.42), 0, 1);
    return musicDucked ? base * 0.28 : base;
  }

  function applyMusicVolume() {
    if (musicAudio) musicAudio.volume = musicVolume();
  }

  function setMusicDucked(ducked) {
    musicDucked = Boolean(ducked);
    applyMusicVolume();
  }

  function stopContextMusic(fadeMs = 250) {
    musicSerial += 1;
    musicCueId = "";
    const audio = musicAudio;
    musicAudio = null;
    if (!audio) return;
    const start = audio.volume;
    const started = performance.now();
    const fade = (now) => {
      const progress = clamp((now - started) / Math.max(1, fadeMs), 0, 1);
      audio.volume = start * (1 - progress);
      if (progress < 1) requestAnimationFrame(fade);
      else { audio.pause(); audio.removeAttribute("src"); audio.load(); }
    };
    requestAnimationFrame(fade);
  }

  function playContextMusic(context = {}) {
    const cue = systems.resolveContextMusic(musicManifest, context);
    if (!cue || !profile.settings.musicEnabled) {
      if (!profile.settings.musicEnabled) stopContextMusic();
      return;
    }
    if (musicCueId === cue.id && musicAudio) { applyMusicVolume(); return; }
    const previous = musicAudio;
    const serial = ++musicSerial;
    musicCueId = cue.id;
    const startSource = (file, sha256, isFallback = false) => {
      const cacheVersion = String(sha256 || "").slice(0, 16);
      const source = cacheVersion ? `${file}?v=${cacheVersion}` : file;
      const audio = new Audio(source);
      musicAudio = audio;
      audio.preload = "auto";
      audio.loop = Boolean(cue.loop);
      audio.volume = 0;
      let failureHandled = false;
      const failed = () => {
        if (failureHandled) return;
        failureHandled = true;
        audio.pause();
        audio.removeAttribute("src");
        audio.load();
        const fallbackFile = String(cue.fallbackFile || "");
        if (!isFallback && fallbackFile && fallbackFile !== cue.file && serial === musicSerial) {
          startSource(fallbackFile, cue.fallbackSha256, true);
          return;
        }
        if (serial === musicSerial) { musicAudio = null; musicCueId = ""; }
      };
      audio.addEventListener("error", failed, { once: true });
      audio.play().then(() => {
        const started = performance.now();
        const duration = 900;
        const previousStart = previous?.volume || 0;
        const fade = (now) => {
          if (serial !== musicSerial) return;
          const progress = clamp((now - started) / duration, 0, 1);
          audio.volume = musicVolume() * progress;
          if (previous) previous.volume = previousStart * (1 - progress);
          if (progress < 1) requestAnimationFrame(fade);
          else if (previous) { previous.pause(); previous.removeAttribute("src"); previous.load(); }
        };
        requestAnimationFrame(fade);
      }).catch(failed);
    };
    startSource(cue.file, cue.sha256);
  }

  function stopStoryVoice() {
    storyAudioSerial += 1;
    if (storyAudio) {
      storyAudio.pause();
      storyAudio.removeAttribute("src");
      storyAudio.load();
      storyAudio = null;
    }
    setMusicDucked(false);
    $("#storyVoiceReplayButton")?.classList.remove("is-playing");
  }

  function playStoryVoice(entry) {
    stopStoryVoice();
    const voice = systems.resolveStoryVoice(voiceManifest, entry?.speaker, entry?.text, entry);
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
    setMusicDucked(true);
    button.classList.add("is-playing");
    const finish = () => {
      if (serial !== storyAudioSerial) return;
      button.classList.remove("is-playing");
      storyAudio = null;
      setMusicDucked(false);
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
    storyMusicContext = {};
    if (state && !state.result && stageRecord) playContextMusic({ stageId: stageRecord.id, kind: "battle", section: "battle" });
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

  function missionProgress() {
    if (!state?.mission) return 0;
    if (state.result?.won) return 1;
    const id = state.mission.contract?.id;
    if (id === "capture") {
      const total = Math.max(1, asList(stageRecord?.sites).length);
      return clamp((state.claimedSites?.length || 0) / total, 0, 1);
    }
    if (["defend", "escort", "escape"].includes(id)) {
      const turnProgress = clamp((Number(state.turn || 1) - 1) / Math.max(1, battleTurnLimit() - 1), 0, .95);
      if (id !== "escort") return turnProgress;
      const allyRatio = activeUnits("ally").length / Math.max(1, state.initialAllyCount || activeUnits("ally").length || 1);
      return clamp(turnProgress * (.7 + .3 * allyRatio), 0, .95);
    }
    if (id === "narrative") return clamp((Number(state.turn || 1) - 1) / Math.max(1, battleTurnLimit() - 1), 0, .95);
    const initial = Math.max(1, Number(state.initialEnemyCount || activeUnits("enemy").length || 1));
    return clamp((initial - activeUnits("enemy").length) / initial, 0, 1);
  }

  function updateMissionDisplay(trackMilestone = false) {
    if (!state?.mission || !stageRecord) return;
    const progress = missionProgress();
    const phases = state.mission.contract?.phases || ["接战", "推进", "决胜"];
    const phaseIndex = state.result?.won ? phases.length - 1 : Math.min(phases.length - 1, Math.floor(progress * phases.length));
    if (trackMilestone && phaseIndex > Number(state.mission.phaseIndex || 0)) {
      for (let index = Number(state.mission.phaseIndex || 0) + 1; index <= phaseIndex; index++) {
        const phase = phases[index];
        if (!state.mission.milestones.includes(phase)) {
          state.mission.milestones.push(phase);
          log(`战局阶段推进：${phase}。`, "event");
          recordEvent("mission_phase", { phase, progress: Math.round(progress * 100) });
        }
      }
    }
    state.mission.phaseIndex = phaseIndex;
    state.mission.progress = progress;
    $("#objectiveText").textContent = `${stageRecord.objective}\n${state.mission.contract.name} · ${phases[phaseIndex]} · ${Math.round(progress * 100)}%`;
  }

  function updateUI() {
    if (!state || !stageRecord) return;
    updateMissionDisplay(true);
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
        <img src="assets/${unitImageFor(unit)}" alt=""><span><span class="roster-name"><span>${escapeHtml(unit.name)}${unit.vanguard ? " · 先锋" : ""}</span><small>${unit.hp <= 0 ? "阵亡" : unit.wounded ? "负伤出阵" : unit.undersupplied ? "缺粮" : unit.acted ? "已行动" : CLASS_LABELS[unit.classId] || unit.classId}</small></span>
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
    const skill = systems.skillForUnit(unit);
    container.innerHTML = `<div class="detail-head"><img src="assets/${portrait}" alt=""><div><h3>${escapeHtml(unit.name)}</h3><p>${TEAM_LABELS[unit.team]} · ${CLASS_LABELS[unit.classId] || unit.classId}${unit.vanguard ? " · 先锋" : ""}${unit.wounded ? " · 负伤" : ""}</p></div></div>
      <div class="detail-grid"><div><span>兵力</span><strong>${Math.max(0, unit.hp)} / ${unit.maxHp}</strong></div><div><span>谋略</span><strong>${unit.mp} / ${unit.maxMp}</strong></div><div><span>移动</span><strong>${unit.move}</strong></div><div><span>攻击</span><strong>${systems.effectivePower(unit)}</strong></div><div><span>防御</span><strong>${systems.effectiveDefense(unit)}</strong></div><div><span>等级</span><strong>${unit.level}</strong></div><div><span>战技</span><strong>${skill ? `${skill.name} · ${unit.skillRank || 1}阶` : "无"}</strong></div><div><span>阵型</span><strong>${unit.team === "own" ? systems.FORMATION_PRESETS[profile.formation].name : "敌阵"}</strong></div></div>`;
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
    if (stageRecord) playContextMusic({ stageId: stageRecord.id, kind: "battle", section: "battle" });
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
    for (const unit of state.units.filter((item) => item.hp > 0 || unitAnimations.has(item.id))) drawUnit(unit, cellW, cellH);
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
    const animation = unitAnimations.get(unit.id);
    const progress = clamp(Number(animation?.progress || 0), 0, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    let renderX = unit.x; let renderY = unit.y; let alpha = 1;
    if (animation?.type === "move") {
      renderX = animation.fromX + (animation.toX - animation.fromX) * eased;
      renderY = animation.fromY + (animation.toY - animation.fromY) * eased;
    } else if (["attack", "skill"].includes(animation?.type)) {
      const dx = Number(animation.targetX || 0) - unit.x; const dy = Number(animation.targetY || 0) - unit.y;
      const distance = Math.max(1, Math.hypot(dx, dy)); const thrust = Math.sin(progress * Math.PI) * (animation.type === "skill" ? .18 : .3);
      renderX += dx / distance * thrust; renderY += dy / distance * thrust;
    } else if (animation?.type === "hit") {
      renderX += Math.sin(progress * Math.PI * 6) * (1 - progress) * .1;
    } else if (animation?.type === "heal") {
      renderY -= Math.sin(progress * Math.PI) * .1;
    } else if (animation?.type === "defeat") {
      renderY += eased * .16; alpha = 1 - eased;
    }
    const cx = (renderX + .5) * cellW; const cy = (renderY + .5) * cellH; const radius = Math.min(cellW, cellH) * .36;
    const colors = { own: ["#8f3028", "#e28b77"], ally: ["#8a6a24", "#e4c66d"], enemy: ["#2e577e", "#79a7d2"] }[unit.team];
    const haloAlpha = currentMapDetailProfile().unitHalo;
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.save(); ctx.fillStyle = `rgba(246,237,205,${haloAlpha})`; ctx.strokeStyle = "rgba(18,14,9,.72)"; ctx.lineWidth = Math.max(2, radius * .09);
    ctx.beginPath(); ctx.arc(cx, cy, radius * 1.17, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = radius * .22; ctx.fillStyle = colors[0];
    ctx.strokeStyle = selectedId === unit.id ? "#ffe291" : inspectionId === unit.id ? "#fff3cc" : colors[1]; ctx.lineWidth = selectedId === unit.id ? 5 : 3;
    ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); ctx.restore();
    const image = getImage(unitImageFor(unit));
    if (image.complete && image.naturalWidth) { const size = radius * 1.38; ctx.drawImage(image, cx - size / 2, cy - size / 2, size, size); }
    if (["skill", "heal"].includes(animation?.type)) {
      ctx.save(); ctx.strokeStyle = animation.type === "heal" ? `rgba(107,190,108,${1 - progress})` : `rgba(232,190,82,${1 - progress})`; ctx.lineWidth = Math.max(2, radius * .08);
      ctx.beginPath(); ctx.arc(cx, cy, radius * (1.05 + progress * .5), 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    }
    const ratio = Math.max(0, unit.hp / unit.maxHp); const barW = cellW * .74; const barH = Math.max(4, cellH * .07); const barX = cx - barW / 2; const barY = (renderY + .88) * cellH;
    ctx.fillStyle = "rgba(8,10,8,.9)"; ctx.fillRect(barX, barY, barW, barH); ctx.fillStyle = ratio > .5 ? "#6ca461" : ratio > .25 ? "#c19442" : "#b7483f"; ctx.fillRect(barX + 1, barY + 1, Math.max(0, (barW - 2) * ratio), barH - 2);
    if (cellW >= 42 || selectedId === unit.id || inspectionId === unit.id) {
      ctx.font = `700 ${Math.max(10, Math.floor(cellW * .18))}px "Microsoft YaHei", sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.lineWidth = 3; ctx.strokeStyle = "rgba(8,10,8,.85)";
      const label = unit.name.length > 6 ? unit.name.slice(0, 6) : unit.name; ctx.strokeText(label, cx, (renderY + .12) * cellH); ctx.fillStyle = "#fff8e6"; ctx.fillText(label, cx, (renderY + .12) * cellH);
    }
    if (unit.acted && unit.team === "own") { ctx.fillStyle = "rgba(8,10,8,.42)"; ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill(); }
    if (unit.invulnerable) { ctx.strokeStyle = "rgba(255,226,130,.9)"; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, radius * 1.12, 0, Math.PI * 2); ctx.stroke(); }
    ctx.restore();
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
    $("#npcInteractionToggle").checked = profile.settings.aiNpcInteractionEnabled;
    renderNpcInteractionPreference();
    $("#feedbackToggle").checked = profile.settings.feedbackEnabled;
    $("#musicToggle").checked = profile.settings.musicEnabled;
    $("#musicVolume").value = Math.round(profile.settings.musicVolume * 100);
    $("#voiceToggle").checked = profile.settings.voiceEnabled;
    $("#voiceVolume").value = Math.round(profile.settings.voiceVolume * 100);
  }

  function renderNpcInteractionPreference() {
    const status = $("#npcInteractionStatus");
    if (!status) return;
    const enabled = Boolean(profile.settings.aiNpcInteractionEnabled);
    const labels = {
      offline: "离线演算，不接收主动来信",
      pending: "等待属官服务确认",
      syncing: "正在同步属官服务",
      deferred: "属官服务待恢复，稍后重试",
      failed: `同步失败，仍保持${enabled ? "开启" : "关闭"}`,
      synced: enabled ? "主动来信已开启" : "主动来信已关闭",
    };
    status.dataset.state = npcInteractionPreferenceState;
    status.textContent = labels[npcInteractionPreferenceState] || labels.pending;
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

  function downloadJson(payload, filename) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function openReplay(index) {
    const replay = profile.replays?.[index];
    if (!replay) return;
    replaySelection = replay;
    const summary = replay.summary || {};
    const record = findStageRecord(replay.stage_id);
    $("#replayTitle").textContent = record?.battleTitle || replay.stage_id || "战局回放";
    const events = replay.events || [];
    $("#replayDetails").innerHTML = `<div class="replay-summary">
      <div><span>结果</span><strong>${summary.won ? "告捷" : "失利"}</strong></div>
      <div><span>回合</span><strong>${summary.turns || 0}</strong></div>
      <div><span>阵型</span><strong>${escapeHtml(systems.FORMATION_PRESETS[summary.formation]?.name || summary.formation || "中军持衡")}</strong></div>
      <div><span>事件</span><strong>${events.length}</strong></div>
    </div><ol class="replay-events">${events.length ? events.map((event) => `<li><span>第 ${Number(event.turn || 0)} 回合</span><b>${escapeHtml(event.type || "event")}</b><span>${escapeHtml(replayEventText(event))}</span></li>`).join("") : "<li><span>无逐步事件</span></li>"}</ol>`;
    $("#replayModal").hidden = false;
  }

  function replayEventText(event) {
    if (event.type === "move") return `${displayName(event.unit)} → (${Number(event.x || 0) + 1}, ${Number(event.y || 0) + 1})`;
    if (["attack", "combat", "skill"].includes(event.type)) return `${displayName(event.actor)} → ${displayName(event.target)}${event.damage ? ` · ${event.damage} 伤害` : ""}`;
    if (event.type === "mission_phase") return `${event.phase} · ${event.progress}%`;
    return Object.entries(event).filter(([key]) => !["type", "t_ms", "turn"].includes(key)).map(([key, value]) => `${key}: ${value}`).join(" · ") || "战局状态更新";
  }

  function exportSelectedReplay() {
    if (!replaySelection) return;
    const date = new Date().toISOString().slice(0, 10);
    downloadJson(replaySelection, `dongzhou-replay-${replaySelection.stage_id || "battle"}-${date}.json`);
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
    $("#focusRestartButton").addEventListener("click", (event) => {
      $("#confirmModal").dataset.stageId = event.currentTarget.dataset.stageId;
      $("#confirmModal").dataset.source = "campaign";
      $("#confirmModal").hidden = false;
    });
    $("#focusArchiveButton").addEventListener("click", () => $("#campaignArchive").scrollIntoView({ behavior: "smooth", block: "start" }));
    $("#focusRouteOptions").addEventListener("click", (event) => {
      const button = event.target.closest("[data-route-method]");
      const record = findStageRecord($("#focusStageButton").dataset.stageId);
      if (!button || !record) return;
      profile.routePreferences ||= {};
      profile.routePreferences[record.id] = button.dataset.routeMethod;
      writeJson(PROFILE_KEY, profile);
      renderCampaignRouteProof(record);
    });
    $("#campaignCampButton").addEventListener("click", () => setCampaignCamp(true));
    $("#campaignCampCloseButton").addEventListener("click", () => setCampaignCamp(false));
    $("#campaignCampBackdrop").addEventListener("click", (event) => {
      if (event.target === event.currentTarget) setCampaignCamp(false);
    });
    $("#campaignOfficeButton").addEventListener("click", () => setCampaignOffice(true));
    $("#campaignOfficeCloseButton").addEventListener("click", () => setCampaignOffice(false));
    $("#campaignOfficeBackdrop").addEventListener("click", (event) => { if (event.target === event.currentTarget) setCampaignOffice(false); });
    $("#officeTaskType").addEventListener("change", () => { $("#officeUseCouncil").checked = false; renderOrganizationPanel(); refreshOfficeNpcAssignment(); });
    $("#officeMemberSelect").addEventListener("change", () => { $("#officeUseCouncil").checked = false; officeMemoryView = []; officeSelectedMemory = null; renderOrganizationPanel(); refreshOfficeNpcState(); });
    $("#officeCorrespondenceRefresh").addEventListener("click", () => refreshOfficeCorrespondence());
    $("#officeInventoryRefresh").addEventListener("click", refreshOfficeInventory);
    $("#officeInventoryRequisition").addEventListener("click", requisitionOfficeInventory);
    $("#officeInventoryApprove").addEventListener("click", () => decideOfficeInventoryRequisition("APPROVE"));
    $("#officeInventoryReject").addEventListener("click", () => decideOfficeInventoryRequisition("REJECT"));
    $("#officeMembershipApply").addEventListener("click", () => requestOfficeMembership("join"));
    $("#officeMembershipLeave").addEventListener("click", () => requestOfficeMembership("leave"));
    $("#officeMembershipLeaveConfirm").addEventListener("click", () => requestOfficeMembership("confirmLeave"));
    $("#officeCareerOptions").addEventListener("click", () => requestOfficeCareer("options"));
    $("#officeCareerRequestForm").addEventListener("submit", submitOfficeCareerRequest);
    $("#officeCareerInbox").addEventListener("click", () => requestOfficeCareer("inbox"));
    $("#officeCareerAccept").addEventListener("click", () => requestOfficeCareer("accept"));
    $("#officeCareerResultForm").addEventListener("submit", submitOfficeCareerResult);
    $("#officeMessageForm").addEventListener("submit", sendOfficeNpcMessage);
    $("#officeCorrespondence").addEventListener("click", (event) => { const button = event.target.closest("[data-correspondence-id]"); if (button) selectOfficeCorrespondence(button.dataset.correspondenceId); });
    $("#officeNpcMemories").addEventListener("click", (event) => { const button = event.target.closest("[data-memory-id]"); if (button) selectOfficeMemory(button.dataset.memoryId); });
    $("#officeScheduleButton").addEventListener("click", generateOfficeNpcSchedule);
    $("#officeThoughtButton").addEventListener("click", requestOfficeNpcThought);
    $("#officeDecisionForm").addEventListener("submit", requestOfficeNpcDecision);
    $("#officeDiplomacyTarget").addEventListener("change", renderOfficeDiplomacyStatus);
    $("#officeLobbyButton").addEventListener("click", lobbyPolity);
    $("#officeAllianceButton").addEventListener("click", signAlliance);
    $("#officeBetrayButton").addEventListener("click", betrayAlliance);
    $("#officeIssueButton").addEventListener("click", () => issueOfficeTask());
    $("#officeMandateApproveButton").addEventListener("click", () => resolveOfficeMandate("APPROVE"));
    $("#officeMandateRejectButton").addEventListener("click", () => resolveOfficeMandate("REJECT"));
    $("#officeSettlementAcceptButton").addEventListener("click", () => resolveOfficeSettlement("ACCEPT"));
    $("#officeSettlementCensureButton").addEventListener("click", () => resolveOfficeSettlement("CENSURE"));
    $("#officeAdvanceButton").addEventListener("click", advanceOfficeMonth);
    $("#officeKnowledgeForm").addEventListener("submit", searchOfficeKnowledge);
    $("#officeStageKnowledgeButton").addEventListener("click", loadOfficeStageKnowledge);
    $("#officeQuizStart").addEventListener("click", startOfficeQuiz);
    $("#officeQuizOptions").addEventListener("click", (event) => {
      const button = event.target.closest("[data-quiz-answer]");
      if (button) answerOfficeQuiz(Number(button.dataset.quizAnswer));
    });
    $("#officeKnowledgeResults").addEventListener("click", selectOfficeEvidence);
    $("#officeCodexToggle").addEventListener("click", () => setOfficeCodex($("#officeCodexPanel").hidden));
    $("#officeCodexRefresh").addEventListener("click", refreshOfficeCodex);
    $("#officeCodexFilter").addEventListener("input", renderOfficeCodex);
    $("#officeCodexStage").addEventListener("change", renderOfficeCodex);
    $("#officeCodexList").addEventListener("click", (event) => {
      const button = event.target.closest("[data-codex-id]");
      if (!button) return;
      officeCodexSelectedId = button.dataset.codexId;
      renderOfficeCodex();
    });
    document.querySelectorAll("[data-era-range]").forEach((button) => button.addEventListener("click", () => {
      $("#stageSearch").value = "";
      $("#stageRange").value = button.dataset.eraRange;
      renderCampaign();
      $("#campaignArchive").scrollIntoView({ behavior: "smooth", block: "start" });
    }));
    $("#proceduralButton").addEventListener("click", startProceduralStage);
    $("#dailyChallengeButton").addEventListener("click", startDailyChallenge);
    document.querySelectorAll("[data-formation]").forEach((button) => button.addEventListener("click", () => {
      profile.formation = button.dataset.formation;
      writeJson(PROFILE_KEY, profile);
      renderCampaign();
      showNotice(`已采用${systems.FORMATION_PRESETS[profile.formation].name}`);
    }));
    $("#vanguardSelect").addEventListener("change", (event) => {
      const record = findStageRecord($("#focusStageButton").dataset.stageId);
      if (!record || !event.currentTarget.value) return;
      profile.stageVanguards[record.id] = event.currentTarget.value;
      writeJson(PROFILE_KEY, profile);
      renderCampaign();
      showNotice(`${displayName(event.currentTarget.value)}已任本关先锋`);
    });
    $("#assistToggle").addEventListener("change", (event) => {
      profile.settings.transparentAssist = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
      renderCampaign();
    });
    $("#restArmyButton").addEventListener("click", () => {
      const result = systems.restArmy(profile, campaign.stages);
      if (!result.ok) { showNotice("铜钱不足，无法休整"); return; }
      profile = result.profile;
      writeJson(PROFILE_KEY, profile);
      renderCampaign();
      showNotice("全军休整：军粮 +30、士气 +20，伤势恢复一阶段");
    });
    $("#closeReplayButton").addEventListener("click", () => { $("#replayModal").hidden = true; replaySelection = null; });
    $("#exportReplayButton").addEventListener("click", exportSelectedReplay);
    $("#proceduralMode").addEventListener("change", syncProceduralButton);
    $("#exerciseMenuButton").addEventListener("click", () => setExerciseMenu($("#exercisePanel").hidden));
    $("#campaignSettingsButton").addEventListener("click", () => setCampaignSettings($("#campaignSettingsBackdrop").hidden));
    $("#campaignSettingsCloseButton").addEventListener("click", () => setCampaignSettings(false));
    $("#campaignSettingsBackdrop").addEventListener("click", (event) => {
      if (event.target === event.currentTarget) setCampaignSettings(false);
    });
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".exercise-menu")) setExerciseMenu(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !$("#campaignSettingsBackdrop").hidden) {
        setCampaignSettings(false);
        $("#campaignSettingsButton").focus();
      } else if (event.key === "Escape" && !$("#campaignCampBackdrop").hidden) {
        setCampaignCamp(false);
        $("#campaignCampButton").focus();
      } else if (event.key === "Escape" && !$("#campaignOfficeBackdrop").hidden) {
        setCampaignOffice(false);
        $("#campaignOfficeButton").focus();
      }
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
    $("#npcInteractionToggle").addEventListener("change", async (event) => {
      const input = event.currentTarget;
      const requested = input.checked;
      input.disabled = true;
      npcInteractionPreferenceState = "syncing";
      renderNpcInteractionPreference();
      try {
        const result = await integration.setNpcInteractionPreference(requested);
        if (result.enabled !== requested) throw new Error("NPC interaction preference was not applied");
        profile.settings.aiNpcInteractionEnabled = requested;
        writeJson(PROFILE_KEY, profile);
        npcInteractionPreferenceState = "synced";
        showNotice(requested ? "已允许属官主动来信" : "已停止属官主动来信");
      } catch (error) {
        input.checked = profile.settings.aiNpcInteractionEnabled;
        npcInteractionPreferenceState = "failed";
        showNotice(error.message);
      } finally {
        input.disabled = false;
        renderNpcInteractionPreference();
      }
    });
    $("#feedbackToggle").addEventListener("change", (event) => {
      profile.settings.feedbackEnabled = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
    });
    $("#musicToggle").addEventListener("change", (event) => {
      profile.settings.musicEnabled = event.currentTarget.checked;
      writeJson(PROFILE_KEY, profile);
      if (!profile.settings.musicEnabled) stopContextMusic();
      else if (!$("#storyModal").hidden) renderStory();
      else if (state && stageRecord) playContextMusic({ stageId: stageRecord.id, kind: "battle", section: "battle" });
    });
    $("#musicVolume").addEventListener("input", (event) => {
      profile.settings.musicVolume = clamp(Number(event.currentTarget.value) / 100, 0, 1);
      applyMusicVolume();
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
      if (intro.length) openStory(intro, null, { stageId: stageRecord.id, section: "intro" });
    });
    $("#restartButton").addEventListener("click", () => {
      if (!state || !stageRecord) return;
      $("#confirmModal").dataset.stageId = stageRecord.id;
      $("#confirmModal").dataset.source = "battle";
      $("#confirmModal").hidden = false;
    });
    $("#cancelRestartButton").addEventListener("click", () => {
      $("#confirmModal").hidden = true;
      delete $("#confirmModal").dataset.stageId;
      delete $("#confirmModal").dataset.source;
    });
    $("#confirmRestartButton").addEventListener("click", () => {
      const modal = $("#confirmModal");
      const stageId = modal.dataset.stageId || stageRecord?.id;
      const options = modal.dataset.source === "battle" && state?.procedural ? { procedural: state.procedural } : {};
      if (!stageId) return;
      localStorage.removeItem(BATTLE_KEY);
      modal.hidden = true;
      delete modal.dataset.stageId;
      delete modal.dataset.source;
      startStage(stageId, null, options);
    });
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
      else if (!$("#replayModal").hidden) { $("#replayModal").hidden = true; replaySelection = null; }
      else if (!$("#storyModal").hidden) advanceStory(true);
      else if (selectedSkillId) { selectedSkillId = null; updateUI(); }
    });
  }

  boot();
})();
