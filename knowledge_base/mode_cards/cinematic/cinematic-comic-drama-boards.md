---
mode_id: cinematic-comic-drama-boards
node: DirectorMasterCinematic
name: 漫剧分镜
one_liner: 漫画感分镜，漫剧分格主导运镜+0.8密度快切，输出仍是视频分镜表
applicable: [漫剧, 动态漫画, 条漫改编]
intensity: medium
style_tags: [漫剧, 分格感, 动态漫画, 快切, 静态视觉]
aliases: [漫画分镜]
---

## 意图

静态漫画语言的视频化：0.8 密度 + "漫剧分格"签名运镜——把"分格/视线动线/跳格"语义写进运镜与焦点字段。与 沉浸式戏剧 同密度，差异是视觉语法来源（MASTER_STATIC_PRINCIPLES 的"视线引导=运镜静态化"思路）。

## 核心手法

- 体量推导：3-10min → 3-5 场；density 0.8 → 分支 D target_avg=8s。
- 分格签名：move="漫剧分格" 覆写 2/3 镜（i%3≠2）——"格"的语义由运镜字段承载；每 3 镜 1 镜原生。
- 静态视觉语义：构图 note（构图法则下拉追加）与焦点物件变体承担"格内视觉权重"；翻页/跳格感靠转场池（跳切/叠化档）近似。
- 格节奏：0.8 密度 + 反应/微距镜配额——漫画"大格爆点+小格铺垫"的节奏近似。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-10（单集） | 桶化 ≥20→30；动态漫画单集建议 3-5min |
| 构图法则 | 无(默认) | 漫剧是构图下拉最有价值的消费场景（对称居中=固定/主体放大=推 的静态转译）——非 ND 时逐镜 note 追加"构图: X"；"🎲 随机" 字面量入 note |
| 节奏风格 | 无(默认)=auto | "🎲 随机" 不生效；钉节奏破坏分格铺垫-爆点对比 |
| 核心数据包 | Core 32 字段 JSON | 漫画角色/场景需上游输入——分格内容物全靠锚定 |

## 已知坑

- 输出是视频分镜表（镜头行+子行），不是漫画页布局（页面/格框/对话框结构属于 format_templates 漫画分镜模板，本节点不产出）——"分格"是运镜语义近似。
- 与 沉浸式戏剧/番剧动漫 同密度族（0.8/0.7）——签名 note 分簇（d1）。
- "漫剧分格" 不在 _MOVE_VARIANTS——签名运镜原样保留。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["漫剧分镜"]（dur_scale 0.8, move "漫剧分格"）→ build_standard_shots(density_scale=0.8) → generate_feature_shots 分支 D；build() V13.2 偏好循环（构图法则 → note 追加）
- 数据来源：format_templates.MASTER_STATIC_PRINCIPLES（视线引导=运镜静态化，文案思路）；SHOT_POOL_BY_DENSITY reaction/micro 池
