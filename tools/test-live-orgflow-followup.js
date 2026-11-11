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

const BASE = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/";
const INSTALLATION = process.env.DONGZHOU_ACCEPTANCE_INSTALLATION || "a07541fb-63a6-4e76-ba2c-538433178dd6";
const PARENT_TASK = process.env.DONGZHOU_PARENT_TASK_ID || "c294a867-8ab1-5b63-9787-3d3e0a8419a0";
const CHILD_TASK = process.env.DONGZHOU_CHILD_TASK_ID || "3a5c0216-1a98-5bd7-9b5a-eaf5176b2712";
const DERIVATION_INTENT = process.env.DONGZHOU_DERIVATION_INTENT_ID || "5d2f2480-cc9e-5adc-b333-26f01ddab540";
const DERIVATION_RULE = process.env.DONGZHOU_DERIVATION_RULE_ID || "dongzhou_supply_success_follow_up";
const CHILD_ASSIGNEE = process.env.DONGZHOU_CHILD_ASSIGNEE || "QinXiangGong";
const PROFILE = "dongzhou-h5-profile-v2";
const outputDirectory = path.resolve(__dirname, "../output/integration-validation");
const resultPath = path.join(outputDirectory, "live-orgflow-followup-lineage-complete86.json");
const screenshotPath = path.join(outputDirectory, "live-orgflow-followup-lineage-complete86.png");
const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(fs.existsSync);

fs.mkdirSync(outputDirectory, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(({ key, installation }) => localStorage.setItem(key, installation), {
      key: "dongzhou-installation-id-v1",
      installation: INSTALLATION,
    });
    const page = await context.newPage();
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(
      ({ key, child, assignee }) => JSON.parse(localStorage.getItem(key) || "{}").organization?.tasks
        ?.some((task) => task.remoteResult === child && task.derivation && task.assigneeId === assignee),
      { key: PROFILE, child: CHILD_TASK, assignee: CHILD_ASSIGNEE },
      { timeout: 45000 },
    );

    const evidence = await page.evaluate(async ({ key, parentId, childId }) => {
      const organization = JSON.parse(localStorage.getItem(key)).organization;
      const parent = organization.tasks.find((task) => task.remoteResult === parentId);
      const child = organization.tasks.find((task) => task.remoteResult === childId);
      const read = async (taskId) => {
        let lastStatus = 0;
        let lastBody = "";
        for (let attempt = 0; attempt < 5; attempt += 1) {
          const response = await fetch(`/api/dongzhou/v1/organization/tasks/${encodeURIComponent(taskId)}`, {
            cache: "no-store",
          });
          if (response.ok) return response.json();
          lastStatus = response.status;
          lastBody = await response.text();
          await new Promise((resolve) => setTimeout(resolve, 500 * (attempt + 1)));
        }
        throw new Error(`organization task read failed after retries: ${lastStatus} ${lastBody}`);
      };
      return {
        parent,
        child,
        parentResponse: await read(parentId),
        childResponse: await read(childId),
        ledgerText: document.querySelector("#officeTaskLedger").innerText,
      };
    }, { key: PROFILE, parentId: PARENT_TASK, childId: CHILD_TASK });

    const parentSnapshot = evidence.parentResponse.result?.data || evidence.parentResponse.result;
    const childSnapshot = evidence.childResponse.result?.data || evidence.childResponse.result;
    assert.equal(parentSnapshot.final_result, "SUCCESS");
    assert.equal(evidence.parentResponse.followUps.length, 1);
    assert.deepEqual(evidence.parentResponse.followUps[0], {
      intentId: DERIVATION_INTENT,
      taskId: CHILD_TASK,
      state: "CREATED",
      source: "FOLLOW_UP",
      taskType: "patrol",
      ruleId: DERIVATION_RULE,
      stageId: "01",
      stageTitle: "Dongzhou stage 01",
      assigneeHeroId: evidence.parent.assigneeId,
    });
    assert.equal(evidence.child.status, "active");
    assert.equal(evidence.child.type, "patrol");
    assert.equal(evidence.child.cost, 0);
    assert.equal(evidence.child.mandate, null);
    assert.equal(evidence.child.stageId, evidence.parent.stageId);
    assert.equal(evidence.child.assigneeId, evidence.childResponse.assigneeHeroId);
    assert.deepEqual(evidence.child.derivation, {
      intentId: DERIVATION_INTENT,
      source: "FOLLOW_UP",
      ruleId: DERIVATION_RULE,
      predecessorTaskId: PARENT_TASK,
    });
    assert.equal(childSnapshot.task_id, CHILD_TASK);
    assert.equal(typeof evidence.child.name, "string");
    assert(evidence.child.name.length > 0);
    assert.match(evidence.ledgerText, new RegExp(evidence.child.name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));

    const childRow = page.locator("#officeTaskLedger li").filter({ hasText: evidence.child.name });
    const scrollMetrics = await childRow.evaluate((element) => {
      const drawer = element.closest(".campaign-office-drawer");
      if (drawer) {
        const elementBox = element.getBoundingClientRect();
        const drawerBox = drawer.getBoundingClientRect();
        drawer.scrollTop += elementBox.top - drawerBox.top - drawer.clientHeight / 2;
        return { scrollTop: drawer.scrollTop, scrollHeight: drawer.scrollHeight, clientHeight: drawer.clientHeight };
      } else {
        element.scrollIntoView({ block: "center" });
        return null;
      }
    });
    await page.waitForTimeout(150);
    const screenshotBox = await childRow.boundingBox();
    assert(screenshotBox && screenshotBox.width > 300 && screenshotBox.height > 20);
    assert(screenshotBox.y > 90 && screenshotBox.y + screenshotBox.height < 1000, JSON.stringify({ screenshotBox, scrollMetrics }));
    await page.screenshot({ path: screenshotPath });
    assert(fs.statSync(screenshotPath).size > 10000);

    const result = {
      result: "PASS",
      mode: "real-services-browser-no-interception",
      parentTaskId: PARENT_TASK,
      parentResult: parentSnapshot.final_result,
      followUp: evidence.parentResponse.followUps[0],
      localTask: {
        taskId: evidence.child.remoteResult,
        type: evidence.child.type,
        cost: evidence.child.cost,
        stageId: evidence.child.stageId,
        assigneeId: evidence.child.assigneeId,
        status: evidence.child.status,
        derivation: evidence.child.derivation,
      },
      remoteChildState: childSnapshot.state,
      screenshot: path.basename(screenshotPath),
    };
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + "\n");
    console.log(JSON.stringify(result));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
