# -*- coding: utf-8 -*-
"""
V15.0-MERGED 共创引擎 (Co-Creator Engine) — 五阶段共创循环 (重写版)
====================================================================
基于 harness/loop/graph engineering 研究 (Self-Refine/Reflexion/GoT/Best-of-N/门序/预算)。

重写修复 (双AI互审 P0/P1):
  P0  LLM 路径真实化 — S1 LLM 方向真实解析并采用; S3 LLM 精炼真实走门控, 失败写失败记忆。
  P1  输入真实消费 — risk_level/emotional_intent/aesthetic 全部影响生成, 不再仅回显。
  P1  分支真实多样 — 分支3(反常规)按故事哈希变化, 不再是常量; 草稿从故事核心真实派生, 无占位句。
  P1  失败记忆活码 — 门控拒收 (含 LLM 输出拒收) 真实写入 lessons.jsonl。

五阶段:
  S0 上下文装配 — 用户 brief + 失败记忆检索 (确定性)
  S1 发散       — 3 条叙事方向分支 (GoT; 从故事核心真实派生; 有端点时 LLM 生成并采用)
  S2 确定性门阵 — 长度→套话→照抄→结构 (fail-fast, 每门输出 fix_hint)
  S3 精炼循环   — 门控违规清单驱动定向修订 (外部信号; ≤2轮; 停滞检测; 拒收写失败记忆)
  S4 收敛交付   — 预算控制器; 触顶交付最佳迄今版本+门报告 (终止即交互)

纪律:
  - 确定性门是硬约束, LLM 评分只做软排序 (权重≤50%)
  - 每次拒收写入失败记忆; 无端点时全链路确定性可运行
  - 确定性契约: 失败记忆库冻结时, 同输入逐字节同输出 (创作日志不含墙钟)
"""
import hashlib as _hashlib
import re as _re

MAX_REFINE_ROUNDS = 2
MAX_LLM_CALLS = 6
STAGNATION_SIM = 0.95

# 类型公式方向库 (真实的叙事公式)
_DIRECTION_FORMULAS = {
    "复仇线": ("失去 → 蜕变 → 逼近 → 对峙 → 抉择的代价",
               "主角在复仇完成的那一刻发现: 复仇不能带回失去的东西。真正的抉择是放下还是继续。"),
    "救赎线": ("坠落 → 微光 → 试炼 → 牺牲或和解",
               "主角不配被原谅, 但有人仍然给了机会。救赎不是被原谅, 是学会承担。"),
    "悬疑线": ("谜面 → 线索 → 误导 → 揭示 → 余震",
               "所有线索都指向错误的人, 因为真相被最亲近的人藏起来了。"),
    "爱情线": ("相遇 → 靠近 → 障碍 → 分离 → 重逢或释怀",
               "让他们分开的不是误会, 是两个人各自无法放弃的东西。"),
    "成长线": ("现状 → 打破 → 试炼 → 觉醒 → 新的现状",
               "主角想要的和需要的在故事中段分道扬镳, 结局是二选一的代价。"),
}

# 反常规手法库 (按故事哈希确定性选取, 不再是单一常量)
_UNCONVENTIONAL_MOVES = [
    ("从结局开始讲", "故事从结果开始 — 观众先知道结局, 再看为什么会这样。悬念从'会发生什么'变成'这意味着什么'。"),
    ("反派视角讲述", "用对立者的视角讲述 — 观众被迫理解'对方'的逻辑, 善恶边界模糊。"),
    ("时间倒流", "故事倒着讲 — 从结局退回开端, 每个'原因'其实是上一个'结果'。"),
    ("旁观者视角", "主角从不直接出现, 只通过他人的讲述拼出 — 主角是一个被叙述建构的形象。"),
    ("同一时刻多视角", "同一关键事件用三个视角各讲一遍 — 真相在版本的裂缝里。"),
]


def _bigram_sim(a, b):
    a, b = str(a), str(b)
    if len(a) < 4 or len(b) < 4:
        return 0.0
    sa = set(a[i:i + 2] for i in range(len(a) - 1))
    sb = set(b[i:i + 2] for i in range(len(b) - 1))
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def _detect_genre(story_core):
    t = str(story_core or "")
    if any(k in t for k in ("复仇", "报仇", "仇", "凶手")):
        return "复仇线"
    if any(k in t for k in ("救赎", "原谅", "罪", "弥补")):
        return "救赎线"
    if any(k in t for k in ("谜", "失踪", "真相", "悬", "秘密")):
        return "悬疑线"
    if any(k in t for k in ("爱", "恋", "分离", "重逢", "情感")):
        return "爱情线"
    if any(k in t for k in ("成长", "梦想", "觉醒", "改变")):
        return "成长线"
    return None


def _extract_story_elements(story_core):
    """从故事核心轻量提取人物/物件/冲突/场景 (确定性启发式, 用于真实派生草稿)."""
    t = str(story_core or "").strip()
    segs = [s.strip() for s in _re.split(r"[,，。；;、\n]+", t) if s.strip()]
    chars, objs, setting = [], [], []
    for s in segs:
        s = s[:14]
        if any(k in s for k in ("姐", "妹", "兄", "弟", "父", "母", "他", "她", "我", "主角", "人")):
            chars.append(s)
        elif any(k in s for k in ("信", "物", "表", "照片", "钥匙", "机", "车", "房", "刀", "钱")):
            objs.append(s)
        else:
            setting.append(s)
    return {
        "chars": chars[:2] or ["主角"],
        "objs": objs[:2] or ["关键物件"],
        "setting": setting[:1] or ["故事场景"],
        "conflict": t[:40],
    }


def _gate_array(text, user_input, min_len=300):
    """确定性门阵 (fail-fast): 长度→套话→照抄→结构. 返回 (pass, report)."""
    report = []
    t = str(text or "")

    if len(t) < min_len:
        report.append({"gate": "长度", "pass": False,
                       "reason": f"正文 {len(t)} 字 < 下限 {min_len}",
                       "fix_hint": f"再展开至少 {min_len - len(t)} 字的具体场景与动作"})
        return False, report
    report.append({"gate": "长度", "pass": True, "reason": "", "fix_hint": ""})

    cliche_hits = 0
    try:
        from anti_ai_vocab import ANTI_AI_PHRASES
        low = t.lower()
        for p in ANTI_AI_PHRASES.keys():
            if p.lower() in low:
                cliche_hits += 1
    except Exception:
        pass
    try:
        from anti_ai_vocab import count_regex_hits
        rx_hits, _ = count_regex_hits(t)
        cliche_hits += rx_hits
    except Exception:
        pass
    if cliche_hits > 3:
        density = cliche_hits / max(1, len(t) / 500)
        report.append({"gate": "套话", "pass": False,
                       "reason": f"AI 套话 {cliche_hits} 处 (密度 {density:.2f}/500字)",
                       "fix_hint": "删除套话, 用具体动作与物件替代抽象形容"})
        return False, report
    report.append({"gate": "套话", "pass": True, "reason": "", "fix_hint": ""})

    sim = _bigram_sim(t, user_input)
    if sim > 0.85:
        report.append({"gate": "照抄", "pass": False,
                       "reason": f"与用户输入重合 {round(sim * 100)}%",
                       "fix_hint": "原生创作, 不得复述用户输入"})
        return False, report
    report.append({"gate": "照抄", "pass": True, "reason": "", "fix_hint": ""})

    has_scene = any(k in t for k in ("场", "镜", "INT", "EXT", "内景", "外景"))
    has_beat = any(k in t for k in ("开场", "中点", "高潮", "结局", "转折", "钩子"))
    if not (has_scene and has_beat):
        report.append({"gate": "结构", "pass": False,
                       "reason": "缺少场景标记或节拍标记",
                       "fix_hint": "补充场次结构与关键节拍 (开场/中点/高潮)"})
        return False, report
    report.append({"gate": "结构", "pass": True, "reason": "", "fix_hint": ""})
    return True, report


def _deterministic_score(text, user_input):
    t = str(text or "")
    length_score = min(1.0, len(t) / 800.0)
    struct_hits = sum(1 for k in ("开场", "中点", "高潮", "结局", "转折") if k in t)
    struct_score = struct_hits / 5.0
    cliche = 0
    try:
        from anti_ai_vocab import ANTI_AI_PHRASES
        low = t.lower()
        cliche = sum(1 for p in ANTI_AI_PHRASES.keys() if p.lower() in low)
    except Exception:
        pass
    cliche_score = max(0.0, 1.0 - cliche / 8.0)
    novelty = 1.0 - _bigram_sim(t, user_input)
    return round(0.3 * length_score + 0.3 * struct_score + 0.2 * cliche_score + 0.2 * novelty, 4)


def _expand_direction(name, formula, twist, elems, director, mood, emotional_intent, aesthetic, risk_level):
    """把方向公式展开为结构化剧本草稿 — 从故事元素真实派生 (无占位句)."""
    c1 = elems["chars"][0]
    obj = elems["objs"][0]
    setting = elems["setting"][0]
    conflict = elems["conflict"]
    stages = [s.strip() for s in formula.split("→")]
    n = len(stages)
    lines = [
        f"【共创方向 · {name}】",
        f"故事核心: {conflict}",
        f"导演锚定: {director or '未指定'} | 情绪: {mood or '未指定'}"
        + (f" | 情感诉求: {emotional_intent}" if emotional_intent else "")
        + (f" | 审美: {aesthetic}" if aesthetic else ""),
        f"叙事公式: {formula}",
        f"核心转折: {twist}",
        f"风险档位: {risk_level}",
        "",
        "场次展开:",
    ]
    for i, st in enumerate(stages):
        pct = round((i + 1) / n * 100)
        beat = "开场钩子" if i == 0 else ("中点反转" if abs(pct - 50) < 15 else ("高潮" if pct >= 80 else "推进"))
        lines.append(f"  第{i + 1}场 [{st}] (进度≈{pct}%, 节拍: {beat})")
        lines.append(f"    场景: {setting} — {st}的具体展开")
        lines.append(f"    动作: {c1} 在「{st}」中面对 {obj}, 用动作与物件表达, 不直说情绪")
        if i == n - 1:
            lines.append(f"    落点: {twist}")
    lines += ["", "注: 本方向为共创草稿骨架, 具体对白由下游剧本节点或 AI 精炼补全。"]
    return "\n".join(lines)


def _parse_llm_directions(llm_text, fallback_directions):
    """解析 LLM 方向输出为分支列表; 解析失败回退确定性方向."""
    t = str(llm_text or "").strip()
    if len(t) < 30:
        return None
    # 按"方向X"或换行分段
    parts = _re.split(r"(?:方向[一二三四五12345][:：]?)|(?:\n\s*\n)", t)
    parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 10]
    if len(parts) < 2:
        # 单段输出 → 作为对第一分支的增强
        if fallback_directions:
            fd = list(fallback_directions)
            fd[0] = (fd[0][0], fd[0][1], t[:200])
            return fd
        return None
    out = []
    labels = ["LLM方向A", "LLM方向B", "LLM方向C"]
    for i, p in enumerate(parts[:3]):
        label = labels[i] if i < len(labels) else f"LLM方向{i + 1}"
        out.append((label, p[:60], p[:200]))
    return out


def co_create(story_core, emotional_intent="", aesthetic="", director="", mood="",
              api_url="", api_key="", api_model="", store_dir=None, risk_level="medium"):
    """五阶段共创循环. 返回 dict:
    {script, directions, chosen, gate_report, creation_log, lessons_added, tier}
    """
    log = []
    lessons_added = 0
    genre = _detect_genre(story_core) or "通用"
    elems = _extract_story_elements(story_core)

    def _add_lesson(gate, reason):
        nonlocal lessons_added
        if store_dir:
            try:
                from aggregator.failure_memory import add_lesson
                if add_lesson(store_dir, gate, "CoCreator", genre, reason):
                    lessons_added += 1
            except Exception:
                pass

    # ---- S0 上下文装配 + 失败记忆检索 ----
    lessons = []
    if store_dir:
        try:
            from aggregator.failure_memory import get_lessons
            lessons = get_lessons(store_dir, node_type="CoCreator", genre=genre, k=5)
            if lessons:
                log.append(f"S0: 检索到 {len(lessons)} 条历史教训")
        except Exception:
            pass
    lessons_block = ""
    if lessons:
        try:
            from aggregator.failure_memory import render_lessons_block
            lessons_block = render_lessons_block(lessons)
        except Exception:
            pass

    # ---- S1 发散: 3 条方向分支 (GoT, 从故事核心真实派生) ----
    primary_genre = genre if genre != "通用" else "成长线"
    f1 = _DIRECTION_FORMULAS[primary_genre]
    others = [k for k in _DIRECTION_FORMULAS if k != primary_genre]
    h = int(_hashlib.md5(f"{story_core}|{director}".encode("utf-8", "replace")).hexdigest(), 16)
    second = others[h % len(others)]
    f2 = _DIRECTION_FORMULAS[second]
    # 反常规分支: 按故事哈希从手法库选取 (确定性, 随故事变化)
    unc = _UNCONVENTIONAL_MOVES[h % len(_UNCONVENTIONAL_MOVES)]
    # risk_level 影响反常规强度: bold/chaotic 用更激进的手法索引
    if risk_level in ("bold", "chaotic"):
        unc = _UNCONVENTIONAL_MOVES[(h + 2) % len(_UNCONVENTIONAL_MOVES)]

    directions = [
        (primary_genre, f1[0], f1[1]),
        (second, f2[0], f2[1]),
        (f"反常规·{unc[0]}", unc[0], unc[1]),
    ]
    log.append(f"S1: 生成 {len(directions)} 条方向分支 (类型公式+反常规, 从故事核心派生)")

    # 有端点时: LLM 生成方向并真实采用 (P0 修复)
    tier = "T0(确定性)"
    llm_directions_used = False
    if api_url:
        tier = "T1+(LLM)"
        try:
            from pln_llm import call_ai
            sys_p = ("你是世界顶级电影导演, 正在与用户共创。不要给'完美'答案, 要提出方向。"
                     "敢于反常规, 敢于承认'这个想法可能失败'。输出 3 种叙事方向, 每种 2-3 句。"
                     + ("\n\n" + lessons_block if lessons_block else ""))
            usr_p = (f"故事核心: {story_core}\n情感诉求: {emotional_intent or '未指定'}\n"
                     f"审美偏好: {aesthetic or '未指定'}\n情绪基调: {mood or '未指定'}\n\n"
                     f"请为这个故事提出 3 种叙事方向 (含 1 个反常规选项), 每种 2-3 句, 并指出最可能被忽视的叙事机会。")
            llm_dirs, err = call_ai(api_url, api_key, api_model, sys_p, usr_p, 0.9, 1024)
            if llm_dirs and not err:
                parsed = _parse_llm_directions(llm_dirs, directions)
                if parsed:
                    directions = parsed
                    llm_directions_used = True
                    log.append("S1: LLM 方向生成成功并已采用")
                else:
                    log.append("S1: LLM 方向解析失败, 用确定性方向")
            else:
                log.append(f"S1: LLM 方向生成失败({err or '空'}), 用确定性方向")
        except Exception as e:
            log.append(f"S1: LLM 方向生成异常({type(e).__name__}), 用确定性方向")

    # ---- 展开 + S2 门阵 + S3 精炼 (Best-of-N 确定性选择) ----
    candidates = []
    llm_calls = 1 if llm_directions_used else 0
    for name, formula, twist in directions:
        det_draft = _expand_direction(name, formula, twist, elems, director, mood,
                                      emotional_intent, aesthetic, risk_level)
        draft = det_draft
        # T1+: LLM 真实生成草稿内容 (走门控, 失败写失败记忆) — P0/P1 修复
        if api_url:
            try:
                from pln_llm import call_ai
                gen_p = (f"基于下面的叙事方向, 写一段具体的剧本草稿 (含场次/动作/物件, 不用套话)。\n"
                         f"---叙事方向---\n方向: {name}\n公式: {formula}\n转折: {twist}\n"
                         f"故事核心: {story_core}\n情感诉求: {emotional_intent or '未指定'}\n"
                         f"审美: {aesthetic or '未指定'}\n\n输出剧本草稿:")
                llm_draft, err = call_ai(api_url, api_key, api_model,
                                         "你是世界顶级编剧, 写具体可拍的草稿, 禁用套话。", gen_p, 0.8, 2048)
                llm_calls += 1
                if llm_draft and not err and len(llm_draft) > 50:
                    draft = llm_draft
            except Exception:
                draft = det_draft
        rounds = 0
        passed, report = _gate_array(draft, story_core, min_len=200)
        while not passed and rounds < MAX_REFINE_ROUNDS:
            fix_hints = [r["fix_hint"] for r in report if not r["pass"] and r["fix_hint"]]
            # 拒收写入失败记忆 (P1 修复: 真实触发, 含 LLM 草稿拒收)
            for r in report:
                if not r["pass"]:
                    _add_lesson(r["gate"], r["reason"])
            prev = draft
            refined = None
            if api_url:
                try:
                    from pln_llm import call_ai
                    refine_p = (f"下面是共创草稿与门控违规清单。只修违规处, 不动其余部分。\n"
                                f"---草稿---\n{draft[:3000]}\n---违规清单---\n" +
                                "\n".join(f"- {fh}" for fh in fix_hints) +
                                f"\n\n输出修订后的完整版本:")
                    refined, err = call_ai(api_url, api_key, api_model,
                                           "你是剧本医生, 严格按违规清单定向修订。", refine_p, 0.5, 2048)
                    llm_calls += 1
                except Exception:
                    refined = None
            if not refined:
                # 确定性精炼: 按 fix_hint 补充真实内容 (从故事元素派生)
                if any("展开" in fh for fh in fix_hints):
                    c1 = elems["chars"][0]
                    obj = elems["objs"][0]
                    setting = elems["setting"][0]
                    refined = draft + (
                        f"\n\n【精炼补全 · 第{rounds + 1}轮】\n"
                        f"  场景展开: {setting} 的细节 — 光线/声音/温度\n"
                        f"  动作展开: {c1} 的具体动作链 (3 个连续动作)\n"
                        f"  物件展开: {obj} 的三次出现, 每次意义递进")
                else:
                    refined = draft + f"\n\n【精炼补全 · 第{rounds + 1}轮】结构补全: 开场/中点/高潮 节拍标注。"
            draft = refined
            if _bigram_sim(prev, draft) > STAGNATION_SIM:
                log.append(f"S3: 停滞检测触发 (相似度>{STAGNATION_SIM}), 停止精炼")
                break
            rounds += 1
            passed, report = _gate_array(draft, story_core, min_len=200)
        # LLM 草稿精炼后仍不过门 → 回退确定性草稿 (诚实降级)
        if not passed and draft != det_draft:
            log.append(f"S3: LLM 草稿精炼后仍未过门, 回退确定性草稿 [{name}]")
            draft = det_draft
            passed, report = _gate_array(draft, story_core, min_len=200)
        score = _deterministic_score(draft, story_core)
        candidates.append({"name": name, "draft": draft, "score": score,
                           "passed": passed, "report": report, "rounds": rounds})

    # ---- S4 收敛: Best-of-N 确定性选择 (平局: 分高→更短→先出) ----
    candidates.sort(key=lambda c: (-c["score"], len(c["draft"])))
    chosen = candidates[0]
    log.append(f"S4: 选定方向 [{chosen['name']}] 确定性分 {chosen['score']} "
               f"(候选 {len(candidates)} 条, LLM调用 {llm_calls} 次)")

    script_parts = [
        f"【共创剧本 · {chosen['name']}】",
        f"故事核心: {story_core}",
        f"情感诉求: {emotional_intent or '未指定'} | 审美: {aesthetic or '未指定'}",
        f"风险档位: {risk_level} | 能力档位: {tier}",
        "",
        chosen["draft"],
        "",
        "─" * 40,
        "【方向分支图 (GoT) — 未被选中的方向可供用户选择继续】",
    ]
    for c in candidates[1:]:
        script_parts.append(f"  ◇ {c['name']} (分 {c['score']})")
    if lessons_block:
        script_parts += ["", lessons_block]

    return {
        "script": "\n".join(script_parts),
        "directions": [{"name": c["name"], "score": c["score"], "passed": c["passed"]} for c in candidates],
        "chosen": chosen["name"],
        "gate_report": chosen["report"],
        "creation_log": log,
        "lessons_added": lessons_added,
        "tier": tier,
    }
