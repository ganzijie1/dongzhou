'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(fs.existsSync);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath});
 try {
  const page=await browser.newPage();
  const errors=[];page.on('pageerror',()=>errors.push(true));
  await page.goto('http://127.0.0.1:8780/',{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#app:not([hidden])',{timeout:45000});
  await page.click('#campaignOfficeButton');
  await page.fill('#officeKnowledgeQuery','杜伯 东郊索命');
  const pending=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/dongzhou/v1/knowledge/search',{timeout:150000});
  await page.click('#officeKnowledgeForm button');
  const response=await pending;assert.equal(response.status(),200);
  const data=await response.json();assert.equal(data.mode,'connected');
  assert(data.results.length>0);
  assert(data.results.every(r=>String(r.id).startsWith('dongzhou_stage_')));
  await page.waitForSelector('#officeKnowledgeResults article');
  await page.waitForFunction(()=>JSON.parse(localStorage.getItem('dongzhou-h5-profile-v2')).organization.knowledge.length>0);
  assert.equal(errors.length,0);
  const root=path.resolve(__dirname,'../output/integration-validation');
  await page.screenshot({path:path.join(root,'fulltext-live-restored.png')});
  const result={result:'PASS',mode:'live-no-api-interception',status:response.status(),resultsCount:data.results.length,publishedDongzhouOnly:true,displayed:true,codexRecorded:true};
  fs.writeFileSync(path.join(root,'fulltext-browser-restored.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
 }catch(e){console.error(JSON.stringify({result:'FAIL',errorType:e.name,details:'redacted'}));process.exitCode=1;}
 finally{await browser.close();}
})();
