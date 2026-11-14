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
const output = path.resolve(__dirname, "../output/integration-validation/contribution-dossier-live.png");
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

    const ledgerResponsePromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "GET"
        && pathname.endsWith("/organization/members/ZuoRu/contributions");
    }, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");
    const ledgerResponse = await ledgerResponsePromise;
    assert.equal(ledgerResponse.status(), 200, await ledgerResponse.text());
    const ledger = await ledgerResponse.json();
    const contribution = ledger.entries.find((entry) => /^(?:organization-task|virtual_task):[0-9a-f-]{36}$/i.test(entry.sourceRef));
    assert(contribution, "ZuoRu has no contribution backed by an organization task");

    const dossierResponsePromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "GET"
        && pathname.endsWith(`/organization/members/ZuoRu/contributions/${contribution.entryId}/dossier`);
    }, { timeout: 45000 });
    await page.click(`[data-contribution-dossier-id="${contribution.entryId}"]`);
    const dossierResponse = await dossierResponsePromise;
    assert.equal(dossierResponse.status(), 200, await dossierResponse.text());
    const dossier = (await dossierResponse.json()).dossier;
    assert.equal(dossier.entryId, contribution.entryId);
    assert.equal(dossier.contribution.digest, contribution.digest);
    assert.equal(dossier.taskId, contribution.sourceRef.split(":", 2)[1]);
    assert.equal(dossier.taskTrace.taskId, dossier.taskId);
    assert.equal(dossier.kernel.module, "dongzhou_organization_contribution_dossier");
    assert.equal(dossier.kernel.state, "SEALED");
    assert(dossier.taskTrace.timeline.some((entry) => entry.type === "TASK_FINALIZED"));

    const panel = page.locator(".office-contribution-dossier");
    await panel.waitFor({ timeout: 45000 });
    const text = await panel.innerText();
    assert.match(text, /功绩卷宗已封印/);
    assert.match(text, /定案/);
    assert(text.includes(dossier.digest.slice(0, 12)));
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await panel.locator("xpath=..").screenshot({ path: output });
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-services-browser-no-interception",
      heroId: "ZuoRu",
      entryId: dossier.entryId,
      taskId: dossier.taskId,
      taskState: dossier.taskState,
      timelineEntries: dossier.taskTrace.timeline.length,
      dossierDigest: dossier.digest,
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
