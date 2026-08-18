# -*- coding: utf-8 -*-
"""
CostumePropSetPro - 服化道专家节点 (环节 19) — L5 导演级深度重写
====================================================
服化道 = 服装 (Costume) + 化妆 (Makeup) + 道具 (Prop) + 场景 (Set)

真正的服化道专家节点, 不是复制粘贴模板:
1. 角色服装设计系统: 服装作为角色弧光的镜像 (干净->磨损->破碎->重生)
2. 道具叙事系统: 每个道具必须有叙事功能 (象征/线索/转折/情感锚)
3. 9D 材质-光响应: 棉/丝/皮/金属/玻璃/木/石/陶 在不同光照下的视觉行为
4. 场景设计: 空间规划 + 时代适配 + 60:30:10 色彩法则
5. 导演个性化服化道方法论 (王家卫26套旗袍/奉俊昊整洁度=阶层/塔可夫斯基自然材质)
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

# 导演数据中枢
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile, SCENE_DATABASE_100, QUOTES_30,
        get_director, get_scene,
    )
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# ============================================================
# 服化道专属: 9D 材质-光响应系统
# ============================================================
MATERIAL_LIGHT_9D = {
    "棉布 (Cotton)": {
        "漫反射": "soft diffuse scattering, no specular peak",
        "皱褶阴影": "micro-shadow in creases, soft penumbra edges",
        "吸光性": "absorbs 60-70% incident light, matte finish",
        "aging": "fading at fold lines, thinning at elbows/collar",
        "触感词": "a worn softness, slightly pilling at the seams",
        "色温响应": "warm light deepens earth tones; cool light grays out color",
    },
    "丝绸 (Silk)": {
        "漫反射": "high specular, directional sheen along warp threads",
        "光泽变化": "color shifts 10-15 degrees with viewing angle (iridescence)",
        "褶皱光影": "sharp highlight ridges, deep shadow valleys in folds",
        "aging": "yellowing at armholes, friction wear at seat, snagged pulls",
        "触感词": "liquid drape, catches light like a slow river",
        "色温响应": "warm light ignites gold undertones; cool light reveals blue-violet shifts",
    },
    "皮革 (Leather)": {
        "漫反射": "deep color saturation, semi-glossy surface",
        "纹理响应": "side-light reveals pore texture and grain direction",
        "aging": "patina darkening, crease whitening, scratch accumulation",
        "触感词": "stiff new, supple aged, cracked neglected",
        "气味暗示": "the camera cannot smell, but the character reacts to the scent of old leather",
        "色温响应": "warm light enriches brown tones; overcast flattens to near-black",
    },
    "金属 (Metal)": {
        "漫反射": "near-zero diffuse, high specular reflectance (80-95%)",
        "环境映射": "reflects surrounding environment in distorted curves",
        "锈蚀层次": "base metal -> oxide layer -> patina -> flaking",
        "声音提示": "ring, clink, scrape - each metal has a pitch",
        "触感词": "cold to touch, weight felt in the wrist",
        "色温响应": "daylight: neutral reflection; tungsten: warm gold; LED: cool blue-white",
    },
    "玻璃 (Glass)": {
        "折射": "IOR 1.5, bends background by 15-20% depending on thickness",
        "焦散": "casts bright caustic patterns on surfaces when backlit",
        "透明梯度": "clear center, slight green tint at edges (soda-lime glass)",
        "aging": "scratches, chips, cloudiness, water stains",
        "触感词": "smooth, cold, fragile - handle with visible care",
        "色温响应": "transmits and slightly warms tungsten; cools daylight at edges",
    },
    "木材 (Wood)": {
        "漫反射": "warm diffuse, visible grain direction",
        "纹理响应": "cross-light reveals annual rings and knots",
        "aging": "darkening, splitting, worm holes, polish patina",
        "触感词": "warm to palm, grain felt under fingertips",
        "气味暗示": "cedar = sharp; oak = earthy; pine = resinous",
        "色温响应": "warm light enhances honey tones; fluorescent makes it look gray-green",
    },
    "石材 (Stone)": {
        "漫反射": "rough diffuse, micro-shadow in pores",
        "纹理响应": "raking light reveals chisel marks and weathering",
        "aging": "erosion, moss growth, water stains, mineral deposits",
        "触感词": "cold, heavy, rough or polished smooth",
        "色温响应": "dawn/dusk warm light turns gray stone golden; noon harsh light flattens it",
    },
    "陶瓷 (Ceramic)": {
        "漫反射": "glazed: specular sheen; unglazed: matte absorptive",
        "光泽变化": "glaze reflects point lights as sharp highlights",
        "aging": "crazing (fine crack network), chips, kiln marks",
        "触感词": "cool, smooth (glazed) or gritty (unglazed), audible tap",
        "色温响应": "glaze reflects light source color faithfully; unglazed absorbs and warms",
    },
    "织物混合 (Blended)": {
        "漫反射": "varies by weave: tweed = rough; jersey = smooth drape",
        "aging": "pilling, stretching, color transfer at contact points",
        "触感词": "depends on blend: wool-cotton = warm-scratchy; silk-linen = cool-crisp",
        "色温响应": "inherits dominant fiber's response, modulated by secondary",
    },
}

# ============================================================
# 导演专属服化道方法论
# ============================================================
DIRECTOR_COSTUME_PHILOSOPHY = {
    "王家卫": {
        "method": "旗袍作为心理地图: 26套旗袍, 每套颜色/花纹=一种心境状态",
        "costume_arc": "色彩从暖(爱意)到冷(疏离), 花纹从繁复(热恋)到素净(放手)",
        "prop_rule": "凤梨罐头保质期=感情期限; 手绢=未说出口的话",
        "set_color": "霓虹蓝绿主调(60%), 暗红木家具(30%), 琥珀灯光点缀(10%)",
        "material_pref": "丝绸 (Silk) 为主, 辅以棉布内衬表达私密",
        "detail": "旗袍领口的磨损程度=这段关系被消耗了多少",
    },
    "奉俊昊": {
        "method": "衣服整洁度=社会阶层的精确标尺",
        "costume_arc": "富人: 始终挺括免烫; 穷人: 从干净到发霉, 回不去了",
        "prop_rule": "地下室气味(角色闻到)=阶级的物理存在; 楼梯=阶层分界线",
        "set_color": "地下室冷绿(60%), 米色墙(30%), 手机屏幕冷白(10%)",
        "material_pref": "棉布 (Cotton) 富人用精梳棉, 穷人用粗纺; 对比即阶级",
        "detail": "富人的白衬衫无一丝皱褶, 穷人的T恤领口已经松了",
    },
    "塔可夫斯基": {
        "method": "自然材质=时间的容器, 人工材质=精神的干扰",
        "costume_arc": "从新衣到旧衣不是磨损, 是角色接受了时间的重量",
        "prop_rule": "水=记忆; 蜡烛=信仰; 旧书=知识的重量; 火=牺牲",
        "set_color": "暗绿苔藓(60%), 金黄烛光(30%), 黑色阴影(10%)",
        "material_pref": "棉麻 (Cotton/Linen) 天然纤维, 拒绝化纤",
        "detail": "衣服上有真实的雨水痕迹, 不是喷的, 是等到真下雨才拍",
    },
    "诺兰": {
        "method": "服装是时间线的标记, 同一套衣服=同一时间层",
        "costume_arc": "梦境层级不同, 西装领口从紧到松, tie从正到歪",
        "prop_rule": "手表=时间; 陀螺=现实检验; 面具=身份",
        "set_color": "冷蓝金属(60%), 黑色混凝土(30%), 橙黄灯光(10%)",
        "material_pref": "金属 (Metal) + 精纺毛料, 冷硬质感",
        "detail": "Cobb的西装在每一层梦境中的皱褶不一样, 越深越皱",
    },
    "是枝裕和": {
        "method": "衣服是日常生活的证据, 不是设计过的戏服",
        "costume_arc": "没有刻意弧线, 就是穿旧了, 像真正的家人一样",
        "prop_rule": "便当=爱的具体形状; 旧物=记忆的承载",
        "set_color": "暖木色(60%), 米白墙(30%), 绿植点缀(10%)",
        "material_pref": "棉布 (Cotton) 家常面料, 柔软被洗过很多次的质感",
        "detail": "孩子的T恤太大了一号, 是哥哥/姐姐穿过的",
    },
    "黑泽明": {
        "method": "铠甲/和服是角色社会身份的宣言",
        "costume_arc": "从完整铠甲到残破铠甲=从秩序到混乱",
        "prop_rule": "武士刀=荣誉与生死; 旗=忠诚; 雨=命运洗礼",
        "set_color": "黑白灰(60%), 土黄泥色(30%), 鲜红旗帜(10%)",
        "material_pref": "金属 (Metal) 铠甲 + 棉 (Cotton) 内衬 + 丝绸 (Silk) 贵族",
        "detail": "足轻的草鞋磨穿底了, 武士的铠甲有修补痕迹",
    },
    "侯孝贤": {
        "method": "衣服就是那个年代普通人真正穿的, 不多不少",
        "costume_arc": "季节变化带来的自然换衣, 不是戏剧性的服装变化",
        "prop_rule": "旧屋=记忆; 风=时间; 田=根",
        "set_color": "自然绿(60%), 木色(30%), 天空蓝(10%)",
        "material_pref": "棉麻 (Cotton/Linen) 闽南衫/台湾乡间面料",
        "detail": "领子有点卷了, 袖口有点脱线, 但很干净",
    },
    "周星驰": {
        "method": "服装是笑料的一部分, 越正经的衣服配越荒诞的行为",
        "costume_arc": "破烂->更破烂->突然西装(反差笑点)->最终不在乎穿什么",
        "prop_rule": "包租婆的拖鞋=权力; 破烂内裤=小人物尊严",
        "set_color": "高饱和暖色(60%), 脏旧墙(30%), 霓虹(10%)",
        "material_pref": "棉布 (Cotton) 最便宜的那种, 越cheap越真实",
        "detail": "领口的污渍有层次: 汗渍(底层)+酱油(中层)+新洒的水(表层)",
    },
    "贾樟柯": {
        "method": "衣服是时代变迁的考古证据",
        "costume_arc": "90年代山西: 假名牌->真地摊->打工服->城市便装",
        "prop_rule": "摩托车=自由的幻觉; 烟=打发时间; 手机=时代标记",
        "set_color": "灰蓝(60%), 砖红旧墙(30%), 锈色(10%)",
        "material_pref": "混合材质: 化纤+棉, 典型中国小镇面料",
        "detail": "毛衣起球但还在穿, 皮带扣是集市上5块钱买的",
    },
}

# ============================================================
# 道具叙事功能分类
# ============================================================
PROP_NARRATIVE_FUNCTIONS = {
    "象征 (Symbol)": {
        "desc": "道具承载超越物理存在的隐喻意义",
        "examples": "《公民凯恩》玫瑰花蕾=失去的童年; 《2001》黑石=进化",
        "rule": "每场戏最多1个象征道具, 多了就稀释",
        "shot_treatment": "首次出现: 用特写/浅景深从背景中'浮'出来; 反复出现: 每次构图位置不同, 暗示意义演变",
    },
    "线索 (Clue)": {
        "desc": "道具为后续剧情埋伏笔, 观众二刷才注意到",
        "examples": "《寄生虫》石头=执念; 《信条》逆向子弹孔墙=时间方向",
        "rule": "线索道具第一次出现时不做任何强调, 让它自然存在于画面中",
        "shot_treatment": "首次: 景深内但不聚焦; 揭示时: 同一道具同一角度, 但这次是主体",
    },
    "转折 (Pivot)": {
        "desc": "道具的状态变化直接触发情节转折",
        "examples": "《教父》枪藏在马桶后面; 《老无所依》硬币正反面",
        "rule": "转折道具的'变化'(碎/开/关/翻转)必须有声音设计配合",
        "shot_treatment": "变化前: 静态构图; 变化瞬间: 轻微Push In; 变化后: Pull Out揭示后果",
    },
    "情感锚 (Emotional Anchor)": {
        "desc": "道具锚定角色的情感状态, 观众看到道具就联想到那个情感",
        "examples": "《飞屋环游记》探险手册; 《花样年华》钟表",
        "rule": "情感锚道具必须在角色情感高峰时出现, 且每次出现都与同一情感绑定",
        "shot_treatment": "始终保持同一镜头语言: 同一焦距, 类似构图, 让观众产生Pavlov式情感反射",
    },
}

# ============================================================
# 服装弧线模板 (与角色弧光同步)
# ============================================================
COSTUME_ARC_STAGES = {
    "干净 (Pristine)": {
        "story_beat": "建立/日常/序幕",
        "fabric_state": "新衣或刚洗过的衣服, 纤维完整, 颜色饱满",
        "visual_cue": "fabric catches light evenly, no shadow pockets in creases",
        "narrative": "角色尚未进入冲突, 世界还是完整的",
    },
    "磨损 (Worn)": {
        "story_beat": "冲突/上升/试炼",
        "fabric_state": "领口松弛, 肘部起球, 颜色微微褪去",
        "visual_cue": "fabric shows differential aging: stress points lighter, protected areas retain color",
        "narrative": "角色开始承受压力, 衣服记录了身体的消耗",
    },
    "破碎 (Torn)": {
        "story_beat": "高潮/危机/最低点",
        "fabric_state": "撕裂/污渍/血迹/烧痕, 结构性损坏",
        "visual_cue": "exposed threads, fabric layers visible at tear edges, stains have wet/dry gradient",
        "narrative": "角色的世界已经碎了, 衣服不再能保护他",
    },
    "重生 (Reborn)": {
        "story_beat": "结局/转变/新开始",
        "fabric_state": "新衣(不同风格) 或 旧衣修补过(缝补痕迹=伤疤)",
        "visual_cue": "either crisp new fabric or visible mending stitches in contrasting thread",
        "narrative": "角色已经不是开头那个人了, 衣服是最直观的证据",
    },
}

# ============================================================
# 60:30:10 色彩法则
# ============================================================
COLOR_SCHEME_RULES = {
    "60:30:10法则": {
        "desc": "经典电影/室内设计色彩比例: 60%主色(墙/地), 30%辅色(家具), 10%点缀(装饰/灯光)",
        "application": "set dominant=wall/floor, secondary=furniture/curtain, accent=lamp/flower/object",
    },
    "单色系": {
        "desc": "同一色相的不同明度/饱和度, 营造统一氛围",
        "application": "set all surfaces to variations of one hue, differentiate by lightness only",
    },
    "互补色": {
        "desc": "色环对面的两色(红-绿, 蓝-橙), 最大视觉冲突",
        "application": "use sparingly: one color dominates, complementary only in small accents",
    },
    "类似色": {
        "desc": "色环相邻的2-3色(蓝-蓝绿-绿), 和谐自然",
        "application": "good for naturalistic sets, avoid high saturation to prevent candy look",
    },
}


class CostumePropSetPro:
    """
    服化道专家节点 (环节 19) — L5 导演级
    真正的服化道设计系统: 角色服装弧线 + 道具叙事 + 9D材质光响应 + 场景色彩规划
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

                # === Phase 17.6 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),

                # === 服化道专属字段 ===
                "时代": (["古装 (Ancient)", "近代 (1900-1980)", "现代 (1980-Now)", "未来 (Sci-fi)", "跨时代 (Mixed)", "auto"], {"default": "auto"}),
                "材质重点": (["棉麻 (Cotton/Linen)", "丝绸 (Silk)", "皮革 (Leather)", "金属 (Metal)", "混合材质", "auto"], {"default": "auto"}),
                "色彩方案": (["60:30:10法则", "单色系", "互补色", "类似色", "auto"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("costumepropsetpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_costume"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_costume(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # 提取用户输入 (加 type 防御)
        _str = lambda kwargs_ref, k, d="": str(kwargs_ref.get(k, d)) if kwargs_ref.get(k) is not None else d

        task_type_full = _str(kwargs, "任务类型", "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs, "类型", "电影")
        scene = _str(kwargs, "场景描述", "")
        director = _str(kwargs, "导演风格", "是枝裕和")
        mood = _str(kwargs, "情绪基调", "")
        subtext = _str(kwargs, "潜文本_情感", "")
        intent_feel = _str(kwargs, "导演意图_观众应感到", "")
        props_raw = _str(kwargs, "关键道具", "")
        ref_films = _str(kwargs, "关键参考片", "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        era_choice = _str(kwargs, "时代", "auto")
        material_choice = _str(kwargs, "材质重点", "auto")
        color_scheme_choice = _str(kwargs, "色彩方案", "auto")

        # ----------------------------------------------------------
        # 1. 查询导演真实档案 (director_data_unified)
        # ----------------------------------------------------------
        director_profile = {}
        director_scenes = []
        if _HAS_DIRECTOR_DATA:
            director_profile = get_director(director)
            for s in SCENE_DATABASE_100:
                if s.get("director") == director:
                    director_scenes.append(s)

        dir_color = director_profile.get("色彩", "自然色调")
        dir_acting = director_profile.get("表演", "中规中矩")
        dir_objects = director_profile.get("物件", "通用")
        dir_era = director_profile.get("年代", "现代")

        # ----------------------------------------------------------
        # 2. 时代自动推断
        # ----------------------------------------------------------
        if era_choice == "auto":
            era_keywords = {
                "古装 (Ancient)": ["战国", "唐", "宋", "明", "清", "古代", "feudal", "dynasty", "1500", "1600", "1700", "1800", "武士", "铠甲", "和服"],
                "近代 (1900-1980)": ["1920", "1930", "1940", "1950", "1960", "1970", "1980", "民国", "二战", "抗战", "解放", "文革", "知青"],
                "现代 (1980-Now)": ["1990", "1998", "2000", "2010", "2020", "现代", "当代", "手机", "电脑", "互联网"],
                "未来 (Sci-fi)": ["2049", "未来", "赛博", "科幻", "飞船", "机器人", "AI", "太空"],
            }
            era_choice = "现代 (1980-Now)"
            combined_text = scene + " " + dir_era
            for era_label, kws in era_keywords.items():
                for kw in kws:
                    if kw in combined_text:
                        era_choice = era_label
                        break

        # ----------------------------------------------------------
        # 3. 材质自动推断 (基于导演偏好)
        # ----------------------------------------------------------
        director_costume_data = DIRECTOR_COSTUME_PHILOSOPHY.get(director, None)
        if material_choice == "auto":
            if director_costume_data:
                mat_pref = director_costume_data.get("material_pref", "")
                if "丝绸" in mat_pref or "Silk" in mat_pref:
                    material_choice = "丝绸 (Silk)"
                elif "皮革" in mat_pref or "Leather" in mat_pref:
                    material_choice = "皮革 (Leather)"
                elif "金属" in mat_pref or "Metal" in mat_pref:
                    material_choice = "金属 (Metal)"
                elif "混合" in mat_pref:
                    material_choice = "混合材质"
                else:
                    material_choice = "棉麻 (Cotton/Linen)"
            else:
                material_choice = "棉麻 (Cotton/Linen)"

        # ----------------------------------------------------------
        # 4. 色彩方案自动推断
        # ----------------------------------------------------------
        if color_scheme_choice == "auto":
            color_scheme_choice = "60:30:10法则"

        # ----------------------------------------------------------
        # 5. 解析道具列表, 赋予叙事功能
        # ----------------------------------------------------------
        prop_list = [p.strip() for p in props_raw.replace("/", " / ").split(" / ") if p.strip()]
        narrative_funcs = list(PROP_NARRATIVE_FUNCTIONS.keys())
        prop_assignments = []
        for i, prop in enumerate(prop_list):
            func = narrative_funcs[i % len(narrative_funcs)]
            func_data = PROP_NARRATIVE_FUNCTIONS[func]
            prop_assignments.append({
                "name": prop,
                "function": func,
                "desc": func_data["desc"],
                "shot_treatment": func_data["shot_treatment"],
            })

        # ----------------------------------------------------------
        # 6. 材质-光响应查询
        # ----------------------------------------------------------
        material_key_map = {
            "棉麻 (Cotton/Linen)": "棉布 (Cotton)",
            "丝绸 (Silk)": "丝绸 (Silk)",
            "皮革 (Leather)": "皮革 (Leather)",
            "金属 (Metal)": "金属 (Metal)",
            "混合材质": "织物混合 (Blended)",
        }
        primary_material_key = material_key_map.get(material_choice, "棉布 (Cotton)")
        material_data = MATERIAL_LIGHT_9D.get(primary_material_key, {})

        # ----------------------------------------------------------
        # 7. 导演专属服化道策略
        # ----------------------------------------------------------
        if director_costume_data is None:
            director_costume_data = {
                "method": "根据角色身份和场景氛围选择服装, 服从叙事需求",
                "costume_arc": "服装状态随角色情感弧线自然变化",
                "prop_rule": "道具必须有叙事功能, 拒绝纯装饰",
                "set_color": "服从60:30:10法则, 主色服从场景氛围",
                "material_pref": material_choice,
                "detail": "每件衣服有穿着历史, 每个道具有使用痕迹",
            }

        # ----------------------------------------------------------
        # 8. 场景色彩规划
        # ----------------------------------------------------------
        color_rule = COLOR_SCHEME_RULES.get(color_scheme_choice, COLOR_SCHEME_RULES["60:30:10法则"])
        set_color_desc = ""
        if director_costume_data.get("set_color"):
            set_color_desc = director_costume_data["set_color"]
        else:
            set_color_desc = "主色60%服从 " + dir_color + ", 辅色30%中性, 点缀10%情感色"

        # ----------------------------------------------------------
        # 9. 服装弧线匹配故事节拍
        # ----------------------------------------------------------
        # 根据情绪基调推断当前故事节拍
        beat_keywords = {
            "干净 (Pristine)": ["平静", "日常", "开始", "序幕", "建立"],
            "磨损 (Worn)": ["压抑", "紧张", "挣扎", "试炼", "冲突"],
            "破碎 (Torn)": ["崩溃", "绝望", "高潮", "危机", "最低"],
            "重生 (Reborn)": ["希望", "重生", "转变", "释然", "和解"],
        }
        current_arc_stage = "磨损 (Worn)"  # default
        for stage, kws in beat_keywords.items():
            for kw in kws:
                if kw in mood or kw in subtext:
                    current_arc_stage = stage
                    break
        arc_data = COSTUME_ARC_STAGES[current_arc_stage]

        # ----------------------------------------------------------
        # 10. 构建 H3 三字段 prompt (服化道版)
        # ----------------------------------------------------------
        # 类型 -> Shot 1 风格
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, high emotional rhythm",
            "短视频": "live-action, high saturation, direct",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        style = style_choices.get(genre, "Cinematic, live-action")

        # 导演镜头运动
        director_motion_map = {
            "塔可夫斯基": "Static Shot holding for 8+ seconds, then Push In at glacial speed",
            "王家卫": "Push In with step-printing at 1/8 speed, neon reflections sliding across silk",
            "诺兰": "Tracking Shot following the suit fabric texture as character walks",
            "是枝裕和": "Static Shot mid-range, letting the worn cotton shirt speak for itself",
            "侯孝贤": "Static Shot extreme long take, clothing as part of the landscape",
            "奉俊昊": "Static to Push In, camera noticing the stain the character tries to hide",
            "黑泽明": "Wide Shot revealing full armor and banner, then medium on samurai face",
            "周星驰": "Quick Cut between absurd costume details, then hold on embarrassment",
            "贾樟柯": "Medium Shot documentary-style, catching the fake brand logo on the jacket",
            "李沧东": "Push In at crawl speed toward hands, the fabric barely visible in frame edge",
            "蔡明亮": "Static Shot ultra-long, watching water slowly soak into fabric",
            "毕赣": "Arc Shot circling around the character, each angle reveals different fabric wear",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + Push In at slow speed")

        # Shot 1: 建立场景, 展示服化道细节
        shot_1 = (
            "a medium-wide shot establishes " + scene + ". "
            + director_motion_pref + ". "
            + "The character wears " + arc_data["fabric_state"] + ". "
            + "The primary material is " + primary_material_key + ": " + material_data.get("漫反射", "natural diffuse") + ". "
            + "Set color follows " + color_scheme_choice + ": " + set_color_desc + ". "
            + "The director intends: " + intent_feel + "."
        )

        # Prop-driven shots
        first_prop = prop_assignments[0] if prop_assignments else {"name": props_raw, "function": "情感锚 (Emotional Anchor)", "shot_treatment": "hold on object"}
        shots = []

        # Shot 2: 服装细节 (材质光响应)
        shots.append(
            "[Shot 2] At 00:04.000, close-up on fabric texture. "
            + material_data.get("色温响应", "natural response") + ". "
            + "The " + arc_data["visual_cue"] + ". "
            + "This is " + current_arc_stage + " in the costume arc: " + arc_data["narrative"] + "."
        )

        # Shot 3: 道具叙事 (第一个道具)
        shots.append(
            "[Shot 3] At 00:09.000, " + format_shot_motion("Push In", "small", "slow")
            + " toward the " + first_prop["name"] + ". "
            + "Narrative function: " + first_prop["function"] + " - " + first_prop.get("desc", "") + ". "
            + "Shot treatment: " + first_prop.get("shot_treatment", "") + "."
        )

        # Shot 4: 角色互动与潜文本
        shots.append(
            "[Shot 4] At 00:15.000, over-the-shoulder shot. "
            + "The character's " + dir_acting + " reveals " + subtext + ". "
            + "The costume's condition (" + current_arc_stage + ") mirrors the emotional state."
        )

        # Shot 5: 场景道具连续性
        last_prop = prop_assignments[-1] if len(prop_assignments) > 1 else first_prop
        shots.append(
            "[Shot 5] At 00:22.000, static shot holding on the wider set. "
            + "Continuity check: the " + last_prop["name"] + " remains in its established position. "
            + "The " + color_scheme_choice + " is visible across the frame: "
            + set_color_desc + ". "
            + "Silence holds for 5 seconds. " + mood + "."
        )

        # Shot 6: 结尾 (材质在光线变化中的响应)
        shots.append(
            "[Shot 6] At 00:27.000, the camera holds for 3 seconds. "
            + "The light shifts and the " + primary_material_key + " responds: "
            + material_data.get("光泽变化", material_data.get("皱褶阴影", material_data.get("纹理响应", "subtly"))) + ". "
            + "End of shot."
        )

        soundscape = (
            "Ambient: " + (director_scenes[0].get("sound", "rain + environment") if director_scenes else "rain + environment") + ". "
            + "Foley: fabric rustling as character adjusts clothing. "
            + "The " + (prop_assignments[0]["name"] if prop_assignments else "prop") + " makes a specific sound when touched. "
            + "Silence gaps between actions let the costume textures breathe."
        )
        music = "Sparse, era-appropriate score. " + ("古典 + 安静" if "古装" in era_choice else "minimal piano or ambient pads, entering only at emotional peaks.")

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # ----------------------------------------------------------
        # 11. 灵魂注入 (Phase 17.6)
        # ----------------------------------------------------------
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
                    "【灵魂核心 - 服化道设计驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        # ----------------------------------------------------------
        # 12. 组装主输出
        # ----------------------------------------------------------
        main_output = "=" * 60 + "\n"
        main_output += soul_header
        main_output += "【CostumePropSetPro】服化道专家节点 - L5 导演级\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【时代设定】 " + era_choice + "\n"
        main_output += "【主要材质】 " + material_choice + "\n"
        main_output += "【色彩方案】 " + color_scheme_choice + "\n\n"

        # 导演档案 (从 director_data_unified)
        if director_profile:
            main_output += "=" * 60 + "\n"
            main_output += "导演真实档案 (director_data_unified 35导演8维)\n"
            main_output += "=" * 60 + "\n"
            main_output += "  色彩: " + dir_color + "\n"
            main_output += "  表演: " + dir_acting + "\n"
            main_output += "  标志物件: " + dir_objects + "\n"
            main_output += "  年代背景: " + dir_era + "\n\n"

        # 导演服化道方法论
        main_output += "=" * 60 + "\n"
        main_output += "导演服化道方法论 (导演个性化策略)\n"
        main_output += "=" * 60 + "\n"
        main_output += "  方法: " + director_costume_data["method"] + "\n"
        main_output += "  服装弧线: " + director_costume_data["costume_arc"] + "\n"
        main_output += "  道具法则: " + director_costume_data["prop_rule"] + "\n"
        main_output += "  场景色彩: " + director_costume_data["set_color"] + "\n"
        main_output += "  材质偏好: " + director_costume_data["material_pref"] + "\n"
        main_output += "  细节要求: " + director_costume_data["detail"] + "\n\n"

        # 当前服装弧线阶段
        main_output += "=" * 60 + "\n"
        main_output += "当前服装弧线阶段: " + current_arc_stage + "\n"
        main_output += "=" * 60 + "\n"
        main_output += "  故事节拍: " + arc_data["story_beat"] + "\n"
        main_output += "  面料状态: " + arc_data["fabric_state"] + "\n"
        main_output += "  视觉线索: " + arc_data["visual_cue"] + "\n"
        main_output += "  叙事含义: " + arc_data["narrative"] + "\n\n"

        # 道具叙事分配
        main_output += "=" * 60 + "\n"
        main_output += "道具叙事功能分配\n"
        main_output += "=" * 60 + "\n"
        for pa in prop_assignments:
            main_output += "  [" + pa["function"] + "] " + pa["name"] + "\n"
            main_output += "    - " + pa["desc"] + "\n"
            main_output += "    - 拍法: " + pa["shot_treatment"] + "\n"
        main_output += "\n"

        # 材质光响应
        main_output += "=" * 60 + "\n"
        main_output += "9D 材质-光响应: " + primary_material_key + "\n"
        main_output += "=" * 60 + "\n"
        for k, v in material_data.items():
            main_output += "  " + k + ": " + v + "\n"
        main_output += "\n"

        # 场景色彩规划
        main_output += "=" * 60 + "\n"
        main_output += "场景色彩规划: " + color_scheme_choice + "\n"
        main_output += "=" * 60 + "\n"
        main_output += "  规则: " + color_rule["desc"] + "\n"
        main_output += "  应用: " + color_rule["application"] + "\n"
        main_output += "  导演方案: " + set_color_desc + "\n\n"

        # H3 prompt
        main_output += "=" * 60 + "\n"
        main_output += "H3 三大字段 (服化道定制版)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_prompt + "\n\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ----------------------------------------------------------
        # 13. 第二输出: 经验矩阵
        # ----------------------------------------------------------
        experience = "【导演服化道实战经验矩阵】\n\n"
        for d_name, d_data in DIRECTOR_COSTUME_PHILOSOPHY.items():
            experience += "  " + d_name + ": " + d_data["method"] + "\n"
        experience += "\n【道具叙事4类功能】\n"
        for func_name, func_data in PROP_NARRATIVE_FUNCTIONS.items():
            experience += "  " + func_name + ": " + func_data["examples"] + "\n"
        experience += "\n【服装弧线4阶段 (与角色弧光同步)】\n"
        for stage_name, stage_data in COSTUME_ARC_STAGES.items():
            experience += "  " + stage_name + " [" + stage_data["story_beat"] + "]: " + stage_data["narrative"] + "\n"
        experience += "\n【9D 材质-光响应 (9种材质)】\n"
        for mat_name in MATERIAL_LIGHT_9D.keys():
            experience += "  - " + mat_name + "\n"
        experience += "\n【导演场景数据 (匹配 " + director + ")】\n"
        for ds in director_scenes[:5]:
            experience += "  - " + ds.get("scene", "") + ": " + ds.get("object", "") + " | " + ds.get("color", "") + "\n"

        # ----------------------------------------------------------
        # 14. 第三输出: AI 深度处理
        # ----------------------------------------------------------
        ai_deep_output = "【服化道 AI 深度处理指令】\n\n"
        ai_deep_output += "【1. 服装-角色弧光同步规则】\n"
        ai_deep_output += "  - 服装不是独立设计, 是角色内心的外化\n"
        ai_deep_output += "  - 当前阶段: " + current_arc_stage + " -> " + arc_data["narrative"] + "\n"
        ai_deep_output += "  - 下一阶段提示: 注意面料状态变化暗示情感转折\n\n"

        ai_deep_output += "【2. 道具连续性追踪】\n"
        for pa in prop_assignments:
            ai_deep_output += "  - " + pa["name"] + " [" + pa["function"] + "]: 必须在跨镜头中保持位置/状态连续\n"

        ai_deep_output += "\n【3. 材质渲染检查清单】\n"
        ai_deep_output += "  - 主材质 " + primary_material_key + " 的光响应是否正确?\n"
        ai_deep_output += "  - 材质aging状态是否匹配角色弧线阶段 (" + current_arc_stage + ")?\n"
        ai_deep_output += "  - 不同光温下材质色彩是否符合 " + material_data.get("色温响应", "physical rules") + "?\n\n"

        ai_deep_output += "【4. 色彩方案执行检查】\n"
        ai_deep_output += "  - " + color_scheme_choice + ": " + color_rule["desc"] + "\n"
        ai_deep_output += "  - 导演方案: " + set_color_desc + "\n"
        ai_deep_output += "  - 检查: 画面中60/30/10比例是否达标?\n\n"

        ai_deep_output += "【5. 反AI具体细节铁律 (服化道版)】\n"
        ai_deep_output += "  - 不写'精致的服装', 写'领口有0.5cm的线头, 第三颗扣子比其他的松'\n"
        ai_deep_output += "  - 不写'古朴的道具', 写'收音机的天线用铁丝缠过, 旋钮左边那个卡在FM98.6'\n"
        ai_deep_output += "  - 不写'温馨的厨房', 写'灶台左侧有油渍积累的深棕色痕迹, 墙砖第3排第7块有裂纹'\n"
        ai_deep_output += "  - 不写'破旧的衣服', 写'右肘有3cm的磨破洞, 内衬已经缩水到可以看到接缝线'\n"
        ai_deep_output += "  - 面料有具体成分: '65%涤纶35%棉, 洗过很多次的那种柔软'\n\n"

        ai_deep_output += "【6. 9D 光照控制 (服化道材质版)】\n"
        try:
            for k, v in LIGHTING_9D.items():
                ai_deep_output += "  - " + k + ": " + v + "\n"
        except Exception:
            ai_deep_output += "  (LIGHTING_9D unavailable)\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "CostumePropSetPro": CostumePropSetPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "CostumePropSetPro": "👘 服化道 (环节 19) — L5 重写",
# }
