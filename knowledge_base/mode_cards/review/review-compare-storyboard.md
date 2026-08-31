---
mode_id: review-compare-storyboard
node: DirectorMasterReview
name: 对比分镜
one_liner: 被审产物对照基准分镜JSON, 核镜数/逐镜时长/锚点覆盖
applicable: [改稿复核, 双版本对照, 上游改分镜后验证]
intensity: medium
style_tags: [对比核对, 镜数对齐, 时长漂移]
aliases: [分镜对比, 对照分镜]
---

## 意图

产物被改写过 (人工改稿/上游重排/另一引擎输出)、需要确认它仍与基准分镜对得上时选它。completeness 阶段 + compare 阶段 (X01 镜数对齐/X02 逐镜时长对齐/X03 锚点覆盖); 与 全量审查 的本质差别是对照物存在——发现全部带基准值与产物值双证据, 适合改稿前后的差异定位。

## 核心手法

1. 基准解析: `分镜JSON` 输入经 `_classify_artifact()` 判定, 非 storyboard 形态 (缺失/纯文本/非分镜 JSON) 时 X01/X02 诚实进「无法验证」并注明形态——绝不拿坏基准硬比。
2. X01 镜数对齐: 被审产物 `分镜表` 长度 vs 基准长度, 失配记 FAIL (证据=分镜数字段, 双数值)。
3. X02 逐镜时长对齐: 按下标逐镜比 `时长` (数值/“3.8s”式字符串统一经 `_num()` 归一), |Δ|>0.5s 记 WARN (证据=镜N, 报基准→产物双值); >8 处聚合上报; 产物非分镜 JSON 时该项降级为「无法验证」。
4. X03 锚点覆盖: 基准每镜 `镜号` 在产物全文中做子串检索, 缺失镜号计数并列举前 8 个——用于产物为纯文本改稿时判断逐镜对应关系是否断裂。
5. completeness 同跑: 对比前先做结构自检 (C01-C05), 基准对得再好、产物自身结构坏了照样 FAIL; compare 阶段摘要=sha256(产物+基准), 基准或产物任一变化自动失效重算。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 被审产物 | 改稿后的分镜JSON | 纯文本产物 → X02 进「无法验证」, 只剩 X01/X03 可判; 空输入 → C01 FAIL + X03 全镜号缺失 WARN |
| 分镜JSON | Cinematic.分镜JSON (基准) | 留空/不可解析 → X01 无法验证 "未提供对比基准" (缺输入不猜测), 报告不产出任何对比结论 |
| 审查模式 | 对比分镜 | 本模式不跑 consistency/coverage 阶段 (C06-C13 显示"本模式不涉及"); 要全核对切 全量审查 |
| 核心数据包 | Core.核心数据包 | 本模式不消费 brief, 留空不影响对比结论 |

## 已知坑

- 逐镜对比按"下标"而非镜号配对: 基准镜 3 被删除时, 产物镜 4 会与基准镜 4 (原镜 4) 按下标对齐——下标漂移场景应结合 X01 镜数失配与 X03 锚点覆盖综合判断, 不要单看 X02。
- X03 是子串检索: 镜号 "1" 会命中 "镜10" 等文本; 产物与基准同为 JSON 时建议以 X01/X02 为准, X03 主要服务于纯文本产物形态。
- 时长漂移门槛 0.5s 为硬编码: 秒级时长产物 (短视频 8-15s) 每镜漂移敏感性高于长片; 超门槛会逐镜 WARN, 改稿若有意调整时长请忽略对应条目。
- 检查点与全量审查共享: compare 摘要独立于 completeness, 但同 pipeline_id="review" 同 step 键空间——先后审不同产物/基准组合时按摘要自动失效, 无脏缓存。

## 节点映射

- 实现文件：aggregator/review_engine.py
- 分支/函数：review_artifacts() MODE_STAGES["对比分镜"]=("completeness","compare") 分支 → _stage_compare() (X01/X02/X03, 基准 `_classify_artifact()` 守卫) + _stage_completeness() → _render_report()
- 数据来源：被审产物文本 + 分镜JSON 基准输入 + aggregator/storyboard_contract.py validate_storyboard() (completeness 阶段) + CheckpointStore 阶段缓存
