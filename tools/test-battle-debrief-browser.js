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

const BASE_URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const WEB = path.resolve(__dirname, "..", "web-game");
const OUT = path.resolve(__dirname, "..", "output", "integration-validation");
const ORIGIN = new URL(BASE_URL).origin;
const CHROME = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft Edge\\Application\\msedge.exe",
].find((candidate) => candidate && fs.existsSync(candidate));

async function routeAssets(page) {
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== ORIGIN || url.pathname.startsWith("/api/")) return route.fallback();
    const file = path.resolve(WEB, `.${decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname)}`);
    if (!file.startsWith(`${WEB}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      return route.fulfill({ status: 404, body: "not found" });
    }
    const types = { ".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".json": "application/json", ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav" };
    return route.fulfill({ status: 200, contentType: types[path.extname(file)] || "application/octet-stream", body: fs.readFileSync(file) });
  });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(CHROME ? { executablePath: CHROME } : {}) });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  let version = 1;
  let stored = {};
  let debriefReads = 0;
  await routeAssets(page);
  await page.route("**/api/dongzhou/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;
    let body = {};
    if (pathname.endsWith("/sessions/guest")) body = { playerId: "battle-debrief-player", expiresIn: 86400 };
    else if (pathname.endsWith("/save") && request.method() === "GET") body = { version, payload: stored };
    else if (pathname.endsWith("/save") && request.method() === "PUT") {
      stored = request.postDataJSON().payload;
      body = { version: ++version, payload: stored };
    } else if (pathname.endsWith("/integration/status")) body = { mode: "connected", services: { nexusKernel: { online: true, requiredModuleCount: 20, operationalModuleCount: 20, unavailableModules: [] }, orgFlow: { online: true }, aiNpc: { online: true }, knowledge: { online: true } } };
    else if (/\/battle-reports\/[^/]+\/debrief$/.test(pathname)) {
      debriefReads += 1;
      body = {
        state: "SEALED",
        reportId: decodeURIComponent(pathname.split("/").at(-2)),
        reportDigest: "1".repeat(64),
        battleReceiptDigest: "2".repeat(64),
        stageId: "01",
        stageTitle: "东郊索命",
        outcome: { won: true, turns: 7, ownLosses: 1, terminalReason: "victory" },
        knowledge: [{ id: "dongzhou_stage_001", title: "第一回史料", summary: "宣王失政，诸侯观望。", sources: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败" }], digest: "3".repeat(64) }],
        participants: [{ heroId: "ZuoRu", npcId: "42", memory: { content: "左儒记得东郊索命告捷，所据 dongzhou_stage_001 已经核验。", digest: "4".repeat(64) } }],
        organizationTasks: [{ timeline: [{ sequence: 1 }, { sequence: 2 }, { sequence: 3 }], digest: "5".repeat(64), kernel: { module: "dongzhou_organization_task_trace", state: "SEALED" } }],
        digest: "6".repeat(64),
        kernel: { module: "dongzhou_battle_debrief", moduleVersion: "1.0.0", state: "SEALED" },
      };
    } else if (pathname.endsWith("/organization/roster")) body = { organization: { name: "东周军府", state: "ACTIVE", templateId: "dongzhou_court", templateVersion: 7, hierarchyVersion: 7, growthContribution: 0 }, members: [{ heroId: "DuBo", office: "军府主官", contributionBalance: 0, lifetimeEarned: 0, lifetimeSpent: 0 }, { heroId: "ZuoRu", office: "军府属官", contributionBalance: 0, lifetimeEarned: 0, lifetimeSpent: 0 }], playerMembership: null, openPositions: [] };
    else if (pathname.endsWith("/organization/inventory")) body = { accounts: [], revision: 1 };
    else if (pathname.endsWith("/organization/scheduled-duties")) body = { state: "ACTIVE", version: 1 };
    else if (pathname.endsWith("/organization/public-notices")) body = { notices: [] };
    else if (pathname.endsWith("/npcs/sync")) body = { ready: true, npcs: [] };
    else if (/\/npcs\/[^/]+\/state$/.test(pathname)) body = { memories: { available: true, items: [] }, runtime: { state: "READY" } };
    else if (/\/npcs\/[^/]+\/schedule$/.test(pathname)) body = { plan: null, overview: { available: false } };
    else if (/\/npcs\/[^/]+\/assignments\//.test(pathname)) body = { assignment: null };
    return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });

  try {
    await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    assert(stored.organization, "Default profile was not persisted");
    stored.organization.battleReports.push({
      id: "battle:01:debrief",
      stageId: "01",
      stageTitle: "东郊索命",
      won: true,
      turns: 7,
      ownLosses: 1,
      terminalReason: "victory",
      month: 1,
      support: {},
      councils: [],
      mandates: [],
      sources: [],
      kernelReceipt: {
        digest: "2".repeat(64),
        verifiedParticipants: ["ZuoRu"],
        verifiedSupport: { councils: [], mandates: [], orders: [{ id: "00000000-0000-4000-8000-000000000081", heroId: "ZuoRu" }], effect: {} },
        rejectedSupport: [],
        kernel: { module: "dongzhou_mandate_workflow", state: "SEALED" },
      },
    });
    stored.organization.archives.push({ id: "battle:01:debrief", type: "battle", stageId: "01", title: "东郊索命告捷", text: "用时7回合，折损1部" });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await page.waitForSelector("#officeBattleDebriefButton:not(:disabled)", { timeout: 15000 });
    await page.click("#officeBattleDebriefButton");
    await page.waitForSelector("#officeBattleDebrief:not([hidden]) >> text=东郊索命", { timeout: 15000 });
    const text = await page.locator("#officeBattleDebrief").innerText();
    assert.match(text, /史证复核/);
    assert.match(text, /参战者回忆/);
    assert.match(text, /左儒/);
    assert.match(text, /1 卷 \/ 3 步/);
    assert.match(text, /《史记·周本纪》/);
    assert(!text.includes("dongzhou_stage_001"), "Internal knowledge key leaked into debrief UI");
    assert(!text.includes("00000000-0000-4000-8000-000000000081"), "Internal task ID leaked into debrief UI");
    assert.equal(debriefReads, 1);
    await page.locator("#officeBattleDebrief").scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(OUT, "battle-debrief-desktop.png"), fullPage: false });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator("#officeBattleDebrief").scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    assert(layout.scrollWidth <= layout.width + 1, `Mobile debrief overflows viewport: ${JSON.stringify(layout)}`);
    await page.screenshot({ path: path.join(OUT, "battle-debrief-mobile.png"), fullPage: false });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", debriefReads, layout }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
