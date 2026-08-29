---
mode_id: cinematic-viral-twist
node: DirectorMasterCinematic
name: 爆火反转分镜
one_liner: 5秒钩子+反转快切分镜，名义0.2密度被夹到下限0.3生效
applicable: [爆款短视频, 神反转剧情号, 投流素材]
intensity: high
style_tags: [爆火反转, 5秒钩子, 快切, 反转, 投流]
aliases: [5秒钩子反转]
---

## 意图

投流爆款结构：前 5 秒钩子（建立镜）+ 中段快切铺垫 + 反转爆点。与 反转小程序分镜 的差别是反转拍不依赖节拍功能词——钩子感由 establishing 池的开场镜与最高可用密度承担。

## 核心手法

- 密度夹取：MODE_PACING dur_scale=0.2 → `generate_feature_shots` 首行 clamp max(0.3, min(4.0, 0.2))=0.3——名义 0.2 被夹到下限，实际 target_avg=3s/镜（与小程序剧三兄弟同档）；这是本模式最重要的实现事实。
- 体量推导：30-60s → 1-2 场 → 每场 max(基准, 场秒/3) 镜——60s 约 20 镜。
- 钩子镜：establishing 池 opening=True 的建立镜排在场首（8-30s 档型缩放到 ~3s），"前 3 秒抓人"由首镜信息密度承担。
- 主导运镜：move="快切" 覆写 2/3 镜；反转爆点若命中"反转"功能场则切一秒三闪（auto 路径）。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 0.5-1 | 不设则按 core 时长；60s 以上密度档不变（3s/镜），时长只加镜 |
| 节奏风格 | 无(默认)=auto | 钉"一秒三闪"全场快闪化（密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 反转内容靠场景/剧本功能词命中——无剧情词时输出是"高密度无反转"的快切表 |
| 剧本输入 | Script 输出 | 前 6 块驱动 purpose；钩子-铺垫-反转建议 3 块结构 |

## 已知坑

- dur_scale 0.2 → 0.3 的 clamp 是静默行为——卡面/注释若宣称 0.2 即失真；实际密度以 clamp 后为准（热血战斗 0.25 同理）。
- 与 创意玩法/搞笑整蛊/Q版 的同族密度问题：0.3 档与小程序三胞胎同构——d1 变体池保指纹唯一，语义区分靠剧本。
- 反转拍位置不保证在片尾——节拍表按比例展开，"神反转在最后 5 秒"需剧本功能词配合。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["爆火反转分镜"]（dur_scale 0.2→clamp 0.3, move "快切"）→ build_standard_shots(density_scale=0.3) → generate_feature_shots 首行 clamp → 分支 D（establishing 池开场钩子）；"反转"功能场 → 分支 C
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY establishing 池；STORY_FUNC_PACING；density clamp 行（generate_feature_shots）
