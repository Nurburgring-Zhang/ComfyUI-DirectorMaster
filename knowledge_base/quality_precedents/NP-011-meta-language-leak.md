---
id: NP-011
rule: 面向模型的元语言 (质量咒语 masterpiece/best quality/ultra detailed、negative prompt 词、"作为AI"式自指、提示词指令语法) 不得泄漏进创作正文; 英文 AI 标志词在正面内容零命中 (禁用语境行豁免); 分辨率/交付规格词 (4K/HDR) 是合法技术参数不属套话, 替换逻辑必须保留其合法用法。
precedent: 仓库双重守门实测: ten_rounds 一票否决扫描以 VETO=[TODO/FIXME/placeholder/占位符/lorem/masterpiece/best quality/ultra detailed/8K/HDR] 扫剧本/分镜/手册三路输出, 规则定义行自身豁免; test_random_full_v16 以 AI_CLICHES 十词扫前 40 镜画面焦点/叙事目的, 负面语境词 (禁用/不用/避免/绝不/negative/禁止/无) 所在行豁免。anti_ai_vocab ANTI_AI_PHRASES 沉淀英文标志词替换表, 且 V13.5 注记明确了合法规格词边界。
self_check: 创作正文是否出现 masterpiece/8K 式咒语、"作为AI"式自指或提示词语法? 禁词是否只出现在规则声明/负面约束行? 分辨率词的合法技术用法是否被误伤替换?
evidence_ref: tests/ten_rounds.py:370-385 (VETO 一票否决+规则行豁免); tests/test_random_full_v16.py:75-76,129-138 (AI_CLICHES 零命中+负面语境豁免); anti_ai_vocab.py:24-40 (替换表与 V13.5 合法规格词边界)
---

# NP-011 元语言泄漏 (meta-language leakage)

## 规则
元语言泄漏 = 写给模型看的话出现在给人看/给下游消费的创作正文里。两种典型:
1. 咒语泄漏: masterpiece / best quality / ultra detailed / trending on artstation 等质量咒语混进画面焦点、叙事目的、剧本正文;
2. 自指泄漏: "作为一个AI""以下是优化后的提示词""注意: 负面提示词为…"式模型自白或提示词语法进入交付文本。
规则: 正面内容对 AI_CLICHES 十词零命中; 一票否决 VETO 十词扫三路输出; 唯一豁免是规则定义行/负面约束行本身 (它们必须枚举禁词才能生效)。边界口径: 4K/HDR/分辨率是合法影视交付规格, 反 AI 词表 V13.5 起明确不对其做空替换 ("空替换会破坏'采用4K HDR拍摄'类合法内容"), 套话防线由其余美学词承担——审查时同理, 不把合法技术参数误判为咒语。

## 判例
守门代码即判例现场: ten_rounds.py:370 `VETO = ["TODO", "FIXME", "placeholder", "占位符", "lorem", "masterpiece", "best quality", "ultra detailed", "8K", "HDR"]`, :373-374 `_rule_line()` 识别含"禁用/反AI套话/ANTI_AI/反AI规则/反AI词"的行并跳过——豁免逻辑本身就是对"规则行必须枚举禁词"这一事实的承认。test_random_full_v16.py:135 用负面语境词表 (`"禁用", "不用", "避免", "绝不", "negative", "禁止", "无"`) 实现同一豁免语义。anti_ai_vocab.py:38-40 注记: "V13.5: 移除纯分辨率/交付规格词 (8k/4k/2k/hd/uhd/hdr/high resolution 等) 的空替换——这些是影视制作的合法交付规格…美学填充词的防AI职责由 masterpiece/best quality/ultra detailed 等其余词条承担。"

## 自检
- 三路输出 (剧本/分镜/手册) 扫 VETO 词表: 是否零命中 (规则行除外)?
- 前 40 镜画面焦点/叙事目的扫 AI_CLICHES: 是否零命中 (负面语境行除外)?
- 交付文本里有没有"作为AI/以下是/提示词:"式自指?
- 分辨率/规格词出现时: 是合法技术参数 (如"采用4K HDR拍摄") 还是无信息量的咒语?

## 证据指针
- tests/ten_rounds.py:370-385 — T10 一票否决扫描 (VETO + _rule_line 豁免)
- tests/test_random_full_v16.py:75-76 — AI_CLICHES 十词表; :129-138 — 正面内容零套话断言
- anti_ai_vocab.py:24-40 — ANTI_AI_PHRASES 英文标志词替换表 + V13.5 合法规格词边界注记
- aggregator/llm_engine.py:219 — 领域规则 "负面约束正向表达优先, 显式排除: 无字幕/无水印/无logo"
