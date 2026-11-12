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

const output = path.resolve(__dirname, "../output/integration-validation/live-quality-loop-complete92.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto("http://127.0.0.1:8780/", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 30000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");
    await page.selectOption("#officeTaskType", "supply");
    const response = await page.evaluate(() => DongzhouIntegration.npcAssignment("ZuoRu", "supply", "01"));
    const assignment = response.assignment;
    const responsibility = assignment.quality.qualities.responsibility;
    const qualityScore = assignment.quality.fit.score;
    await page.waitForFunction(
      (value) => document.querySelector("#officeNpcState")?.innerText.includes(`担当 ${value}`),
      responsibility,
      { timeout: 90000 },
    );
    await page.waitForFunction(
      (value) => document.querySelector("#officeNpcAssignment")?.innerText.includes(`品行 ${value}/100`),
      qualityScore,
      { timeout: 90000 },
    );

    assert.equal(assignment.quality.available, true);
    assert(Number.isFinite(responsibility) && responsibility >= 0 && responsibility <= 100);
    assert(Number.isInteger(qualityScore) && qualityScore >= 0 && qualityScore <= 100);
    assert.equal(assignment.quality.fit.available, true);
    assert.equal(assignment.readiness.factors.quality, assignment.quality.fit.factor);
    assert.deepEqual(
      assignment.quality.fit.signals.map(({ quality, value }) => ({ quality, value })),
      [
        { quality: "responsibility", value: responsibility },
        { quality: "cruelty", value: assignment.quality.qualities.cruelty },
      ],
    );
    assert.equal(errors.length, 0);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator("#officeNpcState").scrollIntoViewIfNeeded();
    await page.screenshot({ path: output });
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-services-browser-no-interception",
      responsibility: assignment.quality.qualities.responsibility,
      qualityFit: assignment.quality.fit,
      readiness: assignment.readiness,
      screenshot: output,
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
