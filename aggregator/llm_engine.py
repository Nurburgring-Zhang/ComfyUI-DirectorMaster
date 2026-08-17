# -*- coding: utf-8 -*-
"""
aggregator/llm_engine.py — V8.0 LLM 原生生成引擎
=============================================
7 域规则 + 534 导演档案 + Hell Grind 约束.

每个节点在无 AI 时使用内置深度模板 (本文件含模板降级逻辑).
"""

DOMAIN_RULES = {
    "核心": (
        "【核心总控】\n"
        "1. 输出10维灵魂参数(创造力/想象力/艺术表达/镜头技巧/氛围掌控/灵感/疲劳/怀疑/叛逆/突破) 与导演档案一致\n"
        "2. 审美判断8原则:主体明确/光影层次/色彩节制/构图张力/情绪留白/节奏控制/细节真实/反AI\n"
        "3. 风格指南:调色(6色彩库)+色彩口诀+60-30-10色板\n"
        "4. 导演意图明确观众情绪目标(具体,非'complex')\n"
        "5. 统一电影提示词:场景+人物+动作+光影+情绪+物件,五感俱全\n"
        "6. 灵魂注入串格式规范"
    ),
    "剧本": (
        "【剧本生成】\n"
        "1. 三幕结构(建立/对抗/解决)+前5秒钩子+潜文本(角色没说的)\n"
        "2. 对白极简(≤20字/句),留白多,物件承载情绪\n"
        "3. 角色弧(Want≠Need),身体习惯+口头禅+标志性物件\n"
        "4. 场次节奏:长镜+短切交替,情绪曲线递进\n"
        "5. 每场给:场景标题/动作/对白/潜文本/镜头建议\n"
        "6. 反AI:无套路反转,无说教,动作和物件表达"
    ),
    "创意氛围": (
        "【创意生成】\n"
        "1. 概念立项:一句话概念+类型+目标受众+商业卖点+灵魂维度\n"
        "2. 主题哲学:主题句+道德困境+哲学内核\n"
        "3. 世界设定:空间/时间/社会规则/视觉锚点(色/光/材质)\n"
        "4. 服化道:时代+材质+色彩方案,每件道具叙事功能\n"
        "5. 漫剧分镜:日漫/美漫/条漫/动态漫4形态,分格+对话框+拟声词+视线引导\n"
        "6. 各类型(VFX/MV/调色/剪辑/QA/绘本/互动剧)按本域规范"
    ),
    "美术指导": (
        "【美术生成】\n"
        "1. 美术圣经:整体视觉基调+主材质+色彩系统60-30-10+光影9D+空间\n"
        "2. 色彩60_30_10:主色60%+辅色30%+点缀色10%,引用6色彩库\n"
        "3. 光影9D:方向/强度/色温/软硬/对比/层次/时间/特殊/氛围\n"
        "4. 摄影8大师:锚定导演档案的镜头/构图(9构图法则)\n"
        "5. 视觉语言参数:焦段mm/光圈T/景别/构图/比例/色温K 具体数值\n"
        "6. 空间一致性:空间类型+尺寸+角色位置+道具+连续运动"
    ),
    "声音设计": (
        "【声音生成】\n"
        "1. 声音提示词:环境层+拟音层+心声层,三层叠加\n"
        "2. 音乐:风格+情感曲线+节拍BPM+乐器+留白点\n"
        "3. 声音层:说话/沉默角色台词+身体动作+空气层+脚步+环境+远景\n"
        "4. 沉默:总时长+停顿占比+眼神对视+空镜留白,留白即叙事\n"
        "5. 每个声音元素:音源/距离/动态/情绪功能\n"
        "6. 声音先于画面时标注(情绪前置)"
    ),
    "画面": (
        "【画面生成】\n"
        "1. 分镜:景别+机位+运动+时长+表演+光影+情绪\n"
        "2. 镜头运动:push/pull/truck/pan/tilt/zoom+幅度+速度\n"
        "3. 30秒6段:6段叙事节奏+每段时间戳+情绪递进\n"
        "4. 表演块:WHAT障碍COST策略TURN+微表情+眨眼+手部\n"
        "5. 选片:8维权重(叙事/情感/节奏/视觉/表演/空间/审美/反AI)\n"
        "6. H3提示词:[Shot N] At MM:SS.mmm 格式+5段结构"
    ),
    "终极汇总": (
        "【终极汇总】\n"
        "1. 制作手册6章节:导演总控→创意→剧本→美术→画面→声音\n"
        "2. 每章节给具体决策(非摘要),保留全部技术参数\n"
        "3. 导演总控摘要:灵魂+审美+风格+意图+签名浓缩到1页\n"
        "4. 剧本+视觉圣经:剧本+美术+画面重组为可拍摄文档\n"
        "5. 声音设计方案:三层声音+音乐+沉默整合\n"
        "6. 输出可直接交付制作团队"
    ),
}


def _get_director_block(director):
    """从 534 导演库提取档案块."""
    try:
        from director_data_unified import get_director_profile, get_director, COLOR_STYLES_5, COMPOSITION_RULES_9
        prof = get_director_profile(director) or get_director(director)
        lines = []
        if prof and isinstance(prof, dict):
            for k, v in prof.items():
                lines.append(f"  {k}: {v}")
        color = "\n【6色彩库】" + " | ".join(
            f"{k}:{v.get('5维标签','')}" if isinstance(v, dict) else str(v)
            for k, v in COLOR_STYLES_5.items()
        )
        comp = "\n【9构图法则】" + " | ".join(
            v.get("name", k) if isinstance(v, dict) else str(v)
            for k, v in COMPOSITION_RULES_9.items()
        )
        return "\n".join(lines) + color + comp
    except Exception:
        return ""


# 每域1个精选正例 — few-shot。V13.3: 内容中立的风格/结构示范 (不注入具体故事),
# 让 LLM 基于 context 的真实场景/情绪/意图原生生成, 而非漂移到固定 demo。
FEW_SHOT = {
    "剧本": (
        "【输出范例·风格参考(仅示范写法, 内容须按当前场景原生)】INT. [本场地点] - [时间]\n"
        "[角色A] 做一个日常动作, 节奏里藏着一处停顿——那是情绪的信号.\n"
        "[角色B] 在场, 但视线避开 [角色A]. 两人无话, 或只说半句.\n"
        "[角色A]: (不抬头) [一句言不由衷的短句].\n [角色B]: [极简回应].\n"
        "(特写: 一件承载秘密的物件, 细节暗示未被说出的往事.)\n"
        "潜文本: 角色想说 X, 说出口的是 Y. 物件承载未说出口的话. 用动作与停顿, 不用旁白解释."
    ),
    "画面": (
        "【输出范例·风格参考(仅示范写法)】[Shot 1] At 00:00.000 [景别]·[机位]·[光]: "
        "环境光把空间染成主色调, 光源只照亮叙事焦点. [角色] 的核心动作. 焦段[XX]mm, 光圈T[X.X].\n"
        "[Shot 2] At 00:0X.000 [景别]·[角度]·[运动]: 关键细节特写, 身体语言泄露情绪. [XX]mm.\n"
        "声音: [环境声]+[关键拟音], 在情绪点骤停. 转场: [切法]. 叙事目的: [这个镜头回答上一镜的什么]."
    ),
    "美术指导": (
        "【输出范例·风格参考(仅示范写法)】色彩60-30-10: 60%[主色, 按场景基调] / 30%[辅色, 按情绪冷暖] / 10%[点缀色, 来自关键物件].\n"
        "光影9D: [主光方向]+[辅光], [软/硬]光, [对比度], [层次: 前景/中景/背景], 色温[XXXX]K.\n"
        "材质: 按年代与角色前史选 [织物/木/金属/玻璃], 强调磨损/使用痕迹. 构图: [法则]+[空间框景]."
    ),
    "声音设计": (
        "【输出范例·风格参考(仅示范写法)】环境层: [场景底噪](距离/持续性)+[年代特征声](时断).\n"
        "拟音层: [关键物件声](材质×材质, 尾音具体)+[角色动作声].\n"
        "沉默层: 关键情感点前静默 [X]s, 呼吸声替代配乐. 留白即叙事."
    ),
    "创意氛围": (
        "【输出范例·风格参考(仅示范写法)】一句话概念: [一个具体物件/动作] 让 [角色关系] 在 [情境] 中 [情感变化].\n"
        "类型: [类型] | 受众: [受众] | 卖点: 每个观众都能在 [角色处境] 里看见自己没说出口的那件事.\n"
        "哲学内核: [主题词] 是保护, 还是伤害? 物件承载未说出口的 [情感]."
    ),
    "核心": (
        "【输出范例·风格参考(仅示范写法)】主导情感: [情绪](权重0.9+) | 融合: 主导.\n"
        "10维: 创造力/想象力/艺术表达/镜头技巧/氛围掌控 按导演风格取 0.8-0.95, 疲劳/怀疑 取低值.\n"
        "观众应感到: [具体可感的情绪, 非'complex'这类抽象词]."
    ),
    "终极汇总": (
        "【输出范例·风格参考(仅示范写法)】手册第一章导演总控: 导演=[导演], 情绪=[情绪], 观众应感到=[具体情绪].\n"
        "色彩60-30-10, 光影9D, 摄影参考. 每章给具体决策(非摘要), 保留全部技术参数."
    ),
}


def _domain_mode_prompt(node_type, mode, context):
    """V14.3-MERGED: 绘本/短剧/分镜 领域系统提示词 (modes_book/modes_drama/modes_storyboard 复活接线).

    命中领域时返回对应领域专家的创作规则块, 否则返回空串. 全部惰性导入+异常降级.
    """
    m = str(mode or "")
    scene = str(context.get("scene", "") or "")[:60]
    try:
        import hashlib as _hl_dm

        def _det_sense():
            try:
                from story_sense_data import STORY_SENSE_LIBRARY
                if not STORY_SENSE_LIBRARY:
                    return ""
                i = int(_hl_dm.md5(scene.encode("utf-8", "replace")).hexdigest(), 16) % len(STORY_SENSE_LIBRARY)
                return STORY_SENSE_LIBRARY[i]
            except Exception:
                return ""

        if any(k in m for k in ("绘本", "睡前", "儿童")):
            from modes_book import _build_picture_book_system_prompt
            return str(_build_picture_book_system_prompt(
                scene or "未命名绘本", "", "", 8, "水彩插画", "温暖", "每页10-30字",
                "3-6岁幼儿", [], _det_sense))[:1500]
        if any(k in m for k in ("短剧", "微短剧", "小程序")):
            from modes_drama import build_short_drama_system_prompt
            return str(build_short_drama_system_prompt(
                scene or "未命名短剧", "", "", 8, "都市爽剧", "快节奏钩子",
                "快切+推近", "高饱和", [], _det_sense))[:1500]
        if any(k in m for k in ("分镜", "故事板", "镜头")):
            from modes_storyboard import _build_storyboard_system_prompt
            return str(_build_storyboard_system_prompt(
                m, "电影感", scene or "未命名分镜", "", "", [], _det_sense))[:1500]
    except Exception:
        return ""
    return ""


def _build_native_prompt(node_type, mode, director, context):
    """构建 LLM 原生生成 system prompt (含导演档案+域规则+few-shot+Hell Grind)."""
    db = _get_director_block(director)
    rule = DOMAIN_RULES.get(node_type, DOMAIN_RULES["核心"])
    fewshot = FEW_SHOT.get(node_type, FEW_SHOT["核心"])
    scene = context.get("scene", "")
    mood = context.get("mood", "")
    intent = context.get("intent", "")
    base = (
        f"你是世界顶级影视导演集群的首席创作总监, 具备王家卫/诺兰/塔可夫斯基/"
        f"奉俊昊/是枝裕和/库布里克/黑泽明级别的视听语言能力.\n"
        f"当前任务: {node_type} — {mode} 模式\n"
        f"导演锚定: {director}\n"
        f"场景: {scene}\n情绪基调: {mood}\n导演意图(观众应感到): {intent}\n\n"
        f"【导演档案】\n{db}\n\n"
        f"{rule}\n\n"
        f"{fewshot}\n\n"
        f"【Hell Grind 约束】\n"
        f"1. 锁定导演档案, 镜头/光/节奏/色彩/构图/声音/情绪 不得漂移\n"
        f"2. 用五感细节(可视可听可触)替代抽象形容词\n"
        f"3. 技术参数具体(焦段mm/光圈T/色温K/比例/时长秒)\n"
        f"4. 物件承载情绪, 动作表达潜文本\n"
        f"5. 绝不使用AI套话: masterpiece/best quality/ultra detailed/stunning/"
        f"breathtaking/cinematic lighting/4K/8K/HDR/photorealistic/epic 等\n"
        f"6. 输出长度不少于结构参考的80%, 内容必须原生生成(非改写参考)"
    )
    # V14.3-MERGED: 领域专家规则注入 (绘本/短剧/分镜 复活库)
    _domain = _domain_mode_prompt(node_type, mode, context)
    if _domain:
        base += f"\n\n【领域专属创作规则 ({mode})】\n{_domain}"
    return base


_REF_SHOWN = 5000  # generate_native 只把 structural_reference[:5000] 喂给模型


def _bigram_overlap_ratio(a, b):
    """字符 bigram 重合率 (0-1), 用于检测 LLM 是否直接照抄结构参考."""
    if not a or not b or len(a) < 4 or len(b) < 4:
        return 0.0
    sa = set(a[i:i+2] for i in range(len(a) - 1))
    sb = set(b[i:i+2] for i in range(len(b) - 1))
    if not sa:
        return 0.0
    return len(sa & sb) / len(sa)


def _quality_gate(result, structural_reference, director, context=None):
    """质量门控 (V13.5 强化): 长度(可达基准) + 全词表反AI + 照抄检测 + 遵循度信号.
    返回 (accept, reason)."""
    context = context or {}
    # 长度门控 — 基准取 min(参考全长, 模型实际可见的5000字), 避免长模板下门槛数学不可达
    if not result or len(result) < 200:
        return False, "长度不足(<200)"
    baseline = min(len(structural_reference), _REF_SHOWN)
    if len(result) < baseline * 0.5:
        return False, f"长度不足(<参考可见{baseline}的50%)"

    # 照抄检测 — LLM 直接复制结构参考 = 零虚假红线, 拒收
    copy_ratio = _bigram_overlap_ratio(result, structural_reference[:_REF_SHOWN])
    if copy_ratio > 0.85:
        return False, f"疑似照抄结构参考(重合{round(copy_ratio*100)}%)"

    # 反AI词后置扫描 — 全词表 (修复只扫前60英文短语对中文套话致盲)
    try:
        from anti_ai_vocab import ANTI_AI_PHRASES
        hits = 0
        low = result.lower()
        for phrase in ANTI_AI_PHRASES.keys():
            if phrase.lower() in low:
                hits += 1
        if hits > 3:
            return False, f"AI套话{hits}处"
    except Exception:
        pass

    # 遵循度软信号 — 导演/场景关键词回现; 与照抄叠加时才拒收, 单独不拒(防误杀)
    try:
        scene_kw = [k for k in str(context.get("scene", "")).split(",") if len(k.strip()) >= 2]
        scene_hits = sum(1 for k in scene_kw if k.strip() in result)
        director_hit = 1 if (director and str(director) in result) else 0
        if copy_ratio > 0.6 and scene_hits == 0 and director_hit == 0:
            return False, "低遵循度且高重合(疑似模板改写)"
    except Exception:
        pass

    return True, ""


def _count_cliche(text):
    """统计文本中反AI词表命中数 (用于迭代前后对比)."""
    try:
        from anti_ai_vocab import ANTI_AI_PHRASES
        low = text.lower()
        return sum(1 for p in ANTI_AI_PHRASES.keys() if p.lower() in low)
    except Exception:
        return 0


def _refine_draft(draft, node_type, mode, director, context, api_url, api_key, model_name,
                  structural_reference, temperature=0.5, max_tokens=6144):
    """V13.5 多轮迭代: 对初稿做一轮"反AI清洗+真人化+导演润色"修订 (基于 ITERATION_TEMPLATES 精神).
    返回修订版(若过门控且套话不比初稿多), 否则 None (调用方保留初稿)。"""
    if not draft or not api_url:
        return None
    from pln_llm import call_ai
    context = context or {}
    revise_prompt = (
        f"你是世界顶级导演 {director} 的剧本医生。下面是「{node_type}·{mode}」的初稿, 请按三轮标准修订:\n"
        f"【第一轮·反AI清洗】逐句删除套路短语与空洞副词(缓缓地/深深地/静静地), 把抽象情绪改成具体动作。\n"
        f"【第二轮·真人化】加入不完美细节/口头禅/身体细节/沉默, 对白控制在15字内。\n"
        f"【第三轮·导演润色】按 {director} 的镜头/节奏/视觉签名润色, 场景={context.get('scene','')}, 情绪={context.get('mood','')}。\n\n"
        f"要求: 保留初稿的章节结构与全部具体技术参数, 只提升文学性与真实感, 不得照抄结构参考, 不得增删章节。\n\n"
        f"---初稿---\n{draft[:6000]}\n---初稿---\n\n现在输出修订后的完整版本:"
    )
    result, err = call_ai(api_url, api_key, model_name,
                          f"你是 {director} 级别的剧本医生, 严格遵循反AI词表与导演档案。",
                          revise_prompt, temperature, max_tokens)
    accept, reason = _quality_gate(result, structural_reference, director, context)
    if not accept:
        return None
    # 修订版套话不得多于初稿, 且长度达标
    try:
        from anti_ai_vocab import clean_anti_ai_text
        refined = clean_anti_ai_text(result) or result
    except Exception:
        refined = result
    baseline = min(len(structural_reference), _REF_SHOWN)
    if not refined or len(refined) < baseline * 0.5:
        return None
    if _count_cliche(refined) > _count_cliche(draft):
        return None
    return refined


def generate_native(node_type, mode, director, context, api_url, api_key, model_name,
                    structural_reference, temperature=0.75, max_tokens=6144, iterate=True):
    """LLM 原生生成. 失败/无配置时返回 structural_reference (零降级)."""
    if not api_url or not structural_reference:
        return structural_reference

    from pln_llm import call_ai

    system_prompt = _build_native_prompt(node_type, mode, director, context)
    # V13.5: 移除"保留所有数值/物件名"矛盾指令(会授权搬运模板虚构内容),
    # 改为要求按场景+导演档案重新推导技术参数, 杜绝照抄模板虚构。
    user_message = (
        f"请以世界顶级导演 {director} 的视角, 原生生成一份「{node_type}·{mode}」级作品.\n\n"
        f"结构参考(仅了解章节格式与组织方式, 严禁照抄其具体内容):\n"
        f"---结构参考---\n{structural_reference[:_REF_SHOWN]}\n---结构参考---\n\n"
        f"要求:\n"
        f"- 严格遵循导演档案与域规则\n"
        f"- 内容必须原生创作, 深度与文学性远超结构参考, 不得改写/搬运结构参考的具体内容\n"
        f"- 具体技术参数(焦段/光圈/色温/时长等)依据场景与导演档案重新推导, 不照抄参考数值\n"
        f"- 紧扣场景/情绪/导演意图, 输出可直接用于拍摄/生成\n"
        f"现在输出原生生成的完整作品:"
    )

    result, err = call_ai(api_url, api_key, model_name, system_prompt,
                          user_message, temperature, max_tokens)
    accept, reason = _quality_gate(result, structural_reference, director, context)
    if accept:
        # 反AI词后置清洗 (保留内容, 去除AI套话)
        draft = result
        try:
            from anti_ai_vocab import clean_anti_ai_text
            cleaned = clean_anti_ai_text(result)
            baseline = min(len(structural_reference), _REF_SHOWN)
            if cleaned and len(cleaned) > baseline * 0.5:
                draft = cleaned
        except Exception:
            pass
        # V13.5 多轮迭代: 初稿→修订 (反AI清洗+真人化+导演润色), 修订失败则保留初稿
        if iterate:
            try:
                refined = _refine_draft(draft, node_type, mode, director, context,
                                        api_url, api_key, model_name, structural_reference)
                if refined:
                    return refined
            except Exception as _re:
                import sys as _sr
                _sr.stderr.write(f"[DirectorMaster] 迭代修订失败→保留初稿: {type(_re).__name__}\n")
        return draft
    # 显式上报失败原因 (不静默), 然后降级到模板
    import sys as _s
    _s.stderr.write(f"[DirectorMaster] AI降级→模板: {reason or err or '质量门控未过'}\n")
    return structural_reference