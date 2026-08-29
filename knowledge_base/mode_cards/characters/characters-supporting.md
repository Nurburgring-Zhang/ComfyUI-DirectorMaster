---
mode_id: characters-supporting
node: DirectorMasterCharacters
name: 配角角色
one_liner: 生成配角卡：情感对照定位文案，机制与角色设定完全同分支无专属池
applicable: [竖屏微短剧, 短视频]
intensity: medium
style_tags: [角色卡, 配角功能, 情感对照]
aliases: [配角]
---

## 意图

给副线人物立卡时选它。诚实口径：本模式与角色设定/主角角色同走单角色分支，专属差异仅为定位文案「副线人物 — 侧面烘托主角, 承担情感对照功能」；无专用性格池、无时代着装池、无独立继承规则。

## 核心手法

- 委托 DirectorMasterAsset 进入 `_CHARACTER_MODES` 单角色分支 else 路径，注入配角定位文案。
- 角色名留默认时继承场景解析首位人物（末位规则是反派模式独有）。
- 性格/外貌/服装清空时按场景+模式种子从通用池确定性补全；同场景下配角与主角模式种子仅差模式名一段，补全结果因此不同。
- 卡结构与其他单角色模式一致：三视图锚定 + 一致性策略 + 生成提示词 + 道具绑定 + 导演档案块。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 配角角色 | 非法值回退 角色设定，文案退回「主要人物设定」 |
| 角色名 | 主角 | 留默认时被场景首位解析人物替换；填具体名则逐字使用 |
| 角色外貌 | 短发, 瘦削, 颧骨高… | 非空默认值直接进卡；清空后从 _LOOK_TRAITS 按种子取条 |
| 核心数据包 | Core 输出的 JSON 包 | 场景为空 → 出场场景行写「未指定」，无道具绑定行 |

## 已知坑

- 与角色设定代码级同构，别在互审中期待本卡出现独立机制——差异只在 `_CHAR_ROLE_HINT` 一行。
- 场景解析可能产出「主角/副线」占位名（probe 实证），配角姓名行会照抄；要真人名需在角色名手填。
- 道具绑定只绑第一物件；配角「随身信物」语义要靠手写进服装/外貌字段补。
- tests/test_all_modes.py 断言本模式六路输出拼接非空；「环境圣经/服化道圣经」两路为空串是路由设计。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _CHARACTER_MODES:` 单角色子支 else 路径；定位文案 `_CHAR_ROLE_HINT["配角角色"]`
- 数据来源：_PERSONA_TRAITS / _LOOK_TRAITS / _WARD_TRAITS（节点内置池）；aggregator/scene_engine.parse_scene
