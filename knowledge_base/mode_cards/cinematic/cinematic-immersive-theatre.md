---
mode_id: cinematic-immersive-theatre
node: DirectorMasterCinematic
name: 沉浸式戏剧分镜
one_liner: 沉浸式戏剧分镜，360°沉浸运镜+环绕调度承担观演关系
applicable: [沉浸式戏剧, VR内容, 360°演出记录]
intensity: medium
style_tags: [沉浸式, 360°, 环绕调度, VR, 观演关系]
aliases: []
---

## 意图

观演关系消失的内容形态：1.2 密度（轻度减镜）+ 360°沉浸签名运镜——观众在场景中间，镜头语义是"环顾"而非"观看"。与 子弹时间（钉死环绕组）的差别是本模式走密度路径、环绕是签名而非全场钉死。

## 核心手法

- 体量推导：3-15min → 3-5 场；density 1.2 → 分支 D target_avg=12s → 每场镜数按 场秒/12。
- 主导运镜：move="360°沉浸" 覆写 2/3 镜；每 3 镜 1 镜原生（建立/转场呼吸位）。
- 环绕调度倾向：auto 节奏下"建立"场 → 固定长镜（观众站定环顾）、"对决/高潮" → 子弹时间（360° 巡礼）——沉浸段的静止-环绕交替。
- 空间锚定：场景地点/物件锚定进 focus——360° 内容的空间参照物靠 objects 与地点锚点。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-15 | 桶化 ≥20→30；VR 单幕建议 5-10min |
| 节奏风格 | 无(默认)=auto | 钉"子弹时间"全场环绕化（密度失效）；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | _画幅比例=360°/VR 类值仅透传视觉语言行——引擎无等距柱状/立体输出格式 |
| 景别偏好 | 无(默认) | 非 ND 覆写景别——VR 语义对景别敏感（特写在 360° 里语义迥异），建议保持 ND |

## 已知坑

- 无 VR 专用输出格式（无等距投影/双眼视差字段）——"360°"是运镜签名文案，下游需自行适配投影。
- 与 漫剧分镜 同 0.8 密度档相邻但签名不同——沉浸的环绕语义靠 note 与运镜字段。
- 环绕运镜在 _MOVE_VARIANTS 有同族键（环绕/弧形环绕/弧线移动）——D1 变体会换词，沉浸语义不变。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["沉浸式戏剧分镜"]（dur_scale 1.2, move "360°沉浸"）→ build_standard_shots(density_scale=1.2, pacing_mode="auto") → 建立场 分支 A（固定长镜）/高潮场 分支 C（子弹时间）
- 数据来源：pacing_engine.STORY_FUNC_PACING + _MOVE_VARIANTS["环绕"]；场景锚定逻辑
