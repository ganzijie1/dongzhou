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
const timeout = Number(process.env.DONGZHOU_TASK_RESPONSE_TIMEOUT_MS || 360000);
const installation = process.env.DONGZHOU_TASK_RESPONSE_INSTALLATION || crypto.randomUUID();
const outputDir = path.resolve(__dirname, "../output/integration-validation");
const reportPath = path.join(outputDir, "live-player-task-response-browser.json");
const screenshotPath = path.join(outputDir, "live-player-task-response-browser.png");
const mobileScreenshotPath = path.join(outputDir, "live-player-task-response-mobile.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

async function getJson(page, endpoint) {
  return page.evaluate(async (target) => {
    const response = await fetch(target, { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) throw new Error(`${target} failed: ${response.status} ${await response.text()}`);
    return response.json();
  }, endpoint);
}

async function readRoster(page) {
  return getJson(page, "/api/dongzhou/v1/organization/roster");
}

async function readTasks(page) {
  return getJson(page, "/api/dongzhou/v1/organization/player-tasks");
}

async function waitFor(page, reader, predicate, label) {
  const deadline = Date.now() + timeout;
  let value = null;
  while (Date.now() < deadline) {
    value = await reader(page);
    if (predicate(value)) return value;
    await page.waitForTimeout(2000);
  }
  throw new Error(`${label} did not become authoritative: ${JSON.stringify(value)}`);
}

async function careerAction(page, selector, label) {
  console.error(`[player-task-response] ${label}: submitting`);
  const previous = (await page.locator("#officeCareerFeedback").textContent()).trim();
  await page.click(selector);
  await page.waitForFunction(
    (before) => {
      const text = document.querySelector("#officeCareerFeedback")?.textContent?.trim() || "";
      const busy = [...document.querySelectorAll("#officeCareer button")].some((button) => button.disabled);
      return !busy && text && text !== before && !text.includes("……") && !text.includes("稍后可在府中书问查看");
    },
    previous,
    { timeout },
  );
  const reply = (await page.locator("#officeCareerFeedback").textContent()).trim();
  assert(reply, `${label} returned an empty reply`);
  console.error(`[player-task-response] ${label}: reply received`);
  return reply;
}

async function releaseMembership(page) {
  if (!(await readRoster(page)).playerMembership) return;
  await page.click("#officeMembershipLeave");
  await page.waitForSelector("#officeMembershipLeaveConfirm:not([hidden])", { timeout });
  await page.click("#officeMembershipLeaveConfirm");
  await waitFor(page, readRoster, (roster) => !roster.playerMembership, "Membership release");
}

(async () => {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), installation);
  const page = await context.newPage();
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  let joined = false;

  try {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 45000 });
    assert.equal((await readRoster(page)).playerMembership, null, "Fresh player unexpectedly has a membership");
    await page.waitForFunction(() => !document.querySelector("#officeMembershipApply")?.disabled, null, { timeout });
    console.error("[player-task-response] Membership: applying");
    await page.click("#officeMembershipApply");
    await waitFor(page, readRoster, (roster) => Boolean(roster.playerMembership), "Player admission");
    console.error("[player-task-response] Membership: admitted");
    joined = true;
    await page.waitForSelector("#officeCareer:not([hidden])", { timeout });

    await page.fill("#officeCareerTaskName", "演练阵法");
    const requestReply = await careerAction(page, "#officeCareerRequestForm button[type=submit]", "Task request");
    assert.match(requestReply, /演练阵法|任务|差事|接受|派/, requestReply);
    const pending = await waitFor(
      page,
      readTasks,
      (result) => result.items?.some((task) => task.title === "演练阵法" && task.state === "MEMBER_RESPONSE_PENDING"),
      "Pending assignment",
    );
    const taskId = pending.items.find((task) => task.title === "演练阵法").taskId;
    console.error(`[player-task-response] First task: ${taskId}`);
    await page.click("#officeCareerStatusRefresh");
    await page.waitForSelector(`[data-task-id="${taskId}"].selected`, { timeout });
    await page.waitForSelector("#officeCareerResponseForm:not([hidden])", { timeout });

    const modification = "将执行总时长调整为三日（259200游戏秒）";
    await page.fill("#officeCareerResponseDetail", modification);
    const modifyReply = await careerAction(page, "#officeCareerModify", "Task modification");
    assert.match(modifyReply, /调整|改令|确认|流程|任务/, modifyReply);
    const modified = await waitFor(
      page,
      readTasks,
      (result) => result.items?.some((task) => task.taskId === taskId && task.state !== "MODIFICATION_CONFIRMATION_PENDING" && task.state !== "MEMBER_RESPONSE_PENDING"),
      "Manager modification decision",
    );
    const modifiedTask = modified.items.find((task) => task.taskId === taskId);
    console.error(`[player-task-response] First task: ${modifiedTask.state}`);
    assert.equal(modifiedTask.state, "IN_PROGRESS", `Unexpected post-modification state: ${modifiedTask.state}`);
    assert.equal(modifiedTask.organizationTrace?.state, "SEALED", "Modified task trace is not sealed");
    assert.match(modifiedTask.organizationTrace?.digest || "", /^[0-9a-f]{64}$/);

    await page.fill("#officeCareerTaskName", "巡察营垒");
    const secondRequestReply = await careerAction(page, "#officeCareerRequestForm button[type=submit]", "Second task request");
    assert.match(secondRequestReply, /巡察营垒|组织任务|差事|派发/, secondRequestReply);
    const secondPending = await waitFor(
      page,
      readTasks,
      (result) => result.items?.some((task) => task.title === "巡察营垒" && task.state === "MEMBER_RESPONSE_PENDING"),
      "Second pending assignment",
    );
    const rejectedTaskId = secondPending.items.find((task) => task.title === "巡察营垒").taskId;
    console.error(`[player-task-response] Second task: ${rejectedTaskId}`);
    await page.click("#officeCareerStatusRefresh");
    await page.click(`[data-office-career-select-task-id="${rejectedTaskId}"]`);
    await page.waitForSelector(`[data-task-id="${rejectedTaskId}"].selected`, { timeout });
    const rejection = "当前军阵器械未齐，请另派属官承办";
    await page.fill("#officeCareerResponseDetail", rejection);
    const rejectReply = await careerAction(page, "#officeCareerReject", "Task rejection");
    assert.match(rejectReply, /拒绝|不接|重新安排|记录|任务/, rejectReply);
    const rejected = await waitFor(
      page,
      readTasks,
      (result) => result.items?.some((task) => task.taskId === rejectedTaskId && task.state === "REJECTED"),
      "Rejected assignment",
    );
    const rejectedTask = rejected.items.find((task) => task.taskId === rejectedTaskId);
    console.error(`[player-task-response] Second task: ${rejectedTask.state}`);
    assert.equal(rejectedTask.organizationTrace?.state, "SEALED", "Rejected task trace is not sealed");
    assert.match(rejectedTask.organizationTrace?.digest || "", /^[0-9a-f]{64}$/);
    await page.click("#officeCareerStatusRefresh");
    await page.waitForSelector(`[data-task-id="${rejectedTaskId}"][data-task-state="REJECTED"]`, { timeout });
    assert.equal(await page.locator("#officeCareerResponseForm").isHidden(), true, "Rejected task still exposes response actions");
    await page.locator("#officeCareer").screenshot({ path: screenshotPath });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator(`[data-task-id="${rejectedTaskId}"]`).scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    assert(layout.scrollWidth <= layout.width + 1, `Mobile task response overflows: ${JSON.stringify(layout)}`);
    await page.locator("#campaignOfficeDrawer").screenshot({ path: mobileScreenshotPath });

    const report = {
      result: "PASS",
      mode: "real-ainpc-orgflow-player-task-modify-review-reject-browser",
      installation,
      modifiedTaskId: taskId,
      rejectedTaskId,
      title: rejectedTask.title,
      modification,
      modificationReply: modifyReply,
      modificationState: modifiedTask.state,
      modificationTraceDigest: modifiedTask.organizationTrace.digest,
      secondRequestReply,
      rejection,
      rejectionReply: rejectReply,
      finalState: rejectedTask.state,
      traceDigest: rejectedTask.organizationTrace.digest,
      trace: rejectedTask.organizationTrace,
      screenshots: [screenshotPath, mobileScreenshotPath],
    };
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
    console.log(JSON.stringify(report, null, 2));
    assert.deepEqual(pageErrors, [], `Page errors: ${pageErrors.join(" | ")}`);
  } finally {
    if (joined) await releaseMembership(page).catch(() => {});
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
