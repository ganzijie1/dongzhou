# 东周列国志 172 关难度结构审计

生成时间：2026-11-03T12:34:32.671Z

方法依据：[离散几何优化：数学模型、核心算法与工程实践](https://my.feishu.cn/docx/AD99dmVLHoUjLIxBFEzcXl4tnZd)

难度预测依据：[小游戏关卡难度预测：方法、数据与工程实践综述](https://my.feishu.cn/docx/Q4uddpasdoijcPxWurfcrJGZnEe)

## 结论

- 已先建立统一成长基线：主线 172 关按 1–60 级展开，军阶约每 3 个首通提升一级，最终战前达到 60 级；武将熟练度最多领先军阶 2 级。
- 三档难度已改为真实战斗参数：简单档降低敌军等级与生命/攻防并增加 25% 回合宽限；标准档保持基线；艰难档提高敌军 2 级、生命/攻击 12%、防御 8%，同时启用完整 HAPPO 概率。
- 172 关中有 164 个战斗关、8 个纯剧情关；111 个战斗关至少触发一项结构风险标记。
- 敌我单位比中位数为 1.053，P90 为 2.133，最大值为 10。这些只能用于排查跳变，不能直接等同于玩家难度。
- 现有 HAPPO 发布评估在 507 局中敌方胜率为 100%，95% 区间 [0.9925, 1.0000]；脚本基线敌胜率为 0%。该结果证明当前验收对手失衡，不能用来证明关卡平衡。
- HAPPO 仅训练 4/11 个角色头，其余角色采用第一个合法动作，现阶段不能作为全职业难度裁判。
- 60 级新基线的 14 个战斗关单种子烟测仍为 HAPPO 敌胜率 100%、脚本敌胜率 0%，脚本超时率 100%。它只验证运行契约，不作为平衡置信结论。
- 已引入离散几何的网格图指标：地形标签总变差（相邻格标签切换率）、地形斑块密度、可通行连通分量和割点比例。它们分别对应纹理过密、碎片化、不可达和单通道瓶颈风险。
- PCGRL 离散几何修复在 60 个三档种子用例中通过 60 个，回退 0 个；最坏地形切换率 0.531、斑块密度 0.282、割点率 0.079。
- 运行时现在将结构风险作为冷启动先验，并按玩家军阶、装备、所选难度和同关实战记录逐步校准；少于 5 局标记为冷启动，5–19 局为有限证据，至少 20 局才标记为已校准。

## 结构风险最高的 15 关

> 结构风险分数只综合兵力比、障碍密度、接敌距离/回合预算、脚本复杂度与目标类型，用于决定测试顺序，不是通关率预测。

| 关 | 战役 | 建议等级 | 友:敌 | 敌我比 | 回合 | 障碍率 | 纹理切换 | 割点率 | 风险 | 标记 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 83 | 桃园脱险 | 29 | 2:20 | 10 | 18 | 0.484 | 0.375 | 0 | 69.9 | enemy-ratio-high, barrier-density-p90, deployment-components-disconnected, adjacent-force-ratio-jump |
| 94 | 藏孤出宫 | 33 | 2:13 | 6.5 | 20 | 0.444 | 0.332 | 0 | 69.8 | enemy-ratio-high, barrier-density-p90, adjacent-force-ratio-jump |
| 5 | 郑伯克段 | 2 | 4:13 | 3.25 | 20 | 0.436 | 0.246 | 0.007 | 63.2 | enemy-ratio-high, adjacent-force-ratio-jump |
| 3 | 镐京陷落 | 1 | 8:20 | 2.5 | 12 | 0.296 | 0.403 | 0.047 | 62.5 | enemy-ratio-high, bottleneck-p90, adjacent-force-ratio-jump |
| 108 | 曲沃灭栾 | 37 | 8:22 | 2.75 | 32 | 0.454 | 0.464 | 0.001 | 62.4 | enemy-ratio-high, barrier-density-p90, deployment-components-disconnected, adjacent-force-ratio-jump |
| 55 | 临淄夜逃 | 19 | 4:8 | 2 | 12 | 0.718 | 0.377 | 0.12 | 61.2 | enemy-ratio-high, barrier-density-p90, bottleneck-p90, deployment-components-disconnected |
| 105 | 高唐平叛 | 36 | 4:16 | 4 | 28 | 0.468 | 0.386 | 0 | 59.3 | enemy-ratio-high, barrier-density-p90, deployment-components-disconnected, adjacent-force-ratio-jump |
| 1 | 东郊索命 | 1 | 2:7 | 3.5 | 18 | 0.177 | 0.337 | 0.018 | 53.4 | enemy-ratio-high, bottleneck-p90 |
| 48 | 蒲城突围 | 17 | 5:8 | 1.6 | 16 | 0.489 | 0.297 | 0.221 | 53 | barrier-density-p90, bottleneck-p90, deployment-components-disconnected |
| 110 | 且于门死战 | 38 | 3:23 | 7.667 | 28 | 0.174 | 0.471 | 0 | 52.7 | enemy-ratio-high, adjacent-force-ratio-jump |
| 112 | 巢门伏射 | 39 | 4:10 | 2.5 | 18 | 0.275 | 0.519 | 0 | 51.1 | enemy-ratio-high, adjacent-force-ratio-jump |
| 102 | 棫林突秦 | 35 | 2:15 | 7.5 | 24 | 0.087 | 0.605 | 0 | 50.9 | enemy-ratio-high, texture-transition-p90, adjacent-force-ratio-jump |
| 104 | 十二国伐齐 | 36 | 15:32 | 2.133 | 40 | 0.251 | 0.47 | 0 | 49.8 | enemy-ratio-high |
| 35 | 楚宫靖难 | 12 | 4:8 | 2 | 20 | 0.914 | 0.273 | 0.739 | 48.8 | enemy-ratio-high, barrier-density-p90, bottleneck-p90, deployment-components-disconnected |
| 8 | 攻取郜城 | 3 | 4:10 | 2.5 | 20 | 0.185 | 0.201 | 0.007 | 48.1 | enemy-ratio-high |

## 脚本等级异常

- 未发现脚本等级异常。

## 下一轮验收

1. 用统一等级重新跑每关至少 20 个确定性种子，记录胜率、回合、伤亡、道具消耗和终局原因。
2. 同一关使用弱、中、强三档代理，目标是胜率随代理强度单调上升，而不是让单一 HAPPO 全胜。
3. 优先人工复核上表 15 关和相邻兵力比跳变关；纯剧情关不参与战斗难度统计。
4. 真人数据进入后，以目标胜率区间和置信区间替换本报告的结构风险分数。

完整逐关数据见 `docs/stage-difficulty-audit.json`。
