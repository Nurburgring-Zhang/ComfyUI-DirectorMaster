# -*- coding: utf-8 -*-
"""
偏好存储 (批次4 builder-m1) — 六分支语义去重 + 计数字段自校验 (验收③)
======================================================================
apply_preference(store, entry) -> branch ∈
  {added, equivalent_skipped, refined, conflict_replaced, invalid_removed, oneoff_ignored}
  - 等价判定 = 标题键相同 + 字符 bigram Jaccard ≥ 0.8 (stdlib 自实现);
  - 冲突替换由条目布尔标记 "冲突替换": True 显式声明 (内容相似度无法判定语义矛盾, 不猜);
  - "失效": True 为删除指令, 未命中任何存量时指令本身一次性消费 -> oneoff_ignored;
  - 一次性信号 (一次性/临时/本轮) 不落库 -> oneoff_ignored;
  - schema 非法条目视为调用方编程错误, 抛 ValueError (库里零改动)。
store 参数为 DmMemory 句柄 (open_memory 产物); verify_counts 另接受载入后的 dict。
存储: <out_dir>/dm_memory/<safe_project>/preferences.json (UTF-8 原子写)。
损坏自愈 (R1 MED-1): preferences.json 截断/非法 JSON/二进制/顶层结构非法 →
隔离改名为 preferences.json.corrupt (已存在则覆盖) + stderr 降级 → 返回默认空库
继续, 写路径不再被损坏永久卡死 (与 shot_cards 损坏行跳过口径对齐)。
入库前脱敏 (R1 HIGH-1): apply_preference 落盘前对自由文本字段 (标题/内容及嵌套
容器) 递归 redact; 结构字段 (signal/失效/一次性/冲突替换/计数) 不碰。
"""
import json
import os
import re
import sys
import threading
import time

from . import redaction, schema

PREFERENCE_BRANCHES = schema.PREFERENCE_BRANCHES
PREFERENCE_JACCARD_THRESHOLD = schema.PREFERENCE_JACCARD_THRESHOLD
PREFERENCE_ONEOFF_SIGNALS = schema.PREFERENCE_ONEOFF_SIGNALS

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
    # ① 替换/strip/截断发生信息丢失, ② 安全名含 ASCII 字母 (NTFS 大小写折叠可致
    # 不同原名同目录), ③ 以 ./空格结尾 (Windows 剥尾) — 任一命中即追加原名短 sha1
    # 后缀 (sha1 基于原始 raw): 同一原始输入恒映射同一文件名, 不同原名绝不共用同一目录。
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\\/:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _prefs_path(memory):
    return os.path.join(memory.out_dir, "dm_memory", _safe_name(memory.project), "preferences.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _blank_store():
    return {"schema_version": 1, "entries": [], "removed": [],
            "counts": {"added": 0, "refined": 0, "conflict_replaced": 0,
                       "invalid_removed": 0, "entries_total": 0}}


def bigram_jaccard(a, b):
    """字符 bigram Jaccard 相似度 (stdlib 自实现); 单字符退化为单字集合比较。"""
    def grams(s):
        s = str(s or "").strip()
        if len(s) < 2:
            return {s} if s else set()
        return {s[i:i + 2] for i in range(len(s) - 1)}
    ga, gb = grams(a), grams(b)
    if not ga and not gb:
        return 1.0
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def _atomic_write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    last_err = None
    for attempt in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            return
        except PermissionError as e:
            last_err = e
            time.sleep(0.03 * (attempt + 1))
    raise last_err if last_err else OSError(f"写入失败: {path}")


def _quarantine_corrupt(path):
    """损坏库隔离 (R1 MED-1): 改名为 <原路径>.corrupt; 已存在则覆盖。
    隔离本身失败也绝不致命 (调用方仍拿到空库继续)。"""
    try:
        os.replace(path, path + ".corrupt")  # os.replace 覆盖已存在目标
        return True
    except OSError:
        try:
            os.remove(path)
            return True
        except OSError:
            return False


def _load_preferences(memory):
    """载入偏好库; 损坏 (截断/非法 JSON/二进制/顶层结构非法) 自愈 (R1 MED-1):
    隔离为 preferences.json.corrupt (已存在则覆盖) + stderr 降级 → 默认空库继续,
    任何调用方 (apply_preference/verify_counts) 不再因损坏抛异常。
    二级结构损坏 (R2 MED-1): 合法 JSON 但 entries/removed 元素非 dict → 只丢弃坏元素
    (stderr 一次性告警带计数, 合法条目照常存活), counts 非 dict → 重置空计数;
    不为单个坏元素隔离整个文件 (避免误伤好数据), 写路径不再抛 AttributeError。"""
    path = _prefs_path(memory)
    if not os.path.exists(path):
        return _blank_store()
    try:
        with open(path, "rb") as f:
            data = json.loads(f.read().decode("utf-8", errors="replace"))
        if not isinstance(data, dict):
            raise ValueError("顶层非 dict")
        if not isinstance(data.get("entries"), list):
            raise ValueError("entries 非列表")
    except (json.JSONDecodeError, UnicodeDecodeError, OSError, ValueError) as e:
        try:
            sys.stderr.write(
                f"[DirectorMaster] 偏好库损坏, 已隔离重置: {path} "
                f"({type(e).__name__}: {e})\n")
        except Exception:
            pass
        _quarantine_corrupt(path)
        return _blank_store()
    # 二级结构损坏过滤 (R2 MED-1): 逐元素 isinstance(dict) 把关, 坏元素丢弃+告警计数
    dropped = 0
    for key in ("entries", "removed"):
        lst = data.get(key)
        if isinstance(lst, list):
            bad = [e for e in lst if not isinstance(e, dict)]
            if bad:
                dropped += len(bad)
                data[key] = [e for e in lst if isinstance(e, dict)]
    if dropped:
        try:
            sys.stderr.write(
                f"[DirectorMaster] 偏好库二级结构损坏, 已丢弃 {dropped} 个非 dict 元素 "
                f"(合法条目保留): {path}\n")
        except Exception:
            pass
    if not isinstance(data.get("counts"), dict):
        try:
            sys.stderr.write(
                f"[DirectorMaster] 偏好库 counts 字段非 dict, 已重置为空计数: {path}\n")
        except Exception:
            pass
        data["counts"] = _blank_store()["counts"]
    if not isinstance(data.get("removed"), list):
        data["removed"] = []  # 失效删除台账: 保留被删条目生命周期计数, 供 verify_counts 复算
    return data


def apply_preference(store, entry):
    """按六分支语义应用一条偏好, 返回分支名。store 为 DmMemory 句柄。
    落盘前对自由文本字段入库脱敏 (R1 HIGH-1); 去重键与存储值使用同一脱敏口径,
    保证同一原始输入的判重/删除指令行为一致。"""
    ok, errors = schema.validate_preference(entry)
    if not ok:
        raise ValueError("偏好校验失败: " + "; ".join(errors))
    entry = redaction.redact_free_text(dict(entry))  # 入库脱敏 (只动文本字段, 永不致命)
    path = _prefs_path(store)
    with _lock_for(path):
        data = _load_preferences(store)
        entries = data["entries"]
        counts = data["counts"]
        if entry.get("失效") is True:
            key = entry["标题"].strip()
            keep = [e for e in entries if str(e.get("标题", "")).strip() != key]
            removed_entries = [e for e in entries if str(e.get("标题", "")).strip() == key]
            if not removed_entries:
                return "oneoff_ignored"  # 删除指令未命中 — 指令一次性消费, 零改动零落盘
            entries[:] = keep
            data["removed"].extend(removed_entries)
            counts["invalid_removed"] += len(removed_entries)
            counts["entries_total"] = len(entries)
            _atomic_write_json(path, data)
            return "invalid_removed"
        if entry.get("signal") in PREFERENCE_ONEOFF_SIGNALS or entry.get("一次性") is True:
            return "oneoff_ignored"  # 一次性信号不落库
        key = entry["标题"].strip()
        idx = next((i for i, e in enumerate(entries)
                    if str(e.get("标题", "")).strip() == key), -1)
        now = _now()
        if idx == -1:
            entries.append({"标题": key, "内容": entry["内容"],
                            "signal": entry.get("signal") or "用户偏好",
                            "created_at": now, "updated_at": now,
                            "refined_count": 0, "replaced_count": 0})
            counts["added"] += 1
            branch = "added"
        elif entry.get("冲突替换") is True:
            e = entries[idx]
            e["内容"] = entry["内容"]
            e["updated_at"] = now
            e["replaced_count"] = int(e.get("replaced_count", 0)) + 1
            counts["conflict_replaced"] += 1
            branch = "conflict_replaced"
        elif bigram_jaccard(entries[idx].get("内容", ""), entry["内容"]) >= PREFERENCE_JACCARD_THRESHOLD:
            return "equivalent_skipped"  # 等价重复 — 跳过不写
        else:
            e = entries[idx]
            e["内容"] = entry["内容"]
            e["updated_at"] = now
            e["refined_count"] = int(e.get("refined_count", 0)) + 1
            counts["refined"] += 1
            branch = "refined"
        counts["entries_total"] = len(entries)
        _atomic_write_json(path, data)
        return branch


def verify_counts(store):
    """计数字段自校验 -> (ok, drift)。全部可复算恒等式:
    entries_total==len(entries); invalid_removed==len(失效删除台账);
    added==entries_total+invalid_removed; refined==Σrefined_count;
    conflict_replaced==Σreplaced_count (Σ 遍历在库条目 + 台账中被删条目)。
    (equivalent_skipped/oneoff_ignored 为纯事件计数, 状态不可复算, 故不入 counts)。
    drift: {字段: {stored, actual}}; store 为 DmMemory 句柄或已载入 dict。"""
    data = store if isinstance(store, dict) else _load_preferences(store)
    entries = data.get("entries") if isinstance(data.get("entries"), list) else []
    removed = data.get("removed") if isinstance(data.get("removed"), list) else []
    counts = data.get("counts") if isinstance(data.get("counts"), dict) else {}
    n = len(entries)

    def _sum(key):
        return sum(int(e.get(key, 0)) for e in list(entries) + list(removed)
                   if isinstance(e, dict))

    drift = {}

    def cmp(field, actual):
        stored = counts.get(field)
        if stored != actual:
            drift[field] = {"stored": stored, "actual": actual}

    cmp("entries_total", n)
    cmp("invalid_removed", len(removed))
    cmp("refined", _sum("refined_count"))
    cmp("conflict_replaced", _sum("replaced_count"))
    cmp("added", n + len(removed))
    return (not drift), drift
