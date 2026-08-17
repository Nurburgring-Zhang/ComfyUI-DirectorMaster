# ============================================================
# 总导演全流程决策树 V1.0 (Director Pipeline Master)
# ============================================================
# 这是知识库的"骨架索引"——总导演真正思考的结构。
# 不是扁平分类词典,而是贯穿 影视生产全周期的决策点网络。
# 每个决策点: 触发条件 → 决策路径 → 量化参数 → 失败模式 → 验收标准 → 交叉影响
#
# 六大阶段(对应总导演工作日历):
#   PHASE 0 开发立项   PHASE 1 剧作   PHASE 2 前期筹备
#   PHASE 3 拍摄现场   PHASE 4 后期   PHASE 5 发行运营
#
# 知识库各模块(map到具体决策点):
#   master_cinematography  → P3摄影指导 / P4调色
#   narrative_structures   → P1结构骨架
#   genre_profiles         → P0赛道/P3类型拍法
#   performance_system     → P3表演指导
#   emotion_rendering      → P1情绪曲线/P4情绪后期
#   transition_grammar     → P4剪辑
#   shot_vocabulary        → P3分镜/P4节奏
#   short_drama_patterns   → P0短剧赛道/P5完播优化
#   viral_video_techniques → P0短视频赛道/P5算法适配
#   director_styles        → P0对标导演/P3风格落地
# ============================================================

DIRECTOR_PIPELINE = {

    # ========================================================
    # PHASE 0 — 开发立项 (Development / Greenlight)
    # 总导演的第一决策: 这部片子为谁拍? 拍给什么平台? 能赚回本吗?
    # ========================================================
    "P0_development": {
        "phase_cn": "开发立项",
        "core_questions": [
            "赛道是否拥挤? 我这部片的差异化定位是什么?",
            "目标受众画像是谁? 核心情感诉求是什么?",
            "首发平台是什么? 该平台的算法偏好我必须遵守什么?",
            "预算档位(短剧1.5-2万/真人类30-50万/院线300万+)决定能做什么不能做什么?",
            "ROI模型是什么? 收入主要来自(分账/广告/会员/品牌植入)?",
        ],
        "decision_points": {
            "D0_1_track_selection": {
                "cn": "赛道选择",
                "trigger": "立项第一步, 决定整部片子的资源与受众",
                "options": {
                    "男频战神流": "目标: 30-50岁男性, 爽感=被蔑视→碾压, 平台: 抖音/快手, 成本低ROI高但红海",
                    "女频甜宠流": "目标: 18-35岁女性, 爽感=被珍视+前任后悔, 平台: 抖音/小程序, 撒糖密度决定完播",
                    "银发温情流": "目标: 50岁+, 爽感=第二春/家庭和解, 平台: 视频号, 流量洼地但受众付费弱",
                    "知识型流": "目标: 高知群体, 爽感=智力碾压+文化自信, 平台: B站/微信, 单价高但天花板低",
                    "院线电影": "目标: 大众, 爽感=情感共鸣+奇观, 需300万+预算, 收入靠票房分账",
                },
                "rationale": "赛道决定一切后续: 选角/布光/节奏/时长全部受其约束。赛道选错, 后面全错。",
                "failure_modes": [
                    "盲目追爆款赛道=红海价格战, 同质化被算法降权",
                    "受众画像模糊=选角/钩子/撒糖点全部失焦",
                    "低估成本=后期被迫砍戏, 全片崩坏",
                ],
                "measurement": "立项前必须有: 1页受众画像 + 3部对标片 + 平台算法规则清单 + 预算明细",
                "cross_refs": ["short_drama_patterns.audience_archetypes", "viral_video_techniques.algorithm_signals"],
            },
            "D0_2_reference_deconstruction": {
                "cn": "对标片拆解",
                "trigger": "选定赛道后, 必须拆解3-5部同赛道爆款",
                "method": "逐15秒切片: 记录每段的 钩子类型/情绪值/反转点/转场/时长/BGM节拍。累计成'赛道节奏模板'",
                "failure_modes": ["只看一部就立项=偶然性大", "对标过时(2年前爆款)的节奏已失效"],
                "cross_refs": ["genre_profiles", "director_styles.style_application_guide.combination_examples"],
            },
        },
    },

    # ========================================================
    # PHASE 1 — 剧作 (Screenwriting)
    # 总导演对剧本的核心控制: 结构骨架+情绪曲线+角色弧光+伏笔回收地图
    # ========================================================
    "P1_screenwriting": {
        "phase_cn": "剧作",
        "core_questions": [
            "故事核(logline)一句话能说清吗? 说不清=没想透",
            "用了什么结构骨架? 这个骨架适合此类型吗?",
            "主角弧光起点→终点是什么? 观众为什么在乎TA?",
            "情绪曲线是否张弛有度? 有没有连续高潮脱敏?",
            "伏笔都埋了吗? 回收点在哪? 红鲱鱼区分了吗?",
        ],
        "decision_points": {
            "D1_1_structure": {
                "cn": "结构骨架选择",
                "trigger": "确定故事核后, 选定叙事结构",
                "decision_tree": {
                    "if 悬疑类型": "→ mystery_reveal(层层剥洋葱)",
                    "if 英雄成长": "→ hero_journey(12节拍)",
                    "if 商业主流": "→ save_the_cat(15节拍)",
                    "if 东方文艺": "→ kishōtenketsu(起承转合)",
                    "if 短剧爽文": "→ short_drama_hook(3秒钩子+15秒反转)",
                    "if 复仇线": "→ buildup_payoff(伏笔密集回收)",
                    "if 多线交织": "→ parallel_convergence(平行交汇)",
                },
                "rationale": "结构不是装饰, 是观众预期管理的工具。错配结构=观众觉得'怪'但说不出原因。",
                "failure_modes": [
                    "短剧用三幕式=前15秒没钩子, 完播率崩盘",
                    "文艺片用救猫咪=商业节拍破坏诗性",
                    "结构对了但beat位置算错=中点落在60%而非50%, 后半拖沓",
                ],
                "measurement": "节拍表进度核对: 每个beat的position%必须落在实际进度附近(±12%)",
                "cross_refs": ["narrative_structures", "director_engine.DIRECTOR_NARRATIVE_AFFINITY"],
            },
            "D1_2_emotion_curve": {
                "cn": "情绪曲线设计",
                "trigger": "结构定后, 为每个beat标注情绪值(0-1)与强度(0-1)",
                "principles": [
                    "never_flat: 平静场景也需微小波动(±0.1)",
                    "contrast_amplifies: 高点因低点够低才高, 先压再弹",
                    "rest_before_peak: 最高潮前必有短暂平静(深呼吸)",
                    "aftermath_matters: 高潮后余波比高潮本身更留印象",
                    "no_double_peak: 两个>0.8高潮之间必须有<0.4的喘息",
                ],
                "curve_templates": ["standard_arc","rollercoaster","slow_burn","descent","oscillation"],
                "failure_modes": [
                    "全程高强度=观众30秒内脱敏疲劳",
                    "全程低落=观众无聊划走(短视频尤甚)",
                    "情绪跳跃无过程=观众出戏",
                ],
                "measurement": "相邻beat情绪差: 渐变<0.2, 拐点>0.3, 禁止无标记的>0.4突变",
                "cross_refs": ["emotion_rendering.emotion_curve_design", "director_engine._build_pacing_guide"],
            },
            "D1_3_character_arc": {
                "cn": "角色弧光",
                "trigger": "主角必须有起点状态→终点状态的可视化变化",
                "arc_types": {
                    "positive_arc": "想要→需要→获得需要(《飞屋》)",
                    "flat_arc": "主角不变, 改变周围(《阿甘》)",
                    "corruption_arc": "好人→堕落(《教父2》Michael)",
                    "disillusionment": "信念→幻灭(《现代启示录》)",
                },
                "failure_modes": ["主角无弧光=观众不在乎TA的成败", "弧光突变无过程=不可信"],
                "cross_refs": ["performance_system.character_archetypes"],
            },
            "D1_4_foreshadow_map": {
                "cn": "伏笔/回收地图",
                "trigger": "重要回收必须有2-3次不经意铺垫",
                "rule": "契诃夫之枪: 第一幕墙上的枪第三幕必须开火",
                "timing": "短剧伏笔→回收间隔3-8集(观众记忆窗口短); 长片可跨幕",
                "failure_modes": ["埋了不回=观众困惑", "回收冲击<埋设印象=失望", "太早回=无悬念"],
                "cross_refs": ["emotion_rendering.foreshadowing_payoff"],
            },
        },
    },

    # ========================================================
    # PHASE 2 — 前期筹备 (Pre-production)
    # 选角/采景/美术/服化/分镜/通告——把剧本翻译成可拍计划
    # ========================================================
    "P2_preproduction": {
        "phase_cn": "前期筹备",
        "core_questions": [
            "选角是否同时满足: 外貌气质+表演力+商业价值+档期预算?",
            "采景是否支持空间叙事(楼上楼下=阶级)? 光照条件够吗?",
            "色彩方案是否统一到每场戏? 服装色彩=角色弧光外化了吗?",
            "分镜是否每个shot都有: 景别/角度/运镜/时长/转场/连续性标注?",
        ],
        "decision_points": {
            "D2_1_casting": {
                "cn": "选角矩阵",
                "trigger": "主角/配角的选角决策",
                "matrix": {
                    "外貌气质": "是否符合角色设定+受众审美?",
                    "表演力": "能否完成微表情/长镜头/爆发戏?",
                    "商业价值": "是否有自带流量(短剧尤其看重)?",
                    "档期预算": "档期是否冲突? 片酬是否超预算?",
                },
                "weighting": "短剧: 商业价值>外貌>表演力; 院线: 表演力>外貌>商业价值",
                "failure_modes": ["流量演员表演力不足=爆发戏崩", "气质不符=观众出戏", "超预算=被迫砍戏"],
            },
            "D2_2_location_scout": {
                "cn": "采景决策",
                "trigger": "确定拍摄场地",
                "criteria": [
                    "空间叙事潜力(垂直空间=阶级, 门窗=困局)",
                    "自然光条件(朝向/时段/可控性)",
                    "声学条件(环境噪声/混响)",
                    "拍摄可行性(电力/ permits/天气contingency)",
                ],
                "failure_modes": ["景美但光照不可控=被迫延期", "声学差=后期补录成本爆"],
            },
            "D2_3_color_design": {
                "cn": "色彩方案设计",
                "trigger": "全片色彩规划, 每场戏专属色方案",
                "method": "主色+辅助色+点缀色三层; 角色弧光用色彩变化外化(白→红=觉醒)",
                "cross_refs": ["master_cinematography.color_psychology", "genre_profiles.*.visual_language.color"],
            },
            "D2_4_shotlist_storyboard": {
                "cn": "分镜脚本",
                "trigger": "剧本→可拍分镜",
                "per_shot_required": ["景别","角度","运镜","时长","转场","连续性标注","台词绑定"],
                "cross_refs": ["shot_vocabulary", "master_cinematography.shot_types"],
            },
        },
    },

    # ========================================================
    # PHASE 3 — 拍摄现场 (Production / Shoot)
    # 摄影指导/灯光/调度/表演/收音/连戏——现场每一镜的决策
    # ========================================================
    "P3_production": {
        "phase_cn": "拍摄现场",
        "core_questions": [
            "这镜的机位/焦段/光圈/快门/ISO/色温——每个参数的叙事理由?",
            "光位/光质/光比/色温是否服务情绪且不破坏连戏?",
            "演员走位与机位关系? 180度轴线守了吗?",
            "表演的潜台词与机位焦点是否同步?",
        ],
        "decision_points": {
            "D3_1_cinematography": {
                "cn": "摄影指导决策(每镜6参数)",
                "trigger": "每镜开机前",
                "params": ["机位位置","焦段","光圈","快门","ISO","色温"],
                "rationale_each": {
                    "机位": "决定观众与角色的权力关系(仰拍=权威,俯拍=弱势)",
                    "焦段": "决定空间感(广角=包裹/变形,长焦=压缩/偷窥)",
                    "光圈": "决定景深(浅=隔离,深=信息全)",
                    "快门": "决定运动模糊(180度法则=电影感)",
                    "ISO": "决定噪点(低=干净,高=纪实粗糙)",
                    "色温": "决定情绪冷暖(3200K暖/5600K冷)",
                },
                "cross_refs": ["master_cinematography.lens_language","depth_of_field","lighting_advanced"],
            },
            "D3_2_lighting": {
                "cn": "灯光设计",
                "trigger": "每场戏布光方案",
                "params": ["光位","光质","光比","色温","动机光源"],
                "principles": ["动机光源必须合理(窗/灯/月/火)","连戏内光线方向不变","光比=情绪强度"],
                "cross_refs": ["master_cinematography.lighting","lighting_advanced"],
            },
            "D3_3_mise_en_scene": {
                "cn": "场面调度",
                "trigger": "演员走位与机位的组合设计",
                "elements": ["走位路径","与机位距离","道具互动","群演层次","空间利用"],
                "cross_refs": ["performance_system.movement_phrases","group_choreography"],
            },
            "D3_4_performance_direction": {
                "cn": "表演指导",
                "trigger": "每场戏的表演目标",
                "method": "潜台词+情绪记忆+机位焦点同步",
                "cross_refs": ["performance_system"],
            },
            "D3_5_continuity": {
                "cn": "连戏管理",
                "trigger": "跨镜头一致性",
                "rules": ["180度轴线","30度规则","视线匹配","运动方向一致","道具位置","光线方向","色调"],
                "failure_modes": ["越轴=观众空间感崩","道具移位=穿帮"],
                "cross_refs": ["shot_vocabulary.continuity_markers","transition_grammar.transition_rules.continuity"],
            },
            "D3_6_production_sound": {
                "cn": "现场收音",
                "trigger": "对白/环境/动效分离录制",
                "principles": ["对白优先清晰(领夹/挑杆)","环境单独录空场","动效后期补录(Foley)"],
            },
        },
    },

    # ========================================================
    # PHASE 4 — 后期 (Post-production)
    # 剪辑/调色/声音/配乐/VFX/平台适配
    # ========================================================
    "P4_postproduction": {
        "phase_cn": "后期",
        "core_questions": [
            "剪辑节奏是否服务情绪曲线? 蒙太奇学派选对了吗?",
            "调色是否强化情绪且风格统一? 一级二级调色分工?",
            "声画关系? 何时声先于画(J切)何时画先于声(L切)?",
            "配乐主题动机是否贯穿? 何时该静默?",
        ],
        "decision_points": {
            "D4_1_editing": {
                "cn": "剪辑",
                "trigger": "素材到成片",
                "schools": ["度量/节奏/调性/理性/平行/联想蒙太奇"],
                "principles": ["节奏=呼吸(紧张短促,抒情绵长)","声画关系(J/L切)","轴线/连戏","高潮后留余韵镜"],
                "cross_refs": ["transition_grammar","master_cinematography.visual_rhythm"],
            },
            "D4_2_color_grading": {
                "cn": "调色",
                "trigger": "成片调色",
                "levels": {
                    "primary": "一级: 校色(白平衡/曝光/对比)统一基准",
                    "secondary": "二级: 局部调色(肤色保护/天空压/区域强调)",
                    "creative": "创意: 整体风格LUT(青橙/去饱和/霓虹)",
                },
                "principle": "调色=情绪外化, 同一时空色调一致, 情绪转折用色温变化",
                "cross_refs": ["master_cinematography.color_psychology"],
            },
            "D4_3_sound_design": {
                "cn": "声音设计",
                "trigger": "声轨设计",
                "layers": ["对白","动效(Foley)","环境","音乐","静默"],
                "principles": ["静默比巨响更有力","环境音层叠=压力上升","音乐戛然而止=最震撼"],
                "cross_refs": ["emotion_rendering.scene_emotion_rendering.atmosphere_building.sound"],
            },
            "D4_4_music": {
                "cn": "配乐",
                "trigger": "配乐设计",
                "method": "主题动机贯穿, 变奏随情绪曲线, 高潮前留静默蓄势",
            },
            "D4_5_vfx": {
                "cn": "特效",
                "types": {"invisible": "隐形特效(换天/擦穿帮)不引人注意","spectacle": "奇观特效(法术/爆炸)制造震撼"},
                "principle": "特效服务叙事而非炫技, 隐形>奇观(除非类型片)",
            },
        },
    },

    # ========================================================
    # PHASE 5 — 发行运营 (Distribution / Analytics)
    # 完播/算法/AB测试/数据回流——拍完不是结束, 是开始
    # ========================================================
    "P5_distribution": {
        "phase_cn": "发行运营",
        "core_questions": [
            "前3秒完播率达标吗? 前15秒呢? 中段流失在哪?",
            "首发平台算法偏好什么信号? 我都给齐了吗?",
            "封面/标题/前3秒AB测试了吗?",
            "数据回流到下次选题了吗?",
        ],
        "decision_points": {
            "D5_1_completion_curve": {
                "cn": "完播率优化",
                "trigger": "成片上线后看留存曲线",
                "key_moments": ["0-3秒: 视觉钩子决定是否划走","3-15秒: 第一个反转决定是否留存","中段每30秒: 需一个小钩子","结尾: 决定是否分享/关注"],
                "failure_modes": ["前3秒无冲击=70%划走","中段平=完播崩","结尾无共鸣=不分享不关注"],
                "cross_refs": ["viral_video_techniques.pacing_formulas","short_drama_patterns.vertical_video_rules.pacing"],
            },
            "D5_2_platform_algorithm": {
                "cn": "平台算法适配",
                "trigger": "按首发平台优化",
                "platform_diff": {
                    "抖音": "完播率权重最高, 前3秒定生死, BGM用热门加权",
                    "快手": "老铁文化, 真实感>精致, 关注转化权重高",
                    "B站": "中长内容友好, 弹幕互动, UP主人设重要",
                    "视频号": "社交推荐, 适合银发/家庭温情, 转发>点赞",
                    "YouTube": "前30秒CTR+观看时长, 缩略图决定点击",
                },
                "cross_refs": ["viral_video_techniques.platform_optimization","algorithm_signals"],
            },
            "D5_3_ab_testing": {
                "cn": "AB测试",
                "trigger": "上线初期测封面/标题/前3秒",
                "method": "同片不同封面/标题/钩子, 24小时看数据, 留胜者",
            },
            "D5_4_data_feedback": {
                "cn": "数据回流",
                "trigger": "每部片上线后2周复盘",
                "feedback": ["完播曲线低点→下次优化该段","分享率→共鸣点复制","关注转化→人设强化"],
            },
        },
    },

    # ========================================================
    # 跨阶段铁律 (Cross-phase invariants)
    # ========================================================
    "cross_phase_invariants": {
        "color_consistency": "色彩方案从P2设计贯穿P3布光P4调色, 全程一致",
        "character_consistency": "角色外貌/服装关键词从P2定到P3连戏, AI生成跨镜一致",
        "emotion_arc_consistency": "情绪曲线从P1设计贯穿P3表演P4剪辑P5完播, 全程对齐beat位置",
        "style_unification": "导演风格从P0选定贯穿全流程, 每个决策点自检'这是否符合选定导演的语法'",
    },
}

# ============================================================
# 决策点快速检索: 冓情况找到该用哪个决策点
# ============================================================
PIPELINE_QUICKREF = {
    "不知道拍什么": "P0_development.D0_1_track_selection",
    "拍给谁看": "P0_development.D0_1_track_selection",
    "故事结构怎么选": "P1_screenwriting.D1_1_structure",
    "情绪曲线设计": "P1_screenwriting.D1_2_emotion_curve",
    "主角没有变化": "P1_screenwriting.D1_3_character_arc",
    "伏笔怎么埋": "P1_screenwriting.D1_4_foreshadow_map",
    "选角": "P2_preproduction.D2_1_casting",
    "采景": "P2_preproduction.D2_2_location_scout",
    "色彩方案": "P2_preproduction.D2_3_color_design",
    "分镜": "P2_preproduction.D2_4_shotlist_storyboard",
    "机位/焦段/光圈": "P3_production.D3_1_cinematography",
    "布光": "P3_production.D3_2_lighting",
    "演员走位": "P3_production.D3_3_mise_en_scene",
    "表演指导": "P3_production.D3_4_performance_direction",
    "连戏/越轴": "P3_production.D3_5_continuity",
    "收音": "P3_production.D3_6_production_sound",
    "剪辑节奏": "P4_postproduction.D4_1_editing",
    "调色": "P4_postproduction.D4_2_color_grading",
    "声音设计": "P4_postproduction.D4_3_sound_design",
    "配乐": "P4_postproduction.D4_4_music",
    "特效": "P4_postproduction.D4_5_vfx",
    "完播率低": "P5_distribution.D5_1_completion_curve",
    "平台算法": "P5_distribution.D5_2_platform_algorithm",
    "封面标题测试": "P5_distribution.D5_3_ab_testing",
    "数据复盘": "P5_distribution.D5_4_data_feedback",
}
