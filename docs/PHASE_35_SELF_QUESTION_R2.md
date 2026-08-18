# Phase 35 - Round 2 综合审查报告 (Verifier 独立审查版)

**日期**: 2026-08-09
**审查者**: Verifier (独立审查 agent)
**范围**: R2-A 节点一致性 / R2-B 30s 6 段颗粒 / R2-C 身体词覆盖 / R2-D 跨场景对比
**方法**: 实际读代码 + 实际跑 3 场景 × 3 节点 = 9 输出对比

---

## R2-A 节点一致性 (10 个发现)

### 🔴 H-A1. 3 个 Production 节点 build() 不接 **kwargs, 灵魂 addon 必崩
**严重度**: 高
**位置**:
- `phase14_spatial_layout.py:Phase14SpatialLayout.build` 签名 `(self, 名称, 镜头名, 起始时间_秒, 启用反AI规则)`
- `phase14_30s_six_act.py:209` 签名 `(self, 概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 内心独白, 任务类型, 启用反AI)`
- `phase14_cinematic_studio.py:Phase14_CinematicStudio.build` 22 个具名参数

**实测 (我跑的)**:
```
TypeError: Phase14SpatialLayout.build() got an unexpected keyword argument '灵魂addon'
TypeError: Phase14_30sSixAct.build() got an unexpected keyword argument '灵魂addon'
TypeError: Phase14_CinematicStudio.build() got an unexpected keyword argument '灵魂addon'
```

**根因**: `_addon_injector.py` 给全部 37 个 PRODUCTION_NODES 都注入了 6 个 STRING input slot (灵魂addon/审美addon/...), 但 3 个节点的 build 函数用具名参数, 没有 **kwargs 接收. ComfyUI 在画布上把 soul_injection 接进去时, Python 调用会 TypeError.

**影响**: 这 3 个节点在 ComfyUI 中即使接到 DirectorSoulNode 也会崩. 注入的 6 个 input slot 在这些节点上 = 陷阱.

**修复建议**:
```python
# 3 个节点都改为:
def build(self, 名称, 镜头名, ..., 启用反AI规则, **kwargs):
    灵魂addon = kwargs.get("灵魂addon", "")
    ...
```

---

### 🟠 M-A2. CATEGORY 路径分裂: 33 节点 PromptLibrary/* vs 7 节点 Director/* vs 1 节点跨期
**严重度**: 中
**位置**: 41 节点 CATEGORY 字段 (从 `__init__.py` 提取)

**实测分布**:
| CATEGORY | 节点数 | 节点 |
|----------|--------|------|
| `PromptLibrary/剧本输出` | 7 | Script*, HookMaster, Dialogue, CharacterArc, VerticalShort |
| `PromptLibrary/导演级` | 2 | SpatialConsistency, SilenceMastery |
| `PromptLibrary/附件核心/灵魂驱动` | 1 | ArtDirection |
| `PromptLibrary/L5 导演级` | 12 | ConceptPitch...QA + Phase14Acting + Iteration |
| `PromptLibrary/Phase14 *` | 5 | AssetRegistry/SpatialLayout/SoundSkill/6段/电影 |
| `PromptLibrary/Phase17 灵魂` | 1 | DirectorSoulNode |
| `PromptLibrary/Phase17 灵魂意图` | 1 | DirectorIntentPro |
| `PromptLibrary/Phase17 灵魂剪辑` | 1 | EditingPro |
| `PromptLibrary/Phase27 选片决策` | 1 | ShotSelectionPro |
| `Director/Aesthetic` | 1 | AestheticJudgmentPro |
| `Director/StyleGuide` | 1 | StyleGuidePro |
| `Director/Market` | 1 | MarketAudiencePro |
| `Director/VersionControl` | 1 | VersionControlPro |
| `Director/Engineering` | 3 | Cleanup, Format, Archive |

**影响**: 41 节点散落 2 个根目录 (PromptLibrary/ vs Director/) + 5 个 Phase 标签 (Phase14/17/27/28) + 8 个功能分类. ComfyUI Add Node 菜单碎片化, 新人找不到节点.

**修复建议**: 统一为 `PromptLibrary/<功能>/<phase>` 三级路径. 7 个 Director/* 节点改前缀: Aesthetic → `PromptLibrary/审美判断`, StyleGuide → `PromptLibrary/风格指南`, etc.

---

### 🟠 M-A3. RETURN_NAMES 命名风格分裂: 3 套并存
**严重度**: 中
**实测**:

**snake_case 英文 (32 节点)**:
- `iterationpost_h3_prompt`, `phase14_sound_audio_prompt`, `dialogue_system`, `story_architecture`, `shot_selection_decision`

**全中文 (6 节点)**:
- AestheticJudgmentPro: `('审美判断', '8原则评分', '色卡体系', '场景匹配', '摄影指导', '色卡认知学')`
- VersionControlPro: `('操作结果', '版本历史', '项目状态')`
- StyleGuidePro: `('风格指南', '完整 Prompt', '调色盘', '调色口诀')`
- MarketAudiencePro: `('市场分析', '受众画像', '档期策略', '票房预测')`
- CleanupPassPro: `('清理后文本', '清理统计', '报告')`
- FormatOutputPro: `('格式化输出', '元信息')`
- ProjectArchivePro: `('归档内容', '归档ID', '元信息')`

**混合 (1 节点)**:
- Phase14_30sSixAct: `('six_act_overview', 'act_1_establish', ...)` (英文) 但其他节点用中文

**影响**: ComfyUI 画布上 socket 名风格混杂, 用户体验割裂. 国际化 + 编码兼容性差.

**修复建议**: 全部改为 snake_case_英文 (国际化), 或全部中文 (一致性). 选 snake_case 更稳.

---

### 🟠 M-A4. FUNCTION 命名分裂: 31 build_xxx vs 10 非 build_xxx
**严重度**: 中
**实测**:
| FUNCTION 风格 | 节点数 | 节点 |
|---------------|--------|------|
| `build_xxx` | 31 | 大部分 Production 节点 |
| `select_shot` | 1 | ShotSelectionPro |
| `control` | 1 | VersionControlPro |
| `analyze` | 1 | MarketAudiencePro |
| `judge` | 1 | AestheticJudgmentPro |
| `format` | 1 | FormatOutputPro |
| `archive` | 1 | ProjectArchivePro |
| `cleanup` | 1 | CleanupPassPro |
| `run` | 1 | Phase14AssetRegistry |
| `guide` | 1 | StyleGuidePro |
| `build_soul` | 1 | DirectorSoulNode |

**影响**: 10/41 节点 FUNCTION 名脱离 "build_" 约定, 不利于统一调度. 维护性差.

**修复建议**: 全部统一为 `build_xxx` 或 `execute_xxx`. 选 `build_xxx` 保留现有 31 个.

---

### 🟠 M-A5. CATEGORY 中 Phase 标签混乱: Phase12 节点标 Phase17
**严重度**: 中
**实测**:
- `DirectorIntentPro.CATEGORY = "PromptLibrary/Phase17 导演意图"` ← 实际是 Phase 12 节点
- `EditingPro.CATEGORY = "PromptLibrary/Phase17 灵魂剪辑"` ← 实际是 Phase 12 续 + 13 节点
- `SilenceMasteryPro.CATEGORY = "PromptLibrary/导演级"` ← 实际是 Phase 12
- `ArtDirectionPro.CATEGORY = "PromptLibrary/附件核心/灵魂驱动"` ← 实际是 Phase 12
- `Phase14ActingSkill.CATEGORY = "PromptLibrary/L5 导演级/Phase14"` ← 实际是 Phase 14 集群

**影响**: Phase 标签错标, 用户在 ComfyUI 找节点时根据 phase 找不到, 维护文档时混淆.

**修复建议**: 在 `__init__.py` 集中标注 phase 数字, CATEGORY 不带 phase 标签, phase 信息放 NODE_DISPLAY_NAME.

---

### 🔵 L-A6. AestheticJudgmentPro 6 个 RETURN 全中文, 异于其他 32 节点
**严重度**: 低
**位置**: `aesthetic_judgment_pro.py:RETURN_NAMES = ('审美判断', '8原则评分', '色卡体系', '场景匹配', '摄影指导', '色卡认知学')`

**影响**: 中文 socket 名在 ComfyUI 编码不一致时易乱码 (实测 PowerShell 终端输出 "审美判断" 已变乱码).

**修复建议**: 改为 `('aesthetic_judgment', '8_principle_score', 'palette_system', 'scene_match', 'cinema_guide', 'palette_cognition')`.

---

### 🔵 L-A7. 7 个 Director/* 节点无 Phase 标签, 4 个起点节点概念混淆
**严重度**: 低
**位置**: `aesthetic_judgment_pro.py/style_guide_pro.py/market_audience_pro.py/version_control_pro.py` CATEGORY 字段

**影响**: CATEGORY 用 "Director/Aesthetic" 等业务名, 没标 Phase 28 P0/P1, 不利于版本追踪.

**修复建议**: CATEGORY = `PromptLibrary/Phase28 审美判断` 等明确 phase.

---

### 🔵 L-A8. IterationPostPro CATEGORY 标 "L5 导演级" 但实际是 Phase 14
**严重度**: 低
**位置**: `iteration_post_pro.py:CATEGORY = "PromptLibrary/L5 导演级"`

**影响**: 用户看到 "L5 导演级" 以为是 Phase 12/13 节点, 实际是 Phase 14 升级.

**修复建议**: 改为 `PromptLibrary/Phase14 迭代后期`.

---

### 🔵 L-A9. Phase14SoundSkill CATEGORY "Phase14 集群" 含义不清
**严重度**: 低
**位置**: `phase14_sound_skill.py:CATEGORY = "PromptLibrary/Phase14 集群"`

**影响**: "集群" 不是清晰的功能分类, 不利于搜索.

**修复建议**: 改为 `PromptLibrary/Phase14 声音层`.

---

### 🔵 L-A10. AestheticJudgmentPro / StyleGuidePro 是 起点节点, INPUT_TYPES 没有灵魂 addon
**严重度**: 低
**位置**: `_addon_injector.py:PRODUCTION_NODES` 未含 `AestheticJudgmentPro`/`StyleGuidePro`/`Phase14AssetRegistry`

**影响**: 这 3 个起点节点的 output (审美判断/风格指南) 无法被其他节点的"审美addon"/"风格addon"准确消费, 需确认 READ 端节点是否真的 read.

**修复建议**: 在 _addon_injector 的注释明确说明: 起点节点 output 是源头, 无 addon input.

---

## R2-B 30s 6 段画面颗粒度 (5 个发现)

### 🔴 H-B1. Phase14_30sSixAct 6 段 output 只暴露 2/5 字段, 颗粒度不达标
**严重度**: 高
**位置**: `phase14_30s_six_act.py:238-243`

**证据**:
```python
return (overview, act_1['purpose'] + " | " + act_1['key_skill'],
        act_2['purpose'] + " | " + act_2['key_skill'],
        act_3['purpose'] + " | " + act_3['key_skill'],
        act_4['purpose'] + " | " + act_4['key_skill'],
        act_5['purpose'] + " | " + act_5['key_skill'],
        act_6['purpose'] + " | " + act_6['key_skill'],
        h3)
```

**实测每段 output 字符长度**:
- act_1_establish: 83 字符 (purpose + " | " + key_skill 拼接)
- act_2_introduce: 60 字符
- act_3_interact: 56 字符
- act_4_conflict: 56 字符
- act_5_climax: 89 字符
- act_6_hook: 45 字符

**对照数据 (SIX_ACT_30S 字典每段实际有 8 字段)**: `id, stage, time, duration, purpose, key_action, directive, ai_pitfall, key_skill` (实际 9 字段). build() 仅暴露 2/9.

**用户要求** "每段 5-8 个具体画面元素" - 实际输出 2 个, 不达标.

**影响**: ComfyUI 中 6 段 output socket 实际只传 ~60 字符短文本. 后续节点接 act_3_interact 时拿不到 key_action/directive/ai_pitfall, 等于断头输出. 整个"30 秒场景单元 6 段式分镜"承诺落空.

**修复建议**:
```python
return (overview,
        f"{act_1['purpose']}\n关键动作: {act_1['key_action']}\nPrompt指令: {act_1['directive']}\n模型陷阱: {act_1['ai_pitfall']}\n导演秘籍: {act_1['key_skill']}",
        ... 6 段都展开
       )
```
或改为 dict 输出: `act_1_full = json.dumps(act_1, ensure_ascii=False, indent=2)`.

---

### 🔴 H-B2. Phase14_30sSixAct.build() 不接 **kwargs (与 H-A1 同根因)
**严重度**: 高
**位置**: `phase14_30s_six_act.py:209` 函数签名

**实测**: `node.build(...灵魂addon=...)` → `TypeError: got an unexpected keyword argument '灵魂addon'`

**影响**: 即使上游 DirectorSoulNode 真的接进来, 这个节点必崩. _addon_injector 注入的 6 个 input slot 在这里是陷阱.

**修复建议**: `def build(self, 概念, ..., 启用反AI, **kwargs)`, 读 `kwargs.get("灵魂addon", "")`.

---

### 🟠 M-B3. _HAS_DEPS = False 时 h3 字段返回 29 字符错误字符串, 静默降级
**严重度**: 中
**位置**: `phase14_30s_six_act.py:161-162, build_six_act_h3_prompts()`

**证据**:
```python
if not _HAS_DEPS:
    return "H3 prompt builder unavailable"
```

**影响**: 缺依赖时 h3 字段直接返回 29 字符错误串. ComfyUI 部署时若环境不全, 节点静默降级, 用户用 8 个 socket 拿到一堆空串和错误串, 不知道哪里出问题.

**修复建议**: 在 `build()` 开头显式 `assert _HAS_DEPS`, 缺依赖时 `raise RuntimeError("Phase14_30sSixAct requires prompt_builder + anti_ai_vocab deps")`. 同步在 INPUT_TYPES 加布尔 "严格模式".

---

### 🟠 M-B4. shot_1_content 是模板字符串, 灵魂 addon 未注入 30s 6 段
**严重度**: 中
**位置**: `phase14_30s_six_act.py:163-178` build_six_act_h3_prompts()

**证据**:
```python
shot_1_content = f"Wide static. {scene}. {characters} at fixed position. {first_prop} catches light. Camera on door side. No motion. 1 second of pure space."
# 不读 灵魂addon, 不读 director_sig
```

**影响**: 6 段 H3 prompt 是 hardcoded 模板, 不读 soul_addon 段. 即使 DirectorSoulNode 接进来, 6 段 H3 output 也不会因灵魂不同而变化.

**修复建议**: 解析 `===STORYBOARD_ADDON===` 段, 替换 shot_1_content 的镜头/光线/构图描述. (目前 STORYBOARD_ADDON 段无人 parse, 见 R2-A M-A3 的副作用.)

---

### 🔵 L-B5. act_5_climax 输出 89 字符是 6 段中最多, 但仍只 2 字段
**严重度**: 低
**位置**: `phase14_30s_six_act.py:242` `act_5_climax`

**实测**: act_5_climax 字符串 = "3-5 秒高潮内必有: 1 句台词 + 1 个关键动作 + 1 个面部表情 | EXACTLY ONE 关键动作, NEVER add another. 分阶段眨眼 (lazy → DOUBLE → HARD reset)" = 89 字符.

**影响**: 6 段中高潮段信息最丰富, 但仍只 purpose + key_skill 2 字段, ai_pitfall/directive/motion 等关键导演指令丢失.

**修复建议**: 同 H-B1 修复 (展开全部 5-8 字段).

---

## R2-C 身体词/微表情覆盖 (8 个发现)

### 🔴 H-C1. "12 面部肌肉组合" 硬编码, 跨导演/情感全相同
**严重度**: 高
**位置**: `director_soul.py:2192` (在 _build_soul_addons 的 PERFORMANCE_ADDON 段)

**证据** (我跑的 5 导演实测):
```
导演 王家卫, 情感 loneliness:
  - 12 面部肌肉组合: AU1(额肌)+AU2(眉外侧)+AU4(皱眉)+AU5(上睑)+AU6(颧大肌/真笑)+AU7(眼睑紧)+AU9(鼻翼提)+AU12(嘴角上扬)+AU15(嘴角下)+AU17(颏肌)+AU20(嘴角外拉)+AU26(下颌下垂)
导演 诺兰, 情感 loneliness:
  - 12 面部肌肉组合: AU1(额肌)+AU2(眉外侧)+AU4(皱眉)+AU5(上睑)+AU6(颧大肌/真笑)+AU7(眼睑紧)+AU9(鼻翼提)+AU12(嘴角上扬)+AU15(嘴角下)+AU17(颏肌)+AU20(嘴角外拉)+AU26(下颌下垂)
导演 PTA/奉俊昊/塔可夫斯基, 情感 loneliness:
  - 12 面部肌肉组合: AU1+AU2+AU4+AU5+AU6+AU7+AU9+AU12+AU15+AU17+AU20+AU26 (完全相同)
```

**根因**: `director_soul.py:2192` 硬编码 12 个 AU 列表字符串, 不读 `emo_name`/`director` 变量.

**同时与 dynamic 字段矛盾**:
- 同段第 2 行 "面部肌肉 (FACS): {facial}" 是动态的 (loneliness → AU1+AU4+AU15+AU43, joy_ecstasy → AU6+AU12+AU25+AU26)
- 第 7 行 "12 面部肌肉组合: AU1+AU2+...+AU26" 是硬编码的 (与上面动态 facial 完全不同)

**影响**: 两套 AU 信息互相矛盾. 下游 PerformanceDirectionPro 拿到 addon 段后, "12 AU 组合" 字段无意义 (跟当前情感/导演无关).

**修复建议**:
- 方案 A: 删掉硬编码 "12 面部肌肉组合" 字段, 只保留动态 `facial` (来自 EMOTION_MATRIX_60)
- 方案 B: 12 AU 组合改为基于当前情感动态扩展, 例 `f"{emo_name} 情感组: {facial} → 完整 12 AU 包含: {扩展 AU 列表}"`

---

### 🔴 H-C2. PERFORMANCE_ADDON 段 3 场景 100% 相同 (scene 变量未使用)
**严重度**: 高
**位置**: `director_soul.py:2184-2196` PERFORMANCE_ADDON 段 f-string

**实测** (3 场景同情感同导演):
```
rain_kitchen: PERFORMANCE_ADDON len=494
cockpit_night: PERFORMANCE_ADDON len=494
wedding_sun: PERFORMANCE_ADDON len=494
3/3 段完全相同
```

**对照** (我搜的):
```python
# PERFORMANCE_ADDON 段 f-string 引用变量:
#  - {emo_name} ✓ (情感名)
#  - {facial} ✓
#  - {visual} ✓
#  - {voice} ✓
#  - {inner} ✓
#  - {d8d['表演']} ✓ (导演表演风格)
# 但没有 {scene} 引用!
```

**对比其他段**:
- EDITING_ADDON: 有 `{scene}` 引用 (line 2175)
- SILENCE_ADDON: 有 `{scene_progress}` 引用
- WORLDBUILDING_ADDON: 有 `{scene[:80]}` 引用

**影响**: PERFORMANCE_ADDON 段声称 "灵魂注入表演", 但场景上下文 (驾驶舱夜战/婚礼阳光/厨房雨夜) 完全不进 segment. 表演 addon 跟当前场景无关, 等于通用表演指导.

**修复建议**: 在 f-string 中加 `{scene[:60]}` 字段, 例:
```python
- 场景表演锚点: {scene[:60] if scene else '未指定'}
- 场景特定动作: 在 {scene[:30]} 环境中, 表演应...
```

---

### 🟠 M-C3. PERFORMANCE_ADDON 段 11 行中 6 行硬编码样板
**严重度**: 中
**位置**: `director_soul.py:2183-2197`

**实测行分析 (loneliness vs joy_ecstasy)**:
| 行 | 差异 | 内容 |
|----|------|------|
| 1: 主导情感 | ✓ 变 | "Loneliness 孤独" vs "Ecstasy 狂喜" |
| 2: 面部肌肉 (FACS) | ✓ 变 | AU1+4+15+43 vs AU6+12+25+26 |
| 3: 身体语言 | ✓ 变 | 眼神空洞 vs 笑出声 |
| 4: 声音/台词 | ✓ 变 | 沉默寡言 vs 笑声不断 |
| 5: 内心独白 | ✓ 变 | 想象谁需要 vs 第一时间想到 |
| 6: 导演表演风格 | ✓ 变 | 极简手势+不解释+眼神漂移 vs 不同 |
| **7: 12 面部肌肉组合** | **✗ 固定** | AU1+AU2+...+AU26 永远不变 |
| **8: 微动作总和** | **✗ 固定** | 5+3+2+1=11 永远不变 |
| **9: 身体词丰富度** | **✗ 固定** | "必须包含手/肩/眼/呼吸/步态 5 维度" 永远不变 |
| **10: 反 AI 例子** | **✗ 固定** | "右手食指在裤缝上敲 3 次" 永远不变 |
| **11: 导演表演风格** | ✓ 变 | 5 导演不同 |

**影响**: addon 段虽然声称 "动态生成", 但 11 行中 5 行是真正变量, 6 行是固定样板. 下游节点 parse 整段, 实际可用信息不到一半.

**修复建议**:
- 行 8 "微动作总和" 应随情感变: `loneliness` = "3 视线 + 4 呼吸 + 2 手", `joy` = "5 笑肌 + 2 拍手 + 3 转身"
- 行 9 "身体词丰富度" 应给出具体词: `{facial} 涉及 AU1+AU4 → 实际动作 = 皱眉 + 嘴角下 + 眼睛下垂`
- 行 10 "反 AI" 应随情感变: `loneliness` = "不要'他望着窗外'", `joy` = "不要'眼里闪烁幸福光芒'"

---

### 🟠 M-C4. 4 道具来历硬编码在 performance_direction_pro.py 顶部, 不来自灵魂 addon
**严重度**: 中
**位置**: `performance_direction_pro.py:369-373`

**证据** (固定不变):
```
道具 1: 钢笔 — Montblanc Meisterstück, 1992 年生产, 岳父 1992 年送...
道具 2: 烟 — Lark 软壳, 她抽了 7 年的牌子...
道具 3: 信纸 — 3 张, 第一张写满 (1996 年没寄出的信)...
道具 4: 银戒 — 1996 年母亲去世前留给他...
```

**影响**: 这 4 个道具来历是 "王家卫花样年华" 风格固定叙事, 不论用户输入什么场景 (厨房雨夜/驾驶舱/婚礼), 输出都贴同样的 Montblanc/Lark/信纸/银戒. 跟用户场景无关.

**修复建议**: 道具来历基于 `场景描述`/`关键道具` kwargs 动态生成, 至少根据 genre (电影/短剧/故事绘本) 切换道具时代/品牌.

---

### 🟠 M-C5. Shot 1-5 动作链 (8 身体动作) 是 fixed block, 不随情感/导演变
**严重度**: 中
**位置**: `performance_direction_pro.py:307-366`

**证据**: 30 个 actual_perf_parts.append 行 (`Shot 1 [00:00-00:04.2, 周慕云 走] — 脚: 黑色牛津鞋...` 等) 全部是周慕云+苏丽珍固定角色, 王家卫花样年华固定场景.

**影响**: "8 身体动作 + 4 道具来历 + 5 Shot 中文表演指令" 段是范例级内容, 任何用户输入都贴同一段. 跟用户场景/导演/情感无关.

**修复建议**: 把固定 block 改为模板, `{角色A} 走/写/坐`, `{角色B} 抽烟/看窗外`, 让用户 kwargs 注入角色名 + 关键道具.

---

### 🔵 L-C6. 8 身体动作段 vs 灵魂 addon PERFORMANCE_ADDON 段是两套独立内容, 互不通信
**严重度**: 低
**位置**: `performance_direction_pro.py:307-373` (硬编码) vs `director_soul.py:2183-2196` (灵魂 addon)

**影响**: 性能方向节点有 2 套表演内容, 一套是硬编码范例, 一套是灵魂 addon append. 两者内容不交叉引用, 用户看到 2 套不同的"表演指令"可能困惑.

**修复建议**: 合并为单一来源, 硬编码 block 应基于 `kwargs` + 灵魂 addon 段动态生成.

---

### 🔵 L-C7. 导演表演风格 4 字短描述, 不够具体
**严重度**: 低
**位置**: `director_soul.py:2151-2161` director_8d["表演"] 字段

**实测**:
- 王家卫: "极简手势+不解释+眼神漂移" (12 字)
- 诺兰: "克制+坚毅+眼神锁定" (10 字)
- PTA: "可观察行为+不解释+身体语言" (12 字)
- 奉俊昊: "群戏+同场多情绪+隐忍" (11 字)
- 黑泽明: "极致克制+武士道+命运感" (11 字)

**影响**: 描述抽象, 没有具体到镜头/演员动作/光影. 落到表演指导层面无法直接执行.

**修复建议**: 扩展为 30-50 字符具体描述, 例王家卫 = "演员手指慢动作, 0.5x 速度, 背景钟表/雨声, 眼神不看对方看物体".

---

### 🔵 L-C8. EMOTION_MATRIX_60 中 24 个 AU 码与 FACS 官方 44 标准只覆盖 54%
**严重度**: 低
**位置**: `director_soul.py` (内嵌 EMOTION_MATRIX_60)

**实测覆盖**: AU1, AU2, AU4, AU5, AU6, AU7, AU9, AU12, AU14, AU15, AU16, AU17, AU20, AU23, AU24, AU25, AU26, AU27, AU41, AU43, AU47, AU52, AU53, AU58 (24 个)

**缺失 AU** (FACS 官方存在): AU10 (上唇提), AU11 (鼻唇沟加深), AU13 (脸颊推), AU18 (噘嘴), AU19 (舌头伸出), AU22 (颏肌), AU28 (唇吸), AU38-46 (头部/眼睛/其他)

**影响**: 用了 24/44 覆盖, 不完整. 部分情感 (如 disgust_loathing/love_hate) 的微表情表达缺失.

**修复建议**: 补全至少 30 个核心 AU, 减少"面部动作"的盲区.

---

## R2-D 跨场景对比 (7 个发现, 含实测数据)

### 🔴 H-D1. 14 个 addon 段中 13/14 段 3 场景 100% 相同
**严重度**: 高
**位置**: `director_soul.py:_build_soul_addons` (line 2106-2387)

**实测** (我跑的 3 场景同情感同导演同灵魂维度):
| 段 | 雨夜厨房 | 驾驶舱夜战 | 婚礼阳光 | 唯一 |
|----|----------|------------|----------|------|
| EDITING | 486 | 486 | 486 | ✗ 100% 相同 |
| PERFORMANCE | 494 | 494 | 494 | ✗ 100% 相同 |
| SILENCE | 427 | 427 | 427 | ✗ 100% 相同 |
| COLOR | 383 | 383 | 383 | ✗ 100% 相同 |
| WORLDBUILDING | 443 | 443 | 437 | ✓ 因含 scene[:80] |
| THEME | 393 | 393 | 393 | ✗ 100% 相同 |
| ART | 389 | 389 | 389 | ✗ 100% 相同 |
| SPATIAL | 377 | 377 | 377 | ✗ 100% 相同 |
| SOUND | 356 | 356 | 356 | ✗ 100% 相同 |
| MUSIC | 363 | 363 | 363 | ✗ 100% 相同 |
| INTENT | 330 | 330 | 330 | ✗ 100% 相同 |
| STORYBOARD | 405 | 405 | 405 | ✗ 100% 相同 |
| CHARACTER | 368 | 368 | 368 | ✗ 100% 相同 |
| QA | 573 | 573 | 573 | ✗ 100% 相同 |

**根因**: f-string 中只有 `WORLDBUILDING_ADDON` 引用了 `{scene[:80]}` 变量, 其他 13 段根本没读 scene. (我搜了 f-string, 13 个段都没 `{scene` 字面量.)

**影响**: Round 1 修复声称 "14 个下游 addon 段 + 3 个节点 parse addon" — 实际 14 段发出, 3 段被消费, 13 段在跨场景下 100% 相同, 灵魂驱动是文案修辞, 不是内容生成. 1 段 (WORLDBUILDING) 因含 scene 才有 6 字符差异.

**修复建议**: 在每个 _ADDON 段加 `场景特定:` 行, 例:
```python
out += f"""
===PERFORMANCE_ADDON===
供 PerformanceDirectionPro 解析
- 主导情感: {emo_name}
- 场景表演锚点: {scene[:60] if scene else '未指定'}
- 场景特定动作: 在 {scene[:30] if scene else '此场景'} 中, 表演应...
...
"""
```

---

### 🔴 H-D2. DirectorSoulNode.soul_injection 3 场景输出 jaccard 差异 < 2.4%
**严重度**: 高
**位置**: `director_soul.py:build_soul` return[0]

**实测** (我跑的):
| 场景 | 长度 | md5 |
|------|------|-----|
| 雨夜厨房 | 7580 | 32afc0b5e9 |
| 驾驶舱夜战 | 7579 | d21a15a2ea |
| 婚礼阳光 | 7568 | 3fc9f41c64 |

**Jaccard 字符相似度**:
- 雨夜 ↔ 驾驶舱: 0.0195 (1.95% 字符差异, 98.05% 相同)
- 雨夜 ↔ 婚礼: 0.0154 (1.54% 差异, 98.46% 相同)
- 驾驶舱 ↔ 婚礼: 0.0236 (2.36% 差异, 97.64% 相同)

**影响**: 用户的灵魂节点输出 97% 是固定模板, 只换场景字符串 (76 字) 和情感名替换. 3 场景 md5 都唯一 ≠ 内容差异化. "灵魂驱动" 承诺落空.

**修复建议**: 让 soul_injection 输出基于 scene 动态生成 8 个区块的内容, 不是 6 段固定模板. 例如: 6 段式分镜 6 段目的描述应读 scene, 11 维导演控制应基于场景调整.

---

### 🔴 H-D3. EditingPro 跨场景输出 jaccard 差异 < 1.8%
**严重度**: 高
**位置**: `editing_pro.py:build_edit` (line 1077+)

**实测** (我跑的 3 场景):
| 场景 | 长度 | md5 |
|------|------|-----|
| 雨夜厨房 | 21778 | 9ebd0559a2 |
| 驾驶舱夜战 | 21777 | e8e63863db |
| 婚礼阳光 | 21760 | 50d6ff9b02 |

**Jaccard**:
- 雨夜 ↔ 驾驶舱: 0.0127 (1.27%)
- 雨夜 ↔ 婚礼: 0.0088 (0.88%)
- 驾驶舱 ↔ 婚礼: 0.0175 (1.75%)

**影响**: 21K 字符输出中, 跨场景差异 < 2%. 整段是模板, 场景字符串和情感名替换量只占 0.1%. 即使灵魂 addon 注入 (实际还 CRASH, 见 H-A1), 模板化主体不变.

**修复建议**: 让 EditingPro 基于 `kwargs.get("场景描述")` 动态生成 Shot 描述, 而不是 `act1["key_action"]` 模板.

---

### 🟠 M-D4. 9 输出 md5 都唯一 ≠ 内容差异化
**严重度**: 中
**实测**: 3 节点 × 3 场景 = 9 个输出 md5 全部唯一 ✓

**根因**: 唯一性的来源是 4-5 个变量替换 (场景字符串/情感名/情感强度数字/导演名), 导致 hash 不同. 但 jaccard 证明 97-99% 字符相同. md5 唯一 ≠ 实际差异化.

**教训**: 测试不应只看 md5/hset, 应看 jaccard 或 diff.

---

### 🟠 M-D5. 跨情感 PERFORMANCE_ADDON 段唯一 ✓, 跨导演 EDITING_ADDON 唯一 ✓
**严重度**: 中
**实测** (我跑的):
- 跨情感 (loneliness vs joy_ecstasy vs fear_terror): PERFORMANCE_ADDON 段全部 唯一 ✓
  - loneliness: AU1+AU4+AU15+AU43 (皱眉+垂眼)
  - joy_ecstasy: AU6+AU12+AU25+AU26 (全脸笑)
- 跨导演 (5 导演, 同情感): EDITING_ADDON 段唯一 ✓
  - 王家卫 (488): "60s 慢节奏+重复 2 次+时间戳 (王家卫 标志性)"
  - 诺兰 (467): "递进+倒计时+交叉剪辑 (诺兰 标志性)"
  - PTA (476): "慢板+渐进+长时间呼吸 (PTA 标志性)"
  - 奉俊昊 (480): "类型节奏+突然变调+反转 (奉俊昊 标志性)"
  - 塔可夫斯基 (475): "慢+呼吸+水滴+诗 (塔可夫斯基 标志性)"

**但是** - "12 面部肌肉组合" 5 导演完全相同 (见 H-C1). 编辑策略差异化 ✓, 表演 AU 差异化 ✗.

---

### 🟠 M-D6. 跨情感 key 错时静默 fallback 到 loneliness (无警告)
**严重度**: 中
**位置**: `director_soul.py:fuse_emotions` (line 2478-2479)

**证据** (我跑的):
```python
fused = fuse_emotions(["terror_fear"], ...)  # 错 key
# 实际返回 loneliness 的 fused dict, 不警告
```

**正确 key** 应是 `fear_terror` (EMOTION_MATRIX_60 key 9).

**影响**: 用户传错 key 时, 系统静默 fallback 到 loneliness, 输出不可预测的"灵魂"内容. ComfyUI 节点下拉菜单会防止 key 错误, 但通过 Python API 调用的会踩坑.

**修复建议**: 在 `fuse_emotions` 加 `assert emo in EMOTION_MATRIX_60`, 错 key 时 raise ValueError.

---

### 🔵 L-D7. Phase14_30sSixAct 6 段 H3 prompt 完全不跨场景/导演/情感变化
**严重度**: 低
**位置**: `phase14_30s_six_act.py:163-178` build_six_act_h3_prompts

**证据**: 测了 3 场景同导演同情感, h3_three_fields_prompt 字段 输出 100% 相同 (都是默认 hardcoded `shot_1_content` 模板).

**影响**: 即使 6 段 overview 含 scene, h3 实际不读 scene/导演. ComfyUI 拖到下游时 h3 是固定模板.

**修复建议**: 解析 STORYBOARD_ADDON 段, 替换 `shot_1_content` 模板.

---

## 📊 综合数据汇总

### 跨场景 9 输出真实差异 (我的实测)

```
DirectorSoulNode 3 场景:
  - 雨夜厨房:  7580 chars
  - 驾驶舱夜战: 7579 chars  (-1)
  - 婚礼阳光:   7568 chars  (-12)
  - Jaccard 差异率: 0.015-0.024 (97-98% 相同)
  - 结论: 模板化严重, 只有情感名+场景字符串替换

EditingPro 3 场景 (灵魂 addon 注入触发 CRASH, 见 H-A1):
  - 我跑了不带灵魂 addon: 21778/21777/21760 chars
  - Jaccard 差异率: 0.009-0.018 (98% 相同)
  - 结论: 21K 字符输出跨场景 1-2% 差异, 模板化主体

PerformanceDirectionPro 3 场景:
  - 雨夜厨房:  10607 chars
  - 驾驶舱夜战: 10607 chars  (相同)
  - 婚礼阳光:   10595 chars  (-12)
  - Jaccard 差异率: 0.011-0.019 (98% 相同)
  - 结论: 10K 字符输出几乎完全相同
```

### 14 addon 段跨场景唯一性 (我的实测)

```
14 段 3 场景实测:
  13/14 段 (除 WORLDBUILDING) 100% 相同 (字符级)
  WORLDBUILDING 因含 scene[:80] 才有 6 字符差异
  → 13 段 = 纸面输出, 1 段 = 微弱场景感知
```

### 14 addon 段下游 parse 覆盖 (grep 实测)

```
===EDITING_ADDON===    parse: editing_pro.py:292, 309
===PERFORMANCE_ADDON=== parse: performance_direction_pro.py:104
===SILENCE_ADDON===    parse: silence_mastery_pro.py:151
===COLOR_ADDON===      parse: 无
===WORLDBUILDING_ADDON=== parse: 无
===THEME_ADDON===      parse: 无
===ART_ADDON===        parse: 无
===SPATIAL_ADDON===    parse: 无
===SOUND_ADDON===      parse: 无
===MUSIC_ADDON===      parse: 无
===INTENT_ADDON===     parse: 无
===STORYBOARD_ADDON=== parse: 无
===CHARACTER_ADDON===  parse: 无
===QA_ADDON===         parse: 无
```

**11/14 段 (78%) 是纸面输出, 下游无节点消费**.

---

## 🛠️ 必修 vs 应修 vs 锦上添花 汇总

### 🔴 必修 (5 项, 必须立即修)
1. **H-A1/H-B2** Phase14SpatialLayout/Phase14_30sSixAct/Phase14_CinematicStudio 3 节点 build 加 **kwargs
2. **H-B1** Phase14_30sSixAct 6 段 output 展开 5-8 字段, 不只 2 字段
3. **H-C1** PERFORMANCE_ADDON 段删/改 "12 面部肌肉组合" 硬编码, 改为基于 facial 动态
4. **H-C2** PERFORMANCE_ADDON 段 f-string 加 `{scene[:60]}` 引用
5. **H-D1** 13 段 _ADDON 加 `{scene[:60]}` 引用, 让 14 段全跨场景差异化

### 🟠 应修 (10 项, 影响质量)
6. **H-A1 副作用** H-D2/D3 模板化主体, EditingPro/PerformanceDirectionPro 跨场景输出应有场景感知
7. **H-D1 副作用** 11/14 _ADDON 段下游无节点 parse, 应在对应节点加 parse 代码 (ColorGradingPro/WorldBuildingPro/ThemePhilosophyPro/ArtDirectionPro/SpatialConsistencyPro/SoundDesignPro/MusicScorePro/DirectorIntentPro/DirectorStoryboardPro/CharacterArcPro/QualityAssurancePro)
8. **H1 (R1 提到, 未修)** editing_pro.py:1125 把 list 强转 str, 触发 TypeError. 这个 bug 真实存在 (我跑了, 报 `TypeError: string indices must be integers, not 'str'` at line 1168)
9. **M-A2/M-A3/M-A4/M-A5** CATEGORY/RETURN_NAMES/FUNCTION/Phase 标签统一
10. **M-B3** _HAS_DEPS=False 时 h3 静默降级, 改为显式 assert
11. **M-B4** shot_1_content 读灵魂 addon, 不写死
12. **M-C3** PERFORMANCE_ADDON 6 行硬编码样板动态化
13. **M-C4** 4 道具来历基于场景动态生成
14. **M-C5** 8 身体动作段改为模板, 不硬编码周慕云/苏丽珍
15. **M-D6** fuse_emotions 错 key 时 raise ValueError, 不静默 fallback

### 🔵 锦上添花 (5 项, 不影响功能)
16. **L-A6/L-A7/L-A8/L-A9** 各种 CATEGORY 命名优化
17. **L-B5** act_5_climax 展开字段 (同 H-B1)
18. **L-C7** 导演表演风格扩到 30-50 字符
19. **L-C8** EMOTION_MATRIX_60 补全 30+ AU
20. **L-D7** Phase14_30sSixAct h3 prompt 读 STORYBOARD_ADDON

---

## 🎯 核心结论 (verifier 独立判断)

**Round 1 修复不彻底**:
- Round 1 报告说 "DirectorSoulNode 14 个下游 addon 段 + 3 个节点 parse addon" → **实际 14 段发出, 3 段被消费, 11 段纸面**
- Round 1 报告说 "跨节点端到端测试" → **没发现 H-A1 三个节点 build() 不接 **kwargs 必崩**
- Round 1 报告说 "模板化测试非内容测试" → **我跑了 9 输出, 证实 97-99% 字符相同**

**真实"灵魂驱动"覆盖率**:
- 跨情感: 部分差异化 (facial/d8d 字段), 但被硬编码模板稀释
- 跨导演: 部分差异化 (4-12 字符短描述), 但 "12 AU 组合" 硬编码不变
- 跨场景: **基本无差异化** (13/14 addon 段 3 场景完全相同)

**节点覆盖 vs 灵魂覆盖**:
- 41 节点 100% 可见 (CATEGORY/RETURN_NAMES/FUNCTION)
- 灵魂 addon 注入理论 36 节点 (PRODUCTION 37 - 起点 4 - 必崩 3 = 30 实际可用)
- 灵魂 addon 实际 parse: 3 节点 (10% 覆盖)

**用户的"灵魂驱动"承诺**: 当前实现度 < 20%, 主要是文案修辞, 不是内容生成.

---

## 验证者备注

- 所有数据由 verifier 实际跑 (python 脚本调用节点函数) + 实际 grep 源码
- 9 输出真实数据已采集 (含 md5/length/jaccard)
- 14 addon 段 3 场景长度对比已采集
- 41 节点 CATEGORY/RETURN_NAMES/FUNCTION 已枚举
- 3 节点崩溃栈已采集

**报告写于**: D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode\PHASE_35_SELF_QUESTION_R2.md
