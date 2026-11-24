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
    let offlineApiRequests = 0;
    desktop.on("request", (request) => {
      if (new URL(request.url()).pathname.startsWith("/api/")) offlineApiRequests += 1;
    });
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
    await desktop.click("#officeKnowledgeResults .office-source-choice:not(:disabled)");
    await desktop.click("#officeStageKnowledgeButton");
    await desktop.waitForSelector("#officeKnowledgeResults article");
    await desktop.waitForSelector("#officeCommendButton:not(:disabled)");
    await desktop.click("#officeCommendButton");
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.commendations.length === 1);
    await desktop.waitForSelector("#officeRecollectionButton:not(:disabled)");
    await desktop.click("#officeRecollectionButton");
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.recollections.length === 1);
    const localNpcHistory = await desktop.evaluate(() => {
      const organization = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization;
      return { commendation: organization.commendations[0], recollection: organization.recollections[0] };
    });
    if (localNpcHistory.commendation.kernel?.module !== "dongzhou_npc_commendation"
      || localNpcHistory.commendation.kernel?.moduleVersion !== "1.1.0"
      || Object.keys(localNpcHistory.commendation.sourceProvenance?.services || {}).length !== 4) {
      throw new Error("Offline commendation lacks the four-repository Nexus seal");
    }
    if (localNpcHistory.recollection.kernel?.module !== "dongzhou_npc_recollection"
      || localNpcHistory.recollection.kernel?.moduleVersion !== "1.2.0"
      || localNpcHistory.recollection.memoryReceipt?.digest !== localNpcHistory.recollection.memoryDigest) {
      throw new Error("Offline recollection lacks the sealed local AINPC memory");
    }
    await desktop.waitForSelector("#officeLogisticsBriefing:not(:disabled)");
    await desktop.click("#officeLogisticsBriefing");
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.logisticsBriefings.length === 1);
    await desktop.waitForSelector("#officeThoughtButton:not(:disabled)");
    await desktop.click("#officeThoughtButton");
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.thoughts.length === 1);
    await desktop.click("#officeDecisionForm button[type=submit]");
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.councils.length === 1);
    const localCouncil = await desktop.evaluate(() => {
      const organization = JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization;
      return { council: organization.councils[0], thought: organization.thoughts[0], briefing: organization.logisticsBriefings[0] };
    });
    if (!localCouncil.council.thought?.digest || localCouncil.council.thought.digest !== localCouncil.thought.digest
      || localCouncil.council.text !== localCouncil.thought.councilProposal) {
      throw new Error("Offline council did not bind the local AINPC thought");
    }
    if (localCouncil.briefing.kernel?.module !== "dongzhou_logistics_briefing"
      || localCouncil.briefing.kernel?.moduleVersion !== "1.1.0"
      || localCouncil.briefing.ainpcDelivery?.mode !== "IN_PROCESS"
      || localCouncil.thought.logisticsBriefing?.digest !== localCouncil.briefing.digest) {
      throw new Error("Offline thought did not bind the sealed local logistics briefing");
    }
    await desktop.click("#officeQuizStart");
    await desktop.waitForSelector("[data-quiz-answer]");
    const stagePeople = new Set(["周宣王", "伯阳父", "乡民", "杜伯", "左儒", "尹吉甫"]);
    const quizOptions = await desktop.locator("[data-quiz-answer]").allTextContents();
    const correctQuizIndex = quizOptions.findIndex((text) => [...stagePeople].some((name) => text.includes(name)));
    if (correctQuizIndex < 0) throw new Error(`Offline knowledge quiz has no stage-bound answer: ${JSON.stringify(quizOptions)}`);
    await desktop.click(`[data-quiz-answer="${correctQuizIndex}"]`);
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).knowledgeQuiz.score === 10);
    await desktop.click("#officeQuizVerify");
    await desktop.waitForFunction(() => document.querySelector("#officeQuizSealStatus")?.textContent.trim().length > 0);
    await desktop.fill("#officeAdviserQuestion", "杜伯在哪里");
    await desktop.click("#officeAdviserForm button[type=submit]");
    await desktop.waitForSelector("#officeAdviserAnswer >> text=杜伯", { timeout: 10000 });
    await desktop.waitForSelector('[data-adviser-guide="ACCEPT"]:not([hidden])');
    const localAdviser = await desktop.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")));
    if (localAdviser.result.state !== "ANSWERED" || localAdviser.result.intentType !== "location") throw new Error("Offline adviser did not answer from the local AINPC contract");
    if (localAdviser.result.adviser?.heroId !== "DuBo" || localAdviser.result.adviser?.organization !== "列国军府") throw new Error("Offline adviser did not bind the local organization authority");
    if (Object.keys(localAdviser.result.sourceProvenance?.services || {}).length !== 4) throw new Error("Offline adviser did not bind all four source repositories");
    await desktop.click('[data-adviser-guide="ACCEPT"]');
    await desktop.waitForSelector("#officeAdviserGuideStatus >> text=引路已经完成", { timeout: 10000 });
    const completedGuide = await desktop.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-adviser-question-v1")).guideDecision.result.guide);
    if (completedGuide.kernel?.module !== "dongzhou_adviser_guide" || completedGuide.kernel?.moduleVersion !== "1.1.0" || completedGuide.kernel?.state !== "SEALED") throw new Error("Offline adviser guide lacks the Nexus seal");
    await desktop.click('[data-adviser-rating="accurate"]');
    await desktop.waitForSelector("#officeAdviserAnswer >> text=已记下评价：准确");
    if (offlineApiRequests !== 0) throw new Error(`Offline knowledge/NPC/adviser flow made ${offlineApiRequests} API requests`);
    await desktop.waitForSelector('[data-adviser-route]:not([hidden]) >> text=查看关卡入口');
    await desktop.click("[data-adviser-route]");
    await desktop.waitForSelector("#campaignOfficeBackdrop", { state: "hidden" });
    if (await desktop.locator("#focusStageButton").getAttribute("data-stage-id") !== "01") throw new Error("Offline adviser did not hand off to the source-bound stage");
    await desktop.click("#campaignOfficeButton");
    await desktop.waitForSelector("#campaignOfficeBackdrop:not([hidden])");
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
    let npcSyncAttempts = 0;
    const npcSyncRequests = [];
    let npcMessageTaskId = null;
    let npcCorrespondenceReads = 0;
    let membershipJoined = false;
    let membershipAction = null;
    let careerAction = null;
    let careerSettled = false;
    const careerActions = [];
    let orderAttempts = 0;
    let mandateAttempts = 0;
    let organizationTaskReads = 0;
    let sourceDrift = false;
    let scheduledDutyState = "ACTIVE";
    let scheduledDutyVersion = 1;
    const scheduledDutyActions = [];
    let savedRemoteTask = false;
    let releaseOrder;
    const orderGate = new Promise((resolve) => { releaseOrder = resolve; });
    const sourceProvenance = {
      digest: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      services: { knowledge: {}, aiNpc: {}, orgFlow: {}, nexusKernel: {} },
      kernel: { module: "dongzhou_service_provenance", state: "SEALED" }
    };
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
      else if (pathName.endsWith("/integration/status")) body = { mode: "connected", organizationId: "org-e2e", services: { nexusKernel: { online: true, mode: "embedded", version: "0.2.0", requiredModuleCount: 22, operationalModuleCount: 22, sourceBoundModuleCount: 20, sourceBoundModules: Array.from({ length: 20 }, (_, index) => `source-bound-${index + 1}`), unavailableModules: [], sourceAttested: true, sourceBranch: "develop", sourceRevision: "190abb1fa889e40aa08dbc6efaaba6fe4940ca6d", integrationRevision: "4f1915b45eadf8608308f7131173d1d60f6c5270", sourceSealDigest: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" }, orgFlow: { online: true, sourceBranch: "develop", sourceRevision: "8b1049e965719d31c51772dde799737e9b92e918", integrationRevision: "fbfc803b264c2c1e1dffe80c8da1bb5caa676cc3" }, aiNpc: { online: true, sourceBranch: "develop", sourceRevision: "82b7a7e02bccceb283563cee9929e29610d6ebf5", integrationRevision: "f2235369e1da5e1e64aa2969ce29bef553f03ee3" }, knowledge: { online: true, sourceBranch: "main", sourceRevision: "45afa2ffe77faea0622e8d3ed3f2b69c0cab9c56", integrationRevision: "5fd67de575113b3f1238149d971106c97eed5c9a" } } };
      else if (pathName.endsWith("/court/mandates/pending")) body = { pending: null };
      else if (pathName.endsWith("/organization/roster")) body = { organization: { name: "东周军府", state: "ACTIVE", templateId: "dongzhou_court", templateVersion: 7, hierarchyVersion: membershipJoined ? 8 : 7, growthContribution: 245 }, members: [{ heroId: "DuBo", office: "军府主官", role: "军府主官", level: "manager", directManagerHeroId: null, contributionBalance: 54, lifetimeEarned: 80, lifetimeSpent: 26 }, { heroId: "ZuoRu", office: "军府属官·第1席", role: "军府属官", level: "officer", directManagerHeroId: "DuBo", contributionBalance: 31, lifetimeEarned: 42, lifetimeSpent: 11 }], playerMembership: membershipJoined ? { office: "军府属官·第12席", role: "军府属官", level: "staff", directManagerHeroId: "DuBo", contributionBalance: 0, lifetimeEarned: 0, lifetimeSpent: 0 } : null, openPositions: membershipJoined ? [] : [{ office: "军府属官·第12席", role: "军府属官", level: "staff" }] };
      else if (pathName.endsWith("/organization/scheduled-duties/status")) {
        const input = request.postDataJSON();
        scheduledDutyState = input.enabled ? "ACTIVE" : "DISABLED";
        scheduledDutyVersion += 1;
        scheduledDutyActions.push(input);
        body = { state: scheduledDutyState, version: scheduledDutyVersion, activeTask: { taskId: "00000000-0000-4000-8000-000000000099", title: "东周朝廷月例察访", state: "IN_PROGRESS" }, sourceProvenance, receipt: { kind: "STATUS_CHANGE", digest: "5".repeat(64), sourceProvenance, kernel: { module: "dongzhou_organization_scheduled_duty", moduleVersion: "1.2.0", state: "SEALED" } } };
      }
      else if (pathName.endsWith("/organization/scheduled-duties")) body = { ruleId: "00000000-0000-4000-8000-000000000098", state: scheduledDutyState, version: scheduledDutyVersion, frequency: "DAILY", triggerMinute: 780, managerHeroId: "DuBo", workerHeroId: "ZuoRu", taskCode: "dongzhou.intelligence", latestTrigger: { state: "SKIPPED", failure_code: "duplicate_active_task", task_id: "00000000-0000-4000-8000-000000000099" }, activeTask: { taskId: "00000000-0000-4000-8000-000000000099", title: "东周朝廷月例察访", state: "IN_PROGRESS", adopted: false }, sourceProvenance, receipt: { kind: "SNAPSHOT", ruleId: "00000000-0000-4000-8000-000000000098", state: scheduledDutyState, version: scheduledDutyVersion, latestTriggerTaskId: "00000000-0000-4000-8000-000000000099", activeTaskId: "00000000-0000-4000-8000-000000000099", activeTaskAdopted: false, sourceProvenance, digest: "4".repeat(64), kernel: { module: "dongzhou_organization_scheduled_duty", moduleVersion: "1.2.0", state: "SEALED" } } };
      else if (pathName.endsWith("/organization/player-tasks")) {
        const hasException = careerAction === "exception";
        body = !careerAction ? { items: [], hasMore: false } : { items: [{
          taskId: "00000000-0000-4000-8000-000000000081",
          title: "核验军粮账册",
          state: careerAction === "supplement" ? "SUCCEEDED" : careerAction === "result" ? "SUPPLEMENT_PENDING" : careerAction === "reject" ? "REJECTED" : ["accept", "exception"].includes(careerAction) ? "IN_PROGRESS" : "MEMBER_RESPONSE_PENDING",
          version: hasException ? 8 : 7,
          updatedAt: "2026-11-14T10:05:00Z",
          executionException: hasException ? {
            exceptionId: "00000000-0000-4000-8000-000000000082",
            code: "road_destroyed",
            summary: "北路桥梁冲毁，军粮车队无法通行。",
            state: "ACCEPTED",
            defaultPlanId: "reroute-west-post-road",
            selectedPlanId: "reroute-west-post-road",
            plans: [{ id: "reroute-west-post-road", title: "改走西驿道", description: "拆分车队，经西驿道绕行并补派斥候护送。" }],
            resolutionSource: "NPC_CONFIRMATION",
            resumedGameTime: "24306616800",
            resolvedAt: "2026-11-14T10:05:00Z",
            version: 2
          } : null,
          organizationTrace: {
            state: "SEALED",
            taskId: "00000000-0000-4000-8000-000000000081",
            taskState: careerAction === "supplement" ? "SUCCEEDED" : careerAction === "result" ? "SUPPLEMENT_PENDING" : careerAction === "reject" ? "REJECTED" : ["accept", "exception"].includes(careerAction) ? "IN_PROGRESS" : "MEMBER_RESPONSE_PENDING",
            taskVersion: hasException ? "8" : "7",
            activeConfirmations: careerAction === "result" ? [{
              caseId: "00000000-0000-4000-8000-000000000084",
              type: "TASK_SUPPLEMENT_REQUEST",
              state: "WAITING_CONFIRMATION",
              recipientType: "PLAYER",
              allowedActions: ["submit_supplement"]
            }] : [],
            supplementRequest: careerAction === "result" ? {
              reviewCaseId: "00000000-0000-4000-8000-000000000085",
              supplementCaseId: "00000000-0000-4000-8000-000000000084",
              reasonCode: "other",
              reasonDetail: "请补齐西仓封识清单十二项。"
            } : null,
            executionException: hasException ? {
              exceptionId: "00000000-0000-4000-8000-000000000082",
              code: "road_destroyed",
              summary: "北路桥梁冲毁，军粮车队无法通行。",
              state: "ACCEPTED",
              defaultPlanId: "reroute-west-post-road",
              selectedPlanId: "reroute-west-post-road",
              plans: [{ id: "reroute-west-post-road", title: "改走西驿道", description: "拆分车队，经西驿道绕行并补派斥候护送。" }]
            } : null,
            timeline: [
              { sequence: 1, type: "TASK_CREATED", occurredAt: "2026-11-14T09:40:00Z", stateCode: "GENERATED" },
              { sequence: 2, type: "EXECUTION_STARTED", occurredAt: "2026-11-14T09:50:00Z", stateCode: "IN_PROGRESS" },
              ...(careerAction === "result" ? [
                { sequence: 3, type: "SUBMISSION_RECORDED", occurredAt: "2026-11-14T10:02:00Z", stateCode: "SUBMISSION_PENDING" },
                { sequence: 4, type: "SUPPLEMENT_REQUESTED", occurredAt: "2026-11-14T10:03:00Z", stateCode: "SUPPLEMENT_PENDING" }
              ] : []),
              ...(hasException ? [
                { sequence: 3, type: "EXECUTION_EXCEPTION_REPORTED", occurredAt: "2026-11-14T10:00:00Z", stateCode: "OPEN" },
                { sequence: 4, type: "EXECUTION_EXCEPTION_RESOLVED", occurredAt: "2026-11-14T10:05:00Z", stateCode: "ACCEPTED" }
              ] : [])
            ],
            digest: "8".repeat(64),
            kernel: { module: "dongzhou_organization_task_trace", state: "SEALED" }
          }
        }], hasMore: false };
        if (["accept", "exception", "result", "supplement"].includes(careerAction)) body.items.push({
          taskId: "00000000-0000-4000-8000-000000000083",
          title: "巡核西仓封识",
          state: "IN_PROGRESS",
          version: 3,
          updatedAt: "2026-11-14T09:55:00Z",
          executionException: null,
          organizationTrace: {
            state: "SEALED",
            taskId: "00000000-0000-4000-8000-000000000083",
            taskState: "IN_PROGRESS",
            taskVersion: "3",
            executionException: null,
            timeline: [
              { sequence: 1, type: "TASK_CREATED", occurredAt: "2026-11-14T09:45:00Z", stateCode: "GENERATED" },
              { sequence: 2, type: "EXECUTION_STARTED", occurredAt: "2026-11-14T09:55:00Z", stateCode: "IN_PROGRESS" }
            ],
            digest: "6".repeat(64),
            kernel: { module: "dongzhou_organization_task_trace", state: "SEALED" }
          }
        });
      }
      else if (/\/organization\/player-contributions\/[0-9a-f-]+\/dossier$/i.test(pathName)) {
        body = { dossier: {
          state: "SEALED",
          organizationId: "org-e2e",
          memberId: "player-member-e2e",
          heroId: "PLAYER",
          entryId: "00000000-0000-4000-8000-000000000091",
          eventCode: "TASK_COMPLETED",
          amount: 20,
          taskId: "00000000-0000-4000-8000-000000000081",
          taskState: "SUCCEEDED",
          contribution: { digest: "9".repeat(64), sourceProvenance },
          taskTrace: { sourceProvenance, timeline: [{ type: "TASK_CREATED" }, { type: "EXECUTION_STARTED" }, { type: "TASK_FINALIZED" }, { type: "SETTLEMENT_RECORDED" }], kernel: { module: "dongzhou_organization_task_trace", moduleVersion: "1.1.0", state: "SEALED" } },
          sourceProvenance,
          digest: "7".repeat(64),
          kernel: { module: "dongzhou_organization_contribution_dossier", moduleVersion: "1.1.0", state: "SEALED" }
        } };
      }
      else if (pathName.endsWith("/organization/player-contributions")) {
        const settled = careerSettled;
        body = {
          heroId: "PLAYER",
          memberId: "player-member-e2e",
          account: { accountVersion: settled ? 2 : 1, accountBalance: settled ? 20 : 0, lifetimeEarned: settled ? 20 : 0, lifetimeSpent: 0 },
          entries: settled ? [{
            organizationId: "org-e2e",
            memberId: "player-member-e2e",
            heroId: "PLAYER",
            entryId: "00000000-0000-4000-8000-000000000091",
            entryVersion: 2,
            amount: 20,
            balanceAfter: 20,
            lifetimeEarnedAfter: 20,
            lifetimeSpentAfter: 0,
            eventCode: "TASK_COMPLETED",
            sourceRef: "organization-task:00000000-0000-4000-8000-000000000081",
            violationId: null,
            ruleSetId: "organization.default",
            ruleSetVersion: 1,
            sourceProvenance,
            digest: "9".repeat(64),
            kernel: { module: "dongzhou_organization_contribution_ledger", moduleVersion: "1.1.0", state: "SEALED" }
          }] : [],
          nextBeforeVersion: null
        };
      }
      else if (pathName.endsWith("/knowledge/search")) body = { mode: "connected", searchReceipt: { id: "search-browser", digest: "4".repeat(64), sourceProvenance }, results: [{ id: "dongzhou_stage_001", name: "第一回·东郊索命", summary: "杜伯进谏", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }], retrieval: { aggregateScore: 0.8, strongestChannel: "graph", graphRelated: true, channels: [{ channel: "graph", score: 1, normalizedScore: 1, rank: 1 }] }, searchReceipt: { id: "search-browser", digest: "4".repeat(64) } }] };
      else if (pathName.endsWith("/knowledge/stages/01")) body = { mode: "connected", results: [{ id: "dongzhou_stage_001", name: "第一回·已发布本回史料", summary: "杜伯进谏", stageId: "01", sourceDetails: [{ work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" }] }] };
      else if (pathName.endsWith("/npcs/sync")) {
        npcSyncAttempts += 1;
        npcSyncRequests.push(request.postDataJSON());
        body = { ready: npcSyncAttempts > 1, npcs: [{ npcId: "42" }], relogin: [{ npcId: "42", receipt: { accepted: true } }] };
      }
      else if (/\/npcs\/[^/]+\/state$/.test(pathName)) {
        npcStateAttempts += 1;
        if (npcStateAttempts <= 6) return route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { code: "npc_unavailable", message: "NPC state is temporarily unavailable." } }) });
        const isManager = pathName.includes("/npcs/DuBo/");
        body = { aiPlayerId: "player-ai-e2e", knownNpcIds: { DuBo: "npc-dubo", ZuoRu: "npc-zuoru" }, emotion: { data: { dominant: { emotion_type: "resolute", intensity: 72 } } }, affection: { data: { total: 2, items: [{ target_id: "player-ai-e2e", dominant_affection_type: "respect", max_value: 68 }, { target_id: "historical-player", dominant_affection_type: "trust", max_value: 41 }] } }, relationships: { data: { total: 3, items: [{ target_id: "npc-dubo", relation_type: "organization", relation_sub: "superior_subordinate", is_bilateral: true, is_active: true }] } }, personality: { available: true, profileId: "profile-zuoru", traits: { stubborn: 79, smooth: 48 }, dominantTraits: ["stubborn", "smooth"], templateSource: "identity", backgroundNote: "fixed profile", updatedAt: "2026-11-07T21:56:40.288000" }, motivation: { available: true, motives: [{ name: "情报核验", score: 35 }], revision: 2, updatedAt: "2026-11-10T08:01:52.476000", threshold: 80 }, execution: isManager ? { available: true, running: false, paused: false, outcome: "unconfirmed", scheduleName: "校核军令" } : { available: true, running: true, paused: false, waitingForReport: true, scheduleName: "巡核军粮", currentActionIndex: 1, totalActions: 3 } };
      }
      else if (/\/npcs\/[^/]+\/messages$/.test(pathName)) {
        const input = request.postDataJSON();
        const message = String(input.content || "");
        membershipAction = message.includes("加入组织申请") ? "join" : message.includes("我确认退出") ? "confirmLeave" : null;
        if (membershipAction === "join" && !message.includes("「军府属官·第12席」岗位")) {
          throw new Error(`Membership request did not bind the formal position name: ${message}`);
        }
        careerAction = message.includes("可以领取的组织任务") ? "options"
          : message.includes("申请领取组织任务：") ? "request"
          : message.includes("任务和待办事项") ? "inbox"
          : message.includes("申请调整你刚才下发") ? "modify"
          : message.includes("拒绝你刚才下发") ? "reject"
          : message.includes("接受你刚才下发") ? "accept"
          : message.includes("重大异常") ? "exception"
          : message.includes("按退回要求提交当前组织任务的补充成果") ? "supplement"
          : message.includes("完成当前组织任务") ? "result"
          : null;
        if (careerAction) careerActions.push({ action: careerAction, message });
        if (careerAction === "supplement") careerSettled = true;
        if (membershipAction === "join") membershipJoined = true;
        if (membershipAction === "confirmLeave") membershipJoined = false;
        npcMessageTaskId = `playerchat-${input.client_request_id}`;
        body = { state: "ACCEPTED", taskId: npcMessageTaskId };
      }
      else if (/\/npcs\/[^/]+\/correspondence$/.test(pathName)) {
        npcCorrespondenceReads += 1;
        const careerReplies = {
          options: "你当前岗位可以向我申请的组织任务有：一、核验军粮账册。",
          request: "核验军粮账册已经派发给你，请明确回复是否接受。",
          inbox: "已有一项核验军粮账册任务等待你处理。",
          modify: "核验军粮账册的改令申请已经登记，等待主官裁定。",
          reject: "已记录拒绝，核验军粮账册将另行安排。",
          accept: "已记录受命，核验军粮账册开始执行。",
          exception: "受阻已经登记，差事暂停；请从冻结方案中等待直属裁定。",
          result: "复命已核验，尚缺西仓封识清单，请按退回要求补呈。",
          supplement: "补呈已收纳，复核通过，贡献已经结算。"
        };
        const reply = membershipAction === "join" ? "准你入仕，列入军府属官。" : membershipAction === "confirmLeave" ? "辞仕已办结。" : careerReplies[careerAction] || "北路军粮已经入仓。";
        body = { npcId: "42", messages: npcMessageTaskId && npcCorrespondenceReads > 1 ? [{ messageId: `npc-reply-${npcCorrespondenceReads}`, taskId: npcMessageTaskId, speakerId: "42", speakerName: membershipAction ? "杜伯" : "左儒", targetId: "99", targetName: "主君", targetType: "PLAYER", content: reply, emotion: "calm", digest: "d".repeat(64) }] : [] };
      }
      else if (pathName.includes("/assignments/")) {
        const taskType = pathName.split("/").at(-1);
        const heroId = decodeURIComponent(pathName.split("/").at(-3));
        body = { assignment: { heroId, npcId: "42", runtimeState: "READY", planId: "plan-e2e", generationId: "generation-e2e", eventId: `event-${taskType}`, transactionId: taskType === "supply" ? 9100103 : 9100102, name: taskType === "supply" ? "转运军粮" : "检阅军阵", type: "军务", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 72, affectionCount: 2, relationshipCount: 3 }, personality: { available: true, profileId: "profile-zuoru", traits: { stubborn: 79, smooth: 48 }, dominantTraits: ["stubborn", "smooth"], fit: { available: true, score: 56, band: "steady", factor: 1.2, signals: [{ trait: "stubborn", value: 79, effect: 6.3 }] } }, motivation: { available: true, motives: [{ name: "情报核验", score: 35 }], revision: 2, updatedAt: "2026-11-10T08:01:52.476000", threshold: 80, fit: { available: true, score: 50, band: "neutral", factor: 0, signals: [] } }, managerSupport: { managerNpcId: "41", affection: { type: "respect", value: 50, count: 2 }, relationships: [{ type: "organization", subtype: "superior_subordinate", title: "上级", bilateral: true }], factor: 5.5 }, readiness: { score: 82, band: "steady", factors: { runtime: 6, duty: 7.2, emotion: 0, support: 5.5, personality: 1.2, motivation: 0 } } } };
      }
      else if (/\/npcs\/[^/]+\/schedule$/.test(pathName) && request.method() === "GET") body = { schedule: { data: { schedules: [{ date: "共和元年", events: [{ name: "整饬军粮" }, { name: "巡视营垒" }] }] } }, runtime: { available: true, degraded: false, loaded: true, online: true, currentGameTime: "0772-10-22T14:00:00", activeWindow: { status: "active", start: "0772-10-22T14:00:00", end: "0772-10-22T22:00:00" }, running: { id: "running-1", name: "休息", type: "休息" }, pending: [{ id: "pending-1", name: "检阅军阵", type: "军事" }, { id: "pending-2", name: "议定军令", type: "军事" }], suspended: [], counts: { pending: 2, suspended: 0, completed: 0, discarded: 0 } } };
      else if (/\/npcs\/[^/]+\/schedule$/.test(pathName)) body = { schedule: { data: { plan_id: "plan-e2e" } } };
      else if (pathName.includes("/court/mandates/") && pathName.endsWith("/schedule")) { const input = request.postDataJSON(); const mandateId = decodeURIComponent(pathName.split("/").at(-2)); body = { state: "COMPLETED", scheduleReceipt: { requestId: input.client_request_id, mandateId, mandateDigest: input.mandate_digest, heroId: "ZuoRu", npcId: "42", eventId: `dongzhou-mandate-${input.mandate_digest.slice(0, 32)}`, action: "insert_today", scheduleId: `dongzhou-mandate-${input.mandate_digest.slice(0, 32)}`, scheduleName: "临时军令", duplicate: false, reason: null, appliedAt: "0771-01-01 14:00:00", digest: "d".repeat(64), sourceProvenance } }; }
      else if (/\/npcs\/[^/]+\/decisions$/.test(pathName)) body = { state: "COMPLETED", decision: { data: { index: 1, type: "OPTION", text: "整军强攻，争取先机" } }, sourceProvenance };
      else if (pathName.endsWith("/court/mandates")) {
        mandateAttempts += 1;
        const input = request.postDataJSON();
        if (input.schedule_plan_id !== "plan-e2e") throw new Error("Nexus mandate did not retain the authoritative AINPC schedule plan ID");
        body = { state: "ISSUED", mandate: { id: `dongzhou:player-e2e:${input.client_request_id}`, stageId: input.stage_id, stageTitle: "东郊索命", heroId: input.hero_id, taskType: input.task_type, evidence: { id: input.knowledge_id, name: "第一回·已发布本回史料", summary: "杜伯进谏", source: { index: input.evidence_source_index, work: "《史记·周本纪》", tier: "史实骨架", scope: "千亩之败", url: "https://ctext.org/shiji/zhou-ben-ji" } }, evidenceFit: { taskType: input.task_type, factor: 2, band: "weak", signals: [{ kind: "sourceTier", label: "史实骨架", factor: 2 }] }, council: { requestId: input.council_request_id, index: input.decision_index, text: "整军强攻，争取先机", sourceProvenance }, assignment: { heroId: input.hero_id, npcId: "42", runtimeState: "READY", planId: input.schedule_plan_id, generationId: "generation-e2e", eventId: input.schedule_event_id, transactionId: 9100103, name: "转运军粮", type: "军需", date: "0772-10-22", day: 1, stageRange: { start: 1, end: 20 }, timeSlot: "", importance: 90, state: { emotion: "resolute", intensity: 72, affectionCount: 2, relationshipCount: 3 }, readiness: { score: 82, band: "steady", factors: { runtime: 6, duty: 7.2, emotion: 0, support: 7 } } }, sourceProvenance, kernel: { module: "dongzhou_runtime", moduleVersion: "1.0.0", nexusKernelVersion: "0.2.0", state: "READY" }, digest: "b".repeat(64), state: "ISSUED" } };
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
          : { state: "ACCEPTED", taskId: "00000000-0000-0000-0000-000000000010", sourceProvenance };
      }
      else if (/\/organization\/tasks\//.test(pathName)) {
        organizationTaskReads += 1;
        body = organizationTaskReads === 1
          ? { taskId: "00000000-0000-0000-0000-000000000010", sourceProvenance, result: { data: { task_id: "00000000-0000-0000-0000-000000000010", state: "MEMBER_RESPONSE_PENDING", execution_started_game_time: null, final_result: null, version: "2" } } }
          : { taskId: "00000000-0000-0000-0000-000000000010", sourceProvenance, npcOutcome: { state: "DELIVERED", attempts: 1, lastError: null, receipt: { state: "SEALED", digest: "a".repeat(64), sourceProvenance, kernel: { module: "dongzhou_npc_settlement", moduleVersion: "1.2.0", state: "SEALED" } } }, result: { data: { task_id: "00000000-0000-0000-0000-000000000010", state: "SUCCEEDED", execution_started_game_time: 24306616800, final_result: "SUCCESS", version: "3" } } };
      }
      else return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ error: { code: "not_mocked", message: pathName } }) });
      if (pathName.endsWith("/integration/status")) {
        for (const service of Object.values(body.services)) service.sourceAttested = true;
      }
      if (sourceDrift && pathName.endsWith("/integration/status")) {
        body.services.aiNpc = { ...body.services.aiNpc, online: false, sourceAttested: false, reportedSourceBranch: "develop", reportedSourceRevision: "0".repeat(40), reason: "source_attestation_failed" };
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    });
    const onlineUrl = new URL(BASE_URL);
    onlineUrl.search = "";
    await online.goto(onlineUrl.toString(), { waitUntil: "domcontentloaded" });
    await online.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await online.click("#campaignOfficeButton");
    await online.waitForSelector("#officeServiceStatus >> text=内核 22/22 · 验源 20/20通达", { timeout: 15000 });
    const sourceBoundStatus = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.backend);
    if (sourceBoundStatus.nexusSourceBoundModules !== 20 || new Set(sourceBoundStatus.nexusSourceBoundModuleNames).size !== 20) throw new Error("Nexus source-bound module coverage was not persisted");
    for (const revision of ["190abb1", "8b1049e", "82b7a7e", "45afa2f"]) {
      await online.waitForSelector(`#officeServiceStatus >> text=${revision}`, { timeout: 15000 });
    }
    await online.waitForSelector("#officeServiceStatus >> text=版本封印0123456", { timeout: 15000 });
    const serviceTitle = await online.locator("#officeServiceStatus span").first().getAttribute("title");
    if (!serviceTitle.includes("Dongzhou 4f1915b45eadf8608308f7131173d1d60f6c5270")) throw new Error(`Missing service provenance tooltip: ${serviceTitle}`);
    await online.waitForSelector("#officeRosterSummary >> text=模板 v7", { timeout: 15000 });
    await online.waitForSelector("#officeMembers >> text=官署实账");
    await online.waitForSelector("#officeScheduledDutyStatus >> text=已有同类差事在办", { timeout: 15000 });
    await online.waitForSelector("#officeScheduledDutyStatus >> text=版本封印 0123456789ab", { timeout: 15000 });
    await online.click("#officeScheduledDutyToggle");
    await online.waitForSelector("#officeScheduledDutyStatus >> text=月例已停办", { timeout: 15000 });
    await online.waitForSelector("#officeScheduledDutyStatus >> text=Nexus封印 555555555555", { timeout: 15000 });
    await online.waitForSelector("#officeScheduledDutyStatus >> text=版本封印 0123456789ab", { timeout: 15000 });
    if (!(await online.locator("#officeScheduledDutyStatus").innerText()).includes("已派差事仍照常办理")) throw new Error("Disabling the monthly duty hid the already dispatched task");
    await online.click("#officeScheduledDutyToggle");
    await online.waitForSelector("#officeScheduledDutyToggle >> text=停办月例", { timeout: 15000 });
    if (scheduledDutyActions.map((entry) => entry.enabled).join(",") !== "false,true") throw new Error(`Unexpected monthly duty actions: ${JSON.stringify(scheduledDutyActions)}`);
    await online.waitForFunction(() => !document.querySelector("#officeMembershipApply").disabled && /1 席可申请/.test(document.querySelector("#officeMembershipDetail").textContent));
    await online.click("#officeMembershipApply");
    await online.waitForSelector("#officeMembershipState >> text=已入仕", { timeout: 15000 });
    await online.waitForSelector("#officeCareer:not([hidden])", { timeout: 15000 });
    await online.click("#officeCareerOptions");
    await online.waitForSelector("#officeCareerFeedback >> text=核验军粮账册", { timeout: 15000 });
    await online.fill("#officeCareerTaskName", "核验军粮账册");
    await online.click("#officeCareerRequestForm button[type=submit]");
    await online.waitForSelector("#officeCareerFeedback >> text=已经派发", { timeout: 15000 });
    await online.click("#officeCareerInbox");
    await online.waitForSelector("#officeCareerFeedback >> text=等待你处理", { timeout: 15000 });
    await online.fill("#officeCareerResponseDetail", "将交付时限顺延一日，并增加西仓封识清单");
    await online.click("#officeCareerModify");
    await online.waitForSelector("#officeCareerFeedback >> text=改令申请已经登记", { timeout: 15000 });
    await online.click("#officeCareerAccept");
    await online.waitForSelector("#officeCareerFeedback >> text=开始执行", { timeout: 15000 });
    await online.waitForSelector('#officeCareerStatus [data-task-id="00000000-0000-4000-8000-000000000083"]', { timeout: 15000 });
    await online.waitForSelector('#officeCareerStatus [data-task-id="00000000-0000-4000-8000-000000000081"].selected >> text=当前差事', { timeout: 15000 });
    await online.fill("#officeCareerResult", "北路桥梁冲毁，军粮车队无法通行");
    await online.click("#officeCareerException");
    await online.waitForSelector("#officeCareerFeedback >> text=差事暂停", { timeout: 15000 });
    await online.waitForSelector('#officeCareerStatus [data-exception-state="ACCEPTED"][data-trace-state="SEALED"] >> text=改走西驿道', { timeout: 15000 });
    await online.waitForSelector("#officeCareerStatus >> text=拆分车队，经西驿道绕行并补派斥候护送", { timeout: 15000 });
    await online.waitForSelector("#officeCareerStatus >> text=行迹封印 8888888888", { timeout: 15000 });
    await online.click('#officeCareerStatus [data-office-career-trace-task-id="00000000-0000-4000-8000-000000000081"]');
    await online.waitForSelector("#officeCareerStatus >> text=1 · 立案", { timeout: 15000 });
    await online.waitForSelector("#officeCareerStatus >> text=4 · 复行", { timeout: 15000 });
    await online.locator("#officeCareerStatus").scrollIntoViewIfNeeded();
    await online.screenshot({ path: path.join(OUT, "desktop-career-recovery.png"), fullPage: false });
    await online.fill("#officeCareerResult", "核清军粮三十车，账册已封存");
    await online.click("#officeCareerResultForm button[type=submit]");
    await online.waitForSelector("#officeCareerFeedback >> text=请按退回要求补呈", { timeout: 15000 });
    await online.waitForSelector("#officeCareerResultSubmit >> text=提交补呈", { timeout: 15000 });
    await online.waitForSelector("#officeCareerSupplementRequirement >> text=退回要求：请补齐西仓封识清单十二项。", { timeout: 15000 });
    if (!(await online.locator("#officeCareerException").isHidden())) throw new Error("Supplement form still exposes the execution blocker action");
    if (await online.locator("#officeCareerResult").getAttribute("aria-label") !== "补呈差事成果") throw new Error("Supplement input lacks its authoritative purpose label");
    await online.fill("#officeCareerResult", "补齐西仓封识清单十二项，并附经手人复核记录");
    await online.click("#officeCareerResultSubmit");
    await online.waitForSelector("#officeCareerFeedback >> text=贡献已经结算", { timeout: 15000 });
    await online.waitForSelector("#officeCareerContributions >> text=差事告成", { timeout: 15000 });
    await online.waitForSelector("#officeCareerContributions >> text=内核印记 999999999999", { timeout: 15000 });
    const playerDossierButton = online.locator('#officeCareerContributions [data-player-contribution-dossier-id="00000000-0000-4000-8000-000000000091"]');
    if (await playerDossierButton.count() !== 1) throw new Error(`Player contribution dossier control is missing: ${await online.locator("#officeCareerContributions").innerHTML()}`);
    await playerDossierButton.click();
    await online.waitForSelector("#officeCareerContributions >> text=个人功绩卷宗已封印", { timeout: 15000 });
    await online.waitForSelector("#officeCareerContributions >> text=立案 → 开工 → 定案 → 结算", { timeout: 15000 });
    await online.click('[data-player-contribution-verify-id="00000000-0000-4000-8000-000000000091"]');
    await online.waitForSelector("#officeCareerContributions >> text=验印通过 · 777777777777", { timeout: 15000 });
    await online.fill("#officeCareerTaskName", "核验军粮账册");
    await online.click("#officeCareerRequestForm button[type=submit]");
    await online.waitForSelector("#officeCareerFeedback >> text=已经派发", { timeout: 15000 });
    await online.fill("#officeCareerResponseDetail", "当前粮道已封，请另派属官承办");
    await online.click("#officeCareerReject");
    await online.waitForSelector("#officeCareerFeedback >> text=已记录拒绝", { timeout: 15000 });
    await online.waitForSelector('#officeCareerStatus [data-task-state="REJECTED"]', { timeout: 15000 });
    if (!(await online.locator("#officeCareerResponseForm").isHidden())) throw new Error("Rejected task still exposes response controls");
    await online.locator("#officeCareerContributions").scrollIntoViewIfNeeded();
    await online.screenshot({ path: path.join(OUT, "desktop-career-contribution.png"), fullPage: false });
    await online.setViewportSize({ width: 390, height: 844 });
    await online.locator("#officeCareerContributions").scrollIntoViewIfNeeded();
    const careerMobileLayout = await online.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    if (careerMobileLayout.scrollWidth > careerMobileLayout.width + 1) throw new Error(`Mobile player contribution ledger overflows viewport: ${JSON.stringify(careerMobileLayout)}`);
    await online.screenshot({ path: path.join(OUT, "mobile-career-contribution.png"), fullPage: false });
    await online.setViewportSize({ width: 1440, height: 900 });
    if (careerActions.map((entry) => entry.action).join(",") !== "options,request,inbox,modify,accept,exception,result,supplement,request,reject") throw new Error(`Unexpected player career sequence: ${JSON.stringify(careerActions)}`);
    if (!careerActions.find((entry) => entry.action === "modify")?.message.includes("将交付时限顺延一日，并增加西仓封识清单")) throw new Error("Task modification detail was not sent to the manager");
    if (!careerActions.find((entry) => entry.action === "modify")?.message.includes("《核验军粮账册》")) throw new Error("Task modification did not bind the selected task");
    if (!careerActions.find((entry) => entry.action === "reject")?.message.includes("当前粮道已封，请另派属官承办")) throw new Error("Task rejection reason was not sent to the manager");
    if (!careerActions.find((entry) => entry.action === "reject")?.message.includes("《核验军粮账册》")) throw new Error("Task rejection did not bind the selected task");
    if (!careerActions.find((entry) => entry.action === "exception")?.message.includes("北路桥梁冲毁")) throw new Error("Player blocker summary was not sent to the manager");
    if (!careerActions.find((entry) => entry.action === "exception")?.message.includes("《核验军粮账册》")) throw new Error("Player blocker report did not bind the selected task");
    if (!careerActions.find((entry) => entry.action === "result")?.message.includes("核清军粮三十车，账册已封存")) throw new Error("Player result summary was not sent to the manager");
    if (!careerActions.find((entry) => entry.action === "result")?.message.includes("《核验军粮账册》")) throw new Error("Player result report did not bind the selected task");
    if (!careerActions.find((entry) => entry.action === "supplement")?.message.includes("补齐西仓封识清单十二项")) throw new Error("Player supplement detail was not sent to the manager");
    if (!careerActions.find((entry) => entry.action === "supplement")?.message.includes("《核验军粮账册》")) throw new Error("Player supplement did not bind the selected task");
    await online.click("#officeMembershipLeave");
    await online.waitForSelector("#officeMembershipLeaveConfirm:not([hidden])", { timeout: 15000 });
    await online.click("#officeMembershipLeaveConfirm");
    await online.waitForSelector("#officeMembershipState >> text=尚未入仕", { timeout: 15000 });
    if (!(await online.locator("#officeCareer").isHidden())) throw new Error("Player career controls remained visible after leaving the court");
    if (membershipJoined) throw new Error("Membership leave did not release the reserved position");
    const visibleMembers = await online.locator("#officeMemberSelect option").evaluateAll((options) => options.map((option) => option.value));
    if (!visibleMembers.includes("DuBo")) throw new Error("Organization manager is missing from the inspectable NPC roster");
    npcStateAttempts = 0;
    await online.selectOption("#officeMemberSelect", "DuBo");
    await online.waitForFunction(() => document.querySelector("#officeIssueButton").disabled && /组织负责人/.test(document.querySelector("#officeOrderHint").textContent));
    await online.waitForSelector("#officeNpcState >> text=属官服务正在恢复", { timeout: 10000 });
    await online.waitForSelector("#officeNpcState >> text=坚决", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=上次事务结果待确认 · 校核军令", { timeout: 15000 });
    const assignee = visibleMembers.find((value) => value && value !== "DuBo");
    if (!assignee) throw new Error("No non-manager organization assignee is available");
    await online.selectOption("#officeMemberSelect", assignee);
    await online.waitForSelector("#officeNpcState >> text=坚决", { timeout: 15000 });
    if (/\bresolute\b/i.test(await online.locator("#officeNpcState").innerText())) throw new Error("Internal NPC emotion enum leaked into the player UI");
    await online.waitForSelector("#officeNpcState >> text=情报核验 35", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=固执 79", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=正在当值 · 巡核军粮 · 第2/3步 · 等待游服回报", { timeout: 15000 });
    await online.waitForSelector("#officeNpcSchedule >> text=今日实况", { timeout: 15000 });
    await online.waitForSelector("#officeNpcSchedule >> text=当下：休息 · 稍后：检阅军阵、议定军令", { timeout: 15000 });
    await online.waitForSelector("#officeNpcSchedule >> text=日程已由属官确认", { timeout: 15000 });
    if (/\bplan-e2e\b/i.test(await online.locator("#officeNpcSchedule").innerText())) throw new Error("Internal AINPC schedule plan ID leaked into the player UI");
    await online.waitForSelector("#officeNpcState >> text=你", { timeout: 15000 });
    await online.waitForSelector("#officeNpcState >> text=杜伯", { timeout: 15000 });
    if (/未具名人物/.test(await online.locator("#officeNpcState").innerText())) throw new Error("Unattributed historical player leaked into the NPC relationship ledger");
    if (await online.locator("#officeNpcState dt", { hasText: "性情" }).count() !== 1) throw new Error("NPC personality was rendered more than once");
    await online.setViewportSize({ width: 390, height: 844 });
    const npcStateMobileLayout = await online.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    if (npcStateMobileLayout.scrollWidth > npcStateMobileLayout.width + 1) throw new Error(`Mobile NPC execution status overflows viewport: ${JSON.stringify(npcStateMobileLayout)}`);
    await online.setViewportSize({ width: 1440, height: 900 });
    await online.waitForSelector("#officeNpcAssignment >> text=胜任 82/100", { timeout: 15000 });
    await online.waitForSelector("#officeNpcAssignment >> text=日程已核验", { timeout: 15000 });
    if (/\bplan-e2e\b/i.test(await online.locator("#officeNpcAssignment").innerText())) throw new Error("Internal assignment plan ID leaked into the player UI");
    await online.waitForSelector("#officeNpcAssignment >> text=情绪 坚决 72", { timeout: 15000 });
    if (/\bresolute\b/i.test(await online.locator("#officeNpcAssignment").innerText())) throw new Error("Internal assignment emotion enum leaked into the player UI");
    await online.waitForSelector("#officeNpcAssignment >> text=适岗 56/100", { timeout: 15000 });
    await online.waitForSelector("#officeNpcAssignment >> text=意愿 50/100", { timeout: 15000 });
    await online.fill("#officeMessageInput", "北路军粮可曾送到？");
    await online.click("#officeMessageForm button[type=submit]");
    await online.waitForSelector("#officeCorrespondence >> text=北路军粮已经入仓", { timeout: 15000 });
    await online.waitForSelector("#officeCorrespondence >> text=平静", { timeout: 15000 });
    if (/\bcalm\b/i.test(await online.locator("#officeCorrespondence").innerText())) throw new Error("Internal correspondence emotion enum leaked into the player UI");
    if (npcStateAttempts < 7) throw new Error("NPC state did not retry after the transient outage");
    await online.fill("#officeKnowledgeQuery", "杜伯");
    await online.click("#officeKnowledgeForm button[type=submit]");
    await online.waitForSelector("#officeKnowledgeResults article");
    await online.waitForSelector("#officeKnowledgeResults >> text=检索封印 0123456789");
    const searchedKnowledge = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.knowledge.find((entry) => entry.id === "dongzhou_stage_001"));
    if (searchedKnowledge?.searchReceipt?.sourceProvenance?.digest !== sourceProvenance.digest) throw new Error("Knowledge search source seal was not persisted");
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
    if (!/受理封印 0123456789/.test(await online.locator("#officeTaskLedger li.active").innerText())) throw new Error("Organization acceptance source seal is missing from the task ledger");
    if (!/版本封印 0123456789/.test(await online.locator("#officeMandateLedger").innerText())) throw new Error("Four-service source seal is missing from the mandate ledger");
    const afterConcurrentOrder = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")));
    const acceptedTask = afterConcurrentOrder.organization.tasks[0];
    const acceptedCouncil = afterConcurrentOrder.organization.councils.find((entry) => entry.id === acceptedTask.mandate.council.requestId);
    if (acceptedCouncil?.sourceProvenance?.digest !== sourceProvenance.digest) throw new Error("Council source seal was not persisted");
    if (acceptedTask.mandate.council.sourceProvenance?.digest !== sourceProvenance.digest) throw new Error("Mandate did not retain its council source seal");
    if (acceptedTask.mandate.scheduleInterruption?.sourceProvenance?.digest !== sourceProvenance.digest) throw new Error("Schedule receipt did not retain its source seal");
    if (acceptedTask.sourceProvenance?.digest !== sourceProvenance.digest) throw new Error("Organization acceptance did not retain its source seal");
    if (afterConcurrentOrder.organization.month !== 2) throw new Error(`Accepted order rolled back a concurrent month advance: ${afterConcurrentOrder.organization.month}`);
    if (afterConcurrentOrder.campaignResources.provisions !== provisionsBeforeOrder - afterConcurrentOrder.organization.tasks[0].cost) throw new Error("Accepted order did not charge exactly once");
    if (orderAttempts !== 2) throw new Error("Repeated click created duplicate remote orders");
    if (mandateAttempts !== 2) throw new Error("Rejected order retry did not reuse the Nexus mandate request exactly once");
    await online.click("#officeAdvanceButton");
    await online.waitForSelector("#officeTaskLedger li.success");
    await online.waitForSelector("#officeTaskLedger >> text=人物四项归档");
    if (!/内核封印 a{10}/.test(await online.locator("#officeTaskLedger li.success").innerText())) throw new Error("Source-bound NPC settlement seal is missing from the task ledger");
    const taskNameWidth = await online.locator("#officeTaskLedger li.success > span").evaluate((element) => element.getBoundingClientRect().width);
    if (taskNameWidth < 100) throw new Error(`Task ledger name column collapsed to ${taskNameWidth}px`);
    if (organizationTaskReads < 2) throw new Error("A pending organization task was not polled within the same month advance");
    if (!savedRemoteTask) throw new Error("Remote task binding was not persisted");
    if (npcSyncAttempts < 2) throw new Error("NPC activation was cached before the service reported ready");
    if (npcSyncRequests.filter((entry) => entry.npcs?.some((npc) => npc.hero_id === "DuBo")).length < 2) throw new Error("Initializing manager NPC was not retried");
    await online.screenshot({ path: path.join(OUT, "desktop-office-online.png"), fullPage: false });
    sourceDrift = true;
    await online.reload({ waitUntil: "domcontentloaded" });
    await online.waitForSelector("#campaignScreen:not([hidden])", { timeout: 45000 });
    await online.click("#campaignOfficeButton");
    await online.waitForSelector("#officeServiceStatus >> text=属官版本不符", { timeout: 15000 });
    await online.waitForSelector("#officeServiceStatus .provenance.drift >> text=封印未验0123456", { timeout: 15000 });
    const driftTitle = await online.locator("#officeServiceStatus .drift:not(.provenance)").getAttribute("title");
    if (!driftTitle.includes(`运行上报 develop@${"0".repeat(40)}`)) throw new Error(`Reported source drift is missing: ${driftTitle}`);
    const driftState = await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-h5-profile-v2")).organization.backend);
    if (driftState.serviceAttestations.aiNpc !== false || driftState.serviceFailures.aiNpc !== "source_attestation_failed") throw new Error(`Source drift was not persisted: ${JSON.stringify(driftState)}`);
    await online.setViewportSize({ width: 390, height: 844 });
    const driftMobileLayout = await online.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth }));
    if (driftMobileLayout.scrollWidth > driftMobileLayout.width + 1) throw new Error(`Source drift status overflows mobile viewport: ${JSON.stringify(driftMobileLayout)}`);
    await online.screenshot({ path: path.join(OUT, "mobile-source-drift.png"), fullPage: false });
    if (errors.length) throw new Error(`Page errors: ${errors.join(" | ")}`);
    console.log(JSON.stringify({ result: "PASS", desktopLayout, mobileLayout, screenshots: OUT }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
