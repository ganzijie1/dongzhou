"use strict";
// Uses isolated offline browser contexts; never writes to live integration services.
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require(path.resolve(__dirname, "../output/playwright-runtime/node_modules/playwright"))); }
catch (_) { ({ chromium } = require("playwright")); }
const url = new URL(process.env.DONGZHOU_TEST_URL || "http://127.0.0.1:8781/");
url.searchParams.set("offline", "1");
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find(p => p && fs.existsSync(p));
const PROFILE = "dongzhou-h5-profile-v2";
const BATTLE = "dongzhou-h5-battle-v2";
async function ready(page) {
  await page.goto(url.href, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#app:not([hidden])", { timeout: 45000 });
}
async function snapshot(page) {
  return page.evaluate(({ PROFILE, BATTLE }) => ({ profile: JSON.parse(localStorage.getItem(PROFILE)), battle: JSON.parse(localStorage.getItem(BATTLE)) }), { PROFILE, BATTLE });
}
async function begin(page) {
  await page.click("#focusStageButton");
  await page.waitForFunction(key => !!localStorage.getItem(key), BATTLE);
}
(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const errors = [];
  try {
    const baseline = await browser.newPage();
    baseline.on("pageerror", error => errors.push(error.message));
    await ready(baseline);
    const initial = (await snapshot(baseline)).profile;
    await begin(baseline);
    const normal = (await snapshot(baseline)).battle;
    const page = await browser.newPage();
    page.on("pageerror", error => errors.push(error.message));
    await ready(page);
    await page.evaluate(({ PROFILE, initial }) => {
      initial.organization.pendingSupport = [{ id: "transaction-support", stageId: "01", source: "事务验收筹备", provisions: 18, morale: 7, attack: .2, defense: .2, recon: 2 }];
      initial.organization.tasks = [{ id: "partial-order", name: "转运军粮", assigneeName: "左儒", assigneeId: "ZuoRu", type: "supply", status: "partial" }];
      localStorage.setItem(PROFILE, JSON.stringify(initial));
    }, { PROFILE, initial });
    await ready(page);
    await page.click("#campaignOfficeButton");
    assert.match(await page.locator("#officeTaskLedger li.partial").innerText(), /部分办成/);
    // Reload closes the drawer and verifies the retained support survives startup.
    await ready(page);
    const before = await snapshot(page);
    let rejected = 0;
    await page.route("**/scenario/stage/**", route => { rejected++; return route.fulfill({ status: 503, body: "stage unavailable" }); });
    await page.click("#focusStageButton");
    await page.waitForFunction(() => document.body.innerText.includes("筹备已保留"));
    assert.equal(rejected, 1);
    const failed = await snapshot(page);
    assert.deepEqual(failed.profile.organization.pendingSupport, before.profile.organization.pendingSupport);
    assert.deepEqual(failed.profile.campaignResources, before.profile.campaignResources);
    assert.equal(failed.battle, null);
    await page.unroute("**/scenario/stage/**");
    for (const callback of ["on_deploy", "on_begin"]) {
      await page.evaluate(callback => {
        const original = window.DongzhouLuaRuntime.prototype.invoke;
        window.__restoreDeploymentInvoke = () => { window.DongzhouLuaRuntime.prototype.invoke = original; };
        window.DongzhouLuaRuntime.prototype.invoke = function (name) {
          const result = original.call(this, name);
          if (name === callback) throw new Error(`injected ${callback} failure after callback`);
          return result;
        };
      }, callback);
      await page.click("#focusStageButton");
      await page.waitForFunction(callback => document.querySelector("#floatingNotice").textContent.includes(`injected ${callback} failure`), callback);
      // Exercise the ordinary leave-battle path too: a half-created state must not
      // be autosaved by openCampaign after initialization failed.
      await page.evaluate(() => document.querySelector("#campaignButton").click());
      const callbackFailed = await snapshot(page);
      assert.deepEqual(callbackFailed.profile.organization.pendingSupport, before.profile.organization.pendingSupport, callback);
      assert.deepEqual(callbackFailed.profile.campaignResources, before.profile.campaignResources, callback);
      assert.equal(callbackFailed.battle, null, callback);
      await page.click("#campaignOfficeButton");
      assert.equal(await page.locator("#officeSupportCount").innerText(), "1", `In-memory preparation must roll back after ${callback}`);
      await page.evaluate(() => { window.__restoreDeploymentInvoke(); document.querySelector("#campaignButton").click(); });
    }
    await begin(page);
    const retried = await snapshot(page);
    assert.equal(retried.profile.organization.pendingSupport.length, 0);
    assert.equal(retried.battle.organizationSupport.attack, .2);
    assert.equal(retried.profile.campaignResources.provisions, Math.min(200, before.profile.campaignResources.provisions + 18));
    const own = retried.battle.units.find(unit => unit.team === "own");
    const ownBase = normal.units.find(unit => unit.heroId === own.heroId && unit.team === "own");
    assert.ok(own.power > ownBase.power, "Attack preparation must change actual unit power");
    assert.ok(own.defense > ownBase.defense, "Defense preparation must change actual unit defense");
    assert.ok(own.maxHp > ownBase.maxHp, "Defense preparation must change actual unit health");
    const enemy = retried.battle.units.find(unit => unit.team === "enemy");
    const enemyBase = normal.units.find(unit => unit.heroId === enemy.heroId && unit.team === "enemy");
    assert.ok(enemy.power < enemyBase.power, "Recon preparation must reduce actual enemy power");
    await ready(page);
    assert.equal(await page.locator("#focusStageButton").getAttribute("data-saved"), "true");
    await page.click("#focusStageButton");
    await page.waitForSelector("#campaignScreen", { state: "hidden" });
    await page.waitForFunction(() => document.body.innerText.includes("已恢复第"));
    const resumed = await snapshot(page);
    assert.deepEqual(resumed.battle.organizationSupport, retried.battle.organizationSupport);
    assert.deepEqual(resumed.profile.campaignResources, retried.profile.campaignResources);
    assert.equal(resumed.profile.organization.pendingSupport.length, 0);
    const online = await browser.newPage();
    online.on("pageerror", error => errors.push(error.message));
    const onlineUrl = new URL(url);
    onlineUrl.searchParams.delete("offline");
    let cloud = JSON.parse(JSON.stringify(before.profile));
    let version = 1;
    let failSaves = false;
    let conflictPage = null;
    let failedPuts = 0;
    let signalFailedPut;
    const failedPut = new Promise(resolve => { signalFailedPut = resolve; });
    const handleApi = async route => {
      const request = route.request();
      const pathname = new URL(request.url()).pathname;
      let body;
      let status = 200;
      if (pathname.endsWith("/sessions/guest")) body = { playerId: "preparation-transaction-test" };
      else if (pathname.endsWith("/save") && request.method() === "GET") body = { version, payload: cloud };
      else if (pathname.endsWith("/save") && request.method() === "PUT") {
        if (request.frame().page() === conflictPage) { status = 409; body = { error: { message: "injected competing page version conflict" } }; }
        else if (failSaves) { status = 503; body = { error: { message: "injected cloud save unavailable" } }; failedPuts++; signalFailedPut(); }
        else { cloud = request.postDataJSON().payload; body = { version: ++version, payload: cloud }; }
      } else if (pathname.endsWith("/integration/status")) body = { services: {} };
      else { status = 503; body = { error: { message: "Test denies all unmocked API calls" } }; }
      await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    };
    await online.route("**/api/**", handleApi);
    await online.goto(onlineUrl.href, { waitUntil: "domcontentloaded" });
    await online.waitForSelector("#app:not([hidden])");
    failSaves = true;
    await begin(online);
    await failedPut;
    assert.equal(cloud.organization.pendingSupport.length, 1, "Failed cloud writes leave the previous cloud preparation intact");
    const unsaved = await snapshot(online);
    assert.equal(unsaved.profile.organization.pendingSupport.length, 0);
    const transaction = unsaved.battle.organizationSupportTransaction;
    assert.ok(transaction);
    assert.ok(await online.evaluate(id => !!JSON.parse(localStorage.getItem("dongzhou-preparation-journal-v1"))[id], transaction));
    await online.reload({ waitUntil: "domcontentloaded" });
    await online.waitForSelector("#loadingScreen.failed");
    assert.equal(await online.locator("#app").isVisible(), false, "Unavailable recovery must not allow gameplay with stale cloud preparation");
    assert.ok(await online.evaluate(id => !!JSON.parse(localStorage.getItem("dongzhou-preparation-journal-v1"))[id], transaction));
    failSaves = false;
    await online.reload({ waitUntil: "domcontentloaded" });
    await online.waitForSelector("#app:not([hidden])");
    const recovered = await snapshot(online);
    assert.equal(recovered.profile.organization.pendingSupport.length, 0);
    assert.equal(cloud.organization.pendingSupport.length, 0);
    assert.deepEqual(recovered.profile.campaignResources, unsaved.profile.campaignResources);
    assert.ok(cloud.organization.consumedSupportTransactions.includes(transaction));
    assert.deepEqual(await online.evaluate(() => JSON.parse(localStorage.getItem("dongzhou-preparation-journal-v1"))), {});
    await online.reload({ waitUntil: "domcontentloaded" });
    await online.waitForSelector("#app:not([hidden])");
    assert.deepEqual((await snapshot(online)).profile.campaignResources, unsaved.profile.campaignResources, "Repeated startup must not credit preparation twice");
    // Two independently loaded pages consume the same business reward. One cloud
    // write wins and the other's journal survives a 409; recovery must not pay again.
    cloud = JSON.parse(JSON.stringify(before.profile));
    const first = await browser.newPage();
    const second = await browser.newPage();
    for (const tab of [first, second]) {
      tab.on("pageerror", error => errors.push(error.message));
      await tab.route("**/api/**", handleApi);
      await tab.goto(onlineUrl.href, { waitUntil: "domcontentloaded" });
      await tab.waitForSelector("#app:not([hidden])");
    }
    conflictPage = second;
    await begin(first);
    await first.waitForFunction(() => Object.keys(JSON.parse(localStorage.getItem("dongzhou-preparation-journal-v1") || "{}")).length === 0);
    const winnerResources = JSON.parse(JSON.stringify(cloud.campaignResources));
    await begin(second);
    await second.waitForFunction(() => document.querySelector("#floatingNotice").textContent.includes("其他页面更新"));
    assert.ok(await second.evaluate(() => Object.keys(JSON.parse(localStorage.getItem("dongzhou-preparation-journal-v1"))).length > 0));
    conflictPage = null;
    await second.reload({ waitUntil: "domcontentloaded" });
    await second.waitForSelector("#app:not([hidden])");
    assert.deepEqual(cloud.campaignResources, winnerResources, "Losing page recovery must not credit the same support again");
    assert.equal(cloud.organization.pendingSupport.length, 0);
    // A journal can overlap only some rewards: credit the still-available entry
    // from the cloud, not the journal's aggregate (which includes spent rewards).
    cloud.organization.pendingSupport = [{ id: "remaining-support", stageId: "01", provisions: 7, morale: 3, source: "剩余筹备" }];
    const partialBefore = JSON.parse(JSON.stringify(cloud.campaignResources));
    await second.evaluate(() => localStorage.setItem("dongzhou-preparation-journal-v1", JSON.stringify({
      "partial-overlap": { committed: true, supportIds: ["transaction-support", "remaining-support"], support: { provisions: 25, morale: 10 } }
    })));
    await second.reload({ waitUntil: "domcontentloaded" });
    await second.waitForSelector("#app:not([hidden])");
    assert.equal(cloud.campaignResources.provisions, Math.min(200, partialBefore.provisions + 7));
    assert.equal(cloud.campaignResources.morale, Math.min(100, partialBefore.morale + 3));
    assert.equal(cloud.organization.pendingSupport.length, 0);
    assert.ok(cloud.organization.consumedSupportIds.includes("remaining-support"));
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ result: "PASS", loadFailureRetainsSupport: true, deploymentCallbackRollback: ["on_deploy", "on_begin"], halfBattleNeverSaved: true, retryConsumesOnce: true, partialLabel: true, actualOwnPower: [ownBase.power, own.power], actualOwnDefense: [ownBase.defense, own.defense], actualEnemyPower: [enemyBase.power, enemy.power], reloadPreservesBattle: true, failedCloudPuts: failedPuts, cloudRecoveryExactlyOnce: true, competingPage409Deduplicated: true, partialOverlapCredited: 7 }));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
