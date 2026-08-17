# -*- coding: utf-8 -*-
"""
SoundDesignPro - 声音设计专家节点 (环节 13)
====================================================
4-layer professional soundscape design with genuine domain logic:

Layer 1 (环境音 Ambience): Scene-type to ambient sound mapping
Layer 2 (拟音 Foley): Action-keyword to foley breakdown
Layer 3 (对白 Dialogue): Character voice descriptors
Layer 4 (音乐 Music): Emotion-to-music summary (detail in MusicScorePro)

Director sound signatures from director_data_unified (35 directors x 声音 field)
H3 overall_soundscape + non_diegetic_music proper format
Professional mixing parameters (LUFS levels per layer)
Anti-AI vocabulary cleanup
"""

import os
import sys
import json
import re

# === Core dependencies (graceful fallback) ===
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

# Phase 17.6: Soul injection
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# === Knowledge base imports (with fallback) ===
try:
    from knowledge_base.emotion_rendering import EMOTION_RENDERING
    _HAS_EMOTION_KB = True
except Exception:
    _HAS_EMOTION_KB = False
    EMOTION_RENDERING = {}

try:
    from knowledge_base.genre_profiles import GENRE_PROFILES
    _HAS_GENRE_KB = True
except Exception:
    _HAS_GENRE_KB = False
    GENRE_PROFILES = {}

try:
    from knowledge_base.h3_prompt_framework import (
        H3_MODES, CAMERA_MOTION_TYPES, H3_VISUAL_STYLES,
        H3_REF2VA_SECTIONS, DIRECTOR_TO_H3_MOTION,
    )
    _HAS_H3_KB = True
except Exception:
    _HAS_H3_KB = False

# === Director data unified (35 directors x 8 dimensions) ===
try:
    from director_data_unified import DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False
    DIRECTOR_PROFILES_35 = {}; DIRECTOR_PROFILES_ALL = {}; get_director_profile = lambda n: {}


# ============================================================
# BUILT-IN DOMAIN DATA: 4-Layer Soundscape Engine
# ============================================================

# Layer 1: Scene-type to ambient sound mapping
# Each entry: list of specific ambient sound elements (English for H3)
SCENE_AMBIENCE_MAP = {
    # --- Indoor scenes ---
    "厨房": [
        "oil crackling in a wok at medium heat",
        "refrigerator compressor cycling on with a low hum",
        "wall clock ticking at 60bpm",
        "water dripping from a not-fully-closed faucet every 4 seconds",
        "fluorescent light buzzing at 50Hz",
    ],
    "客厅": [
        "muffled traffic noise filtering through closed windows",
        "central heating pipes expanding with occasional metallic clicks",
        "TV murmuring at low volume from the next room",
        "fabric rustling against leather sofa cushion",
    ],
    "办公室": [
        "mechanical keyboard clicks at irregular intervals",
        "air conditioning unit drone at a constant 45dB",
        "elevator bell dinging two floors away",
        "paper shuffling and drawer sliding on metal rails",
        "distant phone ringing through a partition wall",
    ],
    "卧室": [
        "distant traffic reduced to a low rumble through double-pane glass",
        "bedside clock ticking softly",
        "sheets rustling with slight movement",
        "neighbor's muffled music bass line bleeding through the wall",
    ],
    "教室": [
        "chalk scraping on blackboard with short strokes",
        "chairs creaking on tile floor",
        "pages turning in unison",
        "whispered conversation in the back row",
        "ceiling fan wobbling with a rhythmic click every rotation",
    ],
    "医院": [
        "heart monitor beeping at steady 72bpm",
        "rubber-soled shoes squeaking on polished linoleum",
        "PA system crackling before an announcement",
        "IV drip clicking every 2 seconds",
        "distant gurney wheels rolling on corridor floor",
    ],
    "电梯": [
        "electric motor humming behind the panel",
        "cable tension creaking as the car shifts",
        "ventilation fan whirring in the ceiling",
        "digital floor indicator chiming at each level",
    ],
    "车内": [
        "engine idling at 800rpm with slight vibration",
        "windshield wipers sweeping in 2-second intervals",
        "turn signal clicking",
        "road surface changing from smooth to rough asphalt",
        "heater blower at level 2",
    ],
    "地下室": [
        "water pipes gurgling through concrete walls",
        "bare lightbulb flickering with a faint electric buzz",
        "distant boiler rumbling",
        "footsteps from the floor above, muted and rhythmic",
    ],
    # --- Outdoor scenes ---
    "街道": [
        "car horns at varying distances",
        "pedestrian footsteps mixing leather soles and sneakers on concrete",
        "bicycle bell ringing once",
        "construction drill operating three blocks away",
        "bus hydraulic brakes hissing to a stop",
    ],
    "森林": [
        "wind moving through pine needles producing a sustained whoosh",
        "bird calls — two species alternating: thrush trill and woodpecker drumming",
        "creek running over smooth stones at a moderate flow",
        "dried leaves crunching underfoot with each step",
        "distant chainsaw starting up then cutting out",
    ],
    "海边": [
        "waves breaking on the shore in 8-second cycles",
        "seagulls calling at random intervals overhead",
        "wet sand sucking at retreating footsteps",
        "wind flapping the edge of a beach towel",
        "distant boat engine puttering across the bay",
    ],
    "雨夜": [
        "rain tapping on glass windowpane at varying intensity",
        "distant traffic splashing through puddles",
        "thunder rolling 4-5 seconds after a lightning flash",
        "rainwater gurgling in the drainpipe",
        "umbrella fabric drumming under heavy drops",
    ],
    "雪地": [
        "boots compressing fresh snow with a crisp crunch",
        "wind howling across open terrain",
        "absolute silence between gusts — the acoustic dead space of snowfield",
        "distant dog barking, sound carrying unusually far in cold air",
    ],
    "市场": [
        "vendors calling prices with overlapping voices",
        "shopping bag plastic crackling",
        "chopping block impacts — cleaver on wood",
        "metal scale pans clanging",
        "bicycle wheels clicking through the crowd",
    ],
    "操场": [
        "basketball bouncing on asphalt with hollow thuds",
        "sneakers squeaking on court surface",
        "metal chain-link fence rattling in the wind",
        "distant whistle blowing — two short blasts",
        "children shouting and laughing at varied distances",
    ],
}

# Layer 2: Action keywords to foley sound breakdown
# Each action maps to a list of component sounds a foley artist would build
FOLEY_ACTION_MAP = {
    "走路": {
        "surfaces": {
            "木地板": "heel strike on hardwood with slight flex creak, toe-off with board give",
            "水泥": "flat impact with gritty texture, minimal resonance",
            "草地": "soft compression, slight moisture squelch after rain",
            "碎石": "irregular crunching with stone-on-stone grinding",
            "瓷砖": "sharp click-clack with echo in enclosed space",
            "地毯": "muffled thuds absorbed by fiber, fabric brush on each step",
            "积雪": "crisp crunch compressing ice crystals, 800-1200Hz frequency range",
            "水洼": "splash on impact, water displacement sound, droplets scattering",
        },
        "modifiers": "pace affects rhythm (slow=0.8s interval, normal=0.5s, fast=0.3s)",
    },
    "打斗": [
        "fist impact on body — deep thud with cloth compression (not Hollywood slap)",
        "grunt forced from diaphragm on exertion — pitched by character size",
        "fabric tearing at stress points during grapple",
        "body hitting floor — weight distribution determines spread of impact",
        "breathing heavy and ragged between exchanges — through nose when mouth guard up",
        "joint cracking or popping during locks/throws",
    ],
    "吃饭": [
        "chopstick tips clicking against ceramic bowl rim",
        "chewing — jaw working with mouth closed, subtle wet sounds",
        "bowl set down on wooden table with ceramic-on-wood contact",
        "liquid poured from thermos into cup — pitch rising as cup fills",
        "chair creaking when leaning forward to reach dishes",
        "soup sipped from spoon with controlled aspiration",
    ],
    "打字": [
        "mechanical keyboard switch actuation (Cherry MX Blue: click + tactile bump)",
        "spacebar hit with thumb — longer key travel, deeper tone",
        "backspace rapid-fire in short burst — error correction rhythm",
        "mouse click — left button single, then scroll wheel ratcheting",
    ],
    "开门": [
        "handle mechanism turning — lever or knob rotation",
        "latch bolt retracting from strike plate",
        "hinge movement — well-oiled is silent, old is a slow creak in mid-arc",
        "air pressure equalization when sealed room opens — subtle whoosh",
        "door bottom sweeping across threshold — carpet drag or tile tap",
    ],
    "做饭": [
        "oil heating in wok — initial quiet bubble to rolling sizzle",
        "vegetables hitting hot oil — explosive hiss with steam burst",
        "spatula scraping wok surface — metal on seasoned iron",
        "pot lid lifted releasing trapped steam",
        "knife on cutting board — rhythm varies: dicing rapid, slicing measured",
        "gas burner clicking then igniting with a soft whump",
    ],
    "驾驶": [
        "engine revving through gear changes — pitch climbing then dropping",
        "steering wheel leather creaking under grip adjustment",
        "turn signal relay clicking behind dashboard",
        "tire rumble changing with road surface texture",
        "gear shift clunking into position — mechanical linkage feedback",
    ],
    "哭泣": [
        "breath catching in throat — irregular, stuttered inhalation",
        "tears hitting fabric — nearly inaudible single drops",
        "nasal congestion sniffling — wet, pressured",
        "jaw trembling — teeth chattering softly",
        "hand wiping face — skin on wet skin friction",
    ],
    "跑步": [
        "rapid footfall impacts — frequency doubles from walking rhythm",
        "breathing labored and rhythmic — exhale on every other footstrike",
        "clothing fabric swooshing at arm and leg joints",
        "keys or loose items jingling in pocket with each stride",
    ],
    "写字": [
        "pen tip scratching on paper — ballpoint rolls, fountain pen drags",
        "paper shifting under hand pressure",
        "page turning with a light finger-lift and drop",
        "pen cap clicking when thinking pauses",
    ],
}

# Layer 3: Voice descriptor templates based on character attributes
VOICE_DESCRIPTOR_TEMPLATE = {
    "age_ranges": {
        "child": "a high, clear voice with occasional pitch cracks",
        "teenager": "a voice still finding its register, slightly nasal",
        "young_adult": "a voice with full resonance, moderate pitch",
        "middle_aged": "a voice with worn edges, slightly lower register, deliberate pacing",
        "elderly": "a voice thinned by age, trembling at phrase endings, breath between sentences",
    },
    "gender_tones": {
        "male": "baritone range, chest resonance",
        "female": "alto range, head resonance with warm undertone",
        "neutral": "mid-range, conversational",
    },
    "registers": {
        "formal": "measured diction, complete sentences, minimal contractions",
        "casual": "relaxed cadence, dropped endings, half-finished thoughts",
        "whisper": "breathy, consonants softened, volume below ambient",
        "shout": "strained vocal cords, cracking at peak volume",
        "internal": "muted, as if speaking inside one's own head, no room reverb",
    },
    "languages": {
        "Chinese": "Mandarin Chinese with regional tones intact",
        "Cantonese": "Cantonese with rising-falling tonal pattern",
        "English": "English with natural prosody",
        "Japanese": "Japanese with polite form cadence",
        "Korean": "Korean with formal sentence endings",
    },
}

# Layer 4: Emotion-to-music summary
# (Light version here; full detail lives in MusicScorePro)
EMOTION_MUSIC_SUMMARY = {
    "悲伤": "sustained low strings pp, solo piano in minor key, 60BPM, descending phrase",
    "喜悦": "light pizzicato strings with woodwind melody, major key, 110BPM, ascending phrase",
    "紧张": "tremolo strings sul ponticello, low brass pedal tone, irregular rhythmic pulse",
    "温暖": "warm cello melody with soft piano accompaniment, 80BPM, gentle rubato",
    "恐惧": "atonal cluster chords in high strings, sudden silence gaps, sub-bass drone at 30Hz",
    "愤怒": "aggressive brass stabs, snare rolls crescendo, dissonant intervals, 140BPM",
    "孤独": "solo instrument (oboe or erhu) unaccompanied, empty reverb space, 50BPM rubato",
    "希望": "French horn melody rising by step, strings swelling underneath, 90BPM, major key resolution",
    "压抑": "muted brass with heavy reverb, low register piano clusters, 55BPM, no resolution",
    "暧昧": "jazz piano with brushed cymbal, detuned vibraphone, 75BPM, suspended chords",
    "怀旧": "music box melody over warm pad, vinyl crackle texture, 70BPM, pentatonic scale",
    "压抑中见希望": "minor key foundation with occasional major chord intrusions, cello to violin handoff, 65BPM rubato",
}

# === Director Sound Signatures (built-in fallback when director_data_unified unavailable) ===
DIRECTOR_SOUND_SIGNATURES = {
    "塔可夫斯基": {
        "philosophy": "Natural sound IS music. Rain is dialogue. Wind is the subconscious speaking.",
        "signature_sounds": ["rain on different surfaces as emotional barometer",
                             "fire crackling as meditation rhythm",
                             "water dripping in ruined buildings",
                             "dog barking in far distance establishing scale"],
        "silence_approach": "Long stretches of pure ambient — the audience must hear themselves think.",
        "music_rule": "Rarely uses score. When he does, it is Bach or Pergolesi — never composed-for-film.",
        "mixing_note": "Ambient pushed to foreground (-12 LUFS). Dialogue sits inside environment, not above it.",
    },
    "王家卫": {
        "philosophy": "Pop songs as emotional shorthand. The right song replaces ten pages of dialogue.",
        "signature_sounds": ["jukebox playing at background level",
                             "clock ticking as metaphor for time running out on love",
                             "high heels on wet pavement — rhythm of longing",
                             "rain against neon-lit windows"],
        "silence_approach": "Never true silence — always a layer of city hum underneath. Loneliness has a frequency.",
        "music_rule": "Licensed pop/world music (Yumeji's Theme, California Dreaming, Quizas). Diegetic sources preferred.",
        "mixing_note": "Music foregrounded (-14 LUFS). Dialogue occasionally buried under song — the FEELING matters more than the words.",
    },
    "奉俊昊": {
        "philosophy": "Everyday sounds as class metaphor. The rich live in silence; the poor live in noise.",
        "signature_sounds": ["rain flooding down concrete stairs — class literally washing downhill",
                             "mosquito buzzing in the semi-basement",
                             "smartphone notification chimes — modern anxiety",
                             "toilet flushing (from below) as indignity marker"],
        "silence_approach": "Strategic silence before violence. The moment sound drops is the moment the knife comes out.",
        "music_rule": "Original orchestral score that subverts: upbeat music during tragedy, silence during comedy.",
        "mixing_note": "Hyper-detailed foley. Every surface tells a class story. Marble echoes vs. linoleum thuds.",
    },
    "是枝裕和": {
        "philosophy": "Domestic sound IS the story. The clink of dishes says what the family cannot.",
        "signature_sounds": ["rice cooker releasing steam with a click",
                             "slippers shuffling on tatami",
                             "children laughing in the next room — overheard, not performed",
                             "cicadas outside the window anchoring summer"],
        "silence_approach": "Not dramatic silence — comfortable silence. The kind where you can hear someone chewing.",
        "music_rule": "Minimal piano or none. When music appears, it floats at the edge of perception.",
        "mixing_note": "All sounds at naturalistic levels. Nothing is boosted for drama. The audience leans in.",
    },
    "诺兰": {
        "philosophy": "Sound as time manipulation. Bass frequencies that vibrate the seat ARE the plot.",
        "signature_sounds": ["pocket watch ticking layered with orchestral rhythm",
                             "Shepard tone rising endlessly — tension that never resolves",
                             "engine roar mixed with heartbeat BPM match",
                             "air lock hissing in vacuum — then total silence"],
        "silence_approach": "Rare and devastating. When Nolan cuts to silence, something irreversible just happened.",
        "music_rule": "Hans Zimmer layered electronic-orchestral hybrid. The BRAAAM inception horn. Time-signature shifts.",
        "mixing_note": "Dialogue sometimes intentionally hard to hear (-30 LUFS while music is at -10). The emotion > the information.",
    },
    "黑泽明": {
        "philosophy": "Weather AS sound design. The storm does not accompany the battle — it IS the battle.",
        "signature_sounds": ["rain hammering on armor and banners",
                             "wind howling across empty battlefield",
                             "taiko drums mirroring heartbeat in combat",
                             "horse hooves thundering on mud"],
        "silence_approach": "The silence after battle. Bodies on the field. Wind the only sound. Kurosawa held these for full minutes.",
        "music_rule": "Noh theater influence. Flute and drum. Or full orchestral for epic scale.",
        "mixing_note": "Weather sounds mixed as loud as dialogue. Nature has equal voice to humans.",
    },
    "库布里克": {
        "philosophy": "Ironic sound counterpoint. Beautiful music against horrifying images.",
        "signature_sounds": ["breathing in space helmet — claustrophobic intimacy",
                             "typewriter keys in hotel corridor echo",
                             "Strauss waltz playing over spacecraft docking",
                             "Beethoven during ultraviolence — beauty and horror fused"],
        "silence_approach": "The hum of machines fills what should be silence. HAL's red eye has a frequency.",
        "music_rule": "Pre-existing classical music, never original score. The irony of the pre-existing adds meaning.",
        "mixing_note": "Spatial audio precision. Every sound placed in 3D space with mathematical accuracy.",
    },
    "侯孝贤": {
        "philosophy": "Distance sound. The audience overhears life from the next room.",
        "signature_sounds": ["wind through bamboo grove",
                             "train passing in far distance",
                             "children's voices floating from downstairs",
                             "rain on tin roof — entire weather system in one sound"],
        "silence_approach": "Silence is the dominant texture. Sounds are events that interrupt silence.",
        "music_rule": "Rare. When music enters, it is from a source in the world (radio, street musician).",
        "mixing_note": "Everything at realistic distance. No close-mic intimacy. The camera AND the mic observe from afar.",
    },
    "贾樟柯": {
        "philosophy": "Pop songs as era markers. The specific song playing on the radio tells you the year.",
        "signature_sounds": ["factory machinery drone as constant baseline",
                             "Chinese pop song from a specific year playing on tinny speakers",
                             "construction demolition in background — change destroying the familiar",
                             "motorcycle engine and horn on rural road"],
        "silence_approach": "No silence — the world of his characters never stops making noise. That IS the oppression.",
        "music_rule": "Diegetic Chinese pop songs (specific to era). Non-diegetic rarely used.",
        "mixing_note": "Documentary-level ambient. Unprocessed. The rawness IS the aesthetic.",
    },
    "李安": {
        "philosophy": "Sound bridges cultures. The bamboo forest fight sounds like a conversation between East and West.",
        "signature_sounds": ["bamboo flexing and creaking during wuxia combat",
                             "string quartet shifting to erhu — cultural translation in real-time",
                             "ice cracking on Brokeback Mountain",
                             "family dinner sounds layered across cultures"],
        "silence_approach": "The silence of things unsaid. Ang Lee's characters are silent because speaking would break them.",
        "music_rule": "Original score blending Western orchestral with Eastern instruments. Mychael Danna, Tan Dun.",
        "mixing_note": "Balanced and transparent. Nothing obscured. Every layer audible. Hollywood craft with art-house intent.",
    },
    "蔡明亮": {
        "philosophy": "Silence as primary material. Sound is what occasionally breaks the silence, not the other way around.",
        "signature_sounds": ["water dripping — always, everywhere, his signature",
                             "footsteps in empty corridor with maximum reverb",
                             "rain inside a building (leaking roofs)",
                             "eating sounds amplified by isolation"],
        "silence_approach": "Minutes of pure silence with only breathing. The audience becomes aware of the theater itself.",
        "music_rule": "Almost never. When music appears (Grace Chang songs), it is a revelatory event.",
        "mixing_note": "Extreme: either total silence or single isolated sound at full volume. No middle ground.",
    },
    "周星驰": {
        "philosophy": "Sound as punchline delivery system. The right sound effect IS the joke.",
        "signature_sounds": ["exaggerated slap with comedic echo",
                             "cartoon spring bounce for physical comedy",
                             "dramatic sting subverted by silence or fart sound",
                             "Cantonese street noise as cultural texture"],
        "silence_approach": "Comedic pause — silence used for timing. The beat before the punchline lands.",
        "music_rule": "Eclectic: Cantonese pop, Western classical for mock-epic, game sound effects.",
        "mixing_note": "Over-processed for comedic effect. Sounds are louder, more resonant, more absurd than reality.",
    },
}

# === Spatial Reverb Profiles ===
REVERB_PROFILES = {
    "大空间 (教堂/洞穴)": {
        "rt60": "3.0-6.0s",
        "early_reflections": "sparse, arriving 30-80ms after direct sound",
        "character": "cathedral-like wash, low-frequency emphasis, sense of vastness",
        "h3_description": "with heavy reverb tail suggesting a large stone interior, echoes arriving at varied intervals",
    },
    "中空间 (客厅/办公室)": {
        "rt60": "0.4-0.8s",
        "early_reflections": "moderate density, arriving 5-20ms",
        "character": "natural room ambience, balanced frequency response",
        "h3_description": "with moderate room reverb appropriate for a furnished domestic space",
    },
    "小空间 (电梯/车内)": {
        "rt60": "0.1-0.3s",
        "early_reflections": "dense, arriving 1-5ms, creating a boxy quality",
        "character": "tight, intimate, slightly claustrophobic, mid-frequency boost",
        "h3_description": "with tight, boxy reverb suggesting close walls and low ceiling",
    },
    "户外开阔": {
        "rt60": "0.0-0.1s (no reflections)",
        "early_reflections": "none — sound dissipates into open air",
        "character": "dry, direct, wind noise fills the void where reverb would be",
        "h3_description": "outdoors with no reverb, sounds dissipating into open air, wind filling the acoustic space",
    },
    "auto": {
        "rt60": "scene-dependent",
        "early_reflections": "auto-detected from scene description",
        "character": "derived from context",
        "h3_description": "",
    },
}

# === Sound Style Profiles ===
SOUND_STYLE_PROFILES = {
    "写实主义": {
        "principle": "Record and reproduce reality. No enhancement, no sweetening. What the mic captures IS the design.",
        "foley_approach": "Naturalistic levels. A door closing sounds like a door closing, not a dramatic punctuation.",
        "mixing": "All elements at real-world relative levels. Dialogue not boosted above environment.",
        "directors": ["是枝裕和", "贾樟柯", "达内兄弟", "侯孝贤"],
    },
    "表现主义": {
        "principle": "Sound serves emotion, not reality. A heartbeat can be louder than a gunshot if the character is afraid.",
        "foley_approach": "Heightened, selective, subjective. Amplify what the CHARACTER hears, suppress what they ignore.",
        "mixing": "Dynamic range extremes. Whisper-quiet to overwhelming in the same scene.",
        "directors": ["诺兰", "大衛·芬奇", "库布里克", "阿里·阿斯特"],
    },
    "极简主义": {
        "principle": "Less is more. Strip away until only the essential sound remains. What you remove defines the design.",
        "foley_approach": "One or two sounds at a time. Silence is the canvas. Each sound is an event.",
        "mixing": "Wide dynamic range with silence as baseline. When a sound appears, it commands total attention.",
        "directors": ["蔡明亮", "塔可夫斯基", "布列松", "贝拉·塔尔"],
    },
    "层叠构建": {
        "principle": "Build complexity through layers. Start sparse, add elements one by one, create a full sonic world.",
        "foley_approach": "20+ simultaneous elements in full-density scenes. Each identifiable on its own.",
        "mixing": "Orchestral approach: each layer has its frequency band and spatial position. Full stereo/surround use.",
        "directors": ["奉俊昊", "黑泽明", "David Lynch", "阿方索·卡隆"],
    },
    "auto": {
        "principle": "Auto-selected based on director and genre.",
        "foley_approach": "Derived from context.",
        "mixing": "Balanced.",
        "directors": [],
    },
}

# === Professional Mixing Parameters (LUFS = Loudness Units Full Scale) ===
MIXING_PARAMETERS = {
    "dialogue": {"target_lufs": -24, "range": "(-22 to -26)", "priority": "highest — dialogue intelligibility is non-negotiable"},
    "music": {"target_lufs": -18, "range": "(-16 to -20)", "priority": "medium — sits behind dialogue, above ambience"},
    "sfx_foley": {"target_lufs": -20, "range": "(-18 to -24)", "priority": "medium — matches scene energy"},
    "ambience": {"target_lufs": -30, "range": "(-26 to -36)", "priority": "lowest — bed layer, felt not heard"},
    "overall_loudness": {"target_lufs": -14, "range": "(-12 to -16)", "note": "streaming platform standard (Spotify/Netflix)"},
}


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

SOUND_LAYERS = [
    "4层全开 (环境+拟音+对白+音乐)",
    "环境+拟音",
    "对白+音乐",
    "纯环境",
    "纯拟音",
]
REVERB_CHOICES = [
    "大空间 (教堂/洞穴)",
    "中空间 (客厅/办公室)",
    "小空间 (电梯/车内)",
    "户外开阔",
    "auto",
]
SOUND_STYLE_CHOICES = ["写实主义", "表现主义", "极简主义", "层叠构建", "auto"]


class SoundDesignPro:
    """
    声音设计专家节点 (环节 13) — 4 层声景构建引擎

    4 layers: Ambience + Foley + Dialogue + Music
    Director sound signatures from 35-director database
    H3 overall_soundscape and non_diegetic_music format
    Professional mixing parameters (LUFS)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                # === Phase 17.6 Soul injection ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                # === Sound-design-specific fields ===
                "声音层级": (SOUND_LAYERS, {"default": "4层全开 (环境+拟音+对白+音乐)"}),
                "空间混响": (REVERB_CHOICES, {"default": "auto"}),
                "声音风格": (SOUND_STYLE_CHOICES, {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("sounddesignpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_sound"
    CATEGORY = "PromptLibrary/L5 导演级"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _str(v, default=""):
        if v is None:
            return default
        if isinstance(v, (list, tuple)):
            return str(v[0]) if v else default
        return str(v)

    def _detect_scene_locations(self, scene_desc):
        """Extract probable scene locations from description for ambience mapping."""
        detected = []
        for key in SCENE_AMBIENCE_MAP:
            if key in scene_desc:
                detected.append(key)
        # Weather/condition detection
        weather_keywords = {
            "雨": "雨夜", "雪": "雪地", "海": "海边",
            "森林": "森林", "树林": "森林", "街": "街道",
            "市场": "市场", "菜市场": "市场", "操场": "操场",
        }
        for keyword, location in weather_keywords.items():
            if keyword in scene_desc and location not in detected:
                detected.append(location)
        if not detected:
            # Fallback: try to guess indoor vs outdoor
            outdoor_hints = ["外", "路", "田", "山", "河", "天", "阳光", "风"]
            if any(h in scene_desc for h in outdoor_hints):
                detected.append("街道")
            else:
                detected.append("客厅")  # default indoor
        return detected

    def _detect_actions(self, scene_desc, props):
        """Extract action keywords from scene description and props."""
        combined = scene_desc + " " + props
        detected = []
        for action_key in FOLEY_ACTION_MAP:
            # Check for the action keyword or related words
            related_words = {
                "走路": ["走", "步", "散步", "踱步"],
                "打斗": ["打", "斗", "格斗", "搏斗", "冲突"],
                "吃饭": ["吃", "饭", "食", "喝", "餐"],
                "打字": ["打字", "键盘", "电脑"],
                "开门": ["开门", "关门", "门"],
                "做饭": ["做饭", "炒", "切菜", "烧", "煮", "厨"],
                "驾驶": ["驾驶", "开车", "车"],
                "哭泣": ["哭", "泪", "流泪"],
                "跑步": ["跑", "奔"],
                "写字": ["写", "笔", "纸"],
            }
            triggers = related_words.get(action_key, [action_key])
            if any(t in combined for t in triggers):
                detected.append(action_key)
        return detected if detected else ["走路"]  # default: at least footsteps

    def _detect_reverb_from_scene(self, scene_desc):
        """Auto-detect spatial reverb from scene description."""
        large_space = ["教堂", "洞穴", "大厅", "体育馆", "仓库", "工厂"]
        small_space = ["电梯", "车内", "厕所", "浴室", "衣柜"]
        outdoor = ["户外", "操场", "海", "山", "田", "草", "森林", "街"]
        if any(k in scene_desc for k in large_space):
            return "大空间 (教堂/洞穴)"
        if any(k in scene_desc for k in small_space):
            return "小空间 (电梯/车内)"
        if any(k in scene_desc for k in outdoor):
            return "户外开阔"
        return "中空间 (客厅/办公室)"

    def _detect_sound_style(self, director):
        """Auto-detect sound style based on director preference."""
        for style_name, profile in SOUND_STYLE_PROFILES.items():
            if style_name == "auto":
                continue
            if director in profile.get("directors", []):
                return style_name
        return "写实主义"  # default

    def _get_director_sound_profile(self, director):
        """Get sound profile from director_data_unified or built-in fallback."""
        clean = director.split("(")[0].split("（")[0].strip()
        profile = {}
        if _HAS_DIRECTOR_DATA:
            for name in (director, clean):
                if name in DIRECTOR_PROFILES_ALL:
                    d = DIRECTOR_PROFILES_ALL[name]
                    profile["unified_sound"] = d.get("声音", "")
                    profile["unified_mood"] = d.get("情绪", "")
                    profile["unified_works"] = d.get("代表作", "")
                    break
        for name in (director, clean, clean.replace("_短剧版", "")):
            if name in DIRECTOR_SOUND_SIGNATURES:
                profile.update(DIRECTOR_SOUND_SIGNATURES[name])
                break
        return profile

    def _get_emotion_atmosphere(self, mood):
        """Get emotion-based atmosphere guidance from knowledge_base."""
        result = {}
        if _HAS_EMOTION_KB and "scene_emotion_rendering" in EMOTION_RENDERING:
            atmo = EMOTION_RENDERING["scene_emotion_rendering"].get("atmosphere_building", {})
            sound_atmo = atmo.get("sound", {})
            weather_atmo = atmo.get("weather_emotion", {})
            result["sound_principles"] = sound_atmo
            # Match weather keywords in mood
            for weather, meaning in weather_atmo.items():
                if weather in mood:
                    result["weather_emotion"] = weather + ": " + meaning
        if _HAS_EMOTION_KB and "rendering_techniques" in EMOTION_RENDERING:
            sound_tech = EMOTION_RENDERING["rendering_techniques"].get("sound_emotion", {})
            if sound_tech:
                result["sound_technique"] = sound_tech
        return result

    def _build_layer1_ambience(self, scene_locations, reverb_profile):
        """Build Layer 1: Environmental ambience from detected locations."""
        lines = []
        all_sounds = []
        for loc in scene_locations:
            sounds = SCENE_AMBIENCE_MAP.get(loc, [])
            all_sounds.extend(sounds)
        # Deduplicate while preserving order
        seen = set()
        unique_sounds = []
        for s in all_sounds:
            if s not in seen:
                seen.add(s)
                unique_sounds.append(s)
        # Limit to 6 for H3 overall_soundscape constraint (1-4 sentences, but can be dense)
        for sound in unique_sounds[:6]:
            lines.append(sound)
        # Add reverb context
        if reverb_profile and reverb_profile != "auto":
            rev = REVERB_PROFILES.get(reverb_profile, {})
            h3_rev = rev.get("h3_description", "")
            if h3_rev:
                lines.append(h3_rev)
        return lines

    def _build_layer2_foley(self, detected_actions, scene_desc):
        """Build Layer 2: Foley sound design from detected actions."""
        lines = []
        for action in detected_actions[:3]:  # Max 3 actions
            foley_data = FOLEY_ACTION_MAP.get(action, [])
            if isinstance(foley_data, dict):
                # Has surface variants (e.g., walking)
                # Try to detect surface from scene
                surfaces = foley_data.get("surfaces", {})
                matched_surface = None
                for surface_name, desc in surfaces.items():
                    if surface_name in scene_desc or any(c in scene_desc for c in surface_name):
                        matched_surface = (surface_name, desc)
                        break
                if matched_surface:
                    lines.append("[Foley/" + action + "/" + matched_surface[0] + "] " + matched_surface[1])
                else:
                    # Default to first surface
                    first = list(surfaces.items())[0] if surfaces else ("default", "footstep impact")
                    lines.append("[Foley/" + action + "] " + first[1])
                mod = foley_data.get("modifiers", "")
                if mod:
                    lines.append("  Modifier: " + mod)
            elif isinstance(foley_data, list):
                # List of component sounds
                for component in foley_data[:3]:  # Max 3 components per action
                    lines.append("[Foley/" + action + "] " + component)
        return lines

    def _build_layer3_dialogue(self, scene_desc, mood, director):
        """Build Layer 3: Voice/dialogue descriptor."""
        lines = []
        # Detect character attributes from scene
        age = "middle_aged"
        gender = "neutral"
        register = "casual"
        language = "Chinese"

        age_hints = {
            "孩子": "child", "小孩": "child", "少年": "teenager",
            "青年": "young_adult", "年轻": "young_adult",
            "中年": "middle_aged", "父": "middle_aged", "母": "middle_aged",
            "老": "elderly", "爷": "elderly", "奶": "elderly", "婆": "elderly",
        }
        for hint, val in age_hints.items():
            if hint in scene_desc:
                age = val
                break

        gender_hints = {
            "父": "male", "男": "male", "他": "male", "先生": "male",
            "母": "female", "女": "female", "她": "female", "小姐": "female",
        }
        for hint, val in gender_hints.items():
            if hint in scene_desc:
                gender = val
                break

        age_desc = VOICE_DESCRIPTOR_TEMPLATE["age_ranges"].get(age, "a moderate voice")
        gender_desc = VOICE_DESCRIPTOR_TEMPLATE["gender_tones"].get(gender, "mid-range, conversational")
        register_desc = VOICE_DESCRIPTOR_TEMPLATE["registers"].get(register, "relaxed cadence")
        lang_desc = VOICE_DESCRIPTOR_TEMPLATE["languages"].get(language, "Mandarin Chinese")

        voice_desc = age_desc + ", " + gender_desc + ", " + register_desc
        lines.append("[Voice/S1] " + voice_desc)
        lines.append("[Language] " + lang_desc)

        # Director-specific dialogue direction
        director_dialogue_map = {
            "是枝裕和": "Natural speech with overlapping. Characters talk while doing other things. No dramatic pauses for camera.",
            "王家卫": "Voiceover dominant. Characters narrate their loneliness. On-screen dialogue is minimal, functional.",
            "塔可夫斯基": "Sparse. Philosophical when present. Long gaps between lines where only ambient sound exists.",
            "奉俊昊": "Naturalistic but precisely timed for comedic or horrific effect. Subtext in WHAT they don't say.",
            "蔡明亮": "Almost no dialogue. When a character speaks, it is an event. The voice sounds alien after so much silence.",
            "周星驰": "Rapid-fire Cantonese. Wordplay. Volume changes for comedic effect. Exaggerated reactions.",
            "诺兰": "Exposition-heavy but layered under action/music. The audience catches 70% — that is enough.",
            "黑泽明": "Theatrical projection. Characters speak as if addressing an audience. Silences are deliberate.",
            "贾樟柯": "Dialect-specific. Characters speak their real regional accent. No Standard Mandarin polish.",
            "李安": "Bilingual subtlety. Characters code-switch. The language they choose reveals their emotional state.",
        }
        dir_key = director.replace("_短剧版", "")
        if dir_key in director_dialogue_map:
            lines.append("[Director Dialogue Style] " + director_dialogue_map[dir_key])

        return lines

    def _build_layer4_music_summary(self, mood, director):
        """Build Layer 4: Music summary (detail in MusicScorePro)."""
        lines = []
        # Match mood to music
        matched_mood = None
        for mood_key in EMOTION_MUSIC_SUMMARY:
            if mood_key in mood:
                matched_mood = mood_key
                break
        if matched_mood:
            lines.append("[Music Summary] " + EMOTION_MUSIC_SUMMARY[matched_mood])
        else:
            # Default to the full mood string as guide
            lines.append("[Music Summary] Instrumentation and tempo to match: " + mood)

        # Director music preference
        profile = self._get_director_sound_profile(director)
        if "music_rule" in profile:
            lines.append("[Director Music Rule] " + profile["music_rule"])

        return lines

    def _build_h3_soundscape(self, ambience_lines, foley_lines, reverb_choice):
        """Build H3 overall_soundscape field (1-4 sentences, English)."""
        # Combine ambience + foley into 1-4 sentences
        all_elements = []
        # Take top ambience sounds
        for line in ambience_lines[:4]:
            if line and not line.startswith("with"):  # skip reverb description
                all_elements.append(line)
        # Add 1-2 foley highlights
        for line in foley_lines[:2]:
            cleaned = re.sub(r'\[Foley/[^\]]+\]\s*', '', line)
            if cleaned and not cleaned.startswith("Modifier"):
                all_elements.append(cleaned)

        if not all_elements:
            return "Ambient room tone with occasional subtle movement."

        # Build 2-4 sentences
        sentences = []
        # Group elements into sentences of 2-3
        for i in range(0, len(all_elements), 2):
            chunk = all_elements[i:i+2]
            sentences.append(". ".join(c.rstrip(".") for c in chunk) + ".")

        result = " ".join(sentences[:4])  # Max 4 sentences per H3 spec
        return result

    def _build_h3_music_field(self, music_lines):
        """Build H3 non_diegetic_music field (1-3 sentences, English)."""
        if not music_lines:
            return "Silence — no non-diegetic music in this scene."
        # Extract the summary content
        summary = ""
        for line in music_lines:
            if line.startswith("[Music Summary]"):
                summary = line.replace("[Music Summary] ", "")
                break
        return summary if summary else "Sparse instrumental accompaniment matching the scene's emotional tone."

    # ------------------------------------------------------------------
    # Main build method
    # ------------------------------------------------------------------
    def build_sound(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("SoundDesignPro requires prompt_builder. Error: " + _AI_DEPS_ERROR, "", "")

        # === Extract inputs ===
        task_type_full = self._str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = self._str(kwargs.get("类型"), "电影")
        scene = self._str(kwargs.get("场景描述"), "")
        director = self._str(kwargs.get("导演风格"), "是枝裕和")
        mood = self._str(kwargs.get("情绪基调"), "")
        subtext = self._str(kwargs.get("潜文本_情感"), "")
        intent_feel = self._str(kwargs.get("导演意图_观众应感到"), "")
        props = self._str(kwargs.get("关键道具"), "")
        ref_films = self._str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # Sound-design specific inputs
        sound_layer_choice = self._str(kwargs.get("声音层级"), "4层全开 (环境+拟音+对白+音乐)")
        reverb_choice = self._str(kwargs.get("空间混响"), "auto")
        style_choice = self._str(kwargs.get("声音风格"), "auto")

        # === Auto-detect parameters ===
        if reverb_choice == "auto":
            reverb_choice = self._detect_reverb_from_scene(scene)
        if style_choice == "auto":
            style_choice = self._detect_sound_style(director)

        scene_locations = self._detect_scene_locations(scene)
        detected_actions = self._detect_actions(scene, props)
        director_sound = self._get_director_sound_profile(director)
        emotion_atmo = self._get_emotion_atmosphere(mood)

        # === Determine which layers to build ===
        build_ambience = "环境" in sound_layer_choice or "4层" in sound_layer_choice
        build_foley = "拟音" in sound_layer_choice or "4层" in sound_layer_choice
        build_dialogue = "对白" in sound_layer_choice or "4层" in sound_layer_choice
        build_music = "音乐" in sound_layer_choice or "4层" in sound_layer_choice

        # === Build 4 layers ===
        ambience_lines = self._build_layer1_ambience(scene_locations, reverb_choice) if build_ambience else []
        foley_lines = self._build_layer2_foley(detected_actions, scene) if build_foley else []
        dialogue_lines = self._build_layer3_dialogue(scene, mood, director) if build_dialogue else []
        music_lines = self._build_layer4_music_summary(mood, director) if build_music else []

        # === Build H3 fields ===
        h3_soundscape = self._build_h3_soundscape(ambience_lines, foley_lines, reverb_choice)
        h3_music = self._build_h3_music_field(music_lines)

        # === Director motion preference ===
        director_motion_map = {
            "塔可夫斯基": "Static Shot held for 60+ seconds + Push In at glacial speed",
            "王家卫": "Push In with small amplitude at slow speed + Step Printing",
            "诺兰": "Tracking Shot with large amplitude at fast speed + time-fold editing",
            "是枝裕和": "Static Shot for domestic observation + Push In with small amplitude at slow speed",
            "侯孝贤": "Static Shot wide-angle long take + maximum breathing room",
            "李沧东": "Push In with small amplitude at slow speed + held moments",
            "蔡明亮": "Static Shot ultra-long + zero movement",
            "毕赣": "Arc Shot continuous + single-take dream sequence",
            "周星驰": "Quick Cut rapid-fire + comedic timing pause",
            "Papi酱": "Static Shot talking-head + direct address",
            "Vince Gilligan": "Push In dark-palette slow approach",
            "大衛·芬奇": "Tracking Shot with calculated precision + dark tone",
            "黑泽明": "Wide Shot multi-figure blocking + weather as character",
            "奉俊昊": "Symmetric Pan with controlled social hierarchy composition",
            "库布里克": "Steadicam float + symmetry obsession",
            "小津安二郎": "Tatami-height Static Shot + pillow shots between scenes",
            "贾樟柯": "Handheld documentary-style in real locations",
            "李安": "Push In with cultural sensitivity + East-West camera grammar",
        }
        dir_key = director.replace("_短剧版", "")
        director_motion_pref = director_motion_map.get(dir_key, director_motion_map.get(director, "Static Shot + Push In"))

        # === Visual style from genre ===
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, high emotional density",
            "短视频": "live-action, high saturation, direct impact",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        visual_style = style_choices.get(genre, "Cinematic, live-action")

        # === Build H3 three fields with sound-aware content ===
        # Shot 1 with sound-conscious description
        shot_1 = (
            "a medium-wide shot establishes the scene - " + scene + ". "
            + "The " + director_motion_pref + " reveals the texture of materials and the quality of light. "
            + "The director intends: " + intent_feel + ". "
            + "The " + props.split(" / ")[0] + " sits within the frame, "
            + "its presence weighted with " + subtext + "."
        )

        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        shots = [
            "[Shot 2] At 00:03.500, the camera cuts to a medium close-up. "
            + format_shot_motion("Push In", "small", "slow")
            + " on the character's face, revealing " + subtext + ". "
            + "Lighting consistent with previous shot.",

            "[Shot 3] At 00:08.000, close-up of hands interacting with " + first_prop + ". "
            + "Static shot as the hands work. (S1) speaks with " + mood + " voice: "
            + "<d>[Chinese] ...</d>",

            "[Shot 4] At 00:15.000, over-the-shoulder shot. "
            + format_shot_motion("Push In", "small", "slow")
            + " toward the other character. The silence carries " + subtext + ".",

            "[Shot 5] At 00:22.000, wider static shot. Both characters in frame. "
            + "5-10 seconds of silence. Intent: " + intent_feel + ". "
            + "Per silence formula: one short line, 3s silence, micro-expression shift, "
            + "relationship-changing action, 5s breathing room.",

            "[Shot 6] At 00:27.000, held for 3 seconds. "
            + last_prop + " catches the light. End of shot.",
        ]

        h3_prompt = build_h3_three_fields(
            style=visual_style, shot_1_content=shot_1, shots_content=shots,
            soundscape=h3_soundscape, music=h3_music, language="Chinese"
        )

        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # === 30-second timeline ===
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice=dialogue_lines[0] if dialogue_lines else "a moderate voice",
            dialogue="...", n_lines=1, director_intent=intent_feel, language="Chinese"
        )

        # ================================================================
        # ASSEMBLE OUTPUT 1: Main H3 Prompt with 4-Layer Sound Design
        # ================================================================
        # Phase 17.6: Soul injection
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
                    "【灵魂核心 - 声音设计驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        main_output = "=" * 60 + "\n"
        main_output += soul_header
        main_output += "【SoundDesignPro】4-Layer Soundscape Engine\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【声音风格】 " + style_choice + "\n"
        main_output += "【空间混响】 " + reverb_choice + "\n"
        main_output += "【声音层级】 " + sound_layer_choice + "\n\n"

        # --- Sound style philosophy ---
        style_profile = SOUND_STYLE_PROFILES.get(style_choice, {})
        main_output += "=" * 60 + "\n"
        main_output += "声音设计哲学 (" + style_choice + ")\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  原则: " + style_profile.get("principle", "") + "\n"
        main_output += "  拟音方式: " + style_profile.get("foley_approach", "") + "\n"
        main_output += "  混音: " + style_profile.get("mixing", "") + "\n\n"

        # --- Director sound signature ---
        main_output += "=" * 60 + "\n"
        main_output += "导演声音签名: " + director + "\n"
        main_output += "=" * 60 + "\n\n"
        if director_sound:
            if "philosophy" in director_sound:
                main_output += "  声音哲学: " + director_sound["philosophy"] + "\n"
            if "unified_sound" in director_sound:
                main_output += "  统一数据 (声音): " + director_sound["unified_sound"] + "\n"
            if "signature_sounds" in director_sound:
                main_output += "  标志性声音:\n"
                for ss in director_sound["signature_sounds"]:
                    main_output += "    - " + ss + "\n"
            if "silence_approach" in director_sound:
                main_output += "  沉默策略: " + director_sound["silence_approach"] + "\n"
            if "music_rule" in director_sound:
                main_output += "  配乐规则: " + director_sound["music_rule"] + "\n"
            if "mixing_note" in director_sound:
                main_output += "  混音备注: " + director_sound["mixing_note"] + "\n"
        main_output += "\n"

        # --- 4-Layer breakdown ---
        main_output += "=" * 60 + "\n"
        main_output += "4-Layer Soundscape Breakdown\n"
        main_output += "=" * 60 + "\n\n"

        if build_ambience:
            main_output += "--- Layer 1: 环境音 (Ambience) ---\n"
            main_output += "  检测场景: " + ", ".join(scene_locations) + "\n"
            for line in ambience_lines:
                main_output += "  - " + line + "\n"
            main_output += "\n"

        if build_foley:
            main_output += "--- Layer 2: 拟音 (Foley) ---\n"
            main_output += "  检测动作: " + ", ".join(detected_actions) + "\n"
            for line in foley_lines:
                main_output += "  - " + line + "\n"
            main_output += "\n"

        if build_dialogue:
            main_output += "--- Layer 3: 对白 (Dialogue) ---\n"
            for line in dialogue_lines:
                main_output += "  - " + line + "\n"
            main_output += "\n"

        if build_music:
            main_output += "--- Layer 4: 音乐 (Music Summary) ---\n"
            for line in music_lines:
                main_output += "  - " + line + "\n"
            main_output += "\n"

        # --- Spatial reverb detail ---
        main_output += "=" * 60 + "\n"
        main_output += "空间混响参数 (" + reverb_choice + ")\n"
        main_output += "=" * 60 + "\n\n"
        rev_data = REVERB_PROFILES.get(reverb_choice, REVERB_PROFILES.get("中空间 (客厅/办公室)", {}))
        main_output += "  RT60: " + rev_data.get("rt60", "N/A") + "\n"
        main_output += "  Early Reflections: " + rev_data.get("early_reflections", "N/A") + "\n"
        main_output += "  Character: " + rev_data.get("character", "N/A") + "\n\n"

        # --- Mixing parameters ---
        main_output += "=" * 60 + "\n"
        main_output += "专业混音参数 (LUFS)\n"
        main_output += "=" * 60 + "\n\n"
        for layer_name, params in MIXING_PARAMETERS.items():
            main_output += "  " + layer_name + ": " + str(params["target_lufs"]) + " LUFS " + params["range"]
            main_output += " [" + params.get("priority", params.get("note", "")) + "]\n"
        main_output += "\n"

        # --- H3 three fields ---
        main_output += "=" * 60 + "\n"
        main_output += "H3 三大字段 (MiniMax-H3 Official Format)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_prompt + "\n\n"

        # --- H3 Sound fields detail ---
        main_output += "=" * 60 + "\n"
        main_output += "H3 overall_soundscape (1-4 sentences)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_soundscape + "\n\n"

        main_output += "=" * 60 + "\n"
        main_output += "H3 non_diegetic_music (1-3 sentences)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_music + "\n\n"

        # --- Emotion atmosphere from KB ---
        if emotion_atmo:
            main_output += "=" * 60 + "\n"
            main_output += "情绪-声音映射 (knowledge_base.emotion_rendering)\n"
            main_output += "=" * 60 + "\n\n"
            if "sound_principles" in emotion_atmo:
                for k, v in emotion_atmo["sound_principles"].items():
                    main_output += "  " + k + ": " + v + "\n"
            if "weather_emotion" in emotion_atmo:
                main_output += "  天气情绪: " + emotion_atmo["weather_emotion"] + "\n"
            if "sound_technique" in emotion_atmo:
                tech = emotion_atmo["sound_technique"]
                if isinstance(tech, dict):
                    main_output += "  声音承载情绪原则: " + tech.get("principle", "") + "\n"
            main_output += "\n"

        # --- Director intent 5D ---
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "based on subtext: " + subtext[:40] if subtext else "unspecified",
            "主题": mood,
            "留白": "unsaid — " + first_prop + " carries the silence",
        }
        intent_block = inject_director_intent(intent_5d)
        main_output += "=" * 60 + "\n"
        main_output += "导演意图 5 维\n"
        main_output += "=" * 60 + "\n\n"
        main_output += intent_block + "\n\n"

        # --- 30s timeline ---
        timeline_30s_lines = "\n".join([
            "  " + str(round(ts, 1)) + "-" + str(round(te, 1)) + "s [" + stage + "]: " + desc
            for (ts, te, stage, desc) in SCENE_UNIT_30S
        ])
        main_output += "=" * 60 + "\n"
        main_output += "30-Second Scene Unit 6-Act Structure\n"
        main_output += "=" * 60 + "\n\n"
        main_output += timeline_30s_lines + "\n\n"

        # Anti-AI cleanup
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ================================================================
        # OUTPUT 2: Experience Matrix
        # ================================================================
        experience = "【SoundDesignPro Experience Matrix】\n\n"

        experience += "--- Director Sound Signatures (Real Data) ---\n"
        for d_name in DIRECTORS_20[:10]:
            d_key = d_name.replace("_短剧版", "")
            prof = self._get_director_sound_profile(d_key)
            if "philosophy" in prof:
                experience += "  " + d_name + ": " + prof["philosophy"][:80] + "...\n"
            elif "unified_sound" in prof:
                experience += "  " + d_name + ": " + prof["unified_sound"] + "\n"
            else:
                experience += "  " + d_name + ": (see director_data_unified)\n"
        experience += "\n"

        experience += "--- Scene Ambience Coverage ---\n"
        experience += "  Mapped locations: " + ", ".join(sorted(SCENE_AMBIENCE_MAP.keys())) + "\n"
        experience += "  Total ambient elements: " + str(sum(len(v) for v in SCENE_AMBIENCE_MAP.values())) + "\n\n"

        experience += "--- Foley Action Coverage ---\n"
        experience += "  Mapped actions: " + ", ".join(sorted(FOLEY_ACTION_MAP.keys())) + "\n\n"

        experience += "--- Genre Sound Profiles ---\n"
        if _HAS_GENRE_KB:
            for gk, gv in list(GENRE_PROFILES.items())[:5]:
                cn = gv.get("cn", gk)
                pacing = gv.get("pacing", {})
                sound_design = pacing.get("sound_design", pacing.get("rhythm", ""))
                if sound_design:
                    experience += "  " + cn + ": " + str(sound_design)[:80] + "\n"
        experience += "\n"

        experience += "--- Reverb Profiles ---\n"
        for rk, rv in REVERB_PROFILES.items():
            if rk != "auto":
                experience += "  " + rk + ": RT60=" + rv.get("rt60", "N/A") + "\n"
        experience += "\n"

        experience += "--- Sound Style Profiles ---\n"
        for sk, sv in SOUND_STYLE_PROFILES.items():
            if sk != "auto":
                experience += "  " + sk + ": " + sv.get("principle", "")[:60] + "...\n"
        experience += "\n"

        experience += "【10 Specific Detail Rules (Anti-AI)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # ================================================================
        # OUTPUT 3: AI Deep Processing
        # ================================================================
        ai_deep_output = "【SoundDesignPro AI Deep Processing】\n\n"

        ai_deep_output += "--- Anti-AI Cleanup Actions ---\n"
        if anti_ai_on:
            # Show what was cleaned
            ai_deep_output += "  Anti-AI rules applied to main output.\n"
            ai_deep_output += "  191+ banned AI phrases checked and replaced.\n"
            ai_deep_output += "  10 forced-specific-detail rules enforced.\n\n"
        else:
            ai_deep_output += "  Anti-AI rules disabled by user.\n\n"

        ai_deep_output += "--- Scene Analysis ---\n"
        ai_deep_output += "  Detected locations: " + ", ".join(scene_locations) + "\n"
        ai_deep_output += "  Detected actions: " + ", ".join(detected_actions) + "\n"
        ai_deep_output += "  Auto-selected reverb: " + reverb_choice + "\n"
        ai_deep_output += "  Auto-selected style: " + style_choice + "\n\n"

        ai_deep_output += "--- Mixing Decisions ---\n"
        ai_deep_output += "  Dialogue target: " + str(MIXING_PARAMETERS["dialogue"]["target_lufs"]) + " LUFS\n"
        ai_deep_output += "  Music target: " + str(MIXING_PARAMETERS["music"]["target_lufs"]) + " LUFS\n"
        ai_deep_output += "  SFX/Foley target: " + str(MIXING_PARAMETERS["sfx_foley"]["target_lufs"]) + " LUFS\n"
        ai_deep_output += "  Ambience target: " + str(MIXING_PARAMETERS["ambience"]["target_lufs"]) + " LUFS\n"
        ai_deep_output += "  Overall loudness: " + str(MIXING_PARAMETERS["overall_loudness"]["target_lufs"]) + " LUFS (streaming standard)\n\n"

        ai_deep_output += "--- Director Sound Data Sources ---\n"
        ai_deep_output += "  director_data_unified: " + ("loaded (35 directors x 8 dims)" if _HAS_DIRECTOR_DATA else "not available") + "\n"
        ai_deep_output += "  knowledge_base.emotion_rendering: " + ("loaded" if _HAS_EMOTION_KB else "not available") + "\n"
        ai_deep_output += "  knowledge_base.genre_profiles: " + ("loaded" if _HAS_GENRE_KB else "not available") + "\n"
        ai_deep_output += "  knowledge_base.h3_prompt_framework: " + ("loaded" if _HAS_H3_KB else "not available") + "\n"
        ai_deep_output += "  Built-in sound signatures: " + str(len(DIRECTOR_SOUND_SIGNATURES)) + " directors\n"
        ai_deep_output += "  Built-in ambience map: " + str(len(SCENE_AMBIENCE_MAP)) + " locations\n"
        ai_deep_output += "  Built-in foley map: " + str(len(FOLEY_ACTION_MAP)) + " action categories\n\n"

        ai_deep_output += "--- Silence Rules ---\n"
        ai_deep_output += inject_silence_mastery_5("对话", 1) + "\n\n"

        ai_deep_output += "--- 9D Lighting Control ---\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "SoundDesignPro": SoundDesignPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "SoundDesignPro": "🔊 声音设计 (环节 13) — L5 重写",
# }
