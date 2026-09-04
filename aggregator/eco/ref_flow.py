# -*- coding: utf-8 -*-
"""aggregator/eco/ref_flow.py — 参考素材流: 来源登记 + 解构三列表 + 契约注入
(批次5 builder-p2, V17.1.0)
================================================================================
register_ref(out_dir, ref_id, source, authorization, project, **kw)
    来源批次登记: authorization (授权声明) 与 source (来源描述) 必填, 缺任一
    (None/空串/纯空白) → {"ok": False, "errors": [...]} fail loud 不落盘。
    法务边界常量 LEGALESE ("只学手法不复制表达"语义句) 写进台账每条记录
    (落盘边界, 非口头约定)。台账 <out_dir>/eco/ref_ledger/<safe_project>.json
    (UTF-8 原子写 tmp+os.replace + MED-1 乐观并发: 写前重读逐字节比对, 冲突
    有界重建重试, 3 轮仍冲突中文 fail loud 绝不静默覆盖丢数据), 按 ref_id 键
    幂等覆盖; 三列表/谱系锚等扩展字段经 **kw 透传入条目 (media_* 控制键除外,
    见 _resolve_media)。
deconstruct(notes) -> {"手法": [...], "参考实现": [...], "取舍": [...]}
    用户笔记逐行确定性归类 (无 LLM): 含 手法/technique → 手法列; 含 实现/做法/
    how → 参考实现列; 含 取舍/放弃/tradeoff 及无法归类行 → 取舍列 (不丢行);
    空白行丢弃; 三键恒齐备。
inject_refs(contract, refs) -> contract'
    批次6 storyboard_contract refs[] 槽位注入: 浅拷贝后只加 "refs" 键, 既有键
    (含嵌套值) 逐字节不动; 已有 refs 键则追加不去重; refs 空列表 → 原样返回
    (零漂移, 不加键, 批次4 T7 additive 口径)。
anchor_lineage(ref_entry, lineage_root_dir) -> dict
    谱系源登记: <lineage_root_dir>/ref_lineage.jsonl 追加一行 {ref_id, ts: None,
    lineage_kind, asset_id}; lineage_kind 对齐 asset_master 派生谱系条目 kind
    命名风格 (类型: 母版/派生 中文复合词) → "参考源" (语义 ref_source);
    ts 恒 None (不写时间戳, 确定性纪律)。

确定性: 无随机/无时间戳/无 locale/无 dict 迭代序依赖 (json.dumps 统一
ensure_ascii=False + sort_keys=True)。媒体引用解析复用 aggregator.ref_media.
resolve_ref 语义口径 (IMAGE 优先/路径回退, 只 import 不改)。stdlib-only,
零网络零 LLM。
"""
import hashlib
import itertools
import json
import os
import re
import threading
import time

from aggregator.ref_media import resolve_ref as _resolve_ref  # noqa: F401 语义口径对齐 (只 import 不改)

ECO_REF_SCHEMA_VERSION = 1

# 法务边界 (落盘进台账每条记录, 非口头约定): "只学手法不复制表达" 语义句。
LEGALESE = ("法务边界：只学手法不复制表达——参考素材仅限手法学习与结构参考使用，"
            "禁止复制来源的表达层内容 (文本/画面/音频原样)，派生产物不得替代来源作品。")

# 谱系源条目 kind — 同款对齐 asset_master 派生谱系词汇命名风格
# (aggregator/asset_master.py 谱系条目 类型: "母版"/"派生", 四态: 完整锚定/母版缺失/
# 派生缺失/母版已更新待同步, 均中文复合词) → 参考来源条目同款命名 "参考源"。
LINEAGE_KIND_REF_SOURCE = "参考源"

LINEAGE_FILENAME = "ref_lineage.jsonl"

# register_ref **kw 控制键 (媒体解析参数, 只作解析输入, 不透传进台账条目)
_KW_CONTROL = ("media_kwargs", "media_img_key", "media_path_key", "media_tag")

# 乐观并发重试上限 (MED-1: 重读重建轮数, 禁 sleep 等待; 3 轮仍冲突 → fail loud)
_CONFLICT_MAX_RETRIES = 3

# R2A-01: tmp 唯一化序列 (进程内单调计数, CPython next() 原子)。tmp 路径由
# pid + 线程 id + 该序号三元组构成, 保证**每次调用唯一** — 同进程两线程同时写
# 同一目标文件不再共用同一 tmp (共用即互踩 → 盘上撕裂写)。
_TMP_SEQ = itertools.count()

# _optimistic_write / _atomic_write_json 的 base 缺省哨兵 (= 以写前当前 bytes 为基线)
_UNSET = object()

_UNSAFE_FILENAME_RE = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')


# ---------- 基础件: safe_name / 原子写 ----------
def _safe_name(s):
    """safe_project 本地实现 — 照抄 episode_pipeline/pipeline.py safe_name 配方
    (同款自实现, 不 import pipeline 以免拉起重依赖): 非法字符→"_" + strip + 截40;
    替换有信息丢失 / 含 ASCII (NTFS 大小写折叠) / 尾部 "."或" " 任一命中 → 追加
    原 raw 的 sha1 前 8 位。同一 raw 恒映射同一文件名, 不同 raw 不共用。"""
    raw = str(s or "")
    base = _UNSAFE_FILENAME_RE.sub("_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _read_file_bytes(path):
    """读全量 bytes (MED-1 乐观并发基线); 文件不存在 → None。
    PermissionError 先走 Win32 瞬时占用有界重试 (range(5)+sleep, 保留层 —
    并发 os.replace 执行窗口内 open 会瞬时 ERROR_ACCESS_DENIED), 重试穷尽
    仍失败 → 中文 fail loud RuntimeError (不裸崩不吞, 持久故障仍然诚实上报)。"""
    last = None
    for _attempt in range(5):
        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except PermissionError as exc:
            last = exc
            time.sleep(0.03 * (_attempt + 1))
    raise RuntimeError("台账读取失败 (文件被占用/权限不足, fail loud 不静默): %s (%s)"
                       % (path, last))


def _tmp_path(path):
    """调用级唯一 tmp 路径 (R2A-01: pid + 线程 id + 进程内单调序号, 每次调用
    唯一 — 同进程任意两线程/同线程多轮重试亦互不踩踏 tmp, 杜绝并发撕裂写;
    tmp 名短暂存在不落产物, 产物内容仍确定性)。"""
    return "%s.tmp.%d.%d.%d" % (path, os.getpid(), threading.get_ident(),
                                next(_TMP_SEQ))


def _write_tmp_occ(tmp, blob):
    """tmp 写 (Win32 瞬时占用有界重试 range(5)+sleep, 保留层)。"""
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "wb") as f:
                f.write(blob)
            return
        except PermissionError as e:
            last = e
            time.sleep(0.03 * (attempt + 1))
    raise last


def _replace_occ(path, tmp, base):
    """os.replace 原子落盘 + Win32 瞬时占用有界重试 (range(5)+sleep 保留层)。
    每次重试前漂移复查: 期间文件被并发写过 (与基线不一致) → 放弃本轮 replace
    返回 False 交回乐观层以最新全量重建 (绝不带陈旧内容落盘覆盖他人); 5 次占用
    仍未落且无漂移 → raise (诚实上报, 不吞)。"""
    last = None
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return True
        except PermissionError as e:
            last = e
            time.sleep(0.03 * (attempt + 1))
            try:
                if _read_file_bytes(path) != base:
                    return False
            except RuntimeError:
                return False
    raise last


def _optimistic_write(path, build, base=_UNSET, verify=None):
    """MED-1 乐观并发写核心 (设计冻结: 读全量 + os.replace 逐字节比对, 不靠写锁)。

    build(current_bytes_or_None) -> bytes 全量新内容; verify(current_bytes, blob)
    -> bool 写后核验回调 (缺省: current == blob, 即落盘内容未被并发改写)。
    每轮: 基于基线构建 → 先写**本轮唯一** tmp (R2A-01: 每轮重取唯一 tmp, 重试
    轮次间自踩亦不可能; 压缩比对→replace 窗口) → os.replace 前重读当前 bytes
    与基线逐字节比对; 一致 → os.replace (占用重试内建漂移复查, 不带陈旧内容
    落盘) + 写后单次核验 (replace 后立即重读一次, 本写方贡献必须在场, 被覆盖
    → 以最新全量重建); 不一致/漂移/核验失败 → 以最新全量为基线重建 (最多
    3 轮, 禁 sleep 等待); 3 轮仍冲突 → 中文 fail loud (绝不静默覆盖丢数据)。
    诚实限制: 跨进程并发存在不可消除的比对→replace 窗口 (无锁设计的既定接受项,
    检测到的冲突一律中文 fail loud; 主部署为 ComfyUI 单进程节点面)。
    """
    cur = _read_file_bytes(path) if base is _UNSET else base
    for _ in range(_CONFLICT_MAX_RETRIES):
        blob = build(cur)
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        tmp = _tmp_path(path)                # R2A-01: 每轮重取唯一 tmp (重试间互不踩踏)
        _write_tmp_occ(tmp, blob)            # tmp 先行 (比对与 replace 相邻)
        current = _read_file_bytes(path)     # os.replace 前重读逐字节比对
        if current == cur:
            if not _replace_occ(path, tmp, cur):
                cur = _read_file_bytes(path)  # 重试期间被并发写: 以最新全量重建
                continue
            post = _read_file_bytes(path)    # 写后单次核验 (replace 后立即重读): 本写方贡献必须在场
            ok_post = (post == blob) if verify is None else verify(post, blob)
            if ok_post:
                return blob
            cur = post                        # replace 后被并发覆盖: 以最新重建
            continue
        cur = current                         # 期间被并发写入过: 以最新全量重建 (无 sleep)
    raise RuntimeError("检测到并发写入冲突，已放弃本次写入以防覆盖丢失: %s (重读重建 %d 轮仍冲突)"
                       % (path, _CONFLICT_MAX_RETRIES))


def _atomic_write_json(path, data, base_bytes=_UNSET):
    """UTF-8 JSON 原子写 (tmp + os.replace) — 台账 JSON 写点公共通道, 内建 MED-1
    乐观并发比对 (写前重读逐字节不一致 → 有界重建重试 → 3 轮仍冲突中文 fail loud)。
    base_bytes: 调用方构建 data 时依据的文件全量 bytes (文件不存在传 None); 缺省
    哨兵 = 以写前当前 bytes 为基线。Win32 瞬时占用重试为其下保留层。"""
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True,
                      indent=2).encode("utf-8")
    return _optimistic_write(path, lambda _cur: blob, base=base_bytes)


def _load_ledger_dict(cur, path):
    """台账全量 bytes (不存在为 None) -> dict。损坏/解码失败/顶层非对象 →
    ValueError 中文 (不静默覆盖, 消息与历史口径逐字一致)。"""
    if cur is None:
        return {}
    try:
        loaded = json.loads(cur.decode("utf-8"))
    except ValueError as exc:
        raise ValueError("台账读取失败 (不静默覆盖): %s (%s)" % (path, exc))
    if not isinstance(loaded, dict):
        raise ValueError("台账损坏 (顶层非对象, 不静默覆盖): %s" % path)
    return loaded


def _req_text(v):
    """必填文本规整: None → ""; 其余 str() 后 strip。判空以 strip 后长度为准。"""
    return ("" if v is None else str(v)).strip()


# ---------- 来源批次登记 ----------
def _resolve_media(kw, ref_key):
    """**kw 可选媒体槽位 → ref_media.resolve_ref 语义口径解析 (IMAGE 优先/路径回退,
    无则 "")。仅当 media_kwargs 为非空 dict 时触发。"""
    mkwargs = kw.get("media_kwargs")
    if not isinstance(mkwargs, dict) or not mkwargs:
        return ""
    return _resolve_ref(mkwargs,
                        kw.get("media_img_key", "参考图_IMAGE"),
                        kw.get("media_path_key", "参考图"),
                        ref_key or "ref")


def register_ref(out_dir, ref_id, source, authorization, project, **kw):
    """来源批次登记 → <out_dir>/eco/ref_ledger/<safe_project>.json。

    authorization (授权声明) 与 source (来源描述) 必填: 缺任一 (None/空串/纯空白)
    → {"ok": False, "errors": [...]} fail loud, 不创建目录不落盘。ref_id 亦必填
    (LOW-1: strip 后为空 → 中文 ValueError 拒绝, 严禁空 ref_id 覆盖既有条目)。
    成功 → {"ok": True, "ledger_path", "ref_id", "entry"}; entry 恒含 legal_boundary
    (LEGALESE) 法务边界字段; 同 ref_id 重复登记 → 幂等覆盖同一条目 (按 ref_id
    键)。既有台账损坏/顶层非对象 → 不静默覆盖, fail loud。**kw 透传扩展字段
    (三列表/谱系锚等), media_* 控制键除外。
    落盘走 MED-1 乐观并发写: 基于读到的全量构建 → 落盘前重读逐字节比对, 期间被
    并发写入则以最新全量重建 (最多 3 轮, 禁 sleep), 仍冲突 → 中文 fail loud 拒写。
    """
    errors = []
    src = _req_text(source)
    auth = _req_text(authorization)
    if not src:
        errors.append("source (来源描述) 必填: 缺失/空串/纯空白 — fail loud 未落盘")
    if not auth:
        errors.append("authorization (授权声明) 必填: 缺失/空串/纯空白 — fail loud 未落盘")
    if errors:
        return {"ok": False, "errors": errors}

    ref_key = "" if ref_id is None else str(ref_id)
    if not ref_key.strip():
        raise ValueError(
            "ref_id (素材批次标识) 必填: None/空串/纯空白 — 拒绝登记, 严禁空 ref_id 覆盖既有条目")
    entry = {"ref_id": ref_key, "source": src, "authorization": auth,
             "project": _req_text(project), "legal_boundary": LEGALESE}
    media = _resolve_media(kw, ref_key)
    if media:
        entry["media_ref"] = media
    for k, v in kw.items():
        if k not in _KW_CONTROL and k not in entry:
            entry[k] = v

    ledger_dir = os.path.join(str(out_dir), "eco", "ref_ledger")
    path = os.path.join(ledger_dir, _safe_name(project) + ".json")

    def _build_ledger(cur):
        """MED-1: 基于当前全量 bytes 重建台账 (冲突重试时以最新全量合入本条)。"""
        data = _load_ledger_dict(cur, path)
        data[ref_key] = entry
        return json.dumps(data, ensure_ascii=False, sort_keys=True,
                          indent=2).encode("utf-8")

    def _verify_merged(cur, _blob):
        """写后核验: 当前台账含本条 (ref_id → entry) 才算成功, 否则视为被覆盖。"""
        try:
            return _load_ledger_dict(cur, path).get(ref_key) == entry
        except ValueError:
            return False

    try:
        _optimistic_write(path, _build_ledger, verify=_verify_merged)
    except ValueError as exc:  # 台账损坏/顶层非对象: 不静默覆盖 (历史口径不变)
        return {"ok": False, "errors": [str(exc)]}
    return {"ok": True, "ledger_path": path, "ref_id": ref_key, "entry": dict(entry)}


# ---------- 素材解构三列表 ----------
def deconstruct(notes):
    """用户笔记逐行归类 (确定性, 无 LLM) → 三列表结构 (三键恒齐备)。

    规则 (按序判定, 首中即止): 行含 手法/technique → 手法列; 含 实现/做法/how →
    参考实现列; 含 取舍/放弃/tradeoff → 取舍列; 无法归类行 → 取舍列 (兜底,
    不丢行)。每行 strip 后非空才算一条 (空白行丢弃); 英文关键词按 lower 子串
    匹配。输入 str 按行切分, list[str] 逐元素为行。
    """
    if notes is None:
        lines = []
    elif isinstance(notes, str):
        lines = notes.splitlines()
    elif isinstance(notes, (list, tuple)):
        lines = ["" if x is None else str(x) for x in notes]
    else:
        lines = str(notes).splitlines()
    out = {"手法": [], "参考实现": [], "取舍": []}
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if "手法" in line or "technique" in low:
            out["手法"].append(line)
        elif "实现" in line or "做法" in line or "how" in low:
            out["参考实现"].append(line)
        else:
            # 含 取舍/放弃/tradeoff 与无法归类行 → 同落取舍列 (兜底不丢行)
            out["取舍"].append(line)
    return out


# ---------- 契约注入 (additive 零漂移) ----------
def inject_refs(contract, refs):
    """素材注入批次6 storyboard_contract refs[] 槽位。

    contract 为 dict: 浅拷贝后只加 "refs" 键, 既有键 (含嵌套值) 逐字节不动;
    已有 refs 键 → 追加不去重 (生成新列表, 原 list 不改写); refs 空列表/None →
    原样返回输入 dict (不加键, 逐字节零漂移)。contract 非 dict → TypeError
    fail loud。refs 类型校验 (LOW-3): 必须为 list 且每项为 dict, 否则中文
    ValueError fail loud (str/元组/含非 dict 项一律拒绝, 拒绝不改 contract)。
    """
    if not isinstance(contract, dict):
        raise TypeError("contract 须为 dict, got %s" % type(contract).__name__)
    if refs is None:
        return contract
    if not isinstance(refs, list):
        raise ValueError("refs 须为 list 且每项为 dict (素材条目), 实际 %s — 拒绝注入"
                         % type(refs).__name__)
    bad = [i + 1 for i, x in enumerate(refs) if not isinstance(x, dict)]
    if bad:
        raise ValueError("refs 各项须为 dict (素材条目), 第 %s 项非 dict — 拒绝注入"
                         % ",".join(str(i) for i in bad))
    if not refs:
        return contract
    out = dict(contract)
    merged = list(out["refs"]) if "refs" in out else []
    merged.extend(refs)
    out["refs"] = merged
    return out


# ---------- 谱系源登记 ----------
def anchor_lineage(ref_entry, lineage_root_dir):
    """谱系源登记: <lineage_root_dir>/ref_lineage.jsonl 追加一行 (JSONL)。

    行结构: {ref_id, ts: None (不写时间戳, 确定性纪律), lineage_kind, asset_id};
    lineage_kind 同款对齐 asset_master 派生谱系条目 kind 命名风格 (类型: 母版/
    派生 中文复合词) → "参考源" (语义 ref_source); asset_id 取 ref_entry
    ["asset_id"], 缺则回退 ref_entry["ref_id"] (两者皆缺 → KeyError fail loud)。
    返回 {"ok": True, "lineage_path", "entry"}。
    """
    if not isinstance(ref_entry, dict):
        raise TypeError("ref_entry 须为 dict, got %s" % type(ref_entry).__name__)
    row = {
        "ref_id": ref_entry.get("ref_id"),
        "ts": None,
        "lineage_kind": LINEAGE_KIND_REF_SOURCE,
        "asset_id": ref_entry.get("asset_id") or ref_entry["ref_id"],
    }
    d = str(lineage_root_dir or "")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, LINEAGE_FILENAME)
    line = json.dumps(row, ensure_ascii=False, sort_keys=True)

    def _build_lineage(cur):
        """MED-1 收编: 谱系 JSONL 追加走统一乐观并发写 (基于当前全量 bytes 构建
        新内容; 冲突重试以最新全量重建, 绝不静默覆盖丢行)。"""
        return (cur or b"") + (line + "\n").encode("utf-8")

    _optimistic_write(path, _build_lineage,
                      verify=lambda cur, blob: cur.startswith(blob))
    return {"ok": True, "lineage_path": path, "entry": dict(row)}
