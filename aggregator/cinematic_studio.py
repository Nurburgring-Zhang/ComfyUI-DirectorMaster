# -*- coding: utf-8 -*-
"""
⑥ DirectorMasterCinematic — 画面执行 (5 合 1)
===============================================
电影工作室/30秒6段/表演块/选片决策/漫剧分镜. 输出 10 个 STRING.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)
from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy, parse_multi_select, resolve_dropdown
from aggregator.cinema_craft import build_life_texture, build_edit_decision_list, build_edit_decision_text
from aggregator.script_studio import _parse_vibe_anchors, _parse_art_anchors, _parse_sound_anchors, _parse_char_anchors, _parse_asset_anchors
import re as _re

# V12.6 v8: 画面模式按 长/短/微/竖/短视/动漫/绘本/MV/广告 10 大类拆分
CINE_MODES = [
    # === 电影长片分镜 (90-180min) ===
    "电影工作室",            # 完整长片分镜
    "电影段落分镜",          # 单段落 (15-30min)
    "电影关键场次分镜",      # 单场戏
    "电影三幕分镜",          # 三幕结构分镜
    "电影救猫咪15拍分镜",    # Blake Snyder 15 beats
    # === V12.6 v9: 节奏风格大师 (按大师级镜头语言) ===
    "长镜大师",              # 侯孝贤/是枝裕和/阿巴斯 60-180s 长镜
    "蒙太奇大师",            # 爱森斯坦/普多夫金 0.5-3s 蒙太奇
    "一秒三闪",              # 王家卫/吴宇森 0.3s × 3 情绪爆发
    "抖音超快",              # 抖音爆款 0.5-1s × 10+ 快剪
    "子弹时间",              # 沃卓斯基姐妹 0.5-2s 360° 静止
    "慢镜高光",              # 王家卫/诺兰 1/8 慢放高光
    "极慢抒情",              # 马力克/塔可夫斯基 1/20 极慢
    "定格凝固",              # 北野武/吴宇森 单帧延长
    "延时摄影",              # 宫崎骏/雅克·贝汉 时间压缩
    "POV 主观",              # 德·帕尔玛/索德伯格 角色视角
    "航拍大师",              # 诺兰/《权游》 航拍升降
    "一镜到底",              # 索科洛夫/席佩尔 8-12min 整段
    "游走长镜",              # 拉赞纽斯/贝拉·塔尔 60-180s 跟拍
    "对话长镜",              # 阿巴斯/李安 60-90s 对话
    "车戏分镜",              # 迈克尔·曼 跟拍+速度感
    "枪战分镜",              # 吴宇森 0.5-2s 手持快切
    "演唱会纪录",            # 怀斯曼/马力克 跟拍+航拍+大特写
    "MV 慢镜",               # 大卫·芬奇 1-5s 慢镜+跳切
    "舞蹈编排",              # 法哈蒂/毕赣 多机位切换
    # === 30-60s 标准分镜 ===
    "30秒6段",               # 标准30s
    "60秒12段",              # 60s
    "90秒18段",              # 90s
    "3分钟完整短片",         # 短片分镜
    # === 短剧分镜 (5-30min/集) ===
    "横屏微短剧分镜",        # 5-15min/集
    "竖屏微短剧分镜",        # 3-5min/集
    "女频甜宠竖屏分镜",      # 言情
    "男频逆袭竖屏分镜",      # 战神
    "古风竖屏分镜",          # 古装
    # === 小程序剧分镜 (1min/集) ===
    "竖屏小程序剧分镜",      # 1min/集
    "爽剧小程序分镜",        # 爽点
    "反转小程序分镜",        # 反转
    # === 创意短视频分镜 (30-60s) ===
    "创意玩法分镜",          # 脑洞
    "爆火反转分镜",          # 5秒钩子+反转
    "情感共鸣分镜",          # 温情感人
    "搞笑整蛊分镜",          # 喜剧
    "美食探店分镜",          # 美食
    "Vlog分镜",              # Vlog博主
    # === 动漫分镜 ===
    "番剧动漫分镜",          # 24min/集
    "热血战斗分镜",          # 战斗
    "校园日常分镜",          # 校园
    "奇幻冒险分镜",          # 异世界
    "Q版泡面番分镜",         # 3-5min 短动画
    # === 绘本/儿童分镜 ===
    "绘本故事分镜",          # 5-10min 图文
    "睡前故事分镜",          # 童话
    "儿童教育分镜",          # 早教
    # === MV/广告/宣传片 ===
    "MV音乐短片分镜",        # 3-5min MV
    "广告宣传片分镜",        # 15-60s
    "品牌故事分镜",          # 1-3min
    # === 纪录片 ===
    "人物纪录片分镜",        # 60-90min
    "社会纪录片分镜",        # 60-120min
    # === 互动/沉浸 ===
    "互动剧分支分镜",        # 多分支
    "沉浸式戏剧分镜",        # 360°/VR
    # === 行业垂直 ===
    "婚礼活动分镜",          # 5-10min
    "课程教学分镜",          # 10-30min
    "直播脚本分镜",          # 30-60min
    # === 通用 ===
    "表演块",                 # 表演细节
    "选片决策",               # 选片分镜
    "漫剧分镜",               # 漫画分镜
]

# V14.1: 模式节奏签名 — 修复模式坍缩 (此前 63 模式全落到同一 build_standard_shots, 输出逐字节相同)。
# 每个模式映射一个节奏签名: dur_scale=时长倍率, move=主导运镜, note=节奏说明。
# 长镜类 dur_scale>1 (镜头拉长/镜数减少), 快闪类 dur_scale<1 (镜头缩短/镜数增多), 慢镜类>1 (慢放)。
MODE_PACING = {
    # 长镜大师类 (60-180s 长镜, 镜头拉长)
    "长镜大师":   {"dur_scale": 6.0, "move": "固定长镜", "note": "60-180s 长镜, 侯孝贤/是枝裕和式凝视"},
    "一镜到底":   {"dur_scale": 10.0, "move": "一镜到底跟拍", "note": "8-12min 整段不切, 索科洛夫式"},
    "游走长镜":   {"dur_scale": 6.0, "move": "游走跟拍", "note": "60-180s 游走跟拍, 贝拉·塔尔式"},
    "对话长镜":   {"dur_scale": 5.0, "move": "对话固定长镜", "note": "60-90s 对话长镜, 阿巴斯/李安式"},
    "演唱会纪录": {"dur_scale": 4.0, "move": "跟拍+航拍", "note": "跟拍+航拍+大特写, 怀斯曼式"},
    # 快闪类 (0.3-1s 快切, 镜头缩短)
    "一秒三闪":   {"dur_scale": 0.12, "move": "快切", "note": "0.3s×3 情绪爆发, 王家卫/吴宇森式"},
    "抖音超快":   {"dur_scale": 0.15, "move": "快切", "note": "0.5-1s×10+ 抖音爆款快剪"},
    "枪战分镜":   {"dur_scale": 0.2, "move": "手持快切", "note": "0.5-2s 手持快切, 吴宇森式"},
    "爆火反转分镜": {"dur_scale": 0.2, "move": "快切", "note": "5秒钩子+反转快切"},
    "热血战斗分镜": {"dur_scale": 0.25, "move": "快切+推拉", "note": "战斗快切+速度线"},
    # 慢镜类 (慢放, 时长拉长)
    "慢镜高光":   {"dur_scale": 3.0, "move": "慢镜推近", "note": "1/8 慢放高光, 王家卫/诺兰式"},
    "极慢抒情":   {"dur_scale": 5.0, "move": "极慢推近", "note": "1/20 极慢抒情, 马力克/塔可夫斯基式"},
    "MV 慢镜":    {"dur_scale": 2.5, "move": "慢镜+跳切", "note": "1-5s 慢镜+跳切, 大卫·芬奇式"},
    "子弹时间":   {"dur_scale": 2.0, "move": "360°环绕", "note": "0.5-2s 360° 静止环绕, 沃卓斯基式"},
    "定格凝固":   {"dur_scale": 2.5, "move": "定格", "note": "单帧延长凝固, 北野武式"},
    # 蒙太奇/延时 (时间压缩)
    "蒙太奇大师": {"dur_scale": 0.4, "move": "蒙太奇剪辑", "note": "0.5-3s 蒙太奇, 爱森斯坦式"},
    "延时摄影":   {"dur_scale": 0.5, "move": "延时", "note": "时间压缩延时, 雅克·贝汉式"},
    # 特殊视角
    "POV 主观":   {"dur_scale": 1.0, "move": "POV主观", "note": "角色第一视角, 德·帕尔玛式"},
    "航拍大师":   {"dur_scale": 2.0, "move": "航拍升降", "note": "航拍升降大景, 诺兰式"},
    "车戏分镜":   {"dur_scale": 0.6, "move": "车戏跟拍", "note": "跟拍+速度感, 迈克尔·曼式"},
    "舞蹈编排":   {"dur_scale": 1.2, "move": "多机位切换", "note": "多机位舞蹈编排"},
    # 短剧/小程序 (快节奏钩子)
    "竖屏微短剧分镜": {"dur_scale": 0.4, "move": "快切+推近", "note": "3-5min/集 快切钩子"},
    "女频甜宠竖屏分镜": {"dur_scale": 0.4, "move": "推近特写", "note": "甜宠推近特写钩子"},
    "男频逆袭竖屏分镜": {"dur_scale": 0.35, "move": "快切", "note": "逆袭爽点快切"},
    "古风竖屏分镜": {"dur_scale": 0.5, "move": "古风运镜", "note": "古装竖屏运镜"},
    "竖屏小程序剧分镜": {"dur_scale": 0.3, "move": "快切", "note": "1min/集 极快钩子"},
    "爽剧小程序分镜": {"dur_scale": 0.3, "move": "快切", "note": "爽点密集快切"},
    "反转小程序分镜": {"dur_scale": 0.3, "move": "快切", "note": "反转钩子快切"},
    "横屏微短剧分镜": {"dur_scale": 0.5, "move": "快切", "note": "5-15min/集 横屏快切"},
    # 创意短视频
    "创意玩法分镜": {"dur_scale": 0.5, "move": "脑洞运镜", "note": "脑洞创意运镜"},
    "情感共鸣分镜": {"dur_scale": 0.8, "move": "温情推近", "note": "温情共鸣推近"},
    "搞笑整蛊分镜": {"dur_scale": 0.5, "move": "快切", "note": "喜剧整蛊快切"},
    "美食探店分镜": {"dur_scale": 0.7, "move": "美食特写", "note": "美食特写+推近"},
    "Vlog分镜":   {"dur_scale": 0.8, "move": "手持Vlog", "note": "Vlog 手持第一视角"},
    # 动漫
    "番剧动漫分镜": {"dur_scale": 0.7, "move": "动漫运镜", "note": "24min/集 番剧运镜"},
    "校园日常分镜": {"dur_scale": 0.8, "move": "日常运镜", "note": "校园日常运镜"},
    "奇幻冒险分镜": {"dur_scale": 0.6, "move": "冒险运镜", "note": "异世界冒险运镜"},
    "Q版泡面番分镜": {"dur_scale": 0.5, "move": "Q版快切", "note": "3-5min Q版快切"},
    # 绘本/儿童
    "绘本故事分镜": {"dur_scale": 1.5, "move": "绘本缓推", "note": "5-10min 图文缓推"},
    "睡前故事分镜": {"dur_scale": 1.5, "move": "舒缓运镜", "note": "睡前舒缓运镜"},
    "儿童教育分镜": {"dur_scale": 1.2, "move": "教育运镜", "note": "早教运镜"},
    # MV/广告
    "MV音乐短片分镜": {"dur_scale": 0.8, "move": "MV运镜", "note": "3-5min MV 运镜"},
    "广告宣传片分镜": {"dur_scale": 0.6, "move": "广告运镜", "note": "15-60s 广告运镜"},
    "品牌故事分镜": {"dur_scale": 0.9, "move": "品牌运镜", "note": "1-3min 品牌运镜"},
    # 纪录片
    "人物纪录片分镜": {"dur_scale": 2.0, "move": "纪录跟拍", "note": "60-90min 人物纪录跟拍"},
    "社会纪录片分镜": {"dur_scale": 2.0, "move": "纪录跟拍", "note": "60-120min 社会纪录跟拍"},
    # 互动/沉浸
    "互动剧分支分镜": {"dur_scale": 0.8, "move": "分支运镜", "note": "多分支互动运镜"},
    "沉浸式戏剧分镜": {"dur_scale": 1.2, "move": "360°沉浸", "note": "360°/VR 沉浸运镜"},
    # 行业垂直
    "婚礼活动分镜": {"dur_scale": 1.0, "move": "婚礼运镜", "note": "5-10min 婚礼运镜"},
    "课程教学分镜": {"dur_scale": 1.2, "move": "教学运镜", "note": "10-30min 教学运镜"},
    "直播脚本分镜": {"dur_scale": 0.8, "move": "直播运镜", "note": "30-60min 直播运镜"},
    # 电影结构类 (标准节奏 + 结构标注)
    "电影工作室":   {"dur_scale": 1.0, "move": None, "note": "完整长片分镜, 标准节奏"},
    "电影段落分镜": {"dur_scale": 1.0, "move": None, "note": "单段落 15-30min 分镜"},
    "电影关键场次分镜": {"dur_scale": 1.0, "move": None, "note": "单场戏关键场次分镜"},
    "电影三幕分镜": {"dur_scale": 1.0, "move": None, "note": "三幕结构分镜"},
    "电影救猫咪15拍分镜": {"dur_scale": 1.0, "move": None, "note": "Blake Snyder 15 拍分镜"},
    "30秒6段":   {"dur_scale": 0.5, "move": "标准快切", "note": "30s 标准 6 段"},
    "60秒12段":  {"dur_scale": 0.5, "move": "标准快切", "note": "60s 12 段"},
    "90秒18段":  {"dur_scale": 0.5, "move": "标准快切", "note": "90s 18 段"},
    "3分钟完整短片": {"dur_scale": 0.7, "move": "短片运镜", "note": "3min 完整短片"},
    # 通用
    "表演块":    {"dur_scale": 1.0, "move": None, "note": "表演细节块"},
    "选片决策":  {"dur_scale": 1.0, "move": None, "note": "选片决策分镜"},
    "漫剧分镜":  {"dur_scale": 0.8, "move": "漫剧分格", "note": "漫画分格分镜"},
}

# V14.2: 节奏大师模式 → PACING_STYLES 映射 — 修复模式坍缩的深度修复。
# 让模式真正驱动 pacing_engine 的完整镜头序列 (镜数/时长/焦段/角度/转场/焦点模板/声音模板),
# 而非仅乘时长标量。仅 19 个节奏大师模式有对应 PACING_STYLES; 其余模式用 auto。
MODE_TO_PACING = {
    "长镜大师": "固定长镜",
    "蒙太奇大师": "蒙太奇",
    "一秒三闪": "一秒三闪",
    "抖音超快": "抖音超快",
    "子弹时间": "子弹时间",
    "慢镜高光": "慢镜高光",
    "极慢抒情": "极慢抒情",
    "定格凝固": "定格",
    "延时摄影": "延时摄影",
    "POV 主观": "POV 主观",
    "航拍大师": "航拍",
    "一镜到底": "一镜到底",
    "游走长镜": "游走长镜",
    "对话长镜": "对话长镜",
    "车戏分镜": "车戏分镜",
    "枪战分镜": "枪战分镜",
    "演唱会纪录": "演唱会纪录",
    "MV 慢镜": "MV 慢镜",
    "舞蹈编排": "舞蹈编排",
}

# V14.2: 「节奏风格」下拉 → PACING_STYLES 键 (修复装饰性输入: 此前声明"强制全场戏用某节奏"但零消费)。
# 与 MODE_TO_PACING 值域一致, 仅 2 个下拉名需转键 (定格凝固→定格, 航拍大师→航拍)。
RHYTHM_TO_PACING = {
    "一秒三闪": "一秒三闪", "抖音超快": "抖音超快", "子弹时间": "子弹时间", "蒙太奇": "蒙太奇",
    "定格凝固": "定格", "延时摄影": "延时摄影", "POV 主观": "POV 主观", "航拍大师": "航拍",
    "固定长镜": "固定长镜", "对话长镜": "对话长镜", "游走长镜": "游走长镜", "一镜到底": "一镜到底",
    "慢镜高光": "慢镜高光", "极慢抒情": "极慢抒情",
    "车戏分镜": "车戏分镜", "枪战分镜": "枪战分镜", "演唱会纪录": "演唱会纪录",
    "MV 慢镜": "MV 慢镜", "舞蹈编排": "舞蹈编排",
}

# V14.2: 结构类电影分镜模式 → 故事理论 — 让结构模式驱动节拍引擎 (story_theory 已下场到节拍生成),
#        修复 电影三幕/救猫咪15拍 等结构模式与其它模式同构。
CINE_MODE_THEORY = {
    "电影三幕分镜": "三幕剧",
    "电影救猫咪15拍分镜": "救猫咪15拍",
    "电影工作室": "三幕剧",
    "电影段落分镜": "三幕剧",
    "电影关键场次分镜": "三幕剧",
}

# V12.6 v7: 导演情感曲线 (每镜情感强度 0-10, 世界顶级导演分镜必备)
EMOTION_CURVE_TEMPLATES = {
    "三幕剧": {
        "建置": 3, "第一情节点": 5, "上升动作": 6, "中点": 7,
        "第二情节点": 8, "高潮": 10, "下降动作": 6, "解决": 4,
    },
    "救猫咪15拍": {
        "开场画面": 3, "主题陈述": 4, "铺垫": 4, "触发": 5,
        "争论": 5, "第二幕开始": 6, "副线": 5, "乐趣与游戏": 5,
        "中点": 7, "反派逼近": 8, "失去一切": 9, "灵魂的黑夜": 9,
        "第三幕开始": 8, "高潮": 10, "结尾": 4,
    },
    "英雄之旅": {
        "平凡世界": 2, "冒险召唤": 4, "拒绝召唤": 5, "导师出现": 4,
        "跨越门槛": 5, "试炼盟友与敌人": 6, "深渊逼近": 7,
        "最大考验": 9, "获得宝物": 8, "归途": 6, "复活": 7, "携宝归来": 5,
    },
}

# V12.6 v7: 多线叙事 / POV 切换 / 非线性时间线
NARRATIVE_STRUCTURE_MODES = {
    "单线": "默认单线叙事 (V12.6 v6 行为)",
    "双线并行": "A线 + B线 平行, 中间交汇, 结尾合并 (例: 父亲线 + 女儿线)",
    "POV切换": "同一事件从多个角色 POV 视角切换 (例: 先父亲看, 再女儿看)",
    "非线性": "时间线打乱, 倒叙/插叙/闪前 (例: 雨夜场景中插入旧日回忆)",
}


def _build_emotion_curve(shot_idx, total_shots, story_theory="三幕剧", director="王家卫", narrative_meta=None):
    """V12.6 v10: 5 种顶级导演型情感曲线, 按 director 选, 不再硬编码 PROGRESSION.
    5 种曲线模板 (从真实电影总结):
      1. 王家卫 (wong_kar_wai) — 不规则起伏, 留白多, 7-9 高位震荡, 中段常下沉
      2. 诺兰 (nolan) — 层层递进, 中点后急剧上升, 结尾双高潮 (10+10+8)
      3. 希区柯克 (hitchcock) — 持续紧张, 每 10% 一个 mini-climax (8-9-7-9-8-10)
      4. 塔可夫斯基 (tarkovsky) — 极慢, 几乎不变 (3-4-4-5-4-5-4-3), 靠空镜
      5. 三幕剧经典 (classic) — act1 低, act2 升, act3 顶峰+收束
    曲线特征:
      - 不再是 PROGRESSION 数组的线性插值 (那是 AI 感的根源)
      - 而是按 director 取**真实电影的张力曲线** + 加入**非线性震荡** (心跳骤停/沉默爆发/重复)
      - 每镜强度 = 0-10 浮点 + 节奏描述 (rising/hold/drop/spike/breath)
    """
    if total_shots <= 0:
        return [5.0]

    # 选 director 曲线模板
    director_key = _normalize_director(director)
    PROGRESSION = DIRECTOR_CURVES.get(director_key, DIRECTOR_CURVES["classic"])

    # 阶段化曲线 (按镜位比例 + PROGRESSION 模板 + 微扰)
    result = []
    for i in range(total_shots):
        pos = i / max(total_shots - 1, 1)  # 0-1
        # 在 PROGRESSION 中找最近的两个点非线性插值 (用 ease-in-out, 不是线性)
        lower = PROGRESSION[0]
        upper = PROGRESSION[-1]
        for j in range(len(PROGRESSION) - 1):
            a_pos, a_val = PROGRESSION[j]
            b_pos, b_val = PROGRESSION[j + 1]
            if a_pos <= pos <= b_pos:
                lower = (a_pos, a_val)
                upper = (b_pos, b_val)
                break
        if upper[0] == lower[0]:
            val = lower[1]
        else:
            t = (pos - lower[0]) / (upper[0] - lower[0])
            # 非线性插值: ease-in-out (t = t*t*(3-2t))
            t_eased = t * t * (3 - 2 * t)
            val = round(lower[1] + t_eased * (upper[1] - lower[1]), 1)
        # 非线性微扰: 每镜有微小起伏 (0.3-0.5), 模拟"心跳"
        # 用 hash 确定性微扰 (同输入同输出, 不同镜位不同)
        perturb = (((i * 7 + 3) % 11) - 5) / 20.0  # -0.25 ~ +0.25
        val = max(0.0, min(10.0, val + perturb))
        result.append(val)

    return result


def _normalize_director(director):
    """归一化导演名到 5 种曲线模板 key."""
    if not director:
        return "classic"
    d = director.lower()
    # 王家卫
    if any(k in director for k in ["王家卫", "Wong Kar-wai", "wong", "kar-wai"]):
        return "wong_kar_wai"
    # 诺兰
    if any(k in director for k in ["诺兰", "Nolan", "nolan", "Christopher"]):
        return "nolan"
    # 希区柯克
    if any(k in director for k in ["希区柯克", "Hitchcock", "hitchcock", "Alfred"]):
        return "hitchcock"
    # 塔可夫斯基
    if any(k in director for k in ["塔可夫斯基", "Tarkovsky", "tarkovsky", "Andrei"]):
        return "tarkovsky"
    # 三幕剧经典
    if any(k in director for k in ["斯皮尔伯格", "Spielberg", "spielberg"]):
        return "classic"
    return "classic"


# V12.6 v10: 5 种顶级导演型情感曲线 (从真实电影张力曲线总结, 28-32 个点)
DIRECTOR_CURVES = {
    # 王家卫: 不规则起伏, 留白多, 7-9 高位震荡, 中段常下沉, 结尾不收束
    "wong_kar_wai": [
        (0.00, 2.0), (0.04, 3.5), (0.08, 2.0), (0.12, 4.0), (0.16, 3.0),  # 开场: 1-2-3-2-4-3, 不规则
        (0.20, 5.0), (0.24, 3.0), (0.28, 6.0), (0.32, 4.0), (0.36, 5.5),  # 铺垫: 起伏大
        (0.40, 4.0), (0.44, 7.0), (0.48, 5.0), (0.52, 8.0), (0.56, 6.0),  # 中点: 高位震荡
        (0.60, 7.5), (0.64, 5.0), (0.68, 8.5), (0.72, 6.0), (0.76, 9.0),  # 第二幕 B: 持续高位
        (0.80, 7.0), (0.84, 9.5), (0.88, 8.0), (0.92, 9.0), (0.96, 7.0),  # 高潮: 9.5 极致但不留 10
        (1.00, 8.0), (1.04, 5.0), (1.08, 6.0), (1.12, 4.0), (1.16, 5.0),  # 收束: 不归 3, 留 5
        (1.20, 3.0),
    ],
    # 诺兰: 层层递进, 中点后急剧上升, 结尾双高潮
    "nolan": [
        (0.00, 2.0), (0.05, 2.5), (0.10, 3.0), (0.15, 3.5), (0.20, 4.0),  # 开场: 平稳上升
        (0.25, 5.0), (0.30, 5.5), (0.35, 6.0), (0.40, 6.5), (0.45, 7.0),  # 第一幕结束: 7.0
        (0.50, 8.0), (0.55, 8.5), (0.60, 9.0), (0.65, 9.5), (0.70, 9.0),  # 中点: 8.0→9.5
        (0.75, 9.5), (0.80, 10.0), (0.85, 9.0), (0.90, 9.5), (0.95, 10.0),  # 第二情节点: 10.0
        (1.00, 10.0), (1.05, 9.0), (1.10, 10.0), (1.15, 7.0), (1.20, 5.0),  # 双高潮: 10+10, 然后 5 收
    ],
    # 希区柯克: 持续紧张, 每 10% 一个 mini-climax
    "hitchcock": [
        (0.00, 4.0), (0.05, 5.0), (0.10, 8.0), (0.15, 6.0), (0.20, 7.0),  # 开场 5-8-6-7
        (0.25, 8.5), (0.30, 7.0), (0.35, 9.0), (0.40, 7.5), (0.45, 8.0),  # 第一情节点: 8.5
        (0.50, 9.0), (0.55, 7.5), (0.60, 9.0), (0.65, 8.0), (0.70, 9.0),  # 中点: 9
        (0.75, 8.5), (0.80, 9.5), (0.85, 8.0), (0.90, 9.0), (0.95, 9.5),  # 持续高位
        (1.00, 10.0), (1.05, 8.5), (1.10, 9.0), (1.15, 7.0), (1.20, 5.0),  # 高潮 10, 收 5
    ],
    # 塔可夫斯基: 极慢, 几乎不变, 靠空镜
    "tarkovsky": [
        (0.00, 3.0), (0.10, 3.5), (0.20, 3.0), (0.30, 4.0), (0.40, 3.5),  # 几乎不动 3-4
        (0.50, 4.0), (0.55, 4.5), (0.60, 4.0), (0.65, 5.0), (0.70, 4.5),  # 中点轻微 4-5
        (0.75, 5.0), (0.80, 5.5), (0.85, 5.0), (0.90, 5.5), (0.95, 5.0),  # 持续 5
        (1.00, 5.5), (1.05, 5.0), (1.10, 4.5), (1.15, 4.0), (1.20, 3.0),  # 收 3
    ],
    # 三幕剧经典
    "classic": [
        (0.00, 3.0), (0.05, 3.0), (0.10, 4.0), (0.15, 4.0), (0.20, 5.0),
        (0.25, 6.0), (0.30, 6.0), (0.35, 6.0), (0.40, 6.0), (0.45, 7.0),
        (0.50, 8.0), (0.55, 8.0), (0.60, 7.0), (0.65, 7.0), (0.70, 7.0),
        (0.75, 8.0), (0.80, 8.0), (0.85, 9.0), (0.88, 9.0), (0.90, 8.0),
        (0.92, 9.0), (0.95, 9.0), (0.97, 10.0), (1.00, 10.0), (1.02, 8.0),
        (1.05, 7.0), (1.10, 5.0), (1.15, 4.0), (1.20, 3.0),
    ],
}


def _build_narrative_structure(narrative_mode, total_shots, scenes=None, chars=None, obj=None):
    """V12.6 v10 + V13.3: 按场次类型自动切 POV/line/timeline — POV 用场景真实角色 (不再硬编码父女凤梨).
    chars: [主角, 副线, ...] 从场景解析; obj: 关键物件.
    """
    chars = chars or ["主角", "副线"]
    cA = chars[0] if len(chars) > 0 else "主角"
    cB = chars[1] if len(chars) > 1 else (chars[0] if chars else "副线")
    obj = obj or "关键道具"
    if not scenes:
        scenes = [{"act": 1, "scene_index": i + 1, "story_function": "推进", "dialogue_density": "mid"} for i in range(35)]

    # 先算每场戏的 POV/line/timeline (用场戏信息决定)
    scene_meta = []
    for sc in scenes:
        act = sc.get("act", 1)
        sidx = sc.get("scene_index", 1)
        story_func = sc.get("story_function", "推进")
        density = sc.get("dialogue_density", "mid")
        # POV 决定:
        if narrative_mode == "POV切换":
            # 同事件多 POV, 按场次切
            if "副线" in story_func or "B" in story_func or "B线" in story_func or "B 故事" in story_func:
                pov = f"{cB} POV"
            elif "主角" in story_func or "对决" in story_func or "失" in story_func or "灵魂" in story_func:
                pov = f"{cA} POV"
            elif "物件" in story_func:
                pov = f"物件 POV ({obj})"
            elif sidx % 3 == 0:
                pov = f"{cA} POV"
            elif sidx % 3 == 1:
                pov = f"{cB} POV"
            else:
                pov = f"物件 POV ({obj})"
        elif narrative_mode == "双线并行":
            if "副线" in story_func or "B" in story_func or "B 故事" in story_func or "深化" in story_func:
                pov = f"{cB} POV (B线)"
            else:
                pov = f"{cA} POV (A线)"
        elif narrative_mode == "非线性":
            # 非线性: 时间线打乱
            if sidx == 1:
                pov = f"{cA} POV (过去)"
            elif sidx == 5:
                pov = f"{cB} POV (回忆)"
            elif sidx == 18:  # 中点
                pov = f"物件 POV ({obj})"
            elif sidx == 23:  # 灵魂黑夜
                pov = f"{cA} POV (内心独白)"
            else:
                pov = "全知" if sidx % 2 == 0 else f"{cA} POV"
        else:
            # 单线 (默认): 按密度切
            if density == "low" or "铺垫" in story_func or "副线" in story_func:
                pov = "全知 (俯瞰)"  # 空镜多
            elif sidx % 4 == 0:
                pov = f"{cB} POV"
            elif sidx % 4 == 1:
                pov = f"{cA} POV"
            else:
                pov = "全知 (俯瞰)"

        # line 决定:
        if narrative_mode == "双线并行":
            if "副线" in story_func or "B" in story_func or "B线" in story_func or "B 故事" in story_func or "深化" in story_func:
                line = f"B ({cB})"
            else:
                line = f"A ({cA})"
        else:
            line = "A"

        # timeline 决定:
        # V13.4: "现在"时间线按场景 weather/time 场景驱动 (不再硬编码雨夜/雪夜)
        def _now_timeline(sc):
            if sc.get("weather") == "雪":
                return "现在 (雪夜)"
            if sc.get("weather") == "雨":
                return "现在 (雨夜)"
            if sc.get("time") == "黄昏":
                return "现在 (黄昏)"
            if sc.get("time") == "深夜":
                return "现在 (深夜)"
            if sc.get("weather"):
                return f"现在 ({sc.get('weather')})"
            return "现在"
        if narrative_mode == "非线性":
            if sidx == 1:
                timeline = "闪回 (过去)"
            elif sidx == 5:
                timeline = "闪前 (未来)"
            elif sidx == 18:
                timeline = "现在"
            elif sidx == 23:
                timeline = "闪回 (关键日)"
            elif sidx == 31:  # 高潮
                timeline = _now_timeline(sc) + ", 时间冻结"
            elif sidx == 35:  # 尾声
                timeline = _now_timeline(sc) + ", 时间重启"
            else:
                timeline = _now_timeline(sc)
        else:
            # 默认: 跟着场戏的 time 字段
            timeline = _now_timeline(sc)

        scene_meta.append({"pov": pov, "line": line, "timeline": timeline})

    # 把场次 meta 展开到每镜 (按每场戏的 shots_target 分配)
    # 重要: 不能让 927 镜都用同一 meta, 要在场次间切换 POV
    result = []
    shot_idx = 0
    for i, sc_meta in enumerate(scene_meta):
        if shot_idx >= total_shots:
            break
        sc = scenes[i] if i < len(scenes) else scenes[-1]
        # 场戏的镜头数 (从 generate_feature_shots 推: 至少 1 镜)
        n_shots = max(1, sc.get("shots_target", 8))
        # 同一场戏的每镜可能进一步切 POV (例如 父 POV 切到女儿 POV)
        for j in range(n_shots):
            if shot_idx >= total_shots:
                break
            # 在同一场戏内, 偶尔切 POV (增加丰富度)
            if j > 0 and j % 4 == 0 and narrative_mode in ("POV切换", "双线并行"):
                # 切到另一种 POV
                if sc_meta["pov"] == "父亲 POV":
                    pov_j = "女儿 POV"
                elif sc_meta["pov"] == "女儿 POV":
                    pov_j = "父亲 POV"
                else:
                    pov_j = sc_meta["pov"]
            else:
                pov_j = sc_meta["pov"]
            result.append({
                "line": sc_meta["line"],
                "pov": pov_j,
                "timeline": sc_meta["timeline"],
            })
            shot_idx += 1

    # 如果 result 比 total_shots 短, 用最后一个填
    while len(result) < total_shots:
        result.append(result[-1] if result else {"line": "A", "pov": "全知", "timeline": "现在"})

    return result[:total_shots]


def _integrate_6d_into_shot_fields(shot, shot_idx, total_shots, vibe_a, art_a, sound_a, char_a, asset_a, scene_dur):
    """V12.6 关键: 把 6 维 anchors 真正融入每镜分镜字段 (镜号/景别/运镜/焦段/时长/焦点/声音/色彩/光影/材质/氛围/情绪/转场/叙事目的/首帧描述 15+ 列)."""
    # 计算每镜分配到的 5 维 anchors (按镜号循环)
    # 镜 1/4: 强调色彩/光影 (Art 锚定)
    # 镜 2/5: 强调声音 (Sound 锚定)
    # 镜 3/6: 强调角色/动作 (Characters 锚定)
    # 所有镜: 都融入物件 (Asset 锚定)
    phase = shot_idx % 3
    enhancements = {}
    if phase == 0 or shot_idx == 0:
        # Art 视觉锚定镜
        if art_a.get("主色"): enhancements["stage_color"] = art_a["主色"][:24]
        if art_a.get("光影方向"): enhancements["stage_light"] = art_a["光影方向"][:18]
        if art_a.get("材质"): enhancements["stage_material"] = art_a["材质"][:18]
    elif phase == 1:
        # Sound 声音锚定镜
        if sound_a.get("环境"):
            enhancements["sound"] = " / ".join(sound_a["环境"][:2])[:18]
        if sound_a.get("拟音"):
            new_sound = " / ".join(sound_a["拟音"][:2])
            if enhancements.get("sound"):
                enhancements["sound"] = (enhancements["sound"] + "+" + new_sound)[:18]
            else:
                enhancements["sound"] = new_sound[:18]
    else:
        # Characters 角色锚定镜
        for ch in char_a.get("角色", []):
            if ch.get("外貌") or ch.get("动作"):
                enhancements["focus"] = f"[{ch.get('名', '角色')}] {ch.get('外貌', '')}"[:30]
                enhancements["stage_emotion"] = ch.get("性格", "")[:14]
                break
    # 所有镜: 物件锚定
    if asset_a.get("道具"):
        old_focus = shot.get("focus", "")
        new_focus = (old_focus + "|" + asset_a["道具"])[:30] if old_focus else asset_a["道具"][:30]
        enhancements["focus"] = new_focus
    if asset_a.get("环境"):
        enhancements["stage_atmosphere"] = asset_a["环境"][:18]
    # Vibe 主题锚定 → 写到 purpose
    if vibe_a.get("主题"):
        old_p = shot.get("purpose", "")
        new_p = f"主题:{vibe_a['主题']}" + (f"|{old_p}" if old_p else "")
        enhancements["purpose"] = new_p[:50]
    elif vibe_a.get("对标"):
        old_p = shot.get("purpose", "")
        new_p = f"对标:{vibe_a['对标'][:20]}" + (f"|{old_p}" if old_p else "")
        enhancements["purpose"] = new_p[:50]
    # Vibe 片名锚定 → 注入首帧描述
    if vibe_a.get("片名"):
        enhancements["首帧描述"] = f"{vibe_a['片名'][0]}-{shot.get('focus', '')[:30]}"[:50]
    # 合并回 shot
    for k, v in enhancements.items():
        if not v: continue
        if k in shot and shot[k]:
            shot[k] = f"{shot[k]}|{v}"[:len(v) + 8] if len(str(v)) < 10 else v
        else:
            shot[k] = v
    return shot


def _parse_script_shot_drivers(script_text):
    """从 Script 输出提取每镜驱动力: 哪个对白/动作/物件在哪个镜号.
    返回 {1: '父亲切菜的手', 2: '女儿抬头', ...} 字典."""
    drivers = {}
    if not script_text: return drivers
    # 简化: 按段落切分, 每个段落(空行分隔)对应一个镜号
    blocks = [b.strip() for b in script_text.split("△") if b.strip()]
    for i, b in enumerate(blocks[:6], 1):  # 限制 6 镜
        # 提取首句作为该镜驱动力
        first_lines = b.split("\n", 5)[:3]
        driver = " ".join(first_lines)[:80]
        if driver:
            drivers[i] = driver
    return drivers

# V14.2 (零虚假 + 零死代码): 移除 TEMPLATES 及 5 个硬编码模板 builder
#   (电影工作室/30秒6段/表演块/选片决策/漫剧分镜)。它们从未被 build() 消费 —
#   全部 63 模式统一走场景驱动的 build_standard_shots 真实引擎; 且模板含硬编码
#   凤梨罐头/厨房/杜可风 内容, 违反零虚假红线。


class DirectorMasterCinematic(DirectorNodeBase):
    """画面执行聚合节点 — 5 合 1."""
    NODE_TYPE = "画面"

    @classmethod
    def INPUT_TYPES(cls):
        _ND = "无(默认)"
        _R = "🎲 随机"
        return {"required": {
            "画面模式": (CINE_MODES+[_R], {"default": "电影工作室",
                "tooltip": "63 模式: 电影工作室/节奏大师/短剧/动漫/绘本/MV/广告/纪录片分镜. Cinematic 是'导演语言翻译' — 把剧本/场景翻译为带景别/运镜/焦段/光影/材质的分镜表, 不是重新生成; 🎲 随机"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "从核心数据包继承, 此处可单独覆盖"}),
            "景别偏好": ([_ND,_R,"大远景","远景","全景","中全景","中景","中近景","近景","特写","大特写",
                          "插入镜头","反应镜头","过肩镜头","POV主观","空镜","荷兰角",
                          "双人近景","群戏全景","鸟瞰","虫视角"], {"default": _ND,
                "tooltip": "镜头景别偏好 (20+ 选项)"}),
            "运镜风格": ([_ND,_R,"固定","推镜头","拉镜头","横移","摇镜头","升降","环绕","跟拍",
                          "手持","斯坦尼康","航拍","穿越机FPV","长镜头","快速切镜",
                          "伸缩炮","吊臂","轨道车","zoom变焦","Dolly推拉","Pan摇移",
                          "Tilt俯仰","Roll滚转","荷兰角倾斜","Crane吊臂","Jib摇臂","Steadicam","Gimbal稳定器"],
                         {"default": _ND,
                "tooltip": "运镜风格 (28+ 选项)"}),
            "焦段偏好": ([_ND,_R,"超广角8-14mm","广角14-24mm","标准35-50mm","中焦50-85mm",
                          "长焦85-135mm","望远135-200mm","超望远200-400mm+",
                          "鱼眼8mm","微距100mm","移轴","变形宽银幕","Hawk V-Lite 1.3x",
                          "Cooke S4i","Master Anamorphic","Lomo","Bokeh切焦"],
                         {"default": _ND,
                "tooltip": "焦段偏好 (17+ 选项)"}),
            "构图法则": ([_ND,_R,"三分法","黄金分割","中心","中心对称","对角线","S形","引导线",
                          "框中框","负空间","前景遮挡","T形/十字","放射性","螺旋形",
                          "三角形","圆形","井字形","V形","菱形"], {"default": _ND,
                "tooltip": "构图法则 (20+ 选项)"}),
            "剪辑节奏": ([_ND,_R,"极慢(单镜超长)","慢(长镜为主)","中","快(频繁切镜)","极快(MV式)",
                          "变速(快慢交替)","动静交替","留白剪辑","跳切","匹配剪辑",
                          "隐剪","L型剪辑","J型剪辑","动作顺剪"], {"default": _ND,
                "tooltip": "剪辑节奏 (16+ 选项)"}),

        }, "optional": {
            "运镜风格_多选": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ V13.2 多选: 多种运镜按镜头顺序轮换/演变, 用 逗号/箭头 分隔。例: '固定→手持→航拍' 或 '推镜头, 环绕, 跟拍'。优先于上方单选运镜风格"}),
            "核心数据包": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Core.核心数据包 — 继承场景/导演/情绪/灵魂/AI (32 字段)"}),
            "剧本输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "★ 必接 Script.剧本 — Cinematic 把剧本'翻译'为分镜表 (景别/运镜/焦段/光影/材质), 没剧本就只能空镜或基于场景描述生成"}),
            "创意输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Vibe.创意 — 注入概念/主题/对标到分镜"}),
            "美术输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Art.美术 — 注入色调/光影/材质到分镜"}),
            "声音输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Sound.声音 — 注入声轨到分镜"}),
            "角色输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Characters.角色圣经 — 角色锚定到分镜"}),
            "资产输入": ("STRING", {"default": "", "multiline": True, "forceInput": True,
                "tooltip": "接 Asset.资产设定 — 道具/环境到分镜"}),
            "目标时长(分钟)": ("FLOAT", {"default": 120, "min": 0.05, "max": 240, "step": 0.05,
                "tooltip": "★ 目标成片时长(分钟). V16.0: 支持秒级 (0.25=15秒, 0.5=30秒, 1=60秒, 5=5分钟, 90=90分钟). 短视频用小数, 长片用整数. 总时长恒覆盖片长."}),
            "节奏风格": ([_ND, _R,
                # === 快闪类 (0.3-1s) ===
                "一秒三闪", "抖音超快", "子弹时间", "蒙太奇", "定格凝固", "延时摄影", "POV 主观", "航拍大师",
                # === 长镜类 (60-180s) ===
                "固定长镜", "对话长镜", "游走长镜", "一镜到底",
                # === 慢镜类 ===
                "慢镜高光", "极慢抒情",
                # === 类型专属 ===
                "车戏分镜", "枪战分镜", "演唱会纪录", "MV 慢镜", "舞蹈编排",
            ], {"default": _ND,
                "tooltip": "★ V12.6 v9 新增: 强制全场戏用某节奏 (默认 ND 走 auto 自动选). 一秒三闪=0.3s×3 嗨爆; 固定/对话/游走长镜=60-180s 不切; 慢镜高光=1/8 慢放; 蒙太奇=0.5-3s×N; 抖音=0.5-1s×10+"}),
            "直觉风险": ([_ND, _R, "safe", "medium", "bold", "chaotic"], {"default": _ND,
                "tooltip": "V15.0 直觉引擎: 确定性反常规镜头语法 (高潮静止/亲密远景/喧闹后静默/孤独不对称/物件代反应/对白后留白, 均有真实作者电影依据). ND=不启用; 🎲 随机"}),
            "AIGC生产模式": (["自动判别", "文生视频", "首帧生视频", "首尾帧生视频", "多参考图生视频", "参考视频生视频"],
                {"default": "自动判别",
                "tooltip": "V16.0 需求4: AIGC 视频生产适配. 自动判别=按首尾帧/参考图/参考视频输入自动判定; 或手动指定. 分镜JSON按模式适配输出"}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("分镜", "分镜JSON")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/画面"

    def build(self, **kwargs):
        from aggregator.pro_format import format_shot_table, build_standard_shots, strip_decor
        import json as _json
        mode = kwargs.get("画面模式","电影工作室")
        # V16.0 需求1: 模式选择器支持 🎲 随机
        if mode == "🎲 随机":
            import random as _r
            mode = _r.choice(CINE_MODES)
        if mode not in CINE_MODES: mode = "电影工作室"
        core = parse_core_pack(kwargs.get("核心数据包",""))
        scene = core.get("_场景描述") or kwargs.get("场景描述","")
        director = core.get("_导演风格") or kwargs.get("导演风格","王家卫")
        mood = core.get("_情绪基调","孤独")

        # V12.6 v9: 目标时长 (决定 ~280/~210/~145/~70/~35 镜体量)
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

        # V12.6 v7: 故事理论 + 叙事结构 (从 Script 节点的输出自动获取, 或用默认值)
        story_theory = kwargs.get("故事理论", "三幕剧")  # 由 Script 节点输出传入
        narrative_mode = kwargs.get("叙事结构", "单线")  # 单线/双线并行/POV切换/非线性
        # V14.2: 结构类电影分镜模式 → 故事理论 (修复结构模式同构; story_theory 已下场到节拍生成)
        if mode in CINE_MODE_THEORY:
            story_theory = CINE_MODE_THEORY[mode]

        # 上游 6 路 forceInput
        script_in = kwargs.get("剧本输入","")
        vibe_in = kwargs.get("创意输入","")
        art_in = kwargs.get("美术输入","")
        sound_in = kwargs.get("声音输入","")
        chars_in = kwargs.get("角色输入","")
        asset_in = kwargs.get("资产输入","")

        # 解析 6 维 anchors
        vibe_a = _parse_vibe_anchors(vibe_in)
        art_a = _parse_art_anchors(art_in)
        sound_a = _parse_sound_anchors(sound_in)
        char_a = _parse_char_anchors(chars_in)
        asset_a = _parse_asset_anchors(asset_in)
        script_drivers = _parse_script_shot_drivers(script_in)

        # V14.2: 模式驱动 pacing_engine — 节奏大师模式映射到 PACING_STYLES, 驱动完整镜头序列
        # (镜数/时长/焦段/角度/转场/焦点模板/声音模板), 修复模式坍缩的深度修复
        pacing_mode = MODE_TO_PACING.get(mode, "auto")
        # V14.2: 「节奏风格」下拉真实生效 (此前声明未消费) — 显式选择时覆盖模式推导的 pacing,
        #        兑现 tooltip "强制全场戏用某节奏"。ND/随机 时保持模式推导。
        rhythm_style = resolve_dropdown(kwargs.get("节奏风格"), None)
        if rhythm_style and rhythm_style in RHYTHM_TO_PACING:
            pacing_mode = RHYTHM_TO_PACING[rhythm_style]

        # V14.2: 镜头密度 — 非 pacing 模式用 MODE_PACING.dur_scale 驱动镜头密度 (消费此前死参数 dur_scale)。
        #        pacing 模式 (MODE_TO_PACING) 已由 pacing_engine 决定镜数, 不再叠加密度。
        density_scale = 1.0
        if pacing_mode == "auto":
            _mp = MODE_PACING.get(mode)
            if _mp and _mp.get("dur_scale"):
                density_scale = float(_mp["dur_scale"])

        # V12.6 v9: 真分镜表 (按 target_minutes 决定 280/210/145/70/35 镜体量)
        shots = build_standard_shots(scene, director, mood, target_minutes=target_minutes,
                                     story_theory=story_theory, pacing_mode=pacing_mode,
                                     density_scale=density_scale, mode_seed=mode)
        # V15.0: 直觉引擎 — 确定性反常规镜头语法 (风险档位, 真实作者电影依据); V16.0 需求1: 支持 🎲 随机
        _intuition_risk = kwargs.get("直觉风险", "无(默认)")
        if _intuition_risk == "🎲 随机":
            import random as _r
            _intuition_risk = _r.choice(["safe", "medium", "bold", "chaotic"])
        if _intuition_risk and _intuition_risk != "无(默认)":
            from aggregator.intuition_engine import apply_intuition
            shots, _intuition_log = apply_intuition(shots, mood=mood, scene=scene,
                                                    risk_level=_intuition_risk,
                                                    seed=f"{mode}|{scene}|{mood}")
        # 6 维 anchors 真正整合到每镜字段
        for i, s in enumerate(shots):
            s = _integrate_6d_into_shot_fields(s, i, len(shots), vibe_a, art_a, sound_a, char_a, asset_a, 30)
            if script_drivers.get(i + 1):
                s["purpose"] = f"{s.get('purpose', '')} | 剧本驱动: {script_drivers[i+1][:60]}"

        # === V13.2: 偏好下拉真实生效 + 运镜多选演变 (此前 5 个偏好仅声明未使用) ===
        size_pref = resolve_dropdown(kwargs.get("景别偏好"), None)
        move_pref = resolve_dropdown(kwargs.get("运镜风格"), None)
        focal_pref = resolve_dropdown(kwargs.get("焦段偏好"), None)
        comp_pref = resolve_dropdown(kwargs.get("构图法则"), None)
        rhythm_pref = resolve_dropdown(kwargs.get("剪辑节奏"), None)
        # 运镜多选优先于单选; 单值 = 全场统一, 多值 = 按镜头顺序轮换演变
        move_arc = parse_multi_select(kwargs.get("运镜风格_多选", ""))
        if not move_arc and move_pref:
            move_arc = [move_pref]
        # 剪辑节奏 → 时长倍率 (影响每镜 dur)
        _dur_scale = 1.0
        if rhythm_pref:
            if "极慢" in rhythm_pref: _dur_scale = 2.5
            elif rhythm_pref.startswith("慢"): _dur_scale = 1.8
            elif "极快" in rhythm_pref: _dur_scale = 0.3
            elif rhythm_pref.startswith("快"): _dur_scale = 0.5
            elif "变速" in rhythm_pref or "动静交替" in rhythm_pref: _dur_scale = -1  # 交替
        n_shots = len(shots)
        for i, s in enumerate(shots):
            if size_pref:
                s["size"] = size_pref
            if move_arc:
                # V13.3 混合语义: 弧值作为主导运镜, 但每 3 镜保留 1 镜原生运镜以保多样性
                # (V13.2 旧逻辑覆写全部镜头 → 运镜种数=弧值个数, 摧毁多样性)
                if len(move_arc) == 1:
                    if i % 3 != 2:
                        s["move"] = move_arc[0]
                else:
                    prog = i / max(n_shots - 1, 1)
                    idx = int(prog * (len(move_arc) - 1) + 0.5)
                    if i % 3 != 2:
                        s["move"] = move_arc[max(0, min(len(move_arc) - 1, idx))]
            if focal_pref:
                s["focal"] = focal_pref
            if comp_pref:
                s["note"] = f"{s.get('note','')} | 构图: {comp_pref}".strip(" |")
            if _dur_scale != 1.0:
                try:
                    dur_val = float(str(s.get("dur", "3")).rstrip("s"))
                except Exception:
                    dur_val = 3.0
                if _dur_scale == -1:  # 变速: 奇偶交替快慢
                    scale = 2.0 if i % 2 == 0 else 0.4
                else:
                    scale = _dur_scale
                s["dur"] = f"{round(dur_val * scale, 1)}s"
        # === V13.2 end ===

        # === V14.1/V14.2: 模式节奏签名生效 — 修复模式坍缩 ===
        # V14.2: 节奏大师模式已由 pacing_mode 驱动 pacing_engine (镜数/时长/焦段/转场/运镜),
        #        无需再覆写 move。仅非 pacing 模式用 MODE_PACING 的主导运镜区分。
        _pacing = MODE_PACING.get(mode)
        mode_note = ""
        if _pacing:
            _mmove = _pacing.get("move")
            mode_note = _pacing.get("note", "")
            # 仅非 pacing 模式覆写主导运镜 (pacing 模式已由引擎设置每镜运镜)
            if _mmove and pacing_mode == "auto":
                for i, s in enumerate(shots):
                    if i % 3 != 2:
                        s["move"] = _mmove
        # === V14.2 end ===

        # === V12.6 v10: 5 种导演型情感曲线 (按 director 自动选) + 多 POV 叙事结构 ===
        emotion_curve = _build_emotion_curve(0, len(shots), story_theory, director=director)
        # V12.6 v10: 从 shots 提取 scenes (按 scene 字段分组), 让 _build_narrative_structure 按场次类型自动切 POV
        scenes_from_shots = []
        if shots:
            cur_scene = None
            for s in shots:
                if s.get("scene") != cur_scene:
                    scenes_from_shots.append({
                        "act": s.get("act", 1),
                        "scene_index": s.get("scene", 1),
                        "story_function": s.get("story_function", "推进"),
                        "dialogue_density": s.get("dialogue_density", "mid"),
                        "weather": s.get("weather", ""),
                        "time": s.get("time", ""),
                    })
                    cur_scene = s.get("scene")
        scenes_for_narrative = scenes_from_shots if scenes_from_shots else None
        # V13.3: 解析场景角色/物件, 让 POV 用真实角色 (不再硬编码父女凤梨)
        try:
            from aggregator.scene_engine import parse_scene as _ps
            _parsed = _ps(scene) if scene else {}
        except Exception:
            _parsed = {}
        _chars = _parsed.get("characters") or ["主角", "副线"]
        _objs = _parsed.get("objects") or ["关键道具"]
        narrative_meta = _build_narrative_structure(narrative_mode, len(shots), scenes=scenes_for_narrative,
                                                    chars=_chars, obj=_objs[0] if _objs else "关键道具")

        for i, s in enumerate(shots):
            # 情感强度写入 note (V14.3 E1: 保留1位小数, 消除浮点伪影)
            intensity = emotion_curve[i] if i < len(emotion_curve) else 5
            try:
                intensity = round(float(intensity), 1)
                intensity = int(intensity) if float(intensity).is_integer() else intensity
            except Exception:
                intensity = 5
            old_note = s.get("note", "")
            new_note = f"情感强度: {intensity}/10" + (f" | {old_note}" if old_note else "")
            s["note"] = new_note
            s["emotion_intensity"] = intensity
            # 多线/POV 写入 purpose
            if i < len(narrative_meta):
                meta = narrative_meta[i]
                old_p = s.get("purpose", "")
                line_pov = f"线:{meta['line']} POV:{meta['pov']} 时间:{meta['timeline']}"
                s["purpose"] = f"{old_p} | {line_pov}" if old_p else line_pov

        main = format_shot_table(director, mood, shots)

        # 视觉参数 — V13.3 场景/年代驱动 (不再固定蓝绿雨夜)
        try:
            from aggregator.feature_film_engine import _detect_era as _de
            _era_v = _de(scene or "")
        except Exception:
            _era_v = "现代"
        _visual = core.get("_视觉调性", "写实") if core else "写实"
        _palette = {
            "古装": "60% 大地色(土黄/赭石) / 30% 青灰(天光) / 10% 朱红(点缀)",
            "科幻": "60% 冷灰蓝(舱体) / 30% 深空黑 / 10% 指示灯光(琥珀/青)",
            "复古": "60% 低饱和暖褐 / 30% 灰绿 / 10% 褪色的艳色",
            "现代": "60% 中性灰 / 30% 环境主色 / 10% 点缀色",
        }.get(_era_v, "60% 中性灰 / 30% 环境主色 / 10% 点缀色")
        _light = {
            "古装": "天光/烛火 | 自然光为主 | 中低对比",
            "科幻": "舱内冷光+舷外深空 | 低照度 | 高对比",
            "复古": " practical 光源(灯/窗) | 软光 | 中对比",
            "现代": "环境光+实用光源 | 软硬结合 | 中对比",
        }.get(_era_v, "环境光+实用光源 | 软硬结合 | 中对比")
        main += (
            f"\n\n【视觉语言】焦段 50mm/35mm/85mm | 比例按核心数据包 | 视觉调性 {_visual}\n"
            f"【色彩 60-30-10 · {_era_v}】{_palette}\n"
            f"【光影】{_light}\n"
            f"【推荐视频模型】MiniMax H3 / Seedance 2.5 / Wan 3.0 / 可灵 / LTX-2.5"
        )
        main += self._director_block(director)
        from aggregator.dimensions import apply_dimensions
        main += "\n\n" + apply_dimensions("分镜", kwargs)
        main += "\n\n" + build_life_texture(scene, mood, director)
        main += "\n\n" + build_edit_decision_text(scene, director, mood)

        # === V12.6 v7: 导演情感曲线展示 (V14.3 E1: 1位小数) ===
        main += f"\n\n【导演情感曲线 (V12.6 v10 镜头情感) — 故事理论: {story_theory} — 导演: {director}】"
        for i, intensity in enumerate(emotion_curve):
            bar = "█" * int(round(intensity)) + "░" * (10 - int(round(intensity)))
            _iv = round(float(intensity), 1)
            _iv = int(_iv) if float(_iv).is_integer() else _iv
            main += f"\n  镜{i+1}: {bar} {_iv}/10"
        main += f"\n  曲线: 5 种导演型 (王家卫/诺兰/希区柯克/塔可夫斯基/三幕剧), 非线性 + 心跳微扰"

        # === V12.6 v7: 多线叙事 / POV 切换 展示 ===
        main += f"\n\n【叙事结构 (V12.6 v7 故事线) — 模式: {narrative_mode}】"
        for i, meta in enumerate(narrative_meta):
            main += f"\n  镜{i+1}: 线={meta['line']} POV={meta['pov']} 时间={meta['timeline']}"

        # 附录
        upstream_injected = []
        if script_in: upstream_injected.append(("Script", script_in[:500]))
        if vibe_in: upstream_injected.append(("Vibe", vibe_in[:400]))
        if art_in: upstream_injected.append(("Art", art_in[:400]))
        if sound_in: upstream_injected.append(("Sound", sound_in[:400]))
        if chars_in: upstream_injected.append(("Characters", chars_in[:400]))
        if asset_in: upstream_injected.append(("Asset", asset_in[:400]))
        if upstream_injected:
            main += "\n\n" + "─"*40
            main += f"\n【上游 6 维内容 (附录)】\n"
            for tag, content in upstream_injected:
                main += f"\n【{tag}】\n{content}\n"

        # AI 强化
        ai_url, ai_key, ai_model = resolve_ai_config(kwargs, core)
        if ai_url:
            upstream_ctx = ""
            if script_in: upstream_ctx += f"\n\n【Script】\n{script_in[:2000]}"
            if vibe_in: upstream_ctx += f"\n\n【Vibe】\n{vibe_in[:1500]}"
            if art_in: upstream_ctx += f"\n\n【Art】\n{art_in[:1500]}"
            if sound_in: upstream_ctx += f"\n\n【Sound】\n{sound_in[:1500]}"
            if chars_in: upstream_ctx += f"\n\n【Characters】\n{chars_in[:1500]}"
            if asset_in: upstream_ctx += f"\n\n【Asset】\n{asset_in[:1500]}"
            ctx = {
                "node_type": "分镜",
                "mode": mode, "director": director, "scene": scene, "mood": mood,
                "intent": core.get("_导演意图_观众应感到", ""),
                "conflict": core.get("_核心冲突", ""), "theme": core.get("_主题词", ""),
                "visual": core.get("_视觉调性", ""),
                "subtext_strength": core.get("_潜文本强度", ""),
                "props": core.get("_关键道具", ""),
                "year": core.get("_时间年代", ""), "platform": core.get("_平台媒介", ""),
                "audience": core.get("_目标受众", ""), "runtime": core.get("_成片时长", ""),
                "aspect": core.get("_画幅比例", ""), "ref_films": core.get("_对标作品", ""),
                "story_theory": story_theory, "narrative_mode": narrative_mode,
                "emotion_curve": emotion_curve, "narrative_meta": narrative_meta,
                "upstream_context": upstream_ctx,
                "rewrite_instruction": f"请作为世界顶级导演的分镜师, 基于 6 路上游 + 故事理论 {story_theory} + 叙事模式 {narrative_mode} + 情感曲线 + 多线/POV, 整体润色分镜. 要求: 1) 镜头情感 (运镜+景别+时长+情感强度按曲线推进) 2) 故事线 (多线/POV/非线性按叙事模式标注) 3) 剧情推进 (按 {story_theory} 节拍点) 4) 空间位置 (screen-left/right/center 标注人物位置) 5) 氛围渲染 (5 维锚定融入) 6) 叙事节奏 (节拍+张力+情感曲线).",
            }
            main = self._ensure_ai_output(main, ctx, ai_url, ai_key, ai_model)

        # === 分镜 JSON (V12.6 v7 加 情感强度 + 线/POV/时间) ===
        shots_json = []
        for i, s in enumerate(shots):
            meta = narrative_meta[i] if i < len(narrative_meta) else {"line":"A","pov":"全知","timeline":"现在"}
            intensity = s.get("emotion_intensity", emotion_curve[i] if i < len(emotion_curve) else 5)
            shots_json.append({
                "镜号": s.get("n"), "阶段": s.get("stage"), "类型阶段": s.get("stage_name"),
                "景别": s.get("size"), "角度": s.get("angle"), "运镜": s.get("move"),
                "焦段": s.get("focal"), "时长": s.get("dur"), "画面焦点": s.get("focus"),
                "声音": s.get("sound"), "转场": s.get("cut"), "叙事目的": s.get("purpose"),
                "色彩": s.get("stage_color", ""), "光影": s.get("stage_light", ""),
                "材质": s.get("stage_material", ""), "氛围": s.get("stage_atmosphere", ""),
                "情绪": s.get("stage_emotion", ""),
                "首帧描述": s.get("首帧描述", s.get("stage_name", "")),
                # V12.6 v7 新增 (V14.3 E1: 1位小数)
                "情感强度": intensity,  # 0-10
                "线": meta["line"], "POV": meta["pov"], "时间线": meta["timeline"],
            })
        # V14.3 E1: 浮点统一 1 位小数 (总时长/情感曲线)
        _total_dur = round(sum(float(str(s.get("时长", 0)).replace("s", "") or 0) for s in shots_json), 1)
        _curve_clean = []
        for _cv in emotion_curve:
            try:
                _cvr = round(float(_cv), 1)
                _curve_clean.append(int(_cvr) if float(_cvr).is_integer() else _cvr)
            except Exception:
                _curve_clean.append(_cv)

        # V16.0 需求4: AIGC 视频生产适配 — 判别生产模式 + 每镜适配
        try:
            from aggregator.aigc_adapter import detect_production_mode, build_aigc_block, adapt_shot_for_mode, MODE_T2V
            _aigc_mode_in = kwargs.get("AIGC生产模式", "自动判别")
            if _aigc_mode_in and _aigc_mode_in != "自动判别":
                _prod_mode = _aigc_mode_in
                _prod_basis = "手动指定"
            else:
                # Cinematic 无首尾帧/参考图/参考视频输入 → 自动判别为文生视频
                _prod_mode, _prod_basis = detect_production_mode(
                    has_first=False, has_last=False, has_ref_images=False, has_ref_video=False)
            # 每镜 AIGC 适配提示词
            for _sj in shots_json:
                _sj["AIGC适配提示词"] = adapt_shot_for_mode(_sj, _prod_mode)
        except Exception as _aigc_e:
            import sys as _aigc_s
            _aigc_s.stderr.write(f"[DirectorMaster] AIGC适配降级: {type(_aigc_e).__name__}\n")
            _prod_mode, _prod_basis = "文生视频", "降级"

        json_str = _json.dumps({
            "分镜数": len(shots_json),
            "总时长秒": _total_dur,
            "导演": director, "情绪": mood, "画面模式": mode,
            "故事理论": story_theory, "叙事结构": narrative_mode,
            "AIGC生产模式": _prod_mode,
            "AIGC判别依据": _prod_basis,
            "情感曲线": _curve_clean,
            "叙事元数据": narrative_meta,
            "分镜表": shots_json,
            "上游应用统计": {
                "剧本": "已应用" if script_in else "未连接",
                "Vibe": "已应用" if vibe_in else "未连接",
                "Art": "已应用" if art_in else "未连接",
                "Sound": "已应用" if sound_in else "未连接",
                "Characters": "已应用" if chars_in else "未连接",
                "Asset": "已应用" if asset_in else "未连接",
            },
        }, ensure_ascii=False, indent=2)

        # V16.0 需求4: AIGC 生产适配块 (注入分镜文本输出)
        try:
            main += "\n\n" + build_aigc_block(_prod_mode, shots_json, scene=scene, director=director)
        except Exception:
            pass

        # V14.2: 启用反AI规则 真实生效 (此前硬编码"开"且未消费); 节点开关优先于核心包
        _anti_ai_flag = kwargs.get("启用反AI规则", None)
        if _anti_ai_flag is None:
            _anti_ai_flag = core.get("_启用反AI规则", True) if core else True
        main += f"\n\n【版本】v3.0 | 模式: {mode} | 节奏签名: {mode_note or '标准'} | 镜头数: {len(shots)} | 故事理论: {story_theory} | 叙事: {narrative_mode} | 反AI: {'开' if _anti_ai_flag else '关'} | AI润色: {'已' if ai_url else '否'} | 6维融入: {sum(1 for x in [vibe_in, art_in, sound_in, chars_in, asset_in, script_in] if x)}/6 | 情感曲线: {len(emotion_curve)} 镜 | 多线: {narrative_mode}"

        # V14-FINAL (零虚假红线): 停用预置分镜库参考模板的自动注入 (与剧本库一致)。
        # 原因: 分镜库模板为槽位填空的编造内容, 会按类型粗匹配把无关分镜注入任意场景, 违反零虚假红线。
        # 场景驱动的主分镜表 (上方 build_standard_shots) 是真实输出, 不依赖该库。

        # V14.3-MERGED: 大师级影视语言原则 (format_templates 复活接线)
        try:
            from format_templates import MASTER_VIDEO_PRINCIPLES
            if MASTER_VIDEO_PRINCIPLES:
                main = "【大师级影视语言原则】\n" + str(MASTER_VIDEO_PRINCIPLES) + "\n\n" + main
        except Exception as _mp_e:
            import sys as _mp_s
            _mp_s.stderr.write(f"[DirectorMaster] 大师原则注入降级: {type(_mp_e).__name__}\n")

        main = self._apply_anti_ai(main, kwargs, core)
        return (main, json_str)