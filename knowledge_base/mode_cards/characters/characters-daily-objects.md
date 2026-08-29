---
mode_id: characters-daily-objects
node: DirectorMasterCharacters
name: 日常用品
one_liner: 生成日常用品卡：用品即习惯化石/品牌年代辨识/使用痕迹三条设计指令
applicable: [生活流短剧, 现实题材]
intensity: medium
style_tags: [服化道卡, 生活道具, 使用痕迹]
aliases: []
---

## 意图

做生活物件专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["日常用品"]` 三条指令（用品即人物习惯的化石 / 品牌/年代可辨识或彻底素体 / 使用痕迹真实）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入日常用品三条；「品牌/年代可辨识或彻底素体」是二选一决策指令，代码不裁决，落在描述文本里。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4；默认示例的钢笔/收音机即日常用品，继承语义贴合。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 日常用品 | 非法值回退 角色设定 |
| 服化道描述 | （清空以继承场景物件） | 手写则手写清单进卡；真实品牌名有版权风险，代码不做提示 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | 不接则清单退化为默认示例或「未指定」 |
| 视觉风格 | 写实 | 逐字进提示词 |

## 已知坑

- 品牌名照抄进卡无合规检查，「彻底素体」与「可辨识」的取舍全在用户。
- 继承清单不筛日常用品类目。
- 使用痕迹程度无量化字段。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["日常用品"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
