# -*- coding: utf-8 -*-
"""
批次4 builder-m2 — 项目档案系列继承 (aggregator/dm_memory/series_inherit.py)
==========================================================================
系列档案 (跨项目全局): <out_dir>/dm_memory/_series/<safe_series_id>.json
  payload: worldview / 风格锚 / dna 列表 (+ series_id / updated_at 元数据)
继承纪律 (验收⑦, 批次6 R1 MED-3 钉死): DNA 继承必须调用 aggregator.character_dna
同一校验管线 (build_dna_profile / merge_dna_profile: 拒抽象词 + 具体视觉词规则
白名单复核, 系列基座维度值不直接采信) — 校验失败该维度诚实跳过并记录原因,
绝不让"拒抽象词"守卫被旁路。
"""
import hashlib
import json
import os
import re
import threading
import time

from aggregator.character_dna import (
    DNA_DIMENSIONS,
    NOT_PROVIDED,
    build_dna_profile,
    merge_dna_profile,
    reject_abstract_words,
)

from . import redaction

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
    # 原始 raw): 不同 series_id 绝不共用同一档案文件; 同一原始 id 恒映射同一文件。
    raw = str(s or "")
    base = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


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


def _sha256(text):
    return hashlib.sha256((text or "").encode("utf-8", errors="replace")).hexdigest()


def series_path(out_dir, series_id):
    # 存储布局 (设计 §3): <out_dir>/dm_memory/_series/<safe_series_id>.json
    return os.path.join(str(out_dir), "dm_memory", "_series",
                        _safe_name(str(series_id)) + ".json")


def upsert_series(out_dir, series_id, payload):
    """创建/更新系列档案 (payload 原样保留 + 元数据)。返回落盘档案 dict。
    入库前脱敏 (R2 MED-4): worldview/风格锚 及 dna 内嵌套 str 值递归 redact
    (与 shot_cards/preference_store/procedure_memory 同款接线, 永不致命);
    结构键 (series_id/updated_at 等元数据与计数类) 不碰, 先脱敏后落盘。"""
    series_id = str(series_id or "").strip()
    if not series_id:
        raise ValueError("series_id 不能为空")
    if not isinstance(payload, dict):
        raise ValueError("payload 需为 dict (含 worldview/风格锚/dna 至少一项)")
    if not any(k in payload for k in ("worldview", "风格锚", "dna")):
        raise ValueError("payload 需含 worldview/风格锚/dna 至少一项")
    doc = redaction.redact_free_text(dict(payload))  # 入库脱敏 (R2 MED-4): 只动自由文本
    doc["series_id"] = series_id
    doc["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    path = series_path(out_dir, series_id)
    with _lock_for(path):
        _atomic_write_json(path, doc)
    return doc


def _dim_skips(base_dims, validated, name):
    """逐维对照: 系列原值非空而校验管线后落为 未提供 → 诚实跳过并记录原因。"""
    skips = []
    for dim in DNA_DIMENSIONS:
        raw = base_dims.get(dim, NOT_PROVIDED) if isinstance(base_dims, dict) else NOT_PROVIDED
        final = validated["维度"].get(dim, NOT_PROVIDED)
        if isinstance(raw, str) and raw.strip() and raw != NOT_PROVIDED and final == NOT_PROVIDED:
            _, rejected = reject_abstract_words(raw)
            reason = ("拒抽象词: " + ",".join(rejected)
                      if rejected else "无规则命中 (具体视觉词规则表未收录)")
            skips.append({"角色名": name, "维度": dim, "原始值": raw, "原因": reason})
    return skips


def _inherit_one_dna(entry, idx):
    """单条 DNA 过 character_dna 校验管线。返回 (继承项|None, skips)。
    条目形状二选一: 已构 DNA 档 (含 维度 dict) → merge_dna_profile 白名单复核;
    原始输入 (外貌/服装/视觉风格) → build_dna_profile 全管线。"""
    if not isinstance(entry, dict):
        return None, [{"角色名": f"dna[{idx}]", "维度": "*", "原始值": str(entry)[:80],
                       "原因": "条目不是 JSON 对象, 整条诚实跳过"}]
    name = str(entry.get("角色名") or entry.get("name") or f"dna[{idx}]").strip() or f"dna[{idx}]"
    if isinstance(entry.get("维度"), dict):
        validated = merge_dna_profile(entry, {}, name)
        return {"角色名": name, "profile": validated}, _dim_skips(entry.get("维度"), validated, name)
    appearance = str(entry.get("外貌") or entry.get("appearance") or "")
    costume = str(entry.get("服装") or entry.get("costume") or "")
    style = str(entry.get("视觉风格") or entry.get("visual_style") or "")
    validated = build_dna_profile(name, appearance, costume, style)
    skips = []
    rejected = list(validated.get("抽象词") or [])
    if rejected:
        skips.append({"角色名": name, "维度": "*", "原始值": "外貌/服装原文",
                      "原因": "拒抽象词: " + ",".join(rejected)})
    return {"角色名": name, "profile": validated}, skips


def inherit_to_project(out_dir, series_id, project):
    """系列档案 → 新项目继承记录 inheritance_record:
    {source_series, inherited_at, fingerprints, worldview, 风格锚, dna, skipped}。
    fingerprints = 继承内容 sha256 指纹 (DNA 指纹取校验管线产出后的内容)。"""
    path = series_path(out_dir, series_id)
    if not os.path.isfile(path):
        raise ValueError(f"系列档案不存在: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"系列档案损坏: {type(e).__name__}: {e}")
    if not isinstance(data, dict):
        raise ValueError("系列档案顶层不是 JSON 对象")
    record = {
        "source_series": str(series_id),
        "project": str(project or "项目"),
        "inherited_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fingerprints": {},
        "worldview": str(data.get("worldview", "") or ""),
        "风格锚": str(data.get("风格锚", "") or ""),
        "dna": [],
        "skipped": [],
    }
    fps = {}
    if record["worldview"]:
        fps["worldview"] = _sha256(record["worldview"])
    if record["风格锚"]:
        fps["风格锚"] = _sha256(record["风格锚"])
    used_names = set()
    dna_list = data.get("dna") if isinstance(data.get("dna"), list) else []
    for i, entry in enumerate(dna_list):
        item, skips = _inherit_one_dna(entry, i)
        record["skipped"].extend(skips)
        if item is None:
            continue
        name = item["角色名"]
        if name in used_names:
            name = f"{name}#{i}"
            item["角色名"] = name
        used_names.add(name)
        record["dna"].append(item)
        fps[f"dna:{name}"] = _sha256(
            json.dumps(item["profile"], ensure_ascii=False, sort_keys=True))
    record["fingerprints"] = fps
    return record
