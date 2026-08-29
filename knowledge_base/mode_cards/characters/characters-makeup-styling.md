---
mode_id: characters-makeup-styling
node: DirectorMasterCharacters
name: 化妆造型
one_liner: 生成化妆造型卡：妆面服务灯光/发型物理逻辑/可触妆效三条设计指令
applicable: [都市短剧, 特效妆题材]
intensity: medium
style_tags: [服化道卡, 化妆, 特效妆]
aliases: []
---

## 意图

做妆发专项设计时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["化妆造型"]` 三条指令（妆面服务于灯光：高清镜头吃妆 / 发型有物理逻辑：风向/湿度 / 伤痕·老化妆效可触）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入化妆三条；「高清镜头吃妆」是拍摄约束型指令，随卡输出供美术消费，节点不做灯光联动。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4——妆发语义弱，建议手写妆发清单（如「右眉断痕, 嘴角旧疤」）。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 化妆造型 | 非法值回退 角色设定 |
| 服化道描述 | （手写妆发清单） | 清空后继承道具物件，产出的「妆」清单可能是罐头/钢笔 |
| 核心数据包 | 含 _导演风格 的 JSON 包 | 导演为空回退「王家卫」；灯光相关指令与导演档案无联动 |
| 视觉风格 | 写实 | 逐字进提示词；妆效风格不做校验 |

## 已知坑

- 继承源与模式语义错位（同服装设计）：清空描述继承到的是道具清单。
- 与角色类模式的外貌字段无联动：角色脸上的疤写在角色卡外貌里，本卡不会读到。
- 指令无量化参数（伤效年代/妆层厚度），细节全靠手写清单。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["化妆造型"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
