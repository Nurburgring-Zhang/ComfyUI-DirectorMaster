# -*- coding: utf-8 -*-
"""
信任序注入 (批次4 builder-m3)
==============================
TRUST_ORDER 钉死: 当前工作流参数 > 用户当前指令 > 记忆卡 > 历史版本。
injection_block(memory, round_no, remind_every=5): 每 remind_every 轮重申一次 —
信任序头 + 风格约束 (项目风格圣经蒸馏段) + 正面教训记忆卡 (只注入已验证卡;
m1 card_to_prompt 已保证未验证卡不产正面教训, 此处再按 is_positive_lesson 过滤双保险)。
无记忆 / 未到重申节奏 / 缺 dm_memory 目录 / 任何异常 → "" (该段整体不出现, 消费方零漂移)。
只读纪律: 绝不创建 dm_memory 目录, 绝不写任何文件 (additive 零漂移硬断言的根基)。
消费接线: aggregator/cinematic_studio.py 分镜提示词面 (调用侧全 try/except 保护)。
"""
import os
import re

TRUST_ORDER = ["当前工作流参数", "用户当前指令", "记忆卡", "历史版本"]
BIBLE_PENDING_MARK = "LLM_DISTILL_PENDING"
_MAX_STYLE_LINES = 8
_STYLE_LINE_MAX = 120
_MAX_CARDS = 5


def _safe_name(s):
    # 同源配方 + R1 MED-3/R2 MED-2 碰撞防护 (仅 dm_memory 层, version_store 不含此防护):
    # ① 替换/strip/截断发生信息丢失, ② 安全名含 ASCII 字母 (NTFS 大小写折叠),
    # ③ 以 ./空格结尾 (Windows 剥尾) — 任一命中即追加原名短 sha1 后缀 (sha1 基于
    # 原始 raw, 确定性), 与写侧各模块同一映射, 保证读取目录与写入目录一致。
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\\/:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def resolve_out_dir():
    """记忆根目录解析 (接线专用, 只读): 环境变量 DM_MEMORY_DIR (须为已存在目录, 便于
    显式指向与测试) > archive_master._get_output_dir (ComfyUI output / 插件 output 既有链)。
    返回 "" 表示无法解析 (调用方跳过记忆段)。绝不创建任何目录。"""
    try:
        env = os.environ.get("DM_MEMORY_DIR", "").strip()
        if env and os.path.isdir(env):
            return env
    except Exception:
        pass
    try:
        from aggregator.archive_master import _get_output_dir
        return _get_output_dir() or ""
    except Exception:
        return ""


def project_rounds(out_dir, project):
    """轮次口径: 项目版本库已提交版本数 (每轮归档提交 = 1 轮); 无库/任何失败 → 0。只读。"""
    try:
        from aggregator.version_store import open_store
        return len(open_store(out_dir, project).data.get("order", []) or [])
    except Exception:
        return 0


class _MemRef:
    """shot_cards.list_cards 所需最小句柄 (out_dir/project 属性)。"""

    def __init__(self, out_dir, project):
        self.out_dir = out_dir
        self.project = project


def _resolve(memory):
    if isinstance(memory, dict):
        out_dir, project = memory.get("out_dir"), memory.get("project")
    else:
        out_dir, project = getattr(memory, "out_dir", None), getattr(memory, "project", None)
    if not out_dir:
        raise ValueError("memory 需含 out_dir (open_memory 句柄或等价 dict)")
    return str(out_dir), str(project or "项目")


def _bible_style_lines(bible_md):
    """bible.md 蒸馏段 → 风格约束行。蒸馏未回填 (占位在) → [] 诚实跳过; 文件缺失/损坏 → []。"""
    try:
        if not os.path.isfile(bible_md):
            return []
        with open(bible_md, "r", encoding="utf-8") as f:
            text = f.read(200_000)
        sec, in_sec = [], False
        for line in text.splitlines():
            if line.startswith("## "):
                in_sec = line.strip().startswith("## 蒸馏段")
                continue
            if in_sec and line.strip():
                sec.append(line.strip())
        if any(BIBLE_PENDING_MARK in ln for ln in sec):
            return []  # 蒸馏未回填: 不把占位当风格结论注入 (不猜测)
        out = []
        for ln in sec:
            ln = ln.lstrip("-• ").strip()
            if ln and ln not in out:
                out.append(ln[:_STYLE_LINE_MAX])
            if len(out) >= _MAX_STYLE_LINES:
                break
        return out
    except Exception:
        return []


def injection_block(memory, round_no, remind_every=5):
    """每 remind_every 轮重申: 信任序头 + 风格约束 + 正面教训记忆卡。
    未到节奏 (round_no ≤ 0 或 % remind_every ≠ 0) / 无记忆内容 / 缺 dm_memory 目录 /
    任何异常 → "" (消费方输出逐字节不变)。全只读。"""
    try:
        try:
            round_no = int(round_no)
            remind_every = int(remind_every)
        except (TypeError, ValueError):
            return ""
        if remind_every <= 0 or round_no <= 0 or round_no % remind_every != 0:
            return ""
        out_dir, project = _resolve(memory)
        dm_dir = os.path.join(out_dir, "dm_memory")
        if not os.path.isdir(dm_dir):
            return ""  # 缺 dm_memory 目录 → 该段整体不出现 (additive 零漂移)
        proj_dir = os.path.join(dm_dir, _safe_name(project))
        style_lines = _bible_style_lines(os.path.join(proj_dir, "bible.md"))
        cards_txt = []
        try:
            from . import shot_cards
            cards = shot_cards.list_cards(_MemRef(out_dir, project))
            positive = [c for c in cards if shot_cards.is_positive_lesson(c)]
            for c in positive[-_MAX_CARDS:]:
                p = shot_cards.card_to_prompt(c)
                if p:
                    cards_txt.append(p)
        except Exception:
            cards_txt = []
        if not style_lines and not cards_txt:
            return ""  # 无记忆内容 → 不注入空段
        lines = [f"【记忆注入 · 第 {round_no} 轮 (每 {remind_every} 轮重申)】"
                 f"信任序: {' > '.join(TRUST_ORDER)}"]
        if style_lines:
            lines.append("【风格约束 (项目风格圣经)】")
            lines.extend(f"- {ln}" for ln in style_lines)
        if cards_txt:
            lines.append("【正面教训记忆卡 (仅已验证)】")
            lines.extend(cards_txt)
        return "\n".join(lines)
    except Exception:
        return ""
