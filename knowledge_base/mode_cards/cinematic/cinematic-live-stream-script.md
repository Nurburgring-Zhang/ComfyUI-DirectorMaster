---
mode_id: cinematic-live-stream-script
node: DirectorMasterCinematic
name: 直播脚本分镜
one_liner: 直播脚本分镜，0.8密度连续流切镜，30-60min时长桶化60分钟档
applicable: [直播脚本, 带播流程, 直播预告片]
intensity: medium
style_tags: [直播, 连续流, 带货, 流程切分]
aliases: []
---

## 意图

直播流程的镜头化脚本：0.8 密度 + 直播运镜——直播是连续流，本模式把它切成可执行的镜头段落（开场-讲解-互动-促单-收尾）。与 课程教学 的差别是密度（0.8 vs 1.2）与节奏目标（留人 vs 讲透）。

## 核心手法

- 体量推导：30-60min → build() 时长桶 ≥50→60 → get_beat_map ≥30 梯 t/3.5（60min→17 场封 18）；density 0.8 → 分支 D target_avg=8s。
- 流程切分：场次功能近似直播流程段——建立（开场暖场）、推进（讲解）、高潮（促单/秒杀）、收束（下播预告）；"触发/压力"功能场 → 抖音超快（促单段的快节奏）。
- 主导运镜：move="直播运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 商品锚定：objects（商品名）锚定 focus——讲解/促单镜的对象一致性。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 30-60（直播时长） | 桶化 ≥50→60、≥20→30：设 45 实际按 30 出 8 场——直播分段与名义时长脱钩 |
| 核心数据包 | Core 32 字段 JSON | 商品名不进 objects → focus 落占位——带货镜失去对象 |
| 节奏风格 | 无(默认)=auto | 保持 ND 让促单段快切生效；"🎲 随机" 不生效 |
| 剧本输入 | Script 直播脚本 | 前 6 块驱动 purpose——直播话术块对应流程段 |

## 已知坑

- 直播是实时连续流，分镜表是"可执行脚本"语义——真实直播的时间轴（分钟级话术）比镜头粒度粗，dur 字段仅供拍摄参考。
- 45min 落 ≥20 桶化到 30min——30-50min 之间的直播体量都按 30min 档出，无逐分钟精度。
- 促单"秒杀"语义靠功能场近似——无倒计时/库存等直播专用字段。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["直播脚本分镜"]（dur_scale 0.8, move "直播运镜"）→ build_standard_shots(density_scale=0.8) → 时长桶（≥50→60）→ get_beat_map ≥30 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.get_beat_map 长梯；STORY_FUNC_PACING（触发/压力→抖音超快）；场景 objects 锚定
