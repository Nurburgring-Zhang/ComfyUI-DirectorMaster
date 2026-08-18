# Phase 14 - Higgsfield Hell Grind + 联网研究综合整合报告

> **Higgsfield Studio** (2026-08-04 起公开 Hell Grind) + **字节 Seedance 2.5** (2026-07 上线) +
> **Luma/Hailuo/Runway 等 12+ 模型** + **Renmu2017 Hell-Grind-AIGC-Skill** 全部整合

---

## 1. 关键产品矩阵 (Higgsfield 完整)

### 1.1 AI 视频生成产品
- **Cinema Studio** (Visual Effects + 12+ 模型):
  - Kling 2.1 / 2.5 / 3.0 (快手可灵)
  - MiniMax Hailuo 02
  - Seedance Pro / 2.0 / 2.5 (字节)
  - Wan 2.2 / 2.5 / 2.6 (阿里)
  - Sora 2 (OpenAI)
  - Veo 3 / 3.1 (Google)
  - Grok Imagine 1.5 (xAI)
  - Gemini Omni Flash (Google)
- **ReelMagic**: multi-agent AI video creation (story → ready-to-watch)
- **Supercomputer**: agentic AI content creation (brief → ship)
- **Explainer**: faceless explainer video (topic → video)
- **Soul Cinema / Soul 2.0 / Soul Cast**: 角色 + 文化原生照片模型
- **Draw-to-Video**: 草图秒变电影级视频 (MiniMax + Veo 3 + Seedance Pro)
- **Higgsfield Originals**: 大师级影片

### 1.2 关键数据点
| 指标 | 值 |
|------|-----|
| 创立时间 | 2023 (USA, San Francisco) |
| 团队规模 | 15 人 (Hell Grind) |
| 预算 | 50 万美元 (40 万算力) |
| 生成期 | 14 天 |
| 生成次数 | 115,446 次 |
| 最终镜头数 | 253 个 (前 25 分钟 16,181 次) |
| 时长 | 95:06 (4096x1716 4K) |
| 资产数 | 115,501 项 |
| 合作模型 | Seedance 2.0 + Soul Cinema + Nano Banana Pro + Seedream 4.5 + GPT Image 2 |
| 电影节 | 2026 戛纳 Marché du Film |
| 媒体报道 | WSJ / Variety / BBC |
| 周边入选 | 《摸金之天机入梦》《饿塔》- 戛纳 Fantastic Pavilion |

---

## 2. Hell Grind 6 大 Skill 系统 (附件原文)

### 2.1 CINEDANCE skill (writer / auditor / workbench)
- **writer**: 按规则自动写视频 prompt
- **auditor**: 审计 prompt 是否符合规范
- **workbench**: prompt 编辑工作台

### 2.2 LIRA skill (图像 prompt 系统)
- 知道每个图像模型的弱点
- Image-to-Image 编辑
- 局部重绘

### 2.3 ACTING skill (统一表演系统)
- 场景五支柱 (5 PILLARS)
- Prompt hacks
- 角色表演主格式

### 2.4 11 阶段制作管线 (Higgsfield Filmmaking Course)
1. Name your assets (资产命名)
2. Generating locations (生成场景)
3. Generating characters (生成角色)
4. Test in Seedance (在 Seedance 测试)
5. Shoot the scene (拍摄场景)
+ 6 个配套阶段: Soundscape / Music / Cut / Color / VFX / QA

### 2.5 6 份核心文件 (Higgsfield 6 Documents)
1. **ASSET_REGISTRY** - 资产注册表 (角色/地点/道具)
2. **SCENE_MAP** - 场景地图 (固定地标/左右/距离/180° axis/光源)
3. **SHOTLIST** - 分镜表 (镜号/时长/首帧/动作/台词/声音/资产)
4. **VERSION_LOG** - 版本日志 (每版 prompt/唯一改动/生成结果/采用原因)
5. **POST_ISSUE_LIST** - 后期问题单 (手脸/文字/接缝/颜色/环境声/待补镜头)
6. **ACTING_STATE** - 表演状态 (目标/障碍/代价/策略/转折)

### 2.6 Style Prefix (12 层技术底座)
```
Style: 8K IMAX. Photorealistic — no 3D render, no game engine, no game-cutscene aesthetic.
Cinematography: floating immersive camera that lives with the actors; natural motivated light;
  painterly composed frames, strong silhouettes against the light.
Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric haze throughout.
  Key light from sky and windows only.
Color: 60:30:10 — dominant / secondary / accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow matching on-set light.
Acting: Hollywood — micro-pauses before reactions, precise eye-line, wet living eyes with catch-lights,
  visible breath and chest rise.
Physics: Gravity and inertia respected — mass has real weight, correct contact shadows. No floating props.
Composition: Rule of thirds + golden ratio. Every person moving from frame one.
Continuity: Characters, props, environment identical across every cut. No identity drift.
Technical: 24fps smooth motion. 8K detail. No jitter.
Audio: Environmental SFX only. No music. No subtitles.
```

---

## 3. Hell Grind 15 块刚性骨架 (CINEDANCE prompt skeleton)

| # | 块名 | 关键规则 |
|---|------|---------|
| 1 | SCENE CONTEXT | "EXACT N CHARACTERS — NO DUPLICATES" 头行 |
| 2 | ACTIVE REFERENCES | @角色 + @地点 + @道具 |
| 3 | LOCATION MAP | GEO SPATIAL LAYOUT + 180° axis |
| 4 | FIRST FRAME | 1 秒全景让 AI 认路 (静态 + 谁在哪) |
| 5 | FORMAT MODE | 单镜/硬切/时长/实时 |
| 6 | OPTICS | 镜头和焦点 (35mm anamorphic / 50mm spherical / 85mm portrait) |
| 7 | CAMERA | 摄影机怎么动 + 绝不动什么 (类型 + small/large amplitude + slow/fast speed) |
| 8 | ACTION TIMING | 逐秒拆, 每节拍 ≤3 句, 复杂动作从第一帧开始 |
| 9 | PHYSICS | 重量 + 接触 + 惯性 (Mass has real weight, No floating props) |
| 10 | LIGHTING | 单一光源逻辑 (Natural light only, contre-jour backlight) |
| 11 | AUDIO | 声音 + 台词 + 沉默 + 尾音 (SFX only. No music. No subtitles.) |
| 12 | CHARACTER ACTING | 5 支柱 + 身体行为 (永远不写情绪, 写可观察行为) |
| 13 | STYLE | 12 层技术底座 (Style Prefix 逐字粘贴) |
| 14 | QUALITY | 细节 + 稳定性 (Photoreal, 8K IMAX, No jitter) |
| 15 | POSITIVE CONSTRAINTS | 数量约束 (EXACTLY ONE mannequin, NEVER render a second) |

### 3.1 4 任务类型 (H3 官方)
- **T2VA** (文生视频) - 无对齐指令
- **I2VA** (图生视频) - "Picture 1 (from [Shot 1]) is fully referenced" 锚定首帧
- **FL2VA** (首尾帧) - 写从首帧到尾帧的运动路径, 末尾须明确对齐到 Picture 2
- **L2VA** (尾帧) - 反推兼容的前情状态, 让动作逐步收敛到尾帧

### 3.2 13 种镜头运动
Zoom In/Out / Push In/Pull Out / Pan Left/Right / Truck Left/Right / Tilt Up/Down /
Pedestal Up/Down / Arc Shot / Tracking Shot / Static Shot / Shake Slightly/Strongly /
POV / Roll Clockwise/Counterclockwise

### 3.3 11 维导演控制能力
空镜 / 留白 / 氛围渲染 / 悬疑 / 多线 / 反转 / 高潮 / 余韵 / 推进节奏 / 感情控制 / 角色塑造

---

## 4. Hell Grind 5 大创作铁律 (反复打磨出来)

1. **资产先行** — 任何资产未锁定并通过压力测试不生成 (省的钱比其他所有规则加起来还多)
2. **每次描述全部** — descriptor 逐字进每个 prompt, 绝不缩写
3. **一次只改一行** — 整段重写会丢掉已经 work 的部分, 每次迭代改一行, 全部进日志
4. **给模型更少的自由** — 角落而不是房间, 锚点而不是开放空间, 地图而不是猜
5. **镜头搞不定就简化** — 别改词, 拆成两个, 删一个动作, 换个角度

### 4.1 7 条活人感规则
1. **分阶段眨眼**: one lazy blink → DOUBLE-BLINK → HARD reset-blink
2. **视线先于头**: 眼睛先到门口, 头晚半拍
3. **微生命**: 每 1-2 秒一个微事件 (呼吸/鼻翼/眉头)
4. **静止保持张力**: 用 "用力维持静止", 不用 "nobody moves"
5. **反应先于台词**: 听话的人半句就懂了, 脸已先答
6. **重要事件后消化**: 重要事件后给角色半秒消化再开口
7. **让手忙起来**: 一边修东西/数东西/倒东西一边聊, 最强重音是突然停下手里的活

---

## 5. Seedance 2.5 30 秒场景单元 6 段式 (卡兹克原文)

| 时间 | 阶段 | 任务 |
|------|------|------|
| 0:00-0:03 | **建置** (建置空间) | 1 秒全景让 AI 认路: 谁在哪, 什么在哪, 光从哪来 |
| 0:03-0:08 | **引入** (角色进入) | 主角进入空间, 模型开始有动作发展 |
| 0:08-0:15 | **互动** (主互动) | 核心情节开始, 主体动作/对话 |
| 0:15-0:22 | **冲突** (冲突建立) | 矛盾开始, 戏剧张力 |
| 0:22-0:27 | **高潮** (情绪高点) | 镜头表达最连贯, 表演密度最高 |
| 0:27-0:30 | **钩子** (留白悬念) | 末帧悬念, 引导下一镜 |

### 5.1 30 秒场景的关键技术点
- 美术优先 (DiDi_OK): 先把"光/色/质/空"写清楚, 后面再写动作
- 声音进步: 环境音分层处理, 音乐留后期
- 空间感 4 句: 描述谁在哪个地标多远处
- 白模参考: 用 3D 白模锁定空间关系
- 3 大能力: 判断/资产/故事 (美术/资产/故事)

---

## 6. Seedance 2.5 核心能力 (2026-07 上线)

| 能力 | 详情 |
|------|------|
| 单条时长 | 30 秒 (同类最多 15-20 秒) |
| 多参考输入 | 50 个全模态素材 (图片+视频+音频), 同类最多 |
| 局部编辑 | 在整体画面不变下框选修改 (手部/商品/模特) |
| 多语言 | 10+ 种语言 (西/印尼/阿拉伯/日/韩) 口型同步 |
| 视频延长 | 最高 3 分钟 (多段拼接) |
| 3D 白模 | 兼容 Maya/Blender 3D 工作流 |
| 多镜头连续 | 12 参考 → 50 参考 |
| Seedance Character | 4K/21:9 角色表 (前/后/侧/动作/表情) |
| 一致性 | consistent_video() 锚定角色表 |
| 5 镜/秒 | 价格 $0.60 (720p), $0.30 (480p) |
| Omni-Reference | 20 图像 / 6 视频 / 6 音频 (MuAPI) |
| 时间戳编辑 | 帧级精确编辑 |
| 绿幕编辑 | 视频内对象绿幕化 |
| 相机视角编辑 | 改变摄影机轨迹 |
| 黏土渲染参考 | 锁定渲染风格 |
| 运动参考 | 锁定运动轨迹 |

---

## 7. 14 部真实 AI 短剧实战 (从 brief 和检索)

### 7.1 中国短剧
- 《摸金之天机入梦》- 戛纳 Fantastic Pavilion
- 《饿塔》- 戛纳 Fantastic Pavilion
- 兵马俑奇妙之旅 / 秦海战姬 / 戎装承志 / 烈焰天街
- 一路狂奔 / 星际郎中 / 兴安岭诡事 / 天才机甲师
- 万兽独尊 / 敦煌女团上线 / 奥运飞天之梦
- 兵马俑的那些事 / 叶良辰你的妹妹终于离婚了

### 7.2 4 类创作者实战
- **齐磊_超级个体**: 一个人跑通 30+ 部
- **王天海_团队作战**: 标准化 8 人小组
- **河南大学 4 女生_学生组**: 学生用爱发电
- **LibTV_平台派**: 平台级流水线

### 7.3 真实角色 (Hell Grind 4 主角)
- **ROCO**: 16-18 岁少年, 右臂水晶化
- **JAXX**: 街头孩子组长, 反应快
- **LULU**: 12-14 岁, 红色卷发
- **REIN**: 技术型, 戴眼镜

---

## 8. 14 部真实短剧 + 30s 6 段 + 3D 白模 → 节点设计

### 8.1 新增节点 phase14_30s_six_act (30 秒场景单元 6 段)
- 输入: 概念/类型/演员/情绪/导演风格
- 输出: 6 段完整 H3 prompt (建置/引入/互动/冲突/高潮/钩子)
- 5 要素架构 + 11 维导演控制 + 反 AI 词表

### 8.2 新增节点 phase14_cinematic_studio (电影效果 + 多模型路由)
- 23 个电影特效 (毒液附体/美杜莎石化/慢动作/...)
- 12+ 模型路由 (Seedance/Kling/Wan/Veo/Sora/...)
- 模型弱点库 (每个模型怕什么)
- 一致性工作流 (character sheet + consistent_video)

### 8.3 更新 phase14_master_orchestrator
- 加入 30s 6 段分镜
- 加入 11 阶段制作管线
- 加入 Style Prefix 12 层底座
- 加入 5 大铁律 (1 行)
- 加入 6 份文件项目级记忆

---

## 9. 重要人物 / 引用

| 人物 | 角色 | 引用 |
|------|------|------|
| 贾樟柯 | 中国第六代导演 | "电影不只是影像, 它是思想与技术的结合" |
| 吕克·贝松 | SEEN 工作室 | 行业领袖, 关注 AI 电影 |
| OutpostVFX | 国际顶级特效公司 | 行业领袖 |
| 卡兹克 (微信公众号) | Seedance 2.5 深度分析 | "30 秒接近完整场景单元, 留白是说不满的一寸" |
| 冷逸 (微信公众号) | H3 提示词教程 | 11 规则 + 4 任务类型 + 13 镜头运动 |
| 齐磊 | 超级个体创作者 | "1 个人能跑通" |
| 王天海 | 团队作战 | "8 人标准化小组" |
| 罗川 | LibTV 平台派 | "流水线化制作" |
| 河南大学 4 女生 | 学生组 | "用爱发电" |
| Renmu2017 | 第三方 GitHub Hell-Grind-AIGC-Skill | "模型无关工作流" |

---

## 10. 与我们项目 25 节点的深度整合

### 10.1 现有 25 节点 → 新 Phase 14 增强
| 节点 | 现状 | Phase 14 增强 |
|------|------|--------------|
| ConceptPitchPro | 7128 字符输出 | + 30s 6 段分镜 + 11 阶段管线 |
| PerformanceDirectionPro | 5 支柱 | + 7 活人感规则 + 反应链 |
| SpatialConsistencyPro | 5 规则 | + 3D 白模 + 11 维控制 |
| SoundDesignPro | 5 维声音 | + SFX-only 强制 + 声音尾音 |
| EditingPro | 切点策略 | + 10-15 次规则 + 局部重绘 |
| DirectorIntentPro | 5 维意图 | + Hell Grind 5 支柱 + 11 维控制 |
| ArtDirectionPro | 4 维美术 | + 12 层 Style Prefix |
| QualityAssurancePro | 反 AI 自检 | + 8 类问题单 + 修复优先级 |
| Phase14AssetRegistry | 资产注册 | + 6 份文件项目级记忆 |
| Phase14SpatialLayout | GEO 地图 | + 3D 白模 + 11 维控制 |
| Phase14ActingSkill | 5 支柱 | + 7 活人感规则 |
| Phase14SoundSkill | 声音 | + SFX-only 强制 + 尾音连续性 |
| IterationPostPro | 5 铁律 + 8 问题 | + 11 阶段管线 + 23 电影特效 |

### 10.2 新增 2 个节点
- **Phase14_30sSixAct**: 30 秒场景单元 6 段式分镜 (建置/引入/互动/冲突/高潮/钩子)
- **Phase14_CinematicStudio**: 电影效果 + 多模型路由 + 角色表 + 一致性工作流

### 10.3 Phase 14 总节点数: 27 (25 + 2)
- 25 已有
- 2 新增 (30s + Cinematic Studio)
- 集成在 __init__.py
- 524+ 测试基线

---

## 11. 立即行动清单

1. ✅ 写 phase14_higgsfield_synthesis.md (本文件) - **完成**
2. ⏳ 写 phase14_30s_six_act.py 节点 (30 秒 6 段分镜)
3. ⏳ 写 phase14_cinematic_studio.py 节点 (电影效果 + 多模型)
4. ⏳ 更新 phase14_master_orchestrator (集成 11 阶段管线 + Style Prefix 12 层)
5. ⏳ 跑全套测试 524+ → 600+
6. ⏳ 更新 AUDIT_REPORT.md Phase 14 升级
7. ⏳ 启动双 AI 互审 (verifier agent)
