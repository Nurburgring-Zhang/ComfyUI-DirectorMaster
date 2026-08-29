---
mode_id: cinematic-performance-block
node: DirectorMasterCinematic
name: 表演块
one_liner: 表演细节分镜，不覆写运镜，靠actor_note表演指导池与微表情焦点
applicable: [表演指导, 演员调度, 表演细节精修]
intensity: low
style_tags: [表演块, actor_note, 微表情, 表演指导, 调度]
aliases: []
---

## 意图

把"怎么演"写进分镜：1.0 基线密度且 move=None（不覆写任何运镜）——本模式的独特性全在表演层：actor_note 池 8 条表演指导（"眼眶湿, 但不要落泪"/"屏住呼吸 3 秒, 然后慢慢呼出"）逐镜哈希分配，focus 拼接微表情级细节。

## 核心手法

- 零运镜干预：MODE_PACING["表演块"] 的 move=None → 跳过主导运镜覆写——镜头语法完全由引擎节奏分支决定，模式只加表演层。
- 表演指导池：`_make_pacing_shot`/`_make_shot` 的 actor_pool 8 条按镜号+mode_seed 哈希注入 actor_note 字段——每镜一条可执行的表演指令。
- 微表情焦点：focus 拼接状态后缀池（"呼吸比动作先泄露"/"眼神比身体先到"）与物件变体——表演的"看不见的戏"写进画面焦点。
- 情绪档联动：stage_emotion 按张力档给情绪基调（"微妙变化/暗流"→"爆发/燃烧"）——表演强度随节拍曲线。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | Core 32 字段 JSON | 角色 anchors（性格/外貌）进 focus/stage_emotion（phase=2 镜）——表演指导与角色设定的绑定来源 |
| 角色输入 | Characters 输出 | 外貌/动作 anchors 决定 phase=2 镜的 focus 前缀 "[角色名] 外貌"——表演块最依赖的上游 |
| 节奏风格 | 无(默认)=auto | 运镜交还引擎；钉节奏不影响表演层注入；"🎲 随机" 不生效 |
| 目标时长(分钟) | 段落级 | 表演层与体量无关——任何时长都逐镜注入 |

## 已知坑

- 与 电影工作室/选片决策 同为 density 1.0 + move None——三者结构差异只有 mode_seed 变体与签名 note；表演块的辨识度在 actor_note 字段（JSON 侧不导出 actor_note，只在分镜表深字段）——下游消费需解析正文。
- actor_note 池是全局 8 条通用指导（不按角色/场景细分）——特定表演需求靠角色输入与 AI 润色补充。
- 微表情语义在 focus 文案——视频模型对"呼吸比动作先泄露"类指令的执行度不可控。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["表演块"]（dur_scale 1.0, move None → 跳过覆写）→ build_standard_shots → generate_feature_shots 分支 A/B/C/D → _make_pacing_shot/_make_shot 的 actor_pool（8 条）与状态后缀池
- 数据来源：pacing_engine.actor_pool/状态后缀池；script_studio._parse_char_anchors；_integrate_6d_into_shot_fields（角色锚定 phase=2）
