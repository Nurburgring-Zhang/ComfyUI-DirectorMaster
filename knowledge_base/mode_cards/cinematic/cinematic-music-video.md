---
mode_id: cinematic-music-video
node: DirectorMasterCinematic
name: MV音乐短片分镜
one_liner: 3-5分钟MV分镜，MV运镜签名+四层声音设计配比承担音画语义
applicable: [MV音乐短片, 歌曲视觉, 演出宣传片]
intensity: medium
style_tags: [MV, 音画同步, 声音设计, 歌词对位]
aliases: []
---

## 意图

完整 MV 的分镜表：0.8 密度 + MV 运镜签名，音画咬合语义由 sound_design 四层配比（环境/拟音/音乐/留白）与 sound 字段的节拍标注承担。与 "MV 慢镜"（节奏引擎模式）的差别是本模式走形态路径——主歌舒缓/副歌爆发的对比靠 auto 节奏按场功能切换。

## 核心手法

- 体量推导：3-5min → 3 场；density 0.8 → 分支 D target_avg=8s → 每场 max(基准, 场秒/8) 镜。
- 主导运镜：move="MV运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 声音层：每镜 sound_design 由镜号哈希给 4 层百分比——副歌场张力高位配"音乐%"上调空间；sound 字段直接携带"音乐高潮一拍"类节拍语义（源自模板池）。
- 副歌联动：副歌功能场命中"高潮"→ 一秒三闪、"牺牲/失去" → 慢镜高光——MV 的情绪段自动获得对应节奏语法。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（歌曲长度） | 桶化 ≥20→30；与歌曲实际时长对齐靠手动设值 |
| 节奏风格 | 无(默认)=auto | 保持 ND 让主歌/副歌的节奏对比生效；钉"MV 慢镜"全场慢镜化；"🎲 随机" 不生效 |
| 声音输入 | Sound 节点输出 | 环境/拟音 anchors 拼进 phase=1 镜 sound 字段（18 字截断）——歌名/乐器的语义锚 |
| 核心数据包 | Core 32 字段 JSON | _对标作品 进 purpose"对标:…"——MV 视觉参考的注入点 |

## 已知坑

- 无真实音轨输入口——卡点/剪辑点语义全靠文案与配比近似，无法按 BPM 对齐。
- 与 "MV 慢镜" 同名前缀易选错：本模式=形态（auto+density 0.8），后者=节奏钉死（组公式）——输出结构完全不同。
- "MV运镜" 不在 _MOVE_VARIANTS——签名运镜原样保留。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/script_studio.py
- 分支/函数：MODE_PACING["MV音乐短片分镜"]（dur_scale 0.8, move "MV运镜"）→ build_standard_shots(density_scale=0.8) → generate_feature_shots 分支 D；_make_pacing_shot sound_design 四层配比；_parse_sound_anchors（声音锚定）
- 数据来源：pacing_engine.STORY_FUNC_PACING（高潮→一秒三闪、牺牲→慢镜高光）；SHOT_POOL_BY_DENSITY
