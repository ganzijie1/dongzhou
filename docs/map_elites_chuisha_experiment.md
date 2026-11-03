# 垂沙之战 MAP-Elites 关卡生成实验

## 结论

本实验选择前 301 年垂沙之战，因为现有 172 关没有该战役，而《吕氏春秋·处方》提供了能直接转为关卡机制的史料：齐、韩、魏联军与楚军夹沘水相持；匡章通过守备强弱反推浅渡位置，随后夜袭楚军重守的浅处。《史记·秦本纪》用于确认匡章（章子）、公孙喜、暴鸢与唐眜等参战人物。

不会据此补写史书没有记载的兵数、伤亡、精确地理坐标或阵形。游戏中的地图尺寸、渡点数量、地形覆盖、单位部署和战斗数值都属于生成演武。

## 实验设计

- 档案维度：`渡河路线数量（1-5） × 楚军守势优势（5 档）`，共 25 格。
- 硬约束：所有部署点合法；双方部署区跨河连通；深水不可通行；浅渡语义一致；实际路线数必须匹配档案描述符。
- 质量函数：路线间距、四种进军策略的路线选择差异、地图可读性、侧翼跨度与零修复奖励。
- 结构变异：70% 局部变异、20% 渡点拓扑变异、10% 大变异。
- 对照：MAP-Elites 与随机搜索使用相同的 5000 次评估预算，运行 5 个固定种子。

## 结果

详见 `output/map-elites-chuisha/report.json`。本次 5 次运行中，MAP-Elites 与随机搜索都覆盖 25/25 格；MAP-Elites 的平均 QD-score 为 22.710368，95% 区间为 [22.563155, 22.857581]，随机基线为 22.427330，[22.378742, 22.475917]。两者区间在本次设置下不重叠，但样本只有 5 个种子，不能据此声称普遍统计优势。

全部入档精英都通过静态硬约束。这里的质量和“守势优势”是离线代理指标，不等于真人通关率或真实难度；后续仍需用完整战斗代理与真人回放校准。

## 史料与方法来源

- [《吕氏春秋·处方》](https://ctext.org/lv-shi-chun-qiu/chu-fang/zh)
- [《史记·秦本纪》](https://ctext.org/shiji/qin-ben-ji/zh)
- [Mouret & Clune, Illuminating search spaces by mapping elites](https://arxiv.org/abs/1504.04909)
- [Gravina et al., Procedural Content Generation through Quality Diversity](https://arxiv.org/abs/1907.04053)
- [Khalifa et al., Talakat: Bullet Hell Generation through Constrained MAP-Elites](https://arxiv.org/abs/1806.04718)
