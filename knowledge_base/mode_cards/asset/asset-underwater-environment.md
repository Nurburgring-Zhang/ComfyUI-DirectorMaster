---
mode_id: asset-underwater-environment
node: DirectorMasterAsset
name: 水下环境
one_liner: 水下环境卡，指令围绕丁达尔光束/气泡呼吸/色彩递减展开
applicable: [AI漫剧, 电影, 短视频]
intensity: medium
style_tags: [水下场景, 丁达尔效应, 深度色彩]
aliases: [海底环境, 深海环境]
---

## 意图

海底/泳池/沉船等水下戏建卡时选它。指令三条是水下光学与生理专属：光束丁达尔效应、气泡节奏即呼吸节奏、色彩随深度递减。

## 核心手法

1. 设计指令块输出 `_ENV_DESIGN["水下环境"]` 三条（丁达尔/气泡呼吸/色彩递减）。
2. 环境描述留空→场景描述→parse_scene 地点词（"深海/海底/珊瑚礁"命中）→空串。
3. 场景内道具行核心物件前 4；环境锚定按导演/情绪定色调光影。
4. 一致性策略统计环境母版数，跨镜头锁定行。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 环境描述 | 自填水深/能见度 | 留空且无核心包→环境描述行空串 |
| 环境类型 | 水下（下拉含此值） | 类型槽与指令块无联动校验，填错照常输出水下指令 |
| 核心数据包 | Core 输出 JSON 包 | 场景词"深海/海底/珊瑚礁"命中地点表；"海边"是岸上不是水下，词表分开 |
| 参考图_环境母版 | IMAGE 或 STRING 路径 | 不接→母版计数 0；水下光衰减难靠文本稳定复现 |

## 已知坑

- 场景写"海边"时 parse_scene 给"海边"锚——那是岸上场景，水下指令与岸上描述会同时出现在一张卡里，需用户改用"深海/海底"。
- 呼吸节奏指令涉及人物表演，实际表演控制在 DirectorMasterCharacters/Cinematic 侧。

## 节点映射

- 实现文件：aggregator/asset_master.py
- 分支/函数：build() `mode in _ENV_MODES` 环境分支；`_ENV_DESIGN["水下环境"]`；env_desc 继承链
- 数据来源：核心数据包→aggregator/scene_engine.py :: parse_scene（水下地点词）
