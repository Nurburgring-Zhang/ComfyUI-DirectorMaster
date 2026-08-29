---
mode_id: characters-ancient-style
node: DirectorMasterCharacters
name: 古风角色
one_liner: 生成古风角色卡：清空服装字段时默认宽袖长袍时代着装，衣冠即身份
applicable: [古装短剧, 古风动画]
intensity: medium
style_tags: [角色卡, 古风, 时代着装]
aliases: [古装角色]
---

## 意图

立古典人物时选它。相对角色设定有两个专属差异：定位文案「古典人物 — 礼仪/称谓/举止符合时代, 衣冠即身份」与时代着装池——服装字段清空时默认「宽袖长袍, 腰封革带, 布料纹理粗粝真实」，而非通用现代服装条目。

## 核心手法

- 走 `_CHARACTER_MODES` 单角色分支，注入古风定位文案。
- 服装补全查 `_ERA_WARD["古风角色"]`，命中即整句进服装行与三视图正面描述；查不到才回落 _WARD_TRAITS（古风在表中，必然命中）。
- 性格/外貌清空走通用 10 条池按场景+模式种子确定性补全；角色名留默认继承场景首位人物。
- 卡内三视图锚定、一致性策略、生成提示词结构与角色设定一致；时代感主要通过服装行与提示词的「风格」段生效。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 古风角色 | 非法值回退 角色设定，时代着装池失效 |
| 角色服装 | （建议清空让时代池生效） | 填现代服装文本会原样进卡——代码不做年代校验，宽袖长袍与牛仔裤可并存 |
| 角色性格 | 沉默寡言, 内敛… | 非空默认值直接进卡；清空走 _PERSONA_TRAITS（无古风专属条目） |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景为空 → 出场场景「未指定」、无道具绑定、种子池退化为纯模式种子 |

## 已知坑

- 时代着装只在服装字段清空时生效：默认值「深蓝色工作服(褪色)…」不清理就直接进卡，古风模式产出现代装束卡。
- 代码不校验服装文本与模式的一致性，用户填什么进什么；防穿帮靠自查。
- 场景解析占位名问题同全体系（parse_scene 词表式提取），姓名行可能写「主角」。
- tests/test_all_modes.py 断言本模式执行非空；六路中「环境圣经/服化道圣经」恒空是路由设计。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() 单角色子支——`costume = _ERA_WARD.get(mode) or _aseed_choice(_WARD_TRAITS, ...)`；定位文案 `_CHAR_ROLE_HINT["古风角色"]`
- 数据来源：_ERA_WARD["古风角色"] 与通用池（节点内置）；aggregator/scene_engine.parse_scene
