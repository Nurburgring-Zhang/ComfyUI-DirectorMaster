---
mode_id: cinematic-costume-vertical
node: DirectorMasterCinematic
name: 古风竖屏分镜
one_liner: 古装竖屏分镜，年代检测切换古装地点/道具/角色池与大地色调色
applicable: [古装竖屏短剧, 古风言情, 穿越剧]
intensity: medium
style_tags: [古风, 竖屏, 年代池, 大地色, 古装]
aliases: [古装竖屏分镜]
---

## 意图

古风短剧的竖屏分镜：0.5 密度快切 + "古风运镜"签名，年代系统（地点/道具/角色/调色）整体切到古装档。与 男频/女频竖屏 的差别不在节奏而在年代资产——1998 年不出无人机，古装不出手机。

## 核心手法

- 年代检测：`_detect_era(场景原文)` 识别古装 → 地点池 LOCATION_POOL_古装、默认道具池（一柄旧剑/一封家书/一块玉佩）、补名角色池（故人/旧敌/少侠/掌柜/随从/游侠/老者）。
- 调色与光：_era_v="古装" → 【色彩 60-30-10】"60% 大地色(土黄/赭石) / 30% 青灰(天光) / 10% 朱红(点缀)" + 【光影】"天光/烛火 | 自然光为主 | 中低对比"。
- 体量与运镜：density 0.5 → 分支 D target_avg=5s；move="古风运镜" 覆写 2/3 镜（i%3≠2）。
- 物件锚定：用户道具（玉佩/剑）经 _user_objects 快照强制进首尾场（V16.1 场景锚点），中段场由年代池补充变化。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（单集） | 桶化 ≥20→30；年代检测不随时长变化 |
| 核心数据包 | Core 32 字段 JSON | 场景原文无古装词（宫/朕/侠/朝/阁…类词未命中）→ _detect_era 落"现代" → 全部年代资产切现代池——古风语义仅剩运镜文案 |
| 节奏风格 | 无(默认)=auto | 钉"固定长镜"可做古风文艺向；"🎲 随机" 不生效 |
| 资产输入 | Asset 节点输出 | 道具 anchors 拼进 focus（≤30字）——古装道具与年代池冲突时两者并存（用户道具优先锚定） |

## 已知坑

- 年代由关键词检测决定、无显式开关——写"王爷"但没写"朝/宫"等词时可能漏判；最稳的做法是场景描述显式含古装词。
- 古装对白池 get_dialogue_pool(era) 按年代给台词素材——竖屏短剧体量下台词密度依赖 dial 密度档，模式不强制。
- "古风运镜"不在 _MOVE_VARIANTS——签名运镜原样保留，同簇 D1 差异靠焦点/景别偏移。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["古风竖屏分镜"]（dur_scale 0.5, move "古风运镜"）→ build_standard_shots(density_scale=0.5) → generate_feature_scenes（_detect_era + LOCATION_POOL_古装 + _DEFAULT_OBJS + _COMPANIONS）→ generate_feature_shots 分支 D
- 数据来源：feature_film_engine._detect_era/_filter_objects_by_era/LOCATION_POOL_古装；cinematic_studio 视觉语言 era 调色表
