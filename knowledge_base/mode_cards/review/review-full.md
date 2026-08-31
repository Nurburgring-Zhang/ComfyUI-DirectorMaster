---
mode_id: review-full
node: DirectorMasterReview
name: 全量审查
one_liner: 干净上下文跑满 13 项清单, 判例库自检加可选 LLM 语义轨
applicable: [交付前终检, 返工后复检, 质量闭环]
intensity: high
style_tags: [13 项清单, 断点续跑, LLM语义轨]
aliases: [全量核对, 深度审查]
---

## 意图

产物要交付、或返工后需要完整质量闭环时选它。completeness+consistency+coverage 三阶段跑满 13 项清单 (C01-C13), 报告带判例库自检段与编号发现统计; 与 快速结构审查 的本质差别是覆盖语义/覆盖类核对 (时长覆盖±1%/景别运镜多样性/场景锚定 60% 门槛/重复手法/空洞词), 与 对比分镜 的差别是不需要基准分镜、但唯一一个会发起 LLM 调用的模式。

## 核心手法

1. 三阶段执行: MODE_STAGES["全量审查"]=("completeness","consistency","coverage"), 每阶段独立过 CheckpointStore (`done(pipeline_id="review", step, input_hash)` → 跳过 / `mark_done(..., artifact_ref=阶段产物JSON)`); 阶段摘要分别为 sha256(产物) / sha256(产物+brief) / sha256(产物+brief), 中断重入已完成阶段直接从磁盘阶段产物恢复, 摘要变化自动失效重算。
2. 一致性轨: C10 把 brief `_导演风格`(剥 `[电影]` 前缀)/`_情绪基调` 与产物顶层 导演/情绪 双向子串比对; C11 扫相邻镜同 (景别,运镜) 连用 ≥2 镜记 WARN (证据=镜A-镜B); C12 用 11 词保守元语言集 (分镜表/待补充/占位/作为AI 等) 扫 AIGC提示词/首帧描述/叙事目的/画面焦点——"上一镜尾帧" 等合法参考绑定措辞不在集内防误伤。
3. 覆盖轨: C06 Σ每镜时长 (契约 normalized duration_s) vs 声明总时长秒, 偏差 >±1% 记 FAIL (README T10 同口径); C07/C08 景别 <3 种 / 运镜 <2 种记塌缩 WARN; C09 从 brief `_场景描述` 提取锚词 (标点分句→功能字再切分→长片段补前 3 字块), 命中率 <60% 记 FAIL (README 维度 H 同口径); C13 先走 anti_ai_vocab.count_regex_hits 正则层, 未命中/缺模块再落 10 词保守罐头表逐镜兜底。
4. LLM 语义轨 (可选): 配置 AI 端点时经 pln_llm.call_ai_ex (temperature 0.2, timeout 120s) 发单次干净上下文审查——system 钉死审查员身份与严格 JSON 输出格式, user 只带 brief 摘要+产物 (截断 6000 字符并诚实标注)+结构检查已给发现 (防重复); json_loads_tolerant 解析, findings 限 12 条、severity 白名单归一、附加 source="llm"; 端点缺席/调用失败/不可解析均自动落回确定性轨并在「审查轨」行诚实标注原因。
5. 判例自检段: `knowledge_base/quality_precedents.py :: list_precedents()` 按条目 rule/self_check 与发现的清单关键词做子串对照 (R-xxx ↔ NP-yyy), 并列自检问题清单 (≤12 条); 判例库 import 失败/为空/结构不符时报告写 "判例库未就绪—跳过判例对照", 绝不编造 NP 引用。

## 参数表

| 参数 | 典型值 | 越界后果 |
|---|---|---|
| 被审产物 | Cinematic.分镜JSON | 纯文本/空产物时 C02-C09/C11 等结构项进「无法验证」; JSON 解析走宽容通道 (围栏/尾逗号), 但内容不改动 |
| 核心数据包 | Core.核心数据包 | 留空 → C09 场景锚定/C10 模式一致性进「无法验证」(缺输入不猜测); brief 无 ≥2 字场景片段 → C09 无法验证 |
| AI接口地址 | http://127.0.0.1:端口/v1 | 留空走确定性轨; 端点 500/超时/返回非 JSON → 「审查轨」行标注失败原因, 发现仍以确定性轨为准, 不阻塞报告 |
| AI密钥 / AI模型名 | 本地端点可空 | 与 Core 包 `_ai_api_url/_ai_api_key/_ai_api_model` 继承 (节点输入优先); SSRF 防护沿用 pln_llm 校验 |

## 已知坑

- LLM 轨发现不落检查点: 阶段结果有磁盘缓存, 但 LLM 语义发现每次现算——同产物重跑时报告 R 编号 (阶段发现在前、LLM 发现追加在后) 对结构发现稳定, 对 LLM 发现不保证逐字节一致; 要逐字节复现请不带 AI 端点跑。
- 场景锚定的锚词是子串匹配: brief 场景句过泛 (如 "夜景") 时命中率虚高、过细时可能误报 FAIL; 门槛 60% 与 tests/test_aigc_random_full.py 维度 H 同口径, 可交叉核对。
- 检查点跨产物互踩: CheckpointStore 清单按 step 键覆盖 (接口冻结粒度), 交替审查两个产物时同一 step 反复重算属预期; 每个阶段产物文件名含摘要前 16 位, 不会被另一产物串写。
- 空洞词表是保守集: anti_ai_vocab 正则层覆盖 masterpiece/8K 等套话, 但 "氛围感拉满" 式罐头仅 10 词兜底; C13 通过≠文风达标, 语义层面看 LLM 轨或判例 NP-004。

## 节点映射

- 实现文件：aggregator/review_engine.py
- 分支/函数：review_artifacts() MODE_STAGES["全量审查"]=("completeness","consistency","coverage") 分支 → _stage_completeness()/_stage_consistency()/_stage_coverage() → _llm_semantic_review() (call_ai_ex 轨) → _load_precedents() (判例自检) → _render_report()
- 数据来源：被审产物 + brief (parse_core_pack 核心数据包) + aggregator/storyboard_contract.py validate_storyboard() + anti_ai_vocab.count_regex_hits() + knowledge_base/quality_precedents.list_precedents() + CheckpointStore 落盘阶段产物
