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
