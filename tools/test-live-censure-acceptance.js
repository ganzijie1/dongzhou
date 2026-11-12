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

const BASE = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const INSTALLATION = process.env.DONGZHOU_CENSURE_INSTALLATION;
const TASK_ID = process.env.DONGZHOU_CENSURE_TASK_ID;
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const resultPath = path.join(outputDirectory, "live-censure-affection-complete91.json");
const screenshotPath = path.join(outputDirectory, "live-censure-affection-complete91.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(fs.existsSync);

assert(INSTALLATION, "DONGZHOU_CENSURE_INSTALLATION is required");
assert(TASK_ID, "DONGZHOU_CENSURE_TASK_ID is required");

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((installation) => {
      localStorage.setItem("dongzhou-installation-id-v1", installation);
    }, INSTALLATION);
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });

    const initial = await page.evaluate(async (taskId) => {
      const task = await window.DongzhouIntegration.organizationTask(taskId);
      const inventory = await window.DongzhouIntegration.organizationInventory();
      return { task, inventory };
    }, TASK_ID);
    assert(initial.task.result?.data?.final_result || initial.task.result?.final_result, "task is not terminal");
    assert.equal(initial.task.review?.state, "REQUIRES_ACTION");
    const beforeAccount = initial.inventory.accounts.find((entry) => entry.resourceKey === "task.execution");

    const reviewed = await page.evaluate(async ({ taskId, actionId }) => (
      window.DongzhouIntegration.reviewOrganizationTask(taskId, {
        action_id: actionId,
        decision: "CENSURE",
      })
    ), { taskId: TASK_ID, actionId: initial.task.review.action.actionId });
    assert.equal(reviewed.state, "CENSURED");
    assert.equal(reviewed.inventoryReward, undefined);
    assert.equal(reviewed.npcConsequence.affectionType, "annoyance");
    assert.equal(reviewed.npcConsequence.severity, 58);
    assert(reviewed.npcConsequence.targetId);

    const replay = await page.evaluate(async ({ taskId, actionId }) => (
      window.DongzhouIntegration.reviewOrganizationTask(taskId, {
        action_id: actionId,
        decision: "CENSURE",
      })
    ), { taskId: TASK_ID, actionId: initial.task.review.action.actionId });
    assert.equal(replay.replayed, true);
    assert.equal(replay.npcConsequence.eventId, reviewed.npcConsequence.eventId);

    const delivered = await page.evaluate(async ({ taskId, heroId, targetId }) => {
      const deadline = Date.now() + 180000;
      let task;
      let state;
      while (Date.now() < deadline) {
        task = await window.DongzhouIntegration.organizationTask(taskId);
        state = await window.DongzhouIntegration.npcState(heroId);
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
      taskId: TASK_ID,
      heroId: reviewed.npcConsequence.heroId,
      targetId: reviewed.npcConsequence.targetId,
    });
    assert.equal(delivered.task?.npcConsequence?.event?.state, "DELIVERED");
    assert.equal(delivered.task?.npcConsequence?.memory?.state, "DELIVERED");
    assert.equal(delivered.task?.npcConsequence?.affection?.state, "DELIVERED");
    assert(delivered.matched, "authoritative AINPC annoyance was not persisted before timeout");
    assert.equal(Number(delivered.matched.max_value ?? delivered.matched.maxValue), 5.8);

    const inventoryAfter = await page.evaluate(() => window.DongzhouIntegration.organizationInventory());
    const afterAccount = inventoryAfter.accounts.find((entry) => entry.resourceKey === "task.execution");
    assert.equal(Number(afterAccount?.balance || 0), Number(beforeAccount?.balance || 0));
    assert.equal(inventoryAfter.revision, initial.inventory.revision);
    assert.deepEqual(pageErrors, []);

    fs.mkdirSync(outputDirectory, { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      taskId: TASK_ID,
      decision: "CENSURE",
      heroId: reviewed.npcConsequence.heroId,
      npcId: reviewed.npcConsequence.npcId,
      targetId: reviewed.npcConsequence.targetId,
      affectionType: delivered.matched.dominant_affection_type ?? delivered.matched.dominantAffectionType,
      affectionValue: Number(delivered.matched.max_value ?? delivered.matched.maxValue),
      eventState: delivered.task.npcConsequence.event.state,
      memoryState: delivered.task.npcConsequence.memory.state,
      inventoryUnchanged: true,
      replayedExactlyOnce: replay.replayed,
      screenshot: path.basename(screenshotPath),
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + "\n");
    console.log(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
