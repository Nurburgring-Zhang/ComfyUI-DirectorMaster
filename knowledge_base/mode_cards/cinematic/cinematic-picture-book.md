---
mode_id: cinematic-picture-book
node: DirectorMasterCinematic
name: 绘本故事分镜
one_liner: 5-10分钟绘本故事分镜，1.5密度缓推少镜（约15s/镜）
applicable: [绘本故事视频, 儿童图文动画, 亲子内容]
intensity: low
style_tags: [绘本, 缓推, 少镜慢节奏, 图文, 亲子]
aliases: []
---

## 意图

绘本翻页感的视频化：1.5 密度（>1 是全节点少数"减镜"档）——平均 15s/镜的缓推长镜组，一镜一页的阅读节奏。与 睡前故事 的差别是缓推签名与图文语义；与 儿童教育 的差别是叙事而非教学。

## 核心手法

- 减镜推导：density_scale=1.5 → 分支 D target_avg=15s → target_shots=max(基准, 场秒/15)/1.5 方向减镜——5-10min 输出明显少于基线的镜量；clamp 上限 4.0 内稳定。
- 主导运镜：move="绘本缓推" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 翻页语义：转场池（叠化/淡入淡出档）承担"翻页"感；画面焦点由场景物件锚定（绘本角色/道具）。
- 低张力全档：tension 1-3 的自然光/暖色/日常材质档贯穿——绘本视觉的柔和基础。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 5-10 | 桶化 ≥20→30；density>1 减镜方向——期望更多镜需换 0.x 档模式 |
| 节奏风格 | 无(默认)=auto | 钉"固定长镜"可做单页长凝视（密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 绘本角色/物件需进场景描述或角色/资产输入——空输入落占位 |
| 剪辑节奏 | 无(默认) | 任何倍率档破坏时长覆盖；绘本的缓节奏已由密度承担 |

## 已知坑

- 输出仍是视频分镜表（镜头语法）——静态绘本的分格/翻页布局是 format_templates 漫画分镜模板的事，本模式用缓推+叠化近似翻页感。
- 1.5 密度对 shots 基准的下限保护：每场基准镜数（8-12）先于密度公式——短场不会因密度被减到 0 镜。
- 与 睡前故事 同 1.5 密度——签名 note（"5-10min 图文缓推" vs "睡前舒缓运镜"）分簇。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["绘本故事分镜"]（dur_scale 1.5, move "绘本缓推"）→ build_standard_shots(density_scale=1.5) → generate_feature_shots 分支 D（transition 池翻页转场）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY transition/lyric 池；四级递进表低张力档
