---
mode_id: script-save-the-cat-15-beats
node: DirectorMasterScript
name: 救猫咪15拍长片
one_liner: Blake Snyder 15 节拍商业片骨架，从开场画面到结尾画面逐拍展开
applicable: [商业类型片, 好莱坞式长片, 合家欢, 类型片]
intensity: high
style_tags: [救猫咪节拍, 商业结构, 类型片, 长片体量]
aliases: [救猫咪节拍表]
---

## 意图

按 Blake Snyder 15 拍写商业长片时选它。与三幕/五幕的差别：节拍骨架是"开场画面→主题陈述→…→灵魂的黑夜→终局→结尾画面"的 15 个功能位，且首尾画面要求对称。

## 核心手法

- `STRUCTURE_THEORY_MAP["救猫咪15拍长片"]="救猫咪15拍"`：STORY_BEATS["救猫咪15拍"] 15 拍全名附录 + `_normalize_theory`→save_the_cat。
- `_beats_save_the_cat`（feature_film_engine.py:59）15 骨架拍各自带预设张力/密度（争论 6/high、第一情节点 7/high、灵魂的黑夜 9/low、终局 10/high）。
- 骨架 expand 后每拍 1-4 场（关键转折拍常为 1 场）；中点拍名"虚假胜利 (A+B 交叉)"未命中关键词表，落全场景池拼接兜底。
- 尾拍"结尾画面 (对称开场)"张力争 4/low——张力曲线在此处释放回落，呼应开场画面的 2/low。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事结构 | 无(默认) | 锁定为救猫咪15拍；下拉值仅改附录节拍文本 |
| 目标时长(分钟) | 0（自动→120→35 场） | 15 拍骨架在任意时长下都完整存在，只改变每拍摊到的场数 |
| 节奏控制 | 无(默认)→中速(标准) | "极慢/慢("→场次体量×0.75，"极快/快("→×1.3，其余值不缩放 |
| 核心数据包 | Core.核心数据包 | `_成片时长` 字符串里的最大数字会被解析为目标时长（"8-15分钟"取 15） |

## 已知坑

- "15 拍"≠15 场：120min 默认输出 35 场，每拍摊 1-4 场（关键转折拍常为 1 场）；想要一拍一场需把目标时长压到 15-30min（10 场内）甚至更低。
- 叙事结构下拉若选"救猫咪15拍(Blake Snyder)"与本模式效果一致，但选"动作(任务递进)"也会落 save_the_cat 生成器（`_normalize_theory` :886-888 动作→商业15拍），跨模式节拍同构。
- 灵魂的黑夜拍密度为 low——配合"密集(快节奏对话)"下拉时该拍仍走低密度，属节拍骨架优先。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() :1762 → `_build_full_screenplay()`（:1413）
- 数据来源：aggregator/feature_film_engine.py::_beats_save_the_cat（:59）、_expand_beats_to_n（:528）；STORY_BEATS["救猫咪15拍"]（script_studio.py:87）
