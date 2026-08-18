# -*- coding: utf-8 -*-
"""
V15.0-MERGED 灵魂引擎 (Soul Engine)
====================================
修正版实现 — 否决原提案的 random.choice(罐头句)。

核心原则: 灵魂片段必须从用户输入派生 (创作者体验文本 + 场景元素),
绝不使用预制的通用句子。全确定性。

三层情感模型:
  表面层 — 来自情绪基调/导演意图的显性情绪
  深层   — 表面情绪的压抑对应面 (愤怒→受伤, 幽默→悲伤, 控制→恐惧…)
  潜意识 — 场景物件的意象联想 (物件→记忆/身体/时间的意象)

叙事装置 (按剧本特征确定性选择):
  伏笔 — 剧本含隐藏/秘密/谎言特征
  反转 — 剧本含矛盾/反转/背叛特征
  留白 — 默认: 不说的比说的更重要
"""
import hashlib as _hashlib
import re as _re

# 表面情绪 → 被压抑的深层情绪 (真实的心理对应, 非随机)
_DEEP_MAP = {
    "愤怒": "受伤", "悲伤": "不舍", "恐惧": "渴望安全", "孤独": "渴望被看见",
    "快乐": "害怕失去", "幽默": "悲伤", "焦虑": "失控感", "控制": "恐惧",
    "嫉妒": "自卑", "骄傲": "脆弱", "冷漠": "曾经在乎", "温柔": "害怕辜负",
    "思念": "无法告别", "愧疚": "渴望原谅", "绝望": "残存的希望",
}

# 物件类别 → 潜意识意象 (物件作为记忆的载体)
_OBJECT_IMAGERY = [
    (r"(信|照片|相册|日记|录音)", "记忆的物证 — 它记得人不记得的事"),
    (r"(钥匙|门|锁)", "入口与拒绝 — 能打开的从来不是锁"),
    (r"(表|钟|时间)", "时间的物证 — 它走它的, 人走人的"),
    (r"(杯|碗|筷|餐桌|食物)", "共同生活的遗迹 — 温度散了, 位置还在"),
    (r"(衣|裙|鞋|帽)", "身体的缺席 — 衣服还保持着人的形状"),
    (r"(灯|窗|镜)", "看与被看 — 光记得所有发生过的"),
    (r"(花|树|植物)", "不问人事的生长 — 它不管人间的离别"),
    (r"(手机|电话|屏幕)", "连接的幻觉 — 随时能联系, 却无话可说"),
]

_HIDDEN_KEYWORDS = ("隐藏", "秘密", "谎言", "瞒着", "藏着", "不说", "隐瞒", "埋下")
_TWIST_KEYWORDS = ("反转", "真相", "其实", "原来", "背叛", "出乎意料", "颠覆")


def _stable_pick(options, seed_str):
    if not options:
        return ""
    h = int(_hashlib.md5(seed_str.encode("utf-8", "replace")).hexdigest(), 16)
    return options[h % len(options)]


def _extract_motifs(experience_text):
    """从创作者体验文本提取母题候选 (轻量名词性片段, 确定性)."""
    t = str(experience_text or "").strip()
    if not t:
        return []
    # 按标点切分, 保留 2-12 字的片段
    segs = [s.strip() for s in _re.split(r"[,，。；;！!？?、\n]+", t) if s.strip()]
    motifs = []
    for s in segs:
        s = s[:12]
        if 2 <= len(s) <= 12 and not _re.fullmatch(r"[的了是在有和与]+", s):
            motifs.append(s)
    # 确定性去重保序
    seen = set()
    out = []
    for m in motifs:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out[:6]


def _deep_emotion(surface):
    s = str(surface or "")
    for k, v in _DEEP_MAP.items():
        if k in s:
            return v
    return "未说出口的" + (s[:4] if s else "情绪")


def _subconscious_imagery(objects):
    """场景物件 → 潜意识意象 (类别模板, 诚实标注为意象层)."""
    out = []
    for obj in objects[:3]:
        o = str(obj)
        for pat, imagery in _OBJECT_IMAGERY:
            if _re.search(pat, o):
                out.append(f"{o}: {imagery}")
                break
    return out


def _select_device(script_text):
    """叙事装置选择 — 用较强的专属信号, 避免高频虚词误判.
    伏笔需'隐藏类'动词, 反转需'真相/反转类'名词; 均无则留白。"""
    t = str(script_text or "")
    hidden_hits = sum(1 for k in _HIDDEN_KEYWORDS if k in t)
    twist_hits = sum(1 for k in _TWIST_KEYWORDS if k in t)
    if hidden_hits >= twist_hits and hidden_hits > 0:
        return "伏笔", "前期埋下的细节必须在后期揭示 — 观众第二次看时全部成立"
    if twist_hits > 0:
        return "反转", "打破预期但合情合理 — 反转前所有细节为反转服务"
    return "留白", "不说的比说的更重要 — 把最关键的话留在沉默里"


def inject_soul(script_text, creator_experience="", emotional_intent="", scene="", objects=None, characters=None):
    """把创作者体验转译为灵魂层注入剧本.

    返回 dict: {script, fragments, layers, device}
    fragments 全部从输入派生 (无罐头句)。
    """
    script = str(script_text or "")
    scene_s = str(scene or "")
    objs = objects if objects else []
    chars = characters if characters else []
    if not objs and scene_s:
        try:
            from aggregator.scene_engine import parse_scene
            p = parse_scene(scene_s)
            objs = p.get("objects") or []
            chars = chars or (p.get("characters") or [])
        except Exception:
            pass

    motifs = _extract_motifs(creator_experience)
    surface = str(emotional_intent or "").strip() or "未指定"
    deep = _deep_emotion(surface)
    imagery = _subconscious_imagery(objs)
    device_name, device_rule = _select_device(script)

    fragments = []
    # 母题 → 物件/动作/沉默 三种载体 (确定性分配)
    carriers = ["物件", "动作", "沉默"]
    for i, m in enumerate(motifs):
        carrier = carriers[i % 3]
        if carrier == "物件" and objs:
            anchor = _stable_pick(objs, f"{m}|{scene_s}")
            fragments.append(f"〔灵魂母题·物件〕把「{m}」藏进 {anchor} — 它出现三次, 每次意义不同")
        elif carrier == "动作" and chars:
            who = _stable_pick(chars, f"{m}|act|{scene_s}")
            fragments.append(f"〔灵魂母题·动作〕让 {who} 用一个动作承载「{m}」— 动作先于台词泄露")
        else:
            fragments.append(f"〔灵魂母题·沉默〕「{m}」不被说出 — 用一镜沉默让它在场")

    layers = {
        "表面": surface,
        "深层": f"{surface} 之下是 {deep}",
        "潜意识": imagery if imagery else ["(场景物件未提供潜意识锚点)"],
    }

    # 注入块 (附加在剧本后, 作为灵魂层标注)
    block_lines = ["", "─" * 40, "【灵魂层注入 (V15.0 Soul Engine)】"]
    block_lines.append(f"叙事装置: {device_name} — {device_rule}")
    block_lines.append(f"情感三层: 表面={surface} | 深层={deep}")
    if imagery:
        block_lines.append("潜意识意象:")
        block_lines.extend(f"  {x}" for x in imagery)
    if fragments:
        block_lines.append("灵魂母题 (来自创作者体验):")
        block_lines.extend(f"  {f}" for f in fragments)
    else:
        block_lines.append("灵魂母题: (未提供创作者体验文本 — 灵魂层仅含情感三层与叙事装置)")

    return {
        "script": script + "\n".join(block_lines),
        "fragments": fragments,
        "layers": layers,
        "device": device_name,
        "device_rule": device_rule,
    }
