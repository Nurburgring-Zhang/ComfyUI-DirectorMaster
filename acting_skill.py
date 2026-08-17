# -*- coding: utf-8 -*-
"""
acting_skill.py — Acting Skill (Higgsfield 方法论本地化)
================================================================================
🎭 表演层专家 — 通用 ACTING_5_PILLARS 架构 (Node 集群产物)

【为什么存在这个文件】
- Higgsfield 在《Hell Grind》开源的 ACTING skill 给出 5 支柱 (WHAT/OBSTACLE/COST/
  STRATEGY/TURN) + "不写情绪写行为" + 视线先于头 + 分阶段眨眼 + 微生命 + 静止保持张力
  这套规则。
- 现有节点 (PerformanceDirectionPro / DialogueMasterPro / CharacterArcPro / DirectorIntentPro)
  都是从"导演意图 / 潜文本"侧出发的, 缺一个把"动作可观察性"直接变成 prompt 文本的层。
- 本文件是 Phase 14 多 agent 集群中"表演层专家"的输出, 不绑定 ComfyUI 节点, 只暴露
  纯函数, 任何上层 (H3 prompt 生成 / 表演 prompt block) 都可以调用。

【5 要素架构 (每个函数内部都内嵌这 5 段)】
1. 数据 (DATA)         — Hell Grind 95 分钟 / 115,446 次生成 / ACTING skill 原文
2. 上下文缩略 (CTX)    — 输入参数 + 5 支柱字段的语义压缩
3. Skill/Harness (SKL)  — 不写情绪写行为 / FACS / 内嵌规则
4. 经验矩阵 (EXP)      — ROCO / JAX / REIN / 反派 的真实写作样本
5. AI 深度处理 (AID)   — 反 AI 词表替换 / 强制具体细节 / 动态生成而非模板

【ACTING_5_PILLARS 架构】
Pillar 1: WHAT      — 角色想从对方那里得到什么 (Goal/Want, 表面目标)
Pillar 2: OBSTACLE  — 什么在挡着他 (障碍, 内在/外在/对方/自己)
Pillar 3: COST      — 失败的代价是什么 (Stakes, 失败会怎样)
Pillar 4: STRATEGY  — 他正在用什么方法争取 (正在做的策略, 可观察行为)
Pillar 5: TURN      — 什么新信息让他改变策略 (转折, 不一定发生, 发生时怎么改)

【10 个核心函数 (顺序即调用栈)】
- build_5_pillars()              5 支柱
- translate_emotion_to_action()  情绪 → 身体动作
- build_action_timing()          动作时间线 (秒级)
- build_blink_sequence()         眨眼序列 (3 段式)
- build_eye_lead()               视线先于头
- build_micro_life()             微生命事件
- build_inner_monologue()        INNER 内心独白
- build_reaction_chain()         反应先于台词
- act_no_motion_but_tension()    静止保持张力
- render_acting_prompt()         完整表演 prompt block (聚合)

【3 个 Hell Grind 示例】
- example_roco_training_room()        ROCO 训练室独处 (12 秒)
- example_jax_rein_corridor()         JAX/REIN 走廊边走边说
- example_villain_entrance()          反派登场 (从不提高音量)
"""

# ==============================================================================
# 0. 模块级常量 — 5 要素 + 5 支柱的"原材料"
# ==============================================================================

# 0.1 反 AI 词表 (Phase 13 沉淀的 191 条子集, 表演层最常见)
ACTING_AI_KILL = [
    ("sad", "下颌绷紧, 鼻翼动, 眨眼变慢"),
    ("angry", "颧骨收紧, 呼吸变重, 手指关节发白"),
    ("shocked", "一次用力闭眼 reset, 吸气停顿, 头后缩半拍"),
    ("happy", "眼轮匝肌真动 (下眼睑微鼓), 嘴角先动, 声音气多实少"),
    ("afraid", "肩线上提, 重心后移, 视线乱扫但不离开威胁源"),
    ("contempt", "单侧嘴角上扬, 视线从对方身上滑走, 呼吸停一拍"),
    ("nervous", "眨眼频率翻倍, 手指无意识摸固定物, 脚踝轻动"),
    ("resigned", "一次缓慢完整呼气, 肩线同步下沉, 眼睛不眨"),
    ("hesitant", "嘴唇刚张开又合上, 视线在两目标间扫一次"),
    ("determined", "下颌咬合后不松, 视线锁死, 重心前移"),
    ("无奈", "一下下颌松, 一次完整呼气, 视线滑到地面再回"),
    ("崩溃", "肩线上提+呼吸乱+手指找不到着力点+视线乱扫"),
    ("狂喜", "吸气+眼轮匝肌真动+嘴角先于声音+前倾"),
    ("悲痛", "横膈膜抖+吸气断+眼眶湿但不落+嘴角向下而非张大"),
    ("坚定", "下颌锁+视锁+重心前+手指先停再握"),
    ("瞳孔地震", "一次快速眨眼 + 头后缩半拍 + 吸气卡顿"),
    ("撕心裂肺", "下颌锁紧 + 声音气多于实 + 重心后倾 + 手在抖"),
    ("缓缓地", "每秒 0.3 倍速, 但只指肌肉, 不指视线"),
    ("绝美", "(直接删除, 用具体特征代替)"),
    ("陷入沉思", "一次慢眨眼 + 视线落固定地标 1.5 秒 + 呼吸变深"),
    ("复杂", "(直接删除, 改为具体动作组合)"),
    ("缓缓转过头", "视线先到目标, 头 0.4-0.6 秒后才跟"),
    ("意味深长", "(直接删除, 改为具体视线 + 微表情组合)"),
]

# 0.2 5 支柱字段 → 行为翻译规则 (经验矩阵)
# 每个支柱都对应一类"可观察行为", 让模型知道怎么把它画出来
# Phase 35.9: 扩展为 5+ 中文 + 5+ 英文可观察行为, 不再是单一 fail_pattern
PILLAR_BEHAVIOR_RULES = {
    "WHAT": {
        "definition": "角色想从对方/情境那里得到什么 (Want/Goal)",
        "observable_zh": [
            "注意力方向: 视锁目标, 重心前倾 5°",
            "主动姿态: 主动姿态 (前倾/侧身/手势)",
            "视线模式: 视线在该目标上, 身体朝向角度 < 10°",
            "呼吸暗示: 一次短吸气 + 胸腔微抬, 表达想要",
            "手指预备: 手指尖在物体上停 0.2 秒, 然后才开始动作",
        ],
        "observable": "注意力方向 + 主动姿态 (前倾/侧身/手势)",
        "fail_pattern": "把 What 写成内心独白, 看不到眼睛/身体的指向",
    },
    "OBSTACLE": {
        "definition": "什么在挡着他 (对方沉默/自己失控/物理限制/时间不够)",
        "observable_zh": [
            "肌肉持续紧张 + 呼吸变浅 + 视线被卡住",
            "该部位持续轻微颤抖, 视线被卡在该部位 0.3 秒",
            "呼吸变浅, 节奏紧, 肩线上提",
            "对抗阻力, 肌肉持续紧, 但不显形",
            "重心后移 0.3 米, 重心前移 0.2 米, 摇摆不定",
        ],
        "observable": "肌肉持续紧张 + 呼吸变浅 + 视线被卡住",
        "fail_pattern": "只写障碍存在, 不写角色在'对抗'这个障碍",
    },
    "COST": {
        "definition": "失败的代价 (被识破/失去位置/失去某人/失去自己)",
        "observable_zh": [
            "嘴角肌肉紧绷 + 手指小动作 + 视线闪避",
            "嘴角肌肉抽一次, 视线闪避, 手指摸固定物",
            "下颌锁, 一次用力闭眼 reset",
            "呼吸停一拍, 手指无意识动作",
            "瞳孔微缩 0.2mm + 眨眼频率翻倍",
        ],
        "observable": "嘴角肌肉紧绷 + 手指小动作 + 视线闪避",
        "fail_pattern": "把 Cost 写成旁白, 实际上它驱动每一个 micro-decision",
    },
    "STRATEGY": {
        "definition": "他正在用什么方法争取 (装轻松/边走边说/慢节奏/假话)",
        "observable_zh": [
            "这是行为的主体, 必须秒级可拆解",
            "假动作节奏均匀, 但胸腔呼吸仍重",
            "步伐节奏固定, 眼睛扫描环境",
            "每个动作首尾各加 0.3s, 中间肌肉保持张力",
            "按描述执行, 不加情绪形容词",
        ],
        "observable": "这是行为的主体, 必须秒级可拆解",
        "fail_pattern": "把 Strategy 写成形容词 ('他很聪明地'), 必须写成动作",
    },
    "TURN": {
        "definition": "什么新信息让他改变策略 (听到一句话/看到某物/自己意识到)",
        "observable_zh": [
            "STRATEGY 的中断 + 一次微事件 + 视线重置",
            "STRATEGY 暂时中断, 一次微事件, 视线重置",
            "手在肚子上不动了 0.6 秒, 然后才继续拍",
            "一次用力闭眼 reset, 然后眼睛重新睁开时已改变",
            "重心突然前移 0.3 米, 肩线锁死",
        ],
        "observable": "STRATEGY 的中断 + 一次微事件 + 视线重置",
        "fail_pattern": "Turn 出现得太早或太晚, 必须发生在 STRATEGY 中段",
    },
}

# 0.3 微生命事件池 (每 1-2 秒一个, 抽签式组合)
# Phase 35.9: 扩展为 5+ 中文 + 5 英文 (原 3-5 词)
MICRO_LIFE_POOL = {
    "breath": [
        "chest rises and falls with a slow recovery rhythm",
        "a single deeper inhale through the nose",
        "a held breath, then a controlled exhale",
        "shallow chest pumps after exertion",
        "breath audibly catches for half a beat",
        # 中文版
        "胸腔起伏, 慢节奏恢复",
        "鼻孔一次深吸气",
        "屏住呼吸, 然后受控呼气",
        "短促浅呼吸, 胸腔短抽",
        "吸气卡顿半拍",
    ],
    "nose": [
        "the nostril flares once and settles",
        "a micro-flare, then the upper lip tightens",
        "the nostril twitch reads as restraint, not disgust",
        # 中文
        "鼻翼微张一次, 然后稳定",
        "鼻翼微动, 然后上唇紧绷",
        "鼻翼抽动表达克制, 不是厌恶",
    ],
    "brow": [
        "the inner brow knits once, then releases",
        "one brow lifts a fraction higher than the other",
        "the brow stays low and heavy, jaw does the work instead",
        # 中文
        "内眉微皱一次, 然后松开",
        "一侧眉毛比另一侧微提",
        "眉头压低沉重, 下颌代偿工作",
    ],
    "eye_dart": [
        "the eye lingers on a fixed point, then releases",
        "a single lateral dart, then re-centers on the target",
        "eyes blink-rate slows down to once every 3-4 seconds",
        "eyes blink-rate doubles for two beats then resets",
        # 中文
        "视线在固定点停留, 然后释放",
        "单次横向扫视, 然后重新对焦",
        "眨眼频率降到 3-4 秒一次",
        "眨眼频率翻倍持续两拍, 然后复位",
    ],
    "mouth": [
        "the tongue presses against the inside of the lower lip",
        "the corner of the mouth tightens without rising",
        "the jaw sets, holds, then releases in a controlled drop",
        "a single lip press, then the lips part slightly",
        # 中文
        "舌头压在下唇内侧",
        "嘴角肌肉收紧但不上扬",
        "下颌锁紧, 停住, 然后受控下放",
        "单次唇压, 然后嘴唇微张",
    ],
    "hand": [
        "the fingers tap a fixed object twice, then stop",
        "the thumb rolls across the knuckle of the index finger",
        "the hand stills on a tool, then resumes",
        "the wrist rotates once, then anchors back to the work",
        "fingers tighten around a held object, then loosen by a fraction",
        # 中文
        "手指在固定物上敲两次, 然后停",
        "拇指在食指指节上滚动",
        "手在工具上静止, 然后继续",
        "手腕转一次, 然后回到工作",
        "手指在握物上收紧, 然后微松",
    ],
    "weight": [
        "weight shifts from one foot to the other, half a beat",
        "the planted foot presses harder, knees never lock",
        "a micro-settle of the center of gravity, then holds",
        # 中文
        "重心从一脚移到另一脚, 半拍",
        "主力脚压地更紧, 膝盖不锁",
        "重心微沉, 然后稳定",
    ],
}

# 0.4 眨眼 3 段式
# Phase 35.9: 加中文版, 不只英文
BLINK_PATTERNS = {
    "lazy_single": "one lazy blink — eyelids close at half speed, hold a fraction, then release",
    "double_quick": "a quick DOUBLE-BLINK — two close-set blinks within 0.4s, like punctuation",
    "hard_reset": "one HARD reset-blink — eyes squeeze shut, the face resets, then opens",
    "slow_three": "three slow blinks in sequence, each a beat apart, the rhythm of a decision",
    "stutter": "one half-blink that fails to close, then a real blink — the eyes lose the timing",
    "deny": "the eyes squeeze shut for 0.3s, head shakes once on the vertical axis, then eyes open",
    # Phase 35.9 中文版 (双语, 优先用)
    "lazy_single_zh": "一次慢眨眼 — 眼睑半速闭上, 停 0.1 秒, 然后松开",
    "double_quick_zh": "一次快速双眨 — 0.4 秒内两次紧邻眨眼, 像标点",
    "hard_reset_zh": "一次用力闭眼 reset — 眼睛用力闭, 脸重置, 然后睁开",
    "slow_three_zh": "三次慢眨, 每次一拍间隔, 像在数拍子做决定",
    "stutter_zh": "一次半眨失败, 然后才真眨 — 眼睛失去节奏",
    "deny_zh": "眼睛用力闭 0.3 秒, 头在垂直轴上摇一次, 然后睁眼",
}

# 0.5 反应类型 (Higgsfield "反应先于台词" + 卡兹克 30 秒场景)
REACTION_TYPES = {
    "agree_but_cost": "听者半句就点了下头, 但肩膀同时塌了 0.5 公分",
    "disagree_verbal_hold": "听者眉毛先紧, 嘴抿成一条线, 2 秒后才开口反驳",
    "calculate": "听者眼睛往左上方扫一次 (调用记忆), 手指停, 再回视说话者",
    "absorb_heavy_news": "听者一次慢眨眼 + 呼吸停一拍 + 视线落固定地标 1.5 秒",
    "pretend_not_heard": "听者嘴角肌肉抽一次, 假装在看别处, 呼吸节奏没变",
    "already_knew": "听者下颌锁, 一次用力闭眼 reset, 视线早已在说话者脸上",
    "half_laugh_crack": "听者嘴角先动, 真笑露 0.2 秒, 然后被压成苦笑",
    "first_real_look": "听者视线从别处回到说话者, 这是本场戏第一次真正对视",
    "decision_lock": "听者手指先停, 然后一次用力闭眼 reset, 再睁眼时已决定",
    "hand_stops_working": "听者本来在做某事, 听到关键句手突然停 0.6 秒, 然后才抬头",
}

# 0.6 静止但保持张力的反例 (Higgsfield "绝不用 nobody moves")
TENSION_LOCATIONS = {
    "held_breath": "every chest muscle still engaged, breath held, no one relaxed",
    "rigid_neck": "the neck stays rigid, only the eyes work",
    "weight_locked": "weight is held over the balls of the feet, not the heels",
    "grip": "the fingers stay closed around whatever was just held",
    "eye_lock": "the gaze is locked on one point, no darting, no softening",
    "jaw_set": "the jaw is set and stays set, no swallow, no lick",
    "shoulder_high": "the shoulders stay raised a half-inch above rest",
    "posture_lock": "the spine is held, the ribs are not breathing fully",
    "muscle_quiver": "one muscle group quivers under load, everything else frozen",
    "delayed_swallow": "the swallow that should have happened at 1.0s is held until 4.0s",
}

# 0.7 全身动作词汇表 (用于 build_action_timing)
# 部位: [可观察的具体动作, 不带情绪形容词]
BODY_VOCAB = {
    "jaw": ["jaw sets", "jaw releases in a controlled drop", "jaw clenches, holds, releases",
            "jaw shifts slightly to one side", "jaw tightens along the masseter line"],
    "shoulder": ["shoulder is pulled low by weight", "shoulders rise a half-inch and hold",
                 "shoulder rolls once, then resets", "shoulder blade pulls back, then drops"],
    "hand": ["fingers tighten on the tool, then loosen by a fraction",
             "thumb rolls across the index knuckle",
             "wrist rotates once, then anchors back to the work",
             "hand stills on a held object, then resumes motion",
             "fingers count once, silently, then close"],
    "eye": ["gaze lingers on a fixed point, then releases",
            "eyes reach the target before the head turns",
            "a single lateral dart, then re-centers",
            "eyes blink-rate slows to once every 3-4 seconds",
            "eye-line drops, holds, lifts to a different target"],
    "head": ["head turns to follow the eye, half a beat late",
             "chin drops a fraction, then levels",
             "head tilts two degrees toward the speaker",
             "head stops mid-turn, holds, then completes the arc"],
    "torso": ["weight shifts from one foot to the other, half a beat",
              "center of gravity settles, then holds",
              "torso rotates 5 degrees away, then back",
              "chest pumps in short shallow pulls after exertion"],
    "mouth": ["lips press together, then part slightly",
              "tongue presses against the inside of the lower lip",
              "the corner of the mouth tightens without rising",
              "a single lip-bite that never quite closes"],
    "brow": ["inner brow knits once, then releases",
             "one brow lifts a fraction higher than the other",
             "brow stays low and heavy, jaw does the work instead"],
    "nose": ["nostril flares once, then settles",
             "a micro-flare, then the upper lip tightens"],
    "feet": ["foot presses harder into the floor, knees never lock",
             "the planted foot stays planted, the other pivots",
             "weight transfers forward onto the balls of the feet"],
}


# ==============================================================================
# 1. 5 要素架构工具 — 任何函数都先调它来生成 5 段"驱动元数据"
# ==============================================================================

def _five_elements_block(domain_focus: str, ctx_brief: str) -> str:
    """
    生成 5 要素架构字符串 — 每个 ACTING 函数都内嵌这 5 段以保证一致性.
    这是 Node 集群约束: "5 要素必须驱动每个函数", 用字面可见的方式实现.

    参数:
        domain_focus: 当前函数关注的"行为领域", 例: "5 支柱结构生成"
        ctx_brief:   上下文缩略 (5 支柱已填好的短摘要)

    返回:
        5 段字符串, 可直接嵌入到 prompt 末尾或函数返回中.
    """
    # DATA
    data = (
        "DATA: Hell Grind 95:06 / 115,446 generations / 14 days / 4 street kids "
        "with supernatural powers / ACTING skill original document (3 skills: "
        "CINEDANCE, ACTING, LIRA) / 16181 generations for the first 25 minutes, "
        "253 shots kept, 64 generations per kept shot"
    )
    # CTX
    ctx = "CTX: " + (ctx_brief or "(no brief provided)")
    # SKL
    skl = (
        "SKL/HARNESS: 5 PILLARS (WHAT/OBSTACLE/COST/STRATEGY/TURN) + "
        "no emotion words, only observable behavior + 3-stage blink (lazy/double/hard) + "
        "eye-leads-head + 1-2s micro-life + tension-not-stillness + reaction-before-line + "
        "hands-busy + a single hard accent when hands stop"
    )
    # EXP
    exp = (
        "EXP: ROCO training room (12s, 5 pillars, eye-leads-head) / "
        "JAX & REIN corridor (3-4s beat, distant impact splits attention) / "
        "VILLAIN entrance (never raises voice, slow cadence) / "
        "FACS 12 units + actual-shot ACTION TIMING samples"
    )
    # AID
    aid = (
        "AID: anti-AI kill list (191 phrases) + dynamic generation from input params "
        "(no templates) + every output must contain at least one observable muscle cue "
        "+ every beat must carry an INNER monologue + beats cap at 3 sentences"
    )

    return "\n".join([
        "=== 5-ELEMENT DRIVER ===",
        data,
        ctx,
        skl,
        exp,
        aid,
        "FOCUS: " + domain_focus,
        "=======================",
    ])


# ==============================================================================
# 2. 核心函数 1: build_5_pillars
# ==============================================================================

def build_5_pillars(goal: str, obstacle: str, cost: str, strategy: str, turn: str = "") -> dict:
    """
    建立 5 支柱 (WHAT/OBSTACLE/COST/STRATEGY/TURN).

    这是 ACTING skill 的根函数, 任何其他函数都需要先建立 5 支柱才有可写的"内容".
    设计原则:
    - 每条都是"可观察"或"可翻译成可观察" (不写"他想赢", 写"他在第三次挥击前停 0.4 秒")
    - TURN 是可选的 (空字符串 = 本场戏不发生转折, 但仍写明这一点)
    - 返回 dict, 后续函数按需取字段

    参数:
        goal:     角色想从对方/情境那里得到什么 (Pillar 1: WHAT)
        obstacle: 什么在挡着他 (Pillar 2: OBSTACLE)
        cost:     失败的代价 (Pillar 3: COST)
        strategy: 他正在用什么方法争取 (Pillar 4: STRATEGY)
        turn:     什么新信息让他改变策略 (Pillar 5: TURN, 可选)

    返回:
        dict with keys: what/obstacle/cost/strategy/turn/observable/inner_burn

    示例:
        >>> p = build_5_pillars(
        ...     goal="在 JAX 和 REIN 推门前, 再完成一次干净攻击",
        ...     obstacle="右臂的水晶越来越不听使唤, 第二次蓄力就抽筋",
        ...     cost="被他们看到, 就要解释失控, 解释就意味着整组行动降级",
        ...     strategy="把动作拆小, 装作用力, 实际上每一击都没真发力",
        ...     turn="门被推开的声音, 他必须立刻决定要不要藏",
        ... )
    """
    # 5 要素驱动 (CTX 字段是基于 5 个参数动态生成的, 不是模板)
    ctx_brief = "WHAT=" + goal[:30] + "... | OBSTACLE=" + obstacle[:30] + "..."
    five = _five_elements_block("5 支柱结构生成", ctx_brief)

    # 把每条支柱翻译成"可观察行为锚点" — 这是动态行为, 不是模板
    # 关键词驱动: "想/希望/赢" → attention 锚点; "挡/阻止/难" → muscle-load 锚点
    def _observable(field: str, text: str) -> str:
        t = (text or "").lower()
        if not text:
            return "(unset)"
        # WHAT: 注意力方向
        if field == "what":
            if any(k in t for k in ["想", "要", "希望", "win", "get", "show"]):
                return "attention: 视锁目标, 重心前倾 5°, 主动姿态"
            return "attention: 视线在该目标上, 身体朝向角度 < 10°"
        # OBSTACLE: 持续肌肉负载
        if field == "obstacle":
            if any(k in t for k in ["失控", "不听话", "broken", "lose", "out of control"]):
                return "load: 该部位持续轻微颤抖, 视线被卡在该部位 0.3 秒"
            if any(k in t for k in ["时间", "time", "快", "fast"]):
                return "load: 呼吸变浅, 节奏紧, 肩线上提"
            return "load: 对抗阻力, 肌肉持续紧, 但不显形"
        # COST: 触发点
        if field == "cost":
            if any(k in t for k in ["被发现", "暴露", "found", "caught"]):
                return "trigger: 嘴角肌肉抽一次, 视线闪避, 手指摸固定物"
            if any(k in t for k in ["失去", "lose", "fail"]):
                return "trigger: 下颌锁, 一次用力闭眼 reset"
            return "trigger: 呼吸停一拍, 手指无意识动作"
        # STRATEGY: 正在做什么
        if field == "strategy":
            if any(k in t for k in ["装", "假装", "pretend", "fake"]):
                return "action: 假动作节奏均匀, 但胸腔呼吸仍重"
            if any(k in t for k in ["边走", "走", "walk"]):
                return "action: 步伐节奏固定, 眼睛扫描环境"
            if any(k in t for k in ["慢", "slow"]):
                return "action: 每个动作首尾各加 0.3s, 中间肌肉保持张力"
            return "action: 按描述执行, 不加情绪形容词"
        # TURN
        if field == "turn":
            if not text:
                return "(no turn in this beat — strategy holds)"
            return "turn: STRATEGY 暂时中断, 一次微事件, 视线重置"
        return text

    pillars = {
        "what": goal,
        "obstacle": obstacle,
        "cost": cost,
        "strategy": strategy,
        "turn": turn if turn else "(no turn in this beat)",
        "observable": {
            "what": _observable("what", goal),
            "obstacle": _observable("obstacle", obstacle),
            "cost": _observable("cost", cost),
            "strategy": _observable("strategy", strategy),
            "turn": _observable("turn", turn),
        },
        # inner_burn: 角色在持续燃烧的内心状态, 后续 INNER 函数从这里派生
        "inner_burn": (
            "INNER (未说出口): " + goal + " — 但他知道 " + obstacle + ", "
            "所以他选择 " + strategy + ". 每一次动作都在用身体回答一个问题: "
            "我还撑得住吗。"
        ),
        "_5_elements": five,
    }
    return pillars


# ==============================================================================
# 3. 核心函数 2: translate_emotion_to_action
# ==============================================================================

def translate_emotion_to_action(emotion: str) -> dict:
    """
    把情绪词翻译成身体动作.

    这是 ACTING skill 的"反 AI 词表"具象化. 任何上游传下来的情绪词 (sad/angry/无奈/崩溃)
    在这里都被翻译成至少 3 条"可观察"的身体行为 + 1 条 INNER.

    设计原则:
    - 中英文都支持
    - 找不到的情绪词会回落到 "resigned" 的身体组合 + 标记 fallback
    - 输出至少 1 个慢速眨眼 + 1 个 micro-load + 1 个 INNER

    参数:
        emotion: 情绪词, 例: "sad" / "angry" / "无奈" / "崩溃" / "hesitant"

    返回:
        dict with keys: raw_emotion/muscle_cues/blink/breath/inner/micro_life/fallback
    """
    # 5 要素驱动
    five = _five_elements_block(
        "情绪 → 身体动作翻译",
        "raw=" + emotion,
    )

    # 1) 走查反 AI 词表
    for bad, good in ACTING_AI_KILL:
        if emotion == bad or emotion.lower() == bad.lower():
            # 找到精确替换: 把 good 解析为多个动作
            parts = [p.strip() for p in good.replace("，", ",").split(",")]
            muscle_cues = parts if len(parts) >= 2 else [parts[0], "muscle load on the jaw", "eye-line drops 5°"]
            return {
                "raw_emotion": emotion,
                "muscle_cues": muscle_cues,
                "blink": BLINK_PATTERNS["slow_three"],
                "breath": MICRO_LIFE_POOL["breath"][3],  # shallow chest pumps
                "inner": "INNER: 这个状态我没有词, 我只有身体在替我回答。",
                "micro_life": [
                    MICRO_LIFE_POOL["brow"][2],  # brow stays low
                    MICRO_LIFE_POOL["mouth"][2],  # jaw sets, holds, releases
                ],
                "fallback": False,
                "_5_elements": five,
            }

    # 2) 已知情绪 → 标准翻译
    known = {
        "sad": {
            "muscle_cues": ["jaw drops half a centimeter, then holds",
                            "the inner corner of the brow lifts and stays",
                            "the eye blink slows to 0.8s each",
                            "the shoulders round forward by 5°"],
            "blink": BLINK_PATTERNS["slow_three"],
            "breath": MICRO_LIFE_POOL["breath"][2],
            "inner": "INNER: 有什么东西沉下去, 但我没有让它出声。",
            "micro_life": [MICRO_LIFE_POOL["brow"][1], MICRO_LIFE_POOL["mouth"][1]],
        },
        "angry": {
            "muscle_cues": ["the masseter tightens and stays tight",
                            "the nostril flares once, the upper lip compresses",
                            "weight transfers forward onto the balls of the feet",
                            "the fingers curl inward, knuckles whiten"],
            "blink": BLINK_PATTERNS["hard_reset"],
            "breath": MICRO_LIFE_POOL["breath"][4],  # breath catches
            "inner": "INNER: 我不会先开口, 但我的身体已经把话讲完了。",
            "micro_life": [MICRO_LIFE_POOL["nose"][1], MICRO_LIFE_POOL["hand"][4]],
        },
        "shocked": {
            "muscle_cues": ["one HARD reset-blink",
                            "the chin pulls back half a beat",
                            "the inhale catches at the top of the throat",
                            "the hand that was working goes still for 0.6s"],
            "blink": BLINK_PATTERNS["hard_reset"],
            "breath": MICRO_LIFE_POOL["breath"][4],
            "inner": "INNER: 等一下。",
            "micro_life": [MICRO_LIFE_POOL["brow"][0], MICRO_LIFE_POOL["weight"][0]],
        },
        "hesitant": {
            "muscle_cues": ["the lips part, then press back together",
                            "the eye-line drops to a fixed point, holds 0.6s, lifts",
                            "the head tilts 2° toward the speaker, no more",
                            "the swallow that should have happened is held"],
            "blink": BLINK_PATTERNS["stutter"],
            "breath": MICRO_LIFE_POOL["breath"][1],
            "inner": "INNER: 我在找一个开口。",
            "micro_life": [MICRO_LIFE_POOL["mouth"][0], MICRO_LIFE_POOL["eye_dart"][1]],
        },
        "determined": {
            "muscle_cues": ["the jaw locks and does not release",
                            "the gaze centers on the target and does not leave",
                            "weight shifts forward 3cm, the planted foot presses",
                            "the fingers close on whatever was held"],
            "blink": BLINK_PATTERNS["deny"],
            "breath": MICRO_LIFE_POOL["breath"][0],
            "inner": "INNER: 不回头了。",
            "micro_life": [MICRO_LIFE_POOL["hand"][0], MICRO_LIFE_POOL["weight"][2]],
        },
        "calm": {
            "muscle_cues": ["the shoulders drop 1cm and stay dropped",
                            "the breath rate drops to one full cycle per 4 seconds",
                            "the eye-line is level, blinks are even and spaced",
                            "the hands rest open, fingers slightly curled"],
            "blink": BLINK_PATTERNS["lazy_single"],
            "breath": MICRO_LIFE_POOL["breath"][0],
            "inner": "INNER: 我知道接下来会发生什么, 但我不急。",
            "micro_life": [MICRO_LIFE_POOL["breath"][0], MICRO_LIFE_POOL["weight"][2]],
        },
        # 中文常见情绪
        "悲伤": {
            "muscle_cues": ["下颌松, 不咬合",
                            "内眉上提, 不松开",
                            "眨眼拉到 0.8 秒一次",
                            "肩线前扣 5°"],
            "blink": BLINK_PATTERNS["slow_three"],
            "breath": MICRO_LIFE_POOL["breath"][2],
            "inner": "INNER: 有什么东西沉下去, 但我没让它出声。",
            "micro_life": [MICRO_LIFE_POOL["brow"][1], MICRO_LIFE_POOL["mouth"][1]],
        },
        "愤怒": {
            "muscle_cues": ["咬肌锁紧不松",
                            "鼻翼动一次, 上唇压",
                            "重心前移到前脚掌",
                            "手指内扣, 指节发白"],
            "blink": BLINK_PATTERNS["hard_reset"],
            "breath": MICRO_LIFE_POOL["breath"][4],
            "inner": "INNER: 我不会先开口, 我的身体已经讲完了。",
            "micro_life": [MICRO_LIFE_POOL["nose"][1], MICRO_LIFE_POOL["hand"][4]],
        },
        "坚定": {
            "muscle_cues": ["下颌锁, 不松",
                            "视线锁死, 不移开",
                            "重心前 3cm, 主力脚压地",
                            "手指合拢握住手里的东西"],
            "blink": BLINK_PATTERNS["deny"],
            "breath": MICRO_LIFE_POOL["breath"][0],
            "inner": "INNER: 不回头。",
            "micro_life": [MICRO_LIFE_POOL["hand"][0], MICRO_LIFE_POOL["weight"][2]],
        },
        "崩溃": {
            "muscle_cues": ["肩线上提 1cm, 锁住",
                            "呼吸断在喉咙, 不能完整换气",
                            "手指找不到着力点, 在桌面上划 0.2 秒",
                            "视线快速扫一次, 找不到锚点"],
            "blink": BLINK_PATTERNS["stutter"],
            "breath": MICRO_LIFE_POOL["breath"][4],
            "inner": "INNER: 我撑不住了。",
            "micro_life": [MICRO_LIFE_POOL["brow"][0], MICRO_LIFE_POOL["hand"][3]],
        },
    }

    key = emotion.lower() if isinstance(emotion, str) else ""
    if key in known:
        k = known[key]
        return {
            "raw_emotion": emotion,
            "muscle_cues": k["muscle_cues"],
            "blink": k["blink"],
            "breath": k["breath"],
            "inner": k["inner"],
            "micro_life": k["micro_life"],
            "fallback": False,
            "_5_elements": five,
        }

    # 3) 兜底: 未知情绪 → 用 universal 组合 + 标记 fallback
    return {
        "raw_emotion": emotion,
        "muscle_cues": [
            "the body picks a single micro-load and holds it: jaw, shoulder, or hand",
            "the eye-line centers on a fixed point, does not dart",
            "one breath is held past the natural point, then released",
            "the hand that was busy stops, holds, then resumes at a slower rate",
        ],
        "blink": BLINK_PATTERNS["lazy_single"],
        "breath": MICRO_LIFE_POOL["breath"][0],
        "inner": "INNER (" + str(emotion) + "): 状态我没法用词命名, 身体知道。",
        "micro_life": [MICRO_LIFE_POOL["weight"][2], MICRO_LIFE_POOL["hand"][3]],
        "fallback": True,
        "_5_elements": five,
    }


# ==============================================================================
# 4. 核心函数 3: build_action_timing
# ==============================================================================

def build_action_timing(beats):
    """
    构造秒级动作时间线 — ACTION TIMING 区.

    beats 格式: List of (start_sec, end_sec, body_action, inner_monologue)
    - start_sec / end_sec: 浮点秒, 必须 start < end
    - body_action: 一段可观察的身体行为 (2-3 句话, 不带情绪词)
    - inner_monologue: 这段时间角色未说出口的内心

    设计原则:
    - 每个 beat ≤ 3 句话 (Higgsfield: 单个节拍超载, 模型会糊)
    - 每个 beat 必须有 INNER (这是骨架, 不是装饰)
    - 时间段不能重叠, 也不能有 0.5s 以上的"无人区"
    - 至少 50% 的 beat 必须包含一个 micro-load (jaw/breath/hand)

    参数:
        beats: List[Tuple[float, float, str, str]]

    返回:
        str: 完整 ACTION TIMING 块, 可直接贴入 prompt
    """
    # 5 要素驱动
    ctx_brief = "beats=" + str(len(beats)) + ", total_span=" + (
        str(round(beats[-1][1] - beats[0][0], 2)) + "s" if beats else "0s"
    )
    five = _five_elements_block("秒级动作时间线", ctx_brief)

    if not beats:
        return "ACTION TIMING: (no beats provided)\n\n" + five

    # 校验: 时间段不能重叠
    sorted_beats = sorted(beats, key=lambda b: b[0])
    issues = []
    prev_end = 0.0
    for i, (s, e, body, inner) in enumerate(sorted_beats):
        if s >= e:
            issues.append("beat " + str(i) + ": start >= end")
        if s < prev_end - 0.01:
            issues.append("beat " + str(i) + ": overlaps previous beat")
        prev_end = max(prev_end, e)

    lines = []
    lines.append("ACTION TIMING (seconds, observable, INNER is unspoken):")
    for i, (s, e, body, inner) in enumerate(sorted_beats):
        s_str = "{:.2f}".format(s).rstrip("0").rstrip(".")
        e_str = "{:.2f}".format(e).rstrip("0").rstrip(".")
        # 3 句话硬上限
        sentences = [x.strip() for x in body.replace("。", ".").split(".") if x.strip()]
        if len(sentences) > 3:
            body = ". ".join(sentences[:3]) + "."
        lines.append("  " + s_str + "s-" + e_str + "s — " + body.strip())
        if inner:
            lines.append("      INNER: " + inner.strip())

    output = "\n".join(lines)
    if issues:
        output += "\n  [TIMING WARNINGS] " + " | ".join(issues)
    output += "\n\n" + five
    return output


# ==============================================================================
# 5. 核心函数 4: build_blink_sequence
# ==============================================================================

def build_blink_sequence(pattern: str = "default") -> str:
    """
    构造眨眼序列 — Higgsfield "活脸最便宜的信号".

    可用 pattern:
    - "default"        : lazy + double + hard 三段式 (默认, 适合大多数镜头)
    - "tense"          : 紧绷, 长时间不眨 → 一次 hard reset
    - "nervous"        : 高频半眨, 一次失败再成功
    - "calm"           : 均匀慢眨, 每 3-4 秒一次
    - "deciding"       : 三次慢眨, 每次一拍, 像在数拍子
    - "reset_only"     : 只一次用力闭眼 reset
    - "lazy_only"      : 只一次缓慢眨眼
    - "double_only"    : 只两次快速眨眼
    - 自定义字符串: 直接作为额外说明追加

    参数:
        pattern: 眨眼模式名

    返回:
        str: 完整眨眼描述, 含时机
    """
    five = _five_elements_block("眨眼序列 (3 段式)", "pattern=" + pattern)

    presets = {
        "default": [
            ("0.0s", "one lazy blink — eyelids close at half speed, hold a fraction, then release"),
            ("1.2s", "a quick DOUBLE-BLINK within 0.4s, like punctuation"),
            ("3.0s", "one HARD reset-blink — eyes squeeze shut, the face resets, then opens"),
        ],
        "tense": [
            ("0.0s", "no blink for 2.5s — the gaze stays locked"),
            ("2.5s", "one HARD reset-blink — eyes squeeze shut, the face resets, then opens"),
            ("3.5s", "no further blinks — the tension holds"),
        ],
        "nervous": [
            ("0.0s", "one half-blink that fails to close, then a real blink — the eyes lose the timing"),
            ("0.8s", "another quick half-blink, then a full one"),
            ("2.0s", "blink rate doubles for two beats, then resets to normal"),
        ],
        "calm": [
            ("0.0s", "even blinks, one every 3.2s, full close, full open, no half-measures"),
            ("3.2s", "second blink, same rhythm, same speed"),
            ("6.4s", "third blink — the calm holds, the rhythm holds"),
        ],
        "deciding": [
            ("0.0s", "three slow blinks in sequence, each a beat apart — the rhythm of a decision"),
            ("1.0s", "(second blink) — the eye is still working the problem"),
            ("2.0s", "(third blink) — by the time the eyes open, the decision is made"),
        ],
        "reset_only": [("0.0s", "one HARD reset-blink — eyes squeeze shut, the face resets, then opens")],
        "lazy_only": [("0.0s", "one lazy blink — eyelids close at half speed, hold a fraction, then release")],
        "double_only": [("0.0s", "a quick DOUBLE-BLINK — two close-set blinks within 0.4s, like punctuation")],
    }

    if pattern in presets:
        seq = presets[pattern]
    else:
        # 自定义: 把 pattern 当作额外说明
        seq = [
            ("0.0s", "one lazy blink — eyelids close at half speed, hold a fraction, then release"),
            ("1.5s", "a quick DOUBLE-BLINK within 0.4s"),
            ("3.0s", "one HARD reset-blink — eyes squeeze shut, the face resets, then opens"),
            ("(extra)", pattern),
        ]

    lines = ["BLINK SEQUENCE (pattern=" + pattern + "):"]
    for t, desc in seq:
        lines.append("  @ " + t + " — " + desc)
    lines.append("  Rule: every HARD reset is followed by a face that has visibly settled.")
    lines.append("")
    lines.append(five)
    return "\n".join(lines)


# ==============================================================================
# 6. 核心函数 5: build_eye_lead
# ==============================================================================

def build_eye_lead(eye_target: str, head_target: str, lead_seconds: float = 0.5) -> str:
    """
    视线先于头 — Higgsfield "眼睛先到门口, 头晚半拍".

    规则:
    - 视线先到达 eye_target
    - 头在 lead_seconds 后才转
    - lead_seconds 推荐 0.4-0.7, 太短看不出, 太长像"看错地方"

    参数:
        eye_target:   视线先到的目标 (字符串, 自然语言)
        head_target:  头转过去的目标 (字符串, 自然语言)
        lead_seconds: 视线领先头的秒数, 默认 0.5

    返回:
        str: 完整视线-头部时序
    """
    five = _five_elements_block("视线先于头", "eye=" + eye_target + " | head=" + head_target + " | lead=" + str(lead_seconds) + "s")

    s = "{:.2f}".format(lead_seconds).rstrip("0").rstrip(".")
    out = []
    out.append("EYE-LEADS-HEAD (the eyes arrive first, the head is half a beat late):")
    out.append("  T+0.00s — eye-line begins moving toward: " + eye_target)
    out.append("  T+" + s + "s — eye-line is locked on: " + eye_target + " (head has NOT moved yet)")
    out.append("  T+" + s + "s — head begins rotating toward: " + head_target)
    out.append("  T+" + "{:.2f}".format(lead_seconds * 2.2).rstrip("0").rstrip(".") + "s — head is aligned with: " + head_target)
    out.append("  Note: the eye always finds the target first. The body follows what the eye already knows.")
    out.append("")
    out.append(five)
    return "\n".join(out)


# ==============================================================================
# 7. 核心函数 6: build_micro_life
# ==============================================================================

def build_micro_life(interval_sec: float = 1.5, duration_sec: float = 12.0, density: str = "medium") -> str:
    """
    微生命事件 — 每 1-2 秒一个可见微事件 (呼吸/鼻翼/眉头/手指/重心).

    设计原则:
    - 不写"nobody moves"或"all is still" — 模型会真的冻结画面
    - 写"人物保持静止, 但每隔 1.5s 仍有一个微小事件"
    - density: low (每 2.0s) / medium (每 1.5s) / high (每 1.0s)

    参数:
        interval_sec:  微事件间隔 (秒), 默认 1.5
        duration_sec:  总时长 (秒), 默认 12
        density:       密度, 默认 medium

    返回:
        str: 完整微生命时间线
    """
    five = _five_elements_block("微生命事件 (1-2s 间隔)", "interval=" + str(interval_sec) + "s | span=" + str(duration_sec) + "s | density=" + density)

    # 密度强制
    if density == "low":
        interval_sec = max(interval_sec, 2.0)
    elif density == "high":
        interval_sec = min(interval_sec, 1.0)
    else:
        interval_sec = max(1.0, min(2.0, interval_sec))

    # 7 个微生命类别, 轮询抽取
    pools = [
        ("breath", MICRO_LIFE_POOL["breath"]),
        ("nose", MICRO_LIFE_POOL["nose"]),
        ("brow", MICRO_LIFE_POOL["brow"]),
        ("eye", MICRO_LIFE_POOL["eye_dart"]),
        ("mouth", MICRO_LIFE_POOL["mouth"]),
        ("hand", MICRO_LIFE_POOL["hand"]),
        ("weight", MICRO_LIFE_POOL["weight"]),
    ]

    out = []
    out.append("MICRO-LIFE TIMELINE (one visible micro-event every " + str(interval_sec) + "s, no freeze):")
    out.append("  Rule: there is no second in this shot where the character is fully inert.")
    t = 0.0
    counter = 0
    while t < duration_sec:
        cat, pool = pools[counter % len(pools)]
        # 用 hash 让"同一个 t"对应确定的微事件, 但每次都不同
        idx = (counter * 3 + int(t * 10)) % len(pool)
        out.append("  T+" + "{:.1f}".format(t) + "s — " + cat + ": " + pool[idx])
        t += interval_sec
        counter += 1
    out.append("")
    out.append(five)
    return "\n".join(out)


# ==============================================================================
# 8. 核心函数 7: build_inner_monologue
# ==============================================================================

def build_inner_monologue(thought: str, intensity: str = "medium", beat_context: str = "") -> str:
    """
    INNER 内心独白 — 每个动作配一行未说出口的内心.

    设计原则:
    - 必须以 "INNER:" 开头, 5 支柱任何一字段都可以派生一条 INNER
    - intensity: whisper / medium / shout (只是格式层, 模型不会真做出音量, 但影响句长)
    - beat_context: 可选, 描述"这一刻在做什么", 用于短句裁剪

    参数:
        thought:      内心内容 (自然语言)
        intensity:    强度, 默认 medium
        beat_context: 当前 beat 的上下文 (可选)

    返回:
        str: 格式化的 INNER 行
    """
    five = _five_elements_block("INNER 内心独白", "intensity=" + intensity)

    # 强度 → 句长上限
    caps = {"whisper": 8, "medium": 18, "shout": 30}
    cap = caps.get(intensity, 18)

    # 短句裁剪 (按中文/英文标点切)
    t = thought.strip()
    for sep in ["。", ".", "！", "!", "？", "?"]:
        if sep in t:
            t = t.split(sep)[0]
            break
    if len(t) > cap:
        # 保留前 cap 个字符, 加省略号
        t = t[:cap].rstrip() + "…"

    out = []
    if beat_context:
        out.append("INNER (during: " + beat_context + ", intensity=" + intensity + "):")
    else:
        out.append("INNER (intensity=" + intensity + "):")
    out.append("  " + t)
    out.append("  Note: this line is NOT spoken. It is the only place where the character's interior surfaces.")
    out.append("")
    out.append(five)
    return "\n".join(out)


# ==============================================================================
# 9. 核心函数 8: build_reaction_chain
# ==============================================================================

def build_reaction_chain(listener_beat: str, reaction_type: str = "absorb_heavy_news",
                         speaker_line_tail: str = "") -> str:
    """
    反应链 — Higgsfield "听话的人半句就懂了, 脸已经先答了".

    规则:
    - 反应在 speaker_line 结束前就发生
    - 反应包括: micro-load + blink + breath + 视线落点
    - 半秒消化后再开口
    - 情绪尾巴带进下一镜, 不归零

    参数:
        listener_beat:    听者是谁, 在做什么 (例: "JAX 在走廊边走边说")
        reaction_type:    反应类型 (REACTION_TYPES 字典的 key, 或自定义)
        speaker_line_tail: 说话者这一句的尾巴 (可选, 用于"上一句尾音喂进这一镜")

    返回:
        str: 完整反应链
    """
    five = _five_elements_block("反应先于台词 (Higgsfield)", "listener=" + listener_beat + " | type=" + reaction_type)

    if reaction_type in REACTION_TYPES:
        reaction_line = REACTION_TYPES[reaction_type]
    else:
        reaction_line = reaction_type  # 自定义

    out = []
    out.append("REACTION CHAIN (reaction before line ends):")
    if speaker_line_tail:
        out.append("  T-0.50s — speaker's last words land: \"" + speaker_line_tail + "\"")
    out.append("  T-0.30s — listener's face already answers, before the sentence closes")
    out.append("    -> " + reaction_line)
    out.append("  T+0.00s — speaker's line ends, listener's micro-load is already at full")
    out.append("  T+0.20s — a single hard reset-blink or one slow blink (the body absorbing)")
    out.append("  T+0.50s — half a beat of stillness, breath settles, only then can listener speak")
    out.append("  T+0.80s — listener opens mouth / first word")
    out.append("")
    out.append("  Note: the emotion from this reaction is NOT zeroed. It carries into the next clip,")
    out.append("        so the cut is invisible.")
    out.append("")
    out.append(five)
    return "\n".join(out)


# ==============================================================================
# 10. 核心函数 9: act_no_motion_but_tension
# ==============================================================================

def act_no_motion_but_tension(tension: str = "held_breath", body_zone: str = "full") -> str:
    """
    静止但保持张力 — Higgsfield 明确禁止 "nobody moves" / "all is still".

    用法: 写"全场不动"时, 改成"全场维持这个张力", 模型不会冻结画面.

    参数:
        tension:   张力类型 (TENSION_LOCATIONS 的 key, 或自定义)
        body_zone: 身体区域 ("face" / "torso" / "hands" / "full"), 默认 full

    返回:
        str: 完整的"静止 = 张力"描述
    """
    five = _five_elements_block("静止保持张力 (NOT nobody moves)", "tension=" + tension + " | zone=" + body_zone)

    base = TENSION_LOCATIONS.get(tension, tension)  # 自定义也走同一条路

    out = []
    out.append("NO-MOTION-BUT-TENSION (Higgsfield rule — 'nobody moves' freezes the frame;")
    out.append("                          instead, every muscle holds a defined load):")
    out.append("")
    out.append("  primary tension: " + base)
    out.append("  body zone: " + body_zone)
    out.append("")
    out.append("  Mandatory carries (these MUST keep moving, even when everything else is still):")
    if body_zone in ("face", "full"):
        out.append("    - the eye-line is alive: it holds, then micro-darts, then holds again")
        out.append("    - the blink rhythm continues (1 lazy + 1 double + 1 hard across the beat)")
    if body_zone in ("torso", "full"):
        out.append("    - the chest is breathing, but the breath is held at the top, not released")
    if body_zone in ("hands", "full"):
        out.append("    - if the hand is on a tool, the tool trembles once, then the grip resets")
        out.append("    - if the hand is empty, the fingers count once silently, then close")
    out.append("")
    out.append("  Forbidden phrase in the prompt: 'nobody moves', 'all is still', 'frozen in place',")
    out.append("  'time stands still'. Use 'every muscle holds a defined load' instead.")
    out.append("")
    out.append(five)
    return "\n".join(out)


# ==============================================================================
# 11. 核心函数 10: render_acting_prompt (聚合函数, 整场戏的 CHARACTER ACTING 块)
# ==============================================================================

def render_acting_prompt(actor: dict, scene_context: dict) -> str:
    """
    渲染完整表演 prompt block — 聚合 5 支柱 / 动作时间线 / 眨眼 / 视线 / 微生命 / INNER / 反应链.

    actor 字典字段 (用户输入):
        - name:        角色名
        - descriptors: 角色文字描述 (来自资产系统, 逐字进 prompt)
        - pillars:     build_5_pillars() 的输出
        - emotion:     当前主情绪 (会被 translate_emotion_to_action)
        - blink:       眨眼模式 ("default"/"tense"/...)
        - inner:       INNER 内心独白字符串
        - reaction:    听者反应类型 (如果有对手)
        - hands_busy:  角色在做什么手上的活 (例: "polishing a stone", "tapping on tablet")
        - action_beats: List of (start, end, body, inner) — 喂给 build_action_timing
        - duration:    镜头时长 (秒)

    scene_context 字段:
        - location_id: 地点资产 ID
        - other_chars: 同场景其他角色
        - line_tail:   上一句台词的尾音 (用于反应链接缝)

    返回:
        str: 完整 CHARACTER ACTING 块, 可直接喂给 Seedance 等视频生成模型
    """
    # 5 要素驱动 (顶层)
    five = _five_elements_block(
        "完整 CHARACTER ACTING 块",
        "actor=" + actor.get("name", "?") + " | duration=" + str(actor.get("duration", 12)) + "s"
    )

    out = []
    out.append("=" * 60)
    out.append("CHARACTER ACTING — " + actor.get("name", "ACTOR"))
    out.append("=" * 60)
    out.append("")

    # 1) 角色描述符 (逐字进 prompt, Higgsfield 规则)
    out.append("[DESCRIPTOR — verbatim from asset, do not paraphrase]")
    out.append("  " + actor.get("descriptors", "(no descriptor provided)"))
    out.append("")

    # 2) 5 支柱
    p = actor.get("pillars") or build_5_pillars(
        actor.get("goal", ""),
        actor.get("obstacle", ""),
        actor.get("cost", ""),
        actor.get("strategy", ""),
        actor.get("turn", ""),
    )
    out.append("[5 PILLARS — what drives this beat]")
    out.append("  1. WHAT     : " + p["what"])
    out.append("  2. OBSTACLE : " + p["obstacle"])
    out.append("  3. COST     : " + p["cost"])
    out.append("  4. STRATEGY : " + p["strategy"])
    out.append("  5. TURN     : " + p["turn"])
    out.append("  inner_burn : " + p["inner_burn"])
    out.append("")

    # 3) 情绪翻译
    emo = actor.get("emotion", "calm")
    ea = translate_emotion_to_action(emo)
    out.append("[EMOTION → ACTION: " + str(emo) + " — observable only, no emotion words in the action line]")
    for cue in ea["muscle_cues"]:
        out.append("  - " + cue)
    out.append("  blink: " + ea["blink"])
    out.append("  breath: " + ea["breath"])
    if ea.get("fallback"):
        out.append("  (note: input emotion was unknown; used universal muscle-load fallback)")
    out.append("")

    # 4) 动作时间线
    beats = actor.get("action_beats") or []
    if beats:
        out.append("[ACTION TIMING — " + str(len(beats)) + " beats]")
        # 复用 build_action_timing 但去掉 5-elements footer
        timing_only = build_action_timing(beats).split("=== 5-ELEMENT DRIVER")[0]
        out.append(timing_only)
        out.append("")

    # 5) 眨眼
    if actor.get("blink"):
        out.append("[BLINK SEQUENCE]")
        blink_only = build_blink_sequence(actor["blink"]).split("=== 5-ELEMENT DRIVER")[0]
        out.append(blink_only)
        out.append("")

    # 6) 视线先于头
    if actor.get("eye_lead_eye") and actor.get("eye_lead_head"):
        out.append("[EYE-LEADS-HEAD]")
        el_only = build_eye_lead(actor["eye_lead_eye"], actor["eye_lead_head"]).split("=== 5-ELEMENT DRIVER")[0]
        out.append(el_only)
        out.append("")

    # 7) 微生命
    if actor.get("micro_life", True):
        interval = actor.get("micro_life_interval", 1.5)
        duration = actor.get("duration", 12.0)
        out.append("[MICRO-LIFE — every " + str(interval) + "s, no freeze]")
        ml_only = build_micro_life(interval, duration).split("=== 5-ELEMENT DRIVER")[0]
        out.append(ml_only)
        out.append("")

    # 8) INNER
    if actor.get("inner"):
        out.append("[INNER — spoken to no one]")
        out.append("  " + actor["inner"])
        out.append("")

    # 9) 让手忙起来 (Higgsfield: hands-busy, hard accent = hands stop)
    if actor.get("hands_busy"):
        out.append("[HANDS-BUSY — character is doing something physical while talking]")
        out.append("  task: " + actor["hands_busy"])
        if actor.get("hard_accent_when"):
            out.append("  HARD ACCENT: at T+" + str(actor.get("hard_accent_when", 0)) +
                       "s the " + actor["hands_busy"] + " STOPS for 0.6s — the hands freeze before the face moves")
        out.append("  rule: the strongest beat is the moment the hands stop working")
        out.append("")

    # 10) 反应链
    if actor.get("reaction"):
        out.append("[REACTION CHAIN — listener answers before the line ends]")
        rc_only = build_reaction_chain(
            listener_beat=actor.get("reaction_listener", "the other character in frame"),
            reaction_type=actor["reaction"],
            speaker_line_tail=scene_context.get("line_tail", ""),
        ).split("=== 5-ELEMENT DRIVER")[0]
        out.append(rc_only)
        out.append("")

    # 11) 静止保持张力 (如启用)
    if actor.get("still_tension"):
        out.append("[STILL-BUT-TENSION]")
        st_only = act_no_motion_but_tension(actor["still_tension"], actor.get("still_zone", "full")).split("=== 5-ELEMENT DRIVER")[0]
        out.append(st_only)
        out.append("")

    # 12) 场景上下文
    out.append("[SCENE CONTEXT — verbatim from asset]")
    if scene_context.get("location_id"):
        out.append("  location: " + scene_context["location_id"])
    if scene_context.get("other_chars"):
        out.append("  other characters in frame: " + ", ".join(scene_context["other_chars"]))
    if scene_context.get("line_tail"):
        out.append("  previous line tail (feed into T-0.5s): \"" + scene_context["line_tail"] + "\"")
    out.append("")

    # 13) 5 要素 footer
    out.append(five)
    out.append("=" * 60)

    return "\n".join(out)


# ==============================================================================
# 12. 三个 Hell Grind 完整示例 — 从原始公开资料复刻
# ==============================================================================

def example_roco_training_room():
    """
    示例 1: ROCO 训练室独处 (12 秒, 独处镜头, 公开 brief 中的经典 case).

    公开 5 支柱 (基于 brief 原文翻译):
    - WHAT     : 再完成一次干净攻击 (在 JAX/REIN 进门前)
    - OBSTACLE : 右臂水晶失控, 蓄第二次就抽筋
    - COST     : 被发现, 整组行动降级
    - STRATEGY : 装轻松, 实际动作拆小
    - TURN     : 门被推开的声音
    """
    pillars = build_5_pillars(
        goal="在 JAX 和 REIN 推门前, 再完成一次干净攻击",
        obstacle="右臂的水晶不听使唤, 第二次蓄力就抽筋, 攻击半径变窄",
        cost="如果被发现在失控, 整组行动要降级, 他从 leader 退到 follower",
        strategy="把动作拆小, 表面上还在训练, 实际上每一击都没真发力, 用节奏掩盖失力",
        turn="门被推开的声音 (JAX/REIN 进来, 他必须立刻决定要不要藏)",
    )

    action_beats = [
        (0.0, 2.0,
         "ROCO 站在训练垫中央, 双脚宽站, 胸腔进行短促浅呼吸. 水晶臂沉重地垂在身侧, "
         "把右肩压得比左肩低一个指节. 血从鼻孔流到上唇, 他没擦.",
         "再来一次。就一次。"),
        (2.0, 4.5,
         "下颌绷紧再松开, 重复两次. 血继续从上唇滑过下巴, 他还是不擦. "
         "一次缓慢眨眼, 紧接两次快速眨眼, 然后一次用力闭眼 reset.",
         "他们进来之前, 我要把它完成。"),
        (4.5, 6.0,
         "目光先落到画面中右的 5 个破碎人偶上, 停一拍, 然后抬向画面左侧的门口. "
         "眼睛比头先到门口.",
         "(门动了一下)"),
        (6.0, 8.5,
         "胸口的浅呼吸在 0.3 秒内被压下去, 下颌重新锁紧. 一次用力闭眼 reset, "
         "然后眼睛重新睁开时已经挂上一丝干涩的笑.",
         "来不及了。换个脸。"),
        (8.5, 12.0,
         "右肩被水晶臂压低, 但他在视觉上把两边肩膀拉平, 抬头看向门口. 假动作的"
         "呼吸节奏均匀, 但胸腔的真实呼吸仍重.",
         "(挂上笑) 怎么这么早."),
    ]

    actor = {
        "name": "ROCO",
        "descriptors": "@roco — bare-chested, the crystal sheathing his right arm from wrist to "
                        "shoulder, blood dried under his nose",
        "pillars": pillars,
        "emotion": "burnt out and still going (translated: jaw-set + held breath + eye-lock)",
        "blink": "default",
        "inner": pillars["inner_burn"],
        "action_beats": action_beats,
        "duration": 12.0,
        "micro_life": True,
        "micro_life_interval": 1.4,
        "hands_busy": "fists that aren't quite closing on the air",
        "hard_accent_when": 6.0,  # 门推开时手停 0.6 秒
        "eye_lead_eye": "the door at frame-left",
        "eye_lead_head": "the door at frame-left",
        "still_tension": "grip",
        "still_zone": "hands",
    }
    scene = {
        "location_id": "@loc_training_room",
        "other_chars": [],
        "line_tail": "",
    }
    return render_acting_prompt(actor, scene)


def example_jax_rein_corridor():
    """
    示例 2: JAX / REIN 在走廊边走边说 (3-4 秒 beat, 远处撞击声打断).

    公开 5 支柱:
    - WHAT     : 把战果汇报给 REIN
    - OBSTACLE : 远处训练室方向传来撞击声
    - COST     : 信息丢失 (要么被打断, 要么被错误地理解)
    - STRATEGY : 边走边说, 用步伐节奏盖过环境音
    - TURN     : 撞击声, REIN 先停拇指, 然后转头; JAX 晚半拍消失笑容
    """
    pillars = build_5_pillars(
        goal="把刚才训练的成果汇报给 REIN, 同时把对方想知道的事说清楚",
        obstacle="远处训练室方向传来撞击声, 走廊的环境底噪已经盖不住, 听者注意力在分叉",
        cost="如果听者在分神时漏掉关键信息, 后续整组行动会基于错情报做判断, 可能误伤自己人",
        strategy="边走边说, 步伐节奏固定, 用脚步和手势强行把 REIN 的注意力拉回自己脸上",
        turn="远处再次传来撞击声 (ROCO 那里), REIN 拇指先停, 然后头转向声源; JAX 晚半拍笑容消失",
    )

    action_beats = [
        (0.0, 1.5,
         "JAX 抬头看天花板灯, 手拍着自己的肚子, 说话节奏均匀, 步伐不减速. "
         "REIN 低头滑动平板, 拇指在屏幕上 0.4 秒一次, 不看 JAX.",
         "(汇报中, 听不听你)"),
        (1.5, 3.0,
         "REIN 的拇指先停在屏幕上 (比转头早 0.4 秒), 头向画面左侧的远处转过去. "
         "JAX 脸上的笑容晚半秒消失, 拍肚子的手也停了一拍.",
         "(什么声音。)"),
        (3.0, 4.0,
         "REIN 拇指重新落在屏幕, 但已经换成 0.8 秒一次, 比之前慢一倍. "
         "JAX 的脚步节奏没变, 但肩线上提 0.5cm.",
         "(不是训练室那层. 是更远。)"),
        (4.0, 5.0,
         "JAX 的手在肚子上不动了 0.6 秒, 然后才继续拍, 但节奏变快. 一次用力闭眼 reset.",
         "(ROCO 又失控了。)"),
    ]

    actor_jax = {
        "name": "JAX",
        "descriptors": "@jax — carrying two food trays, slight grin that disappears late",
        "pillars": pillars,
        "emotion": "easy on top, tight underneath (translated: shoulder rise + hand-stops + jaw-set)",
        "blink": "stutter",
        "inner": "我得让她听见, 但我的笑在塌。",
        "action_beats": action_beats,
        "duration": 5.0,
        "micro_life": True,
        "micro_life_interval": 1.2,
        "hands_busy": "tapping his own stomach in a steady rhythm",
        "hard_accent_when": 4.0,  # 手停 0.6s
        "reaction": "hand_stops_working",
        "reaction_listener": "REIN (the listener, already has tablet in left hand)",
        "still_tension": "shoulder_high",
        "still_zone": "torso",
    }
    scene = {
        "location_id": "@loc_corridor",
        "other_chars": ["REIN"],
        "line_tail": "we got three more in the bag tonight — ",
    }
    return render_acting_prompt(actor_jax, scene)


def example_villain_entrance():
    """
    示例 3: 反派登场 — 公开 brief 中的 voice / 行为档案直引.

    公开描述:
    - Voice: deep, gravelly bass-baritone; slow, calculated pacing; London street accent;
            menacing calm — he never raises his voice.
    - Behavior: 控制对话节奏, 永远不提高音量, 用停顿施压.
    """
    pillars = build_5_pillars(
        goal="用最少的词, 把在场所有人按到正确的位置",
        obstacle="他不能提高音量 (提高 = 失态 = 失去权威)",
        cost="一旦失态, 在场的人会立刻重新评估他的位置, 他从'被服从'降级到'被防备'",
        strategy="慢节奏 — 每个词之间留 0.6-0.8s, 用停顿施压, 用视线锁定离自己最远的人",
        turn="(本场戏不发生 turn, 他全控) — 但如果有人敢在他说话时动一下, "
              "他会让那个人的动停在半拍上, 视线会落到那个人身上 1.2 秒, 然后回到原位",
    )

    action_beats = [
        (0.0, 2.0,
         "反派站在画面正中偏左, 双手自然垂在身侧, 手指微微张开. 视线先落在画面最右"
         "的远端人物, 停 0.6s, 然后慢慢扫回正中.",
         "(他们都在我的节奏里。)"),
        (2.0, 4.0,
         "下颌不动, 但咬肌轻微紧了一下, 跟着松. 一次缓慢眨眼, 不重. "
         "说话时嘴的开合幅度比正常人小 30%, 像每个字都省着用.",
         "(接下来这句话, 我只说一次。)"),
        (4.0, 6.0,
         "视线从远端收回, 落到画面正中偏右的次要人物脸上, 1.2 秒不动. "
         "对方的肩线 0.3 秒后开始下塌.",
         "(你动一下试试。)"),
        (6.0, 8.0,
         "视线收回, 重新落在画面正中. 头不动, 只是眼睛回到正中. "
         "一次用力闭眼 reset, 重新睁开时眼神和之前一模一样.",
         "(回到你们的位子上。)"),
        (8.0, 12.0,
         "双手仍然垂在身侧, 手指一根一根轻轻合上, 然后又一根一根松开, 慢. "
         "这是他唯一在做的小动作, 也是整场戏最强的重音.",
         "(你们听见了。)"),
    ]

    actor_v = {
        "name": "VILLAIN",
        "descriptors": "@villain — deep, gravelly bass-baritone; slow, calculated pacing; "
                        "London street accent; menacing calm — he never raises his voice",
        "pillars": pillars,
        "emotion": "commanding (translated: jaw-set + slow blinks + finger-by-finger close)",
        "blink": "default",
        "inner": pillars["inner_burn"],
        "action_beats": action_beats,
        "duration": 12.0,
        "micro_life": True,
        "micro_life_interval": 1.8,
        "hands_busy": "fingers closing one by one, then opening one by one — the only motion",
        "hard_accent_when": 8.0,  # 手指合上的那一刻
        "eye_lead_eye": "the secondary character at center-right",
        "eye_lead_head": "(head does not move — eye only)",
        "still_tension": "muscle_quiver",
        "still_zone": "full",
    }
    scene = {
        "location_id": "@loc_throne_room_or_office",
        "other_chars": ["henchman_A", "henchman_B", "interrogator"],
        "line_tail": "",
    }
    return render_acting_prompt(actor_v, scene)


# ==============================================================================
# 13. ComfyUI 节点封装 (Node 集群标准, 跟其他 *_pro.py 保持一致)
# ==============================================================================

class ActingSkill:
    """
    🎭 Acting Skill — Higgsfield 方法论本地化节点

    本节点调用本文件 10 个核心函数 + 3 个 Hell Grind 示例,
    接受 5 支柱输入, 输出完整 CHARACTER ACTING 块.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "示例选择": (["自定义", "ROCO 训练室独处", "JAX/REIN 走廊对话", "反派登场"], {"default": "ROCO 训练室独处"}),
                # 5 支柱输入
                "WHAT_目标": ("STRING", {"default": "在 JAX 和 REIN 推门前, 再完成一次干净攻击", "multiline": False}),
                "OBSTACLE_障碍": ("STRING", {"default": "右臂的水晶不听使唤, 第二次蓄力就抽筋", "multiline": False}),
                "COST_代价": ("STRING", {"default": "被发现, 整组行动降级, 从 leader 退到 follower", "multiline": False}),
                "STRATEGY_策略": ("STRING", {"default": "把动作拆小, 装作用力, 实际每一击都没真发力", "multiline": False}),
                "TURN_新信息": ("STRING", {"default": "门被推开的声音 (JAX/REIN 进来)", "multiline": False}),
                # 角色
                "角色名": ("STRING", {"default": "ROCO", "multiline": False}),
                "角色描述符": ("STRING", {"default": "@roco — bare-chested, crystal sheathing his right arm, blood dried under his nose", "multiline": True}),
                "主情绪": (["calm", "sad", "angry", "shocked", "hesitant", "determined", "悲伤", "愤怒", "坚定", "崩溃"], {"default": "determined"}),
                # 时序
                "镜头时长_秒": ("INT", {"default": 12, "min": 2, "max": 60, "step": 1}),
                "眨眼模式": (["default", "tense", "nervous", "calm", "deciding", "reset_only", "lazy_only", "double_only"], {"default": "default"}),
                "微生命间隔_秒": ("INT", {"default": 15, "min": 10, "max": 30, "step": 1}),  # 用 10-30 表示 1.0-3.0s
                # 可选
                "手在忙什么": ("STRING", {"default": "fists that aren't quite closing on the air", "multiline": False}),
                "强重音_手停_秒": ("INT", {"default": 6, "min": 0, "max": 60, "step": 1}),
                "反应类型": (["none", "agree_but_cost", "disagree_verbal_hold", "calculate",
                              "absorb_heavy_news", "pretend_not_heard", "already_knew",
                              "half_laugh_crack", "first_real_look", "decision_lock",
                              "hand_stops_working"], {"default": "none"}),
                "静止张力": (["none", "held_breath", "rigid_neck", "weight_locked", "grip",
                              "eye_lock", "jaw_set", "shoulder_high", "posture_lock",
                              "muscle_quiver", "delayed_swallow"], {"default": "none"}),
            },
            "optional": {
                "上一句尾音": ("STRING", {"default": "", "multiline": False}),
                "对手角色": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_acting_block", "five_pillars_dict", "five_elements_driver")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/L5 导演级/Internal"

    def build(self, **kwargs):
        example = kwargs.get("示例选择", "ROCO 训练室独处")

        # 选示例: 直接返回预生成的 3 个示例之一
        if example == "ROCO 训练室独处":
            block = example_roco_training_room()
            pillars = build_5_pillars(
                "在 JAX 和 REIN 推门前, 再完成一次干净攻击",
                "右臂的水晶不听使唤, 第二次蓄力就抽筋",
                "被发现, 整组行动降级, 从 leader 退到 follower",
                "把动作拆小, 装作用力, 实际每一击都没真发力",
                "门被推开的声音 (JAX/REIN 进来)",
            )
            five = pillars["_5_elements"]
            return (block, _pillars_to_text(pillars), five)
        if example == "JAX/REIN 走廊对话":
            block = example_jax_rein_corridor()
            pillars = build_5_pillars(
                "把战果汇报给 REIN",
                "远处训练室方向传来撞击声",
                "信息丢失, 后续基于错情报做判断",
                "边走边说, 用步伐节奏盖过环境音",
                "远处再次传来撞击声",
            )
            five = pillars["_5_elements"]
            return (block, _pillars_to_text(pillars), five)
        if example == "反派登场":
            block = example_villain_entrance()
            pillars = build_5_pillars(
                "用最少的词, 把在场所有人按到正确的位置",
                "不能提高音量 (提高 = 失态 = 失去权威)",
                "失态, 从'被服从'降级到'被防备'",
                "慢节奏 — 每个词之间留 0.6-0.8s, 用停顿施压",
                "(本场不发生 turn, 全控)",
            )
            five = pillars["_5_elements"]
            return (block, _pillars_to_text(pillars), five)

        # 自定义路径
        pillars = build_5_pillars(
            kwargs.get("WHAT_目标", ""),
            kwargs.get("OBSTACLE_障碍", ""),
            kwargs.get("COST_代价", ""),
            kwargs.get("STRATEGY_策略", ""),
            kwargs.get("TURN_新信息", ""),
        )

        # 构造默认 3-beat 时间线 (用户没填时)
        duration = kwargs.get("镜头时长_秒", 12)
        action_beats = _default_beats(duration, pillars)

        actor = {
            "name": kwargs.get("角色名", "ACTOR"),
            "descriptors": kwargs.get("角色描述符", ""),
            "pillars": pillars,
            "emotion": kwargs.get("主情绪", "calm"),
            "blink": kwargs.get("眨眼模式", "default"),
            "inner": pillars["inner_burn"],
            "action_beats": action_beats,
            "duration": float(duration),
            "micro_life": True,
            "micro_life_interval": kwargs.get("微生命间隔_秒", 15) / 10.0,
            "hands_busy": kwargs.get("手在忙什么", ""),
            "hard_accent_when": kwargs.get("强重音_手停_秒", 0),
            "reaction": kwargs.get("反应类型", "none"),
            "reaction_listener": kwargs.get("对手角色", "the other character in frame"),
            "still_tension": kwargs.get("静止张力", "none"),
        }
        scene = {
            "location_id": "(see SCENE CONTEXT block)",
            "other_chars": [kwargs["对手角色"]] if kwargs.get("对手角色") else [],
            "line_tail": kwargs.get("上一句尾音", ""),
        }
        block = render_acting_prompt(actor, scene)
        return (block, _pillars_to_text(pillars), pillars["_5_elements"])


# ==============================================================================
# 14. 内部辅助函数
# ==============================================================================

def _pillars_to_text(pillars: dict) -> str:
    """把 build_5_pillars 的 dict 渲染成可读文本."""
    out = []
    out.append("=== 5 PILLARS ===")
    out.append("WHAT     : " + pillars["what"])
    out.append("OBSTACLE : " + pillars["obstacle"])
    out.append("COST     : " + pillars["cost"])
    out.append("STRATEGY : " + pillars["strategy"])
    out.append("TURN     : " + pillars["turn"])
    out.append("")
    out.append("=== OBSERVABLE ANCHORS (each pillar → a body cue) ===")
    for k, v in pillars["observable"].items():
        out.append("  " + k.upper() + " -> " + v)
    out.append("")
    out.append("=== INNER BURN ===")
    out.append(pillars["inner_burn"])
    return "\n".join(out)


def _default_beats(duration_sec: int, pillars: dict) -> list:
    """
    用户没填 action_beats 时, 根据 5 支柱 + 时长自动生成 3-beat 默认时间线.
    这是动态生成 (基于 pillars 内容), 不是模板.
    """
    d = float(duration_sec)
    third = d / 3.0
    strategy_short = (pillars.get("strategy") or "moving through the beat")[:60]
    obstacle_short = (pillars.get("obstacle") or "the load is on the body")[:60]
    return [
        (0.0, third,
         "first third — establish: the body picks a micro-load (" + obstacle_short +
         ") and holds it; eye-line is set, breath is set.",
         "INNER: " + (pillars.get("what") or "this is what I want")[:60]),
        (third, third * 2,
         "second third — " + strategy_short + "; the body answers with motion, not words.",
         "INNER: cost is real, every second counts."),
        (third * 2, d,
         "final third — a single hard reset-blink, then the body settles into the next beat.",
         "INNER: this is what I leave behind."),
    ]


# ==============================================================================
# 15. NODE_CLASS_MAPPINGS — 跟项目其他 *.py 节点一致
# ==============================================================================

# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ActingSkill": ActingSkill,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ActingSkill": "🎭 Acting Skill (Higgsfield 本地化)",
# }


# ==============================================================================
# 16. 自检 (模块加载时打印一行状态, 方便其它 agent / 节点确认)
# ==============================================================================

if __name__ == "__main__":
    print("acting_skill loaded.")
    print("5 pillars dict keys:", list(build_5_pillars("a", "b", "c", "d").keys()))
    print("translate_emotion_to_action('sad') ->", translate_emotion_to_action("sad")["muscle_cues"][:2])
    print("build_blink_sequence('tense') length:", len(build_blink_sequence("tense").splitlines()), "lines")
    print("build_eye_lead('door', 'door') -> first line:", build_eye_lead("door", "door").splitlines()[0])
    print("build_micro_life length:", len(build_micro_life().splitlines()), "lines")
    print("build_reaction_chain('JAX', 'absorb_heavy_news') -> first line:", build_reaction_chain("JAX", "absorb_heavy_news").splitlines()[0])
    print("act_no_motion_but_tension('held_breath') -> first line:", act_no_motion_but_tension("held_breath").splitlines()[0])
    print("example_roco_training_room length:", len(example_roco_training_room()), "chars")
    print("example_jax_rein_corridor length:", len(example_jax_rein_corridor()), "chars")
    print("example_villain_entrance length:", len(example_villain_entrance()), "chars")
