---
mode_id: script-five-act-feature
node: DirectorMasterScript
name: 五幕剧长片
one_liner: 莎士比亚五幕结构长片，五段式节拍展开，幕次在场次头显式标注
applicable: [戏剧化长片, 历史剧, 命运悲剧, 舞台改编]
intensity: high
style_tags: [五幕结构, 古典戏剧, 幕次标注, 长片体量]
aliases: []
---

## 意图

要"建置/上升/危机/高潮/结局"五段强分幕的古典戏剧骨架时选它。与三幕模式的差别：节拍生成器换成 `_beats_five_act`，每场 heading 的 [第X幕] 取值范围从 3 变为 5，幕间递进由五幕节拍表驱动。

## 核心手法

- `STRUCTURE_THEORY_MAP["五幕剧长片"]="五幕剧"`：STORY_BEATS["五幕剧"] 5 拍（建置/上升/危机/高潮/结局）作附录；feature engine `_normalize_theory("五幕剧")`→five_act。
- `_beats_five_act`（feature_film_engine.py:285）五幕骨架 expand 到目标场数，幕号随节拍 act 字段写入 heading「[第N幕·阶段]」。
- `_normalize_theory`（:836）匹配顺序刻意"五幕先于三幕"，防"三幕"子串误吞五幕输入。
- 张力曲线仍由 `_shape_tension_curve` 统一塑形，高潮拍名含"高潮/对决/终局"时强制张力 10。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事结构 | 无(默认) | 被模式名锁定为五幕剧；下拉选其他结构只改附录文本 |
| 目标时长(分钟) | 0（自动→120） | 90→25 场、60→15 场；五幕骨架 expand 保证每幕至少有场 |
| 潜文本强度 | 无(默认)→中(每句1层) | 强/极强时每场 1 行〔潜文本〕；零潜文本全片无该行 |
| 核心数据包 | Core.核心数据包 | `_情绪演变弧` 多值时按场次进度推进情绪，heading 追加「情绪:X」标注 |

## 已知坑

- 幕号来自节拍 act 字段经 expand 重排，35 场并非每幕 7 场的均匀切分——幕边界看 heading 而非等分直觉。
- 用户在叙事结构里选"四幕剧"等近似名不会改变本模式行为（模式锁定优先级高于下拉，:1762）。
- "五幕"关键词若出现在用户场景描述里不影响结构——`_normalize_theory` 只吃结构值不吃场景文本。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：build() :1762 → `_build_full_screenplay()`（:1413）
- 数据来源：aggregator/feature_film_engine.py::_beats_five_act（:285）、_normalize_theory（:836）；STORY_BEATS["五幕剧"]（script_studio.py:85）
