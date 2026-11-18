'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
let chromium;
try {
 ({chromium}=require(path.resolve(__dirname,'../output/playwright-runtime/node_modules/playwright')));
} catch (_) {
 ({chromium}=require('playwright'));
}
const url=process.env.DONGZHOU_TEST_URL||'http://127.0.0.1:8780/';
const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(fs.existsSync);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath});
 try {
  const page=await browser.newPage();
  const errors=[];page.on('pageerror',()=>errors.push(true));
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#app:not([hidden])',{timeout:45000});
  await page.click('#campaignOfficeButton');
  await page.fill('#officeKnowledgeQuery','郑伯克段 周郑交质');
  const pending=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/dongzhou/v1/knowledge/search',{timeout:150000});
  await page.click('#officeKnowledgeForm button');
  const response=await pending;assert.equal(response.status(),200);
  const data=await response.json();assert.equal(data.mode,'connected');
  assert(data.results.length>0);
  assert(data.results.every(r=>String(r.id).startsWith('dongzhou_stage_')));
  const graphResult=data.results.find(r=>r.retrieval?.channels?.some(channel=>channel.channel==='graph'&&channel.graphPath));
  assert(graphResult,'expected a result with graph path evidence');
  const graphPath=graphResult.retrieval.channels.find(channel=>channel.channel==='graph'&&channel.graphPath).graphPath;
  assert.equal(graphPath.nodes.length,graphPath.hops+1);
  assert.equal(graphPath.relations.length,graphPath.hops);
  await page.waitForSelector('#officeKnowledgeResults article');
  await page.waitForFunction(()=>document.querySelector('#officeKnowledgeResults').textContent.includes('牵连路径'));
  await page.waitForFunction(()=>JSON.parse(localStorage.getItem('dongzhou-h5-profile-v2')).organization.knowledge.length>0);
  assert.equal(errors.length,0);
  const root=path.resolve(__dirname,'../output/integration-validation');
  const graphArticle=page.locator('#officeKnowledgeResults article').filter({hasText:'牵连路径'}).first();
  await graphArticle.screenshot({path:path.join(root,'graph-path-live.png')});
  await page.setViewportSize({width:390,height:844});
  const mobileLayout=await graphArticle.evaluate(element=>({width:element.getBoundingClientRect().width,scrollWidth:element.scrollWidth,viewport:document.documentElement.clientWidth}));
  assert(mobileLayout.scrollWidth<=mobileLayout.width+1,JSON.stringify(mobileLayout));
  assert(mobileLayout.width<=mobileLayout.viewport,JSON.stringify(mobileLayout));
  await graphArticle.screenshot({path:path.join(root,'graph-path-mobile-live.png')});
  const result={result:'PASS',mode:'live-no-api-interception',status:response.status(),resultsCount:data.results.length,publishedDongzhouOnly:true,graphPath:{hops:graphPath.hops,nodes:graphPath.nodes.map(node=>node.name||node.id),relations:graphPath.relations},displayed:true,codexRecorded:true,mobileNoOverflow:true};
  fs.writeFileSync(path.join(root,'fulltext-browser-restored.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
 }catch(e){console.error(JSON.stringify({result:'FAIL',errorType:e.name,message:e.message,stack:e.stack}));process.exitCode=1;}
 finally{await browser.close();}
})();
