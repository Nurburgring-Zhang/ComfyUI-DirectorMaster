---
mode_id: characters-period-prop
node: DirectorMasterCharacters
name: 时代道具
one_liner: 生成时代道具卡：材质工艺考据/旧化分层/防穿越穿帮三条设计指令
applicable: [年代戏, 历史短剧]
intensity: medium
style_tags: [服化道卡, 年代考据, 旧化]
aliases: []
---

## 意图

做年代道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["时代道具"]` 三条指令（年代考据：材质/印刷/工艺 / 旧化程度分层：全新库存/常用/废弃 / 避免穿越感穿帮）；与历史环境模式构成「环境-道具」年代对，但两分支无代码联动。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入时代道具三条；旧化三档（全新库存/常用/废弃）是分级指令，具体到哪一档要写进描述。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4；年代信息（如「民国铅印」）必须手写进描述，继承源不带年代维度。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 时代道具 | 非法值回退 角色设定 |
| 服化道描述 | （手写如「民国铅印传单, 纸边毛脆」） | 清空后继承普通物件且无年代标注，防穿帮指令落空 |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 年代写进场景描述可间接进卡；仅写 _关键道具 则无年代信息 |
| 视觉风格 | 写实 | 逐字进提示词 |

## 已知坑

- 年代字段不存在：描述里不写年份/工艺，卡内无任何年代锚点。
- 旧化三档不裁决，三词同时进指令块。
- 与历史环境模式的考据口径各自独立，两卡可能给出矛盾年代。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["时代道具"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
