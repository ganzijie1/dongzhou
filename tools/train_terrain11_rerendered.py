from pathlib import Path
import json
import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report,confusion_matrix,f1_score
from terrain_self_evolve_11 import ROOT,OUT,CLASSES,NAMES,SEMANTICS,load

MODEL=ROOT/"output/terrain_model/terrain_11_rerendered.joblib";REPORT=ROOT/"output/terrain_model/terrain_11_rerendered_report.json"
def score(y,p):
 r=classification_report(y,p,labels=CLASSES,output_dict=True,zero_division=0);return{"macro_f1":float(f1_score(y,p,labels=CLASSES,average="macro")),"minimum_class_f1":float(min(r[c]["f1-score"]for c in CLASSES)),"classes":{c:r[c]for c in CLASSES},"confusion_matrix":confusion_matrix(y,p,labels=CLASSES).tolist()}
def main():
 d=json.loads((OUT/"manifest.json").read_text(encoding="utf-8"));train=[e for e in d["maps"]if e["split"]=="train"];val=[e for e in d["maps"]if e["split"]=="validation"];test=[e for e in d["maps"]if e["split"]=="test"]
 tx,ty=load(train);vx,vy=load(val);xx,xy=load(test);model=ExtraTreesClassifier(n_estimators=320,max_depth=28,max_features=.72,min_samples_leaf=1,class_weight="balanced_subsample",n_jobs=-1,random_state=20260812).fit(tx,ty);v=score(vy,model.predict(vx));t=score(xy,model.predict(xx));joblib.dump({"classifier":model,"classes":CLASSES,"names":NAMES,"semantics":SEMANTICS,"auto_apply":False},MODEL);payload={"render_domain":"reviewed MOD textures and production sprites","validation":v,"held_out_synthetic":t,"production_promotion":False,"requires_real_reviewed_test":True,"auto_apply":False};REPORT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps({"validation":v,"held_out":t},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
