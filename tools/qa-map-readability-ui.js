"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "tmp", "playwright", "node_modules", "playwright-core"));

const ROOT = path.resolve(__dirname, "..");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = process.argv[2] || "http://127.0.0.1:8765/index.html";
const campaign = JSON.parse(fs.readFileSync(path.join(ROOT, "web-game", "scenario", "campaign.json"), "utf8"));
const completed = campaign.stages.slice(0, 48).map((stage) => stage.id);
const output = path.join(ROOT, "tmp", "map-density-qa");
fs.mkdirSync(output, { recursive: true });

async function openBattle(browser, mode, viewport, label) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  await page.addInitScript(({ completedStages, mapDetail }) => {
    localStorage.setItem("dongzhou-h5-profile-v2", JSON.stringify({
      completed: completedStages,
      settings: { battleDifficulty: "medium", mapDetail, telemetryEnabled: true, feedbackEnabled: true }
    }));
  }, { completedStages: completed, mapDetail: mode });
  await page.goto(`${URL}?map-qa=${mode}-${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 60_000 });
  const setting = await page.locator("#mapDetailSetting").evaluate((element) => ({
    value: element.value,
    visible: Boolean(element.offsetParent),
    box: element.getBoundingClientRect().toJSON()
  }));
  const focus = await page.locator("#focusStageButton").evaluate((element) => ({
    stage: element.dataset.stageId,
    text: element.textContent
  }));
  if (label === "mobile" && mode === "balanced") {
    await page.screenshot({ path: path.join(output, "browser-campaign-mobile.png"), fullPage: false });
  }
  await page.locator("#focusStageButton").click();
  await page.waitForSelector("#storyModal:not([hidden])", { timeout: 20_000 });
  await page.locator("#storySkipButton").click();
  await page.locator("#storyModal").waitFor({ state: "hidden" });
  await page.waitForFunction(() => document.querySelector("#battleCanvas")?.dataset.mapDetailScale, null, { timeout: 20_000 });
  await page.waitForTimeout(250);
  await page.locator("#battleCanvas").screenshot({ path: path.join(output, `browser-${mode}-${label}.png`) });
  const pixels = await page.evaluate(() => {
    const canvas = document.querySelector("#battleCanvas");
    const context = canvas.getContext("2d");
    const { data, width, height } = context.getImageData(0, 0, canvas.width, canvas.height);
    let variation = 0;
    let samples = 0;
    let nonTransparent = 0;
    const stride = 3;
    for (let y = 0; y < height - stride; y += stride) {
      for (let x = 0; x < width - stride; x += stride) {
        const index = (y * width + x) * 4;
        const right = (y * width + x + stride) * 4;
        const down = ((y + stride) * width + x) * 4;
        for (let channel = 0; channel < 3; channel++) {
          variation += Math.abs(data[index + channel] - data[right + channel]);
          variation += Math.abs(data[index + channel] - data[down + channel]);
        }
        nonTransparent += data[index + 3] > 0 ? 1 : 0;
        samples++;
      }
    }
    return {
      detail: canvas.dataset.mapDetail,
      scale: Number(canvas.dataset.mapDetailScale),
      size: [width, height],
      variation: variation / (samples * 6 * 255),
      opaqueRatio: nonTransparent / samples
    };
  });
  return { page, errors, setting, focus, pixels };
}

async function main() {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  try {
    const mobileViewport = { width: 390, height: 844 };
    const balanced = await openBattle(browser, "balanced", mobileViewport, "mobile");
    const original = await openBattle(browser, "original", mobileViewport, "mobile");
    const desktop = await openBattle(browser, "balanced", { width: 1440, height: 1000 }, "desktop");
    const ratio = balanced.pixels.variation / original.pixels.variation;
    const result = balanced.errors.length === 0
      && original.errors.length === 0
      && balanced.setting.visible
      && balanced.setting.value === "balanced"
      && balanced.focus.stage === "27b"
      && balanced.pixels.detail === "balanced"
      && balanced.pixels.scale === 0.58
      && original.pixels.detail === "original"
      && original.pixels.scale === 1
      && desktop.pixels.detail === "balanced"
      && desktop.pixels.scale === 0.62
      && balanced.pixels.opaqueRatio === 1
      && original.pixels.opaqueRatio === 1
      && ratio < 0.92 ? "PASS" : "FAIL";
    console.log(JSON.stringify({
      result,
      stage: balanced.focus.stage,
      variationRatio: ratio,
      balanced: { setting: balanced.setting, pixels: balanced.pixels },
      original: { setting: original.setting, pixels: original.pixels },
      desktop: { setting: desktop.setting, pixels: desktop.pixels },
      errors: [...balanced.errors, ...original.errors, ...desktop.errors]
    }, null, 2));
    if (result !== "PASS") process.exitCode = 1;
    await balanced.page.close();
    await original.page.close();
    await desktop.page.close();
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
