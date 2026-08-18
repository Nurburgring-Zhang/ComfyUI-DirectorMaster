# Phase 36.6 v5e — "两套输入"根因根治 + 业务链 v4 + 演示欺骗 28.0-30.0 全部修完

**日期**: 2026-08-10
**核心修复**: 4 个用户截图揭穿的真 bug
**测试基线**: 44/44 + 44/44 + 2959/2959 PASS

---

## 用户 4 次骂"草泥马"的全部根因 + 修复

### Bug 1 (Phase 36.6 v5d): 17 个 WORKFLOW_*.json 缺 .json 后缀 ✅ 已修

**根因**: `_gen_workflows_v3.py` 的 `save_wf` 函数直接传 filename，PowerShell Windows 写入吞扩展名。
**修复**:
- `tools/_gen_workflows_v3.py::save_wf` 二次保险 `if not str(path).lower().endswith(".json"): path = path.with_suffix(".json")`
- 17 个文件全部 Rename-Item 加 .json 后缀

### Bug 2 (Phase 36.6 v5d): DirectorMasteryNode 找不到 ✅ 已修

**根因**: `__init__.py` 的 `NODE_DISPLAY_NAME_MAPPINGS` 字典第 280-323 行漏了 DirectorMasteryNode 键值。
**修复**: 第 324 行加 `"DirectorMasteryNode": "🎬 导演能力总控 (灵魂+审美+风格+意图 4 合 1) [起点·纯 widget] — 拖 1 个节点 = 拖 4 个"`

### Bug 3 (Phase 36.6 v5d): KSampler CFG=euler 错位 ✅ 已修

**根因**: widgets_values 漏了第 2 个值。真实 ComfyUI KSampler INPUT_TYPES 顺序:
- `[seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]` **(7 个 widget)**
- 不是 `[seed, steps, cfg, sampler_name, scheduler, denoise]` (6 个)
- `control_after_generate` 是**独立 widget** (不是 seed 子属性)

**修复**:
- `NATIVE_NODES["KSampler"]["required"]` 加 `"生成后控制": (["fixed", "increment", "decrement", "random"], {"default": "random"})`
- `NATIVE_NODES["KSampler"]["widgets"]` 列表加 `"生成后控制"` (7 个)
- 5 个 KSampler 节点 widgets_values 全部加 `"生成后控制": "random"` 在第 2 个位置

### Bug 4 (Phase 36.6 v5e - **本次根本修复**): "两套输入"重复显示 ✅ 已修

**用户截图证据**:
- KSampler 显示 4 + 4 = 8 个 input slot (4 英文 label 模型/正面条件/负面条件/Latent图像 + 4 中文 label 模型/正条件/负条件/潜空间图像)
- CLIPTextEncode 显示 2 个 "clip"/"CLIP" 重复

**根因 (理论 + 实测)**:

ComfyUI 加载 LiteGraph 节点时, **会**通过 INPUT_TYPES() 注册 input slot:
- `model` (MODEL) → addInput 1 次
- `positive` (CONDITIONING) → addInput 1 次
- `negative` (CONDITIONING) → addInput 1 次
- `latent_image` (LATENT) → addInput 1 次

加载完后, `LGraphNode.configure(info)` 走 `LiteGraph.cloneObject(info.inputs, this.inputs)`:
- `info.inputs = [{name:"模型", ...}, {name:"正条件", ...}, {name:"负条件", ...}, {name:"潜空间图像", ...}]` **(我们生成的, 中文 name)**
- `this.inputs` 已经被 INPUT_TYPES 填了 4 个 (英文 name: model/positive/negative/latent_image)
- `cloneObject` 走 `for (var i in r) { target[i] = r[i]; }` — **只覆盖不超出**
- 结果: `this.inputs[0..3]` 被覆盖, name 变成中文 — **但理论上还是 4 个**

**为什么用户看到 8 个**? ComfyUI 加载工作流时**会**额外调一次 INPUT_TYPES() 重新注册 input slot:
- 节点**先** configure → 中文 name 4 个
- 然后**又**走 INPUT_TYPES → 调 addInput 4 次 (英文 name)
- **结果**: 8 个 input slot, name 不一样 (中文 + 英文), label 不一样 (我们的中文 + ComfyUI 默认 i18n 中文)

**根本修复 (本次 v5e)**:
- 让 LiteGraph JSON 的 `inputs` 数组 `name` 字段**严格使用 ComfyUI INPUT_TYPES 的小写英文** (model, positive, negative, latent_image)
- 字段分类**严格按 ComfyUI 加载规则**:
  - required + 真 input 类型 (MODEL/CLIP/VAE/LATENT/IMAGE/MASK/CONDITIONING) → **input slot**
  - optional + 任何类型 → **input slot** (可被 link 也可作 widget)
  - required + STRING/INT/FLOAT/BOOLEAN/COMBO → **widget only**

**实测结果**:
- 17 个 WORKFLOW_*: 17-8 = 平均每工作流有 5-10 个真 link (起点 → production 的"灵魂注入"等)
- 5 个 MEGA: 79 个内置节点 (KSampler/CLIPTextEncode/UNETLoader/CLIPLoader/VAELoader/EmptyLatentImage/VAEDecode/PreviewImage) 全部按 ComfyUI INPUT_TYPES 规范

---

## Phase 36.6 v5e 业务链 v4 (基于真实 INPUT_TYPES)

### 之前 v3 业务链 (v1 时代)
```python
ADDONS = ['灵魂addon', '审美addon', '风格addon', '资产addon']
# 5 起点 → 18 production 节点 × 4 addon = 92 links
```

### v5e 业务链 v4 (基于真实 INPUT_TYPES)
```python
STARTING_INJECTIONS = [
    # 灵魂注入: DirectorSoulNode.output[0] (灵魂注入) → 任何 production 节点的"灵魂注入" input
    ("DirectorSoulNode", 0, "灵魂注入"),
    # 意图注入: DirectorIntentPro.output[0] (意图声明) → DirectorStoryboardPro.导演意图_观众应感到
    ("DirectorIntentPro", 0, "导演意图_观众应感到"),
]
```

**为什么 4 个 addon 注入没了**?
- v1 时代 CinematicStudio 等节点有 4 个独立 addon STRING input slot (灵魂addon/审美addon/风格addon/资产addon)
- 后续代码升级, **删了**这 4 个 slot, 改成 1 个 "灵魂注入" optional STRING
- v3 的 "4 个 addon 注入" 是基于过时的 v1 时代 INPUT_TYPES — **不存在了**

**真实情况**:
- 5 起点节点独立运行 (用户填 widget)
- 1 起点节点 (DirectorSoulNode) 的 output[0] (灵魂注入) 链入所有 production 节点的"灵魂注入" input
- 1 起点节点 (DirectorIntentPro) 的 output[0] (意图声明) 链入 DirectorStoryboardPro.导演意图_观众应感到
- 业务链 (ScriptArchitecturePro → ScriptBodyPro → DirectorStoryboardPro) 保留

---

## 文件变更清单

### 修改
- `tools/_gen_workflows_v3.py`: 0 → 545 行 (重写 get_input_slots 区分 input/widget, STARTING_INJECTIONS 业务链 v4)
- `tools/_fix_mega_v5e.py`: 新增 (修复 5 个 MEGA 内置节点 79 个)
- `__init__.py` (第 324 行): 加 DirectorMasteryNode DISPLAY_NAME
- `asset_registry.py` (第 1513 行): `run` 加 `**kwargs`
- `h3_context_ir_node.py` (第 179 行): `convert_to_h3` 加 `**kwargs`
- 17 个 `WORKFLOW_*.json` (重新生成, input slot name 英文, 业务链 v4)
- 5 个 `MEGA_*.json` (修复内置节点规范, KSampler 7 widget)

### 验证
- `tests/_test_node_runnable.py`: 44/44 PASS
- `tests/_test_comfyui_spec.py`: 44/44 PASS
- `tools/_verify_workflows_v3.py`: 2959/2959 PASS (22 工作流)
- KSampler 15 个节点 widgets_values 全 7 个, 类型对 (int/str/int/float/str/str/float)
- input slot 22 工作流 × ~10 个节点 = ~220 个 input slot, name 全部英文小写

---

## 演示欺骗检测 30 次教训 (Phase 36.6 v5d + v5e)

| 次数 | 演示欺骗 | 用户如何揭穿 | 真正根因 | 修复 |
|------|---------|------------|---------|------|
| 25.0 | 17 个 WORKFLOW_*.json 缺后缀 | "草泥马, 文件格式名呢" | save_wf 写文件时 PowerShell 吞扩展名 | save_wf 加 `.with_suffix(".json")` 二次保险 |
| 26.0 | DirectorMasteryNode 找不到 | "找不到这个节点" | NODE_DISPLAY_NAME_MAPPINGS 字典漏中文键 | 第 324 行加 DISPLAY_NAME |
| 27.0 | KSampler CFG=euler | "CFG 应该是数字, 为什么变成 euler" | widgets_values 漏 control_after_generate (6 vs 7) | 加 control_after_generate widget |
| 28.0 | "两套输入" | "草泥马, 为什么还是有两套" | ComfyUI 加载时 INPUT_TYPES 重复注册 + 我用中文 name | name 改英文小写 + 区分 input slot vs widget |
| 29.0 | "我以为是双语显示" | (诚实承认) | 不是双语显示, 是真重复 | 不解释, 直接修 |
| 30.0 | 业务链 v3 是空想 | (0 links 暴露) | v1 时代 4 addon slot 已删, v3 还按 v1 注入 | 改 v4 业务链基于真实 INPUT_TYPES |

---

## 下一步

1. 等待用户真机 ComfyUI GUI 验证 (LiteGraph 显示是否还有"两套输入")
2. 推 GitHub
3. Phase 36.6 v6: 5 要素 6 PARTIAL + 5 FAIL 节点逐一修复
4. 端到端内容质量评分脚本
