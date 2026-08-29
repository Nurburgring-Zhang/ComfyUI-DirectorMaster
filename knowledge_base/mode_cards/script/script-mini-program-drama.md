---
mode_id: script-mini-program-drama
node: DirectorMasterScript
name: 竖屏小程序剧
one_liner: 小程序剧通用策划：90 秒一集×80 集，付费卡点精准投放
applicable: [小程序剧, 微信投流短剧, 付费短剧]
intensity: medium
style_tags: [小程序剧, 强钩子, 付费卡点, 白字黑边]
aliases: []
---

## 意图

微信/抖字小程序投流短剧的通用形态：没有强题材预设，靠"反常动作/特写/空镜异响"三类万能钩子开集。与爽剧/反转专项的差别：配比中性 (4,3,3)，卡点是"物件真相首次揭晓"而非情绪爆点。

## 核心手法

- `SHORT_DRAMA_SUBTYPES["竖屏小程序剧"]`（script_studio.py:755）：单集 90 秒、总集数 80、爽虐甜 (4,3,3)+seed 漂移。
- 钩子池三选一：一个反常动作停在半空 / 物件特写有不该出现的东西 / 空镜一声异响——三类分别对应动作/道具/空间钩子。
- 字幕策略"标准白字黑边，悬念处字幕悬停"；卡点"{obj}的真相首次揭晓"。
- 本 subtype 同时是 `_build_short_drama_template` 的兜底键（:817 `SHORT_DRAMA_SUBTYPES.get(mode, ...["竖屏小程序剧"])`）：未来新增短剧模式未登记子类型时回落此表。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 对白密度 | 无(默认)→标准对白 | "零对白"→纯画面+字幕叙事，第3镜无台词；"密集"→连珠炮版 |
| 节奏控制 | 无(默认)→中速 | "极快/超快"→2s/3s/2s；"变速/交替"→2s/6s/2s |
| 主题深度 | 无(默认)→中(人物成长) | 核心包含主题词且"深/极深/存在主义/形而上"→追加主题陈述行；纯娱乐向无此行 |
| 核心数据包 | Core.核心数据包 | 缺失时 obj/loc 落"关键道具/场景"占位，卡点文案失去具体性 |

## 已知坑

- 兜底回落意味着"垂直短剧"等未挂到下拉的子类型键也会产出本表内容——卡里模式名与表键一致才保证专属文案。
- 80 集体量只出第 1 集设计；投流用的多集矩阵需换场景多次生成。
- 目标时长不消费；≤3min 时 build() 层追加的 AIGC 五段块与本模板的策划口径（90 秒/集）可能冲突，需人工取舍。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["竖屏小程序剧"]→`_build_short_drama_template()`（:806）；SHORT_DRAMA_SUBTYPES["竖屏小程序剧"]（:755）；兜底 get 默认（:817）
- 数据来源：SHORT_DRAMA_SUBTYPES 内置表 + story_sense_data.STORY_SENSE_LIBRARY + master_director_data.REAL_DRAMA_CASES
