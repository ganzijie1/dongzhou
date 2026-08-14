from copy import deepcopy
from pathlib import Path
import json
import tempfile

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION, read_slot

ROOT = Path(__file__).resolve().parents[1]


def write_old_slot(folder, title, index):
    payload = {
        "format":"mengde-battle-save","version":1,"scenario":"dongzhou",
        "saved_at":"2026-01-01T00:00:00+08:00",
        "metadata":{"chapter":"第十五回·下","battle_title":title},
        "battle":{"stage_index":index,"money":777,"turn_current":3,"current_force":1,"agent_actions":0,"truncated":False,"units":[],"inventory":{"medicine":2},"commander_progress":{}},
        "ui":{}
    }
    (folder / "slot_01.json").write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")


def test_save_migration():
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td)
        write_old_slot(folder,"汶阳断后",25)
        payload=read_slot(1,folder)
        assert payload["stage_table_version"] == STAGE_TABLE_VERSION
        assert payload["battle"]["stage_id"] == "15a"
        assert payload["battle"]["stage_index"] == CURRENT_DONGZHOU_STAGES.index("15a") == 24
        assert payload["battle"]["_restart_merged_stage"] is True
        write_old_slot(folder,"未登记旧关",26)
        payload=read_slot(1,folder)
        assert payload["battle"]["stage_index"] == 25


def test_stage_table_and_scripts():
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    stage=(ROOT/"game/sce/dongzhou/stage/15a.lua").read_text(encoding="utf-8")
    audit=(ROOT/"docs/battle_merge_audit.md").read_text(encoding="utf-8")
    assert '"14a", "14b", "15a", "16"' in config
    assert '"15a", "15b", "16"' not in config
    assert tuple(CURRENT_DONGZHOU_STAGES)[24:26] == ("15a","16")
    assert 'battle_title = "乾时之战"' in stage
    assert "pursuit_phase = true" in stage
    assert 'set_unit_invulnerable("QinZi15", false)' in stage
    assert "if qinzi_fallen then return Enum.status.victory end" in stage
    assert "城濮之战" in audit and "鄢陵之战" in audit and "邲之战" in audit
    assert "玩家控制楚军" in audit


def test_engine_load_and_legacy_restart():
    exe=ROOT/"build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
    with MengdeEnv(exe,scenario="dongzhou",interactive=True) as env:
        env._request("LOAD_STAGE 24")
        assert env.story_info()["battle_title"] == "乾时之战"
        legacy=env.snapshot()
        legacy.update(stage_index=24,money=777,_restart_merged_stage=True)
        _,info=env.restore(legacy)
        assert env.story_info()["battle_title"] == "乾时之战"
        assert info["turn_current"] == 1
        env._request("LOAD_STAGE 25")
        assert env.story_info()["battle_title"] == "长勺鼓阵"


if __name__ == "__main__":
    test_save_migration();test_stage_table_and_scripts();test_engine_load_and_legacy_restart()
    print("battle merge regression checks passed")