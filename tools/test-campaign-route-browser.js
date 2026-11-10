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

const WEB = path.resolve(__dirname, "..", "web-game");
const ORIGIN = "http://127.0.0.1:8780";
const SYSTEM_CHROMIUM = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft Edge\\Application\\msedge.exe"
].find((candidate) => candidate && fs.existsSync(candidate));

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(SYSTEM_CHROMIUM ? { executablePath: SYSTEM_CHROMIUM } : {})
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  let routeRequests = 0;
  let saveVersion = 1;
  const profile = { completed: ["01"], campaignResources: { provisions: 100, morale: 70 } };
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname.startsWith("/api/dongzhou/v1/")) {
      let body = {};
      if (url.pathname.endsWith("/sessions/guest")) body = { playerId: "route-player", expiresIn: 86400 };
      else if (url.pathname.endsWith("/save") && request.method() === "GET") body = { version: saveVersion, payload: profile };
      else if (url.pathname.endsWith("/save")) body = { version: ++saveVersion, payload: request.postDataJSON().payload };
      else if (url.pathname.endsWith("/integration/status")) body = { mode: "connected", services: { knowledge: { online: true }, aiNpc: { online: true }, orgFlow: { online: true }, nexusKernel: { online: true } } };
      else if (url.pathname.endsWith("/knowledge/routes")) {
        routeRequests += 1;
        assert.deepStrictEqual(request.postDataJSON(), {
          from_stage_id: "01",
          from_stage_index: 1,
          to_stage_id: "02",
          to_stage_index: 2
        });
        body = {
          mode: "connected",
          found: true,
          fromStageId: "01",
          toStageId: "02",
          fromMapId: 900001,
          toMapId: 900002,
          routeId: "campaign_progression_900001_900002",
          provisionCost: 2
        };
      } else body = {};
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    }
    if (url.origin !== ORIGIN) return route.fallback();
    const relative = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
    const file = path.resolve(WEB, `.${relative}`);
    if (!file.startsWith(`${WEB}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      return route.fulfill({ status: 404, body: "not found" });
    }
    const types = { ".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".json": "application/json", ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav" };
    return route.fulfill({ status: 200, contentType: types[path.extname(file)] || "application/octet-stream", body: fs.readFileSync(file) });
  });

  try {
    await page.goto(`${ORIGIN}/`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await page.waitForFunction(() => document.querySelector("#focusRouteProof")?.textContent.includes("行军 2 军粮"));
    assert.strictEqual(await page.locator("#focusStageButton").getAttribute("data-stage-id"), "02");
    await page.click("#focusStageButton");
    await page.waitForFunction(() => {
      const battle = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "null");
      return battle?.campaignRoute?.routeId === "campaign_progression_900001_900002";
    }, null, { timeout: 20000 });
    const stored = await page.evaluate(() => ({
      battle: JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2")),
      profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"))
    }));
    assert.strictEqual(stored.battle.campaignRoute.provisionCost, 2);
    assert.strictEqual(stored.profile.campaignResources.provisions, 98);
    assert.strictEqual(routeRequests, 1, "campaign route should be reused between focus and deployment");
    assert.deepStrictEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", routeRequests, provisionCost: 2, provisions: 98 }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
