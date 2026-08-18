# -*- coding: utf-8 -*-
"""
HookMasterPro — 钩子专项节点
=============================
(节点 5/7 — 剧本输出专业节点)

短视频/短剧/电影的开头 3-30 秒决定生死
- 3 秒钩子: 短剧生死线
- 7 秒钩子: 短视频黄金窗口
- 15 秒钩子: 中视频留存点
- 30 秒钩子: 电影/剧集第一个场景

8 大钩子类型 + 实战 50 句钩子库
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
    from director_mastery_v2 import (
        SHORT_DRAMA_RULES,
        DOUYIN_HIT_FORMULA,
        REVERSAL_TYPES,
    )
    _HAS_MASTERY = True
except Exception as e:
    _HAS_MASTERY = False
    _MASTERY_ERROR = str(e)

# Phase 17.6: 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# Knowledge Base 集成
try:
    from knowledge_base import (
        SHORT_DRAMA_PATTERNS, VIRAL_VIDEO_TECHNIQUES,
        get_short_drama_patterns, get_viral_techniques,
    )
    _HAS_KB = True
except Exception:
    _HAS_KB = False


# 8 大钩子类型
HOOK_TYPES = {
    "身份揭秘": "前 3 秒揭示主角的真实身份 (真千金/战神/系统拥有者), 例: 主角在婚礼上被揭穿不是亲生",
    "暴力冲突": "前 3 秒直接展示暴力/打斗/威胁, 例: 主角被人推下楼梯/被围殴",
    "情感爆发": "前 3 秒展示强烈情感, 例: 主角抱着孩子/接到父亲去世电话/发现出轨",
    "性张力": "前 3 秒展示禁忌/擦边/暧昧场景, 例: 错位/误会/偷情",
    "金钱冲突": "前 3 秒展示金钱冲突, 例: 当场开 50 万支票/天价交易/破产",
    "权谋反转": "前 3 秒展示权力游戏, 例: 主角一句话让反派下跪/老板被炒",
    "威胁生命": "前 3 秒展示死亡威胁, 例: 主角被追杀/被困/中毒",
    "神秘悬念": "前 3 秒展示不可思议的事, 例: 主角从未来回来/接到神秘电话/发现日记",
}

# 30 句实战钩子库 (按类型分类)
HOOK_LIBRARY = {
    "身份揭秘": [
        "婚礼上, 当我摘下头纱, 婆家全愣住了: 我长得和婆婆一模一样。",
        "被扫地出门那天, 我才知道我是首富失散 20 年的亲生女儿。",
        "我以为我是被拐卖的孤儿, 直到 DNA 检测报告送到了我手上。",
        "在产房门口, 我丈夫终于承认: 这个孩子, 不是他的。",
        "我死后重生回到 18 岁, 这一世, 我要让所有人付出代价。",
    ],
    "暴力冲突": [
        "我丈夫把我推下楼梯的那一刻, 我听见他说: '这一摔, 我们的债就清了。'",
        "当我被五个打手堵在巷子里, 我缓缓从包里拿出了刀。",
        "婚礼上, 那个男人当着所有人的面, 一巴掌扇在我脸上: '你配吗?'",
        "我闯进办公室, 把咖啡直接泼在他那身 10 万的西装上。",
        "我不再忍了。我拿起桌上的水果刀, 朝他捅了过去。",
    ],
    "情感爆发": [
        "我妈咽气前最后一句话是: '冰箱里还有排骨, 别忘了吃。'",
        "我看到他手机里, 9999 条'老婆'的消息, 才知道我只是个笑话。",
        "我抱着他, 第一次哭出声: '对不起, 我回来晚了。'",
        "她死的时候, 我正挽着别的女人逛街。",
        "离婚那天, 他没签字。他跪下来说: '我错了。'",
    ],
    "性张力": [
        "我被这个男人壁咚的那一刻, 我听见自己的心跳。",
        "出差那晚, 我和他都喝多了。第二天醒来, 他是我姐夫。",
        "我勾着他的领带: '昨晚, 你说的'永远', 是真的吗?'",
        "我脱下他的外套, 才发现他胸口那道疤, 是我留下的。",
        "婚礼前夕, 我和他共处一室。他说: '我不会碰你。' 但他没关灯。",
    ],
    "金钱冲突": [
        "他随手开了一张 500 万的支票, 让我滚。我笑出了声。",
        "破产那天, 我丈夫当着我面撕了结婚证, 拉着秘书的手走了。",
        "我以为我嫁的是穷小子, 直到看见他床头那张 50 亿的卡。",
        "我扔给他一张卡: '50 万, 离开我女儿。' 他说: '好。'",
        "我跪在他脚下: '50 亿, 我要。' 他掐着我的脸: '凭什么?'",
    ],
    "权谋反转": [
        "当所有人以为我只是个实习生, CEO 突然站起来: '董事长, 请上座。'",
        "我一句话, 让他公司的股价蒸发了 100 亿。",
        "我在董事会上, 当着所有人的面, 把他的假账本摔在他脸上。",
        "反派冷笑: '你算什么东西?' 我摘下面具: '我是你爹。'",
        "他们想让我下跪。我站起来: '想好了, 跪不跪的人是谁。'",
    ],
    "威胁生命": [
        "他掐着我脖子: '说, 把钱放哪了?' 我笑: '你猜。'",
        "我被困在电梯里, 手机没电, 门外面传来他磨刀的声音。",
        "她在我水里下了毒。我看着她: '我等这一天, 很久了。'",
        "我醒来时, 发现自己被绑在手术台上。医生说: '开始吧。'",
        "我站在 28 楼阳台, 他在楼下喊: '跳啊, 跳啊!'",
    ],
    "神秘悬念": [
        "我 18 岁那天, 收到一封来自 30 岁的我自己写的信。",
        "我接到一个电话, 对方说: '你三天后会死。' 打电话的是我。",
        "我的日记本里, 多了一页我从来没写过的话。",
        "我发现, 我家的镜子里, 站着另一个我。",
        "他死了 3 年。但他刚刚发了一条微信给我。",
    ],
}


class HookMasterPro:
    """
    钩子专项节点 — 拆节点 5/7
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 钩子参数 ===
                "钩子类型_8选1": (list(HOOK_TYPES.keys()), {"default": "身份揭秘"}),
                "钩子时长_秒": (["3", "7", "15", "30", "60"], {"default": "3"}),
                "钩子强度_1_10": ("INT", {"default": 9, "min": 1, "max": 10, "step": 1}),

                # === 2. 套路 ===
                "套路_11选1": (["穿越", "重生", "真假千金", "霸总", "战神", "团宠", "修仙/系统", "末日", "女帝/女强", "换亲", "马甲"], {"default": "穿越"}),
                "反转类型_8选1": (list(REVERSAL_TYPES.keys()), {"default": "identity_reveal"}),

                # === 3. 风格 ===
                "主角性别": (["男", "女"], {"default": "女"}),
                "画风": (["现代都市", "古装言情", "年代剧", "仙侠", "校园", "豪门宅斗"], {"default": "现代都市"}),
                "受众": (["女频", "男频", "泛人群"], {"default": "女频"}),

                # === 4. 平台 ===
                "平台": (["ReelShort", "DramaBox", "抖音", "快手", "TikTok", "电影/剧集"], {"default": "ReelShort"}),

                # === 5. 实战 ===
                "实战钩子库_5选1": (["身份揭秘", "暴力冲突", "情感爆发", "性张力", "金钱冲突", "权谋反转", "威胁生命", "神秘悬念"], {"default": "身份揭秘"}),

                # === 6. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === 7. 灵魂注入 (Phase 17.6) ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
            },
            "optional": {
                "自定义元素": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("hook_template", "5_hook_samples", "anti_ai_cleaned_samples")
    FUNCTION = "build_hook"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_hook(self, **kwargs):
        if not _HAS_MASTERY:
            return ("未加载 director_mastery_v2: " + _MASTERY_ERROR, "", "")

        hook_type = kwargs.get("钩子类型_8选1", "身份揭秘")
        hook_duration = kwargs.get("钩子时长_秒", "3")
        hook_strength = kwargs.get("钩子强度_1_10", 9)
        trope = kwargs.get("套路_11选1", "穿越")
        reversal = kwargs.get("反转类型_8选1", "identity_reveal")
        gender = kwargs.get("主角性别", "女")
        style = kwargs.get("画风", "现代都市")
        audience = kwargs.get("受众", "女频")
        platform = kwargs.get("平台", "ReelShort")
        library_type = kwargs.get("实战钩子库_5选1", "身份揭秘")
        custom = kwargs.get("自定义元素", "")

        # Phase 17.6: 灵魂注入 (用统一 wrapper, 自动处理 alias 解析 + 字段兼容)
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw != "none" and soul_secondary_raw != "auto" else None
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
                    scene_context=custom or "钩子场景",
                )
                soul_inj = inj
                fused_name = str(fused.get("name", ""))
                fused_polarity = str(fused.get("polarity", "neutral"))
                fused_arousal = str(fused.get("arousal", "medium"))
                fused_intensity = float(fused.get("intensity", 0.5))
            except Exception:
                soul_inj = ""

        # 1. 钩子模板
        # 灵魂前缀 (Phase 17.6)
        soul_header = ""
        if fused_name and _HAS_SOUL:
            soul_header = (
                "【灵魂核心 - 钩子设计】\n"
                "主导情感: " + fused_name + "\n"
                "情感强度: " + "{:.2f}".format(fused_intensity) + "\n"
                "情感极性: " + fused_polarity + "\n"
                "唤醒度: " + fused_arousal + "\n"
                "════════════════════════════════════\n\n"
            )
        template = f"""{soul_header}【{hook_duration} 秒{hook_type}钩子 - 强度 {hook_strength}/10】

【钩子规则 ({platform} 风格)】
- 前 {hook_duration} 秒必抛强冲突/强悬念/颠覆认知画面
- 杜绝铺垫/慢镜头/空镜
- 第一秒锁住观众视线
- 强度 {hook_strength}/10: {self._strength_desc(hook_strength)}

【钩子类型: {hook_type}】
{HOOK_TYPES[hook_type]}

【套路融合: {trope}】
{self._trope_tip(trope)}

【反转类型: {reversal}】
{REVERSAL_TYPES.get(reversal, "")}

【风格】
- 主角: {gender}
- 画风: {style}
- 受众: {audience}
- 平台: {platform}

【{hook_duration} 秒分镜】
- 0-1s: 画面定格 / 强冲突镜头
- 1-3s: 关键台词/事件
- 3-{hook_duration}s: 钩子升级 (留悬念)

【对白要求】
- 不超过 15 字
- 用短句制造速度感
- 用具体动作 (手/眼/呼吸) 不用情绪形容词

【自定义】
{custom if custom else "无"}

【灵魂驱动 - 钩子情绪匹配 (Phase 17.6)】
- 当前主导情感: {fused_name or "默认"}
- 钩子情绪基调: {fused_polarity or "neutral"} 极性 + {fused_arousal or "medium"} 唤醒度
- 灵魂规则: 钩子第一秒的情绪必须与主导情感强烈共振
  - 负极性高唤醒 → 暴力/威胁/绝望开头
  - 负极性低唤醒 → 失去/告别/告别式开头
  - 正极性高唤醒 → 复仇/胜利/反转式开头
  - 正极性低唤醒 → 希望/暖意/和解式开头
  - 矛盾极性 → 反差/双面/对比式开头
- 钩子强度与灵魂强度 ({fused_intensity:.2f}) 强相关, 强度越高钩子越极端
"""

        # 2. 实战钩子样本 (5 句)
        library = HOOK_LIBRARY.get(library_type, HOOK_LIBRARY["身份揭秘"])
        samples = "\n".join([f"  {i+1}. {s}" for i, s in enumerate(library)])

        # 3. 反 AI 清洗后样本
        cleaned = []
        for s in library[:3]:
            cleaned_s = clean_anti_ai_text(s)
            cleaned.append(f"原文: {s}\n  → 清洗: {cleaned_s}\n")
        cleaned_text = "\n".join(cleaned)

        # Knowledge Base 决策注入
        if _HAS_KB:
            try:
                _kb_hooks = get_short_drama_patterns(hook_type)
                _kb_viral = get_viral_techniques(platform)
                kb_block = "\n════════════════════════════════════\n"
                kb_block += "【Knowledge Base — 开场钩子 + 病毒式技法】\n"
                kb_block += "════════════════════════════════════\n\n"
                kb_block += "开场钩子模式 (" + hook_type + "): " + str(_kb_hooks)[:300] + "\n\n"
                kb_block += "病毒式技法 (" + platform + "): " + str(_kb_viral)[:300] + "\n"
                template += kb_block
            except Exception:
                pass

        if kwargs.get("启用反AI规则", True):
            template = inject_anti_ai_rules(template)

        return (template, samples, cleaned_text)

    def _strength_desc(self, strength):
        if strength >= 9:
            return "极致 - 颠覆认知, 观众必停下滑"
        elif strength >= 7:
            return "强烈 - 强冲突, 高留存"
        elif strength >= 5:
            return "中等 - 有钩子, 但不够颠覆"
        else:
            return "温和 - 留白多, 不适合短剧"

    def _trope_tip(self, trope):
        tips = {
            "穿越": "开篇可直接展示现代物品/技能在古代的反差碾压",
            "重生": "开篇可展示重生瞬间/前世最后场景闪回",
            "真假千金": "开篇可展示身份被揭穿/养父母突然翻脸",
            "霸总": "开篇可展示霸总语录/权力压制/宠溺",
            "战神": "开篇可展示妻女被欺/战神身份即将曝光",
            "团宠": "开篇可展示主角被欺负/真大佬身份即将曝光",
            "修仙/系统": "开篇可展示系统激活瞬间/功法觉醒",
            "末日": "开篇可展示末日第一秒/重生回到末日之前",
            "女帝/女强": "开篇可展示女性力量觉醒/女强金句",
            "换亲": "开篇可展示换亲现场/身份置换",
            "马甲": "开篇可展示马甲被揭/装弱时刻",
        }
        return tips.get(trope, "")


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "HookMasterPro": HookMasterPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "HookMasterPro": "🎣 钩子大师 (5/7)",
# }
