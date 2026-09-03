# -*- coding: utf-8 -*-
"""episode_pipeline/splitter.py — 章节检测 + 分集切分 (批次7 builder-e1, V17.0.0)
=================================================================================
detect_chapters(text) -> list[chapter dict{index,title,start,end,marker}]
    章节标记: 第N章/节/卷 (阿拉伯/中文/全宽数字), Chapter N, 罗马数字行。
    防误报双闸: 标记必须在行首 + 标记词后不得紧跟汉字须接分隔符或行尾 (杀
    "第 3 页"/"第十章的内容他早已背熟"); 目录排除: 标记样行与下一条标记样
    行之间仅空白 (无正文) → 目录条目不作章节, 连续条目聚成 toc 区; 末条无
    下一条可依, 退看目录特征 (尾部点线/页码)。无标记 → 整本单章 (marker="")。
split_episodes(text, target_chars) -> (episodes, ledger)
    章节贪心聚合 (章节边界优先); 单章超 target 在段落边界切, 段落缺失退
    句末切, 句末也缺失才硬切 (单一超长段落兜底, 钉板"禁句内断开")。
    episode = {ep_id(ep_000 起 0 基), title, span{start,end}, text},
    text == novel[span.start:span.end] 逐字节。集 span 连续铺满章节区,
    集内包含章标行 (span 恒单连续区间, 管线切片契约)。
ledger = [{"start","end","category"}] 连续铺满 [0,len(text)) 的段列表,
    category ∈ {episode, chapter_marker, blank, toc, preamble, other} —
    toc 区从章节区中扣除, 段间零缝隙零重叠; Σ==len(text) 硬约束由
    ledger.verify_coverage 把关 (lumenx 静默截断反面教材)。

确定性纪律: 纯函数; 无随机/时间/locale/dict 迭代序依赖 (排序全部显式 key);
正则全 compiled 单遍线性扫描, 禁嵌套量词 (100k 样本 <5s 预算)。
"""
import re

# ---- 章节标记正则 (全 compiled) ----
_CN_NUM = r"[0-9０-９零一二三四五六七八九十百千两]+"
# 第N章/节/卷: 行首 + 标记词后不得紧跟汉字 (杀"第十章的内容"), 须分隔符或行尾
RE_CN_MARKER = re.compile(
    r"^(?P<indent>\s*)(?P<marker>第" + _CN_NUM + r"[章节卷])"
    r"(?![\u4e00-\u9fff])(?P<rest>.*)$")
RE_EN_MARKER = re.compile(
    r"^(?P<indent>\s*)(?P<marker>[Cc]hapter\s+(?:[0-9]+|[IVXLCDMivxlcdm]+))"
    r"(?![A-Za-z0-9])(?P<rest>.*)$")
RE_ROMAN_MARKER = re.compile(
    r"^(?P<indent>\s*)(?P<marker>M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})"
    r"(?:IX|IV|V?I{0,3}))(?=[\s.．、:：]|$)(?P<rest>.*)$", re.ASCII)

MARKER_RES = (RE_CN_MARKER, RE_EN_MARKER, RE_ROMAN_MARKER)

CATEGORIES = ("episode", "chapter_marker", "blank", "toc", "preamble", "other")

_SENT_ENDS = "。！？…；"
_ROMAN_MIN_LEN = 2  # 罗马数字须 ≥2 字符, 杀英文 "I" 代词


def _match_marker_line(line):
    """行首标记匹配: 返回 (marker, rest) 或 None。罗马数字行要求 ≥2 字符。"""
    for rx in MARKER_RES:
        m = rx.match(line)
        if m:
            marker = m.group("marker")
            if rx is RE_ROMAN_MARKER and len(marker.strip()) < _ROMAN_MIN_LEN:
                continue
            return marker, m.group("rest")
    return None


_TOC_TAIL_RE = re.compile(r"[.．·…]{2,}\s*[0-9０-９]*\s*$")


def _extract_title(rest):
    """标记行剩余部分 → 章题: 剥前导分隔符 + 剥尾目录点线/页码。"""
    t = rest.lstrip(" .．·—–-:：、\t　")
    t = _TOC_TAIL_RE.sub("", t)
    return t.strip()


def _has_toc_feature(rest):
    """目录条目特征: 标记行尾部点线/页码 (如 "夜行……1")。"""
    return bool(_TOC_TAIL_RE.search(rest))


def _split_lines(text):
    """[(start, content, end_incl_newline)], 确定性单遍。"""
    out = []
    pos = 0
    for ln in text.split("\n"):
        start = pos
        end_content = start + len(ln)
        end_incl = end_content + 1 if end_content < len(text) else end_content
        out.append((start, ln, end_incl))
        pos = end_incl
    return out


def _detect_internal(text):
    """(chapters, toc_regions)。标记样行真假判定: 与下一条标记样行之间有
    正文 (非空白) → 真章节; 仅空白相隔 → 目录条目 (连续条目聚 toc 区);
    末条无下一条可依, 退看目录特征。无真章节非空文本 → 单章兜底
    (marker="")。"""
    lines = _split_lines(text)
    cand = []
    for idx, (start, ln, end_incl) in enumerate(lines):
        m = _match_marker_line(ln)
        if m:
            cand.append((idx, start, end_incl, m[0], m[1]))
    if not cand:
        if not text:
            return [], []
        return [{"index": 1, "title": "", "start": 0, "end": len(text),
                 "marker": ""}], []
    n = len(cand)
    real_flags = []
    for i in range(n):
        if i == n - 1:
            real_flags.append(not _has_toc_feature(cand[i][4]))
        else:
            between = text[cand[i][2]:cand[i + 1][1]]
            real_flags.append(bool(between.strip()))
    real, toc = [], []
    i = 0
    while i < n:
        if real_flags[i]:
            real.append(cand[i])
            i += 1
            continue
        j = i
        while j < n and not real_flags[j]:
            j += 1
        toc.append((cand[i][1], cand[j - 1][2]))
        i = j
    if not real:
        return [{"index": 1, "title": "", "start": 0, "end": len(text),
                 "marker": ""}], toc
    chapters = []
    for k, (_idx, start, _incl, marker, rest) in enumerate(real):
        nxt_start = real[k + 1][1] if k + 1 < len(real) else len(text)
        chapters.append({
            "index": k + 1,
            "title": _extract_title(rest),
            "start": start,
            "end": nxt_start,
            "marker": marker,
        })
    return chapters, toc


def detect_chapters(text):
    """章节检测 (钉板接口)。无标记非空文本 → 整本单章; 空文本 → []。"""
    text = text if isinstance(text, str) else str(text or "")
    return _detect_internal(text)[0]


def _split_range(text, start, end, target):
    """[start,end) 超 target 时切段: 段落边界(\n)优先 → 句末 → 兜底硬切。
    返回 [(ps,pe)] 拼接还原原区间; 尾段并入前段 (若仍 ≤target)。"""
    if end - start <= target:
        return [(start, end)]
    pieces = []
    pos = start
    while end - pos > target:
        cut = -1
        nl = text.rfind("\n", pos, pos + target)
        if nl >= pos:
            cut = nl + 1
        else:
            for si in range(min(pos + target, end) - 1, pos, -1):
                if text[si] in _SENT_ENDS:
                    cut = si + 1
                    break
        if cut <= pos:
            cut = pos + target
        pieces.append((pos, cut))
        pos = cut
    if pos < end:
        if pieces and pieces[-1][1] - pieces[-1][0] + (end - pos) <= target:
            pieces[-1] = (pieces[-1][0], end)
        else:
            pieces.append((pos, end))
    return pieces


def _subtract_ranges(base_start, base_end, cuts):
    """[base_start,base_end) 扣除有序 cuts (toc 区), 返回剩余子区间列表。"""
    out = []
    cur = base_start
    for cs, ce in cuts:
        if ce <= cur or cs >= base_end:
            continue
        if cs > cur:
            out.append((cur, min(cs, base_end)))
        cur = max(cur, ce)
        if cur >= base_end:
            break
    if cur < base_end:
        out.append((cur, base_end))
    return out


def _build_ledger(text, chapters, toc_regions, total):
    """铺满 [0,total) 的覆盖账本 (零缝隙零重叠)。
    章节区扣 toc 后拆 marker 行/正文体; 缝隙按 空白→blank / 单章兜底→
    episode / 首真章前→preamble / 其余→other 归类, 不吞任何字符。"""
    toc_sorted = sorted(toc_regions, key=lambda r: (r[0], r[1]))
    fallback = bool(chapters) and chapters[0]["marker"] == ""
    first_ch_start = None
    for ch in chapters:
        if ch["marker"]:
            first_ch_start = ch["start"]
            break

    occupied = []
    for ts, te in toc_sorted:
        occupied.append((ts, te, "toc"))
    for ch in chapters:
        for rs, re_ in _subtract_ranges(ch["start"], ch["end"], toc_sorted):
            if ch["marker"] and rs == ch["start"]:
                marker_line_end = text.find("\n", ch["start"], ch["end"])
                m_end = marker_line_end + 1 if marker_line_end >= 0 else ch["end"]
                m_end = min(m_end, re_)
                occupied.append((rs, m_end, "chapter_marker"))
                if m_end < re_:
                    occupied.append((m_end, re_, "episode"))
            else:
                occupied.append((rs, re_, "episode"))
    occupied.sort(key=lambda r: (r[0], r[1]))

    segs = []
    cursor = 0
    for s, e, cat in occupied:
        if s > cursor:
            gap = text[cursor:s]
            if gap.strip() == "":
                gcat = "blank"
            elif fallback:
                gcat = "episode"
            elif first_ch_start is not None and s <= first_ch_start:
                gcat = "preamble"
            else:
                gcat = "other"
            segs.append({"start": cursor, "end": s, "category": gcat})
        segs.append({"start": s, "end": e, "category": cat})
        cursor = e
    if cursor < total:
        gap = text[cursor:total]
        if gap.strip() == "":
            gcat = "blank"
        elif fallback:
            gcat = "episode"
        elif first_ch_start is not None and cursor <= first_ch_start:
            gcat = "preamble"
        else:
            gcat = "other"
        segs.append({"start": cursor, "end": total, "category": gcat})
    return segs


def split_episodes(text, target_chars):
    """分集切分 (钉板接口) -> (episodes, ledger)。
    episodes: 章节贪心聚合, 每集 ≤target (单章超 target 段落边界二分);
    ep_id 从 ep_000 起 0 基; text == text[span.start:span.end] 逐字节。"""
    text = text if isinstance(text, str) else str(text or "")
    try:
        target = int(target_chars)
    except Exception:
        target = 0
    if target <= 0:
        raise ValueError("target_chars 必须是正整数, 实际 %r" % (target_chars,))
    if not text:
        return [], []

    chapters, toc = _detect_internal(text)

    units = []  # (piece_start, piece_end, chapter_title, chapter_marker)
    for ch in chapters:
        pieces = _split_range(text, ch["start"], ch["end"], target)
        for ps, pe in pieces:
            units.append((ps, pe, ch["title"], ch["marker"]))

    groups = []
    cur_units = []
    cur_len = 0
    for (ps, pe, ctitle, cmarker) in units:
        plen = pe - ps
        if cur_units and cur_len + plen > target:
            groups.append(cur_units)
            cur_units, cur_len = [], 0
        cur_units.append((ps, pe, ctitle, cmarker))
        cur_len += plen
    if cur_units:
        groups.append(cur_units)

    out = []
    for n, group in enumerate(groups):
        first_ct, first_cm = group[0][2], group[0][3]
        title = first_ct or first_cm or ("第%d集" % (n + 1))
        span_start = group[0][0]
        span_end = group[-1][1]
        out.append({
            "ep_id": "ep_%03d" % n,
            "title": title,
            "span": {"start": span_start, "end": span_end},
            "text": text[span_start:span_end],
        })

    ledger = _build_ledger(text, chapters, toc, len(text))
    return out, ledger
