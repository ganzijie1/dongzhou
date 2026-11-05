"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/index.html";
const outputDir = path.resolve(process.argv[3] || "output/qa-contextual-music");

async function run() {
  fs.mkdirSync(outputDir, { recursive: true });
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
  ].filter(Boolean);
  const executablePath = candidates.find((candidate) => fs.existsSync(candidate));
  const browser = await chromium.launch({ headless: true, executablePath });
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
  const errors = [];
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("requestfailed", (request) => {
    const reason = request.failure()?.errorText || "failed";
    if (reason !== "net::ERR_ABORTED") errors.push(`${request.url()} ${reason}`);
  });
  await page.addInitScript(() => {
    const NativeAudio = window.Audio;
    window.__contextAudioAudit = [];
    window.__contextAudioInstances = [];
    window.Audio = function AuditedAudio(source) {
      const audio = new NativeAudio(source);
      const nativePlay = audio.play.bind(audio);
      window.__contextAudioInstances.push(audio);
      audio.play = () => {
        window.__contextAudioAudit.push({ source: audio.src, volume: audio.volume, loop: audio.loop });
        return nativePlay();
      };
      return audio;
    };
    window.Audio.prototype = NativeAudio.prototype;
  });

  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle" });
  await page.locator("#campaignScreen").waitFor({ state: "visible" });
  await page.locator("#campaignSettingsButton").click();
  await page.locator("#campaignUtilityPanel").waitFor({ state: "visible" });
  const musicControlsVisible = await page.locator(".music-setting").isVisible()
    && await page.locator(".music-volume-setting").isVisible();
  await page.locator("#campaignSettingsCloseButton").click();
  await page.locator("#focusStageButton").click();
  await page.locator("#storyModal").waitFor({ state: "visible" });
  await page.waitForTimeout(2600);
  const intro = await page.evaluate(() => {
    const music = window.__contextAudioInstances.filter((audio) => audio.src.includes("audio/context-music/"));
    const current = music.at(-1);
    return { audit: window.__contextAudioAudit, source: current?.src || "", volume: current?.volume ?? -1, loop: current?.loop };
  });

  for (let index = 0; index < 4; index++) await page.locator("#storyNextButton").click();
  await page.locator("#storyVoiceReplayButton").waitFor({ state: "visible" });
  await page.waitForTimeout(200);
  const ducked = await page.evaluate(() => {
    const music = window.__contextAudioInstances.filter((audio) => audio.src.includes("audio/context-music/"));
    return music.at(-1)?.volume ?? -1;
  });

  await page.locator("#storySkipButton").click();
  await page.waitForTimeout(1300);
  const battle = await page.evaluate(async () => {
    const manifest = await fetch("audio/context-music-manifest.json").then((response) => response.json());
    const music = window.__contextAudioInstances.filter((audio) => audio.src.includes("audio/context-music/"));
    const current = music.at(-1);
    const stage = manifest.cues.filter((cue) => cue.stageId === "01");
    const runtimeCue = manifest.cues.find((cue) => cue.section === "runtime" && cue.triggerText);
    const normalized = window.DongzhouGameSystems.normalizeMusicManifest(manifest);
    const runtimeResolved = window.DongzhouGameSystems.resolveContextMusic(normalized, {
      stageId: runtimeCue.stageId, section: "runtime", text: runtimeCue.triggerText
    });
    const duplicateText = "东宫门就在前方。不要恋战，穿门后继续向东，我在外侧接应！";
    const duplicateCues = manifest.cues.filter((cue) => cue.stageId === "57" && cue.kind === "event" && cue.triggerText === duplicateText);
    const duplicateResolved = window.DongzhouGameSystems.resolveContextMusic(normalized, {
      stageId: "57", section: "runtime", text: duplicateText
    });
    const runtimeResponse = await fetch(runtimeCue.file);
    const runtimeBytes = (await runtimeResponse.arrayBuffer()).byteLength;
    const fetched = await Promise.all(stage.map(async (cue) => {
      const response = await fetch(cue.file);
      return { id: cue.id, status: response.status, bytes: (await response.arrayBuffer()).byteLength };
    }));
    return {
      source: current?.src || "", volume: current?.volume ?? -1, loop: current?.loop,
      totalCues: manifest.cues.length, stageCueCount: stage.length, fetched,
      runtimeResolvedId: runtimeResolved?.id || "", runtimeCueId: runtimeCue.id,
      runtimeStatus: runtimeResponse.status, runtimeBytes,
      duplicateCueCount: duplicateCues.length,
      duplicateExpectedId: duplicateCues[0]?.id || "",
      duplicateResolvedId: duplicateResolved?.id || "",
      requested: window.__contextAudioAudit.filter((item) => item.source.includes("audio/context-music/"))
    };
  });
  await page.screenshot({ path: path.join(outputDir, "desktop-battle-music.png"), fullPage: true });

  await browser.close();
  if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
  if (!musicControlsVisible) throw new Error("Music controls are hidden");
  if (!intro.source.includes("/audio/context-music/01/story-intro.ogg") || intro.loop) throw new Error("Intro cue did not start as a one-shot");
  if (Math.abs(intro.volume - 0.42) > 0.03) throw new Error(`Intro volume was not applied: ${intro.volume}`);
  if (Math.abs(ducked - 0.42 * 0.28) > 0.03) throw new Error(`Dialogue ducking was not applied: ${ducked}`);
  if (!battle.source.includes("/audio/context-music/01/battle.ogg") || !battle.loop) throw new Error("Battle loop did not replace the intro cue");
  if (Math.abs(battle.volume - 0.42) > 0.03) throw new Error(`Battle volume was not restored: ${battle.volume}`);
  if (battle.totalCues !== 1126 || battle.stageCueCount !== 6) throw new Error("Contextual music manifest coverage is stale");
  if (battle.runtimeResolvedId !== battle.runtimeCueId || battle.runtimeStatus !== 200 || battle.runtimeBytes < 1024) throw new Error("Lua runtime music did not resolve or load");
  if (battle.duplicateCueCount < 2 || battle.duplicateResolvedId !== battle.duplicateExpectedId) throw new Error("Duplicate runtime text did not resolve to a deterministic music cue");
  if (battle.fetched.some((item) => item.status !== 200 || item.bytes < 1024)) throw new Error("A stage 01 cue failed to load");
  console.log(JSON.stringify({ result: "PASS", musicControlsVisible, intro, ducked, battle }, null, 2));
}

run().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
