"use strict";

// Real four-service diplomacy acceptance. No API is mocked.
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
const LABEL = process.env.DONGZHOU_ACCEPTANCE_LABEL || "formal-diplomacy-current";
const REQUESTED_INSTALLATION = process.env.DONGZHOU_INSTALLATION_ID || "";
const forceNewTask = process.env.DONGZHOU_FORCE_NEW_TASK === "1";
const taskFinalTimeout = Number(process.env.DONGZHOU_TASK_FINAL_TIMEOUT_MS || 1800000);
const PROFILE = "dongzhou-h5-profile-v2";
const PROPOSAL = "通商互助，共御强敌，不索取财货";
assert(/^[a-z0-9-]+$/.test(LABEL));
assert(Number.isSafeInteger(taskFinalTimeout) && taskFinalTimeout >= 600000);

const privateDirectory = path.resolve(__dirname, "../.agentwork/root");
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const privatePath = path.join(privateDirectory, `diplomacy-acceptance-${LABEL}-private.json`);
const resultPath = path.join(outputDirectory, `live-diplomacy-acceptance-${LABEL}.json`);
const screenshotPath = path.join(outputDirectory, `live-diplomacy-acceptance-${LABEL}.png`);
const tracePath = path.join(privateDirectory, `diplomacy-acceptance-${LABEL}-trace.jsonl`);
const trace = (stage, details = {}) => {
  const entry = JSON.stringify({ at: new Date().toISOString(), progress: stage, ...details });
  fs.appendFileSync(tracePath, `${entry}\n`);
  console.log(entry);
};
fs.mkdirSync(privateDirectory, { recursive: true });
fs.mkdirSync(outputDirectory, { recursive: true });

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((candidate) => fs.existsSync(candidate));
const resume = process.env.DONGZHOU_RESUME === "1";
if (fs.existsSync(privatePath) && !resume) {
  throw new Error("Acceptance journal exists; resume instead of creating another organization task");
}
const journal = resume && fs.existsSync(privatePath)
  ? JSON.parse(fs.readFileSync(privatePath, "utf8"))
  : { installation: REQUESTED_INSTALLATION || crypto.randomUUID(), stage: "starting", startedAt: new Date().toISOString() };
if (resume && journal.stage === "complete") throw new Error("Acceptance already completed");
const saveJournal = () => fs.writeFileSync(privatePath, JSON.stringify(journal, null, 2));
saveJournal();

async function authoritativeTask(page, taskId) {
  return page.evaluate(async (id) => {
    const response = await fetch(`/api/dongzhou/v1/organization/tasks/${encodeURIComponent(id)}`, { cache: "no-store" });
    if (!response.ok) return null;
    const body = await response.json();
    return body.result?.data || body.result || null;
  }, taskId);
}

async function waitForTask(page, taskId, predicate, timeout = 600000) {
  const deadline = Date.now() + timeout;
  let task = null;
  while (Date.now() < deadline) {
    task = await authoritativeTask(page, taskId);
    if (task && predicate(task)) return task;
    await page.waitForTimeout(3000);
  }
  return task;
}

async function advanceMonth(page) {
  await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
  await page.click("#officeAdvanceButton");
  await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
}

(async () => {
  trace("browser-launch");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const requests = { knowledge: 0, decision: 0, mandate: 0, order: 0, taskRead: 0, save: 0 };
  const pageErrors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript((installation) => {
      localStorage.setItem("dongzhou-installation-id-v1", installation);
    }, journal.installation);
    const page = await context.newPage();
    trace("browser-ready");
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      const pathname = new URL(response.url()).pathname;
      const method = response.request().method();
      if (response.status() >= 400) trace("http-error", { method, pathname, status: response.status() });
      if (pathname.includes("/knowledge/stages/")) requests.knowledge += 1;
      if (pathname.includes("/decisions")) requests.decision += 1;
      if (pathname.endsWith("/court/mandates")) requests.mandate += 1;
      if (pathname.endsWith("/organization/tasks") && method === "POST") requests.order += 1;
      if (pathname.includes("/organization/tasks/") && method === "GET") requests.taskRead += 1;
      if (pathname.endsWith("/save") && method === "PUT") requests.save += 1;
    });

    trace("page-open");
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    trace("app-visible");
    await page.click("#campaignOfficeButton");
    trace("office-open");
    await page.waitForFunction((key) => {
      const backend = JSON.parse(localStorage.getItem(key))?.organization?.backend || {};
      return backend.nexusKernel && backend.orgFlow && backend.aiNpc && backend.knowledge;
    }, PROFILE, { timeout: 45000 });
    trace("backend-ready");
    await page.selectOption("#officeMemberSelect", "ZuoRu");

    if (!journal.remoteTask && !forceNewTask) {
      const recovered = await page.evaluate((key) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = [...organization.tasks].reverse().find((entry) => entry.operation?.kind === "diplomacy" && entry.remoteResult);
        return task ? { taskId: task.remoteResult, mandateId: task.mandate?.id } : null;
      }, PROFILE);
      if (recovered?.mandateId) {
        journal.remoteTask = recovered.taskId;
        journal.mandateId = recovered.mandateId;
        saveJournal();
      }
    }

    if (!journal.remoteTask) {
      journal.stage = "knowledge";
      saveJournal();
      await page.click("#officeStageKnowledgeButton");
      await page.waitForSelector("#officeKnowledgeResults article", { timeout: 90000 });
      await page.click('#officeKnowledgeResults [data-source-index="0"]');
      await page.waitForFunction((key) => Boolean(
        JSON.parse(localStorage.getItem(key)).organization.selectedSources?.["01"]
      ), PROFILE);

      journal.stage = "npc-council";
      saveJournal();
      const beforeCouncil = await page.evaluate((key) => (
        JSON.parse(localStorage.getItem(key)).organization.councils.length
      ), PROFILE);
      let councilCompleted = false;
      for (let attempt = 0; attempt < 12 && !councilCompleted; attempt += 1) {
        await page.click('#officeDecisionForm button[type="submit"]');
        try {
          await page.waitForFunction(({ key, before }) => (
            JSON.parse(localStorage.getItem(key)).organization.councils.length > before
          ), { key: PROFILE, before: beforeCouncil }, { timeout: 30000 });
          councilCompleted = true;
        } catch (error) {
          if (attempt === 11) throw error;
          await page.waitForTimeout(1000);
        }
      }

      journal.stage = "npc-schedule-preflight";
      saveJournal();
      // Refresh both office NPC schedules before creating the task. Advancing the
      // game clock after execution starts can cross the short task deadline before
      // the real private-chat result and manager review finish.
      await advanceMonth(page);

      journal.stage = "formal-diplomacy-order";
      saveJournal();
      const knownRemoteTaskIds = await page.evaluate((key) => (
        JSON.parse(localStorage.getItem(key)).organization.tasks
          .map((entry) => entry.remoteResult)
          .filter(Boolean)
      ), PROFILE);
      await page.selectOption("#officeDiplomacyTarget", "zheng");
      await page.fill("#officeDiplomacyProposal", PROPOSAL);
      await page.click("#officeLobbyButton");
      await page.waitForSelector("#officeMandateApproval:not([hidden])", { timeout: 90000 });
      await page.click("#officeMandateApproveButton");
      await page.waitForFunction(({ key, known }) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        return organization.tasks.some((task) => (
          task.operation?.kind === "diplomacy"
          && task.remoteResult
          && !known.includes(task.remoteResult)
        ));
      }, { key: PROFILE, known: knownRemoteTaskIds }, { timeout: 300000 });
      const issued = await page.evaluate(({ key, known }) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = [...organization.tasks].reverse().find((entry) => (
          entry.operation?.kind === "diplomacy"
          && entry.remoteResult
          && !known.includes(entry.remoteResult)
        ));
        const mandate = organization.mandates.find((entry) => entry.id === task.mandate.id);
        return { task, mandate };
      }, { key: PROFILE, known: knownRemoteTaskIds });
      assert.equal(issued.task.operation.target_id, "zheng");
      assert(issued.task.operation.target_name);
      assert.equal(issued.task.operation.proposal, PROPOSAL);
      assert.deepEqual(issued.mandate.operation, issued.task.operation);
      assert(issued.mandate.evidence?.source?.work);
      assert.match(issued.mandate.digest, /^[0-9a-f]{64}$/);
      journal.remoteTask = issued.task.remoteResult;
      journal.mandateId = issued.mandate.id;
      saveJournal();
    }

    journal.stage = "orgflow-execution";
    saveJournal();
    let task = await waitForTask(page, journal.remoteTask, (entry) => (
      Boolean(entry.final_result) || entry.execution_started_game_time != null
    ));
    assert(task && (task.final_result || task.execution_started_game_time != null), "real diplomacy task did not enter execution");
    trace("task-entered-execution", { taskId: journal.remoteTask, state: task.state });
    if (!task.final_result) {
      task = await waitForTask(
        page,
        journal.remoteTask,
        (entry) => Boolean(entry.final_result),
        taskFinalTimeout,
      );
    }
    const terminal = task?.final_result;
    assert(
      ["SUCCESS", "PARTIAL", "FAILURE", "REJECTED", "CANCELLED", "INVALIDATED"].includes(terminal),
      `real diplomacy task did not reach a terminal result (state=${task?.state || "unknown"})`,
    );
    trace("task-terminal", { taskId: journal.remoteTask, terminal });

    journal.stage = "settlement-review";
    saveJournal();
    await advanceMonth(page);
    let settlementReviewed = false;
    if (await page.locator("#officeSettlementReview").isVisible()) {
      await page.click("#officeSettlementAcceptButton");
      await page.waitForFunction(({ key, taskId }) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        return organization.tasks.some((entry) => entry.remoteResult === taskId && entry.pendingReview?.state === "ACCEPTED");
      }, { key: PROFILE, taskId: journal.remoteTask }, { timeout: 120000 });
      settlementReviewed = true;
      await advanceMonth(page);
    }

    journal.stage = "reconcile";
    saveJournal();
    await page.waitForFunction(({ key, taskId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.tasks.some((entry) => entry.remoteResult === taskId && entry.status !== "active")
        && organization.diplomacy.lobbying.some((entry) => entry.organizationTaskId === taskId);
    }, { key: PROFILE, taskId: journal.remoteTask }, { timeout: 120000 });
    const reconciled = await page.evaluate(({ key, taskId, mandateId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return {
        task: organization.tasks.find((entry) => entry.remoteResult === taskId),
        lobbying: organization.diplomacy.lobbying.find((entry) => entry.organizationTaskId === taskId),
        mandate: organization.mandates.find((entry) => entry.id === mandateId),
      };
    }, { key: PROFILE, taskId: journal.remoteTask, mandateId: journal.mandateId });
    assert.equal(reconciled.lobbying.outcome, terminal === "SUCCESS" ? "accepted" : "rejected");
    assert.equal(reconciled.lobbying.mandateId, journal.mandateId);
    assert.equal(reconciled.task.operation.target_id, "zheng");

    await page.selectOption("#officeDiplomacyTarget", "zheng");
    await page.click("#officeAllianceButton");
    let allianceAuthorized = false;
    if (terminal === "SUCCESS") {
      await page.waitForFunction((key) => JSON.parse(localStorage.getItem(key)).organization.diplomacy.alliances.some(
        (entry) => entry.status === "active"
      ), PROFILE, { timeout: 30000 });
      allianceAuthorized = true;
    } else {
      await page.waitForTimeout(500);
      const allianceCount = await page.evaluate((key) => (
        JSON.parse(localStorage.getItem(key)).organization.diplomacy.alliances.length
      ), PROFILE);
      assert.equal(allianceCount, 0, "non-successful orgFlow result must not create an alliance");
    }

    await page.locator("#officeMandateLedger").scrollIntoViewIfNeeded();
    await page.screenshot({ path: screenshotPath, fullPage: true });
    assert(fs.statSync(screenshotPath).size > 10000);
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const restored = await page.evaluate(({ key, taskId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return {
        lobbying: organization.diplomacy.lobbying.find((entry) => entry.organizationTaskId === taskId),
        alliances: organization.diplomacy.alliances,
      };
    }, { key: PROFILE, taskId: journal.remoteTask });
    assert.equal(restored.lobbying.outcome, terminal === "SUCCESS" ? "accepted" : "rejected");
    assert.equal(restored.alliances.some((entry) => entry.status === "active"), allianceAuthorized);
    assert.deepEqual(pageErrors, []);
    assert(requests.taskRead >= 2 && requests.save >= 2);

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      chain: ["knowledge", "AINPC council", "NexusKernel diplomacy mandate", "orgFlow task", "settlement review", "cloud lobbying result", "alliance gate"],
      taskId: journal.remoteTask,
      terminalResult: terminal,
      lobbyingOutcome: restored.lobbying.outcome,
      settlementReviewed,
      allianceAuthorized,
      cloudReloadVerified: true,
      requests,
      screenshot: path.basename(screenshotPath),
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    journal.stage = "complete";
    journal.completedAt = new Date().toISOString();
    delete journal.failedAtStage;
    delete journal.errorType;
    delete journal.error;
    saveJournal();
    console.log(JSON.stringify(result));
  } catch (error) {
    journal.failedAtStage = journal.stage;
    journal.stage = "failed";
    journal.errorType = error.name;
    journal.error = String(error.message).slice(0, 300);
    saveJournal();
    console.error(JSON.stringify({ result: "FAIL", errorType: error.name, details: journal.error }));
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
