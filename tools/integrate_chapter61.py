from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared

ROOT = Path(__file__).resolve().parents[1]

HEROES = '''
        ,{ id = "GongSunXia61", class = "Cavalry", stat = {91,94,91,92,91}, model = "cavalry-1-red" }
        ,{ id = "ZiChan61", class = "Strategist", stat = {94,82,99,96,96}, model = "Strategist-1-red" }
        ,{ id = "GongSunChai61", class = "Cavalry", stat = {90,94,89,91,90}, model = "cavalry-1-red" }
        ,{ id = "WeiZhi61", class = "Cavalry", stat = {87,92,85,89,86}, model = "cavalry-1-blue" }
        ,{ id = "SiChen61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-blue" }
        ,{ id = "HouJin61", class = "Archer", stat = {85,90,87,88,86}, model = "archer-1-blue" }
        ,{ id = "ZhengHouseGuard61", class = "Infantry", stat = {87,92,85,89,87}, model = "infantry-1-red" }
        ,{ id = "ZhengRebel61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-blue" }
        ,{ id = "ZhengRebelArcher61", class = "Archer", stat = {85,90,87,88,86}, model = "archer-1-blue" }
        ,{ id = "FanYang61", class = "Cavalry", stat = {91,95,92,93,91}, model = "cavalry-1-red" }
        ,{ id = "QinJingGong61", class = "Lord", stat = {93,91,94,93,92}, model = "lord-1-blue" }
        ,{ id = "YingZhan61", class = "Cavalry", stat = {91,96,88,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GongZiWuDi61", class = "Cavalry", stat = {90,95,87,91,89}, model = "cavalry-1-blue" }
        ,{ id = "QinYulinGuard61", class = "Infantry", stat = {88,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QinYulinArcher61", class = "Archer", stat = {87,93,90,91,89}, model = "archer-1-blue" }
        ,{ id = "WeiXianGong61", class = "Lord", stat = {88,89,84,87,83}, model = "lord-1-red" }
        ,{ id = "GongSunDing61", class = "Archer", stat = {91,98,90,94,92}, model = "archer-1-red" }
        ,{ id = "SunKuai61", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "SunJia61", class = "Cavalry", stat = {88,93,85,89,87}, model = "cavalry-1-blue" }
        ,{ id = "GengGongCha61", class = "Archer", stat = {90,97,88,92,90}, model = "archer-1-blue" }
        ,{ id = "YinGongTuo61", class = "Archer", stat = {88,95,86,90,88}, model = "archer-1-blue" }
        ,{ id = "GongZiZhuan61", class = "Cavalry", stat = {87,92,86,89,87}, model = "cavalry-1-red" }
        ,{ id = "WeiPalaceGuard61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-red" }
        ,{ id = "SunPursuer61", class = "Cavalry", stat = {87,92,84,89,87}, model = "cavalry-1-blue" }
        ,{ id = "SunArcher61", class = "Archer", stat = {86,91,87,89,87}, model = "archer-1-blue" }'''


def data(mid: str, suffix: str) -> dict:
    return json.loads((ROOT / f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))


def head(chapter, title, battle, objective, asset, intro, victory, defeat, commanders, sites, events):
    return shared.stage_head("", title, chapter, battle, objective, asset, intro, events, victory, defeat, commanders, sites)


def stage_a() -> str:
    d = data("m098", "ch61a")
    intro = [
        ("", "偪阳破城后，晋悼公三次分军临郑，以轮番出师疲敝楚军。第一次驻牛首时，郑国西宫忽生内乱。"),
        ("", "尉止纠集司臣、侯晋等人，杀公子騑、公子发、公孙辄，退据北宫，企图控制郑国朝政。"),
        ("公孙夏", "父亲公子騑死于乱党，我当率家甲攻贼，为父报仇，也保郑国宗庙。"),
        ("子产", "国中虽乱，不能借外兵平事。家甲只击乱党，不得侵扰城中百姓。"),
        ("公孙虿", "我从东街策应。尉止若退入北宫，三路同时合围，不给其逃亡机会。"),
        ("智罃", "郑国内乱本可乘隙攻取，但乘人之危不义。晋军缓攻，听郑人自行定乱。"),
        ("栾黡", "若此时攻城，郑必不能战。元帅既以信义为先，下军遵令列阵，不入城。"),
        ("军令", "率三支家甲从南门进入西宫，击退尉止、司臣、侯晋等乱党。三名我方将领任一被击退则失败。"),
    ]
    victory = [
        ("", "公孙夏率家甲攻入北宫，公孙虿从侧翼夹击。尉止一党溃散，首恶尽被诛灭。"),
        ("子产", "内乱已经平定。收拢兵甲，安抚百姓，迎立公子嘉主持国政。"),
        ("", "智罃接受郑国求和，晋军退去；楚公子贞随后到来，郑国又与楚盟。这是三驾服楚的第一驾。"),
        ("", "次年晋军第二次围郑，向戌屯东门、孙林父屯北鄙、赵武营西郊、智罃扬兵南门。郑简公在毫城北与晋盟。"),
        ("", "郑国为迫使晋楚分出强弱，又诱楚国伐宋。晋悼公会合十二国第三次临郑，驻军萧鱼。"),
        ("晋悼公", "郑若真心归晋，俘虏尽数释放，虎牢戍兵也可撤去。以诚信相待，不再逼其反覆。"),
        ("", "郑简公感泣盟晋，献乐器车甲。悼公赏魏绛、智罃，郑国自此二十四年不再叛晋。"),
        ("军令", "郑宫平乱完成，获得1200金币。下一关：棫林突秦。"),
    ]
    story = head("第六十一回·上", "晋悼公驾楚会萧鱼 孙林父因歌逐献公", "郑宫平乱",
                 "诛灭尉止党羽，平定郑国西宫内乱。", "m098.png", intro, victory,
                 "三名郑国具名将领被击退，家甲失去统领，本关失败。",
                 ["GongSunXia61", "ZiChan61", "GongSunChai61"],
                 '{{id="west_palace",name="郑国西宫",position={24,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="west_store",name="西宫武库",position={16,18},restore_hp=20,restore_mp=10,rewards={}}, {id="east_store",name="东侧府库",position={34,18},restore_hp=20,restore_mp=10,rewards={}}}',
                 [("公孙夏", "乱党退入北宫，三路合围！")])
    rows = shared.terrain_block(d)
    return story + f'''local rebels={{"WeiZhi61","SiChen61","HouJin61"}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("WeiZhi61",1,Enum.force.enemy,{{24,10}});game:generate_unit("SiChen61",1,Enum.force.enemy,{{16,18}});game:generate_unit("HouJin61",1,Enum.force.enemy,{{34,18}});many(game,"ZhengHouseGuard61",{{{{19,30}},{{23,31}},{{27,31}},{{31,30}}}},Enum.force.own);many(game,"ZhengRebel61",{{{{24,25}},{{25,25}},{{14,22}},{{35,22}},{{20,15}},{{29,15}},{{22,9}},{{27,9}}}},Enum.force.enemy);many(game,"ZhengRebelArcher61",{{{{12,18}},{{38,18}},{{19,12}},{{30,12}}}},Enum.force.enemy)end
function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end for _,h in ipairs(rebels)do if game:has_unit(h)then return Enum.status.undecided end end return Enum.status.victory end
gstage={{title_id="ZhengPalaceRevolt61",turn_limit=24,map={{blocked_edges={{}},size={{50,34}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{21,30}},hero="GongSunXia61"}},{{position={{25,30}},hero="ZiChan61"}},{{position={{29,30}},hero="GongSunChai61"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=12000}}}}
'''


def stage_b() -> str:
    d=data("m099","ch61b")
    intro=[("","楚共王去世后，吴王诸樊遣公子党伐楚，养由基一箭射杀公子党，吴军败退。"),("","晋悼公决定报秦救郑之怨，命荀偃率晋军及十二国诸侯伐秦。秦景公在泾水上游投毒，联军渡河受阻。"),("公子蟜","既然从晋出兵，岂能临河观望？郑军先渡泾水，卫军随后跟上！"),("荀偃","诸军鸡鸣驾车，视我马首所向而行。"),("栾黡","军旅进退岂能只说看马首？我的马首要向东，魏绛随我班师！"),("荀偃","号令不明是我的过错。下军既退，诸侯无心再战，全军撤回。"),("栾鍼","此行本为报秦，若人人无功而返，只会再添国耻。范鞅，你可愿与我突入秦阵？"),("范鞅","愿随将军。但秦营有四百乘，击破前阵后不可恋战，须留一人把消息带回。"),("军令","栾鍼、范鞅从西侧渡口突入秦营。栾鍼按原著战死后，范鞅撤回西岸即完成关卡。")]
    victory=[("","栾鍼连杀秦军十余人，嬴詹大军赶到，将二人重重包围。栾鍼身中七箭，力尽而死。"),("范鞅","秦军势大，继续死战只会让栾将军的消息无人带回。范鞅脱甲单车，冲出包围！"),("","范鞅独自回营，栾黡误以为他诱弟送死，拔戈追杀。范匄命范鞅暂奔秦国。"),("秦景公","范鞅能识晋国贤才，也能预见栾氏兴亡，可留作客卿。秦晋积怨至此，应当重新通聘。"),("","秦景公遣庶长武聘晋，请复范鞅之位。晋悼公同意，秦晋自此通和。"),("军令","棫林突秦完成，获得900金币。下一关：卫侯出奔。")]
    story=head("第六十一回·中","晋悼公驾楚会萧鱼 孙林父因歌逐献公","棫林突秦","栾鍼阵亡后，保护范鞅撤回泾水西岸。","m099.png",intro,victory,"范鞅被秦军击退，本关失败。",["FanYang61"],'{{id="qin_center",name="秦军中营",position={50,18},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="qin_rear",name="秦军后营",position={53,23},restore_hp=25,restore_mp=15,rewards={}}}',[("栾鍼","联军虽退，我二人仍要让秦军知道晋国有人！"),("范鞅","栾将军已经战死，向西岸撤退！")])
    rows=shared.terrain_block(d)
    return story+f'''local luan_fallen=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("FanYang61",1);game:appoint_hero("LuanZhen58",1)end
function on_begin(game)game:generate_unit("QinJingGong61",1,Enum.force.enemy,{{50,18}});game:set_unit_invulnerable("QinJingGong61",true);game:generate_unit("YingZhan61",1,Enum.force.enemy,{{53,23}});game:generate_unit("GongZiWuDi61",1,Enum.force.enemy,{{44,20}});many(game,"QinYulinGuard61",{{{{45,17}},{{45,22}},{{48,14}},{{51,14}},{{55,16}},{{55,25}},{{49,27}},{{44,25}}}},Enum.force.enemy);many(game,"QinYulinArcher61",{{{{47,11}},{{54,12}},{{56,20}},{{51,28}}}},Enum.force.enemy)end
function on_update(game)if not luan_fallen and not game:has_unit("LuanZhen58")then luan_fallen=true;game:push_cmd_speak(0,"栾鍼身中七箭，力尽战死！范鞅立即向西渡过泾水！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("FanYang61")then return Enum.status.defeat end if luan_fallen and game:is_unit_within("FanYang61",{{16,19}},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="YulinCharge61",turn_limit=24,map={{blocked_edges={{}},size={{62,40}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{31,18}},hero="LuanZhen58"}},{{position={{31,21}},hero="FanYang61"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=9000}}}}
'''


def stage_c() -> str:
    d=data("m100","ch61c")
    intro=[("","卫献公轻慢孙林父、宁殖，又借《巧言》讥刺孙氏。孙林父在戚邑聚集家甲，迎立公孙剽之谋渐成。"),("孙林父","卫侯已经明言猜忌孙氏，再坐等下去必受其祸。整顿家甲，攻入国都。"),("","孙蒯、孙嘉率兵击散二百余宫甲。卫献公只剩十余人，由神射手公孙丁护送，从东门奔齐。"),("卫献公","前有河泽，后有追兵。寡人若能抵达齐境，尚可等待复国之日。"),("公孙丁","臣负责断后。主公沿东门大道前进，不要停在追兵射程之内。"),("","庾公差追到后认出授业恩师公孙丁，去掉箭镞，四箭只中车身，以全师恩与主命。"),("尹公佗","庾公差顾念师门，我与公孙丁却隔了一层。若无功而返，如何回复孙氏？"),("公孙丁","射艺传承不可忘本。你若仍要追来，我只能以你的箭还射于你。"),("军令","护送卫献公沿东门大道抵达齐境。尹公佗出现后必须击退，公孙丁与卫献公不得被击退。")]
    victory=[("","尹公佗一箭射来，公孙丁伸手接住，搭回弓弦，一箭贯其左臂，再发一箭将其射死。"),("","卫献公之弟公子鱄冒死赶来从驾，君臣进入齐境。齐灵公把卫献公安置在莱城。"),("卫献公","若非公孙丁神射，寡人已经死在河泽。今日奔亡，实由轻慢大臣、自取其祸。"),("","孙林父与宁殖迎公孙剽即位，是为卫殇公。晋悼公认为卫衎无道，没有出兵讨伐。"),("","齐灵公见晋侯无意干涉卫国内乱，开始图谋争霸；晋悼公却已病重。"),("军令","卫侯出奔完成，获得1100金币。第六十一回结束。")]
    story=head("第六十一回·下／第六十二回开端","晋悼公驾楚会萧鱼 孙林父因歌逐献公","卫侯出奔","保护卫献公击退尹公佗并抵达齐境。","m100.png",intro,victory,"卫献公或公孙丁被击退，本关失败。",["WeiXianGong61","GongSunDing61"],'{{id="wei_palace",name="卫国宫城",position={12,12},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}',[("庾公差","四箭去镞，只射车身，不伤吾师与卫侯！"),("尹公佗","师恩为轻，主命为重，我再来追取卫侯！")])
    rows=shared.terrain_block(d)
    return story+f'''local second_wave=false local yin_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("GongZiZhuan61",1)end
function on_begin(game)game:generate_unit("SunKuai61",1,Enum.force.enemy,{{12,25}});game:generate_unit("SunJia61",1,Enum.force.enemy,{{15,27}});many(game,"WeiPalaceGuard61",{{{{16,16}},{{17,18}},{{18,20}}}},Enum.force.own);many(game,"SunPursuer61",{{{{11,23}},{{16,24}},{{18,27}},{{20,25}}}},Enum.force.enemy);many(game,"SunArcher61",{{{{10,27}},{{17,29}}}},Enum.force.enemy)end
function on_update(game)if not second_wave and game:is_unit_within("WeiXianGong61",{{35,18}},3)then second_wave=true;game:push_cmd_speak(0,"庾公差去镞发箭，四箭只中车身，随后依师礼退兵。")end if second_wave and not yin_spawned and game:is_unit_within("WeiXianGong61",{{46,18}},3)then yin_spawned=true;game:generate_unit("YinGongTuo61",1,Enum.force.enemy,{{50,18}});many(game,"SunPursuer61",{{{{49,16}},{{49,20}},{{52,17}},{{52,21}}}},Enum.force.enemy);game:generate_unit("GongZiZhuan61",1,Enum.force.ally,{{54,20}});game:push_cmd_speak(0,"尹公佗再次追来！公子鱄也从齐境方向赶来接应！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if yin_spawned and not game:has_unit("YinGongTuo61") and game:is_unit_within("WeiXianGong61",{{62,18}},1)then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="WeiExileEscape61",turn_limit=28,map={{blocked_edges={{}},size={{64,38}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{18,17}},hero="WeiXianGong61"}},{{position={{19,19}},hero="GongSunDing61"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=11000}}}}
'''


def patch_all() -> None:
    for sid,text in (("61a",stage_a()),("61b",stage_b()),("61c",stage_c())):
        (ROOT/f"game/sce/dongzhou/stage/{sid}.lua").write_text(text,encoding="utf-8")
    p=ROOT/"game/sce/dongzhou/config.lua";t=p.read_text(encoding="utf-8")
    if 'id = "GongSunXia61"' not in t:
        t=t.replace('        ,{ id = "BiYangArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }    },','        ,{ id = "BiYangArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }'+HEROES+'    },')
    t=t.replace('"60a", "60b", "60c" }','"60a", "60b", "60c", "61a", "61b", "61c" }');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/save_system.py";t=p.read_text(encoding="utf-8").replace('STAGE_TABLE_VERSION = 4','STAGE_TABLE_VERSION = 5').replace('"60a","60b","60c"\n)','"60a","60b","60c","61a","61b","61c"\n)');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/play_gui.py";t=p.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m098.png"]' not in t:
        block='''\n_LARGE_BATTLE_MAPS["m098.png"]=(50,34,48)\n_LARGE_BATTLE_MAPS["m099.png"]=(62,40,48)\n_LARGE_BATTLE_MAPS["m100.png"]=(64,38,48)\nHERO_LABELS.update({"GongSunXia61":"公孙夏","ZiChan61":"子产","GongSunChai61":"公孙虿","WeiZhi61":"尉止","SiChen61":"司臣","HouJin61":"侯晋","ZhengHouseGuard61":"郑国家甲","ZhengRebel61":"尉氏乱兵","ZhengRebelArcher61":"尉氏弓手","FanYang61":"范鞅","QinJingGong61":"秦景公","YingZhan61":"嬴詹","GongZiWuDi61":"公子无地","QinYulinGuard61":"秦军甲士","QinYulinArcher61":"秦军弓手","WeiXianGong61":"卫献公","GongSunDing61":"公孙丁","SunKuai61":"孙蒯","SunJia61":"孙嘉","GengGongCha61":"庾公差","YinGongTuo61":"尹公佗","GongZiZhuan61":"公子鱄","WeiPalaceGuard61":"卫侯宫甲","SunPursuer61":"孙氏追兵","SunArcher61":"孙氏弓手"})
HERO_BIOS.update({"GongSunXia61":"郑国大夫，字子西。父亲公子騑被尉止杀害后，率家甲攻灭乱党。","ZiChan61":"郑国名臣公孙侨，字子产。尉止之乱时率家甲平乱，后来执政郑国。","GongSunChai61":"郑国公族大夫，尉止之乱中率众协助平乱。","WeiZhi61":"郑国大夫，发动西宫之乱，最终兵败被诛。","FanYang61":"晋国大夫范鞅，随栾鍼突入秦阵，脱围后暂奔秦国。","QinJingGong61":"秦国君主，棫林之役率四百乘迎战诸侯，后接纳范鞅。","YingZhan61":"秦国大将，棫林之役随秦景公合围栾鍼、范鞅。","GongZiWuDi61":"秦国公子，棫林秦军前锋。","WeiXianGong61":"卫国君主衎，轻慢孙林父、宁殖而引发内乱，被逐后逃往齐国。","GongSunDing61":"卫国神射手，护送卫献公出奔，以尹公佗来箭反射将其击杀。","SunKuai61":"孙林父长子，率兵追击出奔的卫献公。","SunJia61":"孙林父之子，与孙蒯一同追击卫献公。","GengGongCha61":"孙氏家臣，公孙丁弟子，去镞发四箭而不伤恩师。","YinGongTuo61":"庾公差弟子，执意追杀卫献公，被公孙丁反射杀死。","GongZiZhuan61":"卫献公同母弟，卫侯出奔时冒死赶来从驾。"})
PORTRAIT_INDEX_BY_HERO.update({"GongSunXia61":35,"ZiChan61":49,"GongSunChai61":38,"WeiZhi61":34,"SiChen61":25,"HouJin61":33,"FanYang61":35,"QinJingGong61":8,"YingZhan61":34,"GongZiWuDi61":38,"WeiXianGong61":7,"GongSunDing61":33,"SunKuai61":35,"SunJia61":38,"GengGongCha61":24,"YinGongTuo61":34,"GongZiZhuan61":25})
SPEAKER_PORTRAIT_INDEX.update({"公孙夏":35,"子产":49,"公孙虿":38,"智罃":35,"栾黡":35,"公子蟜":38,"荀偃":37,"栾鍼":35,"范鞅":35,"秦景公":8,"孙林父":42,"卫献公":7,"公孙丁":33,"尹公佗":34,"庾公差":24})
HISTORICAL_DEATH_HEROES.update({"WeiZhi61","SiChen61","HouJin61","LuanZhen58","YinGongTuo61"})
'''
        t=t.replace('\nif _original_name == "__main__":',block+'\nif _original_name == "__main__":')
    p.write_text(t,encoding="utf-8")


if __name__ == "__main__":
    patch_all(); print("chapter 61 integrated: 61a, 61b, 61c")
