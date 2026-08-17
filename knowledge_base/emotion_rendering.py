# ============================================================
# 情感渲染与情绪曲线知识库
# 来源：剧作理论 + 心理学 + IMDB Top 250情感架构分析
# ============================================================

EMOTION_RENDERING = {
    "emotion_spectrum": {
        "primary_emotions": {
            "joy": {
                "cn": "喜悦",
                "intensity_levels": [
                    {"level": 0.2, "cn": "微微愉悦", "visual": "嘴角微扬,眼底有光,动作轻快"},
                    {"level": 0.4, "cn": "开心", "visual": "笑容绽放,身体舒展,语调上扬"},
                    {"level": 0.6, "cn": "欢喜", "visual": "眼角皱纹加深,身体微微弹跳,手势打开"},
                    {"level": 0.8, "cn": "狂喜", "visual": "仰头大笑,手舞足蹈,泪光闪烁(喜极而泣)"},
                    {"level": 1.0, "cn": "极乐/感动到无法言语", "visual": "静止、发呆、泪流满面但在笑,全身颤抖"},
                ],
                "camera_response": "缓推面部→环绕→拉开展示世界的美好",
                "lighting_response": "渐暖、渐亮、增加柔光",
                "pacing_response": "逐渐加快→高点慢放→恢复",
            },
            "sadness": {
                "cn": "悲伤",
                "intensity_levels": [
                    {"level": 0.2, "cn": "惆怅", "visual": "目光出神,手无意识抚摸某物,轻叹"},
                    {"level": 0.4, "cn": "难过", "visual": "低头避开目光,嘴角下坠,步伐变慢"},
                    {"level": 0.6, "cn": "伤心", "visual": "眼眶泛红,声音颤抖,身体蜷缩"},
                    {"level": 0.8, "cn": "痛哭", "visual": "泪流满面,身体抽搐,双手掩面或握拳"},
                    {"level": 1.0, "cn": "崩溃/哀嚎", "visual": "跪地/瘫倒,发出破碎的声音,或完全失声无泪"},
                ],
                "camera_response": "缓推特写→固定凝视(不切开给观众消化空间)→缓拉",
                "lighting_response": "渐冷、渐暗、光源收缩至单点",
                "pacing_response": "逐渐减慢→最痛点延长(时间仿佛停止)→慢慢恢复",
            },
            "anger": {
                "cn": "愤怒",
                "intensity_levels": [
                    {"level": 0.2, "cn": "不悦", "visual": "抿唇,目光稍冷,手指轻叩"},
                    {"level": 0.4, "cn": "恼怒", "visual": "眉头紧锁,语气变硬,动作变僵"},
                    {"level": 0.6, "cn": "愤怒", "visual": "咬牙切齿,握拳,声音提高"},
                    {"level": 0.8, "cn": "暴怒", "visual": "拍桌/摔物,面部扭曲,血管凸起"},
                    {"level": 1.0, "cn": "狂怒/失控", "visual": "破坏一切或反而极度安静(暴风雨前的平静)"},
                ],
                "camera_response": "急推特写→手持晃动→快切多角度→极特写瞳孔",
                "lighting_response": "对比加强、红色渗入、阴影加深",
                "pacing_response": "积蓄期极慢→爆发期极快→余波静默",
            },
            "fear": {
                "cn": "恐惧",
                "intensity_levels": [
                    {"level": 0.2, "cn": "不安", "visual": "频繁环顾,手不自觉握紧物品,呼吸变浅"},
                    {"level": 0.4, "cn": "紧张", "visual": "身体僵硬,吞咽动作,手心出汗"},
                    {"level": 0.6, "cn": "恐惧", "visual": "瞳孔放大,后退,手颤抖"},
                    {"level": 0.8, "cn": "惊恐", "visual": "尖叫/失声,身体冻结或狂奔"},
                    {"level": 1.0, "cn": "极度恐惧/癫狂", "visual": "精神崩溃,笑出来,或完全石化瞳孔涣散"},
                ],
                "camera_response": "POV不稳定→快速推拉(呼吸感)→突然定格",
                "lighting_response": "暗部增大、光源不稳定(闪烁)、冷色",
                "pacing_response": "逐渐加快心跳节奏→突然停止(最恐怖的一刻是安静的)",
            },
            "love": {
                "cn": "爱/心动",
                "intensity_levels": [
                    {"level": 0.2, "cn": "好感", "visual": "目光不自觉跟随,嘴角微翘,动作变轻柔"},
                    {"level": 0.4, "cn": "心动", "visual": "呼吸加快,脸红,目光交汇后躲闪"},
                    {"level": 0.6, "cn": "深情", "visual": "目光温柔不移,微笑到眼角,手轻触对方"},
                    {"level": 0.8, "cn": "热恋", "visual": "一切围绕对方转,世界虚化只有TA清晰"},
                    {"level": 1.0, "cn": "至爱/牺牲", "visual": "平静的坚定,为对方做出最大牺牲时反而微笑"},
                ],
                "camera_response": "缓慢环绕两人→景深极浅只有彼此清晰→定格在对视",
                "lighting_response": "柔化、暖化、增加眼神光、逆光光晕",
                "pacing_response": "世界减速(慢动作)→回到正常(梦醒)→比正常更慢(沉浸)",
            },
        },
        "complex_emotions": {
            "bittersweet": {
                "cn": "苦乐参半",
                "description": "笑中带泪,得到的同时失去,回忆的温暖中有再也回不去的冰冷",
                "visual": "微笑但眼眶泛红,手握着某个回忆的物品,看向窗外远方",
                "camera": "中近景固定,不打扰角色的复杂情绪,让观众自己感受",
                "examples": ["《寻梦环游记》最后的歌", "《花样年华》擦肩而过"],
            },
            "guilty_relief": {
                "cn": "带着愧疚的解脱",
                "description": "危机解除但代价是别人的牺牲,活下来但不觉得自己配",
                "visual": "长出一口气但立刻表情凝固,目光空洞,双手发抖",
                "camera": "先紧后松再凝固——推→拉→定格",
            },
            "proud_loneliness": {
                "cn": "骄傲的孤独",
                "description": "达成了目标但发现身边空无一人",
                "visual": "站在高处/颁奖台但画面大量留白,人物渺小",
                "camera": "从特写胜利表情缓缓拉至极远景的孤独身影",
            },
            "tender_anger": {
                "cn": "温柔的愤怒",
                "description": "对所爱之人的失望和恨其不争",
                "visual": "愤怒的声音但手在颤抖想触碰对方,最后转身离开的背影",
                "camera": "正面愤怒→侧面犹豫→背影离开→空镜头(离开后的空间)",
            },
        },
    },

    "emotion_curve_design": {
        "principles": {
            "never_flat": "情绪曲线永远不能是平的——哪怕平静场景也要有微小波动",
            "contrast_amplifies": "高点越高是因为低点够低——先往下压才能弹得更高",
            "rest_before_peak": "最高潮前必须有一个短暂的平静(深呼吸时刻)",
            "aftermath_matters": "高潮后的余波比高潮本身更能留下印象",
            "asymmetric_curve": "上升可以慢(积蓄期望),下降要快(冲击力)——反之亦然看类型",
        },
        "curve_templates": {
            "standard_arc": {
                "cn": "标准弧(大部分故事)",
                "shape": "逐步上升→顶点→快速下降→余韵",
                "emotion_values": [0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 0.95, 0.7, 0.5],
            },
            "rollercoaster": {
                "cn": "过山车(短剧/动作)",
                "shape": "高→低→更高→更低→最高→释放",
                "emotion_values": [0.7, 0.3, 0.8, 0.2, 0.6, 0.1, 0.95, 0.6],
            },
            "slow_burn": {
                "cn": "慢热(悬疑/文艺)",
                "shape": "低平→微升→微升→微升→突然爆发",
                "emotion_values": [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.95],
            },
            "descent": {
                "cn": "坠落(悲剧/黑色)",
                "shape": "高起→逐步下降→最低→微光",
                "emotion_values": [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.15, 0.1, 0.25],
            },
            "oscillation": {
                "cn": "震荡(短视频/情绪向)",
                "shape": "快速在高低之间切换,幅度越来越大",
                "emotion_values": [0.5, 0.7, 0.3, 0.8, 0.2, 0.9, 0.1, 0.95],
            },
        },
    },

    "scene_emotion_rendering": {
        "atmosphere_building": {
            "sound": {
                "silence": "安静积蓄→情绪爆发前的真空→爆发后的耳鸣般寂静",
                "ambient": "环境音层层叠加=压力增加; 环境音一层层消失=聚焦内心",
                "music_absence": "音乐突然停止=最震撼的叙事手法之一(让真实的声音/沉默取代)",
                "heartbeat": "内化的心跳声=观众代入角色的生理恐惧",
            },
            "weather_emotion": {
                "rain": "清洗/悲伤/新开始——取决于角色状态",
                "snow": "纯净/冰冷/时间冻结/死亡的美化",
                "wind": "变化将至/内心波动/自由",
                "fog": "迷茫/未知/记忆模糊/灵界",
                "sunshine": "希望/治愈/日常的温暖/反讽(阳光下的残酷)",
                "storm": "内心风暴的外化/命运打击/考验",
            },
            "color_temperature_shift": {
                "warm_to_cold": "安全→危险 / 现在→回忆 / 清醒→麻木",
                "cold_to_warm": "孤独→温暖 / 危险→安全 / 绝望→希望",
                "saturation_decrease": "活力丧失 / 抑郁侵入 / 记忆褪色",
                "saturation_increase": "情感觉醒 / 物是人非中的一抹鲜活 / 重获生命力",
            },
        },
        "emotional_contrast_pairs": {
            "purpose": "相邻场景使用对比情绪可以让两者都更强烈",
            "effective_pairs": [
                ("欢笑", "紧接着的噩耗", "落差产生最大冲击"),
                ("战争的残酷", "废墟中孩子的笑", "人性光芒在黑暗中最耀眼"),
                ("甜蜜约会", "暗处跟踪者的视角", "反差制造不安"),
                ("葬礼的庄严", "突然的手机铃声/孩子笑", "荒诞揭示生活继续"),
                ("安静的日常", "一通电话改变一切", "平静是暴风雨的最佳铺垫"),
            ],
        },
    },

    "voiceover_narration": {
        "types": {
            "retrospective": {
                "cn": "回顾式旁白",
                "description": "已经知道结局的角色回顾往事",
                "tone": "沉静、带有智慧、偶尔苦涩",
                "examples": ["《肖申克的救赎》Red的旁白", "《阿甘正传》"],
            },
            "real_time_thought": {
                "cn": "实时内心独白",
                "description": "角色当下的想法直接呈现",
                "tone": "情绪化、不冷静、碎片化",
                "examples": ["《搏击俱乐部》Jack的旁白", "短剧常用心声"],
            },
            "omniscient": {
                "cn": "全知旁白",
                "description": "超越角色之上的叙述者",
                "tone": "冷静、客观、有时带讽刺",
                "examples": ["《布达佩斯大饭店》嵌套叙述", "纪录片风格"],
            },
            "unreliable": {
                "cn": "不可靠叙述",
                "description": "旁白者的话不能完全信任",
                "tone": "流畅但隐含矛盾,后期观众发现被骗",
                "examples": ["《搏击俱乐部》", "《禁闭岛》"],
            },
        },
        "when_to_use": {
            "use": [
                "时间跨度大需要压缩叙事时",
                "角色内心与外表矛盾需要揭示时",
                "建立亲密感(对观众说话)时",
                "信息量大但不能用对话传递时",
            ],
            "avoid": [
                "能用画面展示就不用旁白说明",
                "不要用旁白解释观众已经能看到的东西",
                "不要用旁白代替角色之间的真实对话",
                "高潮时刻(行动>语言)",
            ],
        },
    },

    "foreshadowing_payoff": {
        "cn": "伏笔与回收(挖坑填坑)",
        "principles": {
            "plant_naturally": "伏笔必须在第一次出现时有合理的存在理由(不能像在故意提示)",
            "payoff_exceeds_plant": "回收时的冲击力必须大于埋设时的印象——否则观众会失望",
            "timing_matters": "太快回收=没有悬念; 太慢回收=观众已经忘了",
            "multiple_plants": "重要的回收至少要有2-3次'不经意的'铺垫",
        },
        "techniques": {
            "chekhov_gun": {
                "cn": "契诃夫之枪",
                "rule": "第一幕墙上挂的枪第三幕必须开火",
                "visual_method": "特写→自然融入→关键时刻再次特写(观众恍然)",
            },
            "dialogue_echo": {
                "cn": "台词回响",
                "rule": "早期的一句普通对话在后期有了完全不同的含义",
                "example": "角色A早期说'我永远不会离开你'→后期发现A早就计划离开",
            },
            "visual_motif": {
                "cn": "视觉母题",
                "rule": "重复出现的视觉元素最终揭示深层含义",
                "example": "反复出现的红色气球→最终揭示是孩子死亡那天的物品",
            },
            "behavioral_foreshadow": {
                "cn": "行为伏笔",
                "rule": "角色早期一个不起眼的习惯/能力在关键时刻成为解决问题的钥匙",
                "example": "角色总是随手把东西排整齐→最后靠这个强迫症发现了密室的线索",
            },
        },
        "short_drama_application": {
            "fast_plant_fast_payoff": "短剧中伏笔→回收的间隔通常只有3-8集(观众记忆窗口短)",
            "visual_emphasis": "埋伏笔时用0.5秒的特写+音效微妙强调(让注意力高的观众能发现)",
            "multiple_layers": "主线伏笔(必须回收)+彩蛋伏笔(回收是惊喜)+红鲱鱼(故意误导)",
        },
    },

    # ========================================================
    # 扩充: 进阶复合情绪
    # ========================================================
    "complex_emotions_extended": {
        "schadenfreude": {
            "cn": "幸灾乐祸",
            "description": "看到他人受难时隐秘的快感,常伴随道德掩饰",
            "visual": "嘴角强压的笑意,目光从侧面偷瞄,身体微微后仰的放松",
        },
        "weltschmerz": {
            "cn": "世界厌倦",
            "description": "意识到世界本不该如此却只能接受的精神疲惫",
            "visual": "目光缓慢扫过眼前的世界,然后缓缓闭眼,面部所有生机褪去",
        },
        "restless_hope": {
            "cn": "焦灼的希望",
            "description": "希望太大反而变成折磨的等待",
            "visual": "手指不断敲击/搓动,目光频繁看向时间,呼吸浅而急促",
        },
        "vengeful_calm": {
            "cn": "复仇前的平静",
            "description": "已经下定决心后反而异常冷静,暴风雨前的宁静",
            "visual": "面部肌肉彻底放松,目光变得清澈而冷,呼吸深长,动作慢而精准",
        },
        "devastating_realization": {
            "cn": "毁灭性领悟",
            "description": "瞬间理解了改变一切的事实",
            "visual": "动作骤停,瞳孔骤放,面部血色褪尽,然后缓慢地——嘴角抽动一下(无法承受)",
        },
        "tender_grief": {
            "cn": "温柔的悲伤",
            "description": "带着爱的失去,痛里有暖",
            "visual": "微笑着落泪,手轻抚逝者/遗物,目光温柔而非空洞",
        },
    },

    # ========================================================
    # 扩充: 情绪渲染技法清单
    # ========================================================
    "rendering_techniques": {
        "externalization": {
            "cn": "情绪外化",
            "principle": "把内心情绪投射到环境/天气/物件上(让不可见变可见)",
            "examples": ["愤怒→打翻的水杯/裂开的镜子", "悲伤→下雨/枯萎的花", "希望→阳光透过云层"],
        },
        "substitution": {
            "cn": "替代表演",
            "principle": "用物件/动物/环境的反应替代角色直接演情绪(留白更有力)",
            "examples": ["丧子之痛→不拍母亲哭,拍空荡的儿童房摇椅", "愤怒→拍被攥皱的照片而非脸"],
        },
        "contrast_carrier": {
            "cn": "反差承载",
            "principle": "用一个反差元素(欢乐中的悲/残酷中的美)让情绪更刺",
            "examples": ["战场上的蒲公英", "葬礼上的儿童笑声", "死刑前的日出"],
        },
        "rhythm_emotion": {
            "cn": "节奏即情绪",
            "principle": "剪辑节奏本身就在传递情绪,不必依赖表情",
            "examples": ["焦虑→越来越快的跳切", "绝望→越来越长的停顿", "混乱→无规律的切"],
        },
        "sound_emotion": {
            "cn": "声音承载情绪",
            "principle": "环境音/音乐/沉默是情绪的另一半",
            "examples": ["恐惧→心跳声放大", "失去→音乐戛然而止", "孤独→环境音被放大凸显空旷"],
        },
    },

    # ========================================================
    # 扩充: 类型片情绪公式
    # ========================================================
    "genre_emotion_formulas": {
        "甜宠": "委屈(低谷)→小甜(回升)→误会(小跌)→大甜(新高)→分离(最低)→重逢(最高)",
        "复仇": "屈辱(最低)→隐忍(平)→布局(微升)→释放(爆发最高)→空虚(骤降)",
        "恐怖": "平静(中)→不安(缓降)→恐惧(急降)→假安全(反弹)→最大恐惧(最低)",
        "喜剧": "常态(中)→尴尬(微降)→困境(降)→转折(升)→混乱(震荡)→圆满(最高)",
        "悬疑": "平静(中)→疑窦(微降)→误导(假升)→真相(震荡)→冰冷领悟(最低)",
    },
}


# ============================================================
# 情感渲染决策覆盖层 — 为关键技法补7维决策字段
# (保留原principles/techniques, 叠加trigger/failure/measurement等)
# ============================================================
EMOTION_RENDERING_DECISION = {
    # ─── 情绪渲染技法(导演级how-to) ───
    "externalization": {
        "trigger": "内心情绪需可见/投射到环境天气物件/让不可见变可见",
        "rationale": "把内心投射到环境=让观众通过视觉读情绪, 比直接演更高级。",
        "failure_modes": ["投射过明=说教", "投射与情绪不匹配=失逻辑", "投射无回收=悬置"],
        "measurement": "观众通过环境读出情绪, 投射有逻辑且回收",
        "alternatives": ["substitution(更替代表演)", "contrast_carrier(更反差)"],
        "cross_refs": {"show_dont_tell": "展示而非叙述", "weather": "天气情绪", "color": "色彩情绪外化"},
    },
    "substitution": {
        "trigger": "用物件/动物/环境反应替代直接演情绪/留白更有力",
        "rationale": "替代表演=用物件/环境的反应暗示情绪, 留白让观众脑补, 比直接演更深刻。",
        "failure_modes": ["替代物无关联=失暗示", "替代过明=失留白", "无观众理解基础=失意"],
        "measurement": "替代物有关联且暗示, 留白让观众脑补",
        "alternatives": ["externalization(更投射)", "contrast_carrier(更反差)"],
        "cross_refs": {"show_dont_tell": "留白工具", "foreshadow": "物件替代可埋伏笔", "performance": "替代表演"},
    },
    "contrast_carrier": {
        "trigger": "用一个反差元素让情绪更刺/欢乐中的悲/残酷中的美",
        "rationale": "反差元素=让情绪更刺。欢乐中的悲/残酷中的美=反差强化情绪。",
        "failure_modes": ["反差无对照=失刺", "反差过强=失真", "反差无主题=炫技"],
        "measurement": "反差元素让情绪更刺, 有对照与主题",
        "alternatives": ["externalization(更投射)", "substitution(更替代)"],
        "cross_refs": {"emotion_curve": "反差是曲线拐点", "pacing": "反差是节奏重音", "genre": "黑色幽默核心"},
    },
    "rhythm_emotion": {
        "trigger": "用剪辑节奏本身传递情绪/不依赖表情",
        "rationale": "节奏=情绪的另一半。焦虑=越来越快跳切, 绝望=越来越长停顿, 混乱=无规律切。",
        "failure_modes": ["节奏与情绪不匹配=失感", "节奏过极端=眩晕", "无表情配合=单薄"],
        "measurement": "节奏与情绪匹配, 观众通过节奏读情绪",
        "alternatives": ["sound_emotion(更声音)", "externalization(更视觉)"],
        "cross_refs": {"pacing": "节奏即情绪", "editing": "跳切/停顿", "music": "节奏与音乐同步"},
    },
    "sound_emotion": {
        "trigger": "环境音/音乐/沉默承载情绪/声音是情绪一半",
        "rationale": "声音=情绪的另一半。心跳放大=恐惧, 音乐戛然而止=最震撼, 环境音放大=孤独。",
        "failure_modes": ["音乐过多=失留白", "声音与情绪不匹配=失感", "无静默=失力量"],
        "measurement": "声音承载情绪, 有静默留白, 与情绪匹配",
        "alternatives": ["rhythm_emotion(更节奏)", "externalization(更视觉)"],
        "cross_refs": {"sound": "环境音/音乐/静默", "pacing": "静默比巨响更有力", "horror": "心跳放大恐惧"},
    },
    # ─── 旁白类型 ───
    "retrospective": {
        "trigger": "回顾式旁白/已知结局的角色回顾往事/沉静智慧",
        "rationale": "回顾旁白=已知结局的回顾, 带智慧与苦涩。是时间距离的叙述。",
        "failure_modes": ["旁白过多=说教", "旁白与画面重复=冗余", "无时间距离感=失回顾感"],
        "measurement": "旁白有智慧与苦涩, 时间距离感, 不冗余",
        "alternatives": ["real_time_thought(更实时)", "omniscient(更全知)"],
        "cross_refs": {"narrative": "回顾结构", "voice": "沉静智慧语气", "examples": "《肖申克》Red, 《阿甘》"},
    },
    "real_time_thought": {
        "trigger": "实时内心独白/角色当下想法/情绪化碎片化",
        "rationale": "实时独白=角色当下的碎片想法, 情绪化不冷静。是内心直击。",
        "failure_modes": ["独白过多=说教", "独白与表演重复=冗余", "无情绪化=失实时感"],
        "measurement": "独白情绪化碎片化, 实时感, 不冗余",
        "alternatives": ["retrospective(更回顾)", "unreliable(更不可靠)"],
        "cross_refs": {"narrative": "实时内心", "voice": "情绪化碎片语气", "examples": "《搏击俱乐部》, 短剧心声"},
    },
    "omniscient": {
        "trigger": "全知旁白/超越角色之上/冷静客观/有时讽刺",
        "rationale": "全知旁白=超越角色的叙述者, 冷静客观, 有时带讽刺。是上帝视角。",
        "failure_modes": ["全知过多=说教", "无讽刺/客观=失特色", "与角色重复=冗余"],
        "measurement": "全知旁白冷静客观有特色, 不冗余",
        "alternatives": ["retrospective(更回顾)", "unreliable(更不可靠)"],
        "cross_refs": {"narrative": "全知视角", "voice": "冷静客观语气", "examples": "《布达佩斯》嵌套, 纪录片"},
    },
    "unreliable": {
        "trigger": "不可靠叙述/旁白者的话不能完全信任/后期观众发现被骗",
        "rationale": "不可靠旁白=流畅但隐含矛盾, 后期观众发现被骗。是高级悬念。",
        "failure_modes": ["矛盾过明=失悬念", "矛盾过隐=观众信了", "无后期反转=失意义"],
        "measurement": "旁白有暗示矛盾, 观众后期发现, 有反转",
        "alternatives": ["retrospective(更可信)", "real_time_thought(更实时)"],
        "cross_refs": {"narrative": "不可靠叙述", "reversal": "后期反转基础", "examples": "《搏击俱乐部》, 《禁闭岛》"},
    },
    # ─── 伏笔技法 ───
    "chekhov_gun": {
        "trigger": "契诃夫之枪/第一幕墙上的枪第三幕必须开火/伏笔回收核心",
        "rationale": "重要物件必须埋设且回收。特写→自然融入→关键时刻再特写=观众恍然。",
        "failure_modes": ["埋了不回=悬置", "回收冲击<埋设=失望", "回收过快=无悬念"],
        "measurement": "物件有埋设, 自然融入, 关键时刻回收, 冲击>埋设",
        "alternatives": ["dialogue_echo(更台词)", "visual_motif(更视觉)"],
        "cross_refs": {"foreshadow": "伏笔回收核心", "narrative": "契诃夫之枪", "pacing": "前埋后收"},
    },
    "dialogue_echo": {
        "trigger": "台词回响/早期普通对话后期有完全不同含义",
        "rationale": "早期台词后期有新含义=回顾性领悟。是台词层次的伏笔。",
        "failure_modes": ["台词无后期回响=失伏笔", "回响无新含义=失层次", "回响过明=失暗示"],
        "measurement": "早期台词有后期回响, 新含义, 暗示",
        "alternatives": ["chekhov_gun(更物件)", "visual_motif(更视觉)"],
        "cross_refs": {"foreshadow": "台词伏笔", "narrative": "台词回响", "callback": "台词回调"},
    },
    "visual_motif": {
        "trigger": "视觉母题/重复出现的视觉元素最终揭示深层含义",
        "rationale": "重复视觉元素=累积意义, 最终揭示深层含义。是视觉层次的伏笔。",
        "failure_modes": ["母题无重复=失累积", "母题无揭示=悬置", "揭示过明=失暗示"],
        "measurement": "母题重复出现, 最终揭示深层含义, 暗示",
        "alternatives": ["chekhov_gun(更物件)", "behavioral_foreshadow(更行为)"],
        "cross_refs": {"foreshadow": "视觉伏笔", "color": "色彩锚定是视觉母题", "callback": "视觉回调"},
    },
    "behavioral_foreshadow": {
        "trigger": "行为伏笔/角色早期不起眼的习惯能力关键时刻成钥匙",
        "rationale": "早期不起眼习惯/能力=关键时刻的钥匙。是行为层次的伏笔。",
        "failure_modes": ["习惯无回收=悬置", "回收无铺垫=生硬", "习惯过明显=失暗示"],
        "measurement": "早期习惯有铺垫, 关键时刻成钥匙, 暗示",
        "alternatives": ["chekhov_gun(更物件)", "visual_motif(更视觉)"],
        "cross_refs": {"foreshadow": "行为伏笔", "character": "习惯=角色细节", "performance": "行为细节"},
    },
}


def get_emotion_rendering_with_decision(tech_key):
    """合并情感渲染技法基础信息 + 决策覆盖层"""
    base = {}
    for section in ("rendering_techniques", "complex_emotions_extended",
                    "genre_emotion_formulas"):
        if tech_key in EMOTION_RENDERING.get(section, {}):
            base = dict(EMOTION_RENDERING[section][tech_key])
            break
    # voiceover/foreshadow的子结构
    for section in ("voiceover_narration", "foreshadowing_payoff"):
        sec = EMOTION_RENDERING.get(section, {})
        sub = sec.get("types") or sec.get("techniques") or {}
        if tech_key in sub:
            base = dict(sub[tech_key])
            break
    decision = EMOTION_RENDERING_DECISION.get(tech_key, {})
    base.update(decision)
    return base

