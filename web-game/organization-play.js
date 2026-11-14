(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouOrganizationPlay = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SCHEMA_VERSION = 18;
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
      remoteRoster: { organization: null, members: [], playerMembership: null, openPositions: [], observedAt: null },
      tasks: [],
      knowledge: [],
      selectedSources: {},
      selectedCorrespondence: {},
      thoughts: [],
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
      inventoryRequisitions: [],
      inventoryRequisitionIds: [],
      logisticsBriefings: [],
      commendations: [],
      recollections: [],
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
      remoteRoster: {
        organization: source.remoteRoster?.organization && typeof source.remoteRoster.organization === "object" ? copy(source.remoteRoster.organization) : null,
        members: Array.isArray(source.remoteRoster?.members) ? source.remoteRoster.members.filter((entry) => entry && typeof entry === "object").slice(0, 12).map(copy) : [],
        playerMembership: source.remoteRoster?.playerMembership && typeof source.remoteRoster.playerMembership === "object" ? copy(source.remoteRoster.playerMembership) : null,
        openPositions: Array.isArray(source.remoteRoster?.openPositions) ? source.remoteRoster.openPositions.filter((entry) => entry && typeof entry === "object").slice(0, 12).map(copy) : [],
        observedAt: typeof source.remoteRoster?.observedAt === "string" ? source.remoteRoster.observedAt : null
      },
      tasks: retainedTasks.map((task) => ({ ...task, status: ['active', 'success', 'partial', 'failed', 'censured'].includes(task.status) ? task.status : 'failed' })),
      knowledge: Array.isArray(source.knowledge) ? source.knowledge.slice(-30).map((entry) => ({ ...entry })) : [],
      selectedSources: source.selectedSources && typeof source.selectedSources === "object" ? copy(source.selectedSources) : {},
      selectedCorrespondence: source.selectedCorrespondence && typeof source.selectedCorrespondence === "object" ? copy(source.selectedCorrespondence) : {},
      thoughts: Array.isArray(source.thoughts) ? source.thoughts.filter((entry) => entry && typeof entry === "object").slice(-30).map(copy) : [],
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
      inventoryRequisitions: Array.isArray(source.inventoryRequisitions)
        ? source.inventoryRequisitions.filter((entry) => entry && typeof entry.requestId === "string").slice(-100).map(copy)
        : [],
      inventoryRequisitionIds: [...new Set([
        ...(Array.isArray(source.inventoryRequisitionIds) ? source.inventoryRequisitionIds : []),
        ...(Array.isArray(source.inventoryRequisitions) ? source.inventoryRequisitions.map((entry) => entry?.requestId) : [])
      ].filter((value) => typeof value === "string" && value))],
      logisticsBriefings: Array.isArray(source.logisticsBriefings)
        ? source.logisticsBriefings.filter((entry) => entry && typeof entry.requestId === "string").slice(-30).map(copy)
        : [],
      commendations: Array.isArray(source.commendations)
        ? source.commendations.filter((entry) => entry && typeof entry.eventId === "string").slice(-60).map(copy)
        : [],
      recollections: Array.isArray(source.recollections)
        ? source.recollections.filter((entry) => entry && typeof entry.recollectionId === "string").slice(-60).map(copy)
        : [],
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
    const dialogueReceipt = input.dialogueReceipt && typeof input.dialogueReceipt === 'object' ? copy(input.dialogueReceipt) : null;
    if (dialogueReceipt && (dialogueReceipt.state !== 'RECORDED' || !String(dialogueReceipt.sourceRecordId || '').startsWith('dongzhou-council:') || !/^[0-9a-f]{64}$/.test(String(dialogueReceipt.digest || '')))) throw new Error('军议对话归档回执无效');
    const memory = input.memory && typeof input.memory === 'object' ? copy(input.memory) : null;
    if (memory && (!memory.idempotencyKey || !memory.content || !/^[0-9a-f]{64}$/.test(String(memory.digest || '')) || !String(input.question || '').includes(`记忆印记：${memory.digest.slice(0, 12)}`))) throw new Error('军议旧事回执无效');
    const publicNotice = input.publicNotice && typeof input.publicNotice === 'object' ? copy(input.publicNotice) : null;
    if (publicNotice && (!String(publicNotice.messageId || '').startsWith('npc-public:') || publicNotice.heroId !== member.id || !String(publicNotice.message || '').trim() || !/^[0-9a-f]{64}$/.test(String(publicNotice.digest || '')) || publicNotice.kernel?.module !== 'dongzhou_npc_public_notice' || publicNotice.kernel?.state !== 'SEALED' || !String(input.question || '').includes(`告示印记：${publicNotice.digest.slice(0, 12)}`))) throw new Error('军议官署告示回执无效');
    const contribution = input.contribution && typeof input.contribution === 'object' ? copy(input.contribution) : null;
    if (contribution && (!contribution.entryId || contribution.heroId !== member.id || !Number.isSafeInteger(contribution.entryVersion) || !Number.isSafeInteger(contribution.amount) || contribution.amount === 0 || !/^[0-9a-f]{64}$/.test(String(contribution.digest || '')) || contribution.kernel?.module !== 'dongzhou_organization_contribution_ledger' || contribution.kernel?.state !== 'SEALED' || !String(input.question || '').includes(`功绩印记：${contribution.digest.slice(0, 12)}`))) throw new Error('军议属官功绩回执无效');
    const knowledgeMastery = input.knowledgeMastery && typeof input.knowledgeMastery === 'object' ? copy(input.knowledgeMastery) : null;
    if (knowledgeMastery && (!knowledgeMastery.questionId || knowledgeMastery.stageId !== stageId || knowledgeMastery.knowledgeId !== knowledge.id || knowledgeMastery.correct !== true || Number(knowledgeMastery.score) !== 10 || !/^[0-9a-f]{64}$/.test(String(knowledgeMastery.receipt?.digest || '')) || knowledgeMastery.receipt?.kernel?.module !== 'dongzhou_knowledge_tournament' || knowledgeMastery.receipt?.kernel?.state !== 'SEALED' || !String(input.question || '').includes(`史识印记：${knowledgeMastery.receipt.digest.slice(0, 12)}`))) throw new Error('史官问对回执无效');
    if (correspondence && (correspondence.heroId !== member.id || !/^[0-9a-f]{64}$/.test(String(correspondence.digest || "")))) throw new Error('所选耳报不属于当前属官');
    const thought = input.thoughtRequestId ? state.thoughts.find((entry) => entry.requestId === input.thoughtRequestId) : null;
    if (input.thoughtRequestId && (!thought || thought.digest !== input.thoughtDigest || thought.heroId !== member.id || thought.stageId !== stageId || thought.knowledgeId !== knowledge.id || Number(thought.source?.index) !== Number(input.evidenceSourceIndex) || thought.thought?.hasThought !== true || thought.councilProposal !== options[input.index])) throw new Error('属官进言与本次军议结果不匹配');
    const council = { id: String(input.id), stageId, memberId: member.id, memberName: member.name,
      knowledgeId: knowledge.id, knowledgeName: String(input.knowledgeName || knowledge.name),
      knowledgeSummary: String(input.knowledgeSummary ?? knowledge.summary ?? ''), evidenceSource: copy(evidenceSource), question: String(input.question),
      correspondence: correspondence ? copy(correspondence) : null,
      thought: thought ? copy(thought) : null,
      memory,
      publicNotice,
      contribution,
      knowledgeMastery,
      dialogueReceipt,
      options: options.slice(), index: input.index, text: options[input.index] };
    const previous = state.councils.find((entry) => entry.id === council.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(council)) throw new Error('军议来源记录冲突');
    if (!previous) state.councils = [...state.councils, council].slice(-30);
    return { state, council: copy(previous || council) };
  }

  function recordThought(rawState, input) {
    const state = normalizeState(rawState);
    const receipt = input && typeof input === "object" ? copy(input) : null;
    const member = state.members.find((entry) => entry.id === receipt?.heroId);
    const knowledge = state.knowledge.find((entry) => entry.id === receipt?.knowledgeId && entry.stageId === receipt?.stageId);
    if (!receipt?.requestId || !/^[0-9a-f]{64}$/.test(String(receipt.digest || "")) || !member || !knowledge) throw new Error("属官进言回执无效");
    if (!receipt.source?.work || !Number.isInteger(Number(receipt.source.index)) || !receipt.assignment?.planId || !receipt.assignment?.eventId || !receipt.taskType) throw new Error("属官进言缺少史证或当值记录");
    if (!receipt.thought || typeof receipt.thought.hasThought !== "boolean" || !String(receipt.thought.description || "").trim() || !String(receipt.councilProposal || "").trim() || String(receipt.councilProposal).length > 48 || !Number.isFinite(Number(receipt.thought.importance))) throw new Error("属官进言内容无效");
    const previous = state.thoughts.find((entry) => entry.requestId === receipt.requestId);
    if (previous && JSON.stringify(previous) !== JSON.stringify(receipt)) throw new Error("属官进言来源记录冲突");
    if (!previous) state.thoughts = [...state.thoughts, receipt].slice(-30);
    return { state, thought: copy(previous || receipt) };
  }

  function recordLogisticsBriefing(rawState, input) {
    const state = normalizeState(rawState);
    const receipt = input && typeof input === "object" ? copy(input) : null;
    if (
      receipt?.state !== "SEALED"
      || !receipt.requestId
      || !receipt.heroId
      || !receipt.stageId
      || !Number.isSafeInteger(receipt.inventoryRevision)
      || !/^[0-9a-f]{64}$/.test(String(receipt.digest || ""))
      || receipt.kernel?.module !== "dongzhou_logistics_briefing"
      || receipt.kernel?.state !== "SEALED"
      || receipt.ainpcDelivery?.market !== "DELIVERED"
      || receipt.ainpcDelivery?.warehouse !== "DELIVERED"
      || !Number.isSafeInteger(receipt.exchange?.availableUnits)
      || !Number.isSafeInteger(receipt.exchange?.availableLots)
      || receipt.exchange?.priceUnits !== 20
      || receipt.exchange?.provisionsPerLot !== 12
      || !state.members.some((member) => member.id === receipt.heroId)
    ) throw new Error("仓情简报回执无效");
    const previous = state.logisticsBriefings.find((entry) => entry.requestId === receipt.requestId);
    if (previous && JSON.stringify(previous) !== JSON.stringify(receipt)) throw new Error("仓情简报来源记录冲突");
    if (!previous) {
      state.logisticsBriefings = [
        ...state.logisticsBriefings.filter((entry) => entry.heroId !== receipt.heroId || entry.stageId !== receipt.stageId),
        receipt
      ].slice(-30);
      state.history = [...state.history, {
        month: state.month,
        tone: "knowledge",
        text: `${receipt.heroId}查验仓情：军粮 ${Number(receipt.campaignResources?.provisions || 0)}，可调拨 ${receipt.exchange.availableLots} 批`
      }].slice(-40);
    }
    return { state, briefing: copy(previous || receipt) };
  }

  function recordCommendation(rawState, receipt) {
    const state = normalizeState(rawState);
    if (!receipt || receipt.kernel?.module !== "dongzhou_npc_commendation" || receipt.kernel?.state !== "SEALED"
      || !/^[0-9a-f]{64}$/.test(String(receipt.digest || "")) || !String(receipt.eventId || "").startsWith("npc-commendation:")
      || receipt.affectionType !== "appreciation" || Number(receipt.affectionDelta) !== 2) {
      throw new Error("慰勉回执未通过内核校验");
    }
    const previous = state.commendations.find((entry) => entry.eventId === receipt.eventId);
    if (previous && previous.digest !== receipt.digest) throw new Error("同一慰勉事件出现冲突回执");
    if (!previous) {
      state.commendations = [...state.commendations, copy(receipt)].slice(-60);
      state.history.push({ month: state.month, type: "commendation", text: `据《${receipt.knowledgeTitle}》慰勉${receipt.heroId}，感激 +2` });
      state.history = state.history.slice(-40);
    }
    return { state, commendation: copy(previous || receipt), replayed: Boolean(previous) };
  }

  function recordRecollection(rawState, receipt) {
    const state = normalizeState(rawState);
    const requiredText = ["heroId", "stageId", "knowledgeId", "memoryId", "memoryContent"];
    if (!receipt || receipt.kernel?.module !== "dongzhou_npc_recollection" || receipt.kernel?.state !== "SEALED"
      || !/^[0-9a-f]{64}$/.test(String(receipt.digest || ""))
      || !/^[0-9a-f]{64}$/.test(String(receipt.memoryDigest || ""))
      || !String(receipt.recollectionId || "").startsWith("npc-recollection:")
      || requiredText.some((key) => !String(receipt[key] || "").trim())
      || !["dialogue_choice", "system_message"].includes(receipt.memoryType)
      || !["knowledge_dialogue", "latest_system_message"].includes(receipt.matchMode)
      || receipt.memoryReceipt?.idempotencyKey !== receipt.memoryId
      || receipt.memoryReceipt?.sourceType !== receipt.memoryType
      || receipt.memoryReceipt?.timestamp !== receipt.memoryTimestamp
      || receipt.memoryReceipt?.content !== receipt.memoryContent
      || receipt.memoryReceipt?.digest !== receipt.memoryDigest) {
      throw new Error("问忆回执未通过内核校验");
    }
    const previous = state.recollections.find((entry) => entry.recollectionId === receipt.recollectionId);
    if (previous && previous.digest !== receipt.digest) throw new Error("同一问忆事件出现冲突回执");
    if (!previous) {
      state.recollections = [...state.recollections, copy(receipt)].slice(-60);
      state.history.push({ month: state.month, type: "recollection", text: `${receipt.heroId}据史忆起：${receipt.memoryContent.slice(0, 48)}` });
      state.history = state.history.slice(-40);
    }
    return { state, recollection: copy(previous || receipt), replayed: Boolean(previous) };
  }

  function recordMandate(rawState, input) {
    const state = normalizeState(rawState);
    const mandate = input && typeof input === "object" ? copy(input) : null;
    if (!mandate?.id || !mandate.stageId || !mandate.heroId || !mandate.taskType) throw new Error("内核军令缺少关卡、属官或差事");
    if (!mandate.evidence?.id || !mandate.evidence?.source?.work || !mandate.council?.requestId || !mandate.council?.text) throw new Error("内核军令未绑定史料、选证与属官裁断");
    if (mandate.evidence.searchReceipt && (!/^[0-9a-f]{64}$/.test(String(mandate.evidence.searchReceipt.digest || "")) || !Array.isArray(mandate.evidence.retrieval?.channels) || !mandate.evidence.retrieval.channels.length)) throw new Error("内核军令检索回执无效");
    if (mandate.evidenceFit && (mandate.evidenceFit.taskType !== mandate.taskType || !Number.isFinite(Number(mandate.evidenceFit.factor)) || Number(mandate.evidenceFit.factor) < 0 || Number(mandate.evidenceFit.factor) > 9 || !["strong", "aligned", "weak"].includes(mandate.evidenceFit.band) || !Array.isArray(mandate.evidenceFit.signals))) throw new Error("内核军令史证适配无效");
    if (mandate.knowledgeMastery && (mandate.knowledgeMastery.stageId !== mandate.stageId || mandate.knowledgeMastery.knowledgeId !== mandate.evidence.id || Number(mandate.knowledgeMastery.score) !== 10 || Number(mandate.knowledgeMastery.bonus) !== 3 || mandate.knowledgeMastery.state !== "SEALED" || !/^[0-9a-f]{64}$/.test(String(mandate.knowledgeMastery.resultDigest || "")) || mandate.knowledgeMastery.kernel?.module !== "dongzhou_knowledge_tournament" || mandate.knowledgeMastery.kernel?.state !== "SEALED" || mandate.knowledgeMastery.resultDigest !== mandate.council?.knowledgeMastery?.resultDigest)) throw new Error("内核军令史识凭据无效");
    if (mandate.correspondence && (!/^[0-9a-f]{64}$/.test(String(mandate.correspondence.digest || "")) || mandate.correspondence.messageId !== mandate.council?.correspondence?.messageId || mandate.correspondence.digest !== mandate.council?.correspondence?.digest)) throw new Error("内核军令耳报来源无效");
    if (mandate.thought && (!/^[0-9a-f]{64}$/.test(String(mandate.thought.digest || "")) || mandate.thought.requestId !== mandate.council?.thought?.requestId || mandate.thought.digest !== mandate.council?.thought?.digest)) throw new Error("内核军令进言来源无效");
    if (mandate.memory && (!mandate.memory.idempotencyKey || !/^[0-9a-f]{64}$/.test(String(mandate.memory.digest || "")) || mandate.memory.digest !== mandate.council?.memory?.digest)) throw new Error("内核军令旧事来源无效");
    if (mandate.publicNotice && (!String(mandate.publicNotice.messageId || "").startsWith("npc-public:") || mandate.publicNotice.heroId !== mandate.heroId || !/^[0-9a-f]{64}$/.test(String(mandate.publicNotice.digest || "")) || mandate.publicNotice.kernel?.module !== "dongzhou_npc_public_notice" || mandate.publicNotice.kernel?.state !== "SEALED" || mandate.publicNotice.messageId !== mandate.council?.publicNotice?.messageId || mandate.publicNotice.digest !== mandate.council?.publicNotice?.digest)) throw new Error("内核军令官署告示来源无效");
    if (mandate.contribution && (!mandate.contribution.entryId || mandate.contribution.heroId !== mandate.heroId || !Number.isSafeInteger(mandate.contribution.entryVersion) || !Number.isSafeInteger(mandate.contribution.amount) || mandate.contribution.amount === 0 || !/^[0-9a-f]{64}$/.test(String(mandate.contribution.digest || "")) || mandate.contribution.kernel?.module !== "dongzhou_organization_contribution_ledger" || mandate.contribution.kernel?.state !== "SEALED" || mandate.contribution.entryId !== mandate.council?.contribution?.entryId || mandate.contribution.digest !== mandate.council?.contribution?.digest)) throw new Error("内核军令属官功绩来源无效");
    if (!mandate.assignment?.planId || !mandate.assignment?.eventId || mandate.assignment?.heroId !== mandate.heroId) throw new Error("内核军令未绑定属官当值日程");
    if (mandate.collaboration) {
      const collaboration = mandate.collaboration;
      const memberIds = new Set(state.members.map((member) => member.id));
      if (collaboration.primaryHeroId !== mandate.heroId || !collaboration.supportHeroId || collaboration.supportHeroId === mandate.heroId || !memberIds.has(collaboration.supportHeroId)) throw new Error("内核军令协办属官无效");
      if (!collaboration.primaryNpcId || !collaboration.supportNpcId || collaboration.primaryNpcId === collaboration.supportNpcId) throw new Error("内核军令协办身份无效");
      if (!Number.isFinite(Number(collaboration.factor)) || Number(collaboration.factor) < -8 || Number(collaboration.factor) > 10 || !Number.isFinite(Number(collaboration.score)) || Number(collaboration.score) < 10 || Number(collaboration.score) > 100 || !["exceptional", "aligned", "neutral", "strained"].includes(collaboration.band)) throw new Error("内核军令协同评分无效");
      if (!collaboration.supportAssignment?.planId || !collaboration.supportAssignment?.eventId || collaboration.supportAssignment.heroId !== collaboration.supportHeroId) throw new Error("内核军令未绑定副手当值日程");
      if (collaboration.primaryToSupport?.managerNpcId !== collaboration.supportNpcId || collaboration.supportToPrimary?.managerNpcId !== collaboration.primaryNpcId) throw new Error("内核军令双向关系证据无效");
    }
    if (mandate.assignment.personality?.available === true && (!mandate.assignment.personality.profileId || !Array.isArray(mandate.assignment.personality.dominantTraits) || mandate.assignment.personality.fit?.available !== true || !Number.isFinite(Number(mandate.assignment.personality.fit.score)) || Number(mandate.assignment.personality.fit.score) < 0 || Number(mandate.assignment.personality.fit.score) > 100)) throw new Error("内核军令人格适岗证据无效");
    if (mandate.assignment.motivation?.available === true && (!Array.isArray(mandate.assignment.motivation.motives) || mandate.assignment.motivation.fit?.available !== true || !Number.isFinite(Number(mandate.assignment.motivation.fit.score)) || Number(mandate.assignment.motivation.fit.score) < 0 || Number(mandate.assignment.motivation.fit.score) > 100)) throw new Error("内核军令任务意愿证据无效");
    if (mandate.emergency && (typeof mandate.emergency.urgent !== "boolean" || !Number.isFinite(Number(mandate.emergency.score)) || Number(mandate.emergency.score) < 0 || !mandate.emergency.assessedAt || !mandate.emergency.event || (mandate.emergency.urgent && !mandate.emergency.interruptTraceId))) throw new Error("内核军令紧急评估无效");
    const interruption = mandate.scheduleInterruption;
    if (interruption && (
      interruption.mandateId !== mandate.id
      || interruption.mandateDigest !== mandate.digest
      || interruption.heroId !== mandate.heroId
      || !/^[0-9a-f]{64}$/.test(String(interruption.digest || ""))
      || !String(interruption.eventId || "").startsWith("dongzhou-mandate-")
      || !["insert_today", "future", "discard", "expired", "worthless"].includes(interruption.action)
      || (["insert_today", "future"].includes(interruption.action) && (!interruption.scheduleId || !interruption.scheduleName))
    )) throw new Error("属官日程中断回执无效");
    const supportInterruption = mandate.supportScheduleInterruption;
    if (mandate.collaboration && (!supportInterruption
      || supportInterruption.mandateId !== mandate.id
      || supportInterruption.mandateDigest !== mandate.digest
      || supportInterruption.heroId !== mandate.collaboration.supportHeroId
      || supportInterruption.role !== "support"
      || !/^[0-9a-f]{64}$/.test(String(supportInterruption.digest || ""))
      || !String(supportInterruption.eventId || "").startsWith("dongzhou-mandate-support-")
      || !["insert_today", "future", "discard", "expired", "worthless"].includes(supportInterruption.action)
      || (["insert_today", "future"].includes(supportInterruption.action) && (!supportInterruption.scheduleId || !supportInterruption.scheduleName)))) throw new Error("副手日程中断回执无效");
    if (mandate.state !== "ISSUED" || !/^[0-9a-f]{64}$/.test(String(mandate.digest || "")) || !["READY", "DEGRADED"].includes(mandate.kernel?.state)) throw new Error("内核军令尚未签发或印记无效");
    if (mandate.operation && (mandate.taskType !== "diplomacy" || mandate.operation.kind !== "diplomacy" || !mandate.operation.target_id || !mandate.operation.target_name || !mandate.operation.proposal)) throw new Error("外交军令缺少目标或主张");
    const previous = state.mandates.find((entry) => entry.id === mandate.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(mandate)) throw new Error("内核军令来源记录冲突");
    if (!previous) {
      state.mandates = [...state.mandates, mandate].slice(-50);
      state.history.push({ month: state.month, tone: "order", text: `内核签发${mandate.emergency?.urgent ? "急报" : "军令"}：${mandate.evidence.name} · ${mandate.council.text}` });
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
    if ((mandate?.thought?.requestId || null) !== (council?.thought?.requestId || null) || (mandate?.thought?.digest || null) !== (council?.thought?.digest || null)) throw new Error("内核军令与军议进言不匹配");
    if ((mandate?.publicNotice?.messageId || null) !== (council?.publicNotice?.messageId || null) || (mandate?.publicNotice?.digest || null) !== (council?.publicNotice?.digest || null)) throw new Error("内核军令与军议官署告示不匹配");
    if ((mandate?.contribution?.entryId || null) !== (council?.contribution?.entryId || null) || (mandate?.contribution?.digest || null) !== (council?.contribution?.digest || null)) throw new Error("内核军令与军议属官功绩不匹配");
    const operation = input.operation && typeof input.operation === "object" ? copy(input.operation) : mandate?.operation ? copy(mandate.operation) : null;
    if (operation && (input.type !== "diplomacy" || operation.kind !== "diplomacy" || !operation.target_id || !operation.target_name || !operation.proposal || !mandate?.operation || JSON.stringify(operation) !== JSON.stringify(mandate.operation))) throw new Error("外交差事与内核军令不匹配");
    const supportHeroId = mandate?.collaboration?.supportHeroId || null;
    const supportMember = supportHeroId ? state.members.find((entry) => entry.id === supportHeroId) : null;
    if (supportHeroId && (!supportMember || supportHeroId === member.id)) throw new Error("协办副手不在当前官署名册中");
    const participants = new Set([member.id, ...(supportHeroId ? [supportHeroId] : [])]);
    const active = state.tasks.find((task) => task.status === "active" && (
      participants.has(task.assigneeId)
      || participants.has(task.mandate?.collaboration?.supportHeroId)
    ));
    if (active) throw new Error(`${active.assigneeName}及其协办已有差事在身`);
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
      supportNpcOutcomes: [],
      cost: definition.cost
    };
    state.tasks.push(task);
    member.fatigue = clamp(member.fatigue + 12, 0, 100);
    if (supportMember) supportMember.fatigue = clamp(supportMember.fatigue + 8, 0, 100);
    state.history.push({ month: state.month, tone: "order", text: `${member.name}${supportMember ? `与${supportMember.name}` : ""}领命：${definition.name}` });
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
      const same = previous.stageId === stageId && previous.won === input.won && previous.turns === Math.max(0, Number(input.turns || 0)) && previous.ownLosses === Math.max(0, Number(input.ownLosses || 0)) && previous.terminalReason === String(input.terminalReason || "") && JSON.stringify(previous.support) === JSON.stringify(input.support && typeof input.support === "object" ? input.support : {}) && JSON.stringify(previous.campaignRoute || null) === JSON.stringify(input.campaignRoute && typeof input.campaignRoute === "object" ? input.campaignRoute : null);
      if (!same) throw new Error("战后回报记录冲突");
      return { state, report: copy(previous), duplicate: true };
    }
    const support = input.support && typeof input.support === "object" ? copy(input.support) : {};
    const report = {
      id, stageId, stageTitle: String(input.stageTitle || stageId), won: input.won,
      turns: Math.max(0, Number(input.turns || 0)), ownLosses: Math.max(0, Number(input.ownLosses || 0)),
      terminalReason: String(input.terminalReason || ""), support,
      campaignRoute: input.campaignRoute && typeof input.campaignRoute === "object" ? copy(input.campaignRoute) : null,
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
      if (Array.isArray(snapshot.followUps) && snapshot.followUps.some((entry) => entry?.state === "PENDING")) return false;
      if (!snapshot.settlement) return true;
      return ["ACCEPTED", "CENSURED"].includes(snapshot.review?.state);
    }
    return snapshot.execution_started_game_time !== null
      && snapshot.execution_started_game_time !== undefined;
  }

  function registerDerivedTasks(state, snapshots) {
    const knownRemoteIds = new Set(state.tasks.map((task) => String(task.remoteResult || "")).filter(Boolean));
    for (const snapshot of snapshots || []) {
      if (!snapshot || typeof snapshot !== "object" || !Array.isArray(snapshot.followUps)) continue;
      const parent = state.tasks.find((task) => String(task.remoteResult || "") === String(snapshot.task_id || ""));
      if (!parent) continue;
      for (const followUp of snapshot.followUps) {
        if (!followUp || followUp.state !== "CREATED" || !followUp.taskId || knownRemoteIds.has(String(followUp.taskId))) continue;
        if (!Object.prototype.hasOwnProperty.call(TASK_TYPES, followUp.taskType)) throw new Error("组织追办任务类型无效");
        if (!['FOLLOW_UP', 'REMEDIATION'].includes(followUp.source)) throw new Error("组织追办来源无效");
        if (String(followUp.assigneeHeroId) !== String(parent.assigneeId) || String(followUp.stageId) !== String(parent.stageId)) {
          throw new Error("组织追办与原差事不匹配");
        }
        const definition = TASK_TYPES[followUp.taskType];
        const label = followUp.source === 'REMEDIATION' ? '补救' : '追办';
        state.tasks.push({
          ...copy(parent),
          id: `${parent.id}:${String(followUp.intentId || followUp.taskId)}`,
          type: followUp.taskType,
          name: `${label} · ${definition.name}`,
          cost: 0,
          status: 'active',
          createdMonth: state.month,
          dueMonth: state.month + definition.duration,
          resolvedMonth: null,
          remoteResult: String(followUp.taskId),
          remoteState: 'DERIVED',
          remoteVersion: null,
          remoteMirrored: true,
          remoteFinalResult: null,
          mandate: null,
          settlement: null,
          closureReceipt: null,
          pendingSettlement: null,
          pendingReview: null,
          npcOutcome: null,
          supportNpcOutcomes: [],
          derivation: {
            intentId: String(followUp.intentId || ''),
            source: followUp.source,
            ruleId: String(followUp.ruleId || ''),
            predecessorTaskId: String(parent.remoteResult),
          },
        });
        knownRemoteIds.add(String(followUp.taskId));
        state.history.push({ month: state.month, tone: followUp.source === 'REMEDIATION' ? 'bad' : 'neutral', text: `${parent.assigneeName}接到“${parent.name}”的${label}差事。` });
      }
    }
  }

  function reconcileRemoteTasks(rawState, snapshots, options = {}) {
    const state = normalizeState(rawState);
    registerDerivedTasks(state, snapshots);
    const advance = options.advanceMonth !== false;
    if (advance) {
      state.month += 1;
      for (const member of state.members) member.fatigue = clamp(member.fatigue - 5, 0, 100);
    }
    const byId = new Map((snapshots || []).filter(Boolean).map((snapshot) => [String(snapshot.task_id || ""), snapshot]));
    for (const task of state.tasks) {
      if (!task.remoteResult) continue;
      const snapshot = byId.get(String(task.remoteResult));
      if (!snapshot) continue;
      if (snapshot.npcOutcome && typeof snapshot.npcOutcome === "object") {
        task.npcOutcome = copy(snapshot.npcOutcome);
      }
      if (Array.isArray(snapshot.supportNpcOutcomes)) {
        task.supportNpcOutcomes = snapshot.supportNpcOutcomes.map(copy);
      }
      if (snapshot.npcConsequence && typeof snapshot.npcConsequence === "object") {
        task.npcConsequence = copy(snapshot.npcConsequence);
      }
      if (snapshot.collaborationRelationship && typeof snapshot.collaborationRelationship === "object") {
        task.collaborationRelationship = copy(snapshot.collaborationRelationship);
      }
      if (snapshot.organizationTrace && typeof snapshot.organizationTrace === "object") {
        task.organizationTrace = copy(snapshot.organizationTrace);
      }
      if (snapshot.organizationTopology && typeof snapshot.organizationTopology === "object") {
        task.organizationTopology = copy(snapshot.organizationTopology);
      }
      if (task.status !== "active") continue;
      if (task.derivation && snapshot.assigneeHeroId && String(snapshot.assigneeHeroId) !== String(task.assigneeId)) {
        const authoritativeMember = state.members.find((entry) => String(entry.id) === String(snapshot.assigneeHeroId));
        if (!authoritativeMember) throw new Error("组织追办责任人无效");
        task.assigneeId = authoritativeMember.id;
        task.assigneeName = authoritativeMember.name;
      }
      task.remoteState = snapshot.state;
      task.remoteVersion = snapshot.version;
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
        const sealedGrowth = snapshot.review?.growthReward;
        state.contribution = sealedGrowth && Number.isSafeInteger(sealedGrowth.contributionPoints)
          ? Math.trunc(clamp(sealedGrowth.contributionPoints, -999999, 999999))
          : Math.trunc(clamp(state.contribution + organizationDelta, -999999, 999999));
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
      const supportMember = task.mandate?.collaboration?.supportHeroId
        ? state.members.find((entry) => entry.id === task.mandate.collaboration.supportHeroId)
        : null;
      if (supportMember) supportMember.fatigue = clamp(supportMember.fatigue - 6, 0, 100);
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
    const growth = review.growthReward;
    const expectsGrowth = review.state === "ACCEPTED" && Number(task.pendingSettlement?.organizationDelta || 0) > 0;
    const validGrowth = growth
      && growth.settlementId === review.review.settlementId
      && growth.taskId === String(task.remoteResult)
      && growth.closureDigest === review.review.closureDigest
      && Number.isSafeInteger(growth.amount)
      && growth.amount > 0
      && Number.isSafeInteger(growth.contributionPoints)
      && growth.contributionPoints >= growth.amount
      && Number.isSafeInteger(growth.accountVersion)
      && growth.accountVersion > 0
      && typeof growth.digest === "string"
      && /^[0-9a-f]{64}$/.test(growth.digest)
      && growth.kernel?.state === "SEALED";
    if (expectsGrowth && !validGrowth) throw new Error("复命记功印记无效");
    if (growth && !validGrowth) throw new Error("复命记功与待裁簿书不匹配");
    if (validGrowth) state.contribution = growth.contributionPoints;
    task.pendingReview = copy(review);
    return { state, task: copy(task) };
  }

  function recordInventoryRequisition(rawState, response) {
    const state = normalizeState(rawState);
    const requestId = String(response?.requestId || "");
    const stageId = String(response?.stageId || "");
    const debit = response?.inventoryDebit;
    const provisions = response?.effect?.provisions;
    const validDebit = debit
      && debit.resourceKey === "task.execution"
      && Number.isSafeInteger(debit.delta)
      && debit.delta < 0
      && Number.isSafeInteger(debit.balanceAfter)
      && debit.balanceAfter >= 0
      && Number.isSafeInteger(debit.accountVersion)
      && debit.accountVersion > 0
      && Number.isSafeInteger(debit.inventoryRevision)
      && debit.inventoryRevision > 0;
    if (
      response?.state !== "COMPLETED"
      || !requestId
      || !stageId
      || !validDebit
      || !Number.isSafeInteger(provisions)
      || provisions <= 0
      || provisions !== (-debit.delta * 3) / 5
    ) {
      throw new Error("军需调拨回执无效");
    }
    if (state.inventoryRequisitionIds.includes(requestId)) {
      return { state, applied: false, effect: { provisions } };
    }
    const record = {
      requestId,
      stageId,
      provisions,
      inventoryDebit: copy(debit)
    };
    state.inventoryRequisitions.push(record);
    state.inventoryRequisitions = state.inventoryRequisitions.slice(-100);
    state.inventoryRequisitionIds.push(requestId);
    state.inventoryRequisitionIds = [...new Set(state.inventoryRequisitionIds)].slice(-200);
    state.history.push({
      month: state.month,
      tone: "good",
      text: `公共库藏调拨 ${-debit.delta} 点差事额度，为第${stageId}战补入 ${provisions} 军粮。`
    });
    state.history = state.history.slice(-40);
    return { state, applied: true, effect: { provisions } };
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

  function recordRemoteRoster(rawState, snapshot, nameForId) {
    const state = normalizeState(rawState);
    const organization = snapshot?.organization;
    const members = snapshot?.members;
    if (!organization || typeof organization !== "object" || !Array.isArray(members)) throw new Error("官署实账名册无效");
    const growth = organization.growthContribution;
    if (!Number.isSafeInteger(growth)) throw new Error("官署实账贡献无效");
    const normalized = members.slice(0, 12).map((entry) => {
      if (!entry || !/^[A-Za-z0-9_.:-]+$/.test(String(entry.heroId || ""))) throw new Error("官署实账属官无效");
      for (const key of ["contributionBalance", "lifetimeEarned", "lifetimeSpent"]) {
        if (!Number.isSafeInteger(entry[key])) throw new Error("官署实账功绩无效");
      }
      return {
        heroId: String(entry.heroId), office: String(entry.office || ""), role: String(entry.role || ""), level: String(entry.level || ""),
        directManagerHeroId: entry.directManagerHeroId ? String(entry.directManagerHeroId) : null,
        contributionBalance: entry.contributionBalance, lifetimeEarned: entry.lifetimeEarned, lifetimeSpent: entry.lifetimeSpent
      };
    });
    const existingByHero = new Map(state.members.map((member) => [member.id, member]));
    const internalOffice = /^(?:commander|court_officer|officer_\d+)$/i;
    const taskOffices = ["司马", "司徒", "司寇", "行人", "上卿"];
    state.members = normalized.map((account, index) => {
      const existing = existingByHero.get(account.heroId);
      const slot = /^officer_(\d+)$/i.exec(account.office);
      const mappedOffice = account.level === "owner" || account.role === "commander" || account.office === "commander"
        ? "主官"
        : slot
          ? taskOffices[(Number(slot[1]) - 1) % taskOffices.length]
          : "属官";
      const office = account.office && !internalOffice.test(account.office)
        ? account.office
        : existing?.office && !internalOffice.test(existing.office)
          ? existing.office
          : mappedOffice;
      return normalizeMember({
        ...existing,
        id: account.heroId,
        name: existing?.name || (nameForId ? nameForId(account.heroId) : account.heroId),
        office,
        merit: account.lifetimeEarned
      }, index);
    });
    state.contribution = growth;
    if (String(organization.name || "").trim()) state.name = String(organization.name).trim();
    state.remoteRoster = {
      organization: {
        name: String(organization.name || ""), state: String(organization.state || ""),
        hierarchyVersion: Number.isSafeInteger(organization.hierarchyVersion) ? organization.hierarchyVersion : 0,
        growthContribution: growth
      },
      members: normalized,
      playerMembership: snapshot?.playerMembership && typeof snapshot.playerMembership === "object" ? copy(snapshot.playerMembership) : null,
      openPositions: Array.isArray(snapshot?.openPositions) ? snapshot.openPositions.filter((entry) => entry && typeof entry === "object").slice(0, 12).map(copy) : [],
      observedAt: new Date().toISOString()
    };
    return state;
  }

  return { SCHEMA_VERSION, TASK_TYPES, defaultState, normalizeState, syncMembers, recordThought, recordLogisticsBriefing, recordCommendation, recordRecollection, recordCouncil, recordMandate, recordLobbying, createAlliance, breakAlliance, recordBattleOutcome, createTask, advanceMonth, remoteTaskReadyForAdvance, reconcileRemoteTasks, recordTaskReview, recordInventoryRequisition, consumeSupport, recordKnowledge, selectEvidence, selectCorrespondence, updateBackend, recordRemoteRoster, hash };
});
