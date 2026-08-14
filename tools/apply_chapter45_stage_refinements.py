from pathlib import Path


path = Path(r"C:\mengde\game\sce\dongzhou\stage\45a.lua")
text = path.read_text(encoding="utf-8")

old = "ambush_triggered = false\nambush_spoken = false\n"
new = "ambush_triggered = false\nambush_spoken = false\ncapture_announced = {}\n"
assert text.count(old) == 1
text = text.replace(old, new, 1)

old = '''local ambush_named = { "XianQieJu45", "TuJi45", "XuYing45", "HuJuJu45", "HuSheGu27", "HanZiYu45", "LiangHong45", "LaiJu45", "LangTan45" }
'''
new = '''local ambush_named = { "XianQieJu45", "TuJi45", "XuYing45", "HuJuJu45", "HuSheGu27", "HanZiYu45", "LiangHong45", "LaiJu45", "LangTan45" }
local qin_captives = {
    { "MengMingShi26", "孟明视" },
    { "XiQiShu26", "西乞术" },
    { "BaiYiBing26", "白乙丙" }
}
'''
assert text.count(old) == 1
text = text.replace(old, new, 1)

old = '''function on_update(game)
    if not ambush_triggered and (game:is_unit_within("BaoManZi44", {11,14}, 2) or not game:has_unit("BaoManZi44")) then
        spring_ambush(game)
    end
end
'''
new = '''function on_update(game)
    if not ambush_triggered and (game:is_unit_within("BaoManZi44", {11,14}, 2) or not game:has_unit("BaoManZi44")) then
        spring_ambush(game)
    end
    for _, captive in ipairs(qin_captives) do
        local hero, label = captive[1], captive[2]
        if not capture_announced[hero] and not game:has_unit(hero) then
            capture_announced[hero] = true
            game:push_cmd_speak(0, label .. "力尽落马，已被晋军生擒，押往襄公中军。")
        end
    end
end
'''
assert text.count(old) == 1
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8", newline="")
print("Added chapter45 per-commander capture events.")
