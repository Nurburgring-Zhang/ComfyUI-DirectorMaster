# -*- coding: utf-8 -*-
"""
批次6 D3 角色 DNA 档 — 确定性规则映射 (零 LLM 调用 / 零编造 / 零第三方库)
==========================================================================
抽象词拒绝 + 具体视觉描述词规则映射 → 8 维 DNA 档 + promptBlock(≤200字).
输出形状 (§11.6 钉死): {"dna_version": 1, "维度": {8键}, "promptBlock": str, "抽象词": [被拒词]}
无规则命中的维度如实记 "未提供" — 只拼真实输入里出现过的具体视觉词, 绝不猜测.
视觉风格为项目级调性, 不入 8 维 (8 维只收角色本体视觉词).
"""
import json as _json

DNA_VERSION = 1
DNA_DIMENSIONS = ("眼型", "脸型", "发型", "发色", "肤色", "体态", "标志着装", "气质锚")
NOT_PROVIDED = "未提供"
PROMPTBLOCK_MAX = 200

# 内置禁词表 (~30, 主观评价/氛围抽象词, 不构成可执行视觉指令); 长词优先剥除避免子词重复计数
ABSTRACT_WORDS = (
    "美丽", "漂亮", "好看", "帅气", "英俊", "秀气", "优雅", "神秘", "高级感", "高级",
    "惊艳", "绝美", "有气质", "气质", "氛围感", "清纯", "御姐", "大气", "慵懒", "清冷",
    "明媚", "沧桑", "成熟感", "少年感", "治愈", "性感", "冷艳", "甜美", "温柔", "时尚",
    "耐看", "仙气", "灵动", "精致", "妩媚", "气场",
)

# 具体视觉词 → 维度值规则表: (规范值, 触发词元组); 标志着装 markers 值=触发词本身
_DIMENSION_RULES = {
    "眼型": (
        ("单眼皮", ("单眼皮",)),
        ("双眼皮", ("双眼皮",)),
        ("内双", ("内双",)),
        ("丹凤眼", ("丹凤眼",)),
        ("杏眼", ("杏眼",)),
        ("桃花眼", ("桃花眼",)),
        ("三白眼", ("三白眼",)),
        ("下垂眼", ("下垂眼", "眼角下垂")),
        ("吊梢眼", ("吊梢眼", "眼角上挑")),
        ("细长眼", ("细长眼", "眯缝眼")),
        ("眼窝深", ("眼窝深", "深眼窝", "眼窝凹陷", "深目")),
        ("圆眼", ("圆眼", "大眼睛")),
        ("小眼", ("小眼睛",)),
        ("浓眉", ("浓眉",)),
        ("剑眉", ("剑眉",)),
        ("淡眉", ("淡眉", "眉毛稀")),
    ),
    "脸型": (
        ("圆脸", ("圆脸", "脸圆")),
        ("瓜子脸", ("瓜子脸",)),
        ("方脸", ("方脸", "国字脸")),
        ("鹅蛋脸", ("鹅蛋脸",)),
        ("长脸", ("长脸", "脸长")),
        ("高颧骨", ("高颧骨", "颧骨高", "颧弓外扩")),
        ("高鼻梁", ("高鼻梁", "鼻梁高")),
        ("塌鼻梁", ("塌鼻梁", "鼻梁塌")),
        ("鹰钩鼻", ("鹰钩鼻",)),
        ("蒜头鼻", ("蒜头鼻",)),
        ("尖下巴", ("尖下巴",)),
        ("方下巴", ("方下巴", "宽下巴")),
        ("双下巴", ("双下巴",)),
        ("婴儿肥", ("婴儿肥",)),
        ("太阳穴凹陷", ("太阳穴凹陷",)),
        ("下颌线分明", ("下颌线",)),
        ("宽额头", ("宽额头", "额头宽")),
    ),
    "发型": (
        ("板寸", ("板寸", "寸头")),
        ("光头", ("光头",)),
        ("短发", ("短发",)),
        ("齐耳短发", ("齐耳短发",)),
        ("长发", ("长发",)),
        ("马尾", ("马尾",)),
        ("丸子头", ("丸子头",)),
        ("卷发", ("卷发", "波浪卷", "泡面卷")),
        ("直发", ("直发",)),
        ("刘海", ("刘海",)),
        ("中分", ("中分",)),
        ("侧分", ("侧分",)),
        ("背头", ("背头", "油头", "大背头")),
        ("脏辫", ("脏辫",)),
        ("半秃", ("半秃", "秃顶", "发际线高", "地中海")),
        ("编发", ("编发",)),
        ("爆炸头", ("爆炸头",)),
    ),
    "发色": (
        ("黑发", ("黑发",)),
        ("白发", ("白发", "满头白发")),
        ("花白", ("花白", "灰白", "两鬓斑白")),
        ("金发", ("金发", "染金")),
        ("棕发", ("棕发", "栗色", "褐色头发")),
        ("红发", ("红发",)),
        ("蓝发", ("蓝发",)),
        ("挑染", ("挑染", "染发")),
        ("黄发", ("黄毛", "染黄")),
    ),
    "肤色": (
        ("白皙", ("白皙", "皮肤白", "雪白")),
        ("苍白", ("苍白",)),
        ("麦色", ("麦色", "小麦色")),
        ("黝黑", ("黝黑",)),
        ("蜡黄", ("蜡黄",)),
        ("古铜色", ("古铜色", "晒黑")),
        ("潮红", ("潮红",)),
        ("皮肤粗糙", ("皮肤粗糙",)),
    ),
    "体态": (
        ("瘦削", ("瘦削", "消瘦", "清瘦")),
        ("苗条", ("苗条", "纤细")),
        ("高挑", ("高挑",)),
        ("高大", ("高大",)),
        ("娇小", ("娇小",)),
        ("壮实", ("壮实", "结实")),
        ("肌肉", ("肌肉",)),
        ("虎背熊腰", ("虎背熊腰", "宽肩")),
        ("驼背", ("驼背", "佝偻")),
        ("微胖", ("微胖",)),
        ("肥胖", ("肥胖", "臃肿")),
        ("骨感", ("骨感",)),
        ("丰腴", ("丰腴",)),
        ("单薄", ("单薄",)),
        ("长腿", ("长腿",)),
    ),
    "气质锚": (
        ("含胸驼背", ("含胸",)),
        ("腰背挺直", ("挺直", "腰板直", "站得笔直")),
        ("习惯眯眼", ("眯眼",)),
        ("眉头紧锁", ("皱眉", "眉头紧锁")),
        ("习惯抱臂", ("抱臂", "交叉双臂", "双臂环胸")),
        ("手插口袋", ("手插口袋", "插兜", "手插兜")),
        ("咬指甲", ("咬指甲",)),
        ("习惯抖腿", ("抖腿",)),
        ("常扶眼镜", ("扶眼镜", "推眼镜")),
        ("常挠头", ("挠头",)),
        ("低头行走", ("低头走路", "低着头")),
        ("眼神躲闪", ("眼神躲闪", "不敢对视")),
        ("目光锐利", ("目光锐利", "眼神锐利")),
    ),
    "标志着装": tuple((w, (w,)) for w in (
        "工作服", "制服", "西装", "中山装", "旗袍", "汉服", "唐装", "牛仔", "皮夹克",
        "夹克", "风衣", "大衣", "卫衣", "连帽衫", "衬衫", "T恤", "背心", "毛衣", "围裙",
        "军装", "警服", "校服", "工装", "斗篷", "马甲", "长裙", "短裙", "百褶裙",
        "连衣裙", "短裤", "长裤", "阔腿裤", "运动服", "手套", "围巾", "帽子", "鸭舌帽",
        "礼帽", "眼镜", "墨镜", "戒指", "手表", "项链", "耳环", "绷带", "补丁", "袖套",
    )),
}


def reject_abstract_words(text):
    """剔除抽象词; 返回 (清洗后文本, 命中词列表). 长词优先, 避免子词重复计数."""
    cleaned, found = str(text or ""), []
    for w in sorted(ABSTRACT_WORDS, key=lambda x: (-len(x), x)):
        if w in cleaned:
            found.append(w)
            cleaned = cleaned.replace(w, "")
    return cleaned, found


def _match_dimension(dim, text):
    if not text:
        return NOT_PROVIDED
    hits = []
    for value, triggers in _DIMENSION_RULES[dim]:
        if value not in hits and any(t in text for t in triggers):
            hits.append(value)
    if not hits:
        return NOT_PROVIDED
    hits = [v for v in hits if not any(v != o and v in o for o in hits)]
    return "+".join(hits)


def _assemble_prompt_block(char_name, dims):
    parts = [f"{d}:{dims[d]}" for d in DNA_DIMENSIONS if dims.get(d, NOT_PROVIDED) != NOT_PROVIDED]
    if not parts:
        return ""
    head = f"{char_name}:" if str(char_name or "").strip() else ""
    full = head + ";".join(parts)
    if len(full) <= PROMPTBLOCK_MAX:
        return full
    cut = full[:PROMPTBLOCK_MAX]
    # 段边界截断: 舍去不完整尾段, 避免硬截断切在维度值中间 (R1 LOW-7)
    last_sep = cut.rfind(";")
    if last_sep > len(head):
        cut = cut[:last_sep]
    return cut


def build_dna_profile(char_name, appearance, costume, visual_style=""):
    """角色 DNA 档: 抽象词剔除 + 规则映射, 同输入逐字节同 (确定性)."""
    clean_app, app_rejected = reject_abstract_words(appearance)
    clean_cost, cost_rejected = reject_abstract_words(costume)
    dims = {}
    for d in DNA_DIMENSIONS:
        dims[d] = _match_dimension(d, clean_cost if d == "标志着装" else clean_app)
    return {"dna_version": DNA_VERSION, "维度": dims,
            "promptBlock": _assemble_prompt_block(char_name, dims),
            "抽象词": list(dict.fromkeys(app_rejected + cost_rejected))}


def merge_dna_profile(base_dna, char_dna, char_name=""):
    """跨项目继承: 外貌DNA_JSON 基座 + 当前角色字段增量覆盖 (当前未提供的维度沿用基座).
    基座维度值不直接采信: 过 reject_abstract_words + _DIMENSION_RULES 白名单复核,
    不匹配 → 「未提供」, 命中禁词计入 抽象词 (R1 MED-3: 手写/被污染基座无法绕过禁词表)。"""
    base = base_dna if isinstance(base_dna, dict) else {}
    cur = char_dna if isinstance(char_dna, dict) else {}
    base_dims = base.get("维度") if isinstance(base.get("维度"), dict) else {}
    cur_dims = cur.get("维度") if isinstance(cur.get("维度"), dict) else {}
    dims, rejected = {}, []
    for d in DNA_DIMENSIONS:
        c = cur_dims.get(d, NOT_PROVIDED)
        if c and c != NOT_PROVIDED:
            dims[d] = c
            continue
        p = NOT_PROVIDED
        p_raw = base_dims.get(d, NOT_PROVIDED)
        if isinstance(p_raw, str) and p_raw.strip() and p_raw != NOT_PROVIDED:
            clean, rej = reject_abstract_words(p_raw)
            rejected.extend(rej)
            m = _match_dimension(d, clean)
            if m and m != NOT_PROVIDED:
                p = m
        dims[d] = p
    rejected = list(dict.fromkeys(
        list(base.get("抽象词") or []) + list(cur.get("抽象词") or []) + rejected))
    return {"dna_version": DNA_VERSION, "维度": dims,
            "promptBlock": _assemble_prompt_block(char_name, dims), "抽象词": rejected}


def load_dna_json(text):
    """外貌DNA_JSON 解析入口; 非法/非 dict → (None, 错误说明) — 诚实降级, 不伪造基座."""
    raw = str(text or "").strip()
    if not raw:
        return None, ""
    try:
        data = _json.loads(raw)
    except Exception as e:
        return None, f"JSON解析失败: {type(e).__name__}"
    if not isinstance(data, dict):
        return None, "顶层不是JSON对象"
    return data, ""
