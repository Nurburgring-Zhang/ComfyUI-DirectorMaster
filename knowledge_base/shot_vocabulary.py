# ============================================================
# 镜头语汇词典 — 从画面到意义的映射
# 每种镜头语言的精确提示词描述 + 情绪权重 + 时长建议
# ============================================================

SHOT_VOCABULARY = {
    "emotional_shots": {
        "revelation": {
            "cn": "揭示镜头",
            "description": "画面从局部到全貌/从遮挡到展示,揭示关键信息",
            "prompt_template": "镜头缓缓{movement}，逐渐揭示{object}的全貌，{character}的表情从{emotion_a}转为{emotion_b}",
            "movement_options": ["向后拉开", "绕过遮挡物", "上升到鸟瞰", "对焦从模糊到清晰"],
            "duration": "3-6秒",
            "emotion_weight": 0.8,
        },
        "isolation": {
            "cn": "孤立镜头",
            "description": "将角色置于大量空旷空间中,强调孤独",
            "prompt_template": "{character}独自{action}，周围是{vast_space}，人物渺小如蚂蚁，{weather_element}",
            "composition": "人物占画面不超过10%,其余为环境",
            "duration": "4-8秒",
            "emotion_weight": 0.7,
        },
        "confrontation": {
            "cn": "对峙镜头",
            "description": "两个角色面对面,张力拉满",
            "prompt_template": "两人相距{distance}对视，{char_a}表情{emotion_a}，{char_b}表情{emotion_b}，空气仿佛凝固",
            "composition": "双人对称构图/分屏/正反打加速",
            "duration": "2-5秒",
            "emotion_weight": 0.85,
        },
        "tenderness": {
            "cn": "温柔镜头",
            "description": "展示人物间细腻温暖的瞬间",
            "prompt_template": "{character}轻轻{gentle_action}，{light_quality}柔和地包裹两人，时间仿佛慢了下来",
            "composition": "浅景深、暖色、两人紧密构图",
            "duration": "3-6秒",
            "emotion_weight": 0.6,
        },
        "power_shift": {
            "cn": "权力转移镜头",
            "description": "画面语言展示谁掌控了局面",
            "prompt_template": "镜头从{dominant}的{angle_dominant}视角切到{submissive}的{angle_sub}视角，{power_symbol}",
            "technique": "角度变化(仰拍→俯拍)或位置变化(高处→低处)",
            "duration": "2-4秒",
            "emotion_weight": 0.75,
        },
        "breakdown": {
            "cn": "崩溃镜头",
            "description": "角色情绪彻底崩塌的视觉表达",
            "prompt_template": "{character}的脸从{controlled_emotion}突然{collapse_action}，{physical_reaction}，{environment_response}",
            "camera": "固定特写(不切开,逼迫观众直视崩溃过程)",
            "duration": "4-10秒(越长越有力)",
            "emotion_weight": 0.95,
        },
        "anticipation": {
            "cn": "期待/蓄势镜头",
            "description": "大事发生前的寂静积蓄",
            "prompt_template": "{character}凝视{target}，手指{micro_action}，呼吸{breath_state}，{countdown_element}",
            "camera": "极缓推镜,从全身慢慢推到面部",
            "duration": "4-8秒",
            "emotion_weight": 0.65,
        },
    },

    "action_shots": {
        "impact": {
            "cn": "冲击镜头",
            "description": "力量碰撞的瞬间",
            "prompt_template": "{force_a}与{force_b}碰撞的瞬间，{impact_effect}，碎片/冲击波向四周扩散",
            "technique": "高速摄影(慢动作)+帧冻结+环境破坏",
            "duration": "0.5-2秒(慢放可至5秒)",
        },
        "pursuit": {
            "cn": "追逐镜头",
            "description": "紧张的追赶动态",
            "prompt_template": "{character}拼命{movement_verb}，{pursuer}在身后{pursuit_action}，距离{closing_or_widening}",
            "camera": "手持跟拍/POV交替/仰拍奔跑者",
            "duration": "每段2-4秒快切",
        },
        "transformation": {
            "cn": "变身/变化镜头",
            "description": "角色或事物发生根本性改变",
            "prompt_template": "{subject}开始{transformation_verb}，{visual_effect}从{state_a}渐变为{state_b}，{emotional_peak}",
            "technique": "环绕+升格+粒子效果/光效",
            "duration": "3-8秒",
        },
    },

    "narrative_shots": {
        "establishing": {
            "cn": "建立镜头",
            "description": "每个新场景的第一个镜头,交代时空",
            "prompt_template": "{time_of_day}的{location}，{atmosphere_description}，{life_detail}暗示此处的{tone}",
            "requirements": "必须包含:时间信息+地点信息+氛围暗示",
            "duration": "3-6秒",
        },
        "transition_bridge": {
            "cn": "过渡桥梁镜头",
            "description": "连接两个不同情绪/场景的中间画面",
            "prompt_template": "{transitional_image}，色调从{color_a}渐变为{color_b}，象征{thematic_shift}",
            "examples": ["日出/日落(时间过渡)", "交通工具(空间过渡)", "自然元素(情绪过渡)"],
            "duration": "2-4秒",
        },
        "callback": {
            "cn": "回调镜头",
            "description": "画面呼应之前出现过的某个镜头,形成意义叠加",
            "prompt_template": "与第{ref_shot}镜相同的构图/角度，但此刻{what_changed}，赋予画面全新含义",
            "technique": "完全相同的机位+角度,但内容/情绪/色调有变",
            "duration": "同参考镜头",
        },
        "time_passage": {
            "cn": "时间流逝镜头",
            "description": "压缩表达时间跨度",
            "prompt_template": "{fixed_element}不变，而{changing_element}经历{time_span}的变化：{stage_1}→{stage_2}→{stage_3}",
            "techniques": ["同机位延时", "叠化渐变", "四季变化", "人物老化/成长"],
            "duration": "3-8秒",
        },
    },

    "compositional_vocabulary": {
        "depth_planes": {
            "foreground_element": {
                "purpose": "增加层次感/偷窥感/遮挡制造好奇",
                "common_elements": ["虚化的肩膀/背影", "门框/窗框/栏杆", "飘动的纱帘/烟雾", "前景物品(杯子/花)"],
            },
            "midground_action": {
                "purpose": "主要叙事发生的区域",
                "rules": "角色的关键动作和表情在此层呈现",
            },
            "background_story": {
                "purpose": "提供环境信息/隐藏细节/暗示",
                "examples": ["远处走过的人群暗示时代", "墙上的照片暗示过去", "窗外的天气暗示心情"],
            },
        },
        "frame_dynamics": {
            "balanced": {
                "cn": "平衡画面",
                "feeling": "和谐、稳定、日常",
                "when_to_use": "平静叙事、对话、展示",
            },
            "unbalanced": {
                "cn": "失衡画面",
                "feeling": "紧张、不安、即将改变",
                "when_to_use": "危机前夕、心理不稳定、世界观崩塌",
            },
            "crowded": {
                "cn": "拥挤画面",
                "feeling": "压迫、窒息、信息过载",
                "when_to_use": "角色被困、社会压力、混乱场景",
            },
            "empty": {
                "cn": "空旷画面",
                "feeling": "孤独、自由、失去、辽阔",
                "when_to_use": "失去后的空虚、自由奔跑、存在主义",
            },
        },
    },

    "shot_duration_guide": {
        "by_emotion": {
            "shock": "0.5-1.5秒(越短冲击越大)",
            "sadness": "5-12秒(给情绪呼吸的空间)",
            "joy": "2-4秒(快乐不宜停留太久,保持轻快)",
            "tension": "3-6秒(不断在长与短之间切换制造节奏)",
            "awe": "6-10秒(让观众有时间感受壮观)",
            "comedy": "精确到帧(差一帧笑点就死)",
        },
        "by_information": {
            "simple_action": "1-2秒",
            "dialogue_exchange": "按台词节奏(每句话一个镜头)",
            "new_environment": "3-5秒(观众需要时间读取空间)",
            "complex_emotion": "5-8秒(给面部微表情时间发展)",
            "revelation": "先短后长(快速揭示→停留在反应上)",
        },
        "rhythm_patterns": {
            "accelerating": "5s→4s→3s→2s→1s→0.5s(冲向高潮)",
            "decelerating": "1s→2s→3s→5s→8s(高潮后的沉淀)",
            "alternating": "2s→5s→2s→5s(对话/反应的呼吸)",
            "uniform": "全部3s(机械感/倒计时感/MV风格)",
            "chaotic": "随机0.5s-4s(混乱/恐惧/失控)",
        },
    },

    "continuity_markers": {
        "visual_continuity": {
            "eyeline": "角色看向画面右→下一镜从左侧来",
            "screen_direction": "角色向右走=持续向右(除非有过渡镜头)",
            "lighting_consistency": "同一场景内光线方向不变",
            "color_grading": "同一时空的色调保持一致",
            "prop_position": "关键道具位置跨镜头不变",
        },
        "emotional_continuity": {
            "rule": "情绪变化必须有过程,不能跨镜头跳跃",
            "method": "上一镜结束时的情绪=下一镜开始时的情绪基线",
            "exception": "除非有明确的时间跳跃标记(叠化/黑场/字幕)",
        },
        "narrative_continuity": {
            "story_so_far_prefix": "每个分镜输出前标注:当前故事进展+角色状态+待解决悬念",
            "callback_tracking": "记录已埋设的伏笔及其计划回收时机",
            "character_arc_position": "标注角色在成长弧线上的当前位置(0-1)",
        },
    },

    # ========================================================
    # 扩充: 高级镜头语汇
    # ========================================================
    "advanced_shots": {
        "vertigo_dolly_zoom": {
            "cn": "推拉变焦镜头",
            "description": "镜头前推同时焦距拉远(或反之),主体不变而环境变形",
            "usage": "角色顿悟/恐惧/世界观崩塌的瞬间",
            "masters": "《迷魂记》《魔戒》Frodo戴戒",
        },
        "oner": {
            "cn": "一镜到底长镜头",
            "description": "用极长镜头连续完成一段叙事,无任何剪辑",
            "usage": "沉浸式体验、仪式感、导演炫技、空间穿越",
            "masters": "《1917》《好家伙》《鸟人》",
        },
        "split_screen": {
            "cn": "分屏镜头",
            "description": "画面分割同时呈现不同时空/视角",
            "usage": "同时性叙事、对比、凝视的多视角、悬念(两个事件同步)",
            "masters": "《杀死比尔》《 Olympia》",
        },
        "establishing_oner": {
            "cn": "建立性长镜头",
            "description": "用一个连续长镜头建立整个场景的空间/人物/氛围",
            "usage": "新场景入场、展现空间关系、跟着角色进入世界",
            "masters": "Spielberg《1941》《侏罗纪》",
        },
        "POV_immersive": {
            "cn": "沉浸主观视角",
            "description": "完全代入角色视角的连续镜头",
            "usage": "恐怖、追逐、发现、让观众成为角色",
            "masters": "《硬核亨利》《1917》",
        },
        "montage_sequence": {
            "cn": "蒙太奇段落",
            "description": "一组快切镜头压缩时间/展示过程/制造节奏",
            "usage": "训练段落、时间流逝、关系建立、信息爆炸",
            "masters": "《洛奇》训练蒙太奇、《飞屋环游记》人生蒙太奇",
        },
    },

    # ========================================================
    # 扩充: 情绪-镜头映射速查
    # ========================================================
    "emotion_shot_quickmap": {
        "shock_revelation": "急推特写瞳孔→环境缓拉揭示",
        "heartbreak": "固定中景不切开→角色慢慢崩溃→缓拉至远景孤独",
        "rage_explosion": "手持晃动跟拍→破坏动作→极特写瞳孔/血管",
        "tender_intimacy": "缓慢环绕双人→景深极浅只有彼此→定格对视",
        "suspense_build": "极缓推镜从全景推到面部→背景模糊→声音渐弱",
        "triumph": "仰拍角色升起→升格慢动作→拉开展示世界",
        "despair_void": "俯拍蜷缩的人物→缓慢拉远至极远景渺小",
        "awe_sublime": "广角远景人物渺小vs壮景→慢速靠近→面部仰望",
    },

    # ========================================================
    # 扩充: 镜头组接的句法
    # ========================================================
    "shot_syntax": {
        "statement_subject_action": "建立镜(主体是谁在哪)→动作镜(在做什么)→反应镜(后果/情绪)",
        "question_answer": "悬念镜(抛出疑问)→揭示镜(给出答案)→反应镜(角色/观众消化)",
        "build_climax": "蓄势镜(慢)→蓄势镜(更慢)→爆发镜(极快)→余韵镜(慢回)",
        "parallel_contrast": "A线镜→B线镜→A线镜→B线镜(加速→交汇)",
        "callback_structure": "早期镜(埋伏笔)→中期镜(自然推进)→后期镜(同构图回收,新含义)",
    },
}


# ============================================================
# 镜头语汇决策覆盖层 — 为关键镜头补7维决策字段
# (保留原prompt_template/emotion_weight, 叠加trigger/failure/measurement等)
# ============================================================
SHOT_VOCAB_DECISION = {
    # ─── 情绪镜头 ───
    "revelation": {
        "trigger": "揭示关键信息/真相揭露/从局部到全貌/从遮挡到展示",
        "rationale": "揭示镜头=信息从隐藏到展示的过程, 制造认知抵达的冲击。终点应是信息高点。",
        "failure_modes": ["揭示过快=失过程冲击", "揭示终点无信息=推了个寂寞", "揭示无前置铺垫=突兀"],
        "measurement": "揭示过程有张力, 终点=信息高点, 观众有'啊'的抵达感",
        "alternatives": ["vertigo_shot(更认知崩塌)", "push_in(更聚焦)"],
        "cross_refs": {"narrative_func": "识破/揭示", "pacing": "揭示是拐点", "camera": "缓推/拉开/对焦变化"},
    },
    "isolation": {
        "trigger": "角色孤独/失去后的空虚/存在主义/末世渺小",
        "rationale": "人物占画面<10%+大量环境=视觉化的孤独。渺小化是孤立的核心。",
        "failure_modes": ["人物比例过大=失渺小", "环境无情绪=失孤独", "孤立无叙事理由=炫技"],
        "measurement": "观众应读出'渺小/孤独', 人物占画面<10%",
        "alternatives": ["negative_space(更广义留白)", "pull_back(更动态渺小化)"],
        "cross_refs": {"composition": "负空间+极远景", "emotion": "despair/nostalgia", "pacing": "孤立是余韵段"},
    },
    "confrontation": {
        "trigger": "两人对峙/张力拉满/对决前夕/权力对峙",
        "rationale": "双人对称构图/正反打加速=空气凝固的张力。对峙是冲突的视觉顶点。",
        "failure_modes": ["对峙无张力=失力量", "对称无权力暗示=失层次", "对峙过长=拖"],
        "measurement": "观众应感到空气凝固的张力",
        "alternatives": ["two_shot(更关系)", "power_shift(更权力转移)"],
        "cross_refs": {"composition": "对称/分屏/正反打", "pacing": "对峙是冲突顶点", "performance": "对视是核心"},
    },
    "tenderness": {
        "trigger": "人物间细腻温暖/亲密瞬间/言情高光",
        "rationale": "浅景深+暖色+紧密构图=只有彼此的视觉化。温柔镜头让时间慢下来。",
        "failure_modes": ["无浅景深=失只有彼此", "色调冷=失温暖", "无亲密互动=失温柔"],
        "measurement": "观众应读出'只有彼此的温暖', 浅景深+暖色",
        "alternatives": ["two_shot(更关系)", "close_up(更面部)"],
        "cross_refs": {"genre": "言情标配", "lighting": "暖色柔光", "lens": "浅景深长焦"},
    },
    "power_shift": {
        "trigger": "权力转移/谁掌控局面/仰俯转换/位置变化",
        "rationale": "角度变化(仰→俯)或位置变化(高→低)=权力关系的视觉化转移。",
        "failure_modes": ["无角度/位置变化=失转移", "转移无叙事理由=炫技", "转移过快=失过程"],
        "measurement": "观众应读出'权力转移', 角度/位置变化清晰",
        "alternatives": ["confrontation(更对峙)", "low_angle/high_angle(更单一角度)"],
        "cross_refs": {"angle": "仰俯转换是核心", "narrative_func": "逆袭/打脸", "pacing": "权力转移是拐点"},
    },
    "breakdown": {
        "trigger": "角色情绪彻底崩塌/心理崩溃/固定特写逼迫直视",
        "rationale": "固定特写不切=逼迫观众直视崩溃过程, 越长越有力。是情绪极致的视觉化。",
        "failure_modes": ["切走=逃避, 失逼迫", "崩溃过快=失过程", "无前置控制=失对照"],
        "measurement": "观众应被逼迫直视崩溃, 固定特写4-10秒, 有前置控制对照",
        "alternatives": ["extreme_close_up(更极致)", "handheld(更混乱崩溃)"],
        "cross_refs": {"performance": "崩溃=表演极致", "pacing": "崩溃是情绪顶点", "camera": "固定不切是核心"},
    },
    "anticipation": {
        "trigger": "大事发生前/寂静积蓄/蓄势/倒计时/爆发前最静",
        "rationale": "极缓推镜+手指微动+呼吸+倒计时=蓄势到顶点。爆发前的寂静最有张力。",
        "failure_modes": ["蓄势过长=拖", "无倒计时/微动=失蓄势细节", "蓄势后无爆发=泄气"],
        "measurement": "观众应感到'即将爆发'的蓄势, 爆发前最静",
        "alternatives": ["breakdown(更爆发)", "static(更静)"],
        "cross_refs": {"pacing": "蓄势是爆发前段", "sound": "呼吸/心跳渐强", "camera": "极缓推全身→面部"},
    },
    # ─── 动作镜头 ───
    "impact": {
        "trigger": "力量碰撞瞬间/打击/爆炸/冲击波",
        "rationale": "高速摄影+帧冻结+环境破坏=力量碰撞的视觉化。慢动作顶点是冲击核心。",
        "failure_modes": ["无慢动作顶点=失冲击", "无环境破坏=失力量", "冲击无预备=失因果"],
        "measurement": "观众应读出'力量碰撞', 慢动作顶点+环境破坏",
        "alternatives": ["orbit(更环绕)", "handheld(更混乱)"],
        "cross_refs": {"genre": "动作标配", "pacing": "蓄力→爆发→顶点→余波", "vfx": "帧冻结+破坏"},
    },
    "pursuit": {
        "trigger": "追逐/紧张追赶/POV交替/仰拍奔跑",
        "rationale": "手持跟拍+POV交替+仰拍奔跑=代入追逐的紧张。距离收窄/扩大是张力引擎。",
        "failure_modes": ["手持晃过大=晕", "无距离变化=失张力", "追逐无地理=迷失"],
        "measurement": "观众应代入追逐, 距离变化清晰",
        "alternatives": ["tracking(更跟随)", "handheld(更混乱)"],
        "cross_refs": {"genre": "动作/恐怖标配", "camera": "手持+POV+仰拍", "pacing": "快切2-4s"},
    },
    "transformation": {
        "trigger": "角色/事物根本性改变/变身/突破/觉醒",
        "rationale": "环绕+升格+粒子/光效=变化的视觉化。变身镜头让不可见的变化可见。",
        "failure_modes": ["无环绕/升格=失变化感", "特效廉价=失质感", "变化无前置=突兀"],
        "measurement": "观众应读出'根本性变化', 环绕+升格+特效",
        "alternatives": ["vertigo_shot(更认知崩塌)", "impact(更冲击)"],
        "cross_refs": {"genre": "科幻/玄幻标配", "vfx": "粒子/光效", "pacing": "变身是高潮点"},
    },
    # ─── 叙事镜头 ───
    "establishing": {
        "trigger": "新场景首镜/建立时空/定场/交代在哪",
        "rationale": "建立镜=时间+地点+氛围的'地图', 让观众知道后续在哪。须含时间/地点/氛围信息。",
        "failure_modes": ["无时间信息=失时间锚定", "无氛围暗示=失调", "建立镜过长=拖"],
        "measurement": "观众应知道'时间+地点+氛围', 3-6秒",
        "alternatives": ["establishing_oner(更沉浸)", "wide(更广)"],
        "cross_refs": {"narrative_func": "定场", "composition": "纵深分层", "pacing": "新场景首镜"},
    },
    "transition_bridge": {
        "trigger": "连接两个情绪/场景的过渡/日出日落/交通工具/自然元素",
        "rationale": "过渡桥梁=用象征性元素(日出/交通工具)连接两段, 色调渐变象征主题转变。",
        "failure_modes": ["桥梁无象征=失主题", "色调无渐变=失过渡", "桥梁过长=拖"],
        "measurement": "观众应感到情绪/场景过渡, 色调渐变",
        "alternatives": ["dissolve(更直接)", "cutaway(更隐喻)"],
        "cross_refs": {"narrative_func": "过渡", "color": "色调渐变象征主题", "pacing": "桥梁是节奏呼吸"},
    },
    "callback": {
        "trigger": "呼应之前镜头/意义叠加/同构图新含义/伏笔回收",
        "rationale": "完全相同机位+角度但内容/情绪/色调有变=意义叠加。是伏笔回收的视觉化。",
        "failure_modes": ["机位/角度不完全一致=失呼应", "无新含义=失意义叠加", "无前置伏笔=突兀"],
        "measurement": "观众应读出'同构图新含义', 机位一致",
        "alternatives": ["buildup_payoff(更伏笔结构)", "match_cut(更匹配)"],
        "cross_refs": {"foreshadow": "回调是伏笔回收", "narrative_func": "回收/回顾", "composition": "机位须严格一致"},
    },
    "time_passage": {
        "trigger": "压缩时间跨度/同机位延时/四季变化/人物老化",
        "rationale": "固定元素不变+变化元素经历时间=时间流逝的视觉化。是时间压缩工具。",
        "failure_modes": ["无固定锚点=失对比", "变化无逻辑=混乱", "时间跨度不清=失感"],
        "measurement": "观众应读出'时间流逝', 有固定锚点+变化元素",
        "alternatives": ["dissolve(更柔和时间跳)", "montage(更段落时间)"],
        "cross_refs": {"narrative_func": "时间压缩", "pacing": "时间流逝段", "technique": "延时/叠化/四季"},
    },
    # ─── 高级镜头 ───
    "vertigo_dolly_zoom": {
        "trigger": "角色顿悟真相/认知崩塌/恐惧震惊/世界变形而主体不变",
        "rationale": "dolly+zoom反向=主体大小不变而背景透视剧变=认知崩塌的视觉化。须慎用经典技法。",
        "failure_modes": ["dolly与zoom不协调=失效果", "滥用=廉价", "无顿悟理由=炫技"],
        "measurement": "观众应读出'认知崩塌', 主体大小不变背景变形",
        "alternatives": ["急推特写(更直接)", "static+表情(更克制)"],
        "cross_refs": {"narrative_func": "顿悟/揭示", "camera": "dolly+zoom反向", "performance": "须配认知崩塌表情"},
    },
    "oner": {
        "trigger": "一镜到底/沉浸/仪式感/长镜头场面调度/空间穿越",
        "rationale": "极长镜头无剪辑=真实时间+沉浸+场面调度炫技。是导演功力的标志。",
        "failure_modes": ["无调度层次=炫技拖沓", "操作不稳=穿帮", "伪一镜到底过长=拖"],
        "measurement": "观众应沉浸, 完成复杂场面调度",
        "alternatives": ["invisible_cut(伪一镜但更易)", "steadicam(更丝滑)"],
        "cross_refs": {"narrative_func": "沉浸/仪式", "camera": "steadicam/dolly长镜头", "continuity": "长镜头内须守连戏"},
    },
    "split_screen": {
        "trigger": "同时性叙事/对比/多视角/悬念(两事件同步)",
        "rationale": "画面分割同时呈现不同时空/视角=同时性与对比。是悬念与对照工具。",
        "failure_modes": ["分割无对照=失价值", "分割过多=杂乱", "分割无同时性=失意义"],
        "measurement": "观众应读出'同时性/对比', 分割有对照意义",
        "alternatives": ["parallel(更交替)", "cross_cut(更剪辑)"],
        "cross_refs": {"narrative_func": "同时性/对比", "pacing": "分割是节奏对照", "composition": "分割构图"},
    },
    "establishing_oner": {
        "trigger": "新场景连续长镜头入场/跟着角色进入世界/展现空间关系",
        "rationale": "用一个连续长镜头建立整个场景=比静态建立镜更沉浸, 跟着角色进入。",
        "failure_modes": ["无空间建立=失定场", "长镜头拖=失节奏", "操作不稳=穿帮"],
        "measurement": "观众应沉浸建立场景, 知道空间关系",
        "alternatives": ["establishing(更静态)", "oner(更广义长镜头)"],
        "cross_refs": {"narrative_func": "定场/入场", "camera": "steadicam/dolly跟拍", "spielberg": "Spielberg标志"},
    },
    "POV_immersive": {
        "trigger": "完全代入角色/恐怖(看不到背后)/追逐/第一人称/发现揭示",
        "rationale": "完全POV=观众成为角色, 沉浸最强。恐怖片用'看不到背后'最大化恐惧。",
        "failure_modes": ["POV过长=失角色主体", "无揭示=浪费代入", "晃过大=晕"],
        "measurement": "观众应'成为角色', 有揭示或恐惧理由",
        "alternatives": ["over_shoulder(更保留角色)", "fpv_drone(更极速)"],
        "cross_refs": {"genre": "恐怖/追逐/第一人称标配", "performance": "POV后须切反应镜", "sound": "配呼吸/心跳"},
    },
    "montage_sequence": {
        "trigger": "压缩时间/展示过程/训练段落/信息爆炸/节奏段落",
        "rationale": "一组快切镜头压缩时间/展示过程=蒙太奇段落。是时间压缩与节奏段落工具。",
        "failure_modes": ["无时间压缩=失价值", "无节奏=失段落感", "信息过载=混乱"],
        "measurement": "观众应读出'时间压缩/过程/节奏', 段落清晰",
        "alternatives": ["time_passage(更时间)", "metric_montage(更节奏)"],
        "cross_refs": {"narrative_func": "时间压缩/段落", "pacing": "蒙太奇段落", "music": "常配音乐节拍"},
    },
}


def get_shot_with_decision(shot_key):
    """合并镜头语汇基础信息(含prompt_template) + 决策覆盖层"""
    # 在emotional_shots/action_shots/narrative_shots/advanced_shots中查找
    base = {}
    for section in ("emotional_shots", "action_shots", "narrative_shots", "advanced_shots"):
        if shot_key in SHOT_VOCABULARY.get(section, {}):
            base = dict(SHOT_VOCABULARY[section][shot_key])
            break
    decision = SHOT_VOCAB_DECISION.get(shot_key, {})
    base.update(decision)
    return base

