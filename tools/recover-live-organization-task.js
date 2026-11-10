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

const base = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const installation = process.env.DONGZHOU_INSTALLATION_ID;
const taskId = process.env.DONGZHOU_TASK_ID;
const output = process.env.DONGZHOU_RECOVERY_OUTPUT
  || path.resolve(__dirname, "../output/integration-validation/live-task-recovery.json");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find(fs.existsSync);

assert(installation, "DONGZHOU_INSTALLATION_ID is required");
assert(taskId, "DONGZHOU_TASK_ID is required");

async function readRemote(page) {
  return page.evaluate(async (id) => {
    const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(id));
    if (!response.ok) throw new Error("organization task read failed: " + response.status);
    const body = await response.json();
    return body.result?.data || body.result;
  }, taskId);
}

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), installation);
    const page = await context.newPage();
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return profile.organization.backend.orgFlow
        && profile.organization.backend.aiNpc
        && profile.organization.backend.knowledge
        && profile.organization.backend.nexusKernel;
    }, undefined, { timeout: 45000 });
    await page.waitForFunction((id) => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return profile.organization.tasks.some((task) => task.remoteResult === id);
    }, taskId, { timeout: 45000 });

    let remote = await readRemote(page);
    assert(remote.final_result || remote.execution_started_game_time != null, "task has not entered execution state");
    for (let advance = 0; !remote.final_result && advance < 4; advance += 1) {
      const month = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.month);
      await page.click("#officeAdvanceButton");
      await page.waitForFunction((previous) => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.month > previous, month, { timeout: 90000 });
      remote = await page.evaluate(async (id) => {
        const deadline = Date.now() + 60000;
        while (Date.now() < deadline) {
          const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(id));
          if (response.ok) {
            const body = await response.json();
            const data = body.result?.data || body.result;
            if (data?.final_result) return data;
          }
          await new Promise((resolve) => setTimeout(resolve, 3000));
        }
        return readRemoteState(id);

        async function readRemoteState(task) {
          const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(task));
          if (!response.ok) return null;
          const body = await response.json();
          return body.result?.data || body.result;
        }
      }, taskId);
    }
    assert(remote?.final_result, "task did not reach a terminal result after the recovery clock advance");

    await page.click("#officeAdvanceButton");
    await page.waitForFunction((id) => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return profile.organization.tasks.some((task) => task.remoteResult === id && task.status !== "active");
    }, taskId, { timeout: 90000 });
    const local = await page.evaluate((id) => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return profile.organization.tasks.find((task) => task.remoteResult === id);
    }, taskId);
    const result = {
      result: "PASS",
      mode: "same-player-same-task-clock-recovery",
      taskId,
      remoteState: remote.state,
      remoteFinalResult: remote.final_result,
      localStatus: local.status,
      localMonth: local.resolvedMonth
    };
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
