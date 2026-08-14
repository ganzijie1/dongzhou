import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rep(p,o,n):
 p=Path(p);s=p.read_text(encoding="utf-8")
 if o not in s:raise RuntimeError(f"anchor missing {p}: {o[:60]}")
 p.write_text(s.replace(o,n,1),encoding="utf-8")
def inject(stage,manifest):
 d=json.loads((ROOT/"assets/lzc/map_sources"/manifest).read_text(encoding="utf-8"));v="\n"+"\n".join(f'        "{r}",'for r in d["terrain_rows"])+"\n    ";rep(ROOT/"game/sce/dongzhou/stage"/stage," __ROWS__ ",v)
def main():
 inject("56a.lua","m089_ch56a_manifest.json");inject("56b.lua","m090_ch56b_manifest.json")
 cfg=ROOT/"game/sce/dongzhou/config.lua";heroes='''        ,{ id = "SunLiangFu56", class = "Cavalry", stat = {88, 92, 90, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "ShiJi56", class = "Strategist", stat = {88, 86, 94, 92, 90}, model = "Strategist-1-red" }
        ,{ id = "ZhongShuYuXi56", class = "Cavalry", stat = {86, 91, 87, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "GuoZuo56", class = "Strategist", stat = {91, 87, 96, 94, 92}, model = "Strategist-1-blue" }
        ,{ id = "GaoGu56", class = "Cavalry", stat = {88, 95, 84, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "XiKe56", class = "Archer", stat = {92, 94, 96, 95, 93}, model = "archer-1-red" }
        ,{ id = "JiSunXingFu56", class = "Strategist", stat = {92, 84, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "QiQingGong56", class = "King", stat = {88, 92, 88, 91, 89}, model = "lord-1-blue" }
        ,{ id = "FengChouFu56", class = "Cavalry", stat = {90, 93, 90, 92, 91}, model = "cavalry-1-blue" }
        ,{ id = "WeiRaidGuard56", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-red" }
        ,{ id = "QiAmbushGuard56", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "QiAmbushCavalry56", class = "Cavalry", stat = {89, 94, 85, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "WeiReliefGuard56", class = "Infantry", stat = {86, 92, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionGuard56", class = "Infantry", stat = {89, 94, 88, 91, 89}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher56", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-red" }
        ,{ id = "QiCenterChariot56", class = "Cavalry", stat = {89, 95, 87, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "QiArcher56", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-blue" }
''';rep(cfg,"    },\n    equipments = {},",heroes+"    },\n    equipments = {},");rep(cfg,'"54b", "55a", "55b" }','"54b", "55a", "55b", "56a", "56b" }')
 gui=ROOT/"rl/play_gui.py";block='''_LARGE_BATTLE_MAPS["m089.png"] = (48, 32, 48)
_LARGE_BATTLE_MAPS["m090.png"] = (60, 38, 48)
HERO_LABELS.update({"SunLiangFu56":"孙良夫","ShiJi56":"石稷","ZhongShuYuXi56":"仲叔于奚","GuoZuo56":"国佐","GaoGu56":"高固","XiKe56":"郤克","JiSunXingFu56":"季孙行父","QiQingGong56":"齐顷公","FengChouFu56":"逢丑父","WeiRaidGuard56":"卫军夜袭卒","QiAmbushGuard56":"齐军伏兵","QiAmbushCavalry56":"齐军伏骑","WeiReliefGuard56":"新筑援军","JinCoalitionGuard56":"晋国联军甲士","JinCoalitionArcher56":"晋国联军弓手","QiCenterChariot56":"齐中军战车","QiArcher56":"齐军强弓"})
HERO_BIOS.update({"SunLiangFu56":"卫国上卿。因出使齐国遭嘲笑而誓报其辱，新筑夜袭中遭齐军伏击，后赴晋国请兵。","ShiJi56":"卫国将领。劝孙良夫不可轻敌未被采纳，夜袭失败后率军断后。","ZhongShuYuXi56":"卫国新筑大夫。率本境百余乘救援孙良夫，迫使齐军停止追击。","GuoZuo56":"齐国上卿。多次劝齐顷公守礼，后统军参与新筑、鞌地战事。","GaoGu56":"齐国猛将。鞌战前单车闯入晋营，以巨石击敌并夺车而返。","XiKe56":"晋国郤氏主将。出使齐国受辱后主张伐齐，鞌之战负伤仍击鼓，最终大破齐军。","JiSunXingFu56":"鲁国正卿季文子。出使齐国受辱，与晋卫曹使臣歃血盟誓伐齐。","QiQingGong56":"齐国君主无野。因侮辱四国使臣引发鞌之战，兵败后借逢丑父换衣脱身。","FengChouFu56":"齐顷公车右。鞌之战与君主换衣，代齐侯被韩厥俘获，因忠义获释。"})
PORTRAIT_INDEX_BY_HERO.update({"SunLiangFu56":35,"ShiJi56":45,"ZhongShuYuXi56":33,"GuoZuo56":49,"GaoGu56":34,"XiKe56":37,"JiSunXingFu56":42,"QiQingGong56":7,"FengChouFu56":38})
SPEAKER_PORTRAIT_INDEX.update({"羊舌职":45,"国佐":49,"郤克":37,"石稷":45,"孙良夫":35,"高固":34,"齐顷公":7,"解张":31,"韩厥":42,"逢丑父":38})

''';rep(gui,'if _original_name == "__main__":',block+'if _original_name == "__main__":')
 prior=ROOT/"rl/chapter55_test.py";rep(prior,'assert \'"54a", "54b", "55a", "55b" }\'in c','assert \'"54a", "54b", "55a", "55b", "56a", "56b" }\'in c')
 print("Chapter 56 integrated.")
if __name__=="__main__":main()
