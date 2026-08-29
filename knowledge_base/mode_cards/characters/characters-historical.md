---
mode_id: characters-historical
node: DirectorMasterCharacters
name: 历史环境
one_liner: 生成历史环境卡：建材照明考据/防穿帮/仪态符合时代三条设计指令
applicable: [历史短剧, 年代戏]
intensity: medium
style_tags: [环境卡, 年代考据, 防穿帮]
aliases: []
---

## 意图

立年代空间锚点时选它。专属差异是 `_ENV_DESIGN["历史环境"]` 三条指令（年代考据：建材/照明/交通工具 / 无现代痕迹穿帮 / 人群仪态符合时代）；分支与继承机制共用环境基座。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入历史三条；「无现代痕迹穿帮」是检查清单式指令，节点不做图像校验，靠下游生成时自查。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个——现代物件名会原样进卡，年代过滤要靠手写描述。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 历史环境 | 非法值回退 角色设定 |
| 环境描述 | （清空以继承场景） | 默认厨房文本不清理就进卡；年代（如「1937 上海」）必须写进描述 |
| 环境类型 | 室内 | 年代戏多室内景；但默认值不随模式变，需按实际选 |
| 视觉风格 | 写实 | 年代戏建议写实；风格仅进提示词 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- 年代数字无专属字段：写不进描述就不会出现在提示词，「考据」无从谈起。
- 核心场景若含现代物件（手机/空调），道具行会照抄进卡——「无现代痕迹」指令与继承数据可能自相矛盾，需人工清描述。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["历史环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
