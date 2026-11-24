(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.DongzhouIntegration = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  const SESSION_KEY = "dongzhou-integration-session-v1";
  const INSTALLATION_KEY = "dongzhou-installation-id-v1";
  const ORDER_JOURNAL_KEY = "dongzhou-order-journal-v1";
  const KNOWLEDGE_CODEX_KEY = "dongzhou-knowledge-codex-v1";
  const MANDATE_PENDING_PREFIX = "dongzhou-pending-mandate-v1:";
  const MANDATE_REVISION_KEY = "dongzhou-mandate-revision-v1";
  const NPC_MESSAGE_PENDING_PREFIX = "dongzhou-pending-npc-message-v1:";
  const NPC_THOUGHT_PENDING_PREFIX = "dongzhou-pending-npc-thought-v1:";
  const MANDATE_SCHEDULE_PENDING_PREFIX = "dongzhou-pending-mandate-schedule-v1:";
  const INVENTORY_REQUISITION_PENDING_KEY = "dongzhou-pending-inventory-requisition-v1";
  const SCHEDULED_DUTY_STATUS_PENDING_KEY = "dongzhou-pending-scheduled-duty-status-v1";
  const LOGISTICS_BRIEFING_PENDING_PREFIX = "dongzhou-pending-logistics-briefing-v1:";
  const ADVISER_QUESTION_KEY = "dongzhou-adviser-question-v1";
  const KNOWLEDGE_QUIZ_PREFIX = "dongzhou-local-knowledge-quiz-v1:";
  const BATTLE_READINESS_PREFIX = "dongzhou-local-battle-readiness-v1:";
  const BATTLE_DEPLOYMENT_PREFIX = "dongzhou-local-battle-deployment-v1:";
  const BATTLE_DEBRIEF_PREFIX = "dongzhou-local-battle-debrief-v1:";
  const NPC_COMMENDATION_PREFIX = "dongzhou-local-npc-commendation-v1:";
  const NPC_RECOLLECTION_PREFIX = "dongzhou-local-npc-recollection-v1:";
  const NPC_DECISION_PREFIX = "dongzhou-local-npc-decision-v1:";
  const LOCAL_LOGISTICS_BRIEFING_PREFIX = "dongzhou-local-logistics-briefing-v1:";
  const LOCAL_SCHEDULED_DUTY_STATUS_PREFIX = "dongzhou-local-scheduled-duty-status-v1:";
  const offline = new URLSearchParams(root.location?.search || "").get("offline") === "1";
  let session = read(SESSION_KEY, null);
  let sessionPromise = null;
  let saveVersion = 1;
  let persistChain = Promise.resolve();
  let saveBlocked = false;
  let offlineProfile = null;
  let localServiceProvenancePromise = null;
  const TRANSIENT_STATUSES = new Set([502, 503, 504]);

  function read(key, fallback) {
    try { return JSON.parse(root.localStorage.getItem(key)) || fallback; } catch (_) { return fallback; }
  }

  function write(key, value) {
    root.localStorage.setItem(key, JSON.stringify(value));
  }

  function canonicalJson(value) {
    if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
    if (value && typeof value === "object") {
      return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
    }
    return JSON.stringify(value);
  }

  async function sha256(value) {
    const bytes = new root.TextEncoder().encode(String(value));
    const digest = await root.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
  }

  function uuidFromDigest(digest) {
    const chars = digest.slice(0, 32).split("");
    chars[12] = "5";
    chars[16] = ((parseInt(chars[16], 16) & 3) | 8).toString(16);
    const value = chars.join("");
    return `${value.slice(0, 8)}-${value.slice(8, 12)}-${value.slice(12, 16)}-${value.slice(16, 20)}-${value.slice(20)}`;
  }

  async function localServiceProvenance() {
    if (!localServiceProvenancePromise) {
      localServiceProvenancePromise = root.fetch("scenario/service-sources.json", { cache: "no-store" })
        .then((response) => {
          if (!response.ok) throw new Error("local_service_sources_unavailable");
          return response.json();
        })
        .then(async (payload) => {
          const services = payload?.services;
          const names = Object.keys(services || {}).sort();
          if (payload?.schemaVersion !== 1 || names.join(",") !== "aiNpc,knowledge,nexusKernel,orgFlow") {
            throw new Error("local_service_sources_invalid");
          }
          for (const source of Object.values(services)) {
            if (!source || !/^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$/.test(source.sourceBranch)
              || !/^[0-9a-f]{40}$/.test(source.sourceRevision)
              || !/^[0-9a-f]{40}$/.test(source.integrationRevision)) {
              throw new Error("local_service_sources_invalid");
            }
          }
          const trace = { schemaVersion: 1, services };
          return {
            ...trace,
            digest: await sha256(canonicalJson(trace)),
            kernel: {
              module: "dongzhou_service_provenance",
              moduleVersion: "1.0.0",
              nexusKernelVersion: "0.2.0",
              state: "SEALED"
            }
          };
        });
    }
    return JSON.parse(JSON.stringify(await localServiceProvenancePromise));
  }

  async function localKnowledgeCatalog() {
    const response = await root.fetch("scenario/dongzhou-knowledge.json", { cache: "no-store" });
    if (!response.ok) throw new Error("knowledge_quiz_unavailable");
    const payload = await response.json();
    return Array.isArray(payload?.entries) ? payload.entries : [];
  }

  async function localPublishedKnowledge(stageId, knowledgeId) {
    const entry = (await localKnowledgeCatalog()).find((item) => item
      && String(item.stageId || "") === String(stageId)
      && String(item.id || item.aku_id || "") === String(knowledgeId));
    if (!entry || !String(knowledgeId || "").startsWith("dongzhou_stage_")) throw new Error("npc_history_knowledge_invalid");
    return entry;
  }

  function requireLocalOfficer(heroId) {
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const members = Array.isArray(currentProfile?.organization?.members) ? currentProfile.organization.members : [];
    const member = members.find((entry) => String(entry?.id || "") === String(heroId));
    if (!member) throw new Error("npc_not_in_local_organization");
    return member;
  }

  function localKnowledgeSource(entry, input = {}) {
    const sources = Array.isArray(entry?.sourceDetails) ? entry.sourceDetails : Array.isArray(entry?.sources) ? entry.sources : [];
    const index = Number.isInteger(input?.source_index) ? input.source_index : 0;
    const source = sources[index];
    const work = String(source?.work || source?.name || "");
    if (!source || !work || (input?.source_work && String(input.source_work) !== work)) throw new Error("npc_history_source_invalid");
    return work;
  }

  async function buildLocalNpcCommendation(heroId, input) {
    requireLocalOfficer(heroId);
    const knowledge = await localPublishedKnowledge(input?.stage_id, input?.knowledge_id);
    const playerId = await localPlayerId();
    const identity = await sha256(`${playerId}\n${input.stage_id}\n${heroId}\ndongzhou-npc-commendation-v1`);
    const trace = {
      eventId: `npc-commendation:${identity}`,
      playerId,
      heroId: String(heroId),
      npcId: `local:${heroId}`,
      stageId: String(input.stage_id),
      knowledgeId: String(input.knowledge_id),
      knowledgeTitle: String(knowledge.name || knowledge.title || input.knowledge_id),
      sourceWork: localKnowledgeSource(knowledge, input),
      affectionType: "appreciation",
      affectionDelta: 2,
      sourceProvenance: await localServiceProvenance()
    };
    return {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_npc_commendation", moduleVersion: "1.1.0", state: "SEALED" }
    };
  }

  async function localCommendNpc(heroId, input) {
    const key = `${NPC_COMMENDATION_PREFIX}${input?.stage_id || ""}:${heroId}`;
    const receipt = await buildLocalNpcCommendation(heroId, input);
    const existing = read(key, null);
    if (existing) {
      if (canonicalJson(existing.input) !== canonicalJson(input)) throw new Error("npc_commendation_conflict");
      if (canonicalJson(existing.commendation) !== canonicalJson(receipt)) throw new Error("npc_commendation_seal_invalid");
      return { state: "COMPLETED", replayed: true, commendation: receipt };
    }
    write(key, { input, commendation: receipt });
    return { state: "COMPLETED", replayed: false, commendation: receipt };
  }

  async function buildLocalNpcRecollection(heroId, input) {
    requireLocalOfficer(heroId);
    const knowledge = await localPublishedKnowledge(input?.stage_id, input?.knowledge_id);
    const playerId = await localPlayerId();
    const stageIndex = Math.max(0, Number(knowledge.index || 0));
    const memoryId = `local-memory:${input.stage_id}:${heroId}:${input.knowledge_id}`;
    const memoryReceipt = {
      idempotencyKey: memoryId,
      sourceType: "dialogue_choice",
      factKind: "event",
      timestamp: new Date(Date.UTC(2000, 0, 1) + stageIndex * 86400000).toISOString(),
      content: `${heroId}据${localKnowledgeSource(knowledge, input)}忆起：${String(knowledge.summary || knowledge.objective || knowledge.name || input.knowledge_id).slice(0, 800)}`
    };
    memoryReceipt.digest = await sha256(canonicalJson(memoryReceipt));
    const identity = await sha256(`${playerId}\n${input.stage_id}\n${heroId}\n${input.knowledge_id}\n${memoryReceipt.digest}\ndongzhou-npc-recollection-v1`);
    const trace = {
      recollectionId: `npc-recollection:${identity}`,
      playerId,
      heroId: String(heroId),
      npcId: `local:${heroId}`,
      stageId: String(input.stage_id),
      knowledgeId: String(input.knowledge_id),
      knowledgeTitle: String(knowledge.name || knowledge.title || input.knowledge_id),
      sourceWork: localKnowledgeSource(knowledge, input),
      memoryId,
      memoryType: memoryReceipt.sourceType,
      memoryTimestamp: memoryReceipt.timestamp,
      memoryContent: memoryReceipt.content,
      memoryDigest: memoryReceipt.digest,
      memoryReceipt,
      matchMode: "knowledge_dialogue",
      sourceProvenance: await localServiceProvenance()
    };
    return {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_npc_recollection", moduleVersion: "1.2.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
  }

  async function localRecallNpc(heroId, input) {
    const key = `${NPC_RECOLLECTION_PREFIX}${input?.stage_id || ""}:${heroId}:${input?.knowledge_id || ""}`;
    const receipt = await buildLocalNpcRecollection(heroId, input);
    const existing = read(key, null);
    if (existing) {
      if (canonicalJson(existing.recollection) !== canonicalJson(receipt)) throw new Error("npc_recollection_seal_invalid");
      return { state: "COMPLETED", replayed: true, recollection: receipt };
    }
    write(key, { input, recollection: receipt });
    return { state: "COMPLETED", replayed: false, recollection: receipt };
  }

  const LOCAL_TASK_LABELS = Object.freeze({
    supply: "筹措军粮",
    drill: "整训军阵",
    patrol: "巡察境内",
    intelligence: "刺探敌情",
    diplomacy: "出使游说"
  });

  async function buildLocalNpcThought(heroId, input) {
    requireLocalOfficer(heroId);
    const knowledge = await localPublishedKnowledge(input?.stage_id, input?.knowledge_id);
    const taskName = LOCAL_TASK_LABELS[input?.task_type];
    if (!taskName) throw new Error("npc_thought_task_invalid");
    const sources = Array.isArray(knowledge.sourceDetails) ? knowledge.sourceDetails : knowledge.sources;
    const source = sources?.[Number(input.evidence_source_index)];
    if (!source?.work) throw new Error("npc_thought_evidence_invalid");
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    let logisticsBriefing;
    if (input.logistics_briefing_request_id || input.logistics_briefing_digest) {
      logisticsBriefing = (currentProfile?.organization?.logisticsBriefings || []).find((entry) =>
        entry?.requestId === input.logistics_briefing_request_id && entry?.digest === input.logistics_briefing_digest);
      if (!logisticsBriefing) throw new Error("npc_thought_logistics_invalid");
    }
    const sourceProvenance = await localServiceProvenance();
    const seed = await sha256(canonicalJson({ heroId, input, sourceProvenance: sourceProvenance.digest }));
    const assignment = {
      planId: uuidFromDigest(await sha256(`local-thought-plan:${heroId}:${input.stage_id}:${input.task_type}`)),
      eventId: uuidFromDigest(await sha256(`local-thought-event:${heroId}:${input.stage_id}:${input.task_type}`)),
      name: taskName
    };
    const receipt = {
      requestId: String(input.client_request_id),
      operationId: `dongzhou-local-thought:${await localPlayerId()}:${input.client_request_id}`,
      heroId: String(heroId),
      npcId: `local:${heroId}`,
      stageId: String(input.stage_id),
      taskType: String(input.task_type),
      knowledgeId: String(input.knowledge_id),
      source: {
        index: Number(input.evidence_source_index),
        work: String(source.work),
        tier: String(source.tier || "来源"),
        scope: String(source.scope || ""),
        url: String(source.url || "")
      },
      assignment,
      ...(logisticsBriefing ? { logisticsBriefing: {
        requestId: logisticsBriefing.requestId,
        digest: logisticsBriefing.digest,
        inventoryRevision: logisticsBriefing.inventoryRevision,
        sourceProvenance: logisticsBriefing.sourceProvenance
      } } : {}),
      thought: {
        hasThought: true,
        description: `${heroId}据${source.work}斟酌${taskName}，认为应先依史势定次序再执行。`,
        importance: 65 + (parseInt(seed.slice(0, 4), 16) % 26)
      },
      councilProposal: `依${String(source.work).slice(0, 18)}推进${taskName}`.slice(0, 48),
      sourceProvenance
    };
    receipt.digest = await sha256(canonicalJson(receipt));
    return receipt;
  }

  async function localNpcThought(heroId, input) {
    const context = [heroId, input.stage_id, input.knowledge_id, input.evidence_source_index, input.task_type, input.logistics_briefing_request_id || "", input.logistics_briefing_digest || ""].join(":");
    const key = NPC_THOUGHT_PENDING_PREFIX + context;
    const stored = read(key, null);
    const pending = stored?.input || stored || { ...input, client_request_id: root.crypto.randomUUID() };
    if (stored?.input && canonicalJson(stored.input) !== canonicalJson({ ...input, client_request_id: stored.input.client_request_id })) {
      throw new Error("npc_thought_idempotency_conflict");
    }
    const thoughtReceipt = await buildLocalNpcThought(heroId, pending);
    const result = { state: "COMPLETED", requestId: pending.client_request_id, thoughtReceipt };
    if (stored?.result && canonicalJson(stored.result) !== canonicalJson(result)) throw new Error("npc_thought_seal_invalid");
    write(key, { input: pending, result });
    return { replayed: Boolean(stored?.result), ...result };
  }

  function localNoticeTaskText(member, task, month) {
    if (!task) return `第${month}月，${member.name || member.id}在${member.office || "官署"}当值，当前无在办差事。`;
    const states = { active: "正在办理", success: "已经办成", partial: "部分办成", failed: "未能办成", censured: "复命受申斥" };
    return `第${month}月，${member.name || member.id}${states[task.status] || "已记入"}“${task.name || "官署差事"}”。`;
  }

  async function localOrganizationPublicNotices() {
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const organization = currentProfile?.organization || {};
    const members = Array.isArray(organization.members) ? organization.members : [];
    const tasks = Array.isArray(organization.tasks) ? organization.tasks : [];
    const month = Math.max(1, Math.trunc(Number(organization.month || 1)));
    const sourceProvenance = await localServiceProvenance();
    const notices = [];
    for (const member of members) {
      const memberTasks = tasks.filter((task) => task?.assigneeId === member?.id);
      const task = memberTasks.find((entry) => entry.status === "active") || memberTasks.at(-1) || null;
      const localRound = {
        mode: "standalone",
        month,
        heroId: String(member?.id || ""),
        taskId: String(task?.id || ""),
        taskStatus: String(task?.status || "idle"),
        taskName: String(task?.name || "")
      };
      if (!localRound.heroId) continue;
      const loginRoundDigest = await sha256(canonicalJson(localRound));
      const message = localNoticeTaskText(member, task, month);
      const messageId = `npc-public:${await sha256(canonicalJson({ ...localRound, message }))}`;
      const trace = {
        messageId,
        gameServerId: "standalone",
        npcId: `local:${localRound.heroId}`,
        heroId: localRound.heroId,
        npcName: String(member.name || member.id),
        message,
        loginRoundDigest,
        publishedAt: `第${month}月本地账本`,
        deliveryMode: "IN_PROCESS",
        sourceProvenance
      };
      notices.push({
        ...trace,
        digest: await sha256(canonicalJson(trace)),
        kernel: { module: "dongzhou_npc_public_notice", moduleVersion: "1.1.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
      });
    }
    return { mode: "standalone", notices };
  }

  async function localNpcDecision(heroId, question, options, stageId, memory, publicNotice) {
    requireLocalOfficer(heroId);
    if (!String(question || "").trim() || !Array.isArray(options) || options.length < 2 || options.some((item) => !String(item || "").trim())) {
      throw new Error("npc_decision_input_invalid");
    }
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const matchingThought = [...(currentProfile?.organization?.thoughts || [])].reverse().find((entry) =>
      entry?.heroId === heroId && entry?.stageId === String(stageId) && entry?.thought?.hasThought === true
      && options.includes(entry.councilProposal));
    const sourceProvenance = await localServiceProvenance();
    if (memory && (!/^[0-9a-f]{64}$/.test(String(memory.digest || ""))
      || canonicalJson(memory.sourceProvenance) !== canonicalJson(sourceProvenance))) throw new Error("npc_decision_memory_invalid");
    let verifiedPublicNotice;
    if (publicNotice) {
      verifiedPublicNotice = (await localOrganizationPublicNotices()).notices.find((notice) => notice.heroId === heroId
        && notice.messageId === publicNotice.messageId && notice.digest === publicNotice.digest);
      if (!verifiedPublicNotice || canonicalJson(verifiedPublicNotice.sourceProvenance) !== canonicalJson(sourceProvenance)) {
        throw new Error("npc_decision_public_notice_invalid");
      }
      if (!String(question).includes(`告示印记：${verifiedPublicNotice.digest.slice(0, 12)}`)) throw new Error("npc_decision_public_notice_unbound");
    }
    const context = canonicalJson({ heroId, stageId: String(stageId), question, options, memoryId: memory?.idempotencyKey || "", publicNoticeId: verifiedPublicNotice?.messageId || "" });
    const key = NPC_DECISION_PREFIX + await sha256(context);
    const stored = read(key, null);
    const clientRequestId = stored?.input?.clientRequestId || root.crypto.randomUUID();
    const seed = await sha256(`${context}:${clientRequestId}`);
    const thoughtIndex = matchingThought ? options.indexOf(matchingThought.councilProposal) : -1;
    const index = thoughtIndex >= 0 ? thoughtIndex : parseInt(seed.slice(0, 8), 16) % options.length;
    const dialogueTrace = { clientRequestId, heroId: String(heroId), stageId: String(stageId), question, options, index, sourceProvenance };
    const result = {
      state: "COMPLETED",
      decision: { data: { type: "OPTION", index, text: options[index] } },
      dialogueReceipt: {
        state: "RECORDED",
        sourceRecordId: `dongzhou-council:${clientRequestId}`,
        digest: await sha256(canonicalJson(dialogueTrace))
      },
      ...(memory ? { memoryReceipt: memory } : {}),
      ...(verifiedPublicNotice ? { publicNoticeReceipt: verifiedPublicNotice } : {}),
      sourceProvenance,
      clientRequestId
    };
    if (stored?.result && canonicalJson(stored.result) !== canonicalJson(result)) throw new Error("npc_decision_seal_invalid");
    write(key, { input: { clientRequestId, context }, result });
    return { replayed: Boolean(stored?.result), ...result };
  }

  function localInventorySnapshot() {
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const inventory = currentProfile?.organization?.localInventory;
    const accounts = Array.isArray(inventory?.accounts) ? inventory.accounts.map((account) => ({
      resourceKey: String(account?.resourceKey || ""),
      balance: Number(account?.balance),
      version: Number(account?.version)
    })) : [];
    if (!Number.isSafeInteger(inventory?.revision) || inventory.revision < 1
      || !accounts.length
      || accounts.some((account) => !account.resourceKey || !Number.isSafeInteger(account.balance)
        || account.balance < 0 || !Number.isSafeInteger(account.version) || account.version < 1)) {
      throw new Error("local_inventory_invalid");
    }
    return { revision: inventory.revision, accounts };
  }

  async function buildLocalLogisticsBriefing(heroId, input) {
    requireLocalOfficer(heroId);
    const knowledge = (await localKnowledgeCatalog()).find((entry) => entry
      && String(entry.stageId || "") === String(input?.stage_id || "")
      && String(entry.id || entry.aku_id || "").startsWith("dongzhou_stage_"));
    if (!knowledge) throw new Error("organization_logistics_knowledge_unavailable");
    const inventory = localInventorySnapshot();
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const provisions = Math.max(0, Math.min(999999, Math.trunc(Number(currentProfile?.campaignResources?.provisions || 0))));
    const morale = Math.max(0, Math.min(999999, Math.trunc(Number(currentProfile?.campaignResources?.morale || 0))));
    const taskUnits = inventory.accounts.find((account) => account.resourceKey === "task.execution")?.balance || 0;
    const trace = {
      state: "SEALED",
      requestId: String(input.client_request_id),
      heroId: String(heroId),
      npcId: `local:${heroId}`,
      stageId: String(input.stage_id),
      stageTitle: String(input.stage_title || knowledge.name || knowledge.title || input.stage_id),
      knowledge: {
        id: String(knowledge.id || knowledge.aku_id),
        title: String(knowledge.name || knowledge.title || knowledge.id || knowledge.aku_id)
      },
      inventoryRevision: inventory.revision,
      accounts: inventory.accounts,
      campaignResources: { provisions, morale },
      exchange: {
        resourceKey: "task.execution",
        priceUnits: 20,
        provisionsPerLot: 12,
        availableUnits: taskUnits,
        availableLots: Math.floor(taskUnits / 20)
      },
      ainpcDelivery: { market: "DELIVERED", warehouse: "DELIVERED", mode: "IN_PROCESS" },
      sourceProvenance: await localServiceProvenance()
    };
    return {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_logistics_briefing", moduleVersion: "1.1.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
  }

  async function localOrganizationLogisticsBriefing(heroId, input) {
    const inventory = localInventorySnapshot();
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const context = [heroId, input?.stage_id || "", inventory.revision,
      Number(currentProfile?.campaignResources?.provisions || 0), Number(currentProfile?.campaignResources?.morale || 0)].join(":");
    const key = LOCAL_LOGISTICS_BRIEFING_PREFIX + context;
    const stored = read(key, null);
    const pending = stored?.input || { ...input, client_request_id: root.crypto.randomUUID() };
    if (stored?.input && (stored.input.stage_id !== input.stage_id || stored.input.stage_title !== input.stage_title)) {
      throw new Error("organization_logistics_briefing_conflict");
    }
    const briefingReceipt = await buildLocalLogisticsBriefing(heroId, pending);
    const result = { state: "COMPLETED", requestId: pending.client_request_id, briefingReceipt };
    if (stored?.result && canonicalJson(stored.result) !== canonicalJson(result)) throw new Error("organization_logistics_briefing_seal_invalid");
    write(key, { input: pending, result });
    return { replayed: Boolean(stored?.result), ...result };
  }

  function localInventoryRequisitionError(code, message) {
    const error = new Error(message || code);
    error.code = code;
    return error;
  }

  async function localInventoryRequisitionDraft(input) {
    const units = Number(input?.units);
    const stageId = String(input?.stage_id || "");
    const requestId = String(input?.client_request_id || "");
    if (!requestId || !stageId || !Number.isSafeInteger(units) || units < 20 || units > 100 || units % 20) {
      throw localInventoryRequisitionError("organization_inventory_requisition_invalid");
    }
    const sourceProvenance = await localServiceProvenance();
    const playerId = await localPlayerId();
    const trace = {
      id: `dongzhou:requisition:${playerId}:${requestId}`,
      requestId,
      stageId,
      resourceKey: "task.execution",
      units,
      effect: { provisions: units * 3 / 5 },
      sourceProvenance,
      kernel: { module: "dongzhou_mandate_workflow", moduleVersion: "1.14.0", nexusKernelVersion: "0.2.0", state: "REQUIRES_ACTION" }
    };
    const digest = await sha256(canonicalJson(trace));
    return {
      state: "REQUIRES_ACTION",
      requestId,
      stageId,
      requisition: { ...trace, digest, state: "DRAFT" },
      action: {
        actionId: uuidFromDigest(await sha256(`dongzhou-inventory-requisition-action:${digest}`)),
        code: "approve_inventory_requisition",
        type: "confirmation",
        prompt: "Approve this public inventory requisition?",
        options: ["APPROVE", "REJECT"]
      },
      sourceProvenance
    };
  }

  async function validateLocalInventoryRequisitionDraft(result) {
    const requisition = result?.requisition;
    const sourceProvenance = await localServiceProvenance();
    if (!requisition || result.state !== "REQUIRES_ACTION" || requisition.state !== "DRAFT"
      || requisition.kernel?.module !== "dongzhou_mandate_workflow"
      || requisition.kernel?.moduleVersion !== "1.14.0"
      || requisition.kernel?.state !== "REQUIRES_ACTION"
      || canonicalJson(requisition.sourceProvenance) !== canonicalJson(sourceProvenance)
      || canonicalJson(result.sourceProvenance) !== canonicalJson(sourceProvenance)) {
      throw localInventoryRequisitionError("organization_inventory_requisition_seal_invalid");
    }
    const { digest, state, ...trace } = requisition;
    if (state !== "DRAFT" || digest !== await sha256(canonicalJson(trace))) {
      throw localInventoryRequisitionError("organization_inventory_requisition_seal_invalid");
    }
    return requisition;
  }

  async function localResumeOrganizationInventoryRequisition(requisitionId, actionId, decision) {
    const journal = pendingOrganizationInventoryRequisition();
    if (!journal?.input || journal.result?.requisition?.id !== requisitionId) {
      throw localInventoryRequisitionError("organization_inventory_requisition_journal_mismatch");
    }
    if (["COMPLETED", "REJECTED"].includes(journal.result?.state)) return { replayed: true, ...journal.result };
    const requisition = await validateLocalInventoryRequisitionDraft(journal.result);
    if (journal.result.action?.actionId !== actionId || !["APPROVE", "REJECT"].includes(decision)) {
      throw localInventoryRequisitionError("organization_inventory_requisition_action_mismatch");
    }
    const pending = { ...journal, decision };
    write(INVENTORY_REQUISITION_PENDING_KEY, pending);
    if (decision === "REJECT") {
      const result = {
        state: "REJECTED",
        requestId: requisition.requestId,
        stageId: requisition.stageId,
        sourceProvenance: requisition.sourceProvenance,
        requisition: { ...requisition, state: "REJECTED", kernel: { ...requisition.kernel, state: "REJECTED" } }
      };
      write(INVENTORY_REQUISITION_PENDING_KEY, { ...pending, result });
      return result;
    }
    const inventory = localInventorySnapshot();
    const account = inventory.accounts.find((entry) => entry.resourceKey === requisition.resourceKey);
    if (!account || account.balance < requisition.units) {
      throw localInventoryRequisitionError("organization_inventory_insufficient", "The local public inventory does not have enough task credit.");
    }
    const result = {
      state: "COMPLETED",
      requestId: requisition.requestId,
      stageId: requisition.stageId,
      sourceProvenance: requisition.sourceProvenance,
      requisition: { ...requisition, state: "COMPLETED", kernel: { ...requisition.kernel, state: "COMPLETED" } },
      inventoryDebit: {
        entryId: uuidFromDigest(await sha256(`dongzhou-local-inventory-debit:${requisition.requestId}`)),
        resourceKey: requisition.resourceKey,
        delta: -requisition.units,
        balanceAfter: account.balance - requisition.units,
        accountVersion: account.version + 1,
        inventoryRevision: inventory.revision + 1,
        mode: "IN_PROCESS"
      },
      effect: { ...requisition.effect }
    };
    write(INVENTORY_REQUISITION_PENDING_KEY, { ...pending, result });
    return result;
  }

  async function localScheduledDutyIdentity() {
    const playerId = await localPlayerId();
    return {
      organizationId: uuidFromDigest(await sha256(`dongzhou-local-organization:${playerId}`)),
      ruleId: uuidFromDigest(await sha256(`dongzhou-local-scheduled-duty:${playerId}`))
    };
  }

  function currentLocalScheduledDutyState() {
    const currentProfile = read("dongzhou-h5-profile-v2", offlineProfile) || offlineProfile;
    const value = currentProfile?.organization?.localScheduledDuty;
    return {
      state: ["ACTIVE", "DISABLED"].includes(value?.state) ? value.state : "DISABLED",
      version: Number.isSafeInteger(value?.version) && value.version > 0 ? value.version : 1,
      month: Math.max(1, Math.trunc(Number(currentProfile?.organization?.month || 1))),
      tasks: Array.isArray(currentProfile?.organization?.tasks) ? currentProfile.organization.tasks : [],
      members: Array.isArray(currentProfile?.organization?.members) ? currentProfile.organization.members : []
    };
  }

  async function buildLocalScheduledDutySnapshot() {
    const identity = await localScheduledDutyIdentity();
    const local = currentLocalScheduledDutyState();
    const sourceProvenance = await localServiceProvenance();
    const workerAvailable = local.members.some((member) => member?.id === "ZuoRu");
    let task = local.tasks.find((entry) => entry?.status === "active"
      && entry?.scheduledDuty?.ruleId === identity.ruleId
      && entry?.scheduledDuty?.mode === "IN_PROCESS") || null;
    let taskId = String(task?.remoteResult || "");
    if (!taskId && local.state === "ACTIVE" && workerAvailable) {
      taskId = uuidFromDigest(await sha256(`dongzhou-local-scheduled-duty-task:${identity.ruleId}:${local.month}`));
    }
    const activeTask = taskId ? {
      taskId,
      title: "东周朝廷月例察访",
      state: task ? "IN_PROGRESS" : "GENERATED",
      finalResult: null,
      updatedAt: "",
      adopted: true,
      local: true
    } : null;
    const latestTrigger = taskId ? { state: "DISPATCHED", failure_code: null, task_id: taskId } : null;
    const trace = {
      kind: "SNAPSHOT",
      ruleId: identity.ruleId,
      organizationId: identity.organizationId,
      gameServerId: "standalone",
      state: local.state,
      version: local.version,
      frequency: "DAILY",
      triggerMinute: 780,
      managerHeroId: "DuBo",
      workerHeroId: "ZuoRu",
      taskCode: "dongzhou.intelligence",
      latestTriggerState: latestTrigger?.state || null,
      latestTriggerTaskId: taskId || null,
      activeTaskId: taskId || null,
      activeTaskState: activeTask?.state || null,
      activeTaskAdopted: Boolean(activeTask?.adopted),
      sourceProvenance
    };
    const receipt = {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_organization_scheduled_duty", moduleVersion: "1.2.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
    return {
      ruleId: identity.ruleId,
      state: local.state,
      version: local.version,
      frequency: "DAILY",
      triggerMinute: 780,
      managerHeroId: "DuBo",
      workerHeroId: "ZuoRu",
      taskCode: "dongzhou.intelligence",
      dutyTitle: "东周朝廷月例察访",
      latestTrigger,
      activeTask,
      sourceProvenance,
      receipt
    };
  }

  async function localSetOrganizationScheduledDutyEnabled(pending) {
    const snapshot = await buildLocalScheduledDutySnapshot();
    const desiredState = pending.enabled ? "ACTIVE" : "DISABLED";
    const resultingVersion = snapshot.state === desiredState ? snapshot.version : snapshot.version + 1;
    const identity = await localScheduledDutyIdentity();
    const trace = {
      kind: "STATUS_CHANGE",
      playerRequestId: String(pending.client_request_id),
      ruleId: identity.ruleId,
      organizationId: identity.organizationId,
      previousState: snapshot.state,
      resultingState: desiredState,
      desiredState,
      previousVersion: snapshot.version,
      resultingVersion,
      managerHeroId: "DuBo",
      workerHeroId: "ZuoRu",
      taskCode: "dongzhou.intelligence",
      activeTaskId: snapshot.activeTask?.taskId || null,
      sourceProvenance: snapshot.sourceProvenance
    };
    const receipt = {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_organization_scheduled_duty", moduleVersion: "1.2.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
    const result = {
      state: desiredState,
      version: resultingVersion,
      activeTask: snapshot.activeTask,
      sourceProvenance: snapshot.sourceProvenance,
      receipt
    };
    const key = LOCAL_SCHEDULED_DUTY_STATUS_PREFIX + pending.client_request_id;
    const stored = read(key, null);
    if (stored && canonicalJson(stored) !== canonicalJson({ input: pending, result })) {
      throw new Error("organization_scheduled_duty_status_seal_invalid");
    }
    write(key, { input: pending, result });
    return { replayed: Boolean(stored), ...result };
  }

  async function buildLocalKnowledgeQuiz(questionId, stageId, deadlineAt) {
    const entries = await localKnowledgeCatalog();
    const published = entries.find((entry) => entry && String(entry.stageId || "") === String(stageId));
    if (!published) throw new Error("knowledge_quiz_unavailable");
    const rawPeople = Array.isArray(published.people)
      ? published.people
      : Array.isArray(published.entities?.npcs) ? published.entities.npcs : [];
    const currentPeople = [...new Set(rawPeople.map((item) => String(item?.name || item || "").trim()).filter(Boolean))];
    const distractors = [...new Set(entries
      .filter((entry) => entry && String(entry.stageId || "") !== String(stageId))
      .flatMap((entry) => Array.isArray(entry.people) ? entry.people : [])
      .map((item) => String(item || "").trim())
      .filter((name) => name && !currentPeople.includes(name)))];
    if (!currentPeople.length || distractors.length < 3) throw new Error("knowledge_quiz_unavailable");
    const seed = await sha256(`${questionId}:${stageId}`);
    const correctName = currentPeople[parseInt(seed.slice(0, 8), 16) % currentPeople.length];
    const rankedDistractors = await Promise.all(distractors.map(async (name) => ({ name, rank: await sha256(`${seed}:distractor:${name}`) })));
    rankedDistractors.sort((left, right) => left.rank.localeCompare(right.rank));
    const rankedOptions = await Promise.all([correctName, ...rankedDistractors.slice(0, 3).map((item) => item.name)]
      .map(async (name) => ({ name, rank: await sha256(`${seed}:option:${name}`) })));
    rankedOptions.sort((left, right) => left.rank.localeCompare(right.rank));
    const options = rankedOptions.map((item) => item.name);
    const sourceProvenance = await localServiceProvenance();
    const title = String(published.name || published.title || "本回史录");
    const trace = {
      id: String(questionId),
      stageId: String(stageId),
      knowledgeId: String(published.id || published.aku_id || ""),
      title,
      prompt: `下列哪位人物见于《${title}》的已发布人物录？`,
      options,
      correctIndex: options.indexOf(correctName),
      deadlineAt,
      sourceProvenance
    };
    const questionDigest = await sha256(canonicalJson(trace));
    const actionId = uuidFromDigest(await sha256(`dongzhou-knowledge-quiz:${questionDigest}`));
    const publicQuestion = Object.fromEntries(Object.entries(trace).filter(([key]) => key !== "correctIndex" && key !== "sourceProvenance"));
    const ready = {
      mode: "offline",
      state: "READY",
      question: {
        ...publicQuestion,
        receipt: {
          digest: questionDigest,
          sourceProvenance,
          kernel: {
            module: "dongzhou_knowledge_tournament",
            moduleVersion: "1.1.0",
            nexusKernelVersion: "0.2.0",
            state: "READY"
          }
        }
      },
      action: { actionId, code: "answer_knowledge_quiz", type: "selection" }
    };
    const source = Array.isArray(published.sourceDetails)
      ? published.sourceDetails.find((item) => item && typeof item === "object") || null
      : null;
    return { trace, source, ready };
  }

  function adviserIntent(question) {
    const value = String(question || "").toLocaleLowerCase();
    if (/(?:哪里|在哪|何处|怎么去|如何去|带我|引路|location|where)/u.test(value)) return "location";
    if (/(?:任务|军令|目标|怎么打|如何打|攻略|task|objective)/u.test(value)) return "task";
    if (/(?:物品|道具|装备|item)/u.test(value)) return "item";
    if (/(?:谁|何人|人物|将领|角色|role|who)/u.test(value)) return "role";
    if (/(?:系统|规则|玩法|system)/u.test(value)) return "system";
    return "unknown";
  }

  async function buildLocalAdviserAnswer(input) {
    const questionId = String(input?.client_request_id || "");
    const question = String(input?.question || "").trim();
    const stageId = String(input?.stage_id || "");
    const stageIndex = Number(input?.stage_index);
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(questionId)
      || !question || question.length > 500 || !stageId || !Number.isSafeInteger(stageIndex) || stageIndex < 1) {
      throw new Error("adviser_question_invalid");
    }
    const entries = await localKnowledgeCatalog();
    const knowledge = entries.find((entry) => entry && String(entry.stageId || "") === stageId);
    if (!knowledge) throw new Error("adviser_knowledge_unavailable");
    const people = [...new Set((Array.isArray(knowledge.people) ? knowledge.people : [])
      .map((item) => String(item || "").trim()).filter(Boolean))];
    const matchedPerson = people.find((name) => question.includes(name)) || "";
    const intentType = adviserIntent(question);
    const title = String(knowledge.name || knowledge.title || input.stage_title || stageId);
    const objective = String(knowledge.objective || "").trim();
    const summary = String(knowledge.summary || knowledge.content || "").trim().slice(0, 260);
    const summarySentences = summary.match(/[^。！？]+[。！？]?/gu) || [];
    const summaryLead = String(summarySentences[0] || summary).replace(/[。！？]+$/u, "");
    const boundedSummary = summarySentences.slice(0, 2).join("") || summary;
    let answer;
    if (intentType === "location" && matchedPerson) {
      answer = `${matchedPerson}见于《${title}》；可从当前关卡入口前往核验。`;
    } else if (intentType === "task") {
      answer = objective ? `本关军令：${objective}。${summaryLead}。` : boundedSummary;
    } else if (intentType === "role") {
      answer = people.length ? `本回相关人物有${people.slice(0, 6).join("、")}。${summaryLead}。` : boundedSummary;
    } else if (intentType === "item") {
      answer = "本回已发布史料没有可核验的物品来源，请改问具体人物、战役或军令。";
    } else if (intentType === "system") {
      answer = `当前关卡为《${title}》；军师只依据本地已发布史料答复，不补造未收录规则。`;
    } else {
      answer = boundedSummary || "未能理解你的问题，请补充游戏相关的具体信息（如任务名、道具名、地点）。";
    }
    const sourceProvenance = await localServiceProvenance();
    const guideAvailable = intentType === "location" && Boolean(matchedPerson);
    const guideSessionId = guideAvailable
      ? uuidFromDigest(await sha256(`dongzhou-local-adviser-guide:${questionId}:${stageId}:${matchedPerson}`))
      : null;
    const trace = {
      questionId,
      taskId: questionId,
      chatId: `dongzhou-local-adviser-${questionId}`,
      question,
      stageId,
      stageIndex,
      stageTitle: String(input.stage_title || title),
      knowledgeId: String(knowledge.id || knowledge.aku_id || ""),
      adviser: { heroId: "DuBo", name: "杜伯", organization: "列国军府", office: "军府主官" },
      answer,
      intentType,
      guide: guideAvailable ? {
        available: true,
        sessionId: guideSessionId,
        status: "AVAILABLE",
        started: false,
        promptText: `由杜伯引至${matchedPerson}所在的当前关卡入口`,
        target: { mapId: 900000 + stageIndex, mapName: String(input.stage_title || title), name: matchedPerson, description: title }
      } : { available: false, sessionId: null, status: "UNAVAILABLE", started: false },
      sourceProvenance
    };
    const answerDigest = await sha256(canonicalJson(trace));
    return {
      trace,
      result: {
        mode: "offline",
        state: "ANSWERED",
        questionId,
        taskId: questionId,
        chatId: trace.chatId,
        answer,
        intentType,
        guide: trace.guide,
        knowledgeId: trace.knowledgeId,
        adviser: trace.adviser,
        sourceProvenance,
        answerDigest
      }
    };
  }

  async function validatedLocalAdviserJournal(questionId) {
    const journal = pendingAdviserQuestion();
    if (!journal || String(journal.input?.client_request_id || "") !== String(questionId)) {
      throw new Error("adviser_question_not_found");
    }
    const rebuilt = await buildLocalAdviserAnswer(journal.input);
    if (canonicalJson(journal.result) !== canonicalJson(rebuilt.result)) {
      throw new Error("adviser_answer_source_invalid");
    }
    return { journal, rebuilt };
  }

  async function localPlayerId() {
    return uuidFromDigest(await sha256(`dongzhou-local-player:${installationId()}`));
  }

  async function sealLocalAdviserGuide(answer, actionId, decision, state, eventType, fields = {}) {
    const trace = {
      actionId: String(actionId),
      questionId: answer.questionId,
      taskId: answer.taskId,
      playerId: await localPlayerId(),
      chatId: answer.chatId,
      guideSessionId: String(answer.guide?.sessionId || ""),
      decision,
      state,
      eventType,
      guideStarted: state === "RUNNING" || state === "COMPLETED",
      message: String(fields.message || ""),
      reason: String(fields.reason || ""),
      sourceProvenance: answer.sourceProvenance
    };
    return {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: {
        module: "dongzhou_adviser_guide",
        moduleVersion: "1.1.0",
        nexusKernelVersion: "0.2.0",
        state: "SEALED"
      }
    };
  }

  async function validateLocalAdviserGuide(answer, receipt) {
    if (!receipt || receipt.questionId !== answer.questionId || receipt.taskId !== answer.taskId
      || receipt.chatId !== answer.chatId || receipt.guideSessionId !== answer.guide?.sessionId
      || !["ACCEPT", "REJECT"].includes(receipt.decision)
      || !["ACCEPTED", "RUNNING", "COMPLETED", "FAILED", "REJECTED", "CANCELLED"].includes(receipt.state)) {
      throw new Error("adviser_guide_seal_invalid");
    }
    const expected = await sealLocalAdviserGuide(
      answer, receipt.actionId, receipt.decision, receipt.state, receipt.eventType,
      { message: receipt.message, reason: receipt.reason }
    );
    if (canonicalJson(receipt) !== canonicalJson(expected)) throw new Error("adviser_guide_seal_invalid");
    return expected;
  }

  async function localKnowledgeWitness(stageId) {
    const published = (await localKnowledgeCatalog())
      .filter((entry) => entry && String(entry.stageId || "") === String(stageId)
        && String(entry.id || entry.aku_id || "").startsWith("dongzhou_stage_"))
      .sort((left, right) => String(left.id || left.aku_id).localeCompare(String(right.id || right.aku_id)));
    if (!published.length) throw new Error("battle_readiness_knowledge_missing");
    return {
      stageId: String(stageId),
      knowledgeIds: published.map((entry) => String(entry.id || entry.aku_id)),
      digest: await sha256(canonicalJson({ stageId: String(stageId), entries: published }))
    };
  }

  function normalizeLocalBattlePlan(plan) {
    const supportIds = Array.isArray(plan?.supportIds) ? plan.supportIds.map(String) : [];
    const supportEffect = plan?.supportEffect;
    const effects = ["provisions", "morale", "attack", "defense", "recon"];
    if (!plan || !["balanced", "assault", "bulwark", "maneuver"].includes(plan.formation)
      || (plan.vanguardHeroId !== null && !/^[A-Za-z0-9_.:-]{1,128}$/.test(String(plan.vanguardHeroId || "")))
      || supportIds.join("\0") !== [...new Set(supportIds)].sort().join("\0")
      || !supportEffect || Object.keys(supportEffect).sort().join(",") !== effects.slice().sort().join(",")
      || effects.some((key) => typeof supportEffect[key] !== "number" || !Number.isFinite(supportEffect[key]))) {
      throw new Error("battle_deployment_plan_invalid");
    }
    return {
      formation: plan.formation,
      vanguardHeroId: plan.vanguardHeroId === null ? null : String(plan.vanguardHeroId),
      supportIds,
      supportEffect: Object.fromEntries(effects.map((key) => [key, Number(supportEffect[key])]))
    };
  }

  function localActiveHeroIds(plan) {
    const members = Array.isArray(offlineProfile?.organization?.members) ? offlineProfile.organization.members : [];
    const ids = members.map((member) => String(member?.id || "").trim()).filter(Boolean);
    if (!ids.length && plan.vanguardHeroId) ids.push(String(plan.vanguardHeroId));
    return [...new Set(ids)].sort();
  }

  async function sealLocalBattleReadiness(stageId, battlePlan) {
    const plan = normalizeLocalBattlePlan(battlePlan);
    const knowledge = await localKnowledgeWitness(stageId);
    const sourceProvenance = await localServiceProvenance();
    const activeHeroIds = localActiveHeroIds(plan);
    if (!activeHeroIds.length) throw new Error("battle_readiness_roster_missing");
    const organizationId = String(offlineProfile?.organization?.remoteId || "dongzhou-local-court");
    const hierarchyVersion = Math.max(1, Number(offlineProfile?.organization?.remoteRoster?.organization?.hierarchyVersion || 1));
    const readinessId = root.crypto.randomUUID();
    const playerId = await localPlayerId();
    const trace = {
      mode: "standalone",
      state: "READY",
      kind: "BATTLE_READINESS",
      readinessId,
      playerDigest: await sha256(canonicalJson({ playerId })),
      stageId: String(stageId),
      stageTitle: String((await localKnowledgeCatalog()).find((entry) => String(entry?.stageId || "") === String(stageId))?.name || stageId),
      knowledge,
      organization: {
        organizationId,
        state: "ACTIVE",
        hierarchyVersion,
        activeHeroIds,
        rosterDigest: await sha256(canonicalJson({ organizationId, hierarchyVersion, activeHeroIds }))
      },
      aiNpc: {
        readyHeroIds: activeHeroIds,
        actorDigest: await sha256(canonicalJson({ readyHeroIds: activeHeroIds }))
      },
      sourceProvenance
    };
    const receipt = {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_battle_readiness", moduleVersion: "1.3.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
    write(BATTLE_READINESS_PREFIX + readinessId, { receipt, battlePlan: plan });
    return receipt;
  }

  async function validateLocalBattleReadiness(stageId, receipt, battlePlan, requireCurrentRoster = true) {
    const plan = normalizeLocalBattlePlan(battlePlan);
    const record = read(BATTLE_READINESS_PREFIX + String(receipt?.readinessId || ""), null);
    const trace = receipt && Object.fromEntries(Object.entries(receipt).filter(([key]) => !["digest", "kernel"].includes(key)));
    const sourceProvenance = await localServiceProvenance();
    const knowledge = await localKnowledgeWitness(stageId);
    const activeHeroIds = localActiveHeroIds(plan);
    if (!record || canonicalJson(record.receipt) !== canonicalJson(receipt)) throw new Error("battle_readiness_journal_invalid");
    if (canonicalJson(record.battlePlan) !== canonicalJson(plan)) throw new Error("battle_readiness_plan_invalid");
    if (receipt?.mode !== "standalone" || receipt?.state !== "READY" || receipt?.kind !== "BATTLE_READINESS"
      || receipt?.stageId !== String(stageId)) throw new Error("battle_readiness_identity_invalid");
    if (receipt?.playerDigest !== await sha256(canonicalJson({ playerId: await localPlayerId() }))) throw new Error("battle_readiness_player_invalid");
    if (canonicalJson(receipt?.knowledge) !== canonicalJson(knowledge)) throw new Error("battle_readiness_knowledge_invalid");
    const sealedHeroIds = receipt?.organization?.activeHeroIds;
    if (!Array.isArray(sealedHeroIds) || !sealedHeroIds.length
      || canonicalJson(receipt?.aiNpc?.readyHeroIds) !== canonicalJson(sealedHeroIds)) throw new Error("battle_readiness_actors_invalid");
    if (receipt?.organization?.rosterDigest !== await sha256(canonicalJson({
      organizationId: receipt.organization.organizationId,
      hierarchyVersion: receipt.organization.hierarchyVersion,
      activeHeroIds: sealedHeroIds
    }))) throw new Error("battle_readiness_roster_digest_invalid");
    if (requireCurrentRoster && canonicalJson(sealedHeroIds) !== canonicalJson(activeHeroIds)) throw new Error("battle_readiness_roster_invalid");
    if (canonicalJson(receipt?.sourceProvenance) !== canonicalJson(sourceProvenance)) throw new Error("battle_readiness_source_invalid");
    if (receipt?.digest !== await sha256(canonicalJson(trace))) throw new Error("battle_readiness_digest_invalid");
    if (canonicalJson(receipt?.kernel) !== canonicalJson({ module: "dongzhou_battle_readiness", moduleVersion: "1.3.0", nexusKernelVersion: "0.2.0", state: "SEALED" })) {
      throw new Error("battle_readiness_kernel_invalid");
    }
    return receipt;
  }

  function standaloneRouteTrace(route) {
    return Object.fromEntries(["mode", "fromStageId", "toStageId", "fromMapId", "toMapId", "method", "routeId", "label", "provisionCost", "moraleDelta", "guideName", "knowledgeWitnesses", "sourceProvenance"]
      .filter((key) => route[key] !== undefined)
      .map((key) => [key, route[key]]));
  }

  async function validateStandaloneRoute(route) {
    if (!route || route.mode !== "standalone" || !route.found || !/^[0-9a-f]{64}$/.test(String(route.localRouteDigest || ""))) {
      throw new Error("campaign_route_seal_invalid");
    }
    const sourceProvenance = await localServiceProvenance();
    if (canonicalJson(route.sourceProvenance) !== canonicalJson(sourceProvenance)
      || route.localRouteDigest !== await sha256(canonicalJson(standaloneRouteTrace(route)))) {
      throw new Error("campaign_route_seal_invalid");
    }
    return route.localRouteDigest;
  }

  async function sealLocalBattleDeployment(stageId, readiness, campaignRoute, battlePlan) {
    const plan = normalizeLocalBattlePlan(battlePlan);
    await validateLocalBattleReadiness(stageId, readiness, plan);
    const routeDigest = campaignRoute ? await validateStandaloneRoute(campaignRoute) : null;
    const sourceProvenance = await localServiceProvenance();
    const deploymentId = root.crypto.randomUUID();
    const trace = {
      mode: "standalone",
      state: "AUTHORIZED",
      kind: "BATTLE_DEPLOYMENT",
      deploymentId,
      reportId: `battle:${stageId}:${deploymentId}`,
      stageId: String(stageId),
      stageTitle: readiness.stageTitle,
      playerDigest: await sha256(canonicalJson({ playerId: await localPlayerId(), purpose: "battle-deployment" })),
      readinessDigest: readiness.digest,
      routeDigest,
      battlePlan: plan,
      sourceProvenance
    };
    const receipt = {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_battle_deployment", moduleVersion: "1.3.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
    write(BATTLE_DEPLOYMENT_PREFIX + deploymentId, { receipt, readinessId: readiness.readinessId, routeDigest, battlePlan: plan });
    return receipt;
  }

  async function verifyBattleDeployment(stageId, readiness, deployment, battlePlan, campaignRoute = null, historical = false) {
    if (!offline) return true;
    const plan = normalizeLocalBattlePlan(battlePlan);
    await validateLocalBattleReadiness(stageId, readiness, plan, !historical);
    const record = read(BATTLE_DEPLOYMENT_PREFIX + String(deployment?.deploymentId || ""), null);
    const trace = deployment && Object.fromEntries(Object.entries(deployment).filter(([key]) => !["digest", "kernel"].includes(key)));
    const routeDigest = campaignRoute ? await validateStandaloneRoute(campaignRoute) : null;
    if (!record || canonicalJson(record.receipt) !== canonicalJson(deployment)
      || deployment?.mode !== "standalone" || deployment?.state !== "AUTHORIZED" || deployment?.kind !== "BATTLE_DEPLOYMENT"
      || deployment?.stageId !== String(stageId) || deployment?.readinessDigest !== readiness.digest
      || deployment?.routeDigest !== routeDigest || canonicalJson(deployment?.battlePlan) !== canonicalJson(plan)
      || deployment?.digest !== await sha256(canonicalJson(trace))
      || canonicalJson(deployment?.sourceProvenance) !== canonicalJson(await localServiceProvenance())
      || canonicalJson(deployment?.kernel) !== canonicalJson({ module: "dongzhou_battle_deployment", moduleVersion: "1.3.0", nexusKernelVersion: "0.2.0", state: "SEALED" })) {
      throw new Error("battle_deployment_seal_invalid");
    }
    return true;
  }

  async function sealLocalBattleDebrief(reportId) {
    const report = (offlineProfile?.organization?.battleReports || []).find((entry) => entry?.id === String(reportId));
    const supportIds = Array.isArray(report?.battlePlan?.supportIds) ? report.battlePlan.supportIds.map(String) : [];
    if (!report || report?.battleDeployment?.kernel?.module !== "dongzhou_battle_deployment"
      || report.battleDeployment.kernel.state !== "SEALED" || !supportIds.length) {
      throw new Error("battle_debrief_report_ineligible");
    }
    await verifyBattleDeployment(
      report.stageId,
      report.battleReadiness,
      report.battleDeployment,
      report.battlePlan,
      report.campaignRoute || null,
      true
    );
    const sourceProvenance = await localServiceProvenance();
    const reportDigest = await sha256(canonicalJson(report));
    const previous = read(BATTLE_DEBRIEF_PREFIX + reportId, null);
    if (previous && previous.reportDigest !== reportDigest) throw new Error("battle_debrief_report_changed");
    const entries = (await localKnowledgeCatalog())
      .filter((entry) => String(entry?.stageId || "") === String(report.stageId)
        && String(entry?.id || entry?.aku_id || "").startsWith("dongzhou_stage_"));
    if (!entries.length) throw new Error("battle_debrief_knowledge_missing");
    const knowledge = await Promise.all(entries.map(async (entry) => ({
      id: String(entry.id || entry.aku_id),
      title: String(entry.name || report.stageTitle || report.stageId),
      summary: String(entry.summary || entry.objective || ""),
      sources: Array.isArray(entry.sources) ? entry.sources : [],
      digest: await sha256(canonicalJson(entry))
    })));
    const heroIds = [...new Set([
      ...(report.battleReadiness?.organization?.activeHeroIds || []),
      report.battlePlan?.vanguardHeroId
    ].filter(Boolean).map(String))].sort();
    if (!heroIds.length) throw new Error("battle_debrief_participants_missing");
    const participants = await Promise.all(heroIds.map(async (heroId) => {
      const memory = {
        content: `${report.stageTitle || report.stageId}${report.won ? "告捷" : "失利"}，${heroId}参与此役，用时${Number(report.turns || 0)}回合。`,
        reportId: String(reportId),
        stageId: String(report.stageId)
      };
      memory.digest = await sha256(canonicalJson(memory));
      return { heroId, npcId: `local:${heroId}`, memory };
    }));
    const organizationTasks = await Promise.all(supportIds.map(async (supportId) => {
      const trace = {
        taskId: supportId,
        state: "COMPLETED",
        timeline: [{ state: "APPLIED", reportId: String(reportId) }],
        sourceProvenance
      };
      return {
        ...trace,
        digest: await sha256(canonicalJson(trace)),
        kernel: { module: "dongzhou_organization_task_trace", moduleVersion: "1.1.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
      };
    }));
    const trace = {
      mode: "standalone",
      state: "SEALED",
      reportId: String(reportId),
      reportDigest,
      battleReceiptDigest: report.battleDeployment.digest,
      stageId: String(report.stageId),
      stageTitle: String(report.stageTitle || report.stageId),
      outcome: {
        won: Boolean(report.won),
        turns: Number(report.turns || 0),
        ownLosses: Number(report.ownLosses || 0),
        terminalReason: String(report.terminalReason || "")
      },
      knowledge,
      participants,
      organizationTasks,
      sourceProvenance,
      battleSourceProvenance: report.battleDeployment.sourceProvenance || sourceProvenance
    };
    const debrief = {
      ...trace,
      digest: await sha256(canonicalJson(trace)),
      kernel: { module: "dongzhou_battle_debrief", moduleVersion: "1.2.0", nexusKernelVersion: "0.2.0", state: "SEALED" }
    };
    write(BATTLE_DEBRIEF_PREFIX + reportId, { reportDigest, debrief });
    return debrief;
  }

  function installationId() {
    let value = root.localStorage.getItem(INSTALLATION_KEY);
    if (!value) {
      value = root.crypto.randomUUID();
      root.localStorage.setItem(INSTALLATION_KEY, value);
    }
    return value;
  }

  async function request(path, options, retriedAfterAuth) {
    if (offline) throw new Error("offline_mode_enabled");
    const headers = { "Content-Type": "application/json", ...(options?.headers || {}) };
    const response = await root.fetch(`api/dongzhou/v1${path}`, { cache: "no-store", credentials: "same-origin", ...options, headers });
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && path !== "/sessions/guest" && !retriedAfterAuth) {
      await ensureSession(true);
      return request(path, options, true);
    }
    if (!response.ok) {
      const error = new Error(body?.error?.message || body?.message || `${response.status}`);
      error.status = response.status;
      error.code = body?.error?.code || body?.code || "request_failed";
      throw error;
    }
    return body?.data || body;
  }

  function wait(ms) {
    return new Promise((resolve) => root.setTimeout(resolve, ms));
  }

  async function requestWithTransientRetry(path, options) {
    const delays = [250, 750];
    for (let attempt = 0; ; attempt += 1) {
      try {
        return await request(path, options);
      } catch (error) {
        const networkFailure = error.status === undefined && error.message !== "offline_mode_enabled";
        if (attempt >= delays.length || (!networkFailure && !TRANSIENT_STATUSES.has(error.status))) throw error;
        await wait(delays[attempt]);
      }
    }
  }

  async function ensureSession(forceRefresh) {
    if (!forceRefresh && session?.playerId) return session;
    if (sessionPromise) return sessionPromise;
    if (forceRefresh) {
      session = null;
      root.localStorage.removeItem(SESSION_KEY);
    }
    sessionPromise = request("/sessions/guest", { method: "POST", body: JSON.stringify({ installation_id: installationId() }) })
      .then((created) => {
        session = created;
        write(SESSION_KEY, session);
        return session;
      })
      .finally(() => { sessionPromise = null; });
    return sessionPromise;
  }

  async function initialize(localProfile) {
    if (offline) {
      offlineProfile = localProfile;
      return { profile: localProfile, connected: false, offline: true };
    }
    await ensureSession();
    try {
      await recoverPendingCourtMandate();
      const remote = await request("/save");
      saveVersion = remote.version;
      if (remote.payload && Object.keys(remote.payload).length) {
        await recoverOrganizationOrders(remote.payload);
        return { profile: remote.payload, connected: true, offline: false };
      }
      const created = await request("/save", { method: "PUT", body: JSON.stringify({ expected_version: saveVersion, payload: localProfile }) });
      saveVersion = created.version;
      await recoverOrganizationOrders(localProfile);
      return { profile: localProfile, connected: true, offline: false };
    } catch (error) { throw error; }
  }

  function mergeServerBattleReceipts(target, source) {
    const targetReports = target?.organization?.battleReports;
    const sourceReports = source?.organization?.battleReports;
    if (!Array.isArray(targetReports) || !Array.isArray(sourceReports)) return false;
    const receipts = new Map(
      sourceReports
        .filter((report) => report?.id && report?.kernelReceipt?.kernel?.state === "SEALED")
        .map((report) => [String(report.id), report.kernelReceipt])
    );
    let changed = false;
    for (const report of targetReports) {
      const receipt = receipts.get(String(report?.id || ""));
      if (!receipt || report.kernelReceipt?.digest === receipt.digest) continue;
      report.kernelReceipt = JSON.parse(JSON.stringify(receipt));
      changed = true;
    }
    return changed;
  }

  function persist(profile) {
    if (offline) {
      offlineProfile = profile;
      return Promise.resolve(null);
    }
    if (!session?.playerId) return Promise.resolve(null);
    if (saveBlocked) return Promise.reject(new Error("save_conflict_reload_required"));
    const snapshot = JSON.parse(JSON.stringify(profile));
    persistChain = persistChain.catch(() => null).then(async () => {
      if (saveBlocked) throw new Error("save_conflict_reload_required");
      let saved;
      try {
        saved = await request("/save", { method: "PUT", body: JSON.stringify({ expected_version: saveVersion, payload: snapshot }) });
      } catch (error) {
        if (error.status === 409) {
          saveBlocked = true;
          if (typeof root.dispatchEvent === "function" && typeof root.CustomEvent === "function") {
            root.dispatchEvent(new root.CustomEvent("dongzhou-save-conflict"));
          }
        }
        throw error;
      }
      saveVersion = saved.version;
      const receiptsChanged = mergeServerBattleReceipts(profile, saved.payload);
      acknowledgeOrganizationOrders(snapshot);
      if (receiptsChanged && typeof root.dispatchEvent === "function" && typeof root.CustomEvent === "function") {
        root.dispatchEvent(new root.CustomEvent("dongzhou-save-committed", {
          detail: { battleReceiptsChanged: true }
        }));
      }
      return saved;
    });
    return persistChain;
  }

  function status() { return request("/integration/status"); }
  function rememberKnowledge(entries) {
    const codex = read(KNOWLEDGE_CODEX_KEY, {});
    for (const raw of entries || []) {
      const entry = raw?.aku || raw?.data || raw;
      const id = String(entry?.id || entry?.aku_id || "").trim();
      if (id) codex[id] = {
        id,
        index: entry.index,
        stageId: entry.stageId,
        name: entry.name,
        title: entry.title,
        summary: entry.summary,
        objective: entry.objective,
        keywords: Array.isArray(entry.keywords) ? entry.keywords : [],
        people: Array.isArray(entry.people) ? entry.people : [],
        entities: Array.isArray(entry.entities?.npcs) ? { npcs: entry.entities.npcs } : undefined,
        sourceDetails: Array.isArray(entry.sourceDetails) ? entry.sourceDetails : [],
        sources: Array.isArray(entry.sources) ? entry.sources.filter((source) => source && typeof source === "object") : [],
        retrieval: entry.retrieval,
      };
    }
    write(KNOWLEDGE_CODEX_KEY, codex);
  }
  function localKnowledgeView(entry) {
    const sourceDetails = Array.isArray(entry?.sourceDetails)
      ? entry.sourceDetails
      : Array.isArray(entry?.sources) ? entry.sources.filter((source) => source && typeof source === "object") : [];
    return { ...entry, sourceDetails };
  }
  async function searchKnowledge(query, limit, stageId) {
    if (!offline) {
      const result = await request("/knowledge/search", { method: "POST", body: JSON.stringify({ client_request_id: root.crypto.randomUUID(), ...(stageId ? { stage_id: String(stageId) } : {}), query, limit }) });
      const sourceProvenance = result.searchReceipt?.sourceProvenance;
      if (sourceProvenance && Array.isArray(result.results)) {
        result.results = result.results.map((entry) => entry?.searchReceipt
          ? { ...entry, searchReceipt: { ...entry.searchReceipt, sourceProvenance: JSON.parse(JSON.stringify(sourceProvenance)) } }
          : entry);
      }
      return result;
    }
    const data = await root.fetch("scenario/dongzhou-knowledge.json", { cache: "no-store" }).then((response) => response.json());
    const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const results = (data.entries || []).map((entry) => {
      const haystack = [entry.name, entry.summary, entry.content, ...(entry.keywords || [])].join(" ").toLocaleLowerCase();
      return { entry, score: terms.reduce((score, term) => score + (haystack.includes(term) ? 1 : 0), 0) };
    }).filter((item) => !terms.length || item.score).sort((a, b) => b.score - a.score || a.entry.index - b.entry.index).slice(0, limit).map((item) => localKnowledgeView(item.entry));
    rememberKnowledge(results);
    return { mode: "offline", query, results };
  }
  async function knowledgeCodex() {
    if (!offline) return requestWithTransientRetry("/knowledge/codex");
    return { mode: "offline", results: Object.values(read(KNOWLEDGE_CODEX_KEY, {})) };
  }
  function battleDebrief(reportId) {
    if (offline) return sealLocalBattleDebrief(reportId);
    return requestWithTransientRetry(`/battle-reports/${encodeURIComponent(reportId)}/debrief`);
  }
  function battleReadiness(stageId, battlePlan = null) {
    if (offline) return sealLocalBattleReadiness(stageId, battlePlan);
    return requestWithTransientRetry("/battle-readiness", {
      method: "POST",
      body: JSON.stringify({ stage_id: String(stageId) })
    });
  }
  function battleDeployment(stageId, battleReadiness, campaignRoute = null, battlePlan = null) {
    if (offline) return sealLocalBattleDeployment(stageId, battleReadiness, campaignRoute, battlePlan);
    return requestWithTransientRetry("/battle-deployment", {
      method: "POST",
      body: JSON.stringify({
        stage_id: String(stageId),
        battle_readiness: battleReadiness,
        campaign_route: campaignRoute
      })
    });
  }
  async function campaignRoute(input) {
    if (!offline) {
      return requestWithTransientRetry("/knowledge/routes", {
        method: "POST",
        body: JSON.stringify(input)
      });
    }
    const fromStageId = String(input.from_stage_id || "");
    const toStageId = String(input.to_stage_id || "");
    const fromIndex = Number(input.from_stage_index);
    const toIndex = Number(input.to_stage_index);
    if (!fromStageId || !toStageId || !Number.isSafeInteger(fromIndex) || toIndex !== fromIndex + 1) {
      throw new Error("campaign_route_invalid");
    }
    const fromMapId = 900000 + fromIndex;
    const toMapId = 900000 + toIndex;
    const options = [
      { method: "campaign_progression", routeId: `standalone_campaign_progression_${fromMapId}_${toMapId}`, label: "奉诏直进", provisionCost: 2, moraleDelta: 0 },
      { method: "fixed_point", routeId: `standalone_fixed_point_${fromMapId}_${toMapId}`, label: "官道驿行", provisionCost: 3, moraleDelta: 6 },
      { method: "npc_dialog", routeId: `standalone_npc_dialog_${fromMapId}_${toMapId}`, label: "向导引路", provisionCost: 1, moraleDelta: -4, guideName: "杜伯" }
    ];
    const selected = options.find((option) => option.method === String(input.route_method || "campaign_progression"));
    if (!selected) throw new Error("campaign_route_method_invalid");
    const route = {
      mode: "standalone",
      found: true,
      fromStageId,
      toStageId,
      fromMapId,
      toMapId,
      ...selected,
      options,
      knowledgeWitnesses: {
        from: await localKnowledgeWitness(fromStageId),
        to: await localKnowledgeWitness(toStageId)
      },
      sourceProvenance: await localServiceProvenance()
    };
    route.localRouteDigest = await sha256(canonicalJson(standaloneRouteTrace(route)));
    return route;
  }
  function syncNpcs(npcs) { return request("/npcs/sync", { method: "POST", body: JSON.stringify({ npcs: npcs.map((npc) => ({ hero_id: npc.heroId, name: npc.name })) }) }); }
  function setNpcInteractionPreference(enabled) { return request("/npcs/interaction-preference", { method: "POST", body: JSON.stringify({ enabled: Boolean(enabled) }) }); }
  async function commendNpc(heroId, input) {
    if (offline) return localCommendNpc(heroId, input);
    for (let attempt = 0; attempt < 12; attempt += 1) {
      const result = await request(`/npcs/${encodeURIComponent(heroId)}/commendations`, {
        method: "POST",
        body: JSON.stringify(input)
      });
      if (result?.state !== "PENDING") return result;
      await wait(Math.max(100, Math.min(1000, Number(result.retryAfterMs || 300))));
    }
    throw new Error("慰勉仍在送达，请稍后重试");
  }
  async function commendMeritNpc(heroId, input) {
    for (let attempt = 0; attempt < 12; attempt += 1) {
      const result = await request(`/npcs/${encodeURIComponent(heroId)}/merit-commendations`, {
        method: "POST",
        body: JSON.stringify(input)
      });
      if (result?.state !== "PENDING") return result;
      await wait(Math.max(100, Math.min(1000, Number(result.retryAfterMs || 300))));
    }
    throw new Error("论功慰勉仍在送达，请稍后重试");
  }
  function recallNpc(heroId, input) {
    if (offline) return localRecallNpc(heroId, input);
    return request(`/npcs/${encodeURIComponent(heroId)}/recollections`, {
      method: "POST",
      body: JSON.stringify(input)
    });
  }
  function npcState(heroId) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/state`); }
  function npcCorrespondence(heroId, limit = 20) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/correspondence?limit=${encodeURIComponent(limit)}`); }
  function organizationPublicNotices() {
    if (offline) return localOrganizationPublicNotices();
    return requestWithTransientRetry("/organization/public-notices");
  }
  async function sendNpcMessage(heroId, content, options = {}) {
    const pendingKey = NPC_MESSAGE_PENDING_PREFIX + heroId;
    const saved = read(pendingKey, null);
    const pending = saved?.content === content
      ? saved
      : { client_request_id: root.crypto.randomUUID(), content };
    write(pendingKey, pending);
    try {
      const result = await request(`/npcs/${encodeURIComponent(heroId)}/messages`, {
        method: "POST",
        body: JSON.stringify(pending),
        ...(options.signal ? { signal: options.signal } : {})
      });
      root.localStorage.removeItem(pendingKey);
      return result;
    } catch (error) {
      if ([400, 404, 409, 422].includes(error.status)) root.localStorage.removeItem(pendingKey);
      throw error;
    }
  }
  function npcSchedule(heroId) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/schedule`); }
  function npcAssignment(heroId, taskType, stageId) {
    return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/assignments/${encodeURIComponent(taskType)}?stage_id=${encodeURIComponent(stageId)}`);
  }
  function generateNpcSchedule(heroId) { return request(`/npcs/${encodeURIComponent(heroId)}/schedule`, { method: "POST", body: JSON.stringify({ force_regenerate: false }) }); }
  async function npcDecision(heroId, question, options, stageId, memory, publicNotice, contribution, contributionDossier) {
    if (offline) return localNpcDecision(heroId, question, options, stageId, memory, publicNotice);
    const pendingKey = `dongzhou-pending-decision-v5:${JSON.stringify([heroId, stageId || "", question, options, memory?.idempotencyKey || "", publicNotice?.messageId || "", contribution?.entryId || "", contributionDossier?.digest || ""])}`;
    const pending = read(pendingKey, null) || { client_request_id: root.crypto.randomUUID(), ...(stageId ? { stage_id: String(stageId) } : {}), question, options: options.map((text, index) => ({ index, text })), topic: "court_decision", ...(memory ? { memory_idempotency_key: memory.idempotencyKey, memory_digest: memory.digest } : {}), ...(publicNotice ? { public_notice_id: publicNotice.messageId, public_notice_digest: publicNotice.digest } : {}), ...(contribution ? { contribution_entry_id: contribution.entryId, contribution_entry_digest: contribution.digest } : {}), ...(contributionDossier ? { contribution_dossier_digest: contributionDossier.digest } : {}) };
    write(pendingKey, pending);
    const result = await request(`/npcs/${encodeURIComponent(heroId)}/decisions`, { method: "POST", body: JSON.stringify(pending) });
    root.localStorage.removeItem(pendingKey);
    return { ...result, clientRequestId: pending.client_request_id };
  }
  async function npcThought(heroId, input) {
    if (offline) return localNpcThought(heroId, input);
    const context = [heroId, input.stage_id, input.knowledge_id, input.evidence_source_index, input.task_type, input.logistics_briefing_request_id || "", input.logistics_briefing_digest || ""].join(":");
    const pendingKey = NPC_THOUGHT_PENDING_PREFIX + context;
    const pending = read(pendingKey, null) || { ...input, client_request_id: root.crypto.randomUUID() };
    write(pendingKey, pending);
    try {
      const result = await request(`/npcs/${encodeURIComponent(heroId)}/thoughts`, {
        method: "POST",
        body: JSON.stringify(pending)
      });
      root.localStorage.removeItem(pendingKey);
      return result;
    } catch (error) {
      if ([400, 404, 422].includes(error.status)) root.localStorage.removeItem(pendingKey);
      throw error;
    }
  }
  function mandatePendingKey(input) {
    const operation = input.operation ? JSON.stringify(input.operation) : "";
    const context = [input.stage_id, input.hero_id, input.support_hero_id || "", input.knowledge_id, input.evidence_source_index, input.council_request_id, input.task_type, input.schedule_plan_id, input.schedule_event_id, input.correspondence_message_id || "", input.correspondence_digest || "", input.thought_request_id || "", input.thought_digest || "", operation].join(":");
    return MANDATE_PENDING_PREFIX + context;
  }
  async function recoverPendingCourtMandate() {
    const response = await request("/court/mandates/pending");
    const pending = response?.pending;
    if (!pending?.input || !["REQUIRES_ACTION", "ISSUED"].includes(pending.result?.state)) return;
    write(mandatePendingKey(pending.input), pending);
  }
  async function createCourtMandate(input) {
    const pendingKey = mandatePendingKey(input);
    const saved = read(pendingKey, null);
    const revision = read(MANDATE_REVISION_KEY, null);
    const revisionReference = revision?.stage_id === input.stage_id
      ? {
          supersedes_mandate_id: revision.mandate_id,
          supersedes_mandate_digest: revision.mandate_digest
        }
      : {};
    const pending = saved?.input || saved || {
      ...input,
      ...revisionReference,
      client_request_id: input.client_request_id || root.crypto.randomUUID()
    };
    if (saved?.result?.state === "REQUIRES_ACTION") return saved.result;
    write(pendingKey, { input: pending, result: saved?.result || null });
    let result;
    try {
      result = await request("/court/mandates", { method: "POST", body: JSON.stringify(pending) });
    } catch (error) {
      if ([400, 422].includes(error.status)) root.localStorage.removeItem(pendingKey);
      throw error;
    }
    const validMandate = result.mandate?.id && result.mandate?.digest;
    if (result.state === "REQUIRES_ACTION" && validMandate && result.action?.actionId) {
      write(pendingKey, { input: pending, result });
      if (pending.supersedes_mandate_id) root.localStorage.removeItem(MANDATE_REVISION_KEY);
      return result;
    }
    if (result.state !== "ISSUED" || !validMandate) {
      if (result.state === "REJECTED") root.localStorage.removeItem(pendingKey);
      throw new Error("内核尚未签发有效军令");
    }
    write(pendingKey, { input: pending, result });
    return result;
  }
  function pendingCourtMandate() {
    for (let index = 0; index < Number(root.localStorage.length || 0); index += 1) {
      const key = root.localStorage.key(index);
      if (!key?.startsWith(MANDATE_PENDING_PREFIX)) continue;
      const saved = read(key, null);
      const input = saved?.input || saved;
      const result = saved?.result;
      if (input && ["REQUIRES_ACTION", "ISSUED"].includes(result?.state)) return { input, result };
    }
    return null;
  }
  async function resumeCourtMandate(mandateId, actionId, decision) {
    let pendingKey = null;
    let saved = null;
    for (let index = 0; index < Number(root.localStorage.length || 0); index += 1) {
      const key = root.localStorage.key(index);
      if (!key?.startsWith(MANDATE_PENDING_PREFIX)) continue;
      const candidate = read(key, null);
      if (candidate?.result?.mandate?.id === mandateId) {
        pendingKey = key;
        saved = candidate;
        break;
      }
    }
    if (!pendingKey || !saved) throw new Error("未找到待裁决军令");
    const result = await request(`/court/mandates/${encodeURIComponent(mandateId)}/resume`, {
      method: "POST",
      body: JSON.stringify({ action_id: actionId, decision })
    });
    if (result.state === "RETURNED") {
      root.localStorage.removeItem(pendingKey);
      write(MANDATE_REVISION_KEY, {
        stage_id: saved.input.stage_id,
        mandate_id: result.mandate.id,
        mandate_digest: result.mandate.digest
      });
    } else if (result.state === "REJECTED") root.localStorage.removeItem(pendingKey);
    else write(pendingKey, { ...saved, result });
    return result;
  }
  async function scheduleCourtMandate(mandateId, mandateDigest) {
    const pendingKey = MANDATE_SCHEDULE_PENDING_PREFIX + mandateId;
    const saved = read(pendingKey, null);
    const pending = saved?.mandate_digest === mandateDigest
      ? saved
      : { client_request_id: root.crypto.randomUUID(), mandate_digest: mandateDigest };
    write(pendingKey, pending);
    try {
      const result = await request(`/court/mandates/${encodeURIComponent(mandateId)}/schedule`, {
        method: "POST",
        body: JSON.stringify(pending)
      });
      if (result.state !== "COMPLETED" || !result.scheduleReceipt?.digest) throw new Error("属官日程回执无效");
      root.localStorage.removeItem(pendingKey);
      return result;
    } catch (error) {
      if ([400, 404, 409, 422].includes(error.status)) root.localStorage.removeItem(pendingKey);
      throw error;
    }
  }
  function acknowledgeCourtMandate(input) {
    if (input && typeof input === "object") {
      root.localStorage.removeItem(mandatePendingKey(input));
      return;
    }
    for (let index = Number(root.localStorage.length || 0) - 1; index >= 0; index -= 1) {
      const key = root.localStorage.key(index);
      if (!key?.startsWith(MANDATE_PENDING_PREFIX)) continue;
      const pending = read(key, null);
      const requestInput = pending?.input || pending;
      if (pending && (pending?.result?.mandate?.id === input || String(input || "").endsWith(String(requestInput?.client_request_id || "")))) root.localStorage.removeItem(key);
    }
  }
  function applyOrganizationOrder(profile, task, result) {
    task = Object.values(read(ORDER_JOURNAL_KEY, {})).find((entry) => entry.result?.taskId === result.taskId)?.task || task;
    const acceptanceSource = result.sourceProvenance;
    const acceptanceServices = Object.keys(acceptanceSource?.services || {});
    if (acceptanceSource && (!/^[0-9a-f]{64}$/.test(String(acceptanceSource.digest || "")) || acceptanceSource.kernel?.module !== "dongzhou_service_provenance" || acceptanceSource.kernel?.state !== "SEALED" || acceptanceServices.length !== 4 || !["knowledge", "aiNpc", "orgFlow", "nexusKernel"].every((name) => acceptanceServices.includes(name)) || acceptanceSource.digest !== task.mandate?.sourceProvenance?.digest)) {
      throw new Error("组织任务受理服务来源与军令不一致");
    }
    const org = profile.organization;
    if (org.tasks.some((entry) => entry.remoteResult === result.taskId)) return;
    org.mandates ||= [];
    if (task.mandate && !org.mandates.some((entry) => entry.id === task.mandate.id)) {
      org.mandates.push(JSON.parse(JSON.stringify(task.mandate)));
    }
    const mandate = task.mandate ? org.mandates.find((entry) => entry.id === task.mandate.id) : null;
    if (mandate) {
      mandate.state = "ORDERED";
      mandate.organizationTaskId = result.taskId;
    }
    const restored = {
      ...task,
      remoteMirrored: true,
      remoteResult: result.taskId,
      ...(acceptanceSource ? { sourceProvenance: JSON.parse(JSON.stringify(acceptanceSource)) } : {}),
      ...(result.topology ? { organizationTopology: JSON.parse(JSON.stringify(result.topology)) } : {})
    };
    org.tasks.push(restored);
    const sequence = /^dz-\d+-(\d+)-/.exec(task.id);
    org.taskSequence = Math.max(org.taskSequence || 0, sequence ? Number(sequence[1]) : 0);
    const member = org.members.find((entry) => entry.id === task.assigneeId);
    if (member) member.fatigue = Math.min(100, member.fatigue + 12);
    profile.campaignResources.provisions = Math.max(0, profile.campaignResources.provisions - task.cost);
    org.history.push({ month: org.month, tone: "order", text: `${task.assigneeName}领命：${task.name}` });
  }

  function acknowledgeOrganizationOrders(profile) {
    const journal = read(ORDER_JOURNAL_KEY, {});
    for (const [key, entry] of Object.entries(journal)) {
      if (entry.result?.taskId && profile.organization?.tasks?.some((task) => task.remoteResult === entry.result.taskId)) {
        delete journal[key];
        root.localStorage.removeItem(key);
      }
    }
    write(ORDER_JOURNAL_KEY, journal);
  }

  async function recoverOrganizationOrders(profile) {
    const journal = read(ORDER_JOURNAL_KEY, {});
    for (const [key, entry] of Object.entries(journal)) {
      if (!entry.task) continue;
      try {
        const result = entry.result || await createOrganizationTask(entry.input, entry.task);
        applyOrganizationOrder(profile, entry.task, result);
        if (entry.task.mandate?.id) acknowledgeCourtMandate(entry.task.mandate.id);
      } catch (error) {
        // Definitively rejected orders have no charge or binding to restore.
        if (read(ORDER_JOURNAL_KEY, {})[key]) throw error;
      }
    }
    if (Object.keys(journal).length) await persist(profile);
  }

  async function createOrganizationTask(input, task) {
    const pendingKey = `dongzhou-pending-task-v1:${input.task_type}:${input.assignee_hero_id}:${input.stage_id}:${input.parameters?.mandate_id || "unsealed"}`;
    const existing = read(ORDER_JOURNAL_KEY, {});
    if (Object.entries(existing).some(([key, entry]) => key !== pendingKey && entry.input?.assignee_hero_id === input.assignee_hero_id)) {
      throw new Error("该属官尚有待确认差事，请刷新恢复后再派单");
    }
    const pending = read(pendingKey, null) || { ...input, client_request_id: input.client_request_id || root.crypto.randomUUID() };
    write(pendingKey, pending);
    const journal = read(ORDER_JOURNAL_KEY, {});
    if (!journal[pendingKey]) journal[pendingKey] = { input: pending, task };
    write(ORDER_JOURNAL_KEY, journal);
    if (journal[pendingKey].result) return journal[pendingKey].result;
    let result;
    try {
      result = await request("/organization/tasks", { method: "POST", body: JSON.stringify(pending) });
    } catch (error) {
      if ([400, 422].includes(error.status)) {
        const current = read(ORDER_JOURNAL_KEY, {});
        delete current[pendingKey];
        write(ORDER_JOURNAL_KEY, current);
        root.localStorage.removeItem(pendingKey);
      }
      throw error;
    }
    // HTTP 200 也可能是已拒绝请求的幂等回放，只有明确受理且有任务号才能扣粮。
    if (result.state !== "ACCEPTED" || !result.taskId) {
      if (["REJECTED", "FAILED"].includes(result.state)) {
        root.localStorage.removeItem(pendingKey);
        const current = read(ORDER_JOURNAL_KEY, {});
        delete current[pendingKey];
        write(ORDER_JOURNAL_KEY, current);
      }
      const error = new Error(result.error?.message || "差事尚未确认受理，请稍后重试");
      error.code = result.error?.code || "organization_order_unconfirmed";
      throw error;
    }
    const current = read(ORDER_JOURNAL_KEY, {});
    current[pendingKey] = { ...journal[pendingKey], result };
    write(ORDER_JOURNAL_KEY, current);
    return result;
  }
  function organizationTask(taskId) { return requestWithTransientRetry(`/organization/tasks/${encodeURIComponent(taskId)}`); }
  function organizationRoster() { return requestWithTransientRetry("/organization/roster"); }
  function organizationMemberContributions(heroId) { return requestWithTransientRetry(`/organization/members/${encodeURIComponent(heroId)}/contributions`); }
  function organizationContributionDossier(heroId, entryId) { return requestWithTransientRetry(`/organization/members/${encodeURIComponent(heroId)}/contributions/${encodeURIComponent(entryId)}/dossier`); }
  function organizationPlayerTasks() { return requestWithTransientRetry("/organization/player-tasks"); }
  function organizationPlayerContributions() { return requestWithTransientRetry("/organization/player-contributions"); }
  function organizationPlayerContributionDossier(entryId) { return requestWithTransientRetry(`/organization/player-contributions/${encodeURIComponent(entryId)}/dossier`); }
  function organizationInventory() {
    if (offline) return Promise.resolve(localInventorySnapshot());
    return requestWithTransientRetry("/organization/inventory");
  }
  function organizationScheduledDuties() {
    if (offline) return buildLocalScheduledDutySnapshot();
    return requestWithTransientRetry("/organization/scheduled-duties");
  }
  async function setOrganizationScheduledDutyEnabled(enabled) {
    const saved = read(SCHEDULED_DUTY_STATUS_PENDING_KEY, null);
    const pending = saved?.enabled === Boolean(enabled)
      ? saved
      : { client_request_id: root.crypto.randomUUID(), enabled: Boolean(enabled) };
    write(SCHEDULED_DUTY_STATUS_PENDING_KEY, pending);
    try {
      if (offline) {
        const result = await localSetOrganizationScheduledDutyEnabled(pending);
        root.localStorage.removeItem(SCHEDULED_DUTY_STATUS_PENDING_KEY);
        return result;
      }
      const result = await request("/organization/scheduled-duties/status", {
        method: "POST",
        body: JSON.stringify(pending)
      });
      root.localStorage.removeItem(SCHEDULED_DUTY_STATUS_PENDING_KEY);
      return result;
    } catch (error) {
      if ([400, 422].includes(error.status)) {
        root.localStorage.removeItem(SCHEDULED_DUTY_STATUS_PENDING_KEY);
      }
      throw error;
    }
  }
  async function organizationLogisticsBriefing(heroId, input) {
    if (offline) return localOrganizationLogisticsBriefing(heroId, input);
    const pendingKey = LOGISTICS_BRIEFING_PENDING_PREFIX + [heroId, input.stage_id].join(":");
    const saved = read(pendingKey, null);
    const pending = saved?.stage_id === input.stage_id && saved?.stage_title === input.stage_title
      ? saved
      : { ...input, client_request_id: root.crypto.randomUUID() };
    write(pendingKey, pending);
    try {
      const result = await request(`/organization/logistics-briefings/${encodeURIComponent(heroId)}`, {
        method: "POST",
        body: JSON.stringify(pending)
      });
      root.localStorage.removeItem(pendingKey);
      return result;
    } catch (error) {
      if ([400, 409, 422].includes(error.status)) root.localStorage.removeItem(pendingKey);
      throw error;
    }
  }
  function pendingOrganizationInventoryRequisition() {
    const stored = read(INVENTORY_REQUISITION_PENDING_KEY, null);
    if (!stored) return null;
    if (stored.input) return stored;
    return { input: stored, result: null, decision: null };
  }
  async function requisitionOrganizationInventory(input) {
    const existing = pendingOrganizationInventoryRequisition();
    const journal = existing || {
      input: {
        ...input,
        client_request_id: input?.client_request_id || root.crypto.randomUUID()
      },
      result: null,
      decision: null
    };
    write(INVENTORY_REQUISITION_PENDING_KEY, journal);
    if (journal.result && ["REQUIRES_ACTION", "RETRYABLE", "COMPLETED", "REJECTED"].includes(journal.result.state)) {
      return journal.result;
    }
    try {
      if (offline) {
        const result = await localInventoryRequisitionDraft(journal.input);
        write(INVENTORY_REQUISITION_PENDING_KEY, { ...journal, result });
        return result;
      }
      const result = await request("/organization/inventory/requisitions", {
        method: "POST",
        body: JSON.stringify(journal.input)
      });
      write(INVENTORY_REQUISITION_PENDING_KEY, {
        ...journal,
        result,
        decision: result.state === "RETRYABLE" ? "APPROVE" : journal.decision
      });
      return result;
    } catch (error) {
      if ([400, 422].includes(error.status) || [
        "organization_inventory_requisition_conflict"
      ].includes(error.code)) {
        root.localStorage.removeItem(INVENTORY_REQUISITION_PENDING_KEY);
      }
      throw error;
    }
  }
  async function resumeOrganizationInventoryRequisition(requisitionId, actionId, decision) {
    if (offline) return localResumeOrganizationInventoryRequisition(requisitionId, actionId, decision);
    const journal = pendingOrganizationInventoryRequisition();
    if (!journal?.input || journal.result?.requisition?.id !== requisitionId) {
      throw new Error("军需调拨草案与待裁记录不匹配");
    }
    const pending = { ...journal, decision };
    write(INVENTORY_REQUISITION_PENDING_KEY, pending);
    const result = await request(
      `/organization/inventory/requisitions/${encodeURIComponent(requisitionId)}/resume`,
      {
        method: "POST",
        body: JSON.stringify({ action_id: actionId, decision })
      }
    );
    write(INVENTORY_REQUISITION_PENDING_KEY, { ...pending, result });
    return result;
  }
  function acknowledgeOrganizationInventoryRequisition(requestId) {
    const pending = pendingOrganizationInventoryRequisition();
    if (pending?.input?.client_request_id === requestId) {
      root.localStorage.removeItem(INVENTORY_REQUISITION_PENDING_KEY);
    }
  }
  function reviewOrganizationTask(taskId, input) {
    return request(`/organization/tasks/${encodeURIComponent(taskId)}/review`, { method: "POST", body: JSON.stringify(input) });
  }
  async function stageKnowledge(stageId) {
    if (!offline) {
      const result = await requestWithTransientRetry(`/knowledge/stages/${encodeURIComponent(stageId)}`);
      return result;
    }
    const response = await root.fetch("scenario/dongzhou-knowledge.json", { cache: "no-store" });
    if (!response.ok) throw new Error("史料目录暂不可达");
    const data = await response.json();
    const results = (data.entries || []).filter((entry) => entry.stageId === stageId).map(localKnowledgeView);
    rememberKnowledge(results);
    return { mode: "offline", stageId, results };
  }

  async function startKnowledgeQuiz(stageId, clientRequestId) {
    if (offline) {
      const key = KNOWLEDGE_QUIZ_PREFIX + clientRequestId;
      const existing = read(key, null);
      if (existing) {
        if (existing.stageId !== String(stageId)) throw new Error("idempotency_conflict");
        if (existing.result) return { replayed: true, ...existing.result };
        const rebuilt = await buildLocalKnowledgeQuiz(clientRequestId, stageId, existing.deadlineAt);
        if (canonicalJson(existing.ready) !== canonicalJson(rebuilt.ready)) {
          throw new Error("knowledge_quiz_source_invalid");
        }
        return { replayed: true, ...rebuilt.ready };
      }
      const deadlineAt = new Date(Date.now() + 30000).toISOString();
      const built = await buildLocalKnowledgeQuiz(clientRequestId, stageId, deadlineAt);
      write(key, { stageId: String(stageId), deadlineAt, ready: built.ready });
      return built.ready;
    }
    return request("/knowledge/quiz", {
      method: "POST",
      body: JSON.stringify({ stage_id: stageId, client_request_id: clientRequestId })
    });
  }

  async function answerKnowledgeQuiz(questionId, actionId, answerIndex) {
    if (offline) {
      const key = KNOWLEDGE_QUIZ_PREFIX + questionId;
      const record = read(key, null);
      if (!record) throw new Error("knowledge_quiz_not_found");
      if (record.result) {
        if (record.result.selectedIndex !== answerIndex) throw new Error("knowledge_quiz_already_answered");
        return { replayed: true, ...record.result };
      }
      const built = await buildLocalKnowledgeQuiz(questionId, record.stageId, record.deadlineAt);
      if (built.ready.action.actionId !== actionId) throw new Error("knowledge_quiz_action_invalid");
      if (!Number.isInteger(answerIndex) || answerIndex < 0 || answerIndex >= built.trace.options.length) {
        throw new Error("knowledge_quiz_answer_invalid");
      }
      const state = Date.now() > Date.parse(record.deadlineAt) ? "EXPIRED" : "COMPLETED";
      const correct = state === "COMPLETED" && answerIndex === built.trace.correctIndex;
      const resultTrace = {
        questionDigest: built.ready.question.receipt.digest,
        selectedIndex: answerIndex,
        correctIndex: built.trace.correctIndex,
        state,
        correct,
        score: correct ? 10 : 0,
        sourceProvenance: built.trace.sourceProvenance
      };
      const result = {
        mode: "offline",
        ...resultTrace,
        receipt: {
          digest: await sha256(canonicalJson(resultTrace)),
          sourceProvenance: built.trace.sourceProvenance,
          kernel: {
            module: "dongzhou_knowledge_tournament",
            moduleVersion: "1.1.0",
            nexusKernelVersion: "0.2.0",
            state: "SEALED"
          }
        },
        questionId: String(questionId),
        stageId: record.stageId,
        knowledgeId: built.trace.knowledgeId,
        correctAnswer: built.trace.options[built.trace.correctIndex],
        source: built.source
      };
      write(key, { ...record, result });
      return result;
    }
    return request(`/knowledge/quiz/${encodeURIComponent(questionId)}/answer`, {
      method: "POST",
      body: JSON.stringify({ action_id: actionId, answer_index: answerIndex })
    });
  }

  async function verifyKnowledgeQuizSeal(questionId) {
    if (offline) {
      const record = read(KNOWLEDGE_QUIZ_PREFIX + questionId, null);
      if (!record?.result) throw new Error("knowledge_quiz_not_answered");
      const built = await buildLocalKnowledgeQuiz(questionId, record.stageId, record.deadlineAt);
      const expectedTrace = {
        questionDigest: built.ready.question.receipt.digest,
        selectedIndex: record.result.selectedIndex,
        correctIndex: built.trace.correctIndex,
        state: record.result.state,
        correct: record.result.state === "COMPLETED" && record.result.selectedIndex === built.trace.correctIndex,
        score: record.result.state === "COMPLETED" && record.result.selectedIndex === built.trace.correctIndex ? 10 : 0,
        sourceProvenance: built.trace.sourceProvenance
      };
      const digest = await sha256(canonicalJson(expectedTrace));
      const expectedKernel = {
        module: "dongzhou_knowledge_tournament",
        moduleVersion: "1.1.0",
        nexusKernelVersion: "0.2.0",
        state: "SEALED"
      };
      if (record.result.receipt?.digest !== digest
        || record.result.correctIndex !== expectedTrace.correctIndex
        || record.result.correct !== expectedTrace.correct
        || record.result.score !== expectedTrace.score
        || canonicalJson(record.result.receipt?.sourceProvenance) !== canonicalJson(built.trace.sourceProvenance)
        || canonicalJson(record.result.receipt?.kernel) !== canonicalJson(expectedKernel)) {
        throw new Error("knowledge_quiz_seal_invalid");
      }
      return {
        verified: true,
        questionId: String(questionId),
        stageId: record.stageId,
        knowledgeId: built.trace.knowledgeId,
        score: expectedTrace.score,
        digest,
        kernel: expectedKernel,
        sourceProvenance: built.trace.sourceProvenance
      };
    }
    return requestWithTransientRetry(`/knowledge/quiz/${encodeURIComponent(questionId)}/seal`);
  }

  function pendingAdviserQuestion() {
    return read(ADVISER_QUESTION_KEY, null);
  }

  async function askAdviser(input) {
    if (offline) {
      const pending = {
        input: { ...input, client_request_id: root.crypto.randomUUID() },
        result: null,
        feedback: null
      };
      const built = await buildLocalAdviserAnswer(pending.input);
      const journal = { ...pending, result: built.result };
      write(ADVISER_QUESTION_KEY, journal);
      return built.result;
    }
    const existing = pendingAdviserQuestion();
    const pending = existing?.result?.state === "PROCESSING"
      ? existing
      : {
          input: { ...input, client_request_id: root.crypto.randomUUID() },
          result: null,
          feedback: null
        };
    write(ADVISER_QUESTION_KEY, pending);
    const result = await request("/adviser/questions", {
      method: "POST",
      body: JSON.stringify(pending.input)
    });
    write(ADVISER_QUESTION_KEY, { ...pending, result });
    return result;
  }

  async function adviserQuestion(questionId) {
    if (offline) {
      const { rebuilt } = await validatedLocalAdviserJournal(questionId);
      return { ...rebuilt.result, replayed: true };
    }
    const result = await requestWithTransientRetry(`/adviser/questions/${encodeURIComponent(questionId)}`);
    const pending = pendingAdviserQuestion();
    if (pending?.input?.client_request_id === questionId) {
      write(ADVISER_QUESTION_KEY, { ...pending, result });
    }
    return result;
  }

  async function feedbackAdviser(questionId, rating, reason = "") {
    if (offline) {
      if (!['accurate', 'inaccurate'].includes(rating) || String(reason).length > 500) {
        throw new Error("adviser_feedback_invalid");
      }
      const { journal } = await validatedLocalAdviserJournal(questionId);
      if (journal.feedback?.result) {
        if (journal.feedback.rating !== rating || journal.feedback.reason !== reason) {
          throw new Error("adviser_feedback_already_recorded");
        }
        return { ...journal.feedback.result, replayed: true };
      }
      const feedback = {
        action_id: root.crypto.randomUUID(), rating, reason,
        result: { mode: "offline", state: "RECORDED", questionId: String(questionId), rating, replayed: false }
      };
      write(ADVISER_QUESTION_KEY, { ...journal, feedback });
      return feedback.result;
    }
    const pending = pendingAdviserQuestion();
    const feedback = pending?.feedback?.rating === rating
      ? pending.feedback
      : { action_id: root.crypto.randomUUID(), rating, reason };
    if (pending) write(ADVISER_QUESTION_KEY, { ...pending, feedback });
    const result = await request(`/adviser/questions/${encodeURIComponent(questionId)}/feedback`, {
      method: "POST",
      body: JSON.stringify(feedback)
    });
    if (pending) write(ADVISER_QUESTION_KEY, { ...pending, feedback: { ...feedback, result } });
    return result;
  }

  async function decideAdviserGuide(questionId, decision) {
    if (offline) {
      if (!['ACCEPT', 'REJECT'].includes(decision)) throw new Error("adviser_guide_decision_invalid");
      const { journal, rebuilt } = await validatedLocalAdviserJournal(questionId);
      if (!rebuilt.result.guide.available || !rebuilt.result.guide.sessionId) {
        throw new Error("adviser_guide_unavailable");
      }
      if (journal.guideDecision?.result) {
        if (journal.guideDecision.decision !== decision) throw new Error("adviser_guide_already_decided");
        await validateLocalAdviserGuide(rebuilt.result, journal.guideDecision.result.guide);
        return { ...journal.guideDecision.result, replayed: true };
      }
      const actionId = root.crypto.randomUUID();
      const state = decision === "ACCEPT" ? "ACCEPTED" : "REJECTED";
      const receipt = await sealLocalAdviserGuide(rebuilt.result, actionId, decision, state, "guide_decision");
      const result = { mode: "offline", state, replayed: false, guide: receipt };
      write(ADVISER_QUESTION_KEY, {
        ...journal,
        guideDecision: { action_id: actionId, decision, result }
      });
      return result;
    }
    const pending = pendingAdviserQuestion();
    const guideDecision = pending?.guideDecision?.decision === decision
      ? pending.guideDecision
      : { action_id: root.crypto.randomUUID(), decision, result: null };
    if (pending) write(ADVISER_QUESTION_KEY, { ...pending, guideDecision });
    const result = await request(`/adviser/questions/${encodeURIComponent(questionId)}/guide`, {
      method: "POST",
      body: JSON.stringify({ action_id: guideDecision.action_id, decision })
    });
    if (pending) write(ADVISER_QUESTION_KEY, { ...pending, guideDecision: { ...guideDecision, result } });
    return result;
  }

  async function adviserGuide(actionId) {
    if (offline) {
      const journal = pendingAdviserQuestion();
      if (!journal?.input?.client_request_id || journal.guideDecision?.action_id !== actionId) {
        throw new Error("adviser_guide_not_found");
      }
      const { journal: validated, rebuilt } = await validatedLocalAdviserJournal(journal.input.client_request_id);
      const previous = validated.guideDecision?.result?.guide;
      await validateLocalAdviserGuide(rebuilt.result, previous);
      if (previous.decision !== "ACCEPT" || !["ACCEPTED", "RUNNING", "COMPLETED"].includes(previous.state)) {
        return validated.guideDecision.result;
      }
      const nextState = previous.state === "ACCEPTED" ? "RUNNING" : previous.state === "RUNNING" ? "COMPLETED" : "COMPLETED";
      const eventType = nextState === "RUNNING" ? "guide_started" : "guide_completed";
      const receipt = await sealLocalAdviserGuide(
        rebuilt.result, actionId, "ACCEPT", nextState, eventType,
        { message: nextState === "COMPLETED" ? "已抵达当前关卡入口。" : "杜伯正在引路。" }
      );
      const result = { mode: "offline", state: nextState, guide: receipt };
      write(ADVISER_QUESTION_KEY, {
        ...validated,
        guideDecision: { ...validated.guideDecision, result }
      });
      return result;
    }
    const result = await requestWithTransientRetry(`/adviser/guides/${encodeURIComponent(actionId)}`);
    const pending = pendingAdviserQuestion();
    if (pending?.guideDecision?.action_id === actionId) {
      write(ADVISER_QUESTION_KEY, {
        ...pending,
        guideDecision: { ...pending.guideDecision, result }
      });
    }
    return result;
  }

  async function cancelAdviserGuide(actionId, reason = "player_cancelled") {
    if (offline) {
      if (String(reason).length > 500) throw new Error("adviser_guide_cancel_invalid");
      const journal = pendingAdviserQuestion();
      if (!journal?.input?.client_request_id || journal.guideDecision?.action_id !== actionId) {
        throw new Error("adviser_guide_not_found");
      }
      const { journal: validated, rebuilt } = await validatedLocalAdviserJournal(journal.input.client_request_id);
      const previous = validated.guideDecision?.result?.guide;
      await validateLocalAdviserGuide(rebuilt.result, previous);
      if (validated.guideCancellation?.result) {
        await validateLocalAdviserGuide(rebuilt.result, validated.guideCancellation.result.guide);
        return { ...validated.guideCancellation.result, replayed: true };
      }
      if (previous.decision !== "ACCEPT" || !["ACCEPTED", "RUNNING"].includes(previous.state)) {
        throw new Error("adviser_guide_not_cancellable");
      }
      const cancellation = { action_id: root.crypto.randomUUID(), reason: String(reason), result: null };
      const receipt = await sealLocalAdviserGuide(
        rebuilt.result, actionId, "ACCEPT", "CANCELLED", "guide_cancelled", { reason: cancellation.reason }
      );
      const result = { mode: "offline", state: "CANCELLED", replayed: false, guide: receipt };
      cancellation.result = result;
      write(ADVISER_QUESTION_KEY, {
        ...validated,
        guideDecision: { ...validated.guideDecision, result },
        guideCancellation: cancellation
      });
      return result;
    }
    const pending = pendingAdviserQuestion();
    const cancellation = pending?.guideCancellation || {
      action_id: root.crypto.randomUUID(), reason, result: null
    };
    if (pending) write(ADVISER_QUESTION_KEY, { ...pending, guideCancellation: cancellation });
    const result = await request(`/adviser/guides/${encodeURIComponent(actionId)}/cancel`, {
      method: "POST",
      body: JSON.stringify({ action_id: cancellation.action_id, reason: cancellation.reason })
    });
    if (pending) write(ADVISER_QUESTION_KEY, {
      ...pending,
      guideDecision: pending.guideDecision
        ? { ...pending.guideDecision, result }
        : pending.guideDecision,
      guideCancellation: { ...cancellation, result }
    });
    return result;
  }

  return { initialize, persist, status, searchKnowledge, knowledgeCodex, battleDebrief, battleReadiness, battleDeployment, verifyBattleDeployment, campaignRoute, stageKnowledge, startKnowledgeQuiz, answerKnowledgeQuiz, verifyKnowledgeQuizSeal, pendingAdviserQuestion, askAdviser, adviserQuestion, feedbackAdviser, decideAdviserGuide, adviserGuide, cancelAdviserGuide, syncNpcs, setNpcInteractionPreference, commendNpc, commendMeritNpc, recallNpc, npcState, npcCorrespondence, organizationPublicNotices, sendNpcMessage, npcSchedule, npcAssignment, generateNpcSchedule, npcThought, npcDecision, createCourtMandate, pendingCourtMandate, resumeCourtMandate, scheduleCourtMandate, acknowledgeCourtMandate, createOrganizationTask, applyOrganizationOrder, organizationTask, organizationRoster, organizationMemberContributions, organizationContributionDossier, organizationPlayerTasks, organizationPlayerContributions, organizationPlayerContributionDossier, organizationInventory, organizationScheduledDuties, setOrganizationScheduledDutyEnabled, organizationLogisticsBriefing, pendingOrganizationInventoryRequisition, requisitionOrganizationInventory, resumeOrganizationInventoryRequisition, acknowledgeOrganizationInventoryRequisition, reviewOrganizationTask, isOffline: () => offline };
});
