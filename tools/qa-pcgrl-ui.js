"use strict";

const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "tmp", "playwright", "node_modules", "playwright-core"));

const ROOT = path.resolve(__dirname, "..");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = process.argv[2] || "http://127.0.0.1:8765/index.html";

async function openPage(browser, viewport) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  await page.addInitScript(() => {
    const tiles = Array.from({ length: 19 * 14 }, (_, index) => index % 7 === 0 ? 2 : index % 5 === 0 ? 3 : index % 2);
    window.DongzhouPcgrl = {
      isReady: () => true,
      generate: (_difficulty, seed) => JSON.stringify({
        ready: true,
        tiles,
        inference_ms: 2.5,
        model_version: "qa-policy",
        model_sha256: "qa",
        seed
      })
    };
  });
  await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 60_000 });
  return { page, errors };
}

async function main() {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  try {
    const desktop = await openPage(browser, { width: 1440, height: 1000 });
    await desktop.page.locator("#exerciseMenuButton").click();
    const desktopButton = await desktop.page.locator("#proceduralButton").boundingBox();
    await desktop.page.screenshot({ path: path.join(ROOT, "web-game", "qa-pcgrl-campaign-desktop.png"), fullPage: false });
    await desktop.page.locator("#proceduralButton").click();
    await desktop.page.waitForSelector("#storyModal:not([hidden])", { timeout: 20_000 });
    await desktop.page.locator("#storySkipButton").click();
    await desktop.page.locator("#storyModal").waitFor({ state: "hidden" });
    await desktop.page.screenshot({ path: path.join(ROOT, "web-game", "qa-pcgrl-battle-desktop.png"), fullPage: false });
    const battle = await desktop.page.evaluate(() => {
      const canvas = document.querySelector("#battleCanvas");
      const data = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
      const colors = new Set();
      for (let index = 0; index < data.length; index += Math.max(4, Math.floor(data.length / 8000 / 4) * 4)) {
        colors.add(`${data[index]},${data[index + 1]},${data[index + 2]},${data[index + 3]}`);
      }
      return {
        canvas: [canvas.width, canvas.height],
        sampledColors: colors.size,
        stage: document.querySelector("#stageHeading").textContent,
        status: document.querySelector("#statusText").textContent
      };
    });
    await desktop.page.locator(".roster-card:not(:disabled)").first().click();
    const skill = await desktop.page.evaluate(() => ({
      name: document.querySelector("#skillName").textContent,
      cost: document.querySelector("#skillCost").textContent,
      disabled: document.querySelector("#skillButton").disabled
    }));
    await desktop.page.locator("#skillButton").click();
    await desktop.page.evaluate(() => {
      const canvas = document.querySelector("#battleCanvas");
      const box = canvas.getBoundingClientRect();
      canvas.dispatchEvent(new MouseEvent("click", {
        bubbles: true,
        clientX: box.left + (2.5 / 19) * box.width,
        clientY: box.top + (6.5 / 14) * box.height
      }));
    });
    await desktop.page.waitForTimeout(100);
    const skillCast = await desktop.page.evaluate(() => ({
      log: document.querySelector("#battleLog").textContent,
      selectedUnit: document.querySelector("#unitDetail").textContent
    }));
    await desktop.page.locator("#battleCanvas").focus();
    await desktop.page.keyboard.press("ArrowRight");
    const keyboardAnnouncement = await desktop.page.locator("#boardAnnouncement").textContent();

    const mobile = await openPage(browser, { width: 390, height: 844 });
    await mobile.page.locator("#exerciseMenuButton").click();
    const mobileButton = await mobile.page.locator("#proceduralButton").boundingBox();
    await mobile.page.screenshot({ path: path.join(ROOT, "web-game", "qa-pcgrl-campaign-mobile.png"), fullPage: false });
    await mobile.page.locator(".campaign-focus").screenshot({ path: path.join(ROOT, "web-game", "qa-pcgrl-focus-mobile.png") });
    const mobileLayout = await mobile.page.evaluate(() => ({
      viewport: [innerWidth, innerHeight],
      bodyWidth: document.body.scrollWidth,
      visibleButton: Boolean(document.querySelector("#proceduralButton").offsetParent),
      focus: document.querySelector(".campaign-focus").getBoundingClientRect().toJSON(),
      copy: document.querySelector(".focus-copy").getBoundingClientRect().toJSON(),
      archive: document.querySelector(".campaign-archive-heading").getBoundingClientRect().toJSON()
    }));
    const campaignContracts = await mobile.page.evaluate(() => ({
      rank: document.querySelector("#armyRankLabel").textContent,
      autoDifficulty: document.querySelector("#proceduralDifficulty").value,
      lockedStages: document.querySelectorAll(".stage-card.locked").length,
      unlockedStages: document.querySelectorAll(".stage-card:not(.locked)").length,
      coins: document.querySelector("#coinCount").textContent,
      equipment: document.querySelectorAll(".equipment-item").length,
      feedback: document.querySelector("#feedbackToggle").checked
    }));
    await mobile.page.locator("#focusStageButton").click();
    await mobile.page.waitForSelector("#storyModal:not([hidden])", { timeout: 20_000 });
    await mobile.page.locator("#storySkipButton").click();
    await mobile.page.locator("#storyModal").waitFor({ state: "hidden" });
    const tutorialStart = await mobile.page.locator("#floatingNotice").textContent();
    await mobile.page.locator(".roster-card:not(:disabled)").first().click();
    const tutorialSelect = await mobile.page.locator("#floatingNotice").textContent();

    const result = {
      result: desktop.errors.length || mobile.errors.length || !desktopButton || !mobileButton || battle.sampledColors < 8 || skill.disabled || skill.name === "战技" || !skillCast.log.includes(skill.name) || !keyboardAnnouncement || !tutorialStart.includes("演武一") || !tutorialSelect.includes("演武二") || mobileLayout.bodyWidth > mobileLayout.viewport[0] + 1 || mobileLayout.archive.top < mobileLayout.copy.bottom || campaignContracts.autoDifficulty !== "auto" || campaignContracts.lockedStages < 1 || campaignContracts.equipment !== 7 || campaignContracts.coins !== "240" || !campaignContracts.feedback ? "FAIL" : "PASS",
      desktopButton,
      mobileButton,
      mobileLayout,
      battle,
      skill,
      skillCast,
      keyboardAnnouncement,
      campaignContracts,
      tutorial: { start: tutorialStart, afterSelect: tutorialSelect },
      errors: [...desktop.errors, ...mobile.errors]
    };
    console.log(JSON.stringify(result, null, 2));
    if (result.result !== "PASS") process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
