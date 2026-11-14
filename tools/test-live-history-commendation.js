"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults [data-knowledge-id][data-source-index]:not([disabled])");
    await page.locator("#officeKnowledgeResults [data-knowledge-id][data-source-index]:not([disabled])").first().click();
    const heroId = await page.locator("#officeMemberSelect").inputValue();

    await page.click("#officeCommendButton");
    await page.waitForFunction(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      return profile.organization?.commendations?.length === 1;
    }, null, { timeout: 30000 });
    const profile = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    const receipt = profile.organization.commendations[0];
    assert.equal(receipt.heroId, heroId);
    assert.equal(receipt.affectionType, "appreciation");
    assert.equal(receipt.affectionDelta, 2);
    assert.equal(receipt.kernel.module, "dongzhou_npc_commendation");
    assert.equal(receipt.kernel.state, "SEALED");
    assert.match(receipt.digest, /^[0-9a-f]{64}$/);
    await page.waitForFunction(() => document.querySelector("#officeCommendationResult").textContent.includes("感激 +2"));
    const npcState = await page.evaluate(async (selectedHeroId) => {
      const response = await fetch(`api/dongzhou/v1/npcs/${encodeURIComponent(selectedHeroId)}/state`, { credentials: "same-origin" });
      return { status: response.status, body: await response.json() };
    }, heroId);
    assert.equal(npcState.status, 200);
    assert.ok(JSON.stringify(npcState.body).includes("appreciation"));

    await page.click("#officeCommendButton");
    await page.waitForTimeout(1200);
    const countAfterReplay = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.commendations.length);
    assert.equal(countAfterReplay, 1);

    const screenshot = path.resolve(__dirname, "../output/integration-validation/history-commendation-live.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/history-commendation-mobile-live.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.locator(".office-commendation").screenshot({ path: screenshot });
    await page.setViewportSize({ width: 320, height: 760 });
    const layout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      actionWidth: document.querySelector(".office-knowledge-actions").getBoundingClientRect().width
    }));
    assert.ok(layout.scrollWidth <= layout.viewport, JSON.stringify(layout));
    assert.ok(layout.actionWidth <= layout.viewport, JSON.stringify(layout));
    await page.locator(".office-commendation").screenshot({ path: mobileScreenshot });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", heroId, digest: receipt.digest, replayCount: countAfterReplay, screenshot, mobileScreenshot }));
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
