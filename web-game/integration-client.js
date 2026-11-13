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
  const NPC_MESSAGE_PENDING_PREFIX = "dongzhou-pending-npc-message-v1:";
  const NPC_THOUGHT_PENDING_PREFIX = "dongzhou-pending-npc-thought-v1:";
  const MANDATE_SCHEDULE_PENDING_PREFIX = "dongzhou-pending-mandate-schedule-v1:";
  const INVENTORY_REQUISITION_PENDING_KEY = "dongzhou-pending-inventory-requisition-v1";
  const LOGISTICS_BRIEFING_PENDING_PREFIX = "dongzhou-pending-logistics-briefing-v1:";
  const ADVISER_QUESTION_KEY = "dongzhou-adviser-question-v1";
  const offline = new URLSearchParams(root.location?.search || "").get("offline") === "1";
  let session = read(SESSION_KEY, null);
  let sessionPromise = null;
  let saveVersion = 1;
  let persistChain = Promise.resolve();
  let saveBlocked = false;
  const TRANSIENT_STATUSES = new Set([502, 503, 504]);

  function read(key, fallback) {
    try { return JSON.parse(root.localStorage.getItem(key)) || fallback; } catch (_) { return fallback; }
  }

  function write(key, value) {
    root.localStorage.setItem(key, JSON.stringify(value));
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
    if (offline) return { profile: localProfile, connected: false, offline: true };
    await ensureSession();
    try {
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
    if (offline || !session?.playerId) return Promise.resolve(null);
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
  async function searchKnowledge(query, limit, stageId) {
    if (!offline) {
      const result = await request("/knowledge/search", { method: "POST", body: JSON.stringify({ client_request_id: root.crypto.randomUUID(), ...(stageId ? { stage_id: String(stageId) } : {}), query, limit }) });
      return result;
    }
    const data = await root.fetch("scenario/dongzhou-knowledge.json", { cache: "no-store" }).then((response) => response.json());
    const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const results = (data.entries || []).map((entry) => {
      const haystack = [entry.name, entry.summary, entry.content, ...(entry.keywords || [])].join(" ").toLocaleLowerCase();
      return { entry, score: terms.reduce((score, term) => score + (haystack.includes(term) ? 1 : 0), 0) };
    }).filter((item) => !terms.length || item.score).sort((a, b) => b.score - a.score || a.entry.index - b.entry.index).slice(0, limit).map((item) => item.entry);
    rememberKnowledge(results);
    return { mode: "offline", query, results };
  }
  async function knowledgeCodex() {
    if (!offline) return requestWithTransientRetry("/knowledge/codex");
    return { mode: "offline", results: Object.values(read(KNOWLEDGE_CODEX_KEY, {})) };
  }
  function campaignRoute(input) {
    if (!offline) {
      return requestWithTransientRetry("/knowledge/routes", {
        method: "POST",
        body: JSON.stringify(input)
      });
    }
    const fromMapId = 900000 + Number(input.from_stage_index);
    const toMapId = 900000 + Number(input.to_stage_index);
    return Promise.resolve({
      mode: "offline",
      found: true,
      fromStageId: input.from_stage_id,
      toStageId: input.to_stage_id,
      fromMapId,
      toMapId,
      routeId: `offline_campaign_progression_${fromMapId}_${toMapId}`,
      provisionCost: 2
    });
  }
  function syncNpcs(npcs) { return request("/npcs/sync", { method: "POST", body: JSON.stringify({ npcs: npcs.map((npc) => ({ hero_id: npc.heroId, name: npc.name })) }) }); }
  function setNpcInteractionPreference(enabled) { return request("/npcs/interaction-preference", { method: "POST", body: JSON.stringify({ enabled: Boolean(enabled) }) }); }
  function npcState(heroId) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/state`); }
  function npcCorrespondence(heroId, limit = 20) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/correspondence?limit=${encodeURIComponent(limit)}`); }
  async function sendNpcMessage(heroId, content) {
    const pendingKey = NPC_MESSAGE_PENDING_PREFIX + heroId;
    const saved = read(pendingKey, null);
    const pending = saved?.content === content
      ? saved
      : { client_request_id: root.crypto.randomUUID(), content };
    write(pendingKey, pending);
    try {
      const result = await request(`/npcs/${encodeURIComponent(heroId)}/messages`, {
        method: "POST",
        body: JSON.stringify(pending)
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
  async function npcDecision(heroId, question, options, stageId, memory) {
    const pendingKey = `dongzhou-pending-decision-v3:${JSON.stringify([heroId, stageId || "", question, options, memory?.idempotencyKey || ""])}`;
    const pending = read(pendingKey, null) || { client_request_id: root.crypto.randomUUID(), ...(stageId ? { stage_id: String(stageId) } : {}), question, options: options.map((text, index) => ({ index, text })), topic: "court_decision", ...(memory ? { memory_idempotency_key: memory.idempotencyKey, memory_digest: memory.digest } : {}) };
    write(pendingKey, pending);
    const result = await request(`/npcs/${encodeURIComponent(heroId)}/decisions`, { method: "POST", body: JSON.stringify(pending) });
    root.localStorage.removeItem(pendingKey);
    return { ...result, clientRequestId: pending.client_request_id };
  }
  async function npcThought(heroId, input) {
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
  async function createCourtMandate(input) {
    const pendingKey = mandatePendingKey(input);
    const saved = read(pendingKey, null);
    const pending = saved?.input || saved || { ...input, client_request_id: input.client_request_id || root.crypto.randomUUID() };
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
    if (result.state === "REJECTED") root.localStorage.removeItem(pendingKey);
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
    const restored = { ...task, remoteMirrored: true, remoteResult: result.taskId };
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
  function organizationInventory() { return requestWithTransientRetry("/organization/inventory"); }
  function organizationScheduledDuties() { return requestWithTransientRetry("/organization/scheduled-duties"); }
  async function organizationLogisticsBriefing(heroId, input) {
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
    const results = (data.entries || []).filter((entry) => entry.stageId === stageId);
    rememberKnowledge(results);
    return { mode: "offline", stageId, results };
  }

  function startKnowledgeQuiz(stageId, clientRequestId) {
    if (offline) return Promise.reject(new Error("knowledge_quiz_requires_online"));
    return request("/knowledge/quiz", {
      method: "POST",
      body: JSON.stringify({ stage_id: stageId, client_request_id: clientRequestId })
    });
  }

  function answerKnowledgeQuiz(questionId, actionId, answerIndex) {
    if (offline) return Promise.reject(new Error("knowledge_quiz_requires_online"));
    return request(`/knowledge/quiz/${encodeURIComponent(questionId)}/answer`, {
      method: "POST",
      body: JSON.stringify({ action_id: actionId, answer_index: answerIndex })
    });
  }

  function pendingAdviserQuestion() {
    return read(ADVISER_QUESTION_KEY, null);
  }

  async function askAdviser(input) {
    if (offline) return Promise.reject(new Error("adviser_requires_online"));
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
    if (offline) return Promise.reject(new Error("adviser_requires_online"));
    const result = await requestWithTransientRetry(`/adviser/questions/${encodeURIComponent(questionId)}`);
    const pending = pendingAdviserQuestion();
    if (pending?.input?.client_request_id === questionId) {
      write(ADVISER_QUESTION_KEY, { ...pending, result });
    }
    return result;
  }

  async function feedbackAdviser(questionId, rating, reason = "") {
    if (offline) return Promise.reject(new Error("adviser_requires_online"));
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

  return { initialize, persist, status, searchKnowledge, knowledgeCodex, campaignRoute, stageKnowledge, startKnowledgeQuiz, answerKnowledgeQuiz, pendingAdviserQuestion, askAdviser, adviserQuestion, feedbackAdviser, syncNpcs, setNpcInteractionPreference, npcState, npcCorrespondence, sendNpcMessage, npcSchedule, npcAssignment, generateNpcSchedule, npcThought, npcDecision, createCourtMandate, pendingCourtMandate, resumeCourtMandate, scheduleCourtMandate, acknowledgeCourtMandate, createOrganizationTask, applyOrganizationOrder, organizationTask, organizationRoster, organizationInventory, organizationScheduledDuties, organizationLogisticsBriefing, pendingOrganizationInventoryRequisition, requisitionOrganizationInventory, resumeOrganizationInventoryRequisition, acknowledgeOrganizationInventoryRequisition, reviewOrganizationTask, isOffline: () => offline };
});
