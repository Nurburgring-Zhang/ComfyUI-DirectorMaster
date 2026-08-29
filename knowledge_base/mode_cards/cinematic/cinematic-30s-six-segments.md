---
mode_id: cinematic-30s-six-segments
node: DirectorMasterCinematic
name: 30秒6段
one_liner: 30秒短视频分镜（约1场8镜快切），时长须手动设0.5分钟
applicable: [30秒短视频, 单镜头口播, 信息流广告]
intensity: high
style_tags: [30秒, 短视频, 标准快切, 钩子]
aliases: []
---

## 意图

30 秒一条的标准分镜：建立-推进-收束的短结构。与 抖音超快（钉死 0.7s 快剪引擎）的差别是本模式走 auto 节奏 + 0.5 密度的形态路径——节奏仍按场次功能选型，快切感来自密度而非钉死。

## 核心手法

- 体量推导：目标 0.5min → get_beat_map ≥0.5 梯 1 场 → shots 梯 <1min（2s/镜、3-8 镜）→ 每场 8 镜基准；density_scale=0.5 → 分支 D target_avg=5s → target_shots=max(8, 6)=8——实际约 1 场 8 镜。
- 镜型配额：分支 D 7 类池按 //12、//15、//20、//12、//20、//6 配额切 建立/转场/抒情/反应/微距/细节/角色 镜——30s 体量下 建立1+角色3+细节1+反应1+微距1+转场1。
- 主导运镜：MODE_PACING["30秒6段"].move="标准快切" 覆写 2/3 镜（i%3≠2），每 3 镜保留 1 镜引擎原生运镜保多样性。
- 时长覆盖：分支 D 归一化把模板 dur 缩放到 30s 总量——总时长=目标 ±1%（无剪辑节奏/直觉干预时）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5（=30 秒） | 模式不改时长：默认 120 或 core 90min 会出长片体量——"30秒"是创作口径，必须显式设 0.5 |
| 画面模式 | 30秒6段 | "🎲 随机" 会抽到全部 63 模式之一；越界值回退 电影工作室 |
| 节奏风格 | 无(默认)=auto | 显式钉快剪可强化短节奏；"🎲 随机" 不命中映射保持 auto |
| 核心数据包 | Core 32 字段 JSON | 场景信息量决定 8 镜的信息分布——空场景 8 镜全是模板空转 |

## 已知坑

- 名义"6 段"与实际镜数不一致：引擎按 场数梯×每场基准 出约 8 镜（1 场），"6 段"是命名口径不是输出约束——60秒12段/90秒18段 同理（16/24 镜）。
- 30s 目标 <20min → 建立场数 1：开场建立镜配额 shots//12=0 → max(1,…)=1 保底，30s 内仍有 1 个建立镜。
- 与 "抖音超快" 输出形态接近但实现路径不同（density vs pacing）——同输入两者节奏签名不同（d1 分簇），混用时注意口径。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["30秒6段"]（dur_scale 0.5, move "标准快切"）→ build_standard_shots(density_scale=0.5) → get_beat_map ≥0.5 梯 → generate_feature_shots 分支 D（SHOT_POOL_BY_DENSITY 7 类池 + 归一化）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY；pacing_engine.STORY_FUNC_PACING（auto 场节奏）；format_templates.MASTER_VIDEO_PRINCIPLES（前 3 秒钩子原则）
