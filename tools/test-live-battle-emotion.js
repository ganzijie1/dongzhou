'use strict';

const assert = require('assert/strict');
const { createHash, randomUUID } = require('crypto');
const fs = require('fs');
const path = require('path');

let chromium;
try {
  ({ chromium } = require(path.resolve(__dirname, '../output/playwright-runtime/node_modules/playwright')));
} catch (_) {
  ({ chromium } = require('playwright'));
}

const root = path.resolve(__dirname, '..');
const evidencePath = path.join(root, 'output', 'integration-validation', 'live-battle-receipt-complete85.json');
const screenshotPath = path.join(root, 'output', 'integration-validation', 'live-battle-receipt-complete85.png');
const installationId = randomUUID();
const reportId = `battle:receipt-complete85:${Date.now()}`;
const executablePath = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
].find(fs.existsSync);

function sha256(value) {
  return createHash('sha256').update(value, 'utf8').digest('hex');
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
  await context.addInitScript((id) => {
    localStorage.setItem('dongzhou-installation-id-v1', id);
  }, installationId);
  const page = await context.newPage();
  const errors = [];
  const saveResponses = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('response', (response) => {
    if (new URL(response.url()).pathname.endsWith('/save')) {
      saveResponses.push({ method: response.request().method(), status: response.status() });
    }
  });

  try {
    console.log(JSON.stringify({ stage: 'startup', installationId }));
    await page.goto('http://127.0.0.1:8780/', { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 120000 });

    const result = await page.evaluate(async ({ reportId }) => {
      const profileKey = 'dongzhou-h5-profile-v2';
      const profile = JSON.parse(localStorage.getItem(profileKey));
      if (!profile?.organization?.members?.length) throw new Error('organization_roster_unavailable');
      const hero = profile.organization.members[0];
      const councilId = crypto.randomUUID();
      const councilQuestion = 'How should the campaign be supported?';
      const councilOptions = ['Hold formation', 'Advance'];
      const councilResponse = await fetch(`/api/dongzhou/v1/npcs/${encodeURIComponent(hero.id)}/decisions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_request_id: councilId,
          stage_id: '01',
          question: councilQuestion,
          options: councilOptions.map((text, index) => ({ index, text })),
          topic: 'court_decision',
        }),
      });
      if (!councilResponse.ok) throw new Error(`council_failed:${councilResponse.status}`);
      const councilResult = await councilResponse.json();
      const selected = councilResult.decision?.data || councilResult.decision;
      if (selected?.type !== 'OPTION' || !Number.isInteger(selected.index)) throw new Error('council_decision_invalid');
      const council = {
        id: councilId,
        stageId: '01',
        memberId: hero.id,
        memberName: hero.name,
        question: councilQuestion,
        options: councilOptions,
        index: selected.index,
        text: councilOptions[selected.index],
      };
      profile.organization.councils = [...(profile.organization.councils || []), council];
      profile.organization.pendingSupport = [...(profile.organization.pendingSupport || []), {
        id: `support:${reportId}`,
        stageId: '01',
        source: 'Campaign support',
        council,
      }];
      await window.DongzhouIntegration.persist(profile);
      const recorded = window.DongzhouOrganizationPlay.recordBattleOutcome(profile.organization, {
        id: reportId,
        stageId: '01',
        stageTitle: '繻葛之战',
        won: true,
        turns: 6,
        ownLosses: 1,
        terminalReason: 'acceptance',
        support: {
          sources: ['左传战策', '官署军议'],
          councils: [{ memberId: hero.id, memberName: hero.name, text: '整军奋击，克敌告捷。' }],
          mandates: [],
          orders: [{ id: `support:${reportId}`, memberId: hero.id, source: '官署筹备' }],
        },
      });
      const report = recorded.state.battleReports.find((entry) => entry.id === reportId);
      report.councils = [council];
      report.mandates = [];
      report.sources = ['Campaign support', 'Sealed council'];
      report.support = {
        sources: report.sources,
        councils: [council],
        mandates: [],
        orders: [],
      };
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
        receipt: sealedReport.kernelReceipt,
      };
    }, { reportId });

    assert.deepEqual(result.receipt.verifiedParticipants, [result.hero.id]);
    assert.equal(result.receipt.verifiedSupport.councils.length, 1);
    assert.deepEqual(result.receipt.rejectedSupport, []);

    const identityDigest = sha256(`${result.playerId}\n${result.reportId}\n${result.hero.id}`);
    const outcomeDigest = sha256(`${identityDigest}\nbattle-semantics-v3\n${result.receipt.digest}`);
    let expectedEventId = Number(BigInt(`0x${outcomeDigest.slice(0, 8)}`) & 0x7fffffffn);
    if (expectedEventId === 0) expectedEventId = 1;
    console.log(JSON.stringify({ stage: 'wait-authoritative-emotion', expectedEventId, hero: result.hero }));

    let stateBody;
    let matchedEmotion;
    const deadline = Date.now() + 180000;
    while (Date.now() < deadline) {
      const checked = await page.evaluate(async ({ heroId, expectedEventId }) => {
        const response = await fetch(`/api/dongzhou/v1/npcs/${encodeURIComponent(heroId)}/state`);
        const body = await response.json();
        const payload = body?.emotion?.data ?? body?.emotion ?? {};
        const candidates = [
          ...(Array.isArray(payload) ? payload : []),
          ...(Array.isArray(payload.items) ? payload.items : []),
          ...(Array.isArray(payload.emotions) ? payload.emotions : []),
          ...(Array.isArray(payload.current_emotions) ? payload.current_emotions : []),
        ];
        const matched = candidates.find((item) =>
          String(item?.related_event_id ?? item?.relatedEventId ?? '') === String(expectedEventId)
        );
        return { status: response.status, body, matched };
      }, { heroId: result.hero.id, expectedEventId });
      stateBody = checked.body;
      matchedEmotion = checked.matched;
      if (checked.status === 200 && matchedEmotion) break;
      await page.waitForTimeout(3000);
    }

    assert(matchedEmotion, `event ${expectedEventId} emotion was not persisted before timeout`);
    assert.equal(matchedEmotion.emotion_type ?? matchedEmotion.emotionType, 'joy');
    const persistedIntensity = Number(matchedEmotion.intensity);
    assert.equal(persistedIntensity, 78);
    assert.equal(matchedEmotion.trigger_level ?? matchedEmotion.triggerLevel, 'strong');
    assert.equal(matchedEmotion.trigger_reason ?? matchedEmotion.triggerReason, 'standard event protect/support: success');

    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#app:not([hidden])', { timeout: 120000 });
    await page.click('#campaignOfficeButton');
    await page.waitForSelector('#campaignOfficeBackdrop:not([hidden])');
    await page.selectOption('#officeMemberSelect', result.hero.id);
    await page.waitForFunction((intensity) => {
      const text = document.querySelector('#officeNpcState')?.innerText || '';
      return text.includes(`joy ${intensity}`);
    }, persistedIntensity, { timeout: 60000 });
    const stateText = await page.locator('#officeNpcState').innerText();
    const archiveText = await page.locator('#officeBattleArchive').innerText();
    assert(stateText.includes(`joy ${persistedIntensity}`));
    assert(archiveText.includes('内核战果印记'));
    assert(archiveText.includes(result.receipt.digest.slice(0, 12)));
    assert.equal(errors.length, 0);
    assert(saveResponses.some((entry) => entry.method === 'PUT' && entry.status === 200));

    await page.locator('#officeBattleArchive').scrollIntoViewIfNeeded();
    fs.mkdirSync(path.dirname(evidencePath), { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
    const evidence = {
      result: 'PASS',
      mode: 'real-services-browser-no-interception',
      installationId,
      ...result,
      expectedEventId,
      emotion: matchedEmotion,
      cloudStateHeroId: stateBody.heroId,
      saveResponses,
      officeRendered: stateText.includes(`joy ${persistedIntensity}`),
      receiptRendered: archiveText.includes(result.receipt.digest.slice(0, 12)),
      screenshot: screenshotPath,
    };
    fs.writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);
    console.log(JSON.stringify({ ...evidence, evidence: evidencePath }));
  } catch (error) {
    fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
    await page.screenshot({ path: screenshotPath.replace('.png', '-failure.png'), fullPage: true }).catch(() => undefined);
    throw error;
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(JSON.stringify({ result: 'FAIL', errorType: error.name, message: error.message }));
  process.exitCode = 1;
});
