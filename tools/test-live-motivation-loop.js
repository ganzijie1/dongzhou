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

const BASE = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const PROFILE = "dongzhou-h5-profile-v2";
const label = process.env.DONGZHOU_ACCEPTANCE_LABEL || "motivation-loop-complete93";
const journalPath = path.resolve(__dirname, `../.agentwork/root/${label}/acceptance-private.json`);
const resultPath = path.resolve(__dirname, `../output/integration-validation/live-${label}-motivation.json`);
const screenshotPath = path.resolve(__dirname, `../output/integration-validation/live-${label}-motivation.png`);
assert(fs.existsSync(journalPath), "The source organization-task journal is missing");
const journal = JSON.parse(fs.readFileSync(journalPath, "utf8"));
assert(journal.installation && journal.remoteTask, "The source organization-task journal is incomplete");
const previousEvidence = fs.existsSync(resultPath)
  ? JSON.parse(fs.readFileSync(resultPath, "utf8"))
  : null;
const replayVerification = previousEvidence?.taskId === journal.remoteTask && previousEvidence?.result === "PASS";

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));

function motive(snapshot, name) {
  const motives = snapshot?.motivation?.motives;
  return Array.isArray(motives) ? motives.find((entry) => entry?.name === name) || null : null;
}

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript((installation) => localStorage.setItem("dongzhou-installation-id-v1", installation), journal.installation);
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 45000 });

    const expectedName = "再办军粮转运";
    const before = await page.evaluate(() => window.DongzhouIntegration.npcState("ZuoRu"));
    const beforeMotive = motive(before, expectedName);
    const baselineScore = Number(beforeMotive?.score || 0);
    assert(Number.isFinite(baselineScore), "The initial task motive score is invalid");
    const terminalBefore = await page.evaluate(
      (taskId) => window.DongzhouIntegration.organizationTask(taskId),
      journal.remoteTask
    );
    const finalResult = terminalBefore.result?.data?.final_result || terminalBefore.result?.final_result;
    assert(["SUCCESS", "PARTIAL", "FAILURE"].includes(finalResult), "The organization task is not terminal");
    const expectedDelta = { SUCCESS: 8, PARTIAL: 18, FAILURE: 30 }[finalResult];
    const expectedScore = replayVerification ? baselineScore : baselineScore + expectedDelta;

    const persisted = await page.evaluate(async (key) => {
      const profile = JSON.parse(localStorage.getItem(key));
      return window.DongzhouIntegration.persist(profile);
    }, PROFILE);
    assert(Number.isInteger(persisted?.version), "The terminal organization state was not saved to the connected gateway");

    for (let attempt = 0; attempt < 4; attempt += 1) {
      const current = await page.evaluate(() => window.DongzhouIntegration.npcState("ZuoRu"));
      if (motive(current, expectedName)) break;
      await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
      await page.click("#officeAdvanceButton");
      await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, undefined, { timeout: 240000 });
      await page.waitForTimeout(1000);
    }

    const after = await page.evaluate(async (name) => {
      const deadline = Date.now() + 90000;
      while (Date.now() < deadline) {
        const state = await window.DongzhouIntegration.npcState("ZuoRu");
        if (state?.motivation?.motives?.some((entry) => entry?.name === name)) return state;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      return window.DongzhouIntegration.npcState("ZuoRu");
    }, expectedName);
    const afterMotive = motive(after, expectedName);
    assert(afterMotive, "The authoritative task result did not create the expected NPC motive");
    assert.equal(afterMotive.score, expectedScore, "The terminal result applied the wrong motive delta");

    const task = await page.evaluate((taskId) => window.DongzhouIntegration.organizationTask(taskId), journal.remoteTask);
    assert.equal(task.result?.data?.final_result || task.result?.final_result, finalResult);

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const replayed = await page.evaluate(() => window.DongzhouIntegration.npcState("ZuoRu"));
    assert.equal(motive(replayed, expectedName)?.score, expectedScore, "Reloading must not apply the task motive twice");

    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 45000 });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    assert(fs.statSync(screenshotPath).size > 10000, "Motivation acceptance screenshot is unexpectedly blank");
    assert.deepEqual(pageErrors, []);

    const profile = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)), PROFILE);
    const evidence = {
      result: "PASS",
      taskId: journal.remoteTask,
      installation: journal.installation,
      finalResult,
      review: task.review?.state || null,
      baselineScore,
      expectedDelta,
      expectedScore,
      replayVerification,
      motive: afterMotive,
      motivationRevisionBefore: before?.motivation?.revision,
      motivationRevisionAfter: after?.motivation?.revision,
      organizationMonth: profile?.organization?.month,
      screenshot: screenshotPath,
      pageErrors
    };
    fs.writeFileSync(resultPath, JSON.stringify(evidence, null, 2));
    console.log(JSON.stringify(evidence));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, details: error.message }));
  process.exitCode = 1;
});
