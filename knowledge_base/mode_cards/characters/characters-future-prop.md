---
mode_id: characters-future-prop
node: DirectorMasterCharacters
name: 未来道具
one_liner: 生成未来道具卡：功能可读/界面光色统一/保留物理按键三条设计指令
applicable: [科幻短片, 赛博题材]
intensity: medium
style_tags: [服化道卡, 未来道具, 界面设计]
aliases: []
---

## 意图

做未来道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["未来道具"]` 三条指令（功能可读：一眼知道用途 / 界面光色统一世界观 / 保留物理按键的触感）；与科幻角色/科幻场景模式无代码联动。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入未来道具三条；「界面光色统一」需要世界观色号，节点无色板字段，写进描述。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4——继承源多为日常物件，未来道具务必手写。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 未来道具 | 非法值回退 角色设定 |
| 服化道描述 | （手写如「腕体征测仪, 琥珀色单色屏, 侧边三枚实体键」） | 清空后继承日常物件，未来卡里出现钢笔/收音机 |
| 视觉风格 | 3D CG | 逐字进提示词；「界面光色」与视觉风格无联动 |
| 核心数据包 | 含 _导演风格 的 JSON 包 | 导演为空回退「王家卫」；色板倾向随导演档案但不强制 |

## 已知坑

- 界面色号无字段；三科幻类模式（角色/场景/道具）的科技语汇独立成卡，世界观一致性全靠人工。
- 继承清单不筛类目，混入日常物件是常态。
- 「保留物理按键」与全触屏世界观冲突时代码不提示。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["未来道具"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
