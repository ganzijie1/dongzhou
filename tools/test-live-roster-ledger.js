"use strict";

const assert = require("assert/strict");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const output = path.resolve(__dirname, "../output/integration-validation/live-roster-ledger.png");
const mobileOutput = path.resolve(__dirname, "../output/integration-validation/live-roster-ledger-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((installation) => {
    localStorage.setItem("dongzhou-installation-id-v1", installation);
  }, crypto.randomUUID());
  const page = await context.newPage();
  const errors = [];
  const mutations = { tasks: 0, mandates: 0, monthAdvance: 0 };
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.method() !== "POST") return;
    const pathname = new URL(request.url()).pathname;
    if (pathname.endsWith("/organization/tasks")) mutations.tasks += 1;
    if (pathname.endsWith("/court/mandates")) mutations.mandates += 1;
    if (pathname.endsWith("/organization/month/advance")) mutations.monthAdvance += 1;
  });

  try {
    const rosterResponsePromise = page.waitForResponse((response) =>
      response.request().method() === "GET" && new URL(response.url()).pathname.endsWith("/organization/roster"),
    { timeout: 45000 });
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const rosterResponse = await rosterResponsePromise;
    assert.equal(rosterResponse.status(), 200, await rosterResponse.text());
    const roster = await rosterResponse.json();
    assert.equal(roster.organization.state, "ACTIVE");
    assert(Number.isSafeInteger(roster.organization.hierarchyVersion));
    assert(roster.members.length >= 2);

    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await page.waitForFunction((count) => document.querySelector("#officeRosterSummary")?.textContent.includes(`${count} 席在册`), roster.members.length);

    const zuoRu = roster.members.find((member) => member.heroId === "ZuoRu");
    assert(zuoRu, "Live orgFlow roster does not contain ZuoRu");
    assert.equal(zuoRu.directManagerHeroId, "DuBo");
    const row = page.locator('[data-roster-hero="ZuoRu"]');
    await row.waitFor();
    const rowText = await row.innerText();
    assert.match(rowText, /左儒/);
    assert.match(rowText, /属官/);
    assert.match(rowText, /官署实账/);
    assert.match(rowText, /上呈杜伯/);
    assert(rowText.includes(`可用贡献 ${zuoRu.contributionBalance}`));
    assert(rowText.includes(`累计 ${zuoRu.lifetimeEarned}`));
    assert(rowText.includes(`已用 ${zuoRu.lifetimeSpent}`));
    assert(!rowText.includes("officer_01"));
    assert(!rowText.includes("court_officer"));

    const summary = await page.locator("#officeRosterSummary").innerText();
    assert(summary.includes(`谱系 ${roster.organization.hierarchyVersion}`));
    assert.match(summary, /在署/);
    assert.deepEqual(mutations, { tasks: 0, mandates: 0, monthAdvance: 0 });
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator(".office-ledger").screenshot({ path: output });
    await page.setViewportSize({ width: 320, height: 760 });
    await row.scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      row: (() => {
        const box = document.querySelector('[data-roster-hero="ZuoRu"]').getBoundingClientRect();
        return { left: box.left, right: box.right, width: box.width };
      })(),
    }));
    assert(layout.scrollWidth <= layout.viewport, JSON.stringify(layout));
    assert(layout.row.left >= 0 && layout.row.right <= layout.viewport, JSON.stringify(layout));
    await row.screenshot({ path: mobileOutput });

    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-orgflow-browser-no-interception",
      organization: roster.organization.name,
      hierarchyVersion: roster.organization.hierarchyVersion,
      rosterSize: roster.members.length,
      member: {
        heroId: zuoRu.heroId,
        managerHeroId: zuoRu.directManagerHeroId,
        contributionBalance: zuoRu.contributionBalance,
        lifetimeEarned: zuoRu.lifetimeEarned,
        lifetimeSpent: zuoRu.lifetimeSpent,
      },
      noGameplayMutations: true,
      mobileNoOverflow: true,
      screenshot: output,
      mobileScreenshot: mobileOutput,
    }));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, message: error.message, stack: error.stack }));
  process.exitCode = 1;
});
