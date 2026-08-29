---
mode_id: cinematic-montage-master
node: DirectorMasterCinematic
name: 蒙太奇大师
one_liner: 全场戏0.5-2.5s蒙太奇序列，按场时长缩放覆盖，爱森斯坦式时间压缩
applicable: [时间跨越段落, 训练成长戏, 抒情压缩]
intensity: medium
style_tags: [蒙太奇, 爱森斯坦, 时间压缩, 快切]
aliases: [蒙太奇]
---

## 意图

把一段"长时间"压成 10-30 镜的蒙太奇序列：0.5-2.5s 每镜、景别/焦段五档轮换（大特写 85mm→全景 24mm）。与 抖音超快 的差别是蒙太奇有明确的"时间压缩/抒情推进"意图与 1.5s 均值，而非短视频钩子节奏。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["蒙太奇大师"]="蒙太奇"`，走 `generate_feature_shots` 分支 C（快闪类）——`PACING_GROUP_FORMULAS["蒙太奇"]=(1.5s, 1镜, 30镜上限)`，镜数=ceil(场秒/1.5)，超 30 镜时按动态上限加组（硬顶 600 组）保证覆盖。
- 十镜模板循环：`PACING_STYLES["蒙太奇"].shot_sequence` 是 10 镜生成序列——size/move/focal/dur 各按 i%5 轮换（大特写0.5s/特写1.0s/中近景1.5s/中景2.0s/全景2.5s），focus_tpl="蒙太奇第{idx}镜——阶段性瞬间"。
- 时长缩放：`expand_pacing_shots` 以 场时长/模板总时长 求缩放因子，逐镜 dur 上限 30s（原生 <30s 模板），末尾偏差>0.5s 时整体再归一——总秒数覆盖场戏时长（±1% 级）。
- 声音设计：模板 sound_tpl="音乐渐强 + 拟音"；每镜再叠 4 层配比（环境 30-59% + 拟音 10-29% + 音乐 0-19% + 留白余量）由镜号哈希确定。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 段落级（1-5min 压缩段） | 只改镜数（场秒/1.5）不改单镜 0.5-2.5s 档型；长场靠动态加组覆盖而非拉长单镜（V14.3 审查P2 行为） |
| 节奏风格 | 无(默认)=已钉蒙太奇 | 选"抖音超快"等会整场替换蒙太奇档型；"🎲 随机" 不命中映射保持蒙太奇 |
| 剧本输入 | Script 输出 | "△"分块前 6 块折入 purpose；蒙太奇"阶段瞬间"的叙事锚点建议每块一句话 |
| 构图法则 | 无(默认) | 非 ND 追加到每镜 note"构图: X"，不改变模板的景别/焦段轮换；"🎲 随机" 字面量入 note |

## 已知坑

- 动态组上限 600：极端长场（>15min）会产生数百镜蒙太奇——与"抒情压缩"意图相悖，长段请按场拆分输入。
- 与 蒙太奇 下拉（节奏风格="蒙太奇"）完全同源：RHYTHM_TO_PACING["蒙太奇"] 同键——本模式等价于"全场戏强制 节奏风格=蒙太奇"，另加签名 note。
- 模板轮换焦点文案较通用（"阶段性瞬间"），具体物件细节依赖场景解析出的 objects——空物件输入落"关键道具"占位。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["蒙太奇大师"]="蒙太奇" → generate_feature_shots 分支 C（is_fast_pacing）→ PACING_GROUP_FORMULAS["蒙太奇"] → expand_pacing_shots（缩放+归一）→ _make_pacing_shot
- 数据来源：pacing_engine.PACING_STYLES["蒙太奇"]（爱森斯坦/普多夫金/莱昂内 masters + 10 镜序列）；format_templates.MASTER_VIDEO_PRINCIPLES
