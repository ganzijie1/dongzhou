from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/lzc/map_sources/m127_ch81_manifest.json"

HEROES = [
    ("ChenQi81","Strategist","Strategist-1-red","陈乞","齐国陈氏宗主，联合鲍氏攻高、国二族，废安孺子而立齐悼公。"),
    ("BaoMu81","Cavalry","cavalry-1-red","鲍牧","齐国鲍氏大夫，与陈乞共同攻高、国，后遭齐悼公猜忌诛杀。"),
    ("GaoZhang81","Cavalry","cavalry-1-blue","高张","齐景公托孤重臣，与国夏辅佐安孺子，在高国之乱中战死。"),
    ("GuoXia81","Strategist","Strategist-1-blue","国夏","齐景公托孤重臣，高张被杀后出奔莒国。"),
    ("QiClanGuard81","Infantry","infantry-1-red","齐国大夫家甲","陈、鲍及齐国诸大夫召集的家甲。"),
    ("QiClanArcher81","Archer","archer-1-red","齐国大夫弓手","陈、鲍及齐国诸大夫麾下弓手。"),
    ("GaoHouseGuard81","Infantry","infantry-1-blue","高氏家甲","守卫高张府邸的齐国甲士。"),
    ("GaoHouseArcher81","Archer","archer-1-blue","高氏弓手","守卫高张府邸的齐国弓手。"),
    ("GuoHouseGuard81","Infantry","infantry-1-blue","国氏家甲","守卫国夏府邸的齐国甲士。"),
    ("GuoHouseArcher81","Archer","archer-1-blue","国氏弓手","守卫国夏府邸的齐国弓手。"),
    ("GongZiYangSheng81","Lord","lord-1-red","公子阳生","齐景公长子，被陈乞迎回临淄，废安孺子即位为齐悼公。"),
    ("XiShi81","Support","support-1-red","西施","越国苎萝山施氏女，被献入吴宫，成为越国美人计的关键人物。"),
    ("YueNv81","Infantry","infantry-1-red","南林处女","南林剑术高手，受越王聘请训练越军三千人。"),
    ("ChenYin81","Archer","archer-1-red","陈音","避仇入越的楚国射师，为越国训练连弩手三千。"),
    ("ChenHeng81","Strategist","Strategist-1-red","陈恒","陈乞之子，毒杀齐悼公，后被子贡说服移兵强吴。"),
    ("ZiGong81","Strategist","Strategist-1-red","子贡","孔子弟子端木赐，为救鲁周游齐、吴、越、晋。"),
]

INTRO = [
    ("","越王勾践归国后依文种之策遍访美女，半年得二十余人，复选苎萝山下浣纱的西施、郑旦。范蠡以百金聘二女，送入土城，命老乐师教习歌舞容步三年。"),
    ("范蠡","吴强甲于天下，越国尚不能与之争锋。二女入吴不是一朝胜负，而是要让夫差沉湎游乐、疏远忠臣，为越国争得生聚教训的岁月。"),
    ("越王勾践","厚待二女及其家人，衣以绮罗、乘以帷车。待技艺尽善，再由先生亲送吴宫；越国今日每一分忍耐，都是来日复国之资。"),
    ("","同一时期，齐景公舍长立幼，把安孺子荼托付国夏、高张。陈乞素与长公子阳生相结，先劝阳生奔鲁，又散布高、国将尽逐旧臣的流言。"),
    ("陈乞","高、国挟幼君专政，今日若不合诸大夫家甲并攻二府，明日临淄旧臣都要被逐。鲍大夫与我分兵：高张必须伏诛，国夏若弃府西奔莒国，不必穷追。"),
    ("鲍牧","我只为解除托孤二臣的专权，并未答应另立新君。先整齐家众，封住南北街口，不得扰害临淄百姓。"),
    ("高张","先君命我与国夏共辅孺子，陈乞却以谣言召集私甲。关闭府门，弓手据墙，今日只论君命，不论陈氏强弱！"),
    ("国夏","高氏北府若破，我自南府西门撤往莒国保存国氏。陈乞志在改立阳生，绝不只为所谓旧臣自保。"),
    ("军令","陈乞、鲍牧任何一人被击退则失败。攻破高氏北府并击败高张；高张死后，国夏将按史实自动撤往西界，不得将其击杀。"),
]

VICTORY = [
    ("","高张战死，国夏弃南府出奔莒国。陈乞立国书、高无平延续二氏祭祀，表面安抚齐人，暗中却已召公子阳生自鲁返齐。"),
    ("公子阳生","我与子壬、阚止夜抵齐郊，只身藏入陈氏。若诸大夫肯守立长之义，今日便改奉长公子。"),
    ("陈乞","诸大夫请看新得精甲！巨囊中不是甲胄，正是齐景公长子阳生。立子以长，今日奉鲍相国之命改事长君。"),
    ("鲍牧","我本无此谋，何得乘我酒后相诬！陈乞强拉我下拜，诸大夫也被迫歃血；这场废立终会反噬主持之人。"),
    ("","阳生即位为齐悼公，迁安孺子于宫外而杀之，又因疑鲍牧不愿拥立，听陈乞谗言诛杀鲍牧。国人怨悼公杀戮无辜。"),
    ("","鲁国季孙斯伐邾，破国执邾子益。齐悼公为妹婿向吴乞师；鲁国旋即释放邾君，齐又请吴罢兵。夫差怒齐前后反复，反与鲁国合兵围齐。"),
    ("陈恒","国人怨悼公召寇，又怨他杀鲍牧。我在阅师时进鸩酒，称君上暴疾而死，请吴王息兵；再立其子壬为简公。"),
    ("","西施、郑旦学艺三年，范蠡携二女与六名侍女入吴。夫差见二女如神仙下降，伍子胥以妹喜、妲己、褒姒亡国为鉴，力谏不可收受。"),
    ("伍子胥","美女是亡国之物。勾践得此绝色而不用，偏献大王，正说明越国所图不小；今日若收二女，吴宫歌舞必压过军国之声。"),
    ("吴王夫差","好色人所同心，勾践献其所爱，正是尽忠于吴。相国不必把每一件越国贡物都说成兵刃。"),
    ("西施","妾本苎萝山下浣纱之女，今入吴宫，只愿谨守洒扫歌舞之职，不敢过问国政。"),
    ("","夫差独宠西施，在灵岩山建馆娃宫、响屧廊、玩花池、采香泾，四时游乐；郑旦郁郁而死。太宰嚭常侍左右，伍子胥求见屡被拒绝。"),
    ("文种","越国歉收，请向吴太仓借粟万石。吴若拒绝便失恤邻之名；若肯借粮，则越民得活而吴仓转空。"),
    ("伍子胥","今日非吴有越，便是越有吴。勾践早朝晏罢、恤民养士，借粮正为充实越国；大王应当辞绝。"),
    ("吴王夫差","越民既是吴民，岂可见饥不救？寡人贷粟万石，明年只令越国如数偿还。"),
    ("文种","次年当选粗大精粟蒸熟后归还。夫差见谷种肥美，必散给吴民播种；熟谷不生，吴国来岁自有饥荒。"),
    ("","吴人果然尽种越粟，颗粒不生，举国大饥。勾践欲兴兵，文种以吴国忠臣尚在劝止；范蠡则访得南林处女教剑、楚人陈音教弩。"),
    ("南林处女","击刺之道，内实精神，外示安佚；见之如好妇，夺之似猛虎。得此道者一人当百、百人当万。"),
    ("","南林处女在山阴道以竹枝胜白猿，又在越宫接住百名勇士攒刺之戟，遂教军士三千。岁余辞归南林，再召已不可得。"),
    ("陈音","弩生于弓，弓生于弹。臣所授连弩三矢连续而去，使敌不及防；三月之后，越国三千弩手可尽得其巧。"),
    ("","伍子胥探知越国练兵，再谏夫差。伯嚭却称治兵只是守国常事。此时齐国陈恒已陈兵汶水，准备伐鲁。"),
    ("子贡","鲁城卑池浅、君弱臣庸，正是难伐；吴城高池广、兵甲精利，反而易攻。相国内忧诸大夫势盛，应使他们困于强敌。"),
    ("陈恒","先生所言直彻肺腑，只是齐兵已在汶上，忽然转向吴国必惹众疑。若能使吴先来伐齐，我便有名迎战。"),
    ("子贡","我先南见吴王，以救鲁、服齐、威晋之利动其心；再东说越王卑辞出师，使吴王不先伐越。"),
    ("吴王夫差","败万乘之齐、收千乘之鲁，吴国即可威加强晋。只是越国勤政训武，寡人原想先伐越。"),
    ("子贡","畏弱越而避强齐，非勇；逐小利而忘大患，非智。臣愿东见越王，使其献甲从征。"),
    ("越王勾践","先生如起死人而肉白骨。寡人愿献精甲、屈卢之矛、步光之剑，并选锐士三千从吴伐齐。"),
    ("","子贡又北见晋定公，请晋国修兵休卒。待他返回鲁国，齐军已经与吴军交锋；吴如何败齐，留待第八十二回。"),
    ("军令","临淄高国之乱完成，获得2400金币。下一关：艾陵之战。"),
]


def lua_story(items: list[tuple[str, str]]) -> str:
    return "\n".join(f'  {{speaker="{speaker}",text="{text}"}},' for speaker, text in items)


def make_stage(rows: list[str]) -> str:
    terrain = "\n".join(f'        "{row}",' for row in rows)
    text = '''gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"ChenQi81","BaoMu81"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={
 {id="gao_residence",name="高氏府库",position={49,10},restore_hp=24,restore_mp=14,rewards={{item="medicine",amount=1}}},
 {id="guo_residence",name="国氏府库",position={49,31},restore_hp=24,restore_mp=14,rewards={{item="spirit_powder",amount=1}}},
 {id="gao_gate_north",name="高氏西门",position={38,10},restore_hp=8,restore_mp=4,rewards={}},
 {id="gao_gate_south",name="高氏西门",position={38,11},restore_hp=8,restore_mp=4,rewards={}},
 {id="guo_gate_north",name="国氏西门",position={38,30},restore_hp=8,restore_mp=4,rewards={}},
 {id="guo_gate_south",name="国氏西门",position={38,31},restore_hp=8,restore_mp=4,rewards={}}
}
gstory={chapter="第八十一回",title="美人计吴宫宠西施 言语科子贡说列国",battle_title="临淄高国之乱",objective="击败高张，并让不可击杀的国夏按史实撤出临淄西界。",map_asset="m127.png",
 intro={
__INTRO__
 },
 events={
  {id="gao_falls",trigger="defeated",unit="GaoZhang81",speaker="陈乞",text="高张已死，国夏弃府西奔莒国；各军让开退路，不必穷追。"},
  {id="guo_retreats",trigger="scripted",turn=0,hp_percent=0,speaker="国夏",text="高氏已破，国氏不能独支。我按西街出城，往莒国保存宗祀！"}
 },
 victory={
__VICTORY__
 },
 defeat={{speaker="",text="陈乞或鲍牧被击退，或未能完成高张战死、国夏出奔的历史目标，本关失败。"}}
}
local phase=1
local guoxia_id=0
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("GaoZhang81",1,Enum.force.enemy,{49,10});guoxia_id=game:generate_unit("GuoXia81",1,Enum.force.enemy,{49,31});game:set_unit_invulnerable("GuoXia81",true)
 many(game,"QiClanGuard81",{{14,18},{17,16},{17,20},{17,26},{17,30},{23,17},{23,25},{29,18},{29,24}},Enum.force.own)
 many(game,"QiClanArcher81",{{14,24},{20,14},{20,28},{27,15},{27,27}},Enum.force.own)
 many(game,"GaoHouseGuard81",{{40,9},{40,12},{44,7},{44,14},{48,6},{52,7},{52,14},{54,11}},Enum.force.enemy)
 many(game,"GaoHouseArcher81",{{42,5},{42,16},{50,5},{50,16}},Enum.force.enemy)
 many(game,"GuoHouseGuard81",{{40,29},{40,33},{44,26},{44,36},{48,25},{52,27},{52,35},{54,31}},Enum.force.enemy)
 many(game,"GuoHouseArcher81",{{42,25},{42,37},{50,25},{50,37}},Enum.force.enemy)
end
function on_update(game)
 if phase==1 and not game:has_unit("GaoZhang81")then phase=2;game:push_cmd_speak(guoxia_id,"高张已死，国夏弃府出奔莒国！各军让开西街，不必追杀。");game:push_cmd_move(guoxia_id,{1,38})end
end
function on_victory(game)end
function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if phase==2 and game:is_unit_within("GuoXia81",{1,38},2)then return Enum.status.victory end
 return Enum.status.undecided
end
gstage={title_id="Dongzhou81",turn_limit=30,map={blocked_edges={},size={60,42},terrain={
__ROWS__
},file="map.bmp"},deploy={unselectables={{position={10,19},hero="ChenQi81"},{position={10,23},hero="BaoMu81"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=24000}}
'''
    return text.replace("__INTRO__",lua_story(INTRO)).replace("__VICTORY__",lua_story(VICTORY)).replace("__ROWS__",terrain)


def update_config() -> None:
    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    if 'id = "ChenQi81"' not in text:
        block = "\n".join(f'        ,{{ id = "{hero}", class = "{klass}", stat = {{94,90,97,95,93}}, model = "{model}" }}' for hero,klass,model,_,_ in HEROES)
        marker = "    },\n    equipments = {}"
        assert marker in text
        text = text.replace(marker,"\n"+block+"\n"+marker,1)
    if '"80", "81" }' not in text:
        assert '"79", "80" }' in text
        text = text.replace('"79", "80" }','"79", "80", "81" }',1)
    path.write_text(text,encoding="utf-8")


def update_save() -> None:
    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8").replace("STAGE_TABLE_VERSION = 15","STAGE_TABLE_VERSION = 16",1)
    if '"79","80","81"' not in text:
        assert '"79","80"\n)' in text
        text = text.replace('"79","80"\n)','"79","80","81"\n)',1)
    path.write_text(text,encoding="utf-8")


def update_gui() -> None:
    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if "# Dongzhou chapter 81 metadata" in text:
        return
    labels = {hero:label for hero,_,_,label,_ in HEROES}
    bios = {hero:bio for hero,_,_,_,bio in HEROES}
    portraits = {"ChenQi81":49,"BaoMu81":35,"GaoZhang81":34,"GuoXia81":42,"QiClanGuard81":25,"QiClanArcher81":33,"GaoHouseGuard81":25,"GaoHouseArcher81":33,"GuoHouseGuard81":25,"GuoHouseArcher81":33,"GongZiYangSheng81":7,"XiShi81":21,"YueNv81":24,"ChenYin81":33,"ChenHeng81":49,"ZiGong81":45}
    speakers = {labels[hero]:portrait for hero,portrait in portraits.items()}
    addition = f'\n# Dongzhou chapter 81 metadata\n_LARGE_BATTLE_MAPS["m127.png"]=(60,42,48)\nHERO_LABELS.update({labels!r})\nHERO_BIOS.update({bios!r})\nPORTRAIT_INDEX_BY_HERO.update({portraits!r})\nSPEAKER_PORTRAIT_INDEX.update({speakers!r})\nHISTORICAL_DEATH_HEROES.update({{"GaoZhang81"}})\n\n'
    anchor = 'if _original_name == "__main__":'
    assert anchor in text
    path.write_text(text.replace(anchor,addition+anchor,1),encoding="utf-8")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest["terrain_rows"]
    assert manifest["grid"] == [60,42] and len(rows) == 42 and all(len(row) == 60 for row in rows)
    (ROOT / "game/sce/dongzhou/stage/81.lua").write_text(make_stage(rows),encoding="utf-8")
    update_config()
    update_save()
    update_gui()
    print("chapter 81 integrated: Linzi coup and full beauty-grain-training-diplomacy arc")


if __name__ == "__main__":
    main()