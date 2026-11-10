"use strict";
const assert = require("assert");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }
const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8781/";
assert.notStrictEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    const responsePromise = page.waitForResponse((response) => response.url().includes("/knowledge/stages/"));
    await page.click("#officeStageKnowledgeButton");
    const response = await responsePromise;
    assert.strictEqual(response.status(), 200);
    const body = await response.json();
    assert.strictEqual(body.mode, "connected");
    assert.ok(body.results.length > 0);
    await page.waitForSelector("#officeKnowledgeResults article");
    await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.knowledge.some((entry) => entry.stageId === "01"));
    const screenshot = path.resolve(__dirname, "../output/integration-validation/published-stage-live.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.screenshot({ path: screenshot });
    assert.deepStrictEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", mode: "real_upstreams_no_mock_routes", stage: body.stageId, ids: body.results.map((entry) => entry.id), screenshot }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
