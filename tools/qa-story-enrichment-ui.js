"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/index.html";
const outputDir = path.resolve(process.argv[3] || "output/qa-story-enrichment");

async function launch() {
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
  ].filter(Boolean);
  return chromium.launch({ headless: true, executablePath: candidates.find(fs.existsSync) });
}

async function run() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle" });

  await page.locator('.stage-card[data-stage-id="01"]').click();
  await page.locator("#storyModal").waitFor({ state: "visible" });
  await page.locator("#storySkipButton").click();
  await page.locator("#endTurnButton").waitFor({ state: "visible" });
  await page.locator("#endTurnButton").click();
  await page.locator("#storyModal").waitFor({ state: "visible", timeout: 20000 });
  const battleBeat = {
    speaker: await page.locator("#storySpeaker").textContent(),
    text: await page.locator("#storyText").textContent()
  };
  await page.screenshot({ path: path.join(outputDir, "stage-01-battle-beat.png"), fullPage: true });
  if (battleBeat.speaker !== "尹吉甫" || !battleBeat.text.includes("三年前没有说完")) {
    throw new Error(`Stage 01 battle beat did not trigger: ${JSON.stringify(battleBeat)}`);
  }

  await page.evaluate(() => {
    localStorage.removeItem("dongzhou-h5-battle-v2");
    localStorage.setItem("dongzhou-h5-profile-v2", JSON.stringify({ completed: ["01"], lastStage: "02" }));
  });
  await page.reload({ waitUntil: "networkidle" });
  await page.locator('.stage-card[data-stage-id="02"]').click();
  await page.locator("#storyModal").waitFor({ state: "visible" });
  const chapter2Progress = await page.locator("#storyProgress").textContent();
  await page.locator("#storyNextButton").click();
  await page.waitForTimeout(400);
  const chapter2 = {
    speaker: await page.locator("#storySpeaker").textContent(),
    text: await page.locator("#storyText").textContent(),
    voiceVisible: await page.locator("#storyVoiceReplayButton").isVisible()
  };
  await page.screenshot({ path: path.join(outputDir, "stage-02-rewritten-cutscene.png"), fullPage: true });
  if (chapter2Progress !== "1 / 26") throw new Error(`Unexpected chapter 2 length: ${chapter2Progress}`);
  if (chapter2.speaker !== "岐山守臣" || !chapter2.voiceVisible) throw new Error(`Chapter 2 voice/content mismatch: ${JSON.stringify(chapter2)}`);

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await mobile.goto(baseUrl, { waitUntil: "networkidle" });
  await mobile.evaluate(() => {
    localStorage.removeItem("dongzhou-h5-battle-v2");
    localStorage.setItem("dongzhou-h5-profile-v2", JSON.stringify({ completed: ["01"], lastStage: "02" }));
  });
  await mobile.reload({ waitUntil: "networkidle" });
  await mobile.locator("#campaignScreen").waitFor({ state: "visible" });
  await mobile.locator('.stage-card[data-stage-id="02"]').click();
  await mobile.locator("#storyModal").waitFor({ state: "visible" });
  const storyBox = await mobile.locator(".story-dialog").boundingBox();
  if (!storyBox || storyBox.x < 0 || storyBox.x + storyBox.width > 390 || storyBox.y + storyBox.height > 844) {
    throw new Error(`Mobile story panel overflow: ${JSON.stringify(storyBox)}`);
  }
  await mobile.screenshot({ path: path.join(outputDir, "mobile-stage-02-cutscene.png"), fullPage: true });
  await browser.close();

  if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
  console.log(JSON.stringify({ result: "PASS", battleBeat, chapter2Progress, chapter2, mobileStoryBox: storyBox }, null, 2));
}

run().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
