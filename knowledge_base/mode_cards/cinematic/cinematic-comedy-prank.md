---
mode_id: cinematic-comedy-prank
node: DirectorMasterCinematic
name: 搞笑整蛊分镜
one_liner: 喜剧整蛊短视频分镜，0.5密度快切+反应镜配额承担笑点
applicable: [搞笑整蛊短视频, 喜剧段子, 街头互动]
intensity: high
style_tags: [搞笑, 整蛊, 快切, 反应镜, 喜剧]
aliases: []
---

## 意图

笑点的镜头语法：0.5 密度快切 + 反应镜配额——整蛊的"包袱"落在被整者的反应镜上，节奏负责铺垫速度。与 创意玩法（同 0.5 密度）的差别是笑点结构依赖反应镜而非物件陌生化。

## 核心手法

- 体量推导：30-60s → 1-2 场；density 0.5 → 分支 D target_avg=5s → 每场 8-12 镜。
- 反应镜配额：分支 D 的 reaction 池按 shots//12 分配（0.5-3s 档型）——铺垫镜与反应镜交替是喜剧的"设梗-抖包袱"节奏。
- 主导运镜：move="快切" 覆写 2/3 镜；惊吓/反转瞬间若命中"反转"功能场 → 一秒三闪（auto 路径）。
- 张力节奏：喜剧张力曲线中低幅震荡——笑点由反应镜的 stage_emotion 档跳变（平静→震惊）承担。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-1 | 不设则按 core 时长；密度 0.5 在 clamp 内 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"可强化抖包袱（密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 喜剧理论不自动启用——_normalize_theory 仅在理论串含"喜剧"时切 comedy 节拍，本模式默认三幕剧 |
| 剧本输入 | Script 输出 | 前 6 块驱动 purpose——设梗/抖包袱的语义块对应 |

## 已知坑

- 笑点无引擎概念——"包袱"位置由反应镜配额与功能场近似；精确喜剧节拍需剧本侧 comedy 理论。
- 整蛊语义（谁整谁）全靠场景/剧本输入——引擎不识别整蛊关系，角色分配按 parse_scene 顺序。
- 与 创意玩法/Q版泡面番 同 0.5 密度——签名 note 分簇（d1），语义区分靠输入。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["搞笑整蛊分镜"]（dur_scale 0.5, move "快切"）→ build_standard_shots(density_scale=0.5) → generate_feature_shots 分支 D（reaction 池 //12 配额）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY reaction/detail 池；STORY_FUNC_PACING（反转→一秒三闪）
