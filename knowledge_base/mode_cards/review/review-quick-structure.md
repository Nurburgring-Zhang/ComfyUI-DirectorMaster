---
mode_id: review-quick-structure
node: DirectorMasterReview
name: 快速结构审查
one_liner: 完整性阶段结构自检, 秒级判定产物可解析/契约/镜数/字段/时长有效
applicable: [生成后即检, 管线中段把关, 交付前初筛]
intensity: low
style_tags: [结构自检, 分镜契约, 确定性轨]
aliases: [快速审查, 结构自检]
---

## 意图

产物刚从上游节点下来、只想用最低成本确认"结构没坏"时选它。只跑 completeness 阶段 (C01-C05 五项), 不做场景锚定/手法/覆盖类语义核对——与 全量审查 的本质差别是核对范围 (5/13 项) 与耗时, 与 对比分镜 的差别是不需要基准分镜。

## 核心手法

1. 产物形态判定: `_classify_artifact()` 把输入分为 empty/storyboard/json-other/text 四态 (json.loads 优先, 落 pln_llm.json_loads_tolerant 宽容解析); 非分镜 JSON 的结构项诚实进「无法验证」, 不猜测。
2. 契约诊断映射: 调 `aggregator/storyboard_contract.py :: validate_storyboard()` (契约 v1, 11 诊断码), errors 按 code 分流——empty-shots/missing-shot-id/duplicate-shot-id/type-mismatch/relative-* 记 C02, invalid-duration 单独记 C05, warnings 记 INFO; 校验器缺席时手动兜底扫描每镜时长可解析且 >0。
3. 镜数一致性: 顶层声明 `分镜数` 与 `分镜表` 实际长度逐位比对, 类型错/不符记 FAIL (证据=分镜数字段)。
4. 字段完整性: 每镜 10 个必填核心字段 (镜号/景别/运镜/时长/画面焦点/声音/转场/叙事目的/首帧描述/AIGC提示词) 在场且非空; ≤12 处逐条 FAIL (证据=镜N·字段), 超限聚合上报。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 被审产物 | Cinematic.分镜JSON | 空输入 → R-001 FAIL "产物为空" + C02-C05 无法验证; 纯文本 → 结构项全部诚实标注无法验证, 只报 C01 |
| 审查模式 | 快速结构审查 | 本模式只跑 completeness 阶段, 其余 8 项清单显示"本模式不涉及"; 要全核对请切 全量审查 |
| 核心数据包 | Core.核心数据包 | 本模式不消费 brief (无场景锚定/模式一致性项), 留空不影响结果 |

## 已知坑

- 校验器不可用降级: aggregator.storyboard_contract 导入失败时 C02 进「无法验证」并注明原因, C05 落手动兜底扫描 (只判数值可解析, 不覆盖契约相对引用环检测)——报告头可见 "契约校验器不可用" 字样。
- 阶段检查点复用: completeness 阶段结果按 `sha256("v1|completeness|"+产物)` 落盘 (pipeline_id="review"), 同产物随后跑 全量审查 会直接跳过该阶段 (stages.completeness.status=="skipped"); 改产物任一字节即自动失效重算。
- 空分镜表: shots=[] 时 C04 记 FAIL "分镜表为空", 此时 C11/C12 等 shot 级项在全量审查里进「无法验证」而非误报 0 命中通过。

## 节点映射

- 实现文件：aggregator/review_engine.py
- 分支/函数：review_artifacts() MODE_STAGES["快速结构审查"]=("completeness",) 分支 → _stage_completeness() (C01-C05) → _render_report() 编号输出
- 数据来源：被审产物文本 + aggregator/storyboard_contract.py :: validate_storyboard() 诊断码 + CheckpointStore 阶段缓存 (output/_review_checkpoints/)
