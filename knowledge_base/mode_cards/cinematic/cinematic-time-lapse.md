---
mode_id: cinematic-time-lapse
node: DirectorMasterCinematic
name: 延时摄影
one_liner: 时间压缩镜头组，0.5-2s压缩小时/天级流逝，季节与城市变化专用
applicable: [时间流逝, 季节变换, 城市变化, 生命循环]
intensity: low
style_tags: [延时摄影, 宫崎骏, 雅克贝汉, 时间压缩]
aliases: []
---

## 意图

把"很久"压进"一秒"：1.5s 延时镜承载一天/一季/一年的流逝，用于章节间的时空跳跃。与 蒙太奇 的差别是延时压缩的是"环境时间"（固定机位看世界变化），蒙太奇压缩的是"事件序列"。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["延时摄影"]="延时摄影"`，走分支 C 特殊类——is_fast_pacing 命中（category="特殊"），`PACING_TARGET_AVG_DUR["延时摄影"]=3.0`。
- 单镜模板：`PACING_STYLES["延时摄影"]` 全景 24mm 固定、叠化、dur=1.5——focus_tpl="0.5s 镜头 = 1 天, 时间被压缩, 宫崎骏/雅克·贝汉式"；sound_tpl="音乐渐强 + 时间音 (钟/光/季节), 旁白可进入"。
- 缩放覆盖：expand_pacing_shots 把模板按 shots_target 重复并缩放到场戏时长（上限 30s）+ 缺口归一——总秒数覆盖目标。
- 时间语义标注：延时只改 focus/sound 文案与模板档型，真实"压缩比"由下游升格/抽帧执行，引擎输出是镜头表语义。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 过场段落（0.25-1min） | 镜数=场秒/3 均值；15s 约 5 镜——压缩段不宜长，长场靠模板重复会稀释"流逝感" |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="延时摄影" 同键；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _时间年代 驱动地点/道具池（古装/科幻/复古/现代）——延时对象（街景/宫殿/舱外星空）随年代池切换，未知名落现代池 |
| 焦段偏好 | 无(默认) | 非 ND 覆写 24mm 广角——延时惯例是广角固定机位，改长焦会变成"定点长焦观察"，需有意为之 |

## 已知坑

- 压缩比文案固定为"0.5s=1天"修辞——不随场景/季节输入自适应；具体流逝对象（花开/人流/天色）靠场景描述 objects 进 focus。
- 与 蒙太奇 同为"特殊/快闪"分支但签名 note 不同（"时间压缩延时" vs "0.5-3s 蒙太奇"），d1 分簇互不干扰。
- 延时模板 cut=叠化：连续延时镜叠化会弱化"时间跳跃"的顿挫，需要顿挫感时用 剪辑节奏=跳切（注意该操作同时破坏时长覆盖）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["延时摄影"]="延时摄影" → generate_feature_shots 分支 C → expand_pacing_shots → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["延时摄影"]（宫崎骏/是枝裕和/雅克·贝汉 masters）；feature_film_engine._detect_era/_filter_objects_by_era 年代池
