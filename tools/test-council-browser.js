"use strict";
// All browser requests are fulfilled locally. No real service or save is called.
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
let chromium;
try { ({chromium} = require(path.resolve(__dirname, '../output/playwright-runtime/node_modules/playwright'))); }
catch (_) { ({chromium} = require('playwright')); }
const WEB=path.resolve(__dirname,'../web-game');
const PROFILE='dongzhou-h5-profile-v2', BATTLE='dongzhou-h5-battle-v2';
const BASE_URL=process.env.DONGZHOU_TEST_URL || 'http://127.0.0.1:8780/';
const BASE_ORIGIN=new URL(BASE_URL).origin;
const CORRESPONDENCE={messageId:'correspondence-browser-1',digest:'d'.repeat(64),chatId:'chat-browser',taskId:'orgchat-browser',speakerId:'42',speakerName:'左儒',targetId:'99',targetName:'杜伯',content:'军粮路线已定，北道可行。',emotion:'calm',topic:'军粮',deliveredAt:'0772-10-22T08:00:00Z'};
const CODEX_ENTRY={id:'dongzhou_stage_001',stageId:'01',name:'第一回·东郊索命',summary:'周宣王闻谣轻杀，杜伯与左儒化厉鸣冤。',keywords:['杜伯','左儒'],people:['周宣王','杜伯','左儒'],retrieval:{channels:[{channel:'graph',normalizedScore:1}]},sourceDetails:[{work:'《史记·周本纪》',tier:'史实骨架',scope:'千亩之败与宣王晚年',url:'https://ctext.org/shiji/zhou-ben-ji'},{work:'《东周列国志》第一回',tier:'文学演绎',scope:'杜伯、左儒化厉索命',url:'https://zh.wikisource.org/zh-hans/东周列国志/第001回'}]};
const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(p=>fs.existsSync(p));
const clone=x=>JSON.parse(JSON.stringify(x));
async function setup(browser) {
  const context=await browser.newContext();
  const model={cloud:{},version:0,orders:[],decisions:[],mandates:[],mandateResumes:[],settlementReviews:[],reviewAccepted:false,errors:[],unexpected:[],mode:'success',release:null,mandateDraft:null};
  await context.route('**/*', async route=>{
    const req=route.request(), u=new URL(req.url()), p=u.pathname;
    if(u.origin!==BASE_ORIGIN) {model.unexpected.push(req.url());return route.abort();}
    if(!p.startsWith('/api/')) {
      const file=path.resolve(WEB,'.'+decodeURIComponent(p==='/'?'/index.html':p));
      if(!file.startsWith(WEB+path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return route.fulfill({status:404,body:'not found'});
      const mime={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml','.mp3':'audio/mpeg','.ogg':'audio/ogg','.wav':'audio/wav','.lua':'text/plain'};
      return route.fulfill({status:200,contentType:mime[path.extname(file)]||'application/octet-stream',body:fs.readFileSync(file)});
    }
    let body={};
    if(p.endsWith('/sessions/guest')) body={playerId:'council-test-player',expiresIn:86400};
    else if(p.endsWith('/save')) {
      if(req.method()==='PUT') {
        if(model.failSave) return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:{message:'mock save unavailable'}})});
        const input=req.postDataJSON();assert.equal(input.expected_version,model.version);model.cloud=clone(input.payload);model.version++;
      }
      body={version:model.version,payload:clone(model.cloud)};
    } else if(p.endsWith('/integration/status')) body={mode:'connected',organizationId:'test',services:{nexusKernel:{online:true},orgFlow:{online:true},aiNpc:{online:true},knowledge:{online:true}}};
    else if(p.endsWith('/npcs/interaction-preference')) body={enabled:req.postDataJSON().enabled,source:'dongzhou-player-settings',updatedAt:'2026-11-11T12:00:00Z'};
    else if(p.endsWith('/organization/roster')) body={organization:{id:'test',name:'东周军府',state:'ACTIVE',growthContribution:0},members:[]};
    else if(p.endsWith('/organization/inventory')) body={organizationId:'test',gameServerId:'91001',revision:7,accounts:[{resourceKey:'task.execution',balance:128,version:3}]};
    else if(p.endsWith('/knowledge/codex')) body={results:[clone(CODEX_ENTRY)]};
    else if(p.endsWith('/knowledge/stages/01')) body={mode:'connected',results:[{id:'dongzhou_stage_001',name:'Stage One Source',summary:'Published source for this stage.',stageId:'01',sourceDetails:[{work:'《史记·周本纪》',tier:'史实骨架',scope:'千亩之败',url:'https://ctext.org/shiji/zhou-ben-ji'}]}]};
    else if(p.endsWith('/knowledge/search')) body={mode:'connected',results:[{id:'dongzhou_stage_001',name:'Stage One Source',summary:'Published source for this stage.',stageId:'01',retrieval:{aggregateScore:.47,strongestChannel:'graph',graphRelated:true,channels:[{channel:'graph',score:1,normalizedScore:1,rank:1},{channel:'bm25',score:7,normalizedScore:.8,rank:2}]},searchReceipt:{id:'dongzhou:council-test-player:00000000-0000-4000-8000-000000000088',digest:'c'.repeat(64)},sourceDetails:[{work:'《史记·周本纪》',tier:'史实骨架',scope:'千亩之败',url:'https://ctext.org/shiji/zhou-ben-ji'}]}]};
    else if(p.endsWith('/npcs/sync')) body={ready:true,npcs:[]};
    else if(p.endsWith('/correspondence')) body={heroId:p.split('/').at(-2),npcId:'42',messages:[clone(CORRESPONDENCE)]};
    else if(p.endsWith('/state')) body={knownNpcIds:{DuBo:'41',ZuoRu:'42'},emotion:{data:{}},affection:{data:{items:[{target_id:'42',dominant_affection_type:'respect',max_value:68}],total:1}},relationships:{data:{items:[{target_id:'42',relation_type:'organization',relation_sub:'superior_subordinate',title:'司徒',is_bilateral:true,is_active:true}],total:1}}};
    else if(p.includes('/assignments/')) {const type=p.split('/').at(-1);body={assignment:{heroId:p.split('/').at(-3),npcId:'42',runtimeState:'READY',planId:'plan-browser',generationId:'generation-browser',eventId:`event-${type}`,transactionId:9100103,name:type==='supply'?'转运军粮':'检阅军阵',type:'军务',date:'0772-10-22',day:1,stageRange:{start:1,end:20},timeSlot:'',importance:90,state:{emotion:'calm',intensity:0,affectionCount:0,relationshipCount:0}}};}
    else if(p.endsWith('/schedule')) body={schedule:{data:{schedules:[]}}};
    else if(p.endsWith('/decisions')) {
      model.decisions.push(req.postDataJSON());
      if(model.mode==='delay') await new Promise(resolve=>{model.release=resolve;});
      if(model.mode==='failure') return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:{message:'mock decision unavailable'}})});
      body={state:'COMPLETED',decision:{data:{type:'OPTION',index:0,text:req.postDataJSON().options[0].text}}};
    } else if(p.endsWith('/court/mandates')) {
      const input=req.postDataJSON();model.mandates.push(input);
      body={state:'REQUIRES_ACTION',action:{actionId:'00000000-0000-4000-8000-000000000099',code:'seal_court_mandate',type:'confirmation',options:['APPROVE','REJECT']},mandate:{id:`dongzhou:council-test-player:${input.client_request_id}`,stageId:input.stage_id,stageTitle:'东郊索命',heroId:input.hero_id,taskType:input.task_type,evidence:{id:input.knowledge_id,name:'Stage One Source',summary:'Published source for this stage.',source:{index:input.evidence_source_index,work:'《史记·周本纪》',tier:'史实骨架',scope:'千亩之败',url:'https://ctext.org/shiji/zhou-ben-ji'},retrieval:{aggregateScore:.47,strongestChannel:'graph',graphRelated:true,channels:[{channel:'graph',score:1,normalizedScore:1,rank:1},{channel:'bm25',score:7,normalizedScore:.8,rank:2}]},searchReceipt:{id:input.knowledge_search_receipt_id,digest:input.knowledge_search_receipt_digest}},correspondence:clone(CORRESPONDENCE),council:{requestId:input.council_request_id,index:input.decision_index,text:'筹措军粮',correspondence:clone(CORRESPONDENCE)},assignment:{heroId:input.hero_id,npcId:'42',runtimeState:'READY',planId:input.schedule_plan_id,generationId:'generation-browser',eventId:input.schedule_event_id,transactionId:9100103,name:'转运军粮',type:'军需',date:'0772-10-22',day:1,stageRange:{start:1,end:20},timeSlot:'',importance:90,state:{emotion:'calm',intensity:0,affectionCount:0,relationshipCount:0}},kernel:{module:'dongzhou_mandate_workflow',moduleVersion:'1.1.0',nexusKernelVersion:'0.2.0',state:'READY'},digest:'a'.repeat(64),state:'DRAFT'}};model.mandateDraft=clone(body.mandate);
    } else if(p.includes('/court/mandates/')&&p.endsWith('/resume')) {const input=req.postDataJSON();model.mandateResumes.push(input);body={state:'ISSUED',mandate:{...clone(model.mandateDraft),state:'ISSUED'}};
    } else if(p.endsWith('/organization/tasks')) {model.orders.push(req.postDataJSON());body={state:'ACCEPTED',taskId:'council-task'};}
    else if(p.endsWith('/organization/tasks/council-task/review')) {const input=req.postDataJSON();model.settlementReviews.push(input);model.reviewAccepted=true;body={state:'ACCEPTED',review:{settlementId:'settlement-council',closureDigest:'c'.repeat(64),finalResult:'SUCCESS',state:'ACCEPTED',decision:'ACCEPT'}};}
    else if(p.endsWith('/organization/tasks/council-task')) {const review=model.reviewAccepted?{state:'ACCEPTED',review:{settlementId:'settlement-council',closureDigest:'c'.repeat(64),finalResult:'SUCCESS',state:'ACCEPTED',decision:'ACCEPT'}}:{state:'REQUIRES_ACTION',review:{settlementId:'settlement-council',closureDigest:'c'.repeat(64),finalResult:'SUCCESS',state:'PENDING'},action:{actionId:'00000000-0000-4000-8000-000000000021',options:['ACCEPT','CENSURE']}};const settlement={settlementId:'settlement-council',taskId:'council-task',organizationId:'test',memberId:'member',result:'SUCCESS',organizationDelta:100,memberDelta:75,source:'NPC_CONFIRMATION'};body={result:{data:{task_id:'council-task',state:'SUCCEEDED',final_result:'SUCCESS',version:3}},settlement,closureReceipt:{state:'SEALED',digest:'c'.repeat(64),settlement},review};}
    else {model.unexpected.push(p);return route.fulfill({status:404,body:'unexpected mock request'});}
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(body)});
  });
  const page=await context.newPage();page.on('pageerror',e=>model.errors.push(e.message));
  await page.goto(BASE_URL,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#app:not([hidden])',{timeout:45000});
  await page.click('#campaignOfficeButton');
  const members=await page.locator('#officeMemberSelect option').evaluateAll(rows=>rows.map(r=>r.value).filter(Boolean));
  const member=members.find(id=>id!=='DuBo');assert(member);
  await page.selectOption('#officeMemberSelect',member);
  return {context,page,model,member,members};
}
async function knowledge(page) {await page.locator('#officeKnowledgeForm').evaluate(form=>form.requestSubmit());await page.waitForSelector('#officeKnowledgeResults article');assert.match(await page.locator('#officeKnowledgeResults article').innerText(),/图谱牵连 100%/);await page.click('[data-knowledge-id="dongzhou_stage_001"][data-source-index="0"]');await page.waitForSelector('#officeKnowledgeResults >> text=已取为据');}
async function councils(page) {return page.evaluate(key=>JSON.parse(localStorage.getItem(key)).organization.councils||[],PROFILE);}
async function decide(page) {await page.locator('#officeDecisionForm button[type=submit]').click();}
(async()=>{
  const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
  try {
    const happy=await setup(browser), {page,model}=happy;
    await page.waitForSelector('#officeInventoryAccounts >> text=差事额度');
    assert.match(await page.locator('.office-inventory').innerText(),/差事额度\s+128/);
    assert.match(await page.locator('.office-inventory').innerText(),/账本第 7 版/);
    await page.waitForSelector('#officeNpcState >> text=人情簿');
    assert.match(await page.locator('#officeNpcState').innerText(),/左儒[\s\S]*敬重 68/);
    assert.match(await page.locator('#officeNpcState').innerText(),/左儒[\s\S]*司徒 · 相互/);
    await decide(page);await page.waitForTimeout(50);
    assert.equal(model.decisions.length,0);
    await knowledge(page);
    await page.click('#officeCodexToggle');await page.waitForSelector('#officeCodexList [data-codex-id="dongzhou_stage_001"]');
    assert.match(await page.locator('#officeCodexDetail').innerText(),/杜伯 · 左儒/);
    assert.equal(await page.locator('#officeCodexDetail a').first().getAttribute('href'),'https://ctext.org/shiji/zhou-ben-ji');
    await page.fill('#officeCodexFilter','不存在的条目');await page.waitForSelector('#officeCodexSummary >> text=当前 0 卷');
    await page.fill('#officeCodexFilter','杜伯');await page.waitForSelector('#officeCodexSummary >> text=当前 1 卷');
    await page.click('#officeCodexToggle');
    await page.waitForSelector('[data-correspondence-id="correspondence-browser-1"]');await page.click('[data-correspondence-id="correspondence-browser-1"]');await decide(page);
    await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).organization.councils.length===1,PROFILE);
    assert.match(model.decisions[0].question,/选证：《史记·周本纪》｜史实骨架/);
    assert.match(model.decisions[0].question,/耳报印记：dddddddddddd/);
    assert.equal(await page.locator('#officeUseCouncil').isChecked(),false);
    await page.selectOption('#officeTaskType','supply');
    await page.locator('#officeUseCouncil').check();
    const provisionsBeforeDraft=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).campaignResources.provisions,PROFILE);
    await page.click('#officeIssueButton');await page.waitForSelector('#officeMandateApproval:not([hidden])');
    assert.equal(model.orders.length,0,'Draft mandate must not create an organization order');
    assert.equal(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).organization.tasks.length,PROFILE),0);
    assert.equal(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).campaignResources.provisions,PROFILE),provisionsBeforeDraft);
    await page.reload({waitUntil:'domcontentloaded'});await page.waitForSelector('#app:not([hidden])');await page.click('#campaignOfficeButton');
    await page.waitForSelector('#officeMandateApproval:not([hidden])');await page.selectOption('#officeTaskType','supply');
    await page.click('#officeMandateApproveButton');await page.waitForSelector('#officeTaskLedger li.active');
    assert.equal(model.mandateResumes.length,1);assert.equal(model.mandateResumes[0].decision,'APPROVE');
    assert.equal(model.mandates.length,1);assert.equal(model.mandates[0].knowledge_id,'dongzhou_stage_001');assert.equal(model.mandates[0].evidence_source_index,0);assert.equal(model.mandates[0].schedule_event_id,'event-supply');assert.equal(model.mandates[0].council_request_id,model.cloud.organization.councils[0].id);
    assert.equal(model.mandates[0].knowledge_search_receipt_digest,'c'.repeat(64));assert.match(model.decisions[0].question,/检索回执：cccccccccccc/);
    assert.equal(model.mandates[0].correspondence_message_id,CORRESPONDENCE.messageId);assert.equal(model.mandates[0].correspondence_digest,CORRESPONDENCE.digest);
    assert.equal(model.orders.length,1);assert.equal(model.orders[0].parameters.mandate_id,model.cloud.organization.mandates[0].id);assert.equal(model.orders[0].parameters.mandate_digest,'a'.repeat(64));
    await page.waitForFunction(key=>!!JSON.parse(localStorage.getItem(key)).organization.tasks[0].council,PROFILE);
    assert.equal(model.cloud.organization.tasks[0].council.knowledgeId,'dongzhou_stage_001');
    await page.click('#officeAdvanceButton');await page.waitForSelector('#officeSettlementReview:not([hidden])');await page.waitForFunction(()=>!document.querySelector('#officeAdvanceButton').disabled);
    assert.equal(model.cloud.organization.pendingSupport.length,0,'Pending review must not grant support');
    await page.click('#officeSettlementAcceptButton');await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).organization.tasks[0].pendingReview.state==='ACCEPTED',PROFILE);await page.waitForFunction(()=>!document.querySelector('#officeSettlementAcceptButton').disabled);assert.equal(model.settlementReviews[0].decision,'ACCEPT');
    await page.waitForFunction(()=>!document.querySelector('#officeAdvanceButton').disabled);await page.locator('#officeAdvanceButton').click({force:true});await page.waitForSelector('#officeTaskLedger li.success');
    assert.equal(model.cloud.organization.pendingSupport[0].council.id,model.cloud.organization.tasks[0].council.id);assert.equal(model.cloud.organization.pendingSupport[0].mandate.id,model.cloud.organization.tasks[0].mandate.id);
    const before=model.cloud.campaignResources.provisions;
    await page.reload({waitUntil:'domcontentloaded'});await page.waitForSelector('#app:not([hidden])');
    await page.click('#focusStageButton');await page.waitForFunction(key=>!!localStorage.getItem(key),BATTLE);
    const battle=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),BATTLE);
    assert.equal(battle.organizationSupport.provisions,24);assert.equal(battle.organizationSupport.councils[0].knowledgeId,'dongzhou_stage_001');assert.equal(battle.organizationSupport.mandates[0].digest,'a'.repeat(64));
    assert.match(await page.locator('#battleLog').innerText(),/Stage One Source/);assert.match(await page.locator('#battleLog').innerText(),/内核军令/);
    await page.waitForFunction(({key,before})=>JSON.parse(localStorage.getItem(key)).campaignResources.provisions===before+24,{key:PROFILE,before});
    const late=await setup(browser);await knowledge(late.page);late.model.mode='delay';await decide(late.page);
    while(late.model.decisions.length!==1) await new Promise(resolve=>setTimeout(resolve,10));
    while(!late.model.release) await new Promise(resolve=>setTimeout(resolve,10));
    let alternateMember=late.members.find(id=>id!==late.member);
    if(!alternateMember) {
      alternateMember='stale-test-member';
      await late.page.locator('#officeMemberSelect').evaluate((select,value)=>{
        const option=document.createElement('option');option.value=value;option.textContent='迟到答复测试';select.append(option);
      },alternateMember);
    }
    await late.page.selectOption('#officeMemberSelect',alternateMember);late.model.release();
    await late.page.waitForTimeout(100);
    assert.equal((await councils(late.page)).length,0);assert.equal((late.model.cloud.organization.councils||[]).length,0);
    const failure=await setup(browser);await knowledge(failure.page);failure.model.mode='failure';await decide(failure.page);
    while(failure.model.decisions.length!==1) await new Promise(resolve=>setTimeout(resolve,10));
    await failure.page.waitForTimeout(100);
    assert.equal((await councils(failure.page)).length,0);assert.equal((failure.model.cloud.organization.councils||[]).length,0);
    const saveFail=await setup(browser);await knowledge(saveFail.page);saveFail.model.failSave=true;await decide(saveFail.page);
    while(saveFail.model.decisions.length!==1) await new Promise(resolve=>setTimeout(resolve,10));
    await saveFail.page.waitForTimeout(150);
    assert.equal((await councils(saveFail.page)).length,0,'Failed cloud save must roll back the local council');
    assert.equal((saveFail.model.cloud.organization?.councils||[]).length,0);
    await happy.page.setViewportSize({width:320,height:700});await happy.page.goto(BASE_URL,{waitUntil:'domcontentloaded'});
    await happy.page.waitForSelector('#app:not([hidden])',{timeout:45000});await happy.page.click('#campaignOfficeButton');
    const mobileBox=await happy.page.evaluate(()=>{const drawer=document.querySelector('#campaignOfficeDrawer').getBoundingClientRect();return {left:drawer.left,right:drawer.right,width:innerWidth,scrollWidth:document.documentElement.scrollWidth};});
    assert(mobileBox.left>=0 && mobileBox.right<=mobileBox.width+1 && mobileBox.scrollWidth<=mobileBox.width+1);
    for(const test of [happy,late,failure,saveFail]) {assert.deepEqual(test.model.errors,[]);assert.deepEqual(test.model.unexpected,[]);}
    console.log(JSON.stringify({result:'PASS',mockOnly:true,realServiceRequests:0,knowledgeRequired:true,explicitCouncilOptIn:true,nexusMandateBoundToTaskAndBattle:true,councilBoundToTaskAndBattle:true,reward:24,lateMemberChangeDiscarded:true,failedDecisionNotSaved:true,failedCloudSaveRolledBack:true,mobile320NoOverflow:true}));
  } finally {await browser.close();}
})().catch(error=>{console.error(error.stack||error.message);process.exitCode=1;});
