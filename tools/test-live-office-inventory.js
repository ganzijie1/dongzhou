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

const url = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live inventory acceptance requires connected mode");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    const pageErrors = [];
    const inventoryStatuses = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("response", (response) => {
      if (new URL(response.url()).pathname === "/api/dongzhou/v1/organization/inventory") {
        inventoryStatuses.push(response.status());
      }
    });

    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => {
      const text = document.querySelector("#officeInventoryRevision")?.textContent || "";
      return /账本第 \d+ 版/.test(text);
    });

    const refreshResponsePromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === "/api/dongzhou/v1/organization/inventory"
      && response.status() === 200
    ));
    await page.click("#officeInventoryRefresh");
    const refreshResponse = await refreshResponsePromise;
    const inventory = await refreshResponse.json();
    assert.equal(inventory.gameServerId, "91001");
    assert.ok(Number.isInteger(inventory.revision) && inventory.revision >= 0);
    assert.ok(Array.isArray(inventory.accounts));
    await page.waitForFunction((revision) => (
      document.querySelector("#officeInventoryRevision")?.textContent === `账本第 ${revision} 版`
      && document.querySelector("#officeInventoryRefresh")?.disabled === false
    ), inventory.revision);

    const revisionText = await page.locator("#officeInventoryRevision").innerText();
    const accountText = await page.locator("#officeInventoryAccounts").innerText();
    assert.equal(revisionText, `账本第 ${inventory.revision} 版`);
    if (inventory.accounts.length === 0) {
      assert.equal(accountText, "当前无公共库存科目");
    } else {
      for (const account of inventory.accounts) {
        assert.ok(accountText.includes(String(account.balance)));
      }
    }

    const outputDir = path.resolve(__dirname, "../output/integration-validation");
    const desktopScreenshot = path.join(outputDir, "office-inventory-live.png");
    const mobileScreenshot = path.join(outputDir, "office-inventory-mobile-live.png");
    fs.mkdirSync(outputDir, { recursive: true });
    await page.locator(".office-inventory").screenshot({ path: desktopScreenshot });

    await page.setViewportSize({ width: 320, height: 760 });
    const layout = await page.evaluate(() => {
      const inventoryElement = document.querySelector(".office-inventory");
      return {
        viewportWidth: document.documentElement.clientWidth,
        documentWidth: document.documentElement.scrollWidth,
        inventoryWidth: inventoryElement.getBoundingClientRect().width,
        inventoryRight: inventoryElement.getBoundingClientRect().right,
      };
    });
    assert.ok(layout.documentWidth <= layout.viewportWidth, JSON.stringify(layout));
    assert.ok(layout.inventoryWidth <= layout.viewportWidth, JSON.stringify(layout));
    assert.ok(layout.inventoryRight <= layout.viewportWidth, JSON.stringify(layout));
    await page.locator(".office-inventory").screenshot({ path: mobileScreenshot });

    assert.ok(inventoryStatuses.length >= 2, JSON.stringify(inventoryStatuses));
    assert.ok(inventoryStatuses.every((status) => status === 200), JSON.stringify(inventoryStatuses));
    assert.deepEqual(pageErrors, []);
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real_upstreams_no_mock_routes",
      organizationId: inventory.organizationId,
      gameServerId: inventory.gameServerId,
      revision: inventory.revision,
      accountCount: inventory.accounts.length,
      requests: inventoryStatuses.length,
      mobileNoOverflow: true,
      desktopScreenshot,
      mobileScreenshot,
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
