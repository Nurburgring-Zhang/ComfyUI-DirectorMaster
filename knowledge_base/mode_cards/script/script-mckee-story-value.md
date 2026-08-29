---
mode_id: script-mckee-story-value
node: DirectorMasterScript
name: 麦基故事价值长片
one_liner: McKee 欲望/需求驱动，价值正转反转交替推进的人物向长片
applicable: [人物驱动剧情片, 艺术片, 文艺长片, 作者电影]
intensity: high
style_tags: [麦基理论, 价值转折, 人物驱动, 长片体量]
aliases: [麦基故事价值]
---

## 意图

故事重心在人物内在价值翻转而非外部事件时选它。与其他结构模式的差别：节拍位全部以"价值正转/反转"命名（建立欲望/需求 → 四次正反转 → 中点深度反转 → 价值决断），冲突由价值维度承载。

## 核心手法

- `STRUCTURE_THEORY_MAP["麦基故事价值长片"]="麦基故事价值"`：STORY_BEATS["麦基故事价值"]（欲望/需求/价值正转反转 40+ 次）附录 + `_normalize_theory`→mckee。
- `_beats_mckee_story_value`（feature_film_engine.py:104）12 拍骨架：正转/反转交替，张力 5→7→6→8→9（中点深度反转）→10（价值决断）→5→3。
- 潜文本变体池按张力级取词（SUBTEXT_VARIANTS[tension]），高张力场次潜文本措辞更重——价值反转拍的〔潜文本〕行自动加压。
- 与"剧本架构/角色弧光"模板天然咬合：完整输出尾部的角色弧（Want/Need 矛盾原则）即 McKee 的欲望/需求对位。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事结构 | 无(默认) | 锁定为麦基故事价值；选"麦基故事价值(McKee)"效果一致 |
| 目标时长(分钟) | 0（自动→120→35 场） | 12 骨架拍 expand 到任意场数；≥50min 按 18 场阶梯（aggregator/pro_format.py 时长阶梯），12 价值拍每拍约 1-2 场 |
| 潜文本强度 | 无(默认)→中(每句1层) | 控制潜文本行渲染频率；零→全片无〔潜文本〕行（价值拍失去潜文本注解） |
| 核心数据包 | Core.核心数据包 | `_主题词`+"深/极深/存在主义/形而上"主题深度→追加【主题陈述】哲学内核块 |

## 已知坑

- 类型关键词"艺术/文艺"命中 film_art/art 时，类型通道同样落 mckee 生成器（feature_film_engine.py:780）——换其他"结构"下拉可能节拍不变。
- 价值正转/反转的方向（什么价值在翻）不由参数决定，节拍只保证"有翻转位"；具体价值内容依赖场景解析与对白池，过空场景会泛化。
- STORY_BEATS 附录写"40+ 次"是方法论提示，实际生成场次里的正反转次数=骨架拍数（12），勿按字面期待。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() :1762 → `_build_full_screenplay()`（:1413）
- 数据来源：aggregator/feature_film_engine.py::_beats_mckee_story_value（:104）、SUBTEXT_VARIANTS（:1119）；STORY_BEATS["麦基故事价值"]（script_studio.py:89）
