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
const output = path.join(root, 'output', 'integration-validation', 'live-office-npc-state-complete80.png');
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
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])');
    await page.waitForSelector('#officeNpcState strong', { timeout: 45000 });
    await page.waitForSelector('#officeNpcSchedule strong', { timeout: 90000 });

    const stateText = await page.locator('#officeNpcState').innerText();
    const scheduleText = await page.locator('#officeNpcSchedule').innerText();
    assert(!/temporarily unavailable|正在恢复|暂不可用/i.test(stateText));
    assert(!/temporarily unavailable|正在恢复|暂不可用/i.test(scheduleText));
    assert(stateText.trim().length > 0 && scheduleText.trim().length > 0);
    assert(scheduleStatuses.some((entry) => entry.method === 'GET' && entry.status === 200));
    const relationshipItems = stateBody.relationships?.data?.items || stateBody.relationships?.items || [];
    if (relationshipItems.length) {
      assert.match(stateText, /人情簿/);
      assert.match(stateText, /杜伯/);
    }
    assert(requests.sync >= 1 && requests.state >= 1 && requests.schedule >= 1);
    assert.equal(errors.length, 0);

    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.screenshot({ path: output, fullPage: true });
    console.log(JSON.stringify({ result: 'PASS', mode: 'real-services-browser-no-interception', requests, scheduleStatuses, knownHeroes: Object.keys(stateBody.knownNpcIds).length, relationshipDetails: relationshipItems.length, screenshot: output }));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: 'FAIL', errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
