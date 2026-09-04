# -*- coding: utf-8 -*-
"""aggregator/eco/decision_log.py — append-only 决策审计轨 (批次5 builder-p3, V17.1.0)
====================================================================================
append_entry(log_path, category, subject, decision, options_considered=None)
    -> entry dict: 逐条追加 JSONL; 条目含 sha256 哈希链 (prev_hash 接龙, 创世条
    prev_hash="0"*64)。同 (category, subject) 已存在 → 新条目 revised=true 且旧
    条目 decision 移入新条目 options_considered (语义保留, design 验收⑥); 旧条目
    保留原样不动 (append-only, 不改写不删除任何既有行)。
verify_log(log_path) -> (ok: bool, errors: list[str])
    全链重算: 逐行重算哈希 (与写入同配方) + 核对 prev_hash 接龙与 seq 连续;
    任何一行损坏 (非 JSON/非对象/缺字段)/哈希不符/链断裂 → ok=False 且 errors
    逐条列出 (错误定位到行号)。文件不存在或空文件 → (True, []) 空链合法。
replay(log_path) -> list[entry]
    按链序重放全部条目; 文件不存在/空 → []。
attach_to_version(store, snapshot_name, log_ref, bridge_path=None) -> bridge dict
    version_store 只读挂接: 仅调用读取面 API (resolve_ref), 零写入 version_store;
    返回 {"snapshot", "log_ref", "entries"}; 挂接记录落盘由调用方负责 (可选
    bridge_path 传入时本函数代写该路径, 原子写 UTF-8)。

确定性纪律 (design §2): payload 绝不含时间戳/随机/locale —
  MED-2 统一配方 (append 造 hash 与 verify 复核 hash 共用同一函数 _hash_payload):
  payload = json.dumps(条目 dict 剔除 seq/prev_hash/hash 三字段后的全部业务内容
                       (含 revised 与任何未知/未来新增字段),
                       ensure_ascii=False, sort_keys=True, separators=(",",":"))
  hash    = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()
同一链状态 + 同一输入恒产生同一 hash (跨进程跨平台稳定); append 写入条目钉死
8 键 (seq/prev_hash/hash/category/subject/decision/options_considered/revised),
无其他不确定字段。

原子性: 读全文件 bytes + 追加后缀 + tmp 写 + os.replace 整体重写 — 追加前后
前缀逐字节一致 (纯追加可测); 无互斥锁 (篡改防线靠 verify_log 全链重算, 不靠
写锁, design §2 钉板)。MED-1 乐观并发: 落盘前重读当前 bytes 与构建基线逐字节
比对, 不一致则以最新全量重建再比对 (最多 3 轮, 禁 sleep), 仍冲突 → 中文
fail loud 拒写 (绝不静默覆盖丢条目); Win32 瞬时占用 PermissionError 的
range(5)+sleep 有界重试为其下保留层。零第三方依赖 (stdlib-only), UTF-8 显式编码。
"""
import hashlib
import itertools
import json
import os
import threading
import time

GENESIS_PREV_HASH = "0" * 64

# MED-2: 哈希排除字段 (仅此三字段不进 payload; revised/未知字段全进)
_HASH_EXCLUDED_FIELDS = ("seq", "prev_hash", "hash")
# payload 业务四字段 (append 输入面; 与 _ENTRY_FIELDS 定义共用)
_PAYLOAD_FIELDS = ("category", "subject", "decision", "options_considered")
# 条目完整字段 (append 写入钉死 8 键, 无时间戳等不确定字段)
_ENTRY_FIELDS = ("seq", "prev_hash", "hash") + _PAYLOAD_FIELDS + ("revised",)

# MED-1 乐观并发重试上限 (重读重建轮数, 禁 sleep; 3 轮仍冲突 → fail loud)
_CONFLICT_MAX_RETRIES = 3

# R2A-01: tmp 唯一化序列 (进程内单调计数, CPython next() 原子)。tmp 路径由
# pid + 线程 id + 该序号三元组构成, 保证**每次调用唯一** — 同进程两线程同时
# 追加同一 JSONL 不再共用同一 tmp (共用即互踩 → 盘上撕裂写)。
_TMP_SEQ = itertools.count()


def _hash_payload(entry):
    """MED-2 统一哈希 payload (append_entry 造 hash 与 verify_log 复核 hash 唯一
    共用配方, 杜绝两处口径漂移): 覆盖除 seq/prev_hash/hash 三字段外的全部业务
    内容 (含 revised 与任何未知/未来新增字段), sort_keys + 紧凑分隔符 +
    ensure_ascii=False, 确定性 (无时间戳/无随机/无 locale/无字典序不稳因素)。"""
    return json.dumps(
        {k: v for k, v in entry.items() if k not in _HASH_EXCLUDED_FIELDS},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _entry_hash(prev_hash, payload):
    """sha256(prev_hash + payload), 输入统一 utf-8 编码。"""
    return hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()


def _dump_line(entry):
    return json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _read_bytes(log_path):
    if not os.path.isfile(log_path):
        return b""
    last = None
    for _attempt in range(5):
        try:
            with open(log_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return b""
        except PermissionError as exc:
            # Win32 瞬时占用有界重试 (range(5)+sleep, 保留层 — 并发 os.replace
            # 执行窗口内 open 会瞬时 ERROR_ACCESS_DENIED); 穷尽仍失败 → MED-1
            # 中文 fail loud, 不裸 traceback 也不吞 (持久故障诚实上报)
            last = exc
            time.sleep(0.03 * (_attempt + 1))
    raise RuntimeError("decision_log 读取失败 (文件被占用/权限不足, fail loud 不静默): %s (%s)"
                       % (log_path, last))


def _tmp_path(log_path):
    """调用级唯一 tmp 路径 (R2A-01: pid + 线程 id + 进程内单调序号, 每次调用
    唯一 — 同进程任意两线程/同线程多轮重试亦互不踩踏 tmp, 杜绝并发撕裂写;
    tmp 名短暂存在不落产物, 产物内容仍确定性)。"""
    return "%s.tmp.%d.%d.%d" % (log_path, os.getpid(), threading.get_ident(),
                                next(_TMP_SEQ))


def _prepare_tmp(tmp, new_bytes):
    """tmp 写 (Win32 瞬时占用 range(5)+sleep 有界重试, dm_memory 同配方保留层)。"""
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "wb") as f:
                f.write(new_bytes)
            return
        except PermissionError as exc:
            last = exc
            time.sleep(0.03 * (attempt + 1))
    raise last


def _replace_tmp(log_path, tmp, base):
    """os.replace 原子落盘 + Win32 瞬时占用有界重试 (range(5)+sleep, 保留层)。
    每次重试前漂移复查: 期间文件被并发写过 (与基线不一致) → 放弃本轮 replace
    返回 False 交回乐观层以最新全量重建 (绝不带陈旧内容落盘覆盖他人); 5 次占用
    仍未落且无漂移 → raise (诚实上报, 不吞)。"""
    last = None
    for attempt in range(5):
        try:
            os.replace(tmp, log_path)
            return True
        except PermissionError as exc:
            last = exc
            time.sleep(0.03 * (attempt + 1))
            try:
                if _read_bytes(log_path) != base:
                    return False
            except RuntimeError:
                return False
    raise last


def _replace_plain(path, tmp):
    """os.replace 原子落盘 + Win32 瞬时占用有界重试 (range(5)+sleep, 保留层) —
    供 bridge 等派生快照产物使用 (R2A-03)。派生产物每次写入均为全量内容, 并发
    写方后写覆盖先写为既定可接受语义, 故不做乐观层漂移复查; 5 次占用穷尽 →
    raise 诚实上报 (不吞)。"""
    last = None
    for _attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError as exc:
            last = exc
            time.sleep(0.03 * (_attempt + 1))
    raise last


def _split_lines(raw):
    """bytes -> 文本行列表 (UTF-8 strict); 文件末尾单个收尾换行不产生空尾行。"""
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _parse_entries(raw):
    """严格解析: 返回 (entries, None) 或 (None, 错误消息)。append/replay 用
    fail-fast 语义 — 损坏日志拒绝追加/重放 (诚实不静默)。"""
    try:
        lines = _split_lines(raw)
    except UnicodeDecodeError as exc:
        return None, "UTF-8 解码失败: %s" % exc
    entries = []
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            return None, "第 %d 行为空白行 (非合法 JSONL)" % i
        try:
            obj = json.loads(line)
        except ValueError as exc:
            return None, "第 %d 行非 JSON: %s" % (i, exc)
        if not isinstance(obj, dict):
            return None, "第 %d 行非 JSON 对象 (实际 %s)" % (i, type(obj).__name__)
        missing = [k for k in _ENTRY_FIELDS if k not in obj]
        if missing:
            return None, "第 %d 行缺字段: %s" % (i, ",".join(missing))
        entries.append(obj)
    return entries, None


def append_entry(log_path, category, subject, decision, options_considered=None):
    """追加一条决策 (append-only)。返回新条目 dict。

    MED-1 乐观并发: 读全量 bytes 构建新行 → 落盘前重读当前 bytes 逐字节比对,
    不一致则以最新全量重建 (最多 3 轮, 禁 sleep), 仍冲突 → 中文 fail loud 拒写
    (绝不静默覆盖丢条目)。LOW-2: category/subject/decision strip 后为空 →
    中文 ValueError 拒绝 (空决策不入链)。
    诚实限制: 跨进程并发存在不可消除的比对→replace 窗口 (无锁设计的既定接受项,
    检测到的冲突一律中文 fail loud; 主部署为 ComfyUI 单进程节点面)。
    """
    if options_considered is None:
        opts = []
    elif isinstance(options_considered, (list, tuple)):
        opts = [str(x) for x in options_considered]
    else:
        raise ValueError(
            "options_considered 须为 list[str] 或 None, 实际 %s"
            % type(options_considered).__name__)

    for _fname, _val in (("category", category), ("subject", subject),
                         ("decision", decision)):
        if not ("" if _val is None else str(_val)).strip():
            raise ValueError("decision_log %s 必填: None/空串/纯空白 — 拒绝追加空决策条目"
                             % _fname)

    log_path = str(log_path)

    base = _read_bytes(log_path)
    for _ in range(_CONFLICT_MAX_RETRIES):
        entries, err = _parse_entries(base)
        if err is not None:
            raise ValueError("decision_log 损坏, 拒绝追加 (append-only 纪律): %s" % err)

        # 同 (category, subject) 扫描 (design 验收⑥): 新条目 revised=true,
        # 旧条目 decision 移入 options_considered (语义保留); 旧条目行原样不动。
        # (每轮重建, 不得跨轮累积 — MED-1 重试语义)
        revised = False
        prev_decision = None
        for e in entries:
            if e.get("category") == category and e.get("subject") == subject:
                revised = True
                prev_decision = e.get("decision")
        iter_opts = ([prev_decision] + opts) if revised else list(opts)

        prev_hash = entries[-1]["hash"] if entries else GENESIS_PREV_HASH
        entry = {
            "seq": len(entries) + 1,
            "prev_hash": prev_hash,
            "category": category,
            "subject": subject,
            "decision": decision,
            "options_considered": iter_opts,
            "revised": revised,
        }
        # MED-2: hash 覆盖除 seq/prev_hash/hash 外全部业务内容 (与 verify_log 同一函数)
        entry["hash"] = _entry_hash(prev_hash, _hash_payload(entry))
        new_bytes = base + (_dump_line(entry) + "\n").encode("utf-8")

        d = os.path.dirname(log_path)
        if d:
            os.makedirs(d, exist_ok=True)
        tmp = _tmp_path(log_path)                 # R2A-01: 每轮重取唯一 tmp (重试间互不踩踏)
        _prepare_tmp(tmp, new_bytes)              # tmp 先行 (比对与 replace 相邻)
        current = _read_bytes(log_path)           # MED-1: os.replace 前重读逐字节比对
        if current == base:
            if not _replace_tmp(log_path, tmp, base):
                base = _read_bytes(log_path)      # 占用重试期间被并发写: 以最新全量重建
                continue
            post = _read_bytes(log_path)          # 写后单次核验 (replace 后立即重读): 本行必须在场
            if post.startswith(new_bytes):
                return entry
            base = post                            # replace 后被并发覆盖: 以最新重建
            continue
        base = current  # 期间被并发写入过: 以最新全量为基线重建 (无 sleep)
    raise RuntimeError(
        "decision_log 检测到并发写入冲突，已放弃本次写入以防覆盖丢失: %s (重读重建 %d 轮仍冲突)"
        % (log_path, _CONFLICT_MAX_RETRIES))


def verify_log(log_path):
    """全链核验: 逐行重算哈希 (同写入配方) + prev_hash 接龙 + seq 连续。
    返回 (ok, errors); errors 逐条列出且定位行号。文件不存在/空 → (True, [])。"""
    raw = _read_bytes(log_path)
    if not raw:
        return True, []  # 文件不存在或空文件: 空链合法
    try:
        lines = _split_lines(raw)
    except UnicodeDecodeError as exc:
        return False, ["UTF-8 解码失败: %s" % exc]

    errors = []
    expected_prev = GENESIS_PREV_HASH
    expected_seq = 1
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append("第 %d 行为空白行 (非合法 JSONL)" % i)
            continue
        try:
            obj = json.loads(line)
        except ValueError as exc:
            errors.append("第 %d 行非 JSON: %s" % (i, exc))
            continue
        if not isinstance(obj, dict):
            errors.append("第 %d 行非 JSON 对象 (实际 %s)" % (i, type(obj).__name__))
            continue
        missing = [k for k in _ENTRY_FIELDS if k not in obj]
        if missing:
            errors.append("第 %d 行缺字段: %s" % (i, ",".join(missing)))
            continue
        if obj.get("seq") != expected_seq:
            errors.append("第 %d 行 seq 断裂 (期望 %d, 实际 %r)"
                          % (i, expected_seq, obj.get("seq")))
            continue
        if obj.get("prev_hash") != expected_prev:
            errors.append("第 %d 行链断裂 (prev_hash 不接龙: 期望 %s, 实际 %s)"
                          % (i, expected_prev, obj.get("prev_hash")))
            continue
        # MED-2: 与 append_entry 共用 _hash_payload (覆盖 revised 与未知字段)
        recomputed = _entry_hash(obj["prev_hash"], _hash_payload(obj))
        if recomputed != obj.get("hash"):
            errors.append("第 %d 行哈希不符 (重算 %s, 记录 %s)"
                          % (i, recomputed, obj.get("hash")))
            continue
        expected_prev = obj["hash"]
        expected_seq += 1
    return (len(errors) == 0), errors


def replay(log_path):
    """按链序重放全部条目 (文件不存在/空 → [])。损坏日志 fail loud。"""
    raw = _read_bytes(log_path)
    if not raw:
        return []
    entries, err = _parse_entries(raw)
    if err is not None:
        raise ValueError("decision_log 损坏, 无法重放: %s" % err)
    return entries


def attach_to_version(store, snapshot_name, log_ref, bridge_path=None):
    """version_store 只读挂接: 仅调用读取面 API (resolve_ref), 零改写 store。
    返回 bridge dict {"snapshot","log_ref","entries"}; bridge_path 传入时把
    挂接记录原子落盘到该路径 (调用方自有落盘之外的便捷口, 不碰 version_store)。"""
    vid = store.resolve_ref(snapshot_name)
    if not vid:
        raise ValueError("快照不存在, 拒绝挂接: %r" % (snapshot_name,))
    entries = replay(log_ref)
    bridge = {
        "snapshot": snapshot_name,
        "log_ref": str(log_ref),
        "entries": len(entries),
    }
    if bridge_path:
        d = os.path.dirname(str(bridge_path))
        if d:
            os.makedirs(d, exist_ok=True)
        # R2A-03: bridge 落盘改走调用级唯一 tmp + 占用重试层 + os.replace 原子写
        # (旧实现固定 ".tmp" 后缀 — 并发挂接同一 bridge_path 时两写方互踩 tmp)。
        blob = json.dumps(bridge, ensure_ascii=False, sort_keys=True,
                          indent=2).encode("utf-8")
        tmp = _tmp_path(str(bridge_path))
        _prepare_tmp(tmp, blob)
        _replace_plain(str(bridge_path), tmp)
    return bridge
