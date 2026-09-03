# -*- coding: utf-8 -*-
"""episode_pipeline/llm_refine.py — LLM 可选精拆轨 (批次7 builder-e2, V17.0.0)
==============================================================================
对单集做 LLM 精拆: logline (一句话故事线) + 集内场景列表。铁律:
  - 只写注释字段 logline/refined_scenes 且标 llm_generated=true;
    原文 span/text 永不可变 (refined = 原episode dict 浅拷贝 + 仅追加注释键)。
  - 失败/超时/回声/截断 → 降级, status ∈ {"refined","unavailable","degraded:<原因>"}
    诚实标注, 绝不伪造 refined 结果。
  - 容错口径复用 llm_engine 同款 (只 import 不改): llm_engine 内部即
    `from pln_llm import detect_echo / call_ai` (llm_engine.py 质量门与双轨调用处),
    本模块同源直接 import pln_llm 的 call_ai (重试/截断检测/降级链) +
    detect_echo (回声照抄) + json_loads_tolerant (宽容 JSON), 口径逐字一致。
凭据齐备才可用: api_url 与 api_key 均非空 (验收⑤: 无凭据 → unavailable)。
"""
import os as _os
import sys as _sys

REFINE_TIMEOUT_S = 20        # 单请求超时 (秒): 精拆轨降级要快, 不拖管线
REFINE_TEMPERATURE = 0.3
REFINE_MAX_TOKENS = 2048
_MAX_TEXT_CHARS = 6000       # 喂给 LLM 的单集文本上限 (超长截尾, 原文不动)
_MAX_SCENES = 12
_MAX_LOGLINE_CHARS = 120

_SYSTEM_PROMPT = (
    "你是长篇小说分集精拆助手。对给定的一集小说文本, 输出严格的 JSON 对象 "
    "(不要输出任何 JSON 之外的文字):\n"
    '{"logline": "一句话概括本集故事线 (不超过60字)", '
    '"scenes": [{"标题": "场景标题", "摘要": "场景摘要(不超过60字)"}]}\n'
    "要求: 只依据给定文本归纳, 不虚构原文没有的情节; scenes 按原文顺序, 最多 8 条。"
)

_STATUS_UNAVAILABLE = "unavailable"


def _import_pln_llm():
    """pln_llm 在仓库根 (与 aggregator 平级): 常规环境直接 import;
    嵌入/脚本环境补 repo root 到 sys.path 后重试一次。失败抛 RuntimeError。"""
    try:
        import pln_llm
        return pln_llm
    except ImportError:
        pass
    here = _os.path.dirname(_os.path.abspath(__file__))
    root = _os.path.dirname(_os.path.dirname(_os.path.dirname(here)))
    if root not in _sys.path:
        _sys.path.insert(0, root)
    try:
        import pln_llm
        return pln_llm
    except Exception as exc:
        raise RuntimeError("pln_llm 不可用: %s: %s" % (type(exc).__name__, exc))


def refine_available(api_url, api_key):
    """精拆轨可用性: api_url 与 api_key 均为非空 str 才算有凭据。"""
    return bool(str(api_url or "").strip()) and bool(str(api_key or "").strip())


def _call_llm(api_url, api_key, model_name, system_prompt, user_message):
    """llm_engine 容错口径接线 (只 import 不改): 返回 (response_text, err)。"""
    pln = _import_pln_llm()
    return pln.call_ai(
        api_url, api_key, model_name or "", system_prompt, user_message,
        REFINE_TEMPERATURE, REFINE_MAX_TOKENS,
        timeout=REFINE_TIMEOUT_S, enable_recovery=False, max_retries_per_step=1)


def _parse_scenes(obj):
    """scenes 字段宽容归一: [{"标题","摘要"}] (接受 title/summary 别名), 封顶 _MAX_SCENES。"""
    raw = obj.get("scenes")
    if raw is None:
        raw = obj.get("场景")
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw[:_MAX_SCENES]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("标题") or item.get("title") or "").strip()[:60]
        summary = str(item.get("摘要") or item.get("summary") or "").strip()[:200]
        if not title and not summary:
            continue
        out.append({"标题": title, "摘要": summary})
    return out


def refine_episode(episode, api_url, api_key, model_name):
    """单集 LLM 精拆。返回 (refined, status):
    - refined: 原episode 的浅拷贝 + 仅追加 logline/refined_scenes/llm_generated=True
      (成功时); 失败/降级时为 None。
    - status: "refined" | "unavailable" (无凭据/引擎不可用) | "degraded:<原因>"。
    输入 episode 永不被修改 (纯拷贝追加), span/text 逐字节保持原值。"""
    if not isinstance(episode, dict) or not isinstance(episode.get("text"), str):
        return None, "degraded:episode 缺 text 字段"
    if not refine_available(api_url, api_key):
        return None, _STATUS_UNAVAILABLE
    text = episode["text"][:_MAX_TEXT_CHARS]
    user_message = (
        "请对下面这一集小说文本做精拆, 只输出规定格式的 JSON。\n"
        "---集文本---\n%s\n---集文本---" % text)
    try:
        response, err = _call_llm(api_url, api_key, model_name,
                                  _SYSTEM_PROMPT, user_message)
    except Exception as exc:
        return None, "degraded:llm调用异常:%s:%s" % (type(exc).__name__, str(exc)[:120])
    if err or not response:
        return None, "degraded:llm调用失败:%s" % (str(err or "空响应")[:120])
    # 回声照抄检测 (llm_engine 同款口径): 抄回提示词 或 抄回原文 都算零创作
    try:
        pln = _import_pln_llm()
        echo_hit, ratio = pln.detect_echo(response, user_message)
        if echo_hit:
            return None, "degraded:回声照抄提示词(相似%d%%)" % round(ratio * 100)
        echo_hit, ratio = pln.detect_echo(response, text)
        if echo_hit:
            return None, "degraded:回声照抄原文(相似%d%%)" % round(ratio * 100)
    except Exception:
        pass  # 检测器异常不阻断 (与 llm_engine _quality_gate 同口径), 后续结构校验兜底
    try:
        pln = _import_pln_llm()
        obj, diag = pln.json_loads_tolerant(response)
    except Exception as exc:
        obj, diag = None, "%s: %s" % (type(exc).__name__, str(exc)[:120])
    if obj is None or not isinstance(obj, dict):
        return None, "degraded:输出截断/JSON不可解析:%s" % str(diag or "")[:120]
    logline = str(obj.get("logline") or obj.get("一句话故事线") or "").strip()[:_MAX_LOGLINE_CHARS]
    scenes = _parse_scenes(obj)
    if not logline and not scenes:
        return None, "degraded:响应缺少有效 logline/scenes 字段"
    # 只追加注释字段: 原键 (含 span/text) 原值原样 — 原文不可变铁律
    refined = dict(episode)
    refined["logline"] = logline
    refined["refined_scenes"] = scenes
    refined["llm_generated"] = True
    return refined, "refined"
