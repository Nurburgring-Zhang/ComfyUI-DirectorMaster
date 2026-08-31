---
id: NP-012
rule: 宣称与实现必须同构——"随机"必须含执行期熵, 审计口径必须真跑, 结构谎报 (空分镜/重号镜号/坏时长/未知相对引用) 必须被诊断码点名; 自检失败要诚实 FAIL, 禁止静默放宽判定让报告变绿; 参数表注释与卡面宣称若与实现不符即失实。
precedent: 双重实测判例: ① V16.3 P0 "随机名不副实"——MD5(输入) 为种子的"随机"30 轮仅产出 1 位唯一导演, 项目自带 final_capability_audit 4 项 FAIL (导演去重 1/30、剧本指纹 22/30、分镜指纹 28/30、镜头语法重复率 29.4%>15%), 违反项目零虚假红线; ② 分镜契约 v1 以 11 个诊断码把结构谎报变成机器可点的名 (duplicate-shot-id/empty-shots/invalid-duration/relative-ref-unknown…); 批次2 互审沉淀卡面失实教训入红线: "已知坑不得虚构, 确无坑可写时写'未发现', 禁止编造"。
self_check: 本次宣称的每一条"已实现/已通过"是否有对应测试断言或 file:line 证据? 随机是否有执行期熵 (换种子真变)? 是否存在被静默放宽/跳过的判定? 卡面宣称的数值与代码现值是否逐字核对过?
evidence_ref: docs/CHANGELOG.md:85 (V16.3 P0 判例 4 项 FAIL 全数字); tests/final_capability_audit.py:86-91 (同口径常驻守门); aggregator/storyboard_contract.py:17-21 (11 诊断码); knowledge_base/mode_cards/SCHEMA.md:58-60 (红线: 已知坑不得虚构); knowledge_base/mode_cards/cinematic/cinematic-viral-twist.md:34 (clamp 静默行为=卡面失实教训)
---

# NP-012 伪成功 (fake success / 宣称失实)

## 规则
伪成功是最高级别缺陷: 交付物"看起来完成"但承诺虚假。判定与防线:
1. 随机必须真随机: 种子必须含执行期熵 (种子 0 = SystemRandom 真随机; 固定种子可复现是确定性, 不是随机性), "30 轮随机仅 1 位唯一"即伪随机实锤;
2. 审计必须真跑: 能力审计断言 (导演去重≥15/30、剧本指纹 30/30、分镜指纹 30/30、语法重复率<15%) 是机器判定, 不接受"目测没问题";
3. 结构谎报机器化: 分镜 JSON 契约以 11 个诊断码点名谎报形态——missing-contract-version/invalid-contract-version/missing-shot-id/duplicate-shot-id/invalid-duration/type-mismatch/empty-shots/relative-ref-unknown/relative-ref-cycle (+deprecated-field/unknown-field 警告), 空分镜冒充成功会被 empty-shots 直接点破;
4. 宣称对齐: 注释/卡面/文档里的数值与代码现值逐字一致 (dur_scale 0.2→0.3 clamp 这类静默行为必须写在明面), 互审红线明文"已知坑不得虚构, 确无坑可写时写'未发现', 禁止编造";
5. 判定纪律: 自检失败输出 FAIL 并带原因, 禁止为了报告好看放宽阈值或跳过断言。

## 判例
判例一 (V16.3, CHANGELOG 原文): "🎲 随机名不副实 (P0, 违反项目自身零虚假红线): V16.1 起所有 🎲 随机以 MD5(项目名_场景描述) 为种子, 相同输入下每次执行输出完全相同 (30 轮'随机'导演仅 1 位唯一), 项目自带 tests/final_capability_audit.py 4 项失败 (导演去重 1/30、剧本指纹 22/30、分镜指纹 28/30、镜头语法重复率 29.4%>15%)。根因: 随机种子只含输入哈希, 不含任何执行期熵。"——功能名与实现语义脱节, 被项目自己的审计抓出。判例二 (批次2 互审沉淀): 卡面失实教训进入 SCHEMA 红线 ("已知坑不得虚构…禁止编造"), 具体案例为 cinematic-viral-twist 卡记录的 "dur_scale 0.2 → 0.3 的 clamp 是静默行为——卡面/注释若宣称 0.2 即失真; 实际密度以 clamp 后为准"。判例三 (结构谎报防线): 分镜契约 docstring 明列 11 诊断码, empty-shots "分镜表为空 (至少需要 1 个镜头)" 与 duplicate-shot-id 直接把"有输出"≠"有效输出"的谎报拦下。

## 自检
- 每条"已实现/已通过": 测试名或 file:line 在哪? 拿不出即撤回宣称。
- 随机类功能: 换种子输出真变吗? 固定种子逐字节可复现吗? (两者都要成立)
- 有没有被注释掉/放宽过的断言? 有无静默 clamp/静默降级未写进宣称?
- 卡面/注释数值与代码现值: 逐字核对了吗?

## 证据指针
- docs/CHANGELOG.md:85 — V16.3 P0 判例 (4 项 FAIL 全数字, 零虚假红线)
- tests/final_capability_audit.py:86-91 — 导演去重/剧本指纹/分镜指纹/重复率 常驻守门断言
- aggregator/storyboard_contract.py:17-21 — 11 诊断码清单 (结构谎报机器化)
- aggregator/storyboard_contract.py:407-408 — empty-shots ("分镜表为空 (至少需要 1 个镜头)")
- knowledge_base/mode_cards/SCHEMA.md:58-60 — 互审红线: 已知坑不得虚构, 禁止编造
- knowledge_base/mode_cards/cinematic/cinematic-viral-twist.md:34 — 卡面失实教训 (静默 clamp)
