# -*- coding: utf-8 -*-
"""
aggregator/pro_format.py — 专业影视格式引擎
=============================================
按真实剧本/分镜标准格式输出, 摒弃装饰符堆砌.

参考: 真实电影剧本格式(场景头 INT./EXT. + 动作行 + 角色cue + 对白 + 转场)
      真实分镜表(镜号/景别/角度/运镜/焦段/时长/画面焦点/声音/转场/叙事目的)
      分镜原则: 一个镜头只做一件事(五选一), 镜头B回答镜头A的"然后呢",
              切镜=空间不变信息变化, 景别决定观众离事情多远.
"""
import re as _re

# ============================================================
# 镜头词汇表 (来自真实分镜理论)
# ============================================================
SHOT_SIZE = {  # 景别 — 决定观众离这件事多远
    "大远景": "建立世界/时间/氛围, 角色小到看不清脸",
    "全景": "交代人物与空间关系, 角色在空间中的位置",
    "中景": "推进叙事, 膝盖以上, 兼顾肢体+表情",
    "近景": "展示情绪, 胸部以上, 他在想什么",
    "特写": "钉死一个细节, 一只手/一个眼神/一个物件",
    "大特写": "极度强调, 极小局部(瞳孔/嘴唇)",
}
ANGLE = {  # 角度 — 决定观众从什么位置看
    "平视": "客观叙述, 摄像机与角色视线同高, 旁观者",
    "仰拍": "制造压迫感/崇高感, 角色强大",
    "俯拍": "角色脆弱/孤立/被困住",
    "倾斜": "打破水平, 触发失衡/危机/不安",
    "过肩": "对话正反打, 带入一方视角",
}
MOVE = {  # 运镜 — 决定视线静止还是流动
    "固定": "信息全在画面里, 零认知成本, 自己找",
    "推": "注意, 这个东西最重要, 排除其他干扰",
    "拉": "退一步, 看这个人的处境/空间关系",
    "摇": "横向扫视, 建立空间全貌",
    "跟拍": "跟着这个人, 别走散, 身体同步感",
    "升降": "垂直运动, 揭示/建立规模",
    "环绕": "围绕角色转, 立体感/被注视感",
}
FOCAL = {  # 焦段 — 决定空间压缩还是拉伸
    "广角14-24mm": "空间开阔, 强调疏离/环境, 前景背景距离拉大",
    "标准35-50mm": "接近人眼, 在场感, 不变形",
    "长焦85-200mm": "空间扁平, 压迫/亲密/被监视感",
}
COMPOSITION = {  # 构图 — 视觉权重分配
    "中心": "这是唯一重要的东西, 其他是背景",
    "三分法": "注意这个, 也别忽略环境",
    "引导线": "顺着这个方向看, 终点有重要东西",
    "负空间": "这个人的世界很空/孤独/即将被闯入",
    "前景遮挡": "有人在暗中观察/角色被什么困住",
    "框中框": "窥视/层次/电影感",
}
CUT = {  # 转场
    "硬切": "信息直接跳转, 节奏快",
    "匹配剪辑": "动作/形状衔接, 流畅过渡",
    "跳切": "同空间时间跳跃, 打破连续",
    "叠化": "时间流逝/记忆",
    "淡入淡出": "段落分隔/情绪留白",
    "J-cut/L-cut": "声音先于/滞后画面, 情绪前置",
}
NARR_PURPOSE = [  # 一个镜头只做一件事 — 五选一
    "建立空间", "展示情绪", "推进动作", "给出反应", "交代因果关系",
]


def strip_decor(s):
    """去除装饰符 (═══/###/=== 等长串重复符号), 保留内容."""
    if not s:
        return s
    # 去除纯符号行 (>=10个重复符号)
    s = _re.sub(r'^[═#=*\-~▔▁─━┅┄]+\s*$', '', s, flags=_re.MULTILINE)
    # 去除行内长串装饰符 (>=15个)
    s = _re.sub(r'[═]{15,}', '', s)
    s = _re.sub(r'[#]{15,}', '', s)
    s = _re.sub(r'[=]{15,}', '', s)
    # 合并多余空行 (>=3连续→2)
    s = _re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def strip_director_block(s):
    """去除重复的'导演风格锚定'块 (Final汇总时只保留1次)."""
    if not s:
        return s
    # 从 【导演风格锚定 到 5维标签 行(含)整块移除 (跨空白行)
    s = _re.sub(r'【导演风格锚定[\s\S]*?5维标签[^\n]*\n?', '', s)
    s = strip_decor(s)
    return s.strip()


# ============================================================
# 真实剧本格式
# ============================================================
def format_screenplay(title, director, mood, intent, scenes, subtext_strength="强"):
    """专业剧本格式.

    scenes: list of dict:
      {heading: "INT. 厨房 - 夜 - 雨", action: "...", dialogues: [(角色, 括号说明, 对白), ...], transition: "CUT TO:"}
    subtext_strength: V13.3 潜文本强度 — 控制〔潜文本〕行渲染频率.
    """
    # 潜文本渲染频率 (按强度)
    _ss = subtext_strength or "强"
    if "零" in _ss or "无" in _ss:
        _subtext_every = 0  # 不渲染
    elif "弱" in _ss:
        _subtext_every = 4
    elif "中" in _ss:
        _subtext_every = 2
    else:  # 强/极强
        _subtext_every = 1
    lines = []
    lines.append(f"《{title}》")
    lines.append(f"导演: {director}  |  情绪基调: {mood}  |  观众应感到: {intent}")
    lines.append("")
    lines.append("─" * 40)
    lines.append("")
    for _si, sc in enumerate(scenes):
        lines.append(sc.get("heading", ""))
        lines.append("")
        action = sc.get("action", "").strip()
        if action:
            lines.append(action)
            lines.append("")
        for role, paren, line in sc.get("dialogues", []):
            lines.append(f"            {role}")
            if paren:
                lines.append(f"          ({paren})")
            lines.append(f"        {line}")
            lines.append("")
        # V13.3: 渲染潜文本 — 按强度控制频率 (此前 subtext 字段被丢弃)
        subtext = (sc.get("subtext") or "").strip()
        if subtext and _subtext_every > 0 and (_si % _subtext_every == 0):
            lines.append(f"    〔潜文本: {subtext}〕")
            lines.append("")
        if sc.get("transition"):
            lines.append(sc["transition"])
            lines.append("")
    return "\n".join(lines)


# ============================================================
# 真实分镜表格式
# ============================================================
def format_shot_table(director, mood, shots):
    """专业分镜表格式 (含故事弧递进: 每镜有阶段/色彩/光影/材质/氛围/情绪).

    shots: list of dict:
      {n:镜号, stage:故事阶段, stage_name:类型适配阶段名, size:景别, angle:角度,
       move:运镜, focal:焦段, dur:时长, focus:画面焦点, sound:声音, cut:转场,
       purpose:叙事目的, note:设计说明,
       stage_emotion, stage_color, stage_light, stage_material, stage_atmosphere, stage_rhythm}

    V14.2 格式修复: 画面焦点(68-111字)/声音(24字) 超出固定列宽会撑破整行布局,
    改为 短表头行 + 标签子行 (焦点/声音/色彩/光影/材质/氛围/情绪/转场/设计),
    人读对齐 + 机器可解析 (format_export.parse_shot_table 逐镜还原)。
    """
    from aggregator.scene_engine import detect_story_line_type
    story_line = detect_story_line_type(detect_scene_type_local(shots), len(shots))
    lines = []
    lines.append(f"分镜表  |  导演: {director}  |  情绪: {mood}  |  故事线: {story_line}  |  原则: 一个镜头只做一件事, 镜B回答镜A的'然后呢'")
    lines.append(f"故事弧: 建立→铺垫→转折→高潮→收束 (色彩/光影/材质/氛围/声音/节奏随情节递进变化, 非随机)")
    lines.append("")
    # 表头 (短列对齐; 长字段放标签子行)
    lines.append(f"{'镜号':<5}{'阶段':<6}{'类型阶段':<8}{'景别':<7}{'运镜':<8}{'焦段':<8}{'时长':<8}")
    lines.append("─" * 60)
    for s in shots:
        lines.append(
            f"{str(s.get('n','')):<5}{str(s.get('stage','')):<6}{str(s.get('stage_name','')):<8}"
            f"{str(s.get('size','')):<7}{str(s.get('move','')):<8}{str(s.get('focal','')):<8}"
            f"{str(s.get('dur','')):<8}"
        )
        if s.get("focus"):
            lines.append(f"    焦点: {s['focus']}")
        _style_parts = []
        if s.get("sound"):
            _style_parts.append(f"声音: {s['sound']}")
        if s.get("stage_color"):
            _style_parts.append(f"色彩: {s['stage_color']}")
        if s.get("stage_light"):
            _style_parts.append(f"光影: {s['stage_light']}")
        if s.get("stage_material"):
            _style_parts.append(f"材质: {s['stage_material']}")
        if s.get("stage_atmosphere"):
            _style_parts.append(f"氛围: {s['stage_atmosphere']}")
        if s.get("stage_emotion"):
            _style_parts.append(f"情绪: {s['stage_emotion']}")
        if s.get("cut"):
            _style_parts.append(f"转场: {s['cut']}")
        if _style_parts:
            lines.append("    " + " | ".join(_style_parts))
        if s.get("note"):
            lines.append(f"    设计: {s['note']}")
    lines.append("─" * 60)
    return "\n".join(lines)


def detect_scene_type_local(shots):
    """从shots推断场景类型 (用于分镜表标题)."""
    if not shots:
        return "日常室内"
    # 简单: 从第一镜的focus推断
    focus = shots[0].get("focus", "")
    if any(k in focus for k in ["出拳","搏击","拳","打"]): return "搏击打斗"
    if any(k in focus for k in ["驾","车","追","引擎"]): return "追车追击"
    if any(k in focus for k in ["全景","天地","大军","恢弘"]): return "恢弘大场景"
    if any(k in focus for k in ["眼角","泪","微表情","呼吸"]): return "微表情情绪"
    if any(k in focus for k in ["舞","灯光","pose"]): return "MV歌舞"
    if any(k in focus for k in ["暗处","异响","警觉"]): return "恐怖悬疑"
    if any(k in focus for k in ["相拥","靠近","对视"]): return "爱情浪漫"
    return "日常室内"


# ============================================================
# 动态场景生成 (委托 scene_engine, 不再硬编码)
# ============================================================
def build_standard_screenplay_scenes(scene, director, mood, intent="", target_minutes=120, story_theory="三幕剧", mood_arc=None, dial_override=None, mode_seed="", scene_target=None):
    """动态生成剧本场次 — V12.6 v9: 按 target_minutes 决定长/中/短片.
    target_minutes:
        >= 110 → 35 场戏 (120min 电影)
        >= 80  → 26 场戏 (90min 电影)
        >= 50  → 18 场戏 (60min 短片/网剧)
        >= 20  → 9 场戏 (30min 短片)
        <  20  → 5 场戏 (5-15min 短视频)
    mood_arc: V13.2 情绪演变弧 (list), 按叙事进度推进场次情绪.
    dial_override: V13.3 对白密度覆盖 (none/low/mid/high).
    scene_target: V14.3 D2 — 形态模式骨架场数覆盖 (形态结构真实下场).
    """
    from aggregator.scene_engine import parse_scene, generate_screenplay_scenes
    from aggregator.feature_film_engine import generate_feature_scenes
    parsed = parse_scene(scene)
    # V14.2 修复 (FORMAT_DURATION_MAP <20min 失效): 全时长光谱 (5s-180min) 统一走长片生成器 —
    #   此前 <20min 落到 scene_engine.generate_screenplay_scenes (不接收时长), 导致
    #   Vlog/绘本/MV/短视频 等 13 个形态模式全部输出相同 3 场。feature engine 已支持短时长。
    try:
        feature_scenes = generate_feature_scenes(parsed, director, mood, intent, target_minutes, story_theory,
                                                 mood_arc=mood_arc, dial_override=dial_override, mode_seed=mode_seed,
                                                 scene_target=scene_target)
        # 转换为 format_screenplay 期望的 dict 结构
        return [_feature_scene_to_screenplay(s) for s in feature_scenes]
    except Exception:
        return generate_screenplay_scenes(parsed, director, mood, intent)


def _feature_scene_to_screenplay(s):
    """把长片场次 dict 转为 format_screenplay 期望的 dict."""
    return {
        "heading": s["heading"],
        "action": s["action"],
        "dialogues": s.get("dialogues", []),
        "transition": s.get("transition", "CUT TO:"),
        "scene_num": s.get("scene_num", 0),
        "act": s.get("act", 0),
        "story_function": s.get("story_function", ""),
        "tension_level": s.get("tension_level", 5),
        "duration_min": s.get("duration_min", 0),
        "shots_target": s.get("shots_target", 0),
        "location": s.get("location", ""),
        "objects": s.get("objects", []),
        "subtext": s.get("subtext", ""),
        "obj_carrying": s.get("obj_carrying", ""),
    }


def build_standard_shots(scene, director, mood, total_dur=120, target_minutes=120, story_theory="三幕剧", pacing_mode="auto", density_scale=1.0, mode_seed=""):
    """动态生成分镜表 — V12.6 v9: 按 target_minutes 决定长/中/短片.
    target_minutes:
        >= 110 → ~280 镜 (120min 电影)
        >= 80  → ~210 镜 (90min 电影)
        >= 50  → ~145 镜 (60min 短片)
        >= 20  → ~70 镜 (30min 短片)
        <  20  → ~35 镜 (5-15min 短视频)
    pacing_mode: V14.2 — 节奏风格 (PACING_STYLES 键), "auto"=按场次自动选; 指定则全场用该节奏.
    density_scale: V14.2 — 镜头密度倍率 (模式 dur_scale), >1 少镜 <1 多镜, 总时长不变.
    mode_seed: V14.2 — 模式名种子, 同密度模式据此差异化模板选择.
    """
    from aggregator.scene_engine import parse_scene, generate_shots
    from aggregator.feature_film_engine import generate_feature_scenes, generate_feature_shots
    parsed = parse_scene(scene)
    # V14.3 (红队P1修复): 全时长光谱统一走长片生成器 — 此前 <20min 落到 generate_shots,
    #   pacing_mode/density_scale/mode_seed/story_theory 全部被丢弃 (节奏风格对短视频装饰性)。
    #   feature engine 自 V14.2 起支持短时长 (get_beat_map 覆盖 5s-180min)。
    try:
        feature_scenes = generate_feature_scenes(parsed, director, mood, "", target_minutes, story_theory)
        return generate_feature_shots(feature_scenes, target_minutes, director, mood, pacing_mode=pacing_mode,
                                      density_scale=density_scale, mode_seed=mode_seed)
    except Exception:
        return generate_shots(parsed, director, mood, total_dur)
