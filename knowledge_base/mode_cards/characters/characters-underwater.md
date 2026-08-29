---
mode_id: characters-underwater
node: DirectorMasterCharacters
name: 水下环境
one_liner: 生成水下环境卡：丁达尔光束/气泡呼吸/色彩随深度递减三条设计指令
applicable: [海洋题材, 悬疑短片]
intensity: medium
style_tags: [环境卡, 水下, 光衰减]
aliases: []
---

## 意图

立水下空间锚点时选它。专属差异是 `_ENV_DESIGN["水下环境"]` 三条指令（光束丁达尔效应 / 气泡节奏即呼吸节奏 / 色彩随深度递减）；分支与继承机制共用环境基座。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入水下三条；深度维度无独立字段，衰减程度要写进环境描述文本才进提示词。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉，水下语义应切「水下」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 水下环境 | 非法值回退 角色设定 |
| 环境类型 | 水下 | 留默认「室内」→ 提示词「室内场景…」，水下语义丢失 |
| 环境描述 | （清空以继承场景） | 默认厨房文本不清理就进卡；深度信息需手写进描述 |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景空且描述清空 → 环境描述行空文本 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）：模式名不进提示词，进的是下拉值。
- 深度/水体浑浊度无专属字段，全靠描述文本承载。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["水下环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
