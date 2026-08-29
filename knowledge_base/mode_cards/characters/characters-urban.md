---
mode_id: characters-urban
node: DirectorMasterCharacters
name: 城市环境
one_liner: 生成城市环境卡：信息密度/人流反向节奏/混合色温三条专属设计指令
applicable: [都市短剧, 赛博题材]
intensity: medium
style_tags: [环境卡, 都市, 信息密度]
aliases: []
---

## 意图

立城市空间锚点时选它。专属差异是 `_ENV_DESIGN["城市环境"]` 三条指令（招牌/管线/空调外机构成信息密度 / 人流节奏与主角节奏相反 / 夜色用混合色温）；分支与继承机制共用环境基座。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入城市三条；「人流节奏与主角节奏相反」是调度指令，进卡供下游分镜消费，节点本身不做人物关联。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个或 _关键道具 首段。
- 环境锚定块三行（主色调按导演/光影按情绪/道具位置按场景）+ 一致性策略行（参考图计数）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 城市环境 | 非法值回退 角色设定 |
| 环境类型 | 室外 | 城市语义应选室外；默认「室内」会生成「室内场景…」前缀错配 |
| 环境描述 | （清空以继承） | 保留默认厨房文本直接进卡 |
| 核心数据包 | 含 _导演风格 的 JSON 包 | 导演为空回退「王家卫」；主色调/光影锚定行按该导演与情绪生成 |

## 已知坑

- 提示词前缀由环境类型下拉决定，与本模式名无关（全环境类共性问题）。
- 城市指令中的「夜色」无时段字段支撑，时段要写进环境描述文本。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["城市环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
