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

const webRoot = path.resolve(__dirname, "../web-game");
const baseUrl = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const baseOrigin = new URL(baseUrl).origin;
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => fs.existsSync(entry));

const guideReceipt = (actionId, state, digest) => ({
  actionId,
  questionId: "00000000-0000-4000-8000-000000000101",
  taskId: "00000000-0000-4000-8000-000000000101",
  playerId: "00000000-0000-4000-8000-000000000102",
  chatId: "dongzhou-adviser-browser",
  guideSessionId: "guide-browser-session",
  decision: "ACCEPT",
  state,
  eventType: state === "CANCELLED" ? "guide_cancelled" : state === "RUNNING" ? "guide_started" : "guide_decision",
  guideStarted: state === "RUNNING",
  message: "",
  reason: state === "CANCELLED" ? "player_cancelled" : "",
  digest,
  kernel: {
    module: "dongzhou_adviser_guide",
    moduleVersion: "1.0.0",
    nexusKernelVersion: "0.2.0",
    state: "SEALED",
  },
});

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1100, height: 850 } });
  const model = {
    cloud: {}, version: 0, questionId: "", actionId: "", decisions: [], reads: 0,
    cancellations: [], errors: [], unexpected: [], guideAvailable: true, routeRequests: 0,
  };
  await context.route("**/*", async (route) => {
    const request = route.request();
    const parsed = new URL(request.url());
    const pathname = parsed.pathname;
    if (parsed.origin !== baseOrigin) {
      model.unexpected.push(request.url());
      return route.abort();
    }
    if (!pathname.startsWith("/api/")) {
      const file = path.resolve(webRoot, `.${decodeURIComponent(pathname === "/" ? "/index.html" : pathname)}`);
      if (!file.startsWith(`${webRoot}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
        return route.fulfill({ status: 404, body: "not found" });
      }
      const mime = {
        ".html": "text/html", ".js": "application/javascript", ".css": "text/css",
        ".json": "application/json", ".webp": "image/webp", ".png": "image/png",
        ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
        ".wav": "audio/wav", ".lua": "text/plain",
      };
      return route.fulfill({ status: 200, contentType: mime[path.extname(file)] || "application/octet-stream", body: fs.readFileSync(file) });
    }

    let body = {};
    if (pathname.endsWith("/sessions/guest")) body = { playerId: "00000000-0000-4000-8000-000000000102", expiresIn: 86400 };
    else if (pathname.endsWith("/save")) {
      if (request.method() === "PUT") {
        const input = request.postDataJSON();
        model.cloud = JSON.parse(JSON.stringify(input.payload));
        model.version += 1;
      }
      body = { version: model.version, payload: model.cloud };
    } else if (pathname.endsWith("/integration/status")) body = { mode: "connected", organizationId: "test", services: { nexusKernel: { online: true }, orgFlow: { online: true }, aiNpc: { online: true }, knowledge: { online: true } } };
    else if (pathname.endsWith("/npcs/sync")) body = { ready: true, npcs: [] };
    else if (pathname.endsWith("/npcs/interaction-preference")) body = { enabled: true, source: "test" };
    else if (pathname.endsWith("/organization/roster")) body = { organization: { id: "test", name: "东周军府", state: "ACTIVE", growthContribution: 0 }, members: [] };
    else if (pathname.endsWith("/organization/inventory")) body = { organizationId: "test", gameServerId: "91001", revision: 1, accounts: [] };
    else if (pathname.endsWith("/organization/scheduled-duties")) body = { state: "ACTIVE", rules: [], triggers: [], tasks: [] };
    else if (pathname.endsWith("/organization/public-notices")) body = { notices: [] };
    else if (pathname.includes("/organization/members/") && pathname.endsWith("/contributions")) body = { heroId: "ZuoRu", memberId: "member", account: { accountVersion: 1, accountBalance: 0, lifetimeEarned: 0, lifetimeSpent: 0 }, entries: [], nextBeforeVersion: null };
    else if (pathname.endsWith("/knowledge/codex")) body = { results: [] };
    else if (pathname.endsWith("/knowledge/routes")) {
      model.routeRequests += 1;
      body = {
        mode: "connected", found: true, routeId: "campaign_progression_900001_900002",
        provisionCost: 2, moraleDelta: 0, label: "奉诏直进",
        options: [
          { method: "campaign_progression", routeId: "campaign_progression_900001_900002", label: "奉诏直进", provisionCost: 2, moraleDelta: 0 },
          { method: "fixed_point", routeId: "fixed_point_900001_900002", label: "经官道驿行", provisionCost: 4, moraleDelta: 1 },
          { method: "npc_dialog", routeId: "npc_dialog_900001_900002", label: "请乡民引路", provisionCost: 3, moraleDelta: 2, guideName: "东郊乡民" },
        ],
        knowledgeWitnesses: {
          from: { knowledgeIds: ["stage-01"], digest: "4".repeat(64) },
          to: { knowledgeIds: ["stage-02"], digest: "5".repeat(64) },
        },
        receipt: { digest: "6".repeat(64), attestation: "7".repeat(64), kernel: { state: "SEALED" } },
      };
    }
    else if (pathname.includes("/assignments/")) body = { assignment: { heroId: "ZuoRu", npcId: "42", runtimeState: "READY", planId: "plan-browser", generationId: "generation-browser", eventId: "event-supply", transactionId: 9100103, name: "转运军粮", type: "军务", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "calm", intensity: 0, affectionCount: 0, relationshipCount: 0 } } };
    else if (pathname.endsWith("/schedule")) body = { schedule: { data: { schedules: [] } } };
    else if (pathname.endsWith("/state")) body = { knownNpcIds: {}, emotion: { data: {} }, affection: { data: { items: [], total: 0 } }, relationships: { data: { items: [], total: 0 } } };
    else if (pathname.endsWith("/correspondence")) body = { messages: [] };
    else if (pathname.endsWith("/adviser/questions") && request.method() === "POST") {
      const input = request.postDataJSON();
      model.questionId = input.client_request_id;
      body = { state: "PROCESSING", questionId: model.questionId, taskId: model.questionId };
    } else if (/\/adviser\/questions\/[^/]+\/guide$/.test(pathname)) {
      const input = request.postDataJSON();
      model.actionId = input.action_id;
      model.decisions.push(input);
      body = { state: "ACCEPTED", replayed: false, guide: guideReceipt(model.actionId, "ACCEPTED", "1".repeat(64)) };
    } else if (/\/adviser\/guides\/[^/]+\/cancel$/.test(pathname)) {
      model.cancellations.push(request.postDataJSON());
      body = { state: "CANCELLED", replayed: false, guide: guideReceipt(model.actionId, "CANCELLED", "2".repeat(64)) };
    } else if (/\/adviser\/guides\/[^/]+$/.test(pathname)) {
      model.reads += 1;
      body = { state: "RUNNING", guide: guideReceipt(model.actionId, "RUNNING", "3".repeat(64)) };
    } else if (/\/adviser\/questions\/[^/]+$/.test(pathname)) {
      body = {
        state: "ANSWERED", questionId: model.questionId, taskId: model.questionId,
        chatId: "dongzhou-adviser-browser", answer: "前方已有属官可为你引路。", intentType: "location",
        guide: model.guideAvailable
          ? { available: true, sessionId: "guide-browser-session", status: "AVAILABLE", started: false }
          : { available: false, sessionId: "", status: "UNAVAILABLE", started: false },
        guideIgnored: false,
      };
    } else {
      model.unexpected.push(`${request.method()} ${pathname}`);
      return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ error: { message: "unexpected mock route" } }) });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });

  const page = await context.newPage();
  page.on("pageerror", (error) => model.errors.push(error.message));
  try {
    await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.fill("#officeAdviserQuestion", "下一处军令在哪里？");
    await page.click("#officeAdviserAsk");
    await page.waitForSelector('[data-adviser-guide="ACCEPT"]:not([hidden])', { timeout: 10000 });
    assert.match(await page.locator("#officeAdviserAnswer").innerText(), /属官可为你引路/);
    assert.match(await page.locator("#officeAdviserGuideStatus").innerText(), /等待你的决定/);

    await page.click('[data-adviser-guide="ACCEPT"]');
    await page.waitForSelector("[data-adviser-guide-cancel]:not([hidden])", { timeout: 10000 });
    await page.waitForFunction(() => document.querySelector("#officeAdviserGuideStatus")?.textContent.includes("属官正在引路"), null, { timeout: 10000 });
    assert.equal(model.decisions.length, 1);
    assert.equal(model.decisions[0].decision, "ACCEPT");
    assert(model.reads >= 1);

    await page.click("[data-adviser-guide-cancel]");
    await page.waitForFunction(() => document.querySelector("#officeAdviserGuideStatus")?.textContent.includes("已停止本次引路"), null, { timeout: 10000 });
    assert.equal(model.cancellations.length, 1);
    assert.equal(model.cancellations[0].reason, "player_cancelled");
    const journal = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
    assert.equal(journal.guideDecision.result.state, "CANCELLED");
    assert.equal(journal.guideDecision.result.guide.kernel.module, "dongzhou_adviser_guide");

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => document.querySelector("#officeAdviserGuideStatus")?.textContent.includes("已停止本次引路"));
    await page.setViewportSize({ width: 320, height: 700 });
    const bounds = await page.locator(".office-adviser").evaluate((element) => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, width: innerWidth, scrollWidth: document.documentElement.scrollWidth };
    });
    assert(bounds.left >= 0 && bounds.right <= bounds.width + 1 && bounds.scrollWidth <= bounds.width + 1);

    model.guideAvailable = false;
    model.cloud.completed = ["01"];
    model.cloud.lastStage = "01";
    await page.evaluate(() => localStorage.removeItem("dongzhou-adviser-question-v1"));
    await page.setViewportSize({ width: 1100, height: 850 });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    assert.equal(await page.locator("#focusStageButton").getAttribute("data-stage-id"), "02");
    await page.click("#campaignOfficeButton");
    await page.fill("#officeAdviserQuestion", "下一处军令在哪里？");
    await page.click("#officeAdviserAsk");
    await page.waitForSelector("[data-adviser-route]:not([hidden]):not([disabled])", { timeout: 10000 });
    assert.match(await page.locator("#officeAdviserGuideStatus").innerText(), /史料核验/);
    await page.click("[data-adviser-route]");
    await page.waitForFunction(() => document.querySelector("#campaignOfficeBackdrop")?.hidden === true);
    await page.waitForSelector('#focusRouteOptions:not([hidden]) [data-route-method="npc_dialog"]', { timeout: 10000 });
    assert.equal(await page.locator("#focusRouteOptions [data-route-method]").count(), 3);
    assert(model.routeRequests >= 1);
    assert.deepEqual(model.errors, []);
    assert.deepEqual(model.unexpected, []);
    console.log(JSON.stringify({ result: "PASS", guideAccepted: true, guideRunning: true, guideCancelled: true, restoredAfterReload: true, mobile320NoOverflow: true, unavailableGuideRouteHandoff: true, routeOptions: 3 }));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
