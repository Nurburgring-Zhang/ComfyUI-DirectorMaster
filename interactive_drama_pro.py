# -*- coding: utf-8 -*-
"""
InteractiveDramaPro - 互动剧专家节点
====================================================
互动剧 (环节 41) — 分支叙事架构 + 选择设计 + 收束机制 + 重玩价值

核心能力:
1. 分支叙事架构 (线性/双线/树状/网状) — 场景图 + 状态变量
2. 选择设计原则 — 无正确答案 + 后果延迟 + 假选择检测
3. 收束机制 — 硬收束/软收束/延迟收束/状态收束
4. 重玩价值 — 隐藏路径 + 元叙事 + 角色多面
5. 互动镜头语言 — 选择时刻/后果揭示/分支过渡
6. 技术规格 — 节点ID/边条件/状态变量追踪/存档点
"""

import os
import sys
import json
import hashlib

# === 导演数据中枢 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile, SCENE_DATABASE_100, QUOTES_30,
        get_director, get_scene,
    )
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False

# === 叙事结构知识库 ===
try:
    from knowledge_base.narrative_structures import (
        NARRATIVE_STRUCTURES, SHORT_FORM_STRUCTURES,
        NARRATIVE_DECISION, get_structure_with_decision,
    )
    _HAS_NARRATIVE = True
except Exception:
    _HAS_NARRATIVE = False

# === 反 AI 词表 ===
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

# === 灵魂注入 ===
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# 互动剧专业常量
# ============================================================

GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# --- 分支复杂度架构定义 ---
BRANCHING_ARCHITECTURES = {
    "线性 (Linear)": {
        "description": "单路径, 对话选择改变台词/情绪但不改变剧情走向",
        "max_nodes": 12,
        "max_edges": 15,
        "convergence": "implicit",
        "state_vars": 2,
        "example": "Firewatch — 对话选择影响关系值但主线不变",
        "camera_note": "固定镜头语言, 选择时仅改变对话而非场景",
        "complexity_score": 1,
        "scene_graph_pattern": "A->B->C->D (minor dialogue variants at each node)",
    },
    "双线 (Binary)": {
        "description": "关键时刻二选一, 两条路径在幕间收束",
        "max_nodes": 20,
        "max_edges": 28,
        "convergence": "act_boundary",
        "state_vars": 5,
        "example": "黑镜: 潘达斯奈基 — 二叉分支, 死胡同回退",
        "camera_note": "选择时刻: 分屏/画中画暗示两条路; 收束: match cut",
        "complexity_score": 3,
        "scene_graph_pattern": "A->{B1,B2}->C->{D1,D2}->E (converge at act boundaries)",
    },
    "树状 (Tree)": {
        "description": "每次选择产生真正不同的场景, 指数增长由收束点控制",
        "max_nodes": 40,
        "max_edges": 55,
        "convergence": "strategic_points",
        "state_vars": 8,
        "example": "底特律: 变人 — 3 主角各有树状分支, 共享世界状态",
        "camera_note": "不同分支有不同视觉风格 (色温/构图), 收束时风格统一",
        "complexity_score": 5,
        "scene_graph_pattern": "A->{B1,B2,B3}; B1->{C1,C2}; B2->{C3,C4}; converge at D",
    },
    "网状 (Network)": {
        "description": "任意节点可通向多个其他节点, 复杂状态追踪",
        "max_nodes": 60,
        "max_edges": 100,
        "convergence": "state_based",
        "state_vars": 15,
        "example": "隐形守护者 — 多线交叉, 信任/阵营/好感度多变量",
        "camera_note": "POV 随路径切换; 同一场景不同进入方式有不同机位",
        "complexity_score": 8,
        "scene_graph_pattern": "Graph with cross-links: any node -> {multiple targets} based on state",
    },
    "auto": {
        "description": "根据分支数和场景复杂度自动选择",
        "max_nodes": 30,
        "max_edges": 45,
        "convergence": "adaptive",
        "state_vars": 6,
        "example": "自动选择最适合的架构",
        "camera_note": "自适应镜头语言",
        "complexity_score": 4,
        "scene_graph_pattern": "auto",
    },
}

# --- 选择类型设计框架 ---
CHOICE_TYPE_FRAMEWORKS = {
    "道德 (Moral)": {
        "design_principle": "没有正确答案, 每个选项都有代价",
        "dilemma_templates": [
            "电车难题变体: 牺牲少数救多数 vs 不作为",
            "忠诚冲突: 对朋友的忠诚 vs 对正义的忠诚",
            "两害相权: 说出真相伤害对方 vs 隐瞒真相保护对方",
            "短期善意长期伤害: 给钱 vs 给机会",
            "集体 vs 个人: 家族荣誉 vs 个人自由",
        ],
        "consequence_design": "道德选择的后果在 2-3 场景后显现 (consequence delay)",
        "emotion_weight": "guilt, relief, moral_weight",
        "camera_language": "选择时: 慢推至角色眼部特写, 浅景深, 时间膨胀感",
    },
    "策略 (Strategic)": {
        "design_principle": "信息不完整, 需要玩家判断风险",
        "dilemma_templates": [
            "资源分配: 救人 vs 保存弹药",
            "信息博弈: 信任线人 vs 独立调查",
            "时间压力: 快速行动(可能失误) vs 等待(可能错过)",
            "同盟选择: 与A结盟(短期强) vs 与B结盟(长期稳)",
            "暴露风险: 冒险获取情报 vs 安全保守行动",
        ],
        "consequence_design": "策略选择影响后续可用资源/路径, 立即可见部分后果",
        "emotion_weight": "tension, calculation, surprise",
        "camera_language": "选择时: 俯拍战术视角, 信息面板叠加, 倒计时视觉",
    },
    "情感 (Emotional)": {
        "design_principle": "心 vs 脑, 情感直觉 vs 理性判断",
        "dilemma_templates": [
            "原谅 vs 正义: 对方真心悔过但伤害已造成",
            "爱 vs 责任: 留下陪伴 vs 离开追梦",
            "放手 vs 执念: 接受现实 vs 继续等待",
            "自我 vs 他人: 牺牲自己的需求满足他人",
            "记忆 vs 前行: 保留痛苦记忆 vs 选择遗忘",
        ],
        "consequence_design": "情感选择改变角色关系值, 影响后续对话和信任度",
        "emotion_weight": "tenderness, heartbreak, warmth, longing",
        "camera_language": "选择时: 双人中景, 两人之间的空间暗示距离, rack focus",
    },
    "信息 (Information)": {
        "design_principle": "选择获取哪部分信息, 放弃另一部分",
        "dilemma_templates": [
            "视角选择: 跟踪A获取A的秘密 vs 跟踪B获取B的秘密",
            "开门选择: 左门(真相) vs 右门(力量)",
            "对话分支: 追问细节(获取线索) vs 安慰对方(获取信任)",
            "翻看 vs 放下: 偷看日记(获取信息) vs 尊重隐私(保持信任)",
            "时间分配: 在有限时间内选择调查哪条线索",
        ],
        "consequence_design": "信息选择决定玩家在后续场景中的认知水平",
        "emotion_weight": "curiosity, regret, discovery",
        "camera_language": "选择时: POV镜头, 选项物件特写, 轻微景深变化引导注意",
    },
    "混合 (Mixed)": {
        "design_principle": "多维度交叉 (道德+策略+情感), 最高复杂度",
        "dilemma_templates": [
            "综合: 救人(道德) 但暴露位置(策略) 且伤害同伴感情(情感)",
            "综合: 揭露真相(信息) 导致对方崩溃(情感) 但阻止更大伤害(道德)",
        ],
        "consequence_design": "多维后果同时生效, 不同维度的影响可能互相矛盾",
        "emotion_weight": "complexity, weight, ambivalence",
        "camera_language": "选择时: 多层构图, 前景/中景/背景分别暗示不同维度的代价",
    },
    "auto": {
        "design_principle": "根据场景自动选择最合适的选择类型",
        "dilemma_templates": ["自动匹配"],
        "consequence_design": "自适应",
        "emotion_weight": "auto",
        "camera_language": "自适应",
    },
}

# --- 收束机制 ---
CONVERGENCE_MECHANISMS = {
    "hard": {
        "name": "硬收束",
        "description": "所有路径在特定剧情点合并, 无论之前选择",
        "technique": "大事件强制所有角色到同一地点 (爆炸/地震/集合令)",
        "risk": "玩家感到选择无意义 (用状态变量和对话差异缓解)",
        "mitigation": "收束点处不同路径有不同对话/表情/关系状态, 同一场景但体验不同",
    },
    "soft": {
        "name": "软收束",
        "description": "不同路径到达相似情境, 但角色状态/关系不同",
        "technique": "目的地相同但旅程不同 (不同理由到达同一地点)",
        "risk": "设计难度高, 需要维护角色状态差异",
        "mitigation": "用 trust_level / knowledge_level / relationship_score 差异化",
    },
    "delayed": {
        "name": "延迟收束",
        "description": "路径平行运行多场景后再合并",
        "technique": "A 线和 B 线各跑 3-5 场景, 通过共享事件收束",
        "risk": "内容量翻倍, 制作成本高",
        "mitigation": "共享部分场景资产, 只改变对话和角色行为",
    },
    "state_based": {
        "name": "状态收束",
        "description": "角色变量 (信任/知识/关系) 决定收束到哪个节点",
        "technique": "if trust > 7: converge_at('信任结局'); else: converge_at('背叛结局')",
        "risk": "状态阈值设计不当导致路径不可达",
        "mitigation": "确保每个状态区间都有足够的玩家覆盖 (正态分布设计)",
    },
}

# --- 重玩价值设计 ---
REPLAY_VALUE_DESIGN = {
    "character_facets": "不同路径揭示角色的不同面 (勇气/恐惧/温柔/残忍), 不是善恶二元",
    "hidden_paths": "特定选择组合解锁隐藏路径 (例: 连续3次选择沉默 -> 解锁冥想结局)",
    "completionist_rewards": "体验所有分支后解锁元叙事 (角色知道自己在多重时间线中)",
    "meta_narrative": "多周目: 第一次纯粹体验, 第二次发现隐藏线索, 第三次理解全貌",
    "choice_pattern_commentary": "系统记录玩家的选择模式并在最终做出评论 (你总是选择保护而非真相)",
}

# --- 互动镜头语言 ---
INTERACTIVE_CAMERA_LANGUAGE = {
    "choice_moment": {
        "framing": "Slow push-in to character face, shallow DOF (f/1.4), background dissolves",
        "timing": "Time dilation: 实际2秒拉长到感知6秒, 声音低通滤波",
        "lighting": "微妙聚光: 关键光亮度提升10%, 环境光降低20%",
        "sound": "环境音渐弱, 心跳声渐入, 选项音效 (微弱钟声/呼吸)",
    },
    "consequence_reveal": {
        "framing": "Wide shot revealing impact scope, dramatic lighting shift",
        "timing": "正常速度恢复, 0.5秒静止后动作继续",
        "lighting": "色温突变: 暖->冷 (负面后果) 或 冷->暖 (正面后果)",
        "sound": "沉默1.5秒 -> 后果音效 (门关/玻璃碎/雨声/鸟鸣)",
    },
    "branch_transition": {
        "framing": "Match cut: 选择动作 -> 结果场景的相似构图",
        "timing": "0.3秒交叉溶解, 或硬切 (根据情绪决定)",
        "lighting": "分支间光线连续性: 前一场景最后的光 = 下一场景第一帧的光",
        "sound": "声音桥: 前场景的环境音延续到下一场景前2秒",
    },
    "timer_pressure": {
        "framing": "Handheld shake increases, frame rate 感知加速 (更短的 shot duration)",
        "timing": "倒计时: 10秒选择窗口, 5秒时画面抖动加剧, 3秒时边缘暗角收缩",
        "lighting": "闪烁: 灯光不稳定, 暗示时间压力",
        "sound": "心跳加速 + 低频嗡鸣渐强 + 选项提示音加快",
    },
}

# --- 假选择检测规则 ---
FALSE_CHOICE_DETECTION = [
    {"pattern": "两个选项导致完全相同的下一场景", "severity": "CRITICAL", "fix": "至少改变一行对话或一个角色反应"},
    {"pattern": "选项文本暗示不同方向但结果相同", "severity": "HIGH", "fix": "要么分支要么重写选项文本为变体而非对立"},
    {"pattern": "选择后无任何状态变量改变", "severity": "MEDIUM", "fix": "至少修改一个关系值或知识标记"},
    {"pattern": "玩家无法感知到后果 (后果太远或太隐蔽)", "severity": "LOW", "fix": "在1-2场景内给出至少一个微小的后果提示"},
]


def _auto_select_branching(branch_count, scene_desc):
    """根据分支数和场景描述自动选择分支架构"""
    if branch_count <= 2:
        return "双线 (Binary)"
    elif branch_count == 3:
        return "树状 (Tree)"
    elif branch_count >= 4:
        return "网状 (Network)"
    return "双线 (Binary)"


def _auto_select_choice_type(scene_desc, mood, subtext):
    """根据场景/情绪/潜文本自动选择选择类型"""
    moral_keywords = ["对错", "道德", "牺牲", "正义", "善恶", "杀", "救", "罪"]
    strategic_keywords = ["资源", "战斗", "逃跑", "计划", "策略", "路线", "选择"]
    emotional_keywords = ["爱", "恨", "原谅", "离别", "家", "亲情", "友情", "关系"]
    info_keywords = ["秘密", "真相", "线索", "调查", "发现", "日记", "信"]

    combined = scene_desc + mood + subtext
    scores = {
        "道德 (Moral)": sum(1 for k in moral_keywords if k in combined),
        "策略 (Strategic)": sum(1 for k in strategic_keywords if k in combined),
        "情感 (Emotional)": sum(1 for k in emotional_keywords if k in combined),
        "信息 (Information)": sum(1 for k in info_keywords if k in combined),
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "情感 (Emotional)"
    return best


def _generate_node_id(scene_desc, branch_idx):
    """生成场景图节点ID (基于内容的稳定hash)"""
    raw = scene_desc[:30] + str(branch_idx)
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]
    return "N_" + h


def _build_scene_graph(branch_arch, branch_count, scene_desc):
    """生成场景图描述 (节点/边/状态变量)"""
    arch = BRANCHING_ARCHITECTURES.get(branch_arch, BRANCHING_ARCHITECTURES["auto"])

    root_id = _generate_node_id(scene_desc, 0)
    nodes = [{"id": root_id, "type": "entry", "scene": scene_desc[:40] + "..."}]
    edges = []
    state_vars = []

    for i in range(1, branch_count + 1):
        nid = _generate_node_id(scene_desc, i)
        nodes.append({"id": nid, "type": "branch_" + str(i), "scene": "Branch " + str(i)})
        edges.append({"from": root_id, "to": nid, "condition": "choice_" + str(i)})

    conv_id = _generate_node_id(scene_desc + "_conv", 99)
    nodes.append({"id": conv_id, "type": "convergence", "scene": "Convergence point"})
    for i in range(1, branch_count + 1):
        bid = _generate_node_id(scene_desc, i)
        edges.append({"from": bid, "to": conv_id, "condition": "auto_converge"})

    end_id = _generate_node_id(scene_desc + "_end", 100)
    nodes.append({"id": end_id, "type": "ending", "scene": "Ending"})
    edges.append({"from": conv_id, "to": end_id, "condition": "proceed"})

    state_vars = [
        "trust_level (INT 0-10): 角色间信任值, 影响对话和可用路径",
        "knowledge_flags (BITMASK): 已获取的信息 (bit0=秘密A, bit1=线索B, ...)",
        "relationship_score (INT -5 to 5): 角色关系 (-5=敌对, 0=中立, 5=亲密)",
        "moral_alignment (FLOAT -1.0 to 1.0): 道德倾向 (负=功利, 正=利他)",
    ]
    if arch["state_vars"] > 4:
        state_vars.extend([
            "faction_reputation (DICT): 各阵营好感度",
            "resource_count (INT): 可用资源/生命/弹药",
        ])

    return {
        "nodes": nodes,
        "edges": edges,
        "state_vars": state_vars[:arch["state_vars"]],
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "pattern": arch["scene_graph_pattern"],
    }


def _detect_false_choices(choices_text):
    """扫描选择设计中的假选择反模式"""
    warnings = []
    for rule in FALSE_CHOICE_DETECTION:
        warnings.append("[CHECK " + rule["severity"] + "] " + rule["pattern"] + " -> FIX: " + rule["fix"])
    return warnings


class InteractiveDramaPro:
    """
    互动剧专家节点 — 分支叙事 + 选择设计 + 收束机制 + 重玩价值
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "互动剧"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                # === 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                # === 互动剧专属字段 ===
                "分支复杂度": (["线性 (Linear)", "双线 (Binary)", "树状 (Tree)", "网状 (Network)", "auto"],
                             {"default": "auto"}),
                "选择类型": (["道德 (Moral)", "策略 (Strategic)", "情感 (Emotional)",
                            "信息 (Information)", "混合 (Mixed)", "auto"],
                           {"default": "auto"}),
                "分支数": ("INT", {"default": 3, "min": 2, "max": 6, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("interactivedramapro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_interactive"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_interactive(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # --- 提取输入 ---
        def _str(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "互动剧")
        scene = _str(kwargs.get("场景描述"), "")
        director = _str(kwargs.get("导演风格"), "是枝裕和")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        branch_complexity = _str(kwargs.get("分支复杂度"), "auto")
        choice_type = _str(kwargs.get("选择类型"), "auto")
        branch_count = int(kwargs.get("分支数", 3))

        # --- auto 路由 ---
        if branch_complexity == "auto":
            branch_complexity = _auto_select_branching(branch_count, scene)
        if choice_type == "auto":
            choice_type = _auto_select_choice_type(scene, mood, subtext)

        # --- 导演数据 ---
        director_profile = {}
        director_scene = {}
        if _HAS_DIRECTOR_DATA:
            director_profile = get_director(director)
            director_scene = get_scene(director)

        director_motion_map = {
            "塔可夫斯基": "Static Shot 长时间不动 + Push In 慢推",
            "王家卫": "Push In 慢推 + 跳切 + Step Printing",
            "诺兰": "Tracking Shot 跟拍 + 时间折叠剪辑",
            "是枝裕和": "Static Shot 静观 + Push In 缓推",
            "侯孝贤": "Static Shot 远景长镜 + 留白",
            "李沧东": "Push In 微推 + 慢节奏",
            "蔡明亮": "Static Shot 超长 + 完全不动",
            "毕赣": "Arc Shot 环绕 + 长镜头",
            "周星驰": "Quick Cut 快速切换 + 戏谑节奏",
            "Papi酱": "Static Shot 口语化",
            "Vince Gilligan": "Push In 暗调慢推",
            "大衛·芬奇": "Tracking Shot 跟拍 + 暗调",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + Push In 缓推")

        # --- 分支架构 ---
        arch_data = BRANCHING_ARCHITECTURES.get(branch_complexity, BRANCHING_ARCHITECTURES["auto"])
        choice_data = CHOICE_TYPE_FRAMEWORKS.get(choice_type, CHOICE_TYPE_FRAMEWORKS["auto"])

        # --- 场景图生成 ---
        scene_graph = _build_scene_graph(branch_complexity, branch_count, scene)

        # --- 选择设计 ---
        dilemma_list = choice_data["dilemma_templates"]
        consequence_rule = choice_data["consequence_design"]

        # --- 收束策略 ---
        convergence_key = arch_data.get("convergence", "soft")
        conv_mechanism = CONVERGENCE_MECHANISMS.get(convergence_key, CONVERGENCE_MECHANISMS.get("soft", {}))
        if not conv_mechanism:
            conv_mechanism = CONVERGENCE_MECHANISMS["soft"]

        # --- 叙事结构参考 ---
        narrative_ref = ""
        if _HAS_NARRATIVE:
            for struct_key in ["parallel_convergence", "nonlinear", "buildup_payoff"]:
                struct = get_structure_with_decision(struct_key)
                if struct:
                    narrative_ref += "  [" + struct.get("cn", struct_key) + "] trigger: " + str(struct.get("trigger", "")) + "\n"

        # --- H3 三大字段生成 ---
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, immersive branching",
            "互动剧": "Cinematic, live-action, immersive branching narrative",
        }
        style = style_choices.get(genre, "Cinematic, live-action, immersive")

        choice_cam = INTERACTIVE_CAMERA_LANGUAGE["choice_moment"]
        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        shot_1 = ("a medium-wide shot establishes the interactive scene - " + scene +
                  ". " + director_motion_pref +
                  ". The director intends: " + intent_feel +
                  ". The " + first_prop + " sits prominently in frame, " +
                  "a future choice anchor that the viewer does not yet know will demand a decision.")

        shots = [
            ("[Shot 2] At 00:04.000, " + format_shot_motion("Push In", "small", "slow") +
             " toward the main character's face. " + choice_cam["framing"] +
             ". The viewer senses the weight of an approaching decision. " +
             "Subtext: " + subtext + "."),

            ("[Shot 3] At 00:09.000, the camera reveals " + first_prop +
             " in close-up. The object's meaning will change depending on the viewer's choice. " +
             "Sound: " + choice_cam["sound"] + ". " +
             "The mood shifts toward: " + mood + "."),

            ("[Shot 4] At 00:14.000, CHOICE MOMENT. " + choice_cam["framing"] + ". " +
             choice_cam["timing"] + ". " +
             "The frame splits conceptually into " + str(branch_count) + " paths. " +
             "Choice type: " + choice_type + ". " +
             "Dilemma: " + dilemma_list[0] if dilemma_list else "auto" + "."),

            ("[Shot 5] At 00:20.000, CONSEQUENCE REVEAL (Branch A). " +
             INTERACTIVE_CAMERA_LANGUAGE["consequence_reveal"]["framing"] + ". " +
             INTERACTIVE_CAMERA_LANGUAGE["consequence_reveal"]["lighting"] + ". " +
             "Director intent: " + intent_feel + ". " +
             "The " + last_prop + " reacts to the choice."),

            ("[Shot 6] At 00:27.000, CONVERGENCE BEAT. " +
             INTERACTIVE_CAMERA_LANGUAGE["branch_transition"]["framing"] + ". " +
             "All paths begin to approach the convergence point. " +
             "The " + last_prop + " catches the light. End of interactive segment."),
        ]

        soundscape = ("Interactive audio layer: base ambient (" + scene[:30] +
                      ") + choice tension (heartbeat crescendo at 00:14) + " +
                      "consequence stinger (tonal shift at 00:20) + " +
                      "convergence resolve (ambient return at 00:27). " +
                      "Props audio: " + props + " with subtle interaction sounds.")

        music = ("Sparse piano establishes theme. At choice moment: " +
                 "music pauses, replaced by processed breathing and heartbeat. " +
                 "Post-choice: branch-specific music color (warm strings for empathy, " +
                 "cold synth for strategic, minor key for moral weight). " +
                 "Convergence: themes reunite in a resolution chord.")

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # --- 灵魂注入 ---
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
                    "【灵魂核心 - 互动剧驱动】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "选择时刻情感权重: " + str(choice_data.get("emotion_weight", "")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        # ================================================================
        # 主输出: 互动剧专业 prompt
        # ================================================================
        sep = "=" * 55

        main_output = sep + "\n"
        main_output += soul_header
        main_output += "【InteractiveDramaPro】互动剧专家节点\n"
        main_output += sep + "\n\n"

        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + " - 镜头运动倾向: " + director_motion_pref + "\n"
        if _HAS_DIRECTOR_DATA and director_profile:
            main_output += "【导演档案】 情绪=" + str(director_profile.get("情绪", "")) + ", 色彩=" + str(director_profile.get("色彩", "")) + "\n"
        main_output += "\n"

        # 分支架构
        main_output += sep + "\n"
        main_output += "【分支叙事架构】 " + branch_complexity + "\n"
        main_output += sep + "\n\n"
        main_output += "  架构说明: " + arch_data["description"] + "\n"
        main_output += "  参考: " + arch_data["example"] + "\n"
        main_output += "  最大节点数: " + str(arch_data["max_nodes"]) + " | 最大边数: " + str(arch_data["max_edges"]) + "\n"
        main_output += "  状态变量数: " + str(arch_data["state_vars"]) + "\n"
        main_output += "  镜头备注: " + arch_data["camera_note"] + "\n"
        main_output += "  图模式: " + arch_data["scene_graph_pattern"] + "\n\n"

        # 场景图
        main_output += sep + "\n"
        main_output += "【场景图 (Scene Graph)】\n"
        main_output += sep + "\n\n"
        main_output += "  节点总数: " + str(scene_graph["total_nodes"]) + " | 边总数: " + str(scene_graph["total_edges"]) + "\n"
        for node in scene_graph["nodes"]:
            main_output += "  [" + node["id"] + "] type=" + node["type"] + " scene=" + node["scene"] + "\n"
        main_output += "\n  边:\n"
        for edge in scene_graph["edges"]:
            main_output += "    " + edge["from"] + " -> " + edge["to"] + " (when: " + edge["condition"] + ")\n"
        main_output += "\n  状态变量追踪:\n"
        for sv in scene_graph["state_vars"]:
            main_output += "    - " + sv + "\n"
        main_output += "\n"

        # 选择设计
        main_output += sep + "\n"
        main_output += "【选择设计】 " + choice_type + "\n"
        main_output += sep + "\n\n"
        main_output += "  设计原则: " + choice_data["design_principle"] + "\n"
        main_output += "  后果设计: " + choice_data["consequence_design"] + "\n"
        main_output += "  情绪权重: " + str(choice_data["emotion_weight"]) + "\n"
        main_output += "  镜头语言: " + choice_data["camera_language"] + "\n\n"
        main_output += "  困境模板:\n"
        for idx, d in enumerate(dilemma_list[:5], 1):
            main_output += "    " + str(idx) + ". " + d + "\n"
        main_output += "\n"

        # 无正确答案规则
        main_output += sep + "\n"
        main_output += "【选择设计铁律: 无正确答案】\n"
        main_output += sep + "\n\n"
        main_output += "  1. 每个选项必须有真正的代价 (gain something, lose something)\n"
        main_output += "  2. 后果延迟: 最佳选择在 2-3 场景后才显现, 而非立刻反馈\n"
        main_output += "  3. 假选择检测 (anti-pattern):\n"
        for fc in FALSE_CHOICE_DETECTION:
            main_output += "     [" + fc["severity"] + "] " + fc["pattern"] + "\n"
            main_output += "       -> " + fc["fix"] + "\n"
        main_output += "\n"

        # 收束机制
        main_output += sep + "\n"
        main_output += "【收束机制】\n"
        main_output += sep + "\n\n"
        for ck, cv in CONVERGENCE_MECHANISMS.items():
            marker = " <-- 当前" if ck == convergence_key else ""
            main_output += "  [" + cv["name"] + "]" + marker + "\n"
            main_output += "    " + cv["description"] + "\n"
            main_output += "    技术: " + cv["technique"] + "\n"
            main_output += "    风险: " + cv["risk"] + "\n"
            main_output += "    缓解: " + cv["mitigation"] + "\n\n"

        # 重玩价值
        main_output += sep + "\n"
        main_output += "【重玩价值设计】\n"
        main_output += sep + "\n\n"
        for rk, rv in REPLAY_VALUE_DESIGN.items():
            main_output += "  " + rk + ": " + rv + "\n"
        main_output += "\n"

        # 互动镜头语言
        main_output += sep + "\n"
        main_output += "【互动镜头语言】\n"
        main_output += sep + "\n\n"
        for cam_key, cam_val in INTERACTIVE_CAMERA_LANGUAGE.items():
            main_output += "  [" + cam_key + "]\n"
            for ck2, cv2 in cam_val.items():
                main_output += "    " + ck2 + ": " + cv2 + "\n"
            main_output += "\n"

        # 技术规格
        main_output += sep + "\n"
        main_output += "【互动平台技术规格】\n"
        main_output += sep + "\n\n"
        main_output += "  节点ID命名: N_{hash8} (基于场景内容的MD5前8位)\n"
        main_output += "  边条件格式: choice_{n} | state_check(var, threshold) | auto_converge\n"
        main_output += "  存档/检查点: 每个选择点前自动存档, 允许回退\n"
        main_output += "  存档数据: {node_id, state_vars, choice_history[], timestamp}\n"
        main_output += "  变量追踪: " + str(scene_graph["state_vars"][:3]) + "\n"
        main_output += "  分支数: " + str(branch_count) + " | 复杂度评分: " + str(arch_data["complexity_score"]) + "/10\n\n"

        # 叙事结构参考
        if narrative_ref:
            main_output += sep + "\n"
            main_output += "【适用叙事结构参考 (knowledge_base)】\n"
            main_output += sep + "\n\n"
            main_output += narrative_ref + "\n"

        # H3 三大字段
        main_output += sep + "\n"
        main_output += "H3 三大字段 (互动剧特化)\n"
        main_output += sep + "\n\n"
        main_output += h3_prompt + "\n\n"

        # 30 秒场景单元
        timeline_30s = build_30s_timeline(
            scene_type="互动选择", scene_desc=scene,
            speaker_id="S1", speaker_voice="a quiet, slightly hoarse middle-aged voice",
            dialogue="你选哪条路?", n_lines=1, director_intent=intent_feel, language="Chinese"
        )
        timeline_30s_lines = "\n".join(["  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc for (ts, te, stage, desc) in SCENE_UNIT_30S])
        main_output += sep + "\n"
        main_output += "30 秒场景单元 (互动剧: 含选择窗口)\n"
        main_output += sep + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        # 导演意图 5 维
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext + " (选择时刻情绪: " + str(choice_data.get("emotion_weight", "")) + ")",
            "关系": "选择改变关系 (信任/背叛/亲密/疏离)",
            "主题": mood + " -> 互动剧主题: 每个选择都有重量",
            "留白": "没选的那条路永远是个谜 - " + props,
        }
        intent_block = inject_director_intent(intent_5d)
        main_output += sep + "\n"
        main_output += "导演意图 5 维 (互动剧特化)\n"
        main_output += sep + "\n\n"
        main_output += intent_block + "\n\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ================================================================
        # 第二个输出: 经验矩阵
        # ================================================================
        experience = "【互动剧经验矩阵】\n\n"

        experience += "【互动剧参考作品分析】\n"
        interactive_refs = [
            ("黑镜: 潘达斯奈基 (Bandersnatch)", "Binary branching, 5 endings, dead-end loops force retry, meta-narrative about free will"),
            ("底特律: 变人 (Detroit: Become Human)", "3 protagonists, tree branching per character, shared world state, 40+ endings"),
            ("隐形守护者", "Network structure, trust/faction variables, Chinese interactive drama, 8+ endings"),
            ("Late Shift", "Binary choices, cinematic FMV, timer pressure, 180+ decision points"),
            ("Her Story", "Information-seeking choices, non-linear discovery, player-driven narrative"),
            ("Twelve Minutes", "Time loop + choice reset, knowledge persistence across loops"),
        ]
        for title, analysis in interactive_refs:
            experience += "  - " + title + "\n    " + analysis + "\n"
        experience += "\n"

        experience += "【分支叙事设计原则 (实战提炼)】\n"
        experience += "  1. 有意义的选择 > 多选项: 3个精心设计的选择 > 10个浅薄选择\n"
        experience += "  2. 后果可见性: 选择后 1-3 场景内必须有至少一个可见后果\n"
        experience += "  3. 状态一致性: 角色在不同路径中的行为必须与累积状态一致\n"
        experience += "  4. 收束自然性: 路径合并时不能让玩家感到选择被无视\n"
        experience += "  5. 制作效率: 共享场景资产 + 差异化对话/反应 > 完全独立场景\n\n"

        experience += "【20 导演互动剧适配】\n"
        for d in DIRECTORS_20:
            experience += "  - " + d + "\n"
        experience += "\n"

        experience += "【11 维导演控制能力】\n"
        experience += inject_director_control_11() + "\n"

        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # ================================================================
        # 第三个输出: AI 深度处理
        # ================================================================
        ai_deep_output = "【互动剧 AI 深度处理】\n\n"

        ai_deep_output += "【分支叙事架构详解】\n"
        for bk, bv in BRANCHING_ARCHITECTURES.items():
            if bk == "auto":
                continue
            ai_deep_output += "  [" + bk + "] " + bv["description"] + "\n"
            ai_deep_output += "    节点上限: " + str(bv["max_nodes"]) + " | 边上限: " + str(bv["max_edges"]) + "\n"
            ai_deep_output += "    参考: " + bv["example"] + "\n\n"

        ai_deep_output += "【选择类型完整框架】\n"
        for ctk, ctv in CHOICE_TYPE_FRAMEWORKS.items():
            if ctk == "auto":
                continue
            ai_deep_output += "  [" + ctk + "]\n"
            ai_deep_output += "    原则: " + ctv["design_principle"] + "\n"
            ai_deep_output += "    后果: " + ctv["consequence_design"] + "\n"
            ai_deep_output += "    情绪: " + str(ctv["emotion_weight"]) + "\n"
            ai_deep_output += "    镜头: " + ctv["camera_language"] + "\n"
            for tpl in ctv["dilemma_templates"][:3]:
                ai_deep_output += "      - " + tpl + "\n"
            ai_deep_output += "\n"

        ai_deep_output += "【收束机制】\n"
        for cvk, cvv in CONVERGENCE_MECHANISMS.items():
            ai_deep_output += "  [" + cvv["name"] + "] " + cvv["description"] + "\n"
            ai_deep_output += "    技术: " + cvv["technique"] + "\n"
            ai_deep_output += "    缓解: " + cvv["mitigation"] + "\n\n"

        ai_deep_output += "【重玩价值矩阵】\n"
        for rpk, rpv in REPLAY_VALUE_DESIGN.items():
            ai_deep_output += "  " + rpk + ": " + rpv + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【互动镜头语言手册】\n"
        for ick, icv in INTERACTIVE_CAMERA_LANGUAGE.items():
            ai_deep_output += "  [" + ick + "]\n"
            for ick2, icv2 in icv.items():
                ai_deep_output += "    " + ick2 + ": " + icv2 + "\n"
            ai_deep_output += "\n"

        ai_deep_output += "【假选择检测清单】\n"
        for fc in FALSE_CHOICE_DETECTION:
            ai_deep_output += "  [" + fc["severity"] + "] " + fc["pattern"] + "\n"
            ai_deep_output += "    FIX: " + fc["fix"] + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【191 反 AI 词表 + 4 轮迭代】\n"
        ai_deep_output += "瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词\n\n"

        ai_deep_output += "【沉默 5 规则 + 4 步公式】\n"
        ai_deep_output += inject_silence_mastery_5("互动选择", 1) + "\n\n"

        ai_deep_output += "【9 维光照控制 (CIE LAB + 摄影本体)】\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "InteractiveDramaPro": InteractiveDramaPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "InteractiveDramaPro": "🎮 互动剧 (环节 41) — L5 重写",
# }
