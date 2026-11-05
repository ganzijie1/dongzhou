#!/usr/bin/env python3
"""Serve a local blind-review workbench for contextual dialogue voice candidates."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_file


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
REVIEW_PATH = ROOT / "output" / "voice-production" / "contextual-human-review.json"
REQUIRED_RATINGS = (
    "naturalness",
    "intelligibility",
    "breathPause",
    "speedEnergy",
    "genderAge",
    "roleIdentity",
    "historicalContext",
    "performanceCredibility",
)
HARD_ERRORS = ("text", "genderAge", "roleIdentity", "historicalContext", "audioArtifact")
REVIEW_SCOPES = ("isolatedUtterance", "dialoguePair", "fullScene")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def load_index() -> dict:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def load_reviews() -> dict:
    if REVIEW_PATH.exists():
        return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    return {"schemaVersion": 1, "reviews": []}


def write_reviews(payload: dict) -> None:
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_audio(entry_id: str, candidate_number: int) -> Path:
    index = load_index()
    entry = next((item for item in index["entries"] if item["entryId"] == entry_id), None)
    if not entry:
        raise FileNotFoundError(entry_id)
    candidate = next((item for item in entry["candidates"] if int(item["candidate"]) == candidate_number), None)
    if not candidate:
        raise FileNotFoundError(candidate_number)
    relative = Path(candidate["file"])
    path = (ROOT / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or ROOT.resolve() not in path.parents or not path.is_file():
        raise FileNotFoundError(relative)
    return path


def blind_label(entry_id: str, candidate_number: int) -> str:
    digest = hashlib.sha256(f"dongzhou-blind-v1|{entry_id}|{candidate_number}".encode()).digest()
    return f"样本 {chr(65 + digest[0] % 26)}{digest[1] % 10}"


def public_index() -> dict:
    index = load_index()
    reviews = load_reviews()["reviews"]
    reviewed = {(item["entryId"], int(item["candidate"])) for item in reviews}
    entries = []
    for entry in index["entries"]:
        candidates = [
            {
                "candidate": int(item["candidate"]),
                "label": blind_label(entry["entryId"], int(item["candidate"])),
                "audioUrl": f"/audio/{entry['entryId']}/{item['candidate']}",
                "reviewed": (entry["entryId"], int(item["candidate"])) in reviewed,
            }
            for item in entry.get("candidates", [])
        ]
        candidates.sort(key=lambda item: item["label"])
        context = entry.get("context", {})
        entries.append({
            "entryId": entry["entryId"],
            "speaker": entry["speaker"],
            "text": entry["text"],
            "expectedGender": entry.get("expectedGender"),
            "expectedAgeBand": entry.get("expectedAgeBand"),
            "historicalSituation": context.get("historicalSituation", {}),
            "speakerAtScene": context.get("speakerAtScene", {}),
            "speechAct": context.get("speechAct", ""),
            "performanceState": context.get("performanceState", {}),
            "previousTurns": context.get("previousTurns", []),
            "nextTurns": context.get("nextTurns", []),
            "candidates": candidates,
        })
    entries.sort(key=lambda item: (item["speaker"], item["entryId"]))
    return {"entries": entries, "reviewCount": len(reviews)}


def validate_review(data: dict) -> tuple[bool, str]:
    ratings = data.get("ratings") or {}
    for name in REQUIRED_RATINGS:
        value = ratings.get(name)
        if not isinstance(value, int) or not 1 <= value <= 5:
            return False, f"缺少有效评分：{name}"
    hard_errors = data.get("hardErrors") or {}
    if any(name not in hard_errors or not isinstance(hard_errors[name], bool) for name in HARD_ERRORS):
        return False, "硬错误字段不完整"
    review_scopes = data.get("reviewScopes") or {}
    if any(name not in review_scopes or not isinstance(review_scopes[name], bool) for name in REVIEW_SCOPES):
        return False, "试听范围字段不完整"
    if data.get("anchorApproved"):
        if any(hard_errors.values()):
            return False, "存在硬错误时不能批准为锚点"
        for name in ("genderAge", "roleIdentity", "historicalContext"):
            if ratings[name] < 4:
                return False, "性别年龄、角色身份和史实语境至少需要 4 分"
        if ratings["naturalness"] < 3 or ratings["intelligibility"] < 4:
            return False, "锚点的自然度至少 3 分、可懂度至少 4 分"
        if not all(review_scopes.values()):
            return False, "批准锚点前必须完成单句、相邻对话和完整场景三层试听"
    return True, ""


def update_anchor_state(review: dict) -> None:
    index = load_index()
    for entry in index["entries"]:
        if entry["speaker"] != review["speaker"]:
            continue
        if review.get("anchorApproved"):
            entry["approvedAnchorCandidate"] = int(review["candidate"]) if entry["entryId"] == review["entryId"] else None
            entry["gates"]["humanReview"] = "anchor_approved_single_reviewer"
            entry["gates"]["identity"] = "pending_cross_sentence_samples"
        entry["promotionEligible"] = False
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home() -> Response:
        return Response(HTML, content_type="text/html; charset=utf-8")

    @app.get("/api/index")
    def api_index():
        return jsonify(public_index())

    @app.get("/api/reviews")
    def api_reviews():
        return jsonify(load_reviews())

    @app.get("/audio/<entry_id>/<int:candidate_number>")
    def audio(entry_id: str, candidate_number: int):
        return send_file(safe_audio(entry_id, candidate_number), mimetype="audio/wav", conditional=True)

    @app.post("/api/review")
    def save_review():
        data = request.get_json(force=True)
        valid, message = validate_review(data)
        if not valid:
            return jsonify({"ok": False, "error": message}), 400
        index = load_index()
        entry = next((item for item in index["entries"] if item["entryId"] == data.get("entryId")), None)
        if not entry or entry["speaker"] != data.get("speaker"):
            return jsonify({"ok": False, "error": "台词或角色不匹配"}), 400
        safe_audio(data["entryId"], int(data["candidate"]))
        review = {
            "entryId": data["entryId"],
            "speaker": data["speaker"],
            "candidate": int(data["candidate"]),
            "blindLabel": blind_label(data["entryId"], int(data["candidate"])),
            "ratings": data["ratings"],
            "hardErrors": data["hardErrors"],
            "reviewScopes": data["reviewScopes"],
            "breathConfirmed": data.get("breathConfirmed", "not_reviewed"),
            "anchorApproved": bool(data.get("anchorApproved")),
            "notes": str(data.get("notes") or "").strip(),
            "reviewer": getpass.getuser(),
            "reviewedAt": datetime.now(timezone.utc).isoformat(),
            "scope": "single_reviewer_anchor_screen",
        }
        payload = load_reviews()
        payload["reviews"] = [
            item for item in payload["reviews"]
            if not (item["entryId"] == review["entryId"] and int(item["candidate"]) == review["candidate"] and item.get("reviewer") == review["reviewer"])
        ]
        if review["anchorApproved"]:
            for item in payload["reviews"]:
                if item["speaker"] == review["speaker"]:
                    item["anchorApproved"] = False
        payload["reviews"].append(review)
        write_reviews(payload)
        update_anchor_state(review)
        return jsonify({"ok": True, "review": review})

    return app


HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>东周角色语音盲听审核</title>
  <style>
    :root { color-scheme: dark; --bg:#111310; --panel:#1a1d18; --line:#3a4034; --text:#ecefe7; --muted:#aeb6a5; --gold:#c9a85e; --red:#ba5b4d; --green:#6e9d73; }
    * { box-sizing:border-box; letter-spacing:0; }
    body { margin:0; font:15px/1.55 system-ui,"Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); }
    header { position:sticky; top:0; z-index:4; background:#111310f2; border-bottom:1px solid var(--line); padding:14px 22px; display:flex; gap:18px; align-items:center; }
    h1 { margin:0; font-size:20px; font-weight:650; }
    #progress { color:var(--muted); margin-left:auto; }
    main { display:grid; grid-template-columns:260px minmax(0,1fr); min-height:calc(100vh - 61px); }
    nav { border-right:1px solid var(--line); padding:12px; position:sticky; top:61px; height:calc(100vh - 61px); overflow:auto; }
    nav button { width:100%; text-align:left; color:var(--text); background:transparent; border:0; border-bottom:1px solid #272b24; padding:10px; cursor:pointer; }
    nav button.active { background:#25291f; color:#f2d48b; }
    article { padding:26px clamp(18px,4vw,60px) 80px; max-width:1120px; }
    h2 { font-size:24px; margin:0 0 5px; } h3 { font-size:16px; margin:24px 0 8px; }
    .meta,.context { color:var(--muted); } .line { font-size:19px; padding:15px 0; border-bottom:1px solid var(--line); }
    .context { background:#171914; border-left:3px solid var(--gold); padding:12px 14px; margin:14px 0 22px; }
    .candidate { border:1px solid var(--line); border-radius:6px; padding:16px; margin:12px 0; background:var(--panel); }
    .candidate-head { display:flex; align-items:flex-start; flex-direction:column; gap:8px; } audio { width:min(100%,520px); min-width:0; height:36px; }
    .candidate.reviewed { border-color:var(--green); }
    .ratings { display:grid; grid-template-columns:repeat(4,minmax(130px,1fr)); gap:10px 14px; margin-top:15px; }
    label { color:var(--muted); font-size:13px; } select,textarea { width:100%; margin-top:4px; color:var(--text); background:#10120f; border:1px solid var(--line); border-radius:4px; padding:8px; }
    .errors { display:flex; flex-wrap:wrap; gap:8px 18px; margin:15px 0; }
    .errors label,.anchor { color:var(--text); font-size:14px; }
    input[type=checkbox] { accent-color:var(--red); }
    .actions { display:flex; align-items:center; gap:16px; margin-top:12px; }
    button.save { background:#8f392f; border:1px solid #ca6c5d; color:white; border-radius:4px; padding:9px 16px; cursor:pointer; }
    .status { color:var(--muted); } .error { color:#ef8f80; }
    @media(max-width:800px){ main{display:block} nav{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);display:flex;overflow:auto} nav button{min-width:150px} article{padding:20px 14px 60px}.ratings{grid-template-columns:repeat(2,minmax(120px,1fr))}.candidate-head{align-items:flex-start;flex-direction:column}.candidate-head audio{width:100%;min-width:0} header{padding:12px 14px;flex-wrap:wrap} }
  </style>
</head>
<body>
<header><h1>东周角色语音盲听审核</h1><span id="progress">载入中</span></header>
<main><nav id="nav"></nav><article id="content"></article></main>
<script>
const ratingNames={naturalness:'自然度',intelligibility:'可懂度',breathPause:'呼吸与停顿',speedEnergy:'语速与能量',genderAge:'性别年龄匹配',roleIdentity:'角色身份匹配',historicalContext:'史实语境匹配',performanceCredibility:'表演可信度'};
const errorNames={text:'文本或专名错误',genderAge:'性别年龄硬错',roleIdentity:'角色身份硬错',historicalContext:'史实语境硬错',audioArtifact:'爆音、断裂或伪影'};
let data, active=0;
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function contextLines(items){return items.slice(-2).map(x=>`${esc(x.speaker||'旁白')}：${esc(x.text)}`).join('<br>');}
function render(){
 const nav=document.querySelector('#nav'); nav.innerHTML=data.entries.map((e,i)=>`<button class="${i===active?'active':''}" onclick="active=${i};render()">${esc(e.speaker)}<br><small>${e.candidates.filter(x=>x.reviewed).length}/${e.candidates.length} 已审</small></button>`).join('');
 const e=data.entries[active], age=e.speakerAtScene.estimatedAgeRange||e.expectedAgeBand;
 const cards=e.candidates.map(c=>candidateCard(e,c)).join('');
 const p=e.performanceState||{}, focus=(p.focusWords||[]).join('、')||'按语义自然选择', pivot=(p.pivotWords||[]).join('、')||'无显式转折';
 document.querySelector('#content').innerHTML=`<h2>${esc(e.speaker)}</h2><div class="meta">${esc(e.expectedGender)} · ${esc(age)} · ${esc(e.historicalSituation.chapter||'')} ${esc(e.historicalSituation.stageTitle||'')}</div><div class="line">${esc(e.text)}</div><div class="context"><b>剧情状态</b><br>言语行为：${esc(e.speechAct)}<br>状态：${esc(p.emotionBefore||'scene_baseline')} → ${esc(p.emotionAfter||'')}<br>潜台词：${esc(p.subtext||'')}<br>转折词：${esc(pivot)}；重音目标：${esc(focus)}<br>停连要求：${esc(p.pausePlan||'')}<br><br><b>前文</b><br>${contextLines(e.previousTurns)||'无'}<br><br><b>后文</b><br>${contextLines(e.nextTurns)||'无'}</div><h3>盲听候选</h3>${cards}`;
 const reviewed=data.entries.reduce((n,x)=>n+x.candidates.filter(c=>c.reviewed).length,0), total=data.entries.reduce((n,x)=>n+x.candidates.length,0); document.querySelector('#progress').textContent=`${reviewed} / ${total} 已审核`;
}
function ratingOptions(){return '<option value="">未评分</option>'+[1,2,3,4,5].map(x=>`<option value="${x}">${x}</option>`).join('');}
function candidateCard(e,c){
 const ratings=Object.entries(ratingNames).map(([k,v])=>`<label>${v}<select data-rating="${k}">${ratingOptions()}</select></label>`).join('');
 const errors=Object.entries(errorNames).map(([k,v])=>`<label><input type="checkbox" data-error="${k}"> ${v}</label>`).join('');
 return `<section class="candidate ${c.reviewed?'reviewed':''}" data-entry="${e.entryId}" data-candidate="${c.candidate}"><div class="candidate-head"><b>${esc(c.label)}</b><audio controls preload="none" src="${c.audioUrl}"></audio></div><div class="ratings">${ratings}</div><div class="errors">${errors}</div><div class="errors"><label><input type="checkbox" data-scope="isolatedUtterance"> 已听单句</label><label><input type="checkbox" data-scope="dialoguePair"> 已连听前后对话</label><label><input type="checkbox" data-scope="fullScene"> 已听完整场景</label></div><label>呼吸事件确认<select data-breath><option value="not_reviewed">未逐事件检查</option><option value="natural">自然</option><option value="missing">缺少必要呼吸</option><option value="excessive">呼吸过多</option><option value="misplaced">位置错误</option></select></label><label>审核备注<textarea rows="2" data-notes></textarea></label><div class="actions"><label class="anchor"><input type="checkbox" data-anchor> 批准为角色锚点候选</label><button class="save" onclick="saveReview(this)">保存审核</button><span class="status"></span></div></section>`;
}
async function saveReview(button){
 const card=button.closest('.candidate'), ratings={}, hardErrors={}; card.querySelectorAll('[data-rating]').forEach(x=>ratings[x.dataset.rating]=Number(x.value)); card.querySelectorAll('[data-error]').forEach(x=>hardErrors[x.dataset.error]=x.checked);
 const reviewScopes={}; card.querySelectorAll('[data-scope]').forEach(x=>reviewScopes[x.dataset.scope]=x.checked);
 const e=data.entries[active], payload={entryId:e.entryId,speaker:e.speaker,candidate:Number(card.dataset.candidate),ratings,hardErrors,reviewScopes,breathConfirmed:card.querySelector('[data-breath]').value,anchorApproved:card.querySelector('[data-anchor]').checked,notes:card.querySelector('[data-notes]').value};
 const status=card.querySelector('.status'); status.textContent='保存中'; status.className='status';
 const res=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const body=await res.json(); if(!res.ok){status.textContent=body.error;status.className='status error';return;} c=data.entries[active].candidates.find(x=>x.candidate===payload.candidate); c.reviewed=true; status.textContent='已保存；正式上线仍未批准'; card.classList.add('reviewed'); renderProgress();
}
function renderProgress(){const reviewed=data.entries.reduce((n,x)=>n+x.candidates.filter(c=>c.reviewed).length,0),total=data.entries.reduce((n,x)=>n+x.candidates.length,0);document.querySelector('#progress').textContent=`${reviewed} / ${total} 已审核`;}
fetch('/api/index').then(r=>r.json()).then(x=>{data=x;render();}).catch(e=>document.querySelector('#content').textContent=e);
</script>
</body></html>'''


if __name__ == "__main__":
    args = parse_args()
    create_app().run(host=args.host, port=args.port, debug=False)
