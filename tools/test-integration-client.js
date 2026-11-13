"use strict";

const assert = require("assert");

const values = new Map();
global.location = { search: "" };
global.localStorage = {
  getItem: (key) => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
  key: (index) => [...values.keys()][index] || null,
  get length() { return values.size; }
};
let saveVersion = 1;
let organizationAttempts = 0;
const organizationIds = [];
let failNextSave = false;
let conflictNextSave = false;
let decisionAttempts = 0;
const decisionIds = [];
let mandateAttempts = 0;
let mandateResumeAttempts = 0;
let mandateScheduleAttempts = 0;
const mandateScheduleIds = [];
const mandateIds = [];
let saveConflictEvents = 0;
let sessionRequests = 0;
let expireNextSave = false;
let npcStateAttempts = 0;
let npcCorrespondenceAttempts = 0;
let npcMessageAttempts = 0;
const npcMessageIds = [];
let npcScheduleAttempts = 0;
let npcAssignmentAttempts = 0;
let organizationReadAttempts = 0;
let organizationReviewInput = null;
let inventoryRequisitionAttempts = 0;
let inventoryRequisitionResumeAttempts = 0;
let inventoryRequisitionInput = null;
let campaignRouteAttempts = 0;
let knowledgeSearchInput = null;
let knowledgeCodexRequests = 0;
let adviserQuestionInput = null;
let adviserStatusReads = 0;
let adviserFeedbackInput = null;
let organizationResponse = null;
let npcInteractionPreferenceInput = null;
let storedProfile = {};
let saveAttempts = 0;
let sealNextBattleSave = false;
let saveCommittedEvents = 0;
global.CustomEvent = class CustomEvent {
  constructor(type, options = {}) { this.type = type; this.detail = options.detail; }
};
global.dispatchEvent = (event) => {
  if (event.type === "dongzhou-save-conflict") saveConflictEvents += 1;
  if (event.type === "dongzhou-save-committed") saveCommittedEvents += 1;
};
global.fetch = async (url, options = {}) => {
  const body = options.body ? JSON.parse(options.body) : null;
  let status = 200;
  let response;
  if (url.endsWith("/sessions/guest")) {
    sessionRequests += 1;
    response = { playerId: "player-1", expiresIn: 86400 };
  }
  else if (url.endsWith("/save") && options.method === "PUT") {
    saveAttempts += 1;
    if (expireNextSave) {
      expireNextSave = false;
      status = 401;
      response = { error: { code: "invalid_session", message: "expired" } };
    } else if (conflictNextSave) {
      conflictNextSave = false;
      status = 409;
      response = { error: { message: "save conflict" } };
    } else if (failNextSave) {
      failNextSave = false;
      status = 503;
      response = { error: { message: "save unavailable" } };
    } else {
      storedProfile = JSON.parse(JSON.stringify(body.payload));
      if (sealNextBattleSave) {
        sealNextBattleSave = false;
        storedProfile.organization.battleReports[0].kernelReceipt = {
          digest: "b".repeat(64),
          kernel: { state: "SEALED", moduleVersion: "1.4.0" }
        };
      }
      response = { version: ++saveVersion, payload: storedProfile };
    }
  }
  else if (url.endsWith("/save")) response = { version: saveVersion, payload: storedProfile };
  else if (url.endsWith("/knowledge/routes")) {
    campaignRouteAttempts += 1;
    if (campaignRouteAttempts === 1) {
      status = 503;
      response = { error: { code: "knowledge_route_unavailable", message: "retry route" } };
    } else response = { found: true, routeId: "campaign_progression_900001_900002", provisionCost: 2 };
  }
  else if (url.endsWith("/knowledge/search")) {
    knowledgeSearchInput = body;
    response = { mode: "connected", results: [{ id: "dongzhou_stage_001", stageId: "01", retrieval: { graphRelated: true, channels: [{ channel: "graph", normalizedScore: 1 }] }, searchReceipt: { id: "search-receipt", digest: "c".repeat(64) } }] };
  }
  else if (url.endsWith("/knowledge/codex")) {
    knowledgeCodexRequests += 1;
    response = { results: [{ id: "dongzhou_stage_001", stageId: "01", name: "第一回·东郊索命" }] };
  }
  else if (url.endsWith("/adviser/questions") && options.method === "POST") {
    adviserQuestionInput = body;
    response = { state: "PROCESSING", questionId: body.client_request_id, taskId: body.client_request_id };
  }
  else if (/\/adviser\/questions\/[^/]+\/feedback$/.test(url)) {
    adviserFeedbackInput = body;
    response = { state: "RECORDED", questionId: decodeURIComponent(url.split("/").at(-2)), rating: body.rating };
  }
  else if (/\/adviser\/questions\/[^/]+$/.test(url)) {
    adviserStatusReads += 1;
    response = { state: "ANSWERED", questionId: decodeURIComponent(url.split("/").at(-1)), answer: "adviser answer", intentType: "role" };
  }
  else if (url.endsWith("/organization/roster")) {
    response = { organization: { name: "东周军府", growthContribution: 245 }, members: [{ heroId: "DuBo", lifetimeEarned: 80 }] };
  }
  else if (url.endsWith("/organization/inventory")) {
    response = { organizationId: "court", gameServerId: "91001", revision: 7, accounts: [{ resourceKey: "task.execution", balance: 128, version: 3 }] };
  }
  else if (url.endsWith("/organization/inventory/requisitions")) {
    inventoryRequisitionAttempts += 1;
    inventoryRequisitionInput = body;
    response = {
      state: "REQUIRES_ACTION",
      requestId: body.client_request_id,
      stageId: body.stage_id,
      requisition: { id: `dongzhou:requisition:player:${body.client_request_id}`, units: body.units, effect: { provisions: 12 }, digest: "d".repeat(64), state: "DRAFT" },
      action: { actionId: "00000000-0000-4000-8000-000000000088", code: "approve_inventory_requisition", type: "confirmation" }
    };
  }
  else if (/\/organization\/inventory\/requisitions\/[^/]+\/resume$/.test(url)) {
    inventoryRequisitionResumeAttempts += 1;
    const requisitionId = decodeURIComponent(url.split("/").at(-2));
    const requestId = requisitionId.split(":").at(-1);
    response = body.decision === "REJECT" ? {
      state: "REJECTED", requestId, stageId: "01", requisition: { id: requisitionId, state: "REJECTED" }
    } : {
      state: "COMPLETED", requestId, stageId: "01", requisition: { id: requisitionId, state: "COMPLETED" },
      inventoryDebit: { entryId: "entry-1", resourceKey: "task.execution", delta: -20, balanceAfter: 108, accountVersion: 4, inventoryRevision: 8 },
      effect: { provisions: 12 }
    };
  }
  else if (url.endsWith("/npcs/interaction-preference")) {
    npcInteractionPreferenceInput = body;
    response = { enabled: body.enabled, source: "dongzhou-player-settings", updatedAt: "2026-11-11T12:00:00Z" };
  }
  else if (url.endsWith("/court/mandates")) {
    mandateAttempts += 1;
    mandateIds.push(body.client_request_id);
    if (mandateAttempts === 1) {
      status = 503;
      response = { error: { code: "knowledge_unavailable", message: "retry mandate" } };
    } else response = { state: "REQUIRES_ACTION", mandate: { id: `dongzhou:player:${body.client_request_id}`, digest: "a".repeat(64), state: "DRAFT" }, action: { actionId: "00000000-0000-4000-8000-000000000099", code: "seal_court_mandate", type: "confirmation" } };
  }
  else if (/\/court\/mandates\/[^/]+\/resume$/.test(url)) {
    mandateResumeAttempts += 1;
    const state = body.decision === "APPROVE" ? "ISSUED" : body.decision === "REVISE" ? "RETURNED" : "REJECTED";
    response = { state, mandate: { id: decodeURIComponent(url.split("/").at(-2)), digest: "a".repeat(64), state } };
  }
  else if (/\/court\/mandates\/[^/]+\/schedule$/.test(url)) {
    mandateScheduleAttempts += 1;
    mandateScheduleIds.push(body.client_request_id);
    if (mandateScheduleAttempts === 1) {
      status = 503;
      response = { error: { code: "ainpc_schedule_interruption_unavailable", message: "retry schedule interruption" } };
    } else {
      const mandateId = decodeURIComponent(url.split("/").at(-2));
      response = { state: "COMPLETED", scheduleReceipt: { requestId: body.client_request_id, mandateId, mandateDigest: body.mandate_digest, heroId: "DuBo", npcId: "42", eventId: `dongzhou-mandate-${body.mandate_digest.slice(0, 32)}`, action: "insert_today", scheduleId: `dongzhou-mandate-${body.mandate_digest.slice(0, 32)}`, scheduleName: "临时军令", duplicate: false, reason: null, appliedAt: "0771-01-01 14:00:00", digest: "d".repeat(64) } };
    }
  }
  else if (url.endsWith("/organization/tasks")) {
    organizationAttempts += 1;
    organizationIds.push(body.client_request_id);
    if (organizationAttempts === 1) {
      status = 503;
      response = { error: { code: "organization_unavailable", message: "retry" } };
    } else response = organizationResponse || { state: "ACCEPTED", taskId: "task-1" };
  } else if (/\/organization\/tasks\/[^/]+\/review$/.test(url)) {
    organizationReviewInput = body;
    response = { state: body.decision === "ACCEPT" ? "ACCEPTED" : "CENSURED", review: { settlementId: "settlement-1", closureDigest: "c".repeat(64), decision: body.decision } };
  } else if (/\/organization\/tasks\/[^/]+$/.test(url)) {
    organizationReadAttempts += 1;
    if (organizationReadAttempts === 1) {
      status = 504;
      response = { error: { code: "organization_timeout", message: "temporarily unavailable" } };
    } else response = { result: { data: { state: "SUCCEEDED" } } };
  } else if (url.includes("/decisions")) {
    decisionAttempts += 1;
    decisionIds.push(body.client_request_id);
    if (decisionAttempts === 1) {
      status = 503;
      response = { error: { message: "decision unavailable" } };
    } else response = { decision: { data: { selected_index: 0 } } };
  } else if (/\/npcs\/[^/]+\/state$/.test(url)) {
    npcStateAttempts += 1;
    if (npcStateAttempts === 1) {
      status = 503;
      response = { error: { code: "npc_unavailable", message: "temporarily unavailable" } };
    } else response = { emotion: { data: { dominant: { emotion_type: "calm" } } } };
  } else if (/\/npcs\/[^/]+\/correspondence\?limit=/.test(url)) {
    npcCorrespondenceAttempts += 1;
    response = { messages: [{ messageId: "message-1", digest: "d".repeat(64) }] };
  } else if (/\/npcs\/[^/]+\/messages$/.test(url)) {
    npcMessageAttempts += 1;
    npcMessageIds.push(body.client_request_id);
    if (npcMessageAttempts === 1) {
      status = 503;
      response = { error: { code: "ainpc_unavailable", message: "retry message" } };
    } else response = { state: "ACCEPTED", taskId: "playerchat-1" };
  } else if (/\/npcs\/[^/]+\/schedule$/.test(url) && !options.method) {
    npcScheduleAttempts += 1;
    if (npcScheduleAttempts === 1) {
      status = 503;
      response = { error: { code: "schedule_unavailable", message: "temporarily unavailable" } };
    } else response = { schedule: { data: { schedules: [] } } };
  } else if (/\/npcs\/[^/]+\/assignments\/[^/?]+\?stage_id=/.test(url)) {
    npcAssignmentAttempts += 1;
    if (npcAssignmentAttempts === 1) {
      status = 503;
      response = { error: { code: "assignment_unavailable", message: "temporarily unavailable" } };
    } else response = { assignment: { planId: "plan-1", eventId: "event-supply", heroId: "DuBo" } };
  } else response = {};
  return { ok: status < 400, status, json: async () => response };
};

const client = require("../web-game/integration-client.js");

(async () => {
  const initialized = await client.initialize({ completed: [] });
  assert.strictEqual(initialized.connected, true);
  await client.persist({ completed: ["01"] });
  expireNextSave = true;
  await client.persist({ completed: ["01", "renewed"] });
  assert.strictEqual(sessionRequests, 2);
  failNextSave = true;
  await assert.rejects(() => client.persist({ completed: ["01", "02"] }), /save unavailable/);
  await client.persist({ completed: ["01", "02", "03"] });
  const battleProfile = { organization: { battleReports: [{ id: "battle:01:test" }] } };
  sealNextBattleSave = true;
  await client.persist(battleProfile);
  assert.strictEqual(battleProfile.organization.battleReports[0].kernelReceipt.digest, "b".repeat(64));
  assert.strictEqual(saveCommittedEvents, 1);
  const route = await client.campaignRoute({ from_stage_id: "01", from_stage_index: 1, to_stage_id: "02", to_stage_index: 2 });
  assert.strictEqual(route.provisionCost, 2);
  assert.strictEqual(campaignRouteAttempts, 2);
  const knowledge = await client.searchKnowledge("杜伯 东郊", 6, "01");
  assert.strictEqual(knowledgeSearchInput.stage_id, "01");
  assert.match(knowledgeSearchInput.client_request_id, /^[0-9a-f-]{36}$/);
  assert.strictEqual(knowledge.results[0].retrieval.graphRelated, true);
  const codex = await client.knowledgeCodex();
  assert.strictEqual(codex.results[0].name, "第一回·东郊索命");
  assert.strictEqual(knowledgeCodexRequests, 1);
  const adviser = await client.askAdviser({ question: "key people?", stage_id: "01", stage_title: "stage one", stage_index: 1 });
  assert.strictEqual(adviser.state, "PROCESSING");
  assert.match(adviserQuestionInput.client_request_id, /^[0-9a-f-]{36}$/);
  assert.strictEqual(client.pendingAdviserQuestion().input.stage_id, "01");
  const adviserAnswer = await client.adviserQuestion(adviser.questionId);
  assert.strictEqual(adviserAnswer.answer, "adviser answer");
  assert.strictEqual(adviserStatusReads, 1);
  const adviserFeedback = await client.feedbackAdviser(adviser.questionId, "accurate");
  assert.strictEqual(adviserFeedback.state, "RECORDED");
  assert.strictEqual(adviserFeedbackInput.rating, "accurate");
  assert.match(adviserFeedbackInput.action_id, /^[0-9a-f-]{36}$/);
  const roster = await client.organizationRoster();
  assert.strictEqual(roster.organization.growthContribution, 245);
  assert.strictEqual(roster.members[0].heroId, "DuBo");
  const inventory = await client.organizationInventory();
  assert.strictEqual(inventory.accounts[0].balance, 128);
  assert.strictEqual(inventory.revision, 7);
  const requisition = await client.requisitionOrganizationInventory({ units: 20, stage_id: "01" });
  assert.strictEqual(requisition.state, "REQUIRES_ACTION");
  assert.strictEqual(inventoryRequisitionInput.units, 20);
  assert.strictEqual(client.pendingOrganizationInventoryRequisition().result.action.actionId, requisition.action.actionId);
  const approvedRequisition = await client.resumeOrganizationInventoryRequisition(requisition.requisition.id, requisition.action.actionId, "APPROVE");
  assert.strictEqual(approvedRequisition.state, "COMPLETED");
  assert.strictEqual(approvedRequisition.effect.provisions, 12);
  assert.strictEqual(inventoryRequisitionAttempts, 1);
  assert.strictEqual(inventoryRequisitionResumeAttempts, 1);
  client.acknowledgeOrganizationInventoryRequisition(approvedRequisition.requestId);
  assert.strictEqual(client.pendingOrganizationInventoryRequisition(), null);
  const interactionPreference = await client.setNpcInteractionPreference(false);
  assert.strictEqual(interactionPreference.enabled, false);
  assert.deepStrictEqual(npcInteractionPreferenceInput, { enabled: false });
  await client.npcState("DuBo");
  const correspondence = await client.npcCorrespondence("DuBo", 12);
  await client.npcSchedule("DuBo");
  const assignment = await client.npcAssignment("DuBo", "supply", "01");
  assert.strictEqual(npcStateAttempts, 2);
  assert.strictEqual(npcCorrespondenceAttempts, 1);
  assert.strictEqual(correspondence.messages[0].messageId, "message-1");
  await assert.rejects(() => client.sendNpcMessage("DuBo", "北路军粮如何？"), /retry message/);
  const sentMessage = await client.sendNpcMessage("DuBo", "北路军粮如何？");
  assert.strictEqual(sentMessage.taskId, "playerchat-1");
  assert.strictEqual(npcMessageIds[0], npcMessageIds[1]);
  assert.strictEqual(npcScheduleAttempts, 2);
  assert.strictEqual(npcAssignmentAttempts, 2);
  assert.strictEqual(assignment.assignment.eventId, "event-supply");
  await assert.rejects(() => client.npcDecision("DuBo", "test", ["one", "two"]), /decision unavailable/);
  await client.npcDecision("DuBo", "test", ["one", "two"]);
  assert.strictEqual(decisionIds[0], decisionIds[1]);
  const mandateInput = { stage_id: "01", stage_title: "东郊索命", hero_id: "DuBo", knowledge_id: "dongzhou_stage_001", evidence_source_index: 0, schedule_plan_id: "plan-1", schedule_event_id: "event-supply", council_request_id: decisionIds[1], decision_index: 0, task_type: "supply" };
  await assert.rejects(() => client.createCourtMandate(mandateInput), /retry mandate/);
  const mandate = await client.createCourtMandate(mandateInput);
  assert.strictEqual(mandateIds[0], mandateIds[1]);
  assert.strictEqual(mandate.state, "REQUIRES_ACTION");
  assert.strictEqual(client.pendingCourtMandate().result.action.actionId, mandate.action.actionId);
  assert.ok([...values.keys()].some((key) => key.startsWith("dongzhou-pending-mandate-v1:")));
  const approvedMandate = await client.resumeCourtMandate(mandate.mandate.id, mandate.action.actionId, "APPROVE");
  assert.strictEqual(approvedMandate.state, "ISSUED");
  assert.strictEqual(client.pendingCourtMandate().result.state, "ISSUED");
  assert.strictEqual(mandateResumeAttempts, 1);
  await assert.rejects(() => client.scheduleCourtMandate(approvedMandate.mandate.id, approvedMandate.mandate.digest), /retry schedule interruption/);
  const scheduledMandate = await client.scheduleCourtMandate(approvedMandate.mandate.id, approvedMandate.mandate.digest);
  assert.strictEqual(scheduledMandate.scheduleReceipt.scheduleName, "临时军令");
  assert.strictEqual(mandateScheduleIds[0], mandateScheduleIds[1]);
  client.acknowledgeCourtMandate(mandateInput);
  assert.ok(![...values.keys()].some((key) => key.startsWith("dongzhou-pending-mandate-v1:")));
  const returnedDraft = await client.createCourtMandate({ ...mandateInput, hero_id: "ZuoRu" });
  const returnedMandate = await client.resumeCourtMandate(returnedDraft.mandate.id, returnedDraft.action.actionId, "REVISE");
  assert.strictEqual(returnedMandate.state, "RETURNED");
  assert.strictEqual(client.pendingCourtMandate(), null);
  const revisedDraft = await client.createCourtMandate({ ...mandateInput, hero_id: "ZuoRu" });
  assert.strictEqual(revisedDraft.state, "REQUIRES_ACTION");
  assert.strictEqual(revisedDraft.mandate.id !== returnedDraft.mandate.id, true);
  const revisedRequest = JSON.parse([...values.entries()].find(([key]) => key.startsWith("dongzhou-pending-mandate-v1:"))[1]).input;
  assert.strictEqual(revisedRequest.supersedes_mandate_id, returnedDraft.mandate.id);
  assert.strictEqual(revisedRequest.supersedes_mandate_digest, returnedDraft.mandate.digest);
  client.acknowledgeCourtMandate({ ...mandateInput, hero_id: "ZuoRu" });
  const input = { task_type: "supply", assignee_hero_id: "DuBo", stage_id: "01", stage_title: "东郊索命", brief: "test", parameters: {} };
  await assert.rejects(() => client.createOrganizationTask(input), /retry/);
  const accepted = await client.createOrganizationTask(input);
  assert.strictEqual(accepted.taskId, "task-1");
  assert.strictEqual(organizationIds.length, 2);
  assert.strictEqual(organizationIds[0], organizationIds[1]);
  await client.organizationTask("task-1");
  assert.strictEqual(organizationReadAttempts, 2);
  const reviewed = await client.reviewOrganizationTask("task-1", { action_id: "00000000-0000-4000-8000-000000000021", decision: "ACCEPT" });
  assert.strictEqual(reviewed.state, "ACCEPTED");
  assert.strictEqual(organizationReviewInput.decision, "ACCEPT");
  assert.strictEqual([...values.keys()].some((key) => key.startsWith("dongzhou-pending-task-v1:")), true, "Acceptance remains durable until the binding is saved");
  await client.persist({ organization: { tasks: [{ remoteResult: accepted.taskId }] } });
  assert.strictEqual([...values.keys()].some((key) => key.startsWith("dongzhou-pending-task-v1:")), false);
  organizationResponse = { state: "REJECTED", error: { code: "order_rejected", message: "官署拒绝此令" } };
  await assert.rejects(() => client.createOrganizationTask(input), /官署拒绝此令/);
  assert.strictEqual([...values.keys()].some((key) => key.startsWith("dongzhou-pending-task-v1:")), false);
  organizationResponse = { state: "ACCEPTED" };
  await assert.rejects(() => client.createOrganizationTask(input), /尚未确认受理/);
  const uncertainId = organizationIds.at(-1);
  assert.ok([...values.keys()].some((key) => key.startsWith("dongzhou-pending-task-v1:")));
  organizationResponse = null;
  await client.createOrganizationTask(input);
  assert.strictEqual(organizationIds.at(-1), uncertainId, "Uncertain acceptance must retain its idempotency key");
  await client.persist({ organization: { tasks: [{ remoteResult: "task-1" }] } });
  const orderProfile = { organization: { month: 1, tasks: [], taskSequence: 0, members: [{ id: "DuBo", fatigue: 0 }], history: [], knowledge: [] }, campaignResources: { provisions: 100 } };
  await client.persist(orderProfile);
  const localTask = { id: "dz-1-1-123", type: "supply", assigneeId: "DuBo", assigneeName: "杜伯", name: "转运军粮", cost: 8, status: "active" };
  organizationResponse = { state: "ACCEPTED", taskId: "task-recovered" };
  const receipt = await client.createOrganizationTask(input, localTask);
  const attemptsAtCrash = organizationAttempts;
  // Simulate closing the page after acceptance but before saving the task binding.
  delete require.cache[require.resolve("../web-game/integration-client.js")];
  const restoredClient = require("../web-game/integration-client.js");
  const recovered = await restoredClient.initialize(orderProfile);
  assert.strictEqual(organizationAttempts, attemptsAtCrash, "Accepted order must recover without creating a second remote order");
  assert.strictEqual(recovered.profile.organization.tasks[0].remoteResult, receipt.taskId);
  assert.strictEqual(recovered.profile.campaignResources.provisions, 92);
  restoredClient.applyOrganizationOrder(recovered.profile, localTask, receipt);
  assert.strictEqual(recovered.profile.campaignResources.provisions, 92, "Recovery must charge exactly once");
  const latest = JSON.parse(JSON.stringify(orderProfile));
  latest.organization.month = 2;
  latest.organization.knowledge.push({ id: "concurrent-knowledge" });
  restoredClient.applyOrganizationOrder(latest, localTask, receipt);
  assert.strictEqual(latest.organization.month, 2);
  assert.strictEqual(latest.organization.knowledge[0].id, "concurrent-knowledge");
  conflictNextSave = true;
  const attemptsBeforeConflict = saveAttempts;
  const queued = [client.persist({ completed: ["conflict"] }), client.persist({ completed: ["queued-1"] }), client.persist({ completed: ["queued-2"] })];
  const failures = await Promise.allSettled(queued);
  assert.ok(failures.every((entry) => entry.status === "rejected"));
  assert.strictEqual(saveAttempts - attemptsBeforeConflict, 1, "Queued snapshots must not write after a conflict");
  await assert.rejects(() => client.persist({ completed: ["blocked"] }), /save_conflict_reload_required/);
  assert.strictEqual(saveConflictEvents, 1);
  console.log(JSON.stringify({ result: "PASS", saveVersion, organizationAttempts, organizationReadAttempts, campaignRouteAttempts, decisionAttempts, mandateAttempts, mandateResumeAttempts, mandateScheduleAttempts, npcStateAttempts, npcScheduleAttempts, npcAssignmentAttempts, saveConflictEvents }));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
