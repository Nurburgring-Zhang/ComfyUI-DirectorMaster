---
mode_id: characters-postapocalyptic
node: DirectorMasterCharacters
name: 末世环境
one_liner: 生成末世环境卡：文明残骸/植被收复/天空不干净三条专属设计指令
applicable: [末世短剧, 废土题材]
intensity: medium
style_tags: [环境卡, 末世, 废土]
aliases: []
---

## 意图

立废土空间锚点时选它。专属差异是 `_ENV_DESIGN["末世环境"]` 三条指令（文明残骸的具体物件：半块招牌/锈蚀车辆 / 植被 reclaim 人造物 / 天空永远不干净）；分支与继承机制共用环境基座。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入末世三条；残骸物件的「具体性」靠环境描述文本落地（指令只给方向）。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个或 _关键道具 首段。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉，末世多在室外，建议切「室外」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 末世环境 | 非法值回退 角色设定 |
| 环境类型 | 室外 | 留默认「室内」→ 提示词「室内场景…」；代码不做语义校验 |
| 环境描述 | （清空以继承场景） | 默认厨房文本不清理就进卡；残骸物件需写进描述 |
| 核心数据包 | 含 _情绪基调 的 JSON 包 | 情绪为空 → 光影锚定行与提示词情绪段留空 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- 末世年代/灾变类型无字段，全靠描述文本承载；与历史环境模式的「年代考据」指令是反方向的两种考据，别混用。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["末世环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
