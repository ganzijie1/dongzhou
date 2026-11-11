"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find((item) => item && fs.existsSync(item));
const BASE_URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const WEB = path.resolve(__dirname, "../web-game");
const BASE_ORIGIN = new URL(BASE_URL).origin;

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  let cloud = {};
  let version = 1;
  let decisionCount = 0;
  const decisions = [];
  const npcSyncs = [];
  const scheduleGenerations = [];
  const mandates = [];
  const orders = [];
  await page.route("**/*", async (route) => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.origin !== BASE_ORIGIN || requestUrl.pathname.startsWith("/api/")) return route.fallback();
    const file = path.resolve(WEB, `.${decodeURIComponent(requestUrl.pathname === "/" ? "/index.html" : requestUrl.pathname)}`);
    if (!file.startsWith(`${WEB}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return route.fulfill({ status: 404, body: "not found" });
    const contentTypes = { ".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".json": "application/json", ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav" };
    return route.fulfill({ status: 200, contentType: contentTypes[path.extname(file)] || "application/octet-stream", body: fs.readFileSync(file) });
  });
  await page.route("**/api/dongzhou/v1/**", async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    let body = {};
    if (pathname.endsWith("/sessions/guest")) body = { playerId: "diplomacy-browser" };
    else if (pathname.endsWith("/save") && request.method() === "GET") body = { version, payload: cloud };
    else if (pathname.endsWith("/save") && request.method() === "PUT") { cloud = request.postDataJSON().payload; body = { version: ++version, payload: cloud }; }
    else if (pathname.endsWith("/integration/status")) body = { services: { nexusKernel: { online: true }, orgFlow: { online: true }, aiNpc: { online: true }, knowledge: { online: true } }, organizationId: "court-test" };
    else if (pathname.endsWith("/npcs/interaction-preference")) body = { enabled: request.postDataJSON().enabled, source: "dongzhou-player-settings", updatedAt: "2026-11-11T12:00:00Z" };
    else if (pathname.endsWith("/organization/roster")) body = { organization: { id: "court-test", name: "东周军府", state: "ACTIVE", growthContribution: 0 }, members: [] };
    else if (pathname.includes("/knowledge/stages/")) body = { mode: "connected", results: [{ id: "dongzhou_stage_001", name: "第一回史料", summary: "诸侯合纵可御强敌", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败与周宣王晚年", url: "https://ctext.org/shiji/zhou-ben-ji" }, { work: "《东周列国志》第一回", tier: "文学演绎", scope: "杜伯、左儒化厉索命", url: "https://zh.wikisource.org/zh-hans/东周列国志/第001回" }] }] };
    else if (pathname.endsWith("/npcs/sync")) { npcSyncs.push(request.postDataJSON()); body = { ready: true, npcs: [] }; }
    else if (/\/npcs\/[^/]+\/state$/.test(pathname)) body = { emotion: { data: { dominant: { emotion_type: "resolute", intensity: 70 } } }, affection: { data: { total: 1 } }, relationships: { data: { total: 2 } } };
    else if (pathname.includes("/assignments/")) { const taskType = pathname.split("/").at(-1); const heroId = decodeURIComponent(pathname.split("/").at(-3)); body = { assignment: { heroId, npcId: "42", runtimeState: "READY", planId: "plan-browser", generationId: "generation-browser", eventId: `event-${taskType}`, transactionId: taskType === "diplomacy" ? 9100106 : 9100103, name: taskType === "diplomacy" ? "折冲诸侯" : "转运军粮", type: taskType === "diplomacy" ? "外交" : "军需", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 70, affectionCount: 1, relationshipCount: 2 } } }; }
    else if (/\/npcs\/[^/]+\/schedule$/.test(pathname) && request.method() === "POST") { scheduleGenerations.push(decodeURIComponent(pathname.split("/").at(-2))); body = { schedule: { data: { schedules: [] } } }; }
    else if (/\/npcs\/[^/]+\/schedule$/.test(pathname)) body = { schedule: { data: { schedules: [] } } };
    else if (/\/npcs\/[^/]+\/decisions$/.test(pathname)) {
      decisionCount += 1;
      const requestBody = request.postDataJSON();
      decisions.push(requestBody);
      body = { state: "COMPLETED", decision: { data: { type: "OPTION", index: 0, text: requestBody.options[0].text } } };
    } else if (pathname.endsWith("/court/mandates")) {
      const input = request.postDataJSON();
      mandates.push(input);
      body = { state: "ISSUED", mandate: { id: `dongzhou:diplomacy-browser:${input.client_request_id}`, stageId: input.stage_id, stageTitle: "东郊索命", heroId: input.hero_id, taskType: input.task_type, evidence: { id: input.knowledge_id, name: "第一回史料", summary: "诸侯合纵可御强敌", source: { index: input.evidence_source_index, work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败与周宣王晚年", url: "https://ctext.org/shiji/zhou-ben-ji" } }, council: { requestId: input.council_request_id, index: input.decision_index, text: "先固军粮，再谋外援" }, assignment: { heroId: input.hero_id, npcId: "42", runtimeState: "READY", planId: input.schedule_plan_id, generationId: "generation-browser", eventId: input.schedule_event_id, transactionId: 9100106, name: "折冲诸侯", type: "外交", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 70, affectionCount: 1, relationshipCount: 2 } }, operation: input.operation, kernel: { module: "dongzhou_runtime", moduleVersion: "1.0.0", nexusKernelVersion: "0.2.0", state: "READY" }, digest: "c".repeat(64), state: "ISSUED" } };
    } else if (pathname.endsWith("/organization/tasks")) {
      orders.push(request.postDataJSON());
      body = { state: "ACCEPTED", taskId: "00000000-0000-0000-0000-000000000077" };
    } else if (pathname.endsWith("/organization/tasks/00000000-0000-0000-0000-000000000077")) {
      body = { taskId: "00000000-0000-0000-0000-000000000077", result: { data: { task_id: "00000000-0000-0000-0000-000000000077", state: "SUCCEEDED", final_result: "SUCCESS", version: 3 } } };
    } else return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ error: { message: pathname } }) });
    return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
  try {
    await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults >> text=第一回史料");
    await page.click('[data-knowledge-id="dongzhou_stage_001"][data-source-index="0"]');
    await page.waitForSelector("#officeKnowledgeResults >> text=已取为据");
    await page.click("#officeDecisionForm button[type=submit]");
    await page.waitForSelector("#officeDecisionResult >> text=先固军粮");
    await page.selectOption("#officeDiplomacyTarget", "zheng");
    await page.fill("#officeDiplomacyProposal", "互通军情，共御强敌");
    await page.click("#officeLobbyButton");
    await page.waitForSelector("#officeDiplomacyResult >> text=须待 orgFlow 复命");
    assert.equal((await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.diplomacy.lobbying.length)), 0, "accepted order is not yet a successful negotiation");
    await page.click("#officeAdvanceButton");
    await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.diplomacy.lobbying.some((entry) => entry.outcome === "accepted"));
    assert.equal(cloud.organization.diplomacy.lobbying.at(-1).organizationTaskId, "00000000-0000-0000-0000-000000000077", "orgFlow result must be persisted before alliance signing");
    await page.click("#officeAllianceButton");
    await page.waitForSelector("#officeAllianceLedger >> text=生效");
    await page.click("#officeBetrayButton");
    await page.waitForSelector("#officeAllianceLedger >> text=背盟待战");
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization);
    assert.equal(state.schemaVersion, 11);
    assert.equal(state.selectedSources["01"].tier, "史实骨架");
    assert.equal(state.diplomacy.lobbying.length, 1);
    assert.equal(state.diplomacy.alliances[0].status, "broken");
    assert.equal(cloud.organization.diplomacy.alliances[0].status, "broken", "alliance mutation must be stored remotely");
    assert.equal(state.pendingSupport.filter((entry) => entry.id.startsWith("betrayal:")).length, 1);
    assert.equal(decisionCount, 1);
    assert.match(decisions[0].question, /选证：《史记·周本纪》｜史实骨架/);
    assert(npcSyncs.flatMap((entry) => entry.npcs).some((npc) => npc.hero_id === "DuBo"), "organization manager must be synchronized before task execution");
    assert(scheduleGenerations.includes("DuBo") && scheduleGenerations.includes("ZuoRu"), "manager and assignee schedules must be warmed before task execution");
    assert(scheduleGenerations.filter((id) => id === "DuBo").length >= 2 && scheduleGenerations.filter((id) => id === "ZuoRu").length >= 2, "manager and assignee schedules must be refreshed while tasks advance");
    assert.equal(mandates.length, 1);
    assert.equal(mandates[0].evidence_source_index, 0);
    assert.equal(mandates[0].schedule_event_id, "event-diplomacy");
    assert.deepEqual(mandates[0].operation, { kind: "diplomacy", target_id: "zheng", target_name: "郑国", proposal: "互通军情，共御强敌" });
    assert.equal(orders.length, 1);
    assert.equal(orders[0].task_type, "diplomacy");
    assert.equal(orders[0].parameters.mandate_id, cloud.organization.mandates[0].id);
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
    console.log(JSON.stringify({ result: "PASS", decisions: decisionCount, mandates: mandates.length, orders: orders.length, chain: ["史料", "军议", "内核外交军令", "orgFlow游说", "盟约", "背盟战役"], reloadPreserved: true, horizontalOverflow: overflow }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
