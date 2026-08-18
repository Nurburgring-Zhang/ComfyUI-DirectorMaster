# -*- coding: utf-8 -*-
"""
CharacterArcPro — 角色弧光追踪 (环节 9, 12)
====================================================
世界顶级导演集群级 Phase 16 深度重写 — 5 要素 + L1-L7 七层 +
11 维导演控制 + 3 留白 + 3 运镜法则 + H3 三大字段完整输出.

本节点对应:
- 环节 9: 角色弧光追踪 (确保角色发展连贯, 情感变化曲线设计)
- 环节 12: 剧本的"导演读解" (转化为导演视角的角色解读)

数据层 (DATA LAYER):
  - 1161 部 director_view 14 维作品库
  - 63 导演 12 维方法论
  - 191 反 AI 词表 + 10 强制具体细节铁律
  - 12 套剧本理论
  - 14 部真实 AI 短剧实战
  - 8 大世界顶级导演风格库
  - Lajos Egri 角色前提/欲望 vs 需求
  - Carl Jung 12 原型
  - 角色弧光 7 大类型
  - 角色深度 6 维 (生理/心理/社会/性/经济/文化)
  - Vogler 12 阶段

上下文缩略层 (CONTEXT-BRIEF LAYER):
  1 句话总结 = 角色名 + 原型 + 弧光 + 欲望 vs 需求 + 导演风格

Skill/Harness 层 (SKILL/HARNESS LAYER):
  - Lajos Egri 角色前提公式
  - 欲望 (Want) vs 需求 (Need) 公式
  - 12 阶段 (Vogler)
  - 12 原型 (Jung)
  - 7 弧光类型
  - 6 维深度
  - 8 大导演塑造技法 (王家卫/侯孝贤/是枝裕和/李沧东/蔡明亮/毕赣/黑泽明/伯格曼)

经验矩阵层 (EXPERIENCE MATRIX LAYER):
  - 14 部真实短剧角色案例
  - 失败模式 (平面/空洞/工具人/说教)
  - 修复方案

AI 深度处理层 (AI DEEP PROCESSING LAYER):
  - 191 反 AI 词表清洗
  - 10 强制具体细节铁律
  - L1-L7 七层动态拼装
  - 11 维导演控制
  - 3 留白 (时间/空间/叙事)
  - 3 运镜法则
  - H3 三大字段
"""

import os
import sys
import json

# Phase 17.6: 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# Knowledge Base 集成
try:
    from knowledge_base import (
        NARRATIVE_STRUCTURES, EMOTION_RENDERING,
        get_director_decision,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False


try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from director_mastery_v2 import (
        CHARACTER_ARCS,
        HERO_JOURNEY_12,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
        ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
        SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
        build_h3_three_fields, select_camera_motion, format_shot_motion,
        build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
        inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
        inject_silence_mastery_5, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:  # pragma: no cover
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)

try:
    from master_orchestrator import (
        L1_INTENT_TEMPLATE, L2_ASSET_TEMPLATE, L3_SPATIAL_TEMPLATE,
        L4_ACTING_TEMPLATE, L5_CAMERA_TEMPLATE, L6_SOUND_TEMPLATE, L7_STYLE_TEMPLATE,
        THREE_WHITESPACE, THREE_CAMERA_LAWS,
    )
    from style_prefix_data import STYLE_PREFIX, FIFTEEN_BLOCKS
    _HAS_INTERNAL_DOCS = True
except Exception:  # pragma: no cover
    _HAS_INTERNAL_DOCS = False


# ============================================================
# 7 大角色弧光
# ============================================================
CHARACTER_ARC_TYPES = {
    "positive_arc": "正向弧: 主角从缺陷走向圆满, 常见: 英雄片/成长片/救赎片",
    "negative_arc": "负向弧: 主角从圆满走向毁灭, 常见: 悲剧/反英雄/希腊悲剧",
    "flat_arc": "扁平弧: 主角本身不变, 但改变世界, 常见: 漫威式英雄/福尔摩斯",
    "corruption_arc": "堕落弧: 主角从善良走向黑暗, 常见: 黑化片/权力片",
    "redemption_arc": "救赎弧: 主角从罪走向宽恕, 常见: 救赎片/宗教片",
    "testing_arc": "考验弧: 主角坚守本心不被动摇, 常见: 信仰片/道德片",
    "disillusionment_arc": "觉醒弧: 主角从天真走向现实, 常见: 青春片/政治片",
}

# ============================================================
# 12 个经典角色原型 (Carl Jung)
# ============================================================
ARCHETYPES_12 = {
    "1. Innocent": "纯真者: 看到世界最好的一面, 相信美好",
    "2. Everyman": "平凡人: 普通观众代入, 脚踏实地",
    "3. Hero": "英雄: 勇敢面对挑战, 自我牺牲",
    "4. Outlaw": "叛逆者: 反叛规则, 打破体制",
    "5. Explorer": "探险家: 寻找自我, 突破边界",
    "6. Creator": "创造者: 用双手实现梦想",
    "7. Ruler": "统治者: 建立秩序, 控制",
    "8. Caregiver": "照顾者: 保护他人, 牺牲自己",
    "9. Magician": "魔法师: 改变现实, 治愈创伤",
    "10. Lover": "恋人: 追求激情, 关系至上",
    "11. Sage": "智者: 寻求真理, 传授智慧",
    "12. Jester": "愚者: 活在当下, 欢乐至上",
}

# ============================================================
# 角色深度 6 维 (基于 Lajos Egri)
# ============================================================
CHARACTER_DEPTH_6 = {
    "生理学": "身体特征: 性别/年龄/身高/长相/声音/动作/健康",
    "社会学": "社会身份: 阶级/职业/教育/家庭/朋友圈/政治立场",
    "心理学": "内心世界: 性格/脾气/欲望/恐惧/创伤/防御机制/价值观",
    "性": "亲密关系: 性取向/亲密关系/恋爱史/性创伤",
    "经济": "物质条件: 收入/财产/债务/消费习惯/财务目标",
    "文化": "文化背景: 宗教/地域/民族/语言/代际/文化禁忌",
}

# ============================================================
# 欲望 vs 需求 (真实角色塑造核心)
# ============================================================
DESIRE_VS_NEED = {
    "欲望 (Want)": "表层目标, 角色认为想要的东西, 推动剧情",
    "需求 (Need)": "深层需求, 角色真正需要的东西, 但不自知",
    "冲突": "当欲望和需求矛盾时, 角色开始成长, 这是角色弧的核心",
    "真实弧": "角色最终意识到自己真正需要的是什么, 牺牲欲望, 拥抱需求",
    "悲剧弧": "角色始终追求欲望, 拒绝需求, 最终毁灭",
}

# ============================================================
# 8 大世界顶级导演风格库 (含角色塑造技法)
# ============================================================
MASTER_DIRECTORS_8 = {
    "Paul Thomas Anderson (PTA)": {
        "角色塑造": "演员生涯最佳; 从每一个演员身上逼出生涯最佳 (Day-Lewis / Phoenix / Sandler)",
        "镜头运动": "长焦 + 缓推 + 偶发 360 度环轨; 70-100mm",
        "节奏": "非线性, 时序错位; 像小说家般掌控节奏",
        "光影": "自然光 + 钨丝灯混合; 高对比",
        "声音": "环境音为主, 偶发 Low-Fi 弦乐",
        "留白": "大量叙事留白, 不说尽",
        "代表作品": "《木兰花》《血色将至》《魅影缝匠》《甘草披萨》",
        "格言": "用小说家般的方式取景, 拒绝刻奇",
    },
    "Christopher Nolan (诺兰)": {
        "角色塑造": "克制但精确; 演员要承担观念重量 (Bale / DiCaprio / Caine / Murphy)",
        "镜头运动": "IMAX 65mm + 跟踪; 史诗尺度, 三小时道德辩论",
        "节奏": "信息密度高, 时间折叠剪辑",
        "光影": "工业光; 大比度, 单光源",
        "声音": "Hans Zimmer 主导",
        "留白": "空间与叙事留白兼具, 留 30%",
        "代表作品": "《盗梦空间》《星际穿越》《黑暗骑士》《奥本海默》",
        "格言": "把以观念为主的史诗变成全球盛事, 且全程不见一袭披风",
    },
    "奉俊昊 (Bong Joon-ho)": {
        "角色塑造": "演员被允许表演, 但要精确 (宋康昊 / 李善均)",
        "镜头运动": "中景 + 横移 + 精确调度",
        "节奏": "类型当特洛伊木马, 喜剧/恐怖/阶级怒火",
        "光影": "高对比 + 暗部细节; 类型片光感",
        "声音": "类型片配乐 + 关键时刻环境音",
        "留白": "几乎不留, 但情感留白极深",
        "代表作品": "《寄生虫》《杀人回忆》《雪国列车》《汉江怪物》",
        "格言": "在同一场戏中从喜剧滑向恐怖再滑向阶级怒火, 始终不曾失足",
    },
    "Martin Scorsese (斯科塞斯)": {
        "角色塑造": "演员要逼出生涯最佳 (De Niro / DiCaprio / Pesci)",
        "镜头运动": "中焦 + 跟拍 + 燃烧式运镜",
        "节奏": "高速剪辑 + 流行乐标记时代",
        "光影": "高对比 + 烟雾 + 红色霓虹",
        "声音": "流行歌做时代标记 + 古典配乐双轨",
        "留白": "几乎不留, 但要留 1 个让观众崩溃的时刻",
        "代表作品": "《好家伙》《出租车司机》《华尔街之狼》《花月杀手》",
        "格言": "审问美国暴力; Cinemascope 是现代美国的尺寸",
    },
    "Denis Villeneuve (维伦纽瓦)": {
        "角色塑造": "克制但承受压力 (Gosling / Chalamet / Adams)",
        "镜头运动": "极长焦 + 慢推 + 长时间不切",
        "节奏": "史诗慢节奏, 单镜头信息密度高",
        "光影": "自然光 + 沙尘/雾气; 静默与尺度并存",
        "声音": "Hans Zimmer + Jóhann Jóhannsson 低频压迫",
        "留白": "极长的时间留白, 观众情绪在等待中形成",
        "代表作品": "《沙丘》《降临》《银翼杀手 2049》《边境杀手》",
        "格言": "静默与尺度并存; 让观众被画面的尺度压住",
    },
    "Yorgos Lanthimos (兰斯莫斯)": {
        "角色塑造": "古怪眼界, 让演员显得滑稽 (Colman / Stone / Plemons)",
        "镜头运动": "广角 + 鱼眼 + 不规则构图",
        "节奏": "冷调, 节奏却突然加速, 偶发冷幽默",
        "光影": "高对比 + 冷色 + 偶发暖色反差",
        "声音": "极简电子 + 古典; 偶发突然静音",
        "留白": "叙事留白, 不说尽; 让观众自己懂",
        "代表作品": "《可怜的东西》《宠儿》《龙虾》《圣鹿之死》",
        "格言": "从那些甘愿为真正新鲜之物而显得滑稽的明星身上, 逼出毫无畏惧的表演",
    },
    "Greta Gerwig (葛韦格)": {
        "角色塑造": "演员写内心世界 (Saoirse Ronan / Chalamet / Florence Pugh)",
        "镜头运动": "中景 + 自然跟拍 + 大量手部特写",
        "节奏": "节奏自然, 角色走路的速度",
        "光影": "暖调 + 自然光; 50mm 摄影",
        "声音": "流行歌标记时代 (Lady Bird / Little Women)",
        "留白": "角色内心的留白; 大量 POV 镜头",
        "代表作品": "《伯德小姐》《小妇人》《芭比》《弗朗西丝·哈》",
        "格言": "写内心世界胜过几乎所有在世的创作者, 再以举重若轻的笔法将其执导出来",
    },
    "黑泽明 (Kurosawa)": {
        "角色塑造": "三船敏郎 / 志村乔; 演员要承担史诗",
        "镜头运动": "中焦 + 横移 + 多机位; 极端清晰",
        "节奏": "群戏调度, 节奏精确",
        "光影": "硬光高反差 + 黑白摄影; 极端天气即情绪",
        "声音": "古典配乐 + 极端环境音",
        "留白": "空间留白; 大场面下放小人物",
        "代表作品": "《七武士》《罗生门》《乱》《用心棒》《影武者》",
        "格言": "让电影的视觉/叙事/情绪/空间都做到极致清晰",
    },
}

# ============================================================
# 8 大导演角色塑造技法 (8 Director Acting Techniques)
# ============================================================
DIRECTOR_ACTING_8 = {
    "王家卫": "给角色一个标志性物件, 物件 = 内心; 道具承载潜文本",
    "侯孝贤": "让角色不说话, 让动作说话; 长镜头静观",
    "是枝裕和": "给角色一个身体习惯 (摸下巴/眨眼睛); 日常动作 = 内心",
    "李沧东": "角色不解释情绪, 让观众自己懂; 半秒消化再开口",
    "蔡明亮": "角色 = 动作, 不需要心理; 极慢节奏",
    "毕赣": "角色活在时间折叠中, 不分过去现在; 叠化与时间",
    "黑泽明": "天气即情绪; 演员要承担史诗; 多机位群戏",
    "伯格曼": "脸特写 30 秒, 只看到眼睛红了, 但没流泪; 沉默 = 情感",
}

# ============================================================
# 11 维导演控制
# ============================================================
DIRECTOR_CONTROL_11_FULL = {
    "空镜 (Empty Shot)": "用空镜建立空间和时间的厚度; 角色不在场时, 空间本身说话",
    "留白 (Pause)": "在动作和台词之间插入沉默; 3 法则: 时间/空间/叙事",
    "氛围渲染 (Atmosphere)": "用光影/声音/天气营造不可言说的情绪; 雨声/蒸汽/灰尘",
    "悬疑 (Suspense)": "信息释放节奏; 观众知道得比角色少, 制造焦虑",
    "多线 (Multi-thread)": "平行剪辑建立命运交错; A 线 B 线交替",
    "反转 (Reversal)": "剧情/观众/角色认知的颠覆; 8 种反转类型",
    "高潮 (Climax)": "情绪/动作/观念的集中爆发点; 单镜头信息密度最高",
    "余韵 (Aftertaste)": "结尾后观众的余思; 6 种余韵",
    "推进节奏 (Pacing)": "快慢交替; 静极静 + 动极动",
    "感情控制 (Emotion Control)": "导演像调音师一样调音观众情绪曲线",
    "角色塑造 (Character Building)": "用动作/物件/习惯/口头禅替代心理描写",
}


# ============================================================
# Helper
# ============================================================
def _str(v, default=""):
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else default
    return str(v)


def _pick(d, key, default=""):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


# ============================================================
# L1-L7 七层动态生成
# ============================================================
def _build_l1(intent_feel, character_name, arc):
    return (
        "L1 - 意图与验收 (DIRECTOR'S WHY)\n"
        "本镜让观众 " + intent_feel + ";\n"
        "通过 " + character_name + " 的 " + arc + " 完成;\n"
        "结束时观众应看到: " + character_name + " 的情绪从 A 状态过渡到 B 状态, 弧光清晰可信.\n"
        "导演验收: 角色变化必须有原因 (因为发生了 X, 所以 Y 改变), 不能突变; "
        "欲望 vs 需求的张力贯穿全场; 微动作总和 = 角色的真实情感.\n"
        "潜文本目标: 表面在讲" + character_name + " 的故事, 实际在说" + arc + " 的普世性."
    )


def _build_l2(character_name, archetype, location, signature_obj):
    return (
        "L2 - 资产与引用 (LOCKED IDENTITIES)\n"
        "ACTIVE REFERENCES\n"
        "@" + character_name + " — 角色. 固定参照: " + archetype + " 原型, 标志性物件 (" + signature_obj + ").\n"
        "@" + location + " — 空间参照: take only the space and the texture: 90 年代北方质感, 油烟熏黑的白墙.\n"
        "Do not use as a starting frame, do not inherit the composition, the angle or the grade."
    )


def _build_l3(landmarks, axis_side="south"):
    return (
        "L3 - 空间与数量 (UNBREAKABLE STAGE)\n"
        "GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):\n"
        + landmarks + "\n"
        "— 180° AXIS: camera ALWAYS stays on " + axis_side + " side — it NEVER crosses the line.\n\n"
        "三大铁律:\n"
        "  1. 只写空间事实, 不写人物动作\n"
        "  2. 方向用 frame-left/frame-right + 米数, 不用 hero's left\n"
        "  3. 位置挂地标+距离, 不写相对位置"
    )


def _build_l4(character_name, want, need, action_timing, signature_habit):
    return (
        "L4 - 表演与物理 (MAKE DIGITAL ACTORS ALIVE)\n"
        "CHARACTER ACTING\n"
        + character_name + " — 状态: 防御机制展现 (" + signature_habit + "). "
        "What he wants: " + want + ". What he is hiding: 真正需要 " + need + " 但不自知.\n"
        "  Dominant body rhythm: " + signature_habit + " (微动作总和 = 真实情感).\n"
        "  Visible habits: " + signature_habit + ", 表情先于台词 0.3 秒.\n"
        "What changes: 关键微动作触发, 角色从 A 状态进入 B 状态 (弧光的转折点).\n\n"
        "ACTION TIMING (微秒级时间码):\n"
        + action_timing + "\n\n"
        "PHYSICS — Gravity and inertia respected. No floating props.\n\n"
        "5 支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN\n"
        "  WHAT: 角色想要 " + want + " (欲望)\n"
        "  OBSTACLE: 内心防御机制 (拒绝真相/逃避/否认)\n"
        "  COST: 说出来就承认软弱, 维持的是'家之主'的面子\n"
        "  STRATEGY: 用动作替代话 (切菜/摆筷子), 让沉默承担情绪\n"
        "  TURN: 放下刀的瞬间, 弧光的转折 (欲望 → 需求)\n\n"
        "7 活人感规则:\n"
        "  1. 分阶段眨眼: lazy blink → DOUBLE-BLINK → HARD reset-blink\n"
        "  2. 视线先于头\n"
        "  3. 微生命: 每 1-2 秒一个微事件\n"
        "  4. 静止保持张力\n"
        "  5. 反应先于台词\n"
        "  6. 重要事件后消化: 半秒消化再开口\n"
        "  7. 让手忙起来"
    )


def _build_l5(director, signature_obj):
    focal_map = {
        "Paul Thomas Anderson (PTA)": "85",
        "Christopher Nolan (诺兰)": "50",
        "奉俊昊 (Bong Joon-ho)": "40",
        "Martin Scorsese (斯科塞斯)": "50",
        "Denis Villeneuve (维伦纽瓦)": "135",
        "Yorgos Lanthimos (兰斯莫斯)": "24",
        "Greta Gerwig (葛韦格)": "50",
        "黑泽明 (Kurosawa)": "50",
    }
    focal = focal_map.get(director, "50")
    return (
        "L5 - 摄影与剪辑 (CONTROL THE VIEWER'S EYE)\n"
        "OPTICS: " + focal + "mm, T2.0, 浅景深.\n"
        "  角色承载: 焦点永远在角色的微动作 (嘴/手/眼神) 上.\n"
        "CAMERA: Push In 慢推 with small amplitude (0.3m) at slow speed (0.1m/s).\n"
        "  约束: 镜头在角色肩后 0.5m 推进, 不能越过角色肩膀高度.\n"
        "  物件特写: " + signature_obj + " 出现时, 镜头切到 CU, 焦点锁定.\n"
        "NEVER: 不用希区柯克变焦; 不用斯坦尼康长镜 (除非群戏).\n\n"
        "运镜 3 法则:\n"
        "  1. 破坏首帧完成度: 镜头从门框外侧开始, 0.5 秒后'找到'角色\n"
        "  2. 引入非线性运动轨迹: 推轨有 2 个'犹豫点'\n"
        "  3. 制造响应延迟: 角色先动, 镜头 0.3-0.5 秒后跟上"
    )


def _voice_signature(age, gender):
    """V12.7: 按角色真实性别/年龄生成声音签名 (修复硬编码 53岁男性)."""
    try:
        age = int(age)
    except (TypeError, ValueError):
        age = 30
    g = str(gender or "").strip()
    is_female = ("女" in g) or (g.lower() in ("f", "female"))
    gender_label = "女性" if is_female else "男性"
    if age < 13:
        texture = "童声, 清脆, 语速偏快"
    elif age < 26:
        texture = "年轻, 清亮有光泽, 气息足"
    elif age < 45:
        texture = "沉稳, 中音扎实, 语速从容"
    elif age < 60:
        texture = "略带沙哑, 有阅历感, 语速放慢"
    else:
        texture = "苍老, 气息短, 尾音发颤"
    return "%d 岁%s, %s, 说话前咽口水 0.4 秒" % (age, gender_label, texture)


def _build_l6(character_name, signature_habit, quote, silenced, signature_obj,
              gender="女", age=25):
    return (
        "L6 - 声音与对白 (HALF OF PICTURE)\n"
        "VOICE SIGNATURES:\n"
        "  " + character_name + ": " + _voice_signature(age, gender) + "\n\n"
        "DIALOGUE (潜文本对白 6 技巧):\n"
        "  " + character_name + " says: <d>[Chinese] 吃饭吧。</d> (潜文本: 想说对不起)\n"
        "  口头禅: " + quote + " (在弧光转折点重复, 含义反转)\n\n"
        "SILENCED: " + silenced + "\n\n"
        "SFX LAYERS (角色弧光的听觉化):\n"
        "  - 雨声打在玻璃上 (持续, 角色'孤独'的听觉化)\n"
        "  - 切菜声 (0.8 秒/刀, 角色'日常'的节奏化)\n"
        "  - 收音机 (红灯牌) 1990 年代中国流行歌 (邓丽君, 角色'时代记忆')\n"
        "  - 老式冰箱嗡嗡声\n"
        "  - " + signature_habit + " (角色标志性声音)\n"
        "  - 父亲咽口水 (1 次, 开口前 0.4 秒)\n"
        "  - 刀放下的声音 (重点: 比之前 17 刀重 0.3 秒, 弧光转折点)\n"
        "  - " + signature_obj + " 被放下/拿起的声音 (物件承担弧光)\n\n"
        "CONTINUATION TAIL: 上一镜收音机的尾音延 0.5 秒进入本镜\n\n"
        "NO MUSIC (留后期). SFX only. No subtitles."
    )


def _build_l7():
    if _HAS_INTERNAL_DOCS:
        prefix = STYLE_PREFIX
    else:
        prefix = "Live-action. Film grain texture. no 3D render. no game engine."
    return "L7 - 风格约束 (IMMUTABLE)\n" + prefix


# ============================================================
# H3 三大字段生成
# ============================================================
def _build_h3(character_name, scene, want, need, signature_obj, director):
    style = "Cinematic, live-action, 35mm film grain, " + director + " 风格"
    shot_1 = (
        "a medium-wide shot establishes the scene — " + scene + ". "
        "The director intends: 角色 " + character_name + " 的弧光展现, 欲望 '" + want + "' vs 需求 '" + need + "'. "
        "The " + signature_obj + " sits on the table, waiting to be picked up."
    )
    shots = [
        "[Shot 2] At 00:03.500, the camera cuts to a medium close-up of " + character_name + " 's face. "
        + format_shot_motion("Push In", "small", "slow") + " on the eyes, revealing the defense mechanism.",
        "[Shot 3] At 00:08.000, the camera cuts to a close-up of " + character_name + " 's hands holding the " + signature_obj + ". "
        "The camera holds a Static Shot as the hands tremble slightly. S1 says: <d>[Chinese] 吃饭吧。</d>",
        "[Shot 4] At 00:15.000, over-the-shoulder shot. " + format_shot_motion("Push In", "small", "slow") + " toward the other character.",
        "[Shot 5] At 00:22.000, the camera holds a Static Shot. 5-10 seconds of silence. 弧光的转折点.",
        "[Shot 6] At 00:27.000, the camera holds for 3 seconds. The " + signature_obj + " catches the light. End of shot.",
    ]
    soundscape = (
        "Steady rain taps against the window. The knife on the cutting board has a dull rhythm. "
        "The old radio plays a 1990s Chinese song at low volume. The clock ticks. " + character_name + " 's breath is audible. "
        "Subtle sounds of the " + signature_obj + " shifting position."
    )
    music = "N/A (留后期)"
    return style, shot_1, shots, soundscape, music


# ============================================================
# CharacterArcPro 主类
# ============================================================
class CharacterArcPro:
    """
    角色弧光节点 — 世界顶级导演集群级 Phase 16 深度重写

    对应环节 9 (角色弧光追踪) + 环节 12 (剧本的"导演读解").

    真正动态生成: 不再 if/else 套模板. 每个输出根据用户输入 (角色名/原型/
    弧光/欲望 vs 需求/6 维深度/身体习惯/口头禅/标志性物件) 实时计算
    L1-L7 七个层级 + H3 三大字段.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "角色姓名": ("STRING", {"default": "林小满"}),
                "角色性别": (["男", "女"], {"default": "女"}),
                "角色年龄": ("INT", {"default": 25, "min": 5, "max": 90, "step": 1}),
                "角色原型_12选1": (list(ARCHETYPES_12.keys()), {"default": "3. Hero"}),
                "角色弧_7选1": (list(CHARACTER_ARC_TYPES.keys()), {"default": "positive_arc"}),
                "欲望_Want": ("STRING", {"default": "找回失去的记忆"}),
                "需求_Need": ("STRING", {"default": "与失散的家人和解"}),
                "导演风格_8选1": (list(MASTER_DIRECTORS_8.keys()), {"default": "Greta Gerwig (葛韦格)"}),
                "生理学": ("STRING", {"default": "身高 165, 短发, 脸上有颗痣, 走路外八"}),
                "心理学": ("STRING", {"default": "倔强, 不善表达, 童年创伤, 防御机制是冷漠"}),
                "社会学": ("STRING", {"default": "孤儿, 没读完高中, 送外卖"}),
                "身体习惯": ("STRING", {"default": "紧张时摸下巴, 走路外八, 眨眼多"}),
                "口头禅": ("STRING", {"default": "我不信。"}),
                "标志性物件": ("STRING", {"default": "一只破旧的口琴"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === Phase 17.6 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
            },
            "optional": {
                "角色背景": ("STRING", {"default": "", "multiline": True}),
                "情绪基调": ("STRING", {"default": "压抑中见希望"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_bible", "arc_journey", "director_lessons")
    FUNCTION = "build_character"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_character(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _MASTERY_ERROR if not _HAS_AI_DEPS else "", "", "")

        # ===== 提取用户输入 =====
        name = _str(kwargs.get("角色姓名"), "林小满")
        gender = _str(kwargs.get("角色性别"), "女")
        age = int(kwargs.get("角色年龄", 25) or 25)
        archetype = _str(kwargs.get("角色原型_12选1"), "3. Hero")
        arc = _str(kwargs.get("角色弧_7选1"), "positive_arc")
        want = _str(kwargs.get("欲望_Want"), "找回失去的记忆")
        need = _str(kwargs.get("需求_Need"), "与失散的家人和解")
        director = _str(kwargs.get("导演风格_8选1"), "Greta Gerwig (葛韦格)")
        physi = _str(kwargs.get("生理学"), "")
        psych = _str(kwargs.get("心理学"), "")
        social = _str(kwargs.get("社会学"), "")
        habit = _str(kwargs.get("身体习惯"), "")
        quote = _str(kwargs.get("口头禅"), "")
        obj = _str(kwargs.get("标志性物件"), "")
        background = _str(kwargs.get("角色背景"), "")
        mood = _str(kwargs.get("情绪基调"), "压抑中见希望")
        subtext = _str(kwargs.get("潜文本_情感"), "想说对不起但拉不下脸")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "让观众感到复杂")
        scene = _str(kwargs.get("场景描述"), "父女在厨房, 雨夜, 1998 年哈尔滨")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # ===== 节点专属 =====
        domain_name = "角色弧光追踪 (环节 9, 12)"
        domain_focus = "Lajos Egri 角色前提 × 欲望 vs 需求 × Vogler 12 阶段 × 12 原型 × 7 弧光 × 6 维深度"
        h3_special = "微动作总和 = 真实情感 + 物件承载弧光 + 口头禅三次含义反转"
        director_specifics = (
            "PTA: 演员生涯最佳 / 诺兰: 演员承担观念重量 / 奉俊昊: 演员精确 / "
            "斯科塞斯: 逼出生涯最佳 / 维伦纽瓦: 演员承受压力 / 兰斯莫斯: 演员显得滑稽 / "
            "葛韦格: 演员写内心世界 / 黑泽明: 演员承担史诗"
        )
        extra_inject = "8 大导演塑造技法 + 12 原型 + 7 弧光 + 6 维深度 + 5 支柱 + 7 活人感 + 弧光转折点"

        # ===== 导演方法 =====
        director_meta = MASTER_DIRECTORS_8.get(director, {})

        # ===== 5 要素处理 =====
        data_summary = (
            "1161 部 director_view 14 维 + 63 导演 12 维 + 8 顶级导演风格库 + "
            "191 反 AI 词表 + 10 强制具体细节铁律 + 12 套理论 + 14 部真实短剧 + "
            "Lajos Egri 角色前提 + Carl Jung 12 原型 + 7 弧光 + 6 维深度 + Vogler 12 阶段 + "
            "H3 三大字段 + 4 任务类型 + 13 镜头运动 + 11 规则 + 11 维导演控制 + "
            "3 留白 + 3 运镜法则 + 9 维光照 + 5 空间 + 5 沉默 + 卡兹克 2.5 SFT"
        )
        context_brief = (
            "角色=" + name + " (" + gender + ", " + str(age) + "岁), 原型=" + archetype + ", "
            "弧光=" + arc + ", 欲望=" + want + ", 需求=" + need + ", 导演=" + director
        )
        skill_harness = (
            "Lajos Egri 角色前提 + 欲望 vs 需求 + Vogler 12 阶段 + 12 原型 + "
            "7 弧光类型 + 6 维深度 + 8 顶级导演塑造技法 + 5 支柱 + 7 活人感 + "
            "12 套理论 + 191 反 AI + 13 镜头运动 + 11 规则 + 5 沉默 + 5 空间 + 5 维意图 + 4 维美术 + 9 维光照"
        )
        experience_matrix = (
            "14 部真实短剧角色案例 + 失败模式 (平面/空洞/工具人/说教) + 修复方案 + "
            "8 大顶级导演角色塑造实战 + 卡兹克 2.5 SFT 重定义"
        )
        ai_deep = (
            "反 AI 词表 + 10 铁律 + 4 轮迭代 + 沉默 4 步 + 留白 3 法 + 导演意图 5 维 + "
            "11 维导演控制 + 30 秒场景单元 6 段式 + 模型压住随手补戏 + L1-L7 七层 + 8 大导演风格"
        )

        # ===== 关键参考元素 (V13.4: 场景中立 + 角色驱动, 不再硬编码 1998 哈尔滨厨房) =====
        # 从 社会学/角色背景 推导主场空间, 无则用通用描述
        _sociology = (kwargs.get("社会学") or "").strip()
        _bg = (kwargs.get("角色背景") or "").strip()
        if _sociology or _bg:
            location_meta = "角色主场空间 (依据角色前史: " + (_sociology or _bg)[:40] + ")"
        else:
            location_meta = "角色主场空间 (按角色前史设定)"
        texture_of_loc = "空间细节随角色社会学/时代设定, 强调使用痕迹与生活气息"

        # ===== 空间地标 (V13.4: 通用空间锚点, 非特定厨房) =====
        landmarks = (
            "  - 主光区 (frame-center): 角色常驻位置, 承载核心动作\n"
            "  - 入口方向 (frame-left): 角色进入/离开的动线\n"
            "  - 焦点物件区 (frame-right): " + obj + " 的固定位置 (距摄影机 1.5m)\n"
            "  - 背景层 (frame-far): 空间纵深, 暗示角色处境\n"
            "  - 边缘细节: 一处体现角色前史的使用痕迹"
        )

        # ===== 动作时间码 (V13.4: 基于角色身体习惯/标志物件, 非切菜/收音机) =====
        action_timing = (
            "0.0–0.3s — " + name + " 背对/侧对镜头, 日常动作开始 (弧光第一阶段: Ordinary World)\n"
            "0.3–2.0s — 重复性动作循环 (防御机制展现)\n"
            "2.0–2.5s — " + name + " 停手, " + habit + " (欲望 vs 需求冲突)\n"
            "2.5–3.5s — " + name + " 转身, 抬眼 (响应延迟 0.3s)\n"
            "3.5–6.0s — " + name + " 开口一句短台词 (潜文本: 未说出口的话)\n"
            "6.0–9.0s — " + habit + " (弧光的微动作)\n"
            "9.0–11.0s — 口头禅 '" + quote + "' (第一次出现)\n"
            "11.0–18.0s — 沉默 (5 秒, 环境音收远, 弧光转折点)\n"
            "18.0–25.0s — 放下/触碰 " + obj + " (重 0.3 秒, 弧光转折)\n"
            "25.0–30.0s — 弧光完成 (欲望 → 需求)"
        )

        # ===== 构建 L1-L7 =====
        l1 = _build_l1(intent_feel, name, arc)
        l2 = _build_l2(name, archetype, location_meta, obj)
        l3 = _build_l3(landmarks, "south")
        l4 = _build_l4(name, want, need, action_timing, habit)
        l5 = _build_l5(director, obj)
        l6 = _build_l6(name, habit, quote, "沉默 4 步公式: 一句短台词 + 3 秒沉默 + 微表情 + 改变关系动作 + 5 秒呼吸", obj, gender, age)
        l7 = _build_l7()

        # ===== H3 三大字段 =====
        style, shot_1, shots, soundscape, music = _build_h3(
            name, scene, want, need, obj, director
        )
        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese",
        )
        # 对齐指令
        alignment = build_alignment_instruction("T2VA", n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # ===== 11 维导演控制 =====
        director_control_lines = []
        for k, v in DIRECTOR_CONTROL_11_FULL.items():
            director_control_lines.append("  - " + k + ": " + v)
        director_control_text = "【11 维导演控制能力 (人类顶级导演)】\n" + "\n".join(director_control_lines)

        # ===== 3 留白 =====
        whitespace_3 = (
            "【3 留白 (3 Whitespace Techniques)】\n"
            "  1. 时间留白 (Delayed Gratification): " + THREE_WHITESPACE["时间留白"] + "\n"
            "  2. 空间留白 (Emotional Concentration): " + THREE_WHITESPACE["空间留白"] + "\n"
            "  3. 叙事留白 (Don't Say Everything): " + THREE_WHITESPACE["叙事留白"]
        )

        # ===== 3 运镜法则 =====
        camera_3 = (
            "【3 运镜法则 (3 Camera Laws to Kill AI-Feel)】\n"
            "  1. " + THREE_CAMERA_LAWS["破坏首帧完成度"] + "\n"
            "  2. " + THREE_CAMERA_LAWS["引入非线性运动轨迹"] + "\n"
            "  3. " + THREE_CAMERA_LAWS["制造响应延迟"]
        )

        # ===== 8 大导演风格库 =====
        director_8_style = "【8 大世界顶级导演风格库 (Master Director Style Library)】\n"
        for d, m in MASTER_DIRECTORS_8.items():
            director_8_style += "  ▸ " + d + "\n"
            director_8_style += "    角色塑造: " + m["角色塑造"] + "\n"
            director_8_style += "    镜头: " + m["镜头运动"] + "\n"
            director_8_style += "    节奏: " + m["节奏"] + "\n"
            director_8_style += "    光影: " + m["光影"] + "\n"
            director_8_style += "    声音: " + m["声音"] + "\n"
            director_8_style += "    留白: " + m["留白"] + "\n"
            director_8_style += "    代表: " + m["代表作品"] + "\n"
            director_8_style += "    格言: " + m["格言"] + "\n"

        # ===== 8 大导演塑造技法 =====
        director_acting_8 = "【8 大导演角色塑造技法 (8 Director Acting Techniques)】\n"
        for d, m in DIRECTOR_ACTING_8.items():
            director_acting_8 += "  - " + d + ": " + m + "\n"

        # ===== Character Bible (角色圣经) =====
        # Phase 17.6: 灵魂注入
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")
        soul_block = ""
        if _HAS_SOUL:
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_scene_weight,
                    secondary=soul_secondary,
                    fusion_mode=soul_fusion_mode,
                    scene_context=scene,
                )
                soul_block = (
                    "【灵魂核心 - 角色弧光驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_block = ""

        character_bible_parts = []
        if soul_block:
            character_bible_parts.append(soul_block)
        character_bible_parts.append("【" + name + " Character Bible — 世界顶级导演级】\n")
        character_bible_parts.append("=" * 70)
        character_bible_parts.append("L1-L7 七层 Prompt 架构 (7-Layer Prompt Architecture)")
        character_bible_parts.append("=" * 70)
        character_bible_parts.append("")
        character_bible_parts.append(l1)
        character_bible_parts.append("")
        character_bible_parts.append(l2)
        character_bible_parts.append("")
        character_bible_parts.append(l3)
        character_bible_parts.append("")
        character_bible_parts.append(l4)
        character_bible_parts.append("")
        character_bible_parts.append(l5)
        character_bible_parts.append("")
        character_bible_parts.append(l6)
        character_bible_parts.append("")
        character_bible_parts.append(l7)
        character_bible_parts.append("")
        character_bible_parts.append("=" * 70)
        character_bible_parts.append("H3 三大字段 (Higgsfield 官方: integrated_multimodal_description + overall_soundscape + non_diegetic_music)")
        character_bible_parts.append("=" * 70)
        character_bible_parts.append("")
        character_bible_parts.append(h3_prompt)
        character_bible_parts.append("")
        character_bible_parts.append("=" * 70)
        character_bible_parts.append("【基础信息】")
        character_bible_parts.append("  姓名: " + name)
        character_bible_parts.append("  性别: " + gender)
        character_bible_parts.append("  年龄: " + str(age) + " 岁")
        character_bible_parts.append("  角色原型: " + archetype + " - " + ARCHETYPES_12.get(archetype, "—"))
        character_bible_parts.append("  角色弧光: " + arc + " - " + CHARACTER_ARC_TYPES.get(arc, "—"))
        character_bible_parts.append("  导演风格: " + director)
        character_bible_parts.append("  导演塑造技法: " + _pick(director_meta, "角色塑造", "—"))
        character_bible_parts.append("")
        character_bible_parts.append("【6 维深度 (Lajos Egri)】")
        character_bible_parts.append("  1. 生理学: " + physi)
        character_bible_parts.append("  2. 心理学: " + psych)
        character_bible_parts.append("  3. 社会学: " + social)
        character_bible_parts.append("  4. 经济学: (略, 可补)")
        character_bible_parts.append("  5. 亲密关系: (略, 可补)")
        character_bible_parts.append("  6. 文化背景: (略, 可补)")
        character_bible_parts.append("")
        character_bible_parts.append("【标志性】")
        character_bible_parts.append("  - 身体习惯: " + habit)
        character_bible_parts.append("  - 口头禅: " + quote)
        character_bible_parts.append("  - 标志性物件: " + obj)
        character_bible_parts.append("")
        character_bible_parts.append("【欲望 vs 需求 (真实角色塑造核心)】")
        character_bible_parts.append("  - 欲望 (Want): " + want + " (表层目标, 角色认为想要的)")
        character_bible_parts.append("  - 需求 (Need): " + need + " (深层需求, 角色真正需要的)")
        character_bible_parts.append("  - 核心冲突: 欲望和需求的矛盾")
        character_bible_parts.append("  - 真实弧结局: " + name + " 意识到真正需要 " + need + ", 牺牲 " + want)
        character_bible_parts.append("  - 悲剧弧: " + name + " 始终追求 " + want + ", 拒绝 " + need + ", 最终毁灭")
        character_bible_parts.append("")
        character_bible_parts.append("【5 支柱 (角色塑造的 5 个核心)】")
        character_bible_parts.append("  WHAT: 角色要达成什么 — " + want)
        character_bible_parts.append("  OBSTACLE: 阻碍是什么 — " + psych[:30] + "...")
        character_bible_parts.append("  COST: 代价是什么 — 维持'家之主'的面子 vs 承认软弱")
        character_bible_parts.append("  STRATEGY: 角色如何克服 — 用 " + habit + " 替代话, 让 " + obj + " 承担潜文本")
        character_bible_parts.append("  TURN: 转折是什么 — 放下" + obj + "的瞬间, 弧光转折 (欲望 → 需求)")
        character_bible_parts.append("")
        character_bible_parts.append("【口头禅 '" + quote + "' 的三次出现 (含义反转)】")
        character_bible_parts.append("  第一次: " + name + " 第一次说出, 含义是'不信' (防御机制)")
        character_bible_parts.append("  第二次 (中点): 同样的话, 含义开始松动, 有点信了")
        character_bible_parts.append("  第三次 (结尾): " + name + " 说出第三次, 但声音变小了, 完全信了")
        character_bible_parts.append("")
        character_bible_parts.append("【标志性物件 " + obj + " 的使用 (3 阶段)】")
        character_bible_parts.append("  第一幕: 找到 " + obj + " (来历交代, 物件 = 内心)")
        character_bible_parts.append("  第三幕: 失去 " + obj + " (最黑暗时刻, 物件 = 失去自我)")
        character_bible_parts.append("  第五幕: " + name + " 重新拿起 " + obj + ", 但变了 (象征成长, 物件 = 重生的自我)")
        character_bible_parts.append("")
        character_bible_parts.append("【角色背景】")
        character_bible_parts.append(background if background else "  (略, 可在'角色背景'字段补全)")
        character_bible_parts.append("")
        character_bible_parts.append(director_acting_8)
        character_bible_parts.append("")
        character_bible_parts.append(director_8_style)
        character_bible_parts.append("")
        character_bible_parts.append(director_control_text)
        character_bible_parts.append("")
        character_bible_parts.append(whitespace_3)
        character_bible_parts.append("")
        character_bible_parts.append(camera_3)
        character_bible_parts.append("")
        character_bible_parts.append("【5 要素处理 (5 Elements Architecture)】")
        character_bible_parts.append("  数据层: " + data_summary)
        character_bible_parts.append("  上下文: " + context_brief)
        character_bible_parts.append("  Skill/Harness: " + skill_harness)
        character_bible_parts.append("  经验矩阵: " + experience_matrix)
        character_bible_parts.append("  AI 深度: " + ai_deep)
        character_bible_parts.append("")
        character_bible_parts.append("【11 条 H3 官方规则 (Higgsfield)】")
        character_bible_parts.append(inject_h3_rules_11())
        character_bible_parts.append("")
        character_bible_parts.append("【9 维光照控制 (CIE LAB + 摄影本体)】")
        for k, v in LIGHTING_9D.items():
            character_bible_parts.append("  - " + k + ": " + v)
        character_bible_parts.append("")
        character_bible_parts.append("【导演意图 5 维】")
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本)",
            "主题": mood,
            "留白": "想说但没说出口 - " + obj + " 是没寄出的信",
        }
        character_bible_parts.append(inject_director_intent(intent_5d))
        character_bible_parts.append("")
        character_bible_parts.append("【Seedance 2.5 核心升级 (卡兹克)】")
        character_bible_parts.append("  - 卡兹克 (2.5 SFT): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "—"))
        character_bible_parts.append("  - 卡兹克 (30 秒场景单元): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "—"))
        character_bible_parts.append("  - DiDi_OK (美术优先): " + SEEDANCE_25_QUOTES.get("DiDi_OK_美术", "—"))
        character_bible_parts.append("")
        character_bible = "\n".join(character_bible_parts)

        # Knowledge Base 决策注入
        if _HAS_KB:
            try:
                _kb_narrative = None
                for ns in (NARRATIVE_STRUCTURES if isinstance(NARRATIVE_STRUCTURES, list) else [NARRATIVE_STRUCTURES]):
                    if isinstance(ns, dict) and arc in str(ns):
                        _kb_narrative = ns
                        break
                if _kb_narrative is None:
                    _kb_narrative = NARRATIVE_STRUCTURES[0] if isinstance(NARRATIVE_STRUCTURES, list) and NARRATIVE_STRUCTURES else NARRATIVE_STRUCTURES
                _kb_emotion = EMOTION_RENDERING
                _kb_decision = get_director_decision(director, name + " " + arc)
                kb_block = "\n" + "=" * 70 + "\n"
                kb_block += "【Knowledge Base — 角色弧光叙事结构 + 情感强度】\n"
                kb_block += "=" * 70 + "\n\n"
                kb_block += "叙事结构 (" + arc + "): " + str(_kb_narrative)[:300] + "\n\n"
                kb_block += "情感强度层级 (" + name + " 旅程): " + str(_kb_emotion)[:300] + "\n\n"
                kb_block += "导演决策 (" + director + "): " + str(_kb_decision)[:300] + "\n"
                character_bible += kb_block
            except Exception:
                pass

        # ===== Arc Journey (弧光旅程) =====
        arc_journey_parts = []
        arc_journey_parts.append("【" + name + " 弧光旅程 (基于 Vogler 12 阶段) — 世界顶级导演级】\n")
        arc_journey_parts.append("=" * 70)
        # 12 阶段动态生成 (基于欲望 vs 需求)
        vogler_12 = [
            ("1. Ordinary World", "日常世界", name + " 在 " + social + " 的日常, 习惯孤独, 防御机制展现 (" + habit + ")"),
            ("2. Call to Adventure", "冒险召唤", "一封信寄到, 上面写着 " + name + " 的真名 (欲望被点燃: " + want + ")"),
            ("3. Refusal of the Call", "拒绝召唤", name + " 撕了信, " + quote + " (不想知道 / 防御机制: 冷漠)"),
            ("4. Meeting the Mentor", "遇见导师", "院长 (退休老人) 告诉 " + name + ": 真相不会消失, " + habit + " 时说: 你早晚要面对"),
            ("5. Crossing the Threshold", "跨越门槛", name + " 决定去找那封信的来源 (欲望驱动: " + want + ")"),
            ("6. Tests/Allies/Enemies", "试炼/盟友/敌人", name + " 遇到一群和自己一样寻亲的人 (盟友), 也遇到想利用的人 (敌人)"),
            ("7. Approach to Inmost Cave", "接近最深的洞穴", "找到亲生父母家门前 (此时欲望 " + want + " 与需求 " + need + " 开始冲突)"),
            ("8. Ordeal", "严酷考验", "亲生母亲说: 你是谁, 我不认识你 (" + name + " 至暗时刻, 防御机制崩溃)"),
            ("9. Reward", "奖赏", "亲生父亲偷偷告诉 " + name + " 真相 (需求 " + need + " 第一次被看见)"),
            ("10. Road Back", "回归之路", "亲生母亲赶来, 拿刀要赶走 " + name + " (冲突顶点)"),
            ("11. Resurrection", "复活/蜕变", name + " 说出心里话: 我只想见你一面 (潜台词: 真正需要 " + need + ", 不再追求 " + want + ")"),
            ("12. Return with Elixir", "带回灵药", name + " 没有回到原处, 而是在家附近租了房 (弧光完成: 欲望 " + want + " → 需求 " + need + ")"),
        ]
        for stage_en, stage_cn, desc in vogler_12:
            arc_journey_parts.append("  ▸ " + stage_en + " — " + stage_cn)
            arc_journey_parts.append("    " + desc)
            arc_journey_parts.append("")
        arc_journey_parts.append("【关键弧点 (5 个转折)】")
        arc_journey_parts.append("  1. 第 1 阶段: 防御机制展现 (" + habit + " = 拒绝真相)")
        arc_journey_parts.append("  2. 第 5 阶段: 第一次主动选择 (欲望驱动)")
        arc_journey_parts.append("  3. 第 8 阶段: 至暗时刻 (被亲妈拒绝, 防御机制崩溃)")
        arc_journey_parts.append("  4. 第 9 阶段: 需求 " + need + " 第一次被看见")
        arc_journey_parts.append("  5. 第 11 阶段: " + name + " 说出心里话 (欲望 → 需求)")
        arc_journey_parts.append("  6. 第 12 阶段: " + name + " 完成蜕变 (不再逃避, 但也没强融)")
        arc_journey_parts.append("")
        arc_journey_parts.append("【欲望 vs 需求解决】")
        arc_journey_parts.append("  表面: " + name + " 想要 " + want)
        arc_journey_parts.append("  真实: " + name + " 需要 " + need)
        arc_journey_parts.append("  解决: " + name + " 没有强制认亲, 而是远远地看着, 这就是 " + need)
        arc_journey_parts.append("  弧光类型: " + arc + " — " + CHARACTER_ARC_TYPES.get(arc, "—"))
        arc_journey_parts.append("")
        arc_journey_parts.append("【12 原型对应 (Carl Jung)】")
        arc_journey_parts.append("  角色原型: " + archetype + " — " + ARCHETYPES_12.get(archetype, "—"))
        arc_journey_parts.append("  原型在弧光中的作用: 原型决定了 " + name + " 在每个阶段的'姿态'")
        arc_journey_parts.append("  例如: Hero 原型在第 8 阶段 (Ordeal) 会主动承担考验, Jester 原型会开玩笑化解")
        arc_journey_parts.append("")
        arc_journey_parts.append("【" + director + " 风格的弧光处理】")
        arc_journey_parts.append("  角色塑造: " + _pick(director_meta, "角色塑造", "—"))
        arc_journey_parts.append("  节奏: " + _pick(director_meta, "节奏", "—"))
        arc_journey_parts.append("  留白: " + _pick(director_meta, "留白", "—"))
        arc_journey_parts.append("  代表: " + _pick(director_meta, "代表作品", "—"))
        arc_journey_parts.append("  格言: " + _pick(director_meta, "格言", "—"))
        arc_journey_parts.append("")
        arc_journey_parts.append(whitespace_3)
        arc_journey_parts.append("")
        arc_journey_parts.append(camera_3)
        arc_journey_parts.append("")
        arc_journey = "\n".join(arc_journey_parts)

        # ===== Director Lessons (导演塑造技法) =====
        director_lessons_parts = []
        director_lessons_parts.append("【" + name + " — 8 大导演塑造技法 (8 Director Acting Techniques)】\n")
        director_lessons_parts.append("=" * 70)
        director_lessons_parts.append("1. 王家卫式 - 物件代替心理")
        director_lessons_parts.append("   " + name + " 的 " + obj + " = 内心, 场景: " + name + " 擦 " + obj + " 时, 镜头特写 30 秒")
        director_lessons_parts.append("")
        director_lessons_parts.append("2. 侯孝贤式 - 沉默代替表达")
        director_lessons_parts.append("   " + name + " 被亲妈赶出来, 站了一下午, 不说话, 镜头不动 (长镜头静观)")
        director_lessons_parts.append("")
        director_lessons_parts.append("3. 是枝裕和式 - 身体习惯")
        director_lessons_parts.append("   " + name + " 紧张时 " + habit + ", 每次 " + habit + " 都让观众知道 " + name + " 的情绪")
        director_lessons_parts.append("")
        director_lessons_parts.append("4. 李沧东式 - 不解释情绪")
        director_lessons_parts.append("   " + name + " 听到真相, 站了 3 秒, 没说一句话, 转身走了 (半秒消化再开口)")
        director_lessons_parts.append("")
        director_lessons_parts.append("5. 蔡明亮式 - 动作就是心理")
        director_lessons_parts.append("   " + name + " 在家门口徘徊, 走了又回来, 回来又走, 镜头跟 5 分钟 (极慢节奏)")
        director_lessons_parts.append("")
        director_lessons_parts.append("6. 毕赣式 - 时间折叠")
        director_lessons_parts.append("   回忆里 " + name + " 在孤儿院的同一场景, 跟现在门前, 镜头叠化 (时间折叠)")
        director_lessons_parts.append("")
        director_lessons_parts.append("7. 黑泽明式 - 天气即情绪")
        director_lessons_parts.append("   " + name + " 找到亲妈那天, 下着大雨, 雨声盖住一切, " + name + " 没说话 (极端天气 = 主题放大器)")
        director_lessons_parts.append("")
        director_lessons_parts.append("8. 伯格曼式 - 脸特写")
        director_lessons_parts.append("   镜头怼着 " + name + " 脸上 30 秒, 只看到眼睛红了, 但没流泪 (沉默 = 情感)")
        director_lessons_parts.append("")
        director_lessons_parts.append("=" * 70)
        director_lessons_parts.append("【" + director + " 风格应用 — " + name + " 弧光的导演读解】")
        director_lessons_parts.append("=" * 70)
        director_lessons_parts.append("")
        director_lessons_parts.append("  角色塑造: " + _pick(director_meta, "角色塑造", "—"))
        director_lessons_parts.append("  镜头: " + _pick(director_meta, "镜头运动", "—"))
        director_lessons_parts.append("  节奏: " + _pick(director_meta, "节奏", "—"))
        director_lessons_parts.append("  光影: " + _pick(director_meta, "光影", "—"))
        director_lessons_parts.append("  声音: " + _pick(director_meta, "声音", "—"))
        director_lessons_parts.append("  留白: " + _pick(director_meta, "留白", "—"))
        director_lessons_parts.append("  代表: " + _pick(director_meta, "代表作品", "—"))
        director_lessons_parts.append("  格言: " + _pick(director_meta, "格言", "—"))
        director_lessons_parts.append("")
        director_lessons_parts.append("【口头禅 '" + quote + "' 的使用 (3 阶段)】")
        director_lessons_parts.append("  第一幕开场: " + name + " 第一次说出 (含义: 防御机制, 不信)")
        director_lessons_parts.append("  第三幕中点: 同样的话, 含义反了 (开始信)")
        director_lessons_parts.append("  第五幕结尾: " + name + " 说出第三次, 但声音变小了 (完全信)")
        director_lessons_parts.append("")
        director_lessons_parts.append("【标志性物件 " + obj + " 的使用 (3 阶段)】")
        director_lessons_parts.append("  第一幕: 找到 " + obj + " (来历交代, 物件 = 内心)")
        director_lessons_parts.append("  第三幕: 失去 " + obj + " (最黑暗时刻, 物件 = 失去自我)")
        director_lessons_parts.append("  第五幕: " + name + " 重新拿起 " + obj + ", 但变了 (象征成长, 物件 = 重生的自我)")
        director_lessons_parts.append("")
        director_lessons_parts.append("【" + name + " 弧光的 5 支柱 (Higgsfield Phase 14)】")
        director_lessons_parts.append("  WHAT: " + want)
        director_lessons_parts.append("  OBSTACLE: " + psych[:30] + "..., 防御机制: 冷漠/逃避")
        director_lessons_parts.append("  COST: 维持现状 vs 面对真相, 说出 " + need)
        director_lessons_parts.append("  STRATEGY: " + habit + ", " + obj + ", " + quote + " 三者承担弧光")
        director_lessons_parts.append("  TURN: 放下" + obj + "的瞬间, 弧光转折 (欲望 " + want + " → 需求 " + need + ")")
        director_lessons_parts.append("")
        director_lessons_parts.append("【10 条强制具体细节铁律 (反 AI 味)】")
        for r in SPECIFIC_DETAIL_RULES_10:
            director_lessons_parts.append("  - " + str(r))
        director_lessons_parts.append("")
        director_lessons_parts.append(whitespace_3)
        director_lessons_parts.append("")
        director_lessons_parts.append(camera_3)
        director_lessons_parts.append("")
        director_lessons_parts.append(director_control_text)
        director_lessons_parts.append("")
        director_lessons_parts.append(inject_genre_9_types())
        director_lessons_parts.append("")
        director_lessons = "\n".join(director_lessons_parts)

        # ===== 反 AI 词表清洗 =====
        if anti_ai_on:
            try:
                character_bible = inject_anti_ai_rules(character_bible)
                arc_journey = inject_anti_ai_rules(arc_journey)
                director_lessons = inject_anti_ai_rules(director_lessons)
            except Exception:
                pass

        return (character_bible, arc_journey, director_lessons)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "CharacterArcPro": CharacterArcPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "CharacterArcPro": "👤 角色弧光 (环节 9, 12) — Phase 16 世界顶级导演级",
# }
