from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import zipfile


SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "check-local-delivery.py"
SPEC = spec_from_file_location("check_local_delivery", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


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
    with zipfile.ZipFile(package, "a") as archive:
        archive.writestr("scenario/removed-stage.json", b"stale")
    extra = CHECKER.check_package_sources(package, {}, tmp_path, contract)
    assert extra[0]["passed"] is False
    assert extra[0]["mismatches"] == ["extra:scenario/removed-stage.json"]
