# -*- coding: utf-8 -*-
"""
dm_memory 四域 schema 校验 (批次4 builder-m1)
==============================================
覆盖: 决策卡 / 偏好 / 程序记忆 / 风格圣经+系列档案 (验收①)。
只做结构校验 (必填键/枚举/长度), 不做 IO; 对多余键宽容 (additive 演进不破旧档)。
常量全部导出: m3 注入与双盲互审复用同一套口径, 不许各写各的。
"""
CARD_REQUIRED_KEYS = ("标题", "signal", "status")
CARD_SIGNALS = ("用户确认", "成片采用", "生成", "用户纠正")
CARD_VERIFIED_SIGNALS = ("用户确认", "成片采用")   # 只有这些信号产生正面教训 (验收②)
CARD_STATUSES = ("candidate", "confirmed", "rejected")
CARD_TITLE_MAX = 60
CARD_FIELD_MAX = 2000
CARD_PROMPT_MAX = 1100

PREFERENCE_REQUIRED_KEYS = ("标题", "内容")
PREFERENCE_TITLE_MAX = 60
PREFERENCE_CONTENT_MAX = 2000
PREFERENCE_BRANCHES = ("added", "equivalent_skipped", "refined",
                       "conflict_replaced", "invalid_removed", "oneoff_ignored")
PREFERENCE_JACCARD_THRESHOLD = 0.8
PREFERENCE_ONEOFF_SIGNALS = ("一次性", "临时", "本轮")

PROCEDURE_REQUIRED_KEYS = ("use_when", "procedure", "exceptions")
PROCEDURE_TOPIC_MAX = 80
PROCEDURE_FIELD_MAX = 2000

BIBLE_REQUIRED_KEYS = ("项目", "脚本统计", "蒸馏段", "蒸馏状态")
BIBLE_DISTILL_STATES = ("pending", "done")
BIBLE_DISTILL_PENDING = "LLM_DISTILL_PENDING"
BIBLE_TITLE_MAX = 80

SERIES_REQUIRED_KEYS = ("worldview", "风格锚", "dna")
SERIES_FIELD_MAX = 4000
SERIES_DNA_MAX = 64


def _check_str(errors, value, label, max_len, required=True):
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            errors.append(f"{label} 必填且为非空字符串")
        return
    if not isinstance(value, str):
        errors.append(f"{label} 须为字符串")
        return
    if len(value) > max_len:
        errors.append(f"{label} 超长 (>{max_len})")


def validate_card(entry):
    """决策卡校验。rejected 卡被否方案必填 (负面证据纪律, add_card 同口径拒绝)。"""
    errors = []
    if not isinstance(entry, dict):
        return False, ["决策卡不是 dict"]
    _check_str(errors, entry.get("标题"), "标题", CARD_TITLE_MAX)
    if entry.get("signal") not in CARD_SIGNALS:
        errors.append(f"signal 必须是 {list(CARD_SIGNALS)} 之一")
    if entry.get("status") not in CARD_STATUSES:
        errors.append(f"status 必须是 {list(CARD_STATUSES)} 之一")
    for key in ("方案", "教训", "被否方案"):
        v = entry.get(key)
        if v is not None and (not isinstance(v, str) or len(v) > CARD_FIELD_MAX):
            errors.append(f"{key} 须为字符串且 ≤{CARD_FIELD_MAX}")
    if entry.get("status") == "rejected":
        plan = entry.get("被否方案")
        if not isinstance(plan, str) or not plan.strip():
            errors.append("rejected 卡 被否方案 必填 (负面证据保留纪律)")
    if "card_id" in entry and (not isinstance(entry["card_id"], str) or not entry["card_id"]):
        errors.append("card_id 须为非空字符串")
    return (not errors), errors


def validate_preference(entry):
    """偏好条目校验。失效/冲突替换/一次性 须为布尔标记。"""
    errors = []
    if not isinstance(entry, dict):
        return False, ["偏好条目不是 dict"]
    _check_str(errors, entry.get("标题"), "标题", PREFERENCE_TITLE_MAX)
    _check_str(errors, entry.get("内容"), "内容", PREFERENCE_CONTENT_MAX)
    for key in ("失效", "冲突替换", "一次性"):
        if key in entry and not isinstance(entry[key], bool):
            errors.append(f"{key} 须为布尔值")
    if "signal" in entry and (not isinstance(entry["signal"], str) or not entry["signal"].strip()):
        errors.append("signal 须为非空字符串")
    return (not errors), errors


def validate_procedure(doc):
    """SOP 三段式 use_when/procedure/exceptions 校验。"""
    errors = []
    if not isinstance(doc, dict):
        return False, ["SOP 不是 dict"]
    for key in PROCEDURE_REQUIRED_KEYS:
        v = doc.get(key)
        if not isinstance(v, str) or not v.strip():
            errors.append(f"{key} 必填且为非空字符串 (SOP 三段式)")
        elif len(v) > PROCEDURE_FIELD_MAX:
            errors.append(f"{key} 超长 (>{PROCEDURE_FIELD_MAX})")
    return (not errors), errors


def validate_bible(bible):
    """风格圣经校验。蒸馏未完成时必须带诚实占位标记, 不许猜测。"""
    errors = []
    if not isinstance(bible, dict):
        return False, ["风格圣经不是 dict"]
    _check_str(errors, bible.get("项目"), "项目", BIBLE_TITLE_MAX)
    if not isinstance(bible.get("脚本统计"), dict):
        errors.append("脚本统计 必填且为 dict (脚本采证确定性骨架)")
    state = bible.get("蒸馏状态")
    if state not in BIBLE_DISTILL_STATES:
        errors.append(f"蒸馏状态 必须是 {list(BIBLE_DISTILL_STATES)} 之一")
    distill = bible.get("蒸馏段")
    if not isinstance(distill, str):
        errors.append("蒸馏段 须为字符串")
    elif state == "pending" and BIBLE_DISTILL_PENDING not in distill:
        errors.append(f"蒸馏未完成时 蒸馏段 必须含 {BIBLE_DISTILL_PENDING} 诚实占位 (不许猜测)")
    return (not errors), errors


def validate_series(payload):
    """系列档案校验: worldview/风格锚 字符串 + dna 列表 (元素为字符串或 dict)。
    口径注记 (R1 一致性 LOW): upsert_series 允许 payload 三键含其一即落盘
    (系列档案允许分阶段补齐), 本校验器用于全量校验场景 — 分阶段落盘的档案
    在补齐前不过本校验属预期, inherit 读取侧以 .get 容错, 无功能破坏。"""
    errors = []
    if not isinstance(payload, dict):
        return False, ["系列档案不是 dict"]
    for key in ("worldview", "风格锚"):
        _check_str(errors, payload.get(key), key, SERIES_FIELD_MAX)
    dna = payload.get("dna")
    if not isinstance(dna, list):
        errors.append("dna 必须为列表 (角色 DNA 档列表)")
    elif len(dna) > SERIES_DNA_MAX:
        errors.append(f"dna 数量超限 (>{SERIES_DNA_MAX})")
    else:
        for i, item in enumerate(dna):
            if not isinstance(item, (str, dict)):
                errors.append(f"dna[{i}] 须为字符串或 dict")
    return (not errors), errors
