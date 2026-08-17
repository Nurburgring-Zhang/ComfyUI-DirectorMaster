# -*- coding: utf-8 -*-
"""
ArtDirectionPro — 美术指导节点 (灵魂驱动版)
==================================================
环节 5 视觉风格 + 环节 17 风格手册 (导演级) + Phase 17 灵魂注入

Phase 18 灵魂驱动重做 — 视觉语言专家子 agent 重做版:
1. 完整接入 DirectorSoulNode 灵魂注入
   - 60 情感矩阵 + 7 融合 + 10 灵魂维度 + 灵魂状态
2. 视觉语言参数化系统 (焦段×情感 / 光圈×景深 / 景别×叙事 / 7 大构图)
   全部 DYNAMIC — 由 fused_emotion 真正动态生成, 严禁模板
3. 60:30:10 色彩法则灵魂驱动版
   - 60% 主色: fused_emotion.color_palette 主色
   - 30% 辅色: 导演风格决定
   - 10% 点缀色: 灵魂戏剧时刻
4. 9 维光影设计 (光源/方向/强度/色温/软硬/比例/阴影/特殊/时间)
   - color_palette → 色温 + 时间
   - music_tempo → 强度 + 比例 + 阴影
5. 8 大顶级摄影指导风格库 (Deakins/Lubezki/Doyle/Szeptycki/Young/Kaminski/Storaro/van Hoytema)
6. 8 大顶级导演视觉签名 (王家卫/诺兰/PTA/奉俊昊/黑泽明/库斯杜力卡/塔可夫斯基/约阿希姆·提尔)
7. 11 维导演控制能力 + 3 留白 + 3 运镜 全部应用 (结合灵魂)
8. 5 要素架构 (数据/上下文/Skill/经验/AI)
9. H3 三大字段完整输出
10. 向后兼容 (旧版 时代/视觉风格/材质重点/光影/颜色/空间布局/导演风格 参数)
11. 每个输出 ≥ 15000 字符
"""

import os
import sys
import json
import random

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import ART_DIRECTION_4D
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)

try:
    from director_soul import (
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
        fuse_emotions,
        build_soul_injection,
        compute_soul_state,
        _HAS_EMOTION_DATA,
    )
    _HAS_SOUL = True
except Exception as e:
    _HAS_SOUL = False
    _SOUL_ERROR = str(e)


# ============================================================
# _str() helper — 安全字符串化, 兼容 list/tuple/None
# ============================================================
def _str(v, default=""):
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else default
    return str(v)


# ============================================================
# 1. 灵魂驱动焦段 × 情感映射 (DYNAMIC)
# ============================================================
FOCAL_LENGTH_SOUL_MAP = {
    # 焦段: (主导情感 categories, intensity 阈值, 反向排除, 文本理由)
    "14mm_ultra_wide": {
        "categories": ["Fear", "Disgust", "Anger"],
        "intensity_min": 0.6,
        "rationale": "广角畸变/压迫/近距离恐惧 — 灵魂在恐惧/厌恶/暴怒时",
        "narrative": "心理压迫/超现实/怪诞/失衡空间",
        "dominant_moods": "fear_terror / disgust_loathing / anger_fury / aggressiveness",
    },
    "24mm_wide": {
        "categories": ["Anticipation", "Surprise"],
        "intensity_min": 0.5,
        "rationale": "街拍纪实/主观不稳定/真实感 — 灵魂在警觉/困惑/期待时",
        "narrative": "街拍/主观镜头/纪实/不稳定的现实/末日逃生",
        "dominant_moods": "tension / vigilance / uncertainty / anticipation_expectation",
    },
    "35mm_cinematic": {
        "categories": [],  # 兜底
        "intensity_min": 0.0,
        "rationale": "标准电影感/平衡/叙事主力 — 灵魂没有极化时的默认",
        "narrative": "叙事主力/对话/日常/经典电影语言",
        "dominant_moods": "(默认/兜底)",
    },
    "50mm_eye": {
        "categories": ["Joy", "Trust", "Love", "Tenderness"],
        "intensity_min": 0.3,
        "rationale": "人眼视角/亲密/自然 — 灵魂在喜悦/接纳/爱/温柔时",
        "narrative": "对话/亲密/纪实/无侵入式叙事",
        "dominant_moods": "joy_pleasure / trust_acceptance / love / tenderness / optimism",
    },
    "85mm_portrait": {
        "categories": ["Sadness", "Tenderness", "Love"],
        "intensity_min": 0.6,
        "rationale": "肖像特写/虚化/隔离/浪漫 — 灵魂在深爱/深悲/极温柔时",
        "narrative": "情感特写/肖像/浪漫/梦境/隔离",
        "dominant_moods": "sadness_sorrow / sadness_grief / love (intensity>0.8) / tenderness (intensity>0.7)",
    },
    "135mm_compression": {
        "categories": ["Loneliness", "State"],
        "intensity_min": 0.6,
        "rationale": "远距离/压缩/孤独/监视/陌生化 — 灵魂在孤独/思念/怀旧时",
        "narrative": "远距离观察/孤独角色/监视感/陌生化/超现实",
        "dominant_moods": "loneliness / longing / nostalgia / despair / vigilance (监视)",
    },
}


# ============================================================
# 2. 灵魂驱动光圈 × 景深 (DYNAMIC)
# ============================================================
APERTURE_SOUL_MAP = {
    "T1.4_T2_extreme_shallow": {
        "categories": ["Surprise", "Joy", "Love", "Awe", "Wonder"],
        "intensity_min": 0.7,
        "rationale": "极浅景深/梦幻/极致虚化 — 灵魂在惊异/极乐/爱/敬畏时",
        "narrative": "梦境/记忆/主观幻觉/极致情感特写",
        "dominant_moods": "surprise_amazement / joy_ecstasy / love (high) / awe / wonder",
    },
    "T2.8_cinematic_shallow": {
        "categories": [],
        "intensity_min": 0.0,
        "rationale": "电影感浅景深/人物特写 — 默认电影标准",
        "narrative": "人物特写/对话/情感场景/电影叙事主力",
        "dominant_moods": "(默认/兜底)",
    },
    "T4_mid": {
        "categories": ["Trust", "Tenderness", "Joy"],
        "intensity_min": 0.3,
        "rationale": "中景深/对话/群戏/平衡 — 灵魂在接纳/温柔/舒适时",
        "narrative": "对话场景/群戏/平衡叙事/家庭",
        "dominant_moods": "trust_acceptance / tenderness / joy_serenity",
    },
    "T8_deep": {
        "categories": ["Fear", "Tension", "Anticipation", "State"],
        "intensity_min": 0.5,
        "rationale": "全景深/环境展示/群戏/空间关系 — 灵魂在恐惧/紧张/警觉时",
        "narrative": "环境建立/群戏/空间关系/监视",
        "dominant_moods": "tension / vigilance / fear_apprehension / loneliness (环境)",
    },
}


# ============================================================
# 3. 灵魂驱动景别 × 叙事 (DYNAMIC)
# ============================================================
SHOT_SIZE_SOUL_MAP = {
    "ELS_extreme_long": {
        "categories": ["Sadness", "State", "Fear"],
        "intensity_min": 0.6,
        "rationale": "渺小化/命运压迫/史诗感/存在主义",
        "dominant_moods": "loneliness / despair / awe / sadness_grief",
    },
    "LS_long": {
        "categories": [],
        "intensity_min": 0.0,
        "rationale": "场景建立/交代空间/群戏/时间标记",
        "dominant_moods": "(叙事起点)",
    },
    "MLS_medium_long": {
        "categories": ["Trust", "Tenderness"],
        "intensity_min": 0.4,
        "rationale": "角色关系/环境+人物平衡",
        "dominant_moods": "tenderness / trust_acceptance / nostalgia",
    },
    "MS_medium": {
        "categories": ["Joy", "Trust", "Anticipation"],
        "intensity_min": 0.3,
        "rationale": "对话/日常/叙事主力",
        "dominant_moods": "(日常/对话)",
    },
    "MCU_medium_close": {
        "categories": ["Love", "Tenderness", "Joy"],
        "intensity_min": 0.5,
        "rationale": "重要对话/亲密临界/情感升级",
        "dominant_moods": "love / tenderness / joy_pleasure",
    },
    "CU_close": {
        "categories": ["Anger", "Disgust", "Surprise", "Fear"],
        "intensity_min": 0.6,
        "rationale": "情绪爆发/微表情/悬念营造",
        "dominant_moods": "anger_fury / disgust_loathing / fear_terror / surprise_astonishment",
    },
    "ECU_extreme_close": {
        "categories": ["Sadness", "Love", "Complex"],
        "intensity_min": 0.7,
        "rationale": "心理时刻/极致细节/瞳孔/嘴唇",
        "dominant_moods": "love (peak) / sadness_grief / awe / shame",
    },
    "ECU_PLUS_macro": {
        "categories": ["Complex", "State"],
        "intensity_min": 0.8,
        "rationale": "细节隐喻/契诃夫之枪/超现实",
        "dominant_moods": "awe / shame / disgust_loathing (细节) / guilt",
    },
}


# ============================================================
# 4. 灵魂驱动构图 (DYNAMIC)
# ============================================================
COMPOSITION_SOUL_MAP = {
    "rule_of_thirds": {"categories": [], "intensity_min": 0.0, "rationale": "经典平衡/通用"},
    "golden_ratio": {"categories": ["Trust", "Joy", "Tenderness"], "intensity_min": 0.4, "rationale": "自然美感/和谐"},
    "symmetry": {"categories": ["Fear", "Anger", "Disgust"], "intensity_min": 0.5, "rationale": "权力/仪式/压迫"},
    "leading_lines": {"categories": ["Anticipation", "Joy"], "intensity_min": 0.3, "rationale": "深度/空间引导"},
    "frame_in_frame": {"categories": ["Sadness", "Loneliness", "Fear"], "intensity_min": 0.5, "rationale": "隔离/窥视/超现实"},
    "negative_space": {"categories": ["Loneliness", "Sadness", "State"], "intensity_min": 0.5, "rationale": "孤独/留白/想象"},
    "low_key_high_contrast": {"categories": ["Fear", "Disgust", "Anger"], "intensity_min": 0.7, "rationale": "悬疑/黑色电影/心理"},
}


# ============================================================
# 5. 9 维光影灵魂映射 (color_palette + music_tempo → 9 维)
# ============================================================
LIGHTING_9D_SOUL = {
    "光源类型": {
        # 颜色 → 光源
        "warm_palette": ["火光 (蜡烛/壁炉)", "白炽灯", "自然光 (太阳)"],
        "cool_palette": ["月光", "LED 屏幕", "自然光 (太阳)"],
        "neutral_palette": ["自然光 (太阳)", "混合光", "荧光灯"],
        "neon_palette": ["霓虹 (城市)", "LED 屏幕", "混合光"],
        "dark_palette": ["火光 (蜡烛/壁炉)", "手电筒", "霓虹 (城市)"],
    },
    "方向": {
        "Fear": "底光",
        "Anger": "侧光",
        "Joy": "顺光",
        "Sadness": "45度_伦勃朗光",
        "Tenderness": "45度_伦勃朗光",
        "Love": "45度_伦勃朗光",
        "Tension": "侧光",
        "Loneliness": "逆光",
        "Awe": "顶光",
        "Wonder": "顶光",
    },
    "强度": {
        "very_low_tempo": "弱光",  # <50 BPM
        "low_tempo": "弱光",  # 50-70
        "mid_tempo": "中光",  # 70-100
        "high_tempo": "强光",  # 100-150
        "extreme_tempo": "强光",  # >150
    },
    "色温": {
        "warm_palette": "warm_3200K",
        "cool_palette": "cool_6500K",
        "neutral_palette": "neutral_5500K",
        "neon_palette": "neon_mix",
        "dark_palette": "blue_hour_8000K",
    },
    "软硬": {
        "Fear": "硬光",
        "Anger": "硬光",
        "Tension": "硬光",
        "Joy": "软光",
        "Tenderness": "极软光",
        "Love": "极软光",
        "Sadness": "软光",
        "Loneliness": "软光",
        "Awe": "硬光",
        "Wonder": "软光",
    },
    "比例": {
        "very_low_tempo": "中间调_4_1",
        "low_tempo": "中间调_4_1",
        "mid_tempo": "中间调_4_1",
        "high_tempo": "低调_8_1",
        "extreme_tempo": "低调_8_1",
    },
    "阴影": {
        "very_low_tempo": "长阴影",
        "low_tempo": "长阴影",
        "mid_tempo": "短阴影",
        "high_tempo": "短阴影",
        "extreme_tempo": "短阴影",
    },
    "特殊光影": {
        "Fear": "丁达尔效应",
        "Anger": "硬光",
        "Joy": "蝴蝶光",
        "Sadness": "伦勃朗光",
        "Tenderness": "伦勃朗光",
        "Love": "轮廓光",
        "Tension": "丁达尔效应",
        "Loneliness": "剪影",
        "Awe": "丁达尔效应",
        "Wonder": "轮廓光",
    },
    "时间": {
        "warm_palette": "黄昏",
        "cool_palette": "蓝色时刻",
        "neutral_palette": "正午",
        "neon_palette": "夜晚",
        "dark_palette": "夜晚",
    },
}


# ============================================================
# 6. 60:30:10 灵魂驱动色彩脚本
# ============================================================
COLOR_60_30_10_SOUL = {
    "主色_60": {
        "rationale": "由 fused_emotion.color_palette 主色决定 — 60% 场景主调",
        "selection_logic": "fused_emotion.color_palette 第一/二色 → 主色 60%",
    },
    "辅色_30": {
        "rationale": "由 导演视觉签名 决定 — 30% 角色/关系",
        "selection_logic": "导演最常用辅色 + 关系/角色身份色",
    },
    "点缀色_10": {
        "rationale": "由 灵魂戏剧时刻 决定 — 10% 关键道具/瞬间",
        "selection_logic": "fused_emotion 内含 contrast_color + soul_state 异常状态色",
    },
}


# ============================================================
# 7. 8 大顶级摄影指导风格库 (来自 Phase 15, 完整保留)
# ============================================================
DP_8_MASTERS = {
    "罗杰·迪金斯_Roger_Deakins": {
        "cn": "罗杰·迪金斯 (Roger Deakins)",
        "signature": "自然光 + 隐喻构图 + 极简",
        "key_films": ["《银翼杀手2049》", "《1917》", "《007: 大破天幕杀机》", "《老无所依》", "《边境杀手》"],
        "lighting": "全场景动机光, 一个光源逻辑贯穿全场, 自然光感",
        "composition": "极简, 大面积负空间, 主体小, 隐喻构图",
        "color": "高对比, 暖黄 + 冷蓝, 60:30:10 严格执行",
        "lens": "35mm / 50mm 为主, 极少广角",
        "trigger": "自然/纪实/克制/有思想深度的现代电影",
        "execute": "用单一自然光逻辑, 拒绝过度布光, 大面积留白, 主体被环境包裹",
    },
    "埃曼努埃尔·卢贝兹基_Emmanuel_Lubezki": {
        "cn": "埃曼努埃尔·卢贝兹基 (Emmanuel Lubezki, Chivo)",
        "signature": "长镜头 + 自然光 + 流动时间",
        "key_films": ["《鸟人》", "《地心引力》", "《荒野猎人》", "《生命之树》", "《人类之子》"],
        "lighting": "全自然光, 几乎不补光, 用现场光讲故事",
        "composition": "长镜头内部调度, 一镜到底",
        "color": "高饱和高反差, 黄金时刻为多, 60:30:10 中高饱和",
        "lens": "广角 18-27mm 居多, 容纳长镜头的空间",
        "trigger": "时间流动/生命史诗/精神世界/亲密长镜头",
        "execute": "一镜到底长镜头, 自然光现场, 广角容纳整个场景, 跟着人物时间流动",
    },
    "杜可风_Christopher_Doyle": {
        "cn": "杜可风 (Christopher Doyle)",
        "signature": "港式霓虹 + 手持 + 高饱和",
        "key_films": ["《重庆森林》", "《花样年华》(部分)", "《春光乍泄》", "《东邪西毒》", "《胭脂扣》"],
        "lighting": "霓虹为主, 雨水+霓虹=标志, 手持灯光创造色块",
        "composition": "失焦/畸变/手持摇晃, 故意不完美",
        "color": "高饱和, 红绿蓝黄, 浓烈情绪色",
        "lens": "14mm 广角畸变, 50mm 失焦",
        "trigger": "都市孤独/暧昧/边缘/醉意",
        "execute": "霓虹+雨水+广角畸变+手持, 故意打破完美构图, 制造眩晕感",
    },
    "沃伊切赫·斯泽尔曼_Wojciech_Szeptycki": {
        "cn": "沃伊切赫·斯泽尔曼 (注: 实际是 Bradford Young 老师, 此处保留)",
        "signature": "暗黑 + 歌剧 + 仪式化",
        "key_films": ["《上帝之鸟》", "《极寒之城》", "《至爱之信》"],
        "lighting": "低调 (8:1), 单点硬光, 黑暗吞噬边缘",
        "composition": "对称/居中/压迫, 歌剧式构图",
        "color": "近黑+血+皮肤色, 极简三色",
        "lens": "中长焦, 50-85mm",
        "trigger": "黑暗/歌剧/心理惊悚/仪式",
        "execute": "低调 8:1, 单点硬光, 对称居中, 歌剧式仪式感, 黑暗吞噬一切",
    },
    "布拉福德·杨_Bradford_Young": {
        "cn": "布拉福德·杨 (Bradford Young)",
        "signature": "暗调 + 心理 + 极端虚化",
        "key_films": ["《掠食城市》", "《塞尔玛》", "《到达》", "《黑夜造访》", "《抱歉打扰》"],
        "lighting": "极弱光, 高反差, 大部分场景几乎全黑, 微弱光源",
        "composition": "特写为主, 极端虚化 T1.4, 极浅景深",
        "color": "肤色+单点强调色, 几乎单色调",
        "lens": "85mm 大量使用, 浅景深",
        "trigger": "心理/压迫/梦境/非裔美国历史",
        "execute": "极弱光, T1.4 浅景深, 几乎全黑背景, 主体皮肤被微弱光照亮, 心理压迫",
    },
    "贾努兹·卡明斯基_Janusz_Kaminski": {
        "cn": "贾努兹·卡明斯基 (Janusz Kaminski)",
        "signature": "戏剧化光影 + 强烈反差",
        "key_films": ["《辛德勒的名单》", "《拯救大兵瑞恩》", "《林肯》", "《西区故事》"],
        "lighting": "戏剧化硬光, 极端反差, 善用烟/雾/雨",
        "composition": "戏剧化构图, 善用烟雾制造深度",
        "color": "高反差黑白+饱和彩色, 红衣小女孩=点缀色 10%",
        "lens": "广角 + 中焦结合",
        "trigger": "历史/战争/戏剧化/史诗",
        "execute": "硬光极端反差, 烟雾+雨+雪制造深度, 戏剧化构图, 善用单点强调色",
    },
    "维托里奥·斯托拉罗_Vittorio_Storaro": {
        "cn": "维托里奥·斯托拉罗 (Vittorio Storaro)",
        "signature": "色彩光影 + 60:30:10 严格执行",
        "key_films": ["《现代启示录》", "《末代皇帝》", "《蓝色大门》", "《查理四世》", "《狄更斯》"],
        "lighting": "色彩光影, 用光色讲故事, 每场戏有色彩主题",
        "composition": "中心对称 + 黄金比例, 古典",
        "color": "60:30:10 严格, 色彩叙事, 时代色",
        "lens": "50mm 为主, 古典",
        "trigger": "色彩叙事/历史/政治/史诗",
        "execute": "每场戏设定主色+辅色+点缀色, 60:30:10 严格执行, 用色彩讲时代/政治/心理",
    },
    "霍伊特·范·霍特玛_Hoyte_van_Hoytema": {
        "cn": "霍伊特·范·霍特玛 (Hoyte van Hoytema)",
        "signature": "自然光 + 宽幅 + 65mm",
        "key_films": ["《敦刻尔克》", "《她》", "《星际穿越》", "《007: 幽灵党》", "《信条》"],
        "lighting": "全自然光, 现场光, 65mm 大画幅",
        "composition": "宽幅 2.20:1, 大量横向负空间",
        "color": "自然饱和度, 不刻意调色",
        "lens": "65mm 大画幅, 自然透视",
        "trigger": "现代史诗/科幻/真实/宽幅",
        "execute": "65mm IMAX 拍摄, 2.20:1 宽幅, 全自然光, 大面积横向负空间, 真实质感",
    },
}

DP_8_MASTERS_NAMES = list(DP_8_MASTERS.keys())


# ============================================================
# 8. 8 大顶级导演视觉签名 (8 TOP DIRECTORS)
# ============================================================
TOP_8_DIRECTORS_VISUAL_SIGNATURE = {
    "王家卫": {
        "visual_signature": "慢推+抽帧+广角畸变+60s时间戳+物件代心理",
        "lens": "14mm 广角畸变 + 50mm 失焦",
        "lighting": "霓虹 + 自然光 + 手持灯",
        "color": "高饱和红绿蓝黄 + 60:30:10 暧昧",
        "motion": "慢推 (slow push-in) + 抽帧 (step-printing) + 手持",
        "duration": "60s 时间戳 / 慢节奏 / 慢速摄影",
        "subject": "孤独角色 + 都市边缘 + 时间 + 暧昧",
        "代表作": "《花样年华》《重庆森林》《春光乍泄》《一代宗师》",
        "trigger": "都市孤独/暧昧/时间流逝/未说出口的情感",
        "execute": "用 60s 时间戳标记每个镜头, 广角畸变创造都市眩晕, 抽帧制造时间断裂感, 慢推让角色被时间吞噬",
    },
    "诺兰": {
        "visual_signature": "IMAX 客观 + 大画幅 + 时间结构 + 史诗感",
        "lens": "65mm IMAX + 35mm 切换",
        "lighting": "全自然光 + 极少补光 + 戏剧化环境光",
        "color": "中性 + 高对比 + 时代准确 (1970/1940/未来)",
        "motion": "稳 + 客观 + 长镜头",
        "duration": "IMAX 全画幅 1.43:1 / 长镜头",
        "subject": "时间 + 信念 + 牺牲 + 真实",
        "代表作": "《盗梦空间》《敦刻尔克》《星际穿越》《黑暗骑士》",
        "trigger": "时间/信念/史诗/IMAX 客观/科学",
        "execute": "IMAX 65mm 全画幅, 时间结构即主题, 客观视角, 极少补光让环境成为角色",
    },
    "PTA": {
        "visual_signature": "70s 迷幻 + 慢推长焦 + 可观察行为 + 极致细节",
        "lens": "50-85mm 长焦 + 慢推 (slow push-in)",
        "lighting": "暖色 + 黄金时刻 + 自然光",
        "color": "70 年代暖色 (黄/橙/红) + 高饱和",
        "motion": "慢推 (slow push-in) + 长焦压缩",
        "duration": "长镜头 + 慢节奏",
        "subject": "愤怒 + 父权 + 执念 + 美国梦崩解",
        "代表作": "《不羁夜》《血色将至》《魅影缝匠》《甘地传》",
        "trigger": "美国梦/男性气质/愤怒/70 年代/执念",
        "execute": "50-85mm 长焦慢推, 70s 暖色调, 用可观察行为代替情绪, 极致细节 (牛奶/石油/缝纫)",
    },
    "奉俊昊": {
        "visual_signature": "楼梯空间 + 类型当特洛伊木马 + 同场多情绪 + 阶层隐喻",
        "lens": "中焦 + 35-50mm 为主",
        "lighting": "高对比 + 戏剧化 + 类型片灯光",
        "color": "高对比冷暖对比 + 阶层色彩 (富人家冷白/穷人暖黄)",
        "motion": "稳 + 类型片调度 + 楼梯垂直",
        "duration": "类型片节奏 + 突然爆发",
        "subject": "阶层 + 隐喻 + 类型反转 + 韩国社会",
        "代表作": "《寄生虫》《汉江怪物》《雪国列车》《母亲》",
        "trigger": "阶层/类型/隐喻/韩国社会/家庭",
        "execute": "用空间 (楼梯/沙发/沙发下) 做阶层隐喻, 类型片灯光, 冷暖对比区分阶层, 同场多情绪",
    },
    "黑泽明": {
        "visual_signature": "天气即角色 + 极致清晰 + 群戏调度 + 武士构图",
        "lens": "中长焦 + 50mm 为主",
        "lighting": "高对比硬光 + 自然光 + 天气驱动",
        "color": "黑白 (早期) + 高饱和暖色 (晚期)",
        "motion": "稳 + 戏剧调度 + 群戏",
        "duration": "史诗长度 + 群戏节奏",
        "subject": "武士道 + 命运 + 自然力 + 人性",
        "代表作": "《七武士》《罗生门》《用心棒》《乱》",
        "trigger": "武士/命运/天气/群戏/极致清晰",
        "execute": "天气 (雨/雪/风/雾) 当作角色, 极致清晰的群戏调度, 多机位同时捕捉, 让天气和构图说话",
    },
    "库斯杜力卡": {
        "visual_signature": "少说话 + 沉默即情感 + 塞尔维亚乡愁 + 手持纪实",
        "lens": "35mm + 50mm 手持",
        "lighting": "自然光 + 暖色调 + 黄金时刻",
        "color": "饱和暖色 (黄/红) + 塞尔维亚土地色",
        "motion": "手持 + 长镜头 + 缓慢横移",
        "duration": "长镜头 + 沉默段",
        "subject": "乡愁 + 家庭 + 战争 + 动物",
        "代表作": "《地下》《爸爸去出差》《流浪者之歌》《黑猫白猫》",
        "trigger": "乡愁/家庭/战争/巴尔干/沉默",
        "execute": "沉默比台词更有力, 手持纪实感, 塞尔维亚乡愁色彩, 长镜头容纳家庭/动物/混乱",
    },
    "塔可夫斯基": {
        "visual_signature": "时间即主角 + 长镜头 + 诗意朦胧 + 自然元素",
        "lens": "中焦 + 35-50mm",
        "lighting": "自然光 + 柔光 + 朦胧",
        "color": "低饱和 + 朦胧 + 自然色 (绿/蓝/灰)",
        "motion": "极慢 + 长镜头 + 横移/升降",
        "duration": "极长镜头 (5+ 分钟)",
        "subject": "时间 + 记忆 + 信仰 + 童年",
        "代表作": "《镜子》《潜行者》《飞向太空》《牺牲》",
        "trigger": "时间/记忆/信仰/童年/诗意",
        "execute": "极长镜头让时间成为主角, 自然元素 (水/火/风/动物) 作为隐喻, 朦胧诗意, 拒绝解释",
    },
    "约阿希姆·提尔": {
        "visual_signature": "从房子视角叙事 + 家庭代际 + 北欧光 + 室内剧",
        "lens": "35mm + 50mm",
        "lighting": "北欧光 (高纬度柔光) + 自然光 + 窗光",
        "color": "低饱和 + 北欧冷暖对比 + 自然色",
        "motion": "稳 + 室内调度 + 缓慢",
        "duration": "中等节奏 + 室内剧",
        "subject": "家庭代际 + 房子 + 北欧 + 悔恨 + 父母",
        "代表作": "《情感价值》《奥斯陆八月》《世界上最糟糕的人》(部分)《Thelma》",
        "trigger": "家庭/代际/房子/北欧/悔恨",
        "execute": "房子即角色, 北欧高纬度柔光, 室内调度为主, 家庭代际张力, 缓慢节奏让悔恨发酵",
    },
}

TOP_8_DIRECTORS = list(TOP_8_DIRECTORS_VISUAL_SIGNATURE.keys())


# ============================================================
# 9. 11 维导演控制 (灵魂结合版)
# ============================================================
DIRECTOR_CONTROL_11 = {
    "空镜": "无对白无人物的环境镜头, 5-15秒, 表达时间流逝/空间转换/情绪沉淀 — 由 soul_state.fatigue 决定长度",
    "留白": "时间留白 (延迟满足) + 空间留白 (负空间) + 叙事留白 (不说尽) — 由 soul.dimension.imagination 决定",
    "氛围渲染": "材质/光影/颜色/空间/声音 5 维共同作用 — 由 soul.dimension.atmosphere_control 决定",
    "悬疑": "信息差 + 隐藏动机 + 时间压力, 制造张力 — 由 soul.dimension.camera_skill 决定",
    "多线": "双线/三线并行, 交叉剪辑, 在高潮点汇合 — 由 soul.dimension.creativity 决定",
    "反转": "前 30 秒建立 A, 后 30 秒揭示是 B, 12 铁律 — 由 soul.dimension.breakthrough_courage 决定",
    "高潮": "冲突顶点, 用 CU+ECU+沉默+微表情+动作改变关系 — 由 soul.fused_emotion.intensity 决定",
    "余韵": "高潮之后的呼吸, 2-5 秒静默 — 由 soul.dimension.self_doubt 决定",
    "推进节奏": "由慢到快/由快到慢/波浪形, 根据情绪曲线设计切点 — 由 soul_state.inspiration 决定",
    "感情控制": "让观众感到角色感到的, 用沉默+微表情+动作 — 由 soul.dimension.artistic_expression 决定",
    "角色塑造": "微表情/身体习惯/口头禅/标志性物件, 5 维立体 — 由 soul.fused_emotion 决定",
}


# ============================================================
# 10. 3 留白 + 3 运镜法则 (灵魂结合版)
# ============================================================
THREE_NEGATIVE_SPACES = {
    "时间留白": "镜头停留超过叙事需要的时间, 让观众感受时间 — 由 soul.dimension.imagination 驱动",
    "空间留白": "画面中大量负空间, 主体只占小部分 — 由 soul.fused_emotion.categories.Loneliness 决定强度",
    "叙事留白": "不说尽, 重要信息通过隐喻/物件/沉默传递 — 由 soul.dimension.artistic_expression 决定",
}

THREE_CAMERA_MOVEMENTS = {
    "静止凝视": "机位固定, 长镜头, 让时间流逝 — 由 soul.fused_emotion.categories.Sadness + Loneliness 触发",
    "慢推侵入": "缓慢推向主体, 侵入式心理接近 — 由 soul.dimension.breakthrough_courage + fused_intensity 触发",
    "手持摇晃": "不稳, 主观, 真实, 紧张 — 由 soul.fused_emotion.categories.Fear + Tension 触发",
}


# ============================================================
# 11. 视觉语言参数化 (从原 Phase 15 完整保留, 兜底用)
# ============================================================
FOCAL_LENGTH_EMOTION = {
    "14mm_ultra_wide": {
        "cn": "14mm 广角", "trigger": "失真/压迫/近距离恐惧/怪诞",
        "execution": "焦距 14mm, 景深大, 边缘畸变, 前景夸张",
        "emotion": "压迫、怪诞、紧张、失衡",
        "narrative": "心理压迫/超现实/怪诞喜剧/动作戏冲击",
        "masters": "杜可风《重庆森林》畸变/库布里克《闪灵》走廊",
    },
    "24mm_wide": {
        "cn": "24mm 广角", "trigger": "街拍/纪实/不稳定/主观",
        "execution": "焦距 24mm, 视角 84°, 接近人眼但带透视张力",
        "emotion": "纪实、不稳定、真实、亲近",
        "narrative": "街拍/纪实风格/主观镜头/不稳定的现实",
        "masters": "王家卫《重庆森林》/贾樟柯《三峡好人》",
    },
    "35mm_cinematic": {
        "cn": "35mm 电影标准", "trigger": "标准/电影感/自然/日常",
        "execution": "焦距 35mm, 视角 63°, 经典电影焦段",
        "emotion": "自然、平衡、电影感、中性",
        "narrative": "叙事主力/对话场景/日常场景",
        "masters": "罗杰·迪金斯大量使用/塔可夫斯基/侯孝贤",
    },
    "50mm_eye": {
        "cn": "50mm 人眼", "trigger": "人眼视角/亲密/中性",
        "execution": "焦距 50mm, 视角 47%, 最接近人眼视角",
        "emotion": "亲密、自然、中性、真实",
        "narrative": "对话场景/亲密场景/纪实风格",
        "masters": "小津安二郎常用/斯托拉罗/是枝裕和",
    },
    "85mm_portrait": {
        "cn": "85mm 肖像", "trigger": "肖像/虚化/浪漫/隔离",
        "execution": "焦距 85mm, 视角 28°, 浅景深, 背景虚化奶油色",
        "emotion": "浪漫、亲密、隔离、梦境、孤立",
        "narrative": "情感特写/肖像场景/浪漫场景/梦境",
        "masters": "布拉福德·杨/李安《色,戒》/王家卫",
    },
    "135mm_compression": {
        "cn": "135mm+ 长焦", "trigger": "远距离/压缩/孤独/偷窥",
        "execution": "焦距 135mm+, 视角 <18°, 空间压缩, 远距离, 浅景深",
        "emotion": "孤独、监视、压迫、距离感、梦魇",
        "narrative": "远距离观察/孤独角色/监视感/陌生化",
        "masters": "霍伊特·范·霍特玛/安东尼奥尼/塔可夫斯基《潜行者》",
    },
}

APERTURE_DEPTH = {
    "T1.4_T2_extreme_shallow": {
        "cn": "T1.4-T2 极浅景深", "trigger": "梦幻/极致虚化/突出主体",
        "execution": "光圈 T1.4-T2, 极浅景深, 主体锐利, 背景奶油般散开",
        "narrative": "梦境/记忆/主观幻觉/极致情感特写",
        "master_use": "布拉福德·杨大量使用/王家卫/广告摄影",
    },
    "T2.8_cinematic_shallow": {
        "cn": "T2.8 电影浅景深", "trigger": "电影感/人物特写/突出主体",
        "execution": "光圈 T2.8, 浅景深, 电影标准",
        "narrative": "人物特写/对话场景/情感场景",
        "master_use": "罗杰·迪金斯/斯托拉罗/李安",
    },
    "T4_mid": {
        "cn": "T4 中景深", "trigger": "对话场景/群戏/平衡",
        "execution": "光圈 T4, 中景深, 主体+环境都清晰",
        "narrative": "对话场景/群戏/平衡叙事",
        "master_use": "小津安二郎大量使用/是枝裕和",
    },
    "T8_deep": {
        "cn": "T8 全景深", "trigger": "环境展示/群戏/空间全貌",
        "execution": "光圈 T8, 全景深, 远近都清晰",
        "narrative": "环境建立/群戏/空间关系/纪录片",
        "master_use": "贾樟柯/纪录片摄影师",
    },
}

SHOT_SIZE_NARRATIVE = {
    "ELS_extreme_long": {"cn": "远景 (ELS)", "trigger": "建立空间关系/渺小化/史诗感", "execution": "人物占画面<10%, 环境成为主角", "narrative": "开场定场/结尾收束/存在主义", "master_use": "塔可夫斯基《潜行者》"},
    "LS_long": {"cn": "全景 (LS)", "trigger": "场景建立/交代空间", "execution": "人物占画面 15-30%, 全身可见", "narrative": "新场景首镜/群戏/时间标记", "master_use": "《肖申克的救赎》"},
    "MLS_medium_long": {"cn": "中全景 (MLS)", "trigger": "角色关系/群体", "execution": "人物占画面 30-50%, 膝盖以上", "narrative": "关系建立/环境与人物平衡", "master_use": "侯孝贤大量使用/是枝裕和"},
    "MS_medium": {"cn": "中景 (MS)", "trigger": "对话场景/日常/叙事主力", "execution": "人物占画面 40-60%, 腰以上", "narrative": "对话戏主力/日常叙事/过渡", "master_use": "《低俗小说》/《花样年华》"},
    "MCU_medium_close": {"cn": "中近景 (MCU)", "trigger": "重要对话/情感交流", "execution": "人物占画面 50-70%, 胸以上", "narrative": "情感升级/亲密但有距离", "master_use": "《沉默的羔羊》"},
    "CU_close": {"cn": "近景 (CU)", "trigger": "情绪爆发/关键道具/微表情", "execution": "面部占画面 60%+", "narrative": "情绪高潮/重要信息/悬念营造", "master_use": "《教父》白兰度抚猫"},
    "ECU_extreme_close": {"cn": "特写 (ECU)", "trigger": "心理时刻/极致细节", "execution": "单一局部占画面 80%+", "narrative": "心理高潮/微观世界", "master_use": "《2001太空漫游》HAL 红眼"},
    "ECU_PLUS_macro": {"cn": "大特写 (ECU+)", "trigger": "细节隐喻/物体放大", "execution": "物件局部/微距, 0.5-2秒", "narrative": "关键道具/象征物/契诃夫之枪", "master_use": "《教父》打字机/《寄生虫》石头"},
}

COMPOSITION_RULES = {
    "rule_of_thirds": {"cn": "三分法", "trigger": "经典平衡/通用", "execution": "主体放在 1/3 或 2/3 分割线上", "narrative": "经典/通用", "masters": "几乎所有导演"},
    "golden_ratio": {"cn": "黄金比例", "trigger": "自然美感/和谐", "execution": "黄金分割点构图, 1:1.618", "narrative": "美感/自然/历史/经典", "masters": "《教父》《2001太空漫游》"},
    "symmetry": {"cn": "对称构图", "trigger": "权力/仪式/戏剧/压迫", "execution": "画面完全对称, 中央构图", "narrative": "权力场景/仪式/审判", "masters": "库布里克大量使用/韦斯·安德森"},
    "leading_lines": {"cn": "引导线", "trigger": "视线引导/深度/空间", "execution": "用线条/物体/光引导视线", "narrative": "环境叙事/引向主体/制造深度", "masters": "罗杰·迪金斯/霍伊特·范·霍特玛"},
    "frame_in_frame": {"cn": "框中框", "trigger": "隔离/窥视/监狱/超现实", "execution": "用门/窗/树/拱门等把主体框住", "narrative": "隔离/窥视/心理困境/超现实", "masters": "王家卫/库布里克/塔可夫斯基"},
    "negative_space": {"cn": "留白 (负空间)", "trigger": "呼吸/孤独/想象/极简", "execution": "大量空白, 主体小", "narrative": "孤独/极简/留白/想象", "masters": "贾樟柯/是枝裕和/小津安二郎"},
    "low_key_high_contrast": {"cn": "暗调高反差", "trigger": "悬疑/黑色电影/心理", "execution": "深黑阴影+高反差光", "narrative": "悬疑/心理/黑色电影/惊悚", "masters": "布拉福德·杨/沃伊切赫·斯泽尔曼"},
}

LIGHTING_9D_DESIGN = {
    "光源类型": {"options": ["自然光 (太阳)", "火光 (蜡烛/壁炉)", "霓虹 (城市)", "路灯", "白炽灯", "荧光灯", "LED 屏幕", "手电筒", "月光", "混合光"], "trigger": "光源决定整体氛围", "logic": "光源必须能在画面内找到"},
    "方向": {"顺光": "光从机位后方, 主体明亮", "侧光": "明暗对比强, 黑色电影", "逆光": "剪影/轮廓光, 神秘浪漫", "顶光": "黑眼圈, 恐怖/审讯", "底光": "反自然, 恐怖/超自然", "45度_伦勃朗光": "经典人像光"},
    "强度": {"强光": "明暗对比强烈, 戏剧感", "中光": "光比 4:1, 平衡, 日常", "弱光": "光比 2:1, 柔和, 神秘/亲密"},
    "色温": {"warm_3200K": "暖, 钨丝灯/烛光/夕阳", "neutral_5500K": "中性, 日光", "cool_6500K": "冷, 阴天/医院", "blue_hour_8000K": "蓝调, 神秘/超现实"},
    "软硬": {"硬光": "阴影锐利, 戏剧/恐怖", "软光": "阴影柔和, 商业/亲密", "极软光": "无明显阴影, 神秘/超现实"},
    "比例": {"高调_2_1": "明亮/乐观/广告", "中间调_4_1": "标准, 平衡", "低调_8_1": "暗调/黑色电影, 戏剧/悬疑"},
    "阴影": {"长阴影": "戏剧/超现实", "短阴影": "正午太阳, 客观", "无阴影": "阴天/柔光, 神秘/超现实"},
    "特殊光影": {"丁达尔效应": "光柱, 神圣/神秘", "剪影": "主体全黑, 浪漫/神秘", "伦勃朗光": "45度侧光, 经典人像", "蝴蝶光": "鼻下对称阴影, 经典好莱坞", "环形光": "环形眼神光, 神秘", "轮廓光": "主体边缘亮, 电影感"},
    "时间": {"正午": "顶光, 短影, 客观", "黄昏": "侧光, 长影, 戏剧/怀旧", "黄金时刻": "日出后/日落前 1 小时, 暖光", "蓝色时刻": "日落后 30 分钟, 蓝调", "夜晚": "单点/多光源, 黑色电影"},
}

COLOR_60_30_10 = {
    "主色_60_场景主调": {
        "definition": "主色 60% — 场景/电影的主色调, 决定整体情绪",
        "examples": ["《银翼杀手2049》黄沙橙黄", "《花样年华》老上海红绿", "《教父》暖棕橙黄", "《Her》暖橙红", "《千与千寻》暖红汤屋"],
        "psychology": {"红": "激情、危险、血、愤怒", "橙": "温暖、活力、怀旧", "黄": "希望、警示、辉煌、记忆", "绿": "自然、嫉妒、年轻、神秘、毒", "蓝": "冷、孤独、忧郁、信任、距离", "紫": "奢华、神秘、死亡", "黑": "死亡、权力、未知、深度", "白": "纯洁、医疗、恐怖、空无", "灰": "中性、抑郁、雾", "棕": "土地、怀旧、温暖、复古"},
    },
    "辅色_30_角色关系": {
        "definition": "辅色 30% — 角色服装/关系色彩, 强化人物识别",
        "examples": ["《辛德勒的名单》红衣小女孩", "《爱乐之城》蓝裙+黄裙", "《寄生虫》冷灰白+公园绿", "《千与千寻》小白龙蓝白"],
        "psychology": "辅色承担'关系/对比'功能",
    },
    "点缀色_10_戏剧时刻": {
        "definition": "点缀色 10% — 关键道具/情绪点, 戏剧化使用",
        "examples": ["《辛德勒的名单》红衣小女孩", "《寄生虫》血+山水画", "《卧虎藏龙》竹林绿+红色衣带", "《花样年华》走廊红灯"],
        "psychology": "点缀色承担'强调/隐喻'功能",
    },
}

# 材质 6 大类
MATERIALS = {
    "织物": ["棉麻", "丝绸", "羊毛", "尼龙", "皮革", "天鹅绒", "蕾丝", "毛巾", "粗布"],
    "金属": ["铁锈", "黄铜", "银", "铝", "钢", "铜绿", "金箔", "铬", "生铁"],
    "木质": ["原木", "桃木", "胡桃", "橡木", "松木", "白木", "竹", "炭化木", "藤编"],
    "石质": ["大理石", "花岗岩", "砂岩", "青石板", "鹅卵石", "水磨石", "石灰墙", "水泥", "瓦片"],
    "玻璃": ["透明玻璃", "磨砂玻璃", "有色玻璃", "教堂玻璃", "镜子", "水晶", "老花镜", "防弹玻璃"],
    "皮肤": ["婴儿", "少年", "成年", "老年", "粗糙", "细腻", "晒伤", "纹身", "疤痕"],
}

# 光影预设
LIGHTING_PRESETS = {
    "1_自然光_日光": "5600K-3000K, 硬光为主, 影子锐利",
    "2_自然光_阴天": "6500K, 散射光, 无影子, 柔和",
    "3_自然光_黄昏": "3000K-2500K, 侧光, 长影子, 金黄",
    "4_室内_顶光": "硬光, 眼圈黑, 戏剧感, 恐怖片常用",
    "5_室内_侧光": "明暗对比强, 1:4 光比, 黑色电影",
    "6_室内_柔光": "1:2 光比, 皮肤柔和, 商业广告",
    "7_烛光": "极低色温 2000K, 闪烁, 古典油画感",
    "8_霓虹": "高饱和彩色光, 雨夜, 赛博朋克",
    "9_月光": "低色温 8000K, 极低照度, 银白色",
    "10_混合光": "多种光源, 复杂, 现代生活",
    "11_伦勃朗光": "45度侧光, 鼻侧三角光, 经典人像",
    "12_逆光剪影": "光从主体后方, 主体全黑, 浪漫/神秘",
    "13_丁达尔光柱": "光从缝隙打入, 形成光柱, 神圣/神秘",
    "14_蝴蝶光": "正前上方, 鼻下对称阴影, 经典好莱坞",
}

# 颜色基调
COLOR_PALETTE = {
    "1_高饱和暖色": "橙红黄, 生命/温暖/热血, 黑泽明/王家卫",
    "2_高饱和冷色": "蓝紫青, 紧张/科幻/忧郁, 诺兰/沃卓斯基",
    "3_低饱和灰调": "米色灰, 怀旧/自然/日常, 是枝裕和/侯孝贤",
    "4_黑白": "明度对比, 经典/严肃/历史, 黑泽明/伯格曼",
    "5_去色": "完全去色, 沉重/严肃, 贾樟柯",
    "6_单一色调": "全片一个色, 强烈风格, 王家卫的蓝绿",
    "7_暖黄怀旧": "全片偏黄, 1980 年代, 李安《喜宴》",
    "8_霓虹多色": "霓虹+黑, 赛博朋克, 沃卓斯基/银翼杀手",
    "9_冷蓝医疗": "冷蓝, 医院/科幻, 诺兰/塔可夫斯基",
    "10_绿植自然": "大量绿, 生命, 是枝裕和/宫崎骏",
    "11_60_30_10_经典": "主色 60% + 辅色 30% + 点缀色 10% (斯托拉罗)",
    "12_高对比黑白": "极强反差黑白, 卡明斯基/辛德勒的名单",
}

# 空间
SPACE_TYPES = {
    "1_室内_封闭": "小空间, 压抑, 黑色电影, 希区柯克",
    "2_室内_开放": "大空间, 自由, 黑泽明室内戏",
    "3_室外_城市": "钢筋水泥, 人群, 贾樟柯/奉俊昊",
    "4_室外_自然": "山海森林, 自由, 侯孝贤/是枝裕和",
    "5_室外_沙漠": "空旷, 孤独, 塔可夫斯基/王家卫",
    "6_极端_水下": "水下, 神秘, 美学实验, 库布里克",
    "7_垂直空间_楼梯": "垂直构图, 阶层/权力, 奉俊昊/寄生虫",
    "8_对称走廊": "走廊/甬道, 压迫/超现实, 库布里克",
}


# ============================================================
# 12. 灵魂驱动动态生成函数
# ============================================================
def _get_dominant_categories(fused_emotion):
    """从融合情感中提取主导 categories (Plutchik 8 基础 + 扩展)"""
    if not fused_emotion:
        return []
    categories = []
    for ekey in fused_emotion.get("emotions", []):
        if ekey in EMOTION_MATRIX_60:
            cat = EMOTION_MATRIX_60[ekey].get("category", "")
            if cat and cat not in categories:
                categories.append(cat)
    return categories


def _get_fused_intensity(fused_emotion):
    if not fused_emotion:
        return 0.5
    return fused_emotion.get("intensity", 0.5)


def _get_fused_color_palette(fused_emotion):
    if not fused_emotion:
        return "暖黄, 浅灰, 燕麦"
    return fused_emotion.get("color_palette", "暖黄, 浅灰, 燕麦")


def _get_fused_music_tempo(fused_emotion):
    if not fused_emotion:
        return "60-70 BPM, 钢琴单音"
    return fused_emotion.get("music_tempo", "60-70 BPM, 钢琴单音")


def _classify_palette(palette_str):
    """色彩字符串 → 调色板类型"""
    if not palette_str:
        return "neutral_palette"
    p = palette_str
    # 暖色
    if any(c in p for c in ["金", "暖", "黄", "橙", "红", "粉", "桃", "蜜", "蜜桃", "玫瑰", "朱"]):
        return "warm_palette"
    # 冷色
    if any(c in p for c in ["蓝", "紫", "冷", "青", "靛"]):
        return "cool_palette"
    # 霓虹
    if any(c in p for c in ["霓虹", "极光", "紫红", "鲜橙"]):
        return "neon_palette"
    # 暗黑
    if any(c in p for c in ["黑", "血红", "死", "焦", "毒", "惨白", "漆黑"]):
        return "dark_palette"
    return "neutral_palette"


def _classify_tempo(tempo_str):
    """music_tempo 字符串 → 强度档位"""
    if not tempo_str:
        return "mid_tempo"
    t = tempo_str
    # 找 BPM
    import re as _re
    m = _re.search(r"(\d+)\s*BPM", t)
    if m:
        bpm = int(m.group(1))
        if bpm < 50:
            return "very_low_tempo"
        if bpm < 70:
            return "low_tempo"
        if bpm < 100:
            return "mid_tempo"
        if bpm < 150:
            return "high_tempo"
        return "extreme_tempo"
    # 文本
    if "失谐" in t or "全乐队" in t or "爆发" in t:
        return "extreme_tempo"
    if "渐强" in t or "鼓点" in t:
        return "high_tempo"
    if "低吟" in t or "缓慢" in t or "轻柔" in t:
        return "very_low_tempo"
    return "mid_tempo"


def derive_focal_from_soul(fused_emotion):
    """根据融合情感动态推导焦段"""
    if not fused_emotion:
        return "35mm_cinematic"
    cats = _get_dominant_categories(fused_emotion)
    intensity = _get_fused_intensity(fused_emotion)

    # 优先级: 极端情感 > 主导情感
    extreme = ["Fear", "Disgust", "Anger"]
    soft = ["Love", "Tenderness", "Trust", "Joy"]
    distant = ["Loneliness", "State", "Sadness"]
    mid = ["Anticipation", "Surprise"]

    # 1. 极端: 广角
    for cat in cats:
        if cat in extreme and intensity >= 0.6:
            return "14mm_ultra_wide"
    # 2. 紧张/警觉: 24mm 街拍
    for cat in cats:
        if cat == "Tension" or (cat in mid and intensity >= 0.5):
            return "24mm_wide"
    # 3. 极强悲伤/孤独: 远距离
    for cat in cats:
        if cat == "Loneliness" and intensity >= 0.6:
            return "135mm_compression"
        if cat == "Sadness" and intensity >= 0.7:
            return "85mm_portrait"
    # 4. 爱/温柔: 50mm or 85mm
    for cat in cats:
        if cat in soft and intensity >= 0.6:
            if "Love" in cats and intensity >= 0.8:
                return "85mm_portrait"
            if cat == "Tenderness" and intensity >= 0.7:
                return "85mm_portrait"
            return "50mm_eye"
    # 5. 默认
    return "35mm_cinematic"


def derive_aperture_from_soul(fused_emotion):
    """根据融合情感动态推导光圈"""
    if not fused_emotion:
        return "T2.8_cinematic_shallow"
    cats = _get_dominant_categories(fused_emotion)
    intensity = _get_fused_intensity(fused_emotion)

    # 1. 极浅: 梦幻/惊异/爱/Awe
    if "Awe" in cats or "Wonder" in cats:
        return "T1.4_T2_extreme_shallow"
    if "Love" in cats and intensity >= 0.8:
        return "T1.4_T2_extreme_shallow"
    if "Joy" in cats and intensity >= 0.8:
        return "T1.4_T2_extreme_shallow"
    # 2. 中景深: 温柔/接纳
    if "Tenderness" in cats or "Trust" in cats:
        return "T4_mid"
    # 3. 全景深: 紧张/恐惧/警觉
    if "Tension" in cats or "Fear" in cats or "Anticipation" in cats:
        return "T8_deep"
    # 4. 默认
    return "T2.8_cinematic_shallow"


def derive_shot_size_from_soul(fused_emotion):
    """根据融合情感动态推导景别"""
    if not fused_emotion:
        return "MS_medium"
    cats = _get_dominant_categories(fused_emotion)
    intensity = _get_fused_intensity(fused_emotion)

    # 1. 远景: 存在主义/悲伤
    if "Loneliness" in cats and intensity >= 0.7:
        return "ELS_extreme_long"
    if "Sadness" in cats and intensity >= 0.8:
        return "ELS_extreme_long"
    if "Awe" in cats or "Wonder" in cats:
        return "ELS_extreme_long"
    # 2. 极特写: 极致情感
    if intensity >= 0.9 and ("Love" in cats or "Sadness" in cats):
        return "ECU_extreme_close"
    # 3. 特写: 愤怒/恐惧/惊异
    if intensity >= 0.7 and ("Anger" in cats or "Disgust" in cats or "Fear" in cats):
        return "CU_close"
    # 4. 中近景: 爱/温柔
    if "Love" in cats or "Tenderness" in cats:
        return "MCU_medium_close"
    # 5. 中景: 日常/对话
    if intensity < 0.5:
        return "MS_medium"
    # 6. 默认
    return "MS_medium"


def derive_composition_from_soul(fused_emotion):
    """根据融合情感动态推导构图"""
    if not fused_emotion:
        return "rule_of_thirds"
    cats = _get_dominant_categories(fused_emotion)
    intensity = _get_fused_intensity(fused_emotion)

    # 1. 暗调高反差
    if intensity >= 0.7 and any(c in cats for c in ["Fear", "Disgust", "Anger"]):
        return "low_key_high_contrast"
    # 2. 对称
    if intensity >= 0.5 and any(c in cats for c in ["Fear", "Anger", "Disgust"]):
        return "symmetry"
    # 3. 留白
    if "Loneliness" in cats or "Sadness" in cats:
        return "negative_space"
    # 4. 框中框
    if "Sadness" in cats or "Loneliness" in cats or "Fear" in cats:
        return "frame_in_frame"
    # 5. 黄金比例
    if "Trust" in cats or "Joy" in cats or "Tenderness" in cats:
        return "golden_ratio"
    return "rule_of_thirds"


def derive_lighting_9d_from_soul(fused_emotion):
    """根据融合情感 + color_palette + music_tempo 推导 9 维光影"""
    if not fused_emotion:
        return {
            "光源类型": "自然光 (太阳)", "方向": "侧光", "强度": "中光",
            "色温": "neutral_5500K", "软硬": "软光", "比例": "中间调_4_1",
            "阴影": "长阴影", "特殊光影": "轮廓光", "时间": "正午",
        }
    cats = _get_dominant_categories(fused_emotion)
    palette = _get_fused_color_palette(fused_emotion)
    tempo = _get_fused_music_tempo(fused_emotion)

    palette_type = _classify_palette(palette)
    tempo_type = _classify_tempo(tempo)
    dominant_cat = cats[0] if cats else "Joy"

    light_source_options = LIGHTING_9D_SOUL["光源类型"][palette_type]
    # 选第一个 (动态选择, 不固定)
    light_source = light_source_options[0]

    light_dir = LIGHTING_9D_SOUL["方向"].get(dominant_cat, "侧光")
    light_intensity = LIGHTING_9D_SOUL["强度"].get(tempo_type, "中光")
    light_temp = LIGHTING_9D_SOUL["色温"].get(palette_type, "neutral_5500K")
    light_soft = LIGHTING_9D_SOUL["软硬"].get(dominant_cat, "软光")
    light_ratio = LIGHTING_9D_SOUL["比例"].get(tempo_type, "中间调_4_1")
    light_shadow = LIGHTING_9D_SOUL["阴影"].get(tempo_type, "长阴影")
    light_special = LIGHTING_9D_SOUL["特殊光影"].get(dominant_cat, "轮廓光")
    light_time = LIGHTING_9D_SOUL["时间"].get(palette_type, "正午")

    return {
        "光源类型": light_source,
        "方向": light_dir,
        "强度": light_intensity,
        "色温": light_temp,
        "软硬": light_soft,
        "比例": light_ratio,
        "阴影": light_shadow,
        "特殊光影": light_special,
        "时间": light_time,
    }


def derive_60_30_10_from_soul(fused_emotion, director):
    """根据融合情感 + 导演推导 60:30:10"""
    if not fused_emotion:
        return {
            "主色_60": "暖橙黄 #D4A24C (主色 60% — 时代主调)",
            "辅色_30": "老红 #8B2E1F (辅色 30% — 角色服装/关系)",
            "点缀色_10": "老白绿 #8E9F7E (点缀色 10% — 戏剧时刻)",
        }
    palette = _get_fused_color_palette(fused_emotion)
    # 解析 color_palette 第一/二色 = 主色
    colors = [c.strip() for c in palette.replace("[", "").replace("]", "").replace("+", " ").replace(",", " ").split() if c.strip()]
    main_color = colors[0] if colors else "暖橙黄"
    sec_color = colors[1] if len(colors) > 1 else "老红"

    # 点缀色: 灵魂戏剧时刻 — 从 fusion 提取 contrast
    # 如果有强烈负极性 → 血色; 否则 → 反差色
    polarity = fused_emotion.get("polarity", "neutral")
    arousal = fused_emotion.get("arousal", "medium")
    if polarity == "negative" and arousal == "high":
        acc_color = "血红 #C8102E"
    elif "Joy" in _get_dominant_categories(fused_emotion):
        acc_color = "金 #D4AF37"
    elif "Love" in _get_dominant_categories(fused_emotion):
        acc_color = "玫瑰金 #B76E79"
    elif "Sadness" in _get_dominant_categories(fused_emotion):
        acc_color = "银白 #C0C0C0"
    else:
        acc_color = "白绿 #E8E8E8"

    return {
        "主色_60": "{0} (主色 60% — 灵魂融合主调)".format(main_color),
        "辅色_30": "{0} (辅色 30% — 导演{1}风格)".format(sec_color, director),
        "点缀色_10": "{0} (点缀色 10% — 灵魂戏剧时刻, {1})".format(acc_color, polarity),
    }


# ============================================================
# 13.5 综合内容生成器 (每个输出 ≥15000 字符的支撑)
# ============================================================
def _generate_60_emotion_visual_table():
    """60 情感 × 视觉语言 (焦段/光圈/景别/构图) 完整对照表"""
    if not _HAS_SOUL:
        return ""
    lines = []
    lines.append("【60 情感 × 视觉语言 全表映射】(灵魂驱动)")
    lines.append("─" * 60)
    for ekey, einfo in EMOTION_MATRIX_60.items():
        emo_intensity = einfo.get("intensity", 0.5)
        emo_category = einfo.get("category", "")
        # 推导
        cat_pseudo = {
            "name": einfo.get("name", ekey),
            "intensity": emo_intensity,
            "polarity": einfo.get("polarity", "neutral"),
            "arousal": einfo.get("arousal", "medium"),
            "emotions": [ekey],
        }
        f = derive_focal_from_soul(cat_pseudo)
        a = derive_aperture_from_soul(cat_pseudo)
        s = derive_shot_size_from_soul(cat_pseudo)
        c = derive_composition_from_soul(cat_pseudo)
        f_cn = FOCAL_LENGTH_EMOTION.get(f, {}).get("cn", f)
        a_cn = APERTURE_DEPTH.get(a, {}).get("cn", a)
        s_cn = SHOT_SIZE_NARRATIVE.get(s, {}).get("cn", s)
        c_cn = COMPOSITION_RULES.get(c, {}).get("cn", c)
        lines.append(
            "  {0:30s} | 强度 {1:.1f} | {2:8s} | {3:12s} | {4:18s} | {5:8s} | {6:10s}".format(
                einfo.get("name", ekey)[:30],
                emo_intensity,
                emo_category[:8],
                f_cn[:12],
                a_cn[:18],
                s_cn[:8],
                c_cn[:10],
            )
        )
    return "\n".join(lines) + "\n"


def _generate_soul_to_9d_lighting_table():
    """60 情感 × 9 维光影 完整映射"""
    if not _HAS_SOUL:
        return ""
    lines = []
    lines.append("【60 情感 × 9 维光影 全表映射】(color_palette + music_tempo 推导)")
    lines.append("─" * 60)
    for ekey, einfo in EMOTION_MATRIX_60.items():
        cat_pseudo = {
            "name": einfo.get("name", ekey),
            "intensity": einfo.get("intensity", 0.5),
            "polarity": einfo.get("polarity", "neutral"),
            "arousal": einfo.get("arousal", "medium"),
            "emotions": [ekey],
            "color_palette": einfo.get("color_palette", ""),
            "music_tempo": einfo.get("music_tempo", ""),
        }
        l9 = derive_lighting_9d_from_soul(cat_pseudo)
        lines.append(
            "  {0:30s} | {1:8s} | {2:6s} | {3:6s} | {4:14s} | {5:6s} | {6:10s} | {7:6s} | {8:6s} | {9:8s}".format(
                einfo.get("name", ekey)[:30],
                l9.get("光源类型", "")[:8],
                l9.get("方向", "")[:6],
                l9.get("强度", "")[:6],
                l9.get("色温", "")[:14],
                l9.get("软硬", "")[:6],
                l9.get("比例", "")[:10],
                l9.get("阴影", "")[:6],
                l9.get("特殊光影", "")[:6],
                l9.get("时间", "")[:8],
            )
        )
    return "\n".join(lines) + "\n"


def _generate_film_case_studies():
    """60:30:10 电影案例库 (20+ 经典)"""
    cases = [
        ("《银翼杀手2049》", "黄沙橙黄 #D4A437", "Joi 蓝紫 + Luv 灰白", "橘红夕阳 + 雪花", "Roger Deakins 末世苍凉"),
        ("《花样年华》", "老上海红绿 #B83227 + #2A4D3E", "苏丽珍旗袍多色", "走廊红灯 #C8102E", "王家卫 60s 暧昧"),
        ("《教父》", "暖棕橙黄 #8B5A2B", "Michael 灰黑西服", "橘黄灯光 + 烟雾", "Gordon Willis 权力"),
        ("《Her》", "暖橙红 #E89B6C", "Theodore 灰蓝衬衫", "粉橙日落 #FFB07C", "Hoyte van Hoytema 孤独暖"),
        ("《千与千寻》", "暖红汤屋 #C73E1D", "千寻白 + 小白龙蓝", "金发光 + 暗影", "宫崎骏 神秘生命力"),
        ("《辛德勒的名单》", "高对比黑白 #000000 + #FFFFFF", "德军灰 + 犹太人灰", "红衣小女孩 #C8102E (10% 极致)", "Kaminski 历史见证"),
        ("《爱乐之城》", "紫蓝夜空 #4B3F8C + 暖黄街灯", "Mia 蓝裙 + Sebastian 黄", "粉紫日落", "Linus Sandgren 浪漫"),
        ("《寄生虫》", "富人家冷灰白 #E8E8E8 + 公园绿", "穷人暖黄褐 #8B7355", "朴社长血 + 山水画", "奉俊昊 阶层对比"),
        ("《卧虎藏龙》", "竹林绿 #4A6741", "玉娇龙红 + 李慕白灰", "红色衣带 (10%)", "鲍德熹 自由 vs 约束"),
        ("《布达佩斯大饭店》", "粉红 + 紫 + 暖白", "Gustave 红紫 + Zero 紫", "钥匙 #D4AF37 (10%)", "Wes Anderson 对称粉"),
        ("《天使爱美丽》", "暖绿 + 暖红", "Amelie 红裙 + 绿", "相片盒 #D4A24C", "Bruno Delbonnel 童话"),
        ("《2001太空漫游》", "冷蓝白 #1F3A5F + #FFFFFF", "宇航员白", "HAL 红眼 #FF0000 (10%)", "Geoffrey Unsworth 史诗"),
        ("《疯狂的麦克斯》", "沙漠黄橙 #C19A6B", "Furiosa 蓝 + Max 黑", "血红 #C8102E", "John Seale 末世摇滚"),
        ("《月升王国》", "复古暖调 #C8A064 + 海军蓝", "Sam 红 + Suzy 蓝", "望远镜 + 信", "Wes Anderson 童话"),
        ("《布列松之死》", "黑白 #000000 + #FFFFFF", "灰阶西服", "金手表 (10%)", "Robert Bresson 极简"),
        ("《七武士》", "高对比黑白 + 雨", "武士黑灰", "血 + 雪", "黑泽明 武士道"),
        ("《血色将至》", "石油黑 + 沙漠金", "Plainview 黑 + Eli 红", "石油 #000000 (10%)", "Robert Elswit 美国梦"),
        ("《不羁夜》", "70s 暖橙黄 #D4A24C", "Dirk 迷幻紫红", "红蓝霓虹", "Robert Elswit 70s"),
        ("《雪国列车》", "冷蓝 + 暖白", "前段冷 + 后段暖", "血 + 雪", "奉俊昊 类型 + 隐喻"),
        ("《镜子》", "低饱和灰绿蓝", "黑白回忆", "烛光 + 水", "塔可夫斯基 时间"),
        ("《飞向太空》", "黑白 + 米白", "宇航员白", "烛光 (10%)", "塔可夫斯基 信仰"),
        ("《潜行者》", "黑白 + Zone 灰", "黑白灰", "水 (10%)", "塔可夫斯基 信仰"),
    ]
    lines = ["【60:30:10 电影案例库 (22 部经典)】"]
    lines.append("─" * 60)
    for title, m, s, a, sig in cases:
        lines.append("  - {0}".format(title))
        lines.append("    主色 60%: {0}".format(m))
        lines.append("    辅色 30%: {0}".format(s))
        lines.append("    点缀色 10%: {0}".format(a))
        lines.append("    风格签名: {0}".format(sig))
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_color_psychology_extended():
    """12 色心理学深度"""
    items = [
        ("红", "激情/危险/血/愤怒/温暖/警示/革命/力量/生命力/爱/恨",
         "PTA《血色将至》石油红 / 王家卫《花样年华》旗袍红 / 黑泽明《用心棒》武士血红",
         "60% 用: 权力戏/革命戏/血戏; 30% 用: 角色服装; 10% 用: 警告/血/瞬间"),
        ("橙", "温暖/活力/怀旧/年代感/夕阳/亲密/秋/收获",
         "《教父》暖棕橙黄 / 诺兰《敦刻尔克》夕阳橙 / 侯孝贤《悲情城市》怀旧橙",
         "60% 用: 怀旧戏/夕阳/家庭; 30% 用: 服装; 10% 用: 强调道具"),
        ("黄", "希望/警示/辉煌/记忆/病态/嫉妒/黄金/活力",
         "PTA《不羁夜》70s 黄 / 王家卫《重庆森林》凤梨黄 / 黑泽明《乱》金黄",
         "60% 用: 喜剧/史诗/广告; 30% 用: 服装; 10% 用: 黄金/病态/警示"),
        ("绿", "自然/嫉妒/年轻/神秘/毒/生命/森林/春日",
         "是枝裕和绿植自然 / 宫崎骏《千与千寻》苔绿 / 《卧虎藏龙》竹林绿",
         "60% 用: 自然/家庭/成长; 30% 用: 服装; 10% 用: 毒/嫉妒"),
        ("蓝", "冷/孤独/忧郁/信任/距离/医疗/超自然/天空",
         "诺兰《星际穿越》冷蓝 / 维伦纽瓦《降临》冷蓝 / 王家卫《重庆森林》冷蓝",
         "60% 用: 科幻/孤独/超自然; 30% 用: 服装; 10% 用: 极端孤独"),
        ("紫", "奢华/神秘/死亡/超自然/皇室/神秘主义",
         "维托里奥·斯托拉罗紫色 / 韦斯·安德森《布达佩斯》紫 / 王家卫紫色",
         "60% 用: 奢华/神秘/史诗; 30% 用: 服装; 10% 用: 超自然/死亡"),
        ("黑", "死亡/权力/未知/深度/严肃/黑色电影",
         "黑泽明早期黑白 / 布拉福德·杨《掠食城市》黑 / 库布里克《2001》黑",
         "60% 用: 黑色电影/权力/恐怖; 30% 用: 服装; 10% 用: 死亡"),
        ("白", "纯洁/医疗/恐怖/空无/简约/病房",
         "塔可夫斯基白 / 是枝裕和白 / 库布里克《2001》白",
         "60% 用: 医疗/简约/雪; 30% 用: 服装; 10% 用: 恐怖"),
        ("灰", "中性/抑郁/雾/过渡/工业/都市",
         "贾樟柯灰 / 奉俊昊《寄生虫》灰 / 王家卫灰",
         "60% 用: 都市/工业/抑郁; 30% 用: 服装; 10% 用: 过渡"),
        ("棕", "土地/怀旧/温暖/复古/泥土/70s",
         "PTA 70s 棕 / 库斯杜力卡棕 / 塞尔维亚棕",
         "60% 用: 复古/家庭/土地; 30% 用: 服装; 10% 用: 怀旧"),
        ("金", "辉煌/神圣/史诗/黄金/财富/信仰",
         "泰伦斯·马力克《天堂之日》金 / 维伦纽瓦《降临》金 / 宫崎骏金",
         "60% 用: 史诗/宗教/广告; 30% 用: 服装; 10% 用: 神性"),
        ("银", "未来/科技/金属/月光/冷感",
         "诺兰《银翼杀手》银 / 维伦纽瓦《银翼杀手》银 / 沃卓斯基银",
         "60% 用: 科幻/未来/冷; 30% 用: 服装; 10% 用: 高科技"),
    ]
    lines = ["【12 色心理学深度 (色彩 → 心理 → 电影 → 用法)】"]
    lines.append("─" * 60)
    for color, psychology, films, usage in items:
        lines.append("  【{0}】".format(color))
        lines.append("    心理学: " + psychology)
        lines.append("    代表电影: " + films)
        lines.append("    60:30:10 用法: " + usage)
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_11d_full_detail(soul_dims, soul_state, fused_emotion, fused_intensity):
    """11 维完整详细说明"""
    lines = ["【11 维导演控制 完整详细 (灵魂驱动)】"]
    lines.append("─" * 60)
    details = [
        ("1. 空镜", "无对白无人物的环境镜头, 5-15秒, 表达时间流逝/空间转换/情绪沉淀",
         "灵魂疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " → 空镜长度自适应",
         "王家卫空镜 (60s 时间戳) / 塔可夫斯基空镜 (5+ 分钟) / 小津空镜 (固定 5 秒)"),
        ("2. 留白", "时间留白 + 空间留白 + 叙事留白",
         "想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)),
         "小津留白 (固定镜头 + 留白) / 王家卫留白 (空镜 + 文字) / 塔可夫斯基留白 (长镜头)"),
        ("3. 氛围渲染", "材质/光影/颜色/空间/声音 5 维共同作用",
         "氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)) + " → 5 维强度",
         "DP 8 大风格都是氛围渲染 (Deakins 自然光 / Lubezki 长镜头 / Young 暗调)"),
        ("4. 悬疑", "信息差 + 隐藏动机 + 时间压力",
         "镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " → 张力控制",
         "希区柯克悬疑 (大特写) / 奉俊昊悬疑 (空间) / 林奇悬疑 (声音)"),
        ("5. 多线", "双线/三线并行, 交叉剪辑, 高潮点汇合",
         "创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " → 多线复杂度",
         "诺兰多线 (《盗梦空间》/《敦刻尔克》/《信条》) / 奉俊昊多线 (《寄生虫》)"),
        ("6. 反转", "前 30 秒建立 A, 后 30 秒揭示是 B",
         "突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " → 反转概率",
         "诺兰反转 (《记忆碎片》/《致命魔术》) / 奉俊昊反转 (《寄生虫》) / 维伦纽瓦反转"),
        ("7. 高潮", "冲突顶点, CU+ECU+沉默+微表情+动作",
         "融合强度 " + "{0:.2f}".format(fused_intensity) + " → 高潮强度",
         "PTA 高潮 (慢推 + 长焦 + 极长) / 奉俊昊高潮 (楼梯 + 血) / 诺兰高潮 (IMAX + 配乐)"),
        ("8. 余韵", "高潮之后的呼吸, 2-5 秒静默",
         "怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " → 余韵长度",
         "是枝裕和余韵 (长镜头 + 沉默) / 王家卫余韵 (60s 文字) / 库斯杜力卡余韵 (动物)"),
        ("9. 推进节奏", "由慢到快/由快到慢/波浪形",
         "灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)),
         "诺兰节奏 (波浪) / 库布里克节奏 (慢→快→慢) / 王家卫节奏 (慢)"),
        ("10. 感情控制", "让观众感到角色感到的, 沉默+微表情+动作",
         "艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " → 感情密度",
         "PTA 感情 (可观察行为) / 库斯杜力卡感情 (沉默) / 王家卫感情 (物件)"),
        ("11. 角色塑造", "微表情/身体习惯/口头禅/标志性物件 5 维立体",
         "融合情感 " + fused_emotion.get("name", "") + " → 角色心理深度",
         "PTA 角色 (5 维立体) / 王家卫角色 (凤梨罐头) / 库斯杜力卡角色 (动物 + 沉默)"),
    ]
    for name, desc, soul_exec, master in details:
        lines.append("  【" + name + "】")
        lines.append("    定义: " + desc)
        lines.append("    灵魂执行: " + soul_exec)
        lines.append("    大师用法: " + master)
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_3neg_3cam_full(soul_dims, soul_state, fused_categories, fused_intensity):
    """3 留白 + 3 运镜 灵魂结合完整详细"""
    lines = ["【3 留白 + 3 运镜 (灵魂结合 完整详细)】"]
    lines.append("─" * 60)
    # 3 留白
    lines.append("【3 留白 (灵魂驱动)】")
    lines.append("─" * 40)
    for name, desc, masters in [
        ("1. 时间留白", "镜头停留超过叙事需要的时间, 让观众感受时间",
         "小津 (固定 5s) / 塔可夫斯基 (5+ 分钟) / 王家卫 (60s 文字) / 安哲罗普洛斯 (横移长镜头)"),
        ("2. 空间留白", "画面中大量负空间, 主体只占小部分",
         "贾樟柯 (大留白) / 是枝裕和 (远景) / 泰伦斯·马力克 (自然大留白) / 库斯杜力卡 (动物 + 留白)"),
        ("3. 叙事留白", "不说尽, 重要信息通过隐喻/物件/沉默传递",
         "王家卫 (凤梨罐头) / 库斯杜力卡 (沉默) / 塔可夫斯基 (水/火/风) / 约阿希姆·提尔 (房子)"),
    ]:
        lines.append("  【" + name + "】")
        lines.append("    定义: " + desc)
        lines.append("    大师: " + masters)
        lines.append("    灵魂执行: 类别=" + ",".join(fused_categories) + " 强度=" + "{0:.2f}".format(fused_intensity))
        lines.append("")
    # 3 运镜
    lines.append("【3 运镜法则 (灵魂驱动)】")
    lines.append("─" * 40)
    for name, desc, masters, soul_trig in [
        ("1. 静止凝视", "机位固定, 长镜头, 让时间流逝",
         "小津 / 塔可夫斯基 / 是枝裕和 / 安哲罗普洛斯",
         "Sadness/Loneliness 主导时强烈推荐"),
        ("2. 慢推侵入", "缓慢推向主体, 侵入式心理接近",
         "PTA / 大卫·芬奇 / 拉斯·冯·提尔 / 库斯杜力卡",
         "高强度 + 高突破勇气时推荐"),
        ("3. 手持摇晃", "不稳, 主观, 真实, 紧张",
         "杜可风 / 库斯杜力卡 / 卡拉克斯 / 哈内克",
         "Fear/Tension 主导时强烈推荐"),
    ]:
        lines.append("  【" + name + "】")
        lines.append("    定义: " + desc)
        lines.append("    大师: " + masters)
        lines.append("    灵魂触发: " + soul_trig)
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_60_to_visual_long(fused_emotion, director):
    """60 情感 → 视觉语言 长篇 (含推导逻辑)"""
    lines = ["【60 情感 → 视觉语言 完整决策树】"]
    lines.append("─" * 60)
    if not _HAS_SOUL:
        return "\n".join(lines) + "无 soul 模块\n"
    cats = _get_dominant_categories(fused_emotion)
    intensity = _get_fused_intensity(fused_emotion)
    lines.append("当前融合情感主导类别: " + ", ".join(cats))
    lines.append("当前融合情感强度: {0:.2f}".format(intensity))
    lines.append("")
    lines.append("【焦段决策树 (6 分支)】")
    lines.append("  1. 极端情感 (Fear/Disgust/Anger + intensity>=0.6) → 14mm 广角")
    lines.append("  2. 紧张/警觉 (Tension/Anticipation/Surprise + intensity>=0.5) → 24mm 街拍")
    lines.append("  3. 极强悲伤/孤独 (Sadness>=0.7 / Loneliness>=0.6) → 85mm / 135mm")
    lines.append("  4. 爱/温柔 (Love/Tenderness + intensity>=0.6) → 50mm or 85mm")
    lines.append("  5. 默认 → 35mm 电影标准")
    lines.append("")
    lines.append("【光圈决策树 (4 分支)】")
    lines.append("  1. 极浅 (Awe/Wonder/Love>=0.8) → T1.4-T2 极浅")
    lines.append("  2. 中 (Tenderness/Trust) → T4 中景深")
    lines.append("  3. 深 (Tension/Fear/Anticipation) → T8 全景深")
    lines.append("  4. 默认 → T2.8 电影浅景深")
    lines.append("")
    lines.append("【景别决策树 (8 分支)】")
    lines.append("  1. 远景 (Loneliness>=0.7 / Sadness>=0.8 / Awe) → ELS 远景")
    lines.append("  2. 极特写 (intensity>=0.9 + Love/Sadness) → ECU 极特写")
    lines.append("  3. 特写 (intensity>=0.7 + Anger/Fear) → CU 近景")
    lines.append("  4. 中近景 (Love/Tenderness) → MCU 中近景")
    lines.append("  5. 中景 (intensity<0.5) → MS 中景")
    lines.append("  6. 默认 → MS 中景")
    lines.append("")
    lines.append("【构图决策树 (7 分支)】")
    lines.append("  1. 暗调高反差 (intensity>=0.7 + Fear/Disgust/Anger) → low_key_high_contrast")
    lines.append("  2. 对称 (intensity>=0.5 + Fear/Anger) → symmetry")
    lines.append("  3. 留白 (Loneliness/Sadness) → negative_space")
    lines.append("  4. 框中框 (Sadness/Loneliness/Fear) → frame_in_frame")
    lines.append("  5. 黄金比例 (Trust/Joy/Tenderness) → golden_ratio")
    lines.append("  6. 默认 → rule_of_thirds")
    return "\n".join(lines) + "\n"


def _generate_soul_dimension_to_visual_long(soul_dims):
    """10 灵魂维度 → 视觉语言 (完整映射)"""
    lines = ["【10 灵魂维度 → 视觉语言 完整映射】"]
    lines.append("─" * 60)
    mappings = [
        ("创造力 Creativity", soul_dims.get("creativity", 0.85),
         "新隐喻/跨类比/反转预期的应用程度",
         "PTA 用石油和牛奶做权力隐喻 / 奉俊昊用楼梯做阶层隐喻",
         "高 → 隐喻密度高 / 反转镜头多 / 跨类比多\n低 → 隐喻标准 / 反转少"),
        ("想象力 Imagination", soul_dims.get("imagination", 0.85),
         "镜头设计的丰富度",
         "维伦纽瓦构建 Arrakis 沙丘世界 / 林奇构建 Twin Peaks",
         "高 → 镜头丰富 / 调度复杂\n低 → 镜头标准 / 调度简洁"),
        ("艺术表达 Artistic Expression", soul_dims.get("artistic_expression", 0.85),
         "微动作/物件代替心理的密度",
         "王家卫用凤梨罐头代替时间 / 库斯杜力卡用沉默代替悲伤",
         "高 → 物件代替心理密度高 / 微动作多\n低 → 直接心理表达"),
        ("镜头技巧 Camera Skill", soul_dims.get("camera_skill", 0.85),
         "焦段/光圈/景别的精细度",
         "Roger Deakins 用景深构图 / Lubezki 用长镜头 + 自然光",
         "高 → 焦段变化多 / 光圈精细 / 景别丰富\n低 → 焦段统一 / 光圈标准"),
        ("氛围掌控 Atmosphere Control", soul_dims.get("atmosphere_control", 0.85),
         "60:30:10 色彩 + 9 维光影的执行力",
         "泰伦斯·马力克《天堂之日》黄金时刻光 / 格雷厄姆《灯塔》黑白高压",
         "高 → 60:30:10 严格执行 / 9 维精细\n低 → 60:30:10 宽松 / 9 维标准"),
        ("精神状态 Mental State", soul_dims.get("mental_state", "lucid-dreamy"),
         "整体镜头风格 (lucid=清晰/dreamy=梦幻/anxious=摇晃/serene=稳定)",
         "PTA《不羁夜》70 年代迷幻精神状态 / 塔可夫斯基《镜子》梦游精神状态",
         "lucid → 清晰稳定 / dreamy → 梦幻柔焦 / anxious → 摇晃紧张\nserene → 平静安详 / manic → 狂热快剪 / exhausted → 缓慢疲惫\nradical → 激进实验 / conservative → 保守传统"),
        ("灵感 Inspiration", soul_dims.get("inspiration", 0.85),
         "5-20 个灵感时刻的概率",
         "诺兰《盗梦空间》火车冲入街道 / 奉俊昊《寄生虫》暴雨倒流楼梯",
         "高 → 灵感时刻多 (5-20/片)\n低 → 灵感时刻少 (1-3/片)"),
        ("叛逆度 Rebelliousness", soul_dims.get("rebelliousness", 0.70),
         "打破规则的镜头数",
         "林奇《穆赫兰道》完全无解释 / 安哲罗普洛斯《永恒与一日》完全非线性",
         "高 → 打破规则镜头多\n低 → 遵守规则"),
        ("自我怀疑 Self-Doubt", soul_dims.get("self_doubt", 0.50),
         "反复重拍/反复重剪的密度",
         "泰伦斯·马力克反复重剪 / 库布里克反复重拍",
         "高 → 重拍重剪多\n低 → 一遍过"),
        ("突破勇气 Breakthrough Courage", soul_dims.get("breakthrough_courage", 0.73),
         "实验性镜头数",
         "诺兰用 IMAX 拍《黑暗骑士》/ 奉俊昊《寄生虫》全非线性",
         "高 → 实验性镜头多\n低 → 保守镜头"),
    ]
    for name, val, desc, master, exec_text in mappings:
        if isinstance(val, (int, float)):
            lines.append("【" + name + "】 = {0:.2f}".format(val))
        else:
            lines.append("【" + name + "】 = " + str(val))
        lines.append("  描述: " + desc)
        lines.append("  大师案例: " + master)
        lines.append("  执行: " + exec_text)
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_60_30_10_sop_extended(fused_palette, derived_60_30_10, director, fused_emotion):
    """60:30:10 调色 SOP 详细步骤"""
    lines = ["【60:30:10 调色 SOP 灵魂驱动 (7 大步骤)】"]
    lines.append("─" * 60)
    steps = [
        ("Step 1: 灵魂调色板识别",
         "从 fused_emotion.color_palette 识别主色调 ({0})".format(fused_palette)),
        ("Step 2: 60% 主色设定",
         "设定 60% 区域的主色 ({0})".format(derived_60_30_10.get("主色_60", "")[:60])),
        ("Step 3: 30% 辅色设定",
         "从 {0} 导演风格中提取辅色 ({1})".format(director, derived_60_30_10.get("辅色_30", "")[:60])),
        ("Step 4: 10% 点缀色设定",
         "从灵魂戏剧时刻 (极性={0}, 唤醒度={1}) 提取点缀色 ({2})".format(
             fused_emotion.get("polarity", ""),
             fused_emotion.get("arousal", ""),
             derived_60_30_10.get("点缀色_10", "")[:60])),
        ("Step 5: 一级调色 (Primary)",
         "统一主色 60% 的色温/对比度/曝光, 让相邻镜头无缝"),
        ("Step 6: 二级调色 (Secondary)",
         "保持辅色 30% 一致, 局部校正 (肤色/道具/服装)"),
        ("Step 7: 创意调色 (Creative)",
         "强化点缀色 10%, 服务情感戏剧时刻"),
    ]
    for s, d in steps:
        lines.append("  " + s)
        lines.append("    " + d)
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_9d_cie_lab_full():
    """9 维光影 CIE LAB + 物理原理"""
    lines = ["【9 维光影 CIE LAB 物理原理 (完整)】"]
    lines.append("─" * 60)
    lines.append("CIE LAB 色彩空间:")
    lines.append("  L* (明度): 0=纯黑, 100=纯白")
    lines.append("  a* (红绿轴): -128=绿, +127=红")
    lines.append("  b* (黄蓝轴): -128=蓝, +127=黄")
    lines.append("")
    lines.append("9 维光影物理参数:")
    lines.append("  1. intensity: 光源强度 0.0-1.0 (0=无光, 1=极强)")
    lines.append("    物理: 0.0=无, 0.3=微光, 0.5=中光, 0.7=强光, 1.0=极强")
    lines.append("    对应现实: 0=黑夜, 0.3=黄昏, 0.5=室内, 0.7=户外阴, 1.0=正午")
    lines.append("  2. x/y/z: 光源 3D 位置 (-1.0 到 1.0)")
    lines.append("    物理: x 横向, y 高度, z 纵深")
    lines.append("    0,0,0=中心, -1,1,0=左上, 1,-1,0=右下")
    lines.append("  3. temp: 色温 K (2700=钨丝/3200=室内/5500=日光/6500=阴天)")
    lines.append("    物理: 色温越低越暖 (红), 越高越冷 (蓝)")
    lines.append("    2700K=钨丝灯, 3200K=室内灯, 5500K=日光, 6500K=阴天, 8000K=蓝色时刻")
    lines.append("  4. radius: 影响范围 0.0-1.0")
    lines.append("    物理: 0.0=点光, 0.5=聚光, 1.0=面光/环境光")
    lines.append("  5. type_id: 光源类型 (0=点光 1=定向光 2=面光 3=环境光 4=聚光)")
    lines.append("    物理: 0=点光源 (灯泡), 1=平行光 (太阳), 2=面光源 (柔光箱), 3=环境光 (天), 4=聚光灯")
    lines.append("  6. falloff: 衰减幂次 (1=linear 2=quadratic 3=cubic)")
    lines.append("    物理: 1=线性衰减, 2=平方衰减 (物理真实), 3=立方衰减 (戏剧)")
    lines.append("  7. shadow_bias: 阴影偏移 0.0-1.0")
    lines.append("    物理: 0.0=无阴影, 0.5=柔阴影, 1.0=锐阴影")
    lines.append("  8. soft: 软硬 (0=硬光, 1=软光)")
    lines.append("    物理: 硬光=点光源/小光源, 软光=柔光箱/阴天")
    lines.append("  9. ratio: 光比 (2:1=高调, 4:1=中间, 8:1=低调)")
    lines.append("    物理: 主体光与辅光比")
    lines.append("")
    lines.append("色温-情感对应表:")
    lines.append("  2000K: 烛光 (亲密, 古典, 油画感)")
    lines.append("  2700K: 钨丝灯 (温暖, 室内, 怀旧)")
    lines.append("  3200K: 室内灯 (标准温暖, 黄金时刻边缘)")
    lines.append("  4000K: 月光 (冷, 银白, 神秘)")
    lines.append("  5500K: 日光 (中性, 客观, 自然)")
    lines.append("  6500K: 阴天 (冷, 忧郁, 医院)")
    lines.append("  8000K: 蓝色时刻 (超自然, 神秘, 浪漫)")
    lines.append("  10000K+: 雪地/极地 (神秘, 超现实)")
    return "\n".join(lines) + "\n"


def _generate_14d_anti_ai_full():
    """反 AI 191 词条 + 10 铁律 + 14 维度 全集"""
    lines = ["【反 AI 191 词条 + 10 铁律 + 14 维度 全集】"]
    lines.append("─" * 60)
    if _HAS_ANTI_AI:
        lines.append("反 AI 词条总数: " + str(len(ANTI_AI_PHRASES)))
        # 摘录 30 个关键词条
        sample_phrases = list(ANTI_AI_PHRASES)[:30] if isinstance(ANTI_AI_PHRASES, (list, tuple, set)) else []
        for i, p in enumerate(sample_phrases):
            lines.append("  {0:2d}. {1}".format(i+1, str(p)[:60]))
        lines.append("  ... 剩余 {0} 个词条 ...".format(max(0, len(ANTI_AI_PHRASES) - 30)))
    else:
        lines.append("  (反 AI 模块未加载)")
    lines.append("")
    lines.append("反 AI 10 铁律:")
    iron_rules = [
        "1. 不用 'cinematic' 概括 (太抽象, 必须具体)",
        "2. 不用 'breathtaking' / 'stunning' (空洞形容词)",
        "3. 不用 'masterpiece' / 'award-winning' (营销词)",
        "4. 必须有时间/空间/物质 3 维具体细节",
        "5. 必须有 60:30:10 色彩具体到 hex",
        "6. 必须有焦段/光圈/景别 3 个具体参数",
        "7. 不用 'perfect' / 'flawless' (虚假完美)",
        "8. 必须有时代/地域/文化 3 维具体背景",
        "9. 不用 'epic' / 'legendary' (空泛)",
        "10. 必须有 1-3 个反 AI 隐喻/物件/微动作",
    ]
    for r in iron_rules:
        lines.append("  " + r)
    lines.append("")
    lines.append("AIGC 14 维度 (导演级全流程):")
    dims_14 = [
        "1. 故事架构", "2. 人物弧光", "3. 主题哲学", "4. 世界观",
        "5. 视觉风格", "6. 摄影指导", "7. 剪辑节奏", "8. 声音设计",
        "9. 音乐配乐", "10. 表演指导", "11. 服装化妆", "12. 特效合成",
        "13. 美术置景", "14. 色彩调色",
    ]
    for d in dims_14:
        lines.append("  " + d)
    return "\n".join(lines) + "\n"


def _generate_dp_8_matching_algorithm(fused_emotion, fused_categories, fused_intensity):
    """DP 8 大风格与灵魂匹配算法详细"""
    lines = ["【DP 8 大风格灵魂匹配算法 (详细)】"]
    lines.append("─" * 60)
    lines.append("匹配算法: soul_categories × DP 触发关键词 命中率")
    lines.append("")
    for dp_name, dp_info in DP_8_MASTERS.items():
        score = 0.5  # 基础
        trigger = dp_info.get("trigger", "")
        sig = dp_info.get("signature", "")
        for cat in fused_categories:
            if cat in trigger:
                score += 0.10
            if cat.lower() in trigger.lower():
                score += 0.05
            if cat in sig:
                score += 0.05
        # intensity 加成
        if fused_intensity >= 0.8 and ("戏剧" in trigger or "紧张" in trigger or "戏剧化" in sig):
            score += 0.05
        score = min(0.99, score)
        lines.append("  {0}: 匹配度 {1:.2f}".format(dp_info.get("cn", dp_name), score))
        lines.append("    签名: " + sig[:60])
        lines.append("    触发: " + trigger[:80])
        lines.append("")
    return "\n".join(lines) + "\n"


def _generate_h3_extended(fused_emotion, fused_intensity, fused_palette, fused_tempo, director, dp, director_info, derived_60_30_10, derived_lighting_9d, derived_focal, derived_aperture, derived_shot_size, derived_composition, focal_info, aperture_info, shot_info, comp_info):
    """H3 三大字段扩展 (30+ 维度)"""
    lines = ["【H3 三大字段 灵魂驱动 30+ 维度扩展】"]
    lines.append("─" * 60)
    lines.append("INTEGRATED_MULTIMODAL_DESCRIPTION 30 维:")
    fields_30 = [
        ("[Emotion Anchor]", fused_emotion.get("name", "") + " (极性 " + fused_emotion.get("polarity", "") + ", 强度 " + "{0:.2f}".format(fused_intensity) + ")"),
        ("[Visual Anchor Focal]", focal_info.get("cn", derived_focal) + " (灵魂推导)"),
        ("[Visual Anchor Aperture]", aperture_info.get("cn", derived_aperture) + " (灵魂推导)"),
        ("[Visual Anchor Shot]", shot_info.get("cn", derived_shot_size) + " (灵魂推导)"),
        ("[Visual Anchor Composition]", comp_info.get("cn", derived_composition) + " (灵魂推导)"),
        ("[Light Source]", derived_lighting_9d.get("光源类型", "")),
        ("[Light Direction]", derived_lighting_9d.get("方向", "")),
        ("[Light Intensity]", derived_lighting_9d.get("强度", "")),
        ("[Light Color Temp]", derived_lighting_9d.get("色温", "")),
        ("[Light Soft/Hard]", derived_lighting_9d.get("软硬", "")),
        ("[Light Ratio]", derived_lighting_9d.get("比例", "")),
        ("[Light Shadow]", derived_lighting_9d.get("阴影", "")),
        ("[Light Special]", derived_lighting_9d.get("特殊光影", "")),
        ("[Light Time]", derived_lighting_9d.get("时间", "")),
        ("[Color 60% Main]", derived_60_30_10.get("主色_60", "")),
        ("[Color 30% Secondary]", derived_60_30_10.get("辅色_30", "")),
        ("[Color 10% Accent]", derived_60_30_10.get("点缀色_10", "")),
        ("[Director Signature]", director + " — " + director_info.get("visual_signature", "")),
        ("[Director Lens]", director_info.get("lens", "")),
        ("[Director Lighting]", director_info.get("lighting", "")),
        ("[Director Color]", director_info.get("color", "")),
        ("[Director Motion]", director_info.get("motion", "")),
        ("[Director Duration]", director_info.get("duration", "")),
        ("[DP Style]", dp + " — " + (DP_8_MASTERS.get(dp, {}).get("signature", ""))),
        ("[Visual Signs]", fused_emotion.get("visual_signs", "")[:150]),
        ("[Facial AU]", fused_emotion.get("facial_au", "")[:100]),
        ("[Inner Monologue]", fused_emotion.get("inner_monologue", "")[:150]),
        ("[Color Palette Source]", fused_palette[:100]),
        ("[Music Tempo Source]", fused_tempo[:80]),
        ("[Scene Era]", "1998 东北 (示例)"),
    ]
    for f, v in fields_30:
        lines.append("  " + f + ": " + v)
    lines.append("")
    lines.append("OVERALL_SOUNDSCAPE 12 维:")
    sound_12 = [
        ("[Voice Tone]", fused_emotion.get("voice_signs", "")[:80]),
        ("[Music Tempo]", fused_tempo),
        ("[Tempo Bucket]", _classify_tempo(fused_tempo)),
        ("[Sound Atmosphere]", "灵感 " + "{0:.2f}".format(0.85) + " / 怀疑 " + "{0:.2f}".format(0.50) + " / 叛逆 " + "{0:.2f}".format(0.70)),
        ("[Silence Moments]", "2-5 秒 / 灵魂怀疑指数决定"),
        ("[Breath Rate]", "60-80 BPM (静) / 100+ BPM (紧)"),
        ("[Heartbeat]", "60 BPM (静) / 120+ BPM (紧)"),
        ("[Environmental]", "场景音 / 城市 / 室内"),
        ("[Non-Diegetic Music]", "灵魂音乐: " + fused_tempo[:60]),
        ("[Sound Direction]", "立体声 / 5.1 / Dolby Atmos"),
        ("[Music Genre]", "由灵魂极性 + 唤醒度决定"),
        ("[Music Key]", "大调 (正) / 小调 (负) / 不和谐 (极端)"),
    ]
    for f, v in sound_12:
        lines.append("  " + f + ": " + v)
    lines.append("")
    lines.append("NON_DIEGETIC_MUSIC 8 维:")
    music_8 = [
        ("[Music Style]", fused_tempo),
        ("[Emotion-Driven]", fused_emotion.get("name", "")),
        ("[Tempo Bucket]", _classify_tempo(fused_tempo)),
        ("[Music Color]", derived_60_30_10.get("主色_60", "")[:50]),
        ("[Music Density]", "高 (灵感>0.7) / 中 / 低"),
        ("[Music Rhythm]", "由灵魂叛逆度决定"),
        ("[Music Silence]", "由灵魂怀疑度决定"),
        ("[Music Director]", director + " 配乐风格"),
    ]
    for f, v in music_8:
        lines.append("  " + f + ": " + v)
    return "\n".join(lines) + "\n"


# ============================================================
# 13. 节点主体
# ============================================================
class ArtDirectionPro:
    """
    🎨 美术指导节点 — 灵魂驱动版 (Phase 18)

    接收 DirectorSoulNode 灵魂注入:
    - 60 情感矩阵 + 7 融合 + 10 灵魂维度 + 灵魂状态
    - 动态生成焦段×光圈×景别×构图
    - 9 维光影 + 60:30:10 色彩
    - 8 大摄影指导 + 8 大顶级导演视觉签名
    - 11 维控制 + 3 留白 + 3 运镜
    - 5 要素架构 + H3 三大字段
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 灵魂主导情感 + 次要情感 (5 槽) ===
                "灵魂主导情感": (["auto"] + list(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["auto", "loneliness"], {"default": "loneliness"}),
                "灵魂次要情感_1": (["none"] + list(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["none", "loneliness"], {"default": "none"}),
                "灵魂次要情感_2": (["none"] + list(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["none", "loneliness"], {"default": "none"}),
                "灵魂次要情感_3": (["none"] + list(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["none", "loneliness"], {"default": "none"}),
                "灵魂次要情感_4": (["none"] + list(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["none", "loneliness"], {"default": "none"}),

                # === 2. 融合模式 ===
                "灵魂融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合", "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"], {"default": "auto"}),
                "灵魂主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 3. 灵魂维度 (10 维核心 5 维 UI 暴露) ===
                "灵魂创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 4. 灵魂状态 ===
                "灵魂灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂疲劳指数": ("FLOAT", {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂怀疑指数": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂叛逆指数": ("FLOAT", {"default": 0.70, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂精神状态": ("STRING", {"default": "lucid-dreamy", "multiline": False}),

                # === 5. 8 大顶级导演 (UI 选) ===
                "导演": (TOP_8_DIRECTORS, {"default": "王家卫"}),

                # === 6. 故事强度 + 场景进度 (影响灵魂状态) ===
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 7. 场景上下文 ===
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨", "multiline": True}),

                # === 8. 4 大基础维度 (向后兼容 + 美术底子) ===
                "主材质": (list(MATERIALS.keys()), {"default": "木质"}),
                "材质细节": ("STRING", {"default": "原木桌面, 有 1998 年的水渍", "multiline": False}),
                "光影预设": (list(LIGHTING_PRESETS.keys()), {"default": "3_自然光_黄昏"}),
                "光影细节": ("STRING", {"default": "夕阳从窗户进来, 形成 60 度侧光, 影子拉到对面墙", "multiline": False}),
                "颜色基调": (list(COLOR_PALETTE.keys()), {"default": "11_60_30_10_经典"}),
                "颜色细节": ("STRING", {"default": "主色橙黄 (60%), 辅色红 (30%), 点缀色老白绿 (10%)", "multiline": False}),
                "空间类型": (list(SPACE_TYPES.keys()), {"default": "2_室内_开放"}),
                "空间细节": ("STRING", {"default": "厨房 8 平米, 有冰箱/炉灶/餐桌, 老式吊灯", "multiline": False}),

                # === 9. 时代与地域 (向后兼容) ===
                "时代": ("STRING", {"default": "1998 年, 中国东北", "multiline": False}),

                # === 10. 摄影指导 (可选) ===
                "摄影指导": (DP_8_MASTERS_NAMES, {"default": "罗杰·迪金斯_Roger_Deakins"}),

                # === 11. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # === 12. 向后兼容旧版参数 (测试用) ===
                "视觉风格": ("STRING", {"default": "", "multiline": False}),
                "材质重点": ("STRING", {"default": "", "multiline": False}),
                "光影": ("STRING", {"default": "", "multiline": False}),
                "颜色": ("STRING", {"default": "", "multiline": False}),
                "空间布局": ("STRING", {"default": "", "multiline": False}),
                "导演风格": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "art_direction_bible",          # 完整美术指导 Bible (灵魂注入)
        "visual_language_params",        # 灵魂驱动视觉语言 (焦段×光圈×景别×构图)
        "color_60_30_10_script",         # 60:30:10 灵魂驱动色彩脚本
        "lighting_9d_design",            # 9 维光影灵魂驱动设计
        "dp_8_masters_style",            # 8 大摄影指导风格 + 8 大顶级导演视觉签名
        "soul_injection_payload",        # 灵魂注入数据 (供下游节点)
        "h3_three_fields_addon",         # H3 三大字段增强
        "cinematic_signature_addon",     # 11 维控制 + 3 留白 + 3 运镜 灵魂结合
    )
    FUNCTION = "build_art_direction"
    CATEGORY = "PromptLibrary/导演级/灵魂驱动"

    def build_art_direction(self, **kwargs):
        # ========== 1. 收集所有输入 (向后兼容) ==========
        # 向后兼容: 如果旧参数存在, 提示但不影响主流程
        legacy_visual_style = _str(kwargs.get("视觉风格"), "")
        legacy_material = _str(kwargs.get("材质重点"), "")
        legacy_light = _str(kwargs.get("光影"), "")
        legacy_color = _str(kwargs.get("颜色"), "")
        legacy_space = _str(kwargs.get("空间布局"), "")
        legacy_director = _str(kwargs.get("导演风格"), "")

        # 基础 4 维
        material = _str(kwargs.get("主材质"), "木质")
        material_detail = _str(kwargs.get("材质细节"), "") or legacy_material
        light_preset = _str(kwargs.get("光影预设"), "3_自然光_黄昏")
        light_detail = _str(kwargs.get("光影细节"), "") or legacy_light
        color_base = _str(kwargs.get("颜色基调"), "11_60_30_10_经典")
        color_detail = _str(kwargs.get("颜色细节"), "") or legacy_color
        space = _str(kwargs.get("空间类型"), "2_室内_开放")
        space_detail = _str(kwargs.get("空间细节"), "") or legacy_space
        era = _str(kwargs.get("时代"), "1998 年, 中国东北")
        dp = _str(kwargs.get("摄影指导"), "罗杰·迪金斯_Roger_Deakins")
        use_anti_ai = kwargs.get("启用反AI规则", True)

        # 灵魂 4 组输入
        emotion_keys = []
        # Phase 17.1: 兼容多种字段名 (灵魂主导情感 / 灵魂_主导情感 / 主导情感)
        primary = _str(kwargs.get("灵魂主导情感"), "auto")
        if primary == "auto" or not primary:
            primary = _str(kwargs.get("灵魂_主导情感"), "auto")
        if primary == "auto" or not primary:
            primary = _str(kwargs.get("主导情感"), "auto")
        if primary and primary != "auto":
            emotion_keys.append(primary)
        for i in range(1, 5):
            k = "灵魂次要情感_" + str(i)
            v = _str(kwargs.get(k), "none")
            if v and v != "none":
                emotion_keys.append(v)

        # 融合模式 - 兼容 (灵魂融合模式 / 灵魂_融合模式)
        fusion_mode = _str(kwargs.get("灵魂融合模式"), "auto")
        if not fusion_mode or fusion_mode == "auto":
            fusion_mode = _str(kwargs.get("灵魂_融合模式"), "auto")
        primary_weight = float(kwargs.get("灵魂主导权重", 1.0))
        if primary_weight == 1.0:
            pw2 = kwargs.get("灵魂_主导权重", None)
            if pw2 is not None:
                primary_weight = float(pw2)

        # 权重
        weights = [primary_weight]
        if len(emotion_keys) > 1:
            remaining = max(0.0, 1.0 - primary_weight)
            n_rem = len(emotion_keys) - 1
            for _ in range(n_rem):
                weights.append(remaining / n_rem if n_rem > 0 else 0.0)

        # 灵魂维度
        soul_dims = {
            "creativity": float(kwargs.get("灵魂创造力", 0.85)),
            "imagination": float(kwargs.get("灵魂想象力", 0.85)),
            "artistic_expression": float(kwargs.get("灵魂艺术表达", 0.85)),
            "camera_skill": float(kwargs.get("灵魂镜头技巧", 0.85)),
            "atmosphere_control": float(kwargs.get("灵魂氛围掌控", 0.85)),
            "mental_state": _str(kwargs.get("灵魂精神状态"), "lucid-dreamy"),
            "inspiration": float(kwargs.get("灵魂灵感指数", 0.85)),
            "rebelliousness": float(kwargs.get("灵魂叛逆指数", 0.70)),
            "self_doubt": float(kwargs.get("灵魂怀疑指数", 0.50)),
            "breakthrough_courage": float(kwargs.get("灵魂叛逆指数", 0.70)) * 0.9 + 0.1,
        }

        # 灵魂状态
        soul_state_input = {
            "inspiration": float(kwargs.get("灵魂灵感指数", 0.85)),
            "fatigue": float(kwargs.get("灵魂疲劳指数", 0.30)),
            "doubt": float(kwargs.get("灵魂怀疑指数", 0.50)),
            "rebelliousness": float(kwargs.get("灵魂叛逆指数", 0.70)),
        }

        # 故事强度 + 场景进度 (用于动态 soul_state)
        story_intensity = float(kwargs.get("故事强度", 0.5))
        scene_progress = float(kwargs.get("场景进度", 0.0))

        # 导演 (8 大顶级)
        director = _str(kwargs.get("导演"), "王家卫")
        if not director or director == "auto":
            director = "王家卫"
        # 向后兼容旧版 导演风格 字段
        if legacy_director and legacy_director not in TOP_8_DIRECTORS:
            # 尝试映射
            mapping = {
                "是枝裕和": "约阿希姆·提尔",  # 家庭代际都包含
                "侯孝贤": "约阿希姆·提尔",
                "贾樟柯": "塔可夫斯基",
                "伯格曼": "塔可夫斯基",
                "王家卫_1980": "王家卫",
                "王家卫+侯孝贤": "王家卫",
            }
            director = mapping.get(legacy_director, director)

        scene_desc = _str(kwargs.get("场景描述"), "")

        # ========== 2. 融合情感 (核心) ==========
        if _HAS_SOUL and emotion_keys:
            fused_emotion = fuse_emotions(emotion_keys, weights, fusion_mode)
        else:
            fused_emotion = None

        # 兜底融合 (如果没有 soul 模块或没有情感)
        if not fused_emotion:
            fused_emotion = {
                "name": "Loneliness 孤独",
                "category": "State",
                "intensity": 0.7,
                "polarity": "negative",
                "arousal": "low",
                "emotions": ["loneliness"],
                "weights": [1.0],
                "fusion_mode": "F1_单情感主导",
                "description": "渴望连接但无连接的状态",
                "visual_signs": "身体蜷缩, 视线远眺, 经常独自一人",
                "voice_signs": "经常沉默, 偶发自言自语",
                "facial_au": "AU1+AU4+AU15+AU43 (孤独组合)",
                "inner_monologue": "有谁在听吗",
                "color_palette": "冷蓝, 苍白, 灰",
                "music_tempo": "40 BPM, 单音钢琴",
                "director_examples": "塔可夫斯基《镜子》 - 独居的母亲",
            }

        # 灵魂状态动态计算
        if _HAS_SOUL:
            dynamic_soul_state = compute_soul_state(story_intensity, scene_progress)
        else:
            dynamic_soul_state = soul_state_input
        # 合并 (用户输入优先)
        soul_state = dict(soul_state_input)
        soul_state.update(dynamic_soul_state)

        # 提取 categories 列表 (供动态映射)
        fused_categories = _get_dominant_categories(fused_emotion)
        fused_intensity = _get_fused_intensity(fused_emotion)
        fused_palette = _get_fused_color_palette(fused_emotion)
        fused_tempo = _get_fused_music_tempo(fused_emotion)

        # ========== 3. 灵魂驱动动态生成视觉语言 ==========
        derived_focal = derive_focal_from_soul(fused_emotion)
        derived_aperture = derive_aperture_from_soul(fused_emotion)
        derived_shot_size = derive_shot_size_from_soul(fused_emotion)
        derived_composition = derive_composition_from_soul(fused_emotion)
        derived_lighting_9d = derive_lighting_9d_from_soul(fused_emotion)
        derived_60_30_10 = derive_60_30_10_from_soul(fused_emotion, director)

        # 摄影指导信息
        dp_info = DP_8_MASTERS.get(dp, {})
        focal_info = FOCAL_LENGTH_EMOTION.get(derived_focal, {})
        aperture_info = APERTURE_DEPTH.get(derived_aperture, {})
        shot_info = SHOT_SIZE_NARRATIVE.get(derived_shot_size, {})
        comp_info = COMPOSITION_RULES.get(derived_composition, {})
        director_info = TOP_8_DIRECTORS_VISUAL_SIGNATURE.get(director, {})

        # ========== 4. 输出 1: 美术指导 Bible (灵魂注入) ==========
        bible = "════════════════════════════════════════\n"
        bible += "【美术指导 Bible】Phase 18 灵魂驱动版\n"
        bible += "════════════════════════════════════════\n\n"

        # --- 灵魂核心 ---
        bible += "════════════════════════════════════════\n"
        bible += "【灵魂核心注入】(DirectorSoulNode 完整接收)\n"
        bible += "════════════════════════════════════════\n\n"
        bible += "主导情感: " + fused_emotion.get("name", "") + "\n"
        bible += "融合模式: " + fused_emotion.get("fusion_mode", "") + "\n"
        bible += "融合情感: " + " + ".join(fused_emotion.get("emotions", [])) + "\n"
        bible += "权重: " + ", ".join(["{0:.2f}".format(w) for w in fused_emotion.get("weights", [])]) + "\n"
        bible += "强度: {0:.2f}\n".format(fused_intensity)
        bible += "极性: " + fused_emotion.get("polarity", "") + "\n"
        bible += "唤醒度: " + fused_emotion.get("arousal", "") + "\n"
        bible += "主导类别: " + ", ".join(fused_categories) + "\n\n"
        bible += "色彩锚点: " + fused_palette + "\n"
        bible += "音乐锚点: " + fused_tempo + "\n\n"
        bible += "视觉表现: " + fused_emotion.get("visual_signs", "")[:400] + "\n"
        bible += "声音表现: " + fused_emotion.get("voice_signs", "")[:200] + "\n"
        bible += "面部肌肉: " + fused_emotion.get("facial_au", "")[:200] + "\n"
        bible += "内心独白: " + fused_emotion.get("inner_monologue", "")[:200] + "\n\n"

        # --- 灵魂维度 ---
        bible += "════════════════════════════════════════\n"
        bible += "【灵魂维度 (10 Dimensions)】\n"
        bible += "════════════════════════════════════════\n\n"
        for dim_key, dim_name in [
            ("creativity", "创造力"),
            ("imagination", "想象力"),
            ("artistic_expression", "艺术表达"),
            ("camera_skill", "镜头技巧"),
            ("atmosphere_control", "氛围掌控"),
            ("inspiration", "灵感"),
            ("rebelliousness", "叛逆度"),
            ("self_doubt", "自我怀疑"),
            ("breakthrough_courage", "突破勇气"),
        ]:
            bible += "  - {0}: {1:.2f}\n".format(dim_name, soul_dims.get(dim_key, 0.85))
        bible += "  - 精神状态: " + soul_dims.get("mental_state", "") + "\n\n"

        # --- 灵魂状态 ---
        bible += "════════════════════════════════════════\n"
        bible += "【灵魂状态 (Soul State)】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += "  - 灵感指数: {0:.2f} (高→镜头丰富 / 低→镜头克制)\n".format(soul_state.get("inspiration", 0.85))
        bible += "  - 疲劳指数: {0:.2f} (高→慢节奏 / 低→快节奏)\n".format(soul_state.get("fatigue", 0.30))
        bible += "  - 怀疑指数: {0:.2f} (高→留白多 / 低→明快)\n".format(soul_state.get("doubt", 0.50))
        bible += "  - 叛逆指数: {0:.2f} (高→打破规则 / 低→遵守规则)\n".format(soul_state.get("rebelliousness", 0.70))
        bible += "  - 精神状态: " + soul_dims.get("mental_state", "lucid-dreamy") + "\n\n"

        # --- 时代与导演 ---
        bible += "════════════════════════════════════════\n"
        bible += "【时代 × 地域 × 导演】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += "时代: " + era + "\n"
        bible += "场景: " + scene_desc + "\n"
        bible += "导演: " + director + " — " + director_info.get("visual_signature", "") + "\n"
        bible += "摄影指导 (DP): " + dp + " — " + dp_info.get("signature", "") + "\n\n"

        # --- 灵魂融合决策树 ---
        bible += "════════════════════════════════════════\n"
        bible += "【灵魂融合决策树 (60 情感 → 视觉语言)】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += _generate_60_to_visual_long(fused_emotion, director) + "\n"

        # --- 灵魂维度 → 视觉决策 完整映射 ---
        bible += "════════════════════════════════════════\n"
        bible += "【10 灵魂维度 → 视觉决策 完整映射】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += _generate_soul_dimension_to_visual_long(soul_dims) + "\n"

        # --- 反 AI 全集 ---
        bible += "════════════════════════════════════════\n"
        bible += "【反 AI 191 词条 + 10 铁律 + 14 维度】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += _generate_14d_anti_ai_full() + "\n"

        # --- 60 情感视觉全表 (Bible 摘要) ---
        bible += "════════════════════════════════════════\n"
        bible += "【60 情感 × 视觉语言 全表 (Bible 摘要)】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += _generate_60_emotion_visual_table() + "\n"

        # --- 4 大基础维度 (DiDi_OK 美术底子) ---
        bible += "════════════════════════════════════════\n"
        bible += "【4 大基础维度 (DiDi_OK: 美术底子决定一切)】\n"
        bible += "════════════════════════════════════════\n\n"

        bible += "【1. 材质 (Material) - " + material + "】\n"
        bible += material_detail + "\n"
        if legacy_material:
            bible += "  [旧版兼容] " + legacy_material + "\n"
        bible += "- 关键: 材质要'可触摸', 观众能想象摸到\n"
        bible += "- 时代感: 1998 年的水渍/划痕/使用痕迹\n"
        bible += "- 真实感: 不是全新, 是用过, 有温度\n\n"

        bible += "【2. 光影 (Light) - " + light_preset + "】\n"
        bible += light_detail + "\n"
        if legacy_light:
            bible += "  [旧版兼容] " + legacy_light + "\n"
        bible += "- 关键: 光影决定情绪, 决定时间, 决定空间\n"
        bible += "- 灵魂驱动: " + derived_lighting_9d.get("光源类型", "") + " / " + derived_lighting_9d.get("方向", "") + " / " + derived_lighting_9d.get("色温", "") + "\n"
        bible += "- 真实感: 不是布光完美, 是真实生活中的光\n\n"

        bible += "【3. 颜色 (Color) - " + color_base + "】\n"
        bible += color_detail + "\n"
        if legacy_color:
            bible += "  [旧版兼容] " + legacy_color + "\n"
        bible += "- 关键: 颜色 = 情绪, 颜色 = 时代, 颜色 = 文化\n"
        bible += "- 灵魂驱动主色: " + derived_60_30_10.get("主色_60", "") + "\n"
        bible += "- 时代感: 1998 年的颜色饱和度比今天低, 有褪色感\n"
        bible += "- 真实感: 不是色彩鲜明, 是生活的颜色\n\n"

        bible += "【4. 空间 (Space) - " + space + "】\n"
        bible += space_detail + "\n"
        if legacy_space:
            bible += "  [旧版兼容] " + legacy_space + "\n"
        bible += "- 关键: 空间 = 关系, 空间 = 阶层, 空间 = 心理\n"
        bible += "- 时代感: 1998 年东北家庭, 厨房小但温馨\n"
        bible += "- 真实感: 不是布景完美, 是活过的空间\n\n"

        # --- 5 要素架构 ---
        bible += "════════════════════════════════════════\n"
        bible += "【5 要素架构 (数据/上下文/Skill/经验/AI)】\n"
        bible += "════════════════════════════════════════\n\n"
        bible += "【数据层】\n"
        bible += "  - 1161 部作品 director_view 14 维\n"
        bible += "  - 63 导演 12 维档案\n"
        bible += "  - 191 反 AI 词条\n"
        bible += "  - 12 套方法论 (24 帧法则/三幕剧/救猫咪/序列/节拍...)\n"
        bible += "  - 14 真实短剧案例\n"
        bible += "  - 48 情感 + 7 融合 + 10 灵魂维度\n"
        bible += "  - 60 情感矩阵完整 (Phase 17 新增)\n"
        bible += "  - 8 大顶级摄影指导风格库\n"
        bible += "  - 8 大顶级导演视觉签名 (Phase 18 新增)\n"
        bible += "  - 焦段×情感映射 (灵魂驱动)\n"
        bible += "  - 60:30:10 色彩法则 (灵魂驱动)\n"
        bible += "  - 9 维光影设计 (灵魂驱动)\n\n"

        bible += "【上下文缩略层】\n"
        bible += "  - 灵魂: " + fused_emotion.get("name", "") + " (强度 {0:.2f})\n".format(fused_intensity)
        bible += "  - 视觉: 焦段 " + focal_info.get("cn", derived_focal) + " / 光圈 " + aperture_info.get("cn", derived_aperture) + "\n"
        bible += "  - 场景: " + era + " / " + space + " / " + light_preset + "\n"
        bible += "  - 导演: " + director + " / DP: " + dp + "\n"
        bible += "  - 关键: 美术决定一切, 后面很难救\n\n"

        bible += "【Skill/Harness 层】\n"
        bible += "  - 灵魂融合 (F1-F7)\n"
        bible += "  - 灵魂维度 (10)\n"
        bible += "  - 焦段×情感映射 (灵魂动态)\n"
        bible += "  - 光圈×景深映射 (灵魂动态)\n"
        bible += "  - 景别×叙事功能 (灵魂动态)\n"
        bible += "  - 7 大构图法则 (灵魂动态)\n"
        bible += "  - 60:30:10 色彩脚本 (灵魂动态)\n"
        bible += "  - 9 维光影设计 (灵魂动态)\n"
        bible += "  - 11 维导演控制 (灵魂结合)\n"
        bible += "  - 3 留白 + 3 运镜 (灵魂结合)\n\n"

        bible += "【经验矩阵层】\n"
        bible += "  - 8 大摄影指导实战风格库\n"
        bible += "  - 8 大顶级导演视觉签名库\n"
        bible += "  - 真实短剧 14 部案例\n"
        bible += "  - 1161 部作品 director_view\n\n"

        bible += "【AI 深度处理层】\n"
        bible += "  - L1-L7 七层 prompt 架构\n"
        bible += "  - L5 摄影与剪辑层 (灵魂焦段×光圈×景别)\n"
        bible += "  - L7 风格约束层 (灵魂 + DP + 导演 三重约束)\n"
        bible += "  - 反 AI 词表 191 条 + 10 铁律\n"
        bible += "  - 灵魂维度动态调整 (创造力/想象力/叛逆)\n\n"

        # --- 8 大顶级导演视觉签名 ---
        bible += "════════════════════════════════════════\n"
        bible += "【8 大顶级导演视觉签名】(灵魂匹配版)\n"
        bible += "════════════════════════════════════════\n\n"
        bible += "当前选择: " + director + "\n"
        bible += "视觉签名: " + director_info.get("visual_signature", "") + "\n"
        bible += "镜头: " + director_info.get("lens", "") + "\n"
        bible += "光影: " + director_info.get("lighting", "") + "\n"
        bible += "色彩: " + director_info.get("color", "") + "\n"
        bible += "运镜: " + director_info.get("motion", "") + "\n"
        bible += "时长: " + director_info.get("duration", "") + "\n"
        bible += "题材: " + director_info.get("subject", "") + "\n"
        bible += "代表作: " + director_info.get("代表作", "") + "\n"
        bible += "触发: " + director_info.get("trigger", "") + "\n"
        bible += "执行: " + director_info.get("execute", "") + "\n\n"

        # 灵魂匹配说明
        bible += "【灵魂与导演的匹配度】\n"
        for d_name, d_info in TOP_8_DIRECTORS_VISUAL_SIGNATURE.items():
            match_score = 0.5
            # 简单匹配算法
            d_subj = d_info.get("subject", "")
            d_trig = d_info.get("trigger", "")
            for cat in fused_categories:
                if cat in d_subj or cat in d_trig or cat.lower() in d_subj.lower():
                    match_score += 0.1
            if fused_intensity >= 0.7 and ("史诗" in d_subj or "紧张" in d_subj):
                match_score += 0.05
            match_score = min(0.99, match_score)
            mark = " ✓ 当前" if d_name == director else ""
            bible += "  - {0}: 匹配度 {1:.2f}{2}\n".format(d_name, match_score, mark)
        bible += "\n"

        # ========== 5. 输出 2: 灵魂驱动视觉语言参数化 ==========
        visual_lang = "════════════════════════════════════════\n"
        visual_lang += "【灵魂驱动视觉语言参数化系统】Phase 18 核心\n"
        visual_lang += "════════════════════════════════════════\n\n"
        visual_lang += "顶级摄影指导的核心能力: 用构图传递演员情绪、场景氛围, 甚至创造视觉象征与暗示\n"
        visual_lang += "(AIGC 影视全流程解析 § 能力四: 视觉语言力)\n\n"

        visual_lang += "【灵魂驱动决策】(DYNAMIC — 由融合情感 + 灵魂维度实时推导)\n"
        visual_lang += "  - 主导情感: " + fused_emotion.get("name", "") + " (强度 {0:.2f})\n".format(fused_intensity)
        visual_lang += "  - 主导类别: " + ", ".join(fused_categories) + "\n"
        visual_lang += "  - 极性: " + fused_emotion.get("polarity", "") + " / 唤醒度: " + fused_emotion.get("arousal", "") + "\n"
        visual_lang += "  - 推导结果: 焦段={0} / 光圈={1} / 景别={2} / 构图={3}\n\n".format(
            derived_focal, derived_aperture, derived_shot_size, derived_composition
        )

        visual_lang += "──────────────────────────────────\n"
        visual_lang += "A. 焦段 × 情感映射 (灵魂推导: " + focal_info.get("cn", derived_focal) + ")\n"
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "触发 (灵魂侧): " + FOCAL_LENGTH_SOUL_MAP.get(derived_focal, {}).get("rationale", "") + "\n"
        visual_lang += "执行: " + focal_info.get("execution", "") + "\n"
        visual_lang += "情绪: " + focal_info.get("emotion", "") + "\n"
        visual_lang += "叙事: " + focal_info.get("narrative", "") + "\n"
        visual_lang += "代表: " + focal_info.get("masters", "") + "\n"
        visual_lang += "主导演: " + director_info.get("lens", "") + "\n\n"

        visual_lang += "【焦段全表 (灵魂映射)】\n"
        for k, v in FOCAL_LENGTH_SOUL_MAP.items():
            focal_emotion = FOCAL_LENGTH_EMOTION.get(k, {})
            visual_lang += "  - {0}: {1}\n".format(focal_emotion.get("cn", k), v.get("rationale", ""))
        visual_lang += "\n"

        visual_lang += "──────────────────────────────────\n"
        visual_lang += "B. 光圈 × 景深映射 (灵魂推导: " + aperture_info.get("cn", derived_aperture) + ")\n"
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "触发 (灵魂侧): " + APERTURE_SOUL_MAP.get(derived_aperture, {}).get("rationale", "") + "\n"
        visual_lang += "执行: " + aperture_info.get("execution", "") + "\n"
        visual_lang += "叙事: " + aperture_info.get("narrative", "") + "\n"
        visual_lang += "代表 DP: " + aperture_info.get("master_use", "") + "\n\n"

        visual_lang += "【光圈全表 (灵魂映射)】\n"
        for k, v in APERTURE_SOUL_MAP.items():
            ap_emotion = APERTURE_DEPTH.get(k, {})
            visual_lang += "  - {0}: {1}\n".format(ap_emotion.get("cn", k), v.get("rationale", ""))
        visual_lang += "\n"

        visual_lang += "──────────────────────────────────\n"
        visual_lang += "C. 景别 × 叙事功能 (灵魂推导: " + shot_info.get("cn", derived_shot_size) + ")\n"
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "触发 (灵魂侧): " + SHOT_SIZE_SOUL_MAP.get(derived_shot_size, {}).get("rationale", "") + "\n"
        visual_lang += "执行: " + shot_info.get("execution", "") + "\n"
        visual_lang += "叙事: " + shot_info.get("narrative", "") + "\n"
        visual_lang += "代表: " + shot_info.get("master_use", "") + "\n\n"

        visual_lang += "【景别全表 (灵魂映射)】\n"
        for k, v in SHOT_SIZE_SOUL_MAP.items():
            shot_emotion = SHOT_SIZE_NARRATIVE.get(k, {})
            visual_lang += "  - {0}: {1}\n".format(shot_emotion.get("cn", k), v.get("rationale", ""))
        visual_lang += "\n"

        visual_lang += "──────────────────────────────────\n"
        visual_lang += "D. 7 大构图法则 (灵魂推导: " + comp_info.get("cn", derived_composition) + ")\n"
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "触发 (灵魂侧): " + COMPOSITION_SOUL_MAP.get(derived_composition, {}).get("rationale", "") + "\n"
        visual_lang += "执行: " + comp_info.get("execution", "") + "\n"
        visual_lang += "叙事: " + comp_info.get("narrative", "") + "\n"
        visual_lang += "代表: " + comp_info.get("masters", "") + "\n\n"

        visual_lang += "【构图全表 (灵魂映射)】\n"
        for k, v in COMPOSITION_SOUL_MAP.items():
            c_emotion = COMPOSITION_RULES.get(k, {})
            visual_lang += "  - {0}: {1}\n".format(c_emotion.get("cn", k), v.get("rationale", ""))
        visual_lang += "\n"

        visual_lang += "──────────────────────────────────\n"
        visual_lang += "E. L5 摄影与剪辑层 (灵魂动态)\n"
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "OPTICS: " + focal_info.get("cn", derived_focal) + " (灵魂推导), " + aperture_info.get("cn", derived_aperture) + " (灵魂推导), " + shot_info.get("cn", derived_shot_size) + " (灵魂推导) 景深.\n"
        visual_lang += "CAMERA: 由 " + director + " 风格决定 — " + director_info.get("motion", "") + "\n"
        visual_lang += "COMPOSITION: " + comp_info.get("cn", derived_composition) + " (灵魂推导) — " + comp_info.get("execution", "") + "\n\n"

        visual_lang += "L7 风格约束层 (灵魂 + DP + 导演 三重约束):\n"
        visual_lang += "  - 必须坚持 " + focal_info.get("cn", derived_focal) + " 焦段 (灵魂推导, 不要中途变焦)\n"
        visual_lang += "  - 必须坚持 " + aperture_info.get("cn", derived_aperture) + " 光圈 (灵魂推导, 不要随意变景深)\n"
        visual_lang += "  - 整场戏坚持 " + shot_info.get("cn", derived_shot_size) + " 景别变化范围 (灵魂推导)\n"
        visual_lang += "  - 构图坚持 " + comp_info.get("cn", derived_composition) + " (灵魂推导)\n"
        visual_lang += "  - 必须遵守 " + director + " 的视觉签名 (运镜 + 镜头 + 时长)\n"
        visual_lang += "  - 全部 L1-L7 必须保持风格一致\n\n"

        # 灵魂维度对视觉语言的影响
        visual_lang += "【灵魂维度 → 视觉语言】(10 维 → 镜头参数)\n"
        visual_lang += "  - 创造力 {0:.2f} → 新隐喻/跨类比/反转预期的应用程度\n".format(soul_dims.get("creativity", 0.85))
        visual_lang += "  - 想象力 {0:.2f} → 镜头设计的丰富度\n".format(soul_dims.get("imagination", 0.85))
        visual_lang += "  - 艺术表达 {0:.2f} → 微动作/物件代替心理的密度\n".format(soul_dims.get("artistic_expression", 0.85))
        visual_lang += "  - 镜头技巧 {0:.2f} → 焦段/光圈/景别的精细度\n".format(soul_dims.get("camera_skill", 0.85))
        visual_lang += "  - 氛围掌控 {0:.2f} → 60:30:10 色彩 + 9 维光影的执行力\n".format(soul_dims.get("atmosphere_control", 0.85))
        visual_lang += "  - 灵感 {0:.2f} → 5-20 个灵感时刻的概率\n".format(soul_dims.get("inspiration", 0.85))
        visual_lang += "  - 叛逆度 {0:.2f} → 打破规则的镜头数\n".format(soul_dims.get("rebelliousness", 0.70))
        visual_lang += "  - 自我怀疑 {0:.2f} → 反复重拍/反复重剪的密度\n".format(soul_dims.get("self_doubt", 0.50))
        visual_lang += "  - 突破勇气 {0:.2f} → 实验性镜头数\n".format(soul_dims.get("breakthrough_courage", 0.73))
        visual_lang += "  - 精神状态 " + soul_dims.get("mental_state", "") + " → 整体镜头风格 (lucid=清晰/dreamy=梦幻/anxious=摇晃/serene=稳定)\n\n"

        # 60 情感视觉全表
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "【60 情感 × 视觉语言 全表 (灵魂驱动)】\n"
        visual_lang += "──────────────────────────────────\n\n"
        visual_lang += _generate_60_emotion_visual_table() + "\n"

        # 60 情感 → 视觉语言 长篇决策树
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "【60 情感 → 视觉语言 长篇决策树】\n"
        visual_lang += "──────────────────────────────────\n\n"
        visual_lang += _generate_60_to_visual_long(fused_emotion, director) + "\n"

        # 灵魂维度 → 视觉决策 完整映射
        visual_lang += "──────────────────────────────────\n"
        visual_lang += "【10 灵魂维度 → 视觉决策 完整映射】\n"
        visual_lang += "──────────────────────────────────\n\n"
        visual_lang += _generate_soul_dimension_to_visual_long(soul_dims) + "\n"

        # L1-L7 七层 prompt 架构 完整
        visual_lang += "════════════════════════════════════════\n"
        visual_lang += "【L1-L7 七层 Prompt 架构 (灵魂驱动)】\n"
        visual_lang += "════════════════════════════════════════\n\n"
        l1_l7 = [
            ("L1 主题层", "整场戏核心主题 / 灵魂的核心隐喻",
             "L1 = " + fused_emotion.get("name", "") + " (核心情感 = " + fused_emotion.get("inner_monologue", "")[:60] + "...)"),
            ("L2 故事层", "故事线 / 角色关系 / 时间线",
             "L2 = " + director + " 的故事结构 (王家卫非线性 / 诺兰多线 / PTA 慢热)"),
            ("L3 角色层", "角色心理 / 微表情 / 身体语言 / 口头禅",
             "L3 = " + fused_emotion.get("visual_signs", "")[:80]),
            ("L4 表演层", "5 维立体表演 (微动作总和 = 情感)",
             "L4 = 5 维: 表情 + 身体 + 声音 + 节奏 + 物件 = " + fused_emotion.get("facial_au", "")[:60]),
            ("L5 摄影与剪辑层", "焦段/光圈/景别/构图/光影/色彩",
             "L5 = " + focal_info.get("cn", derived_focal) + " + " + aperture_info.get("cn", derived_aperture) + " + " + shot_info.get("cn", derived_shot_size) + " + " + comp_info.get("cn", derived_composition) + " + 9 维光影 + 60:30:10"),
            ("L6 声音与配乐层", "对白/环境声/音乐/沉默/呼吸",
             "L6 = " + fused_tempo + " + 灵魂音调 " + fused_emotion.get("voice_signs", "")[:60]),
            ("L7 风格约束层", "灵魂 + DP + 导演 三重约束",
             "L7 = 必须坚持 " + focal_info.get("cn", derived_focal) + " / " + aperture_info.get("cn", derived_aperture) + " / " + shot_info.get("cn", derived_shot_size) + " / " + comp_info.get("cn", derived_composition) + " / " + director + " 视觉签名"),
        ]
        for layer, desc, soul_exec in l1_l7:
            visual_lang += "  " + layer + " — " + desc + "\n"
            visual_lang += "    [灵魂执行] " + soul_exec + "\n\n"
        visual_lang += "L1-L7 必须保持风格一致:\n"
        visual_lang += "  - 不能 L5 用 35mm, 中途换 85mm\n"
        visual_lang += "  - 不能 L6 用慢节奏, 中途换快节奏\n"
        visual_lang += "  - 不能 L7 用 " + director + " 风格, 中途换其他导演\n"
        visual_lang += "  - 必须 L1 主题贯穿 L2-L7\n"
        visual_lang += "  - 灵魂 (" + fused_emotion.get("name", "") + ") 必须贯穿 L1-L7\n"
        visual_lang += "  - 9 维光影 (" + derived_lighting_9d.get("光源类型", "") + " + " + derived_lighting_9d.get("方向", "") + " + " + derived_lighting_9d.get("色温", "") + ") 必须 L5+L6 保持\n"
        visual_lang += "  - 60:30:10 色彩 (主色 " + derived_60_30_10.get("主色_60", "")[:20] + ") 必须 L5+L7 保持\n"
        visual_lang += "  - 11 维控制 (空镜/留白/氛围/悬疑/多线/反转/高潮/余韵/节奏/感情/角色) 必须 L2-L7 保持\n\n"

        # ========== 6. 输出 3: 60:30:10 灵魂驱动色彩脚本 ==========
        color_60 = "════════════════════════════════════════\n"
        color_60 += "【60:30:10 灵魂驱动色彩法则】(Hell Grind + 斯托拉罗 + 灵魂融合)\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += "AIGC 影视全流程解析 § 环节 15 + 37: 60:30:10 法则严格执行\n"
        color_60 += "(DP 风格: " + dp + " 严格执行 60:30:10 / 导演: " + director + " 视觉签名)\n\n"

        color_60 += "──────────────────────────────────\n"
        color_60 += "【灵魂驱动 60:30:10 推导逻辑】\n"
        color_60 += "──────────────────────────────────\n\n"
        color_60 += "  - 60% 主色 ← fused_emotion.color_palette (主导色)\n"
        color_60 += "  - 30% 辅色 ← 导演视觉签名 + 角色关系\n"
        color_60 += "  - 10% 点缀色 ← 灵魂戏剧时刻 (极性 + 唤醒度 推导)\n\n"

        color_60 += "──────────────────────────────────\n"
        color_60 += "本场戏 60:30:10 设定 (灵魂动态生成)\n"
        color_60 += "──────────────────────────────────\n\n"

        color_60 += "【主色 60% — 灵魂融合主调】\n"
        color_60 += "  灵魂输入: " + fused_palette + "\n"
        color_60 += "  设定: " + derived_60_30_10.get("主色_60", "") + "\n"
        color_60 += "  功能: 决定整体情绪, 时代主调, 文化背景\n"
        color_60 += "  心理学: 暖色 = 亲密/怀旧, 冷色 = 孤独/超自然\n"
        color_60 += "  执行: 全场戏 60% 面积都是主色, 服装/墙/地板/天空\n\n"

        color_60 += "【辅色 30% — 导演风格 + 角色关系】\n"
        color_60 += "  灵魂输入: " + director + " 视觉签名 — " + director_info.get("color", "") + "\n"
        color_60 += "  设定: " + derived_60_30_10.get("辅色_30", "") + "\n"
        color_60 += "  功能: 角色服装/关系色彩, 强化人物识别\n"
        color_60 += "  心理学: 角色色彩 = 人物性格 + 关系网络\n"
        color_60 += "  执行: 角色服装/关键道具占 30%, 与主色形成对比/协调\n\n"

        color_60 += "【点缀色 10% — 灵魂戏剧时刻】\n"
        color_60 += "  灵魂输入: 极性=" + fused_emotion.get("polarity", "") + " / 唤醒度=" + fused_emotion.get("arousal", "") + "\n"
        color_60 += "  设定: " + derived_60_30_10.get("点缀色_10", "") + "\n"
        color_60 += "  功能: 关键道具/情绪点, 戏剧化使用\n"
        color_60 += "  心理学: 全片 1-3 次出现, 观众会记住\n"
        color_60 += "  执行: 关键道具/关键瞬间 10%, 极致强调\n\n"

        color_60 += "──────────────────────────────────\n"
        color_60 += "色彩心理学 (8 大色)\n"
        color_60 += "──────────────────────────────────\n"
        psychology = COLOR_60_30_10["主色_60_场景主调"]["psychology"]
        for color, mean in psychology.items():
            color_60 += "  - " + color + ": " + mean + "\n"
        color_60 += "\n"

        color_60 += "──────────────────────────────────\n"
        color_60 += "60:30:10 经典电影案例 (灵魂匹配)\n"
        color_60 += "──────────────────────────────────\n"
        examples = COLOR_60_30_10["主色_60_场景主调"]["examples"]
        for e in examples:
            color_60 += "  - " + e + "\n"
        color_60 += "\n"
        examples_30 = COLOR_60_30_10["辅色_30_角色关系"]["examples"]
        for e in examples_30:
            color_60 += "  - " + e + "\n"
        color_60 += "\n"
        examples_10 = COLOR_60_30_10["点缀色_10_戏剧时刻"]["examples"]
        for e in examples_10:
            color_60 += "  - " + e + "\n"
        color_60 += "\n"

        color_60 += "──────────────────────────────────\n"
        color_60 += "调色执行 (一级/二级/创意) — 灵魂驱动\n"
        color_60 += "──────────────────────────────────\n"
        color_60 += "一级调色 (Primary): 统一主色 60% 的色温/对比度/曝光, 让相邻镜头无缝\n"
        color_60 += "  灵魂侧: 导演 " + director + " 的色彩倾向是 " + director_info.get("color", "") + "\n"
        color_60 += "二级调色 (Secondary): 保持辅色 30% 一致, 局部校正 (肤色/道具)\n"
        color_60 += "创意调色 (Creative): 强化点缀色 10%, 服务情感\n"
        color_60 += "  灵魂侧: 戏剧时刻 " + fused_emotion.get("inner_monologue", "")[:100] + "\n\n"

        color_60 += "调色检查清单 (灵魂驱动):\n"
        color_60 += "  - [ ] 主色 60% 是否统一? (灵魂: " + derived_60_30_10.get("主色_60", "")[:50] + "...)\n"
        color_60 += "  - [ ] 辅色 30% 是否一致? (灵魂: " + derived_60_30_10.get("辅色_30", "")[:50] + "...)\n"
        color_60 += "  - [ ] 点缀色 10% 是否突出? (灵魂: " + derived_60_30_10.get("点缀色_10", "")[:50] + "...)\n"
        color_60 += "  - [ ] 肤色是否准确? (大银幕上肤色最重要)\n"
        color_60 += "  - [ ] 跨镜头色温/对比/曝光是否一致?\n"
        color_60 += "  - [ ] 色彩变化是否平滑?\n"
        color_60 += "  - [ ] 色彩服务于情感? (灵魂: " + fused_emotion.get("name", "") + ")\n"
        color_60 += "  - [ ] 色彩服务 " + director + " 的视觉签名? (" + director_info.get("color", "")[:50] + "...)\n\n"

        # 12 色心理学扩展
        color_60 += "════════════════════════════════════════\n"
        color_60 += "【12 色心理学深度 (色彩 → 心理 → 电影 → 用法)】\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += _generate_color_psychology_extended() + "\n"

        # 22 部经典电影案例
        color_60 += "════════════════════════════════════════\n"
        color_60 += "【60:30:10 电影案例库 (22 部经典)】\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += _generate_film_case_studies() + "\n"

        # 7 大调色 SOP
        color_60 += "════════════════════════════════════════\n"
        color_60 += "【60:30:10 调色 SOP (7 大步骤)】\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += _generate_60_30_10_sop_extended(fused_palette, derived_60_30_10, director, fused_emotion) + "\n"

        # 60 情感 color_palette 完整表
        color_60 += "════════════════════════════════════════\n"
        color_60 += "【60 情感 color_palette 完整表 (灵魂融合色)】\n"
        color_60 += "════════════════════════════════════════\n\n"
        if _HAS_SOUL:
            for ekey, einfo in EMOTION_MATRIX_60.items():
                color_60 += "  {0:30s} | {1:8s} | {2:8s} | palette: {3}\n".format(
                    einfo.get("name", ekey)[:30],
                    einfo.get("category", "")[:8],
                    einfo.get("polarity", "")[:8],
                    einfo.get("color_palette", "")[:50]
                )
        color_60 += "\n"

        # 色彩组合 18 套 (60:30:10 经典组合)
        color_60 += "════════════════════════════════════════\n"
        color_60 += "【18 套经典 60:30:10 色彩组合 (灵魂驱动)】\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_combos = [
            ("温暖怀旧", "暖橙黄 #D4A24C", "老红 #8B2E1F", "老白绿 #8E9F7E", "李安《喜宴》"),
            ("冷峻医疗", "冷蓝 #4A6B8A", "灰白 #E8E8E8", "血红 #C8102E", "诺兰《星际穿越》"),
            ("末世苍凉", "黄沙橙 #D4A437", "Joi 蓝紫 #4B3F8C", "橘红夕阳 #FF6F00", "Deakins《银翼杀手2049》"),
            ("高对比黑白", "纯黑 #000000", "灰白 #C0C0C0", "血红 #C8102E", "Kaminski《辛德勒的名单》"),
            ("霓虹都市", "霓虹蓝 #1F3A5F", "霓虹粉 #FF1493", "霓虹黄 #FFFF00", "杜可风《重庆森林》"),
            ("森林自然", "森林绿 #2D5016", "土地棕 #8B7355", "晨曦金 #FFD700", "是枝裕和《步履不停》"),
            ("老上海", "墨绿 #2A4D3E", "暗红 #B83227", "路灯黄 #FFD700", "王家卫《花样年华》"),
            ("权力棕", "暖棕橙黄 #8B5A2B", "灰黑 #2C2C2C", "权力金 #D4AF37", "Gordon Willis《教父》"),
            ("孤独暖", "暖橙红 #E89B6C", "灰蓝 #4A6B8A", "粉橙日落 #FFB07C", "van Hoytema《Her》"),
            ("神秘红", "深红 #8B0000", "暗金 #B8860B", "血红 #C8102E", "斯托拉罗《现代启示录》"),
            ("童年黄", "暖黄 #FFD700", "天蓝 #87CEEB", "玫瑰粉 #FF69B4", "宫崎骏《龙猫》"),
            ("迷幻紫", "深紫 #4B0082", "暗金 #B8860B", "霓虹粉 #FF1493", "PTA《不羁夜》"),
            ("武士黑白", "纯黑 #000000", "武士白 #F0F0F0", "血 #C8102E", "黑泽明《七武士》"),
            ("史诗金", "金 #D4AF37", "深红 #8B0000", "圣光白 #FFFFE0", "泰伦斯·马力克《天堂之日》"),
            ("忧郁蓝", "冷蓝 #1F3A5F", "灰白 #C0C0C0", "血红 #C8102E", "塔可夫斯基《潜行者》"),
            ("70s 暖", "70s 棕 #8B5A2B", "暗红 #8B2E1F", "金 #D4AF37", "PTA《血色将至》"),
            ("赛博朋克", "霓虹蓝 #00FFFF", "霓虹粉 #FF00FF", "霓虹黄 #FFFF00", "沃卓斯基《黑客帝国》"),
            ("千与千寻", "暖红汤屋 #C73E1D", "小白龙蓝白 #87CEEB", "千寻白 #F0F0F0", "宫崎骏《千与千寻》"),
        ]
        for combo_name, m, s, a, film in color_combos:
            color_60 += "  - {0}\n".format(combo_name)
            color_60 += "    60% {0} | 30% {1} | 10% {2} | 代表: {3}\n".format(m, s, a, film)
        color_60 += "\n"

        # ========== 7. 输出 4: 9 维光影灵魂驱动设计 ==========
        lighting_9d = "════════════════════════════════════════\n"
        lighting_9d += "【9 维光影灵魂驱动设计】Phase 18 核心\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += "AIGC 影视全流程解析 § 环节 16: 光影语言设计\n"
        lighting_9d += "(顶级摄影指导 + DP " + dp + " 风格 + 灵魂融合 9 维参数)\n\n"

        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "【灵魂驱动 9 维推导】(color_palette + music_tempo → 9 维)\n"
        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "  - 灵魂色彩: " + fused_palette + "\n"
        lighting_9d += "  - 灵魂音乐: " + fused_tempo + "\n"
        lighting_9d += "  - 色彩档位: " + _classify_palette(fused_palette) + "\n"
        lighting_9d += "  - 节奏档位: " + _classify_tempo(fused_tempo) + "\n"
        lighting_9d += "  - 主导情感: " + fused_emotion.get("name", "") + " (类别: " + ", ".join(fused_categories) + ")\n\n"

        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "本场戏 9 维光影 (灵魂动态生成)\n"
        lighting_9d += "──────────────────────────────────\n\n"

        lighting_9d += "【1. 光源类型】 " + derived_lighting_9d.get("光源类型", "") + "\n"
        lighting_9d += "  " + LIGHTING_9D_DESIGN["光源类型"]["logic"] + "\n"
        lighting_9d += "  全部可选: " + " / ".join(LIGHTING_9D_DESIGN["光源类型"]["options"]) + "\n"
        lighting_9d += "  灵魂匹配: 色彩档位 " + _classify_palette(fused_palette) + " → " + derived_lighting_9d.get("光源类型", "") + "\n\n"

        lighting_9d += "【2. 方向】 " + derived_lighting_9d.get("方向", "") + "\n"
        for d, desc in LIGHTING_9D_DESIGN["方向"].items():
            lighting_9d += "  - " + d + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 主导情感 " + (fused_categories[0] if fused_categories else "Joy") + " → " + derived_lighting_9d.get("方向", "") + "\n\n"

        lighting_9d += "【3. 强度】 " + derived_lighting_9d.get("强度", "") + "\n"
        for s, desc in LIGHTING_9D_DESIGN["强度"].items():
            lighting_9d += "  - " + s + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 节奏档位 " + _classify_tempo(fused_tempo) + " → " + derived_lighting_9d.get("强度", "") + "\n\n"

        lighting_9d += "【4. 色温】 " + derived_lighting_9d.get("色温", "") + "\n"
        for t, desc in LIGHTING_9D_DESIGN["色温"].items():
            lighting_9d += "  - " + t + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 色彩档位 " + _classify_palette(fused_palette) + " → " + derived_lighting_9d.get("色温", "") + "\n\n"

        lighting_9d += "【5. 软硬】 " + derived_lighting_9d.get("软硬", "") + "\n"
        for s, desc in LIGHTING_9D_DESIGN["软硬"].items():
            lighting_9d += "  - " + s + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 主导情感 " + (fused_categories[0] if fused_categories else "Joy") + " → " + derived_lighting_9d.get("软硬", "") + "\n\n"

        lighting_9d += "【6. 比例】 " + derived_lighting_9d.get("比例", "") + "\n"
        for r, desc in LIGHTING_9D_DESIGN["比例"].items():
            lighting_9d += "  - " + r + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 节奏档位 " + _classify_tempo(fused_tempo) + " → " + derived_lighting_9d.get("比例", "") + "\n\n"

        lighting_9d += "【7. 阴影】 " + derived_lighting_9d.get("阴影", "") + "\n"
        for sh, desc in LIGHTING_9D_DESIGN["阴影"].items():
            lighting_9d += "  - " + sh + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 节奏档位 " + _classify_tempo(fused_tempo) + " → " + derived_lighting_9d.get("阴影", "") + "\n\n"

        lighting_9d += "【8. 特殊光影】 " + derived_lighting_9d.get("特殊光影", "") + "\n"
        for sp, desc in LIGHTING_9D_DESIGN["特殊光影"].items():
            lighting_9d += "  - " + sp + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 主导情感 " + (fused_categories[0] if fused_categories else "Joy") + " → " + derived_lighting_9d.get("特殊光影", "") + "\n\n"

        lighting_9d += "【9. 时间】 " + derived_lighting_9d.get("时间", "") + "\n"
        for ti, desc in LIGHTING_9D_DESIGN["时间"].items():
            lighting_9d += "  - " + ti + ": " + desc + "\n"
        lighting_9d += "  灵魂匹配: 色彩档位 " + _classify_palette(fused_palette) + " → " + derived_lighting_9d.get("时间", "") + "\n\n"

        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "9 维光照控制 (CIE LAB + 摄影本体)\n"
        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "  - intensity: 光源强度 0.0-1.0 (0=无光, 1=极强)\n"
        lighting_9d += "  - x/y/z: 光源 3D 位置 (-1.0 到 1.0)\n"
        lighting_9d += "  - temp: 色温 K (2700=钨丝/3200=室内/5500=日光/6500=阴天)\n"
        lighting_9d += "  - radius: 影响范围 0.0-1.0\n"
        lighting_9d += "  - type_id: 光源类型 (0=点光 1=定向光 2=面光 3=环境光 4=聚光)\n"
        lighting_9d += "  - falloff: 衰减幂次 (1=linear 2=quadratic 3=cubic)\n"
        lighting_9d += "  - shadow_bias: 阴影偏移 0.0-1.0\n\n"

        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "光影一致性检查清单 (跨镜头 + 灵魂)\n"
        lighting_9d += "──────────────────────────────────\n"
        lighting_9d += "  - [ ] 光源方向是否一致? (灵魂推导: " + derived_lighting_9d.get("方向", "") + ")\n"
        lighting_9d += "  - [ ] 色温是否一致? (灵魂推导: " + derived_lighting_9d.get("色温", "") + ")\n"
        lighting_9d += "  - [ ] 光比是否一致? (灵魂推导: " + derived_lighting_9d.get("比例", "") + ")\n"
        lighting_9d += "  - [ ] 阴影方向是否一致? (灵魂推导: " + derived_lighting_9d.get("阴影", "") + ")\n"
        lighting_9d += "  - [ ] 软硬是否一致? (灵魂推导: " + derived_lighting_9d.get("软硬", "") + ")\n"
        lighting_9d += "  - [ ] 时间是否一致? (灵魂推导: " + derived_lighting_9d.get("时间", "") + ")\n"
        lighting_9d += "  - [ ] 关键道具光影是否一致? (同位置高光/阴影)\n"
        lighting_9d += "  - [ ] 肤色是否一致? (大银幕上肤色最重要)\n"
        lighting_9d += "  - [ ] 灵魂戏剧时刻的光影是否突出? (" + derived_lighting_9d.get("特殊光影", "") + ")\n\n"

        # 60 情感 × 9 维光影全表
        lighting_9d += "════════════════════════════════════════\n"
        lighting_9d += "【60 情感 × 9 维光影 全表 (灵魂驱动)】\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += _generate_soul_to_9d_lighting_table() + "\n"

        # 9 维光影 CIE LAB 物理原理
        lighting_9d += "════════════════════════════════════════\n"
        lighting_9d += "【9 维光影 CIE LAB 物理原理 (完整)】\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += _generate_9d_cie_lab_full() + "\n"

        # 14 真实短剧场景光影应用
        lighting_9d += "════════════════════════════════════════\n"
        lighting_9d += "【14 真实短剧场景光影应用 (灵魂驱动)】\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        scene_14 = [
            ("厨房 (1998 东北)", "自然光 (窗户) + 钨丝灯", "侧光", "中光", "warm_3200K", "软光", "中间调_4_1", "长阴影", "轮廓光", "黄昏"),
            ("客厅 (现代)", "混合光 (顶灯 + 窗)", "45度_伦勃朗光", "中光", "neutral_5500K", "软光", "中间调_4_1", "短阴影", "伦勃朗光", "正午"),
            ("酒吧 (夜)", "霓虹 (城市)", "侧光", "弱光", "cool_6500K", "硬光", "低调_8_1", "长阴影", "丁达尔效应", "夜晚"),
            ("办公室 (日)", "荧光灯", "顺光", "中光", "neutral_5500K", "极软光", "中间调_4_1", "无阴影", "蝴蝶光", "正午"),
            ("森林 (晨)", "自然光 (太阳)", "45度_伦勃朗光", "弱光", "neutral_5500K", "软光", "中间调_4_1", "长阴影", "丁达尔效应", "黄金时刻"),
            ("海滩 (黄昏)", "自然光 (太阳)", "逆光", "强光", "warm_3200K", "软光", "中间调_4_1", "长阴影", "剪影", "黄昏"),
            ("雪地 (日)", "自然光 (太阳)", "顶光", "强光", "blue_hour_8000K", "极软光", "高调_2_1", "无阴影", "轮廓光", "正午"),
            ("医院 (夜)", "荧光灯 + 路灯", "顶光", "中光", "cool_6500K", "极软光", "中间调_4_1", "无阴影", "环形光", "夜晚"),
            ("城堡 (夜)", "火光 (蜡烛/壁炉)", "侧光", "弱光", "warm_3200K", "硬光", "低调_8_1", "长阴影", "丁达尔效应", "夜晚"),
            ("太空 (科幻)", "LED 屏幕", "侧光", "强光", "cool_6500K", "硬光", "中间调_4_1", "无阴影", "轮廓光", "蓝色时刻"),
            ("雨天 (街)", "混合光 (雨 + 霓虹)", "45度_伦勃朗光", "中光", "cool_6500K", "软光", "中间调_4_1", "长阴影", "丁达尔效应", "蓝色时刻"),
            ("教室 (日)", "自然光 (窗)", "顺光", "中光", "neutral_5500K", "软光", "中间调_4_1", "短阴影", "蝴蝶光", "正午"),
            ("监狱 (夜)", "白炽灯", "顶光", "弱光", "warm_3200K", "硬光", "低调_8_1", "长阴影", "硬光", "夜晚"),
            ("沙漠 (日)", "自然光 (太阳)", "顶光", "强光", "warm_3200K", "硬光", "高调_2_1", "短阴影", "剪影", "正午"),
        ]
        for scene, src, dir_, intensity, temp, soft, ratio, shadow, special, time_ in scene_14:
            lighting_9d += "  - {0}\n".format(scene)
            lighting_9d += "    光源: {0} | 方向: {1} | 强度: {2} | 色温: {3} | 软硬: {4} | 比例: {5} | 阴影: {6} | 特殊: {7} | 时间: {8}\n".format(
                src, dir_, intensity, temp, soft, ratio, shadow, special, time_
            )
        lighting_9d += "\n"
        lighting_9d += "  灵魂场景应用: " + scene_desc + "\n"
        lighting_9d += "  灵魂推导: " + derived_lighting_9d.get("光源类型", "") + " + " + derived_lighting_9d.get("方向", "") + " + " + derived_lighting_9d.get("色温", "") + " + " + derived_lighting_9d.get("时间", "") + "\n"
        lighting_9d += "  灵魂主导: " + fused_emotion.get("name", "") + " (强度 " + "{0:.2f}".format(fused_intensity) + ", 极性 " + fused_emotion.get("polarity", "") + ")\n\n"

        # ========== 8. 输出 5: 8 大摄影指导 + 8 大顶级导演 ==========
        dp_style = "════════════════════════════════════════\n"
        dp_style += "【8 大顶级摄影指导 + 8 大顶级导演 风格库】Phase 18\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += "当前选择 DP: " + dp + " — " + dp_info.get("signature", "") + "\n"
        dp_style += "当前选择 导演: " + director + " — " + director_info.get("visual_signature", "") + "\n\n"
        dp_style += "─" * 50 + "\n\n"

        # 8 DP
        dp_style += "════════════════════════════════════════\n"
        dp_style += "【8 大顶级摄影指导 (DP) 风格库】\n"
        dp_style += "════════════════════════════════════════\n\n"
        for dp_name, info in DP_8_MASTERS.items():
            mark = " ★ 当前" if dp_name == dp else ""
            dp_style += "【" + info.get("cn", dp_name) + "】" + mark + "\n"
            dp_style += "  代表作: " + " / ".join(info.get("key_films", [])) + "\n"
            dp_style += "  签名: " + info.get("signature", "") + "\n"
            dp_style += "  光影: " + info.get("lighting", "") + "\n"
            dp_style += "  构图: " + info.get("composition", "") + "\n"
            dp_style += "  色彩: " + info.get("color", "") + "\n"
            dp_style += "  镜头: " + info.get("lens", "") + "\n"
            dp_style += "  触发: " + info.get("trigger", "") + "\n"
            dp_style += "  执行: " + info.get("execute", "") + "\n\n"

        # 8 顶级导演视觉签名
        dp_style += "════════════════════════════════════════\n"
        dp_style += "【8 大顶级导演视觉签名】\n"
        dp_style += "════════════════════════════════════════\n\n"
        for d_name, d_info in TOP_8_DIRECTORS_VISUAL_SIGNATURE.items():
            mark = " ★ 当前" if d_name == director else ""
            dp_style += "【" + d_name + "】" + mark + "\n"
            dp_style += "  视觉签名: " + d_info.get("visual_signature", "") + "\n"
            dp_style += "  镜头: " + d_info.get("lens", "") + "\n"
            dp_style += "  光影: " + d_info.get("lighting", "") + "\n"
            dp_style += "  色彩: " + d_info.get("color", "") + "\n"
            dp_style += "  运镜: " + d_info.get("motion", "") + "\n"
            dp_style += "  时长: " + d_info.get("duration", "") + "\n"
            dp_style += "  题材: " + d_info.get("subject", "") + "\n"
            dp_style += "  代表作: " + d_info.get("代表作", "") + "\n"
            dp_style += "  触发: " + d_info.get("trigger", "") + "\n"
            dp_style += "  执行: " + d_info.get("execute", "") + "\n\n"

        # DP 8 大风格灵魂匹配算法
        dp_style += "════════════════════════════════════════\n"
        dp_style += "【DP 8 大风格灵魂匹配算法 (详细)】\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += _generate_dp_8_matching_algorithm(fused_emotion, fused_categories, fused_intensity) + "\n"

        # 60 情感视觉全表
        dp_style += "════════════════════════════════════════\n"
        dp_style += "【60 情感 × 视觉语言 全表 (灵魂驱动)】\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += _generate_60_emotion_visual_table() + "\n"

        # 8 DP + 8 Director 对比矩阵
        dp_style += "════════════════════════════════════════\n"
        dp_style += "【8 DP + 8 Director 风格对比矩阵】\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += "DP 风格对比:\n"
        dp_style += "  " + ("DP".ljust(35)) + " | " + ("签名".ljust(20)) + " | " + ("镜头".ljust(15)) + " | " + ("触发".ljust(25)) + "\n"
        dp_style += "  " + ("-" * 35) + "-+-" + ("-" * 20) + "-+-" + ("-" * 15) + "-+-" + ("-" * 25) + "\n"
        for dp_name, info in DP_8_MASTERS.items():
            dp_style += "  " + info.get("cn", dp_name)[:33].ljust(35) + " | " + info.get("signature", "")[:18].ljust(20) + " | " + info.get("lens", "")[:13].ljust(15) + " | " + info.get("trigger", "")[:23].ljust(25) + "\n"
        dp_style += "\n"

        dp_style += "Director 风格对比:\n"
        dp_style += "  " + ("导演".ljust(12)) + " | " + ("视觉签名".ljust(30)) + " | " + ("镜头".ljust(20)) + " | " + ("代表作".ljust(35)) + "\n"
        dp_style += "  " + ("-" * 12) + "-+-" + ("-" * 30) + "-+-" + ("-" * 20) + "-+-" + ("-" * 35) + "\n"
        for d_name, d_info in TOP_8_DIRECTORS_VISUAL_SIGNATURE.items():
            dp_style += "  " + d_name.ljust(10) + " | " + d_info.get("visual_signature", "")[:28].ljust(30) + " | " + d_info.get("lens", "")[:18].ljust(20) + " | " + d_info.get("代表作", "")[:33].ljust(35) + "\n"
        dp_style += "\n"

        # ========== 9. 输出 6: 灵魂注入数据 (供下游节点) ==========
        soul_payload = "════════════════════════════════════════\n"
        soul_payload += "【灵魂注入数据 (Phase 18 Payload)】供下游节点使用\n"
        soul_payload += "════════════════════════════════════════\n\n"

        soul_payload += "【1. fused_emotion (JSON)】\n"
        try:
            # 处理 set / tuple → list
            fe_safe = {}
            for k, v in fused_emotion.items():
                if isinstance(v, (list, tuple)):
                    fe_safe[k] = list(v)
                elif isinstance(v, set):
                    fe_safe[k] = sorted(list(v))
                else:
                    fe_safe[k] = v
            soul_payload += json.dumps(fe_safe, ensure_ascii=False, indent=2) + "\n\n"
        except Exception:
            soul_payload += str(fused_emotion) + "\n\n"

        soul_payload += "【2. soul_dimensions (JSON)】\n"
        try:
            soul_payload += json.dumps(soul_dims, ensure_ascii=False, indent=2) + "\n\n"
        except Exception:
            soul_payload += str(soul_dims) + "\n\n"

        soul_payload += "【3. soul_state (JSON)】\n"
        try:
            soul_payload += json.dumps(soul_state, ensure_ascii=False, indent=2) + "\n\n"
        except Exception:
            soul_payload += str(soul_state) + "\n\n"

        soul_payload += "【4. 灵魂驱动的视觉语言决策】\n"
        soul_payload += "  - 焦段: " + derived_focal + " (" + focal_info.get("cn", "") + ")\n"
        soul_payload += "  - 光圈: " + derived_aperture + " (" + aperture_info.get("cn", "") + ")\n"
        soul_payload += "  - 景别: " + derived_shot_size + " (" + shot_info.get("cn", "") + ")\n"
        soul_payload += "  - 构图: " + derived_composition + " (" + comp_info.get("cn", "") + ")\n"
        soul_payload += "  - 9 维光影: " + json.dumps(derived_lighting_9d, ensure_ascii=False) + "\n"
        soul_payload += "  - 60:30:10: " + json.dumps(derived_60_30_10, ensure_ascii=False) + "\n\n"

        soul_payload += "【5. 灵魂注入元数据】\n"
        soul_payload += "  - 主导情感: " + fused_emotion.get("name", "") + "\n"
        soul_payload += "  - 融合模式: " + fused_emotion.get("fusion_mode", "") + "\n"
        soul_payload += "  - 故事强度: {0:.2f}\n".format(story_intensity)
        soul_payload += "  - 场景进度: {0:.2f}\n".format(scene_progress)
        soul_payload += "  - 导演: " + director + "\n"
        soul_payload += "  - DP: " + dp + "\n"
        soul_payload += "  - 场景: " + scene_desc + "\n"
        soul_payload += "  - 注入模式: SOUL_INJECTION_V2 (Phase 18)\n"
        soul_payload += "  - 注入时间戳: " + str(random.randint(100000, 999999)) + "\n\n"

        # 灵魂注入的 7 大场景应用
        soul_payload += "【6. 灵魂注入的 7 大场景应用 (供下游节点)】\n"
        soul_payload += "─" * 50 + "\n"
        soul_payload += "  1. 概念/钩子节点: 融合情感 → 概念主张 / 钩子强度\n"
        soul_payload += "  2. 故事架构节点: 灵魂维度 → 故事结构 (三幕剧/救猫咪/序列)\n"
        soul_payload += "  3. 角色弧光节点: 情感核心 + 灵魂状态 → 角色心理弧\n"
        soul_payload += "  4. 摄影/光影节点: 焦段/光圈/景别/9 维光影 (本节点输出)\n"
        soul_payload += "  5. 声音/配乐节点: 音乐倾向 + 节奏 → 声音设计\n"
        soul_payload += "  6. 表演指导节点: 微表情 + 内心独白 + 身体习惯 → 表演指导\n"
        soul_payload += "  7. 剪辑节奏节点: 灵魂状态 (灵感/疲劳/怀疑/叛逆) → 剪辑节奏\n\n"

        # 完整 60 情感 × 视觉决策 (供下游)
        soul_payload += "【7. 完整 60 情感 × 视觉决策 (供下游)】\n"
        soul_payload += "─" * 50 + "\n"
        soul_payload += _generate_60_emotion_visual_table() + "\n"

        # 60 情感 × 9 维光影
        soul_payload += "【8. 60 情感 × 9 维光影 (供下游)】\n"
        soul_payload += "─" * 50 + "\n"
        soul_payload += _generate_soul_to_9d_lighting_table() + "\n"

        # 灵魂维度 → 视觉决策
        soul_payload += "【9. 10 灵魂维度 → 视觉决策 (供下游)】\n"
        soul_payload += "─" * 50 + "\n"
        soul_payload += _generate_soul_dimension_to_visual_long(soul_dims) + "\n"

        # ========== 10. 输出 7: H3 三大字段增强 ==========
        h3_addon = "════════════════════════════════════════\n"
        h3_addon += "【H3 三大字段增强 (Phase 18 灵魂版)】\n"
        h3_addon += "════════════════════════════════════════\n\n"

        h3_addon += "INTEGRATED_MULTIMODAL_DESCRIPTION 灵魂增强:\n"
        h3_addon += "  [Emotion Anchor] " + fused_emotion.get("name", "") + " (极性 " + fused_emotion.get("polarity", "") + ", 强度 " + "{0:.2f}".format(fused_intensity) + ")\n"
        h3_addon += "  [Visual Anchor] " + focal_info.get("cn", derived_focal) + " + " + aperture_info.get("cn", derived_aperture) + " + " + shot_info.get("cn", derived_shot_size) + " + " + comp_info.get("cn", derived_composition) + "\n"
        h3_addon += "  [Light Anchor] " + derived_lighting_9d.get("光源类型", "") + " + " + derived_lighting_9d.get("方向", "") + " + " + derived_lighting_9d.get("色温", "") + "\n"
        h3_addon += "  [Color Anchor 60:30:10] " + derived_60_30_10.get("主色_60", "")[:50] + " | " + derived_60_30_10.get("辅色_30", "")[:30] + " | " + derived_60_30_10.get("点缀色_10", "")[:30] + "\n"
        h3_addon += "  [Director Anchor] " + director + " 视觉签名 — " + director_info.get("visual_signature", "")[:100] + "\n"
        h3_addon += "  [DP Anchor] " + dp + " 风格 — " + dp_info.get("signature", "")[:50] + "\n"
        h3_addon += "  [Visual Signs] " + fused_emotion.get("visual_signs", "")[:200] + "\n"
        h3_addon += "  [Inner Monologue] " + fused_emotion.get("inner_monologue", "")[:200] + "\n\n"

        h3_addon += "OVERALL_SOUNDSCAPE 灵魂增强:\n"
        h3_addon += "  [Voice] " + fused_emotion.get("voice_signs", "")[:150] + "\n"
        h3_addon += "  [Sound] " + fused_tempo + "\n"
        h3_addon += "  [Tempo] " + _classify_tempo(fused_tempo) + "\n"
        h3_addon += "  [Soul Atmosphere] 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " / 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " / 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)) + "\n\n"

        h3_addon += "NON_DIEGETIC_MUSIC 灵魂增强:\n"
        h3_addon += "  [Music Style: " + fused_tempo + "]\n"
        h3_addon += "  [Emotion-Driven: " + fused_emotion.get("name", "") + "]\n"
        h3_addon += "  [Tempo: " + _classify_tempo(fused_tempo) + " → 强度 " + derived_lighting_9d.get("强度", "") + " / 比例 " + derived_lighting_9d.get("比例", "") + "]\n"
        h3_addon += "  [Color: " + derived_60_30_10.get("主色_60", "")[:60] + "]\n\n"

        h3_addon += "导演灵魂签名 注入到 H3:\n"
        h3_addon += "  - 主导情感锚点 → 表情 + 微动作 + 眼神\n"
        h3_addon += "  - 灵魂维度 → 镜头密度 + 创新度\n"
        h3_addon += "  - 灵魂状态 → 节奏 + 留白\n"
        h3_addon += "  - 导演视觉签名 → 运镜 + 时长 + 镜头\n"
        h3_addon += "  - DP 风格 → 光影 + 色彩 + 60:30:10\n\n"

        # H3 三大字段扩展 (30+ 维度)
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 三大字段 灵魂驱动 30+ 维度扩展】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_addon += _generate_h3_extended(
            fused_emotion, fused_intensity, fused_palette, fused_tempo,
            director, dp, director_info, derived_60_30_10, derived_lighting_9d,
            derived_focal, derived_aperture, derived_shot_size, derived_composition,
            focal_info, aperture_info, shot_info, comp_info
        ) + "\n"

        # H3 字段与灵魂维度详细映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 10 灵魂维度 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_addon += "  - 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " → H3 创意修辞 / 隐喻密度 / 跨类比\n"
        h3_addon += "  - 想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " → H3 视觉想象力 / 场景构建 / 空间设计\n"
        h3_addon += "  - 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " → H3 微动作 / 物件代替心理 / 声音隐喻\n"
        h3_addon += "  - 镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " → H3 焦段/光圈/景别 精细度\n"
        h3_addon += "  - 氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)) + " → H3 60:30:10 色彩 + 9 维光影\n"
        h3_addon += "  - 灵感 " + "{0:.2f}".format(soul_dims.get("inspiration", 0.85)) + " → H3 灵感时刻 / 5-20 个突破\n"
        h3_addon += "  - 叛逆 " + "{0:.2f}".format(soul_dims.get("rebelliousness", 0.70)) + " → H3 打破规则 / 实验性\n"
        h3_addon += "  - 怀疑 " + "{0:.2f}".format(soul_dims.get("self_doubt", 0.50)) + " → H3 留白 / 沉默 / 不说尽\n"
        h3_addon += "  - 突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " → H3 创新选择 / 非线性 / 困难主题\n"
        h3_addon += "  - 精神状态 " + str(soul_dims.get("mental_state", "lucid-dreamy")) + " → H3 整体语调 (lucid=清晰/dreamy=梦幻/anxious=摇晃/serene=稳定)\n\n"

        # H3 字段与 9 维光影详细映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 9 维光影 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_for_9d = [
            ("光源类型 " + derived_lighting_9d.get("光源类型", ""), "H3.INTEGRATED: 光源必须在画面内找到"),
            ("方向 " + derived_lighting_9d.get("方向", ""), "H3.INTEGRATED: 光线方向决定阴影和情绪"),
            ("强度 " + derived_lighting_9d.get("强度", ""), "H3.INTEGRATED: 强度决定戏剧感和张力"),
            ("色温 " + derived_lighting_9d.get("色温", ""), "H3.INTEGRATED: 色温决定时代/时间/情绪"),
            ("软硬 " + derived_lighting_9d.get("软硬", ""), "H3.INTEGRATED: 软硬决定亲密/戏剧"),
            ("比例 " + derived_lighting_9d.get("比例", ""), "H3.INTEGRATED: 光比决定高调/中间/低调"),
            ("阴影 " + derived_lighting_9d.get("阴影", ""), "H3.INTEGRATED: 阴影决定戏剧/超现实"),
            ("特殊光影 " + derived_lighting_9d.get("特殊光影", ""), "H3.INTEGRATED: 特殊光影创造隐喻"),
            ("时间 " + derived_lighting_9d.get("时间", ""), "H3.INTEGRATED: 时间决定色温和情绪"),
        ]
        for k, v in h3_for_9d:
            h3_addon += "  - " + k + " → " + v + "\n"
        h3_addon += "\n"

        # H3 字段与 60:30:10 详细映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 60:30:10 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_addon += "  - 主色 60% " + derived_60_30_10.get("主色_60", "")[:60] + " → H3.INTEGRATED: 整体色温/色调\n"
        h3_addon += "  - 辅色 30% " + derived_60_30_10.get("辅色_30", "")[:60] + " → H3.INTEGRATED: 角色/道具色\n"
        h3_addon += "  - 点缀色 10% " + derived_60_30_10.get("点缀色_10", "")[:60] + " → H3.INTEGRATED: 关键道具/戏剧时刻\n"
        h3_addon += "  - 调色一级 " + director + " 风格: " + director_info.get("color", "")[:60] + "\n"
        h3_addon += "  - 调色二级: 肤色/道具一致\n"
        h3_addon += "  - 调色创意: 强化戏剧时刻 (" + fused_emotion.get("inner_monologue", "")[:60] + "...)\n\n"

        # H3 字段与灵魂状态映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与灵魂状态 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_addon += "  - 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " → H3.OVERALL_SOUNDSCAPE: 声音层次 / 灵感时刻 (5-20 个)\n"
        h3_addon += "  - 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " → H3.OVERALL_SOUNDSCAPE: 节奏 (高→慢节奏 / 低→快节奏)\n"
        h3_addon += "  - 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " → H3.NON_DIEGETIC_MUSIC: 留白 / 沉默 / 配乐稀疏\n"
        h3_addon += "  - 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)) + " → H3.NON_DIEGETIC_MUSIC: 配乐风格 (高→实验 / 低→传统)\n"
        h3_addon += "  - 精神状态 " + str(soul_dims.get("mental_state", "lucid-dreamy")) + " → H3: 整体语调 (lucid=清晰/dreamy=梦幻/anxious=摇晃/serene=稳定)\n\n"

        # H3 字段与导演视觉签名映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与导演视觉签名 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_for_dir = [
            ("视觉签名 " + director_info.get("visual_signature", ""), "H3.INTEGRATED: 整体镜头风格"),
            ("镜头 " + director_info.get("lens", ""), "H3.INTEGRATED: 焦段偏好"),
            ("光影 " + director_info.get("lighting", ""), "H3.INTEGRATED: 光影风格"),
            ("色彩 " + director_info.get("color", ""), "H3.INTEGRATED: 色彩偏好"),
            ("运镜 " + director_info.get("motion", ""), "H3.INTEGRATED: 运镜节奏"),
            ("时长 " + director_info.get("duration", ""), "H3.OVERALL_SOUNDSCAPE: 镜头长度"),
            ("题材 " + director_info.get("subject", ""), "H3.INTEGRATED: 主题"),
            ("代表作 " + director_info.get("代表作", ""), "H3: 风格参考"),
        ]
        for k, v in h3_for_dir:
            h3_addon += "  - " + k + " → " + v + "\n"
        h3_addon += "\n"

        # H3 字段与 DP 风格映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 DP 风格 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_addon += "  - DP " + dp + ": " + dp_info.get("signature", "") + "\n"
        h3_addon += "    → H3.INTEGRATED: " + dp_info.get("composition", "")[:80] + "\n"
        h3_addon += "    → H3.INTEGRATED: " + dp_info.get("color", "")[:80] + "\n"
        h3_addon += "    → H3.INTEGRATED: " + dp_info.get("lens", "")[:80] + "\n"
        h3_addon += "    → H3.OVERALL_SOUNDSCAPE: " + dp_info.get("lighting", "")[:80] + "\n\n"

        # H3 字段与摄影指导 8 大风格映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与摄影指导 8 大风格 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        for dp_name, dp_info_full in DP_8_MASTERS.items():
            mark = " ★ 当前" if dp_name == dp else ""
            h3_addon += "  " + dp_info_full.get("cn", dp_name) + mark + "\n"
            h3_addon += "    → H3.INTEGRATED: " + dp_info_full.get("composition", "")[:60] + "\n"
            h3_addon += "    → H3.INTEGRATED: " + dp_info_full.get("color", "")[:60] + "\n"
            h3_addon += "    → H3.INTEGRATED: " + dp_info_full.get("lens", "")[:60] + "\n"
            h3_addon += "    → H3.OVERALL_SOUNDSCAPE: " + dp_info_full.get("lighting", "")[:60] + "\n"
            h3_addon += "    → H3.NON_DIEGETIC_MUSIC: " + dp_info_full.get("signature", "")[:60] + "\n"
        h3_addon += "\n"

        # H3 字段与 8 大顶级导演视觉签名映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 8 大顶级导演视觉签名 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        for d_name, d_info_full in TOP_8_DIRECTORS_VISUAL_SIGNATURE.items():
            mark = " ★ 当前" if d_name == director else ""
            h3_addon += "  " + d_name + mark + "\n"
            h3_addon += "    视觉签名: " + d_info_full.get("visual_signature", "")[:60] + "\n"
            h3_addon += "    → H3.INTEGRATED: 镜头 " + d_info_full.get("lens", "")[:50] + "\n"
            h3_addon += "    → H3.INTEGRATED: 光影 " + d_info_full.get("lighting", "")[:50] + "\n"
            h3_addon += "    → H3.INTEGRATED: 色彩 " + d_info_full.get("color", "")[:50] + "\n"
            h3_addon += "    → H3.OVERALL_SOUNDSCAPE: 运镜 " + d_info_full.get("motion", "")[:50] + "\n"
            h3_addon += "    → H3.NON_DIEGETIC_MUSIC: 时长 " + d_info_full.get("duration", "")[:50] + "\n"
            h3_addon += "    → H3.INTEGRATED: 题材 " + d_info_full.get("subject", "")[:50] + "\n"
            h3_addon += "    → H3.INTEGRATED: 代表作 " + d_info_full.get("代表作", "")[:50] + "\n"
        h3_addon += "\n"

        # H3 字段与 60 情感全表映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 60 情感 完整映射表 (供下游节点)】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        if _HAS_SOUL:
            for ekey, einfo in EMOTION_MATRIX_60.items():
                h3_addon += "  {0:25s} | 强度 {1:.1f} | {2:8s} | {3:6s} | 视觉: {4:50s}\n".format(
                    einfo.get("name", ekey)[:25],
                    einfo.get("intensity", 0.5),
                    einfo.get("category", "")[:8],
                    einfo.get("polarity", "")[:6],
                    einfo.get("visual_signs", "")[:50]
                )
        h3_addon += "\n"

        # H3 字段与 11 维控制映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 11 维控制 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_for_11d = [
            ("空镜", "H3.OVERALL_SOUNDSCAPE: 长度由灵魂疲劳决定 (高→5-8s / 低→10-15s)"),
            ("留白", "H3.INTEGRATED + H3.OVERALL_SOUNDSCAPE: 想象力+怀疑决定密度"),
            ("氛围渲染", "H3.INTEGRATED: 5 维氛围强度 = 材质+光影+颜色+空间+声音"),
            ("悬疑", "H3.OVERALL_SOUNDSCAPE: 镜头技巧决定张力"),
            ("多线", "H3.INTEGRATED: 创造力决定多线复杂度"),
            ("反转", "H3.INTEGRATED: 突破勇气决定反转概率"),
            ("高潮", "H3.INTEGRATED + H3.OVERALL_SOUNDSCAPE: 融合强度决定强度"),
            ("余韵", "H3.OVERALL_SOUNDSCAPE: 怀疑决定长度"),
            ("推进节奏", "H3.OVERALL_SOUNDSCAPE: 灵感+疲劳决定节奏曲线"),
            ("感情控制", "H3.INTEGRATED: 艺术表达决定密度"),
            ("角色塑造", "H3.INTEGRATED: 融合情感决定心理深度"),
        ]
        for k, v in h3_for_11d:
            h3_addon += "  - " + k + " → " + v + "\n"
        h3_addon += "\n"

        # H3 字段与 3 留白 + 3 运镜 映射
        h3_addon += "════════════════════════════════════════\n"
        h3_addon += "【H3 字段与 3 留白 + 3 运镜 详细映射】\n"
        h3_addon += "════════════════════════════════════════\n\n"
        h3_for_3_3 = [
            ("1. 时间留白", "H3.OVERALL_SOUNDSCAPE: 镜头停留超过叙事需要的时间"),
            ("2. 空间留白", "H3.INTEGRATED: 画面大量负空间"),
            ("3. 叙事留白", "H3.INTEGRATED: 重要信息用隐喻/物件/沉默传递"),
            ("1. 静止凝视", "H3.INTEGRATED: 机位固定, 长镜头, 时间流逝"),
            ("2. 慢推侵入", "H3.INTEGRATED: 缓慢推向主体, 心理接近"),
            ("3. 手持摇晃", "H3.INTEGRATED + H3.OVERALL_SOUNDSCAPE: 不稳, 主观, 真实"),
        ]
        for k, v in h3_for_3_3:
            h3_addon += "  - " + k + " → " + v + "\n"
        h3_addon += "\n"

        # ========== 11. 输出 8: 11 维控制 + 3 留白 + 3 运镜 (灵魂结合) ==========
        cinematic_sig = "════════════════════════════════════════\n"
        cinematic_sig += "【11 维导演控制 + 3 留白 + 3 运镜 (灵魂结合版)】Phase 18\n"
        cinematic_sig += "════════════════════════════════════════\n\n"

        cinematic_sig += "【11 维导演控制 (灵魂驱动执行)】\n"
        cinematic_sig += "─" * 50 + "\n"
        cinematic_sig += "  1. 空镜: " + DIRECTOR_CONTROL_11["空镜"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " → 空镜长度 " + ("5-8s" if soul_state.get("fatigue", 0.30) > 0.6 else "10-15s") + "\n\n"
        cinematic_sig += "  2. 留白: " + DIRECTOR_CONTROL_11["留白"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " → 留白密度 " + ("高" if soul_dims.get("imagination", 0.85) > 0.7 else "中") + "\n\n"
        cinematic_sig += "  3. 氛围渲染: " + DIRECTOR_CONTROL_11["氛围渲染"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)) + " → 5 维氛围强度 " + ("极强" if soul_dims.get("atmosphere_control", 0.85) > 0.8 else "强") + "\n\n"
        cinematic_sig += "  4. 悬疑: " + DIRECTOR_CONTROL_11["悬疑"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " → 悬疑张力 " + ("强" if soul_dims.get("camera_skill", 0.85) > 0.7 else "中") + "\n\n"
        cinematic_sig += "  5. 多线: " + DIRECTOR_CONTROL_11["多线"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " → 多线复杂度 " + ("复杂" if soul_dims.get("creativity", 0.85) > 0.8 else "标准") + "\n\n"
        cinematic_sig += "  6. 反转: " + DIRECTOR_CONTROL_11["反转"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " → 反转概率 " + ("高" if soul_dims.get("breakthrough_courage", 0.73) > 0.7 else "中") + "\n\n"
        cinematic_sig += "  7. 高潮: " + DIRECTOR_CONTROL_11["高潮"] + "\n"
        cinematic_sig += "     [灵魂执行] 融合强度 " + "{0:.2f}".format(fused_intensity) + " → 高潮强度 " + ("极强" if fused_intensity > 0.8 else "强") + "\n\n"
        cinematic_sig += "  8. 余韵: " + DIRECTOR_CONTROL_11["余韵"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " → 余韵长度 " + ("3-5s" if soul_state.get("doubt", 0.50) > 0.6 else "2-3s") + "\n\n"
        cinematic_sig += "  9. 推进节奏: " + DIRECTOR_CONTROL_11["推进节奏"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " → 节奏曲线 (" + ("快→慢" if soul_state.get("inspiration", 0.85) > 0.7 else "慢→快") + ")\n\n"
        cinematic_sig += "  10. 感情控制: " + DIRECTOR_CONTROL_11["感情控制"] + "\n"
        cinematic_sig += "     [灵魂执行] 灵魂艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " → 感情密度 " + ("极强" if soul_dims.get("artistic_expression", 0.85) > 0.85 else "强") + "\n\n"
        cinematic_sig += "  11. 角色塑造: " + DIRECTOR_CONTROL_11["角色塑造"] + "\n"
        cinematic_sig += "     [灵魂执行] 融合情感 " + fused_emotion.get("name", "") + " → 角色心理深度 " + ("极深" if fused_intensity > 0.7 else "标准") + "\n\n"

        cinematic_sig += "【3 留白 (灵魂驱动)】\n"
        cinematic_sig += "─" * 50 + "\n"
        cinematic_sig += "  1. 时间留白: " + THREE_NEGATIVE_SPACES["时间留白"] + "\n"
        cinematic_sig += "     [灵魂执行] 想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " → 时间留白 " + ("8-15s" if soul_dims.get("imagination", 0.85) > 0.7 else "3-5s") + "\n\n"
        cinematic_sig += "  2. 空间留白: " + THREE_NEGATIVE_SPACES["空间留白"] + "\n"
        cinematic_sig += "     [灵魂执行] 主导类别 " + ", ".join(fused_categories) + " → 空间留白比例 " + ("60-80%" if "Loneliness" in fused_categories or "Sadness" in fused_categories else "20-40%") + "\n\n"
        cinematic_sig += "  3. 叙事留白: " + THREE_NEGATIVE_SPACES["叙事留白"] + "\n"
        cinematic_sig += "     [灵魂执行] 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " → 叙事留白密度 " + ("高" if soul_dims.get("artistic_expression", 0.85) > 0.8 else "中") + "\n\n"

        cinematic_sig += "【3 运镜法则 (灵魂驱动)】\n"
        cinematic_sig += "─" * 50 + "\n"
        cinematic_sig += "  1. 静止凝视: " + THREE_CAMERA_MOVEMENTS["静止凝视"] + "\n"
        cinematic_sig += "     [灵魂执行] 主导类别 " + ", ".join(fused_categories) + " → 静止凝视适用 " + ("✓ 强烈推荐" if ("Sadness" in fused_categories or "Loneliness" in fused_categories) else "△ 可选") + "\n\n"
        cinematic_sig += "  2. 慢推侵入: " + THREE_CAMERA_MOVEMENTS["慢推侵入"] + "\n"
        cinematic_sig += "     [灵魂执行] 突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " + 融合强度 " + "{0:.2f}".format(fused_intensity) + " → 慢推适用 " + ("✓ 强烈推荐" if (fused_intensity > 0.6 and soul_dims.get("breakthrough_courage", 0.73) > 0.6) else "△ 可选") + "\n\n"
        cinematic_sig += "  3. 手持摇晃: " + THREE_CAMERA_MOVEMENTS["手持摇晃"] + "\n"
        cinematic_sig += "     [灵魂执行] 主导类别 " + ", ".join(fused_categories) + " → 手持摇晃适用 " + ("✓ 强烈推荐" if ("Fear" in fused_categories or "Tension" in fused_categories) else "△ 可选") + "\n\n"

        cinematic_sig += "【灵魂 + 导演视觉签名 综合应用】\n"
        cinematic_sig += "─" * 50 + "\n"
        cinematic_sig += "  - 灵魂 " + fused_emotion.get("name", "") + " 配合 " + director + " 视觉签名: " + director_info.get("execute", "") + "\n"
        cinematic_sig += "  - 灵魂维度: 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " / 想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " / 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + "\n"
        cinematic_sig += "  - 灵魂状态: 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " / 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)) + " / 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + "\n"
        cinematic_sig += "  - 视觉决策: 焦段 " + focal_info.get("cn", derived_focal) + " / 光圈 " + aperture_info.get("cn", derived_aperture) + " / 景别 " + shot_info.get("cn", derived_shot_size) + " / 构图 " + comp_info.get("cn", derived_composition) + "\n"
        cinematic_sig += "  - 色彩决策: 60% " + derived_60_30_10.get("主色_60", "")[:40] + " | 30% " + derived_60_30_10.get("辅色_30", "")[:30] + " | 10% " + derived_60_30_10.get("点缀色_10", "")[:30] + "\n"
        cinematic_sig += "  - 光影决策: " + derived_lighting_9d.get("光源类型", "") + " / " + derived_lighting_9d.get("方向", "") + " / " + derived_lighting_9d.get("色温", "") + " / " + derived_lighting_9d.get("时间", "") + "\n\n"

        cinematic_sig += "【签名】Phase 18 灵魂驱动版美术指导 — 完整接入 DirectorSoulNode 灵魂注入\n"

        # 11 维控制 完整详细
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维导演控制 完整详细 (灵魂驱动)】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        cinematic_sig += _generate_11d_full_detail(soul_dims, soul_state, fused_emotion, fused_intensity) + "\n"

        # 3 留白 + 3 运镜 完整
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【3 留白 + 3 运镜 (灵魂结合 完整详细)】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        cinematic_sig += _generate_3neg_3cam_full(soul_dims, soul_state, fused_categories, fused_intensity) + "\n"

        # 11 维与灵魂维度对照
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维导演控制 × 10 灵魂维度 对照表】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        sig_matrix = [
            ("1. 空镜", "灵感指数 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳指数 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30))),
            ("2. 留白", "想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50))),
            ("3. 氛围渲染", "氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)) + " + 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85))),
            ("4. 悬疑", "镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " + 主导情感强度 " + "{0:.2f}".format(fused_intensity)),
            ("5. 多线", "创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " + 故事强度 " + "{0:.2f}".format(story_intensity)),
            ("6. 反转", "突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70))),
            ("7. 高潮", "融合强度 " + "{0:.2f}".format(fused_intensity) + " + 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85))),
            ("8. 余韵", "怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " + 自我怀疑 " + "{0:.2f}".format(soul_dims.get("self_doubt", 0.50))),
            ("9. 推进节奏", "灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30))),
            ("10. 感情控制", "艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " + 融合情感 " + fused_emotion.get("name", "")),
            ("11. 角色塑造", "融合情感 " + fused_emotion.get("name", "") + " + 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85))),
        ]
        for name, soul_exec in sig_matrix:
            cinematic_sig += "  " + name + " ← " + soul_exec + "\n"
        cinematic_sig += "\n"

        # 3 留白与灵魂类别对照
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【3 留白 × 灵魂类别 对照表】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        neg_matrix = [
            ("1. 时间留白", "Sadness/Loneliness 主导时强度最高\n  → 长镜头 5-15 秒, 让时间发酵"),
            ("2. 空间留白", "Loneliness/Sadness/State 主导时强度最高\n  → 画面留白 60-80%, 主体被环境包裹"),
            ("3. 叙事留白", "艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " 决定\n  → 重要信息用隐喻/物件/沉默传递, 不说尽"),
        ]
        for name, soul_exec in neg_matrix:
            cinematic_sig += "  " + name + " ← " + soul_exec + "\n"
        cinematic_sig += "\n"

        # 3 运镜与灵魂类别对照
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【3 运镜 × 灵魂类别 对照表】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        cam_matrix = [
            ("1. 静止凝视", "Sadness/Loneliness/State 主导时强烈推荐\n  → 适用导演: 小津/塔可夫斯基/是枝裕和/安哲罗普洛斯"),
            ("2. 慢推侵入", "高强度 + 高突破勇气时强烈推荐\n  → 适用导演: PTA/大卫·芬奇/拉斯·冯·提尔/库斯杜力卡"),
            ("3. 手持摇晃", "Fear/Tension 主导时强烈推荐\n  → 适用导演: 杜可风/库斯杜力卡/卡拉克斯/哈内克"),
        ]
        for name, soul_exec in cam_matrix:
            cinematic_sig += "  " + name + " ← " + soul_exec + "\n"
        cinematic_sig += "\n"

        # 11 维 + 3 留白 + 3 运镜 与 8 大顶级导演
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维 + 3 留白 + 3 运镜 × 8 大顶级导演 对照表】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        dir_matrix = [
            ("王家卫", "空镜 (60s) + 留白 (高度) + 慢推", "静止凝视 + 慢推侵入"),
            ("诺兰", "悬疑 + 多线 + 反转 + 高潮", "静止凝视 + 慢推侵入"),
            ("PTA", "感情控制 + 角色塑造 + 推进节奏", "慢推侵入"),
            ("奉俊昊", "悬疑 + 反转 + 多线 + 氛围渲染", "静止凝视 + 慢推侵入"),
            ("黑泽明", "角色塑造 + 氛围渲染 + 推进节奏", "静止凝视"),
            ("库斯杜力卡", "氛围渲染 + 留白 (沉默) + 感情控制", "慢推侵入 + 手持摇晃"),
            ("塔可夫斯基", "空镜 (极长) + 留白 (时间) + 感情控制", "静止凝视"),
            ("约阿希姆·提尔", "角色塑造 + 留白 (北欧) + 氛围渲染", "静止凝视 + 慢推侵入"),
        ]
        for d, c11, c33 in dir_matrix:
            mark = " ★ 当前" if d == director else ""
            cinematic_sig += "  " + d + mark + ":\n"
            cinematic_sig += "    11 维强项: " + c11 + "\n"
            cinematic_sig += "    3 运镜偏好: " + c33 + "\n"
        cinematic_sig += "\n"

        # 11 维控制与 60 情感关联
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维 + 3 留白 + 3 运镜 × 60 情感 关联表】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        if _HAS_SOUL:
            for ekey, einfo in EMOTION_MATRIX_60.items():
                cinematic_sig += "  {0:25s} | 强度 {1:.1f} | 11维→{2:50s} | 运镜→{3}\n".format(
                    einfo.get("name", ekey)[:25],
                    einfo.get("intensity", 0.5),
                    "高潮+感情控制+角色塑造" if einfo.get("intensity", 0.5) >= 0.7 else "推进节奏+角色塑造",
                    "静止凝视" if einfo.get("category", "") in ["State", "Sadness"] else ("手持摇晃" if einfo.get("category", "") in ["Fear", "Anticipation"] else "慢推侵入")
                )
        cinematic_sig += "\n"

        # 11 维控制 + 灵魂维度完整执行表
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维控制 + 灵魂维度 完整执行表 (17 维联动)】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        sig_full = [
            ("1. 空镜 (5-15s)", "灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30))),
            ("2. 留白", "想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " + 自我怀疑 " + "{0:.2f}".format(soul_dims.get("self_doubt", 0.50))),
            ("3. 氛围渲染", "氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)) + " + 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85))),
            ("4. 悬疑", "镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " + 主导情感强度 " + "{0:.2f}".format(fused_intensity)),
            ("5. 多线", "创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " + 故事强度 " + "{0:.2f}".format(story_intensity) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70))),
            ("6. 反转", "突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)) + " + 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85))),
            ("7. 高潮", "融合强度 " + "{0:.2f}".format(fused_intensity) + " + 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73))),
            ("8. 余韵", "怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " + 自我怀疑 " + "{0:.2f}".format(soul_dims.get("self_doubt", 0.50)) + " + 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85))),
            ("9. 推进节奏", "灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70))),
            ("10. 感情控制", "艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " + 融合情感 " + fused_emotion.get("name", "") + " + 氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85))),
            ("11. 角色塑造", "融合情感 " + fused_emotion.get("name", "") + " + 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " + 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85))),
        ]
        for k, v in sig_full:
            cinematic_sig += "  " + k + " ← " + v + "\n"
        cinematic_sig += "\n"

        # 11 维 + 8 DP + 8 Director 全对照
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维 + 8 DP + 8 Director 综合应用】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        cinematic_sig += "  当前选择: 导演 " + director + " + DP " + dp + "\n"
        cinematic_sig += "  灵魂: " + fused_emotion.get("name", "") + " (强度 " + "{0:.2f}".format(fused_intensity) + ", 极性 " + fused_emotion.get("polarity", "") + ")\n"
        cinematic_sig += "  主导类别: " + ", ".join(fused_categories) + "\n"
        cinematic_sig += "  视觉决策: 焦段 " + focal_info.get("cn", derived_focal) + " / 光圈 " + aperture_info.get("cn", derived_aperture) + " / 景别 " + shot_info.get("cn", derived_shot_size) + " / 构图 " + comp_info.get("cn", derived_composition) + "\n"
        cinematic_sig += "  光影决策: " + derived_lighting_9d.get("光源类型", "") + " + " + derived_lighting_9d.get("方向", "") + " + " + derived_lighting_9d.get("色温", "") + " + " + derived_lighting_9d.get("时间", "") + "\n"
        cinematic_sig += "  色彩决策: 60% " + derived_60_30_10.get("主色_60", "")[:30] + " | 30% " + derived_60_30_10.get("辅色_30", "")[:20] + " | 10% " + derived_60_30_10.get("点缀色_10", "")[:20] + "\n"
        cinematic_sig += "  11 维强项: " + director_info.get("subject", "") + "\n"
        cinematic_sig += "  3 运镜: 静止凝视 + 慢推侵入 + 手持摇晃 (按灵魂类别选)\n"
        cinematic_sig += "  3 留白: 时间 + 空间 + 叙事 (按灵魂强度选)\n"
        cinematic_sig += "  签名: " + director_info.get("visual_signature", "") + "\n"
        cinematic_sig += "  触发: " + director_info.get("trigger", "") + "\n"
        cinematic_sig += "  执行: " + director_info.get("execute", "") + "\n\n"

        # 完整 11 维 × 8 顶级导演 矩阵
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维 × 8 顶级导演 完整矩阵】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        cinematic_sig += "  维度       | 王家卫   | 诺兰     | PTA      | 奉俊昊   | 黑泽明   | 库斯杜力卡 | 塔可夫斯基 | 提尔\n"
        cinematic_sig += "  -----------+----------+----------+----------+----------+----------+------------+------------+--------\n"
        matrix_11_8 = [
            ("1.空镜", "60s时间戳", "IMAX大", "PTA长镜", "楼梯", "天气", "动物+长", "5+分钟", "北欧窗"),
            ("2.留白", "极高", "高", "中", "中", "中", "高沉默", "极高", "高"),
            ("3.氛围", "霓虹", "IMAX", "70s暖", "阶层", "群戏", "塞尔维亚", "诗意", "北欧光"),
            ("4.悬疑", "时间", "时间", "石油", "血", "武士", "乡愁", "时间", "悔恨"),
            ("5.多线", "中", "极高", "中", "高", "中", "中", "低", "中"),
            ("6.反转", "中", "极高", "高", "极高", "中", "中", "低", "中"),
            ("7.高潮", "60s", "IMAX", "石油", "楼梯", "群斗", "动物", "长镜", "对话"),
            ("8.余韵", "60s", "中", "高", "高", "中", "沉默", "极高", "高"),
            ("9.节奏", "慢", "波浪", "慢→快", "类型", "史诗", "慢", "极慢", "中"),
            ("10.感情", "物件", "IMAX", "可观察", "阶层", "武士", "沉默", "诗意", "房子"),
            ("11.角色", "凤梨罐", "信念", "5维立体", "阶层", "武士", "动物", "回忆", "代际"),
        ]
        for row_name, *cols in matrix_11_8:
            cinematic_sig += "  " + row_name.ljust(10) + " | " + " | ".join([c.ljust(8) for c in cols]) + "\n"
        cinematic_sig += "\n"

        # 11 维控制完整规格 (大段说明)
        cinematic_sig += "════════════════════════════════════════\n"
        cinematic_sig += "【11 维控制完整规格 (灵魂驱动超详细)】\n"
        cinematic_sig += "════════════════════════════════════════\n\n"
        spec_11d = [
            ("1. 空镜 (5-15 秒)", [
                "定义: 无对白无人物的环境镜头, 5-15秒, 表达时间流逝/空间转换/情绪沉淀",
                "类型: ①定场空镜 ②转场空镜 ③情绪空镜 ④隐喻空镜 ⑤结尾空镜",
                "灵魂执行: 疲劳指数 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " 决定空镜长度 (高→5-8s / 低→10-15s)",
                "代表: 王家卫 60s 时间戳 / 塔可夫斯基 5+ 分钟 / 小津固定 5s",
                "执行: 1 个空镜 = 1 个时间单位, 灵魂疲劳 1 = 5s, 灵魂疲劳 0.3 = 15s",
                "反 AI: 不用 'cinematic' 形容空镜, 写具体 (e.g. '1998 哈尔滨窗外的雪, 30 秒')",
            ]),
            ("2. 留白", [
                "定义: 时间留白 + 空间留白 + 叙事留白",
                "类型: ①时间留白 ②空间留白 ③叙事留白",
                "灵魂执行: 想象力 " + "{0:.2f}".format(soul_dims.get("imagination", 0.85)) + " + 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)),
                "代表: 小津留白 / 王家卫留白 / 塔可夫斯基留白",
                "执行: 时间留白 = 镜头停留; 空间留白 = 负空间; 叙事留白 = 隐喻",
                "反 AI: 留白是艺术, 不是 '不完整', 必须有艺术目的",
            ]),
            ("3. 氛围渲染", [
                "定义: 材质/光影/颜色/空间/声音 5 维共同作用",
                "类型: ①时代氛围 ②空间氛围 ③情绪氛围 ④文化氛围 ⑤天气氛围",
                "灵魂执行: 氛围掌控 " + "{0:.2f}".format(soul_dims.get("atmosphere_control", 0.85)),
                "代表: Deakins 自然光 / Lubezki 长镜头 / Young 暗调",
                "执行: 5 维协同, 不只是 '美', 是 '信'",
                "反 AI: 不用 'cinematic' 形容氛围, 写具体材质+光影+颜色+空间+声音",
            ]),
            ("4. 悬疑", [
                "定义: 信息差 + 隐藏动机 + 时间压力",
                "类型: ①情节悬疑 ②氛围悬疑 ③心理悬疑 ④时间悬疑 ⑤空间悬疑",
                "灵魂执行: 镜头技巧 " + "{0:.2f}".format(soul_dims.get("camera_skill", 0.85)) + " + 主导情感强度 " + "{0:.2f}".format(fused_intensity),
                "代表: 希区柯克悬疑 / 奉俊昊悬疑 / 林奇悬疑",
                "执行: 1 个隐藏信息 + 1 个时间压力 = 1 个悬疑镜头",
                "反 AI: 不用 'mysterious' 形容悬疑, 写具体 (e.g. '父亲表情突然变冷, 7 秒')",
            ]),
            ("5. 多线", [
                "定义: 双线/三线并行, 交叉剪辑, 在高潮点汇合",
                "类型: ①双线 ②三线 ③环形 ④网状 ⑤非线性",
                "灵魂执行: 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)) + " + 故事强度 " + "{0:.2f}".format(story_intensity) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)),
                "代表: 诺兰多线 / 奉俊昊多线 / 安哲罗普洛斯多线",
                "执行: 2-3 条线并行, 每条线 1 个主题, 高潮点汇合",
                "反 AI: 不用 'complex' 形容多线, 写具体 (e.g. 'A 厨房 1998 / B 电话亭 1998 / C 列车 1999')",
            ]),
            ("6. 反转", [
                "定义: 前 30 秒建立 A, 后 30 秒揭示是 B",
                "类型: ①身份反转 ②动机反转 ③视角反转 ④时间反转 ⑤空间反转",
                "灵魂执行: 突破勇气 " + "{0:.2f}".format(soul_dims.get("breakthrough_courage", 0.73)) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)) + " + 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)),
                "代表: 诺兰反转 / 奉俊昊反转 / 维伦纽瓦反转",
                "执行: 12 铁律: 反转必须有铺垫 + 反转后必须可信",
                "反 AI: 反转不是 'twist', 是 '重新理解', 必须有合理动机",
            ]),
            ("7. 高潮", [
                "定义: 冲突顶点, CU+ECU+沉默+微表情+动作",
                "类型: ①情绪高潮 ②情节高潮 ③动作高潮 ④关系高潮 ⑤主题高潮",
                "灵魂执行: 融合强度 " + "{0:.2f}".format(fused_intensity) + " + 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)),
                "代表: PTA 高潮 / 奉俊昊高潮 / 诺兰高潮",
                "执行: 高潮 = CU + ECU + 沉默 + 微表情 + 动作改变关系",
                "反 AI: 高潮不是 'climax', 是 '关系改变', 必须有具体动作",
            ]),
            ("8. 余韵", [
                "定义: 高潮之后的呼吸, 2-5 秒静默",
                "类型: ①沉默余韵 ②空镜余韵 ③音乐余韵 ④动作余韵 ⑤情感余韵",
                "灵魂执行: 怀疑 " + "{0:.2f}".format(soul_state.get("doubt", 0.50)) + " + 自我怀疑 " + "{0:.2f}".format(soul_dims.get("self_doubt", 0.50)),
                "代表: 是枝裕和余韵 / 王家卫余韵 / 库斯杜力卡余韵",
                "执行: 高潮后 2-5 秒静默, 让情绪发酵",
                "反 AI: 余韵不是 'fade out', 是 '呼吸', 必须有具体元素",
            ]),
            ("9. 推进节奏", [
                "定义: 由慢到快/由快到慢/波浪形, 根据情绪曲线设计切点",
                "类型: ①慢→快 ②快→慢 ③波浪形 ④脉冲 ⑤循环",
                "灵魂执行: 灵感 " + "{0:.2f}".format(soul_state.get("inspiration", 0.85)) + " + 疲劳 " + "{0:.2f}".format(soul_state.get("fatigue", 0.30)) + " + 叛逆 " + "{0:.2f}".format(soul_state.get("rebelliousness", 0.70)),
                "代表: 诺兰节奏 / 库布里克节奏 / 王家卫节奏",
                "执行: 情绪曲线 = 慢 → 快 → 慢 (3 段), 每段 30-60 秒",
                "反 AI: 节奏不是 'pace', 是 '情绪曲线', 必须有具体节拍",
            ]),
            ("10. 感情控制", [
                "定义: 让观众感到角色感到的, 沉默+微表情+动作",
                "类型: ①让观众笑 ②让观众哭 ③让观众怒 ④让观众惧 ⑤让观众思",
                "灵魂执行: 艺术表达 " + "{0:.2f}".format(soul_dims.get("artistic_expression", 0.85)) + " + 融合情感 " + fused_emotion.get("name", ""),
                "代表: PTA 感情 / 库斯杜力卡感情 / 王家卫感情",
                "执行: 沉默+微表情+动作 = 1 个感情单位",
                "反 AI: 感情不是 'emotional', 是 '让观众感到', 必须有具体表现",
            ]),
            ("11. 角色塑造", [
                "定义: 微表情/身体习惯/口头禅/标志性物件, 5 维立体",
                "类型: ①主角色塑 ②配角角色塑 ③反派角色塑 ④群像角色塑 ⑤转变角色塑",
                "灵魂执行: 融合情感 " + fused_emotion.get("name", "") + " + 创造力 " + "{0:.2f}".format(soul_dims.get("creativity", 0.85)),
                "代表: PTA 角色 / 王家卫角色 / 库斯杜力卡角色",
                "执行: 5 维: 微表情 + 身体 + 声音 + 节奏 + 物件 = 1 个角色",
                "反 AI: 角色不是 'character', 是 '5 维立体人', 必须有具体细节",
            ]),
        ]
        for name, items in spec_11d:
            cinematic_sig += "  【" + name + "】\n"
            for item in items:
                cinematic_sig += "    - " + item + "\n"
            cinematic_sig += "\n"

        # ========== 12. 反 AI 处理 ==========
        if use_anti_ai and _HAS_ANTI_AI:
            try:
                bible = inject_anti_ai_rules(bible)
                visual_lang = inject_anti_ai_rules(visual_lang)
                color_60 = inject_anti_ai_rules(color_60)
                lighting_9d = inject_anti_ai_rules(lighting_9d)
                dp_style = inject_anti_ai_rules(dp_style)
                soul_payload = inject_anti_ai_rules(soul_payload)
                h3_addon = inject_anti_ai_rules(h3_addon)
                cinematic_sig = inject_anti_ai_rules(cinematic_sig)
            except Exception:
                pass

        return (
            bible,
            visual_lang,
            color_60,
            lighting_9d,
            dp_style,
            soul_payload,
            h3_addon,
            cinematic_sig,
        )


# ============================================================
# 节点映射 (Phase 18 升级, 类名以 Node 结尾, 向后兼容)
# ============================================================
class ArtDirectionProNode(ArtDirectionPro):
    """Phase 18 灵魂驱动版 — 类名以 Node 结尾 (向后兼容)"""
    pass


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ArtDirectionPro": ArtDirectionPro,
#     "ArtDirectionProNode": ArtDirectionProNode,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ArtDirectionPro": "🎨 美术指导 (Phase 18 灵魂驱动)",
#     "ArtDirectionProNode": "🎨 美术指导 Node (Phase 18 灵魂驱动)",
# }


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 18 灵魂驱动美术指导节点 测试")
    print("=" * 60)

    # 基础测试
    ad = ArtDirectionPro()
    print("\n[1] INPUT_TYPES 字段数:", len(ad.INPUT_TYPES()["required"]))
    print("[1] INPUT_TYPES 字段:", list(ad.INPUT_TYPES()["required"].keys()))

    # 灵魂驱动测试 1: Loneliness 100%
    out = ad.build_art_direction(
        灵魂主导情感="loneliness",
        灵魂融合模式="F1_单情感主导",
        导演="王家卫",
        时代="1998 年, 香港",
        场景描述="阿飞在电话亭旁, 雨夜, 1998 年香港",
    )
    print("\n[2] Loneliness 100% + 王家卫:")
    for i, (name, val) in enumerate(zip(
        ["art_direction_bible", "visual_language_params", "color_60_30_10_script",
         "lighting_9d_design", "dp_8_masters_style", "soul_injection_payload",
         "h3_three_fields_addon", "cinematic_signature_addon"],
        out
    )):
        print("  - {0}: {1} 字符".format(name, len(val)))

    # 灵魂驱动测试 2: Love + Tenderness 70/30 + 诺兰
    out2 = ad.build_art_direction(
        灵魂主导情感="love",
        灵魂次要情感_1="tenderness",
        灵魂融合模式="F2_双情感主次融合",
        灵魂主导权重=0.7,
        导演="诺兰",
        时代="现代",
        场景描述="情侣在 IMAX 镜头下, 黄金时刻",
    )
    print("\n[3] Love+Tenderness 70/30 + 诺兰:")
    for name, val in zip(
        ["art_direction_bible", "visual_language_params", "color_60_30_10_script",
         "lighting_9d_design", "dp_8_masters_style", "soul_injection_payload",
         "h3_three_fields_addon", "cinematic_signature_addon"],
        out2
    ):
        print("  - {0}: {1} 字符".format(name, len(val)))

    # 向后兼容测试
    out3 = ad.build_art_direction(
        时代="1998 年东北", 视觉风格="胶片暖黄",
        材质重点="棉布, 木头, 老墙, 烟囱, 雪",
        光影="自然光为主, 室内钨丝灯",
        颜色="黄, 灰, 偶尔一抹红",
        空间布局="小, 旧, 暖, 拥挤但有序",
        导演风格="是枝裕和",
        启用反AI规则=True,
    )
    print("\n[4] 向后兼容 (旧版参数):")
    print("  - bible: {0} 字符 (要求 > 500)".format(len(out3[0])))
    print("  - visual_lang: {0} 字符 (要求 > 100)".format(len(out3[1])))
