---
mode_id: characters-weapon-design
node: DirectorMasterCharacters
name: 武器设计
one_liner: 生成武器设计卡：重量感/包浆历史/机关自洽三条专属设计指令
applicable: [动作短剧, 奇幻题材]
intensity: medium
style_tags: [服化道卡, 武器, 机关逻辑]
aliases: []
---

## 意图

做武器道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["武器设计"]` 三条指令（重量感通过演员身体表现 / 磨损/包浆暗示使用历史 / 机关结构逻辑自洽）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入武器三条；重量感/包浆无量化字段，具体规格要写进服化道描述（如「军刺, 刃面三处缺口, 握柄缠布磨亮」）。
- 服化道描述清空时继承 _关键道具 + 场景物件——场景少武器时继承错位，建议手写。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 武器设计 | 非法值回退 角色设定 |
| 服化道描述 | （手写武器规格清单） | 清空后继承普通物件，武器卡里出现罐头/收音机 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | 武器写在 _关键道具 里可被继承；括号注记不拆解 |
| 视觉风格 | 写实 | 逐字进提示词；奇幻武器配水墨/油画只改文案 |

## 已知坑

- 机关结构自洽全靠手写描述，代码无结构校验或图示能力。
- 继承清单不区分武器/非武器，混入日常物件是常态而非异常。
- 武器状态变体（出鞘/染血）无机制，HellGrind 模式的状态变体仅覆盖其注册资产（@crystal_sword 等）。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["武器设计"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
