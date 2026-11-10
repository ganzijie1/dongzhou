"use strict";
// One-shot, isolated visitor acceptance against real knowledge, AINPC and orgFlow services.
const assert = require("assert/strict"), fs = require("fs"), path = require("path"), crypto = require("crypto");
let chromium; try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); } catch (_) { ({ chromium } = require("playwright")); }
const BASE = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8787/";
const LABEL = process.env.DONGZHOU_ACCEPTANCE_LABEL || "20261109-diplomacy";
assert(/^[a-z0-9-]+$/.test(LABEL));
const privatePath = path.resolve(__dirname, "../.agentwork/root/diplomacy-acceptance-" + LABEL + "-private.json");
const publicPath = path.resolve(__dirname, "../output/integration-validation/live-diplomacy-acceptance-" + LABEL + ".json");
const executablePath = ["C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find(fs.existsSync);
const resume = process.env.DONGZHOU_RESUME === "1";
if (fs.existsSync(privatePath) && !resume) throw new Error("Acceptance journal exists; inspect it or resume the same task instead of replaying external actions");
const journal = resume && fs.existsSync(privatePath)
  ? JSON.parse(fs.readFileSync(privatePath, "utf8"))
  : { installation: crypto.randomUUID(), stage: "starting", startedAt: new Date().toISOString() };
const resumingTask = Boolean(resume && journal.remoteTask);
const saveJournal = () => { fs.mkdirSync(path.dirname(privatePath), { recursive: true }); fs.writeFileSync(privatePath, JSON.stringify(journal, null, 2)); };
saveJournal();

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const errors = [], requests = { knowledge: 0, decisions: 0, orders: 0, taskReads: 0, saves: 0 };
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.addInitScript((id) => localStorage.setItem("dongzhou-installation-id-v1", id), journal.installation);
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.name));
    page.on("response", (response) => {
      const pathname = new URL(response.url()).pathname, method = response.request().method();
      if (pathname.includes("/knowledge/stages/")) requests.knowledge += 1;
      if (pathname.includes("/decisions")) requests.decisions += 1;
      if (pathname.endsWith("/organization/tasks") && method === "POST") requests.orders += 1;
      if (pathname.includes("/organization/tasks/") && method === "GET") requests.taskReads += 1;
      if (pathname.endsWith("/save") && method === "PUT") requests.saves += 1;
    });
    await page.goto(BASE, { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await page.click("#campaignOfficeButton");
    await page.waitForFunction(() => { const p = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")); return p.organization.backend.orgFlow && p.organization.backend.aiNpc && p.organization.backend.knowledge; }, { timeout: 45000 });
    await page.selectOption("#officeMemberSelect", "ZuoRu");
    let remoteTask = journal.remoteTask || null;
    let terminal = null;
    if (resumingTask) {
      await page.waitForFunction((task) => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.tasks.some((item) => item.remoteResult === task && item.status !== "active"), remoteTask, { timeout: 90000 });
      terminal = await page.evaluate(async (task) => { const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(task)); if (!response.ok) return null; const body = await response.json(); return (body.result?.data || body.result)?.final_result || null; }, remoteTask);
    } else {
      journal.stage = "knowledge"; saveJournal();
      await page.click("#officeStageKnowledgeButton");
      await page.waitForSelector("#officeKnowledgeResults article", { timeout: 90000 });
      journal.stage = "council"; saveJournal();
      await page.click("#officeDecisionForm button[type=submit]");
      await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.length === 1, { timeout: 180000 });
      await page.selectOption("#officeTaskType", "diplomacy");
      await page.locator("#officeUseCouncil").check();
      journal.stage = "orgflow-order"; saveJournal();
      await page.click("#officeIssueButton");
      await page.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.tasks.some((task) => task.type === "diplomacy" && task.remoteResult), { timeout: 90000 });
      remoteTask = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.tasks.find((task) => task.type === "diplomacy").remoteResult);
      journal.remoteTaskCreated = true; journal.remoteTask = remoteTask; journal.stage = "orgflow-acceptance"; saveJournal();
      const acceptedTask = await page.evaluate(async (task) => { const end = Date.now() + 600000; while (Date.now() < end) { const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(task)); if (response.ok) { const body = await response.json(), data = body.result?.data || body.result; if (data?.final_result || data?.execution_started_game_time != null) return data; } await new Promise((resolve) => setTimeout(resolve, 3000)); } return null; }, remoteTask);
      assert(acceptedTask, "real diplomacy task did not enter execution state");
      journal.stage = "orgflow-report"; saveJournal();
      for (let index = 0; index < 2; index += 1) { await page.click("#officeAdvanceButton"); await page.waitForFunction(() => !document.querySelector("#officeAdvanceButton").disabled, { timeout: 90000 }); }
      terminal = await page.evaluate(async (task) => { const end = Date.now() + 600000; while (Date.now() < end) { const response = await fetch("/api/dongzhou/v1/organization/tasks/" + encodeURIComponent(task)); if (response.ok) { const body = await response.json(), data = body.result?.data || body.result; if (data?.final_result) return data.final_result; } await new Promise((resolve) => setTimeout(resolve, 3000)); } return null; }, remoteTask);
      await page.click("#officeAdvanceButton");
      await page.waitForFunction((task) => { const p = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")); return p.organization.tasks.some((item) => item.remoteResult === task && item.status !== "active"); }, remoteTask, { timeout: 90000 });
    }
    assert(["SUCCESS", "PARTIAL", "FAILURE", "REJECTED", "CANCELLED", "INVALIDATED"].includes(terminal), "real diplomacy task did not reach a supported terminal result");
    journal.stage = "lobbying"; saveJournal();
    const negotiations = [
      ["zheng", "互通军情，共御强敌，不索取财货"],
      ["jin", "共享边境预警，彼此守土，不干预内政"],
      ["qi", "开放商旅道路，以军情交换粮道安全"],
      ["chu", "互派斥候传递敌情，盟约限于本回防务"],
      ["qin", "共同防备西戎，双方各守本境，不求质子"]
    ];
    let allianceAccepted = false;
    let acceptedTarget = "";
    const existingDiplomacy = await page.evaluate(() => {
      const profile = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2"));
      const alliance = [...profile.organization.diplomacy.alliances].reverse().find((entry) => entry.status === "broken");
      return { targetId: alliance?.targetId || "", betrayalPending: profile.organization.pendingSupport.some((entry) => entry.id.startsWith("betrayal:")) };
    });
    if (existingDiplomacy.targetId && existingDiplomacy.betrayalPending) {
      allianceAccepted = true;
      acceptedTarget = existingDiplomacy.targetId;
    } else {
      for (const [targetId, proposal] of negotiations) {
        await page.selectOption("#officeDiplomacyTarget", targetId);
        await page.fill("#officeDiplomacyProposal", proposal);
        await page.click("#officeLobbyButton");
        await page.waitForSelector("#officeLobbyButton:disabled", { timeout: 10000 });
        await page.waitForFunction(() => {
          const button = document.querySelector("#officeLobbyButton");
          const text = document.querySelector("#officeDiplomacyResult")?.textContent || "";
          return button && !button.disabled && !text.includes("正在向");
        }, undefined, { timeout: 180000 });
        const lobbyingResult = await page.locator("#officeDiplomacyResult").innerText();
        allianceAccepted = lobbyingResult.includes("可正式缔盟");
        if (allianceAccepted) { acceptedTarget = targetId; break; }
      }
      assert(allianceAccepted, "all five real diplomacy proposals were explicitly rejected or unavailable");
      await page.click("#officeAllianceButton");
      await page.waitForSelector("#officeAllianceLedger >> text=生效");
      await page.click("#officeBetrayButton");
      await page.waitForSelector("#officeAllianceLedger >> text=背盟待战");
    }
    assert(allianceAccepted, "all five real diplomacy proposals were explicitly rejected or unavailable");
    const before = await page.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    assert(before.organization.diplomacy.lobbying.some((entry) => entry.outcome === "accepted"));
    const acceptedAlliance = [...before.organization.diplomacy.alliances].reverse().find((entry) => entry.targetId === acceptedTarget && entry.status === "broken");
    assert(acceptedAlliance, "accepted alliance must be recorded as broken before battle");
    const betrayalSource = `背盟攻${acceptedAlliance.targetName}`;
    assert(before.organization.pendingSupport.some((entry) => entry.id.startsWith("betrayal:")));
    journal.stage = "battle"; saveJournal();
    await page.click("#campaignOfficeCloseButton");
    await page.click("#focusStageButton");
    await page.waitForFunction(() => !!localStorage.getItem("dongzhou-h5-battle-v2"), { timeout: 90000 });
    const accepted = await page.evaluate(() => ({ profile: JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")), battle: JSON.parse(localStorage.getItem("dongzhou-h5-battle-v2")), log: document.querySelector("#battleLog").innerText }));
    const successfulTask = terminal === "SUCCESS" || terminal === "PARTIAL";
    const diplomacyMorale = terminal === "SUCCESS" ? 12 : terminal === "PARTIAL" ? 6 : 0;
    assert.equal(accepted.battle.organizationSupport.sources.includes("折冲诸侯"), successfulTask);
    assert(accepted.battle.organizationSupport.sources.includes(betrayalSource));
    assert.equal(accepted.battle.organizationSupport.alliances[0].targetId, acceptedTarget);
    assert.equal(accepted.battle.organizationSupport.attack, 0.06);
    assert.equal(accepted.battle.organizationSupport.morale, diplomacyMorale - 8);
    assert.equal(accepted.log.includes("折冲诸侯"), successfulTask);
    assert(accepted.log.includes(betrayalSource));
    assert.equal(errors.length, 0);
    if (resumingTask) assert(requests.knowledge === 0 && requests.decisions <= 5 && requests.orders === 0 && requests.taskReads >= 1 && requests.saves >= 1);
    else assert(requests.knowledge >= 1 && requests.decisions >= 2 && requests.decisions <= 6 && requests.orders === 1 && requests.taskReads >= 1 && requests.saves >= 5);
    const result = { result: "PASS", mode: "real-services-browser-no-interception", chain: ["史料", "军议", "外交派差", "NPC游说", "盟约", "背盟战役"], terminalResult: terminal, knowledgeRequests: requests.knowledge, npcDecisions: requests.decisions, organizationOrders: requests.orders, taskReads: requests.taskReads, cloudWrites: requests.saves, allianceBoundToBattle: true, moraleDelta: diplomacyMorale - 8, attackDelta: 0.06 };
    fs.mkdirSync(path.dirname(publicPath), { recursive: true }); fs.writeFileSync(publicPath, JSON.stringify(result, null, 2));
    journal.stage = "complete"; journal.completedAt = new Date().toISOString(); saveJournal();
    console.log(JSON.stringify(result));
  } catch (error) {
    journal.stage = "failed"; journal.errorType = error.name; saveJournal();
    console.error(JSON.stringify({ result: "FAIL", stage: journal.stage, errorType: error.name, details: String(error.message).slice(0, 180) })); process.exitCode = 1;
  } finally { await browser.close(); }
})();
