# -*- coding: utf-8 -*-
"""
V15.0-MERGED 风格融合引擎 (Style Fusion)
=========================================
多导演风格确定性融合: 主风格 (0.6) + 次风格 (0.3) + 反风格 (0.1)。

设计原则 (修正版, 否决原提案的数值评分伪代码):
- 导演档案是文本不是数值 — 融合 = 维度级文本组合, 不是加权分数
- 主风格: 全部 12 维作为基底
- 次风格: 选取与主风格互补的 3 个维度作为修饰层 (确定性选择)
- 反风格: 提取其"反常规动作"作为一条突破指令 (打破主风格惯性)
- 全确定性: 同输入 → 同输出 (哈希选择, 无 random)
"""
import hashlib as _hashlib

# 12 标准维 (与 director_data_unified 档案字段一致)
STYLE_DIMS = ["镜头", "光", "节奏", "色彩", "表演", "构图", "声音", "情绪", "物件", "年代"]

# 维度互补组: 当主风格在某组时, 次风格优先贡献同组维度 (形成对话而非重复)
_COMPLEMENT = {
    "镜头": ["构图", "节奏"], "光": ["色彩", "情绪"], "节奏": ["镜头", "声音"],
    "色彩": ["光", "物件"], "表演": ["情绪", "镜头"], "构图": ["镜头", "光"],
    "声音": ["节奏", "情绪"], "情绪": ["表演", "光"], "物件": ["色彩", "年代"],
    "年代": ["物件", "色彩"],
}


def _stable_pick(options, seed_str):
    if not options:
        return None
    h = int(_hashlib.md5(seed_str.encode("utf-8", "replace")).hexdigest(), 16)
    return options[h % len(options)]


def _get_profile(name):
    """从 600 档案库取档案 (支持带域前缀的输入). 空名返回空档案 (不幽灵回退)."""
    n = str(name or "").strip()
    if not n:
        return {}
    try:
        from director_data_unified import DIRECTOR_PROFILES_ALL
    except ImportError:
        return {}
    if "] " in n:
        n = n.split("] ", 1)[1]
    if n in DIRECTOR_PROFILES_ALL:
        return DIRECTOR_PROFILES_ALL[n]
    # 模糊兜底 (仅对非空输入)
    try:
        from aggregator.node_base import match_director_fuzzy
        m = match_director_fuzzy(n)
        if m and "] " in m:
            m = m.split("] ", 1)[1]
        return DIRECTOR_PROFILES_ALL.get(m, {}) if m else {}
    except Exception:
        return {}


def _clean_name(name):
    n = str(name or "").strip()
    return n.split("] ", 1)[1] if "] " in n else n


def fuse_styles(primary, secondary=None, anti=None, scene="", mood=""):
    """融合多导演风格 → 结构化融合档案文本.

    返回 dict: {text, primary, secondary, anti, fused_dims, break_directive}
    text 可直接注入提示词。全确定性。
    """
    p_prof = _get_profile(primary)
    s_prof = _get_profile(secondary) if secondary else {}
    a_prof = _get_profile(anti) if anti else {}
    p_name = _clean_name(primary)
    s_name = _clean_name(secondary) if secondary else ""
    a_name = _clean_name(anti) if anti else ""

    if not p_prof:
        return {"text": "", "primary": p_name, "secondary": s_name, "anti": a_name,
                "fused_dims": [], "break_directive": "", "error": f"主风格导演无档案: {p_name}"}

    lines = []
    lines.append(f"【风格融合 · 主 {p_name} (0.6)"
                 + (f" + 次 {s_name} (0.3)" if s_prof else "")
                 + (f" + 反 {a_name} (0.1)" if a_prof else "")
                 + "】")

    # 主风格基底 (全维)
    lines.append(f"■ 基底风格 [{p_name}]:")
    for dim in STYLE_DIMS:
        v = p_prof.get(dim, "")
        if v:
            lines.append(f"  {dim}: {v}")

    fused_dims = []
    # 次风格修饰层: 确定性选 3 个互补维度
    if s_prof:
        seed = f"{p_name}|{s_name}|{scene}|{mood}"
        cand = []
        for dim in STYLE_DIMS:
            sv = s_prof.get(dim, "")
            if not sv:
                continue
            pv = p_prof.get(dim, "")
            # 与主风格不同且与主风格强维度互补的优先
            comp = _COMPLEMENT.get(dim, [])
            priority = 1 if any(p_prof.get(c) for c in comp) else 0
            diff = 1 if sv != pv else 0
            cand.append((priority + diff, dim, sv))
        cand.sort(key=lambda x: -x[0])
        picks = cand[:3] if len(cand) >= 3 else cand
        # 确定性排序稳定: 同分按维度名
        picks = sorted(picks, key=lambda x: (-x[0], x[1]))[:3]
        if picks:
            lines.append(f"■ 次风格修饰 [{s_name}] (与主风格对话的维度):")
            for _, dim, sv in picks:
                lines.append(f"  {dim}: {sv}")
                fused_dims.append(dim)

    # 反风格突破指令: 提取反常规动作/失败美学作为一条"打破惯性"指令
    break_directive = ""
    if a_prof:
        bk = a_prof.get("反常规动作", "") or a_prof.get("失败美学", "")
        phil = a_prof.get("哲学内核", "")
        if bk:
            break_directive = f"突破指令(来自反风格 {a_name}): {bk}"
            if phil:
                break_directive += f" | 底层立场: {phil}"
            lines.append(f"■ 反风格突破 [{a_name}] (0.1 权重, 用于打破主风格惯性):")
            lines.append(f"  {break_directive}")

    # 场景/情绪锚定
    if scene or mood:
        lines.append(f"■ 融合锚定: 场景={scene or '未指定'} | 情绪={mood or '未指定'} — "
                     f"以上风格维度须服务于该场景与情绪, 不得堆砌")

    return {"text": "\n".join(lines), "primary": p_name, "secondary": s_name,
            "anti": a_name, "fused_dims": fused_dims, "break_directive": break_directive,
            "error": ""}
