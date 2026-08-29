---
mode_id: cinematic-bedtime-story
node: DirectorMasterCinematic
name: 睡前故事分镜
one_liner: 睡前故事分镜，舒缓运镜+收束场自动切极慢抒情
applicable: [睡前故事视频, 童话动画, 助眠内容]
intensity: low
style_tags: [睡前故事, 舒缓, 童话, 助眠, 低张力]
aliases: []
---

## 意图

越讲越慢的哄睡结构：1.5 密度 + 舒缓运镜，且收束场（尾声/升华功能）在 auto 节奏下自动切极慢抒情——故事结尾自然进入 15s/镜 的空镜溶解，音量与节奏同步下沉。

## 核心手法

- 减镜推导：density 1.5 → 分支 D target_avg=15s——与 绘本故事 同密度档。
- 收束联动：STORY_FUNC_PACING 的"收束/尾声/升华"→极慢抒情——最后一场自动获得 1/20 慢放语义与大远景空镜档型。
- 主导运镜：move="舒缓运镜" 覆写 2/3 镜（i%3≠2）。
- 低张力曲线：tension 1-3 档贯穿，结尾档位最低（漫射光/中性色/日常材质）——视觉亮度递减模拟困意。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 5-15 | 桶化 ≥20→30；助眠内容建议 10min 内（30min 桶会拖长场结构） |
| 节奏风格 | 无(默认)=auto | 保持 ND 让收束场极慢抒情的自动切换生效；钉死节奏会失去"越讲越慢"结构 |
| 核心数据包 | Core 32 字段 JSON | _情绪基调=平静类词进润色与直觉关键词（"空"类词触发 R4）——助眠语境下直觉建议关闭 |
| 声音输入 | Sound 节点输出 | 环境 anchors（风/虫鸣/壁炉）进 sound 字段——助眠声景的输入源 |

## 已知坑

- "越讲越慢"依赖节拍功能词命中（尾声/收束）——节拍表按理论展开，短时长（5min 3 场）下收束功能可能合并进第三场而非独立存在。
- 与 绘本故事 同密度同分支——签名分簇；语义区分是收束联动（睡前独有节拍倾向）。
- 低张力曲线的 88% 波峰仍会出现——哄睡内容的"伪高潮"张力点比日常系更违和，可用 剧本功能词（尾声）引导末场结构。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["睡前故事分镜"]（dur_scale 1.5, move "舒缓运镜"）→ build_standard_shots(density_scale=1.5, pacing_mode="auto") → 收束场 get_pacing_for_scene("收束/尾声")→极慢抒情 → 分支 B
- 数据来源：pacing_engine.STORY_FUNC_PACING（收束/尾声/升华→极慢抒情）；PACING_STYLES["极慢抒情"]
