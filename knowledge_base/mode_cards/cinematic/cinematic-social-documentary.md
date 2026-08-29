---
mode_id: cinematic-social-documentary
node: DirectorMasterCinematic
name: 社会纪录片分镜
one_liner: 60-120分钟社会纪录分镜，2.0密度群像跟拍+年代池约束时代质感
applicable: [社会纪录片, 议题长片, 城市观察]
intensity: low
style_tags: [社会纪录片, 群像, 年代池, 议题, 低密度]
aliases: []
---

## 意图

议题与群像的纪录分镜：2.0 密度同 人物纪录片，差异在叙事宽度——多线群像（叙事线型=双线并行/三线交织）与时代质感（年代池约束地点/道具/角色名）。

## 核心手法

- 减镜推导：density 2.0 → 分支 D target_avg=20s；60-120min → t/4 梯 15-30 场（封 50）。
- 年代质感：_detect_era（复古/现代词）→ LOCATION_POOL 分池 + 默认道具池 + 补名角色池（老友/邻居/同事/街坊/旧识）——时代背景的地点与人物名不穿帮。
- 群像标签：叙事线型=双线并行 时 arrange_scenes 按 A/B 线编排，purpose 写 "线:A (c1)/线:B (c2)"——议题的多视角结构入口。
- 主导运镜：move="纪录跟拍" 覆写 2/3 镜。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 60-120 | ≥150 走 t/4 封 50 场；桶化 ≥110→120 |
| 叙事线型 | 无(默认)=单线 | 设 双线并行/三线交织 激活群像标签与银幕序编排；重排异常 stderr 降级保序 |
| 核心数据包 | Core 32 字段 JSON | 议题关键词（城市/工厂/拆迁类）不在引擎表——议题语义靠剧本与 AI 润色 |
| 节奏风格 | 无(默认)=auto | 保持 ND；"🎲 随机" 不生效 |

## 已知坑

- 与 人物纪录片 同密度同运镜——同簇 d1 验证点；区分度靠叙事线型与输入宽度。
- 议题结构无专用节拍表（doc 生成器需类型归一命中）——默认三幕会把议题片拍成人物弧结构。
- 2.0 密度下每镜 ~20s：投流/短视频场景误用此模式会得到极慢节奏——按用途选密度档。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/narrative_arrangement.py
- 分支/函数：MODE_PACING["社会纪录片分镜"]（dur_scale 2.0, move "纪录跟拍"）→ build_standard_shots(density_scale=2.0) → get_beat_map ≥60 梯 → generate_feature_scenes（_COMPANIONS 现代池补名）；arrange_scenes（叙事线型激活时）
- 数据来源：feature_film_engine._COMPANIONS/_DEFAULT_OBJS；narrative_arrangement.ARRANGEMENT_MODES/NARRATIVE_LINE_MODES
