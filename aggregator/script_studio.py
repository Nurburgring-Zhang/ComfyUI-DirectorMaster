# -*- coding: utf-8 -*-
"""
② DirectorMasterScript — 剧本链 (7 合 1)
=========================================
7 模式: 剧本架构/正文/分镜/钩子/对白/角色弧/短剧.
内置深度模板 — 无 LLM 也输出高质量剧本.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy, resolve_dropdown, derive_seed
from aggregator.cinema_craft import build_life_texture, build_edit_decision_text
from aggregator.narrative_arrangement import (arrange_scenes, ARRANGEMENT_MODES, NARRATIVE_LINE_MODES)
from aggregator import aigc_prompt_builder as _aigc_pb
import re as _re
# 同时暴露 re 给本文件后续 helper 使用
re = _re

# V12.6 v8: 剧本模式按 长/短/微/竖/短视/动漫/绘本/MV/广告/互动剧 10 大类拆分
SCRIPT_MODES = [
    # === 影视长片 (90-180min) ===
    "完整长片剧本",        # 120min+ 完整剧本
    "三幕剧长片",          # 经典三幕剧
    "五幕剧长片",          # 莎士比亚五幕剧
    "救猫咪15拍长片",      # Blake Snyder 15 beats
    "英雄之旅12阶段",      # Joseph Campbell
    "麦基故事价值长片",    # Robert McKee
    # === 横屏短剧 (5-30min/集) ===
    "横屏微短剧",          # 5-15min/集
    "单元剧短剧",          # 每集独立故事
    "系列短剧",            # 多季多集
    # === 竖屏微短剧 (3-5min/集) ===
    "竖屏微短剧",          # 3-5min/集 抖音/快手
    "女频甜宠竖屏",        # 言情/甜宠
    "男频逆袭竖屏",        # 战神/逆袭
    "古风竖屏短剧",        # 古装/穿越
    # === 小程序剧 (1min/集, 80-100集) ===
    "竖屏小程序剧",        # 1min/集
    "爽剧小程序",          # 重生/复仇/总裁
    "反转小程序",          # 强反转
    # === 创意短视频 (30-60s) ===
    "创意玩法短视频",      # 脑洞/反转/爆款
    "爆火反转短视频",      # 5秒钩子+反转
    "脑洞剧情短视频",      # 创意脑洞
    "情感共鸣短视频",      # 温情感人
    "搞笑整蛊短视频",      # 喜剧/搞笑
    # === 动漫/二次元 ===
    "番剧动漫剧本",        # 24min/集
    "热血动漫剧本",        # 战斗/成长
    "校园动漫剧本",        # 青春/校园
    "奇幻冒险动漫剧本",    # 异世界/冒险
    # === 绘本/儿童故事 ===
    "绘本故事脚本",        # 5-10min 图文
    "睡前故事脚本",        # 童话/睡前
    "儿童教育动画脚本",    # 早教/科普
    # === MV/广告/宣传片 ===
    "MV音乐短片脚本",      # 3-5min 音乐MV
    "广告宣传片脚本",      # 15-60s
    "品牌故事片脚本",      # 1-3min
    "演唱会纪录片脚本",    # 60-120min
    # === 纪录片 ===
    "人物纪录片脚本",      # 60-90min
    "社会纪录片脚本",      # 60-120min
    # === 互动剧/沉浸式 ===
    "互动剧分支剧本",      # 多分支选择
    "沉浸式戏剧脚本",      # 360°/VR
    # === 行业垂直 ===
    "婚礼/活动脚本",       # 5-10min
    "课程教学脚本",        # 10-30min
    "Vlog脚本",            # 3-10min
    "直播脚本",            # 30-60min
    "钩子大师",            # 强钩子集
    "对白大师",            # 经典对白集
    "角色弧光",            # 角色成长集
    "剧本架构",            # 故事骨架
    "剧本正文",            # 对白场景
    "导演分镜",            # 分镜脚本
]

# V12.6 v7: 8 故事理论节拍点 (世界顶级编剧必备)
STORY_BEATS = {
    "三幕剧": ["建置(Setup)", "第一情节点", "第一幕结束", "上升动作(Rising Action)", "中点(Midpoint)", "第二情节点", "高潮(Climax)", "下降动作", "第三幕结束/解决"],
    "五幕剧": ["建置", "上升", "危机", "高潮", "结局"],
    "起承转合": ["起(引入)", "承(发展)", "转(转折)", "合(收束)"],
    "救猫咪15拍": ["开场画面", "主题陈述", "铺垫", "触发", "争论", "第二幕开始", "副线", "乐趣与游戏", "中点", "反派逼近", "失去一切", "灵魂的黑夜", "第三幕开始", "高潮", "结尾"],
    "英雄之旅12阶段": ["平凡世界", "冒险召唤", "拒绝召唤", "导师出现", "跨越门槛", "试炼盟友与敌人", "深渊逼近", "最大考验", "获得宝物", "归途", "复活", "携宝归来"],
    "麦基故事价值": ["欲望(主人公想要的)", "需求(真正需要的)", "价值正转/反转 (40+ 次)"],
    "双线并行": ["A线建置", "B线建置", "A线发展", "B线发展", "A线冲突", "B线冲突", "A线高潮", "B线高潮", "A线解决", "B线解决", "A+B 交汇点"],
    "非线性": ["开场悬念", "倒叙展开", "过去线索", "现在线索", "关键转折", "真相揭示", "现在/过去 汇合", "主题升华"],
    "皮克斯22条": ["#1 观众认同", "#2 好奇心", "#3 潜文本", "#4 简单清晰", "#5 找到笑点", "#6 兑现情感承诺", "#7 故事脊椎", "#8 主角主动性", "#9 设定预期", "#10 超越预期", "#11 视觉化讲故事", "#12 戏剧张力", "#13 角色优先", "#14 情感真相", "#15 内心独白", "#16 缺点让角色可爱", "#17 目标明确", "#18 冲突是故事引擎", "#19 让动作说话", "#20 节奏感", "#21 结尾有新意", "#22 让故事永恒"],
}

# V12.6 v13: 3D 空间坐标系统 (导演专业工作站 screen-left/right/center + X/Y/Z)
# 8 空间模板 — 覆盖家庭/工作/户外/特殊场景
SPATIAL_3D_TEMPLATES = {
    "厨房室内": {
        "灶台": {"X": -0.6, "Y": 0.0, "Z": 0.5, "screen": "center-left", "depth": "前景"},
        "砧板": {"X": -0.5, "Y": 0.0, "Z": 0.4, "screen": "left", "depth": "中前景"},
        "餐桌": {"X": 0.4, "Y": 0.0, "Z": 0.3, "screen": "right", "depth": "中景"},
        "窗": {"X": 0.0, "Y": 0.0, "Z": -0.8, "screen": "center", "depth": "背景"},
        "碗柜": {"X": -0.8, "Y": 0.0, "Z": -0.2, "screen": "far-left", "depth": "中景"},
        "门": {"X": 0.8, "Y": 0.0, "Z": 0.0, "screen": "far-right", "depth": "中景"},
    },
    "客厅": {
        "沙发": {"X": -0.3, "Y": 0.0, "Z": 0.2, "screen": "center-left", "depth": "中前景"},
        "电视": {"X": 0.0, "Y": 0.0, "Z": -0.6, "screen": "center", "depth": "中景"},
        "茶几": {"X": 0.2, "Y": 0.0, "Z": 0.5, "screen": "center-right", "depth": "前景"},
        "窗": {"X": -0.8, "Y": 0.0, "Z": -0.3, "screen": "far-left", "depth": "背景"},
        "阳台门": {"X": 0.8, "Y": 0.0, "Z": -0.2, "screen": "far-right", "depth": "中景"},
        "书架": {"X": 0.7, "Y": 0.0, "Z": 0.3, "screen": "right", "depth": "中景"},
    },
    "卧室": {
        "床": {"X": 0.0, "Y": 0.0, "Z": 0.0, "screen": "center", "depth": "中景"},
        "床头柜": {"X": -0.4, "Y": 0.0, "Z": 0.2, "screen": "left", "depth": "中前景"},
        "窗": {"X": 0.0, "Y": 0.0, "Z": -0.7, "screen": "center", "depth": "背景"},
        "衣柜": {"X": 0.8, "Y": 0.0, "Z": -0.3, "screen": "far-right", "depth": "中景"},
        "梳妆台": {"X": -0.7, "Y": 0.0, "Z": -0.2, "screen": "far-left", "depth": "中景"},
    },
    "书房": {
        "书桌": {"X": -0.4, "Y": 0.0, "Z": 0.3, "screen": "left", "depth": "中前景"},
        "椅子": {"X": -0.3, "Y": 0.0, "Z": 0.6, "screen": "center-left", "depth": "前景"},
        "书架": {"X": -0.8, "Y": 0.0, "Z": -0.5, "screen": "far-left", "depth": "中景"},
        "窗": {"X": 0.5, "Y": 0.0, "Z": -0.7, "screen": "right", "depth": "背景"},
        "台灯": {"X": -0.3, "Y": 0.0, "Z": 0.5, "screen": "center-left", "depth": "前景"},
    },
    "办公室": {
        "办公桌": {"X": 0.0, "Y": 0.0, "Z": 0.2, "screen": "center", "depth": "中前景"},
        "椅子": {"X": 0.0, "Y": 0.0, "Z": 0.5, "screen": "center", "depth": "前景"},
        "电脑": {"X": 0.0, "Y": 0.0, "Z": 0.1, "screen": "center", "depth": "中景"},
        "文件柜": {"X": 0.8, "Y": 0.0, "Z": -0.3, "screen": "far-right", "depth": "中景"},
        "窗": {"X": -0.8, "Y": 0.0, "Z": -0.5, "screen": "far-left", "depth": "背景"},
        "门": {"X": 0.6, "Y": 0.0, "Z": 0.4, "screen": "right", "depth": "中前景"},
    },
    "室外街道": {
        "主角": {"X": 0.0, "Y": 0.0, "Z": 0.0, "screen": "center", "depth": "中景"},
        "街对面": {"X": 0.0, "Y": 0.0, "Z": -0.6, "screen": "center", "depth": "背景"},
        "左侧店铺": {"X": -0.7, "Y": 0.0, "Z": -0.3, "screen": "far-left", "depth": "中景"},
        "右侧店铺": {"X": 0.7, "Y": 0.0, "Z": -0.3, "screen": "far-right", "depth": "中景"},
        "天空": {"X": 0.0, "Y": 1.0, "Z": -1.0, "screen": "top", "depth": "极远"},
    },
    "汽车内": {
        "驾驶位": {"X": -0.3, "Y": 0.0, "Z": 0.3, "screen": "left", "depth": "中前景"},
        "副驾": {"X": 0.3, "Y": 0.0, "Z": 0.3, "screen": "right", "depth": "中前景"},
        "后座": {"X": 0.0, "Y": 0.0, "Z": -0.3, "screen": "center", "depth": "中景"},
        "方向盘": {"X": -0.4, "Y": 0.0, "Z": 0.5, "screen": "left", "depth": "前景"},
        "仪表盘": {"X": -0.3, "Y": 0.0, "Z": 0.4, "screen": "left", "depth": "中前景"},
        "前挡风": {"X": 0.0, "Y": 0.0, "Z": -0.8, "screen": "center", "depth": "背景"},
    },
    "医院": {
        "病床": {"X": 0.0, "Y": 0.0, "Z": 0.2, "screen": "center", "depth": "中前景"},
        "心电监护": {"X": 0.4, "Y": 0.0, "Z": 0.3, "screen": "right", "depth": "中前景"},
        "吊瓶架": {"X": -0.5, "Y": 0.0, "Z": 0.2, "screen": "left", "depth": "中前景"},
        "门": {"X": 0.8, "Y": 0.0, "Z": -0.3, "screen": "far-right", "depth": "中景"},
        "窗": {"X": -0.8, "Y": 0.0, "Z": -0.5, "screen": "far-left", "depth": "背景"},
    },
}

# V12.6 v7: 角色 Want/Need/弧光 写入对白模板
CHARACTER_DIALOGUE_TEMPLATES = {
    "Want": "想要(外在目标): {want} → 推动动作/对白",
    "Need": "需要(内在需求): {need} → 推动情感/潜文本",
    "弧光": "{start_state} → {end_state}",
}


# ============================================================
# V14.3-MERGED: 孤儿库复活接线 (自 V14.1-clean 分叉移植) —
#   120 影视场景库 / 15 大师剧本 DNA / 25 故事感总纲 /
#   儿童内容适配 / 14 真实短剧案例 (全部惰性导入, 缺失时零影响)。
#   注: 与 V13.4 零虚假红线不冲突 — 这些库为真实制作知识/创作方法论,
#       非被停用的"槽位洗牌编造剧本模板"。
# ============================================================


def _match_scene_library(scene, mood):
    """120 影视场景库 (scene_library) — 关键词重合度匹配最佳场景."""
    try:
        from scene_library import SCENES, scene_to_prompt
    except Exception:
        return ""
    if not scene:
        return ""
    # 用户场景切词 (标点/空格), 2 字以上片段作为关键词
    import re as _re_sl
    tokens = [t for t in _re_sl.split(r"[,，、。；;\s]+", str(scene)) if len(t) >= 2]
    best, best_score = None, 0
    for idx, sc in enumerate(SCENES):
        text = " ".join(str(sc.get(k, "")) for k in ("name", "desc", "sub", "light", "mood"))
        score = sum(1 for t in tokens if t in text)
        if mood and str(mood) in text:
            score += 2
        if score > best_score:
            best, best_score = sc, score
    if not best or best_score == 0:
        return ""
    return scene_to_prompt(best, "【影视场景库 · 120 场景匹配】")


def _master_script_dna(director, scene):
    """15 位大师导演真实剧本 DNA (director_real_scripts) — 句式范本+创作方法."""
    try:
        from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    except Exception:
        return ""
    d = str(director or "").replace("[电影]", "").replace("[电视]", "").replace(
        "[动画]", "").replace("[广告]", "").replace("[短视频]", "").strip()
    for master in ALL_DIRECTORS:
        if master and master in d:
            return build_micro_finetune_prompt(master, str(scene or "")[:20])
    return ""


def _story_sense_pick(scene, limit=600):
    """25 条故事感总纲 (story_sense_data) — 按场景确定性取一条."""
    try:
        from story_sense_data import STORY_SENSE_LIBRARY
    except Exception:
        return ""
    if not STORY_SENSE_LIBRARY:
        return ""
    import hashlib as _hl_ss
    idx = int(_hl_ss.md5(str(scene or "").encode("utf-8", "replace")).hexdigest(), 16) % len(STORY_SENSE_LIBRARY)
    return str(STORY_SENSE_LIBRARY[idx])[:limit]


def _child_content_block(mode, scene):
    """儿童内容适配 (modes_child) — 年龄分级创作原则 + 格式规范."""
    try:
        from modes_child import build_child_system_prompt
        from story_sense_data import STORY_SENSE_LIBRARY
    except Exception:
        return ""
    if "睡前" in mode:
        sub, age = "儿童视频格式二", "0-3岁低幼"
    elif "绘本" in mode:
        sub, age = "儿童绘本", "3-6岁幼儿"
    else:
        sub, age = "儿童视频格式一", "6-9岁学龄"
    import hashlib as _hl_ch

    def _det_pick():
        if not STORY_SENSE_LIBRARY:
            return ""
        i = int(_hl_ch.md5(str(scene or "").encode("utf-8", "replace")).hexdigest(), 16) % len(STORY_SENSE_LIBRARY)
        return STORY_SENSE_LIBRARY[i]
    try:
        return build_child_system_prompt(sub, str(scene or "")[:30], "", str(scene or "")[:60],
                                         4, age, "卡通动画", [], _det_pick)
    except Exception:
        return ""


def _real_drama_cases(scene, limit=2):
    """14 个真实短剧制作案例 (master_director_data.REAL_DRAMA_CASES)."""
    try:
        from master_director_data import REAL_DRAMA_CASES
    except Exception:
        return ""
    if not isinstance(REAL_DRAMA_CASES, dict) or not REAL_DRAMA_CASES:
        return ""
    import hashlib as _hl_dc
    base = int(_hl_dc.md5(str(scene or "").encode("utf-8", "replace")).hexdigest(), 16)
    keys = list(REAL_DRAMA_CASES.keys())
    lines = []
    for i in range(min(limit, len(keys))):
        k = keys[(base + i) % len(keys)]
        v = REAL_DRAMA_CASES[k]
        if not isinstance(v, dict):
            continue
        lines.append(f"案例《{k}》: {v.get('team','')} | 时长 {v.get('duration','')} | "
                     f"完成 {v.get('completion','')} | 镜头 {v.get('shots','')} 个 | "
                     f"工具 {v.get('ai_tools','')} | 踩坑: {str(v.get('issues',''))[:80]}")
    return "\n".join(lines)


def inject_library_depth(main, mode, director, scene, mood):
    """V14.3-MERGED: 按模式把 5 个复活数据库注入剧本输出 (全部运行时实测接线)."""
    blocks = []
    dna = _master_script_dna(director, scene)
    if dna:
        blocks.append(dna)
    sl = _match_scene_library(scene, mood)
    if sl:
        blocks.append(sl)
    m = str(mode or "")
    if any(k in m for k in ("短剧", "短视频", "微短剧", "钩子", "反转")):
        sense = _story_sense_pick(scene)
        if sense:
            blocks.append("【故事感总纲注入 (短剧/短视频)】\n" + sense)
        cases = _real_drama_cases(scene)
        if cases:
            blocks.append("【真实短剧制作案例参考 (14 案例库)】\n" + cases)
    if any(k in m for k in ("儿童", "睡前", "绘本")):
        child = _child_content_block(m, scene)
        if child:
            blocks.append("【儿童内容适配 (年龄分级)】\n" + child[:1200])
        if "睡前" not in m:
            sense = _story_sense_pick(scene)
            if sense:
                blocks.append("【故事感总纲注入 (儿童)】\n" + sense)
    if not blocks:
        return main
    return main + "\n\n" + "\n\n".join(blocks)


# ============================================================
# V12.6 5 维上游整合 Helper — 真正把上游内容融入剧本内容字段
# ============================================================


def _parse_story_beats(story_theory):
    """V12.6 v7: 把 8 故事理论的节拍点展开, 真正融入剧本结构."""
    if not story_theory or story_theory not in STORY_BEATS:
        return ""
    beats = STORY_BEATS[story_theory]
    return "\n".join(f"  第{i+1}拍: {b}" for i, b in enumerate(beats))


def _parse_spatial_3d(scene_desc):
    """V12.6 v7: 解析场景描述 → 3D 空间坐标系统 (X/Y/Z + screen + depth)."""
    scene_lower = scene_desc or ""
    matched_key = None
    for k in SPATIAL_3D_TEMPLATES:
        if k.replace("室内", "").replace("室外", "") in scene_lower or k in scene_lower:
            matched_key = k
            break
    if not matched_key:
        matched_key = "通用室内"
    coords = SPATIAL_3D_TEMPLATES.get(matched_key, {})
    if not coords:
        return ""
    lines = [f"【3D 空间坐标系统 - {matched_key}】"]
    for obj, pos in coords.items():
        lines.append(f"  {obj}: X={pos['X']:+.1f} Y={pos['Y']:+.1f} Z={pos['Z']:+.1f} (screen-{pos['screen']}, {pos['depth']})")
    return "\n".join(lines)


def _parse_character_want_need(chars_text):
    """V12.6 v7: 从 Characters 输出解析 Want/Need/弧光, 真正融入对白."""
    if not chars_text: return []
    arcs = []
    for line in chars_text.split("\n"):
        s = line.strip()
        if "性格" in s and ":" in s:
            personality = s.split(":", 1)[-1].strip()
            # 推断 Want/Need (基于性格)
            if "沉默寡言" in personality or "用行动" in personality:
                want = "不被女儿读懂/被理解"
                need = "表达对女儿的爱"
            elif "复仇" in personality:
                want = "让仇人付出代价"
                need = "放下过去/释怀"
            elif "寻找" in personality:
                want = "找到某个人/物/真相"
                need = "接受失去/与自己和解"
            else:
                want = "完成外在目标"
                need = "实现内在成长"
            arcs.append({"want": want, "need": need, "personality": personality})
    return arcs


def _parse_vibe_anchors(vibe_text):
    """从 Vibe 输出提取关键锚点: 片名/对标/主题/概念/情感锚点."""
    anchors = {"片名": [], "对标": "", "主题": "", "概念": "", "情感": ""}
    if not vibe_text: return anchors
    for line in vibe_text.split("\n"):
        if "片名建议" in line: anchors["片名"] = re.findall(r"《([^》]+)》", line)
        if "对标作品" in line: anchors["对标"] = line.split("对标作品:")[-1].strip() if "对标作品:" in line else line.split("对标:")[-1].strip()
        if "一句话概念" in line: anchors["概念"] = line.split("一句话概念:")[-1].strip() if "一句话概念:" in line else line.split("概念:")[-1].strip()
        if "主题" in line and "对标" not in line and "主题:" in line:
            anchors["主题"] = line.split("主题:")[-1].strip()
        if "情感锚点" in line: anchors["情感"] = line.split("情感锚点:")[-1].strip() if "情感锚点:" in line else ""
    return anchors


def _parse_art_anchors(art_text):
    """从 Art 输出提取关键锚点: 主色/辅色/光影方向/材质/构图/摄影风格."""
    anchors = {"主色": "", "辅色": "", "光影方向": "", "材质": "", "构图": "", "摄影": "", "色彩系统": ""}
    if not art_text: return anchors
    for line in art_text.split("\n"):
        line_s = line.strip()
        if "主色" in line_s and "%" in line_s: anchors["主色"] = line_s
        if "辅色" in line_s and "%" in line_s: anchors["辅色"] = line_s
        if "光影方向" in line_s or "逆光" in line_s[:6] or "顺光" in line_s[:6]: anchors["光影方向"] = line_s
        if "材质" in line_s and "主" in line_s: anchors["材质"] = line_s
        if "构图" in line_s and ("法则" in line_s or "比例" in line_s or "对称" in line_s): anchors["构图"] = line_s
        if "摄影" in line_s and "风格" in line_s: anchors["摄影"] = line_s
        if "色彩系统" in line_s and "60-30-10" in line_s: anchors["色彩系统"] = line_s
    return anchors


def _parse_sound_anchors(sound_text):
    """从 Sound 输出提取 4 层声音锚点: 环境/拟音/心声/沉默."""
    anchors = {"环境": [], "拟音": [], "心声": [], "沉默": ""}
    if not sound_text: return anchors
    for line in sound_text.split("\n"):
        s = line.strip()
        if not s: continue
        if s.startswith(("雨声", "收音机", "冰箱", "环境", "海浪", "车流", "鸟鸣", "风")):
            anchors["环境"].append(s)
        elif s.startswith(("刀切", "脚步声", "门", "笔", "纸", "碗", "水", "翻书", "拟音")):
            anchors["拟音"].append(s)
        elif "沉默" in s or "留白" in s:
            anchors["沉默"] += s + " "
    return anchors


def _parse_char_anchors(chars_text):
    """从 Characters 输出提取角色锚点: 角色名/性格/外貌/服装/弧光."""
    anchors = {"角色": []}
    if not chars_text: return anchors
    name = ""
    personality = ""
    appearance = ""
    costume = ""
    for line in chars_text.split("\n"):
        s = line.strip()
        if "姓名" in s and ":" in s: name = s.split(":")[-1].strip()
        if "性格" in s and ":" in s: personality = s.split(":")[-1].strip()
        if "外貌" in s and ":" in s: appearance = s.split(":")[-1].strip()
        if "服装" in s and ":" in s: costume = s.split(":")[-1].strip()
    if name:
        anchors["角色"].append({"名": name, "性格": personality, "外貌": appearance, "服装": costume})
    return anchors


def _parse_asset_anchors(asset_text):
    """从 Asset 输出提取资产锚点: 道具/环境/服化道."""
    anchors = {"道具": "", "环境": "", "服化道": ""}
    if not asset_text: return anchors
    for line in asset_text.split("\n"):
        s = line.strip()
        if "道具" in s and ("叙事" in s or "凤梨" in s or "信" in s or "钢笔" in s or "收音" in s): anchors["道具"] += s + " "
        if "环境" in s and ("室内" in s or "厨房" in s or "空间" in s): anchors["环境"] += s + " "
        if "服化道" in s and ":" in s: anchors["服化道"] = s.split(":")[-1].strip() if "服化道:" in s else s
    return anchors


def _render_scene_with_upstream(scene, vibe_a, art_a, sound_a, char_a, asset_a):
    """V12.6 关键函数: 把 5 维 anchors 真正融入场景描写, 产生"5 维增强版场景".
    不再是 V9.5 模板里的"父女在厨房, 雨夜" — 而是"父女在 [主色 蓝绿] 调的厨房, [雨声+收音机+冰箱嗡鸣] 环绕, [凤梨罐头+旧信+钢笔] 陈列在桌上, 父亲 [瘦削+驼背+右手食指有老茧], [慢推镜头] 切菜"."""
    if not any([vibe_a, art_a, sound_a, char_a, asset_a]):
        return scene
    parts = [scene]
    # Art 视觉锚定 → 融入场景视觉
    if art_a.get("主色"): parts.append(f"[视觉锚定] {art_a['主色']}")
    if art_a.get("光影方向"): parts.append(f"[光影] {art_a['光影方向']}")
    if art_a.get("材质"): parts.append(f"[材质] {art_a['材质']}")
    # Sound 声音锚定 → 融入场景音
    if sound_a.get("环境"):
        env_str = " / ".join(sound_a["环境"][:3])
        parts.append(f"[环境音] {env_str}")
    if sound_a.get("拟音"):
        foley_str = " / ".join(sound_a["拟音"][:3])
        parts.append(f"[拟音] {foley_str}")
    # Characters 角色锚定 → 融入人物
    for ch in char_a.get("角色", []):
        if ch.get("外貌") or ch.get("服装"):
            parts.append(f"[{ch.get('名', '角色')}] {ch.get('外貌', '')} / {ch.get('服装', '')} / {ch.get('性格', '')}")
    # Asset 物件锚定 → 融入物件
    if asset_a.get("道具"): parts.append(f"[物件] {asset_a['道具']}")
    if asset_a.get("环境"): parts.append(f"[空间] {asset_a['环境']}")
    return " | ".join(parts)


def _integrate_5d_into_screenplay_content(screenplay, vibe_a, art_a, sound_a, char_a, asset_a, mode):
    """V12.6 关键函数: 把 5 维 anchors 真正整合进剧本内容字段(不是附录).
    策略: 在每个场景头前添加 [5维锚定] 段, 让剧本对白/动作/物件都基于 5 维增强版场景描写."""
    if not any([vibe_a, art_a, sound_a, char_a, asset_a]): return screenplay
    # 5 维锚定块
    anchor_block = []
    if vibe_a.get("片名"): anchor_block.append(f"【片名锚定】{', '.join(vibe_a['片名'])}")
    if vibe_a.get("对标"): anchor_block.append(f"【对标锚定】{vibe_a['对标']}")
    if art_a.get("色彩系统"): anchor_block.append(f"【色彩锚定】{art_a['色彩系统']}")
    if art_a.get("光影方向"): anchor_block.append(f"【光影锚定】{art_a['光影方向']}")
    if sound_a.get("环境"):
        anchor_block.append(f"【环境音锚定】{' / '.join(sound_a['环境'][:3])}")
    if sound_a.get("拟音"):
        anchor_block.append(f"【拟音锚定】{' / '.join(sound_a['拟音'][:3])}")
    if char_a.get("角色"):
        ch_strs = []
        for ch in char_a["角色"]:
            ch_strs.append(f"{ch.get('名')}({ch.get('性格')}, {ch.get('外貌')}, {ch.get('服装')})")
        anchor_block.append(f"【角色锚定】{' / '.join(ch_strs)}")
    if asset_a.get("道具"): anchor_block.append(f"【物件锚定】{asset_a['道具']}")
    if asset_a.get("环境"): anchor_block.append(f"【空间锚定】{asset_a['环境']}")
    if not anchor_block: return screenplay
    anchor_text = "\n".join(anchor_block)
    # 把 anchor_block 插入到 screenplay 头部
    if mode == "完整剧本":
        return f"═══════════════════════════════════════════════════════════\n【5 维锚定 (V12.6 真正整合)】\n{anchor_text}\n═══════════════════════════════════════════════════════════\n\n{screenplay}"
    elif mode == "剧本架构":
        return f"═══════════════════════════════════════════════════════════\n【5 维锚定】\n{anchor_text}\n═══════════════════════════════════════════════════════════\n\n{screenplay}"
    elif mode == "对白大师":
        # 对白模式: 角色锚定直接融入对白
        return f"【5 维锚定】\n{anchor_text}\n\n{screenplay}"
    else:
        return f"【5 维锚定】\n{anchor_text}\n\n{screenplay}"

# ============================================================
# 深度内置模板 — 无 LLM 也输出世界级内容
# ============================================================
def _build_architecture_template(scene, director, mood, core):
    """三幕结构剧本架构 — V13.1: 按场景元素生成 (替代硬编码厨房示范)."""
    import hashlib as _hl
    from aggregator.scene_engine import parse_scene
    parsed = parse_scene(scene)
    chars = parsed.get("characters", ["主角"])
    c1 = chars[0] if chars else "主角"
    c2 = chars[1] if len(chars) > 1 else "对手"
    objs = parsed.get("objects", [])
    obj = objs[0] if objs else "关键道具"
    loc = parsed.get("location", "场景")
    seed = int(_hl.md5(f"{scene}_{director}_arch".encode("utf-8", errors="replace")).hexdigest(), 16)
    hooks = [
        f"{c1}的一个动作突然停顿 — 空气变了",
        f"{obj}出现在不该出现的位置",
        f"{loc}的声音先于画面出现",
    ]
    turns = [
        f"{c2}做了一件{c1}没料到的事",
        f"{obj}背后的真相露出一角",
        f"一句旧话被重新提起",
    ]
    hook = hooks[seed % len(hooks)]
    turn = turns[(seed >> 3) % len(turns)]
    climax = f"{c1}第一次正面回应一直回避的事 — 但用的是最平常的方式"
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【剧本架构】导演: {director} | 场景: {scene} | 情绪: {mood}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        f"【三幕结构】\n"
        f"第一幕·建立 (0-30min):\n"
        f"  场景: {loc} — 建立空间/时间/人物关系 ({c1} vs {c2})\n"
        f"  钩子(前5秒): {hook}\n"
        f"  潜文本: 有话没说, 用日常动作掩盖\n"
        f"  物件承载: {obj} — 承载未说出的事\n\n"
        f"第二幕·对抗 (30-70min):\n"
        f"  转折1: {turn}\n"
        f"  冲突升级: {c1}试图回应, 但选择了沉默/回避\n"
        f"  转折2: {obj}的更多背景被揭开\n"
        f"  情绪递进: 困惑→对抗→动摇→理解\n\n"
        f"第三幕·解决 (70-90min):\n"
        f"  高潮: {climax}\n"
        f"  留白: 两人同处{loc}, 无人先开口\n"
        f"  结尾: 用一个动作完成和解 — 不说一句话"
    )

def _build_script_body_template(scene, director, mood, core):
    """剧本正文 — V13.1: 真实场次生成器 (替代硬编码厨房示范)."""
    from aggregator.pro_format import format_screenplay, build_standard_screenplay_scenes
    title = core.get("_项目名", "未命名项目") if core else "未命名项目"
    intent = core.get("_导演意图_观众应感到", "") if core else ""
    scenes = build_standard_screenplay_scenes(scene, director, mood, intent, 30, "三幕剧")
    return (
        f"═══════════════════════════════════════════════════════════\n"
        f"【剧本正文】导演: {director} | 场景: {scene}\n"
        f"═══════════════════════════════════════════════════════════\n\n"
        + format_screenplay(title, director, mood, intent, scenes)
    )

def _build_storyboard_template(scene, director, mood, core, target_minutes=30, story_theory="三幕剧", dims=None):
    """导演分镜 — V13.4: 时长感知镜头表。长片用 feature 引擎 (镜头数随时长缩放), 不再固定 6 镜。"""
    from aggregator.scene_engine import parse_scene, generate_shots
    parsed = parse_scene(scene)
    intent = core.get("_导演意图_观众应感到", "") if core else ""
    mood_arc = core.get("_情绪演变弧") if core else None
    if not isinstance(mood_arc, list) or not mood_arc:
        mood_arc = None
    # V13.4: 长片 (>=20min) 用 feature 引擎生成随时长缩放的镜头表
    if target_minutes >= 20:
        from aggregator.feature_film_engine import generate_feature_scenes, generate_feature_shots
        _fs = generate_feature_scenes(parsed, director, mood, intent, target_minutes, story_theory, mood_arc=mood_arc)
        shots = generate_feature_shots(_fs, target_minutes, director, mood)
    else:
        shots = generate_shots(parsed, director, mood, target_minutes)
    chars = "、".join(parsed.get("characters", [])[:3]) or "主角"
    objs = "、".join(parsed.get("objects", [])[:3]) or "核心道具"
    lines = [
        f"═══════════════════════════════════════════════════════════",
        f"【导演分镜】导演: {director} | 场景: {scene} | 片长: {target_minutes}min | 镜头数: {len(shots)}",
        f"【角色】{chars} | 【关键物件】{objs} | 【地点】{parsed.get('location','场景')}",
        f"═══════════════════════════════════════════════════════════",
    ]
    # 长片镜头过多时, 展示代表性镜头 (每场首镜 + 关键节拍镜), 避免输出爆炸但保持时长覆盖说明
    _show = shots
    if len(shots) > 60:
        _seen_scenes = set(); _pick = []
        for s in shots:
            _scn = s.get("scene", s.get("scene_num"))
            if _scn not in _seen_scenes:
                _seen_scenes.add(_scn); _pick.append(s)
        _show = _pick[:60]
        lines.append(f"(镜头表共 {len(shots)} 镜, 覆盖 {target_minutes}min; 以下展示每场首镜代表)")
    for s in _show:
        lines.append("───────────────────────────────────────────────────────────")
        lines.append(f"镜{s.get('n','')}. {s.get('size','中景')}·{parsed.get('location','场景')}·{s.get('stage_name','')}")
        lines.append(f"  景别: {s.get('size','中景')} | 焦段: {s.get('focal','35mm')}")
        lines.append(f"  机位/角度: {s.get('angle','平视')}")
        lines.append(f"  运动: {s.get('move','固定')}")
        lines.append(f"  时长: {s.get('dur','4s')}")
        lines.append(f"  表演/焦点: {s.get('focus','')}")
        if s.get("sound"):
            lines.append(f"  声音: {s.get('sound')}")
        if s.get("stage_emotion"):
            lines.append(f"  情绪: {s.get('stage_emotion')} | 光影: {s.get('stage_light','')}")
        lines.append(f"  转场: {s.get('cut','硬切')} | 目的: {s.get('purpose','')}")
    return "\n".join(lines)

def _build_hook_template(scene, director, mood, core):
    """钩子 — V13.1: 按场景元素生成前5秒钩子 (替代硬编码)."""
    import hashlib as _hl
    from aggregator.scene_engine import parse_scene
    parsed = parse_scene(scene)
    chars = parsed.get("characters", ["主角"])
    c1 = chars[0] if chars else "主角"
    objs = parsed.get("objects", [])
    obj = objs[0] if objs else "关键道具"
    loc = parsed.get("location", "场景")
    seed = int(_hl.md5(f"{scene}_{director}_hook".encode("utf-8", errors="replace")).hexdigest(), 16)
    visuals = [
        f"特写: {obj}出现在画面中央, {c1}的手停在半空 — 不动.",
        f"远景: {loc}空无一人, 只有{c1}的背影, 站了很久.",
        f"声音先行: 黑屏, 先听到{loc}的声音, 3秒后才亮画面.",
        f"反常细节: {c1}在做一件日常小事, 但做错了 — 观众立刻知道不对.",
    ]
    sounds = [
        f"环境音突然静音1秒 — 只剩一个动作的声音.",
        f"一段属于过去的声音先出现, 画面却是现在.",
        f"无配乐, 只有呼吸和{loc}的底噪.",
        f"一声极轻的响动, 打破长久的安静.",
    ]
    subs = [
        f"'有些话, 一直没说出来.'",
        f"'这一天, 等了很久.'",
        f"'看似平常, 其实不是.'",
        f"'答案就在{obj}里.'",
    ]
    v, s, u = visuals[seed % len(visuals)], sounds[(seed >> 3) % len(sounds)], subs[(seed >> 6) % len(subs)]
    hook_types = ["神秘悬念", "情感留白", "反常细节", "声音钩子"]
    return (
        f"【钩子大师】导演: {director} | 场景: {scene}\n\n"
        f"【前5秒钩子】\n"
        f"画面: {v}\n"
        f"声音: {s}\n"
        f"字幕: {u}\n"
        f"钩子类型: {hook_types[seed % len(hook_types)]}\n"
        f"钩子强度: {7 + seed % 3}/10\n\n"
        f"【反转设置】\n"
        f"观众以为这是关于{obj}的故事 — 其实是关于{c1}为什么一直没说出口."
    )

def _build_dialogue_template(scene, director, mood, core):
    """对白 — V13.1: 按场景角色生成极简潜文本对白 (替代硬编码)."""
    from aggregator.scene_engine import parse_scene
    parsed = parse_scene(scene)
    chars = parsed.get("characters", ["主角", "副线"])
    c1 = chars[0] if len(chars) > 0 else "主角"
    c2 = chars[1] if len(chars) > 1 else "副线"
    objs = parsed.get("objects", [])
    obj = objs[0] if objs else "那件东西"
    loc = parsed.get("location", "场景")
    return (
        f"【对白大师】导演: {director} | 场景: {scene}\n\n"
        f"角色1: {c1}\n角色2: {c2}\n场景: {loc}\n\n"
        f"── 对白示范 (极简 + 潜文本) ──\n"
        f"{c1}: (不抬头) '来了.'\n"
        f"{c2}: '嗯.'\n"
        f"── 潜文本: {c1}想说的远比说出口的多 ──\n\n"
        f"{c1}: (停顿) '那个{obj}...'\n"
        f"{c2}: (抬头) '怎么了?'\n"
        f"{c1}: (移开视线) '没什么.'\n"
        f"── 潜文本: 话到嘴边又咽下, {obj}承载着没说出的事 ──\n\n"
        f"{c2}: (看着{obj}) '一直留着?'\n"
        f"{c1}: (沉默几秒) '...习惯了.'\n"
        f"── 潜文本: '习惯了' = 一直记得 ──\n\n"
        f"【对白原则】每句≤10字, 真话只说一半, 物件代替语言."
    )

def _build_character_template(scene, director, mood, core):
    """角色弧光 — V13.1: 按场景解析角色生成 Want/Need/弧光 (替代硬编码)."""
    import hashlib as _hl
    from aggregator.scene_engine import parse_scene
    parsed = parse_scene(scene)
    chars = parsed.get("characters", ["主角"])
    c1 = chars[0] if chars else "主角"
    objs = parsed.get("objects", [])
    obj = objs[0] if objs else "标志性物件"
    seed = int(_hl.md5(f"{scene}_{director}_char".encode("utf-8", errors="replace")).hexdigest(), 16)
    wants = ["说出口", "被看见", "弥补", "离开", "守住", "被原谅"]
    needs = ["被理解", "放下", "接受自己", "与人连接", "承认脆弱", "回家"]
    arcs = ["从'不敢'到'做到'", "从'逃避'到'面对'", "从'孤独'到'连接'", "从'执念'到'释然'"]
    habits = ["说话前先停顿", "用手头的小动作掩盖情绪", "习惯把东西摆正", "总是最后一个离开", "笑的时候不看人"]
    w = wants[seed % len(wants)]
    n = needs[(seed >> 3) % len(needs)]
    a = arcs[(seed >> 6) % len(arcs)]
    h = habits[(seed >> 9) % len(habits)]
    return (
        f"【角色弧光】导演: {director} | 场景: {scene}\n\n"
        f"角色: {c1}\n"
        f"Want(欲望): {w}\n"
        f"Need(需求): {n}\n"
        f"角色弧: {a}\n"
        f"身体习惯: {h}\n"
        f"标志性物件: {obj} — 承载角色未说出的情感\n"
        f"情绪基调: {mood}\n\n"
        f"【弧光设计】Want 与 Need 互相矛盾 — 角色追逐 Want 的过程中被迫面对 Need."
    )

# V14.2: 短剧 10 模式子类型差异化 (修复模式坍缩 — 此前 10 模式共用同一模板逐字节同构)
SHORT_DRAMA_SUBTYPES = {
    "女频甜宠竖屏": {
        "定位": "女频甜宠 — 发糖驱动, 3秒一个心动点",
        "单集": "90秒", "总集数": "80-100",
        "爽虐甜": (2, 1, 7),
        "钩子": ["男主下意识护住{c1}的手, 停顿0.5秒", "{obj}上留着男主的温度", "{c1}假装不在意, 镜头拍到她攥紧的衣角"],
        "卡点": "男主身份揭晓 — 他一直就在{c1}身边",
        "字幕": "粉色描边字幕, 心动时刻放大+心跳音",
    },
    "男频逆袭竖屏": {
        "定位": "男频逆袭 — 爽点驱动, 被轻视→当场打脸",
        "单集": "90秒", "总集数": "80-100",
        "爽虐甜": (7, 3, 0),
        "钩子": ["众人嘲笑{c1}, 他没抬头", "{obj}被摔在地上, {c1}的眼神变了", "一句'你配吗', {c1}缓缓掏出手机"],
        "卡点": "{c1}真实身份曝光 — 全场鸦雀无声",
        "字幕": "金色爆裂字幕, 打脸瞬间慢放+重低音",
    },
    "古风竖屏短剧": {
        "定位": "古风 — 重生/复仇/宅斗, 服化道即叙事",
        "单集": "90秒", "总集数": "70-90",
        "爽虐甜": (4, 4, 2),
        "钩子": ["{c1}重生回大婚当日, 盖头下的眼神变了", "{obj}是前世毒杀她的证物", "铜镜里, {c1}看见上一世的自己"],
        "卡点": "{c1}当众揭穿{obj}背后的阴谋 — 前世债今世还",
        "字幕": "竖排书法字幕, 转折处配古琴骤停",
    },
    "反转小程序": {
        "定位": "反转 — 每集一个认知颠覆, 结尾必反转",
        "单集": "60秒", "总集数": "50-80",
        "爽虐甜": (4, 3, 3),
        "钩子": ["{c1}笃定地说出判断, 镜头切到{obj}——细节不对", "所有人都信了, 除了{c1}", "开场即结局, 然后倒放"],
        "卡点": "最后一秒反转: {obj}真正的主人另有其人",
        "字幕": "倒计时字幕压迫感, 反转帧闪白+音效抽离",
    },
    "爽剧小程序": {
        "定位": "爽剧 — 情绪直给, 一集一个爽点闭环",
        "单集": "90秒", "总集数": "80-100",
        "爽虐甜": (6, 2, 2),
        "钩子": ["{c1}被当众羞辱, 三秒后对方跪了", "{obj}一出现, 全场起立", "{c1}只说了一个字, 对面腿软了"],
        "卡点": "{c1}亮出底牌 — 此前所有轻视加倍奉还",
        "字幕": "大号加粗字幕, 爽点处屏幕震动特效",
    },
    "竖屏小程序剧": {
        "定位": "小程序剧通用 — 强钩子+付费卡点精准投放",
        "单集": "90秒", "总集数": "80",
        "爽虐甜": (4, 3, 3),
        "钩子": ["{c1}的一个反常动作, 停在半空", "{obj}特写, 上面有不该出现的东西", "{loc}空镜, 一声异响"],
        "卡点": "{obj}的真相首次揭晓",
        "字幕": "标准白字黑边, 悬念处字幕悬停",
    },
    "竖屏微短剧": {
        "定位": "竖屏微短剧 — 9:16 满屏, 前3秒定生死",
        "单集": "60-90秒", "总集数": "60-80",
        "爽虐甜": (4, 3, 3),
        "钩子": ["第一帧就是冲突最高点", "{c1}对着镜头说了一句不该说的话", "{obj}从画面角落缓缓移入"],
        "卡点": "第8-10集首个付费点: {obj}背后的秘密",
        "字幕": "居中安全区字幕, 避开平台UI遮挡",
    },
    "横屏微短剧": {
        "定位": "横屏微短剧 — 16:9 构图叙事, 调度空间更大",
        "单集": "2-3分钟", "总集数": "30-40",
        "爽虐甜": (4, 3, 3),
        "钩子": ["横移长镜扫过{loc}, 停在{c1}身上", "前景{obj}虚化, 后景{c1}的表情渐变", "一场戏两个信息层, 观众比角色先知道真相"],
        "卡点": "季中点: {c1}发现{obj}与自己的关联",
        "字幕": "底部电影字幕条, 保留画面完整构图",
    },
    "单元剧短剧": {
        "定位": "单元剧 — 每集独立故事, 同一世界观/主角串线",
        "单集": "3-5分钟", "总集数": "24 (每集独立)",
        "爽虐甜": (4, 3, 3),
        "钩子": ["本集委托人带着{obj}找到{c1}", "{loc}来了一个不说实话的人", "开场30秒交代本集谜题"],
        "卡点": "本集结尾: {obj}物归原主, 但{c1}留下了线索",
        "字幕": "单元标题卡开场, 结尾留下集引子",
    },
    "系列短剧": {
        "定位": "系列短剧 — 连续剧情分集, 每集结尾必留钩",
        "单集": "2-3分钟", "总集数": "40-60 (连续剧情)",
        "爽虐甜": (4, 4, 2),
        "钩子": ["上集结尾的悬念, 本集开场直接续上", "{c1}推开{loc}的门, 看见不该看见的", "{obj}换了位置 — 有人来过"],
        "卡点": "每集结尾最后3秒: 新线索或新危机",
        "字幕": "前情提要3秒+本集标题, 结尾'下集更精彩'",
    },
    "垂直短剧": {
        "定位": "垂直短剧 — 行业题材深耕 (医疗/律政/金融)",
        "单集": "2-3分钟", "总集数": "40-60",
        "爽虐甜": (4, 3, 3),
        "钩子": ["{c1}一眼看出{obj}的专业破绽", "外行看热闹, {c1}看出了问题", "行业黑话交锋, 句句是刀"],
        "卡点": "{c1}用专业能力逆转局面 — 行业高光时刻",
        "字幕": "术语注释字幕, 专业感拉满",
    },
}


def _build_short_drama_template(scene, director, mood, core, target_minutes=30, story_theory="三幕剧", dims=None, mode=None):
    """垂直短剧 — V14.2: 10 模式子类型差异化 (钩子/爽虐甜比例/集数/卡点/字幕 全部按子类型).
    V14.3 (红队P2修复): 4 创作维度 (对白密度/节奏控制/潜文本/主题深度) 真实下场。"""
    import hashlib as _hl
    from aggregator.scene_engine import parse_scene
    parsed = parse_scene(scene)
    chars = parsed.get("characters", ["主角"])
    c1 = chars[0] if chars else "主角"
    objs = parsed.get("objects", [])
    obj = objs[0] if objs else "关键道具"
    loc = parsed.get("location", "场景")
    sub = SHORT_DRAMA_SUBTYPES.get(mode, SHORT_DRAMA_SUBTYPES["竖屏小程序剧"])
    seed = int(_hl.md5(f"{scene}_{director}_{mode}_sd".encode("utf-8", errors="replace")).hexdigest(), 16)
    hook = sub["钩子"][seed % len(sub["钩子"])].format(c1=c1, obj=obj, loc=loc)
    kadian = sub["卡点"].format(c1=c1, obj=obj, loc=loc)
    s, n_, t = sub["爽虐甜"]
    ep1 = seed % 3

    # V14.3: 创作维度真实消费
    dims = dims or {}
    _dial = str(dims.get("对白密度", "") or "")
    _rhythm = str(dims.get("节奏控制", "") or "")
    _subtext = str(dims.get("潜文本强度", "") or "")
    _depth = str(dims.get("主题深度", "") or "")
    # 对白密度 → 对白设计 + 第3镜内容
    if "零对白" in _dial:
        dial_line = "对白设计: 零对白 — 纯画面+字幕叙事, 情绪全靠动作/表情/物件传递"
        shot3 = f"第1集·第3镜(3s): {c1}的反应 — 无台词, 手部动作与眼神承担全部情绪"
    elif any(k in _dial for k in ("极简", "稀疏", "默片")):
        dial_line = "对白设计: 极简对白 (每集≤3句, 每句≤10字), 留白优先"
        shot3 = f"第1集·第3镜(3s): {c1}只说了一个字, 然后沉默 — 手在抖"
    elif any(k in _dial for k in ("密集", "台词密集", "独白")):
        dial_line = "对白设计: 对白驱动 — 连珠炮台词推进, 每集≥8句, 语速快"
        shot3 = f"第1集·第3镜(3s): {c1}连说三句质问, 一句比一句快 — 台词即节奏"
    else:
        dial_line = "对白设计: 标准对白 (每集4-6句, 短句为主)"
        shot3 = f"第1集·第3镜(3s): {c1}的反应 — 手在抖, 但没出声"
    # 节奏控制 → 镜时长
    if any(k in _rhythm for k in ("极快", "超快")):
        d1, d2, d3 = "2s", "3s", "2s"
        rhythm_line = "节奏: 极快 — 镜时长压缩, 卡点更密"
    elif any(k in _rhythm for k in ("极慢", "慢(")):
        d1, d2, d3 = "5s", "8s", "5s"
        rhythm_line = "节奏: 慢 — 镜头拉长, 情绪沉淀优先"
    elif "变速" in _rhythm or "交替" in _rhythm:
        d1, d2, d3 = "2s", "6s", "2s"
        rhythm_line = "节奏: 变速 — 快慢交替, 钩子快/情绪慢"
    else:
        d1, d2, d3 = "3s", "5s", "3s"
        rhythm_line = ""
    # 潜文本强度 → 潜文本标注
    if "零" in _subtext or "无" in _subtext:
        subtext_line = ""
    elif "弱" in _subtext:
        subtext_line = "潜文本: 弱 — 表层意思为主, 仅在卡点留一层言外之意"
    else:
        subtext_line = f"潜文本: 每镜一层潜文本 — {obj}的存在本身就是未说出的话; 动作先于台词泄露真实意图"
    # 主题深度 → 主题陈述
    theme = core.get("_主题词", "") if core else ""
    if theme and any(k in _depth for k in ("深", "极深", "存在主义", "形而上")):
        depth_line = f"主题陈述: '{theme}'不说破 — 藏在{c1}的每次选择里, 结尾不给答案"
    else:
        depth_line = ""

    lines = [
        f"【短剧策划 · {mode}】导演: {director} | 场景: {scene}",
        f"  子类型定位: {sub['定位']}",
        "",
        f"单集时长: {sub['单集']} | 总集数: {sub['总集数']}",
        f"爽虐甜比例: {s + ep1}:{n_}:{max(0, t - ep1)}",
        "",
        dial_line,
    ]
    if rhythm_line:
        lines.append(rhythm_line)
    if subtext_line:
        lines.append(subtext_line)
    if depth_line:
        lines.append(depth_line)
    lines += [
        "",
        f"前3秒钩子: {hook}",
        f"第1集·第1镜({d1}): {hook} — 字幕埋悬念",
        f"第1集·第2镜({d2}): {c1}发现{obj}的异常",
        shot3,
        f"第1集·结尾({d3}): 字幕: '第1集·{loc}'",
        "",
        f"付费卡点: {kadian}",
        f"字幕策略: {sub['字幕']}",
        f"情绪基调: {mood} | 导演风格: {director}",
    ]
    return "\n".join(lines)

# V14.2: 形态类模式专属格式约定 — 修复同档期形态模式坍缩 (此前同 target_minutes 的形态模式正文逐字节相同)。
# 每个形态有真实的结构/钩子/节拍约定 (非换标题), 注入剧本正文之后。
FORMAT_MODE_FLAVOR = {
    # 创意短视频 (30-60s)
    "创意玩法短视频": "【短视频格式约定】前3秒钩子(反常识开场)→中段创意展开→结尾记忆点; 单场景闭环, 无支线; 台词≤10句, 视觉创意优先于叙事。",
    "爆火反转短视频": "【短视频格式约定】5秒钩子(冲突/悬念)→铺垫误导→最后5秒反转(认知颠覆); 反转前所有细节为反转服务; 结尾定格+字幕点题。",
    "脑洞剧情短视频": "【短视频格式约定】高概念设定开场(1句交代世界观)→规则演绎→脑洞收束; 设定即钩子, 逻辑自洽是爽点。",
    "情感共鸣短视频": "【短视频格式约定】情感钩子(普遍情绪)→生活细节铺陈→情感爆点(一个动作/一句话); 克制表达, 细节代替煽情; 结尾留白引共鸣。",
    "搞笑整蛊短视频": "【短视频格式约定】整蛊设定开场→受害者反应递进→揭晓/反转笑点; 笑点密度每5秒一个; 结尾揭晓不伤人。",
    # 动漫 (24min/集)
    "番剧动漫剧本": "【动漫格式约定】OP前冷开场(本集悬念)→A part(22min 主线)→eyecatch→B part→ED后下集预告; 每集一个情绪高点(名场面); 内心独白+画面演出并用。",
    "热血动漫剧本": "【动漫格式约定】战斗/成长双轨; 招式命名+分镜演出; 回忆杀插入(战斗中场); 爆发点配台词燃点; 每集留一个实力悬念。",
    "校园动漫剧本": "【动漫格式约定】日常场景开场(教室/社团)→人物关系推进→小事件情感转折; 季节/放学/文化祭等意象承载情绪; 对白生活化+内心吐槽。",
    "奇幻冒险动漫剧本": "【动漫格式约定】世界观规则开场→队伍/目标确立→关卡式推进; 能力体系有代价; 每集解锁一个新规则/新地图。",
    # 绘本/儿童
    "绘本故事脚本": "【绘本格式约定】12-16 页分页结构, 每页一图一句; 重复句式+韵律(适合朗读); 主角一个明确愿望; 结尾温暖闭环; 画面描述含构图/色彩/情绪。",
    "睡前故事脚本": "【睡前故事格式约定】舒缓开场(安抚情绪)→轻柔冒险→安全回归; 句式渐慢渐轻; 结尾明确'晚安'仪式; 无惊吓元素。",
    "儿童教育动画脚本": "【教育动画格式约定】知识点开场(问题)→探索/试错→知识点揭晓+重复强化; 互动提问(打破第四面墙); 片尾口诀总结。",
    # MV/广告
    "MV音乐短片脚本": "【MV格式约定】按音乐结构分段(前奏/主歌/副歌/间奏/桥段/尾奏); 副歌=视觉高光+重复记忆点; 画面节奏卡 BPM; 叙事线+表演线交织。",
    "广告宣传片脚本": "【广告格式约定】15/30/60s 版本; 前3秒抓注意→产品/卖点呈现→行动号召(CTA); 卖点≤3个; 结尾品牌露出+口号。",
    "品牌故事片脚本": "【品牌故事格式约定】1-3min 情感叙事; 品牌价值观融入人物故事(不硬广); 真实质感+情感共鸣; 结尾品牌主张自然升华。",
    "演唱会纪录片脚本": "【演唱会纪录片格式约定】舞台表演+后台纪实双线; 按歌单分段; 穿插采访/排练/观众反应; 高潮曲目=完整呈现+情绪铺垫。",
    # 纪录片
    "人物纪录片脚本": "【纪录片格式约定】观察式长镜+采访穿插; 人物日常→核心事件→内心揭示; 不摆拍, 冲突来自真实; 旁白克制, 让人物自己说。",
    "社会纪录片脚本": "【纪录片格式约定】议题开场(现象)→多视角个案→结构分析→开放结尾; 数据+人物故事结合; 保持立场但呈现复杂。",
    # 互动/沉浸
    "互动剧分支剧本": "【互动剧格式约定】主线节点+选择分支; 每个选择点 2-3 选项(有真实代价); 分支汇合或导向不同结局; 标注分支树与回收点。",
    "沉浸式戏剧脚本": "【沉浸式格式约定】360°/VR 空间叙事; 观众视角=主角视角; 环境叙事(可探索细节); 引导视线与注意力; 无传统剪辑, 用空间转场。",
    # 行业垂直
    "婚礼/活动脚本": "【活动视频格式约定】流程时间轴(准备/仪式/宴会); 情感高光(誓言/感恩/互动); 多机位分工标注; 结尾快剪回顾。",
    "课程教学脚本": "【教学脚本格式约定】学习目标开场→讲解分段(每段≤5min)→示例/演示→小结+练习; 屏幕标注/字幕配合; 节奏留暂停点。",
    "Vlog脚本": "【Vlog格式约定】第一视角口播开场(对镜头说话)→体验过程→感受收尾; 手持真实感; 穿插空镜/转场; 个人化语气。",
    "直播脚本": "【直播格式约定】开播暖场→内容/带货分段→互动环节(弹幕/福利)→高潮→下播预告; 标注话术节点与节奏; 留互动钩子防流失。",
}


# ============================================================
# V14.3-MERGED D2: 形态类模式专属场次骨架 —
#   同档期形态模式不再共用同一场次结构: 每个形态有自己的结构位序列,
#   骨架真实下场 (短形态强制场数=骨架槽数, 长形态按比例标注结构段)。
#   每槽 = {label: 结构位名, mission: 该结构位必须完成的创作任务}。
# ============================================================
FORMAT_SCENE_SKELETONS = {
    # === 短视频族 (1-2min) ===
    "创意玩法短视频": [
        {"label": "钩子位·反常识开场(0-3s)", "mission": "3秒内给出一个反常识的画面或动作, 观众因为'为什么会这样'停下; 不解释, 先呈现异常。"},
        {"label": "创意展开·规则演示", "mission": "核心创意规则逐步演示, 每一步增加一个新元素; 信息靠画面传达, 不靠旁白解释。"},
        {"label": "创意升级·组合反转", "mission": "把前段元素以意想不到的方式组合, 创意升一级; 这里是'有趣'和'惊艳'的分界。"},
        {"label": "记忆点·收尾定格", "mission": "收尾定格或循环结构, 留下一个观众可模仿/可引用的记忆点。"},
    ],
    "爆火反转短视频": [
        {"label": "钩子位·冲突悬念(0-5s)", "mission": "前5秒抛出冲突或悬念, 让观众产生'接下来会怎样'的追问; 悬念必须与结尾反转同源。"},
        {"label": "误导铺垫·细节埋设", "mission": "按观众的惯性思维铺垫, 同时埋入为反转服务的细节; 每个细节反转后都要能重新解释。"},
        {"label": "反转·认知颠覆(最后5s)", "mission": "最后5秒认知颠覆: 前文所有细节瞬间换义; 反转靠信息差, 不靠巧合。"},
        {"label": "定格·字幕点题", "mission": "反转后定格+字幕点题, 给观众1-2秒消化时间, 让反转的余味完成传播动机。"},
    ],
    "脑洞剧情短视频": [
        {"label": "高概念设定开场", "mission": "一句话交代世界观: 这个世界和现实的唯一差异是什么; 设定即钩子, 不铺垫直接进。"},
        {"label": "规则演绎·逻辑链", "mission": "从设定出发演绎规则后果, 每一步推导都要逻辑自洽; 严谨是脑洞的爽点。"},
        {"label": "脑洞升级·边界突破", "mission": "把规则推到边界: 如果继续会怎样; 在这里打破观众对设定的预期上限。"},
        {"label": "脑洞收束·自洽收尾", "mission": "收束回设定本身, 给出闭环或留一个更大的脑洞; 结尾不能推翻前面的逻辑。"},
    ],
    "情感共鸣短视频": [
        {"label": "情感钩子·普遍情绪", "mission": "开场锚定一种普遍情绪(想念/遗憾/被忽视), 用一个具体画面而非形容词唤起。"},
        {"label": "生活细节铺陈", "mission": "用生活细节铺陈情感, 克制表达; 细节代替煽情, 不配乐先行。"},
        {"label": "情感爆点·一个动作一句话", "mission": "情感爆点压缩为一个动作或一句话; 爆点的力量来自前面的克制。"},
        {"label": "留白结尾·共鸣邀请", "mission": "结尾留白, 不给结论; 让观众把自己的经历填进来, 共鸣在画面外完成。"},
    ],
    "搞笑整蛊短视频": [
        {"label": "整蛊设定开场", "mission": "快速交代整蛊设定与规则, 观众提前知道'要发生什么', 期待感代替惊讶感。"},
        {"label": "反应递进·第一层", "mission": "受害者第一层反应: 困惑/不信; 反应要真实, 笑点密度每5秒一个。"},
        {"label": "反应递进·第二层", "mission": "反应升级: 接受现实后的二次反应往往比第一次更好笑; 在这里加码。"},
        {"label": "揭晓·笑点不伤人", "mission": "揭晓真相, 整蛊者与被整蛊者一起笑; 底线是玩笑不造成伤害。"},
    ],
    # === 动漫族 (24min/集) ===
    "番剧动漫剧本": [
        {"label": "OP前冷开场·本集悬念", "mission": "OP前冷开场: 抛出本集悬念或上集高潮余波, 30-90秒抓住观众。"},
        {"label": "A part·主线推进", "mission": "A part推进主线, 建立本集核心矛盾; 内心独白+画面演出并用。"},
        {"label": "Eyecatch·中点过渡", "mission": "Eyecatch中点: 情绪切换标志, 用一张定格画面完成节奏呼吸。"},
        {"label": "B part·主线情感交汇", "mission": "B part主线与情感线交汇, 矛盾升级至本集顶点。"},
        {"label": "名场面·情绪高点", "mission": "每集一个名场面: 情绪高点, 演出拉满(作画/配乐/演出三重叠加)。"},
        {"label": "ED·情绪沉淀", "mission": "ED沉淀本集情绪, 画面可与正文形成互文。"},
        {"label": "下集预告", "mission": "下集预告: 给一个必须追的理由(悬念/反转预告/新角色)。"},
    ],
    "热血动漫剧本": [
        {"label": "战前日常·张力积蓄", "mission": "战前日常: 用轻松段落积蓄张力, 交代战斗动机与代价。"},
        {"label": "战斗上半场·试探压制", "mission": "战斗上半场: 试探→被压制, 主角处于下风; 招式命名+分镜演出。"},
        {"label": "回忆杀插入·动机揭示", "mission": "战斗中场回忆杀: 揭示'为什么而战', 情感为爆发充能。"},
        {"label": "爆发点·燃点台词", "mission": "爆发点: 燃点台词+新招式/觉醒, 战局逆转; 台词要能被观众背诵。"},
        {"label": "战斗下半场·成长确认", "mission": "战斗收尾: 胜利或虽败犹荣, 确认主角成长了什么。"},
        {"label": "实力悬念·下集钩子", "mission": "结尾留一个实力悬念(新敌人/新境界), 驱动追番。"},
    ],
    "校园动漫剧本": [
        {"label": "日常开场·教室社团", "mission": "日常场景开场(教室/社团/放学路), 用人物小动作建立生活感。"},
        {"label": "关系推进·小事件", "mission": "一个小事件推动人物关系变化; 事件不大, 但必须改变两人距离。"},
        {"label": "情感转折·意象承载", "mission": "情感转折: 用季节/放学/文化祭等意象承载情绪, 不直说。"},
        {"label": "内心独白·吐槽收束", "mission": "内心独白收束: 生活化对白+内心吐槽, 把情感落点讲给观众。"},
        {"label": "余韵结尾", "mission": "余韵式结尾: 一个画面定格情绪, 不解释, 让观众自己回味。"},
    ],
    "奇幻冒险动漫剧本": [
        {"label": "世界观规则开场", "mission": "开场交代世界观规则: 能力体系/地图/阵营, 规则必须有代价。"},
        {"label": "队伍目标确立", "mission": "队伍与目标确立: 本集要去哪/为什么/谁同行。"},
        {"label": "关卡式推进·试炼", "mission": "关卡式推进: 一个试炼/一场遭遇, 用规则解决问题而非蛮力。"},
        {"label": "代价与牺牲", "mission": "能力体系的代价显现: 有人付出代价, 规则的可信度在这里建立。"},
        {"label": "新规则新地图解锁", "mission": "结尾解锁一个新规则/新地图, 世界观扩张一格。"},
    ],
    # === 绘本/儿童族 ===
    "绘本故事脚本": [
        {"label": "封面环衬·基调建立", "mission": "封面+环衬: 用画面基调预告故事情绪; 环衬藏一个读完全书才懂的细节。"},
        {"label": "绘本开场·愿望建立", "mission": "主角登场并建立一个明确愿望; 一图一句, 句式简短可朗读。"},
        {"label": "绘本展开·重复句式推进", "mission": "重复句式推进(每次尝试+同一句 refrain), 每次尝试结果不同; 重复是绘本的韵律骨架。"},
        {"label": "绘本波折·小挫折", "mission": "一个小挫折让愿望看似落空; 挫折要轻, 希望不灭。"},
        {"label": "绘本高潮·愿望实现", "mission": "愿望以意料之外的方式实现; 画面情绪到达顶点, 构图/色彩最饱满。"},
        {"label": "绘本收尾·温暖闭环", "mission": "温暖闭环+封底呼应: 最后一页回答封面埋的问题。"},
    ],
    "睡前故事脚本": [
        {"label": "舒缓开场·情绪安抚", "mission": "舒缓开场: 语速慢, 画面柔, 先安抚情绪再进入故事; 无惊吓元素。"},
        {"label": "轻柔冒险·低冲突旅程", "mission": "轻柔冒险: 一段低冲突的小旅程, 每一步都安全可控。"},
        {"label": "小小波折·即时安抚", "mission": "一个小小波折出现后立刻被安抚; 让孩子体验'担心'但马上知道'没事'。"},
        {"label": "安全回归·回到熟悉", "mission": "回到熟悉的地方/人身边, 安全感拉满。"},
        {"label": "晚安仪式·渐慢渐轻", "mission": "晚安仪式: 句式渐慢渐轻, 明确说晚安; 最后一个意象必须是安静温暖的。"},
    ],
    "儿童教育动画脚本": [
        {"label": "知识点开场·提问", "mission": "用一个孩子能理解的问题开场: 今天我们要弄明白什么。"},
        {"label": "探索·第一次试错", "mission": "角色第一次尝试解决问题, 方法直观但不对; 试错本身就是教学。"},
        {"label": "探索·第二次试错", "mission": "换一个方法再试, 接近答案但差一步; 让孩子先于角色想到答案。"},
        {"label": "知识点揭晓·原理可视化", "mission": "知识点揭晓: 用可视化画面讲清原理, 一句话能说清。"},
        {"label": "重复强化·互动提问", "mission": "重复强化+打破第四面墙互动提问: 你学会了吗/你猜接下来会怎样。"},
        {"label": "口诀总结收尾", "mission": "片尾口诀总结: 把知识点编成一句能跟读的口诀。"},
    ],
    # === MV/广告族 ===
    "MV音乐短片脚本": [
        {"label": "前奏·视觉引入", "mission": "前奏段: 视觉引入, 建立世界观/情绪基调, 卡BPM进第一个节奏点。"},
        {"label": "主歌·叙事线建立", "mission": "主歌段: 叙事线建立, 人物与处境交代; 画面节奏跟随节拍。"},
        {"label": "副歌·视觉高光", "mission": "副歌段: 视觉高光+重复记忆点(同一动作/场景的变奏), 副歌=可传播段落。"},
        {"label": "间奏·叙事情感切换", "mission": "间奏段: 叙事线/情感线切换, 用纯视觉推进不靠歌词。"},
        {"label": "桥段·情感转折", "mission": "桥段: 情感转折或视角反转, 为最后副歌蓄力。"},
        {"label": "尾奏·收尾呼应", "mission": "尾奏: 收尾呼应开场意象, 情绪落地或留白。"},
    ],
    "广告宣传片脚本": [
        {"label": "前3秒抓注意", "mission": "前3秒: 一个问题/冲突/奇观抓住注意; 品牌先不出现。"},
        {"label": "卖点呈现(≤3个)", "mission": "卖点呈现: 最多3个卖点, 每个卖点用一个可验证的画面证明。"},
        {"label": "CTA行动号召", "mission": "CTA: 明确的行动号召+品牌露出+口号; 一句话说清'现在该做什么'。"},
    ],
    "品牌故事片脚本": [
        {"label": "人物日常引入", "mission": "人物日常引入: 真实质感, 不硬广; 先让人相信人物, 再谈品牌。"},
        {"label": "价值冲突·选择时刻", "mission": "价值冲突: 人物面临选择, 品牌价值观通过选择显现而非口号。"},
        {"label": "情感积累·真实质感", "mission": "情感积累: 细节堆出真实感, 情绪到位但克制。"},
        {"label": "品牌主张自然升华", "mission": "结尾品牌主张自然升华: 主张从故事里长出来, 不是贴上去。"},
    ],
    "演唱会纪录片脚本": [
        {"label": "开场舞台·第一首", "mission": "开场舞台: 第一首歌完整呈现, 建立现场能量。"},
        {"label": "后台纪实·准备", "mission": "后台纪实: 准备/紧张/仪式, 让观众看到舞台之下的人。"},
        {"label": "高潮曲目·完整呈现", "mission": "高潮曲目: 完整呈现+情绪铺垫, 不剪切打断。"},
        {"label": "采访排练穿插", "mission": "采访/排练/观众反应穿插: 多视角补充现场的意义。"},
        {"label": "观众反应·情绪合唱", "mission": "观众段落: 合唱/泪水/举起的手, 现场属于观众。"},
        {"label": "安可·收尾", "mission": "安可收尾: 最后一首歌+散场后的空镜, 余韵落地。"},
    ],
    # === 纪录片族 ===
    "人物纪录片脚本": [
        {"label": "观察式长镜·人物日常", "mission": "观察式长镜进入人物日常: 不摆拍, 不采访先行, 让观众先'看见'。"},
        {"label": "核心事件浮现", "mission": "核心事件浮现: 人物生活中的真实矛盾显形, 冲突来自真实而非设计。"},
        {"label": "采访穿插·内心揭示", "mission": "采访穿插: 让人物自己说, 旁白克制; 采访回答与观察画面互文。"},
        {"label": "选择时刻·冲突可见", "mission": "选择时刻: 人物做出选择, 性格在取舍中显形。"},
        {"label": "开放结尾·判断留给观众", "mission": "开放结尾: 不给结论, 把判断权留给观众。"},
    ],
    "社会纪录片脚本": [
        {"label": "议题开场·现象呈现", "mission": "议题开场: 用一个具体现象切入议题, 数据后置, 画面先行。"},
        {"label": "个案A·视角一", "mission": "个案A: 第一个当事人的完整故事, 立场之一。"},
        {"label": "个案B·视角二", "mission": "个案B: 与A形成对照的第二个故事, 呈现复杂。"},
        {"label": "结构分析·数据语境", "mission": "结构分析: 数据+专家+语境, 把个案放进结构里解释。"},
        {"label": "碰撞与复杂", "mission": "碰撞段: 立场交锋/利益冲突, 不简化不站队。"},
        {"label": "开放结尾·问题未解", "mission": "开放结尾: 问题未解决, 但观众看问题的方式变了。"},
    ],
    # === 互动/沉浸族 ===
    "互动剧分支剧本": [
        {"label": "主线建立·节点N0", "mission": "主线建立(节点N0): 人物/处境/核心目标; 在观众做出第一次选择前完成代入。"},
        {"label": "选择点一·分支展开", "mission": "选择点一: ≥2个选项, 每个选项有真实代价; 选项差异必须是价值观差异而非信息差异。"},
        {"label": "分支发展·后果分化", "mission": "分支发展: 不同选择导致可见的后果分化; 分支内容不可互换。"},
        {"label": "汇合点或二次选择", "mission": "汇合点(主线回收)或二次选择点(分支加深); 标注回收逻辑。"},
        {"label": "多结局收束", "mission": "多结局收束: ≥2个结局, 每个结局回应开头的核心目标; 结局差异来自选择累积。"},
    ],
    "沉浸式戏剧脚本": [
        {"label": "空间进入·观众即主角", "mission": "空间进入: 观众视角=主角视角; 第一分钟建立'我在这个空间里'的身体感。"},
        {"label": "环境叙事·可探索细节", "mission": "环境叙事: 可探索的细节承载信息(物件/痕迹/声音), 不靠台词交代。"},
        {"label": "视线引导·注意力设计", "mission": "视线引导: 用光线/声音/运动引导注意力; 无剪辑, 用空间调度完成转场。"},
        {"label": "空间转场·无剪辑切换", "mission": "空间转场: 观众被自然移动到下一空间, 转场本身是体验的一部分。"},
        {"label": "终幕·回归现实", "mission": "终幕: 情绪顶点+回归现实的出口设计, 让观众'离开'角色。"},
    ],
    # === 行业垂直族 ===
    "婚礼/活动脚本": [
        {"label": "准备·细节抓取", "mission": "准备段: 化妆/整理/等待的细节; 情绪在细节里, 不在摆拍里。"},
        {"label": "仪式·情感高光", "mission": "仪式段: 誓言/交换/感恩, 情感高光完整保留不剪碎。"},
        {"label": "宴会·互动温度", "mission": "宴会段: 互动/笑声/意外的小温暖, 群像反应镜头。"},
        {"label": "快剪回顾", "mission": "快剪回顾: 全天高光卡音乐节奏回放。"},
        {"label": "收尾·情感落点", "mission": "收尾: 一个安静的落点画面(背影/牵手/空场), 情绪收住。"},
    ],
    "课程教学脚本": [
        {"label": "学习目标开场", "mission": "开场说清学习目标: 学完能做什么; 30秒内给出。"},
        {"label": "讲解段一·概念", "mission": "讲解段一: 核心概念, 每段≤5min; 屏幕标注/字幕配合。"},
        {"label": "示例演示", "mission": "示例/演示: 完整走一遍真实案例, 关键步骤放慢。"},
        {"label": "讲解段二·应用", "mission": "讲解段二: 应用与常见错误; 节奏留暂停点让学员跟练。"},
        {"label": "小结练习收尾", "mission": "小结+练习: 要点回顾+一个可立即做的练习。"},
    ],
    "Vlog脚本": [
        {"label": "第一视角口播开场", "mission": "对镜头口播开场: 今天做什么/为什么值得看; 个人化语气, 手持真实感。"},
        {"label": "体验过程·主线", "mission": "体验过程主线: 按时间推进, 保留真实的反应和对话。"},
        {"label": "空镜插拍·节奏调节", "mission": "空镜/插拍调节节奏: 环境空镜+转场, 给信息密度呼吸。"},
        {"label": "小意外·真实时刻", "mission": "小意外/计划外时刻: 不剪掉, 真实感往往在这里。"},
        {"label": "感受收尾", "mission": "感受收尾: 对镜头说今天的感受, 给观众一个情绪出口。"},
    ],
    "直播脚本": [
        {"label": "开播暖场·福利预告", "mission": "开播暖场: 打招呼+今晚内容预告+福利预告, 留人钩子前置。"},
        {"label": "内容带货段一", "mission": "内容/带货段一: 第一个主题/产品, 话术节点标注(痛点→演示→价格)。"},
        {"label": "互动环节·弹幕福利", "mission": "互动环节: 弹幕问答/抽奖/福利, 防流失钩子。"},
        {"label": "内容带货段二·高潮", "mission": "内容/带货段二: 主推款/核心内容, 情绪与节奏的高潮位。"},
        {"label": "福利兑现·互动峰值", "mission": "福利兑现: 互动峰值, 兑现开播承诺。"},
        {"label": "下播预告收尾", "mission": "下播预告: 下次时间+内容预告, 关注引导。"},
    ],
}


def _apply_format_scene_skeleton(scenes, mode):
    """V14.3 D2: 把形态骨架结构位标注到生成的场次上.

    短形态 (scene_target=骨架槽数) 时一场一槽; 长形态按比例映射 (一槽多场)。
    每场注入: heading 结构位标签 + story_function 覆盖 + action 头部结构任务。
    """
    skel = FORMAT_SCENE_SKELETONS.get(mode)
    if not skel or not scenes:
        return scenes
    n, m = len(scenes), len(skel)
    out = []
    for i, sc in enumerate(scenes):
        slot = skel[min(int(i * m / n), m - 1)]
        sc = dict(sc)
        sc["story_function"] = slot["label"]
        head = (sc.get("heading") or "").strip()
        sc["heading"] = f"{head} 【{slot['label']}】" if head else f"【{slot['label']}】"
        action = (sc.get("action") or "").strip()
        sc["action"] = f"〔结构任务 · {slot['label']}〕{slot['mission']}\n{action}".strip()
        out.append(sc)
    return out


# ---------- V14.3 D2 第二杠杆: 形态专属执行层渲染 ----------
# 把每场的真实场景元素 (地点/物件/动作) 按各形态的制作惯例渲染成执行指令,
# 让同档期形态模式的正文在内容层而不仅是标签层产生结构差异。全部确定性+场景驱动。

def _det_pick(options, seed_str):
    import hashlib as _hl_dp
    return options[int(_hl_dp.md5(seed_str.encode("utf-8", "replace")).hexdigest(), 16) % len(options)]


def _scene_action_brief(sc, limit=40):
    """取 action 首句作为内容摘要 (用于执行层引用)."""
    action = (sc.get("action") or "").strip()
    for ln in action.splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("〔结构任务"):
            return ln[:limit]
    return ""


def _apply_format_execution_layer(scenes, mode, raw_scene):
    """V14.3 D2: 每场追加形态专属执行层 (场景元素驱动, 非编造)."""
    if mode not in FORMAT_SCENE_SKELETONS or not scenes:
        return scenes
    try:
        from aggregator.scene_engine import parse_scene as _ps_fe
        _p = _ps_fe(raw_scene) if raw_scene else {}
    except Exception:
        _p = {}
    ctx_chars = _p.get("characters") or ["主角"]
    ctx_objs = _p.get("objects") or ["关键道具"]
    ctx_loc = _p.get("location") or "主场景"
    c1 = ctx_chars[0]

    out = []
    for i, sc in enumerate(scenes):
        sc = dict(sc)
        loc = sc.get("location") or ctx_loc
        objs = sc.get("objects") or ctx_objs
        obj = str(objs[0]) if objs else "关键道具"
        label = sc.get("story_function") or f"段落{i+1}"
        brief = _scene_action_brief(sc)
        seed = f"{mode}_{raw_scene}_{i}"
        block = ""

        if mode in ("创意玩法短视频", "爆火反转短视频", "脑洞剧情短视频", "情感共鸣短视频", "搞笑整蛊短视频"):
            budget = _det_pick(["3-5镜", "5-8镜", "4-6镜"], seed + "bud")
            first = _det_pick([f"{obj}特写开场", f"{c1}的反常动作开场", f"{loc}空镜+异响开场"], seed + "hook")
            last = _det_pick(["定格0.5s", "黑场0.3s", "循环首尾帧"], seed + "end")
            block = (f"〔{label} · 短视频镜头执行〕镜数预算: {budget} | 场景: {loc} | 记忆物件: {obj}\n"
                     f"  首镜设计: {first} | 收尾: {last}\n"
                     f"  内容锚点: {brief or '本场核心动作'}")
        elif mode in ("番剧动漫剧本", "热血动漫剧本", "校园动漫剧本", "奇幻冒险动漫剧本"):
            sakuga = _det_pick(["本场1个作画cut", "本场2个作画cut", "本场无作画cut(演出补足)"], seed + "sg")
            mono = _det_pick([f"{c1}内心独白1句", "无独白(纯演出)", f"{c1}与环境的静默对视"], seed + "mn")
            block = (f"〔{label} · 动漫演出〕{sakuga} | {mono}\n"
                     f"  场景: {loc} | 关键道具: {obj}\n"
                     f"  演出锚点: {brief or '本场情绪最高点'}")
        elif mode in ("绘本故事脚本", "睡前故事脚本", "儿童教育动画脚本"):
            spread = _det_pick(["跨页大图", "左右分页", "连续小图×3"], seed + "sp")
            text_style = _det_pick(["重复句式(可跟读)", "一句一问(互动)", "轻声叙述(睡前节奏)"], seed + "tx")
            block = (f"〔{label} · 绘本分页〕版式: {spread} | 文字风格: {text_style}\n"
                     f"  画面: {loc}, {obj}\n"
                     f"  本页一句: 围绕「{brief[:20] or '本场核心'}」写一句可朗读的话")
        elif mode == "MV音乐短片脚本":
            bpm = _det_pick(["卡拍切(每2拍1镜)", "长镜跟拍(跨4小节)", "节奏点定格"], seed + "bpm")
            line = _det_pick(["叙事线", "表演线", "叙事+表演交织"], seed + "ln")
            block = (f"〔{label} · MV分段〕音乐同步: {bpm} | 线索: {line}\n"
                     f"  场景: {loc} | 视觉锚点: {obj}")
        elif mode in ("广告宣传片脚本", "品牌故事片脚本"):
            proof = _det_pick(["使用前后对比", "细节微距证明", "真实场景证言"], seed + "pr")
            block = (f"〔{label} · 广告镜头〕卖点画面: {proof}\n"
                     f"  场景: {loc} | 产品/品牌载体: {obj}\n"
                     f"  内容锚点: {brief or '本场核心信息'}")
        elif mode in ("人物纪录片脚本", "社会纪录片脚本", "演唱会纪录片脚本"):
            cam = _det_pick(["观察式长镜(不介入)", "手持跟拍(贴近)", "固定机位+采访正反打"], seed + "cm")
            q = _det_pick(["本场采访问题: 当时你为什么那样选?", "本场采访问题: 那一刻你在想什么?", "本场无采访(纯观察)"], seed + "q")
            block = (f"〔{label} · 纪录片拍法〕机位: {cam}\n"
                     f"  {q}\n"
                     f"  场景: {loc} | 关键物件: {obj}")
        elif mode == "互动剧分支剧本":
            node_id = f"N{i}"
            opt = _det_pick(["2选项(安全/冒险)", "2选项(诚实/隐瞒)", "3选项(含隐藏项)"], seed + "opt")
            block = (f"〔{label} · 分支标注〕节点: {node_id} | 选项设计: {opt}\n"
                     f"  场景: {loc} | 选择代价载体: {obj}\n"
                     f"  节点任务: {brief or '推进主线至下一节点'}")
        elif mode == "沉浸式戏剧脚本":
            pos = _det_pick(["观众站立围观", "观众被引导移动", "观众自由选择视角"], seed + "pos")
            anchor = _det_pick(["光线引导", "声源引导", "演员动线引导"], seed + "an")
            block = (f"〔{label} · 空间设计〕观众位置: {pos} | 注意力锚点: {anchor}\n"
                     f"  空间: {loc} | 可探索细节: {obj}")
        elif mode == "婚礼/活动脚本":
            cams = _det_pick(["机位A正面+B侧拍+C游机", "机位A全景+B特写", "单机位+稳定器游动"], seed + "cam")
            block = (f"〔{label} · 多机位分工〕{cams}\n"
                     f"  场景: {loc} | 情感载体: {obj}")
        elif mode == "课程教学脚本":
            mark = _det_pick(["屏幕圈注关键点", "分步字幕条", "画中画演示"], seed + "mk")
            pause = _det_pick(["本段后留3s暂停点", "本段中插1个提问", "本段无暂停(连贯演示)"], seed + "ps")
            block = (f"〔{label} · 屏幕标注〕{mark} | {pause}\n"
                     f"  演示对象: {obj} | 场景: {loc}")
        elif mode == "Vlog脚本":
            talk = _det_pick(["对镜头说感受30s", "边走边说(手持)", "画外音+现场声交替"], seed + "tk")
            block = (f"〔{label} · 口播稿〕形式: {talk}\n"
                     f"  场景: {loc} | 拍摄对象: {obj}\n"
                     f"  口播锚点: {brief or '本段体验的核心感受'}")
        elif mode == "直播脚本":
            track = _det_pick(["痛点→演示→价格 三段话术", "故事引入→产品亮相", "互动提问→福利钩子"], seed + "tr")
            block = (f"〔{label} · 话术节点〕{track}\n"
                     f"  展示物: {obj} | 场景布置: {loc}")

        if block:
            action = (sc.get("action") or "").strip()
            sc["action"] = f"{action}\n{block}" if action else block
        out.append(sc)
    return out


# ---------- V14.3 D3: 互动剧真实分支树 ----------

def _build_interactive_branch_tree(raw_scene, mood, core):
    """V14.3 D3: 从场景元素确定性生成可解析的互动剧分支树.

    结构: N0 主线 → N1 选择点一 (≥2选项, 价值观差异+真实代价) → N1A/N1B 分支
          → N2 汇合+二次选择 → E1/E2/E3 多结局。全部 target 可解析, 无悬空引用。
    """
    import json as _json_bt
    try:
        from aggregator.scene_engine import parse_scene as _ps_bt
        p = _ps_bt(raw_scene) if raw_scene else {}
    except Exception:
        p = {}
    chars = p.get("characters") or ["主角", "对手"]
    objs = p.get("objects") or ["关键道具"]
    loc = p.get("location") or "主场景"
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else "另一个人"
    obj = objs[0]
    obj2 = objs[1] if len(objs) > 1 else obj
    title = (core.get("_项目名", "未命名互动剧") if core else "未命名互动剧")
    intent = (core.get("_导演意图_观众应感到", "") if core else "")

    def _pick(options, salt):
        import hashlib as _hl_bt
        return options[int(_hl_bt.md5(f"{raw_scene}_{salt}".encode("utf-8", "replace")).hexdigest(), 16) % len(options)]

    # 选择点一: 围绕核心物件的价值观抉择 (说出/隐瞒/交出/销毁 四选二)
    d1_opts = [
        {"text": f"把{obj}的真相告诉{c2}", "cost": f"失去{c2}此刻的信任, 但换来后续坦诚的可能", "value": "诚实"},
        {"text": f"隐瞒{obj}的真相, 独自承担", "cost": "秘密成为两人之间的墙, 每次对视都在加码", "value": "保护"},
        {"text": f"把{obj}交给{c2}处置", "cost": "放弃主导权, 结果完全取决于对方", "value": "信任"},
        {"text": f"当面销毁{obj}", "cost": "真相永远无法被证实, 所有人都将怀疑你", "value": "决绝"},
    ]
    import hashlib as _hl_bt2
    _h = int(_hl_bt2.md5(f"{raw_scene}_d1".encode("utf-8", "replace")).hexdigest(), 16)
    o1 = d1_opts[_h % len(d1_opts)]
    o2 = d1_opts[(_h + 1 + _h % 2) % len(d1_opts)]
    if o2["text"] == o1["text"]:
        o2 = d1_opts[(_h + 2) % len(d1_opts)]

    # 分支后果 (不可互换): A 线走向坦白后的连锁反应, B 线走向隐瞒后的压力升级
    branch_a = (f"{c1}选择'{o1['value']}': {o1['text']}。{loc}里, {c2}的反应超出预期 — "
                f"{_pick(['沉默比指责更重', '一句反问让局面反转', '转身离开, 留下未说完的话'], 'ba')}; "
                f"{obj}成为两人之间新的悬置。")
    branch_b = (f"{c1}选择'{o2['value']}': {o2['text']}。代价立刻显形 — "
                f"{_pick(['每个细节都在圆谎, 越圆越深', '第三个人注意到了破绽', f'{obj2}意外出现, 差点暴露一切'], 'bb')}; "
                f"压力在{loc}的封闭空间里持续升级。")

    # 二次选择 (汇合点): 两条线在此收拢, 面对同一个终局抉择
    d2_opts = [
        {"text": "在所有人面前还原全部真相", "cost": "承担全部后果, 关系重建或彻底破裂", "target": "E1"},
        {"text": f"只向{c2}一个人坦白, 其余永远封存", "cost": "保住大局, 但秘密变成两人共有的债", "target": "E2"},
        {"text": "让真相随时间自然浮现, 不再主动干预", "cost": "把裁决权交给时间, 可能等来原谅也可能等来爆发", "target": "E3"},
    ]
    _h2 = int(_hl_bt2.md5(f"{raw_scene}_d2".encode("utf-8", "replace")).hexdigest(), 16)
    n2_options = [d2_opts[_h2 % 3], d2_opts[(_h2 + 1) % 3]]
    if n2_options[0]["text"] == n2_options[1]["text"]:
        n2_options[1] = d2_opts[(_h2 + 2) % 3]

    endings = {
        "E1": {"label": "结局·真相大白", "summary": f"全部真相在{loc}被还原; {c1}承担后果, {c2}做出最终回应 — 关系在废墟上重建或彻底终结。情绪落点: {mood}的释放。"},
        "E2": {"label": "结局·共有之债", "summary": f"真相只存在于{c1}与{c2}之间; 表面如常, 但每次看到{obj}都是一次无声提醒。情绪落点: {mood}的余震。"},
        "E3": {"label": "结局·时间裁决", "summary": f"{c1}不再干预, 真相以不可控的方式浮现; 结局不由主角决定。情绪落点: {mood}的悬置。"},
    }

    tree = {
        "title": title,
        "mode": "互动剧分支剧本",
        "director_intent": intent,
        "nodes": [
            {"id": "N0", "type": "mainline", "label": "主线建立",
             "summary": f"{loc}: {c1}与{c2}因{obj}陷入同一处境; 核心目标在第一次选择前建立。",
             "next": "N1"},
            {"id": "N1", "type": "choice", "label": "选择点一",
             "question": f"关于{obj}的真相, {c1}怎么办?",
             "options": [
                 {"text": o1["text"], "value_axis": o1["value"], "cost": o1["cost"], "target": "N1A"},
                 {"text": o2["text"], "value_axis": o2["value"], "cost": o2["cost"], "target": "N1B"},
             ]},
            {"id": "N1A", "type": "branch", "label": f"分支A·{o1['value']}", "summary": branch_a, "next": "N2"},
            {"id": "N1B", "type": "branch", "label": f"分支B·{o2['value']}", "summary": branch_b, "next": "N2"},
            {"id": "N2", "type": "choice", "label": "汇合点·二次选择",
             "question": "两条线的后果在此收拢, 终局抉择只有一个:",
             "options": [{"text": o["text"], "cost": o["cost"], "target": o["target"]} for o in n2_options]},
            {"id": "E1", "type": "ending", **endings["E1"]},
            {"id": "E2", "type": "ending", **endings["E2"]},
            {"id": "E3", "type": "ending", **endings["E3"]},
        ],
        "merge_points": ["N2"],
        "endings": ["E1", "E2", "E3"],
        "stats": {
            "nodes": 8,
            "choice_points": 2,
            "options_total": 2 + len(n2_options),
            "endings": 3,
            "branch_depth": 2,
        },
    }
    return _json_bt.dumps(tree, ensure_ascii=False, indent=2)


def _build_aigc_five_section(scene, director, mood, core, scenes, dims):
    """V16.1: 短形态 AIGC 五段结构块 (Mx-Shell 方法) — 把场次转为时间拍 + 五段外壳.
    写法A(时间切片)用于单镜/长镜, 写法B(分镜四件套)用于多分镜。这里按时间拍输出。"""
    try:
        from aggregator.scene_engine import parse_scene as _ps5
        _parsed = _ps5(scene) if scene else {}
    except Exception:
        _parsed = {}
    chars = _parsed.get("characters") or ["主角"]
    era_ctx = {"scene": scene, "director": director, "mood": mood,
               "characters": chars, "platform": dims.get("平台", ""),
               "era": _aigc_pb.detect_era({"scene": scene})}
    # 把场次转为时间拍 (每场一拍, 时长均分)
    n = max(1, len(scenes))
    total_sec = max(5.0, float((core.get("_成片秒", 0) if core else 0) or 0))
    if total_sec <= 0:
        # 从 target 推断 (短形态 ≤3min → 取 30s 作为示范基准)
        total_sec = 30.0
    per = total_sec / n
    beats = []
    t0 = 0.0
    for sc in scenes:
        action = str(sc.get("action", "") or "").split("\n")[0][:60]
        dial = sc.get("dialogues") or []
        dial_txt = ""
        if dial:
            try:
                who, paren, line = dial[0]
                dial_txt = f"{who}:「{line}」"
            except Exception:
                dial_txt = ""
        beats.append({
            "name": str(sc.get("story_function", "推进"))[:12],
            "time": f"{t0:.0f}-{t0 + per:.0f}秒",
            "action": action or dial_txt,
            "camera": "按分镜表执行",
            "sound": "",
        })
        t0 += per
    # 结尾元素: 取最后一场的物件
    ending_elem = ""
    if scenes:
        objs = scenes[-1].get("objects") or []
        ending_elem = objs[0] if objs else "环境声"
    single_shot = (n <= 2)
    return _aigc_pb.build_five_section_block(era_ctx, beats, single_shot=single_shot,
                                             ending_elem=ending_elem)


def _build_full_screenplay(scene, director, mood, core, target_minutes=120, story_theory="三幕剧", dims=None, mode=None):
    """完整剧本 — 专业剧本格式 + 架构 + 角色弧. 可直接拍摄.
    V12.6 v9: target_minutes 决定 35场/26场/18场/9场 长/中/短片体量.
    V13.3: dims (对白密度/潜文本强度/节奏控制/主题深度) 真实生效.
    """
    from aggregator.pro_format import format_screenplay, build_standard_screenplay_scenes, strip_decor
    dims = dims or {}
    title = core.get("_项目名", "未命名项目") if core else "未命名项目"
    intent = core.get("_导演意图_观众应感到", "") if core else ""
    # V13.2: 从核心数据包继承情绪演变弧 (多选), 按叙事进度推进场次情绪
    mood_arc = core.get("_情绪演变弧") if core else None
    if not isinstance(mood_arc, list) or not mood_arc:
        mood_arc = None

    # V13.3: 节奏控制 → 场次体量缩放 (慢节奏=更少更长的场, 快节奏=更多更短的场)
    rhythm = dims.get("节奏控制", "")
    eff_minutes = target_minutes
    if any(k in rhythm for k in ["极慢", "慢("]):
        eff_minutes = int(target_minutes * 0.75)
    elif any(k in rhythm for k in ["极快", "快("]):
        eff_minutes = int(target_minutes * 1.3)

    # V13.3: 对白密度 → 覆盖每场对白密度 (零对白=无对白)
    dial = dims.get("对白密度", "")
    dial_override = None
    if "零对白" in dial:
        dial_override = "none"
    elif any(k in dial for k in ["极简", "稀疏", "默片"]):
        dial_override = "low"
    elif any(k in dial for k in ["密集", "台词密集", "独白"]):
        dial_override = "high"
    elif "适中" in dial or "标准" in dial:
        dial_override = "mid"

    # V14.3 D2: 形态骨架真实下场 — 短形态 (≤24min) 场数=骨架槽数, 全部形态标注结构位
    _skel = FORMAT_SCENE_SKELETONS.get(mode)
    _scene_target = len(_skel) if (_skel and target_minutes <= 24) else None
    _scenes = build_standard_screenplay_scenes(scene, director, mood, intent, eff_minutes, story_theory,
                                               mood_arc=mood_arc, dial_override=dial_override,
                                               mode_seed=mode or "", scene_target=_scene_target)
    _scenes = _apply_format_scene_skeleton(_scenes, mode)
    _scenes = _apply_format_execution_layer(_scenes, mode, scene)

    # === V16.1: 叙事编排 — 把节拍时序重排为银幕时序 + 时间线/线索标注注入场次头 ===
    _arrangement = dims.get("叙事编排", "跟随叙事结构")
    _line_mode = dims.get("叙事线型", "单线")
    _arrange_plan = {}
    if _scenes:
        try:
            _ordered, _arrange_plan = arrange_scenes(_scenes, _arrangement, _line_mode,
                                                     seed=f"{scene}_{director}_{mode}")
            # 时间线/线索/编排批注 注入每场 heading (只标注非"现在"或非"A"线, 避免噪声)
            for sc in _ordered:
                tl = sc.get("timeline", "现在")
                ln = sc.get("line", "A")
                pov = sc.get("pov", "全知")
                tags = []
                if tl and tl != "现在":
                    tags.append(f"时间线:{tl}")
                if ln and ln != "A":
                    tags.append(f"线:{ln}")
                if pov and pov not in ("全知", "") and _line_mode == "POV切换":
                    tags.append(f"POV:{pov}")
                if tags:
                    sc["heading"] = f"{sc.get('heading','')}  [{' | '.join(tags)}]"
                if sc.get("arrangement_note"):
                    sc["heading"] = f"{sc.get('heading','')}\n    〔编排: {sc['arrangement_note']}〕"
            _scenes = _ordered
        except Exception as _ar_e:
            import sys as _ar_s
            _ar_s.stderr.write(f"[DirectorMaster] 叙事编排降级: {type(_ar_e).__name__}\n")

    screenplay = format_screenplay(title, director, mood, intent, _scenes,
                                    subtext_strength=dims.get("潜文本强度", "强"))
    # 架构 + 角色弧 (清洁版, 去装饰符)
    arch = strip_decor(_build_architecture_template(scene, director, mood, core))
    char = strip_decor(_build_character_template(scene, director, mood, core))
    out = f"{screenplay}\n\n{'─'*40}\n【剧本架构】\n{arch}\n\n{'─'*40}\n【角色弧光】\n{char}"

    # V16.1 注: 导演叙事设计块 + AIGC 五段结构 已提升到 build() 层统一追加 (对所有模式生效),
    # 此处仅保留场次重排 + heading 时间线/线索标注。

    # V13.3: 主题深度 → 主题陈述块 (深/极深/存在主义 才展开哲学内核)
    depth = dims.get("主题深度", "")
    theme = core.get("_主题词", "") if core else ""
    if theme and any(k in depth for k in ["深", "极深", "存在主义", "形而上"]):
        out += (
            f"\n\n{'─'*40}\n【主题陈述 · {depth}】\n"
            f"主题词: {theme}\n"
            f"哲学内核: '{theme}'在本片中不是被说出的, 而是被{scene.split(',')[0] if scene else '场景'}中的人物活出来的.\n"
            f"表达原则: 主题藏在选择里——人物每次取舍都在回答'{theme}'是什么.\n"
            f"结尾不给答案: 把'{theme}'的判断权留给观众."
        )
    # V14.2: 形态类模式专属格式约定 (修复同档期形态模式正文坍缩)
    flavor = FORMAT_MODE_FLAVOR.get(mode)
    if flavor:
        out += f"\n\n{'─'*40}\n{flavor}"
    # V14.3 D3: 互动剧真实分支树 (节点/选项/汇合/结局 JSON, 选项≥2/节点, 无悬空引用)
    if mode == "互动剧分支剧本":
        try:
            out += f"\n\n{'─'*40}\n【分支树 JSON (可解析)】\n{_build_interactive_branch_tree(scene, mood, core)}"
        except Exception as _bt_e:
            import sys as _bt_s
            _bt_s.stderr.write(f"[DirectorMaster] 分支树生成降级: {type(_bt_e).__name__}\n")
    return out


TEMPLATE_BUILDERS = {
    "完整剧本": _build_full_screenplay,
    "剧本架构": _build_architecture_template,
    "剧本正文": _build_script_body_template,
    "导演分镜": _build_storyboard_template,
    "钩子大师": _build_hook_template,
    "对白大师": _build_dialogue_template,
    "角色弧光": _build_character_template,
    "垂直短剧": _build_short_drama_template,
    # V13 修复 (B-P0): SCRIPT_MODES 里的短剧/微短剧/小程序剧模式接入短剧 builder,
    # 避免落回 _build_full_screenplay 导致"短剧生成电影剧本"的类型失败
    "横屏微短剧": _build_short_drama_template,
    "单元剧短剧": _build_short_drama_template,
    "系列短剧": _build_short_drama_template,
    "竖屏微短剧": _build_short_drama_template,
    "女频甜宠竖屏": _build_short_drama_template,
    "男频逆袭竖屏": _build_short_drama_template,
    "古风竖屏短剧": _build_short_drama_template,
    "竖屏小程序剧": _build_short_drama_template,
    "爽剧小程序": _build_short_drama_template,
    "反转小程序": _build_short_drama_template,
}

# V14.1: 结构类模式 → 故事理论映射 (修复模式坍缩: 结构模式此前全落到默认三幕剧)。
# 模式名驱动叙事结构, 而非仅靠"叙事结构"下拉。
# V14.2 修正: 移除"完整长片剧本" — 它是通用模式, 叙事结构下拉应真实生效 (此前被静默覆盖为三幕剧)。
#   其余以结构命名的模式 (三幕剧长片/五幕剧长片/...) 结构即模式定义, 锁定结构属设计内。
STRUCTURE_THEORY_MAP = {
    "三幕剧长片": "三幕剧",
    "五幕剧长片": "五幕剧",
    "救猫咪15拍长片": "救猫咪15拍",
    "英雄之旅12阶段": "英雄之旅12阶段",
    "麦基故事价值长片": "麦基故事价值",
}

# V14.1: 形态类模式 → 默认时长映射 (修复模式坍缩: 形态模式此前全生成 120min 电影长片)。
# 模式名驱动剧本体量 (Vlog 3-10min / 绘本 5-10min / MV 3-5min / 纪录片 60-90min 等)。
FORMAT_DURATION_MAP = {
    "创意玩法短视频": 1, "爆火反转短视频": 1, "脑洞剧情短视频": 2,
    "情感共鸣短视频": 2, "搞笑整蛊短视频": 2,
    "番剧动漫剧本": 24, "热血动漫剧本": 24, "校园动漫剧本": 24, "奇幻冒险动漫剧本": 24,
    "绘本故事脚本": 8, "睡前故事脚本": 6, "儿童教育动画脚本": 10,
    "MV音乐短片脚本": 4, "广告宣传片脚本": 1, "品牌故事片脚本": 2, "演唱会纪录片脚本": 90,
    "人物纪录片脚本": 75, "社会纪录片脚本": 90,
    "互动剧分支剧本": 30, "沉浸式戏剧脚本": 45,
    "婚礼/活动脚本": 8, "课程教学脚本": 20, "Vlog脚本": 6, "直播脚本": 45,
}


class DirectorMasterScript(DirectorNodeBase):
    """剧本链聚合节点 — 8 合 1 (含完整剧本)."""
    NODE_TYPE = "剧本"

    @classmethod
    def INPUT_TYPES(cls):
        _ND = "无(默认)"  # V12.6 v7 fix: 兼容老版本 saved workflow
        _R  = "🎲 随机"    # V12.6 v8: 随机选择
        return {"required": {
            "剧本模式": (SCRIPT_MODES+[_R], {"default": "完整长片剧本"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "从核心数据包继承, 此处可单独覆盖"}),
            "叙事结构": ([_ND, _R,
                # === 经典剧作理论 (救猫咪+麦基+菲尔德) ===
                "三幕剧(经典)", "三幕剧(变体)", "四幕剧", "五幕剧(莎士比亚)", "七点结构",
                "救猫咪15拍(Blake Snyder)", "救猫咪10类型(鬼怪屋/金羊毛/如愿以偿等)",
                "起承转合(中式四段)", "英雄之旅12阶段(Campbell)", "麦基故事价值(McKee)",
                "皮克斯22条故事法则", "序列剧25场序列(Field)",
                # === 现代叙事变体 ===
                "双线并行", "三线交织", "POV多视角切换", "非线性(闪回/闪前)",
                "循环叙事(开端=结尾)", "碎片叙事", "章节式(每章独立节奏)",
                # === 类型化叙事 ===
                "悬疑推理(线索递进)", "惊悚(悬念递进)", "恐怖(恐惧升级)",
                "喜剧(误会递进)", "爱情(关系递进)", "动作(任务递进)",
                "史诗(命运递进)", "黑色电影(道德下坠)", "公路片(旅程递进)",
                "反英雄(道德模糊)", "成长(蜕变递进)", "复仇(快意递进)",
            ], {"default": _ND, "tooltip": "30+ 叙事结构 — 经典+现代+类型化"}),
            "叙事编排": ([_ND, _R] + [m for m in ARRANGEMENT_MODES if m != "跟随叙事结构"], {
                "default": _ND,
                "tooltip": "★ V16.1 叙事编排 — 把节拍时序重排为银幕时序。正叙=按时间推进; "
                           "倒叙(结果先行)=先给结局碎片再回溯; 穿插倒叙=现在线+情感谷峰处闪回; "
                           "穿插乱叙=钩子开场+中段多时间线打散; 循环叙事=终点即起点。ND=跟随叙事结构原生顺序"}),
            "叙事线型": ([_ND, _R] + [m for m in NARRATIVE_LINE_MODES if m != "单线"], {
                "default": _ND,
                "tooltip": "★ V16.1 叙事线型 — 单线=一条主线贯穿; 双线并行=A线外部目标+B线内部情感, 中点/高潮合流; "
                           "三线交织=三组人物命运交叉; POV切换=同一事件多视角折射。ND=单线"}),
            "对白密度": ([_ND, _R,
                # === 按密度分层 ===
                "零对白(纯视觉)", "极简(≤10字/句, ≤10句/场)", "精简(≤20字/句, ≤30句/场)",
                "稀疏(默片式留白)", "适中(标准对白)", "密集(快节奏对话)",
                "台词密集(舞台剧式)", "独白为主(内心戏)",
                # === 按风格分层 ===
                "方言对白", "古文对白(古装)", "诗化对白(文艺片)",
                "方言+俚语(地域感)", "文言+白话(时代感)", "专业术语(行业剧)",
                "网络用语(现代)", "英汉夹杂(国际化)",
            ], {"default": _ND, "tooltip": "16+ 对白密度 — 密度分层+风格分层"}),
            "潜文本强度": ([_ND, _R,
                "零潜文本(直白)", "弱(表层意思为主)", "中(每句1层潜文本)",
                "强(每句2-3层潜文本)", "极强(字字潜文本, 影评级)",
                # === 潜文本技法 ===
                "潜文本+潜动作", "潜文本+沉默", "潜文本+反讽", "潜文本+旁白",
                "潜文本+画面隐喻", "潜文本+声音暗示", "潜文本+物件承载",
            ], {"default": _ND, "tooltip": "12+ 潜文本强度 — 强度分层+技法分层"}),
            "节奏控制": ([_ND, _R,
                # === 按速度 ===
                "极慢(长镜头1-3min)", "慢(长镜为主0.5-1min)", "中速(标准)",
                "快(频繁切镜2-5s)", "极快(MV式1-2s/镜)", "超快(抖音1s/镜)",
                "变速(快慢交替)", "递进加速(起慢终快)", "递进减速(起快终慢)",
                # === 按模式 ===
                "动静交替", "留白呼吸(长停顿)", "连续切镜(动作戏)",
                "跳切(意识流)", "匹配剪辑", "L型剪辑", "J型剪辑", "动作顺剪",
            ], {"default": _ND, "tooltip": "16+ 节奏控制 — 速度分层+模式分层"}),
            "主题深度": ([_ND, _R,
                # === 按深度 ===
                "纯娱乐(无主题)", "浅(表层故事)", "中(人物成长)", "深(人性剖析)",
                "极深(哲学内核)", "存在主义(荒诞/自由/死亡)", "形而上学(本质/意义)",
                # === 按主题类型 ===
                "爱情主题", "家庭主题", "成长主题", "复仇主题", "救赎主题",
                "牺牲主题", "信仰主题", "孤独主题", "时间主题", "记忆主题",
                "身份主题", "自由主题", "正义主题", "战争与和平", "人性善恶",
                "社会批判", "文化冲突", "代际冲突", "科技伦理", "生态主题",
            ], {"default": _ND, "tooltip": "20+ 主题深度 — 深度分层+主题类型分层"}),

        }, "optional": {
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承场景/导演/情绪/灵魂/AI/反AI"}),
            "创意输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Vibe.创意 — 注入概念/主题/对标/片名"}),
            "美术输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Art.美术 — 注入色调/光影/材质细节"}),
            "声音输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Sound.声音 — 注入环境音/拟音/留白节奏"}),
            "角色输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Characters.角色圣经 — 角色设定注入对白/动作"}),
            "资产输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Asset.资产设定 — 道具/环境设定注入叙事"}),
            "目标时长(分钟)": ("FLOAT", {"default": 0, "min": 0, "max": 240, "step": 0.05,
                "tooltip": "★ 目标成片时长(分钟). V16.0: 支持秒级 (0.25=15秒, 0.5=30秒, 1=60秒). 0=自动(形态模式用其典型时长, 否则用核心数据包成片时长). 短视频用小数, 长片用整数."}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("剧本",)
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/剧本"

    def build(self, **kwargs):
        core = parse_core_pack(kwargs.get("核心数据包",""))
        mode = kwargs.get("剧本模式","完整剧本")
        # V16.0 需求1: 模式选择器支持 🎲 随机; V16.3: 由核心包随机种子驱动 (固定种子可复现, 种子0真随机)
        if mode == "🎲 随机":
            mode = resolve_dropdown(mode, "完整剧本", SCRIPT_MODES,
                                    seed=derive_seed(core.get("_随机种子"), "剧本模式"))
        if mode not in SCRIPT_MODES: mode = "完整剧本"
        scene = core.get("_场景描述") or kwargs.get("场景描述","")
        director = core.get("_导演风格") or kwargs.get("导演风格","王家卫")
        mood = core.get("_情绪基调","孤独")
        anti_ai = kwargs.get("启用反AI规则", core.get("_启用反AI规则", True) if core else True)

        # V12.6 v9: 目标时长 (决定 35场/26场/18场/9场 长/中/短片体量)
        # 优先级: 核心数据包._成片时长 > 节点输入 target_minutes > 默认 120
        runtime_str = core.get("_成片时长", "")
        target_minutes = 120
        if runtime_str:
            import re as _re_runtime
            # V13 修复 (A-02): 兼容 "90分钟"/"90min"/"8-15分钟" — 取最大数字
            _nums = _re_runtime.findall(r"(\d+)", str(runtime_str))
            if _nums:
                target_minutes = max(int(x) for x in _nums)
        tm_input = kwargs.get("目标时长(分钟)", None)
        if tm_input is not None and str(tm_input).strip() not in ("", "0", "None"):
            try: target_minutes = float(tm_input)
            except: pass
        # V16.0 需求2: 秒级支持 — 短时长(<20min)直通小数, 长时长归一标准桶
        if target_minutes >= 110: target_minutes = 120
        elif target_minutes >= 80: target_minutes = 90
        elif target_minutes >= 50: target_minutes = 60
        elif target_minutes >= 20: target_minutes = 30
        elif target_minutes > 0: target_minutes = max(0.05, target_minutes)  # 短视频保留小数(秒级)

        # V14.1: 形态类模式驱动时长 — 用户未显式设 目标时长 时, 用模式的典型时长
        # (修复模式坍缩: Vlog/绘本/MV/纪录片 等形态模式此前全生成 120min 电影长片)
        _tm_explicit = kwargs.get("目标时长(分钟)", None)
        _tm_explicit_set = _tm_explicit is not None and str(_tm_explicit).strip() not in ("", "0", "None")
        if (not _tm_explicit_set) and mode in FORMAT_DURATION_MAP:
            target_minutes = FORMAT_DURATION_MAP[mode]

        # V12.6 v8: 5 个下拉框全部解析 (支持 "无(默认)" + "🎲 随机"); V16.3 各域独立盐种子驱动
        _STORY_OPTS = ["三幕剧(经典)", "三幕剧(变体)", "四幕剧", "五幕剧(莎士比亚)", "七点结构",
                "救猫咪15拍(Blake Snyder)", "救猫咪10类型(鬼怪屋/金羊毛/如愿以偿等)",
                "起承转合(中式四段)", "英雄之旅12阶段(Campbell)", "麦基故事价值(McKee)",
                "皮克斯22条故事法则", "序列剧25场序列(Field)",
                "双线并行", "三线交织", "POV多视角切换", "非线性(闪回/闪前)",
                "循环叙事(开端=结尾)", "碎片叙事", "章节式(每章独立节奏)",
                "悬疑推理(线索递进)", "惊悚(悬念递进)", "恐怖(恐惧升级)",
                "喜剧(误会递进)", "爱情(关系递进)", "动作(任务递进)",
                "史诗(命运递进)", "黑色电影(道德下坠)", "公路片(旅程递进)",
                "反英雄(道德模糊)", "成长(蜕变递进)", "复仇(快意递进)"]
        _DIAL_OPTS = ["零对白(纯视觉)", "极简(≤10字/句, ≤10句/场)", "精简(≤20字/句, ≤30句/场)",
                "稀疏(默片式留白)", "适中(标准对白)", "密集(快节奏对话)",
                "台词密集(舞台剧式)", "独白为主(内心戏)",
                "方言对白", "古文对白(古装)", "诗化对白(文艺片)",
                "方言+俚语(地域感)", "文言+白话(时代感)", "专业术语(行业剧)",
                "网络用语(现代)", "英汉夹杂(国际化)"]
        _SUBT_OPTS = ["零潜文本(直白)", "弱(表层意思为主)", "中(每句1层潜文本)",
                "强(每句2-3层潜文本)", "极强(字字潜文本, 影评级)",
                "潜文本+潜动作", "潜文本+沉默", "潜文本+反讽", "潜文本+旁白",
                "潜文本+画面隐喻", "潜文本+声音暗示", "潜文本+物件承载"]
        _RHYTHM_OPTS = ["极慢(长镜头1-3min)", "慢(长镜为主0.5-1min)", "中速(标准)",
                "快(频繁切镜2-5s)", "极快(MV式1-2s/镜)", "超快(抖音1s/镜)",
                "变速(快慢交替)", "递进加速(起慢终快)", "递进减速(起快终慢)",
                "动静交替", "留白呼吸(长停顿)", "连续切镜(动作戏)",
                "跳切(意识流)", "匹配剪辑", "L型剪辑", "J型剪辑", "动作顺剪"]
        _THEME_OPTS = ["纯娱乐(无主题)", "浅(表层故事)", "中(人物成长)", "深(人性剖析)",
                "极深(哲学内核)", "存在主义(荒诞/自由/死亡)", "形而上学(本质/意义)",
                "爱情主题", "家庭主题", "成长主题", "复仇主题", "救赎主题",
                "牺牲主题", "信仰主题", "孤独主题", "时间主题", "记忆主题",
                "身份主题", "自由主题", "正义主题", "战争与和平", "人性善恶",
                "社会批判", "文化冲突", "代际冲突", "科技伦理", "生态主题"]
        kwargs["叙事结构"] = resolve_dropdown(kwargs.get("叙事结构"), "三幕剧(经典)", _STORY_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本叙事结构"))
        kwargs["对白密度"] = resolve_dropdown(kwargs.get("对白密度"), "适中(标准对白)", _DIAL_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本对白密度"))
        kwargs["潜文本强度"] = resolve_dropdown(kwargs.get("潜文本强度"), "中(每句1层潜文本)", _SUBT_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本潜文本强度"))
        kwargs["节奏控制"] = resolve_dropdown(kwargs.get("节奏控制"), "中速(标准)", _RHYTHM_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本节奏控制"))
        kwargs["主题深度"] = resolve_dropdown(kwargs.get("主题深度"), "中(人物成长)", _THEME_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本主题深度"))
        # V16.1: 叙事编排 + 叙事线型 下拉解析 (支持 🎲 随机; ND 时回退核心数据包继承值)
        _ARRANGE_OPTS = [m for m in ARRANGEMENT_MODES if m != "跟随叙事结构"]
        _LINE_OPTS = [m for m in NARRATIVE_LINE_MODES if m != "单线"]
        _core_arrange = (core.get("_叙事编排", "跟随叙事结构") if core else "跟随叙事结构") or "跟随叙事结构"
        _core_line = (core.get("_叙事线型", "单线") if core else "单线") or "单线"
        kwargs["叙事编排"] = resolve_dropdown(kwargs.get("叙事编排"), _core_arrange, _ARRANGE_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本叙事编排"))
        kwargs["叙事线型"] = resolve_dropdown(kwargs.get("叙事线型"), _core_line, _LINE_OPTS, seed=derive_seed(core.get("_随机种子"), "剧本叙事线型"))

        # V12.6 v8: 5 个维度值应用到上下文 (供模板使用)
        story_theory = kwargs["叙事结构"]
        dialogue_density = kwargs["对白密度"]
        subtext_strength = kwargs["潜文本强度"]
        rhythm_control = kwargs["节奏控制"]
        theme_depth = kwargs["主题深度"]
        narrative_arrangement = kwargs["叙事编排"]
        narrative_line = kwargs["叙事线型"]

        # V14.1: 结构类模式驱动叙事结构 — 模式名优先于"叙事结构"下拉
        # (修复模式坍缩: 三幕剧长片/五幕剧长片/救猫咪15拍长片 等此前全落到默认三幕剧)
        if mode in STRUCTURE_THEORY_MAP:
            story_theory = STRUCTURE_THEORY_MAP[mode]

        # 上游 5 路 forceInput
        vibe_in = kwargs.get("创意输入","")
        art_in = kwargs.get("美术输入","")
        sound_in = kwargs.get("声音输入","")
        chars_in = kwargs.get("角色输入","")
        asset_in = kwargs.get("资产输入","")

        # === V12.6 解析 5 维 forceInput → 结构化 anchors ===
        vibe_a = _parse_vibe_anchors(vibe_in)
        art_a = _parse_art_anchors(art_in)
        sound_a = _parse_sound_anchors(sound_in)
        char_a = _parse_char_anchors(chars_in)
        asset_a = _parse_asset_anchors(asset_in)

        # === V12.6 v7: 8 故事理论节拍点 + 3D 空间坐标 + 角色 Want/Need/弧光 全部解析 ===
        story_beats_text = _parse_story_beats(story_theory)
        spatial_3d_text = _parse_spatial_3d(scene)
        char_arcs = _parse_character_want_need(chars_in)

        # 5 维增强版场景
        enhanced_scene = _render_scene_with_upstream(scene, vibe_a, art_a, sound_a, char_a, asset_a)

        # 内置深度模板 — V12.6 v9: 传 target_minutes 和 story_theory 给 builder
        builder = TEMPLATE_BUILDERS.get(mode, _build_full_screenplay)
        # V13.3: 把 4 个维度下拉真实传入生成器 (此前 resolve 后成死变量)
        dims = {
            "对白密度": dialogue_density,
            "潜文本强度": subtext_strength,
            "节奏控制": rhythm_control,
            "主题深度": theme_depth,
            # V16.1: 叙事编排 + 叙事线型 传入生成器 (场次重排 + 时间线标注)
            "叙事编排": narrative_arrangement,
            "叙事线型": narrative_line,
            "场景": scene,
            "平台": (core.get("_平台媒介", "") if core else ""),
        }
        try:
            main = builder(enhanced_scene, director, mood, core, target_minutes, story_theory, dims, mode=mode)
        except TypeError:
            try:
                main = builder(enhanced_scene, director, mood, core, target_minutes, story_theory, dims)
            except TypeError:
                try:
                    main = builder(enhanced_scene, director, mood, core, target_minutes, story_theory)
                except TypeError:
                    # 旧 builder 不支持新参数 (保持兼容)
                    main = builder(enhanced_scene, director, mood, core)
        # === 5 维 anchors 真正整合进剧本内容字段 ===
        main = _integrate_5d_into_screenplay_content(main, vibe_a, art_a, sound_a, char_a, asset_a, mode)
        main += self._director_block(director)
        from aggregator.dimensions import apply_dimensions
        main += "\n\n" + apply_dimensions("剧本", kwargs)
        main += "\n\n" + build_life_texture(scene, mood, director)
        main += "\n\n" + build_edit_decision_text(scene, director, mood)

        # === V12.6 v7: 8 故事理论节拍点融入剧本 (剧情推进) ===
        if story_beats_text:
            main += f"\n\n═══════════════════════════════════════════════════════════"
            main += f"\n【剧情推进 · {story_theory} 节拍点 (V12.6 v7 真正融入)】"
            main += f"\n═══════════════════════════════════════════════════════════\n{story_beats_text}\n"

        # === V12.6 v7: 3D 空间坐标系统融入剧本 (空间位置) ===
        if spatial_3d_text:
            main += f"\n\n{spatial_3d_text}\n"

        # === V12.6 v7: 角色 Want/Need/弧光 融入剧本 (对白驱动力) ===
        if char_arcs:
            main += f"\n\n【角色 Want/Need/弧光 (V12.6 v7 写入对白驱动力)】\n"
            for i, arc in enumerate(char_arcs):
                main += f"\n角色 {i+1}: {arc.get('personality', '')}"
                main += f"\n  Want(外在目标): {arc['want']}"
                main += f"\n  Need(内在需求): {arc['need']}"
                main += f"\n  → 对白应该: 外在行为表达 Want, 潜文本/动作暗示 Need, 弧光推动剧情"

        # 附录
        upstream_injected = []
        if vibe_in: upstream_injected.append(("Vibe", vibe_in[:500]))
        if art_in: upstream_injected.append(("Art", art_in[:500]))
        if sound_in: upstream_injected.append(("Sound", sound_in[:500]))
        if chars_in: upstream_injected.append(("Characters", chars_in[:500]))
        if asset_in: upstream_injected.append(("Asset", asset_in[:500]))
        if upstream_injected:
            main += "\n\n" + "─"*40
            main += f"\n【上游 5 维内容 (附录)】\n"
            for tag, content in upstream_injected:
                main += f"\n【{tag}】\n{content}\n"

        # === V16.1: 导演叙事设计块 + AIGC 五段结构 (build层统一追加, 对所有模式生效) ===
        try:
            if narrative_arrangement != "跟随叙事结构":
                from aggregator.feature_film_engine import generate_feature_scenes as _gfs_b
                from aggregator.scene_engine import parse_scene as _ps_b
                _parsed_b = _ps_b(scene)
                _scenes_b = _gfs_b(_parsed_b, director, mood, "", target_minutes, story_theory)
                _ordered_b, _plan_b = arrange_scenes(_scenes_b, narrative_arrangement, narrative_line,
                                                     seed=f"{scene}_{director}_{mode}")
                if _plan_b.get("导演批注"):
                    _sub_b = _plan_b.get("字幕位", [])
                    _sub_txt_b = "; ".join(f"位置{s.get('位置')}: {s.get('字幕')}" for s in _sub_b) if _sub_b else "无"
                    main += (
                        f"\n\n{'─'*40}\n【导演叙事设计 · V16.1】\n"
                        f"叙事编排: {_plan_b.get('方式','跟随叙事结构')}\n"
                        f"叙事线型: {_plan_b.get('叙事结构','单线')}\n"
                        f"时间线图谱: {_plan_b.get('时间线图谱','现在')}\n"
                        f"线索图谱: {_plan_b.get('线索图谱','A')}\n"
                        f"字幕位: {_sub_txt_b}\n"
                        f"导演批注: {_plan_b.get('导演批注','')}"
                    )
        except Exception as _nd_e:
            import sys as _nd_s
            _nd_s.stderr.write(f"[DirectorMaster] 叙事设计块降级: {type(_nd_e).__name__}\n")
        try:
            if target_minutes <= 3:
                from aggregator.scene_engine import parse_scene as _ps_f
                from aggregator.pro_format import build_standard_screenplay_scenes as _bssc_f
                _scenes_f = _bssc_f(scene, director, mood, "", target_minutes, story_theory)
                main += "\n\n" + "─"*40 + "\n" + _build_aigc_five_section(
                    scene, director, mood, core, _scenes_f, dims)
        except Exception as _fs_e:
            import sys as _fs_s
            _fs_s.stderr.write(f"[DirectorMaster] AIGC五段式降级: {type(_fs_e).__name__}\n")

        # === V14.3-MERGED: 复活数据库深度注入 (场景库/大师DNA/故事感/儿童/真实案例) ===
        try:
            main = inject_library_depth(main, mode, director, scene, mood)
        except Exception as _ild_e:
            import sys as _ild_s
            _ild_s.stderr.write(f"[DirectorMaster] 库注入降级: {type(_ild_e).__name__}\n")

        # V13.4 (零虚假红线): 停用预置剧本库参考模板的自动注入。
        # 原因: 库模板为槽位洗牌的编造内容 (随机 token 人名如"孔子春秋/苏伊士风暴"、
        #       编造历史如"1215年卡萨布兰卡"、真实政治历史物件), 且仅按类型匹配(非语义),
        #       会把无关的编造内容注入任意场景 (如唐代武侠注入现代政治文物), 违反零虚假红线。
        # 场景驱动的主剧本 (上方 _build_full_screenplay) 是真实输出, 不依赖该库。
        # 如需恢复, 必须先对库内容做事实一致性清洗 + 语义相关性匹配。

        # AI 强化
        ai_url, ai_key, ai_model = resolve_ai_config(kwargs, core)
        if ai_url:
            upstream_ctx = ""
            if vibe_in: upstream_ctx += f"\n\n【Vibe】\n{vibe_in[:1500]}"
            if art_in: upstream_ctx += f"\n\n【Art】\n{art_in[:1500]}"
            if sound_in: upstream_ctx += f"\n\n【Sound】\n{sound_in[:1500]}"
            if chars_in: upstream_ctx += f"\n\n【Characters】\n{chars_in[:1500]}"
            if asset_in: upstream_ctx += f"\n\n【Asset】\n{asset_in[:1500]}"
            few_shot = """
# Few-shot 世界顶级剧本 (V12.6 v7 全部 6 大专业能力):
场景: 父女厨房雨夜 / 导演: 王家卫 / 8 故事理论: 三幕剧 + 救猫咪15拍

[剧情推进] 8 故事理论节拍点:
  三幕剧: 建置 → 第一情节点 → 第一幕结束 → 上升动作 → 中点 → 第二情节点 → 高潮 → 下降动作 → 解决
  救猫咪15拍: 开场画面(厨房+雨声) → 主题陈述(沉默的爱) → 铺垫(父女日常) → 触发(发现旧信) → 争论(女儿问) → 第二幕开始 → 副线(凤梨罐头) → 乐趣与游戏(切菜) → 中点(罐头被打开) → 反派逼近(沉默对峙) → 失去一切(罐头被放回) → 灵魂的黑夜(雨停) → 第三幕开始 → 高潮(凤梨进父亲碗) → 结尾(父亲低头)

[空间位置] 3D 坐标:
  灶台: X=-0.6 Y=0.0 Z=0.5 (screen-center-left, 前景)
  砧板: X=-0.5 Y=0.0 Z=0.4 (screen-left, 中前景)
  餐桌: X=+0.4 Y=0.0 Z=+0.3 (screen-right, 中景)
  窗: X=0.0 Y=0.0 Z=-0.8 (screen-center, 背景)
  碗柜: X=-0.8 Y=0.0 Z=-0.2 (screen-far-left, 中景)
  → 父亲(砧板处) vs 女儿(餐桌处) 的 screen-left vs screen-right 对峙构图

[氛围渲染] 5 维锚定:
  60-30-10 配色: 蓝绿(雨夜) + 暗红(霓虹) + 琥珀(暖光)
  9D 光影: 逆光+顶光 3200K 暖黄40W
  4 层声音: 雨声中景+收音机粤剧+冰箱嗡鸣+刀切砧板拟音

[镜头情感] 运镜+景别+时长+情感强度:
  镜1: 全景·慢推·5s·情感强度 3/10 (建立)
  镜2: 特写·固定·3s·情感强度 5/10 (父亲的手)
  镜3: 中近景·固定·4s·情感强度 6/10 (女儿抬头)
  镜4: 全景·慢推·8s·情感强度 9/10 (对坐, 高潮前夕)
  镜5: 特写·固定·2s·情感强度 10/10 (凤梨罐头被打开, 顶点)
  镜6: 全景·固定·5s·情感强度 7/10 (收束, 余韵)

[故事线] 600 导演库 12 维档案 + 多线:
  父女双线: A 线(父亲, Want: 不被读懂, Need: 表达爱) vs B 线(女儿, Want: 答案, Need: 接受父亲沉默)
  物件线: 凤梨罐头(15年) → 旧信(泛黄) → 钢笔(没墨水) — 物件承载时间/记忆/父亲沉默

[叙事节奏] 节拍表 + 张力曲线:
  0s: 情感3(建立) → 5s: 情感5(特写) → 12s: 情感6(女儿抬头) → 20s: 情感9(对坐高潮) → 22s: 情感10(凤梨顶点) → 27s: 情感7(收束)

示例输出剧本:
  内.厨房—夜·雨.[视觉锚定: 蓝绿+暗红+琥珀 60-30-10][环境音: 雨声+收音机+冰箱嗡鸣] 父亲[screen-left 砧板处, Want: 不被读懂, Need: 表达爱] 在 [光影: 逆光+顶光 3200K 暖黄] 下切菜, [焦点: 父亲右手食指老茧, 物件: 凤梨罐头(过期15年) 标签起泡]. 女儿[screen-right 餐桌处, Want: 答案, Need: 接受父亲沉默] 坐桌边, 刷手机. [冲突: 凤梨罐头 vs 父亲沉默]. 父亲(不抬头): 吃饭了. 女儿(沉默): 嗯. △ 碗筷, 无对白, 唯呼吸, 张力曲线 9/10.""",
            ctx = {
                "node_type": "剧本",
                "mode": mode,
                "director": director,
                "scene": scene,
                "mood": mood,
                "intent": core.get("_导演意图_观众应感到", ""),
                "conflict": core.get("_核心冲突", ""),
                "theme": core.get("_主题词", ""),
                "visual": core.get("_视觉调性", ""),
                "subtext_strength": core.get("_潜文本强度", ""),
                "promise": core.get("_观众承诺", ""),
                "props": core.get("_关键道具", ""),
                "year": core.get("_时间年代", ""),
                "platform": core.get("_平台媒介", ""),
                "audience": core.get("_目标受众", ""),
                "runtime": core.get("_成片时长", ""),
                "aspect": core.get("_画幅比例", ""),
                "ref_films": core.get("_对标作品", ""),
                "anti_ai": anti_ai,
                "story_theory": story_theory,
                "narrative_arrangement": narrative_arrangement,
                "narrative_line": narrative_line,
                "story_beats": story_beats_text,
                "spatial_3d": spatial_3d_text,
                "char_arcs": char_arcs,
                "upstream_context": upstream_ctx,
                "few_shot_world_class": few_shot,
                "rewrite_instruction": "请作为世界顶级导演的编剧, 基于 8 故事理论节拍点 + 3D 空间坐标 + 角色 Want/Need/弧光 + 上游 5 维 + few-shot 世界顶级范例, 输出完整剧本. 必须包含: 1) 剧情推进 (按所选故事理论的节拍点推进) 2) 空间位置 (用 screen-left/right/center 标注人物位置) 3) 氛围渲染 (5 维锚定融入场景描写) 4) 镜头情感 (运镜+景别+时长+情感强度) 5) 故事线 (600 导演库 12 维 + 角色 Want/Need 推进) 6) 叙事节奏 (节拍表+张力曲线). 输出世界顶级剧本.",
            }
            main = self._ensure_ai_output(main, ctx, ai_url, ai_key, ai_model)

        # V14.3 (红队P2修复): 启用反AI规则 真实生效 (此前仅改 footer 文案)
        main = self._apply_anti_ai(main, kwargs, core)

        main += f"\n\n【版本】v3.0 | 模式: {mode} | 故事理论: {story_theory} | 反AI: {'开' if anti_ai else '关'} | AI润色: {'已' if ai_url else '否'} | 5维融入: {len(upstream_injected)}/5 | 3D空间融入: {'已' if spatial_3d_text else '否'} | Want/Need: {len(char_arcs)}"

        return (main,)