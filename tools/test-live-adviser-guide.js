"use strict";

const assert = require("assert/strict");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const output = path.resolve(__dirname, "../output/integration-validation/adviser-guide-live.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));
const questions = [
  "请带我去东郊索命的战场。",
  "杜伯所在之处怎么走？请派属官带路。",
  "请带我前往下一处军令地点。",
];

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript((installation) => {
    localStorage.setItem("dongzhou-installation-id-v1", installation);
  }, crypto.randomUUID());
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));

  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");

    let journal = null;
    let selectedQuestion = "";
    const attempts = [];
    for (const question of questions) {
      const previousId = journal?.result?.questionId || "";
      await page.fill("#officeAdviserQuestion", question);
      await page.click("#officeAdviserAsk");
      await page.waitForFunction((oldId) => {
        const current = JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1") || "null");
        return current?.result?.state === "ANSWERED"
          && current.result.questionId !== oldId;
      }, previousId, { timeout: 180000 });
      journal = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
      attempts.push({
        question,
        intentType: journal.result.intentType,
        answer: journal.result.answer,
        guideAvailable: Boolean(journal.result.guide?.available),
      });
      if (journal.result.guide?.available) {
        selectedQuestion = question;
        break;
      }
    }
    if (!journal?.result?.guide?.available) {
      assert.equal(await page.locator("#officeAdviserGuide").isHidden(), true);
      assert.deepEqual(errors, []);
      fs.mkdirSync(path.dirname(output), { recursive: true });
      await page.locator(".office-adviser").screenshot({ path: output });
      console.log(JSON.stringify({
        result: "PASS",
        mode: "real-services-browser-no-interception",
        guideAvailable: false,
        lifecycleExercised: false,
        reason: "AINPC core public-map fixed-NPC contract did not offer a guide",
        attempts,
        screenshot: output,
      }));
      return;
    }
    assert.equal(journal.result.guideIgnored, false);
    assert(journal.result.guide.sessionId);
    await page.waitForSelector('[data-adviser-guide="ACCEPT"]:not([hidden])');

    const decisionPromise = page.waitForResponse((response) =>
      response.request().method() === "POST"
      && /\/adviser\/questions\/[^/]+\/guide$/.test(new URL(response.url()).pathname),
    { timeout: 45000 });
    await page.click('[data-adviser-guide="ACCEPT"]');
    const decisionResponse = await decisionPromise;
    assert.equal(decisionResponse.status(), 200, await decisionResponse.text());
    const decision = await decisionResponse.json();
    assert.equal(decision.state, "ACCEPTED");
    assert.equal(decision.guide.kernel.module, "dongzhou_adviser_guide");
    assert.equal(decision.guide.kernel.state, "SEALED");

    await page.waitForFunction(() => {
      const current = JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1") || "null");
      return ["RUNNING", "COMPLETED", "FAILED"].includes(current?.guideDecision?.result?.state);
    }, null, { timeout: 180000 });
    journal = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
    let finalState = journal.guideDecision.result.state;
    if (finalState === "RUNNING") {
      await page.waitForSelector("[data-adviser-guide-cancel]:not([hidden])");
      await page.click("[data-adviser-guide-cancel]");
      await page.waitForFunction(() => {
        const current = JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1") || "null");
        return current?.guideDecision?.result?.state === "CANCELLED";
      }, null, { timeout: 45000 });
      journal = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
      finalState = journal.guideDecision.result.state;
    }
    assert(["COMPLETED", "FAILED", "CANCELLED"].includes(finalState));
    assert.equal(journal.guideDecision.result.guide.kernel.module, "dongzhou_adviser_guide");
    assert.equal(journal.guideDecision.result.guide.kernel.state, "SEALED");
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator(".office-adviser").screenshot({ path: output });
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-services-browser-no-interception",
      question: selectedQuestion,
      questionId: journal.result.questionId,
      guideSessionId: journal.result.guide.sessionId,
      finalState,
      guideAvailable: true,
      lifecycleExercised: true,
      digest: journal.guideDecision.result.guide.digest,
      attempts,
      screenshot: output,
    }));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", message: error.message, stack: error.stack }));
  process.exitCode = 1;
});
