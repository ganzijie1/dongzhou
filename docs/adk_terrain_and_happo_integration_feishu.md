# ADK 地形 Agent 与 HAPPO 组合方案

## 最低类别召回 0 的含义

召回率是“正确识别的该类格数 / 真实该类格数”。最低类别召回为 0，表示至少一个类别的所有真实样本都被错分。上一轮整图留一验证中，草地与山地跨图召回均为 0，因此视觉模型不能生产晋级。

## ADK 地形 Agent

Google ADK 适合编排工具、状态、并行审计、人工确认和评估；HAPPO 适合通过环境交互学习高频离散动作。地形打标的核心是多源证据冲突和高风险写入，因此本轮先接入官方 `google-adk 2.6.3`：

1. EvidenceAgent 检查图像哈希、网格、完全复核状态和渲染源矩阵。
2. ParallelAgent 并行运行 DINOv3 提案与结构硬规则审计。
3. ArbitrationAgent 采用可信源矩阵，否则只输出视觉复核候选。
4. 所有路径均保持 `auto_apply=false`。

## 实测

| 方法 | 宏 F1 | 最低类别召回 | 解释 |
|---|---:|---:|---|
| 两图联合视觉模型 | 0.9812 | 0.9615 | 训练见过 m058，不是跨图结果 |
| ADK 证据仲裁 | 1.0000 | 1.0000 | 采用哈希锁定且驱动渲染的复核源矩阵 |
| 视觉模型整图留一 | 0.2958 | 0.0000 | 训练未见 m058，代表跨图能力 |

ADK 的 1.0 不表示 Agent 看图超过视觉网络，而是它选择了最高等级证据。用未完全复核的旧清单运行时，Agent 切换为 `vision_proposal_review_only`，列出 20 个复核格并禁止生产写入。

## HAPPO 结合方式

```text
ADK 战术监督层
  解析胜利条件、伏兵、城门、阶段目标
  选择检查点、课程和风险预算
  监控异常并触发 CQL/安全待机回退
          ↓
HAPPO 动作层
  对合法移动、攻击、技能、物品和待机候选打分
          ↓
ADK 评测层
  对比胜率、回报、伤亡、目标完成率、耗时和策略熵
```

不建议让 LLM Agent 每个单位每一步直接选格子：延迟高、难复现、成本高，也缺少 HAPPO 的策略训练。HAPPO 也不应用于地形分类，它没有图像监督目标。

战斗操控比较应另开相同地图、随机种子和动作预算的基准，比较 HAPPO、ADK 纯 Agent、ADK+HAPPO、HAPPO+CQL 回退。在完成该基准前不替换当前 HAPPO。

## 文件

- `tools/terrain_adk_agent/agent.py`
- `tools/run_terrain_adk_agent.py`
- `tools/compare_terrain_adk_vs_model.py`
- `requirements-adk.txt`
- `output/terrain_model/m058_adk_agent_report.json`
- `output/terrain_model/m058_adk_unverified_report.json`
- `output/terrain_model/terrain_adk_vs_model_report.json`
