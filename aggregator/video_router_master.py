# -*- coding: utf-8 -*-
"""
V12.6 DirectorMasterVideoRouter — 5 视频模型超级路由
=====================================================
V9.5 DirectorMasterRouter 是单目标模型 (一次生成 1 个模型 prompt + API 请求 + EDL).
V12.6 VideoRouter 一次同时输出 5 路: Seedance 2.5 / LTX-2.5 / Wan 2.6 / Hailuo 2.3 / Sora 2.

每个模型有自己的 prompt 优化策略:
  - Seedance 2.5: 中文友好, 物理一致, 3D CG 强项
  - LTX-2.5:       强项多角度/多镜头拼接
  - Wan 2.6:       阿里, 中文 prompt, 美学/简洁动作
  - Hailuo 2.3:    中文优化, 短剧向, 8s 标准
  - Sora 2:        OpenAI, 物理真实/复杂调度/长视频

接 Core.核心数据包 (forceInput) → 继承导演/场景/情绪/AI 配置.
接 Cinematic.分镜 或 Summary.分镜脚本 (forceInput) → 内容基础.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config
from aggregator.cinema_craft import VIDEO_MODELS, build_video_api_payload, build_video_api_text
from aggregator.ref_media import resolve_ref, image_batch_to_ref_paths


VIDEO_ROUTER_MODES = ["Seedance 2.5", "LTX-2.5", "Wan 2.6", "Hailuo 2.3", "Sora 2"]


class DirectorMasterVideoRouter(DirectorNodeBase):
    """V12.6 5 视频模型超级路由 — 一次输出 5 路, 适配不同 API 平台."""
    NODE_TYPE = "视频路由"

    @classmethod
    def INPUT_TYPES(cls):
        _R = "🎲 随机"
        return {"required": {
            "目标视频模型": (["全部生成"] + VIDEO_ROUTER_MODES + [_R], {"default": "全部生成"}),
            "视频时长_秒": ("INT", {"default": 8, "min": 3, "max": 30, "step": 1}),
            "画幅比例": ([_R, "16:9 横屏", "9:16 竖屏", "1:1 方形", "21:9 电影宽屏"], {"default": "16:9 横屏"}),
            "帧率": ("INT", {"default": 24, "min": 12, "max": 60, "step": 1}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承导演/场景/情绪/灵魂/AI (AI自动从核心数据包继承, 无需重复填)"}),
            "统一电影提示词": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.统一电影提示词 — 完整导演意图"}),
            "剧本输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Script.剧本 — 视频内容基础(优先级最高)"}),
            "分镜脚本": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Cinematic.分镜 或 Summary.分镜脚本 — 视频生成内容基础"}),
            # V12.6 v6: 多图多视频参考全链路
            "参考库JSON": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 接 Asset.参考库JSON — 多图多视频参考库 (角色正面/侧面/背面/环境母版/道具母版/首帧/尾帧/运动母版/风格母版), 一次性传递给 5 视频模型"}),
            "首帧图片": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "[兼容] 接 LoadImage 输出 — 图生视频首帧"}),
            "尾帧图片": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "[兼容] 接 LoadImage 输出 — 视频尾帧锚定"}),
            "角色正面参考": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色正面参考 (IP-Adapter 锁定)"}),
            "角色侧面参考": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色侧面参考"}),
            "角色背面参考": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色背面参考"}),
            "环境母版参考": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 环境母版"}),
            "道具母版参考": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 道具母版"}),
            "运动母版视频": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadVideo 输出 — 运动母版 (锁定运镜/节奏)"}),
            "风格母版视频": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadVideo 输出 — 风格母版 (锁定视觉风格)"}),
            # V13 合并: IMAGE 类型输入槽 (ComfyUI 标准) — 直接接 LoadImage/LoadVideo 的 IMAGE 输出
            "首帧_IMAGE": ("IMAGE", {"tooltip": "★ ComfyUI 标准: 接 LoadImage 的 IMAGE 输出 — 图生视频首帧"}),
            "尾帧_IMAGE": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 — 视频尾帧锚定"}),
            "角色正面_IMAGE": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 — 角色正面 (IP-Adapter)"}),
            "环境母版_IMAGE": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 — 环境母版"}),
            "运动母版_IMAGE": ("IMAGE", {"tooltip": "接 LoadVideo/VHS 的 IMAGE 批次 — 运动母版 (多帧)"}),
            "负向提示词": ("STRING", {"default": "模糊, 变形, 多余手指, 文字水印, 低质量", "multiline": True}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("Seedance 2.5", "LTX-2.5", "Wan 2.6", "Hailuo 2.3", "Sora 2", "视频元数据", "综合API请求JSON")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/视频路由"
    OUTPUT_NODE = True

    def build(self, **kwargs):
        target = kwargs.get("目标视频模型", "全部生成")
        # V16.0 需求1: 目标视频模型与画幅支持 🎲 随机
        import random as _r
        if target == "🎲 随机":
            target = _r.choice(VIDEO_ROUTER_MODES)
        aspect = kwargs.get("画幅比例", "16:9 横屏")
        if aspect == "🎲 随机":
            aspect = _r.choice(["16:9 横屏", "9:16 竖屏", "1:1 方形", "21:9 电影宽屏"])
        duration = kwargs.get("视频时长_秒", 8)
        fps = kwargs.get("帧率", 24)

        # 解析 forceInput
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        director = core.get("_导演风格", "王家卫") if core else "王家卫"
        scene = core.get("_场景描述", "") if core else ""
        mood = core.get("_情绪基调", "") if core else ""
        unified_prompt = kwargs.get("统一电影提示词", "")
        storyboard = kwargs.get("分镜脚本", "")
        script_in = kwargs.get("剧本输入", "")  # V13.3: 接线此前声明未用的 剧本输入
        negative = kwargs.get("负向提示词", "")

        # V12.6 v6: 解析参考库 JSON (Asset 节点的 参考库JSON 输出)
        ref_library_str = kwargs.get("参考库JSON", "")
        ref_library = {"参考图": {}, "参考视频": {}, "统计": {"参考图总数": 0, "参考视频总数": 0}}
        if ref_library_str.strip():
            try:
                ref_library = _json.loads(ref_library_str)
            except Exception:
                pass
        # 也接收独立的 forceInput (兼容直接连接 LoadImage/LoadVideo)
        standalone_refs = {
            "角色正面": resolve_ref(kwargs, "角色正面_IMAGE", "角色正面参考", "角色正面"),
            "角色侧面": kwargs.get("角色侧面参考", "").strip(),
            "角色背面": kwargs.get("角色背面参考", "").strip(),
            "环境母版": resolve_ref(kwargs, "环境母版_IMAGE", "环境母版参考", "环境母版"),
            "道具母版": kwargs.get("道具母版参考", "").strip(),
            "首帧": resolve_ref(kwargs, "首帧_IMAGE", "首帧图片", "首帧"),
            "尾帧": resolve_ref(kwargs, "尾帧_IMAGE", "尾帧图片", "尾帧"),
        }
        standalone_videos = {}
        _mv = kwargs.get("运动母版_IMAGE")
        if _mv is not None:
            _fr = image_batch_to_ref_paths(_mv, "运动母版")
            standalone_videos["运动母版"] = ",".join(_fr) if _fr else ""
        if not standalone_videos.get("运动母版"):
            standalone_videos["运动母版"] = kwargs.get("运动母版视频", "").strip()
        standalone_videos["风格母版"] = kwargs.get("风格母版视频", "").strip()
        # 合并: 独立 forceInput 优先覆盖参考库
        for k, v in standalone_refs.items():
            if v: ref_library.setdefault("参考图", {})[k] = v
        for k, v in standalone_videos.items():
            if v: ref_library.setdefault("参考视频", {})[k] = v
        # 重新计算统计
        ref_library.setdefault("统计", {})
        ref_library["统计"]["参考图总数"] = sum(1 for v in ref_library.get("参考图", {}).values() if v)
        ref_library["统计"]["参考视频总数"] = sum(1 for v in ref_library.get("参考视频", {}).values() if v)

        # V16.0 需求4: AIGC 生产模式自动判别 (基于首帧/尾帧/参考图/参考视频)
        try:
            from aggregator.aigc_adapter import detect_production_mode, get_mode_guidance
            _has_first = bool(ref_library.get("参考图", {}).get("首帧"))
            _has_last = bool(ref_library.get("参考图", {}).get("尾帧"))
            _ref_img_count = sum(1 for k, v in ref_library.get("参考图", {}).items()
                                 if v and k not in ("首帧", "尾帧"))
            _has_ref_video = ref_library["统计"]["参考视频总数"] > 0
            _prod_mode, _prod_basis = detect_production_mode(
                has_first=_has_first, has_last=_has_last,
                has_ref_images=_ref_img_count > 0, has_ref_video=_has_ref_video,
                ref_image_count=_ref_img_count)
        except Exception as _pm_e:
            import sys as _pm_s
            _pm_s.stderr.write(f"[DirectorMaster] AIGC生产模式判别降级: {type(_pm_e).__name__}\n")
            _prod_mode, _prod_basis = "文生视频", "降级"

        # 内容基础 (V13.3: 加入剧本输入优先级)
        if storyboard:
            content = storyboard
        elif script_in:
            content = script_in
        elif unified_prompt:
            content = unified_prompt
        else:
            content = scene or "(未提供内容)"

        if target == "全部生成":
            targets = VIDEO_ROUTER_MODES
        elif target in VIDEO_ROUTER_MODES:
            targets = [target]
        else:
            targets = VIDEO_ROUTER_MODES

        # 模型特定 prompt 优化 (整合参考库)
        results = {}
        for model in VIDEO_ROUTER_MODES:
            if model in targets:
                results[model] = self._optimize_for_model(model, content, director, scene, mood, aspect, duration, ref_library)
            else:
                results[model] = f"(未生成 — 目标为 {target})"

        # V14.3-MERGED: Seedance 2.5 能力边界 (master_director_data 复活接线)
        _seed_caps = {}
        try:
            from master_director_data import SEEDANCE_25_CAPABILITIES
            _cu = SEEDANCE_25_CAPABILITIES.get("core_upgrades", {}) if isinstance(SEEDANCE_25_CAPABILITIES, dict) else {}
            _seed_caps = {
                "版本": SEEDANCE_25_CAPABILITIES.get("version", ""),
                "单镜最大秒": _cu.get("max_duration_single_shot"),
                "延展最大秒": _cu.get("max_duration_extended"),
                "最大参考资产数": _cu.get("max_reference_assets"),
                "图参考上限": _cu.get("image_refs"),
                "视频参考上限": _cu.get("video_refs"),
            }
        except Exception as _sc_e:
            import sys as _sc_s
            _sc_s.stderr.write(f"[DirectorMaster] Seedance能力边界降级: {type(_sc_e).__name__}\n")

        meta = _json.dumps({
            "目标模型": target,
            "AIGC生产模式": _prod_mode,
            "AIGC判别依据": _prod_basis,
            "Seedance能力边界": _seed_caps,
            "时长秒": duration,
            "画幅": aspect,
            "帧率": fps,
            "导演": director,
            "场景": scene[:100],
            "情绪": mood,
            "已生成模型": targets,
            "首帧": bool(kwargs.get("首帧图片", "").strip()),
            "尾帧": bool(kwargs.get("尾帧图片", "").strip()),
            "参考库统计": ref_library["统计"],
            "参考图清单": list(ref_library.get("参考图", {}).keys()),
            "参考视频清单": list(ref_library.get("参考视频", {}).keys()),
        }, ensure_ascii=False, indent=2)

        return (results["Seedance 2.5"], results["LTX-2.5"], results["Wan 2.6"],
                results["Hailuo 2.3"], results["Sora 2"], meta,
                self._build_api_requests_json(results, meta, target, duration, aspect, fps, director, scene, ref_library, negative))

    def _build_api_requests_json(self, results, meta_str, target, duration, aspect, fps, director, scene, ref_library, negative):
        """V12.6 v7: 构建 5 视频模型完整 API 请求 JSON (一键提交给视频 API)."""
        api_requests = {
            "_meta": _json.loads(meta_str) if isinstance(meta_str, str) else meta_str,
            "Seedance 2.5": {
                "endpoint": "POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
                "model": "doubao-seedance-2-5",
                "body": {
                    "prompt": results.get("Seedance 2.5", ""),
                    "ratio": aspect.split(" ")[0],
                    "duration": duration,
                    "fps": fps,
                    "reference_images": [v for v in ref_library.get("参考图", {}).values() if v],
                    "negative_prompt": negative,
                }
            },
            "LTX-2.5": {
                "endpoint": "POST https://api.ltx.video/v1/generate",
                "model": "ltx-2.5",
                "body": {
                    "prompt": results.get("LTX-2.5", ""),
                    "aspect_ratio": aspect.split(" ")[0],
                    "num_frames": duration * fps,
                    "reference_videos": [v for v in ref_library.get("参考视频", {}).values() if v],
                }
            },
            "Wan 2.6": {
                "endpoint": "POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis",
                "model": "wan2.6-t2v",
                "body": {
                    "input": {"prompt": results.get("Wan 2.6", "")},
                    "parameters": {"duration": duration, "ratio": aspect.split(" ")[0], "fps": fps}
                }
            },
            "Hailuo 2.3": {
                "endpoint": "POST https://api.hailuoai.video/v1/video/generate",
                "model": "MiniMax-hailuo-2.3",
                "body": {
                    "prompt": results.get("Hailuo 2.3", ""),
                    "duration": duration,
                    "aspect_ratio": aspect.split(" ")[0],
                    "first_frame_image": ref_library.get("参考图", {}).get("首帧", ""),
                    "last_frame_image": ref_library.get("参考图", {}).get("尾帧", ""),
                }
            },
            "Sora 2": {
                "endpoint": "POST https://api.openai.com/v1/videos",
                "model": "sora-2",
                "body": {
                    "prompt": results.get("Sora 2", ""),
                    "size": aspect.split(" ")[0],
                    "seconds": str(duration),
                    "input_reference": ref_library.get("参考图", {}).get("首帧", ""),
                }
            },
        }
        return _json.dumps(api_requests, ensure_ascii=False, indent=2)

    def _optimize_for_model(self, model, content, director, scene, mood, aspect, duration, ref_library):
        """每个视频模型的 prompt 优化策略 (V12.6 v6 整合多图多视频参考库)."""
        base_scene = f"{scene} | 导演: {director} | 情绪: {mood} | 画幅: {aspect} | 时长: {duration}s"
        content_preview = content[:800] if content else scene

        # V12.6 v6: 构建参考库块
        ref_block = ""
        ref_imgs = ref_library.get("参考图", {})
        ref_vids = ref_library.get("参考视频", {})
        if ref_imgs or ref_vids:
            ref_block = f"\n【多图多视频参考库 (V12.6 v6 一次性传递)】\n"
            if ref_imgs:
                ref_block += f"  参考图 ({ref_library.get('统计', {}).get('参考图总数', 0)} 张):\n"
                for tag, path in ref_imgs.items():
                    if path:
                        ref_block += f"    {tag}: {path}\n"
            if ref_vids:
                ref_block += f"  参考视频 ({ref_library.get('统计', {}).get('参考视频总数', 0)} 段):\n"
                for tag, path in ref_vids.items():
                    if path:
                        ref_block += f"    {tag}: {path}\n"

        if model == "Seedance 2.5":
            return (
                f"═══════════════════════════════════════════════════════════\n"
                f"【Seedance 2.5 视频生成 Prompt】\n"
                f"═══════════════════════════════════════════════════════════\n\n"
                f"导演锚定: {director}\n"
                f"场景: {base_scene}\n\n"
                f"【Seedance 2.5 优化要点】\n"
                f"  - 中文 prompt 友好, 避免复杂英文从句\n"
                f"  - 强项: 3D CG, 物理一致, 多角度\n"
                f"  - 推荐: 描述运镜/光影/物理材质, 不强调长对白\n\n"
                f"【主 Prompt】\n{content_preview}\n\n"
                f"【技术规格】\n  画幅: {aspect}\n  时长: {duration}s\n  帧率: 24fps\n  物理: 重力/惯性/材质真实\n"
                f"【负向】模糊, 变形, 多余手指, 文字水印\n"
                f"【EDL 决策】\n  镜头: 6 镜分镜, 总时长 {duration}s\n  平均时长: {duration // 6}s/镜\n  转场: 硬切 + 偶尔叠化"
                + ref_block
            )
        elif model == "LTX-2.5":
            return (
                f"═══════════════════════════════════════════════════════════\n"
                f"【LTX-2.5 视频生成 Prompt】\n"
                f"═══════════════════════════════════════════════════════════\n\n"
                f"导演锚定: {director}\n场景: {base_scene}\n\n"
                f"【LTX-2.5 优化要点】\n"
                f"  - 强项: 多角度拼接, 镜头间一致性\n"
                f"  - 推荐: 拆分为多个 4-8s 短镜, 提供首尾帧描述\n"
                f"  - 适合: 同场景多机位剪辑, 时间流逝/蒙太奇\n\n"
                f"【分镜 Prompt】(分 6 镜)\n"
                f"  镜1: {director} 风格建立镜头, {scene}, {mood}\n"
                f"  镜2-5: 推进/切入/特写/视角转换, 保持色调/光影连贯\n"
                f"  镜6: 收束, 情绪落点, 留白\n\n"
                f"【技术规格】\n  画幅: {aspect}\n  总时长: {duration}s\n  镜头: 6 镜拼接\n"
                f"【负向】跳轴, 色调不连贯, 角色走形"
                + ref_block
            )
        elif model == "Wan 2.6":
            return (
                f"═══════════════════════════════════════════════════════════\n"
                f"【Wan 2.6 视频生成 Prompt】\n"
                f"═══════════════════════════════════════════════════════════\n\n"
                f"导演锚定: {director}\n场景: {base_scene}\n\n"
                f"【Wan 2.6 优化要点】\n"
                f"  - 阿里通义万相, 中文 prompt 强项\n"
                f"  - 适合: 美学向, 简洁动作, 慢节奏, 氛围电影\n"
                f"  - 推荐: 少对白, 多视觉, 重氛围, 强色调\n\n"
                f"【主 Prompt (中文)】\n{content_preview}\n\n"
                f"【美学锚点】\n  色温: 暖色/冷色 (按情绪定)\n  光影: 9D 光影设计\n  构图: 黄金分割, 9 宫格\n  运镜: 慢推/慢移/固定为主\n"
                f"【技术规格】\n  画幅: {aspect}\n  时长: {duration}s\n  帧率: 24fps"
                + ref_block
            )
        elif model == "Hailuo 2.3":
            return (
                f"═══════════════════════════════════════════════════════════\n"
                f"【Hailuo 2.3 视频生成 Prompt】\n"
                f"═══════════════════════════════════════════════════════════\n\n"
                f"导演锚定: {director}\n场景: {base_scene}\n\n"
                f"【Hailuo 2.3 优化要点】\n"
                f"  - 海螺 AI, 中文短剧向\n"
                f"  - 强项: 8s 标准时长, 抖音/快手风格\n"
                f"  - 推荐: 钩子开场, 字幕驱动, 强情绪转折\n\n"
                f"【钩子 + 主体 Prompt】\n"
                f"  前3秒: 视觉冲击/悬念/反差, 抓眼球\n"
                f"  主体: {content_preview}\n"
                f"  收尾: 情绪落点 + 留白/反转\n\n"
                f"【字幕建议】\n  关键对白加字幕, 字号大, 居中或下方\n  钩子文案: 1-2 行, 强情绪\n"
                f"【技术规格】\n  画幅: 9:16 竖屏 (默认) 或 {aspect}\n  时长: {duration}s\n  帧率: 24fps"
                + ref_block
            )
        else:  # Sora 2
            return (
                f"═══════════════════════════════════════════════════════════\n"
                f"【Sora 2 视频生成 Prompt】\n"
                f"═══════════════════════════════════════════════════════════\n\n"
                f"Director: {director}\nScene: {base_scene}\n\n"
                f"【Sora 2 Optimization】\n"
                f"  - OpenAI, physical realism & complex staging\n"
                f"  - Best for: long-form, multiple characters, precise physics\n"
                f"  - English prompts preferred\n\n"
                f"【Main Prompt (English)】\n{content_preview}\n\n"
                f"【Camera Direction】\n  Movement: {director}'s signature camera work\n  Composition: 60-30-10 color rule, rule of thirds\n  Lighting: 9D lighting design\n\n"
                f"【Tech Specs】\n  Aspect: {aspect}\n  Duration: {duration}s\n  FPS: 24"
                + ref_block
            )
