# -*- coding: utf-8 -*-
"""
项目风格圣经 (批次4 builder-m3) — 脚本采证确定性骨架
====================================================
build_bible_skeleton(out_dir, project, store): version_store.log()/best() 只读抽统计
(版本数 / 最优版本 / 时长分布 / 景别频次), 分镜逐镜数据来自版本分镜存档文件
(只读, format_export.parse_shot_table 解析)。LLM 蒸馏段留 <!-- LLM_DISTILL_PENDING -->
诚实占位 — 未回填前绝不猜测风格结论 (验收①)。
存储: <out_dir>/dm_memory/<safe_project>/bible.md (UTF-8, 原子写 tmp+os.replace)。
两层分离纪律: version_store = raw 权威, 本模块只读使用, 绝不改其语义。
"""
import os
import re
import threading
import time

from . import schema

BIBLE_FILENAME = "bible.md"
BIBLE_DISTILL_PENDING = schema.BIBLE_DISTILL_PENDING
_MAX_SHOTFILE_CHARS = 2_000_000
_DUR_BUCKETS = ("≤1s", "1-3s", "3-5s", ">5s")

# 同源配方: aggregator/version_store._lock_for 同款进程内按路径互斥锁 (自实现, 不 import 私有函数)
_PATH_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def _lock_for(path):
    with _LOCKS_GUARD:
        if len(_PATH_LOCKS) > 1024:
            for k in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(k, None)
        lk = _PATH_LOCKS.get(path)
        if lk is None:
            lk = threading.Lock()
            _PATH_LOCKS[path] = lk
        return lk


def _safe_name(s):
    # 同源配方 + R1 MED-3/R2 MED-2 碰撞防护 (仅 dm_memory 层, version_store 不含此防护):
    # ① 替换/strip/截断发生信息丢失, ② 安全名含 ASCII 字母 (NTFS 大小写折叠),
    # ③ 以 ./空格结尾 (Windows 剥尾) — 任一命中即追加原名短 sha1 后缀 (sha1 基于
    # 原始 raw, 确定性), 与写侧各模块同映射。
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\\/:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def bible_path(out_dir, project):
    # 存储布局 (设计 §3): <out_dir>/dm_memory/<safe_project>/bible.md
    return os.path.join(str(out_dir), "dm_memory", _safe_name(project), BIBLE_FILENAME)


def _atomic_write_text(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)  # 原子替换
            return
        except PermissionError as e:  # Windows 并发占用重试
            last = e
            time.sleep(0.03 * (attempt + 1))
    raise last if last else OSError(f"写入失败: {path}")


def _parse_dur(v):
    m = re.search(r"(\d+(?:\.\d+)?)", str(v or ""))
    return float(m.group(1)) if m else None


def _dur_bucket(sec):
    if sec <= 1.0:
        return "≤1s"
    if sec <= 3.0:
        return "1-3s"
    if sec <= 5.0:
        return "3-5s"
    return ">5s"


def _collect_stats(out_dir, store):
    """确定性采证: log 窗口版本数 / best 最优版本 / 分镜存档逐镜时长分布+景别频次。
    分镜文件缺失/损坏/超长 → 该版本诚实跳过; 无任何可解析分镜 → 未采证说明, 不猜测。"""
    stats = {"版本数": 0, "最优版本": None, "分镜存档镜数": 0,
             "时长分布": {b: 0 for b in _DUR_BUCKETS}, "景别频次": {}}
    versions = []
    try:
        versions = list(store.log() or [])
    except Exception:
        versions = []
    stats["版本数"] = len(versions)
    try:
        best = store.best("total", 1) or []
        if best and isinstance(best[0], (tuple, list)) and len(best[0]) == 2:
            score, v = best[0]
            if isinstance(score, (int, float)) and isinstance(v, dict):
                stats["最优版本"] = {"名称": str(v.get("name") or ""),
                                     "总分": round(float(score), 3)}
    except Exception:
        pass
    sizes, shot_total = {}, 0
    for v in versions:
        if not isinstance(v, dict):
            continue
        try:
            fname = ((v.get("files") or {}).get("分镜") or {}).get("file") or ""
        except Exception:
            continue
        if not fname:
            continue
        try:
            path = os.path.join(str(out_dir), str(fname))
            if not os.path.isfile(path) or os.path.getsize(path) > _MAX_SHOTFILE_CHARS:
                continue
            with open(path, "r", encoding="utf-8") as f:
                text = f.read(_MAX_SHOTFILE_CHARS)
            from aggregator.format_export import parse_shot_table
            shots = (parse_shot_table(text) or {}).get("shots") or []
        except Exception:
            continue
        for s in shots:
            if not isinstance(s, dict):
                continue
            shot_total += 1
            size = str(s.get("景别") or "").strip()
            if size:
                sizes[size] = sizes.get(size, 0) + 1
            dur = _parse_dur(s.get("时长"))
            if dur is not None:
                stats["时长分布"][_dur_bucket(dur)] += 1
    stats["分镜存档镜数"] = shot_total
    stats["景别频次"] = {k: n for k, n in sorted(sizes.items(), key=lambda kv: (-kv[1], kv[0]))}
    if shot_total == 0:
        stats["采证说明"] = "窗口内无可解析分镜存档, 时长/景别未采证 (不猜测)"
    return stats


def _fmt_dist(stats):
    return ", ".join(f"{b}×{stats.get('时长分布', {}).get(b, 0)}" for b in _DUR_BUCKETS)


def _fmt_sizes(stats):
    return ", ".join(f"{k}×{v}" for k, v in stats.get("景别频次", {}).items()) or "无"


def render_bible_markdown(bible):
    """圣经 dict → bible.md 文本 (确定性, 无时间戳, 重跑逐字节稳定)。"""
    if not isinstance(bible, dict):
        raise ValueError("圣经不是 dict")
    stats = bible.get("脚本统计") or {}
    best = stats.get("最优版本")
    lines = [
        f"# 项目风格圣经 — {bible.get('项目', '')}",
        "",
        "> 生成口径: 脚本采证 (version_store log/best 只读取证, 确定性统计)。",
        f"> 蒸馏段须由 LLM 蒸馏回填; 回填前保留 {BIBLE_DISTILL_PENDING} 占位, 绝不猜测编造风格结论。",
        "",
        "## 脚本统计 (确定性采证)",
        f"- 版本数: {stats.get('版本数', 0)}",
        ("- 最优版本: {} (total={})".format(best.get("名称", ""), best.get("总分"))
         if isinstance(best, dict) else "- 最优版本: 无评分版本"),
        f"- 分镜存档镜数: {stats.get('分镜存档镜数', 0)}",
        f"- 时长分布(秒): {_fmt_dist(stats)}",
        f"- 景别频次: {_fmt_sizes(stats)}",
    ]
    if stats.get("采证说明"):
        lines.append(f"- 采证说明: {stats['采证说明']}")
    lines += [
        "",
        "## 蒸馏段 (LLM 蒸馏回填区)",
        str(bible.get("蒸馏段") or f"<!-- {BIBLE_DISTILL_PENDING} -->"),
        "",
        "## 采证口径",
        "- 数据来源: version_store.log()/best() 与版本分镜存档文件 (只读, 不改 version_store 语义)",
        "- 时长分桶: d≤1→≤1s; 1<d≤3→1-3s; 3<d≤5→3-5s; d>5→>5s",
        "- 景别频次: 分镜表 景别 列逐镜计数 (频次降序, 同频按名升序)",
    ]
    return "\n".join(lines) + "\n"


def build_bible_skeleton(out_dir, project, store):
    """脚本采证确定性骨架 → 落盘 bible.md, 返回圣经 dict (schema.validate_bible 可过)。
    蒸馏段恒为诚实占位 (蒸馏状态=pending); LLM 蒸馏回填由调用方改写 蒸馏段/蒸馏状态=done。"""
    project = str(project or "项目")
    bible = {
        "项目": project.strip()[:schema.BIBLE_TITLE_MAX] or "项目",
        "脚本统计": _collect_stats(out_dir, store),
        "蒸馏段": f"<!-- {BIBLE_DISTILL_PENDING} -->",
        "蒸馏状态": "pending",
    }
    ok, errs = schema.validate_bible(bible)
    if not ok:
        raise ValueError("圣经骨架校验失败: " + "; ".join(errs))
    path = bible_path(out_dir, project)
    with _lock_for(path):
        _atomic_write_text(path, render_bible_markdown(bible))
    return bible


def render_bible_prompt(bible):
    """圣经 dict → 注入提示词段 (确定性)。校验不过 → "" (诚实降级, 不编造)。"""
    if not isinstance(bible, dict):
        return ""
    ok, _ = schema.validate_bible(bible)
    if not ok:
        return ""
    stats = bible.get("脚本统计") or {}
    best = stats.get("最优版本")
    best_txt = "{}(total={})".format(best.get("名称", ""), best.get("总分")) if isinstance(best, dict) else "无"
    lines = [
        f"【项目风格圣经 · {bible.get('项目', '')}】",
        (f"脚本采证: 版本数={stats.get('版本数', 0)} | 最优版本={best_txt} "
         f"| 分镜镜数={stats.get('分镜存档镜数', 0)} | 时长分布: {_fmt_dist(stats)} "
         f"| 景别频次: {_fmt_sizes(stats)}"),
    ]
    if bible.get("蒸馏状态") == "done":
        distill = [ln.strip().lstrip("- ").strip() for ln in str(bible.get("蒸馏段", "")).splitlines()]
        distill = [ln for ln in distill if ln]
        if distill:
            lines.append("风格约束 (蒸馏回填):")
            lines.extend(f"- {ln[:120]}" for ln in distill[:8])
    else:
        lines.append("蒸馏状态: pending — 风格结论待蒸馏回填 (诚实占位, 不猜测)")
    return "\n".join(lines)
