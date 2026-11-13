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
const screenshot = path.resolve(__dirname, "../output/integration-validation/nexus-mandate-approval-complete27.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));

(async () => {
  fs.mkdirSync(path.dirname(screenshot), { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.evaluate(() => {
      const input = {
        stage_id: "01", hero_id: "ZuoRu", knowledge_id: "dongzhou_stage_001",
        evidence_source_index: 0, council_request_id: "00000000-0000-4000-8000-000000000001",
        task_type: "supply", schedule_plan_id: "plan-browser", schedule_event_id: "event-supply",
        client_request_id: "00000000-0000-4000-8000-000000000002"
      };
      const result = {
        state: "REQUIRES_ACTION",
        mandate: { id: "dongzhou:test:00000000-0000-4000-8000-000000000002", digest: "a".repeat(64), evidence: { name: "东郊旧闻" }, assignment: { name: "转运军粮" } },
        action: { actionId: "00000000-0000-4000-8000-000000000003", code: "seal_court_mandate", type: "confirmation", options: ["APPROVE", "REVISE", "REJECT"] }
      };
      localStorage.setItem("dongzhou-pending-mandate-v1:visual-acceptance", JSON.stringify({ input, result }));
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#officeMandateApproval:not([hidden])");
    assert.match(await page.locator("#officeMandateApproval").innerText(), /内核待裁/);
    assert.equal(await page.locator("#officeMandateApproveButton").innerText(), "签发");
    assert(await page.locator("#officeMandateReviseButton").isVisible());
    await page.setViewportSize({ width: 320, height: 700 });
    await page.locator("#officeMandateApproval").scrollIntoViewIfNeeded();
    assert(await page.locator("#officeMandateApproveButton").isVisible());
    assert(await page.locator("#officeMandateReviseButton").isVisible());
    const bounds = await page.locator("#officeMandateApproval").evaluate((element) => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth };
    });
    assert(bounds.left >= 0 && bounds.right <= bounds.viewport + 1 && bounds.scrollWidth <= bounds.viewport + 1);
    await page.screenshot({ path: screenshot, fullPage: true });
    assert(fs.statSync(screenshot).size > 10000);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", desktopRefreshRecovery: true, mobile320NoOverflow: true, screenshot: path.basename(screenshot) }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
