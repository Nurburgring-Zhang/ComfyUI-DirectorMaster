# ComfyUI-PromptLibraryNode 使用指南

> **v3.2 - 2026-08-09**
> **41 节点 L5 顶级导演级 Prompt Library**

## ⚠️ 重要说明 (必读)

**这是一个 Prompt Library (提示词库),不是图像生成库。**

所有 41 节点都是 **`STRING -> STRING`** 类型:
- **输入**: 文本提示 (用户填 widgets 或从上游节点连)
- **输出**: 导演级文本 prompt (用于 Stable Diffusion / Midjourney / Sora / 可灵 / 即梦 / Runway 等 AI 视频生成工具)

**不是** ComfyUI 传统的 `IMAGE -> IMAGE` 流水线。每个节点独立运行,产生导演级文本描述。

## 41 节点 ComfyUI 标准检查

所有 41 节点都符合 ComfyUI 标准:
- ✅ `INPUT_TYPES()` (required + optional)
- ✅ `RETURN_TYPES` (元组)
- ✅ `FUNCTION` (函数名)
- ✅ `CATEGORY` (分类)

```python
# 示例: AestheticJudgmentPro INPUT_TYPES
{
    "required": {
        "输入描述": ("STRING", {"default": "", "multiline": True}),
        "导演风格": (["auto", "王家卫", ...], {"default": "auto"}),
        "场景类型": (["auto", "STUDIO_INTERIOR", ...], {"default": "auto"}),
    },
    "optional": {
        "目标情感": ("STRING", {"default": "auto"}),
        "8原则权重": ("STRING", {"default": ""}),
        "自动启用8原则": (["ON", "OFF"], {"default": "ON"}),
        "灵魂_主导情感": ("STRING", {"default": "auto"}),
        "灵魂_次要情感": ("STRING", {"default": ""}),
        "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
        "灵魂_融合模式": (["auto", "weighted", ...], {"default": "auto"}),
    }
}

RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
RETURN_NAMES = ("审美判断", "8原则评分", "色彩体系", "场景匹配", "摄影指导", "色彩心理学")
FUNCTION = "judge"
CATEGORY = "Director/Aesthetic"
```

## 怎么用 (3 种方式)

### 方式 1: 独立节点模式 (最常用) ⭐

每个节点独立运行,填 widgets 即可:

```
1. 打开 ComfyUI (http://127.0.0.1:8188)
2. 右键画布 → Add Node → Director/... → 选择节点
3. 填 widgets (参数)
4. 点 "Queue Prompt" 运行
5. 复制输出 (例如 8 维审美判断文本) 粘贴到 Midjourney/Sora
```

**适用**: 单点使用某个能力 (如只想做审美判断,或者只是想做选片)

### 方式 2: 工作流模式 (串接) ⭐

把多个节点串起来,前一个节点的 STRING 输出连到下一个节点的 STRING 输入。

**示例**: DirectorSoulNode -> AestheticJudgmentPro

```
[DirectorSoulNode]
  主导情感: loneliness
  场景权重: 0.8
  导演: 王家卫
  ...
  ├── output[0] "灵魂addon" ──> [AestheticJudgmentPro].灵魂_主导情感
  └── output[1] "fused_emotion" ──> [AestheticJudgmentPro].灵魂_次要情感
                                 (因为 DirectorSoulNode 实际输出和 AJP 的灵魂参数 slot 都是 STRING 类型)
```

**关键**: ComfyUI 中把上游节点的输出点 (右侧小圆点) 拖到下游节点的输入点 (左侧小圆点,标着 "灵魂_主导情感" 那种 STRING 类型的 input slot) 即可。

### 方式 3: 复制粘贴模式 (最稳妥)

每个节点独立运行,输出文本,然后手动复制到下一个节点的输入 widgets。

**适用**: 当你不确定 ComfyUI 连线规则,或想完全控制每个节点的参数时。

## 9 个工作流 (8 实用 + 1 矩阵)

| # | 文件 | 节点数 | 用途 |
|---|---|---|---|
| 1 | `WORKFLOW_END_TO_END.json` | 9 | 完整 90 分钟电影流程 (Phase 25) |
| 2 | `WORKFLOW_SHORT_DRAMA.json` | 6 | 竖屏短剧 30 分钟 (Phase 25) |
| 3 | `WORKFLOW_MV.json` | 5 | MV 240 秒 (Phase 25) |
| 4 | `WORKFLOW_AESTHETIC_FULL.json` | 8 | 完整审美流程 (Phase 28 P0) |
| 5 | `WORKFLOW_VERSIONED_PIPELINE.json` | 10 | 版本化生产 (Phase 28 P1) |
| 6 | `WORKFLOW_MARKET_AWARE.json` | 6 | 市场驱动 (Phase 28 P1) |
| 7 | `WORKFLOW_CLEANUP_PUBLISH.json` | 6 | 清理发布 (Phase 28 P2) |
| 8 | `WORKFLOW_MV_V2.json` | 6 | MV v2 含审美 (Phase 28) |
| 9 | `WORKFLOW_ALL_NODES.json` | 41 | 全节点矩阵 (Phase 28) |

## 节点矩阵 (41 节点全分类)

### Phase 9: 剧本拆分 (3 节点)
- `ScriptArchitecturePro` - 剧本架构 (三幕剧结构)
- `ScriptBodyPro` - 剧本正文 (完整剧本生成)
- `DirectorStoryboardPro` - 导演分镜 (60 个分镜)

### Phase 11: 专业类型 (4 节点)
- `VerticalShortDramaPro` - 竖屏短剧
- `HookMasterPro` - 钩子大师 (3 秒抓住观众)
- `DialogueMasterPro` - 对白大师
- `CharacterArcPro` - 角色弧光

### Phase 12: 导演附件 (4 节点)
- `DirectorIntentPro` - 导演意图
- `ArtDirectionPro` - 美术指导
- `SpatialConsistencyPro` - 空间一致性
- `SilenceMasteryPro` - 沉默大师

### Phase 12续+13: 生产环节 (14 节点)
- `ConceptPitchPro` - 概念立项
- `WorldBuildingPro` - 世界设定
- `ThemePhilosophyPro` - 主题哲学
- `SoundDesignPro` - 声音设计
- `MusicScorePro` - 音乐配乐
- `PerformanceDirectionPro` - 表演指导
- `CostumePropSetPro` - 服化道
- `EditingPro` - 剪辑
- `ColorGradingPro` - 调色
- `VfxPro` - VFX
- `MvPro` - MV 导演
- `PictureBookPro` - 故事绘本
- `InteractiveDramaPro` - 互动剧
- `QualityAssurancePro` - 质量 QA

### Phase 14: Hell Grind (7 节点)
- `Phase14AssetRegistry` - 资产注册表
- `Phase14SpatialLayout` - GEO 空间布局
- `Phase14ActingSkill` - 表演技能
- `Phase14SoundSkill` - 声音技能
- `IterationPostPro` - 迭代后期
- `Phase14_30sSixAct` - 30 秒 6 段
- `Phase14_CinematicStudio` - 电影效果

### Phase 17: 灵魂节点 (1 节点)
- `DirectorSoulNode` - 灵魂注入 (8 路输出)

### Phase 27: 选片决策 (1 节点)
- `ShotSelectionPro` - 8 维度评分选最佳

### Phase 28 P0: 审美判断 (1 节点)
- `AestheticJudgmentPro` - 8 原则 + 6 导演 + 120 场景 (6 路输出)

### Phase 28 P1: P1 节点 (3 节点)
- `VersionControlPro` - 版本控制 (commit/branch/tag/rollback)
- `StyleGuidePro` - 风格指南 (5 调色风格 + 5 配色)
- `MarketAudiencePro` - 市场受众 (8 类型 + 5 档期 + 3 定位)

### Phase 28 P2: 工程化 (3 节点)
- `CleanupPassPro` - 清理 (反 AI + 重复 + 模板)
- `FormatOutputPro` - 格式化 (8 格式)
- `ProjectArchivePro` - 项目归档 (序列化 + 哈希)

## 怎么组建工作流 (真实连线示例)

### 示例 1: 灵魂驱动审美判断 (2 节点)

```
[DirectorSoulNode]
  inputs (widgets):
    主导情感: "loneliness"
    次要情感: ["longing"]
    场景权重: 0.7
    导演: "王家卫"
    场景: "霓虹街道, 雨夜, 1994 香港"
  outputs (8 STRING):
    [0] 灵魂addon
    [1] fused_emotion
    [2] emotion_dimensions
    ...
  
  [0] (灵魂addon STRING) →  [AestheticJudgmentPro].input[灵魂addon]
  [1] (fused_emotion STRING) → [AestheticJudgmentPro].input[fused_emotion]
  
[AestheticJudgmentPro]
  inputs (widgets + slot):
    输入描述: "王家卫 1994 霓虹 雨夜"
    灵魂addon: <从 DirectorSoulNode 连过来>
    fused_emotion: <从 DirectorSoulNode 连过来>
  outputs (6 STRING):
    [0] 审美判断
    [1] 8原则评分
    ...
```

### 示例 2: 完整 5 节点流水线 (灵魂→审美→风格→调色→归档)

```
DirectorSoulNode (灵魂注入)
  ↓
AestheticJudgmentPro (审美判断)
  ↓
StyleGuidePro (风格指南)
  ↓
ColorGradingPro (调色)
  ↓
ProjectArchivePro (项目归档)
```

每一步的输出 STRING 连到下一步的某个 STRING 输入 slot。

## 重要提示

1. **节点输出是 prompt 文本,不是图像/视频** — 这是 prompt library
2. **真实连线和复制粘贴都支持** — 选你熟悉的方式
3. **每个节点独立可运行** — 不依赖其他节点也能用
4. **8 原则 + 6 导演 + 120 场景 + 60 情感全部内置** — 不用担心参数不够
5. **灵魂/审美/选片/版本/归档/工程化全部到位** — 41 节点覆盖完整导演流程
