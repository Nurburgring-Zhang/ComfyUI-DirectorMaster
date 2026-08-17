# -*- coding: utf-8 -*-
# ============================================================
# 维度输出模块集 V1.0 (用户列的全部输出维度callable)
# ============================================================
# 角色设计/环境设计/故事设计/互动交互/氛围设计 — 7维决策树
# (剧本/分镜/叙事推进/运镜转场/剪辑技巧/故事线 已被现有模块覆盖)
# 引擎按"输出侧重"调用对应模块, 每维度真实callable
# ============================================================

# ============================================================
# 一、角色设计指导 (character_design)
# ============================================================
CHARACTER_DESIGN = {
    "protagonist_arc": {
        "cn": "主角弧光设计",
        "trigger": "任何主角设计/成长弧/转变弧/堕落弧",
        "rationale": "主角须有起点→终点可视化变化弧光, 观众因在乎弧光而在乎故事。",
        "execution": {
            "positive_arc": "想要(欲望)→需要(真相)→获得需要(《飞屋》)",
            "flat_arc": "主角不变, 改变周围(《阿甘》)",
            "corruption_arc": "好人→堕落(《教父2》Michael)",
            "disillusionment": "信念→幻灭(《现代启示录》)",
        },
        "failure_modes": ["无弧光=观众不在乎", "弧光突变无过程=不可信", "起点终点模糊=失方向"],
        "measurement": "主角有清晰起点→终点弧光, 观众能复述变化",
        "alternatives": ["flat_arc(更稳定)"],
        "cross_refs": {"narrative": "弧光=叙事脊梁", "performance": "弧光外化表演"},
    },
    "character_appearance": {
        "cn": "外貌服装设计",
        "trigger": "角色外貌/服装色彩/造型/年龄/体态",
        "rationale": "外貌服装=角色的第一视觉语言, 色彩暗示身份/弧光/阵营, 体态暗示性格。",
        "execution": {
            "color_arc": "服装色彩随弧光变化(白→红=觉醒/朴素→华丽=堕落)",
            "silhouette": "剪影辨识度(一眼认出)",
            "color_camp": "阵营色彩(仙白金青/魔黑红紫/妖绿橙)",
            "age_body": "年龄体态暗示性格+背景",
        },
        "failure_modes": ["无色彩弧=失弧光外化", "剪影无辨识=失记忆", "服装与身份不符=失真"],
        "measurement": "外貌有色彩弧+剪影辨识+身份相符",
        "alternatives": ["character_archetypes"],
        "cross_refs": {"color": "服装色彩=弧光", "composition": "剪影辨识", "performance": "体态=性格"},
    },
    "character_motivation": {
        "cn": "动机与关系网",
        "trigger": "角色动机/欲望/恐惧/关系网/功能角色",
        "rationale": "动机驱动行动, 关系网定义角色功能(主角/反派/导师/变形者), 缺动机=角色空。",
        "execution": {
            "want_need": "外在欲望(想要)+内在需要(真相)",
            "wound_ghost": "创伤+幽灵(过去的隐痛)",
            "relationships": "关系网(谁对谁做什么)",
            "function": "功能角色(主角/导师/门槛守护/反派/变形者/阴影)",
        },
        "failure_modes": ["无动机=行动无因", "无关系网=角色孤立", "功能角色缺=结构散"],
        "measurement": "有want/need+创伤+关系网+功能角色",
        "alternatives": [],
        "cross_refs": {"narrative": "动机=驱动力", "performance": "动机外化表演"},
    },
}


# ============================================================
# 二、环境设计指导 (environment_design)
# ============================================================
ENVIRONMENT_DESIGN = {
    "spatial_narrative": {
        "cn": "空间叙事设计",
        "trigger": "场景空间设计/垂直阶级/门窗困局/迷宫",
        "rationale": "空间是叙事材料非背景。垂直=阶级, 门窗=困局/边界, 迷宫=道德/命运。",
        "execution": {
            "vertical_class": "楼上楼下=阶级(《寄生虫》)",
            "door_frame": "门窗=边界/困局(《教父》)",
            "labyrinth": "迷宫=道德/命运(《闪灵》/《盗梦空间》)",
            "threshold": "跨越门槛=进入新世界(英雄之旅)",
        },
        "failure_modes": ["空间无叙事=空背景", "垂直无阶级=失隐喻", "门窗无边界=失困局"],
        "measurement": "空间有叙事隐喻(阶级/困局/命运)",
        "alternatives": ["atmosphere_design"],
        "cross_refs": {"composition": "空间构图", "narrative": "空间=叙事材料"},
    },
    "color_prop_symbols": {
        "cn": "色彩方案与道具符号",
        "trigger": "场景色彩方案/道具符号/伏笔物件",
        "rationale": "色彩即叙事+道具符号=伏笔锚点。每场专属色方案, 道具=契诃夫之枪。",
        "execution": {
            "scene_palette": "每场专属主色+辅助+点缀",
            "prop_foreshadow": "道具=伏笔(契诃夫之枪)",
            "color_motif": "色彩母题(红=危险/白=纯净)",
            "object_anchor": "物件锚定情感(戒指=承诺/照片=回忆)",
        },
        "failure_modes": ["色彩无叙事=炫色", "道具无回收=悬置", "母题无意义=失锚"],
        "measurement": "色彩即叙事+道具伏笔回收+母题有意义",
        "alternatives": [],
        "cross_refs": {"color": "色彩心理学", "foreshadow": "契诃夫之枪"},
    },
    "lighting_atmosphere": {
        "cn": "光照与质感",
        "trigger": "场景光照/质感/时代感/材质",
        "rationale": "光照定义情绪, 质感定义时代。动机光=合理, 材质暗示时代/阶级。",
        "execution": {
            "motivated_light": "光源须合理(窗/灯/月/火)",
            "material_era": "材质暗示时代(光滑塑料=近未来/生锈=废土)",
            "texture_class": "质感暗示阶级(粗糙=底层/精致=上层)",
            "atmosphere_particle": "粒子/雾气=空气可见=空间可感",
        },
        "failure_modes": ["动机光不合理=穿帮", "材质无时代=失实", "质感无阶级=失层次"],
        "measurement": "动机光合理+材质时代+质感阶级+空气可感",
        "alternatives": ["master_cinematography.lighting"],
        "cross_refs": {"lighting": "布光系统", "genre": "类型视觉语言"},
    },
}


# ============================================================
# 三、故事情节设计 (story_design)
# ============================================================
STORY_DESIGN = {
    "logline_structure": {
        "cn": "故事核与结构骨架",
        "trigger": "故事核设计/结构选择/节拍表",
        "rationale": "logline一句话说清=想透。结构骨架=观众预期管理工具, 节拍表=节奏蓝图。",
        "execution": {
            "logline": "主角+目标+冲突+代价(一句话)",
            "structure": "按类型选骨架(悬疑→mystery_reveal, 英雄→hero_journey)",
            "beat_sheet": "节拍表精确到位置%",
            "theme": "主题陈述(开场暗示, 结尾呼应)",
        },
        "failure_modes": ["logline说不清=没想透", "结构错配=观众觉得'怪'", "节拍位置错=节奏崩"],
        "measurement": "logline清晰+结构匹配类型+节拍位置精确",
        "alternatives": ["narrative_structures"],
        "cross_refs": {"narrative": "结构骨架", "pacing": "节拍表"},
    },
    "foreshadow_map": {
        "cn": "伏笔地图与角色弧光",
        "trigger": "伏笔/回收/角色弧光位置/红鲱鱼",
        "rationale": "伏笔须自然埋设且回收冲击>埋设。角色弧光=叙事脊梁。红鲱鱼区分。",
        "execution": {
            "plant": "自然埋设(有合理存在理由)",
            "payoff": "回收冲击>埋设印象",
            "timing": "短剧3-8集, 长片可跨幕",
            "red_herring": "红鲱鱼(故意误导)",
        },
        "failure_modes": ["埋了不回=悬置", "回收<埋设=失望", "太快=无悬念"],
        "measurement": "伏笔自然埋设+回收冲击+时机+红鲱鱼区分",
        "alternatives": ["emotion_rendering.foreshadowing_payoff"],
        "cross_refs": {"narrative": "伏笔=叙事工具", "pacing": "前埋后收"},
    },
}


# ============================================================
# 四、互动交互设计 (interaction_design) — 短视频/短剧
# ============================================================
INTERACTION_DESIGN = {
    "engagement_hooks": {
        "cn": "互动钩子设计",
        "trigger": "短视频互动/选择/预测/找彩蛋/未完待续/观点表态",
        "rationale": "互动钩子=让观众参与, 评论/关注/重看。算法互动率权重高。",
        "execution": {
            "choice": "选择题(评论区AB讨论)",
            "predict": "预测邀请('猜猜接下来')",
            "easter_egg": "找彩蛋(重看价值)",
            "cliffhanger": "未完待续(关注转化)",
        },
        "failure_modes": ["互动无吸引力=失参与", "选项无两难=无讨论", "未完不回收=失信"],
        "measurement": "观众参与(评论/关注/重看), 互动率提升",
        "alternatives": ["creation_skills"],
        "cross_refs": {"algorithm": "互动率权重", "retention": "互动驱动留存"},
    },
    "share_conversion": {
        "cn": "分享转化设计",
        "trigger": "短视频分享/身份认同/社交货币/话题性",
        "rationale": "分享=传播核心。身份认同/社交货币/话题性驱动分享率。",
        "execution": {
            "identity": "身份认同('这就是我'→转发表态)",
            "social_currency": "社交货币(显得有品味→分享)",
            "topic": "话题性(争议/热点→讨论)",
            "practical": "实用价值(教程→收藏转发)",
        },
        "failure_modes": ["无身份认同=不转发", "社交货币过显=装逼", "无话题=失传播"],
        "measurement": "分享率(社交裂变)提升",
        "alternatives": ["creation_skills"],
        "cross_refs": {"algorithm": "分享率权重", "viral": "分享=传播"},
    },
}


# ============================================================
# 五、画面氛围感设计 (atmosphere_design)
# ============================================================
ATMOSPHERE_DESIGN = {
    "light_color_atmosphere": {
        "cn": "光影色彩氛围",
        "trigger": "画面氛围/光影/色彩/情绪外化",
        "rationale": "光影+色彩=氛围的核心语言。情绪外化到环境/天气/物件=让不可见变可见。",
        "execution": {
            "light_emotion": "光位/光质/光比=情绪(暖=安全, 冷=疏离)",
            "color_emotion": "色彩=情绪(红=激情/蓝=忧郁)",
            "weather_externalize": "天气外化情绪(雨=悲, 雪=纯, 雾=迷茫)",
            "color_shift": "色温变化=情绪转变(暖→冷=安全→危险)",
        },
        "failure_modes": ["光影无情绪=空布光", "色彩无叙事=炫色", "天气无情绪=失外化"],
        "measurement": "光影色彩外化情绪, 氛围达成",
        "alternatives": ["master_cinematography.lighting", "emotion_rendering"],
        "cross_refs": {"lighting": "布光系统", "color": "色彩心理学", "emotion": "情绪外化"},
    },
    "sound_silence_atmosphere": {
        "cn": "声音与留白氛围",
        "trigger": "声音氛围/环境音/音乐/静默/呼吸感",
        "rationale": "声音是氛围的另一半。静默比巨响更有力, 环境音层叠=压力, 留白=呼吸。",
        "execution": {
            "silence": "静默=最震撼叙事(让真实声/沉默取代音乐)",
            "ambient_layer": "环境音层叠=压力上升/消失=聚焦内心",
            "music_absence": "音乐戛然而止=最震撼",
            "breathing_space": "留白=呼吸感(高潮后须给余韵镜)",
        },
        "failure_modes": ["音乐过多=失留白", "无静默=失力量", "环境音无层次=失氛围"],
        "measurement": "声音+留白达成氛围, 静默有力量",
        "alternatives": ["emotion_rendering.scene_emotion_rendering.sound"],
        "cross_refs": {"sound": "声音设计", "pacing": "留白=呼吸", "emotion": "静默>巨响"},
    },
    "texture_quality_atmosphere": {
        "cn": "质感与品质氛围",
        "trigger": "画面质感/胶片感/颗粒/景深/虚实",
        "rationale": "质感定义品质与情绪。胶片颗粒=怀旧, 浅景深=隔离, 长镜头=沉浸。",
        "execution": {
            "film_grain": "胶片颗粒=怀旧/质感",
            "depth_field": "浅景深=隔离/亲密, 深焦=民主/信息",
            "long_take": "长镜头=沉浸/真实时间",
            "quality_finish": "完成度=品质感(每帧精修)",
        },
        "failure_modes": ["无质感=失品质", "景深无情绪=失功能", "长镜头无调度=炫技"],
        "measurement": "质感+景深+长镜头达成品质氛围",
        "alternatives": ["master_cinematography.depth_of_field"],
        "cross_refs": {"lens": "景深系统", "pacing": "长镜头=节奏", "quality": "完成度"},
    },
}


def get_dimension_guide(dimension, key=None):
    """按维度获取指导(character/environment/story/interaction/atmosphere)"""
    maps = {
        "character": CHARACTER_DESIGN,
        "environment": ENVIRONMENT_DESIGN,
        "story": STORY_DESIGN,
        "interaction": INTERACTION_DESIGN,
        "atmosphere": ATMOSPHERE_DESIGN,
    }
    table = maps.get(dimension, {})
    if key:
        return table.get(key, {})
    return table


def build_dimension_section(dimension):
    """构建维度指导章节(注入AI)"""
    table = get_dimension_guide(dimension)
    if not table:
        return ""
    lines = [f"【{dimension}设计指导】"]
    for k, v in table.items():
        lines.append(f"  ◆ {v.get('cn','')}: {v.get('trigger','')[:50]}")
        if v.get("rationale"):
            lines.append(f"    原理: {v['rationale'][:60]}")
        if v.get("failure_modes"):
            lines.append(f"    失败模式: {'; '.join(v['failure_modes'][:2])}")
        if v.get("measurement"):
            lines.append(f"    验收: {v['measurement'][:60]}")
    return "\n".join(lines)
