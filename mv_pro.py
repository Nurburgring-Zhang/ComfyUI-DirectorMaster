# -*- coding: utf-8 -*-
"""
MvPro - MV 导演专家节点 (环节 39)
====================================================
MV (Music Video) 导演专业节点 - 真正的 MV 领域专家系统

核心能力:
1. 音乐结构 -> 视觉结构映射 (Intro/Verse/Chorus/Bridge/Outro 7 段式)
2. BPM -> 剪辑节奏映射 (60-200 BPM 四档)
3. MV 类型路由 (叙事/表演/概念/混合 4 型)
4. 音乐类型视觉编码 (Pop/Rock/Hip-Hop/Electronic/Folk/Classical/R&B/Metal)
5. MV 导演签名 (Hype Williams/Michel Gondry/Spike Jonze/David Fincher/Anton Corbijn)
6. H3 三大字段动态生成
7. 30 秒场景单元分镜
8. 灵魂注入系统
"""

import os
import sys
import json
import math

# === 核心依赖 ===
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import (
        DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5, SILENCE_MASTERY_5,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
        ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
        SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
        build_h3_three_fields, select_camera_motion, format_shot_motion,
        build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
        inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
        inject_silence_mastery_5, inject_5_elements, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)

# === 统一导演数据 ===
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile, SCENE_DATABASE_100, QUOTES_30,
        get_director, get_scene, get_random_quote,
    )
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False

# === 灵魂注入 ===
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# MV 领域专有数据
# ============================================================

GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = [
    "塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和",
    "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安",
    "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇",
    "周星驰", "Papi酱", "诺兰_短剧版",
]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# --- 音乐类型 ---
MUSIC_GENRES = ["流行 (Pop)", "摇滚 (Rock)", "嘻哈 (Hip-Hop)", "电子 (Electronic)",
                "民谣 (Folk)", "古典 (Classical)", "R&B", "金属 (Metal)", "auto"]

# --- MV 概念类型 ---
MV_CONCEPTS = ["叙事型 (Narrative)", "表演型 (Performance)", "概念型 (Concept)", "混合型 (Hybrid)", "auto"]

# --- 音乐结构 -> 视觉结构 7 段式映射 ---
MUSIC_VISUAL_STRUCTURE = {
    "intro": {
        "time": "0-15s",
        "music_role": "建立调性, 引入主旋律元素",
        "visual": "Establishing shot, atmosphere build, slow motion or static",
        "camera": "Slow push in / static wide / aerial descent",
        "editing": "Long takes, fade-in, minimal cuts",
        "energy": 0.2,
        "description": "环境建立, 氛围渲染, 慢动作或静态画面, 让观众进入音乐世界",
    },
    "verse_1": {
        "time": "15-45s",
        "music_role": "第一段叙述, 旋律展开",
        "visual": "Character introduction, medium shots, steady rhythm",
        "camera": "Medium shots, tracking, dolly, steady movement",
        "editing": "Cut on beat (every 2-4 beats), match cuts",
        "energy": 0.4,
        "description": "角色登场, 中景为主, 稳定节奏跟随旋律, 叙事或表演建立",
    },
    "pre_chorus": {
        "time": "45-60s",
        "music_role": "能量积蓄, 和弦进行推进",
        "visual": "Energy build, closer shots, camera starts moving faster",
        "camera": "Push in accelerating, handheld introduction, tighter framing",
        "editing": "Cuts shorten (every 1-2 beats), cross-dissolves to cuts",
        "energy": 0.6,
        "description": "能量攀升, 镜头逐渐靠近, 运动加速, 剪辑加密, 为副歌蓄势",
    },
    "chorus": {
        "time": "60-90s",
        "music_role": "情感高潮, 旋律爆发, 最大能量",
        "visual": "Peak energy, wide+close alternation, fast cuts synced to beat",
        "camera": "Wide-close alternation, whip pan, crane up, 360 arc",
        "editing": "Cut every beat or half-beat, jump cuts, strobe, montage",
        "energy": 1.0,
        "description": "视觉高潮, 广角与特写快速交替, 节拍同步剪辑, 所有视觉元素爆发",
    },
    "verse_2": {
        "time": "90-120s",
        "music_role": "第二段叙述, 旋律变奏",
        "visual": "Development, new locations, narrative progression",
        "camera": "New angles, location change, tracking with variation",
        "editing": "Similar to verse 1 but with variation, new coverage",
        "energy": 0.5,
        "description": "叙事推进, 新场景新角度, 在第一段基础上发展, 增加视觉层次",
    },
    "bridge": {
        "time": "120-150s",
        "music_role": "对比段, 和弦/节奏/情绪转折",
        "visual": "Contrast, different visual language, breakdown moment",
        "camera": "Radically different camera style, overhead, underwater, macro",
        "editing": "Slow down or radical acceleration, visual effects peak",
        "energy": 0.7,
        "description": "视觉反差, 完全不同的影像语言, 打破前面建立的规则, 制造惊喜",
    },
    "final_chorus_outro": {
        "time": "150s-end",
        "music_role": "最终副歌 + 尾奏, 情感顶峰到收束",
        "visual": "Climax, all visual elements converge, payoff, fade",
        "camera": "All signature moves combined, final crane up / pull back",
        "editing": "Peak intensity then gradually longer takes, final hold / fade",
        "energy": 0.9,
        "description": "视觉总爆发, 所有元素汇聚, 然后逐渐收束, 留给观众呼吸空间",
    },
}

# --- BPM -> 剪辑节奏映射 ---
BPM_EDITING_MAP = {
    "slow": {
        "range": "< 80 BPM",
        "cut_rhythm": "Long takes (4-8s per shot), cuts on every 4th beat or phrase boundary",
        "transitions": "Slow dissolves (1-2s), fade through black, gentle wipes",
        "camera_style": "Fluid crane/dolly, slow push in, smooth orbits",
        "energy_feel": "Meditative, atmospheric, breathing space, dream-like",
        "reference": "Radiohead 'No Surprises', Adele 'Someone Like You'",
    },
    "moderate": {
        "range": "80-120 BPM",
        "cut_rhythm": "Standard cuts on beat (2-4s per shot), cut on downbeat",
        "transitions": "Clean cuts, occasional dissolve, match cuts on movement",
        "camera_style": "Dolly/track, steady Steadicam, push in on chorus",
        "energy_feel": "Balanced, rhythmic, controlled energy, grounded",
        "reference": "Beyonce 'Halo', Ed Sheeran 'Shape of You'",
    },
    "fast": {
        "range": "120-160 BPM",
        "cut_rhythm": "Cut every 1-2 beats (0.5-1.5s per shot), whip pan transitions",
        "transitions": "Whip pans, flash frames, in-camera transitions, wipes",
        "camera_style": "Handheld energy, whip pans, snap zooms, dutch angles",
        "energy_feel": "High energy, aggressive, kinetic, pulse-driven",
        "reference": "BTS 'Dynamite', Dua Lipa 'Don't Start Now'",
    },
    "extreme": {
        "range": "> 160 BPM",
        "cut_rhythm": "Strobe cuts (< 0.5s per shot), jump cuts, subliminal inserts",
        "transitions": "Jump cuts, flash frames, strobe, glitch, datamosh",
        "camera_style": "Handheld shake, crash zoom, fish-eye, GoPro, drone crash",
        "energy_feel": "Manic, overwhelming, sensory assault, adrenaline",
        "reference": "Eminem 'Rap God', Slipknot 'Psychosocial'",
    },
}

# --- MV 类型路由 ---
MV_TYPE_ROUTING = {
    "narrative": {
        "cn": "叙事型",
        "structure": "Complete story arc, character development, dialogue-free drama",
        "key_elements": [
            "3-act story structure compressed into 3-4 minutes",
            "Character introduction within first 15 seconds",
            "Conflict/problem by the end of verse 1",
            "Resolution or twist aligned with final chorus",
            "Lip-sync woven into story (character sings as part of narrative)",
        ],
        "camera_approach": "Cinematic coverage (master + coverage), shallow DOF, motivated movement",
        "editing_philosophy": "Story logic overrides beat-sync; emotional beats align with musical beats",
        "lighting": "Motivated, naturalistic with cinematic enhancement, consistent scene lighting",
        "reference_mvs": "Johnny Cash 'Hurt', Childish Gambino 'This Is America', Taylor Swift 'All Too Well (10 Min)'",
    },
    "performance": {
        "cn": "表演型",
        "structure": "Stage/studio, choreography, lip sync, instrument performance",
        "key_elements": [
            "Dynamic stage or studio environment",
            "Choreography synchronized to beat",
            "Lip-sync as primary visual anchor",
            "Instrument close-ups (guitar fretboard, drum hits, keys)",
            "Lighting changes mark song structure transitions",
        ],
        "camera_approach": "Multi-camera coverage, crane/jib for stage, Steadicam for dance, macro for instruments",
        "editing_philosophy": "Beat-sync is king; every cut lands on beat, energy follows music exactly",
        "lighting": "Concert/stage lighting, moving heads, spots, silhouette, backlight rim",
        "reference_mvs": "OK Go 'Here It Goes Again', Beyonce 'Single Ladies', Michael Jackson 'Billie Jean'",
    },
    "concept": {
        "cn": "概念型",
        "structure": "Abstract visuals, symbolism, art installation, experimental",
        "key_elements": [
            "Central visual metaphor or concept drives all imagery",
            "No literal narrative; meaning through symbol and juxtaposition",
            "Art direction is the content (color, texture, shape, material)",
            "Body as sculpture, space as canvas, light as paint",
            "Viewer interpretation is intentionally open-ended",
        ],
        "camera_approach": "Locked-off symmetry, macro/abstract, extreme angles, unusual optics",
        "editing_philosophy": "Rhythm can be counter-intuitive; slow during fast sections, fast during slow",
        "lighting": "Sculptural, colored, neon, projection, practical effects as light source",
        "reference_mvs": "FKA Twigs 'Cellophane', Radiohead 'No Surprises', Bjork 'All Is Full of Love'",
    },
    "hybrid": {
        "cn": "混合型",
        "structure": "Story scenes intercut with performance scenes",
        "key_elements": [
            "A-story (narrative) intercut with B-story (performance)",
            "Verse = narrative progression, Chorus = performance energy",
            "Bridge = narrative climax or twist",
            "Visual language shifts between story (cinematic) and performance (stage/energy)",
            "Color/grading separates the two worlds",
        ],
        "camera_approach": "Two distinct styles: cinematic for story, dynamic for performance",
        "editing_philosophy": "Cross-cut between story and performance, sync emotional peaks",
        "lighting": "Two palettes: naturalistic for story, stylized for performance",
        "reference_mvs": "Eminem '8 Mile' trailer, The Weeknd 'Blinding Lights', Sia 'Chandelier'",
    },
}

# --- 音乐类型视觉编码 ---
GENRE_VISUAL_CODES = {
    "pop": {
        "cn": "流行",
        "palette": "Clean, bright, saturated colors, candy-like tones",
        "camera": "Smooth gimbal/crane, dolly, polished Steadicam, jib",
        "lighting": "High-key, soft beauty light, ring light, backlight glow",
        "texture": "Clean, polished, magazine-quality skin, sharp edges",
        "environment": "Studio, rooftop, city street, colorful interior, beach",
        "wardrobe": "Fashion-forward, coordinated color scheme, seasonal trends",
        "vfx": "Light leaks, lens flares, color overlays, subtle slow-mo",
    },
    "rock": {
        "cn": "摇滚",
        "palette": "Gritty, high contrast, desaturated with red/amber punches",
        "camera": "Handheld, crash zoom, dutch angles, in-the-crowd POV",
        "lighting": "Hard side light, practical lamps, fire, bare bulbs, silhouette",
        "texture": "Film grain, dust, scratches, analog imperfections",
        "environment": "Garage, warehouse, desert highway, dive bar, backstage",
        "wardrobe": "Leather, denim, band tees, boots, sweat-stained reality",
        "vfx": "Film burn, light leaks, split screen, time-lapse, raw energy",
    },
    "hiphop": {
        "cn": "嘻哈",
        "palette": "Urban, gold/platinum tones, neon accents, deep shadows",
        "camera": "Wide angle (16mm), slow-mo (120fps+), low angle power shots, drone",
        "lighting": "Neon, LED strips, car headlights, street lamps, golden hour",
        "texture": "Sharp digital, 4K clarity, wet asphalt reflections, chrome",
        "environment": "Urban streets, luxury interior, cars, rooftop, club, jewelry",
        "wardrobe": "Designer brands, chains, grills, sneakers, oversized fits",
        "vfx": "Slow-mo water/smoke, money rain, car drifts, drone shots, fish-eye",
    },
    "electronic": {
        "cn": "电子",
        "palette": "Neon, geometric, RGB primaries, UV reactive, cyberpunk",
        "camera": "Locked-off symmetry, macro (circuitry/liquid), time-lapse, robotic",
        "lighting": "LED, projection mapping, laser, strobe, blacklight UV",
        "texture": "Clean digital, glitch artifacts, pixel, holographic, glass",
        "environment": "Club, warehouse rave, futuristic set, void/infinite space",
        "wardrobe": "Reflective, chrome, transparent, LED-embedded, minimal",
        "vfx": "Particle systems, data visualization, glitch, datamosh, projection mapping",
    },
    "folk": {
        "cn": "民谣",
        "palette": "Natural, earthy tones, golden hour, warm film stock",
        "camera": "Handheld intimate, 50mm prime, natural light motivated, gentle dolly",
        "lighting": "Golden hour, candle/fire, window light, overcast soft",
        "texture": "Super 16mm grain, warm analog, soft focus edges, vintage",
        "environment": "Forest, field, cabin, roadside, kitchen table, single location",
        "wardrobe": "Flannel, knitwear, worn boots, natural fabrics, lived-in",
        "vfx": "Minimal to none, maybe super 8 overlay, dust particles, rain",
    },
    "classical": {
        "cn": "古典",
        "palette": "Rich, deep, renaissance palette, chiaroscuro",
        "camera": "Elegant crane, smooth dolly, locked-off symmetry, long takes",
        "lighting": "Rembrandt, chiaroscuro, candle/chandelier, stained glass",
        "texture": "35mm or large format, grain-free clarity, painterly depth",
        "environment": "Concert hall, cathedral, garden, library, palatial interior",
        "wardrobe": "Formal, flowing gowns, tailored suits, timeless elegance",
        "vfx": "Minimal, perhaps time-lapse of nature, slow-mo fabric, particle dust",
    },
    "rnb": {
        "cn": "R&B",
        "palette": "Warm amber, purple/violet, moody tones, intimate shadows",
        "camera": "Close-ups, slow push in, shallow DOF, body-focused framing",
        "lighting": "Warm practicals, neon glow, soft top light, skin-flattering",
        "texture": "Smooth, skin-focused, warm grain, anamorphic bokeh",
        "environment": "Bedroom, luxury bath, penthouse, rain-soaked street, car interior",
        "wardrobe": "Silk, satin, bodycon, jewelry, sensual but tasteful",
        "vfx": "Soft slow-mo, rain drops, candle flicker, lens fog, warm overlays",
    },
    "metal": {
        "cn": "金属",
        "palette": "Black, blood red, chrome silver, cold blue, fire orange",
        "camera": "Aggressive handheld, crash zoom, fish-eye, GoPro on instruments, drone dive",
        "lighting": "Hard underlight, fire/pyro, strobe, laser, UV, fog machine",
        "texture": "High contrast, crushed blacks, digital sharp or deliberately degraded",
        "environment": "Stage pit, abandoned factory, battlefield, forest, dungeon",
        "wardrobe": "Black leather, spikes, corpse paint, armor, chains, boots",
        "vfx": "Fire, smoke, slow-mo destruction, time ramp, inverted colors, multi-exposure",
    },
}

# --- MV 导演签名 ---
MV_DIRECTOR_SIGNATURES = {
    "Hype Williams": {
        "signature": "Extreme wide angle, fisheye distortion, luxury excess",
        "techniques": [
            "Ultra-wide fisheye lens (14mm or wider) as primary optic",
            "Cars, jewelry, and champagne as visual currency",
            "Slow-mo power walk, low-angle hero shots",
            "High-saturation color grading, often monochromatic scenes",
            "Anamorphic stretch and warp effects",
        ],
        "visual_motifs": "Fisheye faces, liquid gold, chrome surfaces, money as texture",
        "era": "1990s-2000s hip-hop golden age",
        "reference_works": "Missy Elliott 'The Rain', Busta Rhymes 'Put Your Hands', Beyonce/Jay-Z 'Crazy in Love'",
    },
    "Michel Gondry": {
        "signature": "Handmade effects, stop motion, practical tricks, in-camera magic",
        "techniques": [
            "In-camera practical effects (no CGI, all physical)",
            "Stop-motion animation integrated with live action",
            "Forced perspective and miniature sets",
            "One-take illusions with set transformations",
            "Cardboard/paper/fabric as world-building material",
        ],
        "visual_motifs": "Handmade worlds, Lego bricks, paper craft, childhood bedroom",
        "era": "1990s-2010s art-pop",
        "reference_works": "The White Stripes 'Fell in Love', Chemical Brothers 'Star Guitar', Bjork 'Human Behaviour'",
    },
    "Spike Jonze": {
        "signature": "Surreal narrative, emotional depth, one-take wonder, hidden sadness",
        "techniques": [
            "Absurd premise played with complete sincerity",
            "Long single-take dance or movement sequences",
            "Real locations with surreal intrusions",
            "Emotional subtlety beneath comedic surface",
            "Amateur or found-footage aesthetic as deliberate choice",
        ],
        "visual_motifs": "Dancing in unexpected places, costumes that reveal character, mundane magic",
        "era": "1990s-2020s",
        "reference_works": "Fatboy Slim 'Weapon of Choice', Bjork 'It's Oh So Quiet', Beastie Boys 'Sabotage'",
    },
    "David Fincher": {
        "signature": "Dark precision, narrative-driven, technical perfection, controlled dread",
        "techniques": [
            "Precisely choreographed camera moves (often impossible shots via motion control)",
            "Dark, desaturated palette with selective color",
            "Narrative complexity compressed into 4 minutes",
            "Perfect lip-sync integration into cinematic storytelling",
            "Industrial/mechanical visual metaphors",
        ],
        "visual_motifs": "Rain, shadow, industrial texture, the face half-lit, mechanical precision",
        "era": "1980s-1990s (pre-feature era)",
        "reference_works": "Madonna 'Express Yourself', Madonna 'Vogue', Aerosmith 'Janie's Got a Gun'",
    },
    "Anton Corbijn": {
        "signature": "Black & white, stark landscapes, cinematic, band documentary feel",
        "techniques": [
            "High-contrast black & white as primary aesthetic",
            "Stark European landscapes (desert, coastal, industrial)",
            "Slow, deliberate pacing even on uptempo songs",
            "Band members as cinematic characters, not just performers",
            "Grain, texture, and analog imperfection as emotional language",
        ],
        "visual_motifs": "Silhouettes against sky, lone figure in landscape, European austerity, monochrome grain",
        "era": "1980s-2010s post-punk/alternative",
        "reference_works": "Depeche Mode 'Enjoy the Silence', U2 'One', Joy Division 'Atmosphere'",
    },
}


def _get_bpm_tier(bpm):
    """Map BPM to editing tier key."""
    if bpm < 80:
        return "slow"
    elif bpm < 120:
        return "moderate"
    elif bpm < 160:
        return "fast"
    else:
        return "extreme"


def _parse_music_genre_key(genre_str):
    """Extract the English genre key from the Chinese+English label."""
    mapping = {
        "流行 (Pop)": "pop", "摇滚 (Rock)": "rock", "嘻哈 (Hip-Hop)": "hiphop",
        "电子 (Electronic)": "electronic", "民谣 (Folk)": "folk",
        "古典 (Classical)": "classical", "R&B": "rnb", "金属 (Metal)": "metal",
    }
    return mapping.get(genre_str, "pop")


def _parse_mv_concept_key(concept_str):
    """Extract the English concept key from the Chinese+English label."""
    mapping = {
        "叙事型 (Narrative)": "narrative", "表演型 (Performance)": "performance",
        "概念型 (Concept)": "concept", "混合型 (Hybrid)": "hybrid",
    }
    return mapping.get(concept_str, "hybrid")


def _infer_music_genre_from_scene(scene, mood):
    """Heuristic: infer music genre from scene/mood text."""
    text = (scene + " " + mood).lower()
    if any(w in text for w in ["摇滚", "rock", "吉他", "guitar", "车库", "garage"]):
        return "rock"
    if any(w in text for w in ["嘻哈", "hip", "rap", "街头", "urban"]):
        return "hiphop"
    if any(w in text for w in ["电子", "electro", "neon", "club", "rave"]):
        return "electronic"
    if any(w in text for w in ["民谣", "folk", "田野", "吉他弹唱", "木吉他"]):
        return "folk"
    if any(w in text for w in ["古典", "classical", "交响", "弦乐"]):
        return "classical"
    if any(w in text for w in ["r&b", "节奏布鲁斯", "灵魂", "soul"]):
        return "rnb"
    if any(w in text for w in ["金属", "metal", "重型", "death"]):
        return "metal"
    return "pop"


def _infer_mv_concept_from_scene(scene, mood):
    """Heuristic: infer MV concept from scene/mood text."""
    text = (scene + " " + mood).lower()
    if any(w in text for w in ["故事", "叙事", "narrative", "剧情", "角色"]):
        return "narrative"
    if any(w in text for w in ["舞台", "表演", "performance", "演唱", "乐队", "舞蹈"]):
        return "performance"
    if any(w in text for w in ["抽象", "概念", "concept", "实验", "艺术"]):
        return "concept"
    return "hybrid"


# ============================================================
# MvPro ComfyUI Node
# ============================================================

class MvPro:
    """
    MV 导演专家节点 (环节 39)
    基于音乐结构/BPM/类型/MV 概念, 生成专业 MV 导演级 H3 Prompt.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "MV"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                # Phase 17.6 灵魂注入
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                # --- MV 专属参数 ---
                "音乐类型": (MUSIC_GENRES, {"default": "auto"}),
                "MV概念": (MV_CONCEPTS, {"default": "auto"}),
                "BPM": ("INT", {"default": 120, "min": 60, "max": 200, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("mvpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_mv"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_mv(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # --- 提取用户输入 ---
        def _str(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "MV")
        scene = _str(kwargs.get("场景描述"), "")
        director = _str(kwargs.get("导演风格"), "是枝裕和")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        bpm = int(kwargs.get("BPM", 120))

        # MV 专属: 音乐类型 + MV 概念
        music_genre_raw = _str(kwargs.get("音乐类型"), "auto")
        mv_concept_raw = _str(kwargs.get("MV概念"), "auto")

        if music_genre_raw == "auto":
            music_genre_key = _infer_music_genre_from_scene(scene, mood)
        else:
            music_genre_key = _parse_music_genre_key(music_genre_raw)

        if mv_concept_raw == "auto":
            mv_concept_key = _infer_mv_concept_from_scene(scene, mood)
        else:
            mv_concept_key = _parse_mv_concept_key(mv_concept_raw)

        genre_visual = GENRE_VISUAL_CODES.get(music_genre_key, GENRE_VISUAL_CODES["pop"])
        mv_type = MV_TYPE_ROUTING.get(mv_concept_key, MV_TYPE_ROUTING["hybrid"])
        bpm_tier_key = _get_bpm_tier(bpm)
        bpm_tier = BPM_EDITING_MAP[bpm_tier_key]

        # --- 导演风格 -> 镜头运动 ---
        director_motion_map = {
            "塔可夫斯基": "Static Shot 长镜 + Slow Push In (冥想式)",
            "王家卫": "Push In 慢推 + Step Printing + 跳切 (时间碎片化)",
            "诺兰": "IMAX Tracking Shot + 时间折叠剪辑 (非线性)",
            "是枝裕和": "Static Shot 静观 + Push In 缓推 (日常诗意)",
            "侯孝贤": "Static Shot 远景长镜 + 留白 (空间呼吸)",
            "黑泽明": "Wide Shot + 群像调度 + 经典构图",
            "库布里克": "Symmetrical Tracking + 一点透视 (不安的精确)",
            "蔡明亮": "Static Shot 超长 + 完全不动 (时间本身)",
            "毕赣": "Arc Shot 环绕 + 长镜头 (梦境漫游)",
            "周星驰": "Quick Cut 快速切换 + 戏谑节奏 (喜剧时机)",
            "大衛·芬奇": "Motion Control Tracking + 暗调精确 (机械美学)",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + Push In 缓推")

        # --- 导演档案 (从 director_data_unified) ---
        director_profile_str = ""
        if _HAS_DIRECTOR_DATA:
            profile = get_director(director)
            director_profile_str = (
                "  镜头: " + str(profile.get("镜头", "")) + "\n"
                "  光: " + str(profile.get("光", "")) + "\n"
                "  节奏: " + str(profile.get("节奏", "")) + "\n"
                "  色彩: " + str(profile.get("色彩", "")) + "\n"
                "  构图: " + str(profile.get("构图", "")) + "\n"
                "  声音: " + str(profile.get("声音", "")) + "\n"
                "  情绪: " + str(profile.get("情绪", "")) + "\n"
                "  代表作: " + str(profile.get("代表作", "")) + "\n"
                "  物件: " + str(profile.get("物件", "")) + "\n"
            )

        # === 音乐结构 -> 视觉结构 7 段式 Shot 生成 ===
        beat_interval = 60.0 / max(bpm, 1)
        cuts_per_chorus_beat = 1 if bpm_tier_key in ("slow", "moderate") else (2 if bpm_tier_key == "fast" else 4)

        style = genre_visual.get("palette", "Cinematic, music video")
        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        # Build section-by-section shots following music structure
        intro_section = MUSIC_VISUAL_STRUCTURE["intro"]
        verse1_section = MUSIC_VISUAL_STRUCTURE["verse_1"]
        prechorus_section = MUSIC_VISUAL_STRUCTURE["pre_chorus"]
        chorus_section = MUSIC_VISUAL_STRUCTURE["chorus"]
        verse2_section = MUSIC_VISUAL_STRUCTURE["verse_2"]
        bridge_section = MUSIC_VISUAL_STRUCTURE["bridge"]
        finale_section = MUSIC_VISUAL_STRUCTURE["final_chorus_outro"]

        shot_1 = (
            "a " + genre_visual.get("camera", "dolly") + " establishes the MV world. "
            + style + ". " + genre_visual.get("environment", "studio") + " environment. "
            + "The " + director_motion_pref.split(" ")[0] + " " + director_motion_pref.split(" ")[-1]
            + " reveals the scene - " + scene + ". "
            + "The " + first_prop + " is visible in frame as a visual anchor. "
            + "Lighting: " + genre_visual.get("lighting", "natural") + ". "
            + "Wardrobe: " + genre_visual.get("wardrobe", "appropriate") + ". "
            + "BPM=" + str(bpm) + " (" + bpm_tier["range"] + "), cutting rhythm: " + bpm_tier["cut_rhythm"] + "."
        )

        shots = []
        # Shot 2: Intro -> Verse 1 transition
        shots.append(
            "[Shot 2 - INTRO " + intro_section["time"] + "] "
            + intro_section["visual"] + ". "
            + "Camera: " + intro_section["camera"] + ". "
            + "The energy level is low (" + str(intro_section["energy"]) + "), establishing tone before the vocal entry. "
            + bpm_tier["transitions"] + " transitions. "
            + "The " + first_prop + " enters frame, grounding the scene."
        )
        # Shot 3: Verse 1 - character/story introduction
        shots.append(
            "[Shot 3 - VERSE 1 " + verse1_section["time"] + "] "
            + verse1_section["visual"] + ". "
            + "Camera: " + verse1_section["camera"] + ". "
            + "MV type [" + mv_type["cn"] + "]: " + mv_type["structure"] + ". "
            + "The mood is " + mood + ". "
            + "Subtext: " + subtext + ". "
            + "Editing: " + verse1_section["editing"] + " at " + str(bpm) + " BPM."
        )
        # Shot 4: Pre-chorus energy build
        shots.append(
            "[Shot 4 - PRE-CHORUS " + prechorus_section["time"] + "] "
            + prechorus_section["visual"] + ". "
            + "Camera: " + prechorus_section["camera"] + ". "
            + "Energy escalates from " + str(verse1_section["energy"]) + " to " + str(prechorus_section["energy"]) + ". "
            + "Beat interval: " + "{:.2f}".format(beat_interval) + "s, cuts tightening. "
            + "The " + last_prop + " becomes narratively significant."
        )
        # Shot 5: Chorus - peak energy
        shots.append(
            "[Shot 5 - CHORUS " + chorus_section["time"] + "] "
            + chorus_section["visual"] + ". "
            + "Camera: " + chorus_section["camera"] + ". "
            + "PEAK ENERGY (" + str(chorus_section["energy"]) + "). "
            + cuts_per_chorus_beat.__str__() + " cuts per beat at " + str(bpm) + " BPM. "
            + "Director intent: " + intent_feel + ". "
            + "Genre visual code: " + genre_visual.get("vfx", "standard") + "."
        )
        # Shot 6: Bridge - visual contrast
        shots.append(
            "[Shot 6 - BRIDGE " + bridge_section["time"] + "] "
            + bridge_section["visual"] + ". "
            + "Camera: " + bridge_section["camera"] + ". "
            + "CONTRAST moment - break all visual rules established so far. "
            + "Energy: " + str(bridge_section["energy"]) + ". "
            + "The " + first_prop + " transforms or reveals new meaning."
        )
        # Shot 7: Final chorus + outro
        shots.append(
            "[Shot 7 - FINAL CHORUS+OUTRO " + finale_section["time"] + "] "
            + finale_section["visual"] + ". "
            + "Camera: " + finale_section["camera"] + ". "
            + "All visual elements converge - " + scene + " + " + props + ". "
            + "Energy: " + str(finale_section["energy"]) + " then fade. "
            + "End on: the " + last_prop + " in static frame, 3 seconds of breathing room."
        )

        # Soundscape from genre
        soundscape = (
            "Music-driven soundscape at " + str(bpm) + " BPM (" + genre_visual["cn"] + "). "
            + "Genre texture: " + genre_visual.get("texture", "standard") + ". "
            + "Environment: " + genre_visual.get("environment", "studio") + " ambient. "
            + "Foley: " + props.replace(" / ", " interacts with ") + " as rhythmic accent."
        )
        music = (
            "MV genre: " + genre_visual["cn"] + " at " + str(bpm) + " BPM. "
            + "Structure follows 7-section mapping (Intro/V1/Pre-C/Chorus/V2/Bridge/Final). "
            + "Reference energy curve: " + bpm_tier["reference"] + "."
        )

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=7, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 30 秒场景单元
        timeline_30s = build_30s_timeline(
            scene_type="MV", scene_desc=scene,
            speaker_id="S1", speaker_voice="vocal performance synced to " + str(bpm) + " BPM",
            dialogue="(lip-sync)", n_lines=1, director_intent=intent_feel, language="Chinese"
        )

        # 5 要素注入
        data_summary = (
            "35 导演 8 维真实档案 + 100 场景 + 30 名言 + "
            + "MV 7 段音乐结构映射 + 4 档 BPM 剪辑节奏 + "
            + "4 种 MV 类型路由 + 8 种音乐类型视觉编码 + "
            + "5 位 MV 大师签名 + 191 反 AI 词表"
        )
        context_brief = (
            "音乐类型=" + genre_visual["cn"] + ", MV概念=" + mv_type["cn"]
            + ", BPM=" + str(bpm) + " (" + bpm_tier["range"] + ")"
            + ", 导演=" + director + ", 场景=" + scene[:50] + "..."
        )
        skill_harness = (
            "MV 7 段音乐->视觉映射 + BPM 4 档剪辑 + MV 4 型路由 + "
            + "8 音乐类型视觉编码 + 5 MV 大师签名 + "
            + "13 镜头运动 + 11 规则 + 9 维光照"
        )
        experience_str = (
            "Hype Williams 鱼眼奢华 + Michel Gondry 手工奇迹 + "
            + "Spike Jonze 荒诞真诚 + David Fincher 暗调精密 + "
            + "Anton Corbijn 黑白荒原 + 35 导演 8 维档案"
        )
        ai_deep = (
            "BPM=" + str(bpm) + " -> 剪辑节奏=" + bpm_tier["cut_rhythm"]
            + " + 音乐结构 7 段视觉映射 + MV 类型 [" + mv_type["cn"] + "] 专属路由"
            + " + 反 AI 词表 + 10 铁律"
        )

        elements_block = inject_5_elements(data_summary, context_brief, skill_harness, experience_str, ai_deep)

        # 导演意图 5 维
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "音乐与画面的共振 - 节拍即剪辑, 旋律即运镜",
            "主题": mood,
            "留白": "歌词没说的, 画面说; 画面没说的, 剪辑节奏说",
        }
        intent_block = inject_director_intent(intent_5d)

        director_control = inject_director_control_11()
        h3_rules = inject_h3_rules_11()

        timeline_30s_lines = "\n".join([
            "  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc
            for (ts, te, stage, desc) in SCENE_UNIT_30S
        ])

        sft_quotes = (
            "\n  - 卡兹克 (2.5 升级): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "")
            + "\n  - 卡兹克 (30 秒场景): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "")
            + "\n  - DiDi_OK (美术优先): " + SEEDANCE_25_QUOTES.get("DiDi_OK_美术", "")
        )

        # === 灵魂注入 ===
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")
        soul_header = ""
        if _HAS_SOUL:
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_scene_weight,
                    secondary=soul_secondary,
                    fusion_mode=soul_fusion_mode,
                    scene_context=scene,
                )
                soul_header = (
                    "【灵魂核心 - MV 导演驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        # === 组装主输出 ===
        main_output = "=" * 60 + "\n"
        main_output += soul_header
        main_output += "【MvPro】MV 导演专家节点 - 音乐视觉化引擎\n"
        main_output += "=" * 60 + "\n\n"

        # MV 专属: 音乐参数总览
        main_output += "【MV 核心参数】\n"
        main_output += "  音乐类型: " + genre_visual["cn"] + " (" + music_genre_key + ")\n"
        main_output += "  MV 概念: " + mv_type["cn"] + " (" + mv_concept_key + ")\n"
        main_output += "  BPM: " + str(bpm) + " (" + bpm_tier["range"] + ")\n"
        main_output += "  节拍间隔: " + "{:.3f}".format(beat_interval) + "s\n"
        main_output += "  剪辑节奏: " + bpm_tier["cut_rhythm"] + "\n"
        main_output += "  转场方式: " + bpm_tier["transitions"] + "\n"
        main_output += "  运镜风格: " + bpm_tier["camera_style"] + "\n"
        main_output += "  参考: " + bpm_tier["reference"] + "\n\n"

        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + " - " + director_motion_pref + "\n"
        if director_profile_str:
            main_output += "【导演档案 (35 导演 8 维)】\n" + director_profile_str + "\n"

        # MV 类型路由详情
        main_output += "=" * 60 + "\n"
        main_output += "MV 类型路由: " + mv_type["cn"] + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  结构: " + mv_type["structure"] + "\n"
        for i, elem in enumerate(mv_type["key_elements"], 1):
            main_output += "  " + str(i) + ". " + elem + "\n"
        main_output += "  运镜: " + mv_type["camera_approach"] + "\n"
        main_output += "  剪辑哲学: " + mv_type["editing_philosophy"] + "\n"
        main_output += "  灯光: " + mv_type["lighting"] + "\n"
        main_output += "  参考 MV: " + mv_type["reference_mvs"] + "\n\n"

        # 音乐类型视觉编码
        main_output += "=" * 60 + "\n"
        main_output += "音乐类型视觉编码: " + genre_visual["cn"] + "\n"
        main_output += "=" * 60 + "\n\n"
        for k, v in genre_visual.items():
            if k != "cn":
                main_output += "  " + k + ": " + v + "\n"
        main_output += "\n"

        # 音乐结构 -> 视觉结构 7 段式
        main_output += "=" * 60 + "\n"
        main_output += "音乐结构 -> 视觉结构 7 段式 (BPM=" + str(bpm) + ")\n"
        main_output += "=" * 60 + "\n\n"
        for section_key, section in MUSIC_VISUAL_STRUCTURE.items():
            main_output += "  [" + section_key.upper() + "] " + section["time"] + " (energy=" + str(section["energy"]) + ")\n"
            main_output += "    音乐: " + section["music_role"] + "\n"
            main_output += "    视觉: " + section["visual"] + "\n"
            main_output += "    运镜: " + section["camera"] + "\n"
            main_output += "    剪辑: " + section["editing"] + "\n"
            main_output += "    " + section["description"] + "\n\n"

        # H3 三大字段
        main_output += "=" * 60 + "\n"
        main_output += "H3 三大字段 (MiniMax-H3 官方格式)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_prompt + "\n\n"

        # 30 秒场景单元
        main_output += "=" * 60 + "\n"
        main_output += "30 秒场景单元 6 段式 (卡兹克)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        # 导演意图 5 维
        main_output += "=" * 60 + "\n"
        main_output += "导演意图 5 维 (MV 语境)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += intent_block + "\n\n"

        # 导演控制 + H3 规则
        main_output += "=" * 60 + "\n"
        main_output += director_control + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "=" * 60 + "\n"
        main_output += h3_rules + "\n"
        main_output += "=" * 60 + "\n\n"

        # Seedance 引用
        main_output += "=" * 60 + "\n"
        main_output += "Seedance 2.5 核心升级 (卡兹克)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += sft_quotes + "\n\n"

        # 5 要素
        main_output += "=" * 60 + "\n"
        main_output += elements_block + "\n"
        main_output += "=" * 60 + "\n"

        # 反 AI 处理
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # === 第二个输出: 经验矩阵 (MV 专业化) ===
        experience = "【MV 导演大师签名库 (5 位)】\n\n"
        for name, sig in MV_DIRECTOR_SIGNATURES.items():
            experience += "  " + name + ": " + sig["signature"] + "\n"
            for tech in sig["techniques"]:
                experience += "    - " + tech + "\n"
            experience += "    视觉母题: " + sig["visual_motifs"] + "\n"
            experience += "    时代: " + sig["era"] + "\n"
            experience += "    代表作: " + sig["reference_works"] + "\n\n"

        experience += "【BPM 剪辑节奏对照表】\n\n"
        for tier_name, tier_data in BPM_EDITING_MAP.items():
            experience += "  " + tier_name.upper() + " (" + tier_data["range"] + ")\n"
            experience += "    切点: " + tier_data["cut_rhythm"] + "\n"
            experience += "    转场: " + tier_data["transitions"] + "\n"
            experience += "    运镜: " + tier_data["camera_style"] + "\n"
            experience += "    感受: " + tier_data["energy_feel"] + "\n"
            experience += "    参考: " + tier_data["reference"] + "\n\n"

        experience += "【20 导演集群】\n"
        for d in DIRECTORS_20:
            experience += "  - " + d + "\n"
        experience += "\n【9 大影视类型 + 5 要素处理】\n"
        experience += inject_genre_9_types() + "\n"
        experience += "【11 维导演控制能力 (人类顶级导演)】\n"
        experience += inject_director_control_11() + "\n"
        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # === 第三个输出: AI 深度处理 (MV 专业化) ===
        ai_deep_output = "【MV 音乐结构 -> 视觉结构映射原理】\n\n"
        ai_deep_output += "核心原则: 音乐的能量曲线 = 视觉的能量曲线\n"
        ai_deep_output += "  Intro(0.2) -> V1(0.4) -> PreC(0.6) -> Chorus(1.0) -> V2(0.5) -> Bridge(0.7) -> Final(0.9->fade)\n\n"
        ai_deep_output += "BPM 决定剪辑密度:\n"
        ai_deep_output += "  当前 BPM=" + str(bpm) + " -> 档位=" + bpm_tier_key.upper() + "\n"
        ai_deep_output += "  每拍时长: " + "{:.3f}".format(beat_interval) + "s\n"
        ai_deep_output += "  副歌每拍切点数: " + str(cuts_per_chorus_beat) + "\n\n"

        ai_deep_output += "【MV 类型路由逻辑】\n"
        ai_deep_output += "  当前路由: " + mv_type["cn"] + "\n"
        ai_deep_output += "  Verse = " + ("叙事推进" if mv_concept_key in ("narrative", "hybrid") else "视觉呈现") + "\n"
        ai_deep_output += "  Chorus = " + ("表演能量" if mv_concept_key in ("performance", "hybrid") else "概念爆发") + "\n"
        ai_deep_output += "  Bridge = " + ("叙事高潮/转折" if mv_concept_key == "narrative" else "视觉反差") + "\n\n"

        ai_deep_output += "【音乐类型视觉编码原理】\n"
        ai_deep_output += "  当前类型: " + genre_visual["cn"] + "\n"
        ai_deep_output += "  色彩: " + genre_visual.get("palette", "") + "\n"
        ai_deep_output += "  质感: " + genre_visual.get("texture", "") + "\n"
        ai_deep_output += "  VFX: " + genre_visual.get("vfx", "") + "\n\n"

        ai_deep_output += "【191 反 AI 词表 + 4 轮迭代】\n"
        ai_deep_output += "瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词\n\n"
        ai_deep_output += "【沉默 5 规则 + 4 步公式 + 30 秒场景单元】\n"
        ai_deep_output += inject_silence_mastery_5("MV", 1) + "\n\n"
        ai_deep_output += "【9 维光照控制 (CIE LAB + 摄影本体)】\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "MvPro": MvPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "MvPro": "MV 导演 (环节 39) — L5 重写",
# }
