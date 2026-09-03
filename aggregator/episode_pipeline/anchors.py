# -*- coding: utf-8 -*-
"""episode_pipeline/anchors.py — 锚点抽取 + 归一化回溯 (批次7 builder-e1, V17.0.0)
====================================================================================
extract_anchors(text, episode, max_len=20, n=3) -> list[anchor dict{quote,start,end}]
    每集 n 个 ≤max_len 字原文锚点, 句首/段首优先, 按集内位置散布 (首/中/尾)。
    start/end 为全文绝对偏移; quote == text[start:end] 逐字节 (尾部空白截除时
    end 同步收缩, 恒保持切片一致)。
traceback(text, anchors) -> (ok, results)
    回溯核验: 先精确路径 (text[start:end] == quote → 偏移核验直接通过);
    再归一化路径 (双方剥空白后 substring 匹配, 归一化位置经 index map 映射回
    原文偏移, 且要求声明偏移落在命中跨度内 → 偏移核验通过)。
    伪造/篡改锚点 → 0 命中 → ok=False; 引文真实但偏移错位 → hit 但 offset_ok
    =False → ok=False (验收③双向拦截); 偏移键存在但非 int (str/float/
    None/bool 畸形) 同按 offset_mismatch 拦截, 完全无 start/end 键才算
    无主张 (命中即认)。results 逐锚点 {"index","hit","offset_ok","method","found_start",
    "found_end"}; ok = 所有锚点 hit 且 offset_ok。

确定性纪律: 纯函数; 候选/命中选择全部按显式序 (位置升序, 平距取先);
str.find 顺序扫描; 无随机/时间/locale/dict 迭代序依赖。注意: 本模块不导入
stdlib 同名 traceback, 函数即包内钉板接口。
"""
_MAX_LEN_DEFAULT = 20
_N_DEFAULT = 3
_FRACTIONS = (0.0, 0.5, 0.85)
_SENT_BREAKS = "\n。！？…；"


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _normalize(s):
    """剥所有 Unicode 空白 (str.isspace 口径, 含全角空格/CRLF)。"""
    return "".join(ch for ch in s if not ch.isspace())


def _anchor_candidates(text, start, end):
    """锚点候选位: 集首或句末/段末符之后, 且该位非空白。升序去重。"""
    cands = []
    p = start
    if p < end and not text[p].isspace():
        cands.append(p)
    for i in range(start, end):
        ch = text[i]
        if ch in _SENT_BREAKS:
            q = i + 1
            if q < end and not text[q].isspace() and (not cands or q != cands[-1]):
                cands.append(q)
    return cands


def extract_anchors(text, episode, max_len=_MAX_LEN_DEFAULT, n=_N_DEFAULT):
    """每集 n 个 ≤max_len 字原文锚点 (钉板接口)。集跨度过小/全空白 → 少于
    n 个或空列表 (诚实缺省, 不伪造)。"""
    text = text if isinstance(text, str) else str(text or "")
    try:
        max_len = max(1, int(max_len))
    except Exception:
        max_len = _MAX_LEN_DEFAULT
    try:
        n = max(1, int(n))
    except Exception:
        n = _N_DEFAULT

    span = episode.get("span") if isinstance(episode, dict) else None
    if not isinstance(span, dict):
        return []
    s, e = span.get("start"), span.get("end")
    if not (_is_int(s) and _is_int(e)):
        return []
    s = max(0, min(s, len(text)))
    e = max(s, min(e, len(text)))
    if e <= s:
        return []

    cands = _anchor_candidates(text, s, e)
    if not cands:
        return []

    if n == len(_FRACTIONS):
        fracs = _FRACTIONS
    elif n < len(_FRACTIONS):
        fracs = _FRACTIONS[:n]
    else:
        fracs = tuple(i / (n - 1) * _FRACTIONS[-1] for i in range(n))

    used_starts = set()
    used_quotes = set()
    anchors = []
    for f in fracs:
        target = s + int((e - s) * f)
        ranked = sorted(cands, key=lambda c: (abs(c - target), c))
        for cand in ranked:
            if cand in used_starts:
                continue
            raw = text[cand:min(cand + max_len, e)]
            quote = raw.rstrip()
            if not quote or quote in used_quotes:
                continue
            used_starts.add(cand)
            used_quotes.add(quote)
            anchors.append({"quote": quote, "start": cand,
                            "end": cand + len(quote)})
            break
    return anchors


def traceback(text, anchors):
    """锚点回溯核验 (钉板接口) -> (ok, results)。归一化空白后 substring 匹配
    + 偏移核验; 伪造/篡改/错位全部拦截 (详见模块 docstring)。"""
    text = text if isinstance(text, str) else str(text or "")
    if not isinstance(anchors, list):
        return False, [{"error": "anchors 必须是列表, 实际 %s"
                        % type(anchors).__name__}]

    ntext = None
    idx_map = None

    def _norm_index():
        nonlocal ntext, idx_map
        if ntext is None:
            chars = []
            idx_map = []
            for i, ch in enumerate(text):
                if not ch.isspace():
                    chars.append(ch)
                    idx_map.append(i)
            ntext = "".join(chars)
        return ntext, idx_map

    results = []
    ok = True
    for i, a in enumerate(anchors):
        res = {"index": i, "hit": False, "offset_ok": False, "method": "miss",
               "found_start": None, "found_end": None}
        if not isinstance(a, dict):
            res["method"] = "invalid"
            ok = False
            results.append(res)
            continue
        quote = a.get("quote")
        if not isinstance(quote, str) or not quote.strip():
            res["method"] = "invalid"
            ok = False
            results.append(res)
            continue
        s, e = a.get("start"), a.get("end")
        _claimed = _is_int(s) and _is_int(e)
        _malformed = (not _claimed) and ("start" in a or "end" in a)
        _bad_off = _malformed or (_claimed and not (0 <= s < e <= len(text)))
        has_off = _claimed and not _bad_off

        if has_off and text[s:e] == quote:
            res["hit"] = True
            res["offset_ok"] = True
            res["method"] = "exact"
            res["found_start"] = s
            res["found_end"] = e
        else:
            nt, imap = _norm_index()
            nq = _normalize(quote)
            first = None
            verified = None
            if nq:
                pos = 0
                while True:
                    j = nt.find(nq, pos)
                    if j < 0:
                        break
                    fs = imap[j]
                    fe = imap[j + len(nq) - 1] + 1
                    if first is None:
                        first = (fs, fe)
                    if (not _claimed and not _malformed) or (
                            _claimed and not _bad_off and fs <= s < fe):
                        verified = (fs, fe)
                        break
                    pos = j + 1
            if verified is not None:
                res["hit"] = True
                res["offset_ok"] = True
                res["method"] = "normalized"
                res["found_start"] = verified[0]
                res["found_end"] = verified[1]
            elif first is not None:
                res["hit"] = True
                res["offset_ok"] = False
                res["method"] = "offset_mismatch"
                res["found_start"] = first[0]
                res["found_end"] = first[1]
        if not (res["hit"] and res["offset_ok"]):
            ok = False
        results.append(res)
    return ok, results
