from importlib.util import module_from_spec, spec_from_file_location
import hashlib
import json
from pathlib import Path
import time
import zipfile


SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "check-local-delivery.py"
SPEC = spec_from_file_location("check_local_delivery", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def _append_package_file(package: Path, name: str, content: bytes) -> None:
    for attempt in range(20):
        try:
            with zipfile.ZipFile(package, "a") as archive:
                archive.writestr(name, content)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)


def test_package_source_contract_detects_stale_gameplay_file(tmp_path: Path) -> None:
    source = tmp_path / "web-game" / "game.js"
    source.parent.mkdir(parents=True)
    source.write_text("current gameplay", encoding="utf-8")
    package = tmp_path / "dongzhou.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("game.js", source.read_bytes())

    contract = {"web-game/game.js": "game.js"}
    current = CHECKER.check_package_sources(package, contract, tmp_path)
    assert current[0]["passed"] is True

    source.write_text("new gameplay not packaged", encoding="utf-8")
    stale = CHECKER.check_package_sources(package, contract, tmp_path)
    assert stale[0]["passed"] is False
    assert stale[0]["sourceSha256"] != stale[0]["packageSha256"]


def test_package_source_tree_detects_changed_and_extra_scenario_files(tmp_path: Path) -> None:
    scenario = tmp_path / "web-game" / "scenario"
    scenario.mkdir(parents=True)
    stage = scenario / "stage.json"
    stage.write_text('{"stage": 1}', encoding="utf-8")
    package = tmp_path / "dongzhou.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("scenario/stage.json", stage.read_bytes())

    contract = {"web-game/scenario": "scenario"}
    current = CHECKER.check_package_sources(package, {}, tmp_path, contract)
    assert current[0]["passed"] is True
    assert current[0]["files"] == 1

    stage.write_text('{"stage": 2}', encoding="utf-8")
    changed = CHECKER.check_package_sources(package, {}, tmp_path, contract)
    assert changed[0]["passed"] is False
    assert changed[0]["mismatches"] == ["hash:scenario/stage.json"]

    stage.write_text('{"stage": 1}', encoding="utf-8")
    _append_package_file(package, "scenario/removed-stage.json", b"stale")
    extra = CHECKER.check_package_sources(package, {}, tmp_path, contract)
    assert extra[0]["passed"] is False
    assert extra[0]["mismatches"] == ["extra:scenario/removed-stage.json"]


def test_manifest_file_set_verifies_declared_source_and_package_hashes(tmp_path: Path) -> None:
    audio = tmp_path / "web-game" / "audio" / "dialogue"
    audio.mkdir(parents=True)
    clip = audio / "line.ogg"
    clip.write_bytes(b"voice")
    digest = hashlib.sha256(clip.read_bytes()).hexdigest()
    manifest = tmp_path / "web-game" / "audio" / "dialogue-manifest.json"
    manifest.write_text(
        json.dumps({"entries": [{"file": "audio/dialogue/line.ogg", "sha256": digest}]}),
        encoding="utf-8",
    )
    package = tmp_path / "dongzhou.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("audio/dialogue/line.ogg", clip.read_bytes())

    contract = [{
        "manifest": "web-game/audio/dialogue-manifest.json",
        "sourceRoot": "web-game",
        "items": "entries",
        "archivePrefix": "audio/dialogue",
    }]
    current = CHECKER.check_package_sources(package, {}, tmp_path, manifest_file_sets=contract)
    assert current[0]["passed"] is True
    assert current[0]["files"] == 1

    clip.write_bytes(b"changed voice")
    changed = CHECKER.check_package_sources(package, {}, tmp_path, manifest_file_sets=contract)
    assert changed[0]["passed"] is False
    assert changed[0]["mismatches"] == ["source-hash:audio/dialogue/line.ogg"]

    clip.write_bytes(b"voice")
    _append_package_file(package, "audio/dialogue/stale.ogg", b"stale")
    extra = CHECKER.check_package_sources(package, {}, tmp_path, manifest_file_sets=contract)
    assert extra[0]["passed"] is False
    assert extra[0]["mismatches"] == ["extra:audio/dialogue/stale.ogg"]


def _healthy_readiness() -> dict:
    names = list(CHECKER.four_service_delivery.SERVICE_NAMES)
    return {
        "status": "healthy",
        "requiredServices": names,
        "unavailableServices": [],
        "sourceDriftServices": [],
        "services": {name: {"online": True} for name in names},
    }


def test_readiness_contract_accepts_the_canonical_four_services() -> None:
    names = list(CHECKER.four_service_delivery.SERVICE_NAMES)
    result = CHECKER.check_readiness_contract(_healthy_readiness(), names)

    assert result["passed"] is True
    assert result["manifestMatchesCanonicalServices"] is True
    assert result["sourceDriftServices"] == []


def test_readiness_contract_rejects_source_drift() -> None:
    names = list(CHECKER.four_service_delivery.SERVICE_NAMES)
    readiness = _healthy_readiness()
    readiness["status"] = "unhealthy"
    readiness["sourceDriftServices"] = ["aiNpc"]
    readiness["services"]["aiNpc"] = {"online": False}

    result = CHECKER.check_readiness_contract(readiness, names)

    assert result["passed"] is False
    assert result["error"] == "integration gateway readiness is not healthy"
