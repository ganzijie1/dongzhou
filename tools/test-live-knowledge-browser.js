"use strict";
const assert = require("assert");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }
const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
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
    const codexResponsePromise = page.waitForResponse((candidate) => candidate.url().includes("/knowledge/codex"));
    await page.click("#officeCodexToggle");
    const codexResponse = await codexResponsePromise;
    assert.strictEqual(codexResponse.status(), 200);
    await page.waitForFunction(() => document.querySelectorAll("#officeCodexList [data-codex-id]").length > 0);
    const summary = await page.locator("#officeCodexSummary").innerText();
    assert.match(summary, /已得 \d+ 卷 · 当前 \d+ 卷/);
    assert.ok(await page.locator("#officeCodexStage option").count() > 1);
    const firstEntry = body.results[0];
    const expectedSource = firstEntry.sourceDetails?.[0]?.url || firstEntry.sources?.[0]?.url;
    if (expectedSource && /^https?:\/\//.test(expectedSource)) {
      assert.strictEqual(await page.locator("#officeCodexDetail a").first().getAttribute("href"), expectedSource);
    }
    await page.fill("#officeCodexFilter", "no-such-dongzhou-codex-entry");
    await page.waitForFunction(() => document.querySelector("#officeCodexSummary").textContent.includes("当前 0 卷"));
    await page.fill("#officeCodexFilter", "");
    await page.selectOption("#officeCodexStage", String(firstEntry.stageId));
    await page.waitForFunction(() => document.querySelectorAll("#officeCodexList [data-codex-id]").length > 0);
    const screenshot = path.resolve(__dirname, "../output/integration-validation/published-stage-live.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/knowledge-codex-mobile-live.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.locator("#officeCodexPanel").screenshot({ path: screenshot });
    await page.setViewportSize({ width: 320, height: 760 });
    const mobileLayout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      panelWidth: document.querySelector("#officeCodexPanel").getBoundingClientRect().width,
    }));
    assert.ok(mobileLayout.scrollWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    assert.ok(mobileLayout.panelWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    await page.locator("#officeCodexPanel").screenshot({ path: mobileScreenshot });
    const isolatedContext = await browser.newContext();
    const isolatedPage = await isolatedContext.newPage();
    await isolatedPage.goto(url, { waitUntil: "domcontentloaded" });
    await isolatedPage.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const isolatedCodex = await isolatedPage.evaluate(async () => (await fetch("/api/dongzhou/v1/knowledge/codex")).json());
    assert.deepStrictEqual(isolatedCodex.results, []);
    await isolatedContext.close();
    assert.deepStrictEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", mode: "real_upstreams_no_mock_routes", stage: body.stageId, ids: body.results.map((entry) => entry.id), codexSummary: summary, playerIsolation: true, mobileNoOverflow: true, screenshot, mobileScreenshot }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
