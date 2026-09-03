# -*- coding: utf-8 -*-
"""episode_pipeline/pipeline.py — 长篇输入管线编排 (批次7 builder-e2, V17.0.0)
==============================================================================
run_intake(novel_text, out_dir, project, target_chars, api_url=None, api_key=None)
编排: detect → split → coverage(全量重算) → 逐集[anchors→hooks→refine→产物落盘]
     → memory_bridge → manifest。

断点续跑: CheckpointStore(<out_dir>/dm_checkpoints), pipeline_id=sha1(text)[:16],
step="ep_%03d" (从 ep_000 起, 验收⑦钉板), 逐集 mark_done; 重跑 done() 命中且既有
产物校验通过 → 跳过该集产物生成步 (锚点回溯/账本等全量校验每次重跑, 防跳集后
账本/校验不完整)。任何一段异常 → 整体 fail loud 带 errors 列表, 不静默丢 (ok=False);
memory 段例外 — 全保护永不致命 (内部已全 try, 调用点再包一层防御)。

确定性: 产物 JSON sort_keys + UTF-8 原子写 (tmp+os.replace); manifest 不含
时间戳/绝对路径/记忆段结果 — episodes/ 产物与 dm_memory 有无逐字节无关 (additive
零漂移, 验收⑥)。LLM 轨只加注释字段 (logline, llm_generated=true), 原文不可变。
"""
import hashlib as _hashlib
import json as _json
import os as _os
import re as _re
import time as _time

from aggregator.pipeline_checkpoint import CheckpointStore
from aggregator.episode_pipeline import EPISODE_SCHEMA_VERSION
from . import hooks as _hooks
from . import llm_refine as _llm_refine
from . import memory_bridge as _memory_bridge

EPISODES_DIRNAME = "episodes"
CHECKPOINTS_DIRNAME = "dm_checkpoints"

_PRODUCT_KEYS = ("ep_id", "title", "span", "text", "anchors", "hooks",
                 "logline", "checkpoint_ref", "core_pack_seed")
_UNSAFE_FILENAME_RE = _re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')


# ---------- 基础件: safe_name / 原子写 / 哈希 ----------
def safe_name(s):
    """同 dm_memory._safe_name 配方自实现 (R1 MED-3/R2 MED-2 碰撞防护):
    非法字符→"_" + strip + 截40; 替换有信息丢失 / 含 ASCII (NTFS 大小写折叠) /
    尾部 "."或" " (Windows 剥尾) 任一命中 → 追加原 raw 的 sha1 前 8 位。
    同一 raw 恒映射同一目录名, 不同 raw 不共用。"""
    import hashlib
    raw = str(s or "")
    base = _re.sub(r'[\x00-\x1f\x7f\\/:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or _re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _atomic_write_json(path, data):
    """UTF-8 JSON 原子写 (tmp + os.replace); Win32 瞬时占用有界重试 (dm_memory 同配方)。"""
    d = _os.path.dirname(path)
    if d:
        _os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    last = None
    for attempt in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                _json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=2)
            _os.replace(tmp, path)
            return
        except PermissionError as e:
            last = e
            _time.sleep(0.03 * (attempt + 1))
    raise last if last else OSError("写入失败: %s" % path)


def pipeline_id_of(novel_text):
    """pipeline_id = sha1(novel_text)[:16] (验收⑦钉死口径)。"""
    return _hashlib.sha1(
        (novel_text or "").encode("utf-8", errors="replace")).hexdigest()[:16]


def _episode_input_hash(ep, project, target_chars):
    """逐集步骤的输入指纹: 决定该集产物的全部输入 (schema/project/目标字数/集内容)。"""
    payload = _json.dumps(
        {"schema": EPISODE_SCHEMA_VERSION, "project": str(project),
         "target_chars": target_chars, "ep_id": str(ep.get("ep_id") or ""),
         "title": str(ep.get("title") or ""), "span": ep.get("span"),
         "text": ep.get("text") or ""},
        ensure_ascii=False, sort_keys=True)
    return _hashlib.sha1(payload.encode("utf-8", errors="replace")).hexdigest()[:32]


def _core_pack_seed(ep, project):
    """32 字段核心数据包骨架 — 键名与 node_base.parse_core_pack 消费口径一致
    (director_master Core 节点 canonical 键集 + scene_entity/prompt_layers 消费键)。
    骨架值诚实缺省: 未知字段留空, 不伪造内容; _随机种子 由集文本 sha1 确定性派生
    (可复现); _ai_api_key 绝不入产物 (密钥纪律)。"""
    text = ep.get("text") if isinstance(ep.get("text"), str) else ""
    seed_int = int(_hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:8], 16) \
        % (2 ** 31 - 1) + 1
    return {
        "_项目名": str(project),
        "_场景描述": str(ep.get("title") or ""),
        "_导演风格": "",
        "_启用反AI规则": "是",
        "_情绪基调": "",
        "_情绪演变弧": [],
        "_导演意图_观众应感到": "",
        "_时间年代": "",
        "_季节": "",
        "_地区文化": "",
        "_平台媒介": "",
        "_目标受众": "",
        "_预算级别": "",
        "_成片时长": "",
        "_画幅比例": "",
        "_核心冲突": "",
        "_主题词": "",
        "_视觉调性": "",
        "_视觉调性弧": [],
        "_潜文本强度": "",
        "_观众承诺": "",
        "_对标作品": "",
        "_关键道具": "",
        "_潜文本_情感": "",
        "_叙事编排": "跟随叙事结构",
        "_叙事线型": "单线",
        "_项目风格锚": "",
        "_随机种子": seed_int,
        "_角色": [],
        "_道具": [],
        "_ai_api_url": "",
        "_ai_api_model": "",
    }


def _fail(errors, pid, **extra):
    """fail loud 出口: ok=False + errors 列表, 已知段诚实标注, 不静默丢。"""
    out = {
        "ok": False,
        "errors": list(errors),
        "episodes": [],
        "ledger_summary": {"ok": False, "errors": []},
        "llm_track": {"enabled": False, "status": "unavailable",
                      "episodes": {}, "skipped_episodes": []},
        "checkpoints": {"enabled": True, "pipeline_id": pid,
                        "skipped": 0, "regenerated": 0},
        "memory": {"status": "skipped", "errors": ["前置段失败, 记忆桥未执行"]},
    }
    out.update(extra)
    return out


def _episodes_dir(out_dir, project):
    return _os.path.join(str(out_dir), EPISODES_DIRNAME, safe_name(project))


def _artifact_path(out_dir, project, ep_id):
    fname = _UNSAFE_FILENAME_RE.sub("_", str(ep_id)) or "episode"
    return _os.path.join(_episodes_dir(out_dir, project), fname + ".json")


def _validate_loaded_artifact(product, ep_id, ep, novel_text):
    """跳集恢复的既有产物校验: 结构 9 键 + ep_id/text 与本次切分逐字节一致 +
    锚点仍全部回溯命中。任一不过 → 返回 False (重算该集)。"""
    if not isinstance(product, dict):
        return False
    if any(k not in product for k in _PRODUCT_KEYS):
        return False
    if str(product.get("ep_id")) != str(ep_id):
        return False
    if product.get("text") != ep.get("text"):
        return False
    anchors = product.get("anchors")
    if not isinstance(anchors, list):
        return False
    if anchors:
        try:
            from aggregator.episode_pipeline.anchors import traceback
            ok_tb, _ = traceback(novel_text, anchors)
            if not ok_tb:
                return False
        except Exception:
            return False
    return True


# ---------- 主编排 ----------
def run_intake(novel_text, out_dir, project, target_chars, api_url=None, api_key=None):
    """长篇小说 → 分集产物 (编排入口)。返回 dict:
    {ok, errors, episodes(9键产物列表), ledger_summary, llm_track, checkpoints, memory}"""
    errors = []
    if not isinstance(novel_text, str) or not novel_text:
        return _fail(["novel_text 必须是非空字符串"], "")
    pid = pipeline_id_of(novel_text)
    if not (isinstance(out_dir, str) and out_dir.strip()):
        return _fail(["out_dir 必须是非空字符串"], pid)
    if not (isinstance(project, str) and project.strip()):
        return _fail(["project 必须是非空字符串"], pid)
    try:
        target_chars = int(target_chars)
        if target_chars <= 0:
            raise ValueError("<=0")
    except Exception:
        return _fail(["target_chars 必须是正整数, 实际 %r" % (target_chars,)], pid)

    # ---- 段1: 切分 (e1, 惰性导入; 段缺失 → fail loud 诚实标注) ----
    try:
        from aggregator.episode_pipeline.splitter import detect_chapters, split_episodes
        from aggregator.episode_pipeline.ledger import verify_coverage
        from aggregator.episode_pipeline.anchors import extract_anchors, traceback
    except Exception as exc:
        return _fail(["episode_pipeline 切分段不可用: %s: %s"
                      % (type(exc).__name__, str(exc)[:160])], pid)
    try:
        chapters = detect_chapters(novel_text)
    except Exception as exc:
        return _fail(["章节检测失败: %s: %s" % (type(exc).__name__, str(exc)[:160])], pid)
    try:
        episodes, ledger = split_episodes(novel_text, target_chars)
    except Exception as exc:
        return _fail(["分集切分失败: %s: %s" % (type(exc).__name__, str(exc)[:160])], pid)
    if not isinstance(episodes, list) or not episodes:
        return _fail(["分集切分结果为空 (未产出任何分集)"], pid)

    # ---- 段2: 覆盖账本 (全量重算, Σ==len(text) 硬约束, 未归类字符 → fail loud) ----
    ledger_summary = {"ok": False, "errors": [], "chapters": len(chapters),
                      "episode_count": len(episodes), "total_chars": len(novel_text)}
    try:
        cov_ok, cov_errors = verify_coverage(novel_text, ledger)
    except Exception as exc:
        cov_ok, cov_errors = False, ["verify_coverage 异常: %s: %s"
                                     % (type(exc).__name__, str(exc)[:160])]
    if not cov_ok:
        for e in cov_errors:
            errors.append("覆盖账本: %s" % str(e)[:200])
        ledger_summary["errors"] = [str(e)[:200] for e in cov_errors]
        return _fail(errors, pid, ledger_summary=ledger_summary)
    ledger_summary["ok"] = True

    # ---- 段3: 检查点 + 逐集产物 (skip 或 regenerate) ----
    store = CheckpointStore(_os.path.join(str(out_dir), CHECKPOINTS_DIRNAME))
    refine_enabled = _llm_refine.refine_available(api_url, api_key)
    llm_track = {"enabled": refine_enabled, "status": "unavailable",
                 "episodes": {}, "skipped_episodes": []}
    products = []
    skipped, regenerated = 0, 0

    for idx, ep in enumerate(episodes, start=1):
        if not isinstance(ep, dict) or not isinstance(ep.get("text"), str):
            errors.append("第 %d 集形状异常 (缺 ep_id/text), 该集跳过不产产物" % idx)
            continue
        # 验收⑦钉板: 检查点步名从 ep_000 起 (steps 记录 ep_000..); ep_id 兜底同序
        ep_id = str(ep.get("ep_id") or ("ep_%03d" % (idx - 1)))
        step = "ep_%03d" % (idx - 1)
        ih = _episode_input_hash(ep, project, target_chars)

        # 断点续跑: done() 命中且既有产物校验通过 → 跳过产物生成步
        if store.done(pid, step, ih):
            product = None
            try:
                path = _artifact_path(out_dir, project, ep_id)
                if _os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        product = _json.load(f)
            except Exception:
                product = None
            if product is not None and _validate_loaded_artifact(
                    product, ep_id, ep, novel_text):
                products.append(product)
                skipped += 1
                llm_track["skipped_episodes"].append(ep_id)
                continue
            # 检查点命中但产物缺失/损坏/校验不过 → 重算 (诚实自愈, 不静默)

        # 逐集产物生成
        try:
            anchors = extract_anchors(novel_text, ep)
            tb_ok, tb_results = traceback(novel_text, anchors)
            if not tb_ok:
                raise ValueError("锚点回溯未全部命中: %s"
                                 % _json.dumps(tb_results, ensure_ascii=False)[:200])
        except Exception as exc:
            errors.append("%s 锚点段失败: %s: %s"
                          % (ep_id, type(exc).__name__, str(exc)[:160]))
            continue
        try:
            hooks_result = _hooks.hook_check(ep)
        except Exception as exc:
            errors.append("%s 钩子段失败: %s: %s"
                          % (ep_id, type(exc).__name__, str(exc)[:160]))
            continue
        logline = ""
        if refine_enabled:
            try:
                refined, st = _llm_refine.refine_episode(ep, api_url, api_key, "")
                llm_track["episodes"][ep_id] = st
                if refined:
                    logline = str(refined.get("logline") or "")
            except Exception as exc:
                llm_track["episodes"][ep_id] = "degraded:精拆异常:%s:%s" % (
                    type(exc).__name__, str(exc)[:120])
        else:
            llm_track["episodes"][ep_id] = "unavailable"
        span = ep.get("span") if isinstance(ep.get("span"), dict) else {}
        product = {
            "ep_id": ep_id,
            "title": str(ep.get("title") or ""),
            "span": dict(span),
            "text": ep["text"],
            "anchors": anchors,
            "hooks": hooks_result,
            "logline": logline,
            "checkpoint_ref": "%s:%s" % (pid, step),
            "core_pack_seed": _core_pack_seed(ep, project),
        }
        try:
            _atomic_write_json(_artifact_path(out_dir, project, ep_id), product)
            store.mark_done(pid, step, ih, artifact_ref="%s.json" % ep_id)
        except Exception as exc:
            errors.append("%s 产物落盘失败: %s: %s"
                          % (ep_id, type(exc).__name__, str(exc)[:160]))
            continue
        products.append(product)
        regenerated += 1

    refined_statuses = [v for k, v in sorted(llm_track["episodes"].items())
                        if k not in set(llm_track["skipped_episodes"])]
    if not refine_enabled:
        llm_track["status"] = "unavailable"
    elif refined_statuses and all(s == "refined" for s in refined_statuses):
        llm_track["status"] = "refined"
    elif refined_statuses:
        llm_track["status"] = "degraded"  # 轨已配置但存在未成功集 (含全部 degraded), 不与"未配置"同标签
    else:
        llm_track["status"] = "unavailable"  # 轨已配置但本轮无尝试 (全 skipped/零分集)

    # ---- 段4: 记忆桥 (全保护, 永不致命, 缺失/失败零漂移) ----
    try:
        memory_summary = _memory_bridge.bridge_episodes(
            out_dir, project, products, target_chars)
    except Exception as exc:  # 双保险: bridge 内部已全 try, 此处兜底防未来变更破坏永不致命纪律
        memory_summary = {"status": "partial", "errors": [
            "memory_bridge: 未预期异常: %s: %s" % (type(exc).__name__, str(exc)[:160])],
            "series_id": None, "links": 0, "injection_chars": 0}

    # ---- 段5: manifest (确定性: 无时间戳/无绝对路径/无记忆段结果) ----
    manifest = {
        "schema": EPISODE_SCHEMA_VERSION,
        "project": project,
        "target_chars": target_chars,
        "pipeline_id": pid,
        "episodes": products,
        "ledger_summary": ledger_summary,
        "llm_track": llm_track,
        "checkpoints": {"pipeline_id": pid, "skipped": skipped,
                        "regenerated": regenerated},
        "errors": errors,
    }
    try:
        _atomic_write_json(_os.path.join(_episodes_dir(out_dir, project),
                                         "manifest.json"), manifest)
    except Exception as exc:
        errors.append("manifest 落盘失败: %s: %s" % (type(exc).__name__, str(exc)[:160]))

    return {
        "ok": not errors,
        "errors": errors,
        "episodes": products,
        "ledger_summary": ledger_summary,
        "llm_track": llm_track,
        "checkpoints": {"enabled": True, "pipeline_id": pid, "skipped": skipped,
                        "regenerated": regenerated, "products_total": len(products)},
        "memory": memory_summary,
        "project": project,
        "pipeline_id": pid,
    }
