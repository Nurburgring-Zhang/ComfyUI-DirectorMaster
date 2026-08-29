---
mode_id: cinematic-mv-slow-motion
node: DirectorMasterCinematic
name: MV 慢镜
one_liner: 1-5s慢镜+跳切四镜组，画面与音乐节拍咬合，大卫·芬奇式视觉重击
applicable: [MV, 广告, 高光时刻, 视觉重击段落]
intensity: medium
style_tags: [MV慢镜, 大卫芬奇, Mark Romanek, 跳切, 节拍咬合]
aliases: []
---

## 意图

MV 副歌语法：1/4 慢推表情 → 环绕 360° → 大特写跳切 → 全景拉远，4 镜一组卡音乐节拍。与 慢镜高光 的差别是 MV 慢镜带跳切与节拍组结构，与 MV音乐短片分镜（形态模式）的差别是本模式钉死节奏引擎。

## 核心手法

- 组公式：`PACING_GROUP_FORMULAS["MV 慢镜"]=(4.5s, 4镜, 20组上限)` 分支 C——组数=ceil(场秒/4.5)，动态加组硬顶 600；`PACING_TARGET_AVG_DUR["MV 慢镜"]=3.0`。
- 四镜模板：`PACING_STYLES["MV 慢镜"]` —— 特写 85mm 慢推 2.0s（节拍一拍/跳切）→ 中景 50mm 环绕慢 3.0s（节拍二拍）→ 大特写 100mm 固定俯拍 1.5s（跳切）→ 全景 24mm 拉远 4.0s（音乐高潮）。
- 节拍标注：sound_tpl 按镜序写"音乐节拍一拍/二拍/音乐+节拍/音乐高潮"——剪辑点与音乐的对应关系进声音字段。
- 缩放覆盖：expand_pacing_shots 缩放+归一，总秒数覆盖场戏时长。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | MV 段落（0.5-4min） | 镜数=场秒/4.5 均值；3min 约 40 镜 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="MV 慢镜" 同键（下拉显示名含空格）；"🎲 随机" 不生效 |
| 声音输入 | Sound 节点输出 | 环境/拟音 anchors 会拼进部分镜的 sound 字段（phase=1 镜）——与模板节拍文案并存，真实音轨仍需下游 |
| 景别偏好 | 无(默认) | 非 ND 覆写 特写→中景→大特写→全景 的视觉重击弧——建议保持 ND |

## 已知坑

- 与 "MV音乐短片分镜" 是两个实现：本模式=节奏引擎钉死（MODE_TO_PACING），后者=形态模式（density 0.8 + auto 节奏）——同名"MV"前缀易混，选错会得到完全不同的镜头结构。
- 组上限 20→动态 600：长 MV 段产出数百镜，剪辑点语义（节拍 N 拍）随缩放漂移，无法保证真实卡点。
- "慢推/环绕慢" 不在运镜变体池（登记键"推近"/"环绕"）——签名运镜原样保留。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["MV 慢镜"]="MV 慢镜" → generate_feature_shots 分支 C → PACING_GROUP_FORMULAS["MV 慢镜"] → expand_pacing_shots
- 数据来源：pacing_engine.PACING_STYLES["MV 慢镜"]（大卫·芬奇/Mark Romanek/Hype Williams masters + 4 镜序列）
