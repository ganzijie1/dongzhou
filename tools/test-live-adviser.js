"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.fill("#officeAdviserQuestion", "本关史料中的关键人物是谁？请简要说明。 ");
    const acceptedPromise = page.waitForResponse((response) =>
      response.url().endsWith("/api/dongzhou/v1/adviser/questions")
      && response.request().method() === "POST"
    );
    await page.click("#officeAdviserAsk");
    const accepted = await acceptedPromise;
    assert.equal(accepted.status(), 200, await accepted.text());
    const acceptedBody = await accepted.json();
    assert.equal(acceptedBody.state, "PROCESSING");

    await page.waitForFunction(() => {
      const journal = JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1") || "null");
      return journal?.result?.state === "ANSWERED" && Boolean(journal.result.answer);
    }, null, { timeout: 180000 });
    const journal = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
    assert.equal(journal.result.state, "ANSWERED");
    assert.ok(journal.result.answer.length > 0);
    assert.equal(await page.locator("#officeAdviserAnswer").innerText(), journal.result.answer);

    const screenshot = path.resolve(__dirname, "../output/integration-validation/live-adviser-complete108.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/live-adviser-complete108-mobile.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.locator(".office-adviser").screenshot({ path: screenshot });
    await page.setViewportSize({ width: 360, height: 760 });
    const mobileLayout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      panelWidth: document.querySelector(".office-adviser").getBoundingClientRect().width
    }));
    assert.ok(mobileLayout.scrollWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    assert.ok(mobileLayout.panelWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    await page.locator(".office-adviser").screenshot({ path: mobileScreenshot });

    const feedbackPromise = page.waitForResponse((response) =>
      response.url().includes("/adviser/questions/")
      && response.url().endsWith("/feedback")
      && response.request().method() === "POST"
    );
    await page.click('[data-adviser-rating="accurate"]');
    const feedback = await feedbackPromise;
    assert.equal(feedback.status(), 200, await feedback.text());
    await page.waitForFunction(() => document.querySelector("#officeAdviserAnswer").textContent.includes("已记下评价"));
    assert.deepEqual(errors, []);

    const evidence = {
      result: "PASS",
      questionId: journal.result.questionId,
      intentType: journal.result.intentType,
      answer: journal.result.answer,
      guideIgnored: journal.result.guideIgnored,
      feedback: "accurate",
      screenshot,
      mobileScreenshot
    };
    const evidencePath = path.resolve(__dirname, "../output/integration-validation/live-adviser-complete108.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2) + "\n", "utf8");
    console.log(JSON.stringify({ ...evidence, evidencePath }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
