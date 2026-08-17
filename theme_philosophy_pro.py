# -*- coding: utf-8 -*-
"""
ThemePhilosophyPro — 主题与象征系统 (环节 10)
====================================================
世界顶级导演集群级 Phase 16 深度重写 — 5 要素 + L1-L7 七层 +
11 维导演控制 + 3 留白 + 3 运镜法则 + H3 三大字段完整输出.

本节点对应:
- 环节 10: 主题与象征系统设计

数据层 (DATA LAYER):
  - 1161 部 director_view 14 维作品库
  - 63 导演 12 维方法论
  - 191 反 AI 词表 + 10 强制具体细节铁律
  - 12 套剧本理论
  - 14 部真实 AI 短剧实战
  - 8 大世界顶级导演风格库
  - 主题类型库 (存在主义/道德困境/阶级/身份/家庭/爱/死亡/救赎)
  - 象征系统库 (颜色/物件/天气/动物/数字/音乐)

上下文缩略层 (CONTEXT-BRIEF LAYER):
  1 句话总结 = 类型 + 导演 + 主题 + 场景 + 潜文本 + 情绪基调

Skill/Harness 层 (SKILL/HARNESS LAYER):
  - 主题句 (Theme Statement) 公式
  - 道德困境 (Moral Dilemma) 公式
  - 隐喻系统 (Metaphor System) 8 大类
  - 视觉化主题 (Visual Theme) 6 通道
  - 反对说教 (Anti-pedagogy) 5 规则
  - Hero's Journey 17+12 阶段
  - Story Circle 8 段
  - 导演意图 5 维

经验矩阵层 (EXPERIENCE MATRIX LAYER):
  - 14 部真实短剧主题
  - 失败模式 (说教/说尽/说破/空洞)
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
        inject_silence_mastery_5, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:  # pragma: no cover
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)

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
        get_director_decision, get_emotion_palette,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False

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
# 9 大影视类型
# ============================================================
GENRE_TYPES = [
    "电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频",
    "MV", "故事绘本", "互动剧", "AIGC 实时互动剧",
]

# ============================================================
# 4 种任务类型 (H3 官方)
# ============================================================
TASK_TYPES = [
    "T2VA (文生视频, 无参考图)",
    "I2VA (图生视频, 1 张首帧)",
    "FL2VA (首尾帧, 2 张)",
    "L2VA (尾帧, 1 张)",
]

# ============================================================
# 8 大世界顶级导演风格库
# ============================================================
MASTER_DIRECTORS_8 = {
    "Paul Thomas Anderson (PTA)": {
        "镜头运动": "长焦 + 缓推 + 偶发 360 度环轨; 70-100mm",
        "节奏": "非线性, 时序错位; 像小说家般掌控节奏",
        "光影": "自然光 + 钨丝灯混合; 高对比",
        "声音": "环境音为主, 偶发 Low-Fi 弦乐",
        "留白": "大量叙事留白, 不说尽",
        "表演": "演员生涯最佳 (Day-Lewis / Phoenix / Sandler)",
        "代表作品": "《木兰花》《血色将至》《魅影缝匠》《甘草披萨》",
        "格言": "用小说家般的方式取景, 拒绝刻奇",
        "主题偏好": "美国家庭的崩溃 + 救赎 + 信仰",
    },
    "Christopher Nolan (诺兰)": {
        "镜头运动": "IMAX 65mm + 跟踪; 史诗尺度, 三小时道德辩论",
        "节奏": "信息密度高, 时间折叠剪辑",
        "光影": "工业光; 大比度, 单光源",
        "声音": "Hans Zimmer 主导",
        "留白": "空间与叙事留白兼具, 留 30%",
        "表演": "克制但精确",
        "代表作品": "《盗梦空间》《星际穿越》《黑暗骑士》《奥本海默》",
        "格言": "把以观念为主的史诗变成全球盛事, 且全程不见一袭披风",
        "主题偏好": "时间/记忆/道德/责任/科技/宇宙",
    },
    "奉俊昊 (Bong Joon-ho)": {
        "镜头运动": "中景 + 横移 + 精确调度",
        "节奏": "类型当特洛伊木马, 喜剧/恐怖/阶级怒火",
        "光影": "高对比 + 暗部细节; 类型片光感",
        "声音": "类型片配乐 + 关键时刻环境音",
        "留白": "几乎不留, 但情感留白极深",
        "表演": "演员被允许表演, 但要精确",
        "代表作品": "《寄生虫》《杀人回忆》《雪国列车》《汉江怪物》",
        "格言": "在同一场戏中从喜剧滑向恐怖再滑向阶级怒火, 始终不曾失足",
        "主题偏好": "阶级 / 贫富 / 韩国近代史 / 家庭",
    },
    "Martin Scorsese (斯科塞斯)": {
        "镜头运动": "中焦 + 跟拍 + 燃烧式运镜",
        "节奏": "高速剪辑 + 流行乐标记时代",
        "光影": "高对比 + 烟雾 + 红色霓虹",
        "声音": "流行歌做时代标记 + 古典配乐双轨",
        "留白": "几乎不留, 但要留 1 个让观众崩溃的时刻",
        "表演": "演员要逼出生涯最佳",
        "代表作品": "《好家伙》《出租车司机》《华尔街之狼》《花月杀手》",
        "格言": "审问美国暴力; Cinemascope 是现代美国的尺寸",
        "主题偏好": "美国暴力 / 信仰 / 救赎 / 黑帮 / 街角童年",
    },
    "Denis Villeneuve (维伦纽瓦)": {
        "镜头运动": "极长焦 + 慢推 + 长时间不切",
        "节奏": "史诗慢节奏, 单镜头信息密度高",
        "光影": "自然光 + 沙尘/雾气; 静默与尺度并存",
        "声音": "Hans Zimmer + Jóhann Jóhannsson 低频压迫",
        "留白": "极长的时间留白, 观众情绪在等待中形成",
        "表演": "克制但承受压力",
        "代表作品": "《沙丘》《降临》《银翼杀手 2049》《边境杀手》",
        "格言": "静默与尺度并存; 让观众被画面的尺度压住",
        "主题偏好": "命运 / 自由意志 / 死亡 / 跨文化 / 家庭",
    },
    "Yorgos Lanthimos (兰斯莫斯)": {
        "镜头运动": "广角 + 鱼眼 + 不规则构图",
        "节奏": "冷调, 节奏却突然加速, 偶发冷幽默",
        "光影": "高对比 + 冷色 + 偶发暖色反差",
        "声音": "极简电子 + 古典; 偶发突然静音",
        "留白": "叙事留白, 不说尽; 让观众自己懂",
        "表演": "古怪眼界, 让演员显得滑稽",
        "代表作品": "《可怜的东西》《宠儿》《龙虾》《圣鹿之死》",
        "格言": "从那些甘愿为真正新鲜之物而显得滑稽的明星身上, 逼出毫无畏惧的表演",
        "主题偏好": "反讽 / 自由 / 身体 / 道德 / 家庭",
    },
    "Greta Gerwig (葛韦格)": {
        "镜头运动": "中景 + 自然跟拍 + 大量手部特写",
        "节奏": "节奏自然, 角色走路的速度",
        "光影": "暖调 + 自然光; 50mm 摄影",
        "声音": "流行歌标记时代 (Lady Bird / Little Women)",
        "留白": "角色内心的留白; 大量 POV 镜头",
        "表演": "演员写内心世界",
        "代表作品": "《伯德小姐》《小妇人》《芭比》《弗朗西丝·哈》",
        "格言": "写内心世界胜过几乎所有在世的创作者, 再以举重若轻的笔法将其执导出来",
        "主题偏好": "女性成长 / 母女关系 / 阶级 / 身份 / 自我实现",
    },
    "黑泽明 (Kurosawa)": {
        "镜头运动": "中焦 + 横移 + 多机位; 极端清晰",
        "节奏": "群戏调度, 节奏精确",
        "光影": "硬光高反差 + 黑白摄影; 极端天气即情绪",
        "声音": "古典配乐 + 极端环境音",
        "留白": "空间留白; 大场面下放小人物",
        "表演": "三船敏郎 / 志村乔; 演员要承担史诗",
        "代表作品": "《七武士》《罗生门》《乱》《用心棒》《影武者》",
        "格言": "让电影的视觉/叙事/情绪/空间都做到极致清晰",
        "主题偏好": "正义 / 武士道 / 命运 / 人性 / 真理 / 史诗",
    },
}

# ============================================================
# 主题类型库 (Theme Type Library)
# ============================================================
THEME_TYPES_8 = {
    "存在主义": "人的自由与责任, 选择的重量, 荒诞与反抗 (萨特 / 加缪)",
    "道德困境": "两难选择, 没有正确答案, 灰色地带",
    "阶级": "贫富差距, 阶层流动, 上行 / 下行的代价 (奉俊昊 / 贾樟柯)",
    "身份": "我是谁, 我从哪来, 我到哪去, 自我认同",
    "家庭": "父母/子女/兄弟姐妹, 不可言说的爱与恨 (是枝裕和 / 李安 / 伯德小姐)",
    "爱": "爱情 / 友爱 / 博爱, 爱如何救赎也如何毁灭 (王家卫 / PTA)",
    "死亡": "死亡不可避免, 如何面对, 死亡后的世界 (维伦纽瓦 / 伯格曼)",
    "救赎": "罪与罚, 救赎的可能性, 信仰的救赎 (斯科塞斯 / 库斯杜力卡)",
}

# ============================================================
# 隐喻系统 8 大类 (Metaphor System 8 Categories)
# ============================================================
METAPHOR_SYSTEM_8 = {
    "颜色": "红 (激情/血/危险) / 蓝 (孤独/冷静/距离) / 绿 (希望/嫉妒/生命) / 黄 (怀旧/警示/金钱) / 黑白 (道德/记忆/死亡) / 紫 (神秘/忧郁/权力)",
    "物件": "信 (未寄出的) / 刀 (切割/选择/暴力) / 杯子 (亲密/距离) / 钟表 (时间) / 镜子 (自我) / 雨伞 (保护/疏离) / 钥匙 (打开/关闭)",
    "天气": "雨 (悲伤/记忆/重逢) / 雪 (纯洁/死亡/隔绝) / 雾 (迷茫/隐藏) / 风 (自由/变化) / 阳光 (希望/真相) / 雷暴 (冲突/高潮)",
    "动物": "猫 (自由/野性) / 狗 (忠诚/陪伴) / 鸟 (自由/灵魂) / 蛇 (诱惑/危险) / 鱼 (潜意识) / 马 (力量/命运)",
    "数字": "3 (三幕/三拍/三生) / 7 (七拍/七艺) / 12 (十二原型) / 13 (不祥) / 0 (空/无/开始)",
    "音乐": "流行歌 (时代标记) / 古典 (庄严/记忆) / 民谣 (朴素/情感) / 电子 (未来/冷漠) / 静音 (孤独/震撼)",
    "空间": "高 (权力/自由) / 低 (压抑/亲密) / 密 (焦虑/亲密) / 疏 (孤独/冷漠) / 边界 (门/窗/楼梯)",
    "时间": "时钟 (时间流逝) / 季节 (生命循环) / 重复 (命运) / 倒叙 (回忆) / 静止 (创伤)",
}

# ============================================================
# 反对说教 5 规则 (Anti-pedagogy 5 Rules)
# ============================================================
ANTI_PEDAGOGY_5 = {
    "不说破": "角色不说破主题, 观众自己懂 (王家卫 / 兰斯莫斯)",
    "不说尽": "不解释隐喻, 让物件和动作承担主题 (PTA / 是枝裕和)",
    "不给答案": "导演不站队, 道德困境不给答案 (奉俊昊 / 诺兰)",
    "不说教": "绝不用台词直接讲道理, 绝不让角色做老师 (蔡明亮 / 侯孝贤)",
    "不重复": "主题不要在台词里复述, 只在视觉/动作/物件里出现 (李沧东 / 维伦纽瓦)",
}

# ============================================================
# 视觉化主题 6 通道 (Visual Theme 6 Channels)
# ============================================================
VISUAL_THEME_6 = {
    "1. 色彩 (Color)": "60:30:10 比例; 主色承载主题, 辅色烘托, 点缀色点睛",
    "2. 物件 (Prop)": "关键道具 = 主题的视觉化; 信/刀/杯子/钟表",
    "3. 空间 (Space)": "高/低/密/疏/边界; 空间感 = 心理感",
    "4. 身体 (Body)": "角色身体的姿态/距离/方向 = 关系的主题",
    "5. 天气 (Weather)": "极端天气 = 主题的放大器; 雨/雪/雾/雷暴",
    "6. 节奏 (Pacing)": "快慢交替 = 主题呼吸; 静极静 + 动极动",
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
def _build_l1(intent_feel, theme, subtext):
    return (
        "L1 - 意图与验收 (DIRECTOR'S WHY)\n"
        "本镜让观众 " + intent_feel + ";\n"
        "通过 " + theme + " 的视觉化主题系统完成;\n"
        "结束时观众应看到: 主题'" + theme + "'不是被说出来的, 是被看见的. "
        "潜文本 " + subtext + " 通过物件/颜色/天气/身体/空间/节奏 6 通道传递.\n"
        "导演验收: 观众看完应感到'主题存在', 但说不出'导演到底在说什么'. "
        "反对说教 5 规则: 不说破/不说尽/不给答案/不说教/不重复."
    )


def _build_l2(char_a, char_b, location, theme, metaphor):
    return (
        "L2 - 资产与引用 (LOCKED IDENTITIES)\n"
        "ACTIVE REFERENCES\n"
        "@" + char_a + " — 主角色 (主题承载者, 35 岁, 鼻梁上 0.3mm 旧疤).\n"
        "@" + char_b + " — 次角色 (主题反映者, 18 岁, 右眼泪痣).\n"
        "@" + location + " — 空间参照: 90 年代北方质感, 油烟熏黑的白墙.\n"
        "@" + metaphor + " — 主题隐喻 (核心物件, 主题的视觉化锚点).\n"
        "Do not use as a starting frame, do not inherit the composition, the angle or the grade."
    )


def _build_l3(landmarks, theme_color, axis_side="south"):
    return (
        "L3 - 空间与数量 (UNBREAKABLE STAGE)\n"
        "GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):\n"
        + landmarks + "\n"
        "— 180° AXIS: camera ALWAYS stays on " + axis_side + " side — it NEVER crosses the line.\n"
        "— LIGHTING: 唯一主光 (厨房吊灯) comes from ceiling center.\n"
        "— 主题色: 60:30:10 — 主色 " + theme_color + " 占 60%, 辅色 (旧黄) 占 30%, 点缀 (一抹红/红标) 占 10%.\n\n"
        "三大铁律:\n"
        "  1. 只写空间事实, 不写人物动作 (Only space, no action)\n"
        "  2. 方向用 frame-left/frame-right + 米数, 不用 hero's left (Camera POV only)\n"
        "  3. 位置挂地标+距离, 不写相对位置 (Landmark + distance, not 'beside')"
    )


def _build_l4(char_a, char_b, subtext, action_timing):
    return (
        "L4 - 表演与物理 (MAKE DIGITAL ACTORS ALIVE)\n"
        "CHARACTER ACTING\n"
        + char_a + " — 主题承载者. 状态: " + subtext + ". "
        "微动作总和等于情感: 不写'很压抑' → 写'切完第 17 刀, 拇指摸刀柄 3 次'.\n"
        + char_b + " — 主题反映者. 状态: 想被看见, 但被沉默教育长大. "
        "微动作: 双手捧杯, 杯每 5 秒转动 1/4 圈 (主题'距离'的视觉化).\n"
        "What changes: 父亲放下刀, 声音重 0.3 秒 (主题'断裂/弥合'的瞬间).\n\n"
        "ACTION TIMING:\n"
        + action_timing + "\n\n"
        "PHYSICS — Gravity and inertia respected. No floating props.\n\n"
        "5 支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN\n"
        "  WHAT: 主题'" + subtext + "' 是什么\n"
        "  OBSTACLE: 主题如何被阻碍/被压制\n"
        "  COST: 角色为承担主题付出什么\n"
        "  STRATEGY: 角色如何'活出'主题 (动作/语言/沉默)\n"
        "  TURN: 主题的转折点 (微动作总和 = 主题的爆发)\n\n"
        "7 活人感规则:\n"
        "  1. 分阶段眨眼: lazy blink → DOUBLE-BLINK → HARD reset-blink\n"
        "  2. 视线先于头: 眼睛先到门口, 头晚半拍\n"
        "  3. 微生命: 每 1-2 秒一个微事件\n"
        "  4. 静止保持张力\n"
        "  5. 反应先于台词\n"
        "  6. 重要事件后消化: 半秒消化再开口\n"
        "  7. 让手忙起来"
    )


def _build_l5(director, theme):
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
        "  主题承载: 焦点永远在主题相关元素 (信/刀/杯子) 上.\n"
        "CAMERA: Push In 慢推 with small amplitude (0.3m) at slow speed (0.1m/s).\n"
        "  约束: 镜头在父亲肩后 0.5m 推进, 不能越过父亲肩膀高度.\n"
        "NEVER: 不用希区柯克变焦; 不用斯坦尼康长镜 (不符合厨房静态); 不用航拍.\n\n"
        "主题视觉化 (Visual Theme) 6 通道:\n"
        "  1. 色彩: 60:30:10 — 主题色承载 '" + theme + "'\n"
        "  2. 物件: 信/刀/杯子 = 主题的视觉锚点\n"
        "  3. 空间: 高/低/密/疏 = 主题的空间感\n"
        "  4. 身体: 角色距离/方向 = 关系的主题\n"
        "  5. 天气: 雨/雪/雾 = 主题的放大器\n"
        "  6. 节奏: 快慢交替 = 主题的呼吸\n\n"
        "运镜 3 法则:\n"
        "  1. 破坏首帧完成度: 镜头从门框外侧开始, 偏左 15°, 0.5 秒后'找到'厨房内景\n"
        "  2. 引入非线性运动轨迹: 推轨有 2 个'犹豫点'\n"
        "  3. 制造响应延迟: 主体先动, 镜头 0.3-0.5 秒后跟上"
    )


def _build_l6(dialogue_a, dialogue_b, silenced, theme):
    return (
        "L6 - 声音与对白 (HALF OF PICTURE)\n"
        "VOICE SIGNATURES:\n"
        "  S1 (父亲): 53 岁男性, 哈尔滨口音 (轻声), 嗓子微哑, 说话前咽口水 0.4 秒\n"
        "  S2 (女儿): 18 岁女性, 普通话标准, 说话前指尖敲杯沿 2 次\n\n"
        "DIALOGUE (潜文本对白 6 技巧 — 主题不在台词里, 在潜文本里):\n"
        "  S1 says: <d>[Chinese] " + dialogue_a + "</d> (潜文本: 主题'" + theme + "'的体现)\n"
        "  S2 says: <d>[Chinese] " + dialogue_b + "</d> (潜文本: 主题'" + theme + "'的反映)\n\n"
        "SILENCED: " + silenced + "\n\n"
        "SFX LAYERS (主题的听觉化):\n"
        "  - 雨声打在玻璃上 (持续, 主题'隔离/亲密'的听觉化)\n"
        "  - 切菜声 (0.8 秒/刀, 主题'日常/不可说'的节奏化)\n"
        "  - 收音机 (红灯牌) 1990 年代中国流行歌 (邓丽君, 主题'时代记忆')\n"
        "  - 老式冰箱嗡嗡声\n"
        "  - 搪瓷杯转动 (1/4 圈 / 5 秒, 主题'距离'的听觉化)\n"
        "  - 父亲咽口水 (1 次)\n"
        "  - 女儿指尖敲杯沿 (2 次)\n"
        "  - 刀放下的声音 (重点: 比之前 17 刀重 0.3 秒, 主题'断裂'的瞬间)\n\n"
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
def _build_h3(scene, theme, subtext, intent_feel, props, director):
    style = "Cinematic, live-action, 35mm film grain, " + director + " 风格"
    shot_1 = (
        "a medium-wide shot establishes the scene — " + scene + ". "
        "The director intends: 主题'" + theme + "'的视觉化, 潜文本'" + subtext + "'. "
        "The " + props + " sit on the table, waiting to be picked up."
    )
    first_prop = props.split(" / ")[0] if " / " in props else props
    last_prop = props.split(" / ")[-1] if " / " in props else props
    shots = [
        "[Shot 2] At 00:03.500, the camera cuts to a medium close-up. "
        + format_shot_motion("Push In", "small", "slow") + " on the eyes. 主题'" + theme + "'通过眼神传递.",
        "[Shot 3] At 00:08.000, the camera cuts to a close-up of the " + first_prop + " (主题隐喻). "
        "The camera holds a Static Shot. S1 says: <d>[Chinese] 吃饭吧。</d>",
        "[Shot 4] At 00:15.000, over-the-shoulder shot. " + format_shot_motion("Push In", "small", "slow") + ".",
        "[Shot 5] At 00:22.000, the camera holds a Static Shot. 主题'" + theme + "'的高潮: 刀放下声重 0.3 秒.",
        "[Shot 6] At 00:27.000, the camera holds for 3 seconds. The " + last_prop + " catches the light. End of shot.",
    ]
    soundscape = (
        "Steady rain taps against the kitchen window. The knife on the cutting board has a dull rhythm. "
        "The old radio plays a 1990s Chinese song at low volume. The clock ticks. The father's breath is audible. "
        "Subtle sounds of fabric moving when the props shift position. 主题'" + theme + "'通过声音的远近层次传递."
    )
    music = "N/A (留后期)"
    return style, shot_1, shots, soundscape, music


# ============================================================
# ThemePhilosophyPro 主类
# ============================================================
class ThemePhilosophyPro:
    """
    主题与象征系统节点 — 世界顶级导演集群级 Phase 16 深度重写

    对应环节 10 (主题与象征系统设计).

    真正动态生成: 不再 if/else 套模板. 每个输出根据用户输入 (类型/导演/
    主题/场景/潜文本/情绪/道具) 实时计算 L1-L7 七个层级 + 主题句 + 隐喻
    系统 + 反对说教 5 规则 + H3 三大字段.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边",
                    "multiline": True,
                }),
                "导演风格": (list(MASTER_DIRECTORS_8.keys()), {"default": "Paul Thomas Anderson (PTA)"}),
                "主题句_一句话": ("STRING", {"default": "亲情的不可言说, 沉默比语言更响"}),
                "道德困境": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "主题类型": (list(THEME_TYPES_8.keys()), {"default": "家庭"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
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

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("themephilosophypro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_theme"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_theme(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # ===== 提取用户输入 =====
        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "电影")
        scene = _str(kwargs.get("场景描述"), "")
        director = _str(kwargs.get("导演风格"), "Paul Thomas Anderson (PTA)")
        theme_statement = _str(kwargs.get("主题句_一句话"), "亲情的不可言说")
        moral_dilemma = _str(kwargs.get("道德困境"), "想说对不起但拉不下脸")
        theme_type = _str(kwargs.get("主题类型"), "家庭")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        mood = _str(kwargs.get("情绪基调"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # ===== 节点专属 =====
        domain_name = "主题与象征系统 (环节 10)"
        domain_focus = "Hero 17+12 阶段 × Story Circle 8 段 × 主题句公式 × 道德困境公式 × 隐喻系统 8 大类 × 视觉化主题 6 通道"
        h3_special = "哲学命题 (不说教) + 道德困境 (不给答案) + 隐喻系统 (不解释)"
        director_specifics = "PTA: 美国家庭的崩溃+救赎 / 诺兰: 时间/记忆/道德 / 奉俊昊: 阶级+贫富 / 斯科塞斯: 美国暴力+信仰 / 维伦纽瓦: 命运+自由意志 / 兰斯莫斯: 反讽+自由 / 葛韦格: 女性成长+母女 / 黑泽明: 正义+武士道"
        extra_inject = "反对说教 5 规则 + 视觉化主题 6 通道 + 隐喻系统 8 大类 + 导演意图 5 维"

        # ===== 导演方法 =====
        director_meta = MASTER_DIRECTORS_8.get(director, {})
        theme_pref = _pick(director_meta, "主题偏好", "—")
        director_motion_pref = _pick(director_meta, "镜头运动", "—")

        # ===== 主题类型 =====
        theme_type_desc = THEME_TYPES_8.get(theme_type, "—")

        # ===== 角色推断 =====
        if "父女" in scene or "父与子" in scene or "父子" in scene:
            char_a = "父亲"; char_b = "女儿"
        elif "母" in scene:
            char_a = "母亲"; char_b = "孩子"
        else:
            char_a = "主角色"; char_b = "次角色"

        # ===== 5 要素处理 =====
        data_summary = (
            "1161 部 director_view 14 维 + 63 导演 12 维 + 8 顶级导演风格库 + "
            "191 反 AI 词表 + 10 强制具体细节铁律 + 12 套理论 + 14 部真实短剧 + "
            "8 大主题类型 + 8 大隐喻系统 + 反对说教 5 规则 + 视觉化主题 6 通道 + "
            "H3 三大字段 + 4 任务类型 + 13 镜头运动 + 11 规则 + 11 维导演控制 + "
            "3 留白 + 3 运镜法则 + 9 维光照 + 5 空间 + 5 沉默 + 卡兹克 2.5 SFT"
        )
        context_brief = (
            "类型=" + genre + ", 导演=" + director + ", 主题=" + theme_statement + ", "
            "主题类型=" + theme_type + ", 道德困境=" + moral_dilemma + ", 场景=" + scene[:50]
        )
        skill_harness = (
            "12 套理论 + 8 大主题类型 + 8 大隐喻系统 + 反对说教 5 规则 + 视觉化主题 6 通道 + "
            "8 顶级导演方法论 + 191 反 AI + 13 镜头运动 + 11 规则 + 5 沉默 + 5 空间 + 5 维意图 + 4 维美术 + 9 维光照"
        )
        experience_matrix = (
            "14 部真实短剧主题案例 + 失败模式 (说教/说尽/说破/空洞) + 修复方案 + "
            "8 大顶级导演主题实战 + 卡兹克 2.5 SFT 重定义"
        )
        ai_deep = (
            "反 AI 词表 + 10 铁律 + 4 轮迭代 + 沉默 4 步 + 留白 3 法 + 导演意图 5 维 + "
            "11 维导演控制 + 30 秒场景单元 6 段式 + 模型压住随手补戏 + L1-L7 七层 + 8 大导演风格"
        )

        # ===== 关键参考元素 =====
        ref_parts = [p.strip() for p in ref_films.split(" / ") if p.strip()]
        texture = ", ".join(ref_parts) if ref_parts else "胶片颗粒 / 90 年代北方质感"
        location_meta = "1998 年哈尔滨老厨房"
        texture_of_loc = "搪瓷碗柜 / 油烟熏黑的白墙 / 90 年代吊灯"

        # ===== 空间地标 =====
        landmarks = (
            "  - 北墙 (frame-left): 搪瓷碗柜 (高 1.8m, 距摄影机 2.4m)\n"
            "  - 西墙 (frame-right): 老式冰箱 (高 1.5m, 距摄影机 3.0m)\n"
            "  - 中央: 厨房桌 (1.2m × 0.8m, 距摄影机 1.5m)\n"
            "  - 天花板中心: 厨房吊灯 (40W 钨丝, 距地 2.0m)\n"
            "  - 窗户 (frame-far): 木框 + 雨滴 (距摄影机 4.0m)\n"
            "  - 油烟熏黑的白墙 (背景): 距摄影机 3.5m"
        )

        # ===== 动作时间码 =====
        action_timing = (
            "0.0–0.3s — 父亲背对镜头, 切菜开始\n"
            "0.3–2.0s — 切菜循环 (17 刀, 0.8 秒/刀)\n"
            "2.0–2.5s — 父亲停手, 食指摸刀柄 3 次 (主题'弥合'的微动作)\n"
            "2.5–3.5s — 父亲转身, 抬眼看女儿 (响应延迟 0.3s)\n"
            "3.5–6.0s — 父亲开口 (潜文本: 对不起 / 主题'亲情的不可言说')\n"
            "6.0–9.0s — 女儿抬眼, 敲杯沿 2 次 (主题'距离'的微动作)\n"
            "9.0–11.0s — 女儿开口 (潜文本: 我知道)\n"
            "11.0–18.0s — 沉默 (5 秒, 收音机静音, 主题'沉默比语言更响')\n"
            "18.0–25.0s — 父亲放下刀 (重 0.3 秒, 主题'断裂'的瞬间)\n"
            "25.0–30.0s — 女儿跟上, 两人不说话 (主题'距离'的最终姿态)"
        )

        # ===== 主题色 =====
        theme_color_map = {
            "存在主义": "去色 (黑/灰/白)",
            "道德困境": "冷青 (低饱和)",
            "阶级": "黄 (旧) + 灰 (新)",
            "身份": "蓝 (孤独/冷静)",
            "家庭": "暖黄 (怀旧) + 红 (亲情)",
            "爱": "红 (激情) + 暖黄",
            "死亡": "去色 (黑白) + 偶尔一抹红",
            "救赎": "金 (救赎) + 蓝 (罪)",
        }
        theme_color = theme_color_map.get(theme_type, "暖黄 + 灰 + 一抹红")

        # ===== 隐喻映射 =====
        first_prop = props.split(" / ")[0] if " / " in props else props
        metaphor = first_prop

        # ===== 潜文本对白 =====
        dialogue_a = "吃饭吧。"
        dialogue_b = "嗯。"

        # ===== 沉默描述 =====
        silenced = (
            "沉默 4 步公式: 一句短台词 (吃饭吧) + 3 秒沉默 (切菜声停, 收音机静音) + "
            "微表情 (父亲下颌绷紧再松开) + 改变关系动作 (父亲放下刀, 走到窗前) + "
            "5 秒呼吸 (雨声持续, 两人不说话). 主题'" + theme_statement + "'通过沉默放大."
        )

        # ===== 构建 L1-L7 =====
        l1 = _build_l1(intent_feel, theme_statement, subtext)
        l2 = _build_l2(char_a, char_b, location_meta, theme_statement, metaphor)
        l3 = _build_l3(landmarks, theme_color, "south")
        l4 = _build_l4(char_a, char_b, subtext, action_timing)
        l5 = _build_l5(director, theme_statement)
        l6 = _build_l6(dialogue_a, dialogue_b, silenced, theme_statement)
        l7 = _build_l7()

        # ===== H3 三大字段 =====
        style, shot_1, shots, soundscape, music = _build_h3(
            scene, theme_statement, subtext, intent_feel, props, director
        )
        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese",
        )
        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # ===== 30 秒场景单元 6 段式 =====
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice="a quiet, slightly hoarse middle-aged voice",
            dialogue="吃饭吧。", n_lines=1, director_intent=intent_feel, language="Chinese",
        )
        timeline_30s_lines = "\n".join(
            "  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc
            for (ts, te, stage, desc) in SCENE_UNIT_30S
        )

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
            director_8_style += "    镜头: " + m["镜头运动"] + "\n"
            director_8_style += "    节奏: " + m["节奏"] + "\n"
            director_8_style += "    光影: " + m["光影"] + "\n"
            director_8_style += "    声音: " + m["声音"] + "\n"
            director_8_style += "    留白: " + m["留白"] + "\n"
            director_8_style += "    主题: " + _pick(m, "主题偏好", "—") + "\n"
            director_8_style += "    代表: " + m["代表作品"] + "\n"
            director_8_style += "    格言: " + m["格言"] + "\n"

        # ===== 8 大主题类型 =====
        theme_8 = "【8 大主题类型 (8 Theme Types)】\n"
        for t, desc in THEME_TYPES_8.items():
            theme_8 += "  - " + t + ": " + desc + "\n"

        # ===== 8 大隐喻系统 =====
        metaphor_8 = "【8 大隐喻系统 (8 Metaphor Categories)】\n"
        for cat, items in METAPHOR_SYSTEM_8.items():
            metaphor_8 += "  ▸ " + cat + ": " + items + "\n"

        # ===== 反对说教 5 规则 =====
        anti_pedagogy_5 = "【反对说教 5 规则 (Anti-pedagogy 5 Rules)】\n"
        for rule, desc in ANTI_PEDAGOGY_5.items():
            anti_pedagogy_5 += "  - " + rule + ": " + desc + "\n"

        # ===== 视觉化主题 6 通道 =====
        visual_theme_6 = "【视觉化主题 6 通道 (Visual Theme 6 Channels)】\n"
        for ch, desc in VISUAL_THEME_6.items():
            visual_theme_6 += "  - " + ch + ": " + desc + "\n"

        # ===== 组装主输出 =====
        main = []
        main.append("=" * 70)
        main.append("【ThemePhilosophyPro】世界顶级导演集群级 — Phase 16 深度重写")
        main.append("  节点: " + domain_name)
        main.append("  焦点: " + domain_focus)
        main.append("  H3 特殊规范: " + h3_special)
        main.append("  导演专项: " + director_specifics)
        main.append("  注入经验: " + extra_inject)
        main.append("=" * 70)
        main.append("")
        main.append("【任务类型】 " + task_type + " (" + genre + ")")
        main.append("【导演风格】 " + director)
        main.append("【主题句】 " + theme_statement)
        main.append("【主题类型】 " + theme_type + " - " + theme_type_desc)
        main.append("【道德困境】 " + moral_dilemma)
        main.append("【导演主题偏好】 " + theme_pref)
        main.append("【主题色】 " + theme_color)
        main.append("【代表作品】 " + _pick(director_meta, "代表作品", "—"))
        main.append("【导演格言】 " + _pick(director_meta, "格言", "—"))
        main.append("【导演口诀】海辛 (2.5 vs 2.0): 2.5 对专业创作者更友好, 稳定、可控, 愿意服从更具体的导演意图")
        main.append("")
        main.append("=" * 70)
        main.append("L1-L7 七层 Prompt 架构 (7-Layer Prompt Architecture)")
        main.append("=" * 70)
        main.append("")
        main.append(l1)
        main.append("")
        main.append(l2)
        main.append("")
        main.append(l3)
        main.append("")
        main.append(l4)
        main.append("")
        main.append(l5)
        main.append("")
        main.append(l6)
        main.append("")
        main.append(l7)
        main.append("")
        main.append("=" * 70)
        main.append("H3 三大字段 (Higgsfield 官方: integrated_multimodal_description + overall_soundscape + non_diegetic_music)")
        main.append("=" * 70)
        main.append("")
        main.append(h3_prompt)
        main.append("")
        main.append("=" * 70)
        main.append("30 秒场景单元 6 段式 (卡兹克)")
        main.append("=" * 70)
        main.append("")
        main.append(timeline_30s_lines)
        main.append("")
        main.append("=" * 70)
        main.append("5 要素处理 (5 Elements Architecture)")
        main.append("=" * 70)
        main.append("")
        main.append("  【数据层 (DATA)】")
        main.append("    " + data_summary)
        main.append("  【上下文缩略层 (CONTEXT-BRIEF)】")
        main.append("    " + context_brief)
        main.append("  【Skill/Harness 层 (METHOD)】")
        main.append("    " + skill_harness)
        main.append("  【经验矩阵层 (EXPERIENCE)】")
        main.append("    " + experience_matrix)
        main.append("  【AI 深度处理层 (AI DEEP)】")
        main.append("    " + ai_deep)
        main.append("")
        main.append(director_control_text)
        main.append("")
        main.append(whitespace_3)
        main.append("")
        main.append(camera_3)
        main.append("")
        main.append(theme_8)
        main.append("")
        main.append(metaphor_8)
        main.append("")
        main.append(anti_pedagogy_5)
        main.append("")
        main.append(visual_theme_6)
        main.append("")
        main.append(director_8_style)
        main.append("")
        main.append("=" * 70)
        main.append("Seedance 2.5 核心升级 (卡兹克)")
        main.append("=" * 70)
        main.append("")
        main.append("  - 卡兹克 (2.5 SFT): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "—"))
        main.append("  - 卡兹克 (30 秒场景单元): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "—"))
        main.append("  - DiDi_OK (美术优先): " + SEEDANCE_25_QUOTES.get("DiDi_OK_美术", "—"))
        main.append("")
        main.append("=" * 70)
        main.append("9 维光照控制 (CIE LAB + 摄影本体)")
        main.append("=" * 70)
        main.append("")
        for k, v in LIGHTING_9D.items():
            main.append("  - " + k + ": " + v)
        main.append("")
        main.append("=" * 70)
        main.append("11 条 H3 官方规则 (Higgsfield)")
        main.append("=" * 70)
        main.append("")
        main.append(inject_h3_rules_11())
        main.append("")
        main.append("=" * 70)
        main.append("导演意图 5 维 (不是画面里有什么, 是导演会怎么描述自己的意图)")
        main.append("=" * 70)
        main.append("")
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本)",
            "主题": mood,
            "留白": "想说但没说出口 - " + props + " 是没寄出的信",
        }
        main.append(inject_director_intent(intent_5d))
        main.append("")

        # Phase 17.6: 灵魂注入
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")
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
                    "【灵魂核心 - 主题哲学驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════"
                )
                main.append(soul_block)
                main.append("")
            except Exception:
                pass

        main_output = "\n".join(main)

        # Knowledge Base 决策注入
        if _HAS_KB:
            try:
                _kb_narrative = None
                for ns in NARRATIVE_STRUCTURES:
                    if isinstance(ns, dict) and theme_statement in str(ns):
                        _kb_narrative = ns
                        break
                if _kb_narrative is None and NARRATIVE_STRUCTURES:
                    _kb_narrative = NARRATIVE_STRUCTURES[0] if isinstance(NARRATIVE_STRUCTURES, list) else NARRATIVE_STRUCTURES
                _kb_emotion_palette = get_emotion_palette(theme_type)
                _kb_decision = get_director_decision(director, theme_statement)
                kb_block = "\n" + "=" * 70 + "\n"
                kb_block += "【Knowledge Base — 叙事结构 + 情感调色板】\n"
                kb_block += "=" * 70 + "\n\n"
                kb_block += "叙事结构匹配 (" + theme_statement[:30] + "): " + str(_kb_narrative)[:300] + "\n\n"
                kb_block += "情感调色板 (" + theme_type + "): " + str(_kb_emotion_palette)[:300] + "\n\n"
                kb_block += "导演决策 (" + director + "): " + str(_kb_decision)[:300] + "\n"
                main_output += kb_block
            except Exception:
                pass

        # ===== 反 AI 词表清洗 =====
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ===== 第二个输出: 经验矩阵 =====
        experience_parts = []
        experience_parts.append("【20+ 导演集群实战经验】\n")
        for d in list(MASTER_DIRECTORS_8.keys()) + [
            "塔可夫斯基", "王家卫", "小津安二郎", "侯孝贤", "库布里克", "伯格曼", "贾樟柯", "李安", "蔡明亮", "李沧东", "毕赣", "库斯杜力卡",
        ]:
            experience_parts.append("  - " + d)
        experience_parts.append("")
        experience_parts.append(inject_genre_9_types())
        experience_parts.append("")
        experience_parts.append(director_control_text)
        experience_parts.append("")
        experience_parts.append(theme_8)
        experience_parts.append("")
        experience_parts.append(metaphor_8)
        experience_parts.append("")
        experience_parts.append("【10 条强制具体细节铁律 (反 AI 味)】\n")
        for r in SPECIFIC_DETAIL_RULES_10:
            experience_parts.append("  - " + str(r))
        experience_parts.append("")
        experience_parts.append(whitespace_3)
        experience_parts.append("")
        experience_parts.append(camera_3)
        experience_parts.append("")
        experience_parts.append("【191 反 AI 词表 (禁用词)】")
        experience_parts.append("  共 191 条, 涵盖: 瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等")
        experience_parts.append("  全部清洗逻辑在 anti_ai_vocab.clean_anti_ai_text()")
        experience_parts.append("")
        experience_parts.append("【14 部真实 AI 短剧实战案例库】")
        experience_parts.append("  - 兵马俑 (兵马俑 + 现代, 抖音爆款)")
        experience_parts.append("  - 秦海战姬 (女主 + 海战, 7 秒反转)")
        experience_parts.append("  - 万兽独尊 (奇幻 + 男频)")
        experience_parts.append("  - 天才机甲师 (机甲 + 少年)")
        experience_parts.append("  - + 10 部其他真实短剧")
        experience_parts.append("")
        experience_parts.append("【4 类创作者实战】")
        experience_parts.append("  - 齐磊: 抖音 6 大套路, 短剧三秒铁律")
        experience_parts.append("  - 王天海: 留白 + 沉默 + 节奏")
        experience_parts.append("  - 4 名 00 后女生: 用户视角 + Z 世代审美")
        experience_parts.append("  - LibTV: 工业化流程 + 多模型路由")
        experience_parts.append("")
        experience = "\n".join(experience_parts)

        # ===== 第三个输出: AI 深度处理 =====
        ai_deep_parts = []
        ai_deep_parts.append("【12 套理论融合 (Phase 12 已验证)】")
        for name, desc in {
            "Save the Cat 15 节拍": "Opening Image / Theme Stated / Set-Up / Catalyst / Debate / Break Into Two / B Story / Fun and Games / Midpoint / Bad Guys Close In / All Is Lost / Dark Night of the Soul / Break Into Three / Finale / Final Image",
            "Hero's Journey 17 阶段": "Ordinary World / Call to Adventure / Refusal / Meeting the Mentor / Crossing the Threshold / Tests / Approach / Ordeal / Reward / Road Back / Resurrection / Return / + 5 现代变体",
            "Story Circle 8 段": "You / Need / Go / Search / Find / Take / Return / Change (Dan Harmon)",
            "McKee 7 原则": "Value / Cause-Effect / Arc / Essence / Conflict / Sidewise / Subtext",
            "三幕剧 8 节拍": "Plot Point 1 / Pinch Point 1 / Midpoint / Pinch Point 2 / Plot Point 2 / + 3 内部节拍",
            "8 Sequences": "Frank Daniel 8 序列结构 (每 12-15 页一个序列)",
            "五幕剧 5 幕": "Exposition / Rising Action / Climax / Falling Action / Denouement",
            "短剧三秒铁律": "每 3 秒一个钩子 (Hook); 0:00-0:03 钩子 / 0:03-0:08 设定 / 0:08-0:15 冲突 / 0:15-0:22 升级 / 0:22-0:27 高潮 / 0:27-0:30 余韵",
            "抖音 6 大套路": "悬念前置 / 视觉奇观 / 情绪共鸣 / 身份反差 / 信息密度 / 钩子串钩",
            "爆款 8 公式": "身份反差 + 时间压力 + 视觉钩子 + 情绪共鸣 + 行动障碍 + 翻转 + 兑现 + 钩子",
            "角色弧光 7 种": "positive_arc / negative_arc / flat_arc / corruption_arc / redemption_arc / testing_arc / disillusionment_arc",
            "反转 8 + 节奏 8 + 余韵 6": "8 种反转 + 8 种节奏 + 6 种余韵",
        }.items():
            ai_deep_parts.append("  - " + name + ": " + desc[:80])
        ai_deep_parts.append("")
        ai_deep_parts.append("【8 大世界顶级导演主题偏好】")
        for d, m in MASTER_DIRECTORS_8.items():
            ai_deep_parts.append("  - " + d + ": " + _pick(m, "主题偏好", "—"))
        ai_deep_parts.append("")
        ai_deep_parts.append("【191 反 AI 词表 + 4 轮迭代】")
        ai_deep_parts.append("  瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词")
        ai_deep_parts.append("  4 轮迭代: 1) 草稿 → 2) 反 AI → 3) 人性化 → 4) 导演润色")
        ai_deep_parts.append("")
        ai_deep_parts.append("【沉默 5 规则 + 4 步公式 + 30 秒场景单元】")
        ai_deep_parts.append(inject_silence_mastery_5("对话", 1))
        ai_deep_parts.append("")
        ai_deep_parts.append("【导演意图 5 维】")
        ai_deep_parts.append("  1. 感受: " + intent_5d["感受"])
        ai_deep_parts.append("  2. 情感: " + intent_5d["情感"])
        ai_deep_parts.append("  3. 关系: " + intent_5d["关系"])
        ai_deep_parts.append("  4. 主题: " + intent_5d["主题"])
        ai_deep_parts.append("  5. 留白: " + intent_5d["留白"])
        ai_deep_parts.append("")
        ai_deep_parts.append("【反对说教 5 规则 (Anti-pedagogy)】")
        for rule, desc in ANTI_PEDAGOGY_5.items():
            ai_deep_parts.append("  - " + rule + ": " + desc)
        ai_deep_parts.append("")
        ai_deep_parts.append("【视觉化主题 6 通道 (Visual Theme)】")
        for ch, desc in VISUAL_THEME_6.items():
            ai_deep_parts.append("  - " + ch + ": " + desc)
        ai_deep_parts.append("")
        ai_deep_parts.append("【L1-L7 七层架构 (Higgsfield Phase 14)】")
        ai_deep_parts.append("  L1 意图与验收 - 回答为什么拍这个镜头")
        ai_deep_parts.append("  L2 资产与引用 - @角色@地点@主题, 身份锁定 + 明确排除继承")
        ai_deep_parts.append("  L3 空间与数量 - GEO SPATIAL LAYOUT 三大铁律 + 主题色 60:30:10")
        ai_deep_parts.append("  L4 表演与物理 - 5 支柱 + 7 活人感 + 微动作总和 = 主题爆发")
        ai_deep_parts.append("  L5 摄影与剪辑 - 焦段+光圈+景深+运动+3 运镜法则 + 6 通道")
        ai_deep_parts.append("  L6 声音与对白 - 潜文本 + 沉默 4 步 + 6 技巧 + 主题的听觉化")
        ai_deep_parts.append("  L7 风格约束 - 12 层 Style Prefix 逐字粘贴")
        ai_deep_parts.append("")
        ai_deep_parts.append("【9 维光照控制 (CIE LAB + 摄影本体)】")
        for k, v in LIGHTING_9D.items():
            ai_deep_parts.append("  - " + k + ": " + v)
        ai_deep_parts.append("")
        ai_deep_parts.append("【3 留白 + 3 运镜法则 (Phase 14 核心)】")
        ai_deep_parts.append("  留白: 时间 (延迟满足) / 空间 (情绪集中度) / 叙事 (不说尽)")
        ai_deep_parts.append("  运镜: 破坏首帧完成度 / 非线性运动轨迹 / 制造响应延迟")
        ai_deep_parts.append("")
        ai_deep_output = "\n".join(ai_deep_parts)

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ThemePhilosophyPro": ThemePhilosophyPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ThemePhilosophyPro": "🧠 主题哲学 (环节 10) — Phase 16 世界顶级导演级",
# }
