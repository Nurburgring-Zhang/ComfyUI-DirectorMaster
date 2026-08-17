# -*- coding: utf-8 -*-
"""
DirectorMaster 版本存储 (V14.3-MERGED D4) — 真实磁盘持久化的项目版本控制
================================================================
V14.2 基线: JSON 全量存储 — 每版本存全部资产全文, 十轮测试产生 18-27MB/项目。
V14.3 D4 工程化 (验收: 单项目版本库 <2MB, 回滚仍逐字节还原):

- 增量存储: 资产内容按 sha256 存入共享 blob 池, 版本间相同内容只存一份
- 压缩: 版本库文件 gzip 压缩 (.versions.json.gz), 原子写入 (tmp + os.replace)
- 上限裁剪: 保留最近 MAX_VERSIONS 个版本, 超限删除最旧版本及其独占 blob
- 兼容迁移: 自动读取 V14.2 schema-1 明文 JSON 并升级为 schema-2
- rollback 真实还原: blob 内容原样写盘, sha256 校验逐字节一致

版本库文件位置: <out_dir>/_versions/<项目名>.versions.json.gz (旧: .versions.json)
"""
import os as _os
import json as _json
import gzip as _gzip
import time as _time
import hashlib as _hashlib
import threading as _threading

SCHEMA_VERSION = 2
MAX_CONTENT_CHARS = 2_000_000  # 单版本单资产内容上限 (超出只存摘要+文件名, 诚实标注)
MAX_VERSIONS = 20              # 版本数上限 — 超限裁剪最旧版本 (其独占 blob 一并回收)
MAX_STORE_BYTES = 200 * 1024 * 1024  # V14.3 审查P2: 版本库解压上限 (防 zipbomb 类 OOM)
VALID_STATES = ("DRAFT", "REVIEW", "APPROVED", "REJECTED", "ARCHIVED", "PUBLISHED")

# V14.3 F3: 并发控制 — 进程内按路径互斥锁 + 跨进程锁文件 (O_CREAT|O_EXCL 原子创建)
_PATH_LOCKS = {}
_PATH_LOCKS_GUARD = _threading.Lock()


def _lock_for(path):
    with _PATH_LOCKS_GUARD:
        # V14.3 (审查P2): 锁表防无界增长 — 超限时回收未持有的锁条目
        if len(_PATH_LOCKS) > 1024:
            for _p in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(_p, None)
        lk = _PATH_LOCKS.get(path)
        if lk is None:
            lk = _threading.Lock()
            _PATH_LOCKS[path] = lk
        return lk


class _FileLock:
    """跨进程锁: 原子创建 .lock 文件 + 持有者标识 (pid:token:ts).
    V14.3 (审查P1修复): 接管仅在 持有者进程已死 或 锁过期(>60s) 时发生;
    释放只删自己的锁 (内容==自己的 token), 防止误删接管者的锁。"""

    STALE_SECONDS = 60.0

    def __init__(self, dir_path, timeout=15.0):
        self.lock_path = _os.path.join(dir_path, ".store.lock")
        self.timeout = timeout
        self._token = "{}:{}".format(_os.getpid(), _hashlib.md5(
            "{}_{}".format(id(self), _time.time_ns()).encode()).hexdigest()[:12])
        self._held = False

    def _read_holder(self):
        try:
            with open(self.lock_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""

    def _holder_dead_or_stale(self):
        holder = self._read_holder()
        if not holder:
            return True
        parts = holder.split(":")
        if len(parts) < 3:
            return True
        try:
            pid = int(parts[0])
            ts = float(parts[2])
        except Exception:
            return True
        if _time.time() - ts > self.STALE_SECONDS:
            return True
        # 检查持有者进程是否存活 (同机跨进程)
        try:
            _os.kill(pid, 0)
            return False  # 存活 → 不可接管
        except ProcessLookupError:
            return True   # 进程已死 → 可接管
        except PermissionError:
            return False  # 存活但无权限 → 不可接管
        except Exception:
            return False

    def __enter__(self):
        deadline = _time.time() + self.timeout
        _os.makedirs(_os.path.dirname(self.lock_path), exist_ok=True)
        while True:
            try:
                fd = _os.open(self.lock_path, _os.O_CREAT | _os.O_EXCL | _os.O_WRONLY)
                with _os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write("{}:{}".format(self._token, _time.time()))
                self._held = True
                return self
            except FileExistsError:
                if self._holder_dead_or_stale():
                    # 持有者已死/锁过期 — 接管 (先删再重试创建)
                    try:
                        _os.remove(self.lock_path)
                    except Exception:
                        pass
                    import sys as _sl
                    _sl.stderr.write("[DirectorMaster] 版本库锁接管 (持有者进程已死或锁过期)\n")
                    continue
                if _time.time() > deadline:
                    import sys as _sl
                    _sl.stderr.write("[DirectorMaster] 版本库锁等待超时, 无锁继续 (可能竞态, 原子写保底)\n")
                    return self
                _time.sleep(0.02)
            except Exception:
                return self  # 锁机制本身失败不阻塞业务 (诚实降级)

    def __exit__(self, *exc):
        if self._held:
            # 只删自己的锁 — 若已被接管 (内容≠自己的token), 不动
            try:
                if self._read_holder().startswith(self._token):
                    _os.remove(self.lock_path)
            except Exception:
                pass
        return False


def _safe_name(s):
    import re as _re
    s = _re.sub(r'[\\/:*?"<>|]', "_", s or "项目")
    return s.strip()[:40] or "项目"


def _sha256(text):
    return _hashlib.sha256((text or "").encode("utf-8", errors="replace")).hexdigest()


def _now_ms():
    return int(_time.time() * 1000)


class VersionStore:
    """单项目版本库 — schema-2: blob 去重 + gzip 压缩 + 上限裁剪."""

    def __init__(self, out_dir, project):
        self.out_dir = out_dir
        self.project = project or "项目"
        self.dir = _os.path.join(out_dir, "_versions")
        self.path = _os.path.join(self.dir, _safe_name(self.project) + ".versions.json.gz")
        self._legacy_path = _os.path.join(self.dir, _safe_name(self.project) + ".versions.json")
        self.data = self._load()

    # ---------- 持久化 ----------
    def _blank(self):
        return {
            "schema": SCHEMA_VERSION,
            "project": self.project,
            "created": _time.strftime("%Y-%m-%d %H:%M:%S"),
            "head": None,
            "tags": {},
            "versions": {},
            "order": [],
            "blobs": {},
        }

    def _load(self):
        # schema-2 gzip (V14.3 审查P2: 解压上限防 zipbomb 类 OOM)
        if _os.path.isfile(self.path):
            try:
                with _gzip.open(self.path, "rt", encoding="utf-8") as f:
                    raw = f.read(MAX_STORE_BYTES + 1)
                if len(raw) > MAX_STORE_BYTES:
                    import sys as _lb_s
                    _lb_s.stderr.write("[DirectorMaster] 版本库超过解压上限, 视为损坏重建\n")
                else:
                    d = _json.loads(raw)
                    if isinstance(d, dict) and d.get("schema") == 2 and "versions" in d:
                        d.setdefault("blobs", {})
                        return d
            except Exception:
                pass
        # schema-1 明文迁移
        if _os.path.isfile(self._legacy_path):
            try:
                if _os.path.getsize(self._legacy_path) > MAX_STORE_BYTES:
                    import sys as _lb_s2
                    _lb_s2.stderr.write("[DirectorMaster] 旧版版本库超过大小上限, 跳过迁移\n")
                else:
                    with open(self._legacy_path, "r", encoding="utf-8") as f:
                        d = _json.load(f)
                    if isinstance(d, dict) and "versions" in d:
                        return self._migrate_v1(d)
            except Exception:
                pass
        return self._blank()

    def _migrate_v1(self, d):
        """V14.2 schema-1 (内联全文) → schema-2 (blob 去重). 内容逐字节保留."""
        nd = self._blank()
        nd["created"] = d.get("created", nd["created"])
        nd["head"] = d.get("head")
        nd["tags"] = dict(d.get("tags", {}))
        nd["order"] = list(d.get("order", []))
        for vid, v in (d.get("versions") or {}).items():
            files = {}
            for kind, entry in (v.get("files") or {}).items():
                content = entry.get("content", "") or ""
                sha = entry.get("sha256") or _sha256(content)
                nd["blobs"][sha] = content
                files[kind] = {
                    "file": entry.get("file", ""),
                    "chars": entry.get("chars", len(content)),
                    "sha256": sha,
                }
                if entry.get("content_truncated"):
                    files[kind]["content_truncated"] = True
            nv = dict(v)
            nv["files"] = files
            nd["versions"][vid] = nv
        return nd

    def _save(self):
        _os.makedirs(self.dir, exist_ok=True)
        tmp = self.path + ".tmp"
        # V14.3 F3: Windows 下并发写可能短暂占用文件 — 重试 5 次
        last_err = None
        for _attempt in range(5):
            try:
                with _gzip.open(tmp, "wt", encoding="utf-8", compresslevel=6) as f:
                    _json.dump(self.data, f, ensure_ascii=False, separators=(",", ":"))
                _os.replace(tmp, self.path)  # 原子替换
                return
            except PermissionError as _pe:
                last_err = _pe
                _time.sleep(0.03 * (_attempt + 1))
        raise last_err if last_err else OSError("版本库写入失败")

    def _mutate(self, fn):
        """V14.3 F3: 串行化 read-modify-write — 进程内锁 + 跨进程锁 + 写前重载最新数据.

        fn(data) 直接修改 self.data; 返回 fn 的返回值。
        """
        with _lock_for(self.path):
            with _FileLock(self.dir):
                self.data = self._load()  # 重载: 不覆盖其他进程/线程已提交的版本
                result = fn(self.data)
                self._save()
                return result

    def _trim(self):
        """上限裁剪: 删除最旧版本 + 回收独占 blob (保留版本的回滚能力不受影响)."""
        order = self.data.get("order", [])
        while len(order) > MAX_VERSIONS:
            old_vid = order.pop(0)
            old_v = self.data["versions"].pop(old_vid, None)
            if self.data.get("head") == old_vid:
                self.data["head"] = order[-1] if order else None
            # tags 指向被删版本时清除
            self.data["tags"] = {t: v for t, v in self.data.get("tags", {}).items() if v != old_vid}
            if old_v:
                # 仍被其他版本引用的 blob 不回收
                alive = set()
                for v in self.data["versions"].values():
                    for e in (v.get("files") or {}).values():
                        alive.add(e.get("sha256"))
                for e in (old_v.get("files") or {}).values():
                    sha = e.get("sha256")
                    if sha and sha not in alive:
                        self.data["blobs"].pop(sha, None)

    # ---------- 操作 ----------
    def commit(self, name, files, metadata=None, scores=None, notes=""):
        """提交版本. files: dict kind -> (filename, content). 返回 version_id.
        V14.3 F3: 并发安全 — 锁内重载最新数据再写入, 不丢失其他线程/进程的提交。
        V14.3 (审查P2修复): vid 在锁内生成 (含 order 长度盐), 同毫秒并发不碰撞。"""
        # 内容准备 (锁外纯计算)
        stored_files = {}
        total_chars = 0
        blobs_to_add = {}
        for kind, (fname, content) in files.items():
            content = content or ""
            total_chars += len(content)
            truncated = False
            if len(content) > MAX_CONTENT_CHARS:
                content = content[:MAX_CONTENT_CHARS]
                truncated = True
            sha = _sha256(content)
            blobs_to_add[sha] = content  # 增量: 相同内容只存一份
            entry = {"file": fname, "chars": len(content), "sha256": sha}
            if truncated:
                entry["content_truncated"] = True
            stored_files[kind] = entry
        version = {
            "name": name or "未命名版本",
            "timestamp": _time.strftime("%Y-%m-%d %H:%M:%S"),
            "state": "DRAFT",
            "metadata": metadata or {},
            "scores": scores or {},
            "notes": notes or "",
            "files": stored_files,
            "total_chars": total_chars,
        }

        def _do(data):
            vid = "v_{}_{}".format(_now_ms(), _sha256(
                "{}_{}_{}".format(name, len(data.get("order", [])), data.get("head") or ""))[:8])
            version["id"] = vid
            version["parent"] = data.get("head")
            data["blobs"].update(blobs_to_add)
            data["versions"][vid] = version
            data["order"].append(vid)
            data["head"] = vid
            self._trim()
            return vid

        return self._mutate(_do)

    def _content_of(self, entry):
        return self.data.get("blobs", {}).get(entry.get("sha256"), "")

    def get(self, vid):
        return self.data["versions"].get(vid)

    def log(self, limit=20):
        order = self.data.get("order", [])
        out = []
        for vid in reversed(order[-limit:]):
            v = self.data["versions"].get(vid)
            if v:
                out.append(v)
        return out

    def set_state(self, vid, state):
        if state not in VALID_STATES:
            return False

        def _do(data):
            v = data["versions"].get(vid)
            if v:
                v["state"] = state
                return True
            return False

        return self._mutate(_do)

    def tag(self, vid, tag_name):
        if not tag_name:
            return False

        def _do(data):
            if vid in data["versions"]:
                data["tags"][tag_name] = vid
                return True
            return False

        return self._mutate(_do)

    def resolve_ref(self, ref):
        """把 标签名/版本id/head 解析为版本 id."""
        if not ref or ref == "head":
            return self.data.get("head")
        if ref in self.data.get("tags", {}):
            return self.data["tags"][ref]
        if ref in self.data["versions"]:
            return ref
        cands = [vid for vid in self.data["versions"] if vid.startswith(ref)]
        return cands[0] if len(cands) == 1 else None

    def diff(self, ref1, ref2):
        v1 = self.data["versions"].get(self.resolve_ref(ref1) or "")
        v2 = self.data["versions"].get(self.resolve_ref(ref2) or "")
        if not v1 or not v2:
            return None
        kinds = sorted(set(list(v1["files"].keys()) + list(v2["files"].keys())))
        file_diffs = []
        for k in kinds:
            f1 = v1["files"].get(k)
            f2 = v2["files"].get(k)
            if f1 and f2:
                if f1["sha256"] == f2["sha256"]:
                    file_diffs.append({"资产": k, "变化": "无变化", "字符": f2["chars"]})
                else:
                    file_diffs.append({
                        "资产": k, "变化": "已修改",
                        "字符差": f2["chars"] - f1["chars"],
                        "v1文件": f1.get("file", ""), "v2文件": f2.get("file", ""),
                    })
            elif f1:
                file_diffs.append({"资产": k, "变化": "v2 中已删除", "字符": f1["chars"]})
            else:
                file_diffs.append({"资产": k, "变化": "v2 中新增", "字符": f2["chars"]})
        return {
            "v1": {"id": v1["id"], "name": v1["name"], "time": v1["timestamp"], "state": v1["state"]},
            "v2": {"id": v2["id"], "name": v2["name"], "time": v2["timestamp"], "state": v2["state"]},
            "总字符差": v2["total_chars"] - v1["total_chars"],
            "评分对比": {k: (v1["scores"].get(k), v2["scores"].get(k))
                       for k in sorted(set(list(v1["scores"].keys()) + list(v2["scores"].keys())))},
            "文件级差异": file_diffs,
        }

    def rollback(self, ref, write=True):
        """回滚到某版本 — blob 内容原样写盘 (sha256 校验逐字节). 返回 (new_vid, restored_files)."""
        vid = self.resolve_ref(ref)
        v = self.data["versions"].get(vid or "")
        if not v:
            return None, []
        restored = []
        files_for_commit = {}
        for kind, entry in v["files"].items():
            content = self._content_of(entry)
            # V14.3 F4: basename 消毒 — 防止被篡改的版本库文件借回滚写任意路径
            fname = _os.path.basename(str(entry.get("file") or ""))
            if write and content and fname:
                target = _os.path.join(self.out_dir, fname)
                try:
                    with open(target, "w", encoding="utf-8", newline="") as f:
                        f.write(content)
                    # 逐字节校验
                    with open(target, "r", encoding="utf-8", newline="") as f:
                        if _sha256(f.read()) == entry.get("sha256"):
                            restored.append(fname)
                except Exception:
                    pass
            files_for_commit[kind] = (fname, content)
        new_vid = self.commit(
            name="rollback→{}".format(v["name"]),
            files=files_for_commit,
            metadata={"rollback_from": vid, **v.get("metadata", {})},
            scores=v.get("scores", {}),
            notes="回滚自版本 {} ({})".format(vid, v["name"]),
        )
        return new_vid, restored

    def best(self, score_key="total", top_n=5):
        scored = []
        for vid, v in self.data["versions"].items():
            s = v.get("scores", {}).get(score_key)
            if isinstance(s, (int, float)):
                scored.append((s, v))
        scored.sort(key=lambda x: -x[0])
        return scored[:top_n]

    def summary(self):
        return {
            "project": self.project,
            "path": self.path,
            "head": self.data.get("head"),
            "version_count": len(self.data["versions"]),
            "blob_count": len(self.data.get("blobs", {})),
            "file_bytes": _os.path.getsize(self.path) if _os.path.isfile(self.path) else 0,
            "tags": dict(self.data.get("tags", {})),
        }


def open_store(out_dir, project):
    return VersionStore(out_dir, project)


def compute_archive_scores(assets_saved, total_chars):
    """从真实归档数据计算版本评分 (无捏造: 全部来自本次写盘结果)."""
    asset_count = len(assets_saved)
    completeness = round(min(1.0, asset_count / 5.0), 3)  # 5 类标准资产 (剧本/分镜/视频请求/手册/核心数据)
    volume = round(min(1.0, total_chars / 40000.0), 3)   # 4 万字符 ≈ 120min 完整交付体量
    total = round(completeness * 0.6 + volume * 0.4, 3)
    return {
        "资产数": asset_count,
        "总字符": total_chars,
        "完整度": completeness,
        "体量": volume,
        "total": total,
    }
