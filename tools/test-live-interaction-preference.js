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
const output = path.resolve(__dirname, "../output/integration-validation/live-interaction-preference.png");
const mobileOutput = path.resolve(__dirname, "../output/integration-validation/live-interaction-preference-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

function isPreferenceResponse(response) {
  return response.request().method() === "POST"
    && new URL(response.url()).pathname.endsWith("/npcs/interaction-preference");
}

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript((installation) => {
    localStorage.setItem("dongzhou-installation-id-v1", installation);
  }, crypto.randomUUID());
  const page = await context.newPage();
  const errors = [];
  const mutations = { tasks: 0, mandates: 0, monthAdvance: 0 };
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.method() !== "POST") return;
    const pathname = new URL(request.url()).pathname;
    if (pathname.endsWith("/organization/tasks")) mutations.tasks += 1;
    if (pathname.endsWith("/court/mandates")) mutations.mandates += 1;
    if (pathname.endsWith("/organization/month/advance")) mutations.monthAdvance += 1;
  });

  try {
    const bootResponsePromise = page.waitForResponse(isPreferenceResponse, { timeout: 45000 });
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const bootResponse = await bootResponsePromise;
    assert.equal(bootResponse.status(), 200, await bootResponse.text());
    const boot = await bootResponse.json();
    assert.equal(boot.enabled, true);
    assert.match(boot.aiPlayerId, /^\d+$/);
    assert.equal(boot.source, "dongzhou-player-settings");

    await page.click("#campaignSettingsButton");
    await page.waitForSelector("#campaignSettingsBackdrop:not([hidden])");
    await page.waitForSelector('#npcInteractionStatus[data-state="synced"]');
    assert.match(await page.locator("#npcInteractionStatus").innerText(), /已开启/);

    const disableResponsePromise = page.waitForResponse(isPreferenceResponse, { timeout: 45000 });
    await page.locator("#npcInteractionToggle").uncheck();
    const disableResponse = await disableResponsePromise;
    assert.equal(disableResponse.status(), 200, await disableResponse.text());
    const disabled = await disableResponse.json();
    assert.equal(disabled.enabled, false);
    assert.equal(disabled.aiPlayerId, boot.aiPlayerId);
    await page.waitForSelector('#npcInteractionStatus[data-state="synced"]');
    assert.match(await page.locator("#npcInteractionStatus").innerText(), /已关闭/);
    await page.waitForFunction(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      return profile.settings?.aiNpcInteractionEnabled === false;
    });

    const reloadResponsePromise = page.waitForResponse(isPreferenceResponse, { timeout: 45000 });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const reloadResponse = await reloadResponsePromise;
    assert.equal(reloadResponse.status(), 200, await reloadResponse.text());
    const reloaded = await reloadResponse.json();
    assert.equal(reloaded.enabled, false);
    assert.equal(reloaded.aiPlayerId, boot.aiPlayerId);
    await page.click("#campaignSettingsButton");
    await page.waitForSelector('#npcInteractionStatus[data-state="synced"]');
    assert.equal(await page.locator("#npcInteractionToggle").isChecked(), false);
    assert.match(await page.locator("#npcInteractionStatus").innerText(), /已关闭/);

    const enableResponsePromise = page.waitForResponse(isPreferenceResponse, { timeout: 45000 });
    await page.locator("#npcInteractionToggle").check();
    const enableResponse = await enableResponsePromise;
    assert.equal(enableResponse.status(), 200, await enableResponse.text());
    const enabled = await enableResponse.json();
    assert.equal(enabled.enabled, true);
    assert.equal(enabled.aiPlayerId, boot.aiPlayerId);
    await page.waitForSelector('#npcInteractionStatus[data-state="synced"]');
    assert.match(await page.locator("#npcInteractionStatus").innerText(), /已开启/);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator("#campaignUtilityPanel").screenshot({ path: output });
    await page.setViewportSize({ width: 320, height: 760 });
    const control = page.locator(".npc-interaction-control");
    await control.scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      control: (() => {
        const box = document.querySelector(".npc-interaction-control").getBoundingClientRect();
        return { left: box.left, right: box.right, width: box.width };
      })(),
    }));
    assert(layout.scrollWidth <= layout.viewport, JSON.stringify(layout));
    assert(layout.control.left >= 0 && layout.control.right <= layout.viewport, JSON.stringify(layout));
    await control.screenshot({ path: mobileOutput });

    const isolatedContext = await browser.newContext();
    await isolatedContext.addInitScript((installation) => {
      localStorage.setItem("dongzhou-installation-id-v1", installation);
    }, crypto.randomUUID());
    const isolatedPage = await isolatedContext.newPage();
    const isolatedResponsePromise = isolatedPage.waitForResponse(isPreferenceResponse, { timeout: 45000 });
    await isolatedPage.goto(url, { waitUntil: "domcontentloaded" });
    await isolatedPage.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const isolatedResponse = await isolatedResponsePromise;
    assert.equal(isolatedResponse.status(), 200, await isolatedResponse.text());
    const isolated = await isolatedResponse.json();
    assert.equal(isolated.enabled, true);
    assert.notEqual(isolated.aiPlayerId, boot.aiPlayerId);
    await isolatedContext.close();

    assert.deepEqual(mutations, { tasks: 0, mandates: 0, monthAdvance: 0 });
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-ainpc-browser-no-interception",
      aiPlayerId: boot.aiPlayerId,
      transitions: [true, false, false, true],
      reloadPersisted: true,
      playerIsolation: true,
      noGameplayMutations: true,
      mobileNoOverflow: true,
      screenshot: output,
      mobileScreenshot: mobileOutput,
    }));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, message: error.message, stack: error.stack }));
  process.exitCode = 1;
});
