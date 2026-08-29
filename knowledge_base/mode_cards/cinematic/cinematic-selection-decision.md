---
mode_id: cinematic-selection-decision
node: DirectorMasterCinematic
name: 选片决策
one_liner: 选片向分镜，剪辑意图池+EDL转场文本辅助选片与剪辑决策
applicable: [选片参考, 剪辑决策, 素材评审]
intensity: medium
style_tags: [选片决策, 剪辑意图, EDL, 转场设计, 评审]
aliases: []
---

## 意图

给剪辑/选片决策看的分镜：1.0 基线密度 + move=None——独特性在剪辑层：edit_intent 池 7 条剪辑意图（"在动作前留 0.5s 静默"/"切到空镜, 让'人不在'成为'人在想'"）逐镜注入，正文再附 EDL 转场文本（build_edit_decision_text）。

## 核心手法

- 零运镜干预：move=None 同 表演块——镜头语法交还引擎节奏分支。
- 剪辑意图池：`_make_pacing_shot` 的 edit_pool 7 条按镜号哈希写 edit_intent 字段——每镜一条"为什么这么剪"的决策依据。
- EDL 附加块：`cinema_craft.build_edit_decision_text(场景, 导演, 情绪)` 生成剪辑决策文本追加到正文——转场/节奏的决策参考层。
- 转场语义：cut 字段按节奏模板（硬切/叠化/跳切/无切）+ V13.2 偏好可覆盖——选片的转场一致性检查入口。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 核心数据包 | Core 32 字段 JSON | _核心冲突/_导演意图 进 EDL 与 AI 润色上下文——剪辑决策的叙事依据来源 |
| 剪辑节奏 | 无(默认) | 非 ND 直接改写每镜 dur（×2.5/1.8/0.5/0.3 或奇偶交替）且不再归一——选片评估的时长基准被破坏，建议 ND |
| 节奏风格 | 无(默认)=auto | 钉节奏可模拟特定剪辑风格的全片效果；"🎲 随机" 不生效 |
| 目标时长(分钟) | 段落级 | EDL 文本与体量无关，逐镜生成 |

## 已知坑

- 与 电影工作室/表演块 三胞胎（density 1.0 + move None）——区分度是 edit_intent 字段与 EDL 附加块（正文可见、JSON 不导出 edit_intent）。
- edit_intent 池 7 条通用（含"凤梨罐头"字样的条目）——具体物件语义可能与你项目物件冲突，属池文案现状。
- EDL 文本由 cinema_craft 生成——其内部按场景/导演/情绪确定性生成，无随机漂移。

## 节点映射

- 实现文件：aggregator/cinematic_studio.py；aggregator/pacing_engine.py；aggregator/cinema_craft.py
- 分支/函数：MODE_PACING["选片决策"]（dur_scale 1.0, move None）→ build_standard_shots → _make_pacing_shot edit_pool（7 条）→ build() 尾部 build_edit_decision_text(场景, 导演, 情绪) EDL 块
- 数据来源：pacing_engine.edit_pool；cinema_craft.build_edit_decision_text/build_edit_decision_list；format_templates.MASTER_VIDEO_PRINCIPLES（转场语法原则）
