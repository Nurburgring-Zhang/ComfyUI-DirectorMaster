---
mode_id: cinematic-60s-twelve-segments
node: DirectorMasterCinematic
name: 60秒12段
one_liner: 60秒短视频分镜（约2场16镜），时长须手动设1分钟
applicable: [60秒短视频, 剧情广告, 信息流剧情]
intensity: high
style_tags: [60秒, 短视频, 标准快切, 两场结构]
aliases: []
---

## 意图

60 秒两场结构：场 1 建立钩子、场 2 推进收束。与 30秒6段 的差别是多一场的节拍空间（可承载一次小反转），与 90秒18段 的差别是三场结构里没有中段低谷的呼吸位。

## 核心手法

- 体量推导：目标 1min → get_beat_map ≥0.5 梯 2 场（t/0.5）→ 每场 shots 梯 <5min（5s/镜、5-12 镜）基准 8 → density 0.5 → 分支 D target_avg=5s → 每场 max(8, 6)=8 镜，合计约 16 镜。
- 双场节拍：两场的 story_function 由节拍生成器给出（建置→触发/推进类），auto 节奏按功能选型——建立场偏长镜/蒙太奇、推进场偏快剪。
- 主导运镜：move="标准快切" 覆写 2/3 镜（i%3≠2，跨场连续计数）；每 3 镜 1 镜原生。
- 时长覆盖：每场 dur 归一化到 场时长（30s），总量 60s ±1%。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1（=60 秒） | 不设则按 core 时长出长片；设 0.8 落 ≥0.5 梯 2 场（场时长 24s）——段数由公式给，非名义 12 |
| 节奏风格 | 无(默认)=auto | 钉"抖音超快"可整体提速；"🎲 随机" 不生效 |
| 剪辑节奏 | 无(默认) | 快×0.5 乘 dur 后不再归一 → 60s 目标失效（实际 ~30s）；覆盖依赖保持 ND |
| 剧本输入 | Script 输出 | "△"前 6 块驱动 purpose；两场结构建议剧本给 2 个语义块，第 7 块起无驱动标注 |

## 已知坑

- 名义"12 段"实际约 16 镜（2 场×8）——命名口径与引擎推导的差异同 30秒6段。
- 两场的场时长各 30s：分支 D 每场 ≤40 镜封顶不触发；但把目标设到 5min（≥3 梯 3 场+梯变）会改变场数与配额结构。
- 跨场的 i%3 计数连续（不按场重置）——"每 3 镜 1 镜原生"的相位跨场漂移是预期行为。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["60秒12段"]（dur_scale 0.5, move "标准快切"）→ build_standard_shots(density_scale=0.5) → get_beat_map ≥0.5 梯 2 场 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY + _build_dynamic_beat_table（shots 梯 5s/镜）；pacing_engine.STORY_FUNC_PACING
