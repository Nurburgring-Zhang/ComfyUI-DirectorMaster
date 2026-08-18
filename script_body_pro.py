# -*- coding: utf-8 -*-
"""
ScriptBodyPro — 剧本正文节点 (Phase 17.6 灵魂驱动重写)
=====================================================
(节点 2/3 — 剧本输出拆分为 3 个节点)

功能:
- 接收 节点 1/3 输出的 story_architecture
- 输出: 场次/场景描写/对白/动作
- 强反 AI 词表 + 真实导演微调 + 多轮迭代
- 强制对白 8-15 字以内
- 90% 场景用具象动作
- **Phase 17.6: 真正接入 DirectorSoulNode 灵魂 (soul_inject_simple)**
  - 情感驱动: 颜色/音乐/视觉/声音/内心独白全部由灵魂动态生成
  - 不同 primary (loneliness/fear/warm_regret) → 输出真实不同

输入 (新增 3 个灵魂字段):
- 灵魂_主导情感 (单情感, auto=导演默认)
- 灵魂_场景权重 (0-1, 控制灵魂强度)
- 灵魂_次要情感 (可选, 与主导情感融合)
- 灵魂_融合模式 (F1-F7 / auto)

输出:
- script_body: 灵魂驱动剧本正文
- anti_ai_sample: 清洗后样本
- iteration_chain: 多轮迭代链
"""

import os
import sys
import json
import math

# 反 AI + 真实导演微调
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        ITERATION_TEMPLATES,
        inject_anti_ai_rules,
        clean_anti_ai_text,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)


# ============================================================
# Phase 17.6: 灵魂接入 (统一 wrapper)
# ============================================================
try:
    from director_soul import (
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
        soul_inject_simple,
    )
    _HAS_SOUL = True
except Exception as e:
    _HAS_SOUL = False
    _SOUL_ERROR = str(e)


# ============================================================
# 类型防御 helpers
# ============================================================
def _str(v, default=""):
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else default
    if isinstance(v, float) and math.isnan(v):
        return default
    return str(v)


def _f(v, default=0.0):
    if v is None:
        return default
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except (TypeError, ValueError):
        return default


# 对白密度
DIALOGUE_DENSITY = ["极少 (10%以下)", "少 (30%)", "中 (50%)", "高 (70%)", "对话为主 (90%+)"]

# 静默场景比例(王家卫/蔡明亮式)
SILENCE_RATIO = ["几乎不 (5%)", "少 (15%)", "中 (30%)", "多 (50%)", "极多 (70%+)"]

# 食物出现频率(李安/是枝裕和式)
FOOD_FREQ = ["无", "偶尔", "常出现", "核心场景"]

# 物件密度(王家卫/塔可夫斯基式)
OBJECT_DENSITY = ["少", "中", "多", "极多 (每场 3+ 物件)"]

# 时代具体度
TIME_SPECIFICITY = ["模糊 (一天)", "粗 (某个时期)", "中 (某年)", "精 (年月日)"]

# 地点具体度
PLACE_SPECIFICITY = ["模糊", "粗 (城市)", "中 (区/街道)", "精 (门牌号)"]


# 灵魂情感 keys (auto + 60 矩阵)
SOUL_EMOTION_KEYS = (
    ["auto", "none"] + list(EMOTION_MATRIX_60.keys())
    if _HAS_SOUL
    else ["auto", "none", "loneliness", "fear", "warm_regret", "longing", "bittersweet", "tenderness", "remorse"]
)

# 灵魂融合模式
SOUL_FUSION_MODES = (
    ["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
     "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"]
    if _HAS_SOUL
    else ["auto"]
)


# 导演 → 默认情感映射 (用于 auto 模式)
DIRECTOR_DEFAULT_EMOTION = {
    "王家卫": "loneliness",
    "诺兰": "anticipation_vigilance",
    "PTA": "tension",
    "奉俊昊": "disgust_loathing",
    "黑泽明": "tension",
    "库斯杜力卡": "bittersweet",
    "塔可夫斯基": "loneliness",
    "约阿希姆·提尔": "remorse",
    "是枝裕和": "tenderness",
    "侯孝贤": "loneliness",
    "伯格曼": "sadness_gloominess",
    "小津": "joy_serenity",
    "蔡明亮": "loneliness",
    "李沧东": "sadness_sorrow",
    "库布里克": "fear_apprehension",
    "毕赣": "longing",
    "贾樟柯": "nostalgia",
    "李安": "tenderness",
    "周星驰": "joy_pleasure",
    "Vince Gilligan": "tension",
    "大衛·芬奇": "tension",
    "Papi酱": "joy_pleasure",
}


# ============================================================
# ScriptBodyPro 主类
# ============================================================
class ScriptBodyPro:
    """
    剧本正文节点 — 拆节点 2/3 (Phase 17.6 灵魂驱动)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 导演风格 (业务链 slot 移到 optional, 见下) ===
                "导演风格_63选1": ("STRING", {
                    "default": "王家卫",
                    "multiline": False,
                }),

                # === 3. 风格细节 ===
                "对白密度": (DIALOGUE_DENSITY, {"default": "中 (50%)"}),
                "静默场景比例": (SILENCE_RATIO, {"default": "中 (30%)"}),
                "食物出现频率": (FOOD_FREQ, {"default": "偶尔"}),
                "物件密度": (OBJECT_DENSITY, {"default": "中"}),

                # === 4. 时代与地点 ===
                "时代具体度": (TIME_SPECIFICITY, {"default": "精 (年月日)"}),
                "地点具体度": (PLACE_SPECIFICITY, {"default": "精 (门牌号)"}),

                # === 5. 角色具体度 ===
                "对白最大字数": ("INT", {"default": 15, "min": 5, "max": 50, "step": 1}),
                "主角身体习惯": ("STRING", {
                    "default": "左眼眨眼多 / 走路外八 / 摸下巴",
                    "multiline": False,
                }),
                "主角口头禅": ("STRING", {
                    "default": "嘛 / 反正 / 嗯",
                    "multiline": False,
                }),

                # === 6. 节奏 ===
                "场次数量": ("INT", {"default": 20, "min": 3, "max": 200, "step": 1}),
                "最长场次时长秒": ("INT", {"default": 120, "min": 10, "max": 1800, "step": 1}),

                # === 7. 反 AI 强度 ===
                "反AI强度": (["关", "轻 (词表)", "中 (词表+铁律)", "重 (词表+铁律+微调)"], {"default": "重 (词表+铁律+微调)"}),

                # === 8. Phase 17.6 灵魂注入 (统一 wrapper 接口) ===
                "灵魂_主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "灵魂_融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),
            },
            "optional": {
                # === 业务链 slot (上游节点 1/3 故事架构 输出) ===
                "上游_故事架构": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "生成样例小段": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("script_body", "anti_ai_sample", "iteration_chain")
    FUNCTION = "build_script_body"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_script_body(self, **kwargs):
        director = _str(kwargs.get("导演风格_63选1", "王家卫"), "王家卫")
        architecture = _str(kwargs.get("上游_故事架构", ""), "")

        # ============================================================
        # Phase 17.6: 灵魂注入 — 统一 wrapper soul_inject_simple
        # ============================================================
        soul_primary = _str(kwargs.get("灵魂_主导情感", "auto"), "auto")
        if not soul_primary or soul_primary in ("", "auto", "none"):
            # auto → 按导演选默认情感
            soul_primary = DIRECTOR_DEFAULT_EMOTION.get(director, "loneliness")

        soul_weight = _f(kwargs.get("灵魂_场景权重", 0.6), 0.6)
        soul_secondary_raw = _str(kwargs.get("灵魂_次要情感", "none"), "none")
        soul_secondary_list = (
            [soul_secondary_raw] if soul_secondary_raw not in ("", "none", "auto") else None
        )
        soul_fusion_mode = _str(kwargs.get("灵魂_融合模式", "auto"), "auto")

        soul_inj, soul_fused, soul_state, soul_dims = ("", {}, {}, {})
        if _HAS_SOUL:
            try:
                soul_inj, soul_fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_weight,
                    director=director,
                    secondary=soul_secondary_list,
                    fusion_mode=soul_fusion_mode,
                    scene_context=architecture or "剧本场景",
                )
            except Exception as e:
                # 兜底 — 保持 API 稳定
                soul_inj = (
                    "【灵魂注入 - 兜底】\n"
                    "主导情感: " + str(soul_primary) + "\n"
                    "强度: 0.5\n"
                )
                soul_fused = {
                    "name": str(soul_primary),
                    "intensity": 0.5,
                    "polarity": "neutral",
                    "arousal": "medium",
                    "visual_signs": "由具体动作呈现",
                    "voice_signs": "语速自然",
                    "color_palette": "中性色调",
                    "music_tempo": "60-80 BPM",
                    "inner_monologue": "这一刻我想说点什么",
                    "description": str(soul_primary),
                }
                soul_state = {
                    "inspiration": 0.7, "fatigue": 0.3,
                    "doubt": 0.5, "rebelliousness": 0.6,
                    "mental_state": "lucid-dreamy",
                }
                soul_dims = {
                    "creativity": 0.85, "imagination": 0.85,
                    "artistic_expression": 0.85, "camera_skill": 0.85,
                    "atmosphere_control": 0.85, "mental_state": "lucid-dreamy",
                    "inspiration": 0.85, "rebelliousness": 0.70,
                    "self_doubt": 0.50, "breakthrough_courage": 0.85,
                }

        # 提取灵魂关键字段 (供 prompt 拼装使用)
        fused_name = soul_fused.get("name", str(soul_primary)) if isinstance(soul_fused, dict) else str(soul_primary)
        fused_intensity = float(soul_fused.get("intensity", soul_weight)) if isinstance(soul_fused, dict) else soul_weight
        fused_polarity = soul_fused.get("polarity", "neutral") if isinstance(soul_fused, dict) else "neutral"
        fused_visual = soul_fused.get("visual_signs", "") if isinstance(soul_fused, dict) else ""
        fused_voice = soul_fused.get("voice_signs", "") if isinstance(soul_fused, dict) else ""
        fused_color = soul_fused.get("color_palette", "") if isinstance(soul_fused, dict) else ""
        fused_music = soul_fused.get("music_tempo", "") if isinstance(soul_fused, dict) else ""
        fused_inner = soul_fused.get("inner_monologue", "") if isinstance(soul_fused, dict) else ""
        fused_facial_au = soul_fused.get("facial_au", "") if isinstance(soul_fused, dict) else ""
        fused_description = soul_fused.get("description", "") if isinstance(soul_fused, dict) else ""

        # 灵魂状态
        s_inspiration = float(soul_state.get("inspiration", 0.7)) if isinstance(soul_state, dict) else 0.7
        s_fatigue = float(soul_state.get("fatigue", 0.3)) if isinstance(soul_state, dict) else 0.3
        s_doubt = float(soul_state.get("doubt", 0.5)) if isinstance(soul_state, dict) else 0.5
        s_rebelliousness = float(soul_state.get("rebelliousness", 0.6)) if isinstance(soul_state, dict) else 0.6
        s_mental = soul_state.get("mental_state", "lucid-dreamy") if isinstance(soul_state, dict) else "lucid-dreamy"

        # 灵魂维度
        d_creativity = float(soul_dims.get("creativity", 0.85)) if isinstance(soul_dims, dict) else 0.85
        d_atmosphere = float(soul_dims.get("atmosphere_control", 0.85)) if isinstance(soul_dims, dict) else 0.85
        d_rebelliousness = float(soul_dims.get("rebelliousness", 0.70)) if isinstance(soul_dims, dict) else 0.70

        # 极性 → 灯光/色调倾向
        if fused_polarity == "negative":
            lighting_tone = "冷调 + 低照度 + 阴影压暗"
        elif fused_polarity == "positive":
            lighting_tone = "暖调 + 适度照度 + 高光柔化"
        elif fused_polarity == "mixed":
            lighting_tone = "冷暖对比 + 双色温 + 不稳定光感"
        else:
            lighting_tone = "中性 + 自然光"

        # 怀疑 → 静默场景比例微调
        silence_ratio_input = _str(kwargs.get("静默场景比例", "中 (30%)"), "中 (30%)")
        if s_doubt > 0.7 and "少" in silence_ratio_input:
            silence_ratio_input = "中 (30%)"
        elif s_doubt > 0.7 and "几乎不" in silence_ratio_input:
            silence_ratio_input = "少 (15%)"

        # 叛逆 → 对白密度微调
        dialogue_density_input = _str(kwargs.get("对白密度", "中 (50%)"), "中 (50%)")
        if s_rebelliousness > 0.75 and "对话为主" in dialogue_density_input:
            dialogue_density_input = "高 (70%)"

        # 用户 prompt
        user_prompt = f"""【任务: 基于以下架构写出剧本正文(场次+对白+动作) — Phase 17.6 灵魂驱动】

════════════════════════════════════════
【0. 灵魂核心 (Director Soul) — 由 soul_inject_simple 注入】
════════════════════════════════════════
主导情感: {fused_name}
情感强度: {fused_intensity:.2f}
情感极性: {fused_polarity}
情感描述: {fused_description}

【灵魂视觉表现 — 必须体现在场景描写】
{fused_visual}

【灵魂声音表现 — 必须体现在对白节奏】
{fused_voice}

【灵魂面部肌肉】
{fused_facial_au}

【灵魂内心独白 — 必须体现在潜文本】
{fused_inner}

【灵魂色彩倾向 — 决定全场视觉色温】
{fused_color}

【灵魂音乐节奏 — 决定全场节奏感】
{fused_music}

【灵魂状态】
灵感指数: {s_inspiration:.2f} | 疲劳指数: {s_fatigue:.2f} | 怀疑指数: {s_doubt:.2f} | 叛逆指数: {s_rebelliousness:.2f}
精神状态: {s_mental}

【灵魂维度】
创造力: {d_creativity:.2f} | 氛围掌控: {d_atmosphere:.2f} | 叛逆: {d_rebelliousness:.2f}
灵魂权重: {soul_weight:.2f}
融合模式: {_str(kwargs.get('灵魂_融合模式', 'auto'), 'auto')}

【灵魂驱动 — 灯光 / 节奏 / 潜文本】
灯光色调: {lighting_tone} (由极性 {fused_polarity} 决定)
潜文本核心: {fused_inner}
节奏倾向: {'静默延长 + 物件特写' if s_fatigue > 0.5 else '对话推进 + 动作密度高'}

════════════════════════════════════════
【1. 故事架构 (来自节点 1/3)】
════════════════════════════════════════
{architecture}

════════════════════════════════════════
【2. 导演风格】
════════════════════════════════════════
{director}

════════════════════════════════════════
【3. 风格细节 (灵魂微调后)】
════════════════════════════════════════
- 对白密度: {dialogue_density_input}
- 静默场景比例: {silence_ratio_input}
- 食物出现频率: {_str(kwargs.get('食物出现频率', '偶尔'), '偶尔')}
- 物件密度: {_str(kwargs.get('物件密度', '中'), '中')}

════════════════════════════════════════
【4. 具体度要求】
════════════════════════════════════════
- 时代: {_str(kwargs.get('时代具体度', '精 (年月日)'), '精 (年月日)')}
- 地点: {_str(kwargs.get('地点具体度', '精 (门牌号)'), '精 (门牌号)')}
- 对白最大字数: {_str(kwargs.get('对白最大字数', 15), '15')}
- 主角身体习惯: {_str(kwargs.get('主角身体习惯', ''), '')}
- 主角口头禅: {_str(kwargs.get('主角口头禅', ''), '')}

════════════════════════════════════════
【5. 场次】
════════════════════════════════════════
- 总场次: {_str(kwargs.get('场次数量', 20), '20')}
- 最长场次: {_str(kwargs.get('最长场次时长秒', 120), '120')} 秒

════════════════════════════════════════
【6. 灵魂驱动 — 输出格式 (场次模板)】
════════════════════════════════════════
场次 1: [场次标题, 具体时间, 具体地点]
灵魂视觉锚点: {fused_visual[:120]}
灵魂色彩: {fused_color[:80]}
场景描写: (具体物件 + {fused_visual[:80]} + 不写情绪形容词, 用动作呈现)
(动作 1): [具体动作, 不用"试图/缓缓/静静", 用{fused_visual[:60]}指导微动作]
人物 A: (对白, 8-15 字内, 语速由灵魂 voice 决定: {fused_voice[:60]})
人物 B: (对白)
(沉默 / 动作 / 物件特写 — 沉默比例由 soul.fatigue {s_fatigue:.2f} 决定)
场次 2: ...

════════════════════════════════════════
【7. 灵魂驱动 — 强制要求】
════════════════════════════════════════
1. 对白不超过 {_str(kwargs.get('对白最大字数', 15), '15')} 字
2. 90% 场景用具象动作(物件/数字/品牌/地址) — 不用情绪形容词
3. **每一场的微动作必须能体现主导情感 {fused_name}**:
   - 视觉: {fused_visual[:200]}
   - 声音: {fused_voice[:200]}
   - 内心: {fused_inner[:200]}
4. 静默场景 = 镜头不切 + 不说话 + 物件特写 (灵魂疲劳高 → 静默比例上调)
5. 时代/地点必须可考据
6. **全片色彩与音乐节奏服从 {fused_color} + {fused_music}**
7. **灯光服从 {lighting_tone}**

════════════════════════════════════════
【7.5 叙事逻辑自检清单 — 每场必过】
════════════════════════════════════════
- 因果链: A 发生 → 因此 → B 发生 (不能跳跃)
- 动机链: 人物 X 做 Y → 因为 Z (内心动机, 不能无缘无故)
- 反转/升级: 每一场必须有"前 30s 想不到"的小变化 (眼神/物件/对话断点)
- 因果词标注: 写完一段后, 必须出现 至少 1 个「因为/所以/但是/然而/于是/然后」连接词
- 情绪因果: 情绪不能凭空, 必须有触发事件 (看到什么/听到什么/想到什么)
- 时间连续: 上一场的状态必须延续到下场 (不能跳时间不交代)
- 空间一致: 上下场的空间必须逻辑可达 (不能凭空换房间)
- 物件因果: 关键物件 (笔/烟/信) 的状态必须前后呼应 (出现/变化/消失)
"""

        if _HAS_ANTI_AI:
            # 注入反 AI
            strength = _str(kwargs.get("反AI强度", "重 (词表+铁律+微调)"), "重 (词表+铁律+微调)")
            if strength != "关":
                user_prompt = inject_anti_ai_rules(user_prompt, director if director in DIRECTOR_ANTI_AI_PROMPTS else "")
            if "重" in strength and director in ALL_DIRECTORS:
                user_prompt += "\n\n" + build_micro_finetune_prompt(director, "剧本正文")

            # 额外禁用词
            extra_ban = _str(kwargs.get("额外禁用词", ""), "")
            if extra_ban:
                user_prompt += f"\n\n【额外禁用词(必须严格遵守)】\n{extra_ban}"

            # 多轮迭代链
            iter_chain = [
                ITERATION_TEMPLATES["round_1_draft"].format(
                    theme=architecture[:100] if architecture else fused_description[:100],
                    characters=f"主角: {_str(kwargs.get('主角身体习惯', ''), '')} 口头禅: {_str(kwargs.get('主角口头禅', ''), '')} 灵魂: {fused_name}",
                    structure=f"{_str(kwargs.get('场次数量', 20), '20')} 场次",
                    pacing=f"静默 {silence_ratio_input} (灵魂疲劳 {s_fatigue:.2f})",
                ),
                ITERATION_TEMPLATES["round_2_anti_ai"],
                ITERATION_TEMPLATES["round_3_humanize"],
                ITERATION_TEMPLATES["round_4_director_polish"].format(
                    director=director,
                    camera_style="按" + director + "的镜头习惯 + 灵魂 " + fused_name,
                    pacing_style=silence_ratio_input,
                    theme_focus=f"灵魂核心 = {fused_name} (强度 {fused_intensity:.2f})",
                    visual_signature=f"{fused_color[:80]} + {fused_visual[:80]}",
                ),
            ]
            iter_text = "\n\n=========\n\n".join(iter_chain)

            # 加上灵魂注入块到 iter_text
            iter_text += "\n\n=========\n\n" + soul_inj

            # 反 AI 清洗样本(如果开了样例)
            if _b(kwargs.get("生成样例小段", True), True):
                sample = "他陷入深深的沉思, 瞳孔地震, 心中暗道, 缓缓地站起身来, 看着她绝美的脸庞, 撕心裂肺地喊了一声。"
                cleaned = clean_anti_ai_text(sample)
                # 把灵魂色彩/视觉加入 sample
                cleaned += f"\n\n【灵魂驱动 — {fused_name} 重写版】\n他放下刀, 看一眼窗外. 窗台上的搪瓷缸还有半杯茶. 他拿起, 没喝, 放下."
            else:
                cleaned = ""
        else:
            iter_text = "反 AI 词表未加载"
            cleaned = ""

        return (user_prompt, cleaned, iter_text)


# ============================================================
# 类型防御 helper (boolean)
# ============================================================
def _b(v, default=False):
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return True
    if s in ("false", "0", "no", "off", ""):
        return False
    return default


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "ScriptBodyPro": ScriptBodyPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "ScriptBodyPro": "📜 剧本正文 (2/3)",
# }
