---
mode_id: cinematic-gunfight-boards
node: DirectorMasterCinematic
name: 枪战分镜
one_liner: 0.5-1s手持快切五镜组（扳机-开火-弹壳-中弹-环境），吴宇森式暴烈
applicable: [枪战, 搏击, 暴烈冲突]
intensity: high
style_tags: [枪战, 吴宇森, 手持快切, 跳切, 荷兰角]
aliases: []
---

## 意图

暴烈密度的标准五镜组：0.5s 扳机 → 0.8s 开火 → 0.5s 弹壳 → 0.7s 中弹甩镜 → 1.0s 环境混乱，均值 1.0s/镜。与 一秒三闪 的差别是枪战有因果链（扳机→结果），三闪是情绪三连击。

## 核心手法

- 节奏钉死：`MODE_TO_PACING["枪战分镜"]="枪战分镜"`，走分支 C 类型类——`PACING_TARGET_AVG_DUR["枪战分镜"]=1.0`，镜数=ceil(场秒/1)。
- 五镜模板：`PACING_STYLES["枪战分镜"]` —— 大特写 85mm 固定 0.5s（枪响一拍）→ 中近景 35mm 手持快切 0.8s（跳切）→ 特写 50mm 快推弹壳 0.5s → 中景 24mm 手持甩镜荷兰角 0.7s（跳切）→ 全景 24mm 甩镜 1.0s（环境+回声）。
- 缩放覆盖：expand_pacing_shots 按场时长缩放（0.3s 下限保护），mode_seed 偏移模板起点，缺口>0.5s 再归一。
- 大师注释池：8 条（吴宇森《喋血双雄》慢镜+白鸽+枪响/迈克尔·曼《盗火线》扳机-枪口-中弹-倒地 1s 内 4 镜…）哈希注入 director_note。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 目标时长(分钟) | 交火段（0.25-2min） | 镜数=场秒/1；30s 约 30 镜——快切密度上限按此公式，长场海量镜请拆段 |
| 节奏风格 | 无(默认)=已钉 | 与 节奏风格="枪战分镜" 同键；"🎲 随机" 不生效 |
| 剪辑节奏 | 无(默认) | 极快×0.3 把 0.5s 镜乘成 0.15s 显示且不再归一 → 时长覆盖失效；跳切已内置模板 |
| 直觉风险 | 无(默认) | R3 喧闹后静默（前镜张力≥7 → 本镜"静默(前镜喧闹的余波)"）与枪战声景形成反差——有意的美学选择；R1 时长×1.5 破坏覆盖 |

## 已知坑

- 枪战语义全靠模板文案——引擎不校验场景有无武器；非暴力场景误用会产出违和的扳机/弹壳镜头。
- "手持快切/手持甩镜" 在 _MOVE_VARIANTS 无同族键（"手持"有、"手持快切"无）——同簇 D1 差异主要靠焦段/景别偏移与声音配比哈希。
- 荷兰角角度档仅出现在模板，D1 角度变体池只对"平视"做微俯仰——荷兰角保持原样。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/feature_film_engine.py
- 分支/函数：MODE_TO_PACING["枪战分镜"]="枪战分镜" → generate_feature_shots 分支 C（is_fast_pacing）→ expand_pacing_shots → _make_pacing_shot（director_notes_by_pacing["枪战分镜"]）
- 数据来源：pacing_engine.PACING_STYLES["枪战分镜"]（吴宇森/迈克尔·曼/朴赞郁 masters + 5 镜序列）；aggregator/intuition_engine R3/R8（启用时）
