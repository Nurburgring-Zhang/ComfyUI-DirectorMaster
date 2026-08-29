---
mode_id: characters-special-prop
node: DirectorMasterCharacters
name: 特殊道具
one_liner: 生成特殊道具卡：出场即悬念/多份损耗备份/机关预测试三条设计指令
applicable: [悬疑短剧, 道具向]
intensity: medium
style_tags: [服化道卡, 悬念道具, 拍摄损耗]
aliases: []
---

## 意图

做悬念触发器类道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["特殊道具"]` 三条指令（叙事触发器：出场即悬念 / 可复制多份供拍摄损耗 / 机关·发光部件提前测试）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入特殊道具三条；「可复制多份」是制片指令，「机关预测试」是流程指令——都随卡输出给美术/制片消费，节点不执行。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4；悬念道具建议手写（如「八音盒, 发条可拆, 底盖夹层」）。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 特殊道具 | 非法值回退 角色设定 |
| 服化道描述 | （手写机关规格） | 清空后继承普通物件，悬念卡里出现罐头 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | 道具写入 _关键道具 可被继承并获道具绑定行（角色卡侧） |
| 视觉风格 | 写实 | 逐字进提示词；发光部件无独立光效字段 |

## 已知坑

- 发光/机关部件无参数化描述，亮度色温全靠手写文本。
- 与 HellGrind 模式无联动：@crystal_sword 类已注册特殊道具的状态变体在那边，本卡读不到。
- 继承清单不筛道具类目。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["特殊道具"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
