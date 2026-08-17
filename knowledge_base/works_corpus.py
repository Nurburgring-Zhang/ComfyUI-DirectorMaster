# ============================================================
# 影视/短剧/短视频 作品实证语料库 V1.0
# ============================================================
# 真实作品 + 真实拆解特征(情节推进/叙述/情感/节奏/钩子/技法/受众)
# 当前为种子语料库(电影+短剧+短视频), schema可扩展到10000+
# 诚实标注: 这些是真实作品的真实特征(基于公开影视知识), 非逐帧AI分析
# 但特征是作品可观测的真实属性, 足以做概率匹配的实证锚点
# ============================================================

WORKS_CORPUS = [
    # ========================================================
    # 一、电影 (IMDB Top + 大师代表作)
    # ========================================================
    {
        "id": "godfather", "cn": "教父", "type": "电影", "year": 1972, "director": "coppola",
        "genre": ["黑帮", "史诗", "家族"], "duration": "175min", "vertical": False,
        "plot_pattern": "家族权力更迭+Michael从旁观到沉沦的弧光",
        "narrative_structure": "classic_three_act",
        "emotion_curve": [0.6, 0.7, 0.8, 0.5, 0.85, 0.4, 0.3],
        "pacing": "歌剧式, 慢推权力核心+交叉剪辑神圣暴力",
        "opening_hook": "暗室倾听请求(权力建立, 黑暗中的权威)",
        "key_techniques": ["chiaroscuro", "cross_cut_parallel", "door_frame", "rembrandt", "slow_push_in"],
        "target_audience": "成人/艺术/男性",
        "features": {
            "plot_progression": "权力幽暗→家族更迭→Michael沉沦(旁观→参与→被腐蚀)",
            "narrative_style": "歌剧式宏大+保留私密人性瞬间",
            "emotion_signature": "权力腐蚀的冰冷+家族温度并存",
            "intensity_avg": 0.6, "emotion_dominant": "权力沉沦",
        },
        "matchable_tags": ["黑帮", "史诗", "权力", "家族", "chiaroscuro", "慢推", "cross_cut", "成人", "男性", "歌剧式", "低照度"],
    },
    {
        "id": "shawshank", "cn": "肖申克的救赎", "type": "电影", "year": 1994, "director": "frank_darabont",
        "genre": ["剧情", "监狱"], "duration": "142min", "vertical": False,
        "plot_pattern": "沉沦救赎弧光: 冤狱→隐忍→越狱重生",
        "narrative_structure": "descent_redemption",
        "emotion_curve": [0.4, 0.3, 0.5, 0.4, 0.3, 0.2, 0.9, 0.7],
        "pacing": "希望锚定, 缓推希望眼神+雨中仰拍解放",
        "opening_hook": "法庭判刑(冤屈建立)",
        "key_techniques": ["slow_push_in", "low_angle_rain", "warm_recall_cold_now", "voiceover_retrospective"],
        "target_audience": "大众/男性",
        "features": {
            "plot_progression": "冤屈沉沦→隐忍20年→越狱重生(希望不灭)",
            "narrative_style": "Red回顾式旁白+希望贯穿",
            "emotion_signature": "绝望中的希望微光, 雨中解放的释放",
            "intensity_avg": 0.5, "emotion_dominant": "希望/救赎",
        },
        "matchable_tags": ["剧情", "救赎", "希望", "监狱", "慢推", "雨中仰拍", "旁白", "大众", "暖回忆冷现实"],
    },
    {
        "id": "inception", "cn": "盗梦空间", "type": "电影", "year": 2010, "director": "nolan",
        "genre": ["科幻", "悬疑"], "duration": "148min", "vertical": False,
        "plot_pattern": "多层梦境嵌套+时间不同速+开放结局",
        "narrative_structure": "parallel_convergence",
        "emotion_curve": [0.5, 0.6, 0.7, 0.8, 0.85, 0.7],
        "pacing": "时间交叉加速, IMAX大画幅+留白结尾",
        "opening_hook": "海滩醒来(失忆悬念)",
        "key_techniques": ["cross_cut_parallel", "imax", "practical_effect", "nonlinear", "ambiguous_ending"],
        "target_audience": "成人/智性/男性",
        "features": {
            "plot_progression": "任务进入→多层嵌套→时间交叉→开放结局",
            "narrative_style": "非线性时间, 结构即主题",
            "emotion_signature": "主观时间感+留白叩问",
            "intensity_avg": 0.7, "emotion_dominant": "悬念/敬畏",
        },
        "matchable_tags": ["科幻", "悬疑", "时间结构", "cross_cut", "IMAX", "非线性", "开放结局", "智性"],
    },
    {
        "id": "pulp_fiction", "cn": "低俗小说", "type": "电影", "year": 1994, "director": "tarantino",
        "genre": ["犯罪", "黑色"], "duration": "154min", "vertical": False,
        "plot_pattern": "非线性章节拼贴+对话即动作",
        "narrative_structure": "nonlinear",
        "emotion_curve": [0.6, 0.7, 0.5, 0.7, 0.8, 0.6],
        "pacing": "长对话固定中景+突然zoom+章节卡",
        "opening_hook": "餐厅劫案(对话开场)",
        "key_techniques": ["nonlinear", "chapter_card", "trunk_shot", "sudden_zoom", "long_dialogue_medium"],
        "target_audience": "成人/影迷/男性",
        "features": {
            "plot_progression": "碎片拼贴→观众重组→圆环结构",
            "narrative_style": "对话即动作, 非线性时间",
            "emotion_signature": "暴力有美感+流行文化解构",
            "intensity_avg": 0.6, "emotion_dominant": "黑色幽默",
        },
        "matchable_tags": ["犯罪", "黑色", "非线性", "章节", "对话", "暴力美学", "影迷", "zoom"],
    },
    {
        "id": "blade_runner_2049", "cn": "银翼杀手2049", "type": "电影", "year": 2017, "director": "villeneuve",
        "genre": ["科幻", "悬疑"], "duration": "164min", "vertical": False,
        "plot_pattern": "身份追寻+人机边界+规模敬畏",
        "narrative_structure": "mystery_reveal",
        "emotion_curve": [0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.85],
        "pacing": "沉浸慢速, 寂静>音乐+粒子雾气+几何建筑",
        "opening_hook": "荒野审讯(氛围建立)",
        "key_techniques": ["slow_camera", "silence_over_music", "particles_fog", "geometric_arch", "motivated_light", "neon"],
        "target_audience": "成人/艺术/科幻迷",
        "features": {
            "plot_progression": "身份追寻→真相揭示→敬畏沉默",
            "narrative_style": "沉浸氛围, 不解释奇观",
            "emotion_signature": "规模敬畏+身份叩问",
            "intensity_avg": 0.55, "emotion_dominant": "敬畏/孤独",
        },
        "matchable_tags": ["科幻", "悬疑", "沉浸", "慢", "寂静", "粒子", "几何", "霓虹", "动机光", "艺术"],
    },
    {
        "id": "parasite", "cn": "寄生虫", "type": "电影", "year": 2019, "director": "bong_joon_ho",
        "genre": ["社会讽刺", "悬疑", "喜剧"], "duration": "132min", "vertical": False,
        "plot_pattern": "阶级寄生+垂直空间隐喻+类型转换",
        "narrative_structure": "classic_three_act",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.8, 0.3, 0.9],
        "pacing": "笑→冰瞬间+垂直空间叙事+框中框",
        "opening_hook": "半地下室晒虫(阶级建立)",
        "key_techniques": ["vertical_space_class", "frame_within_frame", "genre_pivot", "precise_mise_en_scene", "extreme_close_to_extreme_wide"],
        "target_audience": "成人/大众",
        "features": {
            "plot_progression": "寄生渗入→真相揭露→暴力爆发+阶级不可调和",
            "narrative_style": "类型杂糅, 笑着突然冰冷",
            "emotion_signature": "阶级看不见的暴力+突然冰冷瞬间",
            "intensity_avg": 0.7, "emotion_dominant": "讽刺/震惊",
        },
        "matchable_tags": ["社会讽刺", "悬疑", "喜剧", "垂直空间", "框中框", "类型杂糅", "阶级", "成人"],
    },
    {
        "id": "in_the_mood_for_love", "cn": "花样年华", "type": "电影", "year": 2000, "director": "wong_kar_wai",
        "genre": ["爱情", "文艺", "都市"], "duration": "98min", "vertical": False,
        "plot_pattern": "错过+无法言说的情感+空间重复",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.4, 0.45, 0.5, 0.4, 0.5, 0.3, 0.35],
        "pacing": "抽格升格+霓虹雨滴+极浅景深+画外独白",
        "opening_hook": "走廊擦肩(空间相遇)",
        "key_techniques": ["step_print", "neon_rain", "shallow_dof", "repeated_space", "offscreen_vo", "no_eyeball"],
        "target_audience": "成人/文艺/女性",
        "features": {
            "plot_progression": "相遇→克制→错过→回忆",
            "narrative_style": "情绪诗, 不说出口的更有力",
            "emotion_signature": "错过的痛+时间的流逝即情感",
            "intensity_avg": 0.45, "emotion_dominant": "惆怅/思念",
        },
        "matchable_tags": ["爱情", "文艺", "都市", "错过", "抽格", "霓虹", "浅景深", "独白", "女性", "文艺"],
    },
    {
        "id": "the_shining", "cn": "闪灵", "type": "电影", "year": 1980, "director": "kubrick",
        "genre": ["恐怖", "心理"], "duration": "146min", "vertical": False,
        "plot_pattern": "幽闭隔离+逐渐疯狂+对称压迫",
        "narrative_structure": "descent_redemption",
        "emotion_curve": [0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.95],
        "pacing": "对称固定凝视+steadicam幽灵跟随+冷调",
        "opening_hook": " aerial公路推镜(隔离建立)",
        "key_techniques": ["symmetry", "steadicam_corridor", "static_stare", "cold_palette", "one_point_perspective"],
        "target_audience": "成人/恐怖迷",
        "features": {
            "plot_progression": "隔离→疯狂→崩溃(环境比人强)",
            "narrative_style": "冷峻凝视, 不给答案",
            "emotion_signature": "环境压迫的渐进疯狂",
            "intensity_avg": 0.6, "emotion_dominant": "恐惧/不安",
        },
        "matchable_tags": ["恐怖", "心理", "对称", "steadicam", "固定", "冷调", "单点透视", "成人", "幽闭"],
    },
    {
        "id": "oldboy", "cn": "老男孩", "type": "电影", "year": 2003, "director": "park_chan_wook",
        "genre": ["悬疑", "惊悚", "复仇"], "duration": "120min", "vertical": False,
        "plot_pattern": "复仇循环+自我毁灭+长镜头暴力",
        "narrative_structure": "mystery_reveal",
        "emotion_curve": [0.5, 0.6, 0.7, 0.8, 0.9, 0.3],
        "pacing": "对称冷峻+精致色彩+长镜头暴力不切",
        "opening_hook": "牢笼释放(复仇启动)",
        "key_techniques": ["symmetry_center", "color_design", "long_take_violence", "frame_within_frame", "vertical_stairs"],
        "target_audience": "成人/男性",
        "features": {
            "plot_progression": "复仇→揭露→自我毁灭循环",
            "narrative_style": "复仇美学, 同情施暴者",
            "emotion_signature": "复仇的冰冷美+道德冲击",
            "intensity_avg": 0.8, "emotion_dominant": "复仇/愤怒",
        },
        "matchable_tags": ["悬疑", "惊悚", "复仇", "对称", "长镜头暴力", "精致色彩", "成人", "男性"],
    },
    {
        "id": "chungking_express", "cn": "重庆森林", "type": "电影", "year": 1994, "director": "wong_kar_wai",
        "genre": ["爱情", "都市", "文艺"], "duration": "102min", "vertical": False,
        "plot_pattern": "都市漂泊+平行爱情+时间标记",
        "narrative_structure": "parallel_convergence",
        "emotion_curve": [0.5, 0.4, 0.45, 0.5, 0.4, 0.45],
        "pacing": "手持人群穿梭+抽格+凤梨罐头时间",
        "opening_hook": "街市奔跑抽格(漂泊建立)",
        "key_techniques": ["handheld_crowd", "step_print", "time_object", "neon", "shallow_dof"],
        "target_audience": "文艺/女性",
        "features": {
            "plot_progression": "两段平行爱情→都市漂泊的连接",
            "narrative_style": "情绪碎片, 时间即情感",
            "emotion_signature": "都市孤独+错过的温柔",
            "intensity_avg": 0.45, "emotion_dominant": "孤独/思念",
        },
        "matchable_tags": ["爱情", "都市", "文艺", "抽格", "手持", "霓虹", "孤独", "女性"],
    },
    {
        "id": "crouching_tiger", "cn": "卧虎藏龙", "type": "电影", "year": 2000, "director": "ang_lee",
        "genre": ["武侠", "冒险", "爱情"], "duration": "120min", "vertical": False,
        "plot_pattern": "克制情感+竹林飘逸+江湖道义",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.8, 0.4],
        "pacing": "静谧固定+竹林飘逸+绿调压抑+长焦眼神",
        "opening_hook": "屋顶夜行(江湖建立)",
        "key_techniques": ["wire_fu_bamboo", "static_quiet", "green_repress", "long_focus_eye", "tableau_group"],
        "target_audience": "大众/成人/国际",
        "features": {
            "plot_progression": "道义→情感压抑→竹林对决→牺牲",
            "narrative_style": "东方克制, 压抑下汹涌",
            "emotion_signature": "克制的爱与江湖的悲",
            "intensity_avg": 0.6, "emotion_dominant": "克制/悲",
        },
        "matchable_tags": ["武侠", "冒险", "爱情", "竹林飘逸", "克制", "绿调", "长焦眼神", "国际", "东方"],
    },
    {
        "id": "hero", "cn": "英雄", "type": "电影", "year": 2002, "director": "zhang_yimou",
        "genre": ["武侠", "史诗"], "duration": "99min", "vertical": False,
        "plot_pattern": "色彩段落叙事+天下+刺客放弃",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.5, 0.6, 0.5, 0.7, 0.8, 0.5],
        "pacing": "单色段落+群体图案+对称纵深+极远渺小",
        "opening_hook": "书法殿前(色彩+秩序建立)",
        "key_techniques": ["color_chapter", "mass_formation", "symmetry_depth", "extreme_wide_small", "natural_element_surreal"],
        "target_audience": "大众/国际",
        "features": {
            "plot_progression": "三色叙事(红蓝白)→真相→放弃刺杀(天下)",
            "narrative_style": "色彩即叙事, 意境>情节",
            "emotion_signature": "集体中的个体命运+色彩情绪",
            "intensity_avg": 0.65, "emotion_dominant": "史诗/牺牲",
        },
        "matchable_tags": ["武侠", "史诗", "色彩段落", "群体", "对称", "极远渺小", "国际", "意境"],
    },
    {
        "id": "spirited_away", "cn": "千与千寻", "type": "电影", "year": 2001, "director": "hayao_miyazaki",
        "genre": ["奇幻", "冒险", "成长"], "duration": "125min", "vertical": False,
        "plot_pattern": "成长冒险+万物有灵+没有绝对恶",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.4, 0.5, 0.4, 0.6, 0.5, 0.7, 0.8],
        "pacing": "云层天空+食物细节+风可视化+自然机械共生",
        "opening_hook": "隧道入口(神秘世界建立)",
        "key_techniques": ["sky_clouds", "food_detail", "wind_visual", "nature_machine", "no_absolute_evil"],
        "target_audience": "全年龄/家庭",
        "features": {
            "plot_progression": "误入→成长→救父母→回归(勇气)",
            "narrative_style": "万物有灵, 日常诗意",
            "emotion_signature": "孩子的勇气+自然敬畏",
            "intensity_avg": 0.55, "emotion_dominant": "勇气/温暖",
        },
        "matchable_tags": ["奇幻", "冒险", "成长", "自然", "食物", "风", "家庭", "全年龄", "万物有灵"],
    },
    {
        "id": "your_name", "cn": "你的名字", "type": "电影", "year": 2016, "director": "makoto_shinkai",
        "genre": ["爱情", "青春", "灾难"], "duration": "106min", "vertical": False,
        "plot_pattern": "时空交错爱情+错过与重逢",
        "narrative_structure": "parallel_convergence",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.4, 0.9, 0.8],
        "pacing": "超写实背景+逆光光晕+黄昏色彩段落",
        "opening_hook": "彗星划过(命运建立)",
        "key_techniques": ["hyper_real_bg", "lens_flare", "dusk_chapter", "sky_extreme", "miss_reunion"],
        "target_audience": "青春/女性/大众",
        "features": {
            "plot_progression": "身体交换→时空错→错过→黄昏重逢",
            "narrative_style": "光影即情绪, 距离与错过",
            "emotion_signature": "青春的遗憾+重逢的释放",
            "intensity_avg": 0.65, "emotion_dominant": "心动/遗憾",
        },
        "matchable_tags": ["爱情", "青春", "灾难", "超写实", "光晕", "黄昏", "错过", "女性", "动画"],
    },
    {
        "id": "interstellar", "cn": "星际穿越", "type": "电影", "year": 2014, "director": "nolan",
        "genre": ["科幻", "冒险"], "duration": "169min", "vertical": False,
        "plot_pattern": "时间相对论+父女跨时空+爱穿越维度",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.5, 0.6, 0.7, 0.4, 0.8, 0.9, 0.7],
        "pacing": "IMAX+时间交叉+实拍+留白",
        "opening_hook": "沙尘暴末日(危机建立)",
        "key_techniques": ["imax", "time_cross", "practical", "silence", "bookshelf_motif"],
        "target_audience": "大众/科幻/家庭",
        "features": {
            "plot_progression": "末日→星际→时间错位→爱穿越",
            "narrative_style": "时间即情感, 科学+人文",
            "emotion_signature": "父女跨时空的爱+时间代价",
            "intensity_avg": 0.65, "emotion_dominant": "敬畏/爱",
        },
        "matchable_tags": ["科幻", "冒险", "时间", "IMAX", "cross_cut", "父女", "家庭", "敬畏"],
    },
    {
        "id": "dunkirk", "cn": "敦刻尔克", "type": "电影", "year": 2017, "director": "nolan",
        "genre": ["战争", "史诗"], "duration": "106min", "vertical": False,
        "plot_pattern": "三线平行(海陆空)+不同时间速+交汇",
        "narrative_structure": "parallel_convergence",
        "emotion_curve": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
        "pacing": "三线加速交汇+悬念音效+IMAX",
        "opening_hook": "街头传单(撤退建立)",
        "key_techniques": ["three_line_parallel", "accelerate_converge", "ticking_sound", "imax", "cross_cut"],
        "target_audience": "成人/历史",
        "features": {
            "plot_progression": "海陆空三线→加速→撤退交汇",
            "narrative_style": "时间不同速, 结构即紧张",
            "emotion_signature": "战争的沉默+个体的求生",
            "intensity_avg": 0.75, "emotion_dominant": "紧张/敬畏",
        },
        "matchable_tags": ["战争", "史诗", "三线平行", "加速交汇", "悬念音效", "成人", "历史"],
    },
    {
        "id": "1917", "cn": "1917", "type": "电影", "year": 2019, "director": "sam_mendes",
        "genre": ["战争", "史诗"], "duration": "119min", "vertical": False,
        "plot_pattern": "一镜到底送信+个体穿越战场",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.8, 0.9, 0.6],
        "pacing": "伪一镜到底+手持+战场鸟瞰",
        "opening_hook": "草地休息(任务下达)",
        "key_techniques": ["fake_one_shot", "invisible_cut", "handheld", "war_birds_eye", "long_take"],
        "target_audience": "成人/历史",
        "features": {
            "plot_progression": "任务→穿越战场→送达(个体锚定)",
            "narrative_style": "沉浸一镜, 真实时间",
            "emotion_signature": "个体的渺小+任务的执着",
            "intensity_avg": 0.7, "emotion_dominant": "紧张/悲悯",
        },
        "matchable_tags": ["战争", "一镜到底", "伪一镜", "手持", "鸟瞰", "成人", "历史", "沉浸"],
    },
    {
        "id": "saving_private_ryan", "cn": "拯救大兵瑞恩", "type": "电影", "year": 1998, "director": "spielberg",
        "genre": ["战争", "史诗"], "duration": "169min", "vertical": False,
        "plot_pattern": "小队送一个人+个体视角锚定宏大战争",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.9, 0.5, 0.6, 0.7, 0.5, 0.8, 0.6],
        "pacing": "手持D-Day+去饱和+前景遮挡+Face-light",
        "opening_hook": "老墓园回忆(框架叙事)",
        "key_techniques": ["handheld_war", "desaturated", "foreground_occlusion", "face_light", "child_perspective", "voiceover"],
        "target_audience": "成人/男性/家庭",
        "features": {
            "plot_progression": "D-Day→小队任务→牺牲→'earn this'",
            "narrative_style": "普通人+非凡处境, 个体锚定",
            "emotion_signature": "战争的残酷+人文希望",
            "intensity_avg": 0.7, "emotion_dominant": "悲壮/希望",
        },
        "matchable_tags": ["战争", "史诗", "手持", "去饱和", "前景遮挡", "个体锚定", "成人", "家庭"],
    },
    {
        "id": "mad_max_fury_road", "cn": "疯狂的麦克斯4", "type": "电影", "year": 2015, "director": "george_miller",
        "genre": ["动作", "末世", "冒险"], "duration": "120min", "vertical": False,
        "plot_pattern": "末世逃亡+女性救赎+极简叙事极致视觉",
        "narrative_structure": "classic_three_act",
        "emotion_curve": [0.7, 0.8, 0.75, 0.85, 0.9, 0.7],
        "pacing": "居中对称高速+橙黄蓝天+帧精确+女性英雄",
        "opening_hook": "逃出囚笼(末世建立)",
        "key_techniques": ["center_symmetry", "orange_blue_contrast", "frame_precise", "female_hero", "practical_effect"],
        "target_audience": "成人/动作迷",
        "features": {
            "plot_progression": "逃→追→返→救赎(极简)",
            "narrative_style": "极简叙事+极致视觉, 神话结构",
            "emotion_signature": "末世中女性互助的救赎",
            "intensity_avg": 0.85, "emotion_dominant": "爆发/救赎",
        },
        "matchable_tags": ["动作", "末世", "居中对称", "橙黄", "帧精确", "女性英雄", "成人", "极简"],
    },
    {
        "id": "black_swan", "cn": "黑天鹅", "type": "电影", "year": 2010, "director": "darren_aronofsky",
        "genre": ["心理", "惊悚", "剧情"], "duration": "108min", "vertical": False,
        "plot_pattern": "完美追求→崩溃→沉沦螺旋",
        "narrative_structure": "descent_redemption",
        "emotion_curve": [0.5, 0.6, 0.7, 0.4, 0.3, 0.2, 0.95],
        "pacing": "snorricam+跳切瞳孔+螺旋下沉+镜子分裂",
        "opening_hook": "梦境芭蕾(心理建立)",
        "key_techniques": ["snorricam", "jump_cut_pupil", "spiral_descent", "mirror_split", "bw_color_chapter"],
        "target_audience": "成人/女性/艺术",
        "features": {
            "plot_progression": "追求完美→幻觉→崩溃(身体是战场)",
            "narrative_style": "沉沦螺旋, 身体性叙事",
            "emotion_signature": "完美的代价+自我毁灭",
            "intensity_avg": 0.75, "emotion_dominant": "崩溃/绝望",
        },
        "matchable_tags": ["心理", "惊悚", "snorricam", "跳切", "螺旋", "镜子", "成人", "女性", "艺术"],
    },
    {
        "id": "roma_2018", "cn": "罗马", "type": "电影", "year": 2018, "director": "alfonso_cuaron",
        "genre": ["剧情", "时代剧"], "duration": "135min", "vertical": False,
        "plot_pattern": "家庭女工记忆+时代裂变+黑白长镜头",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.4, 0.45, 0.5, 0.4, 0.6, 0.5, 0.7],
        "pacing": "数字长镜头复杂调度+黑白灰阶+环境音+低机位孩子视角",
        "opening_hook": "洗院子地面(日常建立)",
        "key_techniques": ["digital_long_take", "bw_gray", "ambient_sound_emotion", "low_child_pov", "wide_angle_long_focus"],
        "target_audience": "成人/艺术/国际",
        "features": {
            "plot_progression": "日常→裂变→失去→和解(私人的即政治)",
            "narrative_style": "私人的即政治, 宏大中锚定个体",
            "emotion_signature": "阶级+记忆+失去的温柔",
            "intensity_avg": 0.5, "emotion_dominant": "悲悯/温柔",
        },
        "matchable_tags": ["剧情", "时代剧", "长镜头", "黑白", "环境音", "孩子视角", "艺术", "国际", "日常"],
    },
    {
        "id": "shape_of_water", "cn": "水形物语", "type": "电影", "year": 2017, "director": "guillermo_del_toro",
        "genre": ["奇幻", "爱情", "童话"], "duration": "123min", "vertical": False,
        "plot_pattern": "怪物同情+跨物种爱+冷战寓言",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.4, 0.5, 0.6, 0.5, 0.7, 0.8],
        "pacing": "蓝绿冷调+暖红点缀+怪物实体特效+对称迷宫垂直",
        "opening_hook": "水下梦境(童话建立)",
        "key_techniques": ["blue_green_cold", "warm_red_accent", "monster_practical", "symmetry_vertical", "child_low_angle"],
        "target_audience": "成人/奇幻/艺术",
        "features": {
            "plot_progression": "发现怪物→爱→救→逃(同情异类)",
            "narrative_style": "童话黑暗, 怪物比人有人性",
            "emotion_signature": "同情弱者+异类的爱",
            "intensity_avg": 0.55, "emotion_dominant": "怜爱/敬畏",
        },
        "matchable_tags": ["奇幻", "爱情", "童话", "蓝绿", "怪物", "实体特效", "对称", "成人", "艺术"],
    },
    {
        "id": "grand_budapest", "cn": "布达佩斯大饭店", "type": "电影", "year": 2014, "director": "wes_anderson",
        "genre": ["喜剧", "冒险", "艺术"], "duration": "99min", "vertical": False,
        "plot_pattern": "嵌套叙事+章节式+糖衣创伤",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.6, 0.55, 0.5, 0.6, 0.45, 0.5],
        "pacing": "中心对称+马卡龙色+90度俯拍+快速摇移+字幕卡",
        "opening_hook": "少女致敬纪念碑(嵌套建立)",
        "key_techniques": ["center_symmetry", "pastel_color", "90_overhead", "whip_pan", "chapter_card", "miniature"],
        "target_audience": "文艺/艺术",
        "features": {
            "plot_progression": "嵌套回忆→章节冒险→糖衣下的创伤",
            "narrative_style": "玩偶匣美学, 忧伤藏糖衣",
            "emotion_signature": "秩序是对混乱的抵抗+糖衣下的忧伤",
            "intensity_avg": 0.55, "emotion_dominant": "忧伤/幽默",
        },
        "matchable_tags": ["喜剧", "冒险", "对称", "马卡龙", "俯拍", "章节", "文艺", "艺术", "糖衣"],
    },
    {
        "id": "no_country_for_old_men", "cn": "老无所依", "type": "电影", "year": 2007, "director": "coen_brothers",
        "genre": ["犯罪", "西部", "黑色"], "duration": "122min", "vertical": False,
        "plot_pattern": "宿命随机+硬币两面+荒诞命运",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.4, 0.3, 0.4],
        "pacing": "居中对称冷峻+荒原孤立+固定凝视荒诞+灰色去饱和",
        "opening_hook": "杀手寂静(宿命建立)",
        "key_techniques": ["center_cold", "wasteland_isolation", "static_stare_absurd", "gray_desaturate", "no_score"],
        "target_audience": "成人/艺术/男性",
        "features": {
            "plot_progression": "随机暴力→追杀→无解(命运随机)",
            "narrative_style": "宿命论, 荒诞平静发生",
            "emotion_signature": "命运的随机残酷+无解",
            "intensity_avg": 0.55, "emotion_dominant": "宿命/荒诞",
        },
        "matchable_tags": ["犯罪", "西部", "黑色", "宿命", "荒原", "固定", "去饱和", "无配乐", "成人"],
    },
    {
        "id": "se7en", "cn": "七宗罪", "type": "电影", "year": 1995, "director": "fincher",
        "genre": ["悬疑", "犯罪", "惊悚"], "duration": "127min", "vertical": False,
        "plot_pattern": "七罪谋杀+箱中真相+黑暗最低点",
        "narrative_structure": "mystery_reveal",
        "emotion_curve": [0.5, 0.55, 0.6, 0.65, 0.7, 0.3, 0.9],
        "pacing": "极暗调+精确构图+去饱和冷绿+缓推真相+鸟瞰审视",
        "opening_hook": "雨夜凶案(黑暗建立)",
        "key_techniques": ["low_key_dark", "precise_composition", "desaturate_cold_green", "slow_push_truth", "bird_eye"],
        "target_audience": "成人/男性",
        "features": {
            "plot_progression": "七罪→追凶→箱中真相→黑暗最低点",
            "narrative_style": "黑暗精确, 最可怕是人自己",
            "emotion_signature": "完美的计划+一个疏忽=崩塌",
            "intensity_avg": 0.7, "emotion_dominant": "黑暗/震惊",
        },
        "matchable_tags": ["悬疑", "犯罪", "黑暗", "精确", "去饱和", "冷绿", "缓推", "鸟瞰", "成人"],
    },
    {
        "id": "gone_girl", "cn": "消失的爱人", "type": "电影", "year": 2014, "director": "fincher",
        "genre": ["悬疑", "犯罪"], "duration": "149min", "vertical": False,
        "plot_pattern": "不可靠叙述+妻子失踪+真相反转",
        "narrative_structure": "mystery_reveal",
        "emotion_curve": [0.5, 0.6, 0.7, 0.8, 0.85, 0.9],
        "pacing": "极暗调+精确+去饱和+不可靠VO+缓推真相",
        "opening_hook": "刀刃寻妻(悬念建立)",
        "key_techniques": ["low_key", "precise", "desaturate", "unreliable_vo", "slow_push_truth", "cross_cut_past_now"],
        "target_audience": "成人/女性",
        "features": {
            "plot_progression": "失踪→调查→日记反转→真相",
            "narrative_style": "不可靠叙述, 黑暗精确",
            "emotion_signature": "婚姻的冰冷+操控",
            "intensity_avg": 0.7, "emotion_dominant": "悬疑/冰冷",
        },
        "matchable_tags": ["悬疑", "犯罪", "不可靠叙述", "黑暗", "精确", "去饱和", "成人", "女性"],
    },
    {
        "id": "farewell_my_concubine", "cn": "霸王别姬", "type": "电影", "year": 1993, "director": "chen_kaige",
        "genre": ["史诗", "戏曲", "文艺"], "duration": "171min", "vertical": False,
        "plot_pattern": "戏曲人生+时代碾压+痴人纯粹",
        "narrative_structure": "descent_redemption",
        "emotion_curve": [0.6, 0.7, 0.8, 0.5, 0.4, 0.3, 0.85],
        "pacing": "大色块仪式+长焦压缩+戏曲脸谱+对称权力+低机位仰拍",
        "opening_hook": "戏班练功(命运建立)",
        "key_techniques": ["color_block_ritual", "long_focus_compress", "opera_face", "symmetry_power", "low_angle_loom"],
        "target_audience": "成人/艺术/国际",
        "features": {
            "plot_progression": "学戏→成角→时代碾压→自刎(痴人)",
            "narrative_style": "历史碾压个体, 文化即身份即枷锁",
            "emotion_signature": "痴人的纯粹+时代的残忍",
            "intensity_avg": 0.7, "emotion_dominant": "悲怆/痴",
        },
        "matchable_tags": ["史诗", "戏曲", "文艺", "色彩", "长焦", "脸谱", "对称", "成人", "艺术", "国际"],
    },
    {
        "id": "wandering_earth_2", "cn": "流浪地球2", "type": "电影", "year": 2023, "director": "guo_fan",
        "genre": ["科幻", "末世", "灾难", "史诗"], "duration": "173min", "vertical": False,
        "plot_pattern": "集体主义末世+带着家园流浪+多线汇合",
        "narrative_structure": "parallel_convergence",
        "emotion_curve": [0.6, 0.7, 0.5, 0.8, 0.7, 0.9, 0.6],
        "pacing": "重工业金属+冰封冷暖对比+群像宏大工程+低机位仰拍巨型",
        "opening_hook": "太空电梯危机(末世建立)",
        "key_techniques": ["heavy_industry_metal", "ice_cold_warm", "ensemble_epic", "low_angle_loom", "red_hope_motif"],
        "target_audience": "大众/科幻/家庭",
        "features": {
            "plot_progression": "危机→多线救援→集体牺牲→家园流浪",
            "narrative_style": "集体主义史诗, 带着家园逃",
            "emotion_signature": "集体的希望信念+牺牲",
            "intensity_avg": 0.75, "emotion_dominant": "史诗/希望",
        },
        "matchable_tags": ["科幻", "末世", "灾难", "重工业", "冷暖", "集体", "仰拍", "家庭", "中国"],
    },
    {
        "id": "matrix", "cn": "黑客帝国", "type": "电影", "year": 1999, "director": "wachowski",
        "genre": ["科幻", "动作"], "duration": "136min", "vertical": False,
        "plot_pattern": "现实是虚构+觉醒+子弹时间对决",
        "narrative_structure": "hero_journey",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.8, 0.9, 0.7],
        "pacing": "绿色代码雨+子弹时间环绕+黑色皮衣+慢动作顶点",
        "opening_hook": "trinity逃亡(超现实建立)",
        "key_techniques": ["green_code_rain", "bullet_time_orbit", "black_leather", "slowmo_peak", "wire_fu"],
        "target_audience": "成人/科幻/动作",
        "features": {
            "plot_progression": "觉醒→训练→对决(现实虚构)",
            "narrative_style": "赛博哲学, 视觉即概念",
            "emotion_signature": "觉醒的震颤+自由的代价",
            "intensity_avg": 0.75, "emotion_dominant": "觉醒/震撼",
        },
        "matchable_tags": ["科幻", "动作", "绿色代码", "子弹时间", "环绕", "慢动作", "赛博", "成人"],
    },
    {
        "id": "the_grandmaster", "cn": "一代宗师", "type": "电影", "year": 2013, "director": "wong_kar_wai",
        "genre": ["武侠", "文艺"], "duration": "130min", "vertical": False,
        "plot_pattern": "宗师之路+门派传承+雨夜对决",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.5, 0.6, 0.7, 0.5, 0.4, 0.6, 0.5],
        "pacing": "雨夜慢动作+竹林水+香烟+长焦眼神+水墨淡雅",
        "opening_hook": "雨夜群斗(宗师建立)",
        "key_techniques": ["rain_slowmo", "bamboo_water", "cigarette_motif", "long_focus_eye", "ink_wash_palette"],
        "target_audience": "文艺/武侠/国际",
        "features": {
            "plot_progression": "学艺→对决→传承→念念不忘(宗师)",
            "narrative_style": "情绪武侠, 意境>情节",
            "emotion_signature": "宗师的隐忍+传承的悲",
            "intensity_avg": 0.6, "emotion_dominant": "隐忍/悲",
        },
        "matchable_tags": ["武侠", "文艺", "雨夜慢动作", "竹林", "长焦眼神", "水墨", "意境", "国际"],
    },

    # ========================================================
    # 二、短剧 (真实爆款)
    # ========================================================
    {
        "id": "sd_family_outside", "cn": "家里家外", "type": "短剧", "year": 2025, "director": "unknown_short",
        "genre": ["家庭", "温情", "年代"], "duration": "80集×3min", "vertical": True,
        "plot_pattern": "80年代重组家庭+日常温情+时代变迁",
        "narrative_structure": "kishōtenkitsu",
        "emotion_curve": [0.5, 0.55, 0.6, 0.5, 0.65, 0.7, 0.6],
        "pacing": "竖屏日常+暖色实景+食物特写+低机位孩子视角, 节奏中速温润",
        "opening_hook": "家庭重组日常(温情建立)",
        "key_techniques": ["vertical_daily", "warm_practical", "food_detail", "low_child_pov", "season_time"],
        "target_audience": "银发/家庭/女性",
        "features": {
            "plot_progression": "重组→磨合→温情→时代变迁(家庭和解)",
            "narrative_style": "日常温润, 不狗血",
            "emotion_signature": "家庭的第二春+被需要的温暖",
            "intensity_avg": 0.55, "emotion_dominant": "温情/怀旧",
        },
        "matchable_tags": ["短剧", "家庭", "温情", "年代", "银发", "竖屏", "暖色", "日常", "食物", "女性"],
    },
    {
        "id": "sd_mr_fu", "cn": "闪婚后傅先生马甲藏不住了", "type": "短剧", "year": 2024, "director": "yan_xiaodi",
        "genre": ["甜宠", "隐藏身份", "都市"], "duration": "100集×2min", "vertical": True,
        "plot_pattern": "契约婚姻+隐藏身份+甜宠升级+马甲掉落",
        "narrative_structure": "short_drama_hook",
        "emotion_curve": [0.7, 0.5, 0.6, 0.7, 0.85, 0.6],
        "pacing": "竖屏3秒钩子+15秒反转+面部70%+急推特写爽点, 节奏密集",
        "opening_hook": "闪婚身份反转(3秒钩子)",
        "key_techniques": ["vertical_face_70", "3s_hook", "15s_reversal", "push_closeup", "sweet_escalation"],
        "target_audience": "女频/甜宠/女性",
        "features": {
            "plot_progression": "闪婚→隐藏身份→甜宠升级→马甲掉落全场震惊",
            "narrative_style": "爽文节奏, 甜度递增不重复",
            "emotion_signature": "被珍视的幻想+身份反差爽",
            "intensity_avg": 0.7, "emotion_dominant": "甜/爽",
        },
        "matchable_tags": ["短剧", "甜宠", "隐藏身份", "女频", "竖屏", "3秒钩子", "15秒反转", "甜度递增", "女性"],
    },
    {
        "id": "sd_black_lotus", "cn": "黑莲花上位手册", "type": "短剧", "year": 2023, "director": "duanmu_rong",
        "genre": ["宫斗", "重生", "复仇"], "duration": "80集×3min", "vertical": True,
        "plot_pattern": "重生复仇+宫斗布局+打脸逆袭",
        "narrative_structure": "short_drama_hook",
        "emotion_curve": [0.5, 0.6, 0.7, 0.4, 0.85, 0.3, 0.9],
        "pacing": "竖屏打脸急推+30秒爆点+身份反转视觉差, 节奏密集爽",
        "opening_hook": "重生开局(复仇建立)",
        "key_techniques": ["vertical_slap_closeup", "30s_peak", "identity_reversal", "ensemble_shock", "revenge_delay"],
        "target_audience": "女频/复仇/女性",
        "features": {
            "plot_progression": "重生→布局→打脸→逆袭(复仇循环)",
            "narrative_style": "复仇爽文, 延迟满足+密集释放",
            "emotion_signature": "复仇的爽+施害者崩溃",
            "intensity_avg": 0.75, "emotion_dominant": "爽/复仇",
        },
        "matchable_tags": ["短剧", "宫斗", "重生", "复仇", "女频", "竖屏", "打脸", "30秒爆点", "身份反转", "女性"],
    },
    {
        "id": "sd_80s_stepmom", "cn": "我在八零年代当后妈", "type": "短剧", "year": 2024, "director": "unknown_short",
        "genre": ["穿越", "年代", "家庭"], "duration": "90集×2min", "vertical": True,
        "plot_pattern": "穿越80年代+后妈日常+时代红利",
        "narrative_structure": "short_drama_hook",
        "emotion_curve": [0.5, 0.6, 0.55, 0.7, 0.6, 0.65],
        "pacing": "竖屏穿越色温差+日常甜+时代红利爽, 节奏中速爽甜",
        "opening_hook": "穿越80年代(色温差钩子)",
        "key_techniques": ["vertical_time_color", "daily_sweet", "era_dividend", "low_machine_age"],
        "target_audience": "女频/穿越/银发",
        "features": {
            "plot_progression": "穿越→后妈日常→时代红利→家庭温情",
            "narrative_style": "穿越+日常, 时代差异即爽点",
            "emotion_signature": "穿越者的上帝视角+家庭温情",
            "intensity_avg": 0.6, "emotion_dominant": "爽/温情",
        },
        "matchable_tags": ["短剧", "穿越", "年代", "家庭", "女频", "银发", "竖屏", "色温差", "日常", "时代红利"],
    },
    {
        "id": "sd_warlord", "cn": "战神归来赘婿流(代表)", "type": "短剧", "year": 2024, "director": "duanmu_rong",
        "genre": ["男频", "战神", "隐藏身份", "爽文"], "duration": "100集×2min", "vertical": True,
        "plot_pattern": "战神隐姓→被欺压→小露一手→身份暴露全场跪",
        "narrative_structure": "short_drama_hook",
        "emotion_curve": [0.4, 0.5, 0.3, 0.6, 0.85, 0.9],
        "pacing": "竖屏打脸急推+全场震惊群像+身份反转视觉差, 节奏密集爽",
        "opening_hook": "被羞辱一幕(男频钩子)",
        "key_techniques": ["vertical_slap", "ensemble_kneel", "identity_reveal", "visual_contrast", "30s_peak"],
        "target_audience": "男频/战神/男性",
        "features": {
            "plot_progression": "隐姓→被欺→暴露→碾压(打脸循环)",
            "narrative_style": "男频爽文, 压得越深弹得越高",
            "emotion_signature": "力量幻想+地位跃升+被尊重",
            "intensity_avg": 0.8, "emotion_dominant": "爽/碾压",
        },
        "matchable_tags": ["短剧", "男频", "战神", "隐藏身份", "打脸", "全场跪", "竖屏", "身份反转", "男性"],
    },

    # ========================================================
    # 三、短视频 (真实爆款格式)
    # ========================================================
    {
        "id": "vv_zach_king", "cn": "Zach King魔术短片(代表)", "type": "短视频", "year": 2020, "director": "zach_king",
        "genre": ["创意", "魔术", "喜剧"], "duration": "15-30s", "vertical": True,
        "plot_pattern": "无缝剪辑魔法错觉+日常超现实",
        "narrative_structure": "emotional_rollercoaster",
        "emotion_curve": [0.6, 0.7, 0.8, 0.5],
        "pacing": "匹配剪辑帧精确+固定遮挡隐形+一次性长镜头错觉, 节奏快",
        "opening_hook": "超现实画面0.5秒(模式打断)",
        "key_techniques": ["match_cut_magic", "frame_precise", "fixed_occlusion", "one_shot_illusion", "no_cg"],
        "target_audience": "全年龄/创意",
        "features": {
            "plot_progression": "超现实开场→魔法过程→不可能结果",
            "narrative_style": "创意>预算, 一镜魔法错觉",
            "emotion_signature": "惊喜+反复观看找剪辑点",
            "intensity_avg": 0.7, "emotion_dominant": "惊喜/趣味",
        },
        "matchable_tags": ["短视频", "创意", "魔术", "匹配剪辑", "隐形剪辑", "一镜到底", "全年龄", "创意"],
    },
    {
        "id": "vv_sam_kolder", "cn": "Sam Kolder旅行Vlog(代表)", "type": "短视频", "year": 2019, "director": "sam_kolder",
        "genre": ["旅行", "MV", "创意"], "duration": "60-180s", "vertical": False,
        "plot_pattern": "匹配转场旅行+色彩节奏+POV沉浸",
        "narrative_structure": "emotional_rollercoaster",
        "emotion_curve": [0.6, 0.7, 0.75, 0.8, 0.7],
        "pacing": "匹配转场无缝+黄暖电影调色+手持稳定+升格降格, 节奏流畅",
        "opening_hook": "最美风景+转场(视觉钩子)",
        "key_techniques": ["match_transition", "warm_cinema_grade", "handheld_stable", "speed_ramp", "pov"],
        "target_audience": "旅行/创意/青年",
        "features": {
            "plot_progression": "旅行流动→匹配转场→节奏高潮",
            "narrative_style": "旅行诗意=转场流畅, 视觉节奏驱动情感",
            "emotion_signature": "自由+流动的诗意",
            "intensity_avg": 0.7, "emotion_dominant": "自由/美",
        },
        "matchable_tags": ["短视频", "旅行", "MV", "匹配转场", "黄暖调", "手持稳定", "升格降格", "POV", "青年"],
    },
    {
        "id": "vv_brandon_li", "cn": "Brandon Li纪实短片(代表)", "type": "短视频", "year": 2020, "director": "brandon_li",
        "genre": ["纪实", "旅行", "人物"], "duration": "120-300s", "vertical": False,
        "plot_pattern": "纪实人物+电影感运动+自然光",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.5, 0.6, 0.55, 0.7, 0.6],
        "pacing": "手持稳定长镜头+黄金时刻+广角近距+动作匹配转场, 节奏纪实流畅",
        "opening_hook": "人物面部+环境(纪实钩子)",
        "key_techniques": ["handheld_long_take", "golden_hour", "wide_close", "match_action_transition", "ambient_sound_layer"],
        "target_audience": "纪实/旅行/成人",
        "features": {
            "plot_progression": "人物日常→电影感呈现→主题升华",
            "narrative_style": "纪实有电影感, 运动=情绪",
            "emotion_signature": "真实人物的电影感尊严",
            "intensity_avg": 0.6, "emotion_dominant": "真实/共鸣",
        },
        "matchable_tags": ["短视频", "纪实", "旅行", "手持长镜头", "黄金时刻", "广角近距", "动作匹配", "环境音", "成人"],
    },
    {
        "id": "vv_liziqi", "cn": "李子柒田园(代表)", "type": "短视频", "year": 2019, "director": "liziqi",
        "genre": ["田园", "文艺", "美食"], "duration": "180-600s", "vertical": False,
        "plot_pattern": "田园劳作+四季+食物+自然诗意",
        "narrative_structure": "kishōtenketsu",
        "emotion_curve": [0.4, 0.45, 0.5, 0.55, 0.5, 0.6],
        "pacing": "自然光黄金时刻+dappled光+大量留白+手工特写+风吹生命, 节奏极慢诗性",
        "opening_hook": "田园全景+劳作(诗意建立)",
        "key_techniques": ["golden_hour", "dappled_light", "negative_space", "handcraft_macro", "wind_life", "ambient_nature"],
        "target_audience": "全年龄/国际/治愈",
        "features": {
            "plot_progression": "劳作→四季→食物→诗意(日常即诗)",
            "narrative_style": "田园诗, 无对白靠视觉",
            "emotion_signature": "治愈+自然敬畏+东方美学",
            "intensity_avg": 0.45, "emotion_dominant": "宁静/治愈",
        },
        "matchable_tags": ["短视频", "田园", "文艺", "美食", "黄金时刻", "留白", "手工特写", "自然", "东方", "全年龄", "国际"],
    },
    {
        "id": "vv_wardrobe_swap", "cn": "抖音变装类(代表)", "type": "短视频", "year": 2023, "director": "unknown_viral",
        "genre": ["变装", "创意", "对比"], "duration": "10-15s", "vertical": True,
        "plot_pattern": "before→遮挡瞬间→after反差",
        "narrative_structure": "emotional_rollercoaster",
        "emotion_curve": [0.5, 0.6, 0.85, 0.6],
        "pacing": "固定机位遮挡切换+反差越大越有效+瞬间, 节奏极快",
        "opening_hook": "before形象(0.5秒钩子)",
        "key_techniques": ["fixed_occlusion_swap", "contrast_max", "instant_cut", "wardrobe_swap"],
        "target_audience": "全年龄/年轻/女性",
        "features": {
            "plot_progression": "before→遮挡→after(反差冲击)",
            "narrative_style": "变装对比, 反差即内容",
            "emotion_signature": "反差冲击+视觉爽",
            "intensity_avg": 0.7, "emotion_dominant": "冲击/爽",
        },
        "matchable_tags": ["短视频", "变装", "对比", "遮挡", "反差", "瞬间", "竖屏", "年轻", "女性"],
    },
    {
        "id": "vv_story_time", "cn": "故事time类(代表)", "type": "短视频", "year": 2023, "director": "unknown_viral",
        "genre": ["故事", "情感", "纪实"], "duration": "60-120s", "vertical": True,
        "plot_pattern": "结果先行+面部情绪+画面配合叙述",
        "narrative_structure": "in_medias_res",
        "emotion_curve": [0.8, 0.6, 0.7, 0.5, 0.8],
        "pacing": "面部情绪特写+画面配合+真实感>精良, 节奏中速情感",
        "opening_hook": "结果先行('我差点死了'钩子)",
        "key_techniques": ["face_emotion_closeup", "result_first", "real_over_polished", "ambient_sync"],
        "target_audience": "全年龄/情感",
        "features": {
            "plot_progression": "结果先行→过程叙述→情感收束",
            "narrative_style": "真实感>精良, 情感>信息",
            "emotion_signature": "共鸣+真实代入",
            "intensity_avg": 0.65, "emotion_dominant": "共鸣/真实",
        },
        "matchable_tags": ["短视频", "故事", "情感", "面部特写", "结果先行", "真实", "竖屏", "全年龄"],
    },
    {
        "id": "vv_skill_flex", "cn": "技能flex类(代表)", "type": "短视频", "year": 2023, "director": "unknown_viral",
        "genre": ["技能", "展示", "创意"], "duration": "30-60s", "vertical": True,
        "plot_pattern": "最惊人成果作开头+多角度慢放+技术细节",
        "narrative_structure": "emotional_rollercoaster",
        "emotion_curve": [0.8, 0.6, 0.7, 0.85, 0.7],
        "pacing": "多角度+慢放+特写技术细节+流畅自信, 节奏快技术",
        "opening_hook": "最惊人成果(技能钩子)",
        "key_techniques": ["multi_angle", "slowmo_detail", "tech_closeup", "flow_confidence"],
        "target_audience": "技能粉/年轻",
        "features": {
            "plot_progression": "惊人成果→过程揭秘→技术细节",
            "narrative_style": "流畅自信>难度, 技术展示",
            "emotion_signature": "技术敬畏+自信魅力",
            "intensity_avg": 0.75, "emotion_dominant": "敬畏/爽",
        },
        "matchable_tags": ["短视频", "技能", "展示", "多角度", "慢放", "特写", "流畅", "年轻"],
    },
    {
        "id": "vv_emotional_micro", "cn": "情感微剧场类(代表)", "type": "短视频", "year": 2023, "director": "unknown_viral",
        "genre": ["情感", "微剧场", "剧情"], "duration": "30-90s", "vertical": True,
        "plot_pattern": "冲突最激烈画面作开头+面部特写+微表情",
        "narrative_structure": "in_medias_res",
        "emotion_curve": [0.85, 0.5, 0.7, 0.6, 0.8],
        "pacing": "面部特写为主+环境极简+微表情真实, 节奏中速情绪递进",
        "opening_hook": "冲突最激烈画面(情绪钩子)",
        "key_techniques": ["face_closeup", "minimal_env", "micro_expression", "emotion_progression"],
        "target_audience": "情感/女性/全年龄",
        "features": {
            "plot_progression": "冲突开头→情绪递进→收束",
            "narrative_style": "微表情>大幅度, 情绪递进不平",
            "emotion_signature": "真实情绪+共鸣",
            "intensity_avg": 0.7, "emotion_dominant": "共鸣/虐或甜",
        },
        "matchable_tags": ["短视频", "情感", "微剧场", "面部特写", "微表情", "极简环境", "情绪递进", "竖屏", "女性"],
    },
]


# 索引: 按类型/导演/受众快速检索
def _build_index():
    idx = {"by_type": {}, "by_director": {}, "by_audience": {}, "by_tag": {}}
    for w in WORKS_CORPUS:
        idx["by_type"].setdefault(w["type"], []).append(w["id"])
        idx["by_director"].setdefault(w["director"], []).append(w["id"])
        for a in [w["target_audience"]]:
            idx["by_audience"].setdefault(a, []).append(w["id"])
        for t in w["matchable_tags"]:
            idx["by_tag"].setdefault(t, []).append(w["id"])
    return idx

WORKS_INDEX = _build_index()


def get_work(work_id):
    """按id获取作品"""
    for w in WORKS_CORPUS:
        if w["id"] == work_id:
            return w
    # 扩展库
    try:
        try:
            from knowledge_base.works_corpus_extended import get_extended_works
        except ImportError:
            from works_corpus_extended import get_extended_works
        for w in get_extended_works():
            if w["id"] == work_id:
                return w
    except Exception:
        pass
    return {}


def corpus_stats():
    """语料库统计(含全部 4 个库: 基础+扩展+电视剧+短剧)"""
    types = {}
    total = len(WORKS_CORPUS)
    for w in WORKS_CORPUS:
        types[w["type"]] = types.get(w["type"], 0) + 1
    for ext_fn, mod_name in [
        ("get_extended_works", "works_corpus_extended"),
        ("get_rich_works", "works_rich"),
        ("get_hot_shortform_works", "works_hot_shortform"),
    ]:
        try:
            try:
                mod = __import__("knowledge_base." + mod_name, fromlist=[ext_fn])
            except ImportError:
                mod = __import__(mod_name, fromlist=[ext_fn])
            ext = getattr(mod, ext_fn)()
            total += len(ext)
            for w in ext:
                # 4 个库的 type 字段可能不同(电影/电视剧/短剧), 归一化
                wtype = w.get("type") or w.get("genre", ["未分类"])[0] if w.get("genre") else "未分类"
                types[wtype] = types.get(wtype, 0) + 1
        except Exception:
            pass
    return {"total": total, "by_type": types}


def get_all_works():
    """获取全部作品(种子+扩展+热点短剧短视频),供feature_matcher使用"""
    all_w = list(WORKS_CORPUS)
    try:
        try:
            from knowledge_base.works_corpus_extended import get_extended_works
        except ImportError:
            from works_corpus_extended import get_extended_works
        all_w.extend(get_extended_works())
    except Exception:
        pass
    try:
        try:
            from knowledge_base.works_hot_shortform import get_hot_shortform_works
        except ImportError:
            from works_hot_shortform import get_hot_shortform_works
        all_w.extend(get_hot_shortform_works())
    except Exception:
        pass
    return all_w
