# -*- coding: utf-8 -*-
"""
aggregator/aigc_prompt_builder.py — V16.1 每镜 AIGC 提示词构建器
==================================================================
把分镜表的每一镜渲染为 AIGC 视频模型可直接消费的提示词。
方法论来源: Seedance 2.5/Wan 3.0 官方手册七要素 + Mx-Shell 五段结构 +
真实视频提示词.skill 的素材来源/设备缺陷/非完美事件方法论。

七要素组装:
  1. 参考绑定   — 生产模式≠T2V 时声明 @图/@视频 绑定
  2. 主体+动作  — 角色一致性锚 + 视觉代偿 (抽象→可见元素)
  3. 空间关系   — screen-left/right、前景/背景、机位关系
  4. 镜头与剪辑 — 景别/角度/运镜路径/焦段/时长
  5. 视觉风格   — 一个光照关键词 + 色调 + 年代设备质感/瑕疵锚
  6. 音频       — 具体声源枚举 + 同期声/配乐声明 + 对白三轴声学
  7. 约束       — 一致性锁定 + 负面排除 (无字幕/水印/logo…)

全部确定性: 同输入同输出 (md5 seed)。
"""
import hashlib as _hashlib
import random as _random


def _rng(seed):
    return _random.Random(int(_hashlib.md5(str(seed).encode("utf-8", "replace")).hexdigest(), 16) % (2 ** 32))


# ============================================================
# 词库
# ============================================================

# 年代设备质感 + 瑕疵锚 (真实感来自缺陷, 不是风格词堆砌)
IMPERFECTION_ANCHORS = {
    "复古": ["胶片颗粒在暗部轻轻浮动", "画面边缘有轻微柔焦与褪色", "镜头偶尔掠过一丝眩光",
             "高光处带着老镜头的轻微晕影", "色彩像存放多年的录像带, 微微偏暖"],
    "现代": ["手持拍摄带来如呼吸般的轻微浮动", "镜头玻璃上偶有一粒灰尘的影子",
             "自动对焦在人物与物件之间犹豫了半秒", "高光边缘带着数码镜头的轻微色散",
             "画面稳定但保留真实的空间杂音"],
    "科幻": ["舱内冷光偶有频闪", "舷窗边缘凝着一层薄雾", "HUD 反光在人物脸上轻轻跳动",
             "金属表面有使用过的划痕与油渍", "空气循环系统的气流让尘埃缓慢漂移"],
    "古装": ["烛火摇曳, 光斑在人物脸上明灭", "织物边缘带着磨损的毛边", "空气中浮尘在光柱里缓慢漂移",
             "木器表面有常年使用的包浆", "窗纸透进的光带着纸纹的肌理"],
}

# 光照关键词 (一个光照关键词 > 十个形容词)
LIGHT_KEYWORD = {
    "晨光柔光": "清晨柔光", "自然顶光": "正午自然光", "斜射暖光": "黄昏斜射暖光",
    "黄昏逆光": "黄昏逆光", "暮色暖光": "暮色暖光", "低照度实用光源": "低照度实用光源",
    "极低照度": "极低照度夜景", "黎明冷光": "黎明冷光",
    "漫射光(阴天)": "阴天漫射光", "顺光/自然光": "自然顺光", "侧顺光": "柔和侧光",
    "阴影增加": "阴影渐重的侧光", "光源不稳定": "忽明忽暗的光源",
    "侧光/逆光(戏剧性)": "戏剧性侧逆光", "底光/顶光": "顶光与底光交错",
    "强光/逆光剪影": "强逆光剪影", "暖光最强": "最暖的一束光",
    "戏剧性光影(顶光/底光)": "戏剧性顶光", "天光/烛火": "天光与烛火混合",
}

# 运镜 → 运镜路径句
CAMERA_PATH = {
    "推": "镜头缓缓向前推进", "拉": "镜头缓缓向后拉远", "摇": "镜头横向摇移扫过空间",
    "跟拍": "镜头贴着人物跟拍", "环绕": "镜头以人物为轴心缓缓环绕", "升降": "镜头垂直升降展开空间",
    "固定": "固定机位, 让画面里的事自己发生", "手持": "手持拍摄, 画面带着呼吸般的浮动",
    "手持快切": "手持快速切换, 画面带着紧张的晃动", "快切": "快速切镜, 节奏压在动作点上",
    "慢推": "镜头极缓地向前推进", "慢摇": "镜头缓慢摇移", "慢拉": "镜头缓缓拉远",
    "快推": "镜头快速推近", "斯坦尼康": "稳定器跟拍, 画面流畅滑行", "航拍": "航拍俯瞰大地",
    "穿越机FPV": "穿越机第一视角高速穿行", "一镜到底跟拍": "一镜到底, 镜头始终不切",
    "游走跟拍": "镜头在空间里游走跟拍", "固定长镜": "固定长镜头, 时间真实流过",
    "对话固定长镜": "固定长镜对准对话, 不切", "慢速环绕": "镜头慢速环绕",
    "POV主观": "第一人称主观视角", "多机位切换": "多机位切换捕捉", "360°环绕": "镜头环绕一周",
}

# 场景声源池 (具体枚举, 非百分比配方)
AUDIO_SOURCES = {
    "雨": ["雨点砸在窗上的声音", "雨水顺着屋檐滴落", "远处雷声滚过"],
    "雪": ["雪落下的簌簌声", "脚踩进雪里的咯吱声", "风掠过空旷的街道"],
    "风": ["风穿过缝隙的声音", "衣角被风掀动的猎猎声", "远处风声渐强"],
    "雾": ["雾中闷闷的环境底噪", "远处传来的模糊人声"],
    "厨房": ["刀碰砧板的节奏", "锅里水汽的滋滋声", "碗筷轻碰"],
    "街道": ["远处车流", "行人脚步", "红绿灯的提示音"],
    "战场": ["兵器相撞", "远处号角", "尘土落下的簌簌声"],
    "太空": ["舱内低频嗡鸣", "仪器规律的滴声", "呼吸声被放大"],
    "客栈": ["碗筷碰撞", "压低的人声", "门外马匹打响鼻"],
    "默认": ["环境底噪", "人物动作的细微声响", "空间里自然的回声"],
}

# 对白三轴声学参数 (按张力段)
VOICE_AXES = {
    "high": {"发声": "声带紧绷, 喉音压低", "节奏": "语速渐慢, 停顿递减", "音调": "尾音下沉, 欲言又止"},
    "mid": {"发声": "气息平稳, 略带气声", "节奏": "语速适中, 句间留半拍", "音调": "平稳, 句尾轻轻收住"},
    "low": {"发声": "放松的自然声线", "节奏": "语速平缓, 停顿自然", "音调": "日常语调, 不刻意"},
    "哭腔": {"发声": "鼻音共鸣, 气声混入", "节奏": "破碎, 偶有停顿", "音调": "起伏不定, 偶有破音"},
    "愤怒": {"发声": "胸腔共鸣加压", "节奏": "短促, 字与字之间发紧", "音调": "压低后突然上扬"},
}

# 角色外观锚 (无上游角色设定时, 按年代给出最小具体外观 — 保证跨镜一致性可描述)
APPEARANCE_POOL = {
    "复古": ["洗得发白的蓝布外套", "旧毛衣, 袖口起了球", "深灰色中山装, 领口磨得发亮",
             "碎花棉袄, 边角缝过补丁", "军绿色旧挎包",
             # V16.1: 民国意象外观 (歌女/租界/百乐门 场景)
             "深色旗袍, 领口盘扣一丝不苟", "阴丹士林蓝旗袍, 外搭旧披肩",
             "长衫外罩针织开衫, 袖口磨白", "西装马甲配怀表链, 领口微旧"],
    "现代": ["深灰色连帽卫衣", "黑色羽绒服, 拉链磨得发白", "白衬衫, 袖口挽起",
             "卡其色风衣, 肩线微皱", "旧T恤配工装裤"],
    "科幻": ["灰白色舱内作训服, 胸前有编号", "深蓝色制服, 肩线带着磨损", "哑光防护服, 袖口有划痕"],
    "古装": ["青色粗布长衫, 下摆沾着尘土", "玄色劲装, 腰间束着旧革带", "月白长袍, 袖口绣纹已褪色",
             "褐色短打, 肩上搭着斗笠"],
}

# 结尾克制句式 (没有X, 只有Y)
ENDING_PATTERNS = [
    "没有台词, 没有爆发, 只有{elem}留在画面里, 慢慢变暗",
    "不堆特效, 不收配乐, 镜头停在{elem}上, 让情绪自己落地",
    "没有解释, 没有回望, 只有{elem}和逐渐远去的环境声",
    "结尾克制: 不煽情, 不点题, {elem}替角色说完最后一句",
]

# 模型适配建议
MODEL_ADVICE = {
    "短视频": "建议 Seedance 2.5 / 可灵 / Wan 3.0 逐段生成; 单镜 5-15s 成功率最高, 超过 20s 的段落建议拆分生成后剪辑拼接; 触发词避免版权词。",
    "竖屏短剧": "建议可灵/Seedance 9:16 竖屏生成; 每集按钩子→反转→卡点拆 3-5 段, 对白段优先保证口型清晰。",
    "长片": "建议按分镜表逐镜生成, 相邻镜头用首尾帧模式衔接; 角色跨镜一致性靠参考图锁定 + 每镜复述外观锚。",
    "广告/MV": "建议 Seedance 2.5 多参考图模式锁定产品/角色; 卡点段按音乐节拍写时间码。",
    "默认": "建议逐镜生成, 单镜不超过 15s; 关键镜头抽卡 3-5 次择优; 跨镜一致性用参考图 + 外观锚复述。",
}


# ============================================================
# 基础工具
# ============================================================

def detect_era(ctx):
    """从 ctx 推断年代类别."""
    era = str(ctx.get("era", "") or "")
    if era in ("古装", "科幻", "复古", "现代"):
        return era
    scene = str(ctx.get("scene", "") or "")
    if any(k in scene for k in ("古装", "武侠", "江湖", "宫廷", "客栈", "古代", "仙侠")):
        return "古装"
    if any(k in scene for k in ("科幻", "太空", "未来", "赛博", "机甲", "飞船", "末日", "废土")):
        return "科幻"
    if any(k in scene for k in ("19", "年代", "旧", "老宅", "县城", "下岗", "磁带",
                                  # V16.1: 民国意象 → 复古 (与 feature_film_engine._detect_era 对齐)
                                  "民国", "旗袍", "百乐门", "歌女", "舞厅", "租界", "留声机", "黄包车")):
        return "复古"
    return "现代"


def build_character_anchor(ctx, max_chars=3):
    """角色一致性锚 — 跨镜复述的外观描述。上游有角色设定则用之, 否则按年代生成最小具体外观."""
    chars = ctx.get("characters") or []
    if not chars:
        return ""
    era = detect_era(ctx)
    pool = APPEARANCE_POOL.get(era, APPEARANCE_POOL["现代"])
    descs = ctx.get("character_desc") or {}
    lines = []
    for i, name in enumerate(chars[:max_chars]):
        name = str(name)
        if name in descs and descs[name]:
            lines.append(f"{name}: {descs[name]} (全部镜头保持该外观一致)")
        else:
            r = _rng(f"appear_{ctx.get('scene','')}_{name}_{i}")
            look = r.choice(pool)
            lines.append(f"{name}: {look}, 发型与体态全部镜头保持一致")
    return "; ".join(lines)


def _light_keyword(shot):
    raw = str(shot.get("stage_light", "") or "")
    for k, v in LIGHT_KEYWORD.items():
        if k in raw or raw in k:
            return v
    return raw or "自然光"


def _camera_path(shot):
    move = str(shot.get("move", "") or "")
    for k, v in CAMERA_PATH.items():
        if k in move:
            return v
    return f"运镜: {move}" if move else "固定机位"


def _audio_sources(shot, ctx, n=3):
    """具体声源枚举 (按天气/地点/场景)."""
    scene = str(ctx.get("scene", "") or "") + str(shot.get("location", "") or "")
    weather = str(shot.get("weather", "") or "")
    picked = []
    if weather and weather in AUDIO_SOURCES:
        picked.extend(AUDIO_SOURCES[weather][:2])
    for key, pool in AUDIO_SOURCES.items():
        if key in ("雨", "雪", "风", "雾", "默认"):
            continue
        if key in scene:
            picked.extend(pool[:2])
            break
    if not picked:
        picked = list(AUDIO_SOURCES["默认"])
    r = _rng(f"audio_{scene}_{weather}_{shot.get('n', 0)}")
    r.shuffle(picked)
    return picked[:n]


def _imperfection(shot, ctx, n=2):
    era = detect_era(ctx)
    pool = list(IMPERFECTION_ANCHORS.get(era, IMPERFECTION_ANCHORS["现代"]))
    r = _rng(f"impf_{ctx.get('scene','')}_{shot.get('n', 0)}_{era}")
    r.shuffle(pool)
    return pool[:n]


def _sound_declaration(ctx):
    """同期声/配乐声明."""
    mood = str(ctx.get("mood", "") or "")
    platform = str(ctx.get("platform", "") or "")
    if any(k in platform for k in ("MV", "广告")):
        return "音乐驱动, 节拍卡点, 环境音垫底"
    if mood in ("史诗", "浪漫", "希望"):
        return "配乐克制进入, 情绪点才铺开, 其余段落只保留同期声"
    return "只保留同期声, 不铺背景音乐"


def render_dialogue_line(who, paren, line, tension=5, mood=""):
    """对白行 + 三轴声学参数."""
    if not line or not str(line).strip() or str(line).strip() in ("……", "…"):
        return f"{who}: (沉默, 只有呼吸声)"
    t = int(tension or 5)
    if t >= 8:
        axes = VOICE_AXES["high"]
    elif t >= 4:
        axes = VOICE_AXES["mid"]
    else:
        axes = VOICE_AXES["low"]
    if "哭" in str(mood) or "悲" in str(mood):
        axes = VOICE_AXES["哭腔"]
    elif "怒" in str(mood):
        axes = VOICE_AXES["愤怒"]
    return (f"{who}: ({paren or '平静'}) 「{line}」 "
            f"[声学: {axes['发声']} / {axes['节奏']} / {axes['音调']}]")


# ============================================================
# 负面约束块 (正向排除优先 + 显式排除行)
# ============================================================

def build_negative_block(ctx):
    era = detect_era(ctx)
    base = ["无字幕", "无水印", "无logo", "画面中不出现文字", "角色外观与服装跨镜头一致"]
    if era in ("复古", "现代", "古装"):
        base.append("杜绝游戏CG感, 保持真人实拍的物理质感")
    if era == "科幻":
        base.append("特效必须有物理反馈, 不做悬浮的光效贴图")
    return "负面约束: " + ", ".join(base)


# ============================================================
# 每镜 AIGC 提示词 (七要素 flowing paragraph)
# ============================================================

def build_shot_aigc_prompt(shot, ctx):
    """把单镜渲染为模型可直接消费的提示词段落."""
    mode = str(ctx.get("production_mode", "文生视频") or "文生视频")
    n = shot.get("n", 0)
    dur = str(shot.get("dur", "5s") or "5s")
    size = str(shot.get("size", "中景") or "中景")
    angle = str(shot.get("angle", "平视") or "平视")
    focal = str(shot.get("focal", "50mm") or "50mm")
    focus = str(shot.get("focus", "") or "").replace("|", ", ")
    location = str(shot.get("location", "") or ctx.get("scene", ""))
    timeline = str(shot.get("timeline", "现在") or "现在")

    parts = []
    # 1. 参考绑定 (按生产模式)
    if mode == "首帧生视频":
        parts.append("[首帧锚定] 以给定首帧为第一帧, 提示词只描述首帧之后的运动与演变, 不重复首帧已有内容。")
    elif mode == "首尾帧生视频":
        parts.append("[首尾帧锚定] 首帧与尾帧已给定, 描述两帧之间的运动轨迹与过渡方式, 保持首尾帧一致。")
    elif mode == "多参考图生视频":
        parts.append("[参考图锁定] 角色/环境/道具外观由参考图锁定, 提示词聚焦动作、运镜与情节推进。")
    elif mode == "参考视频生视频":
        parts.append("[参考视频迁移] 保留参考视频的运动节奏与剪辑节奏, 替换风格与内容。")

    # 2. 主体+动作 (角色锚 + 视觉代偿)
    anchor = build_character_anchor(ctx)
    subject = focus if focus else f"{location}中的主要人物"
    subject = subject.rstrip("。.，, ")
    parts.append(f"主体与动作: {subject}。" + (f" 角色锚: {anchor}。" if anchor and mode == "文生视频" else ""))

    # 3. 空间关系 + 4. 镜头
    path = _camera_path(shot)
    parts.append(f"镜头: {size}, {angle}, {focal} 焦段, {path}, 时长 {dur}。")

    # 5. 视觉风格 (光照关键词 + 色调 + 瑕疵锚)
    light = _light_keyword(shot)
    color = str(shot.get("stage_color", "") or "")
    impf = _imperfection(shot, ctx, 2)
    style = f"光影: {light}"
    if color:
        style += f"; 色调: {color}"
    style += "; 质感: " + ", ".join(impf)
    parts.append(style + "。")

    # 6. 音频
    parts.append(build_audio_desc(shot, ctx))

    # 7. 约束
    parts.append(build_negative_block(ctx) + "。")

    # 时间线标记 (非现在线时显式声明)
    if timeline and timeline != "现在":
        parts.insert(0, f"[时间线: {timeline}]")

    return _dedup_punct(" ".join(parts))


def _dedup_punct(text):
    """折叠重复句号/逗号, 清理'。。'与'，，'等粘连."""
    import re as _re_dp
    text = _re_dp.sub(r"[。]{2,}", "。", text)
    text = _re_dp.sub(r"[，,]{2,}", "，", text)
    text = _re_dp.sub(r"。[，,]+", "。", text)
    text = _re_dp.sub(r"[，,]。", "。", text)
    return text


def build_first_frame_prompt(shot, ctx):
    """首帧/分镜图生成提示词 — 只写静态构图, 不写运动."""
    size = str(shot.get("size", "中景") or "中景")
    angle = str(shot.get("angle", "平视") or "平视")
    focal = str(shot.get("focal", "50mm") or "50mm")
    focus = str(shot.get("focus", "") or "").replace("|", ", ")
    location = str(shot.get("location", "") or ctx.get("scene", ""))
    light = _light_keyword(shot)
    color = str(shot.get("stage_color", "") or "")
    impf = _imperfection(shot, ctx, 1)
    anchor = build_character_anchor(ctx)
    s = f"静态构图: {size}, {angle}, {focal} 焦段。{focus}。环境: {location}。光影: {light}"
    if color:
        s += f", 色调 {color}"
    if anchor:
        s += f"。角色: {anchor}"
    s += f"。质感: {impf[0]}。无运动, 无文字, 无水印。"
    return s


def build_audio_desc(shot, ctx):
    """音频描述: 声源枚举 + 同期声/配乐声明."""
    sources = _audio_sources(shot, ctx, 3)
    decl = _sound_declaration(ctx)
    return f"音频: {'、'.join(sources)}; {decl}"


# ============================================================
# 短视频五段结构 (Mx-Shell 方法)
# ============================================================

def _core_theme_tags(ctx):
    """核心主题 pipe 标签."""
    tags = []
    mood = str(ctx.get("mood", "") or "")
    visual = str(ctx.get("visual", "") or "")
    era = detect_era(ctx)
    era_tag = {"古装": "东方古典美学", "科幻": "硬核科幻", "复古": "年代质感", "现代": "写实当代"}[era]
    tags.append(era_tag)
    if mood:
        tags.append(f"{mood}情绪")
    if visual and visual not in ("写实",):
        tags.append(visual)
    tags.append("真人实景拍摄")
    tags.append("电影级质感")
    return " | ".join(tags[:5])


def _camera_rules_block(ctx, single_shot):
    if single_shot:
        return ("单镜头: 一镜到底, 无剪辑。\n"
                "呼吸感: 手持拍摄, 全程保持极其轻微的、如呼吸般的镜头浮动, 增强临场感。")
    return ("多分镜: 按分镜表逐镜生成, 镜头之间硬切。\n"
            "呼吸感: 非固定机位镜头保持轻微手持浮动, 固定机位保持绝对稳定。")


def build_five_section_block(ctx, beats, single_shot=False, ending_elem=""):
    """五段结构: 核心主题/人物与基础设定/氛围与画质/运镜规则/画面内容 + 结尾 + 模型建议 + 自检.
    beats: [{name, time, action, camera, vfx, sound}] 时间拍列表 (写法A).
    """
    era = detect_era(ctx)
    lines = []
    lines.append(f"【核心主题】{_core_theme_tags(ctx)}")
    # 人物与基础设定
    anchor = build_character_anchor(ctx)
    scene = str(ctx.get("scene", "") or "")
    lines.append("【人物与基础设定】")
    lines.append(f"人物: {anchor or '主角, 外观全部镜头保持一致'}")
    lines.append(f"场景: {scene}")
    # 氛围与画质
    sim_device = {
        "复古": "模拟 16mm 胶片摄影机, 复古定焦镜头",
        "科幻": "模拟 IMAX 胶片摄影机, 搭配 Panavision C 系列镜头",
        "古装": "模拟变形宽银幕镜头, 自然光为主",
        "现代": "模拟全画幅电影机, 35mm/50mm 定焦镜头",
    }[era]
    mood = str(ctx.get("mood", "") or "")
    lines.append("【氛围与画质】")
    lines.append(f"模拟设备: {sim_device}")
    lines.append(f"色彩与影调: 按情绪定调 ({mood or '中性'}), 暗部保留细节, 边缘轻微柔焦与适度颗粒感")
    lines.append(f"风格核心: {era_tag_style(era)}, 强调真实物理反馈, 拒绝悬浮特效贴图")
    lines.append(f"声音: {_sound_declaration(ctx)}")
    # 运镜规则
    lines.append("【运镜规则】")
    lines.append(_camera_rules_block(ctx, single_shot))
    # 画面内容
    lines.append("【画面内容】")
    for b in beats:
        seg = f"{b.get('time', '')} · {b.get('name', '')}"
        detail = []
        if b.get("action"):
            detail.append(f"动作: {b['action']}")
        if b.get("camera"):
            detail.append(f"镜头: {b['camera']}")
        if b.get("vfx"):
            detail.append(f"特效: {b['vfx']}")
        if b.get("sound"):
            detail.append(f"声音: {b['sound']}")
        lines.append(seg + "\n" + "\n".join(detail))
    # 结尾克制
    r = _rng(f"ending_{scene}_{mood}")
    elem = ending_elem or "环境声"
    lines.append("【结尾】" + r.choice(ENDING_PATTERNS).format(elem=elem))
    # 模型建议
    platform = str(ctx.get("platform", "") or "")
    key = "短视频"
    for k in MODEL_ADVICE:
        if k in platform:
            key = k
            break
    lines.append("【模型适配建议】" + MODEL_ADVICE[key])
    # 自检清单
    lines.append("【自检清单】")
    lines.append("1) 五段结构齐全 2) 有摄影机/镜头描述 3) 有呼吸感或稳定性声明 4) 有声音声明 "
                 "5) 瑕疵/真实感锚≥2处 6) 结尾克制不堆特效 7) 无'完美/震撼/史诗/绝美'类空洞词 "
                 "8) 无版权触发词 9) 时长符合目标 10) 每段有具体动作而非情绪形容词")
    return "\n".join(lines)


def era_tag_style(era):
    return {
        "古装": "东方古典美学 + 实景质感",
        "科幻": "重工业机械美学 + 先进科技融合, 保持机械的重量感",
        "复古": "年代写实, 胶片颗粒, 生活流",
        "现代": "写实当代, 自然光与生活质感",
    }.get(era, "写实")


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ctx = {"scene": "父女在厨房, 雨夜, 1998年哈尔滨", "director": "王家卫", "mood": "孤独",
           "characters": ["父亲", "女儿"], "platform": "短视频", "era": "复古"}
    shot = {"n": 1, "size": "特写", "angle": "俯拍", "focal": "85mm", "dur": "4s",
            "move": "慢推", "focus": "父亲的手停在砧板上, 刀尖垂下半寸",
            "stage_light": "低照度实用光源", "stage_color": "低饱和暖褐",
            "location": "厨房", "weather": "雨", "timeline": "现在"}
    p = build_shot_aigc_prompt(shot, ctx)
    assert len(p) >= 80, "提示词过短"
    assert "镜头" in p and "音频" in p and "负面约束" in p
    print(p)
    print()
    print("首帧:", build_first_frame_prompt(shot, ctx))
    print()
    beats = [{"name": "凝视", "time": "0-3秒", "action": "父亲切菜的手停下", "camera": "极缓前推",
              "sound": "雨声 + 刀碰砧板"},
             {"name": "触发", "time": "3-8秒", "action": "女儿翻出旧信", "camera": "切特写",
              "sound": "信纸展开的脆响"}]
    print(build_five_section_block(ctx, beats, single_shot=False, ending_elem="雨声"))
    print("\n自检通过")
