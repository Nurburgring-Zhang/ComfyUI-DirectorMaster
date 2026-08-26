# -*- coding: utf-8 -*-
"""
aggregator/node_base.py — ComfyUI 节点公共基类 + 双轨逻辑
===========================================================
每个节点继承 DirectorNodeBase 获得:
  1. ComfyUI 合规 (INPUT_TYPES classmethod 检测, IS_CHANGED 自动生成)
  2. AI 双轨: 有 LLM 走 generate_native, 无 LLM 走 built-in template
  3. 核心数据包解析 + AI 配置继承
  4. 600 导演模糊匹配

V8.0 彻底重建版 — 无 legacy 依赖.
"""

import os as _os, sys as _sys, json as _json, hashlib as _hashlib, re as _re

# === ComfyUI 加载兼容 ===
if __name__ != "__main__":
    _HERE = _os.path.dirname(_os.path.abspath(__file__))
    _PARENT = _os.path.dirname(_HERE)
    if _PARENT not in _sys.path:
        _sys.path.insert(0, _PARENT)
    if _HERE not in _sys.path:
        _sys.path.insert(0, _HERE)


# ============================================================
# 核心数据包解析
# ============================================================
def parse_core_pack(text):
    if not text or not isinstance(text, str):
        return {}
    try:
        data = _json.loads(text.strip())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def resolve_dropdown(v, default, options=None, seed=None):
    """V12.6 v8: 下拉框值解析 + 随机选择.
    v: 原始值 (用户下拉)
    default: fallback 默认值 (当 v 是 "无(默认)" 或 空)
    options: 可选列表 (当 v 是 "🎲 随机" 时, 从 options 随机选一个)
    seed: 随机种子 (None 用系统时间)
    返回: 解析后的值
    """
    if v is None or v == "" or v == "无(默认)":
        return default
    if v == "🎲 随机" and options:
        import random as _r
        real_opts = [o for o in options if o not in ("无(默认)", "🎲 随机", "")]
        if real_opts:
            # V14.2: seed 参数真实生效 (此前声明未用) — seed=None 时系统随机, 给定 seed 时可复现
            _rng = _r.Random(seed) if seed is not None else _r
            return _rng.choice(real_opts)
        return default
    return v


def parse_multi_select(text, default=None):
    """V13.2: 多选/演变序列解析器.

    把用户输入的多值字符串拆成有序列表。支持分隔符:
      逗号(,/，)、顿号(、)、分号(;/；)、加号(+)、箭头(→/->/=>)、竖线(|)、换行。
    箭头分隔保留"演变"语义(顺序即叙事推进顺序)。
    返回: 去空白、去空项、去重(保序)后的 list; 无内容返回 [default] 或 []。

    例:
      parse_multi_select("压抑→爆发→释然")   → ["压抑","爆发","释然"]
      parse_multi_select("忧郁, 温暖,希望")   → ["忧郁","温暖","希望"]
      parse_multi_select("")                  → []  (或 [default])
    """
    if not text or not isinstance(text, str):
        return [default] if default else []
    # 统一把箭头/加号/分号/顿号/竖线/换行 归一成英文逗号
    norm = text
    for sep in ("→", "->", "=>", "——>", "+", "、", ";", "；", "|", "\n", "，"):
        norm = norm.replace(sep, ",")
    parts = [p.strip() for p in norm.split(",")]
    out = []
    for p in parts:
        p = p.strip()
        if not p or p in ("无(默认)", "无", "默认"):
            continue
        if p not in out:
            out.append(p)
    if not out and default:
        return [default]
    return out


def arc_value_at(arc, progress):
    """V13.2: 按叙事进度(0..1)从演变弧取当前值.
    arc: 值列表; progress: 0..1 (场次/镜头在全片的位置)。
    单值弧恒定返回该值; 空弧返回 ""。
    """
    if not arc:
        return ""
    if len(arc) == 1:
        return arc[0]
    try:
        p = max(0.0, min(1.0, float(progress)))
    except Exception:
        p = 0.0
    idx = int(p * (len(arc) - 1) + 0.5)
    return arc[max(0, min(len(arc) - 1, idx))]


def resolve_ai_config(kwargs, core):
    """节点自身 AI 输入优先, 留空则继承 Core 核心数据包.

    中文槽名: AI接口地址 / AI密钥 / AI模型名.
    """
    url = (kwargs.get("AI接口地址") or "").strip()
    if not url and core:
        url = (core.get("_ai_api_url") or "").strip()
    key = (kwargs.get("AI密钥") or "").strip()
    if not key and core:
        key = (core.get("_ai_api_key") or "").strip()
    model = (kwargs.get("AI模型名") or "").strip()
    if not model and core:
        model = (core.get("_ai_api_model") or "").strip()
    return url, key, model


def get_director_profile_text(director):
    """从 600 导演库提取该导演的 12 维档案文本 (镜头/光/节奏/色彩/表演/构图/声音/情绪/物件/年代/5维标签).

    用于把导演风格知识注入节点输出, 实现"世界顶级导演能力".
    """
    if not director:
        return ""
    try:
        from director_data_unified import get_director_profile, get_director
        prof = get_director_profile(director) or get_director(director)
        if not prof or not isinstance(prof, dict):
            return ""
        lines = []
        for k, v in prof.items():
            if k == "5维标签":
                continue
            lines.append(f"  {k}: {v}")
        if prof.get("5维标签"):
            lines.append(f"  5维标签: {prof['5维标签']}")
        return "\n".join(lines)
    except Exception:
        return ""


def match_director_fuzzy(text):
    """600 导演模糊匹配."""
    if not text or not isinstance(text, str):
        return "王家卫"
    text = text.strip()
    if not text:
        return "王家卫"
    try:
        from director_data_unified import DIRECTOR_PROFILES_ALL
    except Exception:
        return text
    if text in DIRECTOR_PROFILES_ALL:
        return text
    candidates = []
    for k in DIRECTOR_PROFILES_ALL:
        if text in k or k in text:
            candidates.append(k)
    if candidates:
        return min(candidates, key=len)
    t = text.replace(" ", "").lower()
    for k in DIRECTOR_PROFILES_ALL:
        if t in k.replace(" ", "").lower() or k.replace(" ", "").lower() in t:
            return k
    return text


# ============================================================
# 公共基类
# ============================================================
class DirectorNodeBase:
    """所有 DirectorMaster 节点的公共基类.

    子类只需定义:
      - NODE_TYPE: "核心"/"剧本"/"创意氛围"/"美术指导"/"声音设计"/"画面"/"终极汇总"
      - 覆盖 INPUT_TYPES, RETURN_TYPES, RETURN_NAMES, build()
    """

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        for k in ("AI接口地址",):
            if kwargs.get(k):
                return float("nan")
        try:
            payload = {k: v for k, v in kwargs.items()
                       if isinstance(v, (str, int, float, bool, type(None)))}
            return _hashlib.md5(_json.dumps(
                payload, sort_keys=True, default=str, ensure_ascii=False
            ).encode()).hexdigest()
        except Exception:
            return float("nan")

    def _director_block(self, director):
        """生成导演风格锚定块 (12维档案). 注入节点输出实现世界级导演能力."""
        txt = get_director_profile_text(director)
        if not txt:
            return ""
        return (f"\n\n═══════════════════════════════════════════════════════════\n"
                f"【导演风格锚定 · {director} — 600导演库12维档案】\n"
                f"═══════════════════════════════════════════════════════════\n{txt}")

    def _apply_anti_ai(self, text, kwargs, core):
        """V14.2: 启用反AI规则 真实生效 (修复 Vibe/Art/Sound/Cinematic 声明未消费)。
        优先级: 节点输入 启用反AI规则 > 核心数据包._启用反AI规则 > True。
        (节点开关优先, 兑现 tooltip "此处可单独覆盖"; 此前核心包恒胜导致节点开关成摆设。)
        开启时用 anti_ai_vocab.clean_anti_ai_text 清除 masterpiece/8K/HDR 等 AI 套话。
        """
        flag = kwargs.get("启用反AI规则", None)
        if flag is None:
            flag = core.get("_启用反AI规则", True) if core else True
        if not flag or not text:
            return text
        try:
            from anti_ai_vocab import clean_anti_ai_text
            return clean_anti_ai_text(text) or text
        except Exception:
            return text

    def _ensure_ai_output(self, template, context, api_url, api_key, model_name):
        """双轨: 有 LLM → 原生生成; 无 LLM → 返回模板."""
        if not api_url or not template:
            return template
        try:
            from aggregator.llm_engine import generate_native
            node_type = context.get("node_type", getattr(self.__class__, "NODE_TYPE", "核心"))
            mode = context.get("mode", "")
            director = context.get("director", "王家卫")
            rich = {
                "scene": context.get("scene", ""),
                "mood": context.get("mood", ""),
                "intent": context.get("intent", ""),
            }
            result = generate_native(node_type, mode, director, rich,
                                     api_url, api_key, model_name, template)
            return result if result and len(result) > 200 else template
        except Exception as _e:
            # V13.5: 不再静默吞异常 — 写 stderr 使 AI 轨故障可观测
            import sys as _sb
            _sb.stderr.write(f"[DirectorMaster] AI轨异常→模板: {type(_e).__name__}: {str(_e)[:120]}\n")
            return template


# ============================================================
# 公共工具
# ============================================================
def _comfyui_safe_import():
    """确保 ComfyUI 加载时 sys.path 正确."""
    _HERE2 = _os.path.dirname(_os.path.abspath(__file__))
    _PARENT2 = _os.path.dirname(_HERE2)
    if _PARENT2 not in _sys.path:
        _sys.path.insert(0, _PARENT2)
    if _HERE2 not in _sys.path:
        _sys.path.insert(0, _HERE2)