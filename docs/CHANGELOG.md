# Changelog - PromptLibraryNode

所有版本变更记录。格式基于 [Keep a Changelog](https://keepachangelog.com/)。

---

## [v16.6.0-MERGED] - 2026-08-30 - 批次2 知识资产工程 + 分镜契约基座（并入 V16.3-V16.5 迭代后顺延编号）

### 背景
批次2 与另一端从同一批次1 基线（c9d38ce）并行演进：对端产出 V16.3 随机引擎诚实化 / V16.4 情节拓扑引擎 / V16.5 场景实体引擎，本端产出模式卡语料 + 分镜 JSON 契约 v1 + 索引一致性门禁。变基整合后版本顺延 16.6.0，契约注册表吸收对端 V16.4/V16.5 的分镜 JSON 增量键。

### 新增 (Added)
- 244 张模式卡全量入库（`knowledge_base/mode_cards/`，10 节点创作模式，frontmatter 八键 + 正文五节，节点映射给实现 file:line 指针）；单一事实源 `tests/mode_manifest.json`（真实 INPUT_TYPES 探针 + 排除审计表）。
- `tools/dump_mode_manifest.py` 探针 + `--verify` 三方核对；`tools/sync_mode_index.py` 索引生成与 `--check` 门禁（孤儿卡/缺必填字段/错目录/名称错配/索引漂移五类违例硬失败，负样本 8 断言复现）。
- doctor 第 9 类诊断"模式卡与分镜契约一致性"（manifest ↔ 卡 ↔ live 枚举三方对账）。
- `aggregator/storyboard_contract.py` 分镜 JSON 契约 v1（三态字段 + 11 诊断码 + 相对镜头表达式拓扑解析/环检测 + 永不抛宽容解析）；Cinematic additive 接线（产物仅增 contract_version 键，分镜文本逐字节不变）。
- `tests/test_storyboard_contract.py` 81 断言（含 None 链诚实断裂 T20 回归钉）；证据存档随包。

### 整合 (Merged)
- 变基 c9d38ce→302571c 之上，线性历史；对端 7 个新文件与三节 README 版本历史完整保留；契约注册表吸收 叙事拓扑/场景实体/设备美学包/同期声枚举 与 每镜构图/叙事标签/节奏手记/拓扑张力（类型对齐实现赋值点）。

### 口径 (Changed)
- 创作模式数 246→244 诚实修正（258 下拉 − 10 随机/默认 − 2 并集组合 − 2 别名重复，审计表见 tests/mode_manifest.json）。
- 版本口径一致性测试升级为动态三处校验（升版只改三处源，不改测试）。

### 验证
- 并集回归 16 项全绿（277/543/43/18/11/110/19/12/73/71用例/81 断言 + v15_probe 26 + d1/d2 + doctor 54 通过/0 错误）；整合双盲复核双通道 approve。

## [v16.5.0] - 2026-08-29 - 场景实体引擎（真实素材设计范式，对齐生产级提示词标准）

### 背景
以真实生产级 AI 视频提示词标准库（Mx-Shell 生产模板 / 真实素材设计 Skill / Seedance·Wan 官方手册范式）为质量基准，构建全维度测试矩阵（71 用例）实测剧本+分镜输出。首轮实测暴露内容级鸿沟：用户场景"女机甲战士在暴雨码头开启能量护盾"产出"辣椒酱/女儿/护士"罐头内容（用户实体命中≈0）。本版以场景实体引擎彻底修复。

### 新增 (Added)
- `aggregator/scene_entity.py` 场景实体引擎（全确定性, 零依赖）：
  - `extract_entities` 实体提取（角色/道具/地点/天气/色彩/动作; 后缀词典+核心词清洗+连接词拆分）；
  - `device_package` 设备美学包 9 种（IMAX 实拍/暗调数字/暖色胶片/复古港片/手机竖屏/纪录观察/压抑写实/DV 怀旧/风格化动画——摄影机+镜头+画质缺陷+素材身份声明）；
  - `focal_for_size` 焦段-景别电影学匹配（特写 85-135mm / 全景 24-35mm，消灭"中近景 12mm"）；
  - `sound_cues` 同期声显式枚举（天气/地点/道具派生：暴雨砸击声、缆绳吱呀、能量低频嗡鸣…）；
  - `composition_for` 构图库（每镜四件套: 景别+构图+运镜+画面内容）；
  - `rewrite_focus` 画面内容重写（用户实体×阶段动作线×景别化细节×氛围尾注, 三槽独立 md5 驱动, 保留直觉引擎标注）；
  - `first_frame_desc` 首帧描述真实化（不再是阶段名）；
  - `five_segment_shell` 五段结构外壳（核心主题/人物设定含瑕疵锚点/氛围画质含呼吸感手持/镜头控制/同期声）+ 结尾克制 + 自检清单；
  - `second_by_second` ≤20s 按秒切时间轴（[0-3s·凝视] 式, 写法A）。
- `tests/test_matrix_full.py` 全维度矩阵（71 用例: 12 时长档×16 题材×12 叙事组合×4 主角配置×8 导演×13 视觉调性×运镜演变×有/无 LLM 轨）——**71/71 全 PASS**；rubric 含硬门（零崩溃/JSON可解析/场景实体命中）与 14 项质量项（五段结构/设备美学包/呼吸感/同期声枚举/瑕疵锚点/零空洞词/焦段匹配/构图四件套/首帧真实化/多样性/结尾克制/按秒切/拓扑+情感曲线/时长归一）。
- LLM 轨真实验证：本地 OpenAI 兼容 mock 服务器走通 AI 增强轨（Core AI 字段→下游继承→质量门控）。

### 修复 (Fixed)
- **罐头内容脱节（核心）**：`scene_engine.parse_scene` 融合实体引擎（char_map 单字误判角色"女→女儿"在被实体包含时丢弃；实体优先），分镜画面/剧本角色/AIGC 角色锚/POV/音频全链用户实体化。实测：机甲场景"机甲"143 次命中、"女儿"139→0；父女厨房经典场景罐头池正常服务不受影响。
- **空洞词清洗**：罐头池"决战场面/震撼"→"决战场面/胜负手"、"震撼/失重"→"失重般的失衡/眩晕"（附件标准: 用具体可拍描述替代空洞情绪词）。
- **长片指纹多样性**：rewrite_focus 三槽（动词 6 变体/景别细节 6 池/氛围尾注 8 选）独立 md5 驱动且种子含导演|情绪|场景；拓扑时长 jitter 与罐头焦点种子补入导演——final_capability_audit 镜头指纹重复率 71.5%→14.0%（阈值 15%）。
- 直觉引擎标注（〔直觉R…〕）不再被实体重写抹除（v15_probe 回归修复）。

### 验证 (Verification)
- 15 套件全绿（doctor 50P/0E、all_modes 277P、aigc 543P、random_full_v16 73P、ten_rounds 43P、final_audit 全过、llm 110P、isolation 19P、workflows 18P、f2 11P、v15 26P、d1/d2 PASS、adversarial 12P、matrix 71/71）。
- 真实 ComfyUI 宿主：V16.5 同步后 17/17 节点注册、启动零异常。

---

## [v16.4.0] - 2026-08-29 - 情节拓扑引擎（吸收 V16.6-AIGC 参考版真实增量）

### 来源裁决
- 对附件版（包名 V16.6-AIGC / 内部目录 V16.0.1-MERGED / `__version__`=16.6.0 / 文件头 V16.1-AIGC，四处口径矛盾）完成独立审计：其自带 final_capability_audit **17 项 FAIL**（主打 AIGC 五模式适配提示词全缺失、分镜缺景别/运镜字段、总时长=0），删除了 llm_resilience/load_isolation/aigc_random_full 三套件，无 DM_QUARANTINE/PROVIDER_PRESETS，整体删除 46 legacy 节点与 18 legacy 工作流 → **裁决本基座更完善**，仅吸收其两件真实增值（叙事拓扑引擎 + 强化测试维度），按本基座中文 schema 独立重写。明细见 `docs/VERSION_COMPARE_V16.3_vs_V16.6AIGC.md`。

### 新增 (Added)
- `aggregator/plot_topology.py` 情节拓扑引擎（全确定性, 零依赖）：波浪小高潮/反转点(波谷)/层层递进推断；复杂叙事结构检测与落实——套层叙事（框架带+戏中戏）/ 罗生门（A/B/C 视角版本带+真相拼合）/ 时间循环（循环区谷底逐次抬升+破局点）/ 环形叙事（起点+渐近回环+首尾闭环）；支持 `自动`（场景关键词推断, 优先级 循环>罗生门>套层>环形）与手动档。
- Cinematic 节点 optional 输入 `复杂叙事结构`（自动/无/四结构；optional 保证全部旧工作流零破坏）。
- 分镜 JSON 纯增量键：`meta.叙事拓扑`（waves/twists/twist_positions/escalation/complex/复杂结构带）+ 每镜 `叙事标签` / `节奏手记` / `拓扑张力`。
- `tests/test_random_full_v16.py`（73 断言）：时长归一≤8%、时长/景别多样性≥3 种、≥60 镜张力跨度≥4、相邻焦点重复≤15%、四复杂结构端到端（识别+每镜标签+覆盖>10 镜）、拓扑同种子逐字节复现、手动档[无]清空、正面内容零英文 AI 套话。

### 修复 (Fixed)
- **时长归一（吸收自参考版"总时长归一到预算"）**：修复基座时长量化缺陷——用户请求 45 分钟被量化到 30 分钟桶（输出偏差最高 33%），违背 目标时长 输入 tooltip"总时长恒覆盖片长"的既有承诺。新实现：阶段+张力驱动时长权重重塑（低张力长镜/高张力快切 + 确定性 jitter）+ 三步精确闭合（加权→归一→取整残差按比例摊回），任意请求时长总偏差实测 ≤8% 内（常态 <0.5%）。
- **景别/时长单一化**：短档位（8/15/30/45 分钟）此前全镜同时长、景别 1-2 种；现由拓扑权重与阶段带景别阶梯兜底（仅在塌缩时轮换：建立广角/发展中景/高潮紧密/收束拉远，相邻不重复；用户显式偏好仍最优先）。
- **浮点纪律**：拓扑 meta 全量 ≤2 位小数（ten_rounds 浮点伪影扫描清零保持）；张力取整 1-10。

### 验证 (Verification)
- 13 套件全绿：doctor 50P/0E（numpy 装齐后依赖警告清零）、all_modes 277P、aigc_random_full 543P、random_full_v16 73P、ten_rounds 43P、final_capability_audit 全通过、llm_resilience 110P、load_isolation 19P（动态版本校验）、workflows 18P、f2 11P、v15_probe 26P、d1/d2 PASS、adversarial 12P。
- 真实 ComfyUI 宿主端到端（torch 2.13.0+cpu, /object_info + POST /prompt 真实排队）：17/17 节点注册、固定种子全链产出逐字节可复现、种子 0 真随机。

---

## [v16.3.0] - 2026-08-28 - 随机引擎诚实化 + 全链种子驱动 + 独立对抗验证层

### 修复 (Fixed)
- **🎲 随机名不副实（P0，违反项目自身零虚假红线）**：V16.1 起所有 🎲 随机以 `MD5(项目名_场景描述)` 为种子，相同输入下每次执行输出完全相同（30 轮"随机"导演仅 1 位唯一），项目自带 `tests/final_capability_audit.py` 4 项失败（导演去重 1/30、剧本指纹 22/30、分镜指纹 28/30、镜头语法重复率 29.4%>15%）。根因：随机种子只含输入哈希，不含任何执行期熵；且 Core（确定性种子）与下游（全局 random）策略不一致。
- **Intuition 引擎崩溃**：畸形 `分镜JSON`（分镜表为字符串、元素非 dict）导致 `dictionary update sequence element #0` 崩溃。已在 `aggregator/intuition_engine.py` 加类型守卫，非 list 输入原样诚实返回。

### 变更 (Changed)
- **Core 新增 `随机种子` INT 控件**（`control_after_generate=randomize`，ComfyUI KSampler 同款交互）：
  - 种子 0 = 每次执行 OS 熵真随机（`random.SystemRandom`，诚实随机）；
  - 种子 >0 = 固定种子全链完全可复现（保留 V16.1 的可复现设计意图，显式可选）。
- **全链种子传播**：种子以 `_随机种子` 写入核心数据包；Script/Cinematic/Vibe/Art/Sound/Characters/Asset/Router/VideoRouter/Archive/CoCreator/Intuition 的全部 🎲 站点（模式/属性/风险档位/直觉档位/市场推断，30+ 处）统一改为 `resolve_dropdown(..., seed=derive_seed(种子, 域盐))` 驱动；新增 `aggregator/node_base.py::derive_seed / seeded_rng / seeded_choice`。下游单独排队（无核心包）时回退全局随机，向后兼容。
- **行为变化声明**：API 直调 Core 且不传 `随机种子` 时，🎲 相关输出从"恒定"变为"每次执行新随机"；需要旧行为请显式传固定种子。

### 新增 (Added)
- `tests/test_adversarial.py` 独立对抗验证层（12 断言）：全节点 × 1100+ 次畸形输入零崩溃；种子语义属性测试（种子0非恒定/固定种子逐字节复现/多种子分布多样）；独立口径复测导演库规模（≥600）/唯一性/档案维度/反AI层。
- `docs/LEGACY_AUDIT.md`：AST 全仓依赖图诚实审计（29 活跃引擎 / 8 legacy 内部链 / 3 真死代码 `director_pro`+`director_engine`+`engine_story_arc` / 3 独立入口工具）；真死代码处置留维护者裁决，本轮不删除。

### 文档 (Docs)
- WORKFLOW_DOC_V6.1.md / RELEASE_NOTES_V7.0.md / PHASE_NODES_REFERENCE.md / PLAN_COMPARE_V6.3_VS_V7.md 头部加"历史文档"横幅（与当前代码已脱节）。
- README 质量验证节新增对抗验证指标；随机模式声明更新为 V16.3.0 种子驱动语义。

### 验证 (Verification)
- `tests/final_capability_audit.py`：修复后 30 轮全随机链路审计**全部通过**。
- 全量回归：doctor 47P/0E、test_all_modes 277P、test_aigc_random_full 543P、test_llm_resilience 110P、test_load_isolation 19P（版本校验升级为动态三处一致）、test_workflows 18P、f2 11P、v15_probe 24P、d1/d2 PASS、ten_rounds T1-T10 全 PASS、test_adversarial 12P。

---

## [v3.1] - 2026-08-09 - 灵魂节点 (Director Soul)

### 新增 (Added)
- **灵魂节点 v1.0** (DirectorSoulNode) - 60 情感矩阵 + 7 融合公式 + 10 灵魂维度 + 灵魂状态动态计算
- **88 情感别名** (EMOTION_ALIASES) - 8 基础 + 24 子词 + 60+ 中文全自动 alias 解析
- **28 真实电影灵感时刻** (INSPIRATION_DB) - 8 大世界顶级导演 (王家卫 5 / 诺兰 5 / 奉俊昊 3 / 黑泽明 3 / 是枝裕和 3 / 塔可夫斯基 3 / 侯孝贤 3 / 芬奇 3)
- **灵魂注入统一 wrapper** (soul_inject_simple) - 解决 4 大兼容问题 (alias 解析 / 字段名 / _str 检查 / _safe_fuse 预过滤)
- **场景权重推断** (5 大场景类型: key_climax / transitional / inner_monologue / ensemble / transition_moment)
- **灵感时刻注入器** (5 大类 20 个具体灵感: camera / color / composition / rhythm / detail)

### 变更 (Changed)
- **26 节点接入灵魂**:
  - 4 核心节点 (Phase 17.5): concept_pitch / director_intent / editing / art_direction
  - 21 _pro.py 节点 (Phase 17.6 批 1-6): script_architecture / script_body / director_storyboard / vertical_short_drama / hook_master / dialogue_master / character_arc / spatial_consistency / silence_mastery / world_building / theme_philosophy / sound_design / music_score / performance_direction / costume_prop_set / color_grading / vfx_pro / mv_pro / picture_book / interactive_drama / quality_assurance
- **editing_pro.py** 节奏曲线真正由灵魂动态生成 (诺兰起手 10.4s + BPM 98-130 / 塔可夫斯基起手 11.6s + BPM 31-50 / 王家卫起手 13.4s + BPM 56-70)
- **修复 3 个严重 bug**:
  - `EMOTION_ALIASES` 缺失 (8 基础情感 + 24 子词 + 60+ 中文)
  - `_str` 函数缺 `v==""` 检查
  - `_safe_fuse` 预过滤不调 alias

### 测试 (Tested)
- 597/597 测试通过 (test_full_audit 92 + test_e2e_full 200 + test_phase13_audit 305)
- 25 节点 × 4 情感对比 (loneliness/fear/warm_regret/anger) 输出真不同
- 6/6 两两不等
- 3 真实剧本片段端到端验证 (花样年华/盗梦空间/步履不停) 完美

### 文档 (Documented)
- `PHASE_17_DEVELOPMENT_PLAN.md` - 灵魂节点开发计划
- `PHASE_17_DUAL_AI_AUDIT.md` - Phase 17 互审
- `PHASE_17_7_INSPIRATION_DB.md` - 28 真实灵感时刻详解
- `PHASE_19_DUAL_AI_AUDIT.md` - 综合双 AI 互审
- `RELEASE_NOTES_v3.1.md` - v3.1 Release Notes

### Git (Committed)
- 23 commits 总数
- Phase 17.5 (1) + Phase 17.6 批 1-6 (15) + Phase 17.7 (1) + Phase 19 (1) + Phase 20 (1) + Phase 21 (1) + 之前 (3)

---

## [v3.0] - 2026-08-08 - Phase 16 AIGC 影视全流程

### 新增 (Added)
- **Phase 16 AIGC 影视全流程解析对齐** (8 大能力 + 42 环节 + L1-L7 七层 + 3 留白 + 3 运镜)
- **8 大顶级导演能力映射**: AB1 叙事架构 / AB2 情感调度 / AB3 节奏控制 / AB4 视觉语言 / AB5 表演指导 / AB6 场面调度 / AB7 审美判断 / AB8 团队领导
- **L1-L7 七层 Prompt 架构**: L1 意图 / L2 资产 / L3 空间 / L4 表演 / L5 摄影 / L6 声音 / L7 风格
- **3 留白 + 3 运镜法则**: 时间留白 / 空间留白 / 叙事留白 + 破坏首帧 / 非线性运动 / 响应延迟
- **42 环节 8 阶段全流程**
- **director_prompt.py** (43.5KB) 主 agent 重做
- **phase16_six_documents.py** 新增 3 个字典 (L1_L7_ARCHITECTURE / WHITESPACE_CAMERA_LAWS / EIGHT_ABILITIES_MAP)

### 测试
- 597/597 测试通过 (从 595 升级, Cinematic Studio 7→10 输出)

---

## [v2.x] - 2026-08 早期 - Phase 9-14 节点系统

### 已完成
- Phase 9 剧本 3 节点: ScriptArchitecturePro / ScriptBodyPro / DirectorStoryboardPro
- Phase 11 专业 4 节点: VerticalShortDramaPro / HookMasterPro / DialogueMasterPro / CharacterArcPro
- Phase 12 附件 4 节点: DirectorIntentPro / ArtDirectionPro / SpatialConsistencyPro / SilenceMasteryPro
- Phase 12 续+13 环节 14 节点: ConceptPitchPro / WorldBuildingPro / ThemePhilosophyPro / SoundDesignPro / MusicScorePro / PerformanceDirectionPro / CostumePropSetPro / EditingPro / ColorGradingPro / VfxPro / MvPro / PictureBookPro / InteractiveDramaPro / QualityAssurancePro
- Phase 14 Hell Grind 5 节点: Phase14AssetRegistry / Phase14SpatialLayout / Phase14ActingSkill / Phase14SoundSkill / IterationPostPro
- Phase 14 升级 2 节点: Phase14_30sSixAct / Phase14_CinematicStudio
- 12 套剧本理论 + 14 部真实 AI 短剧实战 + 4 类创作者实战
- 卡兹克 6 篇微信文章融合
- H3 三大字段 (integrated_multimodal_description + overall_soundscape + non_diegetic_music)
- 13 镜头运动 + 11 维导演控制 + 9 维光照
- 191 反 AI 词表 + 10 强制具体细节铁律

### 测试
- 从 200/200 升级到 597/597

---

## [v1.0] - 2026 早期 - 初始版本

- 基础提示词库节点
- 导演分镜节点
- 故事板生成

---

[Unreleased]: 持续改进中
- Phase 18 节点去模板化
- Phase 22+ 灵感时刻持续加量
- Phase 23 GitHub 推送
- Phase 24 端到端真实剧本测试扩展
- Phase 25 真实导演反馈收集
