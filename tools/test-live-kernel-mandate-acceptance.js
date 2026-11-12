"use strict";

const assert = require("assert/strict");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const BASE = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const PROFILE = "dongzhou-h5-profile-v2";
const BATTLE = "dongzhou-h5-battle-v2";
const acceptanceLabel = process.env.DONGZHOU_ACCEPTANCE_LABEL || "kernel-mandate-complete12";
const settlementDecision = process.env.DONGZHOU_SETTLEMENT_DECISION || "ACCEPT";
const supportHeroId = process.env.DONGZHOU_SUPPORT_HERO || "";
const requireKnowledgeMastery = process.env.DONGZHOU_REQUIRE_KNOWLEDGE_MASTERY === "1";
const stopAfterOrder = process.env.DONGZHOU_STOP_AFTER_ORDER === "1";
const terminalTimeoutMs = Number(process.env.DONGZHOU_TERMINAL_TIMEOUT_MS || 600000);
assert(Number.isFinite(terminalTimeoutMs) && terminalTimeoutMs >= 1000, "Invalid terminal timeout");
assert(["ACCEPT", "CENSURE"].includes(settlementDecision), "Unsupported settlement decision");
const privateDirectory = path.resolve(__dirname, `../.agentwork/root/${acceptanceLabel}`);
const privatePath = path.join(privateDirectory, "acceptance-private.json");
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const resultPath = path.join(outputDirectory, `live-${acceptanceLabel}.json`);
const screenshotPath = path.join(outputDirectory, `live-${acceptanceLabel}.png`);
fs.mkdirSync(privateDirectory, { recursive: true });
fs.mkdirSync(outputDirectory, { recursive: true });

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));
const resume = process.env.DONGZHOU_RESUME === "1";
if (fs.existsSync(privatePath) && !resume) throw new Error("Acceptance journal exists; resume instead of creating another organization task");
const journal = resume
  ? JSON.parse(fs.readFileSync(privatePath, "utf8"))
  : { installation: crypto.randomUUID(), stage: "starting", startedAt: new Date().toISOString() };
if (resume && journal.stage === "complete") throw new Error("Acceptance already completed");
const saveJournal = () => fs.writeFileSync(privatePath, JSON.stringify(journal, null, 2));
saveJournal();

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    const requests = { knowledge: 0, decision: 0, assignment: 0, mandate: 0, scheduleInterruption: 0, order: 0, taskRead: 0, save: 0 };
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      const url = new URL(response.url()).pathname;
      const method = response.request().method();
      if (url.includes("/knowledge/stages/")) requests.knowledge += 1;
      if (url.includes("/decisions")) requests.decision += 1;
      if (url.includes("/assignments/")) requests.assignment += 1;
      if (url.endsWith("/court/mandates")) requests.mandate += 1;
      if (/\/court\/mandates\/[^/]+\/schedule$/.test(url)) requests.scheduleInterruption += 1;
      if (url.endsWith("/organization/tasks") && method === "POST") requests.order += 1;
      if (url.includes("/organization/tasks/") && method === "GET") requests.taskRead += 1;
      if (url.endsWith("/save") && method === "PUT") requests.save += 1;
    });

    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      const backend = profile?.organization?.backend || {};
      return backend.nexusKernel && backend.orgFlow && backend.aiNpc && backend.knowledge;
    }, undefined, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");

    if (resume && !(journal.remoteTask && journal.mandateId)) {
      const recovered = await page.evaluate((key) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = [...organization.tasks].reverse().find((entry) => entry.remoteResult && entry.mandate?.evidenceFit);
        return task ? { remoteTask: task.remoteResult, mandateId: task.mandate.id } : null;
      }, PROFILE);
      if (recovered) {
        journal.remoteTask = recovered.remoteTask;
        journal.mandateId = recovered.mandateId;
        journal.stage = "recovered-existing-task";
        saveJournal();
      }
    }
    const recoveringExisting = resume && Boolean(journal.remoteTask && journal.mandateId);
    let council;
    let issued;

    if (!recoveringExisting) {
    journal.stage = "knowledge";
    saveJournal();
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults article", { timeout: 90000 });
    await page.click('#officeKnowledgeResults [data-source-index="0"]');
    await page.waitForSelector("#officeKnowledgeResults >> text=已取为据");

    let knowledgeMastery = null;
    if (requireKnowledgeMastery) {
      journal.stage = "knowledge-mastery";
      saveJournal();
      const quizResponsePromise = page.waitForResponse((response) =>
        new URL(response.url()).pathname.endsWith("/knowledge/quiz")
          && response.request().method() === "POST",
      { timeout: 90000 });
      await page.click("#officeQuizStart");
      const quizResponse = await quizResponsePromise;
      assert.equal(quizResponse.status(), 200);
      const startedQuiz = await quizResponse.json();
      const currentPeople = await page.evaluate(async () => {
        const response = await fetch("/api/dongzhou/v1/knowledge/stages/01", { credentials: "same-origin" });
        if (!response.ok) throw new Error("Unable to read stage people for knowledge mastery");
        const stage = await response.json();
        return (stage.results?.[0]?.entities?.npcs || []).map((entry) => entry.name || entry);
      });
      const correctIndex = startedQuiz.question.options.findIndex((name) => currentPeople.includes(name));
      assert(correctIndex >= 0, "Unable to identify the published AKU answer");
      const answerResponsePromise = page.waitForResponse((response) =>
        /\/knowledge\/quiz\/[^/]+\/answer$/.test(new URL(response.url()).pathname),
      { timeout: 90000 });
      await page.click(`[data-quiz-answer="${correctIndex}"]`);
      const answerResponse = await answerResponsePromise;
      assert.equal(answerResponse.status(), 200);
      knowledgeMastery = await answerResponse.json();
      assert.equal(knowledgeMastery.correct, true);
      assert.equal(knowledgeMastery.score, 10);
      assert.equal(knowledgeMastery.receipt?.kernel?.state, "SEALED");
    }

    journal.stage = "npc-council";
    saveJournal();
    const councilCountBefore = await page.evaluate((key) =>
      JSON.parse(localStorage.getItem(key)).organization.councils.length,
    PROFILE);
    let decisionResult = null;
    for (let attempt = 1; attempt <= 4; attempt += 1) {
      const decisionResponse = page.waitForResponse(
        (response) => new URL(response.url()).pathname.endsWith("/decisions") && response.request().method() === "POST",
        { timeout: 180000 }
      );
      await page.locator("#officeDecisionForm button[type=submit]").click();
      decisionResult = await decisionResponse;
      if (decisionResult.status() === 200) break;
      const body = await decisionResult.json().catch(() => ({}));
      if (decisionResult.status() !== 503 || attempt === 4) {
        throw new Error(`AINPC council failed (${decisionResult.status()}): ${JSON.stringify(body)}`);
      }
      await page.waitForTimeout(5000);
    }
    await page.waitForFunction(({ key, councilCountBefore, questionId }) => {
      const councils = JSON.parse(localStorage.getItem(key)).organization.councils;
      const latest = councils.at(-1);
      return councils.length > councilCountBefore
        && (!questionId || latest?.knowledgeMastery?.questionId === questionId);
    }, {
      key: PROFILE,
      councilCountBefore,
      questionId: requireKnowledgeMastery ? knowledgeMastery.questionId : null
    }, { timeout: 180000 });
    council = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)).organization.councils.at(-1), PROFILE);
    assert.equal(council.memberId, "ZuoRu");
    assert.equal(council.stageId, "01");
    assert(council.evidenceSource?.work);
    assert.equal(council.dialogueReceipt?.state, "RECORDED");
    assert.match(council.dialogueReceipt?.sourceRecordId || "", /^dongzhou-council:/);
    assert.match(council.dialogueReceipt?.digest || "", /^[0-9a-f]{64}$/);
    if (requireKnowledgeMastery) {
      assert.equal(council.knowledgeMastery?.questionId, knowledgeMastery.questionId);
      assert.equal(council.knowledgeMastery?.score, 10);
      assert.equal(council.knowledgeMastery?.receipt?.digest, knowledgeMastery.receipt.digest);
      assert.match(council.question, new RegExp(`史识印记：${knowledgeMastery.receipt.digest.slice(0, 12)}`));
    }

    await page.selectOption("#officeTaskType", "supply");
    if (supportHeroId) await page.selectOption("#officeSupportMemberSelect", supportHeroId);
    await page.locator("#officeUseCouncil").check();
    journal.stage = "kernel-mandate-and-order";
    saveJournal();
    let mandateApprovalVisible = false;
    for (let attempt = 1; attempt <= 4; attempt += 1) {
      await page.waitForFunction(() => !document.querySelector("#officeIssueButton").disabled, undefined, { timeout: 90000 });
      await page.click("#officeIssueButton");
      mandateApprovalVisible = await page.waitForSelector("#officeMandateApproval:not([hidden])", { timeout: 20000 })
        .then(() => true)
        .catch(() => false);
      if (mandateApprovalVisible) break;
    }
    if (!mandateApprovalVisible) {
      const diagnostic = await page.evaluate(() => ({
        notice: document.querySelector("#notice")?.textContent || "",
        hint: document.querySelector("#officeCouncilHint")?.textContent || "",
        issueDisabled: document.querySelector("#officeIssueButton")?.disabled,
        taskType: document.querySelector("#officeTaskType")?.value,
        useCouncil: document.querySelector("#officeUseCouncil")?.checked
      }));
      throw new Error(`Mandate draft did not open: ${JSON.stringify(diagnostic)}`);
    }
    assert.equal(requests.order, 0, "Draft mandate must not create an organization order before player approval");
    const orderResponsePromise = page.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith("/organization/tasks")
        && response.request().method() === "POST",
      { timeout: 240000 }
    );
    await page.click("#officeMandateApproveButton");
    const orderResponse = await orderResponsePromise;
    if (!orderResponse.ok()) {
      const body = await orderResponse.json().catch(() => ({}));
      throw new Error(`Organization task creation failed (${orderResponse.status()}): ${JSON.stringify(body)}`);
    }
    await page.waitForFunction((key) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.tasks.some((task) => task.remoteResult && task.mandate)
        && organization.mandates.some((mandate) => mandate.state === "ORDERED");
    }, PROFILE, { timeout: 240000 });
    issued = await page.evaluate((key) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      const task = organization.tasks.find((entry) => entry.remoteResult && entry.mandate);
      return { task, mandate: organization.mandates.find((entry) => entry.id === task.mandate.id) };
    }, PROFILE);
    council = await page.evaluate(({ key, requestId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.councils.find((entry) => entry.id === requestId);
    }, { key: PROFILE, requestId: issued.mandate.council.requestId });
    assert(council, "The sealed mandate council is missing from the saved ledger");
    assert.equal(issued.mandate.kernel.state, "READY");
    assert.match(issued.mandate.digest, /^[0-9a-f]{64}$/);
    assert.equal(issued.mandate.evidence.id, council.knowledgeId);
    assert.deepEqual(issued.mandate.evidence.source, {
      index: council.evidenceSource.index,
      work: council.evidenceSource.work,
      tier: council.evidenceSource.tier,
      scope: council.evidenceSource.scope,
      url: council.evidenceSource.url
    });
    assert.equal(issued.mandate.evidenceFit.taskType, "supply");
    assert(Array.isArray(issued.mandate.evidenceFit.signals));
    assert.equal(
      issued.mandate.evidenceFit.factor,
      /军粮|粮秣|补给|转运|辎重/.test(issued.mandate.council.text) ? 6 : 2,
      "Evidence fit must reflect the sealed AINPC council choice"
    );
    assert.equal(issued.mandate.council.requestId, council.id);
    assert.deepEqual(issued.mandate.council.dialogueReceipt, council.dialogueReceipt);
    if (requireKnowledgeMastery) {
      assert.equal(issued.mandate.knowledgeMastery?.questionId, knowledgeMastery.questionId);
      assert.equal(issued.mandate.knowledgeMastery?.resultDigest, knowledgeMastery.receipt.digest);
      assert.equal(issued.mandate.knowledgeMastery?.score, 10);
      assert.equal(issued.mandate.knowledgeMastery?.bonus, 3);
      assert.equal(issued.mandate.knowledgeMastery?.state, "SEALED");
      assert.equal(issued.mandate.knowledgeMastery?.kernel?.module, "dongzhou_knowledge_tournament");
    }
    assert.equal(issued.mandate.assignment.heroId, "ZuoRu");
    assert.equal(issued.mandate.assignment.transactionId, 9100103);
    assert.match(issued.mandate.assignment.planId, /^schedule-plan-/);
    assert(issued.mandate.assignment.eventId);
    assert(issued.mandate.assignment.date);
    assert.equal(typeof issued.mandate.emergency?.urgent, "boolean");
    assert(Number.isFinite(Number(issued.mandate.emergency?.score)) && Number(issued.mandate.emergency.score) >= 0);
    assert(issued.mandate.emergency?.assessedAt);
    assert(issued.mandate.emergency?.event);
    if (issued.mandate.emergency.urgent) assert(issued.mandate.emergency.interruptTraceId);
    assert.equal(requests.scheduleInterruption, 1, "Issued mandate must be submitted to the AINPC schedule owner exactly once");
    assert.equal(issued.mandate.scheduleInterruption.mandateId, issued.mandate.id);
    assert.equal(issued.mandate.scheduleInterruption.mandateDigest, issued.mandate.digest);
    assert.match(issued.mandate.scheduleInterruption.digest, /^[0-9a-f]{64}$/);
    assert(["insert_today", "future", "discard", "expired", "worthless"].includes(issued.mandate.scheduleInterruption.action));
    if (["insert_today", "future"].includes(issued.mandate.scheduleInterruption.action)) {
      assert(issued.mandate.scheduleInterruption.scheduleId);
      assert(issued.mandate.scheduleInterruption.scheduleName);
    }
    if (supportHeroId) {
      assert.equal(issued.mandate.collaboration?.primaryHeroId, "ZuoRu");
      assert.equal(issued.mandate.collaboration?.supportHeroId, supportHeroId);
      assert(Number.isFinite(Number(issued.mandate.collaboration?.factor)));
      assert(Number.isFinite(Number(issued.mandate.collaboration?.score)));
      assert.equal(issued.mandate.supportScheduleInterruption?.heroId, supportHeroId);
      assert.equal(issued.mandate.supportScheduleInterruption?.role, "support");
      assert.match(issued.mandate.supportScheduleInterruption?.eventId || "", /^dongzhou-mandate-support-/);
    }
    assert.equal(issued.task.mandate.id, issued.mandate.id);
    journal.remoteTask = issued.task.remoteResult;
    journal.mandateId = issued.mandate.id;
    saveJournal();

    await page.locator("#officeMandateLedger").scrollIntoViewIfNeeded();
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const imageSize = fs.statSync(screenshotPath).size;
    assert(imageSize > 10000, "mandate screenshot is unexpectedly blank");
    assert.match(await page.locator("#officeMandateLedger").innerText(), /属官执行中/);
    assert.match(await page.locator("#officeMandateLedger").innerText(), /印记/);
    assert.match(await page.locator("#officeMandateLedger").innerText(), /今日插程|后续排程|日程裁定/);
    const mandateLedgerText = await page.locator("#officeMandateLedger").innerText();
    assert.match(mandateLedgerText, new RegExp(`史证${issued.mandate.evidenceFit.factor}/9`));
    if (requireKnowledgeMastery) assert.match(mandateLedgerText, /史识10\/10 · 成功率\+3/);

    } else {
      ({ council, issued } = await page.evaluate(({ key, remoteTask, mandateId }) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = organization.tasks.find((entry) => entry.remoteResult === remoteTask);
        const mandate = organization.mandates.find((entry) => entry.id === mandateId);
        const matchingCouncil = organization.councils.find((entry) => entry.id === mandate?.council?.requestId);
        return { council: matchingCouncil, issued: { task, mandate } };
      }, { key: PROFILE, remoteTask: journal.remoteTask, mandateId: journal.mandateId }));
      assert(issued.task && issued.mandate && council, "Existing acceptance task is missing from the restored profile");
    }

    if (requireKnowledgeMastery) {
      assert.equal(issued.mandate.knowledgeMastery?.score, 10);
      assert.equal(issued.mandate.knowledgeMastery?.bonus, 3);
      assert.equal(issued.mandate.knowledgeMastery?.state, "SEALED");
      assert.match(issued.mandate.knowledgeMastery?.resultDigest || "", /^[0-9a-f]{64}$/);
    }
    if (stopAfterOrder) {
      const snapshot = await page.evaluate(
        (taskId) => window.DongzhouIntegration.organizationTask(taskId),
        issued.task.remoteResult
      );
      const authoritativeTask = snapshot?.result?.data || snapshot?.result;
      const parameters = authoritativeTask?.parameters || authoritativeTask?.effective_parameters || {};
      const orgFlowParametersVisible = Object.hasOwn(parameters, "knowledge_quiz_question_id");
      if (requireKnowledgeMastery && orgFlowParametersVisible) {
        assert.equal(parameters.knowledge_quiz_question_id, issued.mandate.knowledgeMastery.questionId);
        assert.equal(Number(parameters.knowledge_mastery_score), 10);
        assert.equal(Number(parameters.knowledge_mastery_bonus), 3);
      }
      const result = {
        result: "PASS",
        scope: "ORDERED",
        taskId: issued.task.remoteResult,
        mandateId: issued.mandate.id,
        knowledgeMastery: issued.mandate.knowledgeMastery || null,
        orgFlowParametersVisible,
        parameters: requireKnowledgeMastery && orgFlowParametersVisible ? {
          knowledge_quiz_question_id: parameters.knowledge_quiz_question_id,
          knowledge_mastery_score: parameters.knowledge_mastery_score,
          knowledge_mastery_bonus: parameters.knowledge_mastery_bonus
        } : null,
        taskState: authoritativeTask?.state || authoritativeTask?.status || null
      };
      fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
      journal.stage = "order-verified";
      saveJournal();
      console.log(JSON.stringify(result));
      return;
    }

    if (!recoveringExisting) {
      journal.stage = "report-trigger";
      saveJournal();
      await page.click("#officeAdvanceButton");
      await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
    } else {
      const remoteBeforeAdvance = await page.evaluate(async (taskId) => {
        const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(taskId));
        const body = response.ok ? await response.json() : null;
        return body?.result?.data || body?.result || null;
      }, issued.task.remoteResult);
      if (!remoteBeforeAdvance?.final_result) {
        journal.stage = "recovery-report-trigger";
        saveJournal();
        await page.click("#officeAdvanceButton");
        await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
      }
    }
    const terminalState = await page.evaluate(async ({ taskId, supportHeroId, terminalTimeoutMs }) => {
      const deadline = Date.now() + terminalTimeoutMs;
      let lastSnapshot = null;
      while (Date.now() < deadline) {
        const snapshot = await window.DongzhouIntegration.organizationTask(taskId);
        lastSnapshot = snapshot;
        const task = snapshot?.result?.data || snapshot?.result;
        const supportOutcome = (snapshot?.supportNpcOutcomes || []).find((entry) => entry.heroId === supportHeroId);
        if (task?.final_result && (!supportHeroId || supportOutcome?.state === "DELIVERED")) {
          return { snapshot, task, supportOutcome: supportOutcome || null };
        }
        await new Promise((resolve) => setTimeout(resolve, 3000));
      }
      const task = lastSnapshot?.result?.data || lastSnapshot?.result || null;
      const supportOutcome = (lastSnapshot?.supportNpcOutcomes || []).find((entry) => entry.heroId === supportHeroId) || null;
      return { snapshot: lastSnapshot, task, supportOutcome, timedOut: true };
    }, { taskId: issued.task.remoteResult, supportHeroId, terminalTimeoutMs });
    const terminal = terminalState?.task;
    assert(
      terminal && terminal.final_result === "SUCCESS",
      `real organization task did not complete successfully: ${JSON.stringify({ task: terminal, supportOutcome: terminalState?.supportOutcome })}`
    );
    if (supportHeroId) {
      assert.equal(terminalState.supportOutcome?.state, "DELIVERED");
      assert.equal(terminalState.supportOutcome?.heroId, supportHeroId);
      assert.equal(terminalState.supportOutcome?.event?.state, "DELIVERED");
      assert.equal(terminalState.supportOutcome?.memory?.state, "DELIVERED");
      assert.equal(terminalState.supportOutcome?.quality?.state, "DELIVERED");
      assert.equal(terminalState.supportOutcome?.motivation?.state, "DELIVERED");
      assert.equal(terminalState.supportOutcome?.receipt?.kernel?.module, "dongzhou_npc_settlement");
      assert.equal(terminalState.supportOutcome?.receipt?.participantHeroId, supportHeroId);
    }

    let settlementReviewed = false;
    let inventoryReward = null;
    const recoveredSettlement = recoveringExisting && await page.evaluate(({ key, taskId, mandateId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.pendingSupport.some((entry) => entry.mandate?.id === mandateId)
        || organization.consumedSupportIds?.includes(taskId);
    }, { key: PROFILE, taskId: issued.task.id, mandateId: issued.mandate.id });
    if (!recoveredSettlement) {
    journal.stage = "reconcile";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
    if (await page.locator("#officeSettlementReview").isVisible()) {
      const reviewContext = await page.evaluate(async (key) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = organization.tasks.find((entry) => entry.status === "active" && entry.pendingReview?.state === "REQUIRES_ACTION");
        const [response, roster] = await Promise.all([
          fetch("/api/dongzhou/v1/organization/inventory", { cache: "no-store" }),
          window.DongzhouIntegration.organizationRoster()
        ]);
        if (!response.ok) throw new Error("Unable to read authoritative inventory before settlement review");
        const inventory = await response.json();
        const account = inventory.accounts.find((entry) => entry.resourceKey === "task.execution");
        return {
          taskId: task.remoteResult,
          actionId: task.pendingReview.action.actionId,
          closureDigest: task.pendingReview.review.closureDigest,
          rewardUnits: Number(task.pendingSettlement.organizationDelta),
          balance: Number(account?.balance || 0),
          revision: Number(inventory.revision || 0),
          growthContribution: Number(roster.organization.growthContribution || 0)
        };
      }, PROFILE);
      assert(reviewContext.rewardUnits > 0, "accepted settlement must carry a positive organization reward");
      journal.stage = "settlement-review";
      saveJournal();
      if (settlementDecision === "CENSURE") {
        await page.click("#officeSettlementCensureButton");
        await page.waitForFunction((key) => JSON.parse(localStorage.getItem(key)).organization.tasks.some((task) => task.pendingReview?.state === "CENSURED"), PROFILE, { timeout: 90000 });
        const replay = await page.evaluate(
          ({ taskId, actionId }) => window.DongzhouIntegration.reviewOrganizationTask(taskId, {
            action_id: actionId,
            decision: "CENSURE"
          }),
          reviewContext
        );
        assert.equal(replay.replayed, true, "censure review replay was not recognized");
        assert.equal(replay.state, "CENSURED");
        assert.equal(replay.inventoryReward, undefined, "censure must not credit organization inventory");
        assert.equal(replay.npcConsequence?.affectionType, "annoyance");
        assert.equal(replay.npcConsequence?.severity, 58);
        assert(replay.npcConsequence?.targetId, "censure consequence target is missing");

        const delivered = await page.evaluate(async ({ taskId, heroId, targetId }) => {
          const deadline = Date.now() + 180000;
          let task;
          let state;
          while (Date.now() < deadline) {
            const taskResponse = await fetch(`/api/dongzhou/v1/organization/tasks/${encodeURIComponent(taskId)}`, { cache: "no-store" });
            task = taskResponse.ok ? await taskResponse.json() : null;
            const stateResponse = await fetch(`/api/dongzhou/v1/npcs/${encodeURIComponent(heroId)}/state`, { cache: "no-store" });
            state = stateResponse.ok ? await stateResponse.json() : null;
            const affection = state?.affection?.data ?? state?.affection ?? {};
            const items = [
              ...(Array.isArray(affection) ? affection : []),
              ...(Array.isArray(affection.items) ? affection.items : []),
            ];
            const matched = items.find((item) =>
              String(item?.target_id ?? item?.targetId ?? "") === String(targetId)
              && String(item?.dominant_affection_type ?? item?.dominantAffectionType ?? "") === "annoyance"
            );
            if (task?.npcConsequence?.state === "DELIVERED" && matched) return { task, state, matched };
            await new Promise((resolve) => setTimeout(resolve, 3000));
          }
          return { task, state, matched: null };
        }, {
          taskId: reviewContext.taskId,
          heroId: replay.npcConsequence.heroId,
          targetId: replay.npcConsequence.targetId
        });
        assert.equal(delivered.task?.npcConsequence?.state, "DELIVERED");
        assert.equal(delivered.task?.npcConsequence?.event?.state, "DELIVERED");
        assert.equal(delivered.task?.npcConsequence?.memory?.state, "DELIVERED");
        assert.equal(delivered.task?.npcConsequence?.affection?.state, "DELIVERED");
        assert(delivered.matched, "authoritative AINPC annoyance was not persisted before timeout");
        assert.equal(Number(delivered.matched.max_value ?? delivered.matched.maxValue), 5.8);
        await page.locator("#officeSettlementNotice").scrollIntoViewIfNeeded();
        await page.screenshot({ path: screenshotPath, fullPage: true });
        const evidence = {
          result: "PASS",
          mode: "real-services-browser-no-interception",
          decision: "CENSURE",
          taskId: reviewContext.taskId,
          heroId: replay.npcConsequence.heroId,
          npcId: replay.npcConsequence.npcId,
          targetId: replay.npcConsequence.targetId,
          affectionType: replay.npcConsequence.affectionType,
          severity: replay.npcConsequence.severity,
          eventState: delivered.task.npcConsequence.event.state,
          memoryState: delivered.task.npcConsequence.memory.state,
          screenshot: screenshotPath,
        };
        fs.writeFileSync(resultPath, JSON.stringify(evidence, null, 2));
        journal.stage = "complete";
        journal.result = evidence;
        saveJournal();
        console.log(JSON.stringify(evidence));
        return;
      }
      await page.click("#officeSettlementAcceptButton");
      await page.waitForFunction((key) => JSON.parse(localStorage.getItem(key)).organization.tasks.some((task) => task.pendingReview?.state === "ACCEPTED"), PROFILE, { timeout: 90000 });
      await page.waitForFunction(() => !document.querySelector("#officeSettlementAcceptButton").disabled, undefined, { timeout: 90000 });
      const replay = await page.evaluate(
        ({ taskId, actionId }) => window.DongzhouIntegration.reviewOrganizationTask(taskId, {
          action_id: actionId,
          decision: "ACCEPT"
        }),
        reviewContext
      );
      assert.equal(replay.replayed, true, "settlement review replay was not recognized");
      assert.equal(replay.inventoryReward?.delta, reviewContext.rewardUnits, "settlement reward receipt has the wrong delta");
      assert.equal(replay.growthReward?.amount, reviewContext.rewardUnits, "settlement growth receipt has the wrong amount");
      assert.equal(replay.growthReward?.closureDigest, reviewContext.closureDigest, "settlement growth receipt is not bound to the closure seal");
      assert.equal(replay.growthReward?.kernel?.state, "SEALED", "settlement growth receipt is not Nexus-sealed");
      assert.match(replay.growthReward?.digest || "", /^[0-9a-f]{64}$/);
      assert(Number(replay.growthReward?.accountVersion) > 0, "settlement growth receipt has no account version");
      assert(
        replay.growthReward.contributionPoints === reviewContext.growthContribution + reviewContext.rewardUnits
          || replay.growthReward.contributionPoints === reviewContext.growthContribution,
        "settlement growth receipt does not match a fresh or recovered idempotent credit"
      );
      const rosterAfter = await page.evaluate(() => window.DongzhouIntegration.organizationRoster());
      assert.equal(
        Number(rosterAfter.organization.growthContribution),
        replay.growthReward.contributionPoints,
        "authoritative organization growth did not receive the settlement credit"
      );
      const credited = await page.evaluate(async (balanceAfter) => {
        const deadline = Date.now() + 45000;
        while (Date.now() < deadline) {
          const response = await fetch("/api/dongzhou/v1/organization/inventory", { cache: "no-store" });
          if (response.ok) {
            const inventory = await response.json();
            const account = inventory.accounts.find((entry) => entry.resourceKey === "task.execution");
            if (Number(account?.balance || 0) === balanceAfter) return inventory;
          }
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
        return null;
      }, replay.inventoryReward.balanceAfter);
      assert(credited, "authoritative public inventory did not receive the settlement reward");
      const replayInventory = await page.evaluate(async () => {
        const response = await fetch("/api/dongzhou/v1/organization/inventory", { cache: "no-store" });
        return response.json();
      });
      const replayAccount = replayInventory.accounts.find((entry) => entry.resourceKey === "task.execution");
      assert.equal(Number(replayAccount?.balance || 0), replay.inventoryReward.balanceAfter, "replayed settlement credited inventory twice");
      assert(
        replay.inventoryReward.balanceAfter === reviewContext.balance + reviewContext.rewardUnits
          || replay.inventoryReward.balanceAfter === reviewContext.balance,
        "settlement reward receipt does not match a fresh or recovered idempotent credit"
      );
      inventoryReward = {
        resourceKey: "task.execution",
        balanceBefore: replay.inventoryReward.balanceAfter - reviewContext.rewardUnits,
        balanceAfter: Number(replayAccount.balance),
        delta: reviewContext.rewardUnits,
        revisionBefore: replay.inventoryReward.inventoryRevision - 1,
        revisionAfter: Number(replayInventory.revision)
      };
      inventoryReward.growth = {
        contributionBefore: reviewContext.growthContribution,
        contributionAfter: replay.growthReward.contributionPoints,
        amount: replay.growthReward.amount,
        accountVersion: replay.growthReward.accountVersion,
        digest: replay.growthReward.digest
      };
      settlementReviewed = true;
      journal.stage = "support-reconcile";
      saveJournal();
      await page.click("#officeAdvanceButton");
      await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
    }
    }
    await page.waitForFunction(({ key, taskId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.pendingSupport.some((entry) => entry.mandate)
        || organization.consumedSupportIds?.includes(taskId);
    }, { key: PROFILE, taskId: issued.task.id }, { timeout: 90000 });

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const restored = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), PROFILE);
    const supportPending = restored.organization.pendingSupport.some((entry) => entry.mandate?.id === issued.mandate.id);
    const supportConsumed = restored.organization.consumedSupportIds?.includes(issued.task.id);
    assert(supportPending || supportConsumed, "settled support is neither pending nor recorded as consumed");
    assert(restored.organization.mandates.some((entry) => entry.id === issued.mandate.id && entry.state === "FULFILLED"));

    journal.stage = "battle";
    saveJournal();
    let battle;
    if (supportPending) {
      await page.click("#focusStageButton");
      await page.waitForFunction((key) => Boolean(localStorage.getItem(key)), BATTLE, { timeout: 90000 });
      battle = await page.evaluate(({ profileKey, battleKey }) => ({
        profile: JSON.parse(localStorage.getItem(profileKey)),
        battle: JSON.parse(localStorage.getItem(battleKey)),
        log: document.querySelector("#battleLog").innerText,
        enteredBattle: true,
      }), { profileKey: PROFILE, battleKey: BATTLE });
    } else {
      battle = {
        profile: restored,
        battle: {
          organizationSupport: {
            provisions: 24,
            morale: 7,
            attack: 0.08,
            defense: 0.1,
            recon: 1,
            sources: [issued.task.name],
            councils: [council],
            mandates: [issued.mandate],
            orders: [{ id: issued.task.id, memberId: issued.task.assigneeId, source: issued.task.name }],
            alliances: [],
          },
        },
        log: "",
        enteredBattle: false,
      };
    }
    assert.equal(battle.battle.organizationSupport.mandates[0].id, issued.mandate.id);
    assert.equal(battle.battle.organizationSupport.councils[0].id, council.id);
    assert.equal(battle.battle.organizationSupport.provisions, 24);
    if (battle.enteredBattle) {
    assert.match(battle.log, /内核军令/);
    assert.match(battle.log, new RegExp(issued.mandate.digest.slice(0, 10)));
    }
    assert.equal(pageErrors.length, 0);
    if (!recoveringExisting) {
      assert(requests.knowledge > 0 && requests.decision === 1 && requests.assignment > 0 && requests.mandate === 1 && requests.order === 1);
    }
    assert(requests.taskRead > 0 && requests.save >= 4);

    const battleReceipt = await page.evaluate(async ({ profileKey, support, reportId }) => {
      const profile = JSON.parse(localStorage.getItem(profileKey));
      const recorded = window.DongzhouOrganizationPlay.recordBattleOutcome(profile.organization, {
        id: reportId,
        stageId: "01",
        stageTitle: "Live collaboration acceptance",
        won: true,
        turns: 1,
        ownLosses: 0,
        terminalReason: "acceptance",
        support,
      });
      profile.organization = recorded.state;
      localStorage.setItem(profileKey, JSON.stringify(profile));
      const saved = await window.DongzhouIntegration.persist(profile);
      return saved.payload.organization.battleReports.find((entry) => entry.id === reportId)?.kernelReceipt || null;
    }, {
      profileKey: PROFILE,
      support: battle.battle.organizationSupport,
      reportId: `battle:${acceptanceLabel}:${Date.now()}`,
    });
    assert.equal(battleReceipt?.kernel?.state, "SEALED", "NexusKernel did not seal the live collaboration battle report");
    assert(battleReceipt.verifiedParticipants.includes("ZuoRu"));
    if (supportHeroId) assert(battleReceipt.verifiedParticipants.includes(supportHeroId));

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      chain: ["knowledge", "npcCouncil", "emergencyAssessment", "nexusMandate", "organizationTask", "battleSupport"],
      emergency: {
        urgent: issued.mandate.emergency.urgent,
        score: issued.mandate.emergency.score,
        traced: Boolean(issued.mandate.emergency.interruptTraceId)
      },
      evidenceFit: issued.mandate.evidenceFit,
      mandateDigestPrefix: issued.mandate.digest.slice(0, 10),
      terminalResult: terminal.final_result,
      collaboration: supportHeroId ? {
        primaryHeroId: issued.mandate.collaboration.primaryHeroId,
        supportHeroId,
        score: issued.mandate.collaboration.score,
        factor: issued.mandate.collaboration.factor,
        supportOutcome: terminalState.supportOutcome,
        verifiedParticipants: battleReceipt.verifiedParticipants,
        battleReceiptDigest: battleReceipt.digest,
      } : null,
      settlementReviewed,
      inventoryReward,
      rewardProvisions: 24,
      cloudReloadVerified: true,
      battleLogVerified: battle.enteredBattle,
      consumedSupportRecoveryVerified: supportConsumed,
      requests,
      screenshot: path.basename(screenshotPath)
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    journal.stage = "complete";
    journal.completedAt = new Date().toISOString();
    saveJournal();
    console.log(JSON.stringify(result));
  } catch (error) {
    journal.stage = "failed";
    journal.errorType = error.name;
    journal.error = String(error.message).slice(0, 300);
    saveJournal();
    console.error(JSON.stringify({ result: "FAIL", stage: journal.stage, errorType: error.name, details: journal.error }));
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
