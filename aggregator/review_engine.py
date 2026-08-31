# -*- coding: utf-8 -*-
"""
aggregator/review_engine.py — DirectorMaster 独立审查引擎 (V16.7.0-MERGED 批次3 D6)
====================================================================
设计: design_batch3.md §6 D6 · owner: 批次3 WaveB B1
冻结接口消费 (只 import 不改):
  · aggregator.pipeline_checkpoint.CheckpointStore (A3, D4)
  · pln_llm.call_ai_ex / json_loads_tolerant (A1, D1)
  · aggregator.storyboard_contract.validate_storyboard (批次2, 分镜契约 v1)
  · knowledge_base.quality_precedents.list_precedents (B2, D7 — 并行实现中, 缺位诚实降级)

独立审查 = "干净上下文" 的第二双眼睛:
  · 审查调用不携带任何生成历史/模板/上游链路上下文 — 只依据 (被审产物, brief,
    对比基准) 三样输入做判断;
  · 13 项清单核对 (C01-C13), 分阶段执行: 完整性 → 一致性 → 覆盖;
  · 输出编号化报告 (R-001 起, 每条附镜头号/字段证据) + "无法验证" 显式标注
    (缺输入不猜测, 绝不编造结论);
  · 确定性轨必须真实可用: 结构自检 (分镜契约 v1 诊断码映射) + 规则核对
    (镜数/时长覆盖/字段完整/景别运镜多样性/场景锚定/重复手法/元语言/空洞词);
  · LLM 轨可选 (全量审查 + AI 端点): call_ai_ex 单次语义审查, 端点缺席或失败
    自动落回确定性轨并在报告头诚实标注, 不可解析的 LLM 输出丢弃不上报;
  · 多阶段断点续跑: CheckpointStore(pipeline_id="review", input_hash=阶段输入
    摘要) — 已完成阶段从磁盘阶段产物跳过, 输入变化自动失效重算。

审查模式 (节点下拉恰好 3 个, 无默认/自动/随机伪选项):
  快速结构审查 — completeness 阶段 (结构自检: 输入/契约/镜数/字段/时长有效)
  全量审查     — completeness + consistency + coverage (13 项全核对) + 判例自检
                 + 可选 LLM 语义轨
  对比分镜     — completeness + 对比基准核对 (被审产物 vs 分镜JSON: 镜数对齐/
                 逐镜时长/锚点覆盖; 基准缺失 → 无法验证显式标注)

13 项清单 (C01-C13; stage 归属见 _ITEMS):
  C01 输入完整性  C02 分镜契约    C03 镜数一致  C04 字段完整
  C05 时长有效    C06 时长覆盖    C07 景别多样性 C08 运镜多样性
  C09 场景锚定    C10 模式一致性  C11 重复手法   C12 元语言泄漏  C13 空洞词
对比基准附加项 (仅对比分镜模式, 不占 13 项清单):
  X01 镜数对齐    X02 逐镜时长对齐  X03 锚点覆盖

零第三方依赖 (仅 stdlib), Python ≥3.8 语法兼容。引擎主入口对产物/brief/baseline
的一切畸形输入永不抛异常 (诚实降级为发现/无法验证); 仅编程性误用 (非法 mode /
非 str 产物) 抛 ValueError — 诚实 API 契约; 节点层另兜底成错误报告。
"""
import json as _json
import os as _os
import re as _re
import sys as _sys
import hashlib as _hashlib

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
for _p in (_HERE, _PARENT):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config

# ------------------------------------------------------------------
# 常量: 审查模式 / 阶段 / 13 项清单
# ------------------------------------------------------------------
PIPELINE_ID = "review"          # CheckpointStore pipeline_id (设计 §6 钉死)
CHECKPOINT_SCHEMA = 1

MODE_QUICK = "快速结构审查"
MODE_FULL = "全量审查"
MODE_COMPARE = "对比分镜"
REVIEW_MODES = (MODE_QUICK, MODE_FULL, MODE_COMPARE)

MODE_STAGES = {
    MODE_QUICK: ("completeness",),
    MODE_FULL: ("completeness", "consistency", "coverage"),
    MODE_COMPARE: ("completeness", "compare"),
}
STAGE_NAMES = {"completeness": "完整性", "consistency": "一致性",
               "coverage": "覆盖", "compare": "对比基准"}

# 每镜必填核心字段 (C04; 缺一记 FAIL, 证据=镜N·字段)
REQUIRED_SHOT_FIELDS = ("镜号", "景别", "运镜", "时长", "画面焦点",
                        "声音", "转场", "叙事目的", "首帧描述", "AIGC提示词")

# 景别/运镜塌缩门槛 (依据 README 口径: 景别阶梯 ≥3 种 / 镜头语法唯一性)
MIN_SIZES = 3
MIN_MOVES = 2
ANCHOR_HIT_RATIO = 0.60     # 场景锚定命中率门槛 (README 维度 H 同口径)
DURATION_TOLERANCE = 0.01   # Σ时长 vs 总时长秒 容差 ±1% (README T10 同口径)

# 元语言/占位泄漏词 (低误报保守集; "上一镜/前一镜" 等参考绑定措辞为合法生产语言, 不入集)
META_LEAK_TERMS = ("分镜表", "镜头清单", "待补充", "此处应", "（占位）", "(占位)",
                   "示例文本", "TODO", "Lorem", "作为AI", "作为一个AI")

# 空洞词罐头集 (与去AI味口径一致的最小保守集; 逐字命中即报)
HOLLOW_TERMS = ("震撼", "史诗感拉满", "电影感拉满", "高级感拉满", "大片既视感",
                "8K超清", "16K超清", "极致氛围", "氛围感拉满", "张力拉满")

_ITEM_KEYWORDS = {
    "C01": ["空输入", "缺失"], "C02": ["契约", "结构", "缺失"], "C03": ["镜数"],
    "C04": ["字段", "缺失"], "C05": ["时长", "漂移"], "C06": ["时长", "漂移", "覆盖"],
    "C07": ["景别", "构图"], "C08": ["运镜", "构图"], "C09": ["场景", "脱节", "锚"],
    "C10": ["模式", "一致"], "C11": ["重复", "构图", "运镜"], "C12": ["元语言", "占位", "泄漏"],
    "C13": ["空洞", "套话"],
    "X01": ["镜数"], "X02": ["时长"], "X03": ["场景", "锚"],
}

SEVERITIES = ("FAIL", "WARN", "INFO")


def _ITEMS():
    """13 项清单注册表: [(id, 名称, stage)] — 模块内唯一事实源。"""
    return [
        ("C01", "输入完整性", "completeness"),
        ("C02", "分镜契约", "completeness"),
        ("C03", "镜数一致", "completeness"),
        ("C04", "字段完整", "completeness"),
        ("C05", "时长有效", "completeness"),
        ("C06", "时长覆盖", "coverage"),
        ("C07", "景别多样性", "coverage"),
        ("C08", "运镜多样性", "coverage"),
        ("C09", "场景锚定", "coverage"),
        ("C10", "模式一致性", "consistency"),
        ("C11", "重复手法", "consistency"),
        ("C12", "元语言泄漏", "consistency"),
        ("C13", "空洞词", "coverage"),
    ]


ITEM_IDS = tuple(i[0] for i in _ITEMS())
ITEM_NAME = dict((i[0], i[1]) for i in _ITEMS())
ITEM_STAGE = dict((i[0], i[2]) for i in _ITEMS())


# ------------------------------------------------------------------
# 小工具
# ------------------------------------------------------------------
def _sha256(text):
    return _hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _s(v):
    """防御性字符串化 (None → None; 其余 str(v) 去首尾空白; 空 → None)。"""
    if v is None:
        return None
    try:
        out = str(v).strip()
    except Exception:
        return None
    return out or None


def _num(v):
    """防御性数值化 (bool 不算数值; 支持 "3.8s" 式字符串)。"""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = _re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*(?:s|秒)?\s*$", v, _re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


def _truncate(text, limit):
    if text is None:
        return ""
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "…[已截断, 原文 %d 字符]" % len(text)


def _default_store_dir():
    """ComfyUI 输出目录优先 (与 v15_nodes 同法), 否则包根 output/。"""
    try:
        import folder_paths
        d = folder_paths.get_output_directory()
        if d:
            return d
    except Exception:
        pass
    return _os.path.join(_PARENT, "output")


def _default_checkpoint_dir():
    return _os.path.join(_default_store_dir(), "_review_checkpoints")


def _classify_artifact(text):
    """产物分类: "empty" / "storyboard" / "json-other" / "text"。

    JSON 判定: json.loads 优先, 失败落 pln_llm.json_loads_tolerant (宽容围栏/
    尾逗号/尾部噪声 — 只为判定产物形态, 不改写内容)。"""
    if not text or not text.strip():
        return "empty", None
    data = None
    try:
        data = _json.loads(text.strip())
    except Exception:
        try:
            import pln_llm as _pln
            data, _ = _pln.json_loads_tolerant(text)
        except Exception:
            data = None
    if isinstance(data, dict):
        if isinstance(data.get("分镜表"), list):
            return "storyboard", data
        return "json-other", data
    if isinstance(data, list):
        return "json-other", data
    return "text", None


def _shots_of(data):
    if isinstance(data, dict):
        sh = data.get("分镜表")
        if isinstance(sh, list):
            return sh
    return []


def _contract_report(data):
    """validate_storyboard 包装 (模块缺席/异常 → None, 诚实降级)。"""
    try:
        from aggregator.storyboard_contract import validate_storyboard
        rep = validate_storyboard(data)
        if isinstance(rep, dict) and "errors" in rep:
            return rep
    except Exception:
        return None
    return None


def _brief_digest(brief):
    if not isinstance(brief, dict) or not brief:
        return None
    director = _s(brief.get("_导演名")) or _s(brief.get("_导演风格"))
    mood = _s(brief.get("_情绪基调"))
    scene = _s(brief.get("_场景描述"))
    duration = brief.get("_成片时长")
    return {"导演": director, "情绪": mood, "场景": scene,
            "成片时长": duration if _num(duration) is not None else _s(duration)}


def _anchor_terms(scene):
    """从 brief 场景句提取锚词: 标点分句 → 功能字再切分 (的/了/着/在/与/和/及/被/把)
    → 每片段 ≥2 字; 长片段 (≥4 字) 追加前 3 字块提高召回。上限 12 个。"""
    if not scene:
        return []
    raw = []
    for seg in _re.split(r"[，。；、！？,;.!?\s（）()\[\]【】]+", str(scene)):
        seg = seg.strip()
        if not seg:
            continue
        for part in _re.split(r"[的了着在和与及被把上下里]+", seg):
            part = part.strip()
            if len(part) >= 2 and part not in raw:
                raw.append(part)
            if len(part) >= 4 and part[:3] not in raw:
                raw.append(part[:3])
        if len(raw) >= 12:
            break
    return raw[:12]


def _load_precedents():
    """判例库加载 (B2 接口钉死: list_precedents → [{id, rule, self_check, ...}])。

    import 失败 / 异常 / 结构不符 / 空 → None (审查报告自检段诚实标注
    "判例库未就绪" 并跳过, 绝不崩、绝不编造判例引用)。"""
    try:
        from knowledge_base.quality_precedents import list_precedents
        ps = list_precedents()
        if isinstance(ps, list) and ps and all(isinstance(p, dict) for p in ps):
            return ps
    except Exception:
        pass
    return None


def _scan_spots(kind, shots, artifact_text):
    """C12 扫描点: [(shot标签|None, 字段名, 文本)]。"""
    spots = []
    if kind == "storyboard":
        for i, sh in enumerate(shots):
            if not isinstance(sh, dict):
                continue
            sid = _s(sh.get("镜号")) or ("#%d" % (i + 1))
            for f in ("AIGC提示词", "首帧描述", "叙事目的", "画面焦点"):
                v = _s(sh.get(f))
                if v:
                    spots.append(("镜%s" % sid, f, v))
    elif kind == "text":
        spots.append((None, "全文", artifact_text))
    return spots


# ------------------------------------------------------------------
# 阶段实现 — 每个函数返回 (findings, cannot_verify)
# finding: {item, severity, shot, field, message, source}
# cannot_verify: {item, reason}
# ------------------------------------------------------------------
def _stage_completeness(ctx):
    findings, cannot = [], []
    kind = ctx["kind"]
    if kind == "empty":
        findings.append({"item": "C01", "severity": "FAIL", "shot": None, "field": "被审产物",
                         "message": "被审产物为空输入 — 无从审查 (缺输入不猜测)",
                         "source": "deterministic"})
        for iid in ("C02", "C03", "C04", "C05"):
            cannot.append({"item": iid, "reason": "产物为空, 结构类核对不适用"})
        return findings, cannot
    if kind == "text":
        findings.append({"item": "C01", "severity": "INFO", "shot": None, "field": "全文",
                         "message": "产物为纯文本（非分镜 JSON），共 %d 字符" % len(ctx["artifact_text"]),
                         "source": "deterministic"})
        for iid in ("C02", "C03", "C04", "C05"):
            cannot.append({"item": iid,
                           "reason": "产物为纯文本（无分镜 JSON 结构），结构自检项无法验证（缺输入不猜测）"})
        return findings, cannot

    data = ctx["data"]
    shots = _shots_of(data)
    findings.append({"item": "C01", "severity": "INFO", "shot": None, "field": "被审产物",
                     "message": "分镜 JSON 可解析（%d 镜）" % len(shots),
                     "source": "deterministic"})

    # C02 分镜契约: 契约 v1 校验器诊断码映射 (storyboard_contract.validate_storyboard)
    rep = ctx.get("contract")
    if rep is None:
        rep = _contract_report(data)
        ctx["contract"] = rep
    if rep is None:
        cannot.append({"item": "C02",
                       "reason": "分镜契约校验器不可用（aggregator.storyboard_contract 导入失败）"})
    else:
        hard_codes = {"empty-shots", "missing-shot-id", "duplicate-shot-id",
                      "relative-ref-unknown", "relative-ref-cycle"}
        for e in rep.get("errors", []) or []:
            code = str(e.get("code", "?"))
            if code == "invalid-duration":
                continue  # C05 通道单独映射, 避免双报
            iid = "C02"
            sev = "FAIL" if code in hard_codes else "WARN"
            findings.append({"item": iid, "severity": sev,
                             "shot": _s(e.get("field")), "field": code,
                             "message": "契约诊断 %s: %s" % (code, _s(e.get("message")) or ""),
                             "source": "deterministic"})
        for w in rep.get("warnings", []) or []:
            findings.append({"item": "C02", "severity": "INFO",
                             "shot": _s(w.get("field")), "field": str(w.get("code", "?")),
                             "message": "契约警告 %s: %s" % (w.get("code"), _s(w.get("message")) or ""),
                             "source": "deterministic"})
        if not (rep.get("errors") or []):
            findings.append({"item": "C02", "severity": "INFO", "shot": None,
                             "field": "contract_version",
                             "message": "分镜契约 v1 校验通过（0 错误）",
                             "source": "deterministic"})

    # C03 镜数一致: 声明 分镜数 vs 分镜表实际长度
    declared = data.get("分镜数")
    if declared is None:
        cannot.append({"item": "C03", "reason": "产物未声明『分镜数』顶层键，镜数一致性无法核对（不猜测）"})
    elif isinstance(declared, bool) or not isinstance(declared, int):
        findings.append({"item": "C03", "severity": "FAIL", "shot": None, "field": "分镜数",
                         "message": "『分镜数』类型应为整数, 实际 %s (%s)" % (
                             type(declared).__name__, _truncate(declared, 40)),
                         "source": "deterministic"})
    elif declared != len(shots):
        findings.append({"item": "C03", "severity": "FAIL", "shot": None, "field": "分镜数",
                         "message": "声明分镜数=%d 与 分镜表实际 %d 镜不符" % (declared, len(shots)),
                         "source": "deterministic"})

    # C04 字段完整: 每镜 REQUIRED_SHOT_FIELDS 在场且非空
    if not shots:
        findings.append({"item": "C04", "severity": "FAIL", "shot": None, "field": "分镜表",
                         "message": "分镜表为空 — 每镜字段完整性无从谈起", "source": "deterministic"})
    else:
        missing = []
        for i, sh in enumerate(shots):
            if not isinstance(sh, dict):
                continue
            sid = _s(sh.get("镜号")) or ("#%d" % (i + 1))
            for f in REQUIRED_SHOT_FIELDS:
                v = sh.get(f)
                if v is None or (isinstance(v, str) and not v.strip()):
                    missing.append((sid, f))
        if missing and len(missing) <= 12:
            for sid, f in missing:
                findings.append({"item": "C04", "severity": "FAIL", "shot": "镜%s" % sid,
                                 "field": f, "message": "缺少必填核心字段『%s』" % f,
                                 "source": "deterministic"})
        elif missing:
            detail = "; ".join("镜%s.%s" % (sid, f) for sid, f in missing[:10])
            findings.append({"item": "C04", "severity": "FAIL", "shot": None,
                             "field": "分镜表",
                             "message": "共 %d 处核心字段缺失（聚合上报, 前 10 处: %s…）" % (
                                 len(missing), detail),
                             "source": "deterministic"})

    # C05 时长有效: 优先契约 invalid-duration 诊断 (单一诊断通道), 校验器缺席时手动兜底
    dur_errs = []
    if rep is not None:
        dur_errs = [e for e in (rep.get("errors") or [])
                    if str(e.get("code")) == "invalid-duration"]
        if not dur_errs:
            findings.append({"item": "C05", "severity": "INFO", "shot": None, "field": "时长",
                             "message": "全部 %d 镜时长可解析且 >0（契约校验器判定）" % len(shots),
                             "source": "deterministic"})
    else:
        bad = []
        for i, sh in enumerate(shots):
            if not isinstance(sh, dict):
                continue
            d = _num(sh.get("时长"))
            if d is None or d <= 0:
                bad.append(_s(sh.get("镜号")) or ("#%d" % (i + 1)))
        if bad:
            findings.append({"item": "C05", "severity": "FAIL", "shot": None, "field": "时长",
                             "message": "镜 %s 时长不可解析或 ≤0（手动兜底扫描, 契约校验器不可用）" % ", ".join(bad[:10]),
                             "source": "deterministic"})
        else:
            findings.append({"item": "C05", "severity": "INFO", "shot": None, "field": "时长",
                             "message": "全部 %d 镜时长可解析且 >0（手动兜底扫描）" % len(shots),
                             "source": "deterministic"})
    for e in dur_errs:
        findings.append({"item": "C05", "severity": "FAIL",
                         "shot": _s(e.get("field")), "field": "时长",
                         "message": _s(e.get("message")) or "时长不可解析或非正数（契约诊断 invalid-duration）",
                         "source": "deterministic"})
    return findings, cannot


def _stage_consistency(ctx):
    findings, cannot = [], []
    kind = ctx["kind"]
    data = ctx["data"]
    shots = _shots_of(data)
    brief = ctx["brief"]

    # C10 模式一致性 — brief 导演/情绪 vs 产物顶层声明
    bd = _brief_digest(brief)
    if not bd or (not bd.get("导演") and not bd.get("情绪")):
        cannot.append({"item": "C10",
                       "reason": "未提供核心数据包 brief（或 brief 无 导演/情绪 声明），模式一致性无法验证（缺输入不猜测）"})
    else:
        top_director = _s(data.get("导演")) if isinstance(data, dict) else None
        top_mood = _s(data.get("情绪")) if isinstance(data, dict) else None
        compared = False
        if bd.get("导演") and top_director:
            compared = True
            b_dir = _re.sub(r"^\[[^\]]*\]\s*", "", bd["导演"]).strip()
            if b_dir and b_dir not in top_director and top_director not in bd["导演"]:
                findings.append({"item": "C10", "severity": "WARN", "shot": None,
                                 "field": "导演",
                                 "message": "brief 导演『%s』与产物顶层『导演=%s』不一致" % (
                                     bd["导演"], _truncate(top_director, 30)),
                                 "source": "deterministic"})
        if bd.get("情绪") and top_mood:
            compared = True
            if bd["情绪"] not in top_mood and top_mood not in bd["情绪"]:
                findings.append({"item": "C10", "severity": "WARN", "shot": None,
                                 "field": "情绪",
                                 "message": "brief 情绪『%s』与产物顶层『情绪=%s』不一致" % (
                                     bd["情绪"], _truncate(top_mood, 30)),
                                 "source": "deterministic"})
        if not compared:
            cannot.append({"item": "C10",
                           "reason": "产物缺少『导演』『情绪』顶层声明，模式一致性无法比对（缺输入不猜测）"})

    # C11 重复手法 — 相邻镜同(景别,运镜)连用 ≥2 镜 = 返工提示
    if kind != "storyboard":
        cannot.append({"item": "C11",
                       "reason": "产物无分镜 JSON 结构, 逐镜手法重复无法验证（缺输入不猜测）"})
    elif not shots:
        cannot.append({"item": "C11", "reason": "分镜表为空, 手法重复无法统计"})
    else:
        runs, cur = [], []
        for i, sh in enumerate(shots):
            if not isinstance(sh, dict):
                if len(cur) >= 2:
                    runs.append(cur)
                cur = []
                continue
            pair = (_s(sh.get("景别")), _s(sh.get("运镜")))
            if not pair[0] or not pair[1]:
                if len(cur) >= 2:
                    runs.append(cur)
                cur = []
                continue
            if cur and cur[-1][1] == pair:
                cur.append((i, pair))
            else:
                if len(cur) >= 2:
                    runs.append(cur)
                cur = [(i, pair)]
        if len(cur) >= 2:
            runs.append(cur)
        if runs:
            for run in runs:
                i0, pair0 = run[0]
                i1, _ = run[-1]
                sid0 = _s(shots[i0].get("镜号")) or ("#%d" % (i0 + 1))
                sid1 = _s(shots[i1].get("镜号")) or ("#%d" % (i1 + 1))
                findings.append({"item": "C11", "severity": "WARN",
                                 "shot": "镜%s-镜%s" % (sid0, sid1),
                                 "field": "景别+运镜",
                                 "message": "相邻 %d 镜连用同一手法组合 (景别=%s, 运镜=%s) — 建议轮换" % (
                                     len(run), pair0[0], pair0[1]),
                                 "source": "deterministic"})
        else:
            findings.append({"item": "C11", "severity": "INFO", "shot": None, "field": "景别+运镜",
                             "message": "无相邻镜手法连用（%d 镜扫描）" % len(shots),
                             "source": "deterministic"})

    # C12 元语言泄漏 — 提示词字段中的生成过程语言/占位词
    spots = _scan_spots(kind, shots, ctx["artifact_text"])
    if kind not in ("storyboard", "text") or not spots:
        cannot.append({"item": "C12",
                       "reason": "产物无可扫描的自然语言字段（非分镜结构或字段全空），元语言泄漏无法验证（缺输入不猜测）"})
    else:
        hits = []
        for spot_shot, spot_field, text in spots:
            for term in META_LEAK_TERMS:
                if term in text:
                    hits.append((spot_shot, spot_field, term))
        if hits:
            if len(hits) <= 10:
                for spot_shot, spot_field, term in hits:
                    findings.append({"item": "C12", "severity": "WARN", "shot": spot_shot,
                                     "field": spot_field,
                                     "message": "元语言/占位词『%s』泄漏进产物文本" % term,
                                     "source": "deterministic"})
            else:
                findings.append({"item": "C12", "severity": "WARN", "shot": None, "field": "全文",
                                 "message": "元语言/占位词命中 %d 处（聚合上报）" % len(hits),
                                 "source": "deterministic"})
        else:
            findings.append({"item": "C12", "severity": "INFO", "shot": None, "field": "全文",
                             "message": "元语言/占位词扫描通过（%d 个保守词, 0 命中）" % len(META_LEAK_TERMS),
                             "source": "deterministic"})
    return findings, cannot


def _stage_coverage(ctx):
    findings, cannot = [], []
    kind = ctx["kind"]
    data = ctx["data"]
    shots = _shots_of(data)
    brief = ctx["brief"]

    # C06 时长覆盖 — Σ每镜时长 vs 声明总时长 (±1%)
    if kind != "storyboard":
        cannot.append({"item": "C06",
                       "reason": "产物非分镜 JSON（无分镜结构），Σ时长 vs 总时长秒 无法核对（缺输入不猜测）"})
    else:
        declared = _num(data.get("总时长秒"))
        if declared is None:
            cannot.append({"item": "C06",
                           "reason": "产物未声明数值型『总时长秒』顶层键，时长覆盖无法核对（不猜测）"})
        else:
            durs = []
            rep = ctx.get("contract")
            norm_shots = None
            if rep and isinstance(rep.get("normalized"), dict):
                ns = rep["normalized"].get("分镜表")
                if isinstance(ns, list):
                    norm_shots = ns
            if norm_shots is not None:
                for ns in norm_shots:
                    if isinstance(ns, dict) and isinstance(ns.get("duration_s"), (int, float)) \
                            and not isinstance(ns.get("duration_s"), bool):
                        durs.append(float(ns["duration_s"]))
            else:
                for sh in shots:
                    if isinstance(sh, dict):
                        d = _num(sh.get("时长"))
                        if d is not None and d > 0:
                            durs.append(d)
            if not durs:
                findings.append({"item": "C06", "severity": "FAIL", "shot": None,
                                 "field": "时长",
                                 "message": "0 镜时长可计入 — Σ时长无从覆盖总时长 %.2fs" % declared,
                                 "source": "deterministic"})
            else:
                total = sum(durs)
                dev = abs(total - declared) / declared if declared else 1.0
                if dev > DURATION_TOLERANCE:
                    findings.append({"item": "C06", "severity": "FAIL", "shot": None,
                                     "field": "总时长秒",
                                     "message": "Σ每镜时长 %.2fs vs 声明总时长 %.2fs（偏差 %.1f%%, 门槛 ±%.0f%%）" % (
                                         total, declared, dev * 100, DURATION_TOLERANCE * 100),
                                     "source": "deterministic"})
                else:
                    findings.append({"item": "C06", "severity": "INFO", "shot": None,
                                     "field": "总时长秒",
                                     "message": "时长覆盖达标: Σ=%.2fs / 声明=%.2fs（偏差 %.2f%%）" % (
                                         total, declared, dev * 100),
                                     "source": "deterministic"})

    # C07 景别多样性 / C08 运镜多样性
    if kind != "storyboard":
        cannot.append({"item": "C07", "reason": "产物无分镜 JSON 结构, 景别多样性无法验证（缺输入不猜测）"})
        cannot.append({"item": "C08", "reason": "产物无分镜 JSON 结构, 运镜多样性无法验证（缺输入不猜测）"})
    elif not shots:
        findings.append({"item": "C07", "severity": "FAIL", "shot": None, "field": "分镜表",
                         "message": "分镜表为空 — 景别/运镜多样性无从统计", "source": "deterministic"})
    else:
        sizes, moves = [], []
        for sh in shots:
            if not isinstance(sh, dict):
                continue
            sv, mv = _s(sh.get("景别")), _s(sh.get("运镜"))
            if sv and sv not in sizes:
                sizes.append(sv)
            if mv and mv not in moves:
                moves.append(mv)
        if len(sizes) < MIN_SIZES:
            findings.append({"item": "C07", "severity": "WARN", "shot": None, "field": "景别",
                             "message": "景别塌缩: 仅 %d 种 (%s), 门槛 ≥%d 种 — 建议按阶段带兜底轮换" % (
                                 len(sizes), "/".join(sizes[:6]) or "无", MIN_SIZES),
                             "source": "deterministic"})
        else:
            findings.append({"item": "C07", "severity": "INFO", "shot": None, "field": "景别",
                             "message": "景别 %d 种达标 (%s)" % (len(sizes), "/".join(sizes[:6])),
                             "source": "deterministic"})
        if len(moves) < MIN_MOVES:
            findings.append({"item": "C08", "severity": "WARN", "shot": None, "field": "运镜",
                             "message": "运镜单一: 仅 %d 种 (%s), 门槛 ≥%d 种" % (
                                 len(moves), "/".join(moves[:6]) or "无", MIN_MOVES),
                             "source": "deterministic"})
        else:
            findings.append({"item": "C08", "severity": "INFO", "shot": None, "field": "运镜",
                             "message": "运镜 %d 种达标 (%s)" % (len(moves), "/".join(moves[:6])),
                             "source": "deterministic"})

    # C09 场景锚定 — brief 场景锚词在镜头提示词中的命中率 ≥60%
    bd = _brief_digest(brief)
    scene = (bd or {}).get("场景") or ""
    terms = _anchor_terms(scene)
    if not terms:
        cannot.append({"item": "C09",
                       "reason": "未提供核心数据包 brief（或 brief 无 ≥2 字场景片段），场景锚点无从提取（缺输入不猜测）"})
    elif kind != "storyboard":
        cannot.append({"item": "C09",
                       "reason": "产物无分镜 JSON 结构, 逐镜场景锚定率无法计算（缺输入不猜测）"})
    else:
        hit, miss = 0, []
        for sh in shots:
            if not isinstance(sh, dict):
                continue
            sid = _s(sh.get("镜号")) or "?"
            blob = " ".join(filter(None, [_s(sh.get("AIGC提示词")), _s(sh.get("首帧描述")),
                                          _s(sh.get("画面焦点")), _s(sh.get("氛围"))]))
            if blob and any(t in blob for t in terms):
                hit += 1
            else:
                miss.append("镜%s" % sid)
        total = hit + len(miss)
        if total == 0:
            cannot.append({"item": "C09", "reason": "分镜表无可用镜头, 场景锚定率无法计算"})
        else:
            ratio = hit / float(total)
            if ratio < ANCHOR_HIT_RATIO:
                findings.append({"item": "C09", "severity": "FAIL", "shot": None,
                                 "field": "AIGC提示词",
                                 "message": "场景锚定率 %.0f%% < %.0f%% 门槛（锚词: %s; 命中 %d/%d; 未命中: %s）" % (
                                     ratio * 100, ANCHOR_HIT_RATIO * 100,
                                     ", ".join(terms[:4]), hit, total,
                                     ", ".join(miss[:8]) + ("…" if len(miss) > 8 else "")),
                                 "source": "deterministic"})
            else:
                findings.append({"item": "C09", "severity": "INFO", "shot": None,
                                 "field": "AIGC提示词",
                                 "message": "场景锚定达标: 命中 %d/%d 镜 (%.0f%%, 门槛 %.0f%%)" % (
                                     hit, total, ratio * 100, ANCHOR_HIT_RATIO * 100),
                                 "source": "deterministic"})

    # C13 空洞词 — anti_ai_vocab 正则层复用 (缺模块/未命中则保守词表兜底)
    if kind not in ("storyboard", "text"):
        cannot.append({"item": "C13",
                       "reason": "产物无可扫描的自然语言文本, 空洞词无法验证（缺输入不猜测）"})
    else:
        scan_text = ctx["artifact_text"]
        vocab_hits = None
        if scan_text:
            try:
                from anti_ai_vocab import count_regex_hits
                n, hits = count_regex_hits(scan_text)
                if isinstance(n, int) and n > 0:
                    vocab_hits = (n, hits)
            except Exception:
                vocab_hits = None
        if vocab_hits:
            n, hits = vocab_hits
            sample = ""
            if isinstance(hits, (list, tuple)) and hits:
                sample = "/".join(str(x)[:12] for x in list(hits)[:4])
            findings.append({"item": "C13", "severity": "WARN", "shot": None, "field": "全文",
                             "message": "反AI词表命中 %d 处%s（anti_ai_vocab 正则层）" % (
                                 n, (": " + sample) if sample else ""),
                             "source": "deterministic"})
            if kind == "storyboard":
                h = _hollow_scan(shots, None)
                if h:
                    findings.append({"item": "C13", "severity": "WARN", "shot": h[0],
                                     "field": h[1],
                                     "message": "空洞词『%s』命中（镜级证据）" % h[2],
                                     "source": "deterministic"})
        else:
            h = _hollow_scan(shots if kind == "storyboard" else None, ctx["artifact_text"])
            if h:
                findings.append({"item": "C13", "severity": "WARN", "shot": h[0], "field": h[1],
                                 "message": "空洞词『%s』命中（保守词表兜底）" % h[2],
                                 "source": "deterministic"})
            else:
                findings.append({"item": "C13", "severity": "INFO", "shot": None, "field": "全文",
                                 "message": "空洞词扫描通过（保守词表 %d 词 + anti_ai_vocab 正则层, 0 命中）" % len(HOLLOW_TERMS),
                                 "source": "deterministic"})
    return findings, cannot


def _hollow_scan(shots, text):
    """保守空洞词扫描: storyboard → 逐镜 (镜级证据); text → 全文。返回 (shot|None, field, term)。"""
    if shots:
        for sh in shots:
            if not isinstance(sh, dict):
                continue
            sid = _s(sh.get("镜号")) or "?"
            for f in ("AIGC提示词", "首帧描述", "氛围"):
                v = _s(sh.get(f))
                if v:
                    for term in HOLLOW_TERMS:
                        if term in v:
                            return ("镜%s" % sid, f, term)
        return None
    if text:
        for term in HOLLOW_TERMS:
            if term in text:
                return (None, "全文", term)
    return None


def _stage_compare(ctx):
    """对比基准阶段 (对比分镜模式): 被审产物 vs 分镜JSON 基准。

    X01 镜数对齐 / X02 逐镜时长对齐 / X03 锚点覆盖。基准缺失/不可解析 → 无法验证。"""
    findings, cannot = [], []
    kind = ctx["kind"]
    base_text = ctx["storyboard_text"] or ""
    if not base_text.strip():
        cannot.append({"item": "X01",
                       "reason": "未提供对比基准『分镜JSON』输入 — 对比分镜无法执行（缺输入不猜测）"})
        return findings, cannot
    bkind, bdata = _classify_artifact(base_text)
    if bkind != "storyboard":
        cannot.append({"item": "X01",
                       "reason": "对比基准不可解析为分镜 JSON（形态: %s）— 对比分镜无法执行（缺输入不猜测）" % bkind})
        return findings, cannot
    base_shots = _shots_of(bdata)

    # X01 镜数对齐
    a_shots = _shots_of(ctx["data"])
    a_n, b_n = len(a_shots), len(base_shots)
    if a_n != b_n:
        findings.append({"item": "X01", "severity": "FAIL", "shot": None, "field": "分镜数",
                         "message": "被审产物 %d 镜 vs 基准 %d 镜 — 镜数失配" % (a_n, b_n),
                         "source": "deterministic"})
    else:
        findings.append({"item": "X01", "severity": "INFO", "shot": None, "field": "分镜数",
                         "message": "镜数对齐: %d 镜" % a_n, "source": "deterministic"})

    # X02 逐镜时长对齐 (产物非分镜 JSON → 诚实降级无法验证)
    if kind == "storyboard":
        drift = []
        for i in range(min(a_n, b_n)):
            ad = _num(a_shots[i].get("时长")) if isinstance(a_shots[i], dict) else None
            bd = _num(base_shots[i].get("时长")) if isinstance(base_shots[i], dict) else None
            if ad is None or bd is None:
                continue
            if abs(ad - bd) > 0.5:
                sid = _s(a_shots[i].get("镜号")) or ("#%d" % (i + 1))
                drift.append(("镜%s" % sid, bd, ad))
        if drift:
            for sid, bd, ad in drift[:8]:
                findings.append({"item": "X02", "severity": "WARN", "shot": sid, "field": "时长",
                                 "message": "镜级时长漂移: 基准 %.2fs → 产物 %.2fs (>0.5s)" % (bd, ad),
                                 "source": "deterministic"})
            if len(drift) > 8:
                findings.append({"item": "X02", "severity": "WARN", "shot": None, "field": "时长",
                                 "message": "另有 %d 镜时长漂移（聚合上报）" % (len(drift) - 8),
                                 "source": "deterministic"})
        else:
            findings.append({"item": "X02", "severity": "INFO", "shot": None, "field": "时长",
                             "message": "逐镜时长对齐（|Δ|≤0.5s）", "source": "deterministic"})
    else:
        cannot.append({"item": "X02",
                       "reason": "被审产物非分镜 JSON, 逐镜时长对齐无法执行（缺输入不猜测）"})

    # X03 锚点覆盖: 基准每镜镜号在产物文本中的出现
    text_blob = ctx["artifact_text"] or ""
    missing_ids = []
    for sh in base_shots:
        if not isinstance(sh, dict):
            continue
        sid = _s(sh.get("镜号"))
        if sid and str(sid) not in text_blob:
            missing_ids.append(str(sid))
    if missing_ids:
        findings.append({"item": "X03", "severity": "WARN", "shot": None, "field": "镜号",
                         "message": "基准镜号未在产物文本出现 %d/%d（前几个: %s）— 逐镜对应存疑" % (
                             len(missing_ids), len(base_shots), ", ".join(missing_ids[:8])),
                         "source": "deterministic"})
    else:
        findings.append({"item": "X03", "severity": "INFO", "shot": None, "field": "镜号",
                         "message": "基准 %d 镜镜号全部在产物文本中出现" % len(base_shots),
                         "source": "deterministic"})
    return findings, cannot


_STAGE_FN = {"completeness": _stage_completeness, "consistency": _stage_consistency,
             "coverage": _stage_coverage, "compare": _stage_compare}


# ------------------------------------------------------------------
# CheckpointStore 断点续跑
# ------------------------------------------------------------------
def _get_store(checkpoint_dir=None, checkpoint_store=None):
    if checkpoint_store is not None:
        return checkpoint_store
    from aggregator.pipeline_checkpoint import CheckpointStore
    return CheckpointStore(checkpoint_dir or _default_checkpoint_dir())


def _stage_hashes(artifact_text, brief, storyboard_text):
    """各阶段输入摘要 (不含审查模式 — 跨模式复用已完成阶段; 含 schema 版本盐)。"""
    brief_json = ""
    if isinstance(brief, dict) and brief:
        try:
            brief_json = _json.dumps(brief, sort_keys=True, ensure_ascii=False)
        except Exception:
            brief_json = str(brief)
    return {
        "completeness": _sha256("v%d|completeness|%s" % (CHECKPOINT_SCHEMA, artifact_text)),
        "consistency": _sha256("v%d|consistency|%s|%s" % (CHECKPOINT_SCHEMA, artifact_text, brief_json)),
        "coverage": _sha256("v%d|coverage|%s|%s" % (CHECKPOINT_SCHEMA, artifact_text, brief_json)),
        "compare": _sha256("v%d|compare|%s|%s" % (CHECKPOINT_SCHEMA, artifact_text, storyboard_text or "")),
    }


def _artifact_ref(input_hash, stage):
    return "review_%s_%s.json" % (input_hash[:16], stage)


def _load_stage_artifact(root_dir, ref, stage):
    """读阶段产物; 缺失/损坏/schema 不符 → None (诚实重算, 不带病跳过)。"""
    if not ref:
        return None
    path = _os.path.join(root_dir, ref)
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = _json.load(f)
    except Exception:
        return None
    if (isinstance(d, dict) and d.get("schema") == CHECKPOINT_SCHEMA
            and d.get("stage") == stage and isinstance(d.get("findings"), list)
            and isinstance(d.get("cannot_verify"), list)):
        return d["findings"], d["cannot_verify"]
    return None


def _write_stage_artifact(root_dir, ref, stage, input_hash, findings, cannot):
    path = _os.path.join(root_dir, ref)
    try:
        _os.makedirs(root_dir, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            _json.dump({"schema": CHECKPOINT_SCHEMA, "stage": stage,
                        "input_hash": input_hash,
                        "findings": findings, "cannot_verify": cannot},
                       f, ensure_ascii=False, sort_keys=True)
        _os.replace(tmp, path)
        return True
    except Exception as e:
        _sys.stderr.write("[DirectorMaster] 审查阶段产物写盘失败 (审查继续, 无检查点): %r\n" % (e,))
        return False


# ------------------------------------------------------------------
# LLM 语义轨 (可选; call_ai_ex 单次调用, 干净上下文)
# ------------------------------------------------------------------
_LLM_SYSTEM = (
    "你是独立产物审查员, 对给定创作产物做语义审查。你没有参与该产物的生成, 不了解其"
    "生成过程与任何历史上下文 — 只依据本次给出的材料判断。审查重点: 叙事连贯、镜头意图、"
    "情绪传达、场景贴合、语言质量; 不要重复『结构检查已给发现』清单中的问题。"
    "输出严格 JSON (不要任何其他文本): "
    '{"findings": [{"item": "问题域(≤8字)", "severity": "FAIL|WARN|INFO", '
    '"shot": "镜N 或 null", "field": "字段名 或 null", "message": "一句话中文结论"}], '
    '"cannot_verify": [{"item": "问题域", "reason": "为什么无法验证"}]}'
)


def _llm_semantic_review(artifact_text, brief, det_findings, api_url, api_key, api_model):
    """返回 (llm_findings:list|None, note:str)。失败/不可解析 → (None, 诚实原因)。"""
    try:
        import pln_llm as _pln
    except Exception as e:
        return None, "pln_llm 不可用: %r" % (e,)
    bd = _brief_digest(brief)
    brief_lines = []
    if bd:
        for k in ("导演", "情绪", "成片时长"):
            if bd.get(k) is not None:
                brief_lines.append("%s=%s" % (k, _truncate(bd[k], 60)))
        if bd.get("场景"):
            brief_lines.append("场景=%s" % _truncate(bd["场景"], 200))
    det_lines = ["%s [%s] %s" % (f.get("item"), f.get("severity"),
                                 _truncate(f.get("message"), 80))
                 for f in det_findings if f.get("severity") in ("FAIL", "WARN")]
    user = ("[brief]\n%s\n\n[被审产物]\n%s\n\n[结构检查已给发现 (勿重复)]\n%s\n\n"
            "[任务]\n按系统约定输出严格 JSON 审查发现。" % (
                "\n".join(brief_lines) or "(未提供)",
                _truncate(artifact_text, 6000),
                "\n".join(det_lines) or "(无)"))
    try:
        text, err, meta = _pln.call_ai_ex(api_url, api_key, api_model or "dm-reviewer",
                                          _LLM_SYSTEM, user, 0.2, 1600, timeout=120)
    except Exception as e:
        return None, "LLM 调用异常: %r" % (e,)
    if err or not text:
        return None, "LLM 轨不可用: %s" % _truncate(err or "空响应", 120)
    data, _diag = _pln.json_loads_tolerant(text)
    if not isinstance(data, (dict, list)):
        return None, "LLM 返回不可解析为 JSON, 语义审查结果丢弃（诚实不上报不可解析内容）"
    raw = data.get("findings") if isinstance(data, dict) else data
    if not isinstance(raw, list):
        return None, "LLM 返回缺 findings 数组, 语义审查结果丢弃"
    out = []
    for r in raw[:12]:
        if not isinstance(r, dict):
            continue
        sev = str(r.get("severity", "WARN")).upper()
        if sev not in SEVERITIES:
            sev = "WARN"
        out.append({"item": _truncate(_s(r.get("item")) or "LLM语义", 16),
                    "severity": sev, "shot": _truncate(_s(r.get("shot")), 16),
                    "field": _truncate(_s(r.get("field")), 24),
                    "message": _truncate(_s(r.get("message")) or "(无说明)", 300),
                    "source": "llm"})
    return out, "LLM 语义轨完成 (%s): %d 条发现" % (
        _truncate(api_model or "dm-reviewer", 40), len(out))


# ------------------------------------------------------------------
# 报告渲染 + 主入口
# ------------------------------------------------------------------
def _evidence(f):
    parts = []
    if f.get("shot"):
        parts.append(str(f["shot"]))
    if f.get("field"):
        parts.append("字段=%s" % f["field"])
    return "·".join(parts) if parts else "全文"


def _render_report(r):
    L = []
    L.append("=" * 64)
    L.append("DirectorMaster 独立审查报告 (干净上下文, 与生成历史隔离)")
    L.append("=" * 64)
    L.append("审查模式: %s    审查轨: %s" % (r["mode"], r["track"]))
    L.append("被审产物: %s" % r["artifact_kind_text"])
    L.append("brief: %s" % r["brief_text"])
    L.append("-" * 64)
    findings = r["findings"]
    if findings:
        for f in findings:
            L.append("%s [%s] %s %s — %s (证据: %s)" % (
                f["id"], f["severity"], f["item"], ITEM_NAME.get(f["item"], ""),
                f["message"], _evidence(f)))
    else:
        L.append("（无编号发现）")
    L.append("-" * 64)
    cv = r["cannot_verify"]
    if cv:
        L.append("无法验证 (%d 项 — 缺输入不猜测):" % len(cv))
        for c in cv:
            L.append("  - %s %s — %s" % (c["item"], ITEM_NAME.get(c["item"], "对比基准"), c["reason"]))
    else:
        L.append("无法验证: 0 项（13 项清单全部可判）")
    L.append("-" * 64)
    L.append(r["precedent_text"])
    L.append("-" * 64)
    s = r["summary"]
    L.append("13 项清单核对: 通过 %d / 有发现 %d (清单级 FAIL %d·WARN %d) / 无法验证 %d / 本模式不涉及 %d" % (
        s["pass"], s["find_items"], s["fail_items"], s["warn_items"], s["cannot"], s["not_in_scope"]))
    L.append("编号发现统计: R 系列 %d 条 (FAIL %d / WARN %d / INFO %d)" % (
        s["findings_total"], s["fail_findings"], s["warn_findings"], s["info"]))
    L.append("结论: %s" % ("不通过 (存在 FAIL 级发现)" if s["fail_findings"] else "通过 (无 FAIL 级发现)"))
    L.append("检查点: pipeline=%s, %s @ %s" % (
        PIPELINE_ID, r["checkpoint_text"], r.get("checkpoint_dir") or "-"))
    L.append("=" * 64)
    return "\n".join(L)


def review_artifacts(artifact_text, brief=None, mode=MODE_FULL,
                     storyboard_text="", api_url="", api_key="", api_model="",
                     checkpoint_dir=None, checkpoint_store=None,
                     checkpoint_enabled=True):
    """独立审查主入口 (design_batch3.md §6 D6)。

    参数:
        artifact_text: 被审产物 (分镜 JSON / 其他 JSON / 纯文本)。
        brief: brief 上下文 — 通常传 Core 核心数据包 dict (parse_core_pack 结果);
               None/空 → 场景锚定/模式一致性等 brief 依赖项进入『无法验证』。
        mode: REVIEW_MODES 之一 (快速结构审查/全量审查/对比分镜); 非法值 ValueError。
        storyboard_text: 对比分镜模式的基准分镜 JSON 文本 (其他模式可空)。
        api_url/api_key/api_model: LLM 语义轨端点 (仅全量审查消费; 缺席自动走确定性轨)。
        checkpoint_dir/checkpoint_store: CheckpointStore 落盘目录或注入实例 (测试用)。
        checkpoint_enabled: False 时跳过检查点 (全程重算, 不落盘)。

    返回 dict: ok/mode/track/findings/cannot_verify/report/summary/stages/
    precedents/llm/meta — 全部可 JSON 序列化。"""
    if mode not in REVIEW_MODES:
        raise ValueError("review_artifacts: mode 必须是 %s 之一, 实际 %r" % (list(REVIEW_MODES), mode))
    if not isinstance(artifact_text, str):
        raise ValueError("review_artifacts: artifact_text 必须是 str, 实际 %s"
                         % type(artifact_text).__name__)

    kind, data = _classify_artifact(artifact_text)
    ctx = {"artifact_text": artifact_text, "kind": kind, "data": data,
           "brief": brief if isinstance(brief, dict) and brief else None,
           "storyboard_text": storyboard_text or ""}
    if kind == "storyboard":
        ctx["contract"] = _contract_report(data)

    stages_in_mode = MODE_STAGES[mode]
    hashes = _stage_hashes(artifact_text, ctx["brief"], ctx["storyboard_text"])

    # ---- 多阶段执行 (CheckpointStore 断点续跑) ----
    store = None
    checkpoint_root = "-"
    store_error = None
    if checkpoint_enabled:
        try:
            store = _get_store(checkpoint_dir, checkpoint_store)
            checkpoint_root = store.root_dir
        except Exception as e:
            store_error = repr(e)
            store = None
    stages_meta = {}
    all_findings, all_cannot = [], []
    for stage in stages_in_mode:
        h = hashes[stage]
        ref = _artifact_ref(h, stage)
        skipped, loaded = False, None
        if store is not None:
            try:
                if store.done(PIPELINE_ID, stage, h):
                    loaded = _load_stage_artifact(store.root_dir, ref, stage)
                    skipped = loaded is not None
            except Exception as e:
                store_error = store_error or repr(e)
                loaded, skipped = None, False
        if skipped:
            f_cv = loaded
        else:
            f_cv = _STAGE_FN[stage](ctx)
            if store is not None:
                try:
                    _write_stage_artifact(store.root_dir, ref, stage, h, f_cv[0], f_cv[1])
                    store.mark_done(PIPELINE_ID, stage, h, artifact_ref=ref)
                except Exception as e:
                    store_error = store_error or repr(e)
        stages_meta[stage] = {
            "status": "skipped" if skipped else "computed",
            "input_hash": h, "artifact_ref": ref if store is not None else None,
            "findings": len(f_cv[0]), "cannot_verify": len(f_cv[1]),
        }
        all_findings.extend(f_cv[0])
        all_cannot.extend(f_cv[1])

    # ---- LLM 语义轨 (仅全量审查; 端点缺席/失败自动落回确定性轨) ----
    llm_info = {"used": False, "note": "", "error": None}
    if mode == MODE_FULL:
        if (api_url or "").strip():
            llm_findings, note = _llm_semantic_review(
                artifact_text, ctx["brief"], all_findings,
                (api_url or "").strip(), (api_key or "").strip(), (api_model or "").strip())
            llm_info["note"] = note
            if llm_findings is not None:
                llm_info["used"] = True
                all_findings.extend(llm_findings)
            else:
                llm_info["error"] = note
        else:
            llm_info["note"] = "未配置 AI 端点 — LLM 语义审查不可用, 端点缺席自动走确定性轨"

    # ---- 编号 (R-001 起; 阶段序 → LLM 尾部, 确定性) ----
    for i, f in enumerate(all_findings, 1):
        f["id"] = "R-%03d" % i

    # ---- 13 项清单状态核算 ----
    cv_items = set(c["item"] for c in all_cannot)
    item_status = {}
    for iid, _name, stage in _ITEMS():
        if stage not in stages_in_mode:
            item_status[iid] = "not_in_scope"
        elif iid in cv_items:
            item_status[iid] = "cannot_verify"
        elif any(f["item"] == iid and f["severity"] == "FAIL" for f in all_findings):
            item_status[iid] = "fail"
        elif any(f["item"] == iid and f["severity"] == "WARN" for f in all_findings):
            item_status[iid] = "warn"
        else:
            item_status[iid] = "pass"

    n_fail = sum(1 for f in all_findings if f["severity"] == "FAIL")
    n_warn = sum(1 for f in all_findings if f["severity"] == "WARN")
    n_info = sum(1 for f in all_findings if f["severity"] == "INFO")
    summary = {
        "pass": sum(1 for v in item_status.values() if v == "pass"),
        "find_items": sum(1 for v in item_status.values() if v in ("fail", "warn")),
        "fail_items": sum(1 for v in item_status.values() if v == "fail"),
        "warn_items": sum(1 for v in item_status.values() if v == "warn"),
        "cannot": len(all_cannot),
        "not_in_scope": sum(1 for v in item_status.values() if v == "not_in_scope"),
        "findings_total": len(all_findings),
        "info": n_info,
        "fail_findings": n_fail,
        "warn_findings": n_warn,
    }

    # ---- 判例库自检段 (B2 判例库缺位 → 诚实标注并跳过) ----
    precedents = _load_precedents()
    cited, precedent_text = [], ""
    if precedents is None:
        precedent_text = ("自检判例段: 判例库未就绪（knowledge_base.quality_precedents 不可用或为空）"
                          "— 自检跳过判例对照, 不编造判例引用")
    else:
        for f in all_findings:
            kws = _ITEM_KEYWORDS.get(f["item"], [])
            for p in precedents:
                blob = "%s %s" % (str(p.get("rule", "")), str(p.get("self_check", "")))
                if any(kw in blob for kw in kws) and p.get("id"):
                    cited.append("%s ↔ %s" % (f["id"], str(p["id"])))
        qs = [_s(p.get("self_check")) for p in precedents]
        qs = [q for q in qs if q][:12]
        precedent_text = ("自检判例段: 判例库 %d 条就绪; 判例对照命中 %d 条 (%s); 自检问题清单:\n%s" % (
            len(precedents), len(cited),
            ", ".join(cited[:8]) if cited else "无直接命中",
            "\n".join("  - %s" % q for q in qs) if qs else "  (判例未附自检问题)"))

    # ---- 组装 ----
    kind_text = {
        "empty": "空输入（0 字符）",
        "text": "纯文本（%d 字符, 非分镜 JSON）" % len(artifact_text),
        "json-other": "其他 JSON（非分镜结构）",
        "storyboard": "分镜 JSON（%d 镜, 声明总时长 %s）" % (
            len(_shots_of(data)), _s((data or {}).get("总时长秒")) or "?"),
    }[kind]
    bd = _brief_digest(ctx["brief"])
    if bd:
        brief_text = "[导演]%s [情绪]%s [场景]%s字 [成片时长]%s" % (
            _truncate(bd.get("导演") or "未声明", 24),
            _truncate(bd.get("情绪") or "未声明", 16),
            len(str(bd.get("场景") or "")),
            bd.get("成片时长") if bd.get("成片时长") is not None else "未声明")
    else:
        brief_text = "未提供 — brief 依赖项 (场景锚定/模式一致性) 将以『无法验证』标注"

    if llm_info["used"]:
        track = "确定性轨 + LLM 语义轨"
    elif mode == MODE_FULL and llm_info.get("error"):
        track = "确定性轨（结构自检+规则核对, 无 LLM 语义审查: %s）" % _truncate(llm_info["error"], 60)
    elif mode == MODE_FULL:
        track = "确定性轨（结构自检+规则核对, 无 LLM 语义审查）"
    else:
        track = "确定性轨（结构自检+规则核对）"

    done_steps = sum(1 for v in stages_meta.values() if v["status"] == "skipped")
    if not checkpoint_enabled:
        checkpoint_text = "已禁用 (全程重算, 不落盘)"
    elif store is None:
        checkpoint_text = "不可用 (%s) — 全程重算" % _truncate(store_error or "初始化失败", 60)
    else:
        checkpoint_text = ("本报告 %d/%d 阶段复用磁盘检查点 (其余 %d 阶段现算并落盘)"
                           % (done_steps, len(stages_meta), len(stages_meta) - done_steps))

    result = {
        "ok": n_fail == 0,
        "mode": mode,
        "track": track,
        "artifact_kind": kind,
        "artifact_kind_text": kind_text,
        "brief_text": brief_text,
        "findings": all_findings,
        "cannot_verify": all_cannot,
        "item_status": item_status,
        "summary": summary,
        "stages": stages_meta,
        "precedents": {"ready": precedents is not None,
                       "count": len(precedents) if precedents else 0,
                       "cited": cited},
        "llm": llm_info,
        "checkpoint_text": checkpoint_text,
        "checkpoint_dir": checkpoint_root if checkpoint_enabled else None,
        "precedent_text": precedent_text,
        "meta": {"pipeline_id": PIPELINE_ID,
                 "stage_input_hashes": dict((k, hashes[k]) for k in stages_in_mode),
                 "store_error": store_error},
        "report": "",
    }
    result["report"] = _render_report(result)
    return result


# ------------------------------------------------------------------
# ComfyUI 节点: DirectorMasterReview
# ------------------------------------------------------------------
class DirectorMasterReview(DirectorNodeBase):
    """独立审查节点 (V16.7.0-MERGED 批次3 D6) — 干净上下文 13 项清单核对。

    下拉恰好 3 个审查模式 (无默认/自动/随机伪选项):
      快速结构审查 / 全量审查 / 对比分镜。
    输出: 编号化审查报告 (R-001 起) + 审查 JSON。"""
    NODE_TYPE = "审查"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "被审产物": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 接上游产物 (分镜JSON/剧本/提示词文本) — 审查对象; 空输入将得到诚实的 FAIL 报告"}),
            "审查模式": ([MODE_QUICK, MODE_FULL, MODE_COMPARE], {"default": MODE_QUICK,
                "tooltip": "快速结构审查=结构自检; 全量审查=13项清单+判例自检+可选LLM语义轨; 对比分镜=产物 vs 分镜JSON 逐镜核对"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.核心数据包 — 提供 brief (导演/场景/情绪/时长) 作为审查基准; 缺席时相关项诚实标注无法验证"}),
            "分镜JSON": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "对比分镜模式的基准分镜 (接 Cinematic.分镜JSON); 其他模式可留空"}),
            "AI接口地址": ("STRING", {"default": "",
                "tooltip": "可选 — 全量审查模式的 LLM 语义轨 (OpenAI 兼容端点); 留空走确定性轨"}),
            "AI密钥": ("STRING", {"default": ""}),
            "AI模型名": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("审查报告", "审查JSON")
    FUNCTION = "review_build"
    CATEGORY = "PromptLibrary/聚合/审查"

    def review_build(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        api_url, api_key, api_model = resolve_ai_config(kwargs, core)
        mode = kwargs.get("审查模式", MODE_QUICK)
        if mode not in REVIEW_MODES:
            mode = MODE_QUICK  # 下拉值恒合法; 防御未知值落回首项 (不崩)
        try:
            result = review_artifacts(
                artifact_text=kwargs.get("被审产物", "") or "",
                brief=core if core else None,
                mode=mode,
                storyboard_text=kwargs.get("分镜JSON", "") or "",
                api_url=api_url, api_key=api_key, api_model=api_model,
            )
            return (result["report"], _json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            err_report = ("=" * 64 + "\nDirectorMaster 审查引擎异常 (诚实上报, 不伪造结果)\n"
                          + "=" * 64 + "\n%s: %s\n" % (type(e).__name__, str(e)[:300])
                          + "审查未完成 — 请检查输入; 本节点不产生猜测性结论。\n" + "=" * 64)
            err_meta = _json.dumps({"ok": False,
                                    "engine_error": "%s: %s" % (type(e).__name__, str(e)[:300]),
                                    "mode": mode}, ensure_ascii=False, indent=2)
            return (err_report, err_meta)
