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
const timeout = Number(process.env.DONGZHOU_MEMBERSHIP_TIMEOUT_MS || 180000);
const applyViaMessage = process.env.DONGZHOU_MEMBERSHIP_APPLY_VIA_MESSAGE === "1";
const applyMessage = "我明确要求你现在提交我的加入组织申请：应聘东周朝廷军府属官岗位。";
const installation = process.env.DONGZHOU_MEMBERSHIP_INSTALLATION || crypto.randomUUID();
const cleanupOnly = process.env.DONGZHOU_MEMBERSHIP_CLEANUP_ONLY === "1";
const outputDir = path.resolve(__dirname, "../output/integration-validation");
const reportPath = path.join(outputDir, "live-membership-browser.json");
const joinedScreenshot = path.join(outputDir, "live-membership-joined.png");
const releasedScreenshot = path.join(outputDir, "live-membership-released.png");
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((entry) => entry && fs.existsSync(entry));

async function readRoster(page) {
  return page.evaluate(async () => {
    const response = await fetch("/api/dongzhou/v1/organization/roster", {
      cache: "no-store",
      credentials: "same-origin",
    });
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
  throw new Error(`${label} did not become authoritative within ${timeout}ms: ${JSON.stringify(roster)}`);
}

async function openOffice(page) {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
  await page.click("#campaignOfficeButton");
  await page.waitForSelector("#campaignOfficeBackdrop:not([hidden])", { timeout: 45000 });
}

async function sendDirectMessage(page, content) {
  return page.evaluate(async (message) => {
    const response = await fetch("/api/dongzhou/v1/npcs/DuBo/messages", {
      method: "POST",
      cache: "no-store",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_request_id: crypto.randomUUID(), content: message }),
    });
    if (!response.ok) throw new Error(`message failed: ${response.status} ${await response.text()}`);
    return response.json();
  }, content);
}

async function waitForMessageReply(page, taskId, waitMs = 60000) {
  const deadline = Date.now() + waitMs;
  while (Date.now() < deadline) {
    const found = await page.evaluate(async (expectedTaskId) => {
      const response = await fetch("/api/dongzhou/v1/npcs/DuBo/correspondence?limit=20", {
        cache: "no-store",
        credentials: "same-origin",
      });
      if (!response.ok) return false;
      const body = await response.json();
      return (body.messages || []).some((message) => message.taskId === expectedTaskId);
    }, taskId);
    if (found) return;
    await page.waitForTimeout(1000);
  }
  throw new Error(`NPC reply did not arrive for ${taskId}`);
}

async function requestLeave(page) {
  await openOffice(page);
  await page.waitForFunction(() => !document.querySelector("#officeMembershipLeave")?.hidden, null, { timeout: 45000 });
  await page.click("#officeMembershipLeave");
  await page.waitForFunction(() => !document.querySelector("#officeMembershipLeaveConfirm")?.hidden, null, { timeout: 60000 });
  await page.click("#officeMembershipLeaveConfirm");
}

(async () => {
  assert.notEqual(new URL(url).searchParams.get("offline"), "1", "Live acceptance cannot use offline mode");
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), installation);
  const page = await context.newPage();
  const pageErrors = [];
  const messageTasks = [];
  let joined = false;

  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("response", async (response) => {
    const pathname = new URL(response.url()).pathname;
    if (response.request().method() !== "POST" || !pathname.endsWith("/npcs/DuBo/messages")) return;
    if (response.status() !== 200) {
      messageTasks.push({ status: response.status(), error: await response.text() });
      return;
    }
    const body = await response.json();
    messageTasks.push({ status: response.status(), state: body.state, taskId: body.taskId });
  });

  try {
    await openOffice(page);
    const initial = await readRoster(page);
    if (cleanupOnly) {
      if (initial.playerMembership) {
        const pendingConfirmation = await sendDirectMessage(page, "确认退出");
        await waitForMessageReply(page, pendingConfirmation.taskId);
        let current = await readRoster(page);
        if (current.playerMembership) {
          const initiated = await sendDirectMessage(page, "我想退出组织。");
          await waitForMessageReply(page, initiated.taskId);
          const confirmed = await sendDirectMessage(page, "确认退出");
          await waitForMessageReply(page, confirmed.taskId);
          current = await readRoster(page);
          if (current.playerMembership) {
            const explicitRelease = await sendDirectMessage(page, "我要退出东周朝廷。");
            await waitForMessageReply(page, explicitRelease.taskId);
          }
          current = await waitForRoster(page, (roster) => !roster.playerMembership, "Cleanup membership release");
        }
        assert(current.openPositions.some((position) => position.office === "officer_12"), "Cleanup did not release officer_12");
      }
      console.log(JSON.stringify({ result: "PASS", mode: "cleanup", installation, membershipReleased: true }));
      return;
    }
    assert.equal(initial.playerMembership, null, "Fresh acceptance player unexpectedly already has a court membership");
    assert(initial.openPositions.some((position) => position.office === "officer_12"), "Reserved court position officer_12 is not open");
    await page.waitForFunction(() => !document.querySelector("#officeMembershipApply")?.disabled, null, { timeout: 45000 });

    if (applyViaMessage) {
      await page.selectOption("#officeMemberSelect", "DuBo");
      await page.fill("#officeMessageInput", applyMessage);
      await page.click("#officeMessageForm button[type=submit]");
    } else {
      await page.click("#officeMembershipApply");
    }
    const admitted = await waitForRoster(page, (roster) => Boolean(roster.playerMembership), "Player membership");
    joined = true;
    assert.equal(admitted.playerMembership.office, "officer_12");
    assert.equal(admitted.playerMembership.directManagerHeroId, "DuBo");
    assert(Number.isSafeInteger(admitted.playerMembership.contributionBalance));
    await page.waitForFunction(() => document.querySelector("#officeMembershipState")?.textContent.includes("已入仕"), null, { timeout: 45000 });
    fs.mkdirSync(outputDir, { recursive: true });
    await page.locator(".office-membership").screenshot({ path: joinedScreenshot });

    await page.click("#officeMembershipLeave");
    await page.waitForFunction(() => !document.querySelector("#officeMembershipLeaveConfirm")?.hidden, null, { timeout: 60000 });
    await page.click("#officeMembershipLeaveConfirm");
    const released = await waitForRoster(page, (roster) => !roster.playerMembership, "Released membership");
    joined = false;
    assert(released.openPositions.some((position) => position.office === "officer_12"), "Reserved court position was not released");
    await page.waitForFunction(() => document.querySelector("#officeMembershipState")?.textContent.includes("尚未入仕"), null, { timeout: 45000 });
    await page.locator(".office-membership").screenshot({ path: releasedScreenshot });

    assert.equal(messageTasks.length, 2, JSON.stringify(messageTasks));
    assert(messageTasks.every((entry) => entry.status === 200 && entry.state === "ACCEPTED"), JSON.stringify(messageTasks));
    assert.deepEqual(pageErrors, []);
    const report = {
      result: "PASS",
      mode: "real-ainpc-orgflow-browser-no-interception",
      installation,
      position: admitted.playerMembership.office,
      managerHeroId: admitted.playerMembership.directManagerHeroId,
      contributionBalance: admitted.playerMembership.contributionBalance,
      messageTasks,
      membershipReleased: true,
      screenshots: [joinedScreenshot, releasedScreenshot],
    };
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
    console.log(JSON.stringify(report));
  } finally {
    if (joined) {
      try {
        await requestLeave(page);
        await waitForRoster(page, (roster) => !roster.playerMembership, "Cleanup membership release");
      } catch (cleanupError) {
        console.error(JSON.stringify({ cleanup: "FAIL", message: cleanupError.message, installation }));
      }
    }
    await context.close();
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: "FAIL", errorType: error.name, message: error.message, stack: error.stack }));
  process.exitCode = 1;
});
