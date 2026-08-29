---
mode_id: cinematic-figure-documentary
node: DirectorMasterCinematic
name: 人物纪录片分镜
one_liner: 60-90分钟人物纪录分镜，2.0密度纪录跟拍（约20s/镜）
applicable: [人物纪录片, 传记片, 访谈纪录]
intensity: low
style_tags: [人物纪录片, 纪录跟拍, 长片, 怀斯曼, 低密度]
aliases: []
---

## 意图

纪录片的凝视节奏：2.0 密度（全节点最强减镜档）——平均 20s/镜的纪录跟拍，让真实时间流过画面。与 社会纪录片 的差别是对象（单人物弧线 vs 群像议题）；与 长镜大师（钉死节奏引擎）的差别是本模式走密度路径、节奏仍按场功能混编。

## 核心手法

- 减镜推导：density_scale=2.0 → 分支 D target_avg=20s → 每场镜数=max(基准, 场秒/20)——90min 约 15-25 场（t/4 梯），总量显著低于基线。
- 主导运镜：move="纪录跟拍" 覆写 2/3 镜；每 3 镜 1 镜原生（建立/空镜呼吸位）。
- 纪录节奏混编：auto 路径下"建立/发现"场 → 固定长镜、"铺垫/准备" → 蒙太奇（人物历程压缩）——纪录片的观察-压缩交替有节拍依据。
- 访谈语义：对坐场景命中 亲密关键词 + 直觉启用时 R2 把特写改远景——纪录片的"不消费人物"伦理选项。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 60-90 | 桶化 ≥80→90、≥110→120：设 75 实际按 90 出；密度 2.0 在 clamp 上限 4.0 内 |
| 节奏风格 | 无(默认)=auto | 保持 ND 让观察-压缩交替生效；钉"固定长镜"全场凝视化；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 人物名需进场景角色——parse_scene 解析出的 c1 贯穿 focus/POV；空输入落"主角"占位 |
| 叙事线型 | 无(默认)=单线 | 人物 A 线 + 社会 B 线的双线语义需设 双线并行——标签只进 purpose/JSON |

## 已知坑

- 纪录片节拍不自动切 _beats_doc_chronicle——doc 生成器按场景类型/理论归一才命中；本模式默认三幕剧，人物弧按三幕展开。
- 2.0 密度 × shots 基准下限：短场不会低于基准镜数——密度只影响 time-based 项。
- 与 社会纪录片 完全同密度同运镜签名——区分度仅 mode_seed 变体与签名 note（d1 同簇唯一性验证点）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["人物纪录片分镜"]（dur_scale 2.0, move "纪录跟拍"）→ build_standard_shots(density_scale=2.0) → get_beat_map ≥60 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.get_beat_map 长片梯；STORY_FUNC_PACING（建立→固定长镜、铺垫→蒙太奇）；TYPE_BEAT_GENERATORS["doc"]=_beats_doc_chronicle（需类型归一命中）
