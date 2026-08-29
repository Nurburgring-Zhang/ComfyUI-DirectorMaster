---
mode_id: characters-exterior
node: DirectorMasterCharacters
name: 室外环境
one_liner: 生成室外环境卡：天气叙事/地面反光/天际线情绪三条专属设计指令
applicable: [都市短剧, 公路题材]
intensity: medium
style_tags: [环境卡, 外景, 天气叙事]
aliases: []
---

## 意图

立外景空间锚点时选它。专属差异是 `_ENV_DESIGN["室外环境"]` 三条指令（天气作为情绪参与叙事 / 地面材质反光控制 / 远景天际线压缩或释放情绪）；其余机制与环境类基座共用。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入室外三条；天气维度代码无独立字段，靠描述文本与提示词承载。
- 环境描述清空时继承核心场景文本（scene → core_loc 两级回退）；场景内道具行取场景物件前 4 个。
- 生成提示词前缀取环境类型下拉值；室外语义建议下拉选「室外」，但代码不强制。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 室外环境 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承场景） | 保留默认值则「厨房8平米…」文本进卡，与外景语义冲突且代码不校验 |
| 环境类型 | 室外 | 选室内只换提示词前缀，不换分支；室外模式配「室内」=自相矛盾输出 |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景全空且描述清空 → 环境描述行空文本 |

## 已知坑

- 下拉与子模式不同步问题在本模式最易踩：室外语义 + 默认「室内」下拉 = 提示词「室内场景…」。
- 天气/时段是 parse_scene 可提取维度（time/weather 键），但环境卡不直接输出时段字段，时段信息只随场景文本间接带入。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["室外环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
