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
const output = path.resolve(__dirname, "../output/integration-validation/merit-commendation-live.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 1000 } });
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
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 45000 });

    const ledgerPromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "GET"
        && pathname.endsWith("/organization/members/ZuoRu/contributions");
    }, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");
    const ledgerResponse = await ledgerPromise;
    assert.equal(ledgerResponse.status(), 200, await ledgerResponse.text());
    const ledger = await ledgerResponse.json();
    const contribution = ledger.entries.find((entry) => Number(entry.amount) > 0
      && /^(?:organization-task|virtual_task):[0-9a-f-]{36}$/i.test(entry.sourceRef));
    assert(contribution, "ZuoRu has no positive contribution backed by an organization task");

    const dossierPromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "GET"
        && pathname.endsWith(`/organization/members/ZuoRu/contributions/${contribution.entryId}/dossier`);
    }, { timeout: 45000 });
    await page.click(`[data-contribution-dossier-id="${contribution.entryId}"]`);
    const dossierResponse = await dossierPromise;
    assert.equal(dossierResponse.status(), 200, await dossierResponse.text());
    const dossier = (await dossierResponse.json()).dossier;

    const commendationPromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "POST"
        && pathname.endsWith("/npcs/ZuoRu/merit-commendations");
    }, { timeout: 45000 });
    await page.click(`[data-merit-commendation-id="${contribution.entryId}"]`);
    const commendationResponse = await commendationPromise;
    assert.equal(commendationResponse.status(), 200, await commendationResponse.text());
    const result = await commendationResponse.json();
    assert.equal(result.state, "COMPLETED");
    assert.equal(result.commendation.entryId, contribution.entryId);
    assert.equal(result.commendation.affectionType, "appreciation");
    assert.equal(result.commendation.affectionDelta, 3);
    assert.equal(result.commendation.contribution.digest, contribution.digest);
    assert.equal(result.commendation.contributionDossier.digest, dossier.digest);
    assert.equal(result.commendation.kernel.module, "dongzhou_npc_merit_commendation");
    assert.equal(result.commendation.kernel.state, "SEALED");

    await page.waitForFunction((entryId) => {
      const receipt = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"))
        ?.organization?.commendations?.find((entry) => entry.entryId === entryId);
      return receipt?.kernel?.module === "dongzhou_npc_merit_commendation";
    }, contribution.entryId);
    await page.waitForFunction((entryId) => {
      const button = document.querySelector(`[data-merit-commendation-id="${entryId}"]`);
      return button?.disabled && button.textContent === "已据功慰勉";
    }, contribution.entryId);

    const replay = await page.evaluate(async ({ entryId, entryDigest, dossierDigest }) => {
      const response = await fetch("/api/dongzhou/v1/npcs/ZuoRu/merit-commendations", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          contribution_entry_id: entryId,
          contribution_entry_digest: entryDigest,
          contribution_dossier_digest: dossierDigest,
        }),
      });
      return { status: response.status, body: await response.json() };
    }, {
      entryId: contribution.entryId,
      entryDigest: contribution.digest,
      dossierDigest: dossier.digest,
    });
    assert.equal(replay.status, 200);
    assert.equal(replay.body.state, "COMPLETED");
    assert.equal(replay.body.replayed, true);
    assert.equal(replay.body.commendation.digest, result.commendation.digest);
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator(`[data-merit-commendation-id="${contribution.entryId}"]`).locator("xpath=../..").screenshot({ path: output });
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-services-browser-no-interception",
      heroId: "ZuoRu",
      entryId: contribution.entryId,
      affectionDelta: result.commendation.affectionDelta,
      digest: result.commendation.digest,
      replayed: replay.body.replayed,
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
