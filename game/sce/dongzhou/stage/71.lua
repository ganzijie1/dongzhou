gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"TianKaiJiang71","GuYeZi71"}
gevents_enabled=true
gduel_enabled=true
gduels={{attacker="TianKaiJiang71",defender="YingShuang71",exp=90,outcome="kill",attacker_speech="嬴爽，蒲隧便是你的葬身之地！",defender_speech="田开疆休得夸口！",result_speech="田开疆突入徐阵，斩杀嬴爽！",text="田开疆阵斩嬴爽。"}}
gsites={{id="xu_castle",name="徐城",position={43,14},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}
gstory={chapter="第七十一回",title="晏平仲二桃杀三士 楚平王娶媳逐世子",battle_title="蒲隧之战",objective="田开疆斩嬴爽，击破徐军并迫使徐君请降。",map_asset="m120.png",
 intro={
  {speaker="",text="齐景公欲伐徐国，以田开疆、古冶子为将，率军推进蒲隧。徐军依河与西城列阵。"},
  {speaker="田开疆",text="徐将嬴爽已在河东挑战。我先破其前阵，诸军再越浅水逼近徐城。"},
  {speaker="古冶子",text="深水不可过，浅河可以通行。弓手压住城头，步卒沿两处滩口并进。"},
  {speaker="嬴爽",text="齐军远来，粮道绵长。谁敢越蒲隧一步，我便取谁首级！"},
  {speaker="军令",text="击破蒲隧守军。田开疆与嬴爽相邻可触发史实单挑并直接斩杀；两名我方将领被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="田开疆",text="嬴爽已经出阵。斩将后直取徐城！"}
 },
 victory={
  {speaker="",text="田开疆临阵斩嬴爽，徐军失去先锋。齐军渡过蒲隧，徐君遣使献地请降。"},
  {speaker="徐君",text="徐国愿奉齐国为盟主，岁时纳贡，只求保全宗庙百姓。"},
  {speaker="",text="田开疆班师后与公孙捷、古冶子同受齐景公宠信。三人勇力过人，却不知礼数，晏婴深以为忧。"},
  {speaker="晏婴",text="三勇士功高而不知君臣之礼，一旦为乱，无人能制。可赐二桃，令三人各叙功劳，自取其桃。"},
  {speaker="",text="公孙捷、田开疆先取二桃。古冶子叙说黄河斩鼋救主之功，两人羞惭自刎；古冶子也因独生无义而自尽。"},
  {speaker="齐景公",text="寡人只想抑制三士，岂料三人皆死。厚葬他们，以全旧日君臣之情。"},
  {speaker="",text="楚平王听信费无极，为太子建聘秦女孟嬴。费无极见孟嬴绝色，竟劝平王自娶，以陪嫁齐女冒充太子妃。"},
  {speaker="伍奢",text="夺子之妻、废嫡之母，乱伦败国。费无极只求自固，必将太子逼反。"},
  {speaker="",text="楚平王囚伍奢，召其二子伍尚、伍员入郢。伍尚决意赴死，伍员识破诱杀，带太子建之子公子胜出逃。"},
  {speaker="军令",text="蒲隧之战完成，获得1600金币。下一关：昭关脱逃。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("YingShuang71",1,Enum.force.enemy,{28,17});game:generate_unit("XuJun71",1,Enum.force.enemy,{43,14});many(game,"QiGuard71",{{5,27},{8,33},{12,28},{13,34}},Enum.force.own);many(game,"QiArcher71",{{4,31},{11,31}},Enum.force.own);many(game,"XuGuard71",{{25,15},{26,19},{34,14},{35,18},{39,11},{39,20}},Enum.force.enemy);many(game,"XuArcher71",{{29,13},{31,21},{42,9},{46,18}},Enum.force.enemy)
end
function on_update(game)

end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if game:get_num_enemies_alive()==0 then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou71",turn_limit=24,map={blocked_edges={},size={52,38},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffF",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggff",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfgg",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffF",
        "fffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffggFf",
        "gffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffgg",
        "fFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffff",
        "vvvgFffffFgfffggffFfggffffgFfffgFWWWWWWWWWWWWWWWWgFf",
        "vvvvvvgffffgFfffggfffFggffFfggfffWiiiiiiiiiiiiiiWFgg",
        "vvvvvvvvvffffggFffggFfffggfffFggfWiiiiiiiiiiiiiiWfff",
        "FffvvvvvvvvvffFggfffggfFffggffffFWiiiiiiiiiiiiiiWggf",
        "ggfFfgvvvvvvvvvffFgfffggffFfggfFfWiiiiiiiiiiiiiiWFfg",
        "ffFgfffggvvvvvvvvvfgFfffgFffffggfWiiiiiiiiiiiiiiWfff",
        "ffffgFfffggfvvvvvvvvvggfffggFfffgWiiiiiiiiiiiiiiWggF",
        "ggffffggFffggFfvvvvvvvvvgfffggfFfWiiiiiiiiiCiiiiWffg",
        "ffFgfffFggfffggfFfvvvvvvvvvfffFgfGiiiiiiiiiiiiiiWfff",
        "fFffggffffFgfffggffFfvvvvvvvvvffgGiiiiiiiiiiiiiiWggf",
        "ggffFfggffffgFfffgFffffgvvvvvvvvvWiiiiiiiiiiiiiiWfFg",
        "ffggfffFggffFfggfffggFfffggvvvvvvWiiiiiiiiiiiiiiWgff",
        "gFffggFfffggfffFggfffggfFffggFvvvWiiiiiiiiiiiiiiWfgg",
        "FggfffggfFffggffffFgfffFgffffggfFWiiiiiiiiiiiiiiWfff",
        "fffFgfffggffFfggfFffggfffgFffffggWiiiiiiiiiiiiiiWFff",
        "gffffgFfffgFffffggffFfggfffggFfffWiiiiiiiiiiiiiiWfgg",
        "FggffFfggfffggFfffggfffFggffFggffWiiiiiiiiiiiiiiWvvF",
        "fffggfffFggfffggfFffggFfffggfffFgWWWWWWWWWWWWWWWWvvv",
        "gfFffggffffFgfffFgffffggfFffggfffgFffffFgffffggfvvvv",
        "fggffFfggfFffggfffgFffffggffFfggfFfggffffgFffffggffv",
        "fffgFffffggffFfggfffggFfffgFffffggffFggffffggFfffgFf",
        "ggfffggFfffggfffFggffFggffffggFfffggfffFgfffFggffffg",
        "fFggfffggfFffggFfffggfffFgffffggfFffggFffggffffFgfff",
        "ffffFgfffFgffffggfFffggfffgFffffFgffffggfFfggffffgFf",
        "ggfFffggfffgFffffggffFfggfFfggffffgFffffggffFggffFfg",
        "ffggffFfggfffggFfffgFffffggffFggffffggFfffgFfffggfff",
        "FfffggfffFggffFggffffggFfffggfffFgfffFggffffggFffggf",
        "ggfFffggFfffggfffFgffffggfFffggFffggffffFgffffggfFfg",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFgff",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgF",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffff",
},file="map.bmp"},deploy={unselectables={{position={7,29},hero="TianKaiJiang71"},{position={10,31},hero="GuYeZi71"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=16000}}
