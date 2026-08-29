---
mode_id: cinematic-miniapp-shuang
node: DirectorMasterCinematic
name: 爽剧小程序分镜
one_liner: 爽点密集小程序剧分镜，0.3密度快切，高位张力曲线
applicable: [爽剧小程序, 打脸流短剧, 投流爽点素材]
intensity: high
style_tags: [爽剧, 小程序, 爽点, 快切, 高张力]
aliases: []
---

## 意图

爽点密度优先的小程序剧分镜：与 竖屏小程序剧分镜 同为 0.3 密度快切，差异在张力策略——爽剧的张力曲线整体前移抬高，让每 15-20 秒有一个可投流的爽点镜。

## 核心手法

- 体量推导：1min → 2 场 × 10 镜（density 0.3 → target_avg 3s）；张力曲线 _shape_tension_curve 波浪上升，爽点镜落在波峰。
- 爽点镜型：反应/微距镜配额（//12、//20）+ 高张力档（7-10）的色彩/光影/材质拉满——"打脸瞬间"由 高对比红黑/强逆光/冲突材质 视觉档承担。
- auto 节奏联动："反转/失去"功能场 → 一秒三闪、"对决" → 子弹时间——爽点场自动获得快闪/凝固语法。
- 主导运镜：move="快切" 覆写 2/3 镜（i%3≠2）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1（=60 秒/集） | 0.75min → int 截断 1 场；≥20 → 30min 桶破坏投流体量 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"全场快闪（密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _情绪基调 影响曲线关键词与直觉规则——"孤独"类基调 + 直觉风险触发 R4 不对称（爽剧慎用） |
| 直觉风险 | 无(默认) | R1 高潮静止拖慢爽点节奏且破坏 ±1% 覆盖——投流素材建议保持 ND |

## 已知坑

- 与 竖屏小程序剧分镜/反转小程序分镜 三胞胎：同 density 0.3、同 move"快切"、同分支——区分度只有 mode_seed 驱动的焦点/景别/焦段哈希变体（d1 探针的验证对象）与签名 note。
- "爽点"无引擎概念——波峰位置由通用张力曲线决定，不识别剧情里的打脸点；精确卡点需剧本功能词（反转/对决）进节拍。
- 张力档上限 10 的色彩表（"极致色彩(饱和拉满)"）文案固定——多集连续使用时视觉档复读，靠 mode_seed 变体缓解。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["爽剧小程序分镜"]（dur_scale 0.3, move "快切"）→ build_standard_shots(density_scale=0.3) → get_beat_map ≥0.5 梯 → generate_feature_shots 分支 D + _shape_tension_curve
- 数据来源：feature_film_engine 四级递进表（色彩/光影/材质/氛围 1-10 档）；SHOT_POOL_BY_DENSITY 反应/微距池
