"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const npcId = process.env.DONGZHOU_NOTICE_NPC_ID;
const loginRequestId = process.env.DONGZHOU_NOTICE_LOGIN_REQUEST_ID;
assert.ok(npcId && loginRequestId, "current NPC identity is required");
const message = "东郊军粮已至，诸官依令整备。";
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const delivery = await page.evaluate(async ({ npcId, loginRequestId, message }) => {
      const response = await fetch("/api/v2/NDLLMSendPublicMessage", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ aiId: npcId, loginRequestId, message }) });
      return { status: response.status, body: await response.json() };
    }, { npcId, loginRequestId, message });
    assert.equal(delivery.status, 200);
    assert.equal(delivery.body.success, true);

    await page.click("#campaignOfficeButton");
    await page.selectOption("#officeMemberSelect", "ZuoRu");
    await page.waitForFunction((expected) => document.querySelector("#officePublicNotices")?.textContent.includes(expected), message, { timeout: 30000 });
    const notices = await page.evaluate(async () => (await fetch("/api/dongzhou/v1/organization/public-notices")).json());
    const notice = notices.notices.find((entry) => entry.message === message);
    assert.ok(notice);
    assert.equal(notice.heroId, "ZuoRu");
    assert.equal(notice.kernel.module, "dongzhou_npc_public_notice");
    assert.equal(notice.kernel.state, "SEALED");
    assert.match(notice.digest, /^[0-9a-f]{64}$/);

    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults [data-knowledge-id][data-source-index]:not([disabled])", { timeout: 90000 });
    await page.locator("#officeKnowledgeResults [data-knowledge-id][data-source-index]:not([disabled])").first().click();
    const noticeItem = page.locator("#officePublicNotices li", { has: page.locator(`button[data-public-notice-id="${notice.messageId}"]`) });
    await noticeItem.locator("button[data-public-notice-id]").click();
    await noticeItem.getByText("已取为公议").waitFor();
    const councilCountBefore = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.length);
    const councilResponse = page.waitForResponse((response) => new URL(response.url()).pathname.endsWith("/decisions") && response.request().method() === "POST", { timeout: 180000 });
    await page.locator("#officeDecisionForm button[type=submit]").click();
    const decided = await councilResponse;
    assert.equal(decided.status(), 200, await decided.text());
    await page.waitForFunction(({ councilCountBefore, digest }) => {
      const councils = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils;
      return councils.length > councilCountBefore && councils.at(-1)?.publicNotice?.digest === digest;
    }, { councilCountBefore, digest: notice.digest }, { timeout: 180000 });
    const council = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.at(-1));
    assert.equal(council.memberId, "ZuoRu");
    assert.equal(council.publicNotice.messageId, notice.messageId);
    assert.equal(council.publicNotice.digest, notice.digest);
    assert.match(council.question, new RegExp(`告示印记：${notice.digest.slice(0, 12)}`));

    const screenshot = path.resolve(__dirname, "../output/integration-validation/npc-public-notice-live.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/npc-public-notice-mobile-live.png");
    const councilScreenshot = path.resolve(__dirname, "../output/integration-validation/npc-public-notice-council-live.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.locator("#officePublicNotices").screenshot({ path: screenshot });
    await page.locator("#officeDecisionResult").screenshot({ path: councilScreenshot });
    await page.setViewportSize({ width: 320, height: 760 });
    const layout = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth, panelWidth: document.querySelector("#officePublicNotices").getBoundingClientRect().width }));
    assert.ok(layout.scrollWidth <= layout.viewport, JSON.stringify(layout));
    assert.ok(layout.panelWidth <= layout.viewport, JSON.stringify(layout));
    await page.locator("#officePublicNotices").screenshot({ path: mobileScreenshot });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", messageId: notice.messageId, digest: notice.digest, councilId: council.id, screenshot, councilScreenshot, mobileScreenshot }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
