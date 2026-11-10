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
const privateDirectory = path.resolve(__dirname, "../.agentwork/root/kernel-mandate-complete12");
const privatePath = path.join(privateDirectory, "acceptance-private.json");
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const resultPath = path.join(outputDirectory, "live-kernel-mandate-complete12.json");
const screenshotPath = path.join(outputDirectory, "live-kernel-mandate-complete12.png");
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
    const requests = { knowledge: 0, decision: 0, mandate: 0, order: 0, taskRead: 0, save: 0 };
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      const url = new URL(response.url()).pathname;
      const method = response.request().method();
      if (url.includes("/knowledge/stages/")) requests.knowledge += 1;
      if (url.includes("/decisions")) requests.decision += 1;
      if (url.endsWith("/court/mandates")) requests.mandate += 1;
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
    }, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");

    journal.stage = "knowledge";
    saveJournal();
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults article", { timeout: 90000 });
    await page.click('#officeKnowledgeResults [data-source-index="0"]');
    await page.waitForSelector("#officeKnowledgeResults >> text=已取为据");

    journal.stage = "npc-council";
    saveJournal();
    const decisionResponse = page.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith("/decisions") && response.request().method() === "POST",
      { timeout: 180000 }
    );
    await page.locator("#officeDecisionForm button[type=submit]").click();
    assert.equal((await decisionResponse).status(), 200);
    await page.waitForFunction((key) => JSON.parse(localStorage.getItem(key)).organization.councils.length > 0, PROFILE, { timeout: 180000 });
    const council = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)).organization.councils.at(-1), PROFILE);
    assert.equal(council.memberId, "ZuoRu");
    assert.equal(council.stageId, "01");
    assert(council.evidenceSource?.work);

    await page.selectOption("#officeTaskType", "supply");
    await page.locator("#officeUseCouncil").check();
    journal.stage = "kernel-mandate-and-order";
    saveJournal();
    await page.click("#officeIssueButton");
    await page.waitForFunction((key) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.tasks.some((task) => task.remoteResult && task.mandate)
        && organization.mandates.some((mandate) => mandate.state === "ORDERED");
    }, PROFILE, { timeout: 120000 });
    const issued = await page.evaluate((key) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      const task = organization.tasks.find((entry) => entry.remoteResult && entry.mandate);
      return { task, mandate: organization.mandates.find((entry) => entry.id === task.mandate.id) };
    }, PROFILE);
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
    assert.equal(issued.mandate.council.requestId, council.id);
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

    journal.stage = "report-trigger";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, { timeout: 90000 });
    const terminal = await page.evaluate(async (taskId) => {
      const deadline = Date.now() + 240000;
      while (Date.now() < deadline) {
        const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(taskId));
        if (response.ok) {
          const body = await response.json();
          const task = body.result?.data || body.result;
          if (task?.final_result) return task;
        }
        await new Promise((resolve) => setTimeout(resolve, 3000));
      }
      return null;
    }, issued.task.remoteResult);
    assert(terminal && terminal.final_result === "SUCCESS", "real organization task did not complete successfully");

    journal.stage = "reconcile";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction((key) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.pendingSupport.some((entry) => entry.mandate)
        && organization.mandates.some((entry) => entry.state === "FULFILLED");
    }, PROFILE, { timeout: 90000 });

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const restored = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), PROFILE);
    assert(restored.organization.pendingSupport.some((entry) => entry.mandate?.id === issued.mandate.id));
    assert(restored.organization.mandates.some((entry) => entry.id === issued.mandate.id && entry.state === "FULFILLED"));

    journal.stage = "battle";
    saveJournal();
    await page.click("#focusStageButton");
    await page.waitForFunction((key) => Boolean(localStorage.getItem(key)), BATTLE, { timeout: 90000 });
    const battle = await page.evaluate(({ profileKey, battleKey }) => ({
      profile: JSON.parse(localStorage.getItem(profileKey)),
      battle: JSON.parse(localStorage.getItem(battleKey)),
      log: document.querySelector("#battleLog").innerText
    }), { profileKey: PROFILE, battleKey: BATTLE });
    assert.equal(battle.battle.organizationSupport.mandates[0].id, issued.mandate.id);
    assert.equal(battle.battle.organizationSupport.councils[0].id, council.id);
    assert.equal(battle.battle.organizationSupport.provisions, 24);
    assert.match(battle.log, /内核军令/);
    assert.match(battle.log, new RegExp(issued.mandate.digest.slice(0, 10)));
    assert.equal(pageErrors.length, 0);
    assert(requests.knowledge > 0 && requests.decision === 1 && requests.mandate === 1 && requests.order === 1);
    assert(requests.taskRead > 0 && requests.save >= 4);

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      chain: ["knowledge", "npcCouncil", "nexusMandate", "organizationTask", "battleSupport"],
      mandateDigestPrefix: issued.mandate.digest.slice(0, 10),
      terminalResult: terminal.final_result,
      rewardProvisions: 24,
      cloudReloadVerified: true,
      battleLogVerified: true,
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
