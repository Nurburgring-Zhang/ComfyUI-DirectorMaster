---
mode_id: cinematic-film-workshop
node: DirectorMasterCinematic
name: 电影工作室
one_liner: 三幕节拍驱动全片长片分镜表，约35场，含契约JSON与导演情感曲线
applicable: [电影长片, 网剧, 精品短剧]
intensity: medium
style_tags: [三幕结构, 长片分镜, 场景锚定, 情感曲线, 分镜JSON]
aliases: []
---

## 意图

默认模式：把核心数据包 + 剧本翻译成 90-120 分钟全片体量的专业分镜表（景别/运镜/焦段/时长/焦点/声音/转场/叙事目的 15+ 列）。与相邻的 段落/关键场次 模式本质差别在体量——本模式按全片时长出全部场次骨架，而非单段落或单场。

## 核心手法

- 结构强制：`CINE_MODE_THEORY["电影工作室"]="三幕剧"` 把故事理论钉死为三幕，节拍表由 `_beats_drama_three_act` 生成，上游传什么理论都会被覆盖；节拍表再经 `_shape_tension_curve` 塑形为波浪上升、约 88% 处顶点、高潮后释放的张力弧。
- 节奏自动选型：pacing_mode="auto"，每场按 story_function 查 `STORY_FUNC_PACING`（建立→固定长镜、中点→一秒三闪、灵魂的黑夜→极慢抒情…），再用导演偏置 `DIRECTOR_PACING_BIAS`（如塔可夫斯基慢镜 1.8）在偏置≥1.3 时替换节奏大类。
- 镜头生成：`generate_feature_shots` 按每场命中分支 A（长镜）/B（慢镜）/C（快闪）/D（默认 7 类池：建立/角色/细节/反应/微距/抒情/转场按 //12、//6、//12、//20 配额分配），dur 归一化保证每场镜头时长覆盖场戏时长。
- 情感与叙事层：`_build_emotion_curve` 按导演名取 5 种导演型张力曲线（王家卫/诺兰/希区柯克/塔可夫斯基/三幕经典）做 ease-in-out 插值 + 心跳微扰；`_build_narrative_structure` 按场密度分配 线/POV/时间线 标签。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 跟随核心包 _成片时长（widget 默认 120 不覆盖 core） | 显式改 widget（≠120）才覆盖 core；之后桶化 ≥110→120 / ≥80→90 / ≥50→60 / ≥20→30，上限 240 实际归 120，镜量按桶出 |
| 核心数据包 | Core 输出的 32 字段 JSON | 非法 JSON → parse_core_pack 返回 {} → scene=""、director="王家卫"、mood="孤独" 空场景兜底跑全流程 |
| 节奏风格 | 无(默认)=auto 按场选型 | 显式选项经 RHYTHM_TO_PACING 强制全场戏该节奏（覆盖自动选型）；"🎲 随机" 在无 options 的 resolve_dropdown 里原样返回、不命中映射 → 保持 auto 不抽奖 |
| 剧本输入 | Script.剧本输出 | 按 "△" 分块取前 6 块首行 → 每镜 purpose 追加 "剧本驱动:"（≤60字）；空则分镜退化为场景描述驱动的空镜+模板镜头 |

## 已知坑

- 节点注释宣称 "~280 镜（120min）" 体量阶梯，实际镜数随每场命中的节奏分支浮动（长镜场约 ceil(场秒/30) 镜、快闪场按组公式、默认场 ≤40 镜封顶）——被测试锚定的不变量是总时长覆盖（tests/ten_rounds.py T10：90min 核心包 dev≤1%），不是镜数。
- 模式名不会把时长改成 90/120 分钟；默认 120 widget 且 core 无 _成片时长 时按 120 出分镜。
- 输出正文以 format_templates.MASTER_VIDEO_PRINCIPLES 前缀开头（tests/test_all_modes.py 断言 startswith 【大师级影视语言原则】）。
- 分镜 JSON 由 storyboard_contract.attach_contract_version 幂等注入 "contract_version":1，validate 发现内部不一致只写 stderr 不失败节点。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/pro_format.py
- 分支/函数：cinematic_studio.build() → CINE_MODE_THEORY["电影工作室"] → build_standard_shots() → generate_feature_scenes（get_beat_map 35 场梯）+ generate_feature_shots（分支 A/B/C/D）
- 数据来源：feature_film_engine.THEORY_BEAT_GENERATORS["three_act"]/_beats_drama_three_act；pacing_engine.STORY_FUNC_PACING + DIRECTOR_PACING_BIAS；feature_film_engine.SHOT_POOL_BY_DENSITY；format_templates.MASTER_VIDEO_PRINCIPLES
