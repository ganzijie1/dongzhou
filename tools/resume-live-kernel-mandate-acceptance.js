"use strict";

const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const journalPath = process.argv[2];
const journal = JSON.parse(fs.readFileSync(journalPath, "utf8"));
assert(journal.installation && journal.remoteTask && journal.mandateId);
const base = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const profileKey = "dongzhou-h5-profile-v2";
const battleKey = "dongzhou-h5-battle-v2";
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const resultPath = path.join(outputDirectory, "live-kernel-mandate-complete12.json");
const screenshotPath = path.join(outputDirectory, "live-kernel-mandate-complete12.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));
const saveJournal = () => fs.writeFileSync(journalPath, JSON.stringify(journal, null, 2));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    const pageErrors = [];
    const requests = { order: 0, taskRead: 0, save: 0 };
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      const url = new URL(response.url()).pathname;
      const method = response.request().method();
      if (url.endsWith("/organization/tasks") && method === "POST") requests.order += 1;
      if (url.includes("/organization/tasks/") && method === "GET") requests.taskRead += 1;
      if (url.endsWith("/save") && method === "PUT") requests.save += 1;
    });
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const initial = await page.evaluate(({ profileKey, taskId }) => {
      const profile = JSON.parse(localStorage.getItem(profileKey));
      return { month: profile.organization.month, task: profile.organization.tasks.find((entry) => entry.remoteResult === taskId) };
    }, { profileKey, taskId: journal.remoteTask });
    assert(initial.task && initial.task.mandate?.id === journal.mandateId);
    assert.equal(initial.task.status, "active");
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.backend.orgFlow === true, { timeout: 45000 });

    journal.stage = "resume-advance-due";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(({ key, month }) => JSON.parse(localStorage.getItem(key)).organization.month > month, { key: profileKey, month: initial.month }, { timeout: 90000 });

    const terminal = await page.evaluate(async (taskId) => {
      const deadline = Date.now() + 300000;
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
    }, journal.remoteTask);
    assert(terminal && terminal.final_result === "SUCCESS", "resumed organization task did not complete successfully");

    journal.stage = "resume-reconcile";
    saveJournal();
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(({ key, mandateId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      return organization.pendingSupport.some((entry) => entry.mandate?.id === mandateId)
        && organization.mandates.some((entry) => entry.id === mandateId && entry.state === "FULFILLED");
    }, { key: profileKey, mandateId: journal.mandateId }, { timeout: 90000 });
    await page.locator("#officeMandateLedger").scrollIntoViewIfNeeded();
    assert.match(await page.locator("#officeMandateLedger").innerText(), /复命待战/);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    assert(fs.statSync(screenshotPath).size > 10000);

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const restored = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), profileKey);
    assert(restored.organization.pendingSupport.some((entry) => entry.mandate?.id === journal.mandateId));

    journal.stage = "resume-battle";
    saveJournal();
    await page.click("#focusStageButton");
    await page.waitForFunction((key) => Boolean(localStorage.getItem(key)), battleKey, { timeout: 90000 });
    const battle = await page.evaluate(({ profileKey, battleKey }) => ({
      profile: JSON.parse(localStorage.getItem(profileKey)),
      battle: JSON.parse(localStorage.getItem(battleKey)),
      log: document.querySelector("#battleLog").innerText
    }), { profileKey, battleKey });
    assert.equal(battle.battle.organizationSupport.mandates[0].id, journal.mandateId);
    assert.equal(battle.battle.organizationSupport.councils.length, 1);
    assert.match(battle.log, /内核军令/);
    assert.equal(pageErrors.length, 0);
    assert.equal(requests.order, 0, "resume must not create another organization task");
    assert(requests.taskRead > 0 && requests.save >= 2);

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception-resumed",
      knowledgeBound: true,
      npcCouncilBound: true,
      nexusMandateBound: true,
      organizationTask: journal.remoteTask,
      terminalResult: terminal.final_result,
      mandateId: journal.mandateId,
      battleMandateVisible: true,
      cloudReloadVerified: true,
      newOrdersDuringResume: requests.order,
      taskReads: requests.taskRead,
      cloudWrites: requests.save,
      screenshot: path.basename(screenshotPath)
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    journal.stage = "complete";
    journal.completedAt = new Date().toISOString();
    saveJournal();
    console.log(JSON.stringify(result));
  } catch (error) {
    journal.stage = "resume-failed";
    journal.errorType = error.name;
    journal.error = String(error.message).slice(0, 300);
    saveJournal();
    console.error(JSON.stringify({ result: "FAIL", stage: journal.stage, errorType: error.name, details: journal.error }));
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
