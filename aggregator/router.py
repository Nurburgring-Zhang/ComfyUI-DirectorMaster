# -*- coding: utf-8 -*-
"""
⑧ DirectorMasterRouter — 视频API路由 (7 模型)
================================================
MiniMax H3 / Seedance 2.5 / Wan 3.0 / Sora 2 / Veo 3 / 短剧平台 / 通用.
接收 Core 核心数据包 → 继承导演风格/场景/AI能力.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy
from aggregator.cinema_craft import build_edit_decision_list, build_video_api_payload, VIDEO_MODELS

TARGETS = ["MiniMax H3 (官方)","Seedance 2.5 (字节)","Wan 3.0 (阿里)","Sora 2 (OpenAI)","Veo 3 (Google)","短剧平台 (抖音/快手/小红书)","通用 (兼容所有模型)"]
VISUAL_STYLES = ["电影感","实拍","2D动画","3D CG","黏土动画","水彩","复古胶片","定格动画","纸艺","拼贴画","纪录片","音乐MV"]
ASPECTS = ["16:9 横屏","9:16 竖屏","1:1 方形","21:9 电影宽屏","4:3 经典","9:16 短剧竖屏"]
EMOTIONS = ["通用","孤独","悲","怒","喜","悬疑","浪漫","史诗","温馨","恐惧","宁静"]
LANGUAGES = ["英语","中文","日语","韩语","法语","西班牙语"]
STORY_THEORIES = ["通用","救猫咪(Save the Cat)","英雄之旅(Hero's Journey)","麦基(McKee)","皮克斯22条(Pixar 22)","起承转合(Kishōtenketsu)","三幕剧","五幕剧","七点结构","特鲁比八序列","丹·哈蒙故事圈","倒叙开场(In Medias Res)","双线并行"]
HOOKS = ["无","视觉冲击","悬念问题","情感冲击","动作冲击","反差冲击"]

MODEL_OPTIMIZERS = {
    "MiniMax H3 (官方)": {"primary_field":"integrated_multimodal_description","audio_fields":["overall_soundscape","non_diegetic_music"],"keyframe_first":True,"supports_ref2va":True,"max_dur":15,"min_dur":4,"langs":["英语","中文"],"shot_notation":"[Shot N] At MM:SS.mmm","dialogue_format":"<d>[Language] ...</d>","best_for":["T2VA","I2VA","FL2VA","L2VA","Ref2VA"]},
    "Seedance 2.5 (字节)": {"primary_field":"prompt","audio_fields":[],"keyframe_first":False,"supports_ref2va":False,"max_dur":12,"min_dur":4,"langs":["英语","中文"],"shot_notation":"natural","best_for":["3D CG","物理一致","多角度"]},
    "Wan 3.0 (阿里)": {"primary_field":"prompt","audio_fields":[],"keyframe_first":False,"supports_ref2va":True,"max_dur":15,"min_dur":3,"langs":["中文","英语"],"best_for":["中文 prompt","简洁动作","美学"]},
    "Sora 2 (OpenAI)": {"primary_field":"prompt","audio_fields":[],"keyframe_first":False,"supports_ref2va":True,"max_dur":20,"min_dur":5,"langs":["英语"],"best_for":["长视频","复杂调度","物理真实"]},
    "Veo 3 (Google)": {"primary_field":"prompt","audio_fields":["ambient_sound"],"keyframe_first":False,"supports_ref2va":True,"max_dur":8,"min_dur":4,"langs":["英语"],"best_for":["4K 高质量","拟真","创意"]},
    "短剧平台 (抖音/快手/小红书)": {"primary_field":"hook + body","audio_fields":["bgm","sound_effect"],"keyframe_first":False,"supports_ref2va":False,"max_dur":30,"min_dur":3,"langs":["中文","英语"],"best_for":["3-7s钩子","1-3镜","强烈情绪","字幕驱动"]},
    "通用 (兼容所有模型)": {"primary_field":"prompt","audio_fields":[],"keyframe_first":False,"supports_ref2va":True,"max_dur":20,"min_dur":3,"langs":["英语","中文"],"best_for":["兼容所有模型"]},
}

# V14.2: H3 深度 IR 转换映射 (修复能力降级 — 此前 Router H3 路径只有 2 字段浅格式,
#        真正的 5 模式检测/keyframe 对齐/Ref2VA 6 段/自检 仅存在于 legacy H3ContextIRNode)
_H3_VISUAL_MAP = {
    "电影感": "Cinematic", "实拍": "live-action", "2D动画": "2D-animated",
    "3D CG": "3D CG", "黏土动画": "claymation", "水彩": "watercolor",
    "复古胶片": "vintage film", "定格动画": "claymation", "纪录片": "live-action",
    "音乐MV": "live-action", "纸艺": "watercolor", "拼贴画": "watercolor",
}
_H3_ASPECT_MAP = {
    "16:9 横屏": "16:9", "9:16 竖屏": "9:16", "1:1 方形": "1:1",
    "21:9 电影宽屏": "21:9", "4:3 经典": "4:3", "9:16 短剧竖屏": "9:16",
}
_H3_LANG_MAP = {
    "英语": "English", "中文": "Chinese", "日语": "Japanese",
    "韩语": "Korean", "法语": "French", "西班牙语": "Spanish",
}


def _h3_deep_convert(scene, director, emotion, intent, dur, aspect, visual,
                     dialogue, lang, music, has_first, has_last, has_refs, ref_desc):
    """调用真实 H3ContextIRNode 引擎做 5 模式 IR 转换. 返回 (prompt_text, ok)."""
    try:
        from h3_context_ir_node import H3ContextIRNode
        node = H3ContextIRNode()
        (h3_mode, instruction, multimodal, soundscape, nondiegetic,
         full_prompt, validation, summary) = node.convert_to_h3(
            user_intent=intent or scene,
            has_first_frame=bool(has_first),
            has_last_frame=bool(has_last),
            has_refs=bool(has_refs),
            reference_assets=ref_desc or "无具体 reference",
            director=director or "通用",
            scene=scene or "",
            duration=max(4, min(15, int(dur))),
            visual_style=_H3_VISUAL_MAP.get(visual, "Cinematic"),
            aspect_ratio=_H3_ASPECT_MAP.get(aspect, "16:9"),
            target_language=_H3_LANG_MAP.get(lang, "English"),
            dialogue=dialogue or "",
            non_diegetic_music=music or "",
            emotion=emotion or "通用",
            intent=intent or "",
        )
        block = (
            f"【MiniMax H3 官方格式 · 深度 IR 转换 (5 模式自动检测)】\n"
            f"{summary}\n"
            f"--- H3 Full Prompt ({h3_mode}) ---\n{full_prompt}\n\n"
            f"--- 字段自检 ---\n{validation}"
        )
        return block, True
    except Exception as e:
        # 诚实降级: 保留浅格式 + 明确标注 (不伪造深度转换成功)
        _soundscape = f"{scene}环境底噪+关键道具细节声" if scene else "环境底噪"
        shallow = (
            f"[DEGRADED] H3 深度 IR 引擎不可用 ({e}), 降级为浅格式\n"
            f"integrated_multimodal_description:\n"
            f"[Shot 1] At 00:00.000: {scene}, {visual}风格, {emotion}情绪, {aspect}.\n\n"
            f"overall_soundscape: {_soundscape}\n"
        )
        return shallow, False


class DirectorMasterRouter(DirectorNodeBase):
    """视频API路由 — 7 模型兼容. 接收核心数据包继承导演/AI能力."""
    NODE_TYPE = "画面"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        _R = "🎲 随机"
        return {"required": {
            "用户意图": ("STRING", {"default": "父女厨房雨夜, 霓虹灯在雨水中反射", "multiline": True,
                "tooltip": "用户原始意图(可空, 空时从核心数据包继承场景描述)"}),
            "目标模型": (TARGETS+[_R], {"default": "通用 (兼容所有模型)"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 自动获取导演/场景/情绪/AI配置 (AI自动继承)"}),
            "统一电影提示词": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.统一电影提示词 — 完整导演意图作为内容基础"}),
            "剧本输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Script.剧本 — 作为视频生成的内容基础(优先级最高)"}),
            "分镜输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Cinematic.分镜 或 Summary.分镜脚本 — 视频生成内容基础"}),
            "视觉风格": ([_R]+VISUAL_STYLES, {"default": "电影感"}),
            "对白": ("STRING", {"default": "", "multiline": True}),
            "对白语言": ([_R]+LANGUAGES, {"default": "英语"}),
            "非画内音乐": ("STRING", {"default": "", "multiline": True}),
            "时长秒": ("INT", {"default": 8, "min": 3, "max": 20, "step": 1}),
            "画幅比例": ([_R]+ASPECTS, {"default": "16:9 横屏"}),
            "故事理论": ([_R]+STORY_THEORIES, {"default": "通用"}),
            "钩子风格": ([_R]+HOOKS, {"default": "无"}),
            "需要字幕": ("BOOLEAN", {"default": False}),
            "有首帧": ("BOOLEAN", {"default": False}),
            "有尾帧": ("BOOLEAN", {"default": False}),
            "有参考素材": ("BOOLEAN", {"default": False,
                "tooltip": "V14.2: H3 Ref2VA 全参考模式开关 (有完整 reference 图/视频/音频)"}),
            "参考素材描述": ("STRING", {"default": "", "multiline": True,
                "tooltip": "V14.2: 参考素材描述 — H3 Ref2VA 模式的 subject_definitions 来源"}),
        }}

    RETURN_TYPES = ("STRING","STRING","STRING")
    RETURN_NAMES = ("模型专属提示词","视频生成请求","剪辑决策表EDL")
    FUNCTION = "convert_universal"
    CATEGORY = "PromptLibrary/起点/通用"

    def convert_universal(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包",""))
        intent = kwargs.get("用户意图","")
        target = kwargs.get("目标模型","通用 (兼容所有模型)")
        # V16.0 需求1: 目标模型与属性下拉支持 🎲 随机
        import random as _r
        def _rnd(v, opts):
            if v == "🎲 随机":
                return _r.choice([o for o in opts if o != "🎲 随机"])
            return v
        if target == "🎲 随机":
            target = _r.choice(TARGETS)
        if target not in TARGETS: target = "通用 (兼容所有模型)"
        kwargs["视觉风格"] = _rnd(kwargs.get("视觉风格","电影感"), VISUAL_STYLES)
        kwargs["对白语言"] = _rnd(kwargs.get("对白语言","英语"), LANGUAGES)
        kwargs["画幅比例"] = _rnd(kwargs.get("画幅比例","16:9 横屏"), ASPECTS)
        kwargs["故事理论"] = _rnd(kwargs.get("故事理论","通用"), STORY_THEORIES)
        kwargs["钩子风格"] = _rnd(kwargs.get("钩子风格","无"), HOOKS)
        # 优先核心数据包, fallback widget
        scene = core.get("_场景描述") or kwargs.get("场景描述") or intent
        emotion = core.get("_情绪基调") or kwargs.get("情绪","通用")
        dur = kwargs.get("时长秒",8)
        aspect = kwargs.get("画幅比例","16:9 横屏")
        dialogue = kwargs.get("对白","")
        lang = kwargs.get("对白语言","英语")
        music = kwargs.get("非画内音乐","")
        visual = kwargs.get("视觉风格","电影感")
        hook = kwargs.get("钩子风格","无")
        sub = kwargs.get("需要字幕",False)
        story_theory = kwargs.get("故事理论","通用")
        has_first = kwargs.get("有首帧",False)
        has_last = kwargs.get("有尾帧",False)
        # V13.4: 接线此前声明未用的上游内容输入
        unified_prompt = kwargs.get("统一电影提示词","")
        script_in = kwargs.get("剧本输入","")
        # 导演锚点从核心数据包继承
        director = core.get("_导演风格") or "王家卫"
        # 管线接入: 分镜输入 (Final.分镜脚本 或 Cinematic.分镜)
        storyboard_in = kwargs.get("分镜输入","")

        opt = MODEL_OPTIMIZERS.get(target, MODEL_OPTIMIZERS["通用 (兼容所有模型)"])
        primary = opt.get("primary_field","prompt")

        # 模型专属提示词
        if target == "MiniMax H3 (官方)":
            # V14.2: 深度 IR 转换 — 真实 H3ContextIRNode 引擎 (5 模式自动检测:
            #        T2VA/I2VA/FL2VA/L2VA/Ref2VA + keyframe 对齐 + 3 大字段 + Ref2VA 6 段 + 自检)
            model_prompt, _h3_ok = _h3_deep_convert(
                scene, director, emotion, intent, dur, aspect, visual,
                dialogue, lang, music,
                has_first, has_last,
                kwargs.get("有参考素材", False), (kwargs.get("参考素材描述", "") or "").strip(),
            )
        elif target == "Seedance 2.5 (字节)":
            model_prompt = f"3D CG, physics-consistent, multi-angle: {scene}, {visual}风格, {emotion}情绪, {dur}s."
        elif target == "Wan 3.0 (阿里)":
            model_prompt = f"中文提示词, 简洁动作, 强美学: {scene}, {visual}, {emotion}, {dur}s."
        elif target == "Sora 2 (OpenAI)":
            model_prompt = f"Long-form, complex staging, physics-realistic: {scene}, {visual}风格, {emotion}情绪, {dur}s, {aspect}."
        elif target == "Veo 3 (Google)":
            model_prompt = f"High-fidelity 4K, creative, physics-true: {scene}, {visual}风格, {emotion}情绪, {dur}s."
        elif target == "短剧平台 (抖音/快手/小红书)":
            model_prompt = f"3-7s hook, 1-3 shots, strong emotion, subtitle-driven: {scene}, {emotion}, {dur}s, {aspect}."
        else:
            model_prompt = f"Universal: {scene}, {visual}风格, {emotion}情绪, {dur}s, {aspect}."

        # 管线接入: 分镜输入作为视频生成内容基础 (来自 Final.分镜脚本 / Cinematic.分镜)
        if storyboard_in:
            model_prompt = f"【分镜内容基础(来自管线)】\n{storyboard_in[:3000]}\n\n【模型格式化要求】\n{model_prompt}"

        # V13.4: 上游内容输入接线 — 剧本优先级最高, 其次统一电影提示词
        if script_in:
            model_prompt = f"【剧本内容基础(优先级最高)】\n{script_in[:3000]}\n\n{model_prompt}"
        elif unified_prompt:
            model_prompt = f"【统一电影提示词(导演意图)】\n{unified_prompt[:2000]}\n\n{model_prompt}"

        # V13.4: 生成指令增强 — 消费 对白/语言/音乐/钩子/字幕/故事理论/首尾帧
        _directives = []
        if dialogue:
            _directives.append(f"对白: {dialogue[:300]} (语言: {lang})")
        if music:
            _directives.append(f"非画内音乐: {music[:200]}")
        if hook and hook != "无":
            _directives.append(f"钩子风格: {hook} (前3秒抓人)")
        if sub:
            _directives.append("需要字幕: 是 (台词驱动, 字幕清晰)")
        if story_theory and story_theory != "通用":
            _directives.append(f"故事理论: {story_theory}")
        if has_first:
            _directives.append("首帧: 已提供 (图生视频 first_frame 锚定)")
        if has_last:
            _directives.append("尾帧: 已提供 (图生视频 last_frame 锚定)")
        if _directives:
            model_prompt += "\n\n【生成指令增强】\n" + "\n".join("  - " + d for d in _directives)

        # V14.3-MERGED: CINEDANCE 15 块刚性视觉骨架 (style_prefix_data 复活接线)
        try:
            from style_prefix_data import render_style_prefix
            _skel = render_style_prefix()
            if _skel:
                model_prompt = model_prompt + "\n\n【CINEDANCE 15 块视觉骨架】\n" + str(_skel)
        except Exception as _sp_e:
            import sys as _sp_s
            _sp_s.stderr.write(f"[DirectorMaster] CINEDANCE骨架注入降级: {type(_sp_e).__name__}\n")

        # AI 增强模型专属提示词 (继承Core AI能力)
        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url:
            model_prompt = self._ensure_ai_output(model_prompt,
                {"node_type":"画面","mode":"视频API路由","director":director,"scene":scene,"mood":emotion,"intent":intent},
                api_url, api_key, ai_model)

        # 模型名 → cinema_craft 模型键
        target_to_key = {"MiniMax H3 (官方)":"h3","Seedance 2.5 (字节)":"seedance2.5","Wan 3.0 (阿里)":"wan3.0",
                         "Sora 2 (OpenAI)":"sora2","Veo 3 (Google)":"veo3","短剧平台 (抖音/快手/小红书)":"kling",
                         "通用 (兼容所有模型)":"seedance2.5"}
        model_key = target_to_key.get(target, "seedance2.5")
        # 兼容 flux3 / ltx2.5 (用户可在目标模型选通用, 这里自动选最接近)
        if model_key not in VIDEO_MODELS:
            model_key = "seedance2.5"

        # 剪辑决策表 EDL (agent 可识别标准 JSON)
        edl = build_edit_decision_list(scene, director, emotion, total_dur=max(3, dur), shots=6)

        # 视频生成请求 payload (可直接 POST 到视频API / 交下游ComfyUI视频节点)
        payload = build_video_api_payload(model_key, model_prompt, scene,
                                           aspect=aspect, duration=max(3, dur), fps=24, edl=edl)
        payload_json = _json.dumps(payload, ensure_ascii=False, indent=2)
        edl_json = _json.dumps(edl, ensure_ascii=False, indent=2)

        return (model_prompt, payload_json, edl_json)