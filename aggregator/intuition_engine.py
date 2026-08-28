# -*- coding: utf-8 -*-
"""
V15.0-MERGED 直觉引擎 (Intuition Engine)
=========================================
确定性反常规镜头语法引擎 — 修正版 (否决原提案的 random() 实现)。

每条规则都有真实的作者电影依据 (不是编造的"直觉"):
  R1 高潮静止   — 哈内克《隐藏摄影机》: 情绪顶点用不动的镜头, 让观众无处可逃
  R2 亲密远景   — 侯孝贤/罗伊·安德森: 亲密时刻反而用远景, 拒绝消费情感
  R3 喧闹后静默 — 是枝裕和: 高张力镜头之后留一镜静默, 情绪需要落地
  R4 孤独不对称 — 王家卫: 孤独人物置于画面边缘/不对称构图
  R5 物件代反应 — 小津: 情绪节拍切物件空镜而非人物反应 (物哀)
  R6 对白后留白 — 蔡明亮: 对白结束后镜头继续停留, 让沉默成为内容
  R7 打破第四墙 — bold/chaotic 档: 人物直视镜头 (《Persona》/《伦敦生活》)
  R8 跳切连续动作 — 戈达尔《精疲力尽》: 连续动作中跳切, 制造时间的断裂

风险分级 (确定性触发率, 哈希选择触发镜头, 无 random):
  none=不启用  safe=12%  medium=30%  bold=55%  chaotic=85%+全规则
"""
import hashlib as _hashlib

RISK_RATES = {"safe": 12, "medium": 30, "bold": 55, "chaotic": 85}
RISK_LEVELS = ["无", "safe", "medium", "bold", "chaotic"]

_HIGH_TENSION = 8
_INTIMATE_KEYWORDS = ("对话", "对坐", "两人", "父女", "母子", "情侣", "餐桌", "厨房", "卧室")
_LONELY_KEYWORDS = ("孤独", "独自", "一个人", "空", "寂寞", "离别")


def _fires(shot_n, rule_id, seed, rate):
    h = int(_hashlib.md5(f"{shot_n}|{rule_id}|{seed}".encode("utf-8", "replace")).hexdigest(), 16)
    return (h % 100) < rate


def apply_intuition(shots, mood="", scene="", risk_level="medium", seed=""):
    """对分镜 shot 列表应用确定性反常规规则.

    shots: list of dict (含 size/move/focal/dur/focus/sound/n 等字段)
    返回 (modified_shots, log) — log 为每条触发的规则记录 (可追溯)。
    V16.3.0 对抗修复: 非 list 输入 (如畸形 JSON 的字符串) 原样返回, 不崩溃不伪造。
    """
    if not isinstance(shots, list):
        return shots, []
    if risk_level not in RISK_RATES or not shots:
        return shots, []
    rate = RISK_RATES[risk_level]
    chaotic = risk_level == "chaotic"
    _seed = f"{seed}|{mood}|{scene}"
    mood_s = str(mood or "")
    scene_s = str(scene or "")
    intimate = any(k in scene_s for k in _INTIMATE_KEYWORDS)
    lonely = any(k in mood_s for k in _LONELY_KEYWORDS) or any(k in scene_s for k in _LONELY_KEYWORDS)

    out = []
    log = []
    n = len(shots)
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            out.append(s)
            continue
        s = dict(s)
        shot_n = s.get("n", i + 1)
        tension = s.get("tension_level", 5)
        try:
            tension = int(tension)
        except Exception:
            tension = 5
        dur_sec = s.get("dur_sec")
        if dur_sec is None:
            try:
                dur_sec = float(str(s.get("dur", "5")).replace("s", ""))
            except Exception:
                dur_sec = 5.0

        # R1 高潮静止: 张力>=8 → 固定机位 + 时长拉长 1.5x (上限 60s)
        if tension >= _HIGH_TENSION and _fires(shot_n, "R1", _seed, rate):
            s["move"] = "固定(高潮静止)"
            s["dur"] = f"{min(60.0, round(dur_sec * 1.5, 1))}s"
            s["dur_sec"] = min(60.0, round(dur_sec * 1.5, 1))
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R1·高潮静止: 镜头不动, 让观众无处可逃(哈内克)〕"
            log.append({"镜": shot_n, "规则": "R1 高潮静止", "依据": "哈内克"})

        # R2 亲密远景: 亲密场景 + 特写/近景 → 远景 (拒绝消费情感)
        if intimate and str(s.get("size", "")) in ("特写", "大特写", "近景") and _fires(shot_n, "R2", _seed, rate):
            s["size"] = "远景"
            s["focal"] = "24mm"
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R2·亲密远景: 亲密时刻退到远景, 不消费情感(侯孝贤)〕"
            log.append({"镜": shot_n, "规则": "R2 亲密远景", "依据": "侯孝贤/罗伊·安德森"})

        # R3 喧闹后静默: 上一镜张力>=7 → 本镜声音改静默
        if i > 0:
            try:
                prev_t = int(shots[i - 1].get("tension_level", 5))
            except Exception:
                prev_t = 5
            if prev_t >= 7 and _fires(shot_n, "R3", _seed, rate):
                s["sound"] = "静默(前镜喧闹的余波)"
                s["focus"] = str(s.get("focus", "")) + "。〔直觉R3·喧闹后静默: 情绪需要落地(是枝裕和)〕"
                log.append({"镜": shot_n, "规则": "R3 喧闹后静默", "依据": "是枝裕和"})

        # R4 孤独不对称: 孤独情绪 → 构图边缘化标注
        if lonely and _fires(shot_n, "R4", _seed, rate):
            s["angle"] = str(s.get("angle", "平视")) + "·不对称构图"
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R4·孤独不对称: 人物置于画面边缘(王家卫)〕"
            log.append({"镜": shot_n, "规则": "R4 孤独不对称", "依据": "王家卫"})

        # R5 物件代反应: 情绪节拍(张力6-7) → 切物件空镜
        if 6 <= tension <= 7 and _fires(shot_n, "R5", _seed, rate):
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R5·物件代反应: 切物件空镜代替人物反应(小津物哀)〕"
            s["cut"] = "切物件空镜"
            log.append({"镜": shot_n, "规则": "R5 物件代反应", "依据": "小津安二郎"})

        # R6 对白后留白: 最后一镜 → 时长 +3s 留白
        if i == n - 1 and _fires(shot_n, "R6", _seed, rate):
            s["dur"] = f"{round(dur_sec + 3.0, 1)}s"
            s["dur_sec"] = round(dur_sec + 3.0, 1)
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R6·对白后留白: 对白结束镜头不停, 沉默成为内容(蔡明亮)〕"
            log.append({"镜": shot_n, "规则": "R6 对白后留白", "依据": "蔡明亮"})

        # R7 打破第四墙: bold/chaotic 档, 低概率
        if risk_level in ("bold", "chaotic") and _fires(shot_n, "R7", _seed, 15 if not chaotic else 30):
            s["angle"] = str(s.get("angle", "平视")) + "·直视镜头"
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R7·打破第四墙: 人物直视镜头(《Persona》)〕"
            log.append({"镜": shot_n, "规则": "R7 打破第四墙", "依据": "伯格曼"})

        # R8 跳切连续动作: 运动镜头 → 跳切标注
        if str(s.get("move", "")) in ("跟拍", "手持", "推近") and _fires(shot_n, "R8", _seed, rate if not chaotic else 95):
            s["cut"] = "跳切(连续动作中)"
            s["focus"] = str(s.get("focus", "")) + "。〔直觉R8·跳切连续动作: 时间的断裂(戈达尔)〕"
            log.append({"镜": shot_n, "规则": "R8 跳切连续动作", "依据": "戈达尔"})

        out.append(s)
    return out, log
