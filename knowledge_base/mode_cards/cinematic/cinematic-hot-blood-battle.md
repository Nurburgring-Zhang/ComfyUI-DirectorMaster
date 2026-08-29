---
mode_id: cinematic-hot-blood-battle
node: DirectorMasterCinematic
name: 热血战斗分镜
one_liner: 战斗快切+推拉分镜，名义0.25密度被clamp夹到下限0.3
applicable: [热血战斗集, 王道对波, 动作番]
intensity: high
style_tags: [热血战斗, 快切, 推拉, 速度线, 高张力]
aliases: []
---

## 意图

战斗集的镜头语法：全节点名义最高密度档（0.25）+ "快切+推拉"签名——对波/必杀/觉醒节拍靠密度与张力高位堆出来。与 枪战分镜（钉死节奏引擎）的差别是走 auto 路径、密度驱动。

## 核心手法

- 密度夹取：MODE_PACING dur_scale=0.25 → clamp max(0.3, min(4.0, 0.25))=0.3——实际 target_avg=3s/镜，与小程序剧同档；名义 0.25 是全节点唯一低于下限的档位声明。
- 体量推导：3-24min → 3-8 场；每场镜数=max(基准, 场秒/3)——3min 约 60 镜。
- 高张力联动：战斗场 tension 7-10 → 色彩"高对比红黑"/光影"强光逆光剪影"/材质"冲突材质(铁/血/火)"档拉满；auto 节奏下"对决"→子弹时间、"高潮"→一秒三闪。
- 主导运镜：move="快切+推拉" 覆写 2/3 镜；速度线语义在签名 note（"战斗快切+速度线"）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-24（战斗段-单集） | 密度 0.3 为 clamp 下限——期望更密只能换 pacing 模式（一秒三闪 0.5s/镜）；桶化 ≥20→30 |
| 节奏风格 | 无(默认)=auto | 钉"子弹时间"给必杀瞬间全角度化（密度失效）；"🎲 随机" 不生效 |
| 直觉风险 | 无(默认) | R1 高潮静止会把张力≥8 的战斗镜改固定+1.5x 时长——与热血语义反向；R8 给跟拍/手持镜加跳切标注（合理） |
| 核心数据包 | Core 32 字段 JSON | 战斗语义靠场景功能词（对决/高潮）命中节拍——纯打斗白描无功能词时节奏选型退化为哈希池 |

## 已知坑

- 0.25→0.3 clamp 静默生效——镜数按 0.3 推导，任何按 0.25 的预估都会偏差 20%。
- 高张力档的色彩/材质文案（铁/血/火）在非暴力题材战斗（体育竞技）会违和——语义靠上游美术输入覆盖。
- "快切+推拉"不在 _MOVE_VARIANTS——签名运镜原样保留。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["热血战斗分镜"]（dur_scale 0.25→clamp 0.3, move "快切+推拉"）→ build_standard_shots(density_scale=0.3) → generate_feature_shots 首行 clamp → 分支 D + 四级递进表高张力档
- 数据来源：feature_film_engine 四级递进表 + _shape_tension_curve；STORY_FUNC_PACING（对决→子弹时间、高潮→一秒三闪）
