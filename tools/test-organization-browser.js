"use strict";

const fs = require("fs");
const path = require("path");
let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, "..", "output", "playwright-runtime", "node_modules", "playwright")));
} catch (_) {
  ({ chromium } = require("playwright"));
}

const BASE_URL = process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8780/?offline=1";
const OUT = path.resolve(__dirname, "..", "output", "organization-e2e");
const WEB = path.resolve(__dirname, "..", "web-game");
const BASE_ORIGIN = new URL(BASE_URL).origin;
const SYSTEM_CHROMIUM = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
].find((candidate) => candidate && fs.existsSync(candidate));

async function routeLocalAssets(page) {
  await page.route("**/*", async (route) => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.origin !== BASE_ORIGIN || requestUrl.pathname.startsWith("/api/")) {
      return route.fallback();
    }
    const file = path.resolve(WEB, `.${decodeURIComponent(requestUrl.pathname === "/" ? "/index.html" : requestUrl.pathname)}`);
    if (!file.startsWith(`${WEB}${path.sep}`) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      return route.fulfill({ status: 404, body: "not found" });
    }
    const contentTypes = {
      ".html": "text/html", ".js": "application/javascript", ".css": "text/css",
      ".json": "application/json", ".webp": "image/webp", ".png": "image/png",
      ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav"
    };
    return route.fulfill({
      status: 200,
      contentType: contentTypes[path.extname(file)] || "application/octet-stream",
      body: fs.readFileSync(file)
    });
  });
}

async function openReady(page) {
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
  await page.waitForSelector("#campaignScreen:not([hidden])");
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(SYSTEM_CHROMIUM ? { executablePath: SYSTEM_CHROMIUM } : {})
  });
  const errors = [];
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await routeLocalAssets(desktop);
    desktop.on("pageerror", (error) => errors.push(error.message));
    await openReady(desktop);
    await desktop.click("#campaignOfficeButton");
    await desktop.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await desktop.waitForTimeout(350);
    const desktopLayout = await desktop.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      const viewport = { width: innerWidth, height: innerHeight };
      return { drawer: { left: drawer.left, top: drawer.top, right: drawer.right, bottom: drawer.bottom }, viewport };
    });
    if (desktopLayout.drawer.left < 0 || desktopLayout.drawer.right > desktopLayout.viewport.width || desktopLayout.drawer.top < 0 || desktopLayout.drawer.bottom > desktopLayout.viewport.height + 1) throw new Error(`Desktop organization drawer overflows viewport: ${JSON.stringify(desktopLayout)}`);
    await desktop.fill("#officeKnowledgeQuery", "东郊索命 杜伯");
    await desktop.click("#officeKnowledgeForm button[type=submit]");
    await desktop.waitForSelector("#officeKnowledgeResults article", { timeout: 10000 });
    await desktop.click("#officeStageKnowledgeButton");
    await desktop.waitForSelector("#officeKnowledgeResults article");
    await desktop.click("#officeIssueButton");
    await desktop.waitForSelector("#officeTaskLedger li.active");
    await desktop.screenshot({ path: path.join(OUT, "desktop-office.png"), fullPage: false });

    await desktop.evaluate(() => {
      const key = "dongzhou-h5-profile-v2";
      const profile = JSON.parse(localStorage.getItem(key));
      profile.organization.pendingSupport.push({ id: "e2e-support", stageId: "01", source: "验收筹备", provisions: 18, morale: 7, attack: 0.08, defense: 0.1, recon: 1 });
      localStorage.setItem(key, JSON.stringify(profile));
    });
    await desktop.reload({ waitUntil: "domcontentloaded" });
    await desktop.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await desktop.waitForSelector("#campaignScreen:not([hidden])");
    await desktop.click("#focusStageButton");
    await desktop.waitForSelector("#storyModal:not([hidden])", { timeout: 15000 });
    await desktop.click("#storySkipButton");
    await desktop.waitForSelector("#storyModal", { state: "hidden", timeout: 15000 });
    await desktop.waitForSelector("#battleCanvas:visible", { timeout: 15000 });
    const battleLog = await desktop.locator("#battleLog").innerText();
    if (!battleLog.includes("验收筹备")) throw new Error("Organization support did not reach battle log");

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    await routeLocalAssets(mobile);
    mobile.on("pageerror", (error) => errors.push(error.message));
    await openReady(mobile);
    await mobile.click("#campaignOfficeButton");
    await mobile.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
    await mobile.waitForTimeout(350);
    const mobileLayout = await mobile.evaluate(() => {
      const drawer = document.querySelector("#campaignOfficeDrawer").getBoundingClientRect();
      return { left: drawer.left, right: drawer.right, top: drawer.top, width: innerWidth, scrollWidth: document.documentElement.scrollWidth };
    });
    if (mobileLayout.left < 0 || mobileLayout.right > mobileLayout.width + 1 || mobileLayout.scrollWidth > mobileLayout.width + 1) throw new Error("Mobile organization drawer overflows viewport");
    await mobile.screenshot({ path: path.join(OUT, "mobile-office.png"), fullPage: false });

    const online = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await routeLocalAssets(online);
    online.on("pageerror", (error) => errors.push(error.message));
    let saveVersion = 1;
    let npcStateAttempts = 0;
    let npcMessageTaskId = null;
    let npcCorrespondenceReads = 0;
    let membershipJoined = false;
    let membershipAction = null;
    let orderAttempts = 0;
    let mandateAttempts = 0;
    let organizationTaskReads = 0;
    let savedRemoteTask = false;
    let releaseOrder;
    const orderGate = new Promise((resolve) => { releaseOrder = resolve; });
    await online.route("**/api/dongzhou/v1/**", async (route) => {
      const request = route.request();
      const url = new URL(request.url());
      const pathName = url.pathname;
      let body = {};
      if (pathName.endsWith("/sessions/guest")) body = { playerId: "player-e2e", expiresIn: 86400 };
      else if (pathName.endsWith("/save") && request.method() === "GET") body = { version: saveVersion, payload: {} };
      else if (pathName.endsWith("/save")) {
        const payload = request.postDataJSON().payload;
        if (payload.organization?.tasks?.some((task) => task.remoteResult)) savedRemoteTask = true;
        body = { version: ++saveVersion, payload };
      }
      else if (pathName.endsWith("/integration/status")) body = { mode: "connected", organizationId: "org-e2e", services: { nexusKernel: { online: true, mode: "embedded", version: "0.2.0" }, orgFlow: { online: true }, aiNpc: { online: true }, knowledge: { online: true } } };
      else if (pathName.endsWith("/organization/roster")) body = { organization: { name: "东周军府", state: "ACTIVE", hierarchyVersion: membershipJoined ? 8 : 7, growthContribution: 245 }, members: [{ heroId: "DuBo", office: "司马", role: "军府主官", level: "manager", directManagerHeroId: null, contributionBalance: 54, lifetimeEarned: 80, lifetimeSpent: 26 }, { heroId: "ZuoRu", office: "行人", role: "军府属官", level: "officer", directManagerHeroId: "DuBo", contributionBalance: 31, lifetimeEarned: 42, lifetimeSpent: 11 }], playerMembership: membershipJoined ? { office: "officer_12", role: "court_officer", level: "staff", directManagerHeroId: "DuBo", contributionBalance: 0, lifetimeEarned: 0, lifetimeSpent: 0 } : null, openPositions: membershipJoined ? [] : [{ office: "officer_12", role: "court_officer", level: "staff" }] };
      else if (pathName.endsWith("/knowledge/search")) body = { mode: "connected", results: [{ id: "dongzhou_stage_001", name: "第一回·东郊索命", summary: "杜伯进谏", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }] }] };
      else if (pathName.endsWith("/knowledge/stages/01")) body = { mode: "connected", results: [{ id: "dongzhou_stage_001", name: "第一回·已发布本回史料", summary: "杜伯进谏", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }] }] };
      else if (pathName.endsWith("/npcs/sync")) body = { ready: false, npcs: [{ npcId: "42" }], relogin: [{ npcId: "42", receipt: { accepted: true } }] };
      else if (/\/npcs\/[^/]+\/state$/.test(pathName)) {
        npcStateAttempts += 1;
        if (npcStateAttempts <= 6) return route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "npc_unavailable", message: "NPC state is temporarily unavailable." } }) });
        body = { emotion: { data: { dominant: { emotion_type: "resolute", intensity: 72 } } }, affection: { data: { total: 2 } }, relationships: { data: { total: 3 } }, personality: { available: true, profileId: "profile-zuoru", traits: { stubborn: 79, smooth: 48 }, dominantTraits: ["stubborn", "smooth"], templateSource: "identity", backgroundNote: "fixed profile", updatedAt: "2026-11-07T21:56:40.288000" }, motivation: { available: true, motives: [{ name: "情报核验", score: 35 }], revision: 2, updatedAt: "2026-11-10T08:01:52.476000", threshold: 80 } };
      }
      else if (/\/npcs\/[^/]+\/messages$/.test(pathName)) {
        const input = request.postDataJSON();
        const message = String(input.content || "");
        membershipAction = message.includes("加入组织申请") ? "join" : message.includes("退出东周") ? "confirmLeave" : null;
        if (membershipAction === "join") membershipJoined = true;
        if (membershipAction === "confirmLeave") membershipJoined = false;
        npcMessageTaskId = `playerchat-${input.client_request_id}`;
        body = { state: "ACCEPTED", taskId: npcMessageTaskId };
      }
      else if (/\/npcs\/[^/]+\/correspondence$/.test(pathName)) {
        npcCorrespondenceReads += 1;
        const reply = membershipAction === "join" ? "准你入仕，列入军府属官。" : membershipAction === "confirmLeave" ? "辞仕已办结。" : "北路军粮已经入仓。";
        body = { npcId: "42", messages: npcMessageTaskId && npcCorrespondenceReads > 1 ? [{ messageId: `npc-reply-${npcCorrespondenceReads}`, taskId: npcMessageTaskId, speakerId: "42", speakerName: membershipAction ? "杜伯" : "左儒", targetId: "99", targetName: "主君", targetType: "PLAYER", content: reply, emotion: "calm", digest: "d".repeat(64) }] : [] };
      }
      else if (pathName.includes("/assignments/")) {
        const taskType = pathName.split("/").at(-1);
        const heroId = decodeURIComponent(pathName.split("/").at(-3));
        body = { assignment: { heroId, npcId: "42", runtimeState: "READY", planId: "plan-e2e", generationId: "generation-e2e", eventId: `event-${taskType}`, transactionId: taskType === "supply" ? 9100103 : 9100102, name: taskType === "supply" ? "转运军粮" : "检阅军阵", type: "军务", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 72, affectionCount: 2, relationshipCount: 3 }, personality: { available: true, profileId: "profile-zuoru", traits: { stubborn: 79, smooth: 48 }, dominantTraits: ["stubborn", "smooth"], fit: { available: true, score: 56, band: "steady", factor: 1.2, signals: [{ trait: "stubborn", value: 79, effect: 6.3 }] } }, motivation: { available: true, motives: [{ name: "情报核验", score: 35 }], revision: 2, updatedAt: "2026-11-10T08:01:52.476000", threshold: 80, fit: { available: true, score: 50, band: "neutral", factor: 0, signals: [] } }, managerSupport: { managerNpcId: "41", affection: { type: "respect", value: 50, count: 2 }, relationships: [{ type: "organization", subtype: "superior_subordinate", title: "上级", bilateral: true }], factor: 5.5 }, readiness: { score: 82, band: "steady", factors: { runtime: 6, duty: 7.2, emotion: 0, support: 5.5, personality: 1.2, motivation: 0 } } } };
      }
      else if (/\/npcs\/[^/]+\/schedule$/.test(pathName) && request.method() === "GET") body = { schedule: { data: { schedules: [{ date: "共和元年", events: [{ name: "整饬军粮" }, { name: "巡视营垒" }] }] } } };
      else if (/\/npcs\/[^/]+\/schedule$/.test(pathName)) body = { schedule: { data: { plan_id: "plan-e2e" } } };
      else if (/\/npcs\/[^/]+\/decisions$/.test(pathName)) body = { state: "COMPLETED", decision: { data: { index: 1, type: "OPTION", text: "整军强攻，争取先机" } } };
      else if (pathName.endsWith("/court/mandates")) {
        mandateAttempts += 1;
        const input = request.postDataJSON();
        body = { state: "ISSUED", mandate: { id: `dongzhou:player-e2e:${input.client_request_id}`, stageId: input.stage_id, stageTitle: "东郊索命", heroId: input.hero_id, taskType: input.task_type, evidence: { id: input.knowledge_id, name: "第一回·已发布本回史料", summary: "杜伯进谏", source: { index: input.evidence_source_index, work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" } }, evidenceFit: { taskType: input.task_type, factor: 2, band: "weak", signals: [{ kind: "sourceTier", label: "史实骨架", factor: 2 }] }, council: { requestId: input.council_request_id, index: input.decision_index, text: "整军强攻，争取先机" }, assignment: { heroId: input.hero_id, npcId: "42", runtimeState: "READY", planId: input.schedule_plan_id, generationId: "generation-e2e", eventId: input.schedule_event_id, transactionId: 9100103, name: "转运军粮", type: "军需", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 72, affectionCount: 2, relationshipCount: 3 }, readiness: { score: 82, band: "steady", factors: { runtime: 6, duty: 7.2, emotion: 0, support: 7 } } }, kernel: { module: "dongzhou_runtime", moduleVersion: "1.0.0", nexusKernelVersion: "0.2.0", state: "READY" }, digest: "b".repeat(64), state: "ISSUED" } };
        body.mandate.assignment.personality = { available: true, profileId: "profile-zuoru", traits: { stubborn: 79, smooth: 48 }, dominantTraits: ["stubborn", "smooth"], fit: { available: true, score: 56, band: "steady", factor: 1.2, signals: [{ trait: "stubborn", value: 79, effect: 6.3 }] } };
        body.mandate.assignment.motivation = { available: true, motives: [{ name: "情报核验", score: 35 }], revision: 2, updatedAt: "2026-11-10T08:01:52.476000", threshold: 80, fit: { available: true, score: 50, band: "neutral", factor: 0, signals: [] } };
        body.mandate.assignment.managerSupport = { managerNpcId: "41", affection: { type: "respect", value: 50, count: 2 }, relationships: [{ type: "organization", subtype: "superior_subordinate", title: "上级", bilateral: true }], factor: 5.5 };
        body.mandate.assignment.readiness.factors.personality = 1.2;
        body.mandate.assignment.readiness.factors.motivation = 0;
        body.mandate.emergency = { urgent: true, score: 54.548, interruptTraceId: "itr-browser-emergency", assessedAt: "2026-11-11T04:57:03Z", event: "emergency military report" };
      }
      else if (pathName.endsWith("/organization/tasks")) {
        orderAttempts += 1;
        if (orderAttempts === 2) await orderGate;
        body = orderAttempts === 1
          ? { state: "REJECTED", error: { message: "验收拒单" } }
          : { state: "ACCEPTED", taskId: "00000000-0000-0000-0000-000000000010" };
      }
      else if (/\/organization\/tasks\//.test(pathName)) {
        organizationTaskReads += 1;
        body = organizationTaskReads === 1
          ? { taskId: "00000000-0000-0000-0000-000000000010", result: { data: { task_id: "00000000-0000-0000-0000-000000000010", state: "MEMBER_RESPONSE_PENDING", execution_started_game_time: null, final_result: null, version: "2" } } }
          : { taskId: "00000000-0000-0000-0000-000000000010", npcOutcome: { state: "DELIVERED", attempts: 1, lastError: null }, result: { data: { task_id: "00000000-0000-0000-0000-000000000010", state: "SUCCEEDED", execution_started_game_time: 24306616800, final_result: "SUCCESS", version: "3" } } };
      }
      else return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ error: { code: "not_mocked", message: pathName } }) });
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    });
    const onlineUrl = new URL(BASE_URL);
    onlineUrl.search = "";
    await online.goto(onlineUrl.toString(), { waitUntil: "domcontentloaded" });
    await online.waitForSelector("#app:not([hidden])", { timeout: 45000 });
    await online.click("#campaignOfficeButton");
    await online.waitForSelector("#officeMembers >> text=官署实账");
    await online.waitForFunction(() => !document.querySelector("#officeMembershipApply").disabled && /1 席可申请/.test(document.querySelector("#officeMembershipDetail").textContent));
    await online.click("#officeMembershipApply");
    await online.waitForSelector("#officeMembershipState >> text=已入仕", { timeout: 15000 });
    await online.click("#officeMembershipLeave");
    await online.waitForSelector("#officeMembershipLeaveConfirm:not([hidden])", { timeout: 15000 });
    await online.click("#officeMembershipLeaveConfirm");
    await online.waitForSelector("#officeMembershipState >> text=尚未入仕", { timeout: 15000 });
    if (membershipJoined) throw new Error("Membership leave did not release the reserved position");
    const visibleMembers = await online.locator("#officeMemberSelect option").evaluateAll((options) => options.map((option) => option.value));
    if (!visibleMembers.includes("DuBo")) throw new Error("Organization manager is missing from the inspectable NPC roster");
    await online.selectOption("#officeMemberSelect", "DuBo");
    await online.waitForFunction(() => document.querySelector("#officeIssueButton").disabled && /组织负责人/.test(document.querySelector("#officeOrderHint").textContent));
    await online.waitForSelector("#officeNpcState >> text=属官服务正在恢复", { timeout: 10000 });
    await online.waitForSelector("#officeNpcState >> text=resolute", { timeout: 15000 });
    const assignee = visibleMembers.find((value) => value && value !== "DuBo");
    if (!assignee) throw new Error("No non-manager organization assignee is available");
    await online.selectOption("#officeMemberSelect", assignee);
    await online.waitForSelector("#officeNpcState >> text=resolute", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=情报核验 35", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=固执 79", { timeout: 15000 });
    if (await online.locator("#officeNpcState dt", { hasText: "性情" }).count() !== 1) throw new Error("NPC personality was rendered more than once");
    await online.waitForSelector("#officeNpcAssignment >> text=胜任 82/100", { timeout: 15000 });
    await online.waitForSelector("#officeNpcAssignment >> text=适岗 56/100", { timeout: 15000 });
    await online.waitForSelector("#officeNpcAssignment >> text=意愿 50/100", { timeout: 15000 });
    await online.fill("#officeMessageInput", "北路军粮可曾送到？");
    await online.click("#officeMessageForm button[type=submit]");
    await online.waitForSelector("#officeCorrespondence >> text=北路军粮已经入仓", { timeout: 15000 });
    if (npcStateAttempts < 7) throw new Error("NPC state did not retry after the transient outage");
    await online.fill("#officeKnowledgeQuery", "杜伯");
    await online.click("#officeKnowledgeForm button[type=submit]");
    await online.waitForSelector("#officeKnowledgeResults article");
    await online.click("#officeStageKnowledgeButton");
    await online.waitForSelector("#officeKnowledgeResults >> text=已发布本回史料");
    await online.click('[data-knowledge-id="dongzhou_stage_001"][data-source-index="0"]');
    await online.waitForSelector("#officeKnowledgeResults >> text=已取为据");
    const stageKnowledge = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.knowledge);
    if (!stageKnowledge.some((entry) => entry.id === "dongzhou_stage_001" && entry.stageId === "01")) throw new Error("Published stage knowledge was not saved for preparation");
    await online.click("#officeDecisionForm button[type=submit]");
    await online.waitForSelector("#officeDecisionResult >> text=整军强攻");
    await online.locator("#officeUseCouncil").check();
    const provisionsBeforeOrder = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).campaignResources.provisions);
    await online.click("#officeIssueButton");
    await online.waitForFunction(() => !document.querySelector("#officeIssueButton").disabled);
    const rejectedProfile = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    if (rejectedProfile.campaignResources.provisions !== provisionsBeforeOrder || rejectedProfile.organization.tasks.length) throw new Error("Rejected order consumed resources or created a local task");
    await online.evaluate(() => {
      const button = document.querySelector("#officeIssueButton");
      button.click();
      button.click();
    });
    // Change the organization while the accepted order is still in flight.
    await online.click("#officeAdvanceButton");
    await online.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.month === 2);
    releaseOrder();
    await online.waitForSelector("#officeTaskLedger li.active");
    if (!/胜任82/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed AINPC readiness is missing from the task ledger");
    if (!/适岗56/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed AINPC personality fit is missing from the task ledger");
    if (!/意愿50/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed AINPC task willingness is missing from the task ledger");
    if (!/协同\+5\.5/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed manager relationship support is missing from the task ledger");
    if (!/史证2\/9/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed evidence fit is missing from the task ledger");
    if (!/54\.548/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Sealed AINPC emergency assessment is missing from the task ledger");
    const afterConcurrentOrder = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    if (afterConcurrentOrder.organization.month !== 2) throw new Error(`Accepted order rolled back a concurrent month advance: ${afterConcurrentOrder.organization.month}`);
    if (afterConcurrentOrder.campaignResources.provisions !== provisionsBeforeOrder - afterConcurrentOrder.organization.tasks[0].cost) throw new Error("Accepted order did not charge exactly once");
    if (orderAttempts !== 2) throw new Error("Repeated click created duplicate remote orders");
    if (mandateAttempts !== 2) throw new Error("Rejected order retry did not reuse the Nexus mandate request exactly once");
    await online.click("#officeAdvanceButton");
    await online.waitForSelector("#officeTaskLedger li.success");
    await online.waitForSelector("#officeTaskLedger >> text=经历已形成");
    const taskNameWidth = await online.locator("#officeTaskLedger li.success > span").evaluate((element) => element.getBoundingClientRect().width);
    if (taskNameWidth < 100) throw new Error(`Task ledger name column collapsed to ${taskNameWidth}px`);
    if (organizationTaskReads < 2) throw new Error("A pending organization task was not polled within the same month advance");
    if (!savedRemoteTask) throw new Error("Remote task binding was not persisted");
    await online.screenshot({ path: path.join(OUT, "desktop-office-online.png"), fullPage: false });
    if (errors.length) throw new Error(`Page errors: ${errors.join(" | ")}`);
    console.log(JSON.stringify({ result: "PASS", desktopLayout, mobileLayout, screenshots: OUT }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
