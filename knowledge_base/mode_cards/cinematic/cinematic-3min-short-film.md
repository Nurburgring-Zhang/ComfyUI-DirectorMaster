---
mode_id: cinematic-3min-short-film
node: DirectorMasterCinematic
name: 3分钟完整短片
one_liner: 3分钟三场短片分镜，短片运镜+0.7密度，含完整三幕压缩
applicable: [3分钟短片, 短片竞赛, 品牌微电影]
intensity: medium
style_tags: [短片, 三幕压缩, 短片运镜, 完整叙事]
aliases: []
---

## 意图

3 分钟讲完整故事：三场 × 三幕压缩（建置-对抗-解决），0.7 密度保留呼吸感。与 90秒18段 的差别是每镜更长（7s 级 vs 3.75s 级）、节拍更完整；与 60/90s 档的本质差别是"完整短片"而非"信息流片段"。

## 核心手法

- 体量推导：目标 3min → get_beat_map ≥3 梯 max(3, t/1.5)=3 场 → 每场 shots 基准 12（<5min 梯 time_based=12）→ density 0.7 → 分支 D target_avg=7s → 每场 max(12, 9)=12 镜，合计约 36 镜 × ~5s。
- 三幕节拍：_beats_drama_three_act 展开到 3 场，每场一个幕功能；tension 曲线塑形让第三场承载高潮（色彩/光影/材质档拉满）。
- 主导运镜：move="短片运镜" 覆写 2/3 镜（i%3≠2）；每 3 镜 1 镜原生。
- 情感曲线：5 导演型曲线按导演名插值到 36 镜，ease-in-out + 心跳微扰——短片的情绪起伏有曲线依据。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3 | 不设则按 core 时长出长片；设 5 落 ≥3 梯 3 场（场时长 100s）——场数不变但每场镜头变长 |
| 节奏风格 | 无(默认)=auto | 钉快闪会把短片变成信息流；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _导演风格 决定时长/张力覆写（塔可夫斯基×1.5 场时长 → 3min 目标会被推向更慢的场结构）——导演档与短时长冲突时以覆写为准 |
| 剧本输入 | Script 短片剧本 | 前 6 块驱动 purpose；三场结构建议 3 块以上语义块 |

## 已知坑

- "完整"是三幕压缩语义：3 场各 ~60s 承载建置/对抗/解决，拍点密度远低于长片三幕——用它验证长片结构会失真。
- density 0.7 与 90s 档的 0.5 相比少 30% 镜——跨档对比时长覆盖口径一致（±1%），镜数差异是密度设计。
- 短片运镜覆写与 运镜风格_多选 弧值叠加时，非保留镜最终以模式运镜为准（覆写顺序：偏好→模式）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["3分钟完整短片"]（dur_scale 0.7, move "短片运镜"）→ build_standard_shots(density_scale=0.7) → get_beat_map ≥3 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine._beats_drama_three_act + _shape_tension_curve；cinematic_studio.DIRECTOR_CURVES；SHOT_POOL_BY_DENSITY
