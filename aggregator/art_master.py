# -*- coding: utf-8 -*-
"""
④ DirectorMasterArt — 美术空间 (3 合 1)
========================================
美术指导/空间一致性/空间布局. 输出 6 个 STRING.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy

ART_MODES = ["美术指导","空间一致性","空间布局"]

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


def _build_art_template(scene, director, mood, core):
    """美术圣经 — V13.3 场景驱动 (按场景地点/物件/年代生成色彩+光影+材质)."""
    core = core or {}
    p = _parse_scene_safe(scene)
    loc = p.get("location") or "场景"
    objs = p.get("objects") or ["关键道具"]
    era = _detect_era_safe(scene)
    visual = core.get("_视觉调性", "写实")
    obj_str = "、".join(objs[:4])
    # 年代材质基调
    material_base = {
        "古装": "木材(旧痕), 织物(粗粝), 金属(刀剑铜器), 陶土, 纸",
        "科幻": "金属(哑光), 玻璃(舱体), 复合面板, 光面, 织物(功能面料)",
        "复古": "织物(褪色), 木材(旧痕), 金属(锈迹), 玻璃, 纸(泛黄)",
        "现代": "织物, 木材, 玻璃, 金属, 塑料, 电子屏",
    }.get(era, "织物, 木材, 玻璃, 金属")
    # 情绪→色温/对比
    warm_moods = {"温暖", "浪漫", "喜剧", "希望"}
    cold_moods = {"孤独", "悲伤", "悬疑", "恐惧", "宁静"}
    if mood in warm_moods:
        temp, contrast = "3200K(暖)", "中低"
    elif mood in cold_moods:
        temp, contrast = "5600K(冷)", "中高"
    else:
        temp, contrast = "4300K(中性)", "中"
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【美术圣经】导演: {director} | 场景: {scene}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"整体视觉基调: {visual} · {era} · {mood}——服务于'{core.get('_主题词','情感')}'.\n"
        f"空间: {loc}\n"
        f"主材质: {material_base}\n"
        f"材质细节: {obj_str} 各自的磨损/年代/使用痕迹.\n\n"
        f"色彩系统(60-30-10):\n"
        f"  主色60%: 按{visual}定基调 — 墙面/空间/大面积\n"
        f"  辅色30%: 按情绪({mood})定冷暖 — 光源/家具\n"
        f"  点缀色10%: {objs[0]}的颜色 — 视觉焦点\n\n"
        f"光影9D:\n"
        f"  方向: 按场景光源(窗/灯/天光)定\n"
        f"  色温: {temp}\n"
        f"  对比: {contrast}\n"
        f"  软硬: 按情绪({mood})定——柔化或硬朗\n"
        f"  层次: 3层(前景{objs[0]}/中景人物/背景{loc})\n"
        f"  时代: {era}\n"
        f"  氛围: {mood}\n\n"
        f"视觉语言参数:\n"
        f"  焦段: 50mm(主), 35mm(特写), 85mm(近景)\n"
        f"  景别: 中景为主, 特写({objs[0]}), 全景({loc})\n"
        f"  构图: 三分法+空间框景\n"
        f"  时代: {era} | 视觉调性: {visual}"
    )

def _build_spatial_template(scene, director, mood, core):
    """空间一致性 — V13.3 场景驱动. 关注跨镜头的位置/轴线/物件恒常."""
    core = core or {}
    p = _parse_scene_safe(scene)
    loc = p.get("location") or "场景"
    objs = p.get("objects") or ["关键道具"]
    chars = p.get("characters") or ["主角"]
    ie = p.get("ie", "内")
    n_chars = len(chars)
    char_pos = []
    _positions = ["frame-left", "frame-right", "center", "frame-left-foreground", "frame-right-background"]
    for i, c in enumerate(chars[:3]):
        char_pos.append(f"角色{i+1}({c})位置: {_positions[i % len(_positions)]}")
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【空间一致性】导演: {director} | 场景: {scene}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"空间类型: {loc}({ie}景)\n"
        f"空间细节: 按场景描述还原, 关键物件 {('、'.join(objs[:5]))}\n"
        f"角色数量: {n_chars}\n"
        + "\n".join(char_pos) + "\n"
        f"关键道具: {'、'.join(objs[:4])}\n"
        f"镜头停留秒数: 3.0\n"
        f"连续运动: 按情绪({mood})定——慢推/固定/环绕\n"
        f"空间稳定强度: 8/10\n"
        f"位置可信强度: 8/10\n"
        f"轴线规则: 角色间连线为轴, 镜头不越轴(除非情绪转折)"
    )


def _build_spatial_layout_template(scene, director, mood, core):
    """空间布局 — V14.3 (红队P2修复: 与空间一致性实质区分).
    关注空间本身的功能分区/锚点/动线/机位规划, 而非跨镜头一致性规则."""
    core = core or {}
    p = _parse_scene_safe(scene)
    loc = p.get("location") or "场景"
    objs = p.get("objects") or ["关键道具"]
    chars = p.get("characters") or ["主角"]
    ie = p.get("ie", "内")
    import hashlib as _hl_sl
    _h = int(_hl_sl.md5(f"{scene}_{director}".encode("utf-8", "replace")).hexdigest(), 16)
    depth = ["三层纵深 (前景遮挡/中景主体/背景环境)", "两层纵深 (主体/背景)", "四层纵深 (含画框元素)"][_h % 3]
    anchor = objs[0] if objs else "关键道具"
    route_a = chars[0] if chars else "主角"
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【空间布局】导演: {director} | 场景: {scene}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"空间基底: {loc}({ie}景)\n"
        f"纵深设计: {depth}\n"
        f"功能分区: 主表演区({anchor}所在) / 次表演区(对手位) / 通道区(进出动线) / 背景信息区\n"
        f"空间锚点: {anchor} — 视觉重心, 构图围绕其展开\n"
        f"角色动线: {route_a} 的走位路径 = 入口→主表演区→锚点附近→情绪位\n"
        f"机位规划: A机(主机位·轴线内) / B机(侧逆·情绪位) / C机(游机·细节)\n"
        f"视线设计: 角色视线引导观众注意力至 {anchor}\n"
        f"遮挡关系: 前景元素制造窥视感/层次感 (情绪: {mood})\n"
        f"光源布局: 主光源位置决定阴影方向, 与纵深设计联动"
    )


TEMPLATES = {"美术指导": _build_art_template, "空间一致性": _build_spatial_template, "空间布局": _build_spatial_layout_template}


class DirectorMasterArt(DirectorNodeBase):
    """美术空间聚合节点 — 3 合 1."""
    NODE_TYPE = "美术指导"

    @classmethod
    def INPUT_TYPES(cls):
        _ND = "无(默认)"  # V12.6 v7 fix: 兼容老版本 saved workflow
        _R = "🎲 随机"  # V12.6 v8: 随机化选项
        return {"required": {
            "美术模式": (ART_MODES, {"default": "美术指导"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "从核心数据包继承, 此处可单独覆盖"}),
            "色彩风格": ([_ND,_R,"梦幻","赛博朋克","复古胶片","黑白","暖色","冷色","高饱和","低饱和",
                          "霓虹","日式小清新","港式怀旧","民国复古","欧洲古典","美式脏脏","拉美浓烈",
                          "中东异域","北欧极简","南亚艳丽","非洲暖阳","未来赛博","废土棕黄","胶片绿","血浆红",
                          "水墨青绿","国画朱砂","敦煌重彩","浮世绘","蒸汽朋克","工业风","波西米亚","孟菲斯",
                          "酸性金属","极简白","莫兰迪","中国红","圣诞红绿","万圣节橙黑"], {"default": _ND,
                "tooltip": "选择色彩基调 → 真实影响输出色彩系统 (40+ 选项)"}),
            "光影方向": ([_ND,_R,"逆光","顺光","侧光","顶光","底光","混合光",
                          "霓虹光","烛光","月光","日光","暮光","晨曦",
                          "伦勃朗光","蝴蝶光","环形光","夹板光","轮廓光","剪影光",
                          "舞台光","霓虹灯管光","路灯昏黄","车窗光","台灯光","壁炉光"], {"default": _ND,
                "tooltip": "选择主光源方向 → 真实影响光影9D设计 (25+ 选项)"}),
            "材质重点": ([_ND,_R,"织物","金属","木材","玻璃","石材","塑料","有机/肌肤",
                          "丝绸","皮革","陶瓷","纸张","水/液体","火/烟","植物/树叶","食物",
                          "电子/屏幕","混凝土","砖墙","锈迹","灰尘/沙","冰/雪","毛发"], {"default": _ND,
                "tooltip": "选择主材质 → 真实影响材质细节描述 (25+ 选项)"}),
            "构图法则": ([_ND,_R,"三分法","黄金比例","中心对称","对角线","框中框","引导线","负空间",
                          "S形曲线","三角形","圆形","框中框中框","斜线/对角张力",
                          "极简留白","繁复铺满","放射性","螺旋","中心放射","T形/十字"], {"default": _ND,
                "tooltip": "选择构图法则 → 真实影响视觉语言参数 (20+ 选项)"}),
            "摄影风格": ([_ND,_R,"手持","固定机位","长镜头","快速切镜","航拍","稳定器",
                          "Steadicam","吊臂","伸缩炮","水下摄影","微距","红外热成像",
                          "鱼眼","广角变形","远程遥控","第一视角POV","跟焦拉镜","穿越机FPV",
                          "轨道车","炮臂","希区柯克变焦","荷兰角倾斜"], {"default": _ND,
                "tooltip": "选择摄影运动风格 → 真实影响摄影参考选择 (24+ 选项)"}),
        }, "optional": {
            "色彩风格_多选": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ V13.2 多选: 多种色彩风格随叙事演变, 用 逗号/箭头 分隔。例: '冷色→高饱和→暖色' (开场冷, 高潮艳, 结尾暖)。优先于上方单选色彩风格"}),
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承场景/导演/情绪/灵魂/AI"}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("美术",)
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/美术"

    def build(self, **kwargs):
        from aggregator.node_base import resolve_dropdown
        mode = kwargs.get("美术模式","美术指导")
        if mode not in ART_MODES: mode = "美术指导"
        core = parse_core_pack(kwargs.get("核心数据包",""))
        scene = core.get("_场景描述") or kwargs.get("场景描述","")
        director = core.get("_导演风格") or kwargs.get("导演风格","王家卫")
        mood = core.get("_情绪基调","孤独")

        # V12.6 v8: 下拉框解析 (支持 "无(默认)" 和 "🎲 随机")
        _ART_OPTS = ["梦幻","赛博朋克","复古胶片","黑白","暖色","冷色","高饱和","低饱和",
                      "霓虹","日式小清新","港式怀旧","民国复古","欧洲古典","美式脏脏","拉美浓烈",
                      "中东异域","北欧极简","南亚艳丽","非洲暖阳","未来赛博","废土棕黄","胶片绿","血浆红",
                      "水墨青绿","国画朱砂","敦煌重彩","浮世绘","蒸汽朋克","工业风","波西米亚","孟菲斯",
                      "酸性金属","极简白","莫兰迪","中国红","圣诞红绿","万圣节橙黑"]
        _LIGHT_OPTS = ["逆光","顺光","侧光","顶光","底光","混合光",
                         "霓虹光","烛光","月光","日光","暮光","晨曦",
                         "伦勃朗光","蝴蝶光","环形光","夹板光","轮廓光","剪影光",
                         "舞台光","霓虹灯管光","路灯昏黄","车窗光","台灯光","壁炉光"]
        _MAT_OPTS = ["织物","金属","木材","玻璃","石材","塑料","有机/肌肤",
                       "丝绸","皮革","陶瓷","纸张","水/液体","火/烟","植物/树叶","食物",
                       "电子/屏幕","混凝土","砖墙","锈迹","灰尘/沙","冰/雪","毛发"]
        _COMP_OPTS = ["三分法","黄金比例","中心对称","对角线","框中框","引导线","负空间",
                       "S形曲线","三角形","圆形","框中框中框","斜线/对角张力",
                       "极简留白","繁复铺满","放射性","螺旋","中心放射","T形/十字"]
        _PHOTO_OPTS = ["手持","固定机位","长镜头","快速切镜","航拍","稳定器",
                        "Steadicam","吊臂","伸缩炮","水下摄影","微距","红外热成像",
                        "鱼眼","广角变形","远程遥控","第一视角POV","跟焦拉镜","穿越机FPV",
                        "轨道车","炮臂","希区柯克变焦","荷兰角倾斜"]
        kwargs["色彩风格"] = resolve_dropdown(kwargs.get("色彩风格"), "梦幻", _ART_OPTS)
        kwargs["光影方向"] = resolve_dropdown(kwargs.get("光影方向"), "逆光", _LIGHT_OPTS)
        kwargs["材质重点"] = resolve_dropdown(kwargs.get("材质重点"), "织物", _MAT_OPTS)
        kwargs["构图法则"] = resolve_dropdown(kwargs.get("构图法则"), "三分法", _COMP_OPTS)
        kwargs["摄影风格"] = resolve_dropdown(kwargs.get("摄影风格"), "手持", _PHOTO_OPTS)

        # V13.2: 色彩多选演变 — 多值时首值为主色彩, 全部值按叙事阶段生成色彩演变块
        from aggregator.node_base import parse_multi_select
        color_arc = parse_multi_select(kwargs.get("色彩风格_多选", ""))
        if color_arc:
            kwargs["色彩风格"] = color_arc[0]

        # 美术圣经模板已含 色彩系统/光影9D/摄影8大师/视觉语言参数, 全部在一个主输出里
        builder = TEMPLATES.get(mode, _build_art_template)
        bible = builder(scene, director, mood, core)
        bible += self._director_block(director)
        from aggregator.dimensions import apply_dimensions, COLOR_MAP
        bible += "\n\n" + apply_dimensions("美术", kwargs)

        # V13.2: 色彩演变弧 (多选) — 按 建置/对抗/高潮/解决 叙事阶段分配色彩
        if len(color_arc) > 1:
            _stage_names = ["建置(开场)", "上升(对抗)", "高潮(顶点)", "解决(结尾)"]
            _lines = ["", "【色彩演变弧 (V13.2 多选)】色彩随情节推进演变, 非全片单一色调:"]
            n = len(color_arc)
            for i, cv in enumerate(color_arc):
                stage = _stage_names[int(i / max(n - 1, 1) * (len(_stage_names) - 1) + 0.5)] if n <= 4 else f"阶段{i+1}/{n}"
                palette = COLOR_MAP.get(cv, cv)
                _lines.append(f"  {stage}: {cv} → {palette}")
            _lines.append(f"  过渡: 相邻阶段间用 1-2 场戏渐变 (道具/光源/服装颜色先行), 避免硬切色调")
            bible += "\n".join(_lines)

        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url:
            bible = self._ensure_ai_output(bible,
                {"node_type":"美术指导","mode":mode,"director":director,"scene":scene,"mood":mood,"intent":core.get("_导演意图_观众应感到","") if core else ""},
                api_url, api_key, ai_model)

        from aggregator.pro_format import strip_decor
        # V14.2: 启用反AI规则 真实生效 (此前声明未消费)
        return (self._apply_anti_ai(strip_decor(bible), kwargs, core),)