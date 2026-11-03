"use strict";

const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "tmp", "playwright", "node_modules", "playwright-core"));

const ROOT = path.resolve(__dirname, "..");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = process.argv[2] || "http://127.0.0.1:8765/index.html?v=20261103-11";

async function openPage(browser, viewport) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  const failed = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("requestfailed", (request) => failed.push(`${request.url()} ${request.failure()?.errorText || "failed"}`));
  await page.goto(URL, { waitUntil: "networkidle", timeout: 60_000 });
  await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 60_000 });
  return { page, errors, failed };
}

async function main() {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  try {
    const desktop = await openPage(browser, { width: 1440, height: 1000 });
    const councilBefore = await desktop.page.evaluate(() => ({
      viewport: innerWidth,
      bodyWidth: document.body.scrollWidth,
      formationCount: document.querySelectorAll("[data-formation]").length,
      activeFormation: document.querySelector("[data-formation].active")?.dataset.formation,
      vanguardCount: document.querySelector("#vanguardSelect").options.length,
      resources: ["#provisionsCount", "#moraleCount", "#woundedCount"].map((selector) => document.querySelector(selector).textContent),
      replayVisible: Boolean(document.querySelector("#recentReplays").offsetParent)
    }));
    await desktop.page.locator('[data-formation="bulwark"]').click();
    const formationAfter = await desktop.page.locator("[data-formation].active").getAttribute("data-formation");
    await desktop.page.locator("#assistToggle").uncheck();
    await desktop.page.locator("#assistToggle").check();
    await desktop.page.locator(".war-council").screenshot({ path: path.join(ROOT, "web-game", "qa-war-council-desktop.png") });

    await desktop.page.locator("#focusStageButton").click();
    await desktop.page.waitForFunction(() => !document.querySelector("#storyModal").hidden || /^第 /.test(document.querySelector("#turnLabel").textContent), null, { timeout: 60_000 });
    if (await desktop.page.locator("#storyModal").isVisible()) await desktop.page.locator("#storySkipButton").click();
    await desktop.page.waitForFunction(() => document.querySelector("#storyModal").hidden && /^第 /.test(document.querySelector("#turnLabel").textContent), null, { timeout: 20_000 });
    await desktop.page.waitForTimeout(200);
    const battle = await desktop.page.evaluate(() => ({
      objective: document.querySelector("#objectiveText").textContent,
      roster: [...document.querySelectorAll(".roster-name")].map((node) => node.textContent),
      log: document.querySelector("#battleLog").textContent,
      turn: document.querySelector("#turnLabel").textContent
    }));

    const mobile = await openPage(browser, { width: 390, height: 844 });
    await mobile.page.locator(".war-council").scrollIntoViewIfNeeded();
    await mobile.page.locator(".war-council").screenshot({ path: path.join(ROOT, "web-game", "qa-war-council-mobile.png") });
    const mobileLayout = await mobile.page.evaluate(() => {
      const council = document.querySelector(".war-council").getBoundingClientRect();
      return {
        viewport: innerWidth,
        bodyWidth: document.body.scrollWidth,
        council: { left: council.left, right: council.right, width: council.width },
        formationColumns: getComputedStyle(document.querySelector(".formation-control")).gridTemplateColumns,
        dailyVisible: Boolean(document.querySelector("#dailyChallengeButton").offsetParent)
      };
    });

    const problems = [];
    if (councilBefore.bodyWidth > councilBefore.viewport + 1) problems.push("desktop horizontal overflow");
    if (councilBefore.formationCount !== 4 || formationAfter !== "bulwark") problems.push("formation controls invalid");
    if (!councilBefore.vanguardCount || !councilBefore.replayVisible) problems.push("vanguard or replay panel missing");
    if (!battle.objective.includes("%") || !battle.roster.some((text) => text.includes("先锋"))) problems.push("battle mission or vanguard metadata missing");
    if (battle.roster.length !== 2) problems.push(`stage roster duplicated: ${battle.roster.length}`);
    if (!battle.log.includes("军议：坚营固守") || !battle.turn.includes("回合")) problems.push("battle formation log or turn state missing");
    if ((battle.log.match(/军议：坚营固守/g) || []).length !== 1) problems.push("battle setup ran more than once");
    if (mobileLayout.bodyWidth > mobileLayout.viewport + 1 || mobileLayout.council.left < 0 || mobileLayout.council.right > mobileLayout.viewport + 1) problems.push("mobile council overflow");
    if (!mobileLayout.dailyVisible) problems.push("mobile daily challenge hidden");
    const realFailures = [...desktop.failed, ...mobile.failed].filter((item) => !item.includes("net::ERR_ABORTED"));
    problems.push(...desktop.errors, ...mobile.errors, ...realFailures);
    console.log(JSON.stringify({ result: problems.length ? "FAIL" : "PASS", councilBefore, formationAfter, battle, mobileLayout, problems }, null, 2));
    if (problems.length) process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
