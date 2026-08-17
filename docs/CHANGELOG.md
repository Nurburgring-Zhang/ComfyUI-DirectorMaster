# Changelog - PromptLibraryNode

所有版本变更记录。格式基于 [Keep a Changelog](https://keepachangelog.com/)。

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
