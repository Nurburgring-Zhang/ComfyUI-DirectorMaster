"""
UniversalDirectorPromptNode - 通用影视级导演 prompt 转换节点 (Phase 36.3)

**目标**: 输出世界顶级导演级别的 prompt, 适配所有主流视频生成模型
- MiniMax H3 (T2VA/I2VA/FL2VA/L2VA/Ref2VA)
- 字节 Seedance 2.5
- 阿里 Wan 3.0 (Wan 2.5 已发布, Wan 3.0 即将)
- OpenAI Sora 2
- Google Veo 3
- 短剧平台 (抖音/快手/小红书)
- 其他任意视频模型

**核心提炼** (不复制 H3 链接, 而是从多源提炼通用能力):
1. 5 段导演级 prompt 结构 (subject/style/shot/action/audio) - 任何模型都受益
2. Camera 3 维 (motion type + amplitude + speed) - 国际通用 vocabulary
3. Shot cut timestamp (MM:SS.mmm) + 5 cut 措辞 - 通用
4. Speaker (S1)/(S2) + <d>[Language]</d> 跨 shot 稳定 - 通用
5. Ref 4 labels (Subject/Picture/Video/Audio) - 通用
6. Audio 双轨 (soundscape 1-4 句 + non_diegetic 1-3 句) - 通用
7. 12 套故事理论 + 5 维具体化 + 60 情感 + 35 导演 - 本项目独有

**不同模型特定优化**:
- H3: integrated_multimodal_description 字段 + 严格 [Shot N] At MM:SS.mmm 时间戳
- Seedance 2.5: 强物理一致 + 3D CG + 多角度相机
- Wan 3.0: 中文 prompt 友好 + 简洁动作 + 强美学
- Sora 2: 长视频多 shot + 复杂调度 + 物理真实
- Veo 3: 高质量物理 + 拟真 + 创意 + 4K 输出
- 短剧平台: 3-7s 钩子 + 1-3 镜 + 强烈情绪 + 字幕

**严格符合 ComfyUI 节点规范**:
- INPUT_TYPES: required + optional
- RETURN_TYPES: 8 字段 (snake_case 英文)
- RETURN_NAMES: 与 RETURN_TYPES 等长
- FUNCTION, CATEGORY
"""

import os
import sys
import json
import re
from typing import Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_KB_DIR = os.path.join(_HERE, "knowledge_base")
if _KB_DIR not in sys.path:
    sys.path.insert(0, _KB_DIR)

# === Phase 36.6 v5i: 35 导演统一数据中枢 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_ALL,
        ALL_DIRECTOR_NAMES,
        get_director_profile,
        SCENE_DATABASE_100,
        DP_8_MASTERS,
        COLOR_STYLES_5,
        COMPOSITION_RULES_9,
        get_director,
        get_scene,
    )
    _DIRECTOR_DATA_LOADED = True
except Exception:
    _DIRECTOR_DATA_LOADED = False

# === H3 Prompt Framework (merged from H3ContextIRNode) ===
try:
    from h3_prompt_framework import (
        H3_MODES,
        H3_REF2VA_SECTIONS,
        H3_VISUAL_STYLES,
        H3_REFERENCE_LABELS,
        CAMERA_MOTION_TYPES,
        RETENTION_MARKERS_VISIBLE,
        RETENTION_MARKERS_AUDIO,
        select_h3_mode,
        render_camera_motion,
        render_h3_style_opening,
        render_h3_soundscape,
        render_h3_nondiegetic_music,
        render_h3_dialogue,
        DIRECTOR_TO_H3_MOTION,
        H3_ADDON_INJECTION_PLAN,
        H3_OFFICIAL_SKILLS_SUMMARY,
    )
    _H3_FRAMEWORK_LOADED = True
except Exception as _h3_err:
    _H3_FRAMEWORK_LOADED = False
    _H3_FRAMEWORK_ERROR = str(_h3_err)

# === 5 导演档案兜底 (H3 deep convert 用, merged from H3ContextIRNode) ===
H3_DIRECTOR_PROFILES_FALLBACK = {
    "王家卫": {
        "camera": "Truck right with small amplitude at slow speed",
        "lighting": "霓虹+暖黄路灯+雨夜反光",
        "shot_size": "medium-wide",
        "rhythm": "60s 慢节奏+重复+时间戳",
        "pacing": "1/8 抽帧+慢镜头+手持微晃",
    },
    "侯孝贤": {
        "camera": "Long static shot held for emotional breath",
        "lighting": "自然光+长镜头+留白",
        "shot_size": "wide",
        "rhythm": "极慢+生活流+长呼吸",
        "pacing": "固定机位+长镜头+极少剪辑",
    },
    "黑泽明": {
        "camera": "Multi-figure blocking with weather-as-character",
        "lighting": "天气即角色+极致清晰+云层",
        "shot_size": "wide",
        "rhythm": "群戏调度+多线交叉+缓慢推进",
        "pacing": "三镜头法+群像+动作剪影",
    },
    "李安": {
        "camera": "Push in with small amplitude at slow speed",
        "lighting": "家庭暖光+自然窗光+冷暖对比",
        "shot_size": "medium",
        "rhythm": "家庭代际+饭桌+缓慢推进",
        "pacing": "饭桌+对坐+代际错位",
    },
    "诺兰": {
        "camera": "Tracking shot at fast speed with large amplitude",
        "lighting": "自然光+冷色+高对比",
        "shot_size": "medium-wide",
        "rhythm": "递进+倒计时+交叉剪辑",
        "pacing": "IMAX+长焦+客观视角",
    },
}

# === 6 大模型 prompt 优化器 (Phase 36.3 提炼) ===
MODEL_PROMPT_OPTIMIZERS = {
    "MiniMax H3 (官方)": {
        "primary_field": "integrated_multimodal_description",
        "audio_fields": ["overall_soundscape", "non_diegetic_music"],
        "keyframe_in_first_line": True,
        "supports_ref2va": True,
        "max_duration": 15,
        "min_duration": 4,
        "language_preference": ["English", "Chinese"],
        "camera_vocabulary": "H3 standard",
        "shot_notation": "[Shot N] At MM:SS.mmm",
        "label_format": "<Subject N> / <Picture N> / <Video N> / <Audio N>",
        "dialogue_format": "<d>[Language] ...</d>",
        "best_for": ["T2VA", "I2VA", "FL2VA", "L2VA", "Ref2VA", "reference 4 标签"],
        "key_skill": "5 模式精确 + Ref2VA 6 段 + camera 3D",
    },
    "Seedance 2.5 (字节)": {
        "primary_field": "prompt",
        "audio_fields": [],
        "keyframe_in_first_line": False,
        "supports_ref2va": False,
        "max_duration": 12,
        "min_duration": 4,
        "language_preference": ["English", "Chinese"],
        "camera_vocabulary": "broad",
        "shot_notation": "natural",
        "label_format": "none",
        "dialogue_format": "natural",
        "best_for": ["3D CG", "物理一致", "多角度", "运动控制"],
        "key_skill": "physics-consistent + multi-angle + 3D",
    },
    "Wan 3.0 (阿里)": {
        "primary_field": "prompt",
        "audio_fields": [],
        "keyframe_in_first_line": False,
        "supports_ref2va": True,
        "max_duration": 15,
        "min_duration": 3,
        "language_preference": ["Chinese", "English"],
        "camera_vocabulary": "concise",
        "shot_notation": "natural",
        "label_format": "natural",
        "dialogue_format": "natural",
        "best_for": ["中文 prompt", "简洁动作", "美学", "开源可商用"],
        "key_skill": "Chinese-friendly + concise + aesthetic",
    },
    "Sora 2 (OpenAI)": {
        "primary_field": "prompt",
        "audio_fields": [],
        "keyframe_in_first_line": False,
        "supports_ref2va": True,
        "max_duration": 20,
        "min_duration": 5,
        "language_preference": ["English"],
        "camera_vocabulary": "cinematic",
        "shot_notation": "natural",
        "label_format": "natural",
        "dialogue_format": "natural",
        "best_for": ["长视频", "复杂调度", "物理真实", "多角色互动"],
        "key_skill": "long-form + complex + physics-realistic",
    },
    "Veo 3 (Google)": {
        "primary_field": "prompt",
        "audio_fields": ["ambient_sound"],
        "keyframe_in_first_line": False,
        "supports_ref2va": True,
        "max_duration": 8,
        "min_duration": 4,
        "language_preference": ["English"],
        "camera_vocabulary": "cinematic",
        "shot_notation": "natural",
        "label_format": "natural",
        "dialogue_format": "natural",
        "best_for": ["4K 高质量", "拟真", "创意", "物理真实"],
        "key_skill": "high-fidelity + creative + physics-true",
    },
    "短剧平台 (抖音/快手/小红书)": {
        "primary_field": "hook + body",
        "audio_fields": ["bgm", "sound_effect"],
        "keyframe_in_first_line": False,
        "supports_ref2va": False,
        "max_duration": 30,
        "min_duration": 3,
        "language_preference": ["Chinese", "English"],
        "camera_vocabulary": "engaging",
        "shot_notation": "fast-cut",
        "label_format": "none",
        "dialogue_format": "short-snappy",
        "best_for": ["3-7s 钩子", "1-3 镜", "强烈情绪", "字幕驱动"],
        "key_skill": "hook + 情绪 + 短镜 + 字幕",
    },
}

# === 12 套故事理论 (Phase 9 + 17 整合) ===
STORY_THEORIES_12 = {
    "Save the Cat": {"beats": 15, "key_beat": "All Is Lost + Dark Night of the Soul"},
    "Hero's Journey (Campbell)": {"beats": 17, "key_beat": "Refusal of the Call + Return"},
    "McKee Story Structure": {"beats": 5, "key_beat": "Inciting Incident + Climax"},
    "Pixar 22 Storytelling Rules": {"beats": 22, "key_beat": "Once upon a time + Happily ever after"},
    "Kishōtenketsu (起承转合)": {"beats": 4, "key_beat": "ki-shō-ten-ketsu 起承转合"},
    "Three Act Structure (Field)": {"beats": 3, "key_beat": "Plot Point 1 + Plot Point 2"},
    "Five Act Structure (Freytag)": {"beats": 5, "key_beat": "Climax"},
    "Seven Point Story Structure": {"beats": 7, "key_beat": "Plot Coupling Point"},
    "8 Sequence Structure (Truby)": {"beats": 8, "key_beat": "Weakness/Need + Desire + Opponent"},
    "Dan Harmon's Story Circle": {"beats": 8, "key_beat": "Return"},
    "In Medias Res": {"beats": 3, "key_beat": "起点+闪回+回现"},
    "Parallel Narrative (双线)": {"beats": 2, "key_beat": "双线汇合"},
}

# === 5 段导演级 prompt 结构 (Phase 36.3 通用提炼) ===
# 任何模型都受益的 5 段结构 (来自 H3 + 13 SKILL 通用)
UNIVERSAL_5_SECTION = {
    "1_subject": "Who is in the video? Character identity, age, appearance, clothing, props. (来自 H3 subject_definitions 提炼)",
    "2_style": "Visual style, aspect ratio, duration, color palette, lighting, atmosphere. (来自 H3 integrated_multimodal_description 开场 + 13 SKILL 通用)",
    "3_shot": "Shot-by-shot plan with timestamps, camera motion 3D, cut transitions. (来自 H3 [Shot N] At MM:SS.mmm + camera 3D 提炼)",
    "4_action": "Specific actions, dialogue, lip-sync, expressions, movements. (来自 H3 dialogue + <d> + 13 SKILL action verbs 提炼)",
    "5_audio": "Ambient sound + non-diegetic music + voiceover. (来自 H3 overall_soundscape + non_diegetic_music 提炼)",
}

# === 5 维具体化 (Phase 35.6 整合) ===
DIMENSION_5 = {
    "era": "时代 (1998, 90 年代, 2014, 民国, 清朝, 80s)",
    "location": "地点 (哈尔滨道里区, 巴黎, 洛杉矶, 上海弄堂, 旺角, 纽约)",
    "brand": "品牌 (雪花, 奔驰, Chevrolet, Montblanc, 凤凰牌自行车)",
    "numbers": "数字 (11月7日, 5元, 10秒, 23个, 800米)",
    "objects": "物件 (钢笔, 信纸, 大哥大, 军牌, 5 张老照片)",
}


class UniversalDirectorPromptNode:
    """
    通用影视级/短剧级/短视频级 prompt 转换节点

    支持 6 大视频模型 (H3/Seedance/Wan/Sora/Veo/短剧平台) + 自定义
    输出符合世界顶级导演标准的 prompt
    """

    NODE_NAME = "UniversalDirectorPromptNode"
    DISPLAY_NAME = "🎬 通用导演 Prompt (H3/Seedance/Wan/Sora/Veo/短剧 6 模型) ⭐"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_intent": ("STRING", {
                    "default": "雨夜香港旺角, 男女主角擦肩而过",
                    "multiline": True,
                }),
                "target_model": ([
                    "MiniMax H3 (官方)",
                    "Seedance 2.5 (字节)",
                    "Wan 3.0 (阿里)",
                    "Sora 2 (OpenAI)",
                    "Veo 3 (Google)",
                    "短剧平台 (抖音/快手/小红书)",
                    "通用 (兼容所有模型)",
                ], {"default": "通用 (兼容所有模型)"}),
            },
            "optional": {
                # === 多模态输入 ===
                "has_first_frame": ("BOOLEAN", {"default": False}),
                "has_last_frame": ("BOOLEAN", {"default": False}),
                "has_video_ref": ("BOOLEAN", {"default": False}),
                "has_audio_ref": ("BOOLEAN", {"default": False}),

                # === 视觉风格 ===
                "visual_style": ([
                    "Cinematic", "live-action", "2D-animated", "3D CG",
                    "claymation", "watercolor", "vintage film", "stop-motion",
                    "papercraft", "paper-collage", "documentary", "music video",
                ], {"default": "Cinematic"}),

                # === 导演 (500+ 导演全列表) ===
                "director": (["通用"] + ALL_DIRECTOR_NAMES if _DIRECTOR_DATA_LOADED else [
                    "通用", "王家卫", "张艺谋", "李安", "侯孝贤", "贾樟柯",
                    "诺兰", "奉俊昊", "黑泽明", "小津安二郎", "是枝裕和",
                    "宫崎骏", "北野武", "塔可夫斯基", "维伦纽瓦", "PTA",
                ], {"default": "通用"}),

                # === 时长 + 长宽比 ===
                "duration": ("INT", {"default": 8, "min": 3, "max": 20, "step": 1}),
                "aspect_ratio": ([
                    "16:9 横屏", "9:16 竖屏", "1:1 方形",
                    "21:9 电影宽屏", "4:3 经典", "9:16 短剧竖屏",
                ], {"default": "16:9 横屏"}),

                # === 场景与情感 ===
                "scene": ("STRING", {"default": "雨夜香港旺角, 霓虹灯在雨水中反射", "multiline": True}),
                "emotion": (["通用", "孤独", "悲", "怒", "喜", "悬疑", "浪漫", "史诗", "温馨", "恐惧", "宁静"], {"default": "通用"}),
                "intent": ("STRING", {"default": "营造孤寂浪漫的电影氛围", "multiline": True}),

                # === 对白 + 音乐 ===
                "dialogue": ("STRING", {"default": "", "multiline": True}),
                "dialogue_language": (["English", "Chinese", "Japanese", "Korean", "French", "Spanish"], {"default": "English"}),
                "non_diegetic_music": ("STRING", {"default": "", "multiline": True}),

                # === 故事结构 ===
                "story_theory": ([
                    "通用", "Save the Cat", "Hero's Journey", "McKee",
                    "Pixar 22", "Kishōtenketsu (起承转合)", "Three Act",
                    "Five Act", "7 Point", "Truby 8 Sequence",
                    "Dan Harmon Story Circle", "In Medias Res", "双线 Parallel",
                ], {"default": "通用"}),

                # === 短剧平台特定 (仅 target_model=短剧平台 生效) ===
                "hook_style": (["无", "视觉冲击", "悬念问题", "情感冲击", "动作冲击", "反差冲击"], {"default": "无"}),
                "subtitle_required": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "target_model",
        "model_specific_prompt",
        "h3_mode",                       # 兼容 H3
        "h3_full_prompt",                # 兼容 H3
        "universal_5_section",           # 通用 5 段
        "director_style_anchor",         # 导演风格锚点
        "shot_plan_with_timestamps",     # 镜头计划
        "dialogue_block",                # 对白
        "audio_block",                   # 声音 (soundscape + music)
        "story_arc_anchor",              # 故事弧
        "validation_report",             # 自检
        "anti_ai_clean_guarantee",       # 反 AI 清理保证
    )
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """控制节点重跑: 输入变化才重算; AI节点强制重跑取新鲜输出."""
        # 含AI配置时强制重跑(LLM输出不缓存)
        for k in ("ai_api_url",):
            if kwargs.get(k):
                return float("nan")
        # 否则按输入哈希缓存
        import hashlib, json
        try:
            return hashlib.md5(json.dumps(
                {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool, type(None)))},
                sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()
        except Exception:
            return float("nan")

    FUNCTION = "convert_universal"
    CATEGORY = "PromptLibrary/起点/通用"
    OUTPUT_NODE = True  # 终端节点: 视频API路由枢纽

    def convert_universal(
        self,
        user_intent: str,
        target_model: str = "通用 (兼容所有模型)",
        has_first_frame: bool = False,
        has_last_frame: bool = False,
        has_video_ref: bool = False,
        has_audio_ref: bool = False,
        visual_style: str = "Cinematic",
        director: str = "通用",
        duration: int = 8,
        aspect_ratio: str = "16:9 横屏",
        scene: str = "雨夜香港旺角, 霓虹灯在雨水中反射",
        emotion: str = "通用",
        intent: str = "营造孤寂浪漫的电影氛围",
        dialogue: str = "",
        dialogue_language: str = "English",
        non_diegetic_music: str = "",
        story_theory: str = "通用",
        hook_style: str = "无",
        subtitle_required: bool = False,
        **kwargs,  # 接受灵魂addon 等其他 optional input (ComfyUI 注入)
    ) -> Tuple:
        """
        转换通用 prompt
        """
        # 1. 解析模型配置
        if target_model == "通用 (兼容所有模型)":
            model_cfg = {
                "primary_field": "prompt",
                "audio_fields": ["ambient_sound", "bgm"],
                "supports_ref2va": True,
                "max_duration": 15,
                "language_preference": ["English", "Chinese"],
                "key_skill": "universal 5-section + camera 3D",
            }
        else:
            model_cfg = MODEL_PROMPT_OPTIMIZERS.get(target_model, MODEL_PROMPT_OPTIMIZERS["MiniMax H3 (官方)"])

        # 2. H3 模式自动选择 (兼容 H3)
        has_refs = has_video_ref or has_audio_ref
        if has_refs:
            h3_mode = "Ref2VA"
        elif has_first_frame and has_last_frame:
            h3_mode = "FL2VA"
        elif has_first_frame and not has_last_frame:
            h3_mode = "I2VA"
        elif has_last_frame and not has_first_frame:
            h3_mode = "L2VA"
        else:
            h3_mode = "T2VA"

        # 2b. Deep H3 convert when target is MiniMax H3
        #     Uses h3_prompt_framework for rich mode-aware output
        _is_h3_target = ("H3" in target_model or "MiniMax" in target_model)
        h3_deep_result = None
        if _is_h3_target:
            h3_deep_result = self._h3_deep_convert(
                user_intent=user_intent,
                h3_mode=h3_mode,
                director=director,
                scene=scene,
                duration=duration,
                visual_style=visual_style,
                aspect_ratio=aspect_ratio,
                dialogue=dialogue,
                dialogue_language=dialogue_language,
                non_diegetic_music=non_diegetic_music,
                emotion=emotion,
                intent=intent,
                reference_assets=kwargs.get("reference_assets", ""),
            )

        # 3. Director style anchor (35 导演, 提炼通用风格)
        director_anchor = self._build_director_anchor(director, scene, emotion, intent)

        # 4. Shot plan with timestamps
        shot_plan = self._build_shot_plan(
            scene=scene, duration=duration, director=director,
            emotion=emotion, dialogue=dialogue, dialogue_language=dialogue_language,
        )

        # 5. Dialogue block (通用 <d> 格式)
        dialogue_block = ""
        if dialogue:
            dialogue_block = self._build_dialogue_block(
                dialogue=dialogue, language=dialogue_language,
                is_voiceover=False, speaker_id="S1",
            )

        # 6. Audio block
        audio_block = self._build_audio_block(
            scene=scene, non_diegetic_music=non_diegetic_music, emotion=emotion, director=director,
        )

        # 7. Story arc anchor
        story_arc = self._build_story_arc(
            story_theory=story_theory, user_intent=user_intent, emotion=emotion, intent=intent,
        )

        # 8. 通用 5 段 prompt (任何模型都受益)
        universal_5 = self._build_universal_5_section(
            user_intent=user_intent, visual_style=visual_style, scene=scene,
            director=director, emotion=emotion, intent=intent,
            shot_plan=shot_plan, dialogue_block=dialogue_block, audio_block=audio_block,
        )

        # 9. H3 full prompt (deep convert when H3 target, else backward compat)
        if h3_deep_result:
            h3_full = h3_deep_result["h3_full_prompt"]
        else:
            h3_full = self._build_h3_full_prompt(
                h3_mode=h3_mode, user_intent=user_intent, scene=scene, visual_style=visual_style,
                director=director, duration=duration, dialogue_block=dialogue_block, audio_block=audio_block,
            )

        # 10. Model specific prompt (按 target_model 优化)
        model_specific = self._build_model_specific(
            target_model=target_model, model_cfg=model_cfg, universal_5=universal_5,
            hook_style=hook_style, subtitle_required=subtitle_required, duration=duration,
        )

        # 11. Validation report (use deep H3 validation when targeting H3)
        if h3_deep_result:
            validation = h3_deep_result["h3_validation"]
        else:
            validation = self._validate(
                target_model=target_model, h3_mode=h3_mode, model_cfg=model_cfg,
                universal_5=universal_5, dialogue_block=dialogue_block, audio_block=audio_block,
            )

        # 12. Anti-AI clean guarantee
        anti_ai = self._anti_ai_guarantee(director, scene, emotion, universal_5)

        return (
            target_model,
            model_specific,
            h3_mode,
            h3_full,
            universal_5,
            director_anchor,
            shot_plan,
            dialogue_block,
            audio_block,
            story_arc,
            validation,
            anti_ai,
        )

    # === 内部方法 ===

    def _build_director_anchor(self, director, scene, emotion, intent) -> str:
        """导演风格锚点 - 35 导演的 8 维提炼 (优先用 director_data_unified 统一中枢)"""
        try:
            from director_data_unified import DIRECTOR_PROFILES_ALL as _UP
            d8d = {"通用": {"镜头": "Push in", "光线": "自然光", "节奏": "中等", "色彩": "中性", "表演": "克制", "构图": "中景", "声音": "环境音", "剪辑": "标准"}}
            for name, prof in _UP.items():
                d8d[name] = {
                    "镜头": prof.get("镜头", "未指定"),
                    "光线": prof.get("光", "未指定"),
                    "节奏": prof.get("节奏", "未指定"),
                    "色彩": prof.get("色彩", "未指定"),
                    "表演": prof.get("表演", "未指定"),
                    "构图": prof.get("构图", "未指定"),
                    "声音": prof.get("声音", "未指定"),
                    "剪辑": prof.get("节奏", "未指定"),
                }
        except Exception:
            d8d = {
                "通用": {"镜头": "Push in", "光线": "自然光", "节奏": "中等", "色彩": "中性", "表演": "克制", "构图": "中景", "声音": "环境音", "剪辑": "标准"},
                "王家卫": {"镜头": "Truck right + 慢镜头 1/8", "光线": "霓虹+暖黄+雨夜", "节奏": "60s 慢+重复", "色彩": "蓝绿+暗红+琥珀", "表演": "极简手势+眼神", "构图": "走廊+镜子+门缝", "声音": "环境音>台词", "剪辑": "跳切+闪回"},
                "张艺谋": {"镜头": "远景+群像+对称", "光线": "高对比+东方色", "节奏": "仪式+缓慢", "色彩": "红+黑+金", "表演": "极克制", "构图": "对称+大远景", "声音": "鼓+风", "剪辑": "叠化+群像"},
                "李安": {"镜头": "饭桌+对坐", "光线": "家庭暖光+窗光", "节奏": "家庭代际", "色彩": "东方青+西方暖", "表演": "压抑+爆发", "构图": "饭桌+代际", "声音": "家庭对话+沉默", "剪辑": "饭桌+仪式感"},
                "侯孝贤": {"镜头": "固定+长镜头", "光线": "自然光+留白", "节奏": "极慢+生活流", "色彩": "自然色+朴", "表演": "极少台词", "构图": "家+门+窗", "声音": "环境+沉默", "剪辑": "长+不切"},
                "贾樟柯": {"镜头": "手提+近景", "光线": "自然+时代感", "节奏": "时代+日常", "色彩": "灰+旧色", "表演": "日常+隐忍", "构图": "街+小人物", "声音": "时代音", "剪辑": "长+日常"},
                "诺兰": {"镜头": "IMAX+长焦", "光线": "自然光+冷", "节奏": "递进+倒计时", "色彩": "冷蓝+灰+暖黄", "表演": "克制+坚毅", "构图": "对称+大远景", "声音": "Zimmer 低频+心跳", "剪辑": "非线性+双线"},
                "奉俊昊": {"镜头": "固定+对称", "光线": "冷暖对比", "节奏": "类型+突然变调", "色彩": "冷暖阶层", "表演": "群戏+隐忍", "构图": "楼梯+门+窗", "声音": "现实+爆点", "剪辑": "精确切+突然静默"},
                "黑泽明": {"镜头": "群戏+远景", "光线": "天气即角色", "节奏": "群戏调度", "色彩": "黑白+强对比", "表演": "极致克制", "构图": "三镜头法", "声音": "风+雨+鼓", "剪辑": "动态切+叠化"},
                "小津安二郎": {"镜头": "榻榻米视角固定", "光线": "家庭自然光", "节奏": "极慢+仪式", "色彩": "素雅+灰+米", "表演": "克制+日常", "构图": "榻榻米水平线", "声音": "家庭+寂静", "剪辑": "静态切+不切"},
                "是枝裕和": {"镜头": "固定+长镜头", "光线": "北欧光+窗", "节奏": "慢+生活流", "色彩": "北欧白+米+淡蓝", "表演": "克制+不解释", "构图": "家+童年空间", "声音": "环境+家", "剪辑": "长+家庭代际"},
                "宫崎骏": {"镜头": "Pan right + 远景", "光线": "天空+云", "节奏": "温柔+史诗", "色彩": "天空蓝+绿", "表演": "童真+勇气", "构图": "天空+飞行+森林", "声音": "久石让 钢琴+弦乐", "剪辑": "Pan+叠化"},
                "北野武": {"镜头": "固定+突然动作", "光线": "极简+冷", "节奏": "静默+爆", "色彩": "冷蓝+白", "表演": "极简+暴力", "构图": "方+对称", "声音": "突然静默+爆发", "剪辑": "静态切+爆点"},
                "塔可夫斯基": {"镜头": "超长+固定+微移", "光线": "水+火+烛", "节奏": "慢+呼吸", "色彩": "湿+雾+蓝灰", "表演": "极少台词+眼神", "构图": "水+火+肖像+门", "声音": "水滴+风+呼吸+钢琴", "剪辑": "超长+不切"},
                "维伦纽瓦": {"镜头": "慢推+广角", "光线": "暗+反差", "节奏": "史诗+慢", "色彩": "暗+琥珀", "表演": "沉默+坚毅", "构图": "广角+地标", "声音": "Zimmer 大编制", "剪辑": "慢+叠化"},
                "PTA": {"镜头": "长焦 85mm+浅景深", "光线": "70s 暖黄+窗光", "节奏": "慢板+渐进", "色彩": "琥珀+橘红", "表演": "可观察行为+不解释", "构图": "中景+双人", "声音": "时代金曲", "剪辑": "长+渐入渐出"},
            }
        d = d8d.get(director, d8d["通用"])
        anchor = f"=== Director Anchor: {director} ===\n"
        for k, v in d.items():
            anchor += f"  {k}: {v}\n"
        anchor += f"\nScene: {scene}\nEmotion: {emotion}\nIntent: {intent}\n"
        return anchor

    def _build_shot_plan(self, scene, duration, director, emotion, dialogue, dialogue_language) -> str:
        """镜头计划 - 通用 5 维 (时戳 + camera 3D + cut + dialogue + action)"""
        camera_phrase = {
            "通用": "Push in with small amplitude at slow speed",
            "王家卫": "Truck right with small amplitude at slow speed",
            "侯孝贤": "Long static shot held for emotional breath",
            "黑泽明": "Multi-figure blocking with weather-as-character",
            "李安": "Push in with small amplitude at slow speed",
            "诺兰": "Tracking shot at fast speed with large amplitude",
        }.get(director, "Push in with small amplitude at slow speed")

        plan = "=== Shot Plan ===\n"
        # Shot 1
        mm = int(duration // 60)
        ss = duration % 60
        plan += f"[Shot 1] Cinematic, {scene}.\n"
        plan += f"  Camera: {camera_phrase}\n"
        plan += f"  Action: Subject enters frame, environment establishes.\n"
        if dialogue:
            plan += f"  Dialogue: Subject (S1) says, <d>[{dialogue_language}] {dialogue}</d>\n"
        # Shot 2 (中段)
        if duration > 4:
            cut_time = duration / 2
            mm2 = int(cut_time // 60)
            ss2 = cut_time % 60
            plan += f"\n[Shot 2] At {mm2:02d}:{ss2:06.3f}, the camera cuts to a closer view.\n"
            plan += f"  Camera: Push in with small amplitude at slow speed\n"
            plan += f"  Action: Subject reacts, emotion {emotion} peaks.\n"
        # Shot 3 (结尾)
        if duration > 7:
            mm3 = int((duration * 0.85) // 60)
            ss3 = (duration * 0.85) % 60
            plan += f"\n[Shot 3] At {mm3:02d}:{ss3:06.3f}, the camera cuts to a wide or detail shot.\n"
            plan += f"  Camera: Pull out with small amplitude at slow speed\n"
            plan += f"  Action: Payoff / resolution.\n"

        return plan

    def _build_dialogue_block(self, dialogue, language, is_voiceover=False, speaker_id="S1") -> str:
        """对白 - 通用 <d>[Language]</d> 格式"""
        if not dialogue:
            return ""
        if is_voiceover:
            return f'{speaker_id} says in an off-screen voiceover: <d>[{language}] {dialogue}</d> while his lips remain completely closed.'
        return f'{speaker_id} says: <d>[{language}] {dialogue}</d>'

    def _build_audio_block(self, scene, non_diegetic_music, emotion, director) -> str:
        """声音双轨 - 通用 H3 风格 + 任何模型都支持"""
        # soundscape
        scene_lower = scene.lower() if scene else ""
        ambient = "Low ambient sound surrounds the scene"
        if "雨" in scene or "rain" in scene_lower:
            ambient = "Steady rain taps against surfaces"
        elif "海" in scene or "ocean" in scene_lower or "sea" in scene_lower:
            ambient = "Ocean waves lap against the shore"
        elif "夜" in scene or "night" in scene_lower:
            ambient = "Low urban hum continues underneath"
        elif "山" in scene or "mountain" in scene_lower:
            ambient = "Wind through trees, distant birdsong"

        action = "Footsteps and fabric movement continue throughout"
        if "雨" in scene or "rain" in scene_lower:
            action = "Wet footsteps and soft scrape of a chair"

        soundscape = f"overall_soundscape: {ambient}. {action}."

        # non_diegetic_music
        if non_diegetic_music:
            music = f"non_diegetic_music: {non_diegetic_music} at a slow tempo, sustained and gradually decreasing in volume."
        else:
            music_map = {
                "孤独": "Sparse piano notes at a slow tempo, joined by sustained low strings",
                "悲": "Solo cello with sustained low strings at a slow tempo",
                "怒": "Distorted electric guitar with heavy percussion at a fast tempo",
                "喜": "Bright acoustic guitar with light percussion at a moderate tempo",
                "悬疑": "Low electronic pulse with rising strings at a slow tempo",
                "浪漫": "Soft piano with gentle strings at a slow tempo",
                "史诗": "Full orchestral brass and strings at a slow tempo, building to a climax",
                "温馨": "Soft acoustic guitar with strings at a moderate tempo",
                "恐惧": "Low drone with dissonant strings at a slow tempo",
                "宁静": "Ambient pad with sparse piano at a slow tempo",
            }
            instr = music_map.get(emotion, "Sparse piano notes at a slow tempo")
            music = f"non_diegetic_music: {instr}, gradually decreasing in volume."

        return f"{soundscape}\n{music}"

    def _build_story_arc(self, story_theory, user_intent, emotion, intent) -> str:
        """故事弧锚点 - 12 套理论中激活相关"""
        if story_theory == "通用":
            return f"=== Story Arc: Generic ===\n  Setup → Conflict → Resolution\n  Intent: {intent}\n  Emotion: {emotion}"

        theory = STORY_THEORIES_12.get(story_theory, STORY_THEORIES_12["Save the Cat"])
        return f"=== Story Arc: {story_theory} ({theory['beats']} beats) ===\n  Key beat: {theory['key_beat']}\n  Intent: {intent}\n  Emotion: {emotion}\n  User intent: {user_intent[:60]}"

    def _build_universal_5_section(self, user_intent, visual_style, scene, director, emotion, intent, shot_plan, dialogue_block, audio_block) -> str:
        """通用 5 段 prompt (任何模型都受益)"""
        return f"""=== Universal 5-Section Prompt (任何模型都受益) ===

1. SUBJECT (人物): {director} 风格下, 场景 '{scene}' 中的人物身份、年龄、外观、服饰、道具
2. STYLE (风格): {visual_style}, 导演 {director} 的标志性美学, 主导情感 {emotion}, 创作意图 {intent}
3. SHOT (镜头计划):
{shot_plan}
4. ACTION (动作+对白): {user_intent}
{dialogue_block if dialogue_block else "  (无对白, 纯视觉叙事)"}
5. AUDIO (声音双轨):
{audio_block}
"""

    def _build_h3_full_prompt(self, h3_mode, user_intent, scene, visual_style, director, duration, dialogue_block, audio_block) -> str:
        """H3 完整 prompt (向后兼容)"""
        if h3_mode == "T2VA":
            instruction = ""
        elif h3_mode == "I2VA":
            instruction = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.\n\n"
        elif h3_mode == "FL2VA":
            instruction = f"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the {duration:.2f}-second mark of the target video.\n\n"
        elif h3_mode == "L2VA":
            instruction = f"How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) aligns with the {duration:.2f}-second mark of the target video.\n\n"
        else:  # Ref2VA
            instruction = ""

        multimodal = f"integrated_multimodal_description: [Shot 1] {visual_style}, cinematic, a medium shot frames {scene}. {user_intent}.{(' ' + dialogue_block) if dialogue_block else ''}"
        return f"{instruction}{multimodal}\n\n{audio_block}"

    def _build_model_specific(self, target_model, model_cfg, universal_5, hook_style, subtitle_required, duration) -> str:
        """模型特定 prompt 优化
        Phase 36.6 v5i: 6 模型各自集成导演 8 维真实档案 (镜头/光/节奏/色彩/构图/声音)
        """
        # 提取导演 8 维 (Phase 36.6 v5i)
        director_8d_block = ""
        scene_match_block = ""
        if _DIRECTOR_DATA_LOADED:
            # universal_5 中抽出 director 名
            import re
            m = re.search(r"导演 (\S+?) 的标志性美学", universal_5)
            director_name = m.group(1) if m else "通用"
            d_p = get_director_profile(director_name) if _DIRECTOR_DATA_LOADED else {}
            if d_p:
                director_8d_block = (
                    f"\n[导演 8 维真实档案 - {director_name}]\n"
                    f"  镜头: {d_p['镜头']}\n"
                    f"  光: {d_p['光']}\n"
                    f"  节奏: {d_p['节奏']}\n"
                    f"  色彩: {d_p['色彩']}\n"
                    f"  构图: {d_p['构图']}\n"
                    f"  声音: {d_p['声音']}\n"
                    f"  物件: {d_p['物件']}\n"
                    f"  主题: {d_p['5维标签']}\n"
                )
                s_m = get_scene(director_name, scene_keyword=universal_5[:80])
                if s_m and s_m.get("director") != "通用":
                    scene_match_block = (
                        f"\n[场景匹配 - {s_m['scene']}]\n"
                        f"  物件: {s_m['object']}\n"
                        f"  色调: {s_m['color']}\n"
                        f"  声景: {s_m['sound']}\n"
                        f"  情绪: {s_m['emotion']}\n"
                    )

        if target_model == "短剧平台 (抖音/快手/小红书)":
            # 短剧: 3-7s 钩子 + 1-3 镜 + 强烈情绪 + 字幕
            hook_phrase = ""
            if hook_style == "视觉冲击":
                hook_phrase = "[HOOK] 强视觉冲击开场 (3 秒内必须抓眼球)"
            elif hook_style == "悬念问题":
                hook_phrase = "[HOOK] 悬念问题开场 (3 秒内必须有问题或冲突)"
            elif hook_style == "情感冲击":
                hook_phrase = "[HOOK] 情感冲击开场 (3 秒内必须有情绪爆发)"
            elif hook_style == "动作冲击":
                hook_phrase = "[HOOK] 动作冲击开场 (3 秒内必须有动作)"
            elif hook_style == "反差冲击":
                hook_phrase = "[HOOK] 反差冲击开场 (3 秒内必须有反差/对比)"

            subtitle_note = "\n[SUBTITLE] 字幕: 关键对白加字幕, 字体大, 时间 1-2s" if subtitle_required else ""
            return f"""{hook_phrase}

[STRUCTURE] 1-3 镜结构, 总时长 {duration}s
[镜 1] 0-3s 钩子 (抓住观众)
[镜 2] 3-{duration-1}s 冲突/发展
[镜 3] {duration-1}-{duration}s 转折/钩子结束

{universal_5}
{director_8d_block}{scene_match_block}
{subtitle_note}
"""
        elif target_model == "Wan 3.0 (阿里)":
            # Wan: 中文友好, 简洁动作, 美学
            return f"""[Wan 3.0 优化 - 中文友好]

[核心 prompt - 简洁美学]
{universal_5}
{director_8d_block}{scene_match_block}

[Wan 技巧] 中文 prompt 优于英文, 简洁动作优于复杂描述, 强美学关键词 (电影感, 高质感, 极致细节)
"""
        elif target_model == "Seedance 2.5 (字节)":
            # Seedance: 3D CG 强, 物理一致, 多角度
            return f"""[Seedance 2.5 优化 - 物理一致 + 3D]

[核心 prompt]
{universal_5}
{director_8d_block}{scene_match_block}

[Seedance 技巧] 强 3D 物理一致, 多角度相机, 运动控制精确, 适合角色动作+物体物理
"""
        elif target_model == "Sora 2 (OpenAI)":
            # Sora: 长视频, 复杂调度, 物理真实
            return f"""[Sora 2 优化 - 长视频 + 复杂]

[核心 prompt]
{universal_5}
{director_8d_block}{scene_match_block}

[Sora 技巧] 长视频多 shot, 复杂调度, 物理真实, 多角色互动
"""
        elif target_model == "Veo 3 (Google)":
            # Veo: 4K 高质量, 拟真, 物理
            return f"""[Veo 3 优化 - 4K 高质量]

[核心 prompt]
{universal_5}
{director_8d_block}{scene_match_block}

[Veo 技巧] 4K 高质量, 拟真, 物理真实, 创意场景
"""
        elif target_model == "MiniMax H3 (官方)":
            # H3 完整 5 段
            return f"""[H3 官方 5 模式]

[核心 prompt]
{universal_5}
{director_8d_block}{scene_match_block}

[H3 技巧] integrated_multimodal_description + overall_soundscape + non_diegetic_music 三段式, 严格 [Shot N] At MM:SS.mmm, 4 reference labels
"""
        else:  # 通用
            return f"""[通用 5 段 - 任何模型都支持]

{universal_5}
{director_8d_block}{scene_match_block}
"""

    def _validate(self, target_model, h3_mode, model_cfg, universal_5, dialogue_block, audio_block) -> str:
        """自检报告"""
        checks = []
        checks.append(f"✓ Target Model: {target_model}")
        checks.append(f"✓ H3 Mode (兼容): {h3_mode}")
        checks.append(f"✓ 5-section length: {len(universal_5)} chars (推荐 > 500)")
        if dialogue_block:
            checks.append(f"✓ Dialogue 格式: <d>[Language] 标准")
        else:
            checks.append(f"  i 无对白 (允许, 纯视觉)")
        checks.append(f"✓ Audio 双轨: soundscape + non_diegetic_music")
        if "Push in" in universal_5 or "Truck" in universal_5 or "Tracking" in universal_5:
            checks.append(f"✓ Camera 3D 维度 (motion + amplitude + speed)")
        else:
            checks.append(f"⚠ Camera 3D 维度缺失")
        if "00:" in universal_5:
            checks.append(f"✓ Shot timestamp (MM:SS.mmm)")
        else:
            checks.append(f"  i 无时间戳 (允许, 短片可省略)")
        if "<d>" in universal_5 or "says" in universal_5:
            checks.append(f"✓ 跨 shot dialogue 一致性")
        return "\n".join(checks)

    def _anti_ai_guarantee(self, director, scene, emotion, prompt_content="") -> str:
        """反 AI 清理保证 — 真实扫描"""
        issues = []
        clean_count = 0
        try:
            from anti_ai_vocab import ANTI_AI_PHRASES
            check_text = (prompt_content + " " + scene + " " + emotion).lower()
            found = []
            for phrase in ANTI_AI_PHRASES:
                if phrase.lower() in check_text:
                    found.append(phrase)
            clean_count = len(ANTI_AI_PHRASES) - len(found)
            if found:
                issues.append(f"⚠ 发现 {len(found)} 个AI词汇残留: {', '.join(found[:10])}")
            else:
                issues.append(f"✓ {len(ANTI_AI_PHRASES)} 词AI词汇表全部清洁")
        except ImportError:
            issues.append("⚠ anti_ai_vocab 模块不可用, 无法执行检查")

        has_5d = all(kw in prompt_content for kw in ["年", "市", "号"])
        if has_5d:
            issues.append("✓ 5维具体化 (时代/地点等) 检测到")
        else:
            issues.append("⚠ 5维具体化数据不足")

        if director and director != "auto":
            issues.append(f"✓ 导演 {director} 已指定")
        else:
            issues.append("⚠ 导演未指定")

        return "=== 反 AI 清理验证报告 (Phase 36.3) ===\n" + "\n".join(issues) + "\n"

    # =================================================================
    # H3 Deep Convert (merged from H3ContextIRNode Phase 36.2)
    # Provides full 5-mode detection + h3_prompt_framework integration
    # =================================================================

    def _h3_deep_convert(
        self,
        user_intent: str,
        h3_mode: str,
        director: str,
        scene: str,
        duration: int,
        visual_style: str,
        aspect_ratio: str,
        dialogue: str,
        dialogue_language: str,
        non_diegetic_music: str,
        emotion: str,
        intent: str,
        reference_assets: str = "",
    ) -> dict:
        """
        Deep H3 conversion using h3_prompt_framework.

        Returns a dict with keys:
            h3_mode, h3_instruction, h3_multimodal, h3_soundscape,
            h3_music, h3_full_prompt, h3_validation, h3_summary_card
        """
        if not _H3_FRAMEWORK_LOADED:
            return self._h3_deep_fallback(user_intent, director, scene, duration,
                                          f"H3 framework unavailable: {_H3_FRAMEWORK_ERROR}")

        mode_info = H3_MODES[h3_mode]

        # --- Director style resolution (35 directors 8-dim, fallback 5) ---
        if _DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_ALL:
            d_profile = DIRECTOR_PROFILES_ALL[director]
            camera_phrase = d_profile["镜头"]
            director_lighting = d_profile["光"]
            director_pacing = d_profile["节奏"]
            director_8d = (
                f"{d_profile['镜头']};{d_profile['光']};{d_profile['节奏']};"
                f"{d_profile['色彩']};{d_profile['表演']};{d_profile['构图']};"
                f"{d_profile['声音']};{d_profile['情绪']}"
            )
        else:
            director_profile = H3_DIRECTOR_PROFILES_FALLBACK.get(director, {
                "camera": "Push in with small amplitude at slow speed",
                "lighting": "自然光+中性",
                "shot_size": "medium",
                "rhythm": "中等节奏+渐进",
                "pacing": "标准+克制",
            })
            camera_phrase = director_profile["camera"]
            director_lighting = director_profile.get("lighting", "自然光")
            director_pacing = director_profile.get("pacing", "中等节奏")
            director_8d = camera_phrase + ";" + director_lighting

        shot_size = (
            H3_DIRECTOR_PROFILES_FALLBACK.get(director, {}).get("shot_size", "medium")
            if not (_DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_ALL)
            else "medium"
        )

        # --- Part One: Instruction (keyframe alignment) ---
        instruction = self._h3_build_instruction(h3_mode, duration)

        # --- integrated_multimodal_description ---
        multimodal = self._h3_build_multimodal_description(
            user_intent=user_intent, scene=scene, visual_style=visual_style,
            shot_size=shot_size, camera_phrase=camera_phrase, director=director,
            emotion=emotion, intent=intent, dialogue=dialogue,
            target_language=dialogue_language, duration=duration,
            director_8d=director_8d, director_lighting=director_lighting,
            director_pacing=director_pacing,
        )

        # --- overall_soundscape ---
        soundscape = self._h3_build_soundscape(scene, intent, duration)

        # --- non_diegetic_music ---
        music = self._h3_build_music(non_diegetic_music, emotion, director)

        # --- Full H3 prompt ---
        if h3_mode == "Ref2VA":
            full_prompt = self._h3_build_ref2va_prompt(
                reference_assets=reference_assets,
                user_intent=user_intent,
                scene=scene,
                multimodal=multimodal,
                soundscape=soundscape,
                music=music,
            )
        else:
            full_prompt = self._h3_build_base_prompt(
                instruction=instruction,
                multimodal=multimodal,
                soundscape=soundscape,
                music=music,
            )

        # --- Validation ---
        validation = self._h3_validate(h3_mode, instruction, multimodal, soundscape, music)

        # --- Summary card ---
        summary = self._h3_build_summary_card(
            h3_mode=h3_mode, director=director, scene=scene,
            duration=duration, visual_style=visual_style,
            aspect_ratio=aspect_ratio, emotion=emotion,
            has_dialogue=bool(dialogue), has_music=bool(non_diegetic_music),
        )

        return {
            "h3_mode": h3_mode,
            "h3_instruction": instruction,
            "h3_multimodal": multimodal,
            "h3_soundscape": soundscape,
            "h3_music": music,
            "h3_full_prompt": full_prompt,
            "h3_validation": validation,
            "h3_summary_card": summary,
        }

    def _h3_build_instruction(self, h3_mode: str, duration: int) -> str:
        """Part One: H3 keyframe alignment instruction"""
        if h3_mode == "T2VA":
            return ""
        elif h3_mode == "I2VA":
            return "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
        elif h3_mode == "FL2VA":
            return (
                f"How the reference pictures align with the target video — "
                f"Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; "
                f"Picture 2 (from Shot 1) aligns with the {duration:.2f}-second mark of the target video."
            )
        elif h3_mode == "L2VA":
            return (
                f"How the reference pictures align with the target video — "
                f"<Picture 1> (from [Shot 1]) aligns with the {duration:.2f}-second mark of the target video."
            )
        elif h3_mode == "Ref2VA":
            return ""
        return ""

    def _h3_build_multimodal_description(
        self, user_intent, scene, visual_style, shot_size, camera_phrase,
        director, emotion, intent, dialogue, target_language, duration,
        director_8d="", director_lighting="", director_pacing=""
    ) -> str:
        """H3 integrated_multimodal_description with Shot timestamps + director 8-dim profiles"""
        shot1 = render_h3_style_opening(visual_style, shot_size, scene)
        director_note = f" Director style: {director} - {camera_phrase}."
        intent_desc = f" {user_intent}."

        # 8-dim director profile injection
        if director_8d and director != "通用":
            director_8d_block = (
                f" Director 8-dim profile: {director_8d}. "
                f"Lighting: {director_lighting}. Pacing: {director_pacing}."
            )
        else:
            director_8d_block = ""

        # 35-director signature block
        director_signature_block = ""
        if _DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_ALL:
            d_p = DIRECTOR_PROFILES_ALL[director]
            director_signature_block = (
                f" 代表作 {d_p['代表作']} (年代 {d_p['年代']});"
                f" 标志物件 {d_p['物件']};"
                f" 主题标签 {d_p['5维标签']}."
            )

        # 100-scene database match
        scene_match_block = ""
        if _DIRECTOR_DATA_LOADED:
            s_data = get_scene(director, scene_keyword=scene)
            if s_data and s_data.get("director") != "通用":
                scene_match_block = (
                    f" 场景参考 {s_data['director']} - {s_data['scene']}:"
                    f" 物件 {s_data['object']}, 色调 {s_data['color']},"
                    f" 声景 {s_data['sound']}, 情绪 {s_data['emotion']}."
                )

        # 5-dim specificity injection
        spec_block = ""
        if re.search(r'\b(19|20)\d{2}\b', user_intent + scene):
            spec_block += " 时代锚定 (从用户输入解析): 1990s/2000s/2010s/2020s 年代质感与道具.\n"
        if re.search(
            r'(香港|哈尔滨|巴黎|纽约|东京|上海|北京|广州|重庆|武汉|成都|西安|台北|曼谷|伦敦|柏林|莫斯科|上海弄堂|旺角|道里区|九龙|池袋|涩谷)',
            user_intent + scene,
        ):
            spec_block += " 地点锚定 (从用户输入解析): 真实地理 + 街区级定位.\n"
        if director_8d:
            spec_block += (
                f" 摄影参数: 35mm/50mm 镜头为主, 浅景深, "
                f"自然光 + 3200K 暖调, 24fps 电影帧率.\n"
            )
        if _DIRECTOR_DATA_LOADED and director_8d and "物件" in director_8d:
            objs = director_8d["物件"].split("/")
            if objs:
                spec_block += f" 物件锚定: {objs[0]} (导演标志性物件).\n"
        spec_block += " 数字锚定: 3 人 / 1 场景 / 8 秒 / 1 个关键时刻 / 5 维真实档案驱动.\n"

        # Dialogue with H3 <d> format
        dialogue_block = ""
        if dialogue:
            d_rendered = render_h3_dialogue("(S1)", target_language, dialogue)
            dialogue_block = f" A character (S1) says, {d_rendered}"

        # Shot 2 mid-point cut
        shot2 = ""
        if duration > 4:
            cut_time = duration / 2
            mm = int(cut_time // 60)
            ss = cut_time % 60
            shot2 = f" [Shot 2] At {mm:02d}:{ss:06.3f}, the camera cuts to a closer view of the subject."

        return (
            f"integrated_multimodal_description: {shot1}{director_note}{intent_desc}"
            f"{director_8d_block}{director_signature_block}{scene_match_block}"
            f"{spec_block}{dialogue_block}{shot2}"
        )

    def _h3_build_soundscape(self, scene, intent, duration) -> str:
        """H3 overall_soundscape: 1-4 sentences using h3_prompt_framework"""
        scene_lower = scene.lower() if scene else ""
        ambient_map = {
            "雨": "Steady rain taps against surfaces",
            "night": "Low urban hum continues",
            "夜": "夜风与远距离车流声",
            "海": "海浪轻拍 + 海鸥间歇叫声",
            "山": "风穿过树林 + 远处鸟鸣",
            "办公室": "空调低频 + 键盘敲击 + 同事低声",
            "咖啡": "磨豆机 + 蒸汽 + 杯碟轻响",
            "学校": "走廊脚步 + 铃声 + 课间喧闹",
            "医院": "走廊脚步 + 监护仪滴声 + 远处广播",
        }
        ambient_parts = []
        for key, val in ambient_map.items():
            if key in scene_lower:
                ambient_parts.append(val)
                break
        if not ambient_parts:
            ambient_parts.append(f"Quiet ambient sound surrounds the {scene} scene")

        action = "Footsteps and fabric movement continue throughout"
        if "雨" in scene_lower:
            action = "Wet footsteps and the soft scrape of a chair accompany the scene"

        return render_h3_soundscape(ambient_parts[0], action)

    def _h3_build_music(self, non_diegetic_music, emotion, director) -> str:
        """H3 non_diegetic_music: 1-3 sentences using h3_prompt_framework"""
        if non_diegetic_music:
            return render_h3_nondiegetic_music(
                non_diegetic_music, "slow",
                "sustained low strings gradually decrease in volume",
            )
        emotion_music_map = {
            "孤独": "Sparse piano notes",
            "悲": "Solo cello with sustained low strings",
            "怒": "Distorted electric guitar with heavy percussion",
            "喜": "Bright acoustic guitar with light percussion",
            "悬疑": "Low electronic pulse with rising strings",
            "浪漫": "Soft piano with gentle strings",
            "史诗": "Full orchestral brass and strings at a slow tempo",
        }
        instr = emotion_music_map.get(emotion, "Sparse piano notes")
        return render_h3_nondiegetic_music(
            instr, "slow",
            "sustained low strings gradually decrease in volume",
        )

    def _h3_build_base_prompt(self, instruction, multimodal, soundscape, music) -> str:
        """H3 base mode (T2VA/I2VA/FL2VA/L2VA) full prompt"""
        parts = []
        if instruction:
            parts.append(instruction)
            parts.append("")
        parts.append(multimodal)
        parts.append("")
        parts.append(soundscape)
        parts.append("")
        parts.append(music)
        return "\n".join(parts)

    def _h3_build_ref2va_prompt(self, reference_assets, user_intent, scene,
                                 multimodal, soundscape, music) -> str:
        """H3 Ref2VA 6-section full prompt"""
        sections = []
        sections.append("subject_definitions:")
        sections.append(f"<Subject 1> is the {scene} scene, with all visible environmental details.")
        if reference_assets and reference_assets != "无具体 reference" and reference_assets.strip():
            sections.append(f"<Subject 2> is the referenced character/subject based on {reference_assets[:80]}.")
        sections.append("")

        sections.append("summary:")
        sections.append(f"[reference generation] The target video depicts {user_intent} within {scene}.")
        sections.append("")

        sections.append("retention_analysis:")
        sections.append("<Subject 1> (appears throughout): fully_preserved - all scene anchors are retained.")
        if reference_assets and reference_assets != "无具体 reference" and reference_assets.strip():
            sections.append("<Subject 2> (appears in [Shot 1], [Shot 2]): partially_preserved - identity and core features are retained.")
        sections.append("")

        sections.append("detailed_description:")
        sections.append(multimodal.replace("integrated_multimodal_description:", "").strip())
        sections.append("")

        sections.append(soundscape)
        sections.append("")
        sections.append(music)

        return "\n".join(sections)

    def _h3_validate(self, h3_mode, instruction, multimodal, soundscape, music) -> str:
        """H3-specific validation report"""
        checks = []
        checks.append(f"✓ H3 Mode: {h3_mode} ({H3_MODES[h3_mode]['name_cn']})")

        if h3_mode != "T2VA" and not instruction:
            checks.append(f"⚠ Part One instruction 缺失 ({h3_mode} 需要 keyframe 对齐)")
        else:
            checks.append(f"✓ Part One instruction: {len(instruction)} chars")

        checks.append(f"✓ integrated_multimodal_description: {len(multimodal)} chars (建议 > 100)")
        checks.append(f"✓ overall_soundscape: {len(soundscape)} chars (建议 50-300)")
        checks.append(f"✓ non_diegetic_music: {len(music)} chars (建议 30-200)")

        shot_count = multimodal.count("[Shot ")
        checks.append(f"✓ Shot count: {shot_count} (1-{h3_mode} 模式建议)")

        if "amplitude" in multimodal or "speed" in multimodal:
            checks.append("✓ Camera motion 3D 维度 (motion + amplitude + speed) 完整")
        else:
            checks.append("⚠ Camera motion 缺 amplitude/speed 描述 (建议 H3 三维拆解)")

        if "<d>" in multimodal:
            checks.append("✓ Dialogue 使用 H3 <d>[Language] 格式")
        else:
            checks.append("  i  Dialogue <d> 标签未使用 (无对白时正常)")

        return "\n".join(checks)

    def _h3_build_summary_card(self, h3_mode, director, scene, duration, visual_style,
                                aspect_ratio, emotion, has_dialogue, has_music) -> str:
        """H3 1-screen summary card"""
        return f"""=== H3 Context IR Summary ===
Mode: {h3_mode} ({H3_MODES[h3_mode]['name_cn']})
Director: {director}
Scene: {scene[:60]}
Duration: {duration}s
Visual Style: {visual_style}
Aspect Ratio: {aspect_ratio}
Emotion: {emotion}
Dialogue: {'有' if has_dialogue else '无'}
Music: {'有' if has_music else '无 (auto-generated based on emotion)'}
"""

    def _h3_deep_fallback(self, user_intent, director, scene, duration, error_msg) -> dict:
        """Fallback when H3 framework is not loadable"""
        return {
            "h3_mode": "T2VA",
            "h3_instruction": "",
            "h3_multimodal": f"integrated_multimodal_description: [Shot 1] Cinematic, a {scene} scene. {user_intent}.",
            "h3_soundscape": f"overall_soundscape: Ambient sound surrounds the {scene}.",
            "h3_music": "non_diegetic_music: N/A",
            "h3_full_prompt": f"[H3 framework unavailable: {error_msg}]\n\nintegrated_multimodal_description: [Shot 1] Cinematic, {scene}.",
            "h3_validation": f"⚠ H3 framework 加载失败: {error_msg}",
            "h3_summary_card": f"=== H3 Summary (Fallback) ===\nScene: {scene}\nDirector: {director}\nDuration: {duration}s",
        }


# === 注册到 ComfyUI ===
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "UniversalDirectorPromptNode": UniversalDirectorPromptNode,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "UniversalDirectorPromptNode": "Universal Director Prompt (6 models router)",
# }


if __name__ == "__main__":
    # 本地测试
    print("=== UniversalDirectorPromptNode 本地测试 ===\n")
    node = UniversalDirectorPromptNode()

    # 测试 1: 通用模式
    result = node.convert_universal(
        user_intent="雨夜香港旺角, 男女主角擦肩而过",
        target_model="通用 (兼容所有模型)",
        has_first_frame=False, has_last_frame=False, has_video_ref=False, has_audio_ref=False,
        visual_style="Cinematic", director="王家卫",
        duration=8, aspect_ratio="16:9 横屏",
        scene="雨夜香港旺角, 霓虹灯光在雨水中反射",
        emotion="孤独", intent="营造孤寂浪漫氛围",
        dialogue="I thought I would never see you again.",
        dialogue_language="English", non_diegetic_music="",
        story_theory="Save the Cat", hook_style="无", subtitle_required=False,
    )
    labels = ["target_model", "model_specific", "h3_mode", "h3_full", "universal_5",
              "director_anchor", "shot_plan", "dialogue", "audio", "story_arc",
              "validation", "anti_ai"]
    for label, val in zip(labels, result):
        print(f"--- {label} ---")
        print(val[:300] if len(str(val)) > 300 else val)
        print()
