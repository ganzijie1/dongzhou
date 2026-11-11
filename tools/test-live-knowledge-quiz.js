"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }

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

    const startResponsePromise = page.waitForResponse((response) =>
      response.url().endsWith("/api/dongzhou/v1/knowledge/quiz") && response.request().method() === "POST"
    );
    await page.click("#officeQuizStart");
    const startResponse = await startResponsePromise;
    assert.equal(startResponse.status(), 200);
    const started = await startResponse.json();
    assert.equal(started.question.options.length, 4);
    assert.equal(JSON.stringify(started).includes("correctIndex"), false);
    assert.equal(started.question.receipt.kernel.module, "dongzhou_knowledge_tournament");

    const stageResponse = await page.evaluate(async () => {
      const response = await fetch("api/dongzhou/v1/knowledge/stages/01", { credentials: "same-origin" });
      return response.json();
    });
    const currentPeople = new Set((stageResponse.results[0]?.entities?.npcs || []).map((entry) => entry.name || entry));
    const correctIndex = started.question.options.findIndex((name) => currentPeople.has(name));
    assert.ok(correctIndex >= 0);

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector(`[data-quiz-answer="${correctIndex}"]`);
    assert.match(await page.locator("#officeQuizStatus").innerText(), /余 \d+ 秒/);

    const answerResponsePromise = page.waitForResponse((response) =>
      response.url().includes("/knowledge/quiz/") && response.url().endsWith("/answer")
    );
    await page.click(`[data-quiz-answer="${correctIndex}"]`);
    const answerResponse = await answerResponsePromise;
    assert.equal(answerResponse.status(), 200);
    const result = await answerResponse.json();
    assert.equal(result.correct, true);
    assert.equal(result.score, 10);
    assert.equal(result.receipt.kernel.state, "SEALED");
    await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).knowledgeQuiz.score === 10);
    await page.waitForFunction(() => document.querySelector("#officeQuizStatus").textContent.includes("累计 10 分"));
    assert.match(await page.locator("#officeQuizStatus").innerText(), /本题 10 分 · 累计 10 分/);

    const screenshot = path.resolve(__dirname, "../output/integration-validation/knowledge-quiz-live.png");
    const mobileScreenshot = path.resolve(__dirname, "../output/integration-validation/knowledge-quiz-mobile-live.png");
    fs.mkdirSync(path.dirname(screenshot), { recursive: true });
    await page.locator(".office-quiz").screenshot({ path: screenshot });
    await page.setViewportSize({ width: 320, height: 760 });
    const mobileLayout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      quizWidth: document.querySelector(".office-quiz").getBoundingClientRect().width
    }));
    assert.ok(mobileLayout.scrollWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    assert.ok(mobileLayout.quizWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    await page.locator(".office-quiz").screenshot({ path: mobileScreenshot });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", score: 10, correctAnswer: result.correctAnswer, screenshot, mobileScreenshot }));
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
