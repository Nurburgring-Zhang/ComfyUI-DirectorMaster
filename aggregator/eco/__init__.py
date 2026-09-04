"""eco: 生态预案 (批次5, V17.1.0)。

dm_pack.json 插件包注册表 (pack_registry, 字段/版本/依赖三查) + 参考素材流
(ref_flow, 授权边界必填 + 手法/参考实现/取舍三列表 + refs[] 注入零漂移) +
decision_log (append-only JSONL 决策审计轨, sha256 哈希链防篡改 + version_store
只读挂接)。零第三方依赖。思想层独立重写 (xed-editor/openmontage/video-shotcraft
零代码借鉴)。
"""

ECO_SCHEMA_VERSION = 1

__all__ = [
    "ECO_SCHEMA_VERSION",
    "pack_audit",
    "refflow_register",
    "decision_attach",
    "register_packs",
    "register_ref",
    "deconstruct",
    "inject_refs",
    "append_entry",
    "verify_log",
    "replay",
]

_LAZY = {
    "register_packs": ("aggregator.eco.pack_registry", "register_packs"),
    "register_ref": ("aggregator.eco.ref_flow", "register_ref"),
    "deconstruct": ("aggregator.eco.ref_flow", "deconstruct"),
    "inject_refs": ("aggregator.eco.ref_flow", "inject_refs"),
    "append_entry": ("aggregator.eco.decision_log", "append_entry"),
    "verify_log": ("aggregator.eco.decision_log", "verify_log"),
    "replay": ("aggregator.eco.decision_log", "replay"),
}


def __getattr__(name):
    target = _LAZY.get(name)
    if target is None:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
    import importlib

    return getattr(importlib.import_module(target[0]), target[1])


def _eco_dir(out_dir):
    import os

    return os.path.join(str(out_dir), "eco")


def pack_audit(out_dir, packs_dir=None, **kw):
    """聚合门面: dm_pack 包注册审计。段缺失/损坏时诚实标注 unavailable 不炸。"""
    try:
        from aggregator.eco.pack_registry import register_packs

        search = [packs_dir] if packs_dir is not None else None
        return register_packs(search) if search else register_packs([_eco_dir(out_dir)])
    except Exception as exc:
        return {"ok": False, "packs": [], "errors": ["pack_registry 段不可用: %s" % exc]}


def refflow_register(out_dir, ref_id, source, authorization, project, notes=None, contract=None, **kw):
    """聚合门面: 参考素材登记→解构→(可选)契约注入。authorization/source 必填。"""
    try:
        from aggregator.eco.ref_flow import register_ref, deconstruct, inject_refs

        result = register_ref(out_dir, ref_id, source, authorization, project)
        if not result.get("ok"):
            return result
        result["deconstruct"] = deconstruct(notes) if notes is not None else {"手法": [], "参考实现": [], "取舍": []}
        if contract is not None:
            result["contract"] = inject_refs(contract, [result])
        return result
    except Exception as exc:
        return {"ok": False, "errors": ["ref_flow 段不可用: %s" % exc]}


def decision_attach(out_dir, category, subject, decision, options_considered=None, store=None, snapshot_name=None, **kw):
    """聚合门面: 决策追加 + 验证 + (可选)version_store 挂接。段缺失诚实降级。
    MED-3: store 与 snapshot_name 同时给出时, 门面自动传 bridge_path=
    <out_dir>/eco/dm_versions_bridge.json — 快照桥文件必真实落盘 (零写入
    version_store, 挂接记录由本门面代写)。"""
    import os

    log_path = os.path.join(_eco_dir(out_dir), "decision_log.jsonl")
    try:
        from aggregator.eco.decision_log import append_entry, verify_log

        entry = append_entry(log_path, category, subject, decision,
                             options_considered=options_considered)
        ok, errors = verify_log(log_path)
        result = {"ok": ok, "errors": errors, "entry": entry, "log_path": log_path}
        if store is not None and snapshot_name is not None:
            from aggregator.eco.decision_log import attach_to_version

            bridge_path = os.path.join(_eco_dir(out_dir), "dm_versions_bridge.json")
            result["bridge"] = attach_to_version(store, snapshot_name, log_path,
                                                 bridge_path=bridge_path)
        return result
    except Exception as exc:
        return {"ok": False, "errors": ["decision_log 段不可用: %s" % exc], "log_path": log_path}
