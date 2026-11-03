"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/index.html";
const outputDir = path.resolve(process.argv[3] || "output/qa-dialogue-audio");

async function run() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browserCandidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
  ].filter(Boolean);
  const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
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
    window.__dialogueAudioAudit = [];
    window.Audio = function AuditedAudio(source) {
      const audio = new NativeAudio(source);
      const nativePlay = audio.play.bind(audio);
      audio.play = () => {
        window.__dialogueAudioAudit.push({ source: audio.src, volume: audio.volume });
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
  await page.locator("#voiceVolume").fill("40");
  await page.locator("#voiceVolume").dispatchEvent("input");
  await page.locator("#focusStageButton").click();
  await page.locator("#storyModal").waitFor({ state: "visible" });
  const narratorVoiceHidden = await page.locator("#storyVoiceReplayButton").evaluate((element) => element.hidden);
  const narratorAudioCount = await page.evaluate(() => window.__dialogueAudioAudit.length);
  await page.locator("#storyNextButton").click();
  await page.locator("#storyNextButton").click();
  await page.locator("#storyNextButton").click();
  await page.locator("#storyNextButton").click();
  await page.locator("#storyVoiceReplayButton").waitFor({ state: "visible" });
  await page.waitForTimeout(500);

  const state = await page.evaluate(async () => {
    const manifest = await fetch("audio/dialogue-manifest.json").then((response) => response.json());
    const sample = manifest.entries.find((entry) => entry.speaker === "周宣王" && entry.text.startsWith("市井孩童"));
    const response = await fetch(sample.file);
    const bytes = (await response.arrayBuffer()).byteLength;
    return {
      speaker: document.querySelector("#storySpeaker")?.textContent,
      text: document.querySelector("#storyText")?.textContent,
      replayVisible: !document.querySelector("#storyVoiceReplayButton")?.hidden,
      replayDisabled: document.querySelector("#storyVoiceReplayButton")?.disabled,
      audioAudit: window.__dialogueAudioAudit,
      assetStatus: response.status,
      assetBytes: bytes,
      narrationExcluded: manifest.narrationExcluded,
      voicedNarrationCount: manifest.entries.filter((entry) => ["旁白", "史官", "原著", "军令"].includes(entry.speaker)).length
    };
  });
  await page.screenshot({ path: path.join(outputDir, "desktop-story-voice.png"), fullPage: true });

  await page.locator("#storyVoiceReplayButton").click();
  await page.waitForTimeout(200);
  const replayCount = await page.evaluate(() => window.__dialogueAudioAudit.length);

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await mobile.goto(baseUrl, { waitUntil: "networkidle" });
  await mobile.locator("#campaignScreen").waitFor({ state: "visible" });
  const mobileVoiceToggleVisible = await mobile.locator(".voice-setting").isVisible();
  await mobile.screenshot({ path: path.join(outputDir, "mobile-campaign-voice.png"), fullPage: true });
  await mobile.close();
  await browser.close();

  if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
  if (!narratorVoiceHidden || narratorAudioCount !== 0) throw new Error("Narration unexpectedly exposed or played character voice audio");
  if (state.speaker !== "周宣王" || !state.text.includes("市井孩童")) throw new Error("Did not reach the first voiced character entry");
  if (!state.narrationExcluded || state.voicedNarrationCount !== 0) throw new Error("Narration leaked into the character voice manifest");
  if (!state.replayVisible || state.replayDisabled) throw new Error("Replay control is not available");
  if (state.assetStatus !== 200 || state.assetBytes < 1000) throw new Error("Dialogue asset did not load");
  if (!state.audioAudit.length || !state.audioAudit[0].source.includes("audio/dialogue/full/")) throw new Error("Automatic character playback was not requested");
  if (Math.abs(state.audioAudit[0].volume - 0.4) > 0.01) throw new Error(`Voice volume was not applied: ${state.audioAudit[0].volume}`);
  if (replayCount < 2) throw new Error("Replay did not start a second playback");
  if (!mobileVoiceToggleVisible) throw new Error("Mobile voice toggle is hidden");

  console.log(JSON.stringify({ result: "PASS", narratorVoiceHidden, narratorAudioCount, ...state, replayCount, mobileVoiceToggleVisible }, null, 2));
}

run().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
