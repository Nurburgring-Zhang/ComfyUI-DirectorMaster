---
mode_id: characters-prop-design
node: DirectorMasterCharacters
name: 道具设计
one_liner: 生成道具设计卡：可操作/特写耐放大/状态随情节演进三条设计指令
applicable: [竖屏微短剧, 短视频]
intensity: medium
style_tags: [服化道卡, 道具, 叙事演进]
aliases: []
---

## 意图

做叙事道具专项时选它。与服化道设定的差别收敛为 `_PROP_DESIGN["道具设计"]` 三条指令（道具可被演员真实操作 / 特写细节经得起放大 / 道具状态随情节演进）；分支与继承机制共用。

## 核心手法

- 走 `else:` 服化道分支，卡落「服化道圣经」路。
- 设计指令块注入道具三条；「状态随情节演进」是给分镜的时序指令，节点不产出状态序列（状态变体能力在 HellGrind资产库 模式）。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4——道具语义与继承源一致，本模式的继承是全部服化道子模式中最顺的。
- 角色绑定行取场景解析人物前 3 个；生成提示词固定追加「具体材质纹理」段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 道具设计 | 非法值回退 角色设定 |
| 服化道描述 | （清空以继承 _关键道具） | 手写则手写清单进卡；保留默认示例文本则罐头/信件进卡 |
| 核心数据包 | 含 _关键道具 的 JSON 包 | _关键道具 形如「凤梨罐头(过期), 旧信」整串进清单，括号注记不拆解 |
| 视觉风格 | 写实 | 逐字进提示词 |

## 已知坑

- 清单继承不解析括号注记：「凤梨罐头(过期)」整串进卡，状态信息混在名称里。
- 状态演进只有一行指令，无状态表；要每镜状态差异需逐镜改描述或用 HellGrind 资产状态变体。
- 角色绑定行可能有占位名（parse_scene 局限）。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["道具设计"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
