---
mode_id: characters-future
node: DirectorMasterCharacters
name: 未来角色
one_liner: 生成未来角色卡：清空服装默认无缝功能面料着装，科技外饰保留人性内核
applicable: [科幻短片, 未来题材]
intensity: medium
style_tags: [角色卡, 未来感, 功能面料]
aliases: []
---

## 意图

立未来人物时选它。专属差异：定位文案「未来人物 — 科技外饰保留人性内核, 装备服务于性格」；服装字段清空时默认「无缝剪裁, 哑光功能面料, 隐藏式接口」，替代通用现代服装池。

## 核心手法

- 走 `_CHARACTER_MODES` 单角色分支，注入未来定位文案。
- 服装补全命中 `_ERA_WARD["未来角色"]`，整句进服装行与三视图正面描述，保证提示词层面脱离当代成衣语汇。
- 性格/外貌清空走通用 10 条池——「科技外饰保留人性内核」由定位文案承担，池中人性细节条目（眼下青黑/嘴角抿紧等）与未来外饰形成组合。
- 角色名留默认继承场景首位人物；卡结构与全体系单角色模式一致。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 未来角色 | 非法值回退 角色设定，功能面料池失效 |
| 角色服装 | （建议清空） | 保留默认值则现代工作服文本进卡，未来感丢失 |
| 角色性格 | 沉默寡言, 内敛… | 非空默认直接进卡；清空走 _PERSONA_TRAITS（无未来专属条目） |
| 核心数据包 | 含 _场景描述 的 JSON 包 | 场景空 → 出场场景「未指定」；道具绑定取 _关键道具 首物件或场景首物件 |

## 已知坑

- 着装池只在服装字段清空时生效；与未来道具模式（服化道分支）无任何代码联动——角色装备与道具设计要分别出卡。
- 服装文本无年代校验，用户填什么进什么。
- 场景解析占位名问题同全体系；「30」岁默认值恒进卡。
- tests/test_all_modes.py 断言本模式执行非空；六路输出中角色类只占「角色圣经/三视图锚定/MIP资产卡/完整资产」四路。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() 单角色子支——`_ERA_WARD.get(mode)` 命中路径；定位文案 `_CHAR_ROLE_HINT["未来角色"]`
- 数据来源：_ERA_WARD["未来角色"] 与通用池（节点内置）；aggregator/scene_engine.parse_scene
