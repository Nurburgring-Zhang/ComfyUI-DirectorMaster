---
mode_id: cinematic-brand-story
node: DirectorMasterCinematic
name: 品牌故事分镜
one_liner: 1-3分钟品牌故事分镜，0.9密度接近基线+60-30-10年代调色块
applicable: [品牌故事片, 企业宣传片, 品牌微电影]
intensity: low
style_tags: [品牌故事, 调性, 60-30-10, 微电影, 舒缓]
aliases: []
---

## 意图

品牌调性的叙事化：0.9 密度（几乎基线节奏）——品牌片要"稳"，镜头时间给足；调性视觉靠年代调色块（60-30-10）与导演锚定。与 广告宣传片 的差别是节奏与时长（1-3min vs 15-60s）。

## 核心手法

- 体量推导：1-3min → 2-3 场；density 0.9 → 分支 D target_avg=9s → 每场 max(基准, 场秒/9) 镜。
- 主导运镜：move="品牌运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 年代调色：场景年代检测 → 【色彩 60-30-10】调色块（复古"低饱和暖褐/灰绿/褪色艳色"、现代"中性灰/环境主色/点缀色"）+ 匹配光影档——品牌质感有系统配色依据。
- 导演锚定：_director_block 注入 600 导演库 12 维档案——"像某导演一样拍品牌片"的知识注入点。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 1-3 | 桶化 ≥20→30；1min 落 ≥0.5 梯 2 场、3min 落 ≥3 梯 3 场——跨梯场数跳变 |
| 核心数据包 | Core 32 字段 JSON | _视觉调性（写实/写意类词）进【视觉语言】行——品牌调性的显式开关；未写落"写实" |
| 节奏风格 | 无(默认)=auto | 钉"固定长镜"可做高端信赖感版本；"🎲 随机" 不生效 |
| 创意输入 | Vibe 节点输出 | 主题/对标 anchors 进 purpose——品牌 Slogan/对标片的语义锚 |

## 已知坑

- 品牌 VI（LOGO 位/品牌色比例）是品牌故事板模板的行——Cinematic 分镜表只有 60-30-10 通用调色块，VI 细节靠上游美术/资产输入。
- 0.9 密度与 婚礼活动（1.0）/情感共鸣（0.8）相邻——三者的区分度只有签名与典型时长，语义靠输入。
- 复古年代检测需要场景文本命中复古词——品牌片常无年代词，落"现代"调色块。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["品牌故事分镜"]（dur_scale 0.9, move "品牌运镜"）→ build_standard_shots(density_scale=0.9) → generate_feature_shots 分支 D；cinematic_studio 视觉语言块（_detect_era → _palette/_light）
- 数据来源：cinematic_studio 调色/光影 era 表；node_base.get_director_profile_text（600 导演库）；SHOT_POOL_BY_DENSITY
