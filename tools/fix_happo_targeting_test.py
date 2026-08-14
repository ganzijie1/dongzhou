from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/happo_targeting_test.py"
text = path.read_text(encoding="utf-8")
old = '''    physical_low_def = target_selection_reward(actions[1], tactical[1], units)
    physical_high_def = target_selection_reward(actions[0], tactical[0], units)
    magic_low_spirit = target_selection_reward(actions[5], tactical[5], units)
    magic_high_spirit = target_selection_reward(actions[3], tactical[3], units)
    assert physical_low_def > physical_high_def
    assert magic_low_spirit > magic_high_spirit

    lethal = dict(actions[0], damage=25)
    assert target_selection_reward(lethal, tactical[0], units) >= physical_high_def + 0.44
'''
new = '''    physical_low_hp = target_selection_reward(actions[0], tactical[0], units)
    physical_low_def = target_selection_reward(actions[1], tactical[1], units)
    physical_robust = target_selection_reward(actions[2], tactical[2], units)
    magic_low_spirit = target_selection_reward(actions[5], tactical[5], units)
    magic_robust = target_selection_reward(actions[4], tactical[4], units)
    assert physical_low_hp > physical_robust
    assert physical_low_def > physical_robust
    assert magic_low_spirit > magic_robust

    nonlethal = dict(actions[0], damage=24)
    lethal = dict(actions[0], damage=25)
    assert target_selection_reward(lethal, tactical[0], units) >= target_selection_reward(nonlethal, tactical[0], units) + 0.44
'''
if old not in text:
    raise RuntimeError("targeting test anchor missing")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("HAPPO target-priority assertions corrected.")
