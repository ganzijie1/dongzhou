"use strict";

const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "tmp", "playwright", "node_modules", "playwright-core"));

const ROOT = path.resolve(__dirname, "..");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = process.argv[2] || "http://127.0.0.1:8765/index.html";

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
    await desktop.page.locator("#exerciseMenuButton").click();
    const mode = await desktop.page.locator("#proceduralMode").inputValue();
    const button = await desktop.page.locator("#proceduralButton").boundingBox();
    await desktop.page.screenshot({ path: path.join(ROOT, "web-game", "qa-map-elites-campaign-desktop.png"), fullPage: false });
    await desktop.page.locator("#proceduralButton").click();
    await desktop.page.waitForSelector("#storyModal:not([hidden])", { timeout: 20_000 });
    await desktop.page.locator("#storyNextButton").click();
    const voiced = await desktop.page.evaluate(() => ({
      speaker: document.querySelector("#storySpeaker").textContent,
      replayHidden: document.querySelector("#storyVoiceReplayButton").hidden,
      replayDisabled: document.querySelector("#storyVoiceReplayButton").disabled
    }));
    await desktop.page.locator("#storySkipButton").click();
    await desktop.page.locator("#storyModal").waitFor({ state: "hidden" });
    await desktop.page.waitForTimeout(250);
    await desktop.page.screenshot({ path: path.join(ROOT, "web-game", "qa-map-elites-battle-desktop.png"), fullPage: false });
    const battle = await desktop.page.evaluate(() => {
      const canvas = document.querySelector("#battleCanvas");
      const pixels = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
      const colors = new Set();
      const stride = Math.max(4, Math.floor(pixels.length / 10000 / 4) * 4);
      for (let index = 0; index < pixels.length; index += stride) colors.add(`${pixels[index]},${pixels[index + 1]},${pixels[index + 2]},${pixels[index + 3]}`);
      return {
        stage: document.querySelector("#stageHeading").textContent,
        status: document.querySelector("#statusText").textContent,
        log: document.querySelector("#battleLog").textContent,
        canvas: [canvas.width, canvas.height],
        colors: colors.size,
        roster: document.querySelectorAll(".roster-card").length
      };
    });

    const mobile = await openPage(browser, { width: 390, height: 844 });
    await mobile.page.locator("#exerciseMenuButton").click();
    await mobile.page.screenshot({ path: path.join(ROOT, "web-game", "qa-map-elites-campaign-mobile.png"), fullPage: false });
    const mobileLayout = await mobile.page.evaluate(() => ({
      viewport: [innerWidth, innerHeight],
      bodyWidth: document.body.scrollWidth,
      modeVisible: Boolean(document.querySelector("#proceduralMode").offsetParent),
      buttonVisible: Boolean(document.querySelector("#proceduralButton").offsetParent),
      mode: document.querySelector("#proceduralMode").value,
      buttonText: document.querySelector("#proceduralButton").textContent
    }));
    await mobile.page.locator("#proceduralButton").click();
    await mobile.page.waitForSelector("#storyModal:not([hidden])", { timeout: 20_000 });
    await mobile.page.locator("#storySkipButton").click();
    await mobile.page.locator("#storyModal").waitFor({ state: "hidden" });
    await mobile.page.waitForTimeout(200);
    await mobile.page.screenshot({ path: path.join(ROOT, "web-game", "qa-map-elites-battle-mobile.png"), fullPage: false });
    const mobileBattle = await mobile.page.evaluate(() => ({
      viewport: [innerWidth, innerHeight],
      bodyWidth: document.body.scrollWidth,
      stage: document.querySelector("#stageHeading").textContent,
      canvas: document.querySelector("#battleCanvas").getBoundingClientRect().toJSON()
    }));

    const problems = [];
    if (mode !== "map-elites") problems.push("default mode is not MAP-Elites");
    if (!button) problems.push("desktop experiment button missing");
    if (!/军报/.test(voiced.speaker) || voiced.replayHidden || voiced.replayDisabled) problems.push("new character/system line has no playable audio");
    if (!battle.stage.includes("垂沙") || !battle.status.includes("MAP-Elites") || !battle.log.includes("硬校验通过")) problems.push("desktop battle metadata missing");
    if (battle.colors < 8 || battle.roster !== 6) problems.push("desktop battle canvas or roster invalid");
    if (mobileLayout.bodyWidth > mobileLayout.viewport[0] + 1 || !mobileLayout.modeVisible || !mobileLayout.buttonVisible) problems.push("mobile campaign overflow or controls hidden");
    if (mobileLayout.mode !== "map-elites" || !mobileLayout.buttonText.includes("垂沙")) problems.push("mobile MAP-Elites selection invalid");
    if (mobileBattle.bodyWidth > mobileBattle.viewport[0] + 1 || !mobileBattle.stage.includes("垂沙")) problems.push("mobile battle overflow or wrong stage");
    const realRequestFailures = [...desktop.failed, ...mobile.failed].filter((item) => !item.includes("net::ERR_ABORTED"));
    problems.push(...desktop.errors, ...mobile.errors, ...realRequestFailures);
    const result = { result: problems.length ? "FAIL" : "PASS", mode, voiced, battle, mobileLayout, mobileBattle, problems };
    console.log(JSON.stringify(result, null, 2));
    if (problems.length) process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
