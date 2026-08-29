---
mode_id: script-vertical-short-drama
node: DirectorMasterScript
name: 竖屏微短剧
one_liner: 9:16 竖屏短剧策划：前 3 秒定生死，第 8-10 集首个付费点
applicable: [抖音短剧, 快手短剧, 9:16 竖屏内容]
intensity: medium
style_tags: [竖屏满屏, 前3秒钩子, 付费卡点, 安全区字幕]
aliases: []
---

## 意图

抖音/快手 9:16 竖屏微短剧立项时选它：60-90 秒一集、60-80 集，第一帧即冲突最高点。与小程序剧的差别：更强调平台 UI 遮挡规避（居中安全区字幕）与"前 3 秒定生死"的开场纪律。

## 核心手法

- `SHORT_DRAMA_SUBTYPES["竖屏微短剧"]`（script_studio.py:763）：定位"9:16 满屏，前3秒定生死"、单集 60-90 秒、总集数 60-80、爽虐甜 (4,3,3)+seed 漂移。
- 钩子池三选一：第一帧就是冲突最高点 / 对镜头说不该说的话 / 物件从画面角落缓缓移入——全部为竖屏第一帧服务。
- 付费卡点固定"第 8-10 集首个付费点：{obj}背后的秘密"，字幕策略为居中安全区避开平台 UI。
- 注入 25 故事感总纲 + 14 真实短剧案例；tests/test_all_modes.py 对本模式有"故事感总纲注入/真实短剧制作案例"双断言。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 对白密度 | 无(默认)→标准对白 | "零对白"→纯画面+字幕叙事，第3镜改手部动作+眼神承担情绪 |
| 节奏控制 | 无(默认)→中速 | "超快(抖音1s/镜)"命中"超快"词根→镜时长压到 2s/3s/2s；但模板不会真到 1s/镜 |
| 潜文本强度 | 无(默认)→中 | 默认追加"每镜一层潜文本"行；选零→删除该行 |
| 核心数据包 | Core.核心数据包 | `_平台媒介` 随 dims["平台"] 传入但不进短剧模板正文，仅影响 AIGC 块（目标时长≤3min 时） |

## 已知坑

- 节奏控制下拉里"超快(抖音1s/镜)"词面最贴本模式，但模板最低只压到 2s/3s/2s 三档，不会真到 1s/镜——1s 级切镜属于 Cinematic 节点职责。
- 付费点集数"第 8-10 集"为固定文案，不随总集数参数化。
- 库注入链路依赖 story_sense_data/master_director_data 可导入；两者缺失时输出静默变短，不报错。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["竖屏微短剧"]→`_build_short_drama_template()`（:806）；SHORT_DRAMA_SUBTYPES["竖屏微短剧"]（:763）；`inject_library_depth()`（:288-294 短剧分支）
- 数据来源：SHORT_DRAMA_SUBTYPES 内置表 + story_sense_data.STORY_SENSE_LIBRARY（25）+ master_director_data.REAL_DRAMA_CASES（14）
