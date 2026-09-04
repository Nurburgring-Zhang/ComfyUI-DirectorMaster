# -*- coding: utf-8 -*-
"""episode_pipeline/ledger.py — 覆盖账本校验 (批次7 builder-e1, V17.0.0)
==========================================================================
verify_coverage(text, ledger) -> (ok, errors:list[str])
账本 = [{"start","end","category"}] 段列表, category ∈
{episode, chapter_marker, blank, toc, preamble, other} (splitter.CATEGORIES)。

硬约束 (lumenx 80k 静默截断反面教材 → 全部 fail loud, 任何未归类字符不静默):
  1) 形状: 段为 dict, start/end 为真 int (bool 不算), 0<=start<end<=len(text)
  2) 类别合法
  3) 连续铺满: 首段 start==0, 相邻段零缝隙零重叠 (prev.end==next.start),
     末段 end==len(text) → 任何 gap 即"未归类残余"报错
  4) Σ(end-start) == len(text) (钉板口径, 即使铺满也复核)
  5) 类别-内容 sanity: blank 段必须全空白; episode/other/preamble 段必须含
     非空白字符; chapter_marker 段必须含标记样模式; toc 段必须含标记样行
归一化纪律: BOM/CRLF/全角空格/零宽字符一律"先记账后归类不吞字符"——它们
随所在段计入 Σ, 不做任何剥离。
确定性: 纯函数, 报错顺序 = 段索引顺序, 无 dict 迭代序依赖。
"""

from aggregator.episode_pipeline.splitter import CATEGORIES, MARKER_RES


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _has_marker_like(seg_text):
    for line in seg_text.split("\n"):
        if not line.strip():
            continue
        if any(rx.match(line) for rx in MARKER_RES):
            return True
    return False


def verify_coverage(text, ledger):
    """覆盖账本校验 (钉板接口)。ok=False 时 errors 逐条点名段索引与位置。"""
    text = text if isinstance(text, str) else str(text or "")
    total = len(text)
    errors = []

    if not isinstance(ledger, list):
        return False, ["账本必须是段列表, 实际 %s" % type(ledger).__name__]

    segs = []
    for i, seg in enumerate(ledger):
        if not isinstance(seg, dict):
            errors.append("段 %d 形状异常 (非 dict, 实际 %s)"
                          % (i, type(seg).__name__))
            continue
        s, e = seg.get("start"), seg.get("end")
        cat = seg.get("category")
        if not _is_int(s) or not _is_int(e):
            errors.append("段 %d start/end 必须是整数 (实际 %r/%r)"
                          % (i, s, e))
            continue
        if cat not in CATEGORIES:
            errors.append("段 %d 非法类别 %r (合法: %s)"
                          % (i, cat, "|".join(CATEGORIES)))
            continue
        if s < 0 or e > total:
            errors.append("段 %d [%s, %s) 越界 (文本长度 %d)"
                          % (i, s, e, total))
            continue
        if s >= e:
            errors.append("段 %d 空段或倒序 [%s, %s)" % (i, s, e))
            continue
        segs.append((i, s, e, cat, text[s:e]))

    if errors:
        return False, errors

    if total == 0 and not segs:
        return True, []

    # 铺满校验: 排序后零缝隙零重叠
    ordered = sorted(segs, key=lambda t: (t[1], t[2]))
    cursor = 0
    for (idx, s, e, cat, _st) in ordered:
        if s > cursor:
            errors.append("未归类残余 [%d, %d) 共 %d 字 (fail loud, 不静默丢)"
                          % (cursor, s, s - cursor))
        elif s < cursor:
            errors.append("段 %d [%d, %d) 与前段重叠 (前段末端 %d)"
                          % (idx, s, e, cursor))
        cursor = max(cursor, e)
    if cursor < total:
        errors.append("未归类残余 [%d, %d) 共 %d 字 (fail loud, 不静默丢)"
                      % (cursor, total, total - cursor))

    # Σ==len 硬约束 (钉板口径)
    total_segs = sum(e - s for (_i, s, e, _c, _st) in segs)
    if total_segs != total:
        errors.append("Σ(段长)=%d != len(text)=%d" % (total_segs, total))

    # 类别-内容 sanity
    for (idx, s, e, cat, st) in segs:
        if cat == "blank":
            if st.strip() != "":
                errors.append("段 %d (blank) 含非空白字符 %r"
                              % (idx, st[:20]))
        elif cat in ("episode", "other", "preamble"):
            if st.strip() == "":
                errors.append("段 %d (%s) 为纯空白, 应归类 blank" % (idx, cat))
        elif cat == "chapter_marker":
            if not _has_marker_like(st):
                errors.append("段 %d (chapter_marker) 不含标记样模式: %r"
                              % (idx, st[:20]))
        elif cat == "toc":
            if not _has_marker_like(st):
                errors.append("段 %d (toc) 不含标记样行: %r" % (idx, st[:20]))

    return (not errors), errors
