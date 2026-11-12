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
      const hero = profile.organization.members[0];
      const stageTitle = `繻葛之战-${reportId.slice(-8)}`;
      const councilId = crypto.randomUUID();
      const question = '此战应当如何部署？';
      const options = ['稳守阵列', '整军进击'];
      const councilResponse = await fetch(`/api/dongzhou/v1/npcs/${encodeURIComponent(hero.id)}/decisions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_request_id: councilId,
          stage_id: '01',
          question,
          options: options.map((text, index) => ({ index, text })),
          topic: 'court_decision',
        }),
      });
      if (!councilResponse.ok) throw new Error(`council_failed:${councilResponse.status}`);
      const councilBody = await councilResponse.json();
      const decision = councilBody.decision?.data || councilBody.decision;
      if (decision?.type !== 'OPTION' || !Number.isInteger(decision.index)) throw new Error('council_decision_invalid');
      const council = {
        id: councilId,
        stageId: '01',
        memberId: hero.id,
        memberName: hero.name,
        question,
        options,
        index: decision.index,
        text: options[decision.index],
      };
      profile.organization.councils = [...(profile.organization.councils || []), council];
      profile.organization.pendingSupport = [...(profile.organization.pendingSupport || []), {
        id: `support:${reportId}`,
        stageId: '01',
        source: '实服军议',
        council,
      }];
      await window.DongzhouIntegration.persist(profile);
      const recorded = window.DongzhouOrganizationPlay.recordBattleOutcome(profile.organization, {
        id: reportId,
        stageId: '01',
        stageTitle,
        won: true,
        turns: 7,
        ownLosses: 1,
        terminalReason: 'acceptance',
        support: {
          sources: ['左传战策', '实服军议'],
          councils: [council],
          mandates: [],
          orders: [],
        },
      });
      const report = recorded.state.battleReports.find((entry) => entry.id === reportId);
      report.councils = [council];
      report.mandates = [];
      report.sources = ['左传战策', '实服军议'];
      report.support = { sources: report.sources, councils: [council], mandates: [], orders: [] };
      profile.organization = recorded.state;
      localStorage.setItem(profileKey, JSON.stringify(profile));
      const saved = await window.DongzhouIntegration.persist(profile);
      const sealedReport = saved.payload.organization.battleReports.find((entry) => entry.id === reportId);
      if (!sealedReport?.kernelReceipt?.digest) throw new Error('kernel_battle_receipt_missing');
      const session = JSON.parse(localStorage.getItem('dongzhou-integration-session-v1'));
      return {
        playerId: session.playerId,
        version: saved.version,
        reportId: recorded.report.id,
        hero: { id: hero.id, name: hero.name },
        stageTitle,
        receipt: sealedReport.kernelReceipt,
      };

      function assertProfile(value) {
        if (!value?.organization || !Array.isArray(value.organization.members) || !value.organization.members.length) {
          throw new Error('organization_roster_unavailable');
        }
      }
    }, { reportId });

    console.log(JSON.stringify({ stage: 'wait-authoritative-memory', hero: result.hero }));
    let matchedMemory = null;
    const memoryDeadline = Date.now() + 180000;
    while (Date.now() < memoryDeadline) {
      matchedMemory = await page.evaluate(async ({ heroId, stageTitle }) => {
        const response = await fetch(`/api/dongzhou/v1/npcs/${encodeURIComponent(heroId)}/state`);
        if (!response.ok) return null;
        const body = await response.json();
        return (body.memories?.items || []).find((item) =>
          String(item?.content || '').includes(stageTitle) && String(item?.content || '').includes('告捷')
        ) || null;
      }, { heroId: result.hero.id, stageTitle: result.stageTitle });
      if (matchedMemory) break;
      await page.waitForTimeout(3000);
    }
    assert(matchedMemory, `battle memory for ${result.stageTitle} was not persisted before timeout`);

    console.log(JSON.stringify({ stage: 'reload-cloud-save', playerId: result.playerId }));
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 120000 });
    await page.click('#campaignOfficeButton');
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])');
    await page.selectOption('#officeMemberSelect', result.hero.id);
    await page.waitForFunction(
      (stageTitle) => document.querySelector('#officeNpcMemories')?.innerText.includes(stageTitle),
      result.stageTitle,
      { timeout: 60000 },
    );
    const archive = page.locator('#officeBattleArchive');
    await archive.scrollIntoViewIfNeeded();
    const archiveText = await archive.innerText();
    assert(archiveText.includes(`${result.stageTitle}告捷`));
    assert.match(archiveText, /左传战策/);
    assert.equal(result.receipt.kernel.module, 'dongzhou_mandate_workflow');
    assert.equal(result.receipt.kernel.state, 'SEALED');
    assert.deepEqual(result.receipt.verifiedParticipants, [result.hero.id]);
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
      matchedMemory,
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
