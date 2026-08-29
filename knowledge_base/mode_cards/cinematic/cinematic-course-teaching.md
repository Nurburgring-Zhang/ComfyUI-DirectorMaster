---
mode_id: cinematic-course-teaching
node: DirectorMasterCinematic
name: 课程教学分镜
one_liner: 课程教学分镜，1.2密度均匀节奏，10-30min课程体量桶化30分钟档
applicable: [在线课程, 技能教学, 讲师录播]
intensity: low
style_tags: [课程教学, 均匀节奏, 知识点, 录播, 低张力]
aliases: []
---

## 意图

课程节奏的镜头化：1.2 密度 + 教学运镜——与 儿童教育 的差别是受众（成人教学 vs 早教）与体量（10-30min vs 早教短内容）；两者共享"均匀节奏 + 步骤锚定"的实现路径。

## 核心手法

- 体量推导：10-30min → 5-10 场（≥15 梯 t/3、≥30 梯 t/3.5）；density 1.2 → 分支 D target_avg=12s → 每场镜数按 场秒/12。
- 知识点锚定："△" 分块剧本前 6 块驱动 purpose（"剧本驱动: …"）——每个语义块对应一个知识点的镜头组。
- 主导运镜：move="教学运镜" 覆写 2/3 镜；重点强调靠 detail 池特写与构图 note。
- 强调位：张力曲线波峰（≈88% 处）对应课程收尾重点——可当"总结强调"位使用。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 10-30 | 桶化 ≥20→30：10-19min 课程按 30min 梯出 8 场——课程切分与名义时长脱钩 |
| 节奏风格 | 无(默认)=auto | 保持 ND 均匀节奏；"🎲 随机" 不生效 |
| 剧本输入 | Script 课程脚本 | 前 6 块驱动 purpose；超过 6 个知识点的课程后续块无标注——建议按 6 块拆分输入 |
| 核心数据包 | Core 32 字段 JSON | 高张力导演档（诺兰 +1 张力）会推高教学内容张力曲线——教学场景建议低张力导演档 |

## 已知坑

- 与 儿童教育分镜 同密度同运镜签名（"教学运镜" vs "教育运镜" 仅一字）——区分度是典型时长与受众语义（d1 分簇靠 note 差异）。
- 教学步骤模板（教程步骤格式的 操作说明/完成状态 行）不在本节点——步骤感靠 purpose 与场次。
- 10min 落 ≥3 梯 6 场、15min 落 ≥15 梯 5 场——10-15min 区间场数不单调，切分课程时注意。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_PACING["课程教学分镜"]（dur_scale 1.2, move "教学运镜"）→ build_standard_shots(density_scale=1.2) → get_beat_map ≥15/≥30 梯 → generate_feature_shots 分支 D；_parse_script_shot_drivers（知识点块）
- 数据来源：feature_film_engine.get_beat_map 中长梯；SHOT_POOL_BY_DENSITY detail/establishing 池
