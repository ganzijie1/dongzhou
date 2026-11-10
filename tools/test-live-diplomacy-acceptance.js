"use strict";

// One-shot acceptance for the formal four-service diplomacy chain. No API is mocked.
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
const LABEL = process.env.DONGZHOU_ACCEPTANCE_LABEL || "20261110-formal-diplomacy-complete17";
const PROFILE = "dongzhou-h5-profile-v2";
assert(/^[a-z0-9-]+$/.test(LABEL));

const privateDirectory = path.resolve(__dirname, "../.agentwork/root");
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const privatePath = path.join(privateDirectory, `diplomacy-acceptance-${LABEL}-private.json`);
const resultPath = path.join(outputDirectory, `live-diplomacy-acceptance-${LABEL}.json`);
const screenshotPath = path.join(outputDirectory, `live-diplomacy-acceptance-${LABEL}.png`);
fs.mkdirSync(privateDirectory, { recursive: true });
fs.mkdirSync(outputDirectory, { recursive: true });

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));
const resume = process.env.DONGZHOU_RESUME === "1";
if (fs.existsSync(privatePath) && !resume) throw new Error("Acceptance journal exists; resume instead of creating another organization task");
const journal = resume && fs.existsSync(privatePath)
  ? JSON.parse(fs.readFileSync(privatePath, "utf8"))
  : { installation: crypto.randomUUID(), stage: "starting", startedAt: new Date().toISOString() };
if (resume && journal.stage === "complete") throw new Error("Acceptance already completed");
const saveJournal = () => fs.writeFileSync(privatePath, JSON.stringify(journal, null, 2));
saveJournal();

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const requests = { knowledge: 0, decision: 0, mandate: 0, order: 0, taskRead: 0, save: 0 };
  const pageErrors = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      const pathname = new URL(response.url()).pathname;
      const method = response.request().method();
      if (pathname.includes("/knowledge/stages/")) requests.knowledge += 1;
      if (pathname.includes("/decisions")) requests.decision += 1;
      if (pathname.endsWith("/court/mandates")) requests.mandate += 1;
      if (pathname.endsWith("/organization/tasks") && method === "POST") requests.order += 1;
      if (pathname.includes("/organization/tasks/") && method === "GET") requests.taskRead += 1;
      if (pathname.endsWith("/save") && method === "PUT") requests.save += 1;
    });

    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction((key) => {
      const backend = JSON.parse(localStorage.getItem(key))?.organization?.backend || {};
      return backend.nexusKernel && backend.orgFlow && backend.aiNpc && backend.knowledge;
    }, PROFILE, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");

    const existing = await page.evaluate((key) => {
      const organization = JSON.parse(localStorage.getItem(key))?.organization;
      const task = [...(organization?.tasks || [])].reverse().find((entry) => entry.operation?.kind === "diplomacy" && entry.remoteResult);
      const mandate = task ? (organization.mandates || []).find((entry) => entry.id === task.mandate?.id) : null;
      return task && mandate ? { taskId: task.remoteResult, mandateId: mandate.id } : null;
    }, PROFILE);
    if (!journal.remoteTask && existing) {
      journal.remoteTask = existing.taskId;
      journal.mandateId = existing.mandateId;
      saveJournal();
    }

    if (!journal.remoteTask) {
      journal.stage = "knowledge";
      saveJournal();
      await page.click("#officeStageKnowledgeButton");
      await page.waitForSelector("#officeKnowledgeResults article", { timeout: 90000 });
      await page.click('#officeKnowledgeResults [data-source-index="0"]');
      await page.waitForSelector("#officeKnowledgeResults >> text=已取为据");

      journal.stage = "npc-council";
      saveJournal();
      const councilCount = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)).organization.councils.length, PROFILE);
      if (!councilCount) {
        await page.click("#officeDecisionForm button[type=submit]");
        await page.waitForFunction(({ key, before }) => JSON.parse(localStorage.getItem(key)).organization.councils.length > before, { key: PROFILE, before: councilCount }, { timeout: 180000 });
      }
      await page.waitForFunction(() => !document.querySelector("#officeDecisionForm button[type=submit]").disabled, { timeout: 30000 });

      journal.stage = "formal-diplomacy-order";
      saveJournal();
      await page.selectOption("#officeDiplomacyTarget", "zheng");
      await page.fill("#officeDiplomacyProposal", "互通军情，共御强敌，不索取财货");
      await page.click("#officeLobbyButton");
      await page.waitForFunction((key) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const failed = document.querySelector("#officeDiplomacyResult")?.textContent?.startsWith("游说暂不可用：");
        return failed || organization.tasks.some((task) => task.operation?.kind === "diplomacy" && task.remoteResult);
      }, PROFILE, { timeout: 120000 });
      const lobbyError = await page.locator("#officeDiplomacyResult").innerText();
      if (lobbyError.startsWith("游说暂不可用：")) throw new Error(lobbyError);
      const issued = await page.evaluate((key) => {
        const organization = JSON.parse(localStorage.getItem(key)).organization;
        const task = [...organization.tasks].reverse().find((entry) => entry.operation?.kind === "diplomacy" && entry.remoteResult);
        const mandate = organization.mandates.find((entry) => entry.id === task.mandate.id);
        return { task, mandate };
      }, PROFILE);
      assert.deepEqual(issued.task.operation, { kind: "diplomacy", target_id: "zheng", target_name: "郑国", proposal: "互通军情，共御强敌，不索取财货" });
      assert.deepEqual(issued.mandate.operation, issued.task.operation);
      assert(issued.mandate.evidence?.source?.work, "Nexus mandate must seal the selected source");
      assert.match(issued.mandate.digest, /^[0-9a-f]{64}$/);
      journal.remoteTask = issued.task.remoteResult;
      journal.mandateId = issued.mandate.id;
      saveJournal();
    }

    journal.stage = "orgflow-execution";
    saveJournal();
    const ready = await page.evaluate(async (taskId) => {
      const deadline = Date.now() + 600000;
      while (Date.now() < deadline) {
        const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(taskId));
        if (response.ok) {
          const body = await response.json();
          const task = body.result?.data || body.result;
          if (task?.final_result || task?.execution_started_game_time != null) {
            return { finalResult: task.final_result || null, executionStarted: task.execution_started_game_time != null };
          }
        }
        await new Promise((resolve) => setTimeout(resolve, 3000));
      }
      return null;
    }, journal.remoteTask);
    assert(ready, "real diplomacy task did not enter execution state");
    let terminal = ready.finalResult;
    for (let advance = 0; !terminal && advance < 8; advance += 1) {
      await page.click("#officeAdvanceButton");
      await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, { timeout: 90000 });
      terminal = await page.evaluate(async (taskId) => {
        const deadline = Date.now() + 45000;
        while (Date.now() < deadline) {
          const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(taskId));
          if (response.ok) {
            const body = await response.json();
            const task = body.result?.data || body.result;
            if (task?.final_result) return task.final_result;
          }
          await new Promise((resolve) => setTimeout(resolve, 3000));
        }
        return null;
      }, journal.remoteTask);
    }
    assert(["SUCCESS", "PARTIAL", "FAILURE", "REJECTED", "CANCELLED", "INVALIDATED"].includes(terminal), "real diplomacy task did not reach a supported terminal result");

    journal.stage = "reconcile";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(({ key, taskId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.tasks.some((task) => task.remoteResult === taskId && task.status !== "active")
        && organization.diplomacy.lobbying.some((entry) => entry.organizationTaskId === taskId);
    }, { key: PROFILE, taskId: journal.remoteTask }, { timeout: 90000 });

    const reconciled = await page.evaluate(({ key, taskId, mandateId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return {
        task: organization.tasks.find((entry) => entry.remoteResult === taskId),
        lobbying: organization.diplomacy.lobbying.find((entry) => entry.organizationTaskId === taskId),
        mandate: organization.mandates.find((entry) => entry.id === mandateId)
      };
    }, { key: PROFILE, taskId: journal.remoteTask, mandateId: journal.mandateId });
    assert.equal(reconciled.lobbying.outcome, terminal === "SUCCESS" ? "accepted" : "rejected");
    assert.equal(reconciled.lobbying.mandateId, journal.mandateId);
    assert.equal(reconciled.task.operation.target_id, "zheng");

    let allianceAuthorized = false;
    if (terminal === "SUCCESS") {
      await page.click("#officeAllianceButton");
      await page.waitForSelector("#officeAllianceLedger >> text=生效", { timeout: 30000 });
      allianceAuthorized = true;
    } else {
      await page.click("#officeAllianceButton");
      await page.waitForSelector("#officeDiplomacyResult >> text=尚未接受最近一次游说", { timeout: 30000 });
      const count = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)).organization.diplomacy.alliances.length, PROFILE);
      assert.equal(count, 0, "non-successful orgFlow result must not create an alliance");
    }

    await page.locator("#officeMandateLedger").scrollIntoViewIfNeeded();
    await page.screenshot({ path: screenshotPath, fullPage: true });
    assert(fs.statSync(screenshotPath).size > 10000, "acceptance screenshot is unexpectedly blank");

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const restored = await page.evaluate(({ key, taskId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return {
        lobbying: organization.diplomacy.lobbying.find((entry) => entry.organizationTaskId === taskId),
        alliances: organization.diplomacy.alliances
      };
    }, { key: PROFILE, taskId: journal.remoteTask });
    assert.equal(restored.lobbying.outcome, terminal === "SUCCESS" ? "accepted" : "rejected");
    assert.equal(restored.alliances.some((entry) => entry.status === "active"), allianceAuthorized);
    assert.deepEqual(pageErrors, []);
    assert(requests.knowledge >= (resume ? 0 : 1));
    assert(requests.decision >= (resume ? 0 : 1));
    assert.equal(requests.mandate, resume ? 0 : 1);
    assert.equal(requests.order, resume ? 0 : 1);
    assert(requests.taskRead >= 2 && requests.save >= 2);

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      chain: ["knowledge", "AINPC council", "NexusKernel diplomacy mandate", "orgFlow task", "cloud lobbying result", "alliance gate"],
      terminalResult: terminal,
      lobbyingOutcome: restored.lobbying.outcome,
      allianceAuthorized,
      cloudReloadVerified: true,
      requests,
      screenshot: path.basename(screenshotPath)
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    journal.stage = "complete";
    journal.completedAt = new Date().toISOString();
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
