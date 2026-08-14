import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def rep(path,old,new):
 p=Path(path);s=p.read_text(encoding="utf-8")
 if old not in s:raise RuntimeError(f"anchor missing {p}: {old[:60]}")
 p.write_text(s.replace(old,new,1),encoding="utf-8")

def inject(stage,manifest):
 d=json.loads((ROOT/"assets/lzc/map_sources"/manifest).read_text(encoding="utf-8"));v="\n"+"\n".join(f'        "{r}",' for r in d["terrain_rows"])+"\n    "
 rep(ROOT/"game/sce/dongzhou/stage"/stage," __ROWS__ ",v)

def main():
 inject("55a.lua","m087_ch55a_manifest.json");inject("55b.lua","m088_ch55b_manifest.json")
 cfg=ROOT/"game/sce/dongzhou/config.lua"
 heroes='''        ,{ id = "ShenShuShi55", class = "Strategist", stat = {93, 86, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "ShenXi55", class = "Cavalry", stat = {84, 89, 84, 87, 86}, model = "cavalry-1-red" }
        ,{ id = "WeiKe55", class = "Cavalry", stat = {90, 94, 92, 93, 91}, model = "cavalry-1-red" }
        ,{ id = "DuHui55", class = "Infantry", stat = {86, 99, 86, 93, 90}, model = "infantry-1-blue" }
        ,{ id = "ChuSiegeGuard55", class = "Infantry", stat = {89, 94, 87, 91, 89}, model = "infantry-1-red" }
        ,{ id = "ChuSiegeArcher55", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-red" }
        ,{ id = "SongGateGuard55", class = "Infantry", stat = {88, 93, 87, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "SongCityArcher55", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-blue" }
        ,{ id = "JinAmbushGuard55", class = "Infantry", stat = {87, 93, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinAmbushArcher55", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-red" }
        ,{ id = "QinAxeGuard55", class = "Infantry", stat = {88, 95, 84, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "QinGuard55", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-blue" }
'''
 rep(cfg,"    },\n    equipments = {},",heroes+"    },\n    equipments = {},")
 rep(cfg,'"53b", "54a", "54b" }','"53b", "54a", "54b", "55a", "55b" }')
 gui=ROOT/"rl/play_gui.py"
 block='''_LARGE_BATTLE_MAPS["m087.png"] = (54, 36, 48)
_LARGE_BATTLE_MAPS["m088.png"] = (48, 32, 48)
HERO_LABELS.update({"ShenShuShi55":"申叔时","ShenXi55":"申犀","WeiKe55":"魏颗","DuHui55":"杜回","ChuSiegeGuard55":"楚军攻城卒","ChuSiegeArcher55":"楚军楼车弓手","SongGateGuard55":"睢阳守卒","SongCityArcher55":"宋军城弓手","JinAmbushGuard55":"晋军伏兵","JinAmbushArcher55":"晋军伏弓","QinAxeGuard55":"秦国刀斧手","QinGuard55":"秦军甲士"})
HERO_BIOS.update({"ShenShuShi55":"楚国贤臣。围宋粮尽时建议筑室耕田，以长期围困假象迫使宋国议和。","ShenXi55":"楚臣申舟之子。父亲奉命过宋被杀，随楚庄王伐宋，请求君王践诺报仇。","WeiKe55":"晋国将领，魏犨之子。遵父亲清醒时遗命保全祖姬，后在青草坡获老人结草相助，生擒杜回。","DuHui55":"秦国力士，惯使一百二十斤开山大斧，率三百刀斧手冲阵，最终在青草坡被魏颗生擒处斩。"})
PORTRAIT_INDEX_BY_HERO.update({"ShenShuShi55":45,"ShenXi55":35,"WeiKe55":33,"DuHui55":25})
SPEAKER_PORTRAIT_INDEX.update({"公子婴齐":35,"申舟":49,"华元":49,"楚庄王":8,"解扬":42,"申犀":35,"申叔时":45,"公子侧":49,"魏颗":33,"魏锜":33,"杜回":25,"老人":31,"羊舌职":45})
HISTORICAL_DEATH_HEROES.add("DuHui55")

'''
 rep(gui,'if _original_name == "__main__":',block+'if _original_name == "__main__":')
 prior=ROOT/"rl/chapter54_test.py"
 rep(prior,'assert \'"53a", "53b", "54a", "54b" }\' in config','assert \'"53a", "53b", "54a", "54b", "55a", "55b" }\' in config')
 print("Chapter 55 integrated.")
if __name__=="__main__":main()
