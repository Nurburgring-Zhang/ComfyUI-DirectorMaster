# 工作流目录 — 17 个真生产工作流 (Phase 36.6)

**项目**: ComfyUI-PromptLibraryNode
**版本**: Phase 36.6
**核心原则**:
- **节点 = 真专业工具** (每个节点 output 是真专业 prompt 构造器)
- **工作流 = 真生产流程** (按真实业务上下游,不约束死)
- **节点可任意组合** (用户可拆解/复用,根据需要)
- **每个工作流有明确终节点** = 真专业内容输出

---

## 📂 17 个工作流清单

| # | 文件名 | 视频类型 | 终节点 (输出) | 节点数 | links |
|---|--------|---------|--------------|------:|------:|
| 1 | `WORKFLOW_FILM_PRODUCTION.json` | 电影 (60-120min) | **CinematicStudio** | 23 | 92 |
| 2 | `WORKFLOW_SHORT_DRAMA_30S.json` | 30s 短剧 6 段 | **ThirtySecSixAct** | 11 | 32 |
| 3 | `WORKFLOW_VERTICAL_SHORT_DRAMA.json` | 竖屏短剧 (1-3min) | **VerticalShortDramaPro** | 11 | 30 |
| 4 | `WORKFLOW_DOUYIN_HOOK.json` | 抖音/快手 3-7s | **HookMasterPro + ThirtySecSixAct** | 10 | 25 |
| 5 | `WORKFLOW_FEATURE_SCRIPT.json` | 完整剧本 (60-120min) | **ScriptBodyPro + DialogueMasterPro** | 12 | 36 |
| 6 | `WORKFLOW_STORYBOARD.json` | 完整分镜 (L1-L7 7 层) | **DirectorStoryboardPro** | 11 | 32 |
| 7 | `WORKFLOW_MV.json` | MV 音乐视频 (3-5min) | **MvPro + MusicScorePro** | 10 | 25 |
| 8 | `WORKFLOW_PICTURE_BOOK.json` | 绘本 (5-10min) | **PictureBookPro** | 9 | 20 |
| 9 | `WORKFLOW_INTERACTIVE_DRAMA.json` | 互动剧 (30-60min) | **InteractiveDramaPro** | 11 | 32 |
| 10 | `WORKFLOW_BRAND_FILM.json` | 品牌宣传 (60-180s) | **CinematicStudio** | 11 | 30 |
| 11 | `WORKFLOW_MINIMALIST_PRODUCT_AD.json` | 极简产品广告 (15-30s) | **CinematicStudio** | 9 | 20 |
| 12 | `WORKFLOW_SOUND_DESIGN.json` | 完整声音设计 | **SoundDesignPro + MusicScorePro** | 11 | 30 |
| 13 | `WORKFLOW_COLOR_GRADING.json` | 完整调色 (60-30-10) | **ColorGradingPro** | 9 | 20 |
| 14 | `WORKFLOW_3D_ANIMATION.json` | 3D 动画短片 | **CinematicStudio (3D 模式)** | 11 | 30 |
| 15 | `WORKFLOW_H3_PRODUCTION.json` | H3 多模态生产 | **H3ContextIRNode** | 9 | 20 |
| 16 | `WORKFLOW_UNIVERSAL_6MODELS.json` | 6 大模型通用 prompt | **UniversalDirectorPromptNode** | 10 | 27 |
| 17 | `WORKFLOW_QA_PUBLISH.json` | 质量审核 + 发布 | **ProjectArchivePro** | 11 | 30 |

---

## 🏗️ 通用工作流架构

每个工作流都是**5 起点注入 + production 节点 + 业务链 + 终节点**:

```
[5 起点节点]                                    [终节点]
DirectorSoulNode     ┐                          CinematicStudio
AestheticJudgmentPro ├──> 4 个 addon 注入 ───>  (or 任何 production 节点)
StyleGuidePro        │     (灵魂/审美/风格/资产) │
AssetRegistry        │                          (产出真专业 prompt)
DirectorIntentPro    ┘
                          ↓
                  [production 节点]
                  ScriptArch / ScriptBody / Storyboard
                  + 业务链 link (有 input slot 时)
                          ↓
                  [终节点]
                  (接收所有 addon + 业务链输入,产出最终 prompt)
```

---

## 🎯 核心设计原则

### 1. 节点是 widget 驱动的,大部分没有"业务链 input slot"
- 节点 widget = 用户可编辑参数 (题材/导演/结构/视觉/...)
- 节点 addon slot = 接上游注入 (灵魂/审美/风格/资产 4 个)
- 业务链 slot = 极少数节点之间 (ScriptArch → ScriptBody → Storyboard)

### 2. 真实数据流 = 起点节点注入下游 4 个 addon slot
- 5 起点 (灵魂/审美/风格/资产/意图) → 注入到所有 production 节点
- 每个 production 节点至少接 1 个 addon
- 工作流 link 密度 ≥ 2.0 (links / 节点)

### 3. 节点 output 允许"备而不用"
- ComfyUI 节点 output 不必全部被消费
- 用户根据需要选择性连接
- 终节点 output = 工作流最终输出 (真专业内容)

### 4. 节点可复用,可不复用
- 同节点可出现在多个工作流 (如 CinematicStudio 在 4 个工作流)
- 节点可独立使用 (只用 1 个节点)
- 节点可拆分组合 (根据生产需要)

---

## 🔄 旧工作流清理 (Phase 36.5 之前的演示欺骗)

9 个旧工作流已备份到 `archive/_trash/`:
- WORKFLOW_END_TO_END.json (70 links 但 2 列堆叠)
- WORKFLOW_AESTHETIC_FULL.json (89 links 但孤立 output)
- WORKFLOW_ALL_NODES.json (555 links 但全是平行堆叠)
- WORKFLOW_CLEANUP_PUBLISH.json (89 links 同上)
- WORKFLOW_MARKET_AWARE.json (35 links 同上)
- WORKFLOW_MV.json / WORKFLOW_MV_V2.json (25/31 links)
- WORKFLOW_SHORT_DRAMA.json (105 links 但孤立)
- WORKFLOW_VERSIONED_PIPELINE.json (90 links 同上)

**演示欺骗 13.0 修复**: 旧工作流是"links 数量多但结构错" (一列输入 + 一列输出),不是"真多级多管线"。

---

## 📖 使用方式

### 在 ComfyUI GUI 中加载
1. 启动 ComfyUI
2. 拖拽任意 `WORKFLOW_*.json` 到画布
3. 节点自动展开,所有 widget 可编辑
4. 起点节点 (灵魂/审美/风格/资产/意图) 自动连接到下游 addon slot
5. 业务链自动连接 (ScriptArch → ScriptBody → Storyboard)
6. 运行后,终节点 output = 真专业 prompt 构造器输出

### 自定义工作流
1. 在 ComfyUI GUI 中加载任意一个工作流作为模板
2. 删除/添加/替换节点 (按需)
3. 节点可任意组合 (5 起点 + 任意 production 节点 + 任意终节点)
4. 节点 output 可选连 (ComfyUI 允许孤立 output)

### 配合 LLM 真实生成
- 节点 output 是**真专业 prompt 构造器** (含反 AI/12 套理论/5 维具体化/10 灵魂维度)
- 用任意 LLM (GPT-4/Claude/Qwen) 接收 prompt,产出真专业剧本/分镜/场景

---

## 🔧 工具

- `tools/_gen_workflows_v3.py` — 工作流生成器
- `tools/_verify_workflows_v3.py` — 工作流验证 (addon 注入 + 死节点 + 链接密度)
- `tests/_test_workflows.py` — 单元测试

---

**Phase 36.6: 17 个真生产工作流, 覆盖项目所有视频类型, 每个工作流有明确终节点.**
