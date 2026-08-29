---
mode_id: cinematic-campus-daily
node: DirectorMasterCinematic
name: 校园日常分镜
one_liner: 校园日常分镜，低张力节拍自动配长镜/对话长镜
applicable: [校园日常番, 青春剧, 轻喜剧单集]
intensity: low
style_tags: [校园日常, 长镜, 低张力, 青春]
aliases: []
---

## 意图

日常系的呼吸感：0.8 密度（低于快切族）+ 日常运镜签名——教室/天台/放课后的时间感靠低张力节拍与长镜倾向承担。与 Vlog 的差别是叙事性（有节拍推进）与场景池（校园语境）。

## 核心手法

- 体量推导：3-24min → 3-8 场；density 0.8 → 分支 D target_avg=8s → 每场 max(基准, 场秒/8) 镜。
- 低张力节拍：日常场 tension 1-3 → 色彩"暖色调(自然)"/光影"顺光自然光"/氛围"平和自然温暖"档；auto 节奏下"建立/平凡世界"功能场 → 固定长镜、"主题/起" → 对话长镜——日常系的长镜倾向有节拍依据。
- 主导运镜：move="日常运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 事件锚定：校园物件（课桌/便当/自行车）经 objects 锚定进 focus——日常物件的"意义变化"由物件变体池承担。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-24 | 桶化 ≥20→30；12-19min 单集同样落 30min 档 |
| 节奏风格 | 无(默认)=auto | 保持 ND 让"建立→固定长镜"的日常长镜倾向生效；钉快切会毁掉日常系呼吸；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 校园物件/地点词进 objects/地点锚定——无具体物件时 focus 落占位 |
| 剧本输入 | Script 输出 | 前 6 块驱动 purpose；日常番的"无事发生"剧本也能出分镜（张力低平是语义） |

## 已知坑

- 日常系与低张力曲线天然匹配，但 _shape_tension_curve 仍会造出 88% 处波峰——纯日常集会出现一个"伪高潮"张力点，属曲线塑形的通用行为。
- 校园地点池无专属表（LOC_POOL 按年代不分校园）——地点细节靠场景描述锚定。
- 与 番剧动漫 同为动漫族但密度/签名不同（0.8 vs 0.7；d1 分簇）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["校园日常分镜"]（dur_scale 0.8, move "日常运镜"）→ build_standard_shots(density_scale=0.8) → generate_feature_shots 分支 D；STORY_FUNC_PACING（建立/平凡世界→固定长镜）
- 数据来源：feature_film_engine 四级递进表低张力档；SHOT_POOL_BY_DENSITY character/lyric 池
