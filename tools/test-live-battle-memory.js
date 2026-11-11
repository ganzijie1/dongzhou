'use strict';

const assert = require('assert/strict');
const { randomUUID } = require('crypto');
const fs = require('fs');
const path = require('path');

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, '../output/playwright-runtime/node_modules/playwright')));
} catch (_) {
  ({ chromium } = require('playwright'));
}

const root = path.resolve(__dirname, '..');
const evidencePath = path.join(root, 'output', 'integration-validation', 'live-battle-memory-complete81.json');
const screenshotPath = path.join(root, 'output', 'integration-validation', 'live-battle-memory-complete81.png');
const installationId = randomUUID();
const reportId = `battle:memory-complete81:${Date.now()}`;
const executablePath = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
].find(fs.existsSync);

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((id) => {
    localStorage.setItem('dongzhou-installation-id-v1', id);
  }, installationId);
  const page = await context.newPage();
  const errors = [];
  const responses = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('response', (response) => {
    const pathname = new URL(response.url()).pathname;
    if (pathname.endsWith('/save')) {
      responses.push({ method: response.request().method(), status: response.status() });
    }
  });

  try {
    console.log(JSON.stringify({ stage: 'startup', installationId }));
    await page.goto('http://127.0.0.1:8780/', { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 120000 });
    console.log(JSON.stringify({ stage: 'record-battle' }));
    const result = await page.evaluate(async ({ reportId }) => {
      const profileKey = 'dongzhou-h5-profile-v2';
      const profile = JSON.parse(localStorage.getItem(profileKey));
      assertProfile(profile);
      const members = profile.organization.members;
      const councilMember = members[0];
      const orderMember = members[1] || members[0];
      const recorded = window.DongzhouOrganizationPlay.recordBattleOutcome(profile.organization, {
        id: reportId,
        stageId: '01',
        stageTitle: '繻葛之战',
        won: true,
        turns: 7,
        ownLosses: 1,
        terminalReason: 'acceptance',
        support: {
          sources: ['左传战策', '官署军议'],
          councils: [{ memberId: councilMember.id, memberName: councilMember.name, text: '先整军列，再击其薄处。' }],
          mandates: [],
          orders: [{ id: `support:${reportId}`, memberId: orderMember.id, source: '官署筹备' }],
        },
      });
      profile.organization = recorded.state;
      localStorage.setItem(profileKey, JSON.stringify(profile));
      const saved = await window.DongzhouIntegration.persist(profile);
      const session = JSON.parse(localStorage.getItem('dongzhou-integration-session-v1'));
      return {
        playerId: session.playerId,
        version: saved.version,
        reportId: recorded.report.id,
        participants: [councilMember, orderMember].map((member) => ({ id: member.id, name: member.name })),
      };

      function assertProfile(value) {
        if (!value?.organization || !Array.isArray(value.organization.members) || !value.organization.members.length) {
          throw new Error('organization_roster_unavailable');
        }
      }
    }, { reportId });

    console.log(JSON.stringify({ stage: 'reload-cloud-save', playerId: result.playerId }));
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 120000 });
    await page.click('#campaignOfficeButton');
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])');
    const archive = page.locator('#officeBattleArchive');
    await archive.scrollIntoViewIfNeeded();
    const archiveText = await archive.innerText();
    assert.match(archiveText, /繻葛之战告捷/);
    assert.match(archiveText, /左传战策/);
    assert(responses.some((entry) => entry.method === 'PUT' && entry.status === 200));
    assert.equal(errors.length, 0);

    fs.mkdirSync(path.dirname(evidencePath), { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const evidence = {
      result: 'PASS',
      mode: 'real-services-browser-no-interception',
      installationId,
      ...result,
      cloudReloadArchive: true,
      saveResponses: responses,
      screenshot: screenshotPath,
    };
    fs.writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);
    console.log(JSON.stringify({ ...evidence, evidence: evidencePath }));
  } catch (error) {
    fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
    await page.screenshot({
      path: screenshotPath.replace('.png', '-failure.png'),
      fullPage: true,
    }).catch(() => undefined);
    throw error;
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: 'FAIL', errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
