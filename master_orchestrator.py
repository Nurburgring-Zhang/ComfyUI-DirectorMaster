# -*- coding: utf-8 -*-
"""
Phase 14 - 终极主整合器 (Ultimate Master Orchestrator)
======================================================
**L5 顶级导演级 + AIGC 影视全流程解析附件** 完整集成

把 8 大世界顶级导演能力 + 42 环节 8 阶段 + L1-L7 七层架构
+ 6 层生产系统 + 15 块刚性骨架 + 6 份文件 + 3 留白 + 3 运镜
全部深度整合到 ComfyUI-PromptLibraryNode 节点里。

## 8 大顶级导演能力 (8 Core Abilities)
- AB1 叙事架构力 (Narrative Architecture) - PTA/Nolan/奉俊昊
- AB2 情感调度力 (Emotion Dispatch) - 黑泽明/库斯杜力卡
- AB3 节奏控制力 (Rhythm Control) - Nolan/Villeneuve
- AB4 视觉语言力 (Visual Language) - Roger Deakins/Lubezki
- AB5 表演指导力 (Performance Direction) - PTA/库斯杜力卡
- AB6 场面调度力 (Scene Choreography) - Nolan/Villeneuve
- AB7 审美判断力 (Aesthetic Judgment) - PTA/Gerwig
- AB8 团队领导力 (Team Coordination) - 多智能体协调

## L1-L7 七层 Prompt 架构 (7-Layer Prompt Architecture)
- L1 意图与验收 - 导演的"为什么"
- L2 资产与引用 - 锁定"同一个谁"
- L3 空间与数量 - 不可崩塌的片场
- L4 表演与物理 - 让数字演员活起来
- L5 摄影与剪辑 - 控制观众的眼睛
- L6 声音与对白 - 1/2 影像
- L7 风格约束 - 不变项

## 5 要素架构 (5 Elements)
1. 数据 - 1161 部 + 63 导演 + 191 反 AI + 12 套理论 + 14 真实短剧 + 8 顶级导演
2. 上下文缩略 - 类型/导演/主题/场景 1 句话
3. Skill/Harness - 15 块 + 8 能力 + L1-L7 + 5 维意图 + 4 维美术 + 5 空间 + 5 沉默
4. 经验矩阵 - Hell Grind 6 层 + 真实短剧实战 + 5 铁律
5. AI 深度处理 - 反 AI 词表 + 10 铁律 + 4 轮迭代 + 11 维导演控制 + 10-15 次规则
"""

import os
import sys

try:
    from asset_registry_data import (
        ASSET_REGISTRY, SCENE_MAP, ACTING_STATE,
        SHOTLIST_TEMPLATE, VERSION_LOG_TEMPLATE, POST_ISSUE_LIST_TEMPLATE,
        get_six_documents_summary,
    )
    from style_prefix_data import (
        FIFTEEN_BLOCKS, STYLE_PREFIX,
        build_skeleton_prompt, render_style_prefix, get_skeleton_summary,
    )
    _HAS_INTERNAL_DOCS = True
except Exception:
    _HAS_INTERNAL_DOCS = False


# ============================================================
# 8 大顶级导演能力 (8 Core Abilities) — L5 顶级导演级
# ============================================================
EIGHT_ABILITIES = {
    "AB1_叙事架构力": {
        "name": "Narrative Architecture",
        "core_question": "故事如何在结构上承载情感？",
        "directors": ["Paul Thomas Anderson", "Christopher Nolan", "奉俊昊", "Martin Scorsese"],
        "key_techniques": [
            "Save the Cat 15 节拍", "Hero's Journey 17/12 阶段", "McKee 7 大结构",
            "三幕剧结构", "情节点设计 (激励事件/Plot Point 1/中点/Plot Point 2/高潮/结局)",
            "副线设计", "角色弧光追踪", "主题的视觉化呈现",
        ],
        "ai_implementation": "叙事引擎：剧本分析、结构识别、弧光追踪、情节点标注",
    },
    "AB2_情感调度力": {
        "name": "Emotion Dispatch",
        "core_question": "观众应在什么时刻感受什么情绪？",
        "directors": ["黑泽明", "库斯杜力卡", "奉俊昊", "斯皮尔伯格"],
        "key_techniques": [
            "情感图谱: 悲伤→冷色调慢节奏留白, 恐惧→暗调不稳定运动, 愤怒→暖色高对比快节奏",
            "情感弧光: 8 大情感峰谷设计",
            "微动作总和等于情感: 不写'悲伤'写'下颌松视线掉呼吸浅慢'",
            "重要事件后消化: 半秒静止再开口",
        ],
        "ai_implementation": "情感引擎：情感目标→视觉参数映射词典 + 7 活人感规则",
    },
    "AB3_节奏控制力": {
        "name": "Rhythm Control",
        "core_question": "观众的注意力曲线如何被管理？",
        "directors": ["Christopher Nolan", "Denis Villeneuve", "奉俊昊", "北野武"],
        "key_techniques": [
            "全片节奏曲线: 起(30%) / 承(30%) / 转(20%) / 合(20%)",
            "30s 场景单元 6 段: 建置/引入/互动/冲突/高潮/钩子",
            "加速-减速对比: 高潮前 3-5 秒静止",
            "静止-爆发对比: 长时间静态后突然剧烈运动",
            "时间压缩/拉伸: 3 秒表现 1 小时 vs 30 秒表现 1 秒钟",
        ],
        "ai_implementation": "节奏引擎：全片节奏曲线 + 场景节奏控制 + 镜头时长管理",
    },
    "AB4_视觉语言力": {
        "name": "Visual Language",
        "core_question": "构图/光影/色彩如何传递潜文本？",
        "directors": ["Roger Deakins", "Emmanuel Lubezki", "杜可风", "Bradford Young"],
        "key_techniques": [
            "焦段×情感: 14mm 广角压迫, 35mm 标准, 85mm 肖像, 135mm+ 孤独",
            "光圈×景深: T1.4 极浅, T2.8 电影浅, T8 全景深",
            "60:30:10 色彩法则: 主色 60% / 辅色 30% / 点缀色 10%",
            "9 维光影: 光源类型/方向/强度/色温/软硬/比例/阴影/特殊/时间",
            "构图法则: 三分法/黄金比例/对称/引导线/框中框/留白/负空间",
        ],
        "ai_implementation": "视觉语言引擎：镜头语言参数化 + 12 层 Style Prefix",
    },
    "AB5_表演指导力": {
        "name": "Performance Direction",
        "core_question": "如何逼出数字演员生涯最佳的表演？",
        "directors": ["Paul Thomas Anderson", "库斯杜力卡", "奉俊昊", "王家卫"],
        "key_techniques": [
            "FACS 12 基础表情单元: AU1+AU2+AU4 真实悲伤, AU9+AU15 厌恶加强",
            "5 表演支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN",
            "7 活人感规则: 分阶段眨眼/视线先于头/微生命/静止保持张力/反应先于台词/重要事件后消化/让手忙起来",
            "20 种情绪动作翻译: sad→下颌松视线掉, angry→下颌咬鼻翼张...",
            "潜文本对白 6 技巧: 说反话/转移话题/言此意彼/沉默/动作/潜台词双重",
        ],
        "ai_implementation": "表演引擎：FACS 12 + 5 支柱 + 7 活人感 + 20 情绪动作",
    },
    "AB6_场面调度力": {
        "name": "Scene Choreography",
        "core_question": "空间如何被安排为叙事的舞台？",
        "directors": ["Christopher Nolan", "Denis Villeneuve", "奉俊昊", "韦斯·安德森"],
        "key_techniques": [
            "GEO SPATIAL LAYOUT 三大铁律: 只写空间不写动作 / 摄影机视角 frame-left / 地标+距离",
            "180° 轴线系统: 视线轴/运动轴/关系轴/摄影机轴/越轴处理",
            "5 大空间逻辑: 空间关系/层次/移动/阻碍/寓意",
            "6 大空间类型: 室内住宅/公共/特殊 + 室外城市/自然/特殊",
            "空间叙事顺序: '走错了房间, 选错了入口, 叙事就会崩塌' (诺兰)",
        ],
        "ai_implementation": "空间引擎：GEO MAP + 180° 系统 + 5 空间逻辑 + 6 空间类型",
    },
    "AB7_审美判断力": {
        "name": "Aesthetic Judgment",
        "core_question": "在多个候选中, 哪个最符合叙事意图？",
        "directors": ["Paul Thomas Anderson", "Yorgos Lanthimos", "Greta Gerwig"],
        "key_techniques": [
            "风格不脱离内容: 风格不能脱离影片内容做讨论",
            "不完美制造真实感: 摆拍感源于缺乏物理空间关系",
            "运镜 3 法则: 破坏首帧完成度 / 引入非线性运动 / 制造响应延迟",
            "留白 3 技巧: 时间留白 (延迟满足) / 空间留白 (情绪集中度) / 叙事留白 (不说尽)",
        ],
        "ai_implementation": "审美引擎：候选评估矩阵 + 留白 3 技巧 + 运镜 3 法则",
    },
    "AB8_团队领导力": {
        "name": "Team Coordination",
        "core_question": "多个智能体如何协同为统一意图服务？",
        "directors": ["Peter Jackson", "Christopher Nolan", "Denis Villeneuve"],
        "key_techniques": [
            "11 阶段管线: Name assets → Gen locations → Gen characters → Test in Seedance → Shoot → Sound → Music → Cut → Color → VFX → QA",
            "6 份文件项目级记忆: ASSET_REGISTRY / SCENE_MAP / ACTING_STATE / SHOTLIST / VERSION_LOG / POST_ISSUE_LIST",
            "5 大铁律: 资产先行 / 每次描述全部 / 一次只改一行 / 给模型更少的自由 / 镜头搞不定就简化",
        ],
        "ai_implementation": "多智能体协调：智能体编排 + 工作流管理 + 项目记忆",
    },
}


# ============================================================
# L1-L7 七层 Prompt 架构 (7-Layer Prompt Architecture)
# ============================================================
L1_INTENT_TEMPLATE = """\
L1 - 意图与验收 (DIRECTOR'S WHY)
本镜让观众 {emotional_target};
通过 {main_visible_event} 完成;
结束时观众应看到 {ending_state}.
"""

L2_ASSET_TEMPLATE = """\
L2 - 资产与引用 (LOCKED IDENTITIES)
ACTIVE REFERENCES
{asset_refs}
{location_ref} for location reference — take only the space and the texture: {texture}. Do not use as a starting frame, do not inherit the composition, the angle or the grade.
"""

L3_SPATIAL_TEMPLATE = """\
L3 - 空间与数量 (UNBREAKABLE STAGE)
GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):
{landmarks}
— 180° AXIS: camera ALWAYS stays on {axis_side} side — it NEVER crosses the line.

三大铁律 (Three Iron Laws of Space):
  1. 只写空间事实, 不写人物动作 (Only space, no action)
  2. 方向用 frame-left/frame-right + 米数, 不用 hero's left (Camera POV only)
  3. 位置挂地标+距离, 不写相对位置 (Landmark + distance, not 'beside')
"""

L4_ACTING_TEMPLATE = """\
L4 - 表演与物理 (MAKE DIGITAL ACTORS ALIVE)
CHARACTER ACTING
{acting_block}

ACTION TIMING
{action_timing}

PHYSICS — {physics}

微动作总和等于情感 (Micro-actions Sum to Emotion):
- 不写"ROCO很累" → 写"下颌绷紧再松开两次"
- 不写"ROCO很愤怒" → 写"鼻血流到嘴唇, 没有擦"
- 不写"ROCO很绝望" → 写"目光先看向破坏的人偶, 再看向人"
- 不写"ROCO在强装镇定" → 写"门一开, 他重新武装表情"

7 活人感规则 (7 Human-Like Rules):
1. 分阶段眨眼: one lazy blink → DOUBLE-BLINK → HARD reset-blink
2. 视线先于头: 眼睛先到门口, 头晚半拍
3. 微生命: 每 1-2 秒一个微事件 (呼吸/鼻翼/眉头)
4. 静止保持张力: 用"用力维持静止", 不用"nobody moves"
5. 反应先于台词: 听话的人半句就懂了, 脸已先答
6. 重要事件后消化: 半秒消化再开口
7. 让手忙起来: 一边修东西一边聊, 最强重音是突然停下手里的活

20 情绪动作翻译 (20 Emotion→Action Translation Table):
- sad → 下颌松/视线掉/呼吸浅慢
- angry → 下颌咬/鼻翼张/拳握
- scared → 瞳孔大/呼吸快/身体僵
- happy → 颊部提/眼周收缩/嘴角拉
- surprise → 眉扬/上睑提/嘴张
- disgust → 上唇提/鼻翼皱/头偏
- contempt → 单侧嘴角提/视线下
- anxiety → 呼吸短/手指动/腿抖
- exhausted → 肩塌/眼皮沉/步拖
- determined → 下颌绷/眼锁/身倾
- love → 瞳孔扩/颊微红/嘴角松
- hatred → 眼睛窄/嘴紧/拳紧
- fear → 瞳孔大/面色白/后退
- hope → 眼睛亮/嘴角微提/身展
- despair → 眼神散/肩全塌/声失
- shame → 头低/眼神躲/脸红
- pride → 胸挺/视平/嘴角单侧
- envy → 视紧/咬唇/身紧
- relief → 肩松/呼长气/眼软
- shock → 全身僵/呼吸停/眼大
"""

L5_CAMERA_TEMPLATE = """\
L5 - 摄影与剪辑 (CONTROL THE VIEWER'S EYE)
OPTICS: {focal}mm, T{aperture}, {dof}.
CAMERA: {camera_motion}. {camera_constraint}.
NEVER: {camera_never}.

运镜 3 法则 (3 Camera Laws to Kill AI-Feel):
1. 破坏首帧完成度: 镜头去找画面, 不是直接给完美构图
2. 引入非线性运动轨迹: 拒绝过度平滑的镜头运动
3. 制造响应延迟: 主体先发生动作, 镜头再跟拍
"""

L6_SOUND_TEMPLATE = """\
L6 - 声音与对白 (HALF OF PICTURE)
VOICE SIGNATURES:
{voice_descriptors}

DIALOGUE (only in AUDIO block):
{dialogue_block}

SILENCED: {silenced}

SFX LAYERS:
{sfx_layers}

CONTINUATION TAIL: 上一镜的尾音/呼吸/手部颤抖进新镜头 (cross-shot sound bridge)

潜文本对白 6 技巧 (6 Subtext Dialogue Techniques):
- 说反话: 角色说"没事", 实际崩溃
- 转移话题: 角色用"你吃了吗"逃避问题
- 言此意彼: 角色说"今天天气不错"实际是"我爱你"
- 沉默潜文本: 角色不回答就是回答
- 动作潜文本: 角色在"摸伤口" = "我没好"
- 潜台词双重: 角色对 A 说话其实对 B 说

NO MUSIC (留后期). SFX only. No subtitles.
"""

L7_STYLE_TEMPLATE = """\
L7 - 风格约束 (IMMUTABLE)
{style_prefix}
"""


# ============================================================
# 3 留白 + 3 运镜法则 (3 Whitespace + 3 Camera Laws)
# ============================================================
THREE_WHITESPACE = {
    "时间留白": "延迟满足 (Delayed Gratification) — 观众的情绪是在等待中形成的。镜头不切, 让观众在画面中等待, 情绪在等待中累积。例: 角色在听到坏消息后 3 秒不反应, 然后慢慢坐下。",
    "空间留白": "决定情绪的集中度 (Decide Emotional Concentration) — 主体在大空间里显得孤独, 在小空间里显得压抑。例: 一个人站在巨大空旷的房间里, 视觉上的留白传递心理上的孤独。",
    "叙事留白": "不把一切说尽 (Don't Say Everything) — 留给观众想象的空间。例: 镜头停在角色离开的画面, 不交代他去了哪里; 或者镜头只表现冲突的开头, 不表现结果。",
}

THREE_CAMERA_LAWS = {
    "破坏首帧完成度": "让镜头去找画面, 而非直接给出完美构图。镜头从模糊/偏移开始, 然后'找到'主体, 制造真实感。AI 视频最常见的'摆拍感'就是因为首帧太完美。",
    "引入非线性运动轨迹": "拒绝过度平滑的镜头运动。真实摄影机会有微抖、有犹豫、有加速减速。运镜曲线不是完美的正弦波, 而是有'犹豫点'的非线性轨迹。",
    "制造响应延迟": "主体先发生动作, 镜头再跟拍。例: 角色先转头, 镜头 0.3-0.5 秒后才跟上, 这种延迟让画面有了'摄影师在反应'的真实感, 而不是预设的丝滑跟拍。",
}


# ============================================================
# 6 层注入函数 (保留并升级)
# ============================================================
def inject_layer_1_asset(asset_name: str = "@roco", state: str = "") -> str:
    """Layer 1: ASSET - 资产注册表注入 (Higgsfield 风格)"""
    if not _HAS_INTERNAL_DOCS:
        return f"[ASSET: {asset_name}{':'+state if state else ''} (Phase 14 docs unavailable)]"
    char = ASSET_REGISTRY["characters"].get(asset_name, ASSET_REGISTRY.get("antagonists", {}).get(asset_name, {}))
    if not char:
        return f"[ASSET: {asset_name} not registered]"
    state_descriptor = ""
    if state and "states" in char and state in char["states"]:
        state_descriptor = char["states"][state]
    descriptor = char.get("descriptor", "")
    voice = char.get("voice", {})
    behavior = char.get("behavior", {})
    out = f"""════════════════════════════════════════
【Layer 1: ASSET (Higgsfield 资产合同)】
════════════════════════════════════════

ASSET: {asset_name} {f'(状态: {state})' if state else ''}
DESCRIPTOR: {descriptor}
{f'STATE: {state_descriptor}' if state_descriptor else ''}

VOICE SIGNATURE:
- Range: {voice.get('range', 'N/A')}
- Timbre: {voice.get('timbre', 'N/A')}
- Speed: {voice.get('speed', 'N/A')}
- Accent: {voice.get('accent', 'N/A')}
- Habit: {voice.get('habit', 'N/A')}
- Pressure: {voice.get('pressure_change', 'N/A')}

BEHAVIOR SIGNATURE:
- Walk: {behavior.get('walk_rhythm', 'N/A')}
- Hand: {behavior.get('hand_habit', 'N/A')}
- Eye: {behavior.get('eye_movement', 'N/A')}
- Stress: {behavior.get('stress_response', 'N/A')}
- Pre-break: {behavior.get('pre_break', 'N/A')}

RULE (Higgsfield 5 铁律 #2): descriptor 逐字进每个 prompt, 绝不缩写.
"""
    return out


def inject_layer_2_spatial(location_name: str = "@loc_training_room") -> str:
    """Layer 2: SPATIAL - GEO SPATIAL LAYOUT 注入"""
    if not _HAS_INTERNAL_DOCS:
        return f"[SPATIAL: {location_name} (Phase 14 docs unavailable)]"
    scene = SCENE_MAP.get(location_name, {})
    if not scene:
        return f"[SPATIAL: {location_name} not registered]"
    geo_lines = scene.get("GEO SPATIAL LAYOUT (locked across every shot — pure spatial map)", [])
    init_shot = scene.get("initialization_shot", "")
    out = f"""════════════════════════════════════════
【Layer 2: SPATIAL (Higgsfield 场景地图 + 诺兰空间叙事)】
════════════════════════════════════════

LOCATION: {location_name}

GEO SPATIAL LAYOUT (locked across every shot):
{chr(10).join(geo_lines)}

INITIALIZATION SHOT (0-1s, 让 AI 拍照定格):
{init_shot}

诺兰: "在诺兰的电影世界里, 空间是有叙事顺序的——如果走错了房间、选错了入口, 叙事就会崩塌."

RULE: 方向用 frame-left/frame-right + 米数, 不用 hero's left.
RULE: 摄影机绝不过 180° axis, 所有剪辑才在一条轴上.

3 大铁律:
1. 只写空间事实, 不写人物动作
2. 方向用 frame-left/frame-right (摄影机视角)
3. 位置挂地标+距离, 不写相对位置
"""
    return out


def inject_layer_3_acting(scenario: str = "ROCO_training_alone") -> str:
    """Layer 3: ACTING - 5 支柱 + 身体行为 + 7 活人感规则"""
    if not _HAS_INTERNAL_DOCS:
        return f"[ACTING: {scenario} (Phase 14 docs unavailable)]"
    example = ACTING_STATE.get("examples", {}).get(scenario, {})
    if not example:
        return f"[ACTING: {scenario} not in examples, use build_5_pillars() directly]"
    pillars = ACTING_STATE.get("5_PILLARS", {})
    out = f"""════════════════════════════════════════
【Layer 3: ACTING (Higgsfield 表演系统 + PTA 表演指导)】
════════════════════════════════════════

SCENARIO: {scenario}
{('Scene: ' + example['scene']) if 'scene' in example else ''}

5 PILLARS (5 表演支柱):
- {pillars.get('WHAT', 'WHAT')}: {example.get('WHAT', 'N/A')}
- {pillars.get('OBSTACLE', 'OBSTACLE')}: {example.get('OBSTACLE', 'N/A')}
- {pillars.get('COST', 'COST')}: {example.get('COST', 'N/A')}
- {pillars.get('STRATEGY', 'STRATEGY')}: {example.get('STRATEGY', 'N/A')}
- {pillars.get('TURN', 'TURN')}: {example.get('TURN', 'N/A')}

PTA 法则: "能从所用的每一位演员身上逼出生涯最佳的表演"
库斯杜力卡: "让演员少说话更能传达情感效果"

7 活人感规则 (7 Human-Like Rules):
1. 分阶段眨眼: one lazy blink → DOUBLE-BLINK → HARD reset-blink
2. 视线先于头: 眼睛先到门口, 头晚半拍
3. 微生命: 每 1-2 秒一个微事件
4. 静止保持张力: 用"用力维持静止", 不用"nobody moves"
5. 反应先于台词: 听话的人半句就懂了, 脸已先答
6. 重要事件后消化: 半秒消化再开口
7. 让手忙起来: 一边修东西一边聊, 最强重音是突然停下手里的活

RULE: 永远不写情绪, 写可观察行为.
- 写"下颌绷紧", 不写"愤怒"
- 写"视线先到门口, 头晚半拍", 不写"惊讶"
- 写"鼻血流到上唇但不擦", 不写"受伤"
- 微动作的总和 = 情感

INNER 内心独白: 每一段动作配一行未说出口的内心.
"""
    return out


def inject_layer_4_sound(voices: list = None, dialogue: list = None) -> str:
    """Layer 4: SOUND - 声音 + 台词 + 沉默 + 潜文本"""
    voices = voices or ["@roco"]
    dialogue = dialogue or []
    if not _HAS_INTERNAL_DOCS:
        return f"[SOUND: voices={voices} (Phase 14 docs unavailable)]"
    voice_blocks = []
    for v in voices:
        char = ASSET_REGISTRY.get("characters", {}).get(v, ASSET_REGISTRY.get("antagonists", {}).get(v, {}))
        if char and "voice" in char:
            voice = char["voice"]
            voice_blocks.append(f"  {v}: {voice.get('timbre', '')}; {voice.get('speed', '')}; {voice.get('accent', '')}; {voice.get('habit', '')}")
    voice_text = "\n".join(voice_blocks) if voice_blocks else "  (no voice registered)"

    dialogue_text = ""
    if dialogue:
        for d in dialogue:
            sub = d.get('subtext', '')
            dialogue_text += f"\n  ({d.get('speaker', '?')}) {d.get('line', '')}  # 潜文本: {sub}  # 情感: {d.get('emotion', '')}"

    out = f"""════════════════════════════════════════
【Layer 4: SOUND (Higgsfield 声音资产 + 声音是 1/2 影像)】
════════════════════════════════════════

VOICE SIGNATURES (逐字粘贴进每个 prompt):
{voice_text}

DIALOGUE (只在 AUDIO 块, 动作区不放):
{dialogue_text if dialogue_text else "  (无台词 — 保持沉默)"}

潜文本对白 6 技巧 (6 Subtext Dialogue Techniques):
- 说反话: 角色说"没事", 实际崩溃
- 转移话题: 角色用"你吃了吗"逃避问题
- 言此意彼: 角色说"今天天气不错"实际是"我爱你"
- 沉默潜文本: 角色不回答就是回答
- 动作潜文本: 角色在"摸伤口" = "我没好"
- 潜台词双重: 角色对 A 说话其实对 B 说

RULES (Higgsfield 4 铁律):
- 台词固定结构: 声音+情绪 → 引号里台词 → 身体动作 → 面部反应
- 没台词的人必须保持安静
- 跨片段: 上一句尾音/呼吸/手部颤抖进新镜头
- SFX only. No music. No subtitles.
- "声音是电影的一半" — 库斯杜力卡
"""
    return out


def inject_layer_5_iteration(version: str = "v1", diff: str = "", why: str = "", iter_count: int = 1) -> str:
    """Layer 5: ITERATION - 一次只改一个变量 + 10-15 次规则"""
    ten_fifteen = "⚠️ 触发" if iter_count >= 10 else "未触发"
    simplify = "考虑拆成两镜/删动作/换机位" if iter_count >= 10 else "继续改 prompt"
    out = f"""════════════════════════════════════════
【Layer 5: ITERATION (Higgsfield 迭代铁律)】
════════════════════════════════════════

VERSION: {version}
DIFF (唯一改的): {diff if diff else 'N/A (初版)'}
WHY: {why if why else 'N/A'}

RULE 1: 一次只改一个变量
- 整段重写会丢掉已经 work 的部分
- 每次迭代改一行, 全部进日志

10-15 次规则: {ten_fifteen} (当前 {iter_count} 次)
- 简化方案: {simplify}
- "镜头搞不定, 就简化镜头, 别改词"
- 拆成两个, 删一个动作, 换个角度

Higgsfield 5 铁律:
1. 资产先行 (未锁定不生成)
2. 每次描述全部 (descriptor 逐字进每个 prompt)
3. 一次只改一行
4. 给模型更少的自由 (角落而不是房间)
5. 镜头搞不定, 就简化镜头
"""
    return out


def inject_layer_6_post(issues: list = None) -> str:
    """Layer 6: POST - 后期清理 + 调色 + 声音"""
    issues = issues or []
    if not _HAS_INTERNAL_DOCS:
        return "[POST: (Phase 14 docs unavailable)]"
    issue_text = "\n".join(f"  [{i.get('category', '?')}] {i.get('description', '')} (severity: {i.get('severity', 'medium')})" for i in issues) if issues else "  (无问题)"

    out = f"""════════════════════════════════════════
【Layer 6: POST (Higgsfield 后期系统)】
════════════════════════════════════════

ISSUES (8 类):
{issue_text}

CLEANUP PASS (定剪后独立):
- 脸漂移 (face_drift)
- 多指 (hand_extra_finger)
- 沸腾纹理 (boil_texture)
- 假字 (fake_text)
- 调色不统一 (color_mismatch)
- 声音不连贯 (audio_continuity)
- 待补镜头 (missing_coverage)
- 接缝跳 (seam_jump)

RULES (Higgsfield):
- 剪辑跟生成并行, 缺什么当场下单
- 优先修脸和手
- 调色先统一: 每代生成自带内置调色, 让相邻镜头到一个 look
- 不重录声音: Seedance 对口型台词直接从生成里清理
"""
    return out


# ============================================================
# 8 大能力注入函数 (NEW - L5 顶级导演级)
# ============================================================
def inject_8_abilities(director: str = "Christopher Nolan") -> str:
    """8 大顶级导演能力注入"""
    out = f"""════════════════════════════════════════
【8 大顶级导演能力 (L5 World-Class Director Abilities)】
════════════════════════════════════════

本次导演视角: {director}

AB1 叙事架构力 - {EIGHT_ABILITIES['AB1_叙事架构力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB1_叙事架构力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB1_叙事架构力']['key_techniques'][:4])}

AB2 情感调度力 - {EIGHT_ABILITIES['AB2_情感调度力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB2_情感调度力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB2_情感调度力']['key_techniques'][:4])}

AB3 节奏控制力 - {EIGHT_ABILITIES['AB3_节奏控制力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB3_节奏控制力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB3_节奏控制力']['key_techniques'][:4])}

AB4 视觉语言力 - {EIGHT_ABILITIES['AB4_视觉语言力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB4_视觉语言力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB4_视觉语言力']['key_techniques'][:4])}

AB5 表演指导力 - {EIGHT_ABILITIES['AB5_表演指导力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB5_表演指导力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB5_表演指导力']['key_techniques'][:4])}

AB6 场面调度力 - {EIGHT_ABILITIES['AB6_场面调度力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB6_场面调度力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB6_场面调度力']['key_techniques'][:4])}

AB7 审美判断力 - {EIGHT_ABILITIES['AB7_审美判断力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB7_审美判断力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB7_审美判断力']['key_techniques'][:4])}

AB8 团队领导力 - {EIGHT_ABILITIES['AB8_团队领导力']['core_question']}
  代表: {' / '.join(EIGHT_ABILITIES['AB8_团队领导力']['directors'])}
  技术: {' / '.join(EIGHT_ABILITIES['AB8_团队领导力']['key_techniques'][:3])}
"""
    return out


def inject_3_whitespace() -> str:
    """3 留白技巧注入"""
    out = f"""════════════════════════════════════════
【3 留白技巧 (3 Whitespace Techniques — Denis Villeneuve 静默)】
════════════════════════════════════════

时间留白 (Delayed Gratification):
{THREE_WHITESPACE['时间留白']}

空间留白 (Emotional Concentration):
{THREE_WHITESPACE['空间留白']}

叙事留白 (Don't Say Everything):
{THREE_WHITESPACE['叙事留白']}

Denis Villeneuve: "把镜头保持到远超寻常导演会切走的时刻之后".
Christopher Nolan: "三小时道德辩论像惊悚片一样疾驰".
"""
    return out


def inject_3_camera_laws() -> str:
    """3 运镜法则注入"""
    out = f"""════════════════════════════════════════
【3 运镜法则 (3 Camera Laws to Kill AI-Feel)】
════════════════════════════════════════

法则 1: {list(THREE_CAMERA_LAWS.keys())[0]}
{THREE_CAMERA_LAWS['破坏首帧完成度']}

法则 2: {list(THREE_CAMERA_LAWS.keys())[1]}
{THREE_CAMERA_LAWS['引入非线性运动轨迹']}

法则 3: {list(THREE_CAMERA_LAWS.keys())[2]}
{THREE_CAMERA_LAWS['制造响应延迟']}

核心: "要消除 AI 视频的'AI 味', 关键不在于添加更多特效, 而在于去除随机性.
     你需要少以提示词使用者的视角思考, 多像一名导演那样考量.
     以电影创作意图为起点, 而非电影关键词." (AIGC 影视全流程解析)
"""
    return out


def inject_42_stages() -> str:
    """42 环节 8 阶段总览"""
    out = """════════════════════════════════════════
【42 环节 8 阶段 (AIGC 影视全流程)】
════════════════════════════════════════

阶段 1: 创意孵化 (5 环节 ★★★★☆) - 构思/市场/大纲/角色/视觉风格
阶段 2: 剧本开发 (7 环节 ★★★★★) - 结构/节拍/对白/弧光/主题/定稿/导演读解
阶段 3: 视觉开发 (5 环节 ★★★★☆) - 角色视觉/场景视觉/色彩/光影/风格手册
阶段 4: 资产生产 (5 环节 ★★★☆☆) - 角色/场景/道具/声音/压力测试
阶段 5: 预可视化 (4 环节 ★★★★☆) - 动态分镜/空间地图/镜头语言/审核
阶段 6: 拍摄执行 (8 环节 ★★★★★) - Prompt/批量/质检/选片/迭代/表演/衔接/完成度
阶段 7: 后期制作 (6 环节 ★★★★☆) - 剪辑/清理/调色/声音/VFX/审片
阶段 8: 交付分发 (2 环节 ★★☆☆☆) - 格式/归档

每环节 5 要素: 数据/上下文/Skill/经验矩阵/AI 深度处理
"""
    return out


def inject_all_6_layers(
    asset: str = "@roco",
    state: str = "",
    location: str = "@loc_training_room",
    scenario: str = "ROCO_training_alone",
    voices: list = None,
    dialogue: list = None,
    version: str = "v1",
    diff: str = "",
    why: str = "",
    iter_count: int = 1,
    post_issues: list = None,
) -> str:
    """6 层全部注入 (Higgsfield 6 层生产系统)"""
    return "\n".join([
        inject_layer_1_asset(asset, state),
        inject_layer_2_spatial(location),
        inject_layer_3_acting(scenario),
        inject_layer_4_sound(voices, dialogue),
        inject_layer_5_iteration(version, diff, why, iter_count),
        inject_layer_6_post(post_issues),
    ])


def inject_all_l5():
    """L5 顶级导演级 + 8 大能力 + L1-L7 + 3 留白 + 3 运镜 + 42 环节 全部注入"""
    return "\n".join([
        inject_8_abilities("Christopher Nolan"),
        inject_3_whitespace(),
        inject_3_camera_laws(),
        inject_42_stages(),
    ])


# ============================================================
# 完整 L1-L7 七层 Prompt 拼装
# ============================================================
def build_l1_l7_prompt(
    # L1 意图
    emotional_target: str = "ROCO 的精疲力竭和隐忍",
    main_visible_event: str = "他的呼吸、下巴绷紧、鼻血流淌和目光移动",
    ending_state: str = "他在门打开的瞬间重新武装表情",
    # L2 资产
    asset_refs: list = None,
    location_ref: str = "@loc_training_room",
    location_texture: str = "raw concrete, black rock walls, the round mat, the hard light above it",
    # L3 空间
    spatial_landmarks: list = None,
    axis_side: str = "DOOR",
    # L4 表演
    acting_block: str = "",
    action_timing: list = None,
    physics: str = "Mass has real weight. Correct contact shadows. No floating props.",
    # L5 摄影
    focal: str = "35",
    aperture: str = "2.8",
    dof: str = "shallow depth of field",
    camera_motion: str = "Push In with small amplitude at slow speed",
    camera_constraint: str = "Static shot holds as she lifts her gaze",
    camera_never: str = "crosses 180° axis, tilts more than 15°, pans to mannequin wall",
    # L6 声音
    voice_descriptors: list = None,
    dialogue_in_quotes: list = None,
    silenced: list = None,
    sfx_layers: list = None,
    # L7 风格
    style_prefix: str = "",
    # 总览
    n_characters: int = 3,
    character_list: str = "ROCO, JAX, REIN",
    location_descriptor: str = "Underground base, training hall",
    time_of_day: str = "day",
    one_line_summary: str = "",
    duration: float = 12.0,
    first_frame: str = "",
    constraints: list = None,
) -> str:
    """按 L1-L7 七层架构拼装完整 prompt"""

    asset_refs = asset_refs or [
        "@roco for character reference — bare-chested, the crystal sheathing his right arm from wrist to shoulder, blood dried under his nose",
        "@jax for character reference — carrying two food trays",
        "@rein for character reference — tablet in her left hand, screen alive",
    ]
    spatial_landmarks = spatial_landmarks or [
        "— PLATFORM = raised circular training mat, 6m diameter, at room center",
        "— DOOR: frame-left, 8m from mat center",
        "— SMASHED MANNEQUINS: 5 of them, scattered at frame-right",
    ]
    action_timing = action_timing or [
        ("0.0", "2.0", "ROCO holds the center of the mat, feet planted wide, chest pumping in short shallow pulls; the crystal arm hangs heavy at his side and drags his right shoulder a finger lower than the left"),
        ("2.0", "4.5", "the jaw sets and releases twice; a thread of blood runs from his nose to his upper lip and he lets it run; one lazy blink, a quick DOUBLE-BLINK, one HARD reset-blink"),
        ("4.5", "6.0", "the gaze drops to the smashed mannequins at CENTER-RIGHT, holds one beat, then lifts to the door as it opens — the eyes reach the door before the head turns"),
    ]
    voice_descriptors = voice_descriptors or [
        "@roco: tenor, slightly hoarse; mid-speed; London East End; sentence ends swallowed",
        "@jax: alto, husky, smoky; fast; East End; 'yeah' 'nah' 'oi' lead-ins",
        "@rein: soprano, clean, measured; standard English; sentence ends with 'right?'",
    ]
    dialogue_in_quotes = dialogue_in_quotes or []
    silenced = silenced or []
    sfx_layers = sfx_layers or [
        "underground base air",
        "two pairs of footsteps",
        "tablet tap",
        "distant thud (from elsewhere)",
    ]
    acting_block = acting_block or "ROCO — burnt out and still going. Wants: one more clean hit. Hiding: the arm is winning. Body rhythm: heavy, planted. Habits: jaw set-and-release, right shoulder pulled low, blood not wiped. Changes: door opens, he re-arms his face."
    constraints = constraints or [
        "Exactly 3 people in the hall, and no one else",
        "Exactly ONE crystal arm, on ROCO's right arm, wrist to shoulder",
        "FIVE smashed mannequins, never re-rendered as intact, never multiplied",
        "Two trays, never more",
        "Camera stays on the door side for all twelve seconds",
    ]

    silenced_text = ", ".join(silenced) if silenced else "无"
    dialogue_text = "\n".join(f'  <d>[Chinese] "{d}"</d>' for d in dialogue_in_quotes) if dialogue_in_quotes else "  (no dialogue in this beat — characters remain silent)"
    sfx_text = "\n".join(f"  - {s}" for s in sfx_layers)
    beat_text = "\n".join(f"  {s}-{e}s — {a}" for s, e, a in action_timing)
    constraint_text = "\n".join(f"  - {c}" for c in constraints)
    asset_text = "\n".join(f"  {a}" for a in asset_refs)
    landmark_text = "\n".join(f"  {l}" for l in spatial_landmarks)
    voice_text = "\n".join(f"  {v}" for v in voice_descriptors)

    if not style_prefix:
        style_prefix = STYLE_PREFIX if _HAS_INTERNAL_DOCS else "Live-action. Film grain texture. No 3D render. No game engine."

    # L1-L7 七层
    l1 = L1_INTENT_TEMPLATE.format(
        emotional_target=emotional_target,
        main_visible_event=main_visible_event,
        ending_state=ending_state,
    )
    l2 = L2_ASSET_TEMPLATE.format(
        asset_refs=asset_text,
        location_ref=location_ref,
        texture=location_texture,
    )
    l3 = L3_SPATIAL_TEMPLATE.format(
        landmarks=landmark_text,
        axis_side=axis_side,
    )
    l4 = L4_ACTING_TEMPLATE.format(
        acting_block=acting_block,
        action_timing=beat_text,
        physics=physics,
    )
    l5 = L5_CAMERA_TEMPLATE.format(
        focal=focal, aperture=aperture, dof=dof,
        camera_motion=camera_motion, camera_constraint=camera_constraint,
        camera_never=camera_never,
    )
    l6 = L6_SOUND_TEMPLATE.format(
        voice_descriptors=voice_text,
        dialogue_block=dialogue_text,
        silenced=silenced_text,
        sfx_layers=sfx_text,
    )
    l7 = L7_STYLE_TEMPLATE.format(style_prefix=style_prefix)

    # 头部场景上下文
    header = f"""SCENE CONTEXT
EXACT {n_characters} CHARACTERS — NO DUPLICATES: {character_list}. {location_descriptor}, {time_of_day}. {one_line_summary}. One continuous {duration}s shot, no cuts.

FIRST FRAME (0.0-1.0s 让 AI 认路):
Wide static shot. {first_frame or 'Everyone at fixed position. Hard top light pools on mat. Camera on door side, 6m back. No motion. 1 second of pure space.'} Camera is on door side, 6m back. No motion. 1 second of pure space.

FORMAT MODE: One continuous {duration}s shot, no cuts, 24fps, 16:9, real-time: no
"""

    quality = """QUALITY
- Cinematic, live-action — no 3D render, no game engine, no game-cutscene aesthetic
- Film-grain detail
- Pore-level realism — vellus hair, asymmetric moles, capillary flush
- Wet living eyes with catch-lights
- Visible breath and chest rise
- 24fps smooth motion. Film-grain detail. No jitter
"""

    out = header + l1 + l2 + l3 + l4 + l5 + l6 + l7 + quality + f"\nPOSITIVE CONSTRAINTS\n{constraint_text}\n\nLive-action. NON-IP. 16:9. {duration}s. SFX only. NO CGI. Cinematic."

    return out


# 向后兼容: 保留原 build_hell_grind_prompt 函数
def build_hell_grind_prompt(
    n_characters: int = 3,
    character_list: str = "ROCO, JAX, REIN",
    location_descriptor: str = "Underground base, training hall",
    time_of_day: str = "day",
    one_line_summary: str = "ROCO has been drilling alone for hours; JAX and REIN come in late with food and find the room wrecked",
    duration: float = 12.0,
    asset_refs: list = None,
    location_ref: str = "@loc_training_room",
    spatial_landmarks: list = None,
    first_frame: str = "",
    camera_motion: str = "Push In with small amplitude at slow speed",
    never_moves: str = "crosses 180° axis, tilts more than 15°, pans to mannequin wall",
    action_beats: list = None,
    physics: str = "Mass has real weight. Correct contact shadows. No floating props.",
    lighting: str = "Hard top light 5000K from above only",
    voice_descriptors: list = None,
    dialogue_in_quotes: list = None,
    silenced: list = None,
    sfx_layers: list = None,
    actor_acting: dict = None,
    constraints: list = None,
) -> str:
    """按 15 块刚性骨架拼装完整 Hell Grind 风格 prompt (向后兼容)"""
    acting_block = "\n".join(f"  {k} — {v}" for k, v in (actor_acting or {}).items()) if actor_acting else ""

    return build_l1_l7_prompt(
        emotional_target="ROCO 的精疲力竭和隐忍",
        main_visible_event="他的呼吸、下巴绷紧、鼻血流淌和目光移动",
        ending_state="他在门打开的瞬间重新武装表情",
        asset_refs=asset_refs,
        location_ref=location_ref,
        location_texture="raw concrete, black rock walls, the round mat, the hard light above it",
        spatial_landmarks=spatial_landmarks,
        axis_side="DOOR",
        acting_block=acting_block,
        action_timing=action_beats,
        physics=physics,
        focal="35",
        aperture="2.8",
        dof="shallow on subject, sharp on background",
        camera_motion=camera_motion,
        camera_constraint=f"Filter: Black Pro-Mist 1/4. Subject framing: subject centered, rule of thirds. Lighting: {lighting}. Shadow: hard top-down, contact shadows on mat.",
        camera_never=never_moves,
        voice_descriptors=voice_descriptors,
        dialogue_in_quotes=dialogue_in_quotes,
        silenced=silenced,
        sfx_layers=sfx_layers,
        style_prefix="",
        n_characters=n_characters,
        character_list=character_list,
        location_descriptor=location_descriptor,
        time_of_day=time_of_day,
        one_line_summary=one_line_summary,
        duration=duration,
        first_frame=first_frame,
        constraints=constraints,
    )


# ============================================================
# 总览函数
# ============================================================
def get_hell_grind_overview() -> str:
    """L5 顶级导演级 + Hell Grind 6 层 + 8 能力 + L1-L7 总览"""
    return f"""
═══════════════════════════════════════════════════════════════
【L5 顶级导演级 + AIGC 影视全流程解析 (Phase 14 终极整合)】
═══════════════════════════════════════════════════════════════

【8 大顶级导演能力 (8 Core Abilities)】
{chr(10).join(f'  {k}: {v["name"]} — {v["core_question"]}' for k, v in EIGHT_ABILITIES.items())}

【L1-L7 七层 Prompt 架构】
- L1 意图与验收 (DIRECTOR'S WHY)
- L2 资产与引用 (LOCKED IDENTITIES)
- L3 空间与数量 (UNBREAKABLE STAGE — 三大铁律)
- L4 表演与物理 (MAKE DIGITAL ACTORS ALIVE — 微动作总和等于情感)
- L5 摄影与剪辑 (CONTROL THE VIEWER'S EYE)
- L6 声音与对白 (HALF OF PICTURE — 潜文本 6 技巧)
- L7 风格约束 (IMMUTABLE — 12 层 Style Prefix)

【42 环节 8 阶段】
- 创意孵化 (5) / 剧本开发 (7) / 视觉开发 (5) / 资产生产 (5)
- 预可视化 (4) / 拍摄执行 (8) / 后期制作 (6) / 交付分发 (2)

【3 留白 + 3 运镜法则】
{chr(10).join(f'  - {k}: {v[:50]}...' for k, v in THREE_WHITESPACE.items())}
{chr(10).join(f'  - {k}: {v[:50]}...' for k, v in THREE_CAMERA_LAWS.items())}

【6 层生产系统 (Higgsfield Hell Grind)】
- Layer 1: ASSET       - 资产不是参考图, 是角色合同
- Layer 2: SPATIAL     - 空间不能靠感觉, 要有不会变的地图
- Layer 3: ACTING      - 不写情绪, 写可观察行为
- Layer 4: SOUND       - 声音也是角色资产
- Layer 5: ITERATION   - 一次只改一个变量
- Layer 6: POST        - 生成是素材, 后期交付的是作品

【15 块刚性骨架】
{chr(10).join(f'  {i+1:2d}. {b["name"]:<25s} — {b["purpose"]}' for i, b in enumerate(FIFTEEN_BLOCKS)) if _HAS_INTERNAL_DOCS else '  (Phase 14 docs unavailable)'}

【6 份文件项目级记忆】
- ASSET_REGISTRY / SCENE_MAP / ACTING_STATE / SHOTLIST / VERSION_LOG / POST_ISSUE_LIST

【11 维导演控制】
空镜/留白/氛围渲染/悬疑/多线/反转/高潮/余韵/推进节奏/感情控制/角色塑造

═══════════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    print(get_hell_grind_overview())

    # 演示 L1-L7 完整 prompt
    print("\n=== 演示 L1-L7 七层 12 秒 ROCO 训练室独处镜头 ===")
    p = build_l1_l7_prompt(
        n_characters=3,
        character_list="ROCO, JAX, REIN",
        duration=12.0,
        first_frame="ROCO at mat center, 5 mannequins frame-right, door frame-left, hard top light pools on mat",
    )
    print(p[:3000])
    print(f"\n... 总长度 {len(p)} 字符")
