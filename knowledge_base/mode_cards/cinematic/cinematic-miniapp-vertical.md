---
mode_id: cinematic-miniapp-vertical
node: DirectorMasterCinematic
name: 竖屏小程序剧分镜
one_liner: 1分钟小程序剧分镜，0.3密度（下限档）极快钩子
applicable: [小程序短剧, 1分钟付费短剧, 投流素材]
intensity: high
style_tags: [小程序剧, 竖屏, 极快钩子, 付费卡点]
aliases: [小程序短剧]
---

## 意图

1 分钟一集的付费短剧分镜：0.3 密度（密度公式下限档）的极快钩子节奏——每秒都要留人，卡点付费。与 竖屏微短剧 的差别是体量（2 场 vs 3 场）与密度（0.3 vs 0.4）。

## 核心手法

- 体量推导：1min → get_beat_map ≥0.5 梯 2 场 → 每场 shots 基准 8（<1min 梯 2s/镜）→ density 0.3 → 分支 D target_avg=3s → 每场 max(8, 10)=10 镜，合计约 20 镜。
- 密度下限：0.3 恰为 generate_feature_shots 的 clamp 下限——再低的 dur_scale 也会被夹回 0.3，本模式是全节点快切密度的地板。
- 主导运镜：move="快切" 覆写 2/3 镜；开场建立镜 8-30s 让观众进世界后立刻进高频反应/微距镜。
- 付费卡点：张力曲线把高点推后——集尾高张力镜即付费卡点素材；JSON 侧 情感强度 字段可做卡点依据。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1（=60 秒） | 不设则按 core 时长；设 0.5 落 1 场梯 → 结构退化单场 |
| 节奏风格 | 无(默认)=auto | 钉"抖音超快"时组公式接管镜数（0.7s/镜）——密度失效但快切更极致；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _目标受众 进 AI 润色上下文——付费人群语义影响润色，不影响镜头结构 |
| 剪辑节奏 | 无(默认) | 任何倍率档都会破坏 ±1% 时长覆盖（投流素材对时长敏感）——保持 ND |

## 已知坑

- 1min 恰落 ≥0.5 梯（t/0.5=2 场）；0.75min → max(1, int(1.5))=1 场（int 截断）——集长在 0.5-1min 之间时场数按 int 截断跳变。
- 与 爽剧小程序/反转小程序 同密度同运镜签名——三胞胎差异只有 mode_seed 语法变体与签名 note，d1 靠变体池保指纹唯一。
- 付费卡点无专用字段——"卡点"语义全靠张力曲线与情感强度推断，引擎不输出付费标记。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["竖屏小程序剧分镜"]（dur_scale 0.3, move "快切"）→ build_standard_shots(density_scale=0.3) → get_beat_map ≥0.5 梯 → generate_feature_shots 分支 D（clamp 下限验证点）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY + _shape_tension_curve；density clamp（generate_feature_shots 首行 max(0.3, min(4.0, …))）
