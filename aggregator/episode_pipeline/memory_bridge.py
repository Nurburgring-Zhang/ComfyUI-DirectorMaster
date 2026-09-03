# -*- coding: utf-8 -*-
"""episode_pipeline/memory_bridge.py — dm_memory 记忆桥 (批次7 builder-e2, V17.0.0)
==================================================================================
每集落 dm_memory 消费面 (批次4 既有模块, 只 import 不改):
  series_inherit.upsert_series   系列档案 (worldview/风格锚/集数; series_id=project)
  series_inherit.inherit_to_project  系列档案 → 项目继承记录 (每集产物=project)
  anchor_link.link_card          集产物 vid 锚定 (card_id=ep_id, vid=产物相对引用)
  injection.injection_block      提示词面接线 (只读)

全保护纪律: 任何一段失败 → 记入 summary["errors"], 绝不向管线抛 (永不致命);
dm_memory 模块不可用 → status="unavailable" (零写入)。episodes/ 产物由此保证
零漂移: 本模块只写 <out_dir>/dm_memory/ 之下, 绝不触碰 episodes/。
series 自由文本先过 redact_free_text (批次4 R2 MED-4 教训; upsert_series 内部
还会再 redact 一层, 双保险且幂等)。
入口函数: bridge_episodes (任务钉板主名) = bridge (兼容别名, 同一函数)。
"""
import os as _os

_DM_MEMORY_DIR = "dm_memory"
_TEXT_CAP = 160


def _cap(text):
    return str(text or "")[:_TEXT_CAP]


def _novel_head(episodes):
    """系列 worldview 诚实素材: 首集标题/末集标题 (不虚构世界观, 只记录事实)。"""
    if not isinstance(episodes, list) or not episodes:
        return ""
    first = episodes[0] if isinstance(episodes[0], dict) else {}
    last = episodes[-1] if isinstance(episodes[-1], dict) else {}
    return "首集《%s》, 末集《%s》" % (_cap(first.get("title", "")) or "未命名",
                                      _cap(last.get("title", "")) or "未命名")


def bridge_episodes(out_dir, project, episodes, target_chars=None):
    """把分集产物接进 dm_memory (任务钉板主名)。返回 summary dict (永不抛):
    {status: ok|partial|unavailable|skipped, errors: [], series_id, links,
     injection_chars}
    status: ok=四段全成功; partial=有段失败 (errors 列原因); unavailable=dm_memory
    模块缺失; skipped=无分集可落。"""
    summary = {"status": "skipped", "errors": [], "series_id": None,
               "links": 0, "injection_chars": 0}
    if not isinstance(episodes, list) or not episodes:
        summary["errors"].append("memory_bridge: 无分集产物可落记忆层")
        return summary
    if not (isinstance(out_dir, str) and out_dir.strip()):
        summary["status"] = "unavailable"
        summary["errors"].append("memory_bridge: out_dir 缺失, 记忆段跳过")
        return summary
    try:
        from aggregator.dm_memory import anchor_link, injection, redaction
        from aggregator.dm_memory import series_inherit
    except Exception as exc:  # dm_memory 整体不可用 → 零写入诚实降级
        summary["status"] = "unavailable"
        summary["errors"].append("memory_bridge: dm_memory 导入失败: %s: %s"
                                 % (type(exc).__name__, str(exc)[:120]))
        return summary

    series_id = str(project or "项目").strip() or "项目"
    summary["series_id"] = series_id
    # 自由文本先脱敏 (MED-4): 本模块自产字段全部过 redact_free_text
    payload = redaction.redact_free_text({
        "worldview": _cap(_novel_head(episodes)),
        "风格锚": _cap("长篇分集管线系列档案: 共 %d 集%s"
                       % (len(episodes),
                          ("; 集均目标 %s 字" % target_chars) if target_chars else "")),
        "集数": len(episodes),
    })
    try:
        series_inherit.upsert_series(out_dir, series_id, payload)
    except Exception as exc:
        summary["errors"].append("memory_bridge: upsert_series 失败: %s: %s"
                                 % (type(exc).__name__, str(exc)[:120]))
    try:
        record = series_inherit.inherit_to_project(out_dir, series_id, str(project or "项目"))
        if not isinstance(record, dict) or not record.get("source_series"):
            raise ValueError("继承记录结构异常")
    except Exception as exc:
        summary["errors"].append("memory_bridge: inherit_to_project 失败: %s: %s"
                                 % (type(exc).__name__, str(exc)[:120]))
    memory_ref = {"out_dir": out_dir, "project": str(project or "项目")}
    for ep in episodes:
        if not isinstance(ep, dict):
            continue
        ep_id = str(ep.get("ep_id") or "").strip()
        if not ep_id:
            continue
        try:
            vid = "episodes/%s.json" % ep_id  # 集产物引用 (相对 safe_project 目录)
            anchor_link.link_card(memory_ref, ep_id, vid)
            summary["links"] += 1
        except Exception as exc:
            summary["errors"].append("memory_bridge: link_card(%s) 失败: %s: %s"
                                     % (ep_id, type(exc).__name__, str(exc)[:120]))
    try:
        block = injection.injection_block(memory_ref, 1, remind_every=1)
        summary["injection_chars"] = len(block or "")
    except Exception as exc:
        summary["errors"].append("memory_bridge: injection_block 失败: %s: %s"
                                 % (type(exc).__name__, str(exc)[:120]))
    if summary["errors"]:
        summary["status"] = "partial"
    elif summary["links"] > 0:
        summary["status"] = "ok"
    return summary


# 兼容别名: 早期草稿与部分调用方使用短名 bridge — 行为逐字节同一函数
bridge = bridge_episodes


def memory_root_exists(out_dir):
    """只读探针: <out_dir>/dm_memory 是否已存在 (供调用方诚实标注记忆段前置状态)。"""
    try:
        return _os.path.isdir(_os.path.join(str(out_dir), _DM_MEMORY_DIR))
    except Exception:
        return False
