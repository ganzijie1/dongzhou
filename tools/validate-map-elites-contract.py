"""Run the battle-map contract validator with Dongzhou's shallow-river code."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path.home() / ".codex/skills/mengde-build-battle-maps/scripts/validate_map_contract.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("map_contract_validator", VALIDATOR)
    if spec is None or spec.loader is None: raise RuntimeError(f"validator unavailable: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ALLOWED_TERRAIN.add("v")
    report = module.validate(
        ROOT / "output/map-elites-chuisha/map-contract.json",
        ROOT,
        ROOT / "web-game/scenario/stage/map_elites_chuisha.lua",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]: raise SystemExit(1)


if __name__ == "__main__":
    main()
