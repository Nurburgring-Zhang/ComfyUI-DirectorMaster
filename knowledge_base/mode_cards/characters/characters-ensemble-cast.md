---
mode_id: characters-ensemble-cast
node: DirectorMasterCharacters
name: 群像角色
one_liner: 解析场景人物一次生成最多5张角色卡，首卡用用户输入，其余按种子池补全
applicable: [群像短剧, 多人物短片, 长片]
intensity: high
style_tags: [群像卡, 人物网络, 多主体一致性]
aliases: [群像, 多人物]
---

## 意图

一个场景要同时立住多个人物时选它。与全部单角色模式的本质差别：进入独立子分支，一次产出带人物网络的成组角色卡（每卡独立性格/外貌/服装/关系定位），而不是单卡重复执行。

## 核心手法

- `if mode == "群像角色":` 子分支构建 cast：用户角色名（非默认「主角」时打头）+ 核心场景 parse_scene 解析出的人物去重追加；cast 为空则回退 `[角色名]`，最后截断前 5 人。
- 首卡（i==0）定位「视点人物」，沿用用户填的性格/外貌/服装（非空才用）；第 2 卡起全部按「场景_导演_情绪_模式_项目_人名_序号」md5 种子从三个池独立抽取，同输入同输出。
- 关系定位按种子从 5 条池分配：与主角价值观对照 / 主角的情感软肋 / 推动关键转折 / 见证者·叙述者 / 暗线对手；每卡各拼一条独立生成提示词。
- 一致性策略行换成群像专用文案「每个角色独立参考图锁定, 同框镜头用 IP-Adapter 多主体权重分配」。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 节点模式 | 群像角色 | 填非法值回退 角色设定，丢掉群像子分支 |
| 角色名 | 主角 | 留默认则首卡位置让给场景首位解析人物；填具体人名则该人固定为首卡并继承用户三字段 |
| 角色性格 | 沉默寡言, 内敛, 用行动表达 | 只作用于首卡；第 2 卡起永远走 _PERSONA_TRAITS 种子池，用户值不扩散 |
| 核心数据包 | Core 输出的 JSON 包 | 不接 → cast 只剩用户名或「主角」单元素，人物网络退化为一张卡 |

## 已知坑

- cast[:5] 硬截断：场景解析出第 6 人起静默丢弃，输出无任何提示（代码 `for i, cname in enumerate(cast[:5])`）。
- 人物网络来自 parse_scene 规则提取，可能含「主角/副线」占位名（probe 实证：「深夜厨房, 陈默与苏青对峙」→ ['主角','副线']），真人名不一定进网。
- 想给每个角色都填人工外貌/服装不可行——用户三字段只在 i==0 生效；要逐人精修得用单角色模式分次跑。
- tests/test_all_modes.py 断言本模式执行后六路输出拼接非空，且模式间哈希统计唯一性（同输入不会撞成他模式输出）。

## 节点映射

- 实现文件：aggregator/characters_master.py :: DirectorMasterCharacters.build()（ASSET_MODES 委托段）
- 分支/函数：aggregator/asset_master.py :: DirectorMasterAsset.build() 单角色分支内 `if mode == "群像角色":` 子支（cast 构建 + 5 条关系池）
- 数据来源：_PERSONA_TRAITS / _LOOK_TRAITS / _WARD_TRAITS + 关系池（节点内置）；aggregator/scene_engine.parse_scene
