---
mode_id: cinematic-creative-play
node: DirectorMasterCinematic
name: 创意玩法分镜
one_liner: 脑洞创意短视频分镜，0.5密度脑洞运镜+物件变体池制造陌生感
applicable: [脑洞短视频, 创意挑战, 创意广告]
intensity: adaptive
style_tags: [脑洞, 创意玩法, 陌生化, 物件叙事]
aliases: []
---

## 意图

"把日常拍陌生"的创意分镜：0.5 密度 + 脑洞运镜签名，创意感由物件变体池（"与周围格格不入, 又理所当然"等 6 模板）与状态后缀池（"像一句没说出口的话"等）的语言陌生化承担。与 爆火反转 的差别是不依赖钩子-反转结构，靠持续的语义错位。

## 核心手法

- 体量推导：30-60s → get_beat_map ≥0.5 梯 1-2 场；density 0.5 → 分支 D target_avg=5s → 每场 max(8, 场秒/5) 镜。
- 陌生化文案：物件焦点按 mode_seed+镜号哈希从通用变体池选（"的位置没变, 但意义变了"/"入了画, 没人先碰它"）——同物件逐镜语义漂移是本模式的创意引擎。
- 主导运镜：move="脑洞运镜" 覆写 2/3 镜；每 3 镜 1 镜原生引擎运镜（建立/反应池的非常规机位）。
- 物件锚定：场景 objects 的首物件进 focus 中心，物件细节池围绕它展开——创意对象与用户输入一致。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-1 | 不设则按 core 时长；桶化 ≥20→30 |
| 核心数据包 | Core 32 字段 JSON | 无 objects 输入 → 落"关键道具"占位，陌生化文案失去锚点对象——创意模式对物件输入最敏感 |
| 节奏风格 | 无(默认)=auto | 钉"蒙太奇"可做序列化脑洞；"🎲 随机" 不生效 |
| 创意输入 | Vibe 节点输出 | 主题/对标 anchors 进 purpose（"主题:X|对标:Y"）——脑洞的概念锚点来源 |

## 已知坑

- 同族密度陷阱：创意玩法/搞笑整蛊/Q版泡面番 同为 density 0.5——区分度只有 mode_seed 变体与签名 note（d1 审计背景：Script 侧同族 创意玩法 vs 爆火反转 曾达 0.91 相似度，D2 探针要求 <0.7，本节点的差异化机制是 D1 变体池）。
- 脑洞语义无结构保证（无反转拍/无错位节拍表）——"创意"程度取决于用户物件与 Vibe 输入质量。
- 变体池是通用 6 模板——特定物件（凤梨罐头/旧信/钢笔）有专属 3 模板池但需精确命中物件名。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/script_studio.py
- 分支/函数：MODE_PACING["创意玩法分镜"]（dur_scale 0.5, move "脑洞运镜"）→ build_standard_shots(density_scale=0.5) → generate_feature_shots 分支 D；_make_pacing_shot/_make_shot 物件变体池（obj_variants + 通用 6 模板）；_parse_vibe_anchors（创意锚点）
- 数据来源：pacing_engine 物件/状态变体池；SHOT_POOL_BY_DENSITY；_integrate_6d_into_shot_fields（Vibe 主题/对标）
