# -*- coding: utf-8 -*-
"""
批次4 builder-m2 — 锚点互链 (aggregator/dm_memory/anchor_link.py)
================================================================
两层分离纪律: aggregator/version_store = raw 内容权威 (只读使用, 语义不动);
本模块 = 蒸馏层锚点管理: 决策卡 card_id ↔ 版本 vid 互链 sidecar + adaptive 增量判定。
存储 (设计 §3, 本模块专属文件): <out_dir>/dm_memory/<safe_project>/anchors.json
  {"links": {card_id: [vid, ...]},                       # card_id -> [vid,...] 互链
   "adaptive": {"last_prompt_at": ms|None, "last_seen_vids": [vid,...]},
   "out_of_window": {card_id: [vid, ...]}}               # 窗口外报缺标记 (保留, 绝不删除)
adaptive 钉板: 自上次蒸馏提示以来新版本 >=5 或 距上次提示 >=24h 才再次提示
(sync_check 返回 should_prompt=True 即提示, 并记录提示时刻与已见版本后重新计数)。
窗口外钉板: 锚点 vid 不在 store.log 窗口内 → 计入 out_of_window 报缺,
锚点保留, 绝不删除。
"""
import json
import os
import re
import threading
import time

PROMPT_NEW_VERSIONS = 5                    # 自上次提示以来的新版本阈值
PROMPT_INTERVAL_MS = 24 * 60 * 60 * 1000   # 距上次提示的时间阈值 (24h)
_MAX_SEEN_VIDS = 64

_PATH_LOCKS = {}
_PATH_LOCKS_GUARD = threading.Lock()


def _lock_for(path):
    # 同源配方: aggregator/version_store._lock_for 同款模式自实现 (不 import 私有函数)
    with _PATH_LOCKS_GUARD:
        if len(_PATH_LOCKS) > 1024:
            for p in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(p, None)
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
    base = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _resolve_memory(memory):
    if isinstance(memory, dict):
        out_dir, project = memory.get("out_dir"), memory.get("project")
    else:
        out_dir, project = getattr(memory, "out_dir", None), getattr(memory, "project", None)
    if not out_dir:
        raise ValueError("memory 需含 out_dir (open_memory 句柄或等价 dict)")
    return str(out_dir), str(project or "项目")


def anchors_path(out_dir, project):
    # 存储布局 (设计 §3): <out_dir>/dm_memory/<safe_project>/anchors.json
    return os.path.join(str(out_dir), "dm_memory", _safe_name(project), "anchors.json")


def _str_list(v):
    return [str(x) for x in v] if isinstance(v, list) else []


def _load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = None  # 缺文件/损坏 → 空白 sidecar 起步 (原子写防 further 损坏)
    if not isinstance(data, dict):
        data = {}
    links = data.get("links") if isinstance(data.get("links"), dict) else {}
    adaptive = data.get("adaptive") if isinstance(data.get("adaptive"), dict) else {}
    oow = data.get("out_of_window") if isinstance(data.get("out_of_window"), dict) else {}
    return {
        "links": {str(k): _str_list(lst) for k, lst in links.items()},
        "adaptive": {
            "last_prompt_at": adaptive.get("last_prompt_at"),
            "last_seen_vids": _str_list(adaptive.get("last_seen_vids")),
        },
        "out_of_window": {str(k): _str_list(lst) for k, lst in oow.items()},
    }


def _atomic_write_json(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)  # 原子替换
            return
        except PermissionError as e:  # Windows 并发占用重试 (version_store._save 同款)
            last = e
            time.sleep(0.03 * (attempt + 1))
    raise last if last else OSError(f"写入失败: {path}")


def link_card(memory, card_id, vid):
    """锚点互链: card_id -> vid 追加 (幂等去重, 保序)。返回该卡当前 vid 列表。"""
    out_dir, project = _resolve_memory(memory)
    card_id, vid = str(card_id or "").strip(), str(vid or "").strip()
    if not card_id or not vid:
        raise ValueError("link_card 需要非空 card_id 与 vid")
    path = anchors_path(out_dir, project)
    with _lock_for(path):
        state = _load_state(path)
        lst = state["links"].setdefault(card_id, [])
        if vid not in lst:
            lst.append(vid)
        _atomic_write_json(path, state)
        return list(lst)


def sync_check(memory, store):
    """锚点对账 (store 为 version_store.open_store 句柄, 只读使用, 不改其语义)。
    返回 {"stale_cards", "new_versions", "should_prompt", "out_of_window"}:
    - out_of_window: 锚点 vid 已在 store.log 窗口之外 → 报缺, 锚点保留不删;
    - stale_cards: 存在窗口外证据的卡;
    - new_versions: 自上次蒸馏提示以来窗口内未见过的版本数;
    - should_prompt=True 即本次蒸馏提示 (adaptive: 新版本>=5 或 距上次>=24h),
      同时记录提示时刻与已见版本, 之后重新计数。
    """
    out_dir, project = _resolve_memory(memory)
    path = anchors_path(out_dir, project)
    with _lock_for(path):
        state = _load_state(path)
        log = store.log()  # store.log 窗口 (裁剪后的全窗口, 新→旧)
        vids = [str(v.get("id")) for v in log if v.get("id")]
        window = set(vids)
        oow = {card: [v for v in lst if v not in window]
               for card, lst in state["links"].items()
               if any(v not in window for v in lst)}
        stale_cards = sorted(oow)
        adaptive = state["adaptive"]
        last_at = adaptive.get("last_prompt_at")
        seen = set(adaptive.get("last_seen_vids") or [])
        new_versions = sum(1 for v in vids if v not in seen)
        now_ms = int(time.time() * 1000)
        try:
            aged = (last_at is not None
                    and now_ms - int(last_at) >= PROMPT_INTERVAL_MS)
        except (TypeError, ValueError):
            aged = False
        should_prompt = bool(vids) and (
            new_versions >= PROMPT_NEW_VERSIONS or aged)
        changed = False
        if should_prompt:
            adaptive["last_prompt_at"] = now_ms
            adaptive["last_seen_vids"] = vids[:_MAX_SEEN_VIDS]  # log 为新→旧, 截最新
            changed = True
        if oow != state.get("out_of_window"):
            state["out_of_window"] = oow
            changed = True
        if changed:
            _atomic_write_json(path, state)
        return {"stale_cards": stale_cards, "new_versions": new_versions,
                "should_prompt": should_prompt, "out_of_window": oow}
