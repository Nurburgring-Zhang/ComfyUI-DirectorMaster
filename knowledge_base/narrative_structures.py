# ============================================================
# 叙事结构知识库 — 50+种经过验证的故事模式
# 来源：IMDB Top 250叙事分析 + 剧作理论 + 短剧爆款模式
# ============================================================

NARRATIVE_STRUCTURES = {
    "classic_three_act": {
        "cn": "经典三幕式",
        "description": "设置-对抗-解决，最经典的故事结构",
        "beat_map": [
            {"position": 0.0, "beat": "开场", "function": "建立世界观和主角日常"},
            {"position": 0.10, "beat": "触发事件", "function": "打破日常的事件发生"},
            {"position": 0.25, "beat": "第一转折点", "function": "主角决定踏上旅程/接受挑战"},
            {"position": 0.35, "beat": "上升行动", "function": "遇到困难并努力克服"},
            {"position": 0.50, "beat": "中点", "function": "假胜利或假失败，提高赌注"},
            {"position": 0.62, "beat": "困境加深", "function": "更大的障碍出现"},
            {"position": 0.75, "beat": "第二转折点/最低点", "function": "一切似乎失败，黑暗时刻"},
            {"position": 0.85, "beat": "高潮", "function": "最终对决/最大冲突"},
            {"position": 0.95, "beat": "结局", "function": "新的平衡/变化后的日常"},
        ],
        "emotion_curve": "平稳→好奇→紧张→希望→震惊→绝望→释放→温暖",
        "examples": ["《肖申克的救赎》", "《阿甘正传》", "大部分好莱坞主流电影"],
    },

    "hero_journey": {
        "cn": "英雄之旅",
        "description": "Joseph Campbell的单一神话结构",
        "beat_map": [
            {"position": 0.0, "beat": "普通世界", "function": "展示英雄的日常生活"},
            {"position": 0.08, "beat": "冒险召唤", "function": "使命/机会出现"},
            {"position": 0.12, "beat": "拒绝召唤", "function": "英雄的犹豫和恐惧"},
            {"position": 0.17, "beat": "遇见导师", "function": "获得指导和工具"},
            {"position": 0.25, "beat": "跨越门槛", "function": "进入新世界"},
            {"position": 0.35, "beat": "考验/盟友/敌人", "function": "面对挑战和建立关系"},
            {"position": 0.50, "beat": "逼近洞穴", "function": "接近最大恐惧"},
            {"position": 0.60, "beat": "磨难", "function": "面对死亡/最大考验"},
            {"position": 0.70, "beat": "奖赏", "function": "获得宝物/能力/真相"},
            {"position": 0.80, "beat": "返程", "function": "带着奖赏回归"},
            {"position": 0.90, "beat": "复活", "function": "最后的考验/牺牲"},
            {"position": 0.95, "beat": "带着万灵药归来", "function": "变化的英雄回到日常"},
        ],
        "emotion_curve": "安定→好奇→恐惧→信心→兴奋→绝望→重生→释放→圆满",
        "examples": ["《星球大战》", "《指环王》", "《黑客帝国》", "《狮子王》"],
    },

    "save_the_cat": {
        "cn": "救猫咪节拍表(Blake Snyder)",
        "description": "好莱坞最流行的15节拍剧本结构",
        "beat_map": [
            {"position": 0.0, "beat": "开场画面", "function": "视觉隐喻暗示主题"},
            {"position": 0.05, "beat": "主题陈述", "function": "有人说出主题（主角不自知）"},
            {"position": 0.08, "beat": "铺垫", "function": "主角的世界/缺陷/愿望"},
            {"position": 0.10, "beat": "催化剂", "function": "改变一切的事件"},
            {"position": 0.15, "beat": "辩论", "function": "主角犹豫是否行动"},
            {"position": 0.20, "beat": "进入第二幕", "function": "主角做出决定"},
            {"position": 0.30, "beat": "B故事", "function": "副线（通常是爱情线）"},
            {"position": 0.37, "beat": "欢乐游戏", "function": "享受新世界/新能力"},
            {"position": 0.50, "beat": "中点", "function": "假胜利或假失败"},
            {"position": 0.55, "beat": "坏人逼近", "function": "反面力量反扑"},
            {"position": 0.62, "beat": "一无所有", "function": "失去一切"},
            {"position": 0.68, "beat": "黑暗之夜", "function": "最低谷/灵魂拷问"},
            {"position": 0.75, "beat": "进入第三幕", "function": "找到解决方案"},
            {"position": 0.85, "beat": "结局", "function": "解决冲突"},
            {"position": 0.95, "beat": "结尾画面", "function": "与开场对应的变化画面"},
        ],
        "emotion_curve": "平稳→期待→犹豫→兴奋→危机→绝望→顿悟→释放",
    },

    "kishōtenketsu": {
        "cn": "起承转合(东方叙事)",
        "description": "日本/中国/韩国传统四段叙事结构",
        "beat_map": [
            {"position": 0.0, "beat": "起(Ki)", "function": "引入角色和情境，无冲突"},
            {"position": 0.25, "beat": "承(Shō)", "function": "发展引入的元素"},
            {"position": 0.50, "beat": "转(Ten)", "function": "出人意料的转折（非冲突）"},
            {"position": 0.75, "beat": "合(Ketsu)", "function": "将转折与前文统一"},
        ],
        "emotion_curve": "平和→沉浸→惊奇→回味",
        "examples": ["宫崎骏动画", "是枝裕和电影", "小津安二郎"],
    },

    "in_medias_res": {
        "cn": "倒叙/从中间开始",
        "description": "直接从高潮/紧张时刻开始，再回溯",
        "beat_map": [
            {"position": 0.0, "beat": "高潮片段", "function": "用最紧张的场面抓住观众"},
            {"position": 0.10, "beat": "时间回溯标记", "function": "XX小时/天前"},
            {"position": 0.15, "beat": "日常建立", "function": "回到故事真正的开始"},
            {"position": 0.50, "beat": "走向已知的结果", "function": "观众知道终点,体验过程"},
            {"position": 0.85, "beat": "回到开场时刻", "function": "追上时间线"},
            {"position": 0.95, "beat": "超越已知", "function": "揭示开场未展示的后续"},
        ],
        "emotion_curve": "震惊→好奇→渐进→紧张→恍然→释放",
        "examples": ["《搏击俱乐部》", "《低俗小说》", "短剧热门开头"],
    },

    "nonlinear": {
        "cn": "非线性叙事",
        "description": "打乱时间线，通过碎片拼贴还原真相",
        "beat_map": [
            {"position": 0.0, "beat": "碎片A", "function": "某个时间点的事件片段"},
            {"position": 0.15, "beat": "碎片B", "function": "不同时间点的另一视角"},
            {"position": 0.30, "beat": "连接线索", "function": "观众开始发现碎片关联"},
            {"position": 0.50, "beat": "核心碎片", "function": "关键事件的一面"},
            {"position": 0.70, "beat": "视角切换", "function": "同一事件的另一面"},
            {"position": 0.85, "beat": "拼图完成", "function": "所有碎片合为全貌"},
            {"position": 0.95, "beat": "重新理解", "function": "回顾片段时有新含义"},
        ],
        "emotion_curve": "迷惑→好奇→渐悟→震惊→恍然→回味",
        "examples": ["《低俗小说》", "《记忆碎片》", "《敦刻尔克》"],
    },

    "short_drama_hook": {
        "cn": "短剧钩子结构(爆款模式)",
        "description": "专为竖屏短剧设计，3秒抓人+每15秒反转",
        "beat_map": [
            {"position": 0.0, "beat": "视觉钩子", "function": "3秒内的感官冲击/悬念"},
            {"position": 0.05, "beat": "人物困境建立", "function": "主角的处境(弱势/被欺)"},
            {"position": 0.15, "beat": "第一个反转", "function": "打脸/逆袭的第一步"},
            {"position": 0.30, "beat": "升级冲突", "function": "反派加大力度"},
            {"position": 0.45, "beat": "第二个反转", "function": "更大的逆袭/真相揭露"},
            {"position": 0.60, "beat": "情绪高潮", "function": "爽点/虐点的极致"},
            {"position": 0.75, "beat": "第三个反转", "function": "反套路/超预期发展"},
            {"position": 0.90, "beat": "悬崖挂钩", "function": "未解决的悬念引导下一集"},
        ],
        "emotion_curve": "震惊→心疼→爽快→紧张→更爽→悬念",
        "examples": ["《闪婚后傅先生马甲藏不住了》", "《黑莲花上位手册》"],
    },

    "mystery_reveal": {
        "cn": "悬疑揭秘结构",
        "description": "层层剥洋葱式的真相揭露",
        "beat_map": [
            {"position": 0.0, "beat": "谜面呈现", "function": "不可能的事件/死亡/消失"},
            {"position": 0.10, "beat": "表面解释", "function": "看似合理的第一个答案"},
            {"position": 0.20, "beat": "矛盾出现", "function": "第一个答案被推翻"},
            {"position": 0.35, "beat": "深入调查", "function": "发现隐藏的层面"},
            {"position": 0.50, "beat": "误导高潮", "function": "以为找到了真凶"},
            {"position": 0.60, "beat": "第二次推翻", "function": "新证据推翻一切"},
            {"position": 0.75, "beat": "关键线索", "function": "被忽略的细节成为钥匙"},
            {"position": 0.85, "beat": "真相揭示", "function": "完整真相水落石出"},
            {"position": 0.95, "beat": "意外余波", "function": "真相带来的连锁影响"},
        ],
        "emotion_curve": "好奇→以为懂了→困惑→紧张→震惊→冰冷→恍然→回味",
        "examples": ["《看不见的客人》", "《利刃出鞘》", "《消失的她》"],
    },

    "parallel_convergence": {
        "cn": "平行交汇结构",
        "description": "多条平行线最终交汇在同一时刻",
        "beat_map": [
            {"position": 0.0, "beat": "线索A开始", "function": "第一条故事线建立"},
            {"position": 0.10, "beat": "线索B开始", "function": "第二条故事线建立"},
            {"position": 0.20, "beat": "线索C开始", "function": "第三条故事线(可选)"},
            {"position": 0.40, "beat": "微妙联系", "function": "线索间出现隐约关联"},
            {"position": 0.60, "beat": "加速推进", "function": "各线索同时升温"},
            {"position": 0.80, "beat": "交汇碰撞", "function": "所有线索在同一事件中汇合"},
            {"position": 0.90, "beat": "连锁反应", "function": "汇合后产生更大影响"},
            {"position": 0.95, "beat": "统一收束", "function": "各线索获得共同的意义"},
        ],
        "emotion_curve": "分散注意→逐渐好奇→紧张→震撼→感慨",
        "examples": ["《通天塔》", "《撞车》", "《敦刻尔克》三条时间线"],
    },

    "emotional_rollercoaster": {
        "cn": "情绪过山车(短剧/短视频专用)",
        "description": "每30秒一个情绪拐点，持续刺激多巴胺",
        "beat_map": [
            {"position": 0.0, "beat": "冲击开场", "function": "直接进入情绪高点"},
            {"position": 0.08, "beat": "急速下降", "function": "情绪突然翻转"},
            {"position": 0.20, "beat": "缓冲积蓄", "function": "短暂喘息积蓄下一波"},
            {"position": 0.30, "beat": "第二波冲击", "function": "比第一波更强的情绪"},
            {"position": 0.45, "beat": "虐心低谷", "function": "最虐/最痛的瞬间"},
            {"position": 0.55, "beat": "曙光初现", "function": "一点点希望"},
            {"position": 0.70, "beat": "逆转爆发", "function": "全面反转/逆袭"},
            {"position": 0.85, "beat": "极致满足", "function": "最爽/最甜/最感动"},
            {"position": 0.95, "beat": "留余钩子", "function": "一个未解悬念"},
        ],
        "emotion_curve": "震惊→心痛→喘息→更痛→绝望→希望→狂喜→悬念",
    },

    "buildup_payoff": {
        "cn": "伏笔-回收结构",
        "description": "前半段埋设细节，后半段全部回收形成震撼",
        "beat_map": [
            {"position": 0.0, "beat": "看似无关细节A", "function": "自然地展示某个物品/台词"},
            {"position": 0.10, "beat": "看似无关细节B", "function": "另一个容易被忽略的元素"},
            {"position": 0.20, "beat": "看似无关细节C", "function": "第三个隐藏的伏笔"},
            {"position": 0.30, "beat": "正常推进", "function": "故事按预期发展"},
            {"position": 0.50, "beat": "第一个回收", "function": "细节A的真实含义揭示"},
            {"position": 0.65, "beat": "第二个回收", "function": "细节B连锁揭示"},
            {"position": 0.80, "beat": "全面回收", "function": "所有伏笔同时生效"},
            {"position": 0.95, "beat": "回顾性领悟", "function": "观众重新理解整个故事"},
        ],
        "emotion_curve": "平淡→日常→正常→惊讶→震撼→狂喜→回味",
        "examples": ["《看不见的客人》", "《第六感》", "《禁闭岛》"],
    },

    "descent_redemption": {
        "cn": "沉沦-救赎结构",
        "description": "角色从高处跌落再获得救赎，最具情感张力",
        "beat_map": [
            {"position": 0.0, "beat": "巅峰时刻", "function": "展示角色最好的状态"},
            {"position": 0.15, "beat": "裂缝出现", "function": "隐患/弱点/诱惑浮现"},
            {"position": 0.25, "beat": "第一次跌落", "function": "做出错误选择"},
            {"position": 0.40, "beat": "持续下沉", "function": "越陷越深"},
            {"position": 0.55, "beat": "彻底沉沦", "function": "最黑暗的时刻"},
            {"position": 0.65, "beat": "触底反弹", "function": "在深渊中看到一束光"},
            {"position": 0.75, "beat": "艰难回升", "function": "不是一帆风顺的回归"},
            {"position": 0.85, "beat": "代价之重", "function": "救赎是有代价的"},
            {"position": 0.95, "beat": "不同的重生", "function": "回不到从前但获得新生"},
        ],
        "emotion_curve": "欣赏→不安→痛心→绝望→怜悯→希望→感动→释然",
        "examples": ["《肖申克的救赎》", "《角斗士》", "《摔跤吧爸爸》"],
    },
}

# ============================================================
# 短剧专用的微叙事结构（30秒-3分钟每集）
# ============================================================
SHORT_FORM_STRUCTURES = {
    "golden_3_seconds": {
        "cn": "黄金3秒法则",
        "techniques": [
            "反物理/超现实画面开场（物品悬浮/时间冻结）",
            "强烈情绪面部特写（愤怒/哭泣/震惊）",
            "中间状态入场（正在跑/正在打/正在跳）",
            "信息缺口（说一半的话/未完成的动作）",
            "视觉反差（衣着vs环境/表情vs动作）",
            "声音先行（画面延迟0.5秒出现）",
            "文字悬念（画面+一行神秘文字）",
        ],
    },
    "15_second_reversal": {
        "cn": "15秒反转节奏",
        "structure": "建立预期(5s) → 打破预期(5s) → 新的悬念(5s)",
        "reversal_types": [
            "身份反转（乞丐是总裁/清洁工是天才）",
            "情感反转（恨→爱/信任→背叛/放弃→坚持）",
            "权力反转（弱者翻身/强者跌落）",
            "认知反转（以为是A其实是B）",
            "时空反转（今天的决定来自未来的信息）",
        ],
    },
    "emotional_cliff": {
        "cn": "情绪断崖法则",
        "rule": "同一情绪状态不超过3秒就必须变化",
        "transitions": [
            "笑→突然变脸(内心痛苦)",
            "哭→突然止泪(做出决定)",
            "怒→突然笑(阴险/看开)",
            "甜→突然冷(发现真相)",
            "恐→突然静(接受命运)",
        ],
    },
    "cliffhanger_types": {
        "cn": "悬崖挂钩类型",
        "types": [
            "话说一半被打断（'其实你的身份是——' 画面黑）",
            "动作未完成（手伸向按钮/门即将打开）",
            "新角色出现（影子/脚步声/熟悉的声音）",
            "真相未揭（看到了照片但没给观众看内容）",
            "选择未决（两条路/两个人/两个选项）",
            "时间压力（倒计时中突然停电/故障）",
        ],
    },
}


# ============================================================
# 叙事结构决策覆盖层 V1.0 — 为每个结构补7维决策字段
# (保留原beat_map/emotion_curve, 此层叠加trigger/rationale/failure/measurement/alternatives/cross_refs)
# 引擎合并使用: NARRATIVE_STRUCTURES[key] + NARRATIVE_DECISION[key]
# ============================================================
NARRATIVE_DECISION = {
    "classic_three_act": {
        "trigger": "主流商业片/院线/不确定用什么结构时的安全默认",
        "rationale": "三幕=设置-对抗-解决, 最符合观众预期管理。中点假胜利/假失败是张力引擎。",
        "failure_modes": ["中点落在60%而非50%=后半拖沓", "第二幕过长=中段 sag", "高潮无前置铺垫=突兀"],
        "measurement": "观众应感到'设置→对抗→解决'的完整弧线, 中点有转折",
        "alternatives": ["save_the_cat(更精确节拍)", "hero_journey(更神话化)"],
        "cross_refs": {"genre": "通用商业片", "pacing": "中点须有假胜利/假失败", "emotion": "中点情绪须反转"},
    },
    "hero_journey": {
        "trigger": "英雄成长/神话史诗/奇幻冒险/主角有明显弧光的成长故事",
        "rationale": "Campbell单一神话=跨越门槛→考验→奖赏→返程→复活, 是成长弧线的最完整模板。",
        "failure_modes": ["拒绝召唤过久=开场拖", "复活(最终考验)缺失=弧线不完整", "奖赏无代价=廉价"],
        "measurement": "主角应有完整弧线: 普通→跨越→考验→奖赏→复活→归来",
        "alternatives": ["save_the_cat(更商业节拍)", "classic_three_act(更简洁)"],
        "cross_refs": {"genre": "奇幻/冒险/神话标配", "character_arc": "正向弧光标配", "director": "Spielberg/Guillermo偏好"},
    },
    "save_the_cat": {
        "trigger": "好莱坞商业主流/需要精确到分钟的节拍/类型片标配",
        "rationale": "Blake Snyder 15节拍=精确到位置%, 是好莱坞编剧的最通用工具。'救猫咪'=开场让观众在乎主角。",
        "failure_modes": ["节拍位置算错=节奏崩", "B故事(副线)缺失=情感单薄", "黑暗之夜过短=高潮无重量"],
        "measurement": "15节拍各落在正确位置%, 中点有假胜利/假失败, 黑暗之夜有灵魂拷问",
        "alternatives": ["classic_three_act(更简)", "hero_journey(更神话)"],
        "cross_refs": {"genre": "商业主流/类型片标配", "pacing": "节拍位置精确", "screenwriting": "好莱坞标配"},
    },
    "kishōtenketsu": {
        "trigger": "东方文艺/宫崎骏/是枝裕和/小津/无冲突叙事/诗性",
        "rationale": "起承转合=引入→发展→转折(非冲突)→统一。东方叙事不需要冲突, 靠'转'制造惊奇。",
        "failure_modes": ["强加冲突=破坏东方诗性", "'转'无惊奇=失力量", "用于商业片=节奏过慢"],
        "measurement": "观众应感到'引入→发展→惊奇转折→统一', 而非冲突驱动",
        "alternatives": ["classic_three_act(更冲突驱动)", "emotional_rollercoaster(更情绪)"],
        "cross_refs": {"genre": "东方文艺/日常/动画标配", "director": "宫崎骏/小津/是枝裕和偏好", "conflict": "无冲突叙事"},
    },
    "in_medias_res": {
        "trigger": "冷开场/倒叙/悬疑/短剧爆款开头/需要立刻抓住观众",
        "rationale": "从高潮中间开始=立刻抓住观众, 再回溯。是悬疑与短剧的核心开场工具。",
        "failure_modes": ["回溯段过长=观众失去耐心", "开场与回溯无逻辑=混乱", "无时间标记=观众迷糊"],
        "measurement": "观众应被开场抓住, 回溯清晰, 追上时间线后有新揭示",
        "alternatives": ["nonlinear(更碎片)", "classic_three_act(更线性)"],
        "cross_refs": {"genre": "悬疑/短剧标配", "pacing": "前3秒抓住观众", "short_drama": "短剧爆款开头核心"},
    },
    "nonlinear": {
        "trigger": "记忆/真相拼贴/塔伦蒂诺/诺兰/多视角还原/主题深化",
        "rationale": "打乱时间线=让观众主动拼贴真相, 增加参与感。结构本身成为主题。",
        "failure_modes": ["碎片无关联=混乱", "时间标记不清=观众迷失", "为非线性而非线性=炫技"],
        "measurement": "观众应能拼出全貌, 回顾时碎片有新含义",
        "alternatives": ["in_medias_res(更集中倒叙)", "parallel_convergence(更多线)"],
        "cross_refs": {"genre": "悬疑/犯罪/文艺标配", "director": "Tarantino/Nolan偏好", "pacing": "需观众主动拼贴"},
    },
    "short_drama_hook": {
        "trigger": "竖屏短剧/3秒抓人/每15秒反转/爆款节奏",
        "rationale": "短剧=注意力经济, 3秒钩子+15秒反转是完播率引擎。压得越深弹得越高。",
        "failure_modes": ["前3秒无冲击=70%划走", "反转间隔>20秒=流失", "无悬崖结尾=不关注下一集"],
        "measurement": "前3秒抓人, 每15秒一反转, 结尾悬崖挂钩, 完播率达标",
        "alternatives": ["emotional_rollercoaster(更情绪)", "in_medias_res(更倒叙)"],
        "cross_refs": {"genre": "短剧标配", "pacing": "3秒钩子+15秒反转", "vertical": "竖屏完播率", "platform": "抖音/快手算法"},
    },
    "mystery_reveal": {
        "trigger": "悬疑揭秘/层层剥洋葱/真相揭露/不可靠叙述",
        "rationale": "谜面→误导→推翻→真相=层层揭示, 每次推翻提高赌注。是悬疑片核心结构。",
        "failure_modes": ["真相无前置铺垫=生硬(契诃夫之枪)", "误导过多=观众放弃", "真相冲击<谜面印象=失望"],
        "measurement": "真相须有2-3次前置铺垫, 每次推翻有逻辑, 最终真相震撼",
        "alternatives": ["buildup_payoff(更伏笔)", "nonlinear(更碎片)"],
        "cross_refs": {"genre": "悬疑标配", "director": "Hitchcock/Fincher偏好", "foreshadow": "契诃夫之枪核心"},
    },
    "parallel_convergence": {
        "trigger": "多线交织/《通天塔》/《撞车》/《敦刻尔克》/命运交汇",
        "rationale": "多条平行线最终交汇=命运交织感。各线微妙联系→加速→交汇碰撞=震撼。",
        "failure_modes": ["线索无关联=失交汇价值", "线索过多=观众迷失", "交汇过晚=前段拖"],
        "measurement": "各线有微妙联系, 加速推进, 交汇碰撞产生连锁反应",
        "alternatives": ["nonlinear(更碎片)", "in_medias_res(更集中)"],
        "cross_refs": {"genre": "史诗/多线叙事标配", "director": "Iñárritu/Nolan偏好", "pacing": "各线须同时升温"},
    },
    "emotional_rollercoaster": {
        "trigger": "短剧/短视频情绪向/每30秒拐点/多巴胺循环",
        "rationale": "每30秒情绪拐点=持续刺激多巴胺, 不让情绪平。是短视频情绪向核心。",
        "failure_modes": ["情绪拐点间隔过长=流失", "同一情绪水平重复=脱敏", "无最低谷=高潮无重量"],
        "measurement": "每30秒有情绪拐点, 高低交替幅度递增, 持续刺激不脱敏",
        "alternatives": ["short_drama_hook(更反转)", "oscillation(更震荡)"],
        "cross_refs": {"genre": "短视频/情绪向标配", "pacing": "30秒拐点", "emotion": "曲线幅度递增"},
    },
    "buildup_payoff": {
        "trigger": "伏笔密集回收/《看不见的客人》/《第六感》/真相震撼型",
        "rationale": "前半埋细节, 后半全部回收=回顾性领悟。回收冲击>埋设印象=震撼。",
        "failure_modes": ["埋了不回=悬置", "回收冲击<埋设印象=失望", "太快回收=无悬念"],
        "measurement": "重要回收须有2-3次铺垫, 回收冲击>埋设, 观众回顾有新含义",
        "alternatives": ["mystery_reveal(更悬疑)", "nonlinear(更碎片)"],
        "cross_refs": {"genre": "悬疑/反转片标配", "foreshadow": "伏笔回收核心", "pacing": "前半埋后半收"},
    },
    "descent_redemption": {
        "trigger": "沉沦救赎/《肖申克》/《角斗士》/悲剧后有光/角色从高处坠落再回升",
        "rationale": "巅峰→裂缝→沉沦→触底→艰难回升→代价重生=最有情感张力的弧线。",
        "failure_modes": ["触底后回升过快=廉价救赎", "无代价=失重量", "沉沦无前置巅峰=失对照"],
        "measurement": "有巅峰前置, 沉沦到触底, 艰难回升(非一帆风顺), 救赎有代价",
        "alternatives": ["hero_journey(更正向)", "classic_three_act(更简)"],
        "cross_refs": {"genre": "剧情/传记标配", "character_arc": "沉沦救赎弧光", "emotion": "descent曲线"},
    },
    # ─── 短剧微叙事结构决策 ───
    "golden_3_seconds": {
        "trigger": "短剧/短视频开场/前3秒抓人/完播率决定生死",
        "rationale": "前3秒=70%观众去留决定。视觉冲击/信息缺口/情绪炸弹=抓住本能反应。",
        "failure_modes": ["前3秒无冲击=划走", "钩子与主题无关=欺诈感", "钩子过强后续接不住=完播崩"],
        "measurement": "前3秒有视觉/情绪/信息冲击, 与主题相关, 抓住70%+观众",
        "alternatives": ["in_medias_res(更叙事)", "emotional_bomb(更情绪)"],
        "cross_refs": {"pacing": "3秒生死线", "platform": "抖音/快手算法权重", "short_drama": "开场核心"},
    },
    "15_second_reversal": {
        "trigger": "短剧节奏锚点/每15秒一反转/持续刺激",
        "rationale": "15秒反转=持续打破预期, 不让观众习惯。是短剧留存的核心节奏。",
        "failure_modes": ["反转间隔>20秒=流失", "反转无升级=疲劳", "反转无逻辑=生硬"],
        "measurement": "每15秒有反转, 反转级别递增, 持续打破预期",
        "alternatives": ["emotional_rollercoaster(更情绪)", "short_drama_hook(更钩子)"],
        "cross_refs": {"pacing": "15秒反转锚点", "short_drama": "留存核心", "reversal": "身份/情感/权力/认知反转"},
    },
    "emotional_cliff": {
        "trigger": "短剧情绪管理/同一情绪不超3秒/情绪断崖",
        "rationale": "同一情绪不超3秒=持续变化, 不让观众习惯。情绪断崖=笑变哭/怒变笑的瞬间翻转。",
        "failure_modes": ["同一情绪停留>3秒=疲劳", "情绪翻转无逻辑=生硬", "翻转过频=混乱"],
        "measurement": "情绪每3秒有变化, 翻转有逻辑, 持续变化不脱敏",
        "alternatives": ["emotional_rollercoaster(更广义)", "15_second_reversal(更反转)"],
        "cross_refs": {"pacing": "3秒情绪变化", "emotion": "断崖翻转", "performance": "微表情瞬间翻转"},
    },
    "cliffhanger_types": {
        "trigger": "短剧结尾/未解决悬念/引导关注下一集/留存转化",
        "rationale": "结尾不解决=观众追下一集。话说一半/动作未完成/新威胁入场=悬念挂钩。",
        "failure_modes": ["悬念过弱=不追更", "悬念与主线无关=欺诈", "悬念无后续回收=失信"],
        "measurement": "结尾有未解决悬念, 与主线相关, 引导追下一集",
        "alternatives": ["buildup_payoff(更伏笔)", "short_drama_hook(更开场)"],
        "cross_refs": {"pacing": "结尾挂钩", "retention": "关注转化核心", "short_drama": "留存转化"},
    },
}


def get_structure_with_decision(struct_key):
    """合并叙事结构基础信息 + 决策覆盖层(引擎调用)"""
    base = NARRATIVE_STRUCTURES.get(struct_key, {})
    decision = NARRATIVE_DECISION.get(struct_key, {})
    merged = dict(base)
    merged.update(decision)
    return merged


def get_short_form_with_decision(struct_key):
    """合并短剧微叙事结构 + 决策覆盖层"""
    base = SHORT_FORM_STRUCTURES.get(struct_key, {})
    decision = NARRATIVE_DECISION.get(struct_key, {})
    merged = dict(base)
    merged.update(decision)
    return merged

