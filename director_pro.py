# ============================================================
# DirectorPromptPro V2.0 — 世界级导演批次输出引擎
# ============================================================
# 核心升级:
#   1. 故事前文系统: 每个分镜输出前以前面故事大纲开头
#   2. 知识库驱动: 从10个专业模块实时提取导演级指导
#   3. 镜头间连续性: 角色/场景/情绪/伏笔全程追踪
# ============================================================
import os
import sys

_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

from story_sense_data import STORY_SENSE_LIBRARY
from engine_story_arc import StoryArc, ShotConstraints, PromptSegmenter, CinematographyDirector
from pln_llm import call_ai
from pln_random import random_topic, random_character, random_env
from director_engine import DirectorPromptBuilder, KnowledgeDirector, StoryContextBuilder

from modes_storyboard import _get_mode_name, _get_mode_style, _get_layout_desc
from pln_utils import generate_negative_prompt
from format_templates import get_format_templates


def _parse_shot_data(raw_text):
    """从LLM输出中提取结构化镜头数据用于约束跟踪"""
    data = {}
    for line in raw_text.split('\n'):
        line = line.strip()
        if line.startswith('景别：') or line.startswith('景别:'):
            data['shot_type'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('分镜场景：') or line.startswith('分镜场景:'):
            data['scene'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('角色特征：') or line.startswith('角色特征:'):
            data['characters'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('运镜：') or line.startswith('运镜:'):
            data['camera'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('转场：') or line.startswith('转场:'):
            data['transition'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('时长：') or line.startswith('时长:'):
            try:
                dur_str = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                dur_str = dur_str.replace('秒', '').strip()
                if '-' in dur_str:
                    parts = dur_str.split('-')
                    data['duration'] = (float(parts[0]) + float(parts[1])) / 2
                else:
                    data['duration'] = float(dur_str)
            except (ValueError, IndexError):
                pass
    return data


# ============================================================
# 故事板模式 — 世界级导演引擎驱动
# ============================================================
def process_storyboard_batched(mode, topic, character_desc, env_desc,
                                shot_count, style, color_tone, preferred_shot, camera_style,
                                api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                pick_story_sense_fn,
                                director_keys=None, narrative_structure="",
                                short_drama_type="", audience_archetype="", output_focus="分镜"):
    if not api_url or shot_count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    is_vertical = "竖屏" in (camera_style or "")
    director = DirectorPromptBuilder(
        mode, style, color_tone, topic, character_desc, env_desc,
        shot_count, camera_style=camera_style, is_vertical=is_vertical,
        director_keys=director_keys, narrative_structure=narrative_structure,
        short_drama_type=short_drama_type, audience_archetype=audience_archetype,
        output_focus=output_focus,
    )
    header = director.build_header()

    segments = []
    constraints_tracker = ShotConstraints()

    for shot_idx in range(shot_count):
        beat_info = None
        if story_arc:
            beat_info = story_arc.get_beat_for_shot(shot_idx, shot_count)

        constraint_text = constraints_tracker.get_constraints_text()

        sys_p = director.build_system_prompt(shot_idx, beat_info, constraint_text)

        user_prompt = (
            f"主题: {topic}\n"
            f"角色描述: {character_desc}\n"
            f"环境背景: {env_desc}\n"
            f"当前第{shot_idx+1}/{shot_count}镜。风格: {style}\n"
            f"请输出第{shot_idx+1}个镜头的内容。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        shot_output = (
            f"{header}\n"
            f"【镜头{shot_idx+1}/{shot_count}】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【镜头{shot_idx+1}/{shot_count}】\n（AI调用失败: {err}）\n"
        )

        if ai_result:
            shot_data = _parse_shot_data(ai_result)
            constraints_tracker.record_shot(shot_data)
            director.record_shot_result(shot_idx, ai_result, beat_info)

        segments.append(shot_output)

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 短剧模式 — 竖屏9:16 + 爆款模式驱动
# ============================================================
def process_short_drama_batched(topic, character_desc, env_desc, shot_count,
                                 style, rhythm, camera_style, color_tone,
                                 api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                 pick_story_sense_fn,
                                 director_keys=None, narrative_structure="",
                                 short_drama_type="", audience_archetype="", output_focus="分镜"):
    if not api_url or shot_count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic("短剧模式")
    if not character_desc:
        character_desc = random_character("短剧模式", topic)
    if not env_desc:
        env_desc = random_env("短剧模式", topic)

    director = DirectorPromptBuilder(
        "短剧模式", style, color_tone, topic, character_desc, env_desc,
        shot_count, camera_style=camera_style or "竖屏流畅运动", is_vertical=True,
        director_keys=director_keys, narrative_structure=narrative_structure,
        short_drama_type=short_drama_type, audience_archetype=audience_archetype,
        output_focus=output_focus,
    )
    header = director.build_header()

    segments = []
    constraints_tracker = ShotConstraints()

    for shot_idx in range(shot_count):
        beat_info = None
        if story_arc:
            beat_info = story_arc.get_beat_for_shot(shot_idx, shot_count)

        constraint_text = constraints_tracker.get_constraints_text()
        sys_p = director.build_system_prompt(shot_idx, beat_info, constraint_text)

        # 短剧节奏补充
        rhythm_note = ""
        if rhythm == "舒缓铺垫":
            rhythm_note = "节奏舒缓,注重氛围和情感铺垫。"
        elif rhythm == "紧凑推进":
            rhythm_note = "节奏紧凑,每10秒必须推进情节。"
        elif rhythm == "高能密集":
            rhythm_note = "高能密集节奏,每5秒一个信息点/反转。"

        user_prompt = (
            f"故事主题: {topic}\n"
            f"角色描述: {character_desc}\n"
            f"环境背景: {env_desc}\n"
            f"当前第{shot_idx+1}/{shot_count}镜。风格: {style}。{rhythm_note}\n"
            f"请输出第{shot_idx+1}个镜头(竖屏9:16)。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        shot_output = (
            f"{header}\n"
            f"【镜头{shot_idx+1}/{shot_count}】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【镜头{shot_idx+1}/{shot_count}】\n（AI调用失败: {err}）\n"
        )

        if ai_result:
            shot_data = _parse_shot_data(ai_result)
            constraints_tracker.record_shot(shot_data)
            director.record_shot_result(shot_idx, ai_result, beat_info)

        segments.append(shot_output)

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 绘本模式 — 逐页输出
# ============================================================
def process_picture_book_batched(topic, character_desc, env_desc, pages,
                                  style, color_tone, text_amount, age_group,
                                  api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                  pick_story_sense_fn):
    if not api_url or pages < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic("绘本模式")
    if not character_desc:
        character_desc = random_character("绘本模式", topic)
    if not env_desc:
        env_desc = random_env("绘本模式", topic)

    age_guide = {
        "0-3岁低幼": "适合0-3岁:每页画面简单主体突出,文字极短(5-15字),句式重复有节奏。",
        "3-6岁幼儿": "适合3-6岁:画面丰富有清晰焦点,文字每页20-40字,故事有简单情节。",
        "6-9岁学龄": "适合6-9岁:画面细节丰富,文字每页30-60字,有完整起承转合。",
        "9-12岁少年": "适合9-12岁:更写实或更具艺术风格,每页50-100字,可有多条线索。",
    }
    age_text = age_guide.get(age_group, age_guide["3-6岁幼儿"])

    context_builder = StoryContextBuilder(topic, character_desc, env_desc, pages)

    header = (
        f"绘本总纲\n"
        f"整体视觉风格: {style}，色调{color_tone}，适合{age_group}。\n"
        f"角色物品设定:\n{(character_desc or '待定角色').rstrip()}\n"
        f"场景设定:\n{env_desc or '待定场景'}\n"
        f"叙事设定: 共{pages}页，文字量{text_amount}。\n"
    )

    segments = []
    for page in range(pages):
        story_context = context_builder.build_context_prefix(page)

        beat_info = None
        cinema_block = ""
        if story_arc:
            beat_info = story_arc.get_beat_for_shot(page, pages)
            cinema = beat_info.get('cinematography', {})
            dur = cinema.get('duration_range', (5, 8))
            cinema_block = (
                f"【绘本视觉指导】\n"
                f"  推荐阅读时长: {dur[0]}-{dur[1]}秒\n"
                f"  情绪节拍: {beat_info['beat_name']}(情绪值{beat_info['emotion_value']:.2f})\n"
                f"  叙事功能: {beat_info['narrative_func']}\n"
            )

        sys_p = (
            f"{story_context}\n\n"
            f"你是世界顶级的儿童绘本作家兼插画师。当前: 第{page+1}/{pages}页\n\n"
            f"{cinema_block}\n"
            f"输出格式: 以'【第N页】'开头\n"
            f"1. 时间·空间锚定\n2. 画面描述(用孩子的眼睛看世界,2-4句)\n"
            f"3. 文案(绘本正文,适合朗读)\n4. 视觉连续性提示\n5. 构图景别\n\n"
            f"年龄适配: {age_text}\n"
            f"请直接输出第{page+1}页。不要包含符号标记。\n"
        )
        user_prompt = (
            f"故事主题: {topic}\n角色: {character_desc}\n环境: {env_desc}\n"
            f"第{page+1}/{pages}页。风格: {style}，色调: {color_tone}\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        page_output = (
            f"{header}\n【第{page+1}/{pages}页】\n{ai_result}\n"
            if ai_result else f"{header}\n【第{page+1}/{pages}页】\n（AI调用失败）\n"
        )
        segments.append(page_output)

        if ai_result:
            summary = ai_result.split('\n')[0][:80] if ai_result else ""
            context_builder.record_shot(
                page, summary,
                emotion_value=beat_info.get("emotion_value", 0.5) if beat_info else 0.5,
            )

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 儿童内容模式批处理
# ============================================================
def process_child_batched(mode, topic, character_desc, env_desc, count,
                           age_group, art_style,
                           api_url, api_key, model_name, temperature, max_tokens, ref_images,
                           pick_story_sense_fn):
    if not api_url or count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    style_map = {
        "水彩插画": "水彩晕染,色彩柔和通透",
        "卡通动画": "明亮卡通,粗轮廓线,表情夸张可爱",
        "彩铅手绘": "彩铅手绘质感",
        "黏土定格": "黏土定格动画,立体感强",
        "扁平矢量": "扁平矢量,简洁几何",
    }
    style_text = style_map.get(art_style, "卡通动画")

    context_builder = StoryContextBuilder(topic, character_desc, env_desc, count)

    header = (
        f"{mode}总纲\n"
        f"视觉风格: {art_style}，适合{age_group}。\n"
        f"角色: {(character_desc or '待定').rstrip()}\n"
        f"场景: {env_desc or '待定'}\n"
    )

    segments = []
    for idx in range(count):
        unit = "页" if "绘本" in mode else "片段"
        story_context = context_builder.build_context_prefix(idx)

        beat_info = story_arc.get_beat_for_shot(idx, count) if story_arc else None

        sys_p = (
            f"{story_context}\n\n"
            f"你是顶级儿童动画编剧。当前: 第{idx+1}/{count}个{unit}\n"
            f"画面风格: {style_text}\n"
            f"年龄段: {age_group}\n"
            f"创作原则: 不说教,情绪正向,角色一致,变化必须可见\n"
            f"请直接输出第{idx+1}个{unit}。纯文字,无符号标记。\n"
        )
        user_prompt = (
            f"故事主题: {topic}\n角色: {character_desc}\n环境: {env_desc}\n"
            f"第{idx+1}/{count}个{unit}。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        unit_output = (
            f"{header}\n【{unit}{idx+1}/{count}】\n{ai_result}\n"
            if ai_result else f"{header}\n【{unit}{idx+1}/{count}】\n（AI调用失败）\n"
        )
        segments.append(unit_output)

        if ai_result:
            summary = ai_result.split('\n')[0][:60] if ai_result else ""
            context_builder.record_shot(
                idx, summary,
                emotion_value=beat_info.get("emotion_value", 0.5) if beat_info else 0.5,
            )

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 专业设计模式批处理
# ============================================================
def process_design_batched(mode, topic, character_desc, env_desc, count,
                            style, color_tone, product_material, product_color,
                            shoot_angle, lighting_scheme, bg_type,
                            api_url, api_key, model_name, temperature, max_tokens, ref_images,
                            pick_story_sense_fn):
    if not api_url or count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    try:
        from modes_design import (
            _build_ecommerce_prompt, _build_poster_prompt, _build_brand_prompt,
            _build_ppt_prompt, _build_logic_diagram_prompt, _build_three_view_prompt,
            _build_exploded_view_prompt, _build_pipeline_diagram_prompt,
        )
    except ImportError:
        return f"[提示] 设计模式「{mode}」需要安装 modes_design 模块。"

    builder_map = {
        "电商套图": _build_ecommerce_prompt,
        "海报设计": _build_poster_prompt,
        "品牌设计": _build_brand_prompt,
        "PPT设计": _build_ppt_prompt,
        "逻辑关系图设计": _build_logic_diagram_prompt,
        "三视图设计": _build_three_view_prompt,
        "爆炸拆解图设计": _build_exploded_view_prompt,
        "流水线图设计": _build_pipeline_diagram_prompt,
    }

    builder = builder_map.get(mode)
    if not builder:
        return ""

    sys_p = builder(topic, character_desc, env_desc, count, style, color_tone,
                    product_material, product_color, shoot_angle, lighting_scheme, bg_type, [])

    segments = []
    for idx in range(count):
        cinema_block = ""
        if story_arc:
            beat_info = story_arc.get_beat_for_shot(idx, count)
            cinema_block = (
                f"【视觉节奏】强度{beat_info['intensity']:.2f}, "
                f"节拍: {beat_info['beat_name']}\n"
            )

        user_prompt = (
            f"设计主题: {topic}\n"
            f"{'主体: ' + character_desc + chr(10) if character_desc else ''}"
            f"{'场景: ' + env_desc + chr(10) if env_desc else ''}"
            f"第{idx+1}/{count}张。{cinema_block}\n"
            f"只输出第{idx+1}张的设计内容。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        unit_output = (
            f"{mode}总纲\n设计主题: {topic}\n风格: {style} | 色彩: {color_tone}\n\n"
            f"【设计{idx+1}/{count}】\n{ai_result}\n"
            if ai_result else f"【设计{idx+1}/{count}】\n（AI调用失败）\n"
        )
        segments.append(unit_output)

    return PromptSegmenter.join_outputs(segments)
