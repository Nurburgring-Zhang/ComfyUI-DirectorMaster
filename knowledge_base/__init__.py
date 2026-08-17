# Knowledge Base - 世界级导演知识库
# 包含从IMDB Top 250、热门短剧、爆款短视频中提取的专业影视制作知识

from knowledge_base.master_cinematography import MASTER_CINEMATOGRAPHY
from knowledge_base.narrative_structures import NARRATIVE_STRUCTURES
from knowledge_base.genre_profiles import GENRE_PROFILES
from knowledge_base.performance_system import PERFORMANCE_SYSTEM
from knowledge_base.shot_vocabulary import SHOT_VOCABULARY
from knowledge_base.transition_grammar import TRANSITION_GRAMMAR
from knowledge_base.short_drama_patterns import SHORT_DRAMA_PATTERNS
from knowledge_base.viral_video_techniques import VIRAL_VIDEO_TECHNIQUES
from knowledge_base.director_styles import DIRECTOR_STYLES
from knowledge_base.emotion_rendering import EMOTION_RENDERING

# --- Phase 5.0: 统一查询接口 (供所有节点使用) ---

try:
    from knowledge_base.picture_book_styles import PICTURE_BOOK_STYLES
except Exception:
    PICTURE_BOOK_STYLES = {}

try:
    from knowledge_base.children_content_styles import CHILDREN_CONTENT_STYLES
except Exception:
    CHILDREN_CONTENT_STYLES = {}

try:
    from knowledge_base.dimension_design import DIMENSION_DESIGN
except Exception:
    DIMENSION_DESIGN = {}

try:
    from knowledge_base.creation_skills import CREATION_SKILLS
except Exception:
    CREATION_SKILLS = {}


def get_director_decision(director_name, context=""):
    """统一导演决策查询: 一次调用获取导演在该上下文的所有决策参数"""
    result = {}
    dn = director_name.lower().replace(" ", "_") if director_name else ""
    for key, profile in DIRECTOR_STYLES.items():
        cn = profile.get("cn", "")
        if key == dn or cn == director_name or director_name in cn:
            result["style"] = profile
            break
    cine = MASTER_CINEMATOGRAPHY
    if context:
        ctx_lower = context.lower()
        for cat_name, cat_data in cine.items():
            if isinstance(cat_data, dict):
                for item_name, item_data in cat_data.items():
                    if isinstance(item_data, dict):
                        trigger = str(item_data.get("trigger", ""))
                        if any(kw in ctx_lower for kw in trigger.lower().split("/")):
                            result.setdefault("cinematography_matches", []).append(
                                {"type": cat_name, "item": item_name, "data": item_data}
                            )
    for gk, gv in GENRE_PROFILES.items():
        cn = gv.get("cn", "")
        if context and (gk in context.lower() or cn in context):
            result["genre"] = gv
            break
    return result


def get_scene_toolkit(scene_type):
    """获取场景类型的全套工具包 (镜头/光/色/声/表演建议)"""
    toolkit = {"shot": [], "lighting": [], "color": [], "sound": [], "performance": []}
    st = scene_type.lower() if scene_type else ""
    cine = MASTER_CINEMATOGRAPHY
    if "shot_types" in cine:
        for shot_name, shot_data in cine["shot_types"].items():
            if isinstance(shot_data, dict):
                trigger = str(shot_data.get("trigger", "")).lower()
                if st and any(kw in trigger for kw in st.split()):
                    toolkit["shot"].append({"name": shot_name, "cn": shot_data.get("cn", ""), "data": shot_data})
    if "lighting_types" in cine:
        for lt_name, lt_data in cine["lighting_types"].items():
            if isinstance(lt_data, dict):
                trigger = str(lt_data.get("trigger", "")).lower()
                if st and any(kw in trigger for kw in st.split()):
                    toolkit["lighting"].append({"name": lt_name, "data": lt_data})
    if "color_psychology" in cine:
        for cp_name, cp_data in cine["color_psychology"].items():
            if isinstance(cp_data, dict):
                trigger = str(cp_data.get("trigger", "")).lower()
                if st and any(kw in trigger for kw in st.split()):
                    toolkit["color"].append({"name": cp_name, "data": cp_data})
    er = EMOTION_RENDERING
    if "emotion_spectrum" in er and "primary_emotions" in er["emotion_spectrum"]:
        for emo_name, emo_data in er["emotion_spectrum"]["primary_emotions"].items():
            if isinstance(emo_data, dict) and st:
                toolkit["performance"].append({"emotion": emo_name, "cn": emo_data.get("cn", "")})
    return toolkit


def get_emotion_palette(emotion, intensity=0.5):
    """获取情绪的跨维度映射 (色彩/音乐/节奏/镜头)"""
    palette = {"color": "", "music": "", "pacing": "", "camera": "", "lighting": ""}
    er = EMOTION_RENDERING
    if "emotion_spectrum" not in er:
        return palette
    all_emotions = {}
    for cat in ("primary_emotions", "complex_emotions"):
        cat_data = er["emotion_spectrum"].get(cat, {})
        if isinstance(cat_data, dict):
            all_emotions.update(cat_data)
    emo_data = all_emotions.get(emotion, {})
    if not emo_data:
        for k, v in all_emotions.items():
            if isinstance(v, dict) and v.get("cn", "") == emotion:
                emo_data = v
                break
    if not emo_data:
        return palette
    levels = emo_data.get("intensity_levels", [])
    chosen_level = None
    for lv in levels:
        if isinstance(lv, dict) and lv.get("level", 0) <= intensity:
            chosen_level = lv
    if chosen_level:
        palette["visual_description"] = chosen_level.get("visual", "")
        palette["cn_name"] = chosen_level.get("cn", "")
    palette["camera"] = emo_data.get("camera_response", "")
    palette["lighting"] = emo_data.get("lighting_response", "")
    palette["pacing"] = emo_data.get("pacing_response", "")
    palette["color"] = emo_data.get("color_response", "")
    palette["music"] = emo_data.get("music_response", "")
    return palette


def get_transition_for_context(from_beat="", to_beat="", emotion_delta=0.0):
    """获取场景转场建议"""
    tg = TRANSITION_GRAMMAR
    suggestions = []
    if "cut_types" in tg:
        for cut_name, cut_data in tg["cut_types"].items():
            if isinstance(cut_data, dict):
                trigger = str(cut_data.get("trigger", "")).lower()
                if abs(emotion_delta) > 0.5 and "强烈" in trigger:
                    suggestions.append({"type": cut_name, "data": cut_data, "reason": "情绪跳跃大"})
                elif abs(emotion_delta) < 0.2 and ("平稳" in trigger or "连续" in trigger):
                    suggestions.append({"type": cut_name, "data": cut_data, "reason": "情绪平稳"})
    if "optical_transitions" in tg:
        for ot_name, ot_data in tg["optical_transitions"].items():
            if isinstance(ot_data, dict):
                trigger = str(ot_data.get("trigger", "")).lower()
                if from_beat and from_beat.lower() in trigger:
                    suggestions.append({"type": ot_name, "data": ot_data, "reason": f"匹配{from_beat}"})
    return suggestions


def get_performance_system(archetype="", emotion=""):
    """获取表演系统建议 (微表情/身体语言/Laban)"""
    ps = PERFORMANCE_SYSTEM
    result = {"micro_expressions": [], "body_language": [], "laban": []}
    if "micro_expressions" in ps:
        me = ps["micro_expressions"]
        for cat in ("basic_9", "advanced_21"):
            for expr_name, expr_data in me.get(cat, {}).items():
                if isinstance(expr_data, dict):
                    if emotion and emotion.lower() in str(expr_data).lower():
                        result["micro_expressions"].append({"name": expr_name, "data": expr_data})
    if "laban_efforts" in ps:
        for effort_name, effort_data in ps["laban_efforts"].items():
            if isinstance(effort_data, dict):
                result["laban"].append({"name": effort_name, "data": effort_data})
    if "character_archetypes" in ps:
        for arch_name, arch_data in ps["character_archetypes"].items():
            if isinstance(arch_data, dict):
                if archetype and archetype.lower() in arch_name.lower():
                    result["archetype_match"] = {"name": arch_name, "data": arch_data}
    return result


def get_short_drama_patterns(style=""):
    """获取短剧模式建议"""
    sdp = SHORT_DRAMA_PATTERNS
    result = {"hooks": [], "formulas": [], "techniques": []}
    if "opening_hooks" in sdp:
        for hook_name, hook_data in sdp["opening_hooks"].items():
            if isinstance(hook_data, dict):
                result["hooks"].append({"name": hook_name, "data": hook_data})
    if "narrative_formulas" in sdp:
        for formula_cat, formula_data in sdp["narrative_formulas"].items():
            if isinstance(formula_data, dict):
                for fn, fd in formula_data.items():
                    result["formulas"].append({"category": formula_cat, "name": fn, "data": fd})
    if "cliffhanger_techniques" in sdp:
        result["techniques"] = sdp["cliffhanger_techniques"]
    return result


def get_viral_techniques(platform=""):
    """获取爆款视频技术建议"""
    vvt = VIRAL_VIDEO_TECHNIQUES
    result = {"attention": [], "storytelling": [], "pacing": []}
    cat_map = {"attention_mechanics": "attention", "visual_storytelling": "storytelling", "pacing_formulas": "pacing"}
    for cat in ("attention_mechanics", "visual_storytelling", "pacing_formulas"):
        if cat in vvt:
            for item_name, item_data in vvt[cat].items():
                if isinstance(item_data, dict):
                    result[cat_map[cat]].append({"name": item_name, "data": item_data})
    return result
