---
mode_id: cinematic-fantasy-adventure
node: DirectorMasterCinematic
name: 奇幻冒险分镜
one_liner: 异世界冒险分镜，0.6密度冒险运镜+年代物件池约束世界观
applicable: [异世界番, 奇幻冒险剧, 游戏改编]
intensity: high
style_tags: [奇幻冒险, 异世界, 冒险运镜, 年代池, 世界观]
aliases: []
---

## 意图

冒险节拍 + 世界观约束：0.6 密度 + 冒险运镜签名——出发/试炼/宝物/归途的冒险弧靠张力曲线，世界观物件（剑/芯片/种子）靠年代道具池与用户资产锚定。

## 核心手法

- 体量推导：3-24min → 3-8 场；density 0.6 → 分支 D target_avg=6s → 每场 max(基准, 场秒/6) 镜。
- 冒险弧：三幕节拍默认——"跨越门槛"（第一情节点）拍 tension 7-10 触发快剪节奏、"获得宝物/灵魂黑夜" 拍 → 极慢抒情；英雄之旅理论需上游传入（理论串含"英雄之旅"才归一 hero_journey）。
- 主导运镜：move="冒险运镜" 覆写 2/3 镜；每 3 镜 1 镜原生。
- 物件池：古装/科幻/复古/现代 默认道具池（旧剑/数据芯片/旧信/手机）+ 用户资产锚定——异世界物件需用户显式给（资产输入），否则落最接近的年代池。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-24 | 桶化 ≥20→30；密度 0.6 在 clamp 内 |
| 节奏风格 | 无(默认)=auto | 保持 ND 让冒险弧的快慢交替生效；"🎲 随机" 不生效 |
| 资产输入 | Asset 节点输出 | 异世界道具（魔杖/晶石）不在任何年代池——必须资产输入显式给，否则 focus 落年代池近似物件 |
| 核心数据包 | Core 32 字段 JSON | _时间年代 检测不识别"异世界"——未命中关键词时落"现代"池，世界观物件与场景可能错位 |

## 已知坑

- 无"奇幻/异世界"年代档——_detect_era 只有 古装/科幻/复古/现代 四档，异世界物件全靠用户输入；漏给则出现"手机+魔法"混搭。
- 英雄之旅节拍不自启用——需要 Script 侧理论传"英雄之旅"，否则走三幕。
- 与 番剧动漫 的区分：密度 0.6 vs 0.7 + 签名（d1 分簇）；冒险感语义靠节拍与物件。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["奇幻冒险分镜"]（dur_scale 0.6, move "冒险运镜"）→ build_standard_shots(density_scale=0.6) → generate_feature_scenes（_DEFAULT_OBJS/_detect_era）→ generate_feature_shots 分支 D
- 数据来源：feature_film_engine._DEFAULT_OBJS 年代道具池；STORY_FUNC_PACING（灵魂的黑夜→极慢抒情）；_normalize_theory（hero_journey 需显式理论）
