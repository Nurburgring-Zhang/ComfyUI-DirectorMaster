# -*- coding: utf-8 -*-
"""
QualityAssurancePro - 质量QA专家节点
====================================================
质量 QA (环节 34) — 6 维质量评分 + 严格度分级 + 故障归因 + 反 AI 扫描

核心能力:
1. 6 维质量评分系统 (身份/空间/表演/物理/视觉/音频)
2. 评分引擎 (关键词启发式: 0-absent / 1-mentioned / 2-detailed / 3-excellent)
3. 决策矩阵 (Pass/Fix/Iterate/Discard + 严格度阈值)
4. 故障归因映射 (症状 -> 责任层 L1-L7 -> 修复建议)
5. 反 AI 词表扫描 + 自动替换建议
6. 按严格度分级的阈值系统
"""

import os
import sys
import json
import re

# === 导演数据中枢 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile, SCENE_DATABASE_100, QUOTES_30,
        get_director, get_scene,
    )
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False

# === 反 AI 词表 ===
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import (
        DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5, SILENCE_MASTERY_5,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
        ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
        SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
        build_h3_three_fields, select_camera_motion, format_shot_motion,
        build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
        inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
        inject_silence_mastery_5, inject_5_elements, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)

# === 灵魂注入 ===
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# QA 专业常量
# ============================================================

GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]


# --- 6 维质量评分系统 ---
QUALITY_DIMENSIONS_6D = {
    "D1_Identity": {
        "cn": "身份 (Identity)",
        "description": "角色是否可辨识? 服装正确? 面部稳定? 体型比例?",
        "check_items": [
            {"id": "D1_01", "name": "角色辨识度", "keywords": ["face", "character", "identity", "角色", "人物", "身份", "Soul ID"], "weight": 1.0},
            {"id": "D1_02", "name": "服装一致性", "keywords": ["costume", "outfit", "clothing", "dress", "服装", "衣服", "穿着"], "weight": 0.9},
            {"id": "D1_03", "name": "面部稳定性", "keywords": ["face stable", "face consistent", "facial", "面部", "五官", "表情一致"], "weight": 1.0},
            {"id": "D1_04", "name": "体型比例", "keywords": ["proportion", "body", "height", "体型", "比例", "身材"], "weight": 0.8},
            {"id": "D1_05", "name": "发型/配饰", "keywords": ["hair", "accessory", "glasses", "hat", "发型", "配饰", "眼镜"], "weight": 0.7},
            {"id": "D1_06", "name": "角色特征标记", "keywords": ["scar", "tattoo", "marking", "特征", "标记", "疤痕", "纹身"], "weight": 0.6},
        ],
    },
    "D2_Spatial": {
        "cn": "空间 (Spatial)",
        "description": "位置匹配 GEO MAP? 180 度规则? 比例一致? 景深正确?",
        "check_items": [
            {"id": "D2_01", "name": "180 度规则", "keywords": ["180 degree", "axis", "screen direction", "轴线", "180度", "方向一致"], "weight": 1.0},
            {"id": "D2_02", "name": "位置匹配 GEO MAP", "keywords": ["position", "location", "GEO MAP", "位置", "地图", "布局"], "weight": 1.0},
            {"id": "D2_03", "name": "比例一致性", "keywords": ["scale", "size consistent", "比例", "大小", "尺寸一致"], "weight": 0.9},
            {"id": "D2_04", "name": "景深正确性", "keywords": ["depth", "foreground", "background", "景深", "前景", "背景", "纵深"], "weight": 0.8},
            {"id": "D2_05", "name": "视线匹配", "keywords": ["eyeline", "gaze", "look at", "视线", "目光", "看向"], "weight": 0.9},
            {"id": "D2_06", "name": "空间连续性", "keywords": ["continuity", "spatial", "transition", "连续", "空间过渡", "场景衔接"], "weight": 0.8},
            {"id": "D2_07", "name": "透视正确性", "keywords": ["perspective", "vanishing point", "透视", "消失点", "灭点"], "weight": 0.7},
        ],
    },
    "D3_Performance": {
        "cn": "表演 (Performance)",
        "description": "动作匹配剧本? 时机正确? 情绪可读? 姿态自然?",
        "check_items": [
            {"id": "D3_01", "name": "动作匹配剧本", "keywords": ["action", "movement", "gesture", "动作", "动态", "手势", "表演"], "weight": 1.0},
            {"id": "D3_02", "name": "时机正确", "keywords": ["timing", "beat", "rhythm", "节拍", "时机", "节奏"], "weight": 0.9},
            {"id": "D3_03", "name": "情绪可读性", "keywords": ["emotion", "expression", "feeling", "情绪", "表情", "情感", "心理"], "weight": 1.0},
            {"id": "D3_04", "name": "姿态自然度", "keywords": ["natural", "organic", "pose", "自然", "姿态", "体态", "放松"], "weight": 0.8},
            {"id": "D3_05", "name": "微表情/小动作", "keywords": ["micro expression", "subtle", "微表情", "小动作", "细微", "微妙"], "weight": 0.9},
            {"id": "D3_06", "name": "互动合理性", "keywords": ["interaction", "react", "response", "互动", "反应", "回应"], "weight": 0.8},
        ],
    },
    "D4_Physics": {
        "cn": "物理 (Physics)",
        "description": "重力正确? 物体交互自然? 无浮空? 材质行为?",
        "check_items": [
            {"id": "D4_01", "name": "重力表现", "keywords": ["gravity", "fall", "drop", "weight", "重力", "坠落", "落下", "重量"], "weight": 1.0},
            {"id": "D4_02", "name": "物体交互", "keywords": ["interact", "touch", "hold", "grab", "接触", "持握", "碰", "拿"], "weight": 0.9},
            {"id": "D4_03", "name": "无浮空元素", "keywords": ["float", "hover", "suspend", "浮空", "悬浮", "飘"], "weight": 1.0},
            {"id": "D4_04", "name": "材质行为", "keywords": ["material", "cloth", "fabric", "water", "材质", "布料", "液体", "质感"], "weight": 0.8},
            {"id": "D4_05", "name": "碰撞检测", "keywords": ["collision", "clip", "intersect", "穿透", "碰撞", "穿模", "重叠"], "weight": 0.9},
            {"id": "D4_06", "name": "惯性/动量", "keywords": ["inertia", "momentum", "acceleration", "惯性", "动量", "加速度"], "weight": 0.7},
            {"id": "D4_07", "name": "光影物理", "keywords": ["shadow", "reflection", "refraction", "影子", "反射", "折射"], "weight": 0.8},
        ],
    },
    "D5_Visual": {
        "cn": "视觉 (Visual)",
        "description": "分辨率足够? 无伪影? 光照一致? 色彩准确?",
        "check_items": [
            {"id": "D5_01", "name": "分辨率/清晰度", "keywords": ["resolution", "sharp", "clear", "detail", "分辨率", "清晰", "细节"], "weight": 0.9},
            {"id": "D5_02", "name": "无伪影/瑕疵", "keywords": ["artifact", "glitch", "noise", "band", "伪影", "噪点", "毛刺", "瑕疵"], "weight": 1.0},
            {"id": "D5_03", "name": "光照一致性", "keywords": ["lighting consistent", "light direction", "shadow match", "光照", "光线一致", "光方向"], "weight": 1.0},
            {"id": "D5_04", "name": "色彩准确性", "keywords": ["color accurate", "white balance", "color grade", "色彩", "白平衡", "调色", "色准"], "weight": 0.9},
            {"id": "D5_05", "name": "构图完整性", "keywords": ["composition", "framing", "crop", "构图", "取景", "裁切"], "weight": 0.8},
            {"id": "D5_06", "name": "风格一致性", "keywords": ["style consistent", "visual language", "aesthetic", "风格", "视觉语言", "美感"], "weight": 0.9},
            {"id": "D5_07", "name": "运动模糊适当", "keywords": ["motion blur", "shutter", "运动模糊", "快门"], "weight": 0.6},
        ],
    },
    "D6_Audio": {
        "cn": "音频 (Audio)",
        "description": "声音匹配角色? 声画同步? 音乐情绪对齐? 空间音频?",
        "check_items": [
            {"id": "D6_01", "name": "声音匹配角色", "keywords": ["voice match", "character voice", "tone", "声音匹配", "角色声音", "嗓音"], "weight": 1.0},
            {"id": "D6_02", "name": "声画同步", "keywords": ["sync", "lip sync", "sound sync", "同步", "口型", "声画对齐"], "weight": 1.0},
            {"id": "D6_03", "name": "音乐情绪对齐", "keywords": ["music mood", "score emotion", "soundtrack", "音乐情绪", "配乐", "BGM", "氛围"], "weight": 0.9},
            {"id": "D6_04", "name": "空间音频", "keywords": ["spatial audio", "3D sound", "surround", "panning", "空间音频", "环绕", "立体声"], "weight": 0.7},
            {"id": "D6_05", "name": "环境音自然度", "keywords": ["ambient", "foley", "environment sound", "环境音", "拟音", "自然声"], "weight": 0.8},
            {"id": "D6_06", "name": "音量平衡", "keywords": ["volume", "level", "mix", "balance", "音量", "混音", "平衡"], "weight": 0.7},
        ],
    },
}


# --- QA 维度快捷配置 ---
QA_DIMENSION_PRESETS = {
    "6维全检 (Full 6D)": ["D1_Identity", "D2_Spatial", "D3_Performance", "D4_Physics", "D5_Visual", "D6_Audio"],
    "快速3维 (Quick 3D)": ["D1_Identity", "D3_Performance", "D5_Visual"],
    "视觉专项": ["D2_Spatial", "D4_Physics", "D5_Visual"],
    "音频专项": ["D6_Audio"],
    "叙事专项": ["D1_Identity", "D3_Performance"],
    "auto": ["D1_Identity", "D2_Spatial", "D3_Performance", "D4_Physics", "D5_Visual", "D6_Audio"],
}


# --- 严格度阈值 ---
STRICTNESS_THRESHOLDS = {
    "宽松 (Lenient)": {
        "pass_threshold": 0.60,
        "fix_threshold": 0.40,
        "iterate_threshold": 0.25,
        "per_dim_floor": None,
        "zero_score_rule": "ignore",
        "fix_items_are": "suggestions",
        "description": "通过阈值 >=60%, 修复项为建议, 不强制",
    },
    "标准 (Standard)": {
        "pass_threshold": 0.75,
        "fix_threshold": 0.55,
        "iterate_threshold": 0.35,
        "per_dim_floor": None,
        "zero_score_rule": "warn",
        "fix_items_are": "requirements",
        "description": "通过阈值 >=75%, 修复项为必须项",
    },
    "严格 (Strict)": {
        "pass_threshold": 0.85,
        "fix_threshold": 0.70,
        "iterate_threshold": 0.50,
        "per_dim_floor": 0.70,
        "zero_score_rule": "flag",
        "fix_items_are": "requirements",
        "description": "通过阈值 >=85%, 任何维度 <70% 自动不通过",
    },
    "零容忍 (Zero Tolerance)": {
        "pass_threshold": 0.95,
        "fix_threshold": 0.80,
        "iterate_threshold": 0.65,
        "per_dim_floor": 0.80,
        "zero_score_rule": "auto_fail",
        "fix_items_are": "requirements",
        "description": "通过阈值 >=95%, 任何检查项为 0 分则自动不通过",
    },
    "auto": {
        "pass_threshold": 0.75,
        "fix_threshold": 0.55,
        "iterate_threshold": 0.35,
        "per_dim_floor": None,
        "zero_score_rule": "warn",
        "fix_items_are": "requirements",
        "description": "默认标准模式",
    },
}


# --- 故障归因映射 (症状 -> 责任层 -> 修复建议) ---
FAILURE_ATTRIBUTION_MAP = [
    # (症状关键词, 责任层, 层名, 修复建议)
    ("character face changed", "L2", "Assets 资产层", "添加 Soul ID reference, 锁定角色面部参数"),
    ("角色面部变化", "L2", "Assets 资产层", "添加 Soul ID reference, 锁定角色面部参数"),
    ("character wrong position", "L3", "Space 空间层", "更新 GEO MAP, 明确角色 XYZ 坐标"),
    ("角色位置错误", "L3", "Space 空间层", "更新 GEO MAP, 明确角色 XYZ 坐标"),
    ("action mismatch", "L4", "Performance 表演层", "修订 ACTION TIMING, 逐帧指定动作"),
    ("动作不匹配", "L4", "Performance 表演层", "修订 ACTION TIMING, 逐帧指定动作"),
    ("lighting inconsistent", "L6", "Audiovisual 视听层", "锁定光源方向和色温, 添加 lighting lock 指令"),
    ("光照不一致", "L6", "Audiovisual 视听层", "锁定光源方向和色温, 添加 lighting lock 指令"),
    ("costume changed", "L2", "Assets 资产层", "明确服装描述细节 (材质/颜色/款式), 每场景重申"),
    ("服装变化", "L2", "Assets 资产层", "明确服装描述细节 (材质/颜色/款式), 每场景重申"),
    ("object floating", "L4", "Performance 表演层", "添加物理约束描述 (gravity, surface contact)"),
    ("物体悬浮", "L4", "Performance 表演层", "添加物理约束描述 (gravity, surface contact)"),
    ("scale inconsistent", "L3", "Space 空间层", "在 GEO MAP 中标注物体尺寸参考比例"),
    ("比例不一致", "L3", "Space 空间层", "在 GEO MAP 中标注物体尺寸参考比例"),
    ("voice mismatch", "L6", "Audiovisual 视听层", "指定角色声音特征 (音高/语速/口音), 锁定 voice ID"),
    ("声音不匹配", "L6", "Audiovisual 视听层", "指定角色声音特征 (音高/语速/口音), 锁定 voice ID"),
    ("180 degree violation", "L3", "Space 空间层", "标注轴线位置, 指定 camera side, 禁止跨轴切换"),
    ("越轴", "L3", "Space 空间层", "标注轴线位置, 指定 camera side, 禁止跨轴切换"),
    ("emotion unreadable", "L4", "Performance 表演层", "明确情绪标签 + 微表情指令 (眉间距/嘴角/瞳孔)"),
    ("情绪不可读", "L4", "Performance 表演层", "明确情绪标签 + 微表情指令 (眉间距/嘴角/瞳孔)"),
    ("artifact visible", "L7", "Technical 技术层", "提高渲染参数/降噪/后处理, 检查模型限制"),
    ("伪影可见", "L7", "Technical 技术层", "提高渲染参数/降噪/后处理, 检查模型限制"),
    ("lip sync off", "L6", "Audiovisual 视听层", "对齐 dialogue timing 与画面, 标注每句话的起止时间"),
    ("口型不同步", "L6", "Audiovisual 视听层", "对齐 dialogue timing 与画面, 标注每句话的起止时间"),
    ("color shift between shots", "L5", "Visual 视觉层", "锁定 LUT/调色参数, 场景间保持 color grading 一致"),
    ("镜头间色彩跳变", "L5", "Visual 视觉层", "锁定 LUT/调色参数, 场景间保持 color grading 一致"),
    ("music mood mismatch", "L6", "Audiovisual 视听层", "标注场景情绪标签, 指定 music cue 的情绪关键词"),
    ("配乐情绪不匹配", "L6", "Audiovisual 视听层", "标注场景情绪标签, 指定 music cue 的情绪关键词"),
    ("style inconsistent", "L1", "Concept 概念层", "在全局提示词开头锁定风格描述, 每场景重申"),
    ("风格不一致", "L1", "Concept 概念层", "在全局提示词开头锁定风格描述, 每场景重申"),
    ("narrative discontinuity", "L1", "Concept 概念层", "检查场景间的叙事逻辑, 确保因果链完整"),
    ("叙事不连续", "L1", "Concept 概念层", "检查场景间的叙事逻辑, 确保因果链完整"),
    ("shadow direction wrong", "L6", "Audiovisual 视听层", "明确太阳/主光方向角度, 全场一致"),
    ("阴影方向错误", "L6", "Audiovisual 视听层", "明确太阳/主光方向角度, 全场一致"),
]


def _score_check_item(check_item, text_to_scan):
    """
    对单个检查项评分 (关键词启发式):
    0 = absent (无相关提及)
    1 = mentioned (有提及但不具体)
    2 = detailed (有具体描述)
    3 = excellent (有极具体的参数/数值/专业细节)
    """
    text_lower = text_to_scan.lower()
    keywords = check_item["keywords"]
    hit_count = 0
    detailed_markers = ["具体", "specific", "exactly", "precisely", "mm", "px", "度",
                        "color:", "rgb", "hex", "#", "cm", "inch", "lux", "kelvin",
                        "f/", "iso", "fps", "bpm", "db", "hz"]

    for kw in keywords:
        if kw.lower() in text_lower:
            hit_count += 1

    if hit_count == 0:
        return 0

    # 检查详细度
    detail_hits = sum(1 for dm in detailed_markers if dm.lower() in text_lower)

    if detail_hits >= 2 and hit_count >= 2:
        return 3  # excellent
    elif hit_count >= 2 or detail_hits >= 1:
        return 2  # detailed
    else:
        return 1  # mentioned


def _score_dimension(dimension_key, dim_config, text_to_scan):
    """对单个维度打分, 返回 (得分率, 各检查项详情)"""
    check_items = dim_config["check_items"]
    total_weighted = 0.0
    earned_weighted = 0.0
    item_details = []

    for ci in check_items:
        score = _score_check_item(ci, text_to_scan)
        max_score = 3.0
        weighted_score = score * ci["weight"]
        weighted_max = max_score * ci["weight"]
        total_weighted += weighted_max
        earned_weighted += weighted_score
        item_details.append({
            "id": ci["id"],
            "name": ci["name"],
            "score": score,
            "max": 3,
            "weight": ci["weight"],
            "weighted": round(weighted_score, 2),
        })

    score_pct = (earned_weighted / total_weighted) if total_weighted > 0 else 0.0
    return round(score_pct, 4), item_details


def _run_scoring_engine(text_to_scan, active_dimensions):
    """运行全维度评分引擎"""
    results = {}
    total_score = 0.0
    total_dims = 0

    for dim_key in active_dimensions:
        dim_config = QUALITY_DIMENSIONS_6D.get(dim_key)
        if not dim_config:
            continue
        score_pct, details = _score_dimension(dim_key, dim_config, text_to_scan)
        results[dim_key] = {
            "cn": dim_config["cn"],
            "score_pct": score_pct,
            "details": details,
        }
        total_score += score_pct
        total_dims += 1

    overall = (total_score / total_dims) if total_dims > 0 else 0.0
    return overall, results


def _apply_decision_matrix(overall_score, dim_results, strictness_config):
    """应用决策矩阵, 返回 (决策, 原因, 修复列表)"""
    pass_t = strictness_config["pass_threshold"]
    fix_t = strictness_config["fix_threshold"]
    iterate_t = strictness_config["iterate_threshold"]
    per_dim_floor = strictness_config.get("per_dim_floor")
    zero_rule = strictness_config.get("zero_score_rule", "warn")

    # 检查零分项
    zero_items = []
    low_dims = []
    fix_list = []

    for dk, dv in dim_results.items():
        for item in dv["details"]:
            if item["score"] == 0:
                zero_items.append(item["id"] + " " + item["name"])
            if item["score"] <= 1:
                fix_list.append("[" + dk + "/" + item["id"] + "] " + item["name"] + " (score=" + str(item["score"]) + "/3)")
        if per_dim_floor and dv["score_pct"] < per_dim_floor:
            low_dims.append(dk + " (" + dv["cn"] + "): " + "{:.1%}".format(dv["score_pct"]) + " < " + "{:.1%}".format(per_dim_floor))

    # 零容忍规则
    if zero_rule == "auto_fail" and zero_items:
        return ("DISCARD", "零容忍模式: 发现 " + str(len(zero_items)) + " 个检查项得分为 0", fix_list, zero_items, low_dims)

    # 维度下限规则
    if low_dims:
        return ("ITERATE", "维度 " + str(len(low_dims)) + " 个低于下限 " + "{:.1%}".format(per_dim_floor), fix_list, zero_items, low_dims)

    # 整体阈值
    if overall_score >= pass_t:
        decision = "PASS"
        reason = "整体得分 " + "{:.1%}".format(overall_score) + " >= " + "{:.1%}".format(pass_t)
    elif overall_score >= fix_t:
        decision = "FIX"
        reason = "整体得分 " + "{:.1%}".format(overall_score) + " 介于 FIX 区间 [" + "{:.1%}".format(fix_t) + ", " + "{:.1%}".format(pass_t) + ")"
    elif overall_score >= iterate_t:
        decision = "ITERATE"
        reason = "整体得分 " + "{:.1%}".format(overall_score) + " 介于 ITERATE 区间 [" + "{:.1%}".format(iterate_t) + ", " + "{:.1%}".format(fix_t) + ")"
    else:
        decision = "DISCARD"
        reason = "整体得分 " + "{:.1%}".format(overall_score) + " < " + "{:.1%}".format(iterate_t)

    return (decision, reason, fix_list, zero_items, low_dims)


def _run_failure_attribution(text_to_scan):
    """运行故障归因: 扫描文本中的症状关键词, 映射到责任层"""
    findings = []
    text_lower = text_to_scan.lower()
    for symptom, layer, layer_name, fix in FAILURE_ATTRIBUTION_MAP:
        if symptom.lower() in text_lower:
            findings.append({
                "symptom": symptom,
                "layer": layer,
                "layer_name": layer_name,
                "fix": fix,
            })
    return findings


def _scan_anti_ai(text_to_scan):
    """扫描反 AI 词表违规"""
    violations = []
    try:
        if not ANTI_AI_PHRASES:
            return violations
        text_lower = text_to_scan.lower()
        for phrase, replacement in ANTI_AI_PHRASES.items():
            if phrase.lower() in text_lower:
                violations.append({
                    "phrase": phrase,
                    "replacement": replacement if replacement else "(delete)",
                })
    except Exception:
        pass
    return violations


class QualityAssurancePro:
    """
    质量QA专家节点 — 6维评分 + 严格度分级 + 故障归因 + 反AI扫描
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                # === 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                # === QA 专属字段 ===
                "QA维度": (["6维全检 (Full 6D)", "快速3维 (Quick 3D)", "视觉专项", "音频专项", "叙事专项", "auto"],
                          {"default": "auto"}),
                "严格度": (["宽松 (Lenient)", "标准 (Standard)", "严格 (Strict)", "零容忍 (Zero Tolerance)", "auto"],
                          {"default": "auto"}),
                "上游提示词": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("qualityassurancepro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_qa"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_qa(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # --- 提取输入 ---
        def _str(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "电影")
        scene = _str(kwargs.get("场景描述"), "")
        director = _str(kwargs.get("导演风格"), "是枝裕和")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        qa_dimension_preset = _str(kwargs.get("QA维度"), "auto")
        strictness_name = _str(kwargs.get("严格度"), "auto")
        upstream_prompt = _str(kwargs.get("上游提示词"), "")

        # --- auto 路由 ---
        if strictness_name == "auto":
            strictness_name = "标准 (Standard)"

        # --- 确定激活维度 ---
        active_dimensions = QA_DIMENSION_PRESETS.get(qa_dimension_preset, QA_DIMENSION_PRESETS["auto"])
        strictness_config = STRICTNESS_THRESHOLDS.get(strictness_name, STRICTNESS_THRESHOLDS["auto"])

        # --- 构造扫描文本 ---
        scan_text = upstream_prompt + " " + scene + " " + mood + " " + subtext + " " + intent_feel + " " + props + " " + ref_films

        # --- 导演数据 ---
        director_profile = {}
        if _HAS_DIRECTOR_DATA:
            director_profile = get_director(director)

        director_motion_map = {
            "塔可夫斯基": "Static Shot 长时间不动 + Push In 慢推",
            "王家卫": "Push In 慢推 + 跳切 + Step Printing",
            "诺兰": "Tracking Shot 跟拍 + 时间折叠剪辑",
            "是枝裕和": "Static Shot 静观 + Push In 缓推",
            "侯孝贤": "Static Shot 远景长镜 + 留白",
            "李沧东": "Push In 微推 + 慢节奏",
            "蔡明亮": "Static Shot 超长 + 完全不动",
            "毕赣": "Arc Shot 环绕 + 长镜头",
            "周星驰": "Quick Cut 快速切换 + 戏谑节奏",
            "Papi酱": "Static Shot 口语化",
            "Vince Gilligan": "Push In 暗调慢推",
            "大衛·芬奇": "Tracking Shot 跟拍 + 暗调",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + Push In 缓推")

        # ================================================================
        # 运行评分引擎
        # ================================================================
        overall_score, dim_results = _run_scoring_engine(scan_text, active_dimensions)

        # ================================================================
        # 应用决策矩阵
        # ================================================================
        decision, reason, fix_list, zero_items, low_dims = _apply_decision_matrix(
            overall_score, dim_results, strictness_config
        )

        # ================================================================
        # 故障归因
        # ================================================================
        failure_findings = _run_failure_attribution(scan_text)

        # ================================================================
        # 反 AI 扫描
        # ================================================================
        anti_ai_violations = []
        if anti_ai_on:
            anti_ai_violations = _scan_anti_ai(scan_text)

        # ================================================================
        # H3 三大字段 (QA 报告版)
        # ================================================================
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, 强情绪节奏",
            "短视频": "live-action, 高饱和, 直给",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        style = style_choices.get(genre, "Cinematic, live-action")

        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        shot_1 = ("a medium-wide shot establishes the scene - " + scene +
                  ". " + director_motion_pref +
                  " reveals the texture of materials and the quality of light. " +
                  "Director intent: " + intent_feel + ". " +
                  "The " + first_prop + " sits on the table, waiting to be picked up.")

        shots = [
            "[Shot 2] At 00:03.500, " + format_shot_motion("Push In", "small", "slow") + " toward the main character's face, revealing " + subtext + ". Lighting consistent with Shot 1.",
            "[Shot 3] At 00:08.000, close-up of hands holding " + first_prop + ". Static shot, hands tremble slightly. (S1) speaks with " + mood + " voice: <d>[Chinese] 吃饭吧。</d>",
            "[Shot 4] At 00:15.000, over-the-shoulder shot. " + format_shot_motion("Push In", "small", "slow") + " toward other character. Silence heavy with " + subtext + ".",
            "[Shot 5] At 00:22.000, static wide frame. Both characters silent 5-10 seconds. Director intent: " + intent_feel + ".",
            "[Shot 6] At 00:27.000, hold 3 seconds. The " + last_prop + " catches the light. End of shot.",
        ]

        soundscape = ("Rain taps against the kitchen window. Knife on cutting board has dull rhythm. " +
                      "Old radio plays 1990s Chinese song at low volume. Clock ticks. " +
                      "Father's breath audible. Fabric sounds when " + props + " shifts position.")
        music = "Sparse piano notes at slow tempo, sustained low strings gradually increasing then fading."

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # --- 灵魂注入 ---
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")
        soul_header = ""
        if _HAS_SOUL:
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_scene_weight,
                    secondary=soul_secondary,
                    fusion_mode=soul_fusion_mode,
                    scene_context=scene,
                )
                soul_header = (
                    "【灵魂核心 - 质检驱动】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        # ================================================================
        # 主输出: QA 报告
        # ================================================================
        sep = "=" * 55

        # 决策标记
        decision_emoji = {"PASS": "PASS", "FIX": "FIX", "ITERATE": "ITERATE", "DISCARD": "DISCARD"}
        decision_label = decision_emoji.get(decision, decision)

        main_output = sep + "\n"
        main_output += soul_header
        main_output += "【QualityAssurancePro】质量QA专家节点\n"
        main_output += sep + "\n\n"

        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + " - 镜头运动倾向: " + director_motion_pref + "\n"
        main_output += "【QA 模式】 维度=" + qa_dimension_preset + " | 严格度=" + strictness_name + "\n"
        main_output += "【上游提示词长度】 " + str(len(upstream_prompt)) + " 字符\n\n"

        # 决策
        main_output += sep + "\n"
        main_output += "【QA 决策】 " + decision_label + "\n"
        main_output += sep + "\n\n"
        main_output += "  整体得分: " + "{:.1%}".format(overall_score) + "\n"
        main_output += "  决策原因: " + reason + "\n"
        main_output += "  严格度说明: " + strictness_config["description"] + "\n"
        main_output += "  修复项性质: " + strictness_config["fix_items_are"] + "\n\n"

        # 决策指引
        if decision == "PASS":
            main_output += "  >> Ship as-is. 质量达标, 可直接交付.\n\n"
        elif decision == "FIX":
            main_output += "  >> Minor adjustments needed. 需要以下微调:\n"
            for fi in fix_list[:10]:
                main_output += "     - " + fi + "\n"
            main_output += "\n"
        elif decision == "ITERATE":
            main_output += "  >> Re-prompt with targeted changes. 需要修改提示词后重新生成:\n"
            for fi in fix_list[:10]:
                main_output += "     - " + fi + "\n"
            if low_dims:
                main_output += "  低于下限的维度:\n"
                for ld in low_dims:
                    main_output += "     - " + ld + "\n"
            main_output += "\n"
        else:  # DISCARD
            main_output += "  >> Start over. 质量过低, 建议重做.\n"
            main_output += "  根本原因分析:\n"
            if zero_items:
                main_output += "  零分项: " + ", ".join(zero_items[:5]) + "\n"
            if low_dims:
                for ld in low_dims:
                    main_output += "     - " + ld + "\n"
            main_output += "\n"

        # 6 维评分详情
        main_output += sep + "\n"
        main_output += "【6 维质量评分详情】\n"
        main_output += sep + "\n\n"

        for dk in active_dimensions:
            dr = dim_results.get(dk)
            if not dr:
                continue
            score_bar = "=" * int(dr["score_pct"] * 20) + "-" * (20 - int(dr["score_pct"] * 20))
            main_output += "  [" + dr["cn"] + "] " + "{:.1%}".format(dr["score_pct"]) + " [" + score_bar + "]\n"
            for item in dr["details"]:
                score_stars = "*" * item["score"] + "." * (3 - item["score"])
                main_output += "    " + item["id"] + " " + item["name"] + ": " + score_stars + " (" + str(item["score"]) + "/3, w=" + str(item["weight"]) + ")\n"
            main_output += "\n"

        # 故障归因
        if failure_findings:
            main_output += sep + "\n"
            main_output += "【故障归因 (Failure Attribution)】\n"
            main_output += sep + "\n\n"
            for ff in failure_findings:
                main_output += "  SYMPTOM: " + ff["symptom"] + "\n"
                main_output += "  LAYER: " + ff["layer"] + " (" + ff["layer_name"] + ")\n"
                main_output += "  FIX: " + ff["fix"] + "\n\n"

        # 反 AI 扫描
        if anti_ai_on:
            main_output += sep + "\n"
            main_output += "【反 AI 词表扫描】\n"
            main_output += sep + "\n\n"
            if anti_ai_violations:
                main_output += "  发现 " + str(len(anti_ai_violations)) + " 个 AI 标志词违规:\n"
                for vio in anti_ai_violations[:20]:
                    main_output += "    \"" + vio["phrase"] + "\" -> " + vio["replacement"] + "\n"
            else:
                main_output += "  未发现 AI 标志词违规.\n"
            main_output += "\n"

        # H3 三大字段
        main_output += sep + "\n"
        main_output += "H3 三大字段 (QA 通过后的标准格式)\n"
        main_output += sep + "\n\n"
        main_output += h3_prompt + "\n\n"

        # 30 秒场景单元
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice="a quiet, slightly hoarse middle-aged voice",
            dialogue="吃饭吧。", n_lines=1, director_intent=intent_feel, language="Chinese"
        )
        timeline_30s_lines = "\n".join(["  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc for (ts, te, stage, desc) in SCENE_UNIT_30S])
        main_output += sep + "\n"
        main_output += "30 秒场景单元 6 段式\n"
        main_output += sep + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        # 导演意图 5 维
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本)",
            "主题": mood,
            "留白": "想说但没说出口 - " + props + " 是没寄出的信",
        }
        intent_block = inject_director_intent(intent_5d)
        main_output += sep + "\n"
        main_output += "导演意图 5 维\n"
        main_output += sep + "\n\n"
        main_output += intent_block + "\n\n"

        # 反 AI 注入
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ================================================================
        # 第二个输出: 经验矩阵
        # ================================================================
        experience = "【QA 经验矩阵】\n\n"

        experience += "【6 维质量评分系统规范】\n"
        for dk, dv in QUALITY_DIMENSIONS_6D.items():
            experience += "  [" + dv["cn"] + "] " + dv["description"] + "\n"
            experience += "    检查项: " + str(len(dv["check_items"])) + " 个\n"
            for ci in dv["check_items"]:
                experience += "      - " + ci["id"] + " " + ci["name"] + " (w=" + str(ci["weight"]) + ")\n"
            experience += "\n"

        experience += "【严格度阈值配置】\n"
        for sk, sv in STRICTNESS_THRESHOLDS.items():
            if sk == "auto":
                continue
            experience += "  [" + sk + "] " + sv["description"] + "\n"
            experience += "    Pass>=" + "{:.0%}".format(sv["pass_threshold"])
            experience += " | Fix>=" + "{:.0%}".format(sv["fix_threshold"])
            experience += " | Iterate>=" + "{:.0%}".format(sv["iterate_threshold"])
            if sv.get("per_dim_floor"):
                experience += " | 维度下限=" + "{:.0%}".format(sv["per_dim_floor"])
            experience += " | 零分规则=" + sv["zero_score_rule"]
            experience += "\n\n"

        experience += "【故障归因映射表 (症状 -> 责任层 -> 修复)】\n"
        seen_layers = {}
        for symptom, layer, layer_name, fix in FAILURE_ATTRIBUTION_MAP:
            if layer not in seen_layers:
                seen_layers[layer] = []
            seen_layers[layer].append(symptom + " -> " + fix)
        for lk in sorted(seen_layers.keys()):
            experience += "  [" + lk + "]\n"
            for item in seen_layers[lk][:4]:
                experience += "    - " + item + "\n"
            experience += "\n"

        experience += "【20 导演集群实战经验】\n"
        for d in DIRECTORS_20:
            experience += "  - " + d + "\n"
        experience += "\n"

        experience += "【11 维导演控制能力】\n"
        experience += inject_director_control_11() + "\n"

        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # ================================================================
        # 第三个输出: AI 深度处理
        # ================================================================
        ai_deep_output = "【QA AI 深度处理】\n\n"

        ai_deep_output += "【评分引擎算法说明】\n"
        ai_deep_output += "  评分机制: 关键词启发式扫描\n"
        ai_deep_output += "  评分等级:\n"
        ai_deep_output += "    0 = absent  (无相关关键词, 完全未提及)\n"
        ai_deep_output += "    1 = mentioned  (有关键词但无具体描述)\n"
        ai_deep_output += "    2 = detailed  (有具体描述, 含参数或细节)\n"
        ai_deep_output += "    3 = excellent  (极具体: 有数值/参数/专业术语)\n"
        ai_deep_output += "  加权: 每个检查项有 weight (0.6-1.0), 高权重项对维度得分影响更大\n"
        ai_deep_output += "  聚合: 维度得分 = sum(score*weight) / sum(max_score*weight)\n"
        ai_deep_output += "  整体: 整体得分 = mean(各维度得分)\n\n"

        ai_deep_output += "【详细度标记词 (触发 score 2->3 的词)】\n"
        detail_markers = ["mm", "px", "color:", "rgb", "hex", "#", "cm", "inch", "lux",
                         "kelvin", "f/", "iso", "fps", "bpm", "db", "hz", "具体", "specific",
                         "exactly", "precisely"]
        for dm in detail_markers:
            ai_deep_output += "  - " + dm + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【决策矩阵完整规格】\n"
        ai_deep_output += "  PASS  (>=pass_threshold):  Ship as-is, 直接交付\n"
        ai_deep_output += "  FIX   (>=fix_threshold):   Minor adjustments, 微调后交付\n"
        ai_deep_output += "  ITERATE (>=iterate_threshold): Re-prompt, 修改提示词重新生成\n"
        ai_deep_output += "  DISCARD (<iterate_threshold):  Start over, 根本原因分析后重做\n\n"

        ai_deep_output += "【故障归因完整映射 (30 条)】\n"
        for symptom, layer, layer_name, fix in FAILURE_ATTRIBUTION_MAP:
            ai_deep_output += "  " + symptom + "\n"
            ai_deep_output += "    -> " + layer + " (" + layer_name + ") -> " + fix + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【反 AI 扫描结果】\n"
        ai_deep_output += "  违规数: " + str(len(anti_ai_violations)) + "\n"
        if anti_ai_violations:
            for v in anti_ai_violations[:10]:
                ai_deep_output += "  - \"" + v["phrase"] + "\" -> " + v["replacement"] + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【191 反 AI 词表 + 4 轮迭代】\n"
        ai_deep_output += "瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词\n\n"

        ai_deep_output += "【沉默 5 规则 + 4 步公式 + 30 秒场景单元】\n"
        ai_deep_output += inject_silence_mastery_5("对话", 1) + "\n\n"

        ai_deep_output += "【9 维光照控制 (CIE LAB + 摄影本体)】\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "QualityAssurancePro": QualityAssurancePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "QualityAssurancePro": "✅ 质量 QA (环节 34) — L5 重写",
# }
