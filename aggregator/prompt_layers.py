# -*- coding: utf-8 -*-
"""
aggregator/prompt_layers.py — L1-L7 七层结构化提示词架构
=====================================================
迁移自 Octopus DataVerse 7.3 (DirectorPrompt 模型).

每镜7层结构化提示词 — 世界顶级导演的核心能力:
  L1 意图层: 导演想表达什么 (情感/叙事目的/观众应感到)
  L2 资产层: 谁在画面里 (角色/道具/环境/服装)
  L3 空间层: 谁在哪里 (空间布局/轴线规则/光源方向/地标)
  L4 表演层: 角色在做什么 (动作/微表情/身体语言/潜文本)
  L5 运镜层: 怎么拍 (景别/角度/运镜/焦段/构图)
  L6 风格层: 什么质感 (色彩/光影/材质/氛围/节奏)
  L7 约束层: 什么不能做 (反AI/时长/画幅/一致性)

还有: 节拍表(beat_table)、张力曲线(tension_curve)、角色弧追踪(arc_tracking)
"""
import json as _json
import hashlib as _hashlib

# ============================================================
# L1-L7 七层提示词生成
# ============================================================
def build_layered_prompt(shot, director, scene, mood, intent, core_pack=None):
    """为单个镜头生成 L1-L7 七层结构化提示词.

    shot: 分镜表中的一镜 (含 stage/size/angle/move/focal/focus/sound/cut/purpose
          + stage_color/stage_light/stage_material/stage_atmosphere/stage_emotion/stage_rhythm)
    返回: dict (L1-L7 七层) + rendered_text (可送视频模型的渲染文本)
    """
    n = shot.get("n", 1)
    stage = shot.get("stage", "建立")
    stage_name = shot.get("stage_name", stage)

    # L1 意图层
    l1 = {
        "shot_id": n,
        "story_stage": stage,
        "type_stage": stage_name,
        "narrative_purpose": shot.get("purpose", "建立空间"),
        "director_intent": intent or "",
        "emotion_target": shot.get("stage_emotion", ""),
        "audience_should_feel": intent,
        "design_note": shot.get("note", ""),
    }

    # L2 资产层
    l2 = {
        "characters": [],  # 从场景描述提取
        "props": [],  # 从场景描述提取
        "environment": scene,
        "costume": "",  # 从Asset节点输入
        "key_focus_object": shot.get("focus", ""),
    }
    if core_pack:
        l2["characters"] = core_pack.get("_角色", [])
        l2["props"] = core_pack.get("_道具", [])
        l2["director_style"] = core_pack.get("_导演风格", director)

    # L3 空间层
    l3 = {
        "spatial_layout": "",  # 空间布局 (角色/道具/相机位置)
        "axis_rule": f"180度轴线: 相机在{stage}阶段保持在画面的{('左侧' if n % 2 == 0 else '右侧')}, 不越轴",
        "lighting_direction": shot.get("stage_light", ""),
        "landmarks": [],  # 地标
        "camera_position": f"机位: {shot.get('angle', '平视')} {shot.get('size', '中景')}距离",
    }

    # L4 表演层
    l4 = {
        "action": shot.get("focus", ""),  # 角色在做什么
        "micro_expression": shot.get("stage_emotion", ""),  # 微表情
        "body_language": "",  # 身体语言
        "subtext": "",  # 潜文本
        "breath_pattern": "正常" if stage in ["建立", "收束"] else "急促" if stage in ["转折", "高潮"] else "渐紧",
    }

    # L5 运镜层
    l5 = {
        "shot_size": shot.get("size", ""),
        "angle": shot.get("angle", ""),
        "camera_move": shot.get("move", ""),
        "focal_length": shot.get("focal", ""),
        "composition": "",  # 构图
        "duration_sec": shot.get("dur", "3.0s"),
        "cut_type": shot.get("cut", ""),
        "transition": shot.get("cut", ""),
    }

    # L6 风格层
    l6 = {
        "color": shot.get("stage_color", ""),
        "light": shot.get("stage_light", ""),
        "material": shot.get("stage_material", ""),
        "atmosphere": shot.get("stage_atmosphere", ""),
        "rhythm": shot.get("stage_rhythm", ""),
        "director_style": director,
        "sound": shot.get("sound", ""),
    }

    # L7 约束层
    l7 = {
        "anti_ai": "禁用: masterpiece/best quality/ultra detailed/stunning/breathtaking/cinematic lighting/4K/8K/HDR/photorealistic",
        "duration_limit": shot.get("dur", "3.0s"),
        "aspect_ratio": "16:9",
        "consistency": "角色/服装/环境跨镜头一致 (IP-Adapter锚定)",
        "spatial_consistency": "空间不变(同场景), 信息变化(新动作/新情绪)",
    }

    # 渲染文本 (可送视频模型)
    rendered = (
        f"[Shot {n}] {stage}({stage_name}) | {shot.get('purpose','')}\n"
        f"L1意图: {intent} | 情绪:{l1['emotion_target']}\n"
        f"L2资产: 焦点={l2['key_focus_object']} | 导演={director}\n"
        f"L3空间: {l3['axis_rule']} | 光源:{l3['lighting_direction']}\n"
        f"L4表演: {l4['action']} | 微表情:{l4['micro_expression']} | 呼吸:{l4['breath_pattern']}\n"
        f"L5运镜: {l5['shot_size']} {l5['angle']} {l5['camera_move']} {l5['focal_length']} {l5['duration_sec']}\n"
        f"L6风格: 色彩:{l6['color']} | 光影:{l6['light']} | 材质:{l6['material']} | 氛围:{l6['atmosphere']}\n"
        f"L7约束: {l7['anti_ai']} | {l7['consistency']}"
    )

    return {
        "shot_id": n, "l1_intent": l1, "l2_assets": l2, "l3_spatial": l3,
        "l4_performance": l4, "l5_camera": l5, "l6_style": l6, "l7_constraints": l7,
        "rendered_text": rendered,
    }


def build_all_layered_prompts(shots, director, scene, mood, intent, core_pack=None):
    """为全部分镜生成 L1-L7 七层提示词."""
    return [build_layered_prompt(s, director, scene, mood, intent, core_pack) for s in shots]


def format_layered_prompts_text(layered_prompts):
    """格式化 L1-L7 为可读文本."""
    lines = ["【L1-L7 七层结构化提示词 (迁移自Octopus DataVerse 7.3)】"]
    for lp in layered_prompts:
        lines.append("")
        lines.append(lp["rendered_text"])
    return "\n".join(lines)


# ============================================================
# 节拍表 (Beat Table) — 每个节拍的时间/情绪/信息量
# ============================================================
def build_beat_table(scene, director, mood, total_dur=30):
    """生成节拍表 — 每个节拍有时间点/情绪强度/信息量/叙事功能."""
    from aggregator.scene_engine import STORY_STAGES, STAGE_ORDER, get_stage_for_shot
    beats = []
    beat_count = 6  # 6拍
    per = total_dur / beat_count
    t0 = 0.0
    for i in range(beat_count):
        stage = get_stage_for_shot(i, beat_count)
        stage_info = STORY_STAGES.get(stage, STORY_STAGES["建立"])
        intensity = i / (beat_count - 1) if beat_count > 1 else 0  # 0→1 张力递增
        beats.append({
            "beat": i + 1,
            "in_sec": round(t0, 1),
            "out_sec": round(t0 + per, 1),
            "stage": stage,
            "emotion": stage_info["emotion"],
            "intensity": round(intensity, 2),  # 0.0=最弱, 1.0=最强
            "info_density": "低" if i < 2 else "中" if i < 4 else "高" if i < 5 else "低",
            "narrative_function": stage_info["desc"],
        })
        t0 += per
    return beats


def format_beat_table_text(beats):
    """格式化节拍表为可读文本. V14.3 E1: 入点/出点 1 位小数 + 宽列, 长片大秒数不粘连."""
    lines = ["【节拍表 Beat Table】", f"{'拍':<4}{'入点(s)':<10}{'出点(s)':<10}{'阶段':<5}{'情绪':<12}{'强度':<5}{'信息量':<5}{'叙事功能'}"]
    lines.append("─" * 80)
    for b in beats:
        try:
            in_s = f"{float(b['in_sec']):.1f}"
        except Exception:
            in_s = str(b['in_sec'])
        try:
            out_s = f"{float(b['out_sec']):.1f}"
        except Exception:
            out_s = str(b['out_sec'])
        lines.append(f"{b['beat']:<4}{in_s:<10}{out_s:<10}{b['stage']:<5}{b['emotion']:<12}{b['intensity']:<5}{b['info_density']:<5}{b['narrative_function']}")
    lines.append("─" * 80)
    return "\n".join(lines)


# ============================================================
# 张力曲线 (Tension Curve) — 全片情绪强度随时间变化
# ============================================================
def build_tension_curve(total_dur=30, beat_count=6):
    """生成张力曲线 — 全片情绪强度随时间的变化曲线."""
    from aggregator.scene_engine import STAGE_ORDER
    curve = []
    for i in range(beat_count):
        t = i / (beat_count - 1) if beat_count > 1 else 0
        stage_idx = min(int(i * 5 / beat_count), 4)
        stage = STAGE_ORDER[stage_idx]
        # 张力: 建立0.2 → 铺垫0.4 → 转折0.7 → 高潮1.0 → 收束0.3
        tension_map = {"建立": 0.2, "铺垫": 0.4, "转折": 0.7, "高潮": 1.0, "收束": 0.3}
        curve.append({
            "time_sec": round(t * total_dur, 1),
            "tension": tension_map.get(stage, 0.5),
            "stage": stage,
        })
    return curve


def format_tension_curve_text(curve):
    """格式化张力曲线."""
    lines = ["【张力曲线 Tension Curve】"]
    for c in curve:
        bar = "█" * int(c["tension"] * 20)
        lines.append(f"  {c['time_sec']:>5}s | {c['stage']:<5} | {c['tension']:.1f} {bar}")
    return "\n".join(lines)


# ============================================================
# 角色弧追踪 (Arc Tracking) — 每场角色状态变化
# ============================================================
def build_arc_tracking(characters, mood):
    """生成角色弧追踪 — 每个角色在各阶段的状态变化."""
    from aggregator.scene_engine import STAGE_ORDER
    arcs = {}
    for char in characters[:3]:  # 最多3个角色
        name = char if isinstance(char, str) else char.get("name", "角色")
        stages = []
        for stage in STAGE_ORDER:
            state_map = {
                "建立": "初始状态(未变化)",
                "铺垫": "开始动摇/察觉",
                "转折": "关键变化(被击中)",
                "高潮": "情感/行动的最高点",
                "收束": "新状态(成长/释然)",
            }
            stages.append({"stage": stage, "state": state_map.get(stage, "")})
        arcs[name] = stages
    return arcs


def format_arc_tracking_text(arcs):
    """格式化角色弧追踪."""
    lines = ["【角色弧追踪 Arc Tracking】"]
    for name, stages in arcs.items():
        lines.append(f"  {name}:")
        for s in stages:
            lines.append(f"    {s['stage']}: {s['state']}")
    return "\n".join(lines)
