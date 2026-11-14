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
    const selection = await page.evaluate(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      const heroId = document.querySelector("#officeMemberSelect").value;
      const stageId = String(profile.campaign?.currentStage || profile.currentStage || "01");
      const source = profile.organization?.selectedSources?.[stageId];
      return { heroId, stageId, knowledgeId: source?.knowledgeId };
    });
    assert.ok(selection.heroId);
    assert.ok(selection.knowledgeId);

    await page.click("#officeRecollectionButton");
    await page.waitForFunction(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      return profile.organization?.recollections?.length === 1;
    }, null, { timeout: 30000 });
    const profile = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    const receipt = profile.organization.recollections[0];
    assert.equal(receipt.heroId, selection.heroId);
    assert.equal(receipt.knowledgeId, selection.knowledgeId);
    assert.ok(["dialogue_choice", "system_message"].includes(receipt.memoryType));
    assert.ok(["knowledge_dialogue", "latest_system_message"].includes(receipt.matchMode));
    assert.ok(receipt.memoryContent.length > 0);
    assert.match(receipt.memoryDigest, /^[0-9a-f]{64}$/);
    assert.equal(receipt.memoryReceipt.idempotencyKey, receipt.memoryId);
    assert.equal(receipt.memoryReceipt.digest, receipt.memoryDigest);
    assert.match(receipt.digest, /^[0-9a-f]{64}$/);
    assert.equal(receipt.kernel.module, "dongzhou_npc_recollection");
    assert.equal(receipt.kernel.state, "SEALED");
    assert.equal(receipt.kernel.moduleVersion, "1.1.0");
    await page.waitForFunction(() => document.querySelector("#officeRecollectionResult").textContent.includes("印记"));
    assert.equal(await page.locator(".office-memory-item.selected").count(), 1);
    assert.match(await page.locator("#officeRecollectionResult").innerText(), /已取为军议依据/);

    await page.click("#officeRecollectionButton");
    await page.waitForTimeout(1200);
    const countAfterReplay = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.recollections.length);
    assert.equal(countAfterReplay, 1);

    const councilCountBefore = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.length);
    const decisionResponse = page.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith("/decisions") && response.request().method() === "POST",
      { timeout: 180000 }
    );
    await page.locator("#officeDecisionForm button[type=submit]").click();
    const decision = await decisionResponse;
    assert.equal(decision.status(), 200, await decision.text());
    await page.waitForFunction((before) => {
      const councils = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}").organization?.councils || [];
      return councils.length > before;
    }, councilCountBefore, { timeout: 180000 });
    const council = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.at(-1));
    assert.equal(council.memory.idempotencyKey, receipt.memoryId);
    assert.equal(council.memory.digest, receipt.memoryDigest);

    const screenshot = path.resolve(__dirname, "../output/integration-validation/history-recollection-live.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/history-recollection-mobile-live.png");
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
    console.log(JSON.stringify({ result: "PASS", ...selection, memoryType: receipt.memoryType, matchMode: receipt.matchMode, digest: receipt.digest, councilMemoryDigest: council.memory.digest, replayCount: countAfterReplay, screenshot, mobileScreenshot }));
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
