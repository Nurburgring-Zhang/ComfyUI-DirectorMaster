# -*- coding: utf-8 -*-
"""
⑤ DirectorMasterSound — 声音音乐 (4 合 1)
==========================================
声音设计/音乐配乐/声音层/沉默.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy

SOUND_MODES = ["声音设计","音乐配乐","声音层","沉默"]

def _parse_scene_safe(scene):
    try:
        from aggregator.scene_engine import parse_scene
        return parse_scene(scene) if scene else {}
    except Exception:
        return {}


def _detect_era_safe(scene):
    try:
        from aggregator.feature_film_engine import _detect_era
        return _detect_era(scene or "")
    except Exception:
        return "现代"


def _build_sound_template(scene, director, mood, core):
    """4层声景 — V13.3 场景驱动 + 年代适配."""
    p = _parse_scene_safe(scene)
    loc = p.get("location") or "场景"
    objs = p.get("objects") or ["关键道具"]
    chars = p.get("characters") or ["主角"]
    weather = p.get("weather") or "环境"
    era = _detect_era_safe(scene)
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else chars[0]
    obj = objs[0]
    # 年代环境层
    ambient = {
        "古装": f"风声: 穿过{loc}, 持续, 低频包裹\n  远处更鼓/市声: 时断时续, 年代感\n  烛火/炭火: 微弱噼啪, 近景",
        "科幻": f"舱体嗡鸣: 低频恒稳, 包裹感\n  循环气流: 中景, 持续\n  提示音: 偶尔, 远景点缀",
        "复古": f"{weather}声: 中景, 持续\n  老物件声(钟摆/收音机): 时断时续, 年代感\n  街道远处: 偶尔, 低频",
        "现代": f"{weather}声: 中景, 持续\n  环境底噪: 恒稳, 低频\n  远处生活声: 偶尔, 点缀",
    }.get(era, f"{weather}声: 中景, 持续\n  环境底噪: 恒稳\n  远处生活声: 偶尔")
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【SoundDesignPro】4-Layer Soundscape | 导演: {director}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"【Layer 1: 环境层 (Ambient)】\n  {ambient}\n\n"
        f"【Layer 2: 拟音层 (Foley)】\n"
        f"  {obj}被触碰: 近景, 材质按{era}年代真实, 尾音清晰\n"
        f"  衣物/脚步: 中景, {c1}的动作声, 软而真实\n"
        f"  {objs[1] if len(objs)>1 else obj}的细节声: 近景, 1-2次, 情绪点\n\n"
        f"【Layer 3: 心声层 (Inner Voice)】\n"
        f"  {c1}心声: 近景, 只在呼吸节奏中暗示, 不发声\n"
        f"  {c2}心声: 近景, 只在眼神变化时暗示, 用眨眼/呼吸表达\n\n"
        f"【Layer 4: 沉默层 (Silence)】\n"
        f"  位置: 关键情感点前, {c1}开口前\n"
        f"  力度: 从环境声渐进到完全静默, 呼吸声替代所有声音\n"
        f"  情绪功能: 创造'{mood}'的听觉留白"
    )

def _build_music_template(scene, director, mood, core):
    """音乐配乐 — V13.3 场景驱动 (按情绪/年代选风格)."""
    core = core or {}
    era = _detect_era_safe(scene)
    p = _parse_scene_safe(scene)
    objs = p.get("objects") or ["关键道具"]
    obj = objs[0]
    # 情绪→音乐风格
    style_map = {
        "孤独": "极简钢琴+弦乐拨弦, 无鼓机",
        "温暖": "原声吉他+轻弦乐, 温暖中低频",
        "悲伤": "大提琴独奏+钢琴单音, 缓慢",
        "悬疑": "低音弦乐+不规则打击, 张力",
        "史诗": "管弦乐+民族打击, 宏大",
        "宁静": "氛围音乐+长音, 极简",
        "喜剧": "轻快拨弦+木管, 灵动",
        "浪漫": "弦乐+钢琴, 柔和",
    }
    style = style_map.get(mood, "极简配乐, 克制")
    era_note = {"古装": "可加入民族乐器(古琴/笛/鼓)点缀", "科幻": "可用合成器低频铺底, 克制"}.get(era, "")
    return (
        f"【音乐配乐】导演: {director}\n\n"
        f"风格: {style}\n"
        f"情感曲线: 递进 — 从单音到双音, 高潮后回到单音.\n"
        f"节拍BPM: 按情绪({mood})定, 与场景动作节奏同步.\n"
        f"时代适配: {era}——{era_note}\n"
        f"留白点: {obj}出现时静音0.5-1s, 关键情感点前抽配乐.\n"
        f"原则: 音乐不抢戏, 情绪到位即收."
    )

def _build_sound_layer_template(scene, director, mood, core):
    """声音层 — V13.3 场景驱动."""
    p = _parse_scene_safe(scene)
    chars = p.get("characters") or ["主角"]
    objs = p.get("objects") or ["关键道具"]
    loc = p.get("location") or "场景"
    weather = p.get("weather") or "环境"
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else chars[0]
    return (
        f"【声音层】导演: {director}\n\n"
        f"说话角色: {c1}(声音频率/语速按角色前史定, 停顿多)\n"
        f"沉默角色: {c2}(非语言: 呼吸/眨眼/动作声)\n"
        f"空气层: {weather}声(持续, 中景, 包裹感)\n"
        f"脚步层: 按{loc}地面材质定\n"
        f"环境动作层: {'、'.join(objs[:3])} 各自的材质声\n"
        f"远景层: {loc}的远处声, 偶尔, 低频\n"
        f"画幅: 按核心数据包"
    )

def _build_silence_template(scene, director, mood, core):
    """沉默 — V13.3 场景驱动."""
    p = _parse_scene_safe(scene)
    chars = p.get("characters") or ["主角"]
    objs = p.get("objects") or ["关键道具"]
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else chars[0]
    obj = objs[0]
    return (
        f"【沉默】导演: {director}\n\n"
        f"场景类型: 对话极少, 沉默是主角\n"
        f"沉默总时长: 按场戏节奏, 关键情感点前必留\n"
        f"每句对白前停顿: 0.5s — 呼吸, 眼睛看别处, 然后开口\n"
        f"对白间沉默占比: 0.4 — 用动作声({obj})填充\n"
        f"动作后停顿占比: 0.3 — 动作停了, 然后才是下一句\n"
        f"眼神对视占比: 0.3 — {c1}看{c2}, {c2}看别处\n"
        f"空镜留白占比: 0.2 — {obj}与空间\n"
        f"导演风格: {director} — 留白即叙事, 沉默即对白"
    )

TEMPLATES = {"声音设计": _build_sound_template, "音乐配乐": _build_music_template, "声音层": _build_sound_layer_template, "沉默": _build_silence_template}


class DirectorMasterSound(DirectorNodeBase):
    """声音音乐聚合节点 — 4 合 1."""
    NODE_TYPE = "声音设计"

    @classmethod
    def INPUT_TYPES(cls):
        _ND = "无(默认)"
        _R = "🎲 随机"
        return {"required": {
            "声音模式": (SOUND_MODES, {"default": "声音设计"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "从核心数据包继承, 此处可单独覆盖"}),
            "声音风格": ([_ND,_R,"写实","极简","丰富","电子","民族","环境氛围",
                          "ASMR","Lo-Fi低保真","Hifi高保真","杜比全景声","单声道","默片",
                          "黑胶质感","磁带质感","数字化未来","管风琴","交响乐","爵士"],
                         {"default": _ND,
                "tooltip": "声音整体风格 → 真实影响4层声音设计的质感方向 (22+ 选项)"}),
            "音乐风格": ([_ND,_R,"极简钢琴","弦乐","电子","民族","打击乐","无配乐",
                          "古典交响","巴洛克","新世纪","氛围音乐","新古典","印象派",
                          "Lo-Fi Hip-Hop","Trap","Future Bass","Ambient Drone","凯尔特",
                          "中东","印度西塔琴","非洲鼓乐","中国古乐","禅意佛乐","游戏BGM","恐怖配乐"],
                         {"default": _ND,
                "tooltip": "配乐风格 → 真实影响音乐层 (26+ 选项)"}),
            "混响空间": ([_ND,_R,"干(无混响)","小混响","中混响","大混响","室外开阔",
                          "教堂混响","森林混响","水下混响","隧道混响","房间","大厅",
                          "洞穴","浴室","老房子木地板","金属工业空间","回声沙漠"],
                         {"default": _ND,
                "tooltip": "空间混响 → 真实影响声音距离感/包裹感 (18+ 选项)"}),
            "声音密度": ([_ND,_R,"稀疏","适中","密集","极密",
                          "呼吸可闻","针落有声","交响乐级","白噪音级","极静"],
                         {"default": _ND,
                "tooltip": "声音元素密度 → 真实影响声音层丰富度 (10+ 选项)"}),
            "留白比例": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1, "display": "slider",
                "tooltip": "沉默/留白占比 → 真实影响沉默层时长"}),
        }, "optional": {
            "音乐风格_多选": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ V13.2 多选: 多种配乐风格随叙事演变, 用 逗号/箭头 分隔。例: '极简钢琴→古典交响→氛围音乐'。优先于上方单选音乐风格"}),
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承场景/导演/情绪/灵魂/AI"}),
        }}

    def build(self, **kwargs):
        from aggregator.node_base import resolve_dropdown
        _SND_OPTS = ["写实","极简","丰富","电子","民族","环境氛围",
                       "ASMR","Lo-Fi低保真","Hifi高保真","杜比全景声","单声道","默片",
                       "黑胶质感","磁带质感","数字化未来","管风琴","交响乐","爵士"]
        _MUS_OPTS = ["极简钢琴","弦乐","电子","民族","打击乐","无配乐",
                       "古典交响","巴洛克","新世纪","氛围音乐","新古典","印象派",
                       "Lo-Fi Hip-Hop","Trap","Future Bass","Ambient Drone","凯尔特",
                       "中东","印度西塔琴","非洲鼓乐","中国古乐","禅意佛乐","游戏BGM","恐怖配乐"]
        _REV_OPTS = ["干(无混响)","小混响","中混响","大混响","室外开阔",
                       "教堂混响","森林混响","水下混响","隧道混响","房间","大厅",
                       "洞穴","浴室","老房子木地板","金属工业空间","回声沙漠"]
        _DEN_OPTS = ["稀疏","适中","密集","极密",
                       "呼吸可闻","针落有声","交响乐级","白噪音级","极静"]
        kwargs["声音风格"] = resolve_dropdown(kwargs.get("声音风格"), "写实", _SND_OPTS)
        kwargs["音乐风格"] = resolve_dropdown(kwargs.get("音乐风格"), "极简钢琴", _MUS_OPTS)
        kwargs["混响空间"] = resolve_dropdown(kwargs.get("混响空间"), "中混响", _REV_OPTS)
        kwargs["声音密度"] = resolve_dropdown(kwargs.get("声音密度"), "适中", _DEN_OPTS)
        # V13.2: 音乐多选演变 — 首值为主配乐, 全弧传给 _do_build 生成配乐演变块
        from aggregator.node_base import parse_multi_select
        music_arc = parse_multi_select(kwargs.get("音乐风格_多选", ""))
        if music_arc:
            kwargs["音乐风格"] = music_arc[0]
        kwargs["_music_arc"] = music_arc
        return self._do_build(**kwargs)

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("声音",)
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/声音"

    def _do_build(self, **kwargs):
        mode = kwargs.get("声音模式","声音设计")
        if mode not in SOUND_MODES: mode = "声音设计"
        core = parse_core_pack(kwargs.get("核心数据包",""))
        scene = core.get("_场景描述") or kwargs.get("场景描述","")
        director = core.get("_导演风格") or kwargs.get("导演风格","王家卫")
        mood = core.get("_情绪基调","孤独")

        builder = TEMPLATES.get(mode, _build_sound_template)
        main = builder(scene, director, mood, core)
        main += self._director_block(director)
        from aggregator.dimensions import apply_dimensions
        main += "\n\n" + apply_dimensions("声音", kwargs)

        # V13.2: 配乐演变弧 (多选) — 按叙事阶段分配配乐风格
        music_arc = kwargs.get("_music_arc") or []
        if len(music_arc) > 1:
            _stage_names = ["建置(开场)", "上升(对抗)", "高潮(顶点)", "解决(结尾)"]
            _lines = ["", "【配乐演变弧 (V13.2 多选)】配乐随情节推进演变:"]
            n = len(music_arc)
            for i, mv in enumerate(music_arc):
                stage = _stage_names[int(i / max(n - 1, 1) * (len(_stage_names) - 1) + 0.5)] if n <= 4 else f"阶段{i+1}/{n}"
                _lines.append(f"  {stage}: {mv}")
            _lines.append("  过渡: 主题动机(motif)贯穿, 变奏切换风格; 高潮前 1-2 场先抽配乐只留环境音, 顶点再全奏进入")
            main += "\n".join(_lines)

        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url:
            main = self._ensure_ai_output(main,
                {"node_type":"声音设计","mode":mode,"director":director,"scene":scene,"mood":mood,"intent":core.get("_导演意图_观众应感到","") if core else ""},
                api_url, api_key, ai_model)

        from aggregator.pro_format import strip_decor
        # V14.2: 启用反AI规则 真实生效 (此前声明未消费)
        return (self._apply_anti_ai(strip_decor(main), kwargs, core),)