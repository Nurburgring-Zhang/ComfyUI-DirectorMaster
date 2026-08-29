---
mode_id: characters-memory-scene
node: DirectorMasterCharacters
name: 记忆场景
one_liner: 生成记忆场景卡：色调抽离/选择性清晰/声音先行三条专属设计指令
applicable: [回忆桥段, 心理短片]
intensity: medium
style_tags: [环境卡, 回忆, 褪色调]
aliases: []
---

## 意图

立回忆空间锚点时选它。专属差异是 `_ENV_DESIGN["记忆场景"]` 三条指令（色调抽离：过曝或褪色 / 细节选择性清晰 / 声音先于画面出现）；与梦境场景的分工：记忆做「真实底版的抽离处理」，梦境做「底版的变形」。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入记忆三条；抽离程度（过曝或褪色二选一）无字段承载，落进环境描述或靠提示词情绪段。
- 环境描述清空时继承核心场景文本——回忆通常引用已建立的实景，继承即预期用法。
- 环境锚定块按导演定主色调、按情绪定光影；「声音先于画面」是剪辑指令，节点无音频输出。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 记忆场景 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承原实景） | 手写时写回忆中的差异项；保留默认厨房文本则厨房成回忆底版 |
| 环境类型 | 室内 | 与被回忆实景保持一致即可；只影响提示词前缀 |
| 核心数据包 | 含 _情绪基调 的 JSON 包 | 情绪为空 → 抽离方向（过曝/褪色）与光影锚定都悬空 |

## 已知坑

- 色调抽离的二选一（过曝或褪色）代码不裁决，两词同时进指令块。
- 下拉与子模式不同步（全环境类共性）。
- 与梦境场景指令零重叠，是 16 环境子模式中区分度最清晰的一对，互审按指令逐字比对。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["记忆场景"]`
- 数据来源：aggregator/scene_engine.parse_scene
