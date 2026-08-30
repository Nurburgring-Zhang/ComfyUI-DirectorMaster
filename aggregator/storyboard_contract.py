# -*- coding: utf-8 -*-
"""
《DM 分镜 JSON 契约 v1》— 分镜 JSON 的结构契约 / 宽容解析 / 规范化校验
=======================================================================
批次2-WaveA2 (builder-contract). 设计文档 §5, 以 V16.2.0 真实 Cinematic JSON
结构为基 (设计文档英文键框架 → 真实中文键为准, 偏差记录见实现日志 contract.md)。

三态字段:
  canonical — 契约核心键 = contract_version + 真实 18 顶层键 + 真实 32 每镜键
  (V16.4/V16.5 增量键 叙事拓扑/场景实体/设备美学包/同期声枚举 与
   叙事标签/节奏手记/拓扑张力/构图 已吸收进注册表)
              + 契约表达式键 start/end (相对/绝对时间入口)
  derived   — start_s / end_s (拓扑解析计算) + duration_s (时长数值化)
  legacy    — 旧键别名 (设计文档英文键 + 内部 shot dict 英文键), 命中即映射
              进 normalized 并记 deprecated-field 警告

诊断码 (11 个, {code, field, value, message} 结构化):
  missing-contract-version / invalid-contract-version / missing-shot-id /
  duplicate-shot-id / invalid-duration / type-mismatch / empty-shots /
  relative-ref-unknown / relative-ref-cycle / deprecated-field(warning) /
  unknown-field(warning, 值保留于 normalized 的 extra)

公共 API:
  validate_storyboard(data)     → {"ok", "errors", "warnings", "normalized"} 永不抛
  parse_storyboard_json(text)   → (data|None, warnings) 复用 pln_llm.json_loads_tolerant 永不抛
  attach_contract_version(data) → 幂等注入 "contract_version": 1 永不抛
  self_check()                  → 最小样例自检 (doctor 第 9 类消费)

相对镜头表达式 (start/end 两键, F2-2/F2-6):
  字符串形态 "<shot_id>±<float>s"   例: "3+1.5s" / "shotA-0.5s"
  字典形态   {"ref": <shot_id>, "op": "+"|"-", "offset_s": <float>}
  锚点语义: ref 一律锚定被引用镜头的 end_s (前镜结束点), op/offset 施加偏移。
  拓扑解析 (轮次推进, 无递归), 未知引用 → relative-ref-unknown,
  互相依赖成环 → relative-ref-cycle, 全部进 errors 不抛异常;
  解析失败的镜头回退链式默认 (前一镜 end_s, 首镜 0.0)。

零第三方依赖 (仅 stdlib), Python ≥3.8 语法兼容。
"""
import copy as _copy
import math as _math
import re as _re

STORYBOARD_CONTRACT_VERSION = 1
# 别名导出 (doctor 第 9 类口径保险: "CONTRACT_VERSION==1")
CONTRACT_VERSION = STORYBOARD_CONTRACT_VERSION

# ------------------------------------------------------------------
# canonical 键 (真实 Cinematic JSON 实测键名, 见实现日志定位节)
# ------------------------------------------------------------------
CANON_TOP_KEYS = (
    "contract_version",
    "分镜数", "总时长秒", "导演", "情绪", "画面模式", "故事理论", "叙事结构",
    "AIGC生产模式", "AIGC判别依据", "叙事编排", "情感曲线", "叙事元数据",
    "叙事拓扑", "场景实体", "设备美学包", "同期声枚举",
    "分镜表", "上游应用统计",
)

# 每镜 canonical 键 (实测顺序) + 契约表达式键 start/end
CANON_SHOT_KEYS = (
    "镜号", "阶段", "类型阶段", "景别", "角度", "运镜", "焦段", "时长",
    "画面焦点", "声音", "转场", "叙事目的", "色彩", "光影", "材质", "氛围",
    "情绪", "首帧描述", "情感强度", "线", "POV", "时间线", "银幕序", "时序位",
    "构图", "叙事标签", "节奏手记", "拓扑张力",
    "AIGC提示词", "首帧提示词", "音频描述", "AIGC适配提示词",
    "start", "end",
)

# derived 键 (由解析器计算, 注入 normalized 每镜)
DERIVED_KEYS = ("duration_s", "start_s", "end_s")

# ------------------------------------------------------------------
# legacy 旧键别名表 → canonical (命中 = 重命名 + deprecated-field 警告)
# 来源: 设计文档 §5 英文键框架 + 内部 shot dict 英文键 (cinematic_studio/
# feature_film_engine/pro_format 的 shots 内部键名)
# ------------------------------------------------------------------
LEGACY_TOP_ALIASES = {
    "shots": "分镜表",
    "shot_count": "分镜数",
    "total_duration_s": "总时长秒",
    "mode": "画面模式",
    "director": "导演",
    "mood": "情绪",
    "story_theory": "故事理论",
    "narrative_mode": "叙事结构",
    "production_mode": "AIGC生产模式",
}

LEGACY_SHOT_ALIASES = {
    "shot_id": "镜号",
    "n": "镜号",
    "id": "镜号",
    "duration_s": "时长",
    "duration": "时长",
    "dur": "时长",
    "transition": "转场",
    "cut": "转场",
    "prompt": "AIGC提示词",
    "size": "景别",
    "move": "运镜",
    "focal": "焦段",
    "focus": "画面焦点",
    "sound": "声音",
    "purpose": "叙事目的",
    "stage": "阶段",
    "stage_name": "类型阶段",
    "angle": "角度",
    "emotion_intensity": "情感强度",
    "line": "线",
    "pov": "POV",
    "timeline": "时间线",
}

# ------------------------------------------------------------------
# 类型期望表 (type-mismatch 判定; None 一律放行视为缺省)
#   "int"=仅 int(拒 bool)  "num"=int/float(拒 bool)  "str"=str
#   "list" / "dict"  "id"=int 或非空 str(拒 bool)  "dur"=数值或字符串
# ------------------------------------------------------------------
_TOP_TYPED = {
    "分镜数": "int", "总时长秒": "num", "导演": "str", "情绪": "str",
    "画面模式": "str", "故事理论": "str", "叙事结构": "str",
    "AIGC生产模式": "str", "AIGC判别依据": "str", "叙事编排": "dict",
    "情感曲线": "list", "叙事元数据": "list", "分镜表": "list",
    "叙事拓扑": "dict", "场景实体": "dict", "设备美学包": "dict",
    "同期声枚举": "str",
    "上游应用统计": "dict",
}
_SHOT_STR_KEYS = (
    "阶段", "类型阶段", "景别", "角度", "运镜", "焦段", "画面焦点", "声音",
    "转场", "叙事目的", "色彩", "光影", "材质", "氛围", "情绪", "首帧描述",
    "线", "POV", "时间线", "构图", "叙事标签", "节奏手记",
    "AIGC提示词", "首帧提示词", "音频描述",
    "AIGC适配提示词",
)
_SHOT_TYPED = {
    "镜号": "id", "情感强度": "num", "银幕序": "num", "时序位": "num",
    "拓扑张力": "num",
    # 注: "时长" 不入通用类型表 — 时长全部类型/取值问题统一由 _parse_duration
    #     单一诊断通道负责 (invalid-duration), 避免 bool 等双重报码。
}
for _k in _SHOT_STR_KEYS:
    _SHOT_TYPED[_k] = "str"

# 诊断码全集 (结构化, 供 doctor/测试对账)
DIAGNOSTIC_CODES = (
    "missing-contract-version", "invalid-contract-version",
    "missing-shot-id", "duplicate-shot-id",
    "invalid-duration", "type-mismatch", "empty-shots",
    "relative-ref-unknown", "relative-ref-cycle",
    "deprecated-field", "unknown-field",
)

_REL_STR_RE = _re.compile(
    r"^\s*(?P<ref>.+?)\s*(?P<op>[+-])\s*(?P<off>\d+(?:\.\d+)?)\s*[sS秒]?\s*$")
_DUR_RE = _re.compile(
    r"^\s*(?P<v>-?\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds|秒)?\s*$", _re.IGNORECASE)

_VALUE_MAX = 80


# ------------------------------------------------------------------
# 内部工具
# ------------------------------------------------------------------
def _round3(x):
    """确定性舍入到 3 位小数; None 直通; 规范化 -0.0 → 0.0。"""
    if x is None:
        return None
    try:
        v = round(float(x), 3)
    except Exception:
        return None
    if v == 0:
        return 0.0
    return v


def _trim_value(v):
    """诊断 entry 的 value 字段: 可 JSON 序列化且截断到 _VALUE_MAX。"""
    if v is None or isinstance(v, (int, float, bool)):
        return v
    if isinstance(v, str):
        return v if len(v) <= _VALUE_MAX else v[:_VALUE_MAX] + "…"
    try:
        s = str(v)
    except Exception:
        s = type(v).__name__
    return s if len(s) <= _VALUE_MAX else s[:_VALUE_MAX] + "…"


def _type_ok(value, kind):
    """类型期望判定; None 一律放行 (视为缺省)。"""
    if value is None:
        return True
    if kind == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "num":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "str":
        return isinstance(value, str)
    if kind == "list":
        return isinstance(value, list)
    if kind == "dict":
        return isinstance(value, dict)
    if kind == "id":
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, str) and value.strip() != ""
    if kind == "dur":
        if isinstance(value, bool):
            return False
        return isinstance(value, (int, float, str))
    return True


def _parse_duration(raw):
    """时长解析 → 正的 float 秒 | None (不可解析/非正)。双形态: 数值 或 "3.8s" 式字符串。"""
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, (int, float)):
        v = float(raw)
    elif isinstance(raw, str):
        m = _DUR_RE.match(raw)
        if not m:
            return None
        v = float(m.group("v"))
    else:
        return None
    if not _math.isfinite(v) or v <= 0:
        return None
    return v


def _norm_ref_str(ref):
    """ref 值 → 查表用字符串键 (int/float 整数值 → 整数字符串)。非法返回 None。"""
    if isinstance(ref, bool):
        return None
    if isinstance(ref, int):
        return str(ref)
    if isinstance(ref, float):
        if not _math.isfinite(ref):
            return None
        return str(int(ref)) if float(ref).is_integer() else str(ref)
    if isinstance(ref, str):
        s = ref.strip()
        return s if s else None
    return None


def _classify_expr(value, add_err, field):
    """start/end 表达式分类。
    返回 None(缺省/None) / ("abs", float) / ("rel", (ref_str, signed_offset)) ;
    畸形 (不可解析) → 记 type-mismatch 并返回 ("bad", None)。"""
    if value is None:
        return None
    if isinstance(value, bool):
        add_err("type-mismatch", field, value, "start/end 表达式不可为布尔值")
        return ("bad", None)
    if isinstance(value, (int, float)):
        if not _math.isfinite(float(value)):
            add_err("type-mismatch", field, value, "start/end 绝对秒必须为有限数值")
            return ("bad", None)
        return ("abs", float(value))
    if isinstance(value, str):
        m = _REL_STR_RE.match(value)
        if not m:
            add_err("type-mismatch", field, value,
                    "相对引用字符串形态应为 \"<shot_id>±<float>s\"")
            return ("bad", None)
        off = float(m.group("off"))
        signed = off if m.group("op") == "+" else -off
        return ("rel", (m.group("ref").strip(), signed))
    if isinstance(value, dict):
        ref = value.get("ref")
        ref_str = _norm_ref_str(ref)
        op = value.get("op", "+")
        off = value.get("offset_s", 0.0)
        if ref_str is None:
            add_err("type-mismatch", field, value, "相对引用字典形态缺少有效 ref")
            return ("bad", None)
        if op not in ("+", "-"):
            add_err("type-mismatch", field, value, "相对引用 op 只允许 \"+\" 或 \"-\"")
            return ("bad", None)
        if isinstance(off, bool) or not isinstance(off, (int, float)):
            add_err("type-mismatch", field, value, "相对引用 offset_s 必须为数值")
            return ("bad", None)
        if not _math.isfinite(float(off)):
            add_err("type-mismatch", field, value, "相对引用 offset_s 必须为有限数值")
            return ("bad", None)
        signed = float(off) if op == "+" else -float(off)
        return ("rel", (ref_str, signed))
    add_err("type-mismatch", field, value,
            "start/end 仅支持 数值秒 / \"<shot_id>±<float>s\" 字符串 / {ref,op,offset_s} 字典")
    return ("bad", None)


# ------------------------------------------------------------------
# 公共 API
# ------------------------------------------------------------------
def attach_contract_version(data):
    """幂等注入 "contract_version": 1 (契约版本权威盖章)。永不抛异常。
    非 dict 原样返回; 已是合法 int 1 则不动 (保持既有键位); 其他值覆盖为 1。"""
    try:
        if isinstance(data, dict):
            cv = data.get("contract_version")
            if not (isinstance(cv, int) and not isinstance(cv, bool)
                    and cv == STORYBOARD_CONTRACT_VERSION):
                data["contract_version"] = STORYBOARD_CONTRACT_VERSION
        return data
    except Exception:
        return data


def parse_storyboard_json(text):
    """宽容解析分镜 JSON 文本 → (data|None, warnings)。复用 pln_llm.json_loads_tolerant
    (围栏/最外层配平/尾逗号/截断抢救), 永不抛异常。"""
    warnings = []
    try:
        from pln_llm import json_loads_tolerant
    except Exception as e:
        return None, ["parse-import-failed: json_loads_tolerant 不可用 (%s)" % type(e).__name__]
    try:
        obj, diag = json_loads_tolerant(text)
    except Exception as e:
        return None, ["parse-exception: json_loads_tolerant 异常 %s" % type(e).__name__]
    if obj is None:
        warnings.append("parse-unparsable: %s" % (diag or "未知原因"))
        return None, warnings
    if diag:
        warnings.append("parse-tolerant-recovered: %s" % diag)
    return obj, warnings


def validate_storyboard(data):
    """分镜契约校验 → {"ok": bool, "errors": [...], "warnings": [...], "normalized": ...}。
    永不抛异常 (内部兜底: 意外异常记 internal-error 并返回)。同输入同输出 (确定性)。"""
    try:
        return _validate_inner(data)
    except Exception as e:  # 兜底安全网: 校验器自身故障不得外溢 (超出 11 码集合的防御位)
        return {
            "ok": False,
            "errors": [{"code": "internal-error", "field": "<root>",
                        "value": type(e).__name__, "message": "校验器内部异常(防御兜底)"}],
            "warnings": [],
            "normalized": None,
        }


def _validate_inner(data):
    errors = []
    warnings = []

    def err(code, field, value, message):
        errors.append({"code": code, "field": field,
                       "value": _trim_value(value), "message": message})

    def warn(code, field, value, message):
        warnings.append({"code": code, "field": field,
                         "value": _trim_value(value), "message": message})

    if not isinstance(data, dict):
        err("type-mismatch", "<root>", type(data).__name__,
            "分镜契约根必须是对象(dict), 实际为 %s" % type(data).__name__)
        return {"ok": False, "errors": errors, "warnings": warnings, "normalized": None}

    # ---- 契约版本头 ----
    if "contract_version" not in data:
        err("missing-contract-version", "contract_version", None,
            "缺少契约版本头 contract_version (attach_contract_version 可注入)")
    else:
        cv = data.get("contract_version")
        if isinstance(cv, bool) or not isinstance(cv, int) or cv != STORYBOARD_CONTRACT_VERSION:
            err("invalid-contract-version", "contract_version", cv,
                "contract_version 必须为整数 %d" % STORYBOARD_CONTRACT_VERSION)

    # ---- 顶层 legacy 重命名 (确定性: 按别名表序迭代, 不依赖输入键序) ----
    src = {}
    for k, v in data.items():
        src[k] = v
    for alias, canon in LEGACY_TOP_ALIASES.items():
        if alias in src:
            if canon in src:
                continue  # canonical 已在: 旧键留给 unknown-field 通道
            src[canon] = src.pop(alias)
            warn("deprecated-field", alias, src[canon],
                 "顶层键 '%s' 为旧键, 已映射至 '%s' (契约 v1)" % (alias, canon))

    # ---- 顶层未知键 → extra (保留值) ----
    top_extra = {}
    for k in sorted(src.keys()):
        if k not in CANON_TOP_KEYS:
            top_extra[k] = src.pop(k)
            warn("unknown-field", k, top_extra[k],
                 "顶层键 '%s' 非契约 v1 键, 值保留于 normalized.extra" % k)

    # ---- 顶层类型检查 ----
    for k, kind in _TOP_TYPED.items():
        if k in src and not _type_ok(src.get(k), kind):
            err("type-mismatch", k, src.get(k),
                "顶层键 '%s' 类型应为 %s, 实际为 %s" % (k, kind, type(src.get(k)).__name__))
    if "分镜表" not in src:
        err("type-mismatch", "分镜表", None, "缺少必备键 '分镜表' (契约 v1)")

    # ---- 分镜表预处理 ----
    shots_raw = src.get("分镜表")
    shots_ok = isinstance(shots_raw, list)
    if shots_ok and len(shots_raw) == 0:
        err("empty-shots", "分镜表", 0, "分镜表为空 (至少需要 1 个镜头)")

    # ---- 每镜: legacy 重命名 / unknown / 类型 / 镜号查重 / 时长 / 表达式分类 ----
    shot_id_map = {}      # str(镜号) → 首次出现下标
    shot_metas = []       # 每镜元数据 (供时间轴轮次解析)
    normalized_shots = []

    if shots_ok:
        for i, raw_shot in enumerate(shots_raw):
            path = "分镜表[%d]" % i
            if not isinstance(raw_shot, dict):
                err("type-mismatch", path, type(raw_shot).__name__,
                    "%s 必须为对象(dict), 实际为 %s" % (path, type(raw_shot).__name__))
                normalized_shots.append(_copy.deepcopy(raw_shot))
                shot_metas.append(None)
                continue
            s = dict(raw_shot)
            # legacy 重命名 (按别名表序, 确定性)
            for alias, canon in LEGACY_SHOT_ALIASES.items():
                if alias in s:
                    if canon in s:
                        continue
                    s[canon] = s.pop(alias)
                    warn("deprecated-field", "%s.%s" % (path, alias), s[canon],
                         "镜头键 '%s' 为旧键, 已映射至 '%s' (契约 v1)" % (alias, canon))
            # unknown → 镜内 extra (排序保序)
            shot_extra = {}
            for k in sorted(s.keys()):
                if k not in CANON_SHOT_KEYS:
                    shot_extra[k] = s.pop(k)
                    warn("unknown-field", "%s.%s" % (path, k), shot_extra[k],
                         "镜头键 '%s' 非契约 v1 键, 值保留于 normalized extra" % k)

            # 类型检查
            for k, kind in _SHOT_TYPED.items():
                if k in s and not _type_ok(s.get(k), kind):
                    err("type-mismatch", "%s.%s" % (path, k), s.get(k),
                         "镜头键 '%s' 类型应为 %s, 实际为 %s" % (k, kind, type(s.get(k)).__name__))

            # 镜号 (缺失/类型错 → missing-shot-id / type-mismatch 已记; 查重用 str 形态)
            sid_raw = s.get("镜号")
            sid_key = None
            if sid_raw is None or (isinstance(sid_raw, str) and not sid_raw.strip()):
                err("missing-shot-id", "%s.镜号" % path, sid_raw,
                    "%s 缺少有效镜号" % path)
            elif _type_ok(sid_raw, "id"):
                sid_key = _norm_ref_str(sid_raw) or str(sid_raw)
                if sid_key in shot_id_map:
                    err("duplicate-shot-id", "%s.镜号" % path, sid_raw,
                        "镜号 %s 与 分镜表[%d] 重复" % (sid_key, shot_id_map[sid_key]))
                else:
                    shot_id_map[sid_key] = i
            # (镜号类型错已由 _SHOT_TYPED 的 id 判定记 type-mismatch, 不再重复报 missing)

            # 时长
            dur_raw = s.get("时长")
            dur = _parse_duration(dur_raw)
            if dur is None:
                err("invalid-duration", "%s.时长" % path, dur_raw,
                    "时长不可解析或非正数 (支持 正数值秒 或 \"3.8s\" 式字符串), 实际为 %r" % (dur_raw,))

            # start/end 表达式分类
            start_expr = _classify_expr(s.get("start"), err, "%s.start" % path)
            end_expr = _classify_expr(s.get("end"), err, "%s.end" % path)

            shot_metas.append({
                "path": path, "dict": s, "extra": shot_extra, "sid": sid_key,
                "duration_s": dur, "start_expr": start_expr, "end_expr": end_expr,
            })

    # ---- 时间轴轮次解析 (无递归, 确定性; ref 锚定被引用镜 end_s) ----
    start_s = [None] * len(shot_metas)
    end_s = [None] * len(shot_metas)
    sdone = [False] * len(shot_metas)
    edone = [False] * len(shot_metas)
    rel_failed = [False] * len(shot_metas)

    def _ref_index(ref_str):
        return shot_id_map.get(ref_str)

    # 未知引用预扫 (一次且仅一次: 全量镜号集合就绪后才能判定) — relative-ref-unknown
    for i, meta in enumerate(shot_metas):
        if meta is None:
            continue
        for side_key, expr in (("start", meta["start_expr"]), ("end", meta["end_expr"])):
            if expr is not None and expr[0] == "rel" and expr[1][0] not in shot_id_map:
                err("relative-ref-unknown", "%s.%s" % (meta["path"], side_key), expr[1][0],
                    "相对引用的镜号 '%s' 不存在于分镜表 (已回退链式时间轴)" % expr[1][0])
                rel_failed[i] = True

    def _chain_start(i):
        if i == 0:
            return 0.0
        if edone[i - 1]:
            return end_s[i - 1]  # 可能为 None (前镜时间轴断裂), 诚实传递
        return None

    def _try_shot(i):
        """尝试推进第 i 镜的 start_s/end_s; 返回是否有进展。"""
        meta = shot_metas[i]
        progressed = False
        # --- start ---
        if not sdone[i]:
            se = meta["start_expr"]
            if se is None:
                cs = _chain_start(i)
                if i == 0 or edone[i - 1]:
                    start_s[i] = _round3(cs)
                    sdone[i] = True
                    progressed = True
            elif se[0] == "abs":
                start_s[i] = _round3(se[1])
                sdone[i] = True
                progressed = True
            elif se[0] == "rel":
                ref, off = se[1]
                ri = _ref_index(ref)
                if ri is None:
                    rel_failed[i] = True  # unknown 已在预扫报错
                elif edone[ri]:
                    if end_s[ri] is None:
                        rel_failed[i] = True  # 锚点 end_s 不可用 → 回退链式
                    else:
                        start_s[i] = _round3(end_s[ri] + off)
                        sdone[i] = True
                        progressed = True
            # ("bad", _) 表达式 → 视同无显式 start (type-mismatch 已记)
            if not sdone[i] and (meta["start_expr"] is None or meta["start_expr"][0] == "bad"
                                 or rel_failed[i]):
                cs = _chain_start(i)
                if i == 0 or edone[i - 1]:
                    start_s[i] = _round3(cs)
                    sdone[i] = True
                    progressed = True
        # --- end (可能消费刚算出的 start_s[i]) ---
        if not edone[i]:
            ee = meta["end_expr"]
            dur = meta["duration_s"]
            if ee is None:
                if sdone[i]:
                    end_s[i] = _round3(start_s[i] + dur) if (dur is not None
                                                             and start_s[i] is not None) else None
                    edone[i] = True
                    progressed = True
            elif ee[0] == "abs":
                end_s[i] = _round3(ee[1])
                edone[i] = True
                progressed = True
            elif ee[0] == "rel":
                ref, off = ee[1]
                ri = _ref_index(ref)
                if ri is None:
                    rel_failed[i] = True
                elif edone[ri]:
                    if end_s[ri] is None:
                        rel_failed[i] = True
                    else:
                        end_s[i] = _round3(end_s[ri] + off)
                        edone[i] = True
                        progressed = True
            if not edone[i] and (meta["end_expr"] is None or meta["end_expr"][0] == "bad"
                                 or rel_failed[i]):
                if sdone[i]:
                    end_s[i] = _round3(start_s[i] + dur) if (dur is not None
                                                             and start_s[i] is not None) else None
                    edone[i] = True
                    progressed = True
        return progressed

    # 轮次推进 (最多 n+1 轮; 每轮按下标序扫描, 全无进展则停)
    n = len(shot_metas)
    for _round in range(n + 1):
        any_progress = False
        for i in range(n):
            if shot_metas[i] is not None:
                if _try_shot(i):
                    any_progress = True
        if not any_progress:
            break

    # 仍未解析 → 相对引用环 (一次汇总报错) → rel 标失败后链式回退
    unresolved = [i for i in range(n)
                  if shot_metas[i] is not None and not (sdone[i] and edone[i])]
    if unresolved:
        ids_txt = ", ".join("分镜表[%d](镜号 %s)" % (i, shot_metas[i]["sid"] or "?")
                            for i in unresolved)
        err("relative-ref-cycle", "分镜表[].start/end", ids_txt,
            "相对引用互相依赖形成环, 涉及: %s (已回退链式时间轴)" % ids_txt)
        for i in unresolved:
            rel_failed[i] = True
        # 链式回退: 反复下标序扫描直到稳定 (有界)
        for _sweep in range(n + 1):
            changed = False
            for i in range(n):
                if shot_metas[i] is not None and _try_shot(i):
                    changed = True
            if not changed:
                break

    # ---- normalized 每镜 (canonical 定序 → 表达式键 → derived → extra) ----
    if shots_ok:
        for i, meta in enumerate(shot_metas):
            if meta is None:
                continue
            s = meta["dict"]
            ns = {}
            for k in CANON_SHOT_KEYS:
                if k in ("start", "end"):
                    continue
                if k in s:
                    ns[k] = _copy.deepcopy(s[k])
            for k in ("start", "end"):
                if k in s:
                    ns[k] = _copy.deepcopy(s[k])
            ns["duration_s"] = meta["duration_s"]
            ns["start_s"] = start_s[i]
            ns["end_s"] = end_s[i]
            if meta["extra"]:
                ns["extra"] = dict((k, _copy.deepcopy(meta["extra"][k]))
                                   for k in sorted(meta["extra"].keys()))
            normalized_shots.append(ns)

    # ---- normalized 顶层 (canonical 定序 + extra) ----
    normalized = {"contract_version": STORYBOARD_CONTRACT_VERSION}
    for k in CANON_TOP_KEYS[1:]:
        if k == "分镜表" and shots_ok:
            normalized[k] = normalized_shots
        elif k in src:
            normalized[k] = _copy.deepcopy(src[k])
    if top_extra:
        normalized["extra"] = dict((k, _copy.deepcopy(top_extra[k]))
                                   for k in sorted(top_extra.keys()))

    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings,
            "normalized": normalized}


def self_check():
    """最小样例自检 (doctor 第 9 类消费): 合法最小分镜应 ok 且零 errors。"""
    sample = {
        "contract_version": STORYBOARD_CONTRACT_VERSION,
        "分镜数": 2,
        "总时长秒": 5.0,
        "导演": "自检", "情绪": "孤独", "画面模式": "电影工作室",
        "分镜表": [
            {"镜号": 1, "时长": "3.0s", "景别": "全景"},
            {"镜号": 2, "时长": 2.0, "start": {"ref": 1, "op": "+", "offset_s": 0}},
        ],
    }
    try:
        rep = validate_storyboard(sample)
        n0 = rep["normalized"]["分镜表"][0]
        return bool(rep["ok"]) and not rep["errors"] and n0["start_s"] == 0.0 \
            and n0["end_s"] == 3.0 and rep["normalized"]["分镜表"][1]["start_s"] == 3.0
    except Exception:
        return False
