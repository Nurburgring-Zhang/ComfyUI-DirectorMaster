# 🔬 V6.2 审核 + 双计划对比决策文档

> 生成日期: 2026/08/11 · 项目: comfyui-DirectorMaster

---

## 一、联网调研结论(ComfyUI 2025-2026 最新标准)

来源: ComfyUI 官方文档翻译(zhuanlan.zhihu.com/p/718535264)、comfy_api/latest/_io.py、CSDN 多篇 2025/2026 节点开发指南。

| 规则 | 结论 | 我们是否合规 |
|------|------|-------------|
| INPUT_TYPES 必须 @classmethod | ✅ 是(支持下拉动态计算) | ✅ 合规 |
| RETURN_TYPES/RETURN_NAMES 长度必须相等 | ✅ 必须 | ✅ 9节点全合规 |
| optional 输入仅连线时传入函数 | 必须用 `**kwargs` 或默认值捕获 | ✅ 全用 `def build(self, **kwargs)` |
| `OUTPUT_NODE=True` | 终端节点(无下游消费也执行)必设 | ❌ **Final/Archive/Router 全未设** |
| `defaultInput:True`/`forceInput` | 让 optional 默认显示为可连线槽 | ⚠️ 未用, optional 靠手动转槽 |
| JSON-in-STRING 单线传递 | ✅ 社区通用范式(VHS/Impact-Pack 同款) | ✅ 核心数据包合规 |
| IS_CHANGED 控制缓存 | 可选 | ⚠️ 未实现(每次重跑) |
| 节点输出多 STRING | 合规(只要 RETURN_NAMES 命名清晰) | ✅ 合规 |

**关键发现**: ComfyUI 社区不反对"一个节点内多模式下拉路由"(Combo + 逻辑分支), 也不反对 JSON 数据包单线传递。我们的架构方向**符合主流范式**, 不是反模式。

---

## 二、逐行逐文件审计结果

### AUDIT 1: ComfyUI 规范合规 — ✅ 全过
9 节点全部: INPUT_TYPES 是 classmethod、RETURN_TYPES==RETURN_NAMES、FUNCTION 方法存在、optional 全用 **kwargs 捕获。

### AUDIT 2: 下游输入槽完整性 — ✅ 全过
Vibe/Art/Sound/Cinematic/Script 5 节点**全部具备**: 核心数据包槽 + AI 3槽(url/key/model) + 灵魂注入槽。

### AUDIT 3: 汇总节点定位 — ⚠️ 1 个缺陷

**回答你的问题"汇总节点是 Router 吗?"**: **不是 Router, 是 Final (DirectorMasterFinal)**。

| 节点 | 定位 | 输入 | 输出 |
|------|------|------|------|
| **🏆 Final** | **汇总终点**(你要求的"对所有上游输出作汇总"节点) | 核心数据包+5Studio主输出 | 完整制作手册/剧本视觉圣经/声音方案/导演摘要/JSON |
| 🎬 Router | 视频API路由(接H3/Seedance/Wan/Sora/Veo/短剧) | 提示词 | 12个模型专属输出 |
| 📦 Archive | 归档终态 | 文本 | 6个归档输出 |

**链路**: `Core → [5 Studio] → Final(汇总) → Router(视频API) → Archive(归档)`

### AUDIT 3 致命缺陷:
| 节点 | OUTPUT_NODE | 后果 |
|------|-------------|------|
| Final | ❌ 未设置 | 作为终点节点但不被引擎当终点, 无下游时可能不执行 |
| Archive | ❌ 未设置 | 同上 |
| Router | ❌ 未设置 | 同上 |

**这是真缺陷**, ComfyUI 要求终端交付节点设 `OUTPUT_NODE = True`。

### AUDIT 4: 冗余输入问题 — ✅ 设计正确

**回答你"场景/导演/反AI/灵魂 还需每节点重复输入吗?"**: **不需要**。

机制: 这几项虽在下游节点 `required` 里(ComfyUI 不能条件隐藏 required), 但 `build()` 里 `core.get("_场景描述") or kwargs.get("场景描述")` — **连了 Core 核心数据包 → 自动用 Core 的值, widget 输入框被忽略(仅作 fallback)**。

> ⚠️ 注意: ComfyUI 无法"连了上游就隐藏本节点 widget", 这是框架限制, 非设计缺陷。当前 `core优先/fallback widget` 是社区标准做法。

### AUDIT 5: AI 增强全覆盖 — ✅ 全过
9 节点中 7 个(Core/Vibe/Art/Sound/Cinematic/Script/Final)接 AI 增强; Router 内置 LLM 可选; Archive 纯归档(无需 AI)。AI 配置从 Core 核心数据包继承到下游(resolve_ai_config), 节点自身输入 override 优先。无 AI 时返回模板(零降级)。

### AUDIT 6: 世界顶级导演级输出 — ⚠️ 核心瓶颈

**当前架构**: `legacy 43 节点确定性模板 + ai_enhance() LLM 后处理`

| 类型 | 无 AI 输出质量 | 有 AI 输出质量 |
|------|---------------|---------------|
| 剧本/分镜 | 模板拼接(中等, 中文导演风格) | LLM 润色(可达顶级, 取决于模型) |
| 短剧/电影 | 同上 | 同上 |
| 绘本/MV | 同上 | 同上 |
| 漫剧 | ⚠️ 无专门漫剧节点(缺) | 同上 |

**薄弱环节**:
1. 无 AI 时, 模板输出是"中等导演级"而非"世界顶级"(模板固有的天花板)
2. 漫剧(漫画分镜)类型缺失
3. ai_enhance 是"模板→LLM 润色"单向流, 不是"LLM 原生生成+规则约束"
4. legacy 43 节点是 V1-V5 时代写的, 部分模板陈旧

---

## 三、两个计划

### 🅰️ 计划 A: 继续打补丁 (Patch V6.2 → V6.3)

**思路**: 在现有 9 聚合节点 + 43 legacy 架构上, 修复缺陷 + 增强模板 + 补类型。

**改动清单**:
1. **修复 OUTPUT_NODE**: Final/Archive/Router 加 `OUTPUT_NODE = True` (30 分钟)
2. **加 IS_CHANGED**: 9 节点加缓存控制 (2 小时)
3. **optional 用 forceInput**: 5 下游的 核心数据包/AI 槽加 `forceInput:True` 默认显示连线 (1 小时)
4. **补漫剧节点**: 新增 Vibe 模式"漫剧分镜" + Cinematic 模式"漫剧分镜" (1 天)
5. **增强模板深度**: 给 43 legacy 节点模板加更多世界级导演细节(镜头/光影/节奏/情绪曲线) (2-3 天)
6. **ai_enhance 升级**: 系统 prompt 加导演知识库注入(533 导演档案作 few-shot) (1 天)
7. **清理 stale 测试**: test_full_audit/test_e2e_full/test_rewrite_complete 改为 V6 适配 (半天)
8. **工作流 JSON 补 OUTPUT_NODE flags** (半天)

**工作量**: ~5-7 天 · **风险**: 低(增量, 不破坏) · **向后兼容**: ✅ 完全兼容

**能达到**:
- 无 AI: 中等→良好导演级(模板增强后)
- 有 AI: 良好→顶级导演级(取决于 LLM 模型)

**达不到**: 真正"无 AI 也世界顶级"(模板天花板)

---

### 🅱️ 计划 B: 完全重建 (Rebuild V7.0)

**思路**: 抛弃 43 legacy 包装层, 重写为原生 ComfyUI 节点。LLM 作为**主生成器**, legacy 模板降级为**降级兜底 + 规则约束器**。

**新架构**:
```
Core (LLM原生: 用533导演档案+Hell Grind规则约束LLM生成"灵魂/审美/风格/意图")
  ↓ 核心数据包(含AI配置)
[Vibe/Art/Sound/Cinematic/Script] (LLM原生: 每节点系统prompt锚定世界级导演+本域知识)
  ↓
Final (LLM原生综合: 顶级导演总监级制作手册)
  ↓
Router (视频API路由, 保持)
  ↓
Archive (归档, 保持)
```

**改动清单**:
1. **重写 9 个节点** 为原生 ComfyUI 节点(无 load_legacy 包装)
2. **每节点双模式**: `AI原生生成`(LLM 主, 规则约束) / `模板兜底`(无 AI 时高质量模板)
3. **导演知识库深度集成**: 533 导演档案 + 12 维度 + 6 色彩风格 + 9 构图法则 → LLM few-shot 注入
4. **类型补全**: 加漫剧分镜/动态漫画/竖屏短剧等所有类型
5. **OUTPUT_NODE/IS_CHANGED/forceInput** 原生实现
6. **重写所有工作流 JSON**(MEGA/MINIMAL/各类型示例)
7. **重写测试套件**(替换 stale V5 测试)
8. **打包发布 V7.0**

**工作量**: ~10-14 天 · **风险**: 中高(大改, 破坏现有) · **向后兼容**: ❌ 不兼容(节点名/接口变)

**能达到**:
- 无 AI: 良好导演级(模板兜底, 但模板需重写到高质量)
- 有 AI: **真·世界顶级导演级**(LLM 原生 + 533 导演 few-shot + Hell Grind 规则约束)

---

## 四、对比表

| 维度 | 🅰️ 计划 A 补丁 | 🅱️ 计划 B 重建 |
|------|---------------|---------------|
| 工作量 | 5-7 天 | 10-14 天 |
| 风险 | 低 | 中高 |
| 向后兼容 | ✅ | ❌ |
| 修复 OUTPUT_NODE 缺陷 | ✅ | ✅ |
| 无 AI 输出质量 | 中等→良好 | 良好(模板需重写) |
| 有 AI 输出质量 | 良好→顶级 | **真·顶级** |
| 漫剧类型补全 | ✅(加模式) | ✅(原生节点) |
| 代码整洁度 | 仍有 legacy 包袱 | 干净 |
| 测试真实性 | 半清 stale | 全重写 |
| 用户切换成本 | 零 | 需重学接口 |

---

## 五、推荐: 🅰️+🅱️ 混合 (推荐)

**不二选一, 分两阶段**:

**阶段一(立即, 1 周) — 计划 A 的必修项**:
- 修复 OUTPUT_NODE 缺陷(致命, 必须修)
- 补 IS_CHANGED/forceInput
- 清理 stale 测试
- 补漫剧类型
- ai_enhance 注入 533 导演 few-shot

→ 产出 **V6.3**: 合规 + 无致命缺陷 + 类型全 + AI 增强更强。**立即满足你历史所有要求**。

**阶段二(后续, 2 周) — 计划 B 渐进重建**:
- 逐节点重写为 LLM 原生(一个节点一个节点来, 不破坏整体)
- 每重写一个, V6.3 仍可用(双轨过渡)
- 全部重写完 → 发布 V7.0

→ 产出 **V7.0**: 真·世界顶级导演级。**不破坏 V6.3 用户**。

**理由**: 你要求"必须满足所有历史要求"(阶段一即满足) + "世界顶级导演级"(阶段二达成)。直接重建(B)风险高且会破坏现有; 只打补丁(A)达不到顶级。混合方案**既不丢现有成果, 又能达顶级**。
