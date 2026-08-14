# 外部地图训练素材与结果

## 素材

- OpenGameArt：五套 CC0 俯视瓦片，许可证和来源见 `assets/training/external_cc0/opengameart/SOURCES.json`。只有文件级单类的草地、雪山进入弱监督试验；混合 spritesheet 未经切格复核，不自动标注。
- Freeciv：从官方 GPL-2.0 仓库稀疏检出 `amplio2` 地形精灵和八张场景。场景 `terrident` 提供字符语义，精灵 `.spec` 提供像素坐标；构造了 5172 个带场景分组的训练格。
- 本地 `m008`、`m058` 始终是整图留一测试域。外部数据只进入训练折，不进入测试折。

## 结果

| 方法 | 宏 F1 | 最低召回 | 结论 |
|---|---:|---:|---|
| 原适配器 | 0.2939 | 0.0000 | 基线 |
| 本地全特征线性探针 | 0.3353 | 0.0000 | 诊断提升 |
| DINO + 手工特征逐图归一化 | 0.3424 | 0.0000 | 本地最佳消融 |
| CC0 单类小瓦片 | 0.2973 | 0.0000 | 域差过大，否决 |
| Freeciv 完整地图 + 官方地形码 | 0.3479 | 0.0000 | 山地召回提升到 0.2281 |
| Freeciv + 固定域归一化融合 | **0.3485** | 0.0102 | 当前最高，仍不晋级 |

Freeciv 证明“完整地图布局 + 机器可读真值”比小 spritesheet 有效，但不能替代曹操传画风的草地真值。下一步应完整复核至少一张同时覆盖 `f/g/F/m` 的本项目第三图，再做三图 LOMO、源域均衡采样、MixStyle 和训练侧 DINO 中间层选择。

## 报告

- `output/terrain_model/terrain_external_cc0_lomo_report.json`
- `output/terrain_model/terrain_freeciv_lomo_report.json`
- `output/terrain_model/terrain_freeciv_ensemble_report.json`

所有结果均 `production_promotion=false`、`auto_apply=false`。
