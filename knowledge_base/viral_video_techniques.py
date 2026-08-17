# ============================================================
# 社交媒体爆款短视频技巧库
# 来源：TikTok/抖音/快手/YouTube Shorts 10000+爆款视频分析
# ============================================================

VIRAL_VIDEO_TECHNIQUES = {
    "attention_mechanics": {
        "pattern_interrupt": {
            "cn": "模式打断",
            "description": "打破观众正常浏览节奏的视觉/听觉冲击",
            "techniques": [
                "极端画面比例(巨大vs微小/超近vs超远)",
                "非常规角度(颠倒/极端倾斜/虫视角)",
                "声音断裂(突然静音/突然巨响/ASMR极端)",
                "色彩冲击(全黑白中的一抹红/画面突然变色)",
                "打破第四面墙(直视镜头/对观众说话)",
            ],
            "timing": "必须在0.5秒内发生,否则观众已经划走",
        },
        "curiosity_gap": {
            "cn": "好奇心缺口",
            "description": "给出足够信息引起好奇但不给答案",
            "visual_cues": [
                "被遮挡的关键信息(马赛克/手遮/角度遮)",
                "文字预告但画面延迟('接下来的事让所有人震惊')",
                "进程条/倒计时暗示即将发生什么",
                "角色的震惊反应但不展示他们看到的东西",
            ],
        },
        "dopamine_loops": {
            "cn": "多巴胺循环",
            "description": "持续的奖励-期待循环让观众无法停止",
            "structure": [
                "预期(即将发生什么)→满足(发生了)→新预期(但还有更多)",
                "挑战(能做到吗)→结果(做到了!)→升级(更难的来了)",
                "谜题(什么意思)→揭示(原来如此)→新谜题(但等等...)",
            ],
            "interval": "每5-8秒提供一次小满足/新预期",
        },
    },

    "visual_storytelling": {
        "show_dont_tell": {
            "cn": "展示而非叙述",
            "principles": [
                "用一个动作代替一段解释(摘下婚戒=离婚)",
                "环境变化代替时间描述(绿叶→黄叶→雪)",
                "物品特写传递信息(空酒瓶=酗酒/堆满书桌=学霸)",
                "表情变化代替内心独白(3秒微表情>30秒旁白)",
            ],
        },
        "visual_metaphor": {
            "cn": "视觉隐喻",
            "common_metaphors": {
                "cage_prison": "笼子/围栏/铁窗→被困/不自由",
                "mirror": "镜子/倒影→自我认知/双重身份",
                "stairs_up_down": "上楼梯→进步; 下楼梯→堕落",
                "light_dark": "走向光→希望; 走入暗→绝望",
                "water": "平静水面→内心平和; 暴风雨→内心翻涌",
                "clock": "时钟/沙漏→时间压力/生命流逝",
                "door": "打开门→新可能; 关门→拒绝/结束",
                "chain": "链条/绳索→束缚; 断裂→解放",
            },
        },
        "emotional_anchoring": {
            "cn": "情感锚定",
            "description": "用重复出现的视觉元素锚定特定情感",
            "technique": [
                "颜色锚定(每次出现红色→危险/爱情)",
                "物品锚定(戒指=承诺、照片=回忆、刀=威胁)",
                "构图锚定(框中框=被困时都用此构图)",
                "光线锚定(逆光=美好回忆、底光=恐惧)",
                "音效锚定(特定音效→特定角色/情绪)",
            ],
        },
    },

    "pacing_formulas": {
        "15s_format": {
            "cn": "15秒极短视频",
            "structure": "钩子(2s)→主体(10s)→反转/结尾(3s)",
            "rules": [
                "只讲一个点,一个情绪,一个信息",
                "无废帧:每一帧都在传递信息",
                "文字辅助:配合字幕加速信息传递",
                "重复观看价值:结尾让人想重新看一遍",
            ],
        },
        "60s_format": {
            "cn": "60秒短视频",
            "structure": "钩子(3s)→建立(12s)→发展(20s)→高潮(15s)→结尾(10s)",
            "rules": [
                "每15秒一个节奏点(新信息/反转/升级)",
                "中段不能平:必须有一个mini转折",
                "结尾必须超越开头(情绪/信息量)",
                "BGM节拍与内容节奏严格同步",
            ],
        },
        "3min_format": {
            "cn": "3分钟短剧/故事",
            "structure": "钩子(5s)→建立(20s)→冲突(40s)→升级(40s)→高潮(30s)→余韵(15s)",
            "rules": [
                "每30秒检查:观众是否有理由继续看",
                "情绪不能重复:同一水平的情绪出现两次观众就走",
                "必须有记忆点:一个画面/一句台词让人记住",
                "结尾决定是否被分享:共鸣/震惊/温暖最易分享",
            ],
        },
    },

    "engagement_triggers": {
        "emotional_triggers": {
            "empathy": "观众代入角色情感(被欺负/被误解/被感动)",
            "justice": "正义感被激发(坏人被惩罚/弱者被帮助)",
            "superiority": "智力优越感(观众知道角色不知道的信息)",
            "nostalgia": "唤起共同记忆(童年/校园/初恋/家乡)",
            "awe": "超出预期的震撼(技术/美景/才华/勇气)",
            "controversy": "触发讨论欲(有争议的选择/两难困境)",
        },
        "interaction_hooks": {
            "cn": "互动钩子",
            "types": [
                "选择题('你会选A还是B'→评论区讨论)",
                "预测邀请('猜猜接下来发生什么')",
                "找不同/找彩蛋(让观众反复观看)",
                "未完待续(让观众关注等下一集)",
                "观点表态('同意的点赞'→数据加权)",
            ],
        },
        "shareability_factors": {
            "cn": "可分享因素",
            "factors": [
                "身份认同('这就是我/我们'→转发表态)",
                "实用价值(教程/技巧/知识→收藏转发)",
                "社交货币(显得我有品味/有见识→分享装逼)",
                "情感共振(感动/搞笑→分享传递情感)",
                "话题性(争议/热点→分享参与讨论)",
            ],
        },
    },

    "content_categories": {
        "transformation": {
            "cn": "变化/变装/对比",
            "hook": "before→after的视觉冲击",
            "camera": "固定机位+遮挡切换 或 旋转转场",
            "key": "反差越大越有效果,过程越快冲击越强",
        },
        "process_reveal": {
            "cn": "过程揭秘",
            "hook": "成品预览→如何做到的",
            "camera": "俯拍工作台/第一人称/延时摄影",
            "key": "关键步骤要慢放+特写,其余快进",
        },
        "story_time": {
            "cn": "故事叙述",
            "hook": "结果先行(我差点死了/我中了彩票)",
            "camera": "面部情绪特写+画面配合叙述",
            "key": "真实感>制作精良,情感>信息",
        },
        "skill_flex": {
            "cn": "技能展示",
            "hook": "最惊人的成果片段作为开头",
            "camera": "多角度+慢放+特写技术细节",
            "key": "动作的流畅度和自信感比难度更重要",
        },
        "emotional_micro_drama": {
            "cn": "情感微剧场",
            "hook": "冲突最激烈的一个画面/一句话",
            "camera": "面部特写为主+环境交代极简",
            "key": "表演要真实(微表情>大幅度表演),情绪要递进不要平",
        },
    },

    "platform_optimization": {
        "vertical_9_16": {
            "composition": "中心构图、上1/3放眼线、下1/5留字幕空间",
            "movement": "以纵向运动为主(升降/推拉)、避免横摇",
            "text_overlay": "关键信息文字浮层、字体大且居中、配色醒目",
            "safe_zones": "顶部60px(状态栏)、底部150px(导航/互动按钮)",
        },
        "sound_design": {
            "importance": "70%的病毒视频依赖声音(BGM/音效/人声)",
            "rules": [
                "开头2秒必须有声音(静音=划走)",
                "BGM节拍匹配画面切换点",
                "音效强化关键动作(打击感/惊叹感)",
                "人声清晰且有辨识度(不要淹没在BGM中)",
                "爆款BGM复用(算法识别热门音频加权推送)",
            ],
        },
        "algorithm_signals": {
            "cn": "算法友好信号",
            "signals": [
                "完播率:开头钩子+无死角内容+结尾悬念",
                "重复观看:隐藏细节/反转让人想看第二遍",
                "互动率:触发评论(争议/选择/猜测)",
                "分享率:情感共鸣/实用价值/社交货币",
                "关注转化:系列化内容+人设辨识度",
            ],
        },
    },

    "ai_video_specifics": {
        "prompt_to_visual": {
            "cn": "提示词到画面的优化",
            "rules": [
                "每个镜头描述必须包含:主体+动作+情绪+环境+光线+色调",
                "运动描述要精确:方向+速度+起终点",
                "表情描述要分层:整体情绪+关键面部部位",
                "环境要有层次:前景+中景+背景各一个元素",
                "色彩要有主次:主色调+辅助色+点缀色",
            ],
        },
        "consistency_across_shots": {
            "cn": "跨镜头一致性",
            "checklist": [
                "角色外貌描述保持关键词一致",
                "场景光线方向在同一场次中不变",
                "色调风格用相同的修饰词体系",
                "物品/道具描述每次出现用相同措辞",
                "情绪递进有逻辑(不能突然跳跃)",
            ],
        },
        "shot_to_shot_coherence": {
            "cn": "镜头间连贯性",
            "methods": [
                "前一镜头的结束动作=后一镜头的开始动作",
                "前一镜头建立的环境信息在后续镜头中保持",
                "角色位置关系(左右/远近)跨镜头一致",
                "情绪变化遵循曲线而非跳跃",
                "每个镜头携带前面故事的上下文摘要",
            ],
        },
    },

    # ========================================================
    # 扩充: 高级叙事钩子库
    # ========================================================
    "narrative_hooks_advanced": {
        "open_question": {
            "cn": "悬念提问",
            "technique": "开场抛出一个让观众迫切想知道答案的问题",
            "examples": ["为什么这个百万富翁每天穿破衣服?", "她为什么在大婚前夜逃跑?"],
        },
        "stake_frontload": {
            "cn": "前置赌注",
            "technique": "开场就告诉观众如果失败会失去什么,提高全程紧张度",
            "example": "'如果24小时内不还钱,我女儿就...'→全程倒计时",
        },
        "contradiction_setup": {
            "cn": "矛盾人设",
            "technique": "展示一个内在矛盾的角色,矛盾本身就是钩子",
            "example": "顶级外科医生却治不好自己的手抖;亿万富翁捡垃圾",
        },
        "mystery_object": {
            "cn": "神秘物件",
            "technique": "一个意义不明的物件反复出现,观众会自动脑补",
            "example": "主角随身带的一把旧钥匙——开什么门?为什么重要?",
        },
        "unreliable_opening": {
            "cn": "不可靠开场",
            "technique": "开场告诉观众一件事,但暗示这可能不是真相",
            "example": "旁白说'这是一个幸福家庭'——画面却是空荡的餐桌上一个人吃饭",
        },
    },

    # ========================================================
    # 扩充: 转场创意大全(短视频爆款向)
    # ========================================================
    "creative_transitions_full": {
        "match_action_transitions": [
            "A推门→B推开(同一动作跨场景)",
            "A转身→B已背对(转身匹配)",
            "A伸手抓→B已握住(动作传递)",
            "A跳跃落地→B从落地起跳(垂直匹配)",
            "A挥手→B挥手回应(跨时空呼应)",
        ],
        "object_transitions": [
            "杯子挡镜头→移开已是新场景",
            "衣服/披风掠过镜头→新场景",
            "伞撑开/合上→场景切换",
            "书本翻开/合上→进出故事",
        ],
        "light_transitions": [
            "走入阴影→走出已是新场景",
            "灯光闪烁/熄灭→场景切换",
            "阳光/月光方向变化暗示时间",
            "车灯扫过→新场景",
        ],
        "speed_transitions": [
            "常速→升格(时间变慢)→新场景常速",
            "快进蒙太奇→定格→新场景",
            "倒放→正放切换(超现实)",
        ],
        "impossible_transitions": [
            "分身:一个动作跨场景完成(如穿墙)",
            "缩放:镜头z推进画面→放大进入新场景",
            "镜面:镜中世界是另一时空",
            "画中画:屏幕中的画面成为新场景",
        ],
    },

    # ========================================================
    # 扩充: AI视频生成的提示词工程
    # ========================================================
    "ai_prompt_engineering": {
        "per_shot_checklist": [
            "主体:谁/什么(外貌关键词一致)",
            "动作:在做什么(动词精确)",
            "情绪:什么表情(微表情而非情绪词)",
            "环境:在哪(前景+中景+背景各一)",
            "光线:光源+方向+质感",
            "色调:主色+辅助色+点缀色",
            "运镜:方向+速度+起终点",
            "景别:取景范围",
        ],
        "consistency_keywords": {
            "character": "角色每次出现用相同的外貌关键词组合(发色/瞳色/服饰特征)",
            "scene": "同一场次的光线方向/色调修饰词保持一致",
            "prop": "道具描述每次用相同措辞",
            "style": "整体风格修饰词在所有镜头重复(如'电影感/暖调/浅景深')",
        },
        "movement_description": {
            "principle": "运动描述=方向+速度+起终点+主体",
            "good": "镜头从女主背影缓缓推向她的侧脸,最终停留在含泪的眼角",
            "bad": "镜头移动(太空泛)",
        },
        "emotion_description": {
            "principle": "用可见的面部动作替代抽象情绪词",
            "good": "她的嘴角不自觉上扬,眼角挤出细纹,瞳孔微微扩大",
            "bad": "她很开心(太抽象)",
        },
    },
}


# ============================================================
# 短视频决策覆盖层 — 为关键技法补7维决策字段
# (保留原techniques/visual_cues/structure, 叠加trigger/failure/measurement等)
# ============================================================
VIRAL_VIDEO_DECISION = {
    # ─── 注意力机制 ───
    "pattern_interrupt": {
        "trigger": "短视频0-0.5秒/打破浏览节奏/视觉听觉冲击/防止划走",
        "rationale": "0.5秒内必须发生冲击, 否则观众已划走。模式打断抓住本能反应。",
        "failure_modes": ["冲击0.5秒后=太晚, 已划走", "冲击与主题无关=欺诈", "冲击过强后续接不住=完播崩"],
        "measurement": "前0.5秒有冲击, 与主题相关, 抓住本能反应",
        "alternatives": ["curiosity_gap(更悬念)", "dopamine_loops(更持续)"],
        "cross_refs": {"pacing": "0.5秒生死线", "platform": "抖音/快手算法", "vertical": "竖屏冲击更直接"},
    },
    "curiosity_gap": {
        "trigger": "短视频0-5秒/给信息不给答案/悬念驱动留存",
        "rationale": "给足够信息引起好奇但不给答案=好奇心驱动。比冲击更可持续的留存。",
        "failure_modes": ["信息太多=失悬念", "信息太少=不懂", "缺口不回收=失信"],
        "measurement": "前5秒制造信息缺口, 观众想知答案, 后续回收",
        "alternatives": ["pattern_interrupt(更冲击)", "dopamine_loops(更循环)"],
        "cross_refs": {"pacing": "5秒悬念建立", "narrative": "悬念驱动", "mystery": "信息缺口核心"},
    },
    "dopamine_loops": {
        "trigger": "短视频持续留存/奖励-期待循环/多巴胺驱动不划走",
        "rationale": "每5-8秒小满足+新预期=多巴胺循环, 观众无法停止。是持续留存核心。",
        "failure_modes": ["满足间隔过长=流失", "无新预期=停止", "满足无升级=疲劳"],
        "measurement": "每5-8秒小满足+新预期, 持续循环不划走",
        "alternatives": ["curiosity_gap(更悬念)", "15s_format(更结构)"],
        "cross_refs": {"pacing": "5-8秒循环", "retention": "持续留存核心", "emotion": "多巴胺驱动"},
    },
    # ─── 节奏公式 ───
    "15s_format": {
        "trigger": "15秒极短视频/一个点一个情绪一个信息",
        "rationale": "15秒只够一个点, 必须无废帧。钩子2s+主体10s+反转3s。",
        "failure_modes": ["超过一个点=超载", "有废帧=流失", "无重复观看价值=不火"],
        "measurement": "一个点一个情绪, 无废帧, 有重复观看价值",
        "alternatives": ["60s_format(更丰富)", "3min_format(更故事)"],
        "cross_refs": {"pacing": "钩子2+主体10+反转3", "structure": "15s结构", "repeat": "重复观看价值"},
    },
    "60s_format": {
        "trigger": "60秒短视频/每15秒节奏点/中段不能平",
        "rationale": "60s=钩子3+建立12+发展20+高潮15+结尾10。每15秒一个节奏点, BGM同步。",
        "failure_modes": ["中段平=流失", "无mini转折=失节奏", "结尾不超越开头=不分享"],
        "measurement": "每15秒节奏点, 中段有mini转折, 结尾超越开头",
        "alternatives": ["15s_format(更极简)", "3min_format(更故事)"],
        "cross_refs": {"pacing": "每15秒节奏点", "music": "BGM节拍同步", "structure": "60s结构"},
    },
    "3min_format": {
        "trigger": "3分钟短剧/故事/每30秒检查留存",
        "rationale": "3min=钩子5+建立20+冲突40+升级40+高潮30+余韵15。每30秒须有留看理由。",
        "failure_modes": ["情绪重复=流失", "无记忆点=不留", "结尾无共鸣=不分享"],
        "measurement": "每30秒留看理由, 情绪不重复, 有记忆点, 结尾共鸣",
        "alternatives": ["60s_format(更短)", "15s_format(更极简)"],
        "cross_refs": {"pacing": "每30秒检查", "emotion": "情绪不重复", "share": "结尾决定分享"},
    },
    # ─── 叙事钩子进阶 ───
    "open_question": {
        "trigger": "开场抛问题/让观众迫切想知道答案",
        "rationale": "开场一个问题=好奇心驱动。问题须与主题相关且答案值得期待。",
        "failure_modes": ["问题无吸引力=失钩", "答案不值得=失信", "问题过隐=不懂"],
        "measurement": "开场问题有吸引力, 与主题相关, 答案值得",
        "alternatives": ["stake_frontload(更赌注)", "mystery_object(更物件)"],
        "cross_refs": {"hook": "开场钩子", "pacing": "问题驱动留存", "curiosity": "好奇心缺口"},
    },
    "stake_frontload": {
        "trigger": "开场前置赌注/告诉观众失败会失去什么",
        "rationale": "前置赌注=全程紧张。让观众知道'如果失败...'=提高全程赌注。",
        "failure_modes": ["赌注不够大=失紧张", "赌注无具体=失感", "赌注不兑现=失信"],
        "measurement": "开场赌注够大且具体, 全程紧张, 兑现",
        "alternatives": ["open_question(更问题)", "contradiction_setup(更矛盾)"],
        "cross_refs": {"hook": "开场钩子", "tension": "全程紧张", "pacing": "倒计时压迫"},
    },
    "contradiction_setup": {
        "trigger": "开场展示矛盾人设/矛盾本身就是钩子",
        "rationale": "内在矛盾的角色=本身就是钩子。观众想知'为什么矛盾'。",
        "failure_modes": ["矛盾无解释=失钩", "矛盾过牵强=失真", "矛盾无回收=悬置"],
        "measurement": "矛盾人设有吸引力, 后续有解释/回收",
        "alternatives": ["mystery_object(更物件)", "open_question(更问题)"],
        "cross_refs": {"hook": "开场钩子", "character": "矛盾人设", "performance": "反差萌基础"},
    },
    "mystery_object": {
        "trigger": "意义不明的物件反复出现/观众自动脑补",
        "rationale": "神秘物件=观众主动赋予意义。反复出现=悬念累积。",
        "failure_modes": ["物件无回收=悬置", "物件意义过明=失神秘", "物件无反复=失累积"],
        "measurement": "物件反复出现, 意义不明但回收, 观众脑补",
        "alternatives": ["open_question(更问题)", "unreliable_opening(更不可靠)"],
        "cross_refs": {"hook": "开场钩子", "foreshadow": "契诃夫之枪", "callback": "物件回调"},
    },
    "unreliable_opening": {
        "trigger": "开场告诉观众一件事但暗示非真相/不可靠叙述",
        "rationale": "不可靠开场=观众潜意识怀疑, 主动寻找真相。是高级悬念。",
        "failure_modes": ["暗示过明=失悬念", "暗示过隐=观众信了", "无后续反转=失意义"],
        "measurement": "开场有暗示非真相, 观众潜意识怀疑, 后续反转",
        "alternatives": ["open_question(更问题)", "contradiction_setup(更矛盾)"],
        "cross_refs": {"hook": "开场钩子", "narrative": "不可靠叙述", "reversal": "后续反转基础"},
    },
    # ─── visual_storytelling 3 ───
    "show_dont_tell": {
        "trigger": "任何视觉叙事/用动作代替解释/用环境代替描述/用表情代替独白",
        "rationale": "视觉>语言。一个动作(摘婚戒=离婚)比一段解释更有力, 是电影语言核心。",
        "failure_modes": ["动作过隐=观众不懂", "环境无信息=失叙事", "用旁白代替视觉=失电影感"],
        "measurement": "观众通过视觉读出信息, 不靠旁白解释",
        "alternatives": ["visual_metaphor(更隐喻)", "emotional_anchoring(更锚定)"],
        "cross_refs": {"screenwriting": "Show don't tell核心", "performance": "微表情>旁白", "pacing": "3秒微表情>30秒旁白"},
    },
    "visual_metaphor": {
        "trigger": "视觉隐喻/笼子=困/镜=双重/楼梯=升降/光暗=希望绝望",
        "rationale": "用视觉符号承载抽象概念=观众潜意识读取, 比台词更深。",
        "failure_modes": ["隐喻过隐=不懂", "隐喻过明=说教", "隐喻无回收=悬置"],
        "measurement": "观众读出隐喻含义, 符号有逻辑且回收",
        "alternatives": ["emotional_anchoring(更锚定)", "show_dont_tell(更直接)"],
        "cross_refs": {"symbolism": "视觉符号学", "foreshadow": "隐喻可埋伏笔", "intellectual_montage": "隐喻蒙太奇"},
    },
    "emotional_anchoring": {
        "trigger": "重复视觉元素锚定情感/颜色物品构图光线音效锚定",
        "rationale": "用重复元素锚定情感=每次出现自动唤起情绪, 是情感累积工具。",
        "failure_modes": ["锚定无重复=失累积", "锚定过频=疲劳", "锚定无回收=悬置"],
        "measurement": "重复元素锚定情感, 观众自动唤起情绪",
        "alternatives": ["visual_metaphor(更隐喻)", "show_dont_tell(更直接)"],
        "cross_refs": {"color": "色彩锚定(红=危险)", "foreshadow": "物品锚定可埋伏笔", "callback": "锚定是回调基础"},
    },
    # ─── engagement_triggers 3 ───
    "emotional_triggers": {
        "trigger": "触发情绪/代入/正义/优越/怀旧/敬畏/争议",
        "rationale": "情绪触发=观众情绪被唤起=留存+分享。6种触发器覆盖核心情绪。",
        "failure_modes": ["触发情绪与内容无关=硬煽情出戏", "触发过强(强行催泪)=观众逆反", "6种触发器堆砌=情绪过载"],
        "measurement": "观众在评论/弹幕表达与触发器匹配的情绪(如justice触发→骂反派), 非单纯点赞",
        "alternatives": ["interaction_hooks(更互动)", "shareability_factors(更分享)"],
        "cross_refs": {"engagement": "情绪触发核心", "shareability": "情绪触发驱动分享", "emotion": "6种触发器: empathy/justice/superiority/nostalgia/awe/controversy"},
    },
    "interaction_hooks": {
        "trigger": "互动钩子/选择题/预测/找彩蛋/未完待续/观点表态",
        "rationale": "互动钩子=让观众参与, 评论/关注/重复观看。是算法互动率核心。",
        "failure_modes": ["互动无吸引力=失参与", "选择题选项无两难=无讨论价值", "未完待续无回收=失信掉粉"],
        "measurement": "评论区出现与钩子匹配的行为(选择题→AB讨论/找彩蛋→重看截图), 非空评论",
        "alternatives": ["emotional_triggers(更情绪)", "shareability_factors(更分享)"],
        "cross_refs": {"algorithm": "互动率权重", "retention": "互动驱动留存", "engagement": "5种互动: 选择/预测/找彩蛋/未完待续/表态"},
    },
    "shareability_factors": {
        "trigger": "可分享因素/身份认同/实用价值/社交货币/情感共振/话题性",
        "rationale": "分享=传播核心。5种分享因素覆盖观众分享动机, 分享率=算法加权推送。",
        "failure_modes": ["分享因素与内容不匹配=硬蹭热点出戏", "社交货币过显=装逼感", "无身份认同=不转发"],
        "measurement": "分享时附带文案/转发理由与因素匹配(身份认同→'这就是我', 实用→收藏), 非裸转",
        "alternatives": ["emotional_triggers(更情绪)", "interaction_hooks(更互动)"],
        "cross_refs": {"algorithm": "分享率权重", "viral": "分享=传播核心", "engagement": "5因素: 身份/实用/社交货币/共振/话题"},
    },
    # ─── content_categories 5 ───
    "transformation": {
        "trigger": "变化/变装/对比类短视频/before→after视觉冲击",
        "rationale": "before→after反差=视觉冲击, 反差越大冲击越强, 是变装类爆款核心。",
        "failure_modes": ["反差不够=失冲击", "过程过慢=失快冲击", "无主题=炫技"],
        "measurement": "before→after反差冲击达成, 过程快",
        "alternatives": ["process_reveal(更过程)", "skill_flex(更技能)"],
        "cross_refs": {"viral": "变装类爆款", "camera": "固定机位+遮挡切换", "wardrobe_swap": "变装转场"},
    },
    "process_reveal": {
        "trigger": "过程揭秘类短视频/成品预览→如何做到",
        "rationale": "成品预览→揭秘过程=好奇心驱动, 关键步骤慢放+特写是核心。",
        "failure_modes": ["无成品预览=失好奇", "关键步骤无特写=失揭秘", "全慢放=失节奏"],
        "measurement": "成品预览→揭秘, 关键步骤慢放特写",
        "alternatives": ["transformation(更对比)", "skill_flex(更技能)"],
        "cross_refs": {"viral": "过程揭秘爆款", "camera": "俯拍/第一人称/延时", "pacing": "关键慢放其余快进"},
    },
    "story_time": {
        "trigger": "故事叙述类短视频/结果先行/真实感>制作",
        "rationale": "结果先行+面部情绪+画面叙述=真实感>制作精良, 情感>信息。",
        "failure_modes": ["无结果先行=失好奇", "面部无情绪=失真", "制作过精=失真实"],
        "measurement": "结果先行+面部情绪+真实感达成",
        "alternatives": ["emotional_micro_drama(更戏剧)", "process_reveal(更过程)"],
        "cross_refs": {"viral": "故事叙述爆款", "camera": "面部情绪特写", "performance": "真实>精良"},
    },
    "skill_flex": {
        "trigger": "技能展示类短视频/最惊人成果作开头",
        "rationale": "最惊人成果作开头=抓住技能粉, 多角度+慢放+技术细节是核心。",
        "failure_modes": ["无惊人开头=失抓", "无慢放细节=失技术", "无流畅自信=失魅"],
        "measurement": "惊人开头+慢放技术细节+流畅自信",
        "alternatives": ["process_reveal(更过程)", "transformation(更对比)"],
        "cross_refs": {"viral": "技能展示爆款", "camera": "多角度+慢放+特写", "pacing": "流畅自信>难度"},
    },
    "emotional_micro_drama": {
        "trigger": "情感微剧场类短视频/冲突最激烈画面作开头",
        "rationale": "冲突最激烈画面作开头+面部特写+微表情=真实表演>大幅度, 情绪递进不平。",
        "failure_modes": ["开头无冲突=失抓", "无微表情=失真", "情绪平=失递进"],
        "measurement": "冲突开头+微表情真实+情绪递进",
        "alternatives": ["story_time(更叙述)", "transformation(更对比)"],
        "cross_refs": {"viral": "情感微剧场爆款", "camera": "面部特写+环境极简", "performance": "微表情>大幅度"},
    },
    # ─── platform_optimization 3 ───
    "vertical_9_16": {
        "trigger": "竖屏9:16适配/中心构图/纵向运动/字幕浮层/安全区",
        "rationale": "竖屏=纵向运动+中心构图+字幕浮层+安全区。适配9:16是竖屏爆款基础。",
        "failure_modes": ["横摇=失竖屏", "主体偏中心=失焦", "无字幕安全区=被遮"],
        "measurement": "中心构图+纵向运动+字幕浮层+安全区达成",
        "alternatives": ["algorithm_signals(更算法)", "sound_design(更声音)"],
        "cross_refs": {"vertical": "竖屏铁律", "composition": "中心+上1/3眼线", "safe_zones": "顶部60px底部150px"},
    },
    "sound_design": {
        "trigger": "短视频声音设计/70%病毒视频依赖声音/BGM音效人声",
        "rationale": "70%病毒视频依赖声音。开头2秒有声音+BGM节拍匹配+音效强化+人声清晰。",
        "failure_modes": ["开头静音=划走", "BGM不卡节拍=失律动", "人声淹没BGM=失清晰", "无爆款BGM复用=失算法加权"],
        "measurement": "开头有声音+BGM卡节拍+音效强化+人声清晰+爆款BGM复用",
        "alternatives": ["vertical_9_16(更视觉)", "algorithm_signals(更算法)"],
        "cross_refs": {"viral": "声音是70%因素", "pacing": "BGM节拍匹配", "algorithm": "爆款BGM复用加权"},
    },
    "algorithm_signals": {
        "trigger": "算法友好信号/完播率/重复观看/互动率/分享率/关注转化",
        "rationale": "算法权重5信号: 完播+重看+互动+分享+关注。优化信号=算法加权推送。",
        "failure_modes": ["无完播率优化=失推", "无重复观看价值=失推", "无互动=失推", "无分享=失传播", "无系列化=失关注"],
        "measurement": "5信号优化: 完播+重看+互动+分享+关注",
        "alternatives": ["vertical_9_16(更视觉)", "sound_design(更声音)"],
        "cross_refs": {"algorithm": "5信号权重", "viral": "算法加权=爆款", "platform": "完播率权重最高"},
    },
    # ─── ai_video_specifics 3 ───
    "prompt_to_visual": {
        "trigger": "AI视频提示词到画面优化/每镜头描述含主体动作情绪环境光线色调",
        "rationale": "AI视频=提示词到画面。每镜头须含主体+动作+情绪+环境+光线+色调, 否则AI失焦。",
        "failure_modes": ["描述缺要素=AI失焦", "运动描述空泛=失精确", "表情描述抽象=失微表情"],
        "measurement": "每镜头含6要素+精确运动+分层表情",
        "alternatives": ["consistency_across_shots(更一致)", "shot_to_shot_coherence(更连贯)"],
        "cross_refs": {"ai_video": "提示词工程核心", "prompt": "6要素清单", "performance": "表情分层(整体+部位)"},
    },
    "consistency_across_shots": {
        "trigger": "AI视频跨镜头一致性/角色外貌/光线方向/色调/道具/情绪递进",
        "rationale": "AI视频跨镜头一致=角色关键词一致+光线方向不变+色调修饰词体系一致+道具措辞一致+情绪有逻辑。",
        "failure_modes": ["外貌关键词变=角色变", "光线方向变=失连戏", "色调修饰词不一致=失风格", "情绪跳跃=失逻辑"],
        "measurement": "跨镜头5一致: 外貌+光线+色调+道具+情绪",
        "alternatives": ["prompt_to_visual(更提示词)", "shot_to_shot_coherence(更连贯)"],
        "cross_refs": {"ai_video": "一致性是AI视频难点", "continuity": "跨镜头连戏", "prompt": "关键词一致体系"},
    },
    "shot_to_shot_coherence": {
        "trigger": "AI视频镜头间连贯性/结束动作=开始动作/环境保持/位置一致/情绪曲线/上下文摘要",
        "rationale": "镜头间连贯=前镜结束动作=后镜开始+环境保持+位置一致+情绪曲线+每镜携带上下文摘要。",
        "failure_modes": ["动作不衔接=失连贯", "环境变=失保持", "位置不一致=失轴", "情绪跳跃=失曲线", "无上下文=失连续"],
        "measurement": "5连贯: 动作衔接+环境保持+位置一致+情绪曲线+上下文摘要",
        "alternatives": ["consistency_across_shots(更一致)", "prompt_to_visual(更提示词)"],
        "cross_refs": {"ai_video": "连贯性是AI视频核心", "continuity": "镜头间连戏", "story_context": "上下文摘要=故事前文系统"},
    },
}


def get_viral_with_decision(pattern_key):
    """合并短视频技法基础信息 + 决策覆盖层"""
    base = {}
    for section in ("attention_mechanics", "visual_storytelling", "pacing_formulas",
                    "engagement_triggers", "content_categories", "platform_optimization",
                    "narrative_hooks_advanced", "creative_transitions_full", "ai_video_specifics"):
        if pattern_key in VIRAL_VIDEO_TECHNIQUES.get(section, {}):
            base = dict(VIRAL_VIDEO_TECHNIQUES[section][pattern_key])
            break
    decision = VIRAL_VIDEO_DECISION.get(pattern_key, {})
    base.update(decision)
    return base

