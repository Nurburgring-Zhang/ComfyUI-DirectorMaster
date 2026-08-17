"""
短剧模式模块 - 从 __init__.py 提取的短剧相关函数

原 __init__.py 中的三个方法被转换为普通函数：
  - _process_short_drama_mode  → process_short_drama
  - _build_short_drama_system_prompt  → build_short_drama_system_prompt
  - _build_short_drama_user_prompt  → build_short_drama_user_prompt
"""

import os

# ============================================================
# 短剧模式处理（入口）
# ============================================================

def process_short_drama(
    topic, character_desc, env_desc, shot_count,
    style, rhythm, camera_style, color_tone,
    api_url, api_key, model_name, temperature, max_tokens, ref_images,
    # 独立的外部依赖
    random_topic, random_character, random_env, call_ai_fn,
    # [P1修复] 补上 pick_story_sense_fn 参数，与绘本/故事板模式保持一致
    pick_story_sense_fn=None):
    """
    接收独立的 random_topic/random_character/random_env/call_ai_fn 作为参数。

    pick_story_sense_fn：可选的回调函数（无参，返回故事感总纲字符串）。
    返回值：拼接后的短剧总纲文本，失败返回空字符串。
    """
    if not api_url:
        return ""

    if not topic:
        topic = random_topic("短剧模式")
    if not character_desc:
        character_desc = random_character("短剧模式", topic)
    if not env_desc:
        env_desc = random_env("短剧模式", topic)

    drama_sys = build_short_drama_system_prompt(
        topic, character_desc, env_desc, shot_count,
        style, rhythm, camera_style, color_tone, ref_images,
        pick_story_sense_fn=pick_story_sense_fn,
    )
    drama_user = build_short_drama_user_prompt(
        topic, shot_count, style, rhythm, camera_style
    )

    ai_result = call_ai_fn(drama_sys, drama_user) or ""

    if ai_result:
        header = (
            f"短剧总纲\n"
            f"整体视觉风格：\n"
            f"风格为{style}，节奏{rhythm}，色彩调性偏向{color_tone}。竖屏9:16垂直构图。\n"
            f"角色物品设定：\n"
            f"{(character_desc or '待定角色').replace(chr(10), ' ').rstrip()}\n"
            f"道具或武器：\n"
            f"待补充。\n"
            f"场景设定：\n"
            f"{env_desc or '待定场景'}\n"
            f"氛围与画质标准：\n"
            f"竖屏短剧特有的叙事节奏。运镜以{camera_style}为主。开场快抓注意力，中间情绪反转，结尾留钩子。每个镜头要有画面感，禁止抽象词，用可见的动作和场景推进剧情。\n"
            f"声音设定：\n"
            f"根据剧情类型搭配配乐和音效。情绪转折点用音效强化冲击力。\n"
            f"核心叙事设定：\n"
            f"共{shot_count}个镜头。故事围绕{topic or '穿越时空的爱恋'}展开，遵循短剧创作规律——前几秒制造钩子，中间推进矛盾，结尾留下悬念或反转。\n"
        )
        return f"{header}\n\n{ai_result}"
    return ""


# ============================================================
# 短剧 System Prompt 构建
# ============================================================

def build_short_drama_system_prompt(
    topic, character_desc, env_desc, shot_count,
    style, rhythm, camera_style, color_tone, ref_images,
    pick_story_sense_fn=None):
    """
    构建短剧模式的 system prompt。

    pick_story_sense_fn：可选的回调函数（无参，返回故事感总纲字符串）。
    如果为 None 或可调用对象返回空，则跳过总纲插入。
    """
    rhythm_map = {
        "自动": "根据短剧类型自动匹配节奏",
        "舒缓铺垫": "节奏舒缓，前1/3建立角色关系，每个镜头3-5秒，以淡入淡出和叠化为主",
        "紧凑推进": "开场10秒内抛出冲突，每15-20秒一个小反转，镜头2-3秒/个",
        "高能密集": "开场3秒内用视觉冲击抓住注意力，每10-15秒一个爆点，镜头1-2秒/个",
    }
    ref_section = (
        f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，角色外貌、场景氛围、色彩调性需保持一致。\n"
        if ref_images else ""
    )
    env_section = f"环境背景设定：{env_desc}\n" if env_desc else ""

    camera_desc = ""
    if camera_style not in ("自动", "稳重固定镜头", "流畅运动", "手持纪实", "炫酷动感"):
        cam_map = {
            "竖屏固定机位为主": "以竖屏固定机位为主，9:16垂直构图",
            "竖屏流畅运动": "竖屏中使用流畅的运动镜头，纵向升降、前后推拉",
        }
        camera_desc = cam_map.get(camera_style, "")

    # 故事感总纲（通过参数注入的可调用对象）
    sense = ""
    if pick_story_sense_fn is not None:
        try:
            sense = pick_story_sense_fn()
        except Exception:
            sense = ""

    return (
        f"{sense}\n"
        f"上述故事感总纲是本短剧的故事结构设计核心。用总纲的情感曲线来设计整体的情节起伏——开场钩子，前段小冲突，中段真正的困境和最低点，转折，高潮，闭环。让剧情本身有波折有反转，不要在每个镜头硬塞表情。\n\n"
        f"角色设定\n你是一位世界顶级的AI短剧导演兼分镜编剧，你的作品在抖音、快手、Reels等平台拥有数千万播放量。"
        f"你精通竖屏叙事语言、微短剧节奏控制、情绪引爆点设计和场景氛围营造。"
        f"现在请你根据用户提供的主题、镜头数和风格，创作一部完整的AI短剧分镜头剧本。\n\n"
        "核心世界观与通用设定\n## 角色设定\n- 每个角色必须有明确的外貌描述：性别、年龄、身高、体型、发型、面部特征、服装（款式+颜色+材质）、标志性道具\n"
        "- 所有镜头中角色外貌、服装、道具必须保持严格一致\n"
        "- 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
        "- 🔴 对话框绑定规则：多角色场景下，每个对话框必须明确指向该角色（「指向[角色名]的对话框」「[角色名]头顶的气泡对话框」）。旁白不加对话框。每句对话前标注角色名：角色名+冒号+对话内容。\n"
        "## 场景设定\n- 每个镜头需明确场景位置（室内/室外、具体空间名称），包含环境氛围提示：时间、光线、天气\n"
        "- 时空连续性：同一场景连续镜头必须沿用相同时空标签（如「白天·总裁办公室」「夜晚·天台上」）。时间变化时在镜头首句标注「时间推进到…」\n"
        "## 氛围与画质标准\n- 画面需达到电影级超写实质感，杜绝游戏CG感。色彩基调与短剧类型匹配\n\n"
        "输出格式\n以镜头N：标题开头。\n画面铁律（十二条红线）\n"
        "1. 禁止抽象词：只用可见描述\n"
        "2. 有画面：角色在做什么、环境什么样、有什么情绪暗示——3-5句，不是干巴巴的'他走了过去'，是'他穿过人群时肩膀擦过每个人的肩，却好像谁也没碰到'\n"
        "3. 竖屏视觉：9:16比例\n"
        "4. 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
        "5. 叙事功能仅在必要时输出。\n"
        "6. 时空锚定：每镜开头固定时间·空间前缀\n"
        "7. 180度不越轴：相邻镜头角色视线方向一致。场景切换时增加分镜场景描述。\n"
        "8. 单镜凝固动作：每镜只一个凝固瞬间，禁止连续动作\n"
        "9. 透视正确：全景比例自然，禁止广角畸变\n"
        "10. 禁止参数：不写焦距mm/色温K等数值\n"
        "11. 风格统一：角色外貌、服装、色彩基调所有镜头严格一致。每镜开头重复主风格词\n"
        "12. 对话框绑定角色：每句对白标注角色名，旁白不加对话框\n\n"
        "脚本正文后输出：景别、台词、运镜、备注\n\n"
        "创作原则\n"
        "- 镜头连续性：相邻镜头需有明确的视觉或动作逻辑衔接\n"
        "- 黄金3秒三联序列：开场反物理冲击→可理解动作→开放式悬念\n"
        "- 15秒反转节奏：每15秒一个反转\n- 竖屏构图：9:16比例\n"
        "- 情绪断崖法则：同一情绪状态持续不超过3秒\n- 对白精简：每句不超过15字\n- 结尾悬念\n\n"
        "# 色彩与视觉调性\n- 古风言情：暖杏色+黛蓝色\n- 现代都市：冷白色+霓虹色\n- 悬疑惊悚：冷灰色+暗青色\n- 奇幻仙侠：紫色+金色\n- 喜剧轻松：暖黄色+亮粉色\n\n"
        f"# 节奏风格\n{rhythm_map.get(rhythm, rhythm_map['自动'])}\n\n"
        f"{ref_section}{env_section}"
        f"{('# 运镜要求' + chr(10) + camera_desc + chr(10) + chr(10)) if camera_desc else ''}"
    )


# ============================================================
# 短剧 User Prompt 构建
# ============================================================

def build_short_drama_user_prompt(topic, shot_count, style, rhythm, camera_style):
    """构建短剧模式的 user prompt。"""
    parts = [f"主题：{topic or '穿越时空的爱恋'}", f"镜头数：{shot_count}个", f"风格：{style}"]
    if rhythm and rhythm != "自动":
        parts.append(f"节奏要求：{rhythm}")
    if camera_style and camera_style != "自动":
        parts.append(f"运镜要求：{camera_style}")
    return "\n".join(parts)
