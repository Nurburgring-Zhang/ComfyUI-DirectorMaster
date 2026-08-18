# Phase 17 - 导演灵魂节点完整开发计划

> **核心目标**: 用情感矩阵 + 融合算法 + 灵魂维度来极限模拟世界顶级导演的"灵魂"，注入到所有 32 节点
> **开始时间**: 2026-08-08
> **当前状态**: 灵魂节点 v1.0 完成, 4 子 agent 重写 4 核心节点中

---

## 1. 背景与动机

用户在 2026-08-08 提出:
> "AI 不会有灵魂, 但是能否极限列举各种情感的特点与影响, 建立情感矩阵, 然后每次根据剧本的故事情节, 选取相应的不同的一种(大多数时间)或者两种(少数时间)或者几种情感(很少数时间)、不同的情感数量、不同的情感比例、创造力、想象力、艺术表达力、镜头语言技巧、画面氛围掌控、甚至精神状态的微调, 进行融合, 来模拟世界顶级导演的灵魂?"

**关键洞见**:
1. AI 不会有"真正的灵魂" (个人/欲望/创伤/叛逆)
2. 但可以用**情感矩阵 + 融合算法 + 灵魂维度** 来**极限模拟**
3. 灵魂必须**作为单独节点**, 注入到所有其他节点
4. 严禁模板实现 - 必须真正动态生成
5. 必须保证输出是"世界顶级导演水平" - 不能像疯子/神经病

---

## 2. 灵魂节点 v1.0 设计 (已实现)

### 2.1 核心组成 (60+ 情感)

**EMOTION_MATRIX_60** - 60+ 种情感完整定义:
- **Plutchik 8 基础情感 × 3 强度 = 24 种**
  - Joy: Serenity(0.3) / Pleasure(0.6) / Ecstasy(1.0)
  - Trust: Acceptance(0.3) / Admiration(0.7) / Surrender(1.0)
  - Fear: Timidity(0.3) / Apprehension(0.6) / Terror(1.0)
  - Surprise: Uncertainty(0.3) / Astonishment(0.7) / Amazement(1.0)
  - Sadness: Gloominess(0.3) / Sorrow(0.7) / Grief(1.0)
  - Disgust: Dislike(0.3) / Revulsion(0.7) / Loathing(1.0)
  - Anger: Annoyance(0.3) / Frustration(0.7) / Fury(1.0)
  - Anticipation: Interest(0.3) / Expectation(0.7) / Vigilance(1.0)
- **Izard 10 基础情感** (补 Plutchik): Interest / Shyness / Guilt / Contempt / Shame / Pride
- **8 大复合情感** (二元组合): Love / Hate / Awe / Aggressiveness / Optimism / Disapproval / Remorse
- **10 大状态情感**: Loneliness / Longing / Bittersweet / Nostalgia / Tension / Tenderness / Relief / Despair / Hope / Gratitude / Wonder

每种情感包含 12 字段:
- name / category / intensity / polarity / arousal
- description (情感内涵)
- visual_signs (视觉表现)
- voice_signs (声音表现)
- facial_au (FACS 12 基础表情单元)
- inner_monologue (内心独白)
- color_palette (色彩)
- music_tempo (音乐)
- director_examples (导演实例)

### 2.2 7 大融合公式 (EMOTION_FUSION_7)

| 公式 | 场景占比 | 权重分布 | 例子 |
|---|---|---|---|
| F1 单情感主导 | 70% | 100% | 王家卫《重庆森林》何志武独白 (loneliness 100%) |
| F2 双情感主次融合 | 25% | 70% + 30% | 《情感价值》父亲 (acceptance 70% + remorse 30%) |
| F3 双情感对等融合 | 20% | 50% + 50% | 《花样年华》(tenderness 50% + repression 50%) |
| F4 三情感递进融合 | 10% | 20% + 30% + 50% (随时间) | 《步履不停》兴趣→关切→悔恨 |
| F5 矛盾情感爆炸 | 5% | 50%+50% (intensity 1.0+1.0) | 《寄生虫》朴社长 (disgust 100% + fear 100%) |
| F6 复合情绪三角 | 2% | 33%+33%+33% | 《魅影缝匠》Reynolds (love+obsession+control) |
| F7 情感转化 | 1% (但最重要) | A→B 完全转化 | 《泰坦尼克号》Jack 死时 (love→grief) |

### 2.3 10 大灵魂维度 (SOUL_DIMENSIONS_10)

- D1 创造力 Creativity - 突破常规的联想能力
- D2 想象力 Imagination - 构建虚构世界
- D3 艺术表达力 Artistic Expression - 用具体形式承载抽象情感
- D4 镜头语言技巧 Camera Language Skill - 摄影机控制观众情感
- D5 画面氛围掌控 Visual Atmosphere Control - 光影色彩营造情绪
- D6 精神状态 Mental State - 创作当下的状态 (清醒/梦幻/焦虑/平静/狂热/疲惫/激进/保守)
- D7 灵感时刻 Inspiration Moment - "突然知道怎么拍"的瞬间
- D8 叛逆度 Rebelliousness - 打破规则的勇气
- D9 自我怀疑 Self-Doubt - 推动反复修改的不安
- D10 突破勇气 Breakthrough Courage - 创新但风险巨大的选择

### 2.4 灵魂状态计算 (SOUL_STATE)

```python
def compute_soul_state(story_intensity, scene_progress):
    # 灵感指数: 开头低, 中间高, 结尾中等 (钟形曲线)
    inspiration = 0.3 + 0.7 * exp(-((scene_progress - 0.4) ** 2) / 0.1)
    # 疲劳指数: 随时间累积
    fatigue = min(0.95, 0.1 + scene_progress * 0.85)
    # 怀疑指数: 故事强度越大, 怀疑越低
    doubt = max(0.2, 0.8 - story_intensity * 0.6)
    # 叛逆指数: 故事强度越大, 越可能打破规则
    rebelliousness = min(0.95, 0.4 + story_intensity * 0.5)
    return {...}
```

### 2.5 灵魂输出 (8 个输出字段)

- soul_injection (完整灵魂注入字符串)
- fused_emotion (融合情感档案 JSON)
- emotion_dimensions (强度 + 极性 + 唤醒度)
- soul_dimensions (10 灵魂维度)
- soul_state (当前灵魂状态)
- director_signature (导演签名)
- scene_prompt_addon (场景 prompt 增强)
- h3_alignment_addon (H3 三大字段增强)

---

## 3. 完整开发计划

### 阶段 1: 灵魂节点 v1.0 (已完成 ✅)
- [x] 60+ 情感矩阵
- [x] 7 融合公式
- [x] 10 灵魂维度
- [x] 灵魂状态计算
- [x] DirectorSoulNode 节点 (8 输出)
- [x] __init__.py 注册 (33 节点)
- [x] 测试期望更新 (33 节点)
- [x] 597 测试通过

### 阶段 2: 4 核心节点接入灵魂 (后台运行中 🏃)
- [ ] concept_pitch_pro.py (ConceptPitchPro) - 概念架构
- [ ] director_intent_pro.py (DirectorIntentPro) - 5 维意图
- [ ] editing_pro.py (EditingPro) - 节奏曲线 + 30s 6 段
- [ ] art_direction_pro.py (ArtDirectionPro) - 视觉语言 + 60:30:10

### 阶段 3: 28 节点接入灵魂 (待启动)
**Phase 9 剧本 3 节点**:
- ScriptArchitecturePro - 剧本结构
- ScriptBodyPro - 剧本主体
- DirectorStoryboardPro - 分镜

**Phase 11 专业 4 节点**:
- VerticalShortDramaPro - 短剧
- HookMasterPro - 钩子
- DialogueMasterPro - 对白
- CharacterArcPro - 角色弧光

**Phase 12 附件 4 节点**:
- DirectorIntentPro (阶段 2 已做)
- ArtDirectionPro (阶段 2 已做)
- SpatialConsistencyPro - 空间一致性
- SilenceMasteryPro - 沉默掌控

**Phase 12 续 + 13 环节 13 节点**:
- ConceptPitchPro (阶段 2 已做)
- WorldBuildingPro - 世界观
- ThemePhilosophyPro - 主题哲学
- SoundDesignPro - 声音设计
- MusicScorePro - 音乐
- PerformanceDirectionPro - 表演指导
- CostumePropSetPro - 服装道具
- EditingPro (阶段 2 已做)
- ColorGradingPro - 调色
- VfxPro - VFX
- MvPro - MV
- PictureBookPro - 故事绘本
- InteractiveDramaPro - 互动剧
- QualityAssurancePro - 质量保证

**Phase 14 7 节点**:
- Phase14AssetRegistry - 资产注册
- Phase14SpatialLayout - 空间布局
- Phase14ActingSkill - 表演技能
- Phase14SoundSkill - 声音技能
- IterationPostPro - 迭代后期
- Phase14_30sSixAct - 30s 6 段
- Phase14_CinematicStudio - 电影工作室

### 阶段 4: 全流程双 AI 互审
- [ ] 自我质疑
- [ ] 自我解答
- [ ] 多子 agent 验证
- [ ] 测试覆盖
- [ ] 边界情况

### 阶段 5: GitHub 发布
- [ ] 完整 commit
- [ ] Release Notes
- [ ] Push to GitHub

---

## 4. 严禁事项

### ❌ 模板实现
- 禁止 if director == "王家卫" return "固定文本"
- 必须根据 soul 真正动态生成
- 每个节点输出 ≥ 15000 字符

### ❌ 表面接入
- 灵魂不能只放在头部一段
- 必须深度影响 L1-L7 每个环节
- L4 表演要嵌入灵魂的微动作
- L5 摄影要嵌入灵魂状态的光影
- L6 声音要嵌入灵魂的 voice_signs
- L7 风格要嵌入灵魂的 color_palette

### ❌ 单情感直接套用
- 至少 70% 场景用 F1 单情感主导, 但仍需根据灵魂重新生成

### ❌ 纸面契合
- 必须真正契合, 不能是装饰性的

### ❌ 疯子/神经病输出
- 必须保证输出是"世界顶级导演水平"
- 不能失控, 不能偏离主题

---

## 5. 测试基线

- **当前**: 597/597 ✅ (33 节点)
- **目标**: 597+ ✅ (33+ 节点, 4-7 核心节点重写后)

测试文件:
- test_full_audit.py (92 测试)
- test_e2e_full.py (200 测试)
- test_phase13_audit.py (305 测试)
- **合计: 597 测试**

---

## 6. 风险与缓解

### 风险 1: 子 agent 引入 bug
**缓解**: 每批完成后立即跑 597 测试, 修复后继续

### 风险 2: 节点输出过长导致性能问题
**缓解**: 每个节点 ≥ 15000 字符, 但不超过 50000 字符

### 风险 3: 灵魂融合不自然
**缓解**: 7 融合公式严格定义, 权重自动归一化

### 风险 4: 30+ 节点重写工作量大
**缓解**: 8 子 agent 并行, 每 4 个一组, 验证后启动下一组

---

## 7. 成功标准

- [ ] 所有 32 节点接入灵魂节点
- [ ] 每个节点输出 ≥ 15000 字符
- [ ] 597 测试 100% 通过
- [ ] 至少 8 大顶级导演风格支持
- [ ] 11 维导演控制全部应用
- [ ] 3 留白 + 3 运镜全部应用
- [ ] H3 三大字段完整输出
- [ ] 191 反 AI 词表 + 10 铁律
- [ ] 严禁模板 - 真正动态生成
- [ ] GitHub 完整 commit

---

## 8. 时间表

- **2026-08-08 17:00**: 灵魂节点 v1.0 完成
- **2026-08-08 17:30**: 4 核心节点接入完成
- **2026-08-08 19:00**: 28 节点接入完成
- **2026-08-08 21:00**: 双 AI 互审 + 测试
- **2026-08-08 23:00**: GitHub 发布

---

**文档维护**: Mavis (MiniMax Code)
**最后更新**: 2026-08-08 17:30
**版本**: v1.0
