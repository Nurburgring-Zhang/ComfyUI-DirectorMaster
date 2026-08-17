# -*- coding: utf-8 -*-
"""
CleanupPassPro - 清理通道节点 (P2 工程化)
================================================
Phase 28 P2 - 清理节点输出 (去除 AI 味/反 AI 词/格式化)

清理内容:
- 191 个反 AI 词表
- 重复内容
- AI 套路表达 (瞳孔地震/心中暗道/绝美地笑了)
- 格式不一致
- 无效信息
"""
from __future__ import annotations

import re
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False


# ============================================================
# 清理规则
# ============================================================
CLEANUP_RULES = {
    "remove_anti_ai_phrases": True,  # 移除反 AI 词
    "remove_repetitions": True,  # 移除重复句
    "remove_template_phrases": True,  # 移除模板表达
    "normalize_whitespace": True,  # 标准化空白
    "remove_empty_lines": True,  # 移除空行
    "trim_lines": True,  # trim 每行
}


TEMPLATE_PHRASES = [
    r"在当今.*?的时代[，,].*?[。\.]",
    r"随着.*?的不断发展[，,].*?[。\.]",
    r"本文将.*?介绍[。\.]",
    r"首先[，,].*?其次[，,].*?最后[。\.]",
    r"总而言之[，,].*?[。\.]",
    r"综上所述[，,].*?[。\.]",
    r"值得注意的是[，,].*?[。\.]",
]


def cleanup_text(text, rules=None):
    """清理文本"""
    if not text:
        return text

    if rules is None:
        rules = CLEANUP_RULES

    result = text

    # 1. 反 AI 词
    if rules.get("remove_anti_ai_phrases") and _HAS_ANTI_AI:
        result = clean_anti_ai_text(result)

    # 2. 模板表达
    if rules.get("remove_template_phrases"):
        for pattern in TEMPLATE_PHRASES:
            result = re.sub(pattern, "", result, flags=re.MULTILINE)

    # 3. 重复句
    if rules.get("remove_repetitions"):
        seen = set()
        lines = result.split("\n")
        new_lines = []
        for line in lines:
            key = line.strip().lower()
            if key and key in seen:
                continue
            seen.add(key)
            new_lines.append(line)
        result = "\n".join(new_lines)

    # 4. 标准化空白
    if rules.get("normalize_whitespace"):
        result = re.sub(r"[ \t]+", " ", result)
        result = re.sub(r" *\n *", "\n", result)

    # 5. 移除空行
    if rules.get("remove_empty_lines"):
        result = re.sub(r"\n{3,}", "\n\n", result)

    # 6. trim 每行
    if rules.get("trim_lines"):
        result = "\n".join([line.strip() for line in result.split("\n")])

    return result.strip()


def cleanup_prompt_output(prompt_text, strict=True):
    """专门清理 prompt 输出"""
    rules = CLEANUP_RULES.copy()
    if strict:
        rules["remove_anti_ai_phrases"] = True
        rules["remove_repetitions"] = True
        rules["remove_template_phrases"] = True
    return cleanup_text(prompt_text, rules)


def get_cleanup_stats(original, cleaned):
    """获取清理统计"""
    return {
        "original_length": len(original),
        "cleaned_length": len(cleaned),
        "removed_chars": len(original) - len(cleaned),
        "removed_pct": round((len(original) - len(cleaned)) / max(1, len(original)) * 100, 1),
    }


# ============================================================
# ComfyUI 节点
# ============================================================
class CleanupPassPro:
    """
    清理通道 Pro 节点 - Phase 28 P2
    工程化: 清理反 AI 词 / 重复 / 模板

    自动赋予: 默认严格清理
    专项调整: 6 维规则开关
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "输入文本": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "移除反AI词": (["ON", "OFF"], {"default": "ON"}),
                "移除重复句": (["ON", "OFF"], {"default": "ON"}),
                "移除模板表达": (["ON", "OFF"], {"default": "ON"}),
                "标准化空白": (["ON", "OFF"], {"default": "ON"}),
                "移除空行": (["ON", "OFF"], {"default": "ON"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("清理后文本", "清理统计", "报告")
    FUNCTION = "cleanup"
    CATEGORY = "Director/Engineering"

    def cleanup(self, **kwargs):
        text = kwargs.get("输入文本", "")
        rules = {
            "remove_anti_ai_phrases": kwargs.get("移除反AI词", "ON") == "ON",
            "remove_repetitions": kwargs.get("移除重复句", "ON") == "ON",
            "remove_template_phrases": kwargs.get("移除模板表达", "ON") == "ON",
            "normalize_whitespace": kwargs.get("标准化空白", "ON") == "ON",
            "remove_empty_lines": kwargs.get("移除空行", "ON") == "ON",
            "trim_lines": True,
        }
        cleaned = cleanup_text(text, rules)
        stats = get_cleanup_stats(text, cleaned)
        stats_str = json.dumps(stats, ensure_ascii=False, indent=2)
        report = "清理完成: 移除 {} 字符 ({}%)\n规则: {}".format(
            stats["removed_chars"], stats["removed_pct"], rules
        )
        return (cleaned, stats_str, report)


import json
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "CleanupPassPro": CleanupPassPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "CleanupPassPro": "🧹 清理通道 Pro (P2) — Phase 28 P2 / 反AI+重复+模板+空白",
# }
