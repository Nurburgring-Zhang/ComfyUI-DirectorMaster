---
mode_id: script-screenplay-body
node: DirectorMasterScript
name: 剧本正文
one_liner: 专业台本格式的场次正文：30 分钟 8 场，角色 cue 居中+潜文本+转场
applicable: [剧本初稿, 单场戏打磨, 台本格式示范]
intensity: medium
style_tags: [专业台本, 场次正文, 角色cue, 三幕默认]
aliases: [正文剧本]
---

## 意图

直接产出"能读能拍"的场次正文：INT./EXT 式场次头+动作行+居中角色 cue+对白+〔潜文本〕+CUT TO 转场。与完整长片剧本的差别：体量固定 30 分钟 8 场、结构固定三幕、不并入架构/弧光尾部——是纯正文工具。

## 核心手法

- `_build_script_body_template`（script_studio.py:552）：调 `build_standard_screenplay_scenes(scene, director, mood, intent, 30, "三幕剧")`——目标时长硬编码 30（get_beat_map 30min→8 场）、story_theory 硬编码三幕剧；再经 `format_screenplay`（pro_format.py:95）按专业台本格式渲染（cue 缩进/括号说明/潜文本行/CUT TO）。
- 潜文本行按 format_screenplay 默认"强"频率渲染（每场 1 行）——本模式未传 subtext_strength。
- 每场 heading 带幕次/阶段/戏剧张力标注（[第1幕·建置 · 场1/8 · 起 (建立) · 戏剧张力:3/10]）。
- 情绪演变弧（核心包 `_情绪演变弧`）在本模式未传入 build_standard_screenplay_scenes——弧推进只在完整长片链路生效。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 不消费 | 恒 30min/8 场——设任何值都不改变体量（与完整长片模式行为相反） |
| 叙事结构 | 无(默认)→三幕剧(经典) | 节拍主体恒三幕剧；下拉只改尾部【剧情推进】附录与维度 footer 声明 |
| 对白密度 | 无(默认)→适中 | dial_override 未传入生成器——密度档不改变每场对白行数 |
| 潜文本强度 | 无(默认)→中 | 渲染层未接线（恒按"强"频率每场 1 行）；维度 footer 仍声称已生效，以正文实际为准 |

## 已知坑

- 三个维度下拉（对白密度/潜文本强度/目标时长）在本模式"footer 声称生效、渲染层未接线"——是全节点里参数失真最明显的模式，验收正文以实际输出为准。
- 情绪演变弧不生效：需要按场推进情绪的长片写法请用完整长片剧本。
- tests/test_all_modes.py 全模式扫描断言本模式输出非空（场1/8 头部已实测）。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["剧本正文"]→`_build_script_body_template()`（:552）；渲染 aggregator/pro_format.py::format_screenplay（:95）、build_standard_screenplay_scenes（:217）
- 数据来源：aggregator/feature_film_engine.generate_feature_scenes（30min→8 场）+ aggregator/scene_engine.parse_scene
