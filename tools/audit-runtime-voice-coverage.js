"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const STAGES = path.join(ROOT, "web-game", "scenario", "stage");
const MANIFEST = path.join(ROOT, "web-game", "audio", "dialogue-manifest.json");
const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
const voicedTexts = new Set((manifest.entries || []).map((entry) => String(entry.text || "")));
const calls = [];
const pattern = /push_cmd_speak\s*\(\s*([^,]+)\s*,\s*"((?:[^"\\]|\\.)*)"\s*\)/g;

for (const file of fs.readdirSync(STAGES).filter((name) => name.endsWith(".lua")).sort()) {
  const source = fs.readFileSync(path.join(STAGES, file), "utf8");
  let match;
  while ((match = pattern.exec(source))) {
    calls.push({ file, reference: match[1].trim(), text: match[2].replace(/\\"/g, '"') });
  }
}

const missing = calls.filter((call) => !voicedTexts.has(call.text));
const characterMissing = missing.filter((call) => !/^(?:0|1|2|3|nil)$/.test(call.reference));
const result = {
  result: missing.length ? "FAIL" : "PASS",
  runtimeSpeechCalls: calls.length,
  uniqueRuntimeTexts: new Set(calls.map((call) => call.text)).size,
  coveredCalls: calls.length - missing.length,
  missingCalls: missing.length,
  missingCharacterCalls: characterMissing.length,
  missingSystemCalls: missing.length - characterMissing.length,
  characterMissing,
  systemMissing: missing.filter((call) => !characterMissing.includes(call))
};
console.log(JSON.stringify(result, null, 2));
if (missing.length) process.exitCode = 1;
