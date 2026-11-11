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
const timeout = Number(process.env.DONGZHOU_CAREER_TIMEOUT_MS || 240000);
const installation = process.env.DONGZHOU_CAREER_INSTALLATION || crypto.randomUUID();
const outputDir = path.resolve(__dirname, "../output/integration-validation");
const reportPath = path.join(outputDir, "live-player-career-browser.json");
const screenshotPath = path.join(outputDir, "live-player-career-browser.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

async function readRoster(page) {
  return page.evaluate(async () => {
    const response = await fetch("/api/dongzhou/v1/organization/roster", { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) throw new Error(`roster failed: ${response.status} ${await response.text()}`);
    return response.json();
  });
}

async function waitForRoster(page, predicate, label) {
  const deadline = Date.now() + timeout;
  let roster = null;
  while (Date.now() < deadline) {
    roster = await readRoster(page);
    if (predicate(roster)) return roster;
    await page.waitForTimeout(2000);
  }
  throw new Error(`${label} did not become authoritative: ${JSON.stringify(roster)}`);
}

async function waitForCareerReply(page, previousText, label) {
  await page.waitForFunction(
    (previous) => {
      const feedback = document.querySelector("#officeCareerFeedback")?.textContent?.trim() || "";
      const busy = [...document.querySelectorAll("#officeCareer button")].some((button) => button.disabled);
      return !busy && feedback && feedback !== previous && !feedback.includes("……") && !feedback.includes("稍后可在府中书问查看");
    },
    previousText,
    { timeout },
  );
  const text = (await page.locator("#officeCareerFeedback").textContent()).trim();
  assert(text, `${label} returned an empty reply`);
  return text;
}

async function careerAction(page, selector, label) {
  const previous = (await page.locator("#officeCareerFeedback").textContent()).trim();
  await page.click(selector);
  return waitForCareerReply(page, previous, label);
}

async function releaseMembership(page) {
  const roster = await readRoster(page);
  if (!roster.playerMembership) return;
  await page.click("#officeMembershipLeave");
  await page.waitForSelector("#officeMembershipLeaveConfirm:not([hidden])", { timeout });
  await page.click("#officeMembershipLeaveConfirm");
  await waitForRoster(page, (current) => !current.playerMembership, "Membership release");
}

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot run offline");
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
    const initial = await readRoster(page);
    assert.equal(initial.playerMembership, null, "Fresh player unexpectedly already has a court membership");
    await page.waitForFunction(() => !document.querySelector("#officeMembershipApply")?.disabled, null, { timeout });
    await page.click("#officeMembershipApply");
    const admitted = await waitForRoster(page, (roster) => Boolean(roster.playerMembership), "Player admission");
    joined = true;
    await page.waitForSelector("#officeCareer:not([hidden])", { timeout });
    const startingContribution = Number(admitted.playerMembership.contributionBalance || 0);

    const optionsReply = await careerAction(page, "#officeCareerOptions", "Task options");
    assert.match(optionsReply, /任务|差事|申请|领取/, optionsReply);
    const structuredTaskName = optionsReply.match(/(?:^|\n)\s*1\.\s*[^｜\n]*｜([^（｜\n]+)(?:（[^）]+）)?/)?.[1]?.trim();
    const naturalTaskName = [...optionsReply.matchAll(/([\u4e00-\u9fff]{2,12}任务)/g)]
      .map((match) => match[1])
      .find((name) => !/(几个|组织|岗位|申请|领取|可供)/.test(name));
    const firstTaskName = structuredTaskName || naturalTaskName;
    assert(firstTaskName, `Could not extract the first authoritative task name: ${optionsReply}`);
    await page.fill("#officeCareerTaskName", firstTaskName);
    const requestReply = await careerAction(page, "#officeCareerRequestForm button[type=submit]", "Task request");
    assert.match(requestReply, /任务|接受|派|安排|领/, requestReply);
    const inboxReply = await careerAction(page, "#officeCareerInbox", "Task inbox");
    assert.match(inboxReply, /任务|待办|接受|处理/, inboxReply);
    const acceptReply = await careerAction(page, "#officeCareerAccept", "Task acceptance");
    assert.match(acceptReply, /任务|接受|执行|开始|受命/, acceptReply);

    const resultSummary = "已核清军府粮册与入库数目，账目相符，封存复核记录。";
    await page.fill("#officeCareerResult", resultSummary);
    const previous = (await page.locator("#officeCareerFeedback").textContent()).trim();
    await page.click("#officeCareerResultForm button[type=submit]");
    const resultReply = await waitForCareerReply(page, previous, "Task result");
    assert.match(resultReply, /复命|成果|完成|审核|贡献|收纳/, resultReply);

    const settled = await waitForRoster(
      page,
      (roster) => Number(roster.playerMembership?.contributionBalance || 0) > startingContribution,
      "Contribution settlement",
    );
    await page.waitForFunction(
      (value) => Number((document.querySelector("#officeCareerAccount")?.textContent || "").match(/可用贡献\s*(\d+)/)?.[1] || 0) > value,
      startingContribution,
      { timeout },
    );
    fs.mkdirSync(outputDir, { recursive: true });
    await page.locator("#officeCareer").screenshot({ path: screenshotPath });
    assert.deepEqual(pageErrors, []);

    const report = {
      result: "PASS",
      mode: "real-ainpc-orgflow-player-career-browser-no-interception",
      installation,
      position: admitted.playerMembership.office,
      managerHeroId: admitted.playerMembership.directManagerHeroId,
      contributionBefore: startingContribution,
      contributionAfter: Number(settled.playerMembership.contributionBalance),
      replies: { optionsReply, requestReply, inboxReply, acceptReply, resultReply },
      screenshot: screenshotPath,
    };
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
    console.log(JSON.stringify(report));
  } finally {
    if (joined) {
      try {
        await releaseMembership(page);
      } catch (cleanupError) {
        console.error(JSON.stringify({ cleanup: "FAIL", installation, message: cleanupError.message }));
      }
    }
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, message: error.message, stack: error.stack }));
  process.exitCode = 1;
});
