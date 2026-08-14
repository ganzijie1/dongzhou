from pathlib import Path
import json
import joblib

ROOT=Path(__file__).resolve().parents[1]

def main():
 manifest=json.loads((ROOT/'output/terrain_model/self_evolve_11/manifest.json').read_text(encoding='utf-8'))
 synthetic=json.loads((ROOT/'output/terrain_model/terrain_11_rerendered_report.json').read_text(encoding='utf-8'))
 real=json.loads((ROOT/'output/terrain_model/terrain_11_rerendered_real_domain_report.json').read_text(encoding='utf-8'))
 expected={'f','g','s','F','m','W','C','e','P','~','v'}
 assert manifest['split']=={'train':800,'validation':100,'test':100}
 assert len(manifest['maps'])==1000 and set(manifest['classes'])==expected
 ids={s:{e['id']for e in manifest['maps']if e['split']==s}for s in('train','validation','test')}
 assert not(ids['train']&ids['validation']or ids['train']&ids['test']or ids['validation']&ids['test'])
 assert '白色开阔地' in manifest['snow_rule'] and '浅蓝小河' in manifest['water_rule']
 assert all((ROOT/e['image']).is_file()for e in manifest['maps'])
 held=synthetic['held_out_synthetic'];assert held['macro_f1']>=.92 and held['minimum_class_f1']>=.75
 assert real['maps']==34 and real['aggregate']['macro_f1_supported']<.72
 assert real['production_promotion']is False and synthetic['production_promotion']is False
 bundle=joblib.load(ROOT/'output/terrain_model/terrain_11_rerendered.joblib')
 assert set(bundle['classes'])==expected and bundle['auto_apply']is False
 print('terrain self-evolution checks passed')

if __name__=='__main__':main()
