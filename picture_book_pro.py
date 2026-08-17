# -*- coding: utf-8 -*-
"""
PictureBookPro - 故事绘本专家节点 (环节 40)
====================================================
故事绘本 (Picture Book) 导演专业节点 - 真正的绘本领域专家系统

核心能力:
1. 年龄适配内容设计 (0-3/3-6/6-9/9-12/全年龄 5 档)
2. 绘本画风决策系统 (水彩/剪纸/油画/数字/蜡笔/混合媒材 6 型)
3. 页面布局与节奏 (张力-释放-攀升-高潮-收束)
4. 儿童角色设计 (头身比/表情/轮廓/标识)
5. 绘本叙事结构 (3 幕/重复变奏/累积/环形结尾)
6. H3 三大字段动态生成
7. 30 秒场景单元分镜 (绘本语境)
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

# === 绘本知识库 ===
try:
    from knowledge_base.children_content_styles import (
        CHILDREN_CONTENT_STYLES, AGE_STYLE_MATRIX,
        get_children_style, get_age_style_recommendations,
    )
    _HAS_CHILDREN_STYLES = True
except Exception:
    _HAS_CHILDREN_STYLES = False

try:
    from knowledge_base.picture_book_styles import (
        PICTURE_BOOK_STYLES, PICTURE_BOOK_NARRATIVE,
        get_picture_book_style,
    )
    _HAS_BOOK_STYLES = True
except Exception:
    _HAS_BOOK_STYLES = False

# === 灵魂注入 ===
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False


# ============================================================
# 绘本领域专有数据
# ============================================================

GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = [
    "塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和",
    "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安",
    "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇",
    "周星驰", "Papi酱", "诺兰_短剧版",
]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# --- 目标年龄 ---
AGE_GROUPS = ["0-3岁 (婴幼儿)", "3-6岁 (学前)", "6-9岁 (低龄)", "9-12岁 (高龄)", "全年龄", "auto"]

# --- 绘本风格 ---
BOOK_STYLES = ["水彩 (Watercolor)", "剪纸 (Paper-cut)", "油画 (Oil painting)",
               "数字 (Digital)", "蜡笔 (Crayon)", "混合媒材 (Mixed media)", "auto"]

# --- 年龄 -> 内容设计规则 ---
AGE_CONTENT_DESIGN = {
    "0-3": {
        "cn": "0-3岁 婴幼儿",
        "visual": "Simple shapes, primary colors, minimal elements, high contrast, large subjects",
        "text": "1-2 words per page maximum, onomatopoeia, repetition as structure",
        "focus": "Sensory: texture, sound, shape, color, touch",
        "complexity": "Single subject + single action per spread, no subplot",
        "pacing": "Repetition IS the narrative (peek-a-boo, where-is-it)",
        "emotions": "Basic: happy, sad, surprised, scared (resolved immediately)",
        "taboo": "No real danger, no complex cause-effect, no text walls",
        "head_body_ratio": "1:2 (very large head, small body, maximum cute)",
        "expression_clarity": "Maximum exaggeration: wide eyes, big smile, simple",
        "reference": "《小熊宝宝》, 《蹦》, 'Dear Zoo', 'Peek-a-Boo!'",
    },
    "3-6": {
        "cn": "3-6岁 学前",
        "visual": "Clear characters, action-driven compositions, 3-6 primary colors, visual focus",
        "text": "5-10 words per page, complete simple sentences, action verbs",
        "focus": "Social: friendship, family, sharing, emotions, moral lessons, humor",
        "complexity": "Simple beginning-middle-end, one main problem, one solution",
        "pacing": "Small surprises on page turns, humor beats, satisfying resolution",
        "emotions": "Expanded: empathy, jealousy, pride, shame (externalized clearly)",
        "taboo": "No ambiguous endings, no irony, no complex metaphor",
        "head_body_ratio": "1:2.5 (large head, slightly more body, still cute)",
        "expression_clarity": "Clear facial expressions, body language supports emotion",
        "reference": "《好饿的毛毛虫》, 《我爸爸》, 'Where the Wild Things Are'",
    },
    "6-9": {
        "cn": "6-9岁 低龄",
        "visual": "Complex compositions, multiple layers of detail, visual subplots in backgrounds",
        "text": "20-30 words per page, dialogue, emotional depth, chapter-like sections",
        "focus": "Growth: courage, identity, problem-solving, friendship complexity",
        "complexity": "Complete narrative arc, 2-3 threads, foreshadowing, payoff",
        "pacing": "True tension-release cycle, cliffhanger page turns, earned climax",
        "emotions": "Nuanced: bittersweet, conflicted, nostalgic, determined",
        "taboo": "Avoid preaching (show don't tell), no gratuitous fear",
        "head_body_ratio": "1:3 (proportional but still stylized)",
        "expression_clarity": "Subtle mixed expressions allowed, body language nuance",
        "reference": "《神奇树屋》, 《西游记》绘本版, 'The Fantastic Flying Books'",
    },
    "9-12": {
        "cn": "9-12岁 高龄",
        "visual": "Sophisticated composition, visual metaphor, symbolic backgrounds, art-quality illustration",
        "text": "30-50 words per page, literary language, irony, multiple interpretations",
        "focus": "Identity: moral grey areas, societal themes, self-discovery, injustice",
        "complexity": "Multi-layered narrative, unreliable hints, metaphorical meaning",
        "pacing": "Literary rhythm, reflection pages, visual poetry, ambiguous moments",
        "emotions": "Full adult spectrum adapted: loss, sacrifice, moral conflict, hope despite darkness",
        "taboo": "Avoid condescension, childish aesthetics, oversimplification",
        "head_body_ratio": "1:4-5 (near-realistic proportions, stylized)",
        "expression_clarity": "Subtle, ambiguous expressions encouraged, context-dependent",
        "reference": "《草房子》, Shaun Tan 'The Arrival', 'The Invention of Hugo Cabret'",
    },
    "all_ages": {
        "cn": "全年龄",
        "visual": "Layered depth: simple surface for young, hidden details for older readers",
        "text": "Simple enough for 4-year-old read-aloud, deep enough for adult reflection",
        "focus": "Universal: love, loss, belonging, wonder, the nature of time",
        "complexity": "Surface narrative + subtext layer + symbolic layer",
        "pacing": "Picture book rhythm with adult emotional weight",
        "emotions": "Simple on surface, devastating underneath",
        "taboo": "None (but execution must serve all ages simultaneously)",
        "head_body_ratio": "1:3 (balanced, appealing across ages)",
        "expression_clarity": "Readable at surface, ambiguous at depth",
        "reference": "'The Giving Tree', 《猜猜我有多爱你》, 'The Red Tree'",
    },
}

# --- 画风决策系统 ---
ART_STYLE_SYSTEM = {
    "watercolor": {
        "cn": "水彩",
        "mood": "Soft, dreamy, gentle, nostalgic, warm, fluid",
        "technique": "Wet-on-wet washes, color bleeding at edges, paper texture visible",
        "palette": "Transparent layers, 2-3 primary hues with white of paper as highlight",
        "texture": "Paper grain shows through, soft edges, water bloom marks",
        "best_for": "Nature, animals, gentle emotions, seasons, memory stories",
        "avoid": "Hard edges, solid blocks of color, over-saturated pigments",
        "execution_notes": "Leave 30-40% white space, let colors bleed into each other at boundaries, "
                          "use dry brush for texture on tree bark/fur, wet wash for sky/water",
        "masters": "Beatrix Potter (Peter Rabbit), Quentin Blake (Roald Dahl), "
                  "Eric Carle (tissue paper collage with watercolor base)",
    },
    "paper_cut": {
        "cn": "剪纸",
        "mood": "Bold, folk-art, festive, cultural, layered, graphic",
        "technique": "Cut shapes with visible paper edges, layered depth from overlapping",
        "palette": "Strong contrast, traditional (red/black/gold) or modern bold primaries",
        "texture": "Paper fiber visible at edges, shadow between layers, flat color within shapes",
        "best_for": "Cultural stories, folk tales, festival themes, silhouette narratives",
        "avoid": "Gradients within shapes, photorealistic detail, soft transitions",
        "execution_notes": "Negative space (the holes) is as important as positive space. "
                          "Each layer adds depth. Symmetry creates folk-art feel. "
                          "Paper edge imperfections add handmade authenticity.",
        "masters": "Eric Carle (painted tissue paper), Lois Ehlert (bold color paper), "
                  "Chinese folk paper-cut tradition, shadow puppet aesthetics",
    },
    "oil_painting": {
        "cn": "油画",
        "mood": "Rich, classical, emotional weight, dramatic, timeless",
        "technique": "Thick impasto strokes, glazing layers, visible brush direction",
        "palette": "Deep, rich colors with warm undertones, Rembrandt-like chiaroscuro possible",
        "texture": "Canvas weave visible, paint thickness varies, palette knife marks",
        "best_for": "Epic tales, historical stories, emotional depth, nature grandeur, 9-12 age",
        "avoid": "Flat uniform coverage, primary-only colors, cartoon proportions",
        "execution_notes": "Brush strokes follow form (curve with the body, sweep with the sky). "
                          "Background softer (sfumato), foreground sharper. "
                          "Light source consistent and dramatic across all pages.",
        "masters": "Chris Van Allsburg (Jumanji, Polar Express), "
                  "Kadir Nelson (historical picture books), classical European illustration",
    },
    "digital": {
        "cn": "数字",
        "mood": "Clean, modern, consistent, animation-ready, versatile",
        "technique": "Vector or raster digital painting, clean lines, gradient fills",
        "palette": "Flexible, from pastel to vivid, consistent across pages",
        "texture": "Smooth or simulated texture brushes, consistent edge quality",
        "best_for": "Modern stories, STEM themes, character series, animation spinoffs",
        "avoid": "Over-rendering, uncanny valley realism, inconsistent style between pages",
        "execution_notes": "Consistency is the superpower of digital. "
                          "Character model sheet before starting. "
                          "Lighting and shadow system must be unified. "
                          "Export quality: 300 DPI minimum for print.",
        "masters": "Oliver Jeffers (minimalist digital), Mo Willems (Elephant & Piggie), "
                  "modern children's app aesthetics",
    },
    "crayon": {
        "cn": "蜡笔",
        "mood": "Childlike, warm, imperfect, personal, relatable, innocent",
        "technique": "Visible wax strokes, color layering, paper texture through thin areas",
        "palette": "Warm, slightly muted by wax overlay, 6-12 crayon colors",
        "texture": "Waxy sheen, uneven coverage, scribble energy, white specks from paper grain",
        "best_for": "Personal stories, child-narrator, family, feelings, 0-6 age group",
        "avoid": "Precision, clean edges, photorealism, cool/clinical palette",
        "execution_notes": "Imperfection IS the aesthetic. Going outside the lines is warmth. "
                          "Pressure variation creates light/dark within single strokes. "
                          "Mix hard press (dark, waxy) with light press (textured, grainy). "
                          "White crayon on colored paper for highlights.",
        "masters": "Todd Parr (bold simple crayon), "
                  "children's own drawings as inspiration (authentic child perspective), "
                  "Harold and the Purple Crayon (Crockett Johnson)",
    },
    "mixed_media": {
        "cn": "混合媒材",
        "mood": "Sophisticated, surprise, textural variety, layered, collage energy",
        "technique": "Combine 2+ media: watercolor base + collage + ink line + found objects",
        "palette": "Depends on combination, but contrast between media creates visual interest",
        "texture": "Maximum variety: smooth paint + rough paper + glossy photo + matte ink",
        "best_for": "Art-forward stories, 6-12 age, museum themes, dream/imagination stories",
        "avoid": "Random combination without purpose, visual chaos, too many media in one spread",
        "execution_notes": "Each medium should serve a narrative purpose: "
                          "watercolor for emotion, collage for reality, ink for structure. "
                          "Limit to 2-3 media per spread to avoid visual noise. "
                          "One medium dominates, others accent.",
        "masters": "Shaun Tan (The Lost Thing), Lauren Child (Charlie and Lola), "
                  "Hervé Tullet (Press Here - interactive mixed media)",
    },
}

# --- 页面布局与节奏 ---
PAGE_LAYOUT_PACING = {
    "spread_rhythm": {
        "description": "每个对开页(spread)有自己的情感节拍",
        "pattern": "tension -> release -> build -> climax -> resolution",
        "rules": [
            "Right page carries the moment of reveal (page turn surprise)",
            "Left page sets up anticipation for the right page reveal",
            "Double-spread (full bleed) = emotional climax",
            "Vignette (small image, white space) = pause, breath, reflection",
            "Text placement follows eye flow: top-left to bottom-right (LTR), top-right to bottom-left (RTL)",
        ],
    },
    "text_image_relationship": {
        "embedded": "Text within the illustration (speech bubble, sign, object label) - younger audiences",
        "separated": "Text block below or beside image, clear separation - standard picture book",
        "speech_bubble": "Dialogue-driven, comic-influenced, dynamic and fun - 3-9 age",
        "integrated": "Text IS the illustration (words curve, grow, shrink with meaning) - art books",
        "wordless": "No text at all, pure visual narrative - all ages, requires strong visual literacy",
    },
    "visual_continuity": {
        "character_position": "Character consistently enters from left, moves right (progress direction in LTR culture)",
        "background_progression": "Backgrounds subtly change to show time/journey: dawn->noon->dusk->night",
        "time_indicators": "Seasonal changes, clock positions, shadow length, clothing layers",
        "color_arc": "Color palette evolves with story: cool/muted(problem) -> warm/saturated(resolution)",
    },
    "page_turn_surprise": {
        "description": "The most powerful tool in a picture book is what the reader cannot see until they turn the page",
        "techniques": [
            "Show cause on recto, hide effect until verso of next spread",
            "Ask a question in text, answer only in the next page's image",
            "Character looks offscreen right -> reader turns page to see what they see",
            "Zoom in tight -> page turn reveals the wide context (or reverse)",
            "Sound word (BOOM!) on last line -> page turn reveals the aftermath",
        ],
    },
}

# --- 角色设计规则 ---
CHARACTER_DESIGN_RULES = {
    "head_body_ratio": {
        "0-3_target": "1:2 ratio (巨大头部, 极小身体, 最大化可爱感)",
        "3-6_target": "1:2.5 ratio (大头, 稍多身体, 仍然可爱)",
        "6-9_target": "1:3 ratio (比例适中但仍风格化, 可读性强)",
        "9-12_target": "1:4-5 ratio (接近真实但保持风格化, 尊重读者)",
        "rule": "Younger audience = larger head ratio = more instant recognition and empathy",
    },
    "expression_system": {
        "0-3": "Maximum 4 expressions: happy, sad, surprised, scared. Each VERY distinct.",
        "3-6": "6-8 expressions: add angry, proud, shy, confused. Still clear and exaggerated.",
        "6-9": "Full range but readable: mixed emotions allowed (happy-sad), body language carries weight.",
        "9-12": "Subtle, ambiguous expressions OK. A single tear, a half-smile. Context-dependent reading.",
    },
    "silhouette_test": {
        "rule": "Every character must be recognizable in solid black silhouette",
        "how": "Distinctive shape: ears, hat, tail, posture, size ratio",
        "why": "Children identify characters by shape before detail. Silhouette = instant recognition.",
        "examples": "Miffy (square ears), Peppa (snout profile), Totoro (round+ears+umbrella)",
    },
    "costume_markers": {
        "rule": "Each character has 1-2 identification markers that NEVER change",
        "examples": [
            "Paddington: blue coat + red hat (remove either and he's unrecognizable)",
            "Eloise: black hair bow + suspenders",
            "Madeline: yellow hat + blue coat",
            "Curious George: no clothes (the monkey IS the costume)",
        ],
        "application": "Define marker in page 1, maintain through ALL pages without exception",
    },
}

# --- 绘本叙事结构 ---
NARRATIVE_STRUCTURES_BOOK = {
    "classic_3act": {
        "cn": "经典三幕式",
        "description": "Classic 3-act structure compressed into picture book page count",
        "pages_12": {
            "setup": "Pages 1-3: World, character, normal life, the want",
            "problem": "Pages 4-6: The problem arrives, the want is blocked",
            "attempts": "Pages 7-9: Tries to solve, fails, tries again, escalates",
            "resolution": "Pages 10-11: The solution, the change, the growth",
            "closing": "Page 12: Return to opening image WITH the change visible",
        },
        "pages_24": {
            "setup": "Pages 1-6: Richer world-building, character relationships established",
            "problem": "Pages 7-10: Problem develops with complications",
            "attempts": "Pages 11-17: Multiple attempts, allies, obstacles, midpoint twist",
            "resolution": "Pages 18-22: Climax, revelation, transformation",
            "closing": "Pages 23-24: Denouement, circular return, new normal",
        },
        "reference": "'Where the Wild Things Are' (Sendak), '《逃家小兔》'",
    },
    "repetition_with_variation": {
        "cn": "重复变奏式 (毛毛虫模式)",
        "description": "Each page repeats a pattern with ONE element changed",
        "structure": [
            "Page 1: Establish the pattern (On Monday, he ate through ONE apple)",
            "Pages 2-N: Repeat pattern, change ONE variable each time (quantity, day, food)",
            "Penultimate page: Break the pattern (he ate too much! stomachache!)",
            "Final page: Transform (cocoon -> butterfly, quantity -> quality)",
        ],
        "power": "Repetition = security for young readers. Variation = delight. Pattern break = climax.",
        "reference": "'The Very Hungry Caterpillar' (Carle), '《好饿的毛毛虫》', 'Brown Bear, Brown Bear'",
    },
    "cumulative": {
        "cn": "累积叠加式",
        "description": "Each page adds one element to a growing list/scene",
        "structure": [
            "Page 1: Element A alone",
            "Page 2: Element A + Element B",
            "Page 3: Element A + B + C",
            "...",
            "Climax page: ALL elements visible together (visual payoff of accumulation)",
            "Resolution: Elements disperse OR transform into something new",
        ],
        "power": "Memory game for readers. Visual complexity grows satisfyingly. Climax is overwhelming fullness.",
        "reference": "'This Is the House That Jack Built', '《拔萝卜》', 'The Napping House'",
    },
    "circular_ending": {
        "cn": "环形结尾",
        "description": "Final page echoes the opening image, but with a visible change",
        "technique": [
            "Opening: Character sits alone under a tree, looking away",
            "Story happens...",
            "Closing: Character sits under THE SAME tree, but now with a friend, looking at reader",
            "The change is small but unmistakable: a new object, a new expression, a new companion",
        ],
        "power": "Completion satisfies. Change within sameness proves growth. Reader sees the journey.",
        "reference": "'Where the Wild Things Are' (supper was still hot), '《猜猜我有多爱你》'",
    },
}


def _get_age_key(age_str):
    """Extract age key from Chinese label."""
    mapping = {
        "0-3岁 (婴幼儿)": "0-3", "3-6岁 (学前)": "3-6",
        "6-9岁 (低龄)": "6-9", "9-12岁 (高龄)": "9-12",
        "全年龄": "all_ages",
    }
    return mapping.get(age_str, "3-6")


def _get_style_key(style_str):
    """Extract style key from Chinese label."""
    mapping = {
        "水彩 (Watercolor)": "watercolor", "剪纸 (Paper-cut)": "paper_cut",
        "油画 (Oil painting)": "oil_painting", "数字 (Digital)": "digital",
        "蜡笔 (Crayon)": "crayon", "混合媒材 (Mixed media)": "mixed_media",
    }
    return mapping.get(style_str, "watercolor")


def _infer_age_from_scene(scene, mood):
    """Heuristic: infer target age from scene/mood text."""
    text = (scene + " " + mood).lower()
    if any(w in text for w in ["婴儿", "宝宝", "baby", "peek", "简单", "重复"]):
        return "0-3"
    if any(w in text for w in ["幼儿园", "小朋友", "分享", "kindergarten"]):
        return "3-6"
    if any(w in text for w in ["冒险", "勇气", "成长", "小学", "adventure"]):
        return "6-9"
    if any(w in text for w in ["青春", "复杂", "哲学", "社会", "identity"]):
        return "9-12"
    return "3-6"


def _infer_style_from_scene(scene, mood):
    """Heuristic: infer art style from scene/mood text."""
    text = (scene + " " + mood).lower()
    if any(w in text for w in ["民间", "节庆", "剪纸", "folk", "传统"]):
        return "paper_cut"
    if any(w in text for w in ["古典", "史诗", "厚重", "oil", "classical"]):
        return "oil_painting"
    if any(w in text for w in ["现代", "科技", "digital", "机器人"]):
        return "digital"
    if any(w in text for w in ["蜡笔", "涂鸦", "crayon", "childlike"]):
        return "crayon"
    if any(w in text for w in ["拼贴", "混合", "collage", "mixed"]):
        return "mixed_media"
    return "watercolor"


def _build_page_plan(total_pages, age_key, scene, props, mood, subtext, intent_feel):
    """Generate a page-by-page plan based on total pages and 3-act structure.
    V13.3: problem/resolution derived from scene characters+props (real story), not mood/intent."""
    age_data = AGE_CONTENT_DESIGN.get(age_key, AGE_CONTENT_DESIGN["3-6"])
    words_per_page = age_data["text"].split(",")[0] if "," in age_data["text"] else age_data["text"]

    # V13.3: 解析场景角色/物件, 构建真实的故事问题与解决
    try:
        from aggregator.scene_engine import parse_scene as _ps_b
        _pb = _ps_b(scene) if scene else {}
    except Exception:
        _pb = {}
    _chars = _pb.get("characters") or ["the hero"]
    _hero = _chars[0]
    _scene_objs = _pb.get("objects") or []

    # Divide pages into 3-act structure
    setup_end = max(2, int(total_pages * 0.25))
    problem_end = max(setup_end + 1, int(total_pages * 0.5))
    attempts_end = max(problem_end + 1, int(total_pages * 0.8))
    resolution_end = total_pages - 1
    closing = total_pages

    prop_list = [p.strip() for p in props.split("/") if p.strip()] if props else []
    if not prop_list:
        prop_list = _scene_objs or ["the special object"]
    first_prop = prop_list[0] if prop_list else "the special object"
    last_prop = prop_list[-1] if prop_list else "the special object"

    plan_lines = []
    for p in range(1, total_pages + 1):
        if p <= setup_end:
            act = "SETUP"
            note = "Establish world, introduce character, show normal life"
            if p == 1:
                note = "Opening image: " + scene + ". " + _hero + " and " + first_prop + " introduced."
        elif p <= problem_end:
            act = "PROBLEM"
            note = ("The problem arrives: " + _hero + " needs " + first_prop
                    + " but something blocks the way. Subtext: " + (subtext or mood))
        elif p <= attempts_end:
            act = "ATTEMPTS"
            note = "Try to solve, fail, escalate. " + first_prop + " plays a role."
        elif p <= resolution_end:
            act = "RESOLUTION"
            act_note = ("The solution, the change: " + _hero + " understands what "
                        + last_prop + " truly means. " + (intent_feel or "Growth"))
            note = act_note
        else:
            act = "CLOSING"
            note = "Circular return: echo page 1 image with change visible."

        plan_lines.append("  Page " + str(p) + " [" + act + "]: " + note)

    return "\n".join(plan_lines)


# ============================================================
# PictureBookPro ComfyUI Node
# ============================================================

class PictureBookPro:
    """
    故事绘本专家节点 (环节 40)
    基于年龄/画风/页数, 生成专业绘本导演级 H3 Prompt.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "故事绘本"}),
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
                # --- 绘本专属参数 ---
                "目标年龄": (AGE_GROUPS, {"default": "auto"}),
                "绘本风格": (BOOK_STYLES, {"default": "auto"}),
                "页数": ("INT", {"default": 12, "min": 4, "max": 32, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("picturebookpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_book"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_book(self, **kwargs):
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
        genre = _str(kwargs.get("类型"), "故事绘本")
        scene = _str(kwargs.get("场景描述"), "")
        director = _str(kwargs.get("导演风格"), "是枝裕和")
        mood = _str(kwargs.get("情绪基调"), "")
        subtext = _str(kwargs.get("潜文本_情感"), "")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "")
        props = _str(kwargs.get("关键道具"), "")
        ref_films = _str(kwargs.get("关键参考片"), "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        total_pages = int(kwargs.get("页数", 12))

        # 绘本专属: 年龄 + 画风
        age_raw = _str(kwargs.get("目标年龄"), "auto")
        style_raw = _str(kwargs.get("绘本风格"), "auto")

        if age_raw == "auto":
            age_key = _infer_age_from_scene(scene, mood)
        else:
            age_key = _get_age_key(age_raw)

        if style_raw == "auto":
            style_key = _infer_style_from_scene(scene, mood)
        else:
            style_key = _get_style_key(style_raw)

        age_data = AGE_CONTENT_DESIGN.get(age_key, AGE_CONTENT_DESIGN["3-6"])
        art_style = ART_STYLE_SYSTEM.get(style_key, ART_STYLE_SYSTEM["watercolor"])

        # --- 知识库增强 (graceful fallback) ---
        kb_children_info = ""
        if _HAS_CHILDREN_STYLES:
            age_kb_key_map = {"0-3": "age_0_3", "3-6": "age_3_6", "6-9": "age_6_9", "9-12": "age_9_12"}
            kb_age_key = age_kb_key_map.get(age_key, "age_3_6")
            kb_data = get_children_style(kb_age_key)
            if kb_data:
                kb_children_info = (
                    "  KB 年龄段: " + kb_data.get("cn", "") + "\n"
                    "  KB 原理: " + kb_data.get("rationale", "") + "\n"
                    "  KB 失败模式: " + str(kb_data.get("failure_modes", [])) + "\n"
                )

        kb_style_info = ""
        if _HAS_BOOK_STYLES:
            kb_style_key_map = {"watercolor": "watercolor", "paper_cut": "paper_cut",
                                "oil_painting": "oil_painting", "digital": "digital_cute",
                                "crayon": "pastel", "mixed_media": "watercolor"}
            kb_sk = kb_style_key_map.get(style_key, "watercolor")
            kb_style_data = get_picture_book_style(kb_sk)
            if kb_style_data:
                kb_style_info = (
                    "  KB 画风: " + kb_style_data.get("cn", "") + "\n"
                    "  KB 原理: " + kb_style_data.get("rationale", "") + "\n"
                    "  KB 失败模式: " + str(kb_style_data.get("failure_modes", [])) + "\n"
                )

        # --- 导演档案 ---
        director_profile_str = ""
        if _HAS_DIRECTOR_DATA:
            profile = get_director(director)
            director_profile_str = (
                "  镜头: " + str(profile.get("镜头", "")) + "\n"
                "  光: " + str(profile.get("光", "")) + "\n"
                "  色彩: " + str(profile.get("色彩", "")) + "\n"
                "  情绪: " + str(profile.get("情绪", "")) + "\n"
                "  代表作: " + str(profile.get("代表作", "")) + "\n"
                "  物件: " + str(profile.get("物件", "")) + "\n"
            )

        # --- 导演运镜 ---
        director_motion_map = {
            "塔可夫斯基": "Static Shot 长镜 + 圣像式静帧 (绘本: 冥想式全幅)",
            "王家卫": "Push In 慢推 + 色块碎片 (绘本: 城市孤独水彩)",
            "是枝裕和": "Static Shot 静观 + 日常诗意 (绘本: 家庭温度)",
            "侯孝贤": "Static Shot 远景 + 留白 (绘本: 自然与沉默)",
            "宫崎骏": "Push In + 飞行 + 水彩 (绘本: 自然飞行器)",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + 柔和缓推")

        # === H3 Shot 生成: 绘本页面序列 ===
        # V13.3: 空 props 兜底 + 从场景解析角色/冲突 (不再把 mood 当冲突)
        _prop_tokens = [p.strip() for p in props.split(" / ") if p.strip()] if props else []
        if not _prop_tokens:
            _prop_tokens = [p.strip() for p in props.split("/") if p.strip()] if props else []
        try:
            from aggregator.scene_engine import parse_scene as _ps_h
            _ph = _ps_h(scene) if scene else {}
        except Exception:
            _ph = {}
        if not _prop_tokens:
            _prop_tokens = _ph.get("objects") or ["the special object"]
        _hero_h = (_ph.get("characters") or ["the hero"])[0]
        first_prop = _prop_tokens[0] if _prop_tokens else "the special object"
        last_prop = _prop_tokens[-1] if _prop_tokens else "the special object"

        style_desc = art_style["cn"] + " style, " + art_style["mood"] + ". " + art_style["technique"]

        shot_1 = (
            "A " + art_style["cn"] + " illustration in " + style_desc + ". "
            + "The scene: " + scene + ". "
            + "Age target: " + age_data["cn"] + " (head-to-body ratio " + age_data["head_body_ratio"] + "). "
            + "Expression: " + age_data["expression_clarity"] + ". "
            + "Text density: " + age_data["text"] + ". "
            + "Palette: " + art_style["palette"] + ". "
            + "The " + first_prop + " is the visual anchor, placed at eye-level for the child reader."
        )

        shots = []
        # Page 2-3: Setup
        shots.append(
            "[Page 2-3 SETUP] " + age_data["cn"] + " content rules: "
            + age_data["visual"] + ". "
            + "Complexity: " + age_data["complexity"] + ". "
            + "The character is introduced with " + age_data["head_body_ratio"] + " head-body ratio. "
            + "Silhouette test: character must be recognizable in solid black shadow. "
            + "Costume marker established: one accessory/color that never changes. "
            + "The " + first_prop + " appears as a recurring visual motif."
        )
        # Page 4-6: Problem
        shots.append(
            "[Page 4-6 PROBLEM] The conflict: " + _hero_h + " wants " + first_prop
            + " but something stands in the way. "
            + "Subtext: " + (subtext or mood) + ". "
            + "Art style intensifies: " + art_style.get("best_for", "") + ". "
            + "Page turn surprise: right page reveals the problem hidden by left page setup. "
            + "Text-image relationship: " + ("embedded" if age_key in ("0-3", "3-6") else "separated") + ". "
            + "Color palette shifts toward tension (cooler, less saturated)."
        )
        # Page 7-9: Attempts
        shots.append(
            "[Page 7-9 ATTEMPTS] Repetition with variation pattern: "
            + "each spread repeats the attempt structure but changes ONE element. "
            + "Visual continuity: character position consistent, background evolves. "
            + "Pacing: " + age_data["pacing"] + ". "
            + "The " + last_prop + " gains narrative significance through repetition."
        )
        # Page 10-11: Resolution
        shots.append(
            "[Page 10-11 RESOLUTION] Climax spread (double-page, full bleed). "
            + "Director intent: " + intent_feel + ". "
            + "Emotions: " + age_data["emotions"] + ". "
            + "Art style at maximum expression: " + art_style["technique"] + ". "
            + "All visual motifs (" + props + ") converge in this spread."
        )
        # Page 12: Closing
        shots.append(
            "[Page 12 CLOSING] Circular ending: echo page 1 composition with visible change. "
            + "Same scene (" + scene + ") but character has grown/changed. "
            + "The " + first_prop + " is in the same position but means something different now. "
            + "Final image holds for emotional weight. Vignette with generous white space."
        )

        # Soundscape (for animated picture book / video)
        soundscape = (
            "Gentle " + art_style["cn"] + "-appropriate ambient: "
            + "page-turn sound effect (soft paper), "
            + "environment (" + scene.split(",")[0] if "," in scene else scene + "), "
            + "foley for " + first_prop + " (cloth, paper, wood as appropriate). "
            + "Voice: warm narrator, " + ("very slow, simple words" if age_key == "0-3"
                                          else "moderate pace, clear diction" if age_key in ("3-6", "6-9")
                                          else "literary rhythm, nuanced") + "."
        )
        music = (
            "Gentle, " + art_style["mood"] + " music. "
            + "Instrumentation: "
            + ("music box, gentle chimes, lullaby" if age_key == "0-3"
               else "ukulele, xylophone, light percussion" if age_key == "3-6"
               else "piano, strings, light woodwind" if age_key == "6-9"
               else "chamber music, solo piano, subtle orchestral") + ". "
            + "Tempo follows page rhythm, not beat-driven."
        )

        h3_prompt = build_h3_three_fields(
            style=style_desc, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 30 秒场景单元
        timeline_30s = build_30s_timeline(
            scene_type="绘本", scene_desc=scene,
            speaker_id="Narrator", speaker_voice="warm, gentle storyteller voice",
            dialogue="(narrator reads text)", n_lines=1,
            director_intent=intent_feel, language="Chinese"
        )

        # 页面计划
        page_plan = _build_page_plan(total_pages, age_key, scene, props, mood, subtext, intent_feel)

        # 5 要素注入
        data_summary = (
            "35 导演 8 维档案 + 绘本画风 7 维知识库 + 儿童内容 4 档年龄适配 + "
            + "6 种画风决策系统 + 4 种叙事结构 + 角色设计规则 + "
            + "页面布局节奏系统 + 191 反 AI 词表"
        )
        context_brief = (
            "年龄=" + age_data["cn"] + ", 画风=" + art_style["cn"]
            + ", 页数=" + str(total_pages) + ", 导演=" + director
            + ", 场景=" + scene[:50] + "..."
        )
        skill_harness = (
            "年龄 5 档内容适配 + 画风 6 型决策 + 页面节奏系统 + "
            + "角色设计 4 维 + 叙事结构 4 型 + 翻页悬念 + 视觉韵律"
        )
        experience_str = (
            "《好饿的毛毛虫》重复变奏 + Shaun Tan 混合媒材 + "
            + "Beatrix Potter 水彩 + 几米城市孤独 + 宫崎骏水彩飞行器 + "
            + "Eric Carle 拼贴 + Mo Willems 数字极简"
        )
        ai_deep = (
            "年龄=" + age_key + " -> 头身比=" + age_data["head_body_ratio"]
            + " + 画风 [" + art_style["cn"] + "] -> " + art_style["technique"]
            + " + " + str(total_pages) + " 页三幕结构 + 反 AI 词表 + 10 铁律"
        )
        elements_block = inject_5_elements(data_summary, context_brief, skill_harness, experience_str, ai_deep)

        # 导演意图 5 维 (绘本语境)
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "图与文的共舞 - 图说文没说的, 文说图没画的",
            "主题": mood,
            "留白": "翻页之前的悬念, 翻页之后的惊喜 - " + first_prop + " 是贯穿全书的视觉锚点",
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
                    "【灵魂核心 - 故事绘本驱动 (Phase 17.6)】\n"
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
        main_output += "【PictureBookPro】故事绘本专家节点 - 绘本视觉化引擎\n"
        main_output += "=" * 60 + "\n\n"

        # 绘本专属: 核心参数总览
        main_output += "【绘本核心参数】\n"
        main_output += "  目标年龄: " + age_data["cn"] + "\n"
        main_output += "  绘本风格: " + art_style["cn"] + " (" + style_key + ")\n"
        main_output += "  页数: " + str(total_pages) + " 页\n"
        main_output += "  头身比: " + age_data["head_body_ratio"] + "\n"
        main_output += "  表情系统: " + age_data["expression_clarity"] + "\n"
        main_output += "  文字密度: " + age_data["text"] + "\n"
        main_output += "  情感范围: " + age_data["emotions"] + "\n"
        main_output += "  参考作品: " + age_data["reference"] + "\n\n"

        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + " - " + director_motion_pref + "\n"
        if director_profile_str:
            main_output += "【导演档案 (35 导演 8 维)】\n" + director_profile_str + "\n"

        # 年龄适配详情
        main_output += "=" * 60 + "\n"
        main_output += "年龄适配内容设计: " + age_data["cn"] + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  视觉: " + age_data["visual"] + "\n"
        main_output += "  文字: " + age_data["text"] + "\n"
        main_output += "  焦点: " + age_data["focus"] + "\n"
        main_output += "  复杂度: " + age_data["complexity"] + "\n"
        main_output += "  节奏: " + age_data["pacing"] + "\n"
        main_output += "  禁忌: " + age_data["taboo"] + "\n"
        if kb_children_info:
            main_output += "\n  [知识库增强]\n" + kb_children_info
        main_output += "\n"

        # 画风决策详情
        main_output += "=" * 60 + "\n"
        main_output += "画风决策: " + art_style["cn"] + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  情绪: " + art_style["mood"] + "\n"
        main_output += "  技法: " + art_style["technique"] + "\n"
        main_output += "  色彩: " + art_style["palette"] + "\n"
        main_output += "  质感: " + art_style["texture"] + "\n"
        main_output += "  适合: " + art_style["best_for"] + "\n"
        main_output += "  避免: " + art_style["avoid"] + "\n"
        main_output += "  执行要点: " + art_style["execution_notes"] + "\n"
        main_output += "  大师参考: " + art_style["masters"] + "\n"
        if kb_style_info:
            main_output += "\n  [知识库增强]\n" + kb_style_info
        main_output += "\n"

        # 页面计划
        main_output += "=" * 60 + "\n"
        main_output += str(total_pages) + " 页叙事计划 (三幕式)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += page_plan + "\n\n"

        # 角色设计
        main_output += "=" * 60 + "\n"
        main_output += "角色设计规则 (年龄=" + age_data["cn"] + ")\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "  头身比: " + CHARACTER_DESIGN_RULES["head_body_ratio"].get(age_key + "_target",
                       CHARACTER_DESIGN_RULES["head_body_ratio"].get("3-6_target", "")) + "\n"
        main_output += "  表情系统: " + CHARACTER_DESIGN_RULES["expression_system"].get(age_key, "") + "\n"
        main_output += "  轮廓测试: " + CHARACTER_DESIGN_RULES["silhouette_test"]["rule"] + "\n"
        main_output += "  服饰标记: " + CHARACTER_DESIGN_RULES["costume_markers"]["rule"] + "\n\n"

        # 页面布局
        main_output += "=" * 60 + "\n"
        main_output += "页面布局与节奏\n"
        main_output += "=" * 60 + "\n\n"
        for rule in PAGE_LAYOUT_PACING["spread_rhythm"]["rules"]:
            main_output += "  - " + rule + "\n"
        main_output += "\n  翻页悬念技巧:\n"
        for tech in PAGE_LAYOUT_PACING["page_turn_surprise"]["techniques"]:
            main_output += "    - " + tech + "\n"
        main_output += "\n"

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
        main_output += "导演意图 5 维 (绘本语境)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += intent_block + "\n\n"

        # 导演控制 + H3 规则
        main_output += "=" * 60 + "\n"
        main_output += director_control + "\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "=" * 60 + "\n"
        main_output += h3_rules + "\n"
        main_output += "=" * 60 + "\n\n"

        # Seedance
        main_output += "=" * 60 + "\n"
        main_output += "Seedance 2.5 核心升级 (卡兹克)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += sft_quotes + "\n\n"

        # 5 要素
        main_output += "=" * 60 + "\n"
        main_output += elements_block + "\n"
        main_output += "=" * 60 + "\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # === 第二个输出: 经验矩阵 (绘本专业化) ===
        experience = "【绘本画风决策系统 (6 型)】\n\n"
        for sk, sv in ART_STYLE_SYSTEM.items():
            experience += "  " + sv["cn"] + " (" + sk + ")\n"
            experience += "    情绪: " + sv["mood"] + "\n"
            experience += "    技法: " + sv["technique"] + "\n"
            experience += "    适合: " + sv["best_for"] + "\n"
            experience += "    大师: " + sv["masters"] + "\n\n"

        experience += "【绘本叙事结构 (4 型)】\n\n"
        for nk, nv in NARRATIVE_STRUCTURES_BOOK.items():
            experience += "  " + nv["cn"] + " (" + nk + ")\n"
            experience += "    " + nv["description"] + "\n"
            experience += "    参考: " + nv["reference"] + "\n\n"

        experience += "【年龄适配角色设计】\n\n"
        for age_k, age_v in AGE_CONTENT_DESIGN.items():
            experience += "  " + age_v["cn"] + ": 头身比 " + age_v["head_body_ratio"] + ", " + age_v["expression_clarity"] + "\n"

        experience += "\n【20 导演集群】\n"
        for d in DIRECTORS_20:
            experience += "  - " + d + "\n"
        experience += "\n【9 大影视类型 + 5 要素处理】\n"
        experience += inject_genre_9_types() + "\n"
        experience += "【11 维导演控制能力 (人类顶级导演)】\n"
        experience += inject_director_control_11() + "\n"
        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"

        # === 第三个输出: AI 深度处理 (绘本专业化) ===
        ai_deep_output = "【绘本年龄 -> 视觉设计映射原理】\n\n"
        ai_deep_output += "核心原则: 年龄决定一切 - 头身比/表情/文字密度/情感复杂度\n"
        ai_deep_output += "  当前年龄: " + age_data["cn"] + "\n"
        ai_deep_output += "  头身比: " + age_data["head_body_ratio"] + "\n"
        ai_deep_output += "  文字: " + age_data["text"] + "\n"
        ai_deep_output += "  复杂度: " + age_data["complexity"] + "\n\n"

        ai_deep_output += "【画风决策原理】\n"
        ai_deep_output += "  当前画风: " + art_style["cn"] + "\n"
        ai_deep_output += "  技法: " + art_style["technique"] + "\n"
        ai_deep_output += "  避免: " + art_style["avoid"] + "\n"
        ai_deep_output += "  执行: " + art_style["execution_notes"] + "\n\n"

        ai_deep_output += "【页面节奏系统】\n"
        ai_deep_output += "  总页数: " + str(total_pages) + "\n"
        ai_deep_output += "  节奏: tension -> release -> build -> climax -> resolution\n"
        ai_deep_output += "  翻页悬念: " + PAGE_LAYOUT_PACING["page_turn_surprise"]["description"] + "\n\n"

        ai_deep_output += "【角色设计 4 维】\n"
        ai_deep_output += "  1. 头身比: " + age_data["head_body_ratio"] + "\n"
        ai_deep_output += "  2. 表情: " + age_data["expression_clarity"] + "\n"
        ai_deep_output += "  3. 轮廓: " + CHARACTER_DESIGN_RULES["silhouette_test"]["rule"] + "\n"
        ai_deep_output += "  4. 标记: " + CHARACTER_DESIGN_RULES["costume_markers"]["rule"] + "\n\n"

        ai_deep_output += "【191 反 AI 词表 + 4 轮迭代】\n"
        ai_deep_output += "瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词\n\n"
        ai_deep_output += "【沉默 5 规则 + 4 步公式 + 30 秒场景单元】\n"
        ai_deep_output += inject_silence_mastery_5("绘本", 1) + "\n\n"
        ai_deep_output += "【9 维光照控制 (CIE LAB + 摄影本体)】\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "PictureBookPro": PictureBookPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "PictureBookPro": "故事绘本 (环节 40) — L5 重写",
# }
