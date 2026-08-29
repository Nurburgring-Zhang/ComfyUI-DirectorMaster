---
mode_id: cinematic-ad-promo
node: DirectorMasterCinematic
name: 广告宣传片分镜
one_liner: 15-60秒广告分镜，0.6密度广告运镜+建立镜强制开场钩子
applicable: [广告宣传片, 产品广告, 活动宣传]
intensity: high
style_tags: [广告, 宣传片, 钩子, 产品质感, 快节奏]
aliases: []
---

## 意图

短广告的镜头语法：0.6 密度 + 广告运镜签名——前 3 秒钩子由 establishing 池的开场镜承担（branch D 保证每场 ≥1 个建立镜），产品质感靠 detail 池与道具锚定。

## 核心手法

- 体量推导：15-60s → get_beat_map ≥0.5 梯 1-2 场；density 0.6 → 分支 D target_avg=6s → 每场 max(基准, 场秒/6) 镜——30s 约 8 镜。
- 钩子结构：establishing 池 opening=True 排场首（开场 5-8s 沉稳建立的文案原则来自 MASTER_VIDEO_PRINCIPLES，短广告下缩放到秒级）；产品镜由 detail 池（1-5s）+ 物件锚定（产品名进 focus）。
- 主导运镜：move="广告运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 收尾品牌位：转场池（//15 配额）的淡出档型承担"最后 3 秒强化记忆"的收束位。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.25-1（15-60s） | 0.25（15s）→ 1 场梯；不设则按 core 时长出长片级——广告模式对时长最敏感 |
| 核心数据包 | Core 32 字段 JSON | 产品名不进 objects 时 focus 落"关键道具"——产品质感镜失去对象 |
| 节奏风格 | 无(默认)=auto | 钉"抖音超快"可做信息流版本；"🎲 随机" 不生效 |
| 剪辑节奏 | 无(默认) | 快×0.5 破坏 ±1% 时长覆盖——投放平台对 15/30/60s 硬时长敏感，保持 ND |

## 已知坑

- 广告的"卖点/品牌元素"结构（广告故事板模板的 卖点传达/品牌元素 行）不在 Cinematic 分镜表——本模式输出统一镜头表，卖点语义靠 purpose 与道具锚定。
- 15s 档（0.25min）落 ≥0.5 梯的 1 场（int(0.5)=1？int(0.25/0.5)=0 → max(1,0)=1 场）——15-45s 都是 1 场，45-60s 才 2 场，档位跳变在 30-60s 之间。
- 与 品牌故事 的分界：时长与密度（0.6 vs 0.9）——15s-1min 用本模式，1min 以上用品牌故事。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["广告宣传片分镜"]（dur_scale 0.6, move "广告运镜"）→ build_standard_shots(density_scale=0.6) → get_beat_map ≥0.5 梯 → generate_feature_shots 分支 D（establishing 强制 ≥1）
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY establishing/detail/transition 池；format_templates.MASTER_VIDEO_PRINCIPLES（开场沉稳/收尾余韵原则）
