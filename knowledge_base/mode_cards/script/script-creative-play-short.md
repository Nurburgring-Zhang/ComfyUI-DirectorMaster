---
mode_id: script-creative-play-short
node: DirectorMasterScript
name: 创意玩法短视频
one_liner: 反常识开场→规则演示→组合反转→记忆点收尾的 4 槽创意短视频
applicable: [抖音短视频, 创意短片, 玩法演示类内容]
intensity: medium
style_tags: [反常识钩子, 规则演绎, 记忆点, 视觉优先]
aliases: []
---

## 意图

靠"创意玩法"本身抓人的 30-60 秒短视频：观众为"为什么会这样"停留。与脑洞剧情的差别：脑洞以世界观设定为核心，本模式以一个可演示的创意玩法为核心，逻辑强度要求低、视觉记忆点要求高。

## 核心手法

- `FORMAT_SCENE_SKELETONS["创意玩法短视频"]`（script_studio.py:944）4 结构槽：钩子位·反常识开场(0-3s)→创意展开·规则演示→创意升级·组合反转→记忆点·收尾定格；1min 目标时长下场景数=4 槽。
- 执行层 `_apply_format_execution_layer`（:1164 短视频分支）逐场追加镜数预算（3-5/5-8/4-6 镜）、首镜设计（物件特写/反常动作/空镜异响三选一）、收尾方式（定格 0.5s/黑场 0.3s/循环首尾帧）。
- `FORMAT_MODE_FLAVOR`（:903）注入格式约定：台词≤10 句、视觉创意优先于叙事、单场景闭环无支线。
- 目标时长 1min ≤3 → build() 层追加 `_build_aigc_five_section` 时间拍块（aigc_prompt_builder.py:381 五段结构+模型建议+自检）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0（自动→1） | 显式设 >24 分钟会退出骨架场数覆盖，场景数改由时长阶梯算且槽位按比例映射 |
| 节奏控制 | 无(默认)→中速 | 本模式场数固定 4 槽，节奏只影响场内文字时长感；"极快/快("→eff_minutes×1.3 不改变 4 槽 |
| 潜文本强度 | 无(默认)→中 | 控制〔潜文本〕行频率；创意玩法依赖画面而非潜文本，选零影响小 |
| 核心数据包 | Core.核心数据包 | 缺失时执行层的"记忆物件"落"关键道具"，首镜设计失焦 |

## 已知坑

- 执行层"镜数预算 3-8 镜"是给拍摄/分镜的建议数字，本节点不产出分镜——承接下游是 Cinematic 节点。
- 用户显式设目标时长 2 分钟以上（仍 ≤24）时场景数仍是 4 槽，不会因时长变长而加场——长创意内容应换脑洞剧情短视频（2min）或直接拉长目标时长走比例映射。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：默认 builder `_build_full_screenplay()`（:1413）+ FORMAT_SCENE_SKELETONS["创意玩法短视频"]（:944）+ `_apply_format_scene_skeleton`（:1122）+ 执行层短视频分支（:1189-1195）
- 数据来源：FORMAT_SCENE_SKELETONS/FORMAT_MODE_FLAVOR 内置表 + aggregator/scene_engine.parse_scene + aggregator/aigc_prompt_builder.build_five_section_block
