"""Versioned save-slot storage for the playable Mengde frontend."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SAVE_FORMAT = "mengde-battle-save"
SAVE_VERSION = 1
SLOT_COUNT = 6
STAGE_TABLE_VERSION = 13
CURRENT_DONGZHOU_STAGES = (
    "01","02","03","03b","04a","04","05","06","07","07b","08a","08","09","10a","10b","11a","11b","11c","12a","12b","13a","13b","14a","14b","15a","16","17","18","19a","19b","20a","20b","20c","20d","21a","21b","21c","22","23a","23b","24a","24b","25a","25b","26a","26b","27a","27b","28","29","30a","30b","31","32","33a","33b","34a","34b","35","36a","36b","38a","38b","39","40","42","43a","43b","44","45a","45b","46a","46b","46c","47a","47b","48a","48b","49","50a","50b","50c","51","52","53a","53b","54a","54b","55a","55b","56a","56b","57","58","59a","59b","60a","60b","60c","61a","61b","61c","62a","62b","62c","63a","63b","64a","64b","65a","65b","65c","66a","66b","66c","66d","66e","67a","67b","68","69"
)
LEGACY_STAGE_TITLES = {"乾时伏击":"15a","汶阳断后":"15a","邲之战":"54a","河口夺俘":"54b","城濮之战":"40","鄢陵交锋":"58","鄢陵之战":"58"}


def _migrate_stage_reference(payload: dict[str, Any]) -> None:
    if payload.get("scenario") != "dongzhou":
        return
    battle = payload.get("battle") or {}
    metadata = payload.get("metadata") or {}
    stage_id = str(battle.get("stage_id") or LEGACY_STAGE_TITLES.get(str(metadata.get("battle_title", "")), ""))
    if stage_id in CURRENT_DONGZHOU_STAGES:
        battle["stage_index"] = CURRENT_DONGZHOU_STAGES.index(stage_id)
        battle["stage_id"] = stage_id
    elif int(payload.get("stage_table_version", 1)) < 2:
        old_index = int(battle.get("stage_index", 0))
        battle["stage_index"] = old_index if old_index <= 24 else old_index - 1
    if str(metadata.get("battle_title", "")) == "汶阳断后":
        battle["stage_index"] = CURRENT_DONGZHOU_STAGES.index("15a")
        battle["stage_id"] = "15a"
        battle["_restart_merged_stage"] = True
    payload["stage_table_version"] = STAGE_TABLE_VERSION
if getattr(sys, "frozen", False):
    DEFAULT_SAVE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Ekgd" / "saves"
else:
    DEFAULT_SAVE_DIR = Path(__file__).resolve().parents[1] / "saves"


class SaveFormatError(ValueError):
    pass


def slot_path(slot: int, save_dir: Path = DEFAULT_SAVE_DIR) -> Path:
    if slot < 1 or slot > SLOT_COUNT:
        raise ValueError(f"save slot must be between 1 and {SLOT_COUNT}")
    return save_dir / f"slot_{slot:02d}.json"


def read_slot(slot: int, save_dir: Path = DEFAULT_SAVE_DIR) -> dict[str, Any] | None:
    path = slot_path(slot, save_dir)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SaveFormatError(f"存档损坏：{error}") from error
    if payload.get("format") != SAVE_FORMAT:
        raise SaveFormatError("不是东周列国志存档")
    if int(payload.get("version", 0)) != SAVE_VERSION:
        raise SaveFormatError("存档版本不兼容")
    if not isinstance(payload.get("battle"), dict):
        raise SaveFormatError("存档缺少战斗状态")
    _migrate_stage_reference(payload)
    return payload


def list_slots(save_dir: Path = DEFAULT_SAVE_DIR) -> list[dict[str, Any]]:
    slots = []
    for slot in range(1, SLOT_COUNT + 1):
        try:
            payload = read_slot(slot, save_dir)
            slots.append({"slot": slot, "payload": payload, "error": None})
        except SaveFormatError as error:
            slots.append({"slot": slot, "payload": None, "error": str(error)})
    return slots


def write_slot(slot: int, scenario: str, battle: dict[str, Any], metadata: dict[str, Any],
               ui_state: dict[str, Any], save_dir: Path = DEFAULT_SAVE_DIR) -> dict[str, Any]:
    save_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "scenario": scenario,
        "stage_table_version": STAGE_TABLE_VERSION,
        "saved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "metadata": metadata,
        "battle": dict(battle, stage_id=(CURRENT_DONGZHOU_STAGES[int(battle.get("stage_index", 0))] if scenario == "dongzhou" and 0 <= int(battle.get("stage_index", 0)) < len(CURRENT_DONGZHOU_STAGES) else battle.get("stage_id", ""))),
        "ui": ui_state,
    }
    destination = slot_path(slot, save_dir)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return payload
