"use strict";

const fs = require("fs");
const path = require("path");
let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const journal = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const base = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext();
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const snapshot = await page.evaluate(async (taskId) => {
      const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(taskId));
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return { status: response.status, body: await response.json(), organization: { month: profile.organization.month, task: profile.organization.tasks.find((entry) => entry.remoteResult === taskId) } };
    }, journal.remoteTask);
    console.log(JSON.stringify(snapshot));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
