---
mode_id: cinematic-anime-series
node: DirectorMasterCinematic
name: 番剧动漫分镜
one_liner: 24分钟番剧单集分镜，时长桶化到30分钟档（约8场）出体量
applicable: [番剧单集, 动画连续剧, 国创动画]
intensity: medium
style_tags: [番剧, 动漫运镜, 单集, 24分钟]
aliases: []
---

## 意图

24 分钟番剧单集的标准分镜：0.7 密度 + 动漫运镜签名。与 完整短片的差别是集结构（OP/正片/ED 的节拍空间）与更高信息密度；与 Q版泡面番 的差别是体量与叙事完整度。

## 核心手法

- 时长桶化：24min → build() 时长桶 ≥20→30 → get_beat_map(30) ≥30 梯 t/3.5=8 场——单集体量按 30min 档出，24min 是名义口径。
- 密度推导：density 0.7 → 分支 D target_avg=7s → 每场镜数=max(基准, 场秒/7)。
- 主导运镜：move="动漫运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 动漫语义项：动作夸张/违反物理运镜是 format_templates 动画故事板模板的文案原则——Cinematic 分镜表通过运镜/焦段字段语义透传，无逐帧关键帧输出。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 24（单集名义） | 桶化 ≥20→30：24min 实际按 30min 梯出 8 场；设 12 → 30min 桶不变（≥20）——12min 单集也出 30min 体量 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"强化战斗集；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _导演风格=宫崎骏 → DIRECTOR_OVERRIDES 派别（自然灵动）影响张力/时长——动漫+导演档可组合 |
| 剧本输入 | Script 番剧剧本 | 前 6 块驱动 purpose；单集剧本（OP-正片-ED）块对应 |

## 已知坑

- 12-19min 的短单集也被 ≥20 桶吸到 30min——低于 20min 的动漫体量需求只能用 <20 档（5 场梯）近似，无逐分钟精度。
- "动漫运镜"不在 _MOVE_VARIANTS——签名运镜原样保留。
- 动画帧率/12-24 帧语义是动画模板的文案——分镜表 dur 仍按秒，帧率由下游。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["番剧动漫分镜"]（dur_scale 0.7, move "动漫运镜"）→ build_standard_shots(density_scale=0.7) → 时长桶（≥20→30）→ get_beat_map ≥30 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.get_beat_map ≥30 梯 + SHOT_POOL_BY_DENSITY；format_templates 动画故事板原则（文案参考）
