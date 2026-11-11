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

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
    await page.goto("http://127.0.0.1:8780/", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const result = await page.evaluate(async () => {
      const taskTypes = ["supply", "drill", "patrol", "intelligence", "diplomacy"];
      const failures = [];
      for (const taskType of taskTypes) {
        try {
          return { taskType, response: await DongzhouIntegration.npcAssignment("ZuoRu", taskType, "01") };
        } catch (error) {
          failures.push(`${taskType}:${error.code || error.message}`);
        }
      }
      throw new Error(failures.join(","));
    });
    const support = result.response.assignment.managerSupport;
    assert.equal(support.managerNpcId, "6195011151089261734");
    assert.equal(support.factor, 0);
    assert.equal(support.affection, null);
    assert.deepEqual(support.relationships, []);
    console.log(JSON.stringify({ result: "PASS", taskType: result.taskType, managerSupport: support }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
