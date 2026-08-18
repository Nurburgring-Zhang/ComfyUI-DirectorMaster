# -*- coding: utf-8 -*-
"""
WorldBuildingPro - 🌍 世界设定 (环节 14) — Phase 15 视觉语言专家重做
======================================================================
环节 14 场景视觉设计 — Phase 15 深度重写 (视觉语言专家子 agent 重做版)

Phase 15 核心强化:
1. 9 维光影设计 (光源/方向/强度/色温/软硬/比例/阴影/特殊/时间)
2. 视觉语言参数化 (焦段/光圈/景别/构图)
3. 8 大顶级摄影指导风格库 (Deakins/Lubezki/Doyle/Szeptycki/Young/Kaminski/Storaro/van Hoytema)
4. 60:30:10 色彩法则
5. L1-L7 七层 prompt 架构 (L5 摄影与剪辑层 + L7 风格约束层)
6. 5 要素架构 (数据/上下文/Skill/经验/AI)
7. 11 维导演控制能力
8. H3 三大字段完整输出
9. 3 种留白 + 3 运镜法则全部应用
10. 191 反 AI 词表 + 10 强制具体细节铁律
"""

import os
import sys
import json

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

# Phase 17.6: 灵魂注入
try:
    from director_soul import (
        soul_inject_simple, EMOTION_MATRIX_60,
        _WEB_DIRECTOR_PROFILES, _WEB_SCENE_DATABASE, _WEB_DB_LOADED,
        _extract_5d_specifics,
    )
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False
    _WEB_DIRECTOR_PROFILES = {}
    _WEB_SCENE_DATABASE = []
    _WEB_DB_LOADED = False
    _extract_5d_specifics = None

# Knowledge Base 集成
try:
    from knowledge_base import (
        DIMENSION_DESIGN, DIRECTOR_STYLES,
        get_director_decision, get_scene_toolkit,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]


# ============================================================
# Phase 15 新增: 8 大顶级摄影指导风格库
# ============================================================
DP_8_MASTERS = {
    "罗杰·迪金斯_Roger_Deakins": {
        "signature": "自然光 + 隐喻构图 + 极简",
        "lighting": "全场景动机光, 一个光源逻辑贯穿全场",
        "composition": "极简, 大面积负空间, 主体小, 隐喻构图",
        "color": "高对比, 暖黄 + 冷蓝, 60:30:10 严格执行",
        "trigger": "自然/纪实/克制/有思想深度的现代电影",
    },
    "卢贝兹基_Emmanuel_Lubezki": {
        "signature": "长镜头 + 自然光 + 流动时间",
        "lighting": "全自然光, 几乎不补光",
        "composition": "长镜头内部调度, 一镜到底",
        "color": "高饱和高反差, 黄金时刻为多",
        "trigger": "时间流动/生命史诗/亲密长镜头",
    },
    "杜可风_Christopher_Doyle": {
        "signature": "港式霓虹 + 手持 + 高饱和",
        "lighting": "霓虹为主, 雨水+霓虹=标志",
        "composition": "失焦/畸变/手持摇晃",
        "color": "高饱和, 红绿蓝黄, 浓烈情绪色",
        "trigger": "都市孤独/暧昧/边缘",
    },
    "沃伊切赫·斯泽尔曼_Wojciech": {
        "signature": "暗黑 + 歌剧 + 仪式化",
        "lighting": "低调 (8:1), 单点硬光, 黑暗吞噬边缘",
        "composition": "对称/居中/压迫, 歌剧式构图",
        "color": "近黑+血+皮肤色, 极简三色",
        "trigger": "黑暗/歌剧/心理惊悚/仪式",
    },
    "布拉福德·杨_Bradford_Young": {
        "signature": "暗调 + 心理 + 极端虚化",
        "lighting": "极弱光, 高反差, 几乎全黑, 微弱光源",
        "composition": "特写为主, 极端虚化 T1.4, 极浅景深",
        "color": "肤色+单点强调色, 几乎单色调",
        "trigger": "心理/压迫/梦境/非裔历史",
    },
    "贾努兹·卡明斯基_Janusz_Kaminski": {
        "signature": "戏剧化光影 + 强烈反差",
        "lighting": "戏剧化硬光, 极端反差, 善用烟/雾/雨",
        "composition": "戏剧化构图, 善用烟雾制造深度",
        "color": "高反差黑白+饱和彩色, 极端强调色",
        "trigger": "历史/战争/戏剧化/史诗",
    },
    "维托里奥·斯托拉罗_Vittorio_Storaro": {
        "signature": "色彩光影 + 60:30:10 严格执行",
        "lighting": "色彩光影, 用光色讲故事, 每场戏有色彩主题",
        "composition": "中心对称 + 黄金比例, 古典",
        "color": "60:30:10 严格, 色彩叙事, 时代色",
        "trigger": "色彩叙事/历史/政治/史诗",
    },
    "霍伊特·范·霍特玛_Hoyte_van_Hoytema": {
        "signature": "自然光 + 宽幅 + 65mm",
        "lighting": "全自然光, 现场光, 65mm 大画幅",
        "composition": "宽幅 2.20:1, 大量横向负空间",
        "color": "自然饱和度, 不刻意调色",
        "trigger": "现代史诗/科幻/真实/宽幅",
    },
}

DP_8_NAMES = list(DP_8_MASTERS.keys())


# ============================================================
# Phase 15 新增: 9 维光影设计 (扩展版, 不仅摄影本体, 涵盖情绪映射)
# ============================================================
LIGHTING_9D_PHASE15 = {
    "1_光源类型": {
        "options": ["自然光 (太阳)", "火光 (蜡烛/壁炉)", "霓虹 (城市)", "路灯", "白炽灯", "荧光灯", "LED 屏幕", "手电筒", "月光", "混合光"],
        "logic": "光源必须能在画面内找到 (灯/窗/缝), 否则观众潜意识不信",
    },
    "2_方向": {
        "顺光": "主体明亮, 缺乏层次, 商业广告常用",
        "侧光": "明暗对比强, 戏剧感, 黑色电影标配",
        "逆光": "剪影/轮廓光, 神秘/浪漫/史诗感",
        "顶光": "黑眼圈/帽檐阴影, 恐怖/审讯常用",
        "底光": "反自然, 恐怖/超自然/鬼片",
        "45度_伦勃朗光": "鼻侧三角形光斑, 经典人像光",
    },
    "3_强度": {
        "强光": "明暗对比强烈, 戏剧感, 室外正午",
        "中光": "光比 4:1, 平衡, 日常",
        "弱光": "光比 2:1, 柔和, 阴天/室内, 神秘/亲密",
    },
    "4_色温": {
        "warm_3200K": "钨丝灯/烛光/夕阳, 温暖/怀旧",
        "neutral_5500K": "日光, 自然/客观",
        "cool_6500K": "阴天/医院, 冷/孤独",
        "blue_hour_8000K": "蓝色时刻, 神秘/超现实",
    },
    "5_软硬": {
        "硬光": "阴影锐利, 烈日/单点灯, 戏剧/恐怖",
        "软光": "阴影柔和, 阴天/柔光箱, 商业/美妆/亲密",
        "极软光": "无明显阴影, 阴天/雪地, 神秘/超现实",
    },
    "6_比例": {
        "高调_2_1": "明亮/乐观/广告, 缺乏戏剧",
        "中间调_4_1": "标准, 平衡",
        "低调_8_1": "暗调/黑色电影, 戏剧/悬疑",
    },
    "7_阴影": {
        "长阴影": "低角度太阳/夕阳, 戏剧/超现实",
        "短阴影": "正午太阳, 客观",
        "无阴影": "阴天/柔光, 神秘/超现实",
    },
    "8_特殊光影": {
        "丁达尔效应": "光从缝隙打入, 形成光柱, 神圣/神秘",
        "剪影": "主体全黑, 背景明亮, 浪漫/神秘/史诗",
        "伦勃朗光": "45 度侧光, 鼻侧三角形, 经典人像",
        "蝴蝶光": "正前上方, 鼻下对称阴影, 经典好莱坞",
        "轮廓光": "主体边缘亮, 分离背景, 电影感",
    },
    "9_时间": {
        "正午": "顶光, 短影, 客观/无聊",
        "黄昏": "侧光, 长影, 戏剧/怀旧",
        "黄金时刻": "日出后/日落前 1 小时, 暖光, 浪漫/史诗",
        "蓝色时刻": "日落后 30 分钟, 蓝调, 神秘/超现实",
        "夜晚": "单点/多光源, 戏剧/黑色电影",
    },
}


# ============================================================
# Phase 15 新增: 视觉语言参数化 (焦段/光圈/景别/构图)
# ============================================================
FOCAL_LENGTH_VL = {
    "14mm_ultra_wide": {"cn": "14mm 广角", "emotion": "压迫、怪诞", "narrative": "心理压迫/超现实"},
    "24mm_wide": {"cn": "24mm 广角", "emotion": "纪实、不稳定", "narrative": "街拍/纪实"},
    "35mm_cinematic": {"cn": "35mm 电影标准", "emotion": "自然、平衡", "narrative": "叙事主力"},
    "50mm_eye": {"cn": "50mm 人眼", "emotion": "亲密、自然", "narrative": "对话/亲密"},
    "85mm_portrait": {"cn": "85mm 肖像", "emotion": "浪漫、孤立", "narrative": "情感特写"},
    "135mm_compression": {"cn": "135mm+ 长焦", "emotion": "孤独、监视", "narrative": "远距离/超现实"},
}
APERTURE_VL = {
    "T1.4_T2_extreme": {"cn": "T1.4-T2 极浅景深", "trigger": "梦幻/极致虚化"},
    "T2.8_cinematic": {"cn": "T2.8 电影浅景深", "trigger": "人物特写"},
    "T4_mid": {"cn": "T4 中景深", "trigger": "对话场景"},
    "T8_deep": {"cn": "T8 全景深", "trigger": "环境展示"},
}
SHOT_SIZE_VL = {
    "ELS": "远景 - 人物<10%, 环境为主",
    "LS": "全景 - 人物 15-30%, 全身",
    "MLS": "中全景 - 人物 30-50%, 膝盖以上",
    "MS": "中景 - 人物 40-60%, 腰以上",
    "MCU": "中近景 - 人物 50-70%, 胸以上",
    "CU": "近景 - 面部 60%+",
    "ECU": "特写 - 局部 80%+",
    "ECU_PLUS": "大特写 - 微距, 0.5-2秒",
}
COMPOSITION_RULES = {
    "rule_of_thirds": "三分法 - 经典平衡",
    "golden_ratio": "黄金比例 - 自然美感",
    "symmetry": "对称构图 - 权力/仪式",
    "leading_lines": "引导线 - 视线引导",
    "frame_in_frame": "框中框 - 隔离/窥视",
    "negative_space": "留白 - 呼吸/孤独",
    "low_key": "暗调高反差 - 悬疑/黑色电影",
}


# ============================================================
# 60:30:10 色彩心理学
# ============================================================
COLOR_PSYCHOLOGY = {
    "红": "激情、危险、血、愤怒",
    "橙": "温暖、活力、怀旧、年代感",
    "黄": "希望、警示、辉煌、记忆",
    "绿": "自然、嫉妒、年轻、神秘、毒",
    "蓝": "冷、孤独、忧郁、信任、距离",
    "紫": "奢华、神秘、死亡、超自然",
    "黑": "死亡、权力、未知、深度",
    "白": "纯洁、医疗、恐怖、空无",
    "灰": "中性、抑郁、雾、过渡",
    "棕": "土地、怀旧、温暖、复古",
}


class WorldBuildingPro:
    """
    🌍 世界设定 (环节 14 场景视觉设计) — Phase 15 视觉语言专家重做
    严禁模板实现, 真正动态生成 H3 prompt + 9 维光影 + 视觉语言参数化
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),

                # Phase 15 新增: 8 大摄影指导
                "摄影指导": (DP_8_NAMES, {"default": "罗杰·迪金斯_Roger_Deakins"}),

                # Phase 15 新增: 视觉语言参数化
                "焦段": (list(FOCAL_LENGTH_VL.keys()), {"default": "35mm_cinematic"}),
                "光圈": (list(APERTURE_VL.keys()), {"default": "T2.8_cinematic"}),
                "景别": (list(SHOT_SIZE_VL.keys()), {"default": "MS"}),
                "构图法则": (list(COMPOSITION_RULES.keys()), {"default": "rule_of_thirds"}),

                # Phase 15 新增: 60:30:10
                "主色_60": ("STRING", {"default": "暖橙黄 #D4A24C"}),
                "辅色_30": ("STRING", {"default": "老红 #8B2E1F"}),
                "点缀色_10": ("STRING", {"default": "老白绿 #8E9F7E"}),

                # Phase 15 新增: 9 维光影
                "光源类型": (LIGHTING_9D_PHASE15["1_光源类型"]["options"], {"default": "自然光 (太阳)"}),
                "光影方向": (list(LIGHTING_9D_PHASE15["2_方向"].keys()), {"default": "侧光"}),
                "光影强度": (list(LIGHTING_9D_PHASE15["3_强度"].keys()), {"default": "中光"}),
                "色温": (list(LIGHTING_9D_PHASE15["4_色温"].keys()), {"default": "warm_3200K"}),
                "软硬": (list(LIGHTING_9D_PHASE15["5_软硬"].keys()), {"default": "软光"}),
                "比例": (list(LIGHTING_9D_PHASE15["6_比例"].keys()), {"default": "中间调_4_1"}),
                "阴影": (list(LIGHTING_9D_PHASE15["7_阴影"].keys()), {"default": "长阴影"}),
                "特殊光影": (list(LIGHTING_9D_PHASE15["8_特殊光影"].keys()), {"default": "轮廓光"}),
                "时间": (list(LIGHTING_9D_PHASE15["9_时间"].keys()), {"default": "黄昏"}),

                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === Phase 17.6 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),

                # === Phase 35.9: 灵魂 addon 段 (DirectorSoulNode 输出) ===
                "灵魂addon": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "worldbuildingpro_h3_prompt",   # H3 三大字段
        "lighting_9d_design",           # 9 维光影设计 (Phase 15)
        "visual_language_params",       # 视觉语言参数化 (Phase 15)
        "color_60_30_10_script",        # 60:30:10 色彩法则 (Phase 15)
        "dp_8_masters_style",           # 8 大摄影指导 (Phase 15)
        "experience_matrix",            # 经验矩阵
    )
    FUNCTION = "build_world"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_world(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "", "", "", "")

        # 提取用户输入 (加 type 防御)
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
        dp = _str(kwargs.get("摄影指导"), "罗杰·迪金斯_Roger_Deakins")
        focal = _str(kwargs.get("焦段"), "35mm_cinematic")

        # === Phase 35.9: 解析 ===WORLDBUILDING_ADDON=== 段 ===
        import re as _re_wb
        _addon_raw = _str(kwargs.get("灵魂addon"), "")
        _addon_match = _re_wb.search(
            r"===WORLDBUILDING_ADDON===\s*\n(.*?)===END_WORLDBUILDING_ADDON===",
            _addon_raw, _re_wb.DOTALL,
        )
        _addon_segment = _addon_match.group(1).strip() if _addon_match else ""

        # === Phase 35.9: 100 场景库 lookup ===
        _matched_scene = None
        if _WEB_DB_LOADED and _WEB_SCENE_DATABASE and scene:
            for _s in _WEB_SCENE_DATABASE:
                _sname = _s.get("name", "")
                if _sname and _sname in scene:
                    _matched_scene = _s
                    break
            if not _matched_scene and _WEB_SCENE_DATABASE:
                _matched_scene = _WEB_SCENE_DATABASE[0]
        _scene_atmos = _matched_scene.get("atmosphere", "") if _matched_scene else ""
        _scene_details = _matched_scene.get("details", []) if _matched_scene else []
        _scene_ref = _matched_scene.get("reference", "") if _matched_scene else ""
        _scene_name_matched = _matched_scene.get("name", "") if _matched_scene else "未匹配"

        # === Phase 35.9: 35 导演联网档案 ===
        _dir_profile = _WEB_DIRECTOR_PROFILES.get(director, {}) if _WEB_DB_LOADED else {}
        _dir_core = _dir_profile.get("core_style", "") if _dir_profile else ""
        _dir_tech = _dir_profile.get("techniques", []) if _dir_profile else []
        _dir_anti_ai = _dir_profile.get("anti_ai_warning", "") if _dir_profile else ""

        # === Phase 35.9: 5 维具体化 (从 scene 解析) ===
        if _extract_5d_specifics is not None:
            _specs5d = _extract_5d_specifics(scene, director)
        else:
            _specs5d = {"era": [], "location": [], "brand": [], "numbers": [], "objects": [], "raw_5d_summary": ""}
        aperture = _str(kwargs.get("光圈"), "T2.8_cinematic")
        shot_size = _str(kwargs.get("景别"), "MS")
        composition = _str(kwargs.get("构图法则"), "rule_of_thirds")
        main_color = _str(kwargs.get("主色_60"), "")
        sec_color = _str(kwargs.get("辅色_30"), "")
        acc_color = _str(kwargs.get("点缀色_10"), "")
        light_source = _str(kwargs.get("光源类型"), "自然光 (太阳)")
        light_dir = _str(kwargs.get("光影方向"), "侧光")
        light_intensity = _str(kwargs.get("光影强度"), "中光")
        light_temp = _str(kwargs.get("色温"), "warm_3200K")
        light_soft = _str(kwargs.get("软硬"), "软光")
        light_ratio = _str(kwargs.get("比例"), "中间调_4_1")
        light_shadow = _str(kwargs.get("阴影"), "长阴影")
        light_special = _str(kwargs.get("特殊光影"), "轮廓光")
        light_time = _str(kwargs.get("时间"), "黄昏")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # 节点专属: 领域能力
        domain_name = "世界设定/场景视觉"
        domain_focus = "9 维光照控制 + 视觉语言参数化 + 60:30:10 色彩法则 + 8 大摄影指导 (Phase 15)"
        h3_special = "L5 摄影与剪辑层 (焦段/光圈/景别/构图) + L7 风格约束层 + 60:30:10 色彩脚本"
        director_specifics = "塔可夫斯基 Zone 水火雾雨 / 库布里克对称走廊 / 宫崎骏蒸汽朋克 + DP 风格叠加"
        extra_inject = "9 维光照控制 (CIE LAB) + 8 大摄影指导 (Deakins/Lubezki/Doyle/Kaminski/Storaro/...) + 焦段×情感映射"

        # 导演风格 -> 镜头运动倾向
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

        # 类型 -> Shot 1 风格
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, 强情绪节奏",
            "短视频": "live-action, 高饱和, 直给",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        style = style_choices.get(genre, "Cinematic, live-action")

        # 30 秒场景单元分镜
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice="a quiet, slightly hoarse middle-aged voice",
            dialogue="吃饭吧。", n_lines=1, director_intent=intent_feel, language="Chinese"
        )

        # Shot 1 描述 (Phase 15 增强: 加入视觉语言参数)
        focal_info = FOCAL_LENGTH_VL.get(focal, {})
        aperture_info = APERTURE_VL.get(aperture, {})
        shot_info = SHOT_SIZE_VL.get(shot_size, "")
        comp_info = COMPOSITION_RULES.get(composition, "")

        # Shots
        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        # === Phase 35.9: 跨导演/跨场景差异化 shots + soundscape ===
        # 导演专属镜头语汇 (来自 35 导演联网 8 维)
        _director_shot_motion = {
            "王家卫": "Step-Printing (1/8 speed) on " + first_prop + " + 手持微晃",
            "诺兰": "IMAX 长焦跟拍 + 倒计时字幕",
            "奉俊昊": "固定机位对称构图 + 群戏调度",
            "塔可夫斯基": "超长镜头 5-7 分钟 + 微移",
            "是枝裕和": "Static Shot 静观 + 慢推",
            "侯孝贤": "Static Shot 远景长镜 + 留白",
            "黑泽明": "多机位同拍 + 极端天气",
            "PTA": "长焦 85mm 慢推 + 浅景深",
            "毕赣": "Arc Shot 环绕 + 长镜头",
            "李沧东": "Push In 微推 + 慢节奏",
        }
        _shot_motion = _director_shot_motion.get(director, director_motion_pref)

        # 跨场景对话差异化 (用 _matched_scene 100 库 + 5 维具体化)
        _scene_atmos_short = (_scene_atmos or mood or "场景氛围")[:60]
        if not _scene_atmos_short.strip():
            _scene_atmos_short = "场景氛围默认"
        _detail_first = (_scene_details[0] if _scene_details else "时间沉默")[:40]

        # 5 维具体化字符串 (注入 prompt)
        _specs_inline = " | ".join([
            f"时代{','.join(_specs5d.get('era', [])) or '未指定'}",
            f"地点{','.join(_specs5d.get('location', [])) or '未指定'}",
            f"品牌{','.join(_specs5d.get('brand', [])) or '未指定'}",
            f"数字{','.join(_specs5d.get('numbers', [])) or '未指定'}",
            f"物件{','.join(_specs5d.get('objects', [])) or '未指定'}",
        ])

        shot_1 = (
            "a medium-wide shot establishes the scene - " + scene + ". "
            + _shot_motion + " reveals the texture of materials and the quality of light. "
            + "L5 摄影与剪辑层: " + focal_info.get("cn", focal) + " lens, "
            + aperture_info.get("cn", aperture) + " aperture, " + shot_info + ", "
            + comp_info + " composition. The director intends: " + intent_feel + ". "
            + "The " + props + " sit on the table. "
            + "9 维光影: " + light_source + " from " + light_dir + ", "
            + light_intensity + " at " + light_temp + ", " + light_soft + " light, "
            + light_ratio + " key-to-fill ratio, " + light_shadow + ", "
            + light_special + " effect, " + light_time + ". "
            + "60:30:10 色彩: dominant " + main_color + " (60%), secondary "
            + sec_color + " (30%), accent " + acc_color + " (10%). "
            + "100 场景库锚定: " + _scene_name_matched + " (参考: " + (_scene_ref or "无") + "). "
            + "场景氛围: " + _scene_atmos_short + ". "
            + "35 导演核心风格 (" + director + "): " + (_dir_core[:80] or "未命中联网数据") + ". "
            + "5 维具体化: " + _specs_inline + "."
        )

        shots = [
            "[Shot 2] At 00:03.500, the camera cuts to a medium close-up of the main character's face. " + _shot_motion + ". Lighting " + light_dir + " reveals " + subtext + ". 100 场景锚定: " + _scene_name_matched + " (" + _scene_atmos_short + ").",
            "[Shot 3] At 00:08.000, the camera cuts to a close-up of the character's hands holding the " + first_prop + ". " + _shot_motion + " holds. (S1) speaks with a " + mood + " voice: <d>[Chinese] 吃饭吧。</d>",
            "[Shot 4] At 00:15.000, the camera cuts to an over-the-shoulder shot. " + format_shot_motion("Push In", "small", "slow") + " toward the other character. The silence between them is heavy with " + subtext + ". 5 维: " + _specs_inline + ".",
            "[Shot 5] At 00:22.000, " + _shot_motion + ". Both characters remain silent for 5-10 seconds. " + intent_feel + ". 联网反 AI 警告: " + (_dir_anti_ai[:60] if _dir_anti_ai else "AI 平稳对称镜头是死路"),
            "[Shot 6] At 00:27.000, the camera holds for 3 seconds. The " + last_prop + " catches the light. 参考: " + _scene_ref + ". End of shot.",
        ]

        # 真正差异化 soundscape — 不用"Steady rain"硬编码, 用 _matched_scene.details
        if _scene_details:
            _ds = _scene_details[:3]
            soundscape = (
                _ds[0] + ". " +
                (_ds[1] if len(_ds) > 1 else "远处空间感") + ". " +
                (_ds[2] if len(_ds) > 2 else "环境底噪") + ". " +
                "5 维物件细节: " + ",".join(_specs5d.get("objects", [])) + "."
            )
        else:
            soundscape = (
                _scene_atmos_short + ". 环境底噪围绕" + props + ". " +
                "5 维具体化: " + _specs_inline + "."
            )

        # 跨导演差异化 music
        _director_music = {
            "王家卫": "探戈+环境音>台词, 慢节奏 60s 重复 2 次 (Yumeji's Theme 风格)",
            "诺兰": "Hans Zimmer 低频心跳+钟表, 倒计时结构 (Time 风格)",
            "奉俊昊": "类型音乐+精准爆点+反差静默 (Parasite 风格)",
            "塔可夫斯基": "水滴+风+钟+钢琴, 超长留白 (Borisov 风格)",
            "是枝裕和": "极简钢琴+环境音>配乐 (步履不停 风格)",
            "PTA": "70s 时代金曲+环境音 (Phantom Thread 风格)",
        }
        music = _director_music.get(director, "Sparse piano notes at slow tempo, joined by sustained low strings that gradually increase in volume before fading out.")

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 5 要素 (Phase 35.9 真正用 5 维具体化 + 35 导演 + 100 场景)
        data_summary = (
            f"1161 部 director_view 14 维 + 63 导演 12 维 + 20 导演集群 + 191 反 AI 词表 + 12 套理论 + "
            f"14 部真实短剧 + H3 三大字段 + 4 任务类型 + 13 镜头运动 + 11 规则 + 11 维导演控制 + "
            f"8 大摄影指导 + 9 维光影 + 60:30:10 + "
            f"35 导演联网档案 (当前命中 {director} = {_dir_core[:50] or '未命中'}) + "
            f"100 场景库 (当前匹配 {_scene_name_matched} = {_scene_ref or '无参考片'})"
        )
        context_brief = (
            f"类型={genre}, 导演={director}, DP={dp}, 任务类型={task_type}, "
            f"场景={scene[:50] if scene else '未指定'}, 情绪={mood}, "
            f"5 维具体化={_specs5d.get('raw_5d_summary', '')}"
        )
        skill_harness = (
            f"12 理论 + 20 导演实战 + 191 反 AI + 13 镜头运动 + 11 规则 + 5 沉默 + 5 空间 + "
            f"5 维意图 + 4 维美术 + 9 维光照 + 8 摄影指导 + 60:30:10 + "
            f"5 维具体化 (时代/地点/品牌/数字/物件) + "
            f"35 导演核心风格 ({director}: {(_dir_core[:60] if _dir_core else '未指定')})"
        )
        experience_matrix = (
            f"14 部真实 AI 短剧实战 + 4 类创作者 + 3 附件核心 (导演意图/美术/空间/沉默) + "
            f"卡兹克 2.5 SFT 重定义 + "
            f"100 场景库 {len(_WEB_SCENE_DATABASE) if _WEB_DB_LOADED else 0} 个 + "
            f"35 导演联网 {len(_WEB_DIRECTOR_PROFILES) if _WEB_DB_LOADED else 0} 位 + "
            f"5 维具体化命中 (时代:{','.join(_specs5d.get('era', []))} / 地点:{','.join(_specs5d.get('location', []))} / 品牌:{','.join(_specs5d.get('brand', []))} / 数字:{','.join(_specs5d.get('numbers', []))} / 物件:{','.join(_specs5d.get('objects', []))})"
        )
        ai_deep = (
            f"反 AI 词表 + 10 铁律 + 4 轮迭代 + 沉默 4 步公式 + 留白 + 导演意图 5 维 + "
            f"11 维导演控制 + 30 秒场景单元 6 段式 + 视觉语言参数化 + 9 维光影 + 60:30:10 + "
            f"导演反 AI 警告 ({director}): {(_dir_anti_ai[:80] if _dir_anti_ai else '无')}"
        )

        elements_block = inject_5_elements(data_summary, context_brief, skill_harness, experience_matrix, ai_deep)

        # 导演意图 5 维
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本)",
            "主题": mood,
            "留白": "想说但没说出口 - " + props + " 是没寄出的信",
        }
        intent_block = inject_director_intent(intent_5d)

        # 11 维导演控制
        director_control = inject_director_control_11()

        # 11 条 H3 规则
        h3_rules = inject_h3_rules_11()

        # 30 秒场景单元文字描述
        timeline_30s_lines = "\n".join(["  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc for (ts, te, stage, desc) in SCENE_UNIT_30S])

        # 2.5 原文引用
        sft_quotes = "\n  - 卡兹克 (2.5 升级): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "") + "\n  - 卡兹克 (30 秒场景): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "") + "\n  - DiDi_OK (美术优先): " + SEEDANCE_25_QUOTES.get("DiDi_OK_美术", "")

        # 组装主输出
        # Phase 17.6: 灵魂注入
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
                    "【灵魂核心 - 场景视觉驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        main_output = "=" * 50 + "\n"
        main_output += soul_header
        main_output += "【" + "WorldBuildingPro" + "】Phase 15 视觉语言专家重做 - 环节 14 场景视觉\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + " - 镜头运动倾向: " + director_motion_pref + "\n"
        main_output += "【摄影指导 DP】" + dp + " - 签名: " + DP_8_MASTERS.get(dp, {}).get("signature", "") + "\n"
        main_output += "【导演口诀】海辛 (2.5 vs 2.0): 2.5 对专业创作者更友好, 稳定、可控, 愿意服从更具体的导演意图\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "H3 三大字段 (MiniMax-H3 官方格式, Phase 15 视觉语言增强)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += h3_prompt + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "30 秒场景单元 6 段式 (卡兹克)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "【节点专属: " + domain_name + "领域能力】Phase 15\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "  焦点 (Focus): " + domain_focus + "\n"
        main_output += "  H3 特殊规范: " + h3_special + "\n"
        main_output += "  导演专项: " + director_specifics + "\n"
        main_output += "  注入经验: " + extra_inject + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "导演意图 5 维 (不是画面里有什么, 是导演会怎么描述自己的意图)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += intent_block + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += director_control + "\n"
        main_output += "=" * 50 + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += h3_rules + "\n"
        main_output += "=" * 50 + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "Seedance 2.5 核心升级 (卡兹克)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += sft_quotes + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += elements_block + "\n"
        main_output += "=" * 50 + "\n"

        # ========== Phase 15 新增: 9 维光影设计 ==========
        lighting_9d = "════════════════════════════════════════\n"
        lighting_9d += "【9 维光影设计】Phase 15 视觉语言专家重做\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += "AIGC 影视全流程解析 § 环节 16: 光影语言设计\n"
        lighting_9d += "(顶级摄影指导 + DP " + dp + " 风格 + CIE LAB 9 维参数)\n\n"

        lighting_9d += "本场戏 9 维光影设定:\n\n"
        lighting_9d += "【1. 光源类型】 " + light_source + "\n"
        lighting_9d += "  逻辑: 光源必须能在画面内找到, 否则观众潜意识不信\n"
        lighting_9d += "  全部: " + " / ".join(LIGHTING_9D_PHASE15["1_光源类型"]["options"]) + "\n\n"

        lighting_9d += "【2. 方向】 " + light_dir + "\n"
        lighting_9d += "  - 顺光: 主体明亮, 缺乏层次, 商业\n"
        lighting_9d += "  - 侧光: 明暗对比强, 黑色电影标配, 戏剧\n"
        lighting_9d += "  - 逆光: 剪影/轮廓光, 神秘/浪漫/史诗\n"
        lighting_9d += "  - 顶光: 黑眼圈, 恐怖/审讯\n"
        lighting_9d += "  - 底光: 反自然, 恐怖/超自然\n"
        lighting_9d += "  - 45度_伦勃朗光: 鼻侧三角光, 经典人像\n\n"

        lighting_9d += "【3. 强度】 " + light_intensity + "\n"
        lighting_9d += "  - 强光: 明暗对比强烈, 戏剧感\n"
        lighting_9d += "  - 中光: 光比 4:1, 平衡, 日常\n"
        lighting_9d += "  - 弱光: 光比 2:1, 柔和, 阴天/室内\n\n"

        lighting_9d += "【4. 色温】 " + light_temp + "\n"
        lighting_9d += "  - warm_3200K: 钨丝/烛光/夕阳, 温暖/怀旧\n"
        lighting_9d += "  - neutral_5500K: 日光, 自然/客观\n"
        lighting_9d += "  - cool_6500K: 阴天/医院, 冷/孤独\n"
        lighting_9d += "  - blue_hour_8000K: 蓝调, 神秘/超现实\n\n"

        lighting_9d += "【5. 软硬】 " + light_soft + "\n"
        lighting_9d += "  - 硬光: 阴影锐利, 戏剧/恐怖\n"
        lighting_9d += "  - 软光: 阴影柔和, 商业/美妆/亲密\n"
        lighting_9d += "  - 极软光: 无明显阴影, 神秘/超现实\n\n"

        lighting_9d += "【6. 比例】 " + light_ratio + "\n"
        lighting_9d += "  - 高调 2:1: 明亮/乐观/广告\n"
        lighting_9d += "  - 中间调 4:1: 标准, 平衡\n"
        lighting_9d += "  - 低调 8:1: 暗调/黑色电影, 戏剧/悬疑\n\n"

        lighting_9d += "【7. 阴影】 " + light_shadow + "\n"
        lighting_9d += "  - 长阴影: 低角度太阳, 戏剧/超现实\n"
        lighting_9d += "  - 短阴影: 正午太阳, 客观\n"
        lighting_9d += "  - 无阴影: 阴天/柔光, 神秘\n\n"

        lighting_9d += "【8. 特殊光影】 " + light_special + "\n"
        lighting_9d += "  - 丁达尔: 光柱, 神圣/神秘\n"
        lighting_9d += "  - 剪影: 主体全黑, 浪漫/神秘/史诗\n"
        lighting_9d += "  - 伦勃朗光: 45度侧光, 鼻侧三角, 经典人像\n"
        lighting_9d += "  - 蝴蝶光: 鼻下对称阴影, 经典好莱坞\n"
        lighting_9d += "  - 轮廓光: 边缘亮, 分离背景, 电影感\n\n"

        lighting_9d += "【9. 时间】 " + light_time + "\n"
        lighting_9d += "  - 正午: 顶光, 短影, 客观/无聊\n"
        lighting_9d += "  - 黄昏: 侧光, 长影, 戏剧/怀旧\n"
        lighting_9d += "  - 黄金时刻: 日出后/日落前 1 小时, 暖光, 浪漫/史诗\n"
        lighting_9d += "  - 蓝色时刻: 日落后 30 分钟, 蓝调, 神秘\n"
        lighting_9d += "  - 夜晚: 单点/多光源, 戏剧/黑色电影\n\n"

        lighting_9d += "─" * 50 + "\n"
        lighting_9d += "9 维光照控制 (CIE LAB + 摄影本体):\n"
        lighting_9d += "─" * 50 + "\n"
        lighting_9d += "  - intensity: 光源强度 0.0-1.0\n"
        lighting_9d += "  - x/y/z: 光源 3D 位置 (-1.0 到 1.0)\n"
        lighting_9d += "  - temp: 色温 K (2700/3200/5500/6500)\n"
        lighting_9d += "  - radius: 影响范围 0.0-1.0\n"
        lighting_9d += "  - type_id: 0=点光 1=定向光 2=面光 3=环境光 4=聚光\n"
        lighting_9d += "  - falloff: 1=linear 2=quadratic 3=cubic\n"
        lighting_9d += "  - shadow_bias: 阴影偏移 0.0-1.0\n\n"

        lighting_9d += "光影一致性检查清单 (跨镜头):\n"
        lighting_9d += "  - [ ] 光源方向是否一致? (顺光/侧光/逆光保持)\n"
        lighting_9d += "  - [ ] 色温是否一致? (K 值锁定)\n"
        lighting_9d += "  - [ ] 光比是否一致? (8:1/4:1/2:1 锁定)\n"
        lighting_9d += "  - [ ] 阴影方向是否一致? (不能左跳右)\n"
        lighting_9d += "  - [ ] 软硬是否一致? (软光→软光)\n"
        lighting_9d += "  - [ ] 时间是否一致? (黄昏→黄昏)\n"
        lighting_9d += "  - [ ] 关键道具光影是否一致?\n"
        lighting_9d += "  - [ ] 肤色是否一致? (大银幕上肤色最重要)\n\n"

        # ========== Phase 15 新增: 视觉语言参数化 ==========
        visual_lang = "════════════════════════════════════════\n"
        visual_lang += "【视觉语言参数化系统】Phase 15 核心\n"
        visual_lang += "════════════════════════════════════════\n\n"
        visual_lang += "顶级摄影指导: 用构图传递演员情绪/场景氛围, 创造视觉象征与暗示\n"
        visual_lang += "(AIGC 影视全流程解析 § 能力四 视觉语言力)\n\n"

        visual_lang += "A. 焦段 × 情感映射 (选: " + focal_info.get("cn", focal) + ")\n"
        visual_lang += "  情绪: " + focal_info.get("emotion", "") + "\n"
        visual_lang += "  叙事: " + focal_info.get("narrative", "") + "\n"
        for k, v in FOCAL_LENGTH_VL.items():
            visual_lang += "    - " + v.get("cn", k) + ": " + v.get("emotion", "") + " — " + v.get("narrative", "") + "\n"
        visual_lang += "\n"

        visual_lang += "B. 光圈 × 景深映射 (选: " + aperture_info.get("cn", aperture) + ")\n"
        visual_lang += "  触发: " + aperture_info.get("trigger", "") + "\n"
        for k, v in APERTURE_VL.items():
            visual_lang += "    - " + v.get("cn", k) + ": " + v.get("trigger", "") + "\n"
        visual_lang += "\n"

        visual_lang += "C. 景别 × 叙事功能 (选: " + shot_info + ")\n"
        for k, v in SHOT_SIZE_VL.items():
            visual_lang += "    - " + k + ": " + v + "\n"
        visual_lang += "\n"

        visual_lang += "D. 7 大构图法则 (选: " + comp_info + ")\n"
        for k, v in COMPOSITION_RULES.items():
            visual_lang += "    - " + v + "\n"
        visual_lang += "\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "L5 摄影与剪辑层 (L1-L7 七层 prompt 架构):\n"
        visual_lang += "─" * 50 + "\n"
        visual_lang += "OPTICS: " + focal_info.get("cn", focal) + ", " + aperture_info.get("cn", aperture) + ", " + shot_info + " 景深.\n"
        visual_lang += "CAMERA: 由 " + dp + " 风格决定 — " + DP_8_MASTERS.get(dp, {}).get("composition", "") + "\n"
        visual_lang += "COMPOSITION: " + comp_info + "\n\n"

        visual_lang += "L7 风格约束层:\n"
        visual_lang += "  - 必须坚持 " + focal_info.get("cn", focal) + " 焦段\n"
        visual_lang += "  - 必须坚持 " + aperture_info.get("cn", aperture) + " 光圈\n"
        visual_lang += "  - 整场戏坚持 " + shot_info + " 景别变化范围\n"
        visual_lang += "  - 构图坚持 " + comp_info + "\n"
        visual_lang += "  - 全部 L1-L7 必须保持风格一致\n\n"

        # ========== Phase 15 新增: 60:30:10 色彩法则 ==========
        color_60 = "════════════════════════════════════════\n"
        color_60 += "【60:30:10 色彩法则】Phase 15 (Hell Grind + 斯托拉罗)\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += "AIGC 影视全流程解析 § 环节 15 + 37: 60:30:10 法则严格执行\n\n"

        color_60 += "本场戏 60:30:10 设定:\n\n"
        color_60 += "【主色 60% — 场景/电影主调】\n"
        color_60 += "  设定: " + main_color + "\n"
        color_60 += "  功能: 决定整体情绪, 时代主调, 文化背景\n"
        color_60 += "  执行: 全场戏 60% 面积都是主色\n\n"

        color_60 += "【辅色 30% — 角色/关系】\n"
        color_60 += "  设定: " + sec_color + "\n"
        color_60 += "  功能: 角色服装/关系色彩, 强化人物识别\n"
        color_60 += "  执行: 角色服装/关键道具占 30%\n\n"

        color_60 += "【点缀色 10% — 戏剧时刻】\n"
        color_60 += "  设定: " + acc_color + "\n"
        color_60 += "  功能: 关键道具/情绪点, 戏剧化使用\n"
        color_60 += "  执行: 关键道具/关键瞬间 10%, 极致强调\n\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "色彩心理学 (10 色):\n"
        color_60 += "─" * 50 + "\n"
        for c, m in COLOR_PSYCHOLOGY.items():
            color_60 += "  - " + c + ": " + m + "\n"
        color_60 += "\n"

        color_60 += "经典电影 60:30:10 案例:\n"
        color_60 += "  - 《银翼杀手2049》主色 60% = 黄沙橙黄 + 辅色 30% = 高对比蓝 + 点缀 10% = 红色\n"
        color_60 += "  - 《辛德勒的名单》黑白 + 点缀 10% = 红衣小女孩\n"
        color_60 += "  - 《花样年华》主色 60% = 老上海红绿 + 辅色 30% = 暖黄 + 点缀 10% = 走廊红灯\n"
        color_60 += "  - 《寄生虫》主色 60% = 富人家冷灰白 + 辅色 30% = 公园绿 + 点缀 10% = 山水画血\n\n"

        color_60 += "调色执行 (一级/二级/创意):\n"
        color_60 += "  一级调色 (Primary): 统一主色 60% 色温/对比度/曝光\n"
        color_60 += "  二级调色 (Secondary): 保持辅色 30% 一致, 局部校正 (肤色/道具)\n"
        color_60 += "  创意调色 (Creative): 强化点缀色 10%, 服务情感\n\n"

        # ========== Phase 15 新增: 8 大摄影指导风格 ==========
        dp_style = "════════════════════════════════════════\n"
        dp_style += "【8 大顶级摄影指导风格库】Phase 15\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += "当前选择: " + dp + "\n"
        dp_style += "签名: " + DP_8_MASTERS.get(dp, {}).get("signature", "") + "\n\n"
        dp_style += "─" * 50 + "\n"

        for dp_name, info in DP_8_MASTERS.items():
            dp_style += "【" + dp_name + "】\n"
            dp_style += "  签名: " + info.get("signature", "") + "\n"
            dp_style += "  光影: " + info.get("lighting", "") + "\n"
            dp_style += "  构图: " + info.get("composition", "") + "\n"
            dp_style += "  色彩: " + info.get("color", "") + "\n"
            dp_style += "  触发: " + info.get("trigger", "") + "\n\n"

        # Knowledge Base 决策注入
        if _HAS_KB:
            try:
                _kb_dimension = DIMENSION_DESIGN
                _kb_scene_toolkit = get_scene_toolkit(scene)
                _kb_decision = get_director_decision(director, scene)
                kb_block = "\n" + "=" * 50 + "\n"
                kb_block += "【Knowledge Base — 世界设定维度设计 + 场景工具箱】\n"
                kb_block += "=" * 50 + "\n\n"
                kb_block += "维度设计数据: " + str(_kb_dimension)[:200] + "\n\n"
                kb_block += "场景工具箱 (" + scene[:30] + "): " + str(_kb_scene_toolkit)[:300] + "\n\n"
                kb_block += "导演决策 (" + director + "): " + str(_kb_decision)[:300] + "\n"
                main_output += kb_block
            except Exception:
                pass

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
                lighting_9d = inject_anti_ai_rules(lighting_9d)
                visual_lang = inject_anti_ai_rules(visual_lang)
                color_60 = inject_anti_ai_rules(color_60)
                dp_style = inject_anti_ai_rules(dp_style)
            except Exception:
                pass

        # 第二个输出: 经验矩阵 (Phase 35.9 真正跨导演差异化)
        experience = "【当前导演深度档案 — " + director + "】\n"
        if _dir_profile:
            experience += "  核心风格: " + (_dir_core or "(未命中联网数据)") + "\n"
            experience += "  联网技法:\n"
            for _t in (_dir_tech or [])[:4]:
                experience += "    - " + str(_t) + "\n"
            if _dir_anti_ai:
                experience += "  反 AI 警告: " + _dir_anti_ai[:120] + "\n"
            experience += "  来源: " + str(_dir_profile.get("source", ""))[:80] + "\n"
        else:
            experience += "  (35 导演联网未命中, 退回默认)\n"
        experience += "\n【当前场景深度档案 — " + _scene_name_matched + "】\n"
        if _matched_scene:
            experience += "  氛围: " + (_scene_atmos or "(空)")[:100] + "\n"
            experience += "  联网细节:\n"
            for _d in _scene_details[:4]:
                experience += "    - " + str(_d) + "\n"
            if _scene_ref:
                experience += "  参考片: " + _scene_ref + "\n"
        else:
            experience += "  (100 场景库未匹配)\n"
        experience += "\n【5 维具体化命中 — " + director + "】\n"
        experience += "  时代: " + ",".join(_specs5d.get("era", [])) + "\n"
        experience += "  地点: " + ",".join(_specs5d.get("location", [])) + "\n"
        experience += "  品牌: " + ",".join(_specs5d.get("brand", [])) + "\n"
        experience += "  数字: " + ",".join(_specs5d.get("numbers", [])) + "\n"
        experience += "  物件: " + ",".join(_specs5d.get("objects", [])) + "\n"
        experience += "  raw: " + _specs5d.get("raw_5d_summary", "") + "\n"
        experience += "\n【9 大影视类型 + 5 要素处理】\n"
        experience += inject_genre_9_types() + "\n"
        experience += "【11 维导演控制能力 (人类顶级导演)】\n"
        experience += inject_director_control_11() + "\n"
        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"
        if _addon_segment:
            experience += "\n【灵魂 addon 段消费 — WorldBuildingPro】\n"
            experience += _addon_segment[:300] + "\n"

        return (main_output, lighting_9d, visual_lang, color_60, dp_style, experience)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "WorldBuildingPro": WorldBuildingPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "WorldBuildingPro": "🌍 世界设定 (环节 14) — Phase 15 视觉语言专家重做",
# }
