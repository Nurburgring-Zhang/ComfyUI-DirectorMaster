# -*- coding: utf-8 -*-
"""
V15.0-MERGED 失败记忆 (Reflexion Failure Memory)
=================================================
每次质量门拒收 → 结构化 lesson 追加 lessons.jsonl。
下次生成前按 (node_type, genre) 检索 top-k 注入提示词。
全确定性, 无 LLM — 这是无端点时系统"越用越聪明"的唯一学习通道。

V15.0 重写修复 (双AI互审 P1-2/P2-2):
  P1-2 并发写竞态 — 加 per-path 线程锁 + tmp 文件名唯一后缀 (pid+uuid) + PermissionError 重试。
  P2-2 get_lessons 排序 — 真实返回最新 k 条 (此前双重排序导致同分档最旧优先)。
"""
import os as _os
import json as _json
import time as _time
import threading as _threading
import uuid as _uuid

MAX_LESSONS = 200

_PATH_LOCKS = {}
_PATH_LOCKS_GUARD = _threading.Lock()


def _lock_for(path):
    with _PATH_LOCKS_GUARD:
        if len(_PATH_LOCKS) > 1024:
            for _p in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(_p, None)
        lk = _PATH_LOCKS.get(path)
        if lk is None:
            lk = _threading.Lock()
            _PATH_LOCKS[path] = lk
        return lk


def _lessons_path(store_dir):
    return _os.path.join(store_dir, "lessons.jsonl")


def _read_all(path):
    existing = []
    if _os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        existing.append(_json.loads(line))
                    except Exception:
                        pass
    return existing


def add_lesson(store_dir, gate_id, node_type, genre, reason, snippet_hash=""):
    """追加一条拒收教训 (去重: 同 gate+node+genre+reason 不重复记录). 并发安全."""
    try:
        _os.makedirs(store_dir, exist_ok=True)
        path = _lessons_path(store_dir)
        with _lock_for(path):
            existing = _read_all(path)
            for e in existing:
                if (e.get("gate") == gate_id and e.get("node") == node_type
                        and e.get("genre") == genre and e.get("reason") == reason):
                    return False
            lesson = {
                "ts": _time.strftime("%Y-%m-%d %H:%M:%S"),
                "gate": gate_id, "node": node_type, "genre": genre,
                "reason": reason, "snippet_hash": snippet_hash,
            }
            existing.append(lesson)
            existing = existing[-MAX_LESSONS:]
            # tmp 文件名唯一后缀 (pid+uuid) — 避免并发互踩固定 tmp
            tmp = path + f".tmp.{_os.getpid()}.{_uuid.uuid4().hex[:8]}"
            last_err = None
            for _attempt in range(5):
                try:
                    with open(tmp, "w", encoding="utf-8") as f:
                        for e in existing:
                            f.write(_json.dumps(e, ensure_ascii=False) + "\n")
                    _os.replace(tmp, path)
                    return True
                except PermissionError as _pe:
                    last_err = _pe
                    _time.sleep(0.03 * (_attempt + 1))
            if last_err:
                raise last_err
            return False
    except Exception as e:
        import sys as _s
        _s.stderr.write(f"[DirectorMaster] 失败记忆写入降级: {type(e).__name__}\n")
        return False


def get_lessons(store_dir, node_type="", genre="", k=5):
    """检索最相关的 k 条教训 (同 node+genre 优先, 同分档内取最新)."""
    try:
        path = _lessons_path(store_dir)
        if not _os.path.isfile(path):
            return []
        lessons = _read_all(path)

        def score(e):
            s = 0
            if node_type and e.get("node") == node_type:
                s += 2
            if genre and e.get("genre") == genre:
                s += 1
            return s

        # 先按时间倒序 (最新在前), 再按相关度稳定排序 → 同分档内最新优先
        lessons.sort(key=lambda e: e.get("ts", ""), reverse=True)
        lessons.sort(key=score, reverse=True)
        return lessons[:k]
    except Exception:
        return []


def render_lessons_block(lessons):
    """把教训渲染为提示词区块."""
    if not lessons:
        return ""
    lines = ["【历史教训 (来自失败记忆, 本次必须避免)】"]
    for e in lessons:
        lines.append(f"  - [{e.get('gate', '?')}门] {e.get('reason', '')} (节点: {e.get('node', '?')})")
    return "\n".join(lines)
