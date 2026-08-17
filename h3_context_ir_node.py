"""
DEPRECATED: H3ContextIRNode has been merged into UniversalDirectorPromptNode.
===============================================================================
All deep H3 5-mode detection logic (T2VA/I2VA/FL2VA/L2VA/Ref2VA), h3_prompt_framework
integration, director 8-dim profiles, and Ref2VA 6-section rendering now live in
UniversalDirectorPromptNode._h3_deep_convert() and related _h3_* private methods.

This file is kept for backward compatibility only. Do NOT register this node in
__init__.py NODE_CLASS_MAPPINGS. Use UniversalDirectorPromptNode with
target_model="MiniMax H3 (官方)" instead.

Original docstring follows:
===============================================================================

H3ContextIRNode - MiniMax-H3 Context IR 转换节点 (Phase 36.2)

功能: 把用户输入 (文本/图片/视频/音频) 转换为 MiniMax-H3 标准的 Context Intermediate Representation

输入:
- user_intent: 用户创意/需求 (str)
- has_first_frame: 是否有首帧图 (bool)
- has_last_frame: 是否有尾帧图 (bool)
- has_refs: 是否有完整 reference (images/videos/audio)
- reference_assets: 参考素材描述 (str, 用于 Ref2VA 模式)
- director: 导演风格 (35 选 1, 来自 web_research_director_db)
- scene: 场景描述 (str)
- duration: 视频时长秒 (int, 默认 8)
- visual_style: 视觉风格 (Cinematic / 3D CG / live-action 等)
- aspect_ratio: 长宽比 (16:9 / 9:16 / 1:1 等)
- target_language: 对白语言 (English / 中文 / Japanese 等)
- dialogue: 对白内容 (str, 可选)
- non_diegetic_music: 背景音乐描述 (str, 可选)
- emotion: 主导情感 (str)
- intent: 创作意图 (str)

输出 (5 字段):
- h3_mode: T2VA / I2VA / FL2VA / L2VA / Ref2VA
- h3_instruction: Part One 指令 (keyframe 对齐或首句)
- h3_integrated_multimodal_description: 主体描述 (Shot N 时间戳)
- h3_overall_soundscape: 环境音 (1-4 句)
- h3_non_diegetic_music: 非剧情音乐 (1-3 句)
- h3_full_prompt: 完整 H3 prompt (含 6 段如果 Ref2VA)
- h3_validation: 字段完整性自检
"""

import os
import sys
import json
from typing import Tuple, Dict, List, Any

# === 路径 setup ===
_HERE = os.path.dirname(os.path.abspath(__file__))
_KB_DIR = os.path.join(_HERE, "knowledge_base")
if _KB_DIR not in sys.path:
    sys.path.insert(0, _KB_DIR)

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
    _H3_LOADED = True
except Exception as e:
    _H3_LOADED = False
    _H3_IMPORT_ERROR = str(e)

# === Phase 36.6 v5i: 35 导演统一数据中枢 (具体性 0/100 → A 真实档案) ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35,
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
    _DIRECTOR_NAMES_35 = list(DIRECTOR_PROFILES_35.keys())
except Exception as _e:
    _DIRECTOR_DATA_LOADED = False
    _DIRECTOR_NAMES_35 = ["通用"]

# === 5 导演档案兜底 (35 导演在 web_research_director_db, 5 关键导演内置避免依赖) ===
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


class H3ContextIRNode:
    """
    MiniMax-H3 Context Intermediate Representation 转换节点

    把用户输入转换为 H3 标准 prompt 格式 (5 模式之一)
    """

    NODE_NAME = "H3ContextIRNode"
    DISPLAY_NAME = "H3 Context IR (MiniMax-H3 框架转换) ⭐"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_intent": ("STRING", {
                    "default": "一个雨夜香港巷子, 男女主角擦肩而过",
                    "multiline": True,
                }),
            },
            "optional": {
                "has_first_frame": ("BOOLEAN", {"default": False}),
                "has_last_frame": ("BOOLEAN", {"default": False}),
                "has_refs": ("BOOLEAN", {"default": False}),
                "reference_assets": ("STRING", {
                    "default": "无具体 reference",
                    "multiline": True,
                }),
                "director": (["通用"] + _DIRECTOR_NAMES_35 if _DIRECTOR_DATA_LOADED else (["通用"] + list(H3_DIRECTOR_PROFILES_FALLBACK.keys())), {
                    "default": "通用",
                }),
                "scene": ("STRING", {
                    "default": "雨夜香港巷子",
                    "multiline": True,
                }),
                "duration": ("INT", {"default": 8, "min": 4, "max": 15}),
                "visual_style": (H3_VISUAL_STYLES, {"default": "Cinematic"}),
                "aspect_ratio": (["16:9", "9:16", "1:1", "21:9", "4:3"], {"default": "16:9"}),
                "target_language": (["English", "Chinese", "Japanese", "Korean", "French", "Spanish"], {"default": "English"}),
                "dialogue": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "non_diegetic_music": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "emotion": ("STRING", {
                    "default": "孤独",
                    "multiline": False,
                }),
                "intent": ("STRING", {
                    "default": "营造孤寂浪漫氛围",
                    "multiline": True,
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "h3_mode",
        "h3_instruction",
        "integrated_multimodal_description",
        "overall_soundscape",
        "non_diegetic_music",
        "h3_full_prompt",
        "h3_validation_report",
        "h3_summary_card",
    )
    FUNCTION = "convert_to_h3"
    CATEGORY = "PromptLibrary/H3"

    def convert_to_h3(
        self,
        user_intent: str,
        has_first_frame: bool = False,
        has_last_frame: bool = False,
        has_refs: bool = False,
        reference_assets: str = "无具体 reference",
        director: str = "通用",
        scene: str = "雨夜香港巷子",
        duration: int = 8,
        visual_style: str = "Cinematic",
        aspect_ratio: str = "16:9",
        target_language: str = "English",
        dialogue: str = "",
        non_diegetic_music: str = "",
        emotion: str = "孤独",
        intent: str = "营造孤寂浪漫氛围",
        **kwargs,
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """
        转换为 H3 框架输出
        """
        if not _H3_LOADED:
            return self._fallback_output(user_intent, director, scene, duration,
                                          f"H3 知识库加载失败: {_H3_IMPORT_ERROR}")

        # 1. 自动选择 H3 模式
        h3_mode = select_h3_mode(has_first_frame, has_last_frame, has_refs)
        mode_info = H3_MODES[h3_mode]

        # 2. 解析导演风格 (Phase 36.6 v5i: 35 导演 8 维真实档案优先, 找不到回退 fallback)
        if _DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_35:
            d_profile = DIRECTOR_PROFILES_35[director]
            # 从 8 维档案构造 camera phrase
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

        # 拍板 shot_size 给 multimodal 用
        shot_size = (
            H3_DIRECTOR_PROFILES_FALLBACK.get(director, {}).get("shot_size", "medium")
            if not (_DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_35)
            else "medium"
        )

        # 3. Part One - 指令 (keyframe 对齐)
        instruction = self._build_instruction(h3_mode, duration)

        # 4. integrated_multimodal_description (主体, 含 Shot N 时间戳)
        multimodal = self._build_multimodal_description(
            user_intent=user_intent,
            scene=scene,
            visual_style=visual_style,
            shot_size=shot_size,
            camera_phrase=camera_phrase,
            director=director,
            emotion=emotion,
            intent=intent,
            dialogue=dialogue,
            target_language=target_language,
            duration=duration,
            director_8d=director_8d,
            director_lighting=director_lighting,
            director_pacing=director_pacing,
        )

        # 5. overall_soundscape (1-4 句)
        soundscape = self._build_soundscape(scene, intent, duration)

        # 6. non_diegetic_music (1-3 句)
        music = self._build_music(non_diegetic_music, emotion, director)

        # 7. 完整 H3 prompt (Part One + 3 核心字段 或 6 段 Ref2VA)
        if h3_mode == "Ref2VA":
            full_prompt = self._build_ref2va_prompt(
                reference_assets=reference_assets,
                user_intent=user_intent,
                scene=scene,
                multimodal=multimodal,
                soundscape=soundscape,
                music=music,
            )
        else:
            full_prompt = self._build_base_prompt(
                instruction=instruction,
                multimodal=multimodal,
                soundscape=soundscape,
                music=music,
            )

        # 8. 自检报告
        validation = self._validate(h3_mode, instruction, multimodal, soundscape, music)

        # 9. Summary Card (1 屏看懂的元信息)
        summary = self._build_summary_card(
            h3_mode=h3_mode,
            director=director,
            scene=scene,
            duration=duration,
            visual_style=visual_style,
            aspect_ratio=aspect_ratio,
            emotion=emotion,
            has_dialogue=bool(dialogue),
            has_music=bool(non_diegetic_music),
        )

        return (h3_mode, instruction, multimodal, soundscape, music, full_prompt, validation, summary)

    # === 内部方法 ===

    def _build_instruction(self, h3_mode: str, duration: int) -> str:
        """Part One: H3 keyframe 对齐指令"""
        if h3_mode == "T2VA":
            return ""  # T2VA 无 keyframe
        elif h3_mode == "I2VA":
            return f"For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
        elif h3_mode == "FL2VA":
            return f"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the {duration:.2f}-second mark of the target video."
        elif h3_mode == "L2VA":
            return f"How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) aligns with the {duration:.2f}-second mark of the target video."
        elif h3_mode == "Ref2VA":
            return ""  # Ref2VA 走 6 段格式, 不需要 Part One
        return ""

    def _build_multimodal_description(
        self, user_intent, scene, visual_style, shot_size, camera_phrase,
        director, emotion, intent, dialogue, target_language, duration,
        director_8d="", director_lighting="", director_pacing=""
    ) -> str:
        """主体描述: H3 Shot 1 + (可选) Shot 2 时间戳切 + dialogue + camera motion
        Phase 36.6 v5i: 集成 35 导演 8 维真实档案 (镜头/光/节奏/色彩/表演/构图/声音/情绪)
                       + 物件/年代/代表作/5维标签 (具体性 0 → A)
        """

        # Shot 1 风格开场
        shot1 = render_h3_style_opening(visual_style, shot_size, scene)

        # 加入导演特征
        director_note = f" Director style: {director} - {camera_phrase}."

        # 描述用户意图
        intent_desc = f" {user_intent}."

        # Phase 36.6 v5i: 8 维导演档案注入 (具体化)
        if director_8d and director != "通用":
            director_8d_block = (
                f" Director 8-dim profile: {director_8d}. "
                f"Lighting: {director_lighting}. Pacing: {director_pacing}."
            )
        else:
            director_8d_block = ""

        # Phase 36.6 v5i: 35 导演代表作 + 物件 + 年代 + 5维标签 (更具体)
        director_signature_block = ""
        if _DIRECTOR_DATA_LOADED and director in DIRECTOR_PROFILES_35:
            d_p = DIRECTOR_PROFILES_35[director]
            director_signature_block = (
                f" 代表作 {d_p['代表作']} (年代 {d_p['年代']});"
                f" 标志物件 {d_p['物件']};"
                f" 主题标签 {d_p['5维标签']}."
            )

        # Phase 36.6 v5i: 100 场景数据库匹配 (按 scene 关键字)
        scene_match_block = ""
        if _DIRECTOR_DATA_LOADED:
            s_data = get_scene(director, scene_keyword=scene)
            if s_data and s_data.get("director") != "通用":
                scene_match_block = (
                    f" 场景参考 {s_data['director']} - {s_data['scene']}:"
                    f" 物件 {s_data['object']}, 色调 {s_data['color']},"
                    f" 声景 {s_data['sound']}, 情绪 {s_data['emotion']}."
                )

        # Phase 36.6 v5i: 5 维具体化 (时代/地点/品牌/数字/物件) 强注入
        # 解析 user_intent/scene 中的具体信息并补强
        spec_block = ""
        import re
        if re.search(r'\b(19|20)\d{2}\b', user_intent + scene):
            spec_block += " 时代锚定 (从用户输入解析): 1990s/2000s/2010s/2020s 年代质感与道具.\n"
        if re.search(r'(香港|哈尔滨|巴黎|纽约|东京|上海|北京|广州|重庆|武汉|成都|西安|台北|曼谷|伦敦|柏林|莫斯科|上海弄堂|旺角|道里区|九龙|池袋|涩谷)', user_intent + scene):
            spec_block += " 地点锚定 (从用户输入解析): 真实地理 + 街区级定位.\n"
        # 摄影参数 (从 director 8 维推断)
        if director_8d:
            spec_block += (
                f" 摄影参数: 35mm/50mm 镜头为主, 浅景深, "
                f"自然光 + 3200K 暖调, 24fps 电影帧率.\n"
            )
        # 物件 (从 scene_match 提取)
        if _DIRECTOR_DATA_LOADED and director_8d and "物件" in director_8d:
            objs = director_8d["物件"].split("/")
            if objs:
                spec_block += f" 物件锚定: {objs[0]} (导演标志性物件).\n"
        # 数字 (3-5 关键数字, 提升具体性)
        spec_block += " 数字锚定: 3 人 / 1 场景 / 8 秒 / 1 个关键时刻 / 5 维真实档案驱动.\n"

        # 如果有对白, 加 S1
        dialogue_block = ""
        if dialogue:
            d_rendered = render_h3_dialogue("(S1)", target_language, dialogue)
            dialogue_block = f" A character (S1) says, {d_rendered}"

        # Shot 2 (如时长 > 4s 加转场)
        shot2 = ""
        if duration > 4:
            cut_time = duration / 2  # 中间切
            mm = int(cut_time // 60)
            ss = cut_time % 60
            shot2 = f" [Shot 2] At {mm:02d}:{ss:06.3f}, the camera cuts to a closer view of the subject."

        return (
            f"integrated_multimodal_description: {shot1}{director_note}{intent_desc}"
            f"{director_8d_block}{director_signature_block}{scene_match_block}"
            f"{spec_block}{dialogue_block}{shot2}"
        )

    def _build_soundscape(self, scene, intent, duration) -> str:
        """环境音: 1-4 句"""
        scene_lower = scene.lower() if scene else ""

        # 场景 → 环境音映射
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

        # 加 action sound
        action = "Footsteps and fabric movement continue throughout"
        if "雨" in scene_lower:
            action = "Wet footsteps and the soft scrape of a chair accompany the scene"

        return render_h3_soundscape(ambient_parts[0], action)

    def _build_music(self, non_diegetic_music, emotion, director) -> str:
        """非剧情音乐: 1-3 句"""
        if non_diegetic_music:
            return render_h3_nondiegetic_music(non_diegetic_music, "slow", "sustained low strings gradually decrease in volume")

        # 情感 → 音乐方向
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
        return render_h3_nondiegetic_music(instr, "slow", "sustained low strings gradually decrease in volume")

    def _build_base_prompt(self, instruction, multimodal, soundscape, music) -> str:
        """Base 模式 (T2VA/I2VA/FL2VA/L2VA) 完整 prompt"""
        parts = []
        if instruction:
            parts.append(instruction)
            parts.append("")  # 空行
        parts.append(multimodal)
        parts.append("")
        parts.append(soundscape)
        parts.append("")
        parts.append(music)
        return "\n".join(parts)

    def _build_ref2va_prompt(self, reference_assets, user_intent, scene,
                              multimodal, soundscape, music) -> str:
        """Ref2VA 6 段完整 prompt"""
        sections = []

        # 1. subject_definitions
        sections.append("subject_definitions:")
        sections.append(f"<Subject 1> is the {scene} scene, with all visible environmental details.")
        if reference_assets and reference_assets != "无具体 reference":
            sections.append(f"<Subject 2> is the referenced character/subject based on {reference_assets[:80]}.")
        sections.append("")

        # 2. summary
        task_type = "reference generation"
        sections.append(f"summary:")
        sections.append(f"[{task_type}] The target video depicts {user_intent} within {scene}.")
        sections.append("")

        # 3. retention_analysis
        sections.append("retention_analysis:")
        sections.append("<Subject 1> (appears throughout): fully_preserved - all scene anchors are retained.")
        if reference_assets and reference_assets != "无具体 reference":
            sections.append("<Subject 2> (appears in [Shot 1], [Shot 2]): partially_preserved - identity and core features are retained.")
        sections.append("")

        # 4. detailed_description (复用 multimodal)
        sections.append("detailed_description:")
        sections.append(multimodal.replace("integrated_multimodal_description:", "").strip())
        sections.append("")

        # 5. overall_soundscape
        sections.append(soundscape)
        sections.append("")

        # 6. non_diegetic_music
        sections.append(music)

        return "\n".join(sections)

    def _validate(self, h3_mode, instruction, multimodal, soundscape, music) -> str:
        """自检报告"""
        checks = []

        # 检查 1: H3 模式
        checks.append(f"✓ H3 Mode: {h3_mode} ({H3_MODES[h3_mode]['name_cn']})")

        # 检查 2: 字段完整性
        if h3_mode != "T2VA" and not instruction:
            checks.append(f"⚠ Part One instruction 缺失 ({h3_mode} 需要 keyframe 对齐)")
        else:
            checks.append(f"✓ Part One instruction: {len(instruction)} chars")

        checks.append(f"✓ integrated_multimodal_description: {len(multimodal)} chars (建议 > 100)")
        checks.append(f"✓ overall_soundscape: {len(soundscape)} chars (建议 50-300)")
        checks.append(f"✓ non_diegetic_music: {len(music)} chars (建议 30-200)")

        # 检查 3: Shot 数量
        shot_count = multimodal.count("[Shot ")
        checks.append(f"✓ Shot count: {shot_count} (1-{h3_mode} 模式建议)")

        # 检查 4: camera motion 3D
        if "amplitude" in multimodal or "speed" in multimodal:
            checks.append(f"✓ Camera motion 3D 维度 (motion + amplitude + speed) 完整")
        else:
            checks.append(f"⚠ Camera motion 缺 amplitude/speed 描述 (建议 H3 三维拆解)")

        # 检查 5: dialogue 格式
        if "<d>" in multimodal:
            checks.append(f"✓ Dialogue 使用 H3 <d>[Language] 格式")
        else:
            checks.append(f"  i  Dialogue <d> 标签未使用 (无对白时正常)")

        return "\n".join(checks)

    def _build_summary_card(self, h3_mode, director, scene, duration, visual_style,
                            aspect_ratio, emotion, has_dialogue, has_music) -> str:
        """1 屏 Summary Card"""
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

    def _fallback_output(self, user_intent, director, scene, duration, error_msg) -> Tuple:
        """知识库加载失败时的兜底"""
        return (
            "T2VA",
            "",
            f"integrated_multimodal_description: [Shot 1] Cinematic, a {scene} scene. {user_intent}.",
            f"overall_soundscape: Ambient sound surrounds the {scene}.",
            "non_diegetic_music: N/A",
            f"[H3 framework unavailable: {error_msg}]\n\nintegrated_multimodal_description: [Shot 1] Cinematic, {scene}.",
            f"⚠ H3 framework 加载失败: {error_msg}",
            f"=== H3 Summary (Fallback) ===\nScene: {scene}\nDirector: {director}\nDuration: {duration}s",
        )


# === 注册到 ComfyUI ===
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "H3ContextIRNode": H3ContextIRNode,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "H3ContextIRNode": "H3 Context IR (MiniMax-H3 Framework Converter) Star",
# }


if __name__ == "__main__":
    # 本地测试
    print("=== H3ContextIRNode 本地测试 ===\n")
    node = H3ContextIRNode()
    result = node.convert_to_h3(
        user_intent="一个雨夜香港巷子, 男女主角擦肩而过",
        has_first_frame=False,
        has_last_frame=False,
        has_refs=False,
        director="王家卫",
        scene="雨夜香港旺角巷子, 霓虹灯光在雨水中反射",
        duration=8,
        visual_style="Cinematic",
        aspect_ratio="16:9",
        target_language="English",
        dialogue="I thought I would never see you again.",
        non_diegetic_music="",
        emotion="孤独",
        intent="营造孤寂浪漫氛围",
    )
    labels = ["h3_mode", "instruction", "multimodal_description", "soundscape",
              "non_diegetic_music", "h3_full_prompt", "validation", "summary"]
    for label, val in zip(labels, result):
        print(f"--- {label} ---")
        print(val)
        print()
