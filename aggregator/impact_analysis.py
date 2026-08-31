# -*- coding: utf-8 -*-
"""
DirectorMaster 修订影响面 (V16.7-MERGED D5) — 核心数据包差集 × 静态依赖规则表
================================================================
设计: design_batch3.md §5 D5 · owner: 批次3 A3 · 消费方: archive_master 版本提交接线

compute_impact(old_pack, new_pack) -> 纯函数 (确定性, 无时间戳/无随机/无全局态):

    {
      "changed_dims": ["_导演风格", ...],        # 发生变化的维度名 (排序后)
      "affected": {                              # 仅含非空段, 段序固定
         "分镜表":   ["全部镜头(共N镜): ...", "镜N: 引用角色'X'", ...],
         "AIGC提示词": [...],
         "音频":   [...],
         "角色":   [...],
         "时序":   [...],          # 时长规则段
         "未建模维度": [...],       # 未知维度诚实列出 (不猜测影响)
      },
      "reasons": ["...每个变化维度一条, 与 changed_dims 同序..."],
    }

静态依赖规则表 (14 条, 本文件唯一事实源 _IMPACT_RULES):
  全链 (导演/情绪/场景/意图主题/视觉/叙事/导演级能力块/随机种子 → 分镜表+AIGC提示词+音频+角色);
  角色 DNA/资产 id → 引用它的镜 (对分镜表逐镜文本子串匹配, 单字符身份不扫防误报);
  时长 → 全部时序字段 (总时长/逐镜 时长+start/end/情感曲线等派生);
  分镜表 → 逐镜差集 (按镜号: 内容变化/新增/移除, 派生提示词/音频/时序段);
  项目名/AI 配置 → 元数据配置维度 (不影响内容链);
  未命中规则表 → "未建模维度" 诚实列出, 不猜测。

无变化 → {"changed_dims": [], "affected": {}, "reasons": []} (全空)。

输入约定: 两份核心数据包 dict (director_master 核心数据包的 "_" 维度 + 可选内嵌
  "分镜表"/"角色"/"场景实体" 等结构 — 缺失结构诚实降级, 绝不编造镜号)。
坏输入 (非 dict) → ValueError, 诚实报错。
"""
import json as _json

# ------------------------------------------------------------------
# 静态依赖规则表 — (规则名, 维度名集合, 类别)
# 类别: global=全链 / character=角色引用 / asset=资产引用 /
#       duration=时序 / storyboard=逐镜差集 / meta=元数据配置(不影响内容链)
# 维度名覆盖 director_master 核心数据包真实键 (V12.6 32 字段) + 分镜契约顶层键。
# ------------------------------------------------------------------
_IMPACT_RULES = [
    ("导演风格", frozenset(["_导演风格", "导演"]), "global"),
    ("情绪", frozenset(["_情绪基调", "_情绪演变弧", "情绪"]), "global"),
    ("场景/时空", frozenset(["_场景描述", "_地区文化", "_时间年代", "_季节", "场景实体"]), "global"),
    ("意图/主题", frozenset(["_导演意图_观众应感到", "_核心冲突", "_主题词", "_观众承诺",
                     "_潜文本强度", "_潜文本_情感"]), "global"),
    ("视觉调性", frozenset(["_视觉调性", "_视觉调性弧", "色板", "设备美学包", "_画幅比例"]), "global"),
    ("叙事结构", frozenset(["_叙事编排", "_叙事线型", "叙事结构"]), "global"),
    ("导演级能力块", frozenset(["灵魂注入_整合", "审美判断", "风格指南", "统一电影提示词", "导演签名",
                       "灵魂维度", "反AI清理后", "8原则评分", "对标作品解析", "_对标作品",
                       "_启用反AI规则", "_预算级别", "_平台媒介", "_目标受众"]), "global"),
    ("随机种子", frozenset(["_随机种子"]), "global"),
    ("时长", frozenset(["_成片时长", "总时长秒"]), "duration"),
    ("角色", frozenset(["角色", "_角色档案", "角色卡", "角色DNA"]), "character"),
    ("资产/道具", frozenset(["_关键道具", "资产", "_资产", "资产注册表"]), "asset"),
    ("分镜表", frozenset(["分镜表", "shots"]), "storyboard"),
    ("项目名", frozenset(["_项目名"]), "meta"),
    ("AI配置", frozenset(["_ai_api_url", "_ai_api_key", "_ai_api_model"]), "meta"),
]

# 维度名 → 类别 (规则表展开; 表内维度名互不重复 — 新增条目前请确认)
_RULE_CATEGORY = {}
for _name, _dims, _cat in _IMPACT_RULES:
    for _d in _dims:
        if _d in _RULE_CATEGORY:
            raise RuntimeError("impact_analysis: 规则表维度名重复: %s" % _d)
        _RULE_CATEGORY[_d] = _cat

# affected 段固定输出顺序
_SEGMENT_ORDER = ("分镜表", "AIGC提示词", "音频", "角色", "时序", "未建模维度")

# 分镜表逐镜字段分组 (派生段判定)
_SHOT_AUDIO_FIELDS = ("声音", "音频描述")
_SHOT_TIMING_FIELDS = ("时长", "start", "end", "start_s", "end_s")
_SHOT_PROMPT_FIELDS = ("AIGC提示词", "首帧提示词", "首帧描述", "AIGC适配提示词")

# 角色条目身份键 (取第一个命中者)
_ENTITY_ID_KEYS = ("名字", "名称", "姓名", "角色名", "资产名", "资产id", "name", "id")

# 单字符身份不做子串扫描 (防 "光"/"雨" 类误报全表)
_MIN_SCAN_LEN = 2


def _short(value, limit=24):
    """值摘要 (确定性): str 直取, 其余 sort_keys JSON; 超长截断带总长标注."""
    if isinstance(value, str):
        s = value
    else:
        try:
            s = _json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            s = repr(value)
    s = s.replace("\n", " ").replace("\r", " ")
    if len(s) > limit:
        return s[:limit] + "…(共%d字符)" % len(s)
    return s


def _entities(value):
    """维度值 → [(identity, profile), ...] (保持原序).

    list[dict] → 身份取 _ENTITY_ID_KEYS 首个命中, 缺失则用整条内容的 sort_keys JSON;
    list[标量] / dict / str → 身份=条目/键/原文。无身份键的条目以内容为身份
    (位置序不可靠, 内容才稳定) — 诚实口径, 文档已注明。
    """
    out = []
    if isinstance(value, list):
        for it in value:
            if isinstance(it, dict):
                ident = None
                for k in _ENTITY_ID_KEYS:
                    if it.get(k) not in (None, ""):
                        ident = it[k]
                        break
                if ident is None:
                    try:
                        ident = _json.dumps(it, ensure_ascii=False, sort_keys=True)
                    except Exception:
                        ident = repr(it)
                out.append((str(ident), it))
            else:
                out.append((str(it), it))
    elif isinstance(value, dict):
        for k, v in value.items():
            out.append((str(k), v))
    elif isinstance(value, str):
        out.append((value.strip(), value))
    return out


def _diff_entities(old_v, new_v):
    """实体差集 → [(identity, verb, old_profile, new_profile)], 新序在前旧序在后."""
    om = {}
    for ident, prof in _entities(old_v):
        om.setdefault(ident, prof)
    nm = {}
    for ident, prof in _entities(new_v):
        nm.setdefault(ident, prof)
    out = []
    for ident, prof in nm.items():
        if ident not in om:
            out.append((ident, "新增", None, prof))
        elif om[ident] != prof:
            out.append((ident, "变化", om[ident], prof))
    for ident, prof in om.items():
        if ident not in nm:
            out.append((ident, "移除", prof, None))
    return out


def _shot_texts(shot):
    """收集单镜全部字符串值 (递归, 深度限 4) — 供身份子串匹配."""
    texts = []

    def walk(v, depth):
        if depth > 4:
            return
        if isinstance(v, str):
            texts.append(v)
        elif isinstance(v, list):
            for x in v:
                walk(x, depth + 1)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x, depth + 1)

    walk(shot, 0)
    return texts


def _shot_id(shot):
    sid = shot.get("镜号") if isinstance(shot, dict) else None
    return str(sid) if sid is not None else "?"


def _storyboard(pack):
    """取分镜表 (list 才算数); 不在/类型不符 → (None, [])."""
    sb = pack.get("分镜表") if isinstance(pack, dict) else None
    if isinstance(sb, list):
        return sb, [s for s in sb if isinstance(s, dict)]
    return None, []


def _refs_of(ident, shots):
    """在分镜表逐镜文本中定位引用 ident 的镜号 (保持分镜表原序, 去重)."""
    refs = []
    needle = ident.strip()
    if len(needle) < _MIN_SCAN_LEN:
        return refs  # 单字符身份不扫 — 防误报 (诚实口径, 宁缺勿猜)
    for shot in shots:
        for t in _shot_texts(shot):
            if needle in t:
                sid = _shot_id(shot)
                if sid not in refs:
                    refs.append(sid)
                break
    return refs


class _Affected(object):
    """段收集器: 精确去重, 段序按 _SEGMENT_ORDER 输出."""

    def __init__(self):
        self._data = {}

    def add(self, segment, entry):
        lst = self._data.setdefault(segment, [])
        if entry not in lst:
            lst.append(entry)

    def has(self, segment):
        return bool(self._data.get(segment))

    def build(self):
        return {seg: self._data[seg] for seg in _SEGMENT_ORDER if self._data.get(seg)}


def compute_impact(old_pack, new_pack):
    """两份核心数据包差集 → 修订影响面 (纯函数, 确定性; 规则表见模块头).

    old_pack/new_pack: dict (核心数据包). 非 dict → ValueError (诚实报错)。
    返回 {"changed_dims": [...], "affected": {...非空段...}, "reasons": [...]}。
    """
    if not isinstance(old_pack, dict) or not isinstance(new_pack, dict):
        raise ValueError(
            "compute_impact: old_pack/new_pack 必须是 dict (核心数据包), 实际 %s / %s"
            % (type(old_pack).__name__, type(new_pack).__name__))

    # ---- 差集 (维度名按 str 排序 → 确定性) ----
    changed = []
    union = sorted(set(old_pack) | set(new_pack), key=lambda k: str(k))
    for key in union:
        if key not in new_pack:
            changed.append((key, old_pack[key], None, "移除"))
        elif key not in old_pack:
            changed.append((key, None, new_pack[key], "新增"))
        elif old_pack[key] != new_pack[key]:
            changed.append((key, old_pack[key], new_pack[key], "变化"))

    if not changed:  # 无变化 → 全空 (设计 §5: 无变化→空)
        return {"changed_dims": [], "affected": {}, "reasons": []}

    aff = _Affected()
    reasons = []
    old_sb, old_shots = _storyboard(old_pack)
    new_sb, new_shots = _storyboard(new_pack)
    shots_available = new_sb is not None or old_sb is not None
    shot_note = ("共%d镜" % len(new_shots)) if new_sb is not None else "分镜表不在数据包内"

    for dim, old_v, new_v, verb in changed:
        cat = _RULE_CATEGORY.get(dim)
        diff = "%s → %s" % (_short(old_v), _short(new_v))

        if cat == "global":
            aff.add("分镜表", "全部镜头(%s): '%s' %s → 全链重算" % (shot_note, dim, verb))
            aff.add("AIGC提示词", "全部镜头AIGC提示词: '%s' %s → 全链重算" % (dim, verb))
            aff.add("音频", "全部镜头音频: '%s' %s → 全链重算" % (dim, verb))
            aff.add("角色", "全部角色DNA: '%s' %s → 全链重算" % (dim, verb))
            reasons.append("'%s' %s: %s — 全链依赖维度: 分镜表/AIGC提示词/音频/角色 全部受影响"
                           % (dim, verb, diff))

        elif cat in ("character", "asset"):
            kind = "角色" if cat == "character" else "资产"
            diffs = _diff_entities(old_v, new_v)
            if not diffs:
                # 结构级变化但实体差集为空 (如同值换容器形态) — 诚实标注, 不猜镜
                reasons.append("'%s' %s: %s — %s维度实体差集为空 (容器形态变化), 影响面未建模"
                               % (dim, verb, diff, kind))
                aff.add("未建模维度", "'%s' (%s)" % (dim, verb))
                continue
            names = []
            notes = []
            for ident, everb, _op, _np in diffs:
                names.append(ident)
                if cat == "character":
                    aff.add("角色", "角色'%s': DNA/档案%s" % (ident, everb))
                refs = _refs_of(ident, new_shots or old_shots)
                for sid in refs:
                    aff.add("分镜表", "镜%s: 引用%s'%s'" % (sid, kind, ident))
                    aff.add("AIGC提示词", "镜%s: 引用%s'%s'" % (sid, kind, ident))
                if not refs:
                    if shots_available:
                        notes.append("%s'%s' %s — 分镜表中未找到引用镜 (无需逐镜返工, 仅%s档案级)"
                                     % (kind, ident, everb, kind))
                    else:
                        notes.append("%s'%s' %s — 分镜表不在数据包内, 无法定位引用镜 (不猜测)"
                                     % (kind, ident, everb, kind))
            reasons.append("'%s' %s: %s — %s维度: 仅引用这些%s的镜受影响 (%s)"
                           % (dim, verb, diff, kind, kind, "、".join(names[:8])))
            reasons.extend(notes)

        elif cat == "duration":
            aff.add("时序", "总时长/成片时长 ('%s' %s)" % (dim, verb))
            if new_sb is not None:
                aff.add("时序", "分镜表逐镜 时长/start/end (%s)" % shot_note)
            else:
                aff.add("时序", "分镜表不在数据包内 (镜级时序未知)")
            aff.add("时序", "情感曲线/叙事拓扑/时序位 等时序派生字段")
            reasons.append("'%s' %s: %s — 时长维度: 全部时序字段需重算" % (dim, verb, diff))

        elif cat == "storyboard":
            added = removed = changed_n = 0
            om = {}
            for s in old_shots:
                om.setdefault(_shot_id(s), s)
            nm = {}
            for s in new_shots:
                nm.setdefault(_shot_id(s), s)
            for sid in nm:
                if sid not in om:
                    added += 1
                    aff.add("分镜表", "镜%s: 新增镜" % sid)
                    aff.add("AIGC提示词", "镜%s: 新增镜→AIGC提示词需生成" % sid)
                    aff.add("音频", "镜%s: 新增镜→音频需生成" % sid)
                else:
                    if om[sid] != nm[sid]:
                        changed_n += 1
                        aff.add("分镜表", "镜%s: 内容变化" % sid)
                        aff.add("AIGC提示词", "镜%s: 分镜变化→AIGC提示词需重算" % sid)
                    o_s, n_s = om[sid], nm[sid]
                    if any(o_s.get(f) != n_s.get(f) for f in _SHOT_AUDIO_FIELDS):
                        aff.add("音频", "镜%s: 音频相关字段变化→音频需重算" % sid)
                    if any(o_s.get(f) != n_s.get(f) for f in _SHOT_TIMING_FIELDS):
                        aff.add("时序", "镜%s: 时长/start/end 变化" % sid)
            for sid in om:
                if sid not in nm:
                    removed += 1
                    aff.add("分镜表", "镜%s: 移除镜" % sid)
            reasons.append("'分镜表' %s: 新增%d/移除%d/修改%d — 逐镜差集"
                           % (verb, added, removed, changed_n))

        elif cat == "meta":
            reasons.append("'%s' %s: %s — 元数据/配置维度: 不影响内容链" % (dim, verb, diff))

        else:
            # 未建模维度 — 诚实列出, 不猜测影响 (设计 §5)
            aff.add("未建模维度", "'%s' (%s)" % (dim, verb))
            reasons.append("'%s' %s: %s — 未建模维度: 影响面未建模, 不猜测" % (dim, verb, diff))

    return {"changed_dims": [dim for dim, _o, _n, _v in changed],
            "affected": aff.build(), "reasons": reasons}
