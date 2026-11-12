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

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
assert.notEqual(new URL(url).searchParams.get("offline"), "1");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await page.waitForFunction(() => {
      const button = document.querySelector("#officeLogisticsBriefing");
      return button && !button.disabled;
    }, null, { timeout: 60000 });

    const selectedHero = await page.locator("#officeMemberSelect").inputValue();
    const briefingResponsePromise = page.waitForResponse(
      (response) => /\/organization\/logistics-briefings\/[^/]+$/.test(new URL(response.url()).pathname),
      { timeout: 120000 }
    );
    await page.click("#officeLogisticsBriefing");
    const briefingResponse = await briefingResponsePromise;
    assert.equal(briefingResponse.status(), 200, await briefingResponse.text());
    const briefingBody = await briefingResponse.json();
    const briefingResult = briefingBody.data || briefingBody;
    const receipt = briefingResult.briefingReceipt;
    assert.equal(briefingResult.state, "COMPLETED");
    assert.equal(receipt.heroId, selectedHero);
    assert.equal(receipt.kernel.module, "dongzhou_logistics_briefing");
    assert.equal(receipt.kernel.state, "SEALED");
    assert.deepEqual(receipt.ainpcDelivery, { market: "DELIVERED", warehouse: "DELIVERED" });
    assert.equal(receipt.exchange.priceUnits, 20);
    assert.equal(receipt.exchange.provisionsPerLot, 12);
    await page.waitForFunction(() => /仓情 · [0-9a-f]{8}/.test(document.querySelector("#officeLogisticsBriefing")?.textContent || ""));

    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults .office-source-choice:not([disabled])", { timeout: 60000 });
    await page.locator("#officeKnowledgeResults .office-source-choice:not([disabled])").first().click();
    let thoughtResponse;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const thoughtResponsePromise = page.waitForResponse(
        (response) => /\/npcs\/[^/]+\/thoughts$/.test(new URL(response.url()).pathname),
        { timeout: 180000 }
      );
      await page.click("#officeThoughtButton");
      thoughtResponse = await thoughtResponsePromise;
      if (thoughtResponse.status() === 200) break;
      if (thoughtResponse.status() !== 503 || attempt === 2) break;
      await page.waitForFunction(() => !document.querySelector("#officeThoughtButton")?.disabled, null, { timeout: 30000 });
      await page.waitForTimeout(5000);
    }
    const thoughtBody = await thoughtResponse.json();
    const thoughtResult = thoughtBody.data || thoughtBody;
    const thoughtBound = thoughtResponse.status() === 200;
    if (thoughtBound) {
      assert.equal(thoughtResult.state, "COMPLETED");
      assert.equal(thoughtResult.thoughtReceipt.logisticsBriefing.requestId, receipt.requestId);
      assert.equal(thoughtResult.thoughtReceipt.logisticsBriefing.digest, receipt.digest);
    } else {
      assert.equal(thoughtResponse.status(), 503, JSON.stringify(thoughtBody));
      assert.equal(thoughtBody.error?.code, "npc_thought_context_unavailable");
    }

    const layout = await page.evaluate(() => ({
      viewportWidth: document.documentElement.clientWidth,
      documentWidth: document.documentElement.scrollWidth,
      buttonText: document.querySelector("#officeLogisticsBriefing")?.textContent,
    }));
    assert.ok(layout.documentWidth <= layout.viewportWidth, JSON.stringify(layout));
    assert.deepEqual(pageErrors, []);
    const output = path.resolve(__dirname, "../output/integration-validation/live-logistics-briefing-mobile.png");
    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator("#campaignOfficeDrawer").screenshot({ path: output });
    assert.ok(fs.statSync(output).size > 8000);
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real_upstreams_no_interception",
      heroId: selectedHero,
      inventoryRevision: receipt.inventoryRevision,
      availableLots: receipt.exchange.availableLots,
      briefingDigest: receipt.digest,
      thoughtBound,
      thoughtDigest: thoughtBound ? thoughtResult.thoughtReceipt.digest : null,
      mobileNoOverflow: true,
      screenshot: output,
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
