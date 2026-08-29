---
mode_id: cinematic-female-sweet-vertical
node: DirectorMasterCinematic
name: 女频甜宠竖屏分镜
one_liner: 甜宠竖屏分镜，推近特写主导运镜+亲密张力曲线
applicable: [女频甜宠短剧, 言情竖屏, 情感短剧]
intensity: medium
style_tags: [甜宠, 竖屏, 推近特写, 言情, 亲密感]
aliases: [甜宠剧分镜]
---

## 意图

女频甜宠的竖屏语法：0.4 密度 + "推近特写"主导运镜——心动/吃醋/对视全靠怼脸特写。与 男频逆袭 的差别是张力曲线更柔和（亲密大于冲突）、运镜是推近而非快切。

## 核心手法

- 体量推导：同 竖屏微短剧分镜（3-5min、density 0.4、3 场）——差异在运镜签名与情绪档。
- 主导运镜：move="推近特写" 覆写 2/3 镜；甜蜜/心动节拍靠 stage_emotion 张力 3-5 档（微妙变化/暗流/紧张积累）而非高张力档。
- 亲密场景识别：场景文本含 对话/对坐/两人/情侣/餐桌/卧室 等关键词时，启用直觉风险会触发 R2 亲密远景（特写→远景 24mm）——甜宠的"克制镜头"反差选项。
- 情感曲线：导演名归一后取曲线模板——甜宠配 王家卫 型（7-9 高位震荡、中段下沉）比诺兰型（持续上升）更贴言情呼吸。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 3-5（单集） | 桶化 ≥20→30；密度 0.4 只在 auto 路径生效（显式节奏风格钉死时失效） |
| 核心数据包 | Core 32 字段 JSON | _情绪基调=甜/暖 类不在直觉引擎关键词表——R2 只认 对话/情侣/餐桌 等场景词，基调词不触发 |
| 直觉风险 | 无(默认) | medium 档 30% 触发率：R2 把心动特写改远景是美学反差（侯孝贤式拒绝消费情感），与甜宠预期冲突时保持 ND |
| 叙事线型 | 无(默认)=单线 | 甜宠的 A/B 线（主 CP/副 CP）需设 双线并行 才写 B 线标签；线标签只进 purpose/JSON，不改镜头结构 |

## 已知坑

- "推近特写"覆写发生在偏好之后——运镜风格_多选 的弧值在非保留镜被覆盖。
- 甜宠节拍不走 romance 理论生成器（story_theory 默认三幕剧；"爱情"关键词归一 romance 只在理论串含该词时）——心动拍位置靠张力曲线而非专属节拍表。
- 亲密关键词表（_INTIMATE_KEYWORDS）不含"甜宠/心动"等女频词——R2 触发依赖场景白描（两人对坐吃饭等）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py；aggregator/intuition_engine.py
- 分支/函数：MODE_PACING["女频甜宠竖屏分镜"]（dur_scale 0.4, move "推近特写"）→ build_standard_shots(density_scale=0.4) → generate_feature_shots 分支 D；intuition_engine.apply_intuition R2（_INTIMATE_KEYWORDS 命中时）
- 数据来源：cinematic_studio.DIRECTOR_CURVES/_normalize_director；SHOT_POOL_BY_DENSITY 反应/微距池
