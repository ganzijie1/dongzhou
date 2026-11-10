"use strict";
// Replays an actually captured final snapshot only in an isolated offline browser.
// No service request, save, NPC message or clock mutation is permitted.
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
let chromium;
try { ({chromium} = require(path.resolve(__dirname, '../output/playwright-runtime/node_modules/playwright'))); }
catch (_) { ({chromium} = require('playwright')); }
const [snapshotPath, journalPath] = process.argv.slice(2);
assert(snapshotPath && journalPath, 'Supply the real captured task snapshot and its private acceptance journal');
const response = JSON.parse(fs.readFileSync(snapshotPath, 'utf8'));
const remote = response.result?.data || response.result || response.data || response;
const journal = JSON.parse(fs.readFileSync(journalPath, 'utf8'));
assert.equal(remote.task_id, journal.remoteTask);
assert(['SUCCESS', 'PARTIAL'].includes(remote.final_result), 'Actual successful/partial final result is required; never invent it');
assert.equal(remote.state, remote.final_result === 'SUCCESS' ? 'SUCCEEDED' : 'PARTIALLY_COMPLETED', 'Task state must match its actual final result');
assert.equal(journal.orderRequest.task_type, 'supply');
const url = new URL(process.env.DONGZHOU_TEST_URL || 'http://127.0.0.1:8780/');
url.searchParams.set('offline', '1');
const executablePath = [process.env.DONGZHOU_CHROMIUM_EXECUTABLE, 'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(p => p && fs.existsSync(p));
const PROFILE='dongzhou-h5-profile-v2', BATTLE='dongzhou-h5-battle-v2';
async function ready(page) { await page.goto(url.href, {waitUntil:'domcontentloaded'}); await page.waitForSelector('#app:not([hidden])', {timeout:45000}); }
async function saved(page) { return page.evaluate(({PROFILE,BATTLE}) => ({profile:JSON.parse(localStorage.getItem(PROFILE)),battle:JSON.parse(localStorage.getItem(BATTLE))}), {PROFILE,BATTLE}); }
(async () => {
  const browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath}: {})});
  const apiRequests=[], errors=[];
  try {
    const context=await browser.newContext();
    await context.route('**/api/**', route => {apiRequests.push(route.request().method());return route.abort();});
    const page=await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await ready(page);
    const expected=remote.final_result === 'PARTIAL' ? 12 : 24;
    await page.evaluate(({PROFILE,remote,journal,expected}) => {
      const p=JSON.parse(localStorage.getItem(PROFILE));
      p.campaignResources.provisions=80;
      p.organization.tasks=[{id:journal.localTask,type:'supply',name:'转运军粮',status:'active',assigneeId:'ZuoRu',assigneeName:'左儒',stageId:'01',stageTitle:'东郊索命',remoteResult:journal.remoteTask}];
      p.organization.pendingSupport=[];
      p.organization=DongzhouOrganizationPlay.reconcileRemoteTasks(p.organization,[remote]);
      if(p.organization.pendingSupport.length!==1 || p.organization.pendingSupport[0].provisions!==expected) throw Error('Real final result did not create its expected support');
      p.organization=DongzhouOrganizationPlay.reconcileRemoteTasks(p.organization,[remote]);
      if(p.organization.pendingSupport.length!==1) throw Error('Repeated snapshot duplicated reward');
      localStorage.setItem(PROFILE,JSON.stringify(p));
    },{PROFILE,remote,journal,expected});
    await ready(page);
    await page.click('#campaignOfficeButton');
    await page.waitForSelector(`#officeTaskLedger li.${remote.final_result === 'PARTIAL' ? 'partial' : 'success'}`);
    await ready(page);
    await page.click('#focusStageButton');
    await page.waitForFunction(key=>!!localStorage.getItem(key),BATTLE);
    const first=await saved(page);
    assert.equal(first.battle.organizationSupport.provisions,expected);
    assert.equal(first.profile.campaignResources.provisions,80+expected);
    assert.equal(first.profile.organization.pendingSupport.length,0);
    await ready(page);
    assert.equal(await page.locator('#focusStageButton').getAttribute('data-saved'),'true');
    await page.click('#focusStageButton');
    await page.waitForFunction(()=>document.body.innerText.includes('已恢复第'));
    const resumed=await saved(page);
    assert.deepEqual(resumed.battle.organizationSupport,first.battle.organizationSupport);
    assert.deepEqual(resumed.profile.campaignResources,first.profile.campaignResources);
    assert.equal(resumed.profile.organization.pendingSupport.length,0);
    assert.deepEqual(apiRequests,[]); assert.deepEqual(errors,[]);
    console.log(JSON.stringify({result:'PASS',source:'captured-real-task-snapshot',finalResult:remote.final_result,rewardProvisions:expected,resourcesBefore:80,resourcesAfter:80+expected,duplicateSnapshotCreditedOnce:true,reloadCreditedOnce:true,serviceRequests:0}));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error.message);process.exitCode=1;});
