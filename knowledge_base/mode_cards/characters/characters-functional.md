---
mode_id: characters-functional
node: DirectorMasterCharacters
name: 工具人角色
one_liner: 生成功能人物卡：定位关键节点推动情节，用细节让人记住，无专属池
applicable: [竖屏微短剧, 短视频]
intensity: medium
style_tags: [角色卡, 功能人物, 细节锚点]
aliases: [工具人]
---

## 意图

给只在关键节点出场、承担情节推动的功能人物立卡时选它。定位文案「功能人物 — 关键节点出场推动情节, 用一个细节让人记住」是本模式唯一专属差异；分支代码、补全池、继承规则与角色设定完全共用。

## 核心手法

- 委托 DirectorMasterAsset 进入 `_CHARACTER_MODES` 单角色分支 else 路径，注入工具人定位文案。
- 角色名留默认时继承场景解析首位人物；人物网络类需求应改用群像角色模式。
- 性格/外貌/服装清空时按场景+模式 md5 种子从通用池确定性补全——「一个细节让人记住」的落点在外貌池条目（如「手指粗糙, 有一处旧伤」）。
- 卡内固定拼三视图锚定（正面/侧面/背面+3 情绪变体）、一致性策略与生成提示词，供 IP-Adapter 跨镜头锁定。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 工具人角色 | 非法值回退 角色设定 |
| 角色名 | 主角 | 留默认时被场景首位解析人物替换；工具人常无名，建议手填「报摊老人」这类功能名 |
| 角色服装 | 深蓝色工作服(褪色)… | 非空默认值直接进卡；清空走 _WARD_TRAITS，无本模式专属条目 |
| 视觉风格 | 写实 | 逐字进生成提示词；🎲 随机时输出不可复现 |

## 已知坑

- 与角色设定代码级同构：定位文案外无任何专属行为，需要差异化细节必须靠手填字段或换群像模式。
- 场景解析占位名问题同其他单角色模式（parse_scene 词表式提取），姓名行可能写「主角」。
- 角色年龄默认「30」恒进卡——工具人若设定为老人/小孩必须手动改，否则生成提示词永远是「30岁男性」。
- tests/test_all_modes.py 断言本模式执行非空；六路中「环境圣经/服化道圣经」恒空属正常路由。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() `elif mode in _CHARACTER_MODES:` 单角色子支 else 路径；定位文案 `_CHAR_ROLE_HINT["工具人角色"]`
- 数据来源：_PERSONA_TRAITS / _LOOK_TRAITS / _WARD_TRAITS（节点内置池）；aggregator/scene_engine.parse_scene
