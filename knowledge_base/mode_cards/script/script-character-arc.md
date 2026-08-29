---
mode_id: script-character-arc
node: DirectorMasterScript
name: 角色弧光
one_liner: 单角色弧光卡：Want/Need 矛盾设计+身体习惯+标志性物件承载
applicable: [角色设计前置, 人物小传, 剧本人物层]
intensity: low
style_tags: [Want与Need, 角色弧, 身体习惯, 物件承载]
aliases: [角色弧光设计]
---

## 意图

为场景主角出一张弧光设计卡：外在欲望（Want）与内在需求（Need）互为矛盾，弧光即"追逐 Want 的过程中被迫面对 Need"。与 Characters 节点的角色设定的差别：这里是剧作功能层的弧光（服务叙事），不是外观层人设（服务生成）。

## 核心手法

- `_build_character_template`（script_studio.py:683）：seed=md5(场景_导演_char)，从 6 Want（说出口/被看见/弥补/离开/守住/被原谅）、6 Need（被理解/放下/接受自己/与人连接/承认脆弱/回家）、4 弧（从不敢到做到/从逃避到面对/从孤独到连接/从执念到释然）、5 身体习惯（说话前先停顿/手部小动作掩盖情绪等）各确定性选一。
- 标志性物件=场景解析的第一个道具，标注"承载角色未说出的情感"。
- 尾部【弧光设计】固定原则行：Want 与 Need 互相矛盾——追逐 Want 的过程被迫面对 Need。
- 本模板 strip_decor 后被 `_build_full_screenplay`（:1489）并入所有长片/形态模式输出尾部——是全节点的角色弧公共件。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 角色输入 | 空（可选） | build() 层 `_parse_character_want_need`（:340）按"性格:"行推断第二路 Want/Need 并追加（沉默寡言→不被女儿读懂等映射）；无"性格:"行则该路为空 |
| 情绪基调 | 继承核心包（默认孤独） | 直接进弧光卡"情绪基调"行 |
| 核心数据包 | Core.核心数据包 | 无角色解析时 c1 落"主角"、物件落"标志性物件"占位 |
| 主题深度 | 无(默认)→中 | 本模板不消费深度档；Need 池固定 6 项 |

## 已知坑

- Want/Need/弧/习惯是四池独立选一——组合之间无语义联动校验（"被原谅"+"从孤独到连接"这类错配可能同时出现），需人工审核组合一致性。
- 第二路 Want/Need 推断（:340）的映射表只有 3 条具体规则（沉默寡言/复仇/寻找），其余性格全落"完成外在目标/实现内在成长"通用兜底。
- 模式名"角色弧光"与 Characters 节点输出无数据直连——两边靠用户分别填写，不自动同步。

## 节点映射

- 实现文件：aggregator/script_studio.py
- 分支/函数：TEMPLATE_BUILDERS["角色弧光"]→`_build_character_template()`（:683）；长片并入点 :1489；第二路推断 `_parse_character_want_need`（:340）
- 数据来源：仅节点内置模板池（wants/needs/arcs/habits 四池）+ aggregator/scene_engine.parse_scene
