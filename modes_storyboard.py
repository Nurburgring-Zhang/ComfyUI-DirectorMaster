"""
故事板模式模块

从原 __init__.py 提取的 _process_storyboard_mode 及相关辅助函数，
全部转为普通函数（去掉 self），pick_story_sense_fn 作为参数传入。
_process_storyboard_mode 接收独立的 _random_topic / _random_character / _random_env
函数和 call_ai_fn 作为参数。
"""

# [P2修复] 从共享模块导入格式模板，消除与 director_pro.py 的重复
from format_templates import get_format_templates


def _get_mode_name(mode):
    names = {
        "电影分镜": "电影分镜", "广告故事板": "广告故事板", "动画故事板": "动画故事板",
        "漫画分镜": "漫画分镜", "MV故事板": "MV故事板", "教程步骤": "教程步骤",
        "短视频分镜": "短视频分镜", "品牌故事板": "品牌故事板", "剧情分镜": "剧情分镜",
    }
    return names.get(mode, "故事板")


def _get_mode_style(mode):
    styles = {
        "电影分镜": "🎬 电影分镜风格：强调镜头语言，包含景别标注，描述光影氛围，标注镜头时长",
        "广告故事板": "📺 广告故事板风格：每个镜头突出产品卖点/品牌信息，包含视觉焦点，节奏明快",
        "动画故事板": "🎨 动画故事板风格：注意角色动作夸张表现，描述关键帧，适合2D/3D制作",
        "漫画分镜": "📖 漫画分镜风格：标注页面布局，描述对话框位置，注意阅读顺序，包含拟声词提示",
        "MV故事板": "🎵 MV故事板风格：标注对应歌词段落，描述画面节奏与音乐配合",
        "教程步骤": "📚 教程步骤风格：每步清晰序号和标题，描述具体操作，步骤逻辑连贯",
        "短视频分镜": "📱 短视频分镜风格：单镜头1-3秒，竖屏9:16，描述画面切换和转场",
        "品牌故事板": "🏢 品牌故事板风格：突出品牌VI元素，描述调性和情感氛围，标注LOGO位置",
        "剧情分镜": "🎭 剧情分镜风格：强调角色情感表达和表演，描述戏剧冲突和节奏",
    }
    return styles.get(mode, "标准故事板格式")


def _get_layout_desc(mode):
    layouts = {
        "电影分镜": "推荐16:9宽屏比例，注重纵深构图",
        "广告故事板": "每个镜头中心突出产品或品牌",
        "动画故事板": "注意角色表情和动作的夸张表达，16:9",
        "漫画分镜": "页面布局推荐3x3或2x4格",
        "MV故事板": "画面比例2.35:1电影宽银幕",
        "教程步骤": "画面比例4:3或1:1方形，标注编号",
        "短视频分镜": "画面比例9:16竖屏，垂直构图",
        "品牌故事板": "统一品牌色系，16:9比例",
        "剧情分镜": "推荐2.35:1宽银幕比例",
    }
    return layouts.get(mode, "标准16:9比例")


def _build_storyboard_system_prompt(mode, style, topic, character_desc, env_desc, ref_images, pick_story_sense_fn, story_arc=None):
    """构建故事板系统提示词"""
    mode_name = _get_mode_name(mode)
    mode_style = _get_mode_style(mode)
    layout_desc = _get_layout_desc(mode)

    ref_section = ""
    if ref_images:
        ref_section = (
            f"\n# 参考图信息\n"
            f"用户提供了 {len(ref_images)} 张参考图。这些图片的角色外貌、服装风格、场景环境、色彩氛围应作为本故事板的核心视觉参考。\n"
            f"在所有镜头中，角色外貌、服装样式、色彩基调需与参考图保持一致。在画面描述中参考参考图的构图、光影和氛围。\n"
        )

    env_section = ""
    if env_desc:
        env_section = f"环境背景：{env_desc}\n"

    # [P2修复] 使用共享格式模板
    format_templates = get_format_templates()
    format_section = format_templates.get(mode,
        "输出格式（标准故事板）\n每个镜头包含：景别+画面描述+运镜+转场+备注\n"
    )

    if story_arc is not None:
        # 使用故事弧引擎的结构化数据
        story_sense_text = story_arc.sense_text
        arc_data = story_arc.get_beat_for_shot(0, 1)  # 整体弧线参考
        emotion_range = f"{min(story_arc.emotion_curve):.1f}-{max(story_arc.emotion_curve):.1f}"
        beat_desc = " → ".join([b.name for b in story_arc.beats])
        emotion_desc = " → ".join([f"{b.narrative_func}({b.emotion_value:.1f})" for b in story_arc.beats])
        
        story_section = (
            f"{story_sense_text}\n"
            f"上述故事感总纲是本片的故事结构设计核心。\n\n"
            f"【故事弧结构化数据】\n"
            f"节拍序列：{beat_desc}\n"
            f"情绪曲线：{emotion_desc}\n"
            f"情绪范围：{emotion_range}\n"
            f"核心主题：{story_arc.core}\n\n"
            f"请严格按照上述情绪曲线设计每个镜头的视觉情绪。\n"
            f"开场阶段：情绪偏低（0.1-0.3），用远景/全景建立情境\n"
            f"前段发展阶段：情绪回升（0.3-0.6），节奏加快\n"
            f"中段转折阶段：情绪触底（0.0-0.2），节奏放慢，氛围压抑\n"
            f"高潮阶段：情绪冲顶（0.6-1.0），节奏最快，视觉冲击最强\n"
            f"结尾收束阶段：情绪回落（0.4-0.6），节奏放慢，给余韵\n\n"
        )
    else:
        story_sense = pick_story_sense_fn()
        story_section = (
            f"{story_sense}\n"
            f"上述故事感总纲是本片的故事结构设计核心。你必须用该总纲的情感曲线来设计整体情节的起伏——开场建立好奇，前段有小挫折，中段有真正的困境和最低点，之后出现转折，高潮解决问题，结尾温暖闭环。不要在每个分镜硬塞表情，而是让故事本身的走向有波折、有悬念、有反转。想象观众看到每个转折点时的反应：好奇→担心→心疼→松一口气→感动。\n\n"
        )

    return (
        f"{story_section}"
        f"角色设定\n"
        f"你是一位世界顶级的{mode_name}导演兼分镜师，拥有20年好莱坞/影视行业经验。"
        f"你精通镜头语言、视觉叙事和节奏控制。"
        f"现在请你根据用户提供的主题、角色描述和镜头数量，创作一个完整的{style}风格{mode_name}故事板。\n"
        f"分镜具体内容\n\n"
        f"画面铁律（十二条红线）\n"
        f"1. 禁止抽象词：禁止「悲伤」「紧张」等情绪词，只用可见的描述来传递情绪。\n"
        f"2. 饱满叙事：每格3-6句话，充分描写场景氛围和角色动态，让画面生动丰满。\n"
        f"3. 镜头连续性：相邻镜头之间的角色位置、光线、道具必须一致。\n"
        f"4. 禁止参数：不能写焦距mm、色温K、分辨率dpi等数值参数。\n"
        f"5. 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
        f"6. 叙事功能仅在需要说明镜头作用时才输出，不是每个镜头都必须有。\n"
        f"7. 时空锚定：每页/每格开头固定用「时间·空间」前缀（如「清晨·森林小屋厨房」「傍晚·湖边小码头」）。当时间或空间发生变化时，在先导句中明确标注「时间推进到…」或「场景切换到…」。\n"
        f"8. 180度不越轴：相邻镜头保持角色视线和站位方向一致（左侧机位/右侧机位锁定），禁止突然镜像翻转。\n"
        f"9. 单格凝固动作：每格/每页只描述一个凝固的瞬间动作，禁止连续动作（如「跑向…然后跳起来」会导致画面鬼影）。\n"
        f"10. 场景切换时在首镜内增加场景描述和角色特征变化描述（换装/变脏等可见变化，无变化不写）。\n"
        f"11. 风格统一：所有镜头中角色外貌、服装、色彩基调必须保持严格一致（除非场景转换有明确交代）。每格开头重复主风格词。\n"
        f"12. 对话框绑定角色：多角色场景下，每个对话框必须明确指向该角色（如「指向[角色名]的对话框」「[角色名]头顶的气泡对话框」），禁止模糊的「有对话框」。旁白不加对话框。\n\n"
        f"{format_section}\n"
        f"# {mode_name}风格参考\n"
        f"{layout_desc}\n"
        f"{mode_style}\n"
        f"{ref_section}"
        f"{env_section}"
        f"请直接输出故事板内容，不要额外解释。\n"
        f"重要：输出中不要包含任何** - 等符号标记，不要用星号或横线装饰文字标题。直接输出纯文字。"
    )


def _build_storyboard_user_prompt(mode, topic, character_desc, shot_count, style,
                                   color_tone, preferred_shot, camera_style, env_desc):
    """构建故事板用户提示词"""
    parts = []
    if topic:
        parts.append(f"【主题】\n{topic}")
    if character_desc:
        parts.append(f"【角色描述】\n{character_desc}")
    if env_desc:
        parts.append(f"【环境背景】\n{env_desc}")
    parts.append(f"【镜头数量】\n{shot_count}个镜头")
    parts.append(f"【风格】\n{style}")

    tone_map = {
        "暖色调": "整体色调采用暖色调风格，以橙红、金黄、琥珀色为主",
        "冷色调": "整体色调采用冷色调风格，以蓝灰、青蓝、冷白为主",
        "高对比": "整体采用高对比风格，明暗反差强烈，光影分明",
        "低饱和": "整体采用低饱和风格，色彩淡雅克制，氛围沉静",
        "复古": "整体采用复古色调风格，暖黄+褪色感，仿胶片质感",
        "赛博朋克": "整体采用赛博朋克风格，霓虹紫蓝+暗黑对比",
        "日系清新": "整体采用日系清新风格，高明度低饱和，干净通透",
        "黑白": "整体采用黑白风格，以灰度层次表现光影",
    }
    if color_tone and color_tone != "自动":
        desc = tone_map.get(color_tone, f"整体色调采用{color_tone}风格")
        parts.append(f"【色彩基调要求】\n{desc}。请在所有镜头的画面描述中统一体现。")
    if preferred_shot and preferred_shot != "自动-多种交替":
        parts.append(f"【景别要求】\n以{preferred_shot}为主，占比60%以上。")
    if camera_style and camera_style != "自动":
        cam_map = {
            "稳重固定镜头": "大部分镜头使用固定机位，强调画面构图和内部运动",
            "流畅运动": "大量使用轨道推拉、稳定器跟拍等流畅运动镜头",
            "手持纪实": "使用手持摄影风格，轻微晃动感，增强真实感",
            "炫酷动感": "使用环绕、快速推拉、航拍等动感镜头",
        }
        desc = cam_map.get(camera_style, camera_style)
        parts.append(f"【运镜风格要求】\n{desc}")

    return "\n\n".join(parts)


def _process_storyboard_mode(mode, topic, character_desc, env_desc,
                              shot_count, style, color_tone, preferred_shot, camera_style,
                              api_url, api_key, model_name, temperature, max_tokens, ref_images,
                              random_topic_fn, random_character_fn, random_env_fn, call_ai_fn,
                              pick_story_sense_fn, story_arc=None):
    """
    处理故事板模式 - 9种子模式

    参数：
        random_topic_fn(mode) -> str
        random_character_fn(mode, topic) -> str
        random_env_fn(mode, topic) -> str
        call_ai_fn(system_prompt, user_message) -> str  (注意：返回纯字符串，不含错误信息)
        pick_story_sense_fn() -> str
        story_arc: StoryArc对象（可选），提供结构化的故事弧数据
    """
    if not api_url:
        return ""

    # 用户没填信息时随机生成，确保所有信息相互匹配
    if not topic:
        topic = random_topic_fn(mode)
    if not character_desc:
        character_desc = random_character_fn(mode, topic)
    if not env_desc:
        env_desc = random_env_fn(mode, topic)

    sys_p = _build_storyboard_system_prompt(mode, style, topic, character_desc, env_desc, ref_images, pick_story_sense_fn, story_arc=story_arc)
    user_prompt = _build_storyboard_user_prompt(
        mode, topic, character_desc, shot_count, style,
        color_tone, preferred_shot, camera_style, env_desc
    )

    # 故事板专属总纲：五维设定展开
    storyboard_header = (
        f"{mode}总纲\n"
        f"整体视觉风格：\n"
        f"整体风格为{style}，色彩基调偏向{color_tone}。\n"
        f"角色物品设定：\n"
        f"{(character_desc or '待定角色').rstrip()}\n"
        f"道具或武器：\n"
        f"待补充。\n"
        f"场景设定：\n"
        f"{(env_desc or '待定场景').rstrip()}\n"
        f"氛围与画质标准：\n"
        f"{mode}风格叙事，景别以{preferred_shot}为主，运镜采用{camera_style}的方式。镜头语言注重叙事节奏和情绪表达，禁止使用抽象情绪词，用具体可见的画面传递情感。\n"
        f"声音设定：\n"
        f"根据场景氛围搭配环境音效和配乐。\n"
        f"核心叙事设定：\n"
        f"共{shot_count}个镜头，围绕主题展开，镜头之间要有因果推进关系，节奏上注意松紧交替。每个镜头用饱满的画面描写，让读者能清晰想象出画面。\n"
    )

    ai_result = call_ai_fn(sys_p, user_prompt)
    if not ai_result:
        return ""

    return f"{storyboard_header}\n\n{ai_result}"
