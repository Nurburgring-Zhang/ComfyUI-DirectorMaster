---
mode_id: characters-scifi
node: DirectorMasterCharacters
name: 科幻角色
one_liner: 生成科幻角色卡：清空服装默认磨损轻量装备着装，科技功能逻辑自洽
applicable: [科幻短片, 机甲题材]
intensity: medium
style_tags: [角色卡, 科幻, 装备逻辑]
aliases: []
---

## 意图

立科幻人物时选它。专属差异：定位文案「科幻人物 — 科技装备逻辑自洽, 功能可解释」；服装字段清空时默认「轻量化装备, 磨损掉漆, 有使用痕迹」——着装池直接写进「使用痕迹」防崭新穿帮。

## 核心手法

- 走 `_CHARACTER_MODES` 单角色分支，注入科幻定位文案。
- 服装补全命中 `_ERA_WARD["科幻角色"]`，整句进服装行与三视图正面描述。
- 性格/外貌清空走通用 10 条池；「功能可解释」无专属字段承载，装备功能描述需手填进外貌/服装文本。
- 角色名留默认继承场景首位人物；卡结构与全体系单角色模式一致（三视图+一致性策略+生成提示词+道具绑定）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 科幻角色 | 非法值回退 角色设定，磨损装备池失效 |
| 角色服装 | （建议清空） | 保留默认值则现代工作服进卡；清空命中「轻量化装备, 磨损掉漆, 有使用痕迹」 |
| 角色性格 | 沉默寡言, 内敛… | 非空默认直接进卡；清空走 _PERSONA_TRAITS（无科幻专属条目） |
| 视觉风格 | 写实 | 科幻题材可配 3D CG；风格仅进提示词，不做可行性校验 |

## 已知坑

- 与科幻场景/未来道具模式无代码联动——角色装备、场景、道具三卡要分别生成再人工对齐世界观。
- 着装池仅在服装字段清空时生效；服装文本无校验。
- 场景解析占位名问题同全体系；年龄默认「30」恒进卡。
- tests/test_all_modes.py 断言本模式执行非空；本模式属于 11 个角色类模式之一，输出落「角色圣经」路。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() 单角色子支——`_ERA_WARD.get(mode)` 命中路径；定位文案 `_CHAR_ROLE_HINT["科幻角色"]`
- 数据来源：_ERA_WARD["科幻角色"] 与通用池（节点内置）；aggregator/scene_engine.parse_scene
