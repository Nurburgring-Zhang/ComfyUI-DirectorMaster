# -*- coding: utf-8 -*-
"""
入库前脱敏 (批次4 builder-m1; R1 修复: 永不致命降级 + LOW-5 绕过面补齐 + 入库接线助手)
====================================================================================
redact(text, whitelist=()) -> (clean, findings)
findings: [{type, placeholder}], type ∈ {phone, email, api_key, private_path}。
  手机号 (1[3-9] 开头 11 位, 含 138-1234-5678 / 138 1234 5678 分隔符形态)
  / 邮箱 / API-key 形态 (sk- 令牌; Bearer 令牌, 含 "Bearer:无空格" 形态;
  keyword:value, 键名含 api_key/token/secret/secret_key/api_token/password/passwd/
  credentials/auth/pwd/密码 等别名, 键值间容忍引号或反斜杠 — 覆盖嵌套 dict str()
  与 JSON 双重转义形态)
  / 盘符私有路径 (盘符 + Users|用户 目录) → 类型化占位符;
  白名单整词豁免 (匹配串或密钥值与白名单项精确相等才豁免, 不做子串放水)。
应用顺序 = 私有路径 → 邮箱 → API-key → 手机号, 防止前类匹配被后类二次击穿。
永不致命 (R1): redact 内部任何异常按原文本放行 + stderr 降级 (与注入接线段同口径)。
redact_free_text(obj, whitelist=()) — 入库前接线专用 (R1 HIGH-1): 仅对自由文本键
(TEXT_REDACT_KEYS 及其嵌套容器内) 的字符串值递归 redact; 数值/seed/id/enum/counts
等结构字段一律不碰 (宁可漏脱不可破坏数据结构); 任何异常整体按原值放行。
"""
import re
import sys

PLACEHOLDERS = {
    "phone": "[手机号]",
    "email": "[邮箱]",
    "api_key": "[API密钥]",
    "private_path": "[私有路径]",
}

_RE_PRIVATE_PATH = re.compile(
    r"""[A-Za-z]:[\\/]+(?:Users|用户)[\\/]+[^\s，。；、！？：；“”‘’（）【】《》<>|"'']*""")
_RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_RE_SK = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}")
# R1 LOW-5: "Bearer:" 无空格形态同样命中 (仍要求 分隔符 或 空白, 防普通单词误伤)
# R2 LOW-5: 纯空白分支要求次词至少含一个数字 — "bearer <纯连字/纯字母长串>" 不再误伤
_RE_BEARER = re.compile(
    r"(?i)\bbearer(?:\s*[:=]\s*|\s+(?=\S*\d))[A-Za-z0-9_\-./+=]{16,}")
# R1 LOW-5: 键名别名 (secret_key/api_token/credentials/auth/pwd/密码); 键值间容忍
# 引号/反斜杠 (嵌套 dict str() 的 'password': 与 JSON 双重转义的 \"api_key\": 形态)
# R2 LOW-5: 值类要求至少含一个字母数字 (纯连字符/纯标点值不再命中)
_RE_KV = re.compile(
    r"(?i)\b(api[_-]?key|apikey|api[_-]?token|token|secret[_-]?key|secret|password|passwd"
    r"|credential[s]?|auth|pwd|密码)[\"\\']?\s*[:=]\s*[\"\\']?"
    r"(?=[A-Za-z0-9_./+=-]{12,})"
    r"([A-Za-z0-9_./+=-]*[A-Za-z0-9][A-Za-z0-9_./+=-]*)[\"\\']?")
# R1 LOW-5: 分隔符手机号 138-1234-5678 / 138 1234 5678 与连写形态二选一命中
_RE_PHONE = re.compile(
    r"(?<!\d)1[3-9]\d{9}(?!\d)|(?<!\d)1[3-9]\d[- ]\d{4}[- ]\d{4}(?!\d)")

# 入库接线 (H1): 自由文本键清单 — 各域卡片/偏好/SOP/系列档案的文本字段 + 常见英文别名。
# 不在此清单内的键 (signal/status/card_id/topic/seed/created_at/counts 等结构字段)
# 及其值一律原样保留。
TEXT_REDACT_KEYS = frozenset({
    "标题", "方案", "教训", "被否方案", "内容", "备注", "说明",
    "use_when", "procedure", "exceptions",
    "title", "note", "decision", "reason", "summary", "lesson", "content", "value",
    "worldview", "风格锚", "dna",  # R2 MED-4: 系列档案自由文本 (dna 内嵌套 str 全走 redact)
})


def redact(text, whitelist=()):
    """脱敏 -> (clean, findings)。白名单整词精确豁免; findings 每次命中一条。
    永不致命: 内部任何异常按原文本放行 + stderr 降级 (与消费接线段同口径)。"""
    original = None
    try:
        # R2 LOW-3: str(text) 本身可能抛 (__str__/__bool__ 炸弹), 移入 try —
        # 失败时原样返回入参 text, 对任何对象不抛 (红线)
        original = str(text or "")
        wl = {str(w).strip() for w in (whitelist or ()) if str(w).strip()}
        findings = []

        def _plain(ptype):
            def repl(m):
                if m.group(0) in wl:
                    return m.group(0)
                findings.append({"type": ptype, "placeholder": PLACEHOLDERS[ptype]})
                return PLACEHOLDERS[ptype]
            return repl

        def _kv(m):
            secret = m.group(2)
            if secret in wl or m.group(0) in wl:
                return m.group(0)
            findings.append({"type": "api_key", "placeholder": PLACEHOLDERS["api_key"]})
            return m.group(0).replace(secret, PLACEHOLDERS["api_key"])

        s = _RE_PRIVATE_PATH.sub(_plain("private_path"), original)
        s = _RE_EMAIL.sub(_plain("email"), s)
        s = _RE_SK.sub(_plain("api_key"), s)
        s = _RE_BEARER.sub(_plain("api_key"), s)
        s = _RE_KV.sub(_kv, s)
        s = _RE_PHONE.sub(_plain("phone"), s)
        return s, findings
    except Exception as e:  # noqa: BLE001 — 脱敏永不致命: 原文放行 + stderr 降级
        try:
            sys.stderr.write(
                f"[DirectorMaster] redaction 降级 (原文放行): {type(e).__name__}: {e}\n")
        except Exception:
            pass
        # R2 LOW-3: str() 转换失败 (original 未及赋值) → 原样返回入参对象本身
        return original if original is not None else text, []


def redact_free_text(obj, whitelist=()):
    """入库前接线助手 (H1): 递归遍历 dict/list, 仅对文本键 (TEXT_REDACT_KEYS,
    以及文本键下嵌套容器内的字符串) 的字符串值做 redact;
    结构字段 (数值/seed/id/enum/counts/布尔标记) 一律不碰 — 宁可漏脱不可破坏数据结构。
    任何异常整体按原值放行 (永不致命)。"""
    try:
        return _redact_walk(obj, False, whitelist)
    except Exception:  # noqa: BLE001 — 接线永不致命: 原值放行
        return obj


def _redact_walk(obj, in_text, whitelist):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            ctx = in_text or str(k) in TEXT_REDACT_KEYS
            out[k] = _redact_walk(v, ctx, whitelist)
        return out
    if isinstance(obj, list):
        return [_redact_walk(v, in_text, whitelist) for v in obj]
    if in_text and isinstance(obj, str):
        return redact(obj, whitelist)[0]
    return obj
