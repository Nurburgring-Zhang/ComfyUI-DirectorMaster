# -*- coding: utf-8 -*-
"""
aggregator/contract_render.py — V16.7 批次3 D2 契约渲染层
==========================================================
把分镜契约 JSON (validate_storyboard 的报告, 或含 contract_version 的原始结构)
确定性渲染为每镜 AIGC 视频模型提示词文本。纯 stdlib, Python ≥3.8, 零第三方依赖。

公共 API:
  render_storyboard_prompts(storyboard_json, model_key=None)
      → {"per_shot": [{"镜号": <原值>, "prompt_text": <7 段文本>}, ...],
         "render_meta": {...}}

七要素固定顺序 (与 aggregator/aigc_prompt_builder 七要素方法论同源):
  1 参考绑定   ← 顶层 AIGC生产模式 → 绑定声明
  2 主体动作   ← 画面焦点 (缺省回退 首帧描述) + 叙事目的 + 情绪
  3 空间       ← 构图 + POV + 时间线 + 线
  4 镜头       ← 景别/角度/焦段/运镜/转场 + duration_s + 时间轴 (start_s-end_s)
  5 视觉       ← 色彩/光影/材质/氛围
  6 音频       ← 音频描述 (缺省回退 声音)
  7 约束       ← 固定负面/一致性块 + 模型侧重指令 + 模型参数后缀

STAGE 教训落地: 结构化字段 → 提示词文本的映射逐字段确定性 —
  每个字段的去向由 FIELD_MAP 登记 (可审计); 缺省渲染为 "未指定" 而非静默丢弃;
  无时间戳/无随机/无环境感知, 同输入两次渲染逐字节一致。

模型侧重视图 (model_key, 内置小表):
  SEEDANCE_25 — 多参考位/秒级时间戳锚/音画同录; 参数后缀实时只读引用
                master_director_data.SEEDANCE_25_CAPABILITIES (数字取自能力表, 不复制内容)
  WAN_30      — 中文提示词友好/简洁动作/强美学 (内置侧重视图)
  GENERIC     — 通用兜底; 模型建议只读引用 aggregator.aigc_prompt_builder.MODEL_ADVICE["默认"]
  未知键 → 诚实 ValueError (消息列出已知键)。

坏输入诚实报错 (绝不抛裸 KeyError/TypeError):
  非 dict / 缺 contract_version 且非 validate 报告 / 不支持的契约版本 /
  缺失或空 '分镜表' / 镜非 dict / 缺有效镜号 → ValueError (带下标与实际类型)。
"""
import math as _math

RENDER_VERSION = 1

# 七要素固定顺序 (渲染段顺序, 不可调; per spec 设计 §2)
ELEMENT_ORDER = ("参考绑定", "主体动作", "空间", "镜头", "视觉", "音频", "约束")

# 已知模型键: 两个真实键 + 通用兜底
MODEL_KEYS = ("SEEDANCE_25", "WAN_30", "GENERIC")

DEFAULT_MODEL_KEY = "GENERIC"

# 字段去向登记表 (STAGE 教训: 结构化字段→提示词文本逐字段确定性映射, 供审计)
FIELD_MAP = {
    "参考绑定": {"top": ("AIGC生产模式",), "shot": ()},
    "主体动作": {"top": (), "shot": ("画面焦点", "首帧描述", "叙事目的", "情绪")},
    "空间": {"top": (), "shot": ("构图", "POV", "时间线", "线")},
    "镜头": {"top": (), "shot": ("景别", "角度", "焦段", "运镜", "转场",
                                  "duration_s", "start_s", "end_s")},
    "视觉": {"top": (), "shot": ("色彩", "光影", "材质", "氛围")},
    "音频": {"top": (), "shot": ("音频描述", "声音")},
    "约束": {"top": (), "shot": ()},  # 固定负面/一致性块 + 模型侧重指令 + 模型参数后缀
}

# 参考绑定声明 (顶层 AIGC生产模式 → 绑定句; 与 aigc_prompt_builder 生产模式语义对齐)
_BINDING_LINES = {
    "文生视频": "无参考绑定, 以提示词完整描述画面主体与场景。",
    "首帧生视频": "以给定首帧为第一帧, 只描述首帧之后的运动与演变, 不重复首帧内容。",
    "首尾帧生视频": "以首尾帧为边界, 只描述两帧之间的运动轨迹与过渡, 保持首尾一致。",
    "多参考图生视频": "角色/场景/道具外观由参考图锁定, 提示词聚焦动作、运镜与情节推进。",
    "参考视频生视频": "保留参考视频的运动节奏与剪辑节奏, 替换风格与内容。",
}
_BINDING_UNDECLARED = "生产模式未声明, 按文生视频处理 (无参考绑定)。"

# 约束固定块 (跨模型不变; 一致性 + 负面排除)
_CONSTRAINT_BASE = ("无字幕/无水印/无logo/画面中不出现文字; "
                    "角色外观与服装跨镜一致, 与相邻镜头衔接连续。")

_ANCHOR_UNSET = "未指定"


def _err(msg):
    """诚实报错: 所有坏输入统一 ValueError, 带渲染层前缀。"""
    raise ValueError("[contract_render] %s" % msg)


# ------------------------------------------------------------------
# 只读引用既有数据池 (不复制内容)
# ------------------------------------------------------------------
def _seedance_capabilities():
    """只读引用 master_director_data.SEEDANCE_25_CAPABILITIES → (version, core_upgrades)。
    引用失败/结构意外 → 诚实降级为 ("", {}), 参数后缀回退保守默认; 不抛异常。"""
    try:
        from master_director_data import SEEDANCE_25_CAPABILITIES as _CAPS
    except Exception:
        return "", {}
    if not isinstance(_CAPS, dict):
        return "", {}
    core = _CAPS.get("core_upgrades")
    if not isinstance(core, dict):
        core = {}
    ver = _CAPS.get("version")
    return (ver if isinstance(ver, str) else ""), core


def _generic_advice():
    """GENERIC 模型建议 — 只读引用 aigc_prompt_builder.MODEL_ADVICE["默认"], 不复制内容。"""
    try:
        try:
            from aggregator.aigc_prompt_builder import MODEL_ADVICE
        except Exception:
            from aigc_prompt_builder import MODEL_ADVICE
    except Exception:
        return ""
    if isinstance(MODEL_ADVICE, dict):
        adv = MODEL_ADVICE.get("默认")
        if isinstance(adv, str) and adv.strip():
            return adv.strip()
    return ""


# ------------------------------------------------------------------
# 模型参数后缀 (SEEDANCE 数字实时取自能力表; 其余内置)
# ------------------------------------------------------------------
def _fmt_num(v):
    """确定性数字格式化: 3.8→"3.8", 30.0→"30", 2.5→"2.5"。"""
    return "%g" % float(v)


def _num_ok(v):
    """可用数字判定: int/float 且非 bool 且有限且 > 0。"""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    return _math.isfinite(v) and v > 0


def _seedance_param_line():
    _ver, core = _seedance_capabilities()
    parts = []
    if _num_ok(core.get("max_duration_single_shot")):
        parts.append("单镜时长≤%s 秒" % _fmt_num(core["max_duration_single_shot"]))
    if _num_ok(core.get("max_reference_assets")):
        parts.append("参考资产≤%d 个" % int(core["max_reference_assets"]))
    if _num_ok(core.get("max_prompt_chars")):
        parts.append("提示词≤%d 字" % int(core["max_prompt_chars"]))
    res = core.get("native_resolution")
    if isinstance(res, str) and res.strip():
        parts.append("原生规格 %s" % res.strip())
    if parts:
        return "模型参数: " + ", ".join(parts) + "。"
    return "模型参数: 以 Seedance 2.5 官方能力表为准。"


def _wan_param_line():
    return "模型参数: 中文提示词提交, 单镜建议 5-10 秒, 一镜一事、动作简洁, 美学关键词前置。"


def _generic_param_line():
    adv = _generic_advice()
    if adv:
        return "模型参数: " + adv
    return "模型参数: 建议逐镜生成, 单镜不超过 15 秒, 关键镜头多次抽卡择优。"


def _seedance_timestamp_directive(shot):
    """秒级时间戳锚 — 仅当本镜时间轴可解析时给出 (链断诚实留空, 不编造)。"""
    window = _time_window(shot)
    if window:
        return "秒级时间戳锚: 提示词内以上列时间轴 %s 为秒级时间戳, 逐段对齐动作与情绪节拍。" % window
    return ""


# ------------------------------------------------------------------
# 模型侧重视图 (内置小表; SEEDANCE 数字引用能力表, 表内只存侧重指令)
# ------------------------------------------------------------------
_MODEL_VIEWS = {
    "SEEDANCE_25": {
        "label": "Seedance 2.5",
        "traits": ("多参考资产", "秒级时间戳", "音画同录"),
        "capabilities_source": "master_director_data.SEEDANCE_25_CAPABILITIES",
        "directives": {
            "参考绑定": "多参考位声明: 角色家谱/场景家谱/道具家谱参考位可绑定 (上限见模型参数)。",
            "镜头": _seedance_timestamp_directive,
            "音频": "音画同录: 保留皮肤接触声/脚步/布料摩擦等微声源, 随动作距离自然变化。",
        },
        "param_line": _seedance_param_line,
    },
    "WAN_30": {
        "label": "Wan 3.0",
        "traits": ("中文提示词友好", "简洁动作", "强美学"),
        "capabilities_source": None,
        "directives": {
            "主体动作": "动作指令保持简洁单一, 一镜一事。",
            "视觉": "美学关键词前置: 材质/光影/构图优先, 拒绝形容词堆砌。",
            "约束": "以中文提示词提交, 避免英文空洞词。",
        },
        "param_line": _wan_param_line,
    },
    "GENERIC": {
        "label": "通用",
        "traits": (),
        "capabilities_source": None,
        "directives": {},
        "param_line": _generic_param_line,
    },
}


# ------------------------------------------------------------------
# 内部工具 (全部确定性, 无随机/无时间/无环境感知)
# ------------------------------------------------------------------
def _field_text(src, key):
    """结构化字段 → 干净文本; None/缺省 → ""; 其他类型 str() 兜底 (确定性)。"""
    v = src.get(key)
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, bool):
        return ""
    return str(v).strip()


def _field_num(src, key):
    """数值字段 → float | None (bool/非有限值拒绝)。"""
    v = src.get(key)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not _math.isfinite(v):
        return None
    return float(v)


def _end_period(s):
    """句末补句号 (已有终止标点则不动)。确定性。"""
    if not s:
        return ""
    if s[-1] in "。.！!？?；;":
        return s
    return s + "。"


def _time_window(shot):
    """start_s/end_s → "3.8-6.3s" | "" (任一缺失/链断 → "", 诚实留空)。"""
    a = _field_num(shot, "start_s")
    b = _field_num(shot, "end_s")
    if a is None or b is None:
        return ""
    return "%s-%ss" % (_fmt_num(a), _fmt_num(b))


def _join_seg(header, parts):
    """段头 + 非空子句 (空格连接)。确定性。"""
    return header + " ".join(p for p in parts if p)


def _view_directive(view, element, shot):
    """模型侧重指令: 静态字符串或 callable(shot) → 文本; 视图未声明 → ""。"""
    d = view["directives"].get(element)
    if d is None:
        return ""
    if callable(d):
        return d(shot) or ""
    return d


# ------------------------------------------------------------------
# 七要素段渲染 (顺序由 _render_shot_text 的列表字面量钉死)
# ------------------------------------------------------------------
def _seg_reference_binding(top, directive):
    mode = _field_text(top, "AIGC生产模式")
    line = _BINDING_LINES.get(mode, _BINDING_UNDECLARED)
    return _join_seg("【参考绑定】", [line, directive])


def _seg_subject_action(shot, directive):
    subject = _field_text(shot, "画面焦点") or _field_text(shot, "首帧描述")
    parts = [
        "主体: %s" % (subject or _ANCHOR_UNSET),
        "动作意图: %s" % (_field_text(shot, "叙事目的") or _ANCHOR_UNSET),
        "情绪: %s" % (_field_text(shot, "情绪") or _ANCHOR_UNSET),
    ]
    return _join_seg("【主体动作】", ["; ".join(parts) + "。", directive])


def _seg_space(shot, directive):
    parts = [
        "构图: %s" % (_field_text(shot, "构图") or _ANCHOR_UNSET),
        "视点: %s" % (_field_text(shot, "POV") or _ANCHOR_UNSET),
        "时间线: %s" % (_field_text(shot, "时间线") or "现在"),
        "叙事线: %s" % (_field_text(shot, "线") or _ANCHOR_UNSET),
    ]
    return _join_seg("【空间】", ["; ".join(parts) + "。", directive])


def _seg_camera(shot, directive):
    dur = _field_num(shot, "duration_s")
    dur_txt = ("时长: %ss" % _fmt_num(dur)) if dur is not None else "时长: %s" % _ANCHOR_UNSET
    parts = [
        "景别: %s" % (_field_text(shot, "景别") or _ANCHOR_UNSET),
        "角度: %s" % (_field_text(shot, "角度") or _ANCHOR_UNSET),
        "焦段: %s" % (_field_text(shot, "焦段") or _ANCHOR_UNSET),
        "运镜: %s" % (_field_text(shot, "运镜") or _ANCHOR_UNSET),
        "转场: %s" % (_field_text(shot, "转场") or _ANCHOR_UNSET),
        dur_txt,
    ]
    window = _time_window(shot)
    if window:
        parts.append("时间轴: %s" % window)
    return _join_seg("【镜头】", ["; ".join(parts) + "。", directive])


def _seg_visual(shot, directive):
    parts = [
        "色彩: %s" % (_field_text(shot, "色彩") or _ANCHOR_UNSET),
        "光影: %s" % (_field_text(shot, "光影") or _ANCHOR_UNSET),
        "材质: %s" % (_field_text(shot, "材质") or _ANCHOR_UNSET),
        "氛围: %s" % (_field_text(shot, "氛围") or _ANCHOR_UNSET),
    ]
    return _join_seg("【视觉】", ["; ".join(parts) + "。", directive])


def _seg_audio(shot, directive):
    body = _field_text(shot, "音频描述") or _field_text(shot, "声音")
    return _join_seg("【音频】", [_end_period(body or _ANCHOR_UNSET), directive])


def _seg_constraint(view, directive):
    param = view["param_line"]()
    return _join_seg("【约束】", [_CONSTRAINT_BASE, directive, param])


def _render_shot_text(shot, top, view):
    """单镜 → 7 段提示词文本 (段顺序 = ELEMENT_ORDER, 列表字面量钉死)。"""
    segs = [
        _seg_reference_binding(top, _view_directive(view, "参考绑定", shot)),
        _seg_subject_action(shot, _view_directive(view, "主体动作", shot)),
        _seg_space(shot, _view_directive(view, "空间", shot)),
        _seg_camera(shot, _view_directive(view, "镜头", shot)),
        _seg_visual(shot, _view_directive(view, "视觉", shot)),
        _seg_audio(shot, _view_directive(view, "音频", shot)),
        _seg_constraint(view, _view_directive(view, "约束", shot)),
    ]
    return "\n".join(segs)


# ------------------------------------------------------------------
# 输入解析 (坏输入诚实 ValueError)
# ------------------------------------------------------------------
def _precheck_raw_shots(storyboard_json):
    """raw 形态输入的定位诚实预检: 分镜表非列表 / 镜非 dict → 按原始下标报 ValueError。
    (validate_storyboard 对非 dict 镜先收集后重建, normalized 中位置可能位移;
     渲染层在归一化前按原始结构预检, 保证错误定位与用户输入一致。)"""
    shots_raw = storyboard_json.get("分镜表")
    if not isinstance(shots_raw, list):
        _err("'分镜表' 必须为列表, 实际为 %s" % type(shots_raw).__name__)
    for i, s in enumerate(shots_raw):
        if not isinstance(s, dict):
            _err("分镜表[%d] 必须为对象(dict), 实际为 %s" % (i, type(s).__name__))


def _resolve_contract(storyboard_json):
    """→ (normalized dict, source_form, contract_ok)。两种合法形态:
    1) validate_storyboard 报告 (含 normalized dict) → 直接消费 normalized
    2) 含 contract_version 的原始结构 → validate_storyboard 归一化 (派生 duration_s/start_s/end_s)"""
    if not isinstance(storyboard_json, dict):
        _err("分镜契约输入必须为 dict, 实际为 %s" % type(storyboard_json).__name__)
    if isinstance(storyboard_json.get("normalized"), dict):
        return storyboard_json["normalized"], "validate_report", storyboard_json.get("ok")
    if "contract_version" in storyboard_json:
        _precheck_raw_shots(storyboard_json)
        try:
            try:
                from aggregator.storyboard_contract import validate_storyboard
            except Exception:
                from storyboard_contract import validate_storyboard
        except Exception as _e:
            _err("契约校验器不可用 (%s: %s), 无法归一化原始结构" % (type(_e).__name__, _e))
        rep = validate_storyboard(storyboard_json)
        norm = rep.get("normalized") if isinstance(rep, dict) else None
        if not isinstance(norm, dict):
            _err("契约校验器未产出 normalized (输入结构不可恢复), 拒绝渲染")
        cv = norm.get("contract_version")
        if isinstance(cv, bool) or not isinstance(cv, int) or cv != 1:
            _err("不支持的契约版本 %r (本渲染器支持契约 v1)" % (cv,))
        return norm, "raw_contract", rep.get("ok")
    _err("输入既非 validate_storyboard 报告 (缺 normalized 键) 也缺 contract_version 契约头, 拒绝渲染")


def _resolve_shots(data):
    """分镜表健壮性检查 → shots 列表 (每个元素均为含有效镜号的 dict)。"""
    if "分镜表" not in data:
        _err("分镜契约缺少 '分镜表' 键, 无镜头可渲染")
    shots = data.get("分镜表")
    if not isinstance(shots, list):
        _err("'分镜表' 必须为列表, 实际为 %s" % type(shots).__name__)
    if len(shots) == 0:
        _err("'分镜表' 为空, 无镜头可渲染")
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            _err("分镜表[%d] 必须为对象(dict), 实际为 %s" % (i, type(s).__name__))
        sid = s.get("镜号")
        if sid is None or (isinstance(sid, str) and not sid.strip()):
            _err("分镜表[%d] 缺少有效镜号, 无法渲染" % i)
    return shots


def _resolve_view(model_key):
    """model_key → (key, view); 未知键诚实 ValueError 列出已知键。"""
    if model_key is None:
        model_key = DEFAULT_MODEL_KEY
    if not isinstance(model_key, str):
        _err("model_key 必须为字符串或 None, 实际为 %s" % type(model_key).__name__)
    key = model_key.strip()
    if key not in MODEL_KEYS:
        _err("未知 model_key %r; 已知键: %s (键名大小写敏感)" % (model_key, ", ".join(MODEL_KEYS)))
    return key, _MODEL_VIEWS[key]


# ------------------------------------------------------------------
# 公共 API
# ------------------------------------------------------------------
def render_storyboard_prompts(storyboard_json, model_key=None):
    """从分镜契约 JSON 确定性渲染每镜提示词。

    storyboard_json: validate_storyboard 的报告 {"ok","errors","warnings","normalized"}
                     或含 contract_version 的原始分镜结构 (自动归一化取派生时间轴)
    model_key:       "SEEDANCE_25" | "WAN_30" | "GENERIC" | None (默认 GENERIC)

    返回: {"per_shot": [{"镜号": 原值, "prompt_text": 7 段文本}, ...],
           "render_meta": {...}}
    确定性: 同输入两次调用逐字节一致 (无时间戳/无随机)。
    坏输入: ValueError (诚实, 带定位信息), 绝不抛裸 KeyError/TypeError。
    """
    key, view = _resolve_view(model_key)
    data, source_form, contract_ok = _resolve_contract(storyboard_json)
    shots = _resolve_shots(data)

    per_shot = []
    for s in shots:
        per_shot.append({"镜号": s.get("镜号"), "prompt_text": _render_shot_text(s, data, view)})

    caps_ver = None
    if key == "SEEDANCE_25":
        caps_ver, _core = _seedance_capabilities()
        caps_ver = caps_ver or None
    cv = data.get("contract_version")
    total_dur = _field_num(data, "总时长秒")

    meta = {
        "render_version": RENDER_VERSION,
        "model_key": key,
        "model_label": view["label"],
        "model_traits": list(view["traits"]),
        "capabilities_source": view["capabilities_source"],
        "capabilities_version": caps_ver,
        "element_order": list(ELEMENT_ORDER),
        "source_form": source_form,
        "contract_ok": bool(contract_ok) if contract_ok is not None else None,
        "contract_version": cv if (isinstance(cv, int) and not isinstance(cv, bool)) else None,
        "shot_count": len(per_shot),
        "total_duration_s": total_dur,
        "deterministic": True,
    }
    return {"per_shot": per_shot, "render_meta": meta}
