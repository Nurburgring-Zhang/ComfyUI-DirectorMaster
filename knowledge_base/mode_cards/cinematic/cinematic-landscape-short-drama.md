---
mode_id: cinematic-landscape-short-drama
node: DirectorMasterCinematic
name: 横屏微短剧分镜
one_liner: 横屏短剧分镜，0.5密度快切，体量随集长（5-15min）桶化
applicable: [横屏微短剧, 网剧单集, 精品短剧]
intensity: medium
style_tags: [微短剧, 横屏, 快切, 单集体量]
aliases: []
---

## 意图

横屏微短剧的单集分镜：5-15 分钟/集，快切节奏但保留横屏叙事空间（双人/群像构图不被竖屏裁切约束）。与 竖屏微短剧分镜 的差别是密度（0.5 vs 0.4）与构图自由度；与 电影段落分镜 的差别是短剧的钩子-反转节拍优先于电影节拍。

## 核心手法

- 体量推导：5min → get_beat_map ≥3 梯 3 场；15min → ≥15 梯 5 场；density_scale=0.5 → 分支 D target_avg=5s → 每场镜数=max(基准, 场秒/5)。
- 主导运镜：move="快切" 覆写 2/3 镜；每 3 镜 1 镜原生引擎运镜。
- 钩子节拍：auto 节奏按场功能选型——开场场命中"建立"→固定长镜（横屏建立镜），冲突场命中"触发/逼近"→抖音超快，反转拍命中"反转"→一秒三闪。
- 画幅透传：横屏不是引擎概念——画幅比例来自核心包 _画幅比例，进【视觉语言】块与 JSON；镜头生成本身画幅无关。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 5-15（单集） | 桶化 ≥20→30：设 18 实际按 30min 梯出 8-10 场；不设则按 core 时长 |
| 核心数据包 | Core 32 字段 JSON | _画幅比例 缺失 → 【视觉语言】写"比例按核心数据包"占位，下游自行决定 16:9 |
| 节奏风格 | 无(默认)=auto | 钉"固定长镜"可做文艺向单集；"🎲 随机" 不生效 |
| 剧本输入 | Script 短剧剧本 | 前 6 块驱动 purpose；单集剧本块数超过 6 后无驱动标注 |

## 已知坑

- "横屏"只影响用户心智与画幅字段，引擎无横竖屏分支——竖屏裁切风险由下游视频模型承担。
- 5min 恰落 ≥3 梯（t/1.5=3 场）；8min → 5 场（≥3 梯 t/1.5=5）；跨 ≥15 梯（t/3）时场数公式切换——15min 边界两侧场数推导不同源。
- 与 竖屏微短剧分镜 同签名簇吗——不是：签名 note 分别为"5-15min/集 横屏快切"/"3-5min/集 快切钩子"，d1 分簇各自唯一。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["横屏微短剧分镜"]（dur_scale 0.5, move "快切"）→ build_standard_shots(density_scale=0.5) → get_beat_map ≥3/≥15 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY；pacing_engine.STORY_FUNC_PACING；core 包 _画幅比例（视觉语言块透传）
