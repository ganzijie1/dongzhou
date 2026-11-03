"use strict";

const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "tmp", "playwright", "node_modules", "playwright-core"));

const ROOT = path.resolve(__dirname, "..");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = process.argv[2] || "http://127.0.0.1:8765/index.html?v=20261103-12";

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
    await desktop.page.waitForFunction(() => performance.getEntriesByType("resource").some((entry) => entry.name.includes("unit-infantry-blue.svg")), null, { timeout: 10_000 });
    const spriteResources = await desktop.page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name).filter((name) => /unit-(infantry|chariot)/.test(name)));
    const dispatchCellClick = (x, y) => desktop.page.evaluate(([cellX, cellY]) => {
      const canvas = document.querySelector("#battleCanvas");
      const rect = canvas.getBoundingClientRect();
      canvas.dispatchEvent(new MouseEvent("click", {
        bubbles: true,
        clientX: rect.left + (cellX + .5) / 19 * rect.width,
        clientY: rect.top + (cellY + .5) / 14 * rect.height
      }));
    }, [x, y]);
    const movementDigest = () => desktop.page.evaluate(() => {
      const canvas = document.querySelector("#battleCanvas");
      const context = canvas.getContext("2d");
      const pixels = context.getImageData(2 * 64, 5 * 64, 3 * 64, 3 * 64).data;
      let hash = 2166136261;
      for (let index = 0; index < pixels.length; index += 4) hash = Math.imul(hash ^ pixels[index] ^ (pixels[index + 1] << 8) ^ (pixels[index + 2] << 16), 16777619) >>> 0;
      return hash;
    });
    await dispatchCellClick(2, 6);
    await dispatchCellClick(3, 6);
    await desktop.page.waitForTimeout(40);
    const moveFrameA = await movementDigest();
    await desktop.page.waitForTimeout(100);
    const moveFrameB = await movementDigest();
    await desktop.page.waitForTimeout(260);
    const moveFrameC = await movementDigest();
    const savedMove = await desktop.page.evaluate(() => {
      const saved = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "{}");
      const unit = (saved.units || []).find((entry) => entry.heroId === "DuBo");
      return unit ? [unit.x, unit.y] : null;
    });
    const battle = await desktop.page.evaluate(() => ({
      objective: document.querySelector("#objectiveText").textContent,
      roster: [...document.querySelectorAll(".roster-name")].map((node) => node.textContent),
      log: document.querySelector("#battleLog").textContent,
      turn: document.querySelector("#turnLabel").textContent
    }));
    const attackSetup = await desktop.page.evaluate(() => {
      const saved = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "{}");
      const actor = (saved.units || []).find((entry) => entry.heroId === "DuBo");
      const target = (saved.units || []).find((entry) => entry.heroId === "RoyalGuard" && entry.x === 12 && entry.y === 1);
      actor.x = 11; actor.y = 1; actor.acted = false; actor.moved = false;
      saved.phase = "player"; saved.result = null;
      localStorage.setItem("dongzhou-h5-battle-v2", JSON.stringify(saved));
      return { targetHp: target.hp };
    });
    await desktop.page.reload({ waitUntil: "networkidle", timeout: 60_000 });
    await desktop.page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 60_000 });
    await desktop.page.locator("#resumeButton").click();
    await desktop.page.waitForFunction(() => document.querySelector("#campaignScreen").hidden && /^第 /.test(document.querySelector("#turnLabel").textContent), null, { timeout: 60_000 });
    const combatDigest = () => desktop.page.evaluate(() => {
      const context = document.querySelector("#battleCanvas").getContext("2d");
      const pixels = context.getImageData(10 * 64, 0, 4 * 64, 4 * 64).data;
      let hash = 2166136261;
      for (let index = 0; index < pixels.length; index += 4) hash = Math.imul(hash ^ pixels[index] ^ (pixels[index + 1] << 8) ^ (pixels[index + 2] << 16), 16777619) >>> 0;
      return hash;
    });
    await dispatchCellClick(11, 1);
    await dispatchCellClick(12, 1);
    await desktop.page.waitForTimeout(40);
    const attackFrameA = await combatDigest();
    await desktop.page.waitForTimeout(110);
    const attackFrameB = await combatDigest();
    await desktop.page.waitForTimeout(160);
    const attackFrameC = await combatDigest();
    await desktop.page.waitForFunction(() => {
      const saved = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "{}");
      return Number(saved.eventCounts?.attack || 0) >= 1;
    }, null, { timeout: 10_000 });
    const attackResult = await desktop.page.evaluate(() => {
      const saved = JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2") || "{}");
      const target = (saved.units || []).find((entry) => entry.heroId === "RoyalGuard" && entry.x === 12 && entry.y === 1);
      return { targetHp: target?.hp, attacks: saved.eventCounts?.attack || 0 };
    });
    await desktop.page.screenshot({ path: path.join(ROOT, "web-game", "qa-unit-actions-desktop.png"), fullPage: false });

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
    if (!spriteResources.some((name) => name.includes("unit-infantry-blue.svg")) || spriteResources.some((name) => name.includes("unit-chariot.png"))) problems.push("infantry sprite mapping invalid");
    if (new Set([moveFrameA, moveFrameB, moveFrameC]).size < 2 || moveFrameA === moveFrameC || String(savedMove) !== "3,6") problems.push("movement animation or final position invalid");
    if (new Set([attackFrameA, attackFrameB, attackFrameC]).size < 2 || attackFrameA === attackFrameC || !(attackResult.targetHp < attackSetup.targetHp) || attackResult.attacks < 1) problems.push("attack animation or damage persistence invalid");
    if (mobileLayout.bodyWidth > mobileLayout.viewport + 1 || mobileLayout.council.left < 0 || mobileLayout.council.right > mobileLayout.viewport + 1) problems.push("mobile council overflow");
    if (!mobileLayout.dailyVisible) problems.push("mobile daily challenge hidden");
    const realFailures = [...desktop.failed, ...mobile.failed].filter((item) => !item.includes("net::ERR_ABORTED"));
    problems.push(...desktop.errors, ...mobile.errors, ...realFailures);
    console.log(JSON.stringify({ result: problems.length ? "FAIL" : "PASS", councilBefore, formationAfter, spriteResources, moveFrames: [moveFrameA, moveFrameB, moveFrameC], savedMove, attackFrames: [attackFrameA, attackFrameB, attackFrameC], attackSetup, attackResult, battle, mobileLayout, problems }, null, 2));
    if (problems.length) process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
