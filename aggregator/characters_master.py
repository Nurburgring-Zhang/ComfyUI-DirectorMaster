# -*- coding: utf-8 -*-
"""
V12.6 DirectorMasterCharacters — 角色超级节点 (4 模式)
========================================================
V12.6 包装 V9.5 DirectorMasterAsset (3 模式: 角色/环境/服化道) + V12.6 新增"参考图"模式.
- 核心数据包 forceInput 接 Core 节点, 继承灵魂/场景/导演/AI
- 参考图模式: 生成 L1-L7 分层 prompt 用于 IP-Adapter/参考图引导生成
- 6 路 output: 角色圣经 / 环境圣经 / 服化道圣经 / 三视图锚定 / MIP资产卡 / 完整资产

V9.5 真实能力继承 — 不重复输入故事描述.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config
from aggregator.pro_format import strip_decor
from aggregator.asset_master import DirectorMasterAsset, ASSET_MODES, _CHARACTER_MODES, _ENV_MODES
from aggregator.ref_media import resolve_ref, image_batch_to_ref_paths

CHARACTER_MODES = ASSET_MODES + ["参考图"]  # 4 模式: 角色/环境/服化道/参考图


class DirectorMasterCharacters(DirectorNodeBase):
    """V12.6 角色超级节点 — 4 模式 (V9.5 3 模式 + V12.6 参考图). 6 路 output."""
    NODE_TYPE = "角色"

    @classmethod
    def INPUT_TYPES(cls):
        _R = "🎲 随机"
        return {"required": {
            "节点模式": (CHARACTER_MODES+[_R], {"default": "角色设定"}),
            "项目名": ("STRING", {"default": "我的电影项目"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承导演风格/场景/情绪/灵魂/AI, 无需重复输入"}),
            "参考图路径": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "参考图路径/URL — 或用 IMAGE 槽直接接 LoadImage"}),
            "参考视频路径": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "参考视频路径/URL — 或用 IMAGE 槽直接接 LoadVideo"}),
            # V13 合并: IMAGE 类型输入槽 (ComfyUI 标准) — 直接接 LoadImage/LoadVideo 的 IMAGE 输出
            "参考图_IMAGE": ("IMAGE", {"tooltip": "★ ComfyUI 标准: 接 LoadImage 的 IMAGE 输出 — 锁定角色面部/服装锚点"}),
            "参考视频_IMAGE": ("IMAGE", {"tooltip": "接 LoadVideo/VHS 的 IMAGE 批次 — 锁定运动/节奏"}),
            "角色名": ("STRING", {"default": "主角"}),
            "角色年龄": ("STRING", {"default": "30"}),
            "角色性别": ([_R,"男", "女", "不限"], {"default": "男"}),
            "角色性格": ("STRING", {"default": "沉默寡言, 内敛, 用行动表达", "multiline": True}),
            "角色外貌": ("STRING", {"default": "短发, 瘦削, 颧骨高, 眼窝深, 右手食指有老茧", "multiline": True}),
            "角色服装": ("STRING", {"default": "深蓝色工作服(褪色), 灰色秋衣, 布鞋", "multiline": True}),
            "环境类型": ([_R,"室内", "室外", "太空", "水下", "虚拟"], {"default": "室内"}),
            "环境描述": ("STRING", {"default": "厨房8平米, 灶台+砧板+碗柜+餐桌+窗", "multiline": True}),
            "服化道描述": ("STRING", {"default": "旧信(泛黄), 凤梨罐头(过期), 钢笔(没墨水), 收音机", "multiline": True}),
            "视觉风格": ([_R,"写实", "日漫", "美漫", "3D CG", "水彩", "油画", "赛璐璐", "水墨"], {"default": "写实"}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("角色圣经", "环境圣经", "服化道圣经", "三视图锚定", "MIP资产卡", "完整资产")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/角色"

    def build(self, **kwargs):
        mode = kwargs.get("节点模式", "角色设定")
        # V16.0 需求1: 模式选择器支持 🎲 随机
        if mode == "🎲 随机":
            import random as _r
            mode = _r.choice(CHARACTER_MODES)
        if mode not in CHARACTER_MODES: mode = "角色设定"
        # V16.0 需求1: 属性下拉支持 🎲 随机
        import random as _r_attr
        def _rnd_attr(v, opts):
            if v == "🎲 随机":
                return _r_attr.choice([o for o in opts if o != "🎲 随机"])
            return v
        kwargs["角色性别"] = _rnd_attr(kwargs.get("角色性别", "男"), ["男", "女", "不限"])
        kwargs["环境类型"] = _rnd_attr(kwargs.get("环境类型", "室内"), ["室内", "室外", "太空", "水下", "虚拟"])
        kwargs["视觉风格"] = _rnd_attr(kwargs.get("视觉风格", "写实"), ["写实", "日漫", "美漫", "3D CG", "水彩", "油画", "赛璐璐", "水墨"])
        core = parse_core_pack(kwargs.get("核心数据包", ""))
        director = core.get("_导演风格", "王家卫") if core else "王家卫"
        scene = core.get("_场景描述", "") if core else ""
        mood = core.get("_情绪基调", "") if core else ""
        project = kwargs.get("项目名", "我的电影项目")

        # 模式 1-3 复用 V9.5 DirectorMasterAsset 真实能力
        if mode in ASSET_MODES:
            v95_kwargs = dict(kwargs)
            v95_kwargs["资产模式"] = mode  # V9.5 用 资产模式 字段名
            # 提取参考图/视频 (V9.5 用 参考图路径 字段, 但也接受 forceInput)
            if kwargs.get("参考图路径"):
                v95_kwargs["参考图路径"] = kwargs["参考图路径"]
            if kwargs.get("参考视频路径"):
                v95_kwargs["参考视频路径"] = kwargs["参考视频路径"]
            # V13 合并: 单一 IMAGE 输入按模式映射到 Asset 对应 IMAGE 槽
            if kwargs.get("参考图_IMAGE") is not None:
                _img_key_map = {"角色设定": "参考图_IMAGE_角色正面",
                                 "环境设定": "参考图_IMAGE_环境母版",
                                 "服化道设定": "参考图_IMAGE_道具母版"}
                v95_kwargs[_img_key_map.get(mode, "参考图_IMAGE_角色正面")] = kwargs["参考图_IMAGE"]
            if kwargs.get("参考视频_IMAGE") is not None:
                v95_kwargs["参考视频_IMAGE_运动母版"] = kwargs["参考视频_IMAGE"]
            # V9.5 强制解包 forceInput 引用 (空字符串也安全)
            asset_node = DirectorMasterAsset()
            asset_text = asset_node.build(**v95_kwargs)[0]
            # V13.1: 拆分到 6 路 — 按 角色/环境/服化道 三类路由 (不再只认三个基础模式名)
            char_bible = asset_text if mode in _CHARACTER_MODES else ""
            env_bible = asset_text if mode in _ENV_MODES else ""
            costume_bible = asset_text if (mode not in _CHARACTER_MODES and mode not in _ENV_MODES) else ""
            # 三视图锚定
            three_view = self._extract_three_view(asset_text, mode, kwargs)
            # MIP 资产卡
            mip_card = self._build_mip_card(asset_text, mode, director, scene, mood, kwargs)
            return (char_bible, env_bible, costume_bible, three_view, mip_card, asset_text)

        # 模式 4: 参考图 (V12.6 新增 — 用于 IP-Adapter/参考图引导生成)
        # V13 合并: IMAGE 张量优先(落盘返回文件名), 否则 STRING 路径
        ref_img = resolve_ref(kwargs, "参考图_IMAGE", "参考图路径", "角色参考")
        _ref_vid_raw = kwargs.get("参考视频_IMAGE")
        if _ref_vid_raw is not None:
            _frames = image_batch_to_ref_paths(_ref_vid_raw, "运动母版")
            ref_vid = ",".join(_frames) if _frames else (kwargs.get("参考视频路径") or "").strip()
        else:
            ref_vid = (kwargs.get("参考视频路径") or "").strip()
        visual_style = kwargs.get("视觉风格", "写实")
        char_name = kwargs.get("角色名", "主角")
        appearance = kwargs.get("角色外貌", "")
        costume = kwargs.get("角色服装", "")

        if not ref_img and not ref_vid:
            ref_text = f"(未提供参考图/视频 — 可接 LoadImage/LoadVideo 的 IMAGE 输出到 IMAGE 槽, 或填路径到路径槽)"
        else:
            ref_text = f"参考图: {ref_img or '无'}\n参考视频: {ref_vid or '无'}"

        # 构建参考图引导 prompt
        ref_card = (
            f"═══════════════════════════════════════════════════════════\n"
            f"【参考图引导】导演: {director} | 项目: {project} | 风格: {visual_style}\n"
            f"═══════════════════════════════════════════════════════════\n\n"
            f"【视觉锚点】\n{ref_text}\n\n"
            f"【IP-Adapter 提示词模板】(用于跨镜头一致性)\n"
            f"  主体: {char_name}, {appearance}, {costume}\n"
            f"  风格: {visual_style}, {director} 导演, {mood} 情绪\n"
            f"  场景: {scene}\n\n"
            f"【使用建议】\n"
            f"  1. 首镜生成时将参考图作为 IP-Adapter 输入, 锁定角色面部/服装/色调\n"
            f"  2. 后续每镜复用同一参考图 + 不同 prompt, 确保视觉一致\n"
            f"  3. 若用 FaceID/ControlNet 联合, 面部特征锁定更强\n"
            f"  4. 参考视频用于锁定运镜节奏 (镜头切换/推拉速度/构图方式)"
        )
        char_bible = f"参考图锚定: {char_name} = {ref_img or ref_vid or '无'}"
        return (char_bible, "", "", ref_card, ref_card, ref_card)

    def _extract_three_view(self, asset_text, mode, kwargs):
        """从 V9.5 asset 输出中提取三视图锚定 (全部角色模式)."""
        if mode not in _CHARACTER_MODES:
            return f"(非角色模式 — 三视图锚定仅在角色类模式下生成)"
        char_name = kwargs.get("角色名", "主角")
        appearance = kwargs.get("角色外貌", "")
        costume = kwargs.get("角色服装", "")
        visual_style = kwargs.get("视觉风格", "写实")
        return (
            f"【三视图锚定】{char_name}\n"
            f"  正面: {char_name}正面半身, {appearance}, {costume}, {visual_style}\n"
            f"  侧面: {char_name}侧面半身, 轮廓特征清晰\n"
            f"  背面: {char_name}背面半身, 服装后片完整\n"
            f"  表情锚定: 中性 + 3 种情绪变体(微笑/凝重/惊讶)\n"
            f"  → 用 IP-Adapter / Reference-only / FaceID 锁定, 跨镜头一致"
        )

    def _build_mip_card(self, asset_text, mode, director, scene, mood, kwargs):
        """MIP (Multi-IP) 资产卡 — 跨多角色/多场景一致性策略."""
        char_name = kwargs.get("角色名", "主角")
        return (
            f"═══════════════════════════════════════════════════════════\n"
            f"【MIP 资产卡】{director} | 模式: {mode}\n"
            f"═══════════════════════════════════════════════════════════\n\n"
            f"【多 IP 锚定策略】\n"
            f"  主IP: {char_name} (锁定: 面部骨骼+服装配色+身高比例)\n"
            f"  副IP: 环境母版 (锁定: 空间布局+光影+色调)\n"
            f"  副IP: 道具母版 (锁定: 旧信/凤梨罐头/钢笔/收音机)\n\n"
            f"【跨镜头一致性】\n"
            f"  镜头1-6 复用同一组 IP-Adapter 输入, 调整 prompt 实现动作/情绪变化\n"
            f"  关键: 不重置参考图, 只调整 IP-Adapter 权重 (0.6-0.8)\n\n"
            f"【场景/情绪上下文】\n"
            f"  场景: {scene}\n  情绪: {mood}\n  导演: {director}"
        )
