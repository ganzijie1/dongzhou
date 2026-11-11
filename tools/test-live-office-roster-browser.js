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
const outputDir = path.join(root, 'output', 'integration-validation');
const reportPath = path.join(outputDir, 'live-office-roster-browser.json');
const screenshotPath = path.join(outputDir, 'live-office-roster-browser.png');
const url = process.env.DONGZHOU_TEST_URL || 'http://127.0.0.1:8780/';
const executablePath = [
  process.env.DONGZHOU_CHROMIUM_EXECUTABLE,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
].find((candidate) => candidate && fs.existsSync(candidate));

function businessOk(value) {
  return value && [0, 200, '0', '200'].includes(value.code);
}

function heroPath(response, suffix) {
  const pathname = new URL(response.url()).pathname;
  return pathname.includes('/npcs/') && pathname.endsWith(suffix);
}

(async () => {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const pageErrors = [];
  const failedResponses = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('response', (response) => {
    const pathname = new URL(response.url()).pathname;
    if (pathname.includes('/api/dongzhou/v1/') && response.status() >= 400) {
      failedResponses.push({ pathname, status: response.status() });
    }
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#campaignScreen:not([hidden])', { timeout: 45000 });
    await page.click('#campaignOfficeButton');
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])', { timeout: 45000 });
    await page.waitForFunction(() => document.querySelectorAll('#officeMemberSelect option').length === 12, null, { timeout: 45000 });

    const options = await page.locator('#officeMemberSelect option').evaluateAll((items) =>
      items.map((item) => ({ heroId: item.value, label: item.textContent.trim() }))
    );
    assert.equal(options.length, 12);
    assert.equal(new Set(options.map((item) => item.heroId)).size, 12);

    const members = [];
    for (const option of options) {
      const current = await page.locator('#officeMemberSelect').inputValue();
      if (current !== option.heroId) {
        const stateResponsePromise = page.waitForResponse(
          (response) => heroPath(response, '/state') && decodeURIComponent(new URL(response.url()).pathname).includes(`/npcs/${option.heroId}/`),
          { timeout: 45000 }
        );
        await page.selectOption('#officeMemberSelect', option.heroId);
        const stateResponse = await stateResponsePromise;
        assert.equal(stateResponse.status(), 200);
      }

      await page.waitForFunction(
        ({ heroId }) => {
          if (document.querySelector('#officeMemberSelect')?.value !== heroId) return false;
          const state = document.querySelector('#officeNpcState')?.textContent || '';
          const schedule = document.querySelector('#officeNpcSchedule')?.textContent || '';
          return /心境/.test(state) && /性情/.test(state) && /动机/.test(state)
            && /90 日当值/.test(schedule) && !/正在|恢复|不可用/.test(`${state}${schedule}`);
        },
        { heroId: option.heroId },
        { timeout: 60000 }
      );

      const stateText = await page.locator('#officeNpcState').innerText();
      const scheduleText = await page.locator('#officeNpcSchedule').innerText();

      const stateResponse = await page.evaluate(async (heroId) => {
        const response = await fetch(`api/dongzhou/v1/npcs/${encodeURIComponent(heroId)}/state`, {
          cache: 'no-store', credentials: 'same-origin'
        });
        return { status: response.status, body: await response.json() };
      }, option.heroId);
      assert.equal(stateResponse.status, 200);
      const state = stateResponse.body.data || stateResponse.body;
      assert.equal(state.heroId, option.heroId);
      assert.equal(state.runtime?.state, 'READY');
      assert.equal(state.knownNpcIds?.[option.heroId], state.npcId);
      for (const component of ['emotion', 'affection', 'relationships']) {
        assert(businessOk(state[component]), `${option.heroId} ${component} failed`);
      }

      members.push({
        heroId: option.heroId,
        npcId: state.npcId,
        label: option.label,
        personalityVisible: stateText.includes('性情'),
        motivationVisible: stateText.includes('动机'),
        scheduleVisible: scheduleText.includes('90 日当值'),
      });
    }

    assert.deepEqual(pageErrors, []);
    assert.deepEqual(failedResponses, []);
    fs.mkdirSync(outputDir, { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const report = {
      result: 'PASS',
      mode: 'real-services-browser-no-interception',
      memberCount: members.length,
      members,
      pageErrors,
      failedResponses,
      screenshot: screenshotPath,
    };
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
    console.log(JSON.stringify(report));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: 'FAIL', errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
