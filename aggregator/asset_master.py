# -*- coding: utf-8 -*-
"""
⑩ DirectorMasterAsset — 角色/环境/服化道设定 (新增)
====================================================
AI漫剧全流程命门: 角色一致性. 本节点:
  - 接收参考图/参考视频(路径或描述) → 锁定角色/环境视觉锚点
  - 输出角色卡(外貌/服装/三视图锚定) + 环境卡 + 服化道卡
  - 可接 Core 核心数据包继承导演风格/AI能力
  - 输出1个 资产设定 STRING, 连入 Final 汇总

41模式: 角色设定 / 环境设定 / 服化道设定 细分 + HellGrind资产库
V14.2: HellGrind资产库 接线真实 asset_registry 引擎 (Higgsfield Hell Grind 复刻:
       8 资产 descriptor/状态变体/voice/behavior/压力测试/锁定), 此前默认 13 节点无入口。
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config
from aggregator.pro_format import strip_decor
from aggregator.ref_media import resolve_ref, image_batch_to_ref_paths

# V12.6 v8: 资产模式按 角色/环境/服化道 + 类型细分
ASSET_MODES = [
    # === 角色设定 ===
    "角色设定", "群像角色", "反派角色", "主角角色", "配角角色", "工具人角色",
    "古风角色", "现代角色", "未来角色", "奇幻角色", "科幻角色",
    # === 环境设定 ===
    "环境设定", "室内环境", "室外环境", "城市环境", "乡村环境", "自然环境",
    "太空环境", "水下环境", "虚拟环境", "末世环境", "历史环境",
    "现实场景(写实)", "奇幻场景", "科幻场景", "梦境场景", "记忆场景",
    # === 服化道设定 ===
    "服化道设定", "服装设计", "化妆造型", "道具设计", "武器设计", "交通工具设计",
    "食品设计", "日常用品", "特殊道具", "时代道具", "未来道具",
    # === 混合 ===
    "综合资产卡", "参考库生成",
    # === V14.2: Hell Grind 资产库 (接线真实 asset_registry 引擎) ===
    "HellGrind资产库",
]

# V13 合并修复 (A-01): 39 模式按 角色/环境/服化道 三类路由, 避免 37 模式静默落入服化道分支
_CHARACTER_MODES = {"角色设定", "群像角色", "反派角色", "主角角色", "配角角色", "工具人角色",
                     "古风角色", "现代角色", "未来角色", "奇幻角色", "科幻角色"}
_ENV_MODES = {"环境设定", "室内环境", "室外环境", "城市环境", "乡村环境", "自然环境",
              "太空环境", "水下环境", "虚拟环境", "末世环境", "历史环境",
              "现实场景(写实)", "奇幻场景", "科幻场景", "梦境场景", "记忆场景"}
# 其余 (服化道设定/服装设计/化妆造型/道具设计/武器设计/交通工具设计/食品设计/日常用品/特殊道具/时代道具/未来道具/综合资产卡/参考库生成) → 服化道分支

# ============================================================
# V13.1: 全 40 模式差异化内容池 + 核心数据包继承
# ============================================================
import hashlib as _hashlib

def _aseed_choice(pool, seed):
    """确定性种子选择 — 同输入同输出."""
    if not pool:
        return ""
    idx = int(_hashlib.md5(str(seed).encode("utf-8", errors="replace")).hexdigest(), 16) % len(pool)
    return pool[idx]

# 每个角色子模式的叙事定位 (差异化, 不再是同一张卡换个标题)
_CHAR_ROLE_HINT = {
    "角色设定": "主要人物设定 — 全片视点与情感锚点",
    "主角角色": "叙事视点人物 — 承载主题弧光, 从缺失走向完成",
    "反派角色": "对抗轴心 — 主角价值观的镜像与考验, 动机自洽不脸谱",
    "配角角色": "副线人物 — 侧面烘托主角, 承担情感对照功能",
    "工具人角色": "功能人物 — 关键节点出场推动情节, 用一个细节让人记住",
    "群像角色": "多视点人物网络 — 命运交织, 每人一条独立欲望线",
    "古风角色": "古典人物 — 礼仪/称谓/举止符合时代, 衣冠即身份",
    "现代角色": "当代人物 — 生活质感优先, 细节真实可触",
    "未来角色": "未来人物 — 科技外饰保留人性内核, 装备服务于性格",
    "奇幻角色": "超自然人物 — 视觉符号强, 能力有代价",
    "科幻角色": "科幻人物 — 科技装备逻辑自洽, 功能可解释",
}

# 自动补全池 (用户未填性格/外貌/服装时, 按种子生成 — 同输入同输出)
_PERSONA_TRAITS = [
    "沉默寡言, 用行动表达", "外冷内热, 嘴硬心软", "隐忍克制, 情绪藏在细节里",
    "爽朗直接, 心里藏着事", "谨慎多疑, 观察力极强", "温和退让, 底线分明",
    "倔强执拗, 不撞南墙不回头", "幽默自嘲, 用玩笑掩饰伤痛", "敏感细腻, 善于察觉他人难堪",
    "果断强势, 独处时才松懈",
]
_LOOK_TRAITS = [
    "眼角细纹, 目光先躲闪后坚定", "手指粗糙, 有一处旧伤", "站姿微驼, 坐下才放松",
    "头发凌乱却干净", "眼下青黑, 强撑精神", "嘴角习惯性抿紧", "笑时先动眼睛",
    "肩线紧绷, 走路快", "皮肤晒痕明显", "指甲修剪得极短",
]
_WARD_TRAITS = [
    "洗旧但整洁", "低饱和色系", "随身一件不合时宜的旧物", "袖口磨损已缝补",
    "鞋干净但变形", "领口永远扣到最上一颗", "腰间挂着实用小物", "衣物有职业痕迹",
]
_ERA_WARD = {
    "古风角色": "宽袖长袍, 腰封革带, 布料纹理粗粝真实",
    "未来角色": "无缝剪裁, 哑光功能面料, 隐藏式接口",
    "科幻角色": "轻量化装备, 磨损掉漆, 有使用痕迹",
    "奇幻角色": "手工感服饰, 符号纹样, 材质混搭",
    "现代角色": "当代成衣, 有生活褶皱",
}

# 环境子模式设计指令 (每个模式给出专属空间设计要点)
_ENV_DESIGN = {
    "环境设定": ["空间三层: 前景遮挡/中景动作区/后景信息层", "光源单一可解释", "留一处人物生活痕迹"],
    "室内环境": ["窗户位置决定光路", "家具磨损程度暗示居住年限", "墙面物件交代人物背景"],
    "室外环境": ["天气作为情绪参与叙事", "地面材质反光控制", "远景天际线压缩或释放情绪"],
    "城市环境": ["招牌/管线/空调外机构成信息密度", "人流节奏与主角节奏相反", "夜色用混合色温"],
    "乡村环境": ["土路/植被季节性真实", "炊烟与狗吠的空间感", "光线无遮挡, 阴影硬朗"],
    "自然环境": ["风声/水声作为情绪底色", "植物层次: 近草/中灌/远林", "天气变化推动情节"],
    "太空环境": ["零重力漂浮细节(头发/水滴/衣物)", "舱壁冷光与舷外深空对比", "设备指示灯是唯一暖色"],
    "水下环境": ["光束丁达尔效应", "气泡节奏即呼吸节奏", "色彩随深度递减"],
    "虚拟环境": ["网格/粒子暴露虚拟边界", "物理规则可局部失效", "色彩过饱和暗示非真实"],
    "末世环境": ["文明残骸的具体物件(半块招牌/锈蚀车辆)", "植被 reclaim 人造物", "天空永远不干净"],
    "历史环境": ["年代考据: 建材/照明/交通工具", "无现代痕迹穿帮", "人群仪态符合时代"],
    "现实场景(写实)": ["自然光优先, 不打修饰光", "环境音完整保留", "允许画面'不完美'"],
    "奇幻场景": ["物理尺度夸张(巨树/浮岛)", "自洽的生态链", "光源可超自然但有规则"],
    "科幻场景": ["科技有使用痕迹不崭新", "界面信息可读", "空间逻辑服务于世界观"],
    "梦境场景": ["空间连续性可断裂", "熟悉场景的陌生化变形", "光线无来源"],
    "记忆场景": ["色调抽离(过曝或褪色)", "细节选择性清晰", "声音先于画面出现"],
}

# 服化道子模式设计指令
_PROP_DESIGN = {
    "服化道设定": ["每件道具承载一个情感/叙事功能", "材质/年代/磨损程度具体到可拍", "服装色彩与场景主色形成关系"],
    "服装设计": ["服装是穿在身上的前史", "主色/辅色/点缀色 = 60/30/10", "磨损位置符合人物职业"],
    "化妆造型": ["妆面服务于灯光(高清镜头吃妆)", "发型有物理逻辑(风向/湿度)", "伤痕/老化妆效可触"],
    "道具设计": ["道具可被演员真实操作", "特写细节经得起放大", "道具状态随情节演进"],
    "武器设计": ["重量感通过演员身体表现", "磨损/包浆暗示使用历史", "机关结构逻辑自洽"],
    "交通工具设计": ["内饰磨损匹配车龄", "声音特征先行(引擎/铃铛)", "涂装有地域与年代依据"],
    "食品设计": ["热气/油光是生命力", "食用动作设计", "食物与人物关系互文"],
    "日常用品": ["用品即人物习惯的化石", "品牌/年代可辨识或彻底素体", "使用痕迹真实"],
    "特殊道具": ["叙事触发器: 出场即悬念", "可复制多份供拍摄损耗", "机关/发光部件提前测试"],
    "时代道具": ["年代考据: 材质/印刷/工艺", "旧化程度分层(全新库存/常用/废弃)", "避免穿越感穿帮"],
    "未来道具": ["功能可读: 一眼知道用途", "界面光色统一世界观", "保留物理按键的触感"],
    "综合资产卡": ["角色/环境/道具三库联动", "母版资产锁定后批量派生", "跨镜头一致性优先"],
    "参考库生成": ["每类资产 3-5 张参考图", "参考图标注用途(正面锁定/材质参考)", "母版→变体派生链"],
}


# ============================================================
# V14.2: HellGrind 资产库 — 接线真实 asset_registry 引擎
# (修复能力降级: 此前仅 legacy AssetRegistry 节点可用, 默认 13 节点无入口)
# ============================================================
def _hellgrind_names():
    try:
        import asset_registry as _ar
        return sorted(_ar.ASSET_REGISTRY.keys())
    except Exception:
        return ["@roco"]


def _hellgrind_states():
    try:
        import asset_registry as _ar
        states = sorted({s for a in _ar.ASSET_REGISTRY.values() for s in a.states.keys()})
        return ["(默认)"] + states
    except Exception:
        return ["(默认)"]


def _build_hellgrind_asset(kwargs, project, director):
    """HellGrind 资产库 — 真实引擎输出: descriptor/状态变体/voice/behavior/完整prompt块/压测/锁定."""
    import asset_registry as _ar
    # V16.0 需求1: HellGrind 资产名/状态版本支持 🎲 随机
    import random as _r_hg
    name = kwargs.get("HellGrind资产名") or "@roco"
    if name == "🎲 随机":
        name = _r_hg.choice(sorted(_ar.ASSET_REGISTRY.keys()))
    state_raw = kwargs.get("HellGrind状态版本") or "(默认)"
    if state_raw == "🎲 随机":
        _states = sorted({s for a in _ar.ASSET_REGISTRY.values() for s in a.states.keys()})
        state_raw = _r_hg.choice(_states) if _states else "(默认)"
    state = None if state_raw == "(默认)" else state_raw
    do_test = bool(kwargs.get("HellGrind压力测试", True))
    do_lock = bool(kwargs.get("HellGrind锁定", False))

    asset = _ar._get_asset(name)
    if asset is None:
        return f"HellGrind资产库: 未找到资产 {name} (可选: {', '.join(sorted(_ar.ASSET_REGISTRY.keys()))})"

    lines = []
    lines.append("═══════════════════════════════════════════════════════════")
    lines.append(f"【HellGrind 资产库】{name} | 项目: {project} | 导演: {director}")
    lines.append(f"  来源: Higgsfield Hell Grind 生产体系复刻 (descriptor 锁定 + 状态变体 + 压力测试)")
    lines.append("═══════════════════════════════════════════════════════════")
    lines.append("")
    lines.append(f"【Descriptor (锁定描述符, 跨镜头一致性铁律: 一次只改一行)】")
    lines.append(_ar.get_descriptor(name))
    lines.append("")
    if state:
        lines.append(f"【状态变体 · {state}】")
        lines.append(_ar.get_state_descriptor(name, state))
        lines.append("")
    else:
        lines.append(f"【可用状态变体】{', '.join(sorted(asset.states.keys())) or '(无)'}")
        lines.append("")
    if asset.kind == "character":
        lines.append("【Voice Signature (声音签名)】")
        lines.append(_ar.get_voice_signature(name))
        lines.append("")
        lines.append("【Behavior Signature (行为签名)】")
        lines.append(_ar.get_behavior_signature(name))
        lines.append("")
    lines.append("【完整生成 Prompt 块 (可直接注入视频模型)】")
    lines.append(_ar.render_asset_prompt(name, state=state))

    if do_test:
        pt = _ar.pressure_test(name)
        lines.append("")
        lines.append("【压力测试报告 (同帧一致性 + 失败模式检查)】")
        lines.append(f"  轮数: {pt.get('n_rounds', 0)} | 全部通过: {pt.get('all_pass', False)}")
        lines.append(f"  同帧检查: {len(pt.get('same_frame', []))} 项 | 失败模式检查: {len(pt.get('fail_mode_checks', {}))} 项")
        fails = {k: v for k, v in pt.get("fail_mode_checks", {}).items() if not v.get("pass", True)}
        if fails:
            lines.append(f"  未通过项: {', '.join(fails.keys())}")
    if do_lock:
        lr = _ar.lock_asset(name)
        lines.append("")
        lines.append("【锁定报告 (锁定后 descriptor 不可再改 — Higgsfield 铁律)】")
        for k, v in lr.items():
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


class DirectorMasterAsset(DirectorNodeBase):
    """角色/环境/服化道设定节点 — 接收参考图/视频, 输出资产卡."""
    NODE_TYPE = "美术指导"

    @classmethod
    def INPUT_TYPES(cls):
        _R = "🎲 随机"
        return {"required": {
            "资产模式": (ASSET_MODES+[_R], {"default": "角色设定"}),
            "项目名": ("STRING", {"default": "我的电影项目"}),
        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承导演风格/场景/情绪/灵魂/AI"}),
            # V12.6 v6: 参考能力全链路扩展 — 支持多图多视频参考
            "参考图_角色正面": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色正面参考图 (IP-Adapter 正面锁定)"}),
            "参考图_角色侧面": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色侧面参考图 (IP-Adapter 侧面锁定)"}),
            "参考图_角色背面": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 角色背面参考图 (IP-Adapter 背面锁定)"}),
            "参考图_环境母版": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 环境母版图 (锁定场景空间/光影/色调)"}),
            "参考图_道具母版": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 道具母版图 (锁定道具外观/材质)"}),
            "参考图_首帧": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 视频首帧参考图 (图生视频 first_frame)"}),
            "参考图_尾帧": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadImage 输出 — 视频尾帧参考图 (图生视频 last_frame)"}),
            "参考视频_运动母版": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadVideo 输出 — 运动母版视频 (锁定运镜/节奏)"}),
            "参考视频_风格母版": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 LoadVideo 输出 — 风格母版视频 (锁定整体视觉风格)"}),
            # 兼容旧字段
            "参考图路径": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "[兼容] 单一参考图路径 — 旧字段, 新版用上面的多图字段"}),
            "参考视频路径": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "[兼容] 单一参考视频路径 — 旧字段, 新版用上面的多视频字段"}),
            # V13 合并: IMAGE 类型输入槽 (ComfyUI 标准) — 直接接 LoadImage/LoadVideo 的 IMAGE 输出, 优先于 STRING 路径
            "参考图_IMAGE_角色正面": ("IMAGE", {"tooltip": "★ ComfyUI 标准: 接 LoadImage 的 IMAGE 输出 (角色正面)"}),
            "参考图_IMAGE_角色侧面": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (角色侧面)"}),
            "参考图_IMAGE_角色背面": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (角色背面)"}),
            "参考图_IMAGE_环境母版": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (环境母版)"}),
            "参考图_IMAGE_道具母版": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (道具母版)"}),
            "参考图_IMAGE_首帧": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (视频首帧)"}),
            "参考图_IMAGE_尾帧": ("IMAGE", {"tooltip": "接 LoadImage 的 IMAGE 输出 (视频尾帧)"}),
            "参考视频_IMAGE_运动母版": ("IMAGE", {"tooltip": "接 LoadVideo/VHS 的 IMAGE 批次 (运动母版, 多帧)"}),
            "参考视频_IMAGE_风格母版": ("IMAGE", {"tooltip": "接 LoadVideo/VHS 的 IMAGE 批次 (风格母版, 多帧)"}),
            "角色名": ("STRING", {"default": "主角", "tooltip": "角色名称"}),
            "角色年龄": ("STRING", {"default": "30", "tooltip": "角色年龄"}),
            "角色性别": ([_R,"男", "女", "不限"], {"default": "男"}),
            "角色性格": ("STRING", {"default": "沉默寡言, 内敛, 用行动表达", "multiline": True}),
            "角色外貌": ("STRING", {"default": "短发, 瘦削, 颧骨高, 眼窝深, 右手食指有老茧", "multiline": True}),
            "角色服装": ("STRING", {"default": "深蓝色工作服(褪色), 灰色秋衣, 布鞋", "multiline": True}),
            "环境类型": ([_R,"室内", "室外", "太空", "水下", "虚拟"], {"default": "室内"}),
            "环境描述": ("STRING", {"default": "厨房8平米, 灶台+砧板+碗柜+餐桌+窗", "multiline": True}),
            "服化道描述": ("STRING", {"default": "旧信(泛黄), 凤梨罐头(过期), 钢笔(没墨水), 收音机", "multiline": True}),
            "视觉风格": ([_R,"写实", "日漫", "美漫", "3D CG", "水彩", "油画", "赛璐璐", "水墨"], {"default": "写实"}),
            # V14.2: HellGrind 资产库输入 (仅 HellGrind资产库 模式使用); V16.0 需求1: 加 🎲 随机
            "HellGrind资产名": (["🎲 随机"]+_hellgrind_names(), {"default": "@roco",
                "tooltip": "V14.2: Hell Grind 资产库 — 5角色(@roco/@jax/@rein/@lulu/@kaine) + 2场景(@loc_*) + 1道具(@crystal_sword); 🎲 随机"}),
            "HellGrind状态版本": (["🎲 随机"]+_hellgrind_states(), {"default": "(默认)",
                "tooltip": "V14.2: 资产状态变体 (blood/injured/wet/clothed_change/night/rain...); 🎲 随机"}),
            "HellGrind压力测试": ("BOOLEAN", {"default": True,
                "tooltip": "V14.2: 运行同帧一致性+失败模式压力测试"}),
            "HellGrind锁定": ("BOOLEAN", {"default": False,
                "tooltip": "V14.2: 锁定 descriptor (Higgsfield 铁律: 锁定后不可再改)"}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("资产设定", "参考库JSON")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/资产"

    def build(self, **kwargs):
        import json as _json
        mode = kwargs.get("资产模式", "角色设定")
        # V16.0 需求1: 模式选择器支持 🎲 随机
        if mode == "🎲 随机":
            import random as _r
            mode = _r.choice(ASSET_MODES)
        if mode not in ASSET_MODES: mode = "角色设定"
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
        project = kwargs.get("项目名", "我的电影项目")
        director = core.get("_导演风格", "王家卫") if core else "王家卫"
        scene = core.get("_场景描述", "") if core else ""
        mood = core.get("_情绪基调", "") if core else ""
        visual_style = kwargs.get("视觉风格", "写实")

        # V13 合并: 收集多图多视频参考 — IMAGE 张量优先(落盘返回文件名), 否则 STRING 路径
        ref_images = {
            "角色正面": resolve_ref(kwargs, "参考图_IMAGE_角色正面", "参考图_角色正面", "角色正面"),
            "角色侧面": resolve_ref(kwargs, "参考图_IMAGE_角色侧面", "参考图_角色侧面", "角色侧面"),
            "角色背面": resolve_ref(kwargs, "参考图_IMAGE_角色背面", "参考图_角色背面", "角色背面"),
            "环境母版": resolve_ref(kwargs, "参考图_IMAGE_环境母版", "参考图_环境母版", "环境母版"),
            "道具母版": resolve_ref(kwargs, "参考图_IMAGE_道具母版", "参考图_道具母版", "道具母版"),
            "首帧": resolve_ref(kwargs, "参考图_IMAGE_首帧", "参考图_首帧", "首帧"),
            "尾帧": resolve_ref(kwargs, "参考图_IMAGE_尾帧", "参考图_尾帧", "尾帧"),
        }
        ref_videos = {}
        for _vtag, _ikey, _pkey in (("运动母版", "参考视频_IMAGE_运动母版", "参考视频_运动母版"),
                                     ("风格母版", "参考视频_IMAGE_风格母版", "参考视频_风格母版")):
            _vid = kwargs.get(_ikey)
            if _vid is not None:
                _frames = image_batch_to_ref_paths(_vid, _vtag)
                ref_videos[_vtag] = ",".join(_frames) if _frames else ""
            if not ref_videos.get(_vtag):
                ref_videos[_vtag] = (kwargs.get(_pkey) or "").strip()
        # 兼容旧字段
        old_ref_img = (kwargs.get("参考图路径") or "").strip()
        old_ref_vid = (kwargs.get("参考视频路径") or "").strip()
        if old_ref_img and not any(ref_images.values()):
            ref_images["角色正面"] = old_ref_img
        if old_ref_vid and not any(ref_videos.values()):
            ref_videos["运动母版"] = old_ref_vid

        # 参考库 JSON (传递到下游 VideoRouter 节点)
        ref_library = {
            "项目": project, "导演": director, "视觉风格": visual_style,
            "参考图": {k: v for k, v in ref_images.items() if v},
            "参考视频": {k: v for k, v in ref_videos.items() if v},
            "统计": {
                "参考图总数": sum(1 for v in ref_images.values() if v),
                "参考视频总数": sum(1 for v in ref_videos.values() if v),
            }
        }
        ref_json_str = _json.dumps(ref_library, ensure_ascii=False, indent=2)

        # 参考库文本块 (显示在资产设定输出里)
        ref_block = ""
        if any(ref_images.values()):
            ref_block += "\n【多图参考库 (V12.6 v6 全链路扩展)】\n"
            for tag, path in ref_images.items():
                if path:
                    if "首帧" in tag: ref_block += f"  {tag}: {path} → 图生视频 first_frame 输入\n"
                    elif "尾帧" in tag: ref_block += f"  {tag}: {path} → 图生视频 last_frame 输入\n"
                    elif "正面" in tag: ref_block += f"  {tag}: {path} → IP-Adapter 正面锁定 (面部骨骼+表情)\n"
                    elif "侧面" in tag: ref_block += f"  {tag}: {path} → IP-Adapter 侧面锁定 (轮廓特征)\n"
                    elif "背面" in tag: ref_block += f"  {tag}: {path} → IP-Adapter 背面锁定 (服装后片)\n"
                    elif "环境" in tag: ref_block += f"  {tag}: {path} → 场景母版 (空间布局/光影/色调锁定)\n"
                    elif "道具" in tag: ref_block += f"  {tag}: {path} → 道具母版 (外观/材质/年代锁定)\n"
        if any(ref_videos.values()):
            ref_block += "\n【多视频参考库】\n"
            for tag, path in ref_videos.items():
                if path:
                    if "运动" in tag: ref_block += f"  {tag}: {path} → 锁定运镜/节奏/推拉速度\n"
                    elif "风格" in tag: ref_block += f"  {tag}: {path} → 锁定整体视觉风格 (色彩/质感/调度)\n"

        # V13.1: 核心数据包继承 — 从 Core 场景解析角色/物件/地点, 下游不再重复输入
        try:
            from aggregator.scene_engine import parse_scene as _parse_scene
            _parsed = _parse_scene(scene) if scene else {}
        except Exception:
            _parsed = {}
        core_chars = (_parsed.get("characters") or []) if _parsed else []
        core_loc = (_parsed.get("location") or "") if _parsed else ""
        core_objects = [x for x in ((_parsed.get("objects") or []) if _parsed else []) if x]
        key_props_core = ((core.get("_关键道具", "") if core else "") or "").strip()
        _seed_base = f"{scene}_{director}_{mood}_{mode}_{project}"

        if mode == "HellGrind资产库":
            # V14.2: 真实 asset_registry 引擎 (descriptor/状态/voice/behavior/压测/锁定)
            main = _build_hellgrind_asset(kwargs, project, director)
        elif mode in _CHARACTER_MODES:
            name = (kwargs.get("角色名") or "主角").strip() or "主角"
            age = kwargs.get("角色年龄", "30")
            gender = kwargs.get("角色性别", "男")
            personality = (kwargs.get("角色性格") or "").strip()
            appearance = (kwargs.get("角色外貌") or "").strip()
            costume = (kwargs.get("角色服装") or "").strip()
            role_hint = _CHAR_ROLE_HINT.get(mode, "人物设定")

            if mode == "群像角色":
                # 群像: 核心场景解析出的全部角色, 每人一张卡 (用户输入作为首卡)
                cast = []
                if name and name != "主角":
                    cast.append(name)
                for c in core_chars:
                    if c not in cast:
                        cast.append(c)
                if not cast:
                    cast = [name]
                cards = []
                for i, cname in enumerate(cast[:5]):
                    cseed = f"{_seed_base}_{cname}_{i}"
                    cp = personality if (i == 0 and personality) else _aseed_choice(_PERSONA_TRAITS, cseed + "_p")
                    ca = appearance if (i == 0 and appearance) else _aseed_choice(_LOOK_TRAITS, cseed + "_l")
                    cw = costume if (i == 0 and costume) else _aseed_choice(_WARD_TRAITS, cseed + "_w")
                    relation = "主角" if i == 0 else _aseed_choice(
                        ["与主角价值观对照", "主角的情感软肋", "推动关键转折", "见证者/叙述者", "暗线对手"], cseed + "_r")
                    cards.append(
                        f"  ◆ {cname}\n"
                        f"    定位: {'视点人物' if i == 0 else relation}\n"
                        f"    性格: {cp}\n    外貌: {ca}\n    服装: {cw}\n"
                        f"    生成提示词: {cname}, {ca}, {cw}, {visual_style}风格, {mood}情绪"
                    )
                main = (
                    f"群像角色卡 · {project}  [{mode}]\n"
                    f"  叙事定位: {role_hint}\n"
                    f"  人物网络: {' / '.join(cast[:5])}\n"
                    f"  出场场景: {scene or core_loc or '未指定'}\n"
                    f"  情绪基调: {mood}\n\n" + "\n\n".join(cards) + "\n\n"
                    f"  一致性策略: 每个角色独立参考图锁定, 同框镜头用 IP-Adapter 多主体权重分配\n"
                    f"  导演风格: {director}"
                )
            else:
                # 单角色: 默认名"主角"时继承核心场景角色 (反派取末位, 其余取首位)
                if name == "主角" and core_chars:
                    name = core_chars[-1] if (mode == "反派角色" and len(core_chars) >= 2) else core_chars[0]
                if not personality:
                    personality = _aseed_choice(_PERSONA_TRAITS, _seed_base + "_p")
                    if mode == "反派角色":
                        personality = _aseed_choice(
                            ["礼貌周到, 狠在不动声色", "信念坚定, 只是站错了位置", "控制欲极强, 恐惧失控",
                             "魅力型操纵者, 从不提高嗓门", "旧伤驱动的偏执"], _seed_base + "_pv")
                if not appearance:
                    appearance = _aseed_choice(_LOOK_TRAITS, _seed_base + "_l")
                if not costume:
                    costume = _ERA_WARD.get(mode) or _aseed_choice(_WARD_TRAITS, _seed_base + "_w")
                prop_bind = ""
                if core_objects or key_props_core:
                    _bind_obj = core_objects[0] if core_objects else key_props_core.split(",")[0].split("(")[0].strip()
                    prop_bind = f"  道具绑定: {_bind_obj} — 此物件是人物情感的外化, 出场必带\n"
                main = (
                    f"角色卡 · {name}  [{mode}]\n"
                    f"  叙事定位: {role_hint}\n"
                    f"  姓名: {name}\n  年龄: {age}\n  性别: {gender}\n"
                    f"  性格: {personality}\n"
                    f"  外貌: {appearance}\n"
                    f"  服装: {costume}\n"
                    f"  出场场景: {scene or core_loc or '未指定'}\n"
                    f"  情绪基调: {mood}\n"
                    f"{prop_bind}"
                    f"  视觉风格: {visual_style}\n"
                    f"  导演风格: {director}\n\n"
                    f"  三视图锚定 (IP-Adapter 用):\n"
                    f"    正面: {name}正面半身, {appearance}, {costume}, {visual_style}风格\n"
                    f"    侧面: {name}侧面半身, 轮廓特征\n"
                    f"    背面: {name}背面半身, 服装后片完整\n"
                    f"    表情: 中性 + 3 种情绪变体 (微笑/凝重/惊讶)\n"
                    f"  一致性策略: 加载 {ref_library['统计']['参考图总数']} 张参考图, 锁定面部骨骼+服装配色\n"
                    f"  生成提示词: {name}, {age}岁{gender}性, {appearance}, {costume}, {visual_style}风格, {mood}情绪"
                )
        elif mode in _ENV_MODES:
            env_type = kwargs.get("环境类型", "室内")
            env_desc = (kwargs.get("环境描述") or "").strip()
            # 继承: 用户未填环境描述时用 Core 场景
            if not env_desc:
                env_desc = scene or core_loc or ""
            design = _ENV_DESIGN.get(mode, _ENV_DESIGN["环境设定"])
            design_block = "\n".join(f"    {i+1}. {d}" for i, d in enumerate(design))
            props_in_scene = "、".join(core_objects[:4]) if core_objects else (key_props_core.split(",")[0].strip() if key_props_core else "无")
            main = (
                f"环境卡 · {project}  [{mode}]\n"
                f"  环境类型: {env_type}\n  环境描述: {env_desc}\n"
                f"  地点: {core_loc or '按场景描述'}\n"
                f"  场景内道具: {props_in_scene}\n"
                f"  视觉风格: {visual_style}\n  导演风格: {director}\n  情绪基调: {mood}\n\n"
                f"  【{mode}设计指令】\n{design_block}\n\n"
                f"  环境锚定(场景母版):\n    主色调: 按导演风格({director})定\n    光影: 按情绪({mood})定\n    关键道具位置: 按场景描述定\n"
                f"  一致性策略: 加载 {ref_library['统计']['参考图总数']} 张环境母版, 跨镜头空间/光影/色调锁定\n"
                f"  生成提示词: {env_type}场景, {env_desc}, {visual_style}风格, {director}导演, {mood}情绪"
            )
        else:  # 服化道设定及全部子模式
            costume_desc = (kwargs.get("服化道描述") or "").strip()
            # 继承: 用户未填时用 Core 关键道具 + 场景物件
            if not costume_desc:
                _merged = []
                if key_props_core:
                    _merged.append(key_props_core)
                if core_objects:
                    _merged.extend([o for o in core_objects[:4] if o not in key_props_core])
                costume_desc = ", ".join(_merged) if _merged else ""
            design = _PROP_DESIGN.get(mode, _PROP_DESIGN["服化道设定"])
            design_block = "\n".join(f"    {i+1}. {d}" for i, d in enumerate(design))
            char_bind = f"  角色绑定: {'、'.join(core_chars[:3])}\n" if core_chars else ""
            main = (
                f"服化道卡 · {project}  [{mode}]\n"
                f"  服化道清单: {costume_desc or '未指定'}\n"
                f"{char_bind}"
                f"  场景: {scene or core_loc or '未指定'}\n"
                f"  视觉风格: {visual_style}\n  导演风格: {director}\n  情绪基调: {mood}\n\n"
                f"  【{mode}设计指令】\n{design_block}\n\n"
                f"  一致性策略: 加载 {ref_library['统计']['参考图总数']} 张道具母版, 跨镜头外观/材质锁定\n"
                f"  生成提示词: {costume_desc or '核心道具'}, {visual_style}风格, 具体材质纹理, {mood}情绪"
            )

        if ref_block:
            main += ref_block

        main += self._director_block(director)

        # V14.3-MERGED: Higgsfield 6 份项目级记忆文档 (asset_registry_data 复活接线)
        try:
            from asset_registry_data import get_six_documents_summary
            _six = get_six_documents_summary()
            if _six:
                main += "\n\n" + str(_six)
        except Exception as _sd_e:
            import sys as _sd_s
            _sd_s.stderr.write(f"[DirectorMaster] 6文档注入降级: {type(_sd_e).__name__}\n")

        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url:
            main = self._ensure_ai_output(main,
                {"node_type": "美术指导", "mode": mode, "director": director, "scene": scene, "mood": mood,
                 "ref_images_count": ref_library['统计']['参考图总数'],
                 "ref_videos_count": ref_library['统计']['参考视频总数']},
                api_url, api_key, ai_model)

        from aggregator.pro_format import strip_decor
        return (strip_decor(main), ref_json_str)
