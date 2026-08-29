---
mode_id: cinematic-three-act-boards
node: DirectorMasterCinematic
name: 电影三幕分镜
one_liner: 强制三幕节拍骨架的全片分镜，中点/高潮位置有测试断言兜底
applicable: [电影长片, 类型片, 剧本结构验证]
intensity: medium
style_tags: [三幕结构, 节拍引擎, 张力曲线, 长片分镜]
aliases: []
---

## 意图

结构优先的工作流入口：显式以三幕节拍驱动全片分镜，适用于需要按"建置-对抗-解决"核对拍点的长片项目。与 电影工作室 用同一理论，但语义定位是"我在验证/执行三幕结构"；若上游 Script 传了别的叙事结构，本模式无条件覆盖。

## 核心手法

- 理论钉死：`CINE_MODE_THEORY["电影三幕分镜"]="三幕剧"` → `_normalize_theory("三幕剧")→"three_act"` → `THEORY_BEAT_GENERATORS["three_act"]=_beats_drama_three_act`，35 场梯（120min）上按比例展开三幕拍点。
- 张力塑形：`_shape_tension_curve` 把逐拍固定张力重塑为电影弧——波动上升、≈88% 顶点、高潮后回落；每场 tension_level 再驱动色彩/光影/材质/氛围四级递进表（1-10 档）。
- 节奏混编：auto 节奏按每场功能选型（三幕的"中点"拍 → 一秒三闪、"灵魂的黑夜"拍 → 极慢抒情），导演偏置可整场替换。
- 结构可见性：正文输出【导演情感曲线】逐镜条形图 +【叙事结构】逐镜 线/POV/时间线；JSON 侧 情感曲线/叙事元数据 字段逐镜对齐。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 90-120 | 桶化 ≥110→120 / ≥80→90：设 100 实际按 90 出 25 场梯（t/3.5）；≥150 走 t/4 梯封 50 场 |
| 核心数据包 | Core 32 字段 JSON | _导演风格 未知名 → 曲线/偏置归一 "classic/default"（三幕经典曲线 + 无偏置），不报错 |
| 节奏风格 | 无(默认)=auto | 显式钉死会抹平三幕的节奏对比（建置长镜→高潮快闪的混编是本模式价值）；"🎲 随机" 不生效保持 auto |
| 叙事编排 | 无(默认)=跟随叙事结构 | 设 正叙/倒叙/穿插倒叙/穿插乱叙/循环 时 arrange_scenes 重排银幕序并重编镜号；重排异常 stderr 降级保序 |

## 已知坑

- tests/ten_rounds.py T10 结构硬指标对三幕输出断言：中点 0.35-0.62、高潮 0.72-0.97（经典三幕无独立灵魂黑夜拍）——动节拍表会破坏该回归。
- story_theory 覆盖是单向的：本模式不看上游理论；要按英雄之旅出分镜请用 Script 侧结构而不是在此模式里找参数。
- 节奏签名 note="三幕结构分镜" 与 工作室/段落/关键场次 各不相同（d1 探针按签名分簇），但四者同为 auto+density 1.0+三幕理论，结构差异只在 mode_seed 带来的模板偏移——同输入下正文高度相似是已知同源现象，靠 D1 语法变体保指纹唯一。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：CINE_MODE_THEORY["电影三幕分镜"] → feature_film_engine.THEORY_BEAT_GENERATORS["three_act"]=_beats_drama_three_act → get_beat_map → _shape_tension_curve → generate_feature_shots
- 数据来源：_beats_drama_three_act 拍点表；pacing_engine.STORY_FUNC_PACING/DIRECTOR_PACING_BIAS；cinematic_studio.DIRECTOR_CURVES；format_templates.MASTER_VIDEO_PRINCIPLES
