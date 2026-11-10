"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "..", "output", "playwright-runtime", "node_modules", "playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const SCREENSHOT = path.resolve(__dirname, "..", "output", "campaign-route-live.png");
const SYSTEM_CHROMIUM = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft Edge\\Application\\msedge.exe"
].find((candidate) => candidate && fs.existsSync(candidate));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(SYSTEM_CHROMIUM ? { executablePath: SYSTEM_CHROMIUM } : {}) });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  try {
    await page.goto(URL, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await page.evaluate(async () => {
      const key = "dongzhou-h5-profile-v2";
      const profile = JSON.parse(localStorage.getItem(key));
      profile.completed = ["01"];
      profile.lastStage = "01";
      profile.campaignResources.provisions = 100;
      localStorage.setItem(key, JSON.stringify(profile));
      await window.DongzhouIntegration.persist(profile);
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await page.waitForFunction(() => document.querySelector("#focusRouteProof")?.textContent.includes("行军 2 军粮"), null, { timeout: 30000 });
    const layout = await page.locator("#focusRouteProof").evaluate((element) => {
      const rect = element.getBoundingClientRect();
      return { text: element.textContent, width: rect.width, height: rect.height, viewport: innerWidth };
    });
    assert(layout.width > 0 && layout.height > 0 && layout.width <= layout.viewport);
    fs.mkdirSync(path.dirname(SCREENSHOT), { recursive: true });
    await page.screenshot({ path: SCREENSHOT, fullPage: false });
    await page.click("#focusStageButton");
    await page.waitForFunction(() => {
      const battle = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "null");
      return battle?.campaignRoute?.routeId === "campaign_progression_900001_900002";
    }, null, { timeout: 30000 });
    const result = await page.evaluate(() => ({
      profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")),
      battle: JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2"))
    }));
    assert.strictEqual(result.profile.campaignResources.provisions, 98);
    assert.strictEqual(result.battle.campaignRoute.provisionCost, 2);
    assert.deepStrictEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", routeId: result.battle.campaignRoute.routeId, provisions: 98, screenshot: SCREENSHOT }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
