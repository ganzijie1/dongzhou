"use strict";

const assert = require("assert/strict");
const { verifyFourServiceRuntime } = require("./four-service-runtime-gate");

const calls = [];
const passed = verifyFourServiceRuntime("http://127.0.0.1:8766/", {
  pythonPath: "python-test",
  runner(command, args, options) {
    calls.push({ command, args, options });
    return { status: 0, stdout: JSON.stringify({ result: "PASS", checks: { liveRuntime: { onlineServices: 4 } } }), stderr: "" };
  },
});
assert.equal(passed.checks.liveRuntime.onlineServices, 4);
assert.equal(calls[0].command, "python-test");
assert.deepEqual(calls[0].args.slice(-2), ["--url", "http://127.0.0.1:8766"]);

assert.throws(() => verifyFourServiceRuntime("http://127.0.0.1:8766", {
  runner: () => ({ status: 1, stdout: "", stderr: "source drift" }),
}), /source drift/);
assert.throws(() => verifyFourServiceRuntime("file:///tmp/game", {
  runner: () => ({ status: 0, stdout: "{}", stderr: "" }),
}), /HTTP gateway URL/);

console.log("PASS: JavaScript live acceptance uses the canonical four-service runtime gate");
