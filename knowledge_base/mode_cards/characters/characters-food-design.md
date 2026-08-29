---
mode_id: characters-food-design
node: DirectorMasterCharacters
name: 食品设计
one_liner: 生成食品设计卡：热气油光/食用动作/食物人物互文三条设计指令
applicable: [美食短剧, 生活流]
intensity: medium
style_tags: [服化道卡, 食物, 生活质感]
aliases: []
---

## 意图

做食物道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["食品设计"]` 三条指令（热气/油光是生命力 / 食用动作设计 / 食物与人物关系互文）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入食品三条；「食用动作设计」是表演指令，节点不产出动作序列。
- 服化道描述清空时继承 _关键道具 + 场景物件——默认示例里「凤梨罐头(过期)」正是食品项，是全部子模式中继承语义最贴的用例之一。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 食品设计 | 非法值回退 角色设定 |
| 服化道描述 | （清空以继承，或手写如「白粥冒热气, 咸菜碟」） | 保留默认示例则罐头/信件混装进卡 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | 食品写入 _关键道具 可被继承；括号注记（过期）不拆解 |
| 视觉风格 | 写实 | 逐字进提示词 |

## 已知坑

- 食用动作/互文关系无机制承载，纯指令文案。
- 继承清单不筛食品项，非食品物件会混入。
- 括号注记（过期/热）原样进名称，状态语义混在名称串里。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["食品设计"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
