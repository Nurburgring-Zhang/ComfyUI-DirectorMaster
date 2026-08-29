---
mode_id: characters-realistic-scene
node: DirectorMasterCharacters
name: 现实场景(写实)
one_liner: 生成写实场景卡：自然光优先/环境音保留/允许不完美三条设计指令
applicable: [现实题材, 纪录感短片]
intensity: medium
style_tags: [环境卡, 写实, 自然光]
aliases: [写实场景]
---

## 意图

立纪录感空间锚点时选它。专属差异是 `_ENV_DESIGN["现实场景(写实)"]` 三条指令（自然光优先, 不打修饰光 / 环境音完整保留 / 允许画面'不完美'）；名称含半角括号，是 42 个创作模式中唯一带括号的枚举值。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入写实三条；「允许不完美」是对抗过度修饰的负面清单指令，无字段承载。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个或 _关键道具 首段。
- 环境锚定块按导演定主色调、按情绪定光影——写实语义与「按导演定」存在张力，主色调倾向仍由导演档案决定。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 现实场景(写实) | 必须逐字含半角括号；写成「现实场景(写实) 」带空格或全角括号 → 回退 角色设定 |
| 环境描述 | （清空以继承场景） | 默认厨房文本不清理就进卡 |
| 环境类型 | 室内/室外 | 按实际场景选；不选只影响提示词前缀 |
| 核心数据包 | 含 _导演风格 的 JSON 包 | 导演为空回退「王家卫」，其档案色倾向可能与「自然光优先」指令相左 |

## 已知坑

- 名称括号是半角：manifest 与下拉枚举逐字为「现实场景(写实)」，frontmatter name 必须逐字（sync 逐字匹配，全角括号即孤儿卡）。
- 下拉与子模式不同步（全环境类共性）。
- 「自然光优先」与导演档案块的色调倾向无仲裁逻辑，两段文本并存于卡内。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["现实场景(写实)"]`
- 数据来源：aggregator/scene_engine.parse_scene；导演块 director_data_unified
