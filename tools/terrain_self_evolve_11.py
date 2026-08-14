"""Generate 1000 truth-first maps and evolve an 11-class terrain model."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from terrain_semantic_model import image_cells


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/terrain_model/self_evolve_11"
MODEL = ROOT / "output/terrain_model/terrain_11_self_evolved.joblib"
REPORT = ROOT / "output/terrain_model/terrain_11_self_evolution_report.json"
CLASSES = ["f", "g", "s", "F", "m", "W", "C", "e", "P", "~", "v"]
NAMES = {"f":"平原","g":"草地","s":"雪地","F":"树林","m":"山地","W":"城墙","C":"城池","e":"营寨","P":"栅栏","~":"大河","v":"小河"}
SEMANTICS = {
    "f":{"passable":True,"supply":False}, "g":{"passable":True,"supply":False},
    "s":{"passable":True,"supply":False}, "F":{"passable":True,"supply":False},
    "m":{"passable":True,"supply":False}, "W":{"passable":False,"supply":False},
    "C":{"passable":True,"supply":True}, "e":{"passable":True,"supply":True},
    "P":{"passable":False,"supply":False}, "~":{"passable":False,"supply":False},
    "v":{"passable":True,"supply":False},
}
SEED=20260812; GW=12; GH=9; CELL=36


def natural_regions(rng):
    seeds=np.column_stack((rng.uniform(0,GW,8),rng.uniform(0,GH,8)))
    labels=rng.choice(5,8,p=[.24,.23,.13,.22,.18]); yy,xx=np.mgrid[0:GH,0:GW]
    dist=(xx[...,None]-seeds[:,0])**2+(yy[...,None]-seeds[:,1])**2
    grid=labels[dist.argmin(2)]
    for label in range(5):
        if not np.any(grid==label):grid[int(rng.integers(GH)),int(rng.integers(GW))]=label
    return np.asarray(CLASSES,dtype="U1")[grid]


def overlay_structures(grid,rng):
    # Deep river is a coherent impassable band; shallow river is a separate thin passable band.
    deep_x=int(rng.integers(1,4)); grid[:,deep_x]="~"
    shallow_y=int(rng.integers(1,GH-1)); grid[shallow_y,5:GW]="v"
    # Continuous wall with a two-cell opening; castle lies behind it and remains passable/supply.
    wall_y=int(rng.integers(1,4)); grid[wall_y,5:GW-1]="W"; grid[wall_y,8:10]="f"
    grid[max(0,wall_y-1),int(rng.integers(6,GW-1))]="C"
    # Center-axis fence rectangle with a one-cell gate; camp icon is inside, empty interior stays natural.
    x0,x1=6,10; y0,y1=max(4,wall_y+2),min(GH-1,wall_y+5)
    for x in range(x0,x1+1):grid[y0,x]=grid[y1,x]="P"
    for y in range(y0,y1+1):grid[y,x0]=grid[y,x1]="P"
    gate=(x0+x1)//2; grid[y1,gate]="f"
    if y1-y0>=2:grid[y0+1,gate]="e"
    # Guarantee all structural classes after occasional overlaps.
    required={"W":(5,wall_y),"C":(6,max(0,wall_y-1)),"e":(gate,y0+1),"P":(x0,y0),"~":(deep_x,GH-1),"v":(GW-1,shallow_y)}
    for c,(x,y) in required.items():grid[y,x]=c
    return grid


def texture(label,rng,snow_weather):
    n=CELL+12
    colors={"f":(151,137,99),"g":(91,126,67),"s":(221,227,223),"F":(65,96,53),"m":(113,103,89),
            "W":(133,126,113),"C":(146,111,62),"e":(142,62,48),"P":(93,66,42),"~":(34,67,112),"v":(100,176,211)}
    base=np.asarray(colors[label])+rng.integers(-10,11,3); noise=rng.normal(0,6,(n,n,1))
    im=Image.fromarray(np.clip(base+noise,0,255).astype(np.uint8),"RGB").convert("RGBA");d=ImageDraw.Draw(im,"RGBA")
    if label=="f":
        for _ in range(12):x,y=rng.integers(0,n,2);d.line((x,y,min(n,x+12),y),fill=(80,67,45,90),width=1)
    elif label=="g":
        for _ in range(35):x,y=rng.integers(0,n,2);d.line((x,y,x-1,max(0,y-7)),fill=(36,78,33,150),width=1)
    elif label=="s":
        for _ in range(8):x,y=rng.integers(0,n,2);d.arc((x-8,y-3,x+8,y+5),190,350,fill=(113,145,164,75),width=2)
    elif label=="F":
        if snow_weather:d.rectangle((0,0,n,n),fill=(190,202,193,145))
        for _ in range(16):
            x,y=rng.integers(4,n-4,2);r=int(rng.integers(4,8));d.ellipse((x-r,y-r//2,x+r,y+r),fill=(32,75,36,235));d.line((x,y,x,y+r+4),fill=(70,47,30,220),width=2)
            if snow_weather:d.arc((x-r,y-r//2,x+r,y+r//2),180,355,fill=(239,243,240,230),width=2)
    elif label=="m":
        if snow_weather:d.rectangle((0,0,n,n),fill=(185,190,187,125))
        for _ in range(8):
            x,y=rng.integers(5,n-5,2);rw=int(rng.integers(8,15));rh=int(rng.integers(7,14));d.polygon([(x-rw,y+rh),(x,y-rh),(x+rw,y+rh)],fill=(86,79,70,245),outline=(55,53,50,255))
            if snow_weather:d.line((x,y-rh,x+rw//2,y+rh//3),fill=(240,243,241,235),width=3)
    elif label=="W":
        for y in range(5,n,12):d.rectangle((1,y,n-2,min(n,y+8)),outline=(65,61,57,230),width=2)
        for x in range(0,n,16):d.line((x,0,x,n),fill=(75,68,61,180),width=2)
    elif label=="C":
        d.rectangle((5,14,n-6,n-6),fill=(117,75,48,255),outline=(54,45,39,255),width=3);d.polygon([(1,15),(n//2,2),(n-2,15)],fill=(57,68,67,255));d.rectangle((n//2-4,n-17,n//2+4,n-6),fill=(49,39,31,255))
    elif label=="e":
        d.polygon([(3,n-7),(n//2,5),(n-3,n-7)],fill=(153,47,40,255),outline=(72,42,34,255));d.line((n//2,5,n//2,n-4),fill=(68,48,31,255),width=3)
    elif label=="P":
        d.line((0,n//2,n,n//2),fill=(58,38,25,255),width=6)
        for x in range(5,n,13):d.line((x,4,x,n-4),fill=(80,51,30,255),width=5)
    elif label in {"~","v"}:
        for y in range(4,n,10):d.arc((-5,y,n+5,y+7),190,350,fill=((137,188,220,150) if label=="~" else (225,245,250,190)),width=2)
    return im.filter(ImageFilter.GaussianBlur(.25))


def render(grid,rng):
    canvas=Image.new("RGBA",(GW*CELL,GH*CELL),(120,110,80,255));snow=bool(rng.random()<.35)
    for y in range(GH):
        for x in range(GW):canvas.alpha_composite(texture(grid[y,x],rng,snow),(x*CELL-6,y*CELL-6))
    im=canvas.convert("RGB");im=ImageEnhance.Color(im).enhance(float(rng.uniform(.9,1.12)));im=ImageEnhance.Contrast(im).enhance(float(rng.uniform(.94,1.08)));return im


def make(index,split):
    rng=np.random.default_rng(SEED+index*1009);grid=overlay_structures(natural_regions(rng),rng);im=render(grid,rng)
    path=OUT/split/f"terrain-{index:04d}.png";path.parent.mkdir(parents=True,exist_ok=True);im.save(path,"PNG",optimize=True)
    return {"id":index,"split":split,"image":str(path.relative_to(ROOT)),"grid":[GW,GH],"rows":["".join(r)for r in grid]}


def load(entries):
    xs=[];ys=[]
    for e in entries:
        xs.append(image_cells(Image.open(ROOT/e["image"]).convert("RGB"),GW,GH));ys.extend("".join(e["rows"]))
    return np.concatenate(xs),np.asarray(ys)


def scores(y,p):
    cr=classification_report(y,p,labels=CLASSES,output_dict=True,zero_division=0)
    return {"accuracy":float(accuracy_score(y,p)),"macro_f1":float(f1_score(y,p,labels=CLASSES,average="macro")),"minimum_class_f1":float(min(cr[c]["f1-score"]for c in CLASSES)),"classes":{c:cr[c]for c in CLASSES},"confusion_matrix":confusion_matrix(y,p,labels=CLASSES).tolist()}


def montage(entries):
    out=Image.new("RGB",(5*288,5*216),(25,25,25))
    for i,e in enumerate(entries[:25]):out.paste(Image.open(ROOT/e["image"]).resize((288,216)),((i%5)*288,(i//5)*216))
    out.save(OUT/"test_montage.png","PNG")


def run():
    if OUT.exists():shutil.rmtree(OUT)
    entries=[make(i,"train" if i<800 else "validation" if i<900 else "test")for i in range(1000)]
    train=[e for e in entries if e["split"]=="train"];val=[e for e in entries if e["split"]=="validation"];test=[e for e in entries if e["split"]=="test"]
    vx,vy=load(val);history=[];best=None;model=None
    for generation,count in enumerate((200,500,800),1):
        tx,ty=load(train[:count]);candidate=ExtraTreesClassifier(n_estimators=220,max_depth=24,max_features=.75,min_samples_leaf=1,class_weight="balanced_subsample",n_jobs=-1,random_state=SEED+generation).fit(tx,ty);result=scores(vy,candidate.predict(vx));promote=best is None or(result["macro_f1"]>=best["macro_f1"]and result["minimum_class_f1"]>=best["minimum_class_f1"]);history.append({"generation":generation,"training_maps":count,"validation":result,"promoted":promote});
        if promote:best=result;model=candidate
    xx,xy=load(test);held=scores(xy,model.predict(xx));accepted=held["macro_f1"]>=.92 and held["minimum_class_f1"]>=.85 and all(held["classes"][c]["recall"]>=.85 for c in CLASSES)
    counts=Counter("".join("".join(e["rows"])for e in entries));manifest={"version":2,"classes":NAMES,"semantics":SEMANTICS,"water_rule":"浅蓝小河v可通过；深蓝大河~不可跨越","snow_rule":"只有白色开阔地是雪地s；白色树林/山地仍是F/m","split":{"train":800,"validation":100,"test":100},"class_cells":dict(counts),"maps":entries};(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8");montage(test)
    joblib.dump({"classifier":model,"classes":CLASSES,"names":NAMES,"semantics":SEMANTICS,"confidence_threshold":.72,"auto_apply":False},MODEL)
    report={"maps_generated":1000,"classes":NAMES,"split_by_complete_map":True,"truth_source":"pre-render programmatic matrices","evolution":history,"held_out_test":held,"synthetic_acceptance":accepted,"production_promotion":False,"auto_apply":False};REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps({"maps":1000,"class_cells":dict(counts),"held_out":held,"accepted":accepted},ensure_ascii=False,indent=2))


if __name__=="__main__":run()
