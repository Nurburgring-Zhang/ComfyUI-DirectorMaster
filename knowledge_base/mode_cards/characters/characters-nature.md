---
mode_id: characters-nature
node: DirectorMasterCharacters
name: 自然环境
one_liner: 生成自然环境卡：声景底色/植物三层/天气推情节三条专属设计指令
applicable: [探险题材, 田园短片]
intensity: medium
style_tags: [环境卡, 自然, 天气驱动]
aliases: []
---

## 意图

立荒野/山林类空间锚点时选它。专属差异是 `_ENV_DESIGN["自然环境"]` 三条指令（风声/水声作为情绪底色 / 植物层次：近草/中灌/远林 / 天气变化推动情节）；其余机制与环境类基座共用。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入自然三条；「天气变化推动情节」是叙事指令，节点不改写剧本，仅随卡输出供下游分镜消费。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个（自然场景常解析为空 → 显示「无」）。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉值。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 自然环境 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承场景） | 保留默认厨房文本直接进卡，与自然语义冲突 |
| 环境类型 | 室外 | 默认「室内」前缀错配；代码不拦截 |
| 核心数据包 | 含 _情绪基调 的 JSON 包 | 情绪为空 → 光影锚定行与提示词情绪段留空 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- parse_scene 对自然场景常提不出物件，场景内道具行落「无」——这是预期回退而非缺陷，但卡面会显得空。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["自然环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
