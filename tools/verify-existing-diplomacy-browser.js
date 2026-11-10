"use strict";

const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }

const BASE = (process.env.DONGZHOU_BASE_URL || "http://127.0.0.1:8780/").replace(/\/?$/, "/");
const PROFILE = "dongzhou-h5-profile-v2";
const TASK = "c27e41ed-2304-5f02-a087-7f89bf441681";
const journal = JSON.parse(fs.readFileSync(path.resolve(__dirname, "../.agentwork/root/diplomacy-acceptance-20261109-diplomacy-v1-private.json"), "utf8"));
const executablePath = ["C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const pageErrors = [], requests = { taskReads: 0, taskCreates: 0, saves: 0 };
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), journal.installation);
    const page = await context.newPage();
    page.on("pageerror", error => pageErrors.push(error.message));
    page.on("response", response => {
      const pathname = new URL(response.url()).pathname;
      const method = response.request().method();
      if (pathname.includes("/organization/tasks/") && method === "GET") requests.taskReads += 1;
      if (pathname.endsWith("/organization/tasks") && method === "POST") requests.taskCreates += 1;
      if (pathname.endsWith("/save") && method === "PUT") requests.saves += 1;
    });
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#officeTaskLedger li.active, #officeTaskLedger li.failed", { timeout: 45000 });
    const before = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), PROFILE);
    const tasksBefore = before.organization.tasks.filter(task => task.type === "diplomacy");
    assert.equal(tasksBefore.length, 1);
    assert.equal(tasksBefore[0].remoteResult, TASK);
    assert(["active", "failed"].includes(tasksBefore[0].status));

    if (tasksBefore[0].status === "active") {
      await page.click("#officeAdvanceButton");
      await page.waitForFunction(({ key, taskId }) => {
        const profile = JSON.parse(localStorage.getItem(key));
        return profile.organization.tasks.some(task => task.remoteResult === taskId && task.status === "failed" && task.remoteFinalResult === "FAILURE");
      }, { key: PROFILE, taskId: TASK }, { timeout: 90000 });
    }
    await page.waitForSelector("#officeTaskLedger li.failed", { timeout: 30000 });
    const after = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), PROFILE);
    const tasksAfter = after.organization.tasks.filter(task => task.type === "diplomacy");
    assert.equal(tasksAfter.length, 1);
    assert.equal(tasksAfter[0].remoteResult, TASK);
    assert.equal(tasksAfter[0].status, "failed");
    assert.equal(tasksAfter[0].remoteFinalResult, "FAILURE");
    assert.equal(requests.taskCreates, 0);
    if (tasksBefore[0].status === "active") assert(requests.taskReads >= 1);
    assert(requests.saves >= 0);
    assert.deepEqual(pageErrors, []);
    const out = path.resolve(__dirname, "../output/integration-validation/diplomacy-existing-task-browser.png");
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out, fullPage: false });
    const result = { result: "PASS", taskId: TASK, localStatus: "failed", remoteFinalResult: "FAILURE", taskCount: 1, ...requests, pageErrors: 0 };
    fs.writeFileSync(path.resolve(__dirname, "../output/integration-validation/diplomacy-existing-task-browser.json"), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error.stack || error.message); process.exitCode = 1; });
