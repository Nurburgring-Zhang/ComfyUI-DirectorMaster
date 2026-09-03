"""episode_pipeline: 长篇小说→分集输入管线 (批次7, V17.0.0)。

确定性切分 (splitter) + 覆盖账本 (ledger, Σ==len(text) fail loud——lumenx 80k
静默截断反面教材) + 锚点回溯 (anchors) + 钩子三指标 (hooks) + LLM 可选精拆轨
(llm_refine, 只写注释字段) + 断点续跑 (pipeline, CheckpointStore) + dm_memory
记忆桥 (memory_bridge, additive 缺目录零漂移)。零第三方依赖。
"""

EPISODE_SCHEMA_VERSION = 1

__all__ = [
    "EPISODE_SCHEMA_VERSION",
    "intake",
    "run_intake",
    "detect_chapters",
    "split_episodes",
    "verify_coverage",
    "extract_anchors",
    "traceback",
    "hook_metrics",
    "hook_check",
    "refine_available",
    "refine_episode",
]

_LAZY = {
    "run_intake": ("aggregator.episode_pipeline.pipeline", "run_intake"),
    "detect_chapters": ("aggregator.episode_pipeline.splitter", "detect_chapters"),
    "split_episodes": ("aggregator.episode_pipeline.splitter", "split_episodes"),
    "verify_coverage": ("aggregator.episode_pipeline.ledger", "verify_coverage"),
    "extract_anchors": ("aggregator.episode_pipeline.anchors", "extract_anchors"),
    "traceback": ("aggregator.episode_pipeline.anchors", "traceback"),
    "hook_metrics": ("aggregator.episode_pipeline.hooks", "hook_metrics"),
    "hook_check": ("aggregator.episode_pipeline.hooks", "hook_check"),
    "refine_available": ("aggregator.episode_pipeline.llm_refine", "refine_available"),
    "refine_episode": ("aggregator.episode_pipeline.llm_refine", "refine_episode"),
}


def __getattr__(name):
    target = _LAZY.get(name)
    if target is None:
        raise AttributeError("module %r has no attribute %r" % (__name__, name))
    import importlib

    return getattr(importlib.import_module(target[0]), target[1])


def intake(novel_text, out_dir, project, target_chars, api_url=None, api_key=None, **kw):
    """聚合门面: 长篇小说 → 分集产物。段缺失/损坏时诚实标注 unavailable 不炸。"""
    try:
        from aggregator.episode_pipeline.pipeline import run_intake
    except Exception as exc:
        return {
            "ok": False,
            "errors": ["episode_pipeline pipeline 段不可用: %s" % exc],
            "episodes": [],
            "ledger_summary": {"ok": False, "errors": ["pipeline 段缺失"]},
            "llm_track": {"status": "unavailable"},
            "checkpoints": {"enabled": False},
            "memory": {"status": "unavailable"},
        }
    return run_intake(novel_text, out_dir, project, target_chars,
                      api_url=api_url, api_key=api_key, **kw)
