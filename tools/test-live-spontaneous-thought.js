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

const output = path.resolve(__dirname, "../output/integration-validation/live-spontaneous-thought-mobile.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 320, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto("http://127.0.0.1:8780/", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await page.selectOption("#officeTaskType", "drill");
    await page.click("#officeStageKnowledgeButton");
    await page.waitForSelector("#officeKnowledgeResults .office-source-choice:not([disabled])", { timeout: 60000 });
    await page.locator("#officeKnowledgeResults .office-source-choice:not([disabled])").first().click();
    const thoughtResponsePromise = page.waitForResponse(
      (response) => /\/npcs\/[^/]+\/thoughts$/.test(new URL(response.url()).pathname),
      { timeout: 180000 }
    );
    await page.click("#officeThoughtButton");
    const thoughtResponse = await thoughtResponsePromise;
    assert.equal(thoughtResponse.status(), 200);
    const body = await thoughtResponse.json();
    const result = body.data || body;
    assert.equal(result.state, "COMPLETED");
    assert.equal(result.thoughtReceipt.thought.hasThought, true);
    await page.waitForFunction(() => /印记/.test(document.querySelector("#officeThoughtResult")?.innerText || ""), null, { timeout: 45000 });
    const options = page.locator(".office-decision-option");
    await options.nth(0).fill("不核军情，仓促撤军");
    await options.nth(1).fill("放弃检阅，闭营不出");
    const councilResponsePromise = page.waitForResponse(
      (response) => /\/npcs\/[^/]+\/decisions$/.test(new URL(response.url()).pathname),
      { timeout: 120000 }
    );
    await page.locator("#officeDecisionForm button[type=submit]").click();
    const councilResponse = await councilResponsePromise;
    assert.equal(councilResponse.status(), 200);
    const councilBody = await councilResponse.json();
    const councilResult = councilBody.data || councilBody;
    const selected = councilResult.decision?.data || councilResult.decision;
    assert.equal(selected.index, 2, "AINPC must select the signed spontaneous-thought proposal");
    await page.check("#officeUseCouncil");
    const mandateResponsePromise = page.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith("/court/mandates"),
      { timeout: 120000 }
    );
    await page.click("#officeIssueButton");
    const mandateResponse = await mandateResponsePromise;
    assert.equal(mandateResponse.status(), 200);
    const mandateBody = await mandateResponse.json();
    const mandateResult = mandateBody.data || mandateBody;
    assert.equal(mandateResult.state, "REQUIRES_ACTION");
    assert.equal(mandateResult.mandate.thought.digest, result.thoughtReceipt.digest);
    assert.equal(mandateResult.mandate.council.thought.digest, result.thoughtReceipt.digest);
    const rejectResponsePromise = page.waitForResponse(
      (response) => /\/court\/mandates\/[^/]+\/resume$/.test(new URL(response.url()).pathname),
      { timeout: 60000 }
    );
    await page.click("#officeMandateRejectButton");
    const rejectResponse = await rejectResponsePromise;
    assert.equal(rejectResponse.status(), 200);
    const rejectBody = await rejectResponse.json();
    assert.equal((rejectBody.data || rejectBody).state, "REJECTED");
    const layout = await page.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      const result = document.querySelector("#officeThoughtResult");
      const option = [...document.querySelectorAll(".office-decision-option")].at(-1);
      return {
        viewport: innerWidth,
        documentWidth: document.documentElement.scrollWidth,
        drawerLeft: drawer.left,
        drawerRight: drawer.right,
        resultWidth: result.scrollWidth,
        resultClientWidth: result.clientWidth,
        option: option.value,
        resultText: result.innerText
      };
    });
    assert.equal(layout.option, result.thoughtReceipt.councilProposal);
    assert(layout.drawerLeft >= -1 && layout.drawerRight <= layout.viewport + 1);
    assert(layout.documentWidth <= layout.viewport + 1);
    assert(layout.resultWidth <= layout.resultClientWidth + 1);
    assert.equal(errors.length, 0);
    await page.locator("#officeThoughtResult").evaluate((element) => element.scrollIntoView({ block: "center" }));
    await page.waitForTimeout(200);
    await page.screenshot({ path: output });
    assert(fs.statSync(output).size > 8000);
    console.log(JSON.stringify({
      result: "PASS",
      viewport: "320x900",
      noHorizontalOverflow: true,
      routeTo: result.thoughtReceipt.routeTo,
      importance: result.thoughtReceipt.thought.importance,
      councilSelected: selected.index,
      nexusDraft: mandateResult.state,
      finalMandateState: "REJECTED",
      digest: result.thoughtReceipt.digest,
      screenshot: path.basename(output)
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
