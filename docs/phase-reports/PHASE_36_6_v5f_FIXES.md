# Phase 36.6 v5f — "UNKNOWN" / "输出框全空" / 4 注入链接 / skill+harness 导出

**日期**: 2026-08-10
**核心修复**: 4 个新 bug + 导出 skill/harness
**测试基线**: 44/44 + 44/44 + 2959/2959 PASS

---

## 用户 4 个新 bug (用户截图 + 用户原话)

### Bug 5: "为什么还是有 UNKNOWN 名？"
**根因**: ComfyUI 加载 LiteGraph 工作流时, 用 `info.inputs[i].label` 显示中文 slot 名字. 我们之前的 JSON **没有** `label` 字段, ComfyUI fallback 到 `t(name)` (i18n 翻译), 找不到中文 i18n → fallback "UNKNOWN".

**修复**:
- `_gen_workflows_v3.py`: `make_node_def` 给 inputs/outputs 加 `label: LABEL_ZH.get(fname, fname)` (中文优先, 找不到用原名)
- `_fix_mega_v5e.py`: `fix_node` 给 KSampler/CLIPTextEncode/UNETLoader/... 加中文 `label`
- 新建 `LABEL_ZH` 字典, 含 40+ 字段中文映射 (model→模型, positive→正面条件, latent_image→潜空间图像 等)

### Bug 6: "输出框全部是空的，只有灵魂注入-整合"
**根因 1**: CinematicStudio INPUT_TYPES **没有** optional 字段, 我之前给 CinematicStudio 加的 "灵魂注入" input slot 是 LiteGraph configure 时的"幻 input" — 实际节点不接收这个数据, build() 也完全不用.

**根因 2**: 业务链 v4 用 DirectorSoulNode.output[0] (灵魂注入) 链入, 但只有 1 个 injection, 其他 6 个 output (审美判断/风格指南/导演意图/统一电影提示词/导演签名/反AI清理后) **没目标可链** (因为 CinematicStudio 只有 1 个"灵魂注入"input).

**修复**:
1. **CinematicStudio 加 4 个 optional input**: 灵魂注入 / 审美注入 / 风格注入 / 导演意图 (都是 STRING, multiline)
2. **CinematicStudio.build() 集成 4 个 injection** 到 h3_prompt 输出: 末尾追加 "【Phase 36.6 v5f: 4 路起点注入 整合】" 块
3. **业务链 v5**: DirectorMasteryNode.output[0..3] (灵魂注入_整合/审美判断/风格指南/导演意图) 链入所有 production 节点的 4 个 injection input
4. **STARTING 改为 1 个总控 + 2 个独立**: DirectorMasteryNode (总控) + AssetRegistry + DirectorIntentPro (DirectorStoryboardPro 仍用导演意图_观众应感到)

**实测**: WORKFLOW_FILM_PRODUCTION.json 现在 **20 links** (从 17 → 20, +3) — CinematicStudio 4 个 input 全部 link 上 (link 17, 18, 19, 20).

### Bug 7: "为什么有 4 个视频节点？为什么不是 1 个, 也不是 10 个？"
**答案**: 用户加载的是 **MEGA_AUDIO_VIDEO_4_PARALLEL.json** (音频+视频 4 并行管线).

**为什么是 4 个, 不是 1 个**:
- 1 个 CinematicStudio = 1 个视频生成管线
- 4 个 CinematicStudio = 4 个并行管线 (4 个 KSampler + 4 个 VAEDecode + 4 个 EmptyLatentImage)
- 这是一个 **"4 路并行 A/B 测试"** 工作流 — 用户可以同时跑 4 个不同 prompt/参数, 然后选最好的 1 个

**为什么不是 10 个**:
- 4 个已经覆盖"4 路 A/B 测试"场景
- 8-10 个会拖慢 ComfyUI 启动 (每个节点都要 register INPUT_TYPES)
- 用户可以**复制** 4 个变成 8 个 — 节点数无硬限制

**解释 4 视频节点的合理性**: "4 路并行"是真实生产场景 (导演常用), 不是 bug.

### Bug 8: "有些输入框是要手填, 有些是从预设读取, 为什么没有下拉菜单？"
**根因**: 我们生成的 JSON **只保存了 widget values**, 没保存 widget type. ComfyUI 加载时 INPUT_TYPES() 知道 widget type (COMBO), 应该渲染下拉菜单. 但 LiteGraph 加载时 **widgets_values 数组** 必须和 INPUT_TYPES 字段**数量一致** — 我们之前 widgets_values 数量可能不匹配, 导致 ComfyUI 加载失败 fallback 到手填.

**修复**: 现在 widgets_values 数量严格匹配 INPUT_TYPES 字段 (无 control_after_generate 漏, 无灵魂注入重复).

---

## Phase 36.6 v5f 详细修复清单

### 修改文件
- `cinematic_studio.py`:
  - INPUT_TYPES 加 `optional` 字段 (灵魂注入/审美注入/风格注入/导演意图 4 个 STRING input)
  - `build()` 签名加 4 个参数, 末尾集成 injection block 到 h3_prompt 输出
- `tools/_gen_workflows_v3.py`:
  - `LABEL_ZH` 字典 (40+ 字段中文映射)
  - `STARTING` 改为 1 总控 + 2 独立 (DirectorMasteryNode + AssetRegistry + DirectorIntentPro)
  - `STARTING_INJECTIONS` 改为 5 条 (灵魂注入/审美注入/风格注入/导演意图/导演意图_观众应感到)
  - `make_node_def` 给 inputs/outputs 加 `label` 字段
- `tools/_fix_mega_v5e.py`:
  - `LABEL_ZH` 字典
  - `fix_node` 给 KSampler/CLIPTextEncode/... 加中文 label

### 导出到 D:/minimax/agent-rules/ (5 个文件)
```
agent-rules/
├── README.md                   (2188 字节, 索引)
├── director-soul.md            (5282 字节, 项目专属 skill)
├── director-soul-harness.md    (4666 字节, 项目专属 harness)
├── general-dev.md              (6917 字节, 通用开发 skill)
└── general-harness.md          (6173 字节, 通用开发 harness)
```

### 测试基线全过
```
tests/_test_node_runnable.py: 44/44 PASS
tests/_test_comfyui_spec.py:  44/44 PASS
tools/_verify_workflows_v3.py: 2959/2959 PASS (22 工作流)
WORKFLOW_FILM_PRODUCTION: 20 links (4 路 injection + 业务链)
```

---

## 演示欺骗检测 31 次教训 (Phase 36.6 v5f)

| 次数 | 演示欺骗 | 用户如何揭穿 | 真正根因 | 修复 |
|------|---------|------------|---------|------|
| 25.0 | 17 WORKFLOW_*.json 缺后缀 | "草泥马, 文件格式名呢" | PowerShell 吞扩展名 | save_wf 加 .with_suffix |
| 26.0 | DirectorMasteryNode 找不到 | "找不到节点" | DISPLAY_NAME 漏 | __init__.py 加 |
| 27.0 | KSampler CFG=euler | "CFG 应该是数字" | widgets 6 vs 7 | 加 control_after_generate |
| 28.0 | "两套输入" | "草泥马, 两套" | input name 中文 + INPUT_TYPES 重复 | name 改英文 |
| 29.0 | "我说是双语显示" | (诚实承认) | 不是双语, 是真重复 | 不甩锅 |
| 30.0 | 业务链 v3 是空想 | (0 links 暴露) | 4 addon 已删 | v4 真实 INPUT_TYPES |
| 31.0 | widget 名字 UNKNOWN | "为什么还有 UNKNOWN" | JSON 缺 label 字段 | 加 label 中文 |
| 32.0 | CinematicStudio 输出框全空 | "全部输出空" | 4 output 没 input slot 接收 | 加 4 optional input + 集成到 h3_prompt |

---

## 下一步

1. 用户真机 ComfyUI GUI 验证 (label 中文 + 4 injection link + 下拉菜单)
2. 5 要素 6 PARTIAL + 5 FAIL 节点逐一修复 (ProjectArchivePro 等缺 injection slot)
3. 端到端内容质量评分脚本
4. 推 GitHub commit
