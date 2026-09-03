# 🎬 ComfyUI-DirectorMaster

**导演级 AI 影视创作 ComfyUI 节点包** — 一句话创意 → 剧本 → 分镜 → AIGC 镜头级提示词，直供 Seedance / Wan / LTX / Hailuo / Sora 等主流视频生成模型。

`V17.0.0` · 19 注册节点（17 超级 + Final 别名 + 长篇接入，可选扩展至 65 节点） · 600 位真实导演风格库 · 247 创作模式（247 张模式卡全量入库） · 零第三方依赖

---

## 什么是 DirectorMaster

DirectorMaster 不是又一套提示词模板，而是一个**导演风格转译与创作引擎**：把 600 位真实导演的已知风格特征（镜头 / 光 / 节奏 / 色彩 / 表演 / 构图 / 声音 / 情绪 / 物件 / 年代等 12–17 维档案）与剧作方法论，转译成结构化剧本、分镜与视频模型提示词。选导演即锁定其风格——你拿到的不是一段罐头文案，而是一份带着导演思路的完整制作方案。

输出为 **AIGC 视频模型可直接消费的生产级提示词**：每镜生成七要素提示词（参考绑定 / 主体与动作 / 空间 / 镜头 / 视觉 / 音频 / 约束，遵循 Seedance 2.5 / Wan 3.0 官方手册范式）+ 首帧提示词 + 音频描述，并自动判别生产模式（参考视频 > 首尾帧 > 多参考图 > 首帧 > 文生）注入分镜 JSON 与交付 JSON。内置去 AI 味文本质量层（空洞词具象翻译 / 后缀去复读 / 元语言出清）与场景锚定引擎——分镜从你的输入场景里长出来，不跑题、不串场。

无论是否接入 AI 增强端点，全部 247 创作模式均可在确定性轨道上运行：无 mock、无占位、无硬编码空数据，降级路径诚实上报。

## 核心特性

- 🎥 **600 导演风格库**：真实导演 × 12–17 维档案（V15 扩容 66 位当代/跨界/非西方导演），模糊搜索（王家卫 / Kubrick / 诺兰 均可）
- 🧩 **叙事编排引擎**：正叙 / 倒叙(结果先行) / 穿插倒叙 / 穿插乱叙 / 循环叙事 × 单线 / 双线并行 / 三线交织 / POV 切换，确定性时序重排 + 时间线/线索图谱 + 导演批注 + 字幕位
- 🎯 **每镜七要素 AIGC 提示词**：+ 首帧提示词 + 音频三轴描述，分镜 JSON / 交付 JSON 双注入
- 📍 **场景锚定**：输入场景的地点 / 时间 / 天气 / 道具主导分镜生成，首尾场 100% 锚定、中间场相邻空间变体，极简/抽象/英文输入有语义兜底
- ✍️ **剧本引擎**：46 模式，30+ 真实叙事结构下场（三幕 / 五幕 / 救猫咪 15 拍 / 英雄之旅 / 皮克斯 22 条 / 双线 / 非线性…），结构硬指标达标（实测中点 48-53%、灵魂黑夜 68-76%、高潮 76-84%，T10 断言覆盖）
- 🎬 **分镜引擎**：63 模式，节奏大师系统（快闪 / 长镜 / 蒙太奇 / 慢镜 4 类 21 种节奏风格），镜头语法指纹 63/63 唯一，总时长恒覆盖片长（±1% 内）
- 🧠 **AI 增强轨**：任意节点可接 OpenAI 兼容端点做剧本/分镜润色，内置质量门控（长度门 / 照抄检测 / 反 AI 套话扫描 / SSRF 防护），无端点时自动走确定性模板轨。V16.2.0 起增加 LLM 链路健壮性层：provider 预设注册表（内置 10 厂商 + 用户覆盖）、三态降级状态机（连续失败自动切备用端点、冷却后探测恢复）、上下文溢出两层压缩、上游截断检测与拆分重试、节点加载崩溃隔离（单模块损坏不拖垮整包）
- 🎭 **形态专精**：短视频 / 动漫 / 绘本 / MV / 广告 / 纪录片 / 互动剧 / 直播等 24 种形态各有专属场次骨架；长片遵循影视特性、短片遵循短视频特性
- 🗂️ **归档与版本控制**：真实写盘 + 磁盘持久化版本库（blob 去重 + gzip，并发安全），回滚逐字节还原，TXT / JSON / MD / HTML 多格式导出

## 快速上手

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Nurburgring-Zhang/ComfyUI-DirectorMaster.git
```

重启 ComfyUI 即可使用 19 个 DirectorMaster 节点。无第三方依赖（可选 torch/PIL/numpy 用于 IMAGE 参考槽）。

安装后自检：

```bash
cd ComfyUI-DirectorMaster
python doctor.py   # 9 类诊断：安装路径 / Python 环境 / 模块导入 / 节点注册 / 知识库完整性 / 复活接线消费验证 / V15.0 引擎运行时消费验证 / 加载隔离与 LLM 容错 / 模式卡与分镜契约一致性
```

最小链路：

```
DirectorMasterCore → DirectorMasterScript → DirectorMasterCinematic → DirectorMasterSummary → DirectorMasterArchive
```

1. **DirectorMasterCore**：填项目名/导演/场景/情绪等 11 维，输出统一电影提示词 + 核心数据包
2. 下游节点用 forceInput 槽接核心数据包，按需接剧本/创意/美术/声音/角色/资产六维上游
3. **DirectorMasterSummary** 汇总为完整制作手册 + JSON 交付包
4. **DirectorMasterArchive** 写盘归档，可做版本提交/对比/回滚/选优

现成工作流在 `workflows/`：`MINIMAL_PIPELINE_V8.2.json`（最小管线）、`MEGA_PIPELINE_V8.3.json`（全链路）。

## 19 节点

| 节点 | 能力 |
|---|---|
| DirectorMasterCore | 起点：统一电影提示词 + 核心数据包（11 维 + 600 导演库） |
| DirectorMasterScript | 剧本 46 模式（长片/短剧/短视频/动漫/绘本/MV/广告/纪录片/互动剧/钩子/对白/角色弧） |
| DirectorMasterVibe | 创意 23 模式（15 创意 + 8 设计：电商/海报/品牌/PPT/图表/三视图/爆炸图/流水线图） |
| DirectorMasterArt | 美术 3 模式（美术指导/空间一致性/空间布局） |
| DirectorMasterSound | 声音 4 模式（声音设计/音乐/声音层/沉默） |
| DirectorMasterCinematic | 分镜 63 模式（电影工作室/节奏大师/短剧/动漫/绘本/MV/广告/纪录片分镜） |
| DirectorMasterCharacters | 角色 42 模式（角色/环境/服化道/参考图 → 6 路输出） |
| DirectorMasterAsset | 资产 41 模式（含 HellGrind 资产库 → IP-Adapter/参考图锁定） |
| DirectorMasterSummary | 终极汇总 3 路（完整制作手册/JSON 交付包/项目索引） |
| DirectorMasterRouter | 通用路由（7 目标模型，H3 深度 IR 5 模式 + EDL） |
| DirectorMasterVideoRouter | 5 视频模型超级路由（Seedance/LTX/Wan/Hailuo/Sora） |
| DirectorMasterArchive | 归档（真实写盘 + 磁盘持久化版本控制 + TXT/JSON/MD/HTML 格式多选） |
| DirectorMasterCoCreator | AI 共创循环：故事核心→3方向分支→门阵→精炼→共创剧本（含方向分支图JSON+创作日志） |
| DirectorMasterSoul | 灵魂注入：创作者体验→母题派生→灵魂层注入剧本（含灵魂片段报告） |
| DirectorMasterIntuition | 直觉修改：分镜JSON→确定性反常规镜头语法（含修改日志） |
| DirectorMasterFusion | 风格融合：主0.6/次0.3/反0.1 确定性融合，反风格提取突破指令（含元数据JSON） |
| DirectorMasterFinal | Summary 兼容别名 |
| DirectorMasterReview | 独立审查：干净上下文 13 项清单核对（快速结构审查/全量审查/对比分镜），编号化报告（R-001 起，附镜头号/字段证据）+「无法验证」显式标注，多阶段 CheckpointStore 断点续跑，判例库自检引用，可选 LLM 语义轨 |
| DirectorMasterNovelIntake | 长篇分集接入：小说原文 → 分集产物（章节感知切分 + 覆盖账本 Σ 校验 + 锚点回溯 + 三指标钩子 + CheckpointStore 断点续跑 + dm_memory 记忆桥），输出人读接入报告 + 管线 JSON（每集 9 键产物含 core_pack_seed） |

另有 46 个 legacy 细粒度节点可选兼容层（V16.0.1 恢复）：设置环境变量 `DIRECTORMASTER_LEGACY_NODES=1` 后加载 65 节点（19 注册 + 46 legacy），0 加载错误；默认不加载。

## 数据聚合（真实消费，非装饰）

600 导演 12/17 维档案、120 影视场景库、15 大师剧本 DNA、25 故事感总纲、儿童年龄分级、14 真实短剧案例、Seedance 2.5 能力边界、Higgsfield 6 份项目记忆文档、CINEDANCE 15 块视觉骨架、AIGC 42 环节 + 留白/运镜三定律、大师级影视语言原则、8 设计模式系统。全部惰性导入 + 异常降级（stderr 诚实上报），缺失零影响。

## 质量验证（实测指标）

- 全模式执行：261 个下拉选项全通过（247 创作模式为审定口径：剔除随机项/聚合项/别名重复，逐条理由见 tests/mode_manifest.json 排除审计表），唯一输出按节点实测 46/23/3/4/63/42/41/7/5/10/3（Script/Vibe/Art/Sound/Cine/Chars/Asset/Router/VideoRouter/Archive/Review，逐项相加=247，含 DirectorMasterReview 3）
- AIGC 场景贴合：40 例全量随机测试 A–H 八维断言 PASS=543 FAIL=0（证据存档 tests/aigc_random_full_results.json；维度 H：≥60% 镜头提示词命中输入场景锚点）
- Cinematic 镜头语法指纹（景别/运镜/焦段/时长）：63/63 唯一（含 4 个同节奏簇）
- 同档期形态模式正文相似度：0.295-0.606（16 对实测，最大为纪录片对，门槛 <0.7）
- 互动剧分支树：可解析 JSON，2 选择点 × ≥2 选项，3 结局，零悬空引用
- 版本存储：commit/state/tag/diff/rollback 全操作实测，回滚逐字节还原（sha256 校验）；19 个版本（含 8 线程×2 并发提交）仅 2458 B（blob 去重 + gzip，T7 实测记录）；并发零丢失为 T7 实测断言（16/16 可取回、内容 sha 逐一相符、历史数精确）
- 时长覆盖：90min 核心包分镜总时长实测偏差 0.16%（T10 断言 ±1% 内）
- 浮点伪影：0（情感强度/张力/节拍表统一 1 位小数）
- 结构硬指标：中点 48-53%、灵魂黑夜 68-76%（含此节拍的结构）、高潮 76-84%（T10 四结构断言全过）
- 安全：SSRF 防护（link-local/云 metadata 禁止 + DNS 解析失败即拒 + 校验后 IP 钉扎直连 + 禁重定向 + 显式禁用环境代理）、归档路径消毒
- LLM 链路故障注入（V16.2.0 批次1）：110 断言全过 / FAIL=0 —— 退避重试、同端点与跨端点降级、冷却探测恢复与回落、溢出两层压缩（含压缩耗尽跨级）、上游截断拆分重试、终端类错误不计降级阈值、围栏 JSON 宽容抢救、4 线程并发状态机无撕裂、SSRF 链级拦截（含 IPv4 兼容 IPv6 形态）；真实 HTTP 服务器 + 确定性时钟注入，证据存档 tests/llm_resilience_results.json
- 加载崩溃隔离（V16.2.0 批次1）：19 断言全过 / FAIL=0 —— 19 注册节点黑盒核验、坏模块/坏类名故障注入按 import/getattr 分相入隔离清单且好节点不拖垮、版本三处一致（__version__/pyproject/README）；证据存档 tests/load_isolation_results.json
- 独立对抗验证（V16.3.0）：12 断言全过 / FAIL=0 —— 全节点 × 1100+ 次畸形输入（超长/Unicode/控制字符/畸形 JSON/异常种子）零崩溃；种子语义属性测试（种子0真随机非恒定、固定种子全链逐字节可复现、多种子分布多样）；独立口径复测导演库规模/唯一性/档案维度；final_capability_audit 30 轮全随机链路审计全部通过
- 模式卡语料与索引（V16.6.0 批次2）：244/244 卡与 manifest 对账零漂移（tools/sync_mode_index.py --check）；孤儿卡/缺必填字段/错目录/名称错配/索引漂移 5 类负样本硬失败实测复现（8 断言全过）；实现指针双盲抽查 29 卡 × 10 目录全命中
- 分镜 JSON 契约 v1→v2（批次2 起，批次6 升 v2）：83 断言全过 / FAIL=0 —— 14 诊断码可达（含相对引用环检测、槽位双射/越界拦截）、对抗输入零异常逃逸（解析永不抛）、normalize 逐字节确定、v1 文件结构零漂移；V16.4/V16.5/V16.8 增量键已吸收进契约注册表；manifest↔卡↔live 枚举三方一致性 doctor 第 9 类全过；证据存档 tests/storyboard_contract_results.json
- 独立审查引擎（V16.7.0 批次3 D6）：确定性轨 13 项清单核对（结构自检复用分镜契约 v1 诊断 + 规则核对：镜数/时长覆盖/字段完整/景别运镜多样性/场景锚定 60% 门槛/重复手法/元语言/空洞词）、编号化报告 R-001 起（每条附镜头号/字段证据）、「无法验证」显式标注（缺输入不猜测）、CheckpointStore 断点续跑（中断重入已完成阶段跳过、输入变更自动失效重算）、LLM 语义轨本地 OpenAI 兼容服务器实测、判例库缺位诚实降级——tests/test_review_node.py 全过
- 角色 DNA 档案（V16.8.0 批次6）：8 维（眼型/脸型/发型/发色/肤色/体态/标志着装/气质锚）+ 禁词表 36 词拒绝抽象词（"神秘/高级"类不落档、计数入证据）；跨镜注入（角色卡→每镜提示词）；prompt block 超限按段边界截断不腰斩；merge 基座维度同管线禁词+白名单复核（同输入同判定）——tests/test_character_dna.py 54 断言全过；项目风格锚 `_项目风格锚` 确定性拼装经 core 包与第 3 路输出双通道下发，资产台账/视频路由/角色卡/cinematic 4 消费方条件注入缺键零漂移（golden 回放钉死锚字段）
- 资产派生谱系（V16.8.0 批次6）：version_store 快照台账 + 四态词汇表（完整锚定/母版缺失/派生缺失/母版已更新待同步）；母版变更但快照入库失败时诚实标"待同步"绝不伪造一致性；首次入库/滞后/派生失效各有自解释说明；滞后确认不重复入库——tests/test_asset_lineage.py 57 断言全过
- 视频路由槽位协议（V16.8.0 批次6）：Seedance 2.5 reference_images 按参考槽位升序注入；槽位映射折入载荷（槽位→数组下标 1:1、镜头槽位逐镜记录、prompt 标签核对）；缺槽（负数/越界）诚实跳过逐槽说明，绝不伪造占位；非法元素（str/bool）未入计划但如实记录"损坏元素"，双射硬校验归契约层——tests/test_contract_v2.py 58 断言全过
- 时长口径统一（V16.8.0 批次6）：4 模式时长口径统一修复；plot_topology 时长归一对 NaN/Inf 病态输入守卫（诚实返回不扩散）；前镜时长断裂链诚实断开——tests/test_duration_consistency.py 27 断言全过

## 测试

```bash
python doctor.py                     # 9 类自检
python tests/test_all_modes.py       # 19 节点 × 全模式回归 (283 断言)
python tests/test_episode_node.py    # 批次7 长篇接入节点 (注册/形状/运行时/诚实失败/输出目录兜底)
python tests/test_review_node.py     # V16.7.0 独立审查引擎 (确定性轨/编号报告/断点续跑/LLM 轨/无法验证/判例降级)
python tests/test_aigc_random_full.py # 40 例全量随机 AIGC 测试 (A–H 八维, 含场景贴合度)
python tests/test_workflows.py       # 工作流 JSON 有效性
python tests/ten_rounds.py           # 十轮全量测试 (43 断言: 部署/功能/数据/链路/AI/质量)
python tests/f2_ai_track_e2e.py      # AI 轨端到端 (本地 OpenAI 兼容服务器, 真实 HTTP)
python tests/test_llm_resilience.py  # V16.2.0 LLM 链路健壮性故障注入 (110 断言, 真实 HTTP + 确定性状态机)
python tests/test_load_isolation.py  # V16.2.0 加载崩溃隔离机制 + 版本口径一致性 (19 断言)
python tests/test_adversarial.py     # V16.3.0 独立对抗验证 (12 断言: 模糊输入/种子语义/独立口径)
python tests/test_random_full_v16.py # V16.4.0 全量随机+叙事拓扑 (73 断言)
python tests/test_matrix_full.py     # V16.5.0 全维度矩阵 (71 用例: 时长×题材×叙事×主角×导演×视觉×运镜×LLM)
python tools/sync_mode_index.py --check  # 模式卡索引一致性 (孤儿/缺卡/漂移硬失败)
python tests/test_storyboard_contract.py # 分镜 JSON 契约 v2 口径 (83 断言, 对抗输入零异常逃逸, v1 零漂移)
python tests/test_contract_v2.py     # 批次6 契约v2槽位协议 (58 断言, 双射/越界/稀疏库/非法元素点名)
python tests/test_contract_render.py  # 契约渲染层 (35 断言, 契约JSON→提示词确定性)
python tests/test_character_dna.py   # 批次6 角色DNA档案 (54 断言, 禁词表/跨镜注入/段边界截断)
python tests/test_asset_lineage.py   # 批次6 资产派生谱系 (57 断言, 四态词汇/快照台账/入库失败不伪造一致性)
python tests/test_duration_consistency.py # 批次6 4模式时长口径统一 (27 断言, NaN/Inf守卫)
python tests/test_golden_replay.py   # golden 回放 (20 断言, 固定种子42结构零漂移)
python tests/test_review_node.py     # 独立审查节点 (66 断言, 确定性轨+LLM轨)
python tests/test_mode_dedup.py      # 卖点映射+手法去重 (34 断言)
python tests/test_pipeline_checkpoint.py # 产物检查点 (51 断言, 断点续跑)
python tests/test_impact_analysis.py # 修订影响面 (61 断言)
python tests/d1_grammar_probe.py     # 同簇镜头语法唯一性
python tests/d2_similarity_probe.py  # 形态模式正文相似度
```

## 目录结构

```
├── __init__.py              # 19 节点注册 (17 超级 + Final 别名 + 长篇接入)
├── doctor.py                # 安装自检
├── aggregator/              # 超级节点 + 引擎 (场景/节拍/节奏/长片/LLM/AIGC提示词/叙事编排/版本存储/格式导出)
├── knowledge_base/          # 知识库子模块 (摄影/叙事/类型/表演/镜头语汇/转场…)
├── workflows/               # 现行管线 (MINIMAL/MEGA) + legacy 存档
├── tests/                   # 回归与探针测试
└── docs/                    # 历史开发文档
```

---

## 版本历史

### V17.0.0（批次7：长篇输入管线）

- **来源与政策**：延续零代码借鉴纪律（wind-comic 章节切分思想 / lumenx 两段式与锚点切分思想，思想层独立重写，cue 词表与指标定义全为本仓独立定义），零第三方依赖不变（仅 stdlib）。产物为数据层分集文件，不产像素，与既有模式面 additive 并存，既有 18 节点输出零改动。
- **确定性切分与覆盖账本**：`aggregator/episode_pipeline/` 8 模块——splitter 章节贪心 + 段落二分（禁句内断）；ledger 覆盖账本 Σ(分集 span + 非分集归类段) == len(text) 硬约束，任何未归类字符（BOM/CRLF/全角空格先记账后归类不吞字符）fail loud 不静默丢，根除长文本静默截断。
- **锚点回溯**：anchors 每集 3 个 ≤20 字原文锚点（句首/段首优先，按集内位置首/中/尾散布），traceback 精确 + 归一化（剥空白 substring）双路径核验偏移；伪造/篡改 → 0 命中拦截，引文真实但偏移错位 → offset_mismatch 拦截，畸形偏移声明（str/None/float/bool）同按 offset_mismatch 拦截（完全无 start/end 键才视为无主张）。
- **钩子三指标与 LLM 可选轨**：hooks m1 悬念 / m2 主角赌注 / m3 新揭示，确定性启发式（自写 cue 词表，非语义理解），flags 只标记不阻断、阈值常量可调；llm_refine 可选精拆轨只写注释字段（logline/refined_scenes 标 llm_generated），原文 span/text 不可变，无凭据时 llm_track=unavailable 诚实降级。
- **断点续跑与记忆桥**：pipeline 断点续跑复用批次3 CheckpointStore（pipeline_id=sha1(text)[:16]，跳集只跳过逐集产物生成，账本/锚点以全量重算与逐集核验为准）；memory_bridge 消费 dm_memory series 档案/锚点/注入，缺记忆目录管线产物逐字节零漂移（批次4 T7 口径 additive 硬断言）。
- **节点**：新增 `DirectorMasterNovelIntake`（长篇小说 → 分集数据包），注册 18 → 19（映射 tuple/显示名/docstring 三处 + doctor + dump_mode_manifest 同步联动）。
- **质量与双盲**：三新套件 248 断言全过（split 96 / hooks 115 / node 37），100k 字端到端实测 0.376s（验收线 <5s）；双盲互审 3 轮闭环（R1 双通道 9 项 → 修复 → R2 对抗审计 + 闭环核验 → R2A-02 畸形偏移声明修复 + 全矩阵复跑 → R3 收尾），零 HIGH/MED 残留。
- **注册口径**：19 注册节点 / 247 创作模式不变；版本三处口径 17.0.0（__version__/pyproject/README）。

### V16.9.0-MERGED（批次4：记忆层）

- **来源与政策**：延续零代码借鉴纪律（六仓二轮经验思想层独立重写），零第三方依赖不变（仅 stdlib）。节点拓扑与下拉口径零改动（记忆层为纯库模块，不新增节点）。
- **四域记忆与信任注入**：`aggregator/dm_memory/` 10 模块——决策卡（shot_cards，脱敏后 digest 稳定 card_id + 原子追加）、偏好（preference_store 六分支 + verify_counts 计数自校验）、程序性记忆（procedure_memory）、进化日志（evolution 阈值记账 maybe_reflect 确定性提议，失败永不致命）；检索（retrieval 词频索引召回）；风格圣经（style_bible）与系列继承（series_inherit 世界观/风格锚/DNA 跨项目长存 + anchor_link 锚点联动）；cinematic_studio 出口 additive 信任注入（rounds 信任序 + 已验证卡），缺记忆目录输出逐字节零漂移（T7 硬断言）。
- **脱敏层**：redact_free_text 手机号/邮箱/API 密钥/Bearer/JWT 正则脱敏；决策卡/偏好/程序性/series 四条自由文本写路径全接线，先脱敏后哈希后落盘（card_id 哈希稳定）；永不致命（内部异常原样放行 + stderr 降级）；结构字段保护（seed/镜号/counts 等结构键不误伤）。
- **管线韧性**：_safe_name 同源碰撞防护（含 ASCII 字母/尾点尾空格名追加 sha1 后缀，9 处副本同步——NTFS 大小写折叠/Windows 剥尾点/保留名不再跨项目串档）；preference 二级结构损坏逐元素过滤自愈（好条目存活，不隔离整个文件）；evolution.jsonl 二进制容错解码 + stderr 诚实告警（损坏不再静默锁死记账）；幽灵卡软过滤（缺卡片标识字段的损坏行不入列表与检索索引）。
- **质量与双盲**：三套件 264 断言全过（core 131 / retrieve 61 / bible 72），T7 additive 零漂移硬断言保持绿；双盲互审 3 轮闭环（R1 两通道 1 HIGH+4 MED → 修复 → R2 对抗审计 4 MED+6 LOW → 修复 → R3 复攻 111 项探针 PASS），零 HIGH/MED 残留；3 项已知 LOW 取舍留档（超深/循环容器整体放行、redaction 高召回残余误伤、card_id 型幽灵行绕过有界）。
- **注册口径**：18 注册节点 / 247 创作模式不变；版本三处口径 16.9.0（__version__/pyproject/README）。

### V16.8.0-MERGED（批次6：一致性资产化）

- **来源与政策**：延续零代码借鉴纪律（六仓二轮经验思想层独立重写），零第三方依赖不变（仅 stdlib，本批新增 hashlib/re/math 均标准库）。
- **角色 DNA 档**：8 维档案（眼型/脸型/发型/发色/肤色/体态/标志着装/气质锚）+ 禁词表 36 词（"神秘/高级"类抽象词不落档、计数入证据）；跨镜注入；prompt block 超限按段边界截断（回退最近分号，段完整不腰斩）；merge 基座维度过同管线禁词+白名单复核（build 与 merge 同输入同判定）——tests/test_character_dna.py 54 断言全过。
- **项目风格锚**：`_项目风格锚` 导演风格确定性拼装（空段跳过、全空缺省串），core 包 + 第 3 路输出双通道下发；资产台账/视频路由/角色卡/cinematic 4 消费方统一 .get 条件注入，缺键零漂移（golden 回放钉死锚字段）。
- **分镜契约 v2**：contract_version=2（合法集 {1,2}，生产链仍按 v1 兼容章输出），锚定库 + 每镜 参考槽位/锚定/机位锚 新增；诊断码 11→14；槽位↔prompt【参考@N】标签双射校验（非整数元素逐个点名）+ 库大小=整数键最大值+1（稀疏键不误报）；v1 文件结构零漂移——test_contract_v2.py 58 断言 + test_storyboard_contract.py 83 断言全过。
- **资产派生谱系**：version_store 快照台账 + 四态词汇表（完整锚定/母版缺失/派生缺失/母版已更新待同步）；母版变更但快照入库失败时诚实标"待同步"，绝不伪造一致性；首次入库/滞后/派生失效各有自解释说明；滞后确认快照不重复入库——tests/test_asset_lineage.py 57 断言全过。
- **视频路由槽位协议**：Seedance 2.5 reference_images 按参考槽位升序注入；槽位映射折入载荷（槽位→数组下标 1:1、镜头槽位逐镜记录、prompt 标签核对）；缺槽（负数/越界）诚实跳过逐槽说明，绝不伪造占位；非法元素（str/bool）未入计划但如实记录"损坏元素"，双射硬校验归契约层。
- **时长口径统一**：4 模式时长口径统一修复；plot_topology 时长归一对 NaN/Inf 病态输入守卫（诚实返回不扩散）；前镜时长断裂链诚实断开——tests/test_duration_consistency.py 27 断言全过。
- **注册口径**：18 注册节点 / 247 创作模式不变；版本三处口径 16.8.0（__version__/pyproject/README）。

### V16.7.0-MERGED（批次3：质量闭环 + 管线韧性）

- **来源与政策**：延续零代码借鉴纪律（ViMax 断点续跑/参照重选、lumenx echo 检测与 slot 思想、wind-comic stale 传播与反假绿测试、STAGE「结构化≠生成有效」警告、H3-Promptor「代码守契约」——均思想层独立重写），零第三方依赖不变（仅 stdlib，新增 difflib）。
- **质量闭环**：独立审查节点 DirectorMasterReview（干净上下文 13 项清单、编号化报告 R-001 起逐条附镜号/字段证据、确定性轨无端点可用、LLM 轨可选、CheckpointStore 断点续跑）；提示词质量判例库 NP-001~012（每条含真实证据指针，脸崩/文字糊类诚实标注"预防性判例"）；golden 回放（固定种子 42，结构级+64 字符锚零漂移，--regen 显式再生成）；卖点→镜头位映射（漏拍即提示）+ 手法去重校验（同运镜/构图不得连续两镜当主角）。
- **管线韧性**：产物检查点 CheckpointStore（逐产物存在即跳过、input_hash 变更自动失效重算、Win32 os.replace 有界重试）；修订影响面分析（核心包 diff→受影响下游清单，Archive 提交时对比上一版附 impact 段，只提示不自动执行）；LLM echo 回声检测（difflib ≥0.95 拒收降级）；LLM 经济性模式（system 字节级冻结开关 freeze_system，动态信息外置 [RUN] 段）。
- **契约与渲染**：契约注册表吸收批次3 顶层键"手法去重"（19 顶层键）；新增契约渲染层（契约 JSON→每镜七要素提示词确定性渲染，SEEDANCE_25/WAN_30/GENERIC 三视图，STAGE 警告的落地对策）。
- **注册口径**：18 注册节点（17 超级 + Final 别名），247 创作模式/247 张模式卡（manifest 同步吸收 Review 节点 3 模式）。
- **回归基线**：并集回归 22 项全绿（280/543/43/18/11/117/19/82/12/73/71用例/35/20/66/34/51/61 断言 + audit/probe/d1/d2 + doctor 0 错误）；双盲互审 2 轮闭环（R1 双通道 conditional→修复 8 项→R2 approve 零 HIGH/MED 残留）。

### V16.6.0-MERGED（批次2：知识资产工程 + 分镜契约基座；并入他端 V16.3-V16.5 迭代后顺延编号）

- **来源与政策**：延续六仓集成**零代码借鉴**纪律（video-shotcraft 配方卡组织法、hyperframes 契约工程思路独立重写），零第三方依赖不变（仅 stdlib）；节点拓扑与下拉口径零改动。本批与另一端从同一批次1 基线并行演进（对端 V16.3 随机诚实化 / V16.4 情节拓扑 / V16.5 场景实体），变基整合后版本顺延 16.6.0。
- **模式卡语料 244 张全量入库**：10 个节点下拉的全部创作模式逐张建卡（frontmatter 八键：mode_id/node/name/one_liner/applicable/intensity/style_tags/aliases；正文五节：意图 / 核心手法 / 参数表「典型值+越界后果」/ 已知坑 / 节点映射实现指针）；单一事实源 `tests/mode_manifest.json`（真实 INPUT_TYPES 探针生成 + 排除审计表：随机项/聚合项/别名重复逐条给理由）。创作模式口径由旧文案"246+"修正为审定值 244（诚实阀门：审计与文案不符时改文案，不凑数字）。
- **索引自动生成 + 硬失败门禁**：`tools/sync_mode_index.py` 生成 INDEX.md / index.json（确定性、无时间戳），`--check` 全量零漂移；孤儿卡 / 缺必填字段 / 错目录 / 名称与 manifest 错配 / 索引漂移五类违例一律 exit 1。
- **doctor 第 9 类诊断**："模式卡与分镜契约一致性"——manifest 三方对账（manifest ↔ 卡文件 ↔ live INPUT_TYPES 枚举）+ 索引零漂移 + 契约 v1 自检，与既有 8 类共存。
- **分镜 JSON 契约 v1**：`aggregator/storyboard_contract.py`（STORYBOARD_CONTRACT_VERSION=1）——canonical/derived/legacy 三态字段、11 个结构化诊断码、相对镜头表达式（上一镜 end ± 偏移，拓扑解析 + 环检测）、宽容解析器永不抛异常；Cinematic 接线为 additive（产物仅新增 contract_version 键，分镜文本逐字节不变）。
- **双盲互审 2 轮闭环**：R1 功能通道（HIGH3/MED2/LOW2）+ 一致性通道（MED1/LOW2）全部修复（8 卡文案 + 契约 None 守卫 + T20×5 回归钉），R2 双通道 approve 零新发现。

### V16.5.0（场景实体引擎：真实素材设计范式，对齐生产级提示词标准）

- **质量基准**：以真实生产级 AI 视频提示词标准库（Mx-Shell 生产模板 + 真实素材设计 Skill + Seedance/Wan 官方范式）为准绳，构建 `tests/test_matrix_full.py` 全维度矩阵（71 用例：12 时长档 × 16 题材 × 12 叙事组合 × 4 主角配置 × 8 导演 × 13 视觉调性 × 运镜演变 × 有/无 LLM），**71/71 全 PASS**。
- **场景实体引擎**（新增 `aggregator/scene_entity.py`）：从用户场景句提取 角色/道具/地点/天气/色彩/动作（后缀词典启发式），驱动分镜画面内容、剧本角色、AIGC 角色锚、POV、音频——**消灭罐头句**（修复"女机甲战士"场景产出"辣椒酱/女儿/护士"的内容脱节：修复后机甲 143 次命中、罐头角色 0 次；父女厨房等经典场景罐头池服务不受影响）。
- **设备美学包**（素材身份）：IMAX 实拍 / 暗调数字（威尼斯+K35）/ 暖色胶片（ARRICAM+Cooke）/ 复古港片 / 手机竖屏 / 纪录观察 / 压抑写实 / DV 怀旧 / 风格化动画——每包含摄影机+镜头+画质缺陷+素材身份声明（"这是一段 IMAX 实拍电影素材，不是广告片"）。
- **五段结构外壳**：核心主题 / 人物与基础设定（每主体≥2 瑕疵锚点）/ 氛围与画质（呼吸感手持）/ 镜头控制 / 声音（同期声+显式枚举）+ 结尾克制 + 模型建议 + 自检清单；≤20s 输出按秒切时间轴（[0-3s·凝视] 式，写法A）。
- **电影学修正**：焦段-景别匹配（特写 85-135mm/全景 24-35mm，消灭"中近景 12mm"）；每镜构图四件套；首帧描述真实化（不再是阶段名）；音效从天气/地点/道具派生（暴雨砸击声、缆绳吱呀、能量低频嗡鸣…）。
- **空洞词清洗**：罐头池"震撼/史诗感拉满/4K/8K/温馨/治愈系"等 12 类空洞词清除，改用具体可拍描述（附件标准："用具体动作传达情绪"）。

### V16.4.0（情节拓扑引擎：吸收 V16.6-AIGC 参考版真实增量）

- **来源与裁决**：对附件版（自称 V16.6-AIGC，内部口径四处矛盾）完成独立审计后裁决：本基座更完善（该版本自带 final_capability_audit 17 项 FAIL、删除了 3 个测试套件、无 V16.2 加固、整体删除 legacy 层），仅吸收其两件真实增值并按本基座 schema 独立重写。详见 `docs/VERSION_COMPARE_V16.3_vs_V16.6AIGC.md`。
- **情节拓扑引擎**（新增 `aggregator/plot_topology.py`，全确定性）：波浪式小高潮（一波高过一波）/ 反转点（位于波谷）/ 层层递进 推断；**复杂叙事结构**：套层叙事（戏中戏框架带）/ 罗生门（多视角版本带）/ 时间循环（循环区谷底逐次抬升+破局）/ 环形叙事（首尾闭环带），支持场景关键词自动推断与手动档。Cinematic 新增 optional 输入 `复杂叙事结构`（旧工作流零破坏）。
- **分镜 JSON 增量**（纯新增键，不改既有 schema）：`meta.叙事拓扑` + 每镜 `叙事标签` / `节奏手记` / `拓扑张力`。
- **时长归一修复**：阶段+张力驱动时长重塑 + 三步精确闭合，总时长精确覆盖用户请求预算——兑现 目标时长 输入"总时长恒覆盖片长"的既有承诺（此前 45 分钟请求被量化到 30 分钟桶，偏差最高 33%）。实测默认 90 分钟包偏差从 0.16% 级保持、任意请求时长 ≤8% 内（多数 <0.5%）。
- **景别阶梯兜底**：短档位景别塌缩（唯一值 <3 种）时按 阶段带（建立广角/发展中景/高潮紧密/收束拉远）轮换，相邻不重复；用户显式 景别偏好 仍最优先。
- **新增测试** `tests/test_random_full_v16.py`（73 断言，移植参考版高价值维度）：时长归一 ≤8%、时长/景别多样性、张力跨度、相邻焦点重复 ≤15%、四复杂结构端到端、拓扑确定性、零英文 AI 套话。首轮运行即暴露基座 3 类真实缺口（时长量化/多样性/标签覆盖），全部修复后 73 全绿。

### V16.3.0（随机引擎诚实化 + 全链种子驱动 + 独立对抗验证层）

- **🎲 随机引擎诚实化（P0 修复）**：修复 V16.1 引入的"随机名不副实"——旧实现以 `MD5(项目名_场景描述)` 为种子，相同输入下 30 轮"🎲 随机"恒定输出同一位导演（项目自带 final_capability_audit 4 项失败：导演去重 1/30、剧本指纹 22/30、分镜指纹 28/30、镜头语法重复率 29.4%）。新实现：Core 节点新增 **随机种子** INT 控件（`control_after_generate=randomize`，与 KSampler 同款交互）——**种子 0 = 每次执行 OS 熵真随机**；**种子 >0 = 固定种子全链完全可复现**（保留 V16.1 的可复现能力，显式可选）。
- **全链种子传播**：种子写入核心数据包 `_随机种子` 字段；Script/Cinematic/Vibe/Art/Sound/Characters/Asset/Router/VideoRouter/Archive/V15 四节点的全部 🎲 下拉（模式选择/属性/风险档位/直觉档位/市场推断等 30+ 站点）统一改为按 `md5(种子|域盐)` 派生子种子驱动（各域独立盐，互不串扰）；下游节点无核心包单独排队时回退全局随机（向后兼容）。消除旧版 Core 确定性 vs 下游全局随机"三处两制"的不一致。
- **修复后实测**：final_capability_audit 全部通过（30 轮全随机链路）；全量回归 11 套件无退化。
- **Intuition 引擎健壮性修复**：畸形 `分镜JSON`（分镜表为字符串/元素非 dict）不再崩溃，原样诚实返回（由新增对抗测试发现）。
- **独立对抗验证层**：新增 `tests/test_adversarial.py`（12 断言）——全节点 × 1100+ 次畸形输入零崩溃、种子语义属性测试（真随机非恒定/固定种子逐字节复现/多种子分布多样）、独立口径复测导演库规模/唯一性/档案维度。
- **诚实审计文档**：新增 `docs/LEGACY_AUDIT.md`（AST 全仓依赖图：29 活跃引擎 / 8 legacy 内部链 / 3 真死代码 director_pro+director_engine+engine_story_arc / 3 独立工具）；V6/V7 时代过时文档（WORKFLOW_DOC_V6.1 等 4 份）加历史文档横幅。真死代码处置留待维护者裁决，本轮不删除。

### V16.2.0-MERGED（批次1：LLM 链路健壮性加固 + 加载崩溃隔离）

- **来源与政策**：集成 openclacky / memorax-code / video-shotcraft / OpenMontage / hyperframes / Xed-Editor 六仓的优秀经验与方法。执行**零代码借鉴**（最严边界）——只学习思想/方法/SOP/结构，全部能力用 Python 独立重写，未复制任何一行外部代码；保持零第三方依赖纪律（仅 stdlib），不引入任何新运行时依赖。
- **provider 预设注册表**：内置 10 厂商预设（openai / deepseek / moonshot / 智谱GLM / 百炼DashScope / minimax / siliconflow / openrouter / ollama / lmstudio），含匹配主机、key 环境变量提示、能力标注与同端点备用模型；`llm_presets.user.json` 可覆盖/扩展（坏文件只警告不阻断）。模型谱系更新快的厂商不内置过时清单，诚实留空由用户覆盖。
- **三态降级状态机**：primary_ok / fallback_active / probing。主端点连续 3 次阈值类失败（可重试类 + OVERFLOW；AUTH/TRUNCATION 等终端类不计入，避免配置/内容级错误引发无意义降级重放）→ 自动切备用端点；冷却 60s 后下一次调用先单次探测主端点，成功则恢复（recovered），失败则回落并重置冷却，探测状态滞留超冷却自动回落（防永久卡在 probing）。AUTH/BAD_REQUEST 属配置级错误，不跳级直接诚实报错；OVERFLOW 压缩后仍可跨级（备用模型上下文可能更大）；TRUNCATION/PROTOCOL 属内容级问题，不触发跨级。
- **溢出两层压缩**：上下文溢出时按 gentle（保留头尾各 25%）→ aggressive（各 12.5%）逐级压缩重试，插入"[…中段内容已省略]"标记；短于 400 字符不可压即如实报错，不伪造。
- **上游截断检测**：识别 finish_reason=length / 空内容 / 200 非 JSON 等截断形态，自动注入 [SYSTEM] 拆分提示重试（每次调用最多 2 次），仍截断则诚实报"上游截断诊断"，不再静默返回空成功。
- **字段别名四级容错 + 宽容 JSON**：LLM 交付 JSON 字段漂移（精确→忽略大小写→中英别名表→归一化键）四级解析；宽容 JSON 解析支持代码围栏、尾逗号、尾部噪声、截断抢救。
- **加载崩溃隔离**：16 个超级节点改为逐项加载，单模块/类加载失败记入 `DM_QUARANTINE` 隔离清单而不拖垮其余节点；Final 别名与显示名按实际加载过滤；doctor 新增第 8 类诊断统一可见。
- **向后兼容**：`call_ai` 保持 7 位置参数签名不变，新增能力均为关键字可选参数（timeout / fallback_chain / max_retries_per_step / enable_recovery）；`call_ai_ex` 返回 (text, err, meta) 供需要可观测性的调用方。

### V16.1.1-MERGED（审计修复版）

- **版本库并发安全加固**：Windows 进程探活改为只读查询（ctypes OpenProcess + GetExitCodeProcess + WaitForSingleObject 消歧 STILL_ACTIVE，不再调用会误杀进程的 os.kill）；锁文件沿用 V14.3 的 O_CREAT|O_EXCL 原子创建，token 写入改单次 write+fsync（消除"已创建未写入"竞态窗口）；空锁文件引入 10s 宽限期防误判；新增 T7 并发 8 线程×2 提交零丢失实测断言
- **SSRF 防护加固**：API URL 校验后 IP 钉扎直连（二次 DNS 解析归零，杜绝 DNS rebinding/TOCTOU），IPv4-mapped IPv6 归一化，云 metadata IP 显式拦截，DNS 解析失败即拒绝
- **长片引擎修复**：身体细节池重复键合并（"父亲"两处 10 项池静默覆盖问题）；角色弧位置改为按全片镜头比例定位（不再被绝对镜头号阈值绑架）
- **Cinematic 修复**：总时长输入继承逻辑修正（非默认值优先）；POV 切换保留后缀；删除零消费死代码（情绪曲线模板/叙事结构表）
- **诚实口径统一**：534→600 导演库文案/诊断全面对齐；doctor 6→7 类诊断；MEGA 工作流元数据 total_links 修正；workflows/README 按实测重写（含 legacy 存档 23 个工作流实测节点/链接数）
- **T10 结构断言补齐**：新增灵魂黑夜位置断言（稳健匹配"灵魂黑夜/灵魂的黑夜"双写法），英雄之旅 12 阶段纳入四结构断言；实测区间中点 48-53%、黑夜 68-76%、高潮 76-84%
- **终审增强（双 AI 终审闭环）**：IP 钉扎集为空即拒绝连接（fail-closed，禁止回退二次 DNS 解析）；测试证据存档机制（AIGC 全量结果 JSON 落盘、T7 并发后体积入记录）；README 实测数字与存档逐一对齐（VideoRouter 唯一 6、相似度最大 0.606、19 版本并发后 2458 B）

### V16.1.0-MERGED（最终输出 AIGC 化 + 场景锚定）

- **叙事编排引擎**：正叙 / 倒叙(结果先行) / 穿插倒叙 / 穿插乱叙 / 循环叙事 × 单线 / 双线并行 / 三线交织 / POV切换，确定性时序重排 + 时间线/线索图谱 + 导演批注 + 字幕位
- **每镜七要素 AIGC 提示词**：参考绑定 / 主体与动作 / 空间 / 镜头 / 视觉 / 音频 / 约束（Seedance 2.5 / Wan 3.0 官方手册范式）+ 首帧提示词 + 音频描述，分镜 JSON / 交付 JSON 双注入
- **场景锚定（本版核心修复）**：输入场景的地点/时间/天气/道具主导分镜生成——修复此前随机取池导致的场景脱节（输入"民国上海雨夜后台卸妆"却产出"天台大雪/邮局营业厅大雪"）。首尾场 100% 锚定、中间场相邻空间变体；时间/天气仅在输入含显式词时锚定；用户道具开场/收束必现
- **无锚点兜底**：二级空间词表（车厢/路/河/医院/咖啡馆/走廊等 70+）+ 动作语义兜底（走→漫漫长路 / 梦→梦境）+ 常见英文空间词兜底，极简/抽象/英文输入不再落回无关通用池
- **解析加固**：单字关键词复合词守卫（上海/国家/江山不再误判自然风光），城市名最长匹配优先，室内空间词优先判内景，民国年代检测（旗袍/百乐门/黄包车等）
- **去AI味文本质量层**：空洞词具象翻译表 / 后缀去复读 / 元语言出清
- **回归防线**：tests/test_aigc_random_full.py 新增维度 H 场景贴合度断言（≥60% 镜头 AIGC 提示词命中输入锚点）。实测：40 例全量随机 PASS=543 FAIL=0；18 组合 AIGC 抽检全 OK（贴合率 100%，空洞词 0）

### V16.0.1-MERGED（完整性恢复）

- **恢复 46 个 legacy 细粒度节点可选兼容层**：从 V14.3 归档完整恢复 73 个文件（46 legacy 节点模块 + 23 legacy 工作流 + 历史文档），接回 `DIRECTORMASTER_LEGACY_NODES=1` 动态注册机制。实测：默认加载 17 节点；`DIRECTORMASTER_LEGACY_NODES=1` 加载 63 节点，0 加载错误
- **保持移除编造内容库**：`aggregator/library/` 下 500 条槽位拼接的编造剧本/分镜 JSON（24.6MB）违反零虚假红线，维持移除，当前代码零引用
- **数据库完整性核实**：600 导演库、knowledge_base（25 文件）、scene_library / story_sense_data / director_soul 等真实数据库逐字节比对完整

### V16.0-MERGED（四项能力）

- **全下拉随机模式**：全部 71 个下拉框补全 🎲 随机；V16.3.0 起全部 🎲 站点由"随机种子"统一驱动（种子0每次执行真随机 / 固定种子全链可复现，见版本历史 V16.3.0），非随机路径确定性不被破坏
- **目标时长秒级支持**：Cinematic/Script 目标时长 INT→FLOAT（min=0.05=3秒, step=0.05），短视频用小数（0.25=15秒 / 0.5=30秒 / 1=60秒），长片用整数，总时长恒覆盖片长
- **节点全方向输出**：美术节点"全部"模式输出 美术指导+空间一致性+空间布局 三方向；声音节点"全部"输出 声音设计+音乐配乐+声音层+沉默 四方向
- **AIGC 视频生产适配**：自动判别生产模式（参考视频 > 首尾帧 > 多参考图 > 首帧 > 文生），分镜 JSON 含生产模式 + 每镜 AIGC 适配提示词，Cinematic + VideoRouter 双节点集成

### V15.0-MERGED（AI 赋能）

- **导演库扩容 534→600**：当代新锐 / 跨界（MV/游戏/时尚/艺术）/ 非西方（非洲/拉美/中东/亚洲）66 位真实导演，17 维档案（12 标准维 + 跨媒介影响/反常规动作/情绪暗流/失败美学/哲学内核）
- **风格融合引擎**：主风格 0.6 + 次风格 0.3 + 反风格 0.1 确定性文本融合，反风格提取"反常规动作"作为突破指令
- **直觉引擎**：确定性反常规镜头语法，8 条规则均有真实作者电影依据（哈内克高潮静止/侯孝贤亲密远景/是枝裕和喧闹后静默/王家卫孤独不对称/小津物件代反应/蔡明亮对白后留白/伯格曼打破第四墙/戈达尔跳切），风险分级 safe/medium/bold/chaotic
- **灵魂引擎**：创作者体验文本 → 物件/动作/沉默母题（场景驱动，零罐头句），三层情感模型 + 叙事装置（伏笔/反转/留白）
- **多模态理解**：真实图像分析（numpy k-means 色板/亮度→光影/饱和度→情绪/能量分布→构图），音视频诚实降级
- **共创引擎**：五阶段共创循环（S0 上下文+失败记忆 → S1 三方向分支 → S2 确定性门阵 → S3 门控驱动精炼 → S4 预算收敛），基于 Self-Refine/Reflexion/GoT/Best-of-N 研究，无端点时 T0 确定性档可运行
- **失败记忆**：每次质量门拒收写入 lessons.jsonl，下次生成检索注入（Reflexion 模式，全确定性）
- **反AI正则检测层**：中文 AI 套话结构模式检测（八股连接词/过度修饰/回避决断/空洞升华）

V15.0 新增节点：

| 节点 | 能力 |
|---|---|
| DirectorMasterCoCreator | AI 共创循环：故事核心→3方向分支→门阵→精炼→共创剧本（含方向分支图JSON+创作日志） |
| DirectorMasterSoul | 灵魂注入：创作者体验→母题派生→灵魂层注入剧本（含灵魂片段报告） |
| DirectorMasterIntuition | 直觉修改：分镜JSON→确定性反常规镜头语法（含修改日志） |
| DirectorMasterFusion | 风格融合：主0.6/次0.3/反0.1 确定性融合，反风格提取突破指令（含元数据JSON） |

### V14.x

- **V14.3-MERGED**：V14.2 + V14.1-clean 合并（9 项数据库接线复活），阶段 1/2 质量深化（镜头语法差异化/形态骨架/互动剧分支树/版本存储工程化），并发安全与安全加固
- **V14.2**：P0 根治（假分镜/数据损坏/密钥清除），模式坍缩根治，结构节拍归位，4 项能力接线，保存格式多选
- **V14-FINAL**：节点收敛 59 → 13 超级节点

---

## 定位说明

本系统是导演级提示词转译与创作引擎：把导演的已知风格特征与剧作方法论转译成结构化剧本/分镜/视频模型提示词。最终画面质量取决于下游视频模型。
