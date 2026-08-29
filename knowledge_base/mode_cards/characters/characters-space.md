---
mode_id: characters-space
node: DirectorMasterCharacters
name: 太空环境
one_liner: 生成太空环境卡：零重力细节/舱壁冷光/指示灯唯一暖色三条设计指令
applicable: [科幻短片, 太空题材]
intensity: medium
style_tags: [环境卡, 太空, 零重力]
aliases: []
---

## 意图

立太空舱/深空空间锚点时选它。专属差异是 `_ENV_DESIGN["太空环境"]` 三条指令（零重力漂浮细节：头发/水滴/衣物 / 舱壁冷光与舷外深空对比 / 设备指示灯是唯一暖色）；本模式是最容易踩「下拉不同步」坑的场景之一。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入太空三条；零重力细节是提示词层指令，节点不做物理模拟。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个或 _关键道具 首段，全无写「无」。
- 生成提示词前缀取环境类型下拉——太空语义必须把下拉切到「太空」，否则产「室内场景, …」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 太空环境 | 非法值回退 角色设定 |
| 环境类型 | 太空 | 留默认「室内」→ 提示词「室内场景, 厨房8平米…」（probe 实证），太空语义完全丢失 |
| 环境描述 | （清空以继承） | 默认厨房文本不清理就进卡，与舱内场景混搭 |
| 视觉风格 | 写实 | 可配 3D CG；风格只进提示词文案 |

## 已知坑

- probe 实证本模式 + 默认下拉/默认描述 → 「环境类型: 室内 / 环境描述: 厨房8平米… / 生成提示词: 室内场景, 厨房8平米…」——三处都要人工纠正。
- 设计指令与下拉值无一致性校验，防穿帮靠使用者。
- 三视图锚定路输出占位句；MIP 卡为角色向内容。
- tests/test_all_modes.py 断言本模式执行非空（默认参数即触发上述错配，仍判非空通过）。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["太空环境"]`
- 数据来源：aggregator/scene_engine.parse_scene
