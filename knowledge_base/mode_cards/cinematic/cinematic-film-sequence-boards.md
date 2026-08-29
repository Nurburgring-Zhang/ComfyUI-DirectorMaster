---
mode_id: cinematic-film-sequence-boards
node: DirectorMasterCinematic
name: 电影段落分镜
one_liner: 三幕骨架出单段落分镜，段落体量由目标时长桶决定（15-30min约5-10场）
applicable: [电影长片段落, 网剧单元, 预告段落]
intensity: medium
style_tags: [三幕结构, 段落分镜, 场景锚定, 情感曲线]
aliases: []
---

## 意图

只做长片中的一段（15-30 分钟量级）：用户把 目标时长(分钟) 设到 15-30，引擎按该时长出 5-10 场的分镜表。与 电影工作室 的差别在体量而非理论——同走三幕节拍骨架；与 关键场次 的差别是仍有完整节拍推进，不是单场精修。

## 核心手法

- 理论钉死：`CINE_MODE_THEORY["电影段落分镜"]="三幕剧"`，节拍由 `_beats_drama_three_act` 展开到 n 场（`_expand_beats_to_n` 按比例插值），短时长下三幕拍点压缩但中点/高潮相对位置不变（ten_rounds 结构硬指标同源）。
- 体量阶梯：`get_beat_map(15-30)` → t/3 场（15min→5 场、30min→8-10 场），每场 duration_min=总时长/场数。
- 节奏与镜头：auto 节奏按 story_function 查表 + 导演偏置；镜头经分支 A/B/C/D 生成后按场时长归一 dur，总秒数覆盖目标时长。
- 模式种子：mode_seed="电影段落分镜" 折入模板池偏移与 D1 语法变体——同输入下与 电影工作室/关键场次 的镜头语法指纹不同（tests/d1_grammar_probe.py 同簇唯一）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 15-30（段落量级） | 桶化 ≥20→30、≥50→60：设 25 实际按 30 出；设 90 会出全片体量——"段落"边界完全由时长桶决定，引擎无段落语义 |
| 核心数据包 | Core 32 字段 JSON | 空/非法 → scene="" 兜底；_成片时长 存在时优先于 widget 默认值 120 |
| 节奏风格 | 无(默认)=auto | 显式选项强制全场该节奏，覆盖按场自动选型；"🎲 随机" 不命中 RHYTHM_TO_PACING → 保持 auto |
| 剧本输入 | Script 输出（段落对应块） | 前 6 块折入 purpose；超出 6 块的段落内容不进驱动标注 |

## 已知坑

- "单段落"不是引擎概念：段落感 100% 来自目标时长；忘设时长（默认 120 或 core 90min）会得到全片体量而非段落。
- 15min 恰好落 ≥15 梯（t/3→5 场）；14min 落 ≥3 梯（t/1.5→8 场封顶）——跨梯时场数跳变，段落结构会突变。
- 张力曲线 `_shape_tension_curve` 仍按全片弧塑形，段落输出的"高潮"在段落末尾而非原片位——用作原片段落复刻时需自行核对拍点。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：CINE_MODE_THEORY["电影段落分镜"] → MODE_PACING["电影段落分镜"]（dur_scale 1.0、move None）→ build_standard_shots → get_beat_map ≥15/≥3 梯 → generate_feature_shots 分支 A/B/C/D
- 数据来源：feature_film_engine._beats_drama_three_act + _expand_beats_to_n；pacing_engine.STORY_FUNC_PACING；format_templates.MASTER_VIDEO_PRINCIPLES
