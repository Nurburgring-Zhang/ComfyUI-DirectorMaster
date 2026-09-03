# -*- coding: utf-8 -*-
"""
SHOT_MEMORY 分镜决策卡 (批次4 builder-m1)
==========================================
追加写 cards.jsonl 决策记忆。纪律 (验收②, 钉死):
  - signal ∉ 已验证信号 且 status==candidate 的卡不产生正面教训注入
    (is_positive_lesson=False, prompt 显式标注 "未验证·不作正面教训");
  - rejected 卡保留为负面证据, 被否方案字段必填 (add_card 缺失即拒绝)。
存储: <out_dir>/dm_memory/<safe_project>/cards.jsonl (UTF-8 追加写)。
入库前脱敏 (R1 HIGH-1 接线): add_card 落盘前对自由文本字段 (标题/方案/教训/被否方案
及嵌套容器) 递归 redact; 结构字段 (signal/status/card_id/镜号等) 不碰; card 哈希在
脱敏后计算保证稳定。读取容错 (R1 MED-2): 二进制损坏行按占位解码后走 json 跳过逻辑,
损坏行跳过、合法行照常消费, 写路径不被损坏锁死。
"""
import hashlib
import json
import os
import re
import sys
import threading
import time

from . import redaction, schema

CARD_PROMPT_MAX = schema.CARD_PROMPT_MAX
CARD_VERIFIED_SIGNALS = schema.CARD_VERIFIED_SIGNALS

# 同源配方: version_store._lock_for 同款进程内按路径互斥锁 (自实现, 不 import 其私有函数)
_PATH_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def _lock_for(path):
    with _LOCKS_GUARD:
        if len(_PATH_LOCKS) > 1024:
            for k in [p for p, lk in _PATH_LOCKS.items() if not lk.locked()]:
                _PATH_LOCKS.pop(k, None)
        lk = _PATH_LOCKS.get(path)
        if lk is None:
            lk = threading.Lock()
            _PATH_LOCKS[path] = lk
        return lk


def _safe_name(s):
    # 同源配方 + R1 MED-3/R2 MED-2 碰撞防护 (仅 dm_memory 层, version_store 不含此防护):
    # ① 替换/strip/截断发生信息丢失 ("夜景/布光"≠"夜景:布光"、>40 截断各异名),
    # ② 安全名含 ASCII 字母 (NTFS 大小写折叠: "Film"≠"film"), ③ 以 ./空格结尾
    # (Windows 剥尾: "proj."≠"proj") — 任一命中即追加原名短 sha1 后缀 (sha1 基于
    # 原始 raw, 确定性跨进程稳定), 不同原名绝不共用同一目录; 纯中文/纯数字名零漂移。
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\\/:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


def _cards_path(memory):
    return os.path.join(memory.out_dir, "dm_memory", _safe_name(memory.project), "cards.jsonl")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def is_positive_lesson(card):
    """验收②纪律: 已验证信号 或 status==confirmed 才可作正面教训;
    未验证生成 (signal∉VERIFIED 且 status==candidate) 与 rejected 卡一律 False。"""
    if not isinstance(card, dict):
        return False
    if card.get("status") == "rejected":
        return False
    return card.get("signal") in CARD_VERIFIED_SIGNALS or card.get("status") == "confirmed"


def add_card(memory, entry):
    """校验并追加一张决策卡 -> (card_id|None, reason)。非法/缺被否方案一律拒绝不落盘。
    落盘前对自由文本字段入库脱敏 (R1 HIGH-1); card 哈希在脱敏后计算保证稳定。"""
    if not isinstance(entry, dict):
        return None, "决策卡不是 dict"
    ok, errors = schema.validate_card(entry)
    if not ok:
        return None, "卡校验失败: " + "; ".join(errors)
    path = _cards_path(memory)
    with _lock_for(path):
        seq = 0
        needs_nl = False
        if os.path.exists(path):
            # 二进制计数 (R1 MED-2): 非法字节行不再炸 UnicodeDecodeError, 照常计入行数
            with open(path, "rb") as f:
                seq = sum(1 for line in f if line.strip())
                # 写路径自愈 (R1 MED-2): 末尾缺换行 (历史损坏数据) 时补边界,
                # 保证追加卡独立成行可被 json 行解析消费 — 损坏不锁死写路径。
                if f.seek(0, os.SEEK_END) > 0:
                    f.seek(-1, os.SEEK_END)
                    needs_nl = f.read(1) != b"\n"
        # 入库脱敏 (R1 HIGH-1): 只动自由文本字段, 结构字段原样; 脱敏永不致命
        card = redaction.redact_free_text(dict(entry))
        # 序列化兜底 (R2 LOW-3): JSON 不可序列化的额外字段 (bytes/循环引用) 走
        # 既有 (None, reason) 契约, 不再抛 TypeError/ValueError, 零落盘
        try:
            digest = hashlib.sha256(
                json.dumps(card, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()[:8]
        except (TypeError, ValueError) as e:
            return None, f"卡含 JSON 不可序列化字段 ({type(e).__name__}), 不落盘"
        card["card_id"] = f"card-{seq + 1:04d}-{digest}"
        card.setdefault("created_at", _now())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(("\n" if needs_nl else "") + json.dumps(card, ensure_ascii=False) + "\n")
    return card["card_id"], ""


def _looks_like_card(card):
    """幽灵卡软过滤 (R2 LOW-1): errors="replace" 可把二进制坏行"修复"成合法 JSON,
    这类行缺卡片标识字段 — 至少含 signal/标题/title/card_id 之一才当卡片消费。"""
    return any(k in card for k in ("signal", "标题", "title", "card_id"))


def list_cards(memory, filters=None):
    """读取决策卡 (追加序), filters 为字段等值过滤; 损坏行诚实跳过不伪造。
    二进制容错 (R1 MED-2): 非法 UTF-8 字节行降级为占位后走 json 跳过逻辑 —
    损坏行跳过、合法行照常消费, 读取路径不被损坏锁死。
    幽灵卡软过滤 (R2 LOW-1): decode 后恰为合法 JSON 的坏行 (缺卡片标识字段) 跳过
    并 stderr 告警计数, 不进列表与检索索引。"""
    path = _cards_path(memory)
    if not os.path.exists(path):
        return []
    out = []
    ghosts = 0
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except Exception:
                continue
            if not isinstance(card, dict):
                continue
            if not _looks_like_card(card):  # 幽灵卡: 缺 signal/标题/title/card_id 之一
                ghosts += 1
                continue
            if filters and not all(card.get(k) == v for k, v in filters.items()):
                continue
            out.append(card)
    if ghosts:
        try:
            sys.stderr.write(
                f"[DirectorMaster] cards.jsonl 有 {ghosts} 行疑似幽灵卡 (缺卡片标识字段), "
                f"已跳过: {path}\n")
        except Exception:
            pass
    return out


def card_to_prompt(card):
    """决策卡 → 注入提示词段 (≤CARD_PROMPT_MAX 字符)。
    未验证卡显式标注不作正面教训; rejected 卡以负面证据呈现, 不冒充正面教训。"""
    if not isinstance(card, dict):
        return ""
    head = f"【决策卡 {card.get('card_id') or '?'}】{str(card.get('标题') or '').strip()}"
    meta = f"信号:{card.get('signal', '')} 状态:{card.get('status', '')}"
    if card.get("status") == "rejected":
        meta += " 已否决"
    elif not is_positive_lesson(card):
        meta += " 未验证·不作正面教训"
    else:
        meta += " 已验证"
    text = head + "\n" + meta
    fields = []
    if str(card.get("方案") or "").strip():
        fields.append(("方案", str(card["方案"]).strip()))
    if str(card.get("教训") or "").strip():
        fields.append(("教训", str(card["教训"]).strip()))
    if card.get("status") == "rejected" and str(card.get("被否方案") or "").strip():
        fields.append(("负面证据·被否方案", str(card["被否方案"]).strip()))
    for label, val in fields:
        if len(text) + len(label) + len(val) + 2 <= CARD_PROMPT_MAX:
            text += f"\n{label}:{val}"
            continue
        budget = CARD_PROMPT_MAX - len(text) - len(label) - 3
        if budget >= 12:
            text += f"\n{label}:{val[:budget]}…"
        break
    return text[:CARD_PROMPT_MAX]
