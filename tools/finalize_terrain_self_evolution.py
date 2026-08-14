from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
doc='''# 梦德11类地形自进化实测记录

## 类别与玩法语义

| 标签 | 地形 | 语义 |
|---|---|---|
| `f` | 平原 | 可通行 |
| `g` | 草地 | 可通行 |
| `s` | 雪地 | 白色开阔地，可通行；覆雪树林和山地仍标 `F/m` |
| `F` | 树林 | 可通行，增加移动消耗 |
| `m` | 山地 | 可通行，高移动消耗 |
| `W` | 城墙 | 整格不可跨越，必须连续 |
| `C` | 城池 | 可通行，写入关卡时必须登记补给点 |
| `e` | 营寨 | 仅中心有营帐图标的格子；可通行且必须登记补给点 |
| `P` | 栅栏 | 中心轴整格阻挡，不可跨越 |
| `~` | 大河 | 深蓝、宽且连续，不可跨越 |
| `v` | 小河 | 浅蓝、较窄，可通过但移动消耗高于平原 |

## 已执行的自进化流程

1. 程序先生成地形矩阵，矩阵是真值，模型预测永不回写为标签。
2. 实际生成1000张地图、108000个真值格，按完整地图拆分为800训练、100验证、100最终盲测。
3. 第一版固定色块在同分布合成盲测得到1.0，但真实34图宏F1仅0.1631，判定为渲染域过拟合并拒绝晋级。
4. 第二版改用逐格复核的MOD纹理、生产城墙/建筑/营寨/栅栏精灵和真实水纹理重渲染全部1000张。
5. 重渲染合成盲测宏F1为0.9523，最低类别F1为0.7907；真实34图宏F1提升到0.4227，但草地、山地仍不合格。
6. DINOv3密集特征分层头已在RTX 3060上运行；结构识别明显改善，但普通地形受旧Lua弱标签污染，仍未达到晋级门槛。

## 发布约束

- 所有候选保持 `production_promotion=false` 和 `auto_apply=false`。
- 新生成地图直接使用生成前矩阵，不允许生成后模型覆盖逻辑地形。
- 旧地图识别只输出建议；低于0.72置信度、所有结构格和自然边界必须复核。
- 城墙、城池、营寨、栅栏、水系使用独立高召回检测头；自然地形投票不得覆盖结构类。
- 城池/营寨只有同步写入 `supply_sites/gsites` 后才可作为补给地形。
- 下一代普通地形训练只接收逐格人工复核的真实视觉标签，不再把程序花纹矩阵当强监督。
'''
(ROOT/'docs/terrain_self_evolution_protocol.md').write_text(doc,encoding='utf-8')
test='''from pathlib import Path
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
'''
(ROOT/'rl/terrain_self_evolve_test.py').write_text(test,encoding='utf-8')
print('terrain self-evolution report and tests finalized')
