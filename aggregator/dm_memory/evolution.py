# -*- coding: utf-8 -*-
"""
知识进化钩子 (批次4 builder-m3)
================================
should_store(signal): 4 信号白名单 (明确决策/新持久上下文/用户纠正/用户偏好) —
进度与临时状态一律不存不记。口径统一: aggregator/failure_memory (lessons.jsonl)
同守"可行动教训才入库"纪律, 白名单共同约束两库, 绝不为进度/临时状态膨胀记忆。
maybe_reflect(memory, signal) -> plan|None:
  - reflect 与 auto-create 互斥: 返回 plan 时调用方不得再自动创建该类记忆;
  - 同类信号自上次提议起 ≥REFLECT_THRESHOLD 次才提议 (阈值门控, 防失控膨胀);
  - 一切异常吞掉返回 None — 进化钩子永不致命 (验收⑤: 异常注入不影响主流程返回值)。
存储: <out_dir>/dm_memory/<safe_project>/evolution.jsonl (UTF-8, 原子写 tmp+os.replace)。
"""
import json
import os
import re
import sys
import threading
import time
import uuid

STORE_SIGNALS = ("明确决策", "新持久上下文", "用户纠正", "用户偏好")
REFLECT_THRESHOLD = 3
MAX_EVENTS = 200  # 口径同 failure_memory.MAX_LESSONS: 日志上限裁剪, 防无界膨胀

_PATH_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def _lock_for(path):
    # 同源配方: aggregator/version_store._lock_for 同款模式自实现 (不 import 私有函数)
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
    base = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def evolution_path(out_dir, project):
    # 存储布局 (设计 §3): <out_dir>/dm_memory/<safe_project>/evolution.jsonl
    return os.path.join(str(out_dir), "dm_memory", _safe_name(project), "evolution.jsonl")


def should_store(signal):
    """4 信号白名单判定: 命中 True; 进度/临时状态/未知/非字符串一律 False (不存不记)。"""
    try:
        return isinstance(signal, str) and signal.strip() in STORE_SIGNALS
    except Exception:
        return False


def _resolve_memory(memory):
    if isinstance(memory, dict):
        out_dir, project = memory.get("out_dir"), memory.get("project")
    else:
        out_dir, project = getattr(memory, "out_dir", None), getattr(memory, "project", None)
    if not out_dir:
        raise ValueError("memory 需含 out_dir (open_memory 句柄或等价 dict)")
    return str(out_dir), str(project or "项目")


def _read_events(path):
    """二进制逐行容错读 (R2 MED-3, 对齐 shot_cards/retrieval 口径): 非法 UTF-8 字节行
    降级为占位解码后走 json 跳过逻辑 — 损坏行诚实跳过不再完全静默 (stderr 一次性告警
    带跳过行数), 合法行照常消费, 信号阈值记账不被损坏锁死; 写路径不受损坏影响。"""
    events = []
    if not os.path.isfile(path):
        return events
    skipped = 0
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                skipped += 1  # 损坏行诚实跳过, 不伪造
                continue
            if isinstance(e, dict):
                events.append(e)
    if skipped:
        try:
            sys.stderr.write(
                f"[DirectorMaster] evolution.jsonl 有 {skipped} 行损坏, 已跳过 "
                f"(合法行照常消费): {path}\n")
        except Exception:
            pass
    return events


def _append_events(path, events):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    merged = (_read_events(path) + list(events))[-MAX_EVENTS:]
    tmp = path + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                for e in merged:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
            os.replace(tmp, path)  # 原子替换
            return
        except PermissionError as e2:  # Windows 并发占用重试
            last = e2
            time.sleep(0.03 * (attempt + 1))
    raise last if last else OSError(f"写入失败: {path}")


def maybe_reflect(memory, signal):
    """白名单信号记账; 同类信号自上次提议起 ≥REFLECT_THRESHOLD 次才提议 reflect plan。
    返回 plan dict (action=reflect, 不含时间戳 — 同输入同输出) 或 None。
    任何异常吞掉返回 None, 永不影响调用方主流程 (验收⑤)。"""
    try:
        if not should_store(signal):
            return None
        out_dir, project = _resolve_memory(memory)
        sig = str(signal).strip()
        path = evolution_path(out_dir, project)
        with _lock_for(path):
            since = 0
            for e in _read_events(path):
                if e.get("signal") != sig:
                    continue
                if e.get("event") == "signal":
                    since += 1
                elif e.get("event") == "reflect":
                    since = 0  # 上次已提议: 计数窗口重置
            since += 1
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            events = [{"event": "signal", "signal": sig, "同类计数": since, "ts": now}]
            plan = None
            if since >= REFLECT_THRESHOLD:
                plan = {"action": "reflect", "signal": sig,
                        "同类计数": since, "阈值": REFLECT_THRESHOLD}
                events.append({"event": "reflect", "signal": sig, "同类计数": since, "ts": now})
            _append_events(path, events)
            return plan
    except Exception:
        return None
