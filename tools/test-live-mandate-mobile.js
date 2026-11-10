"use strict";

const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const journal = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const base = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const screenshot = path.resolve(__dirname, "../output/integration-validation/live-kernel-mandate-complete12-mobile.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => /复命待战|战后/.test(document.querySelector("#officeMandateLedger")?.innerText || ""), null, { timeout: 45000 });
    await page.locator("#officeMandateLedger").scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      const ledger = document.querySelector("#officeMandateLedger");
      const item = ledger.querySelector("li");
      return {
        viewport: innerWidth,
        documentWidth: document.documentElement.scrollWidth,
        drawerLeft: drawer.left,
        drawerRight: drawer.right,
        ledgerClientWidth: ledger.clientWidth,
        ledgerScrollWidth: ledger.scrollWidth,
        itemClientWidth: item?.clientWidth || 0,
        itemScrollWidth: item?.scrollWidth || 0,
        text: ledger.innerText
      };
    });
    assert(layout.drawerLeft >= -1 && layout.drawerRight <= layout.viewport + 1);
    assert(layout.documentWidth <= layout.viewport + 1);
    assert(layout.ledgerScrollWidth <= layout.ledgerClientWidth + 1);
    assert(layout.itemScrollWidth <= layout.itemClientWidth + 1);
    assert.match(layout.text, /战后告捷|战后失利|复命待战/);
    assert.equal(errors.length, 0);
    await page.screenshot({ path: screenshot, fullPage: true });
    assert(fs.statSync(screenshot).size > 8000);
    console.log(JSON.stringify({ result: "PASS", viewport: "390x844", noHorizontalOverflow: true, cloudMandateVisible: true, screenshot: path.basename(screenshot) }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
