---
mode_id: characters-character-profile
node: DirectorMasterCharacters
name: 角色设定
one_liner: 从核心数据包继承场景与导演，产出带三视图锚定与生成提示词的单角色卡
applicable: [竖屏微短剧, 短视频, 长片]
intensity: medium
style_tags: [角色卡, 一致性锚定, IP-Adapter]
aliases: []
---

## 意图

需要一张能跨镜头复用的单角色视觉锚定时选它，本节点默认模式。与相邻模式（主角/配角/工具人）同走一个代码分支，本模式差异仅在叙事定位文案「主要人物设定 — 全片视点与情感锚点」，无时代着装池、无专用性格池。

## 核心手法

- characters_master 把 `节点模式=角色设定` 换写成 `资产模式` 委托 DirectorMasterAsset，进入 `_CHARACTER_MODES` 单角色分支，角色卡落到六路输出的「角色圣经」。
- 核心数据包继承：`_场景描述` 交给 scene_engine.parse_scene 提取人物/地点/物件；角色名留默认「主角」时自动改为解析出的首位人物；`_关键道具` 首段变成「道具绑定 — 出场必带」行。
- 性格/外貌/服装字段被手动清空时，按 md5 种子（场景_导演_情绪_模式_项目名）从 10 性格/10 外貌/8 服装条池确定性补全，同输入同输出。
- 卡内固定拼装：三视图锚定（正面/侧面/背面+微笑/凝重/惊讶）、一致性策略（统计参考图数）、生成提示词（姓名+年龄性别+外貌+服装+风格+情绪），末尾追加导演 12 维档案块与 Higgsfield 6 份项目记忆摘要。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 角色设定 | 填下拉外非法值在 build() 入口静默回退为 角色设定，不报错 |
| 核心数据包 | Core 节点输出的 JSON 包 | 不接或非 JSON dict → parse_core_pack 返回空 dict，导演回退「王家卫」、场景/情绪/关键道具全空 |
| 角色名 | 主角 | 留默认且场景解析出人物时被替换为首人物；填了具体名字则逐字使用不再替换 |
| 角色性格 | 沉默寡言, 内敛, 用行动表达 | 默认值非空会直接进卡；只有手动清空才触发 _PERSONA_TRAITS 种子池补全 |
| 角色外貌 | 短发, 瘦削, 颧骨高, 眼窝深, 右手食指有老茧 | 同上，清空后从 _LOOK_TRAITS 按种子取一条 |
| 角色服装 | 深蓝色工作服(褪色), 灰色秋衣, 布鞋 | 清空后本模式无 _ERA_WARD 条目，走 _WARD_TRAITS 通用服装池 |

## 已知坑

- 默认值非空挡住继承：不手动清空性格/外貌/服装，核心数据包与种子池永远不会生效（probe 实证）。
- parse_scene 是规则词表式提取：「深夜厨房, 陈默与苏青对峙」解析出 characters=['主角','副线']，真人名反而提取不到，姓名行会被写成占位名。
- 道具绑定只取第一个物件：_关键道具「凤梨罐头(过期), 旧信」只绑「凤梨罐头」（取第一段 "(" 前文本），第二件起不进绑定行。
- tests/test_all_modes.py 对本节点 43 个下拉选项逐一执行并断言六路输出拼接非空；本模式是回退兜底模式，非法模式名最终都落到它。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（`if mode in ASSET_MODES:` 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _CHARACTER_MODES:` 单角色子支；定位文案 `_CHAR_ROLE_HINT["角色设定"]`
- 数据来源：_PERSONA_TRAITS / _LOOK_TRAITS / _WARD_TRAITS（节点内置池）；aggregator/scene_engine.parse_scene；asset_registry_data.get_six_documents_summary
