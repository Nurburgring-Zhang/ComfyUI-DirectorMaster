# -*- coding: utf-8 -*-
"""
程序记忆 SOP (批次4 builder-m1) — 三段式 use_when/procedure/exceptions
======================================================================
落盘纪律: 只有调用方显式传 explicit=True 才写文件 (用户显式要求才沉淀 SOP);
否则返回未写原因, 绝不偷偷落盘。
存储: <out_dir>/dm_memory/<safe_project>/procedures/<safe_topic>.json (UTF-8 原子写)。
入库前脱敏 (R1 HIGH-1 接线): 落盘前对 SOP 三段自由文本 (use_when/procedure/exceptions)
递归 redact; topic 作为定位键属结构字段不碰。
"""
import json
import os
import re
import threading
import time

from . import redaction, schema

PROCEDURE_REQUIRED_KEYS = schema.PROCEDURE_REQUIRED_KEYS

# 同源配方: version_store._lock_for 同款进程内按路径互斥锁 (自实现, 不 import 其私有函数)
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
    # 原始 raw, 确定性跨进程稳定), 不同原名绝不共用同一目录; 纯中文/纯数字名零漂移。
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _procedures_dir(memory):
    return os.path.join(memory.out_dir, "dm_memory", _safe_name(memory.project), "procedures")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def upsert_procedure(memory, topic, doc, explicit=False):
    """新增/更新一条 SOP -> (written: bool, reason)。
    explicit=False 按纪律不落盘; explicit=True 但 schema 校验失败同样拒绝。"""
    topic_s = str(topic or "").strip()
    if not topic_s:
        return False, "topic 为空, 未写"
    if not explicit:
        return False, "用户未显式要求 (explicit=False), 按纪律不落盘"
    ok, errors = schema.validate_procedure(doc)
    if not ok:
        return False, "SOP 校验失败: " + "; ".join(errors)
    doc = redaction.redact_free_text(dict(doc))  # 入库脱敏 (R1 HIGH-1): 三段文本, topic 不碰
    payload = {"schema_version": 1, "topic": topic_s,
               "use_when": doc["use_when"], "procedure": doc["procedure"],
               "exceptions": doc["exceptions"], "updated_at": _now()}
    path = os.path.join(_procedures_dir(memory), _safe_name(topic_s) + ".json")
    with _lock_for(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        last_err = None
        for attempt in range(5):
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=1)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, path)
                last_err = None
                break
            except PermissionError as e:
                last_err = e
                time.sleep(0.03 * (attempt + 1))
        if last_err is not None:
            raise last_err
    return True, ""


def load_procedures(memory):
    """载入全部 SOP (按文件名序, 即 topic 序); 目录缺失或损坏条目诚实跳过。"""
    d = _procedures_dir(memory)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, name), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        if isinstance(data, dict):
            out.append(data)
    return out
