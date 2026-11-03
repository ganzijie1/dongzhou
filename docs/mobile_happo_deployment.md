# Mobile HAPPO deployment

The mobile runtime performs frozen inference only. Training stays in Python,
and the Web battle rules remain authoritative for legal actions and fallback.
The phone never updates the deep policy. Local personalization is limited to a
deletable three-arm difficulty bandit stored in the player profile.

## Pipeline

The current APK uses an Android WebView shell, Java ONNX Runtime bridge,
Android API 36, JDK 21, and ARM64. The build emits an APK and adjacent build
JSON containing both ONNX hashes. Unity remains a separate remake path and is
not the runtime used by this APK.

1. Train a checkpoint with `rl.train_happo_dongzhou`.
2. Export one role-conditioned ONNX model with `rl.export_happo_mobile`.
3. Place the model under
   `unity-remake/Assets/Resources/Models/HappoMobile.onnx`.
4. `HappoBridge` verifies and loads the model, then exposes only legal candidate
   selection to the local WebView.
5. Feed the same 20 local features and 34 candidate features used by Python.
6. Treat the returned value as an index into the already validated legal list.

Dongzhou currently has 108 narrative chapters and 172 registered stage entries
because split chapters use suffixes such as `a`, `b`, and `c`. The stage folder
has 172 Lua files, including the independently registered `15b.lua`. Training and
release evaluation default to all 172 entries, then skip story-only
entries.

The runtime accepts at most 256 candidates and 11 role indices in this order:
`Lord`, `King`, `Infantry`, `Cavalry`, `Archer`, `Strategist`, `Support`,
`Artillery`, `Fighter`, `Bandit`, `Other`.

The checkpoint records roles observed during updates. The current checkpoint
trained `King`, `Infantry`, `Cavalry`, and `Strategist`. The Web runtime refuses
neural inference for all other roles and uses the deterministic rule fallback.
Easy, medium, and hard battles allow the trained policy to control roughly
30%, 65%, and 100% of eligible enemy decisions respectively.

Every enemy decision records schema, policy and runtime versions, legal action
count, selected controller, and fallback reason. Because the ONNX policy uses
deterministic argmax, the log leaves action probability null rather than
inventing a probability. Battle summaries and decomposed rewards stay local,
can be exported, can be disabled, and can be deleted without losing progress.
The v4 player profile also stores coins, persistent supplies, four equipment
slots, per-hero mastery, and at most 20 versioned action replays. None of these
records leave the device automatically.

## Export

```powershell
python -m rl.export_happo_mobile `
  --checkpoint rl/models/mobile-candidate/happo.pt `
  --output unity-remake/Assets/Resources/Models/HappoMobile.onnx `
  --metadata unity-remake/Assets/Resources/Models/HappoMobile.json `
  --release-report rl/models/mobile-candidate/release-gate.json
```

The exporter fails when ONNX and PyTorch choose different actions or when the
maximum absolute logit error exceeds `1e-4`. The metadata benchmark is a host
sanity check, not a substitute for measurements on Android devices.

## Android build

Install Unity 2022.3.62f3 with Android Build Support, SDK, NDK, and OpenJDK.
Then run:

```powershell
.\tools\build-unity-android.ps1
```

The automated build uses IL2CPP, ARM64, API 26 or newer, and produces
`unity-remake/Builds/Android/Dongzhou.apk` by default.

## Release gate

- ONNX/PyTorch parity passes for all roles.
- The policy only selects an action already marked legal.
- Missing model, invalid input, inference failure, invalid output, and budget
  overrun return the first legal action deterministically.
- P50/P95/P99 latency, peak memory, battery, temperature, throttling, and frame
  time are measured on at least one low, middle, and high tier Android device.
- The v2 gate covers 169 battle stages with three seeds per stage: 507 scripted
  baseline episodes and 507 HAPPO episodes. The scripted baseline timed out in
  every episode; HAPPO won every episode with a 95% Wilson interval of
  `[0.99248, 1.0]` and no timeout.
- This proves stable dominance of the weak baseline, not player-facing balance.
  The release status is `pass-with-runtime-calibration-required`; difficulty
  blending and untrained-role fallback are mandatory until human calibration.
