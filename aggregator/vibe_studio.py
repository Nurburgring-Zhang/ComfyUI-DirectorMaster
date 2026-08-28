# -*- coding: utf-8 -*-
"""
③ DirectorMasterVibe — 创意氛围 (23 合 1)
==========================================
23 模式: 概念立项/主题哲学/世界设定/服化道/表演指导/VFX特效/MV导演/调色/剪辑/迭代/质量QA/绘本/互动剧/漫剧分镜/市场受众分析
        + 电商套图/海报设计/品牌设计/PPT设计/逻辑关系图设计/三视图设计/爆炸拆解图设计/流水线图设计
V14.2: 市场受众分析 接线真实 market_audience_pro 引擎 (8类型受众画像+5档期+3定位+票房预测),
       此前该能力在 (V14 时代默认 13 节点下) 无入口 (能力降级), 现为 17 默认节点之一。
V14.3-MERGED: 8 设计模式复活接线 (modes_design 孤儿库) — 电商/海报/品牌/PPT/图表,
       修复原分叉适配器参数不全导致的静默降级, 全部参数真实传递。
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy, resolve_dropdown, derive_seed

VIBE_MODES = ["概念立项","主题哲学","世界设定","服化道","表演指导","VFX特效","MV导演","调色","剪辑","迭代","质量QA","绘本","互动剧","漫剧分镜","市场受众分析",
              "电商套图","海报设计","品牌设计","PPT设计","逻辑关系图设计","三视图设计","爆炸拆解图设计","流水线图设计"]

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


# ============================================================
# V14.2: 市场受众分析 — 接线真实 market_audience_pro 引擎
# (修复能力降级: 此前该能力仅存在于 legacy 节点, V14 时代默认 13 节点无入口)
# ============================================================
_MARKET_GENRE_KEYWORDS = {
    "动作": ["动作", "武侠", "打斗", "拳", "枪", "警", "追", "特工", "刺客", "保镖", "格斗", "江湖"],
    "喜剧": ["喜剧", "搞笑", "笑话", "笑", "囧", "整蛊", "欢喜", "乌龙"],
    "爱情": ["爱情", "恋爱", "恋人", "初恋", "告白", "分手", "婚礼", "相亲", "暗恋", "情侣"],
    "悬疑": ["悬疑", "谜", "案件", "凶", "侦探", "真相", "失踪", "秘密", "阴谋", "推理", "绑架"],
    "科幻": ["科幻", "太空", "未来", "AI", "机器人", "外星", "飞船", "赛博", "穿越", "星际", "人工智能"],
    "动画": ["动画", "动漫", "绘本", "儿童", "童话", "魔法", "萌", "奇幻冒险", "精灵"],
    "战争": ["战争", "历史", "军队", "战役", "将军", "帝国", "王朝", "古装", "史诗", "战场"],
    "现实主义": ["现实", "小人物", "社会", "家庭", "亲子", "留守", "疾病", "职场", "打工", "故乡"],
}


def _infer_market_genre(scene, core, mood):
    """从核心数据包/场景描述推断类型片 (8 类). 返回 (genre, 推断依据)."""
    text = " ".join([
        scene or "",
        (core.get("_场景描述", "") if core else ""),
        (core.get("_类型", "") if core else ""),
        (core.get("_故事梗概", "") if core else ""),
        mood or "",
    ])
    for genre, kws in _MARKET_GENRE_KEYWORDS.items():
        hit = [k for k in kws if k in text]
        if hit:
            return genre, "关键词命中: " + "/".join(hit[:3])
    return "现实主义", "无明显类型关键词, 按题材默认 (现实主义)"


def _infer_release_period(genre):
    """按类型的最佳档期推断 (数据来自 RELEASE_PERIODS_5.best_genres)."""
    if genre == "爱情":
        return "非档期"  # 情人节/七夕 属非档期分线发行
    if genre == "战争":
        return "国庆档"
    if genre == "动画":
        return "春节档"
    return "暑期档"


def _infer_market_position(creative_direction):
    """从创意方向推断市场定位."""
    d = creative_direction or ""
    if any(k in d for k in ["短剧", "小程序", "爆款反转", "搞笑整蛊", "脑洞"]):
        return "黑马"
    if any(k in d for k in ["商业类型片", "网剧爆款", "战争史诗", "仙侠奇幻"]):
        return "头部"
    return "腰部"


def _build_market_audience(scene, director, mood, core, kwargs):
    """市场受众分析 — 真实引擎输出: 受众画像/档期策略/市场定位/票房预测."""
    from market_audience_pro import (
        predict_box_office, GENRE_AUDIENCE_8, RELEASE_PERIODS_5, MARKET_POSITION_3,
    )
    core = core or {}
    # 1. 类型/档期/定位: 用户显式选择优先, 否则自动推断 (V16.0 需求1: 支持 🎲 随机; V16.3 种子驱动)
    def _rnd_mkt(v, opts, domain):
        if v == "🎲 随机":
            return resolve_dropdown(v, None, [o for o in opts if o not in ("🎲 随机", "auto")],
                                    seed=derive_seed(core.get("_随机种子"), domain)) or (opts[0] if opts else v)
        return v
    genre = _rnd_mkt((kwargs.get("类型片市场") or "auto").strip(), list(GENRE_AUDIENCE_8.keys()), "市场类型片")
    period = _rnd_mkt((kwargs.get("档期策略") or "auto").strip(), list(RELEASE_PERIODS_5.keys()), "市场档期")
    position = _rnd_mkt((kwargs.get("市场定位") or "auto").strip(), list(MARKET_POSITION_3.keys()), "市场定位")
    genre_basis, period_basis, position_basis = "", "", ""
    if genre == "auto" or genre not in GENRE_AUDIENCE_8:
        genre, genre_basis = _infer_market_genre(scene, core, mood)
    else:
        genre_basis = "用户指定"
    if period == "auto" or period not in RELEASE_PERIODS_5:
        period = _infer_release_period(genre)
        period_basis = "按类型最佳档期推断"
    else:
        period_basis = "用户指定"
    if position == "auto" or position not in MARKET_POSITION_3:
        position = _infer_market_position(kwargs.get("创意方向", ""))
        position_basis = "按创意方向推断"
    else:
        position_basis = "用户指定"

    # 2. 真实票房预测引擎 (4 维评分输入)
    result = predict_box_office(
        genre=genre, period=period, position=position,
        director_popularity=float(kwargs.get("导演知名度", 0.7)),
        cast_popularity=float(kwargs.get("演员阵容", 0.6)),
        marketing_budget=float(kwargs.get("营销预算", 0.5)),
        quality_score=float(kwargs.get("质量评分", 0.7)),
    )
    gi, pi, po = result["genre_info"], result["period_info"], result["position_info"]

    # 3. 渲染完整报告
    lines = []
    lines.append("═══════════════════════════════════════════════════════════")
    lines.append(f"【市场受众分析】项目: {kwargs.get('项目名', '电影项目')} | 导演: {director}")
    lines.append(f"  输入场景: {scene or '(未提供)'}")
    lines.append("═══════════════════════════════════════════════════════════")
    lines.append("")
    lines.append(f"【定位结论】类型: {gi['name_zh']} ({genre_basis}) | 档期: {pi['name_zh']} ({period_basis}) | 定位: {po['name_zh']} ({position_basis})")
    lines.append("")
    lines.append("【受众画像】(数据源: 2024-2025 中国电影市场报告)")
    lines.append(f"  主要受众: {gi['primary_audience']}")
    lines.append(f"  次要受众: {gi['secondary_audience']}")
    lines.append(f"  市场份额: {gi['market_share']}")
    lines.append(f"  关键驱动: {' / '.join(gi['key_drivers'])}")
    lines.append(f"  对标作品: {' / '.join(gi['examples'])}")
    lines.append(f"  类型风险: {gi['risk']}")
    lines.append("")
    lines.append("【档期策略】")
    lines.append(f"  档期: {pi['name_zh']} | 持续: {pi['duration']}")
    lines.append(f"  竞争强度: {pi['competition']}")
    lines.append(f"  最佳类型: {' / '.join(pi['best_genres'])}")
    lines.append(f"  档期受众: {pi['audience']}")
    lines.append(f"  票房占比: {pi['box_office_share']}")
    lines.append(f"  发行策略: {pi['strategy']}")
    lines.append("")
    lines.append("【市场定位与打法】")
    lines.append(f"  定位: {po['name_zh']}")
    lines.append(f"  投资规模: {po['investment']} | 票房目标: {po['box_office_target']}")
    lines.append(f"  份额目标: {po['share_target']}")
    for i, s in enumerate(po["strategies"], 1):
        lines.append(f"  策略{i}: {s}")
    lines.append(f"  定位案例: {' / '.join(po['examples'])}")
    lines.append("")
    lines.append("【票房预测】(4 维加权: 质量35% + 导演20% + 演员15% + 营销15% + 类型15% + 档期加分)")
    lines.append(f"  输入: 质量评分={kwargs.get('质量评分', 0.7)} | 导演知名度={kwargs.get('导演知名度', 0.7)} | 演员阵容={kwargs.get('演员阵容', 0.6)} | 营销预算={kwargs.get('营销预算', 0.5)}")
    lines.append(f"  综合评分: {result['score']:.3f}")
    lines.append(f"  预估票房: {result['box_office_estimate_yi']:.2f} 亿")
    lines.append(f"  风险等级: {result['risk_level']}")
    lines.append(f"  决策建议: {result['recommendation']}")
    lines.append("")
    lines.append("【受众-类型-档期-营销 4 维矩阵】")
    lines.append(f"  受众 × 类型: {gi['primary_audience']} ←→ {gi['name_zh']} (驱动: {'/'.join(gi['key_drivers'][:2])})")
    lines.append(f"  类型 × 档期: {gi['name_zh']} 在 {pi['name_zh']} 属 {'最佳类型' if genre in pi['best_genres'] else '可上映类型'}")
    lines.append(f"  档期 × 营销: {pi['strategy']}")
    lines.append(f"  定位 × 受众: {po['name_zh']} 打法面向 {pi['audience']}")
    return "\n".join(lines)


def _build_concept_template(scene, director, mood, core):
    """概念立项 — V13.3 场景驱动 (从核心数据包提取主题/冲突/道具生成真实立项)."""
    core = core or {}
    p = _parse_scene_safe(scene)
    chars = p.get("characters") or ["主角"]
    objs = p.get("objects") or ["关键道具"]
    loc = p.get("location") or "场景"
    theme = core.get("_主题词", "记忆")
    conflict = core.get("_核心冲突", "家庭")
    props = core.get("_关键道具", "") or "、".join(objs)
    promise = core.get("_观众承诺", "感动落泪")
    ref = core.get("_对标作品", "")
    c1 = chars[0]
    obj = objs[0]
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【概念立项】导演: {director} | 场景: {scene}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"一句话概念: 在{loc}, {c1}因为{obj}被迫面对'{theme}'——{conflict}在此刻被点燃.\n"
        f"类型: {conflict}/剧情 | 情绪基调: {mood}\n"
        f"商业卖点: 每个观众都能在{c1}的处境里, 看见自己没说出口的那件事.\n"
        f"情感锚点: {core.get('_导演意图_观众应感到', '说不出口的情感')}\n"
        f"核心道具: {props}\n"
        f"观众承诺: {promise}\n"
        f"对标作品: {ref or '按导演风格与类型匹配'}\n"
        f"独特卖点: 情感不靠台词堆, 靠{obj}与沉默承载, 让'{theme}'可被看见."
    )

def _build_theme_template(scene, director, mood, core):
    """主题哲学 — V13.3 场景驱动."""
    core = core or {}
    p = _parse_scene_safe(scene)
    objs = p.get("objects") or ["关键道具"]
    theme = core.get("_主题词", "记忆")
    conflict = core.get("_核心冲突", "家庭")
    subtext = core.get("_潜文本_情感", "") or "真正想说的, 一直没说出来"
    obj = objs[0]
    return (
        f"【主题哲学】导演: {director}\n\n"
        f"主题句: 关于'{theme}'——它不会消失, 只会在{obj}里安静地等着.\n"
        f"道德困境: {conflict}的两难——说出来会破坏, 不说会积压.\n"
        f"哲学内核: {theme}是保护, 还是会变成一种伤害?\n"
        f"主题类型: {theme} | {conflict}\n"
        f"隐喻: {obj} = 未完成的'{theme}', 一直在场, 一直未被正视.\n"
        f"潜文本: {subtext}\n"
        f"结尾留白: 不给答案, 把'{theme}'的判断权交还给观众."
    )

def _build_world_template(scene, director, mood, core):
    """世界设定 — V13.3 场景驱动 (从场景解析 时间/空间/视觉/声音锚点)."""
    core = core or {}
    p = _parse_scene_safe(scene)
    loc = p.get("location") or "场景"
    t = p.get("time") or "日"
    weather = p.get("weather") or ""
    objs = p.get("objects") or ["关键道具"]
    chars = p.get("characters") or ["主角"]
    era = _detect_era_safe(scene)
    year = core.get("_时间年代", "")
    visual = core.get("_视觉调性", "写实")
    obj_str = "、".join(objs[:4])
    # 年代适配的声音锚点
    sound_anchor = {
        "古装": "风声+衣袂+远处更鼓, 无现代音",
        "科幻": "舱体低频嗡鸣+循环气流+提示音, 极简",
        "复古": "环境声+老物件声(收音机/钟摆), 无配乐",
        "现代": "环境底噪+生活声, 克制配乐",
    }.get(era, "环境底噪+生活声, 克制配乐")
    return (
        f"【世界设定】导演: {director}\n\n"
        f"时间: {year} · {t}{(' · '+weather) if weather else ''}\n"
        f"空间: {loc}——按场景描述还原真实尺度与陈设\n"
        f"时代质感: {era}\n"
        f"社会规则: 由'{core.get('_核心冲突','关系')}'决定人物间的相处方式与禁忌.\n"
        f"登场人物: {'、'.join(chars[:4])}\n"
        f"视觉锚点: {obj_str} 的质感与光, 视觉调性={visual}.\n"
        f"声音锚点: {sound_anchor}\n"
        f"主色60%: 按{visual}定基调 | 辅色30%: 按情绪({mood})定 | 点缀色10%: {objs[0]}的颜色"
    )

def _build_costume_template(scene, director, mood, core):
    """服化道 — V13.3 场景驱动 (按年代+角色+道具生成)."""
    core = core or {}
    p = _parse_scene_safe(scene)
    chars = p.get("characters") or ["主角"]
    objs = p.get("objects") or ["关键道具"]
    era = _detect_era_safe(scene)
    year = core.get("_时间年代", "")
    props = core.get("_关键道具", "") or "、".join(objs)
    # 年代服装基调
    costume_base = {
        "古装": "宽袖长袍/束腰, 布料粗粝有垂感, 配色按身份等级",
        "科幻": "无缝功能面料, 哑光, 隐藏接口, 有使用磨损",
        "复古": "洗旧但整洁, 低饱和, 有年代品牌/剪裁痕迹",
        "现代": "当代成衣, 有生活褶皱与职业痕迹",
    }.get(era, "当代成衣, 有生活褶皱与职业痕迹")
    char_lines = []
    for i, c in enumerate(chars[:3]):
        char_lines.append(f"{c}: {costume_base}, 细节随角色前史磨损.")
    return (
        f"【服化道】导演: {director}\n\n"
        f"时代: {year} · {era}\n"
        + "\n".join(char_lines) + "\n"
        f"材质重点: 按{era}年代真实材质, 强调磨损/褪色/使用痕迹.\n"
        f"色彩方案: 低饱和, 按情绪({mood})定冷暖, 点缀色来自{objs[0]}.\n"
        f"关键道具: {props}\n"
        f"每件道具叙事功能: 各自承载一段未说出的'{core.get('_主题词','情感')}'."
    )

def _build_comic_template(scene, director, mood, core):
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【漫剧分镜】导演: {director} | 日漫分镜 | 8页×5格\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"第1页·格1(全景): 厨房外景, 雨夜, 窗户透出暖光. 拟声词: 淅沥.\n"
        f"第1页·格2(中景): 父亲切菜, 背影. 速度线: 刀起刀落.\n"
        f"第1页·格3(近景): 女儿刷手机, 屏幕光映脸. 对话框: '...'(省略号).\n"
        f"第1页·格4(特写): 刀尖抵砧板, 停了. 拟声词: 嗒.\n"
        f"第1页·格5(留白): 窗外的雨, 半页留白. 字幕: 第1页·沉默.\n\n"
        f"第2页·格1(特写): 女儿从抽屉翻出信. 视线引导: 从上至下.\n"
        f"第2页·格2(近景): 信纸特写—泛黄, 笔迹模糊, 署名'妈妈'.\n"
        f"第2页·格3(近景): 女儿抬头, 眼神从信移向父亲. 集中线: 聚向父亲背影.\n"
        f"第2页·格4(中景): 父亲擦灶台, 手停了一下.\n"
        f"第2页·格5(留白): 凤梨罐头, 桌子中央, 半页留白.\n\n"
        f"...至第8页, 节奏: 首格全景→中段近景→末格特写/留白.\n"
        f"阅读方向: 从右至左从上至下(日漫). 格框形状: 规整矩形+少量破格.\n"
        f"线条: 中细线1-2px. 对白密度: 0.5. 拟声词: 开."
    )

# V13 合并: MV/绘本/漫剧 接线 legacy 专业引擎 (修复空壳模式)
def _core_extras(core):
    """V13 修复 (B-P0): 从核心数据包提取 关键道具/潜文本/导演意图, 透传给 legacy 引擎修空变量."""
    core = core or {}
    return {
        "关键道具": core.get("_关键道具", ""),
        "潜文本_情感": core.get("_潜文本_情感", ""),
        "导演意图_观众应感到": core.get("_导演意图_观众应感到", ""),
    }


def _build_mv_engine(scene, director, mood, core):
    """MV导演 — 接线 mv_pro 引擎 (BPM + 七段音乐结构 + 节拍剪辑映射)."""
    try:
        from mv_pro import MvPro
        out = MvPro().build_mv(场景描述=scene, 导演风格=director, 情绪基调=mood, 启用反AI规则=True,
                               **_core_extras(core))
        main = out[0] if isinstance(out, (tuple, list)) else str(out)
        if main and len(main) > 200:
            return main
    except Exception:
        pass
    return _generic_vibe_template(scene, director, mood, core, "MV导演")


def _build_book_engine(scene, director, mood, core):
    """绘本 — 接线 picture_book_pro 引擎 (年龄适配 + 分页 + 画面描述)."""
    try:
        from picture_book_pro import PictureBookPro
        out = PictureBookPro().build_book(场景描述=scene, 导演风格=director, 情绪基调=mood, 启用反AI规则=True,
                                          **_core_extras(core))
        main = out[0] if isinstance(out, (tuple, list)) else str(out)
        if main and len(main) > 200:
            return main
    except Exception:
        pass
    return _generic_vibe_template(scene, director, mood, core, "绘本")


def _build_comic_engine(scene, director, mood, core):
    """漫剧分镜 — 接线 comic_drama_pro 引擎 (分格 + 对话框 + 拟声词 + 视线引导)."""
    try:
        from comic_drama_pro import ComicDramaPro
        out = ComicDramaPro().build_comic(
            场景描述=scene, 导演风格=director, 漫剧风格="日漫分镜", 页数=8, 每页格数=5,
            情绪基调=mood, 对白密度=0.5, 拟声词使用=True, 启用反AI规则=True,
            **_core_extras(core))
        main = out[0] if isinstance(out, (tuple, list)) else str(out)
        if main and len(main) > 200:
            return main
    except Exception:
        pass
    return _build_comic_template(scene, director, mood, core)


# V14.3-MERGED: 设计类 8 模式复活接线 (modes_design 孤儿库) — 电商/海报/品牌/PPT/图表
# 修复原 V14.1-clean 分叉适配器只传 6/13 个必填参数导致 100% 静默降级的缺陷 — 全参数真实传递。
_DESIGN_PHOTO_MODES = {"电商套图", "海报设计", "品牌设计"}


def _build_design_adapter(design_mode):
    def _builder(scene, director, mood, core):
        try:
            from modes_design import _build_design_system_prompt, _build_design_user_prompt
            core = core or {}
            p = _parse_scene_safe(scene)
            chars = p.get("characters") or []
            objs = p.get("objects") or []
            loc = p.get("location") or ""
            topic = str(scene or "")[:80] or "未命名产品"
            subject = chars[0] if chars else (objs[0] if objs else "")
            style = "商业摄影" if design_mode in _DESIGN_PHOTO_MODES else "扁平矢量"
            color_tone = str(core.get("_视觉调性", "") or "") or ("品牌主色" if design_mode == "品牌设计" else "高对比")
            sys_p = _build_design_system_prompt(
                design_mode, topic, subject, loc, 4, style, color_tone,
                "", "", "", "", "", [])
            user_p = _build_design_user_prompt(
                design_mode, topic, subject, loc, 4, style, color_tone,
                "", "", "", "", "")
            return (f"【{design_mode} · 设计提示词系统】导演: {director} | 情绪基调: {mood}\n\n{sys_p}\n\n"
                    f"【{design_mode} · 执行指令】\n{user_p}")
        except Exception as _de:
            import sys as _ds
            _ds.stderr.write(f"[DirectorMaster] 设计模式降级 ({design_mode}): {type(_de).__name__}\n")
            return f"【{design_mode}】设计模式生成降级: {type(_de).__name__} (modes_design 调用失败)"
    return _builder


TEMPLATES = {
    "概念立项": _build_concept_template,
    "主题哲学": _build_theme_template,
    "世界设定": _build_world_template,
    "服化道": _build_costume_template,
    "漫剧分镜": _build_comic_engine,
    "MV导演": _build_mv_engine,
    "绘本": _build_book_engine,
    "电商套图": _build_design_adapter("电商套图"),
    "海报设计": _build_design_adapter("海报设计"),
    "品牌设计": _build_design_adapter("品牌设计"),
    "PPT设计": _build_design_adapter("PPT设计"),
    "逻辑关系图设计": _build_design_adapter("逻辑关系图设计"),
    "三视图设计": _build_design_adapter("三视图设计"),
    "爆炸拆解图设计": _build_design_adapter("爆炸拆解图设计"),
    "流水线图设计": _build_design_adapter("流水线图设计"),
}

# 通用模板用于其他模式 — V13.3: 场景驱动 + 模式专属内容 (替代 5 行空壳)
def _generic_vibe_template(scene, director, mood, core, mode):
    core = core or {}
    p = _parse_scene_safe(scene)
    chars = p.get("characters") or ["主角"]
    objs = p.get("objects") or ["关键道具"]
    loc = p.get("location") or "场景"
    era = _detect_era_safe(scene)
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else chars[0]
    obj = objs[0]
    theme = core.get("_主题词", "情感")
    intent = core.get("_导演意图_观众应感到", "")
    header = (
        f"═══════════════════════════════════════════════════════════\n"
        f"【{mode}】导演: {director} | 场景: {scene} | 情绪: {mood}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
    )
    if mode == "表演指导":
        body = (
            f"角色: {c1} (由演员承载'{theme}')\n"
            f"本场目标: {c1}想要掩饰, 但身体先泄露.\n"
            f"内在动作: {c1}的手停在{obj}上, 0.5秒, 又若无其事地继续.\n"
            f"视线设计: {c1}看{c2}→移开→再看, 三次, 每次更短.\n"
            f"呼吸节奏: 说话前吸气, 说到一半屏住, 说完才呼出.\n"
            f"禁忌: 不许用脸'演'情绪, 情绪靠动作与停顿流露.\n"
            f"导演提示: {intent or '让观众自己发现, 不告诉观众'}."
        )
    elif mode == "VFX特效":
        body = (
            f"特效原则: 服务于'{theme}', 不炫技.\n"
            f"本场特效点: {loc}中的超现实细节——{obj}的异常(光/漂浮/时间).\n"
            f"时代适配: {era}——特效质感需贴合年代, 避免穿帮.\n"
            f"合成要点: 实拍前景+CG背景, 光影方向统一, 颗粒感匹配胶片.\n"
            f"克制原则: 特效出现≤3处, 每处都有叙事理由."
        )
    elif mode == "调色":
        body = (
            f"调色基调: {mood}, 时代={era}.\n"
            f"60-30-10: 主色按{core.get('_视觉调性','写实')}定, 辅色按情绪({mood}), 点缀色={obj}的颜色.\n"
            f"暗部: 保留细节, 不死黑; 高光: 不过曝, 留呼吸.\n"
            f"肤色: 以{c1}的肤色为锚, 全片一致.\n"
            f"情绪曲线: 色调随张力变化——低谷偏冷, 高潮对比增强."
        )
    elif mode == "剪辑":
        body = (
            f"剪辑节奏: 按情绪({mood})定——低谷长镜, 高潮短切.\n"
            f"本场切点: {c1}的动作/视线/呼吸, 三选一切.\n"
            f"转场逻辑: 镜B回答镜A的'然后呢', 不为了切而切.\n"
            f"留白: 关键情感点后留1-2秒静帧, 让观众消化.\n"
            f"禁忌: 不用无意义快切制造虚假节奏."
        )
    elif mode == "迭代":
        body = (
            f"迭代焦点: 本场'{theme}'是否被观众接收到.\n"
            f"检查项1: {c1}的动机是否清晰——观众能否一句话说出.\n"
            f"检查项2: {obj}是否承担了情感——去掉它故事是否塌.\n"
            f"检查项3: 节奏——低谷是否太长, 高潮是否太赶.\n"
            f"改进方向: 强化潜文本, 削弱直白台词."
        )
    elif mode == "质量QA":
        body = (
            f"QA清单 (场景: {loc}, 时代: {era}):\n"
            f"□ 年代穿帮: 无现代物件/称谓/语汇\n"
            f"□ 角色一致: {c1}/{c2} 的外形/服装跨镜头一致\n"
            f"□ 空间连续: {loc}的布局/光源方向不跳\n"
            f"□ 情绪连贯: 情绪({mood})不被单镜破坏\n"
            f"□ 反AI套话: 无 masterpiece/8K/HDR 等词"
        )
    elif mode == "互动剧":
        body = (
            f"互动节点: {c1}在{obj}前面临选择.\n"
            f"分支A: {c1}拿起{obj}→真相线\n"
            f"分支B: {c1}转身离开→遗憾线\n"
            f"汇合点: 两条线都在结尾回到'{theme}'.\n"
            f"选择设计: 无绝对对错, 只有不同代价."
        )
    else:
        body = (
            f"场景: {scene}\n情绪基调: {mood}\n"
            f"输出要求: 五感细节, 具体参数, 可直接用于拍摄/生成."
        )
    return header + body + (
        f"\n\n导演风格锚定: {director} — 镜头/光/节奏/色彩/构图/声音/情绪/物件/年代 全维度锁定.\n"
        f"反AI规则: 禁用 masterpiece/best quality/ultra detailed/4K/8K/HDR 等套话."
    )


class DirectorMasterVibe(DirectorNodeBase):
    """创意氛围聚合节点 — 23 合 1 (V14.2: +市场受众分析; V14.3-MERGED: +8 设计模式)."""
    NODE_TYPE = "创意氛围"

    @classmethod
    def INPUT_TYPES(cls):
        _ND = "无(默认)"  # V12.6 v7 fix: 兼容老版本 saved workflow
        _R  = "🎲 随机"    # V12.6 v8: 随机选择
        return {"required": {
            "创意模式": (VIBE_MODES+[_R], {"default": "概念立项"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "从核心数据包继承, 此处可单独覆盖"}),
            "创意方向": ([_ND, _R,
                # === 商业向 ===
                "商业类型片", "作者电影", "商业+艺术平衡", "网剧爆款", "短剧爽剧", "小程序剧",
                "创意短视频", "爆款反转短视频", "脑洞剧情", "情感共鸣", "搞笑整蛊", "Vlog博主风",
                "纪录观察", "新闻专题", "访谈谈话",
                # === 艺术向 ===
                "文艺小品", "实验先锋", "实验影像", "散文电影", "默片致敬", "舞台纪录",
                "装置艺术", "动画艺术", "拼贴影像", "数据库电影", "超现实主义",
                # === 类型化 ===
                "古装权谋", "仙侠奇幻", "都市言情", "悬疑烧脑", "惊悚悬疑", "恐怖心理",
                "战争史诗", "黑帮犯罪", "赛博朋克", "末日废土", "蒸汽朋克", "太空歌剧",
                "校园青春", "军旅热血", "谍战特工", "律政检察", "医疗行业", "金融商战",
                "体育竞技", "音乐歌舞", "美食治愈", "旅行公路", "家庭亲情", "老年关怀",
                "儿童动画", "神话传说", "民俗志怪", "宗教灵性",
            ], {"default": _ND, "tooltip": "40+ 创意方向 — 商业/艺术/类型化三层分类"}),
            "世界观深度": ([_ND, _R,
                "零设定(写实)", "浅(单一场景)", "中(有背景设定)", "深(完整社会规则)",
                "极深(完整宇宙观)", "架空历史(真实感)", "异世界(完整生态)",
                "平行宇宙(多世界)", "赛博空间(数字化)", "时间循环(封闭)", "末世废土(文明崩塌)",
                "乌托邦/反乌托邦", "奇幻体系(魔法/修真)", "科幻设定(高概念)",
            ], {"default": _ND, "tooltip": "14+ 世界观深度 — 深度分层+设定类型"}),
            "情感浓度": ([_ND, _R,
                # === 强度分层 ===
                "零情感(纯视觉/动作)", "极克制(冷感留白)", "克制(留白为主)",
                "适中(平衡)", "浓烈(情绪外放)", "极致(情绪爆发)", "过载(超载体验)",
                # === 情感类型 ===
                "悲伤", "愤怒", "恐惧", "喜悦", "厌恶", "惊讶", "平静", "怀旧",
                "孤独", "希望", "绝望", "爱恋", "仇恨", "嫉妒", "愧疚", "释然",
                "诗意", "悲壮", "诙谐", "荒诞",
            ], {"default": _ND, "tooltip": "20+ 情感浓度 — 强度分层+情感类型"}),
            "商业卖点": ([_ND, _R,
                # === 强度分层 ===
                "零卖点(纯艺术)", "弱卖点(艺术为主)", "有卖点(艺术+商业)",
                "强卖点(爆款逻辑)", "纯爆款(流量逻辑)", "IP改编向", "系列化(IP宇宙)",
                # === 卖点类型 ===
                "强反转", "强悬念", "强情绪(爽点)", "强共鸣(共情)", "强视觉(奇观)",
                "强人物(明星/角色)", "强话题(争议/讨论)", "强节奏(快节奏)",
                "强创意(脑洞)", "强金句(台词)", "强情感(泪点)", "强喜剧(笑点)",
            ], {"default": _ND, "tooltip": "16+ 商业卖点 — 强度分层+卖点类型"}),

        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承场景/导演/情绪/灵魂/AI/反AI"}),
            # V14.2: 市场受众分析 输入 (仅 市场受众分析 模式使用); V16.0 需求1: 加 🎲 随机
            "类型片市场": ([_R, "auto", "动作", "喜剧", "爱情", "悬疑", "科幻", "动画", "战争", "现实主义"],
                {"default": "auto", "tooltip": "市场受众分析: 类型片 (auto=从场景/核心数据包推断); 🎲 随机"}),
            "档期策略": ([_R, "auto", "春节档", "暑期档", "国庆档", "贺岁档", "非档期"],
                {"default": "auto", "tooltip": "市场受众分析: 档期 (auto=按类型最佳档期推断); 🎲 随机"}),
            "市场定位": ([_R, "auto", "头部", "腰部", "黑马"],
                {"default": "auto", "tooltip": "市场受众分析: 定位 (auto=按创意方向推断); 🎲 随机"}),
            "导演知名度": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05,
                "tooltip": "市场受众分析: 导演号召力 0-1"}),
            "演员阵容": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.05,
                "tooltip": "市场受众分析: 演员号召力 0-1"}),
            "营销预算": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05,
                "tooltip": "市场受众分析: 营销投入 0-1"}),
            "质量评分": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05,
                "tooltip": "市场受众分析: 成片质量预估 0-1"}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("创意",)
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/创意"

    def build(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包",""))
        mode = kwargs.get("创意模式","概念立项")
        # V16.0 需求1: 模式选择器支持 🎲 随机; V16.3: 由核心包随机种子驱动
        if mode == "🎲 随机":
            mode = resolve_dropdown(mode, "概念立项", VIBE_MODES,
                                    seed=derive_seed(core.get("_随机种子"), "创意模式"))
        if mode not in VIBE_MODES: mode = "概念立项"
        scene = core.get("_场景描述") or kwargs.get("场景描述","")
        director = core.get("_导演风格") or kwargs.get("导演风格","王家卫")
        mood = core.get("_情绪基调","孤独")

        # V12.6 v8: 4 个下拉框解析 (支持 "无(默认)" + "🎲 随机"); V16.3 各域独立盐种子驱动
        _VIBE_DIR_OPTS = ["商业类型片", "作者电影", "商业+艺术平衡", "网剧爆款", "短剧爽剧", "小程序剧",
                "创意短视频", "爆款反转短视频", "脑洞剧情", "情感共鸣", "搞笑整蛊", "Vlog博主风",
                "纪录观察", "新闻专题", "访谈谈话",
                "文艺小品", "实验先锋", "实验影像", "散文电影", "默片致敬", "舞台纪录",
                "装置艺术", "动画艺术", "拼贴影像", "数据库电影", "超现实主义",
                "古装权谋", "仙侠奇幻", "都市言情", "悬疑烧脑", "惊悚悬疑", "恐怖心理",
                "战争史诗", "黑帮犯罪", "赛博朋克", "末日废土", "蒸汽朋克", "太空歌剧",
                "校园青春", "军旅热血", "谍战特工", "律政检察", "医疗行业", "金融商战",
                "体育竞技", "音乐歌舞", "美食治愈", "旅行公路", "家庭亲情", "老年关怀",
                "儿童动画", "神话传说", "民俗志怪", "宗教灵性"]
        _WORLD_OPTS = ["零设定(写实)", "浅(单一场景)", "中(有背景设定)", "深(完整社会规则)",
                "极深(完整宇宙观)", "架空历史(真实感)", "异世界(完整生态)",
                "平行宇宙(多世界)", "赛博空间(数字化)", "时间循环(封闭)", "末世废土(文明崩塌)",
                "乌托邦/反乌托邦", "奇幻体系(魔法/修真)", "科幻设定(高概念)"]
        _EMO_OPTS = ["零情感(纯视觉/动作)", "极克制(冷感留白)", "克制(留白为主)",
                "适中(平衡)", "浓烈(情绪外放)", "极致(情绪爆发)", "过载(超载体验)",
                "悲伤", "愤怒", "恐惧", "喜悦", "厌恶", "惊讶", "平静", "怀旧",
                "孤独", "希望", "绝望", "爱恋", "仇恨", "嫉妒", "愧疚", "释然",
                "诗意", "悲壮", "诙谐", "荒诞"]
        _SELL_OPTS = ["零卖点(纯艺术)", "弱卖点(艺术为主)", "有卖点(艺术+商业)",
                "强卖点(爆款逻辑)", "纯爆款(流量逻辑)", "IP改编向", "系列化(IP宇宙)",
                "强反转", "强悬念", "强情绪(爽点)", "强共鸣(共情)", "强视觉(奇观)",
                "强人物(明星/角色)", "强话题(争议/讨论)", "强节奏(快节奏)",
                "强创意(脑洞)", "强金句(台词)", "强情感(泪点)", "强喜剧(笑点)"]
        kwargs["创意方向"] = resolve_dropdown(kwargs.get("创意方向"), "商业类型片", _VIBE_DIR_OPTS, seed=derive_seed(core.get("_随机种子"), "创意方向"))
        kwargs["世界观深度"] = resolve_dropdown(kwargs.get("世界观深度"), "中(有背景设定)", _WORLD_OPTS, seed=derive_seed(core.get("_随机种子"), "世界观深度"))
        kwargs["情感浓度"] = resolve_dropdown(kwargs.get("情感浓度"), "适中(平衡)", _EMO_OPTS, seed=derive_seed(core.get("_随机种子"), "情感浓度"))
        kwargs["商业卖点"] = resolve_dropdown(kwargs.get("商业卖点"), "有卖点(艺术+商业)", _SELL_OPTS, seed=derive_seed(core.get("_随机种子"), "商业卖点"))

        # V14.2: 市场受众分析 — 真实 market_audience_pro 引擎 (需要市场输入, 单独构建)
        if mode == "市场受众分析":
            main = _build_market_audience(scene, director, mood, core, kwargs)
        else:
            builder = TEMPLATES.get(mode, lambda s,d,m,c: _generic_vibe_template(s,d,m,c,mode))
            main = builder(scene, director, mood, core)
        main += self._director_block(director)
        from aggregator.dimensions import apply_dimensions
        main += "\n\n" + apply_dimensions("创意", kwargs)

        api_url, api_key, ai_model = resolve_ai_config(kwargs, core)
        if api_url:
            main = self._ensure_ai_output(main,
                {"node_type":"创意氛围","mode":mode,"director":director,"scene":scene,"mood":mood,"intent":core.get("_导演意图_观众应感到","") if core else ""},
                api_url, api_key, ai_model)

        from aggregator.pro_format import strip_decor
        # V14.2: 启用反AI规则 真实生效 (此前声明未消费)
        return (self._apply_anti_ai(strip_decor(main), kwargs, core),)