---
mode_id: cinematic-tiktok-hyper-cut
node: DirectorMasterCinematic
name: 抖音超快
one_liner: 0.5-1s高密度快剪序列，0.7s/镜的钩子-推进-收束三段节奏
applicable: [抖音短视频, 高密度广告, 嗨爆预告]
intensity: high
style_tags: [抖音超快, 快剪, 跳切, 节拍同步]
aliases: [高密度快剪]
---

## 意图

短视频快剪语法：0.7s/镜均值、10 镜一组循环（0.5s 钩子 → 0.7-0.8s 推进 → 1.0s 收束），视觉密度优先。与 一秒三闪 的差别是没有"组收束"结构，是持续高密度；与 30秒6段（形态模式）的差别是本模式钉死快剪节奏而非按场自动选型。

## 核心手法

- 镜数公式：走分支 C——`PACING_GROUP_FORMULAS["抖音超快"]=(0.7s, 1镜, 30镜上限)`，镜数=ceil(场秒/0.7)，超 30 镜动态加组（硬顶 600）；`PACING_TARGET_AVG_DUR["抖音超快"]=0.7`。
- 十镜模板：0.5s 大特写快推钩子（节拍重音一拍）→ 0.7s 中近景跟拍动作 → 0.5s 特写物件闪 → 0.8s 中景推表情 → 1.0s 全景环绕（音乐高潮）→ 0.6s 近景跳切对话 → … → 1.0s 大特写淡出收束。
- 节拍同步语义：每镜 sound_tpl 绑音乐节拍（重音/动作声+节拍/音乐高潮一拍/音乐渐弱），配合 4 层声音配比输出。
- 时长覆盖：expand_pacing_shots 缩放+缺口归一，总秒数覆盖场戏时长；快剪密度不受目标时长影响。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.25-1（15-60s 短视频） | <0.5 落 1 场梯；镜数=场秒/0.7，60s 约 86 镜——密度由公式给，"10+ 镜"是模板组语义非总量 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="抖音超快" 同键；"🎲 随机" 不生效保持钉死 |
| 运镜风格_多选 | 空 | 填多值（如 "快推, 环绕, 跟拍"）会按镜位弧形轮换且每 3 镜留 1 镜原生——但模板运镜（快推/跳切/环绕）在非保留镜会被弧值覆盖，破坏快剪档型 |
| 剪辑节奏 | 无(默认) | 极快×0.3 乘 0.5s 镜后不再归一 → 时长覆盖失效；跳切语义已在模板 cut，无需下拉 |

## 已知坑

- 0.7s 公式对长场会产生海量镜（5min→428 镜）——本模式按场拆用；动态上限 600 组×1 镜是兜底不是建议。
- 模板钩子文案是通用的（"产品/角色眼睛"）——产品名靠场景 objects 锚定进 focus，空输入落"关键道具"。
- 节奏签名 "0.5-1s×10+ 抖音爆款快剪" 与 一秒三闪/枪战分镜 各自成簇（d1 按 note 分簇），簇内唯一性靠 mode_seed 哈希变体。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["抖音超快"]="抖音超快" → generate_feature_shots 分支 C → PACING_GROUP_FORMULAS["抖音超快"] → expand_pacing_shots → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["抖音超快"]（10 镜序列 + use_cases）；format_templates.MASTER_VIDEO_PRINCIPLES（短视频钩子原则）
