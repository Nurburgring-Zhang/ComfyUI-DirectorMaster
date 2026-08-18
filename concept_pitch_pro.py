# -*- coding: utf-8 -*-
"""
ConceptPitchPro — 概念立项与故事架构 (环节 1-3, 6-7)
=====================================================
世界顶级导演集群级 (Paul Thomas Anderson / Christopher Nolan / 奉俊昊 /
Martin Scorsese / Denis Villeneuve / Yorgos Lanthimos / Greta Gerwig /
黑泽明 / 库斯杜力卡 / 塔可夫斯基 / 约阿希姆·提尔 / 王家卫) Phase 17 灵魂注入重写 —

5 要素 + L1-L7 七层 + 11 维导演控制 + 3 留白 + 3 运镜法则 + H3 三大字段
+ 48 情感矩阵 + 7 融合公式 + 10 灵魂维度 + 灵魂状态计算

本节点对应:
- 环节 1: 创意构思与概念开发
- 环节 2: 市场与受众分析 (隐含)
- 环节 3: 故事大纲与世界观构建
- 环节 6: 剧本结构规划
- 环节 7: 场景分解与节拍表

【灵魂注入哲学 — Phase 17】
AI 不会有真正的"灵魂" (个人、欲望、创伤、叛逆)
但可以用情感矩阵 + 融合算法 + 灵魂维度来极限模拟顶级导演的"灵魂"
让所有其他节点能接收灵魂注入

数据层 (DATA LAYER):
  - 1161 部 director_view 14 维作品库
  - 63 导演 12 维方法论
  - 191 反 AI 词表 + 10 强制具体细节铁律
  - 12 套剧本理论
  - 14 部真实 AI 短剧实战
  - 4 类创作者实战
  - 48 情感矩阵 (Plutchik + Izard + 复杂情感 + 状态情感)
  - 7 情感融合公式 (F1-F7)
  - 10 灵魂维度 (创造力/想象力/艺术表达/镜头语言/氛围掌控/精神状态/灵感/叛逆/怀疑/突破)
  - 灵魂状态 (灵感指数/疲劳指数/怀疑指数/叛逆指数)

上下文缩略层 (CONTEXT-BRIEF LAYER):
  1 句话总结 = 类型 + 导演 + 主题 + 场景 + 潜文本 + 情绪基调 + 灵魂融合

Skill/Harness 层 (SKILL/HARNESS LAYER):
  - Save the Cat 15 节拍 (Blake Snyder)
  - Hero's Journey 17 阶段 + 12 阶段
  - McKee 7 原则
  - 3 幕剧 8 节拍
  - 8 Sequences (Frank Daniel)
  - 五幕剧
  - 12 原型
  - 角色弧光 7 种
  - 8 顶级导演风格库
  - 灵魂融合公式 (F1-F7)
  - 灵魂维度映射

经验矩阵层 (EXPERIENCE MATRIX LAYER):
  - 14 部真实短剧案例库
  - 失败模式库
  - 修复方案库
  - 灵魂状态案例 (灵感时刻/自我怀疑/突破勇气)

AI 深度处理层 (AI DEEP PROCESSING LAYER):
  - 191 反 AI 词表清洗
  - 10 强制具体细节铁律
  - L1-L7 七层动态拼装 (灵魂注入)
  - 11 维导演控制 (灵魂映射)
  - 3 留白 (时间/空间/叙事) + 灵魂状态
  - 3 运镜法则 (破坏首帧/非线性轨迹/响应延迟) + 灵魂状态
  - H3 三大字段 (灵魂增强)
"""

import os
import sys
import json
import time
import random
import math

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

# Phase 5.0: 知识库深度集成
try:
    from knowledge_base import (
        GENRE_PROFILES, NARRATIVE_STRUCTURES, EMOTION_RENDERING,
        get_director_decision, get_emotion_palette,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False

# Phase 5.0.2: 533 导演统一数据库
try:
    from director_data_unified import get_director_profile
    _HAS_DIRECTOR_DB = True
except Exception:
    _HAS_DIRECTOR_DB = False

# ============================================================
# 灵魂注入 — Phase 17 核心
# ============================================================
try:
    from director_soul import (
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
        fuse_emotions,
        build_soul_injection,
        compute_soul_state,
        DirectorSoulNode,
    )
    _HAS_SOUL = True
except Exception:  # pragma: no cover
    _HAS_SOUL = False


# ============================================================
# 9 大影视类型 (9 Genre Types) — 向后兼容
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
# 20 导演集群 (向后兼容 - Phase 12 已使用)
# ============================================================
DIRECTORS_20 = [
    "塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和",
    "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安",
    "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰",
    "Papi酱", "诺兰_短剧版",
]

# ============================================================
# 8 大世界顶级导演风格库 (8 Master Director Style Library)
# 灵魂驱动版 — Phase 17
# 王家卫 / 诺兰 / PTA / 奉俊昊 / 黑泽明 / 库斯杜力卡 / 塔可夫斯基 / 约阿希姆·提尔
# ============================================================
MASTER_DIRECTORS_8 = {
    "Paul Thomas Anderson (PTA)": {
        "镜头运动": "长焦 + 缓推 + 偶发 360 度环轨; 喜欢在人物腰部高度, 70-100mm 拍摄",
        "节奏": "非线性, 时序错位, 但不张扬; 像小说家般掌控节奏, 一部一个声调",
        "光影": "自然光 + 钨丝灯混合; 高对比; 安纳摩根 (Robert Elswit) 风格",
        "声音": "环境音为主, 偶发 Low-Fi 弦乐; 从不喧宾夺主",
        "留白": "大量叙事留白, 不说尽, 人物通过沉默和动作表达",
        "表演": "演员生涯最佳 (Daniel Day-Lewis / Joaquin Phoenix / Adam Sandler)",
        "代表作品": "《木兰花》《血色将至》《魅影缝匠》《甘草披萨》《不羁之夜》",
        "格言": "用小说家般的方式取景, 拒绝刻奇",
        "灵魂签名": "D1创造力=0.95, D2想象力=0.90, D3艺术表达=0.95, D4镜头=0.90, D5氛围=0.92",
        "灵魂倾向情感": ["joy_ecstasy", "hate", "remorse", "disgust_revulsion", "sadness_grief"],
    },
    "Christopher Nolan (诺兰)": {
        "镜头运动": "IMAX 65mm + 跟踪 + 偶发固定; 史诗尺度, 道德辩论三小时像惊悚片",
        "节奏": "信息密度高, 时间折叠剪辑, 决不拖沓",
        "光影": "工业光 (Wally Pfister / Hoyte van Hoytema); 大比度, 单光源",
        "声音": "Hans Zimmer 主导, 配乐驱动 (Inception 铜管 / Dunkirk 滴答声)",
        "留白": "空间留白与叙事留白兼具, 留 30% 给观众思考",
        "表演": "克制但精确, 演员要承担观念重量",
        "代表作品": "《盗梦空间》《星际穿越》《黑暗骑士》《奥本海默》《敦刻尔克》《信条》",
        "格言": "把以观念为主的史诗变成全球盛事, 且全程不见一袭披风",
        "灵魂签名": "D1创造力=0.92, D2想象力=0.97, D3艺术表达=0.85, D4镜头=0.93, D5氛围=0.90",
        "灵魂倾向情感": ["awe", "fear_apprehension", "anticipation_vigilance", "wonder", "surprise_amazement"],
    },
    "奉俊昊 (Bong Joon-ho)": {
        "镜头运动": "中景 + 横移 + 精确调度; 同一场戏从喜剧滑向恐怖再滑向阶级怒火",
        "节奏": "类型当特洛伊木马, 节奏控制大师",
        "光影": "高对比 + 暗部细节; 类型片光感",
        "声音": "类型片配乐, 但关键时刻切到环境音",
        "留白": "几乎不留, 但情感留白极深",
        "表演": "演员被允许表演, 但要精确 (宋康昊 / 李善均)",
        "代表作品": "《寄生虫》《杀人回忆》《雪国列车》《汉江怪物》《母亲》《玉子》",
        "格言": "在同一场戏中从喜剧滑向恐怖再滑向阶级怒火, 始终不曾失足",
        "灵魂签名": "D1创造力=0.93, D2想象力=0.88, D3艺术表达=0.92, D4镜头=0.88, D5氛围=0.91",
        "灵魂倾向情感": ["disgust_loathing", "tension", "shame", "guilt", "anger_fury"],
    },
    "Martin Scorsese (斯科塞斯)": {
        "镜头运动": "中焦 + 跟拍 + 燃烧式运镜; 90 年代长镜头 + 后期加速",
        "节奏": "高速剪辑 + 流行乐标记时代 (Goodfellas 滚石 / Wolf of Wall Street)",
        "光影": "高对比 + 烟雾 + 红色霓虹",
        "声音": "流行歌做时代标记 + 古典配乐双轨",
        "留白": "几乎不留, 但要留 1 个让观众崩溃的时刻",
        "表演": "演员要逼出生涯最佳 (De Niro / DiCaprio / Pesci)",
        "代表作品": "《好家伙》《出租车司机》《愤怒的公牛》《华尔街之狼》《花月杀手》《爱尔兰人》",
        "格言": "审问美国暴力; Cinemascope 是现代美国的尺寸",
        "灵魂签名": "D1创造力=0.88, D2想象力=0.85, D3艺术表达=0.93, D4镜头=0.90, D5氛围=0.89",
        "灵魂倾向情感": ["anger_fury", "guilt", "shame", "hate", "remorse"],
    },
    "Denis Villeneuve (维伦纽瓦)": {
        "镜头运动": "极长焦 + 慢推 + 长时间不切; 把镜头保持到远超寻常导演会切走的时刻之后",
        "节奏": "史诗慢节奏, 单镜头信息密度高",
        "光影": "自然光 + 沙尘 / 雾气; 静默与尺度并存",
        "声音": "Hans Zimmer + Jóhann Jóhannsson 低频压迫",
        "留白": "极长的时间留白, 观众情绪在等待中形成",
        "表演": "克制但承受压力 (Ryan Gosling / Timothée Chalamet / Amy Adams)",
        "代表作品": "《沙丘》《降临》《银翼杀手 2049》《边境杀手》《焦土之城》《囚徒》",
        "格言": "静默与尺度并存; 让观众被画面的尺度压住",
        "灵魂签名": "D1创造力=0.90, D2想象力=0.95, D3艺术表达=0.93, D4镜头=0.95, D5氛围=0.96",
        "灵魂倾向情感": ["awe", "wonder", "loneliness", "despair", "trust_surrender"],
    },
    "Yorgos Lanthimos (兰斯莫斯)": {
        "镜头运动": "广角 + 鱼眼 + 不规则构图; 像一面怪镜",
        "节奏": "冷调, 节奏却突然加速, 偶发冷幽默",
        "光影": "高对比 + 冷色 + 偶发暖色反差",
        "声音": "极简电子 + 古典; 偶发突然静音",
        "留白": "叙事留白, 不说尽; 让观众自己懂",
        "表演": "古怪眼界, 让演员显得滑稽 (Olivia Colman / Emma Stone / Jesse Plemons)",
        "代表作品": "《可怜的东西》《宠儿》《龙虾》《圣鹿之死》《阿尔卑斯》",
        "格言": "从那些甘愿为真正新鲜之物而显得滑稽的明星身上, 逼出毫无畏惧的表演",
        "灵魂签名": "D1创造力=0.96, D2想象力=0.92, D3艺术表达=0.90, D4镜头=0.85, D5氛围=0.88",
        "灵魂倾向情感": ["contempt", "disgust_dislike", "surprise_astonishment", "shyness", "disapproval"],
    },
    "Greta Gerwig (葛韦格)": {
        "镜头运动": "中景 + 自然跟拍 + 大量手部特写; 像观察内心世界",
        "节奏": "节奏自然, 角色走路的速度",
        "光影": "暖调 + 自然光; 50mm 摄影",
        "声音": "流行歌标记时代 (Lady Bird / Little Women)",
        "留白": "角色内心的留白; 大量 POV 镜头",
        "表演": "Saoirse Ronan / Timothée Chalamet / Florence Pugh; 演员写内心世界",
        "代表作品": "《伯德小姐》《小妇人》《芭比》《弗朗西丝·哈》",
        "格言": "写内心世界胜过几乎所有在世的创作者, 再以举重若轻的笔法将其执导出来",
        "灵魂签名": "D1创造力=0.85, D2想象力=0.88, D3艺术表达=0.92, D4镜头=0.85, D5氛围=0.90",
        "灵魂倾向情感": ["bittersweet", "tenderness", "nostalgia", "shyness", "optimism"],
    },
    "黑泽明 (Kurosawa)": {
        "镜头运动": "中焦 + 横移 + 多机位; 极端的视觉/叙事/情绪/空间清晰",
        "节奏": "群戏调度, 节奏精确",
        "光影": "硬光高反差 + 黑白摄影; 极端天气即情绪",
        "声音": "古典配乐 + 极端环境音 (雨声/刀声/风)",
        "留白": "空间留白; 大场面下放小人物",
        "表演": "三船敏郎 / 志村乔; 演员要承担史诗",
        "代表作品": "《七武士》《罗生门》《乱》《用心棒》《影武者》《梦》",
        "格言": "让电影的视觉/叙事/情绪/空间都做到极致清晰",
        "灵魂签名": "D1创造力=0.91, D2想象力=0.87, D3艺术表达=0.94, D4镜头=0.92, D5氛围=0.93",
        "灵魂倾向情感": ["anger_frustration", "pride", "disapproval", "fear_apprehension", "vigilance"],
    },
    "王家卫 (Wong Kar-wai)": {
        "镜头运动": "广角 + 手持 + 慢快门; 雨夜霓虹 + 60 年代慢节奏 + 0.5 倍速世界",
        "节奏": "慢节奏, 时间断裂, 标点符号般精确的节奏控制",
        "光影": "彩色霓虹 + 城市光; 蓝/绿/红的色彩游戏",
        "声音": "流行歌 (Diane Keaton, 邓丽君) + 城市环境音 + 偶发弦乐",
        "留白": "时间留白 (skip time) + 叙事留白 (不说破)",
        "表演": "演员要像在梦游 (梁朝伟 / 张曼玉 / 金城武 / 王菲)",
        "代表作品": "《花样年华》《重庆森林》《春光乍泄》《阿飞正传》《一代宗师》《繁花》",
        "格言": "在 0.5 倍速的世界里, 爱情比正常人慢半拍地开始",
        "灵魂签名": "D1创造力=0.95, D2想象力=0.94, D3艺术表达=0.97, D4镜头=0.90, D5氛围=0.95",
        "灵魂倾向情感": ["longing", "nostalgia", "loneliness", "love", "bittersweet"],
    },
    "塔可夫斯基 (Tarkovsky)": {
        "镜头运动": "极长镜头 (5-10 分钟); 跟人物走, 不切; 慢推, 像一只凝视的眼睛",
        "节奏": "时间即主角; 一秒可以被拉伸为 10 分钟",
        "光影": "自然光 + 水 + 火 + 蒸汽; 半透明, 像记忆的质地",
        "声音": "水声 / 钟声 / 风 / 几乎不用配乐",
        "留白": "极致的留白; 不解释, 让观众在画面里住下来",
        "表演": "极少的对白, 大量凝视, 演员要能承受长镜头的重量",
        "代表作品": "《飞向太空》《镜子》《潜行者》《牺牲》《乡愁》《安德烈·卢布廖夫》",
        "格言": "电影的形象, 严格地讲, 应当是时间的形象, 而非运动的形象",
        "灵魂签名": "D1创造力=0.94, D2想象力=0.98, D3艺术表达=0.96, D4镜头=0.97, D5氛围=0.98",
        "灵魂倾向情感": ["trust_surrender", "despair", "loneliness", "wonder", "longing"],
    },
    "库斯杜力卡 (Kusturica)": {
        "镜头运动": "广角 + 手持跟拍 + 偶尔航拍; 像在吉普赛马戏团里奔跑的镜头",
        "节奏": "热闹 + 突然静默; 音乐家般掌握节奏",
        "光影": "暖色 + 自然光 + 偶尔黄昏逆光; 巴尔干的金黄",
        "声音": "手风琴 / 小提琴 / 铜管 / 民族音乐 + 偶尔突然完全静音",
        "留白": "少说; 沉默即情感; 让音乐说话",
        "表演": "群戏 + 即兴 + 演员写角色; 让群演活起来",
        "代表作品": "《地下》《流浪者之歌》《黑猫白猫》《亚利桑纳之梦》《爸爸去出差》",
        "格言": "塞尔维亚的乡愁是吉普赛马戏团, 不是博物馆",
        "灵魂签名": "D1创造力=0.89, D2想象力=0.91, D3艺术表达=0.93, D4镜头=0.85, D5氛围=0.92",
        "灵魂倾向情感": ["bittersweet", "joy_ecstasy", "nostalgia", "tenderness", "longing"],
    },
    "约阿希姆·提尔 (Joachim Trier)": {
        "镜头运动": "中焦 + 跟拍 + 自然观察; 像一个温柔的朋友在观察你的家庭",
        "节奏": "对话驱动, 节奏像真实生活; 慢到能听见呼吸",
        "光影": "北欧光 (高纬度柔光) + 室内暖光 + 偶尔窗外的灰蓝天",
        "声音": "流行歌 (挪威/瑞典独立音乐) + 家庭环境音 + 偶尔弦乐",
        "留白": "角色之间的留白; 大量未说出口的话",
        "表演": "演员写内心世界; Renate Reinsve / Anders Danielsen Lie",
        "代表作品": "《情感价值》《世界上最糟糕的人》《奥斯陆八月》《雷纳》《1971》",
        "格言": "从房子的视角讲故事, 家庭代际, 北欧光",
        "灵魂签名": "D1创造力=0.88, D2想象力=0.86, D3艺术表达=0.94, D4镜头=0.88, D5氛围=0.93",
        "灵魂倾向情感": ["remorse", "guilt", "tenderness", "bittersweet", "nostalgia"],
    },
}

# ============================================================
# 8 大导演方法论映射 (灵魂驱动)
# ============================================================
DIRECTOR_METHOD_8 = {
    "Paul Thomas Anderson (PTA)": "Save the Cat 15 拍 × Hero 17 阶段 × 小说化叙事 (非线性时序 + 角色驱动) × 灵魂: hate+remorse+grief 主导",
    "Christopher Nolan (诺兰)": "Hero 12 阶段 × 时间折叠剪辑 × 观念密度 (Plot > Character) × 灵魂: awe+wonder+vigilance 主导",
    "奉俊昊 (Bong Joon-ho)": "类型当特洛伊木马 × 阶级怒火 × 群戏调度 × 灵魂: disgust+tension+shame 主导",
    "Martin Scorsese (斯科塞斯)": "三幕剧 × 美国暴力考古 × 流行乐时代标记 × 灵魂: anger+guilt+shame 主导",
    "Denis Villeneuve (维伦纽瓦)": "McKee 7 原则 × 空间史诗 × 静默压顶 × 灵魂: awe+wonder+loneliness 主导",
    "Yorgos Lanthimos (兰斯莫斯)": "短剧三秒铁律 × 反讽叙事 × 冷调喜剧 × 灵魂: contempt+disgust+shyness 主导",
    "Greta Gerwig (葛韦格)": "Save the Cat 15 拍 × 内心独白 × 自然观察 × 灵魂: bittersweet+tenderness+nostalgia 主导",
    "黑泽明 (Kurosawa)": "五幕剧 × 群戏 × 空间叙事 × 灵魂: anger+pride+disapproval 主导",
    "王家卫 (Wong Kar-wai)": "时间断裂 × 物件代替心理 × 慢快门 × 灵魂: longing+nostalgia+loneliness 主导",
    "塔可夫斯基 (Tarkovsky)": "时间即主角 × 长镜头 × 诗意朦胧 × 灵魂: trust_surrender+despair+wonder 主导",
    "库斯杜力卡 (Kusturica)": "少说话 × 沉默即情感 × 群戏即兴 × 灵魂: bittersweet+joy+nostalgia 主导",
    "约阿希姆·提尔 (Joachim Trier)": "对话驱动 × 房子视角 × 家庭代际 × 灵魂: remorse+guilt+tenderness 主导",
}

# ============================================================
# 12 套理论映射 (12 Theories Mapping)
# ============================================================
THEORIES_12 = {
    "Save the Cat 15 节拍": "Opening Image / Theme Stated / Set-Up / Catalyst / Debate / Break Into Two / B Story / Fun and Games / Midpoint / Bad Guys Close In / All Is Lost / Dark Night of the Soul / Break Into Three / Finale / Final Image",
    "Hero's Journey 17 阶段": "Ordinary World / Call to Adventure / Refusal / Meeting the Mentor / Crossing the Threshold / Tests / Approach / Ordeal / Reward / Road Back / Resurrection / Return / + 5 现代变体",
    "Hero's Journey 12 阶段": "Vogler 12: Ordinary World / Call / Refusal / Mentor / Threshold / Tests / Approach / Ordeal / Reward / Road Back / Resurrection / Return",
    "Story Circle 8 段": "You / Need / Go / Search / Find / Take / Return / Change (Dan Harmon)",
    "McKee 7 原则": "Value / Cause-Effect / Arc / Essence / Conflict / Sidewise / Subtext",
    "三幕剧 8 节拍": "Plot Point 1 / Pinch Point 1 / Midpoint / Pinch Point 2 / Plot Point 2 / + 3 内部节拍",
    "8 Sequences": "Frank Daniel 8 序列结构 (每 12-15 页一个序列)",
    "五幕剧 5 幕": "Exposition / Rising Action / Climax / Falling Action / Denouement",
    "短剧三秒铁律": "每 3 秒一个钩子 (Hook); 0:00-0:03 钩子 / 0:03-0:08 设定 / 0:08-0:15 冲突 / 0:15-0:22 升级 / 0:22-0:27 高潮 / 0:27-0:30 余韵",
    "抖音 6 大套路": "悬念前置 / 视觉奇观 / 情绪共鸣 / 身份反差 / 信息密度 / 钩子串钩",
    "爆款 8 公式": "身份反差 + 时间压力 + 视觉钩子 + 情绪共鸣 + 行动障碍 + 翻转 + 兑现 + 钩子",
    "角色弧光 7 种": "positive_arc / negative_arc / flat_arc / corruption_arc / redemption_arc / testing_arc / disillusionment_arc",
}

# ============================================================
# 11 维导演控制 (11-Dimensional Director Control) — 灵魂映射
# ============================================================
DIRECTOR_CONTROL_11_FULL = {
    "空镜 (Empty Shot)": "用空镜建立空间和时间的厚度; 角色不在场时, 空间本身说话. 灵魂映射: 灵魂状态 'lucid-dreamy' 主导时空厚度, 灵感指数>0.7 时倾向诗意空镜",
    "留白 (Pause)": "在动作和台词之间插入沉默; 3 法则: 时间/空间/叙事. 灵魂映射: 怀疑指数>0.6 时倾向长留白, 精神状态 'anxious' 时更慢",
    "氛围渲染 (Atmosphere)": "用光影/声音/天气营造不可言说的情绪; 雨声/蒸汽/灰尘. 灵魂映射: 融合情感 color_palette 直接影响光色, music_tempo 决定环境音节奏",
    "悬疑 (Suspense)": "信息释放节奏; 观众知道得比角色少, 制造焦虑. 灵魂映射: vigilance 情感 + 灵感指数>0.8 时制造认知悬疑, 而非剧情悬疑",
    "多线 (Multi-thread)": "平行剪辑建立命运交错; A 线 B 线交替. 灵魂映射: rebelliousness>0.7 时倾向非线性多线, 反对传统单线",
    "反转 (Reversal)": "剧情/观众/角色认知的颠覆; 8 种反转类型. 灵魂映射: 突破勇气>0.85 时采用精神反转 (角色内心) 而非情节反转",
    "高潮 (Climax)": "情绪/动作/观念的集中爆发点; 单镜头信息密度最高. 灵魂映射: 主导情感 intensity>0.8 时达到情感顶点, 与灵魂疲劳指数反比 (疲劳越大, 高潮越静)",
    "余韵 (Aftertaste)": "结尾后观众的余思; 6 种余韵: 苦涩/温暖/震撼/平静/不安/释然. 灵魂映射: 由融合情感的 polarity 决定: positive→温暖, negative→苦涩, mixed→不安",
    "推进节奏 (Pacing)": "快慢交替; 静极静 + 动极动. 灵魂映射: 疲劳指数+灵感指数 决定节奏: 高疲劳低灵感 = 极静, 高灵感低疲劳 = 极动",
    "感情控制 (Emotion Control)": "导演像调音师一样调音观众情绪曲线. 灵魂映射: 主导情感 visual_signs+voice_signs 决定演员微动作的精度",
    "角色塑造 (Character Building)": "用动作/物件/习惯/口头禅替代心理描写. 灵魂映射: 主导情感 inner_monologue 决定角色的潜台词, facial_au 决定演员的脸部肌肉",
}

# ============================================================
# 灵魂导演映射 (12 灵魂导演 — 来自 director_soul)
# ============================================================
SOUL_DIRECTORS_12 = [
    "王家卫", "诺兰", "PTA", "奉俊昊", "黑泽明", "库斯杜力卡",
    "塔可夫斯基", "伯格曼", "王家卫_1980", "约阿希姆·提尔", "李安", "王家卫+侯孝贤",
]

# ============================================================
# 灵魂状态到留白/运镜的映射
# ============================================================
SOUL_WHITESPACE_MAP = {
    "时间留白 (Delayed Gratification)": {
        "description": "延迟满足 — 观众的情绪是在等待中形成的. 镜头不切, 让观众在画面中等待, 情绪在等待中累积.",
        "soul_state_amplifier": "高疲劳 + 高怀疑时, 时间留白拉伸至原 2 倍, 镜头不动 8-10 秒",
        "emotion_binding": "loneliness, longing, despair, wonder, trust_surrender",
    },
    "空间留白 (Emotional Concentration)": {
        "description": "决定情绪的集中度 — 主体在大空间里显得孤独, 在小空间里显得压抑. 例: 一个人站在巨大空旷的房间里.",
        "soul_state_amplifier": "灵感高时, 空间留白充满诗意; 叛逆高时, 空间留白带挑衅意味",
        "emotion_binding": "awe, loneliness, fear_terror, surrender, desperation",
    },
    "叙事留白 (Don't Say Everything)": {
        "description": "不把一切说尽 — 留给观众想象的空间. 镜头停在角色离开的画面, 不交代他去了哪里.",
        "soul_state_amplifier": "怀疑高时, 叙事留白更彻底; 突破勇气高时, 敢于完全不解释",
        "emotion_binding": "curiosity, ambiguity, contemplation, mystery, freedom",
    },
}

SOUL_CAMERA_LAW_MAP = {
    "破坏首帧完成度": {
        "description": "让镜头去找画面, 而非直接给出完美构图. 镜头从模糊/偏移开始, 然后'找到'主体, 制造真实感.",
        "soul_state_amplifier": "灵感高+叛逆高时, 倾向极端偏移首帧; 保守时只轻微偏移",
        "emotion_binding": "surprise_uncertainty, bewilderment, discovery, rawness",
    },
    "引入非线性运动轨迹": {
        "description": "拒绝过度平滑的镜头运动. 真实摄影机会有微抖、有犹豫、有加速减速. 运镜曲线不是完美的正弦波.",
        "soul_state_amplifier": "高疲劳+高灵感时, 镜头'犹豫点'多, 像疲惫但专注的摄影师",
        "emotion_binding": "uncertainty, hesitation, deliberation, wandering, search",
    },
    "制造响应延迟": {
        "description": "主体先发生动作, 镜头再跟拍. 角色先转头, 镜头 0.3-0.5 秒后才跟上, 这种延迟让画面有了'摄影师在反应'的真实感.",
        "soul_state_amplifier": "怀疑高时, 延迟更长 (0.5-0.8 秒), 像摄影师不敢确定; 灵感高时延迟短 (0.1-0.2 秒), 像直觉反应",
        "emotion_binding": "shock, realization, second-thought, reconsideration, doubt",
    },
}

# ============================================================
# 灵魂情感 → 摄影/光影/调度的映射
# ============================================================
SOUL_VISUAL_AMPLIFIER = {
    "loneliness": {"camera": "更长的空镜, 角色在远景", "lighting": "冷蓝单光源, 大量阴影", "sound": "环境音为主, 偶发心跳"},
    "longing": {"camera": "慢推 + 浅景深, 焦点在远方", "lighting": "暖黄逆光, 朦胧", "sound": "城市噪音 + 偶尔音乐"},
    "joy_pleasure": {"camera": "中景 + 跟拍 + 自然跟拍", "lighting": "暖白 + 自然光, 高光不过曝", "sound": "轻快弦乐 + 笑声"},
    "anger_fury": {"camera": "手持 + 摇晃 + 偶尔快速摇", "lighting": "高对比, 红色调, 阴影锋利", "sound": "失谐重击 + 寂静交替"},
    "sadness_grief": {"camera": "静止 + 慢推, 几乎不动", "lighting": "阴雨色, 灰蓝, 暗部细节", "sound": "大提琴低吟, 雨声"},
    "fear_terror": {"camera": "快速切 + 偶尔偷窥视角", "lighting": "高反差, 闪烁, 危险橙", "sound": "尖啸 + 突然静音"},
    "love": {"camera": "双人中景 + 浅景深 + 慢推", "lighting": "暖金 + 玫瑰金, 柔光", "sound": "弦乐 + 钢琴, 偶尔呼吸声"},
    "awe": {"camera": "极长焦 + 慢推 + 长时间不切", "lighting": "自然光 + 沙尘雾气, 圣光", "sound": "全乐队 + 和声, 低频压迫"},
    "bittersweet": {"camera": "中景 + 跟拍, 慢节奏", "lighting": "金 + 蓝对位, 暖冷交替", "sound": "大调小调交替, 钢琴"},
    "remorse": {"camera": "人物脸特写 + 浅景深", "lighting": "阴绿 + 暗灰, 阴郁", "sound": "钢琴单音, 偶尔哽咽"},
    "hate": {"camera": "中景 + 偶发快速推", "lighting": "漆黑 + 血红 + 死灰", "sound": "不和谐音, 极简电子"},
    "hope": {"camera": "慢推 + 自然跟拍, 渐亮", "lighting": "暖金 + 浅黄 + 晨曦", "sound": "渐强轻快, 70 BPM"},
}


# ============================================================
# Helper: type 防御
# ============================================================
def _str(v, default=""):
    # Phase 17.1 修复: 子 agent 删了 v=="" 检查, 导致空字符串默认值失效
    if v is None or v == "":
        return default
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else default
    return str(v)


def _pick(d, key, default=""):
    """从 dict 拿值, 容错"""
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


def _parse_soul_list(s, default=None):
    """解析逗号/换行分隔的灵魂情感 key 列表"""
    if not s:
        return list(default) if default else []
    if isinstance(s, (list, tuple)):
        return [str(x).strip() for x in s if x]
    s = str(s).strip()
    if not s:
        return list(default) if default else []
    # 支持中文逗号 + 英文逗号 + 换行 + 分号
    parts = []
    for sep in ["\n", ";", "，", ","]:
        if sep in s:
            parts = s.split(sep)
            break
    if not parts:
        parts = [s]
    return [p.strip() for p in parts if p.strip()]


def _parse_soul_weights(s, n=0, default_weights=None):
    """解析灵魂权重字符串"""
    if not s:
        if default_weights:
            return list(default_weights)
        return [1.0 / max(1, n)] * max(1, n)
    s = str(s).strip()
    parts = []
    for sep in ["\n", ";", "，", ","]:
        if sep in s:
            parts = s.split(sep)
            break
    if not parts:
        parts = [s]
    try:
        weights = [float(p.strip()) for p in parts if p.strip()]
    except Exception:
        weights = []
    if not weights:
        if default_weights:
            return list(default_weights)
        return [1.0 / max(1, n)] * max(1, n)
    return weights


def _parse_soul_dict(s, default=None):
    """解析灵魂维度 / 状态 JSON 字符串 (支持 JSON / 换行 / 逗号 / 混合)"""
    if isinstance(s, dict):
        return s
    if not s:
        return dict(default) if default else {}
    s = str(s).strip()
    if not s:
        return dict(default) if default else {}
    # 1. 先试 JSON
    try:
        return json.loads(s)
    except Exception:
        pass
    # 2. 解析 key=value 格式 (换行 或 逗号 分隔)
    result = dict(default) if default else {}
    # 先按换行 split, 再按逗号 split
    for chunk in s.replace("\n", ",").split(","):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        k, v = chunk.split("=", 1)
        k = k.strip()
        v = v.strip()
        try:
            result[k] = float(v)
        except Exception:
            # 字符串值 (如 mental_state=lucid-dreamy)
            if v:
                result[k] = v
    return result


def _safe_fuse(emotion_keys, weights, mode):
    """安全调用 fuse_emotions, 失败返回 None
    Phase 17.1: 不再预过滤, 由 fuse_emotions 内部做 alias 解析 (fear→fear_apprehension)
    """
    if not _HAS_SOUL:
        return None
    if not emotion_keys:
        return None
    try:
        # 让 fuse_emotions 自己处理 alias 解析和验证
        return fuse_emotions(list(emotion_keys), weights, mode)
    except Exception:
        return None


def _safe_soul_state(intensity, progress):
    """安全调用 compute_soul_state"""
    if not _HAS_SOUL:
        return {
            "inspiration": 0.85, "fatigue": 0.30,
            "doubt": 0.50, "rebelliousness": 0.70,
            "mental_state": "lucid-dreamy",
        }
    try:
        return compute_soul_state(intensity, progress)
    except Exception:
        return {
            "inspiration": 0.85, "fatigue": 0.30,
            "doubt": 0.50, "rebelliousness": 0.70,
            "mental_state": "lucid-dreamy",
        }


# ============================================================
# 场景动态分析引擎 (替代硬编码demo)
# ============================================================
def _analyze_scene(scene, char_a, char_b, props, mood, subtext, director):
    """从用户输入动态提取场景元素，生成上下文变量"""
    import re
    scene_lower = scene.lower() if scene else ""

    _LOCATION_TEXTURES = {
        "厨房": ("灶台/油烟/砧板/碗柜", "油烟熏黄的白墙/不锈钢台面/调料瓶排列"),
        "弄堂": ("石板路/晾衣绳/旧式门框/路灯", "青苔砖墙/木质门板/潮湿石板"),
        "咖啡馆": ("吧台/玻璃杯/吊灯/窗框", "暖黄灯光/深色木质/铜制把手/磨砂玻璃"),
        "街道": ("路灯/电话亭/行道树/车流", "湿漉柏油路/霓虹反光/人行道砖缝"),
        "办公室": ("荧幕/文件柜/百叶窗/白板", "冷色日光灯/灰色隔断/键盘声"),
        "教室": ("黑板/课桌/粉笔灰/窗帘", "米白墙面/磨损桌面/阳光斜射"),
        "医院": ("病床/监护仪/白色墙壁/消毒水", "冰冷白色/不锈钢/荧光灯管"),
        "车站": ("候车椅/时刻表/广播/月台", "水泥地面/铁质栏杆/人群嘈杂"),
        "海边": ("沙滩/礁石/海浪/灯塔", "湿润沙地/贝壳碎片/盐渍痕迹"),
        "森林": ("树冠/落叶/苔藓/溪流", "斑驳树影/泥土气息/腐叶层"),
        "卧室": ("床/台灯/窗帘/书架", "柔和织物/暖色调/私密空间"),
        "酒吧": ("吧台/酒瓶/霓虹/烟雾", "深色木质/琥珀灯光/玻璃反光"),
        "工厂": ("机器/管道/金属/天窗", "铁锈/工业灰/油渍金属"),
        "太空": ("舱壁/仪表/星光/失重", "冷金属/LED指示灯/真空黑暗"),
        "沙漠": ("沙丘/烈日/仙人掌/风纹", "金黄沙粒/热浪扭曲/干裂大地"),
        "地铁": ("车厢/扶手/广告牌/隧道", "不锈钢/荧光灯/摇晃倒影"),
    }

    loc_key = ""
    loc_elements = ""
    loc_texture = scene[:30] if scene else "场景未指定"
    for k, (elems, tex) in _LOCATION_TEXTURES.items():
        if k in scene_lower:
            loc_key = k
            loc_elements = elems
            loc_texture = tex
            break
    if not loc_key:
        loc_elements = "环境元素"
        loc_texture = "场景特有质感"

    _TIME_CUES = {
        "夜": "夜间, 低光环境", "晚": "傍晚/夜间", "黄昏": "黄昏, 金色光线",
        "清晨": "清晨, 柔和光线", "午": "正午, 强光", "雨": "雨天, 潮湿",
        "雪": "雪天, 冷白光", "雾": "雾天, 能见度低",
    }
    time_desc = ""
    for cue, desc in _TIME_CUES.items():
        if cue in scene_lower:
            time_desc = desc
            break
    if not time_desc:
        time_desc = "自然光环境"

    era_match = re.search(r'(\d{4})\s*年', scene)
    era = era_match.group(0) if era_match else ""

    location_meta = scene[:60] if scene else "未指定场景"

    prop_list = [p.strip() for p in props.replace("，", ",").split(",") if p.strip()] if props else ["道具A"]
    first_prop = prop_list[0]
    last_prop = prop_list[-1]
    prop_desc = " / ".join(prop_list[:4])

    return {
        "location_meta": location_meta,
        "loc_key": loc_key or "场景",
        "loc_elements": loc_elements,
        "loc_texture": loc_texture,
        "time_desc": time_desc,
        "era": era,
        "prop_list": prop_list,
        "first_prop": first_prop,
        "last_prop": last_prop,
        "prop_desc": prop_desc,
    }


def _dynamic_landmarks(scene_ctx):
    """从场景上下文动态生成空间地标"""
    parts = scene_ctx["loc_elements"].split("/")
    lines = []
    distances = [2.4, 3.0, 1.5, 2.0, 4.0, 3.5]
    positions = ["frame-left", "frame-right", "中央", "天花板/上方", "frame-far", "背景"]
    for i, part in enumerate(parts[:6]):
        p = part.strip()
        pos = positions[i] if i < len(positions) else "背景"
        dist = distances[i] if i < len(distances) else 3.0
        lines.append(f"  - {pos}: {p} (距摄影机 {dist}m)")
    return "\n".join(lines)


def _dynamic_action_timing(char_a, char_b, scene, mood, subtext, soul_state):
    """从角色和场景动态生成动作时间码"""
    fatigue = float(_pick(soul_state, "fatigue", 0.3))
    doubt = float(_pick(soul_state, "doubt", 0.5))
    inspiration = float(_pick(soul_state, "inspiration", 0.85))
    pause_len = "1.5-2.0" if fatigue > 0.6 else ("0.8-1.2" if fatigue > 0.3 else "0.3-0.5")

    return (
        f"0.0-0.3s — {char_a} 进入画面/在场景中, 建立空间关系\n"
        f"0.3-3.0s — {char_a} 的主要动作展开 (节奏: {mood}驱动, 微动作间隔 {pause_len}s) "
        f"— 灵魂灵感 {inspiration} 影响节奏密度\n"
        f"3.0-5.0s — 关键转折: {char_a} 的动作出现变化 (与 {subtext} 相关)\n"
        f"5.0-8.0s — {char_b} 的反应 (视线/肢体语言), 镜头开始微调 "
        f"(响应延迟 = 灵魂怀疑 {doubt})\n"
        f"8.0-12.0s — 对白/互动开始, 潜文本浮现: {subtext}\n"
        f"12.0-20.0s — 情绪积累, {mood} 的张力通过微动作持续建构\n"
        f"20.0-25.0s — 高潮点: 关键的一个动作/台词/沉默, 定义整个镜头的意义\n"
        f"25.0-30.0s — 收束: 两人的空间关系发生微妙变化, 情绪落定"
    )


def _dynamic_sfx_layers(scene_ctx, props):
    """从场景动态生成音效层"""
    _SCENE_SFX = {
        "雨": "雨声打在表面上 (持续, 从远到近的空间层次)",
        "夜": "夜间虫鸣 / 远处车声 / 偶尔的狗吠",
        "海": "海浪声 (有节奏地拍打, 3-5秒一波)",
        "森林": "风穿过树叶 / 鸟鸣 / 溪水声",
        "工厂": "机器低频嗡鸣 / 金属碰撞 / 通风管道声",
        "地铁": "列车进出站 / 报站广播 / 人群脚步",
        "酒吧": "背景人声嘈杂 / 玻璃碰撞 / 低音音乐",
        "医院": "监护仪滴声 / 脚步回响 / 广播呼叫",
        "街": "车流 / 行人脚步 / 远处喇叭 / 商铺音乐",
    }
    scene_lower = (scene_ctx.get("loc_key", "") + " " + scene_ctx.get("location_meta", "")).lower()
    layers = []
    for cue, sfx in _SCENE_SFX.items():
        if cue in scene_lower:
            layers.append(f"  - {sfx}")
    if not layers:
        layers.append("  - 环境底噪 (空间特有的背景声)")
    prop_list = scene_ctx.get("prop_list", [])
    for p in prop_list[:3]:
        layers.append(f"  - {p} 相关音效 (被触碰/放置/移动时的声音)")
    layers.append("  - 角色呼吸 / 衣物摩擦 / 脚步 (近距离拟音)")
    return "\n".join(layers)


# ============================================================
# 灵魂驱动: 动态 L1-L7 七层 (Dynamic L1-L7 with Soul)
# ============================================================
def _build_l1_intent_with_soul(intent_feel, subtext, scene, soul_fused, soul_state, soul_dims):
    """L1 - 意图与验收 — 灵魂驱动
    回答'为什么拍这个镜头' + 灵魂核心情感
    """
    fused_name = _pick(soul_fused, "name", "复合情感")
    fused_intensity = _pick(soul_fused, "intensity", 0.5)
    fused_polarity = _pick(soul_fused, "polarity", "neutral")
    fused_visual = _pick(soul_fused, "visual_signs", "")
    fused_inner = _pick(soul_fused, "inner_monologue", "")
    inspiration = _pick(soul_state, "inspiration", 0.85)
    doubt = _pick(soul_state, "doubt", 0.50)

    return (
        "L1 - 意图与验收 (DIRECTOR'S WHY) — 灵魂驱动版\n"
        "本镜让观众 " + intent_feel + ";\n"
        "通过 " + scene + " 这一主要可见事件完成;\n"
        "结束时观众应看到: 角色处于" + subtext + "的状态, 情绪从压抑过渡到复杂, "
        "镜头为下一幕的转折埋下潜文本伏笔.\n"
        "导演验收: 当观众看完本镜, 不应感到信息不足 (欠缺/没说完), 也不应感到被填鸭 (过度解释). "
        "情绪应处于'说不清但有重量'的中间态, 让观众主动参与解读.\n"
        "潜文本目标: 表面在讲" + scene + ", 实际在说" + subtext + ".\n\n"
        "【灵魂核心注入 (Phase 17)】\n"
        "主导情感: " + str(fused_name) + " (融合强度 " + str(round(float(fused_intensity), 2)) + ", 极性 " + str(fused_polarity) + ")\n"
        "灵魂视觉锚点: " + str(fused_visual[:300]) + "\n"
        "灵魂内心独白: " + str(fused_inner[:300]) + "\n"
        "灵魂状态: 灵感 " + str(inspiration) + " / 怀疑 " + str(doubt) + " — "
        + (
            "高灵感低怀疑 = 直接精确的导演意图表达"
            if float(inspiration) > 0.7 and float(doubt) < 0.5
            else (
                "高灵感高怀疑 = 反复重拍, 镜头里处处都是'或者这样'的犹豫"
                if float(inspiration) > 0.7
                else "低灵感 = 倾向保守, 选已验证的镜头语法"
            )
        )
    )


def _build_l2_assets_with_soul(char_a, char_b, location, texture, props, soul_fused, soul_dims, scene_ctx=None, director_profile=None):
    """L2 - 资产与引用 — 灵魂驱动 (动态版)
    @角色@地点@道具, 身份锁定 + 灵魂维度映射 + 导演 12 维数据
    """
    fused_color = _pick(soul_fused, "color_palette", "")
    fused_music = _pick(soul_fused, "music_tempo", "")
    artistic_expr = _pick(soul_dims, "artistic_expression", 0.85)

    ctx = scene_ctx or {}
    dp = director_profile or {}
    loc_texture = ctx.get("loc_texture", texture)
    prop_desc = ctx.get("prop_desc", props)

    dp_objects = dp.get("物件", "")
    dp_color = dp.get("色彩", "")

    asset_lines = [
        "@" + char_a + " — (主) 角色参照: 基于场景推断的外貌/服装/年龄特征, 需由用户或上游节点锁定具体外观.",
        "@" + char_b + " — (次) 角色参照: 基于场景推断的外貌/服装/年龄特征, 需由用户或上游节点锁定具体外观.",
        "@" + location + " — 空间参照: " + loc_texture + ".",
        "@" + props + " — 道具参照: " + prop_desc + ".",
    ]
    if dp_objects:
        asset_lines.append("@导演签名物件 — " + dp_objects + " (导演标志性视觉符号, 可融入场景)")
    refs = "\n".join(asset_lines)

    color_section = ""
    if dp_color:
        color_section = "导演色彩体系: " + dp_color + "\n"

    return (
        "L2 - 资产与引用 (LOCKED IDENTITIES) — 灵魂驱动版\n"
        "ACTIVE REFERENCES\n" + refs + "\n\n"
        "@" + location + " for location reference — take only the space and the texture: " + texture + ". "
        "Do not use as a starting frame, do not inherit the composition, the angle or the grade.\n\n"
        + color_section
        + "【灵魂艺术表达注入】\n"
        "D3 艺术表达力 = " + str(round(float(artistic_expr), 2)) + " — "
        + (
            "高 (>=0.9): 用具体物件代替心理 (" + (dp_objects.split("/")[0] if dp_objects else "旧信") + " 式); 选有重量的道具"
            if float(artistic_expr) >= 0.9
            else (
                "中 (0.7-0.9): 物件有情绪指向但不过度象征; 选日常的: 杯子 / 勺子 / 围裙"
                if float(artistic_expr) >= 0.7
                else "低 (<0.7): 倾向直观呈现, 道具少而清晰, 不玩象征"
            )
        )
        + "\n"
        "灵魂色彩倾向: " + str(fused_color[:200]) + "\n"
        "灵魂音乐倾向: " + str(fused_music[:200])
    )


def _build_l3_spatial_with_soul(landmarks, axis_side, soul_fused, soul_dims, atmosphere_ctrl, scene_ctx=None, director_profile=None):
    """L3 - 空间与数量 — 灵魂驱动 (动态版)
    GEO SPATIAL LAYOUT 三大铁律 + 灵魂空间感知 + 导演构图
    """
    fused_arousal = _pick(soul_fused, "arousal", "medium")
    ctx = scene_ctx or {}
    dp = director_profile or {}
    loc_key = ctx.get("loc_key", "场景")
    loc_elements = ctx.get("loc_elements", "环境元素")
    time_desc = ctx.get("time_desc", "自然光")

    dp_composition = dp.get("构图", "")
    composition_line = ""
    if dp_composition:
        composition_line = "导演构图签名: " + dp_composition + "\n"

    return (
        "L3 - 空间与数量 (UNBREAKABLE STAGE) — 灵魂驱动版\n"
        "GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):\n"
        + landmarks + "\n"
        "— 180° AXIS: camera ALWAYS stays on " + axis_side + " side — it NEVER crosses the line.\n"
        "— LIGHTING: 基于场景 (" + loc_key + ") 的主光源, " + time_desc + ".\n\n"
        + composition_line
        + "三大铁律 (Three Iron Laws of Space):\n"
        "  1. 只写空间事实, 不写人物动作 (Only space, no action)\n"
        "  2. 方向用 frame-left/frame-right + 米数, 不用 hero's left (Camera POV only)\n"
        "  3. 位置挂地标+距离, 不写相对位置 (Landmark + distance, not 'beside')\n\n"
        "【灵魂空间感知注入】\n"
        "D5 氛围掌控 = " + str(round(float(atmosphere_ctrl), 2)) + " — "
        + (
            "高 (>=0.9): 空间本身会说话, " + loc_key + " 的 " + loc_elements.split("/")[0] + " 是角色; 拒绝空场"
            if float(atmosphere_ctrl) >= 0.9
            else (
                "中 (0.7-0.9): 空间是布景, 角色是主人"
                if float(atmosphere_ctrl) >= 0.7
                else "低 (<0.7): 空间最小化, 把注意力压在人物脸上"
            )
        )
        + "\n"
        "灵魂唤醒度: " + str(fused_arousal) + " — "
        + (
            "高唤醒: 空间紧凑, 主体贴近, 镜头距离 0.5-1.5m"
            if str(fused_arousal) == "high"
            else (
                "中唤醒: 中景, 镜头距离 1.5-2.5m"
                if str(fused_arousal) == "medium"
                else "低唤醒: 远景, 主体在画面 1/3, 空间压迫"
            )
        )
    )


def _build_l4_acting_with_soul(char_a, char_b, subtext, action_timing, soul_fused, soul_state, mood="", scene="", director_profile=None):
    """L4 - 表演与物理 — 灵魂驱动 (动态版)
    5 支柱 + 7 活人感 + 灵魂情感微动作 + 导演表演风格
    """
    fused_visual = _pick(soul_fused, "visual_signs", "")
    fused_voice = _pick(soul_fused, "voice_signs", "")
    fused_au = _pick(soul_fused, "facial_au", "")
    fused_inner = _pick(soul_fused, "inner_monologue", "")
    fatigue = _pick(soul_state, "fatigue", 0.30)
    inspiration = _pick(soul_state, "inspiration", 0.85)

    dp = director_profile or {}
    dp_acting = dp.get("表演", "")
    dp_rhythm = dp.get("节奏", "")

    acting_directive = ""
    if dp_acting:
        acting_directive = (
            "导演表演签名: " + dp_acting + "\n"
            "导演节奏偏好: " + dp_rhythm + "\n"
        )

    return (
        "L4 - 表演与物理 (MAKE DIGITAL ACTORS ALIVE) — 灵魂驱动版\n"
        + acting_directive
        + "CHARACTER ACTING\n"
        + char_a + " — 主角色. 状态: " + mood + ". "
        + ("表演方法: " + dp_acting + ". " if dp_acting else "基于场景 (" + scene[:40] + ") 的角色意图和隐藏动机需由导演定义.\n")
        + "  Dominant body rhythm: " + (dp_rhythm if dp_rhythm else "基于情绪 (" + mood + ") 的身体节奏") + ", 微动作间隔与灵魂疲劳指数联动. "
        "Visible habits: 需由上游 CharacterArcPro 或 PerformanceDirectionPro 定义.\n"
        + char_b + " — 次角色. 状态: 与 " + char_a + " 的关系驱动其行为模式. "
        "基于潜文本 (" + subtext + ") 的反应模式.\n"
        "  Dominant body rhythm: 与 " + char_a + " 形成对比节奏. "
        "Visible habits: 需由上游节点定义.\n"
        "What changes: 关键转折由 " + subtext + " 驱动, 微动作总和等于情感.\n\n"
        "【灵魂情感微动作注入 — Phase 17】\n"
        "主导情感 visual_signs: " + str(fused_visual[:300]) + "\n"
        "主导情感 voice_signs: " + str(fused_voice[:300]) + "\n"
        "主导情感 facial_au: " + str(fused_au[:300]) + "\n"
        "主导情感 inner_monologue: " + str(fused_inner[:300]) + "\n"
        "灵魂疲劳指数 = " + str(fatigue) + " — "
        + (
            "高疲劳 (>=0.7): 表演更慢, 微动作之间停顿 1.5-2.0 秒, 身体语言内收"
            if float(fatigue) >= 0.7
            else (
                "中疲劳: 微动作之间停顿 0.8-1.2 秒, 节奏自然"
                if float(fatigue) >= 0.4
                else "低疲劳 (<0.4): 微动作密集, 节奏明快"
            )
        )
        + "\n"
        "灵魂灵感指数 = " + str(inspiration) + " — "
        + (
            "高灵感: 演员有即兴空间, 偶发 1-2 个非排练动作"
            if float(inspiration) > 0.8
            else "中灵感: 演员严格按 beat 走, 偶发即兴在导演确认后"
        )
        + "\n\n"
        "ACTION TIMING (微秒级时间码, 严格按 beat):\n"
        + action_timing + "\n\n"
        "PHYSICS — Gravity and inertia respected. No floating props. 所有物理交互必须符合真实世界规律.\n\n"
        "5 支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN\n"
        "  WHAT: " + char_a + " 的核心意图 (基于 " + mood + " 和场景)\n"
        "  OBSTACLE: 阻碍意图实现的内在/外在因素\n"
        "  COST: 行动的代价 — 会失去什么\n"
        "  STRATEGY: 角色选择的策略 — 用行为替代语言, 或反之\n"
        "  TURN: 转折点 — " + subtext + " 浮出表面的一刻\n\n"
        "7 活人感规则:\n"
        "  1. 分阶段眨眼: 关键时刻 DOUBLE-BLINK; 高压后 HARD reset-blink\n"
        "  2. 视线先于头: 眼睛先动, 头晚 0.3 秒跟随\n"
        "  3. 微生命: 每 1.2 秒一个微事件 (眉/鼻翼/嘴角)\n"
        "  4. 静止保持张力: 身体完全不动 0.5 秒 = '用力维持'的信号\n"
        "  5. 反应先于台词: 听见刺激后, 脸先动, 嘴后开\n"
        "  6. 重要事件后消化: 关键动作后, 0.6 秒消化时间再开口\n"
        "  7. 让手忙起来: 手部持续微动, 突然停手 = 最强重音"
    )


def _build_l5_optics_with_soul(director, soul_fused, soul_state, soul_dims, camera_skill, scene="", char_a="主角色", director_profile=None):
    """L5 - 摄影与剪辑 — 灵魂驱动 (动态版)
    焦段+光圈+景深+运动+约束 + 灵魂状态光影选择 + 导演镜头/光数据
    """
    dp = director_profile or {}
    dp_camera = dp.get("镜头", "")
    dp_light = dp.get("光", "")

    focal_default = {
        "Paul Thomas Anderson (PTA)": "85",
        "Christopher Nolan (诺兰)": "50",
        "奉俊昊 (Bong Joon-ho)": "40",
        "Martin Scorsese (斯科塞斯)": "50",
        "Denis Villeneuve (维伦纽瓦)": "135",
        "Yorgos Lanthimos (兰斯莫斯)": "24",
        "Greta Gerwig (葛韦格)": "50",
        "黑泽明 (Kurosawa)": "50",
        "王家卫 (Wong Kar-wai)": "50",
        "塔可夫斯基 (Tarkovsky)": "75",
        "库斯杜力卡 (Kusturica)": "35",
        "约阿希姆·提尔 (Joachim Trier)": "50",
    }
    focal = focal_default.get(director, "50")
    fused_color = _pick(soul_fused, "color_palette", "")
    fatigue = _pick(soul_state, "fatigue", 0.30)
    doubt = _pick(soul_state, "doubt", 0.50)
    inspiration = _pick(soul_state, "inspiration", 0.85)
    rebelliousness = _pick(soul_state, "rebelliousness", 0.70)

    scene_short = scene[:40] if scene else "场景"

    camera_directive = ""
    if dp_camera:
        camera_directive = "导演镜头签名: " + dp_camera + "\n"
    light_directive = ""
    if dp_light:
        light_directive = "导演光影签名: " + dp_light + "\n"

    return (
        "L5 - 摄影与剪辑 (CONTROL THE VIEWER'S EYE) — 灵魂驱动版\n"
        + camera_directive + light_directive
        + "OPTICS: " + focal + "mm, T2.0, 浅景深 (焦点永远在人物眼睛或手的微动作上).\n"
        "CAMERA: " + (dp_camera if dp_camera else "基于 " + director + " 的镜头偏好") + ", 在场景 (" + scene_short + ") 中构建运镜方案.\n"
        "  约束: 镜头运动服从场景空间逻辑, 不能违反已建立的 180° 轴线.\n"
        "LIGHTING: " + (dp_light if dp_light else "基于场景主光源") + ".\n"
        "NEVER: 不用希区柯克变焦 (破坏时间感); 不用与场景不匹配的运镜; 不用航拍 (除非场景要求).\n\n"
        "【灵魂光影选择注入 — Phase 17】\n"
        "D4 镜头语言技巧 = " + str(round(float(camera_skill), 2)) + " — "
        + (
            "高 (>=0.9): 镜头服务于情绪, 从 " + char_a + " 的动作细节出发构建焦点; 拒绝模式化运镜"
            if float(camera_skill) >= 0.9
            else "中: 标准镜头语法, 中景 + 中焦"
        )
        + "\n"
        "灵魂色彩 (来自融合情感): " + str(fused_color[:200]) + "\n"
        "灵魂状态决定光比: "
        + (
            "高疲劳(" + str(fatigue) + ") + 高灵感(" + str(inspiration) + ") = 极低光比, 疲惫但专注的画面质感"
            if float(fatigue) > 0.6 and float(inspiration) > 0.7
            else (
                "高怀疑(" + str(doubt) + ") = 光源不稳定, 摇曳感"
                if float(doubt) > 0.6
                else "高叛逆(" + str(rebelliousness) + ") = 不对称光, 故意打破传统三点光"
            )
        )
        + "\n\n"
        "运镜 3 法则 (3 Camera Laws to Kill AI-Feel) — 灵魂状态修正:\n"
        "  1. 破坏首帧完成度: 镜头从场景入口外侧开始, 偏移 15°, 0.5 秒后'找到'场景内景."
        + (" 灵魂高叛逆(" + str(rebelliousness) + ") 时, 偏移更极端 (30°+), 镜头'找不到'主体" if float(rebelliousness) > 0.8 else "")
        + "\n"
        "  2. 引入非线性运动轨迹: 推轨有 2 个'犹豫点' (关键动作停顿时镜头也停), 不是匀速."
        + (" 灵魂高疲劳(" + str(fatigue) + ") 时, 犹豫点增至 4 个" if float(fatigue) > 0.6 else "")
        + "\n"
        "  3. 制造响应延迟: 关键动作发生 0.3 秒后, 镜头才开始微推进."
        + (
            " 灵魂高怀疑(" + str(doubt) + ") 时, 延迟延长至 0.5-0.8 秒"
            if float(doubt) > 0.7
            else (
                " 灵魂高灵感时, 延迟缩短至 0.1-0.2 秒 (直觉反应)"
                if float(inspiration) > 0.85
                else ""
            )
        )
    )


def _build_l6_sound_with_soul(dialogue_a, dialogue_b, silenced, props, soul_fused, scene_ctx=None, director_profile=None):
    """L6 - 声音与对白 — 灵魂驱动 (动态版)
    潜文本 + 沉默 4 步 + 灵魂 voice_signs + 导演声音签名
    """
    fused_voice = _pick(soul_fused, "voice_signs", "")
    fused_music = _pick(soul_fused, "music_tempo", "")
    fused_inner = _pick(soul_fused, "inner_monologue", "")

    ctx = scene_ctx or {}
    dp = director_profile or {}
    char_a = ctx.get("char_a", "角色 A")
    char_b = ctx.get("char_b", "角色 B")
    loc_key = ctx.get("loc_key", "场景")
    sfx_layers = _dynamic_sfx_layers(ctx, props) if ctx else (
        "  - 环境音 (基于场景推断)\n"
        "  - 角色动作音 (基于道具和行为)\n"
        "  - 物件交互音 (基于 " + props + ")\n"
        "  - 背景氛围音"
    )

    dp_sound = dp.get("声音", "")
    sound_directive = ""
    if dp_sound:
        sound_directive = "导演声音签名: " + dp_sound + "\n"

    return (
        "L6 - 声音与对白 (HALF OF PICTURE) — 灵魂驱动版\n"
        + sound_directive
        + "VOICE SIGNATURES:\n"
        "  S1 (" + char_a + "): 基于角色年龄/性别/地域的声音特征, 需由上游节点或用户定义.\n"
        "  S2 (" + char_b + "): 基于角色年龄/性别/地域的声音特征, 需由上游节点或用户定义.\n\n"
        "【灵魂 voice_signs 注入 — Phase 17】\n"
        "主导情感声音签名: " + str(fused_voice[:300]) + "\n"
        "主导情感音乐节奏: " + str(fused_music[:200]) + "\n"
        "主导情感内心独白: " + str(fused_inner[:200]) + "\n\n"
        "DIALOGUE (only in AUDIO block, 潜文本对白 6 技巧):\n"
        "  S1 says: <d>[Chinese] " + dialogue_a + "</d>\n"
        "  S2 says: <d>[Chinese] " + dialogue_b + "</d>\n\n"
        "SILENCED: " + silenced + "\n\n"
        "SFX LAYERS (基于 " + loc_key + " 场景动态生成):\n"
        + sfx_layers + "\n"
        "  - " + props + " 的交互音效\n\n"
        "CONTINUATION TAIL: 上一镜的尾音延 0.5 秒进入本镜 (cross-shot sound bridge)\n\n"
        "NO MUSIC (留后期). SFX only. No subtitles."
    )


def _build_l7_style_with_soul(soul_fused, soul_dims, soul_state, director_profile=None):
    """L7 - 风格约束 — 灵魂驱动
    12 层 Style Prefix 逐字粘贴 + 灵魂 color_palette + music_tempo + 导演风格
    """
    dp = director_profile or {}
    if _HAS_INTERNAL_DOCS:
        prefix = STYLE_PREFIX
    elif dp:
        dp_color = dp.get("色彩", "naturalistic color")
        dp_light = dp.get("光", "natural lighting")
        dp_era = dp.get("年代", "contemporary")
        prefix = (
            "Live-action, " + dp_color + ". "
            + dp_light + ". "
            "Film grain texture, " + dp_era + " aesthetic. "
            "no 3D render. no game engine. no AI-generated look."
        )
    else:
        prefix = "Live-action. Natural lighting. Film grain texture. no 3D render. no game engine."
    fused_color = _pick(soul_fused, "color_palette", "")
    fused_music = _pick(soul_fused, "music_tempo", "")
    return (
        "L7 - 风格约束 (IMMUTABLE) — 灵魂驱动版\n"
        + prefix + "\n\n"
        "【灵魂色彩与音乐倾向注入 — Phase 17】\n"
        "主导情感色彩 palette: " + str(fused_color[:300]) + "\n"
        "主导情感音乐 tempo: " + str(fused_music[:300])
    )


# ============================================================
# H3 三大字段生成 — 灵魂增强
# ============================================================
def _build_h3_with_soul(scene, mood, subtext, intent_feel, props, director, soul_fused, soul_state, char_a="主角色", char_b="次角色", scene_ctx=None, director_profile=None):
    """动态生成 H3 三大字段 — 灵魂增强 + 导演 12 维数据 (动态版)"""
    ctx = scene_ctx or {}
    dp = director_profile or {}
    loc_key = ctx.get("loc_key", "场景")
    time_desc = ctx.get("time_desc", "")
    first_prop = ctx.get("first_prop", props.split(" / ")[0] if " / " in props else props)
    last_prop = ctx.get("last_prop", props.split(" / ")[-1] if " / " in props else props)

    dp_camera = dp.get("镜头", "")
    dp_sound = dp.get("声音", "")
    dp_color = dp.get("色彩", "")
    dp_emotion = dp.get("情绪", "")
    dp_objects = dp.get("物件", "")
    dp_acting = dp.get("表演", "")

    shot_1 = (
        "a medium-wide shot establishes the scene — " + scene[:80] + ". "
        + char_a + " and " + char_b + " in " + loc_key + ". "
        + (time_desc + ". " if time_desc else "")
        + "Mood: " + mood + ". "
        + ("Camera: " + dp_camera + ". " if dp_camera else "")
        + "The director intends: " + intent_feel + ". The " + props + " are present in the scene. "
        "Soul signature: " + _pick(soul_fused, "name", "") + " (intensity " + str(_pick(soul_fused, "intensity", 0.5)) + ")"
    )
    shots = [
        "[Shot 2] At 00:03.500, " + (dp_camera.split("+")[0].strip() + ". " if dp_camera and "+" in dp_camera else "the camera cuts to a medium close-up of " + char_a + ". ")
        + char_a + "'s expression carries " + mood + ". "
        "Director's intent: " + subtext + ". "
        + ("Lighting: " + dp.get("光", "") + ". " if dp.get("光") else "")
        + "Soul micro-action: " + _pick(soul_fused, "visual_signs", "")[:100],
        "[Shot 3] At 00:08.000, " + ("close-up of " + char_a + "'s hands with " + first_prop + ". " if first_prop else "")
        + (dp_acting + ". " if dp_acting else "基于角色行为的节奏. ")
        + "Soul voice: " + _pick(soul_fused, "voice_signs", "")[:100],
        "[Shot 4] At 00:15.000, over-the-shoulder shot from behind " + char_b + ". "
        "The tension between them carries " + subtext + ". "
        + ("Objects in frame: " + dp_objects.split("/")[0] + ". " if dp_objects and "/" in dp_objects else "")
        + "Soul inner_monologue: " + _pick(soul_fused, "inner_monologue", "")[:100],
        "[Shot 5] At 00:22.000, " + ("key beat — " + dp_acting + ". " if dp_acting else "关键转折动作. ")
        + "Per the silence formula: 一句短台词 + 3 秒沉默 + 微表情 + 改变关系动作 + 5 秒呼吸. "
        "Director's intent: " + intent_feel + ". "
        "Soul fatigue: " + str(_pick(soul_state, "fatigue", 0.3)) + " / inspiration: " + str(_pick(soul_state, "inspiration", 0.85)),
        "[Shot 6] At 00:27.000, the camera holds for 3 seconds, allowing the audience to process. "
        "The " + last_prop + " catches the light. End of shot. "
        + ("Emotional register: " + dp_emotion + ". " if dp_emotion else "")
        + "Soul aftertaste: " + str(_pick(soul_fused, "polarity", "neutral")) + " (positive→温暖 / negative→苦涩 / mixed→不安)",
    ]
    soundscape = (
        (dp_sound + " — " if dp_sound else "")
        + "环境音基于 " + loc_key + " 场景动态生成. "
        + "角色动作产生的声音与道具 (" + props + ") 交互. "
        + "声音的空间层次: 远景环境音 (3m+), 中景动作音 (0.8-2m), 近景细节音 (0.3m以内).\n\n"
        "【灵魂 soundscape 注入】\n"
        "主导情感 voice_signs: " + str(_pick(soul_fused, "voice_signs", "")[:200]) + "\n"
        "主导情感 music_tempo: " + str(_pick(soul_fused, "music_tempo", "")[:200])
    )
    music = (
        "Sparse " + str(_pick(soul_fused, "music_tempo", "piano notes at 60 BPM")) +
        " joined by low strings. (来自主导情感的音乐节奏指引)"
    )
    style = (
        "Cinematic, live-action, "
        + (dp_color + ", " if dp_color else "")
        + "35mm film grain, " + director + " 风格. 灵魂调色: " + str(_pick(soul_fused, "color_palette", ""))
    )
    return style, shot_1, shots, soundscape, music


# ============================================================
# 灵魂驱动: 11 维导演控制映射
# ============================================================
def _build_director_control_11_soul(soul_fused, soul_state, soul_dims):
    """生成 11 维导演控制 — 灵魂状态增强版 (动态)"""
    inspiration = float(_pick(soul_state, "inspiration", 0.85))
    fatigue = float(_pick(soul_state, "fatigue", 0.30))
    doubt = float(_pick(soul_state, "doubt", 0.50))
    rebelliousness = float(_pick(soul_state, "rebelliousness", 0.70))
    creativity = float(_pick(soul_dims, "creativity", 0.85))
    imagination = float(_pick(soul_dims, "imagination", 0.85))
    artistic = float(_pick(soul_dims, "artistic_expression", 0.85))
    camera = float(_pick(soul_dims, "camera_skill", 0.85))
    atmosphere = float(_pick(soul_dims, "atmosphere_control", 0.85))
    breakthrough = float(_pick(soul_dims, "breakthrough_courage", 0.85))

    parts = ["【11 维导演控制能力 (灵魂驱动版)】\n"]
    parts.append(
        "  1. 空镜 (Empty Shot) — 灵魂维度 D2=" + str(round(imagination, 2))
        + " + 灵感 " + str(inspiration) + ": "
        + ("高想象: 5-8 秒空镜 (场景中最具象征性的物件/空间); 让空间说话"
           if imagination > 0.9
           else "中: 2-3 秒空镜 (只交代空间)")
    )
    parts.append(
        "  2. 留白 (Pause) — 灵魂状态怀疑 " + str(doubt) + ": "
        + ("高怀疑: 留白 8-10 秒, 镜头不动, 演员也不动; 沉默即情感"
           if doubt > 0.6
           else "中: 留白 3-5 秒, 标准沉默")
    )
    parts.append(
        "  3. 氛围渲染 (Atmosphere) — 灵魂色彩: " + str(_pick(soul_fused, "color_palette", "")[:100])
        + " / D5 氛围 = " + str(round(atmosphere, 2))
        + ": 基于场景的多层环境音堆叠, 营造沉浸感"
    )
    parts.append(
        "  4. 悬疑 (Suspense) — 灵魂主导情感 vigilance=" + str(inspiration) + ": "
        + "信息差制造悬疑 (观众知道 > 角色知道), 不靠 jump scare"
    )
    parts.append(
        "  5. 多线 (Multi-thread) — 灵魂叛逆度 " + str(rebelliousness) + ": "
        + ("高叛逆: 闪回 + 现时 + 内心独白三线交叉"
           if rebelliousness > 0.7
           else "中: 单线 + 偶尔回忆闪切")
    )
    parts.append(
        "  6. 反转 (Reversal) — 灵魂突破勇气 " + str(round(breakthrough, 2)) + ": "
        + ("高突破: 精神反转 — 角色认知的翻转; 观众最后一刻才发现真相"
           if breakthrough > 0.85
           else "中: 情节反转 — 关键动作的结果超出预期")
    )
    parts.append(
        "  7. 高潮 (Climax) — 灵魂状态 灵感/疲劳比 = " + str(round(inspiration / max(0.1, fatigue), 2))
        + ": 高潮可以静到极致, 也可以爆发; 关键是一个微小的变化撑起整个画面"
    )
    parts.append(
        "  8. 余韵 (Aftertaste) — 灵魂极性 " + str(_pick(soul_fused, "polarity", "neutral"))
        + ": 余韵由情感极性决定 — 观众在结尾想问'接下来怎么办'; 镜头停留, 让观众自行消化"
    )
    parts.append(
        "  9. 推进节奏 (Pacing) — 灵魂状态组合: 灵感 " + str(inspiration)
        + " + 疲劳 " + str(fatigue) + " + 怀疑 " + str(doubt)
        + ": 静极静 + 动极动 — 节奏在微动作的间隔里完成"
    )
    parts.append(
        "  10. 感情控制 (Emotion Control) — 灵魂 voice_signs "
        + str(_pick(soul_fused, "voice_signs", "")[:80])
        + ": 声音比台词更会说话; 微动作和物件交互传递情感"
    )
    parts.append(
        "  11. 角色塑造 (Character Building) — 灵魂 facial_au "
        + str(_pick(soul_fused, "facial_au", "")[:80])
        + ": 角色前史通过物件和行为呈现; 用物件代替心理"
    )
    return "\n".join(parts)


# ============================================================
# 灵魂驱动: 3 留白 + 3 运镜法则
# ============================================================
def _build_three_whitespace_soul(soul_state, soul_fused):
    """3 留白 — 灵魂状态增强 (动态)"""
    inspiration = float(_pick(soul_state, "inspiration", 0.85))
    fatigue = float(_pick(soul_state, "fatigue", 0.30))
    doubt = float(_pick(soul_state, "doubt", 0.50))
    return (
        "【3 留白 (3 Whitespace Techniques) — 灵魂状态增强】\n"
        "  1. 时间留白 (Delayed Gratification) — 灵魂状态: 灵感 " + str(inspiration)
        + " / 怀疑 " + str(doubt) + " — "
        + ("高怀疑时, 镜头 0.5-0.8 秒后才反应; 时间留白拉伸至原 2 倍"
           if doubt > 0.7
           else "中: 标准 0.3-0.5 秒反应延迟")
        + "\n"
        "  2. 空间留白 (Emotional Concentration) — 灵魂维度 D5 氛围 — "
        + ("主体在大空间里显得孤独, 在小空间里显得压抑; 空间留白 30% 以上"
           if float(_pick(soul_state, "inspiration", 0.85)) > 0.7
           else "中: 主体在中景, 周围 20% 空间留白")
        + "\n"
        "  3. 叙事留白 (Don't Say Everything) — 灵魂状态 怀疑 " + str(doubt) + " — "
        + ("高怀疑时, 叙事留白更彻底; 镜头不停在反应, 而是停在离开的背影 = 不说破, 留观众自己想"
           if doubt > 0.6
           else "中: 切到反应镜头, 留白 1 秒")
    )


def _build_three_camera_laws_soul(soul_state, soul_fused):
    """3 运镜法则 — 灵魂状态增强 (动态)"""
    rebelliousness = float(_pick(soul_state, "rebelliousness", 0.70))
    fatigue = float(_pick(soul_state, "fatigue", 0.30))
    doubt = float(_pick(soul_state, "doubt", 0.50))
    return (
        "【3 运镜法则 (3 Camera Laws to Kill AI-Feel) — 灵魂状态增强】\n"
        "  1. 破坏首帧完成度 — 灵魂叛逆 " + str(rebelliousness) + " — "
        + ("高叛逆(" + str(rebelliousness) + "): 镜头从场景入口外侧开始, 偏移 30°+, 镜头'找不到'主体"
           if rebelliousness > 0.8
           else "中: 偏移 15°, 0.5 秒后找到主体")
        + "\n"
        "  2. 引入非线性运动轨迹 — 灵魂疲劳 " + str(fatigue) + " — "
        + ("高疲劳(" + str(fatigue) + "): 推轨有 4 个'犹豫点' (关键动作/角色停顿/环境变化/互动时刻), 不是匀速"
           if fatigue > 0.6
           else "中: 2 个犹豫点")
        + "\n"
        "  3. 制造响应延迟 — 灵魂怀疑 " + str(doubt) + " — "
        + ("高怀疑(" + str(doubt) + "): 关键动作 0.5-0.8 秒后, 镜头才开始微推进"
           if doubt > 0.7
           else "中: 0.3 秒响应延迟")
    )


# ============================================================
# 灵魂驱动: 5 要素架构 — 数据层增加灵魂维度
# ============================================================
def _build_5_elements_soul(soul_fused, soul_state, soul_dims, director, scene):
    """5 要素 — 灵魂数据层增强"""
    return {
        "data": (
            "1161 部 director_view 14 维 + 63 导演 12 维 + 8 顶级导演风格库 (PTA/Nolan/Bong/Scorsese/Villeneuve/Lanthimos/Gerwig/Kurosawa) + "
            + str(len(EMOTION_MATRIX_60) if _HAS_SOUL else 48) + " 情感矩阵 (Plutchik 8 基础 × 3 强度 + Izard 10 基础 + 5 复杂 + 10 状态) + "
            "7 情感融合公式 (F1-F7) + 10 灵魂维度 (创造力/想象力/艺术表达/镜头/氛围/精神/灵感/叛逆/怀疑/突破) + "
            "灵魂状态 (灵感/疲劳/怀疑/叛逆) + "
            "191 反 AI 词表 + 10 强制具体细节铁律 + 12 套理论 + 14 部真实短剧 + "
            "4 类创作者实战 + H3 三大字段 + 4 任务类型 + 13 镜头运动 + "
            "11 维导演控制 + 3 留白 + 3 运镜法则 + 9 维光照 + 5 空间 + 5 沉默 + 卡兹克 2.5 SFT"
        ),
        "context": (
            "类型 + 导演=" + director + " + 主题 + 场景=" + str(scene[:60]) + " + "
            "灵魂融合=" + str(_pick(soul_fused, "name", "")) + " (强度 " + str(_pick(soul_fused, "intensity", 0.5)) + ", 极性 " + str(_pick(soul_fused, "polarity", "")) + ") + "
            "灵魂状态: 灵感 " + str(_pick(soul_state, "inspiration", 0.85))
            + " / 疲劳 " + str(_pick(soul_state, "fatigue", 0.30))
            + " / 怀疑 " + str(_pick(soul_state, "doubt", 0.50))
            + " / 叛逆 " + str(_pick(soul_state, "rebelliousness", 0.70))
            + " / 精神=" + str(_pick(soul_state, "mental_state", "lucid-dreamy"))
        ),
        "skill": (
            "12 套理论 (Save the Cat/Hero/Story Circle/McKee/三幕/8 Seq/五幕/短剧规则/抖音/爆款/弧光/反转) + "
            "8 顶级导演方法论 + 191 反 AI + 13 镜头运动 + 11 规则 + 5 沉默 + 5 空间 + 5 维意图 + 4 维美术 + 9 维光照 + "
            "7 情感融合公式 (F1 单情感 / F2 主次 70-30 / F3 对等 50-50 / F4 三情感递进 / F5 矛盾爆炸 / F6 复合三角 / F7 情感转化) + "
            "10 灵魂维度 (D1 创造力 / D2 想象力 / D3 艺术表达 / D4 镜头 / D5 氛围 / D6 精神 / D7 灵感 / D8 叛逆 / D9 怀疑 / D10 突破) + "
            "灵魂状态动态计算 (灵感/疲劳/怀疑/叛逆, scene_progress 0.0→1.0 动态变化)"
        ),
        "experience": (
            "14 部真实 AI 短剧实战 + 4 类创作者 (齐磊/王天海/00 后女生/LibTV) + "
            "3 附件核心 (导演意图/美术/空间/沉默) + 卡兹克 2.5 SFT 重定义 + 8 大顶级导演实战 + "
            "灵魂状态案例: 灵感时刻 (诺兰《盗梦空间》火车冲入街道) / 自我怀疑 (泰伦斯·马力克 反复重剪) / "
            "突破勇气 (奉俊昊《寄生虫》非线性) / 叛逆 (林奇《穆赫兰道》无解释)"
        ),
        "ai_deep": (
            "反 AI 词表 (191) + 10 铁律 + 4 轮迭代 + 沉默 4 步公式 + 留白 3 法 + 导演意图 5 维 + "
            "11 维导演控制 (灵魂映射) + 30 秒场景单元 6 段式 + 卡兹克 2.5 (压住随手补戏的冲动) + "
            "L1-L7 七层动态生成 (灵魂注入) + 8 大导演风格库 + 灵魂融合公式 (F1-F7) + "
            "灵魂状态动态注入每个镜头 + H3 三大字段 (integrated_multimodal_description + overall_soundscape + non_diegetic_music 灵魂增强)"
        ),
    }


# ============================================================
# ConceptPitchPro 主类 — Phase 17 灵魂注入版
# ============================================================
class ConceptPitchPro:
    """
    概念立项与故事架构节点 — Phase 17 灵魂注入

    接入 DirectorSoulNode:
    - 接收 soul_emotion_keys / soul_weights / soul_mode
    - 接收 soul_dimensions (10 维度)
    - 接收 soul_state (灵感/疲劳/怀疑/叛逆)
    - 接收 soul_director (12 灵魂导演)

    真正动态生成: 灵魂融合后, 所有 L1-L7 / 11 维 / 3 留白 / 3 运镜 / H3 全部重新生成
    """

    @classmethod
    def INPUT_TYPES(cls):
        # 默认 灵魂情感 keys
        default_soul_keys = (
            "loneliness, longing"
        )
        default_soul_weights = "0.5, 0.5"
        default_soul_dims = (
            "creativity=0.85, imagination=0.85, artistic_expression=0.85, "
            "camera_skill=0.85, atmosphere_control=0.85, mental_state=lucid-dreamy, "
            "inspiration=0.85, rebelliousness=0.70, self_doubt=0.50, breakthrough_courage=0.85"
        )
        default_soul_state = (
            "inspiration=0.85, fatigue=0.30, doubt=0.50, rebelliousness=0.70, "
            "mental_state=lucid-dreamy, story_intensity=0.5, scene_progress=0.0"
        )
        return {
            "required": {
                # === 基础任务 (向后兼容) ===
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边",
                    "multiline": True,
                }),
                "导演风格": (list(MASTER_DIRECTORS_8.keys()), {"default": "王家卫 (Wong Kar-wai)"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === Phase 17 灵魂注入 (核心) ===
                "灵魂融合情感": ("STRING", {
                    "default": default_soul_keys,
                    "multiline": True,
                    "tooltip": "逗号分隔的情感 key 列表 (来自 director_soul.EMOTION_MATRIX_60 的 key)",
                }),
                "灵魂融合权重": ("STRING", {
                    "default": default_soul_weights,
                    "multiline": True,
                    "tooltip": "逗号分隔的权重, 与情感对应 (auto=自动归一化)",
                }),
                "灵魂融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                "灵魂维度JSON": ("STRING", {
                    "default": default_soul_dims,
                    "multiline": True,
                    "tooltip": "10 灵魂维度: creativity/imagination/artistic_expression/camera_skill/atmosphere_control/mental_state/inspiration/rebelliousness/self_doubt/breakthrough_courage",
                }),
                "灵魂状态JSON": ("STRING", {
                    "default": default_soul_state,
                    "multiline": True,
                    "tooltip": "灵魂状态: inspiration/fatigue/doubt/rebelliousness/mental_state/story_intensity/scene_progress",
                }),
                "灵魂导演": (SOUL_DIRECTORS_12, {"default": "王家卫"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("conceptpitchpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_concept"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_concept(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # ============================================================
        # Phase 17 灵魂注入: 解析所有灵魂输入
        # ============================================================
        # Phase 17.1: 优先读 灵魂_主导情感 (单情感入口)
        soul_primary_input = _str(kwargs.get("灵魂_主导情感", ""), "")
        if not soul_primary_input:
            soul_primary_input = _str(kwargs.get("主导情感", ""), "")
        soul_keys_raw = _str(kwargs.get("灵魂融合情感", ""), "")
        # 智能判断: 有主导情感但没融合列表 → 用主导情感作单情感
        if soul_primary_input and soul_primary_input != "auto" and not soul_keys_raw.strip():
            soul_keys = [soul_primary_input]
        else:
            soul_keys = _parse_soul_list(soul_keys_raw, default=["loneliness", "longing"])
        soul_weights_raw = _str(kwargs.get("灵魂融合权重", ""), "")
        soul_mode = _str(kwargs.get("灵魂融合模式", ""), "auto")
        soul_dims = _parse_soul_dict(_str(kwargs.get("灵魂维度JSON", ""), ""),
                                      default={"creativity": 0.85, "imagination": 0.85,
                                               "artistic_expression": 0.85, "camera_skill": 0.85,
                                               "atmosphere_control": 0.85, "mental_state": "lucid-dreamy",
                                               "inspiration": 0.85, "rebelliousness": 0.70,
                                               "self_doubt": 0.50, "breakthrough_courage": 0.85})
        soul_state_in = _parse_soul_dict(_str(kwargs.get("灵魂状态JSON", ""), ""),
                                          default={"inspiration": 0.85, "fatigue": 0.30,
                                                   "doubt": 0.50, "rebelliousness": 0.70,
                                                   "mental_state": "lucid-dreamy",
                                                   "story_intensity": 0.5, "scene_progress": 0.0})
        soul_director = _str(kwargs.get("灵魂导演", ""), "王家卫")

        # 计算灵魂权重
        n_soul = len(soul_keys)
        if soul_weights_raw and soul_weights_raw != "":
            soul_weights = _parse_soul_weights(soul_weights_raw, n_soul)
        else:
            soul_weights = None

        # 1. 情感融合
        soul_fused = _safe_fuse(soul_keys, soul_weights, soul_mode)
        if soul_fused is None:
            soul_fused = {
                "name": "复合情感 (默认)",
                "emotions": soul_keys or ["loneliness", "longing"],
                "weights": soul_weights or [0.5, 0.5],
                "fusion_mode": "F3_双情感对等融合",
                "intensity": 0.65,
                "polarity": "mixed",
                "arousal": "medium",
                "description": "默认复合情感融合",
                "visual_signs": "微微的孤独 + 远方的思念, 视线远眺",
                "voice_signs": "语速慢, 经常停顿, 声音轻",
                "facial_au": "AU1+AU2+AU15",
                "inner_monologue": "这一刻, 我想靠近但又怕靠近",
                "color_palette": "冷蓝 + 暖黄, 朦胧, 雾色",
                "music_tempo": "60-70 BPM, 钢琴 + 弦乐",
                "director_examples": "王家卫《花样年华》",
            }

        # 2. 灵魂状态 (动态计算, 基于故事强度 + 场景进度)
        story_intensity = float(_pick(soul_state_in, "story_intensity", 0.5))
        scene_progress = float(_pick(soul_state_in, "scene_progress", 0.0))
        soul_state = _safe_soul_state(story_intensity, scene_progress)
        # 用用户传入的状态覆盖默认值
        for k in ["inspiration", "fatigue", "doubt", "rebelliousness", "mental_state"]:
            if k in soul_state_in:
                soul_state[k] = soul_state_in[k]

        # ============================================================
        # 基础用户输入 (向后兼容)
        # ============================================================
        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "电影")
        scene = _str(kwargs.get("场景描述"), "")
        # 新增测试 kwargs 兼容
        concept_logline = _str(kwargs.get("概念一句话"), "") or scene
        audience = _str(kwargs.get("受众画像"), "")
        core_selling = _str(kwargs.get("核心卖点"), "")
        differentiation = _str(kwargs.get("差异化"), "")
        ref_films = _str(kwargs.get("参考作品"), "")
        director = _str(kwargs.get("导演风格"), "王家卫 (Wong Kar-wai)")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films_old = _str(kwargs.get("关键参考片"), "")
        if not ref_films:
            ref_films = ref_films_old
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # ============================================================
        # 节点专属: 领域能力 (灵魂增强)
        # ============================================================
        domain_name = "概念立项 + 故事架构 (环节 1-3, 6-7) — Phase 17 灵魂注入"
        domain_focus = "Save the Cat 15 拍 × Hero 17/12 阶段 × McKee 7 原则 × 三幕剧 8 节拍 × 灵魂融合 F1-F7 × 10 灵魂维度"
        h3_special = "BS2 Opening Image + BS1 Final Image + Logline 反差结构 + 灵魂 H3 增强 (integrated_multimodal_description + overall_soundscape + non_diegetic_music 全部嵌入灵魂 voice_signs + color_palette + music_tempo)"

        director_specifics = (
            "PTA: 小说化时序折叠 / 诺兰: 观念密度 + 三小时道德辩论 / 奉俊昊: 类型当特洛伊木马 / "
            "斯科塞斯: 审问美国暴力 / 维伦纽瓦: 静默与尺度 / 兰斯莫斯: 古怪眼界 / "
            "葛韦格: 写内心世界 / 黑泽明: 视觉/叙事/情绪/空间极致清晰 / "
            "王家卫: 时间断裂+物件代替心理 / 塔可夫斯基: 时间即主角+长镜头 / "
            "库斯杜力卡: 沉默即情感+塞尔维亚乡愁 / 约阿希姆·提尔: 房子视角+家庭代际"
        )
        extra_inject = "12 套理论 + 14 部真实短剧 + 4 类创作者 + 卡兹克 2.5 SFT + 48 情感矩阵 + 7 融合公式 + 10 灵魂维度 + 灵魂状态"

        # ============================================================
        # 导演方法 (灵魂驱动)
        # ============================================================
        director_method = DIRECTOR_METHOD_8.get(director, "Save the Cat 15 拍 × Hero 12 × 灵魂融合 F3")
        director_motion_pref = {
            "Paul Thomas Anderson (PTA)": "Push In 慢推 + Arc Shot 环绕 + 70-100mm 中长焦",
            "Christopher Nolan (诺兰)": "Tracking Shot 跟拍 + 时间折叠剪辑 + IMAX 65mm",
            "奉俊昊 (Bong Joon-ho)": "横移 + 精确调度 + 中景",
            "Martin Scorsese (斯科塞斯)": "中焦跟拍 + 燃烧式运镜 + 偶尔 90 年代长镜头",
            "Denis Villeneuve (维伦纽瓦)": "Static Shot 长时间不动 + Push In 慢推 + 极长焦",
            "Yorgos Lanthimos (兰斯莫斯)": "广角 + 鱼眼 + 不规则构图",
            "Greta Gerwig (葛韦格)": "中景跟拍 + 50mm + 手部特写",
            "黑泽明 (Kurosawa)": "中焦 + 横移 + 多机位",
            "王家卫 (Wong Kar-wai)": "广角 + 手持 + 慢快门 + 0.5 倍速世界",
            "塔可夫斯基 (Tarkovsky)": "极长镜头 (5-10 分钟) + 跟人物走 + 慢推",
            "库斯杜力卡 (Kusturica)": "广角 + 手持跟拍 + 偶尔航拍",
            "约阿希姆·提尔 (Joachim Trier)": "中焦 + 跟拍 + 自然观察",
        }.get(director, "Push In 慢推 + 中焦")
        director_meta = MASTER_DIRECTORS_8.get(director, {})

        # ============================================================
        # 角色推断 (从场景中提取)
        # ============================================================
        scene_for_chars = scene + " " + concept_logline
        if "父女" in scene_for_chars or "父与子" in scene_for_chars or "父子" in scene_for_chars:
            char_a = "父亲"
            char_b = "女儿"
        elif "母" in scene_for_chars:
            char_a = "母亲"
            char_b = "孩子"
        elif "夫妻" in scene_for_chars or "夫妇" in scene_for_chars:
            char_a = "丈夫"
            char_b = "妻子"
        elif "朋友" in scene_for_chars or "两人" in scene_for_chars:
            char_a = "角色 A"
            char_b = "角色 B"
        else:
            char_a = "主角色"
            char_b = "次角色"

        # ============================================================
        # 5 要素 (灵魂增强)
        # ============================================================
        five_elements = _build_5_elements_soul(soul_fused, soul_state, soul_dims, director, scene)
        data_summary = five_elements["data"]
        context_brief = five_elements["context"]
        skill_harness = five_elements["skill"]
        experience_matrix = five_elements["experience"]
        ai_deep = five_elements["ai_deep"]

        # ============================================================
        # Phase 5.0: 知识库深度集成
        # ============================================================
        kb_section = ""
        if _HAS_KB:
            director_clean = director.split("(")[0].strip() if "(" in director else director.strip()
            kb_decision = get_director_decision(director_clean, scene)
            kb_emotion = get_emotion_palette(
                soul_fused.get("emotions", ["loneliness"])[0] if isinstance(soul_fused.get("emotions"), list) else "loneliness",
                soul_fused.get("intensity", 0.5),
            )
            genre_key = genre.lower().replace(" ", "_")
            genre_data = GENRE_PROFILES.get(genre_key, {})
            kb_lines = ["", "═══ 知识库决策层注入 ═══"]
            if kb_decision.get("style"):
                ds = kb_decision["style"]
                kb_lines.append(f"【导演签名】{ds.get('cn', director)}: {ds.get('signature', '')}")
                kb_lines.append(f"  叙事原则: {ds.get('narrative_principle', '')[:200]}")
                if ds.get("visual_techniques"):
                    kb_lines.append(f"  视觉技法: {', '.join(ds['visual_techniques'][:4])}")
            if genre_data:
                vl = genre_data.get("visual_language", {})
                if vl:
                    kb_lines.append(f"【类型视觉语言】{genre_data.get('cn', genre)}")
                    kb_lines.append(f"  光: {vl.get('lighting', '')[:100]}")
                    kb_lines.append(f"  构图: {vl.get('composition', '')[:100]}")
                    kb_lines.append(f"  色彩: {vl.get('color', '')[:100]}")
            if kb_emotion.get("camera"):
                kb_lines.append(f"【情绪镜头响应】{kb_emotion.get('cn_name', '')}: {kb_emotion['camera']}")
            if kb_emotion.get("lighting"):
                kb_lines.append(f"【情绪光影响应】{kb_emotion['lighting']}")
            if kb_emotion.get("pacing"):
                kb_lines.append(f"【情绪节奏响应】{kb_emotion['pacing']}")
            kb_section = "\n".join(kb_lines) + "\n"

        # ============================================================
        # 关键参考元素 + 道具拆分 (动态)
        # ============================================================
        ref_parts = [p.strip() for p in ref_films.split(" / ") if p.strip()] if ref_films else []
        texture = ", ".join(ref_parts) if ref_parts else "场景质感由导演风格和类型决定"

        scene_ctx = _analyze_scene(scene, char_a, char_b, props, mood, subtext, director)
        dp = get_director_profile(director) if _HAS_DIRECTOR_DB else {}
        location_meta = scene_ctx.get("location_meta", scene[:30] if scene else "场景")
        texture_of_loc = scene_ctx.get("loc_texture", "基于场景推断")
        landmarks = _dynamic_landmarks(scene_ctx)
        action_timing = _dynamic_action_timing(char_a, char_b, scene, mood, subtext, soul_state)

        dp_performance = dp.get("表演", "") if dp else ""
        dp_rhythm = dp.get("节奏", "") if dp else ""
        if dp_performance:
            dialogue_a = "（" + char_a + " 的台词, " + dp_performance + " 风格, 基于 " + mood + " 和 " + subtext + "）"
            dialogue_b = "（" + char_b + " 的回应, 与 " + char_a + " 形成 " + dp_rhythm + " 节奏对比）"
        else:
            dialogue_a = "（基于场景和潜文本的台词, 由 " + char_a + " 说出）"
            dialogue_b = "（基于场景和潜文本的回应, 由 " + char_b + " 说出）"

        silenced = (
            "沉默 4 步公式: 一句短台词 + 3 秒沉默 + "
            "微表情 + 改变关系动作 + "
            "5 秒呼吸 (基于 " + mood + " 和 " + subtext + " 的沉默设计)"
        )

        # ============================================================
        # 生成 L1-L7 七层 (灵魂注入)
        # ============================================================
        l1 = _build_l1_intent_with_soul(intent_feel, subtext, scene, soul_fused, soul_state, soul_dims)
        l2 = _build_l2_assets_with_soul(char_a, char_b, location_meta, texture_of_loc, props, soul_fused, soul_dims,
                                          scene_ctx=scene_ctx, director_profile=dp)
        l3 = _build_l3_spatial_with_soul(landmarks, "south", soul_fused, soul_dims,
                                          _pick(soul_dims, "atmosphere_control", 0.85),
                                          scene_ctx=scene_ctx, director_profile=dp)
        l4 = _build_l4_acting_with_soul(char_a, char_b, subtext, action_timing, soul_fused, soul_state,
                                          mood=mood, scene=scene, director_profile=dp)
        l5 = _build_l5_optics_with_soul(director, soul_fused, soul_state, soul_dims,
                                          _pick(soul_dims, "camera_skill", 0.85),
                                          scene=scene, char_a=char_a, director_profile=dp)
        scene_ctx["char_a"] = char_a
        scene_ctx["char_b"] = char_b
        l6 = _build_l6_sound_with_soul(dialogue_a, dialogue_b, silenced, props, soul_fused,
                                          scene_ctx=scene_ctx, director_profile=dp)
        l7 = _build_l7_style_with_soul(soul_fused, soul_dims, soul_state, director_profile=dp)

        # ============================================================
        # H3 三大字段 (灵魂增强)
        # ============================================================
        style, shot_1, shots, soundscape, music = _build_h3_with_soul(
            scene, mood, subtext, intent_feel, props, director, soul_fused, soul_state,
            char_a=char_a, char_b=char_b, scene_ctx=scene_ctx, director_profile=dp
        )
        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese",
        )
        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 灵魂 H3 增强 (附加)
        h3_soul_addon = (
            "\n\n【灵魂 H3 增强 — Phase 17】\n"
            "integrated_multimodal_description 灵魂锚点: " + str(_pick(soul_fused, "name", ""))
            + " (极性 " + str(_pick(soul_fused, "polarity", "")) + ", 强度 "
            + str(_pick(soul_fused, "intensity", 0.5)) + ")\n"
            "overall_soundscape 灵魂维度: voice_signs = " + str(_pick(soul_fused, "voice_signs", "")[:200])
            + " | music_tempo = " + str(_pick(soul_fused, "music_tempo", "")[:200])
            + "\nnon_diegetic_music 灵魂节奏: " + str(_pick(soul_fused, "music_tempo", ""))
        )
        h3_prompt = h3_prompt + h3_soul_addon

        # ============================================================
        # 30 秒场景单元 6 段式 (灵魂增强)
        # ============================================================
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice="基于 " + char_a + " 角色设定的声音",
            dialogue=dialogue_a, n_lines=1, director_intent=intent_feel, language="Chinese",
        )
        timeline_30s_lines = "\n".join(
            "  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc
            for (ts, te, stage, desc) in SCENE_UNIT_30S
        )

        # ============================================================
        # 11 维导演控制 (灵魂驱动)
        # ============================================================
        director_control_text = _build_director_control_11_soul(soul_fused, soul_state, soul_dims)

        # ============================================================
        # 3 留白 + 3 运镜法则 (灵魂驱动)
        # ============================================================
        whitespace_3 = _build_three_whitespace_soul(soul_state, soul_fused)
        camera_3 = _build_three_camera_laws_soul(soul_state, soul_fused)

        # ============================================================
        # 8 大导演方法论
        # ============================================================
        director_8_method = "【8 大世界顶级导演方法论 — 灵魂驱动】\n"
        for d, m in DIRECTOR_METHOD_8.items():
            director_8_method += "  - " + d + ": " + m + "\n"

        # ============================================================
        # 8 大导演风格库
        # ============================================================
        director_8_style = "【8 大世界顶级导演风格库 (Master Director Style Library) — 灵魂映射】\n"
        for d, m in MASTER_DIRECTORS_8.items():
            director_8_style += "  ▸ " + d + "\n"
            director_8_style += "    镜头: " + m["镜头运动"] + "\n"
            director_8_style += "    节奏: " + m["节奏"] + "\n"
            director_8_style += "    光影: " + m["光影"] + "\n"
            director_8_style += "    声音: " + m["声音"] + "\n"
            director_8_style += "    留白: " + m["留白"] + "\n"
            director_8_style += "    代表: " + m["代表作品"] + "\n"
            director_8_style += "    格言: " + m["格言"] + "\n"
            director_8_style += "    " + _pick(m, "灵魂签名", "") + "\n"
            director_8_style += "    灵魂倾向情感: " + ", ".join(_pick(m, "灵魂倾向情感", [])) + "\n"

        # ============================================================
        # 12 套理论
        # ============================================================
        theories_12 = "【12 套剧本理论 (12 Theories) — 灵魂融合适用】\n"
        for name, desc in THEORIES_12.items():
            theories_12 += "  ▸ " + name + ": " + desc + "\n"

        # ============================================================
        # 灵魂融合详情
        # ============================================================
        soul_injection = (
            "【灵魂融合详情 — Phase 17 核心】\n"
            "融合模式: " + str(_pick(soul_fused, "fusion_mode", "F3")) + "\n"
            "主导情感: " + str(_pick(soul_fused, "name", "")) + "\n"
            "融合情感 keys: " + ", ".join(soul_keys) + "\n"
            "权重: " + ", ".join([str(w) for w in (_pick(soul_fused, "weights", [0.5, 0.5]))]) + "\n"
            "融合强度: " + str(_pick(soul_fused, "intensity", 0.5)) + "\n"
            "极性: " + str(_pick(soul_fused, "polarity", "")) + "\n"
            "唤醒度: " + str(_pick(soul_fused, "arousal", "")) + "\n"
            "主导情感视觉锚点: " + str(_pick(soul_fused, "visual_signs", "")[:300]) + "\n"
            "主导情感声音锚点: " + str(_pick(soul_fused, "voice_signs", "")[:300]) + "\n"
            "主导情感面部肌肉: " + str(_pick(soul_fused, "facial_au", "")[:200]) + "\n"
            "主导情感内心独白: " + str(_pick(soul_fused, "inner_monologue", "")[:300]) + "\n"
            "主导情感色彩: " + str(_pick(soul_fused, "color_palette", "")[:300]) + "\n"
            "主导情感音乐节奏: " + str(_pick(soul_fused, "music_tempo", "")[:300]) + "\n"
            "主导情感导演案例: " + str(_pick(soul_fused, "director_examples", "")[:300]) + "\n\n"
            "【灵魂状态 — 当前】\n"
            "灵感指数: " + str(_pick(soul_state, "inspiration", 0.85)) + " — "
            + ("高灵感 = 即兴空间大, 偶发 1-2 个非排练动作"
               if float(_pick(soul_state, "inspiration", 0.85)) > 0.8
               else "中灵感 = 严格按 beat 走")
            + "\n"
            "疲劳指数: " + str(_pick(soul_state, "fatigue", 0.30)) + " — "
            + ("高疲劳 = 表演更慢, 微动作之间停顿 1.5-2.0 秒"
               if float(_pick(soul_state, "fatigue", 0.30)) > 0.6
               else "低疲劳 = 节奏明快, 微动作密集")
            + "\n"
            "怀疑指数: " + str(_pick(soul_state, "doubt", 0.50)) + " — "
            + ("高怀疑 = 镜头响应延迟 0.5-0.8 秒, 像摄影师不敢确定"
               if float(_pick(soul_state, "doubt", 0.50)) > 0.7
               else "中怀疑 = 标准 0.3 秒延迟")
            + "\n"
            "叛逆指数: " + str(_pick(soul_state, "rebelliousness", 0.70)) + " — "
            + ("高叛逆 = 镜头偏 30°+, 运镜非线性, 打破三点光"
               if float(_pick(soul_state, "rebelliousness", 0.70)) > 0.8
               else "中叛逆 = 标准偏移 15°")
            + "\n"
            "精神状态: " + str(_pick(soul_state, "mental_state", "lucid-dreamy")) + " — "
            + ("lucid-dreamy = 清醒但带梦幻色彩, 镜头在现实与诗意之间"
               if "dreamy" in str(_pick(soul_state, "mental_state", "lucid-dreamy"))
               else str(_pick(soul_state, "mental_state", "lucid-dreamy")))
            + "\n\n"
            "【10 灵魂维度】\n"
            "D1 创造力 = " + str(_pick(soul_dims, "creativity", 0.85)) + "\n"
            "D2 想象力 = " + str(_pick(soul_dims, "imagination", 0.85)) + "\n"
            "D3 艺术表达 = " + str(_pick(soul_dims, "artistic_expression", 0.85)) + "\n"
            "D4 镜头语言技巧 = " + str(_pick(soul_dims, "camera_skill", 0.85)) + "\n"
            "D5 氛围掌控 = " + str(_pick(soul_dims, "atmosphere_control", 0.85)) + "\n"
            "D6 精神状态 = " + str(_pick(soul_dims, "mental_state", "lucid-dreamy")) + "\n"
            "D7 灵感时刻 = " + str(_pick(soul_dims, "inspiration", 0.85)) + "\n"
            "D8 叛逆度 = " + str(_pick(soul_dims, "rebelliousness", 0.70)) + "\n"
            "D9 自我怀疑 = " + str(_pick(soul_dims, "self_doubt", 0.50)) + "\n"
            "D10 突破勇气 = " + str(_pick(soul_dims, "breakthrough_courage", 0.85)) + "\n\n"
            "【灵魂导演视角 — " + soul_director + "】\n"
            + str(_pick({
                "王家卫": "用物件代替心理, 时间戳, 60s 慢节奏, 灵魂倾向: longing+nostalgia+loneliness",
                "诺兰": "时间结构即主题, 史诗感, IMAX 客观, 灵魂倾向: awe+wonder+vigilance",
                "PTA": "用可观察行为代替情绪, 70s 迷幻, 慢推长焦, 灵魂倾向: hate+remorse+grief",
                "奉俊昊": "用空间做阶层隐喻, 类型当特洛伊木马, 同场多情绪, 灵魂倾向: disgust+tension+shame",
                "黑泽明": "天气即角色, 极致清晰, 群戏调度, 灵魂倾向: anger+pride+disapproval",
                "库斯杜力卡": "少说话, 沉默即情感, 塞尔维亚乡愁, 灵魂倾向: bittersweet+joy+nostalgia",
                "塔可夫斯基": "时间即主角, 长镜头, 诗意朦胧, 灵魂倾向: trust_surrender+despair+wonder",
                "伯格曼": "脸特写, 沉默, 心理剧",
                "王家卫_1980": "王家卫早期, 短片, 实验性",
                "约阿希姆·提尔": "从房子视角叙事, 家庭代际, 北欧光, 灵魂倾向: remorse+guilt+tenderness",
                "李安": "饭桌戏, 东西方文化张力, 父亲",
                "王家卫+侯孝贤": "长镜头+少台词+物件, 东方美学",
            }, soul_director, "用可观察行为代替情绪, 不写情绪"))
        )

        # ============================================================
        # 1 句话 Logline (灵魂驱动)
        # ============================================================
        logline_1_sentence = (
            "【1 句话总结 (灵魂驱动版)】\n"
            "类型=" + genre + ", 导演=" + director + ", 灵魂导演=" + soul_director + ", "
            "灵魂融合=" + str(_pick(soul_fused, "name", "")) + " (强度 "
            + str(_pick(soul_fused, "intensity", 0.5)) + ", 极性 " + str(_pick(soul_fused, "polarity", "")) + ")\n"
            "Logline: " + (concept_logline if concept_logline else scene[:100]) + "\n"
            "潜文本: " + subtext + "\n"
            "情绪基调: " + mood + "\n"
            "核心卖点: " + core_selling + "\n"
            "差异化: " + differentiation + "\n"
            "受众: " + audience + "\n"
            "参考作品: " + ref_films + "\n"
            "关键道具: " + props + "\n"
            "灵魂状态: 灵感 " + str(_pick(soul_state, "inspiration", 0.85))
            + " / 疲劳 " + str(_pick(soul_state, "fatigue", 0.30))
            + " / 怀疑 " + str(_pick(soul_state, "doubt", 0.50))
            + " / 叛逆 " + str(_pick(soul_state, "rebelliousness", 0.70))
            + " / 精神=" + str(_pick(soul_state, "mental_state", "lucid-dreamy"))
        )

        # ============================================================
        # 组装主输出 (≥ 15000 字符)
        # ============================================================
        main = []
        main.append("=" * 70)
        main.append("【ConceptPitchPro】世界顶级导演集群级 — Phase 17 灵魂注入深度重写")
        main.append("  节点: " + domain_name)
        main.append("  焦点: " + domain_focus)
        main.append("  H3 特殊规范: " + h3_special)
        main.append("  导演专项: " + director_specifics)
        main.append("  灵魂注入: " + extra_inject)
        main.append("=" * 70)
        main.append("")
        main.append("【任务类型】 " + task_type + " (" + genre + ")")
        main.append("【导演风格】 " + director)
        main.append("【灵魂导演】 " + soul_director)
        main.append("【导演方法】 " + director_method)
        main.append("【导演镜头运动倾向】 " + director_motion_pref)
        main.append("【代表作品】 " + _pick(director_meta, "代表作品", "—"))
        main.append("【导演格言】 " + _pick(director_meta, "格言", "—"))
        main.append("【导演灵魂签名】 " + _pick(director_meta, "灵魂签名", "—"))
        main.append("【导演灵魂倾向情感】 " + ", ".join(_pick(director_meta, "灵魂倾向情感", [])))
        main.append("【导演口诀】海辛 (2.5 vs 2.0): 2.5 对专业创作者更友好, 稳定、可控, 愿意服从更具体的导演意图")
        main.append("")
        main.append(logline_1_sentence)
        main.append("")
        main.append(soul_injection)
        main.append("")
        main.append("=" * 70)
        main.append("L1-L7 七层 Prompt 架构 (灵魂注入版)")
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
        main.append("H3 三大字段 (Higgsfield 官方 + 灵魂增强)")
        main.append("=" * 70)
        main.append("")
        main.append(h3_prompt)
        main.append("")
        main.append("=" * 70)
        main.append("30 秒场景单元 6 段式 (卡兹克 + 灵魂状态修正)")
        main.append("=" * 70)
        main.append("")
        main.append(timeline_30s_lines)
        main.append("")
        main.append("=" * 70)
        main.append("5 要素处理 (5 Elements Architecture — 灵魂数据层)")
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
        main.append(director_8_method)
        main.append("")
        main.append(director_8_style)
        main.append("")
        main.append(theories_12)
        main.append("")
        main.append("=" * 70)
        main.append("Seedance 2.5 核心升级 (卡兹克 + 灵魂融合)")
        main.append("=" * 70)
        main.append("")
        main.append("  - 卡兹克 (2.5 SFT): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "—"))
        main.append("  - 卡兹克 (30 秒场景单元): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "—"))
        main.append("  - DiDi_OK (美术优先): " + SEEDANCE_25_QUOTES.get("DiDi_OK_美术", "—"))
        main.append("  - 灵魂融合注: 卡兹克强调'压住随手补戏的冲动', 与灵魂状态 'low inspiration' 时更倾向保守; 高灵感时倾向突破")
        main.append("")
        main.append("=" * 70)
        main.append("9 维光照控制 (CIE LAB + 摄影本体 + 灵魂状态)")
        main.append("=" * 70)
        main.append("")
        for k, v in LIGHTING_9D.items():
            main.append("  - " + k + ": " + v)
        main.append("  - 灵魂光照修正: 灵魂状态 灵感/疲劳 = "
                    + str(_pick(soul_state, "inspiration", 0.85)) + "/"
                    + str(_pick(soul_state, "fatigue", 0.30))
                    + " 决定光比 — 高疲劳低灵感 = 极低光比; 高灵感低疲劳 = 高反差")
        main.append("")
        main.append("=" * 70)
        main.append("11 条 H3 官方规则 (Higgsfield + 灵魂增强)")
        main.append("=" * 70)
        main.append("")
        main.append(inject_h3_rules_11())
        main.append("")
        main.append("=" * 70)
        main.append("导演意图 5 维 (灵魂融合 — 潜文本/关系/主题/留白)")
        main.append("=" * 70)
        main.append("")
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本 + 灵魂融合 " + str(_pick(soul_fused, "name", "")) + ")",
            "主题": mood,
            "留白": "想说但没说出口 - " + props + " 是没寄出的信 (灵魂留白: "
                    + str(_pick(soul_fused, "polarity", "")) + " → "
                    + ("温暖" if str(_pick(soul_fused, "polarity", "")) == "positive"
                       else "苦涩" if str(_pick(soul_fused, "polarity", "")) == "negative"
                       else "不安") + ")",
        }
        main.append(inject_director_intent(intent_5d))
        main.append("")
        # 9 大类型 + 20 导演集群完整列表 (Phase 12 已验证 — 必须在 main_output)
        main.append("【9 大影视类型】 " + " / ".join(GENRE_TYPES))
        main.append("【20 导演集群实战经验】")
        for d in DIRECTORS_20:
            main.append("  - " + d)
        main.append("")
        main.append("【12 灵魂导演 — 来自 director_soul 模块】")
        for d in SOUL_DIRECTORS_12:
            main.append("  - " + d)
        main.append("")
        main.append("【灵魂情感矩阵 — " + str(len(EMOTION_MATRIX_60) if _HAS_SOUL else 48) + " 种情感】")
        if _HAS_SOUL:
            categories = {}
            for ek, ev in EMOTION_MATRIX_60.items():
                cat = _pick(ev, "category", "Other")
                categories.setdefault(cat, []).append(ek)
            for cat, keys in categories.items():
                main.append("  - " + cat + " (" + str(len(keys)) + "): " + ", ".join(keys[:8]) + ("..." if len(keys) > 8 else ""))
        main.append("")
        main.append("【7 大情感融合公式 (F1-F7)】")
        for fk, fv in (EMOTION_FUSION_7.items() if _HAS_SOUL else []):
            main.append("  - " + fk + ": " + _pick(fv, "name", "") + " — " + _pick(fv, "scenarios", ""))
        main.append("")
        main.append("【10 大灵魂维度】")
        if _HAS_SOUL:
            for dk, dv in SOUL_DIMENSIONS_10.items():
                main.append("  - " + dk + ": " + _pick(dv, "name", "") + " — " + _pick(dv, "description", ""))
        main.append("")
        main_output = "\n".join(main)

        # ============================================================
        # 反 AI 词表清洗
        # ============================================================
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ============================================================
        # 第二个输出: 经验矩阵 (灵魂增强)
        # ============================================================
        experience_parts = []
        experience_parts.append("【20+ 导演集群实战经验 — 灵魂映射】\n")
        for d in list(MASTER_DIRECTORS_8.keys()) + [
            "塔可夫斯基", "王家卫", "小津安二郎", "侯孝贤", "库布里克", "伯格曼",
            "贾樟柯", "李安", "蔡明亮", "李沧东", "毕赣", "库斯杜力卡",
        ]:
            experience_parts.append("  - " + d)
        experience_parts.append("")
        experience_parts.append("【12 灵魂导演 — 来自 director_soul】")
        for d in SOUL_DIRECTORS_12:
            experience_parts.append("  - " + d)
        experience_parts.append("")
        experience_parts.append(inject_genre_9_types())
        experience_parts.append("")
        experience_parts.append(director_control_text)
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
        experience_parts.append("【灵魂状态案例库 — 灵感时刻 / 自我怀疑 / 突破勇气】")
        experience_parts.append("  - 灵感时刻 (诺兰《盗梦空间》火车冲入街道)")
        experience_parts.append("  - 灵感时刻 (奉俊昊《寄生虫》暴雨倒流楼梯)")
        experience_parts.append("  - 自我怀疑 (泰伦斯·马力克 反复重剪)")
        experience_parts.append("  - 自我怀疑 (库布里克 反复重拍)")
        experience_parts.append("  - 突破勇气 (诺兰《黑暗骑士》IMAX 拍片)")
        experience_parts.append("  - 突破勇气 (奉俊昊《寄生虫》非线性)")
        experience_parts.append("  - 叛逆 (林奇《穆赫兰道》完全无解释)")
        experience_parts.append("  - 叛逆 (安哲罗普洛斯《永恒与一日》完全非线性)")
        experience_parts.append("")
        experience_parts.append("【灵魂融合案例库 — F1-F7 实战】")
        experience_parts.append("  - F1 单情感: 王家卫《重庆森林》何志武独白 (loneliness 100%)")
        experience_parts.append("  - F2 主次融合: 《情感价值》父亲 (acceptance 70% + remorse 30%)")
        experience_parts.append("  - F3 对等融合: 《花样年华》压抑欲望 (tenderness 50% + repression 50%)")
        experience_parts.append("  - F4 三情感递进: 《步履不停》兴趣→关切→悔恨")
        experience_parts.append("  - F5 矛盾爆炸: 《寄生虫》朴社长地下室 (disgust 100% + fear 100%)")
        experience_parts.append("  - F6 复合三角: 《魅影缝匠》Reynolds 复杂 (love 33% + obsession 33% + control 33%)")
        experience_parts.append("  - F7 情感转化: 《泰坦尼克号》Jack 死时 (love 100% → grief 100%)")
        experience_parts.append("")
        experience = "\n".join(experience_parts)

        # ============================================================
        # 第三个输出: AI 深度处理 (灵魂融合 + 12 套理论 + 191 反 AI)
        # ============================================================
        ai_deep_parts = []
        ai_deep_parts.append("【12 套理论融合 (Phase 12 已验证 + 灵魂融合适用)】")
        for name, desc in THEORIES_12.items():
            ai_deep_parts.append("  - " + name + ": " + desc[:120])
        ai_deep_parts.append("")
        ai_deep_parts.append("【8 大世界顶级导演方法论 — 灵魂驱动】")
        for d, m in DIRECTOR_METHOD_8.items():
            ai_deep_parts.append("  - " + d + ": " + m)
        ai_deep_parts.append("")
        ai_deep_parts.append("【12 灵魂导演 — 来自 director_soul】")
        for d in SOUL_DIRECTORS_12:
            ai_deep_parts.append("  - " + d)
        ai_deep_parts.append("")
        ai_deep_parts.append("【191 反 AI 词表 + 4 轮迭代】")
        ai_deep_parts.append("  瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词")
        ai_deep_parts.append("  4 轮迭代: 1) 草稿 → 2) 反 AI → 3) 人性化 → 4) 导演润色")
        ai_deep_parts.append("")
        ai_deep_parts.append("【沉默 5 规则 + 4 步公式 + 30 秒场景单元 — 灵魂修正】")
        ai_deep_parts.append(inject_silence_mastery_5("对话", 1))
        ai_deep_parts.append("  灵魂修正: 灵魂状态 fatigue=" + str(_pick(soul_state, "fatigue", 0.3))
                              + " 决定沉默长度; doubt=" + str(_pick(soul_state, "doubt", 0.5))
                              + " 决定沉默的深度")
        ai_deep_parts.append("")
        ai_deep_parts.append("【导演意图 5 维 — 灵魂融合增强】")
        ai_deep_parts.append("  1. 感受: " + intent_5d["感受"])
        ai_deep_parts.append("  2. 情感: " + intent_5d["情感"])
        ai_deep_parts.append("  3. 关系: " + intent_5d["关系"])
        ai_deep_parts.append("  4. 主题: " + intent_5d["主题"])
        ai_deep_parts.append("  5. 留白: " + intent_5d["留白"])
        ai_deep_parts.append("")
        ai_deep_parts.append("【L1-L7 七层架构 (Higgsfield Phase 14 + Phase 17 灵魂注入)】")
        ai_deep_parts.append("  L1 意图与验收 — 灵魂核心情感注入")
        ai_deep_parts.append("  L2 资产与引用 — 灵魂艺术表达 D3 注入")
        ai_deep_parts.append("  L3 空间与数量 — 灵魂氛围 D5 + 唤醒度 arousal 注入")
        ai_deep_parts.append("  L4 表演与物理 — 灵魂情感微动作 (visual_signs + voice_signs + facial_au + inner_monologue) 注入")
        ai_deep_parts.append("  L5 摄影与剪辑 — 灵魂状态光影选择 (灵感/疲劳/怀疑/叛逆) 注入")
        ai_deep_parts.append("  L6 声音与对白 — 灵魂 voice_signs 注入")
        ai_deep_parts.append("  L7 风格约束 — 灵魂 color_palette + music_tempo 注入")
        ai_deep_parts.append("")
        ai_deep_parts.append("【9 维光照控制 (CIE LAB + 摄影本体 + 灵魂状态)】")
        for k, v in LIGHTING_9D.items():
            ai_deep_parts.append("  - " + k + ": " + v)
        ai_deep_parts.append("  灵魂光照修正: 灵感/疲劳比 = " + str(_pick(soul_state, "inspiration", 0.85))
                              + "/" + str(_pick(soul_state, "fatigue", 0.30))
                              + " 决定光比")
        ai_deep_parts.append("")
        ai_deep_parts.append("【3 留白 + 3 运镜法则 (Phase 14 核心 + 灵魂状态增强)】")
        ai_deep_parts.append("  留白: 时间 (延迟满足) / 空间 (情绪集中度) / 叙事 (不说尽) — 灵魂怀疑/灵感/叛逆 增强")
        ai_deep_parts.append("  运镜: 破坏首帧完成度 / 非线性运动轨迹 / 制造响应延迟 — 灵魂叛逆/疲劳/怀疑 增强")
        ai_deep_parts.append("")
        ai_deep_parts.append("【灵魂融合 F1-F7 (Phase 17 核心)】")
        if _HAS_SOUL:
            for fk, fv in EMOTION_FUSION_7.items():
                ai_deep_parts.append("  - " + fk + ": " + _pick(fv, "name", "")
                                      + " — 权重 " + _pick(fv, "weight_distribution", "")
                                      + " — 场景: " + _pick(fv, "scenarios", "")
                                      + " — 案例: " + _pick(fv, "director_examples", ""))
        ai_deep_parts.append("")
        ai_deep_parts.append("【10 灵魂维度 (D1-D10) — 注入每个决策】")
        if _HAS_SOUL:
            for dk, dv in SOUL_DIMENSIONS_10.items():
                ai_deep_parts.append("  - " + dk + " (" + _pick(dv, "name", "") + "): " + _pick(dv, "description", "")
                                      + " | 当前值: " + str(_pick({
                                          "D1_创造力": soul_dims.get("creativity", 0.85),
                                          "D2_想象力": soul_dims.get("imagination", 0.85),
                                          "D3_艺术表达力": soul_dims.get("artistic_expression", 0.85),
                                          "D4_镜头语言技巧": soul_dims.get("camera_skill", 0.85),
                                          "D5_画面氛围掌控": soul_dims.get("atmosphere_control", 0.85),
                                          "D6_精神状态": soul_dims.get("mental_state", "lucid-dreamy"),
                                          "D7_灵感时刻": soul_dims.get("inspiration", 0.85),
                                          "D8_叛逆度": soul_dims.get("rebelliousness", 0.70),
                                          "D9_自我怀疑": soul_dims.get("self_doubt", 0.50),
                                          "D10_突破勇气": soul_dims.get("breakthrough_courage", 0.85),
                                      }, dk, 0.85)) + ")")
        ai_deep_parts.append("")
        ai_deep_output = "\n".join(ai_deep_parts)

        # ============================================================
        # Phase 30 双 AI 互审反馈: 实际内容 (基于导演12维数据+场景分析动态生成)
        # ============================================================
        director = _str(kwargs.get("导演风格", ""), "")
        emotion = _str(kwargs.get("情绪基调", ""), "")
        subtext = _str(kwargs.get("潜文本_情感", ""), "")
        intent = _str(kwargs.get("导演意图_观众应感到", ""), "")
        props = _str(kwargs.get("关键道具", ""), "")
        refs = _str(kwargs.get("关键参考片", ""), "")

        prop_list = [p.strip() for p in props.split(",") if p.strip()] if props else []
        ref_list = [r.strip() for r in refs.split(",") if r.strip()] if refs else []

        dp_camera = dp.get("镜头", "") if dp else ""
        dp_light = dp.get("光", "") if dp else ""
        dp_rhythm = dp.get("节奏", "") if dp else ""
        dp_color = dp.get("色彩", "") if dp else ""
        dp_acting = dp.get("表演", "") if dp else ""
        dp_composition = dp.get("构图", "") if dp else ""
        dp_sound = dp.get("声音", "") if dp else ""
        dp_emotion = dp.get("情绪", "") if dp else ""
        dp_works = dp.get("代表作", "") if dp else ""
        dp_objects = dp.get("物件", "") if dp else ""
        dp_era = dp.get("年代", "") if dp else ""

        sc_loc = scene_ctx.get("loc_key", "场景")
        sc_elements = scene_ctx.get("loc_elements", "环境元素")
        sc_time = scene_ctx.get("time_desc", "")
        sc_era = scene_ctx.get("era", dp_era)

        if dp:
            director_borrow = (
                dp_camera + " + " + dp_composition + " + "
                + dp_sound + " + 签名物件: " + dp_objects
            )
        else:
            director_borrow = f"参考 {director} 的标志性镜头语言 + 节奏曲线"

        actual_content_parts = []
        actual_content_parts.append("═" * 50)
        actual_content_parts.append(f"【实际内容 — 6 事件 / 5 角色 / 3 时空 / 30 秒画面】 (基于: {director} + {scene[:30]})")
        actual_content_parts.append("═" * 50)
        actual_content_parts.append("")

        actual_content_parts.append("【6 个具体事件 — 30 秒 6 段分镜】")
        actual_content_parts.append(f"场景: {scene}")
        actual_content_parts.append(f"导演: {director}  |  情绪基调: {emotion}  |  潜文本: {subtext}")
        actual_content_parts.append(f"导演意图: {intent}")
        actual_content_parts.append(f"导演12维签名: 镜头={dp_camera} | 光={dp_light} | 声音={dp_sound} | 色彩={dp_color}")
        actual_content_parts.append("")
        actual_content_parts.append(f"事件 1 [00:00-00:04.5, 建置] — {dp_camera or '镜头建立空间'}, 主角处于 {sc_loc} ({sc_elements}), {sc_time}. 观众第一秒看到: {scene_ctx.get('location_meta', scene[:40])}. 演员动作: 脚步停顿, 呼吸节奏比正常快 30%, 视线从 {sc_elements.split('/')[0] if '/' in sc_elements else sc_loc} 到主角.")
        actual_content_parts.append(f"事件 2 [00:04.5-00:08, 引入] — 转折点, {prop_list[0] if prop_list else '关键道具'} 出现在画面中, 承载 {intent[:40] if intent else subtext[:40] if subtext else '角色意图'}. {dp_acting + '.' if dp_acting else ''}")
        actual_content_parts.append(f"事件 3 [00:08-00:13.2, 互动] — 主角与 {char_b} 产生冲突或接触, 潜文本: {subtext if subtext else '压抑/等待'}. 不用台词, 用身体距离 (1.2→0.4m) 表示关系变化. {dp_rhythm + '.' if dp_rhythm else ''}")
        actual_content_parts.append(f"事件 4 [00:13.2-00:18.5, 升级] — 矛盾升级, 关键节拍: {dp_objects.split('/')[0] if dp_objects and '/' in dp_objects else '道具'} 表面停 0.3 秒 = 犹豫. 声音: {dp_sound if dp_sound else '环境音为主'}.")
        actual_content_parts.append(f"事件 5 [00:18.5-00:25, 高潮] — 情绪峰值 ({dp_emotion if dp_emotion else emotion}), 镜头推到微动作. {dp_acting if dp_acting else '面部 AU 微动作'}.")
        actual_content_parts.append(f"事件 6 [00:25-00:30, 余韵] — 情绪收尾, 镜头留在 {dp_objects.split('/')[-1] if dp_objects and '/' in dp_objects else '最后物件'} 上 2-5 秒, 暗示下一场方向.")
        actual_content_parts.append("")
        actual_content_parts.append("【5 个角色 — 姓名 / 年龄 / 穿着 / 动机】 (用户需填角色名和穿着)")
        actual_content_parts.append("")
        actual_content_parts.append(f"角色 1: 主角 / [姓名: 用户填] ([年龄: 用户填] / [穿着: 用户填] / 核心物品: {prop_list[0] if prop_list else '用户填'}) — 动机: {subtext[:40] if subtext else '基于场景潜文本'}.")
        actual_content_parts.append(f"角色 2: 对方 / [姓名: 用户填] ([年龄: 用户填] / [穿着: 用户填]) — 动机: 与主角形成 {dp_emotion if dp_emotion else '情感'} 张力.")
        if prop_list:
            actual_content_parts.append(f"角色 3: 物品 / {prop_list[0]} — {dp_objects.split('/')[0] if dp_objects else '替代语言'}, 让沉默有重量.")
        if len(prop_list) > 1:
            actual_content_parts.append(f"角色 4: 物品 / {prop_list[1]} — 替代声音, 让情绪有物理痕迹.")
        else:
            actual_content_parts.append(f"角色 4: 物品 / {dp_objects.split('/')[-1] if dp_objects else '[用户填]'} — 替代叙事.")
        actual_content_parts.append(f"角色 5: 环境 / {sc_loc} ({sc_elements}) — 替代叙事, {sc_time if sc_time else '让时间感模糊'}.")
        actual_content_parts.append("")
        actual_content_parts.append("【3 个时空锚点】")
        actual_content_parts.append(f"过去 — {sc_era or dp_era or '场景设定年代'} 之前, {dp_objects.split('/')[0] if dp_objects else '关键物品'} 如何到主角手中.")
        actual_content_parts.append(f"现在 — {sc_era or dp_era or '当下'}, 主角在 {sc_loc} 的此刻处境.")
        actual_content_parts.append("未来 — 镜头暗示方向, 主角下一步行动, 观众期待.")
        actual_content_parts.append("")
        actual_content_parts.append(f"【{director} 具体借什么 (导演12维数据驱动)】")
        actual_content_parts.append(director_borrow)
        actual_content_parts.append("")
        actual_content_parts.append(f"【{director} 标杆参考】")
        if ref_list:
            for r in ref_list:
                actual_content_parts.append(f"- {r}: 借 {dp_camera if dp_camera else '镜头语言'} + {dp_color if dp_color else '调色'} + {dp_acting if dp_acting else '表演风格'}")
        elif dp_works:
            actual_content_parts.append(f"参考: {dp_works} — 借 {dp_camera} + {dp_color}")
        else:
            actual_content_parts.append(f"应参考 {director} 的标志性作品")

        # 拼接到 main_output 开头
        actual_content_block = "\n".join(actual_content_parts)
        main_output = actual_content_block + "\n\n" + main_output
        if kb_section:
            main_output = main_output + kb_section

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ConceptPitchPro": ConceptPitchPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ConceptPitchPro": "💡 概念立项 (环节 1-3, 6-7) — Phase 17 灵魂注入版",
# }
