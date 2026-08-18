# 工作流模板总览 (Workflows Overview)

> **v3.2 - 2026-08-09**
> **8 个端到端工作流模板 JSON** (Phase 25 + Phase 28 扩展)
> **所有模板都注入灵魂 (Phase 17) + 接入审美 (Phase 28 P0) + 工程化 (Phase 28 P2)**

---

## 工作流模板清单 (8 个)

| # | 文件 | 节点数 | 复杂度 | 场景 | 导演 | 灵魂情感 | Phase |
|---|---|---|---|---|---|---|---|
| 1 | `WORKFLOW_END_TO_END.json` | 9 | 高 | 父女在厨房, 雨夜, 1998 哈尔滨 | 王家卫 | loneliness + longing F3 | 25 |
| 2 | `WORKFLOW_SHORT_DRAMA.json` | 6 | 中 | 女主被陷害入狱, 30 分钟短剧 | 诺兰 | fear + anger F5 矛盾 | 25 |
| 3 | `WORKFLOW_MV.json` | 5 | 中 | MV: 男孩雨夜寻找已逝爱人, 240 秒 | 王家卫 | longing + tenderness F2 | 25 |
| 4 | `WORKFLOW_AESTHETIC_FULL.json` | 8 | 高 | 重庆森林 663/阿菲, 1994 香港 | 王家卫 | loneliness + longing | 28 P0 |
| 5 | `WORKFLOW_VERSIONED_PIPELINE.json` | 10 | 高 | 父子拉萨布达拉宫重逢, 90 分钟 | 侯孝贤 | warm_regret + tenderness | 28 P1 |
| 6 | `WORKFLOW_MARKET_AWARE.json` | 6 | 中 | 24h 便利店密室杀人案, 悬疑片 | 诺兰 | anticipation + fear | 28 P1 |
| 7 | `WORKFLOW_CLEANUP_PUBLISH.json` | 6 | 中 | AI 剧本清理发布流程 | auto | - | 28 P2 |
| 8 | `WORKFLOW_MV_V2.json` | 6 | 中 | MV 王家卫美学 (含审美/风格指南) | 王家卫 | loneliness + longing | 28 |

---

## 1. WORKFLOW_END_TO_END.json (9 节点 - 完整电影流水线)

**场景**: 父女在厨房, 雨夜, 1998 年哈尔滨 (穿越 20 年和解)
**导演**: 王家卫 (高饱和+霓虹+冷暖对比+运动模糊)
**灵魂情感**: loneliness + longing (F3 融合)
**节点链路**: 灵魂 → 剧本架构 → 剧本正文 → 导演分镜 → 概念立项 → 美术 → 剪辑 → 调色 → 选片

**适用**: 90-120 分钟剧情长片, 顶级情感深度, 多场景复杂

---

## 2. WORKFLOW_SHORT_DRAMA.json (6 节点 - 竖屏短剧)

**场景**: 女主被陷害入狱 (悬疑+情感+逆袭)
**导演**: 诺兰 (高对比冷色调+IMAX 物理真实)
**灵魂情感**: fear + anger (F5 矛盾)
**节点链路**: 灵魂 → 短剧 → 钩子 → 角色弧光 → 对白 → 选片

**适用**: 30 分钟竖屏短剧, 抖音/快手/TikTok 平台, 强冲突高反转

---

## 3. WORKFLOW_MV.json (5 节点 - MV 流水线)

**场景**: MV 男孩雨夜寻找已逝爱人 (240 秒)
**导演**: 王家卫
**灵魂情感**: longing + tenderness (F2 辅助)
**节点链路**: 灵魂 → 垂直短剧 (变体) → 钩子 → 角色弧光 → MV

**适用**: 3-5 分钟 MV, 含 1-2 个长镜头, 慢节奏抒情

---

## 4. WORKFLOW_AESTHETIC_FULL.json (8 节点 - 完整审美工作流) ⭐ NEW

**场景**: 重庆森林 663 与阿菲, 1994 香港霓虹街道
**导演**: 王家卫
**灵魂情感**: loneliness + longing (F3 融合)
**节点链路**: **审美判断** → 灵魂 → **风格指南** → 空间一致性 → 调色 → 美术 → 选片 → 质量保证

**Phase 28 P0 接入**:
- AestheticJudgmentPro: 8 原则+6 导演+120 场景自动+专项
- StyleGuidePro: 5 风格+5 配色+6 导演+20 口诀
- 与灵魂节点 + 选片节点联动

**适用**: 王家卫/侯孝贤/陈凯歌/诺兰 等强烈视觉风格作品, 需要 8 维度全审美判断

**复杂度**: 高 | **耗时**: 30-60 分钟

---

## 5. WORKFLOW_VERSIONED_PIPELINE.json (10 节点 - 版本化全流程) ⭐ NEW

**场景**: 父子在拉萨布达拉宫门前重逢, 父亲即将离世
**导演**: 侯孝贤 (远观+长镜头+自然光+距离美学)
**灵魂情感**: warm_regret + tenderness
**节点链路**: 概念 → 剧本 → 分镜 → **审美** → **风格指南** → 导演意图 → 选片 → **版本控制** → **项目归档** → 质量保证

**Phase 28 P1 接入**:
- VersionControlPro: commit/branch/tag/rollback/diff/log/best
- ProjectArchivePro: 序列化+哈希+多格式
- StyleGuidePro: 调色风格

**适用**: 中等规模电影/剧集生产, 需要版本管理 (commit/tag/branch/rollback) + 项目归档

**复杂度**: 高 | **耗时**: 2-4 小时

---

## 6. WORKFLOW_MARKET_AWARE.json (6 节点 - 市场感知工作流) ⭐ NEW

**场景**: 雨夜中的密室杀人案, 24 小时便利店, 4 个嫌疑人
**导演**: 诺兰
**灵魂情感**: anticipation + fear
**节点链路**: **市场分析** → 概念 → 分镜 → **审美** → 钩子 → **版本控制**

**Phase 28 P1 接入**:
- MarketAudiencePro: 8 类型+5 档期+3 定位+4 维票房预测
- 基于 2024-2025 中国电影市场及观众变化趋势报告

**适用**: 从市场分析出发, 制作 5-30 亿腰部中成本悬疑/犯罪/科幻片

**复杂度**: 中 | **耗时**: 1-2 小时

---

## 7. WORKFLOW_CLEANUP_PUBLISH.json (6 节点 - 清理发布工作流) ⭐ NEW

**场景**: AI 生成的剧本需要清理后才能使用
**节点链路**: 剧本生成 → **清理** → 分镜 → **格式化** → **归档** → QA

**Phase 28 P2 接入**:
- CleanupPassPro: 反 AI + 重复 + 模板 + 空白清理
- FormatOutputPro: 8 格式 (text/md/json/yaml/xml/html/csv/srt)
- ProjectArchivePro: 序列化+哈希+多格式

**适用**: AI 生成的剧本需要清理后才能使用, 提供完整清理/格式化/归档流程

**复杂度**: 中 | **耗时**: 30-60 分钟

---

## 8. WORKFLOW_MV_V2.json (6 节点 - MV v2 含审美) ⭐ NEW

**场景**: MV 雨夜霓虹慢歌, 城市孤独, 3 分钟
**导演**: 王家卫
**灵魂情感**: loneliness + longing (F3 融合, 场景权重 0.8)
**节点链路**: 灵魂 → **审美** → **风格指南** → MV → 音乐 → 调色

**Phase 28 P0 + P1 升级**:
- AestheticJudgmentPro: 自动识别王家卫 + URBAN_EXTERIOR 场景
- StyleGuidePro: 流行+互补色+王家卫导演体系
- 灵魂注入: scene_weight=0.8 (高场景权重)

**适用**: 王家卫/侯孝贤/塔可夫斯基 风格 MV, 含灵魂注入 + 8 原则 + 6 导演 + 120 场景

**复杂度**: 中 | **耗时**: 1-2 小时

---

## 节点组合策略

### 按场景选
- **完整电影 (90+ 分钟)**: WORKFLOW_END_TO_END.json (9) / WORKFLOW_VERSIONED_PIPELINE.json (10)
- **竖屏短剧 (15-30 分钟)**: WORKFLOW_SHORT_DRAMA.json (6)
- **MV (3-5 分钟)**: WORKFLOW_MV.json (5) / WORKFLOW_MV_V2.json (6)
- **强烈视觉风格 (王家卫等)**: WORKFLOW_AESTHETIC_FULL.json (8) / WORKFLOW_MV_V2.json (6)
- **市场驱动 (悬疑/犯罪)**: WORKFLOW_MARKET_AWARE.json (6)
- **AI 清理流程**: WORKFLOW_CLEANUP_PUBLISH.json (6)

### 按 Phase 28 节点选
- **必用 8 原则 + 6 导演 + 120 场景**: WORKFLOW_AESTHETIC_FULL / WORKFLOW_MV_V2
- **必用 版本控制 + 项目归档**: WORKFLOW_VERSIONED_PIPELINE
- **必用 市场分析**: WORKFLOW_MARKET_AWARE
- **必用 清理 + 格式化 + 归档**: WORKFLOW_CLEANUP_PUBLISH

### 按导演风格选
- **王家卫** (霓虹+抽帧+冷暖): WORKFLOW_END_TO_END / WORKFLOW_MV / WORKFLOW_AESTHETIC_FULL / WORKFLOW_MV_V2
- **诺兰** (高对比冷色+IMAX): WORKFLOW_SHORT_DRAMA / WORKFLOW_MARKET_AWARE
- **侯孝贤** (长镜头+自然光+距离): WORKFLOW_VERSIONED_PIPELINE

---

## 导入方法

1. 启动 ComfyUI
2. 打开 Web 界面 (http://127.0.0.1:8188)
3. 拖拽 JSON 文件到画布, 或点 "Load" 按钮加载
4. 检查参数 (导演/情感/场景描述等)
5. Queue Prompt 运行

---

## 测试验证

- ✅ WORKFLOW_END_TO_END.json: 6/6 节点验证 (Phase 25)
- ✅ WORKFLOW_SHORT_DRAMA.json: 6/6 节点验证 (Phase 25)
- ✅ WORKFLOW_MV.json: 5/5 节点验证 (Phase 25)
- ✅ WORKFLOW_AESTHETIC_FULL.json: 8/8 节点验证 (Phase 28)
- ✅ WORKFLOW_VERSIONED_PIPELINE.json: 10/10 节点验证 (Phase 28)
- ✅ WORKFLOW_MARKET_AWARE.json: 6/6 节点验证 (Phase 28)
- ✅ WORKFLOW_CLEANUP_PUBLISH.json: 6/6 节点验证 (Phase 28)
- ✅ WORKFLOW_MV_V2.json: 6/6 节点验证 (Phase 28)

**总计 8 个工作流 / 56 节点配置 / 全部验证通过**
