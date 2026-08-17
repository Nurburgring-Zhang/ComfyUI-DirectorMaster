# -*- coding: utf-8 -*-
"""
DialogueMasterPro — 对白专项节点
================================
(节点 6/7 — 剧本输出专业节点)

对白是剧本的灵魂。基于 McKee《对白》+ 真实导演对白
- 对白 7 大功能
- 潜文本/子文本/潜台词
- 反 AI 对白 30 句反例
- 8 大对白类型
- 8 大方言/口头禅模板
"""

import os
import sys
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        clean_anti_ai_text,
        inject_anti_ai_rules,
    )
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)

# Phase 17.6: 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# Knowledge Base 集成
try:
    from knowledge_base import (
        DIRECTOR_STYLES, EMOTION_RENDERING,
        get_director_decision,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False


# 8 大对白类型
DIALOGUE_TYPES = {
    "对话型": "日常对话, 推进剧情, 简单直接, 不绕弯子",
    "潜文本型": "嘴上说不要, 身体在做; 反话、讽喻、双关",
    "冲突型": "吵架、对峙、质问, 节奏快, 用短句",
    "告白型": "情感爆发, 长句, 慢节奏, 配合音乐",
    "指令型": "命令、安排、施压, 短句, 强语气",
    "示弱型": "请求、哀求、撒娇, 软语气",
    "沉默型": "没有对白, 只有动作, 高级写法",
    "意识流型": "内心独白, 时间错位, 适合非线叙事",
}

# 对白 7 大功能 (McKee)
DIALOGUE_FUNCTIONS = {
    "1_信息传递": "传递剧情信息, 但不能无聊地说, 要有冲突",
    "2_性格塑造": "展示人物性格, 通过用词/句式/方言/口头禅",
    "3_氛围营造": "营造场景氛围, 通过语气/节奏/潜台词",
    "4_推进动作": "对白 = 行动, 不是说话, 是做事",
    "5_展现价值观": "展示人物的价值观/态度/立场",
    "6_制造冲突": "对白中产生冲突, 一个对白让两个人站到对立面",
    "7_主题表达": "对白承载主题, 但不能让角色直接说主题",
}

# 30 句反 AI 对白反例
BAD_AI_DIALOGUE = [
    ("她瞳孔地震: '不!这不可能!'", "她后退一步: '谁告诉你的。'"),
    ("他心中暗道: '这个女人不简单。'", "他看了她一眼, 没说话。"),
    ("他陷入深深的沉思。", "他看着她, 把烟按灭了。"),
    ("她绝美地笑了。", "她笑了一下, 眼角有颗小痣。"),
    ("他撕心裂肺地喊: '为什么!'", "他声音哑了: '为什么。'"),
    ("她缓缓地转过头。", "她转过头。"),
    ("他意味深长地看着她。", "他看了她一眼, 又看别处。"),
    ("她复杂地说: '我不知道。'", "她说: '不知道。'"),
    ("他浑身颤抖。", "他手在抖。"),
    ("她留下了美好的回忆。", "她想起 1998 年的那场雨。"),
    ("他怒火中烧。", "他压低声音: '出去。'"),
    ("她陷入了回忆。", "她看着窗外的雨, 没说话。"),
    ("他不禁感叹。", "他叹了口气。"),
    ("她美若天仙。", "她 27 岁, 笑起来左边有酒窝。"),
    ("他倒吸一口凉气。", "他停了一下。"),
    ("她复杂地看着他。", "她看了他一眼, 把脸别过去。"),
    ("他心如刀割。", "他低头不说话。"),
    ("她百感交集。", "她站了一会儿, 走了。"),
    ("他暗自思忖。", "他看了她一眼, 没接话。"),
    ("她泪流满面。", "她没哭, 但手在抖。"),
    ("他陷入了沉默。", "他没说话。"),
    ("她呆住了。", "她手停了一下。"),
    ("他悲愤交加。", "他咬牙。"),
    ("她苦涩地笑了。", "她笑了一下, 没说话。"),
    ("他下定决心。", "他站起来。"),
    ("她陷入了恐慌。", "她手抖了一下, 把杯子摔了。"),
    ("他心意已决。", "他走了。"),
    ("她五味杂陈。", "她坐了一会儿, 站起来了。"),
    ("他心事重重。", "他没动。"),
    ("她若有所思。", "她看着窗外, 没接话。"),
]


class DialogueMasterPro:
    """
    对白专项节点 — 拆节点 6/7
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 风格 ===
                "对白类型_8选1": (list(DIALOGUE_TYPES.keys()), {"default": "潜文本型"}),
                "对白功能_7选1": (list(DIALOGUE_FUNCTIONS.keys()), {"default": "1_信息传递"}),
                "对白最大字数": ("INT", {"default": 15, "min": 5, "max": 50, "step": 1}),

                # === 2. 角色 ===
                "角色1_性别": (["男", "女"], {"default": "女"}),
                "角色1_年龄": ("INT", {"default": 28, "min": 5, "max": 90, "step": 1}),
                "角色1_身份": ("STRING", {
                    "default": "豪门失散千金",
                    "multiline": False,
                }),
                "角色1_口头禅": ("STRING", {
                    "default": "我不信。",
                    "multiline": False,
                }),
                "角色1_身体习惯": ("STRING", {
                    "default": "摸下巴, 咬嘴唇",
                    "multiline": False,
                }),

                "角色2_性别": (["男", "女"], {"default": "男"}),
                "角色2_年龄": ("INT", {"default": 32, "min": 5, "max": 90, "step": 1}),
                "角色2_身份": ("STRING", {
                    "default": "霸道总裁",
                    "multiline": False,
                }),
                "角色2_口头禅": ("STRING", {
                    "default": "我说过的话, 从来不收回。",
                    "multiline": False,
                }),
                "角色2_身体习惯": ("STRING", {
                    "default": "敲桌子, 抬头看人",
                    "multiline": False,
                }),

                # === 3. 场景 ===
                "场景": ("STRING", {
                    "default": "办公室, 雨天, 黄昏",
                    "multiline": False,
                }),
                "情绪基调": (["冷漠", "紧张", "暧昧", "悲伤", "愤怒", "释然"], {"default": "紧张"}),

                # === 4. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === 5. 灵魂注入 (Phase 17.6) ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
            },
            "optional": {
                "潜台词方向": ("STRING", {
                    "default": "他们表面上在谈公事, 其实在试探对方底牌",
                    "multiline": True,
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("dialogue_system", "dialogue_sample", "anti_ai_pairs")
    FUNCTION = "build_dialogue"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_dialogue(self, **kwargs):
        if not _HAS_ANTI_AI:
            return ("未加载 anti_ai_vocab: " + _ANTI_AI_ERROR, "", "")

        dlg_type = kwargs.get("对白类型_8选1", "潜文本型")
        dlg_func = kwargs.get("对白功能_7选1", "1_信息传递")
        max_words = kwargs.get("对白最大字数", 15)
        c1_gender = kwargs.get("角色1_性别", "女")
        c1_age = kwargs.get("角色1_年龄", 28)
        c1_id = kwargs.get("角色1_身份", "豪门失散千金")
        c1_quotes = kwargs.get("角色1_口头禅", "我不信。")
        c1_habit = kwargs.get("角色1_身体习惯", "摸下巴, 咬嘴唇")
        c2_gender = kwargs.get("角色2_性别", "男")
        c2_age = kwargs.get("角色2_年龄", 32)
        c2_id = kwargs.get("角色2_身份", "霸道总裁")
        c2_quotes = kwargs.get("角色2_口头禅", "我说过的话, 从来不收回。")
        c2_habit = kwargs.get("角色2_身体习惯", "敲桌子, 抬头看人")
        scene = kwargs.get("场景", "办公室, 雨天, 黄昏")
        emotion = kwargs.get("情绪基调", "紧张")
        subtext = kwargs.get("潜台词方向", "他们表面上在谈公事, 其实在试探对方底牌")

        # Phase 17.6: 灵魂注入
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")

        soul_inj = ""
        fused_name = ""
        fused_polarity = "neutral"
        fused_arousal = "medium"
        fused_intensity = 0.5
        if _HAS_SOUL:
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_scene_weight,
                    secondary=soul_secondary,
                    fusion_mode=soul_fusion_mode,
                    scene_context=scene,
                )
                soul_inj = inj
                fused_name = str(fused.get("name", ""))
                fused_polarity = str(fused.get("polarity", "neutral"))
                fused_arousal = str(fused.get("arousal", "medium"))
                fused_intensity = float(fused.get("intensity", 0.5))
            except Exception:
                soul_inj = ""

        # 1. 对白系统 prompt
        soul_header = ""
        if fused_name and _HAS_SOUL:
            soul_header = (
                "【灵魂核心 - 对白情绪驱动 (Phase 17.6)】\n"
                "主导情感: " + fused_name + "\n"
                "情感强度: " + "{:.2f}".format(fused_intensity) + "\n"
                "情感极性: " + fused_polarity + "\n"
                "唤醒度: " + fused_arousal + "\n"
                "════════════════════════════════════\n\n"
            )
        system = f"""{soul_header}【任务: 写出 {c1_id} 与 {c2_id} 在 {scene} 的对白】

【对白类型: {dlg_type}】
{DIALOGUE_TYPES[dlg_type]}

【对白功能: {dlg_func}】
{DIALOGUE_FUNCTIONS[dlg_func]}

【角色 1: {c1_id}】
- 性别: {c1_gender}, 年龄 {c1_age}
- 口头禅: {c1_quotes}
- 身体习惯: {c1_habit}

【角色 2: {c2_id}】
- 性别: {c2_gender}, 年龄 {c2_age}
- 口头禅: {c2_quotes}
- 身体习惯: {c2_habit}

【场景】
- 地点: {scene}
- 情绪基调: {emotion}

【潜台词方向】
{subtext}

【对白 7 大铁律】
1. 对白 = 行动, 不是说话
2. 单句对白不超过 {max_words} 字
3. 潜文本: 嘴上说不要, 身体在做
4. 用具体动作 (手/眼/呼吸), 不用情绪形容词
5. 沉默 = 高级对白
6. 每个角色有独特口头禅和身体习惯

【对白样本(反 AI 演示)】
{{反例示意: 真实对白 (左) vs 套路对白 (右)}}
  真实写法: 她后退一步: '谁告诉你的。'  ✓ 具体动作
  反例: 用空话 + 形容词  ✗ 不用套路

【灵魂驱动 - 对白情绪注入 (Phase 17.6)】
- 当前主导情感: {fused_name or "默认"}
- 情感极性: {fused_polarity or "neutral"} / 唤醒度: {fused_arousal or "medium"} / 强度: {fused_intensity:.2f}
- 灵魂规则: 角色对白必须与主导情感强共振
  - 负极性高唤醒 → 短促冲突, 几乎不留余地, 沉默即答案
  - 负极性低唤醒 → 慢速告别, 长句+沉默, 失去感
  - 正极性高唤醒 → 快速反转, 反讽幽默, 短句爆发
  - 正极性低唤醒 → 慢热温暖, 轻声细语, 亲密感
  - 矛盾极性 → 嘴上一套身体另一套, 强潜文本
- 身体习惯/口头禅必须与灵魂情绪一致
"""

        # 2. 对白样本
        sample = f"""场景: {scene}
情绪: {emotion}
潜台词: {subtext}

【示范对白 1 - 推进剧情】
{DIALOGUE_FUNCTIONS['1_信息传递']}

{DIALOGUE_FUNCTIONS['2_性格塑造']}
{c1_id} (摸下巴): 那件事... 你听到什么没有。
{c2_id} (敲桌子): 你说的是哪件。
{c1_id} (咬嘴唇): {c1_quotes}
{c2_id} (抬头): 我说过, {c2_quotes}

【示范对白 2 - 潜文本型】
{DIALOGUE_FUNCTIONS['3_氛围营造']}

{c1_id}: 听说你下周要走。
{c2_id}: 你听谁说的。
{c1_id}: 公司都在传。
{c2_id}: (沉默 3 秒, 看着窗外) 你信吗。
{c1_id}: (没接话)

【示范对白 3 - 冲突型】
{DIALOGUE_FUNCTIONS['6_制造冲突']}

{c2_id} (站起来): 我说最后一次。
{c1_id} (没动): {c1_quotes}
{c2_id} (压低声音): 你不要逼我。
{c1_id} (站起来): 走啊。
"""

        # 3. 反 AI 对白对 (前 5 句)
        pairs = "\n".join([
            f"✗ {bad}\n  ✓ {good}"
            for bad, good in BAD_AI_DIALOGUE[:5]
        ])

        # Knowledge Base 决策注入
        if _HAS_KB:
            try:
                _kb_dialogue_style = DIRECTOR_STYLES
                _kb_emotion_voice = EMOTION_RENDERING
                _kb_decision = get_director_decision("dialogue_master", scene)
                kb_block = "\n════════════════════════════════════\n"
                kb_block += "【Knowledge Base — 导演对白风格 + 情感-声音映射】\n"
                kb_block += "════════════════════════════════════\n\n"
                kb_block += "导演对白风格: " + str(_kb_dialogue_style)[:300] + "\n\n"
                kb_block += "情感-声音映射: " + str(_kb_emotion_voice)[:300] + "\n\n"
                kb_block += "对白决策: " + str(_kb_decision)[:300] + "\n"
                system += kb_block
            except Exception:
                pass

        if kwargs.get("启用反AI规则", True):
            system = inject_anti_ai_rules(system)

        return (system, sample, pairs)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "DialogueMasterPro": DialogueMasterPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "DialogueMasterPro": "💬 对白大师 (6/7)",
# }
