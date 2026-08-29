---
mode_id: cinematic-vlog-boards
node: DirectorMasterCinematic
name: Vlog分镜
one_liner: Vlog手持第一视角分镜，0.8密度低干预贴近日常记录感
applicable: [Vlog博主, 日常记录, 旅行记录]
intensity: low
style_tags: [Vlog, 手持, 第一视角, 日常记录, 真实感]
aliases: []
---

## 意图

日常记录的镜头语法：0.8 密度 + 手持 Vlog 签名运镜——不设计感优先，"真实感"优先（手持微晃=混乱/临场，来自 MASTER_VIDEO_PRINCIPLES 的心理语言表）。与 美食探店 的差别是焦点在人与日常而非食物。

## 核心手法

- 体量推导：1-5min → 2-3 场；density 0.8 → 分支 D target_avg=8s → 每场 max(基准, 场秒/8) 镜。
- 主导运镜：move="手持Vlog" 覆写 2/3 镜；每 3 镜 1 镜原生（建立/转场池的稳定机位做呼吸位）。
- 真实感设计：sound_design 的环境%配比偏高（30-59% 由镜号哈希）+ stage_emotion 低张力档——"住在生活里"的声音与情绪基础。
- 手持变体：D1 角度变体池对"平视"做微俯仰 5°（平视·微仰/微俯）——手持的自然晃动感有确定性微变。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1-5 | 不设则按 core 时长；Vlog 长记录建议分段输入（每段一个场景锚点） |
| 节奏风格 | 无(默认)=auto | 钉"游走长镜"可做跟拍长记录（密度失效）；"🎲 随机" 不生效 |
| 运镜风格 | 无(默认) | 非 ND 覆写手持签名——Vlog 真实感即模式本体，改稳定器运镜会变"伪 Vlog" |
| 核心数据包 | Core 32 字段 JSON | 日常场景无强冲突 → 张力曲线低平——曲线平坦是 Vlog 语义的预期行为，非缺陷 |

## 已知坑

- 与 情感共鸣分镜 同 0.8 密度——区分度是运镜签名与焦点对象（d1 分簇）。
- "手持Vlog" 不在 _MOVE_VARIANTS（池内是"手持跟拍/手持/手持微晃"）——签名运镜原样保留。
- 下拉名是"Vlog分镜"（无空格）——与 "MV 慢镜"（含空格）命名风格不一致，逐字匹配时注意。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["Vlog分镜"]（dur_scale 0.8, move "手持Vlog"）→ build_standard_shots(density_scale=0.8) → generate_feature_shots 分支 D；pacing_engine._ANGLE_VARIANTS（平视微俯仰）
- 数据来源：format_templates.MASTER_VIDEO_PRINCIPLES（手持=混乱/临场 心理语言）；sound_design 配比逻辑
