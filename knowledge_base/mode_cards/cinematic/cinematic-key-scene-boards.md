---
mode_id: cinematic-key-scene-boards
node: DirectorMasterCinematic
name: 电影关键场次分镜
one_liner: 单场戏精修分镜，节奏按场次叙事功能自动选型（高潮→快闪、建立→长镜）
applicable: [单场戏精修, 试拍片段, 通道测试]
intensity: medium
style_tags: [单场分镜, 节奏选型, 场景锚定, 情感曲线]
aliases: []
---

## 意图

把一场戏做成可拍摄的精修分镜：目标时长设 0.5-3 分钟，引擎出 1-2 场、几十秒到三分钟的镜头表。与 段落模式 的差别是节拍只剩单场功能（建立/中点/高潮其一），节奏选型完全由该场的 story_function 决定。

## 核心手法

- 场数收敛：`get_beat_map(0.5-3)` → ≥0.5 梯 t/0.5 场（0.5min→1 场、3min→6 场封 5），单场 duration_min 即目标时长。
- 功能驱动节奏：auto 模式下 `get_pacing_for_scene(story_function=…)` 查 `STORY_FUNC_PACING`——"高潮/中点"→一秒三闪、"对决"→子弹时间、"建立"→固定长镜、"牺牲"→慢镜高光；导演偏置≥1.3 时替换大类（如希区柯克快剪 1.3）。
- 分支执行：命中长镜类走分支 A（单镜≤30s 叠化）、慢镜类走 B（1/8 或 1/20 慢放）、快闪/特殊/类型走 C（组公式展开）；`expand_pacing_shots` 把节奏模板缩放到场戏时长并做缺口归一（偏差>0.5s 时按比例再分配）。
- 场景锚定：V16.1 场景锚点——用户显式地点/时间/天气强制主导开场与收束场，池子仅作补充；时间词仅在场景原文出现时锚定（防"默认夜"回归）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-3（单场量级） | <0.5 → 1 场 5s 级；桶化规则 ≥20→30 不影响秒级；0.05 下限=3 秒 |
| 核心数据包 | Core 32 字段 JSON | 空包 → scene=""，场次功能落"推进"兜底 → 节奏退化为按 (act,scene_index) 哈希随机池选 |
| 景别偏好 | 无(默认) | 非 ND 逐镜覆写引擎景别设计（含快闪模板的 大特写→全景 递进）；"🎲 随机" 会把字面量写进每镜 景别 字段 |
| 节奏风格 | 无(默认)=按场功能 | 想钉死单场节奏（如子弹时间）用此项最直接；"🎲 随机" 原样返回不抽奖 |

## 已知坑

- 场次功能来自节拍表 story_function；空场景描述时落"推进"，STORY_FUNC_PACING 无命中 → 兜底按 (act, scene_index) 哈希从全部节奏池抽，输出不可预期的节奏。
- 单场 30s 内的快闪组公式（一秒三闪 1.9s/组）至少 1 组 4 镜——30s 目标出约 8 镜而非 3 镜，"关键瞬间"感由 focus 文案而非镜数保证。
- 情感曲线仍按全片位插值（单场=曲线起点段），强度整体偏低是预期行为。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：CINE_MODE_THEORY["电影关键场次分镜"]="三幕剧" → build_standard_shots → get_beat_map ≥0.5 梯 → get_pacing_for_scene（STORY_FUNC_PACING 查表 + DIRECTOR_PACING_BIAS 替换）→ generate_feature_shots 分支 A/B/C
- 数据来源：pacing_engine.PACING_STYLES/PACING_GROUP_FORMULAS；feature_film_engine._shape_tension_curve；format_templates.MASTER_VIDEO_PRINCIPLES
