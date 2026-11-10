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
const JOURNAL = process.env.DONGZHOU_SETTLEMENT_JOURNAL
  || path.resolve(__dirname, "../.agentwork/root/kernel-mandate-complete12/acceptance-private.json");
const SCREENSHOT = path.resolve(__dirname, "../output/integration-validation/live-authoritative-settlement.png");
const PROFILE = "dongzhou-h5-profile-v2";
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((candidate) => fs.existsSync(candidate));

const journal = JSON.parse(fs.readFileSync(JOURNAL, "utf8"));
const taskId = journal.remoteTask || journal.taskId;
assert(journal.installation && taskId, "completed live task journal is incomplete");

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((installation) => {
      localStorage.setItem("dongzhou-installation-id-v1", installation);
    }, journal.installation);
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });

    const actual = await page.evaluate(async (id) => window.DongzhouIntegration.organizationTask(id), taskId);
    const snapshot = actual.result?.data || actual.result;
    assert.equal(snapshot.final_result, "SUCCESS");
    assert(actual.settlement?.settlementId);
    assert.equal(actual.closureReceipt?.state, "SEALED");

    const applied = await page.evaluate(({ id, snapshot, settlement, closureReceipt }) => {
      const play = window.DongzhouOrganizationPlay;
      let state = play.defaultState();
      state.members = [{ id: "ZuoRu", name: "左儒", office: "司徒", loyalty: 68, fatigue: 0, merit: 0 }];
      const created = play.createTask(state, {
        type: "supply", assigneeId: "ZuoRu", stageId: "01", stageTitle: "东郊索命"
      });
      created.task.remoteResult = id;
      const input = { ...snapshot, settlement, closureReceipt };
      const first = play.reconcileRemoteTasks(created.state, [input], { advanceMonth: false });
      const replayed = play.reconcileRemoteTasks(first, [input], { advanceMonth: false });
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      profile.organization = replayed;
      localStorage.setItem("dongzhou-h5-profile-v2", JSON.stringify(profile));
      return {
        firstContribution: first.contribution,
        replayContribution: replayed.contribution,
        firstMerit: first.members[0].merit,
        replayMerit: replayed.members[0].merit,
        settlementIds: replayed.settlementIds,
        closureDigest: replayed.tasks[0].closureReceipt.digest
      };
    }, { id: taskId, snapshot, settlement: actual.settlement, closureReceipt: actual.closureReceipt });

    assert.equal(applied.firstContribution, actual.settlement.organizationDelta);
    assert.equal(applied.replayContribution, applied.firstContribution);
    assert.equal(applied.firstMerit, actual.settlement.memberDelta);
    assert.equal(applied.replayMerit, applied.firstMerit);
    assert.deepEqual(applied.settlementIds, [actual.settlement.settlementId]);
    assert.match(applied.closureDigest, /^[0-9a-f]{64}$/);

    await page.goto(BASE + "?offline=1", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    assert.equal(await page.locator("#officeContribution").textContent(), String(actual.settlement.organizationDelta));
    const memberText = await page.locator("#officeMembers").innerText();
    const ledgerText = await page.locator("#officeTaskLedger").innerText();
    assert(memberText.includes(`功绩 +${actual.settlement.memberDelta}`));
    assert(ledgerText.includes("军府+100"));
    assert(ledgerText.includes("印记"));
    fs.mkdirSync(path.dirname(SCREENSHOT), { recursive: true });
    await page.screenshot({ path: SCREENSHOT, fullPage: false });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({
      result: "PASS",
      taskId,
      settlementId: actual.settlement.settlementId,
      organizationContribution: applied.replayContribution,
      memberMerit: applied.replayMerit,
      closureDigest: applied.closureDigest,
      exactlyOnce: true,
      screenshot: SCREENSHOT
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
