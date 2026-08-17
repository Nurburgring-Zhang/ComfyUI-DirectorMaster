# -*- coding: utf-8 -*-
"""
DirectorMaster 格式导出引擎 (V14.2) — TXT / JSON / MD / HTML 真实格式转换
====================================================================
最终输出保存格式支持。不是简单改后缀 — 每种格式有真实的结构转换:

- TXT : 原文 (剧本/分镜/手册 保持工业格式)
- JSON: 结构化解析 — 剧本解析为 场次/对白 对象, 分镜解析为 逐镜对象
        (按 format_shot_table 的固定列宽精确切片), 手册按 【】 分节
- MD  : Markdown 重构 — 场次标题 → ##, 对白 → 角色加粗, 分镜 → Markdown 表格
- HTML: 完整样式文档 — 内嵌 CSS, 剧本等宽排版, 分镜真实 <table>, 实体转义
"""
import re as _re
import json as _json
import html as _html

VALID_FORMATS = ("TXT", "JSON", "MD", "HTML")

# V14.2 分镜表格式: 短表头行 (镜号/阶段/类型阶段/景别/运镜/焦段/时长, ljust 5/6/8/7/8/8/8)
# + 标签子行 (焦点 / 声音|色彩|光影|材质|氛围|情绪|转场 / 设计)
_SHOT_ROW_WIDTHS = [5, 6, 8, 7, 8, 8, 8]
_SHOT_ROW_NAMES = ["镜号", "阶段", "类型阶段", "景别", "运镜", "焦段", "时长"]
_SHOT_SUBKEYS = ("声音", "色彩", "光影", "材质", "氛围", "情绪", "转场")
_SHOT_COL_NAMES = ["镜号", "阶段", "类型阶段", "景别", "运镜", "焦段", "时长",
                   "画面焦点", "声音", "色彩", "光影", "材质", "氛围", "情绪", "转场"]


def parse_shot_table(text):
    """解析 format_shot_table 输出为逐镜对象 (V14.2 短行+子行格式)."""
    shots = []
    meta_line = ""
    cur = None
    for raw in (text or "").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("分镜表"):
            meta_line = line.strip()
            continue
        if line.startswith("─") or line.startswith("故事弧") or line.startswith("镜号"):
            continue
        stripped = line.strip()
        # 子行: 焦点 / 风格键值对 / 设计
        if line.startswith("    ") and cur is not None:
            if stripped.startswith("焦点:") or stripped.startswith("焦点："):
                cur["画面焦点"] = stripped.split(":", 1)[-1].split("：", 1)[-1].strip()
            elif stripped.startswith("设计:") or stripped.startswith("设计："):
                cur["设计"] = stripped.split(":", 1)[-1].split("：", 1)[-1].strip()
            else:
                body = stripped
                for key in _SHOT_SUBKEYS:
                    m = _re.search(rf"{key}:\s*([^|]*?)(?=\s*\|\s*(?:{'|'.join(_SHOT_SUBKEYS)}):|$)", body)
                    if m:
                        cur[key] = m.group(1).strip()
            continue
        # 表头行: 前 5 字符内是数字镜号
        head = line[:5].strip()
        if not head.isdigit():
            continue
        rec = {name: "" for name in _SHOT_COL_NAMES}
        rec["设计"] = ""
        pos = 0
        for name, w in zip(_SHOT_ROW_NAMES, _SHOT_ROW_WIDTHS):
            rec[name] = line[pos:pos + w].strip()
            pos += w
        cur = rec
        shots.append(rec)
    return {"meta": meta_line, "shots": shots}

_HEADING_RE = _re.compile(r"^(INT\.|EXT\.|INT\./EXT\.|EST\.|内\.|外\.|内\./外\.)", _re.I)
_TRANSITION_RE = _re.compile(
    r"^(CUT TO:|FADE OUT\.|FADE IN:|DISSOLVE TO|SMASH CUT|MATCH CUT|INTERCUT|LATER:|MEANWHILE:|FREEZE FRAME|IRIS IN|BACK TO|CONTINUOUS:|THE NEXT)", _re.I)
_HEADING_META_RE = _re.compile(r"\[(第\d+幕·[^·\]]+)\s*·\s*场(\d+/\d+)\s*·\s*([^·\]]+?)\s*·\s*戏剧张力[:：](\d+)/10\]")


def _parse_heading_meta(heading):
    """从场景标题的 [第N幕·XX · 场X/Y · 节拍 · 戏剧张力:Z/10] 提取结构化元数据."""
    m = _HEADING_META_RE.search(heading)
    if not m:
        return {}
    return {"幕": m.group(1).strip(), "场次": m.group(2), "节拍": m.group(3).strip(), "张力": int(m.group(4))}


def parse_formats(text):
    """解析多选格式串 → 去重校验后的格式列表 (顺序保持, 非法项丢弃)."""
    from aggregator.node_base import parse_multi_select
    items = parse_multi_select(text or "TXT", default="TXT")
    out = []
    for it in items:
        v = it.strip().upper().replace(".", "")
        if v in VALID_FORMATS and v not in out:
            out.append(v)
    return out or ["TXT"]


# ============================================================
# 剧本解析 (format_screenplay 输出 → 结构化)
# ============================================================
def parse_screenplay(text):
    """把 format_screenplay 的文本解析为结构化 dict. 真实解析, 非包装."""
    lines = (text or "").split("\n")
    result = {"title": "", "meta": "", "scenes": []}
    cur = None
    pending_role = None
    pending_paren = ""
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        m = _re.match(r"^《([^》]+)》", stripped)
        if m and not result["title"]:
            result["title"] = m.group(1)
            continue
        if stripped.startswith("导演:") and not result["meta"]:
            result["meta"] = stripped
            continue
        if stripped.startswith("─" * 4) or stripped.startswith("【") or stripped.startswith("════"):
            # 附录/装饰块 — 不属于剧本正文场次
            if cur:
                result["scenes"].append(cur)
                cur = None
            continue
        if _HEADING_RE.match(stripped):
            if cur:
                result["scenes"].append(cur)
            cur = {"heading": stripped, "meta": _parse_heading_meta(stripped),
                   "action": [], "dialogues": [], "transition": ""}
            pending_role = None
            continue
        if _TRANSITION_RE.match(stripped):
            if cur:
                cur["transition"] = stripped
                result["scenes"].append(cur)
                cur = None
            continue
        if cur is None:
            continue
        # 对白三行式: 角色(12空格) / 括号(10空格) / 台词(8空格)
        if raw.startswith("            ") and not raw.startswith("          ("):
            pending_role = stripped
            pending_paren = ""
            continue
        if raw.startswith("          (") and pending_role is not None:
            pending_paren = stripped.strip("()")
            continue
        if raw.startswith("        ") and pending_role is not None:
            cur["dialogues"].append({"role": pending_role, "paren": pending_paren, "line": stripped})
            pending_role = None
            pending_paren = ""
            continue
        if stripped.startswith("〔潜文本"):
            cur.setdefault("subtext", stripped)
            continue
        # 其余视为动作行
        cur["action"].append(stripped)
    if cur:
        result["scenes"].append(cur)
    return result


# ============================================================
# 分镜表解析 — 见文件顶部 parse_shot_table (V14.2 短行+子行格式)
# ============================================================


def split_sections(text):
    """按 【...】 标题分节 (手册/报告类文本)."""
    sections = []
    cur_title, cur_body = "", []
    for line in (text or "").split("\n"):
        m = _re.match(r"^【([^】]+)】", line.strip())
        if m:
            if cur_title or cur_body:
                sections.append({"title": cur_title, "body": "\n".join(cur_body).strip()})
            cur_title = m.group(1)
            cur_body = []
        else:
            cur_body.append(line)
    if cur_title or cur_body:
        sections.append({"title": cur_title, "body": "\n".join(cur_body).strip()})
    return [s for s in sections if s["title"] or s["body"]]


# ============================================================
# 转换器
# ============================================================
def to_json(content, kind, project):
    """内容 → 结构化 JSON 字符串 (按资产类型真实解析)."""
    content = content or ""
    payload = {"项目": project, "资产类型": kind, "字符数": len(content)}
    # 已是 JSON 的资产 (视频请求/核心数据) — 校验并原样嵌入
    stripped = content.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            payload["data"] = _json.loads(content)
            return _json.dumps(payload, ensure_ascii=False, indent=2)
        except Exception:
            pass
    if kind == "剧本":
        sp = parse_screenplay(content)
        payload["format"] = "screenplay"
        payload.update(sp)
        payload["场次数"] = len(sp["scenes"])
    elif kind == "分镜":
        st = parse_shot_table(content)
        payload["format"] = "shot_table"
        payload.update(st)
        payload["镜头数"] = len(st["shots"])
    else:
        payload["format"] = "sections"
        payload["sections"] = split_sections(content)
    return _json.dumps(payload, ensure_ascii=False, indent=2)


def to_md(content, kind, project):
    """内容 → Markdown (场次→##, 对白→加粗角色, 分镜→表格)."""
    content = content or ""
    out = [f"# {project} · {kind}", ""]
    if kind == "剧本":
        sp = parse_screenplay(content)
        if sp["title"]:
            out[0] = f"# 《{sp['title']}》"
        if sp["meta"]:
            out += [f"> {sp['meta']}", ""]
        for i, sc in enumerate(sp["scenes"], 1):
            out.append(f"## 场 {i} · {sc['heading']}")
            out.append("")
            for a in sc["action"]:
                out.append(a)
            if sc["action"]:
                out.append("")
            for d in sc["dialogues"]:
                paren = f" _({d['paren']})_" if d["paren"] else ""
                out.append(f"**{d['role']}**{paren}: {d['line']}")
            if sc.get("subtext"):
                out.append("")
                out.append(f"> {sc['subtext']}")
            if sc["transition"]:
                out.append("")
                out.append(f"*{sc['transition']}*")
            out.append("")
        if not sp["scenes"]:
            out += ["```", content, "```"]
    elif kind == "分镜":
        st = parse_shot_table(content)
        if st["meta"]:
            out += [f"> {st['meta']}", ""]
        if st["shots"]:
            cols = _SHOT_COL_NAMES
            out.append("| " + " | ".join(cols) + " |")
            out.append("|" + "---|" * len(cols))
            for s in st["shots"]:
                out.append("| " + " | ".join((s.get(c, "") or "").replace("|", "/") for c in cols) + " |")
                if s.get("设计"):
                    out.append(f"> 设计: {s['设计']}")
            out.append("")
        else:
            out += ["```", content, "```"]
    else:
        for sec in split_sections(content):
            if sec["title"]:
                out.append(f"## {sec['title']}")
                out.append("")
            if sec["body"]:
                out.append(sec["body"])
                out.append("")
    return "\n".join(out)


_CSS = """
body{background:#111418;color:#e8e6e3;font-family:'Segoe UI',system-ui,sans-serif;margin:0;padding:32px 8vw;line-height:1.7}
h1{color:#f5d76e;border-bottom:2px solid #f5d76e;padding-bottom:8px}
h2{color:#8fd3f4;margin-top:2em}
.meta{color:#9aa0a6;font-size:.9em}
pre.script{background:#181c22;border-left:3px solid #f5d76e;padding:14px 18px;white-space:pre-wrap;font-family:Consolas,'Courier New',monospace;font-size:.95em}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.85em}
th,td{border:1px solid #333a42;padding:5px 8px;text-align:left}
th{background:#1d232b;color:#8fd3f4}
tr:nth-child(even){background:#161a20}
.role{color:#f5d76e;font-weight:600}
.paren{color:#9aa0a6;font-style:italic}
.trans{color:#8fd3f4;font-style:italic;letter-spacing:.1em}
.subtext{color:#b7a6f5;font-style:italic}
footer{margin-top:3em;color:#6b7280;font-size:.8em;border-top:1px solid #2a3038;padding-top:10px}
"""


def to_html(content, kind, project):
    """内容 → 完整 HTML 文档 (内嵌 CSS + 实体转义 + 真实结构)."""
    content = content or ""
    e = _html.escape
    body = []
    if kind == "剧本":
        sp = parse_screenplay(content)
        body.append(f"<h1>《{e(sp['title'] or project)}》</h1>")
        if sp["meta"]:
            body.append(f"<p class='meta'>{e(sp['meta'])}</p>")
        for i, sc in enumerate(sp["scenes"], 1):
            body.append(f"<h2>场 {i} · {e(sc['heading'])}</h2>")
            if sc["action"]:
                body.append("<pre class='script'>" + e("\n".join(sc["action"])) + "</pre>")
            for d in sc["dialogues"]:
                paren = f" <span class='paren'>({e(d['paren'])})</span>" if d["paren"] else ""
                body.append(f"<p><span class='role'>{e(d['role'])}</span>{paren}<br>&nbsp;&nbsp;&nbsp;&nbsp;{e(d['line'])}</p>")
            if sc.get("subtext"):
                body.append(f"<p class='subtext'>{e(sc['subtext'])}</p>")
            if sc["transition"]:
                body.append(f"<p class='trans'>{e(sc['transition'])}</p>")
        if not sp["scenes"]:
            body.append("<pre class='script'>" + e(content) + "</pre>")
    elif kind == "分镜":
        st = parse_shot_table(content)
        body.append(f"<h1>{e(project)} · 分镜表</h1>")
        if st["meta"]:
            body.append(f"<p class='meta'>{e(st['meta'])}</p>")
        if st["shots"]:
            body.append("<table><tr>" + "".join(f"<th>{e(c)}</th>" for c in _SHOT_COL_NAMES) + "</tr>")
            for s in st["shots"]:
                body.append("<tr>" + "".join(f"<td>{e(s.get(c, '') or '')}</td>" for c in _SHOT_COL_NAMES) + "</tr>")
            body.append("</table>")
        else:
            body.append("<pre class='script'>" + e(content) + "</pre>")
    else:
        body.append(f"<h1>{e(project)} · {e(kind)}</h1>")
        for sec in split_sections(content):
            if sec["title"]:
                body.append(f"<h2>{e(sec['title'])}</h2>")
            if sec["body"]:
                body.append("<pre class='script'>" + e(sec["body"]) + "</pre>")
    import time as _t
    stamp = _t.strftime("%Y-%m-%d %H:%M:%S")
    return (
        "<!DOCTYPE html>\n<html lang='zh-CN'>\n<head>\n<meta charset='utf-8'>\n"
        f"<title>{e(project)} · {e(kind)}</title>\n<style>{_CSS}</style>\n</head>\n<body>\n"
        + "\n".join(body) +
        f"\n<footer>DirectorMaster V14.2 归档导出 · {e(kind)} · {stamp}</footer>\n</body>\n</html>"
    )


def convert(content, fmt, kind, project):
    """统一入口: (content, fmt) → (转换后内容, 文件扩展名)."""
    fmt = (fmt or "TXT").upper()
    if fmt == "JSON":
        return to_json(content, kind, project), "json"
    if fmt == "MD":
        return to_md(content, kind, project), "md"
    if fmt == "HTML":
        return to_html(content, kind, project), "html"
    return content, "txt"
