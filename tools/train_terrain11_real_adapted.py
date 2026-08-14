"""Train a hierarchical terrain model with grouped real-map supervision."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from terrain_semantic_model import image_cells


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/terrain_model/terrain_11_real_adapted.joblib"
REPORT=ROOT/"output/terrain_model/terrain_11_real_adapted_report.json"
NATURAL=np.asarray(["f","g","s","F","m","v"])
REAL_NATURAL=np.asarray(["f","g","F","m"])
STRUCTURE=np.asarray(["W","C","e","P","~"])
TEST={"m064","m066","m076","m081","m084","m086","m089","m091"}
VALIDATION={"m058","m065","m074","m079","m087"}
SEED=20260812


def manifest_id(path):return path.name.split("_")[0]


def load_real(split):
 xs=[];ys=[];groups=[]
 for path in sorted((ROOT/"assets/lzc/map_sources").glob("m*_manifest.json")):
  mid=manifest_id(path)
  target="test"if mid in TEST else"validation"if mid in VALIDATION else"train"
  if target!=split:continue
  d=json.loads(path.read_text(encoding="utf-8"));rows=d.get("terrain_rows",[]);grid=d.get("grid",[]);image=ROOT/d.get("map","")
  if len(grid)!=2 or len(rows)!=grid[1]or not image.is_file():continue
  y=np.asarray(list("".join(rows)));eligible=np.isin(y,np.concatenate((REAL_NATURAL,STRUCTURE)))
  x=image_cells(Image.open(image).convert("RGB"),int(grid[0]),int(grid[1]))
  xs.append(x[eligible]);ys.append(y[eligible]);groups.extend([mid]*int(eligible.sum()))
 return np.concatenate(xs),np.concatenate(ys),np.asarray(groups)


def load_synthetic_special(limit=800):
 d=json.loads((ROOT/"output/terrain_model/self_evolve_11/manifest.json").read_text(encoding="utf-8"));xs=[];ys=[]
 for e in [x for x in d["maps"]if x["split"]=="train"][:limit]:
  y=np.asarray(list("".join(e["rows"])));mask=np.isin(y,["s","v"])
  if not mask.any():continue
  x=image_cells(Image.open(ROOT/e["image"]).convert("RGB"),*e["grid"]);xs.append(x[mask]);ys.append(y[mask])
 return np.concatenate(xs),np.concatenate(ys)


def forest(seed):return ExtraTreesClassifier(n_estimators=320,max_depth=28,max_features=.72,min_samples_leaf=1,class_weight="balanced",n_jobs=-1,random_state=seed)


def fit_hierarchy(x,y):
 gate_y=np.where(np.isin(y,STRUCTURE),"structure","natural");gate=forest(SEED).fit(x,gate_y)
 natural_mask=np.isin(y,REAL_NATURAL);sx,sy=load_synthetic_special();nx=np.concatenate((x[natural_mask],sx));ny=np.concatenate((y[natural_mask],sy));nw=np.concatenate((np.full(natural_mask.sum(),8.0),np.full(len(sy),.65)))
 natural=forest(SEED+1).fit(nx,ny,sample_weight=nw)
 structure_mask=np.isin(y,STRUCTURE);structure=forest(SEED+2).fit(x[structure_mask],y[structure_mask])
 return gate,natural,structure


def predict(bundle,x):
 gate=bundle["gate"].predict(x);out=np.empty(len(x),dtype="<U1");sm=gate=="structure";out[~sm]=bundle["natural"].predict(x[~sm]);out[sm]=bundle["structure"].predict(x[sm]);return out


def score(y,p):
 labels=REAL_NATURAL.tolist()+STRUCTURE.tolist();r=classification_report(y,p,labels=labels,output_dict=True,zero_division=0);supported=[c for c in labels if r[c]["support"]]
 return {"macro_f1_supported":float(np.mean([r[c]["f1-score"]for c in supported])),"minimum_class_f1":float(min(r[c]["f1-score"]for c in supported)),"classes":{c:r[c]for c in labels},"confusion_matrix":confusion_matrix(y,p,labels=labels).tolist()}


def main():
 tx,ty,tg=load_real("train");vx,vy,vg=load_real("validation");xx,xy,xg=load_real("test")
 candidate={};candidate["gate"],candidate["natural"],candidate["structure"]=fit_hierarchy(tx,ty)
 val=score(vy,predict(candidate,vx));test=score(xy,predict(candidate,xx))
 # Synthetic-only audit for classes without reviewed real fixtures.
 sd=json.loads((ROOT/"output/terrain_model/self_evolve_11/manifest.json").read_text(encoding="utf-8"));special=[e for e in sd["maps"]if e["split"]=="test"];sx=[];sy=[]
 for e in special:
  y=np.asarray(list("".join(e["rows"])));m=np.isin(y,["s","v"]);x=image_cells(Image.open(ROOT/e["image"]).convert("RGB"),*e["grid"]);sx.append(x[m]);sy.append(y[m])
 sx=np.concatenate(sx);sy=np.concatenate(sy);sp=candidate["natural"].predict(sx);sr=classification_report(sy,sp,labels=["s","v"],output_dict=True,zero_division=0)
 production=(test["macro_f1_supported"]>=.80 and test["minimum_class_f1"]>=.55 and all(test["classes"][c]["recall"]>=.55 for c in REAL_NATURAL.tolist()+STRUCTURE.tolist()))
 bundle={**candidate,"natural_classes":NATURAL.tolist(),"structure_classes":STRUCTURE.tolist(),"confidence_threshold":.72,"production_promotion":production,"auto_apply":False,"semantics":{"W":"impassable","P":"impassable","~":"impassable deep river","C":"passable supply candidate","e":"passable supply candidate","v":"passable shallow river","s":"passable snow"}}
 joblib.dump(bundle,OUT)
 payload={"split":"grouped by complete reviewed map","training_maps":sorted(set(tg)),"validation_maps":sorted(set(vg)),"test_maps":sorted(set(xg)),"training_cells":len(ty),"validation_cells":len(vy),"test_cells":len(xy),"validation":val,"held_out_real_test":test,"synthetic_only_unverified":{"s":sr["s"],"v":sr["v"]},"production_promotion":production,"auto_apply":False}
 REPORT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(payload,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
