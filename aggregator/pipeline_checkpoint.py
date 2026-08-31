# -*- coding: utf-8 -*-
"""
DirectorMaster 产物检查点 (V16.7-MERGED D4) — 断点续跑的真实落盘状态
================================================================
设计: design_batch3.md §4 D4 · owner: 批次3 A3 · 消费方: D6 review_engine (B1)

CheckpointStore(root_dir) 把"某管线的某步骤已用某输入完成"记录为磁盘 JSON 清单,
进程中断/崩溃后重入时可据此跳过已完成步骤 (断点续跑), 输入变化时自动判定该步失效。

三函数 (接口冻结 — B1 的 review_engine 将消费, 签名不得改):

- done(pipeline_id, step, input_hash) -> bool
    True  = 清单中该步存在且 input_hash 相同 → 可跳过 (断点续跑)
    False = 该步未做过 / input_hash 变化 (该步失效, 需重算)
- mark_done(pipeline_id, step, input_hash, artifact_ref=None) -> None
    记录该步完成 (同步骤重复调用 = 覆盖旧记录); artifact_ref 为该步产物引用
    (文件名/相对路径等字符串), 原样存入清单供恢复后取用。
- clear(pipeline_id) -> int
    清空该管线全部检查点 (返回清除的步骤数), 之后所有步骤重算。
- step_done(...) 为 done 的别名 (设计文档 §4 命名, 行为逐字节一致)。

清单落盘 (确定性):
  文件: <root_dir>/<编码后 pipeline_id>.checkpoint.json
  内容: {"pipeline_id": <原名>, "schema": 1, "steps": {<step>: {"input_hash": ..,
        "artifact_ref": ..|null}}}, json.dumps(sort_keys=True) — 无时间戳字段,
  同状态逐字节一致; 写入 tmp + os.replace 原子替换 (Win32 并发加固: replace 遇
  瞬时共享冲突 — 杀软/索引器/跨进程读者短暂持有目标句柄 — 有界重试 ≤5 次,
  每次 10ms; 耗尽后抛最后一次异常, 诚实失败不吞错)。

线程安全: 模块级按清单路径互斥锁 (同 aggregator/version_store 的 _lock_for 模式);
  同进程多实例/多线程对同一管线操作串行化。跨进程不保证 (需求口径为 threading.Lock)。

路径消毒 (白名单):
  pipeline_id / step / input_hash 必须为非空 str, 且不得含控制字符、路径分隔符
  (\\ / :)、Windows 保留字符 (* ? " < > |) 或 ".." — 违者 ValueError (诚实报错)。
  清单文件名对一切非 [0-9A-Za-z] 字符做 _x%06x 定宽转义 (可逆 + 不可穿越,
  转义序列定宽故解码无歧义); 转义后命中 Windows 保留设备名 (CON/NUL/COM1..) 加 p_ 前缀;
  超长 (编码 >120 字符) 截断为前 96 字符 + "-" + sha256 前 16 位 (确定性)。

诚实降级: 清单文件缺失或 JSON 损坏 → 视为无检查点 (done 全 False), 不抛错不伪造;
  下一次 mark_done 以合法清单自愈。done() 只读不删除 — hash 不匹配的旧记录保留
  至 mark_done 覆盖或 clear 清除, 行为可预测。
"""
import os as _os
import json as _json
import re as _re
import hashlib as _hashlib
import threading as _threading
import time as _time

SCHEMA_VERSION = 1
_MANIFEST_SUFFIX = ".checkpoint.json"

# os.replace Win32 并发加固: 瞬时共享冲突 (PermissionError/OSError) 有界重试
_REPLACE_MAX_RETRIES = 5      # ≤5 次尝试 (含首次)
_REPLACE_RETRY_DELAY_S = 0.01  # 每次 10ms

# 路径白名单之外的字符: 控制字符 + 路径元字符 (出现即拒绝 — 含穿越/逃逸向量)
_UNSAFE_TOKEN_RE = _re.compile(u"[\x00-\x1f\x7f/\\\\:*?\"<>|]")

# Windows 保留设备名 (大小写不敏感) — 转义后无 '.', 故整名即 stem
_WIN_RESERVED = frozenset(
    ["CON", "PRN", "AUX", "NUL"] +
    ["COM%d" % i for i in range(1, 10)] + ["LPT%d" % i for i in range(1, 10)]
)

# ---------- 并发控制 (模块级按清单路径互斥, 仿 version_store._lock_for) ----------
_PATH_LOCKS = {}
_PATH_LOCKS_GUARD = _threading.Lock()


def _lock_for(path):
    with _PATH_LOCKS_GUARD:
        # 锁表防无界增长: 回收当前未被持有的条目
        if len(_PATH_LOCKS) > 1024:
            for _p in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(_p, None)
        lk = _PATH_LOCKS.get(path)
        if lk is None:
            lk = _threading.Lock()
            _PATH_LOCKS[path] = lk
        return lk


def _sanitize_token(value, field):
    """白名单消毒: 非 str/空串/含路径元字符或控制字符/'..' → ValueError (诚实报错).

    通过校验的原值 (仅去首尾空白) 返回 — 中文等 Unicode 词字符合法可用。
    """
    if not isinstance(value, str):
        raise ValueError(
            "pipeline_checkpoint: %s 必须是 str, 实际 %s" % (field, type(value).__name__))
    v = value.strip()
    if not v:
        raise ValueError("pipeline_checkpoint: %s 不能为空" % field)
    if ".." in v:
        raise ValueError(
            "pipeline_checkpoint: %s 含 '..' (路径穿越风险), 已拒绝: %r" % (field, value))
    m = _UNSAFE_TOKEN_RE.search(v)
    if m:
        raise ValueError(
            "pipeline_checkpoint: %s 含非白名单字符 %r (控制字符/路径分隔符/保留字符), 已拒绝"
            % (field, m.group(0)))
    return v


def _encode_filename(value):
    """非 [0-9A-Za-z] 字符 → '_x%06x' 定宽转义: 文件名安全 + 可逆 + 无解析歧义."""
    out = []
    for ch in value:
        if ("0" <= ch <= "9") or ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            out.append(ch)
        else:
            out.append("_x%06x" % ord(ch))
    enc = "".join(out)
    if enc.upper() in _WIN_RESERVED:
        enc = "p_" + enc
    if len(enc) > 120:
        enc = enc[:96] + "-" + _hashlib.sha256(
            value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return enc


def _atomic_replace(tmp, path):
    """tmp → path 原子替换, Win32 并发加固版。

    os.replace 在 Windows 上遇瞬时共享冲突 (目标文件被杀软/索引器/跨进程读者
    短暂持有句柄 → PermissionError/OSError) 会失败; 此处有界重试 ≤
    _REPLACE_MAX_RETRIES 次, 每次 sleep _REPLACE_RETRY_DELAY_S (10ms, 固定
    无随机抖动 — 确定性口径)。重试耗尽后抛最后一次异常 (诚实失败, 不吞错);
    POSIX 上 replace 本身原子, 首次即成功, 行为不变。
    """
    last_exc = None
    for attempt in range(_REPLACE_MAX_RETRIES):
        try:
            _os.replace(tmp, path)
            return
        except (PermissionError, OSError) as exc:  # PermissionError ⊂ OSError
            last_exc = exc
            if attempt + 1 < _REPLACE_MAX_RETRIES:
                _time.sleep(_REPLACE_RETRY_DELAY_S)
    raise last_exc


class CheckpointStore(object):
    """管线步骤检查点 — 磁盘 JSON 清单, 断点续跑 + 输入 hash 失效判定."""

    def __init__(self, root_dir):
        if not isinstance(root_dir, str) or not root_dir.strip():
            raise ValueError(
                "pipeline_checkpoint: root_dir 必须是非空字符串, 实际 %r" % (root_dir,))
        self.root_dir = _os.path.abspath(_os.path.expanduser(root_dir))

    # ---------- 路径 ----------
    def manifest_path(self, pipeline_id):
        """该管线的清单文件绝对路径 (pipeline_id 先过白名单消毒再编码)."""
        pid = _sanitize_token(pipeline_id, "pipeline_id")
        return _os.path.join(self.root_dir, _encode_filename(pid) + _MANIFEST_SUFFIX)

    # ---------- 读写清单 ----------
    def _read_manifest(self, path):
        """读清单; 缺失/损坏 → None (视为无检查点, 诚实降级)."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = _json.load(f)
        except Exception:
            return None
        if isinstance(d, dict) and isinstance(d.get("steps"), dict):
            return d
        return None

    def _write_manifest(self, path, data):
        _os.makedirs(self.root_dir, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            _json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=2)
        _atomic_replace(tmp, path)  # 原子替换 (Win32 瞬时冲突有界重试)

    # ---------- 接口冻结三函数 ----------
    def done(self, pipeline_id, step, input_hash):
        """该步可否跳过: 存在且 input_hash 相同 → True; 否则 False (只读不删)."""
        pid = _sanitize_token(pipeline_id, "pipeline_id")
        st = _sanitize_token(step, "step")
        h = _sanitize_token(input_hash, "input_hash")
        path = _os.path.join(self.root_dir, _encode_filename(pid) + _MANIFEST_SUFFIX)
        with _lock_for(path):
            data = self._read_manifest(path)
        if not data:
            return False
        rec = data.get("steps", {}).get(st)
        return isinstance(rec, dict) and rec.get("input_hash") == h

    def mark_done(self, pipeline_id, step, input_hash, artifact_ref=None):
        """记录该步完成 (覆盖旧记录) 并原子落盘. artifact_ref 仅接受 str 或 None."""
        pid = _sanitize_token(pipeline_id, "pipeline_id")
        st = _sanitize_token(step, "step")
        h = _sanitize_token(input_hash, "input_hash")
        if artifact_ref is not None and not isinstance(artifact_ref, str):
            raise ValueError(
                "pipeline_checkpoint: artifact_ref 必须是 str 或 None, 实际 %s"
                % type(artifact_ref).__name__)
        path = _os.path.join(self.root_dir, _encode_filename(pid) + _MANIFEST_SUFFIX)
        with _lock_for(path):
            data = self._read_manifest(path) or {
                "schema": SCHEMA_VERSION, "pipeline_id": pid, "steps": {}}
            data["schema"] = SCHEMA_VERSION
            data["pipeline_id"] = pid
            steps = data.get("steps")
            if not isinstance(steps, dict):
                steps = data["steps"] = {}
            steps[st] = {"input_hash": h, "artifact_ref": artifact_ref}
            self._write_manifest(path, data)
        return None

    def clear(self, pipeline_id):
        """清空该管线全部检查点 (删除清单文件), 返回清除的步骤数; 不存在的管线 → 0."""
        pid = _sanitize_token(pipeline_id, "pipeline_id")
        path = _os.path.join(self.root_dir, _encode_filename(pid) + _MANIFEST_SUFFIX)
        with _lock_for(path):
            data = self._read_manifest(path)
            n = 0
            if data:
                steps = data.get("steps") or {}
                n = len([k for k, v in steps.items() if isinstance(v, dict)])
                try:
                    _os.remove(path)
                except OSError:
                    pass
            return n

    # ---------- 设计文档 §4 命名兼容别名 ----------
    def step_done(self, pipeline_id, step, input_hash):
        """done() 的别名 (design §4 命名) — 行为一致, 便于消费方二选一."""
        return self.done(pipeline_id, step, input_hash)

    # ---------- 只读辅助 (非冻结接口, 供测试/消费方检视) ----------
    def steps(self, pipeline_id):
        """该管线全部步骤记录的浅拷贝快照: {step: {"input_hash": .., "artifact_ref": ..}}."""
        pid = _sanitize_token(pipeline_id, "pipeline_id")
        path = _os.path.join(self.root_dir, _encode_filename(pid) + _MANIFEST_SUFFIX)
        with _lock_for(path):
            data = self._read_manifest(path)
        out = {}
        if data:
            for k, v in (data.get("steps") or {}).items():
                if isinstance(v, dict):
                    out[k] = dict(v)
        return out
