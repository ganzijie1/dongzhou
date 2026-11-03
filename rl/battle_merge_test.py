from copy import deepcopy
from pathlib import Path
import json
import tempfile

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION, read_slot

ROOT = Path(__file__).resolve().parents[1]


def write_old_slot(folder, title, index, table_version=1):
    payload = {
        "format":"mengde-battle-save","version":1,"scenario":"dongzhou",
        "stage_table_version":table_version,
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
        assert payload["battle"]["stage_id"] == "15b"
        assert payload["battle"]["stage_index"] == CURRENT_DONGZHOU_STAGES.index("15b") == 25
        write_old_slot(folder,"未登记旧关",25,table_version=18)
        payload=read_slot(1,folder)
        assert payload["battle"]["stage_index"] == 26


def test_stage_table_and_scripts():
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    stage_a=(ROOT/"game/sce/dongzhou/stage/15a.lua").read_text(encoding="utf-8")
    stage_b=(ROOT/"game/sce/dongzhou/stage/15b.lua").read_text(encoding="utf-8")
    audit=(ROOT/"docs/battle_merge_audit.md").read_text(encoding="utf-8")
    assert '"14a", "14b", "15a", "15b", "16"' in config
    assert tuple(CURRENT_DONGZHOU_STAGES)[24:27] == ("15a","15b","16")
    assert 'battle_title = "乾时之战"' in stage_a
    assert "pursuit_phase" not in stage_a
    assert 'battle_title = "汶阳断后"' in stage_b
    assert 'title_id = "WenyangRearGuard"' in stage_b
    assert 'if game:get_num_enemies_alive() == 0 then return Enum.status.victory end' in stage_b
    assert "城濮之战" in audit and "鄢陵之战" in audit and "邲之战" in audit
    assert "玩家控制楚军" in audit


def test_engine_load_registered_stages():
    exe=ROOT/"build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
    with MengdeEnv(exe,scenario="dongzhou",interactive=True) as env:
        env._request("LOAD_STAGE 24")
        assert env.story_info()["battle_title"] == "乾时之战"
        env._request("LOAD_STAGE 25")
        assert env.story_info()["battle_title"] == "汶阳断后"
        env._request("LOAD_STAGE 26")
        assert env.story_info()["battle_title"] == "长勺鼓阵"


if __name__ == "__main__":
    test_save_migration();test_stage_table_and_scripts();test_engine_load_registered_stages()
    print("battle merge regression checks passed")
