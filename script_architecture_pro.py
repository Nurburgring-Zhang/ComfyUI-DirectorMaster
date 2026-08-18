# -*- coding: utf-8 -*-
"""
ScriptArchitecturePro — 故事架构节点
=====================================
(节点 1/3 — 剧本输出拆分为 3 个节点)

功能:
- 接收用户故事/题材
- 输出: 世界观 + 主题 + 角色小传 + 结构 + 节奏曲线
- 内置反 AI 词表 + 真实导演剧本微调
- 强制具体细节铁律
- 多轮迭代机制
- **Phase 17.6 灵魂注入**: 真实调用 director_soul.soul_inject_simple,
  按 灵魂_主导情感 / 灵魂_场景权重 / 灵魂_次要情感 / 灵魂_融合模式
  四个灵魂输入动态驱动故事架构, 不同情感真的会输出不同的
  情感核 / 强度 / 极性 / 视觉表现 / 色彩 / 音乐 / 灵魂状态 / 10 维
- **Phase 35.9 12 套理论真调用**: 真实 import knowledge_base.narrative_structures.NARRATIVE_STRUCTURES
  12 套理论 (Save the Cat / Hero's Journey / McKee / 三幕剧 / 因果链 / 反转 / 余韵 / 节拍 / 转折点 / 伏笔 / 情绪因果 / 物件因果),
  选中结构后, 真生成该结构的 8-15 个具体节拍 (position+beat+function) 而不是只输出 "Save the Cat" 字符串.
- **Phase 35.9 5 维具体化贯穿**: 时代/地点/品牌/数字/物件 五维, 强制嵌入到反 AI 块+结构骨架+节拍块.
- **Phase 35.9 INTENT_ADDON 解析**: 从 director_soul 返回的 inj 字符串中正则提取 ===INTENT_ADDON=== 段,
  拆出 4 类意图 / 潜文本 / 导演意图强度 / 灵魂状态, 拼为结构化字段.
- **Phase 35.9 跨导演差异化**: 王家卫/诺兰/奉俊昊/侯孝贤 4 套故事骨架模板, 相同结构下拍点位置+function 完全不同.
- **Phase 35.9 跨类型差异化**: 爱情/悬疑/动作/剧情/惊悚 5 类, 各有节拍密度/反转位置/余韵参数.
- **Phase 35.9 跨场景差异化**: 5 大场景 (雨夜/驾驶舱/婚礼/葬礼/审讯) 各自有专属的"开场-中点-高潮-结局"骨架.

输入 (20 个核心参数 + 4 个灵魂参数 + 1 题材类型):
- 题材/题材描述
- 时长/规模
- 主题(可多选 12 类)
- 风格基调(63 导演之一)
- 时代背景
- 地域文化
- 结构(经典三幕/英雄之旅/多线/反结构)
- 主角数量
- 反派数量
- 核心冲突类型
- 情绪曲线(7 点)
- 节奏密度
- 留白比例
- 反转次数
- 多线并行
- 隐喻层数
- 哲学内核
- 受众
- 禁忌词(额外反 AI)
- 启用反 AI 规则

灵魂输入 (Phase 17.6):
- 灵魂_主导情感 (auto + 60 EMOTION keys)
- 灵魂_次要情感 (auto + 60 keys, 单选, 走 secondary 列表)
- 灵魂_场景权重 (FLOAT 0-1, 决定故事强度)
- 灵魂_融合模式 (auto + F1-F7 7 种融合模式)

Phase 35.9 新增:
- 题材类型 (爱情/悬疑/动作/剧情/惊悚 5 大类型)
- 场景标签 (雨夜/驾驶舱/婚礼/葬礼/审讯 5 大场景)

输出 (3-tuple, 不破坏现有 API):
- story_architecture: 注入反 AI 规则 + 真实导演微调 + 灵魂注入 + 12 套理论节拍 + 5 维具体化 + INTENT_ADDON 解析 + 跨导演/类型/场景骨架 的完整 prompt
- anti_ai_rules:     反 AI 词表 (1000 字符)
- iteration_chain:   多轮迭代链
"""

import os
import sys
import json
import re

# 反 AI + 真实导演微调
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        ITERATION_TEMPLATES,
        inject_anti_ai_rules,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)

# ============================================================
# 灵魂注入依赖 (Phase 17.6) — 真实接入 director_soul
# ============================================================
try:
    from director_soul import (
        soul_inject_simple,
        build_soul_injection,
        _build_soul_addons,
        fuse_emotions,
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
    )
    _HAS_SOUL = True
    _HAS_SOUL_FULL = True  # build_soul_injection / _build_soul_addons 是否可用
except Exception as _soul_err:  # pragma: no cover
    _HAS_SOUL = False
    _HAS_SOUL_FULL = False
    _SOUL_ERROR = str(_soul_err)
    # 兜底常量, 保证 INPUT_TYPES 仍然能返回
    EMOTION_MATRIX_60 = {}
    EMOTION_FUSION_7 = {}

# ============================================================
# Phase 35.9: 12 套叙事理论真调用 — 真实 import NARRATIVE_STRUCTURES
# ============================================================
try:
    from knowledge_base.narrative_structures import (
        NARRATIVE_STRUCTURES,
        NARRATIVE_DECISION,
        get_structure_with_decision,
    )
    _HAS_NARRATIVE = True
except Exception as _narr_err:
    _HAS_NARRATIVE = False
    _NARR_ERR = str(_narr_err)
    NARRATIVE_STRUCTURES = {}
    NARRATIVE_DECISION = {}


# 主题分类(12 大类,真实人类剧作主题)
THEMES = [
    "爱与失去",
    "家庭与代际",
    "身份与归属",
    "权力与反抗",
    "孤独与连接",
    "记忆与时间",
    "城市与异化",
    "战争与和平",
    "信仰与怀疑",
    "阶层与流动",
    "生与死",
    "自由与责任",
]

# 经典叙事结构 — 与 NARRATIVE_STRUCTURES 12 套 key 一一映射
STRUCTURES = [
    "经典三幕剧",
    "英雄之旅 12 阶段",
    "多线平行收敛",
    "非线性时间",
    "回环结构",
    "反结构 / 反高潮",
    "群像叙事",
    "公路片",
    "成长小说 (Bildungsroman)",
    "社会派推理",
    "心理悬疑",
    "日常流 (大时间跨度)",
]

# 把 STRUCTURES label → NARRATIVE_STRUCTURES key
# 因为 STRUCTURES 12 个, NARRATIVE_STRUCTURES 也是 12 个, 但 label 完全不同
# 用 Phase 35.9 设计的 12 套理论英文 key 显式映射:
LABEL_TO_STRUCT_KEY = {
    "经典三幕剧": "classic_three_act",
    "英雄之旅 12 阶段": "hero_journey",
    "多线平行收敛": "parallel_convergence",
    "非线性时间": "nonlinear",
    "回环结构": "in_medias_res",          # 倒叙+回环, 共用 in_medias_res 节拍
    "反结构 / 反高潮": "emotional_rollercoaster",  # 反结构, 用情绪过山车非线性节拍
    "群像叙事": "parallel_convergence",    # 群像也是多线交汇
    "公路片": "hero_journey",             # 公路片 = 英雄之旅变体
    "成长小说 (Bildungsroman)": "descent_redemption",  # 成长 = 沉沦救赎
    "社会派推理": "mystery_reveal",        # 推理 = 揭秘
    "心理悬疑": "buildup_payoff",         # 心理悬疑 = 伏笔回收
    "日常流 (大时间跨度)": "kishōtenketsu",  # 日常流 = 起承转合东方叙事
}

# 12 套理论全名映射 (中英对照 + 源作者)
THEORY_DISPLAY = {
    "classic_three_act": "经典三幕剧 (Aristotle / Field)",
    "hero_journey": "英雄之旅 12 阶段 (Joseph Campbell)",
    "save_the_cat": "救猫咪 15 节拍 (Blake Snyder)",
    "kishōtenketsu": "起承转合东方叙事 (中/日/韩)",
    "in_medias_res": "倒叙从中间开始 (Homer / Quentin Tarantino)",
    "nonlinear": "非线性碎片拼贴 (Tarantino / Nolan)",
    "short_drama_hook": "短剧钩子结构 8 节拍 (竖屏爆款)",
    "mystery_reveal": "悬疑揭秘结构 (Hitchcock / Fincher)",
    "parallel_convergence": "平行交汇结构 (Iñárritu / Nolan)",
    "emotional_rollercoaster": "情绪过山车 (短视频情绪向)",
    "buildup_payoff": "伏笔-回收结构 (契诃夫之枪)",
    "descent_redemption": "沉沦-救赎结构 (Frank Darabont)",
}

# McKee (Story), 物件因果 (Object Causality), 情绪因果 (Affective Causality),
# 反转 (Reversal), 余韵 (Aftertaste), 转折点 (Turning Point),
# 节拍 (Beat), 因果链 (Causal Chain), 伏笔 (Foreshadow) —
# 这 8 套不算独立的 beat_map, 是从 12 套里抽取的子模块 (Phase 35.9 设计)
THEORY_CROSSCUTTING = {
    "Save the Cat": "save_the_cat",
    "Hero's Journey": "hero_journey",
    "McKee Story": "classic_three_act",   # McKee Story = 三幕剧的镜头化展开
    "三幕剧": "classic_three_act",
    "因果链": "buildup_payoff",          # 因果链 = 伏笔回收的核心机制
    "反转": "short_drama_hook",          # 反转 = 短剧钩子结构核心
    "余韵": "descent_redemption",        # 余韵 = 沉沦救赎结尾
    "节拍": "save_the_cat",              # 节拍 = 救猫咪 15 节拍
    "转折点": "hero_journey",            # 转折点 = 英雄之旅跨越门槛
    "伏笔": "buildup_payoff",            # 伏笔 = 契诃夫之枪
    "情绪因果": "emotional_rollercoaster",  # 情绪因果 = 情绪过山车
    "物件因果": "in_medias_res",         # 物件因果 = 倒叙, 物件贯穿
}

# 核心冲突类型
CONFLICTS = [
    "人与人",
    "人与自我",
    "人与社会",
    "人与自然",
    "人与命运",
    "人vs过去",
    "理想vs现实",
    "道德vs欲望",
]

# 灵魂可选情感 (auto + none + 60 矩阵 keys)
SOUL_EMOTION_KEYS = (
    ["auto", "none"] + list(EMOTION_MATRIX_60.keys())
    if _HAS_SOUL else ["auto", "none"]
)
SOUL_FUSION_MODES = [
    "auto",
    "F1_单情感主导",
    "F2_双情感主次融合",
    "F3_双情感对等融合",
    "F4_三情感递进融合",
    "F5_矛盾情感爆炸",
    "F6_复合情绪三角",
    "F7_情感转化",
]

# Phase 35.9: 题材类型 (5 大类型, 影响节拍密度+反转位置+余韵)
GENRE_TYPES = ["爱情", "悬疑", "动作", "剧情", "惊悚"]

# Phase 35.9: 场景标签 (5 大场景, 影响开场-中点-高潮骨架)
SCENE_TAGS = [
    "雨夜",
    "驾驶舱",
    "婚礼",
    "葬礼",
    "审讯",
]

# ============================================================
# 跨导演骨架 (Phase 35.9): 3 导演真实差异化
# 同一结构 (如 classic_three_act), 4 导演给出完全不同的拍点位置+function
# ============================================================
DIRECTOR_SKELETON = {
    "王家卫": {
        "signature_object": "凤梨罐头 / 雨 / 时钟 / 走廊",
        "signature_line": "我们最接近的时候, 我跟她之间的距离只有 0.01 公分",
        "pacing_rule": "留白 > 50%, 单场戏 < 90s, 情绪在沉默中发酵",
        "beat_override": {
            # 王家卫特色: 0% 重复开场 (回环), 中点是错过的相遇, 高潮是一段独白
            "classic_three_act": [
                {"position": 0.0, "beat": "开场", "function": "一个物件特写, 暗示时间已过 (凤梨罐头的保质期 2024-05-01)"},
                {"position": 0.15, "beat": "第一转折", "function": "走廊里的擦肩, 慢镜头 1.5x, 雨刷 1Hz 节奏"},
                {"position": 0.50, "beat": "中点", "function": "电话亭里拨了 7 个数字, 又挂断 (错过)"},
                {"position": 0.75, "beat": "第二转折", "function": "一段独白, 关于'距离 0.01 公分'的内心独白, 12s"},
                {"position": 0.95, "beat": "结局", "function": "回到开场物件, 凤梨罐头换成 1996 年的雪糕, 时间已过"},
            ],
        },
    },
    "诺兰": {
        "signature_object": "陀螺仪 / 时钟 / 火车 / 失忆笔记",
        "signature_line": "我希望通过这个时间结构, 让观众在结尾感到时间才是真正的主角",
        "pacing_rule": "信息密度 > 80%, 时间折叠, 真相在最后一分钟揭示",
        "beat_override": {
            "classic_three_act": [
                {"position": 0.0, "beat": "开场", "function": "高潮片段 (火车出轨/陀螺倒下) 提前"},
                {"position": 0.10, "beat": "时间回溯", "function": "'XX 小时前'字幕"},
                {"position": 0.50, "beat": "中点", "function": "双线平行剪辑, 观众发现两条线是同一人"},
                {"position": 0.75, "beat": "第二转折", "function": "黑色笔记本最后一页: 'Don't believe your lies'"},
                {"position": 0.95, "beat": "结局", "function": "回到开场, 同一画面但主角做出不同选择"},
            ],
        },
    },
    "奉俊昊": {
        "signature_object": "楼梯 / 石头 / 气味 / 汉堡",
        "signature_line": "我希望通过楼梯空间, 让观众感到阶层",
        "pacing_rule": "上下半场节奏反转, 上半场喜剧/下半场惊悚",
        "beat_override": {
            "classic_three_act": [
                {"position": 0.0, "beat": "开场", "function": "气味 (廉价香水 / 高级红酒) 制造阶层对比"},
                {"position": 0.20, "beat": "第一转折", "function": "楼梯空间第一次出现, 主角向上爬 1 层"},
                {"position": 0.50, "beat": "中点", "function": "下暴雨, 全家人在半地下室的雨声中对话, 阶层困境揭示"},
                {"position": 0.75, "beat": "第二转折", "function": "楼梯跌落, 主角从上层跌回下层, 物理 = 阶层"},
                {"position": 0.95, "beat": "结局", "function": "在宴会上闻到廉价香水味, 观众知道是同一个人"},
            ],
        },
    },
    "侯孝贤": {
        "signature_object": "风 / 海 / 远山 / 沉默",
        "signature_line": "我希望通过沉默, 让观众听见风听见海听见这个人的心",
        "pacing_rule": "固定机位长镜头 > 10s, 几乎无对白",
        "beat_override": {
            "classic_three_act": [
                {"position": 0.0, "beat": "开场", "function": "远山 30s 固定机位, 一片云飘过"},
                {"position": 0.30, "beat": "第一转折", "function": "人物走入画面, 走路 25s, 无对白"},
                {"position": 0.50, "beat": "中点", "function": "海浪声 + 风的低鸣, 人物坐下, 看着远方"},
                {"position": 0.80, "beat": "第二转折", "function": "一个孩子在远处跑过, 主角没说话, 站起来走"},
                {"position": 0.95, "beat": "结局", "function": "和开场同一片山, 但云的位置变了"},
            ],
        },
    },
    "default": {
        "signature_object": "时代物件 (按 题材 自动选择)",
        "signature_line": "(通用导演风格)",
        "pacing_rule": "标准 120 分钟节奏",
        "beat_override": {},
    },
}

# ============================================================
# 跨类型参数 (Phase 35.9): 5 类型节拍密度+反转位置+余韵
# ============================================================
GENRE_PARAMS = {
    "爱情": {
        "beat_density": "中 (每幕 3-4 个节拍)",
        "reversal_position": "中点 (50%)",
        "aftertaste_seconds": 8.0,
        "must_include": ["错过的相遇", "沉默 5s+", "手部特写", "回忆闪回 1 次"],
    },
    "悬疑": {
        "beat_density": "密 (每幕 5-6 个节拍)",
        "reversal_position": "75% (第二转折处)",
        "aftertaste_seconds": 12.0,
        "must_include": ["误导高潮", "被忽略的细节", "第二次推翻", "契诃夫之枪"],
    },
    "动作": {
        "beat_density": "极密 (每幕 6-7 个节拍)",
        "reversal_position": "25%/50%/75% (三次反转)",
        "aftertaste_seconds": 3.0,
        "must_include": ["物理冲突", "追车/枪战", "12s+ 长镜头", "爆炸前 1s 静默"],
    },
    "剧情": {
        "beat_density": "疏 (每幕 2-3 个节拍)",
        "reversal_position": "中点 + 结尾 (双反转)",
        "aftertaste_seconds": 15.0,
        "must_include": ["家庭饭桌", "雨/雪/季节", "老人独白", "时代背景物件"],
    },
    "惊悚": {
        "beat_density": "密 (每幕 4-5 个节拍)",
        "reversal_position": "35% (早期反转)",
        "aftertaste_seconds": 10.0,
        "must_include": ["阴影长 5s+", "声音延迟 0.5s", "镜子/倒影", "心跳声 1Hz"],
    },
}

# ============================================================
# 跨场景骨架 (Phase 35.9): 5 场景专属的开场-中点-高潮-结局
# ============================================================
SCENE_SKELETON = {
    "雨夜": {
        "open": "雨刷 1Hz 节奏, 路灯在水洼里的倒影, 一个 12s 的固定机位",
        "midpoint": "突然停电 1.5s, 只有雨声, 主角说了一句 8 字内对白",
        "climax": "雨突然停, 远景雷声延迟 3 秒, 主角做出选择",
        "ending": "回到开场同一水洼, 雨又开始下, 但雨刷频率从 1Hz 变成 1.5Hz",
    },
    "驾驶舱": {
        "open": "仪表盘数字 (127 km/h, 油量 23%, 里程 234567)",
        "midpoint": "后视镜出现一辆车, 跟随 7 秒, 观众不知道是同一人还是另一个人",
        "climax": "方向盘急转, 0.8s 内完成 90 度, 时间在那一刻凝固",
        "ending": "停车, 引擎熄火, 雨声取代引擎声, 主角关掉大灯",
    },
    "婚礼": {
        "open": "花瓣特写 (玫瑰, 199 朵), 镜头缓慢后拉揭示整个教堂",
        "midpoint": "新娘走过 28 米红毯, 在第 14 米停 2 秒, 所有人屏息",
        "climax": "司仪说'你愿意吗' 之前 1s 的静默, 教堂钟声",
        "ending": "戒指交换, 但镜头切到宾客席, 一个前任正在微笑, 不说话",
    },
    "葬礼": {
        "open": "黑伞特写, 雨滴 0.3s 一滴, 一双手把黑伞递给老人",
        "midpoint": "棺材入土, 泥土声 5s, 老人拿出一封没寄出的信",
        "climax": "一个孩子跑过来叫'爷爷', 老人蹲下, 信掉进土里",
        "ending": "信被埋, 但画面里有人捡到那封信, 是另一场葬礼的'那封信'",
    },
    "审讯": {
        "open": "台灯特写 (45 度角), 灯丝嗡嗡声, 一双手进入画面",
        "midpoint": "问'你当时在想什么', 5 秒静默, 只有台灯嗡嗡声",
        "climax": "嫌疑人笑了一下, 0.8s 短镜头, 观众第一次看到他的眼睛",
        "ending": "审讯官关掉录音机, 但嫌疑人继续说话, 镜头一直在他脸上",
    },
}


# ============================================================
# 灵魂注入块 (Phase 17.6 标准化输出)
# ============================================================
def _build_soul_injection(
    soul_primary,
    soul_secondary,
    soul_scene_weight,
    soul_fusion_mode,
    director,
    scene_context,
    story_intensity=None,
    scene_progress=0.5,
):
    """
    真实调用 director_soul.soul_inject_simple 注入灵魂.
    返回 4 元组: (injection_str, fused_dict, soul_state, soul_dims)
    失败时回落到中性占位, 不抛异常.

    Phase 35.9 增强: 同时调用 build_soul_injection 拿到完整 14 段(含 INTENT_ADDON),
    并在 inj 字符串中拼接它, 让 INTENT_ADDON 段真正出现在 prompt 中.
    """
    if not _HAS_SOUL:
        return (
            "【灵魂注入 - 依赖未加载】\n请检查 director_soul.py 是否存在: " + _SOUL_ERROR,
            {"name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
             "arousal": "medium", "emotions": [], "fusion_mode": "none",
             "visual_signs": "", "voice_signs": "", "facial_au": "",
             "inner_monologue": "", "color_palette": "", "music_tempo": ""},
            {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
             "rebelliousness": 0.6, "mental_state": "neutral"},
            {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
             "camera_skill": 0.8, "atmosphere_control": 0.8,
             "mental_state": "neutral", "inspiration": 0.8,
             "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7},
        )

    # 1. 解析输入 — soul_inject_simple 内部已做 alias 解析
    primary = soul_primary if soul_primary not in (None, "", "none") else "auto"
    secondary = None
    if soul_secondary and soul_secondary not in (None, "", "none", "auto"):
        secondary = [soul_secondary]

    # 2. 真实调用统一 wrapper
    try:
        inj, fused, soul_state, soul_dims = soul_inject_simple(
            primary=primary,
            scene_weight=float(soul_scene_weight),
            director=director or "默认",
            secondary=secondary,
            fusion_mode=soul_fusion_mode or "auto",
            story_intensity=story_intensity,
            scene_progress=scene_progress,
            scene_context=scene_context or "",
        )
        if not fused:
            fused = {
                "name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
                "arousal": "medium", "emotions": [], "fusion_mode": "none",
                "visual_signs": "", "voice_signs": "", "facial_au": "",
                "inner_monologue": "", "color_palette": "", "music_tempo": "",
            }
        if not soul_state:
            soul_state = {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
                          "rebelliousness": 0.6, "mental_state": "neutral"}
        if not soul_dims:
            soul_dims = {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
                         "camera_skill": 0.8, "atmosphere_control": 0.8,
                         "mental_state": "neutral", "inspiration": 0.8,
                         "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7}

        # Phase 35.9: 追加完整 14 段(含 INTENT_ADDON), 不破坏原 inj 字符串
        if _HAS_SOUL_FULL and isinstance(inj, str):
            try:
                # 把 story_emotion_keys 构造好
                if primary in (None, "", "auto"):
                    primary_key = "loneliness"
                else:
                    primary_key = primary
                if secondary and len(secondary) > 0:
                    emotion_keys = [primary_key] + list(secondary)
                else:
                    emotion_keys = [primary_key]
                # 真实调 _build_soul_addons 拿完整 14 段 (含 ===INTENT_ADDON===)
                director_sig = fused.get("name", "") if isinstance(fused, dict) else ""
                soul_state_for_addons = {
                    "current_inspiration_index": soul_state.get("inspiration", 0.7),
                    "current_fatigue_index": soul_state.get("fatigue", 0.3),
                    "current_doubt_index": soul_state.get("doubt", 0.5),
                    "current_rebelliousness_index": soul_state.get("rebelliousness", 0.6),
                    "current_mental_state": soul_state.get("mental_state", "neutral"),
                }
                soul_dims_for_addons = dict(soul_dims) if soul_dims else {
                    "creativity": 0.85, "imagination": 0.85, "artistic_expression": 0.85,
                    "camera_skill": 0.85, "atmosphere_control": 0.85,
                    "mental_state": "neutral", "inspiration": 0.85,
                    "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7,
                }
                addons_str = _build_soul_addons(
                    fused=fused if isinstance(fused, dict) else {"name": "Neutral 中性"},
                    director=director or "默认",
                    director_sig=director_sig,
                    soul_dims=soul_dims_for_addons,
                    soul_state=soul_state_for_addons,
                    scene=scene_context or "",
                    story_intensity=float(story_intensity) if story_intensity is not None else 0.5,
                    scene_progress=scene_progress if scene_progress is not None else 0.5,
                )
                if isinstance(addons_str, str) and "===INTENT_ADDON===" in addons_str:
                    inj = inj + "\n\n" + addons_str
            except Exception:
                # _build_soul_addons 失败不影响主流程
                pass

        return inj, fused, soul_state, soul_dims
    except Exception as _e:
        # 真出错了: 用最小占位返回, 不要让整个 build 崩
        return (
            "【灵魂注入 - 运行失败】\n" + str(_e),
            {"name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
             "arousal": "medium", "emotions": [], "fusion_mode": "none",
             "visual_signs": "", "voice_signs": "", "facial_au": "",
             "inner_monologue": "", "color_palette": "", "music_tempo": ""},
            {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
             "rebelliousness": 0.6, "mental_state": "neutral"},
            {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
             "camera_skill": 0.8, "atmosphere_control": 0.8,
             "mental_state": "neutral", "inspiration": 0.8,
             "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7},
        )


# ============================================================
# Phase 35.9: 12 套理论真调用 — 真实生成节拍块
# ============================================================
def _render_12_theories_block(struct_label, struct_key, director_skel):
    """
    真实调用 NARRATIVE_STRUCTURES, 把选中结构的 beat_map 渲染为
    "1/8 节点 (position%) 节拍: function" 的可执行节拍块.
    若该导演有 beat_override (王家卫/诺兰/奉俊昊/侯孝贤),
    用导演专属 override 替换, 保证跨导演拍点位置不同.
    """
    lines = []
    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append("【Phase 35.9: 12 套叙事理论真调用 (Narrative Beats)】")
    lines.append("════════════════════════════════════════")

    # 1. 主结构: 用户选中的 STRUCTURES label 对应 NARRATIVE_STRUCTURES key
    main_struct = NARRATIVE_STRUCTURES.get(struct_key, {})
    main_decision = NARRATIVE_DECISION.get(struct_key, {})

    if not main_struct:
        lines.append(f"⚠ 主结构 {struct_key!r} 未在 NARRATIVE_STRUCTURES 中找到, 降级到 classic_three_act")
        main_struct = NARRATIVE_STRUCTURES.get("classic_three_act", {})
        main_decision = NARRATIVE_DECISION.get("classic_three_act", {})

    lines.append("")
    lines.append(f"【主结构: {struct_label} → {struct_key}】")
    lines.append(f"中文名: {main_struct.get('cn', '')}")
    lines.append(f"源作者/学派: {THEORY_DISPLAY.get(struct_key, struct_key)}")
    lines.append(f"说明: {main_struct.get('description', '')}")
    if main_decision.get("trigger"):
        lines.append(f"触发场景: {main_decision['trigger']}")
    if main_decision.get("rationale"):
        lines.append(f"理论依据: {main_decision['rationale']}")
    if main_decision.get("failure_modes"):
        lines.append(f"失败模式: {' / '.join(main_decision['failure_modes'])}")
    if main_decision.get("measurement"):
        lines.append(f"达标测量: {main_decision['measurement']}")
    if main_decision.get("alternatives"):
        lines.append(f"备选: {' / '.join(main_decision['alternatives'])}")
    lines.append(f"情绪曲线: {main_struct.get('emotion_curve', '')}")

    # 2. 节拍表 (position 排序) — 跨导演 override
    override_beats = director_skel.get("beat_override", {}).get(struct_key, [])
    beats_to_use = override_beats if override_beats else main_struct.get("beat_map", [])

    lines.append("")
    lines.append(f"【节拍表: {len(beats_to_use)} 个拍点 (position% 升序)】")
    for b in sorted(beats_to_use, key=lambda x: x.get("position", 0)):
        pos = b.get("position", 0)
        beat_name = b.get("beat", "")
        func = b.get("function", "")
        lines.append(f"  • {pos*100:5.1f}%  {beat_name}: {func}")

    # 3. 5 套关键子理论 (Phase 35.9 跨切理论) — Save the Cat / 物件因果 / 情绪因果 / 伏笔 / 余韵
    lines.append("")
    lines.append("【跨切理论: 5 套子模块 (Crosscutting Theories)】")

    sub_modules = [
        ("Save the Cat 15 节拍", "save_the_cat", "救猫咪的精确分钟节拍, 用于校验中点位置"),
        ("伏笔-回收 (契诃夫之枪)", "buildup_payoff", "前半埋设细节, 后半回收形成震撼"),
        ("情绪过山车", "emotional_rollercoaster", "每 30s 情绪拐点, 防止脱敏"),
        ("沉沦-救赎", "descent_redemption", "角色从高处跌落再回升, 最有情感张力"),
        ("倒叙/物件因果", "in_medias_res", "物件贯穿, 倒叙揭示真相"),
    ]
    for name, key, desc in sub_modules:
        sub = NARRATIVE_STRUCTURES.get(key, {})
        if not sub:
            continue
        # 抽取关键拍点 (position < 0.5 用于上半, >= 0.5 用于下半)
        all_beats = sub.get("beat_map", [])
        up_beats = [b for b in all_beats if b.get("position", 0) < 0.5]
        down_beats = [b for b in all_beats if b.get("position", 0) >= 0.5]
        lines.append(f"  ◆ {name} ({key}): {desc}")
        lines.append(f"    上半 ({len(up_beats)} 拍): {' → '.join(b['beat'] for b in up_beats[:5])}")
        lines.append(f"    下半 ({len(down_beats)} 拍): {' → '.join(b['beat'] for b in down_beats[:5])}")

    # 4. 12 套理论全覆盖校验清单
    lines.append("")
    lines.append("【12 套理论全覆盖校验清单 (Phase 35.9)】")
    all_keys = list(NARRATIVE_STRUCTURES.keys())
    for i, k in enumerate(all_keys, 1):
        name = THEORY_DISPLAY.get(k, k)
        has_beats = len(NARRATIVE_STRUCTURES[k].get("beat_map", [])) if k in NARRATIVE_STRUCTURES else 0
        active = "● 激活" if k == struct_key else "○ 备用"
        lines.append(f"  {i:2d}. {name}: {active} ({has_beats} 节拍)")

    return "\n".join(lines)


# ============================================================
# Phase 35.9: INTENT_ADDON 段解析 — 从 inj 字符串提取结构化字段
# ============================================================
def _parse_intent_addon(inj_str):
    """
    用正则从 director_soul 原始 inj 字符串中提取 ===INTENT_ADDON=== 段,
    拆为 4 类意图 / 潜文本 / 观众情感 / 导演意图强度 / 灵魂状态.
    """
    if not inj_str or not isinstance(inj_str, str):
        return {
            "found": False,
            "scene_anchor": "",
            "primary_emotion": "",
            "intent_4": [],
            "subtext": "",
            "audience_feel": "",
            "director_intensity": 0.0,
            "soul_state_3": {},
            "anti_ai": "",
        }
    # 正则: 抓 ===INTENT_ADDON=== ... ===END_INTENT_ADDON===
    m = re.search(r"===INTENT_ADDON===\s*(.*?)\s*===END_INTENT_ADDON===",
                  inj_str, re.DOTALL)
    if not m:
        return {
            "found": False,
            "scene_anchor": "",
            "primary_emotion": "",
            "intent_4": [],
            "subtext": "",
            "audience_feel": "",
            "director_intensity": 0.0,
            "soul_state_3": {},
            "anti_ai": "",
        }
    body = m.group(1)
    result = {"found": True, "_raw": body}

    # 解析每行
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if "场景锚点" in line:
            result["scene_anchor"] = line.split(":", 1)[-1].strip()
        elif line.startswith("- 主导情感:"):
            result["primary_emotion"] = line.split(":", 1)[-1].strip()
        elif line.startswith("- 4 类意图:"):
            intents_str = line.split(":", 1)[-1].strip()
            # 拆 情感意图 / 主题意图 / 节奏意图 / 视觉意图
            result["intent_4"] = [
                p.strip() for p in intents_str.split("+") if p.strip()
            ]
        elif line.startswith("- 潜文本:"):
            result["subtext"] = line.split(":", 1)[-1].strip()
        elif line.startswith("- 观众应感到:"):
            result["audience_feel"] = line.split(":", 1)[-1].strip()
        elif line.startswith("- 导演意图强度:"):
            try:
                txt = line.split(":", 1)[-1].strip()
                # 抓 "故事强度 0.50" 之类
                m2 = re.search(r"([0-9]+\.?[0-9]*)", txt)
                result["director_intensity"] = float(m2.group(1)) if m2 else 0.0
            except Exception:
                result["director_intensity"] = 0.0
        elif line.startswith("- 灵魂状态:"):
            txt = line.split(":", 1)[-1].strip()
            # 抓 "灵感 0.85 | 怀疑 0.30 | 叛逆 0.70"
            soul_state = {}
            for part in txt.split("|"):
                part = part.strip()
                kv = part.split(" ", 1)
                if len(kv) == 2:
                    try:
                        soul_state[kv[0]] = float(kv[1])
                    except Exception:
                        pass
            result["soul_state_3"] = soul_state
        elif line.startswith("- 反 AI:"):
            result["anti_ai"] = line.split(":", 1)[-1].strip()

    # 兜底字段
    for k in ["scene_anchor", "primary_emotion", "subtext", "audience_feel", "anti_ai"]:
        if k not in result:
            result[k] = ""
    if "intent_4" not in result:
        result["intent_4"] = []
    if "director_intensity" not in result:
        result["director_intensity"] = 0.0
    if "soul_state_3" not in result:
        result["soul_state_3"] = {}
    return result


def _render_intent_addon_block(parsed, fused):
    """把 INTENT_ADDON 解析结果拼成结构化块"""
    if not parsed.get("found"):
        return "【INTENT_ADDON】解析失败: director_soul 输出中未找到 ===INTENT_ADDON=== 段"
    lines = []
    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append("【Phase 35.9: INTENT_ADDON 解析 (来自 director_soul)】")
    lines.append("════════════════════════════════════════")
    lines.append(f"  • 场景锚点: {parsed.get('scene_anchor', '')}")
    lines.append(f"  • 主导情感: {parsed.get('primary_emotion', '') or fused.get('name', 'Neutral')}")
    lines.append(f"  • 4 类意图: {' / '.join(parsed.get('intent_4', [])) or '(空)'}")
    lines.append(f"  • 潜文本: {parsed.get('subtext', '')}")
    lines.append(f"  • 观众应感到: {parsed.get('audience_feel', '')}")
    lines.append(f"  • 导演意图强度: {parsed.get('director_intensity', 0.0):.2f}")
    soul = parsed.get("soul_state_3", {})
    if soul:
        soul_str = " | ".join(f"{k} {v:.2f}" for k, v in soul.items())
        lines.append(f"  • 灵魂状态: {soul_str}")
    if parsed.get("anti_ai"):
        lines.append(f"  • 反 AI 指令: {parsed['anti_ai']}")
    return "\n".join(lines)


# ============================================================
# Phase 35.9: 5 维具体化 — 强制注入时代/地点/品牌/数字/物件
# ============================================================
def _concrete_5dims_block(era, region, scene_label, genre, director, struct_key):
    """
    根据 5 维 (时代/地点/场景/类型/导演) 强制生成至少 5 个具体物件 + 5 个数字 + 3 个品牌.
    每一项必须有时代特征 (1998 vs 2024 物件不同), 地域特征 (哈尔滨 vs 香港 vs 东京 物件不同).
    """
    lines = []
    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append("【Phase 35.9: 5 维具体化铁律 (Era × Region × Scene × Genre × Director)】")
    lines.append("════════════════════════════════════════")
    lines.append(f"  时代: {era or '未指定'}")
    lines.append(f"  地点: {region or '未指定'}")
    lines.append(f"  场景标签: {scene_label or '未指定'}")
    lines.append(f"  题材类型: {genre or '未指定'}")
    lines.append(f"  导演: {director or '未指定'}")

    # 时代物件库 (按年代划分的真实物件)
    era_objects = {
        "1990": ["BP 机", "VCD 机", "大哥大", "磁带", "胶卷相机", "雪糕 5 毛", "公用电话", "飞鸽自行车"],
        "2000": ["DVD 机", "彩屏诺基亚", "QQ 聊天", "随身听", "千千静听", "5 毛辣条", "上岛咖啡"],
        "2010": ["iPhone 4", "微博", "微信红包", "美团外卖", "高铁", "余额宝"],
        "2020": ["iPhone 15", "抖音", "电动车", "剧本杀", "剧本杀", "核酸检测", "新冠后遗症"],
    }
    # 地域物件库
    region_objects = {
        "哈尔滨": ["红肠", "马迭尔冰棍", "索菲亚教堂", "松花江", "中央大街", "哈啤", "冰雪大世界"],
        "香港": ["菠萝包", "茶餐厅", "庙街", "叮叮车", "维港", "重庆大厦", "7-11 鱼蛋"],
        "东京": ["涩谷十字", "拉面店", "自动贩卖机", "新干线", "富士山", "711 饭团"],
        "上海": ["外滩", "南京路", "石库门", "小笼包", "永康路", "老克勒", "上海牌手表"],
    }

    # 选 era key
    era_key = "1990" if "199" in (era or "") else ("2000" if "200" in (era or "") else ("2010" if "201" in (era or "") else ("2020" if "202" in (era or "") else "1990")))
    era_objs = era_objects.get(era_key, era_objects["1990"])

    # 选 region key
    region_key = None
    for k in region_objects.keys():
        if k in (region or ""):
            region_key = k
            break
    region_key = region_key or "哈尔滨"
    region_objs = region_objects[region_key]

    # 5 物件 (时代 2 + 地域 2 + 场景 1)
    scene_objects = {
        "雨夜": ["伞", "雨鞋", "水洼"],
        "驾驶舱": ["仪表盘", "安全带", "后视镜"],
        "婚礼": ["戒指", "婚纱", "花球"],
        "葬礼": ["黑伞", "白菊", "遗像"],
        "审讯": ["台灯", "录音机", "笔录纸"],
    }
    scene_objs = scene_objects.get(scene_label, [])

    five_objects = []
    five_objects.extend(era_objs[:2])
    five_objects.extend(region_objs[:2])
    five_objects.extend(scene_objs[:1])
    # 导演物件 1 个
    if director in DIRECTOR_SKELETON:
        five_objects.append(DIRECTOR_SKELETON[director].get("signature_object", ""))
    five_objects = [o for o in five_objects if o][:5]

    # 5 数字
    five_numbers = [
        f"片长 {era_key} 年代 120 分钟",
        f"3-5 句话世界观",
        f"7 个灵魂维度 (灵感/怀疑/叛逆/...)",
        f"15 节拍 (Save the Cat 校验)",
        f"9-15 个节拍总数",
    ]
    # 3 品牌
    brands_by_era = {
        "1990": ["三洋电视机", "爱华随身听", "万宝路香烟"],
        "2000": ["诺基亚 3310", "索尼 Walkman", "李宁运动鞋"],
        "2010": ["iPhone 4S", "小米手机", "耐克 Air Max"],
        "2020": ["iPhone 15 Pro", "大疆无人机", "比亚迪海豹"],
    }
    three_brands = brands_by_era.get(era_key, brands_by_era["1990"])[:3]

    lines.append("")
    lines.append(f"  强制 5 物件 (时代×地域×场景×导演): {' / '.join(five_objects) if five_objects else '(空)'}")
    lines.append(f"  强制 5 数字: {' / '.join(five_numbers)}")
    lines.append(f"  强制 3 品牌: {' / '.join(three_brands)}")

    # 跨导演/类型/场景骨架
    director_skel = DIRECTOR_SKELETON.get(director, DIRECTOR_SKELETON["default"])
    genre_params = GENRE_PARAMS.get(genre, {})
    scene_skel = SCENE_SKELETON.get(scene_label, {})

    lines.append("")
    lines.append("  【跨导演拍点规则】")
    lines.append(f"    {director} 节奏: {director_skel.get('pacing_rule', '')}")
    lines.append(f"    标志性物件: {director_skel.get('signature_object', '')}")
    lines.append(f"    标志性对白: {director_skel.get('signature_line', '')}")

    lines.append("")
    lines.append("  【跨类型参数】")
    if genre_params:
        lines.append(f"    节拍密度: {genre_params.get('beat_density', '')}")
        lines.append(f"    反转位置: {genre_params.get('reversal_position', '')}")
        lines.append(f"    余韵秒数: {genre_params.get('aftertaste_seconds', 0.0)}s")
        must_inc = genre_params.get("must_include", [])
        if must_inc:
            lines.append(f"    必含: {' / '.join(must_inc)}")
    else:
        lines.append(f"    (未指定题材类型, 用默认中密度)")

    lines.append("")
    lines.append("  【跨场景骨架】")
    if scene_skel:
        lines.append(f"    开场: {scene_skel.get('open', '')}")
        lines.append(f"    中点: {scene_skel.get('midpoint', '')}")
        lines.append(f"    高潮: {scene_skel.get('climax', '')}")
        lines.append(f"    结局: {scene_skel.get('ending', '')}")
    else:
        lines.append(f"    (未指定场景标签, 用默认骨架)")

    return "\n".join(lines)


def _format_soul_block(inj, fused, soul_state, soul_dims, director, scene_context):
    """
    把灵魂注入结果拼成清晰的文本块, 拼到 anti_ai_text 之后.
    这一块包含 fused['name'] (如 'Loneliness 孤独' / 'Apprehension 恐惧' / 'Warm Regret 温暖遗憾'),
    不同情感真的会输出不同文本.
    """
    lines = []
    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append("【Phase 17.6 灵魂注入 (Director Soul)】")
    lines.append("════════════════════════════════════════")
    # 1. 情感核心 (含 fused['name'])
    lines.append("")
    lines.append("【1. 情感核心 (Emotion Core)】")
    lines.append(f"主导情感 (fused name): {fused.get('name', 'Neutral 中性')}")
    lines.append(f"融合模式: {fused.get('fusion_mode', 'F1_单情感主导')}")
    emos = fused.get("emotions", []) or []
    lines.append(f"融合来源: {' + '.join(emos) if emos else '(无)'}")
    lines.append(f"强度: {float(fused.get('intensity', 0.0)):.2f}")
    lines.append(f"极性: {fused.get('polarity', 'neutral')}")
    lines.append(f"唤醒度: {fused.get('arousal', 'medium')}")

    # 2. 情感表达
    lines.append("")
    lines.append("【2. 情感表达 (Emotion Manifestation)】")
    vs = str(fused.get("visual_signs", "") or "").strip()
    if vs:
        lines.append(f"- 视觉表现: {vs[:500]}")
    vos = str(fused.get("voice_signs", "") or "").strip()
    if vos:
        lines.append(f"- 声音表现: {vos[:300]}")
    fau = str(fused.get("facial_au", "") or "").strip()
    if fau:
        lines.append(f"- 面部肌肉: {fau[:300]}")
    im = str(fused.get("inner_monologue", "") or "").strip()
    if im:
        lines.append(f"- 内心独白: {im[:300]}")

    # 3. 艺术氛围
    lines.append("")
    lines.append("【3. 艺术氛围 (Atmosphere)】")
    cp = str(fused.get("color_palette", "") or "").strip()
    if cp:
        lines.append(f"- 色彩: {cp[:300]}")
    mt = str(fused.get("music_tempo", "") or "").strip()
    if mt:
        lines.append(f"- 音乐: {mt[:300]}")

    # 4. 灵魂状态
    lines.append("")
    lines.append("【4. 灵魂状态 (Soul State)】")
    lines.append(f"灵感指数: {soul_state.get('inspiration', 0.0):.2f}")
    lines.append(f"疲劳指数: {soul_state.get('fatigue', 0.0):.2f}")
    lines.append(f"怀疑指数: {soul_state.get('doubt', 0.0):.2f}")
    lines.append(f"叛逆指数: {soul_state.get('rebelliousness', 0.0):.2f}")
    lines.append(f"精神状态: {soul_state.get('mental_state', 'neutral')}")

    # 5. 灵魂维度 (10 维度)
    lines.append("")
    lines.append("【5. 灵魂维度 (Soul Dimensions)】")
    lines.append(f"创造力: {soul_dims.get('creativity', 0.0):.2f}")
    lines.append(f"想象力: {soul_dims.get('imagination', 0.0):.2f}")
    lines.append(f"艺术表达: {soul_dims.get('artistic_expression', 0.0):.2f}")
    lines.append(f"镜头技巧: {soul_dims.get('camera_skill', 0.0):.2f}")
    lines.append(f"氛围掌控: {soul_dims.get('atmosphere_control', 0.0):.2f}")
    lines.append(f"精神状态: {soul_dims.get('mental_state', 'neutral')}")
    lines.append(f"灵感时刻: {soul_dims.get('inspiration', 0.0):.2f}")
    lines.append(f"叛逆度: {soul_dims.get('rebelliousness', 0.0):.2f}")
    lines.append(f"自我怀疑: {soul_dims.get('self_doubt', 0.0):.2f}")
    lines.append(f"突破勇气: {soul_dims.get('breakthrough_courage', 0.0):.2f}")

    # 6. 导演视角
    lines.append("")
    lines.append("【6. 导演视角 (Director Lens)】")
    lines.append(f"导演: {director or '默认'}")
    if scene_context:
        lines.append(f"场景: {scene_context[:100]}")
    lines.append("注入模式: SOUL_INJECTION_V1 (Phase 17.6 wrapper)")
    lines.append("════════════════════════════════════════")

    # 7. 原始 injection 字符串 (来自 director_soul.build_soul_injection, 完整版)
    if inj and isinstance(inj, str) and "导演灵魂注入" in inj:
        lines.append("")
        lines.append("【附: director_soul 原始注入 (build_soul_injection)】")
        lines.append(inj)
        lines.append("════════════════════════════════════════")

    return "\n".join(lines)


# ============================================================
# 节点类 (Phase 17.6 灵魂接入 + Phase 35.9 12 套理论)
# ============================================================
class ScriptArchitecturePro:
    """
    故事架构节点 — 拆节点 1/3
    输出: 世界观 + 主题 + 角色 + 结构 + 节奏曲线 (+ Phase 17.6 灵魂注入 + Phase 35.9 12 套理论)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 题材/输入 ===
                "题材": ("STRING", {
                    "default": "一段关于父女的故事, 在 1998 年哈尔滨",
                    "multiline": True,
                }),
                "片长分钟": ("INT", {"default": 120, "min": 1, "max": 600, "step": 1}),
                "集数": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),

                # === 2. 主题与冲突 ===
                "主题_可多选": ("STRING", {
                    "default": "家庭与代际,记忆与时间,孤独与连接",
                    "multiline": False,
                }),
                "核心冲突": (CONFLICTS, {"default": "人与人"}),
                "哲学内核": ("STRING", {
                    "default": "失去的不可逆, 但记忆可以重建",
                    "multiline": True,
                }),

                # === 3. 风格与导演 ===
                "导演风格_63选1": ("STRING", {
                    "default": "王家卫",
                    "multiline": False,
                }),
                "时代背景": ("STRING", {
                    "default": "1990 年代",
                    "multiline": False,
                }),
                "地域文化": ("STRING", {
                    "default": "东北 / 香港 / 东京",
                    "multiline": False,
                }),

                # === 4. 结构 ===
                "叙事结构": (STRUCTURES, {"default": "经典三幕剧"}),
                "反转次数": ("INT", {"default": 1, "min": 0, "max": 5, "step": 1}),
                "多线并行": (["无", "双线", "三线", "四线+"], {"default": "无"}),
                "隐喻层数": ("INT", {"default": 1, "min": 0, "max": 4, "step": 1}),

                # === 5. 角色与受众 ===
                "主角数量": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "反派数量": ("INT", {"default": 1, "min": 0, "max": 5, "step": 1}),
                "目标受众": (["大众", "成人/艺术", "智性", "女性向", "男性向", "青少年"], {"default": "大众"}),

                # === 6. 节奏 ===
                "节奏密度": (["疏 (留白多)", "中", "密 (高信息)"], {"default": "中"}),
                "留白比例": (["10%以下", "30%", "50%", "70%", "90%以上"], {"default": "30%"}),
                "余韵强度": (["淡", "中", "重 (反转后留白)"], {"default": "中"}),

                # === 7. 灵魂注入 (Phase 17.6) — 真实驱动, 与 editing_pro.py 命名一致 ===
                "灵魂_主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "灵魂_次要情感": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),

                # === 8. Phase 35.9 新增: 题材类型 + 场景标签 ===
                "题材类型": (GENRE_TYPES, {"default": "剧情"}),
                "场景标签": (SCENE_TAGS, {"default": "雨夜"}),
            },
            "optional": {
                # === 9. 额外反 AI 配置 ===
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                "多轮迭代": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("story_architecture", "anti_ai_rules", "iteration_chain")
    FUNCTION = "build_architecture"
    CATEGORY = "PromptLibrary/剧本输出"

    # ------------------------------------------------------------------
    # build_architecture — 真实灵魂驱动 (Phase 17.6) + 12 套理论 (Phase 35.9)
    # ------------------------------------------------------------------
    def build_architecture(self, **kwargs):
        """构建故事架构 (含灵魂注入 + 12 套理论真调用 + 5 维具体化 + INTENT_ADDON 解析)"""
        # 0. 灵魂输入 (Phase 17.6) — 必须在最前面, 反 AI 块也要看灵魂色彩
        director = kwargs.get("导演风格_63选1", "王家卫")
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_secondary = kwargs.get("灵魂_次要情感", "none")
        soul_scene_weight = kwargs.get("灵魂_场景权重", 0.5)
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")

        # Phase 35.9: 题材类型 + 场景标签
        genre_type = kwargs.get("题材类型", "剧情")
        scene_label = kwargs.get("场景标签", "雨夜")

        # 真实调用 director_soul.soul_inject_simple (统一 wrapper)
        inj, fused, soul_state, soul_dims = _build_soul_injection(
            soul_primary=soul_primary,
            soul_secondary=soul_secondary,
            soul_scene_weight=soul_scene_weight,
            soul_fusion_mode=soul_fusion_mode,
            director=director,
            scene_context=kwargs.get("题材", "") or kwargs.get("哲学内核", ""),
            story_intensity=soul_scene_weight,  # 故事强度 = 场景权重
            scene_progress=0.5,                 # 故事架构节点: 进度 0.5
        )

        # 注入反 AI 规则
        if _HAS_ANTI_AI:
            user_prompt = f"""【任务: 为以下故事生成完整架构】

题材: {kwargs.get('题材', '')}
片长: {kwargs.get('片长分钟', '')} 分钟
集数: {kwargs.get('集数', '')}
主题: {kwargs.get('主题_可多选', '')}
核心冲突: {kwargs.get('核心冲突', '')}
哲学内核: {kwargs.get('哲学内核', '')}
导演风格: {director}
时代背景: {kwargs.get('时代背景', '')}
地域文化: {kwargs.get('地域文化', '')}
题材类型: {genre_type}
场景标签: {scene_label}
叙事结构: {kwargs.get('叙事结构', '')}
反转次数: {kwargs.get('反转次数', '')}
多线并行: {kwargs.get('多线并行', '')}
隐喻层数: {kwargs.get('隐喻层数', '')}
主角数量: {kwargs.get('主角数量', '')}
反派数量: {kwargs.get('反派数量', '')}
目标受众: {kwargs.get('目标受众', '')}
节奏密度: {kwargs.get('节奏密度', '')}
留白比例: {kwargs.get('留白比例', '')}
余韵强度: {kwargs.get('余韵强度', '')}

【输出格式 JSON】
{{
  "worldview": "世界观的 3-5 句话具象描述",
  "theme": "主题的具象呈现(不用'关于'XXX 直接说XXX)",
  "characters": [
    {{"name": "姓名", "age": 年龄, "body": "身体特征", "habit": "身体习惯", "object": "标志性物件", "arc": "人物弧光"}}
  ],
  "structure": "分幕/分集结构, 每幕用一句话+一个关键场景",
  "pacing_curve": [0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0],
  "metaphysics": "哲学内核的具象呈现",
  "direct_signature": "{director}的标志性手法怎么用在本题材"
}}
"""
            # 注入反 AI 规则
            if kwargs.get("启用反AI规则", True):
                anti_ai_text = inject_anti_ai_rules(user_prompt, director if director in DIRECTOR_ANTI_AI_PROMPTS else "")
            else:
                anti_ai_text = user_prompt

            # 注入真实导演微调
            if director in ALL_DIRECTORS:
                micro_tune = build_micro_finetune_prompt(director, "故事架构")
                anti_ai_text = f"{anti_ai_text}\n\n{micro_tune}"

            # 注入额外禁用词
            extra_ban = kwargs.get("额外禁用词", "")
            if extra_ban:
                anti_ai_text += f"\n\n【额外禁用词(必须严格遵守)】\n{extra_ban}"

            # ============================================================
            # Phase 35.9: 12 套理论真调用 — 真实展开节拍表
            # ============================================================
            struct_label = kwargs.get("叙事结构", "经典三幕剧")
            struct_key = LABEL_TO_STRUCT_KEY.get(struct_label, "classic_three_act")
            director_skel = DIRECTOR_SKELETON.get(director, DIRECTOR_SKELETON["default"])
            theories_block = _render_12_theories_block(struct_label, struct_key, director_skel)
            anti_ai_text = f"{anti_ai_text}\n\n{theories_block}"

            # ============================================================
            # Phase 35.9: 5 维具体化 — 时代×地域×场景×类型×导演
            # ============================================================
            concrete_block = _concrete_5dims_block(
                era=kwargs.get("时代背景", ""),
                region=kwargs.get("地域文化", ""),
                scene_label=scene_label,
                genre=genre_type,
                director=director,
                struct_key=struct_key,
            )
            anti_ai_text = f"{anti_ai_text}\n\n{concrete_block}"

            # ============================================================
            # Phase 17.6 灵魂块: 拼到 anti_ai_text 后面
            # ============================================================
            soul_block = _format_soul_block(
                inj, fused, soul_state, soul_dims,
                director=director,
                scene_context=kwargs.get("题材", "") or "",
            )
            anti_ai_text = f"{anti_ai_text}\n\n{soul_block}"

            # ============================================================
            # Phase 35.9: INTENT_ADDON 解析 — 从 inj 提取结构化字段
            # ============================================================
            intent_parsed = _parse_intent_addon(inj)
            intent_block = _render_intent_addon_block(intent_parsed, fused)
            anti_ai_text = f"{anti_ai_text}\n\n{intent_block}"

            # 多轮迭代链
            if kwargs.get("多轮迭代", True):
                iter_chain = [
                    ITERATION_TEMPLATES["round_1_draft"].format(
                        theme=kwargs.get("主题_可多选", ""),
                        characters=f"{kwargs.get('主角数量', 1)} 主角 + {kwargs.get('反派数量', 1)} 反派",
                        structure=kwargs.get("叙事结构", ""),
                        pacing=kwargs.get("节奏密度", ""),
                    ),
                    ITERATION_TEMPLATES["round_2_anti_ai"],
                    ITERATION_TEMPLATES["round_3_humanize"],
                    ITERATION_TEMPLATES["round_4_director_polish"].format(
                        director=director,
                        camera_style="按" + director + "的镜头习惯",
                        pacing_style=kwargs.get("节奏密度", "中"),
                        theme_focus=kwargs.get("主题_可多选", ""),
                        visual_signature="按" + director + "的视觉签名",
                    ),
                ]
                iter_text = "\n\n=========\n\n".join(iter_chain)
            else:
                iter_text = "未启用多轮迭代"

            return (
                anti_ai_text,  # story_architecture(反 AI + 真实导演微调 + Phase 17.6 灵魂 + Phase 35.9 12 套理论 + 5 维 + INTENT_ADDON 解析)
                json.dumps({k: v for k, v in ANTI_AI_PHRASES.items() if k}, ensure_ascii=False)[:1000] if _HAS_ANTI_AI else "未加载",
                iter_text,
            )
        else:
            # 没有反 AI 词表时, 简单 prompt + 灵魂注入 (灵魂注入是独立的, 不依赖 anti_ai)
            soul_block = _format_soul_block(
                inj, fused, soul_state, soul_dims,
                director=director,
                scene_context=kwargs.get("题材", "") or "",
            )
            return (
                f"题材: {kwargs.get('题材','')}\n输出: 故事架构 JSON\n\n{soul_block}",
                "反 AI 词表未加载: " + _ANTI_AI_ERROR if not _HAS_ANTI_AI else "",
                "未启用多轮迭代",
            )


# 节点注册映射
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ScriptArchitecturePro": ScriptArchitecturePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ScriptArchitecturePro": "📖 剧本架构 (1/3)",
# }
