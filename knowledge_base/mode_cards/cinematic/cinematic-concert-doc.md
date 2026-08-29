---
mode_id: cinematic-concert-doc
node: DirectorMasterCinematic
name: 演唱会纪录
one_liner: 航拍+斯坦尼康跟拍+手部大特写五镜组，怀斯曼式现场感
applicable: [演唱会, 音乐节, 舞台现场]
intensity: medium
style_tags: [演唱会纪录, 怀斯曼, 航拍, 跟拍, 现场感]
aliases: []
---

## 意图

让观众"在现场"：8s 航拍万人场馆 → 6s 斯坦尼康跟拍表演者 → 3s 手部/乐器大特写 → 5s 环绕 → 4s 表情推近，怀斯曼式纪录语法。与 航拍大师 的差别是有完整的"舞台-人-细节"机位链，航拍只是开场一环。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["演唱会纪录"]="演唱会纪录"`，走分支 C 类型类——`PACING_TARGET_AVG_DUR["演唱会纪录"]=8.0`，镜数=ceil(场秒/8)。
- 五镜模板：`PACING_STYLES["演唱会纪录"]` —— 大远景 14mm 航拍俯拍 8.0s（音乐+万人欢呼）→ 中景 50mm 斯坦尼康跟拍 6.0s（现场音乐+呼吸）→ 大特写 100mm 手/弦/鼓 3.0s → 中景 35mm 环绕 5.0s → 特写 85mm 表情推近 4.0s。
- 缩放覆盖：expand_pacing_shots 按场时长缩放五镜组 + 缺口归一，mode_seed 偏移起点；总秒数覆盖目标。
- 声音设计：模板声景（欢呼/乐器/高潮）与 4 层配比叠加——现场感的音量层级写在 sound 字段。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 演出段（1-10min） | 镜数=场秒/8；3min 约 23 镜——五镜组循环铺满 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="演唱会纪录" 同键；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 场景无演出语境时产出语义悬空的舞台模板——建议场景写明场馆/曲目/观众 |
| 剪辑节奏 | 无(默认) | 变速档奇偶 2.0/0.4 交替放大/缩短模板镜 → 现场纪录的匀速感破碎且不再归一 |

## 已知坑

- MODE_PACING 的 dur_scale=4.0 对本模式无效（pacing 模式不叠密度），镜数全由 分支C 公式给。
- "斯坦尼康跟拍" 不在 _MOVE_VARIANTS（登记键是"手持跟拍"等）——同簇 D1 差异靠焦段池（100/85/50/35/14mm 不在池内的原样保留）与景别偏移。
- 手部特写模板（手/弦/鼓）不随场景乐器自适应——民谣/电音/交响都出同一文案，细节靠场景 objects 锚定。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["演唱会纪录"]="演唱会纪录" → generate_feature_shots 分支 C（is_fast_pacing）→ expand_pacing_shots → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["演唱会纪录"]（怀斯曼/马力克/PJ 哈维 masters + 5 镜序列）
