---
mode_id: cinematic-kids-education
node: DirectorMasterCinematic
name: 儿童教育分镜
one_liner: 早教内容分镜，1.2密度均匀节奏+低张力曲线，步骤感靠场次切分
applicable: [早教动画, 知识科普短视频, 儿童课程]
intensity: low
style_tags: [儿童教育, 早教, 均匀节奏, 低张力, 科普]
aliases: []
---

## 意图

教学节奏的镜头化：1.2 密度（轻度减镜）+ 教育运镜——知识点的"步骤感"由场次切分与均匀镜时承担，一讲一个点。与 绘本故事 的差别是教学语义（步骤/强调）与密度（1.2 vs 1.5）。

## 核心手法

- 体量推导：10-30min → get_beat_map ≥15/≥30 梯 5-10 场；density 1.2 → 分支 D target_avg=12s → 每场镜数按 场秒/12 推导。
- 主导运镜：move="教育运镜" 覆写 2/3 镜；教学强调靠 detail 池（知识点物件特写）与构图 note 追加。
- 低张力均匀档：tension 1-3 贯穿——儿童内容的视觉安全档（无高对比/冲突材质）。
- 步骤锚定：剧本/场景的知识点块经 "△" 分块驱动 purpose（前 6 块）——"第一步/第二步"的语义锚。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 10-30 | 桶化 ≥20→30：10-19min 内容按 30min 梯出 8 场——课程体量与名义时长脱钩 |
| 节奏风格 | 无(默认)=auto | 保持 ND 均匀节奏；钉快闪会违反儿童内容安全节奏；"🎲 随机" 不生效 |
| 核心数据包 | Core 32 字段 JSON | 张力高位档（红黑对比/冲突材质）不会被本模式触发——但 _导演风格=诺兰 等会推高张力（+1），儿童内容慎配高张力导演档 |
| 剧本输入 | Script 教程脚本 | 前 6 块驱动 purpose——超过 6 个知识点的课程后续块无驱动标注 |

## 已知坑

- 教学步骤结构（教程步骤模板）属于 format_templates 其他节点的模板——本模式输出统一分镜表，步骤感靠 purpose 标注与场次切分近似。
- 10min 恰落 ≥3 梯（t/1.5=6 场）；15min 落 ≥15 梯（5 场）——10-15min 之间跨梯时场数反而可能变少（6→5），教学切分需留意。
- 张力曲线的波峰在教学内容里对应"重点强调"——可当强调位用，但视觉档仍是低张力（无红色警报档）。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["儿童教育分镜"]（dur_scale 1.2, move "教育运镜"）→ build_standard_shots(density_scale=1.2) → get_beat_map ≥15/≥3 梯 → generate_feature_shots 分支 D
- 数据来源：feature_film_engine.SHOT_POOL_BY_DENSITY detail/establishing 池；四级递进表低张力档；_parse_script_shot_drivers（知识点块）
