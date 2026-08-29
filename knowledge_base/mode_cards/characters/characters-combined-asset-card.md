---
mode_id: characters-combined-asset-card
node: DirectorMasterCharacters
name: 综合资产卡
one_liner: 三库联动指令的服化道分支卡：输出落服化道圣经，不合并角色环境输出
applicable: [多资产项目, 长片]
intensity: adaptive
style_tags: [服化道卡, 三库联动, 派生策略]
aliases: []
---

## 意图

想在一张卡里统筹角色/环境/道具时选它——但必须知道实现口径：本模式落在服化道分支，输出只进「服化道圣经」路，角色圣经与环境圣经两路为空串（probe 实证六路长度 [0,0,1903,25,402,1903]）。「三库联动」是指令文案，不是合并输出。

## 核心手法

- 走 `else:` 服化道分支（_CHARACTER_MODES/_ENV_MODES 均不含本模式），产出「服化道卡 · [综合资产卡]」。
- 设计指令块注入 `_PROP_DESIGN["综合资产卡"]` 三条：角色/环境/道具三库联动、母版资产锁定后批量派生、跨镜头一致性优先——全部为策略文案，随卡输出供下游消费。
- 服化道描述清空时继承 _关键道具 + 场景物件前 4；角色绑定行取场景解析人物前 3。
- MIP 资产卡路照常输出多 IP 锚定策略（主 IP=角色名），是本模式「统筹」语义在六路中的实际落点。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 综合资产卡 | 非法值回退 角色设定 |
| 服化道描述 | （清空以继承 _关键道具+场景物件） | 保留默认示例文本则罐头/信件进卡 |
| 核心数据包 | 含 _场景描述+_关键道具 的 JSON 包 | 不接 → 清单「未指定」、无角色绑定、无三库素材 |
| 视觉风格 | 写实 | 逐字进生成提示词与 MIP 卡风格段 |

## 已知坑

- 期望「一张卡合并三路」会落空：六路输出只有服化道圣经/三视图占位/MIP/完整资产非空，角色与环境仍需各自模式出卡。
- probe 实证三视图锚定路输出 25 字占位句「(非角色模式 — 三视图锚定仅在角色类模式下生成)」。
- MIP 资产卡的「副IP: 道具母版（旧信/凤梨罐头/钢笔/收音机）」是硬编码示例文本，不随用户道具变化（characters_master._build_mip_card）。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + costume 路由 + _build_mip_card()）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `else:` 分支；设计指令 `_PROP_DESIGN["综合资产卡"]`
- 数据来源：核心数据包 _关键道具 + aggregator/scene_engine.parse_scene
