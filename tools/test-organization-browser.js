"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require(path.resolve(__dirname, "..", "output", "playwright-runtime", "node_modules", "playwright"));

const BASE_URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const OUT = path.resolve(__dirname, "..", "output", "organization-e2e");

async function openReady(page) {
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
  await page.waitForSelector("#campaignScreen:not([hidden])");
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    desktop.on("pageerror", (error) => errors.push(error.message));
    await openReady(desktop);
    await desktop.click("#campaignOfficeButton");
    await desktop.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await desktop.waitForTimeout(350);
    const desktopLayout = await desktop.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      const viewport = { width: innerWidth, height: innerHeight };
      return { drawer: { left: drawer.left, top: drawer.top, right: drawer.right, bottom: drawer.bottom }, viewport };
    });
    if (desktopLayout.drawer.left < 0 || desktopLayout.drawer.right > desktopLayout.viewport.width || desktopLayout.drawer.top < 0 || desktopLayout.drawer.bottom > desktopLayout.viewport.height + 1) throw new Error(`Desktop organization drawer overflows viewport: ${JSON.stringify(desktopLayout)}`);
    await desktop.fill("#officeKnowledgeQuery", "东郊索命 杜伯");
    await desktop.click("#officeKnowledgeForm button[type=submit]");
    await desktop.waitForSelector("#officeKnowledgeResults article", { timeout: 10000 });
    await desktop.click("#officeIssueButton");
    await desktop.waitForSelector("#officeTaskLedger li.active");
    await desktop.screenshot({ path: path.join(OUT, "desktop-office.png"), fullPage: false });

    await desktop.evaluate(() => {
      const key = "dongzhou-h5-profile-v2";
      const profile = JSON.parse(localStorage.getItem(key));
      profile.organization.pendingSupport.push({ id: "e2e-support", stageId: "01", source: "验收筹备", provisions: 18, morale: 7, attack: 0.08, defense: 0.1, recon: 1 });
      localStorage.setItem(key, JSON.stringify(profile));
    });
    await desktop.reload({ waitUntil: "domcontentloaded" });
    await desktop.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await desktop.waitForSelector("#campaignScreen:not([hidden])");
    await desktop.click("#focusStageButton");
    await desktop.waitForSelector("#storyModal:not([hidden])", { timeout: 15000 });
    await desktop.click("#storySkipButton");
    await desktop.waitForSelector("#storyModal", { state: "hidden", timeout: 15000 });
    await desktop.waitForSelector("#battleCanvas:visible", { timeout: 15000 });
    const battleLog = await desktop.locator("#battleLog").innerText();
    if (!battleLog.includes("验收筹备")) throw new Error("Organization support did not reach battle log");

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    mobile.on("pageerror", (error) => errors.push(error.message));
    await openReady(mobile);
    await mobile.click("#campaignOfficeButton");
    await mobile.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await mobile.waitForTimeout(350);
    const mobileLayout = await mobile.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      return { left: drawer.left, right: drawer.right, top: drawer.top, width: innerWidth, scrollWidth: document.documentElement.scrollWidth };
    });
    if (mobileLayout.left < 0 || mobileLayout.right > mobileLayout.width + 1 || mobileLayout.scrollWidth > mobileLayout.width + 1) throw new Error("Mobile organization drawer overflows viewport");
    await mobile.screenshot({ path: path.join(OUT, "mobile-office.png"), fullPage: false });
    if (errors.length) throw new Error(`Page errors: ${errors.join(" | ")}`);
    console.log(JSON.stringify({ result: "PASS", desktopLayout, mobileLayout, screenshots: OUT }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
