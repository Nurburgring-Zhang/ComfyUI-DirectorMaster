# -*- coding: utf-8 -*-
"""
aggregator/plot_topology.py — V16.4 情节拓扑引擎 (吸收自 V16.6-AIGC 参考版的真实增量,
按 GitHub 基座的中文 schema 独立重写适配)
================================================================
职责 (全部确定性, md5 种子驱动, 无全局随机, 无外部依赖):
  1. 情节拓扑推断: 波浪式小高潮数 / 反转点数量与位置 / 层层推进 / 线型
  2. 复杂叙事结构检测: 套层叙事 / 罗生门 / 时间循环 / 环形叙事 (手动档 > 关键词 > 无)
  3. 拓扑落实到分镜: 每镜 narrative_tag / tension_level 塑形 / dur_note
     - 波浪: 每波一个局部高潮, 一波高过一波, 最后一波=大高潮
     - 反转点位于波谷 (重置情境开启新一波, 不吞掉前一波峰)
     - 套层: 框架带 (开场 8% 框架, 中段插叙, 92% 收口) → 框架·现在 / 戏中戏 标记
     - 时间循环: 25-72% 循环区, 谷底逐次抬升 (循环中学到东西), 末次循环破局
     - 罗生门: 视角版本带 (A版→B版→C版→真相暗示)
     - 环形: 首尾同点, 结尾标签 首尾呼应·环形闭环
输出:
  infer_plot_topology(...)  → topo dict (纯数据, 可入 meta)
  apply_topology(shots, topo) → (塑造后的 shots, 应用手记) — 仅增量修改
    (新增 narrative_tag/dur_note 键; tension_level 就近取整; 不改动既有键的语义)
"""
import hashlib as _hl
import math as _math

COMPLEX_MODES = ["自动", "无", "套层叙事", "罗生门", "时间循环", "环形叙事"]

_COMPLEX_KW = {
    "套层叙事": ("戏中戏", "框架", "讲述", "回忆往事", "日记里", "信中写道", "旁白讲述",
               "故事里的故事", "剧中剧", "写小说", "戏班里", "排练"),
    "罗生门": ("罗生门", "各执一词", "每个人的说法", "不同版本", "视角不同", "真相不明",
             "谁在撒谎", "供词", "目击者说法不一"),
    "时间循环": ("时间循环", "循环", "重复的一天", "同一天", "重置", "困在", "无限轮回",
               "醒来又是", "土拨鼠", "重来一次", "回到昨天"),
    "环形叙事": ("环形", "首尾呼应", "兜兜转转", "回到原点", "结尾就是开头", "绕了一圈",
               "命运轮回", "起点即终点"),
}
_TWIST_KW = ("反转", "真相", "揭示", "秘密", "身份揭穿", "出乎意料", "意料之外", "背叛",
             "揭穿", "隐藏的")
_ESC_KW = ("升级", "层层", "步步紧逼", "越陷越深", "不断加剧", "雪上加霜", "恶化", "对抗升级")
_FRAME_INNER = "戏中戏"


def _seed_int(*parts):
    raw = "|".join(str(p) for p in parts)
    return int(_hl.md5(raw.encode("utf-8", "replace")).hexdigest(), 16)


def detect_complex_structure(scene, core=None, mode="", complex_opt="自动"):
    """复杂叙事结构检测: 手动档优先 > 关键词推断 > 无. 返回 (结构名, 依据)."""
    if complex_opt and complex_opt != "自动" and complex_opt in COMPLEX_MODES:
        return (None if complex_opt == "无" else complex_opt), "手动指定"
    core = core or {}
    text = " ".join(str(x or "") for x in [
        scene, core.get("_核心冲突", ""), core.get("_主题词", ""), mode])
    # 优先级: 时间循环 > 罗生门 > 套层 > 环形 (循环/罗生门信号更具体)
    for cx in ("时间循环", "罗生门", "套层叙事", "环形叙事"):
        if any(k in text for k in _COMPLEX_KW[cx]):
            return cx, "场景关键词推断"
    return None, ""


def _wave_count(minutes):
    if minutes < 5:
        return 1
    if minutes < 15:
        return 2
    return max(3, min(8, int(minutes // 12)))


def _twist_count(text, minutes):
    if any(k in text for k in ("多次反转", "连环反转", "层层反转")):
        n_tw = 3
    elif any(k in text for k in _TWIST_KW):
        n_tw = 2 if minutes >= 30 else 1
    else:
        n_tw = 0 if minutes < 10 else (1 if minutes < 45 else 2)
    if minutes < 3:
        n_tw = 0
    return n_tw


def infer_plot_topology(scene, core=None, mode="", minutes=120.0,
                        arrangement="跟随叙事结构", lines="单线", complex_opt="自动"):
    """从场景+核心数据包推断情节拓扑 (全确定性).

    返回 topo dict:
      waves / twists / twist_positions / escalation / lines / arrangement /
      complex / complex_why / frame_bands (仅套层) / loop_zone (仅时间循环)
    """
    try:
        minutes = float(minutes)
    except (TypeError, ValueError):
        minutes = 120.0
    minutes = max(0.5, minutes)
    core = core or {}
    text = " ".join(str(x or "") for x in [
        scene, core.get("_核心冲突", ""), core.get("_主题词", ""),
        core.get("_观众承诺", ""), mode])
    n_tw = _twist_count(text, minutes)
    K = 1 if minutes < 5 else (2 if minutes < 15 else max(3, min(8, int(minutes // 12))))
    seg_b = 0.80 / K
    # 反转点位于波段边界 (波谷): 反转重置情境开启新一波
    # (V16.4: 保留 2 位小数 — 遵守项目"浮点≤1位小数输出"纪律, 3 位小数会被浮点伪影扫描命中)
    twist_pos = [round(seg_b * (j + 1) * K / (n_tw + 1), 2) for j in range(n_tw)]
    escalation = any(k in text for k in _ESC_KW) or minutes >= 30
    topo = {
        "waves": _wave_count(minutes),
        "twists": n_tw,
        "twist_positions": twist_pos,
        "escalation": escalation,
        "lines": lines,
        "arrangement": arrangement,
    }
    cx, cx_why = detect_complex_structure(scene, core, mode, complex_opt)
    topo["complex"] = cx
    topo["complex_why"] = cx_why
    if cx == "套层叙事":
        # 框架带: 开头8%框架开场, 中段每~22%一次框架插叙(3%), 结尾92%起框架收口
        bands = [(0.0, 0.08)]
        b = 0.26
        while b < 0.88:
            bands.append((b, min(b + 0.03, 0.88)))
            b += 0.22
        bands.append((0.92, 1.0))
        topo["frame_bands"] = bands
    elif cx == "时间循环":
        # 循环区 25-72%: 循环次数随时长 (2-4), 每次谷底抬升
        n_loops = 2 if minutes < 30 else (3 if minutes < 90 else 4)
        topo["loop_zone"] = (0.25, 0.72, n_loops)
    elif cx == "罗生门":
        n_ver = 3 if minutes >= 15 else 2
        topo["version_zone"] = (0.15, 0.85, n_ver)
    return topo


def _clamp_tension(v, lo=1, hi=10):
    try:
        v = int(round(float(v)))
    except (TypeError, ValueError):
        v = 5
    return max(lo, min(hi, v))


_SIZE_LADDER = ["大远景", "远景", "全景", "中景", "中近景", "近景", "特写", "大特写"]


def _phase_band(phase):
    """阶段 → 拓扑带 (0 建立 / 1 发展 / 2 高潮 / 3 收束). phase 取值来自长片引擎 (建立/铺垫/转折/高潮/收束 等)."""
    p = str(phase or "")
    if any(k in p for k in ("建立", "开场", "铺垫", "设置")):
        return 0
    if any(k in p for k in ("发展", "推进", "上升")):
        return 1
    if any(k in p for k in ("高潮", "转折", "危机", "对决")):
        return 2
    if any(k in p for k in ("收束", "结局", "尾声", "解决")):
        return 3
    return 1


_LADDER_BY_BAND = {
    0: ["大远景", "远景", "全景"],          # 建立: 广角交代空间
    1: ["全景", "中景", "中近景", "远景"],  # 发展: 中景为主
    2: ["中近景", "近景", "特写", "中景"],  # 高潮: 紧密景别
    3: ["远景", "全景", "大远景", "中景"],  # 收束: 拉远留白
}


def _renorm_durations(shots, budget_sec, seed):
    """V16.4 吸收修复 (批次6 D2 重做第三步): 阶段+张力驱动时长重塑, 总时长精确归一到预算
    (兑现'总时长恒覆盖片长')。

    权重: 低张力(建立/留白)更长, 高张力(高潮/快切)更短, 确定性 jitter 防全同。
    三步闭合: 加权目标 → 精确归一 → 1位小数取整+0.2s 地板, 残差以 0.1s 为单位在能力池内
    迭代摊回 (让出方池=可下探到 0.2s 以上的镜, 吸收方池=全部镜, 每轮重算残差, ≤10 轮,
    按时长比例 largest-remainder 整数摊分, 禁止单镜整包倾倒);
    病态预算 (budget_sec < 0.2s×有效镜数) 诚实跳过: 原时长保留, 返回 (0, total), 绝不产负值。
    返回 (修改的镜数, 原总时长)。"""
    total = 0.0
    n_active = 0
    for s in shots:
        try:
            cur = float(s.get("dur_sec", 0) or 0)
        except (TypeError, ValueError):
            cur = 0.0
        total += cur
        if cur > 0:
            n_active += 1
    if not _math.isfinite(total) or not _math.isfinite(budget_sec):
        return 0, total          # NaN/Inf 预算或时长: 病态输入诚实跳过 (R1 LOW-4, 不抛异常)
    if total <= 1 or budget_sec <= 1:
        return 0, total
    if budget_sec < 0.2 * n_active:
        return 0, total
    # 第一步: 加权目标 (张力驱动 + 确定性 jitter)
    scale = budget_sec / total
    targets = []
    for i, s in enumerate(shots):
        try:
            cur = float(s.get("dur_sec", 0) or 0)
        except (TypeError, ValueError):
            cur = 0.0
        if cur <= 0:
            targets.append(None)
            continue
        t = _clamp_tension(s.get("tension_level", 5))
        base_w = 0.65 + 0.75 * (1.0 - (t - 1) / 9.0)      # 张力1→1.4, 张力10→0.65
        jitter = 0.88 + (((seed >> (i % 12)) & 0xFF) / 255.0) * 0.24   # 0.88..1.12
        targets.append(cur * scale * max(0.2, base_w * jitter))
    # 第二步: 精确归一到预算 (均匀校正)
    tsum = sum(x for x in targets if x)
    if tsum <= 0:
        return 0, total
    corr = budget_sec / tsum
    targets = [None if x is None else x * corr for x in targets]
    # 第三步: 取整+地板, 残差以 0.1s 整数单位迭代摊回 (全程每镜 ≥0.2s)
    durs = [None if x is None else max(0.2, round(x, 1)) for x in targets]
    idx = [i for i, x in enumerate(durs) if x is not None]
    if idx:
        budget_t = int(round(budget_sec * 10))
        durs_t = [None if x is None else int(round(x * 10)) for x in durs]
        for _round in range(10):
            residual_t = budget_t - sum(x for x in durs_t if x is not None)
            if residual_t == 0:
                break
            if residual_t < 0:
                pool = [i for i in idx if durs_t[i] > 2]        # 让出方: 高于 0.2s 地板
                caps = dict((i, durs_t[i] - 2) for i in pool)
            else:
                pool = list(idx)                                 # 吸收方: 全部有效镜
                caps = dict((i, None) for i in pool)
            if not pool:
                break
            pool_sum = sum(durs_t[i] for i in pool)
            alloc = dict((i, 0) for i in pool)
            order = []
            for i in pool:
                ideal = abs(residual_t) * durs_t[i] / pool_sum
                q = int(ideal)
                if caps[i] is not None:
                    q = min(q, caps[i])
                alloc[i] += q
                order.append((ideal - int(ideal), i))
            order.sort(key=lambda p: (-p[0], p[1]))
            leftover = abs(residual_t) - sum(alloc.values())
            while leftover > 0:
                progressed = False
                for _, i in order:
                    if leftover <= 0:
                        break
                    if caps[i] is None or alloc[i] < caps[i]:
                        alloc[i] += 1
                        leftover -= 1
                        progressed = True
                if not progressed:
                    break
            sign = 1 if residual_t > 0 else -1
            for i in pool:
                durs_t[i] += sign * alloc[i]
        final = [None if x is None else x / 10.0 for x in durs_t]
    else:
        final = durs
    changed = 0
    for s, x in zip(shots, final):
        if x is None:
            continue
        try:
            cur = float(s.get("dur_sec", 0) or 0)
        except (TypeError, ValueError):
            cur = 0.0
        if abs(x - cur) >= 0.05:
            s["dur_sec"] = x
            s["dur"] = f"{x:.1f}s"
            changed += 1
        else:
            s["dur_sec"] = round(cur, 1)
    return changed, total


def _apply_size_ladder(shots):
    """V16.4 吸收修复: 景别塌缩 (唯一值 <3) 时按阶段带轮换景别阶梯, 相邻不重复。

    仅修复塌缩, 不动已有多样输出; 用户显式 景别偏好 在上游仍最终生效 (接线顺序: 偏好应用在本函数之后,
    本函数只做'多样性不足'时的兜底轮换)。返回轮换镜数。"""
    sizes = [str(s.get("size", "")) for s in shots if isinstance(s, dict)]
    if len(set(x for x in sizes if x)) >= 3:
        return 0
    changed = 0
    last = None
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            continue
        band = _phase_band(s.get("phase", ""))
        ladder = _LADDER_BY_BAND[band]
        cand = ladder[i % len(ladder)]
        if cand == last:
            ladder2 = _LADDER_BY_BAND[(band + 1) % 4]
            cand = ladder2[i % len(ladder2)]
        if cand != last:
            s["size"] = cand
            last = cand
            changed += 1
    return changed


def apply_topology(shots, topo, scene="", mood="", budget_sec=None, director=""):
    """把拓扑落实到分镜 (仅增量修改; 返回 (shots, 手记)).

    每镜新增:
      narrative_tag — 拓扑位置标签 (第k波·小高潮 / 波谷·过渡 / 反转点 / 框架·现在 / 戏中戏 /
                      第k次循环 / A视角版本 / 首尾呼应·环形闭环 ...)
      dur_note — 复杂结构的节奏手记 (框架间离呼吸 / 破局点 等, 仅必要时)
    tension_level 重塑: 波浪包络 × 复杂结构修饰 (就近视整)。
    V16.4 吸收修复 (来自 V16.6-AIGC 参考版的高价值维度):
      budget_sec 给定时 — 阶段+张力驱动时长重塑, 总时长归一到预算 (兑现"总时长恒覆盖片长")。
      景别塌缩 (唯一值<3) 时 — 阶段带景别阶梯轮换兜底 (相邻不重复)。
    """
    if not isinstance(shots, list) or not shots:
        return shots, []
    n = len(shots)
    if n == 0:
        return shots, []
    notes = []
    cx = (topo or {}).get("complex")
    waves = max(1, int((topo or {}).get("waves", 1)))
    twist_pos = [float(p) for p in (topo or {}).get("twist_positions", [])]
    escalate = bool((topo or {}).get("escalation"))
    seed = _seed_int(scene, mood, cx or "plain", director)

    # 波浪包络: 每波内张力爬升, 波峰=局部高潮, 波谷=过渡; 整体基线随 escalation 抬升
    def envelope(pos):
        wave_id = min(waves - 1, int(pos * waves))
        local = pos * waves - wave_id            # 0..1 波内相位
        peak = 6 + int(round(4 * wave_id / max(1, waves - 1))) if waves > 1 else 9
        base = 3 + (1 if escalate else 0)
        val = base + (peak - base) * local
        # 反转点前后: 波谷压低
        for tp in twist_pos:
            if abs(pos - tp) < 0.015:
                val = min(val, 3.0)
        return _clamp_tension(val)

    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            continue
        pos = i / max(1, n - 1) if n > 1 else 0.0
        wave_id = min(waves - 1, int(pos * waves))
        local = pos * waves - wave_id
        tag_parts = []
        if cx is None:
            if local >= 0.85:
                tag_parts.append(f"第{wave_id + 1}波·小高潮" if wave_id < waves - 1 else "大高潮")
            elif local <= 0.15 and i > 0:
                tag_parts.append("波谷·过渡")
        for tp_i, tp in enumerate(twist_pos):
            if abs(pos - tp) < 0.02:
                tag_parts.append(f"反转点{tp_i + 1}")
        # 复杂结构标记
        if cx == "套层叙事":
            in_band = any(a <= pos <= b for a, b in (topo or {}).get("frame_bands", []))
            s["narrative_tag"] = "框架·现在" if in_band else _FRAME_INNER
            if in_band and 0.2 < pos < 0.9:
                s["dur_note"] = s.get("dur_note") or "框架层·间离呼吸"
            if not tag_parts:
                tag_parts = [s["narrative_tag"]]
            else:
                tag_parts.append(s["narrative_tag"])
        elif cx == "时间循环":
            z = (topo or {}).get("loop_zone")
            if z and z[0] <= pos <= z[1]:
                k = min(z[2] - 1, int((pos - z[0]) / max(1e-6, (z[1] - z[0])) * z[2]))
                s["narrative_tag"] = f"第{k + 1}次循环"
                tag_parts.append(s["narrative_tag"])
                # 谷底逐次抬升 (循环中学到东西)
                if envelope(pos) <= 4:
                    floor = 2.5 + k * (2.2 / max(1, z[2]))
                    s["tension_level"] = _clamp_tension(max(envelope(pos), floor))
            elif pos > (z[1] if z else 0.72):
                s["narrative_tag"] = s.get("narrative_tag") or "破局·循环外"
                if i == n - 1:
                    s["dur_note"] = s.get("dur_note") or "破局点·走出循环"
                tag_parts.append(s["narrative_tag"])
        elif cx == "罗生门":
            z = (topo or {}).get("version_zone")
            names = ["A视角版本", "B视角版本", "C视角版本"]
            if z and z[0] <= pos <= z[1]:
                k = min(z[2] - 1, int((pos - z[0]) / max(1e-6, (z[1] - z[0])) * z[2]))
                s["narrative_tag"] = names[k]
                tag_parts.append(s["narrative_tag"])
            elif pos > (z[1] if z else 0.85):
                s["narrative_tag"] = "真相暗示·拼合"
                tag_parts.append(s["narrative_tag"])
        elif cx == "环形叙事":
            if i == 0:
                s["narrative_tag"] = "起点·环形开场"
                tag_parts.append(s["narrative_tag"])
            elif pos >= 0.82:
                s["narrative_tag"] = "首尾呼应·环形闭环" if i == n - 1 else "回环·渐近起点"
                tag_parts.append(s["narrative_tag"])
                if i == n - 1:
                    s["dur_note"] = s.get("dur_note") or "与第一镜同地点同构图 (首尾闭环)"
        # 张力重塑 (复杂结构内部已个别处理的镜不重复覆盖基础包络)
        if not (cx == "时间循环" and "narrative_tag" in s and "循环" in str(s.get("narrative_tag", ""))
                and s.get("tension_level") is not None and "tension_override" in s):
            s["tension_level"] = envelope(pos)
        # 波峰镜张力显式标记 (供下游 pacing/音乐对位消费)
        if tag_parts and any("高潮" in t for t in tag_parts):
            s["narrative_tag"] = " / ".join(tag_parts)
        elif "narrative_tag" not in s and tag_parts:
            s["narrative_tag"] = " / ".join(tag_parts)
    # 时长归一 (V16.4 吸收修复): 阶段+张力驱动重塑 → 总时长精确覆盖预算
    if budget_sec:
        changed, before = _renorm_durations(shots, float(budget_sec), seed)
        if changed:
            notes.append(f"时长归一: {before:.0f}s → {float(budget_sec):.0f}s ({changed} 镜重塑)")
    # 景别阶梯兜底 (V16.4 吸收修复): 塌缩时按阶段带轮换
    ladder_n = _apply_size_ladder(shots)
    if ladder_n:
        notes.append(f"景别阶梯兜底: {ladder_n} 镜轮换 (塌缩修复)")
    notes.append(f"拓扑: waves={waves} twists={len(twist_pos)} escalate={escalate} complex={cx or '无'}")
    return shots, notes
