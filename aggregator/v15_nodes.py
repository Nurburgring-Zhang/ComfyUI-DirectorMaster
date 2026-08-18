# -*- coding: utf-8 -*-
"""
V15.0-MERGED 新增超级节点 (14-16)
==================================
  DirectorMasterCoCreator  — AI 共创 (五阶段共创循环: 失败记忆/方向分支/门阵/精炼/预算收敛)
  DirectorMasterSoul       — 灵魂引擎 (创作者体验 → 物件/动作/沉默母题, 场景驱动)
  DirectorMasterIntuition  — 直觉引擎 (确定性反常规镜头语法, 风险分级)
"""
import os as _os, sys as _sys, json as _json

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path:
    _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config


def _default_store_dir():
    try:
        import folder_paths
        d = folder_paths.get_output_directory()
        if d:
            return d
    except Exception:
        pass
    return _os.path.join(_PARENT, "output")


class DirectorMasterCoCreator(DirectorNodeBase):
    """AI 共创节点 — 五阶段共创循环 (V15.0).
    无 AI 端点时走 T0 确定性档 (类型公式方向+完整门阵+失败记忆), 有端点时升级 LLM 共创。"""
    NODE_TYPE = "共创"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "故事核心": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ 你的故事核心 (一句话-一段话). 共创从理解它开始"}),
            "情感诉求": ("STRING", {"default": "", "multiline": True,
                "tooltip": "你希望观众感受到什么"}),
            "审美偏好": ("STRING", {"default": "", "multiline": True,
                "tooltip": "视觉/叙事审美偏好 (可选)"}),
            "风险档位": (["medium", "safe", "bold", "chaotic", "🎲 随机"], {"default": "medium",
                "tooltip": "safe=稳妥 medium=平衡 bold=冒险 chaotic=实验; 🎲 随机"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Core.核心数据包 — 继承导演/场景/情绪/AI配置"}),
            "参考图像": ("IMAGE", {"tooltip": "V15.0: 接参考图 — 真实图像分析(色板/光影/构图)作为审美锚定"}),
            "参考图像分析": ("STRING", {"default": "", "multiline": True,
                "tooltip": "或直接粘贴已有的图像分析文本 (与参考图像二选一)"}),
            "AI接口地址": ("STRING", {"default": ""}),
            "AI密钥": ("STRING", {"default": ""}),
            "AI模型名": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("共创剧本", "方向分支图JSON", "创作日志")
    FUNCTION = "co_create_build"
    CATEGORY = "PromptLibrary/聚合/共创"

    def co_create_build(self, **kwargs):
        import random as _r
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        director = core.get("_导演名", "")
        mood = core.get("_情绪基调", "")
        scene = core.get("_场景描述", "")
        api_url, api_key, api_model = resolve_ai_config(kwargs, core)
        store_dir = _os.path.join(_default_store_dir(), "_cocreator")

        # V15.0: 参考图像真实分析 (多模态理解, 非装饰)
        ref = (kwargs.get("参考图像分析") or "").strip()
        img = kwargs.get("参考图像")
        if img is not None and not ref:
            try:
                from aggregator.multimodal_engine import analyze_image
                ia = analyze_image(img)
                if ia.get("ok"):
                    ref = ia["text"]
                else:
                    _sys.stderr.write(f"[DirectorMaster] 参考图像分析降级: {ia.get('error')}\n")
            except Exception as e:
                _sys.stderr.write(f"[DirectorMaster] 参考图像分析异常: {type(e).__name__}\n")

        from aggregator.cocreator_engine import co_create
        result = co_create(
            story_core=kwargs.get("故事核心", ""),
            emotional_intent=kwargs.get("情感诉求", ""),
            aesthetic=kwargs.get("审美偏好", ""),
            director=director, mood=mood,
            api_url=api_url, api_key=api_key, api_model=api_model,
            store_dir=store_dir,
            risk_level=(lambda _v: (_r.choice(["medium","safe","bold","chaotic"]) if _v=="🎲 随机" else _v))(kwargs.get("风险档位", "medium")),
        )

        script = result["script"]
        # 参考图像分析锚定
        if ref:
            script += f"\n\n【审美锚定 · 参考图像分析】\n{ref}"
        # 场景锚定
        if scene:
            script += f"\n\n【场景锚定】{scene}"
        script = self._apply_anti_ai(script, kwargs, core)

        branches_json = _json.dumps({
            "选定方向": result["chosen"],
            "能力档位": result["tier"],
            "方向分支": result["directions"],
            "门控报告": result["gate_report"],
            "新增教训": result["lessons_added"],
        }, ensure_ascii=False, indent=2)
        log_text = "\n".join(result["creation_log"]) + \
            f"\n\n失败记忆库: {store_dir} (lessons.jsonl, 每次拒收自动记录)"
        return (script, branches_json, log_text)


class DirectorMasterSoul(DirectorNodeBase):
    """灵魂引擎节点 — 把创作者体验转译为灵魂层 (物件/动作/沉默母题).
    全确定性, 母题从用户输入派生 (无罐头句)。"""
    NODE_TYPE = "灵魂"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "剧本输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Script.剧本 — 灵魂层注入其后"}),
            "创作者体验": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ 你的生命体验片段 (一次失败/一次爱/一次告别…) — 灵魂母题从这里派生"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
            "情感诉求": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("灵魂注入剧本", "灵魂片段报告")
    FUNCTION = "soul_build"
    CATEGORY = "PromptLibrary/聚合/灵魂"

    def soul_build(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        scene = core.get("_场景描述", "")
        mood = kwargs.get("情感诉求", "") or core.get("_情绪基调", "")

        from aggregator.soul_engine import inject_soul
        result = inject_soul(
            script_text=kwargs.get("剧本输入", ""),
            creator_experience=kwargs.get("创作者体验", ""),
            emotional_intent=mood,
            scene=scene,
        )
        report = _json.dumps({
            "叙事装置": result["device"],
            "装置规则": result["device_rule"],
            "情感三层": result["layers"],
            "灵魂母题": result["fragments"],
        }, ensure_ascii=False, indent=2)
        return (result["script"], report)


class DirectorMasterIntuition(DirectorNodeBase):
    """直觉引擎节点 — 对分镜 JSON 应用确定性反常规镜头语法 (风险分级).
    每条规则有真实作者电影依据, 修改日志可追溯。"""
    NODE_TYPE = "直觉"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "分镜JSON": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Cinematic.分镜JSON — 直觉修改其镜头"}),
            "风险档位": (["medium", "safe", "bold", "chaotic", "🎲 随机"], {"default": "medium"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("直觉分镜JSON", "直觉修改日志")
    FUNCTION = "intuition_build"
    CATEGORY = "PromptLibrary/聚合/直觉"

    def intuition_build(self, **kwargs):
        import random as _r
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        mood = core.get("_情绪基调", "")
        scene = core.get("_场景描述", "")
        try:
            data = _json.loads(kwargs.get("分镜JSON", "") or "{}")
        except Exception:
            data = {}
        shots = data.get("分镜表", []) if isinstance(data, dict) else []

        from aggregator.intuition_engine import apply_intuition
        # V16.0 需求1: 风险档位支持 🎲 随机
        _risk = kwargs.get("风险档位", "medium")
        if _risk == "🎲 随机":
            _risk = _r.choice(["medium", "safe", "bold", "chaotic"])
        modified, log = apply_intuition(
            shots, mood=mood, scene=scene,
            risk_level=_risk,
            seed=f"{scene}|{mood}",
        )
        if isinstance(data, dict):
            data["分镜表"] = modified
            data["直觉引擎"] = {"风险档位": kwargs.get("风险档位", "medium"), "触发数": len(log)}
        log_text = _json.dumps(log, ensure_ascii=False, indent=2)
        return (_json.dumps(data, ensure_ascii=False, indent=2), log_text)


class DirectorMasterFusion(DirectorNodeBase):
    """风格融合节点 — 主风格(0.6)+次风格(0.3)+反风格(0.1) 确定性文本融合.
    反风格提取"反常规动作"作为突破指令, 打破主风格惯性。全确定性。"""
    NODE_TYPE = "融合"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "主风格导演": ("STRING", {"default": "[电影] 王家卫",
                "tooltip": "★ 主风格 (权重0.6) — 全部维度作为基底"}),
            "次风格导演": ("STRING", {"default": "",
                "tooltip": "次风格 (权重0.3) — 选互补维度作为修饰层 (可空)"}),
            "反风格导演": ("STRING", {"default": "",
                "tooltip": "反风格 (权重0.1) — 提取反常规动作作为突破指令 (可空)"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
            "场景描述": ("STRING", {"default": ""}),
            "情绪基调": ("STRING", {"default": ""}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("融合风格档案", "融合元数据JSON")
    FUNCTION = "fusion_build"
    CATEGORY = "PromptLibrary/聚合/融合"

    def fusion_build(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        scene = kwargs.get("场景描述", "") or core.get("_场景描述", "")
        mood = kwargs.get("情绪基调", "") or core.get("_情绪基调", "")

        from aggregator.style_fusion import fuse_styles
        result = fuse_styles(
            primary=kwargs.get("主风格导演", ""),
            secondary=(kwargs.get("次风格导演", "") or "").strip() or None,
            anti=(kwargs.get("反风格导演", "") or "").strip() or None,
            scene=scene, mood=mood,
        )
        meta = _json.dumps({
            "主风格": result["primary"],
            "次风格": result["secondary"],
            "反风格": result["anti"],
            "融合维度": result["fused_dims"],
            "突破指令": result["break_directive"],
            "错误": result["error"],
        }, ensure_ascii=False, indent=2)
        text = result["text"] or f"(风格融合失败: {result['error']})"
        return (text, meta)
