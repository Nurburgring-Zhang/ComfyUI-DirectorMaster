"""
MiniMax-H3 Prompt Framework Knowledge Base (Phase 36.2)

集成 MiniMax-H3 (MiniMaxAI/MiniMax-H3) 官方 prompt 写作框架:

1. 5 种生成模式 (T2VA / I2VA / FL2VA / L2VA / Ref2VA)
2. Camera Motion 3 维 (motion type + amplitude + speed) - 13 种 motion types
3. Reference Labels (<Subject N> / <Picture N> / <Video N> / <Audio N>)
4. Speaker IDs (S1) (S2) 跨 shot 稳定
5. <d>[Language] ...</d> dialogue 格式
6. <scenetrans> / <cutoff> 跨切对话控制
7. Non-diegetic music 1-3 句
8. overall_soundscape 1-4 句
9. 6 段 Ref2VA: subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music
10. 3 关系 markers: fully_preserved / partially_preserved / weak_reference

来源: https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills
       https://huggingface.co/MiniMaxAI/MiniMax-H3/tree/main/docs
"""

# === 5 种 H3 生成模式 (MiniMax H3 prompt framework) ===
H3_MODES = {
    "T2VA": {
        "name_cn": "文生音视频",
        "description": "Builds a complete audiovisual timeline from text",
        "keyframe": "无 (纯文本生成)",
        "structure": "integrated_multimodal_description + overall_soundscape + non_diegetic_music",
        "use_when": "用户只提供文本, 没有参考图/视频/音频",
    },
    "I2VA": {
        "name_cn": "首帧图生视频",
        "description": "T2VA body + first-frame instruction + visual path develops forward",
        "keyframe": "Picture 1 @ 0.00s = Shot 1 first frame",
        "structure": "first-frame instruction + 3 core fields",
        "use_when": "用户提供首帧图, 视频从首帧开始延展",
    },
    "FL2VA": {
        "name_cn": "首尾帧图生视频",
        "description": "T2VA body + first-and-last-frame instruction + continuous path",
        "keyframe": "Picture 1 @ 0.00s, Picture 2 @ S.SS s (final)",
        "structure": "two-image alignment instruction + 3 core fields",
        "use_when": "用户提供首尾两帧图, 生成中间过渡路径",
    },
    "L2VA": {
        "name_cn": "尾帧图生视频",
        "description": "T2VA body + last-frame instruction + path converges to last frame",
        "keyframe": "Picture 1 @ S.SS s (final), 起始帧由模型推断",
        "structure": "last-frame alignment instruction + 3 core fields",
        "use_when": "用户只提供尾帧图, 视频收敛到尾帧",
    },
    "Ref2VA": {
        "name_cn": "全参考模式",
        "description": "Multimodal reference-to-video with images/videos/audio",
        "keyframe": "subject_definitions + 4 种 reference labels (Subject/Picture/Video/Audio)",
        "structure": "6 sections: subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music",
        "use_when": "用户提供图片+视频+音频多种参考, 需要全参考重写",
    },
}

# === Camera Motion 13 种 (MiniMax H3 camera vocabulary) ===
CAMERA_MOTION_TYPES = [
    "Zoom In",       # 焦距变化
    "Zoom Out",
    "Push In",       # 摄像机前推
    "Pull Out",
    "Pan Left",      # 机位不动镜头左转
    "Pan Right",
    "Truck Left",    # 摄像机水平平移
    "Truck Right",
    "Tilt Up",       # 镜头上下转
    "Tilt Down",
    "Pedestal Up",   # 整体上下移
    "Pedestal Down",
    "Arc Shot",      # 弧线运动
    "Tracking Shot", # 跟随主体
    "Static Shot",   # 静止
    "Shake Slightly", # 轻微抖动
    "Shake Strongly", # 强烈抖动
    "POV",           # 主观视角
    "Roll Clockwise",   # 顺时针翻滚
    "Roll Counterclockwise",  # 逆时针翻滚
]

CAMERA_AMPLITUDE = [
    "with small amplitude",   # 小幅
    "with large amplitude",   # 大幅
    "with medium amplitude",  # 中幅 (通常省略)
]

CAMERA_SPEED = [
    "at slow speed",   # 慢速
    "at fast speed",   # 快速
    "at normal speed", # 正常 (通常省略)
]

# === 视觉风格 7 种 (MiniMax H3 style vocabulary) ===
H3_VISUAL_STYLES = [
    "Cinematic",         # 电影感
    "live-action",       # 实拍
    "2D-animated",       # 2D 动画
    "3D CG",             # 3D CG
    "claymation",        # 黏土动画
    "watercolor",        # 水彩
    "vintage film",      # 老电影
]

# === 6 段 Ref2VA 模板 (Full-Reference Mode) ===
H3_REF2VA_SECTIONS = [
    "subject_definitions",  # 定义参考内容 + reference labels
    "summary",              # [task type] + 目标视频 + 主要参考关系
    "retention_analysis",   # 每个 reference label 的保留关系 (fully_preserved/weak_reference 等)
    "detailed_description", # shot-by-shot 主体 (style opening + [Shot 1]... [Shot N])
    "overall_soundscape",   # 1-4 句环境音
    "non_diegetic_music",   # 1-3 句背景乐 (观众专属, 角色听不到)
]

# === 保留关系 markers (Visible content) ===
RETENTION_MARKERS_VISIBLE = [
    "fully_preserved",       # 完全保留
    "partially_preserved",   # 部分保留
    "attribute_transfer",    # 属性转移
    "weak_reference",        # 弱参考
]

# === 保留关系 markers (Audio) ===
RETENTION_MARKERS_AUDIO = [
    "fully_copy",        # 完全复制
    "partially_copy",    # 部分复制
    "reference",         # 引用 (timbre/rhythm/style/lyrics)
    "weak_reference",    # 弱参考
]

# === Reference label 4 种 ===
H3_REFERENCE_LABELS = {
    "<Subject N>": "可复用的可见内容 (人/物/场景/服装/风格/动作/表情), 在 target video 真正使用的内容单元",
    "<Picture N>": "用作具体目标帧/关键帧/构图锚点的参考图",
    "<Video N>": "用作编辑源/续接起点/整体时间结构的参考视频",
    "<Audio N>": "复制或引用的音频信号",
}

# === Shot cut 表述 (5 种标准转场措辞) ===
SHOT_CUT_PHRASES = [
    "the camera cuts to",
    "the shot cuts to",
    "the shot transitions to",
    "the shot changes to",
    "the shot switches to",
]

# === Dialogue/Singing 跨 cut 标记 ===
H3_DIALOGUE_MARKERS = {
    "<d>[Language] ...</d>": "对白/歌词内容, 保留原文 verbatim, 不翻译不重写",
    "<scenetrans>":           "跨切点标记, 配合 'continues seamlessly across the cut' 等表达",
    "<cutoff>":               "被视频结束截断的语音",
}

# === Voice-over 标准句式 ===
VOICEOVER_PHRASES = [
    "says in an off-screen voiceover",
    "while his lips remain completely closed",  # 配音时屏幕角色嘴部必须保持关闭
]

# === 导演镜头调度映射 (35 导演 × H3 motion 13 种) ===
# 关键整合: 把我们 35 导演的标志性镜头调度映射到 H3 camera vocabulary
DIRECTOR_TO_H3_MOTION = {
    "王家卫":   {"primary": "Truck Right", "amplitude": "with small amplitude", "speed": "at slow speed", "phrase": "Truck right with small amplitude at slow speed"},
    "张艺谋":   {"primary": "Static Shot", "amplitude": "with large amplitude", "speed": "at slow speed", "phrase": "Wide static establishing shot"},
    "李安":     {"primary": "Push In",     "amplitude": "with small amplitude", "speed": "at slow speed", "phrase": "Push in with small amplitude at slow speed"},
    "侯孝贤":   {"primary": "Static Shot", "amplitude": "", "speed": "", "phrase": "Long static shot held for emotional breath"},
    "贾樟柯":   {"primary": "Handheld / Tracking Shot", "amplitude": "", "speed": "", "phrase": "Handheld tracking shot in street environment"},
    "诺兰":     {"primary": "Tracking Shot", "amplitude": "with large amplitude", "speed": "at fast speed", "phrase": "Tracking shot at fast speed with large amplitude"},
    "奉俊昊":   {"primary": "Pan Right",    "amplitude": "with small amplitude", "speed": "at slow speed", "phrase": "Symmetric pan with controlled composition"},
    "黑泽明":   {"primary": "Pan Right",    "amplitude": "with large amplitude", "speed": "at slow speed", "phrase": "Multi-figure blocking with weather-as-character"},
    "小津":     {"primary": "Static Shot", "amplitude": "", "speed": "", "phrase": "Tatami-height static shot on domestic geometry"},
    "是枝裕和": {"primary": "Static Shot", "amplitude": "", "speed": "", "phrase": "Domestic static shot with breathing room"},
    "宫崎骏":   {"primary": "Pan Right",    "amplitude": "with large amplitude", "speed": "at slow speed", "phrase": "Wind-driven pan with painted sky movement"},
    "北野武":   {"primary": "Static Shot", "amplitude": "", "speed": "", "phrase": "Static hold then sudden action"},
    "塔可夫斯基": {"primary": "Static Shot", "amplitude": "", "speed": "at slow speed", "phrase": "Ultra-long static shot with natural-light drift"},
    "维伦纽瓦":  {"primary": "Push In",     "amplitude": "with small amplitude", "speed": "at slow speed", "phrase": "Slow push in with wide composition"},
}

# === 4 模式对应 14 段 addon 注入策略 ===
# Phase 36.2: H3 框架注入到 DirectorSoulNode 14 段 addon
H3_ADDON_INJECTION_PLAN = {
    "EDITING_ADDON":      "注入 H3 shot cut 5 措辞 + cut timestamp (MM:SS.mmm) + continuity 规则",
    "PERFORMANCE_ADDON":  "注入 H3 speaker (S1)/(S2) 格式 + <d>[Language]</d> 跨段",
    "SILENCE_ADDON":      "注入 H3 <scenetrans>/<cutoff> 跨切沉默策略 + voiceover 唇闭",
    "COLOR_ADDON":        "注入 H3 visual style 7 种选 1 + palette 锚点",
    "WORLDBUILDING_ADDON":"注入 H3 100 场景库 + first-frame anchor (I2VA) / last-frame landing (L2VA)",
    "THEME_ADDON":        "注入 H3 retention_analysis 'theme_preservation' 维度",
    "ART_ADDON":          "注入 H3 6 段 Ref2VA subject_definitions 模板",
    "SPATIAL_ADDON":      "注入 H3 camera 3D vocabulary (motion + amplitude + speed)",
    "SOUND_ADDON":        "注入 H3 overall_soundscape 1-4 句格式",
    "MUSIC_ADDON":        "注入 H3 non_diegetic_music 1-3 句格式 (instrumentation/tempo/dynamic)",
    "INTENT_ADDON":       "注入 H3 [task type] 前缀 + 5 模式选 1",
    "STORYBOARD_ADDON":   "注入 H3 [Shot N] At MM:SS.mmm 时间戳 + style opening",
    "CHARACTER_ADDON":    "注入 H3 <Subject N> 角色档案 + identity lock",
    "QA_ADDON":           "注入 H3 6 段检查清单 (subject/summary/retention/soundscape)",
}

# === H3 模式自动选择器 ===
def select_h3_mode(has_first_frame: bool = False,
                   has_last_frame: bool = False,
                   has_refs: bool = False) -> str:
    """
    根据用户输入自动选择 H3 模式

    Returns: T2VA / I2VA / FL2VA / L2VA / Ref2VA
    """
    if has_refs:
        return "Ref2VA"
    if has_first_frame and has_last_frame:
        return "FL2VA"
    if has_last_frame and not has_first_frame:
        return "L2VA"
    if has_first_frame and not has_last_frame:
        return "I2VA"
    return "T2VA"


def render_camera_motion(director: str) -> str:
    """
    根据导演返回 H3 风格 camera motion 描述
    Phase 36.2: 整合 H3 camera vocabulary 到 35 导演
    """
    if director in DIRECTOR_TO_H3_MOTION:
        return DIRECTOR_TO_H3_MOTION[director]["phrase"]
    # 默认: 静态 + 推镜
    return "Push in with small amplitude at slow speed"


def render_h3_style_opening(visual_style: str = "Cinematic",
                            shot_size: str = "medium-wide",
                            setting: str = "the scene") -> str:
    """
    H3 风格 [Shot 1] opening 模板

    来源: base-en.txt 第 4.1 节 + Case examples
    """
    style_map = {
        "电影感": "Cinematic",
        "live-action": "Live-action, cinematic",
        "3D CG": "3D CG, cinematic",
        "2D-animated": "2D-animated, cinematic",
        "黏土": "Claymation, cinematic",
        "水彩": "Watercolor, cinematic",
        "老电影": "Vintage film, cinematic",
    }
    style_str = style_map.get(visual_style, f"{visual_style}, cinematic")
    return f"[Shot 1] {style_str}, a {shot_size} shot frames {setting}."


def render_h3_soundscape(ambient: str, action_sound: str = "", human_sound: str = "") -> str:
    """
    H3 overall_soundscape 1-4 句模板

    来源: base-en.txt 第 4.6 节
    """
    parts = []
    if ambient:
        parts.append(ambient)
    if action_sound:
        parts.append(action_sound)
    if human_sound:
        parts.append(human_sound)
    if not parts:
        return "overall_soundscape: N/A"
    return f"overall_soundscape: {' '.join(parts[:4])}"


def render_h3_nondiegetic_music(instrumentation: str, tempo: str = "slow",
                                dynamic: str = "sustained") -> str:
    """
    H3 non_diegetic_music 1-3 句模板

    来源: base-en.txt 第 4.7 节
    """
    if not instrumentation:
        return "non_diegetic_music: N/A"
    return f"non_diegetic_music: {instrumentation} at a {tempo} tempo, {dynamic}."


def render_h3_dialogue(speaker_id: str, language: str, content: str,
                       is_voiceover: bool = False) -> str:
    """
    H3 dialogue 模板

    来源: base-en.txt 第 4.4 节
    """
    prefix = f"{speaker_id} says in an off-screen voiceover: " if is_voiceover else f"{speaker_id} says: "
    suffix = " while his lips remain completely closed." if is_voiceover else ""
    return f'{prefix}<d>[{language}] {content}</d>{suffix}'


# === 13 个官方 SKILL 摘要 (供 DirectorSoulNode 跨场景调用) ===
H3_OFFICIAL_SKILLS_SUMMARY = {
    "h3-prompt-writing": "5 模式 prompt 写作 (T2VA/I2VA/FL2VA/L2VA/Ref2VA) + camera + speakers + audio",
    "3d-animation-short-generator": "10 步端到端 3D 动画工作流 (intake → brief → outline → character → scene → shot table → storyboard → model choice → clip render → assembly → BGM → QC)",
    "brand-promo-video-generator": "10 步品牌宣推视频 (asset intake → truth sheet → provenance → story spine → beats → motion language → confirm → produce → verify → deliver)",
    "music-video-subtitle-generator": "MV 字幕 + 节奏同步 (preflight → contract → reference roles → preset grammar → prompt structure → BGM continuity → checklist → canvas delivery → final gen)",
    "minimalist-product-ad-generator": "Apple 风格产品广告 (start gate → asset check → brief → narrative spine → motion language → copy → 3 anchor photos → beat storyboard → video gen → music-2.6 BGM → assembly → delivery)",
    "co-op-game-intro-generator": "双人合作游戏开场 (style → player info → GPT confirmation image → approval → refill H3 video prompt → generate → repair)",
    "papercraft-stop-motion-explainer": "纸质定格动画讲解 (目标提取 → 视觉隐喻 → 角色/场景/道具 → 概念预览 → 故事板 → 相机/转场/声音 → 阶段批准 → 审核)",
    "paper-collage-explainer-generator": "纸质拼贴讲解 (meaning → metaphor → 计划 + storyboard → halftone collage stills → stop-motion clips → optional assembly)",
    "handdrawn-live-video-generator": "手绘+实拍混合 (physical contact → continuous morphing → escape route → handheld chase → H3 15s 16:9 prompt → generation → realism check)",
}


def get_h3_prompt_framework_summary() -> str:
    """返回 H3 框架完整摘要 (供 DirectorSoulNode 注入)"""
    lines = ["=== MiniMax-H3 Prompt Framework Summary ===\n"]
    lines.append("# 5 生成模式:")
    for k, v in H3_MODES.items():
        lines.append(f"  {k} ({v['name_cn']}): {v['description']}")
    lines.append(f"\n# Camera Motion: {len(CAMERA_MOTION_TYPES)} motion types × {len(CAMERA_AMPLITUDE)} amplitudes × {len(CAMERA_SPEED)} speeds")
    lines.append(f"\n# Visual Styles: {', '.join(H3_VISUAL_STYLES)}")
    lines.append(f"\n# Ref2VA 6 段: {' / '.join(H3_REF2VA_SECTIONS)}")
    lines.append(f"\n# Retention Markers (Visible): {', '.join(RETENTION_MARKERS_VISIBLE)}")
    lines.append(f"\n# Retention Markers (Audio): {', '.join(RETENTION_MARKERS_AUDIO)}")
    lines.append(f"\n# Reference Labels: {', '.join(H3_REFERENCE_LABELS.keys())}")
    lines.append(f"\n# 13 导演 → H3 camera motion 映射 (DirectorSoulNode 14 段 addon 注入)")
    lines.append(f"\n# 14 段 addon × H3 注入策略: {' / '.join(H3_ADDON_INJECTION_PLAN.keys())}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_h3_prompt_framework_summary())
    print()
    print("=== Test Cases ===")
    print(f"select_h3_mode() = {select_h3_mode()}")
    print(f"select_h3_mode(has_first_frame=True) = {select_h3_mode(has_first_frame=True)}")
    print(f"select_h3_mode(has_first_frame=True, has_last_frame=True) = {select_h3_mode(has_first_frame=True, has_last_frame=True)}")
    print(f"select_h3_mode(has_refs=True) = {select_h3_mode(has_refs=True)}")
    print()
    print(f"render_camera_motion('王家卫') = {render_camera_motion('王家卫')}")
    print(f"render_camera_motion('侯孝贤') = {render_camera_motion('侯孝贤')}")
    print(f"render_h3_style_opening('电影感', 'medium', 'a rainy Hong Kong alley at midnight')")
    print(f"render_h3_soundscape('Steady rain taps against the windows', 'low room ambience underneath')")
    print(f"render_h3_nondiegetic_music('Sparse piano notes', 'slow', 'sustained low strings')")
    print(f"render_h3_dialogue('(S1)', 'English', 'I get off at the next station.')")
