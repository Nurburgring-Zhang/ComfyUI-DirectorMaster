# -*- coding: utf-8 -*-
"""
Phase 14 - Cinematic Studio 电影效果 + 多模型路由 — Phase 15 视觉语言专家重做
================================================================================
环节 能力四 视觉语言力 — Phase 15 深度重做

Phase 15 核心强化:
1. 23 个电影特效 (Higgsfield Effects) + 视觉语言参数化
2. 12+ 模型路由 (Seedance/Kling/Wan/Veo/Sora/Hailuo/Grok/...)
3. 视觉语言参数化 (焦段/光圈/景别/构图)
4. 60:30:10 色彩法则
5. 9 维光影设计
6. 8 大顶级摄影指导风格库
7. L1-L7 七层 prompt 架构
8. 5 要素架构
9. 11 维导演控制能力
10. 3 种留白 + 3 运镜法则
11. 模型弱点库 (每个模型怕什么)
12. 一致性工作流 (character sheet + consistent_video)
"""

import os
import sys

try:
    from anti_ai_vocab import clean_anti_ai_text, inject_anti_ai_rules
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, H3_RULES_11, DIRECTOR_CONTROL_11,
        build_h3_three_fields, inject_director_control_11,
        inject_anti_ai_rules as inject_anti_ai_pb,
    )
    from asset_registry_data import ASSET_REGISTRY
    from style_prefix_data import STYLE_PREFIX
    _HAS_DEPS = True
except Exception as e:
    _HAS_DEPS = False
    _DEPS_ERROR = str(e)


# ============================================================
# 23 电影特效 (Higgsfield Effects 完整复刻)
# ============================================================
CINEMATIC_EFFECTS_23 = {
    "venom_symbiote": {"name": "毒液附体", "duration": "5-10s", "models": ["Seedance 2.5", "Kling 2.5", "Veo 3.1"]},
    "medusa_petrify": {"name": "美杜莎石化", "duration": "3-8s", "models": ["Seedance 2.5", "Wan 2.6"]},
    "slow_motion_bullet": {"name": "子弹时间慢动作", "duration": "5-15s", "models": ["Hailuo 02", "Kling 3.0", "Veo 3.1"]},
    "teleportation": {"name": "瞬移特效", "duration": "2-5s", "models": ["Wan 2.6", "Sora 2"]},
    "fire_burst": {"name": "火焰爆发", "duration": "3-8s", "models": ["Kling 2.5", "Hailuo 02"]},
    "water_explosion": {"name": "水花爆裂", "duration": "3-8s", "models": ["Seedance 2.5", "Hailuo 02"]},
    "smoke_formation": {"name": "烟雾化形", "duration": "5-15s", "models": ["Wan 2.6", "Veo 3.1"]},
    "shadow_morph": {"name": "暗影变形", "duration": "5-12s", "models": ["Sora 2", "Kling 3.0"]},
    "levitation": {"name": "悬浮术", "duration": "3-10s", "models": ["Seedance 2.5", "Wan 2.6"]},
    "double_exposure": {"name": "双重曝光", "duration": "5-15s", "models": ["Veo 3.1", "Sora 2"]},
    "lightning_strike": {"name": "闪电击中", "duration": "2-5s", "models": ["Kling 2.5", "Hailuo 02"]},
    "energy_blast": {"name": "能量冲击波", "duration": "3-8s", "models": ["Seedance 2.5", "Veo 3.1"]},
    "wind_blast": {"name": "狂风冲击", "duration": "3-8s", "models": ["Kling 2.5", "Wan 2.6"]},
    "ice_freeze": {"name": "冰冻凝固", "duration": "3-8s", "models": ["Seedance 2.5", "Hailuo 02"]},
    "acid_splash": {"name": "酸液飞溅", "duration": "3-8s", "models": ["Kling 2.5", "Wan 2.6"]},
    "portal_open": {"name": "传送门开启", "duration": "5-12s", "models": ["Sora 2", "Veo 3.1"]},
    "ghost_appear": {"name": "幽灵显形", "duration": "5-12s", "models": ["Wan 2.6", "Sora 2"]},
    "transformation": {"name": "变身特效", "duration": "8-20s", "models": ["Seedance 2.5", "Kling 3.0"]},
    "matrix_dodge": {"name": "子弹时间闪避", "duration": "5-15s", "models": ["Hailuo 02", "Veo 3.1"]},
    "force_push": {"name": "原力推动", "duration": "3-8s", "models": ["Kling 2.5", "Seedance 2.5"]},
    "earth_quake": {"name": "地震特效", "duration": "5-15s", "models": ["Wan 2.6", "Hailuo 02"]},
    "soul_extraction": {"name": "灵魂抽离", "duration": "5-15s", "models": ["Veo 3.1", "Sora 2"]},
    "void_rift": {"name": "虚空裂缝", "duration": "3-10s", "models": ["Sora 2", "Wan 2.6"]},
}


# ============================================================
# 12 模型路由 (Cinema Studio 完整复刻)
# ============================================================
MODEL_REGISTRY = {
    "Seedance 2.5": {
        "provider": "字节跳动火山引擎",
        "max_duration": 30,
        "max_references": 50,
        "price": "$0.60/秒 (720p), $0.30/秒 (480p)",
        "weaknesses": ["复杂多人交互", "长时长 (但 30s 突破)"],
        "strengths": ["30s 单条", "50 参考", "局部编辑", "3D 白模", "多语言"],
        "best_for": "短剧/广告/科普",
    },
    "Kling 2.5": {
        "provider": "快手可灵",
        "max_duration": 10,
        "max_references": 4,
        "price": "$0.30/秒",
        "weaknesses": ["手指", "复杂动作"],
        "strengths": ["动作流畅", "中文友好"],
        "best_for": "武侠/动作/舞蹈",
    },
    "Kling 3.0": {
        "provider": "快手可灵",
        "max_duration": 15,
        "max_references": 6,
        "price": "$0.50/秒",
        "weaknesses": ["超长时长"],
        "strengths": ["1080p 高清", "运动稳定"],
        "best_for": "广告/高端短片",
    },
    "Veo 3.1": {
        "provider": "Google",
        "max_duration": 8,
        "max_references": 3,
        "price": "$0.40/秒",
        "weaknesses": ["中文 prompt"],
        "strengths": ["物理真实", "光照"],
        "best_for": "电影感/物理",
    },
    "Sora 2": {
        "provider": "OpenAI",
        "max_duration": 20,
        "max_references": 4,
        "price": "$0.50/秒",
        "weaknesses": ["手部", "中文"],
        "strengths": ["叙事", "电影感"],
        "best_for": "剧情/故事",
    },
    "Wan 2.6": {
        "provider": "阿里通义万相",
        "max_duration": 15,
        "max_references": 5,
        "price": "$0.30/秒",
        "weaknesses": ["英文 prompt"],
        "strengths": ["中文理解", "复杂场景"],
        "best_for": "中国风/古风",
    },
    "Hailuo 02": {
        "provider": "MiniMax海螺",
        "max_duration": 6,
        "max_references": 2,
        "price": "$0.20/秒",
        "weaknesses": ["时长短"],
        "strengths": ["物理真实", "人体"],
        "best_for": "舞蹈/动作",
    },
    "Grok Imagine 1.5": {
        "provider": "xAI",
        "max_duration": 10,
        "max_references": 3,
        "price": "$0.30/秒",
        "weaknesses": ["中文"],
        "strengths": ["幽默/广告"],
        "best_for": "广告/幽默",
    },
    "Gemini Omni Flash": {
        "provider": "Google",
        "max_duration": 10,
        "max_references": 3,
        "price": "$0.35/秒",
        "weaknesses": ["角色一致性"],
        "strengths": ["多模态", "速度"],
        "best_for": "原型/快速",
    },
    "Seedance 2.0": {
        "provider": "字节跳动",
        "max_duration": 15,
        "max_references": 12,
        "price": "$0.40/秒 (原生 4K 升级)",
        "weaknesses": ["新功能不全面"],
        "strengths": ["4K 原生", "稳定"],
        "best_for": "标准 4K 输出",
    },
}


# ============================================================
# Phase 15 新增: 8 大顶级摄影指导风格库
# ============================================================
DP_8_MASTERS = {
    "罗杰·迪金斯_Roger_Deakins": {
        "signature": "自然光 + 隐喻构图 + 极简",
        "key_films": ["《银翼杀手2049》", "《1917》", "《007: 大破天幕杀机》", "《老无所依》"],
        "lighting": "全场景动机光, 一个光源逻辑贯穿全场",
        "composition": "极简, 大面积负空间, 主体小, 隐喻构图",
        "color": "高对比, 暖黄 + 冷蓝, 60:30:10 严格执行",
        "lens": "35mm / 50mm 为主, 极少广角",
        "trigger": "自然/纪实/克制/有思想深度的现代电影",
        "execute": "用单一自然光逻辑, 拒绝过度布光, 大面积留白, 主体被环境包裹",
    },
    "卢贝兹基_Emmanuel_Lubezki": {
        "signature": "长镜头 + 自然光 + 流动时间",
        "key_films": ["《鸟人》", "《地心引力》", "《荒野猎人》", "《生命之树》"],
        "lighting": "全自然光, 几乎不补光, 用现场光讲故事",
        "composition": "长镜头内部调度, 一镜到底",
        "color": "高饱和高反差, 黄金时刻为多",
        "lens": "广角 18-27mm 居多, 容纳长镜头的空间",
        "trigger": "时间流动/生命史诗/精神世界/亲密长镜头",
        "execute": "一镜到底长镜头, 自然光现场, 广角容纳整个场景, 跟着人物时间流动",
    },
    "杜可风_Christopher_Doyle": {
        "signature": "港式霓虹 + 手持 + 高饱和",
        "key_films": ["《重庆森林》", "《花样年华》(部分)", "《春光乍泄》", "《东邪西毒》"],
        "lighting": "霓虹为主, 雨水+霓虹=标志, 手持灯光创造色块",
        "composition": "失焦/畸变/手持摇晃, 故意不完美",
        "color": "高饱和, 红绿蓝黄, 浓烈情绪色",
        "lens": "14mm 广角畸变, 50mm 失焦",
        "trigger": "都市孤独/暧昧/边缘/醉意",
        "execute": "霓虹+雨水+广角畸变+手持, 故意打破完美构图, 制造眩晕感",
    },
    "沃伊切赫·斯泽尔曼_Wojciech": {
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
        "signature": "暗调 + 心理 + 极端虚化",
        "key_films": ["《掠食城市》", "《塞尔玛》", "《到达》", "《黑夜造访》"],
        "lighting": "极弱光, 高反差, 大部分场景几乎全黑, 微弱光源",
        "composition": "特写为主, 极端虚化 T1.4, 极浅景深",
        "color": "肤色+单点强调色, 几乎单色调",
        "lens": "85mm 大量使用, 浅景深",
        "trigger": "心理/压迫/梦境/非裔美国历史",
        "execute": "极弱光, T1.4 浅景深, 几乎全黑背景, 主体皮肤被微弱光照亮, 心理压迫",
    },
    "贾努兹·卡明斯基_Janusz_Kaminski": {
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
        "signature": "色彩光影 + 60:30:10 严格执行",
        "key_films": ["《现代启示录》", "《末代皇帝》", "《蓝色大门》", "《查理四世》"],
        "lighting": "色彩光影, 用光色讲故事, 每场戏有色彩主题",
        "composition": "中心对称 + 黄金比例, 古典",
        "color": "60:30:10 严格, 色彩叙事, 时代色",
        "lens": "50mm 为主, 古典",
        "trigger": "色彩叙事/历史/政治/史诗",
        "execute": "每场戏设定主色+辅色+点缀色, 60:30:10 严格执行, 用色彩讲时代/政治/心理",
    },
    "霍伊特·范·霍特玛_Hoyte_van_Hoytema": {
        "signature": "自然光 + 宽幅 + 65mm",
        "key_films": ["《敦刻尔克》", "《她》", "《星际穿越》", "《007: 幽灵党》"],
        "lighting": "全自然光, 现场光, 65mm 大画幅",
        "composition": "宽幅 2.20:1, 大量横向负空间",
        "color": "自然饱和度, 不刻意调色",
        "lens": "65mm 大画幅, 自然透视",
        "trigger": "现代史诗/科幻/真实/宽幅",
        "execute": "65mm IMAX 拍摄, 2.20:1 宽幅, 全自然光, 大面积横向负空间, 真实质感",
    },
}

DP_8_NAMES = list(DP_8_MASTERS.keys())


# ============================================================
# Phase 15 新增: 视觉语言参数化 (焦段/光圈/景别/构图)
# ============================================================
FOCAL_LENGTH_VL = {
    "14mm_ultra_wide": {"cn": "14mm 广角", "emotion": "压迫、怪诞", "narrative": "心理压迫/超现实", "masters": "杜可风《重庆森林》"},
    "24mm_wide": {"cn": "24mm 广角", "emotion": "纪实、不稳定", "narrative": "街拍/纪实", "masters": "王家卫/贾樟柯"},
    "35mm_cinematic": {"cn": "35mm 电影标准", "emotion": "自然、平衡", "narrative": "叙事主力", "masters": "迪金斯/塔可夫斯基/侯孝贤"},
    "50mm_eye": {"cn": "50mm 人眼", "emotion": "亲密、自然", "narrative": "对话/亲密", "masters": "小津/斯托拉罗/是枝裕和"},
    "85mm_portrait": {"cn": "85mm 肖像", "emotion": "浪漫、孤立", "narrative": "情感特写", "masters": "杨/李安/王家卫"},
    "135mm_compression": {"cn": "135mm+ 长焦", "emotion": "孤独、监视", "narrative": "远距离/超现实", "masters": "范·霍特玛/安东尼奥尼/塔可夫斯基"},
}
APERTURE_VL = {
    "T1.4_T2_extreme": {"cn": "T1.4-T2 极浅景深", "trigger": "梦幻/极致虚化", "masters": "杨/王家卫"},
    "T2.8_cinematic": {"cn": "T2.8 电影浅景深", "trigger": "人物特写", "masters": "迪金斯/李安"},
    "T4_mid": {"cn": "T4 中景深", "trigger": "对话场景", "masters": "小津/是枝裕和"},
    "T8_deep": {"cn": "T8 全景深", "trigger": "环境展示", "masters": "贾樟柯"},
}
SHOT_SIZE_VL = {
    "ELS": "远景 - 人物<10%, 环境为主, 5-15秒, 塔可夫斯基/《阿拉伯的劳伦斯》",
    "LS": "全景 - 人物 15-30%, 4-10秒, 《肖申克》/《教父》",
    "MLS": "中全景 - 人物 30-50%, 3-8秒, 侯孝贤/是枝裕和",
    "MS": "中景 - 人物 40-60%, 2-6秒, 《低俗小说》/《花样年华》",
    "MCU": "中近景 - 人物 50-70%, 2-5秒, 《沉默的羔羊》/《闻香识女人》",
    "CU": "近景 - 面部 60%+, 1-4秒, 《教父》/《这个杀手不太冷》",
    "ECU": "特写 - 局部 80%+, 0.5-3秒, 《2001太空漫游》/《黑天鹅》",
    "ECU_PLUS": "大特写 - 微距 0.5-2秒, 《教父》/《肖申克》/《寄生虫》",
}
COMPOSITION_RULES = {
    "rule_of_thirds": "三分法 - 经典平衡, 通用",
    "golden_ratio": "黄金比例 - 自然美感, 《教父》《2001太空漫游》",
    "symmetry": "对称构图 - 权力/仪式, 库布里克/卡明斯基",
    "leading_lines": "引导线 - 视线引导, 迪金斯/范·霍特玛",
    "frame_in_frame": "框中框 - 隔离/窥视, 王家卫/库布里克",
    "negative_space": "留白 - 呼吸/孤独, 贾樟柯/是枝裕和/小津",
    "low_key": "暗调高反差 - 悬疑/黑色电影, 杨/斯泽尔曼",
}


# ============================================================
# Phase 15 新增: 60:30:10 色彩心理学
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


# ============================================================
# Phase 15 新增: 9 维光影
# ============================================================
LIGHTING_9D_PHASE15 = {
    "1_光源类型": ["自然光 (太阳)", "火光 (蜡烛/壁炉)", "霓虹 (城市)", "路灯", "白炽灯", "荧光灯", "LED 屏幕", "手电筒", "月光", "混合光"],
    "2_方向": ["顺光", "侧光", "逆光", "顶光", "底光", "45度_伦勃朗光"],
    "3_强度": ["强光", "中光", "弱光"],
    "4_色温": ["warm_3200K", "neutral_5500K", "cool_6500K", "blue_hour_8000K"],
    "5_软硬": ["硬光", "软光", "极软光"],
    "6_比例": ["高调_2_1", "中间调_4_1", "低调_8_1"],
    "7_阴影": ["长阴影", "短阴影", "无阴影"],
    "8_特殊光影": ["丁达尔效应", "剪影", "伦勃朗光", "蝴蝶光", "轮廓光"],
    "9_时间": ["正午", "黄昏", "黄金时刻", "蓝色时刻", "夜晚"],
}


# ============================================================
# 模型路由函数
# ============================================================
def route_model(effect, scene, duration, language="zh"):
    """根据特效/场景/时长/语言, 推荐最优模型组合"""
    seen = set()
    candidates = []
    if effect in CINEMATIC_EFFECTS_23:
        eff = CINEMATIC_EFFECTS_23[effect]
        for m in eff.get("models", []):
            if m in MODEL_REGISTRY and m not in seen:
                seen.add(m)
                candidates.append((m, MODEL_REGISTRY[m]))

    candidates = [(m, s) for m, s in candidates if s["max_duration"] >= duration]

    if language == "zh":
        candidates = [(m, s) for m, s in candidates if "中文" in s["strengths"] or m in ["Seedance 2.5", "Wan 2.6", "Hailuo 02", "Kling 2.5", "Kling 3.0"]]

    if not candidates:
        candidates.append(("Seedance 2.5", MODEL_REGISTRY["Seedance 2.5"]))

    candidates.sort(key=lambda x: float(x[1]["price"].split("$")[1].split("/")[0]))
    return [m for m, s in candidates[:3]]


# ============================================================
# 角色一致性工作流 (Seedance Character + consistent_video)
# ============================================================
def build_character_consistency_workflow(
    reference_image_url="https://example.com/person.jpg",
    outfit_description="赛博朋克夹克配霓虹面罩",
    character_name="ROCO",
):
    """Seedance 2.5 Character 一致性工作流"""
    return """════════════════════════════════════════
【角色一致性工作流 (Seedance 2.5 Character + consistent_video)】
════════════════════════════════════════

Step 1: 创建角色表 (create_character)
- POST https://api.muapi.ai/api/v1/seedance-2-character
- Body: {
    "images_list": ["%s"],
    "prompt": "%s"
  }
- 输出: 4K/21:9 角色表 (前/后/侧/动作/表情)
- 价格: $0.18/角色表
- 角色名: %s

Step 2: 锚定一致视频 (consistent_video)
- POST https://api.muapi.ai/api/v1/seedance-2.5-omni-reference
- Body: {
    "prompt": "The character %s rides a motorcycle through a neon-lit city at night",
    "sheet_url": "<Step 1 输出的角色表 URL>",
    "aspect_ratio": "16:9",
    "duration": 5
  }
- 输出: 角色身份锁定的视频
- 价格: $0.72/秒 (720p)

Step 3: 多场景扩展
- 同一 sheet_url 可重复使用
- 每次换 prompt 即可, 角色身份保持一致
- 适合短剧/广告/角色系列内容

════════════════════════════════════════
【3D 白模工作流 (Seedance 2.5 新功能)】
════════════════════════════════════════

Step 1: 在 Maya/Blender 搭建白模
Step 2: 导出 3D 路径 + 渲染参考
Step 3: 喂给 Seedance 2.5
- 适合: 复杂长镜头/空间调度
- 例: 飞船主体 10 万面 + 渲染材质参考 → 30s 推镜视频
- 例: 男女主 3D 站位 + 摄影机轨迹 → 镜头一动空间不崩

════════════════════════════════════════
【11 阶段制作管线 (Higgsfield Filmmaking Course)】
════════════════════════════════════════

1. Name your assets       - 资产命名
2. Generating locations   - 生成场景
3. Generating characters  - 生成角色
4. Test in Seedance       - 在 Seedance 测试
5. Shoot the scene        - 拍摄场景
6. Soundscape             - 声音设计
7. Music                  - 音乐配乐
8. Cut                    - 剪辑
9. Color                  - 调色
10. VFX                    - 视觉特效
11. QA                     - 质量检查

════════════════════════════════════════
【6 份核心文件 (Higgsfield 6 Documents 项目级记忆)】
════════════════════════════════════════

1. ASSET_REGISTRY  - 资产注册表 (角色/地点/道具)
2. SCENE_MAP       - 场景地图 (固定地标/180° axis)
3. ACTING_STATE    - 表演状态 (5 支柱)
4. SHOTLIST        - 分镜表
5. VERSION_LOG     - 版本日志
6. POST_ISSUE_LIST - 后期问题单

════════════════════════════════════════
【5 大创作铁律】
════════════════════════════════════════

1. 资产先行 (省的钱比其他所有规则加起来还多)
2. 每次描述全部 (descriptor 逐字进每个 prompt)
3. 一次只改一行 (整段重写会丢 work)
4. 给模型更少的自由 (角落而不是房间)
5. 镜头搞不定就简化 (拆/删/换)
""" % (reference_image_url, outfit_description, character_name, character_name)


# ============================================================
# ComfyUI 节点
# ============================================================
class CinematicStudio:
    """Phase 14 - Cinematic Studio 电影效果 + 多模型路由 + 视觉语言专家重做"""

    CATEGORY = "PromptLibrary/Phase14 电影"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "effects_23_overview",         # 23 特效概览
        "visual_language_params",      # 视觉语言参数化 (Phase 15 核心)
        "color_60_30_10_script",       # 60:30:10 色彩法则 (Phase 15 核心)
        "lighting_9d_design",          # 9 维光影设计 (Phase 15 核心)
        "dp_8_masters_style",          # 8 大摄影指导风格 (Phase 15 核心)
        "selected_model",              # 推荐模型
        "model_weakness_avoidance",    # 模型弱点规避
        "character_consistency_workflow",  # 角色一致性
        "11_stage_pipeline",           # 11 阶段管线
        "h3_prompt",                   # H3 prompt
    )
    FUNCTION = "build"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "特效类型": (list(CINEMATIC_EFFECTS_23.keys()) + ["自定义..."], {"default": "venom_symbiote"}),
                "场景描述": ("STRING", {"default": "赛博朋克城市夜晚, 主角获得超能力", "multiline": True}),
                "时长_秒": ("INT", {"default": 5, "min": 1, "max": 30, "step": 1}),
                "语言": (["zh", "en"], {"default": "zh"}),
                "参考图片URL": ("STRING", {"default": "https://example.com/person.jpg", "multiline": False}),
                "服装描述": ("STRING", {"default": "赛博朋克夹克配霓虹面罩, 残破牛仔裤", "multiline": True}),
                "角色名": ("STRING", {"default": "ROCO", "multiline": False}),
                "导演风格": (["塔可夫斯基", "王家卫", "诺兰", "是枝裕和", "侯孝贤", "李沧东", "奉俊昊", "贾樟柯", "周星驰"], {"default": "诺兰"}),

                # Phase 15 新增: 8 大摄影指导
                "摄影指导": (DP_8_NAMES, {"default": "罗杰·迪金斯_Roger_Deakins"}),

                # Phase 15 新增: 视觉语言参数化
                "焦段": (list(FOCAL_LENGTH_VL.keys()), {"default": "35mm_cinematic"}),
                "光圈": (list(APERTURE_VL.keys()), {"default": "T2.8_cinematic"}),
                "景别": (list(SHOT_SIZE_VL.keys()), {"default": "MS"}),
                "构图法则": (list(COMPOSITION_RULES.keys()), {"default": "rule_of_thirds"}),

                # Phase 15 新增: 60:30:10
                "主色_60": ("STRING", {"default": "冷蓝 #1A2B3C (主色 60% — 赛博朋克冷色)"}),
                "辅色_30": ("STRING", {"default": "霓虹紫 #9D4EDD (辅色 30% — 城市霓虹)"}),
                "点缀色_10": ("STRING", {"default": "毒液红 #FF003D (点缀色 10% — 戏剧时刻)"}),

                # Phase 15 新增: 9 维光影
                "光源类型": (LIGHTING_9D_PHASE15["1_光源类型"], {"default": "霓虹 (城市)"}),
                "光影方向": (LIGHTING_9D_PHASE15["2_方向"], {"default": "侧光"}),
                "色温": (LIGHTING_9D_PHASE15["4_色温"], {"default": "cool_6500K"}),
                "比例": (LIGHTING_9D_PHASE15["6_比例"], {"default": "低调_8_1"}),
                "时间": (LIGHTING_9D_PHASE15["9_时间"], {"default": "夜晚"}),

                "启用反AI": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # === Phase 36.6 v5f: 4 路起点注入 (接收 DirectorMasteryNode 或起点节点的输出) ===
                "灵魂注入": ("STRING", {"default": "", "multiline": True, "tooltip": "来自 DirectorMasteryNode.output[0] 灵魂注入_整合 (60 情感 + 10 维度)"}),
                "审美注入": ("STRING", {"default": "", "multiline": True, "tooltip": "来自 AestheticJudgmentPro.output[0] 审美判断 (8 原则)"}),
                "风格注入": ("STRING", {"default": "", "multiline": True, "tooltip": "来自 StyleGuidePro.output[0] 风格指南 (5 调色)"}),
                "导演意图": ("STRING", {"default": "", "multiline": True, "tooltip": "来自 DirectorIntentPro.output[0] 意图声明 (4 类意图)"}),
            },
        }

    def build(self, 特效类型, 场景描述, 时长_秒, 语言, 参考图片URL, 服装描述, 角色名, 导演风格,
              摄影指导, 焦段, 光圈, 景别, 构图法则, 主色_60, 辅色_30, 点缀色_10,
              光源类型, 光影方向, 色温, 比例, 时间, 启用反AI,
              灵魂注入="", 审美注入="", 风格注入="", 导演意图="", **kwargs):

        def _str(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        # 取视觉语言参数
        focal_info = FOCAL_LENGTH_VL.get(焦段, {})
        aperture_info = APERTURE_VL.get(光圈, {})
        shot_info = SHOT_SIZE_VL.get(景别, "")
        comp_info = COMPOSITION_RULES.get(构图法则, "")
        dp_info = DP_8_MASTERS.get(摄影指导, {})

        # 23 特效概览
        if 特效类型 in CINEMATIC_EFFECTS_23:
            eff = CINEMATIC_EFFECTS_23[特效类型]
            effects_overview = "特效: " + 特效类型 + " (" + eff['name'] + ")\n"
            effects_overview += "推荐时长: " + eff['duration'] + "\n"
            effects_overview += "推荐模型: " + ", ".join(eff['models']) + "\n"
            effects_overview += "DP 风格叠加: " + 摄影指导 + " — " + dp_info.get("signature", "") + "\n"
        else:
            effects_overview = "特效: " + 特效类型 + " (自定义)"

        # ========== Phase 15 核心: 视觉语言参数化 (≥ 2000 字符) ==========
        visual_lang = "════════════════════════════════════════\n"
        visual_lang += "【视觉语言参数化系统】Phase 15 核心 — 能力四 视觉语言力\n"
        visual_lang += "════════════════════════════════════════\n\n"
        visual_lang += "顶级摄影指导: 用构图传递演员情绪/场景氛围, 创造视觉象征与暗示\n"
        visual_lang += "(AIGC 影视全流程解析 § 能力四 视觉语言力)\n"
        visual_lang += "摄影指导选择: " + 摄影指导 + " — " + dp_info.get("signature", "") + "\n\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "A. 焦段 × 情感映射 (选: " + focal_info.get("cn", 焦段) + ")\n"
        visual_lang += "─" * 50 + "\n"
        visual_lang += "情绪: " + focal_info.get("emotion", "") + "\n"
        visual_lang += "叙事: " + focal_info.get("narrative", "") + "\n"
        visual_lang += "代表: " + focal_info.get("masters", "") + "\n\n"

        visual_lang += "焦段速查 (6 焦段):\n"
        for k, v in FOCAL_LENGTH_VL.items():
            visual_lang += "  - " + v.get("cn", k) + ": " + v.get("emotion", "") + " — " + v.get("narrative", "") + " (代表: " + v.get("masters", "") + ")\n"
        visual_lang += "\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "B. 光圈 × 景深映射 (选: " + aperture_info.get("cn", 光圈) + ")\n"
        visual_lang += "─" * 50 + "\n"
        visual_lang += "触发: " + aperture_info.get("trigger", "") + "\n"
        visual_lang += "代表 DP: " + aperture_info.get("masters", "") + "\n\n"

        visual_lang += "光圈速查 (4 档):\n"
        for k, v in APERTURE_VL.items():
            visual_lang += "  - " + v.get("cn", k) + ": " + v.get("trigger", "") + " (代表: " + v.get("masters", "") + ")\n"
        visual_lang += "\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "C. 景别 × 叙事功能 (选: " + shot_info + ")\n"
        visual_lang += "─" * 50 + "\n"
        for k, v in SHOT_SIZE_VL.items():
            visual_lang += "  - " + k + ": " + v + "\n"
        visual_lang += "\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "D. 7 大构图法则 (选: " + comp_info + ")\n"
        visual_lang += "─" * 50 + "\n"
        for k, v in COMPOSITION_RULES.items():
            visual_lang += "  - " + v + "\n"
        visual_lang += "\n"

        visual_lang += "─" * 50 + "\n"
        visual_lang += "L5 摄影与剪辑层 (L1-L7 七层 prompt 架构)\n"
        visual_lang += "─" * 50 + "\n"
        visual_lang += "OPTICS: " + focal_info.get("cn", 焦段) + ", " + aperture_info.get("cn", 光圈) + ", " + shot_info + " 景深.\n"
        visual_lang += "CAMERA: 由 " + 摄影指导 + " 风格决定 — " + dp_info.get("composition", "") + "\n"
        visual_lang += "COMPOSITION: " + comp_info + "\n\n"

        visual_lang += "L7 风格约束层:\n"
        visual_lang += "  - 必须坚持 " + focal_info.get("cn", 焦段) + " 焦段\n"
        visual_lang += "  - 必须坚持 " + aperture_info.get("cn", 光圈) + " 光圈\n"
        visual_lang += "  - 整场戏坚持 " + shot_info + " 景别变化范围\n"
        visual_lang += "  - 构图坚持 " + comp_info + "\n"
        visual_lang += "  - 全部 L1-L7 必须保持风格一致\n\n"

        # ========== Phase 15 核心: 60:30:10 色彩法则 (≥ 1000 字符) ==========
        color_60 = "════════════════════════════════════════\n"
        color_60 += "【60:30:10 色彩法则】Phase 15 核心\n"
        color_60 += "════════════════════════════════════════\n\n"
        color_60 += "AIGC 影视全流程解析 § 环节 15 + 37: 60:30:10 法则严格执行\n"
        color_60 += "(Hell Grind + 斯托拉罗色彩理论 + 8 大色彩风格)\n\n"

        color_60 += "本场戏 60:30:10 设定:\n\n"
        color_60 += "【主色 60% — 场景/电影主调】\n"
        color_60 += "  设定: " + 主色_60 + "\n"
        color_60 += "  功能: 决定整体情绪, 时代主调, 文化背景\n"
        color_60 += "  执行: 全场戏 60% 面积都是主色\n\n"

        color_60 += "【辅色 30% — 角色/关系】\n"
        color_60 += "  设定: " + 辅色_30 + "\n"
        color_60 += "  功能: 角色服装/关系色彩\n"
        color_60 += "  执行: 角色服装/关键道具占 30%\n\n"

        color_60 += "【点缀色 10% — 戏剧时刻】\n"
        color_60 += "  设定: " + 点缀色_10 + "\n"
        color_60 += "  功能: 关键道具/情绪点, 戏剧化使用\n"
        color_60 += "  执行: 关键道具/关键瞬间 10%, 极致强调\n\n"

        color_60 += "色彩心理学 (10 色):\n"
        for c, m in COLOR_PSYCHOLOGY.items():
            color_60 += "  - " + c + ": " + m + "\n"
        color_60 += "\n"

        color_60 += "经典电影 60:30:10 案例:\n"
        color_60 += "  - 《银翼杀手2049》主色 60% = 黄沙橙黄 + 辅色 30% = 高对比蓝 + 点缀 10% = 红色 (Joi)\n"
        color_60 += "  - 《辛德勒的名单》黑白 60% + 黑灰 30% + 点缀 10% = 红衣小女孩\n"
        color_60 += "  - 《花样年华》主色 60% = 老上海红绿 + 辅色 30% = 暖黄 + 点缀 10% = 走廊红灯\n"
        color_60 += "  - 《寄生虫》主色 60% = 富人家冷灰白 + 辅色 30% = 公园绿 + 点缀 10% = 山水画血\n"
        color_60 += "  - 《教父》主色 60% = 暖棕橙黄 + 辅色 30% = 深红 + 点缀 10% = 黑色\n\n"

        color_60 += "调色 3 阶段 (一级/二级/创意):\n"
        color_60 += "  - 一级 (Primary): 统一主色 60% 色温/对比度/曝光\n"
        color_60 += "  - 二级 (Secondary): 保持辅色 30% 一致, 肤色优先\n"
        color_60 += "  - 创意 (Creative): 强化点缀色 10%, 服务情感\n\n"

        # ========== Phase 15 核心: 9 维光影 (≥ 1000 字符) ==========
        lighting_9d = "════════════════════════════════════════\n"
        lighting_9d += "【9 维光影设计】Phase 15 核心\n"
        lighting_9d += "════════════════════════════════════════\n\n"
        lighting_9d += "AIGC 影视全流程解析 § 环节 16: 光影语言设计\n"
        lighting_9d += "(DP " + 摄影指导 + " 风格 + CIE LAB 9 维参数)\n\n"

        lighting_9d += "本场戏 9 维光影设定:\n\n"
        lighting_9d += "  【1. 光源类型】 " + 光源类型 + "\n"
        lighting_9d += "    逻辑: 光源必须能在画面内找到, 否则观众潜意识不信\n"
        lighting_9d += "    全部: " + " / ".join(LIGHTING_9D_PHASE15["1_光源类型"]) + "\n\n"

        lighting_9d += "  【2. 方向】 " + 光影方向 + "\n"
        for d in LIGHTING_9D_PHASE15["2_方向"]:
            lighting_9d += "    - " + d + ": 方向 (顺光/侧光/逆光/顶光/底光/伦勃朗)\n"
        lighting_9d += "\n"

        lighting_9d += "  【3. 强度】 强光 (戏剧) / 中光 (平衡) / 弱光 (柔和神秘)\n"
        lighting_9d += "  【4. 色温】 " + 色温 + " (K 值锁定)\n"
        lighting_9d += "    - warm_3200K: 钨丝/烛光/夕阳, 温暖/怀旧\n"
        lighting_9d += "    - neutral_5500K: 日光, 自然\n"
        lighting_9d += "    - cool_6500K: 阴天/医院, 冷/孤独\n"
        lighting_9d += "    - blue_hour_8000K: 蓝调, 神秘/超现实\n\n"

        lighting_9d += "  【5. 软硬】 硬光 (戏剧/恐怖) / 软光 (商业/美妆/亲密) / 极软光 (神秘/超现实)\n"
        lighting_9d += "  【6. 比例】 " + 比例 + " (高调 2:1 明亮 / 中间调 4:1 平衡 / 低调 8:1 戏剧)\n"
        lighting_9d += "  【7. 阴影】 长阴影 (戏剧/超现实) / 短阴影 (客观) / 无阴影 (神秘)\n"
        lighting_9d += "  【8. 特殊光影】 丁达尔 (光柱) / 剪影 / 伦勃朗光 / 蝴蝶光 / 轮廓光\n"
        lighting_9d += "  【9. 时间】 " + 时间 + "\n"
        lighting_9d += "    - 正午/黄昏/黄金时刻/蓝色时刻/夜晚\n\n"

        lighting_9d += "9 维光照控制 (CIE LAB + 摄影本体):\n"
        lighting_9d += "  - intensity: 光源强度 0.0-1.0\n"
        lighting_9d += "  - x/y/z: 光源 3D 位置 (-1.0 到 1.0)\n"
        lighting_9d += "  - temp: 色温 K (2700/3200/5500/6500)\n"
        lighting_9d += "  - radius: 影响范围 0.0-1.0\n"
        lighting_9d += "  - type_id: 0=点光 1=定向光 2=面光 3=环境光 4=聚光\n"
        lighting_9d += "  - falloff: 1=linear 2=quadratic 3=cubic\n"
        lighting_9d += "  - shadow_bias: 阴影偏移 0.0-1.0\n\n"

        lighting_9d += "光影一致性检查清单 (跨镜头):\n"
        lighting_9d += "  - [ ] 光源方向是否一致?\n"
        lighting_9d += "  - [ ] 色温是否一致? (K 值锁定)\n"
        lighting_9d += "  - [ ] 光比是否一致? (" + 比例 + ")\n"
        lighting_9d += "  - [ ] 阴影方向是否一致?\n"
        lighting_9d += "  - [ ] 软硬是否一致?\n"
        lighting_9d += "  - [ ] 时间是否一致? (" + 时间 + ")\n"
        lighting_9d += "  - [ ] 关键道具光影是否一致?\n"
        lighting_9d += "  - [ ] 肤色是否一致? (大银幕上肤色最重要)\n\n"

        # ========== Phase 15 核心: 8 大摄影指导 ==========
        dp_style = "════════════════════════════════════════\n"
        dp_style += "【8 大顶级摄影指导风格库】Phase 15\n"
        dp_style += "════════════════════════════════════════\n\n"
        dp_style += "当前选择: " + 摄影指导 + "\n"
        dp_style += "签名: " + dp_info.get("signature", "") + "\n\n"
        dp_style += "─" * 50 + "\n"

        for dp_name, info in DP_8_MASTERS.items():
            dp_style += "【" + dp_name + "】\n"
            dp_style += "  代表作: " + " / ".join(info.get("key_films", [])) + "\n"
            dp_style += "  签名: " + info.get("signature", "") + "\n"
            dp_style += "  光影: " + info.get("lighting", "") + "\n"
            dp_style += "  构图: " + info.get("composition", "") + "\n"
            dp_style += "  色彩: " + info.get("color", "") + "\n"
            dp_style += "  镜头: " + info.get("lens", "") + "\n"
            dp_style += "  触发: " + info.get("trigger", "") + "\n"
            dp_style += "  执行: " + info.get("execute", "") + "\n\n"

        # 模型路由
        recommended = route_model(特效类型, 场景描述, 时长_秒, 语言)
        if recommended:
            sel = recommended[0]
            sel_model = "推荐模型: " + sel + "\n规格: " + str(MODEL_REGISTRY[sel]['max_duration']) + "秒上限 / " + str(MODEL_REGISTRY[sel]['max_references']) + "参考\n价格: " + MODEL_REGISTRY[sel]['price'] + "\n擅长: " + MODEL_REGISTRY[sel]['best_for']
        else:
            sel = "Seedance 2.5"
            sel_model = "默认推荐: " + sel + " (兼容性最好)"

        # 模型弱点规避
        if sel in MODEL_REGISTRY:
            weaknesses = MODEL_REGISTRY[sel]['weaknesses']
            strength = MODEL_REGISTRY[sel]['strengths']
            avoid = "模型 " + sel + " 弱点规避:\n"
            avoid += "- 弱点: " + ", ".join(weaknesses) + "\n"
            avoid += "- 规避方法:\n"
            avoid += "  1. 把弱项拆成短片段 (< 5 秒)\n"
            avoid += "  2. 用多模型组合 (Kling 动作 + Veo 物理)\n"
            avoid += "  3. 局部重绘 (Seedance 2.5 框选)\n"
            avoid += "  4. 局部 + 后期清理 pass\n\n"
            avoid += "模型 " + sel + " 优势放大:\n"
            avoid += "- 优势: " + ", ".join(strength) + "\n"
            avoid += "- 放大方法:\n"
            avoid += "  1. 用 50 参考锚定 (Seedance 2.5)\n"
            avoid += "  2. 3D 白模控制空间 (Seedance 2.5)\n"
            avoid += "  3. 多语言口型 (Seedance 2.5)\n"
        else:
            avoid = "无弱点数据"

        # 角色一致性工作流
        consistency = build_character_consistency_workflow(参考图片URL, 服装描述, 角色名)

        # 11 阶段管线
        pipeline = """════════════════════════════════════════
【11 阶段制作管线 (Higgsfield Filmmaking Course)】
════════════════════════════════════════

Phase 1 (资产准备, 7-10 天):
  1. Name your assets       - 资产命名
  2. Generating locations   - 生成场景
  3. Generating characters  - 生成角色
  4. Test in Seedance       - 在 Seedance 测试 (10 次压力测试)

Phase 2 (生成期, 14 天):
  5. Shoot the scene        - 拍摄场景 (115,446 次生成)

Phase 3 (后期, 7-14 天):
  6. Soundscape             - 声音设计
  7. Music                  - 音乐配乐
  8. Cut                    - 剪辑 (跟生成并行)
  9. Color                  - 调色 (统一 look) — 60:30:10 严格执行
  10. VFX                    - 视觉特效
  11. QA                     - 质量检查 (8 类问题)

════════════════════════════════════════
【5 大创作铁律】
════════════════════════════════════════

1. 资产先行 (省的钱比其他所有规则加起来还多)
2. 每次描述全部 (descriptor 逐字进每个 prompt)
3. 一次只改一行 (整段重写会丢 work)
4. 给模型更少的自由 (角落而不是房间)
5. 镜头搞不定就简化 (拆/删/换)
"""

        # H3 prompt
        h3 = """SCENE CONTEXT
EXACT 3 CHARACTERS — NO DUPLICATES: %s, JAX, REIN. %s, night. %s effect on main character. %s directing style, %s DP style (signature: %s). One continuous 12.0s shot, no cuts.

ACTIVE REFERENCES
  @%s for character reference — %s
  @jax for character reference
  @rein for character reference
  @loc_%s_scene for location reference

GEO SPATIAL LAYOUT (locked across every shot):
  — PLATFORM = circular ritual disc at scene center
  — CAMERA STAYS on action side
  — 180° AXIS: camera NEVER crosses the line

L5 摄影与剪辑层 (Phase 15):
  OPTICS: %s, %s, %s 景深
  CAMERA: %s DP style
  COMPOSITION: %s
  60:30:10 COLOR: 主色 60%% = %s, 辅色 30%% = %s, 点缀色 10%% = %s
  9 维光影: %s from %s at %s, %s key-to-fill, %s

FIRST FRAME AND SPATIAL BLOCKING
  0.0-1.0s: Wide static shot. Everyone at fixed position. %s effect visible. No motion. 1 second of pure space.

ACTION TIMING
  0.0-3.0s — %s effect builds up
  3.0-8.0s — main action
  8.0-12.0s — %s resolves

PHYSICS
  Mass has real weight. Correct contact shadows. No floating props.

LIGHTING
  Dramatic backlight from %s source. Rim-lighting on characters. %s

AUDIO
  - Voice: characters speak only in quotes
  - Sound: %s SFX (crackle/whoosh/rumble)
  - NO MUSIC (留后期)

CHARACTER ACTING
  %s — emotional state: visible body state. Wants: execute %s. Dominant body rhythm: heavy, planted.

STYLE
%s

QUALITY
  Cinematic, live-action, 24fps smooth motion

POSITIVE CONSTRAINTS
  - Exactly 3 people
  - Exactly ONE %s effect
  - No floating props
  - Camera stays on action side for all 12 seconds

Live-action. NON-IP. 16:9. 12s. SFX only. NO CGI. Cinematic.
""" % (
            角色名, 场景描述, 特效类型, 导演风格, 摄影指导, dp_info.get("signature", ""),
            角色名, 服装描述, 特效类型,
            focal_info.get("cn", 焦段), aperture_info.get("cn", 光圈), shot_info,
            摄影指导, comp_info,
            主色_60, 辅色_30, 点缀色_10,
            光源类型, 光影方向, 色温, 比例, 时间,
            特效类型, 特效类型, 特效类型,
            光源类型, 光影方向,
            特效类型,
            角色名, 特效类型,
            STYLE_PREFIX if _HAS_DEPS else "Cinematic, live-action, film grain, no CGI",
            特效类型,
        )

        if 启用反AI and _HAS_DEPS:
            try:
                visual_lang = inject_anti_ai_pb(visual_lang)
            except Exception:
                pass
            try:
                color_60 = inject_anti_ai_pb(color_60)
            except Exception:
                pass
            try:
                lighting_9d = inject_anti_ai_pb(lighting_9d)
            except Exception:
                pass
            try:
                dp_style = inject_anti_ai_pb(dp_style)
            except Exception:
                pass
            try:
                h3 = inject_anti_ai_pb(h3)
            except Exception:
                pass

        # ========== Phase 36.6 v5f: 4 路起点注入 集成到 h3_prompt 输出 ==========
        # 把 DirectorMasteryNode / AestheticJudgmentPro / StyleGuidePro / DirectorIntentPro
        # 的输出整合到 h3_prompt, 让模型能感知灵魂/审美/风格/意图
        injection_block = ""
        if 灵魂注入 or 审美注入 or 风格注入 or 导演意图:
            injection_block = "\n\n════════════════════════════════════════\n"
            injection_block += "【Phase 36.6 v5f: 4 路起点注入 整合】\n"
            injection_block += "════════════════════════════════════════\n\n"
            if 灵魂注入:
                injection_block += "【灵魂注入】(60 情感 + 10 维度 + 7 融合模式):\n" + str(灵魂注入) + "\n\n"
            if 审美注入:
                injection_block += "【审美判断】(8 原则 + 120 场景):\n" + str(审美注入) + "\n\n"
            if 风格注入:
                injection_block += "【风格指南】(5 调色 + 8 摄影指导 + 9 构图):\n" + str(风格注入) + "\n\n"
            if 导演意图:
                injection_block += "【导演意图】(4 类意图 + 观众应感到):\n" + str(导演意图) + "\n"
            h3 = h3 + injection_block

        # ========== Phase 36.6 v5i: 35 导演 8 维档案 + 100 场景匹配增强 ==========
        # 把导演风格的 8 维真实档案 (镜头/光/节奏/色彩/表演/构图/声音/情绪) + 物件/年代/代表作
        # 集成到 h3_prompt 末尾, 提升输出具体性 (D级 → A级)
        try:
            from director_data_unified import (
                DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, ALL_DIRECTOR_NAMES, get_director_profile, SCENE_DATABASE_100, get_scene
            )
            director_zh = str(导演风格).split(" (")[0] if "(" in str(导演风格) else str(导演风格)
            if director_zh and director_zh != "通用" and director_zh in DIRECTOR_PROFILES_ALL:
                d_p = DIRECTOR_PROFILES_ALL[director_zh]
                v5i_block = "\n\n════════════════════════════════════════\n"
                v5i_block += f"【Phase 36.6 v5i: {director_zh} 35 导演 8 维真实档案】\n"
                v5i_block += "════════════════════════════════════════\n\n"
                v5i_block += f"镜头: {d_p['镜头']}\n"
                v5i_block += f"光: {d_p['光']}\n"
                v5i_block += f"节奏: {d_p['节奏']}\n"
                v5i_block += f"色彩: {d_p['色彩']}\n"
                v5i_block += f"表演: {d_p['表演']}\n"
                v5i_block += f"构图: {d_p['构图']}\n"
                v5i_block += f"声音: {d_p['声音']}\n"
                v5i_block += f"情绪: {d_p['情绪']}\n"
                v5i_block += f"代表作: {d_p['代表作']} (年代 {d_p['年代']})\n"
                v5i_block += f"标志物件: {d_p['物件']}\n"
                v5i_block += f"5 维标签: {d_p['5维标签']}\n"
                # 100 场景匹配
                s_match = get_scene(director_zh, scene_keyword=str(场景描述))
                if s_match and s_match.get("director") != "通用":
                    v5i_block += (
                        f"\n场景参考: {s_match['director']} - {s_match['scene']} | "
                        f"物件={s_match['object']} | 色调={s_match['color']} | "
                        f"声景={s_match['sound']} | 情绪={s_match['emotion']}\n"
                    )
                h3 = h3 + v5i_block
        except Exception:
            pass

        return (effects_overview, visual_lang, color_60, lighting_9d, dp_style, sel_model, avoid, consistency, pipeline, h3)


# ============================================================
# 演示
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Phase 14 - Cinematic Studio + Phase 15 视觉语言专家重做")
    print("=" * 70)
    n = CinematicStudio()
    print("CATEGORY=%s" % n.CATEGORY)
    print("RETURN_NAMES=%s" % str(n.RETURN_NAMES))
    print()
    print("23 电影特效: %d" % len(CINEMATIC_EFFECTS_23))
    print("模型数量: %d" % len(MODEL_REGISTRY))
    print("8 大摄影指导: %d" % len(DP_8_MASTERS))
    print()
    recs = route_model("venom_symbiote", "赛博朋克夜晚", 5, "zh")
    print("毒液附体 5s zh 推荐模型: %s" % recs)
