---
mode_id: script-horizontal-short-drama
node: DirectorMasterScript
name: 横屏微短剧
one_liner: 16:9 横屏短剧策划案：单集 2-3 分钟×30-40 集，双信息层调度
applicable: [横屏短剧, 平台网剧, 精品短剧]
intensity: medium
style_tags: [横屏构图, 分集策划, 付费卡点, 电影字幕条]
aliases: []
---

## 意图

做横屏（16:9）平台短剧时选它：调度空间大，靠构图与信息层而非满屏怼脸叙事。与竖屏系的差别：钩子设计依赖横移长镜/前后景虚化等横屏调度，字幕策略为底部电影字幕条。

## 核心手法

- `_build_short_drama_template` + `SHORT_DRAMA_SUBTYPES["横屏微短剧"]`（script_studio.py:771）：子类型定位"16:9 构图叙事，调度空间更大"、单集 2-3 分钟、总集数 30-40。
- 三个钩子模板（横移长镜停在主角/前景物件虚化后景表情渐变/一场戏两个信息层）按 `md5(场景_导演_模式)` seed 确定性选一，卡点=季中点发现物件关联。
- 爽虐甜比例 (4,3,3) 加 seed%3 漂移输出；第1集前 4 镜的镜时长由节奏控制维度决定（极快 2s/3s/2s，慢 5s/8s/5s，默认 3s/5s/3s）。
- inject_library_depth 按"短剧"关键词注入 25 故事感总纲 + 14 真实短剧制作案例（含团队/时长/镜头数/踩坑）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节奏控制 | 无(默认)→中速 | "极快/超快"→镜时长 2s/3s/2s 并标注"卡点更密"；"变速/交替"→快慢交替 2s/6s/2s |
| 对白密度 | 无(默认)→标准对白 | "零对白"→输出改为"纯画面+字幕叙事"且第3镜无台词；"密集"→连珠炮台词版第3镜 |
| 目标时长(分钟) | 不消费 | 短剧模板单集时长/集数来自子类型表；仅当 ≤3min 时 build() 层额外追加 AIGC 五段结构块 |
| 核心数据包 | Core.核心数据包 | 缺失时场景/角色占位（关键道具/主角）直接进钩子文案 |

## 已知坑

- 设"目标时长(分钟)"不会改变单集时长——它由子类型表硬编码；唯一影响是 ≤3min 时追加与短剧无关的 AIGC 时间拍块。
- 钩子/卡点文案是子类型模板插值（c1/obj/loc），不感知用户具体题材，古风题材也可能出"掏出手机"式现代钩子。
- 案例库注入依赖 master_director_data 导入成功，库缺失时该块静默为空（tests/test_all_modes.py 对竖屏系有注入断言，横屏同链路）。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["横屏微短剧"]→`_build_short_drama_template()`（:806）；SHORT_DRAMA_SUBTYPES["横屏微短剧"]（:771）；注入 `inject_library_depth()`（:278）
- 数据来源：SHORT_DRAMA_SUBTYPES 内置表 + story_sense_data.STORY_SENSE_LIBRARY（25 总纲）+ master_director_data.REAL_DRAMA_CASES（14 案例）
