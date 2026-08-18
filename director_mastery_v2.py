# -*- coding: utf-8 -*-
"""
Director Mastery V2 — 全球 12 套顶级导演/编剧理论融合系统
============================================================

融合以下 12 套理论,用于每一流程、每一环节、每一步:
1. Save the Cat 15 拍 (Blake Snyder)
2. Joseph Campbell Hero's Journey 17 阶段
3. Christopher Vogler Hero's Journey 12 阶段
4. Dan Harmon Story Circle 8 步
5. Robert McKee 故事 22 原则
6. Syd Field 三幕剧结构
7. Sequence Approach 8 sequences (Frank Daniel)
8. 五幕结构 (Aristotle/Shakespeare)
9. 新媒体短剧三秒铁律 (ReelShort/DramaBox)
10. 抖音短剧 6 大套路
11. Lajos Egri 角色前提/角色弧
12. Story Circle + Sequence Method 综合
"""

# ============================================================
# 1. Save the Cat 15 拍 (Blake Snyder)
# ============================================================
SAVE_THE_CAT_BEATS = {
    "Opening Image": "第 1 页 | 故事开始的世界定格画面,30 秒内把观众拉入世界",
    "Theme Stated": "第 5 页 | 主题被某角色说出,但主角没听进去",
    "Set-up": "第 1-10 页 | 建立世界/角色/状态/暗示后续",
    "Catalyst": "第 12 页 | 事件打破主角现状(inciting incident)",
    "Debate": "第 12-25 页 | 主角犹豫是否上路(refusal of the call)",
    "Break into Two": "第 25 页 | 主角做出选择,正式进入新世界",
    "B Story": "第 30 页 | 副线出现(常是爱情/导师),承载主题",
    "Fun and Games": "第 30-55 页 | 主角在新世界玩/promise of the premise",
    "Midpoint": "第 55 页 | 假胜利/假失败,主角状态翻转",
    "Bad Guys Close In": "第 55-75 页 | 内外敌人夹击,主角内部弱点暴露",
    "All Is Lost": "第 75 页 | 至暗时刻,失去 mentor/love/希望",
    "Dark Night of the Soul": "第 75-85 页 | 主角最低谷,质疑一切",
    "Break into Three": "第 85 页 | 主角找到答案/灵感,重新上路",
    "Finale": "第 85-110 页 | 终局之战,综合 Act 1 + Act 2 学到的",
    "Final Image": "第 110 页 | 终场定格画面,与开场形成对比/反转",
}

# ============================================================
# 2. Joseph Campbell Hero's Journey 17 阶段
# ============================================================
HERO_JOURNEY_17 = {
    "1. Call to Adventure": "冒险召唤: 主角被邀请进入未知世界",
    "2. Refusal of the Call": "拒绝召唤: 主角犹豫/拒绝/逃避",
    "3. Supernatural Aid": "超自然援助: 导师/神器出现,提供工具/智慧",
    "4. Crossing the Threshold": "跨越门槛: 主角正式离开旧世界",
    "5. Belly of the Whale": "鲸腹: 主角被吞噬/彻底投入未知,蜕变开始",
    "6. Road of Trials": "试炼之路: 一系列考验,盟友/敌人浮现",
    "7. Meeting with the Goddess": "邂逅女神: 主角遇到爱的对象/终极接受",
    "8. Woman as Temptress": "诱惑女人: 主角被物质/权力/欲望诱惑",
    "9. Atonement with the Father": "与父和解: 主角面对权威,获得认可",
    "10. Apotheosis": "神化: 主角获得终极洞见/重生",
    "11. The Ultimate Boon": "终极恩赐: 主角获得宝藏/答案",
    "12. Refusal of the Return": "拒绝回归: 主角不愿回到旧世界",
    "13. The Magic Flight": "神奇飞行: 主角携宝逃亡",
    "14. Rescue from Without": "外援救援: 主角被外界力量拉回",
    "15. Crossing the Return Threshold": "回归门槛: 主角再次跨越",
    "16. Master of Two Worlds": "双界之主: 主角整合二元世界",
    "17. Freedom to Live": "自由生活: 主角摆脱二元对立,活在当下",
}

# ============================================================
# 3. Christopher Vogler Hero's Journey 12 阶段 (编剧常用版)
# ============================================================
HERO_JOURNEY_12 = {
    "1. Ordinary World": "平凡世界: 主角在舒适区,观众建立共情",
    "2. Call to Adventure": "冒险召唤: 事件打破现状,主角必须行动",
    "3. Refusal of the Call": "拒绝召唤: 主角恐惧未知,犹豫不前",
    "4. Meeting the Mentor": "遇见导师: 智者/朋友给出工具/勇气",
    "5. Crossing the First Threshold": "跨越门槛: 主角承诺冒险,不可回头",
    "6. Tests, Allies, Enemies": "试炼盟友敌人: 主角在新世界学习规则",
    "7. Approach to the Inmost Cave": "接近最深处: 主角准备面对最大考验",
    "8. Ordeal": "试炼: 主角最黑暗时刻,濒死/被击溃,浴火重生",
    "9. Reward (Seizing the Sword)": "奖赏: 主角获得宝藏/知识/盟友",
    "10. The Road Back": "归途: 主角携宝返回,追击开始",
    "11. Resurrection": "复活: 终极考验,主角最后一次死亡/重生",
    "12. Return with the Elixir": "携宝归来: 主角回归,带来改变世界的礼物",
}

# ============================================================
# 4. Dan Harmon Story Circle 8 步
# ============================================================
STORY_CIRCLE_8 = {
    "1. Comfort Zone": "舒适区: 主角在熟悉的日常,渴望被打破",
    "2. Want": "欲望: 主角想要某物(表层/深层)",
    "3. Cross Threshold": "跨越门槛: 主角进入陌生情境",
    "4. Adapt": "适应: 主角学会新规则,获得技能/盟友",
    "5. Get What They Want": "得到: 主角得到想要的(表层目标)",
    "6. Pay Heavy Price": "付出代价: 意外损失发生(深层代价)",
    "7. Return": "回归: 主角回到熟悉情境(但已经不同)",
    "8. Having Changed": "改变: 主角已完成蜕变,带回智慧",
}

# ============================================================
# 5. Robert McKee 故事原则 (核心 7 条)
# ============================================================
MCKEE_PRINCIPLES = {
    "principle_1_gap": "故事 = 欲望 + 障碍 + 行动 + 结果,价值落差构成故事",
    "principle_2_choice": "故事 = 角色在关键时刻的选择,不是巧合,选择塑造人物",
    "principle_3_truth": "故事讲述的不是生活,是生活的比喻(更深层的真理)",
    "principle_4_desire": "主角的欲望必须明确(单数),观众的同情通过欲望建立",
    "principle_5_conflict": "冲突 = 期待+阻力,角色面对的对手必须强大且对等",
    "principle_6_arc": "角色弧 = 价值正负电荷的变化(从-到+或+到-)",
    "principle_7_beats": "故事 = 场景序列,场景 = 节拍序列,节拍 = 行动/反应",
}

# ============================================================
# 6. Syd Field 三幕剧 (Paradigm)
# ============================================================
THREE_ACT_PARADIGM = {
    "Act_1_Setup": "建置 (0-25%): 介绍主角/世界/状态,结尾是 Plot Point 1",
    "Act_1_PlotPoint1": "Plot Point 1 (25%): 触发事件,主角进入新世界",
    "Act_2_Confrontation": "对抗 (25-75%): 主角在新世界遇到障碍,中点是 Midpoint",
    "Act_2_Midpoint": "中点 (50%): 主要情节转折,主角获得/失去关键信息",
    "Act_2_PlotPoint2": "Plot Point 2 (75%): 主要危机,主角进入 Act 3",
    "Act_3_Resolution": "解决 (75-100%): 主角解决冲突,Climax 在 90%",
    "Act_3_Climax": "Climax (90%): 终极对决,主角选择/改变",
    "Act_3_Resolution_end": "尾声 (100%): 新状态/新平衡",
}

# ============================================================
# 7. Sequence Approach 8 Sequences (Frank Daniel)
# ============================================================
EIGHT_SEQUENCES = {
    "Sequence_1_Setup": "8 段第 1 段 (0-12.5%): 故事起点/主角/激励事件",
    "Sequence_2_Response": "8 段第 2 段 (12.5-25%): 主角首次反应,确立新方向",
    "Sequence_3_Attack": "8 段第 3 段 (25-37.5%): 第一次进攻/挑战",
    "Sequence_4_Midpoint": "8 段第 4 段 (37.5-50%): 中点,主角反击/决战",
    "Sequence_5_Response": "8 段第 5 段 (50-62.5%): 中点后反响,情势逆转",
    "Sequence_6_Attack": "8 段第 6 段 (62.5-75%): 第二次进攻,危机升级",
    "Sequence_7_Response": "8 段第 7 段 (75-87.5%): 主角最后一次反击",
    "Sequence_8_Resolution": "8 段第 8 段 (87.5-100%): 终局,新平衡",
}

# ============================================================
# 8. 五幕结构 (Aristotle / Shakespeare / Gustav Freytag)
# ============================================================
FIVE_ACT_STRUCTURE = {
    "Act_1_Exposition": "第 1 幕 介绍 (0-10%): 介绍人物/世界/冲突种子",
    "Act_2_Rising": "第 2 幕 上升 (10-30%): 上升动作,冲突展开",
    "Act_3_Climax": "第 3 幕 高潮 (30-70%): 中点高潮(戏剧最大转折)",
    "Act_4_Falling": "第 4 幕 下降 (70-90%): 下降动作,后果显现",
    "Act_5_Catastrophe": "第 5 幕 结局 (90-100%): 灾难/和解,新秩序",
}

# ============================================================
# 9. 新媒体短剧三秒铁律 (ReelShort / DramaBox)
# ============================================================
SHORT_DRAMA_RULES = {
    "three_second_rule": "0-3 秒铁律: 开头前 3 秒必抛强冲突/强悬念/颠覆认知画面,杜绝铺垫/慢镜头/空镜,第一秒锁住观众视线",
    "ten_second_upgrade": "10-15 秒升级: 每 10-15 秒升级一次矛盾(误会/对峙/打脸/危机/反转铺垫),持续拉扯情绪",
    "ending_hook": "结尾钩子: 每集最后 2 秒抛终极悬念/致命反转/突发危机/身份揭秘,倒逼看下一集",
    "visual_grounding": "画面落地: 所有情节标注镜头景别/画面动作/细节神态,编剧摄像可直接对标拍摄",
    "youth_dialogue": "对白年轻化: 摒弃书面化/生硬台词,贴合年轻人日常口语,自然真实利落不拖沓",
    "shot_division": "0-3s 黄金开篇: 爆点画面+直击悬念,拒绝铺垫;30%-70% 中段: 矛盾升级/误会加深/伏笔预埋/正反对峙;最后 3s 结尾钩子: 突发反转/身份曝光/致命危机/惊天秘密",
}

# ============================================================
# 10. 抖音短剧 6 大套路
# ============================================================
DOUYIN_TROPES = {
    "穿越": "现代人穿越古代/未来/平行世界,带现代知识碾压(主角用现代 Excel/PPT/医学/物理/厨艺/短视频)",
    "重生": "主角死前回溯时间,复仇/弥补遗憾/逆袭,常见:前世被害-重生复仇,或被渣男贱女陷害-重生揭穿",
    "真假千金/少爷": "豪门错换 18 年,主角是流落民间的真千金/少爷,被假千金/少爷陷害,最终身份曝光,真千金归来复仇",
    "霸总": "霸道总裁爱上灰姑娘,常见:万亿富豪+普通女,宠溺无底线,身份差制造冲突",
    "战神": "退役战神/兵王回归都市,妻女被欺,复仇+展现实力,男频爽剧",
    "团宠": "马甲大佬被家人忽视,实际上是顶级大佬(神医/黑客/玄学/商业/科技),身份曝光逆袭",
    "修仙/系统": "主角获得系统/修仙传承,一路升级打怪,常见:废柴少爷/校园修仙/都市修仙",
    "末日": "末日来临前重生,未卜先知,囤货建基地,常见:丧尸/极寒/洪水",
    "女帝/女强": "女尊/女帝/女强剧,女性逆袭,经济独立,不靠男人",
    "换亲": "换亲/换婚,嫡女换庶女,穿越/重生,身份置换",
    "马甲": "主角多个隐藏身份(医学天才/商业女王/黑客/玄学大师/退隐大佬),装弱打脸",
}

# ============================================================
# 11. 抖音爆款短剧 8 大标准 (爆款公式)
# ============================================================
DOUYIN_HIT_FORMULA = {
    "formula_1_钩子": "前 3 秒钩子,7 秒冲突,15 秒反转,30 秒第一个爽点,60 秒第二个爽点,结尾钩子",
    "formula_2_人物": "扁平化人物 (好/坏清楚, 反派脸谱化), 主角人设快建立 (有鲜明标签)",
    "formula_3_节奏": "3 集一个小反转, 10 集一个大反转, 全剧不超过 100 集",
    "formula_4_对话": "对白 < 12 字/句, 平均 7 字, 用短句制造速度感",
    "formula_5_情绪": "3 大情绪: 爽/虐/甜, 不断切换, 爽 5 虐 3 甜 2 循环",
    "formula_6_付费点": "每 5-8 集设付费点, 关键时刻卡点(揭秘/反转/身份曝光/复仇)",
    "formula_7_平台": "竖屏拍摄, 9:16, 字幕必须, 镜头快切 (1-2 秒/镜)",
    "formula_8_制作": "低成本高节奏, 一天拍 3-5 集, 5-7 天拍完 60 集",
}

# ============================================================
# 12. 角色弧光 7 种类型
# ============================================================
CHARACTER_ARCS = {
    "positive_arc": "正向弧: 主角从缺陷走向圆满(常见:英雄片/成长片)",
    "negative_arc": "负向弧: 主角从圆满走向毁灭(悲剧/反英雄)",
    "flat_arc": "扁平弧: 主角本身不变,但改变世界(漫威式英雄)",
    "corruption_arc": "堕落弧: 主角从善良走向黑暗(黑化片)",
    "redemption_arc": "救赎弧: 主角从罪走向宽恕(救赎片)",
    "testing_arc": "考验弧: 主角坚守本心不被动摇(信仰片)",
    "disillusionment_arc": "觉醒弧: 主角从天真走向现实(青春片)",
}

# ============================================================
# 13. 反 AI 词表升级 (V2) - 加入编剧教学级细节
# ============================================================
# (已在 anti_ai_vocab.py 中,这里只 import 即可)

# ============================================================
# 14. 短剧付费卡点设计
# ============================================================
SHORT_DRAMA_PAYWALL = {
    "paywall_1_reveal": "第一付费卡点: 身份揭秘 (例: 真千金身份, 战神身份, 系统身份)",
    "paywall_2_revenge": "第二付费卡点: 复仇得手 (例: 假千金被揭穿, 渣男后悔, 恶人受罚)",
    "paywall_3_romance": "第三付费卡点: 爱情确认 (例: 总裁告白, 战神归位, 情感爆发)",
    "paywall_4_climax": "第四付费卡点: 终极对决 (例: 大反派对决, 家族揭晓, 系统升级)",
    "interval_rule": "每 5-8 集设一个付费卡点, 卡点时刻: 揭秘/反转/复仇/告白/对决",
}

# ============================================================
# 15. 多线叙事规则 (Multi-thread Narration)
# ============================================================
MULTI_THREAD_RULES = {
    "thread_design": "每条线有一个独立主角,独立欲望,独立冲突,在线索节点处交叉",
    "intersection_points": "交叉点 = 转折点 (3 种): 时间交叉/空间交叉/主题交叉",
    "rhythm_design": "多线节奏: A1→B1→A2→C1→B2→A3→交叉→A4→B3→C2→A5(高潮)→结局",
    "pov_rule": "每线用 POV (主观视角) 推进, 避免全知视角",
    "balance_rule": "主线占 60%, 副线各占 20%, 但高潮时主线要占 80%",
    "convergence_rule": "所有线在 75% 汇合, 最后 25% 一起解决",
}

# ============================================================
# 16. 节奏控制 8 种模式
# ============================================================
PACING_PATTERNS = {
    "constant": "匀速: 适合文艺片/日常片, 永远保持一种节奏",
    "accelerating": "加速: 情节越来越快, 适合惊悚/悬疑",
    "decelerating": "减速: 开局快, 越到后面越慢, 适合成长片",
    "wave": "波浪: 快-慢-快-慢, 适合多线叙事",
    "pulse": "脉冲: 突然加速, 然后慢, 适合戏剧性转折",
    "plateau_cliff": "平台+悬崖: 平稳 60%, 突然剧变, 适合短剧",
    "zigzag": "锯齿: 反复反转, 适合喜剧/短剧",
    "spiral": "螺旋: 同一节奏, 越绕越深, 适合心理片/惊悚片",
}

# ============================================================
# 17. 反转 8 种类型
# ============================================================
REVERSAL_TYPES = {
    "identity_reveal": "身份反转: 主角是反派/反派是主角的亲人/主角是失散多年的",
    "value_reversal": "价值反转: 看似坏人是好人/看似好人是坏人",
    "motive_reversal": "动机反转: 看似为爱其实是复仇/看似为钱其实为爱",
    "event_reversal": "事件反转: 看似失败其实成功/看似成功其实失败",
    "power_reversal": "权力反转: 主角由弱变强/由强变弱",
    "time_reversal": "时间反转: 现在变过去/过去变现在",
    "perception_reversal": "认知反转: 观众以为的真相被推翻",
    "relationship_reversal": "关系反转: 敌人变朋友/朋友变敌人/爱人变仇人",
}

# ============================================================
# 18. 余韵 6 种强度
# ============================================================
AFTERTASTE_LEVELS = {
    "level_1_quick": "淡余韵: 看完就忘, 仅供娱乐, 例: 爆米花商业片",
    "level_2_light": "轻余韵: 看完回味一下, 记得一些片段, 例: 类型片",
    "level_3_medium": "中余韵: 看完会想几天, 例: 优秀剧情片",
    "level_4_heavy": "重余韵: 看完会想几个月, 改变认知, 例: 肖申克/教父",
    "level_5_deep": "深入余韵: 看完改变价值观, 例: 美丽人生/辛德勒名单",
    "level_6_lasting": "永久余韵: 改变一生的认知, 例: 霸王别姬/一一/活着",
}

# ============================================================
# 工具函数: 注入所有理论到 prompt
# ============================================================

def inject_all_theories(director: str = "", include_vertical_drama: bool = True,
                        include_save_the_cat: bool = True,
                        include_hero_journey: bool = True,
                        include_story_circle: bool = True,
                        include_mckee: bool = True,
                        include_three_act: bool = True,
                        include_eight_sequences: bool = True,
                        include_five_act: bool = True,
                        pacing_pattern: str = "pulse",
                        reversal_type: str = "identity_reveal",
                        aftertaste_level: str = "level_4_heavy",
                        character_arc: str = "positive_arc",
                        trope: str = "") -> str:
    """注入所有可用的导演/编剧理论到 prompt"""
    sections = []

    # 1. Save the Cat
    if include_save_the_cat:
        sections.append("【结构 1: Save the Cat 15 拍 (Blake Snyder) - 用于把控全场节奏】")
        for beat, desc in SAVE_THE_CAT_BEATS.items():
            sections.append(f"  {beat}: {desc}")

    # 2. Hero's Journey 12 阶段
    if include_hero_journey:
        sections.append("\n【结构 2: Hero's Journey 12 阶段 (Vogler) - 用于主角弧光】")
        for stage, desc in HERO_JOURNEY_12.items():
            sections.append(f"  {stage}: {desc}")

    # 3. Story Circle
    if include_story_circle:
        sections.append("\n【结构 3: Dan Harmon Story Circle 8 步 - 用于 TV/短剧结构】")
        for step, desc in STORY_CIRCLE_8.items():
            sections.append(f"  {step}: {desc}")

    # 4. McKee
    if include_mckee:
        sections.append("\n【结构 4: Robert McKee 故事 7 大原则 - 用于故事价值】")
        for k, v in MCKEE_PRINCIPLES.items():
            sections.append(f"  {k}: {v}")

    # 5. 三幕剧
    if include_three_act:
        sections.append("\n【结构 5: Syd Field 三幕剧 Paradigm - 用于电影/剧集】")
        for k, v in THREE_ACT_PARADIGM.items():
            sections.append(f"  {k}: {v}")

    # 6. 8 Sequences
    if include_eight_sequences:
        sections.append("\n【结构 6: Frank Daniel 8 Sequences - 用于中长篇】")
        for k, v in EIGHT_SEQUENCES.items():
            sections.append(f"  {k}: {v}")

    # 7. 五幕剧
    if include_five_act:
        sections.append("\n【结构 7: 五幕结构 (Aristotle/Freytag) - 用于经典剧】")
        for k, v in FIVE_ACT_STRUCTURE.items():
            sections.append(f"  {k}: {v}")

    # 8. 垂直短剧
    if include_vertical_drama:
        sections.append("\n【结构 8: 新媒体短剧三秒铁律 (ReelShort/DramaBox) - 1-2 分钟短剧】")
        for k, v in SHORT_DRAMA_RULES.items():
            sections.append(f"  {k}: {v}")
        sections.append("\n  【短剧爆款 8 大公式】")
        for k, v in DOUYIN_HIT_FORMULA.items():
            sections.append(f"  {k}: {v}")
        sections.append("\n  【抖音短剧 6+ 大套路】")
        for k, v in DOUYIN_TROPES.items():
            sections.append(f"  {k}: {v[:80]}...")

    # 9. 节奏
    if pacing_pattern:
        sections.append(f"\n【节奏模式: {pacing_pattern}】")
        if pacing_pattern in PACING_PATTERNS:
            sections.append(f"  {PACING_PATTERNS[pacing_pattern]}")

    # 10. 反转
    if reversal_type:
        sections.append(f"\n【反转类型: {reversal_type}】")
        if reversal_type in REVERSAL_TYPES:
            sections.append(f"  {REVERSAL_TYPES[reversal_type]}")

    # 11. 余韵
    if aftertaste_level:
        sections.append(f"\n【余韵强度: {aftertaste_level}】")
        if aftertaste_level in AFTERTASTE_LEVELS:
            sections.append(f"  {AFTERTASTE_LEVELS[aftertaste_level]}")

    # 12. 角色弧
    if character_arc:
        sections.append(f"\n【角色弧: {character_arc}】")
        if character_arc in CHARACTER_ARCS:
            sections.append(f"  {CHARACTER_ARCS[character_arc]}")

    return "\n".join(sections)


# ============================================================
# 数据完整性验证
# ============================================================
if __name__ == "__main__":
    print(f"=== Director Mastery V2 ===")
    print(f"Save the Cat beats: {len(SAVE_THE_CAT_BEATS)}")
    print(f"Hero's Journey 17 阶段: {len(HERO_JOURNEY_17)}")
    print(f"Hero's Journey 12 阶段: {len(HERO_JOURNEY_12)}")
    print(f"Story Circle 8 步: {len(STORY_CIRCLE_8)}")
    print(f"McKee 7 原则: {len(MCKEE_PRINCIPLES)}")
    print(f"三幕剧 8 段: {len(THREE_ACT_PARADIGM)}")
    print(f"8 Sequences: {len(EIGHT_SEQUENCES)}")
    print(f"五幕剧 5 段: {len(FIVE_ACT_STRUCTURE)}")
    print(f"短剧规则 6 条: {len(SHORT_DRAMA_RULES)}")
    print(f"抖音套路 10+ 类: {len(DOUYIN_TROPES)}")
    print(f"爆款公式 8 条: {len(DOUYIN_HIT_FORMULA)}")
    print(f"角色弧 7 种: {len(CHARACTER_ARCS)}")
    print(f"付费卡点 5 类: {len(SHORT_DRAMA_PAYWALL)}")
    print(f"多线规则 6 条: {len(MULTI_THREAD_RULES)}")
    print(f"节奏模式 8 种: {len(PACING_PATTERNS)}")
    print(f"反转类型 8 种: {len(REVERSAL_TYPES)}")
    print(f"余韵强度 6 级: {len(AFTERTASTE_LEVELS)}")
    print()
    # 测试 inject_all_theories
    print("=== 测试注入所有理论 ===")
    full = inject_all_theories(director="王家卫", pacing_pattern="pulse",
                                reversal_type="identity_reveal",
                                aftertaste_level="level_4_heavy",
                                character_arc="positive_arc",
                                trope="穿越")
    print(f"注入 prompt 长度: {len(full)} 字符")
    print(f"前 500 字符预览:")
    print(full[:500])
