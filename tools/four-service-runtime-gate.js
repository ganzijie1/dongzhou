"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const VERIFIER = path.join(__dirname, "verify_four_service_runtime.py");

function defaultPython() {
  const configured = process.env.DONGZHOU_PYTHON;
  if (configured) return configured;
  const bundled = path.join(ROOT, "integration-service", ".venv", "Scripts", "python.exe");
  return fs.existsSync(bundled) ? bundled : "python";
}

function verifyFourServiceRuntime(url, options = {}) {
  const base = String(url || "").replace(/\/+$/, "");
  if (!/^https?:\/\//.test(base)) throw new Error("Four-service gate requires an HTTP gateway URL");
  const python = options.pythonPath || defaultPython();
  const runner = options.runner || spawnSync;
  const result = runner(python, [VERIFIER, "--url", base], {
    cwd: ROOT,
    encoding: "utf8",
    windowsHide: true,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    const detail = String(result.stderr || result.stdout || "unknown verification failure").trim();
    throw new Error(`Four-service runtime gate failed: ${detail}`);
  }
  let report;
  try {
    report = JSON.parse(result.stdout);
  } catch (_) {
    throw new Error("Four-service runtime gate returned invalid JSON");
  }
  if (report.result !== "PASS") throw new Error("Four-service runtime gate did not pass");
  return report;
}

module.exports = { verifyFourServiceRuntime };
