# -*- coding: utf-8 -*-
"""
knowledge_base/quality_precedents — 质量判例库 (V16.7 批次3 D7, builder-b2)
==========================================================================
NP-*.md 质量判例语料 + 确定性加载器 (仅 stdlib, 零第三方依赖)。

冻结接口 (批次3 派发钉死, 消费方 aggregator/review_engine.py 等):
    list_precedents() -> list[dict]

条目键结构 (8 键, 有效/无效条目同构, 消费方可统一取值):
    id           判例编号 "NP-001" 起 (frontmatter id)
    rule         规则一句话 (str)
    precedent    判例正文摘要, 含证据指针 (str)
    self_check   自检问题 (str)
    evidence_ref 证据指针 file:line 或测试名 (str)
    file         来源文件名 (NP-xxx.md)
    ok           True=有效条目 / False=无效条目
    error        有效条目为 ""; 无效条目为具体原因 (缺字段逐个点名)

硬校验 (加载即校验, 字段完整率必须 100%):
  - id / rule / precedent / self_check / evidence_ref 五字段任一缺失或为空
    → 该条记为错误条目进返回值 (诚实报错), 绝不静默跳过;
  - id 必须匹配 ^NP-\\d{3}$, 重复 id 的后到文件记错误条目;
  - frontmatter 键集封闭 (仅上述 5 键), 未知键记错误条目;
  - 单文件读取/解析异常不崩加载器 — 逐文件 try, 错误项带原因返回。

import 无副作用: 本模块 import 时不做任何文件 I/O, 仅在 list_precedents()
调用时扫描目录; 目录不可读同样以错误条目返回而非抛异常。
"""
import os as _os
import re as _re

_HERE = _os.path.dirname(_os.path.abspath(__file__))

__all__ = ["list_precedents", "REQUIRED_FIELDS"]

# frontmatter 必填字段 (键集封闭)
REQUIRED_FIELDS = ("id", "rule", "precedent", "self_check", "evidence_ref")

_ID_RE = _re.compile(r"^NP-\d{3}$")
_FM_LINE_RE = _re.compile(r"^([a-z][a-z0-9_]*):\s*(.*)$")


def _empty_entry(file_name):
    """统一 8 键空条目 (无效条目的底座, 字段缺失置 "")."""
    return {"id": "", "rule": "", "precedent": "", "self_check": "", "evidence_ref": "",
            "file": file_name, "ok": False, "error": ""}


def _split_frontmatter(text):
    """手写 frontmatter 解析 (对齐 tools/sync_mode_index.py 的禁 yaml 口径)。
    返回 (dict, error)。容忍 BOM 与 \\r\\n; 值两端成对引号剥除。"""
    s = (text or "").replace("\ufeff", "").replace("\r\n", "\n")
    lines = s.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, "缺少 frontmatter 起始行 '---'"
    fm = {}
    closed = False
    for ln in lines[1:]:
        if ln.strip() == "---":
            closed = True
            break
        if not ln.strip():
            continue
        m = _FM_LINE_RE.match(ln.strip())
        if not m:
            return {}, "frontmatter 行无法解析: %r" % ln.strip()[:48]
        val = m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1].strip()
        fm[m.group(1)] = val
    if not closed:
        return {}, "frontmatter 未闭合 (缺结束 '---')"
    return fm, ""


def list_precedents(directory=None):
    """扫描 NP-*.md 判例语料 → list[dict] (确定性: 按文件名排序)。

    硬校验与容错语义见模块 docstring; 任何情况下不抛异常、不静默丢条目:
    目录不可读/文件损坏/字段缺失/键越界/id 重复 全部以 ok=False 错误条目返回。
    """
    root = directory or _HERE
    try:
        names = sorted(n for n in _os.listdir(root)
                       if n.lower().startswith("np-") and n.lower().endswith(".md"))
    except OSError as e:
        bad = _empty_entry(str(root))
        bad["error"] = "目录不可读: %s" % e
        return [bad]
    if not names:
        return []
    seen_ids = {}
    result = []
    for name in names:
        entry = _empty_entry(name)
        try:
            with open(_os.path.join(root, name), "r", encoding="utf-8") as f:
                text = f.read()
            if not text.strip():
                entry["error"] = "空文件"
                result.append(entry)
                continue
            fm, fm_err = _split_frontmatter(text)
            if fm_err:
                entry["error"] = fm_err
                result.append(entry)
                continue
            unknown = sorted(k for k in fm if k not in REQUIRED_FIELDS)
            if unknown:
                entry["error"] = "frontmatter 未知键(键集封闭): %s" % ",".join(unknown)
                result.append(entry)
                continue
            for k in REQUIRED_FIELDS:
                entry[k] = str(fm.get(k, "") or "").strip()
            missing = [k for k in REQUIRED_FIELDS if not entry[k]]
            if missing:
                entry["error"] = "缺字段: %s" % ",".join(missing)
                result.append(entry)
                continue
            if not _ID_RE.match(entry["id"]):
                entry["error"] = "id 不符合 NP-\\d{3} 口径: %s" % entry["id"][:24]
                result.append(entry)
                continue
            if entry["id"] in seen_ids:
                entry["error"] = "id 重复 (首次出现于 %s)" % seen_ids[entry["id"]]
                result.append(entry)
                continue
            seen_ids[entry["id"]] = name
            entry["ok"] = True
            result.append(entry)
        except Exception as e:  # 坏文件不崩: 单文件异常带原因返回
            entry["error"] = "%s: %s" % (type(e).__name__, e)
            result.append(entry)
    return result
