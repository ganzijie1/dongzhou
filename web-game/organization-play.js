(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouOrganizationPlay = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SCHEMA_VERSION = 1;
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
      influence: 12,
      backend: { mode: "local", orgFlow: false, aiNpc: false, knowledge: false, checkedAt: null },
      members: [],
      tasks: [],
      knowledge: [],
      relations: {},
      pendingSupport: [],
      history: []
    };
  }

  function normalizeMember(member, index) {
    return {
      id: String(member?.id || `officer-${index + 1}`),
      name: String(member?.name || `属官${index + 1}`),
      office: String(member?.office || ["司马", "司徒", "司寇", "行人"][index % 4]),
      loyalty: clamp(member?.loyalty ?? 68, 20, 100),
      fatigue: clamp(member?.fatigue ?? 0, 0, 100)
    };
  }

  function normalizeState(raw) {
    const source = raw && typeof raw === "object" ? raw : {};
    const base = defaultState();
    return {
      ...base,
      ...source,
      schemaVersion: SCHEMA_VERSION,
      month: Math.max(1, Math.floor(Number(source.month || 1))),
      influence: clamp(source.influence ?? 12, 0, 999),
      backend: { ...base.backend, ...(source.backend || {}) },
      members: Array.isArray(source.members) ? source.members.slice(0, 12).map(normalizeMember) : [],
      tasks: Array.isArray(source.tasks) ? source.tasks.slice(-40).map((task) => ({ ...task })) : [],
      knowledge: Array.isArray(source.knowledge) ? source.knowledge.slice(-30).map((entry) => ({ ...entry })) : [],
      relations: source.relations && typeof source.relations === "object" ? { ...source.relations } : {},
      pendingSupport: Array.isArray(source.pendingSupport) ? source.pendingSupport.slice(-12).map((entry) => ({ ...entry })) : [],
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

  function createTask(rawState, input) {
    const state = normalizeState(rawState);
    const definition = TASK_TYPES[input?.type];
    if (!definition) throw new Error("未知差事");
    const member = state.members.find((entry) => entry.id === input?.assigneeId);
    if (!member) throw new Error("请选择承办官员");
    const active = state.tasks.some((task) => task.status === "active" && task.assigneeId === member.id);
    if (active) throw new Error(`${member.name}已有差事在身`);
    const serial = state.tasks.length + state.history.length + 1;
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
      state.pendingSupport.push({ id: task.id, stageId: task.stageId, source: task.name, ...definition.reward });
      state.history.push({ month: state.month, tone: "good", text: `${member.name}办成“${task.name}”，所获将用于${task.stageTitle || "下一战"}。` });
    } else {
      state.influence = clamp(state.influence - 1, 0, 999);
      member.loyalty = clamp(member.loyalty - 1, 20, 100);
      state.relations[member.id] = clamp(Number(state.relations[member.id] || 0) - 2, -100, 100);
      state.history.push({ month: state.month, tone: "bad", text: `${member.name}未能办成“${task.name}”，军府未获助益。` });
    }
    member.fatigue = clamp(member.fatigue - 8, 0, 100);
  }

  function advanceMonth(rawState) {
    const state = normalizeState(rawState);
    state.month += 1;
    for (const member of state.members) member.fatigue = clamp(member.fatigue - 5, 0, 100);
    for (const task of state.tasks) {
      if (task.status === "active" && Number(task.dueMonth) <= state.month) resolveTask(state, task);
    }
    state.history = state.history.slice(-40);
    return state;
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
      sources: [...total.sources, entry.source]
    }), { provisions: 0, morale: 0, attack: 0, defense: 0, recon: 0, sources: [] });
    if (selected.length) state.history.push({ month: state.month, tone: "good", text: `${selected.length}项官署筹备已投入${stageKey ? `第${stageKey}战` : "战事"}。` });
    return { state, support };
  }

  function recordKnowledge(rawState, entry) {
    const state = normalizeState(rawState);
    if (!entry?.id) return state;
    state.knowledge = [{ id: String(entry.id), name: String(entry.name || entry.title || "史官条目"), summary: String(entry.summary || ""), stageId: String(entry.stageId || "") }, ...state.knowledge.filter((item) => item.id !== String(entry.id))].slice(0, 30);
    return state;
  }

  function updateBackend(rawState, status) {
    const state = normalizeState(rawState);
    state.backend = { ...state.backend, ...(status || {}), checkedAt: new Date().toISOString() };
    state.backend.mode = state.backend.orgFlow || state.backend.aiNpc || state.backend.knowledge ? "connected" : "local";
    return state;
  }

  return { SCHEMA_VERSION, TASK_TYPES, defaultState, normalizeState, syncMembers, createTask, advanceMonth, consumeSupport, recordKnowledge, updateBackend, hash };
});
