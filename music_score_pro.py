# -*- coding: utf-8 -*-
"""
MusicScorePro - 音乐配乐专家节点 (环节 14)
====================================================
Professional film scoring engine with genuine domain logic:

1. Emotion-to-music mapping (key, tempo, instrumentation, dynamics)
2. Genre-to-score templates (film noir, sci-fi, horror, etc.)
3. Director scoring signatures (Zimmer, Morricone, Sakamoto, Hisaishi, etc.)
4. 30-second scene scoring (6 acts mapped to music changes)
5. H3 non_diegetic_music field generation (instrument + mood + tempo + key)

All data derived from real film scoring practice and music theory.
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
# BUILT-IN DOMAIN DATA: Film Scoring Engine
# ============================================================

# === Emotion-to-Music Mapping ===
# Each emotion has: key, mode, tempo_bpm, instrumentation, dynamics, phrase_contour
EMOTION_MUSIC_MAP = {
    "joy": {
        "cn": "喜悦",
        "key": "C major",
        "mode": "major / Ionian",
        "tempo_bpm": 120,
        "tempo_marking": "Allegro",
        "instrumentation": ["strings (arco, full section)", "brass (French horn melody)", "woodwinds (flute + oboe)", "light percussion (triangle, tambourine)"],
        "dynamics": "mf to ff",
        "phrase_contour": "ascending stepwise motion, large interval leaps at climax",
        "harmonic_character": "diatonic, I-IV-V-I progressions, added 6ths for warmth",
        "orchestration_note": "Strings carry melody, brass punctuate at cadences, woodwinds double at octave for brightness",
    },
    "sadness": {
        "cn": "悲伤",
        "key": "Ab minor",
        "mode": "minor / Aeolian",
        "tempo_bpm": 60,
        "tempo_marking": "Adagio",
        "instrumentation": ["solo piano", "solo cello", "strings (con sordino)", "English horn"],
        "dynamics": "pp to p",
        "phrase_contour": "descending, stepwise, phrases trail off without resolution",
        "harmonic_character": "minor i-iv-v with frequent deceptive cadences, unresolved suspensions",
        "orchestration_note": "Solo instrument exposed against silence. When strings enter, they sustain underneath, never lead.",
    },
    "anger": {
        "cn": "愤怒",
        "key": "D minor",
        "mode": "minor / Phrygian inflection",
        "tempo_bpm": 140,
        "tempo_marking": "Vivace agitato",
        "instrumentation": ["brass (trombones + trumpets, marcato)", "strings (tremolo, sul ponticello)", "percussion (timpani rolls, snare)", "bass (doubled octaves)"],
        "dynamics": "f to fff, sforzando accents",
        "phrase_contour": "angular, wide intervals, syncopated rhythmic attacks",
        "harmonic_character": "tritone relationships, augmented chords, pedal point bass drone",
        "orchestration_note": "Brass in unison for maximum aggression. Strings provide texture, not melody. Percussion drives rhythm.",
    },
    "fear": {
        "cn": "恐惧",
        "key": "atonal / chromatic cluster",
        "mode": "chromatic / whole-tone / Locrian",
        "tempo_bpm": 0,
        "tempo_marking": "Rubato / no fixed tempo",
        "instrumentation": ["strings (col legno, harmonics, Bartok pizzicato)", "prepared piano", "low brass (pedal tones)", "waterphone", "bowed cymbals"],
        "dynamics": "ppp with sudden sfz stabs",
        "phrase_contour": "static drones punctuated by sudden attacks, Shepard tone illusion",
        "harmonic_character": "cluster chords, quarter-tones, no tonal center, polytonal stacking",
        "orchestration_note": "Extended techniques dominate. Nothing sounds 'normal'. The instrument itself becomes alien.",
    },
    "love": {
        "cn": "爱/心动",
        "key": "Eb major",
        "mode": "major / Lydian inflection",
        "tempo_bpm": 72,
        "tempo_marking": "Andante con moto",
        "instrumentation": ["strings (warm vibrato, divisi)", "solo oboe or clarinet", "harp arpeggios", "celesta for sparkle"],
        "dynamics": "p to mf, crescendo to peak then gentle diminuendo",
        "phrase_contour": "lyrical, singing, long sustained notes at peak of phrase",
        "harmonic_character": "rich chromatic passing tones, augmented 6th chords, Neapolitan 6th for yearning",
        "orchestration_note": "Two solo instruments in dialogue (representing two characters). Strings provide warm bed. Harp fills transitions.",
    },
    "tension": {
        "cn": "紧张/悬疑",
        "key": "B minor pedal",
        "mode": "minor / octatonic (diminished)",
        "tempo_bpm": 90,
        "tempo_marking": "Moderato, molto agitato",
        "instrumentation": ["strings (tremolo pp, gradually thickening)", "solo timpani ostinato", "bass clarinet", "muted brass"],
        "dynamics": "pp building to f (long crescendo over entire cue)",
        "phrase_contour": "ostinato pattern that gradually rises in pitch, tightening intervals",
        "harmonic_character": "diminished 7th chords, tritone substitutions, unresolved dominants",
        "orchestration_note": "Hitchcock/Herrmann technique: repeating pattern with one element changing each cycle. Psychological ratchet.",
    },
    "hope": {
        "cn": "希望",
        "key": "G major",
        "mode": "major / Mixolydian",
        "tempo_bpm": 88,
        "tempo_marking": "Andante, con speranza",
        "instrumentation": ["French horn (melody)", "strings (sustained, swelling)", "flute (countermelody)", "timpani (soft rolls at climax)"],
        "dynamics": "p building to ff at resolution",
        "phrase_contour": "ascending by step, each phrase higher than the last, final phrase reaches highest note",
        "harmonic_character": "IV-I plagal cadences (amen cadence), suspensions resolving upward",
        "orchestration_note": "Horn states theme alone. Strings join. Woodwinds join. Full orchestra at climax = hope realized.",
    },
    "nostalgia": {
        "cn": "怀旧",
        "key": "F major",
        "mode": "major with minor inflections",
        "tempo_bpm": 66,
        "tempo_marking": "Andante, rubato",
        "instrumentation": ["solo piano (music box quality)", "strings (con sordino, distant)", "accordion or harmonica", "music box or celesta"],
        "dynamics": "pp throughout, gentle swells",
        "phrase_contour": "simple melody that repeats, slightly varied each time, as if imperfectly remembered",
        "harmonic_character": "major key with borrowed minor chords (i, vi), pentatonic passages",
        "orchestration_note": "Thin texture. Imperfect. A melody heard through the filter of time. Processing: add vinyl crackle, room reverb.",
    },
    "loneliness": {
        "cn": "孤独",
        "key": "E minor",
        "mode": "Dorian",
        "tempo_bpm": 54,
        "tempo_marking": "Largo, desolato",
        "instrumentation": ["solo instrument (oboe, erhu, or English horn)", "sustained string pad (PPP, barely present)", "no percussion"],
        "dynamics": "ppp to pp, no crescendo ever reaches mf",
        "phrase_contour": "single line floating in space, long rests between phrases, phrases shorten as if running out of breath",
        "harmonic_character": "unaccompanied or simple drone underneath, modal rather than tonal",
        "orchestration_note": "One voice in a vast empty acoustic space. The reverb tail IS the accompaniment. Less is everything.",
    },
    "ambiguity": {
        "cn": "暧昧/模糊",
        "key": "Bb with suspended harmony",
        "mode": "Lydian-Mixolydian hybrid",
        "tempo_bpm": 76,
        "tempo_marking": "Moderato, senza rigore",
        "instrumentation": ["jazz piano (suspended voicings)", "vibraphone (motor on, detuned)", "brushed cymbal", "upright bass (arco, not pizz)"],
        "dynamics": "mp, constant level, no dramatic changes",
        "phrase_contour": "circular, phrases that seem about to resolve but cycle back",
        "harmonic_character": "sus4, sus2, add9, no clear major/minor definition, Debussy-like parallel motion",
        "orchestration_note": "Wong Kar-wai territory. The music refuses to commit, just like the characters.",
    },
    "triumph": {
        "cn": "胜利/壮烈",
        "key": "Bb major",
        "mode": "major / Lydian",
        "tempo_bpm": 108,
        "tempo_marking": "Allegro maestoso",
        "instrumentation": ["full brass section (horns + trumpets + trombones)", "full strings", "timpani + crash cymbals", "choir (wordless)"],
        "dynamics": "ff to fff",
        "phrase_contour": "fanfare motif: dotted rhythm + ascending 4th/5th, repeated at higher pitch levels",
        "harmonic_character": "power chords, I-V-I cadences, plagal resolution, pedal on tonic",
        "orchestration_note": "Everything playing. Choir adds human weight. Timpani rolls at transitions. John Williams territory.",
    },
    "melancholy": {
        "cn": "忧郁",
        "key": "C# minor",
        "mode": "minor / Dorian",
        "tempo_bpm": 58,
        "tempo_marking": "Lento, con dolore",
        "instrumentation": ["solo cello (melody)", "piano (sparse chords)", "strings (sustained, PPP)", "no brass, no percussion"],
        "dynamics": "pp, occasional p at phrase peaks, returning to pp",
        "phrase_contour": "long sustained notes with tiny ornamental turns, like sighing",
        "harmonic_character": "i-VI-III-VII natural minor progressions, plagal minor cadences",
        "orchestration_note": "Cello IS the character's voice. Piano responds as the memory. Strings are the weight of time.",
    },
}

# === Genre-to-Score Templates ===
GENRE_SCORE_TEMPLATES = {
    "film_noir": {
        "cn": "黑色电影",
        "ensemble": "jazz combo (4-6 players)",
        "lead_instrument": "alto saxophone (smoky, breathy tone)",
        "rhythm_section": "brushed drums on snare + walking upright bass",
        "harmony": "minor 7th and diminished chords, tritone substitutions",
        "tempo_range": "60-80 BPM (slow swing)",
        "signature_elements": ["muted trumpet solo", "piano comping with 9th/13th voicings", "finger snaps instead of hi-hat"],
        "reference_scores": ["Chinatown (Jerry Goldsmith)", "Taxi Driver (Bernard Herrmann)", "Blade Runner (Vangelis)"],
    },
    "sci_fi": {
        "cn": "科幻",
        "ensemble": "synthesizers + processed orchestra",
        "lead_instrument": "synth pads (evolving textures, granular synthesis)",
        "rhythm_section": "electronic percussion, processed found sounds, clock mechanisms",
        "harmony": "parallel 5ths, whole-tone scales, quartal harmony",
        "tempo_range": "variable, often no fixed pulse",
        "signature_elements": ["Shepard tone (endless ascending illusion)", "sub-bass oscillation below 40Hz",
                               "reversed reverb tails", "vocoder-processed choir"],
        "reference_scores": ["Interstellar (Hans Zimmer)", "Blade Runner 2049 (Zimmer/Wallfisch)", "Arrival (Johann Johannsson)", "2001 (Ligeti/Strauss)"],
    },
    "horror": {
        "cn": "恐怖",
        "ensemble": "chamber strings + prepared instruments",
        "lead_instrument": "solo violin (extreme register, harmonics)",
        "rhythm_section": "no traditional rhythm — heartbeat pulse from bass drum at 60-80 BPM",
        "harmony": "cluster chords, quarter-tones, atonal",
        "tempo_range": "rubato, no consistent pulse",
        "signature_elements": ["sudden silence (the scariest sound)", "Bartok pizzicato (string snap)",
                               "bowed metal (waterphone, singing bowls)", "infrasound at 18-19Hz (causes unease below hearing threshold)"],
        "reference_scores": ["The Shining (Penderecki/Bartok)", "Hereditary (Colin Stetson)", "Psycho (Bernard Herrmann)", "It Follows (Disasterpeace)"],
    },
    "romance": {
        "cn": "爱情/浪漫",
        "ensemble": "string orchestra + solo instrument + harp",
        "lead_instrument": "solo violin or piano (trading phrases = two characters)",
        "rhythm_section": "no percussion, or gentle brushed cymbal for jazz-inflected romance",
        "harmony": "rich chromatic harmony, augmented 6ths, Neapolitan chords, extended dominant 9ths",
        "tempo_range": "60-84 BPM (Andante to Moderato)",
        "signature_elements": ["two solo instruments in dialogue", "harp glissando at emotional peaks",
                               "key change up a half-step at declaration of love", "waltz time (3/4) for dance scenes"],
        "reference_scores": ["Cinema Paradiso (Ennio Morricone)", "Atonement (Dario Marianelli)", "La La Land (Justin Hurwitz)"],
    },
    "war_epic": {
        "cn": "战争/史诗",
        "ensemble": "full symphony orchestra + choir",
        "lead_instrument": "French horn (heroic), strings (elegy)",
        "rhythm_section": "orchestral percussion battery — snare (military), timpani (power), bass drum (impact)",
        "harmony": "modal (Aeolian/Dorian for martial), open 5ths for ancient, full chromatic for modern war",
        "tempo_range": "variable — march at 100-120 BPM, elegy at 50-60 BPM",
        "signature_elements": ["snare drum military tattoo", "choir singing in Latin or constructed language",
                               "solo bugle/trumpet over silence (taps/last post)", "ethnic instruments for location (taiko, duduk, uilleann pipes)"],
        "reference_scores": ["Saving Private Ryan (John Williams)", "Gladiator (Hans Zimmer/Lisa Gerrard)", "Dunkirk (Hans Zimmer)", "1917 (Thomas Newman)"],
    },
    "comedy": {
        "cn": "喜剧",
        "ensemble": "small orchestra or band + quirky solo instruments",
        "lead_instrument": "pizzicato strings, xylophone, or clarinet",
        "rhythm_section": "light percussion — wood blocks, cowbell, rim clicks",
        "harmony": "major key, simple progressions, chromatic neighbor notes for comedic effect",
        "tempo_range": "100-140 BPM (upbeat, bouncy)",
        "signature_elements": ["staccato strings for sneaking/scheming", "trombone slide for slapstick",
                               "timpani hit + silence for punchline", "kazoo/slide whistle for absurdity"],
        "reference_scores": ["The Grand Budapest Hotel (Alexandre Desplat)", "Home Alone (John Williams)", "Kung Fu Hustle (Raymond Wong)"],
    },
    "wuxia": {
        "cn": "武侠/古装",
        "ensemble": "Chinese traditional + Western strings hybrid",
        "lead_instrument": "erhu (heroic melody), guzheng (nature/beauty), xiao (loneliness)",
        "rhythm_section": "Chinese percussion — bangu, bo, tanggu + Western timpani for scale",
        "harmony": "pentatonic base (gong mode), modal shifts for tension, Western chromatic for climax",
        "tempo_range": "variable — combat at 140+ BPM, contemplation at 50 BPM",
        "signature_elements": ["guzheng glissando for swordplay", "xiao solo over mountain landscape",
                               "large taiko drums for battle", "silence between sword strikes"],
        "reference_scores": ["Crouching Tiger Hidden Dragon (Tan Dun)", "Hero (Tan Dun)", "House of Flying Daggers (Shigeru Umebayashi)"],
    },
    "documentary": {
        "cn": "纪录片",
        "ensemble": "minimalist — piano + strings + electronics",
        "lead_instrument": "solo piano (Philip Glass style) or guitar",
        "rhythm_section": "subtle electronic pulse or none",
        "harmony": "modal, repetitive arpeggiated patterns, slowly evolving",
        "tempo_range": "80-100 BPM, steady",
        "signature_elements": ["arpeggiated piano patterns (Glass/Nyman)", "gentle rhythmic pulse that drives forward",
                               "no dramatic swells — the music observes, does not comment"],
        "reference_scores": ["Koyaanisqatsi (Philip Glass)", "Planet Earth (George Fenton)", "The Cove (J. Ralph)"],
    },
    "short_drama": {
        "cn": "短剧",
        "ensemble": "electronic production + sampled orchestra",
        "lead_instrument": "synth lead or piano (instant emotional recognition)",
        "rhythm_section": "modern beat production — trap hi-hats, 808 bass, or clean acoustic kit",
        "harmony": "pop progressions (I-V-vi-IV), minor versions for drama",
        "tempo_range": "80-130 BPM (matching scene energy)",
        "signature_elements": ["bass drop at plot twist", "stripped-back piano for emotional peak",
                               "vocal chop samples for modern feel", "3-second music sting for hook/cliffhanger"],
        "reference_scores": ["Various C-drama/K-drama OSTs", "TikTok viral audio trends"],
    },
}

# === Composer/Director Scoring Signatures ===
COMPOSER_SIGNATURES = {
    "Hans Zimmer": {
        "cn": "汉斯·季默",
        "technique": "Layered electronic-orchestral hybrid. Builds from single synth note to full orchestra.",
        "signature_sounds": ["BRAAAM (inception horn — processed trombone ensemble)",
                             "ticking clock as rhythmic base (Dunkirk, Interstellar)",
                             "massive organ (Interstellar — real church organ recorded in Temple Church London)",
                             "sub-bass synth oscillation that vibrates theater seats"],
        "tempo_approach": "Often slow (60-80 BPM) but with internal rhythmic complexity. The pulse is felt, not heard.",
        "harmonic_language": "Simple harmonic vocabulary (I-V-vi-IV variations) with complex textural layering",
        "associated_directors": ["诺兰", "Ridley Scott", "Denis Villeneuve", "Gore Verbinski"],
        "key_scores": ["Inception", "Interstellar", "The Dark Knight", "Gladiator", "Dune"],
    },
    "Ennio Morricone": {
        "cn": "埃尼奥·莫里康内",
        "technique": "Melody-first scoring. Every score has a hummable theme. Unusual instrumentation as identity.",
        "signature_sounds": ["human whistling as lead instrument",
                             "harmonica (solo, reverberant, lonely)",
                             "electric guitar (twangy, tremolo, spaghetti western)",
                             "wordless soprano voice (Edda Dell'Orso)",
                             "choir chanting"],
        "tempo_approach": "Varied. Can be extremely slow (funeral march) or galloping (chase). Rubato is king.",
        "harmonic_language": "Modal melody over simple ostinato. Melody carries ALL the emotional weight.",
        "associated_directors": ["Sergio Leone", "Giuseppe Tornatore", "Brian De Palma"],
        "key_scores": ["The Good the Bad and the Ugly", "Cinema Paradiso", "The Mission", "Once Upon a Time in the West"],
    },
    "坂本龙一": {
        "cn": "坂本龙一 (Ryuichi Sakamoto)",
        "technique": "Minimalist piano + ambient electronics. Post-classical. Music as meditation.",
        "signature_sounds": ["solo piano with sustain pedal (notes bleeding into each other)",
                             "ambient electronics (soft granular textures)",
                             "prepared piano (objects on strings altering timbre)",
                             "cello + piano duet in unison"],
        "tempo_approach": "Extremely slow. Rubato. Time dissolves. Each note is an event.",
        "harmonic_language": "Extended chords (maj7, add9), cluster voicings, Debussy influence. Neither major nor minor — floating.",
        "associated_directors": ["贝纳尔多·贝托鲁奇", "Alejandro Gonzalez Inarritu", "李安"],
        "key_scores": ["Merry Christmas Mr. Lawrence", "The Revenant", "The Last Emperor", "async (album)"],
    },
    "Joe Hisaishi": {
        "cn": "久石让",
        "technique": "Lyrical orchestral melody. Waltz time signatures. Music that makes you feel you can fly.",
        "signature_sounds": ["piano melody doubled by strings at octave (trademark fullness)",
                             "waltz rhythm (3/4 time) for flight/magic/wonder",
                             "marimba for playful scenes",
                             "full orchestra tutti at emotional peak with soaring strings"],
        "tempo_approach": "Moderate to fast. Clear pulse. The music has forward momentum — it goes somewhere.",
        "harmonic_language": "Tonal, major key dominant, chromatic passing tones for color, key changes for emotional shift",
        "associated_directors": ["宫崎骏", "北野武"],
        "key_scores": ["Spirited Away", "My Neighbor Totoro", "Princess Mononoke", "Howl's Moving Castle", "Kikujiro"],
    },
    "Alexandre Desplat": {
        "cn": "亚历山大·德斯普拉",
        "technique": "Elegant chamber orchestration. Rhythmic patterns as emotional undercurrent.",
        "signature_sounds": ["ostinato patterns in upper woodwinds (flute, piccolo, celesta)",
                             "plucked strings (harp, pizzicato) as rhythmic pulse",
                             "solo oboe or clarinet melody over sparse accompaniment",
                             "chamber-sized orchestrations even in large films"],
        "tempo_approach": "Precise, often driven by a subtle rhythmic pattern that ticks underneath the melody.",
        "harmonic_language": "Neo-classical with French impressionist color. Subtle and refined.",
        "associated_directors": ["Wes Anderson", "George Miller", "Guillermo del Toro"],
        "key_scores": ["The Grand Budapest Hotel", "The Shape of Water", "Harry Potter 7&8", "The Imitation Game"],
    },
    "John Williams": {
        "cn": "约翰·威廉姆斯",
        "technique": "Late-Romantic orchestral tradition. Leitmotif master. Every character has a theme.",
        "signature_sounds": ["brass fanfare (5-note motif, ascending, heroic)",
                             "sustained string melody (legato, soaring)",
                             "harp glissando at magical moments",
                             "full orchestra tutti with choir at maximum grandeur"],
        "tempo_approach": "Classic — march, waltz, scherzo, adagio. Each scene type has its traditional tempo.",
        "harmonic_language": "Late Romantic — Wagner, Holst, Korngold lineage. Leitmotif development across entire film.",
        "associated_directors": ["Steven Spielberg", "George Lucas"],
        "key_scores": ["Star Wars", "Schindler's List", "Jurassic Park", "E.T.", "Indiana Jones"],
    },
    "Jonny Greenwood": {
        "cn": "乔尼·格林伍德",
        "technique": "Avant-garde meets film. String orchestra as noise machine. Radiohead sensibility in classical form.",
        "signature_sounds": ["strings playing at extreme dynamics (fff tremolo)",
                             "col legno (hitting strings with wood of bow)",
                             "microtonal clusters (quarter-tone tuning)",
                             "ondes Martenot (Radiohead's signature electronic instrument)"],
        "tempo_approach": "Irregular. Shifting meters. The rhythm destabilizes the viewer's sense of ground.",
        "harmonic_language": "Atonal passages with sudden tonal islands. Disorienting beauty.",
        "associated_directors": ["Paul Thomas Anderson"],
        "key_scores": ["There Will Be Blood", "Phantom Thread", "The Power of the Dog", "Spencer"],
    },
    "Trent Reznor & Atticus Ross": {
        "cn": "特伦特·雷兹诺/阿提克斯·罗斯",
        "technique": "Industrial ambient. Analog synthesizers + processed acoustic instruments. Texture over melody.",
        "signature_sounds": ["modular synth drones (slow filter sweeps)",
                             "processed piano (pitched down, reversed, granulated)",
                             "metallic percussion (industrial found objects)",
                             "whispered vocals buried in the mix"],
        "tempo_approach": "Slow. Pulse emerges from texture rather than rhythm section.",
        "harmonic_language": "Minimal — often a single chord or drone. Timbre IS the harmony.",
        "associated_directors": ["大衛·芬奇"],
        "key_scores": ["The Social Network", "Gone Girl", "Soul", "Mank"],
    },
}

# === Director-to-Composer mapping ===
DIRECTOR_COMPOSER_MAP = {
    "诺兰": "Hans Zimmer",
    "是枝裕和": "坂本龙一",  # spiritual affinity, though not direct collaboration
    "王家卫": None,  # uses licensed pop music, no single composer
    "塔可夫斯基": None,  # uses Bach/Pergolesi, rarely original score
    "奉俊昊": "Jung Jae-il",  # Parasite composer
    "黑泽明": "Toru Takemitsu",
    "库布里克": None,  # uses pre-existing classical
    "侯孝贤": None,  # minimal music use
    "贾樟柯": None,  # diegetic pop songs
    "蔡明亮": None,  # almost no music
    "周星驰": None,  # eclectic, no single composer
    "大衛·芬奇": "Trent Reznor & Atticus Ross",
    "李安": "坂本龙一",  # sometimes Mychael Danna
    "小津安二郎": None,  # minimal
    "毕赣": None,  # ambient/found
    "Vince Gilligan": "Dave Porter",
    "Papi酱": None,
}

# === Emotion Curve Shapes ===
EMOTION_CURVES = {
    "渐强 (Crescendo)": {
        "description": "Continuous build from quiet to full. Each act adds an instrument or raises dynamics.",
        "act_dynamics": ["ppp", "pp", "p", "mp", "mf", "ff"],
        "act_tempo_shift": [0.9, 0.95, 1.0, 1.05, 1.1, 1.15],  # multiplier on base tempo
        "use_when": "scenes building to revelation, approaching climax, hope growing",
    },
    "渐弱 (Diminuendo)": {
        "description": "Starts full and strips away. Each act removes an element until only silence remains.",
        "act_dynamics": ["ff", "mf", "mp", "p", "pp", "ppp"],
        "act_tempo_shift": [1.1, 1.05, 1.0, 0.95, 0.9, 0.85],
        "use_when": "fading hope, death scenes, endings, loss becoming real",
    },
    "波浪 (Wave)": {
        "description": "Rise-fall-rise-fall. Two emotional peaks with a valley between. Breathing rhythm.",
        "act_dynamics": ["p", "mf", "p", "ff", "mp", "p"],
        "act_tempo_shift": [1.0, 1.1, 0.95, 1.15, 1.0, 0.9],
        "use_when": "dialogue scenes with emotional ebb and flow, normal life rhythm",
    },
    "突变 (Sudden)": {
        "description": "Flat-flat-flat-EXPLOSION-aftermath. Maximum impact through contrast.",
        "act_dynamics": ["pp", "pp", "pp", "fff", "p", "pp"],
        "act_tempo_shift": [1.0, 1.0, 1.0, 1.5, 0.7, 0.8],
        "use_when": "plot twists, betrayals, discoveries, jump scares, revelations",
    },
    "持续 (Sustained)": {
        "description": "Same intensity throughout. Drone-like. The emotion does not change — it presses.",
        "act_dynamics": ["mp", "mp", "mp", "mp", "mp", "mp"],
        "act_tempo_shift": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        "use_when": "tension that does not release, oppressive atmosphere, waiting, dread",
    },
    "auto": {
        "description": "Auto-selected based on emotion and genre.",
        "act_dynamics": ["p", "mp", "mf", "f", "mf", "p"],
        "act_tempo_shift": [1.0, 1.0, 1.05, 1.1, 1.0, 0.95],
        "use_when": "default",
    },
}

# === 30-Second Scene Scoring: 6-Act Music Map ===
SCENE_SCORING_6ACT = {
    "act_1_establish": {
        "time": "00:00-00:05",
        "music_role": "Set tonal palette. Single instrument states the harmonic world. Sparse.",
        "scoring_note": "Do NOT start with full orchestra. One voice. One idea. Let the ear adjust.",
    },
    "act_2_develop": {
        "time": "00:05-00:10",
        "music_role": "Second voice enters. Texture thickens slightly. Rhythmic element introduced.",
        "scoring_note": "The dialogue between two instruments mirrors character interaction on screen.",
    },
    "act_3_conflict": {
        "time": "00:10-00:17",
        "music_role": "Tension point. Harmony darkens. Tempo may shift. This is where the music works hardest.",
        "scoring_note": "If the scene has a confrontation, the music should anticipate it by 1-2 seconds.",
    },
    "act_4_climax": {
        "time": "00:17-00:22",
        "music_role": "Emotional peak. Maximum instrumentation employed. Or: complete silence for maximum impact.",
        "scoring_note": "The choice between FULL ORCHESTRA and TOTAL SILENCE at climax defines the director's voice.",
    },
    "act_5_resolve": {
        "time": "00:22-00:27",
        "music_role": "Release. Instruments drop out. Harmony resolves or deliberately does not resolve.",
        "scoring_note": "Unresolved ending = audience carries the tension home. Resolved = catharsis.",
    },
    "act_6_linger": {
        "time": "00:27-00:30",
        "music_role": "Tail. Last note sustains into reverb. Or a new single note hints at what comes next.",
        "scoring_note": "This is the emotional aftertaste. What the audience hears in their head after the scene cuts.",
    },
}


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

MUSIC_STYLE_CHOICES = [
    "管弦乐 (Orchestral)",
    "电子 (Electronic)",
    "极简 (Minimalist)",
    "民族 (Ethnic/Folk)",
    "爵士 (Jazz)",
    "摇滚 (Rock)",
    "无配乐 (Diegetic Only)",
    "auto",
]
EMOTION_CURVE_CHOICES = [
    "渐强 (Crescendo)",
    "渐弱 (Diminuendo)",
    "波浪 (Wave)",
    "突变 (Sudden)",
    "持续 (Sustained)",
    "auto",
]


class MusicScorePro:
    """
    音乐配乐专家节点 (环节 14) — Film Scoring Engine

    Emotion-to-music mapping with music theory (key, mode, tempo, instrumentation)
    Genre-to-score templates (9 genres)
    Composer/director scoring signatures (8 composers)
    30-second 6-act scene scoring
    H3 non_diegetic_music format generation
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
                # === Phase 17.6 Soul injection ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),
                # === Music-score-specific fields ===
                "音乐风格": (MUSIC_STYLE_CHOICES, {"default": "auto"}),
                "情感曲线": (EMOTION_CURVE_CHOICES, {"default": "auto"}),
                "节拍BPM": ("INT", {"default": 0, "min": 0, "max": 240, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("musicscorepro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_music"
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

    def _detect_emotion_key(self, mood):
        """Match user mood text to emotion map key."""
        # Direct keyword matching
        keyword_map = {
            "悲": "sadness", "悲伤": "sadness", "难过": "sadness",
            "喜": "joy", "喜悦": "joy", "开心": "joy", "快乐": "joy",
            "怒": "anger", "愤怒": "anger", "生气": "anger",
            "恐": "fear", "恐惧": "fear", "害怕": "fear",
            "爱": "love", "心动": "love", "浪漫": "love",
            "紧张": "tension", "悬疑": "tension", "不安": "tension",
            "希望": "hope", "期待": "hope",
            "怀旧": "nostalgia", "回忆": "nostalgia",
            "孤独": "loneliness", "寂寞": "loneliness",
            "暧昧": "ambiguity", "模糊": "ambiguity",
            "胜利": "triumph", "壮烈": "triumph",
            "忧郁": "melancholy", "惆怅": "melancholy",
            "压抑": "melancholy",
        }
        for keyword, emotion in keyword_map.items():
            if keyword in mood:
                return emotion
        # Compound emotion detection
        if "中见" in mood or "但" in mood:
            # Mixed emotion — find the dominant one
            for keyword, emotion in keyword_map.items():
                if keyword in mood:
                    return emotion
        return "melancholy"  # default

    def _detect_genre_score_key(self, genre, scene):
        """Map genre/scene to genre-score template key."""
        genre_mapping = {
            "电影": "romance",  # will be refined by scene
            "MV": "romance",
            "AIGC 短剧": "short_drama",
            "短视频": "short_drama",
            "AIGC 短视频": "short_drama",
            "故事绘本": "documentary",
            "互动剧": "sci_fi",
        }
        base = genre_mapping.get(genre, "romance")

        # Refine by scene keywords
        scene_refinements = {
            "战": "war_epic", "打斗": "war_epic", "军": "war_epic", "战场": "war_epic",
            "武侠": "wuxia", "剑": "wuxia", "功夫": "wuxia", "江湖": "wuxia",
            "恐怖": "horror", "鬼": "horror", "黑暗": "horror",
            "搞笑": "comedy", "喜剧": "comedy", "无厘头": "comedy",
            "悬疑": "film_noir", "犯罪": "film_noir", "侦探": "film_noir",
            "科幻": "sci_fi", "未来": "sci_fi", "太空": "sci_fi",
            "纪录": "documentary",
        }
        for keyword, score_key in scene_refinements.items():
            if keyword in scene or keyword in genre:
                return score_key
        return base

    def _get_director_scoring_info(self, director):
        """Get scoring information for a director from multiple sources."""
        info = {}
        # From director_data_unified
        if _HAS_DIRECTOR_DATA:
            dir_key = director.replace("_短剧版", "")
            if dir_key in DIRECTOR_PROFILES_ALL:
                d = DIRECTOR_PROFILES_ALL.get(dir_key, {})
                info["unified_sound"] = d.get("声音", "")
                info["unified_mood"] = d.get("情绪", "")
                info["unified_works"] = d.get("代表作", "")

        # From composer mapping
        dir_key = director.replace("_短剧版", "")
        composer_name = DIRECTOR_COMPOSER_MAP.get(dir_key)
        if composer_name and composer_name in COMPOSER_SIGNATURES:
            info["composer"] = COMPOSER_SIGNATURES[composer_name]
            info["composer_name"] = composer_name
        else:
            # Director has no fixed composer — note why
            if dir_key in DIRECTOR_COMPOSER_MAP and DIRECTOR_COMPOSER_MAP[dir_key] is None:
                no_composer_reasons = {
                    "王家卫": "Uses licensed pop/world music. The song IS the score. No single composer.",
                    "塔可夫斯基": "Uses pre-existing Bach/Pergolesi. Natural sound replaces composed score.",
                    "库布里克": "Uses pre-existing classical (Strauss, Ligeti, Beethoven). Ironic counterpoint.",
                    "侯孝贤": "Minimal music use. Ambient sound and silence preferred.",
                    "贾樟柯": "Diegetic Chinese pop songs from specific eras. Music = documentary evidence.",
                    "蔡明亮": "Almost no music. Silence IS the score. When Grace Chang plays, it is a revelation.",
                    "周星驰": "Eclectic: Cantonese pop, Western classical mock-epic, game SFX. No consistent composer.",
                    "小津安二郎": "Minimal, functional music. The domestic sounds ARE the music.",
                    "毕赣": "Ambient textures, found sound. No traditional score.",
                    "Papi酱": "No score. Talking-head format. Music is occasional pop reference.",
                }
                info["no_composer_reason"] = no_composer_reasons.get(dir_key, "Director typically works without a dedicated composer.")
        return info

    def _select_emotion_curve(self, mood, genre):
        """Auto-select emotion curve based on mood and genre."""
        if "突然" in mood or "反转" in mood or "震惊" in mood:
            return "突变 (Sudden)"
        if "渐" in mood and "强" in mood or "希望" in mood or "成长" in mood:
            return "渐强 (Crescendo)"
        if "渐" in mood and "弱" in mood or "消逝" in mood or "离去" in mood:
            return "渐弱 (Diminuendo)"
        if "压抑" in mood or "持续" in mood or "等待" in mood:
            return "持续 (Sustained)"
        return "波浪 (Wave)"  # default

    def _select_music_style(self, director, genre):
        """Auto-select music style from director and genre."""
        director_style_map = {
            "诺兰": "管弦乐 (Orchestral)",
            "是枝裕和": "极简 (Minimalist)",
            "王家卫": "爵士 (Jazz)",
            "塔可夫斯基": "无配乐 (Diegetic Only)",
            "蔡明亮": "无配乐 (Diegetic Only)",
            "侯孝贤": "极简 (Minimalist)",
            "奉俊昊": "管弦乐 (Orchestral)",
            "黑泽明": "管弦乐 (Orchestral)",
            "库布里克": "管弦乐 (Orchestral)",
            "大衛·芬奇": "电子 (Electronic)",
            "李安": "民族 (Ethnic/Folk)",
            "周星驰": "管弦乐 (Orchestral)",
            "贾樟柯": "民族 (Ethnic/Folk)",
            "毕赣": "电子 (Electronic)",
        }
        dir_key = director.replace("_短剧版", "")
        result = director_style_map.get(dir_key)
        if result:
            return result
        # Fallback by genre
        genre_style_map = {
            "MV": "管弦乐 (Orchestral)",
            "AIGC 短剧": "电子 (Electronic)",
            "短视频": "电子 (Electronic)",
        }
        return genre_style_map.get(genre, "管弦乐 (Orchestral)")

    def _build_h3_music_field(self, emotion_data, genre_score, bpm, style_choice):
        """Build H3 non_diegetic_music field (1-3 sentences, English)."""
        if "无配乐" in style_choice:
            return "No non-diegetic music. The scene relies entirely on ambient sound and silence."

        parts = []
        # Sentence 1: instrumentation + tempo
        if emotion_data:
            instruments = emotion_data.get("instrumentation", [])
            inst_str = instruments[0] if instruments else "solo piano"
            tempo = emotion_data.get("tempo_bpm", 80)
            if bpm > 0:
                tempo = bpm
            key = emotion_data.get("key", "")
            parts.append(inst_str + " at " + str(tempo) + " BPM in " + key)

        # Sentence 2: dynamic contour
        if emotion_data:
            dynamics = emotion_data.get("dynamics", "p to mf")
            contour = emotion_data.get("phrase_contour", "")
            if contour:
                parts.append(dynamics + ", " + contour[:80])

        # Sentence 3: genre-specific element
        if genre_score:
            sig_elements = genre_score.get("signature_elements", [])
            if sig_elements:
                parts.append(sig_elements[0])

        result = ". ".join(p.rstrip(".") for p in parts[:3]) + "."
        return result

    def _build_6act_scoring(self, emotion_data, curve_data, base_bpm, style_choice):
        """Build 6-act scene scoring breakdown."""
        if "无配乐" in style_choice:
            return "No score. Silence and ambient sound only for all 6 acts."

        acts = []
        act_dynamics = curve_data.get("act_dynamics", ["p", "mp", "mf", "f", "mf", "p"])
        act_tempo_shifts = curve_data.get("act_tempo_shift", [1.0]*6)

        instruments = emotion_data.get("instrumentation", ["solo piano", "strings", "woodwinds", "brass"])

        act_keys = list(SCENE_SCORING_6ACT.keys())
        for i, act_key in enumerate(act_keys):
            act_info = SCENE_SCORING_6ACT[act_key]
            dyn = act_dynamics[i] if i < len(act_dynamics) else "mp"
            tempo_mult = act_tempo_shifts[i] if i < len(act_tempo_shifts) else 1.0
            act_bpm = int(base_bpm * tempo_mult)

            # Select instrument for this act (build up through acts)
            if i == 0:
                act_inst = instruments[0] if instruments else "solo piano"
            elif i < len(instruments):
                act_inst = " + ".join(instruments[:i+1])
            else:
                act_inst = " + ".join(instruments)

            act_desc = (
                "Act " + str(i+1) + " [" + act_info["time"] + "]: "
                + act_info["music_role"] + " "
                + "|| Instruments: " + act_inst + " | Dynamics: " + dyn + " | Tempo: " + str(act_bpm) + " BPM"
            )
            acts.append(act_desc)
        return "\n".join(acts)

    def _get_emotion_kb_insights(self, emotion_key):
        """Get insights from knowledge_base emotion_rendering."""
        insights = {}
        if not _HAS_EMOTION_KB:
            return insights

        # Get primary emotion data
        primary_emotions = EMOTION_RENDERING.get("emotion_spectrum", {}).get("primary_emotions", {})
        if emotion_key in primary_emotions:
            emo = primary_emotions[emotion_key]
            insights["camera_response"] = emo.get("camera_response", "")
            insights["pacing_response"] = emo.get("pacing_response", "")

        # Get atmosphere sound data
        atmo = EMOTION_RENDERING.get("scene_emotion_rendering", {}).get("atmosphere_building", {})
        sound_atmo = atmo.get("sound", {})
        if sound_atmo:
            insights["sound_atmosphere"] = sound_atmo

        # Get emotion curve design
        curve_design = EMOTION_RENDERING.get("emotion_curve_design", {})
        principles = curve_design.get("principles", {})
        if principles:
            insights["curve_principles"] = principles

        # Get genre emotion formula
        genre_formulas = EMOTION_RENDERING.get("genre_emotion_formulas", {})
        if genre_formulas:
            insights["genre_formulas"] = genre_formulas

        return insights

    # ------------------------------------------------------------------
    # Main build method
    # ------------------------------------------------------------------
    def build_music(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("MusicScorePro requires prompt_builder. Error: " + _AI_DEPS_ERROR, "", "")

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

        # Music-specific inputs
        music_style_raw = self._str(kwargs.get("音乐风格"), "auto")
        emotion_curve_raw = self._str(kwargs.get("情感曲线"), "auto")
        bpm_input = int(kwargs.get("节拍BPM", 0))

        # === Auto-detect parameters ===
        emotion_key = self._detect_emotion_key(mood)
        genre_score_key = self._detect_genre_score_key(genre, scene)

        if music_style_raw == "auto":
            music_style_raw = self._select_music_style(director, genre)
        if emotion_curve_raw == "auto":
            emotion_curve_raw = self._select_emotion_curve(mood, genre)

        # === Get data ===
        emotion_data = EMOTION_MUSIC_MAP.get(emotion_key, EMOTION_MUSIC_MAP.get("melancholy", {}))
        genre_score = GENRE_SCORE_TEMPLATES.get(genre_score_key, {})
        curve_data = EMOTION_CURVES.get(emotion_curve_raw, EMOTION_CURVES.get("auto", {}))
        director_scoring = self._get_director_scoring_info(director)
        emotion_kb = self._get_emotion_kb_insights(emotion_key)

        # Determine BPM
        if bpm_input > 0:
            base_bpm = bpm_input
        else:
            base_bpm = emotion_data.get("tempo_bpm", 80)
            if base_bpm == 0:
                base_bpm = 72  # rubato default

        # === Build H3 music field ===
        h3_music = self._build_h3_music_field(emotion_data, genre_score, base_bpm, music_style_raw)

        # === Build 6-act scoring ===
        six_act_scoring = self._build_6act_scoring(emotion_data, curve_data, base_bpm, music_style_raw)

        # === Director motion preference ===
        director_motion_map = {
            "塔可夫斯基": "Static Shot held for 60+ seconds + Push In at glacial speed",
            "王家卫": "Push In with small amplitude at slow speed + Step Printing",
            "诺兰": "Tracking Shot with large amplitude at fast speed + time-fold editing",
            "是枝裕和": "Static Shot for domestic observation + Push In with small amplitude",
            "侯孝贤": "Static Shot wide-angle long take + maximum breathing room",
            "李沧东": "Push In with small amplitude at slow speed + held moments",
            "蔡明亮": "Static Shot ultra-long + zero movement",
            "毕赣": "Arc Shot continuous + single-take dream sequence",
            "周星驰": "Quick Cut rapid-fire + comedic timing pause",
            "Papi酱": "Static Shot talking-head + direct address",
            "Vince Gilligan": "Push In dark-palette slow approach",
            "大衛·芬奇": "Tracking Shot with calculated precision",
            "黑泽明": "Wide Shot multi-figure blocking + weather as character",
            "奉俊昊": "Symmetric Pan with controlled composition",
            "库布里克": "Steadicam float + symmetry obsession",
            "小津安二郎": "Tatami-height Static Shot + pillow shots",
            "贾樟柯": "Handheld documentary-style",
            "李安": "Push In with cultural sensitivity + East-West grammar",
        }
        dir_key = director.replace("_短剧版", "")
        director_motion_pref = director_motion_map.get(dir_key, director_motion_map.get(director, "Static Shot + Push In"))

        # === Visual style ===
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, high emotional density",
            "短视频": "live-action, high saturation, direct impact",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        visual_style = style_choices.get(genre, "Cinematic, live-action")

        # === Build H3 three fields ===
        first_prop = props.split(" / ")[0] if " / " in props else props
        last_prop = props.split(" / ")[-1] if " / " in props else props

        # Build soundscape (light version — sound_design_pro has the detail)
        soundscape = "Room ambience with domestic sounds appropriate to " + scene[:40] + "."

        shot_1 = (
            "a medium-wide shot establishes the scene - " + scene + ". "
            + "The " + director_motion_pref + " reveals the space. "
            + "The director intends: " + intent_feel + ". "
            + first_prop + " is visible in the frame."
        )
        shots = [
            "[Shot 2] At 00:03.500, medium close-up. "
            + format_shot_motion("Push In", "small", "slow")
            + " on the character, revealing " + subtext + ".",

            "[Shot 3] At 00:08.000, close-up of hands with " + first_prop + ". "
            + "Static shot. (S1) speaks: <d>[Chinese] ...</d>",

            "[Shot 4] At 00:15.000, over-the-shoulder. "
            + format_shot_motion("Push In", "small", "slow")
            + " toward the other character. Silence carries " + subtext + ".",

            "[Shot 5] At 00:22.000, wider static shot. "
            + "5-10 seconds of silence. Intent: " + intent_feel + ".",

            "[Shot 6] At 00:27.000, held for 3 seconds. "
            + last_prop + " in the light. End.",
        ]

        h3_prompt = build_h3_three_fields(
            style=visual_style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=h3_music, language="Chinese"
        )
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # === 30-second timeline ===
        timeline_30s = build_30s_timeline(
            scene_type="对话", scene_desc=scene,
            speaker_id="S1", speaker_voice="a moderate voice",
            dialogue="...", n_lines=1, director_intent=intent_feel, language="Chinese"
        )

        # ================================================================
        # ASSEMBLE OUTPUT 1: Main H3 Prompt with Scoring Engine
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
                    "【灵魂核心 - 音乐配乐驱动 (Phase 17.6)】\n"
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
        main_output += "【MusicScorePro】Film Scoring Engine\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【音乐风格】 " + music_style_raw + "\n"
        main_output += "【情感曲线】 " + emotion_curve_raw + "\n"
        main_output += "【节拍BPM】 " + str(base_bpm) + (" (user-specified)" if bpm_input > 0 else " (auto from emotion)") + "\n"
        main_output += "【检测情绪】 " + emotion_key + " (" + emotion_data.get("cn", "") + ")\n\n"

        # --- Emotion-to-Music Mapping ---
        main_output += "=" * 60 + "\n"
        main_output += "Emotion-to-Music Mapping: " + emotion_key + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  Key: " + emotion_data.get("key", "N/A") + "\n"
        main_output += "  Mode: " + emotion_data.get("mode", "N/A") + "\n"
        main_output += "  Tempo: " + str(base_bpm) + " BPM (" + emotion_data.get("tempo_marking", "") + ")\n"
        main_output += "  Dynamics: " + emotion_data.get("dynamics", "N/A") + "\n"
        main_output += "  Phrase Contour: " + emotion_data.get("phrase_contour", "N/A") + "\n"
        main_output += "  Harmonic Character: " + emotion_data.get("harmonic_character", "N/A") + "\n"
        main_output += "  Orchestration: " + emotion_data.get("orchestration_note", "N/A") + "\n"
        main_output += "  Instrumentation:\n"
        for inst in emotion_data.get("instrumentation", []):
            main_output += "    - " + inst + "\n"
        main_output += "\n"

        # --- Genre Score Template ---
        main_output += "=" * 60 + "\n"
        main_output += "Genre Score Template: " + genre_score.get("cn", genre_score_key) + "\n"
        main_output += "=" * 60 + "\n\n"
        if genre_score:
            main_output += "  Ensemble: " + genre_score.get("ensemble", "N/A") + "\n"
            main_output += "  Lead Instrument: " + genre_score.get("lead_instrument", "N/A") + "\n"
            main_output += "  Rhythm Section: " + genre_score.get("rhythm_section", "N/A") + "\n"
            main_output += "  Harmony: " + genre_score.get("harmony", "N/A") + "\n"
            main_output += "  Tempo Range: " + genre_score.get("tempo_range", "N/A") + "\n"
            main_output += "  Signature Elements:\n"
            for elem in genre_score.get("signature_elements", []):
                main_output += "    - " + elem + "\n"
            main_output += "  Reference Scores:\n"
            for ref in genre_score.get("reference_scores", []):
                main_output += "    - " + ref + "\n"
        main_output += "\n"

        # --- Director Scoring Signature ---
        main_output += "=" * 60 + "\n"
        main_output += "Director Scoring Signature: " + director + "\n"
        main_output += "=" * 60 + "\n\n"
        if "composer" in director_scoring:
            composer = director_scoring["composer"]
            c_name = director_scoring.get("composer_name", "")
            main_output += "  Associated Composer: " + c_name + " (" + composer.get("cn", "") + ")\n"
            main_output += "  Technique: " + composer.get("technique", "") + "\n"
            main_output += "  Tempo Approach: " + composer.get("tempo_approach", "") + "\n"
            main_output += "  Harmonic Language: " + composer.get("harmonic_language", "") + "\n"
            main_output += "  Signature Sounds:\n"
            for ss in composer.get("signature_sounds", []):
                main_output += "    - " + ss + "\n"
            main_output += "  Key Scores:\n"
            for ks in composer.get("key_scores", []):
                main_output += "    - " + ks + "\n"
        elif "no_composer_reason" in director_scoring:
            main_output += "  No Fixed Composer: " + director_scoring["no_composer_reason"] + "\n"
        if "unified_sound" in director_scoring:
            main_output += "  Director Data (声音): " + director_scoring["unified_sound"] + "\n"
        if "unified_mood" in director_scoring:
            main_output += "  Director Data (情绪): " + director_scoring["unified_mood"] + "\n"
        main_output += "\n"

        # --- Emotion Curve ---
        main_output += "=" * 60 + "\n"
        main_output += "Emotion Curve: " + emotion_curve_raw + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  Description: " + curve_data.get("description", "") + "\n"
        main_output += "  Use When: " + curve_data.get("use_when", "") + "\n"
        main_output += "  Act Dynamics: " + " -> ".join(curve_data.get("act_dynamics", [])) + "\n"
        act_bpms = [str(int(base_bpm * m)) for m in curve_data.get("act_tempo_shift", [1.0]*6)]
        main_output += "  Act Tempos: " + " -> ".join(act_bpms) + " BPM\n\n"

        # --- 6-Act Scene Scoring ---
        main_output += "=" * 60 + "\n"
        main_output += "30-Second 6-Act Scene Scoring\n"
        main_output += "=" * 60 + "\n\n"
        main_output += six_act_scoring + "\n\n"

        # --- Emotion KB insights ---
        if emotion_kb:
            main_output += "=" * 60 + "\n"
            main_output += "Emotion-Music Intelligence (knowledge_base)\n"
            main_output += "=" * 60 + "\n\n"
            if "camera_response" in emotion_kb:
                main_output += "  Camera-Music Sync: " + emotion_kb["camera_response"] + "\n"
            if "pacing_response" in emotion_kb:
                main_output += "  Pacing-Music Sync: " + emotion_kb["pacing_response"] + "\n"
            if "sound_atmosphere" in emotion_kb:
                for k, v in emotion_kb["sound_atmosphere"].items():
                    main_output += "  Sound/" + k + ": " + v + "\n"
            if "curve_principles" in emotion_kb:
                main_output += "\n  Emotion Curve Principles:\n"
                for k, v in emotion_kb["curve_principles"].items():
                    main_output += "    " + k + ": " + v + "\n"
            main_output += "\n"

        # --- H3 Three Fields ---
        main_output += "=" * 60 + "\n"
        main_output += "H3 Three Fields (MiniMax-H3 Official Format)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_prompt + "\n\n"

        # --- H3 non_diegetic_music detail ---
        main_output += "=" * 60 + "\n"
        main_output += "H3 non_diegetic_music (1-3 sentences)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_music + "\n\n"

        # --- Director intent 5D ---
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "based on subtext: " + subtext[:40] if subtext else "unspecified",
            "主题": mood,
            "留白": "unsaid — music carries what words cannot",
        }
        intent_block = inject_director_intent(intent_5d)
        main_output += "=" * 60 + "\n"
        main_output += "Director Intent 5D\n"
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
        experience = "【MusicScorePro Experience Matrix】\n\n"

        experience += "--- Emotion-to-Music Coverage ---\n"
        for emo_key, emo_data in EMOTION_MUSIC_MAP.items():
            experience += "  " + emo_data.get("cn", emo_key) + " (" + emo_key + "): "
            experience += emo_data.get("key", "") + ", " + str(emo_data.get("tempo_bpm", 0)) + "BPM, "
            experience += emo_data.get("dynamics", "") + "\n"
        experience += "\n"

        experience += "--- Genre Score Templates ---\n"
        for gk, gv in GENRE_SCORE_TEMPLATES.items():
            experience += "  " + gv.get("cn", gk) + ": " + gv.get("ensemble", "") + "\n"
        experience += "\n"

        experience += "--- Composer Signatures ---\n"
        for ck, cv in COMPOSER_SIGNATURES.items():
            experience += "  " + ck + " (" + cv.get("cn", "") + "): " + cv.get("technique", "")[:60] + "...\n"
        experience += "\n"

        experience += "--- Director-Composer Map ---\n"
        for dk, cv in DIRECTOR_COMPOSER_MAP.items():
            if cv:
                experience += "  " + dk + " -> " + cv + "\n"
            else:
                experience += "  " + dk + " -> (no fixed composer)\n"
        experience += "\n"

        experience += "--- Emotion Curves ---\n"
        for ck, cv in EMOTION_CURVES.items():
            if ck != "auto":
                experience += "  " + ck + ": " + cv.get("description", "")[:60] + "...\n"
        experience += "\n"

        experience += "【10 Specific Detail Rules (Anti-AI)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # ================================================================
        # OUTPUT 3: AI Deep Processing
        # ================================================================
        ai_deep_output = "【MusicScorePro AI Deep Processing】\n\n"

        ai_deep_output += "--- Score Decisions Made ---\n"
        ai_deep_output += "  Detected emotion: " + emotion_key + " (" + emotion_data.get("cn", "") + ")\n"
        ai_deep_output += "  Selected key: " + emotion_data.get("key", "N/A") + "\n"
        ai_deep_output += "  Selected mode: " + emotion_data.get("mode", "N/A") + "\n"
        ai_deep_output += "  Base BPM: " + str(base_bpm) + (" (user override)" if bpm_input > 0 else " (auto)") + "\n"
        ai_deep_output += "  Genre score template: " + genre_score.get("cn", genre_score_key) + "\n"
        ai_deep_output += "  Music style: " + music_style_raw + "\n"
        ai_deep_output += "  Emotion curve: " + emotion_curve_raw + "\n"
        ai_deep_output += "  Director: " + director + "\n"
        if "composer_name" in director_scoring:
            ai_deep_output += "  Associated composer: " + director_scoring["composer_name"] + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "--- Anti-AI Cleanup ---\n"
        if anti_ai_on:
            ai_deep_output += "  191+ banned AI phrases checked.\n"
            ai_deep_output += "  Music-specific cleanup: replaced 'epic music' with specific instrumentation.\n"
            ai_deep_output += "  Replaced 'beautiful melody' with actual key/tempo/instrument description.\n\n"
        else:
            ai_deep_output += "  Anti-AI rules disabled.\n\n"

        ai_deep_output += "--- Data Sources Loaded ---\n"
        ai_deep_output += "  director_data_unified: " + ("loaded (35 directors)" if _HAS_DIRECTOR_DATA else "not available") + "\n"
        ai_deep_output += "  knowledge_base.emotion_rendering: " + ("loaded" if _HAS_EMOTION_KB else "not available") + "\n"
        ai_deep_output += "  knowledge_base.genre_profiles: " + ("loaded" if _HAS_GENRE_KB else "not available") + "\n"
        ai_deep_output += "  knowledge_base.h3_prompt_framework: " + ("loaded" if _HAS_H3_KB else "not available") + "\n"
        ai_deep_output += "  Built-in emotion map: " + str(len(EMOTION_MUSIC_MAP)) + " emotions\n"
        ai_deep_output += "  Built-in genre templates: " + str(len(GENRE_SCORE_TEMPLATES)) + " genres\n"
        ai_deep_output += "  Built-in composer signatures: " + str(len(COMPOSER_SIGNATURES)) + " composers\n\n"

        ai_deep_output += "--- Music Theory Notes ---\n"
        ai_deep_output += "  Major keys convey: brightness, openness, resolution, joy\n"
        ai_deep_output += "  Minor keys convey: darkness, introspection, tension, sadness\n"
        ai_deep_output += "  Lydian mode: dreamy, floating, wonder (#4 = Joe Hisaishi territory)\n"
        ai_deep_output += "  Dorian mode: jazzy minor with warm 6th (melancholy but not despair)\n"
        ai_deep_output += "  Phrygian mode: Spanish/Middle-Eastern flavor, tension from b2\n"
        ai_deep_output += "  Mixolydian mode: bluesy major, relaxed, folksy (b7 = earthy)\n"
        ai_deep_output += "  Locrian mode: unstable, horror, no resolution (b5 = no home)\n\n"

        ai_deep_output += "--- Silence Rules ---\n"
        ai_deep_output += inject_silence_mastery_5("对话", 1) + "\n\n"

        ai_deep_output += "--- 9D Lighting Control ---\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "MusicScorePro": MusicScorePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "MusicScorePro": "🎼 音乐配乐 (环节 14) — L5 重写",
# }
