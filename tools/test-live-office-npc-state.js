'use strict';

const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, '../output/playwright-runtime/node_modules/playwright')));
} catch (_) {
  ({ chromium } = require('playwright'));
}

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'output', 'integration-validation', 'npc-execution-status-live.png');
const mobileOutput = path.join(root, 'output', 'integration-validation', 'npc-execution-status-mobile-live.png');
const executablePath = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  const page = await context.newPage();
  const requests = { sync: 0, state: 0, schedule: 0 };
  const scheduleStatuses = [];
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.name));
  page.on('response', (response) => {
    const pathname = new URL(response.url()).pathname;
    if (pathname.endsWith('/npcs/sync')) requests.sync += 1;
    if (/\/npcs\/[^/]+\/state$/.test(pathname)) requests.state += 1;
    if (/\/npcs\/[^/]+\/schedule$/.test(pathname)) {
      requests.schedule += 1;
      scheduleStatuses.push({ method: response.request().method(), status: response.status() });
    }
  });

  try {
    await page.goto('http://127.0.0.1:8780/', { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 45000 });
    const stateResponsePromise = page.waitForResponse((response) => /\/npcs\/[^/]+\/state$/.test(new URL(response.url()).pathname));
    await page.click('#campaignOfficeButton');
    const stateResponse = await stateResponsePromise;
    assert.equal(stateResponse.status(), 200);
    const stateBody = await stateResponse.json();
    assert.equal(stateBody.knownNpcIds[stateBody.heroId], stateBody.npcId);
    assert.match(String(stateBody.aiPlayerId || ''), /^\d+$/);
    assert.equal(stateBody.execution?.available, true);
    assert.equal(typeof stateBody.execution?.running, 'boolean');
    assert(!/[ÃÂ]|ä¼/.test(String(stateBody.execution?.scheduleName || '')));
    const leakedExecution = JSON.stringify(stateBody.execution);
    assert(!/loginRequest|session|terminal|pendingOperation|errorMessage/i.test(leakedExecution));
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])');
    await page.waitForSelector('#officeNpcState strong', { timeout: 45000 });
    await page.waitForSelector('#officeNpcSchedule strong', { timeout: 90000 });
    await page.waitForSelector('#officeNpcMemories .office-memory-item', { timeout: 45000 });

    const stateText = await page.locator('#officeNpcState').innerText();
    const scheduleText = await page.locator('#officeNpcSchedule').innerText();
    assert(!/temporarily unavailable|正在恢复|暂不可用/i.test(stateText));
    assert(!/temporarily unavailable|正在恢复|暂不可用/i.test(scheduleText));
    assert(stateText.trim().length > 0 && scheduleText.trim().length > 0);
    assert.match(stateText, /执行/);
    assert.match(stateText, /正在当值|当前无执行中的事务|执行暂停/);
    assert(!/未具名人物/.test(stateText));
    assert(scheduleStatuses.some((entry) => entry.method === 'GET' && entry.status === 200));
    const relationshipItems = stateBody.relationships?.data?.items || stateBody.relationships?.items || [];
    if (relationshipItems.length) {
      assert.match(stateText, /人情簿/);
      assert.match(stateText, /杜伯/);
    }
    assert(requests.sync >= 1 && requests.state >= 1 && requests.schedule >= 1);
    assert.equal(errors.length, 0);
    const memoryItems = await page.locator('#officeNpcMemories .office-memory-item').count();
    await page.locator('#officeNpcMemories [data-memory-id]').first().click();
    assert.equal(await page.locator('#officeNpcMemories .office-memory-item.selected').count(), 1);
    assert(memoryItems > 0);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.screenshot({ path: output, fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    const statePanel = page.locator('#officeNpcState');
    await statePanel.scrollIntoViewIfNeeded();
    const stateOverflow = await statePanel.evaluate((element) => element.scrollWidth > element.clientWidth + 1);
    assert.equal(stateOverflow, false);
    await statePanel.screenshot({ path: mobileOutput });
    const memoryPanel = page.locator('#officeNpcMemories');
    await memoryPanel.scrollIntoViewIfNeeded();
    const memoryOverflow = await memoryPanel.evaluate((element) => element.scrollWidth > element.clientWidth + 1);
    assert.equal(memoryOverflow, false);
    console.log(JSON.stringify({ result: 'PASS', mode: 'real-services-browser-no-interception', requests, scheduleStatuses, knownHeroes: Object.keys(stateBody.knownNpcIds).length, relationshipDetails: relationshipItems.length, memoryItems, screenshot: output, mobileScreenshot: mobileOutput }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: 'FAIL', errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
