---
mode_id: characters-protagonist
node: DirectorMasterCharacters
name: 主角角色
one_liner: 生成主角卡：视点人物定位文案，继承场景首位人物，结构与角色设定相同
applicable: [竖屏微短剧, 短视频, 长片]
intensity: medium
style_tags: [角色卡, 主角弧光, 一致性锚定]
aliases: [主角]
---

## 意图

给叙事视点人物立卡时选它。必须说清：本模式与角色设定共享同一分支代码，专属差异只有 `_CHAR_ROLE_HINT` 定位文案「叙事视点人物 — 承载主题弧光, 从缺失走向完成」——没有专用性格池、没有时代着装池，选它不选角色设定不会改变卡结构。

## 核心手法

- 委托 DirectorMasterAsset 进入 `_CHARACTER_MODES` 单角色分支，注入主角定位文案。
- 角色名留默认「主角」且场景解析出人物时继承首位人物（反派的末位规则不适用本模式）。
- 性格/外貌/服装清空时按场景+模式 md5 种子从 10/10/8 条通用池确定性补全（与角色设定同池，无主角专属条目）。
- 卡内固定输出三视图锚定、一致性策略（参考图计数）、生成提示词，尾部追加导演 12 维档案与 6 份项目记忆摘要。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 主角角色 | 非法值回退 角色设定，定位文案退回「主要人物设定」 |
| 角色名 | 主角 | 留默认时被场景首位解析人物替换；与反派模式不同，人物再多也只取首位 |
| 角色性格 | 沉默寡言, 内敛, 用行动表达 | 非空默认值直接进卡；清空才走 _PERSONA_TRAITS 种子池 |
| 视觉风格 | 写实 | 逐字进三视图锚定与生成提示词；填 🎲 随机时从 8 项风格随机抽取，输出不可复现 |

## 已知坑

- 与角色设定代码级同构：除定位文案外全部行为一致，互审时两卡的机制描述差异只有文案指针。
- 场景首位继承可能拿到「主角」占位名——parse_scene 词表式提取对无名场景会产出占位人物，姓名行原地打转。
- 默认性格/外貌/服装非空，不清理字段就没有任何「自动差异化」发生。
- tests/test_all_modes.py 全下拉执行断言覆盖本模式；本模式六路输出中「环境圣经/服化道圣经」恒为空串，属正常路由而非缺陷。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _CHARACTER_MODES:` 单角色子支（else 路径）；定位文案 `_CHAR_ROLE_HINT["主角角色"]`
- 数据来源：_PERSONA_TRAITS / _LOOK_TRAITS / _WARD_TRAITS（节点内置池）；aggregator/scene_engine.parse_scene
