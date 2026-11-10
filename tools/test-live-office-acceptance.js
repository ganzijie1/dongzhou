'use strict';
// Use only the dedicated existing acceptance account; no new order or clock change.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
let chromium;
try {({chromium}=require(path.resolve(__dirname,'../output/playwright-runtime/node_modules/playwright')));}
catch (_) {({chromium}=require('playwright'));}
const journal=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
assert(journal.reportVerified && journal.remoteTask && journal.installation);
const PROFILE='dongzhou-h5-profile-v2',BATTLE='dongzhou-h5-battle-v2';
const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(fs.existsSync);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath});
 let stage='load';
 try {
  const context=await browser.newContext();
  await context.addInitScript(installation=>localStorage.setItem('dongzhou-installation-id-v1',installation),journal.installation);
  const page=await context.newPage(),writes=[],taskReads=[],errors=[];
  page.on('pageerror',()=>errors.push(true));
  page.on('response',r=>{const u=new URL(r.url()).pathname;
   if(u==='/api/dongzhou/v1/save' && r.request().method()==='PUT')writes.push(r.status());
   if(u.startsWith('/api/dongzhou/v1/organization/tasks/'))taskReads.push(r.status());
  });
  const ready=async()=>{await page.goto('http://127.0.0.1:8780/',{waitUntil:'domcontentloaded'});await page.waitForSelector('#app:not([hidden])',{timeout:45000});};
  const read=()=>page.evaluate(({PROFILE,BATTLE})=>({profile:JSON.parse(localStorage.getItem(PROFILE)),battle:JSON.parse(localStorage.getItem(BATTLE))}),{PROFILE,BATTLE});
  await ready();
  const initial=await read();
  assert(initial.profile.organization.tasks.some(t=>t.remoteResult===journal.remoteTask));
  assert(!initial.battle,'Acceptance already entered battle; inspect saved evidence instead of repeating');
  const before=initial.profile.campaignResources.provisions;
  stage='live-task-reconciliation';
  await page.click('#campaignOfficeButton');
  await page.waitForFunction(()=>JSON.parse(localStorage.getItem('dongzhou-h5-profile-v2')).organization.backend.orgFlow===true);
  const saved=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/dongzhou/v1/save'&&r.request().method()==='PUT'&&r.status()===200);
  await page.click('#officeAdvanceButton');
  await page.waitForSelector('#officeTaskLedger li.success');
  await saved;
  const settled=await read();
  assert.equal(settled.profile.organization.pendingSupport.length,1);
  assert.equal(settled.profile.organization.pendingSupport[0].provisions,24);
  stage='cloud-reload';
  await ready();
  const loaded=await read();
  assert.equal(loaded.profile.organization.pendingSupport.length,1);
  assert.equal(loaded.profile.organization.tasks.find(t=>t.remoteResult===journal.remoteTask).status,'success');
  stage='live-battle';
  const battleSave=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/dongzhou/v1/save'&&r.request().method()==='PUT'&&r.status()===200);
  await page.click('#focusStageButton');
  await page.waitForFunction(key=>!!localStorage.getItem(key),BATTLE);
  await battleSave;
  const first=await read();
  assert.equal(first.battle.organizationSupport.provisions,24);
  assert.equal(first.profile.campaignResources.provisions,before+24);
  assert.equal(first.profile.organization.pendingSupport.length,0);
  stage='resume';
  await ready();
  await page.click('#focusStageButton');
  await page.waitForFunction(()=>document.body.innerText.includes('已恢复第'));
  const resumed=await read();
  assert.deepEqual(resumed.battle.organizationSupport,first.battle.organizationSupport);
  assert.equal(resumed.profile.campaignResources.provisions,before+24);
  assert.equal(resumed.profile.organization.pendingSupport.length,0);
  assert(taskReads.length>0 && taskReads.every(s=>s===200));
  assert(writes.length>=2 && writes.every(s=>s===200));
  assert.equal(errors.length,0);
  const result={result:'PASS',mode:'live-services-no-interception',realTaskReads:taskReads.length,cloudWrites:writes.length,resourcesBefore:before,resourcesAfter:before+24,rewardProvisions:24,cloudReloadVerified:true,battleResumeCreditedOnce:true,newOrders:0,clockChanges:0};
  fs.writeFileSync(path.resolve(__dirname,'../output/integration-validation/live-office-acceptance-20261109.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
 }catch(e){console.error(JSON.stringify({result:'FAIL',stage,errorType:e.name,details:'redacted; preserve current acceptance state before retry'}));process.exitCode=1;}
 finally{await browser.close();}
})();
