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

const executablePath = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
    await page.goto("http://127.0.0.1:8780/", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    const result = await page.evaluate(async () => {
      const taskTypes = ["supply", "drill", "patrol", "intelligence", "diplomacy"];
      const failures = [];
      for (const taskType of taskTypes) {
        try {
          return { taskType, response: await DongzhouIntegration.npcAssignment("ZuoRu", taskType, "01") };
        } catch (error) {
          failures.push(`${taskType}:${error.code || error.message}`);
        }
      }
      throw new Error(failures.join(","));
    });
    const assignment = result.response.assignment;
    const support = assignment.managerSupport;
    const positiveAffections = new Set([
      "love", "adoration", "kinship", "friendship", "dependence", "respect", "appreciation",
    ]);
    const negativeAffections = { annoyance: -4, hatred: -6 };
    const relationshipWeights = { family: 3, legal: 2, organization: 2, social: 1 };
    const affection = support.affection;
    let affectionFactor = 0;
    if (affection) {
      const value = Math.max(0, Math.min(100, Number(affection.value) || 0));
      if (positiveAffections.has(affection.type)) affectionFactor = value * 0.06;
      else if (Object.hasOwn(negativeAffections, affection.type)) {
        affectionFactor = value * negativeAffections[affection.type] / 100;
      }
    }
    const relationshipFactor = support.relationships.reduce((sum, relationship) => (
      sum + (relationshipWeights[relationship.type] || 0) + (relationship.bilateral ? 0.5 : 0)
    ), 0);
    const expectedFactor = Math.round(
      Math.max(-8, Math.min(10, affectionFactor + Math.min(4, relationshipFactor))) * 10,
    ) / 10;
    assert.equal(support.managerNpcId, "6195011151089261734");
    assert.equal(support.factor, expectedFactor);
    assert.equal(assignment.readiness.factors.support, expectedFactor);
    assert(expectedFactor >= -8 && expectedFactor <= 10);
    console.log(JSON.stringify({
      result: "PASS",
      taskType: result.taskType,
      managerSupport: support,
      readinessSupport: assignment.readiness.factors.support,
    }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
