---
mode_id: cinematic-car-chase-boards
node: DirectorMasterCinematic
name: 车戏分镜
one_liner: 跟拍/车内POV/后拍/仪表盘/航拍五镜组，迈克尔·曼式速度感语法
applicable: [追车, 飙车, 快速通过, 危险段落]
intensity: high
style_tags: [车戏, 迈克尔曼, 跟拍, 速度感, 航拍]
aliases: []
---

## 意图

速度感的标准五镜组：车外跟拍 → 车内 POV → 车外后拍 → 仪表盘特写 → 航拍全景，2-3s 每镜。与 枪战分镜 的差别是速度来源（车 vs 火）、机位组合（跟拍系 vs 手持甩镜系）。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["车戏分镜"]="车戏分镜"`，走分支 C 类型类——`PACING_TARGET_AVG_DUR["车戏分镜"]=2.0`，镜数=ceil(场秒/2)。
- 五镜模板：`PACING_STYLES["车戏分镜"]` —— 中近景 35mm 侧拍跟拍 2.0s（引擎+风+轮胎尖叫）→ 特写 24mm 车内 POV 1.5s（引擎+心跳）→ 全景 24mm 后拍摇镜 2.0s → 特写 50mm 仪表盘固定 1.0s（警报）→ 远景 14mm 航拍俯拍 3.0s（音乐高潮）。
- 缩放覆盖：expand_pacing_shots 按场时长缩放五镜组（mode_seed 偏移起点），上限 30s/镜 + 缺口归一。
- 场景类型联动：focus 含 驾/车/追/引擎 关键词时 format_shot_table 标题判为"追车追击"——类型标签与镜头语义对齐。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 追逐段（0.25-2min） | 镜数=场秒/2；30s 约 15 镜 3 组——组内五镜结构在缩放下保持 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="车戏分镜" 同键；"🎲 随机" 不生效 |
| 景别偏好 | 无(默认) | 非 ND 覆写五镜组的中近景/特写/全景/远景递进——机位语言（车外/车内/仪表盘）仍在 focus，景别弧被抹平 |
| 核心数据包 | Core 32 字段 JSON | 场景无车相关词时产出"语义悬空"的车戏模板（有跟拍文案无车辆语境）——建议场景描述写明车辆与路线 |

## 已知坑

- 车戏模板不校验场景是否真有车——纯室内场景也会产出仪表盘/航拍追车组，语义错位由用户输入兜底。
- "跟拍/手持"类运镜启用直觉风险时触发 R8 跳切标注——追车+跳切是合理组合，但会破坏时长覆盖（R8 只改 cut 不改 dur，实际覆盖破坏来自 R1/R6）。
- 五镜组循环的焦段跨度大（14-50mm）——下游视频模型换镜成本高，可按需用 焦段偏好 统一（覆盖模板递进）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py；aggregator/pro_format.py
- 分支/函数：MODE_TO_PACING["车戏分镜"]="车戏分镜" → generate_feature_shots 分支 C（is_fast_pacing）→ expand_pacing_shots → _make_pacing_shot；pro_format.detect_scene_type_local（追车标题）
- 数据来源：pacing_engine.PACING_STYLES["车戏分镜"]（迈克尔·曼/温丁·雷弗恩/吴宇森 masters + 5 镜序列）
