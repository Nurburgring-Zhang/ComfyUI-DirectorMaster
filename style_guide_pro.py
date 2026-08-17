# -*- coding: utf-8 -*-
"""
StyleGuidePro - 风格指南节点 (环节 8)
================================================
Phase 28 P1 - AIGC 影视全流程解析 补全节点

数据源 (Phase 28 联网研究):
- 5 大调色风格 (梦幻/日韩/素雅/性感/流行) - 抖音/勤学网
- 5 种电影配色方案 (单色/互补色/相似色/三元色/不协调) - 尊正资讯/搜狐
- 6 大电影配色 (王家卫/韦斯·安德森/陈凯歌/诺兰/塔可夫斯基/黑泽明)
- 5 大调色口诀 (光影逻辑/色彩情绪/实战细节) - 抖音
- 20 调色口诀 (高光透气阴影藏戏/冷唇暖肤/撞色不撞明 等)

核心能力:
- 5 调色风格生成 (梦幻/日韩/素雅/性感/流行)
- 5 配色方案生成 (单色/互补色/相似色/三元色/不协调)
- 6 导演色彩体系融合
- 风格指南完整文档生成 (用于 AI 视频生成 prompt)
- 全局风格一致性控制
"""
from __future__ import annotations

import json

try:
    from anti_ai_vocab import clean_anti_ai_text, inject_anti_ai_rules
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False

try:
    from aesthetic_judgment_pro import DIRECTOR_COLOR_SYSTEMS_6
    _HAS_AJP = True
except Exception:
    _HAS_AJP = False

# === Phase 36.6 v5i: 35 导演统一数据中枢 (8 大师 + 5 调色 + 9 构图) ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, ALL_DIRECTOR_NAMES, get_director_profile,
        DP_8_MASTERS,
        COLOR_STYLES_5 as DDU_COLOR_STYLES,
        COMPOSITION_RULES_9,
        get_director,
    )
    _HAS_DDU = True
except Exception:
    _HAS_DDU = False


# ============================================================
# 5 大调色风格 (抖音/勤学网 20 调色口诀 + 5 流行风格)
# ============================================================
COLOR_STYLES_5 = {
    "梦幻": {
        "name_zh": "梦幻风 (Dreamy)",
        "description": "虚幻/梦境/如仙境, 色彩两极化, 低饱和度与高饱和度并存, 渐变加光, 蒙版模糊",
        "key_colors": ["粉紫", "青蓝", "暖橙", "白"],
        "lighting": "Soft Light 叠加 + Blur 模糊 + 渐变加光",
        "applies_to": ["MV", "短剧", "文艺片", "少女系"],
        "mood": "tenderness,longing,joy",
        "prompt_keywords": "dreamy, ethereal, soft light, bokeh, gradient, fantasy glow",
    },
    "日韩": {
        "name_zh": "日韩风 (J-K Style)",
        "description": "日范儿色彩柔和温暖, 暗部冷调, 亮部暖调, 低保和高对比; 韩范儿色彩鲜艳",
        "key_colors": ["暖米黄", "冷青", "粉橘", "墨绿"],
        "lighting": "暖白 + 冷阴影, 自然光为主, 高调",
        "applies_to": ["青春片", "爱情片", "日常剧", "写真"],
        "mood": "warm_regret,tenderness,trust",
        "prompt_keywords": "soft, warm tones, J-pop aesthetic, high key, pastel",
    },
    "素雅": {
        "name_zh": "素雅风 (Minimalist)",
        "description": "干净时尚大气, 画面柔和细腻, 低饱和, 低对比, 减色加灰, 明度载入",
        "key_colors": ["米白", "浅灰", "淡蓝", "浅咖"],
        "lighting": "高调均匀, 自然光, 无强烈对比",
        "applies_to": ["文艺片", "时尚", "建筑", "高端商业"],
        "mood": "trust,tenderness,anticipation",
        "prompt_keywords": "minimalist, clean, low saturation, soft, high key, contemporary",
    },
    "性感": {
        "name_zh": "性感风 (Sensual)",
        "description": "大胆暴露, 皮肤细腻, 以红黄调整为主, 黄色和红色, 黑柔光, 室内私房",
        "key_colors": ["深红", "金黄", "肌肤色", "深黑"],
        "lighting": "侧光 + 暖色柔光 + 黑柔光, 私密感",
        "applies_to": ["私房照", "女性写真", "MV 慢歌", "情欲戏"],
        "mood": "desire,longing,anticipation",
        "prompt_keywords": "sensual, warm golden, skin glow, intimate lighting, soft focus",
    },
    "流行": {
        "name_zh": "流行/橙青风 (Orange-Teal Blockbuster)",
        "description": "好莱坞大片标准, 橙色高光/中间调肤色, 蓝绿色阴影, 互补色高对比",
        "key_colors": ["橙", "蓝绿 (Teal)", "深棕", "黄"],
        "lighting": "强对比, 橙色高光, 蓝绿阴影, 戏剧化",
        "applies_to": ["商业大片", "动作片", "科幻片", "漫改"],
        "mood": "anticipation,anger,trust",
        "prompt_keywords": "orange and teal, blockbuster, high contrast, cinematic color grade",
    },
}


# ============================================================
# 5 种电影配色方案 (尊正资讯/搜狐)
# ============================================================
COLOR_SCHEMES_5 = {
    "单色": {
        "description": "单一颜色的不同色调, 柔和舒缓的和谐感",
        "color_theory": "monochromatic - same hue, different values/saturations",
        "examples": ["黑客帝国 (绿)", "花样年华 (红)"],
        "use_when": "需要统一氛围, 不分散注意力",
    },
    "互补色": {
        "description": "色轮上相对的两种颜色, 强烈戏剧化对比",
        "color_theory": "complementary - opposite colors, high tension",
        "examples": ["天使爱美丽 (红绿)", "搏击俱乐部 (橙蓝绿)", "亡命驾驶 (橙蓝绿)"],
        "use_when": "需要冲突/对立/张力",
    },
    "相似色": {
        "description": "色相环上邻近的颜色, 柔和协调, 非暖非冷",
        "color_theory": "analogous - adjacent colors, harmonious",
        "examples": ["美国骗局 (红橙棕黄)", "人类之子"],
        "use_when": "需要整体和谐, 自然风景",
    },
    "三元色": {
        "description": "色轮上等距 120 度的三种颜色, 醒目有冲击力",
        "color_theory": "triadic - three equal-spaced colors",
        "examples": ["狂人皮埃罗 (红蓝绿)"],
        "use_when": "需要强烈视觉效果, 罕见但冲击",
    },
    "不协调色": {
        "description": "偏离主色调的颜色, 引导观众注意力到特定元素",
        "color_theory": "clashing colors - intentionally dissonant",
        "examples": ["天使爱美丽 (绿色)", "第六感 (红色)", "闪灵"],
        "use_when": "需要突出特定角色/物体/场景",
    },
}


# ============================================================
# 20 大调色口诀 (抖音/网易)
# ============================================================
GRADING_TIPS_20 = [
    "高光透气, 阴影藏戏: 高光添微青/蓝显透气, 阴影加灰棕/墨绿藏故事感",
    "亮部柔, 暗部实: 亮部低对比柔化, 暗部强化纹理, 增强立体感",
    "光从哪来, 色往哪染: 受光面叠暖色 (如侧光加橙), 背光面补冷色平衡",
    "逆光不脏, 补色要藏: 逆光降灰雾, 暗部补色饱和度控在 10% 内",
    "轮廓靠光, 情绪靠影: 高光勾勒轮廓, 阴影调情绪 (如忧郁蓝、温暖橙)",
    "冷唇暖肤, 高级不突兀: 暖橘肤色配冷玫红唇色, 冷暖对比",
    "背景压暗, 人物跳脱: 背景降明度变冷调, 人物提亮变微暖",
    "同色系渐变, 杂色要切断: 同色系渐变过渡, 杂色降饱和",
    "情绪看色温, 故事看色调: 悲伤用低色温蓝灰, 回忆用高色温黄绿",
    "撞色不撞明: 红绿撞色, 降一方明度 (如暗红配灰绿), 避免刺眼",
    "皮肤质感, 橙黄当家: HSL 橙色调肤色, 加明度减饱和显通透",
    "眼神光冷, 氛围才稳: 眼球高光加冷白 (如青蓝), 避免死白",
    "发色不抢戏, 灰调压艳丽: 头发艳就 HSL 降饱和加灰 (如红变棕红)",
    "服装色彩, 背景让路: 人物穿亮色, 背景选中性色或互补色低饱和版",
    "瑕疵隐形, 纹理救命: 磨皮后加 10% 纹理, 去瑕疵还留真实肌理",
    "暗部冷亮部暖: 经典好莱坞调色口诀, 暗部加蓝绿, 亮部加橙",
    "橙青是好莱坞标配: 70% 橙色高光肤色 + 30% 蓝绿阴影",
    "霓虹不溢出: 霓虹光不调到 100% 饱和, 加点白雾保留细节",
    "黑场不纯黑: 最暗部 RGB 不低于 (10,10,15) 保留细节",
    "白场不纯白: 最亮部 RGB 不超过 (245,245,245) 避免死白",
]


# ============================================================
# 主入口
# ============================================================
def generate_style_guide(style="梦幻", scheme="互补色", director="",
                          include_tips=True, include_palette=True):
    """
    生成风格指南

    Args:
        style: 5 大调色风格之一
        scheme: 5 种配色方案之一
        director: 6 大导演之一 (空 = 通用)
        include_tips: 包含 20 调色口诀
        include_palette: 包含调色盘
    """
    if _HAS_ANTI_AI:
        pass

    # 1. 调色风格
    style_info = COLOR_STYLES_5.get(style, COLOR_STYLES_5["梦幻"])

    # 2. 配色方案
    scheme_info = COLOR_SCHEMES_5.get(scheme, COLOR_SCHEMES_5["互补色"])

    # 3. 导演体系
    director_info = None
    if director and _HAS_AJP and director in DIRECTOR_COLOR_SYSTEMS_6:
        director_info = DIRECTOR_COLOR_SYSTEMS_6[director]

    # 4. 调色盘 (主色 + 辅色 + 强调色)
    palette = {
        "primary": style_info["key_colors"][0] if style_info["key_colors"] else "橙",
        "secondary": style_info["key_colors"][1] if len(style_info["key_colors"]) > 1 else "蓝绿",
        "accent": style_info["key_colors"][2] if len(style_info["key_colors"]) > 2 else "白",
        "shadow": style_info["key_colors"][3] if len(style_info["key_colors"]) > 3 else "深棕",
    }

    # 5. 生成完整风格指南
    guide = {
        "调色风格": style_info,
        "配色方案": scheme_info,
        "导演体系": director_info,
        "调色盘": palette if include_palette else None,
        "调色口诀": GRADING_TIPS_20 if include_tips else None,
    }

    # 6. 生成用于 AI 视频生成的 prompt 关键词
    prompt_parts = [style_info["prompt_keywords"]]
    if director_info:
        prompt_parts.append(director_info.get("primary", ""))
        prompt_parts.append(director_info.get("lighting", ""))
    full_prompt = ", ".join([p for p in prompt_parts if p])

    guide["full_prompt"] = full_prompt

    return guide


# ============================================================
# ComfyUI 节点
# ============================================================
class StyleGuidePro:
    """
    风格指南 Pro 节点 - Phase 28 P1
    环节 8 - 全局风格一致性控制

    自动赋予: 默认梦幻 + 互补色
    专项调整: 5 风格 + 5 配色 + 6 导演 + 20 口诀
    """

    @classmethod
    def INPUT_TYPES(cls):
        _director_choices = (["auto", "无"] + ALL_DIRECTOR_NAMES) if _HAS_DDU else (
            ["auto", "无", "王家卫", "韦斯·安德森", "陈凯歌", "诺兰", "塔可夫斯基", "黑泽明"]
        )
        return {
            "required": {
                "调色风格": (list(COLOR_STYLES_5.keys()) + ["auto"], {"default": "梦幻"}),
                "配色方案": (list(COLOR_SCHEMES_5.keys()) + ["auto"], {"default": "互补色"}),
                # Phase 36.6 v5i: 35 导演真实档案 (镜头/光/节奏/色彩/表演/构图/声音/情绪)
                "导演体系": (_director_choices, {"default": "auto"}),
            },
            "optional": {
                "包含调色口诀": (["ON", "OFF"], {"default": "ON"}),
                "包含调色盘": (["ON", "OFF"], {"default": "ON"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("风格指南", "完整 Prompt", "调色盘", "调色口诀")
    FUNCTION = "guide"
    CATEGORY = "Director/StyleGuide"

    def guide(self, **kwargs):
        style = kwargs.get("调色风格", "梦幻")
        if style == "auto":
            style = "梦幻"
        scheme = kwargs.get("配色方案", "互补色")
        if scheme == "auto":
            scheme = "互补色"
        director = kwargs.get("导演体系", "auto")
        if director in ("auto", "无"):
            director = ""
        include_tips = kwargs.get("包含调色口诀", "ON") == "ON"
        include_palette = kwargs.get("包含调色盘", "ON") == "ON"

        result = generate_style_guide(
            style=style,
            scheme=scheme,
            director=director,
            include_tips=include_tips,
            include_palette=include_palette,
        )

        guide_text = "【{} + {}】\n导演: {}\n主色: {}\n光影: {}\n适用: {}".format(
            result["调色风格"]["name_zh"],
            result["配色方案"]["description"],
            director or "通用",
            result["调色风格"]["key_colors"],
            result["调色风格"]["lighting"],
            result["调色风格"]["applies_to"],
        )

        # Phase 36.6 v5i: 35 导演 8 维真实档案 (镜头/光/节奏/色彩/表演/构图/声音/情绪)
        if director and _HAS_DDU and director in DIRECTOR_PROFILES_ALL:
            d_p = DIRECTOR_PROFILES_ALL[director]
            guide_text += "\n\n【Phase 36.6 v5i: 35 导演 8 维真实档案】\n"
            guide_text += f"  镜头: {d_p['镜头']}\n"
            guide_text += f"  光: {d_p['光']}\n"
            guide_text += f"  节奏: {d_p['节奏']}\n"
            guide_text += f"  色彩: {d_p['色彩']}\n"
            guide_text += f"  表演: {d_p['表演']}\n"
            guide_text += f"  构图: {d_p['构图']}\n"
            guide_text += f"  声音: {d_p['声音']}\n"
            guide_text += f"  情绪: {d_p['情绪']}\n"
            guide_text += f"  代表作: {d_p['代表作']} (年代 {d_p['年代']})\n"
            guide_text += f"  物件: {d_p['物件']}\n"
            guide_text += f"  5维标签: {d_p['5维标签']}\n"
            # 8 大师摄影指导匹配
            tag_set = set(d_p["5维标签"].split("/"))
            for dp_name, dp_info in DP_8_MASTERS.items():
                if "罗杰·狄金斯" in dp_name and dp_info.get("代表作") == []:
                    continue
                dp_tag = set(dp_info.get("5维标签", "").split("/"))
                if tag_set & dp_tag:
                    guide_text += f"  推荐摄影指导: {dp_name} - {dp_info['signature']}\n"
                    break

        full_prompt = result.get("full_prompt", "")
        # Phase 36.6 v5i: 把 director 5 维标签加到 full_prompt
        if director and _HAS_DDU and director in DIRECTOR_PROFILES_ALL:
            d_p = DIRECTOR_PROFILES_ALL[director]
            full_prompt += f", {d_p['5维标签']}, {d_p['代表作'][:40]}"

        palette_str = json.dumps(result.get("调色盘", {}), ensure_ascii=False, indent=2)
        tips_str = ""
        if include_tips and result.get("调色口诀"):
            for i, tip in enumerate(result["调色口诀"], 1):
                tips_str += "{}. {}\n".format(i, tip)

        return (guide_text, full_prompt, palette_str, tips_str)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "StyleGuidePro": StyleGuidePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "StyleGuidePro": "🎨 风格指南 Pro (环节8) — Phase 28 P1 / 5风格+5配色+6导演+20口诀",
# }
