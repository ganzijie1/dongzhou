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
const OUTPUT_DIR = path.resolve(__dirname, "..", "output", "integration-validation");
const SYSTEM_CHROMIUM = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft Edge\\Application\\msedge.exe"
].find((candidate) => candidate && fs.existsSync(candidate));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(SYSTEM_CHROMIUM ? { executablePath: SYSTEM_CHROMIUM } : {}) });
  try {
    const scenarios = [
      { name: "desktop", viewport: { width: 1280, height: 800 }, method: "npc_dialog", provisions: 99, morale: 66 },
      { name: "mobile", viewport: { width: 390, height: 844 }, isMobile: true, method: "fixed_point", provisions: 97, morale: 76 }
    ];
    const accepted = [];
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    for (const scenario of scenarios) {
      const context = await browser.newContext({ viewport: scenario.viewport, isMobile: Boolean(scenario.isMobile) });
      const page = await context.newPage();
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await page.goto(URL, { waitUntil: "domcontentloaded" });
      await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
      await page.evaluate(async () => {
        const key = "dongzhou-h5-profile-v2";
        const profile = JSON.parse(localStorage.getItem(key));
        profile.completed = ["01"];
        profile.lastStage = "01";
        profile.campaignResources = { provisions: 100, morale: 70 };
        profile.routePreferences = {};
        localStorage.setItem(key, JSON.stringify(profile));
        await window.DongzhouIntegration.persist(profile);
      });
      await page.reload({ waitUntil: "domcontentloaded" });
      await page.waitForSelector("#focusRouteOptions:not([hidden]) button", { timeout: 45000 });
      const options = await page.locator("#focusRouteOptions button").evaluateAll((buttons) => buttons.map((button) => ({
        method: button.dataset.routeMethod,
        right: button.getBoundingClientRect().right,
        left: button.getBoundingClientRect().left
      })));
      assert.deepStrictEqual(options.map((option) => option.method), ["campaign_progression", "fixed_point", "npc_dialog"]);
      assert(options.every((option) => option.left >= 0 && option.right <= scenario.viewport.width));
      const routeProof = await page.locator("#focusRouteProof").textContent();
      assert(routeProof.includes("双史料封印"));
      assert.strictEqual(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), true);
      await page.click(`[data-route-method="${scenario.method}"]`);
      await page.waitForFunction((method) => document.querySelector(`[data-route-method="${method}"]`)?.getAttribute("aria-checked") === "true", scenario.method);
      const screenshot = path.join(OUTPUT_DIR, `campaign-routes-${scenario.name}-live.png`);
      await page.screenshot({ path: screenshot, fullPage: false });
      await page.click("#focusStageButton");
      await page.waitForFunction((method) => {
        const battle = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "null");
        return battle?.campaignRoute?.method === method;
      }, scenario.method, { timeout: 30000 });
      const result = await page.evaluate(() => ({
        profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")),
        battle: JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2"))
      }));
      assert.strictEqual(result.profile.campaignResources.provisions, scenario.provisions);
      assert.strictEqual(result.profile.campaignResources.morale, scenario.morale);
      assert.strictEqual(result.battle.campaignRoute.receipt.kernel.module, "dongzhou_campaign_route");
      assert.strictEqual(result.battle.campaignRoute.receipt.kernel.moduleVersion, "1.2.0");
      assert.strictEqual(result.battle.campaignRoute.receipt.kernel.state, "SEALED");
      assert.strictEqual(result.battle.campaignRoute.receipt.digest.length, 64);
      assert.strictEqual(result.battle.campaignRoute.receipt.attestation.length, 64);
      assert.deepStrictEqual(result.battle.campaignRoute.knowledgeWitnesses.from.knowledgeIds, ["dongzhou_stage_001"]);
      assert.deepStrictEqual(result.battle.campaignRoute.knowledgeWitnesses.to.knowledgeIds, ["dongzhou_stage_002"]);
      assert.strictEqual(result.battle.campaignRoute.knowledgeWitnesses.from.digest.length, 64);
      assert.strictEqual(result.battle.campaignRoute.knowledgeWitnesses.to.digest.length, 64);
      assert.deepStrictEqual(errors, []);
      accepted.push({
        name: scenario.name,
        method: scenario.method,
        routeId: result.battle.campaignRoute.routeId,
        receipt: result.battle.campaignRoute.receipt.digest,
        screenshot
      });
      await context.close();
    }
    console.log(JSON.stringify({ result: "PASS", accepted }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
