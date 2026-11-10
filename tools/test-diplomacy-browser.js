"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find((item) => item && fs.existsSync(item));
const BASE_URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8790/";

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  let cloud = {};
  let version = 1;
  let decisionCount = 0;
  await page.route("**/api/dongzhou/v1/**", async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    let body = {};
    if (pathname.endsWith("/sessions/guest")) body = { playerId: "diplomacy-browser" };
    else if (pathname.endsWith("/save") && request.method() === "GET") body = { version, payload: cloud };
    else if (pathname.endsWith("/save") && request.method() === "PUT") { cloud = request.postDataJSON().payload; body = { version: ++version, payload: cloud }; }
    else if (pathname.endsWith("/integration/status")) body = { services: { nexusKernel: { online: true }, orgFlow: { online: true }, aiNpc: { online: true }, knowledge: { online: true } }, organizationId: "court-test" };
    else if (pathname.includes("/knowledge/stages/")) body = { mode: "connected", results: [{ id: "dongzhou_stage_001", name: "第一回史料", summary: "诸侯合纵可御强敌", stageId: "01" }] };
    else if (pathname.endsWith("/npcs/sync")) body = { ready: true, npcs: [] };
    else if (/\/npcs\/[^/]+\/state$/.test(pathname)) body = { emotion: { data: { dominant: { emotion_type: "resolute", intensity: 70 } } }, affection: { data: { total: 1 } }, relationships: { data: { total: 2 } } };
    else if (/\/npcs\/[^/]+\/schedule$/.test(pathname)) body = { schedule: { data: { schedules: [] } } };
    else if (/\/npcs\/[^/]+\/decisions$/.test(pathname)) {
      decisionCount += 1;
      const requestBody = request.postDataJSON();
      body = { state: "COMPLETED", decision: { data: { type: "OPTION", index: 0, text: requestBody.options[0].text } } };
    } else return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ error: { message: pathname } }) });
    return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
  try {
    await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults >> text=第一回史料");
    await page.click("#officeDecisionForm button[type=submit]");
    await page.waitForSelector("#officeDecisionResult >> text=先固军粮");
    await page.selectOption("#officeDiplomacyTarget", "zheng");
    await page.fill("#officeDiplomacyProposal", "互通军情，共御强敌");
    await page.click("#officeLobbyButton");
    await page.waitForSelector("#officeDiplomacyResult >> text=可正式缔盟");
    await page.click("#officeAllianceButton");
    await page.waitForSelector("#officeAllianceLedger >> text=生效");
    await page.click("#officeBetrayButton");
    await page.waitForSelector("#officeAllianceLedger >> text=背盟待战");
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization);
    assert.equal(state.schemaVersion, 2);
    assert.equal(state.diplomacy.lobbying.length, 1);
    assert.equal(state.diplomacy.alliances[0].status, "broken");
    assert.equal(state.pendingSupport.filter((entry) => entry.id.startsWith("betrayal:")).length, 1);
    assert.equal(decisionCount, 2);
    assert.match(await page.locator("#officeBattleArchive").innerText(), /与郑国结盟/);
    assert.match(await page.locator("#officeBattleArchive").innerText(), /背盟：郑国/);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    assert.ok(overflow <= 1, "desktop must not overflow horizontally");
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])");
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#officeAllianceLedger >> text=背盟待战");
    assert.equal((await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.diplomacy.alliances.length)), 1);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", decisions: decisionCount, chain: ["史料", "军议", "游说", "盟约", "背盟战役"], reloadPreserved: true, horizontalOverflow: overflow }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
