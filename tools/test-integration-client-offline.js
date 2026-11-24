"use strict";

const assert = require("assert");

const values = new Map();
const fetchedUrls = [];
const serviceSources = {
  schemaVersion: 1,
  services: {
    knowledge: { sourceBranch: "main", sourceRevision: "45afa2ffe77faea0622e8d3ed3f2b69c0cab9c56", integrationRevision: "5fd67de575113b3f1238149d971106c97eed5c9a" },
    aiNpc: { sourceBranch: "develop", sourceRevision: "82b7a7e02bccceb283563cee9929e29610d6ebf5", integrationRevision: "f2235369e1da5e1e64aa2969ce29bef553f03ee3" },
    orgFlow: { sourceBranch: "develop", sourceRevision: "8b1049e965719d31c51772dde799737e9b92e918", integrationRevision: "fbfc803b264c2c1e1dffe80c8da1bb5caa676cc3" },
    nexusKernel: { sourceBranch: "develop", sourceRevision: "190abb1fa889e40aa08dbc6efaaba6fe4940ca6d", integrationRevision: "4f1915b45eadf8608308f7131173d1d60f6c5270" },
  },
};
global.location = { search: "?offline=1" };
global.localStorage = {
  getItem: (key) => values.has(key) ? values.get(key) : null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
  key: (index) => [...values.keys()][index] || null,
  get length() { return values.size; },
};
global.fetch = async (url) => {
  fetchedUrls.push(String(url));
  return ({
  ok: true,
  json: async () => String(url).endsWith("service-sources.json") ? serviceSources : ({
    entries: [{
      id: "dongzhou_stage_001",
      index: 1,
      stageId: "01",
      name: "Chapter One",
      summary: "An archived account of the first court crisis.",
      content: "A deliberately long source body that must not enter localStorage.",
      people: ["Du Bo"],
      keywords: ["court crisis"],
      sources: [{ work: "Dongzhou Chronicle", tier: "primary", scope: "first crisis", url: "https://example.test/source" }],
      sourceDetails: [{ work: "Dongzhou Chronicle", tier: "primary", scope: "first crisis" }],
    }, {
      id: "dongzhou_stage_002", index: 2, stageId: "02", name: "Chapter Two", people: ["King You"]
    }, {
      id: "dongzhou_stage_003", index: 3, stageId: "03", name: "Chapter Three", people: ["Marquis Shen"]
    }, {
      id: "dongzhou_stage_004", index: 4, stageId: "04", name: "Chapter Four", people: ["Duke Zheng"]
    }],
  }),
  });
};

const client = require("../web-game/integration-client.js");

(async () => {
  const localProfile = {
    formation: "balanced",
    stageVanguards: { "02": "DuBo" },
    campaignResources: { provisions: 84, morale: 67 },
    organization: {
      remoteId: "dongzhou-local-court",
      members: [{ id: "DuBo" }, { id: "ZuoRu" }],
      remoteRoster: { organization: { hierarchyVersion: 1 } },
      localInventory: {
        revision: 3,
        accounts: [
          { resourceKey: "task.execution", balance: 60, version: 3 },
          { resourceKey: "guild.capacity", balance: 12, version: 1 },
        ],
      },
    },
  };
  await client.initialize(localProfile);
  const search = await client.searchKnowledge("court", 6, "01");
  assert.strictEqual(search.results.length, 1);
  const codex = await client.knowledgeCodex();
  assert.strictEqual(codex.mode, "offline");
  assert.strictEqual(codex.results[0].name, "Chapter One");
  assert.strictEqual(codex.results[0].content, undefined);
  assert.deepStrictEqual(codex.results[0].people, ["Du Bo"]);
  assert.ok(values.has("dongzhou-knowledge-codex-v1"));

  const commendation = await client.commendNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" });
  assert.strictEqual(commendation.state, "COMPLETED");
  assert.strictEqual(commendation.commendation.kernel.module, "dongzhou_npc_commendation");
  assert.strictEqual(commendation.commendation.affectionDelta, 2);
  assert.strictEqual((await client.commendNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" })).replayed, true);
  const commendationKey = [...values.keys()].find((key) => key.startsWith("dongzhou-local-npc-commendation-v1:"));
  const cleanCommendation = values.get(commendationKey);
  const forgedCommendation = JSON.parse(cleanCommendation);
  forgedCommendation.commendation.digest = "0".repeat(64);
  values.set(commendationKey, JSON.stringify(forgedCommendation));
  await assert.rejects(
    client.commendNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" }),
    /npc_commendation_seal_invalid/
  );
  values.set(commendationKey, cleanCommendation);
  await assert.rejects(
    client.commendNpc("DuBo", { stage_id: "01", knowledge_id: "forged" }),
    /npc_history_knowledge_invalid|npc_commendation_conflict/
  );
  const recollection = await client.recallNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" });
  assert.strictEqual(recollection.state, "COMPLETED");
  assert.strictEqual(recollection.recollection.kernel.module, "dongzhou_npc_recollection");
  assert.strictEqual(recollection.recollection.memoryReceipt.digest, recollection.recollection.memoryDigest);
  assert.strictEqual((await client.recallNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" })).replayed, true);
  const recollectionKey = [...values.keys()].find((key) => key.startsWith("dongzhou-local-npc-recollection-v1:"));
  const cleanRecollection = values.get(recollectionKey);
  const forgedRecollection = JSON.parse(cleanRecollection);
  forgedRecollection.recollection.memoryReceipt.content = "forged memory";
  values.set(recollectionKey, JSON.stringify(forgedRecollection));
  await assert.rejects(
    client.recallNpc("DuBo", { stage_id: "01", knowledge_id: "dongzhou_stage_001" }),
    /npc_recollection_seal_invalid/
  );
  values.set(recollectionKey, cleanRecollection);
  await assert.rejects(
    client.recallNpc("Unknown", { stage_id: "01", knowledge_id: "dongzhou_stage_001" }),
    /npc_not_in_local_organization/
  );
  const inventory = await client.organizationInventory();
  assert.strictEqual(inventory.revision, 3);
  assert.strictEqual(inventory.accounts.find((account) => account.resourceKey === "task.execution").balance, 60);
  const briefing = await client.organizationLogisticsBriefing("DuBo", { stage_id: "01", stage_title: "Chapter One" });
  assert.strictEqual(briefing.state, "COMPLETED");
  assert.strictEqual(briefing.briefingReceipt.kernel.module, "dongzhou_logistics_briefing");
  assert.strictEqual(briefing.briefingReceipt.inventoryRevision, 3);
  assert.strictEqual(briefing.briefingReceipt.exchange.availableLots, 3);
  assert.strictEqual(briefing.briefingReceipt.campaignResources.provisions, 84);
  assert.strictEqual(briefing.briefingReceipt.ainpcDelivery.mode, "IN_PROCESS");
  assert.strictEqual((await client.organizationLogisticsBriefing("DuBo", { stage_id: "01", stage_title: "Chapter One" })).replayed, true);
  const briefingKey = [...values.keys()].find((key) => key.startsWith("dongzhou-local-logistics-briefing-v1:"));
  const cleanBriefing = values.get(briefingKey);
  const forgedBriefing = JSON.parse(cleanBriefing);
  forgedBriefing.result.briefingReceipt.exchange.availableLots = 999;
  values.set(briefingKey, JSON.stringify(forgedBriefing));
  await assert.rejects(
    client.organizationLogisticsBriefing("DuBo", { stage_id: "01", stage_title: "Chapter One" }),
    /organization_logistics_briefing_seal_invalid/
  );
  values.set(briefingKey, cleanBriefing);
  localProfile.organization.logisticsBriefings = [briefing.briefingReceipt];
  await client.persist(localProfile);
  const thought = await client.npcThought("DuBo", {
    stage_id: "01",
    stage_title: "Chapter One",
    knowledge_id: "dongzhou_stage_001",
    evidence_source_index: 0,
    task_type: "supply",
    logistics_briefing_request_id: briefing.briefingReceipt.requestId,
    logistics_briefing_digest: briefing.briefingReceipt.digest,
  });
  assert.strictEqual(thought.state, "COMPLETED");
  assert.strictEqual(thought.thoughtReceipt.thought.hasThought, true);
  assert.strictEqual(thought.thoughtReceipt.logisticsBriefing.digest, briefing.briefingReceipt.digest);
  assert.match(thought.thoughtReceipt.digest, /^[0-9a-f]{64}$/);
  assert.strictEqual((await client.npcThought("DuBo", {
    stage_id: "01", stage_title: "Chapter One", knowledge_id: "dongzhou_stage_001", evidence_source_index: 0, task_type: "supply",
    logistics_briefing_request_id: briefing.briefingReceipt.requestId, logistics_briefing_digest: briefing.briefingReceipt.digest,
  })).replayed, true);
  const thoughtKey = [...values.keys()].find((key) => key.startsWith("dongzhou-pending-npc-thought-v1:"));
  const cleanThought = values.get(thoughtKey);
  const forgedThought = JSON.parse(cleanThought);
  forgedThought.result.thoughtReceipt.digest = "0".repeat(64);
  values.set(thoughtKey, JSON.stringify(forgedThought));
  await assert.rejects(
    client.npcThought("DuBo", { stage_id: "01", stage_title: "Chapter One", knowledge_id: "dongzhou_stage_001", evidence_source_index: 0, task_type: "supply", logistics_briefing_request_id: briefing.briefingReceipt.requestId, logistics_briefing_digest: briefing.briefingReceipt.digest }),
    /npc_thought_seal_invalid/
  );
  values.set(thoughtKey, cleanThought);
  localProfile.organization.thoughts = [thought.thoughtReceipt];
  await client.persist(localProfile);
  const localMemory = { ...recollection.recollection.memoryReceipt, sourceProvenance: recollection.recollection.sourceProvenance };
  const decisionOptions = ["Hold", "Advance", thought.thoughtReceipt.councilProposal];
  const decision = await client.npcDecision("DuBo", "What should the court do?", decisionOptions, "01", localMemory);
  assert.strictEqual(decision.state, "COMPLETED");
  assert.strictEqual(decision.decision.data.text, thought.thoughtReceipt.councilProposal);
  assert.strictEqual(decision.dialogueReceipt.state, "RECORDED");
  assert.strictEqual((await client.npcDecision("DuBo", "What should the court do?", decisionOptions, "01", localMemory)).replayed, true);

  const inventoryBeforeDraft = await client.organizationInventory();
  const requisitionDraft = await client.requisitionOrganizationInventory({ units: 20, stage_id: "01" });
  assert.strictEqual(requisitionDraft.state, "REQUIRES_ACTION");
  assert.strictEqual(requisitionDraft.requisition.state, "DRAFT");
  assert.strictEqual(requisitionDraft.requisition.effect.provisions, 12);
  assert.strictEqual((await client.organizationInventory()).accounts.find((account) => account.resourceKey === "task.execution").balance, 60);
  await assert.rejects(
    client.resumeOrganizationInventoryRequisition(requisitionDraft.requisition.id, global.crypto.randomUUID(), "APPROVE"),
    /organization_inventory_requisition_action_mismatch/
  );
  const cleanRequisitionJournal = values.get("dongzhou-pending-inventory-requisition-v1");
  const forgedRequisitionJournal = JSON.parse(cleanRequisitionJournal);
  forgedRequisitionJournal.result.requisition.digest = "0".repeat(64);
  values.set("dongzhou-pending-inventory-requisition-v1", JSON.stringify(forgedRequisitionJournal));
  await assert.rejects(
    client.resumeOrganizationInventoryRequisition(requisitionDraft.requisition.id, requisitionDraft.action.actionId, "APPROVE"),
    /organization_inventory_requisition_seal_invalid/
  );
  values.set("dongzhou-pending-inventory-requisition-v1", cleanRequisitionJournal);
  const approvedRequisition = await client.resumeOrganizationInventoryRequisition(
    requisitionDraft.requisition.id,
    requisitionDraft.action.actionId,
    "APPROVE"
  );
  assert.strictEqual(approvedRequisition.state, "COMPLETED");
  assert.strictEqual(approvedRequisition.inventoryDebit.balanceAfter, 40);
  assert.strictEqual(approvedRequisition.inventoryDebit.inventoryRevision, inventoryBeforeDraft.revision + 1);
  assert.strictEqual((await client.resumeOrganizationInventoryRequisition(
    requisitionDraft.requisition.id,
    requisitionDraft.action.actionId,
    "APPROVE"
  )).replayed, true);
  client.acknowledgeOrganizationInventoryRequisition(approvedRequisition.requestId);
  assert.strictEqual(client.pendingOrganizationInventoryRequisition(), null);

  const rejectedDraft = await client.requisitionOrganizationInventory({ units: 20, stage_id: "01" });
  const rejectedRequisition = await client.resumeOrganizationInventoryRequisition(
    rejectedDraft.requisition.id,
    rejectedDraft.action.actionId,
    "REJECT"
  );
  assert.strictEqual(rejectedRequisition.state, "REJECTED");
  assert.strictEqual(rejectedRequisition.requisition.kernel.state, "REJECTED");
  assert.strictEqual((await client.organizationInventory()).accounts.find((account) => account.resourceKey === "task.execution").balance, 60);
  client.acknowledgeOrganizationInventoryRequisition(rejectedRequisition.requestId);

  const battlePlan = {
    formation: "balanced",
    vanguardHeroId: "DuBo",
    supportIds: ["support-local-1"],
    supportEffect: { provisions: 8, morale: 3, attack: 0.1, defense: 0.05, recon: 1 },
  };
  await client.persist(localProfile);
  const route = await client.campaignRoute({
    from_stage_id: "01", from_stage_index: 1, to_stage_id: "02", to_stage_index: 2, route_method: "npc_dialog",
  });
  assert.strictEqual(route.mode, "standalone");
  assert.strictEqual(route.options.length, 3);
  assert.strictEqual(route.knowledgeWitnesses.from.knowledgeIds[0], "dongzhou_stage_001");
  assert.strictEqual(route.knowledgeWitnesses.to.knowledgeIds[0], "dongzhou_stage_002");
  assert.match(route.localRouteDigest, /^[0-9a-f]{64}$/);
  const readiness = await client.battleReadiness("02", battlePlan);
  assert.strictEqual(readiness.mode, "standalone");
  assert.strictEqual(readiness.kernel.module, "dongzhou_battle_readiness");
  assert.strictEqual(readiness.kernel.moduleVersion, "1.3.0");
  assert.deepStrictEqual(readiness.organization.activeHeroIds, ["DuBo", "ZuoRu"]);
  assert.deepStrictEqual(readiness.aiNpc.readyHeroIds, readiness.organization.activeHeroIds);
  const deployment = await client.battleDeployment("02", readiness, route, battlePlan);
  assert.strictEqual(deployment.state, "AUTHORIZED");
  assert.strictEqual(deployment.kernel.module, "dongzhou_battle_deployment");
  assert.strictEqual(deployment.kernel.moduleVersion, "1.3.0");
  assert.strictEqual(deployment.routeDigest, route.localRouteDigest);
  assert.deepStrictEqual(deployment.battlePlan, battlePlan);
  assert.strictEqual(await client.verifyBattleDeployment("02", readiness, deployment, battlePlan, route), true);
  await assert.rejects(
    client.verifyBattleDeployment("02", readiness, { ...deployment, digest: "0".repeat(64) }, battlePlan, route),
    /battle_deployment_seal_invalid/
  );
  await assert.rejects(
    client.battleDeployment("02", { ...readiness, knowledge: { ...readiness.knowledge, digest: "0".repeat(64) } }, route, battlePlan),
    /battle_readiness_.*_invalid/
  );
  await assert.rejects(
    client.battleDeployment("02", readiness, { ...route, localRouteDigest: "0".repeat(64) }, battlePlan),
    /campaign_route_seal_invalid/
  );
  localProfile.organization.battleReports = [{
    id: deployment.reportId,
    stageId: "02",
    stageTitle: "Second stage",
    won: true,
    turns: 7,
    ownLosses: 1,
    terminalReason: "victory",
    campaignRoute: route,
    battleReadiness: readiness,
    battleDeployment: deployment,
    battlePlan,
  }];
  await client.persist(localProfile);
  const debrief = await client.battleDebrief(deployment.reportId);
  assert.strictEqual(debrief.mode, "standalone");
  assert.strictEqual(debrief.kernel.module, "dongzhou_battle_debrief");
  assert.strictEqual(debrief.kernel.moduleVersion, "1.2.0");
  assert.deepStrictEqual(debrief.organizationTasks.map((entry) => entry.taskId), battlePlan.supportIds);
  assert.deepStrictEqual(debrief.participants.map((entry) => entry.heroId), ["DuBo", "ZuoRu"]);
  assert.match(debrief.digest, /^[0-9a-f]{64}$/);

  const questionId = "00000000-0000-4000-8000-000000000501";
  const started = await client.startKnowledgeQuiz("01", questionId);
  assert.strictEqual(started.mode, "offline");
  assert.strictEqual(started.question.options.length, 4);
  assert.ok(!JSON.stringify(started).includes("correctIndex"));
  const quizKey = [...values.keys()].find((key) => key.endsWith(questionId));
  assert.ok(quizKey);
  assert.ok(!values.get(quizKey).includes("correctIndex"));
  assert.strictEqual((await client.startKnowledgeQuiz("01", questionId)).replayed, true);
  const pendingRecord = values.get(quizKey);
  const tamperedQuestion = JSON.parse(pendingRecord);
  tamperedQuestion.ready.question.prompt = "forged prompt";
  values.set(quizKey, JSON.stringify(tamperedQuestion));
  await assert.rejects(client.startKnowledgeQuiz("01", questionId), /knowledge_quiz_source_invalid/);
  values.set(quizKey, pendingRecord);
  const correctIndex = started.question.options.indexOf("Du Bo");
  assert.ok(correctIndex >= 0);
  const answered = await client.answerKnowledgeQuiz(questionId, started.action.actionId, correctIndex);
  assert.strictEqual(answered.correct, true);
  assert.strictEqual(answered.score, 10);
  assert.strictEqual(answered.receipt.kernel.module, "dongzhou_knowledge_tournament");
  assert.strictEqual(answered.receipt.kernel.state, "SEALED");
  const verified = await client.verifyKnowledgeQuizSeal(questionId);
  assert.strictEqual(verified.verified, true);
  assert.strictEqual(verified.digest, answered.receipt.digest);
  assert.strictEqual((await client.answerKnowledgeQuiz(questionId, started.action.actionId, correctIndex)).replayed, true);
  await assert.rejects(
    client.answerKnowledgeQuiz(questionId, started.action.actionId, (correctIndex + 1) % 4),
    /knowledge_quiz_already_answered/
  );
  const completedRecord = values.get(quizKey);
  const tampered = JSON.parse(completedRecord);
  tampered.result.receipt.digest = "0".repeat(64);
  values.set(quizKey, JSON.stringify(tampered));
  await assert.rejects(client.verifyKnowledgeQuizSeal(questionId), /knowledge_quiz_seal_invalid/);
  const tamperedKernel = JSON.parse(completedRecord);
  tamperedKernel.result.receipt.kernel.state = "READY";
  values.set(quizKey, JSON.stringify(tamperedKernel));
  await assert.rejects(client.verifyKnowledgeQuizSeal(questionId), /knowledge_quiz_seal_invalid/);

  const adviser = await client.askAdviser({
    question: "Where is Du Bo?",
    stage_id: "01",
    stage_title: "Chapter One",
    stage_index: 1,
  });
  assert.strictEqual(adviser.mode, "offline");
  assert.strictEqual(adviser.state, "ANSWERED");
  assert.strictEqual(adviser.intentType, "location");
  assert.strictEqual(adviser.guide.available, true);
  assert.strictEqual(adviser.guide.target.name, "Du Bo");
  assert.strictEqual(adviser.adviser.heroId, "DuBo");
  assert.strictEqual(Object.keys(adviser.sourceProvenance.services).length, 4);
  assert.match(adviser.answerDigest, /^[0-9a-f]{64}$/);
  const adviserJournal = JSON.parse(values.get("dongzhou-adviser-question-v1"));
  const adviserId = adviserJournal.input.client_request_id;
  assert.strictEqual((await client.adviserQuestion(adviserId)).replayed, true);
  const cleanAdviserJournal = values.get("dongzhou-adviser-question-v1");
  adviserJournal.result.answer = "forged answer";
  values.set("dongzhou-adviser-question-v1", JSON.stringify(adviserJournal));
  await assert.rejects(client.adviserQuestion(adviserId), /adviser_answer_source_invalid/);
  values.set("dongzhou-adviser-question-v1", cleanAdviserJournal);

  const guide = await client.decideAdviserGuide(adviserId, "ACCEPT");
  assert.strictEqual(guide.state, "ACCEPTED");
  assert.strictEqual(guide.guide.kernel.module, "dongzhou_adviser_guide");
  assert.strictEqual(guide.guide.kernel.moduleVersion, "1.1.0");
  assert.strictEqual(guide.guide.sourceProvenance.digest, adviser.sourceProvenance.digest);
  assert.strictEqual((await client.decideAdviserGuide(adviserId, "ACCEPT")).replayed, true);
  await assert.rejects(client.decideAdviserGuide(adviserId, "REJECT"), /adviser_guide_already_decided/);
  const guideActionId = guide.guide.actionId;
  assert.strictEqual((await client.adviserGuide(guideActionId)).state, "RUNNING");
  assert.strictEqual((await client.adviserGuide(guideActionId)).state, "COMPLETED");
  const feedback = await client.feedbackAdviser(adviserId, "accurate");
  assert.strictEqual(feedback.state, "RECORDED");
  assert.strictEqual((await client.feedbackAdviser(adviserId, "accurate")).replayed, true);
  await assert.rejects(client.feedbackAdviser(adviserId, "inaccurate"), /adviser_feedback_already_recorded/);

  const cancellable = await client.askAdviser({
    question: "Where is Du Bo?",
    stage_id: "01",
    stage_title: "Chapter One",
    stage_index: 1,
  });
  const cancellableId = JSON.parse(values.get("dongzhou-adviser-question-v1")).input.client_request_id;
  const accepted = await client.decideAdviserGuide(cancellableId, "ACCEPT");
  const cancelled = await client.cancelAdviserGuide(accepted.guide.actionId, "player_changed_plan");
  assert.strictEqual(cancelled.state, "CANCELLED");
  assert.strictEqual(cancelled.guide.reason, "player_changed_plan");
  assert.strictEqual((await client.cancelAdviserGuide(accepted.guide.actionId, "player_changed_plan")).replayed, true);
  const sealedJournal = values.get("dongzhou-adviser-question-v1");
  const forgedGuide = JSON.parse(sealedJournal);
  forgedGuide.guideDecision.result.guide.digest = "0".repeat(64);
  values.set("dongzhou-adviser-question-v1", JSON.stringify(forgedGuide));
  await assert.rejects(client.adviserGuide(accepted.guide.actionId), /adviser_guide_seal_invalid/);
  values.set("dongzhou-adviser-question-v1", sealedJournal);
  await assert.rejects(client.cancelAdviserGuide(accepted.guide.actionId, "x".repeat(501)), /adviser_guide_cancel_invalid/);

  await client.askAdviser({ question: "Where is Du Bo?", stage_id: "01", stage_title: "Chapter One", stage_index: 1 });
  const rejectedId = JSON.parse(values.get("dongzhou-adviser-question-v1")).input.client_request_id;
  const rejected = await client.decideAdviserGuide(rejectedId, "REJECT");
  assert.strictEqual(rejected.state, "REJECTED");
  assert.strictEqual(rejected.guide.decision, "REJECT");
  assert.strictEqual(rejected.guide.kernel.state, "SEALED");
  assert.strictEqual(fetchedUrls.some((url) => url.includes("/api/")), false);

  console.log(JSON.stringify({ result: "PASS", entries: codex.results.length, compact: true, localQuiz: true, localAdviser: true, localBattleGate: true, localDebrief: true, localCommendation: true, localRecollection: true, localLogistics: true, localInventoryRequisition: true, localThought: true, localCouncil: true }));
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
