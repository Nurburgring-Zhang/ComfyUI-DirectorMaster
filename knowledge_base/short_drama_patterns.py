# ============================================================
# 短剧爆款模式知识库
# 来源：2021-2026年热门短剧平台数据分析
# ============================================================

SHORT_DRAMA_PATTERNS = {
    "opening_hooks": {
        "visual_shock": {
            "cn": "视觉冲击开场",
            "techniques": [
                "反物理画面(物品悬浮/时间冻结/空间扭曲)",
                "强烈情绪面部特写(愤怒到变形/泪流满面/震惊到僵住)",
                "中间状态入场(正在跑/正在跌倒/正在被打)",
                "极端对比(华丽婚礼vs泥泞地面/笑脸vs背后的危险)",
            ],
            "duration": "0-3秒",
        },
        "information_gap": {
            "cn": "信息缺口开场",
            "techniques": [
                "话说一半('其实你根本不知道他是——')",
                "看到了什么但观众看不到(角色看手机屏幕变脸)",
                "动作未完成(手伸向按钮停住/门即将打开)",
                "倒叙提问('三天前我还不知道,我的丈夫其实是——')",
            ],
            "duration": "0-5秒",
        },
        "identity_reversal": {
            "cn": "身份反转开场",
            "techniques": [
                "被羞辱的人收到一通电话后眼神突变",
                "所有人嘲笑的对象突然被超跑车队接走",
                "清洁工打扫时不小心暴露了军衔徽章",
                "被赶出家门的人在街对面的豪宅里按下指纹锁",
            ],
            "duration": "3-10秒",
        },
        "emotional_bomb": {
            "cn": "情绪炸弹开场",
            "techniques": [
                "直接从哭戏开始(不解释原因)",
                "两人对峙的最激烈一句话作为第一句台词",
                "一巴掌/一跪/一个绝望的动作作为第一个画面",
                "极端的不公平场面(所有人对一个人的欺压)",
            ],
            "duration": "0-3秒",
        },
    },

    "narrative_formulas": {
        "face_slapping_cascade": {
            "cn": "打脸流/逆袭爽文",
            "structure": "被欺压(3-5集积蓄)→小打脸(第6-8集释放)→再被压(9-12集)→大打脸(13-15集爆发)→更大危机→终极打脸",
            "key_principle": "压得越深弹得越高,每次打脸的级别必须递增",
            "emotional_loop": "憋屈→憋屈加倍→一点释放→更大憋屈→彻底释放(观众爽感来自落差)",
        },
        "hidden_identity": {
            "cn": "隐藏身份/扮猪吃虎",
            "structure": "低调隐藏→被人看不起→小露一手→继续低调→大危机逼迫暴露→全场震惊",
            "character_pairs": [
                "快递员 ↔ 龙王/首富",
                "赘婿 ↔ 战神归来",
                "保安 ↔ 最强兵王",
                "清洁工 ↔ 天才医生",
                "灰姑娘 ↔ 真正的千金",
            ],
            "key_principle": "身份反差越大越爽,暴露时机越晚观众越满足",
        },
        "sweet_romance_escalation": {
            "cn": "甜宠升级",
            "structure": "偶遇→误会→日久生情→互相心动→小甜蜜→误会分离→重逢更甜",
            "sugar_points": [
                "不经意的身体接触(接住/擦汗/拉手)",
                "只对TA一个人的温柔反差",
                "公开场合的护短/宣布所有权",
                "生病/受伤时的照顾(最经典虐→甜转换)",
                "被第三者看到的独家亲密瞬间",
            ],
            "key_principle": "甜度必须递增,同一水平的甜不能重复,每次必须比上次更进一步",
        },
        "revenge_rebirth": {
            "cn": "重生复仇",
            "structure": "惨死/重大失败→重生回到关键节点→利用未来知识→逐个击破敌人→反转命运",
            "power_sources": [
                "前世记忆(知道谁是敌人)",
                "金手指(带着系统/空间/技能重生)",
                "时间优势(知道哪些股票涨/谁会出事)",
                "情感觉醒(前世太善良这辈子该狠)",
            ],
            "key_principle": "观众通过重生者的上帝视角看着坏人不知不觉走进圈套,享受智力碾压的快感",
        },
        "cliff_build": {
            "cn": "悬崖修炼(仙侠/修真)",
            "structure": "被打入深渊/废掉修为→绝境中偶得机缘→秘密修炼→一朝出世碾压群雄",
            "power_visualization": [
                "修炼时周身出现光圈/符文",
                "突破时天地异象(雷劫/花开/星辰移位)",
                "战斗时的视觉等级对比(对方震惊脸)",
                "能力展示的递进(一指→一掌→一剑→法天象地)",
            ],
        },
    },

    "vertical_video_rules": {
        "composition": {
            "center_axis": "主体始终在画面纵轴中心线上,左右偏移不超过15%",
            "eye_line": "角色眼睛置于画面上1/3分割线位置",
            "face_ratio": "情感场景中面部占画面面积70%以上",
            "safe_zones": "顶部留状态栏空间,底部留导航/弹幕空间",
            "depth_over_width": "利用纵向结构(楼梯/高楼/门框)创造纵深而非横向展开",
        },
        "camera_movement": {
            "forbidden": "禁止大幅度横摇(水平运动在竖屏中效果差)",
            "recommended": [
                "推拉(纵深运动,加强压迫感或释放感)",
                "微抬压(垂直方向替代横摇)",
                "固定机位(对话场景,稳定专业)",
                "纵向升降(穿越楼层/天空)",
                "极缓推向面部(情绪积蓄)",
            ],
        },
        "pacing": {
            "new_info_every": "10秒",
            "mini_reversal_every": "15-20秒",
            "scene_max_length": "15-30秒",
            "shot_duration_emotional": "3-5秒/镜",
            "shot_duration_dialogue": "5-8秒/镜",
            "zero_dead_air": "每一帧都在推进情节或情绪",
        },
    },

    "cliffhanger_techniques": {
        "half_spoken_truth": {
            "cn": "话只说一半",
            "example": "'其实你的亲生父亲是——'（画面黑）",
            "principle": "在信息传递到99%时戛然而止",
        },
        "half_face_slap": {
            "cn": "打脸只打一半",
            "example": "电话打出去了,但没给观众看对方的反应",
            "principle": "观众已经知道结果会很爽,但不给看爽的瞬间",
        },
        "one_second_before": {
            "cn": "揭晓前一秒",
            "example": "所有人看向门口,门慢慢打开——（结束）",
            "principle": "利用群体反应暗示即将发生的事的震撼程度",
        },
        "countdown_pressure": {
            "cn": "倒计时压迫",
            "example": "炸弹还有3秒/签字截止还有1天/航班起飞前30分钟",
            "principle": "外部不可逆的时间压力制造紧迫感",
        },
        "new_threat_entry": {
            "cn": "新威胁入场",
            "example": "刚解决一个危机,背后传来脚步声/电话响起",
            "principle": "观众以为安全了的瞬间引入新的不安",
        },
    },

    "audience_archetypes": {
        "male_frequency": {
            "cn": "男频观众",
            "core_desire": "力量幻想+地位跃升+被尊重",
            "keywords": ["战神", "龙王", "首富", "赘婿逆袭", "扮猪吃虎"],
            "satisfaction_formula": "被蔑视→展现实力→所有人跪",
        },
        "female_frequency": {
            "cn": "女频观众",
            "core_desire": "被爱+自我价值+情感满足",
            "keywords": ["甜宠", "霸总独宠", "重生复仇", "大女主", "觉醒"],
            "satisfaction_formula": "被辜负→自己强大起来→前任后悔+新人捧在手心",
        },
        "silver_hair": {
            "cn": "银发/中年观众",
            "core_desire": "第二春+被需要+家庭和解",
            "keywords": ["中年爱情", "闪婚老伴", "退休生活", "家庭温情"],
            "satisfaction_formula": "人到中年不被看好→遇到真心人/事业第二春→证明永远不晚",
        },
        "intellectual": {
            "cn": "知识型观众",
            "core_desire": "智力优越感+文化认同+深度内容",
            "keywords": ["穿越知识流", "诗词/历史梗", "智斗", "权谋"],
            "satisfaction_formula": "用知识/智慧碾压对手→文化自信→深层满足",
        },
    },

    "production_economics": {
        "ai_drama_2026": {
            "cycle": "7-14天",
            "cost": "1.5-2万元",
            "team": "3-8人",
            "output_share": "95%产量(月产12.2万部)",
        },
        "true_person_2026": {
            "cycle": "20-30天",
            "cost": "30-50万元",
            "team": "40-50人",
            "output_share": "5%产量但占据流量高地(春节期间25倍于AI剧观看量)",
        },
        "premium_example": {
            "title": "家里家外",
            "budget": "300万元",
            "shoot_days": "17天",
            "rating": "豆瓣8.3",
            "views": "30亿+",
        },
    },

    # ========================================================
    # 扩充: 更多爆款叙事公式
    # ========================================================
    "narrative_formulas_extended": {
        "regret_redemption": {
            "cn": "追妻火葬场/后悔流",
            "structure": "男主伤害女主→女主心死离开/假死→男主发现真相→疯狂寻找悔恨→重逢时女主已蜕变",
            "key_principle": "让虐心主角的'迟来的深情'比一开始的甜更戳人。观众要的是施害者的彻底崩溃与赎罪",
            "visual_anchor": "前期男主冷漠仰拍→后期男主狼狈俯拍的角度反转",
        },
        "true_false_daughter": {
            "cn": "真假千金/替身上位",
            "structure": "假千金鸠占鹊巢→真千金回归受冷落→真千金低调展现实力→身份真相大白→假千金结局",
            "key_principle": "身份错位的爽感+被偏待者的委屈释放。真相揭穿的那一刻要给足所有人震惊的群像反应",
        },
        "contract_marriage": {
            "cn": "契约婚姻/先婚后爱",
            "structure": "被迫契约→同住屋檐→日常摩擦→暗生情愫→契约到期不愿放手→真心暴露",
            "key_principle": "日久生情的甜来自生活细节(早餐/接送/病中照顾),而非大场面。空间从疏远到亲密的可视化",
        },
        "academic_genius": {
            "cn": "学霸/扮猪吃虎校园流",
            "structure": "差生人设→考试惊艳→继续低调→天才身份逐步暴露→全场跪服",
            "key_principle": "学术碾压的爽感=智力优越感。每次'暴露'都要配上旁观者震惊的群像",
        },
        "ceo_secretary": {
            "cn": "总裁文/霸总甜宠",
            "structure": "误会相遇→女主进霸总公司→霸总独宠→情敌阻挠→公开宣布所有权→大团圆",
            "key_principle": "霸总的爽=对所有其他人冷酷唯独对女主温柔的反差。公开场合护短是高光",
        },
        "jianghu_undercover": {
            "cn": "江湖潜伏/扮猪吃虎(男频)",
            "structure": "战神/龙王隐姓埋名→被羞辱→低调展现实力→身份暴露碾压→称霸",
            "key_principle": "身份反差越大越爽,暴露前压得越低,暴露时反弹越高。所有欺压者的恐惧脸是核心",
        },
    },

    # ========================================================
    # 扩充: 钩子进阶技巧
    # ========================================================
    "hook_techniques_advanced": {
        "cold_open": {
            "cn": "冷开场",
            "technique": "直接进入冲突最激烈的一刻,不交代前因后果,让观众带着疑问看下去",
            "example": "开场就是女主把离婚协议拍在桌上,男主冷笑——为什么?",
        },
        "promise_break": {
            "cn": "承诺破坏",
            "technique": "开场展示一个美好承诺/约定,然后立刻展示它被打破",
            "example": "'我答应过妈妈会保护你'→镜头切到妹妹倒在血泊中",
        },
        "visual_paradox": {
            "cn": "视觉悖论",
            "technique": "展示一个不合常理的画面,迫使观众停留找答案",
            "example": "穿婚纱的女人站在葬礼花圈前;乞丐碗里有钻石",
        },
        "time_anchor": {
            "cn": "时间锚点",
            "technique": "用倒计时/时间标记制造紧迫",
            "example": "'距离她的死刑还有72小时'倒计时开场",
        },
        "role_reversal_open": {
            "cn": "身份对调开场",
            "technique": "展示与预期完全相反的身份关系",
            "example": "以为是老板训斥员工→镜头拉开,老板在给员工擦鞋",
        },
    },

    # ========================================================
    # 扩充: 反转类型全集
    # ========================================================
    "reversal_types_full": {
        "identity_reversal": "身份反转(乞丐是总裁/清洁工是天才/赘婿是战神)",
        "emotion_reversal": "情感反转(恨→爱/信任→背叛/放弃→坚持/虐→甜)",
        "power_reversal": "权力反转(弱者翻身/强者跌落/被欺者反杀)",
        "cognition_reversal": "认知反转(以为是A其实是B/以为敌是友/以为死是活)",
        "time_reversal": "时空反转(今天的决定来自未来/重生带着记忆)",
        "motive_reversal": "动机反转(以为为钱其实是为爱/以为害其实是救)",
        "alliance_reversal": "阵营反转(敌变友/友变敌/中立者关键时刻倒戈)",
        "value_reversal": "价值反转(嘲笑的东西成为救命稻草/珍视的成为毒药)",
    },

    # ========================================================
    # 扩充: 竖屏专属运镜与构图禁忌
    # ========================================================
    "vertical_advanced": {
        "composition_do": [
            "面部占画面70%+(情感场景)放大微表情",
            "主角始终在纵轴中心线(左右偏移<15%)",
            "利用纵向结构(楼梯/高楼/门框)造纵深",
            "双人构图利用身高差(男主俯视/女主仰视)",
            "上方1/3放眼线,下方留字幕/弹幕空间",
        ],
        "composition_dont": [
            "禁止大幅度横摇(水平运动在竖屏效果差)",
            "避免横向展开的广角全景(信息看不全)",
            "避免画面左右两侧放重要信息(易被裁切)",
            "避免太多横向并排的人物(竖屏看不清)",
        ],
        "movement_recommend": [
            "推拉(纵深运动,加强压迫/释放感)",
            "微抬压(垂直方向替代横摇)",
            "纵向升降(穿越楼层/天空/地下)",
            "极缓推向面部(情绪积蓄)",
            "急推特写+音效(爽点强化)",
        ],
    },
}


# ============================================================
# 短剧决策覆盖层 — 为关键模式补7维决策字段
# (保留原structure/key_principle/emotional_loop, 叠加trigger/failure/measurement等)
# ============================================================
SHORT_DRAMA_DECISION = {
    # ─── 开场钩子 ───
    "visual_shock": {
        "trigger": "短剧开场0-3秒/视觉冲击抓人/完播率生死线",
        "rationale": "前3秒70%观众去留。视觉冲击=抓住本能反应, 来不及思考就留下来。",
        "failure_modes": ["冲击与主题无关=欺诈感", "冲击过强后续接不住=完播崩", "冲击无新意=划走"],
        "measurement": "前3秒有视觉冲击, 与主题相关, 抓住70%+观众",
        "alternatives": ["information_gap(更悬念)", "emotional_bomb(更情绪)"],
        "cross_refs": {"pacing": "3秒生死线", "platform": "抖音/快手算法权重", "vertical": "竖屏冲击更直接"},
    },
    "information_gap": {
        "trigger": "短剧开场/信息缺口抓好奇/话说一半/看到了但观众看不到",
        "rationale": "给足够信息引起好奇但不给答案=好奇心驱动留存。是悬念式钩子。",
        "failure_modes": ["信息给太多=失悬念", "信息太少=观众不懂", "缺口不回收=失信"],
        "measurement": "前3秒制造信息缺口, 观众想知答案, 后续回收",
        "alternatives": ["visual_shock(更冲击)", "identity_reversal(更反转)"],
        "cross_refs": {"pacing": "3秒钩子", "narrative": "悬念驱动", "mystery": "信息缺口是悬念核心"},
    },
    "identity_reversal": {
        "trigger": "短剧开场/身份反转/被羞辱者收到电话眼神突变/清洁工暴露军衔",
        "rationale": "身份反差=爽感源头。开场即展示身份反转=抓住爽文受众本能。",
        "failure_modes": ["反转过早暴露=失悬念", "反差不够大=失爽", "反转无后续=泄气"],
        "measurement": "前3秒展示身份反转, 反差够大, 后续兑现",
        "alternatives": ["visual_shock(更冲击)", "emotional_bomb(更情绪)"],
        "cross_refs": {"pacing": "3秒钩子", "formula": "hidden_identity隐藏身份", "audience": "男频战神流"},
    },
    "emotional_bomb": {
        "trigger": "短剧开场/情绪炸弹/直接哭戏/一巴掌开场/极端不公平",
        "rationale": "直接进入情绪高点=抓住情感共鸣。情绪炸弹让观众瞬间代入。",
        "failure_modes": ["无前置=失情绪重量", "情绪过强=失真", "情绪与主题无关=欺诈"],
        "measurement": "前3秒情绪炸弹, 与主题相关, 抓住情感共鸣",
        "alternatives": ["visual_shock(更视觉)", "information_gap(更悬念)"],
        "cross_refs": {"pacing": "3秒钩子", "emotion": "情绪代入", "audience": "女频情感流"},
    },
    # ─── 叙事公式 ───
    "face_slapping_cascade": {
        "trigger": "男频战神流/打脸逆袭/被欺压后反弹/爽文核心",
        "rationale": "压得越深弹得越高。打脸级别递增=爽感递增, 每次打脸比上次更狠。",
        "failure_modes": ["压得不够深=失弹", "打脸不递增=疲劳", "打脸间隔过长=流失", "打脸无爽点细节=失爽"],
        "measurement": "打脸级别递增, 每次有爽点细节(全场震惊), 压弹落差明显",
        "alternatives": ["hidden_identity(更身份)", "revenge_rebirth(更复仇)"],
        "cross_refs": {"audience": "男频战神流", "pacing": "压→弹循环", "emotion": "憋屈→释放"},
    },
    "hidden_identity": {
        "trigger": "扮猪吃虎/隐藏身份/男频战神/女频千金/身份反差爽",
        "rationale": "身份反差越大越爽, 暴露时机越晚观众越满足。上帝视角看反派不知=爽。",
        "failure_modes": ["暴露过早=失悬念", "反差不够大=失爽", "暴露无全场震惊=失爽点"],
        "measurement": "身份反差大, 暴露晚, 暴露时全场震惊群像, 观众满足",
        "alternatives": ["face_slapping_cascade(更打脸)", "revenge_rebirth(更复仇)"],
        "cross_refs": {"audience": "男频战神/女频千金", "pacing": "低调→小露→大暴露", "performance": "暴露时群像震惊"},
    },
    "sweet_romance_escalation": {
        "trigger": "女频甜宠/甜度递增/虐甜交替/言情核心",
        "rationale": "甜度递增不重复=糖分持续升级。虐是甜的对照, 虐甜交替=情绪过山车。",
        "failure_modes": ["甜度原地踏步=失糖", "虐无理由=为虐而虐", "无反差萌=失心动", "HE无障碍=廉价"],
        "measurement": "甜度递增, 虐甜交替, 反差萌建立, HE有障碍",
        "alternatives": ["contract_marriage(更契约)", "ceo_secretary(更霸总)"],
        "cross_refs": {"audience": "女频甜宠流", "pacing": "甜度递升+虐甜交替", "emotion": "心动→深情→热恋"},
    },
    "revenge_rebirth": {
        "trigger": "重生复仇/带着未来知识/上帝视角看坏人入圈套/智力碾压",
        "rationale": "重生者上帝视角=观众享受智力碾压。看着坏人不知不觉走进圈套=爽感核心。",
        "failure_modes": ["无前世铺垫=失动机", "重生金手指过强=失悬念", "复仇无延迟=失爽", "坏人不蠢=失智力碾压"],
        "measurement": "有前世铺垫, 上帝视角清晰, 复仇有延迟, 坏人入圈套有逻辑",
        "alternatives": ["face_slapping_cascade(更打脸)", "hidden_identity(更身份)"],
        "cross_refs": {"audience": "女频复仇/男频重生", "pacing": "重生→布局→释放", "narrative": "上帝视角"},
    },
    "cliff_build": {
        "trigger": "仙侠修真/悬崖修炼/废掉修为后偶得机缘/出世碾压",
        "rationale": "废→机缘→秘密修炼→出世碾压=修真爽文核心。境界突破是节奏锚点。",
        "failure_modes": ["修炼无可视化=失爽", "突破无天地异象=失仙气", "出世碾压无震惊群像=失爽点", "境界无递进=失升级感"],
        "measurement": "境界有可视化, 突破有异象, 出世有震惊群像, 境界递进",
        "alternatives": ["hidden_identity(更身份)", "face_slapping_cascade(更打脸)"],
        "cross_refs": {"genre": "xianxia_cultivation", "pacing": "废→机缘→出世", "vfx": "境界可视化"},
    },
    "regret_redemption": {
        "trigger": "追妻火葬场/男主伤害女主后后悔/迟来的深情",
        "rationale": "让虐心主角的'迟来深情'比一开始的甜更戳。施害者彻底崩溃与赎罪=爽感。",
        "failure_modes": ["男主后悔过快=失重量", "女主原谅过快=失虐", "无前期虐=失对照"],
        "measurement": "有前期虐, 男主崩溃有过程, 女主蜕变, 赎罪有代价",
        "alternatives": ["sweet_romance_escalation(更甜)", "revenge_rebirth(更复仇)"],
        "cross_refs": {"audience": "女频追妻", "pacing": "虐→后悔→赎罪", "emotion": "虐心→迟来深情"},
    },
    "contract_marriage": {
        "trigger": "契约婚姻/先婚后爱/被迫契约→日久生情",
        "rationale": "日久生情的甜来自生活细节(早餐/接送/病中照顾), 空间从疏远到亲密可视化。",
        "failure_modes": ["无生活细节=失日久生情", "契约无冲突=失张力", "空间无变化=失亲密可视化"],
        "measurement": "有生活细节甜点, 契约有冲突, 空间从疏远到亲密",
        "alternatives": ["sweet_romance_escalation(更甜)", "ceo_secretary(更霸总)"],
        "cross_refs": {"audience": "女频甜宠", "pacing": "契约→同住→生情", "space": "空间疏远→亲密"},
    },
    "ceo_secretary": {
        "trigger": "霸总甜宠/总裁文/高冷总裁独宠女主/反差萌",
        "rationale": "霸总的爽=对所有人冷酷唯独对女主温柔的反差。公开护短是高光。",
        "failure_modes": ["霸总无反差=失萌", "反差无建立=突兀", "无公开护短=失高光"],
        "measurement": "有反差萌, 公开护短高光, 反差有建立",
        "alternatives": ["contract_marriage(更契约)", "sweet_romance_escalation(更甜)"],
        "cross_refs": {"audience": "女频霸总", "pacing": "高冷→独宠→护短", "performance": "反差萌是核心"},
    },
    # ─── 受众原型 ───
    "male_frequency": {
        "trigger": "男频观众/30-50岁男性/力量幻想+地位跃升+被尊重",
        "rationale": "男频爽感=被蔑视→展现实力→所有人跪。是力量幻想与地位跃升。",
        "failure_modes": ["无被蔑视=失弹", "实力展示无递进=失升级", "无所有人跪=失爽点"],
        "measurement": "有被蔑视, 实力递进展示, 所有人跪群像, 爽感达成",
        "alternatives": ["female_frequency(女频)", "intellectual(知识型)"],
        "cross_refs": {"formula": "face_slapping/hidden_identity", "pacing": "压→展→跪", "keywords": "战神/龙王/首富/赘婿"},
    },
    "female_frequency": {
        "trigger": "女频观众/18-35岁女性/被爱+自我价值+情感满足",
        "rationale": "女频爽感=被辜负→自己强大→前任后悔+新人捧在手心。是情感满足与自我价值。",
        "failure_modes": ["无被辜负=失弹", "强大无过程=失真", "前任不后悔=失爽", "新人不宠=失甜"],
        "measurement": "有被辜负, 强大有过程, 前任后悔, 新人捧, 情感满足",
        "alternatives": ["male_frequency(男频)", "silver_hair(银发)"],
        "cross_refs": {"formula": "revenge_rebirth/regret_redemption", "pacing": "辜负→强大→后悔+新人", "keywords": "甜宠/霸总/重生/大女主"},
    },
    "silver_hair": {
        "trigger": "银发/中年观众/50岁+/第二春+被需要+家庭和解",
        "rationale": "银发爽感=人到中年不被看好→遇到真心人/事业第二春→证明永远不晚。",
        "failure_modes": ["无中年困境=失弹", "第二春无真诚=失暖", "无家庭和解=失共鸣"],
        "measurement": "有中年困境, 第二春真诚, 家庭和解, 共鸣达成",
        "alternatives": ["female_frequency(女频)", "family_warmth(家庭)"],
        "cross_refs": {"platform": "视频号权重高", "pacing": "困境→第二春→和解", "keywords": "中年爱情/闪婚老伴/退休"},
    },
    "intellectual": {
        "trigger": "知识型观众/高知/智力优越感+文化认同+深度内容",
        "rationale": "知识型爽感=用知识/智慧碾压对手+文化自信。是智力优越感。",
        "failure_modes": ["无知识碾压=失爽", "知识过浅=失优越", "无文化认同=失共鸣"],
        "measurement": "有知识碾压, 知识有深度, 文化认同, 智力优越感",
        "alternatives": ["male_frequency(男频)", "female_frequency(女频)"],
        "cross_refs": {"platform": "B站/微信权重高", "pacing": "用知识→碾压→自信", "keywords": "穿越知识流/诗词/智斗"},
    },
}


def get_short_drama_with_decision(pattern_key):
    """合并短剧模式基础信息 + 决策覆盖层"""
    base = {}
    for section in ("opening_hooks", "narrative_formulas", "narrative_formulas_extended",
                    "cliffhanger_techniques", "audience_archetypes"):
        if pattern_key in SHORT_DRAMA_PATTERNS.get(section, {}):
            base = dict(SHORT_DRAMA_PATTERNS[section][pattern_key])
            break
    decision = SHORT_DRAMA_DECISION.get(pattern_key, {})
    base.update(decision)
    return base

