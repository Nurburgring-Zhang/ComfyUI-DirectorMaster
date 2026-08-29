---
mode_id: cinematic-interactive-branching
node: DirectorMasterCinematic
name: 互动剧分支分镜
one_liner: 互动剧分镜，分支感由银幕序重排+线/POV标注承担，JSON含时序位字段
applicable: [互动剧, 多分支短剧, 游戏化叙事]
intensity: adaptive
style_tags: [互动剧, 分支叙事, 银幕序, 多线, 非线性]
aliases: []
---

## 意图

分支结构的分镜基座：0.8 密度 + 分支运镜签名——"分支"由两层机制承担：叙事编排下拉把镜头按时序重排为银幕序（倒叙/穿插/循环），JSON 的 银幕序/时序位 双字段记录每个镜头的两个位置。

## 核心手法

- 体量推导：3-10min → 3-5 场；density 0.8 → 分支 D target_avg=8s。
- 银幕序重排：叙事编排=穿插倒叙/穿插乱叙/循环叙事(首尾相扣) → arrange_scenes 生成编排计划（方式/时间线图谱/线索图谱/导演批注/字幕位）→ arrange_shots_by_scenes 重排并重编镜号；同场镜头不拆散。
- 分支标签：叙事线型=POV切换/双线并行 → purpose 写 线/POV/时间 标签；JSON 银幕序=screen_order、时序位=story_order——分支播放器的排序依据。
- 主导运镜：move="分支运镜" 覆写 2/3 镜。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 叙事编排 | 穿插倒叙/循环叙事(首尾相扣) | 保持"跟随叙事结构"则零重排——分支语义只剩运镜签名；重排异常 stderr 降级保原序 |
| 叙事线型 | POV切换/双线并行 | 未设则 purpose 标签恒 单线/全知——分支选择感无标签支撑 |
| 目标时长(分钟) | 3-10 | 桶化 ≥20→30；分支剧建议单集短体量 |
| 节奏风格 | 无(默认)=auto | "🎲 随机" 不生效；钉节奏会破坏分支段的快慢对比 |

## 已知坑

- 无真实分支树输出（A/B/C 选项树不在契约 v1 字段）——"分支"是银幕序+标签的线性近似，真互动引擎需下游按 银幕序/时序位 自行组树。
- 编排计划依赖重新 generate_feature_scenes——异常时（场景解析失败等）stderr "[DirectorMaster] 分镜叙事编排降级" 后保持原序，不失败节点。
- 叙事编排的 🎲 随机真随机生效（resolve_dropdown 带 options）——不可复现，调试时用固定值。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/narrative_arrangement.py
- 分支/函数：MODE_PACING["互动剧分支分镜"]（dur_scale 0.8, move "分支运镜"）→ build() 叙事编排/叙事线型 解析（resolve_dropdown 带 options）→ arrange_scenes + arrange_shots_by_scenes → JSON 银幕序/时序位/叙事编排 块
- 数据来源：narrative_arrangement.ARRANGEMENT_MODES/NARRATIVE_LINE_MODES/_arrange_plan（导演批注/字幕位）
