# -*- coding: utf-8 -*-
"""
VerticalShortDramaPro — 垂直短剧专业节点
=========================================
(节点 4/7 — 剧本输出专业节点)

基于 ReelShort / DramaBox / 抖音短剧实战经验

核心功能:
- 1-2 分钟单集结构生成
- 3 秒钩子 + 30 秒爽点 + 结尾钩子
- 6 大套路应用
- 8 大爆款公式
- 付费卡点设计
- 短剧对白 / 节奏 / 镜头的全套

Phase 17.6: 接入 director_soul 真实灵魂
- 灵魂_主导情感 / 灵魂_场景权重 / 灵魂_次要情感 / 灵魂_融合模式
- 不同情感 → 钩子/爽点/反转/付费卡点 真正不同的设计
"""

import os
import sys
import json

try:
    from director_mastery_v2 import (
        SHORT_DRAMA_RULES,
        DOUYIN_TROPES,
        DOUYIN_HIT_FORMULA,
        SHORT_DRAMA_PAYWALL,
        PACING_PATTERNS,
        REVERSAL_TYPES,
        AFTERTASTE_LEVELS,
        CHARACTER_ARCS,
        MULTI_THREAD_RULES,
        inject_all_theories,
    )
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        clean_anti_ai_text,
        inject_anti_ai_rules,
    )
    from director_soul import (
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
        soul_inject_simple,
    )
    _HAS_MASTERY = True
    _HAS_SOUL = True
except Exception as e:
    _HAS_MASTERY = False
    _HAS_SOUL = False
    _MASTERY_ERROR = str(e)


# 11 大套路
TROPES = list(DOUYIN_TROPES.keys()) if _HAS_MASTERY else ["穿越", "重生", "真假千金"]

# 8 大爆款节奏
PACINGS = list(PACING_PATTERNS.keys()) if _HAS_MASTERY else ["pulse", "plateau_cliff", "zigzag"]

# 8 大反转类型
REVERSALS = list(REVERSAL_TYPES.keys()) if _HAS_MASTERY else ["identity_reveal", "value_reversal"]

# 7 大角色弧
ARCS = list(CHARACTER_ARCS.keys()) if _HAS_MASTERY else ["positive_arc"]

# 6 级余韵
AFTERTASTES = list(AFTERTASTE_LEVELS.keys()) if _HAS_MASTERY else ["level_3_medium"]


# ============================================================
# 灵魂输入选项 (Phase 17.6)
# ============================================================
SOUL_EMOTION_KEYS = (["auto"] + list(EMOTION_MATRIX_60.keys())) if _HAS_SOUL else ["auto"]
SOUL_FUSION_MODES = (
    ["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
     "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"]
    if _HAS_SOUL
    else ["auto"]
)


# ============================================================
# 灵魂驱动的短剧策略 (Phase 17.6 真正不同)
# ============================================================
# 不只是字符串不同 — 钩子/爽点/反转/卡点 4 套都跟着情感切换
SOUL_DRAMA_STRATEGY = {
    # === 恐惧系 (悬疑/惊悚/虐) ===
    "Fear": {
        "name": "惊悚悬疑派",
        "hook_archetype": "悬念钩子",
        "hook_examples": [
            "主角在深夜接到一通无人电话, 来电显示是自己的号码",
            "主角发现枕头下有一根不属于自己的长发, 但同居人三年前就去世了",
            "监控录像里, 主角在睡梦中说出自己从未说过的秘密",
            "陌生人在电梯按了和主角完全相同的楼层, 扭头微笑",
        ],
        "hit_archetype": "真相爽点",
        "hit_examples": [
            "反派密谋被完整录音, 当场播放, 对方哑口无言",
            "警察冲进门的那一刻, 主角已先一步拿到了对方的把柄",
            "隐藏身份被揭穿, 众人惊呆, 主角冷漠抽身",
        ],
        "reversal_archetype": "真相大反转",
        "reversal_examples": [
            "以为是跟踪者的人其实是亲生父亲",
            "看似加害者其实是保护者, 镜头闪回三集前的伏笔",
            "死亡的配角其实在伪装, 镜头切到他的视角",
        ],
        "paywall_moment": "濒死 + 真相只揭露一半",
        "pacing_signature": "前 3 秒=悬念 / 7 秒=紧张 / 15 秒=恐惧升级 / 30 秒=凶手露半脸 / 60 秒=真相 60% / 结尾=致命未知",
        "color_mood": "冷青, 暗红, 惨白, 高对比阴影",
        "music_signature": "低频心跳 + 突发弦乐 + 突然静音制造不安",
        "dialogue_tone": "句子短, 经常半句被打断, 多用省略号, 喘息声明显",
    },
    # === 喜悦系 (爽剧/甜剧/爆笑) ===
    "Joy": {
        "name": "痛快爽剧派",
        "hook_archetype": "爽感钩子",
        "hook_examples": [
            "婚礼现场, 主角当众甩出渣男出轨的 30 张照片",
            "前任嘲讽主角没钱, 主角当场刷卡买下整栋楼",
            "主角被同事陷害停职, 下一秒接到总部任命 CEO 的电话",
            "恶婆婆刁难, 主角一个电话召来十个保镖",
        ],
        "hit_archetype": "痛快反击爽点",
        "hit_examples": [
            "反派刚说完'你以为你是谁', 主角掏出证据, 对方跪地求饶",
            "所有人都在嘲笑, 主角用一记神操作让所有人闭嘴",
            "前男友/前女友回头求复合, 主角微笑拒绝, 牵起新欢",
        ],
        "reversal_archetype": "身份/实力反转",
        "reversal_examples": [
            "扮猪吃虎: 看似普通员工其实是公司最大股东",
            "废柴逆袭: 被退婚的废柴其实是隐藏天才/大小姐",
            "反杀绿茶: 一直示弱的女主其实在下一盘大棋",
        ],
        "paywall_moment": "复仇/打脸的关键一击前一刻",
        "pacing_signature": "前 3 秒=被打脸 / 7 秒=隐忍 / 15 秒=反扑前奏 / 30 秒=第一记重击 / 60 秒=连续暴击 / 结尾=对方跪地",
        "color_mood": "亮金, 鲜红, 高饱和大色块, 强光对比",
        "music_signature": "快节奏鼓点 + 弦乐上行 + 爽点时的爆点音效",
        "dialogue_tone": "金句频出, 押韵, 反讽, 让观众'想截图'",
    },
    # === 悲伤/孤独系 (虐剧/情感/余韵) ===
    "Sadness": {
        "name": "虐心催泪派",
        "hook_archetype": "情感钩子",
        "hook_examples": [
            "母亲临终前给女儿写了一封信, 女儿在葬礼后才打开",
            "主角把离婚协议撕碎, 对方却以为主角在撒娇",
            "老人在车站等了三小时, 等的人三年前已去世",
            "主角为家人放弃梦想, 家人却不知道这件事",
        ],
        "hit_archetype": "余韵爽点",
        "hit_examples": [
            "误解终于解除, 两人四目相对, 镜头慢推",
            "主角放弃的梦想被别人替他完成, 主角含泪微笑",
            "反派道歉, 主角说'我不需要你的道歉, 我只需要你记得'",
        ],
        "reversal_archetype": "情感反转",
        "reversal_examples": [
            "看似抛弃孩子的人其实是为了给孩子治病卖房",
            "一直强势的母亲其实在偷偷给孩子攒嫁妆",
            "冷血总裁其实每晚偷偷去看望前妻",
        ],
        "paywall_moment": "真相大白 + 角色崩溃的那一刻",
        "pacing_signature": "前 3 秒=情感冲击 / 7 秒=压抑铺垫 / 15 秒=情绪累积 / 30 秒=第一次心碎 / 60 秒=无声爆发 / 结尾=余韵回响",
        "color_mood": "暖黄褪色, 雾蓝, 米白, 柔光低对比",
        "music_signature": "钢琴主旋律 + 弦乐低吟 + 长静音留白",
        "dialogue_tone": "省略号多, 句子在结尾变轻, 经常欲言又止, 多用反问句",
    },
    # === 愤怒系 (复仇/黑化) ===
    "Anger": {
        "name": "复仇黑化派",
        "hook_archetype": "愤怒钩子",
        "hook_examples": [
            "主角看到父亲被当众羞辱, 镜头推近主角握紧的拳头",
            "主角的孩子被人推下楼梯, 主角冲上去挡在身前",
            "公司会议上, 主角被合伙人当场踢出, 摔门而去",
            "妹妹被欺负的视频被传到网上, 主角一秒黑脸",
        ],
        "hit_archetype": "复仇爽点",
        "hit_examples": [
            "反派被主角亲手送进警局, 一句'你没想到吧'",
            "黑化的主角出现在反派面前, 对方当场瘫软",
            "商业复仇: 主角一通电话让对方公司破产",
        ],
        "reversal_archetype": "黑化反转",
        "reversal_examples": [
            "小白兔一夜之间变成大魔王, 微笑+眼睛全黑",
            "一直善良的主角被逼到极限, 开始用对手的方式对付对手",
            '原本"好人"的配角其实是最终 BOSS',
        ],
        "paywall_moment": "复仇完成前最后一秒的反转",
        "pacing_signature": "前 3 秒=愤怒触发 / 7 秒=压抑到极限 / 15 秒=筹谋开始 / 30 秒=第一次出手 / 60 秒=大规模反击 / 结尾=致命一击",
        "color_mood": "血红, 暗金, 黑色, 高对比强光",
        "music_signature": "低频鼓点 + 弦乐急速上行 + 金属撞击声",
        "dialogue_tone": "短句为主, 多用反问和命令句, 经常冷笑",
    },
    # === 惊讶系 (揭秘/烧脑) ===
    "Surprise": {
        "name": "烧脑揭秘派",
        "hook_archetype": "认知颠覆钩子",
        "hook_examples": [
            "主角一直以为的救命恩人, 镜头一转其实是幕后 BOSS",
            "主角发现自己生活了 20 年的家其实是个片场",
            "同事送的'生日礼物'里掉出一把钥匙, 打开的是主角的保险箱",
            "主角的妈妈在镜头外喊了一声英文名, 主角呆住",
        ],
        "hit_archetype": "恍然大悟爽点",
        "hit_examples": [
            "前面 30 集的所有伏笔串起来, 主角一句话点破真相",
            "观众以为的凶手其实是受害者, 镜头闪回三集前",
            "隐藏的时间线终于拼出全貌, 观众恍然大悟",
        ],
        "reversal_archetype": "认知反转",
        "reversal_examples": [
            "主角的'敌人'其实是自己的另一个人格",
            "整部剧其实是主角写的小说, 现实早就不存在",
            "观众以为的旁观者其实是主角的内心独白",
        ],
        "paywall_moment": "真相只解 70%, 留 30% 让观众自己猜",
        "pacing_signature": "前 3 秒=认知冲突 / 7 秒=线索铺设 / 15 秒=第一次暗示 / 30 秒=误导反转 / 60 秒=真相轮廓 / 结尾=震撼留白",
        "color_mood": "冷蓝, 紫光, 黑白高对比, 偶尔冷暖交替",
        "music_signature": "钢琴 + 电子音效 + 突然的静默",
        "dialogue_tone": "经常用反问和暗示, 关键台词藏在前半句",
    },
    # === 复合/默认 (State 类情感: 孤独/思念/苦涩等) ===
    "State": {
        "name": "情感余韵派",
        "hook_archetype": "余韵钩子",
        "hook_examples": [
            "主角在咖啡馆点了和前任一样的咖啡, 抬头看到熟悉的陌生人",
            "翻到旧手机里的录音, 是自己三年前对未来的自己说的话",
            "主角在公交车上看到一对父女, 想起自己离家的理由",
            "老人在窗前等一封永远不会来的信",
        ],
        "hit_archetype": "内心爽点",
        "hit_examples": [
            "主角终于和自己和解, 镜头从背影切到正面微笑",
            "一个迟到了 10 年的道歉, 两人在雨里站着不说话",
            "主角把最珍贵的东西送出去, 对方终于懂了",
        ],
        "reversal_archetype": "关系反转",
        "reversal_examples": [
            "一直冷漠的爸爸其实在偷偷给女儿写信",
            "最亲近的人其实是伤害最深的人, 也是最爱自己的人",
            "陌生人其实是失散多年的亲人",
        ],
        "paywall_moment": "角色做出重大决定的最后一刻",
        "pacing_signature": "前 3 秒=氛围铺底 / 7 秒=内心独白 / 15 秒=回忆闪回 / 30 秒=情感蓄力 / 60 秒=无声高潮 / 结尾=余韵收束",
        "color_mood": "暖黄, 雾蓝, 米色, 柔光",
        "music_signature": "钢琴 + 弦乐, 慢节奏, 留白多",
        "dialogue_tone": "句子短, 多省略号, 经常自言自语",
    },
    # === 兜底 ===
    "default": {
        "name": "通用爆款派",
        "hook_archetype": "冲突钩子",
        "hook_examples": [
            "主角被当众揭穿 / 被推下楼梯 / 接到神秘电话",
            "婚礼现场意外来访 / 公司会议当场翻脸",
            "前任/仇人突然出现 / 隐藏身份被识破",
        ],
        "hit_archetype": "反击爽点",
        "hit_examples": [
            "主角强势反击, 当场让对方下不来台",
            "关键证据被公开, 局势瞬间逆转",
        ],
        "reversal_archetype": "身份反转",
        "reversal_examples": [
            "扮猪吃虎, 隐藏实力曝光",
            "看似弱者其实是真正的强者",
        ],
        "paywall_moment": "复仇/揭秘/告白的关键一刻",
        "pacing_signature": "前 3 秒=钩子 / 7 秒=冲突 / 15 秒=反转铺垫 / 30 秒=第一爽点 / 60 秒=第二爽点 / 结尾=悬念",
        "color_mood": "高对比, 强光, 暖色主调",
        "music_signature": "节奏紧凑, 鼓点 + 弦乐",
        "dialogue_tone": "短句, 节奏感强, 易于截图",
    },
}


def _resolve_soul_strategy(fused: dict) -> dict:
    """
    根据融合情感结果, 决定使用哪一套策略
    真正不同的判定: fused['category'] / fused['arousal'] / fused['polarity']
    """
    if not fused or not isinstance(fused, dict):
        return SOUL_DRAMA_STRATEGY["default"]

    category = str(fused.get("category", "")).strip()
    polarity = str(fused.get("polarity", "")).strip()
    arousal = str(fused.get("arousal", "")).strip()
    name = str(fused.get("name", "")).strip()

    # 1. 优先用 category
    if category in SOUL_DRAMA_STRATEGY:
        return SOUL_DRAMA_STRATEGY[category]

    # 2. 用极性+唤醒度推断
    if polarity == "positive" and arousal in ("medium", "high"):
        return SOUL_DRAMA_STRATEGY["Joy"]
    if polarity == "negative" and arousal == "high":
        return SOUL_DRAMA_STRATEGY["Anger"]
    if polarity == "negative" and arousal in ("low", "medium"):
        return SOUL_DRAMA_STRATEGY["Sadness"]
    if polarity == "neutral":
        return SOUL_DRAMA_STRATEGY["Surprise"]

    # 3. 用名字模糊匹配
    n = name.lower()
    if "loneliness" in n or "longing" in n or "nostalgia" in n or "bittersweet" in n:
        return SOUL_DRAMA_STRATEGY["State"]
    if "love" in n or "tenderness" in n:
        return SOUL_DRAMA_STRATEGY["State"]

    return SOUL_DRAMA_STRATEGY["default"]


def _format_soul_block(soul_inj: str, fused: dict, soul_state: dict) -> str:
    """
    格式化灵魂注入块, 加到 system_prompt 头部
    """
    if not soul_inj:
        return ""
    if not fused or not isinstance(fused, dict):
        return "\n" + soul_inj

    # 提取关键信息
    name = fused.get("name", "")
    intensity = fused.get("intensity", 0.5)
    polarity = fused.get("polarity", "")
    arousal = fused.get("arousal", "")
    category = fused.get("category", "")
    visual = fused.get("visual_signs", "")[:200]
    voice = fused.get("voice_signs", "")[:200]
    inner = fused.get("inner_monologue", "")[:120]
    color = fused.get("color_palette", "")[:120]
    music = fused.get("music_tempo", "")[:120]

    state_block = ""
    if soul_state and isinstance(soul_state, dict):
        state_block = (
            f"\n灵魂状态: 灵感={soul_state.get('inspiration', 0)} "
            f"疲劳={soul_state.get('fatigue', 0)} "
            f"怀疑={soul_state.get('doubt', 0)} "
            f"叛逆={soul_state.get('rebelliousness', 0)} "
            f"精神={soul_state.get('mental_state', '')}"
        )

    summary = f"""
════════════════════════════════════════
【灵魂驱动短剧策略】(Phase 17.6 真正接入)
════════════════════════════════════════
主导情感: {name}  ({category} / {polarity} / arousal={arousal})
强度: {intensity}
视觉锚点: {visual}
声音锚点: {voice}
内心独白: {inner}
色彩策略: {color}
音乐策略: {music}{state_block}
════════════════════════════════════════
"""
    return summary + "\n" + soul_inj


def _strategy_block(strategy: dict, fused: dict) -> str:
    """
    把策略渲染成可读文本 (钩子/爽点/反转/卡点 4 套)
    """
    if not strategy:
        return ""
    cat = fused.get("name", "") if isinstance(fused, dict) else ""
    return f"""
【灵魂派别: {strategy['name']}】(情感: {cat})

=== 钩子策略 ({strategy['hook_archetype']}) ===
{chr(10).join('- ' + s for s in strategy['hook_examples'])}

=== 爽点策略 ({strategy['hit_archetype']}) ===
{chr(10).join('- ' + s for s in strategy['hit_examples'])}

=== 反转策略 ({strategy['reversal_archetype']}) ===
{chr(10).join('- ' + s for s in strategy['reversal_examples'])}

=== 付费卡点策略 ===
- 关键时刻: {strategy['paywall_moment']}

=== 节奏签名 ===
{strategy['pacing_signature']}

=== 视觉风格 ===
- 色彩: {strategy['color_mood']}
- 音乐: {strategy['music_signature']}
- 对白: {strategy['dialogue_tone']}
"""


class VerticalShortDramaPro:
    """
    垂直短剧专业节点 — 拆节点 4/7
    ReelShort / DramaBox / 抖音短剧实战级 + Phase 17.6 灵魂驱动
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 套路选择 ===
                "套路_11选1": (TROPES, {"default": "穿越"}),
                "爆款公式_8选1": (PACINGS, {"default": "plateau_cliff"}),
                "反转类型": (REVERSALS, {"default": "identity_reveal"}),
                "角色弧_7选1": (ARCS, {"default": "positive_arc"}),
                "余韵强度": (AFTERTASTES, {"default": "level_3_medium"}),

                # === 2. 规模 ===
                "总集数": ("INT", {"default": 80, "min": 20, "max": 300, "step": 1}),
                "单集时长秒": ("INT", {"default": 90, "min": 30, "max": 300, "step": 1}),
                "付费卡点位置_第几集": ("INT", {"default": 8, "min": 3, "max": 30, "step": 1}),

                # === 3. 节奏 ===
                "爽虐甜比例_532": ("STRING", {
                    "default": "5 爽 / 3 虐 / 2 甜",
                    "multiline": False,
                }),
                "钩子强度_1_10": ("INT", {"default": 9, "min": 1, "max": 10, "step": 1}),
                "前3秒冲突类型": (["暴力", "身份揭秘", "情感爆发", "性张力", "金钱冲突", "权谋", "威胁生命"], {"default": "身份揭秘"}),

                # === 4. 风格 ===
                "对白最大字数": ("INT", {"default": 12, "min": 5, "max": 25, "step": 1}),
                "主角性别": (["男", "女", "双男主", "双女主", "群像"], {"default": "女"}),
                "画风": (["现代都市", "古装言情", "年代剧", "仙侠", "校园", "都市悬疑", "豪门宅斗"], {"default": "现代都市"}),
                "受众": (["女频", "男频", "泛人群"], {"default": "女频"}),

                # === 5. 平台 ===
                "目标平台": (["ReelShort", "DramaBox", "抖音", "快手", "TikTok", "通用"], {"default": "ReelShort"}),
                "字幕语言": (["中文", "英文", "双语", "多语言"], {"default": "双语"}),

                # === 6. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                # === 7. 灵魂注入 (Phase 17.6) ===
                "灵魂_主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "灵魂_融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),
                "剧本片段": ("STRING", {"default": "", "multiline": True}),
                "导演风格": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("short_drama_system", "single_episode_template", "paywall_design")
    FUNCTION = "build_short_drama"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_short_drama(self, **kwargs):
        if not _HAS_MASTERY:
            return ("未加载 director_mastery_v2: " + _MASTERY_ERROR, "", "")

        # 用户要求
        trope = kwargs.get("套路_11选1", "穿越")
        pacing = kwargs.get("爆款公式_8选1", "plateau_cliff")
        reversal = kwargs.get("反转类型", "identity_reveal")
        arc = kwargs.get("角色弧_7选1", "positive_arc")
        aftertaste = kwargs.get("余韵强度", "level_3_medium")
        total_eps = kwargs.get("总集数", 80)
        ep_duration = kwargs.get("单集时长秒", 90)
        paywall_ep = kwargs.get("付费卡点位置_第几集", 8)
        hook_type = kwargs.get("前3秒冲突类型", "身份揭秘")
        hook_strength = kwargs.get("钩子强度_1_10", 9)
        dialogue_max = kwargs.get("对白最大字数", 12)
        gender = kwargs.get("主角性别", "女")
        style = kwargs.get("画风", "现代都市")
        audience = kwargs.get("受众", "女频")
        platform = kwargs.get("目标平台", "ReelShort")
        lang = kwargs.get("字幕语言", "双语")
        ratio = kwargs.get("爽虐甜比例_532", "5 爽 / 3 虐 / 2 甜")

        # ============================================================
        # Phase 17.6: 真实灵魂注入 (不是表面工作)
        # ============================================================
        soul_enabled = _HAS_SOUL
        if soul_enabled:
            try:
                soul_secondary = kwargs.get("灵魂_次要情感", "none")
                secondary_list = (
                    [soul_secondary] if soul_secondary and soul_secondary not in ("none", "auto", "") else None
                )
                _inj, _fused, _state, _dims = soul_inject_simple(
                    primary=kwargs.get("灵魂_主导情感", "auto"),
                    scene_weight=float(kwargs.get("灵魂_场景权重", 0.5) or 0.5),
                    director=kwargs.get("导演风格", ""),
                    secondary=secondary_list,
                    fusion_mode=kwargs.get("灵魂_融合模式", "auto"),
                    scene_context=kwargs.get("剧本片段", ""),
                )
                soul_strategy = _resolve_soul_strategy(_fused)
                soul_summary = _format_soul_block(_inj, _fused, _state)
                soul_strategy_text = _strategy_block(soul_strategy, _fused)
                # 记录真正的情感锚点 (用于 episode_template 头部)
                fused_name = _fused.get("name", "复合情感") if isinstance(_fused, dict) else "复合情感"
                fused_category = _fused.get("category", "State") if isinstance(_fused, dict) else "State"
                fused_polarity = _fused.get("polarity", "mixed") if isinstance(_fused, dict) else "mixed"
                fused_arousal = _fused.get("arousal", "medium") if isinstance(_fused, dict) else "medium"
                fused_intensity = _fused.get("intensity", 0.5) if isinstance(_fused, dict) else 0.5
            except Exception:
                soul_enabled = False
                soul_strategy = SOUL_DRAMA_STRATEGY["default"]
                soul_summary = ""
                soul_strategy_text = ""
                fused_name = "复合情感"
                fused_category = "State"
                fused_polarity = "mixed"
                fused_arousal = "medium"
                fused_intensity = 0.5

        if not soul_enabled:
            soul_strategy = SOUL_DRAMA_STRATEGY["default"]
            soul_summary = ""
            soul_strategy_text = ""
            fused_name = "复合情感"
            fused_category = "State"
            fused_polarity = "mixed"
            fused_arousal = "medium"
            fused_intensity = 0.5

        # ===== 1. 系统级 prompt (导演/编剧) =====
        soul_header = ""
        if soul_summary:
            soul_header = f"""{soul_summary}

{soul_strategy_text}

"""

        system_prompt = f"""{soul_header}【任务: 写出 {total_eps} 集 {platform} 风格短剧剧本】

【套路: {trope}】
{DOUYIN_TROPES.get(trope, "")}

【爆款公式: {pacing}】
{PACING_PATTERNS.get(pacing, "")}

【反转类型: {reversal}】
{REVERSAL_TYPES.get(reversal, "")}

【角色弧: {arc}】
{CHARACTER_ARCS.get(arc, "")}

【余韵强度: {aftertaste}】
{AFTERTASTE_LEVELS.get(aftertaste, "")}

【基础设定】
- 总集数: {total_eps} 集
- 单集: {ep_duration} 秒
- 主角性别: {gender}
- 画风: {style}
- 受众: {audience}
- 平台: {platform}
- 语言: {lang}
- 爽虐甜比例: {ratio}
- 对白最大字数: {dialogue_max} 字
- 钩子强度: {hook_strength}/10
- 付费卡点: 第 {paywall_ep} 集

【爆款公式核心 (8 条)】
1. 前 3 秒钩子, 7 秒冲突, 15 秒反转, 30 秒第一个爽点, 60 秒第二个爽点
2. 扁平化人物 (好/坏清楚, 反派脸谱化)
3. 3 集一个小反转, 10 集一个大反转, 全剧不超过 100 集
4. 对白 < {dialogue_max} 字/句, 平均 7 字
5. 3 大情绪: 爽/虐/甜 不断切换 {ratio} 循环
6. 每 5-8 集设付费卡点, 关键时刻卡点
7. 竖屏 9:16, 字幕必须, 镜头快切 1-2 秒/镜
8. 低成本高节奏, 一天拍 3-5 集

【前 3 秒铁律 (灵魂驱动: {fused_name} / {fused_polarity}/{fused_arousal})】
{hook_type} 类型钩子, 强度 {hook_strength}/10。前 3 秒必抛强冲突/强悬念/颠覆认知画面, 杜绝铺垫/慢镜头/空镜, 第一秒锁住观众视线。
灵魂策略派别: {soul_strategy.get('name', '通用爆款派')}
钩子原型: {soul_strategy.get('hook_archetype', '冲突钩子')}
色彩锚点: {soul_strategy.get('color_mood', '')}
"""

        # ===== 2. 单集模板 (灵魂驱动差异化) =====
        # 选不同节奏/爽点模板
        ep_template_intro = ""
        if soul_enabled:
            ep_template_intro = f"""【本剧情感主调: {fused_name} ({fused_category}) - 强度 {fused_intensity}】
- 极性: {fused_polarity} / 唤醒度: {fused_arousal}
- 派别: {soul_strategy.get('name', '通用爆款派')}
- 节奏签名: {soul_strategy.get('pacing_signature', '')}
- 对白风格: {soul_strategy.get('dialogue_tone', '')}

"""
        else:
            ep_template_intro = f"""【本剧情感主调: 复合 (默认)】
- 派别: {soul_strategy.get('name', '通用爆款派')}
- 节奏签名: {soul_strategy.get('pacing_signature', '')}

"""

        # 根据派别挑选不同的爽点示例
        hit_examples = "\n".join(f"   - {s}" for s in soul_strategy.get("hit_examples", []))

        episode_template = f"""{ep_template_intro}【单集 {ep_duration} 秒标准结构】

0-3s: 黄金开篇 (钩子) [{soul_strategy.get('hook_archetype', '冲突钩子')}]
   - {hook_type} 冲突画面 + 直击悬念
   - 拒绝铺垫, 直接进入核心冲突
   - 灵魂派别示例:
{chr(10).join('   - ' + s for s in soul_strategy.get('hook_examples', []))}

3-7s: 升级冲突
   - 让冲突更激烈, 符合 {fused_arousal} 唤醒度
   - 视觉锚点: {(_fused.get('visual_signs', '')[:120]) if _HAS_SOUL and isinstance(_fused, dict) else '高对比强光'}

7-15s: 第一次反转铺垫 ({soul_strategy.get('reversal_archetype', '身份反转')})
   - 暗示有什么不对
   - {chr(10).join('   - ' + s for s in soul_strategy.get('reversal_examples', []))}

15-30s: 第一个爽点 (或虐点) [{soul_strategy.get('hit_archetype', '反击爽点')}]
   - 小高潮, 锁定观众
{hit_examples}

30-60s: 中段剧情 (拉扯)
   - 矛盾升级/误会加深/伏笔预埋/正反对峙
   - 镜头快切, 1-2 秒/镜
   - 音乐: {soul_strategy.get('music_signature', '')}

60-{ep_duration-3}s: 第二个爽点 (或虐点) [{soul_strategy.get('hit_archetype', '反击爽点')}]
   - 大高潮, 推动剧情
   - 必须呼应当前情感: {fused_name}

{ep_duration-3}s-{ep_duration}s: 结尾钩子 (锁粉) [{soul_strategy.get('reversal_archetype', '身份反转')}]
   - 突发反转/身份曝光/致命危机/惊天秘密
   - 留白收尾, 悬念拉满
   - 倒逼看下一集
   - 派别提示: {soul_strategy.get('paywall_moment', '')}

【单集对白铁律】
- 单句对白不超过 {dialogue_max} 字
- 平均对白长度 7 字
- 用短句制造速度感
- 不用书面化/生硬台词
- 贴合 {gender} {audience} 视角
- 对白风格: {soul_strategy.get('dialogue_tone', '')}
- 不要"瞳孔地震"等 AI 套路

【画面要求】
- 竖屏 9:16
- 1-2 秒/镜 镜头快切
- 所有情节标注镜头景别/动作/细节
- 字幕必加, 居中下方
- 重要对白加 emoji 表情
- 色彩策略: {soul_strategy.get('color_mood', '')}
"""

        # ===== 3. 付费卡点设计 (灵魂驱动) =====
        paywall_design = f"""【{total_eps} 集付费卡点设计 (每 5-8 集)】

灵魂派别: {soul_strategy.get('name', '通用爆款派')}
卡点关键时刻: {soul_strategy.get('paywall_moment', '')}

{SHORT_DRAMA_PAYWALL.get('paywall_1_reveal', '')}  → 建议第 {paywall_ep} 集
{SHORT_DRAMA_PAYWALL.get('paywall_2_revenge', '')}  → 建议第 {paywall_ep + 5} 集
{SHORT_DRAMA_PAYWALL.get('paywall_3_romance', '')}  → 建议第 {paywall_ep + 10} 集
{SHORT_DRAMA_PAYWALL.get('paywall_4_climax', '')}  → 建议第 {paywall_ep + 15} 集

{SHORT_DRAMA_PAYWALL.get('interval_rule', '')}

【付费卡点时刻的设计原则 (灵魂驱动)】
1. 揭秘/反转/复仇/告白/对决 - 关键时刻
2. 每 5-8 集一个, 不可太密集 (用户疲劳)
3. 卡点前 30 秒必须有强烈铺垫
4. 卡点后第一句台词必须是"什么?"
5. 卡点不能解决主冲突, 只暴露信息
6. 卡点必须服务于本剧情感主调: {fused_name} ({fused_polarity}/{fused_arousal})
7. 不同派别的卡点风格:
   - Joy 派: 卡点在"打脸"开始前一刻
   - Fear 派: 卡点在"真相只揭露 50%"的那一刻
   - Sadness 派: 卡点在"角色崩溃"的那一刻
   - Anger 派: 卡点在"复仇最后一击"前
   - Surprise 派: 卡点在"认知颠覆"时
   - State 派: 卡点在"重大决定"前
"""

        # ===== 4. 注入反 AI 规则 =====
        if kwargs.get("启用反AI规则", True):
            system_prompt = inject_anti_ai_rules(system_prompt)
            episode_template = inject_anti_ai_rules(episode_template)
            paywall_design = inject_anti_ai_rules(paywall_design)

        # 5. 额外禁用词
        extra_ban = kwargs.get("额外禁用词", "")
        if extra_ban:
            system_prompt += f"\n\n【额外禁用词】\n{extra_ban}"

        return (system_prompt, episode_template, paywall_design)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "VerticalShortDramaPro": VerticalShortDramaPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "VerticalShortDramaPro": "📱 垂直短剧 (4/7)",
# }
