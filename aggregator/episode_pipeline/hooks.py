# -*- coding: utf-8 -*-
"""episode_pipeline/hooks.py — 集尾钩子三指标确定性启发式 (批次7 builder-e2, V17.0.0)
====================================================================================
m1 悬念/未决冲突: 尾段窗口内悬念问句 + 未决标记词表命中 (词表完全自研, 与
wind-comic 无代码/词表借鉴 — 仅"集尾钩子量化"思想层转译)。
m2 主角赌注/危机: 主角名 (episode["主角"] 显式给出, 否则从集内文本按"常见姓氏
+出现次数≥2"确定性挖掘) 出现于尾段 且 危机/赌注词表命中。
m3 新信息揭示: 尾段新信息揭示标记词表命中。

全部纯确定性: 无随机/无时间/无 locale/无 dict 迭代序依赖 (词表用 tuple, 排序用
显式 key); 只标记不阻断 — hook_check 永不抛错 (欠钩子 → flags 显式列出)。
阈值常量导出: HOOK_THRESHOLD_M1/M2/M3, 尾段窗口 HOOK_ENDING_WINDOW_CHARS。
"""
import re as _re

HOOK_ENDING_WINDOW_CHARS = 400   # 尾段窗口: episode["text"] 最后 N 字
HOOK_THRESHOLD_M1 = 0.5
HOOK_THRESHOLD_M2 = 0.5
HOOK_THRESHOLD_M3 = 0.5

# ---------- 自研 cue 词表 (tuple 保序, 全子串匹配) ----------
_QUESTION_CHARS = ("？", "?")

_M1_UNRESOLVED_CUES = (
    "未解", "无解", "不得而知", "无人知晓", "没有人知道", "没人知道",
    "没有回答", "没人回答", "没有人回答", "无人应答", "没人应答", "没有答案", "悬而未决",
    "不知去向", "下落不明", "杳无音信", "尚未揭晓", "还没有揭晓",
    "谜团", "谜底", "谁也没想到", "谁曾想", "谁都没有料到",
    "暗中", "埋伏", "守候", "等待消息", "等待天亮", "停在半空",
)

_M2_CRISIS_CUES = (
    "危险", "告急", "命悬一线", "生死", "垂危", "重伤", "见血", "流血",
    "追杀", "围杀", "伏击", "偷袭", "爆炸", "坍塌", "起火", "失火",
    "沉没", "坠崖", "坠落", "濒死", "绝境", "被困", "困在", "包围",
    "挟持", "绑架", "威胁", "走投无路", "来不及", "中毒", "刀锋", "枪口",
)

_M2_STAKES_CUES = (
    "赌上", "赌注", "押上", "代价", "拼命", "孤注一掷", "背水一战",
    "最后机会", "最后一次", "再不", "错过", "失去", "生死攸关",
    "身家性命", "全部家当", "不得不", "只能", "豁出去",
)

_M3_REVEAL_CUES = (
    "原来", "真相", "竟然是", "居然是", "发现", "暴露", "揭穿", "揭开",
    "揭晓", "坦白", "承认", "供认", "亮出", "摊牌", "说出实情",
    "第一次知道", "头一回知道", "破天荒", "从未见过", "认出",
    "想起", "回忆起", "梦到", "遗物", "密信", "字条", "遗言",
)

# 主角挖掘: 常见姓氏 (确定性白名单) + 高频误报排除表
_SURNAMES = (
    "李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
    "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
    "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
    "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
    "余", "潘", "杜", "戴", "夏", "钟", "汪", "田", "任", "姜",
    "范", "方", "石", "姚", "谭", "廖", "邹", "熊", "金", "陆",
    "郝", "孔", "白", "崔", "康", "毛", "邱", "秦", "江", "史",
    "顾", "侯", "邵", "孟", "龙", "万", "段", "雷", "钱", "汤",
)
_NAME_RE = _re.compile("(" + "|".join(_SURNAMES) + ")([一-龥]{1,2})")
# 2 字名误报排除表 (姓+首字 token 形态)
_NAME_STOPLIST = frozenset({
    "王国", "王朝", "王法", "王子", "王后", "王爷", "王公", "王家",
    "天下", "天子", "天才", "子孙", "公子", "夫人", "马上", "天文",
    "地理", "治安", "张力", "白天", "白日", "明白", "清楚", "江南",
    "江北", "江湖", "北京", "南京", "东京", "西安", "大唐", "大宋",
    "大明", "大清", "太守", "大夫", "皇帝", "皇后", "太子", "公主",
    "将军", "丞相", "李子", "张口", "马匹", "马车", "马路",
})

_PROTAGONIST_KEYS = ("主角", "protagonist", "protagonists")
_MAX_PROTAGONISTS = 3
_MIN_NAME_COUNT = 2


def _count_distinct(text, cues):
    """词表命中数 (distinct cue, 只计出现与否; tuple 保序遍历, 无迭代序依赖)."""
    n = 0
    for cue in cues:
        if cue in text:
            n += 1
    return n


def _explicit_protagonists(episode):
    """episode 显式主角字段 (主角/protagonist[s]): str 按分隔符拆, list 取 str 项."""
    for key in _PROTAGONIST_KEYS:
        v = episode.get(key)
        if isinstance(v, str):
            parts = _re.split(r"[,，、;；/|\s]+", v.strip())
            return tuple(p for p in (s.strip() for s in parts) if p)
        if isinstance(v, (list, tuple)):
            return tuple(str(x).strip() for x in v if str(x).strip())
    return ()


def _mine_protagonists(text):
    """从集内文本确定性挖掘主角候选: 姓+首字 (2 字名, 匹配贪心但只取首字防
    "林照推开"整段吞名), 全文出现 ≥2 次; 按 (-出现次数, 名字) 显式排序取前 3
    — 无随机/无迭代序依赖。"""
    counts = {}
    for m in _NAME_RE.finditer(text):
        name = m.group(1) + m.group(2)[:1]
        if name in _NAME_STOPLIST:
            continue
        counts[name] = counts.get(name, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return tuple(name for name, c in ranked
                 if c >= _MIN_NAME_COUNT)[:_MAX_PROTAGONISTS]


def _round4(x):
    return round(x + 0.0, 4)


def hook_metrics(ending_text, episode):
    """三指标打分 (0-1)。ending_text 为调用方截好的尾段文本 (hook_check 用
    HOOK_ENDING_WINDOW_CHARS 截取); episode 用于主角名解析。

    m1 = 0.5*有悬念问句 + 0.25*未决标记数(封顶2, 含未决省略号收尾), 封顶 1.0
    m2 = 主角在尾段 × (0.5*有危机/赌注词命中 + 0.25*命中数(封顶2)), 封顶 1.0
    m3 = 0.5*新信息揭示标记数(封顶2), 封顶 1.0
    """
    if not isinstance(ending_text, str):
        ending_text = ""
    episode = episode if isinstance(episode, dict) else {}

    # --- m1 悬念/未决 ---
    q = 1 if any(ch in ending_text for ch in _QUESTION_CHARS) else 0
    u = _count_distinct(ending_text, _M1_UNRESOLVED_CUES)
    if ending_text.rstrip().endswith("…"):
        u += 1  # 未决省略号收尾计 1 个未决标记
    m1 = min(1.0, 0.5 * q + 0.25 * min(u, 2))

    # --- m2 主角赌注/危机 ---
    protag = _explicit_protagonists(episode) or _mine_protagonists(
        episode.get("text") if isinstance(episode.get("text"), str) else "")
    p = 1 if any(name and name in ending_text for name in protag) else 0
    hits = (_count_distinct(ending_text, _M2_CRISIS_CUES)
            + _count_distinct(ending_text, _M2_STAKES_CUES))
    base = min(1.0, 0.5 * (1 if hits else 0) + 0.25 * min(hits, 2))
    m2 = p * base

    # --- m3 新信息揭示 ---
    r = _count_distinct(ending_text, _M3_REVEAL_CUES)
    m3 = min(1.0, 0.5 * min(r, 2))

    return {
        "m1_cliffhanger": _round4(m1),
        "m2_protagonist_stakes": _round4(m2),
        "m3_new_reveal": _round4(m3),
    }


def hook_check(episode):
    """集尾钩子自检。返回 {"m1","m2","m3","passed","flags"} — 只标记不阻断:
    永不抛错; 欠钩子 → flags 显式列出 (逐指标一句, 顺序 m1→m2→m3)。"""
    flags = []
    try:
        text = episode.get("text") if isinstance(episode, dict) else ""
        ending = text[-HOOK_ENDING_WINDOW_CHARS:] if isinstance(text, str) else ""
        m = hook_metrics(ending, episode if isinstance(episode, dict) else {})
        m1, m2, m3 = m["m1_cliffhanger"], m["m2_protagonist_stakes"], m["m3_new_reveal"]
    except Exception as exc:  # 自检绝不阻断管线: 异常 → 全 0 + 显式 flag
        m1 = m2 = m3 = 0.0
        flags.append("hook_check 内部异常: %s: %s" % (type(exc).__name__, str(exc)[:120]))
        m = {"m1_cliffhanger": m1, "m2_protagonist_stakes": m2, "m3_new_reveal": m3}
    if m1 < HOOK_THRESHOLD_M1:
        flags.append("m1_cliffhanger 欠钩子: %.2f<%.2f (尾段无悬念问句/未决标记)"
                     % (m1, HOOK_THRESHOLD_M1))
    if m2 < HOOK_THRESHOLD_M2:
        flags.append("m2_protagonist_stakes 欠钩子: %.2f<%.2f (尾段缺主角赌注/危机标记)"
                     % (m2, HOOK_THRESHOLD_M2))
    if m3 < HOOK_THRESHOLD_M3:
        flags.append("m3_new_reveal 欠钩子: %.2f<%.2f (尾段无新信息揭示标记)"
                     % (m3, HOOK_THRESHOLD_M3))
    return {
        "m1": m1,
        "m2": m2,
        "m3": m3,
        "passed": not flags,
        "flags": flags,
    }
