---
mode_id: cinematic-chibi-short-anime
node: DirectorMasterCinematic
name: Q版泡面番分镜
one_liner: 3-5分钟泡面番分镜，Q版快切+高密度短单元剧
applicable: [Q版泡面番, 短动画单元, IP 衍生小剧场]
intensity: high
style_tags: [Q版, 泡面番, 快切, 单元剧, 萌系]
aliases: [泡面番]
---

## 意图

3-5 分钟一个小故事的单元剧分镜：0.5 密度 + Q版快切签名——每集一个梗、快进快出。与 番剧动漫 的差别是体量（3 场 vs 8 场）与密度（0.5 vs 0.7 反而更密——泡面番靠短平快）。

## 核心手法

- 体量推导：3-5min → get_beat_map ≥3 梯 3 场；density 0.5 → 分支 D target_avg=5s → 每场 max(12, 场秒/5) 镜——3min 约 36 镜。
- 单元节奏：三场承载 设梗-发展-抖包袱 的压缩三幕；张力曲线短幅震荡（泡面番不需要长弧）。
- 主导运镜：move="Q版快切" 覆写 2/3 镜；Q版视觉（大头/变形）不在引擎——靠上游美术输入的角色锚定与"Q版"语义透传。
- 反应镜配额：reaction 池 //12 + 微距池 //20——夸张表情的"萌点"镜位有配额保证。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（单集） | 桶化 ≥20→30；<3min 落 ≥0.5 梯（场数变 1-5）——单集结构突变 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"强化抖包袱；"🎲 随机" 不生效 |
| 角色输入 | Characters 输出 | Q版角色特征（外貌/性格 anchors）进 focus/stage_emotion——萌感语义的输入源 |
| 核心数据包 | Core 32 字段 JSON | _情绪基调=欢乐类词不影响节拍——Q版的情绪靠张力档与反应镜，基调词进润色 |

## 已知坑

- 与 创意玩法/搞笑整蛊 同 0.5 密度——三胞胎区分度靠 mode_seed 变体与签名 note（d1 分簇）。
- "Q版"无引擎概念——变形/大头不产生任何镜头字段差异，纯语义透传。
- 3min 恰落 ≥3 梯（max(3, 2)=3 场）；2.5min 落 ≥0.5 梯 5 场——跨梯场数跳变。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["Q版泡面番分镜"]（dur_scale 0.5, move "Q版快切"）→ build_standard_shots(density_scale=0.5) → get_beat_map ≥3 梯 → generate_feature_shots 分支 D（reaction/micro 配额）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY；_shape_tension_curve；script_studio._parse_char_anchors（角色锚定）
