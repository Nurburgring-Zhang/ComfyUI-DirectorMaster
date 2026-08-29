---
mode_id: characters-scifi-scene
node: DirectorMasterCharacters
name: 科幻场景
one_liner: 生成科幻场景卡：使用痕迹/界面可读/空间服务世界观三条设计指令
applicable: [科幻短片, 赛博朋克]
intensity: medium
style_tags: [环境卡, 科幻, 世界观]
aliases: []
---

## 意图

立科幻空间锚点时选它。专属差异是 `_ENV_DESIGN["科幻场景"]` 三条指令（科技有使用痕迹不崭新 / 界面信息可读 / 空间逻辑服务于世界观）；与科幻角色/未来道具模式无代码联动。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入科幻场景三条；「使用痕迹」与科幻角色模式的着装池条目（磨损掉漆）理念同源但分属两分支，各自独立进卡。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个或 _关键道具 首段。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉（科幻场景多配太空/虚拟/室内）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 科幻场景 | 非法值回退 角色设定 |
| 环境类型 | 太空 | 按世界观选；留默认「室内」只错配提示词前缀，不改指令块 |
| 环境描述 | （清空以继承） | 默认厨房文本不清理就进卡；界面/科技要素需手写 |
| 视觉风格 | 3D CG | 科幻常配 3D CG；风格仅进提示词 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- 界面信息的「可读」标准无字段承载，落进描述文本。
- 与科幻角色模式的世界观对齐无任何机制保障，两卡独立生成。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["科幻场景"]`
- 数据来源：aggregator/scene_engine.parse_scene
