# -*- coding: utf-8 -*-
"""
AestheticJudgmentPro - 审美判断节点 (环节 7 摄影指导 + 美术 + 调色综合)
==========================================================================
Phase 28 P0 - 联网研究影视审美 + 100+ 场景库 + 自动赋予审美判断能力

数据源 (Phase 28 联网研究):
- 杨远婴《电影概论》 画面基本元素 (构图/景别/角度/景深/运动)
- 梅耶尔艺术鉴赏六要素 (Meier 1942 美术能力)
- Graves Design Judgment Test 8 大美学原则 (调和/主题/变化/平衡/连贯/对称/比例/韵律)
- 格式塔心理学 (整体性/选择性/同型性/闭合性/连续性)
- 王家卫/韦斯·安德森/陈凯歌/诺兰/塔可夫斯基/黑泽明 6 大导演色彩体系
- 6 大基础场景类型 + 120 场景库 (scene_library)

核心能力 (基于 AIGC 影视全流程解析 2.1 节):
- 摄影指导: 构图 / 景别 / 角度 / 景深 / 运动
- 美术指导: 场景 / 道具 / 服装 / 色彩
- 调色: 色彩心理学 / 调色方向 / 情绪色彩
- 8 美学原则: 调和/主题/变化/平衡/连贯/对称/比例/韵律
- 6 大导演色彩体系: 自动识别输入,适配签名
- 120 场景库自动匹配

**自动赋予能力** (默认开启) + **专项调整** (用户输入参数覆盖)

5 要素架构 (AIGC 文档 1.2 节):
- 数据层: 美学维度权重 + 8 原则 + 6 导演体系 + 120 场景
- 上下文缩略层: 输入概要
- Skill/Harness: 评分算法 (加权求和)
- 经验矩阵: 导演历史 (director_soul 灵魂注入)
- AI 深度处理: LLM 风格的综合决策
"""
from __future__ import annotations

import os
import sys

# === Phase 36.6 v5i: 35 导演统一数据中枢 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, ALL_DIRECTOR_NAMES, get_director_profile,
        SCENE_DATABASE_100,
        DP_8_MASTERS,
        get_director,
        get_scene,
    )
    _HAS_DDU = True
except Exception:
    _HAS_DDU = False
import json
import re

# ============================================================
# 反 AI 词表导入
# ============================================================
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False

# 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# 场景库
try:
    from scene_library import (
        SCENES, SCENE_TYPES_6, get_scene_by_id, get_scenes_by_type,
        get_scenes_by_mood, get_scenes_by_director, scene_to_prompt,
    )
    _HAS_SCENE_LIB = True
except Exception:
    _HAS_SCENE_LIB = False


# ============================================================
# 8 大美学原则 (Graves Design Judgment Test 1948)
# ============================================================
AESTHETIC_PRINCIPLES_8 = {
    "1_调和": {
        "name_zh": "调和 (Harmony)",
        "description": "画面中各元素 (色相/明度/饱和度/线条/形状) 之间协调统一, 没有冲突",
        "weight_default": 0.12,
        "criteria": "色彩调和 / 形式调和 / 概念调和",
        "applies_to": ["COLOR", "COMPOSITION", "LIGHTING"],
    },
    "2_主题": {
        "name_zh": "主题 (Theme)",
        "description": "画面所有元素围绕一个清晰主题/中心思想, 主次分明",
        "weight_default": 0.15,
        "criteria": "主题清晰 / 视觉中心 / 主体突出",
        "applies_to": ["COMPOSITION", "STORY", "CHARACTER"],
    },
    "3_变化": {
        "name_zh": "变化 (Variation)",
        "description": "在统一中求变化, 避免单调, 通过对比/节奏/层次避免画面死板",
        "weight_default": 0.10,
        "criteria": "层次变化 / 光影变化 / 动态变化",
        "applies_to": ["COMPOSITION", "LIGHTING", "MOTION"],
    },
    "4_平衡": {
        "name_zh": "平衡 (Balance)",
        "description": "画面元素在视觉重量上达到平衡, 重心稳定, 不偏不倚",
        "weight_default": 0.12,
        "criteria": "左右平衡 / 上下平衡 / 视觉重量",
        "applies_to": ["COMPOSITION", "LIGHTING"],
    },
    "5_连贯": {
        "name_zh": "连贯 (Unity)",
        "description": "画面作为一个整体呈现, 各部分相互联系, 视觉上一气呵成",
        "weight_default": 0.12,
        "criteria": "整体感 / 连贯性 / 视觉统一",
        "applies_to": ["COMPOSITION", "STORY", "COLOR"],
    },
    "6_对称": {
        "name_zh": "对称 (Symmetry)",
        "description": "画面中轴/中心对称, 营造仪式感/庄严感/童话感",
        "weight_default": 0.08,
        "criteria": "中轴对称 / 镜像对称 / 几何对称",
        "applies_to": ["COMPOSITION"],
        "directors": ["韦斯·安德森"],
    },
    "7_比例": {
        "name_zh": "比例 (Proportion)",
        "description": "画面元素之间的比例关系 (黄金分割/三分法/大小对比) 合理",
        "weight_default": 0.12,
        "criteria": "黄金分割 / 三分法 / 大小对比",
        "applies_to": ["COMPOSITION", "FRAMING"],
    },
    "8_韵律": {
        "name_zh": "韵律 (Rhythm)",
        "description": "画面元素的重复/渐变/跳跃形成韵律感, 推动视觉流动",
        "weight_default": 0.10,
        "criteria": "视觉韵律 / 节奏感 / 元素重复",
        "applies_to": ["COMPOSITION", "MOTION", "EDITING"],
    },
}


# ============================================================
# 6 大导演色彩体系 (联网研究: 王家卫/韦斯·安德森/陈凯歌/诺兰/塔可夫斯基/黑泽明)
# ============================================================
DIRECTOR_COLOR_SYSTEMS_6 = {
    "王家卫": {
        "description": "高饱和色彩 + 霓虹光 + 冷暖对比 + 运动模糊",
        "primary": "高饱和的红/绿/蓝/紫, 标志霓虹色温偏移",
        "secondary": "暖红 (花样年华) / 冷蓝 (重庆森林) / 黄沙 (东邪西毒)",
        "lighting": "霓虹主光 + 高光溢出 + 阴影保留细节 + 人工光源主导",
        "contrast": "强烈冷暖对比 (春光乍泄冷蓝/暖黄)",
        "lens": "前景遮挡构图 + 反射表面 + 抽帧 (80% 速度)",
        "applies": ["hk_neon", "sh_alley", "rain", "psyche_loneliness"],
    },
    "韦斯·安德森": {
        "description": "对称构图 + 高饱和糖果色 + 平面化 + 童话感",
        "primary": "粉/红/黄/绿/蓝 高饱和糖果色",
        "secondary": "千禧粉 (布达佩斯) / 黄绿 (月升王国) / 蓝色 (水中生活)",
        "lighting": "柔和均匀, 平面化, 高对比度, 童话感",
        "contrast": "互补色控制 (黄紫) 表达对立 (布达佩斯 D 夫人)",
        "lens": "完美对称 + 中心构图 + 强迫症般几何感",
        "applies": ["dream_paper", "psyche_joy", "coffee", "tokyo_street"],
    },
    "陈凯歌": {
        "description": "厚重文化感 + 浓重色彩 + 黄金分割 + 象征式构图",
        "primary": "浓重红/蓝/金/黑, 文化象征",
        "secondary": "霸王别姬宝蓝/金/黑 / 妖猫传红/金/白",
        "lighting": "侧光 + 逆光 + 烛光, 戏剧化光影",
        "contrast": "明暗对比强烈, 黄金分割/倾斜式构图",
        "lens": "景别+角度考究, 复合式运动镜头",
        "applies": ["throne_palace", "brothel", "hengdian_tang"],
    },
    "诺兰": {
        "description": "IMAX 物理真实 + 高对比冷色调 + 宏大叙事",
        "primary": "冷色 (蓝/灰/青) + 偶尔暖色 (琥珀)",
        "secondary": "星际穿越冷蓝 / 黑暗骑士冷青 / 奥本海默琥珀",
        "lighting": "自然光 + 实用光, 物理真实, 大反差",
        "contrast": "明暗硬对比, 黑色深沉, 高光清晰",
        "lens": "IMAX 70mm, 大景深, 广角",
        "applies": ["matrix", "psyche_madness", "mirror", "train_loop"],
    },
    "塔可夫斯基": {
        "description": "诗意长镜头 + 自然光 + 水/火/记忆意象",
        "primary": "自然色 (水/火/雪/光) + 暗调",
        "secondary": "水波光影 / 烛光摇曳 / 雨后光 / 雾",
        "lighting": "自然光 + 烛光, 时间流动感",
        "contrast": "明暗渐变, 长镜头内部自然变化",
        "lens": "极致长镜头 (4-10 分钟), 固定机位",
        "applies": ["lake", "sky", "psyche_underwater", "rain", "meadow"],
    },
    "黑泽明": {
        "description": "多机位动态构图 + 自然光 + 武士道色彩",
        "primary": "自然色 (红/白/黑) + 武士道色彩",
        "secondary": "乱的红/白/黑 / 梦的水彩/油画",
        "lighting": "多机位动态构图, 自然光, 戏剧化",
        "contrast": "强烈明暗对比, 红色象征 (红)",
        "lens": "多机位动态构图, 戏剧化运动",
        "applies": ["mountain", "dream", "rain", "wuxia"],
    },
}


# ============================================================
# 摄影指导 5 维 (杨远婴《电影概论》)
# ============================================================
CINEMATOGRAPHY_5 = {
    "构图": {
        "description": "画面布局/视觉中心/非对称均衡/留白/封闭 vs 开放",
        "sub_principles": ["视觉中心", "非对称均衡", "线条与几何形构架", "留白", "封闭式 vs 开放式", "黄金分割", "三分法", "对称"],
        "techniques": ["黄金分割", "三分法", "对角线构图", "框中框", "引导线", "前景遮挡", "反射表面"],
    },
    "景别": {
        "description": "取景范围 (远/全/中/近/特)",
        "sub_principles": ["EWS 极端广角", "WS 广角", "FS 全景", "MWS 中广角", "MS 中景", "MCU 中特写", "CU 特写", "ECU 极端特写", "Establishing 定场"],
        "techniques": ["定场镜头", "对话中近景", "特写表情", "极端特写细节"],
    },
    "角度": {
        "description": "摄影机相对主体的俯仰/方向",
        "sub_principles": ["平视角", "仰角 (高大)", "俯角 (渺小)", "鸟瞰 (上帝视角)", "虫视 (极端仰角)", "荷兰角 (倾斜)"],
        "techniques": ["仰角 (权力感)", "俯角 (压迫感)", "荷兰角 (心理失衡)"],
    },
    "景深": {
        "description": "画面纵深清晰范围 (深/浅)",
        "sub_principles": ["深景深 (环境)", "浅景深 (主体突出)", "移焦 (rack focus)", "散景"],
        "techniques": ["f/1.4 浅景深人像", "f/16 深景深环境", "移焦引导视线"],
    },
    "运动": {
        "description": "摄影机的运动方式 (推/拉/摇/移/跟)",
        "sub_principles": ["固定", "推", "拉", "横摇", "直摇", "横移", "跟", "升降", "复合运动", "长镜头"],
        "techniques": ["长镜头 4-10 分钟 (塔可夫斯基)", "斯坦尼康稳定器", "摇臂", "无人机航拍", "360 度环绕"],
    },
}


# ============================================================
# 色彩心理学 (基于 6 大导演体系 + 通用色彩心理学)
# ============================================================
COLOR_PSYCHOLOGY_8 = {
    "red": {"emotion": "激情/危险/爱情/愤怒", "directors": ["王家卫", "黑泽明", "陈凯歌"]},
    "blue": {"emotion": "冷静/忧郁/信任/孤独", "directors": ["诺兰", "王家卫", "塔可夫斯基"]},
    "green": {"emotion": "生命/希望/危险/嫉妒", "directors": ["韦斯·安德森", "王家卫"]},
    "yellow": {"emotion": "希望/温暖/警示/疯狂", "directors": ["韦斯·安德森", "陈凯歌"]},
    "purple": {"emotion": "神秘/高贵/孤独/灵性", "directors": ["韦斯·安德森", "陈凯歌"]},
    "orange": {"emotion": "温暖/活力/快乐/丰收", "directors": ["韦斯·安德森", "黑泽明"]},
    "black": {"emotion": "死亡/神秘/权力/正式", "directors": ["诺兰", "陈凯歌", "塔可夫斯基"]},
    "white": {"emotion": "纯净/死亡/医疗/超现实", "directors": ["陈凯歌", "塔可夫斯基"]},
}


# ============================================================
# 评分算法 - 加权求和
# ============================================================
def judge_aesthetic(input_text="", director="", scene_id="", scene_type="",
                    target_emotion="", auto_principles=True,
                    custom_weights=None):
    """
    审美判断 - 8 维度评分 + 6 导演体系 + 场景库匹配

    Args:
        input_text: 输入描述 (场景/情节/角色/画面)
        director: 导演风格 (空 = 自动)
        scene_id: 场景 ID (从 scene_library)
        scene_type: 场景类型 (从 scene_library)
        target_emotion: 目标情感
        auto_principles: 是否自动启用 8 原则
        custom_weights: 自定义权重 dict {原则: 权重}

    Returns:
        dict: {
            "scores": {原则: 分数},
            "total": 总分,
            "color_system": 适配的色彩体系,
            "scene_match": 场景匹配结果,
            "directors": 适配的导演风格,
            "principles_text": 8 原则文本,
            "judgment": 整体判断,
        }
    """
    if not input_text:
        input_text = ""

    # 1. 自动识别导演
    detected_director = director or _auto_detect_director(input_text)

    # 2. 自动匹配场景
    matched_scene = None
    if scene_id and _HAS_SCENE_LIB:
        matched_scene = get_scene_by_id(scene_id)
    elif scene_type and _HAS_SCENE_LIB:
        candidates = get_scenes_by_type(scene_type)
        if candidates:
            matched_scene = candidates[0]
    elif _HAS_SCENE_LIB and input_text:
        matched_scene = _auto_match_scene(input_text)

    # 3. 8 原则评分 (基于关键词启发)
    principles_scores = _score_8_principles(input_text, custom_weights, auto_principles)

    # 4. 6 导演体系匹配
    color_system = _match_color_system(input_text, detected_director)

    # 5. 5 维摄影指导
    cinematography = _score_cinematography(input_text, detected_director)

    # 6. 8 色彩心理学匹配
    color_psych = _match_color_psychology(input_text)

    # 7. 加权总分
    total = sum(principles_scores.values()) / 8.0  # 平均分 0-1

    # 8. 整体判断
    judgment = _make_judgment(total, detected_director, matched_scene, color_system)

    return {
        "scores": principles_scores,
        "total": round(total, 3),
        "color_system": color_system,
        "scene_match": matched_scene,
        "directors": [detected_director] if detected_director else [],
        "principles_text": "\n".join(["- {}: {:.2f}".format(k, v) for k, v in principles_scores.items()]),
        "cinematography": cinematography,
        "color_psychology": color_psych,
        "judgment": judgment,
    }


def _auto_detect_director(input_text):
    """根据输入文本自动识别导演风格"""
    text = input_text.lower()
    director_keywords = {
        "王家卫": ["霓虹", "重庆", "花样年华", "2046", "春光乍泄", "孤独", "高饱和", "抽帧"],
        "韦斯·安德森": ["对称", "糖果色", "千禧粉", "布达佩斯", "强迫症", "对称构图", "平面化"],
        "陈凯歌": ["霸王别姬", "妖猫传", "刺秦", "黄金分割", "侧光", "逆光", "象征式"],
        "诺兰": ["盗梦空间", "星际穿越", "黑暗骑士", "敦刻尔克", "imax", "高对比", "冷色调", "心理空间"],
        "塔可夫斯基": ["镜子", "乡愁", "潜行者", "长镜头", "诗意", "自然光", "水", "火", "记忆"],
        "黑泽明": ["七武士", "乱", "罗生门", "梦", "武士", "动态构图", "多机位"],
    }
    for d, kws in director_keywords.items():
        if any(k in input_text for k in kws) or any(k in text for k in kws):
            return d
    return ""


def _auto_match_scene(input_text):
    """根据输入文本自动匹配场景"""
    if not _HAS_SCENE_LIB:
        return None
    scene_keywords = {
        "urban_hk_neon_street": ["香港", "重庆森林", "霓虹", "庙街", "重庆大厦"],
        "urban_sh_liaison_alley": ["上海", "弄堂", "花样年华", "石库门"],
        "urban_paris_eiffel": ["巴黎", "铁塔", "香榭丽舍"],
        "urban_london_brick": ["伦敦", "大本钟", "泰晤士"],
        "nature_sea_ocean": ["海", "海洋", "沙滩", "海边"],
        "nature_field_grass": ["麦田", "油菜花", "草原", "高粱"],
        "nature_bamboo_forest": ["竹林", "竹海"],
        "studio_kitchen_restaurant": ["厨房", "餐厅", "做饭"],
        "studio_bathhouse_japan": ["澡堂", "温泉"],
        "nature_rain_storm": ["雨", "暴雨", "雨夜", "雷"],
        "nature_snow_winter_street": ["雪", "雪夜", "冬日", "雪景"],
        "psyche_loneliness_room": ["孤独", "空房间", "心理", "内心"],
        "psyche_grief_rain": ["悲伤", "哀伤", "葬礼"],
        "psyche_fear_shadow": ["恐惧", "害怕", "阴影"],
        "psyche_awe_cosmos": ["敬畏", "宇宙", "星空", "星空"],
        "nature_cherry_blossom": ["樱花", "春日", "桃花"],
        "studio_throne_palace": ["宫殿", "王座", "皇宫"],
        "studio_office_modern": ["办公室", "写字楼", "工位"],
        "nature_forest_deep": ["森林", "深林", "古树"],
        "nature_starry_night_sky": ["星空", "夜空", "月夜", "极光"],
        "nature_meadow_wildflower": ["野花", "草地", "山间", "花海"],
        "dream_floating_island": ["漂浮", "空中", "失重", "天空之城"],
        "dream_magical_forest": ["魔法", "精灵", "萤火虫"],
        "virtual_cyberpunk_city": ["赛博朋克", "未来都市", "霓虹都市"],
        "virtual_space_station": ["太空", "飞船", "宇宙"],
        "nature_mountain_snow": ["雪山", "高山", "冰川"],
        "urban_tokyo_shinjuku": ["东京", "新宿", "涉谷", "歌舞伎町"],
    }
    for sid, kws in scene_keywords.items():
        if any(k in input_text for k in kws):
            return get_scene_by_id(sid)
    return None


def _score_8_principles(input_text, custom_weights, auto_principles):
    """8 原则评分 (关键词启发)"""
    text = input_text
    scores = {}

    # 1 调和 (Harmony)
    harmony_kws = ["和谐", "调和", "协调", "统一", "呼映", "匹配"]
    scores["1_调和"] = _kw_score(text, harmony_kws, AESTHETIC_PRINCIPLES_8["1_调和"]["weight_default"], custom_weights)

    # 2 主题 (Theme)
    theme_kws = ["主题", "中心", "主体", "主角", "聚焦", "突出", "视觉中心"]
    scores["2_主题"] = _kw_score(text, theme_kws, AESTHETIC_PRINCIPLES_8["2_主题"]["weight_default"], custom_weights)

    # 3 变化 (Variation)
    variation_kws = ["变化", "对比", "层次", "动态", "节奏", "反差"]
    scores["3_变化"] = _kw_score(text, variation_kws, AESTHETIC_PRINCIPLES_8["3_变化"]["weight_default"], custom_weights)

    # 4 平衡 (Balance)
    balance_kws = ["平衡", "对称", "稳重", "均衡"]
    scores["4_平衡"] = _kw_score(text, balance_kws, AESTHETIC_PRINCIPLES_8["4_平衡"]["weight_default"], custom_weights)

    # 5 连贯 (Unity)
    unity_kws = ["连贯", "整体", "一气", "统一", "完整", "系列感"]
    scores["5_连贯"] = _kw_score(text, unity_kws, AESTHETIC_PRINCIPLES_8["5_连贯"]["weight_default"], custom_weights)

    # 6 对称 (Symmetry)
    symmetry_kws = ["对称", "镜像", "中轴", "韦斯", "安德森", "几何"]
    scores["6_对称"] = _kw_score(text, symmetry_kws, AESTHETIC_PRINCIPLES_8["6_对称"]["weight_default"], custom_weights)

    # 7 比例 (Proportion)
    proportion_kws = ["比例", "黄金", "三分", "大小", "对比"]
    scores["7_比例"] = _kw_score(text, proportion_kws, AESTHETIC_PRINCIPLES_8["7_比例"]["weight_default"], custom_weights)

    # 8 韵律 (Rhythm)
    rhythm_kws = ["韵律", "节奏", "重复", "渐变", "跳跃", "流动"]
    scores["8_韵律"] = _kw_score(text, rhythm_kws, AESTHETIC_PRINCIPLES_8["8_韵律"]["weight_default"], custom_weights)

    # 归一化到 0-1
    max_possible = 0.15 + 0.15 + 0.10 + 0.12 + 0.12 + 0.08 + 0.12 + 0.10  # = 0.94
    for k in scores:
        scores[k] = round(scores[k] / max_possible, 3)

    return scores


def _kw_score(text, keywords, default_w, custom_w):
    """根据关键词命中打分"""
    score = default_w  # 基础分 = 默认权重
    if not text:
        return score
    for kw in keywords:
        if kw in text:
            score += 0.05
    return score


def _match_color_system(input_text, director):
    """匹配 6 大导演色彩体系"""
    if director and director in DIRECTOR_COLOR_SYSTEMS_6:
        return {"director": director, **DIRECTOR_COLOR_SYSTEMS_6[director]}

    # 关键词匹配
    text = input_text
    if any(k in text for k in ["霓虹", "重庆", "花样年华", "高饱和", "抽帧"]):
        return {"director": "王家卫", **DIRECTOR_COLOR_SYSTEMS_6["王家卫"]}
    if any(k in text for k in ["对称", "糖果", "千禧粉", "布达佩斯", "平面化"]):
        return {"director": "韦斯·安德森", **DIRECTOR_COLOR_SYSTEMS_6["韦斯·安德森"]}
    if any(k in text for k in ["霸王别姬", "妖猫传", "刺秦", "黄金分割"]):
        return {"director": "陈凯歌", **DIRECTOR_COLOR_SYSTEMS_6["陈凯歌"]}
    if any(k in text for k in ["盗梦", "星际", "黑暗骑士", "imax", "高对比", "冷色调"]):
        return {"director": "诺兰", **DIRECTOR_COLOR_SYSTEMS_6["诺兰"]}
    if any(k in text for k in ["长镜头", "诗意", "自然光", "水", "记忆"]):
        return {"director": "塔可夫斯基", **DIRECTOR_COLOR_SYSTEMS_6["塔可夫斯基"]}
    if any(k in text for k in ["七武士", "乱", "武士", "多机位", "动态构图"]):
        return {"director": "黑泽明", **DIRECTOR_COLOR_SYSTEMS_6["黑泽明"]}

    # 默认王家卫 (最广泛适配)
    return {"director": "王家卫", **DIRECTOR_COLOR_SYSTEMS_6["王家卫"]}


def _score_cinematography(input_text, director):
    """5 维摄影指导评分"""
    text = input_text
    result = {}
    for dim, info in CINEMATOGRAPHY_5.items():
        hits = []
        for sub in info["sub_principles"]:
            # 提取核心词
            core = sub.split(" ")[-1] if " " in sub else sub
            if core in text:
                hits.append(sub)
        result[dim] = {
            "description": info["description"],
            "matched_techniques": hits,
            "match_count": len(hits),
        }
    return result


def _match_color_psychology(input_text):
    """8 色彩心理学匹配"""
    text = input_text.lower()
    matches = []
    color_keywords = {
        "red": ["红", "朱", "红绸", "血红", "red"],
        "blue": ["蓝", "青", "靛", "冷", "blue"],
        "green": ["绿", "翠", "翡翠", "green"],
        "yellow": ["黄", "金", "琥珀", "yellow"],
        "purple": ["紫", "绛", "purple"],
        "orange": ["橙", "橘", "orange"],
        "black": ["黑", "墨", "暗", "black"],
        "white": ["白", "皓", "银白", "white"],
    }
    for color, kws in color_keywords.items():
        if any(k in text for k in kws):
            info = COLOR_PSYCHOLOGY_8[color]
            matches.append({"color": color, "emotion": info["emotion"], "directors": info["directors"]})
    return matches


def _make_judgment(total, director, scene, color_system):
    """综合判断"""
    level = "极高" if total >= 0.85 else "高" if total >= 0.7 else "中" if total >= 0.55 else "待提升"
    parts = [
        "【综合审美判断】",
        "美学水准: {} ({}/100)".format(level, int(total * 100)),
        "适配导演: {}".format(director or color_system.get("director", "王家卫")),
        "色彩体系: {}".format(color_system.get("description", "通用美学")),
    ]
    if scene:
        parts.append("场景匹配: 【{}】({})".format(scene["name"], scene["type"]))
        parts.append("  - {}".format(scene["desc"]))
    return "\n".join(parts)


# ============================================================
# ComfyUI 节点类
# ============================================================
class AestheticJudgmentPro:
    """
    审美判断 Pro 节点 - Phase 28 P0
    环节 7 摄影指导 + 美术 + 调色综合

    输入:
        输入描述 (textarea): 场景/情节/角色/画面描述
        导演风格 (dropdown): 王家卫/韦斯·安德森/陈凯歌/诺兰/塔可夫斯基/黑泽明/auto
        场景类型 (dropdown): 6 大基础类型 + auto
        目标情感 (text): 主导情感 (8 基础/60 矩阵/auto)
        8 原则权重 (text): JSON 自定义权重, 留空用默认
        自动启用 (toggle): 默认 ON
        灵魂_主导情感 (text): 与 director_soul 兼容
        灵魂_场景权重 (float): 与 director_soul 兼容
        灵魂_次要情感 (text): 与 director_soul 兼容
        灵魂_融合模式 (dropdown): 与 director_soul 兼容

    输出:
        审美判断 (string): 综合判断文本
        8 原则评分 (string): JSON
        色彩体系 (string): 6 导演体系匹配
        场景匹配 (string): 场景库匹配结果
        摄影指导 (string): 5 维摄影指导建议
        色彩心理学 (string): 8 色彩心理学匹配
    """

    @classmethod
    def INPUT_TYPES(cls):
        _director_choices = (
            ["auto", "无"] + ALL_DIRECTOR_NAMES
            if _HAS_DDU else
            ["auto", "王家卫", "韦斯·安德森", "陈凯歌", "诺兰", "塔可夫斯基", "黑泽明", "无"]
        )
        return {
            "required": {
                "输入描述": ("STRING", {"default": "", "multiline": True}),
                # Phase 36.6 v5i: 35 导演全列表 (镜头/光/节奏/色彩/表演/构图/声音/情绪)
                "导演风格": (_director_choices, {"default": "auto"}),
                "场景类型": (["auto", "STUDIO_INTERIOR", "NATURE_EXTERIOR", "URBAN_EXTERIOR", "URBAN_INTERIOR", "PERIOD_FILM_LOCATION", "VIRTUAL_SCENE", "PSYCHE_SPACE", "DREAM_MEMORY"], {"default": "auto"}),
            },
            "optional": {
                "目标情感": ("STRING", {"default": "auto"}),
                "8原则权重": ("STRING", {"default": "", "multiline": True}),
                "自动启用8原则": (["ON", "OFF"], {"default": "ON"}),
                "灵魂_主导情感": ("STRING", {"default": "auto"}),
                "灵魂_次要情感": ("STRING", {"default": ""}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_融合模式": (["auto", "weighted", "primary_only", "max", "harmonic"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("审美判断", "8原则评分", "色彩体系", "场景匹配", "摄影指导", "色彩心理学")
    FUNCTION = "judge"
    CATEGORY = "Director/Aesthetic"

    def judge(self, **kwargs):
        # 提取参数 (兼容中文 key)
        input_text = kwargs.get("输入描述", kwargs.get("input_desc", ""))
        director = kwargs.get("导演风格", kwargs.get("director", "auto"))
        scene_type = kwargs.get("场景类型", kwargs.get("scene_type", "auto"))
        target_emotion = kwargs.get("目标情感", kwargs.get("target_emotion", "auto"))
        weights_json = kwargs.get("8原则权重", kwargs.get("weights_json", ""))
        auto_principles = kwargs.get("自动启用8原则", kwargs.get("auto_principles", "ON"))
        soul_primary = kwargs.get("灵魂_主导情感", kwargs.get("soul_primary", "auto"))
        soul_secondary = kwargs.get("灵魂_次要情感", kwargs.get("soul_secondary", ""))
        soul_scene_weight = kwargs.get("灵魂_场景权重", kwargs.get("soul_scene_weight", 0.5))
        soul_fusion_mode = kwargs.get("灵魂_融合模式", kwargs.get("soul_fusion_mode", "auto"))

        # 反 AI 处理
        if _HAS_ANTI_AI:
            input_text = clean_anti_ai_text(input_text)
            input_text = inject_anti_ai_rules(input_text)

        # 解析自定义权重
        custom_weights = None
        if weights_json:
            try:
                custom_weights = json.loads(weights_json)
            except Exception:
                custom_weights = None

        # 适配兼容字段名
        director = "" if director in ("auto", "无") else director
        scene_type = "" if scene_type == "auto" else scene_type
        target_emotion = "" if target_emotion == "auto" else target_emotion
        auto_p = auto_principles == "ON"

        # 主判断
        result = judge_aesthetic(
            input_text=input_text,
            director=director,
            scene_type=scene_type,
            target_emotion=target_emotion,
            auto_principles=auto_p,
            custom_weights=custom_weights,
        )

        # Phase 36.6 v5i: 35 导演 8 维真实档案增强审美判断
        if director and _HAS_DDU and director in DIRECTOR_PROFILES_ALL:
            d_p = DIRECTOR_PROFILES_ALL[director]
            v5i_block = (
                f"\n\n【Phase 36.6 v5i: {director} 35 导演 8 维真实档案】\n"
                f"  镜头: {d_p['镜头']}\n"
                f"  光: {d_p['光']}\n"
                f"  节奏: {d_p['节奏']}\n"
                f"  色彩: {d_p['色彩']}\n"
                f"  表演: {d_p['表演']}\n"
                f"  构图: {d_p['构图']}\n"
                f"  声音: {d_p['声音']}\n"
                f"  情绪: {d_p['情绪']}\n"
                f"  代表作: {d_p['代表作']} (年代 {d_p['年代']})\n"
                f"  标志物件: {d_p['物件']}\n"
                f"  5 维标签: {d_p['5维标签']}\n"
            )
            # 8 大师摄影指导匹配
            tag_set = set(d_p["5维标签"].split("/"))
            for dp_name, dp_info in DP_8_MASTERS.items():
                if "罗杰·狄金斯" in dp_name and dp_info.get("代表作") == []:
                    continue
                dp_tag = set(dp_info.get("5维标签", "").split("/"))
                if tag_set & dp_tag:
                    v5i_block += f"  推荐摄影指导: {dp_name} - {dp_info['signature']}\n"
                    break
            # 100 场景匹配
            s_m = get_scene(director, scene_keyword=input_text[:50])
            if s_m and s_m.get("director") != "通用":
                v5i_block += (
                    f"  场景参考: {s_m['scene']} - 物件 {s_m['object']}, "
                    f"色调 {s_m['color']}, 声景 {s_m['sound']}\n"
                )
            result["judgment"] = result["judgment"] + v5i_block

        # 灵魂注入 (如果提供)
        if _HAS_SOUL and soul_primary != "auto":
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=float(soul_scene_weight) if soul_scene_weight else 0.5,
                    director=director or "auto",
                    secondary=[soul_secondary] if soul_secondary else None,
                    fusion_mode=soul_fusion_mode,
                    scene_context=input_text,
                )
                # 把灵魂状态融入判断
                if fused:
                    result["judgment"] += "\n\n【灵魂注入】主导: {} / 次要: {} / 融合态: {}".format(
                        soul_state.get("primary", ""),
                        soul_state.get("secondary", ""),
                        str(fused)[:200],
                    )
            except Exception as e:
                pass

        # 格式化输出
        scores_json = json.dumps(result["scores"], ensure_ascii=False, indent=2)
        color_system_str = json.dumps(result["color_system"], ensure_ascii=False, indent=2)
        scene_str = ""
        if result["scene_match"]:
            scene_str = scene_to_prompt(result["scene_match"], prefix="[匹配场景]")
        else:
            scene_str = "[未匹配] 请输入更具体描述或选择场景类型"
        cinematography_str = json.dumps(result["cinematography"], ensure_ascii=False, indent=2)
        color_psych_str = json.dumps(result["color_psychology"], ensure_ascii=False, indent=2)

        return (
            result["judgment"],
            scores_json,
            color_system_str,
            scene_str,
            cinematography_str,
            color_psych_str,
        )


# ============================================================
# 节点注册
# ============================================================
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "AestheticJudgmentPro": AestheticJudgmentPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "AestheticJudgmentPro": "审美判断 Pro (环节7 自动+专项)",
# }


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        {
            "input": "王家卫重庆森林 霓虹街道 雨夜 孤独 抽帧",
            "director": "auto",
            "scene_type": "auto",
        },
        {
            "input": "韦斯·安德森 布达佩斯大饭店 对称 千禧粉 童话感",
            "director": "auto",
            "scene_type": "auto",
        },
        {
            "input": "陈凯歌 妖猫传 唐代宫殿 红色 金色 盛唐",
            "director": "auto",
            "scene_type": "auto",
        },
        {
            "input": "诺兰 盗梦空间 走廊 心理空间 冷色调 高对比",
            "director": "auto",
            "scene_type": "auto",
        },
        {
            "input": "塔可夫斯基 镜子 水 烛光 记忆 长镜头",
            "director": "auto",
            "scene_type": "auto",
        },
    ]

    print("=" * 60)
    print("AestheticJudgmentPro 测试 (Phase 28 P0)")
    print("=" * 60)
    for tc in test_cases:
        print("\n输入: {}".format(tc["input"]))
        r = judge_aesthetic(input_text=tc["input"], director=tc["director"], scene_type=tc["scene_type"])
        print(r["judgment"][:300])
        if r["scene_match"]:
            print("[场景] {} ({})".format(r["scene_match"]["name"], r["scene_match"]["type"]))
