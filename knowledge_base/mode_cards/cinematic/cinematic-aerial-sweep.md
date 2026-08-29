---
mode_id: cinematic-aerial-sweep
node: DirectorMasterCinematic
name: 航拍大师
one_liner: 5-15s航拍升降大景镜头组，建立地理感与史诗感
applicable: [史诗开场, 地理建立, 城市与奇观]
intensity: medium
style_tags: [航拍, 诺兰, 权游, 升降, 大远景]
aliases: []
---

## 意图

用垂直/大范围机位运动建立世界尺度：10s 升降（5m→500m）让观众"飞"过整个场景。与 延时摄影（固定机位压缩时间）的差别是航拍压缩的是"空间距离"。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["航拍大师"]="航拍"`（下拉名"航拍大师"经 RHYTHM_TO_PACING 同映射"航拍"），走分支 C 特殊类——is_fast_pacing 命中（category="特殊"）。
- 镜数推导：`expand_pacing_shots` 按 shots_target 重复模板并缩放到场时长；均值档 `PACING_TARGET_AVG_DUR["航拍大师"]=10.0`（运行时传入键"航拍"恰落同值默认，无错位）。
- 单镜模板：`PACING_STYLES["航拍"]` 大远景 14mm 俯拍/斜拍、航拍升降、dur=10.0、叠化——focus_tpl="从 5m 升到 500m, 10s, 看到整个 {location} 的全貌, 诺兰式"；sound_tpl="风+环境音+音乐渐强, 史诗感"。
- 场景锚定：focus 的 {location} 由场景解析地点填充——V16.1 锚定让显式地点主导开场/收束场，航拍对象与用户输入一致。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 开场/转场段（0.25-2min） | 镜数=场秒/10 均值；30s 约 3 镜——航拍是稀疏镜型，密集需求请换 蒙太奇 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="航拍大师" 同键（注意下拉显示名带"大师"，映射后是"航拍"）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 场景无显式地点 → {location} 落池选地点，航拍对象与用户预期可能脱节；显式地点则锚定主导 |
| 景别偏好 | 无(默认) | 非 ND 覆写大远景——航拍失去尺度基础即失去模式本体 |

## 已知坑

- 航拍升降文案是修辞——引擎不产出高度/轨迹参数；下游消费 14mm/俯拍/10s 字段语义。
- 长焦航拍（用户焦段偏好覆盖）会同时保留"5m→500m"文案——文案与焦段语义冲突时以文案误导，建议航拍保持广角。
- _classify_pacing 把 "航拍" 归入"长镜"大类参与导演偏置——仅 auto 路径相关；本模式钉死节奏不受偏置影响。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["航拍大师"]="航拍" + RHYTHM_TO_PACING["航拍大师"] → generate_feature_scenes 场景锚点（_anchor_loc）→ generate_feature_shots 分支 C → expand_pacing_shots
- 数据来源：pacing_engine.PACING_STYLES["航拍"]（诺兰《盗梦空间》/《权游》/DJI masters）；feature_film_engine 场景锚定逻辑
