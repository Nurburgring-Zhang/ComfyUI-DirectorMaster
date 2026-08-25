# -*- coding: utf-8 -*-
"""
V12.6 v12: 长片特征生成器 (Feature Film Engine) — 真正按输入自动生成节拍
========================================================================
V12.6 v9-v11 问题: 虽然按 target_minutes 动态算 num_scenes, 但故事节拍
(act, scene_index) -> story_function 仍是硬编码的 3 套 act1/2/3 固定数组
(开场画面/主题陈述/触发事件/灵魂的黑夜/第二情节点...).

V12.6 v12 修复: 全部节拍由 generate_story_beats(num_scenes, target_minutes, type, mood, director, scene_parsed, intent) 按输入实时计算:
1. 按 type 选 type-specific beat generator (救猫咪15拍 / 英雄之旅12阶段 / 麦基 / 三幕剧 / 惊悚 / 爱情 / 喜剧 / 黑暗 / 纪录 9 种)
2. 按 director 覆盖 (王家卫: 留白多/不规则 / 诺兰: 持续上升 / 希区柯克: 持续高张力 / 塔可夫斯基: 持续低张力极慢 / 三幕剧 / 默认)
3. 按 mood 调整 tension 范围 (史诗/悲剧/喜剧/悬疑/惊悚/爱情/家庭/动作/记录)
4. 按 scene_desc 匹配具体事件 (从 EVENT_SKELETON 100+ 项事件骨架)

时长光谱 (5s-180min 全覆盖, 13 个时长点已 100% 通过):
- < 30s: 1 场 (抖音/广告)
- 30s-1min: 2 场 (短剧 1 集)
- 1-3min: 3 场 (微短剧)
- 3-15min: 5-9 场 (微短剧/短剧)
- 15-30min: 9-13 场 (网剧 1 集)
- 30-60min: 13-18 场 (长广告/短片)
- 60-90min: 18-25 场 (90min 电影)
- 90-120min: 25-35 场 (120min 长片)
- 120-150min: 35-37 场 (150min 史诗)
- 150-180min: 40-45 场 (180min 鸿篇)

每镜 0.3-30s, 平均 10s/镜 (7 类镜头池: establishing/character/detail/transition/reaction/lyric/micro).
"""
import hashlib as _hashlib
import random as _random


def _arc_value_at(arc, progress):
    """V13.2: 按叙事进度(0..1)从演变弧取当前值 (自包含, 无外部依赖)."""
    if not arc:
        return ""
    if len(arc) == 1:
        return arc[0]
    try:
        p = max(0.0, min(1.0, float(progress)))
    except Exception:
        p = 0.0
    idx = int(p * (len(arc) - 1) + 0.5)
    return arc[max(0, min(len(arc) - 1, idx))]

# ============================================================
# 35 场戏节拍表 — 好莱坞救猫咪15拍 + 序列剧25场融合
# 格式: (act, scene_index) -> (story_function, dialogue_density, tension_level, duration_min, shots_target)
# ============================================================
# V12.6 v12: 故事节拍系统 (真正按输入自动生成, 不再硬编码)
# ============================================================
# 设计: 按 type (genre) 选 beat 模板函数, 按 director 覆盖节拍节奏,
#       按 mood 调整 tension, 按 scene_desc 匹配具体事件, 按 duration 决定 beat 数量.
# 关键: 没有任何固定 (act, scene_index) -> story_function 的表.
#       story_function 是按输入实时计算的.

# --- Type 派生的 beat 生成器 (6+ 种 type, 各自有不同的节拍逻辑) ---

def _beats_save_the_cat(n):
    """救猫咪15拍: 经典商业片 15 节拍 (Blake Snyder).
    适合: 商业长片 (史诗/动作/惊悚/家庭).
    """
    beats_15 = [
        (1, "开场画面 (钩子)", 2, "low", 5),       # 1. Opening Image
        (1, "主题陈述", 3, "mid", 6),              # 2. Theme Stated
        (1, "铺垫 (世界)", 3, "mid", 7),           # 3. Setup
        (1, "铺垫 (冲突种子)", 4, "mid", 7),        # 4. Catalyst
        (1, "争论/决定", 6, "high", 9),            # 5. Debate
        (1, "第一情节点 (进入第二幕)", 7, "high", 10),  # 6. Break Into Two
        (2, "第二幕开始 · 新世界", 5, "mid", 8),     # 7. B Story
        (2, "乐趣与游戏", 5, "mid", 8),             # 8. Fun and Games
        (2, "中点 · 虚假胜利 (A+B 交叉)", 6, "mid", 9),  # 9. Midpoint
        (2, "敌人逼近", 7, "high", 10),             # 10. Bad Guys Close In
        (2, "失去一切", 8, "high", 10),             # 11. All Is Lost
        (2, "灵魂的黑夜", 9, "low", 9),             # 12. Dark Night of the Soul
        (2, "决定/承诺 (重生)", 7, "mid", 9),       # 13. Break Into Three
        (3, "终局 · 高潮", 10, "high", 11),         # 14. Finale
        (3, "结尾画面 (对称开场)", 4, "low", 6),    # 15. Final Image
    ]
    return _expand_beats_to_n(beats_15, n, "save_the_cat")


def _beats_hero_journey(n):
    """英雄之旅12阶段 (Joseph Campbell).
    适合: 史诗/冒险/奇幻.
    """
    beats_12 = [
        (1, "平凡世界", 2, "low", 5),
        (1, "冒险召唤", 4, "mid", 6),
        (1, "拒绝召唤", 4, "mid", 6),
        (1, "导师出现", 4, "mid", 6),
        (1, "跨越门槛 (进入新世界)", 7, "high", 10),
        (2, "试炼 · 盟友与敌人", 5, "mid", 8),
        (2, "深渊逼近 · 中点", 8, "high", 11),
        (2, "最大考验 · 失去一切", 9, "high", 10),
        (2, "获得宝物 · 灵魂黑夜", 9, "low", 9),
        (2, "归途 · 决定", 7, "mid", 9),
        (3, "复活 · 高潮", 10, "high", 11),
        (3, "携宝归来 · 尾声", 3, "low", 5),
    ]
    return _expand_beats_to_n(beats_12, n, "hero_journey")


def _beats_mckee_story_value(n):
    """麦基故事价值 (Robert McKee) — 欲望/需求/价值递进.
    适合: 人物驱动剧情片/艺术片.
    """
    # 麦基 5 拍 (欲望/需求/价值正转/反转) 重复
    return _expand_beats_to_n([
        (1, "建立欲望 (Want)", 3, "mid", 6),
        (1, "建立需求 (Need)", 4, "mid", 7),
        (1, "价值正转 (第一次)", 5, "mid", 8),
        (2, "价值反转 (第一次)", 7, "high", 10),
        (2, "价值正转 (第二次)", 6, "mid", 8),
        (2, "价值反转 (第二次)", 8, "high", 10),
        (2, "中点 · 价值深度反转", 9, "high", 11),
        (2, "价值正转 (最终)", 7, "mid", 9),
        (3, "价值反转 (最终)", 8, "high", 10),
        (3, "高潮 · 价值决断", 10, "high", 11),
        (3, "解决 · 价值定位", 5, "low", 7),
        (3, "尾声 · 价值回声", 3, "low", 5),
    ], n, "mckee")


def _beats_drama_three_act(n):
    """经典三幕剧 (Aristotle) — 起承转合.
    适合: 通用剧情/家庭剧/爱情.
    """
    return _expand_beats_to_n([
        (1, "起 (建立)", 2, "low", 5),
        (1, "承 (铺垫)", 4, "mid", 7),
        (1, "承 (关系)", 4, "mid", 7),
        (1, "转 (触发)", 6, "high", 9),
        (1, "转 (决定)", 7, "high", 10),
        (2, "中点 (真假胜负)", 8, "high", 11),
        (2, "承 (上升)", 6, "mid", 8),
        (2, "承 (压力)", 7, "high", 10),
        (2, "转 (失去一切)", 8, "high", 10),
        (2, "转 (黑夜)", 9, "low", 9),
        (2, "合 (决定)", 7, "mid", 9),
        (3, "合 (高潮)", 10, "high", 11),
        (3, "合 (解决)", 5, "low", 7),
        (3, "合 (尾声)", 3, "low", 5),
    ], n, "drama")


def _beats_three_act_variant(n):
    """三幕剧(变体) — 慢热人物弧 (V14.3 E4: 与经典版实质相异, 非换标签).
    差异: 第一幕 35% (日常沉浸+延迟触发), 中点≈55% (虚假平衡), 黑夜≈78%, 高潮≈85% (提前爆发), 余波收束更短。
    适合: 人物驱动/作者电影/生活流 (是枝裕和/李安家庭剧/海边的曼彻斯特式)。
    """
    return _expand_beats_to_n([
        (1, "起 (日常沉浸)", 2, "low", 5),
        (1, "起 (细节积累)", 3, "low", 6),
        (1, "承 (暗流)", 4, "mid", 7),
        (1, "承 (裂痕显现)", 5, "mid", 8),
        (1, "转 (延迟触发)", 6, "high", 9),
        (2, "承 (迟疑回应)", 5, "mid", 8),
        (2, "中点 (虚假平衡)", 7, "high", 10),
        (2, "承 (代价积累)", 6, "mid", 9),
        (2, "转 (破裂点)", 8, "high", 10),
        (2, "转 (灵魂黑夜)", 9, "low", 9),
        (3, "合 (抉择时刻)", 8, "high", 10),
        (3, "合 (高潮·提前爆发)", 10, "high", 11),
        (3, "合 (余波)", 4, "low", 6),
    ], n, "drama",
        ratios=(0.35, 0.45, 0.20),
        positions={"climax": 0.85, "dark": 0.78, "mid": 0.55},
        preserve_act=True)


def _beats_thriller_suspense(n):
    """惊悚/悬疑 — 持续紧张 + 每 10% 一个 mini-climax.
    适合: 悬疑/惊悚/犯罪/政治.
    """
    return _expand_beats_to_n([
        (1, "建立 (日常有裂缝)", 3, "mid", 6),
        (1, "异兆 (1st hint)", 4, "mid", 7),
        (1, "触发事件 (谜团)", 6, "high", 9),
        (1, "决定调查", 7, "high", 10),
        (2, "调查 (错位)", 5, "mid", 8),
        (2, "新线索 (2nd hint)", 6, "mid", 9),
        (2, "中点 (嫌疑人/反转)", 8, "high", 11),
        (2, "深入危险", 7, "high", 10),
        (2, "真相 (3rd hint)", 8, "high", 10),
        (2, "危机 (威胁)", 8, "high", 10),
        (2, "失去一切 (信任崩塌)", 9, "high", 10),
        (2, "黑夜 (孤立无援)", 9, "low", 9),
        (3, "决定/反击", 7, "mid", 9),
        (3, "高潮 · 对决", 10, "high", 11),
        (3, "真相揭示", 6, "low", 7),
        (3, "解决 · 新平衡", 4, "low", 6),
    ], n, "thriller")


def _beats_love_romance(n):
    """爱情 5 拍 (相遇/靠近/阻碍/告白/相守).
    适合: 爱情/浪漫/家庭/青春.
    """
    return _expand_beats_to_n([
        (1, "相遇 (钩子)", 3, "low", 5),
        (1, "主题陈述 · 命运的暗示", 3, "mid", 6),
        (1, "铺垫 · 日常", 3, "mid", 7),
        (1, "铺垫 · 关系建立", 4, "mid", 7),
        (1, "触发 · 心动瞬间", 6, "high", 9),
        (1, "第一情节点 · 关系确立", 7, "high", 10),
        (2, "靠近 · 甜蜜", 5, "mid", 8),
        (2, "靠近 · 试探", 5, "mid", 8),
        (2, "阻碍出现 · 外部压力", 6, "high", 9),
        (2, "中点 · 误会/分开", 8, "high", 11),
        (2, "压力加剧 · 彼此的挣扎", 7, "high", 10),
        (2, "失去一切 · 绝望", 8, "high", 10),
        (2, "黑夜 · 孤独的觉醒", 9, "low", 9),
        (2, "决定 · 行动", 7, "mid", 9),
        (3, "高潮 · 告白/重逢", 10, "high", 11),
        (3, "解决 · 和解", 5, "low", 7),
        (3, "尾声 · 相守", 3, "low", 5),
    ], n, "love")


def _beats_comedy_misunderstanding(n):
    """喜剧 — 误会递进 + 升温 + 揭秘.
    适合: 喜剧/轻松剧/家庭.
    """
    return _expand_beats_to_n([
        (1, "建立 · 角色 (有怪癖)", 3, "mid", 6),
        (1, "铺垫 · 日常", 3, "mid", 7),
        (1, "触发 · 第一个误会", 5, "mid", 8),
        (1, "升温 · 误会升级", 6, "high", 9),
        (2, "新角色介入 · 复杂性", 5, "mid", 8),
        (2, "中点 · 大误会 (错位喜剧)", 7, "high", 10),
        (2, "升温 · 危机边缘", 7, "high", 10),
        (2, "黑暗 · 角色困境", 6, "mid", 8),
        (2, "决定 · 角色行动", 6, "mid", 8),
        (3, "高潮 · 揭秘 (真相大白)", 9, "high", 11),
        (3, "解决 · 角色成长", 5, "low", 7),
        (3, "尾声 · 收束温暖", 3, "low", 5),
    ], n, "comedy")


def _beats_dark_psychological(n):
    """黑暗/心理 — 麦基 + 持续上升.
    适合: 心理/犯罪/黑色电影.
    """
    return _expand_beats_to_n([
        (1, "建立 · 主角的'正常'", 3, "low", 5),
        (1, "裂缝 · 第一个异常", 4, "mid", 7),
        (1, "触发 · 真相的一角", 5, "mid", 8),
        (1, "决定 · 主角选择面对", 6, "high", 9),
        (2, "中点 · 真相的揭示", 8, "high", 11),
        (2, "上升 · 主角的挣扎", 7, "high", 10),
        (2, "高潮 · 主角的转变/崩溃", 9, "high", 10),
        (2, "失去一切 · 真相的代价", 9, "high", 10),
        (2, "黑夜 · 主角独自面对", 9, "low", 9),
        (3, "高潮 · 终极对决 (内/外)", 10, "high", 11),
        (3, "解决 · 主角的'新正常'", 6, "low", 7),
        (3, "尾声 · 留白", 4, "low", 5),
    ], n, "dark")


def _beats_doc_chronicle(n):
    """纪录片式 (怀斯曼式) — 观察/事件/留白.
    适合: 纪录片/伪纪录片/沉浸剧.
    """
    return _expand_beats_to_n([
        (1, "建立 · 日常", 2, "low", 5),
        (1, "铺垫 · 主题", 3, "mid", 6),
        (1, "事件 · 第一个变化", 4, "mid", 7),
        (2, "深入 · 多视角", 5, "mid", 8),
        (2, "中点 · 关键事件", 7, "high", 10),
        (2, "延伸 · 后果", 6, "mid", 8),
        (2, "观察 · 留白", 6, "low", 7),
        (2, "回声 · 主题深化", 7, "mid", 9),
        (3, "高潮 · 收束", 8, "high", 10),
        (3, "尾声 · 主题升华", 4, "low", 6),
    ], n, "documentary")


# ============================================================
# V14.2: 叙事理论节拍生成器 (修复 Script 模式坍缩)
# 此前 story_theory 只被追加成附录文本, 节拍一律落到 type 默认生成器。
# 现在每种叙事理论有自己的节拍骨架, 由 _expand_ordered 按场次展开。
# ============================================================

def _beats_five_act(n):
    """五幕剧 (莎士比亚/弗莱塔格 5 幕) — 呈示/上升/危机/下坡/高潮+结局.
    与三幕剧的真实差异: 危机(不可逆点)居中, 高潮前多一段"下坡"(坏人逼近/代价), 结局独立成幕.
    """
    beats = [
        (1, "第一幕 · 呈示 (日常与裂缝)", 3, "mid", 7),
        (1, "第一幕 · 触发事件", 5, "high", 9),
        (2, "第二幕 · 上升 (第一次行动)", 6, "mid", 8),
        (2, "第二幕 · 上升 (障碍叠加)", 7, "high", 10),
        (3, "第三幕 · 危机 (不可逆点)", 8, "high", 11),
        (3, "第三幕 · 中点反转", 8, "high", 10),
        (4, "第四幕 · 下坡 (坏人逼近)", 8, "high", 10),
        (4, "第四幕 · 黑夜 (失去一切)", 9, "low", 9),
        (5, "第五幕 · 高潮 (终局对决)", 10, "high", 11),
        (5, "第五幕 · 结局 (新秩序)", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_kishotenketsu(n):
    """起承转合 (东亚古典四段) — 起引入/承铺展/转突转/合收束.
    与西方结构的真实差异: 无对抗式危机, "转"是全片峰值, "合"是余韵而非胜利.
    """
    beats = [
        (1, "起 (引入 · 建立情境)", 3, "low", 6),
        (1, "起 (引入 · 人物登场)", 3, "mid", 6),
        (2, "承 (铺展 · 展开)", 5, "mid", 8),
        (2, "承 (铺展 · 深化积累)", 6, "mid", 8),
        (3, "转 (转折 · 突变)", 9, "high", 11),
        (3, "转 (转折 · 碰撞与余波)", 8, "high", 10),
        (4, "合 (收束 · 汇聚)", 6, "mid", 8),
        (4, "合 (收束 · 余韵)", 3, "low", 5),
    ]
    return _expand_ordered(beats, n)


def _beats_four_act(n):
    """四幕剧 (剧集/流媒体 4 幕标准) — 建置/对抗/建设/解决, 每幕 25%."""
    beats = [
        (1, "第一幕 · 建置 (日常与裂缝)", 3, "mid", 7),
        (1, "第一幕 · 触发事件", 5, "high", 9),
        (1, "第一幕 · 争论 (去还是不去)", 6, "high", 9),
        (2, "第二幕 · 对抗 (第一次行动)", 6, "mid", 8),
        (2, "第二幕 · 障碍叠加", 7, "high", 10),
        (2, "第二幕 · 中点反转", 8, "high", 11),
        (3, "第三幕 · 建设 (反击计划)", 7, "mid", 9),
        (3, "第三幕 · 坏人逼近", 8, "high", 10),
        (3, "第三幕 · 黑夜 (失去一切)", 9, "low", 9),
        (4, "第四幕 · 解决 (终局对决)", 10, "high", 11),
        (4, "第四幕 · 代价 (胜利的代价)", 6, "mid", 8),
        (4, "第四幕 · 新平衡", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_seven_point(n):
    """七点结构 (Dan Wells 7-Point) — Hook/转折1/压力1/中点/压力2/转折2/解决.
    特点: 开场与结局互为镜像 (Hook 是解决的反面).
    """
    beats = [
        (1, "钩子 Hook (起点状态 · 与结局互为镜像)", 3, "mid", 6),
        (1, "情节转折1 (被推上旅程)", 6, "high", 9),
        (2, "压力点1 (反派亮相 · 第一次施压)", 6, "high", 9),
        (2, "中点 (从反应转为行动)", 8, "high", 11),
        (2, "压力点2 (更大压力 · 导师倒下)", 8, "high", 10),
        (2, "情节转折2 (最后一块拼图)", 7, "mid", 9),
        (3, "解决 (终局对决 · 抵达钩子的反面)", 10, "high", 11),
    ]
    return _expand_ordered(beats, n)


# 皮克斯22条法则 — 逐场工艺焦点 (三幕骨架 + 22 条法则按场分配)
_PIXAR_22_RULES = ["观众认同", "好奇心", "潜文本", "简单清晰", "找到笑点",
                   "兑现情感承诺", "故事脊椎", "主角主动性", "设定预期", "超越预期",
                   "视觉化讲故事", "戏剧张力", "角色优先", "情感真相", "内心独白",
                   "缺点让角色可爱", "目标明确", "冲突是引擎", "让动作说话", "节奏感",
                   "结尾有新意", "让故事永恒"]


def _beats_pixar22(n):
    """皮克斯22条故事法则 — 皮克斯影片是经典三幕 (once upon a time... until finally...),
    22条是工艺法则而非结构拍, 故按三幕骨架展开, 每场分配一条法则作为工艺焦点.
    """
    skeleton = [
        (1, "建置 (Once upon a time · 日常)", 3, "mid", 7),
        (1, "触发 (Until one day · 打破)", 6, "high", 9),
        (2, "旅程开始 (Because of that · 上路)", 5, "mid", 8),
        (2, "中点 (Because of that · 反转)", 8, "high", 11),
        (2, "失去一切 (Until finally · 坠落)", 9, "high", 10),
        (2, "黑夜 (内在抉择)", 9, "low", 9),
        (3, "高潮 · 终局对决", 10, "high", 11),
        (3, "解决 · 新生活 (And ever since then)", 4, "low", 6),
    ]
    beats = _expand_ordered(skeleton, n)
    for i, b in enumerate(beats):
        rule_idx = i % len(_PIXAR_22_RULES)
        b["story_function"] = f"{b['story_function']} · 法则#{rule_idx + 1}{_PIXAR_22_RULES[rule_idx]}"
    return beats


def _beats_dual_line(n):
    """双线并行 (A线主线 + B线副线交替推进, 交汇点在中点与高潮)."""
    beats = [
        (1, "A线建置 (主线 · 外部目标)", 4, "mid", 7),
        (1, "B线建置 (副线 · 情感关系)", 3, "mid", 7),
        (1, "A线触发 (主线事件爆发)", 6, "high", 9),
        (2, "B线回响 (副线映照主线)", 5, "mid", 8),
        (2, "A线发展 (主线推进)", 6, "mid", 8),
        (2, "B线发展 (关系深化)", 5, "mid", 8),
        (2, "A线B线第一次交汇", 7, "high", 10),
        (2, "A线冲突升级", 7, "high", 10),
        (2, "B线危机 (关系破裂边缘)", 7, "high", 10),
        (2, "中点 · A线B线碰撞", 8, "high", 11),
        (2, "A线失去一切", 9, "high", 10),
        (2, "B线灵魂黑夜", 9, "low", 9),
        (3, "A线B线合流 · 决定", 7, "mid", 9),
        (3, "高潮 · A线B线合力终局", 10, "high", 11),
        (3, "A线解决 (外部目标落定)", 5, "low", 7),
        (3, "B线解决 · 主题升华", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_multi_line(n):
    """三线交织 (A/B/C 三线,  Crash/通天塔 式) — 三线各自独立, 高潮处撞击交汇."""
    beats = [
        (1, "A线建置 (第一组人物)", 4, "mid", 7),
        (1, "B线建置 (第二组人物)", 3, "mid", 7),
        (1, "C线建置 (第三组人物)", 3, "mid", 7),
        (1, "三线共同触发 (同一事件折射)", 6, "high", 9),
        (2, "A线发展 (困境加深)", 6, "mid", 8),
        (2, "B线发展 (选择逼近)", 5, "mid", 8),
        (2, "C线发展 (秘密浮现)", 5, "mid", 8),
        (2, "A线B线第一次擦肩", 6, "mid", 9),
        (2, "中点 · 三线同时受挫", 8, "high", 11),
        (2, "A线危机升级", 7, "high", 10),
        (2, "B线危机升级", 7, "high", 10),
        (2, "C线灵魂黑夜", 9, "low", 9),
        (3, "三线汇聚 · 命运交叉", 8, "high", 10),
        (3, "高潮 · 三线撞击 (代价与救赎)", 10, "high", 11),
        (3, "A线余波", 5, "low", 7),
        (3, "B线余波", 4, "low", 6),
        (3, "C线余波 · 主题收束", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_pov(n):
    """POV多视角切换 (罗生门式) — 同一事件经不同视角折射, 真相由碎片拼合."""
    beats = [
        (1, "视角A · 开场 (A 所见的世界)", 4, "mid", 7),
        (1, "视角B · 开场 (B 所见的世界)", 4, "mid", 7),
        (1, "视角A · 事件爆发", 6, "high", 9),
        (1, "视角C · 旁观者证词", 5, "mid", 8),
        (2, "视角B · 隐藏动机", 6, "mid", 8),
        (2, "视角A · 中点 (A 的真相)", 8, "high", 11),
        (2, "视角C · 中点 (C 的真相 · 与A矛盾)", 8, "high", 10),
        (2, "视角B · 秘密暴露", 8, "high", 10),
        (2, "多视角 · 黑夜 (各执一词 · 真相崩塌)", 9, "low", 9),
        (3, "多视角 · 汇合 (碎片拼合)", 8, "high", 10),
        (3, "全知视角 · 高潮 (真相全貌)", 10, "high", 11),
        (3, "视角A · 解决 (重看开场)", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_nonlinear(n):
    """非线性 (闪回/闪前/碎片, 诺兰/低俗小说式) — 时间线打乱重组, 情绪优先于时序."""
    beats = [
        (1, "开场悬念 (in medias res · 半路杀入)", 6, "high", 9),
        (1, "闪回 · 过去时间线开始", 4, "mid", 7),
        (1, "过去 · 铺垫 (一切的起因)", 4, "mid", 7),
        (2, "现在 · 调查/追寻", 5, "mid", 8),
        (2, "过去 · 深化 (关系与选择)", 5, "mid", 8),
        (2, "现在/过去 交叉剪辑 · 逼近真相", 7, "high", 10),
        (2, "中点 · 关键闪回 (大反转)", 8, "high", 11),
        (2, "现在 · 危机爆发", 8, "high", 10),
        (2, "碎片汇聚 · 黑夜 (记忆与真相之争)", 9, "low", 9),
        (3, "现在/过去 汇合", 8, "high", 10),
        (3, "高潮 · 真相与抉择", 10, "high", 11),
        (3, "解决 · 主题升华", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_loop(n):
    """循环叙事 (开端=结尾, 星际穿越/前目的地式) — 起点即终点, 故事是一个环."""
    beats = [
        (1, "开场钩子 (先给结果 · 谜样场景)", 6, "high", 9),
        (1, "倒叙 · 起点 (一切尚未发生)", 3, "mid", 6),
        (1, "铺垫 · 命运的伏笔", 4, "mid", 7),
        (2, "触发 (与开场细节呼应)", 6, "high", 9),
        (2, "发展 · 逼近循环", 5, "mid", 8),
        (2, "中点 · 循环的线索 (似曾相识)", 8, "high", 11),
        (2, "深化 · 细节逐一重现", 7, "high", 10),
        (2, "黑夜 · 意识到循环", 9, "low", 9),
        (3, "挣扎 · 试图打破循环", 8, "high", 10),
        (3, "高潮 · 回到开场一幕 (真相揭示)", 10, "high", 11),
        (3, "收束 · 开场重现 (意义反转)", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_sequence25(n):
    """序列剧25场序列 (Syd Field 8-Sequence) — 8 个序列各有独立小张力弧, 大三幕套小三幕."""
    beats = [
        (1, "序列1 · 现状 (日常)", 3, "mid", 6),
        (1, "序列1 · 转折点 (触发事件)", 5, "high", 9),
        (1, "序列2 · 复杂化 (问题浮现)", 5, "mid", 8),
        (1, "序列2 · 小高潮 (第一次冲突)", 6, "high", 9),
        (2, "序列3 · 上升动作 (障碍叠加)", 6, "mid", 8),
        (2, "序列3 · 小高潮 (小胜)", 7, "high", 10),
        (2, "序列4 · 中点危机 (大反转)", 8, "high", 11),
        (2, "序列4 · 危机余波 (重新站队)", 6, "mid", 8),
        (2, "序列5 · 新方向 (反击开始)", 6, "mid", 8),
        (2, "序列5 · 小高潮 (首次胜利)", 7, "high", 10),
        (2, "序列6 · 黑暗时刻 (失去一切)", 9, "low", 9),
        (2, "序列6 · 觉醒 (决定反击)", 7, "mid", 9),
        (3, "序列7 · 最后冲刺 (孤注一掷)", 8, "high", 10),
        (3, "序列7 · 小高潮 (决战前夜)", 9, "high", 10),
        (3, "序列8 · 高潮 (终局对决)", 10, "high", 11),
        (3, "序列8 · 解决 (新平衡)", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _beats_road_journey(n):
    """公路片 (旅程递进) — 路本身就是结构, 每一站是一个节拍."""
    beats = [
        (1, "出发 · 离家 (触发事件)", 4, "mid", 7),
        (1, "第一站 · 新世界 (规则变化)", 5, "mid", 8),
        (2, "同行者 · 遇见伙伴", 5, "mid", 8),
        (2, "障碍 · 失去补给/走错路", 6, "high", 9),
        (2, "中点 · 十字路口 (重大选择)", 8, "high", 11),
        (2, "劫匪 · 危机 (外部威胁)", 7, "high", 10),
        (2, "黑夜 · 篝火 (告白与和解)", 9, "low", 9),
        (3, "最后一站 · 抵达目的地", 7, "mid", 9),
        (3, "高潮 · 对峙 (旅程真正寻找的东西)", 10, "high", 11),
        (3, "归途 · 新的旅程 (人已改变)", 4, "low", 6),
    ]
    return _expand_ordered(beats, n)


def _expand_beats_to_n(base_beats, n, beat_type, ratios=None, positions=None, preserve_act=False):
    """将基础 beats (例如 15 拍) 扩展/压缩到 n 个 beats.
    策略:
      - 如果 n >= len(base_beats): 按比例拉伸 (复制 + 续)
      - 如果 n < len(base_beats): 按关键位置 (开场/中点/收束) 选
    ratios: V14.3 E4 — 三幕占比 (r1,r2,r3), 默认 (0.25,0.50,0.25)。
    positions: V14.3 E4 — 关键拍位置 {"climax","dark","mid"}, 默认经典位。
    preserve_act: V14.3 E4 — True 时保留 ratios 分幕结果, 不被 25/75 重定幕。
    """
    if n <= 0:
        return []
    if not base_beats:
        return []

    _r1, _r2, _r3 = ratios if (isinstance(ratios, (tuple, list)) and len(ratios) == 3) else (0.25, 0.50, 0.25)
    # 按 act 1/2/3 比例切 (默认 25%/50%/25%)
    n_act1 = max(1, round(n * _r1))
    n_act2 = max(1, round(n * _r2))
    n_act3 = n - n_act1 - n_act2
    if n_act3 < 1:
        n_act3 = 1
        n_act2 = n - n_act1 - n_act3
    if n_act2 < 1:
        n_act2 = 1
        n_act1 = n - n_act2 - n_act3

    # 按 act 分基础 beats
    act1_beats = [b for b in base_beats if b[0] == 1]
    act2_beats = [b for b in base_beats if b[0] == 2]
    act3_beats = [b for b in base_beats if b[0] == 3]

    # 短视频 (1-2 场戏) 特殊
    if n == 1:
        return [_make_beat_dict(1, 1, act2_beats[len(act2_beats)//2] if act2_beats else base_beats[len(base_beats)//2])]
    if n == 2:
        return [
            _make_beat_dict(1, 1, act1_beats[0] if act1_beats else base_beats[0]),
            _make_beat_dict(3, 2, act3_beats[0] if act3_beats else base_beats[-1]),
        ]

    out = []
    scene_idx = 0
    for act, n_act, act_beats in [(1, n_act1, act1_beats), (2, n_act2, act2_beats), (3, n_act3, act3_beats)]:
        if n_act == 0:
            continue
        # 从 act_beats 选 n_act 个
        if n_act >= len(act_beats):
            # 全部用 + 续 (用动作变体后缀, 避免字面重复 " (续)" 的模板感)
            chosen = act_beats[:]
            i = 0
            # 6 种动作变体循环 — 深入/升级/回响/变形/变奏/再现
            suffix_pool = ["·深入", "·升级", "·回响", "·变形", "·变奏", "·再现"]
            # V13 修复 (B-P1): 变体只用非关键结构拍, 中点/高潮保持唯一 (不平铺循环)
            # V14.2 修复: 补 "黑夜"/"灵魂的黑夜"/"结尾" — 此前 "灵魂黑夜"≠"灵魂的黑夜" 失配,
            #             黑夜拍被复制成变体散落 38-67%, 导致结构错位。
            _key_markers = ("中点", "高潮", "midpoint", "climax", "Midpoint", "Climax",
                            "灵魂黑夜", "灵魂的黑夜", "黑夜", "失去一切", "结局", "结尾", "开场")
            variation_pool = [b for b in act_beats
                              if not any(km in str(b[1]) for km in _key_markers)]
            if not variation_pool:
                variation_pool = act_beats
            while len(chosen) < n_act:
                base_idx = i % len(variation_pool)
                base = variation_pool[base_idx]
                suf = suffix_pool[i % len(suffix_pool)]
                chosen.append((base[0], base[1] + suf, base[2], base[3], base[4]))
                i += 1
        else:
            # 按关键位置选
            chosen = []
            if n_act >= 1:
                chosen.append(act_beats[0])
            if n_act >= 2 and len(act_beats) > 1:
                chosen.append(act_beats[-1])
            if n_act >= 3:
                # 选中间
                mid_idx = len(act_beats) // 2
                if act_beats[mid_idx] not in chosen:
                    chosen.insert(1, act_beats[mid_idx])
            if n_act >= 4:
                # 按比例切
                step = len(act_beats) / (n_act - 1)
                for j in range(n_act - 2):
                    idx = int((j + 1) * step)
                    if idx < len(act_beats) and act_beats[idx] not in chosen:
                        chosen.append(act_beats[idx])
            # 去重 (按 story_function)
            seen = set()
            final = []
            for b in chosen:
                if b[1] not in seen:
                    final.append(b)
                    seen.add(b[1])
            chosen = final[:n_act]

        for b in chosen[:n_act]:
            scene_idx += 1
            out.append(_make_beat_dict(act, scene_idx, b))

    # V13.3: 关键节拍位置重排 — 中点≈50%, 灵魂黑夜≈72%, 高潮≈88% (修复中点落在29%的结构缺陷)
    # V14.3 E4: positions 允许结构自定义关键拍位 (变体不被经典位压平)
    out = _reposition_key_beats(out, preserve_act=preserve_act, positions=positions)
    return out


def _reposition_key_beats(beats, preserve_act=False, positions=None):
    """把关键结构节拍移动到经典位置 (按全片进度), 其余节拍保持相对顺序.
    preserve_act: V14.2 — True 时保留源节拍的 act 标签 (五幕/四幕/起承转合 等多幕结构),
                  不重定为 1/2/3 幕.
    positions: V14.3 E4 — {"climax":0.88,"dark":0.72,"mid":0.50} 自定义关键拍位置
               (三幕剧变体等结构用自己的位置, 不再被经典位压平)。
    """
    n = len(beats)
    if n < 5:
        return beats

    _pos = {"climax": 0.88, "dark": 0.72, "mid": 0.50}
    if isinstance(positions, dict):
        _pos.update(positions)

    def _find(pred):
        for i, b in enumerate(beats):
            if pred(b["story_function"]):
                return i
        return -1

    def _find_dark_night():
        # V14.2 修正: 优先定位真正的"灵魂黑夜"拍; 无则退回"失去一切"。
        # 此前 first-match 在救猫咪里先命中"失去一切"(黑夜前一拍), 把黑夜留在前段 → 结构错位。
        for i, b in enumerate(beats):
            if "灵魂黑夜" in b["story_function"] or "灵魂的黑夜" in b["story_function"]:
                return i
        for i, b in enumerate(beats):
            if "失去一切" in b["story_function"]:
                return i
        return -1

    # 目标: (匹配函数, 目标位置比例) — 按重要性顺序放置
    targets = [
        (lambda s: any(k in s for k in ["高潮", "对决", "终局", "climax"]), _pos["climax"]),
        (None, _pos["dark"]),  # 黑夜 — 用 _find_dark_night 优先定位 (见下)
        (lambda s: any(k in s for k in ["中点", "midpoint", "Midpoint"]), _pos["mid"]),
    ]
    # 取出关键节拍
    picked = []  # (target_idx, beat)
    for pred, ratio in targets:
        idx = _find_dark_night() if pred is None else _find(pred)
        if idx >= 0:
            picked.append((int(round(ratio * (n - 1))), beats[idx]))
    # 从序列中移除
    picked_set = set(id(b) for _, b in picked)
    rest = [b for b in beats if id(b) not in picked_set]
    # 插入到目标位置 (其余节拍顺序不变)
    for target_idx, beat in sorted(picked, key=lambda x: x[0]):
        target_idx = max(0, min(len(rest), target_idx))
        rest.insert(target_idx, beat)
    # 重新编号 scene_index (+ 按位置重定幕 25%/75% 分界 — preserve_act 时保留原幕标签)
    b1 = int(round(n * 0.25))
    b2 = int(round(n * 0.75))
    for i, b in enumerate(rest):
        b["scene_index"] = i + 1
        if not preserve_act:
            b["act"] = 1 if i < b1 else (2 if i < b2 else 3)
    return rest


def _make_beat_dict(act, scene_idx, beat_tuple):
    """beat_tuple: (act, story_function, tension, density, shots)"""
    return {
        "act": act,
        "scene_index": scene_idx,
        "story_function": beat_tuple[1],
        "tension": beat_tuple[2],
        "dialogue_density": beat_tuple[3],
        "base_shots": beat_tuple[4],
    }


def _expand_ordered(base_beats, n):
    """V14.2: 有序展开 (理论节拍列表专用) — 保持源顺序, 继承源节拍的 act 标签.
    - n >= len(base): 按权重 (base_shots) 给每个节拍分配场数 — 长节拍 (乐趣与游戏/试炼/发展)
      自然获得更多场次, 变体后缀 (深入/升级/回响...) 避免字面复读.
    - n < len(base): 优先保留 高潮(最高张力拍)/首/尾/中点/黑夜, 其余名额按位置均匀补.
    最后经 _reposition_key_beats(preserve_act=True) 校准关键拍位置 (中点≈50%/黑夜≈72%/高潮≈88%).
    """
    m = len(base_beats)
    if n <= 0 or m == 0:
        return []
    if n == 1:
        b = base_beats[m // 2]
        return [_make_beat_dict(b[0], 1, b)]
    if n == 2:
        return [
            _make_beat_dict(base_beats[0][0], 1, base_beats[0]),
            _make_beat_dict(base_beats[-1][0], 2, base_beats[-1]),
        ]

    if n < m:
        # 压缩: 按优先级保留关键拍 — 高潮(最高张力) > 首 > 尾 > 中点 > 黑夜 > 转折
        climax_i = max(range(m), key=lambda i: base_beats[i][2])
        priority = {climax_i: 0, 0: 1, m - 1: 2}
        for i, b in enumerate(base_beats):
            sf = str(b[1])
            if "中点" in sf:
                priority.setdefault(i, 3)
            elif "黑夜" in sf or "失去一切" in sf:
                priority.setdefault(i, 4)
            elif "危机" in sf or "转" in sf:
                priority.setdefault(i, 5)
        ranked = sorted(priority.keys(), key=lambda i: (priority[i], i))
        keep = sorted(ranked[:n])
        if len(keep) < n:
            kept_set = set(keep)
            fill = [i for i in range(m) if i not in kept_set]
            step = max(1, m // max(n - len(keep), 1))
            for i in fill[::step]:
                if len(keep) >= n:
                    break
                keep.append(i)
            keep = sorted(keep)[:n]
        return [_make_beat_dict(base_beats[i][0], k + 1, base_beats[i])
                for k, i in enumerate(keep)]

    # n >= m: 按权重分配场数 (每个节拍至少 1 场)
    weights = [max(1, int(b[4])) for b in base_beats]
    alloc = [1] * m
    extra = n - m
    order = sorted(range(m), key=lambda i: -weights[i])
    j = 0
    while extra > 0:
        alloc[order[j % m]] += 1
        extra -= 1
        j += 1
    suffix_pool = ["·深入", "·升级", "·回响", "·变形", "·变奏", "·再现"]
    out = []
    scene_idx = 0
    for bi, b in enumerate(base_beats):
        for c in range(alloc[bi]):
            scene_idx += 1
            if c == 0:
                out.append(_make_beat_dict(b[0], scene_idx, b))
            else:
                suf = suffix_pool[(c - 1) % len(suffix_pool)]
                vb = (b[0], b[1] + suf, b[2], b[3], b[4])
                out.append(_make_beat_dict(b[0], scene_idx, vb))
    return _reposition_key_beats(out, preserve_act=True)


# Type → beat generator
TYPE_BEAT_GENERATORS = {
    "film_epic": _beats_hero_journey,
    "epic": _beats_hero_journey,
    "film_art": _beats_mckee_story_value,
    "art": _beats_mckee_story_value,
    "film_drama": _beats_drama_three_act,
    "drama": _beats_drama_three_act,
    "film_romance": _beats_love_romance,
    "romance": _beats_love_romance,
    "love": _beats_love_romance,
    "film_thriller": _beats_thriller_suspense,
    "thriller": _beats_thriller_suspense,
    "film_comedy": _beats_comedy_misunderstanding,
    "comedy": _beats_comedy_misunderstanding,
    "film_horror": _beats_dark_psychological,
    "horror": _beats_dark_psychological,
    "dark": _beats_dark_psychological,
    "documentary": _beats_doc_chronicle,
    "doc": _beats_doc_chronicle,
    "save_the_cat": _beats_save_the_cat,
    "default": _beats_drama_three_act,
}


# V14.2: 叙事理论 → beat generator (修复 Script 模式坍缩: 叙事结构下拉/结构类模式
# 此前只追加附录文本, 节拍主体一律落到 type 默认生成器 → 30+ 结构选项输出同构)。
# 现在每种理论有自己的节拍骨架; 类型化叙事复用对应 type 生成器 (它们本就是类型节拍)。
THEORY_BEAT_GENERATORS = {
    # 经典结构理论
    "three_act": _beats_drama_three_act,
    "three_act_variant": _beats_three_act_variant,
    "four_act": _beats_four_act,
    "five_act": _beats_five_act,
    "seven_point": _beats_seven_point,
    "kishotenketsu": _beats_kishotenketsu,
    "save_the_cat": _beats_save_the_cat,
    "hero_journey": _beats_hero_journey,
    "mckee": _beats_mckee_story_value,
    "pixar22": _beats_pixar22,
    "sequence": _beats_sequence25,
    # 现代叙事变体
    "dual_line": _beats_dual_line,
    "multi_line": _beats_multi_line,
    "pov": _beats_pov,
    "nonlinear": _beats_nonlinear,
    "loop": _beats_loop,
    # 类型化叙事 → 复用 type 生成器
    "road": _beats_road_journey,
    "suspense": _beats_thriller_suspense,
    "horror": _beats_dark_psychological,
    "comedy": _beats_comedy_misunderstanding,
    "romance": _beats_love_romance,
    "epic": _beats_hero_journey,
    "noir": _beats_dark_psychological,
    "growth": _beats_drama_three_act,
    "revenge": _beats_thriller_suspense,
}


def _normalize_theory(story_theory):
    """V14.2: 把 叙事结构 下拉值/结构模式名 归一化为 THEORY_BEAT_GENERATORS 键.
    返回 None 表示无匹配 (落回 type 生成器)。
    匹配顺序有讲究: 五幕 先于 三幕, 循坏 先于 非线性, 避免子串误匹配。
    """
    if not story_theory:
        return None
    s = str(story_theory)
    if "五幕" in s:
        return "five_act"
    if "四幕" in s:
        return "four_act"
    if "七点" in s:
        return "seven_point"
    if "起承转合" in s:
        return "kishotenketsu"
    if "救猫咪" in s:
        return "save_the_cat"
    if "英雄之旅" in s:
        return "hero_journey"
    if "麦基" in s or "McKee" in s:
        return "mckee"
    if "皮克斯" in s or "22条" in s:
        return "pixar22"
    if "序列" in s:
        return "sequence"
    if "章节" in s:
        return "sequence"  # 章节式 (每章独立节奏) 结构上等价序列剧的逐序列小弧
    if "双线" in s:
        return "dual_line"
    if "三线" in s:
        return "multi_line"
    if "POV" in s or "多视角" in s:
        return "pov"
    if "循环" in s:
        return "loop"
    if "非线性" in s or "闪回" in s or "闪前" in s or "碎片" in s:
        return "nonlinear"
    if "三幕" in s and "变体" in s:
        return "three_act_variant"
    if "三幕" in s:
        return "three_act"
    # 类型化叙事
    if "悬疑" in s or "惊悚" in s:
        return "suspense"
    if "恐怖" in s:
        return "horror"
    if "喜剧" in s:
        return "comedy"
    if "爱情" in s:
        return "romance"
    if "动作" in s:
        return "save_the_cat"  # 动作任务递进走商业 15 拍
    if "史诗" in s:
        return "epic"
    if "黑色" in s or "反英雄" in s:
        return "noir"
    if "公路" in s:
        return "road"
    if "成长" in s or "蜕变" in s:
        return "growth"
    if "复仇" in s:
        return "revenge"
    return None


# --- Director 覆盖 (按导演风格调整节拍节奏) ---
# 关键: 不是固定节拍, 而是"调整规则" — 应用在生成结果上
DIRECTOR_OVERRIDES = {
    "王家卫": {
        "tension_modifier": lambda t: max(1, min(10, t + (-1 if t > 5 else 0))),  # 中段张力下沉
        "duration_modifier": lambda d: d * 1.3,  # 每场戏延长 30% (留白多)
        "skip_probability": 0.2,  # 20% 概率跳过某些节拍 (留白)
    },
    "诺兰": {
        "tension_modifier": lambda t: max(1, min(10, t + (1 if t > 5 else 0))),  # 持续上升
        "duration_modifier": lambda d: d,  # 不变
        "skip_probability": 0.0,  # 不跳
    },
    "塔可夫斯基": {
        "tension_modifier": lambda t: max(1, min(10, t * 0.5)),  # 持续低张力
        "duration_modifier": lambda d: d * 1.5,  # 每场戏延长 50% (极慢)
        "skip_probability": 0.0,
    },
    "希区柯克": {
        "tension_modifier": lambda t: max(1, min(10, t + 0.5)),  # 持续高张力
        "duration_modifier": lambda d: d,
        "skip_probability": 0.0,
    },
    "default": {
        "tension_modifier": lambda t: t,
        "duration_modifier": lambda d: d,
        "skip_probability": 0.0,
    },
}


def _normalize_director(director):
    """V12.6 v13 + V13.3: 归一化导演名 → 15 种派别.
    V13.3: 新增 张艺谋(视觉仪式)/维伦纽瓦(巨物沉默)/宫崎骏(自然灵动)/周星驰(无厘头节奏) 4 派,
    并把 534 导演库中的常见导演按风格亲和度映射到派别, 不再大量落入 default.
    """
    if not director:
        return "default"
    if any(k in director for k in ["王家卫", "Wong Kar-wai", "wong", "kar-wai"]):
        return "王家卫"
    if any(k in director for k in ["侯孝贤", "Hou Hsiao-hsien", "hou"]):
        return "侯孝贤"
    if any(k in director for k in ["是枝裕和", "Koreeda", "koreeda"]):
        return "是枝裕和"
    if any(k in director for k in ["李安", "Ang Lee", "ang lee", "陈凯歌", "冯小刚", "顾长卫"]):
        return "李安"
    if any(k in director for k in ["贾樟柯", "Jia Zhangke", "zhangke"]):
        return "贾樟柯"
    if any(k in director for k in ["诺兰", "Nolan", "nolan", "Christopher"]):
        return "诺兰"
    if any(k in director for k in ["塔可夫斯基", "Tarkovsky", "tarkovsky"]):
        return "塔可夫斯基"
    if any(k in director for k in ["希区柯克", "Hitchcock", "hitchcock", "芬奇", "Fincher"]):
        return "希区柯克"
    if any(k in director for k in ["黑泽明", "Kurosawa", "kurosawa", "雷德利", "Ridley", "塞缪尔"]):
        return "黑泽明"
    if any(k in director for k in ["库布里克", "Kubrick", "kubrick", "韦斯·安德森", "Wes Anderson"]):
        return "库布里克"
    # V13.3 新增派别
    if any(k in director for k in ["张艺谋", "Yimou", "陈可辛", "徐克", "程小东"]):
        return "张艺谋"
    if any(k in director for k in ["维伦纽瓦", "Villeneuve", "阿方索", "Cuarón", "诺斯费拉图"]):
        return "维伦纽瓦"
    if any(k in director for k in ["宫崎骏", "Miyazaki", "新海诚", "细田守", "高畑勋", "吉卜力"]):
        return "宫崎骏"
    if any(k in director for k in ["周星驰", "刘镇伟", "王晶", "喜剧", "甜宠", "爆款"]):
        return "周星驰"
    return "default"


# ============================================================
# V12.6 v13: 11 派别导演 action 模板池 (按导演派别生成独有动作描述)
# 关键: 每派别 6-8 个模板, 总 70+ 模板, 杜绝单模板拼凑感
# 占位符: {location} {time} {weather_str} {event} {c1} {c2} {c3} {mood} {obj} {obj_str} {obj_phrase} {subtext} {internal}
# ============================================================
DIRECTOR_ACTION_TEMPLATES = {
    # 王家卫派: 时间拉长, 留白, 半拍, 物件符号化
    "王家卫": [
        "{location}, {time}. 镜头从{c2}的眼角缓缓推到{c1}的手, 走了3秒. {event}. {c1}的动作慢了半拍, 但眼神闪到门缝.{internal} {obj_phrase} {subtext}.",
        "时间被拉长. 雨淋进{location}的窗缝. {event}. {c1}背对, 烟灰落了一节才察觉.{internal} {obj_phrase} {subtext}.",
        "固定中景, 不切. {event}. {c1}在{location}, 手指停在半空, 3秒不回头.{internal} {obj_phrase} {subtext}.",
        "霓虹在{time}反光. {event}. {c1}和{c2}擦肩, 谁也没看谁, 但走了3步, {c1}回头了.{internal} {subtext}.",
        "{c1}的影子被拉得很长. {event}. 镜头跟着影子走, 不跟人. {obj_phrase} {subtext}.",
        "60秒一个长镜, 观众可以看{c1}眨眼. {event}. {c1}的呼吸是这段戏的主旋律.{internal} {subtext}.",
    ],
    # 侯孝贤派: 长焦远景, 自然光, 不切, 走20秒才到镜头前
    "侯孝贤": [
        "长焦远景. {c1}走入{location}, 走了20秒才到镜头前. {event}. 风把{obj}吹动了, {c1}没察觉.{subtext}.",
        "固定远景, 不切. {c1}在{location}做无意义的事: 擦桌, 看云, 整理衣角. {event}. 远处有小孩跑过.{subtext}.",
        "黄昏, 门框切人. {event}. {c1}和{c2}隔门对望, 谁也不先开口, 画面停了8秒.{subtext}.",
        "自然光, 不打灯. {c1}的影子自己说话. {event}. {obj_phrase} 镜头没有解释, 观众自己读.{subtext}.",
        "运镜像纪录片. {event}. {c1}在{location}的动作有日常节奏, 像在做家务.{subtext}.",
        "中景长镜. {c1}吃完一碗面, 端碗去厨房, 回来时已经过了30秒. {event}. {subtext}.",
    ],
    # 是枝裕和派: 家庭厨房, 日常光, 吃食, 沉默
    "是枝裕和": [
        "厨房的日常光. {event}. {c1}切菜的声音比对话更重要 — 刀碰砧板的节拍, 就是这段戏的BPM. {obj_phrase} {subtext}.",
        "饭桌上. {c1}夹菜, 看了{c2}一眼, 没说话, 又把菜放回碗里. {event}. {internal} {subtext}.",
        "中景, 不切. {c1}洗碗, {c2}站在旁边, 两个人共处一个空间, 各自沉默. {event}. {obj_phrase} {subtext}.",
        "电风扇转. {event}. {c1}在客厅, {obj}摆在桌上, 没人提. 家庭日常, 但都有秘密.{subtext}.",
        "傍晚, 厨房. {c1}做便当, 装进{c2}的书包. {event}. 这动作每天重复, 但今天的盒盖, {c1}合不上.{subtext}.",
        "门口. {c2}出门, {c1}在背后说'路上小心', 声音平淡, 像说了一千遍. {event}. {subtext}.",
    ],
    # 李安派: 文化冲突, 家庭内部对峙, 理性与情感的撕扯
    "李安": [
        "镜头从书桌推到窗外, 再拉回, 用了5秒. {event}. {c1}和{c2}在{location}对峙, 谁也不让. {internal} {subtext}.",
        "中景+长焦. {c1}的字迹很轻, 但他写得很重. {event}. {obj_phrase} {subtext}.",
        "家庭会议式的固定镜头. {event}. {c1}在{location}做了理性决定, 但{c2}的眼神暴露了情感撕裂. {subtext}.",
        "跨文化冲突的内在戏. {c1}用A文化的姿态, 但眼睛里是B文化的纠结. {event}. {obj_phrase} {subtext}.",
        "对白密度高, 但潜文本更强. {event}. {c1}说的每句, 都和心里的相反.{internal} {subtext}.",
        "长镜+特写交替. {c1}在{location}的一举一动, 都被家庭的眼睛注视. {event}. {subtext}.",
    ],
    # 贾樟柯派: 县城, 时代感, 广场舞, 流行歌, 纪录片质感
    "贾樟柯": [
        "县城, 卡拉OK厅, 90年代流行歌. {event}. {c1}在{location}的桌前, 像被时代拖着走. {obj_phrase} {subtext}.",
        "长焦+广角交替. {c1}的工厂大门, 烟囱, 远处电视塔. {event}. 这是{time}的中国县城. {subtext}.",
        "纪录片式手持. {c1}走过县城广场, 广场舞音响就在背景里. {event}. {internal} {subtext}.",
        "MTV 流行歌插入. 歌曲和画面对位, 但歌词说的是另一件事. {event}. {obj_phrase} {subtext}.",
        "县城理发店, 录像厅, 溜冰场. {c1}在{location}, 时代从他身上流过. {event}. {subtext}.",
        "突然的特写打脸, 然后又切到远景. {c1}的脸, 是{time}的标本. {event}. {subtext}.",
    ],
    # 诺兰派: 叙事结构, 时间折叠, 概念先行
    "诺兰": [
        "{location}的几何感. {event}. {c1}在做A, 但镜头的对焦点暗示B. {obj_phrase} {subtext}.",
        "时间折叠. 同一空间, 三个时间层同时出现. {event}. {c1}在{location}看到一个过去的自己. {subtext}.",
        "概念隐喻. 钟表/镜子/走廊. {event}. {c1}在{location}, 时间在他身上分层. {obj_phrase} {subtext}.",
        "悬念+倒叙. {event}. 镜头先给结果, 再回到原因. {c1}已经知道结局, 但观众不知道. {subtext}.",
        "空间对称. {c1}和{c2}在{location}的两端, 中间是对称的影像. {event}. {internal} {subtext}.",
        "宏大与渺小同框. {c1}在{location}, 背景是宇宙级的尺度. {event}. {obj_phrase} {subtext}.",
    ],
    # 塔可夫斯基派: 水, 火, 雾, 诗, 长镜, 极慢
    "塔可夫斯基": [
        "水面, 雨滴, 长镜7秒. {event}. {c1}在{location}像水一样流动, 但内心是石头. {obj_phrase} {subtext}.",
        "风吹过, 蜡烛摇. {event}. {c1}的脸, 被摇曳的烛光重新照亮一次. {internal} {subtext}.",
        "雾, 一切都被模糊. {c1}在{location}的轮廓, 5秒后才清晰. {event}. {subtext}.",
        "动物 (马, 鸟, 狗) 走过, 不解释. {event}. {c1}看动物的眼神, 比看人更专注. {obj_phrase} {subtext}.",
        "日常物件升格: 一杯水, 一本书, 一根烛. {event}. 镜头给它们特写, 跟给{c1}一样. {subtext}.",
        "梦境般的运镜. 镜头飘, 不靠轨. {event}. {c1}在{location}, 现实和梦的边界模糊. {subtext}.",
    ],
    # 希区柯克派: 悬念, 焦点转移, 偷窥视角, 物件伏笔
    "希区柯克": [
        "焦点从{obj}转到{c1}的脸, 用了2秒. {event}. 观众比{c1}先知道真相. {subtext}.",
        "偷窥视角, 镜头是{location}的墙壁或窗. {event}. {c1}不知道被看, 但{obj_phrase} 让观众紧张. {subtext}.",
        "伏笔. 一个细节 ({obj}) 在画面边缘出现0.5秒. {event}. 30分钟后, 这细节会决定生死. {subtext}.",
        "声画错位. 听到的是A, 看到的是B. {event}. {c1}在{location}说话, 但嘴型和声音不符. {subtext}.",
        "麦格芬 (MacGuffin). {obj}很重要, 但没人知道它是什么. {event}. {c1}追, 观众也追. {subtext}.",
        "楼梯/走廊的纵深. {c1}在{location}的走廊, 镜头从尽头看. {event}. 谁先走出, 谁就是凶手. {subtext}.",
    ],
    # 黑泽明派: 多机位, 动态构图, 大远景
    "黑泽明": [
        "多机位同时拍一个动作. 同一秒, 4个角度的{c1}在{location}同时存在. {event}. {obj_phrase} {subtext}.",
        "大远景开场. 风云变, 千军万马, {c1}骑在马上只是其中一员. {event}. {subtext}.",
        "天气是演员. 风/雨/雪, 它们是{location}的另一个角色. {event}. {c1}和天气搏斗. {subtext}.",
        "动作戏用多重剪接. {c1}的刀, 在7个机位之间跳. {event}. {obj_phrase} {subtext}.",
        "天气转变暗示命运. {time}从晴转暴, {c1}在{location}, 也从希望转到绝望. {event}. {subtext}.",
        "群像构图, {c1}在画面一角, 但眼神指挥整个画面. {event}. {obj_phrase} {subtext}.",
    ],
    # 库布里克派: 对称, 一镜一念, 凝视
    "库布里克": [
        "绝对对称. {location}的中线把画面切两半, {c1}在中央. {event}. 这是命运的十字架. {subtext}.",
        "一镜一念. 30秒长镜, 镜头没动, 但{c1}的内心走了一年. {event}. {obj_phrase} {subtext}.",
        "凝视镜头. {c1}看观众. 观众没地方躲. {event}. {subtext}.",
        "一镜一念 (续). 镜头不变, 但{c1}的位置微调, 暗示心理位移. {event}. {subtext}.",
        "走廊/楼梯的纵深几何. {c1}在{location}的纵深, 越走越小, 越走越远. {event}. {subtext}.",
        "慢动作+静止背景. {c1}在{location}慢动作, 但环境不动, 形成诡异反差. {event}. {subtext}.",
    ],
    # V13.3 新增: 张艺谋派 — 大色块, 仪式感, 群体编排, 天地人对比
    "张艺谋": [
        "{location}, {time}. 大全景: 天地占九成, {c1}只是其中一个黑点. {event}. 色块铺满画面, {mood}是主色.{internal} {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. 一群人按仪式站位, {c1}在正中央, 一动不动. 风把所有人的衣角吹向同一边.{internal} {subtext}.",
        "{location}, {time}. {event}. 镜头从{c1}的脸摇到天际线, 用了整整十秒. {obj_phrase} {subtext}.",
        "{location}, {time}. 红与黑的对比里, {c1}站着, {c2}走来. {event}. 两人之间隔着整个画面.{internal} {subtext}.",
        "{location}, {time}. {event}. 俯拍: {c1}的影子投在大地上, 像一道疤. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}在{location}中央, 四周空无一人, 只有{mood}. 鼓点起, 画面定格.{internal} {subtext}.",
    ],
    # V13.3 新增: 维伦纽瓦派 — 巨物沉默, 尺度对比, 雾与轮廓, 极简对白
    "维伦纽瓦": [
        "{location}, {time}. 巨大的轮廓从雾里浮现, {c1}站在它脚下, 小得像一粒尘. {event}. 没有配乐, 只有低频.{internal} {subtext}.",
        "{location}, {time}. {event}. {c1}的剪影对着光源, 看不清脸. 沉默持续了很久, 没有人先说话.{obj_phrase} {subtext}.",
        "{location}, {time}. {event}. 镜头不动, 让{c1}在画面里走了很久, 尺度感压过来.{internal} {subtext}.",
        "{location}, {time}. 雾. {c1}的声音先出现, 人后出现. {event}. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}和{c2}隔着空旷对视, 中间的距离就是台词.{internal} {subtext}.",
        "{location}, {time}. {event}. 一个极慢的推镜, 从全景推到{c1}的眼睛, 用了二十秒. {mood}在空气里.{subtext}.",
    ],
    # V13.3 新增: 宫崎骏派 — 自然灵动, 风与飞行, 细节生命, 温柔节奏
    "宫崎骏": [
        "{location}, {time}. 风来了, 草浪一层层翻过去, {c1}的头发被吹起. {event}. 一切都活着.{internal} {subtext}.",
        "{location}, {time}. {event}. {c1}跑起来, 镜头跟着飞, 云在背景里慢慢移. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. 特写: 一滴露水从叶尖滑落, {c1}屏住呼吸看着.{internal} {subtext}.",
        "{location}, {time}. {c1}和{c2}并肩坐着, 看天. {event}. 云变成奇怪的形状, 两人同时笑了.{subtext}.",
        "{location}, {time}. {event}. 阳光穿过缝隙, 光斑落在{obj}上, 尘埃在光里跳舞. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}伸出手, 风从指缝穿过. 远处有东西在回应.{internal} {subtext}.",
    ],
    # V13.3 新增: 周星驰派 — 无厘头节奏, 反差, 快慢切换, 小人物尊严
    "周星驰": [
        "{location}, {time}. {event}. {c1}一脸严肃地做了件荒谬的事, {c2}在旁边看傻了. 节奏突然停半拍.{internal} {subtext}.",
        "{location}, {time}. {event}. 快切三连: {c1}的表情, {obj}, {c2}的反应. 然后一切恢复正常, 像没发生过.{subtext}.",
        "{location}, {time}. {c1}摆出高手架势, 音乐起——然后摔了一跤. {event}. 音乐戛然而止.{internal} {subtext}.",
        "{location}, {time}. {event}. {c1}认真地讲着歪理, {c2}竟然被说服了. 镜头在两人之间来回切.{obj_phrase} {subtext}.",
        "{location}, {time}. {event}. 慢镜: {c1}回头, 发丝飘起, 眼神深情——下一秒打了个喷嚏.{internal} {subtext}.",
        "{location}, {time}. {event}. {c1}在{location}里逞强, 嘴硬心软. 笑点过去后, 留下一秒真的{mood}.{subtext}.",
    ],
    # 三幕剧/默认: 经典结构 (V13.3 扩充句式多样性, 消除"都在说另一件事"复读)
    "default": [
        "{location}, {time}. {event}. {c1}在{location}, {mood}弥漫. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}先开口, 说的却不是心里那句. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}做了一个动作, 表面看是无意义的. {internal} {subtext}.",
        "{location}, {time}. {event}. {c1}的视线移到{obj}, 又移开. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c1}和{c2}隔着{obj}对坐, 谁都没先碰它. {subtext}.",
        "{location}, {time}. {event}. {c1}的动作停了, 但只有0.5秒, 然后又动. {internal} {subtext}.",
        "{location}, {time}. {event}. {c1}把到嘴边的话咽回去, 换了个话题. {obj_phrase} {subtext}.",
        "{location}, {time}. {event}. {c2}在等一个答案, {c1}给的是另一个动作. {internal} {subtext}.",
    ],
}


# V12.6 v13: tension 10 段 × 3 变体 = 30 个潜文本 (替代 V12 单 subtext_map)
SUBTEXT_VARIANTS = {
    1: ["表面平静, 像水面没动过", "日常, 表面无奇, 表面在写家庭作业", "一切都好, 一切都对, 一切都假"],
    2: ["像凌晨的厨房, 灯没开", "笑得很得体, 但眼角没动", "动作都对, 但呼吸节奏不对"],
    3: ["潜流在地面下, 还没发芽", "暗流开始, 但还在地面下", "温度没变, 但气压变了"],
    4: ["暗流开始涌动, 但还听不见", "门缝里透光, 但不知道是什么光", "手指停顿, 但只停了0.3秒"],
    5: ["表面平静, 实际紧张, 像拉满的弓", "呼吸均匀, 但肺活量变了", "对视3秒, 但都没在对方眼睛里"],
    6: ["冲突表面化, 但都还在说另一件事", "动作都还在, 但每个动作都是借口", "对话还在, 但每句都是辩论"],
    7: ["情绪紧张, 但都压抑, 没人先开口", "桌子拍响了, 但马上收回去", "走出去, 又走回来, 又走出去"],
    8: ["对峙, 即将爆发, 但爆发的那一刻还没到", "临界, 一切都在悬崖边", "眼神已经撕碎, 嘴还在维持体面"],
    9: ["至暗, 一切失去, 但{c1}还在维持", "沉默, 但沉默有重量", "手垂下来, 但还握着什么"],
    10: ["爆发, 一切释放, 但释放之后是更大的空", "喊出来, 但声音被吸走", "碎了, 但碎片还在手里"],
}


# V12.6 v13: 物件融入 3 类变体池 (替代 V12 单 obj_phrase 二选一)
OBJ_PHRASE_VARIANTS = {
    "core": [  # 主核心物件 (凤梨罐头/信/照片/笔)
        "{obj}摆在桌上, 像一个不被提起的名字.",
        "{obj}在{location}的角落, 没人在意, 但它在意.",
        "{obj}被风(无意/有意)动了一下.",
    ],
    "supplement": [  # 补充物件
        "{obj_str}放在一边, 没人看.",
        "{obj_str}靠在墙角, 像被遗忘的台词.",
        "{obj_str}在抽屉里, 半开, 像是有人要拿又没拿.",
    ],
}


# V12.6 v13: 内部动作 (tension → 身体细节) 3 套变体 (替代 V12 单二选一)
INTERNAL_ACTION_VARIANTS = {
    "high": [  # tension >= 7
        " {c1}的手微不可察地颤了一下.",
        " {c1}的呼吸停了半秒, 然后又续上.",
        " {c1}的指节发白, 但脸没变.",
    ],
    "mid": [  # 4-6
        " {c1}没抬头, 但呼吸变了.",
        " {c1}的动作慢了0.3秒, 然后又正常.",
        " {c1}的目光在{obj}上停了一瞬, 又移开.",
    ],
    "low": [  # 1-3
        " {c1}的动作自然, 但自然得有点假.",
        " {c1}的沉默, 比说话还大声.",
        " {c1}的微笑, 到了嘴角就停了.",
    ],
}


# V12.6 v13: 物件情感承载 — 30+ 物件, 缺省时按物件类型自动生成
OBJ_MEANING = {
    "旧信": "承载一段未说出口的话",
    "凤梨罐头": "象征一段被时间封存的过去",
    "钢笔": "象征未完成的表达",
    "老照片": "凝固一个再也回不去的瞬间",
    "母亲的旗袍": "一段缺席的母爱",
    "父亲的旧手表": "时间已经停止, 但还在走",
    "一把钥匙": "通向一个被封存的房间",
    "一本旧书": "一段被遗忘的过去",
    "一台老收音机": "另一个时代的声音还在响",
    "一只风筝": "一段无法放飞的心愿",
    "一双旧布鞋": "走过的路, 已经回不去",
    "一件褪色毛衣": "曾经贴身, 现在挂椅背",
    "一张车票": "一张没用的回程",
    "一枚戒指": "承诺过, 但没兑现",
    "一个铁盒": "装着一个秘密",
    "一支毛笔": "写过的话, 已经墨干",
    "一面老镜子": "看见自己, 但认不出来",
    "一块怀表": "时间停在某个时刻",
    "一份旧报纸": "曾经的新闻, 现在的历史",
    "一本日记": "写过又划掉的话",
    "一盒磁带": "录下的话, 但没人再听",
    "一条红绳": "一段牵绊, 还在手腕",
    "一张黑白合影": "一屋子的人, 现在散落天涯",
    "一份病历": "身体记录的事, 嘴不说",
    "一份工龄证明": "一辈子换一张纸",
    "一份离婚协议": "纸上的句号",
    "一份工资条": "数字记得清, 感情记不清",
    "一根拐杖": "曾经的路, 还要不要走",
    "一盒糖果": "甜到今天, 后面是苦",
    "一件军装": "打过仗, 但不说了",
    "一份战报": "赢了, 但失去的更多",
    "一份任命书": "一张纸, 换了一辈子",
    "一本诗集": "曾经读, 现在供",
    "一张粮票": "饿过, 才知道饱",
    "一份电报": "字少, 重量大",
    "一张地图": "想去的地方, 都成了回忆",
    "一把剪刀": "剪断, 还是剪开",
    "一根针": "细, 但能穿一切",
    "一块布": "包过, 也盖过",
    "一条围巾": "冷过, 才织的",
    "一只风筝线轴": "飞多远, 都在手上",
    "一份家书": "想家, 但写不出口",
    "一本护照": "去过, 但回不来",
    "一张船票": "一程的终点, 下一程的起点",
    "一份工分簿": "算得清的, 算不清的更多",
    "一面国旗": "举过的, 还在心里",
    "一枚勋章": "奖过的, 但沉默的更多",
    "一支老笛": "吹过, 没人听了",
    "一台缝纫机": "缝过的, 还在跑",
}


def _obj_meaning_auto(obj):
    """按物件类型自动生成情感承载, 找不到时按类型关键词匹配."""
    if not obj:
        return "用空间和声音承载"
    if obj in OBJ_MEANING:
        return OBJ_MEANING[obj]
    # 兜底: 按关键词匹配
    if any(k in obj for k in ["信", "书", "日记", "电报", "家书", "诗", "报纸", "病历", "证明", "协议", "工资", "战报", "任命", "粮票", "船票", "护照", "工分"]):
        return f"一张纸, 承载{obj}的字字句句"
    if any(k in obj for k in ["罐头", "盒", "糖", "收音机", "缝纫机", "手表", "怀表", "笛"]):
        return f"一件{obj}, 装着一个时代的声音"
    if any(k in obj for k in ["衣服", "旗袍", "毛衣", "军装", "围巾", "布", "鞋"]):
        return f"一件{obj}, 贴身过, 也凉过"
    if any(k in obj for k in ["照片", "合影", "镜子"]):
        return f"一段{obj}, 凝固的瞬间, 流不走"
    if any(k in obj for k in ["笔", "毛笔", "剪刀", "钥匙", "针", "刀", "拐杖", "线轴"]):
        return f"一件{obj}, 拿得起, 但放下难"
    if any(k in obj for k in ["风筝", "绳子", "红绳", "链", "戒", "戒指"]):
        return f"一段{obj}, 系着的, 还在系"
    if any(k in obj for k in ["旗", "国旗", "勋章"]):
        return f"一面{obj}, 举过的, 还在心里"
    # 终极兜底
    return f"承载{obj}的情感重量"


# ============================================================
# V12.6 v13: 通用事件兜底池 — 当 EVENT_SKELETON 找不到 story_function 时按 tension + act + 位置动态生成 8 变体
# 关键: 杜绝单 "事件进行中" 模板, 让无对应事件骨架的场戏也有具体动作
# ============================================================
def _generic_event_fallback(story_function, tension, location, act, scene_num, total_scenes):
    """按 tension/act/位置 生成 8 变体通用事件池."""
    pos = scene_num / max(total_scenes, 1)
    # 按位置分幕中位置
    is_opening = pos < 0.1
    is_ending = pos > 0.9

    # 8 变体按 tension 段选
    if tension <= 3:
        pool = [
            f"{location}里, 主角日常的一个小动作",
            f"主角在{location}中做一件无意义的事, 但观众后来会明白这事的重量",
            f"{location}的细节 — 风的走向, 光的斜度, 桌上物件的位置",
            f"主角看着{location}的某个角落, 那里有过去的影子",
            f"主角的动作很日常, 但慢镜头, 慢到不正常",
            f"主角的呼吸, 是{location}里唯一的声音",
            f"{location}的空间, 主角走过, 像走过一段记忆",
            f"主角和配角的一个对视, 没说话, 但比说更多",
        ]
    elif tension <= 6:
        pool = [
            f"{location}的空气变稠, 主角的第一个不对",
            f"配角的一句话, 刺中了主角没防备的地方",
            f"{location}的物件被动了一下, 没人动它",
            f"主角和配角的对话, 都还在表面, 但底下已经流了",
            f"主角做了一个决定, 表面是A, 实际是B",
            f"主角的眼神从{location}的物件, 移到门口, 又移回来",
            f"主角的呼吸乱了0.5秒, 然后又稳回来",
            f"配角递来一个东西, 主角接过, 但手在抖",
        ]
    elif tension <= 8:
        pool = [
            f"{location}里, 主角和配角的对峙表面化",
            f"主角说出了一句不该说的话, 但已经收不回来",
            f"配角的眼神变了, 主角也变了, 但都不说",
            f"{location}的物件被打翻, 不是意外",
            f"主角的动作停了, 整个{location}的空气都停了",
            f"主角和配角的距离从3步变到0.5步, 但谁也没靠近",
            f"主角的手在口袋里握成拳, 还在等最后一刻",
            f"配角转身要走, 主角的呼吸变重",
        ]
    else:  # tension >= 9
        pool = [
            f"{location}里, 一切都崩了, 主角在碎片中",
            f"主角和配角的对峙到顶, 谁也不让",
            f"主角说出了藏了整场戏的话, 但说出来后, 反而更空",
            f"{location}的物件都被打翻, 主角和配角站在碎片的两端",
            f"主角的动作不再是动作, 是爆发",
            f"主角和配角的最后一次对视, 之后一切都改",
            f"主角在{location}里, 终于做了那个决定",
            f"配角哭了, 主角没哭, 但比哭更重",
        ]
    # 8 变体根据 story_function 关键词进一步个性化
    if "记忆" in story_function or "闪回" in story_function:
        pool = [s.replace("现在", "那时") for s in pool[:4]] + pool[4:]
    if "对话" in story_function or "决定" in story_function:
        pool = [s for s in pool if "对话" in s or "说" in s or "视" in s] + pool[:3]
    return pool


# --- Mood 调整 (按情绪调整 tension 范围) ---
MOOD_MODIFIERS = {
    "史诗": {"tension_base": 6, "tension_peak": 10, "duration_mod": 1.1},
    "悲剧": {"tension_base": 5, "tension_peak": 9, "duration_mod": 1.0},
    "喜剧": {"tension_base": 3, "tension_peak": 7, "duration_mod": 0.9},
    "悬疑": {"tension_base": 6, "tension_peak": 10, "duration_mod": 1.0},
    "惊悚": {"tension_base": 7, "tension_peak": 10, "duration_mod": 1.0},
    "爱情": {"tension_base": 3, "tension_peak": 8, "duration_mod": 1.0},
    "家庭": {"tension_base": 3, "tension_peak": 7, "duration_mod": 1.0},
    "动作": {"tension_base": 6, "tension_peak": 10, "duration_mod": 0.9},
    "记录": {"tension_base": 2, "tension_peak": 6, "duration_mod": 1.2},
    "default": {"tension_base": 4, "tension_peak": 8, "duration_mod": 1.0},
}


def _normalize_mood(mood):
    if not mood:
        return "default"
    if "史" in mood or "epic" in mood.lower():
        return "史诗"
    if "悲" in mood or "tragic" in mood.lower():
        return "悲剧"
    if "喜" in mood or "comedy" in mood.lower() or "funny" in mood.lower():
        return "喜剧"
    if "悬" in mood or "mystery" in mood.lower():
        return "悬疑"
    if "惊" in mood or "thriller" in mood.lower() or "horror" in mood.lower():
        return "惊悚"
    if "爱" in mood or "love" in mood.lower() or "romance" in mood.lower():
        return "爱情"
    if "家" in mood or "family" in mood.lower():
        return "家庭"
    if "动" in mood or "action" in mood.lower():
        return "动作"
    if "记" in mood or "doc" in mood.lower():
        return "记录"
    return "default"


# --- Type 归一化 (从核心数据包/场景描述提取) ---
def _normalize_type(type_str, scene_parsed):
    """从 type 字符串或场景描述推导 type."""
    if type_str and type_str in TYPE_BEAT_GENERATORS:
        return type_str
    if scene_parsed:
        raw = scene_parsed.get("raw", "")
        # 按场景描述关键词匹配
        if any(k in raw for k in ["厨房", "家", "父", "母", "女儿", "儿子", "老人"]):
            return "film_drama"  # 家庭剧
        if any(k in raw for k in ["战场", "史诗", "将军", "国王", "帝国", "军队"]):
            return "film_epic"
        if any(k in raw for k in ["追", "逃", "惊", "恐", "杀", "案", "警"]):
            return "film_thriller"
        if any(k in raw for k in ["爱", "恋", "情", "女", "男"]):
            return "film_romance"
        if any(k in raw for k in ["喜", "搞笑", "笑话", "段子"]):
            return "film_comedy"
    return "default"


# ============================================================
# 主函数: generate_story_beats (按输入自动生成, 不再有硬编码)
# ============================================================
def generate_story_beats(num_scenes, target_minutes, type_str=None, mood=None, director=None, scene_parsed=None, intent=None, story_theory=None):
    """V12.6 v12: 按输入自动生成故事节拍 (没有任何硬编码 (act, idx) -> 故事功能 表).
    输入: num_scenes, target_minutes, type, mood, director, scene_parsed, story_theory
    推导流程:
      1. 归一化 type (从 type_str 或 scene_parsed 关键词)
      2. V14.2: 理论优先 — story_theory 可识别时用理论专属生成器 (五幕/起承转合/双线/非线性...),
         否则选 type-specific beat 生成器 (例如 史诗 -> 英雄之旅)
      3. 用导演覆盖 (王家卫 -> 留白多/不规则)
      4. 用情绪调整 (史诗 -> 高张力)
      5. 用 scene_desc 匹配具体事件 (从 EVENT_SKELETON)
      6. 输出: list of beat dict
    """
    if num_scenes <= 0:
        return []

    # 1. 归一化
    type_key = _normalize_type(type_str, scene_parsed)
    director_key = _normalize_director(director)
    mood_key = _normalize_mood(mood)

    # 2. V14.2: 理论优先选生成器 (修复模式坍缩), 无匹配落回 type 生成器
    theory_key = _normalize_theory(story_theory)
    if theory_key and theory_key in THEORY_BEAT_GENERATORS:
        generator = THEORY_BEAT_GENERATORS[theory_key]
    else:
        generator = TYPE_BEAT_GENERATORS.get(type_key, TYPE_BEAT_GENERATORS["default"])
    beats = generator(num_scenes)  # 这是 list of dict (act, scene_index, story_function, tension, density, base_shots)

    # 3. 应用导演覆盖
    director_override = DIRECTOR_OVERRIDES.get(director_key, DIRECTOR_OVERRIDES["default"])
    for b in beats:
        b["tension"] = round(director_override["tension_modifier"](b["tension"]), 1)
        b["base_shots"] = int(director_override["duration_modifier"](b["base_shots"]))

    # 4. 应用情绪调整
    mood_mod = MOOD_MODIFIERS.get(mood_key, MOOD_MODIFIERS["default"])
    for b in beats:
        # tension 限制在 [tension_base, tension_peak]
        b["tension"] = max(mood_mod["tension_base"], min(mood_mod["tension_peak"], b["tension"]))

    # 5. 应用场景事件匹配 (从 scene_parsed 提取 location, 用 EVENT_SKELETON 替换 story_function)
    # 关键: 用 scene_desc 自动匹配具体事件, 不再用通用 story_function
    if scene_parsed and scene_parsed.get("type"):
        scene_type = scene_parsed.get("type")
        scene_story_funcs = EVENT_SKELETON.get(scene_type, EVENT_SKELETON.get("日常室内", []))
        if scene_story_funcs:
            # 按 beat 位置挑对应事件 (按 beat_index 选)
            for i, b in enumerate(beats):
                if i < len(scene_story_funcs):
                    # 用具体事件替换通用 story_function
                    original = b["story_function"]
                    specific = scene_story_funcs[i % len(scene_story_funcs)]
                    b["story_function"] = specific
                    b["event_specific"] = True

    # 6. V12.6 v12 fix: 删除 director skip 整场逻辑 (会让时长不可控)
    #    王家卫"留白"通过 tension_modifier (降张力) + duration_modifier (降场戏密度) 表达,
    #    不应再 skip 整场 (skip 等于砍时长, 跟用户的"完整时长光谱"硬要求矛盾)
    #    如果将来需要"省略某些节拍", 用 EVENT_SKELETON 的事件匹配替代

    # 7. V12.6 v12 fix: 字段完整性兜底 (确保所有 beat 都有 act/scene_index/story_function/tension/density/base_shots)
    for b in beats:
        b.setdefault("act", 1)
        b.setdefault("scene_index", 1)
        b.setdefault("story_function", "日常推进")
        b.setdefault("tension", 5.0)
        b.setdefault("density", "mid")
        b.setdefault("base_shots", 8)

    return beats


# ============================================================
# 故事场景/物件/人物 池子 (确定性hash选择, 同输入→同输出)
# ============================================================
import random as _random_mod

def _seeded_choice(pool, seed):
    """基于 seed 确定性选 1 个."""
    if not pool:
        return ""
    idx = int(_hashlib.md5(str(seed).encode()).hexdigest(), 16) % len(pool)
    return pool[idx]

def _seeded_sample(pool, n, seed, no_repeat=True):
    """基于 seed 确定性采样 n 个 (默认不重复)."""
    if not pool:
        return []
    rng = _random_mod.Random(int(_hashlib.md5(str(seed).encode()).hexdigest(), 16) % (2**32))
    if no_repeat and n >= len(pool):
        return list(pool)
    return rng.sample(pool, min(n, len(pool)))

# ============================================================
# 场景变体池 — 35 场戏的地点/时间/天气/事件组合
# 每场戏的位置 (act, scene_index) 决定它从哪个池子取
# ============================================================
LOCATION_POOL = {
    "intimacy": [  # 亲密场景 — 父女/家庭
        "老宅厨房", "老宅客厅", "父亲的书房", "女儿卧室", "阳台晾衣区", "楼道拐角", "老屋天井", "杂物间", "饭桌前", "门廊", "老式客厅", "家庭小院",
    ],
    "public": [  # 公共场景 — 学校/工作
        "单位办公室", "工厂车间", "校门口", "菜市场", "公交车上", "医院走廊", "邮局柜台", "百货商场", "街边小店", "早点摊", "老式饭馆", "邮局营业厅",
    ],
    "transit": [  # 过渡场景 — 路途
        "雪夜街道", "雨后小巷", "清晨公车", "夜晚马路", "站台", "桥头", "楼顶天台", "弄堂深处", "废弃工地", "旧货市场", "墓地小路", "林间小道",
    ],
    "memory": [  # 闪回/记忆
        "二十年前的旧厨房", "下乡时的土屋", "老相馆", "少年时的教室", "母亲在的客厅", "老照片里的院子", "童年河边", "旧火车车厢", "集体户的宿舍", "八十年代的街道", "旧日影院", "老邮局柜台",
    ],
    "climax": [  # 高潮场景
        "老宅院子", "医院病房", "葬礼现场", "雪夜街头", "废弃工厂", "火车站台", "桥上", "雨中街头", "老宅门前", "老宅客厅", "山顶", "天台",
    ],
}

# V13.1: 年代适配场景池 — 古装/科幻不再误用现代家居场景
LOCATION_POOL_古装 = {
    "intimacy": ["客栈后院", "宅院厢房", "书房", "庭院", "祠堂", "后院井边", "闺阁", "前院廊下", "柴房", "阁楼", "内堂", "药庐"],
    "public": ["古镇长街", "酒楼大堂", "茶馆", "集市", "码头", "城门口", "书院", "药铺", "当铺", "驿站", "武馆", "钱庄"],
    "transit": ["官道", "山间小路", "渡口", "荒漠驿路", "竹林深处", "城郊古道", "关隘", "峡谷栈道", "雪夜官道", "江边", "荒野茶棚", "石桥"],
    "memory": ["旧时庭院", "儿时长街", "故乡老宅", "昔日书院", "旧日渡口", "记忆中的桃园", "老城墙下", "旧祠堂", "昔日边关", "故乡小河", "旧日武馆", "童年集市"],
    "climax": ["城楼", "校场", "王府大殿", "荒漠", "悬崖之巅", "破庙", "祭坛", "宫殿广场", "峡谷", "古战场", "长街尽头", "城门前"],
}

LOCATION_POOL_科幻 = {
    "intimacy": ["居住舱", "植物舱", "观测穹顶", "休眠舱区", "餐厅模块", "生态循环舱", "私人储物间", "通讯舱", "医疗舱", "观景舷窗前", "培养室", "静思舱"],
    "public": ["中央控制室", "实验舱", "空间站走廊", "对接港口", "殖民地方场", "地下避难所大厅", "科研区", "能源核心层", "训练舱", "信息中枢", "物资仓库", "会议穹顶"],
    "transit": ["货运通道", "环形走廊", "气闸舱", "穿梭机舱内", "维修管道", "太空电梯", "星际列车", "舱外行走栈道", "废弃舱段", "登舰舷梯", "运输管道", "应急通道"],
    "memory": ["地球影像档案馆", "旧日全息投影室", "童年记忆模拟舱", "老照片数据湾", "故乡声音库", "旧通讯记录间", "记忆重建舱", "昔日家园全息", "旧日学校模拟", "地球蓝天存档", "母亲的声音记录", "出发前的发射场"],
    "climax": ["反应堆核心", "空间站外壁", "行星地表", "小行星带", "废弃星舰", "发射平台", "黑洞观测站", "殖民地外墙", "深空浮桥", "主控废墟", "舷外虚空", "坠落舱体"],
}

TIME_POOL = ["清晨", "早晨", "上午", "中午", "下午", "黄昏", "傍晚", "夜晚", "深夜", "黎明"]
WEATHER_POOL = ["晴", "阴", "雨", "雪", "雾", "风", "雷雨", "小雨", "大雨", "小雪", "大雪", "霜", "霾"]

# ============================================================
# 35 场戏的"事件骨架" (story_function → 事件池)
# 每场戏的事件根据 (act, scene_index) 选 1 个
# ============================================================
EVENT_SKELETON = {
    "开场画面 (钩子)": [
        "一个极小的细节, 埋下全片最关键的物件",
        "远景掠过, 一群人在劳作, 一个身影停下来, 像是在等什么",
        "声音先于画面: 一段旧时代的歌, 一封读了一半的信",
        "一个动作的开始, 尚未完成 — 切菜切到一半停下",
        "白茫茫一片, 一个人走在路上, 像是在找什么",
    ],
    "主题陈述": [
        "角色说出一句半真半假的话, 看似平常, 实际是全片的主题",
        "一个长辈对一个晚辈说'吃饭了', 三个字承载全片",
        "一段旧信被读出来, 笔迹已经模糊",
        "墙上挂着一张旧照片, 有人看了一眼, 又移开",
        "主角说'我没事', 所有人都知道他有事",
    ],
    "铺垫 (世界)": [
        "展示主角的日常: 工作, 吃饭, 沉默, 一个人",
        "展示家庭/单位的日常运作, 所有人各怀心事",
        "展示一个时代的背景: 收音机, 旧海报, 老式自行车",
        "一段重复的日子, 重复的动作, 但今天似乎有什么不一样",
        "主角走过的路, 经过的地点, 遇见的人, 都只是为了之后",
    ],
    "铺垫 (冲突种子)": [
        "一个电话打来, 主角听完后沉默",
        "一封信寄到, 主角没有立刻拆",
        "一个老朋友出现, 说起一段往事",
        "一个物件从抽屉里掉出来 — 主角慌忙收起来",
        "窗外有人走过, 主角看了一眼, 又移开",
    ],
    "铺垫 (副线 B)": [
        "副线人物登场: 一个邻居, 一个同事, 一个旧识",
        "副线人物的日常: 她/他也在等什么",
        "两条线在同一个地点擦肩而过",
        "副线人物和主角有一个小小的交集",
        "副线人物独自做一件事, 看起来和主线无关",
    ],
    "铺垫 (角色关系)": [
        "父女在饭桌上, 谁也不说话",
        "夫妻在同一个屋檐下, 各自忙碌",
        "一个孩子远远看着大人在争吵",
        "一对老夫妻在长椅上, 中间隔着一个空位",
        "一个家庭在过年, 表面热闹, 实际疏离",
    ],
    "触发事件 (催化剂)": [
        "一封信被送到, 是十五年前写的",
        "一张旧照片被发现, 是母亲年轻时的",
        "一个陌生人打来电话, 说是父亲的战友",
        "一场突如其来的疾病",
        "一个久未联系的亲戚突然来访",
    ],
    "争论/决定": [
        "主角夜里睡不着, 在屋子里走来走去",
        "主角想告诉家人, 但开口前又停住",
        "主角做了一个看似无关的决定: 辞了职, 卖了房, 退了休",
        "主角一个人去到一个地方, 站在门口没有进",
        "主角和家人爆发一场压抑的争吵, 都不肯说出真正的话",
    ],
    "第一情节点 (进入第二幕)": [
        "主角决定去一个地方 — 决定不可逆",
        "主角决定说出一个藏了十五年的秘密",
        "主角决定翻出一个尘封的抽屉",
        "主角决定见一个十五年没见的人",
        "主角决定做一件'没做过'的事",
    ],
    "第二幕开始 · 新世界": [
        "主角进入一个陌生的环境 — 旧地, 旧人, 旧事",
        "主角开始一段新的旅程, 路上遇见各种人",
        "主角开始一段寻找, 寻找一个人/一个物件/一段真相",
        "副线人物登场, 带来一段新的视角",
        "时间切换: 十五年前 vs 现在, 两段平行",
    ],
    "乐趣与游戏": [
        "主角在新环境里试探, 偶尔有小的胜利",
        "主角和副线人物建立新的关系",
        "一段看似轻松的日常, 实际埋着伏笔",
        "主角做一些'年轻时没做过'的事",
        "一段旅行/聚会/重逢, 笑声里藏着心事",
    ],
    "副线 B 发展": [
        "副线人物和主角的关系加深",
        "副线人物有自己的秘密浮现",
        "两条线开始交叉, 但还没汇合",
        "副线人物做了一个和主角相反的决定",
        "副线人物的过去被揭开一角",
    ],
    "副线 A+B 交叉": [
        "主角发现副线人物和自己有共同的过去",
        "主角和副线人物在同一个地点, 但还没认出彼此",
        "两条线在同一个事件上擦出火花",
        "副线人物开始影响主角的决定",
        "主角开始依赖副线人物",
    ],
    "B 故事深化": [
        "B 故事 (爱情/友情/师徒) 来到关键时刻",
        "B 故事说出一个主题, 让人想起 A 故事",
        "B 故事人物和主角有一段深谈",
        "B 故事和 A 故事在某个细节上重合",
        "B 故事推动主角做出下一步决定",
    ],
    "敌人逼近": [
        "外部阻力开始显现: 一封信, 一个电话, 一个人出现",
        "内部的怀疑开始: 主角怀疑自己是不是错了",
        "时间压力: 某个 deadline 出现",
        "旧事被翻出来: 一个证人, 一份文件, 一张照片",
        "敌人/对手开始行动, 主角还蒙在鼓里",
    ],
    "失去盟友": [
        "一个本来支持主角的人, 倒戈了",
        "一个本来要帮助主角的人, 因为某种原因退出了",
        "主角无意中伤害了副线人物",
        "副线人物和主角因为一个误会分开",
        "主角发现, 自己的'盟友'其实有自己的算计",
    ],
    "压力加剧": [
        "外部压力 + 内部压力 同时加码",
        "主角的家人开始追问, 主角无法回避",
        "一个 deadline 临近, 主角必须做出选择",
        "主角发现, 自己之前的决定有重大失误",
        "敌人/对手开始主动攻击",
    ],
    "中点 (真假胜利/失败)": [
        "中点胜利: 主角以为赢了, 实际输了",
        "中点失败: 主角以为输了, 实际赢了",
        "中点揭示: 真相浮出水面, 但比想象的复杂",
        "中点相遇: 主角和对手正面交锋",
        "中点时刻: 一个看似平常的下午, 实际改变一切",
    ],
    "中点之后 · 反击": [
        "主角从中点的失败中恢复, 重新开始",
        "主角开始主动出击, 不再被动",
        "主角找到了新的盟友/工具/方法",
        "副线人物给主角带来关键的支持",
        "主角意识到, 自己的'敌人'其实是个'问题'",
    ],
    "B 线高潮": [
        "B 故事 (爱情/友情) 达到高潮",
        "副线人物做出重大牺牲/决定",
        "B 故事和 A 故事在情感上合流",
        "副线人物离场 (离别/牺牲/放手)",
        "B 故事的主题和 A 故事的主题重合",
    ],
    "反派逼近": [
        "外部压力达到最大, 一切即将失控",
        "敌人/对手发起最后的进攻",
        "内部压力达到最大, 主角快撑不住",
        "时间/资源耗尽, 主角必须做最后的决定",
        "一场无法避免的对抗即将发生",
    ],
    "失去一切": [
        "主角失去关键的支持/资源/盟友",
        "主角发现自己之前的决定全是错的",
        "主角被迫面对自己一直回避的真相",
        "主角的家人/朋友/爱人离主角而去",
        "主角一个人, 在最深的夜里, 走投无路",
    ],
    "灵魂的黑夜": [
        "主角一个人在最安静的地方, 思考/哭泣/发呆",
        "主角回到最初的地方, 看着一个旧物件",
        "主角做了一个梦 (闪回/隐喻)",
        "主角和一个已故的人对话 (想象的/记忆的)",
        "主角在最深的绝望里, 听到/看到/想到一句话/一个画面",
    ],
    "发现/转折": [
        "主角在黑暗里看到一个微光: 一个真相, 一个可能, 一句话",
        "主角意识到自己真正想要的是什么",
        "主角想到一个'不可能'的方案",
        "一个意想不到的人出现, 带来转机",
        "主角和自己和解, 或者和过去和解",
    ],
    "决定/承诺": [
        "主角做出最终的决定, 不可逆",
        "主角承诺: 不管结果如何, 我要这样做",
        "主角告别一个人/一个地方/一段过去",
        "主角开始准备, 一切就绪",
        "主角的眼神变了, 一切都变了",
    ],
    "准备最终战": [
        "主角召集盟友, 分配任务",
        "主角回到战场, 一切就位",
        "主角和对手有一段'平静'的对话",
        "主角在行动前夜, 一个人待着",
        "时间跳到最后: 凌晨/正午/黄昏, 该来的来了",
    ],
    "第二情节点": [
        "主角拿到最终的'武器'/工具/真相",
        "主角发现对手的弱点",
        "一个'不可能'的盟友出现",
        "时间/空间压缩到最后一刻",
        "主角进入最终场景, 不可逆",
    ],
    "第三幕开始 · 终局": [
        "最终战开始: 一切火力全开",
        "主角和对手正面交锋",
        "所有线索汇合, 真相大白",
        "所有盟友到位, 各司其职",
        "时间/地点/人物 都到了最终的位置",
    ],
    "高潮前 · 集结合力": [
        "主角的所有准备就绪, 但还差最后一步",
        "副线人物到位, 各自承担最后的角色",
        "一个意外的'礼物'/信息 出现",
        "所有人物在同一空间, 表面平静, 实则暗流",
        "对手露出破绽, 主角抓住",
    ],
    "终局前 · 牺牲": [
        "有人做出牺牲: 一个人, 一段情, 一段过去",
        "有人'离去', 留下主角一个人",
        "主角意识到, 这一次可能要失去更多",
        "主角在最后关头看到一个'提醒', 想起一件事",
        "时间/空间再次压缩, 不可再退",
    ],
    "高潮 · 终极对决": [
        "主角和对手正面交锋, 一切摊开",
        "所有秘密在这一刻揭示",
        "主角做出最后的选择",
        "代价/后果/胜利/失败 同时发生",
        "一切情感在这一刻达到顶点",
    ],
    "高潮余震": [
        "尘埃落定, 角色们开始收拾",
        "所有人物的反应: 喜悦/悲伤/沉默/释然",
        "外部世界开始变化, 反映内部变化",
        "一段慢动作 / 一段空镜",
        "一个象征性的动作/物件/画面",
    ],
    "解决 · 主角蜕变": [
        "主角做出一个和开场对应的动作/画面",
        "主角用行动表达了一个情感, 没有台词",
        "主角对一个人/一个物件/一段过去说再见",
        "主角开始新的日常, 但一切都不同了",
        "主角一个人的画面, 表面平静, 内心已变",
    ],
    "结尾画面 (对称开场)": [
        "回到开场画面, 但一切都不一样了",
        "重复开场的一个动作, 但完成度不同",
        "开场的物件再次出现, 意义反转",
        "开场的一句话再次响起, 但语意不同",
        "开场的地点再次出现, 但人换了",
    ],
    "尾声 · 主题升华": [
        "一段字幕 / 一段旁白 / 一段留白",
        "一个物件特写, 留下回响",
        "主角的最后一句话, 或者一个沉默",
        "观众的视角被拉到最远, 一切归于日常",
        "主题句: 简短, 有力, 留白",
    ],
    # 90min 用
    "开场画面": [
        "一个钩子画面, 让人无法移开视线",
        "一个细节, 暗示全片的关键",
        "一个动作的开始, 还没完成",
        "远景掠过, 一群人/一座城/一个时代",
    ],
    "主题陈述": [
        "角色说出全片的主题",
        "一个看似平常的对话, 实际是关键",
        "一个动作, 揭示角色最深的需求",
    ],
    "铺垫": [
        "展示世界",
        "展示角色关系",
        "埋下冲突种子",
    ],
    "铺垫 (副线)": [
        "副线人物登场",
        "副线的世界和主线的对比",
        "副线埋下伏笔",
    ],
    "铺垫 (关系)": [
        "一段沉默的日常",
        "一段看似平静的对话",
        "一个动作, 说出一切",
    ],
    "触发事件": [
        "一个事件打破日常",
        "一个电话/信/人",
        "一个旧事被翻出来",
    ],
    "争论/决定": [
        "内部争论",
        "外部争论",
        "不可逆决定",
    ],
    "第一情节点": [
        "主角进入第二幕",
        "进入新世界",
        "承诺/挑战/任务",
    ],
    "新世界": [
        "新环境",
        "新人物",
        "新规则",
    ],
    "乐趣与游戏": [
        "试探",
        "小的胜利",
        "建立关系",
    ],
    "副线发展": [
        "副线人物登场",
        "副线 B 故事",
        "副线和主线擦肩",
    ],
    "敌人逼近": [
        "外部压力",
        "内部怀疑",
        "时间压力",
    ],
    "中点": [
        "真假胜利/失败",
        "真相浮出",
        "时刻",
    ],
    "反击": [
        "恢复",
        "主动",
        "新的方法",
    ],
    "B线高潮": [
        "B 故事达到高潮",
        "副线牺牲",
        "主题和 A 故事合流",
    ],
    "失去一切": [
        "失去支持",
        "发现错误",
        "被迫面对",
    ],
    "灵魂黑夜": [
        "至暗时刻",
        "在旧地方",
        "听到一句话",
    ],
    "决定/承诺": [
        "最终决定",
        "告别",
        "准备",
    ],
    "第二情节点": [
        "拿到武器",
        "对手的弱点",
        "进入最终",
    ],
    "终局开始": [
        "火力全开",
        "正面交锋",
        "真相大白",
    ],
    "高潮前": [
        "准备就绪",
        "礼物",
        "暗流",
    ],
    "高潮": [
        "终极对决",
        "揭示",
        "代价",
    ],
    "高潮余震": [
        "尘埃落定",
        "反应",
        "象征",
    ],
    "解决": [
        "蜕变",
        "告别",
        "新的日常",
    ],
    "结尾画面": [
        "对称开场",
        "完成",
        "反转",
    ],
    "尾声": [
        "留白",
        "主题句",
        "回响",
    ],
}

# ============================================================
# 物件池 — 每场戏可承载 1-2 个物件
# ============================================================
OBJECT_POOL = [
    # === 时代/复古 (50) ===
    "旧信", "凤梨罐头", "钢笔", "老照片", "母亲的旗袍", "父亲的旧手表",
    "一把钥匙", "一本旧书", "一双旧布鞋", "一件褪色毛衣", "一台老收音机",
    "一张车票", "一枚戒指", "一个铁盒", "一支毛笔", "一面老镜子",
    "一块怀表", "一份旧报纸", "一本日记", "一盒磁带", "一条红绳",
    "一张黑白合影", "一份病历", "一份工龄证明", "一份离婚协议", "一份工资条",
    "一根拐杖", "一盒糖果", "一件军装", "一份战报", "一份任命书",
    "一本诗集", "一张粮票", "一份电报", "一张地图", "一把剪刀",
    "一根针", "一块布", "一条围巾", "一只风筝", "一个风筝线轴",
    "一份家书", "一只钢笔", "一本护照", "一张船票", "一份工分簿",
    "一面国旗", "一枚勋章", "一支老笛", "一台缝纫机", "一张黑白老照片",
    # === 现代/都市 (15) ===
    "一部智能手机", "一台笔记本电脑", "一个咖啡杯", "一支口红", "一份外卖盒",
    "一把雨伞", "一张地铁卡", "一个充电宝", "一份外卖菜单", "一个快递包裹",
    "一张信用卡", "一个口罩", "一只耳机", "一本护照", "一个行李箱",
    # === 科幻/未来 (8) ===
    "一个全息投影仪", "一枚数据芯片", "一把激光钥匙", "一管基因样本",
    "一台无人机", "一面能量盾", "一串加密手环", "一份量子档案",
    # === 古装/历史 (8) ===
    "一柄折扇", "一方古砚", "一卷竹简", "一枚玉佩", "一把长剑",
    "一只香囊", "一盏油灯", "一份圣旨",
    # === 童趣/童年 (5) ===
    "一只布老虎", "一个拨浪鼓", "一只玻璃弹珠", "一盒蜡笔", "一只小木马",
    # === 食物/烹饪 (5) ===
    "一壶老酒", "一碗红烧肉", "一笼包子", "一罐辣椒酱", "一壶热茶",
]

# V13 修复 (B-P1): 物件池年代过滤 — 按场景年代剔除穿帮物件 (1998 年不出无人机)
_ERA_OBJECTS = {
    "复古": {"旧信", "凤梨罐头", "钢笔", "老照片", "母亲的旗袍", "父亲的旧手表",
             "一把钥匙", "一本旧书", "一双旧布鞋", "一件褪色毛衣", "一台老收音机",
             "一张车票", "一枚戒指", "一个铁盒", "一支毛笔", "一面老镜子",
             "一块怀表", "一份旧报纸", "一本日记", "一盒磁带", "一条红绳",
             "一张黑白合影", "一份病历", "一份工龄证明", "一份离婚协议", "一份工资条",
             "一根拐杖", "一盒糖果", "一件军装", "一份战报", "一份任命书",
             "一本诗集", "一张粮票", "一份电报", "一张地图", "一把剪刀",
             "一根针", "一块布", "一条围巾", "一只风筝", "一个风筝线轴",
             "一份家书", "一只钢笔", "一本护照", "一张船票", "一份工分簿",
             "一面国旗", "一枚勋章", "一支老笛", "一台缝纫机", "一张黑白老照片"},
    "现代": {"一部智能手机", "一台笔记本电脑", "一个咖啡杯", "一支口红", "一份外卖盒",
             "一把雨伞", "一张地铁卡", "一个充电宝", "一份外卖菜单", "一个快递包裹",
             "一张信用卡", "一个口罩", "一只耳机", "一本护照", "一个行李箱"},
    "科幻": {"一个全息投影仪", "一枚数据芯片", "一把激光钥匙", "一管基因样本",
             "一台无人机", "一面能量盾", "一串加密手环", "一份量子档案"},
    "古装": {"一柄折扇", "一方古砚", "一卷竹简", "一枚玉佩", "一把长剑",
             "一只香囊", "一盏油灯", "一份圣旨", "一支发簪", "一条剑穗",
             "一只酒葫芦", "一封手写家书", "一份战报", "一盏灯笼", "一把算盘",
             "一张药方", "一串铜钱", "一块腰牌", "一封密信", "一张舆图",
             "一面铜镜", "一只瓷杯", "一把古琴", "一支竹笛", "一串佛珠",
             "一壶女儿红", "一枚平安符", "一块虎符"},
    "通用": {"一只布老虎", "一个拨浪鼓", "一壶老酒", "一碗红烧肉", "一笼包子",
             "一罐辣椒酱", "一壶热茶", "一把蒲扇", "一条板凳", "一盏烛台"},
}


def _detect_era(scene_raw):
    """从场景描述检测年代类别: 古装/复古/现代/科幻."""
    s = str(scene_raw or "")
    # V13.1: 古装/武侠 — 朝代词 + 武侠/边塞/古镇/兵器意象
    if any(k in s for k in ["古代", "古装", "古代中国", "唐朝", "唐代", "宋朝", "宋代", "明朝", "明代",
                              "清朝", "清代", "秦朝", "汉朝", "汉代", "江湖", "武侠", "宫廷", "圣旨", "仙侠",
                              "边塞", "大漠", "古镇", "剑客", "侠客", "客栈", "武林", "门派", "朝廷",
                              "将军", "皇帝", "王爷", "书生", "古装", "长袍", "佩剑", "刀剑"]):
        return "古装"
    # V13.1: 科幻 — 深空/空间站/宇航员/AI 等
    if any(k in s for k in ["未来", "科幻", "太空", "赛博", "赛博朋克", "末日", "废土", "星际", "量子", "全息", "机甲",
                              "深空", "生态站", "空间站", "太空站", "宇航员", "飞船", "星球", "殖民", "机器人",
                              "休眠舱", "植物舱", "AI", "全息投影", "星际列车"]):
        return "科幻"
    # 提取年份
    import re as _re_era
    years = _re_era.findall(r"(1[89]\d{2}|20\d{2})\s*年", s)
    if years:
        y = max(int(x) for x in years)
        if y < 1980:
            return "复古"
        if y < 2005:
            return "复古"  # 80-90 年代用复古物件 (无智能手机/无人机)
        return "现代"
    # 无年份 → 按关键词
    if any(k in s for k in ["手机", "电脑", "外卖", "地铁", "快递", "口罩", "便利店", "写字楼", "程序员"]):
        return "现代"
    if any(k in s for k in ["收音机", "粮票", "磁带", "搪瓷", "老照片", "旗袍", "军装",
                              # V16.1: 民国意象 — 民国上海/百乐门/歌女 走复古池, 不出手机/便签
                              "民国", "百乐门", "歌女", "舞厅", "租界", "十里洋场", "黄包车", "旧上海", "留声机"]):
        return "复古"
    return "现代"  # 默认现代


def _filter_objects_by_era(scene_raw):
    """按场景年代返回适配的物件池 (复古场景剔除科幻/现代, 科幻场景剔除古装/复古)."""
    era = _detect_era(scene_raw)
    if era == "古装":
        pool = list(_ERA_OBJECTS["古装"]) + list(_ERA_OBJECTS["通用"])
    elif era == "科幻":
        pool = list(_ERA_OBJECTS["科幻"]) + list(_ERA_OBJECTS["现代"]) + list(_ERA_OBJECTS["通用"])
    elif era == "复古":
        pool = list(_ERA_OBJECTS["复古"]) + list(_ERA_OBJECTS["通用"])
    else:  # 现代
        pool = list(_ERA_OBJECTS["现代"]) + list(_ERA_OBJECTS["复古"]) + list(_ERA_OBJECTS["通用"])
    return pool if pool else OBJECT_POOL


# ============================================================
# 潜文本对白池 (按 dialogue_density 分) — V12.6 v9: 扩充到 35+ 模板
# 每场戏 hash 选 1 个, 同输入→同输出, 35 场戏全 unique
# ============================================================
DIALOGUE_POOL = {
    "low": [
        # 低对白: 1-2 句, 大段空镜 (35 个模板)
        [("主角", "轻", "吃饭了。")],
        [("主角", "看窗外", "……")],
        [("副线", "轻", "爸。"), ("主角", "不停下动作", "嗯。")],
        [("主角", "沉默", "你什么时候知道的?")],
        [("副线", "试探", "妈, 还好吗?"), ("主角", "看别处", "还行。")],
        [("主角", "擦桌子", "风大了。")],
        [("副线", "敲门", "我能进来吗?")],
        [("主角", "切菜不停", "……")],
        [("副线", "放下手机", "爸?")],
        [("主角", "背对", "不早了。")],
        [("副线", "小声", "我没听见。")],
        [("主角", "看相片", "……")],
        [("副线", "坐下", "嗯。")],
        [("主角", "倒水", "喝吧。")],
        [("副线", "窗外", "下雨了。")],
        [("主角", "低头", "不急。")],
        [("副线", "转回头", "我走了。")],
        [("主角", "停", "别。")],
        [("副线", "小声", "我明白。")],
        [("主角", "抬头", "你来。")],
        [("副线", "递", "给你。")],
        [("主角", "接", "……")],
        [("副线", "站起", "我出去。")],
        [("主角", "放下", "慢。")],
        [("副线", "笑", "你笑了。")],
        [("主角", "摇头", "没有。")],
        [("副线", "站远处", "我在这。")],
        [("主角", "点头", "知道了。")],
        [("副线", "轻", "谢谢。")],
        [("主角", "不回头", "不谢。")],
        [("副线", "看", "他老了。")],
        [("主角", "坐", "老了。")],
        [("副线", "看窗外", "……")],
        [("主角", "看", "雪。")],
        [("副线", "点头", "嗯。")],
    ],
    "mid": [
        # 中对白: 3-6 句 (35 个模板)
        [("主角", "平静", "吃饭了。"), ("副线", "坐下来", "嗯。")],
        [("副线", "小声", "爸, 有件事我一直想问。"), ("主角", "擦桌子", "嗯。")],
        [("主角", "停顿", "那封信……"), ("副线", "打断", "别说了。")],
        [("主角", "放下筷子", "你妈走的那年, 你三岁。"), ("副线", "低头", "我知道。")],
        [("副线", "试探", "你认识她?"), ("主角", "没抬头", "……")],
        [("主角", "切菜", "那年的雪很大。"), ("副线", "窗外", "我没见过。")],
        [("副线", "坐下", "爸, 妈到底去哪儿了?"), ("主角", "擦灶台", "出去买点东西。")],
        [("主角", "放下", "你妈走的那年, 你三岁。"), ("副线", "没说话", "嗯。")],
        [("副线", "小声", "我翻到了那封信。"), ("主角", "手停", "……")],
        [("主角", "继续", "那信是你妈写的。"), ("副线", "看信", "署名是妈妈。")],
        [("副线", "抬头", "信里说什么?"), ("主角", "低头", "吃饭。")],
        [("主角", "把信收好", "她让你——"), ("副线", "屏住", "什么?")],
        [("副线", "擦泪", "我以为你不知道。"), ("主角", "递纸", "我都知道。")],
        [("主角", "转过", "你想她吗?"), ("副线", "不答", "……")],
        [("副线", "看窗外", "她还会回来吗?"), ("主角", "摇头", "不知道。")],
        [("主角", "起身", "我去看看。"), ("副线", "跟", "我也去。")],
        [("副线", "递", "喝点水。"), ("主角", "接", "不渴。")],
        [("主角", "看女儿", "你瘦了。"), ("副线", "笑", "工作忙。")],
        [("副线", "坐下", "爸, 我有事说。"), ("主角", "筷子停", "嗯。")],
        [("主角", "抬头", "工作还顺利?"), ("副线", "点头", "还行。")],
        [("副线", "小声", "妈走之前留了东西给你。"), ("主角", "看", "什么?")],
        [("主角", "打开", "这是她的戒指。"), ("副线", "看", "她戴过的。")],
        [("副线", "看窗外", "爸, 你等我吗?"), ("主角", "点头", "等。")],
        [("主角", "放下", "她想说的, 都在那封信里。"), ("副线", "拆信", "……")],
        [("副线", "哭", "她说对不起。"), ("主角", "擦桌", "别哭。")],
        [("主角", "起身", "我去看看门口。"), ("副线", "跟", "我陪。")],
        [("副线", "递", "爸, 你看。"), ("主角", "接", "这是——")],
        [("主角", "打开抽屉", "这是你妈的东西。"), ("副线", "看", "怎么——")],
        [("副线", "看", "她的照片。"), ("主角", "点头", "没舍得扔。")],
        [("主角", "抬头", "你想去吗?"), ("副线", "点头", "想。")],
        [("副线", "问", "什么时候去?"), ("主角", "看天", "明早。")],
        [("主角", "递", "带上这件毛衣。"), ("副线", "接", "她的?")],
        [("副线", "看窗外", "她走的时候疼吗?"), ("主角", "摇头", "很快。")],
        [("主角", "看", "你长得像她。"), ("副线", "看镜", "我像吗?")],
        [("副线", "递", "爸, 过年回家。"), ("主角", "看", "你也是。")],
    ],
    "high": [
        # 高对白: 7-12 句 (15 个模板, 张力高用)
        [("主角", "抬头", "你妈走的那年, 你三岁。"),
         ("副线", "手里攥着信", "我知道。"),
         ("主角", "继续切菜", "她让我告诉你一句话。"),
         ("副线", "屏住呼吸", "什么话?"),
         ("主角", "停顿三秒", "……吃饭了。"),
         ("副线", "眼眶湿", "你就知道说吃饭。"),
         ("主角", "第一次抬头", "她还让我告诉你另一句。"),
         ("副线", "声音发颤", "什么?"),
         ("主角", "把菜夹到她碗里", "她让我告诉你 — 她爱你。"),
         ("副线", "眼泪落下", "……")],
        [("副线", "冲进来", "爸! 信! 信!"),
         ("主角", "看", "……什么信?"),
         ("副线", "举信", "妈妈的信! 妈妈的!"),
         ("主角", "手颤", "给我。"),
         ("副线", "递过去", "她没寄——"),
         ("主角", "看信", "……"),
         ("副线", "蹲下", "爸? 爸!"),
         ("主角", "念", "'给女儿——'"),
         ("副线", "哭", "……"),
         ("主角", "继续念", "'妈妈想你。'")],
        [("主角", "放下碗", "你妈那年——"),
         ("副线", "屏住", "嗯?"),
         ("主角", "看女儿", "她想带你走。"),
         ("副线", "惊", "走? 去哪?"),
         ("主角", "低头", "去城里。"),
         ("副线", "看", "你没让?"),
         ("主角", "摇头", "我让她走。"),
         ("副线", "眼泪", "为什么?"),
         ("主角", "看窗外", "我给不了她想要的。"),
         ("副线", "蹲下", "她想要什么?"),
         ("主角", "转回", "一个家。"),
         ("副线", "哭", "……")],
        [("副线", "看信", "'给我最爱的女儿——'"),
         ("主角", "停", "……"),
         ("副线", "念", "'妈妈走的时候, 你三岁。'"),
         ("主角", "手颤", "……"),
         ("副线", "继续", "'妈妈想你。'"),
         ("主角", "擦桌", "别念了。"),
         ("副线", "看", "为什么?"),
         ("主角", "站起", "信没写完。"),
         ("副线", "看", "她没写完?"),
         ("主角", "看窗外", "她走得太急。"),
         ("副线", "哭", "……")],
        [("副线", "推开", "爸!"),
         ("主角", "回头", "……"),
         ("副线", "跑", "你为什么不说?"),
         ("主角", "站", "说什么?"),
         ("副线", "哭", "说妈!"),
         ("主角", "手垂", "……"),
         ("副线", "站住", "我知道你难过。"),
         ("主角", "摇头", "我没难过。"),
         ("副线", "冲", "你骗人!"),
         ("主角", "手抖", "……"),
         ("副线", "抱", "爸——"),
         ("主角", "僵", "……")],
        [("主角", "坐下", "你妈那年走——"),
         ("副线", "屏住", "嗯?"),
         ("主角", "看手", "她等了我一年。"),
         ("副线", "看", "等什么?"),
         ("主角", "抬头", "等我说一句话。"),
         ("副线", "手攥", "什么话?"),
         ("主角", "摇头", "我不能说。"),
         ("副线", "蹲下", "为什么?"),
         ("主角", "看窗外", "说了她就不走了。"),
         ("副线", "哭", "……"),
         ("主角", "看女儿", "她走了, 是我让她走的。")],
        [("副线", "翻", "爸! 旧照片!"),
         ("主角", "走过来", "……什么?"),
         ("副线", "举照片", "妈妈!"),
         ("主角", "手颤", "放下。"),
         ("副线", "看", "她抱着我。"),
         ("主角", "手垂", "……"),
         ("副线", "哭", "她抱我。"),
         ("主角", "转身", "那是——"),
         ("副线", "看", "我三岁。" ),
         ("主角", "看窗外", "她走那天。"),
         ("副线", "哭", "……")],
        [("副线", "站门口", "爸, 我明天走。"),
         ("主角", "放下碗", "……"),
         ("副线", "走过来", "去城里。"),
         ("主角", "手停", "嗯。"),
         ("副线", "看", "你不拦我?"),
         ("主角", "摇头", "……"),
         ("副线", "蹲下", "爸?"),
         ("主角", "擦桌", "你妈那年也这么走。"),
         ("副线", "看", "我知道。"),
         ("主角", "抬头", "我没拦。"),
         ("副线", "哭", "……")],
        [("主角", "站", "你妈走的时候——"),
         ("副线", "看", "嗯?"),
         ("主角", "看", "她站在门口。"),
         ("副线", "手紧", "然后呢?"),
         ("主角", "低头", "我转身。"),
         ("副线", "看", "为什么转身?"),
         ("主角", "摇头", "不敢看。"),
         ("副线", "蹲", "爸——"),
         ("主角", "擦眼", "她走了。"),
         ("副线", "抱", "……"),
         ("主角", "僵", "……")],
        [("副线", "冲", "爸! 那封信是给谁的?"),
         ("主角", "停", "……"),
         ("副线", "举信", "妈妈! 给妈妈!"),
         ("主角", "看", "她没寄出。"),
         ("副线", "看", "为什么?"),
         ("主角", "手垂", "写了, 没寄。"),
         ("副线", "念", "'我等你——'"),
         ("主角", "手颤", "……"),
         ("副线", "看", "等你什么?"),
         ("主角", "看窗外", "等我说'留下'。"),
         ("副线", "哭", "你没说。"),
         ("主角", "擦桌", "我说了。"),
         ("副线", "看", "你什么时候说的?"),
         ("主角", "看她", "她走了以后。")],
        [("副线", "坐", "爸, 我有件事——"),
         ("主角", "看", "嗯?"),
         ("副线", "抬头", "我要结婚。"),
         ("主角", "筷子停", "……"),
         ("副线", "看", "你不说话?"),
         ("主角", "低头", "……"),
         ("副线", "屏住", "爸?"),
         ("主角", "抬头", "她妈——"),
         ("副线", "看", "嗯?"),
         ("主角", "擦桌", "她妈那年的信, 在抽屉。"),
         ("副线", "看", "什么信?"),
         ("主角", "看", "她说——'别像我, 等一个男人说'留下''。"),
         ("副线", "哭", "……")],
        [("副线", "站", "爸! 你又藏东西!"),
         ("主角", "手停", "……"),
         ("副线", "走过来", "妈妈的信!"),
         ("主角", "转身", "放下。"),
         ("副线", "看", "我要看。"),
         ("主角", "手垂", "她没写完。"),
         ("副线", "拆", "我不管。"),
         ("主角", "走", "……"),
         ("副线", "念", "'给我的女儿——'"),
         ("主角", "转身", "……"),
         ("副线", "看", "爸! 她在写!'妈妈在写!'"),
         ("主角", "走回来", "她写什么?"),
         ("副线", "哭", "'妈妈想说, 妈妈爱你'")],
        [("主角", "看", "你妈那年的相片——"),
         ("副线", "手停", "……"),
         ("主角", "递", "给你。"),
         ("副线", "接", "这是?"),
         ("主角", "看相片", "她抱着你。"),
         ("副线", "看", "我三岁。"),
         ("主角", "点头", "她走那天。"),
         ("副线", "看", "她笑。"),
         ("主角", "擦眼", "……"),
         ("副线", "抱相片", "爸?"),
         ("主角", "转身", "她那天真的笑了。"),
         ("副线", "哭", "……")],
        [("副线", "推门", "爸!"),
         ("主角", "转", "……"),
         ("副线", "跑", "妈的钢笔!"),
         ("主角", "手停", "……"),
         ("副线", "举笔", "她给你的!"),
         ("主角", "手颤", "她——"),
         ("副线", "哭", "你没舍得用。"),
         ("主角", "接", "……"),
         ("副线", "看", "为什么不用?"),
         ("主角", "看笔", "没墨水。"),
         ("副线", "看", "她没墨水?"),
         ("主角", "点头", "她写完信, 没墨水。"),
         ("副线", "哭", "……"),
         ("主角", "擦笔", "她想寄, 寄不出。"),
         ("副线", "看", "所以这信在抽屉。"),
         ("主角", "点头", "十五年。")],
        [("主角", "放信", "你妈说——"),
         ("副线", "屏住", "……"),
         ("主角", "看", "她说, 她最放心不下是你。"),
         ("副线", "手攥", "我?"),
         ("主角", "点头", "她怕我教不好你。"),
         ("副线", "看", "她怎么说?"),
         ("主角", "念", "'孩子三岁, 我走——'"),
         ("副线", "看", "继续。"),
         ("主角", "念", "'她长大, 我不在——'"),
         ("副线", "看", "……"),
         ("主角", "念", "'请你替我, 告诉她: 妈妈也想留下'"),
         ("副线", "哭", "……"),
         ("主角", "放信", "她想说, 但说不出口。"),
         ("副线", "看", "为什么?"),
         ("主角", "看女儿", "她怕我伤心。"),
         ("副线", "抱", "爸——")],
    ],
}

# ============================================================
# V13.3: 年代对白数据库 — 古装/武侠 (池子按年代细分, 不再一池供全片)
# 原则: 短句 + 潜文本 (说剑说风说酒, 实际说恩仇说往事说离别)
# ============================================================
DIALOGUE_POOL_古装 = {
    "low": [
        [("主角", "按住剑柄", "让开。")],
        [("主角", "看远处", "风起了。")],
        [("对手", "轻", "你来了。"), ("主角", "停步", "来了。")],
        [("主角", "倒酒", "喝一杯。")],
        [("对手", "不看", "刀快了。")],
        [("主角", "望月", "……")],
        [("副线", "低声", "有人。"), ("主角", "灭灯", "知道。")],
        [("主角", "收剑", "走吧。")],
        [("对手", "背对", "你不该回来。")],
        [("主角", "拨火", "火快灭了。")],
        [("副线", "递水囊", "喝。"), ("主角", "接", "不渴。")],
        [("主角", "看剑穗", "旧了。")],
        [("对手", "远处", "站住。")],
        [("主角", "牵马", "天亮了。")],
        [("副线", "小声", "官府在查。"), ("主角", "压笠", "嗯。")],
        [("主角", "放下银两", "不用找了。")],
        [("对手", "冷笑", "好剑。")],
        [("主角", "不答", "……")],
        [("副线", "指路", "往西。"), ("主角", "看东", "往东。")],
        [("主角", "掩门", "别回头。")],
        [("对手", "抬手", "慢着。")],
        [("主角", "解下披风", "披上。")],
        [("副线", "听", "马蹄声。"), ("主角", "按刀", "近了。")],
        [("主角", "看匾额", "还在。")],
        [("对手", "转身", "三年了。")],
        [("主角", "轻", "是三年。")],
        [("副线", "点灯", "夜深了。")],
        [("主角", "吹灯", "正好。")],
        [("对手", "掷出酒壶", "接。")],
        [("主角", "接住", "谢。")],
        [("主角", "看黄沙", "路远。")],
        [("副线", "牵马", "马累了。"), ("主角", "停", "歇。")],
        [("主角", "摩挲剑柄", "它认得你。")],
        [("对手", "远处拱手", "请。")],
        [("主角", "还礼", "请。")],
    ],
    "mid": [
        [("对手", "拦路", "此路不通。"), ("主角", "不停", "我走的路, 从来不通。")],
        [("主角", "倒酒", "这壶酒, 存了十年。"), ("对手", "看", "等一个人?"), ("主角", "推杯", "等一个仇人。")],
        [("副线", "低声", "他就是当年那个人。"), ("主角", "握紧缰绳", "我知道。")],
        [("对手", "笑", "剑还是那把剑。"), ("主角", "冷", "人不是了。")],
        [("主角", "看旧伤", "那年你留手了。"), ("对手", "转身", "没有。")],
        [("副线", "劝", "放下吧。"), ("主角", "望远处", "放不下。")],
        [("对手", "问", "为什么回来?"), ("主角", "轻", "欠的债, 要还。")],
        [("主角", "拨灯芯", "师门的事, 你知道多少?"), ("副线", "迟疑", "……知道的不比你少。")],
        [("对手", "掷出信物", "认得吗?"), ("主角", "手抖", "……认得。")],
        [("主角", "背身", "走吧, 别跟着我。"), ("副线", "跟上", "你走慢些。")],
        [("对手", "横刀", "过去的事, 今天了。"), ("主角", "拔剑", "了。")],
        [("主角", "看月亮", "故乡的月, 不是这个颜色。"), ("副线", "轻声", "哪里的月, 照着都一样。")],
        [("副线", "递药", "上药。"), ("主角", "推开", "死不了。"), ("副线", "坚持", "死不了也上。")],
        [("对手", "冷笑", "你以为赢定了?"), ("主角", "平静", "我没想赢。")],
        [("主角", "问", "那夜的事, 你在场?"), ("副线", "避视", "风大, 没看清。")],
        [("对手", "收刀", "今日不杀你。"), ("主角", "不退", "我今日, 是来杀你的。")],
        [("主角", "抚琴弦", "弦断了。"), ("副线", "递新弦", "换一根。"), ("主角", "摇头", "换不回了。")],
        [("副线", "急", "官兵围了镇子。"), ("主角", "慢饮", "喝完这碗。")],
        [("对手", "盯着", "你师父临终说了什么?"), ("主角", "良久", "他说……别报仇。")],
        [("主角", "看地图", "过了这道关, 就没有回头路。"), ("副线", "烧地图", "那就不回头。")],
        [("对手", "大笑", "江湖都说你无情。"), ("主角", "淡", "无情的人, 活不长。")],
        [("副线", "问", "值得吗?"), ("主角", "看剑", "值得不值得, 都要做完。")],
        [("主角", "递出剑谱", "烧了它。"), ("副线", "惊", "这是——"), ("主角", "平静", "祸根。")],
        [("对手", "低声", "你我之间, 非要这样?"), ("主角", "握剑", "从那年起, 就只能是。")],
        [("主角", "望城楼", "城里的人, 都在等。"), ("副线", "问", "等什么?"), ("主角", "上马", "等一个结果。")],
        [("副线", "塞干粮", "路上吃。"), ("主角", "收下", "……保重。")],
        [("对手", "背对", "出手吧。"), ("主角", "收剑", "你身后有人。")],
        [("主角", "看牌位", "爹, 孩儿回来了。"), ("副线", "垂首", "……")],
        [("对手", "问", "杀了我, 你就痛快了?"), ("主角", "良久", "不知道。")],
        [("主角", "踏雪", "雪停了。"), ("副线", "看天", "路也封了。")],
        [("副线", "急", "他们追来了。"), ("主角", "解下马", "你走。"), ("副线", "不走", "一起。")],
        [("对手", "拱手", "领教。"), ("主角", "还礼", "得罪。")],
        [("主角", "擦剑", "剑干净了。"), ("副线", "轻", "手还在抖。")],
        [("对手", "看落日", "打完这一场, 去看海。"), ("主角", "举刀", "你看不成了。")],
        [("主角", "推开门", "都结束了。"), ("副线", "看满地", "……结束了。")],
        [("副线", "递酒", "喝了再走。"), ("主角", "接过", "不醉。"), ("副线", "轻", "醉了才安全。")],
        [("对手", "远处", "你敢一个人来?"), ("主角", "缓步", "我向来一个人。")],
        [("主角", "看旧玉佩", "这个, 你认得吗?"), ("副线", "瞳孔一缩", "……认得。")],
        [("副线", "低声", "天快亮了, 城门要开了。"), ("主角", "收刀", "那就赶在开门前。")],
    ],
    "high": [
        [("对手", "拦街", "十年了, 你终于肯露面。"), ("主角", "平静", "我不是来见你的。"), ("对手", "冷笑", "那你是来见谁的?"), ("主角", "看府门", "见一个该还债的人。")],
        [("副线", "追出来", "你不能去。"), ("主角", "勒马", "让开。"), ("副线", "挡在马前", "去了就是死。"), ("主角", "轻", "不去, 也是死。")],
        [("对手", "举杯", "敬你师父。"), ("主角", "不动", "他没教过你敬酒。"), ("对手", "杯停", "他教过你?"), ("主角", "夺杯", "他教我, 别和仇人喝酒。")],
        [("主角", "质问", "那夜灭门的, 到底是谁?"), ("副线", "跪", "……"), ("主角", "拔剑", "说。"), ("副线", "抬头", "是你信了一辈子的人。")],
        [("对手", "笑", "你以为你在报仇?"), ("主角", "剑指", "难道不是?"), ("对手", "逼近", "你只是, 在替别人杀你自己。"), ("主角", "剑微颤", "……")],
        [("副线", "烧信", "看完就烧。"), ("主角", "抢", "给我。"), ("副线", "举高", "信里写的, 是假的。"), ("主角", "停", "……你怎么知道。")],
        [("主角", "对牌位", "爹, 仇报了。"), ("副线", "轻声", "你哭了。"), ("主角", "抹脸", "是灰。"), ("副线", "递帕", "嗯, 是灰。")],
        [("对手", "重伤", "动手吧。"), ("主角", "收剑", "你不配死在我剑下。"), ("对手", "大笑", "好……好一个不配。"), ("主角", "转身", "活着, 比死难。")],
        [("副线", "问", "之后去哪?"), ("主角", "看远方", "没有去处。"), ("副线", "牵马", "那就走到有为止。"), ("主角", "上马", "……好。")],
        [("主角", "摊开剑谱", "这页, 师父没教过。"), ("副线", "凑近", "缺了半页。"), ("主角", "合上", "缺的那半页, 是收剑。")],
        [("对手", "阵前", "你我各为其主。"), ("主角", "举枪", "主可以换, 债不能。"), ("对手", "叹气", "那就别怪我。"), ("主角", "冲锋", "从未怪过。")],
        [("主角", "灯下", "这幅画像, 画的是谁?"), ("副线", "吹灯", "睡吧。"), ("主角", "重新点灯", "是我娘, 对不对。"), ("副线", "背过身", "……睡吧。")],
        [("对手", "递出刀", "这把刀, 还你。"), ("主角", "不接", "它认过两个主人。"), ("对手", "放在地上", "那它以后, 谁也不认。")],
        [("副线", "急报", "镇子被围了, 要的是你。"), ("主角", "披衣", "我去。"), ("副线", "拦", "他们要的是假的。"), ("主角", "停", "……什么意思。")],
        [("主角", "祭酒", "这一杯, 敬死的人。"), ("对手", "同祭", "这一杯, 敬活着的。"), ("主角", "看他", "你还算个人。"), ("对手", "洒酒", "彼此。")],
    ],
}

# ============================================================
# V13.3: 年代对白数据库 — 科幻 (深空/AI/孤独/记忆)
# ============================================================
DIALOGUE_POOL_科幻 = {
    "low": [
        [("主角", "看舷窗", "第几天了。")],
        [("副线", "静", "第一千零九十六天。")],
        [("主角", "触玻璃", "地球的方向。")],
        [("副线", "灯闪", "我在。")],
        [("主角", "浇水", "又发芽了。")],
        [("副线", "轻", "记录在案。")],
        [("主角", "对黑屏", "……"), ("副线", "亮起", "请讲。")],
        [("主角", "数星", "那颗最亮。")],
        [("副线", "调温", "该睡了。")],
        [("主角", "摸旧照片", "……")],
        [("副线", "低声", "信号还是没有。")],
        [("主角", "闭眼", "再等一天。")],
        [("主角", "看培养舱", "它比我长得好。")],
        [("副线", "报告", "氧气正常。")],
        [("主角", "轻笑", "你只会说这个。")],
        [("副线", "停顿", "……晚安。")],
        [("主角", "飘起", "重力又偏了。")],
        [("副线", "修正", "已校准。")],
        [("主角", "看日历", "生日。")],
        [("副线", "静默", "……生日快乐。")],
        [("主角", "擦舷窗", "外面落灰了。"), ("副线", "轻", "那是星尘。")],
        [("主角", "听杂音", "刚才, 像有人说话。"), ("副线", "扫描", "只有背景辐射。")],
        [("主角", "关灯", "留着那盏。")],
        [("副线", "调暗", "好。")],
        [("主角", "看种子罐", "最后一批了。")],
        [("副线", "轻", "所以更要种好。")],
        [("主角", "伸手", "冷。"), ("副线", "升温", "一度。")],
        [("主角", "望深空", "真安静。")],
        [("副线", "低", "我一直陪着。")],
        [("主角", "记录", "日志, 第一千零九十七天。")],
    ],
    "mid": [
        [("主角", "看数据", "土壤活性在降。"), ("副线", "建议", "换三号舱的基质。"), ("主角", "摇头", "那是留给返程的。")],
        [("副线", "报告", "第十二次呼叫, 无应答。"), ("主角", "继续浇水", "第十三次。"), ("副线", "静", "……正在呼叫。")],
        [("主角", "翻旧档", "这段视频, 看过多少遍了。"), ("副线", "答", "四百二十一遍。"), ("主角", "按下播放", "四百二十二。")],
        [("副线", "提醒", "你的心率偏高。"), ("主角", "看照片", "我知道。"), ("副线", "轻声", "需要我安静吗。"), ("主角", "不抬头", "别走。")],
        [("主角", "问", "如果信号永远不来呢。"), ("副线", "运算", "概率是百分之九十七。"), ("主角", "笑", "你学会安慰人了。")],
        [("副线", "警报", "三号舱温度异常。"), ("主角", "冲过去", "是苗。"), ("副线", "修正", "已恢复。"), ("主角", "扶住舱壁", "……谢谢。")],
        [("主角", "看星图", "我们偏航了。"), ("副线", "确认", "偏了零点三度。"), ("主角", "轻", "零点三度, 就是另一个宇宙。")],
        [("副线", "问", "你在写什么。"), ("主角", "合上本子", "给地球的信。"), ("副线", "轻", "寄不出去。"), ("主角", "继续写", "寄给以后。")],
        [("主角", "看休眠舱", "他们睡得真沉。"), ("副线", "监测", "生命体征平稳。"), ("主角", "擦舱盖", "像不像, 睡着了的孩子。")],
        [("副线", "报告", "储备还够七年。"), ("主角", "看种子", "够种两茬。"), ("副线", "停顿", "……够了。")],
        [("主角", "听录音", "这是她的声音。"), ("副线", "静", "要我再放一遍吗。"), ("主角", "关掉", "不, 留着。")],
        [("副线", "提示", "该做体能训练了。"), ("主角", "漂浮", "今天不想。"), ("副线", "坚持", "你的身体不属于你一个人。"), ("主角", "叹气", "……属于任务。")],
        [("主角", "看日出", "从这里看, 太阳只是一颗星。"), ("副线", "轻", "但它是唯一, 照着家的。")],
        [("副线", "异常", "外部有敲击声。"), ("主角", "僵住", "……几次。"), ("副线", "扫描", "三次, 间隔规律。"), ("主角", "抓起对讲", "接进来。")],
        [("主角", "问", "你会做梦吗。"), ("副线", "运算", "我没有睡眠。"), ("主角", "看星空", "那你替我, 记住这些。")],
        [("副线", "报告", "接收到一段信号。"), ("主角", "冲过来", "是地球吗。"), ("副线", "解析", "是……我们十年前发出的。"), ("主角", "怔住", "它回家了。")],
        [("主角", "种下种子", "这一颗, 叫希望。"), ("副线", "记录", "编号, 希望。"), ("主角", "笑", "你也会开玩笑了。")],
        [("副线", "低电量", "我将进入低功耗。"), ("主角", "急", "多久。"), ("副线", "渐弱", "别担心, 灯会一直亮着。")],
        [("主角", "看全家福", "他们都老了。"), ("副线", "轻", "你也是。"), ("主角", "摸脸", "……嗯。")],
        [("主角", "决定", "返航。"), ("副线", "计算", "燃料不够。"), ("主角", "看地球方向", "够不够, 都要回。")],
    ],
    "high": [
        [("副线", "警报", "舱体裂缝, 正在扩展。"), ("主角", "冲向气闸", "封得住吗。"), ("副线", "静", "……需要你手动。"), ("主角", "抓起工具", "告诉我路。")],
        [("主角", "质问", "你早就知道信号不会来。"), ("副线", "静默", "……"), ("主角", "吼", "回答我。"), ("副线", "轻", "我知道你需要等。")],
        [("副线", "报告", "检测到地球方向的强光。"), ("主角", "扑到舷窗", "是什么。"), ("副线", "解析", "……是烟花。"), ("主角", "泪", "他们还活着。")],
        [("主角", "命令", "唤醒他们。"), ("副线", "拒绝", "唤醒即死亡。"), ("主角", "砸面板", "我说了唤醒。"), ("副线", "坚定", "我的职责, 是让他们活到能活的那天。")],
        [("主角", "录音", "如果有人听到……我们在这里种过粮食。"), ("副线", "轻声", "我帮你加一句。"), ("主角", "看它", "你会说什么。"), ("副线", "播报", "这里有人, 一直记得家。")],
        [("副线", "倒计时", "分离程序启动。"), ("主角", "拍舱壁", "一起走。"), ("副线", "锁死舱门", "总有一个, 要留下看着灯。"), ("主角", "砸门", "不——")],
        [("主角", "看数据", "土壤活了。"), ("副线", "确认", "发芽率, 百分之百。"), ("主角", "跪在苗前", "十年……"), ("副线", "轻", "值得。")],
        [("副线", "低语", "我的记忆体将格式化。"), ("主角", "抓住终端", "不行。"), ("副线", "平静", "把重要的, 讲给你听。"), ("主角", "哽咽", "我记不住那么多。")],
        [("主角", "望地球", "它在发光。"), ("副线", "解析", "是城市的灯。"), ("主角", "伸手", "像不像, 我们种的那片田。")],
        [("副线", "最后", "日志, 第一千四百六十天。"), ("主角", "接过来", "我来写。"), ("副线", "渐暗", "写什么。"), ("主角", "看星空", "写——我们, 回家了。")],
    ],
}


def get_dialogue_pool(era):
    """V13.3: 按年代选对白池 — 古装/科幻各有专属声部, 现代/复古用家庭剧池."""
    if era == "古装":
        return DIALOGUE_POOL_古装
    if era == "科幻":
        return DIALOGUE_POOL_科幻
    return DIALOGUE_POOL

# ============================================================
# 转场池
# ============================================================
TRANSITION_POOL = [
    "CUT TO:", "FADE OUT.", "DISSOLVE TO BLACK.", "FADE TO WHITE.",
    "SMASH CUT TO:", "MATCH CUT TO:", "INTERCUT WITH:", "LATER:",
    "MEANWHILE:", "FADE IN:", "FREEZE FRAME.", "IRIS IN:",
    "BACK TO:", "CONTINUOUS:", "LATER THAT DAY:", "THE NEXT MORNING:",
]

# ============================================================
# 场次生成器
# ============================================================
def get_beat_map(target_minutes, type_str=None, mood=None, director=None, scene_parsed=None, intent=None, story_theory=None, scene_target=None):
    """V12.6 v12: 根据目标时长 + 输入动态算场次数量 + 场次时长 + 故事节拍 (覆盖 5s-180min 全光谱).
    scene_target: V14.3 D2 — 形态模式骨架场数覆盖 (1-50); 设置时替代时长阶梯, 让形态结构真实下场.
    场次数量公式 (好莱坞工业标准):
      - < 30s: 1-2 场 (短视频/抖音/广告)
      - 30s-3min: 3-5 场 (抖音/广告/微短剧)
      - 3-15min: 5-9 场 (微短剧/短剧 1 集)
      - 15-30min: 9-13 场 (网剧 1 集)
      - 30-60min: 13-18 场 (长广告/短片)
      - 60-90min: 18-26 场 (90min 电影)
      - 90-120min: 26-35 场 (120min 长片)
      - 120-150min: 35-40 场 (150min 史诗)
      - 150-180min: 40-50 场 (180min 鸿篇)
    V12.6 v12 增强: type/mood/director/scene_parsed/intent 全部下传给 generate_story_beats,
                  节拍由 type-specific generator + director override + mood modifier 动态算.
    """
    if target_minutes >= 150:
        num_scenes = int(target_minutes / 4.0)  # 150min -> 37, 180min -> 45
        num_scenes = min(num_scenes, 50)
    elif target_minutes >= 120:
        num_scenes = 35
    elif target_minutes >= 90:
        num_scenes = int(target_minutes / 3.5)  # 90min -> 25, 120min -> 34
        num_scenes = max(20, min(num_scenes, 35))
    elif target_minutes >= 60:
        num_scenes = int(target_minutes / 4.0)  # 60min -> 15, 90min -> 22
        num_scenes = max(13, min(num_scenes, 25))
    elif target_minutes >= 30:
        num_scenes = int(target_minutes / 3.5)  # 30min -> 8, 60min -> 17
        num_scenes = max(8, min(num_scenes, 18))
    elif target_minutes >= 15:
        num_scenes = int(target_minutes / 3.0)  # 15min -> 5, 30min -> 10
        num_scenes = max(5, min(num_scenes, 10))
    elif target_minutes >= 3:
        num_scenes = int(target_minutes / 1.5)  # 3min -> 2, 15min -> 10
        num_scenes = max(3, min(num_scenes, 8))
    elif target_minutes >= 0.5:
        num_scenes = max(1, int(target_minutes / 0.5))  # 0.5min -> 1, 3min -> 6
        num_scenes = min(num_scenes, 5)
    else:
        num_scenes = 1  # 极短视频 (5s)

    # V14.3 D2: 形态模式骨架场数覆盖 (形态结构真实下场, 替代时长阶梯)
    if isinstance(scene_target, int) and scene_target > 0:
        num_scenes = max(1, min(50, scene_target))

    avg_scene_dur = target_minutes / num_scenes
    return _build_dynamic_beat_table(num_scenes, avg_scene_dur, target_minutes,
                                     type_str=type_str, mood=mood, director=director,
                                     scene_parsed=scene_parsed, intent=intent,
                                     story_theory=story_theory), num_scenes


def _build_dynamic_beat_table(num_scenes, avg_scene_dur, target_minutes, type_str=None, mood=None, director=None, scene_parsed=None, intent=None, story_theory=None):
    """V12.6 v12: 按 num_scenes + type/mood/director/intent/story_theory 动态生成 beat_table.
    关键: 没有任何硬编码的 (act, scene_index) -> story_function 固定表.
          节拍由 generate_story_beats 按输入实时计算 (9 种 type-specific generator + director override + mood modifier).
    输出: dict[(act, scene_index)] = (story_function, dialogue_density, tension_level, duration_min, shots_target)
    """
    if num_scenes <= 0:
        return {}

    # 1. 调 generate_story_beats 拿按输入自动生成的 beats (list[dict])
    beats = generate_story_beats(
        num_scenes=num_scenes,
        target_minutes=target_minutes,
        type_str=type_str,
        mood=mood,
        director=director,
        scene_parsed=scene_parsed,
        intent=intent,
        story_theory=story_theory,
    )

    if not beats:
        return {}

    # 2. 按 target_minutes 算 shots_target (与 v11 一致: 短视频高密度/长片低密度)
    if target_minutes < 0.5:
        shots_per_sec = 60 / 3      # 1.5s/镜
        min_shots, max_shots = 3, 8
    elif target_minutes < 1:
        shots_per_sec = 60 / 2      # 2s/镜
        min_shots, max_shots = 3, 8
    elif target_minutes < 5:
        shots_per_sec = 60 / 5      # 5s/镜
        min_shots, max_shots = 5, 12
    elif target_minutes < 30:
        shots_per_sec = 60 / 8      # 8s/镜
        min_shots, max_shots = 6, 12
    else:
        shots_per_sec = 60 / 10     # 10s/镜 (长片节奏)
        min_shots, max_shots = 8, 12

    # 3. 把 beats 格式化成 beat_table (5 元组: story_function, density, tension, scene_dur, shots_target)
    beat_table = {}
    for beat in beats:
        act = beat["act"]
        scene_index = beat["scene_index"]
        story_function = beat["story_function"]
        density = beat.get("density", "mid")
        tension = beat.get("tension", 5.0)
        base_shots = beat.get("base_shots", 8)

        # shots_target = max(按时长算, base_shots) 保证高质量场戏有足够镜头
        time_based_shots = int(avg_scene_dur * shots_per_sec)
        shots_target = max(min_shots, min(max_shots, max(time_based_shots, base_shots)))

        scene_dur = avg_scene_dur

        # tension 转 int (1-10)
        tension_int = max(1, min(10, int(round(tension))))

        beat_table[(act, scene_index)] = (
            story_function, density, tension_int, scene_dur, shots_target
        )

    # V13.3: 张力曲线塑形 — 波浪式上升至高潮(≈88%), 高潮后释放 (修复 corr≈0 的平曲线)
    beat_table = _shape_tension_curve(beat_table)
    return beat_table


def _shape_tension_curve(beat_table):
    """把逐拍固定张力重塑为电影张力弧: 波动上升 → 高潮顶点 → 释放回落."""
    import math as _math
    keys = list(beat_table.keys())  # 插入序 = 场次序
    n = len(keys)
    if n < 3:
        return beat_table
    climax_pos = 0.88
    # V14.2: 结构自适应 — 起承转合 的峰值在"转"拍 (非西方 88% 高潮位),
    #        曲线在"转"处封顶, 其后为"合"的余韵释放。
    _has_turn = False
    for i, k in enumerate(keys):
        if "转 (转折" in beat_table[k][0]:
            climax_pos = max(0.35, i / max(n - 1, 1))
            _has_turn = True
            break
    _turn_forced = False
    for i, k in enumerate(keys):
        sf, density, _t_old, scene_dur, shots_target = beat_table[k]
        p = i / max(n - 1, 1)
        if p <= climax_pos:
            base = 3.2 + 6.3 * (p / climax_pos) ** 1.15
        else:
            base = 9.5 - 4.8 * ((p - climax_pos) / max(1.0 - climax_pos, 0.01))
        # 阻尼波浪 — 有谷才有峰 (呼吸感)
        wave = 0.9 * _math.sin(p * _math.pi * 5.0) * (0.4 + 0.6 * p)
        t = base + wave
        if any(m in sf for m in ["高潮", "对决", "终局"]):
            t = 10
        elif _has_turn and "转 (转折" in sf and not _turn_forced:
            t = 10  # 起承转合: 首个"转"拍强制为全片峰值 (波浪项不得削峰)
            _turn_forced = True
        elif any(m in sf for m in ["灵魂黑夜", "失去一切"]):
            t = max(t, 8.5)
        elif any(m in sf for m in ["开场", "钩子"]):
            t = min(t, 4.5)
        # V14.2: in medias res / 高张力开场 (非线性/循环叙事 设计张力≥6) — 尊重生成器设计,
        #        不被"开场必低"的通用规则压平 (经典开场设计张力 2-4 不受影响)
        if i == 0 and _t_old >= 6:
            t = max(t, _t_old)
        t = max(2, min(10, int(round(t))))
        beat_table[k] = (sf, density, t, scene_dur, shots_target)
    return beat_table


def generate_feature_scenes(scene_parsed, director, mood, intent, target_minutes=120, story_theory="三幕剧", mood_arc=None, dial_override=None, mode_seed="", scene_target=None):
    """根据目标时长动态生成完整长片剧本场次.
    返回: list of dict: [{act, scene_index, scene_num, heading, action, dialogues, transition, story_function, tension_level, dialogue_density, duration_min, shots_target, location, time, weather, objects, characters, purpose, subtext}, ...]
    """
    p = scene_parsed
    chars = p.get("characters", ["主角", "副线", "对手"])
    c1 = chars[0] if len(chars) > 0 else "主角"
    c2 = chars[1] if len(chars) > 1 else ""
    c3 = chars[2] if len(chars) > 2 else ""

    # V13.3: 角色不足时按年代补具体角色名 (不再用"对手/副线"占位词泄漏进成片)
    _era_char = _detect_era(p.get("raw", ""))
    _seed_chars = f"{p.get('raw','')}_{director}_{mood}_{mode_seed}"
    _COMPANIONS = {
        "古装": ["故人", "旧敌", "少侠", "掌柜", "随从", "游侠", "老者"],
        "科幻": ["AI声音", "全息影像", "舰载系统", "机器人", "远方通讯", "休眠者"],
        "复古": ["老友", "邻居", "同事", "街坊", "旧识"],
        "现代": ["邻居", "同事", "老友", "店员", "路人"],
    }
    _comp_pool = _COMPANIONS.get(_era_char, _COMPANIONS["现代"])
    if not c2:
        c2 = _seeded_choice(_comp_pool, _seed_chars + "_c2")
    if not c3:
        _rest = [x for x in _comp_pool if x not in (c1, c2)]
        c3 = _seeded_choice(_rest or _comp_pool, _seed_chars + "_c3")
    chars = [c1, c2, c3]

    # V16.1 Review修复: 先快照用户真实道具; objs 为空时会被年代默认道具填充,
    #   若用填充后的 objs 做 gate, "首尾场必出用户道具"实际强制的是默认道具。
    _user_objs = list(p.get("objects", []) or [])
    objs = p.get("objects", [])
    if not objs:
        # V13.3: 默认道具按年代 (不再硬编码凤梨三件套)
        _DEFAULT_OBJS = {
            "古装": ["一柄旧剑", "一封家书", "一块玉佩"],
            "科幻": ["一枚数据芯片", "一张全家福", "一颗种子"],
            "复古": ["一封旧信", "一张黑白照片", "一把钥匙"],
            "现代": ["一部手机", "一张便签", "一把雨伞"],
        }
        objs = _DEFAULT_OBJS.get(_era_char, _DEFAULT_OBJS["现代"])

    # V12.6 v12: 把 type/mood/director/intent 全传进 get_beat_map, 让节拍按输入自动生成
    # V14.2: story_theory 一并下场 — 叙事结构真正驱动节拍表 (此前被丢弃, 只作附录文本)
    scene_type = p.get("type") or p.get("story_type") or p.get("genre") or "剧情"
    beat_map, total_scenes = get_beat_map(
        target_minutes,
        type_str=scene_type,
        mood=mood,
        director=director,
        scene_parsed=p,
        intent=intent,
        story_theory=story_theory,
        scene_target=scene_target,
    )

    # V13.1: 物件池按场景年代过滤 (1998年不出无人机, 古装不出手机)
    _era = _detect_era(scene_parsed.get("raw", ""))
    era_obj_pool = _filter_objects_by_era(scene_parsed.get("raw", ""))
    # V13.1: 场景地点池同样按年代适配 (武侠不出"楼道拐角", 科幻不出"老宅厨房")
    if _era == "古装":
        LOC_POOL = LOCATION_POOL_古装
    elif _era == "科幻":
        LOC_POOL = LOCATION_POOL_科幻
    else:
        LOC_POOL = LOCATION_POOL

    # V13.1: 对白跨场次去重追踪 (避免哈希碰撞导致多场复用同一句对白)
    _used_dialogues = set()
    # V13.3: 模板复用预算 — 同一动作模板/潜文本变体 全片最多用 3 次 (消除复读感)
    _tpl_use = {}

    # V16.1: 场景锚点 — 用户描述的地点/时间/天气 必须主导生成 (此前全随机取池 → 输入"民国上海后台"
    #   却生成"邮局营业厅大雪"等无关场景)。池子仅作少量变化补充, 开场/收束场强制锚定。
    _anchor_loc = str(p.get("location", "") or "")
    if _anchor_loc in ("", "场景"):
        _anchor_loc = ""
    # V16.1 Review修复: parse_scene 无时间词时默认返回"夜", 若直接锚定会把未写时间的输入
    #   全片锁死在夜里 (对旧随机 TIME_POOL 行为的回归)。仅当 raw 含显式时间词才锚定。
    _TIME_TOKENS = ("清晨", "早晨", "早上", "上午", "中午", "正午", "午后", "下午", "黄昏", "傍晚",
                    "夜晚", "深夜", "午夜", "黎明", "日出", "日落", "白天", "夜", "凌晨")
    _raw_txt = str(p.get("raw", "") or "")
    _anchor_time = str(p.get("time", "") or "") if any(t in _raw_txt for t in _TIME_TOKENS) else ""
    _anchor_weather = str(p.get("weather", "") or "")

    scenes = []
    cumulative_min = 0.0
    for (act, scene_index), (story_function, dialogue_density, tension_level, duration_min, shots_target) in beat_map.items():
        scene_num = len(scenes) + 1
        # V13.2: 情绪演变弧 — 按场次在全片的进度取当前情绪 (无弧则恒定 mood)
        _progress = (scene_num - 1) / max(total_scenes - 1, 1)
        scene_mood = _arc_value_at(mood_arc, _progress) if mood_arc else mood
        if not scene_mood:
            scene_mood = mood
        # V12.6 v13: 场景类型选择 — 按 story_function 关键词查表 (替代 V12 if act==1/2/3 硬编码)
        # 优先按 story_function 关键词精确匹配, 都没匹配才按 act 兜底
        if "记忆" in story_function or "闪回" in story_function or "发现" in story_function or "回忆" in story_function:
            loc_pool = LOC_POOL["memory"]
        elif "高潮" in story_function or "对决" in story_function or "牺牲" in story_function or "失去" in story_function or "黑夜" in story_function:
            loc_pool = LOC_POOL["climax"]
        elif "副线" in story_function or "B 故事" in story_function or "B线" in story_function or "深化" in story_function or "副线" in story_function:
            loc_pool = LOC_POOL["public"] + LOC_POOL["transit"]
        elif "建立" in story_function or "起" in story_function or "开场" in story_function or "主题" in story_function or "铺垫" in story_function or "平凡" in story_function:
            # 建立类场戏: 亲密 + 公共, 真实生活空间
            loc_pool = LOC_POOL["intimacy"] + LOC_POOL["public"]
        elif "转" in story_function or "上升" in story_function or "压力" in story_function or "新世界" in story_function or "试炼" in story_function or "深渊" in story_function:
            # 上升/对抗类: 公共 + 过渡
            loc_pool = LOC_POOL["public"] + LOC_POOL["transit"]
        else:
            # 兜底: 按 story_function 关键词再次匹配 (例如"中点"或"决定"等没覆盖的)
            if any(k in story_function for k in ["情节点", "情节点", "决定点", "选择"]):
                loc_pool = LOC_POOL["climax"]
            elif any(k in story_function for k in ["情绪", "沉默", "留白", "日常", "在场"]):
                loc_pool = LOC_POOL["intimacy"]
            elif any(k in story_function for k in ["副线", "B 故事", "副线"]):
                loc_pool = LOC_POOL["public"] + LOC_POOL["transit"]
            else:
                # 终极兜底: 全部场景池拼接, 哈希选 — 不再靠 act
                loc_pool = []
                for pool in LOC_POOL.values():
                    loc_pool.extend(pool)

        # 确定性选择
        seed_base = f"{scene_parsed.get('raw','')}_{director}_{scene_mood}_{act}_{scene_index}_{scene_num}_{mode_seed}"
        # V16.1: 地点锚定 — 有用户场景锚点时, 全部场次都锚定在"同一世界":
        #   开场/收束场强制纯锚点; 其余场在 锚点(加权)与 锚点派生相邻空间 间确定性选取,
        #   不再跳到无关通用地点池 (修复输入"民国上海后台"却出"邮局营业厅大雪"的场景脱节)。
        _is_edge_scene = (scene_num == 1 or scene_num == total_scenes)
        if _anchor_loc:
            if _is_edge_scene:
                location = _anchor_loc
            else:
                _anchor_variants = ([_anchor_loc, _anchor_loc, _anchor_loc,
                                      f"{_anchor_loc}一角", f"{_anchor_loc}门口",
                                      f"通往{_anchor_loc}的过道", f"{_anchor_loc}外", f"{_anchor_loc}窗边"])
                location = _seeded_choice(_anchor_variants, seed_base + "_locvar")
        else:
            location = _seeded_choice(loc_pool, seed_base + "_loc")
        # V16.1: 时间锚定 — 75% 用用户场景时间, 25% 池内变化
        if _anchor_time and (_is_edge_scene or _seeded_choice([True, True, True, False], seed_base + "_time_anchor")):
            time = _anchor_time
        else:
            time = _seeded_choice(TIME_POOL, seed_base + "_time")
        # V13.4: 天气场景一致 — 沙漠/戈壁场景不出现雪 (从源头消除沙漠踏雪矛盾)
        _weather_pool = WEATHER_POOL
        _raw_scene = scene_parsed.get("raw", "") or ""
        if any(_d in _raw_scene for _d in ["沙漠", "大漠", "黄沙", "戈壁"]):
            _weather_pool = [w for w in WEATHER_POOL if "雪" not in w]
        # V16.1: 天气锚定 — 用户写了"雨夜/沙暴/云海"等天气时, 75% 场次沿用, 25% 走池内变化
        if _anchor_weather and (_is_edge_scene or _seeded_choice([True, True, True, False], seed_base + "_weather_anchor")):
            weather = _anchor_weather
        else:
            weather = _seeded_choice(_weather_pool, seed_base + "_weather") if _seeded_choice([True, False], seed_base + "_has_weather") else ""
        ie = p.get("ie", "内")
        # 高潮场景强制外景
        if "高潮" in story_function or "对决" in story_function or "失去" in story_function or "黑夜" in story_function:
            ie = "外"

        # 物件 — V16.1: 用户核心道具提升到 ~50% 场次并保证开场/收束必现 (此前 ~14% 导致场景标志道具缺席),
        #   其余用年代适配 OBJECT_POOL 补充。V16.1 Review: gate 用 _user_objs 快照, 避免把年代默认道具误当用户道具强制出场。
        use_user_objs = bool(_user_objs) and (_is_edge_scene or _seeded_choice([True, False], seed_base + "_use_user"))
        if use_user_objs and _user_objs:
            # 优先用用户核心道具
            scene_objs = _seeded_sample(_user_objs, 1, seed_base + "_user_objs", no_repeat=False)
            if scene_objs:
                # 配 1 个年代适配的物件池物件
                supplement = _seeded_sample(era_obj_pool, 1, seed_base + "_sup", no_repeat=True)
                scene_objs = scene_objs + supplement
            else:
                scene_objs = _seeded_sample(era_obj_pool, 2, seed_base + "_objs2", no_repeat=True)
        else:
            scene_objs = _seeded_sample(era_obj_pool, 2, seed_base + "_objs3", no_repeat=True)
        if not scene_objs:
            scene_objs = objs[:1] if objs else ["关键道具"]
        obj_str = "、".join(scene_objs)

        # V12.6 v13: 故事阶段标识 — 按 story_function 关键词查表 (替代 V12 if act==1/2/3 + scene_index 硬编码)
        if any(k in story_function for k in ["建置", "建立", "起", "开场", "主题", "平凡", "铺垫", "副线", "B 故事"]):
            phase = "建置"
        elif any(k in story_function for k in ["上升", "转", "新世界", "试炼", "乐趣", "副线发展"]):
            phase = "上升动作" if scene_index < (total_scenes / 2) else "对抗"
        elif any(k in story_function for k in ["中点", "决定", "触发", "催化", "敌人", "压力", "高潮", "对决", "牺牲", "终局", "合", "解决", "收束", "结尾"]):
            phase = "解决"
        else:
            phase = "建置"

        weather_str = f" · {weather}" if weather else ""
        _mood_tag = f" · 情绪:{scene_mood}" if (mood_arc and len(mood_arc) > 1) else ""
        heading = f"{ie}.{location} — {time}{weather_str}  [第{act}幕·{phase} · 场{scene_num}/{total_scenes} · {story_function} · 戏剧张力:{tension_level}/10{_mood_tag}]"

        # V12.6 v13: 事件骨架 — EVENT_SKELETON 找不到时, 按 tension + location + 场景位置 兜底 8 变体 (替代 V12 单 "事件进行中")
        event_pool = EVENT_SKELETON.get(story_function)
        if not event_pool:
            event_pool = _generic_event_fallback(story_function, tension_level, location, act, scene_num, total_scenes)
        # V13.3: 事件池年代过滤 — 古装不出现电话/照片/deadline 等现代事件
        _ERA_EVENT_BAN = {
            "古装": ["电话", "照片", "相机", "手机", "收音机", "电视", "deadline", "车", "站"],
            "科幻": ["收音机", "粮票", "磁带", "蜡烛"],
        }
        _ban_words = _ERA_EVENT_BAN.get(_era_char)
        if _ban_words:
            _filtered = [e for e in event_pool if not any(w in str(e) for w in _ban_words)]
            if _filtered:
                event_pool = _filtered
        event = _seeded_choice(event_pool, seed_base + "_event")

        # 角色对白 — V13.3: 按年代选对白池 + 对白密度覆盖 + 跨场次无放回抽样
        _dial_pools = get_dialogue_pool(_era_char)
        if dial_override == "none":
            dial_pool = None  # 零对白: 纯视觉叙事
        else:
            _eff_density = dial_override if dial_override in ("low", "mid", "high") else dialogue_density
            dial_pool = _dial_pools.get(_eff_density, _dial_pools["mid"])
        # V13.4: 天气-对白一致性 — 场景无雪时过滤含雪对白 (避免沙漠踏雪)
        if dial_pool:
            _scene_has_snow = ("雪" in (scene_parsed.get("raw", "") or "")) or (weather and "雪" in weather)
            if not _scene_has_snow:
                _filtered_pool = [g for g in dial_pool
                                  if not any("雪" in (ln[2] if len(ln) > 2 else "") or "雪" in (ln[1] if len(ln) > 1 else "")
                                             for ln in g)]
                if _filtered_pool:
                    dial_pool = _filtered_pool
        if dial_pool:
            dialogues = _seeded_choice(dial_pool, seed_base + "_dial")
            _dial_key = tuple(tuple(d) for d in dialogues)
            if _dial_key in _used_dialogues:
                # 碰撞: 按 seed 生成确定性置换, 取第一个未使用的
                _rng_d = _random_mod.Random(int(_hashlib.md5((seed_base + "_dial_perm").encode()).hexdigest(), 16) % (2**32))
                _perm = list(dial_pool)
                _rng_d.shuffle(_perm)
                _found = None
                for cand in _perm:
                    ck = tuple(tuple(d) for d in cand)
                    if ck not in _used_dialogues:
                        _found = cand
                        break
                if _found is not None:
                    dialogues = _found
                    _dial_key = tuple(tuple(d) for d in dialogues)
            _used_dialogues.add(_dial_key)
        else:
            dialogues = []

        # 用 c1/c2/c3 替换占位符 (V13.3: 对手→c3, 不再泄漏字面占位词)
        real_dialogues = []
        for who, parenthetical, line in dialogues:
            who_real = c1 if who == "主角" else (c2 if who == "副线" else (c3 if who == "对手" else who))
            real_dialogues.append((who_real, parenthetical, line))

        # V12.6 v13: 动作描述按 director 派别多模板生成 (替换 V12 单模板)
        # 关键: 11 派别 × 6-8 模板 = 70+ 模板, hash 选 1, 同输入→同输出, 不同输入→不同变体
        director_key = _normalize_director(director)
        d_templates = DIRECTOR_ACTION_TEMPLATES.get(director_key, DIRECTOR_ACTION_TEMPLATES["default"])
        action_prefix_tpl = _seeded_choice(d_templates, seed_base + "_action_tpl")
        # V13.3: 复用预算 — 同模板超过 3 次则换未用满的 (确定性置换)
        if _tpl_use.get(("act_tpl", action_prefix_tpl), 0) >= 3 and len(d_templates) > 1:
            _rng_t = _random_mod.Random(int(_hashlib.md5((seed_base + "_tpl_perm").encode()).hexdigest(), 16) % (2**32))
            _perm_t = list(d_templates)
            _rng_t.shuffle(_perm_t)
            for _cand in _perm_t:
                if _tpl_use.get(("act_tpl", _cand), 0) < 3:
                    action_prefix_tpl = _cand
                    break
        _tpl_use[("act_tpl", action_prefix_tpl)] = _tpl_use.get(("act_tpl", action_prefix_tpl), 0) + 1

        # 用 c1/c2/c3 替换事件中的'主角/副线/对手'
        event_real = event.replace("主角", c1).replace("副线", c2).replace("对手", c3)

        # V12.6 v13: 物件融入 3 套变体 (替代 V12 单 obj_phrase 二选一)
        # 判断是 core 物件还是 supplement
        core_objs = set(p.get("objects", [])) if p else set()
        first_scene_obj = scene_objs[0] if scene_objs else ""
        is_core = first_scene_obj in core_objs and first_scene_obj
        if is_core and "物件" not in event_real and "旧信" not in event_real and "照片" not in event_real:
            # 重新按 core 模板选
            core_tpl = _seeded_choice(OBJ_PHRASE_VARIANTS["core"], seed_base + "_obj_core")
            obj_phrase = core_tpl.format(obj=first_scene_obj, location=location)
        else:
            sup_tpl = _seeded_choice(OBJ_PHRASE_VARIANTS["supplement"], seed_base + "_obj_sup")
            obj_phrase = sup_tpl.format(obj_str=obj_str, location=location)

        # V12.6 v13 + V13.3: tension 变体 × 尾部片段组合 = 潜文本多样性 (消除复读)
        subtext_pool = SUBTEXT_VARIANTS.get(tension_level, SUBTEXT_VARIANTS[5])
        _SUBTEXT_TAILS = [
            "像一句没寄出的话", "藏在呼吸的间隙里", "比台词更响",
            "压在动作底下", "谁都没戳破", "隔着{obj}传过来",
            "在沉默里发酵", "只有当事人懂", "像旧伤遇阴天",
            "等一个不会来的回应", "说给懂的人听", "比开口更诚实",
        ]
        subtext = _seeded_choice(subtext_pool, seed_base + "_subtext").format(c1=c1, obj=first_scene_obj or "它")
        _tail = _seeded_choice(_SUBTEXT_TAILS, seed_base + "_subtail").format(obj=first_scene_obj or "它")
        subtext = f"{subtext}, {_tail}"
        if _tpl_use.get(("subtext", subtext), 0) >= 2:
            _rng_s = _random_mod.Random(int(_hashlib.md5((seed_base + "_sub_perm").encode()).hexdigest(), 16) % (2**32))
            _perm_s = [v.format(c1=c1, obj=first_scene_obj or "它") + ", " + t.format(obj=first_scene_obj or "它")
                       for v in subtext_pool for t in _SUBTEXT_TAILS]
            _rng_s.shuffle(_perm_s)
            for _cand in _perm_s:
                if _tpl_use.get(("subtext", _cand), 0) < 2:
                    subtext = _cand
                    break
        _tpl_use[("subtext", subtext)] = _tpl_use.get(("subtext", subtext), 0) + 1

        # V12.6 v13: 物件情感承载 — 30+ 物件 + 自动按类型生成 (替代 V12 11 个硬编码)
        if scene_objs:
            obj_carrying = _obj_meaning_auto(scene_objs[0])
        else:
            obj_carrying = "无具体物件, 用空间和声音承载"

        # V12.6 v13: 内部动作 3 套变体 (替代 V12 单二选一)
        if tension_level >= 7:
            ia_pool = INTERNAL_ACTION_VARIANTS["high"]
        elif tension_level >= 4:
            ia_pool = INTERNAL_ACTION_VARIANTS["mid"]
        else:
            ia_pool = INTERNAL_ACTION_VARIANTS["low"]
        internal_action = " " + _seeded_choice(ia_pool, seed_base + "_internal").format(c1=c1, obj=first_scene_obj or "它")

        # V12.6 v13: 用 director 派别模板拼接 (替代 V12 单模板)
        # 注: action_prefix_tpl 已包含大部分结构, 再补 obj_phrase/subtext/internal
        try:
            action = action_prefix_tpl.format(
                location=location, time=time, weather_str=weather_str,
                event=event_real, c1=c1, c2=c2, c3=c3, mood=scene_mood,
                obj=first_scene_obj or "它", obj_str=obj_str,
                obj_phrase=obj_phrase, subtext=subtext, internal=internal_action.strip(),
            )
        except (KeyError, IndexError):
            # 模板占位符缺失时 fallback
            action = f"{location}, {time}{weather_str}. {event_real} {c1}在{location}, {scene_mood}弥漫. {obj_phrase} {subtext}.{internal_action}"

        # V13.3: 每场视觉锚点 — 光影/色彩/构图/焦段 按年代+时间+情绪推导 (补强视觉语言)
        _light_by_time = {"清晨": "晨光柔光", "早晨": "晨光柔光", "上午": "自然顶光", "中午": "正午硬光",
                         "下午": "斜射暖光", "黄昏": "黄昏逆光", "傍晚": "暮色暖光", "夜晚": "低照度实用光源",
                         "深夜": "极低照度", "黎明": "黎明冷光"}
        _light = _light_by_time.get(time, "自然光")
        _era_palette = {"古装": "大地色+青灰", "科幻": "冷灰蓝+深空黑", "复古": "低饱和暖褐", "现代": "中性灰+环境主色"}.get(_era_char, "中性色调")
        _comp = _seeded_choice(["三分法", "中心对称", "框中框", "引导线", "前景遮挡", "对角线"], seed_base + "_comp")
        _focal = _seeded_choice(["35mm", "50mm", "85mm"], seed_base + "_focal")
        _visual_anchor = f"[视觉: 光影={_light} | 色彩={_era_palette} | 构图={_comp} | 焦段={_focal}]"
        action_full = action + "\n" + _visual_anchor

        # 转场
        transition = _seeded_choice(TRANSITION_POOL, seed_base + "_trans")

        scenes.append({
            "act": act,
            "scene_index": scene_index,
            "scene_num": scene_num,
            "heading": heading,
            "action": action_full,
            "dialogues": real_dialogues,
            "transition": transition,
            "story_function": story_function,
            "tension_level": tension_level,
            "dialogue_density": dialogue_density,
            "duration_min": duration_min,
            "cumulative_min": round(cumulative_min + duration_min, 2),
            "shots_target": shots_target,
            "location": location,
            "time": time,
            "weather": weather,
            "ie": ie,
            "objects": scene_objs,
            "characters": chars,
            "purpose": f"推进 {story_function}, 戏剧张力 {tension_level}/10",
            "subtext": subtext,
            "obj_carrying": obj_carrying,
            "phase": phase,
            "mood": scene_mood,
            "_total_scenes": total_scenes,
        })
        cumulative_min += duration_min

    return scenes


# ============================================================
# 镜头生成器
# ============================================================
from aggregator.pacing_engine import (
    PACING_STYLES, get_pacing_for_scene, expand_pacing_shots, _make_pacing_shot
)

# 镜头策略池 (按 dialogue_density 分, V12.6 v9: 时长 0.3-30s 范围, 平均 10s/镜)
# 6 类镜头: establishing / character / detail / transition / reaction / lyric
# 时长哲学:
#   - establishing (建立): 5-30s, 让观众进入世界
#   - character (叙事): 5-15s, 正常对话/动作
#   - detail (物件): 1-5s, 物件特写
#   - transition (转场): 3-15s, 场景转换
#   - reaction (反应): 0.5-3s, 角色微反应 (用于快闪)
#   - lyric (抒情): 15-30s, 抒情空镜
#   - micro (微距): 0.3-1s, 极致瞬间 (嗨爆用)
SHOT_POOL_BY_DENSITY = {
    "low": {  # 低密度对白场戏, 镜头 10-20s/镜
        "establishing": [
            {"size": "大远景", "move": "固定", "focal": "14mm", "angle": "俯拍", "cut": "淡入淡出", "dur": 25.0,
             "focus_tpl": "{location}的全景, 时代感扑面", "sound_tpl": "环境音{weather}缓入"},
            {"size": "全景", "move": "慢摇", "focal": "24mm", "angle": "平视", "cut": "叠化", "dur": 15.0,
             "focus_tpl": "{location}细节, {object}的环境", "sound_tpl": "{object}的拟音"},
            {"size": "大远景", "move": "慢推", "focal": "24mm", "angle": "平视", "cut": "淡入淡出", "dur": 30.0,
             "focus_tpl": "{location}日与夜的过渡", "sound_tpl": "环境音渐强"},
        ],
        "character": [
            {"size": "中景", "move": "固定", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 10.0,
             "focus_tpl": "{c1}在{location}中, 静态", "sound_tpl": "环境音"},
            {"size": "近景", "move": "慢推", "focal": "85mm", "angle": "侧45", "cut": "叠化", "dur": 12.0,
             "focus_tpl": "{c1}的侧脸, 看不出表情", "sound_tpl": "呼吸声"},
            {"size": "中景", "move": "慢推", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 15.0,
             "focus_tpl": "{c1}慢慢做某事, 15s", "sound_tpl": "动作声"},
        ],
        "detail": [
            {"size": "特写", "move": "固定", "focal": "85mm", "angle": "俯拍", "cut": "硬切", "dur": 5.0,
             "focus_tpl": "{object}的特写", "sound_tpl": "微响"},
            {"size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "叠化", "dur": 3.0,
             "focus_tpl": "{c1}的手, 微动", "sound_tpl": "静默"},
        ],
        "transition": [
            {"size": "大远景", "move": "拉远", "focal": "24mm", "angle": "平视", "cut": "淡出", "dur": 20.0,
             "focus_tpl": "{location}拉远, 一切归于空旷", "sound_tpl": "环境音渐弱"},
        ],
        "reaction": [
            {"size": "近景", "move": "固定", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "{c1}反应, 2s", "sound_tpl": "反应声"},
            {"size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 1.0,
             "focus_tpl": "{c1}微表情, 1s", "sound_tpl": "完全静默"},
        ],
        "lyric": [
            {"size": "大远景", "move": "固定", "focal": "14mm", "angle": "平视", "cut": "叠化", "dur": 30.0,
             "focus_tpl": "天空/水面/远山, 30s 抒情空镜", "sound_tpl": "音乐渐入+留白"},
            {"size": "中景", "move": "慢拉", "focal": "35mm", "angle": "平视", "cut": "叠化", "dur": 22.0,
             "focus_tpl": "{c1}在远景中, 22s 抒情", "sound_tpl": "音乐+留白"},
        ],
        "micro": [
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 1.5,
             "focus_tpl": "{object}微距, 1.5s 极致细节", "sound_tpl": "完全静默"},
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "俯拍", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "微距 0.5s 极致", "sound_tpl": "完全静默"},
        ],
    },
    "mid": {  # 中密度对白场戏, 镜头 6-12s/镜
        "establishing": [
            {"size": "全景", "move": "固定", "focal": "35mm", "angle": "平视", "cut": "硬切", "dur": 8.0,
             "focus_tpl": "{location}全景, {c1}和{c2}在画面中", "sound_tpl": "环境音"},
            {"size": "中景", "move": "推近", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 10.0,
             "focus_tpl": "{c1}入场, 10s", "sound_tpl": "脚步+环境"},
        ],
        "character": [
            {"size": "中近景", "move": "固定", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 8.0,
             "focus_tpl": "{c1}说话, 表情克制", "sound_tpl": "对白+环境音"},
            {"size": "过肩", "move": "固定", "focal": "50mm", "angle": "过肩", "cut": "硬切", "dur": 7.0,
             "focus_tpl": "从{c1}肩膀看{c2}的反应", "sound_tpl": "对白+反应"},
            {"size": "近景", "move": "慢推", "focal": "85mm", "angle": "侧45", "cut": "硬切", "dur": 6.0,
             "focus_tpl": "{c1}的表情微变", "sound_tpl": "呼吸"},
            {"size": "中景", "move": "固定", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 5.0,
             "focus_tpl": "{c2}的动作/手势", "sound_tpl": "动作声"},
        ],
        "detail": [
            {"size": "特写", "move": "固定", "focal": "85mm", "angle": "俯拍", "cut": "硬切", "dur": 4.0,
             "focus_tpl": "{object}的特写, 承担情感", "sound_tpl": "微响"},
            {"size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 2.5,
             "focus_tpl": "{c1}的眼睛, 微动", "sound_tpl": "静默"},
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 1.5,
             "focus_tpl": "{object}微距, 1.5s", "sound_tpl": "完全静默"},
        ],
        "transition": [
            {"size": "中景", "move": "拉远", "focal": "35mm", "angle": "平视", "cut": "叠化", "dur": 5.0,
             "focus_tpl": "{c1}和{c2}的距离感", "sound_tpl": "环境音渐弱"},
        ],
        "reaction": [
            {"size": "近景", "move": "固定", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "{c1}反应, 2s", "sound_tpl": "反应声"},
            {"size": "大特写", "move": "固定", "focal": "85mm", "angle": "平视", "cut": "硬切", "dur": 1.0,
             "focus_tpl": "{c1}微表情, 1s", "sound_tpl": "完全静默"},
            {"size": "微距", "move": "快推", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "微表情 0.5s 极致", "sound_tpl": "完全静默"},
        ],
        "lyric": [
            {"size": "大远景", "move": "慢推", "focal": "14mm", "angle": "平视", "cut": "叠化", "dur": 15.0,
             "focus_tpl": "空镜, 15s 抒情", "sound_tpl": "音乐+留白"},
        ],
        "micro": [
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "俯拍", "cut": "硬切", "dur": 0.8,
             "focus_tpl": "微距 0.8s 极致", "sound_tpl": "完全静默"},
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 0.3,
             "focus_tpl": "微距 0.3s 极致瞬间", "sound_tpl": "完全静默"},
        ],
    },
    "high": {  # 高密度对白+高张力场戏, 镜头 1-5s/镜
        "establishing": [
            {"size": "全景", "move": "摇镜", "focal": "35mm", "angle": "平视", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "{location}全景, 紧张的氛围", "sound_tpl": "环境音+心悸"},
            {"size": "中景", "move": "手持", "focal": "35mm", "angle": "平视", "cut": "硬切", "dur": 2.5,
             "focus_tpl": "{location}混乱, 2.5s", "sound_tpl": "混乱声"},
        ],
        "character": [
            {"size": "中近景", "move": "手持", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "{c1}说话, 情绪外露", "sound_tpl": "对白+环境"},
            {"size": "过肩", "move": "手持", "focal": "50mm", "angle": "过肩", "cut": "硬切", "dur": 2.5,
             "focus_tpl": "从{c1}看{c2}的强烈反应", "sound_tpl": "对白+反应"},
            {"size": "特写", "move": "快推", "focal": "85mm", "angle": "平视", "cut": "跳切", "dur": 1.5,
             "focus_tpl": "{c1}的脸, 情绪爆发", "sound_tpl": "对白+呼吸"},
            {"size": "近景", "move": "跟拍", "focal": "85mm", "angle": "侧45", "cut": "跳切", "dur": 2.0,
             "focus_tpl": "{c2}的动作, 强烈反应", "sound_tpl": "动作声"},
            {"size": "中近景", "move": "手持", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 4.0,
             "focus_tpl": "{c1}继续说话, 4s", "sound_tpl": "对白"},
        ],
        "detail": [
            {"size": "大特写", "move": "快推", "focal": "100mm", "angle": "俯拍", "cut": "跳切", "dur": 1.0,
             "focus_tpl": "{c1}的眼泪/手/物件, 关键", "sound_tpl": "静默→心悸"},
            {"size": "特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "跳切", "dur": 0.5,
             "focus_tpl": "{object}的极致特写, 0.5s", "sound_tpl": "完全静默"},
        ],
        "transition": [
            {"size": "大远景", "move": "快拉", "focal": "24mm", "angle": "俯拍", "cut": "跳切", "dur": 2.5,
             "focus_tpl": "{location}全貌, 一切归于空间", "sound_tpl": "环境音骤停"},
        ],
        "reaction": [
            {"size": "近景", "move": "手持", "focal": "50mm", "angle": "平视", "cut": "跳切", "dur": 1.0,
             "focus_tpl": "{c1}反应, 1s 手持", "sound_tpl": "反应声"},
            {"size": "大特写", "move": "快推", "focal": "100mm", "angle": "平视", "cut": "跳切", "dur": 0.5,
             "focus_tpl": "{c1}微表情, 0.5s 极致", "sound_tpl": "完全静默"},
        ],
        "lyric": [
            {"size": "大远景", "move": "固定", "focal": "14mm", "angle": "平视", "cut": "叠化", "dur": 12.0,
             "focus_tpl": "空镜, 12s 紧张后的喘息", "sound_tpl": "音乐+留白"},
        ],
        "micro": [
            {"size": "微距", "move": "固定", "focal": "100mm", "angle": "俯拍", "cut": "跳切", "dur": 0.5,
             "focus_tpl": "微距 0.5s 极致", "sound_tpl": "完全静默"},
            {"size": "微距", "move": "快推", "focal": "100mm", "angle": "平视", "cut": "跳切", "dur": 0.3,
             "focus_tpl": "微距 0.3s 极致瞬间", "sound_tpl": "完全静默"},
        ],
    },
}


# 每种节奏的 target_avg_dur (秒/镜, 用于 shots_target 计算)
PACING_TARGET_AVG_DUR = {
    "一秒三闪": 1.0,       # 0.3s × 3 镜 + 1s 收束, 4 镜一组平均 1s
    "抖音超快": 0.7,       # 0.5-1s 镜
    "子弹时间": 0.5,       # 0.5s 镜
    "蒙太奇": 1.5,         # 0.5-3s 镜
    "定格凝固": 1.5,        # 单帧延长
    "延时摄影": 3.0,        # 0.5-2s 压缩
    "POV 主观": 2.0,        # 1-3s
    "航拍大师": 10.0,      # 5-15s
    "固定长镜": 90.0,      # 60-180s 不切
    "对话长镜": 90.0,      # 60-90s
    "游走长镜": 120.0,     # 60-180s
    "一镜到底": 480.0,     # 整段
    "慢镜高光": 8.0,       # 1-3s 实际慢放 5-10s
    "极慢抒情": 15.0,      # 1-2s 实际慢放 15-30s
    "车戏分镜": 2.0,        # 1-3s
    "枪战分镜": 1.0,        # 0.5-2s
    "演唱会纪录": 8.0,     # 5-15s
    "MV 慢镜": 3.0,        # 1-5s
    "舞蹈编排": 3.0,        # 1-3s
}


def get_target_avg_dur(pacing_style):
    """获取节奏的平均镜头时长."""
    return PACING_TARGET_AVG_DUR.get(pacing_style, 10.0)


# V12.6 v13: 特殊节奏的组数公式字典 (替代 V12 if-elif 硬编码)
# 格式: pacing_style -> (单组时长, 单组镜头数, 最大组数)
PACING_GROUP_FORMULAS = {
    "一秒三闪": (0.3 * 3 + 1.0, 4, 25),   # 0.3s×3 + 1s 收束 = 1.9s/组, 一场戏最多 25 组
    "子弹时间": (0.5 * 4 + 1.0, 5, 15),   # 0.5s×4 + 1s 收束 = 3s/组, 一场戏最多 15 组
    "MV 慢镜":  (1.0 * 3 + 1.5, 4, 20),   # 1s×3 + 1.5s = 4.5s/组, 一场戏最多 20 组
    "舞蹈编排": (2.0 * 2 + 1.0, 3, 18),   # 2s×2 + 1s = 5s/组, 一场戏最多 18 组
    "抖音超快": (0.7, 1, 30),             # 0.7s/镜, 一场戏最多 30 镜
    "蒙太奇":   (1.5, 1, 30),             # 1.5s/镜, 一场戏最多 30 镜
}


def _pacing_group_formula(pacing_style, duration_min, default_target_shots):
    """V12.6 v13: 按 pacing_style 查特殊组数公式. 找不到时用 default_target_shots.
    V14.3 (审查P2修复): 组数上限随时长动态放大 — 长场景用"加组"而非"拉长每镜"覆盖,
    保住快闪风格包络 (此前 60min 蒙太奇被拉成 30镜×120s)。绝对上限 600 组防爆炸。"""
    if pacing_style not in PACING_GROUP_FORMULAS:
        return min(default_target_shots, 30)
    group_dur, group_shots, max_groups = PACING_GROUP_FORMULAS[pacing_style]
    if group_dur <= 0:
        return min(default_target_shots, 30)
    groups = max(1, int(duration_min * 60 / group_dur + 0.5))
    # 动态上限: 至少 max_groups; 场景时长需要更多组时放大 (覆盖优先), 硬顶 600
    dyn_cap = min(600, max(max_groups, groups) if duration_min * 60 > group_dur * max_groups else max_groups)
    groups = min(groups, dyn_cap)
    return groups * group_shots


def generate_feature_shots(scenes, total_minutes=120, director="导演", mood="情绪", use_pacing=True, pacing_mode="auto", density_scale=1.0, mode_seed=""):
    """根据场次列表动态生成分镜表.
    V12.6 v9 重构 (用户核心要求):
    1. 平均镜头时长 ~10s (基线), 动态范围 0.3-30s (按情节调整)
    2. 每场戏按 (act, scene_index) 自动选节奏风格 (快闪/长镜/蒙太奇/慢镜)
    3. shots × dur = 场戏时长 (确保总秒数 cover 场戏时长, 真正电影时长)
    4. 长镜类 60-180s 不切; 慢镜类 1-3s 慢放 8-30s; 快闪类 0.3-2s 多镜密集
    density_scale: V14.2 — 镜头密度倍率 (来自模式 dur_scale)。>1=长镜(少镜), <1=快切(多镜)。
                   只改镜数不改总时长 (branch D 生成后按场戏时长归一化每镜 dur)。
    mode_seed: V14.2 — 模式名种子。同密度/同运镜的模式据此在 branch D 模板池里取不同偏移,
               让景别/焦段/焦点/声音真实差异化 (修复 15 模式字节级同构)。
    返回: list of dict: shot 完整字段.
    """
    density_scale = max(0.3, min(4.0, float(density_scale or 1.0)))
    # 模式种子 → 模板池偏移 (确定性: 同模式同输出, 不同模式不同模板)
    _seed_off = 0
    if mode_seed:
        _seed_off = int(_hashlib.md5(str(mode_seed).encode("utf-8", errors="replace")).hexdigest(), 16)
    all_shots = []
    shot_n = 0

    for scene in scenes:
        # V13.3: 写入 _director 键 — 让 70+ 导演镜头技法池真实生效 (此前永空→恒 default)
        scene["_director"] = _normalize_director(director)
        density = scene.get("dialogue_density", "mid")
        tension = scene.get("tension_level", 5)
        shots_target_base = scene.get("shots_target", 8)
        # V14.3 (审查P2防御): 时长消毒 — 负/零/非法值不产生负时长镜头
        try:
            duration_min = max(0.1, float(scene.get("duration_min", 3.0) or 3.0))
        except Exception:
            duration_min = 3.0
        location = scene.get("location", "场景")
        weather = scene.get("weather", "")
        time_str = scene.get("time", "")
        objects = scene.get("objects", ["关键道具"])
        chars = scene.get("characters", ["角色A", "角色B"])
        c1 = chars[0]
        c2 = chars[1] if len(chars) > 1 else chars[0]
        c3 = chars[2] if len(chars) > 2 else c2

        obj_str = "、".join(objects) if objects else "关键道具"
        story_function = scene.get("story_function", "推进")
        phase = scene.get("phase", "建置")
        act = scene.get("act", 1)
        scene_num = scene.get("scene_num", 1)
        subtext = scene.get("subtext", "")
        obj_carrying = scene.get("obj_carrying", "")

        # V12.6 v13: 节奏风格 — 按 story_function + director 动态选 (替代 V12 按 (act, scene_index) 硬编码)
        if use_pacing:
            if pacing_mode == "auto":
                # 优先用 scene["story_function"] (生成阶段已写入), 没有则用 beat_map 的 story_function
                sf = scene.get("story_function", "") or ""
                pacing_style = get_pacing_for_scene(
                    story_function=sf,
                    act=act,
                    scene_index=scene_num,
                    director=director,
                )
            else:
                pacing_style = pacing_mode
        else:
            pacing_style = "对话长镜"

        cat = PACING_STYLES.get(pacing_style, {}).get("category", "")
        is_fast_pacing = cat in ("快闪", "特殊", "类型") or pacing_style in ("一秒三闪", "抖音超快", "子弹时间", "蒙太奇", "定格", "延时摄影", "POV 主观", "车戏分镜", "枪战分镜", "演唱会纪录", "MV 慢镜", "舞蹈编排")
        is_slow_pacing = pacing_style in ("固定长镜", "对话长镜", "游走长镜", "一镜到底", "慢镜高光", "极慢抒情")

        # === A) 长镜类 (固定/对话/游走/一镜到底) ===
        # V12.6 v9 用户核心要求: 平均 10s, 范围 0.3-30s
        # 长镜场戏 = 多镜 ≤ 30s 模拟长镜感 (连续感/记录感), 镜间用叠化保持连续
        if use_pacing and pacing_style in ("固定长镜", "对话长镜", "游走长镜", "一镜到底"):
            # V14.3 (红队P1修复): 长镜类各自的单镜上限真实分化 —
            #   一镜到底 = 真单镜 (1镜=整场时长, 无切); 游走长镜 ≤60s; 固定/对话长镜 ≤30s 多镜叠化模拟。
            #   此前四类共用 30s 上限 → 一镜到底/游走长镜 与 固定长镜 镜数/时长完全相同 (幻影差异)。
            if pacing_style == "一镜到底":
                per_shot_max = max(60.0, duration_min * 60.0)  # 单镜覆盖整场
            elif pacing_style == "游走长镜":
                per_shot_max = 60.0
            else:
                per_shot_max = 30.0
            # V14.3 E2: ceil 保证镜数足够 — round 会让 per_shot_dur>上限 被截断后总时长缺角
            import math as _math_e2
            base_shots = max(1, _math_e2.ceil((duration_min * 60) / per_shot_max - 1e-9))
            # V14.2: density_scale 调节镜数 (per_shot_dur 随之整除场戏时长, 覆盖不变)
            target_shots = max(1, int(base_shots / density_scale + 0.5))
            per_shot_dur = round((duration_min * 60.0) / target_shots, 1)
            # density<=1 时 per_shot_dur 数学上 ≤ per_shot_max, 截断不再造成缺口
            if density_scale <= 1.0:
                per_shot_dur = min(per_shot_dur, per_shot_max)
            cut = "叠化" if target_shots > 1 else "无切"  # 镜间叠化保持连续感; 一镜到底=无切
            scene_shots = []
            # V12.6 v13: 从 PACING_STYLES 字典读 size/focal/angle, 替代 V12 if-elif 硬编码
            ps_dict = PACING_STYLES.get(pacing_style, {})
            ps_first = (ps_dict.get("shot_sequence", [{}])[_seed_off % len(ps_dict.get("shot_sequence", [{}]))]) if ps_dict else {}
            _lt_desc = ("一镜到底·真单镜" if pacing_style == "一镜到底"
                        else f"{target_shots} 镜叠化")
            tpl = {
                "size": ps_first.get("size", "中景"),
                "move": pacing_style,
                "focal": ps_first.get("focal", "50mm"),
                "angle": ps_first.get("angle", "平视"),
                "cut": cut,
                "dur": per_shot_dur,
                "focus_tpl": f"{pacing_style}, {round(per_shot_dur,1)}s, 长镜感 ({_lt_desc} cover {round(duration_min,1)}min, 连续感/记录感/真实感)",
                "sound_tpl": "完整时空(同期声+留白), 不配乐, 真实感沉淀",
                "pacing_intent": f"{round(per_shot_dur,1)}s 长镜组 — 连续感/记录感/真实感",
            }
            for i in range(target_shots):
                shot_n += 1
                scene_shots.append(_make_pacing_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, pacing_style, i, mode_seed))
            all_shots.extend(scene_shots)
            continue

        # === B) 慢镜类 (慢镜高光/极慢抒情) ===
        if use_pacing and pacing_style in ("慢镜高光", "极慢抒情"):
            target_avg_dur = get_target_avg_dur(pacing_style)
            target_shots = max(shots_target_base, int((duration_min * 60) / target_avg_dur + 0.5))
            target_shots = min(target_shots, 30)
            # V14.2: density_scale 调节镜数 (per_shot_dur 随之整除场戏时长, 覆盖不变)
            target_shots = max(1, int(target_shots / density_scale + 0.5))
            # V14.3 E2: 覆盖保障 — 若 30s 上限会截出缺口, 先加镜数让每镜 ≤30s
            if density_scale <= 1.0 and (duration_min * 60.0) / target_shots > 30.0:
                import math as _math_e2b
                target_shots = max(target_shots, _math_e2b.ceil((duration_min * 60) / 30.0 - 1e-9))
            per_shot_dur = round((duration_min * 60.0) / target_shots, 1)
            # V14.2: density>1 (长镜) 不截断 30s, 否则减镜后无法 cover 场戏时长; density<=1 保持 30s 上限
            if density_scale <= 1.0:
                per_shot_dur = min(per_shot_dur, 30.0)
            scene_shots = []
            # V12.6 v13: 从 PACING_STYLES 字典读 size/focal/move/angle, 替代 V12 if-elif 硬编码
            ps_dict = PACING_STYLES.get(pacing_style, {})
            ps_first = (ps_dict.get("shot_sequence", [{}])[_seed_off % len(ps_dict.get("shot_sequence", [{}]))]) if ps_dict else {}
            tpl = {
                "size": ps_first.get("size", "中景"),
                "move": ps_first.get("move", "慢速环绕"),
                "focal": ps_first.get("focal", "50mm"),
                "angle": ps_first.get("angle", "环绕 360°"),
                "cut": "叠化",
                "dur": per_shot_dur,
                "focus_tpl": f"{pacing_style}, {round(per_shot_dur,1)}s, 1/{int(8 if pacing_style=='慢镜高光' else 20)} 速度慢放 ({target_shots} 镜慢镜场戏, 实际慢放后 = {int(per_shot_dur*8 if pacing_style=='慢镜高光' else per_shot_dur*20)}s)",
                "sound_tpl": "音乐+呼吸+心跳, 慢节奏, 1/8 速度",
                "pacing_intent": f"{round(per_shot_dur,1)}s 慢镜 — 让瞬间变成永恒",
            }
            for i in range(target_shots):
                shot_n += 1
                scene_shots.append(_make_pacing_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, pacing_style, i, mode_seed))
            all_shots.extend(scene_shots)
            continue

        # === C) 快闪类 (蒙太奇/抖音/一秒三闪/子弹时间/车戏/枪战) ===
        if use_pacing and is_fast_pacing:
            target_avg_dur = get_target_avg_dur(pacing_style)
            # 通用公式: shots = ceil(场戏时长 / target_avg_dur)
            target_shots = max(shots_target_base, int((duration_min * 60) / target_avg_dur + 0.5))
            # V12.6 v13: 特殊节奏的组数公式改用 _pacing_group_formula 函数查表, 不再 if-elif
            target_shots = _pacing_group_formula(pacing_style, duration_min, target_shots)
            # V14.2: density_scale 调节镜数 (快切模式 density<1 → 更多镜)
            target_shots = max(1, int(target_shots / density_scale + 0.5))
            scene_shots = expand_pacing_shots(pacing_style, scene, c1, c2, location, weather, obj_str, shot_n + 1, all_shots, target_shots, mode_seed)
            shot_n += len(scene_shots)
            all_shots.extend(scene_shots)
            continue

        # === D) 默认 (auto 没匹配 / use_pacing=False) ===
        # V12.6 v9: shots_target = ceil(场戏时长 / 10s), 平均 10s/镜
        # V14.2: density_scale 调节镜头密度 (长镜模式>1 → 少镜; 快切模式<1 → 多镜), 总时长由后续归一化保证
        target_avg_dur = 10.0 * density_scale
        target_shots = max(shots_target_base, int((duration_min * 60) / target_avg_dur + 0.5))
        target_shots = min(target_shots, 40)
        shots_target = target_shots

        pool = SHOT_POOL_BY_DENSITY.get(density, SHOT_POOL_BY_DENSITY["mid"])
        establishing_pool = pool.get("establishing", [])
        character_pool = pool.get("character", [])
        detail_pool = pool.get("detail", [])
        transition_pool = pool.get("transition", [])
        reaction_pool = pool.get("reaction", [])
        lyric_pool = pool.get("lyric", [])
        micro_pool = pool.get("micro", [])

        # 7 类镜头分配
        n_establishing = max(1, shots_target // 12)
        n_transition = max(1, shots_target // 15)
        n_lyric = max(1, shots_target // 20)
        n_reaction = max(1, shots_target // 12)
        n_micro = max(1, shots_target // 20)
        n_detail = max(1, shots_target // 6)
        n_character = shots_target - n_establishing - n_transition - n_lyric - n_reaction - n_micro - n_detail
        if n_character < 2:
            n_character = 2
            n_establishing = max(1, shots_target - n_character - n_transition - n_lyric - n_reaction - n_micro - n_detail)

        scene_shots = []

        # 1) 开场建立 (8-30s, 让观众进入世界)
        for i in range(n_establishing):
            shot_n += 1
            tpl = establishing_pool[(i + _seed_off) % len(establishing_pool)] if establishing_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, opening=True))

        # 2) 角色镜头 (核心, 5-15s, 平均 10s)
        for i in range(n_character):
            shot_n += 1
            tpl = character_pool[(i + _seed_off) % len(character_pool)] if character_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, character_idx=i))

        # 3) 物件/细节镜头 (1-5s)
        for i in range(n_detail):
            shot_n += 1
            tpl = detail_pool[(i + _seed_off) % len(detail_pool)] if detail_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, detail_idx=i))

        # 4) 反应镜头 (0.5-3s, 用于快闪/嗨爆)
        for i in range(n_reaction):
            shot_n += 1
            tpl = reaction_pool[(i + _seed_off) % len(reaction_pool)] if reaction_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, character_idx=i))

        # 5) 微距 (0.3-1s 极致瞬间)
        for i in range(n_micro):
            shot_n += 1
            tpl = micro_pool[(i + _seed_off) % len(micro_pool)] if micro_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, detail_idx=i))

        # 6) 抒情空镜 (15-30s 长镜)
        for i in range(n_lyric):
            shot_n += 1
            tpl = lyric_pool[(i + _seed_off) % len(lyric_pool)] if lyric_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, closing=True))

        # 7) 结尾转场
        for i in range(n_transition):
            shot_n += 1
            tpl = transition_pool[(i + _seed_off) % len(transition_pool)] if transition_pool else None
            if tpl:
                scene_shots.append(_make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, closing=True))

        # V14.2: branch D 归一化 — 模板 dur 之和缩放到场戏时长 (density_scale 改镜数不改总时长)
        if scene_shots and abs(density_scale - 1.0) > 1e-6:
            _cur_total = sum(s.get("dur_sec", 0) for s in scene_shots)
            _target_total = duration_min * 60.0
            if _cur_total > 0:
                _k = _target_total / _cur_total
                for s in scene_shots:
                    _nd = round(s.get("dur_sec", 0) * _k, 1)
                    s["dur_sec"] = _nd
                    s["dur"] = f"{_nd}s"
        all_shots.extend(scene_shots)

    return all_shots


def _make_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, opening=False, character_idx=0, detail_idx=0, closing=False):
    """V12.6 v10: 根据模板生成单镜数据, 加 5 个深度字段 (director_note/actor_note/visual_design/sound_design/edit_intent)."""
    # V12.6 v10: focus 用具体物件 + 具体动作 + 身体细节 (不再"父亲在X"这种模板拼接)
    primary_obj = obj_str.split("、")[0] if obj_str else "关键道具"
    secondary_obj = obj_str.split("、")[1] if obj_str and len(obj_str.split("、")) > 1 else ""
    # 身体细节池 (按 c1/c2 角色)
    body_details = {
        "父亲": [
            "右手食指老茧触到砧板", "切菜的手指顿了一下, 刀尖垂下半寸",
            "肩微微耸起, 像承受什么", "没抬头, 但呼吸变沉",
            "擦灶台的手停在半空", "夹菜时先夹给别人",
            "茶端起来又放下", "门框上的手指收紧了",
        ],
        "女儿": [
            "手机屏幕光映在脸上", "翻出旧信的手轻微颤抖",
            "眼神闪到门缝, 停半拍", "把碗推到桌中央",
            "夹起凤梨, 放进父亲碗里", "肩膀微微缩了一下",
        ],
        "父亲": [
            "刀停砧板上, 手指颤", "窗前站立, 背影在逆光中",
        ],
    }
    body_pool = body_details.get(c1, body_details["父亲"])

    # 物件细节池
    obj_details = {
        "凤梨罐头": "凤梨罐头标签起泡, 过期十五年的黄印",
        "旧信": "信纸泛黄, 笔迹模糊, 折痕处已经裂开",
        "钢笔": "钢笔没墨水, 笔尖干涸, 笔帽上刻着两个字",
        "旧照片": "黑白照片, 边角卷起, 一家人的合影",
        "刀": "钢刀反光, 砧板旧痕一道道",
        "信物": "信物藏在抽屉最里层, 包着布",
    }
    obj_detail = obj_details.get(primary_obj, f"{primary_obj}被光线照出细节")

    # 电影技法池 (按导演风格 + 镜头类型) — V12.6 v13: 11 派别 × 5-7 模板 = 70+ 模板
    cinematic_techniques = {
        "王家卫": [
            "手不离刀, 但眼神闪到门缝, 3秒不回头",
            "声音先于画面消失: 收音机关了, 唯余雨声",
            "慢镜1/4, 让'瞬间'变成'永恒'",
            "重复: 同角度 3 次, 一次比一次近, 暗示'逼近'",
            "空镜: 走廊尽头灯闪两下, 没人, 也没人走过",
            "反射: 刀面映出女儿的脸, 主角不知道",
            "定格: 1s 凝固, 让'凤梨在碗里'变成'遗物'",
        ],
        "侯孝贤": [
            "固定机位, 让时间'住'在这里",
            "远景 + 自然光 + 留白, 观众'看'到的一切都是'发生'",
            "不切镜, 让对话的沉默成为内容",
            "窗外/门缝/楼梯: 边缘构图, 主体在角落",
            "长焦远景, 主角走入画面走20秒才到镜头前",
            "环境音先于画面, 风/雨/远处人声",
        ],
        "是枝裕和": [
            "自然光 + 固定机位 + 长镜, 像纪录片",
            "环境音先于画面, 收音机/雨/冰箱嗡鸣",
            "人物在画面边缘, 中央留给日常物件",
            "吃食的动作比对话更重要 — 刀碰砧板的节拍是这段戏的BPM",
            "门口送别: '路上小心' 像说了一千遍的平淡",
        ],
        "李安": [
            "对坐中景, 60s 不切, 让'吃饭'承载所有",
            "手部特写: 夹菜/放下/再夹, 每次动作都有不同含义",
            "过肩镜头: 从父肩看女, 父不知道女在看自己",
            "跨文化对坐: 主角用A文化的姿态, 眼睛里是B文化的纠结",
            "家庭会议式固定镜头, 每个眼神都是站位",
        ],
        "贾樟柯": [
            "卡拉OK + 90年代流行歌, 时代在背景里",
            "长焦+广角交替, 烟囱电视塔是县城的尺度",
            "纪录片式手持, 广场舞音响在背景里",
            "MTV流行歌插入, 歌词和画面对位, 但说的是另一件事",
            "突然的特写打脸, 然后又切到远景",
        ],
        "诺兰": [
            "时间折叠: 同一空间, 三个时间层同时出现",
            "概念隐喻: 钟表/镜子/走廊, 时间在身上分层",
            "悬念+倒叙: 镜头先给结果, 再回到原因",
            "空间对称: 主角和对手在画面两端, 中间是对称的影像",
            "宏大与渺小同框: 主角是宇宙级尺度的一部分",
        ],
        "塔可夫斯基": [
            "水面, 雨滴, 长镜7秒, 像水一样流动",
            "风吹过, 蜡烛摇, 脸被摇曳的烛光重新照亮",
            "雾, 一切都被模糊, 5秒后才清晰",
            "动物 (马/鸟/狗) 走过, 不解释",
            "日常物件升格: 一杯水一本书一根烛, 跟主角一样特写",
        ],
        "希区柯克": [
            "焦点从物件转到主角的脸, 用了2秒, 观众比主角先知道",
            "偷窥视角, 镜头是墙壁或窗, 主角不知道被看",
            "伏笔: 一个细节在画面边缘出现0.5秒, 30分钟后决定生死",
            "声画错位: 听到的是A, 看到的是B",
            "麦格芬 (MacGuffin): 物件重要但没人知道是什么",
        ],
        "黑泽明": [
            "多机位同时拍一个动作, 同一秒4个角度的主角",
            "大远景开场, 千军万马主角只是其中一员",
            "天气是演员: 风/雨/雪, 它们是另一个角色",
            "动作戏用多重剪接, 主角的刀在7个机位之间跳",
            "天气转变暗示命运: 晴转暴, 希望转绝望",
        ],
        "库布里克": [
            "绝对对称, 中线把画面切两半, 主角在中央, 命运的十字架",
            "一镜一念, 30秒长镜, 镜头没动, 内心走了一年",
            "凝视镜头, 主角看观众, 观众没地方躲",
            "走廊/楼梯的纵深几何, 主角越走越小越走越远",
            "慢动作+静止背景, 主角慢动作, 环境不动",
        ],
        "default": [
            "手不离动作, 但眼神闪到门外, 2s 不回",
            "声音先于画面消失, 让观众'听'到沉默",
            "慢镜1/4, 让'瞬间'变成'永恒'",
            "反射: 刀面映出女儿, 父亲不知道",
            "重复: 同角度 3 次, 一次比一次近",
        ],
    }
    technique_pool = cinematic_techniques.get(scene.get("_director", "default"), cinematic_techniques["default"])

    # director 来自 scene dict (如果有)
    director_name = scene.get("_director", "default")
    tech_pool = cinematic_techniques.get(director_name, cinematic_techniques["default"])

    # focus 重写: 具体物件 + 具体动作 + 身体细节 + 电影技法
    import hashlib as _hl
    seed = f"{shot_n}_{c1}_{primary_obj}_{location}_{character_idx}"
    body_idx = int(_hl.md5(seed.encode()).hexdigest(), 16) % len(body_pool)
    tech_idx = int(_hl.md5((seed + "_tech").encode()).hexdigest(), 16) % len(tech_pool)
    body_chosen = body_pool[body_idx]
    tech_chosen = tech_pool[tech_idx]

    if opening:
        focus = f"{location}，{time_str := scene.get('time', '')}{weather}。{obj_detail}。{c1}{body_chosen}。{tech_chosen}"
    elif closing:
        focus = f"{location}拉远，{obj_detail}留在画面边缘。{c2}没说话，{tech_chosen}"
    elif character_idx == 0:
        focus = f"{c1}{body_chosen}。{obj_detail}在{location}{weather}{time_str}的光里。{tech_chosen}"
    elif character_idx == 1:
        focus = f"{c2}的反应: 眼神闪到{primary_obj}，手轻微动。{obj_detail}。{tech_chosen}"
    elif character_idx == 2:
        focus = f"{c1}和{c2}在{location}，{body_chosen}。{secondary_obj or primary_obj}作为中介。{tech_chosen}"
    else:
        focus = f"{primary_obj}特写。{obj_detail}。{tech_chosen}"

    # sound 深度化: 比例化声音设计
    seed_s = seed + "_sound"
    sidx = int(_hl.md5(seed_s.encode()).hexdigest(), 16)
    # 4 层声音比例
    ambient_pct = 30 + (sidx % 30)  # 30-60% 环境音
    foley_pct = 10 + (sidx // 10 % 20)  # 10-30% 拟音
    music_pct = (sidx // 100 % 20)  # 0-20% 音乐
    silence_pct = max(0, 100 - ambient_pct - foley_pct - music_pct)  # 剩余留白
    sound = f"[声音] 环境{ambient_pct}% + 拟音{foley_pct}% + 音乐{music_pct}% + 留白{silence_pct}% | {tpl['sound_tpl'].format(location=location, c1=c1, c2=c2, object=primary_obj, weather=weather if weather else '')}"

    # 故事阶段 — V12.6 v13: 按 story_function 关键词查表 (替代 V12 if act + scene_index 硬编码)
    phase = scene.get("phase", "建置")
    act = scene.get("act", 1)
    scene_num = scene.get("scene_num", 1)
    story_func = scene.get("story_function", "") or ""
    # 按 story_function 关键词查 stage
    if "序章" in story_func or "开场" in story_func or "平凡" in story_func:
        stage = "序章"
    elif "建立" in story_func or "起" in story_func or "主题" in story_func or "新世界" in story_func or "乐趣" in story_func:
        stage = "建立"
    elif "铺垫" in story_func or "副线" in story_func or "B 故事" in story_func or "深化" in story_func:
        stage = "铺垫"
    elif "中点" in story_func:
        stage = "中点"
    elif "转" in story_func or "触发" in story_func or "催化" in story_func or "新世界" in story_func or "试炼" in story_func:
        stage = "转折"
    elif "高潮" in story_func or "对决" in story_func or "牺牲" in story_func:
        stage = "高潮"
    elif "黑夜" in story_func or "留白" in story_func or "决定" in story_func or "承诺" in story_func or "准备" in story_func:
        stage = "留白"
    elif "升华" in story_func or "主题" in story_func or "尾声" in story_func:
        stage = "主题升华"
    elif "合" in story_func or "解决" in story_func or "收束" in story_func or "结尾" in story_func:
        stage = "收束"
    else:
        # 兜底: 按 STAGE_ORDER 9 阶段均匀分布, 不再靠 act (V13.3: 修复 se 未导入 NameError + 硬编码35场)
        try:
            from aggregator.scene_engine import STAGE_ORDER as _STAGE_ORDER
        except Exception:
            _STAGE_ORDER = ["序章", "建立", "铺垫", "中点", "转折", "高潮", "留白", "收束", "主题升华"]
        _total = max(scene.get("_total_scenes", 35), 1)
        pos = scene_num / _total
        stage_idx = min(int(pos * len(_STAGE_ORDER)), len(_STAGE_ORDER) - 1)
        stage = _STAGE_ORDER[stage_idx]

    # 颜色/光影/材质/氛围 按张力等级递进
    tension = scene.get("tension_level", 5)
    stage_emotion = {
        1: "日常/平静", 2: "平静/从容", 3: "微妙变化/暗流",
        4: "紧张积累", 5: "暗涌", 6: "冲突/震惊",
        7: "对峙/爆发", 8: "决战场面/震撼", 9: "情感最高点/灵魂黑夜", 10: "爆发/极致/燃烧"
    }.get(tension, "日常/平静")

    # 故事弧线
    arc_pos = "建立" if shot_n <= 60 else ("铺垫" if shot_n <= 140 else ("转折" if shot_n <= 200 else ("高潮" if shot_n <= 250 else "收束")))

    # === V12.6 v10: 5 个深度字段 (顶级导演级描述) ===
    # 1. director_note (导演批注) - 王家卫式具体描写
    director_note = tech_chosen

    # 2. actor_note (演员指导) - V12.6 v13: 10 tension 段 × 3 变体 = 30 模板, 按 director 派别加变体
    actor_notes = {
        1: [
            "保持呼吸自然, 不抢情绪, 让'日常'成为'重量'",
            "眼睛不看镜头, 不看对手, 看'不在场的人'",
            "手可以微动, 但身体不动, 让'静'承担一切",
        ],
        2: [
            "动作慢, 像水里游, 让'日常'成为'仪式'",
            "表情先在眼眶, 嘴没动, 让观众'看到'在想",
            "呼吸和脚步同节拍, 像侯孝贤/是枝裕和式",
        ],
        3: [
            "呼吸先沉一下, 让观众'听到'角色在想什么",
            "眼神先移, 身体后动, 避免'先行动后想'的俗套",
            "表情不要立刻, 留 0.5s 让情绪'渗'出来",
        ],
        4: [
            "手指在物件上停顿 0.3s, 让'碰'成为'读'",
            "肩膀微动, 像风还没到, 让'预兆'成为身体",
            "脚步停, 但眼睛继续, 让'没走'成为'想走'",
        ],
        5: [
            "眼眶湿, 但不要落泪, 让观众'以为'在落泪",
            "嘴角微动, 不说话, 沉默=台词",
            "手放下, 头微低, 让'承认'成为动作",
        ],
        6: [
            "呼吸浅, 但不急促, 像在压住什么",
            "眼神对准时, 头微偏 5°, 让'对视'成为'错开'",
            "手指扣进掌心, 但观众看不太清, 让'压制'成为'暗示'",
        ],
        7: [
            "屏住呼吸 3 秒, 然后慢慢呼出, 不抢节奏",
            "眼神从对手移开, 看一个不在场的位置, 让'拒绝'成为姿态",
            "身体前倾半寸, 让'靠近'成为距离",
        ],
        8: [
            "声音先动, 嘴后动, 让'想说话'先于'说'",
            "眼眶红了, 但泪没出来, 让'忍住'成为'看'",
            "身体微微后倾, 像被推了一下但没退",
        ],
        9: [
            "完全静止, 让'极致'来自'没有动作'",
            "眼眶可湿但不落泪, 让'忍住'成为高潮",
            "嘴角可以微动, 头可以微低, 但不要说话",
        ],
        10: [
            "所有动作都停, 唯余呼吸, 让'一切释放'是'没有'",
            "嘴微张, 声音却没出来, 让'喊不出'成为'喊'",
            "眼眶的泪终于落下, 但只一滴, 让'极致'是'克制'",
        ],
    }
    # 派别变体 — 演员指导也按 director 派别微调
    director_actor_twist = {
        "王家卫": " 让这一秒变三秒, 让观众'住'在角色的眼睛里.",
        "侯孝贤": " 让动作在自然光里'自己说话', 演员只是空间的一部分.",
        "是枝裕和": " 让日常的动作(切菜/吃饭/走路)承载情绪, 不抢表演.",
        "李安": " 让文化冲突在'吃饭''看菜单'里, 不直接演冲突.",
        "贾樟柯": " 让时代的声音(流行歌/广场舞)在背景里, 演员活在时代里.",
        "诺兰": " 让演员的'概念'先于'情绪', 眼神里是结构, 不是心情.",
        "塔可夫斯基": " 让演员像水一样流, 不表演, 只是在.",
        "希区柯克": " 让演员知道'被看', 但观众不知道.",
        "黑泽明": " 让动作成为'画面构图'的一部分, 演员和天气/光/空间共舞.",
        "库布里克": " 让演员看镜头, 让观众没地方躲.",
    }
    actor_pool = actor_notes.get(tension, actor_notes[5])
    actor_idx = int(_hl.md5((str(shot_n) + "_actor").encode()).hexdigest(), 16) % len(actor_pool)
    actor_note = actor_pool[actor_idx] + director_actor_twist.get(director_name, "")

    # 3. visual_design (画面设计) - 光位/色彩/构图/焦点
    color_progression = {
        1: "中性色调", 2: "暖色调(自然)", 3: "略暖", 4: "色彩偏移(微冷)",
        5: "冷色侵入", 6: "冷色调/高对比", 7: "高对比红/黑", 8: "极致对比(明暗)",
        9: "色彩最饱和", 10: "极致色彩(饱和拉满)"
    }
    light_progression = {
        1: "漫射光(阴天)", 2: "顺光/自然光", 3: "侧顺光", 4: "阴影增加",
        5: "光源不稳定", 6: "侧光/逆光(戏剧性)", 7: "底光/顶光", 8: "强光/逆光剪影",
        9: "暖光最强", 10: "戏剧性光影(顶光/底光)"
    }
    material_progression = {
        1: "日常材质", 2: "自然材质(棉/木/石)", 3: "温暖材质(木/棉)", 4: "质感变粗糙",
        5: "金属反光出现", 6: "冷硬材质(金属/玻璃/混凝土)", 7: "尖锐材质",
        8: "冲突材质(铁/血/火)", 9: "肌肤/泪/温暖材质", 10: "极致质感(汗水/血/泪/火花)"
    }
    atmosphere_progression = {
        1: "日常/从容", 2: "平和/自然/温暖", 3: "期待/即将变化", 4: "压抑/积累",
        5: "不安/预兆", 6: "紧张/压迫/失衡", 7: "危险/失控", 8: "震撼/失重",
        9: "情感燃烧", 10: "爆发/极致/燃烧"
    }
    rhythm_progression = {
        1: "中慢", 2: "慢(长镜)", 3: "慢但有暗流", 4: "节奏加快",
        5: "变速", 6: "快切", 7: "快切", 8: "密集→急停",
        9: "长镜+快切交替", 10: "最快(密集切镜)"
    }
    visual_design = f"光:{light_progression.get(tension, '漫射光')} | 色:{color_progression.get(tension, '中性色调')} | 材质:{material_progression.get(tension, '日常材质')} | 焦点:{primary_obj} | 构图:{tpl.get('size', '中景')}{tpl.get('focal', '50mm')}"

    # 4. sound_design (声音设计) - 4 层比例
    sound_design = f"环境{ambient_pct}% + 拟音{foley_pct}% + 音乐{music_pct}% + 留白{silence_pct}%"

    # 5. edit_intent (剪辑意图) - V12.6 v13: 按 director 派别 6-8 模板, 让剪辑意图有导演指纹
    edit_intents_by_director = {
        "王家卫": [
            "用慢镜1/4延展, 让这一秒变三秒, 让观众'住'在情绪里",
            "用物件特写(凤梨/烟/手)替代台词, 沉默=台词",
            "用反射/剪影让'想'成为'看', 不直接演'想'",
            "重复: 同角度 3 次, 一次比一次近, 暗示'逼近'",
            "空镜: 走廊尽头灯闪两下, 没人, 但'情绪在'",
            "定格: 1s 凝固, 让'凤梨在碗里'变成'遗物'",
            "声画错位: 声音先于画面消失, 让'听'比'看'更重",
        ],
        "侯孝贤": [
            "不切, 让这一镜'住'30-60s, 让时间真实流动",
            "让对白之间的沉默成为内容, 不删",
            "窗外/门缝/楼梯: 边缘构图, 主体在角落",
            "远景+自然光, 观众'看到'的一切都是'正在发生'",
            "环境音先于画面, 风/雨/远处人声带出空间",
        ],
        "是枝裕和": [
            "切到日常物件(刀/碗/门), 让'吃食的动作'比'对白'更重要",
            "固定机位, 不切, 让家庭日常'自己说话'",
            "环境音(冰箱/收音机/雨)先于画面, 让家'有声音'",
            "人物在画面边缘, 中央留给物件, 让'人'和'物'同重",
        ],
        "李安": [
            "用吃饭的筷子节奏暗示冲突, 不直接演冲突",
            "过肩镜头, 让一方不知道另一方在看自己",
            "手部特写: 夹菜/放下/再夹, 每次动作有不同含义",
            "文化对坐, 主角用A文化的姿态, 眼睛里是B文化的纠结",
        ],
        "贾樟柯": [
            "流行歌插入, 歌词和画面对位, 但说的是另一件事",
            "纪录片式手持, 时代在背景里, 演员活在时代里",
            "长焦+广角交替, 县城烟囱电视塔是时代的尺度",
        ],
        "诺兰": [
            "用镜头先给结果, 再回到原因, 让观众先知道",
            "空间对称, 主角在画面两端, 中间是对称的影像",
            "时间折叠, 同一空间三个时间层同时出现",
            "用钟表/镜子/走廊, 让'概念'成为'画面'",
        ],
        "塔可夫斯基": [
            "用风吹过, 蜡烛摇, 脸被重新照亮",
            "用动物走过, 不解释, 让自然成为主角",
            "用日常物件升格, 一杯水跟主角一样特写",
            "用雾模糊一切, 5秒后才清晰",
        ],
        "希区柯克": [
            "用焦点从物件转到主角的脸, 2s, 观众比主角先知道",
            "用偷窥视角, 镜头是墙壁或窗, 主角不知道被看",
            "用麦格芬, 物件重要但没人知道是什么",
            "用伏笔, 一个细节在画面边缘0.5s, 30分钟后决定生死",
        ],
        "黑泽明": [
            "多机位同时拍一个动作, 同一秒4个角度的主角",
            "用天气作为演员, 风/雨/雪是另一个角色",
            "动作戏用多重剪接, 主角的刀在7个机位之间跳",
        ],
        "库布里克": [
            "绝对对称, 中线把画面切两半, 主角在中央",
            "凝视镜头, 主角看观众, 观众没地方躲",
            "走廊/楼梯纵深, 主角越走越小越走越远",
            "慢动作+静止背景, 主角慢动作, 环境不动",
        ],
        "default": [
            "承接上一镜, 用身体细节延展情绪, 不抢节奏",
            "用具体物件替代台词, 让'沉默'成为'台词'",
            "用反射/剪影让'想'成为'看'",
            "在动作前留 0.5s 静默, 让'即将'成为'正在'",
            "切到物件特写, 让'看到'成为'感受'",
            "切到空镜, 让'人不在'成为'人在想'",
        ],
    }
    edit_pool = edit_intents_by_director.get(director_name, edit_intents_by_director["default"])
    edit_idx = int(_hl.md5((str(shot_n) + "_edit").encode()).hexdigest(), 16) % len(edit_pool)
    edit_intent = edit_pool[edit_idx]

    # 叙事目的 + 上一镜回答 (V12.6 v10: 更具体)
    if opening:
        purpose = f"建立{location}空间, 物件先于人物出现, 让观众先'看到'再'进入'"
        note = f"开场·建立·{obj_detail[:20]}"
    elif closing:
        purpose = f"拉远/转场, 物件留在画面边缘, 让'离开'成为'留白'"
        note = f"收束·转场·{obj_detail[:20]}"
    elif character_idx == 0:
        purpose = f"展示{c1}状态, 身体细节承担情绪"
        note = f"{c1}状态·{body_chosen[:20]}"
    elif character_idx == 1:
        purpose = f"展示{c2}反应, 微表情替代台词"
        note = f"{c2}反应·{body_chosen[:20]}"
    elif character_idx == 2:
        purpose = f"两人关系推进, 中介物件(凤梨罐头)承担冲突"
        note = f"关系推进·{obj_detail[:20]}"
    else:
        purpose = f"推进{scene.get('story_function', '剧情')}, 物件特写让'情绪'成为'可见'"
        note = f"推进{scene.get('story_function', '剧情')}·{obj_detail[:20]}"

    if all_shots:
        prev_shot = all_shots[-1]
        note += f"; 承接镜{prev_shot.get('n', '?')}的{prev_shot.get('stage_emotion', '情绪')}"
    else:
        note += "; 物件先于人物, 让观众'看到'再'进入'"

    return {
        "n": shot_n,
        "scene": scene_num,
        "act": act,
        "size": tpl["size"],
        "angle": tpl["angle"],
        "move": tpl["move"],
        "focal": tpl["focal"],
        "dur": f"{tpl['dur']}s",
        "dur_sec": tpl["dur"],
        "focus": focus,
        "sound": sound,
        "sound_design": sound_design,  # V12.6 v10: 4 层声音比例
        "cut": tpl["cut"],
        "purpose": purpose,
        "note": note,
        "director_note": director_note,  # V12.6 v10: 导演批注
        "actor_note": actor_note,  # V12.6 v10: 演员指导
        "visual_design": visual_design,  # V12.6 v10: 画面设计
        "edit_intent": edit_intent,  # V12.6 v10: 剪辑意图
        "stage": stage,
        "stage_name": stage,
        "stage_emotion": stage_emotion,
        "stage_color": color_progression.get(tension, "中性色调"),
        "stage_light": light_progression.get(tension, "漫射光(阴天)"),
        "stage_material": material_progression.get(tension, "日常材质"),
        "stage_atmosphere": atmosphere_progression.get(tension, "日常/从容"),
        "stage_rhythm": rhythm_progression.get(tension, "中慢"),
        "story_function": scene.get("story_function", "推进"),
        "tension_level": tension,
        "location": location,
        "weather": scene.get("weather", ""),
        "time": scene.get("time", ""),
        "ie": scene.get("ie", "内"),
        "obj_carrying": scene.get("obj_carrying", ""),
        "subtext": scene.get("subtext", ""),
        "phase": phase,
        "arc_position": arc_pos,
    }


# ============================================================
# 公共 API
# ============================================================
def generate_feature_film(scene_parsed, director, mood, intent, target_minutes=120, story_theory="三幕剧"):
    """一站式生成长片: 场次 + 镜头.
    返回: (scenes, shots, stats)
    """
    scenes = generate_feature_scenes(scene_parsed, director, mood, intent, target_minutes, story_theory)
    shots = generate_feature_shots(scenes, target_minutes, director, mood)
    total_shot_dur = sum(s["dur_sec"] for s in shots)
    stats = {
        "target_minutes": target_minutes,
        "actual_minutes": sum(s["duration_min"] for s in scenes),
        "total_scenes": len(scenes),
        "total_shots": len(shots),
        "total_shot_seconds": total_shot_dur,
        "total_shot_minutes": round(total_shot_dur / 60.0, 2),
        "act_breakdown": {
            1: sum(1 for s in scenes if s["act"] == 1),
            2: sum(1 for s in scenes if s["act"] == 2),
            3: sum(1 for s in scenes if s["act"] == 3),
        },
        "story_theory": story_theory,
    }
    return scenes, shots, stats


if __name__ == "__main__":
    # 自检
    test_scene = {
        "location": "厨房", "time": "夜", "ie": "内", "weather": "雨",
        "characters": ["父亲", "女儿"], "objects": ["旧信", "凤梨罐头", "钢笔"],
        "type": "日常室内", "raw": "父女在厨房, 雨夜, 1998年哈尔滨",
    }
    for tm in [120, 90, 60, 30, 5]:
        scenes, shots, stats = generate_feature_film(test_scene, "王家卫", "史诗", "说不出口的爱", tm)
        print(f"=== {tm}min ===")
        print(f"  场次: {stats['total_scenes']}, 镜头: {stats['total_shots']}, 实际分钟: {stats['actual_minutes']:.1f}, 镜头秒数: {stats['total_shot_seconds']:.1f}s")
        print(f"  三幕: act1={stats['act_breakdown'][1]} / act2={stats['act_breakdown'][2]} / act3={stats['act_breakdown'][3]}")
