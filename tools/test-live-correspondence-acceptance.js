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
const timeout = Number(process.env.DONGZHOU_CORRESPONDENCE_TIMEOUT_MS || 180000);
const installation = crypto.randomUUID();
const marker = `live-correspondence-${crypto.randomUUID()}`;
const content = `请核验北路军粮是否已经入仓。验收记号：${marker}`;
const output = path.resolve(__dirname, "../output/integration-validation/live-correspondence-acceptance.png");
const mobileOutput = path.resolve(__dirname, "../output/integration-validation/live-correspondence-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

async function readClock(page) {
  return page.evaluate(async () => {
    const serversResponse = await fetch("/api/v1/QueryServers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    if (!serversResponse.ok) throw new Error(`server query failed: ${serversResponse.status}`);
    const servers = await serversResponse.json();
    if (!servers.servers?.[0]) throw new Error("clock server is unavailable");
    const response = await fetch("/api/v1/QueryGameTimeAndTimeScale", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ serverID: servers.servers[0] }),
    });
    if (!response.ok) throw new Error(`clock query failed: ${response.status}`);
    return response.json();
  });
}

async function openOffice(page) {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
  await page.click("#campaignOfficeButton");
  await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
  await page.selectOption("#officeMemberSelect", "ZuoRu");
  await page.waitForFunction(() => {
    const panel = document.querySelector("#officeCorrespondence");
    return panel && !panel.textContent.includes("正在调阅");
  }, null, { timeout: 45000 });
}

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), installation);
  const page = await context.newPage();
  const errors = [];
  const mutations = { organizationTasks: 0, courtMandates: 0, monthAdvance: 0 };
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.method() !== "POST") return;
    const pathname = new URL(request.url()).pathname;
    if (pathname.endsWith("/organization/tasks")) mutations.organizationTasks += 1;
    if (pathname.endsWith("/court/mandates")) mutations.courtMandates += 1;
    if (pathname.endsWith("/organization/month/advance")) mutations.monthAdvance += 1;
  });

  try {
    await openOffice(page);
    const clockBefore = await readClock(page);
    const acceptedResponsePromise = page.waitForResponse((response) => {
      const pathname = new URL(response.url()).pathname;
      return response.request().method() === "POST" && pathname.endsWith("/npcs/ZuoRu/messages");
    }, { timeout: 45000 });
    await page.fill("#officeMessageInput", content);
    await page.click("#officeMessageForm button[type=submit]");
    const acceptedResponse = await acceptedResponsePromise;
    assert.equal(acceptedResponse.status(), 200, await acceptedResponse.text());
    const accepted = await acceptedResponse.json();
    assert.equal(accepted.state, "ACCEPTED");
    assert.match(accepted.taskId, /^playerchat-/);

    const deadline = Date.now() + timeout;
    let reply = null;
    while (Date.now() < deadline && !reply) {
      const responsePromise = page.waitForResponse((response) => {
        const pathname = new URL(response.url()).pathname;
        return response.request().method() === "GET" && pathname.endsWith("/npcs/ZuoRu/correspondence");
      }, { timeout: Math.min(30000, Math.max(1000, deadline - Date.now())) });
      await page.click("#officeCorrespondenceRefresh");
      const response = await responsePromise;
      assert.equal(response.status(), 200, await response.text());
      const body = await response.json();
      reply = (body.messages || []).find((message) => message.taskId === accepted.taskId) || null;
      if (!reply) await page.waitForTimeout(2500);
    }

    assert(reply, `AINPC did not produce correspondence for ${accepted.taskId} within ${timeout}ms`);
    assert.match(reply.messageId, /\S+/);
    assert.match(reply.digest, /^[0-9a-f]{64}$/);
    assert.equal(reply.speakerId, accepted.npcId);
    assert.equal(reply.targetType, "PLAYER");
    assert(reply.content.trim().length > 0);

    const selector = `[data-correspondence-id="${reply.messageId.replace(/["\\]/g, "\\$&")}"]`;
    await page.waitForSelector(selector);
    await page.click(selector);
    await page.waitForFunction(({ messageId, digest }) => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      const selected = profile.organization?.selectedCorrespondence?.["01"];
      return selected?.messageId === messageId && selected?.digest === digest && selected?.heroId === "ZuoRu";
    }, { messageId: reply.messageId, digest: reply.digest });
    await page.waitForFunction((buttonSelector) => {
      return document.querySelector(buttonSelector)?.textContent?.includes("已取用");
    }, selector);
    assert.match(await page.locator(selector).innerText(), /已取用/);
    assert.equal(await page.locator(selector).locator("xpath=ancestor::div[contains(@class, 'office-correspondence-item')]/strong").innerText(), "左儒");
    const untranslatedNames = await page.evaluate(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2") || "{}");
      const displayed = [...document.querySelectorAll(".office-correspondence-item strong")].map((node) => node.textContent.trim());
      return (profile.organization?.members || [])
        .filter((member) => member.id !== member.name && displayed.includes(member.id))
        .map((member) => member.id);
    });
    assert.deepEqual(untranslatedNames, []);
    const displayedNames = await page.locator(".office-correspondence-item strong").allInnerTexts();
    assert(!displayedNames.includes("ZhouYouWang"));
    assert(!displayedNames.includes("DuBo"));
    assert(!displayedNames.includes("QinXiangGong"));
    assert(!displayedNames.some((name) => /^\d{12,}$/.test(name)));

    const clockAfter = await readClock(page);
    assert.equal(clockAfter.virtualTime, clockBefore.virtualTime, "Correspondence advanced the shared game clock");
    assert.deepEqual(mutations, { organizationTasks: 0, courtMandates: 0, monthAdvance: 0 });
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator("#campaignOfficeDrawer").screenshot({ path: output });
    await page.setViewportSize({ width: 320, height: 760 });
    const mobileLayout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      drawerWidth: document.querySelector("#campaignOfficeDrawer").getBoundingClientRect().width,
    }));
    assert(mobileLayout.scrollWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    assert(mobileLayout.drawerWidth <= mobileLayout.viewport, JSON.stringify(mobileLayout));
    const selectedItem = page.locator(selector).locator("xpath=ancestor::div[contains(@class, 'office-correspondence-item')]");
    await selectedItem.scrollIntoViewIfNeeded();
    const itemBox = await selectedItem.boundingBox();
    assert(itemBox && itemBox.x >= 0 && itemBox.x + itemBox.width <= mobileLayout.viewport, JSON.stringify(itemBox));
    await selectedItem.screenshot({ path: mobileOutput });

    const isolatedContext = await browser.newContext();
    await isolatedContext.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), crypto.randomUUID());
    const isolatedPage = await isolatedContext.newPage();
    await isolatedPage.goto(url, { waitUntil: "domcontentloaded" });
    await isolatedPage.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const isolatedMessages = await isolatedPage.evaluate(async () => {
      const response = await fetch("api/dongzhou/v1/npcs/ZuoRu/correspondence?limit=50", { cache: "no-store" });
      if (!response.ok) throw new Error(`isolated correspondence failed: ${response.status}`);
      return (await response.json()).messages || [];
    });
    assert(!isolatedMessages.some((message) => message.taskId === accepted.taskId || message.messageId === reply.messageId));
    await isolatedContext.close();

    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-services-browser-no-interception",
      installation,
      heroId: accepted.heroId,
      taskId: accepted.taskId,
      messageId: reply.messageId,
      digest: reply.digest,
      playerIsolation: true,
      sharedClockUnchanged: true,
      organizationMutations: mutations,
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
