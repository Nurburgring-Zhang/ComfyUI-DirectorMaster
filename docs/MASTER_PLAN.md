# ComfyUI-PromptLibraryNode V10.1 — 世界顶级补全开发计划

> **目标**：把现有 50% 真实可用、50% 装饰性包装的混合状态，补到 100% 全部可上生产、对标世界顶级导演引擎的标准。
> **方法论**：分阶段实施 + 双 AI 互审 + 多子 agent 集群并行 + 端到端验证。

---

## 0. 现状诚实评估（基准线）

| 维度 | 当前状态 | 距离世界顶级 |
|---|---|---|
| 节点注册/安装 | ✅ 100% 可用（实环境已验证） | ✅ 已对齐 |
| 提示词库读取 / AI 生成润色 | ✅ 100% 可用 | ✅ 已对齐 |
| 25 模式分派 | ⚠️ 70% 可用，30% API 缺失时静默 | 需补 fallback |
| 故事板 9 种 | ✅ 100% 可用（API 在线时） | ✅ 已对齐 |
| 故事弧引擎 (StoryArc) | ✅ 100% 可用 | ✅ 已对齐 |
| 镜头连续性追踪 | ✅ 100% 可用 | ✅ 已对齐 |
| 摄影/运镜/转场/表演/类型/创作技法 6 知识库 | ✅ 100% 接通 | ✅ 已对齐 |
| 63 导演基础档案 (5 字段) | ⚠️ 100% 存在但浅 | 需补 7-12 维 |
| 63 导演决策层 (DIRECTOR_DECISION) | ❌ 0% 接通 | 需接引擎 |
| 叙事决策 (NARRATIVE_DECISION) | ❌ 0% 接通 | 需接引擎 |
| 标签/细分 (TAG_TAXONOMY / STYLE_SUBDIVISIONS) | ❌ 0% 接通 | 需接引擎 |
| Director Pipeline 速查 | ❌ 0% 接通 | 需接引擎 |
| 作品库 works_corpus_extended/rich/hot_shortform | ❌ 0%（空模块） | 需补 45+ 部 |
| output_focus 5 维差异化 | ❌ 0%（仅字符串） | 需真注入 |
| 维度设计 5 模块 | ❌ 0% 接通 | 需接通 |
| 双 AI 互审 / 端到端落地 | ⚠️ 121 自检过但无真机测试 | 需补 |

**核心结论**：基础闭环 50% 已达世界级，50% 是装饰数据。**补全 7 大块就能到 95%+ 顶级**。

---

## 1. 全局策略

### 1.1 开发原则
- **不破坏现有**：所有修改必须保证现有 121 个自检 + ComfyUI 注册 + 已有 prompt 流程不破
- **数据驱动**：导演档案、决策层、作品库必须是真实专家级数据，不是占位字符串
- **引擎先行**：先改 `director_engine.py` 的注入逻辑，再填数据进知识库
- **双 AI 互审**：每个 PR 实施后必须跑静态分析 + 动态模拟 + 真实路径触发

### 1.2 阶段划分（每阶段都有"实施 + 互审 + 测试"三步）

| 阶段 | 内容 | 预计改动文件 | 完成标志 |
|---|---|---|---|
| Phase 0 | 实施框架与诊断工具 | `__init__.py`, `INSTALL_GUIDE.md`, `doctor.py` | 节点不显示可自诊断 |
| Phase 1 | 补全 63 导演 12 维档案 | `knowledge_base/director_styles.py` | 63/63 导演全部字段满 |
| Phase 2 | 补全作品库 45+ 部 | `works_corpus_extended.py` / `works_rich.py` / `works_hot_shortform.py` | 45+ 部真实作品可引用 |
| Phase 3 | 决策层接通引擎 | `director_engine.py` / `format_templates.py` | 5 个决策 dict 真实注入 prompt |
| Phase 4 | output_focus 真实差异化 | `director_engine.py` | 5 维度切了 prompt 真变 |
| Phase 5 | 维度设计 5 维接通 | `dimension_design.py` / `director_engine.py` | CHARACTER/ENVIRONMENT/STORY/ATMOSPHERE/INTERACTION 真注入 |
| Phase 6 | 端到端落地测试 | `test_e2e_full.py` | 200+ 测试全过 |
| Phase 7 | 双 AI 互审 + 文档 | `AUDIT_REPORT.md` | 真实路径全部验证 |

---

## 2. 详细实施计划

### Phase 0：实施框架与安装诊断工具

**目标**：当用户遇到"节点不显示"时，给出可执行的自检脚本。

**新增**：
- `INSTALL_GUIDE.md` — 三种安装方式（Manager / git clone / 手动） + 4 类故障排查
- `doctor.py` — 自检脚本：检测 custom_nodes 路径、__init__.py、NODE_CLASS_MAPPINGS、依赖模块、API 连通
- `__init__.py` 顶部添加兼容性检查代码（捕获 import 错误并打印详细建议）

**验收**：
- 在 4 种错误安装场景下跑 `python doctor.py` 都给出可执行建议
- 不破坏现有 import 流程

---

### Phase 1：补全 63 导演 12 维档案

**目标**：每位导演从 5 字段（cn/signature/visual_techniques/narrative_principle/applicable_genres）扩到 12+ 字段。

**新增字段（每位）**：
```python
{
    "cn": "阿尔弗雷德·希区柯克",
    "en": "Alfred Hitchcock",
    "signature": "悬念大师——不可靠叙述者",
    "era": "1899-1980",
    "nationality": "英国/美国",
    "characteristics": "操控观众情绪,利用'麦格芬'制造悬念,镜头即主观视角",
    "visual_style": "高对比黑白/冷色调,光滑玻璃反射,楼梯阴影构图,仰拍/俯拍制造心理压迫",
    "camera": "固定长焦推拉,dolly zoom(眩晕效果),受限视角,360度环绕镜头",
    "color_palette": "黑白片:深灰高光阴影对比;彩色片:冷调蓝灰为主,洋红点缀",
    "lighting": "高对比chiaroscuro,逆光剪影,聚光灯单人,符号性光源(灯/窗)",
    "composition": "中心对称失衡,垂直/对角线张力,人物被空间压迫,门/窗/楼梯作视觉锚点",
    "narrative_traits": "麦格芬(无关紧要的触发物),延迟揭露,无辜被陷害,罪与罚暧昧,黑色幽默",
    "rhythm_preference": "中速铺陈+骤然爆发,长镜蓄势/急剪爆点交替",
    "works": ["vertigo", "psycho", "rear_window", "north_by_northwest", "rope"],
    "emotional_signature": "焦虑不安/窥视/悬疑/黑色幽默",
    "color_grading": "冷峻/低饱和/胶片颗粒",
    "sound_music": "Bernard Herrmann弦乐主导,尖锐短促,环境音刻意放大",
    "failure_modes": "过度依赖jump scare=廉价;信息早揭露=失悬疑;忽视麦格芬=失风格",
    "measurement": "观众是否在关键揭示前主动产生推测+心跳加速",
    "alternatives": ["fincher(数字时代)", "polanski(心理惊悚)"],
    "applicable_genres": ["悬疑", "惊悚", "心理"],
    "scene_examples": "楼梯坠落(vertigo)/浴室谋杀(psycho)/后窗窥视(rear_window)",
    "prompt_style_prefix": "Hitchcockian suspense, voyeuristic POV, chiaroscuro lighting, McGuffin-driven plot"
}
```

**实施方式**：
- 由 5 个 sub-agent 并行写（每个 agent 负责 ~13 个导演）
- 完成后由 verifier agent 随机抽 10 个导演做真实性核查
- 数据来源：联网搜索 + IMDB + 维基百科

**验收**：
- 63 导演全部 12+ 字段满
- works 字段全部能在 works_corpus* 中找到对应 id
- random 抽查 5 个导演，事实性无错

---

### Phase 2：补全作品库 45+ 部

**目标**：在 `works_corpus_extended.py` / `works_rich.py` / `works_hot_shortform.py` 三个空模块里填 45+ 部真实作品，每部 8-10 维。

**数据结构**：
```python
{
    "id": "shawshank_redemption",
    "title_cn": "肖申克的救赎",
    "title_en": "The Shawshank Redemption",
    "year": 1994,
    "director_key": null,  # Frank Darabont - 非 63 导演之一
    "director_display": "Frank Darabont",
    "genre": ["剧情", "监狱"],
    "rating_imdb": 9.3,
    "style_tags": ["希望", "自由", "友谊", "体制"],
    "visual_signature": "低饱和监狱绿/灰,大量阴影,远景/中景为主,光象征希望",
    "key_scenes": ["屋顶啤酒", "图书馆扩建", "海边重逢"],
    "narrative_structure": "英雄之旅变体",
    "cultural_impact": "IMDB Top 1, 1994-至今,被誉为'希望圣经'",
    "prompt_seed": "prison escape, hope, friendship, two decades, redemption"
}
```

**作品分类**：
- `works_corpus_extended.py`（电影 15+ 部）— 经典 IMDB Top 250
- `works_rich.py`（电视剧 15+ 部）— HBO/Netflix 顶级剧
- `works_hot_shortform.py`（短剧 15+ 部）— 中国短剧出海/海外微短剧

**验收**：
- 3 个模块全部非空
- 作品 id 唯一不重复
- 与 63 导演的 works 引用 100% 命中

---

### Phase 3：决策层接通引擎

**目标**：把 4 个被忽略的决策 dict 真实注入 prompt。

**改动点**（`director_engine.py`）：

```python
# 旧：只读 DIRECTOR_STYLES
# 新：增加 4 个决策层读取

def _get_decision_layer(director_keys, narrative_structure, story_arc, mode):
    """统一的决策层注入函数"""
    parts = []
    
    # 1. DIRECTOR_DECISION: 导演的 trigger / failure_modes / measurement
    if director_keys:
        for dk in director_keys:
            dec = DIRECTOR_DECISION.get(dk, {})
            if dec.get("trigger"):
                parts.append(f"## 导演触发条件\n{dec['trigger']}")
            if dec.get("failure_modes"):
                fm = " / ".join(dec["failure_modes"])
                parts.append(f"## 必须避免的失败模式\n{fm}")
            if dec.get("measurement"):
                parts.append(f"## 自检标准\n{dec['measurement']}")
    
    # 2. NARRATIVE_DECISION: 叙事结构的展开策略
    if narrative_structure:
        ns = NARRATIVE_DECISION.get(narrative_structure, {})
        for k, v in ns.items():
            if isinstance(v, str):
                parts.append(f"## 叙事-{k}\n{v}")
    
    # 3. TAG_TAXONOMY: 平台标签分类
    # 4. STYLE_SUBDIVISIONS: 风格子分类
    # 5. DIRECTOR_PIPELINE: 导演工作流速查
    
    return "\n\n".join(parts)
```

**在 `build_system_prompt` / `build_user_prompt` 中调用，确保所有 24 个模式都受益**。

**验收**：
- 4 个决策 dict 全部被代码实际引用
- 注入测试：选导演"希区柯克"+"悬疑揭秘"，生成的 system_prompt 长度 > 0 且包含 trigger/failure_modes 关键词

---

### Phase 4：output_focus 真实差异化

**目标**：5 个维度（分镜/角色/环境/故事/氛围/互动）的切换，**真的让 prompt 内容不一样**。

**当前问题**：`output_focus = "分镜" / "角色"` 只是字符串透传，没差异。

**修复**：
```python
def _build_focus_layer(output_focus, mode):
    """根据输出侧重,生成对应的维度引导"""
    focus_map = {
        "分镜": _focus_storyboard,
        "角色设计": _focus_character,
        "环境设计": _focus_environment,
        "故事情节": _focus_story,
        "画面氛围": _focus_atmosphere,
        "互动交互": _focus_interaction,
    }
    fn = focus_map.get(output_focus, _focus_storyboard)
    return fn(mode)

def _focus_character(mode):
    return """
## 当前输出侧重:角色设计
每个分镜/页面,优先输出:
- 角色外貌(年龄/身高/体型/肤色/发型/标志性特征)
- 服装细节(款式/材质/颜色/时代)
- 表情微动作(眼/嘴/手)
- 角色间关系张力
- 角色弧光变化
- 禁止"动作"叙事(只写外貌/状态变化)
"""
```

**验收**：
- 同样参数，切换 5 个 output_focus，生成 5 个不同 system_prompt
- 每个 prompt 关键词与侧重维度匹配

---

### Phase 5：维度设计 5 维接通

**目标**：`dimension_design.py` 已有的 5 个 dict (CHARACTER/ENVIRONMENT/STORY/ATMOSPHERE/INTERACTION) 接通到引擎。

**改动**：
- 在 `build_system_prompt` 增加 `_build_dimension_layer()` 调用
- 根据 `output_focus` 选择性注入对应维度的 `callable` 模块
- 模式为"角色设计"时，注入 CHARACTER_DESIGN 的 character_arc / appearance / costume / motivation / relationship
- 其他 4 维度同理

**验收**：
- 每个维度的 dict 数据被实际引用
- 输出 prompt 真的体现维度

---

### Phase 6：端到端落地测试

**目标**：写一个 `test_e2e_full.py`，跑通所有 200+ 真实场景。

**测试维度**：
1. 节点注册（23 个模式 + 2 个节点全部能 load）
2. 提示词库读取（8 种读取模式 × 5 种循环模式 = 40 组合）
3. AI 生成/润色/翻译
4. 故事板 9 种 × 5 种风格 × 5 种景别 = 225 组合（采样 30 个）
5. 绘本 / 短剧 / 儿童 / 设计
6. 23 模式批次输出
7. 63 导演 × 24 模式 = 1512 组合（采样 50）
8. 决策层注入（4 个决策层 × 5 个模式 = 20 组合）
9. output_focus 5 维差异
10. 边界条件（空 API / 空文件夹 / 无效路径 / 字符编码）

**验收**：所有测试通过 + 输出报告

---

### Phase 7：双 AI 互审 + 文档

**目标**：
- A 角色：开发 + 实施
- B 角色（verifier agent）：独立审查代码 + 数据真实性
- 双方分别给出报告，对比有冲突的地方再修复

**产出**：
- `AUDIT_REPORT.md`：A/B 互审报告
- `FINAL_USAGE.md`：用户使用文档（每模式截图、API 配置、常见问题）
- `RELEASE_NOTES.md`：版本变更日志

---

## 3. 子 agent 任务分配（并行执行）

| Agent | 任务 | 输入 | 输出 |
|---|---|---|---|
| **Agent A** | Phase 0: 诊断工具 + 安装文档 | 项目根目录 | `INSTALL_GUIDE.md`, `doctor.py`, `__init__.py` 改动 |
| **Agent B** | Phase 1: 13 经典 + 5 艺术 + 7 新好莱坞 | `director_styles.py` | 25 导演档案 |
| **Agent C** | Phase 1: 18 当代 + 16 亚洲 | `director_styles.py` | 34 导演档案 |
| **Agent D** | Phase 1: 3 国际 + 4 短剧 + 3 新媒体 | `director_styles.py` | 10 导演档案 + 互审 B/C |
| **Agent E** | Phase 2: 作品库 45+ 部 | 3 个空文件 | 3 个文件填满 |
| **Agent F** | Phase 3+4: 引擎改动（决策层 + output_focus） | `director_engine.py` | 引擎改造 + 单元测试 |
| **Agent G** | Phase 5+6: 维度设计 + E2E 测试 | `dimension_design.py` + 新增 | 测试 200+ 全过 |
| **Verifier** | 全程双 AI 互审 | 所有改动 | `AUDIT_REPORT.md` |

---

## 4. 自我质疑清单

- [ ] 数据真实性：63 导演档案是否专家级（不是 AI 臆造）？
- [ ] 引擎注入路径：5 个决策层是否真在 prompt 中？
- [ ] 边界条件：空 API 时各模式是否优雅降级？
- [ ] 性能：shot 数 60 × batch 输出是否会超时？
- [ ] 兼容性：现有用户工作流不破？
- [ ] 可维护性：知识库扩到 N 个导演时是否方便？
- [ ] 国际化：双语/多语言 prompt 是否支持？
- [ ] 可观测：每个 prompt 生成过程能否追踪？

---

## 5. 验收标准

### 功能验收
- ✅ 121/121 现有自检不破
- ✅ 200+ E2E 测试全过
- ✅ 63 导演 12 维字段 100% 完整
- ✅ 45+ 作品真实可引用
- ✅ 5 决策层全部接通
- ✅ output_focus 5 维真差异化
- ✅ dimension_design 5 维真注入
- ✅ 双 AI 互审无重大问题

### 文档验收
- ✅ INSTALL_GUIDE 用户能跟着装上
- ✅ doctor.py 能诊断 5 类常见问题
- ✅ FINAL_USAGE 用户知道怎么用每个模式
- ✅ AUDIT_REPORT 真实记录每个 PR 审核

### 生产验收
- ✅ 节点不显示：能自诊断 + 修复
- ✅ API 离线：模式不崩，给出明确提示
- ✅ 路径错误：提示清晰
- ✅ 中文乱码：UTF-8 全程无坑

---

## 6. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 数据来源真实性 | 知识库错误 | 联网搜索官方资料 + 交叉验证 + verifier 抽查 |
| 引擎改动破现有功能 | 121 自检失败 | 灰度实施，每步跑自检 |
| LLM 输出不可控 | 测试难做断言 | 用规则匹配 + 关键词检查，不强制格式 |
| 用户环境差异 | "装不上"反馈多 | 提供 3 种安装方式 + doctor 诊断 |
| 时间预算 | 7 阶段太长 | 优先 Phase 1+3（最大价值），其他分批 |

---

## 7. 立即开始

按子 agent 任务分配，**5 个 agent 并行启动**：
1. Agent A — 安装诊断（5 min）
2. Agent B + C + D — 63 导演档案（并行，30 min）
3. Agent E — 作品库（20 min）
4. Agent F — 引擎改造（15 min）
5. Agent G — 维度 + E2E（20 min）
6. Verifier — 全程互审（最后 10 min）

**总预算 ~60 min 达到 95% 世界顶级。**
