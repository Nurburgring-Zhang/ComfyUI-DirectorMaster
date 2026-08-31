---
id: NP-004
rule: 禁空洞情绪词 ("震撼/完美/史诗感拉满/帅气/质感拉满"式)——每个情绪词必须有可见动作/物件/环境承载, 用具体可拍描述替代 ("震撼/失重"→"失重般的失衡/眩晕"); 输出文本对 VACANT_WORDS 与一票否决词表零命中。
precedent: V16.5 实测返工: 罐头池"决战场面/震撼"→"决战场面/胜负手"、"震撼/失重"→"失重般的失衡/眩晕", 动机即"用具体可拍描述替代空洞情绪词"; 清洗后的词句固化进 feature_film_engine 张力词表并沿用至今。测试侧双守门: 全维度矩阵把 VACANT_WORDS 零命中列为质量项, ten_rounds 一票否决扫描把 masterpiece/8K 等列入禁词。
self_check: 输出文本是否命中 VACANT_WORDS (完美/震撼/史诗感拉满/帅气/质感拉满) 或一票否决词表? 每个"情绪词"是否都有可见的动作/物件/环境承载, 还是只有形容词?
evidence_ref: aggregator/feature_film_engine.py:3689 ("决战场面/胜负手"); aggregator/feature_film_engine.py:3796 ("失重般的失衡/眩晕"); tests/test_matrix_full.py:55,142 (VACANT_WORDS 零命中); tests/ten_rounds.py:370-385 (一票否决扫描)
---

# NP-004 空洞词 (vacant words)

## 规则
空洞词是"看起来在写、实际拍不出"的元凶: "震撼""完美""史诗感"不传达任何摄影机可执行的信息。规则:
1. 词表防线: VACANT_WORDS (完美/震撼/史诗感拉满/帅气/4K/8K/质感拉满…) 与 ten_rounds 一票否决词表 (masterpiece/best quality/ultra detailed/占位符/lorem…) 双表零容忍, 规则声明行本身豁免;
2. 替代原则: 用具体可拍描述替代空洞情绪词——不是"震撼", 而是"失重般的失衡/眩晕"; 不是"决战很燃", 而是"胜负手在这一拍";
3. 情绪承载: 每个情绪必须落到可见的动作/物件/环境 (汗珠、停顿半拍的筷子、起泡的标签), 形容词只许做从句不做主句;
4. 生成侧与审查侧共用同一词表, 审查命中即打回, 不接受"感觉到了就行"。

## 判例
V16.5 场景实体引擎提交里的实测返工: 罐头池原文"决战场面/震撼"被清洗为"决战场面/胜负手"、"震撼/失重"被清洗为"失重般的失衡/眩晕", CHANGELOG 记录动机为"附件标准: 用具体可拍描述替代空洞情绪词"。清洗结果不是一次性脚本, 而是固化进张力量表: feature_film_engine.py:3689 张力 8 档词面至今写作 `"决战场面/胜负手"`, :3796 写作 `"失重般的失衡/眩晕"`。测试侧配套: test_matrix_full.py 以 `VACANT_WORDS` 元组驱动"零空洞词"质量项 (含 _空洞词明细 诊断输出); ten_rounds T10 一票否决扫描把 masterpiece/8K/HDR/占位符 等列为零容忍词 (规则定义行豁免)。

## 自检
- 全文 grep VACANT_WORDS 与一票否决词表: 是否零命中 (规则声明行除外)?
- 每个情绪描述: 能否让摄影指导直接照着摆机位? 不能 → 重写为动作/物件/环境承载。

## 证据指针
- aggregator/feature_film_engine.py:3689 — `8: "决战场面/胜负手"` (清洗后固化)
- aggregator/feature_film_engine.py:3796 — `8: "失重般的失衡/眩晕"` (清洗后固化)
- docs/CHANGELOG.md:50 — 空洞词清洗记录与动机
- tests/test_matrix_full.py:55 — `VACANT_WORDS = ("完美", "震撼", "史诗感拉满", "帅气", ...)`; :142 `quality["零空洞词"]`
- tests/ten_rounds.py:370-385 — 一票否决扫描 (VETO 词表 + 规则行豁免)
