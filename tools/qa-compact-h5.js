"use strict";

const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright");

const root = path.resolve(process.argv[2] || "output/compact-preview-20261105-v2");
const outputDir = path.resolve(process.argv[3] || "output/qa-compact-h5");
const mime = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".ogg": "audio/ogg", ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml",
};

function startServer() {
  const server = http.createServer((request, response) => {
    const requestPath = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
    const relative = requestPath === "/" ? "index.html" : requestPath.replace(/^\/+/, "");
    const target = path.resolve(root, relative);
    if (!target.startsWith(root + path.sep) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
      response.writeHead(404).end("Not found");
      return;
    }
    response.writeHead(200, { "Content-Type": mime[path.extname(target).toLowerCase()] || "application/octet-stream" });
    fs.createReadStream(target).pipe(response);
  });
  return new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server)));
}

async function run() {
  fs.mkdirSync(outputDir, { recursive: true });
  const server = await startServer();
  const port = server.address().port;
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  ].filter(Boolean);
  const executablePath = candidates.find((candidate) => fs.existsSync(candidate));
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.addInitScript(() => {
      const NativeAudio = window.Audio;
      window.__compactAudioAudit = [];
      window.Audio = function CompactAuditedAudio(source) {
        const audio = new NativeAudio(source);
        const nativePlay = audio.play.bind(audio);
        audio.play = () => {
          window.__compactAudioAudit.push({ source: audio.src, loop: audio.loop });
          return nativePlay();
        };
        return audio;
      };
      window.Audio.prototype = NativeAudio.prototype;
    });

    const url = `http://127.0.0.1:${port}/index.html?v=20261105-27`;
    await page.goto(url, { waitUntil: "networkidle" });
    const campaign = await page.evaluate(() => fetch("scenario/campaign.json").then((response) => response.json()));
    const completed = campaign.stages.slice(0, 40).map((stage) => String(stage.id));
    const targetStage = campaign.stages[40];
    await page.evaluate(({ completed }) => {
      localStorage.setItem("dongzhou-h5-profile-v2", JSON.stringify({ completed, lastStage: null, tutorial: { completed: true, dismissed: true } }));
    }, { completed });
    await page.reload({ waitUntil: "networkidle" });
    await page.locator("#campaignScreen").waitFor({ state: "visible" });
    const focusedStage = await page.locator("#focusStageButton").getAttribute("data-stage-id");
    if (focusedStage !== String(targetStage.id)) throw new Error(`Expected stage ${targetStage.id}, focused ${focusedStage}`);
    await page.locator("#focusStageButton").click();
    await page.locator("#storyModal").waitFor({ state: "visible" });
    await page.waitForTimeout(3000);

    const result = await page.evaluate(async (stageId) => {
      const manifest = await fetch("audio/context-music-manifest.json").then((response) => response.json());
      const cue = manifest.cues.find((item) => item.stageId === stageId && item.kind === "intro");
      return { cue, audit: window.__compactAudioAudit.filter((item) => item.source.includes("audio/context-music/")) };
    }, String(targetStage.id));
    await page.screenshot({ path: path.join(outputDir, "compact-stage-41-fallback.png"), fullPage: true });

    if (pageErrors.length) throw new Error(`Browser errors:\n${pageErrors.join("\n")}`);
    if (!result.cue || result.cue.availableInBase !== false) throw new Error("Target cue is not an external compact cue");
    if (!result.cue.fallbackFile || result.cue.fallbackFile === result.cue.file) throw new Error("Target cue has no distinct fallback");
    if (!result.audit.some((item) => item.source.includes(result.cue.file))) throw new Error("Original chapter cue was not attempted");
    if (!result.audit.some((item) => item.source.includes(result.cue.fallbackFile))) throw new Error("Core fallback cue was not played");
    console.log(JSON.stringify({ result: "PASS", url, targetStage: targetStage.id, cue: result.cue.id, fallback: result.cue.fallbackFile, attempts: result.audit }, null, 2));
  } finally {
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

run().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
