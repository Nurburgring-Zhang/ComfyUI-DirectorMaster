# 节点输入指南 (Node Input Guide)

> **v3.1 - 2026-08-09**
> **33 节点完整输入字段说明**
> **灵魂节点统一 4 字段 (主导/场景权重/次要/融合模式)**

---

## 一、灵魂统一字段 (所有节点都有)

接入灵魂的节点统一暴露以下 4 个灵魂字段（**灵魂节点 v1.0 必加**）:

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `灵魂_主导情感` | COMBO (60 情感 + auto) | "auto" | 主导情感。可选: `loneliness` / `fear` / `warm_regret` / `lucid_despair` / `tenderness` / `joy` / `anger` / `sadness` 等; 或 `auto` 由场景自动推断 |
| `灵魂_场景权重` | FLOAT 0-1 | 0.5 | 场景权重。0=轻度情绪, 0.5=普通, 0.95+=高潮/关键 |
| `灵魂_次要情感` | COMBO (60 情感 + none) | "none" | 次要情感 (单选)。`none`=无次要; `loneliness`/`longing` 等作为次要 |
| `灵魂_融合模式` | COMBO (8 选项) | "auto" | 融合公式: `auto` / `F1_单情感主导` / `F2_双情感主次融合` / `F3_双情感对等融合` / `F4_三情感递进融合` / `F5_矛盾情感爆炸` / `F6_复合情绪三角` / `F7_情感转化` |

**60 情感完整列表** (在 `DirectorSoulNode` 节点的下拉里全部可见):
- Plutchik 24: `joy_serenity` / `joy_pleasure` / `joy_ecstasy` / `trust_acceptance` / ... / `anticipation_vigilance`
- Izard 6: `interest` / `shyness` / `guilt` / `contempt` / `shame` / `pride`
- 复合 8: `love` / `hate` / `awe` / `aggressiveness` / `optimism` / `disapproval` / `remorse`
- 状态 10: `loneliness` / `longing` / `bittersweet` / `nostalgia` / `tension` / `tenderness` / `relief` / `despair` / `hope` / `gratitude` / `wonder`
- 复杂 12: `bittersweet_pain` / `warm_regret` / `hopeless_hope` / `love_hate` / `lucid_despair` / `awed_fear` / `tender_contradiction` / `perfect_regret` / `yuan` / `chouchang` / `ji` / `chou`
- **也支持简写**: `fear` (=`fear_apprehension` 中等强度) / `joy` (=`joy_pleasure`) / `sadness` / `anger` / `surprise` / `trust` / `disgust` / `anticipation` (8 基础情感)
- **也支持中文**: `孤独`/`寂寞` → `loneliness`, `恐惧` → `fear_apprehension`, `喜悦` → `joy_pleasure`, `思念` → `longing`, `愤怒` → `anger_frustration` 等

---

## 二、节点分类与输入详解

### A. Phase 9 剧本 3 节点 (剧本流水线)

#### 1. 📖 ScriptArchitecturePro - 剧本架构 (1/3)
**输入字段**:
- `主题`: STRING - 一句话主题
- `导演风格`: COMBO (63 导演) - 王家卫/诺兰/是枝裕和/塔可夫斯基/侯孝贤/奉俊昊/黑泽明/库斯杜力卡/Scorsese/Villeneuve/Lanthimos/Gerwig 等
- `场景描述`: STRING - 场景设定
- `情绪基调`: STRING - 整体情绪
- `潜文本_情感`: STRING - 潜文本
- `导演意图_观众应感到`: STRING
- `关键道具`: STRING
- `关键参考片`: STRING
- `启用反AI规则`: BOOLEAN
- 4 灵魂字段

**典型工作流位置**: 第一个节点 → 输出给 `ScriptBodyPro`

#### 2. 📜 ScriptBodyPro - 剧本正文 (2/3)
**输入字段**:
- `故事架构_来自节点1`: STRING - 接收上一节点输出
- `导演风格_63选1`: COMBO
- `对白密度`: FLOAT - 0.1-1.0
- `场次数量`: INT
- `反AI强度`: FLOAT
- 4 灵魂字段

**典型工作流位置**: 接 `ScriptArchitecturePro` 输出 → 给 `DirectorStoryboardPro`

#### 3. 🎬 DirectorStoryboardPro - 导演分镜 (3/3)
**输入字段**:
- `剧本片段`: STRING
- `导演风格`: COMBO
- `视频时长`: FLOAT (秒)
- `分镜密度`: COMBO (low/medium/high)
- 4 灵魂字段

**输出**: 6 段分镜, 真实灵感时刻 (诺兰起手 10.4s / 塔可夫斯基 11.6s / 王家卫 13.4s 真不同)

---

### B. Phase 11 专业 4 节点 (短剧/对话/角色)

#### 4. 📱 VerticalShortDramaPro - 垂直短剧 (4/7)
**输入字段**:
- `剧本片段`: STRING
- `导演风格`: COMBO (20)
- `视频时长`: FLOAT
- `集数`: INT
- 4 灵魂字段

#### 5. 🎣 HookMasterPro - 钩子大师 (5/7)
**输入字段**:
- `钩子类型_8选1`: COMBO (身份揭秘/暴力冲突/情感爆发/性张力/金钱冲突/权谋反转/威胁生命/神秘悬念)
- `钩子时长_秒`: COMBO (3/7/15/30/60)
- `钩子强度_1_10`: INT
- `套路_11选1`: COMBO (穿越/重生/真假千金/霸总/战神/团宠/修仙/末日/女帝/换亲/马甲)
- `反转类型_8选1`: COMBO
- `主角性别`: COMBO
- `画风`: COMBO
- `受众`: COMBO
- `平台`: COMBO (ReelShort/抖音/快手/TikTok/电影)
- `实战钩子库_5选1`: COMBO
- `启用反AI规则`: BOOLEAN
- 4 灵魂字段

#### 6. 💬 DialogueMasterPro - 对白大师 (6/7)
**输入字段**:
- `对白类型_8选1`: COMBO (对话/潜文本/冲突/告白/指令/示弱/沉默/意识流)
- `对白功能_7选1`: COMBO
- `对白最大字数`: INT
- 角色 1/2: 性别/年龄/身份/口头禅/身体习惯 (10 字段)
- `场景`: STRING
- `情绪基调`: COMBO
- `潜台词方向`: STRING
- `启用反AI规则`: BOOLEAN
- 4 灵魂字段

#### 7. 👤 CharacterArcPro - 角色弧光 (7/7)
**输入字段**:
- `角色姓名`: STRING
- `角色性别`: COMBO
- `角色年龄`: INT
- `角色原型_12选1`: COMBO (Hero/Shadow/Anima 等 12 Jung 原型)
- `角色弧_7选1`: COMBO (positive/negative/flat/transformation 等)
- `欲望_Want`: STRING
- `需求_Need`: STRING
- `导演风格_8选1`: COMBO
- 6 维深度: 生理学/心理学/社会学/身体习惯/口头禅/标志性物件
- `启用反AI规则`: BOOLEAN
- 4 灵魂字段

---

### C. Phase 12 附件核心 4 节点

#### 8. 🎯 DirectorIntentPro - 导演意图
**输入字段**:
- 任务类型/类型/场景描述/导演风格 (8)
- 导演意图 5 维: 感受/情感/关系/主题/留白 (5)
- 关键道具/参考片
- `启用反AI规则`
- 4 灵魂字段

#### 9. 🎨 ArtDirectionPro - 美术指导
**输入字段**:
- 任务类型/类型/场景描述/导演风格 (4)
- 摄影指导: 8 大 DP (罗杰·迪金斯/卢贝兹基/罗曼·波兰斯基等)
- 视觉语言参数化: 焦段/光圈/景别/构图法则 (4)
- 60:30:10 色彩: 主色/辅色/点缀色 (3)
- 9 维光影: 光源类型/方向/强度/色温/软硬/比例/阴影/特殊/时间 (9)
- 情绪基调/潜文本/导演意图/关键道具/参考片 (5)
- 4 灵魂字段

#### 10. 📐 SpatialConsistencyPro - 空间一致性
**输入字段**:
- `空间类型`: COMBO (厨房/客厅/卧室/办公室/餐厅/走廊/楼梯/街头)
- `空间细节`/`空间尺寸`: STRING
- 角色 1/2: 位置
- `关键道具`: STRING
- 镜头参数: 停留秒数/连续运动/换角度次数 (3)
- 4 规则强度: 连续运动/空间稳定/镜头停留/位置可信 (4)
- 4 灵魂字段

#### 11. 🤫 SilenceMasteryPro - 沉默大师
**输入字段**:
- `场景类型`: COMBO (对话/吃饭/独处/重逢/送别/工作/睡觉)
- `场景描述`: STRING
- `实际对白数`: INT
- `沉默总时长秒`: INT
- `每句对白前停顿秒`: INT
- 5 类沉默占比: 对白前/对白间/动作后/眼神/空镜 (5)
- `导演风格`: COMBO (15 导演: 塔可夫斯基/王家卫/诺兰/小津/侯孝贤/是枝裕和 等)
- 4 灵魂字段

---

### D. Phase 12 续+13 L5 导演级 14 节点 (统一模式)

**统一输入模式** (所有 14 个):
- 任务类型/类型/场景描述/导演风格 (4 必填)
- 情绪基调/潜文本/导演意图/关键道具/关键参考片 (5 必填)
- 启用反AI规则 (1 必填)
- 4 灵魂字段

**14 个节点 + 各自领域特定字段**:

| 节点 | 领域特定字段 |
|---|---|
| **ConceptPitchPro** 💡 概念立项 (1) | (无额外, 输出 6 字段) |
| **WorldBuildingPro** 🌍 世界设定 (3) | 摄影指导 + 焦段 + 光圈 + 景别 + 构图法则 + 主色 + 辅色 + 点缀色 + 9 维光影 (15 字段) |
| **ThemePhilosophyPro** 🧠 主题哲学 (4) | 主题句_一句话 + 道德困境 + 主题类型 (3 字段) |
| **SoundDesignPro** 🔊 声音设计 (13) | (无额外, 输出 3 字段) |
| **MusicScorePro** 🎼 音乐配乐 (14) | (无额外) |
| **PerformanceDirectionPro** 🎭 表演指导 (17) | (无额外) |
| **CostumePropSetPro** 👘 服化道 (19) | (无额外) |
| **EditingPro** ✂️ 剪辑 (28) | (仅 4 灵魂 + 视频时长) |
| **ColorGradingPro** 🎨 调色 (32) | 摄影指导 + 4 维光影 (5 字段) |
| **VfxPro** ✨ VFX (33) | (无额外) |
| **MvPro** 🎵 MV 导演 (39) | (无额外) |
| **PictureBookPro** 📚 故事绘本 (40) | (无额外) |
| **InteractiveDramaPro** 🎮 互动剧 (41) | (无额外) |
| **QualityAssurancePro** ✅ 质检 (节点数 28) | (无额外) |

---

### E. Phase 14 Hell Grind 5 节点

#### 25. Phase14AssetRegistry - 资产注册
**输入**: 任务类型/类型/场景/导演/情绪/潜文本/意图/关键道具/参考片/启用反AI + 4 灵魂

#### 26. Phase14SpatialLayout - 空间布局
**输入**: 任务类型/类型/场景/导演/9 维光影 + 4 灵魂

#### 27. Phase14ActingSkill - 表演技能
**输入**: 任务类型/类型/场景/导演/情绪/潜文本 + 4 灵魂

#### 28. Phase14SoundSkill - 声音技能
**输入**: 任务类型/类型/场景/导演/情绪/潜文本 + 4 灵魂

#### 29. IterationPostPro - 迭代后期
**输入**: (Phase 14 完整字段)

---

### F. Phase 14 升级 2 节点

#### 30. Phase14_30sSixAct - 30 秒 6 段
**输入**: (Phase 14 完整字段) + 30 秒时长

#### 31. Phase14_CinematicStudio - 电影工坊 (7-10 输出)
**输入**: 完整 Phase 14 字段, 输出最大最全

---

### G. Phase 17 灵魂节点 (新增)

#### 32. DirectorSoulNode - 灵魂节点 🆕
**输入字段** (8):
- `主导情感`: COMBO (60 + auto) - 单情感输入
- `次要情感`: STRING - 逗号分隔多情感 (e.g. `"longing, remorse"`)
- `场景权重`: FLOAT 0-1
- `融合模式`: COMBO (8 选项 + auto)
- `导演`: COMBO (20 导演)
- `场景描述`: STRING
- `故事强度`: FLOAT (默认 = scene_weight)
- `场景进度`: FLOAT 0-1

**输出字段** (8):
- `soul_injection` (完整灵魂注入字符串, 1400+ 字符)
- `fused_emotion`
- `emotion_dimensions`
- `soul_dimensions`
- `soul_state`
- `director_signature`
- `scene_prompt_addon`
- `h3_alignment_addon`

**灵魂节点本身**是 8 输出, **其他节点** 接收它输出后**自己内部**再调 `soul_inject_simple` 拼到主输出头部。

---

## 三、怎么输入 (ComfyUI 操作步骤)

### 3.1 安装

1. **下载** ComfyUI-PromptLibraryNode 整个目录
2. **复制**到 `<ComfyUI 安装目录>/custom_nodes/ComfyUI-PromptLibraryNode/`
3. **重启** ComfyUI
4. 在 ComfyUI **右键 → Add Node → PromptLibrary** 分类下, 你会看到 33 个节点 (按 emoji 分类)

### 3.2 加载工作流模板

1. 打开 ComfyUI
2. **File → Load** → 选择 `WORKFLOW_END_TO_END.json`
3. 工作流自动加载, 9 个节点 + 8 条连线

### 3.3 调整输入

每个节点右键 → **Properties** 或直接在画布上点击节点 → 看到右侧参数面板 → 修改字段

**最小输入** (必填项):
- `主题`/`剧本片段`/`场景描述` (STRING) - 1 句话描述你想做的内容
- `导演风格` (COMBO) - 选一个导演
- `视频时长` (FLOAT) - 30.0/60.0/120.0 秒
- `启用反AI规则` (BOOLEAN) - true/false

**灵魂字段** (推荐设置):
- `灵魂_主导情感` - 从下拉选 (60 + auto) - 推荐 `loneliness`/`warm_regret`/`fear`/`joy`/`lucid_despair`
- `灵魂_场景权重` - FLOAT 0-1 - 默认 0.5
- `灵魂_次要情感` - 选次要 (或 `none`)
- `灵魂_融合模式` - `F3_双情感对等融合` (最常用) / `F2_主次融合` (70/30) / `F1_单情感` (100%)

### 3.4 执行

1. 节点都连好 → **Queue Prompt** (Ctrl+Enter 或右上角)
2. 每个节点运行, 输出显示在节点下方
3. **关键节点输出**:
   - `ScriptArchitecturePro` → 3 字段 (架构/结构/元素)
   - `EditingPro` → 3 字段 (灵魂 prompt / 经验矩阵 / 深度处理)
   - `Phase14_CinematicStudio` → 7-10 字段 (最全)

### 3.5 保存

**File → Save** (Ctrl+S) 保存你的自定义工作流

### 3.6 工作流模板 3 个 (我立刻写)

| 模板 | 内容 |
|---|---|
| **端到端 9 节点** | `WORKFLOW_END_TO_END.json` (灵魂 + 剧本 3 + L5 3 + 附件 2) |
| **短剧 5 节点** | (下一步写) - 短剧流水线 |
| **MV 4 节点** | (下一步写) - MV 流水线 |

---

## 四、5 条黄金规则

1. **每个节点必传 4 灵魂字段** - 否则没灵魂注入
2. **场景描述要具体** - "父女在厨房, 雨夜, 1998 年哈尔滨" 比 "家庭场景" 好 10 倍
3. **导演风格决定一切** - 王家卫 vs 诺兰 vs 是枝裕和 输出天差地别
4. **关键道具要具体** - "一封没寄出的信" 比 "旧物" 好
5. **灵魂_主导情感 + 场景权重** 是最影响输出的两个字段 - 必填

---

**发布日期**: 2026-08-09
**节点总数**: 33 (含 1 灵魂节点)
**灵魂节点**: DirectorSoulNode
**统一灵魂字段**: 主导情感/场景权重/次要情感/融合模式
