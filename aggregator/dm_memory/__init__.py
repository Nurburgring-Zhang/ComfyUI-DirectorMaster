"""DirectorMaster 创作记忆层 (dm_memory) — 批次4 (V16.9.0).

两层分离纪律: aggregator/version_store = raw 内容权威 (归档层, 语义不动);
本包 = 蒸馏记忆层, 四域:
  shot_cards        SHOT_MEMORY 分镜决策卡 (未验证生成不入正面教训, 负面证据保留)
  preference_store  偏好 (六分支语义去重 + 计数自校验)
  procedure_memory  创作 SOP 程序记忆 (三段式, 用户显式要求才写)
  style_bible       项目风格圣经 (脚本采证确定性骨架, LLM 蒸馏段诚实占位)
+ retrieval  检索 (词频主档纯 stdlib; 嵌入档仅在 onnxruntime+本地模型齐备时启用)
+ anchor_link  version_store 锚点互链 (vid) + adaptive 增量
+ redaction  入库前脱敏 (类型化占位符+白名单豁免)
+ series_inherit  项目档案系列继承 (DNA 继承过 character_dna 同一校验管线)
+ evolution  知识进化钩子 (4 信号白名单, 反映/自建互斥, 失败永不致命)

设计冻结: 编排端 .acs/design_batch4.md (批次4, 验收 ①-⑧).
存储: <out_dir>/dm_memory/<project>/ (与 version_store 同源 out_dir).
域模块缺失时 open_memory 诚实标 unavailable, 绝不伪造.
"""

DM_MEMORY_SCHEMA_VERSION = 1

_TRUST_ORDER = ("当前工作流参数", "用户当前指令", "记忆卡", "历史版本")

trust_order = _TRUST_ORDER

_LAZY_EXPORTS = {
    "schema": "aggregator.dm_memory.schema",
    "shot_cards": "aggregator.dm_memory.shot_cards",
    "preference_store": "aggregator.dm_memory.preference_store",
    "procedure_memory": "aggregator.dm_memory.procedure_memory",
    "style_bible": "aggregator.dm_memory.style_bible",
    "retrieval": "aggregator.dm_memory.retrieval",
    "anchor_link": "aggregator.dm_memory.anchor_link",
    "series_inherit": "aggregator.dm_memory.series_inherit",
    "redaction": "aggregator.dm_memory.redaction",
    "evolution": "aggregator.dm_memory.evolution",
    "injection": "aggregator.dm_memory.injection",
}


def __getattr__(name):
    mod_name = _LAZY_EXPORTS.get(name)
    if mod_name is None:
        raise AttributeError(f"dm_memory 无属性 {name!r}")
    import importlib

    return importlib.import_module(mod_name)


def domain_status():
    """逐域可用性盘点 (诚实口径: 缺模块标 missing, 绝不伪造)."""
    out = {}
    for key in sorted(_LAZY_EXPORTS):
        try:
            __getattr__(key)
            out[key] = "ok"
        except Exception as e:  # noqa: BLE001 — 盘点入口, 任何失败都如实上报
            out[key] = f"missing: {type(e).__name__}"
    return out


def open_memory(out_dir, project):
    """聚合门面: 逐域可选装载, 域缺失诚实标 unavailable 不炸.

    返回 DmMemory 句柄; 各域句柄在 .domains dict, 缺失域值为 None 并记 .unavailable.
    """
    unavailable = []
    domains = {}
    for key in ("shot_cards", "preference_store", "procedure_memory",
                "style_bible", "retrieval", "anchor_link",
                "series_inherit", "redaction", "evolution", "injection"):
        try:
            domains[key] = __getattr__(key)
        except Exception:  # noqa: BLE001 — 渐进启用: 域缺失诚实降级
            domains[key] = None
            unavailable.append(key)
    return DmMemory(out_dir, project, domains, unavailable)


class DmMemory:
    """四域记忆句柄 (轻量: 只持配置与域模块引用, 读写时再落盘)."""

    def __init__(self, out_dir, project, domains, unavailable):
        self.out_dir = out_dir
        self.project = project
        self.domains = domains
        self.unavailable = unavailable

    @property
    def trust_order(self):
        return _TRUST_ORDER

    def status(self):
        return {
            "schema_version": DM_MEMORY_SCHEMA_VERSION,
            "project": self.project,
            "unavailable": list(self.unavailable),
        }
