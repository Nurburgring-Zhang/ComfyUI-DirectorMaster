---
mode_id: cinematic-90s-eighteen-segments
node: DirectorMasterCinematic
name: 90秒18段
one_liner: 90秒短视频分镜（约3场24镜），时长须手动设1.5分钟
applicable: [90秒剧情短视频, 三段式广告, 微短剧单场]
intensity: high
style_tags: [90秒, 三场结构, 标准快切, 短视频]
aliases: []
---

## 意图

90 秒三场结构：建立-推进-收束各占 30s，是最小的"完整三幕"短视频体量。与 60秒12段 的差别是有中场的节拍呼吸（第二场可承载转折），与 3分钟完整短片 的差别是密度更高（0.5 vs 0.7）、叙事更紧凑。

## 核心手法

- 体量推导：目标 1.5min → get_beat_map ≥0.5 梯 3 场 → 每场 8 镜基准（shots 梯 <5min）→ density 0.5 → 分支 D 每场 max(8, 6)=8 镜，合计约 24 镜。
- 三场节拍：节拍生成器给 3 场功能（三幕压缩：建置/对抗/解决），auto 节奏按功能混编——典型组合 固定长镜/蒙太奇/一秒三闪。
- 主导运镜：move="标准快切" 覆写 2/3 镜；每 3 镜 1 镜原生保多样性。
- 时长覆盖：每场 30s 归一化，总量 90s ±1%（保持 ND 干预时）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1.5（=90 秒） | 不设则按 core 时长；设 2 落 ≥0.5 梯 4 场——场数跳变改变叙事结构 |
| 节奏风格 | 无(默认)=auto | 钉单一节奏抹掉三场的快慢对比；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _情绪基调 驱动情感曲线选型与直觉规则关键词——"孤独"类基调 + 直觉风险会触发 R4 不对称标注 |
| 叙事编排 | 无(默认)=跟随叙事结构 | 短体量下设倒叙/乱叙会让 3 场的银幕序≠时序——JSON 银幕序/时序位 字段是唯一可靠的还原依据 |

## 已知坑

- 名义"18 段"实际约 24 镜（3 场×8）——命名口径差异同前两档。
- 1.5min 恰在 ≥0.5 梯（t/0.5=3 场）；若目标 ≥3（如 2min→4 场）梯不变但场时长降到 30s 以下，每场镜头 dur 归一后普遍 <4s。
- 三场的 story_function 组合随节拍生成器确定性变化，但同输入恒定——复现依赖同 core 包。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["90秒18段"]（dur_scale 0.5, move "标准快切"）→ build_standard_shots(density_scale=0.5) → get_beat_map ≥0.5 梯 3 场 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY + 节拍生成器（三幕压缩）；pacing_engine.STORY_FUNC_PACING
