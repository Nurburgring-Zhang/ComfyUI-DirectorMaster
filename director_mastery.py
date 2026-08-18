# -*- coding: utf-8 -*-
"""
导演能力总控节点 (DirectorMasteryNode)
=========================================

**Phase 36.6 v5 整体控制节点**:
- 一个节点 = 4 个核心起点节点的能力聚合
  1. 灵魂注入 (DirectorSoulNode 的 60 情感 + 10 维度 + 7 融合)
  2. 审美判断 (AestheticJudgmentPro 的 8 原则 + 120 场景)
  3. 风格指南 (StyleGuidePro 的 5 调色 + 6 导演)
  4. 导演意图 (DirectorIntentPro 的 4 类意图)

**为什么是总控**:
- 用户在 ComfyUI 里拖 1 个节点 = 拖 4 个节点
- 4 个起点节点的 widget 全部整合到一个节点的 30+ widget
- 输出 4 路灵魂注入, 1 路统一 prompt, 1 路导演签名
- 工作流更简洁, 节点更少, 整体控制

**用法**:
- 用户在 ComfyUI 里调节点内的 widget 即可同时控制灵魂/审美/风格/意图
- 不需要连 4 个起点节点
- 输出 (灵魂注入_整合) 直接连到所有需要灵魂的节点的 [灵魂注入] slot
- 输出 (统一电影 prompt) 直接连 CLIPTextEncode 的 text (但 ComfyUI 设计 text 是 widget, 所以用户直接复制粘贴)
"""
import json

# === Phase 36.6 v5i: 35 导演统一数据中枢 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, ALL_DIRECTOR_NAMES, get_director_profile,
        SCENE_DATABASE_100,
        QUOTES_30,
        DP_8_MASTERS,
        COLOR_STYLES_5,
        COMPOSITION_RULES_9,
        DIRECTOR_12_DIMS,
        get_director,
        get_scene,
        get_random_quote,
    )
    _DIRECTOR_DATA_LOADED = True
    # 35 导演 (中英双语) - 实际只用中文名 + (English)
    _DIRECTOR_35_DUAL = [
        "王家卫 (Wong Kar-wai)", "塔可夫斯基 (Tarkovsky)", "黑泽明 (Kurosawa)",
        "诺兰 (Christopher Nolan)", "奉俊昊 (Bong Joon-ho)", "侯孝贤 (Hou Hsiao-hsien)",
        "维伦纽瓦 (Denis Villeneuve)", "斯科塞斯 (Scorsese)", "是枝裕和 (Kore-eda)",
        "周星驰 (Stephen Chow)", "宫崎骏 (Miyazaki)", "北野武 (Kitano)",
        "姜文 (Jiang Wen)", "张艺谋 (Zhang Yimou)", "陈凯歌 (Chen Kaige)",
        "费穆 (Fei Mu)", "小津安二郎 (Ozu)", "沟口健二 (Mizoguchi)",
        "成濑巳喜男 (Naruse)", "今村昌平 (Imamura)", "岩井俊二 (Iwai Shunji)",
        "兰斯莫斯 (Lanthimos)", "葛韦格 (Gerwig)", "李沧东 (Lee Chang-dong)",
        "贾樟柯 (Jia Zhangke)", "库斯杜力卡 (Kusturica)", "市川崑 (Ichikawa)",
        "木下惠介 (Kinoshita)", "大岛渚 (Oshima)", "增村保造 (Masumura)",
        "深作欣二 (Fukasaku)", "安哲罗普洛斯 (Angelopoulos)", "贝拉·塔尔 (Béla Tarr)",
        "维姆·文德斯 (Wenders)", "今敏 (Satoshi Kon)", "押井守 (Oshii)",
    ]
except Exception as _e:
    _DIRECTOR_DATA_LOADED = False
    _DIRECTOR_35_DUAL = []

# === anti_ai_vocab 模块检测 ===
try:
    from anti_ai_vocab import ANTI_AI_PHRASES as _ANTI_AI_PHRASES_CHECK
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False


# 60 情感 (Phase 36.6 v5i: 缩减为 12 主情感 + 60 子情感, 主情感与 12 维 DIRECTOR_12_DIMS["主导情感"] 对齐)
SOUL_EMOTION_KEYS = [
    "auto", "love", "longing", "ambition", "fear", "joy", "anger", "grief",
    "hope", "shame", "pride", "wonder", "tenderness",
    # 子情感 (向后兼容 60 体系)
    "aggressiveness", "anger_annoyance", "anger_frustration", "anger_fury",
    "anticipation_expectation", "anticipation_interest", "anticipation_vigilance",
    "awe", "awed_fear", "bittersweet", "bittersweet_pain", "chou", "chouchang",
    "contempt", "despair", "disapproval", "disgust_dislike", "disgust_loathing",
    "disgust_revulsion", "fear_apprehension", "fear_terror", "fear_timidity",
    "gratitude", "guilt", "hate", "hopeless_hope", "interest", "ji",
    "joy_ecstasy", "joy_pleasure", "joy_serenity", "loneliness", "love_hate",
    "lucid_despair", "nostalgia", "optimism", "perfect_regret",
    "relief", "remorse", "sadness_gloominess", "sadness_grief", "sadness_sorrow",
    "shyness", "surprise_amazement", "surprise_astonishment", "surprise_uncertainty",
    "tender_contradiction", "tension", "trust_acceptance", "trust_admiration",
    "trust_surrender", "warm_regret", "yuan", "none",
]

# 10 灵魂维度 (Phase 36.6 v5i: 与 DIRECTOR_12_DIMS["灵魂维度"] 对齐)
SOUL_DIMS = [
    "创造力", "想象力", "艺术表达", "镜头技巧", "氛围掌控",
    "灵感指数", "疲劳指数", "怀疑指数", "叛逆指数", "突破勇气",
]

# 7 融合模式 (Phase 36.6 v5i: 与 DIRECTOR_12_DIMS["融合模式"] 对齐)
SOUL_FUSION_MODES = [
    "auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
    "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化",
]

# 35 导演 (Phase 36.6 v5i: 从 8 扩展到 35, 全部用 director_data_unified)
DIRECTOR_AESTHETIC_8 = _DIRECTOR_35_DUAL if _DIRECTOR_DATA_LOADED else [
    "Paul Thomas Anderson (PTA)", "Christopher Nolan (诺兰)", "奉俊昊 (Bong Joon-ho)",
    "Martin Scorsese (斯科塞斯)", "Denis Villeneuve (维伦纽瓦)",
    "Yorgos Lanthimos (兰斯莫斯)", "Greta Gerwig (葛韦格)", "黑泽明 (Kurosawa)",
    "王家卫 (Wong Kar-wai)", "塔可夫斯基 (Tarkovsky)", "库斯杜力卡 (Kusturica)",
    "约阿希姆·提尔 (Joachim Trier)",
]

# 6 调色风格 (Phase 36.6 v5i: 5 调色 + 1 通用)
COLOR_STYLES_6 = ["梦幻", "赛博朋克", "复古胶片", "黑白", "暖色", "冷色"]

# 4 类导演意图
INTENT_TYPES = [
    "情感冲击", "哲学深度", "社会隐喻", "美学实验",
]


class DirectorMasteryNode:
    """导演能力总控节点 - 1 节点 = 4 节点能力"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 灵魂注入 (10 维 + 主导情感 + 融合) ===
                "主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "次要情感_1": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_2": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_3": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_4": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),
                "主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                "创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "疲劳指数": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.05}),
                "怀疑指数": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "叛逆指数": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05}),
                "突破勇气": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 2. 导演 (灵魂状态 + 导演选择) ===
                "导演选择": ("STRING", {"default": "王家卫", "multiline": False}),
                "场景描述": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边",
                    "multiline": True,
                }),

                # === 3. 审美判断 (8 原则) ===
                "审美输入": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨",
                    "multiline": True,
                }),

                # === 4. 风格指南 (调色 + 配色) ===
                "调色风格": (COLOR_STYLES_6, {"default": "梦幻"}),
                "导演体系": ("STRING", {"default": "王家卫", "multiline": False}),

                # === 5. 导演意图 (4 类) ===
                "意图类型": (INTENT_TYPES, {"default": "情感冲击"}),
                "观众应感到": ("STRING", {
                    "default": "让观众感到复杂, 难说清",
                    "multiline": True,
                }),

                # === 6. 启用反 AI 规则 ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # === 业务链 slot (接收下游输出) ===
                "上游灵魂注入": ("STRING", {"default": "", "multiline": True, "tooltip": "上游节点注入的灵魂字符串 (可被本节点综合)"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "灵魂注入_整合",
        "审美判断",
        "风格指南",
        "导演意图",
        "统一电影提示词",
        "导演签名",
        "反AI清理后",
    )
    FUNCTION = "build_mastery"
    CATEGORY = "PromptLibrary/起点/总控"

    def build_mastery(self, **kwargs):
        """
        总控节点: 聚合灵魂/审美/风格/意图
        Phase 36.6 v5i: 集成 35 导演 8 维真实档案 + 100 场景匹配 + 30 名言
        """
        # 1. 灵魂注入字符串
        dominant = kwargs.get("主导情感", "auto")
        sub1 = kwargs.get("次要情感_1", "none")
        sub2 = kwargs.get("次要情感_2", "none")
        sub3 = kwargs.get("次要情感_3", "none")
        sub4 = kwargs.get("次要情感_4", "none")
        fusion = kwargs.get("融合模式", "auto")
        main_weight = kwargs.get("主导权重", 1.0)
        creativity = kwargs.get("创造力", 0.85)
        imagination = kwargs.get("想象力", 0.85)
        art = kwargs.get("艺术表达", 0.85)
        camera = kwargs.get("镜头技巧", 0.85)
        atmosphere = kwargs.get("氛围掌控", 0.85)
        inspiration = kwargs.get("灵感指数", 0.85)
        fatigue = kwargs.get("疲劳指数", 0.3)
        doubt = kwargs.get("怀疑指数", 0.5)
        rebellion = kwargs.get("叛逆指数", 0.7)
        breakthrough = kwargs.get("突破勇气", 0.85)
        story_intensity = kwargs.get("故事强度", 0.5)
        scene_progress = kwargs.get("场景进度", 0.0)
        director = kwargs.get("导演选择", "王家卫")
        scene_desc = kwargs.get("场景描述", "")

        director_zh = director.split(" (")[0].split("（")[0].strip() if director else "王家卫"
        director_8d = None
        scene_match = None
        random_quote = None
        if _DIRECTOR_DATA_LOADED:
            director_8d = get_director_profile(director_zh)
            if director_8d:
                scene_match = get_scene(director_zh, scene_keyword=scene_desc)
                random_quote = get_random_quote()

        # 1. 灵魂注入字符串
        soul_lines = [
            "[灵魂注入]",
            f"主导情感: {dominant}",
            f"次要情感: {sub1}, {sub2}, {sub3}, {sub4}",
            f"融合模式: {fusion}",
            f"主导权重: {main_weight}",
            f"10 灵魂维度: 创造力={creativity}, 想象力={imagination}, 艺术表达={art}, "
            f"镜头技巧={camera}, 氛围掌控={atmosphere}, 灵感={inspiration}, "
            f"疲劳={fatigue}, 怀疑={doubt}, 叛逆={rebellion}, 突破={breakthrough}",
            f"灵魂状态: 故事强度={story_intensity}, 场景进度={scene_progress}",
            f"导演: {director}",
            f"场景: {scene_desc}",
        ]
        if director_8d:
            soul_lines.extend([
                f"导演 8 维真实档案 (Phase 36.6 v5i 集成):",
                f"  镜头={director_8d['镜头']}",
                f"  光={director_8d['光']}",
                f"  节奏={director_8d['节奏']}",
                f"  色彩={director_8d['色彩']}",
                f"  表演={director_8d['表演']}",
                f"  构图={director_8d['构图']}",
                f"  声音={director_8d['声音']}",
                f"  情绪={director_8d['情绪']}",
                f"  代表作={director_8d['代表作']}",
                f"  年代={director_8d['年代']}",
                f"  物件={director_8d['物件']}",
                f"  5维标签={director_8d['5维标签']}",
            ])
        if scene_match and scene_match.get("director") != "通用":
            soul_lines.append(
                f"场景匹配: {scene_match['director']} - {scene_match['scene']} | "
                f"物件={scene_match['object']} | 色调={scene_match['color']} | "
                f"声景={scene_match['sound']} | 情绪={scene_match['emotion']}"
            )
        if random_quote:
            soul_lines.append(f"导演名言: {random_quote[0]} - \"{random_quote[1]}\"")
        soul_injection = "\n".join(soul_lines) + "\n"

        # 2. 审美判断 (Phase 36.6 v5i: 用导演 8 维真实档案评估)
        aesthetic_input = kwargs.get("审美输入", scene_desc)
        aesthetic_lines = [
            "[审美判断]",
            f"输入: {aesthetic_input}",
            "8 原则应用: 1.主体明确 2.光影层次 3.色彩节制 4.构图张力 5.情绪留白 "
            "6.节奏呼吸 7.细节具体 8.反 AI 词表规避",
        ]
        if director_8d:
            aesthetic_lines.extend([
                f"基于 {director_zh} 真实档案评估:",
                f"  光影评估: {director_8d['光']} → 9D 设计对齐",
                f"  色彩评估: {director_8d['色彩']} → 60-30-10 (主-辅-点)",
                f"  构图评估: {director_8d['构图']} → 9 法适配",
                f"  情绪评估: {director_8d['情绪']} → 主导情感锁定",
            ])
        score = 0
        reasons = []
        if director_8d:
            score += 2
            reasons.append("导演真实档案匹配")
        else:
            reasons.append("⚠ 无导演档案")
        if aesthetic_input and len(aesthetic_input) > 20:
            score += 1
            reasons.append("审美输入有效")
        else:
            reasons.append("⚠ 审美输入过短或为空")
        if kwargs.get("场景描述", "") and len(kwargs.get("场景描述", "")) > 10:
            score += 1
            reasons.append("场景描述具体")
        else:
            reasons.append("⚠ 场景描述缺失或过短")
        if kwargs.get("灵魂_主导情感", "auto") != "auto":
            score += 1
            reasons.append("情感指定明确")
        else:
            reasons.append("⚠ 情感为auto默认")
        if _HAS_ANTI_AI:
            from anti_ai_vocab import ANTI_AI_PHRASES
            ai_count = sum(1 for phrase in list(ANTI_AI_PHRASES.keys())[:50] if phrase.lower() in aesthetic_input.lower())
            if ai_count == 0:
                score += 1
                reasons.append("反AI词汇清洁")
            else:
                reasons.append(f"⚠ 发现{ai_count}个AI词汇")
        total = 6
        pct = round(score / total * 100)
        level = "L5顶级" if pct >= 85 else "L4高级" if pct >= 65 else "L3中级" if pct >= 45 else "L2基础"
        aesthetic_lines.append(f"评估: {level} ({score}/{total}, {pct}%) — {'; '.join(reasons)}")
        aesthetic = "\n".join(aesthetic_lines) + "\n"

        # 3. 风格指南 (Phase 36.6 v5i: 5 调色 + 9 构图 + 8 大师)
        color_style = kwargs.get("调色风格", "梦幻")
        director_system = kwargs.get("导演体系", director)
        # 5 调色查实际色板
        color_palette = ""
        if _DIRECTOR_DATA_LOADED and color_style in COLOR_STYLES_5:
            color_palette = " / ".join(COLOR_STYLES_5[color_style].get("color_palette", []))
        # 8 大师查实际匹配
        dp_recommend = ""
        if _DIRECTOR_DATA_LOADED and director_8d:
            tag_set = set(director_8d["5维标签"].split("/"))
            for dp_name, dp_info in DP_8_MASTERS.items():
                if "罗杰·狄金斯" in dp_name and dp_info.get("代表作") == []:
                    continue
                dp_tag = set(dp_info.get("5维标签", "").split("/"))
                if tag_set & dp_tag:
                    dp_recommend = f"{dp_name}: {dp_info['signature']}"
                    break
        style_lines = [
            "[风格指南]",
            f"调色风格: {color_style}" + (f" (色板: {color_palette})" if color_palette else ""),
            f"导演体系: {director_system}",
            "色板: 60-30-10 (主色-辅色-点缀)",
            "光影: 9D 设计 (光源/方向/色温/强度/形状/质感/时间/情绪/对比)",
            "构图: 9 法 (三分/黄金/对称/中心/对角/三角/框中框/引导线/留白)",
        ]
        if dp_recommend:
            style_lines.append(f"摄影指导推荐 (Phase 36.6 v5i): {dp_recommend}")
        if director_8d:
            style_lines.append(f"导演专属: 镜头={director_8d['镜头']}, 节奏={director_8d['节奏']}")
        style_guide = "\n".join(style_lines) + "\n"

        # 4. 导演意图
        intent_type = kwargs.get("意图类型", "情感冲击")
        audience_feel = kwargs.get("观众应感到", "")
        director_intent_lines = [
            "[导演意图]",
            f"类型: {intent_type}",
            f"观众应感到: {audience_feel}",
            "潜文本: 通过场景的细节暗示情感, 不直接说教",
        ]
        if director_8d:
            director_intent_lines.append(f"导演情绪风格: {director_8d['情绪']}")
            director_intent_lines.append(f"导演 5 维标签: {director_8d['5维标签']}")
        director_intent = "\n".join(director_intent_lines) + "\n"

        # 5. 统一电影提示词 (Phase 36.6 v5i: 集成导演 8 维 + 100 场景)
        unified_lines = [
            f"电影级 prompt ({director} 风格):",
            f"导演: {director}",
            f"场景: {scene_desc}",
            f"主导情感: {dominant}",
            f"调色: {color_style}",
            f"意图: {intent_type} - {audience_feel}",
            f"具体细节 (反 AI): 真实物件名, 真实地点, 真实品牌, 真实数字",
        ]
        if director_8d:
            unified_lines.extend([
                f"摄影: 镜头={director_8d['镜头']}",
                f"光: {director_8d['光']}",
                f"构图: {director_8d['构图']}",
                f"色彩: {director_8d['色彩']}",
                f"节奏: {director_8d['节奏']}",
                f"代表作: {director_8d['代表作']}",
                f"年代/地点: {director_8d['年代']}",
                f"标志物件: {director_8d['物件']}",
            ])
        else:
            unified_lines.extend([
                f"摄影: 8 大师风格 ({director_system})",
                f"光: 自然光 / 顺光 / warm 3200K",
                f"构图: 9 法之 rule_of_thirds",
                f"色彩: 60-30-10 (主色 60% 冷蓝 / 辅色 30% 霓虹紫 / 点缀 10% 戏剧红)",
            ])
        if scene_match and scene_match.get("director") != "通用":
            unified_lines.append(
                f"场景匹配参考: {scene_match['scene']} - 物件 {scene_match['object']}, "
                f"色调 {scene_match['color']}, 声景 {scene_match['sound']}"
            )
        unified_lines.append(
            f"提示: {creativity} 创造力 + {art} 艺术表达 + {camera} 镜头技巧"
        )
        unified_prompt = "\n".join(unified_lines) + "\n"

        # 6. 导演签名 (Phase 36.6 v5i: 加 5 维标签)
        signature_lines = [
            f"导演: {director}",
            f"风格: {color_style} + {director_system}",
            f"灵魂: 创造力{creativity} 想象力{imagination} 艺术表达{art}",
            f"意图: {intent_type}",
        ]
        if director_8d:
            signature_lines.append(f"5维标签: {director_8d['5维标签']}")
        signature = "\n".join(signature_lines) + "\n"

        # 7. 反 AI 清理 (Phase 36.6 v5i: 用 281 词 anti_ai_vocab)
        try:
            from anti_ai_vocab import ANTI_AI_PHRASES
            en_count = sum(
                1 for k in ANTI_AI_PHRASES
                if all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_"
                       for c in k)
            )
            total_count = len(ANTI_AI_PHRASES)
        except Exception:
            en_count, total_count = 0, 0
        anti_ai = (
            f"[反 AI 清理后 (Phase 36.6 v5i: {total_count} 词表, {en_count} 英文)]\n"
            f"删除词: masterpiece, best quality, ultra detailed, 4k, 8k, hdr, photorealistic, "
            f"hyper realistic, ultra realistic, cinematic lighting, dramatic lighting, "
            f"perfect composition, award winning, magazine cover, "
            f"blurred, low quality, cartoon, anime, watermark, text, deformed\n"
            f"替换: 用具体细节替代抽象描述\n"
            f"强制细节: 真实物件 + 真实地点 + 真实品牌 + 真实数字 + 真实五感\n"
        )

        return (
            soul_injection,
            aesthetic,
            style_guide,
            director_intent,
            unified_prompt,
            signature,
            anti_ai,
        )
