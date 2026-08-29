---
mode_id: characters-rural
node: DirectorMasterCharacters
name: 乡村环境
one_liner: 生成乡村环境卡：季节真实/炊烟空间感/硬朗阴影三条专属设计指令
applicable: [乡土短剧, 田园题材]
intensity: medium
style_tags: [环境卡, 乡土, 自然光]
aliases: []
---

## 意图

立乡村空间锚点时选它。专属差异是 `_ENV_DESIGN["乡村环境"]` 三条指令（土路/植被季节性真实 / 炊烟与狗吠的空间感 / 光线无遮挡, 阴影硬朗）；其余与环境类基座共用。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入乡村三条；声景维度（狗吠）是文案指令，节点无音频输出。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个。
- 生成提示词拼「{环境类型}场景, {描述}, {风格}风格, {导演}导演, {情绪}情绪」，建议下拉配「室外」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 乡村环境 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承场景） | 默认厨房文本不清理就进卡 |
| 环境类型 | 室外 | 默认「室内」产生前缀错配；代码不校验模式与下拉一致性 |
| 视觉风格 | 写实 | 逐字进提示词；不做风格可行性判断 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）：模式名不进提示词。
- 季节维度无独立字段，需写进环境描述（「深秋, 秸秆已收」）才能进提示词。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["乡村环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
