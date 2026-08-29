---
mode_id: cinematic-pov-subjective
node: DirectorMasterCinematic
name: POV 主观
one_liner: 角色第一视角手持镜头组，观众的眼睛=角色的眼睛
applicable: [恐怖沉浸, 主观视角段落, 游戏感动作]
intensity: medium
style_tags: [POV, 德帕尔玛, 索德伯格, 手持跟拍, 第一视角]
aliases: [主观视角]
---

## 意图

让观众"成为"角色：1-3s 手持跟拍、POV 角度、角色呼吸心跳做声音主体。与 游走长镜（客观跟拍）的本质差别是视点归属——POV 的镜头就是角色的视网膜。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["POV 主观"]="POV 主观"`，走分支 C 特殊类——`PACING_TARGET_AVG_DUR["POV 主观"]=2.0`，镜数=ceil(场秒/2)。
- 单镜模板：`PACING_STYLES["POV 主观"]` 中近景 35mm 手持跟拍、angle="POV"、dur=2.0、硬切——focus_tpl="{c1} 的视角, 看到 {c2} / 物件 / 环境"；sound_tpl="{c1} 呼吸+心跳+环境, 让观众'住在角色里'"。
- 视角对象链：focus 由场景解析的 c1/c2/objects 填充——看谁、看什么随场景角色与物件池变化；空场景落"主角/关键道具"占位。
- 物件变体池：焦点拼接 6 模板变体（被光线照出细节/静静待在原处…）+ 状态后缀池哈希，主观注视对象逐镜微变。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 主观段落（0.5-3min） | 镜数=场秒/2；60s 约 30 镜——主观镜高频硬切，长场易疲劳，建议段落化 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="POV 主观" 同键；"🎲 随机" 不生效 |
| 叙事线型 | 无(默认)=单线 | 设 "POV切换" 时 arrange/purpose 侧会写 POV 标签（线/POV/时间），与本模式的运镜 POV 是两层——标签层看该下拉，镜头层看本模式 |
| 运镜风格 | 无(默认) | 非 ND 覆写"手持跟拍"——POV 失去手持临场感即失去模式本体，建议保持 ND |

## 已知坑

- "POV" 一词三处出现、互不取代：本模式（运镜/角度层）、叙事线型=POV切换（purpose 标签层）、_build_narrative_structure 的 POV 切换逻辑（由未声明的叙事结构 kwarg 驱动，实际恒"单线"）——想要标签层 POV 必须显式设 叙事线型。
- angle="POV" 是字符串标注，不在 ANGLE 词汇表五档内——下游解析按原样透传，不映射俯仰档。
- 与恐怖类型联动靠场景文本（暗处/异响/警觉 关键词）触发 detect_scene_type_local="恐怖悬疑" 标题，不改变镜头生成。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["POV 主观"]="POV 主观" → generate_feature_shots 分支 C → expand_pacing_shots → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["POV 主观"]（德·帕尔玛/索德伯格/GTA masters）；aggregator/scene_engine.parse_scene 角色/物件解析
