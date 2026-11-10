(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouOrganizationPlay = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SCHEMA_VERSION = 10;
  const TASK_TYPES = {
    supply: { name: "转运军粮", office: "司徒", duration: 1, cost: 8, base: 72, reward: { provisions: 24 } },
    drill: { name: "整训军阵", office: "司马", duration: 1, cost: 6, base: 68, reward: { attack: 0.08 } },
    patrol: { name: "巡察营垒", office: "司寇", duration: 1, cost: 5, base: 74, reward: { defense: 0.1 } },
    intelligence: { name: "访求军情", office: "行人", duration: 2, cost: 7, base: 64, reward: { recon: 1 } },
    diplomacy: { name: "折冲诸侯", office: "上卿", duration: 2, cost: 9, base: 60, reward: { morale: 12 } }
  };

  const clamp = (value, min, max) => Math.max(min, Math.min(max, Number(value) || 0));
  const copy = (value) => JSON.parse(JSON.stringify(value));

  function hash(text) {
    let value = 2166136261;
    for (const char of String(text)) {
      value ^= char.codePointAt(0);
      value = Math.imul(value, 16777619);
    }
    return value >>> 0;
  }

  function defaultState() {
    return {
      schemaVersion: SCHEMA_VERSION,
      name: "列国军府",
      month: 1,
      taskSequence: 0,
      influence: 12,
      contribution: 0,
      backend: { mode: "local", nexusKernel: false, orgFlow: false, aiNpc: false, knowledge: false, checkedAt: null },
      members: [],
      tasks: [],
      knowledge: [],
      selectedSources: {},
      selectedCorrespondence: {},
      councils: [],
      mandates: [],
      relations: {},
      diplomacy: { lobbying: [], alliances: [], relations: {} },
      battleReports: [],
      relationEvents: [],
      archives: [],
      pendingSupport: [],
      settlements: [],
      settlementIds: [],
      history: []
    };
  }

  function normalizeMember(member, index) {
    return {
      id: String(member?.id || `officer-${index + 1}`),
      name: String(member?.name || `属官${index + 1}`),
      office: String(member?.office || ["司马", "司徒", "司寇", "行人"][index % 4]),
      loyalty: clamp(member?.loyalty ?? 68, 20, 100),
      fatigue: clamp(member?.fatigue ?? 0, 0, 100),
      merit: Math.trunc(clamp(member?.merit ?? 0, -999999, 999999))
    };
  }

  function normalizeState(raw) {
    const source = raw && typeof raw === "object" ? raw : {};
    const base = defaultState();
    const tasks = Array.isArray(source.tasks) ? source.tasks.filter((task) => task && typeof task === "object") : [];
    // 历史记录可以裁剪，尚未复命的差事和未投入战斗的筹备不能随之丢失。
    const recentClosed = new Set(tasks.filter((task) => task.status !== "active").slice(-40));
    const retainedTasks = tasks.filter((task) => task.status === "active" || recentClosed.has(task));
    const inheritedSequence = tasks.reduce((highest, task) => {
      const match = /^dz-\d+-(\d+)-/.exec(String(task.id || ""));
      return Math.max(highest, match ? Number(match[1]) : 0);
    }, 0);
    return {
      ...base,
      ...source,
      schemaVersion: SCHEMA_VERSION,
      month: Math.max(1, Math.floor(Number(source.month || 1))),
      taskSequence: Math.max(inheritedSequence, Number.isSafeInteger(source.taskSequence) && source.taskSequence >= 0 ? source.taskSequence : 0),
      influence: clamp(source.influence ?? 12, 0, 999),
      contribution: Math.trunc(clamp(source.contribution ?? 0, -999999, 999999)),
      backend: { ...base.backend, ...(source.backend || {}) },
      members: Array.isArray(source.members) ? source.members.slice(0, 12).map(normalizeMember) : [],
      tasks: retainedTasks.map((task) => ({ ...task, status: ['active', 'success', 'partial', 'failed', 'censured'].includes(task.status) ? task.status : 'failed' })),
      knowledge: Array.isArray(source.knowledge) ? source.knowledge.slice(-30).map((entry) => ({ ...entry })) : [],
      selectedSources: source.selectedSources && typeof source.selectedSources === "object" ? copy(source.selectedSources) : {},
      selectedCorrespondence: source.selectedCorrespondence && typeof source.selectedCorrespondence === "object" ? copy(source.selectedCorrespondence) : {},
      councils: Array.isArray(source.councils) ? source.councils.filter((entry) => entry && typeof entry === 'object').slice(-30).map(copy) : [],
      mandates: Array.isArray(source.mandates) ? source.mandates.filter((entry) => entry && typeof entry === "object").slice(-50).map(copy) : [],
      relations: source.relations && typeof source.relations === "object" ? { ...source.relations } : {},
      diplomacy: {
        lobbying: Array.isArray(source.diplomacy?.lobbying) ? source.diplomacy.lobbying.filter(Boolean).slice(-30).map(copy) : [],
        alliances: Array.isArray(source.diplomacy?.alliances) ? source.diplomacy.alliances.filter(Boolean).slice(-20).map(copy) : [],
        relations: source.diplomacy?.relations && typeof source.diplomacy.relations === "object" ? { ...source.diplomacy.relations } : {}
      },
      battleReports: Array.isArray(source.battleReports) ? source.battleReports.filter(Boolean).slice(-40).map(copy) : [],
      relationEvents: Array.isArray(source.relationEvents) ? source.relationEvents.filter(Boolean).slice(-80).map(copy) : [],
      archives: Array.isArray(source.archives) ? source.archives.filter(Boolean).slice(-80).map(copy) : [],
      pendingSupport: Array.isArray(source.pendingSupport) ? source.pendingSupport.filter((entry) => entry && typeof entry === "object").map((entry) => ({ ...entry })) : [],
      settlements: Array.isArray(source.settlements) ? source.settlements.filter((entry) => entry && typeof entry.settlementId === "string").slice(-100).map(copy) : [],
      settlementIds: [...new Set([
        ...(Array.isArray(source.settlementIds) ? source.settlementIds : []),
        ...(Array.isArray(source.settlements) ? source.settlements.map((entry) => entry?.settlementId) : [])
      ].filter((value) => typeof value === "string" && value))],
      history: Array.isArray(source.history) ? source.history.slice(-40).map((entry) => ({ ...entry })) : []
    };
  }

  function uniqueHeroIds(stage) {
    const deploy = stage?.stage?.deploy || {};
    const raw = [...(Array.isArray(deploy.unselectables) ? deploy.unselectables : []), ...(Array.isArray(deploy.selectables) ? deploy.selectables : Object.values(deploy.selectables || {}))];
    return [...new Set(raw.map((entry) => entry?.hero).filter(Boolean))];
  }

  function syncMembers(rawState, stage, nameForId) {
    const state = normalizeState(rawState);
    const known = new Map(state.members.map((member) => [member.id, member]));
    const offices = ["司马", "司徒", "司寇", "行人", "上卿"];
    for (const [index, id] of uniqueHeroIds(stage).entries()) {
      if (known.has(id)) continue;
      known.set(id, normalizeMember({ id, name: nameForId ? nameForId(id) : id, office: offices[index % offices.length] }, known.size));
    }
    state.members = [...known.values()].slice(0, 12);
    return state;
  }

  function recordCouncil(rawState, input) {
    const state = normalizeState(rawState);
    const stageId = String(input?.stageId || '');
    const member = state.members.find((entry) => entry.id === input?.memberId);
    const knowledge = state.knowledge.find((entry) => entry.id === input?.knowledgeId && entry.stageId === stageId);
    const evidenceSource = state.selectedSources[stageId];
    const correspondence = state.selectedCorrespondence[stageId];
    const options = input?.options;
    if (!stageId || !member || !knowledge) throw new Error('请先选定官员并查阅本回史料');
    if (!evidenceSource || evidenceSource.knowledgeId !== knowledge.id || Number(evidenceSource.index) !== Number(input.evidenceSourceIndex)) throw new Error('请先从本回史料中选定军议依据');
    if (!Array.isArray(options) || options.length < 2 || options.some((text) => typeof text !== 'string' || !text.trim())) throw new Error('军议方案不完整');
    if (!Number.isInteger(input.index) || input.index < 0 || input.index >= options.length) throw new Error('军议结果不属于本次方案');
    if (!String(input.question || '').trim() || !String(input.id || '').trim()) throw new Error('军议缺少来源记录');
    if (correspondence && (correspondence.heroId !== member.id || !/^[0-9a-f]{64}$/.test(String(correspondence.digest || "")))) throw new Error('所选耳报不属于当前属官');
    const council = { id: String(input.id), stageId, memberId: member.id, memberName: member.name,
      knowledgeId: knowledge.id, knowledgeName: String(input.knowledgeName || knowledge.name),
      knowledgeSummary: String(input.knowledgeSummary ?? knowledge.summary ?? ''), evidenceSource: copy(evidenceSource), question: String(input.question),
      correspondence: correspondence ? copy(correspondence) : null,
      options: options.slice(), index: input.index, text: options[input.index] };
    const previous = state.councils.find((entry) => entry.id === council.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(council)) throw new Error('军议来源记录冲突');
    if (!previous) state.councils = [...state.councils, council].slice(-30);
    return { state, council: copy(previous || council) };
  }

  function recordMandate(rawState, input) {
    const state = normalizeState(rawState);
    const mandate = input && typeof input === "object" ? copy(input) : null;
    if (!mandate?.id || !mandate.stageId || !mandate.heroId || !mandate.taskType) throw new Error("内核军令缺少关卡、属官或差事");
    if (!mandate.evidence?.id || !mandate.evidence?.source?.work || !mandate.council?.requestId || !mandate.council?.text) throw new Error("内核军令未绑定史料、选证与属官裁断");
    if (mandate.evidence.searchReceipt && (!/^[0-9a-f]{64}$/.test(String(mandate.evidence.searchReceipt.digest || "")) || !Array.isArray(mandate.evidence.retrieval?.channels) || !mandate.evidence.retrieval.channels.length)) throw new Error("内核军令检索回执无效");
    if (mandate.correspondence && (!/^[0-9a-f]{64}$/.test(String(mandate.correspondence.digest || "")) || mandate.correspondence.messageId !== mandate.council?.correspondence?.messageId || mandate.correspondence.digest !== mandate.council?.correspondence?.digest)) throw new Error("内核军令耳报来源无效");
    if (!mandate.assignment?.planId || !mandate.assignment?.eventId || mandate.assignment?.heroId !== mandate.heroId) throw new Error("内核军令未绑定属官当值日程");
    if (mandate.state !== "ISSUED" || !/^[0-9a-f]{64}$/.test(String(mandate.digest || "")) || !["READY", "DEGRADED"].includes(mandate.kernel?.state)) throw new Error("内核军令尚未签发或印记无效");
    if (mandate.operation && (mandate.taskType !== "diplomacy" || mandate.operation.kind !== "diplomacy" || !mandate.operation.target_id || !mandate.operation.target_name || !mandate.operation.proposal)) throw new Error("外交军令缺少目标或主张");
    const previous = state.mandates.find((entry) => entry.id === mandate.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(mandate)) throw new Error("内核军令来源记录冲突");
    if (!previous) {
      state.mandates = [...state.mandates, mandate].slice(-50);
      state.history.push({ month: state.month, tone: "order", text: `内核签发军令：${mandate.evidence.name} · ${mandate.council.text}` });
    }
    return { state, mandate: copy(previous || mandate) };
  }

  function createTask(rawState, input) {
    const state = normalizeState(rawState);
    const definition = TASK_TYPES[input?.type];
    if (!definition) throw new Error("未知差事");
    const member = state.members.find((entry) => entry.id === input?.assigneeId);
    if (!member) throw new Error("请选择承办官员");
    const council = input.councilId ? state.councils.find((entry) => entry.id === input.councilId) : null;
    if (input.councilId && (!council || council.memberId !== member.id || council.stageId !== String(input.stageId || '') || council.knowledgeId !== input.knowledgeId)) throw new Error('军议与本次关卡、官员或史料不匹配');
    const mandate = input.mandateId ? state.mandates.find((entry) => entry.id === input.mandateId) : null;
    const councilSource = council?.evidenceSource ? {
      index: council.evidenceSource.index, work: council.evidenceSource.work, tier: council.evidenceSource.tier,
      scope: council.evidenceSource.scope, url: council.evidenceSource.url
    } : null;
    if (input.mandateId && (!mandate || mandate.stageId !== String(input.stageId || "") || mandate.heroId !== member.id || mandate.taskType !== input.type || mandate.evidence?.id !== input.knowledgeId || mandate.council?.requestId !== input.councilId || JSON.stringify(mandate.evidence?.source || null) !== JSON.stringify(councilSource))) throw new Error("内核军令与本次关卡、属官、选证或差事不匹配");
    if (mandate?.evidence?.searchReceipt && JSON.stringify(mandate.evidence.searchReceipt) !== JSON.stringify(council?.evidenceSource?.searchReceipt || null)) throw new Error("内核军令与军议检索回执不匹配");
    if ((mandate?.correspondence?.messageId || null) !== (council?.correspondence?.messageId || null) || (mandate?.correspondence?.digest || null) !== (council?.correspondence?.digest || null)) throw new Error("内核军令与军议耳报不匹配");
    const operation = input.operation && typeof input.operation === "object" ? copy(input.operation) : mandate?.operation ? copy(mandate.operation) : null;
    if (operation && (input.type !== "diplomacy" || operation.kind !== "diplomacy" || !operation.target_id || !operation.target_name || !operation.proposal || !mandate?.operation || JSON.stringify(operation) !== JSON.stringify(mandate.operation))) throw new Error("外交差事与内核军令不匹配");
    const active = state.tasks.some((task) => task.status === "active" && task.assigneeId === member.id);
    if (active) throw new Error(`${member.name}已有差事在身`);
    // 序号独立于可裁剪的台账，旧存档从已有任务 ID 恢复，读档后不会重复领单。
    const serial = state.taskSequence + 1;
    if (!Number.isSafeInteger(serial)) throw new Error("差事编号已达上限");
    state.taskSequence = serial;
    const task = {
      id: `dz-${state.month}-${serial}-${hash(`${input.type}:${member.id}:${input.stageId || ""}`)}`,
      type: input.type,
      name: definition.name,
      assigneeId: member.id,
      assigneeName: member.name,
      office: member.office,
      stageId: String(input.stageId || ""),
      stageTitle: String(input.stageTitle || ""),
      knowledgeId: input.knowledgeId ? String(input.knowledgeId) : null,
      council: council ? copy(council) : null,
      mandate: mandate ? copy(mandate) : null,
      operation,
      startedMonth: state.month,
      dueMonth: state.month + definition.duration,
      status: "active",
      cost: definition.cost
    };
    state.tasks.push(task);
    member.fatigue = clamp(member.fatigue + 12, 0, 100);
    state.history.push({ month: state.month, tone: "order", text: `${member.name}领命：${definition.name}` });
    return { state, task };
  }

  function recordLobbying(rawState, input) {
    const state = normalizeState(rawState);
    const id = String(input?.id || "").trim();
    const stageId = String(input?.stageId || "").trim();
    const targetId = String(input?.targetId || "").trim();
    const targetName = String(input?.targetName || targetId).trim();
    const member = state.members.find((entry) => entry.id === input?.memberId);
    const knowledge = state.knowledge.find((entry) => entry.id === input?.knowledgeId && entry.stageId === stageId);
    const council = input?.councilId ? state.councils.find((entry) => entry.id === input.councilId) : null;
    if (!id || !stageId || !targetId || !member || !knowledge) throw new Error("游说须绑定本回史料、使者与诸侯");
    if (input?.councilId && (!council || council.stageId !== stageId || council.knowledgeId !== knowledge.id || council.memberId !== member.id)) throw new Error("游说军议与本回来源不匹配");
    if (!["accepted", "rejected"].includes(input?.outcome)) throw new Error("游说结果无效");
    const record = {
      id, stageId, targetId, targetName, memberId: member.id, memberName: member.name,
      knowledge: { id: knowledge.id, name: knowledge.name, summary: knowledge.summary || "" },
      council: council ? copy(council) : null,
      proposal: String(input?.proposal || "").trim(), outcome: input.outcome,
      decision: input?.decision ? copy(input.decision) : null, month: state.month
    };
    if (!record.proposal) throw new Error("游说主张不可为空");
    return applyLobbyingRecord(state, record);
  }

  function applyLobbyingRecord(state, record) {
    const previous = state.diplomacy.lobbying.find((entry) => entry.id === record.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(record)) throw new Error("游说来源记录冲突");
    if (!previous) {
      state.diplomacy.lobbying = [...state.diplomacy.lobbying, record].slice(-30);
      const delta = record.outcome === "accepted" ? 8 : -4;
      state.diplomacy.relations[record.targetId] = clamp(Number(state.diplomacy.relations[record.targetId] || 0) + delta, -100, 100);
      state.history.push({ month: state.month, tone: record.outcome === "accepted" ? "good" : "bad", text: record.memberName + "游说" + record.targetName + (record.outcome === "accepted" ? "得其响应。" : "未获响应。") });
    }
    return { state, lobbying: copy(previous || record) };
  }

  function createAlliance(rawState, input) {
    const state = normalizeState(rawState);
    const id = String(input?.id || "").trim();
    const lobbying = state.diplomacy.lobbying.find((entry) => entry.id === input?.lobbyingId);
    const terms = Array.isArray(input?.terms) ? input.terms.map((term) => String(term).trim()).filter(Boolean) : [];
    if (!id || !lobbying || lobbying.outcome !== "accepted") throw new Error("须先有获准的游说记录");
    if (terms.length < 1) throw new Error("盟约须有明确条款");
    const previous = state.diplomacy.alliances.find((entry) => entry.id === id);
    if (previous) {
      if (previous.targetId !== lobbying.targetId || previous.stageId !== lobbying.stageId || previous.lobbyingId !== lobbying.id || JSON.stringify(previous.terms) !== JSON.stringify(terms)) throw new Error("盟约记录冲突");
      return { state, alliance: copy(previous) };
    }
    if (state.diplomacy.alliances.some((entry) => entry.targetId === lobbying.targetId && entry.status === "active")) throw new Error("该诸侯已有生效盟约");
    const alliance = { id, targetId: lobbying.targetId, targetName: lobbying.targetName, stageId: lobbying.stageId, lobbyingId: lobbying.id, terms, status: "active", signedMonth: state.month };
    state.diplomacy.alliances = [...state.diplomacy.alliances, alliance].slice(-20);
    state.diplomacy.relations[alliance.targetId] = clamp(Number(state.diplomacy.relations[alliance.targetId] || 0) + 12, -100, 100);
    state.archives.push({ id: "alliance:" + id, month: state.month, type: "alliance", stageId: alliance.stageId, title: "与" + alliance.targetName + "结盟", text: terms.join("；") });
    return { state, alliance: copy(alliance) };
  }

  function breakAlliance(rawState, input) {
    const state = normalizeState(rawState);
    const alliance = state.diplomacy.alliances.find((entry) => entry.id === input?.allianceId);
    const stageId = String(input?.stageId || "").trim();
    const reason = String(input?.reason || "").trim();
    if (!alliance || alliance.status !== "active") throw new Error("没有可背弃的生效盟约");
    if (!stageId || !reason) throw new Error("背盟须绑定战役并说明缘由");
    alliance.status = "broken";
    alliance.betrayalStageId = stageId;
    alliance.betrayalReason = reason;
    alliance.brokenMonth = state.month;
    state.diplomacy.relations[alliance.targetId] = clamp(Number(state.diplomacy.relations[alliance.targetId] || 0) - 35, -100, 100);
    state.pendingSupport.push({ id: "betrayal:" + alliance.id, stageId, source: "背盟攻" + alliance.targetName, morale: -8, attack: 0.06, alliance: copy(alliance) });
    state.archives.push({ id: "betrayal:" + alliance.id, month: state.month, type: "betrayal", stageId, title: "背盟：" + alliance.targetName, text: reason });
    return { state, alliance: copy(alliance) };
  }

  function recordBattleOutcome(rawState, input) {
    const state = normalizeState(rawState);
    const id = String(input?.id || "").trim();
    const stageId = String(input?.stageId || "").trim();
    if (!id || !stageId || typeof input?.won !== "boolean") throw new Error("战后回报不完整");
    const previous = state.battleReports.find((entry) => entry.id === id);
    if (previous) {
      const same = previous.stageId === stageId && previous.won === input.won && previous.turns === Math.max(0, Number(input.turns || 0)) && previous.ownLosses === Math.max(0, Number(input.ownLosses || 0)) && previous.terminalReason === String(input.terminalReason || "") && JSON.stringify(previous.support) === JSON.stringify(input.support && typeof input.support === "object" ? input.support : {});
      if (!same) throw new Error("战后回报记录冲突");
      return { state, report: copy(previous), duplicate: true };
    }
    const support = input.support && typeof input.support === "object" ? copy(input.support) : {};
    const report = {
      id, stageId, stageTitle: String(input.stageTitle || stageId), won: input.won,
      turns: Math.max(0, Number(input.turns || 0)), ownLosses: Math.max(0, Number(input.ownLosses || 0)),
      terminalReason: String(input.terminalReason || ""), support,
      councils: Array.isArray(support.councils) ? support.councils.map(copy) : [],
      mandates: Array.isArray(support.mandates) ? support.mandates.map(copy) : [],
      sources: Array.isArray(support.sources) ? support.sources.map(String) : [], month: state.month
    };
    const affected = new Set(report.councils.map((entry) => entry.memberId).filter(Boolean));
    for (const order of Array.isArray(support.orders) ? support.orders : []) if (order.memberId) affected.add(order.memberId);
    const delta = input.won ? 4 : -3;
    for (const memberId of affected) {
      state.relations[memberId] = clamp(Number(state.relations[memberId] || 0) + delta, -100, 100);
      state.relationEvents.push({ id: id + ":" + memberId, reportId: id, stageId, memberId, delta, reason: input.won ? "战策奏效" : "战策受挫" });
    }
    for (const used of report.mandates) {
      const mandate = state.mandates.find((entry) => entry.id === used.id);
      if (!mandate) continue;
      mandate.state = "RESOLVED";
      mandate.reportId = id;
      mandate.outcome = { won: input.won, turns: report.turns, ownLosses: report.ownLosses };
    }
    const betrayal = state.diplomacy.alliances.find((entry) => entry.status === "broken" && entry.betrayalStageId === stageId && !entry.resolvedReportId);
    if (betrayal) {
      betrayal.status = "resolved";
      betrayal.resolvedReportId = id;
      betrayal.battleWon = input.won;
      state.diplomacy.relations[betrayal.targetId] = clamp(Number(state.diplomacy.relations[betrayal.targetId] || 0) + (input.won ? -10 : -5), -100, 100);
      report.betrayal = { allianceId: betrayal.id, targetId: betrayal.targetId, targetName: betrayal.targetName, reason: betrayal.betrayalReason };
    }
    state.battleReports.push(report);
    state.archives.push({ id: "battle:" + id, month: state.month, type: "battle", stageId, title: report.stageTitle + (input.won ? "告捷" : "失利"), text: "用时" + report.turns + "回合，折损" + report.ownLosses + "部" + (report.sources.length ? "；筹备：" + report.sources.join("、") : "") + (report.mandates.length ? "；内核军令已结案" : "") });
    state.battleReports = state.battleReports.slice(-40);
    state.relationEvents = state.relationEvents.slice(-80);
    state.archives = state.archives.slice(-80);
    return { state, report: copy(report), duplicate: false };
  }

  function resolveTask(state, task) {
    const definition = TASK_TYPES[task.type];
    const member = state.members.find((entry) => entry.id === task.assigneeId) || normalizeMember({ id: task.assigneeId, name: task.assigneeName }, 0);
    const officeFit = member.office === definition.office ? 12 : 0;
    const knowledgeFit = task.knowledgeId ? 10 : 0;
    const chance = clamp(definition.base + officeFit + knowledgeFit + (member.loyalty - 60) * 0.25 - member.fatigue * 0.22, 25, 95);
    const roll = hash(`${task.id}:${state.month}:${member.loyalty}`) % 100;
    const success = roll < chance;
    task.status = success ? "success" : "failed";
    task.resolvedMonth = state.month;
    task.chance = Math.round(chance);
    task.roll = roll;
    if (success) {
      state.influence = clamp(state.influence + 2, 0, 999);
      member.loyalty = clamp(member.loyalty + 2, 20, 100);
      state.relations[member.id] = clamp(Number(state.relations[member.id] || 0) + 3, -100, 100);
      state.pendingSupport.push({ id: task.id, stageId: task.stageId, source: task.name, memberId: member.id, ...definition.reward });
      state.history.push({ month: state.month, tone: "good", text: `${member.name}办成“${task.name}”，所获将用于${task.stageTitle || "下一战"}。` });
    } else {
      state.influence = clamp(state.influence - 1, 0, 999);
      member.loyalty = clamp(member.loyalty - 1, 20, 100);
      state.relations[member.id] = clamp(Number(state.relations[member.id] || 0) - 2, -100, 100);
      state.history.push({ month: state.month, tone: "bad", text: `${member.name}未能办成“${task.name}”，军府未获助益。` });
    }
    member.fatigue = clamp(member.fatigue - 8, 0, 100);
  }

  function advanceMonth(rawState, options = {}) {
    const state = normalizeState(rawState);
    const resolveLocalTasks = options.resolveLocalTasks !== false;
    state.month += 1;
    for (const member of state.members) member.fatigue = clamp(member.fatigue - 5, 0, 100);
    for (const task of state.tasks) {
      if (resolveLocalTasks && !task.remoteResult && task.status === "active" && Number(task.dueMonth) <= state.month) resolveTask(state, task);
    }
    state.history = state.history.slice(-40);
    return state;
  }

  function remoteTaskReadyForAdvance(snapshot) {
    if (!snapshot || typeof snapshot !== "object") return false;
    if (snapshot.final_result) {
      if (!snapshot.settlement) return true;
      return ["ACCEPTED", "CENSURED"].includes(snapshot.review?.state);
    }
    return snapshot.execution_started_game_time !== null
      && snapshot.execution_started_game_time !== undefined;
  }

  function reconcileRemoteTasks(rawState, snapshots, options = {}) {
    const state = normalizeState(rawState);
    const advance = options.advanceMonth !== false;
    if (advance) {
      state.month += 1;
      for (const member of state.members) member.fatigue = clamp(member.fatigue - 5, 0, 100);
    }
    const byId = new Map((snapshots || []).filter(Boolean).map((snapshot) => [String(snapshot.task_id || ""), snapshot]));
    for (const task of state.tasks) {
      if (task.status !== "active" || !task.remoteResult) continue;
      const snapshot = byId.get(String(task.remoteResult));
      if (!snapshot) continue;
      task.remoteState = snapshot.state;
      task.remoteVersion = snapshot.version;
      if (snapshot.npcOutcome && typeof snapshot.npcOutcome === "object") {
        task.npcOutcome = copy(snapshot.npcOutcome);
      }
      const finalResult = snapshot.final_result;
      if (!finalResult) continue;
      if (snapshot.review && typeof snapshot.review === "object") {
        task.pendingReview = copy(snapshot.review);
      }
      if (snapshot.settlement && typeof snapshot.settlement === "object") task.pendingSettlement = copy(snapshot.settlement);
      const reviewState = snapshot.review?.state;
      if (snapshot.settlement && !["ACCEPTED", "CENSURED"].includes(reviewState)) continue;
      const censured = reviewState === "CENSURED";
      if (snapshot.review?.review) task.review = copy(snapshot.review.review);
      delete task.pendingReview;
      delete task.pendingSettlement;
      const member = state.members.find((entry) => entry.id === task.assigneeId) || normalizeMember({ id: task.assigneeId, name: task.assigneeName }, 0);
      const definition = TASK_TYPES[task.type];
      const success = !censured && (finalResult === "SUCCESS" || finalResult === "PARTIAL");
      task.status = censured ? "censured" : finalResult === "SUCCESS" ? "success" : finalResult === "PARTIAL" ? "partial" : "failed";
      task.resolvedMonth = state.month;
      task.remoteFinalResult = finalResult;
      const settlement = snapshot.settlement;
      const closureReceipt = snapshot.closureReceipt;
      if (settlement && typeof settlement === "object") {
        const settlementId = String(settlement.settlementId || "");
        const organizationDelta = Number(settlement.organizationDelta);
        const memberDelta = Number(settlement.memberDelta);
        if (!settlementId || !Number.isSafeInteger(organizationDelta) || !Number.isSafeInteger(memberDelta)) {
          throw new Error("组织结算凭据无效");
        }
        if (settlement.taskId !== task.remoteResult || settlement.result !== finalResult || settlement.memberId === undefined) {
          throw new Error("组织结算与差事不匹配");
        }
        if (!closureReceipt || closureReceipt.state !== "SEALED" || closureReceipt.settlement?.settlementId !== settlementId) {
          throw new Error("内核结案印记无效");
        }
        if (state.settlementIds.includes(settlementId)) continue;
        state.contribution = Math.trunc(clamp(state.contribution + organizationDelta, -999999, 999999));
        member.merit = Math.trunc(clamp(member.merit + memberDelta, -999999, 999999));
        const influenceDelta = organizationDelta === 0 ? 0 : Math.sign(organizationDelta) * Math.max(1, Math.ceil(Math.abs(organizationDelta) / 50));
        state.influence = clamp(state.influence + influenceDelta, 0, 999);
        task.settlement = copy(settlement);
        task.closureReceipt = copy(closureReceipt);
        state.settlements.push({ ...copy(settlement), closureReceipt: copy(closureReceipt) });
        state.settlements = state.settlements.slice(-100);
        state.settlementIds.push(settlementId);
      }
      const mandate = task.mandate ? state.mandates.find((entry) => entry.id === task.mandate.id) : null;
      if (mandate) {
        mandate.state = censured ? "CENSURED" : finalResult === "SUCCESS" ? "FULFILLED" : finalResult === "PARTIAL" ? "PARTIAL" : "FAILED";
        mandate.organizationTaskId = task.remoteResult;
        mandate.organizationResult = finalResult;
      }
      if (censured) {
        member.loyalty = clamp(member.loyalty - 1, 20, 100);
        state.relations[member.id] = clamp(Number(state.relations[member.id] || 0) - 2, -100, 100);
        state.history.push({ month: state.month, tone: "bad", text: `${member.name}复命所报“${task.name}”被申斥，簿书功过照录，军府不取其助益。` });
      } else if (success) {
        const factor = finalResult === "PARTIAL" ? 0.5 : 1;
        if (!settlement) state.influence = clamp(state.influence + (finalResult === "PARTIAL" ? 1 : 2), 0, 999);
        member.loyalty = clamp(member.loyalty + 1, 20, 100);
        state.relations[member.id] = clamp(Number(state.relations[member.id] || 0) + 2, -100, 100);
        const reward = Object.fromEntries(Object.entries(definition.reward).map(([key, value]) => [key, Number(value) * factor]));
        state.pendingSupport.push({ id: task.id, stageId: task.stageId, source: task.name, memberId: member.id, council: task.council ? copy(task.council) : null, mandate: mandate ? copy(mandate) : task.mandate ? copy(task.mandate) : null, ...reward });
        state.history.push({ month: state.month, tone: "good", text: `${member.name}${finalResult === "PARTIAL" ? "部分办成" : "办成"}“${task.name}”，成果将用于${task.stageTitle || "下一战"}。` });
      } else {
        if (!settlement) state.influence = clamp(state.influence - 1, 0, 999);
        state.history.push({ month: state.month, tone: "bad", text: `${member.name}未能办成“${task.name}”，军府未获助益。` });
      }
      if (task.operation?.kind === "diplomacy") {
        const accepted = !censured && finalResult === "SUCCESS";
        applyLobbyingRecord(state, {
          id: "lobby:" + task.remoteResult,
          stageId: task.stageId,
          targetId: String(task.operation.target_id),
          targetName: String(task.operation.target_name),
          memberId: task.assigneeId,
          memberName: task.assigneeName,
          knowledge: { id: task.knowledgeId, name: task.council?.knowledgeName || task.knowledgeId, summary: task.council?.knowledgeSummary || "" },
          council: task.council ? copy(task.council) : null,
          proposal: String(task.operation.proposal),
          outcome: accepted ? "accepted" : "rejected",
          decision: { type: "ORGFLOW_RESULT", finalResult },
          organizationTaskId: task.remoteResult,
          mandateId: task.mandate?.id || null,
          month: state.month
        });
      }
      member.fatigue = clamp(member.fatigue - 8, 0, 100);
    }
    state.history = state.history.slice(-40);
    return state;
  }

  function recordTaskReview(rawState, input) {
    const state = normalizeState(rawState);
    const task = state.tasks.find((entry) => entry.status === "active" && String(entry.remoteResult) === String(input?.taskId || ""));
    const review = input?.review;
    if (!task || !review || !["ACCEPTED", "CENSURED"].includes(review.state)) throw new Error("复命裁决与当前差事不匹配");
    const pending = task.pendingReview;
    if (!pending || pending.review?.settlementId !== review.review?.settlementId || pending.review?.closureDigest !== review.review?.closureDigest) {
      throw new Error("复命裁决印记与待裁簿书不匹配");
    }
    task.pendingReview = copy(review);
    return { state, task: copy(task) };
  }

  function consumeSupport(rawState, stageId) {
    const state = normalizeState(rawState);
    const stageKey = String(stageId || "");
    const selected = state.pendingSupport.filter((entry) => !entry.stageId || entry.stageId === stageKey);
    state.pendingSupport = state.pendingSupport.filter((entry) => entry.stageId && entry.stageId !== stageKey);
    const support = selected.reduce((total, entry) => ({
      provisions: total.provisions + Number(entry.provisions || 0),
      morale: total.morale + Number(entry.morale || 0),
      attack: total.attack + Number(entry.attack || 0),
      defense: total.defense + Number(entry.defense || 0),
      recon: total.recon + Number(entry.recon || 0),
      sources: [...total.sources, entry.source],
      councils: [...total.councils, ...(entry.council ? [copy(entry.council)] : [])],
      mandates: [...total.mandates, ...(entry.mandate ? [copy(entry.mandate)] : [])],
      orders: [...total.orders, { id: entry.id, memberId: entry.memberId || null, source: entry.source }],
      alliances: [...total.alliances, ...(entry.alliance ? [copy(entry.alliance)] : [])]
    }), { provisions: 0, morale: 0, attack: 0, defense: 0, recon: 0, sources: [], councils: [], mandates: [], orders: [], alliances: [] });
    if (selected.length) state.history.push({ month: state.month, tone: "good", text: `${selected.length}项官署筹备已投入${stageKey ? `第${stageKey}战` : "战事"}。` });
    return { state, support };
  }

  function selectEvidence(rawState, input) {
    const state = normalizeState(rawState);
    const stageId = String(input?.stageId || "");
    const knowledge = state.knowledge.find((entry) => entry.id === String(input?.knowledgeId || "") && entry.stageId === stageId);
    const index = Number(input?.sourceIndex);
    const source = knowledge?.sources?.[index];
    if (!stageId || !knowledge || !Number.isInteger(index) || !source?.work) throw new Error("所选出处不属于本回已发布史料");
    const selection = {
      knowledgeId: knowledge.id, index, work: String(source.work), tier: String(source.tier || "来源"),
      scope: String(source.scope || ""), url: String(source.url || ""),
      ...(knowledge.searchReceipt ? { searchReceipt: copy(knowledge.searchReceipt) } : {}),
      ...(knowledge.retrieval ? { retrieval: copy(knowledge.retrieval) } : {})
    };
    state.selectedSources[stageId] = selection;
    state.history.push({ month: state.month, tone: "knowledge", text: `本回选证：${selection.work}（${selection.tier}）` });
    state.history = state.history.slice(-80);
    return { state, source: copy(selection), knowledge: copy(knowledge) };
  }

  function recordKnowledge(rawState, entry) {
    const state = normalizeState(rawState);
    if (!entry?.id) return state;
    const sources = Array.isArray(entry.sourceDetails) ? entry.sourceDetails : [];
    const channels = Array.isArray(entry.retrieval?.channels) ? entry.retrieval.channels.filter((item) => item && ["vector", "bm25", "entity", "category", "schedule_tag", "graph"].includes(item.channel)).slice(0, 6).map((item) => ({
      channel: item.channel, score: Number(item.score || 0), normalizedScore: clamp(item.normalizedScore, 0, 1), rank: Math.max(1, Math.trunc(Number(item.rank || 1)))
    })) : [];
    const retrieval = channels.length ? {
      aggregateScore: clamp(entry.retrieval?.aggregateScore, 0, 1), strongestChannel: String(entry.retrieval?.strongestChannel || ""),
      graphRelated: Boolean(entry.retrieval?.graphRelated), channels
    } : null;
    const searchReceipt = entry.searchReceipt && typeof entry.searchReceipt.id === "string" && /^[0-9a-f]{64}$/.test(String(entry.searchReceipt.digest || ""))
      ? { id: entry.searchReceipt.id, digest: entry.searchReceipt.digest }
      : null;
    state.knowledge = [{
      id: String(entry.id), name: String(entry.name || entry.title || "史官条目"), summary: String(entry.summary || ""),
      content: String(entry.content || ""), stageId: String(entry.stageId || ""),
      ...(retrieval ? { retrieval } : {}), ...(searchReceipt ? { searchReceipt } : {}),
      sources: sources.filter((source) => source && typeof source === "object" && source.work).slice(0, 20).map((source, index) => ({
        index, work: String(source.work), tier: String(source.tier || "来源"), scope: String(source.scope || ""), url: String(source.url || "")
      }))
    }, ...state.knowledge.filter((item) => item.id !== String(entry.id))].slice(0, 30);
    return state;
  }

  function selectCorrespondence(rawState, input) {
    const state = normalizeState(rawState);
    const stageId = String(input?.stageId || "");
    const heroId = String(input?.heroId || "");
    const message = input?.message;
    if (!stageId || !state.members.some((entry) => entry.id === heroId)) throw new Error("耳报缺少本回属官");
    if (!message?.messageId || !/^[0-9a-f]{64}$/.test(String(message.digest || "")) || !message.content) throw new Error("耳报来源印记无效");
    const selected = {
      heroId, messageId: String(message.messageId), digest: String(message.digest),
      chatId: String(message.chatId || ""), taskId: String(message.taskId || ""), speakerId: String(message.speakerId || ""),
      speakerName: String(message.speakerName || "属官"), targetId: String(message.targetId || ""),
      targetName: String(message.targetName || ""), content: String(message.content),
      emotion: String(message.emotion || ""), topic: String(message.topic || ""),
      deliveredAt: String(message.deliveredAt || "")
    };
    state.selectedCorrespondence[stageId] = selected;
    state.history.push({ month: state.month, tone: "knowledge", text: `本回取耳报：${selected.speakerName}“${selected.content.slice(0, 32)}”` });
    state.history = state.history.slice(-40);
    return { state, correspondence: copy(selected) };
  }

  function updateBackend(rawState, status) {
    const state = normalizeState(rawState);
    state.backend = { ...state.backend, ...(status || {}), checkedAt: new Date().toISOString() };
    state.backend.mode = state.backend.nexusKernel && state.backend.orgFlow && state.backend.aiNpc && state.backend.knowledge ? "connected" : "local";
    return state;
  }

  return { SCHEMA_VERSION, TASK_TYPES, defaultState, normalizeState, syncMembers, recordCouncil, recordMandate, recordLobbying, createAlliance, breakAlliance, recordBattleOutcome, createTask, advanceMonth, remoteTaskReadyForAdvance, reconcileRemoteTasks, recordTaskReview, consumeSupport, recordKnowledge, selectEvidence, selectCorrespondence, updateBackend, hash };
});
