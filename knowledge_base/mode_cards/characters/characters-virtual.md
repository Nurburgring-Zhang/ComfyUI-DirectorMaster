---
mode_id: characters-virtual
node: DirectorMasterCharacters
name: 虚拟环境
one_liner: 生成虚拟环境卡：边界暴露/局部物理失效/过饱和三条专属设计指令
applicable: [赛博短片, 游戏题材]
intensity: medium
style_tags: [环境卡, 虚拟空间, 过饱和]
aliases: []
---

## 意图

立虚拟/数字空间锚点时选它。专属差异是 `_ENV_DESIGN["虚拟环境"]` 三条指令（网格/粒子暴露虚拟边界 / 物理规则可局部失效 / 色彩过饱和暗示非真实）；分支与继承机制共用环境基座。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入虚拟三条；「局部失效」的范围界定无字段承载，要写进环境描述（如「重力在半径三米内失效」）。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个。
- 生成提示词前缀取环境类型下拉，虚拟语义应切「虚拟」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 虚拟环境 | 非法值回退 角色设定 |
| 环境类型 | 虚拟 | 留默认「室内」→ 提示词「室内场景…」，虚拟语义丢失 |
| 环境描述 | （清空以继承） | 默认厨房文本不清理就进卡 |
| 视觉风格 | 3D CG | 虚拟空间常配 3D CG；风格仅进提示词，不改输出结构 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- 物理规则失效范围、边界样式皆无专属字段，全靠描述文本。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["虚拟环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
