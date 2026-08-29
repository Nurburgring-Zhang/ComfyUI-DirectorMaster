---
mode_id: cinematic-male-comeback-vertical
node: DirectorMasterCinematic
name: 男频逆袭竖屏分镜
one_liner: 逆袭竖屏分镜，0.35密度爽点快切+高张力节拍
applicable: [男频逆袭短剧, 战神赘婿类, 爽点竖屏]
intensity: high
style_tags: [逆袭, 竖屏, 爽点快切, 高张力, 战神]
aliases: [战神短剧分镜]
---

## 意图

男频爽感的竖屏语法：0.35 密度（接近下限）的极致快切 + 张力曲线高位运行——打脸/扮猪吃虎/身份揭露节拍全靠快切堆密度。与 女频甜宠 的差别是张力档（6-10 高位 vs 3-5 低位）与运镜（快切 vs 推近）。

## 核心手法

- 体量推导：3-5min、density_scale=0.35 → 分支 D target_avg=3.5s → 每场镜数=max(12, 场秒/3.5)——3min 单集约 51 镜，全节点最高密度档之一。
- 主导运镜：move="快切" 覆写 2/3 镜；爽点节拍靠张力 7-10 档（对峙/爆发/决战/燃烧）驱动色彩/光影/材质四级表拉满。
- 爽点节奏联动：auto 节奏下"反转/失去/中点"功能场 → 一秒三闪、"对决/终局" → 子弹时间——打脸瞬间自动获得快闪语法。
- 张力塑形：_shape_tension_curve 波浪上升 + 88% 顶点——"最后一集大高潮"的爽点位置有结构性保证。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（单集） | 密度 0.35 > clamp 下限 0.3，正常生效；桶化 ≥20→30 破坏单集体量 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"可全场快闪化（密度失效、组公式接管）；"🎲 随机" 不生效 |
| 直觉风险 | 无(默认) | R1 高潮静止（张力≥8 时长×1.5 上限 60s）与爽点快切反向——bold 档会明显拖慢集尾高潮；破坏时长覆盖 |
| 核心数据包 | Core 32 字段 JSON | _核心冲突/_导演意图 进 AI 润色上下文——爽点强度描述影响 LLM 轨润色，不影响确定性镜头结构 |

## 已知坑

- 密度 0.35 是 MODE_PACING 名义值，未触 clamp 但已接近——下游若调低 dur_scale 到 <0.3 会被夹到 0.3（热血战斗 0.25 即实例）。
- 高密度 + 30s 上限内海量镜 → 每镜 ~3.5s，快切感由镜数而非单镜时长保证；对时长敏感的投放平台注意总时长=目标 ±1%。
- 爽点词（打脸/金手指）不在任何关键词表——节拍来自三幕张力结构，语义靠剧本输入与 AI 润色承载。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["男频逆袭竖屏分镜"]（dur_scale 0.35, move "快切"）→ build_standard_shots(density_scale=0.35) → get_beat_map ≥3 梯 → generate_feature_shots 分支 D + _shape_tension_curve
- 数据来源：feature_film_engine._shape_tension_curve + 四级递进表；pacing_engine.STORY_FUNC_PACING（反转/对决映射）
