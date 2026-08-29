---
mode_id: cinematic-emotional-resonance
node: DirectorMasterCinematic
name: 情感共鸣分镜
one_liner: 温情共鸣短视频分镜，0.8密度低快切+温情推近主导运镜
applicable: [温情感人短视频, 公益短片, 亲情故事]
intensity: low
style_tags: [情感共鸣, 温情, 推近, 低快切, 亲情]
aliases: []
---

## 意图

慢下来的情绪短片：0.8 密度（接近基线、低于全部快切模式）+ 温情推近运镜——让情绪有时间落地。与 Vlog分镜（同为 0.8）的差别是运镜签名（推近 vs 手持）与情绪目标（共鸣 vs 记录）。

## 核心手法

- 体量推导：30-60s → 1-2 场；density 0.8 → 分支 D target_avg=8s → 每场 max(8, 场秒/8) 镜——60s 约 8-10 镜，全创意族最稀疏。
- 主导运镜：move="温情推近" 覆写 2/3 镜；情绪档靠张力 1-4 档（日常/平静→紧张积累）的低对比色彩/柔光档。
- 低张力曲线：_shape_tension_curve 的波峰在共鸣场（对视/拥抱）而非动作场——曲线形状与快切族相反。
- 亲密反差：场景含 对话/情侣/餐桌 等词 + 启用直觉风险时 R2 把特写改远景——"不消费情感"的克制选项。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-1.5 | 不设则按 core 时长；密度 0.8 在 clamp 内稳定生效 |
| 节奏风格 | 无(默认)=auto | 钉"极慢抒情"可整体空镜化（密度失效、15s/镜）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _情绪基调=温情类词不触发直觉规则——共鸣感来自张力档与推近运镜，基调词主要进 AI 润色 |
| 声音输入 | Sound 节点输出 | 环境/拟音 anchors 进 phase=1 镜的 sound 字段——BGM 语义靠 sound_design 配比（音乐% 由镜号哈希） |

## 已知坑

- "共鸣点"无引擎概念——情绪高点由通用张力曲线与 stage_emotion 档位近似，精确落点需剧本功能词。
- 温情推近与 运镜风格_多选 弧值叠加时非保留镜以模式运镜为准（覆写顺序偏好→模式）。
- 与 Vlog分镜 同密度——签名 note（"温情共鸣推近" vs "Vlog 手持第一视角"）是 d1 分簇依据。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["情感共鸣分镜"]（dur_scale 0.8, move "温情推近"）→ build_standard_shots(density_scale=0.8) → generate_feature_shots 分支 D + _shape_tension_curve
- 数据来源：feature_film_engine 四级递进表低张力档；SHOT_POOL_BY_DENSITY character/reaction 池；intuition_engine R2（启用时）
