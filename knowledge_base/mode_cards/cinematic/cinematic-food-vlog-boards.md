---
mode_id: cinematic-food-vlog-boards
node: DirectorMasterCinematic
name: 美食探店分镜
one_liner: 美食探店分镜，菜品道具锚定画面焦点+美食特写主导运镜
applicable: [美食探店, 吃播, 餐厅宣传]
intensity: medium
style_tags: [美食探店, 特写, 道具锚定, 质感]
aliases: []
---

## 意图

食物的镜头语法：0.7 密度 + "美食特写"主导运镜——菜品的质感细节（热气/酱汁/拉丝）靠 detail 池与物件锚定进画面焦点。与 Vlog分镜 的差别是焦点对象（食物 vs 博主日常）与特写密度。

## 核心手法

- 体量推导：0.5-2min → 1-3 场；density 0.7 → 分支 D target_avg=7s → 每场 max(基准, 场秒/7) 镜。
- 道具锚定：场景 objects（菜名）经 _user_objects 快照锚定首尾场；detail 池（1-5s 档型）按 //6 配额给食物特写镜；focus 拼接物件变体（"被光线照出细节"/"使用过的痕迹"）制造食欲质感。
- 主导运镜：move="美食特写" 覆写 2/3 镜；推近语义与 detail 池的特写档型对齐。
- 资产增强：资产输入的 道具/环境 anchors 拼进 focus（≤30字）与 stage_atmosphere——菜品名+环境氛围双锚定。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-2 | 不设则按 core 时长；探店多场景建议按场景分段输入（每场一个地点锚定） |
| 核心数据包 | Core 32 字段 JSON | 菜名不进 objects 时落"关键道具"占位——食物特写失去对象，模板文案泛化 |
| 节奏风格 | 无(默认)=auto | 钉"蒙太奇"可做菜品串烧；"🎲 随机" 不生效 |
| 资产输入 | Asset 节点输出 | 道具锚定进 focus 有 30 字截断——长菜名+修饰词会被截，保留核心词 |

## 已知坑

- 食物质感（热气/拉丝）不在模板——质感语义靠物件变体池的泛化文案+上游美术输入的材质锚定。
- 多菜品探店：objects 列表只有首物件进 focus 中心，次要物件靠 obj_str 拼接（"菜A、菜B"）——变体池只对首物件生效。
- 与 Vlog分镜 签名分簇（d1）——同密度不同运镜与焦点结构。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/script_studio.py
- 分支/函数：MODE_PACING["美食探店分镜"]（dur_scale 0.7, move "美食特写"）→ build_standard_shots(density_scale=0.7) → generate_feature_scenes（_user_objects 场景锚点）→ generate_feature_shots 分支 D（detail 池 //6）；_parse_asset_anchors（道具/环境锚定）
- 数据来源：feature_film_engine 场景锚点逻辑 + 物件变体池；SHOT_POOL_BY_DENSITY detail 池
