# -*- coding: utf-8 -*-
"""
Phase 14 - 30 秒场景单元 6 段式分镜 (Higgsfield 卡兹克 2.5 升级版)
================================================
Higgsfield Hell Grind + 卡兹克 2.5 升级版核心: 30 秒接近完整场景单元
6 段式分镜 (建置/引入/互动/冲突/高潮/钩子) - 卡兹克 2.5 升级

Phase 35.9 升级 (分镜专家子 agent):
- 5 维具体化智能解析 (时代/地点/品牌/数字/物件)
- 12 面部 AU 锚点 (FACS Action Units)
- 8 身体动词 (站立/坐下/转身/前倾/后仰/低头/抬头/侧头)
- 8 大导演 + 12 中文导演风格真映射 (王家卫/诺兰/奉俊昊/是枝裕和/...)
- 真正 6 段差异化 (基于场景/导演/情感)
- 30 秒 = 8-12 镜头, 平均 2.5-3.7s/镜头
- ===STORYBOARD_ADDON=== 段注入供下游 parse

5 要素架构:
1. 数据         - 14 部真实短剧 + 4 类创作者实战 + 50 参考输入
2. 上下文缩略   - 类型/演员/情绪/导演 1 句话
3. Skill/Harness- 30s 6 段 + 11 维控制 + 11 H3 规则 + 13 镜头
4. 经验矩阵     - Hell Grind 卡兹克 2.5 升级 + 6 段式分镜
5. AI 深度处理  - 模型压住随手补戏的冲动 (卡兹克 2.5 核心)
"""

import os
import sys
import re

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP,
        H3_RULES_11, SEEDANCE_25_QUOTES, DIRECTOR_CONTROL_11,
        build_30s_timeline, build_alignment_instruction, build_h3_three_fields,
        inject_director_control_11, inject_5_elements,
    )
    from asset_registry_data import ASSET_REGISTRY
    from style_prefix_data import STYLE_PREFIX
    _HAS_DEPS = True
except Exception as e:
    _HAS_DEPS = False
    _DEPS_ERROR = str(e)


# ============================================================
# Phase 35.9 (分镜专家子 agent): 5 维具体化 + 12 AU + 8 身体词
# ============================================================

# 5 维具体化 (时代/地点/品牌/数字/物件) 智能解析
ERA_KEYWORDS = {
    "1980": ["1980", "80 年代", "80s"],
    "1990": ["1990", "1998", "1995", "1994", "90 年代", "90s"],
    "2000": ["2000", "千禧", "2008", "00 年代"],
    "2010": ["2010", "2018", "10 年代"],
    "2020": ["2020", "2024", "现在", "当代", "疫后"],
}
LOCATION_KEYWORDS = {
    "厨房": ["厨房", "灶台", "切菜"],
    "驾驶舱": ["驾驶舱", "飞机", "波音", "747", "737", "驾驶"],
    "婚礼": ["婚礼", "教堂", "花童", "新娘", "新郎"],
    "客厅": ["客厅", "沙发", "电视"],
    "教室": ["教室", "黑板", "课桌"],
    "医院": ["医院", "病床", "手术", "护士"],
    "街道": ["街道", "巷子", "马路", "雨夜街"],
    "雪地": ["雪", "雪山", "雪原"],
    "海边": ["海", "船", "渔港"],
}
BRAND_KEYWORDS = {
    "RADO": ["RADO", "雷达", "雷达表"],
    "可口可乐": ["可口可乐", "Coca-Cola", "可乐"],
    "海尔": ["海尔", "Haier"],
    "康佳": ["康佳", "Konka"],
    "凤凰": ["凤凰", "自行车"],
    "LARK": ["LARK", "白沙"],
    "Marlboro": ["Marlboro", "万宝路"],
    "Panasonic": ["Panasonic", "松下"],
    "Sony": ["Sony", "索尼"],
    "Nikon": ["Nikon", "尼康", "F3"],
}
DIGIT_KEYWORDS = {
    "17 刀": ["17 刀", "切菜循环"],
    "1/4 圈": ["1/4 圈", "搪瓷杯转"],
    "5 拍": ["5 拍", "心跳"],
    "0.4 秒": ["0.4 秒", "咽口水"],
    "2 次": ["敲杯沿 2 次", "敲 2 次"],
    "7 发": ["弹匣 7 发", "7 发子弹"],
    "3 块": ["3 块", "3 块糖"],
    "4 颗": ["4 颗", "4 颗扣子"],
}
PROP_KEYWORDS = {
    "口琴": ["口琴", "harmonica"],
    "信": ["信", "没寄出", "寄出"],
    "照片": ["照片", "全家福"],
    "酒": ["白酒", "白兰地", "威士忌", "半瓶酒"],
    "收音机": ["收音机", "红灯牌", "老式收音机"],
    "搪瓷杯": ["搪瓷杯", "搪瓷"],
    "刀": ["菜刀", "切菜刀"],
    "烟": ["烟", "香烟", "滤嘴"],
    "军牌": ["军牌", "缺角"],
    "凤凰自行车": ["凤凰自行车", "永久自行车"],
}


# 12 面部 AU (FACS Action Units)
FACIAL_AU_12 = {
    "AU1": "Inner Brow Raiser (眉头内提) - 怀疑/惊讶",
    "AU2": "Outer Brow Raiser (眉外提) - 抬眉, 感兴趣",
    "AU4": "Brow Lowerer (皱眉) - 愤怒/专注",
    "AU5": "Upper Lid Raiser (上睑提) - 惊恐",
    "AU6": "Cheek Raiser (颧肌) - 真笑/克制的笑",
    "AU7": "Lid Tightener (眼睑紧) - 怀疑/愤怒",
    "AU9": "Nose Wrinkler (皱鼻) - 厌恶",
    "AU12": "Lip Corner Puller (嘴角拉) - 笑",
    "AU14": "Dimpler (酒窝) - 紧张的笑",
    "AU15": "Lip Corner Depressor (嘴角下拉) - 悲伤",
    "AU17": "Chin Raiser (下颚提) - 悲伤/嘴抿",
    "AU43": "Eyes Closed (闭眼) - 眨眼/闭目",
}

# 8 身体动词 (Phase 35.9 分镜专家定义)
BODY_VERB_8 = {
    "站立": "Standing - 中性基线, 角色默认体态",
    "坐下": "Sitting - 关系缓和, 餐桌/驾驶位/教堂长椅",
    "转身": "Turning - 180°/90° 转身, 戏剧性时刻",
    "前倾": "Leaning Forward - 亲密/靠近/逼问",
    "后仰": "Leaning Back - 退缩/惊讶/拉开距离",
    "低头": "Head Down - 内省/羞愧/失败",
    "抬头": "Head Up - 觉醒/决定/挑战",
    "侧头": "Head Tilt - 好奇/困惑/温柔",
}

# 6 段×8 身体词 矩阵 (Phase 35.9 新增: 每段默认身体动词)
SIX_ACT_BODY_VERB_MATRIX = {
    1: "站立",  # 建置: 中性站立, 远景观察
    2: "坐下",  # 引入: 进入空间, 坐/立切换
    3: "前倾",  # 互动: 靠近对方
    4: "侧头",  # 冲突: 头侧, 怀疑
    5: "抬头",  # 高潮: 抬, 觉醒
    6: "转身",  # 钩子: 转身离开
}


# ============================================================
# 8 大 + 12 中文导演风格映射 (Phase 35.9 分镜专家)
# ============================================================
DIRECTOR_STYLE_MAP = {
    # 8 大世界顶级导演 (来自 director_storyboard_pro.MASTER_DIRECTORS_8)
    "Paul Thomas Anderson (PTA)": {
        "镜头": "85mm 长焦 + 缓推 + 偶发 360° 环轨",
        "光": "钨丝灯 + 自然光混合, 高对比",
        "节奏": "非线性, 时序错位",
        "AU锚": "AU4+AU7+AU12 (克制但精确)",
        "身体": "站立+前倾+侧头",
        "代表": "《木兰花》《血色将至》",
    },
    "Christopher Nolan (诺兰)": {
        "镜头": "IMAX 65mm + 跟踪 + 偶发固定",
        "光": "工业光, 大比度, 单光源",
        "节奏": "信息密度高, 时间折叠剪辑",
        "AU锚": "AU1+AU4+AU7 (克制的紧张)",
        "身体": "站立+转身+抬头",
        "代表": "《盗梦空间》《星际穿越》",
    },
    "奉俊昊 (Bong Joon-ho)": {
        "镜头": "中景 + 横移 + 精确调度",
        "光": "高对比 + 暗部细节",
        "节奏": "类型当特洛伊木马, 喜剧滑向恐怖",
        "AU锚": "AU4+AU9+AU12+AU15 (矛盾表情)",
        "身体": "站立+坐下+前倾+侧头",
        "代表": "《寄生虫》《杀人回忆》",
    },
    "Martin Scorsese (斯科塞斯)": {
        "镜头": "中焦 + 跟拍 + 燃烧式运镜",
        "光": "高对比 + 烟雾 + 红色霓虹",
        "节奏": "高速剪辑 + 流行乐标记时代",
        "AU锚": "AU4+AU5+AU7+AU9 (戏剧化)",
        "身体": "站立+转身+前倾",
        "代表": "《好家伙》《出租车司机》",
    },
    "Denis Villeneuve (维伦纽瓦)": {
        "镜头": "极长焦 135mm + 慢推 + 长时间不切",
        "光": "自然光 + 沙尘/雾气",
        "节奏": "史诗慢节奏, 单镜头信息密度高",
        "AU锚": "AU1+AU4+AU15 (静默压力)",
        "身体": "站立+低头+抬头",
        "代表": "《沙丘》《降临》",
    },
    "Yorgos Lanthimos (兰斯莫斯)": {
        "镜头": "广角 24mm + 鱼眼 + 不规则构图",
        "光": "高对比 + 冷色 + 偶发暖色反差",
        "节奏": "冷调, 突然加速, 偶发冷幽默",
        "AU锚": "AU1+AU4+AU7+AU12 (古怪)",
        "身体": "站立+侧头+坐下",
        "代表": "《可怜的东西》《宠儿》",
    },
    "Greta Gerwig (葛韦格)": {
        "镜头": "中景 + 自然跟拍 + 大量手部特写",
        "光": "暖调 + 自然光 50mm",
        "节奏": "节奏自然, 角色走路的速度",
        "AU锚": "AU6+AU12+AU14 (温柔微笑)",
        "身体": "站立+坐下+前倾+低头",
        "代表": "《伯德小姐》《小妇人》",
    },
    "黑泽明 (Kurosawa)": {
        "镜头": "中焦 + 横移 + 多机位",
        "光": "硬光高反差 + 黑白摄影",
        "节奏": "群戏调度, 节奏精确",
        "AU锚": "AU4+AU5+AU7+AU15 (史诗重负)",
        "身体": "站立+坐下+转身+抬头",
        "代表": "《七武士》《罗生门》",
    },
    # 12 中文导演 (Phase 14 + Phase 35 节点下拉)
    "王家卫": {
        "镜头": "中焦 + 缓推 + 跳切 + 慢镜",
        "光": "霓虹 + 高饱和, 60:30:10",
        "节奏": "非线性时间, 暧昧独白",
        "AU锚": "AU4+AU6+AU12+AU15+AU43 (暧昧, 半闭眼)",
        "身体": "站立+侧头+低头+前倾",
        "代表": "《花样年华》《重庆森林》",
    },
    "诺兰": {
        "镜头": "IMAX 65mm + 跟踪 + 偶发固定",
        "光": "工业光, 大比度, 单光源",
        "节奏": "信息密度高, 时间折叠剪辑",
        "AU锚": "AU1+AU4+AU7 (克制的紧张)",
        "身体": "站立+转身+抬头",
        "代表": "《盗梦空间》《星际穿越》",
    },
    "是枝裕和": {
        "镜头": "固定 + 自然跟拍 + 静观",
        "光": "自然光 + 窗光, 柔光",
        "节奏": "极慢, 30 秒/镜, 留白多",
        "AU锚": "AU12+AU15+AU43 (自然/克制的温柔)",
        "身体": "坐下+站立+低头+侧头",
        "代表": "《步履不停》《小偷家族》",
    },
    "侯孝贤": {
        "镜头": "长镜头 + 远景 + 固定机位",
        "光": "自然光, 低饱和",
        "节奏": "极慢, 环境声 + 远景",
        "AU锚": "AU12+AU15 (留白中的情感)",
        "身体": "站立+坐下+远观",
        "代表": "《悲情城市》《最好的时光》",
    },
    "李沧东": {
        "镜头": "中景 + 缓推 + 极克制",
        "光": "自然光, 低饱和",
        "节奏": "克制中爆发, 5 分钟/镜",
        "AU锚": "AU4+AU12+AU15+AU17 (压抑)",
        "身体": "站立+坐下+前倾+低头",
        "代表": "《燃烧》《诗》",
    },
    "贾樟柯": {
        "镜头": "中景 + 横移 + 流行乐标记",
        "光": "高对比 + 工业光",
        "节奏": "流行歌 + 即兴表演",
        "AU锚": "AU4+AU7+AU12 (即兴, 怀疑)",
        "身体": "站立+坐下+转身",
        "代表": "《小武》《三峡好人》",
    },
    "周星驰": {
        "镜头": "广角 + 快速推拉 + 夸张",
        "光": "高饱和, 戏剧化",
        "节奏": "快 2 秒/镜, 喜剧节奏",
        "AU锚": "AU6+AU12+AU14 (夸张笑)",
        "身体": "站立+坐下+转身+前倾",
        "代表": "《大话西游》《功夫》",
    },
    "毕赣": {
        "镜头": "中焦 + 缓推 + 长镜头",
        "光": "自然光 + 凯里雾气",
        "节奏": "极慢, 诗意留白",
        "AU锚": "AU4+AU15+AU43 (诗意)",
        "身体": "站立+坐下+前倾",
        "代表": "《路边野餐》《地球最后的夜晚》",
    },
    "小津安二郎": {
        "镜头": "固定 + 低机位 + 榻榻米视角",
        "光": "自然光, 低仰角",
        "节奏": "极慢, 静态构图",
        "AU锚": "AU12+AU15 (克制的日常)",
        "身体": "坐下+站立+低头",
        "代表": "《东京物语》《晚春》",
    },
    "塔可夫斯基": {
        "镜头": "长镜头 + 缓推 + 水/火/烛光",
        "光": "烛光 + 自然光混合",
        "节奏": "极慢, 静默 + 5 分钟/镜",
        "AU锚": "AU15+AU17+AU43 (静默沉思)",
        "身体": "站立+坐下+低头",
        "代表": "《镜子》《乡愁》",
    },
    "库布里克": {
        "镜头": "中焦 + 单点透视 + 缓推",
        "光": "烛光 + 单点主光",
        "节奏": "极度精确, 对称构图",
        "AU锚": "AU1+AU4+AU5 (凝视的恐惧)",
        "身体": "站立+坐下+侧头",
        "代表": "《闪灵》《2001太空漫游》",
    },
    "伯格曼": {
        "镜头": "中景 + 特写 + 固定",
        "光": "高对比黑白",
        "节奏": "极慢, 心理戏剧",
        "AU锚": "AU4+AU7+AU15+AU17 (灵魂重负)",
        "身体": "坐下+站立+低头+抬头",
        "代表": "《第七封印》《假面》",
    },
    "李安": {
        "镜头": "中景 + 缓推 + 柔光",
        "光": "柔光 + 古典配乐",
        "节奏": "自然, 角色驱动",
        "AU锚": "AU6+AU12+AU15 (克制的深情)",
        "身体": "坐下+站立+前倾",
        "代表": "《饮食男女》《断背山》",
    },
    "蔡明亮": {
        "镜头": "极长镜头 + 固定 + 远观",
        "光": "自然光, 极低饱和",
        "节奏": "极慢, 留白极多",
        "AU锚": "AU12+AU15+AU43 (近空寂)",
        "身体": "站立+坐下+前倾",
        "代表": "《爱情万岁》《郊游》",
    },
}

# 缺省导演风格
DEFAULT_DIRECTOR_STYLE = {
    "镜头": "中景 + 缓推",
    "光": "自然光",
    "节奏": "中 (5 秒/镜)",
    "AU锚": "AU12+AU15 (默认情感)",
    "身体": "站立+坐下",
    "代表": "—",
}


# ============================================================
# 30 秒场景单元 6 段定义 (Higgsfield + 卡兹克 2.5 升级)
# Phase 35.9 升级: 6 段差异化 + 5 维具体化 + 12 AU 锚点
# ============================================================
SIX_ACT_30S = [
    {
        "id": 1, "stage": "建置 (Establish)", "time": "0:00-0:03", "duration": 3,
        "purpose_template": "{scene} 1 秒全景, 让 AI 认路: 人物在 frame-{side}, 关键物件在 {prop_pos}, 光从 {light_dir}",
        "key_action_template": "Wide static shot, {character_count} 人在固定位置, {first_prop} 接收光线, 无动作无台词",
        "directive_template": "EXACT {character_count} CHARACTERS — NO DUPLICATES + GEO SPATIAL LAYOUT 一次性定位置",
        "ai_pitfall": "模型爱在第 1 秒就放人物动作, 删掉这一秒角色就开始换位",
        "key_skill": "小 hack: 这一秒里让谁蹦一个短词 (如 'hm'), Seedance 更容易把它当独立镜头处理",
    },
    {
        "id": 2, "stage": "引入 (Introduce)", "time": "0:03-0:08", "duration": 5,
        "purpose_template": "主角进入 {scene}, 模型开始有动作发展, 标志 {director} 风格开场",
        "key_action_template": "Character 坐下/站起, 首次接触 {first_prop}, 眼睛先到, 头晚半拍",
        "directive_template": "{director} 标志性开场: {director_motion}, 复杂动作从第一帧直接开始",
        "ai_pitfall": "模型爱加 'uhm'/傻笑/整句台词, prompt 必须下硬性规定: 每个人只说引号里的那句",
        "key_skill": "光从 sky and windows only, 动作开始时眼睛先到, 头晚半拍, 12 AU 锚: {au_anchor}",
    },
    {
        "id": 3, "stage": "互动 (Interact)", "time": "0:08-0:15", "duration": 7,
        "purpose_template": "{scene} 核心情节开始, 主体动作/对话, 身体动词: {body_verb}",
        "key_action_template": "{character_a} 与 {character_b} 互动, {first_prop} 在手, 8 身体词: {body_verb}",
        "directive_template": "听者半句就懂了, 脸已先答, 没台词的人必须保持安静, 12 AU: {au_anchor}",
        "ai_pitfall": "重要事件后立刻切, 模型不消化, 让尾巴进下一镜",
        "key_skill": "让手忙起来: 一边修东西/数东西/倒东西一边聊, 最强重音是突然停下手里的活",
    },
    {
        "id": 4, "stage": "冲突 (Conflict)", "time": "0:15-0:22", "duration": 7,
        "purpose_template": "{scene} 矛盾开始, 戏剧张力, 身体动词: {body_verb}",
        "key_action_template": "{character_a} 与 {character_b} 冲突, 1-2 个 180° axis 微妙变化, 12 AU: {au_anchor}",
        "directive_template": "30 秒这里应该有 1-2 个 180° axis 的微妙变化, 但绝不越线, {director} 风格: {director_pacing}",
        "ai_pitfall": "模型爱 '漂移', 摄影机突然跑到轴线另一边, 180° 锁死",
        "key_skill": "冲突时, 角色必须保持张力, 绝不 'nobody moves' 静止 (会冻结画面)",
    },
    {
        "id": 5, "stage": "高潮 (Climax)", "time": "0:22-0:27", "duration": 5,
        "purpose_template": "{scene} 镜头表达最连贯, 表演密度最高, 关键镜头: 1 个 12s+ 长镜头",
        "key_action_template": "1 句台词 + 1 个关键动作 + 1 个面部表情, {body_verb}, 12 AU: {au_anchor}",
        "directive_template": "3-5 秒高潮内必有: 1 句台词 + 1 个关键动作 + 1 个面部表情, 8 身体词: {body_verb}",
        "ai_pitfall": "模型爱在高潮抢戏, 加新角色, 加新道具",
        "key_skill": "EXACTLY ONE 关键动作, NEVER add another. 分阶段眨眼 (lazy → DOUBLE → HARD reset)",
    },
    {
        "id": 6, "stage": "钩子 (Hook)", "time": "0:27-0:30", "duration": 3,
        "purpose_template": "{scene} 末帧悬念, 引导下一镜, 身体动词: {body_verb}",
        "key_action_template": "末帧: 1 个未说完的台词 / 1 个未完成的动作 / 1 个出框的视线, {body_verb}",
        "directive_template": "末帧应留下: 1 个未说完的台词 / 1 个未完成的动作 / 1 个出框的视线, 12 AU: {au_anchor}",
        "ai_pitfall": "模型爱 '圆满' 收尾, 加 'the end', 完美握手, 大合影",
        "key_skill": "30s 钩子: 把最有趣的元素放在最后一秒, 让观众想看下一秒",
    },
]


# ============================================================
# Phase 35.9 新增: 5 维具体化智能解析
# ============================================================
def extract_5d_specifics(scene, characters, first_prop):
    """
    5 维具体化: 时代 (era) / 地点 (location) / 品牌 (brand) / 数字 (digit) / 物件 (prop)
    智能解析输入字符串,返回 5 维具体化结果。
    """
    specs = {
        "era": "1990s (默认, 中国 90 年代)",  # 默认
        "location": scene if scene else "未指定场景",
        "brand": "无品牌",
        "digit": "0 数字",
        "prop": first_prop if first_prop else "未指定道具",
    }

    # 时代
    for era, kws in ERA_KEYWORDS.items():
        if any(kw in scene for kw in kws) or any(kw in str(first_prop) for kw in kws):
            specs["era"] = era
            break

    # 地点
    for loc, kws in LOCATION_KEYWORDS.items():
        if any(kw in scene for kw in kws):
            specs["location"] = loc
            break

    # 品牌
    for brand, kws in BRAND_KEYWORDS.items():
        if any(kw in str(first_prop) for kw in kws) or any(kw in scene for kw in kws):
            specs["brand"] = brand
            break

    # 数字 (优先从 first_prop 中找)
    for digit, kws in DIGIT_KEYWORDS.items():
        if any(kw in str(first_prop) for kw in kws) or any(kw in scene for kw in kws):
            specs["digit"] = digit
            break

    # 物件
    for prop, kws in PROP_KEYWORDS.items():
        if any(kw in str(first_prop) for kw in kws):
            specs["prop"] = prop
            break

    return specs


# ============================================================
# Phase 35.9 新增: 6 段镜头数智能分配 (8-12 镜头, 平均 2.5-3.7s)
# ============================================================
def distribute_6_act_shot_counts(director):
    """
    6 段镜头数: 段 1 = 1 镜头, 段 6 = 1 镜头, 中间 4 段总共 6-10 镜头
    总数 8-12, 平均 2.5-3.7s/镜头 (30s 30/8=3.75, 30/12=2.5)
    """
    # 导演风格 → 镜头数分配
    if director in ("奉俊昊 (Bong Joon-ho)", "周星驰", "Martin Scorsese (斯科塞斯)"):
        # 快速剪辑风格
        return [1, 2, 2, 2, 2, 1]  # 总 10, 30/10=3.0
    elif director in ("是枝裕和", "侯孝贤", "小津安二郎", "塔可夫斯基", "蔡明亮", "Denis Villeneuve (维伦纽瓦)"):
        # 极慢风格
        return [1, 1, 2, 2, 1, 1]  # 总 8, 30/8=3.75
    elif director in ("王家卫", "Paul Thomas Anderson (PTA)"):
        # 中等
        return [1, 1, 2, 2, 2, 1]  # 总 9, 30/9=3.33
    elif director in ("诺兰", "Christopher Nolan (诺兰)", "Christopher Nolan (诺兰)"):
        # IMAX
        return [1, 1, 2, 2, 2, 1]  # 总 9
    else:
        return [1, 1, 2, 2, 2, 1]  # 默认 9 镜头


# ============================================================
# Phase 35.9 新增: 真正差异化的 6 段生成
# ============================================================
def build_one_act_differentiated(act, idx, scene, characters, first_prop, director,
                                  specs_5d, director_style, shot_count):
    """
    单段差异化生成 - 真正基于场景/导演/5 维/12 AU / 8 身体词。
    每段 ≥ 5 字段 × ≥ 40 字符 = ≥ 200 字符总。
    """
    # 人物解析
    char_list = [c.strip() for c in str(characters).split(",") if c.strip()] if characters else ["主角色"]
    char_a = char_list[0] if len(char_list) > 0 else "主角色"
    char_b = char_list[1] if len(char_list) > 1 else char_a
    character_count = len(char_list)

    # 位置默认值
    side = "left" if idx % 2 == 1 else "right"
    prop_pos = "center-frame" if idx in (1, 5) else f"frame-{side}"

    # 身体动词 (按 6 段矩阵)
    body_verb = SIX_ACT_BODY_VERB_MATRIX.get(idx, "站立")

    # 替换模板
    purpose = act["purpose_template"].format(
        scene=scene, side=side, prop_pos=prop_pos, light_dir=specs_5d["era"] + " 时代的窗光",
        director=director, director_motion=director_style["镜头"],
        body_verb=body_verb, au_anchor=director_style["AU锚"],
        character_a=char_a, character_b=char_b,
    )
    key_action = act["key_action_template"].format(
        character_count=character_count, first_prop=specs_5d["prop"],
        character_a=char_a, character_b=char_b, body_verb=body_verb,
        au_anchor=director_style["AU锚"], director=director,
    )
    directive = act["directive_template"].format(
        character_count=character_count, director=director,
        director_motion=director_style["镜头"], director_pacing=director_style["节奏"],
        au_anchor=director_style["AU锚"], body_verb=body_verb,
    )

    # Shot 列表 (按 shot_count 切分)
    shot_list_lines = []
    duration = act["duration"]
    sub_dur = duration / max(shot_count, 1)
    for j in range(shot_count):
        start_t = idx_to_act_start_time(idx) + j * sub_dur
        end_t = start_t + sub_dur
        shot_label = f"[Shot {idx_to_global_shot(idx, shot_count, j)}]"
        # 每个子镜头 1 行 ≥ 40 字符
        shot_list_lines.append(
            f"{shot_label} 0:{int(start_t):02d}.{int((start_t % 1) * 1000):03d} - "
            f"0:{int(end_t):02d}.{int((end_t % 1) * 1000):03d} | "
            f"{body_verb} + {director_style['光']} | {director} 风格: {director_style['代表']}"
        )

    # 5 维具体化行
    specs5d_line = (
        f"5 维具体化: 时代={specs_5d['era']} | 地点={specs_5d['location']} | "
        f"品牌={specs_5d['brand']} | 数字={specs_5d['digit']} | 物件={specs_5d['prop']}"
    )

    # 12 AU 锚点
    au_anchor_line = f"12 AU 锚: {director_style['AU锚']}"

    # 8 身体词应用
    body_8_line = f"8 身体词: {body_verb} (基于 {director} 风格 + 段 {idx}/6 任务)"

    # 导演秘籍 (含 5 维 + 12 AU + 8 身体)
    # V12.7: key_skill 含 {au_anchor} 占位符, 原版未替换导致残留 — 用 replace 安全替换
    key_skill_text = act['key_skill'].replace('{au_anchor}', str(director_style['AU锚']))
    key_skill_enhanced = (
        f"{key_skill_text} | "
        f"{specs5d_line} | "
        f"{au_anchor_line} | "
        f"{body_8_line}"
    )

    # 拼装
    seg = f"""--- 段 {idx}/6: {act['stage']} ({act['time']}, {act['duration']}秒, {shot_count} 个镜头) ---

目的: {purpose}

关键动作: {key_action}

Prompt 指令: {directive}

模型陷阱: {act['ai_pitfall']}

导演秘籍: {key_skill_enhanced}

{chr(10).join(shot_list_lines)}

[Time] {act['time']} (持续 {act['duration']} 秒, {shot_count} 镜头, 平均 {sub_dur:.2f}s/镜头)

════════════════════════════════════════
"""
    return seg


def idx_to_act_start_time(idx):
    """段 idx 的开始时间 (秒)"""
    starts = [0, 3, 8, 15, 22, 27]
    return starts[idx - 1]


def idx_to_global_shot(idx, shot_count, j):
    """段 idx 第 j 个子镜头的全局镜头号"""
    # 简化: 段 1 = 1 镜头, 段 2-5 各 2 镜头, 段 6 = 1 镜头
    base = [1, 2, 4, 6, 8, 10]
    return base[idx - 1] + j


# ============================================================
# Phase 35.9 新增: 6 段生成主函数
# ============================================================
def build_six_act_30s(
    concept="一个失败的父亲在女儿婚礼上找回她所有生日",
    genre="电影",
    director="是枝裕和",
    characters="ROCO, JAX, REIN",
    scene="训练室, 雨夜 1998",
    mood="压抑中见希望",
    first_prop="一只破旧口琴",
    inner_monologue="我想你/我错了/再给我一次机会",
    task_type="T2VA",
):
    """6 段式 30 秒场景单元生成 - Phase 35.9 真正差异化版"""
    # 5 维具体化
    specs_5d = extract_5d_specifics(scene, characters, first_prop)

    # 导演风格 (查表, 缺省 fallback)
    director_style = DIRECTOR_STYLE_MAP.get(director, DEFAULT_DIRECTOR_STYLE)

    # 6 段镜头数
    shot_counts = distribute_6_act_shot_counts(director)
    total_shots = sum(shot_counts)

    # 头部
    out = f"""════════════════════════════════════════
【30 秒场景单元 6 段式分镜 (Higgsfield + 卡兹克 2.5 升级 - Phase 35.9)】
════════════════════════════════════════

【核心】30 秒 = {total_shots} 镜头, 平均 {30.0/total_shots:.2f}s/镜头, 6 段式分镜, 真正差异化

概念: {concept}
类型: {genre}
导演: {director} - {director_style['代表']} 风格
导演特征: {director_style['镜头']} | 光: {director_style['光']} | 节奏: {director_style['节奏']}
场景: {scene}
情绪: {mood}
人物: {characters} (EXACT N CHARACTERS — NO DUPLICATES)
任务类型: {task_type}
关键道具: {first_prop}
内心独白 (INNER): {inner_monologue}

5 维具体化 (时代/地点/品牌/数字/物件):
  - 时代: {specs_5d['era']}
  - 地点: {specs_5d['location']}
  - 品牌: {specs_5d['brand']}
  - 数字: {specs_5d['digit']}
  - 物件: {specs_5d['prop']}

12 AU 锚: {director_style['AU锚']}
8 身体词: {', '.join(set(director_style['身体'].split('+')))}
导演代表: {director_style['代表']}

════════════════════════════════════════
6 段式分镜 ({total_shots} 镜头 / 30 秒)
════════════════════════════════════════

"""

    # 6 段分别生成 (真正差异化)
    for i, act in enumerate(SIX_ACT_30S, 1):
        out += build_one_act_differentiated(
            act=act, idx=i, scene=scene, characters=characters,
            first_prop=first_prop, director=director,
            specs_5d=specs_5d, director_style=director_style,
            shot_count=shot_counts[i - 1],
        )

    # ===STORYBOARD_ADDON=== 段注入 (供下游 parse)
    addon = build_storyboard_addon_block(
        scene=scene, director=director, first_prop=first_prop,
        total_shots=total_shots, director_style=director_style,
        specs_5d=specs_5d, shot_counts=shot_counts,
    )
    out += "\n" + addon

    return out


def build_storyboard_addon_block(scene, director, first_prop, total_shots,
                                  director_style, specs_5d, shot_counts):
    """
    Phase 35.9 新增: ===STORYBOARD_ADDON=== 段生成,供 DirectorStoryboardPro parse。
    """
    return f"""════════════════════════════════════════
===STORYBOARD_ADDON===
供 DirectorStoryboardPro 解析 (分镜)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 关键道具: {first_prop}
- 导演: {director} - 风格: {director_style['代表']}
- 5 维具体化: 时代={specs_5d['era']} | 地点={specs_5d['location']} | 品牌={specs_5d['brand']} | 数字={specs_5d['digit']} | 物件={specs_5d['prop']}
- 30s 6 段: 1={shot_counts[0]}镜 / 2={shot_counts[1]}镜 / 3={shot_counts[2]}镜 / 4={shot_counts[3]}镜 / 5={shot_counts[4]}镜 / 6={shot_counts[5]}镜 = 总 {total_shots} 镜头
- 镜头时长: 平均 {30.0/total_shots:.2f}s/镜头 (符合 2.5-3.7s 区间)
- 关键镜头: 高潮段 (段 5) 必有 1 个 12s+ 长镜头
- 运动: {director_style['镜头']}
- 光线: {director_style['光']}
- 节奏: {director_style['节奏']}
- 12 AU 锚: {director_style['AU锚']}
- 8 身体词: {director_style['身体']}
- 6 段任务: 起 (建立) / 承 (冲突) / 转 (反转) / 合 (深化) / 高 (爆发) / 余 (留白)
- 反 AI: 不许"特写表现情绪", 要"第 23 秒: 固定机位 14s, 男主背影站在窗前, 雨刷 1Hz 节奏, 突然停 1 拍, 然后加速 1.5Hz"
===END_STORYBOARD_ADDON===
════════════════════════════════════════
"""


def parse_storyboard_addon(text):
    """
    Phase 35.9 新增: 解析 ===STORYBOARD_ADDON=== 段
    返回 dict: {scene_anchor, key_prop, director, specs_5d, shot_counts, total_shots, ...}
    """
    m = re.search(
        r"===STORYBOARD_ADDON===(.*?)===END_STORYBOARD_ADDON===",
        text, re.DOTALL,
    )
    if not m:
        return None
    block = m.group(1)
    result = {}
    for line in block.strip().split("\n"):
        line = line.strip()
        if line.startswith("- "):
            line = line[2:]
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip()
    return result


def build_six_act_h3_prompts(
    concept="一个失败的父亲在女儿婚礼上找回她所有生日",
    genre="电影",
    director="是枝裕和",
    characters="ROCO, JAX, REIN",
    scene="训练室, 雨夜 1998",
    mood="压抑中见希望",
    first_prop="一只破旧口琴",
    task_type="T2VA",
    n_shots=6,
):
    """完整 H3 三大字段 × 6 段 = 30 秒场景 - Phase 35.9 升级"""
    assert _HAS_DEPS, "thirty_sec_six_act requires prompt_builder + anti_ai_vocab deps. Install: pip install -r requirements.txt"

    # 5 维具体化 + 导演风格
    specs_5d = extract_5d_specifics(scene, characters, first_prop)
    director_style = DIRECTOR_STYLE_MAP.get(director, DEFAULT_DIRECTOR_STYLE)
    shot_counts = distribute_6_act_shot_counts(director)
    total_shots = sum(shot_counts)

    # 人物
    char_list = [c.strip() for c in str(characters).split(",") if c.strip()] if characters else ["主角色"]
    char_a = char_list[0] if char_list else "主角色"

    h3 = build_h3_three_fields(
        style="Cinematic, live-action, 35mm film grain",
        shot_1_content=(
            f"Wide static. {scene}. {characters} at fixed position. {first_prop} catches light. "
            f"Camera on door side. No motion. 1 second of pure space. "
            f"Director: {director} ({director_style['代表']}). 12 AU: {director_style['AU锚']}. "
            f"5 维: 时代={specs_5d['era']} 地点={specs_5d['location']} 品牌={specs_5d['brand']} "
            f"数字={specs_5d['digit']} 物件={specs_5d['prop']}."
        ),
        shots_content=[
            f"[Shot {i+1}] At 00:0{i*5}.000, the camera cuts to {SIX_ACT_BODY_VERB_MATRIX.get(i+1, '站立')} + {director_style['镜头']}. "
            f"12 AU 锚: {director_style['AU锚']}. 5 维物件: {specs_5d['prop']}. "
            f"{SIX_ACT_30S[i]['directive_template'].format(character_count=len(char_list), director=director, director_motion=director_style['镜头'], director_pacing=director_style['节奏'], au_anchor=director_style['AU锚'], body_verb=SIX_ACT_BODY_VERB_MATRIX.get(i+1, '站立'))}"
            for i in range(6)
        ],
        soundscape=(
            f"Steady rain taps against the {specs_5d['location']} window. The clock ticks. "
            f"The old radio plays at low volume. Underwater silence in pauses. "
            f"Director {director} audio signature: {director_style['节奏']}."
        ),
        music=(
            f"Sparse piano notes at a slow tempo, joined by sustained low strings that "
            f"gradually increase in volume before fading out at 0:28. {director} style: {director_style['节奏']}."
        ),
        language="Chinese",
    )
    # 对齐指令
    alignment = build_alignment_instruction(task_type, n_shots=total_shots, duration_sec=30.0)
    if alignment:
        h3 = alignment + "\n\n" + h3
    return h3


# ============================================================
# ComfyUI 节点
# ============================================================
class ThirtySecSixAct:
    """Phase 14 - 30 秒场景单元 6 段式分镜 (Higgsfield + 卡兹克 2.5 升级) - Phase 35.9 真正差异化"""

    CATEGORY = "PromptLibrary/Phase14 6段"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("six_act_overview", "act_1_establish", "act_2_introduce", "act_3_interact", "act_4_conflict", "act_5_climax", "act_6_hook", "h3_three_fields_prompt")
    FUNCTION = "build"

    @classmethod
    def INPUT_TYPES(cls):
        # 导演下拉: 8 大世界导演 + 12 中文导演 = 20 个
        all_directors = list(DIRECTOR_STYLE_MAP.keys())
        return {
            "required": {
                "概念": ("STRING", {"default": "一个失败的父亲在女儿婚礼上找回她所有生日", "multiline": True}),
                "类型": (["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"], {"default": "电影"}),
                "导演": (all_directors, {"default": "是枝裕和"}),
                "人物": ("STRING", {"default": "ROCO, JAX, REIN", "multiline": False}),
                "场景": ("STRING", {"default": "训练室, 雨夜 1998", "multiline": True}),
                "情绪": ("STRING", {"default": "压抑中见希望", "multiline": False}),
                "关键道具": ("STRING", {"default": "一只破旧口琴", "multiline": False}),
                "内心独白": ("STRING", {"default": "我想你/我错了/再给我一次机会", "multiline": True}),
                "任务类型": (["T2VA", "I2VA", "FL2VA", "L2VA"], {"default": "T2VA"}),
                "启用反AI": ("BOOLEAN", {"default": True}),
            },
        }

    def build(self, 概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 内心独白, 任务类型, 启用反AI, **kwargs):
        # 6 段概览 (Phase 35.9 真正差异化)
        overview = build_six_act_30s(概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 内心独白, 任务类型)
        # 6 段分别 (Phase 35.9 真正差异化, 来自 overview 解析)
        act_segments = re.split(r"--- 段 (\d)/6:", overview)
        # act_segments[0] = header, [1]=idx, [2]=content, [3]=idx, [4]=content, ...
        act_strings = {}
        for i in range(0, len(act_segments) - 1, 2):
            idx = act_segments[i + 1]
            content = act_segments[i + 2] if i + 2 < len(act_segments) else ""
            # 截到下一个 "--- 段" 或 "===STORYBOARD_ADDON===" 或 "════════"
            cut = re.search(r"--- 段 \d/6:|===STORYBOARD_ADDON===|════════", content)
            seg_text = content[:cut.start()] if cut else content
            act_strings[f"act_{idx}"] = seg_text.strip()

        # H3 prompt (Phase 35.9 升级)
        director_style = DIRECTOR_STYLE_MAP.get(导演, DEFAULT_DIRECTOR_STYLE)
        total_shots = sum(distribute_6_act_shot_counts(导演))
        h3 = build_six_act_h3_prompts(概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 任务类型, n_shots=total_shots)

        # 注入 11 维导演控制
        if _HAS_DEPS:
            try:
                control_block = inject_director_control_11()
                overview += "\n" + control_block
            except Exception:
                pass

        # 反 AI
        if 启用反AI and _HAS_DEPS:
            try:
                overview = inject_anti_ai_rules(overview)
                h3 = inject_anti_ai_rules(h3)
            except Exception:
                pass

        return (
            overview,
            act_strings.get("act_1", "段 1 缺失"),
            act_strings.get("act_2", "段 2 缺失"),
            act_strings.get("act_3", "段 3 缺失"),
            act_strings.get("act_4", "段 4 缺失"),
            act_strings.get("act_5", "段 5 缺失"),
            act_strings.get("act_6", "段 6 缺失"),
            h3,
        )


# ============================================================
# 演示
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Phase 14 - 30 秒场景单元 6 段式 (Higgsfield + 卡兹克 2.5 升级 - Phase 35.9)")
    print("=" * 70)
    n = ThirtySecSixAct()
    print(f"ComfyUI 节点: CATEGORY={n.CATEGORY}, RETURN_NAMES={n.RETURN_NAMES}")
    print()
    overview = build_six_act_30s()
    print(overview[:2500])
    print("...")
