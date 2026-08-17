# -*- coding: utf-8 -*-
"""
ShotSelectionPro - 选片决策节点 (环节 30)
================================================
Phase 27 P0 补全节点 - AIGC 影视全流程解析环节 30 "选片决策"

AI 时代最关键的环节: 一次生成多候选, 从中选最佳
本节点模拟"导演选片"决策逻辑, 基于多维度评分给候选打分并选最佳

核心能力 (AIGC 文档 2.1 节):
- 叙事架构力: 哪个候选最符合剧本结构
- 情感调度力: 哪个候选最能让观众感受到目标情感
- 节奏控制力: 哪个候选最符合节奏曲线
- 视觉语言力: 哪个候选视觉层次最好
- 表演指导力: 哪个候选表演最自然

5 要素架构 (AIGC 文档 1.2 节):
- 数据层: 评分维度权重 (导演风格 / 情感匹配 / 视觉美感 / 表演自然 / 节奏契合)
- 上下文缩略层: 候选概要
- Skill/Harness: 评分算法 (加权求和)
- 经验矩阵: 历史最优 (从 director_soul 灵魂注入)
- AI 深度处理: LLM 风格的综合决策
"""

import os
import sys
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False

# Phase 17 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# 8 大评分维度 (基于 AIGC 文档 2.1 节顶级导演能力)
# ============================================================
SCORING_DIMENSIONS_8 = {
    "1_叙事架构": {
        "description": "候选是否符合剧本的三幕剧结构、情节点、角色弧光",
        "weight_default": 0.15,
        "criteria": "场景在剧情中的位置 / 信息密度 / 推动剧情 / 与前后的连贯",
    },
    "2_情感调度": {
        "description": "候选能否让观众在特定时刻感受到目标情感",
        "weight_default": 0.20,
        "criteria": "目标情感是否清晰 / 强度是否匹配场景权重 / 是否有潜文本",
    },
    "3_节奏控制": {
        "description": "候选是否符合导演节奏签名 (王家卫慢 / 诺兰快 / 塔可夫斯基极慢)",
        "weight_default": 0.15,
        "criteria": "镜头长度 / 切点位置 / 静默比例 / 加速减速曲线",
    },
    "4_视觉语言": {
        "description": "候选的构图 / 光影 / 色彩 / 镜头语言是否传达潜文本",
        "weight_default": 0.15,
        "criteria": "构图 / 焦段 / 光影方向 / 色彩情绪 / 视觉层次",
    },
    "5_表演指导": {
        "description": "候选中演员/角色的微动作 / 表情 / 身体语言是否自然",
        "weight_default": 0.10,
        "criteria": "微动作总和 / 面部肌肉 / 身体习惯 / 口头禅",
    },
    "6_场面调度": {
        "description": "候选中角色在空间中的位置 / 运动是否符合空间叙事",
        "weight_default": 0.10,
        "criteria": "空间布局 / 角色位置 / 运动轨迹 / 180°轴线",
    },
    "7_审美判断": {
        "description": "候选整体是否独特 / 是否符合导演风格美学",
        "weight_default": 0.10,
        "criteria": "风格独特性 / 美学一致性 / 导演签名",
    },
    "8_反AI味": {
        "description": "候选是否避免了 AI 套路 (瞳孔地震/心中暗道/绝美地笑了)",
        "weight_default": 0.05,
        "criteria": "反 AI 词表 191 词 / 10 强制具体细节 / 沉默比例",
    },
}

# 决策算法 (候选打分 + 加权求和)
def score_candidate(candidate_text, scoring_weights=None, director="", target_emotion=""):
    """
    对单个候选打分 (8 维度)
    返回: dict {维度: 分数, 总分, 决策建议}

    算法: 基于关键词 + 字符统计的启发式评分
    """
    if not candidate_text:
        return {"总分": 0, "评分明细": {}, "建议": "候选为空"}

    weights = scoring_weights or {k: v["weight_default"] for k, v in SCORING_DIMENSIONS_8.items()}

    # 1. 叙事架构: 检测情节点关键词
    narrative_keywords = ["因为", "所以", "但是", "然后", "突然", "结果", "意识到", "发现", "决定", "选择"]
    narrative_score = min(1.0, sum(0.1 for k in narrative_keywords if k in candidate_text))

    # 2. 情感调度: 检测情感词
    emotion_keywords = ["情感", "感受", "观众", "心", "灵魂", "眼泪", "笑容", "痛苦", "孤独", "温暖", "失去", "眷恋"]
    emotion_score = min(1.0, sum(0.1 for k in emotion_keywords if k in candidate_text))
    if target_emotion and target_emotion in candidate_text:
        emotion_score = min(1.0, emotion_score + 0.2)

    # 3. 节奏控制: 检测节奏词
    rhythm_keywords = ["慢", "快", "停顿", "加速", "静止", "跳跃", "切换", "长镜", "跳切"]
    rhythm_score = min(1.0, sum(0.1 for k in rhythm_keywords if k in candidate_text))
    # 导演偏好节奏加成
    if director in ["王家卫", "侯孝贤", "塔可夫斯基"] and "慢" in candidate_text:
        rhythm_score = min(1.0, rhythm_score + 0.15)
    if director in ["诺兰", "奉俊昊", "芬奇"] and ("快" in candidate_text or "跳切" in candidate_text):
        rhythm_score = min(1.0, rhythm_score + 0.15)

    # 4. 视觉语言: 检测视觉词
    visual_keywords = ["构图", "光", "影", "色", "镜头", "焦段", "景深", "对称", "三分法", "视觉"]
    visual_score = min(1.0, sum(0.08 for k in visual_keywords if k in candidate_text))

    # 5. 表演指导: 检测表演词
    performance_keywords = ["微动作", "表情", "眼神", "身体", "手势", "点头", "摇头", "沉默", "台词"]
    performance_score = min(1.0, sum(0.1 for k in performance_keywords if k in candidate_text))

    # 6. 场面调度: 检测空间词
    spatial_keywords = ["空间", "位置", "移动", "走向", "背对", "面对", "侧身", "站立", "坐下", "走"]
    spatial_score = min(1.0, sum(0.1 for k in spatial_keywords if k in candidate_text))

    # 7. 审美判断: 检测风格词
    aesthetic_keywords = ["风格", "美学", "氛围", "气质", "独特", "签名", "偏好"]
    aesthetic_score = min(1.0, sum(0.1 for k in aesthetic_keywords if k in candidate_text))

    # 8. 反AI味: 检测 AI 套路词 (越多越减分)
    ai_cliches = ["瞳孔地震", "心中暗道", "绝美地笑了", "缓缓地转过头", "复杂地说", "陷入了深深的沉思",
                  "美若天仙", "悲愤交加", "苦涩地笑了", "下定决心", "陷入恐慌"]
    ai_count = sum(1 for c in ai_cliches if c in candidate_text)
    anti_ai_score = max(0.0, 1.0 - ai_count * 0.3)

    scores = {
        "1_叙事架构": round(narrative_score, 3),
        "2_情感调度": round(emotion_score, 3),
        "3_节奏控制": round(rhythm_score, 3),
        "4_视觉语言": round(visual_score, 3),
        "5_表演指导": round(performance_score, 3),
        "6_场面调度": round(spatial_score, 3),
        "7_审美判断": round(aesthetic_score, 3),
        "8_反AI味": round(anti_ai_score, 3),
    }

    total = sum(scores[k] * weights.get(k, 0.1) for k in scores)
    total = round(total, 3)

    # 决策建议
    if total >= 0.7:
        suggestion = "强烈推荐 - 顶级候选"
    elif total >= 0.5:
        suggestion = "推荐 - 良好候选"
    elif total >= 0.3:
        suggestion = "可用 - 中等候选"
    else:
        suggestion = "不推荐 - 需重做"

    return {
        "总分": total,
        "评分明细": scores,
        "建议": suggestion,
    }


# ============================================================
# 选片决策节点
# ============================================================
class ShotSelectionPro:
    """
    选片决策节点 (环节 30) — Phase 27 P0 补全
    输入多个候选, 8 维度评分, 选最佳 + 给出决策理由
    """

    @classmethod
    def INPUT_TYPES(cls):
        dim_keys = list(SCORING_DIMENSIONS_8.keys())
        return {
            "required": {
                "候选1": ("STRING", {
                    "default": "[Shot 1] 父女在厨房, 雨夜。镜头: 静止远景, 8 秒。色调: 暖橙黄+老红+老白绿 (王家卫 60:30:10)。光: 侧光, 长阴影, 黄昏。表演: 父亲背影切菜, 女儿坐桌边无言。情绪: loneliness 0.7 + longing 0.3 F3 50/50。灵感: 花样年华走廊擦肩。",
                    "multiline": True,
                }),
                "候选2": ("STRING", {
                    "default": "[Shot 1] 父女厨房, 雨夜。镜头: 快速切换, 4 秒。色调: 冷蓝+铁灰。表演: 父亲瞳孔地震, 心中暗道: '她不简单。' 女儿绝美地笑了。情绪: 复杂地说: '我不知道。' 灵感: AI 套路。",
                    "multiline": True,
                }),
                "候选3": ("STRING", {
                    "default": "[Shot 1] 父亲 60 岁, 女儿 28 岁, 厨房 8 平米, 老式吊灯下, 米酒一壶。镜头: 60fps 慢镜头 12 秒。构图: rule_of_thirds, 主体小在画面右下。声音: 雨声 + 切菜声 + 老式收音机低唱。情绪: 父亲背影沉默, 女儿看着父亲背影, 想说话但没说。",
                    "multiline": True,
                }),
                "导演风格": (["王家卫", "诺兰", "是枝裕和", "侯孝贤", "奉俊昊", "黑泽明", "塔可夫斯基", "大卫·芬奇", "李安", "陈凯歌", "贾樟柯", "蔡明亮", "李沧东", "毕赣"],
                    {"default": "王家卫"}),
                "目标情感": (["loneliness", "longing", "fear", "warm_regret", "tenderness", "joy", "sadness", "lucid_despair", "ji", "yuan"],
                    {"default": "loneliness"}),
                "决策权重_1_叙事": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_2_情感": ("FLOAT", {"default": 0.20, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_3_节奏": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_4_视觉": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_5_表演": ("FLOAT", {"default": 0.10, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_6_空间": ("FLOAT", {"default": 0.10, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_7_审美": ("FLOAT", {"default": 0.10, "min": 0.0, "max": 0.5, "step": 0.05}),
                "决策权重_8_反AI": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 0.5, "step": 0.05}),
            },
            "optional": {
                "候选4": ("STRING", {"default": "", "multiline": True}),
                "候选5": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("shot_selection_decision", "scoring_matrix", "director_rationale")
    FUNCTION = "select_shot"
    CATEGORY = "PromptLibrary/Phase27 选片决策"

    def select_shot(self, **kwargs):
        if not _HAS_ANTI_AI:
            return ("未加载 anti_ai_vocab", "", "")

        director = kwargs.get("导演风格", "王家卫")
        target_emotion = kwargs.get("目标情感", "loneliness")

        # 自定义权重
        custom_weights = {
            "1_叙事架构": kwargs.get("决策权重_1_叙事", 0.15),
            "2_情感调度": kwargs.get("决策权重_2_情感", 0.20),
            "3_节奏控制": kwargs.get("决策权重_3_节奏", 0.15),
            "4_视觉语言": kwargs.get("决策权重_4_视觉", 0.15),
            "5_表演指导": kwargs.get("决策权重_5_表演", 0.10),
            "6_场面调度": kwargs.get("决策权重_6_空间", 0.10),
            "7_审美判断": kwargs.get("决策权重_7_审美", 0.10),
            "8_反AI味": kwargs.get("决策权重_8_反AI", 0.05),
        }
        # 归一化
        w_sum = sum(custom_weights.values())
        if w_sum > 0:
            custom_weights = {k: v / w_sum for k, v in custom_weights.items()}

        # 收集所有候选
        candidates = []
        for i in range(1, 6):
            c = kwargs.get(f"候选{i}", "")
            if c and c.strip():
                candidates.append((f"候选{i}", c))

        if not candidates:
            return ("未提供候选", "", "请输入至少 1 个候选")

        # 对每个候选打分
        scored = []
        for name, text in candidates:
            result = score_candidate(text, custom_weights, director, target_emotion)
            scored.append((name, text, result))

        # 选最高分
        scored.sort(key=lambda x: x[2]["总分"], reverse=True)
        best_name, best_text, best_result = scored[0]

        # 输出 1: 选片决策
        decision = "【选片决策 (Phase 27 环节 30)】\n\n"
        decision += "=" * 60 + "\n"
        decision += "导演: " + director + "\n"
        decision += "目标情感: " + target_emotion + "\n"
        decision += "候选数: " + str(len(candidates)) + "\n"
        decision += "=" * 60 + "\n\n"
        decision += "【最佳候选】" + best_name + " (总分 " + str(best_result["总分"]) + " / 1.0)\n"
        decision += "建议: " + best_result["建议"] + "\n\n"
        decision += "【最佳候选内容】\n" + best_text + "\n\n"
        decision += "【全部候选排名】\n"
        for i, (name, _, result) in enumerate(scored, 1):
            decision += "  " + str(i) + ". " + name + " - 总分 " + str(result["总分"]) + " - " + result["建议"] + "\n"

        # 输出 2: 评分矩阵 (按候选实际编号, 不是排序)
        matrix = "【8 维度评分矩阵】\n\n"
        matrix += "维度             | 权重   | "
        for name, _, _ in scored:
            matrix += name.ljust(8) + " | "
        matrix += "\n"
        matrix += "-" * (20 + 11 * len(scored)) + "\n"
        for dim_key, dim_info in SCORING_DIMENSIONS_8.items():
            weight = custom_weights.get(dim_key, 0.0)
            scores_str = ""
            for name, _, result in scored:
                s = result["评分明细"].get(dim_key, 0)
                scores_str += " | " + str(s).ljust(8)
            matrix += dim_key.ljust(16) + " | " + str(round(weight, 3)).ljust(6) + scores_str + "\n"
        matrix += "-" * (20 + 11 * len(scored)) + "\n"
        matrix += "总分             |        | "
        for name, _, result in scored:
            matrix += str(result["总分"]).ljust(8) + " | "
        matrix += "\n"

        # 输出 3: 导演视角决策理由
        rationale = "【导演决策理由 - " + director + "】\n\n"
        rationale += "为什么 " + best_name + " 胜出？\n\n"
        # 找出 3 个最强维度
        top_dims = sorted(best_result["评分明细"].items(), key=lambda x: x[1], reverse=True)[:3]
        for dim_key, score in top_dims:
            dim_info = SCORING_DIMENSIONS_8[dim_key]
            rationale += "- " + dim_info["description"] + " (得分 " + str(score) + ")\n"
            rationale += "  评估: " + dim_info["criteria"] + "\n\n"
        # 导演签名
        if director == "王家卫":
            rationale += "【王家卫选片理由】\n"
            rationale += "- 时间拉长, 物件代替心理, 留白比台词更有力\n"
            rationale += "- 看候选中是否体现'物件承载情感' (怀表/缝纫机/信)\n"
        elif director == "诺兰":
            rationale += "【诺兰选片理由】\n"
            rationale += "- 时间结构即主题, 强冲突, 强对比\n"
            rationale += "- 看候选中是否体现'时间的物理重量'\n"
        elif director == "侯孝贤":
            rationale += "【侯孝贤选片理由】\n"
            rationale += "- 不动, 让沉默说话, 中式意境\n"
            rationale += "- 看候选中是否体现'长镜 + 静默 + 远景'\n"

        if _HAS_ANTI_AI:
            decision = inject_anti_ai_rules(decision)
            matrix = inject_anti_ai_rules(matrix)
            rationale = inject_anti_ai_rules(rationale)

        return (decision, matrix, rationale)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ShotSelectionPro": ShotSelectionPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ShotSelectionPro": "🎯 选片决策 (环节 30) — Phase 27 P0",
# }
