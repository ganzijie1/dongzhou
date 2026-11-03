"use strict";

const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const report = JSON.parse(fs.readFileSync(path.join(root, "rl", "models", "mobile-candidate", "release-gate-v2.json"), "utf8"));
const metadata = JSON.parse(fs.readFileSync(path.join(root, "unity-remake", "Assets", "Resources", "Models", "HappoMobile.json"), "utf8"));
const runtime = fs.readFileSync(path.join(root, "web-game", "game.js"), "utf8");
const errors = [];

if (report.battle_stages !== 169) errors.push(`expected 169 battle stages, got ${report.battle_stages}`);
if (report.episodes_per_stage < 3) errors.push("HAPPO release gate requires at least three seeds per stage");
if (report.happo?.timeout_rate > 0.05) errors.push(`HAPPO timeout rate too high: ${report.happo.timeout_rate}`);
if (report.release_gate?.balanced_against_scripted_player !== false) errors.push("current overpowering result must remain explicitly marked as uncalibrated");
if (report.release_gate?.status !== "pass-with-runtime-calibration-required") errors.push(`unexpected gate status: ${report.release_gate?.status}`);
if (!Array.isArray(report.untrained_core_roles) || !report.untrained_core_roles.length) errors.push("untrained role coverage gap is missing");
if (!runtime.includes("TRAINED_HAPPO_ROLES") || !runtime.includes("difficulty-blend") || !runtime.includes("untrained-role")) errors.push("runtime difficulty blend or untrained-role fallback is missing");
if (metadata.release_evaluation?.episodes_per_stage !== report.episodes_per_stage) errors.push("ONNX metadata does not embed the v2 release report");

console.log(JSON.stringify({
  result: errors.length ? "FAIL" : "PASS",
  stages: report.battle_stages,
  episodesPerStage: report.episodes_per_stage,
  happoEpisodes: report.happo?.episodes,
  happoWinRate: report.happo?.enemy_win_rate,
  confidence95: report.happo?.enemy_win_rate_ci95,
  timeoutRate: report.happo?.timeout_rate,
  trainedRoles: report.trained_roles,
  untrainedCoreRoles: report.untrained_core_roles,
  status: report.release_gate?.status,
  errors
}, null, 2));
if (errors.length) process.exitCode = 1;
