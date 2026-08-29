---
mode_id: cinematic-slow-motion-highlight
node: DirectorMasterCinematic
name: 慢镜高光
one_liner: 1/8慢放镜头组，每镜标注实际慢放时长，高潮凝视专用
applicable: [情感高潮, 动作凝固, 诗意瞬间]
intensity: low
style_tags: [慢镜高光, 王家卫, 诺兰, 升格, 1/8慢放]
aliases: [升格镜头]
---

## 意图

给高光时刻"时间上的放大"：镜头时长按 1/8 速度语义标注慢放倍率，让观众住进这一刻。与 极慢抒情（1/20 空镜）的差别是本模式对准人物动作/表情的中近景，与 子弹时间 的差别是变时间不变机位。

## 核心手法

- 分支 B 慢镜：`MODE_TO_PACING["慢镜高光"]="慢镜高光"` → `generate_feature_shots` 分支 B——target_shots=max(场次基准, ceil(场秒/8.0))，30 镜封顶；density≤1 时若单镜>30s 自动加镜保覆盖。
- 慢放标注：focus_tpl 动态注入 "1/8 慢镜, {dur}s 实际 = {dur×8}s 慢放"——慢放倍率写进画面焦点字段，下游可直接读；sound_tpl="音乐+呼吸+心跳, 慢节奏, 1/8 速度"。
- 模板档型：中景 50mm 慢速环绕 360°、叠化转场；"慢速环绕" 不参与 D1 运镜变体（签名保护），同簇差异靠焦点文案与 4 层声音配比哈希。
- 张力联动：tension 6-10 场（冲突→爆发档）自动获得 高对比/强逆光/冲突材质 的色彩光影材质递进，慢镜视觉与情节张力对齐。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 高光段落（秒-2min） | 镜数=场秒/8（均值 8s/镜）；120s 场约 15 镜；30 镜封顶后单镜>30s 会加镜摊薄 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="慢镜高光" 同键；"🎲 随机" 不生效 |
| 焦段偏好 | 无(默认) | 非 ND 覆写 50mm 模板焦段；长焦/广角会改变"环绕亲密"语义，需有意识选择 |
| 剪辑节奏 | 无(默认) | 极慢×2.5 会把 8s 镜乘成 20s 且不再归一 → 时长覆盖失效；慢放语义已内置，勿叠加 |

## 已知坑

- 1/8 慢放是文案语义（dur×8 写进 focus），不是对 dur 字段的 8 倍改写——总时长仍按原 dur 覆盖场戏；下游按 focus 提示自行升格。
- 导演偏置对慢镜类的加成（王家卫 慢镜 1.5）只在 auto 节奏路径生效；本模式已钉节奏，偏置不叠加。
- 30 镜 cap：超长场（>4min）每镜被摊到 >8s，"高光"密度感稀释——按段落拆场使用。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["慢镜高光"]="慢镜高光" → generate_feature_shots 分支 B（is_slow_pacing）→ PACING_TARGET_AVG_DUR["慢镜高光"]=8.0 → _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["慢镜高光"]（王家卫/诺兰/扎克·施奈德 masters）；feature_film_engine 色彩/光影/材质/氛围四级递进表
