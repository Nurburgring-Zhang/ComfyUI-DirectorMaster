# -*- coding: utf-8 -*-
"""
ColorGradingPro - 🎨 调色 (环节 15 + 37) — Phase 15 视觉语言专家重做
=======================================================================
环节 15 色彩脚本设计 + 环节 37 调色与色彩统一 — Phase 15 深度重写

Phase 15 核心强化:
1. 60:30:10 色彩法则完整实现 (主色 60% / 辅色 30% / 点缀色 10%)
2. 8 大色彩风格库 (Deakins / Storaro / Doyle / Lubezki / Kaminski / Young / van Hoytema / Szeptycki)
3. 9 维光影设计 + CIE LAB 颜色空间
4. 调色 3 阶段 (一级/二级/创意调色)
5. 视觉语言参数化 (焦段/光圈/景别/构图)
6. 11 维导演控制能力
7. 3 种留白 + 3 运镜法则
8. L1-L7 七层 prompt 架构 (L5 摄影与剪辑层 + L7 风格约束层)
9. 5 要素架构
10. H3 三大字段完整输出
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
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# Phase 5.0: 知识库深度集成
try:
    from knowledge_base import (
        MASTER_CINEMATOGRAPHY, EMOTION_RENDERING,
        get_director_decision, get_emotion_palette,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]


# ============================================================
# Phase 15 新增: 8 大色彩风格 (从 8 大摄影指导提取)
# ============================================================
COLOR_8_MASTERS = {
    "罗杰·迪金斯_Roger_Deakins": {
        "signature": "高对比 + 暖黄 + 冷蓝 + 60:30:10 严格",
        "60_30_10": "主色 60% = 暖黄 + 辅色 30% = 冷蓝 + 点缀色 10% = 高饱和",
        "key_films": ["《银翼杀手2049》", "《1917》", "《007: 大破天幕杀机》", "《老无所依》"],
        "trigger": "现代/纪实/克制/有思想深度的电影",
        "lut_style": "Kodak 2383 + Deakins 蓝黄高对比",
        "emotional_palette": "克制、内敛、思想、距离感",
    },
    "维托里奥·斯托拉罗_Vittorio_Storaro": {
        "signature": "色彩光影叙事 + 60:30:10 严格执行 + 时代色",
        "60_30_10": "每场戏 60:30:10, 时代色 + 政治色 + 心理色",
        "key_films": ["《现代启示录》", "《末代皇帝》", "《蓝色大门》", "《查理四世》"],
        "trigger": "色彩叙事/历史/政治/史诗",
        "lut_style": "Storaro Color Theory 三色轮",
        "emotional_palette": "政治隐喻、时代感、史诗",
    },
    "杜可风_Christopher_Doyle": {
        "signature": "高饱和 + 红绿蓝黄 + 浓烈情绪色 + 雨夜霓虹",
        "60_30_10": "主色 60% = 雨夜蓝/霓虹紫 + 辅色 30% = 鲜红/绿 + 点缀 10% = 暖黄",
        "key_films": ["《重庆森林》", "《春光乍泄》", "《东邪西毒》", "《花样年华》"],
        "trigger": "都市孤独/暧昧/边缘/醉意",
        "lut_style": "Doyle 高饱和霓虹 + 雨水反光",
        "emotional_palette": "都市、孤独、暧昧、醉意",
    },
    "卢贝兹基_Emmanuel_Lubezki": {
        "signature": "高饱和高反差 + 黄金时刻 + 自然",
        "60_30_10": "主色 60% = 黄金时刻暖光 + 辅色 30% = 自然色 + 点缀 10% = 极致高光",
        "key_films": ["《鸟人》", "《地心引力》", "《荒野猎人》", "《生命之树》"],
        "trigger": "时间流动/生命史诗/亲密长镜头",
        "lut_style": "Lubezki 黄金时刻 + 自然饱和",
        "emotional_palette": "生命、时间、亲密、史诗",
    },
    "贾努兹·卡明斯基_Janusz_Kaminski": {
        "signature": "高反差黑白+饱和彩色 + 极端强调色",
        "60_30_10": "主色 60% = 黑白灰 + 辅色 30% = 戏剧高光 + 点缀 10% = 极端红/血",
        "key_films": ["《辛德勒的名单》", "《拯救大兵瑞恩》", "《林肯》", "《西区故事》"],
        "trigger": "历史/战争/戏剧化/史诗",
        "lut_style": "Kaminski 极端反差 + 烟雾染色",
        "emotional_palette": "历史、战争、戏剧、史诗",
    },
    "布拉福德·杨_Bradford_Young": {
        "signature": "极弱光 + 肤色 + 单点强调色 + 几乎单色调",
        "60_30_10": "主色 60% = 暗肤色 + 辅色 30% = 微弱光色 + 点缀 10% = 单点强调",
        "key_films": ["《掠食城市》", "《塞尔玛》", "《到达》", "《黑夜造访》"],
        "trigger": "心理/压迫/梦境/非裔历史",
        "lut_style": "Young 极弱光 + 肤色优先",
        "emotional_palette": "心理、压迫、梦境、神秘",
    },
    "霍伊特·范·霍特玛_Hoyte_van_Hoytema": {
        "signature": "自然饱和度 + 不刻意调色 + 65mm 大画幅真实",
        "60_30_10": "主色 60% = 自然色 + 辅色 30% = 真实饱和 + 点缀 10% = 自然高光",
        "key_films": ["《敦刻尔克》", "《她》", "《星际穿越》", "《信条》"],
        "trigger": "现代史诗/科幻/真实/宽幅",
        "lut_style": "Van Hoytema 自然饱和 + IMAX 65mm",
        "emotional_palette": "真实、史诗、科幻、宽幅",
    },
    "沃伊切赫·斯泽尔曼_Wojciech": {
        "signature": "近黑+血+皮肤色 + 极简三色 + 暗黑歌剧",
        "60_30_10": "主色 60% = 近黑 + 辅色 30% = 皮肤色 + 点缀 10% = 血红",
        "key_films": ["《上帝之鸟》", "《极寒之城》", "《至爱之信》"],
        "trigger": "黑暗/歌剧/心理惊悚/仪式",
        "lut_style": "Szeptycki 极简三色 + 暗黑",
        "emotional_palette": "黑暗、歌剧、仪式、心理",
    },
}

COLOR_8_NAMES = list(COLOR_8_MASTERS.keys())


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

# 经典电影 60:30:10 案例
COLOR_FILMS_60_30_10 = {
    "《银翼杀手2049》": "主色 60% = 黄沙橙黄 + 辅色 30% = 高对比蓝 + 点缀 10% = 红色 (Joi)",
    "《辛德勒的名单》": "黑白 60% + 黑灰 30% + 点缀 10% = 红衣小女孩",
    "《花样年华》": "主色 60% = 老上海红绿 + 辅色 30% = 暖黄 + 点缀 10% = 走廊红灯",
    "《教父》": "主色 60% = 暖棕橙黄 + 辅色 30% = 深红 + 点缀 10% = 黑色",
    "《寄生虫》": "主色 60% = 富人家冷灰白 + 辅色 30% = 公园绿 + 点缀 10% = 山水画血",
    "《Her》": "主色 60% = 暖橙红 + 辅色 30% = 柔粉 + 点缀 10% = 蓝",
    "《千与千寻》": "主色 60% = 暖红汤屋 + 辅色 30% = 蓝白 + 点缀 10% = 父母变猪的灰",
    "《爱乐之城》": "主色 60% = 紫蓝 + 辅色 30% = 暖黄 + 点缀 10% = 红色 (爱情主题)",
    "《现代启示录》": "主色 60% = 橙 (战场) + 辅色 30% = 绿 (丛林) + 点缀 10% = 红 (暴力)",
    "《末代皇帝》": "主色 60% = 黄 (皇帝) + 辅色 30% = 红 (中国) + 点缀 10% = 黑 (死亡)",
    "《2001太空漫游》": "主色 60% = 黑 (太空) + 辅色 30% = 白 (技术) + 点缀 10% = 红 (HAL)",
    "《卧虎藏龙》": "主色 60% = 竹林绿 + 辅色 30% = 月白 + 点缀 10% = 红色衣带",
    "《爱在》三部曲": "主色 60% = 暖黄 (怀旧) + 辅色 30% = 城市色 + 点缀 10% = 红色",
    "《哈利路亚》": "主色 60% = 暖金 + 辅色 30% = 暮色紫 + 点缀 10% = 血红",
}


# ============================================================
# 9 维光影
# ============================================================
LIGHTING_9D_PHASE15 = {
    "1_光源类型": ["自然光 (太阳)", "火光 (蜡烛/壁炉)", "霓虹 (城市)", "路灯", "白炽灯", "荧光灯", "LED 屏幕", "手电筒", "月光", "混合光"],
    "2_方向": {
        "顺光": "主体明亮, 缺乏层次, 商业",
        "侧光": "明暗对比强, 黑色电影, 戏剧",
        "逆光": "剪影/轮廓光, 神秘/浪漫/史诗",
        "顶光": "黑眼圈, 恐怖/审讯",
        "底光": "反自然, 恐怖/超自然",
        "45度_伦勃朗光": "鼻侧三角光, 经典人像",
    },
    "3_强度": ["强光 (戏剧)", "中光 (平衡/日常)", "弱光 (柔和/神秘)"],
    "4_色温": ["warm_3200K", "neutral_5500K", "cool_6500K", "blue_hour_8000K"],
    "5_软硬": ["硬光", "软光", "极软光"],
    "6_比例": ["高调_2_1", "中间调_4_1", "低调_8_1"],
    "7_阴影": ["长阴影", "短阴影", "无阴影"],
    "8_特殊光影": ["丁达尔效应", "剪影", "伦勃朗光", "蝴蝶光", "轮廓光"],
    "9_时间": ["正午", "黄昏", "黄金时刻", "蓝色时刻", "夜晚"],
}


# ============================================================
# 视觉语言参数化
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
    "ELS": "远景 - 人物<10%",
    "LS": "全景 - 人物 15-30%",
    "MLS": "中全景 - 人物 30-50%",
    "MS": "中景 - 人物 40-60%",
    "MCU": "中近景 - 人物 50-70%",
    "CU": "近景 - 面部 60%+",
    "ECU": "特写 - 局部 80%+",
    "ECU_PLUS": "大特写 - 微距 0.5-2秒",
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


class ColorGradingPro:
    """
    🎨 调色 (环节 15 色彩脚本 + 环节 37 调色统一) — Phase 15 视觉语言专家重做
    严禁模板实现, 真正动态生成 60:30:10 色彩脚本 + 8 大色彩风格
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),

                # Phase 15 新增: 8 大色彩风格
                "色彩风格": (COLOR_8_NAMES, {"default": "罗杰·迪金斯_Roger_Deakins"}),

                # Phase 15 新增: 视觉语言参数化
                "焦段": (list(FOCAL_LENGTH_VL.keys()), {"default": "35mm_cinematic"}),
                "光圈": (list(APERTURE_VL.keys()), {"default": "T2.8_cinematic"}),
                "景别": (list(SHOT_SIZE_VL.keys()), {"default": "MS"}),
                "构图法则": (list(COMPOSITION_RULES.keys()), {"default": "rule_of_thirds"}),

                # Phase 15 核心: 60:30:10
                "主色_60": ("STRING", {"default": "暖橙黄 #D4A24C (主色 60% — 时代主调, 1998 年东北暖光)"}),
                "辅色_30": ("STRING", {"default": "老红 #8B2E1F (辅色 30% — 角色服装/关系, 父亲的红毛衣)"}),
                "点缀色_10": ("STRING", {"default": "老白绿 #8E9F7E (点缀色 10% — 戏剧时刻, 缝纫机/碗)"}),

                # 调色 3 阶段
                "一级调色": (["统一色温/对比度/曝光", "相邻镜头无缝", "整体色温锁定"], {"default": "统一色温/对比度/曝光"}),
                "二级调色": (["肤色优先", "关键道具色校正", "局部 HSL 调整"], {"default": "肤色优先"}),
                "创意调色": (["强化点缀色 10%", "服务情感氛围", "色彩变化轨迹"], {"default": "服务情感氛围"}),

                # 9 维光影
                "光源类型": (LIGHTING_9D_PHASE15["1_光源类型"], {"default": "自然光 (太阳)"}),
                "光影方向": (list(LIGHTING_9D_PHASE15["2_方向"].keys()), {"default": "侧光"}),
                "色温": (LIGHTING_9D_PHASE15["4_色温"], {"default": "warm_3200K"}),
                "比例": (LIGHTING_9D_PHASE15["6_比例"], {"default": "中间调_4_1"}),
                "时间": (LIGHTING_9D_PHASE15["9_时间"], {"default": "黄昏"}),

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
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "colorgradingpro_h3_prompt",  # H3 三大字段
        "color_60_30_10_script",     # 60:30:10 完整脚本 (Phase 15 核心)
        "color_8_masters_style",     # 8 大色彩风格 (Phase 15)
        "color_grading_3stage",      # 3 阶段调色 (一级/二级/创意)
        "lighting_9d_design",        # 9 维光影
        "experience_matrix",         # 经验矩阵
    )
    FUNCTION = "build_color"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_color(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "", "", "", "")

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
        color_style = _str(kwargs.get("色彩风格"), "罗杰·迪金斯_Roger_Deakins")
        focal = _str(kwargs.get("焦段"), "35mm_cinematic")
        aperture = _str(kwargs.get("光圈"), "T2.8_cinematic")
        shot_size = _str(kwargs.get("景别"), "MS")
        composition = _str(kwargs.get("构图法则"), "rule_of_thirds")
        main_color = _str(kwargs.get("主色_60"), "")
        sec_color = _str(kwargs.get("辅色_30"), "")
        acc_color = _str(kwargs.get("点缀色_10"), "")
        stage_1 = _str(kwargs.get("一级调色"), "统一色温/对比度/曝光")
        stage_2 = _str(kwargs.get("二级调色"), "肤色优先")
        stage_3 = _str(kwargs.get("创意调色"), "服务情感氛围")
        light_source = _str(kwargs.get("光源类型"), "自然光 (太阳)")
        light_dir = _str(kwargs.get("光影方向"), "侧光")
        light_temp = _str(kwargs.get("色温"), "warm_3200K")
        light_ratio = _str(kwargs.get("比例"), "中间调_4_1")
        light_time = _str(kwargs.get("时间"), "黄昏")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # 节点专属: 领域能力
        domain_name = "调色/色彩脚本"
        domain_focus = "60:30:10 色彩法则 + 8 大色彩风格 + 9 维光影 + 3 阶段调色 (Phase 15)"
        h3_special = "60:30:10 严格执行 (主色/辅色/点缀色) + CIE LAB 颜色空间 + 跨镜头色彩一致性"
        director_specifics = "斯托拉罗色彩叙事 / 卡明斯基极端反差 / 王家卫红绿黄 / 奉俊昊灰冷 vs 金黄 / 塔可夫斯基金焦黄水气"
        extra_inject = "8 大色彩风格 LUT (Kodak 2383 / Fuji 3510 / Storaro 三色轮 / Doyle 霓虹 / Young 极弱光) + 调色 3 阶段 (一级/二级/创意) + 11 维导演控制"

        director_motion_pref = "Static Shot + Push In 缓推"

        style = "Cinematic, live-action, 35mm film grain"

        # Shot 1 (Phase 15 增强: 60:30:10 嵌入 H3)
        focal_info = FOCAL_LENGTH_VL.get(focal, {})
        aperture_info = APERTURE_VL.get(aperture, {})
        shot_info = SHOT_SIZE_VL.get(shot_size, "")
        comp_info = COMPOSITION_RULES.get(composition, "")
        color_master = COLOR_8_MASTERS.get(color_style, {})

        shot_1 = "a medium-wide shot establishes the scene - " + scene + ". L5 摄影与剪辑层: " + focal_info.get("cn", focal) + " lens, " + aperture_info.get("cn", aperture) + " aperture, " + shot_info + ", " + comp_info + " composition. L7 风格约束层: 60:30:10 color script — dominant " + main_color + " (60%), secondary " + sec_color + " (30%), accent " + acc_color + " (10%). 9 维光影: " + light_source + " from " + light_dir + " at " + light_temp + ", " + light_ratio + " key-to-fill, " + light_time + ". The director " + director + " intends: " + intent_feel + ". The " + props + " sit on the table. Color grading: " + color_style + " style — " + color_master.get("signature", "") + "."

        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        shots = [
            "[Shot 2] At 00:03.500, the camera cuts to a medium close-up of the main character's face. " + format_shot_motion("Push In", "small", "slow") + " on the eyes, revealing a " + subtext + ". The color palette stays within 60:30:10, the " + acc_color + " accent reads against the " + main_color + " background.",
            "[Shot 3] At 00:08.000, the camera cuts to a close-up of the character's hands holding the " + first_prop + ". The skin tone is preserved per the 60:30:10 rule. (S1) speaks a short line in a " + mood + " voice, the words held back (subtext-driven).",
            "[Shot 4] At 00:15.000, the camera cuts to an over-the-shoulder shot. " + format_shot_motion("Push In", "small", "slow") + " toward the other character. The " + sec_color + " secondary color frames the relationship.",
            "[Shot 5] At 00:22.000, the camera holds a static shot on the wider frame. Both characters remain silent for 5-10 seconds. The director's intent: " + intent_feel + ". Per the silence formula: one short line, 3 seconds of silence, a subtle micro-expression shift, an action that changes the relationship, 5 seconds of breathing room.",
            "[Shot 6] At 00:27.000, the camera holds for 3 seconds, allowing the audience to process. The " + acc_color + " accent on the " + last_prop + " catches the eye. End of shot.",
        ]

        # V13.4: 声景场景驱动 — 由场景/情绪生成, 不再硬编码雨夜厨房
        soundscape = ("Ambient sound drawn from the scene: " + scene + ". "
                      "The dominant room tone of the space, a subtle signature sound of the " + props + ", "
                      "and the characters' restrained breathing. Mood: " + mood + ". "
                      "Sparse, diegetic only — no non-diegetic filler.")
        music = "Sparse piano notes at a slow tempo, joined by sustained low strings that gradually increase in volume before fading out."

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 5 要素
        data_summary = "1161 部 director_view + 63 导演 + 20 集群 + 191 反 AI + 12 理论 + 14 短剧 + 8 色彩风格 + 9 维光影 + 60:30:10"
        context_brief = "类型=" + genre + ", 导演=" + director + ", 色彩=" + color_style + ", 任务=" + task_type + ", 场景=" + scene[:50] + "..., 情绪=" + mood
        skill_harness = "60:30:10 色彩脚本 + 8 色彩风格 + 9 维光影 + 3 阶段调色 + 11 维导演控制 + 4 维美术 + L1-L7 七层"
        experience_matrix = "Hell Grind + 真实短剧实战 + 斯托拉罗色彩理论 + 卡兹克 2.5 SFT 重定义 + 卡明斯基极端反差"
        ai_deep = "60:30:10 严格执行 + 反 AI 词表 + 10 铁律 + 调色 3 阶段 + 视觉语言参数化 + 8 色彩风格"

        elements_block = inject_5_elements(data_summary, context_brief, skill_harness, experience_matrix, ai_deep)

        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害",
            "主题": mood,
            "留白": "想说但没说出口 - " + props,
        }
        intent_block = inject_director_intent(intent_5d)
        director_control = inject_director_control_11()
        h3_rules = inject_h3_rules_11()

        timeline_30s_lines = "\n".join(["  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc for (ts, te, stage, desc) in SCENE_UNIT_30S])

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
                    "【灵魂核心 - 调色驱动 (Phase 17.6)】\n"
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
        main_output += "【" + "ColorGradingPro" + "】Phase 15 视觉语言专家重做 - 环节 15 + 37 调色\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【色彩风格】" + color_style + " - 签名: " + color_master.get("signature", "") + "\n"
        main_output += "【调色 3 阶段】一级: " + stage_1 + " / 二级: " + stage_2 + " / 创意: " + stage_3 + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "H3 三大字段 (MiniMax-H3, Phase 15 60:30:10 增强)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += h3_prompt + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "30 秒场景单元 6 段式 (卡兹克)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "【节点专属: " + domain_name + "】Phase 15\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "  焦点: " + domain_focus + "\n"
        main_output += "  H3 特殊: " + h3_special + "\n"
        main_output += "  导演专项: " + director_specifics + "\n"
        main_output += "  注入经验: " + extra_inject + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "导演意图 5 维\n"
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

        # ========== Phase 15 核心: 60:30:10 色彩脚本完整版 ==========
        color_60 = "════════════════════════════════════════\n"
        color_60 += "【60:30:10 色彩法则完整脚本】Phase 15 核心\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += "AIGC 影视全流程解析 § 环节 15 + 37: 60:30:10 法则严格执行\n"
        color_60 += "(Hell Grind + 斯托拉罗 + 8 大色彩风格 + CIE LAB)\n"
        color_60 += "当前色彩风格: " + color_style + " — " + color_master.get("signature", "") + "\n\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "本场戏 60:30:10 设定\n"
        color_60 += "─" * 50 + "\n\n"

        color_60 += "【主色 60% — 场景/电影主调】\n"
        color_60 += "  设定: " + main_color + "\n"
        color_60 += "  功能: 决定整体情绪, 时代主调, 文化背景\n"
        color_60 += "  心理学: 暖色 = 亲密/怀旧, 冷色 = 孤独/超自然\n"
        color_60 += "  执行: 全场戏 60% 面积都是主色\n"
        color_60 += "  调色: 一级调色统一主色 60% 的色温/对比度/曝光\n\n"

        color_60 += "【辅色 30% — 角色/关系】\n"
        color_60 += "  设定: " + sec_color + "\n"
        color_60 += "  功能: 角色服装/关系色彩, 强化人物识别\n"
        color_60 += "  心理学: 角色色彩 = 人物性格 + 关系网络\n"
        color_60 += "  执行: 角色服装/关键道具占 30%\n"
        color_60 += "  调色: 二级调色保持辅色 30% 一致, 局部校正\n\n"

        color_60 += "【点缀色 10% — 戏剧时刻】\n"
        color_60 += "  设定: " + acc_color + "\n"
        color_60 += "  功能: 关键道具/情绪点, 戏剧化使用\n"
        color_60 += "  心理学: 全片 1-3 次出现, 观众会记住\n"
        color_60 += "  执行: 关键道具/关键瞬间 10%, 极致强调\n"
        color_60 += "  调色: 创意调色强化点缀色 10%, 服务情感\n\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "色彩心理学 (10 色)\n"
        color_60 += "─" * 50 + "\n"
        for c, m in COLOR_PSYCHOLOGY.items():
            color_60 += "  - " + c + ": " + m + "\n"
        color_60 += "\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "经典电影 60:30:10 案例 (斯托拉罗/Hell Grind 验证)\n"
        color_60 += "─" * 50 + "\n"
        for film, desc in COLOR_FILMS_60_30_10.items():
            color_60 += "  - " + film + ": " + desc + "\n"
        color_60 += "\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "调色 3 阶段 (一级/二级/创意)\n"
        color_60 += "─" * 50 + "\n\n"

        color_60 += "【一级调色 Primary Color Correction】\n"
        color_60 += "  目标: 统一主色 60% 的色温/对比度/曝光\n"
        color_60 += "  本场: " + stage_1 + "\n"
        color_60 += "  检查清单:\n"
        color_60 += "    - [ ] 色温是否一致?\n"
        color_60 += "    - [ ] 对比度是否一致?\n"
        color_60 += "    - [ ] 曝光是否一致?\n"
        color_60 += "    - [ ] 饱和度是否一致?\n"
        color_60 += "    - [ ] 相邻镜头是否可以无缝衔接?\n\n"

        color_60 += "【二级调色 Secondary Color Correction】\n"
        color_60 += "  目标: 保持辅色 30% 一致, 局部校正\n"
        color_60 += "  本场: " + stage_2 + "\n"
        color_60 += "  检查清单:\n"
        color_60 += "    - [ ] 肤色是否正确? (大银幕上肤色最重要)\n"
        color_60 += "    - [ ] 关键道具颜色是否正确?\n"
        color_60 += "    - [ ] 特定区域的色彩是否符合设计?\n"
        color_60 += "    - [ ] 点缀色是否突出?\n\n"

        color_60 += "【创意调色 Creative Grading】\n"
        color_60 += "  目标: 强化点缀色 10%, 服务情感\n"
        color_60 += "  本场: " + stage_3 + "\n"
        color_60 += "  检查清单:\n"
        color_60 += "    - [ ] 场景的情感氛围是否达成?\n"
        color_60 += "    - [ ] 色彩是否服务于叙事?\n"
        color_60 += "    - [ ] 光影是否增强情感?\n"
        color_60 += "    - [ ] 色彩变化是否平滑?\n\n"

        color_60 += "─" * 50 + "\n"
        color_60 += "调色与场景情感的关系 (AIGC 影视全流程解析)\n"
        color_60 += "─" * 50 + "\n"
        color_60 += "  - 温暖/希望: 暖色 (橙/黄), 中高对比, 高饱和, 正常曝光\n"
        color_60 += "  - 阴郁/绝望: 冷色 (蓝/灰), 低对比, 低饱和, 欠曝\n"
        color_60 += "  - 紧张/悬疑: 绿色调, 高对比, 中饱和, 欠曝\n"
        color_60 += "  - 浪漫/爱情: 暖色, 低对比, 中高饱和, 过曝 (柔和)\n"
        color_60 += "  - 暴力/激烈: 红色调, 极高对比, 高饱和, 正常曝光\n"
        color_60 += "  - 孤独/分离: 冷色, 低对比, 低饱和, 欠曝\n\n"

        # ========== Phase 15 新增: 8 大色彩风格 ==========
        color_8 = "════════════════════════════════════════\n"
        color_8 += "【8 大色彩风格库】Phase 15\n"
        color_8 += "════════════════════════════════════════\n\n"
        color_8 += "当前选择: " + color_style + "\n"
        color_8 += "签名: " + color_master.get("signature", "") + "\n"
        color_8 += "60:30:10: " + color_master.get("60_30_10", "") + "\n"
        color_8 += "LUT: " + color_master.get("lut_style", "") + "\n"
        color_8 += "情绪色板: " + color_master.get("emotional_palette", "") + "\n\n"
        color_8 += "─" * 50 + "\n"

        for cs_name, info in COLOR_8_MASTERS.items():
            color_8 += "【" + cs_name + "】\n"
            color_8 += "  签名: " + info.get("signature", "") + "\n"
            color_8 += "  60:30:10: " + info.get("60_30_10", "") + "\n"
            color_8 += "  代表作: " + " / ".join(info.get("key_films", [])) + "\n"
            color_8 += "  触发: " + info.get("trigger", "") + "\n"
            color_8 += "  LUT: " + info.get("lut_style", "") + "\n"
            color_8 += "  情绪: " + info.get("emotional_palette", "") + "\n\n"

        # ========== Phase 15 新增: 3 阶段调色方法论 ==========
        grading_3stage = "════════════════════════════════════════\n"
        grading_3stage += "【3 阶段调色方法论】Phase 15 核心\n"
        grading_3stage += "════════════════════════════════════════\n\n"
        grading_3stage += "AIGC 影视全流程解析 § 环节 37 调色与色彩统一\n"
        grading_3stage += "原则一: 调色先统一 (每代生成自带内置调色, 调色师是精修, 不是发明)\n"
        grading_3stage += "原则二: 60:30:10 法则严格执行\n"
        grading_3stage += "原则三: 肤色为王 (大银幕上, 肤色是最重要的)\n\n"

        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "【阶段 1: 一级调色 (Primary)】\n"
        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "目标: 统一相邻镜头的整体色温、对比度、曝光\n"
        grading_3stage += "本场执行: " + stage_1 + "\n\n"
        grading_3stage += "技术方法:\n"
        grading_3stage += "  - 色温校正: 锁定主色 60% 的 K 值\n"
        grading_3stage += "  - 对比度: 锁定光比 (" + light_ratio + ")\n"
        grading_3stage += "  - 曝光: 锁定整体亮度\n"
        grading_3stage += "  - 饱和度: 锁定主饱和度\n\n"
        grading_3stage += "检查清单:\n"
        grading_3stage += "  - [ ] 色温是否一致?\n"
        grading_3stage += "  - [ ] 对比度是否一致?\n"
        grading_3stage += "  - [ ] 曝光是否一致?\n"
        grading_3stage += "  - [ ] 饱和度是否一致?\n"
        grading_3stage += "  - [ ] 相邻镜头是否可以无缝衔接?\n\n"

        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "【阶段 2: 二级调色 (Secondary)】\n"
        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "目标: 选择性调整画面中的特定元素 (肤色/特定道具/特定区域)\n"
        grading_3stage += "本场执行: " + stage_2 + "\n\n"
        grading_3stage += "技术方法:\n"
        grading_3stage += "  - 肤色优先: 锁定肤色范围, 优先保证肤色准确\n"
        grading_3stage += "  - 关键道具: 锁定关键道具颜色 (辅色 30%)\n"
        grading_3stage += "  - 局部 HSL: 选择性调整画面特定区域\n"
        grading_3stage += "  - 窗口/限定: 用 HSL 二级窗口圈定\n\n"
        grading_3stage += "检查清单:\n"
        grading_3stage += "  - [ ] 肤色是否正确? (大银幕上肤色最重要)\n"
        grading_3stage += "  - [ ] 关键道具颜色是否正确?\n"
        grading_3stage += "  - [ ] 特定区域的色彩是否符合设计?\n"
        grading_3stage += "  - [ ] 点缀色是否突出?\n\n"

        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "【阶段 3: 创意调色 (Creative)】\n"
        grading_3stage += "─" * 50 + "\n"
        grading_3stage += "目标: 为场景营造特定的情感氛围\n"
        grading_3stage += "本场执行: " + stage_3 + "\n\n"
        grading_3stage += "技术方法:\n"
        grading_3stage += "  - 强化点缀色 10%: 用 HSL/曲线强化关键颜色\n"
        grading_3stage += "  - 服务情感: 色彩变化服务情感 (高潮用暖, 危机用冷)\n"
        grading_3stage += "  - 色彩变化轨迹: 暖→冷 或 冷→暖, 跟随角色弧光\n"
        grading_3stage += "  - LUT 应用: " + color_master.get("lut_style", "") + "\n\n"
        grading_3stage += "检查清单:\n"
        grading_3stage += "  - [ ] 场景的情感氛围是否达成?\n"
        grading_3stage += "  - [ ] 色彩是否服务于叙事?\n"
        grading_3stage += "  - [ ] 光影是否增强情感?\n"
        grading_3stage += "  - [ ] 色彩变化是否平滑?\n\n"

        # ========== Phase 15 新增: 9 维光影 ==========
        lighting_9d = "════════════════════════════════════════\n"
        lighting_9d += "【9 维光影设计】Phase 15\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += "AIGC 影视全流程解析 § 环节 16 + 37: 光影语言设计 + 调色\n"
        lighting_9d += "(DP " + color_style + " 风格 + CIE LAB 9 维)\n\n"

        lighting_9d += "本场戏 9 维光影设定:\n\n"
        lighting_9d += "  【1. 光源类型】 " + light_source + "\n"
        lighting_9d += "  【2. 方向】 " + light_dir + "\n"
        lighting_9d += "  【4. 色温】 " + light_temp + "\n"
        lighting_9d += "  【6. 比例】 " + light_ratio + "\n"
        lighting_9d += "  【9. 时间】 " + light_time + "\n\n"

        lighting_9d += "调色 + 光影一致性:\n"
        lighting_9d += "  - [ ] 光源方向是否一致?\n"
        lighting_9d += "  - [ ] 色温是否一致? (K 值锁定)\n"
        lighting_9d += "  - [ ] 光比是否一致? (" + light_ratio + ")\n"
        lighting_9d += "  - [ ] 阴影方向是否一致?\n"
        lighting_9d += "  - [ ] 时间是否一致? (" + light_time + ")\n"
        lighting_9d += "  - [ ] 肤色是否一致? (大银幕上肤色最重要)\n\n"

        lighting_9d += "视觉语言参数 (L5 摄影与剪辑层):\n"
        lighting_9d += "  - 焦段: " + focal_info.get("cn", focal) + " — " + focal_info.get("emotion", "") + "\n"
        lighting_9d += "  - 光圈: " + aperture_info.get("cn", aperture) + " — " + aperture_info.get("trigger", "") + "\n"
        lighting_9d += "  - 景别: " + shot_info + "\n"
        lighting_9d += "  - 构图: " + comp_info + "\n\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
                color_60 = inject_anti_ai_rules(color_60)
                color_8 = inject_anti_ai_rules(color_8)
                grading_3stage = inject_anti_ai_rules(grading_3stage)
                lighting_9d = inject_anti_ai_rules(lighting_9d)
            except Exception:
                pass

        # Phase 5.0: 知识库调色决策层
        if _HAS_KB:
            director_clean = director.split("(")[0].strip() if "(" in director else director.strip()
            kb_decision = get_director_decision(director_clean, scene)
            soul_fused = locals().get('fused', {})
            emotion_key = soul_fused.get("emotions", ["loneliness"])[0] if isinstance(soul_fused, dict) and isinstance(soul_fused.get("emotions"), list) else "loneliness"
            kb_emotion = get_emotion_palette(emotion_key, soul_fused.get("intensity", 0.5) if isinstance(soul_fused, dict) else 0.5)
            kb_lines = ["\n═══ 知识库调色决策层 ═══"]
            if kb_decision.get("style"):
                ds = kb_decision["style"]
                kb_lines.append(f"【导演色彩签名】{ds.get('cn', '')}")
                kb_lines.append(f"  色彩: {ds.get('color_palette', '')[:200]}")
                kb_lines.append(f"  视觉风格: {ds.get('visual_style', '')[:200]}")
            color_data = MASTER_CINEMATOGRAPHY.get("color_psychology", {})
            if color_data and kb_emotion.get("color"):
                kb_lines.append(f"【情绪色彩心理】{kb_emotion['color']}")
            if kb_emotion.get("lighting"):
                kb_lines.append(f"【情绪光影】{kb_emotion['lighting']}")
            main_output += "\n".join(kb_lines) + "\n"

        experience = "【20 导演集群实战经验】\n\n"
        for d in DIRECTORS_20:
            experience += "  - " + d + "\n"
        experience += "\n【9 大影视类型 + 5 要素处理】\n"
        experience += inject_genre_9_types() + "\n"
        experience += "【11 维导演控制能力 (人类顶级导演)】\n"
        experience += inject_director_control_11() + "\n"
        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        return (main_output, color_60, color_8, grading_3stage, lighting_9d, experience)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ColorGradingPro": ColorGradingPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ColorGradingPro": "🎨 调色 (环节 15 + 37) — Phase 15 视觉语言专家重做",
# }
