# -*- coding: utf-8 -*-
"""
作品库 — 电视剧/网剧库 V1.0
================================================
18 部 HBO/Netflix/中国顶级剧,每部 12 维,数据来自 IMDB/豆瓣。
覆盖美剧巅峰、英剧神作、亚洲剧王、中国现象级剧。
"""

WORKS_DATA = {
    "game_of_thrones": {
        "title_cn": "权力的游戏",
        "title_en": "Game of Thrones",
        "year_start": 2011,
        "year_end": 2019,
        "director": "David Benioff & D.B. Weiss",
        "genre": ["奇幻", "史诗", "权谋"],
        "rating_imdb": 9.2,
        "style_tags": ["铁王座", "龙", "家族", "权谋"],
        "visual_signature": "中世纪油画,冷蓝/金/血红,大场面,大远景",
        "key_scenes": ["血色婚礼", "私生子之战", "龙母焚城"],
        "narrative_structure": "POV多线,大型群像",
        "cultural_impact": "HBO巅峰,改变电视行业",
        "prompt_seed": "medieval power game, dragons, red wedding, iron throne, multiple POV",
        "director_view": {            "logline": "维斯特洛大陆七大王国的贵族为铁王座厮杀,同时面临北境异鬼和龙妈回归的远古威胁",            "theme": "权力的代价 / 家族宿命的不可逃 / 善恶的灰色",            "protagonist_arc": "无单一主角,POV轮换;Ned Stark 荣誉→死;Daenerys 失语→崛起→疯狂;Cersei 母亲→疯王;Jon Snow 私生子→王",            "conflict_structure": "家族vs家族(五王之战);人vs远古(异鬼);统治者vs内心(王座代价);多线POV汇聚",            "visual_palette": "中世纪油画+冷蓝/金/血红+战火橙+北境雪白+龙焰",            "lighting_approach": "实景+大远景+火把/烛光(室内)+低光(战争/阴谋)+史诗大场面",            "pacing_signature": "慢铺垫(宫廷戏)→中段加速(大战/血色婚礼)→快结尾(大战)+8季逐步失控",            "performance_direction": "Peter Dinklage Tyrion 智慧+嘴;Sean Bean Ned 荣誉;Emilia Clarke 龙母渐进式疯狂;Kit Harington Jon 沉静",            "thematic_layers": "表层:奇幻权谋;中层:权力的腐蚀(所有人);深层:善良在权力世界行不通;象征:铁王座/龙/雪/冰",            "philosophical_core": "When you play the game of thrones, you win or you die. - 权力的零和博弈",            "shot_sequence_analysis": "开场临冬城(Ned 荣誉)→君临(政治毒)→长城(异鬼伏笔)→血色婚礼(震撼)→私生子之战(史诗)→龙母焚城(毁灭)→Bran 称王(留白)",            "why_it_works": "①多POV 让观众代入不同视角②每个POV角色都会死=高风险③中世纪奇幻实景化=视觉革命④红色婚礼/黑水河之战=影史级场景",            "direct_lessons": "多POV必须各自独立;每个角色都'可杀';史诗大场面用实景+实拍;不要害怕'主角'死亡;长剧必须分季独立高潮",            "replication_template": "多POV轮换+中世纪奇幻+每季独立高潮+主角可死+实景大场面+长剧季节弧光",        },
    },
    "breaking_bad": {
        "title_cn": "绝命毒师",
        "title_en": "Breaking Bad",
        "year_start": 2008,
        "year_end": 2013,
        "director": "Vince Gilligan",
        "genre": ["犯罪", "剧情"],
        "rating_imdb": 9.5,
        "style_tags": ["制毒", "中产崩塌", "化学"],
        "visual_signature": "沙漠黄/绿,新墨西哥州,室内暖灯,化学符号",
        "key_scenes": ["沙漠制毒", "厕所对峙", "古斯炸死"],
        "narrative_structure": "中产堕入深渊,主角变反派",
        "cultural_impact": "AMC神剧, IMDb Top 3",
        "prompt_seed": "chemistry teacher, meth cook, new mexico desert, anti hero, family fall",
        "director_view": {            "logline": "高中化学老师Walter White确诊肺癌后,为家人制毒,从懦弱老师变黑帮帝王海森堡",            "theme": "中产崩塌 / 权力的诱惑 / 自我重塑",            "protagonist_arc": "Walter 懦弱教师(被轻视)→制毒(为家)→Heisenberg(权力感)→彻底黑化(妻儿被伤害)→死亡(选择)",            "conflict_structure": "Walter vs 体制(医保/制药);Walter vs 自己(良知);Walter vs Gus/Jack 帮派",            "visual_palette": "新墨西哥沙漠黄/绿+室内暖灯+化学符号(元素周期表)+绿色晶体(冰毒)",            "lighting_approach": "Vince Gilligan 明亮为主(沙漠)+ 关键场景极暗(死亡)+符号化元素(颜色=情绪)",            "pacing_signature": "慢铺垫(每季初)→中段加速(冲突)→高潮(每季后段大爆发)→62集 5 季弧光",            "performance_direction": "Bryan Cranston 渐进式黑化(眼睛/姿态/语速);Aaron Paul Jesse 纯真→崩溃;Anna Gunn Skyler 复杂",            "thematic_layers": "表层:犯罪;中层:中产尊严崩塌;深层:权力即自我;象征:冰毒晶体(白)/元素周期表(身份)/Heisenberg 面具",            "philosophical_core": "I am the danger. - 平凡人也能是危险的人",            "shot_sequence_analysis": "化学开场(教师身份)→癌症诊断(触发)→制毒(开始)→沙漠(双重身份)→炸 Gus(崛起)→Jack 帮(陨落)→林中死(终)",            "why_it_works": "①Walter 渐进式黑化让观众同情他②62集 5 季的弧光设计=前所未有的犯罪剧③'Heisenberg' 成为文化符号④结局不完美 Walter 选择=开放式",            "direct_lessons": "主角堕落要让观众共情;长期弧光要分季设计;演员的渐进式变化(眼睛/姿态)是关键;结尾要角色驱动",            "replication_template": "主角渐进式黑化+每季独立高潮+5季总弧光+演员渐进表演+化学/专业符号",        },
    },
    "sopranos": {
        "title_cn": "黑道家族",
        "title_en": "The Sopranos",
        "year_start": 1999,
        "year_end": 2007,
        "director": "David Chase",
        "genre": ["黑帮", "家庭", "心理"],
        "rating_imdb": 9.2,
        "style_tags": ["焦虑", "家庭", "心理治疗"],
        "visual_signature": "新泽西郊区,室内暖灯,自然光,餐厅家常",
        "key_scenes": ["Tony昏迷开场", "鸭子池塘", "最终剪影"],
        "narrative_structure": "心理双线,日常+犯罪",
        "cultural_impact": "HBO开山祖师,改写电视",
        "prompt_seed": "mob boss therapy, new jersey suburb, panic attacks, ducks pond, family dinner",
        "director_view": {            "logline": "新泽西黑帮老大Tony Soprano一边管理家族,一边接受心理治疗,处理焦虑症与家庭危机",            "theme": "现代黑帮的疲惫 / 男性焦虑 / 美国梦的隐喻",            "protagonist_arc": "Tony 焦虑(开场昏迷)→治疗(自我)→家族平衡(母亲/妻子/孩子)→中年危机(鸭子池塘象征)→结尾突然黑屏",            "conflict_structure": "Tony vs 焦虑(心理);Tony vs 家族(母亲/妻子/同辈);Tony vs FBI",            "visual_palette": "新泽西郊区+室内暖灯+自然光+餐厅家常+Tony家暖橙",            "lighting_approach": "David Chase 日常感(纪录片式)+偶尔梦幻(昏迷)→结尾突然切断(黑屏)",            "pacing_signature": "慢日常(家庭+心理治疗)+突然暴力(执行)+多年弧光(86集)+结尾突然切断(争议)",            "performance_direction": "James Gandolfini 焦虑+疲惫+可爱(矛盾体)=影史级表演;Edie Falco 妻子 Carmela 复杂",            "thematic_layers": "表层:黑帮;中层:中年焦虑;深层:美国梦的疲惫;象征:鸭子池塘(自由)/俄狄浦斯(家庭)/Meadow(继承)",            "philosophical_core": "When you're married, the boredom is so intense... - 现代生活的无聊即绝望",            "shot_sequence_analysis": "Tony 昏迷开场(焦虑)→治疗师(自我)→家族日常(家庭)→黑帮业务(暴力)→鸭子池塘(渴望)→结尾黑屏(突然)",            "why_it_works": "①Tony 既黑帮又焦虑=矛盾体观众共情②心理治疗=创新(前所未有)③结尾黑屏=史上最大争议(HBO 被骂了 20 年)④日常感+偶尔暴力=节奏",            "direct_lessons": "主角要有人性弱点(焦虑/治疗);日常生活要够长才让暴力震撼;结尾争议性=讨论度;现代黑帮=中产化",            "replication_template": "黑帮老大+心理治疗+焦虑+家庭日常+结尾争议(切断/留白)+86集慢弧光",        },
    },
    "the_wire": {
        "title_cn": "火线",
        "title_en": "The Wire",
        "year_start": 2002,
        "year_end": 2008,
        "director": "David Simon",
        "genre": ["犯罪", "社会", "城市"],
        "rating_imdb": 9.3,
        "style_tags": ["巴尔的摩", "制度", "群像"],
        "visual_signature": "手持纪实,巴尔的摩港口,室内自然光,城市实景",
        "key_scenes": ["码头监听", "Omar出没", "Marlo街头"],
        "narrative_structure": "5季每季一机构(港口/工会/政客/学校/媒体)",
        "cultural_impact": "电视史上最伟大, IMDb Top 1",
        "prompt_seed": "baltimore drug trade, institutional critique, ensemble, hand held realism",
        "director_view": {            "logline": "巴尔的摩毒品/政治/教育/媒体五大系统同时崩溃的群像剧,无主角",            "theme": "系统的失败 / 个人的渺小 / 美国城市的真相",            "protagonist_arc": "无主角,每季一个系统(毒品/港口/政治/教育/媒体);Omar 永远是'道德标杆'例外",            "conflict_structure": "警察vs毒贩(无法胜利);系统vs个人(都失败);社会结构(种族/阶级)无法破",            "visual_palette": "巴尔的摩现实+灰/棕/自然光+港口/街道+监狱+中产郊区",            "lighting_approach": "纪录片感+手持跟拍+自然光+城市真实(不用柔光)",            "pacing_signature": "极慢(每季 12 集只讲一个系统)+多线并进+季节弧光独立但汇聚",            "performance_direction": "非职业演员(真实)+Dominic West McNulty 疲惫警察;Michael K. Williams Omar 同性恋匪盗(影史)",            "thematic_layers": "表层:警匪;中层:系统的失败(警/政/教/媒都腐败);深层:美国种族的循环;象征:港口/毒品/教育/报纸",            "philosophical_core": "The game is rigged. - 系统永远在,个人改变不了",            "shot_sequence_analysis": "巴尔的摩开场(全景)=系统→毒品线(警察困境)→Omar 抢劫(道德对比)→学校线(失败)→媒体线(失败)→报纸结尾(留白)",            "why_it_works": "①无主角群像=革命性②每季一个系统=完整剖析③Omar 作为道德标杆=观众出口④'系统永远在'的悲观=真实",            "direct_lessons": "无主角群像剧可以成立;每季一个独立系统剖析;非职业演员=真实;长期剧不要怕慢(60集);道德标杆角色(Omar)是出口",            "replication_template": "无主角群像+每季一个系统+非职业演员+悲观真实+道德标杆例外",        },
    },
    "chernobyl": {
        "title_cn": "切尔诺贝利",
        "title_en": "Chernobyl",
        "year_start": 2019,
        "year_end": 2019,
        "director": "Johan Renck",
        "genre": ["历史", "灾难", "迷你剧"],
        "rating_imdb": 9.3,
        "style_tags": ["核灾", "真相", "苏联"],
        "visual_signature": "胶片质感,冷蓝/灰/辐射黄,医院/反应堆,真实记录",
        "key_scenes": ["反应堆爆炸", "消防员送医院", "矿工挖隧道"],
        "narrative_structure": "5集线性灾难还原",
        "cultural_impact": "IMDB Top 1迷你剧",
        "prompt_seed": "nuclear disaster, soviet cover up, hospital radiation, miners dig, real footage",
        "director_view": {            "logline": "1986 年切尔诺贝利核电站爆炸,消防员/科学家/苏联官员在真相与谎言间做出选择",            "theme": "真相的代价 / 谎言对系统的破坏 / 个体在灾难中的选择",            "protagonist_arc": "Valery 科学家(追真相)→消防员(送死)→工人(自杀清污)→Dmitri 副部长(自尽);系统压制真相",            "conflict_structure": "科学家vs系统(谎言);真相vs谎言(代价);个体vs灾难(选择);官僚vs良知",            "visual_palette": "苏联灰/绿+辐射蓝(开裂)+切尔诺贝利废墟(纪录片感)+医院暗黄",            "lighting_approach": "Johan Renck 阴冷+灰+辐射蓝(放射物特殊光)+医院+地下室(指挥)",            "pacing_signature": "慢铺垫(爆炸+掩盖)→加速(真相揭露)→极快结尾(献身/清理)+5集精炼",            "performance_direction": "Jared Harris Valery 内化科学家+道德;Stellan Skarsgård 副部长 崩溃选择;Emily Watson 物理学家 坚定",            "thematic_layers": "表层:灾难;中层:苏联体制的谎言;深层:真相是文明的底线;象征:辐射/堆芯/纪录片质感",            "philosophical_core": "What is the cost of lies? It's not that we'll mistake them for the truth. The real danger is that if we hear enough lies, then we no longer recognize the truth. - 谎言让真相不可识",            "shot_sequence_analysis": "爆炸(慢)→掩盖(快)→真相(慢)→献身(快)→清理(慢)→'我不再害怕'(结尾)",            "why_it_works": "①基于真实=震撼②苏联体制的谎言剖析=历史意义③演员的克制表演=避免煽情④5集精炼(不拖沓)⑤辐射的视觉表达",            "direct_lessons": "基于真实的力量;克制表演比煽情强;精炼集数(5集)足以讲完;体制剖析要冷静;献身场景要真",            "replication_template": "基于真实灾难+体制谎言剖析+5集精炼+克制表演+献身场景+辐射/灾难视觉",        },
    },
    "succession": {
        "title_cn": "继承之战",
        "title_en": "Succession",
        "year_start": 2018,
        "year_end": 2023,
        "director": "Jesse Armstrong",
        "genre": ["商战", "家族", "喜剧"],
        "rating_imdb": 8.9,
        "style_tags": ["传媒帝国", "无能继承人", "冷幽默"],
        "visual_signature": "曼哈顿高楼/直升机,室内豪华,西装革履,极简构图",
        "key_scenes": ["Logan生日趴", "Kendall独白rap", "最后董事局"],
        "narrative_structure": "家族群像+商战",
        "cultural_impact": "HBO当代神剧",
        "prompt_seed": "media mogul family, weak heirs, manhattan boardroom, sharp suits, dark humor",
        "director_view": {            "logline": "媒体帝国Logan Roy的成年子女们为继承权明争暗斗,父亲决定他们谁都不像",            "theme": "权力的继承 / 家庭即公司 / 爱的无能为力",            "protagonist_arc": "Kendall 摇摆(被父亲压制)→叛逆(车祸)→政变(失败);Shiv 记者→妻子→野心;Roman 玩笑→崩溃;Connor 局外人",            "conflict_structure": "子女vs父亲(权力);子女vs子女(继承);爱vs权力(不可兼)",            "visual_palette": "高饱和现代+玻璃高楼+私人飞机+冷暖对比(办公室冷+卧室暖)",            "lighting_approach": "现代极简+玻璃反射+会议室冷白+卧室暖橙+大远景(城市权力)",            "pacing_signature": "慢对白(权力游戏)+突然决断(父亲一句话)+39集 4 季+每集大转折",            "performance_direction": "Brian Cox Logan 权威+衰败+反复;Jeremy Strong Kendall 神经质+失控(方法派);Sarah Snook Shiv 冷静",            "thematic_layers": "表层:家族继承;中层:爱的无能为力;深层:权力即身份(没有Logan你什么都不是);象征:玻璃高楼/私人飞机/餐桌",            "philosophical_core": "If you are not the chosen one, do not try to make yourself chosen. - 继承即命运",            "shot_sequence_analysis": "Logan 摔倒(开头)=权力交接伏笔→家庭晚餐(权力游戏)→Kendall 政变(失败)→Logan 死(冲击)→结尾悬空(留白)",            "why_it_works": "①Logan 权威+衰败=影史级角色②'我就是神'金句+对白密集=权力戏③'Kendall 决堤'演员的崩溃表演④餐桌戏=权力战场⑤结尾悬空=继承空",            "direct_lessons": "权力戏靠对白而非动作;餐桌=战场;父权角色要反复无常(让观众紧张);演员方法派(Strong 沉浸式)=极致;结尾不要给答案",            "replication_template": "家族继承战+权威父亲+餐桌=战场+对白密集+演员方法派+结尾悬空",        },
    },
    "true_detective_s1": {
        "title_cn": "真探S1",
        "title_en": "True Detective Season 1",
        "year_start": 2014,
        "year_end": 2014,
        "director": "Nic Pizzolatto",
        "genre": ["犯罪", "悬疑", "哲学"],
        "rating_imdb": 8.9,
        "style_tags": ["路易斯安那", "哲学", "时间跳跃"],
        "visual_signature": "路易斯安那湿地,长镜头6分钟(抢劫),黄绿锈色",
        "key_scenes": ["6分钟抢劫长镜头", "Rust独白", "最终对决"],
        "narrative_structure": "时间跳跃双线调查",
        "cultural_impact": "HBO神剧,哲学犯罪剧巅峰",
        "prompt_seed": "louisiana swamp, 6 minute heist shot, philosophical cop, time jump, yellow green",
        "director_view": {            "logline": "1995 年路易斯安那州 Ritual Killer 案,2012 年两位警探 Martin 与 Rust 的回忆录式追凶",            "theme": "虚无主义 vs 救赎 / 兄弟情 / 真相的黑暗",            "protagonist_arc": "Rust 虚无(失去妻女)→案件(重新相信)→结尾'光在隧道里'(回归光);Martin 家庭危机→酒→与 Rust 重逢",            "conflict_structure": "侦探vs连环杀手(信仰);Rust vs 虚无(内心);Martin vs 家庭(表面)",            "visual_palette": "路易斯安那湿热+绿/棕/暗黄+Bayou(沼泽)+Rust 公寓黑",            "lighting_approach": "Cary Joji Fukunaga 影史级长镜头(6 分钟)+雨/夜/湿地+手电筒光(追踪)",            "pacing_signature": "双时间线(1995/2012)交叉+长镜头(影史 6 分钟)+慢追凶+突然暴力+结尾哲学",            "performance_direction": "Matthew McConaughey Rust 哲学+虚无+爆发(奥斯卡);Woody Harrelson Martin 火爆+崩溃",            "thematic_layers": "表层:犯罪追凶;中层:虚无vs救赎;深层:人类意识的本质(光);象征:鹿角王(仪式)/隧道/星星",            "philosophical_core": "I think human consciousness is a tragic misstep in evolution. - 意识即悲剧,但光在",            "shot_sequence_analysis": "教堂画外音(Rust 哲学)=主题→监狱对峙(影史长镜头)→灯塔审讯(信仰)→地道追凶(长镜头)→结尾'光'(哲学)",            "why_it_works": "①影史 6 分钟长镜头(监狱+枪战)=革命②Matthew 减肥+化妆=奥斯卡③Rust 哲学独白=影史级台词④鹿角王仪式=震撼视觉⑤双时间线结构",            "direct_lessons": "长镜头要承担剧情(不是炫技);演员的身体变化(减肥)=角色;哲学独白+犯罪=主题深化;双时间线=神秘感;结尾要哲学",            "replication_template": "双时间线+影史长镜头+哲学独白+演员身体变化+宗教仪式视觉+虚无vs光",        },
    },
    "dark": {
        "title_cn": "暗黑",
        "title_en": "Dark",
        "year_start": 2017,
        "year_end": 2020,
        "director": "Baran bo Odar",
        "genre": ["科幻", "悬疑", "德剧"],
        "rating_imdb": 8.8,
        "style_tags": ["时间循环", "德国小镇", "核"],
        "visual_signature": "德国小镇阴沉,蓝色灰,洞穴,雨,时间线",
        "key_scenes": ["洞穴发现", "时间机器", "三季穿越"],
        "narrative_structure": "三季时间循环",
        "cultural_impact": "Netflix德剧巅峰",
        "prompt_seed": "german town, time cycle, nuclear cave, family tree, dark blue gray",
        "director_view": {            "logline": "德国小镇 Winden 2019/1986/1953 三个时间线因孩子失踪交叉,揭示时间循环与命运",            "theme": "时间循环 / 命运的不可逃 / 因果的悖论",            "protagonist_arc": "Jonas 失父→穿越→中年→老去→回到起点(循环);多家族 33 年跨代",            "conflict_structure": "人vs时间(无法改变);家族vs命运(3 家族循环);真相vs时间悖论",            "visual_palette": "德国冷灰+洞穴+钟表+时间机器(球体)+Yellow Raincoat(黄色雨衣)",            "lighting_approach": "Baran bo Odar 阴冷+蓝灰+洞穴+闪电(穿越时刻)+中世纪钟表(时间)",            "pacing_signature": "极慢(铺垫3家族)+快(揭示)+3 季总弧光(第3季全面揭示)+每集结尾钩子",            "performance_direction": "Louis Hofmann 多代 Jonas(少年→中年);Lisa Vicari Martha 平行宇宙;Oliver Masucci 老年 Ulrich",            "thematic_layers": "表层:科幻;中层:时间的不可逆;深层:命运即选择(薛定谔);象征:钟表/洞穴/黄雨衣/球体",            "philosophical_core": "We are doomed to repeat. - 命运即循环,但选择决定当下",            "shot_sequence_analysis": "2019 失踪(开场)=谜→1986 真相(回溯)→1921 起源(再回)→末日(2020/2052/其他)→循环结束(亚当与夏娃)",            "why_it_works": "①3 个时间线平行(前所未有)②德国冷静质感=独特氛围③多家族跨代叙事④第3季彻底揭示+平行宇宙⑤黄雨衣=影史符号",            "direct_lessons": "多时间线要清晰标注;多家族跨代=史诗;德国冷静+科幻=独特氛围;每集结尾钩子;第3季彻底揭示+开放",            "replication_template": "3时间线+多家族跨代+冷静质感+每集钩子+第3季揭示+循环/命运主题",        },
    },
    "the_queens_gambit": {
        "title_cn": "后翼弃兵",
        "title_en": "The Queen's Gambit",
        "year_start": 2020,
        "year_end": 2020,
        "director": "Scott Frank",
        "genre": ["剧情", "成长"],
        "rating_imdb": 8.6,
        "style_tags": ["国际象棋", "天才少女", "60年代"],
        "visual_signature": "60年代复古,室内暖灯,黑白格地板,大量特写",
        "key_scenes": ["天花板下棋", "莫斯科邀请赛", "最终冠军"],
        "narrative_structure": "天才成长+毒瘾",
        "cultural_impact": "Netflix2020年现象级",
        "prompt_seed": "chess prodigy girl, 1960s retro, orphanage, ceiling play, moscow tournament",
        "director_view": {            "logline": "1960 年代天才少女Beth Harmon在孤儿院学会国际象棋,击败世界冠军,但要克服药物与孤独",            "theme": "天才与代价 / 女性自我实现 / 孤独的救赎",            "protagonist_arc": "孤儿院(药物依赖)→自学(天赋)→比赛(上升)→崩溃(成瘾)→纽约(复出)→失败(认清)→俄罗斯(救赎)",            "conflict_structure": "Beth vs 男性世界(国际象棋);Beth vs 自己(药物+孤独);天才vs代价",            "visual_palette": "60 年代复古+暖橙(美国)+冷蓝(俄罗斯)+棋盘方格+连衣裙",            "lighting_approach": "Scott Frank 复古质感+暖光(美国)+冷光(俄罗斯)+天花板/地板构图+棋盘+车灯",            "pacing_signature": "慢铺垫(童年+孤儿院)→加速(比赛)→慢结尾(俄罗斯+自我)→7集精炼",            "performance_direction": "Anya Taylor-Joy 沉静+眼睛表演(影史级选角)+Beth 内在(药物/性/孤独)",            "thematic_layers": "表层:国际象棋;中层:女性在男性世界;深层:天才的代价+孤独;象征:棋盘/药物(绿黄药)/母亲",            "philosophical_core": "The only winning move is to play. - 唯一不败的方式是继续",            "shot_sequence_analysis": "孤儿院(药物)→自学(天才)→第一比赛(崛起)→哈利路亚(突破)→纽约(失败)→俄罗斯(救赎)",            "why_it_works": "①Anya 选角=影史(眼睛表演)②60 年代复古质感完美③女性题材+国际象棋=突破④天花板/地板构图=视觉⑤7集精炼",            "direct_lessons": "选角要极准(眼睛表演);复古质感要从服装到灯光统一;女性题材+冷门领域=突破;7集足以讲完;天花板构图=压抑",            "replication_template": "天才+复古时代+女性视角+选角为王+天花板构图+7集精炼+孤独救赎",        },
    },
    "severance": {
        "title_cn": "人生切割术",
        "title_en": "Severance",
        "year_start": 2022,
        "year_end": "ongoing",
        "director": "Dan Erickson",
        "genre": ["科幻", "悬疑", "办公室"],
        "rating_imdb": 8.7,
        "style_tags": ["工作/生活分离", "反乌托邦"],
        "visual_signature": "极简白色办公室,荧光灯,蓝色冷调,光面地面",
        "key_scenes": ["办公室神秘奖励", "大楼外逃", "Helly跳楼"],
        "narrative_structure": "工作内外双线",
        "cultural_impact": "Apple TV+神剧",
        "prompt_seed": "office cubicle brain split, sterile white floor, fluorescence, work life divide",
        "director_view": {            "logline": "未来公司 Lumon 让员工切除工作/生活记忆,Mark 选择切除后陷入公司邪教与阴谋",            "theme": "工作与生活的分离 / 自由的代价 / 记忆与身份",            "protagonist_arc": "Mark 切除(逃避丧妻痛苦)→办公室(分裂人格)→发现阴谋→拒绝切除(选真实)",            "conflict_structure": "人vs公司(邪教);记忆vs身份(分裂);工作vs生活(切割不可能)",            "visual_palette": "极简冷白+走廊(无限)+绿松石+室外(现实暖)→办公室(冷)+白色制服",            "lighting_approach": "Ben Stiller 反乌托邦极简+长走廊+几何+冷白+室外暖光(对比)",            "pacing_signature": "极慢铺垫(办公室日常)→加速(阴谋)→结尾(选择+动乱)→2 季悬念",            "performance_direction": "Adam Scott 内部分裂(办公室 Mark vs 户外 Mark);Patricia Arquette 老板诡异;Zach Cherry 黑笑话",            "thematic_layers": "表层:科幻办公;中层:工作与生活的本质;深层:记忆即身份;象征:走廊(无限)/地图/数字/感谢歌",            "philosophical_core": "Would you like to be free? - 自由=记忆的痛苦",            "shot_sequence_analysis": "电梯开场(切割)→办公室(反乌托邦日常)→户外(另一个 Mark)→阴谋(发现)→结尾选择(真实)",            "why_it_works": "①工作/生活记忆切割=原创科幻设定②极简反乌托邦办公=视觉签名③演员分裂式表演(双重身份)④走廊=无限⑤结尾'找到她'选择",            "direct_lessons": "原创科幻设定=从概念开始;极简反乌托邦=视觉;演员双重身份表演=难点;走廊=无限隐喻;结尾要'选择真实'",            "replication_template": "原创设定+反乌托邦办公+双重身份表演+极简走廊+工作/生活主题+选择真实",        },
    },
    "squid_game": {
        "title_cn": "鱿鱼游戏",
        "title_en": "Squid Game",
        "year_start": 2021,
        "year_end": "ongoing",
        "director": "Hwang Dong-hyuk",
        "genre": ["悬疑", "生存", "韩剧"],
        "rating_imdb": 8.0,
        "style_tags": ["儿童游戏", "巨额奖金", "韩国"],
        "visual_signature": "粉红/绿/黄糖果色宿舍,几何游戏场地,鲜艳对比",
        "key_scenes": ["一二三木头人", "椪糖", "鱿鱼游戏"],
        "narrative_structure": "生存游戏6轮",
        "cultural_impact": "Netflix韩国现象级",
        "prompt_seed": "child game survival, dormitory pink green, huge cash prize, geometric arena",
        "director_view": {            "logline": "456 名负债累累的人参加童年游戏,胜者可获 456 亿韩元,败者死亡",            "theme": "资本主义批判 / 阶级不可越 / 童年即地狱",            "protagonist_arc": "Gi-hun 失败司机(负债)→游戏(为钱)→发现真相(退赛)→又回来(为救 Sang-woo)→红发男人(再战)",            "conflict_structure": "穷人vs游戏(资本);选手vs选手(淘汰);童年游戏vs成人死亡(反差)",            "visual_palette": "马卡龙色(童年反差)+粉红士兵+几何(圆/方/三角)+血红死亡",            "lighting_approach": "Hwang Dong-hyuk 高饱和童年+反差的成人暴死+几何(楼梯)+反差色",            "pacing_signature": "慢铺垫(6 集铺垫+社会)+快游戏(6 集加速)+红色灯光(暴死)+2季悬念",            "performance_direction": "Lee Jung-jae Gi-hun 平民+善良+崩溃;Park Hae-soo Sang-woo 知识分子堕落;Wi Ha-jun 警察",            "thematic_layers": "表层:生存游戏;中层:资本主义批判;深层:童年的残酷本质;象征:糖饼/马卡龙色/几何/楼梯",            "philosophical_core": "We are all the same. We are all just animals. - 人类在压力下即动物",            "shot_sequence_analysis": "游戏介绍(慢)=悬念→第一夜(红光)=震撼→糖饼(童年反差)→玻璃桥(智斗)→鱿鱼游戏(肉搏)→红发男人(再战)",            "why_it_works": "①童年游戏+成人死亡=反差点子②马卡龙色+暴力=Netflix全球爆款③韩剧国际化=西方成功④阶级批判普世⑤红发男人=续作悬念",            "direct_lessons": "反差视觉(童年+死亡)=爆款;阶级批判普世;韩剧可以全球;游戏设计要简单(观众易懂);续作悬念=商业",            "replication_template": "童年游戏+成人死亡+马卡龙色+阶级批判+全球爆款+续作悬念",        },
    },
    "三体": {
        "title_cn": "三体",
        "title_en": "Three-Body Problem (CN)",
        "year_start": 2023,
        "year_end": 2023,
        "director": "Yang Lei",
        "genre": ["科幻", "中国", "史诗"],
        "rating_imdb": 8.7,
        "style_tags": ["三体游戏", "ETO", "古筝行动"],
        "visual_signature": "中国80年代+现代+三体游戏,冷蓝/暗,沙漠红岸基地",
        "key_scenes": ["倒计时", "古筝行动", "三体游戏"],
        "narrative_structure": "三线时空,科学边界",
        "cultural_impact": "中国科幻剧天花板,Netflix全球播",
        "prompt_seed": "three body game, ETO cult, countdown, guzheng action, red coast base",
        "director_view": {            "logline": "中国科学家叶文洁在文革后向宇宙发送信号,三体人入侵地球,人类面临'不要回答'的道德抉择",            "theme": "人类文明的脆弱 / 科学的代价 / 宇宙的沉默",            "protagonist_arc": "叶文洁 绝望(文革)→发送信号→后悔(ETO 分裂);汪淼 纳米科学家→史强协助→'古筝行动'→'黑暗森林'认知;史强 警察→协助汪淼",            "conflict_structure": "人类vs三体(降维);科学vs信仰;个人vs文明(叶文洁选择);三体内部(拯救派vs降临派)",            "visual_palette": "中国60s文革(灰)→现代北京(冷蓝)→三体游戏(奇幻)→ETO 暗红→'古筝行动'纳米丝",            "lighting_approach": "Mohan Zhang(腾讯版)/Weir/Derbyshire(网飞版)+文革质感(灰)+三体游戏(奇幻)+'古筝行动'白天高光+夜晚蓝光",            "pacing_signature": "多时间线(60s/现代/三体游戏)+慢铺垫+加速(ETO 危机)+'古筝行动'+三体真相+季末钩子",            "performance_direction": "王子文/陈瑾 叶文洁 冷+绝望;张鲁一/John Bradley 汪淼 科学家沉静;于和伟/Sea Shimooka 史强 阳刚直",            "thematic_layers": "表层:科幻;中层:文明的脆弱;深层:黑暗森林法则(宇宙社会学);象征:纳米丝/三体游戏/智子/ETO 暗红",            "philosophical_core": "The universe is a dark forest. Every civilization is an armed hunter stalking through the trees. - 宇宙即黑暗森林",            "shot_sequence_analysis": "文革叶文洁(灰)→红岸基地(发送)=原点→现代汪淼(冷)→三体游戏(奇幻)→ETO 暗红→'古筝行动'(纳米丝白)→'不要回答'",            "why_it_works": "①刘慈欣原作+东方哲学=世界级②'古筝行动'视觉震撼(纳米丝切船)③'黑暗森林'宇宙社会学=哲学④多时间线+三体游戏=科幻感⑤季末'不要回答'钩子",            "direct_lessons": "中国科幻IP=世界级潜力;科幻特效要扎实(古筝行动);哲学内核要保留(黑暗森林);多时间线+游戏叙事=中国式;季末钩子=续作",            "replication_template": "中国IP+多时间线+游戏叙事+黑暗哲学+扎实特效(古筝/智子)+季末钩子",        },
    },
    "漫长的季节": {
        "title_cn": "漫长的季节",
        "title_en": "The Long Season",
        "year_start": 2023,
        "year_end": 2023,
        "director": "Xin Shuang",
        "genre": ["悬疑", "东北", "时代"],
        "rating_imdb": 9.4,
        "style_tags": ["东北下岗", "碎尸案", "90年代"],
        "visual_signature": "东北90年代,工厂区,秋日金色,白桦林",
        "key_scenes": ["火车鸣笛", "碎尸袋", "彪子开车"],
        "narrative_structure": "时代三线并进,草蛇灰线",
        "cultural_impact": "2023年豆瓣9.4神剧",
        "prompt_seed": "northeast china 1990s, factory layoffs, dismembered case, birch forest, golden autumn",
        "director_view": {            "logline": "1998 年东北桦钢下岗案,出租车司机王响追查 18 年前儿子王阳被谁杀死",            "theme": "时代碾压个体 / 真相的迟到 / 东北的失意",            "protagonist_arc": "王响 桦钢工人(1998)→下岗(2000s)→出租车司机(2016)→追凶(老年);龚彪 下海(失败)→中风;马德胜 刑警(1998)→老年舞蹈",            "conflict_structure": "时代vs个体(下岗);真相vs 18 年沉默;老年vs过去",            "visual_palette": "东北金秋(1998)→灰白下岗(2000s)→现代暖;冬雪;桦林黄;绿皮火车",            "lighting_approach": "辛爽 暖金秋(1998)+冷下岗(2000s)+老年+雪+火车=东北质感",            "pacing_signature": "三时间线交叉(1998/2000s/2016)+慢铺垫+12集精炼+结尾'往前看别回头'",            "performance_direction": "范伟 王响 东北口音+固执+温情;秦昊 龚彪 失意+中风+魅力;陈明昊 马队 刑警+老年舞蹈",            "thematic_layers": "表层:东北追凶;中层:下岗时代碾压;深层:迟到的真相无法挽回;象征:火车/桦林/雪/港商(尸)",            "philosophical_core": "往前走,别回头。 - 真相已过去,要向前看",            "shot_sequence_analysis": "1998桦钢(暖金秋)→儿子死(伏笔)→2000s 下岗(灰)→2016 老年(追凶)→真相(火车)→'往前看'(结尾)",            "why_it_works": "①东北下岗时代情绪共鸣②范伟影帝级表演③辛爽多时间线结构④结尾'往前看'情感爆发⑤12集精炼不拖沓",            "direct_lessons": "时代情绪共鸣=地域题材;多时间线结构(1998/2000s/2016)=厚度;演员选准(范伟)=影帝;结尾情感爆发=观众出口;12集精炼",            "replication_template": "时代情绪+多时间线(过去/现在/老年)+地域质感+影帝级演员+情感爆发结尾+12集精炼",        },
    },
    "狂飙": {
        "title_cn": "狂飙",
        "title_en": "The Knockout",
        "year_start": 2023,
        "year_end": 2023,
        "director": "Xu Jizhou",
        "genre": ["犯罪", "扫黑", "中国"],
        "rating_imdb": 8.5,
        "style_tags": ["黑社会", "警察", "20年跨度"],
        "visual_signature": "中国南方城市,室内暖灯,大量对白戏,时间跨度黄绿蓝",
        "key_scenes": ["高启强发家", "指导组入驻", "最终审判"],
        "narrative_structure": "20年三段式扫黑",
        "cultural_impact": "2023年现象级国产剧",
        "prompt_seed": "chinese anti mafia 20 years, cop informant, organized crime, interrogation",
        "director_view": {            "logline": "2000-2020 年,警察安欣与黑社会高启强从正义 vs 邪恶到相互纠缠 20 年",            "theme": "黑社会的崛起 / 体制内腐败 / 善恶的循环",            "protagonist_arc": "高启强 鱼贩(2021)→小混混(2000)→建工集团(2006)→黑社会(2014)→人大代表(2020);安欣 热血警察(2000)→失望(2014)→疲惫(2020)",            "conflict_structure": "警察vs黑社会(20年);高启强vs自己(欲望);安欣vs体制(孤独)",            "visual_palette": "2000 绿(菜市场)+2010 金(京海繁华)+2020 灰冷+夜店霓虹+黑帮金",            "lighting_approach": "徐纪周 暖金(高启强崛起)+冷灰(安欣疲惫)+霓虹(黑帮)→2000-2020 时代质感",            "pacing_signature": "三时间线(2000/2006/2020)交叉+39集 节奏+高启强弧光=影史级反派成长",            "performance_direction": "张颂文 高启强 三阶段(鱼贩→大佬→人大代表) 影史级反派;张译 安欣 热血→失望→疲惫",            "thematic_layers": "表层:扫黑;中层:黑社会如何崛起(时代);深层:善恶的循环(好人累坏人爽);象征:鱼档/奶茶/白金瀚/指导组",            "philosophical_core": "风浪越大鱼越贵. - 时代的风浪让普通人变黑社会",            "why_it_works": "①张颂文高启强三阶段表演=影史级反派②三时间线(2000/2006/2020)结构③黑社会如何崛起的现实写照④'风浪越大鱼越贵'金句⑤安欣的孤独=出口",            "direct_lessons": "反派要有'成长弧光'(鱼贩→大佬);多时间线展示时代;演员要演'三阶段';体制内孤独=观众共情;扫黑题材=普世共鸣",            "replication_template": "三时间线+反派成长弧光+影帝级演员+时代+体制+风浪越大金句",        },
    },
    "隐秘的角落": {
        "title_cn": "隐秘的角落",
        "title_en": "The Bad Kids",
        "year_start": 2020,
        "year_end": 2020,
        "director": "Xin Shuang",
        "genre": ["悬疑", "中国", "家庭"],
        "rating_imdb": 8.8,
        "style_tags": ["儿童", "爬山", "南方小镇"],
        "visual_signature": "中国南方小镇,潮湿,室内自然光,童年阴影",
        "key_scenes": ["爬山拍照", "朱朝阳日记", "最后船上"],
        "narrative_structure": "三孩子视角,暗线多重",
        "cultural_impact": "2020年国产剧神作",
        "prompt_seed": "kids accidental witness, southern town, diary, climbing mountain, humid summer",
        "director_view": {            "logline": "三个孩子在景区玩耍时无意拍到谋杀案,选择要 30 万还是报警,与凶手周旋",            "theme": "童真 vs 成人恶 / 选择的代价 / 家庭悲剧",            "protagonist_arc": "朱朝阳 乖学生(伪装)→黑化(借刀杀人);严良 孤儿(天真)→被利用;普普 早熟(救弟弟)→死亡;张东升 杀人(软弱)→被反杀",            "conflict_structure": "孩子vs成人(凶手);孩子vs孩子(背叛);童年vs成人(伪装)",            "visual_palette": "南方湿热+绿色(夏天)+阴雨+朱朝阳家冷+张东升家暖+数学课",            "lighting_approach": "辛爽(网剧) 阴冷+绿色(夏)+潮湿+高对比+阴影+楼道",            "pacing_signature": "12集 慢铺垫+孩子心理+突然暴力+结尾开放(朱朝阳黑化?)",            "performance_direction": "荣梓杉 朱朝阳 天真+黑化(孩子演技影史);秦昊 张东升 秃头+杀人+温情;王圣迪 普普 早熟+可怜",            "thematic_layers": "表层:悬疑;中层:童真vs成人恶;深层:家庭的悲剧如何养出朱朝阳;象征:日记(伪造)/魔方/数学(秩序)",            "philosophical_core": "Children are not as innocent as we think. - 童真与恶的边界",            "shot_sequence_analysis": "景区拍摄(悬念)→三个孩子(联盟)→警告张东升(周旋)→朱朝阳黑化(借刀杀人)→结尾'你可以相信童话'",            "why_it_works": "①孩子主演+演技=突破②秦昊秃头张东升=影史③'你可以相信童话'双关④12集精炼⑤朱朝阳黑化的开放",            "direct_lessons": "孩子题材+演技突破=爆款;反派有温情面=复杂;双关结尾=讨论度;家庭悲剧如何养成恶=主题;12集精炼",            "replication_template": "孩子主演+演技突破+反派温情+双关结尾+家庭悲剧+12集精炼+12集",        },
    },
    "band_of_brothers": {
        "title_cn": "兄弟连",
        "title_en": "Band of Brothers",
        "year_start": 2001,
        "year_end": 2001,
        "director": "Tom Hanks (执行制), David Frankel等",
        "genre": ["战争", "二战", "迷你剧"],
        "rating_imdb": 9.4,
        "style_tags": ["101空降师", "诺曼底", "友情"],
        "visual_signature": "纪实质感,欧洲战场,手持跟拍,冷色+硝烟",
        "key_scenes": ["诺曼底", "巴斯通", "最后柏林"],
        "narrative_structure": "10集线性,每集一角色",
        "cultural_impact": "HBO战争迷你剧巅峰",
        "prompt_seed": "WW2 paratrooper 101, normandy, bastogne cold, berlin, brotherhood",
        "director_view": {            "logline": "二战美军 101 空降师 E 连从诺曼底到贝希特斯加登的真实历程,10集一人称回忆",            "theme": "兄弟情 / 战争的代价 / 普通士兵的勇气",            "protagonist_arc": "E连100+士兵每人有弧光;从诺曼底(菜鸟)到贝希特斯加登(老兵);Winters 冷静领导;Speirs 冷血传奇",            "conflict_structure": "士兵vs德军(战争);士兵vs恐惧(人性);士兵vs自己(杀人后的创伤)",            "visual_palette": "二战纪录片+胶片(真实)+欧洲绿色+雪(巴斯托涅)+火光",            "lighting_approach": "HBO 真实质感(实拍+胶片)+手提+纪录片+大远景(欧洲)+战场(烟火)",            "pacing_signature": "10集 每人1-2集(准纪录片)+慢铺垫+快战斗+真实采访+结尾老兵",            "performance_direction": "非职业+真实老兵采访+Damian Lewis Winters 冷静;Ron Livingston Winters(老);E连集体群像",            "thematic_layers": "表层:战争;中层:兄弟情;深层:战争的代价(战后PTSD);象征:降落伞/钢盔/Bastogne 雪",            "philosophical_core": "We're not supermen. - 我们不是超人,只是普通人做了非凡的事",            "shot_sequence_analysis": "诺曼底空降(震撼)→卡灵顿(领导诞生)→巴斯托涅(雪+战)→市场花园(失败)→集中营(震撼)→贝希特斯加登(胜利)→老兵访谈(留白)",            "why_it_works": "①真实老兵访谈=纪实力②10集一集一人=准纪录③诺曼底空降=震撼开场④集中营=道德震撼⑤'我们不是超人'的克制",            "direct_lessons": "战争剧要真实质感(胶片+实拍);老兵访谈=真实;10集一集一人=准纪录;集中营/平民=道德;结尾'我们不是超人'克制",            "replication_template": "战争+真实老兵访谈+10集一集一人+纪录片质感+道德震撼(集中营)+克制结尾",        },
    },
    "fargo_s1": {
        "title_cn": "冰血暴S1",
        "title_en": "Fargo Season 1",
        "year_start": 2014,
        "year_end": 2014,
        "director": "Noah Hawley",
        "director_key": "coen_brothers",
        "genre": ["犯罪", "黑色喜剧"],
        "rating_imdb": 8.9,
        "style_tags": ["科恩兄弟", "雪地", "意外"],
        "visual_signature": "明尼苏达雪白,广角室内,科恩式冷幽默",
        "key_scenes": ["Lester撞车", "黑帮杀手谈判", "森林结束"],
        "narrative_structure": "日常卷入犯罪",
        "cultural_impact": "FX科恩衍生神剧",
        "prompt_seed": "minnesota snow, accidental murder, coen style, dark comedy, wood chipper",
        "director_view": {            "logline": "明尼苏达销售员 Lester 因推销员来访崩溃杀人,引来黑帮杀手 Lorne Malvo,警长 Molly 介入",            "theme": "平庸的恶 / 命运的连锁 / 北方的黑色幽默",            "protagonist_arc": "Lester 懦弱销售→杀人(压垮)→变坏(冷血);Malvo 杀手(哲学恶);Molly 警长(怀孕+正义)",            "conflict_structure": "人vs人(连锁);懦夫vs自己(变坏);正义vs恶(追凶)",            "visual_palette": "明尼苏达雪白+冷+室内暖橙+血+警徽",            "lighting_approach": "Noah Hawley 雪白+冷+室内暖+血+黑色幽默+对称",            "pacing_signature": "慢铺垫(推销员来访)→中段加速(杀人+Malvo)→结尾对决(警长vs杀手)",            "performance_direction": "Billy Bob Thornton Malvo 影史级杀手(冷哲学);Martin Freeman Lester 渐进变坏;Allison Tolman Molly 怀孕+坚持",            "thematic_layers": "表层:犯罪;中层:平庸的恶;深层:命运的连锁;象征:雪/警徽/皮草/广播",            "philosophical_core": "There's no worse tyranny than to force a man to work in a job he hates. - 工作的暴政导致杀人",            "shot_sequence_analysis": "推销员来访(压垮)=伏笔→Lester 杀人(懦弱)→Malvo 到(影史)→Molly 介入(正义)→最终对决(结局)",            "why_it_works": "①Malvo 影史级杀手(冷哲学)②'平庸的恶'主题深刻③Billy Bob Thornton 影帝表演④明尼苏达雪白+冷+黑色幽默⑤怀孕警长=反差",            "direct_lessons": "杀手要有哲学(冷);'平庸的恶'主题;地域质感(明尼苏达雪);怀孕警长=反差;黑色幽默+冷暴力",            "replication_template": "影史级杀手+平庸的恶+地域质感(雪)+怀孕警长反差+黑色幽默+连锁命运",        },
    },
    "planet_earth_ii": {
        "title_cn": "地球脉动2",
        "title_en": "Planet Earth II",
        "year_start": 2016,
        "year_end": 2016,
        "director": "David Attenborough",
        "genre": ["纪录片", "自然"],
        "rating_imdb": 9.5,
        "style_tags": ["BBC", "自然", "4K"],
        "visual_signature": "4K HDR,自然光,动物特写,慢动作,航拍",
        "key_scenes": ["鬣蜥逃生蛇", "雪豹跳崖", "城市动物"],
        "narrative_structure": "6集+岛屿/山/丛林/沙漠/草原/城市",
        "cultural_impact": "BBC纪录片巅峰",
        "prompt_seed": "bbc nature 4K, animal close up, slow motion, mountain leopard, urban wildlife",
        "director_view": {            "logline": "BBC 自然纪录片巅峰,6 集讲述岛屿/山脉/丛林/沙漠/草原/城市的野生动物",            "theme": "自然的壮美 / 物种的智慧 / 人与自然",            "protagonist_arc": "无主角,每个物种都是主角;鬣蜥/雪豹/蛇雕/虎鲸/草原象/城市狐",            "conflict_structure": "物种vs环境(生存);捕食者vs猎物(自然);人vs自然(城市集)",            "visual_palette": "4K HDR 极致(从未见过)+蓝色海洋+金色草原+雪山+城市夜晚",            "lighting_approach": "David Attenborough 4K HDR+无人机+长焦(动物不惊)+微距+长时间曝光(罕见)",            "pacing_signature": "6集 6 主题(岛/山/丛/沙/草/城)+慢铺垫+震撼瞬间(雪豹扑猎)+音乐渲染",            "performance_direction": "David Attenborough 旁白(64 岁到 90 岁 一生);真实动物(无表演);音乐(Hans Zimmer)",            "thematic_layers": "表层:自然;中层:物种智慧;深层:人也是自然一部分;象征:鬣蜥逃生/雪豹/虎鲸/城市狐",            "philosophical_core": "We are part of nature. - 人即自然一部分",            "shot_sequence_analysis": "岛屿(海鬣蜥逃生)=震撼开场→山脉(雪豹扑猎)=影史→丛林(罕见)→沙漠→草原(大象)→城市(狐)+结尾'我们也是'",            "why_it_works": "①4K HDR 视觉革命(从未见过)②雪豹扑猎+海鬣蜥逃生=影史瞬间③Attenborough 旁白=权威④Hans Zimmer 音乐=史诗⑤城市集(我们也是)结尾",            "direct_lessons": "4K HDR =视觉革命;Attenborough 旁白=权威;罕见瞬间要长焦+等待;音乐渲染史诗;城市集(我们也是)=新维度",            "replication_template": "4K HDR+6 主题分组+罕见瞬间+权威旁白+史诗音乐+城市收尾+人即自然",        },
    },
}

def get_works_by_director(director_key):
    """根据导演 key 反查作品"""
    return [w for w in WORKS_DATA.values() if w.get("director_key") == director_key]


def get_works_by_genre(genre):
    """按体裁筛选"""
    return [w for w in WORKS_DATA.values() if genre in w.get("genre", [])]


def get_top_rated(n=10, min_rating=8.5):
    """获取 Top N 高分剧"""
    return sorted(
        [w for w in WORKS_DATA.values() if w.get("rating_imdb", 0) >= min_rating],
        key=lambda x: -x.get("rating_imdb", 0)
    )[:n]



# 兼容 works_corpus 的别名和函数
def get_extended_works():
    """兼容函数 - 返回所有作品"""
    return list(WORKS_DATA.values())


def get_hot_shortform_works():
    """兼容函数 - 返回所有作品"""
    return list(WORKS_DATA.values())


def get_rich_works():
    """兼容函数 - 返回所有作品(rich 库)"""
    return list(WORKS_DATA.values())



# 别名 — 兼容旧接口
WORKS_RICH = WORKS_DATA



def _collect_all_works():
    """聚合 3 个作品库(电影 21 + 电视剧 18 + 短剧 16) + Phase A 100 部,返回 [{...work, '_src': 'movie'|'tv'|'sf'|'phase_a'}, ...]

    排序: Phase A (最新 100 部) → 电影(原 21) → 短剧(16) → 电视剧(18)
    Phase A 优先,因为它是 2018-2026 最新,最有参考价值
    """
    pool = []
    # 1. Phase A 100 部 (2018-2026 IMDB 高分电影) - 优先
    try:
        from knowledge_base.works_corpus_extended import PHASE_A_DIRECTOR_VIEWS as PA
        import re as _re
        for work_id, dv in PA.items():
            # 从 director_view 所有 14 维提取关键词(中文 2-4 字 + 英文 3-12 字符)
            all_text = " ".join(dv.values())
            cn_keywords = _re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
            en_keywords = _re.findall(r'[A-Za-z]{3,12}', all_text)
            # 加入 work_id 本身(支持 tag 直接命中),id_kw 优先
            id_kw_raw = work_id.replace("_", " ").split()
            en_from_id = _re.findall(r'[A-Za-z]{2,}', work_id)
            id_kw = list(set(id_kw_raw + en_from_id))
            keywords = list(id_kw) + list(set(cn_keywords + en_keywords) - set(id_kw))
            keywords = keywords[:30]
            pool.append({
                "title_cn": work_id.replace("_", " ").title(),
                "title_en": work_id.replace("_", " ").title(),
                "year": 2020,
                "director": "?",
                "genre": ["电影", "高分", "PhaseA"],
                "rating_imdb": 8.0,
                "style_tags": keywords + ["PhaseA"],
                "visual_signature": dv.get("visual_palette", "")[:100],
                "key_scenes": [],
                "narrative_structure": dv.get("pacing_signature", "")[:80],
                "cultural_impact": "Phase A 2018-2026 IMDB 高分",
                "prompt_seed": "",
                "director_view": dv,
                "_src": "phase_a",
            })
    except Exception:
        try:
            from works_corpus_extended import PHASE_A_DIRECTOR_VIEWS as PA
            import re as _re
            for work_id, dv in PA.items():
                all_text = " ".join(dv.values())
                cn_keywords = _re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
                en_keywords = _re.findall(r'[A-Za-z]{3,12}', all_text)
                id_kw_raw = work_id.replace("_", " ").split()
                en_from_id = _re.findall(r'[A-Za-z]{2,}', work_id)
                id_kw = list(set(id_kw_raw + en_from_id))
                keywords = list(id_kw) + list(set(cn_keywords + en_keywords) - set(id_kw))
                keywords = keywords[:30]
                id_keywords = work_id.replace("_", " ").split()
                keywords = list(set(cn_keywords + en_keywords + id_keywords))[:20]
                pool.append({
                    "title_cn": work_id.replace("_", " ").title(),
                    "title_en": work_id.replace("_", " ").title(),
                    "year": 2020,
                    "director": "?",
                    "genre": ["电影", "高分", "PhaseA"],
                    "rating_imdb": 8.0,
                    "style_tags": keywords + ["PhaseA"],
                    "visual_signature": dv.get("visual_palette", "")[:100],
                    "key_scenes": [],
                    "narrative_structure": dv.get("pacing_signature", "")[:80],
                    "cultural_impact": "Phase A 2018-2026 IMDB 高分",
                    "prompt_seed": "",
                    "director_view": dv,
                    "_src": "phase_a",
                })
        except Exception:
            pass
    # 2. 电影(works_corpus_extended) - 原有 21 部
    try:
        from knowledge_base.works_corpus_extended import WORKS_DATA as EXT_DATA
        for w in EXT_DATA.values():
            pool.append({**w, "_src": "movie"})
    except Exception:
        try:
            from works_corpus_extended import WORKS_DATA as EXT_DATA
            for w in EXT_DATA.values():
                pool.append({**w, "_src": "movie"})
        except Exception:
            pass
    # 3. 短剧(works_hot_shortform)
    try:
        from knowledge_base.works_hot_shortform import WORKS_DATA as SF_DATA
        for w in SF_DATA.values():
            pool.append({**w, "_src": "sf"})
    except Exception:
        try:
            from works_hot_shortform import WORKS_DATA as SF_DATA
            for w in SF_DATA.values():
                pool.append({**w, "_src": "sf"})
        except Exception:
            pass
    # 4. Phase B 50 部真实爆款短视频 (导演思维 14 维深写)
    try:
        from knowledge_base.works_hot_shortform import PHASE_B_DIRECTOR_VIEWS as PB
        import re as _re_pb
        for work_id, dv in PB.items():
            all_text = " ".join(dv.values())
            cn_kw = _re_pb.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
            en_kw = _re_pb.findall(r'[A-Za-z]{3,12}', all_text)
            # 把 work_id 整词 + 拆词都加进去,确保中英混合词也被搜到
            id_kw_raw = work_id.replace("_", " ").split()
            # 拆 work_id 里的英文部分(只保留 ASCII 字符)
            en_from_id = _re_pb.findall(r'[A-Za-z]{2,}', work_id)
            id_kw = list(set(id_kw_raw + en_from_id))
            # 关键词排序:id_kw 优先(确保 work_id 关键词在结果中)
            keywords = list(id_kw) + list(set(cn_kw + en_kw) - set(id_kw))
            keywords = keywords[:30]
            pool.append({
                "title_cn": work_id.replace("_", " ").title(),
                "title_en": work_id.replace("_", " ").title(),
                "year": 2024,
                "director": "?",
                "genre": ["短视频", "爆款", "PhaseB"],
                "rating_douyin": 9.0,
                "style_tags": keywords + ["PhaseB"],
                "visual_signature": dv.get("visual_palette", "")[:100],
                "key_scenes": [],
                "narrative_structure": dv.get("pacing_signature", "")[:80],
                "cultural_impact": "Phase B 真实爆款短视频",
                "prompt_seed": "",
                "director_view": dv,
                "_src": "phase_b",
            })
    except Exception:
        try:
            from works_hot_shortform import PHASE_B_DIRECTOR_VIEWS as PB
            import re as _re_pb
            for work_id, dv in PB.items():
                all_text = " ".join(dv.values())
                cn_kw = _re_pb.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
                en_kw = _re_pb.findall(r'[A-Za-z]{3,12}', all_text)
                id_kw_raw = work_id.replace("_", " ").split()
                en_from_id = _re_pb.findall(r'[A-Za-z]{2,}', work_id)
                id_kw = list(set(id_kw_raw + en_from_id))
                keywords = list(id_kw) + list(set(cn_kw + en_kw) - set(id_kw))
                keywords = keywords[:30]
                pool.append({
                    "title_cn": work_id.replace("_", " ").title(),
                    "title_en": work_id.replace("_", " ").title(),
                    "year": 2024,
                    "director": "?",
                    "genre": ["短视频", "爆款", "PhaseB"],
                    "rating_douyin": 9.0,
                    "style_tags": keywords + ["PhaseB"],
                    "visual_signature": dv.get("visual_palette", "")[:100],
                    "key_scenes": [],
                    "narrative_structure": dv.get("pacing_signature", "")[:80],
                    "cultural_impact": "Phase B 真实爆款短视频",
                    "prompt_seed": "",
                    "director_view": dv,
                    "_src": "phase_b",
                })
        except Exception:
            pass
    # 5. 电视剧(本文件) - 放最后(因为 TV 集最容易被宽泛 tag 误命中)
    for w in WORKS_DATA.values():
        pool.append({**w, "_src": "tv"})
    return pool


# 别名池(只读,内部缓存)
_ALL_WORKS_POOL = None
def _all_works():
    global _ALL_WORKS_POOL
    if _ALL_WORKS_POOL is None:
        _ALL_WORKS_POOL = _collect_all_works()
    return _ALL_WORKS_POOL


def build_rich_reference(tags=None, top_k=1):
    """根据标签生成富信息对标文本(用于注入 prompt)

    V2: 整合 3 个作品库(电影/电视剧/短剧),输出包含 director_view 5 层拆解:
    - 故事层: logline / theme / protagonist_arc / conflict_structure
    - 视觉层: visual_palette / lighting_approach
    - 节奏层: pacing_signature
    - 表演层: performance_direction
    - 主题层: thematic_layers / philosophical_core
    + 4 辅助: shot_sequence_analysis / why_it_works / direct_lessons / replication_template
    """
    if tags is None:
        tags = []
    pool = _all_works()
    selected = []
    # 按 genre/style_tags 简单匹配
    for w in pool:
        w_genre = w.get("genre", []) + w.get("style_tags", [])
        if any(t in w_genre for t in tags):
            selected.append(w)
        if len(selected) >= top_k:
            break
    if not selected and pool:
        # 优先选有 director_view 的高分作品
        with_dv = [w for w in pool if w.get("director_view")]
        if with_dv:
            with_dv.sort(key=lambda w: w.get("rating_imdb", w.get("rating_douyin", 0)), reverse=True)
            selected = with_dv[:top_k]
        else:
            selected = pool[:top_k]

    if not selected:
        return "[富信息对标] 暂无匹配作品"

    parts = ["[富信息对标 · 导演思维 5 层]"]
    for w in selected:
        title = w.get("title_cn") or w.get("title_en") or w.get("id", "?")
        director = w.get("director", "?")
        year = w.get("year", w.get("year_start", ""))
        genre = ", ".join(w.get("genre", []))
        src = w.get("_src", "tv")
        src_label = {"movie": "电影", "tv": "剧集", "sf": "短剧", "phase_a": "近期高分", "phase_b": "爆款短视频"}.get(src, "作品")
        visual = w.get("visual_signature", "")
        key_scenes = " / ".join(w.get("key_scenes", [])[:3])
        structure = w.get("narrative_structure", "")

        parts.append(f"  ▶ {title} ({year}, {director}) [{src_label} · {genre}]")
        parts.append(f"    视觉签名: {visual}")
        if key_scenes:
            parts.append(f"    代表场景: {key_scenes}")
        if structure:
            parts.append(f"    叙事结构: {structure}")
        # 故事推进节奏(兼容老接口,保留关键词)
        if w.get("plot_pattern") or w.get("narrative_structure"):
            parts.append(f"    故事推进节奏: 遵循{structure or '三幕式'}节奏,情绪曲线分层推进")

        # ===== 新增:导演思维 5 层 director_view =====
        dv = w.get("director_view")
        if dv:
            parts.append(f"    ── 导演思维拆解 ──")
            # 故事层
            if dv.get("logline"):
                parts.append(f"    故事·logline: {dv['logline']}")
            if dv.get("theme"):
                parts.append(f"    故事·主题: {dv['theme']}")
            if dv.get("protagonist_arc"):
                parts.append(f"    故事·主角弧光: {dv['protagonist_arc']}")
            if dv.get("conflict_structure"):
                parts.append(f"    故事·冲突结构: {dv['conflict_structure']}")
            # 视觉层
            if dv.get("visual_palette"):
                parts.append(f"    视觉·色彩签名: {dv['visual_palette']}")
            if dv.get("lighting_approach"):
                parts.append(f"    视觉·光影手法: {dv['lighting_approach']}")
            # 节奏层
            if dv.get("pacing_signature"):
                parts.append(f"    节奏·节奏签名: {dv['pacing_signature']}")
            # 表演层
            if dv.get("performance_direction"):
                parts.append(f"    表演·表演指导: {dv['performance_direction']}")
            # 主题层
            if dv.get("thematic_layers"):
                parts.append(f"    主题·主题层次: {dv['thematic_layers']}")
            if dv.get("philosophical_core"):
                parts.append(f"    主题·哲学内核: {dv['philosophical_core']}")
            # 4 辅助字段
            if dv.get("shot_sequence_analysis"):
                parts.append(f"    镜头序列: {dv['shot_sequence_analysis']}")
            if dv.get("why_it_works"):
                parts.append(f"    为何伟大: {dv['why_it_works']}")
            if dv.get("direct_lessons"):
                parts.append(f"    导演课: {dv['direct_lessons']}")
            if dv.get("replication_template"):
                parts.append(f"    复刻模板: {dv['replication_template']}")
    return "\n".join(parts)
