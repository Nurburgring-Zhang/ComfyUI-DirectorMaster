---
mode_id: cinematic-ultra-slow-lyric
node: DirectorMasterCinematic
name: 极慢抒情
one_liner: 1/20极慢自然空镜组，马力克/塔可夫斯基式时间溶解
applicable: [自然空镜, 时间流逝, 梦境段落]
intensity: low
style_tags: [极慢抒情, 马力克, 塔可夫斯基, 空镜, 1/20慢放]
aliases: [超慢速]
---

## 意图

全片最慢的一档：大远景自然空镜（天空/水面/风）按 1/20 速度语义溶解时间，用于章节呼吸、梦境与收束。与 慢镜高光 的差别是景别（大远景 vs 中景）、速度（1/20 vs 1/8）与对象（自然 vs 人物）。

## 核心手法

- 分支 B 慢镜：`MODE_TO_PACING["极慢抒情"]="极慢抒情"` → 分支 B——target_shots=ceil(场秒/15.0)（`PACING_TARGET_AVG_DUR["极慢抒情"]=15.0`），30 镜封顶 + >30s 自动加镜。
- 模板档型：大远景 14mm 固定、平视、叠化；focus_tpl="自然/天空/水面, 1.5s 实际 = 30s 慢放, 1/20 速度, 马力克式"；sound_tpl="风/水/光, 自然音, 旁白进入"。
- 收束场联动：auto 叙事里"收束/尾声/升华"功能场在 STORY_FUNC_PACING 中本就映射 极慢抒情——本模式把该语义扩展到全场戏。
- 张力低档：tension 1-3 场获 漫射光/中性色调/自然材质/日常氛围 档，空镜语义与视觉低张力一致。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 抒情段落（0.5-3min） | 镜数=场秒/15；90s 约 6 镜——密度天然稀疏，短场 <15s 仍保 1 镜 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="极慢抒情" 同键；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _导演风格=塔可夫斯基 → DIRECTOR_OVERRIDES 把每场时长×1.5、张力×0.5（生成期行为）——空镜更慢更平，属预期；未知名落 default 无缩放 |
| 景别偏好 | 无(默认) | 非 ND 覆写大远景——空镜语义崩坏（特写空镜失去"时间溶解"基础），建议保持 ND |

## 已知坑

- 1/20 是 focus 文案语义（1.5s=30s 慢放），dur 字段不变——总时长覆盖不受影响，升格由下游执行。
- focus_tpl 是自然物泛指（天空/水面），具体空镜对象依赖场景 objects/环境锚定；都市场景会产出语义违和的"自然空镜"，需场景描述配合。
- 与 睡前故事/绘本故事 等 density 模式相比，本模式镜数最少（均值 15s/镜），不适合信息密度需求。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["极慢抒情"]="极慢抒情" → generate_feature_shots 分支 B → PACING_TARGET_AVG_DUR["极慢抒情"]=15.0 → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["极慢抒情"]（马力克/塔可夫斯基/阿彼察邦 masters）；STORY_FUNC_PACING 收束类映射；feature_film_engine.DIRECTOR_OVERRIDES
