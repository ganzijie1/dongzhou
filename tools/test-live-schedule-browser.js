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
const output = path.resolve(__dirname, "../output/integration-validation/live-schedule-browser.png");
const mobileOutput = path.resolve(__dirname, "../output/integration-validation/live-schedule-browser-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

function isZuoRuSchedule(response, method) {
  return response.request().method() === method
    && new URL(response.url()).pathname.endsWith("/npcs/ZuoRu/schedule");
}

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((installation) => {
    localStorage.setItem("dongzhou-installation-id-v1", installation);
  }, crypto.randomUUID());
  const page = await context.newPage();
  const errors = [];
  const requests = { schedulePost: 0, tasks: 0, mandates: 0, monthAdvance: 0 };
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    const pathname = new URL(request.url()).pathname;
    if (request.method() === "POST" && pathname.endsWith("/npcs/ZuoRu/schedule")) requests.schedulePost += 1;
    if (request.method() !== "POST") return;
    if (pathname.endsWith("/organization/tasks")) requests.tasks += 1;
    if (pathname.endsWith("/court/mandates")) requests.mandates += 1;
    if (pathname.endsWith("/organization/month/advance")) requests.monthAdvance += 1;
  });

  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const initialSchedulePromise = page.waitForResponse((response) => isZuoRuSchedule(response, "GET"), { timeout: 90000 });
    const warmSchedulePromise = page.waitForResponse((response) => isZuoRuSchedule(response, "POST"), { timeout: 90000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    if (await page.locator("#officeMemberSelect").inputValue() !== "ZuoRu") {
      await page.selectOption("#officeMemberSelect", "ZuoRu");
    }
    const initialResponse = await initialSchedulePromise;
    assert.equal(initialResponse.status(), 200, await initialResponse.text());
    const warmResponse = await warmSchedulePromise;
    assert.equal(warmResponse.status(), 200, await warmResponse.text());
    const schedulePostsBeforeClick = requests.schedulePost;

    const postResponsePromise = page.waitForResponse((response) => isZuoRuSchedule(response, "POST"), { timeout: 180000 });
    const refreshedResponsePromise = page.waitForResponse((response) => isZuoRuSchedule(response, "GET"), { timeout: 180000 });
    await page.click("#officeScheduleButton");
    const postResponse = await postResponsePromise;
    assert.equal(postResponse.status(), 200, await postResponse.text());
    assert.deepEqual(postResponse.request().postDataJSON(), { force_regenerate: false });
    const refreshedResponse = await refreshedResponsePromise;
    assert.equal(refreshedResponse.status(), 200, await refreshedResponse.text());
    const body = await refreshedResponse.json();
    const plan = body.schedule?.data || body.schedule || {};
    const days = Array.isArray(plan.schedules) ? plan.schedules : [];
    assert.equal(days.length, 90);
    assert.match(plan.plan_id, /^schedule-plan-/);
    assert.match(plan.generation_id, /^[0-9a-f]{32}$/);

    const events = days.flatMap((day) => Array.isArray(day.events) ? day.events : []);
    assert(events.length >= 90);
    assert(events.every((event) => Number.isInteger(event.transaction_id)
      && event.transaction_id >= 9100101 && event.transaction_id <= 9100112));
    const planText = JSON.stringify(plan);
    assert(!/机体|银河币|天关|飞船/.test(planText));

    await page.waitForFunction(() => document.querySelector("#officeNpcSchedule")?.textContent.includes("90 日当值"));
    const scheduleText = await page.locator("#officeNpcSchedule").innerText();
    assert(scheduleText.includes(days[0].date));
    assert(scheduleText.includes(days.at(-1).date));
    assert(scheduleText.includes(String(plan.plan_id).slice(0, 24)));
    for (const event of days[0].events.slice(0, 5)) assert(scheduleText.includes(event.name));
    await page.waitForFunction(() => !document.querySelector("#officeScheduleButton").disabled, null, { timeout: 45000 });
    assert.equal(await page.locator("#officeScheduleButton").isEnabled(), true);
    assert.deepEqual(requests, { schedulePost: schedulePostsBeforeClick + 1, tasks: 0, mandates: 0, monthAdvance: 0 });
    assert.deepEqual(errors, []);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.locator(".office-npc-schedule").screenshot({ path: output });
    await page.setViewportSize({ width: 320, height: 760 });
    const schedule = page.locator(".office-npc-schedule");
    await schedule.scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      schedule: (() => {
        const box = document.querySelector(".office-npc-schedule").getBoundingClientRect();
        return { left: box.left, right: box.right, width: box.width };
      })(),
    }));
    assert(layout.scrollWidth <= layout.viewport, JSON.stringify(layout));
    assert(layout.schedule.left >= 0 && layout.schedule.right <= layout.viewport, JSON.stringify(layout));
    await schedule.screenshot({ path: mobileOutput });

    console.log(JSON.stringify({
      result: "PASS",
      mode: "real-ainpc-browser-no-interception",
      heroId: "ZuoRu",
      planId: plan.plan_id,
      generationId: plan.generation_id,
      days: days.length,
      events: events.length,
      transactionIds: [...new Set(events.map((event) => event.transaction_id))].sort(),
      foreignTermsAbsent: true,
      duplicatePosts: false,
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
