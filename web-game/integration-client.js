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
  const offline = new URLSearchParams(root.location?.search || "").get("offline") === "1";
  let session = read(SESSION_KEY, null);
  let sessionPromise = null;
  let saveVersion = 1;
  let persistChain = Promise.resolve();
  let saveBlocked = false;
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
    }).filter((item) => !terms.length || item.score).sort((a, b) => b.score - a.score || a.entry.index - b.entry.index).slice(0, limit).map((item) => item.entry);
    rememberKnowledge(results);
    return { mode: "offline", query, results };
  }
  async function knowledgeCodex() {
    if (!offline) return requestWithTransientRetry("/knowledge/codex");
    return { mode: "offline", results: Object.values(read(KNOWLEDGE_CODEX_KEY, {})) };
  }
  function battleDebrief(reportId) {
    if (offline) return Promise.reject(new Error("battle_debrief_requires_online"));
    return requestWithTransientRetry(`/battle-reports/${encodeURIComponent(reportId)}/debrief`);
  }
  function battleReadiness(stageId) {
    if (offline) return Promise.resolve({ mode: "offline", state: "READY", stageId: String(stageId) });
    return requestWithTransientRetry("/battle-readiness", {
      method: "POST",
      body: JSON.stringify({ stage_id: String(stageId) })
    });
  }
  function battleDeployment(stageId, battleReadiness, campaignRoute = null) {
    if (offline) return Promise.resolve(null);
    return requestWithTransientRetry("/battle-deployment", {
      method: "POST",
      body: JSON.stringify({
        stage_id: String(stageId),
        battle_readiness: battleReadiness,
        campaign_route: campaignRoute
      })
    });
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
  async function commendNpc(heroId, input) {
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
    return request(`/npcs/${encodeURIComponent(heroId)}/recollections`, {
      method: "POST",
      body: JSON.stringify(input)
    });
  }
  function npcState(heroId) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/state`); }
  function npcCorrespondence(heroId, limit = 20) { return requestWithTransientRetry(`/npcs/${encodeURIComponent(heroId)}/correspondence?limit=${encodeURIComponent(limit)}`); }
  function organizationPublicNotices() { return requestWithTransientRetry("/organization/public-notices"); }
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
    const pendingKey = `dongzhou-pending-decision-v5:${JSON.stringify([heroId, stageId || "", question, options, memory?.idempotencyKey || "", publicNotice?.messageId || "", contribution?.entryId || "", contributionDossier?.digest || ""])}`;
    const pending = read(pendingKey, null) || { client_request_id: root.crypto.randomUUID(), ...(stageId ? { stage_id: String(stageId) } : {}), question, options: options.map((text, index) => ({ index, text })), topic: "court_decision", ...(memory ? { memory_idempotency_key: memory.idempotencyKey, memory_digest: memory.digest } : {}), ...(publicNotice ? { public_notice_id: publicNotice.messageId, public_notice_digest: publicNotice.digest } : {}), ...(contribution ? { contribution_entry_id: contribution.entryId, contribution_entry_digest: contribution.digest } : {}), ...(contributionDossier ? { contribution_dossier_digest: contributionDossier.digest } : {}) };
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
  function organizationInventory() { return requestWithTransientRetry("/organization/inventory"); }
  function organizationScheduledDuties() { return requestWithTransientRetry("/organization/scheduled-duties"); }
  async function setOrganizationScheduledDutyEnabled(enabled) {
    const saved = read(SCHEDULED_DUTY_STATUS_PENDING_KEY, null);
    const pending = saved?.enabled === Boolean(enabled)
      ? saved
      : { client_request_id: root.crypto.randomUUID(), enabled: Boolean(enabled) };
    write(SCHEDULED_DUTY_STATUS_PENDING_KEY, pending);
    try {
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

  return { initialize, persist, status, searchKnowledge, knowledgeCodex, battleDebrief, battleReadiness, battleDeployment, campaignRoute, stageKnowledge, startKnowledgeQuiz, answerKnowledgeQuiz, verifyKnowledgeQuizSeal, pendingAdviserQuestion, askAdviser, adviserQuestion, feedbackAdviser, decideAdviserGuide, adviserGuide, cancelAdviserGuide, syncNpcs, setNpcInteractionPreference, commendNpc, commendMeritNpc, recallNpc, npcState, npcCorrespondence, organizationPublicNotices, sendNpcMessage, npcSchedule, npcAssignment, generateNpcSchedule, npcThought, npcDecision, createCourtMandate, pendingCourtMandate, resumeCourtMandate, scheduleCourtMandate, acknowledgeCourtMandate, createOrganizationTask, applyOrganizationOrder, organizationTask, organizationRoster, organizationMemberContributions, organizationContributionDossier, organizationPlayerTasks, organizationPlayerContributions, organizationPlayerContributionDossier, organizationInventory, organizationScheduledDuties, setOrganizationScheduledDutyEnabled, organizationLogisticsBriefing, pendingOrganizationInventoryRequisition, requisitionOrganizationInventory, resumeOrganizationInventoryRequisition, acknowledgeOrganizationInventoryRequisition, reviewOrganizationTask, isOffline: () => offline };
});
