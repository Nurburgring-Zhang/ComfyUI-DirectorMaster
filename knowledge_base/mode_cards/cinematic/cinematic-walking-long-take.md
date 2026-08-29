---
mode_id: cinematic-walking-long-take
node: DirectorMasterCinematic
name: 游走长镜
one_liner: ≤60s斯坦尼康跟拍长镜组，一镜穿越多空间调度群戏
applicable: [群戏调度, 空间穿越, 技术展示段落]
intensity: low
style_tags: [游走长镜, 贝拉塔尔, 拉赞纽斯, 斯坦尼康, 跟拍]
aliases: []
---

## 意图

摄影机跟着人物走完整事件：60s 封顶的跟拍长镜组（叠化衔接），空间随人物流动。与 长镜大师（固定机位）的差别是机位运动，与 一镜到底 的差别是有切点（≤60s）。

## 核心手法

- 分支 A：`MODE_TO_PACING["游走长镜"]="游走长镜"` —— per_shot_max=60.0（V14.3 分化：游走 60s 介于固定/对话 30s 与一镜到底整场之间），base_shots=ceil(场秒/60)，镜间 cut=叠化。
- 模板档型：`PACING_STYLES["游走长镜"]` 中景 35mm 环绕角度、move="斯坦尼康跟拍 (60-180s)"、dur=120（模板语义）——focus_tpl="从 {location} 起点 跟拍 {c1} 走/跑/做, 120s 一镜穿越多个空间, 调度 5-15 个角色"。
- 时间切片：按镜序加"开始/中段/收束切片"提示（物件先于人物出现→人物进入动作被稀释→人物没动物件被光移动），长镜组内部有微观节拍。
- 实际 dur：分支 A 用 场时长/镜数 覆写模板 dur——60s 场=1 镜 60s，180s 场=3 镜各 60s 叠化。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 段落级（1-5min） | 镜数=场秒/60；3min→3 镜——镜数天然稀疏，密集信息请换分支 D 模式 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="游走长镜" 同键；"🎲 随机" 不生效 |
| 运镜风格_多选 | 空 | 填弧值会在非保留镜覆盖"斯坦尼康跟拍"——签名运镜不在变体池但会被用户覆写，跟拍身份消失 |
| 核心数据包 | Core 32 字段 JSON | 场景角色数决定"调度 5-15 个角色"文案的真实性——仅 c1/c2/c3 三人解析时文案夸大，属模板修辞 |

## 已知坑

- 模板 dur=120 与分支 A 实际 dur（≤60s）不一致是已知分化（V14.3 红队P1 修复单镜上限后模板文案未同步）——以实际 dur 字段为准。
- "斯坦尼康跟拍 (60-180s)" 带时长后缀的运镜串不参与 _MOVE_VARIANTS（键不在池内）——同簇 D1 差异靠焦点/景别偏移。
- 60s 上限意味着 >60s 的连续调度需求会被切分叠化——需要绝对无切用 一镜到底。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["游走长镜"]="游走长镜" → generate_feature_shots 分支 A（per_shot_max=60.0）→ _make_pacing_shot（时间切片提示分支）
- 数据来源：pacing_engine.PACING_STYLES["游走长镜"]（贝拉·塔尔/拉赞纽斯/陈可辛 masters）
