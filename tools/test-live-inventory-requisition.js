"use strict";

const assert = require("assert/strict");
const { randomUUID } = require("crypto");
const fs = require("fs");
const path = require("path");

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const installationId = "00000000-0000-4000-8000-000000005021";
const requestId = "00000000-0000-4000-8000-000000005022";
const pendingKey = "dongzhou-pending-inventory-requisition-v1";
const approvalScreenshot = path.resolve(__dirname, "../output/integration-validation/inventory-requisition-approval-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), installationId);
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => !document.querySelector("#officeInventoryRequisition")?.disabled);

    const before = await page.evaluate(async () => ({
      inventory: await window.DongzhouIntegration.organizationInventory(),
      profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"))
    }));
    const beforeBalance = before.inventory.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance;
    const alreadyApplied = before.profile.organization.inventoryRequisitionIds.includes(requestId);
    assert.ok(Number.isInteger(beforeBalance) && beforeBalance >= 20, `insufficient live task credit: ${beforeBalance}`);
    assert.ok(before.profile.campaignResources.provisions <= 188);

    await page.evaluate(({ key, request }) => {
      localStorage.setItem(key, JSON.stringify({
        client_request_id: request,
        units: 20,
        stage_id: "01"
      }));
    }, { key: pendingKey, request: requestId });
    const draftResponsePromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === "/api/dongzhou/v1/organization/inventory/requisitions"
      && response.status() === 200
    ));
    await page.click("#officeInventoryRequisition");
    const draftResponse = await draftResponsePromise;
    let receipt = await draftResponse.json();
    if (receipt.state === "REQUIRES_ACTION") {
      assert.equal(receipt.requisition.kernel.module, "dongzhou_mandate_workflow");
      assert.equal(receipt.requisition.state, "DRAFT");
      assert.equal(receipt.action.code, "approve_inventory_requisition");
      const draftInventory = await page.evaluate(() => window.DongzhouIntegration.organizationInventory());
      assert.equal(draftInventory.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance, beforeBalance, "Draft creation must not debit inventory");
      await page.waitForSelector("#officeInventoryApproval:not([hidden])");
      assert.match(await page.locator("#officeInventoryApproval").innerText(), /内核待裁/);
      const approvalResponsePromise = page.waitForResponse((response) => (
        new URL(response.url()).pathname.endsWith("/resume") && response.status() === 200
      ));
      await page.click("#officeInventoryApprove");
      receipt = await (await approvalResponsePromise).json();
    }
    assert.equal(receipt.state, "COMPLETED");
    assert.equal(receipt.requestId, requestId);
    assert.equal(receipt.inventoryDebit.delta, -20);
    assert.equal(receipt.effect.provisions, 12);

    await page.waitForFunction((id) => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      return !localStorage.getItem("dongzhou-pending-inventory-requisition-v1")
        && profile.organization.inventoryRequisitionIds.includes(id);
    }, requestId);
    const after = await page.evaluate(async () => ({
      inventory: await window.DongzhouIntegration.organizationInventory(),
      profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"))
    }));
    const afterBalance = after.inventory.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance;
    assert.equal(afterBalance, beforeBalance - (alreadyApplied ? 0 : 20));
    assert.equal(after.profile.campaignResources.provisions, before.profile.campaignResources.provisions + (alreadyApplied ? 0 : 12));

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const persisted = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    assert.equal(persisted.campaignResources.provisions, after.profile.campaignResources.provisions);
    assert.equal(persisted.organization.inventoryRequisitions.filter((entry) => entry.requestId === requestId).length, 1);

    const replay = await page.evaluate(async ({ request, key }) => {
      const response = await window.DongzhouIntegration.requisitionOrganizationInventory({
        client_request_id: request,
        units: 20,
        stage_id: "01"
      });
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      const recorded = window.DongzhouOrganizationPlay.recordInventoryRequisition(profile.organization, response);
      window.DongzhouIntegration.acknowledgeOrganizationInventoryRequisition(request);
      return {
        replayed: response.replayed,
        applied: recorded.applied,
        pending: localStorage.getItem(key)
      };
    }, { request: requestId, key: pendingKey });
    assert.equal(replay.replayed, true);
    assert.equal(replay.applied, false);
    assert.equal(replay.pending, null);
    const finalInventory = await page.evaluate(() => window.DongzhouIntegration.organizationInventory());
    assert.equal(finalInventory.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance, afterBalance);

    const rejectionRequestId = randomUUID();
    const beforeRejection = finalInventory.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance;
    await page.click("#campaignOfficeButton").catch(() => {});
    await page.waitForFunction(() => !document.querySelector("#officeInventoryRequisition")?.disabled);
    await page.evaluate(({ key, request }) => {
      localStorage.setItem(key, JSON.stringify({
        input: { client_request_id: request, units: 20, stage_id: "01" },
        result: null,
        decision: null
      }));
    }, { key: pendingKey, request: rejectionRequestId });
    const rejectionDraftPromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === "/api/dongzhou/v1/organization/inventory/requisitions"
      && response.status() === 200
    ));
    await page.click("#officeInventoryRequisition");
    assert.equal((await (await rejectionDraftPromise).json()).state, "REQUIRES_ACTION");
    await page.waitForSelector("#officeInventoryApproval:not([hidden])");
    await page.setViewportSize({ width: 320, height: 760 });
    await page.locator("#officeInventoryApproval").scrollIntoViewIfNeeded();
    const approvalLayout = await page.locator("#officeInventoryApproval").evaluate((element) => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth };
    });
    assert.ok(approvalLayout.left >= 0 && approvalLayout.right <= approvalLayout.viewport + 1, JSON.stringify(approvalLayout));
    assert.ok(approvalLayout.scrollWidth <= approvalLayout.viewport + 1, JSON.stringify(approvalLayout));
    fs.mkdirSync(path.dirname(approvalScreenshot), { recursive: true });
    await page.locator("#officeInventoryApproval").screenshot({ path: approvalScreenshot });
    const rejectionPromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname.endsWith("/resume") && response.status() === 200
    ));
    await page.click("#officeInventoryReject");
    const rejected = await (await rejectionPromise).json();
    assert.equal(rejected.state, "REJECTED");
    await page.waitForFunction(() => !localStorage.getItem("dongzhou-pending-inventory-requisition-v1"));
    const afterRejection = await page.evaluate(() => window.DongzhouIntegration.organizationInventory());
    assert.equal(afterRejection.accounts.find((entry) => entry.resourceKey === "task.execution")?.balance, beforeRejection, "Rejected draft must not debit inventory");
    assert.deepEqual(errors, []);

    console.log(JSON.stringify({
      result: "PASS",
      mode: alreadyApplied ? "IDEMPOTENT_REPLAY" : "FIRST_APPLY",
      requestId,
      balance: `${beforeBalance}->${afterBalance}`,
      provisions: `${before.profile.campaignResources.provisions}->${after.profile.campaignResources.provisions}`,
      reload: "PASS",
      replay: "NO_DOUBLE_APPLY",
      nexusApproval: "REQUIRED",
      rejection: "NO_DEBIT",
      mobileNoOverflow: true,
      approvalScreenshot
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
