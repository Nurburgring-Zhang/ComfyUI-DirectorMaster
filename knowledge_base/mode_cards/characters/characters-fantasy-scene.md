---
mode_id: characters-fantasy-scene
node: DirectorMasterCharacters
name: 奇幻场景
one_liner: 生成奇幻场景卡：尺度夸张/自洽生态/有规则超自然光三条设计指令
applicable: [奇幻短剧, 玄幻动画]
intensity: medium
style_tags: [环境卡, 奇幻, 超自然光]
aliases: []
---

## 意图

立奇幻空间锚点时选它。专属差异是 `_ENV_DESIGN["奇幻场景"]` 三条指令（物理尺度夸张：巨树/浮岛 / 自洽的生态链 / 光源可超自然但有规则）；与奇幻角色模式无代码联动，世界观对齐靠人工。

## 核心手法

- 进入 `elif mode in _ENV_MODES:` 分支，环境卡落「环境圣经」路。
- 设计指令块注入奇幻场景三条；尺度与生态细节无字段承载，落进环境描述文本。
- 环境描述清空时继承核心场景文本；场景内道具行取场景物件前 4 个。
- 环境锚定块按导演定主色调、按情绪定光影；生成提示词前缀取环境类型下拉（奇幻场景多虚拟/室外）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 奇幻场景 | 非法值回退 角色设定 |
| 环境类型 | 虚拟 | 奇幻空间常配虚拟/室外；留默认「室内」→ 提示词前缀错配 |
| 环境描述 | （清空以继承） | 默认厨房文本不清理就进卡；巨树/浮岛等尺度要素需手写 |
| 视觉风格 | 油画 | 奇幻可配油画/水彩；风格仅进提示词 |

## 已知坑

- 下拉与子模式不同步（全环境类共性）。
- 「有规则」的超自然光规则要写进描述，代码无规则字段；不写则指令悬空。
- 与奇幻角色模式共用 `_ERA_WARD`/`_ENV_DESIGN` 之外的机制为零——两卡间一致性纯靠使用者。
- tests/test_all_modes.py 断言本模式执行非空；三视图锚定路输出占位句。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托 + env 路由）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _ENV_MODES:` 分支；设计指令 `_ENV_DESIGN["奇幻场景"]`
- 数据来源：aggregator/scene_engine.parse_scene
