# ============================================================
# 类型片导演风格库
# 来源：IMDB Top 250 + 热门短剧 + 专业影视理论
# ============================================================

GENRE_PROFILES = {
    "suspense_thriller": {
        "cn": "悬疑/惊悚",
        "visual_language": {
            "lighting": "低调光为主、大面积阴影、冷色温(4000-5000K)、单一光源制造不安",
            "composition": "压迫构图、框中框(被困感)、大量负空间(隐藏威胁)、荷兰角(失衡)",
            "color": "冷灰+暗青+低饱和度、偶尔的红色点缀(危险信号)",
            "shot_types": "特写(恐惧表情)→远景(环境威胁)的极端切换",
        },
        "camera_techniques": [
            "缓慢推镜制造逼近感(Hitchcock技法)",
            "POV镜头让观众代入受害者",
            "固定机位长时间凝视制造不安(Kubrick风格)",
            "快速摇镜暗示未知威胁的方向",
            "景深极浅让背景模糊(未知恐惧)",
            "突然的zoom in制造jump scare",
        ],
        "pacing": {
            "rhythm": "慢→更慢→突然加速→再慢→爆发",
            "shot_duration": "长镜头积蓄→极短镜头释放",
            "tension_formula": "信息不对称+时间压力+空间压迫",
        },
        "narrative_hooks": [
            "不可靠叙述者（观众被误导）",
            "时间循环（同一事件不同视角）",
            "密室困局（物理/心理密闭空间）",
            "倒计时（外部时间压力）",
            "红鲱鱼（故意误导线索）",
        ],
        "masters": "Hitchcock, Fincher, Villeneuve, 朴赞郁, 奉俊昊",
        "reference_films": ["《七宗罪》", "《消失的爱人》", "《寄生虫》", "《看不见的客人》", "《利刃出鞘》"],
    },

    "action_combat": {
        "cn": "动作/打斗",
        "visual_language": {
            "lighting": "高对比、硬光、火焰/爆炸实景光、运动模糊",
            "composition": "对角线构图(动感)、极端角度(力量感)、人物全身(动作清晰)",
            "color": "高饱和、火焰橙红、烟雾灰蓝、金属冷光",
            "shot_types": "全身→手部特写→面部→极远景 快速切换",
        },
        "camera_techniques": [
            "手持跟拍营造临场感(Paul Greengrass)",
            "环绕慢动作(《黑客帝国》子弹时间)",
            "急速推拉制造冲击波效果",
            "仰拍+慢速呈现力量爆发",
            "剪辑加速:2-3帧一切的快节奏",
            "长镜头打斗(成龙/《老男孩》走廊)",
        ],
        "choreography_principles": [
            "动作必须有因果链(A打→B闪→B反击→A格挡)",
            "地理一致性:观众始终知道谁在哪个方位",
            "情绪节奏:打斗也有起承转合",
            "招式与角色性格匹配(暴烈vs精准vs灵巧)",
            "环境互动:利用场景道具增加变化",
            "呼吸节点:高强度打斗中留出1-2秒喘息",
        ],
        "pacing": {
            "rhythm": "蓄力(慢)→爆发(快)→顶点(慢动作)→余波(快归静)",
            "shot_duration": "打斗中0.5-2秒/镜; 对峙时3-5秒/镜",
            "impact_formula": "预备动作(抬手)→打击瞬间(帧冻结)→反应(被击者)→后果(环境破坏)",
        },
        "masters": "成龙, 袁和平, Chad Stahelski(John Wick), 吴宇森, Park Chan-wook",
        "reference_films": ["《突袭》", "《疯狂的麦克斯4》", "《卧虎藏龙》", "《一代宗师》", "《杀死比尔》"],
    },

    "war_epic": {
        "cn": "战争/史诗",
        "visual_language": {
            "lighting": "去饱和自然光、硝烟弥漫的散射光、夜晚仅火光照明",
            "composition": "极远景(战场规模)→极特写(个体痛苦)的反复切换",
            "color": "去饱和冷灰绿+血红点缀、泥土棕黄、硝烟灰白",
            "shot_types": "鸟瞰(战略)→POV(体验)→特写(情感)三层叙事",
        },
        "camera_techniques": [
            "手持长镜头沉浸式跟拍(《1917》全片长镜头风格)",
            "高速摄影捕捉爆炸碎片飞溅",
            "无人机鸟瞰展示战场规模",
            "急速晃动+音效消失(炮弹近爆效果)",
            "《拯救大兵瑞恩》D-Day: 高速快门+去饱和+手持=混乱真实",
        ],
        "emotional_architecture": [
            "个人视角锚定:在宏大战争中始终跟着一个人",
            "沉默比爆炸更有力:战后的死寂",
            "日常细节的温暖:战壕里的一封信/一张照片",
            "敌人的人性时刻:消除非黑即白",
        ],
        "pacing": {
            "rhythm": "宁静等待→混乱爆发→短暂平静(误以为安全)→再次爆发→漫长余波",
            "sound_design": "安静积蓄→震耳欲聋→突然寂静(耳鸣)→渐渐恢复",
        },
        "masters": "Spielberg, Nolan, 张艺谋(《影》), Ridley Scott, Sam Mendes",
        "reference_films": ["《拯救大兵瑞恩》", "《1917》", "《敦刻尔克》", "《现代启示录》", "《集结号》"],
    },

    "mythology_fantasy": {
        "cn": "神话/玄幻",
        "visual_language": {
            "lighting": "超自然光源(发光物体/法术光)、金色神圣光、紫色妖魅光",
            "composition": "纵深极深(天地之大)、对称(仪式感)、俯瞰(神的视角)",
            "color": "浓郁饱和色(金/紫/翠/玄)、法术特效色、天地异象色彩",
            "shot_types": "极远景(仙境全貌)→特写(灵力汇聚瞳孔)的极端对比",
        },
        "world_building_visual_cues": [
            "云雾缭绕暗示仙境/高处",
            "光柱/能量流展示力量体系",
            "天象变化反映大事件(日食/雷暴/流星)",
            "建筑比例超人类(巨大感)",
            "材质超现实(玉石城墙/水晶宫殿/浮空岛屿)",
        ],
        "camera_techniques": [
            "垂直升降穿越云层(从凡界到仙界)",
            "360度环绕法术释放瞬间",
            "超慢速捕捉粒子/能量效果",
            "广角+仰拍呈现建筑/生物的巨大感",
            "鱼眼/超广角制造异世界扭曲感",
        ],
        "masters": "Peter Jackson, 张艺谋, 徐克, 陈凯歌",
        "reference_films": ["《指环王》", "《卧虎藏龙》", "《英雄》", "《封神》", "《云渺》系列"],
    },

    "xianxia_cultivation": {
        "cn": "修真/仙侠",
        "visual_language": {
            "lighting": "仙光(白金)+妖光(紫红)+魔光(暗绿)区分阵营",
            "composition": "人物居中+背后意象(法相天地)、飘逸的衣袂线条引导视线",
            "color": "修仙者白金青+魔道黑红紫+妖族绿橙、境界越高色彩越纯净",
            "shot_types": "对峙远景→瞳孔极特写(境界突破)→法术全景(天地异象)",
        },
        "power_visualization": [
            "气(透明涟漪/空气扭曲/尘土飞扬)",
            "灵力(光流/粒子/符文环绕)",
            "破境(光柱冲天/天象突变/自然呼应)",
            "神通(大范围地形改变/法天象地)",
            "剑气(纯粹线条美学/切割一切)",
        ],
        "narrative_patterns": [
            "废柴觉醒→逆袭修炼→门派争斗→魔难考验→破境飞升",
            "每N集一次境界突破作为节奏锚点",
            "前世今生的因果循环",
            "三千大道各有不同(个性化修炼路线)",
        ],
        "masters": "徐克(蜀山), 程小东, 赵小丁",
        "reference_films": ["《云渺》系列(短剧)", "《仙剑》系列", "《诛仙》", "《蜀山》"],
    },

    "romance_sweet": {
        "cn": "言情/甜宠",
        "visual_language": {
            "lighting": "柔光为主、自然光+反光板、黄金时刻暖调、逆光发丝光",
            "composition": "双人构图(对称/互补)、浅景深虚化背景(只有彼此)、框中框(二人世界)",
            "color": "暖粉+奶白+浅金、春天色调、低对比柔和",
            "shot_types": "中近景为主(情感交流距离)、双人过肩、手部特写(触碰)",
        },
        "camera_techniques": [
            "缓慢推向两人之间缩短距离感",
            "环绕两人制造 '世界只有彼此' 的时间冻结感",
            "交叉剪辑两人思念彼此的对比画面",
            "浅景深让背景化为朦胧光斑",
            "竖屏特有:男主视角俯视女主(身高差利用)",
        ],
        "emotional_beats": [
            "初遇(意外身体接触/目光交汇)",
            "误会期(以为对方讨厌自己)",
            "心动瞬间(不经意的关心被发现)",
            "确认心意(一方先表白或意外暴露)",
            "甜蜜期(日常互动/撒糖)",
            "虐心期(必要的分离/误会)",
            "HE大团圆(克服障碍重逢)",
        ],
        "short_drama_specifics": {
            "先婚后爱": "契约婚姻→冷淡同居→日久生情→真心暴露",
            "霸总甜宠": "高冷总裁→独对女主温柔→用权势解决所有障碍",
            "反差萌": "外冷内热/外强内弱的反差制造心动",
            "盛夏芬德拉模式": "尊重型男主+独立女主+慢热+高光撒糖",
        },
        "masters": "Wong Kar-wai(花样年华), 岩井俊二, 是枝裕和(温情)",
        "reference_films": ["《花样年华》", "《情书》", "《怦然心动》", "《盛夏芬德拉》(短剧)"],
    },

    "comedy_humor": {
        "cn": "喜剧",
        "visual_language": {
            "lighting": "高调光(明亮)、均匀照明、自然感强",
            "composition": "正面平视(观众席视角)、画面工整(反差出笑点)、留出反应时间",
            "color": "饱和度偏高、温暖明亮、色彩活泼",
            "shot_types": "中景为主(肢体表演清晰)、反应shot特写(打节拍)",
        },
        "comedy_timing_camera": [
            "固定机位让演员的身体喜剧完整呈现(Chaplin/Mr.Bean)",
            "反应镜头(reaction shot)是喜剧节拍的关键——笑点=动作+反应",
            "正反打中故意延长回应时间制造尴尬笑(The Office式)",
            "突然zoom in到荒唐细节(Edgar Wright风格)",
            "快速剪辑+音效配合(每个笑点卡在cut上)",
        ],
        "humor_types_visual": {
            "slapstick": "全身景、慢动作回放、物理冲突",
            "awkward": "长时间中景固定、沉默、不舒服的距离",
            "absurd": "荒唐的画面用最正经的镜头语言呈现",
            "satire": "精确的构图对比(贫/富、大/小)",
            "dark_humor": "美丽画面+残酷内容的反差",
        },
        "masters": "Wes Anderson, Edgar Wright, 周星驰, Buster Keaton",
        "reference_films": ["《布达佩斯大饭店》", "《功夫》", "《热辣滚烫》"],
    },

    "sci_fi": {
        "cn": "科幻",
        "visual_language": {
            "lighting": "冷蓝白+霓虹点缀、屏幕光/全息光、极简人工光源",
            "composition": "几何对称(科技秩序感)、人物渺小vs巨大结构、线条引导(走廊/管道)",
            "color": "青蓝+白+黑为主、霓虹紫粉点缀、去饱和或超饱和两极",
            "shot_types": "极远景(宇宙/城市规模)→特写(人性细节)的反差",
        },
        "world_building_visual": [
            "材质暗示时代(光滑塑料=近未来/生锈金属=废土/有机=生物科技)",
            "界面设计暗示科技水平(全息/脑机接口/投影)",
            "尺度对比暗示人类位置(巨大飞船/无尽太空/微观世界)",
            "声音设计:低频嗡鸣暗示巨大机器/寂静暗示真空",
        ],
        "masters": "Kubrick, Villeneuve, Ridley Scott, 郭帆, Alex Garland",
        "reference_films": ["《银翼杀手2049》", "《2001太空漫游》", "《流浪地球》", "《星际穿越》", "《沙丘》"],
    },

    "period_costume": {
        "cn": "古装/宫廷",
        "visual_language": {
            "lighting": "烛光/灯笼的暖色实景光、月光银白、晨光金黄",
            "composition": "画框式构图(门/窗/帘)、左右对称(宫廷威严)、纵深(走廊/庭院层次)",
            "color": "暖金+深红+墨绿(宫廷); 水墨淡雅(文人); 浓艳(妖/魅)",
            "shot_types": "远景(宫殿气派)→面部特写(权谋心机)的对比",
        },
        "period_specific_techniques": [
            "服饰色彩暗示身份等级(黄=帝/紫=贵/白=素/红=喜)",
            "建筑透视体现权力层级(越高越远=越难接近)",
            "季节变化标记时间流逝(落叶/飞雪/花开)",
            "礼仪动作展示文化(跪拜/拱手/甩袖)",
            "书法/绘画入画面增加文化厚度",
        ],
        "masters": "张艺谋, 李安, 陈凯歌, 侯孝贤, 王家卫(东邪西毒)",
        "reference_films": ["《英雄》", "《满城尽带黄金甲》", "《卧虎藏龙》", "《冒姓琅琊》(短剧)"],
    },

    "horror": {
        "cn": "恐怖",
        "visual_language": {
            "lighting": "极低调光、单点光源(手电/蜡烛)、底光(脸部扭曲)、闪烁不稳定光",
            "composition": "大量负空间(恐惧填充)、画面边缘的暗示、正面凝视(打破第四面墙)",
            "color": "深蓝黑+冷白+血红点缀、去饱和至接近黑白",
            "shot_types": "固定远景(等待恐惧出现)→jump scare特写的节奏",
        },
        "fear_techniques": [
            "看不到比看到更可怕:画面外的声音/影子的边缘",
            "长时间固定镜头让观众自己寻找恐怖元素",
            "安静积蓄→突然的声音/画面冲击",
            "慢速推向黑暗深处(观众不想看但无法移开目光)",
            "镜子/反射/对称中的异常(某处不对称)",
            "儿童/日常物品的恐怖化(脱离语境的熟悉事物)",
        ],
        "masters": "Ari Aster, Jordan Peele, James Wan, 中田秀夫, 清水崇",
        "reference_films": ["《闪灵》", "《遗传厄运》", "《午夜凶铃》", "《寂静之地》"],
    },

    "urban_modern": {
        "cn": "都市/现代",
        "visual_language": {
            "lighting": "霓虹混合光、屏幕光映脸、办公室荧光灯、车灯流光",
            "composition": "线条几何(建筑/玻璃)、人群中的孤立个体、上下分割(天际线/地面)",
            "color": "冷灰蓝+霓虹暖色点缀、白天去饱和/夜晚高饱和",
            "shot_types": "中景对话(日常)→特写情绪(内心)→远景城市(渺小)",
        },
        "modern_life_visual_cues": [
            "手机屏幕光映在脸上(现代孤独标志)",
            "玻璃反射中的双重自我(内外冲突)",
            "电梯/地铁的密闭空间(都市压迫)",
            "高楼俯瞰vs街道仰望(阶层对比)",
            "外卖/打车/加班等现代生活符号",
        ],
        "reference_films": ["《寄生虫》", "《社交网络》", "《迷失东京》", "《重庆森林》"],
    },

    "pastoral_idyllic": {
        "cn": "田园/文艺",
        "visual_language": {
            "lighting": "自然光为主、黄金时刻、dappled光(树叶间光斑)、柔和均匀",
            "composition": "大量留白(呼吸感)、自然线条(河流/山脊)、人与自然融合",
            "color": "低饱和暖绿+麦黄+天蓝+白、四季色彩变化",
            "shot_types": "远景(自然全貌)→中景(日常生活)→特写(自然细节/手工)",
        },
        "atmospheric_elements": [
            "风吹动的草/树/布料(生命感)",
            "水面倒影(宁静/内省)",
            "炊烟/雾气(人间烟火/晨间诗意)",
            "四季标记(花开/萤火/红叶/初雪)",
            "手工劳动的特写(编织/耕种/料理)",
        ],
        "masters": "是枝裕和, Terrence Malick, 侯孝贤, 李子柒(视频)",
        "reference_films": ["《小森林》", "《天堂的日子》", "《悲情城市》", "《家里家外》(短剧)"],
    },

    # ========================================================
    # 新增类型(2026扩充)
    # ========================================================
    "time_travel": {
        "cn": "穿越/时空旅行",
        "visual_language": {
            "lighting": "时代差异化布光(古代暖烛光vs现代冷白光)、白闪/白场作为穿越媒介",
            "composition": "匹配构图(同一空间不同时代的对比)、镜像/水面的穿越门",
            "color": "古代暖金/水墨 vs 现代冷蓝/去饱和,时代色温差异即叙事",
            "shot_types": "极特写(穿越瞬间瞳孔)→匹配远景(时代对比)",
        },
        "time_markers": [
            "服饰变化标记时代(古装→现代/反之)",
            "建筑/工具/科技水平差异(马车vs汽车)",
            "语言/称谓/礼仪的时代特征",
            "自然元素的季节/天象变化",
            "文字载体(竹简→纸张→手机)",
        ],
        "narrative_techniques": [
            "蝴蝶效应可视化(一个动作→历史改变的连锁)",
            "上帝视角(穿越者知道未来)的悬念",
            "时代身份错位的喜剧/悲剧行为",
            "固定锚点(某物件/某人跨越时代存在)",
        ],
        "masters": "Nolan, 今敏, Robert Zemeckis, 张大碗(穿越短剧)",
        "reference_films": ["《星际穿越》", "《信条》", "《回到未来》", "《你的名字。》"],
    },

    "cyberpunk": {
        "cn": "赛博朋克",
        "visual_language": {
            "lighting": "霓虹为主光(紫/粉/青/红)、雨夜反射、全息屏幕光映脸、底部投光",
            "composition": "垂直巨型城市(上流vs底层)、霓虹倒影的湿润地面、广告牌满构图",
            "color": "高饱和霓虹(紫粉青红)+深黑阴影、去肉色肤色(蓝绿调色)",
            "shot_types": "广角扭曲的拥挤城市→长焦偷窥主角→特写义体/接口",
        },
        "world_building_visual": [
            "巨型企业logo垄断天际线",
            "义体/接口/植入物的金属与肉体混合",
            "全息广告/AR界面叠加现实",
            "雨/雾/蒸汽让光可见(空气有质感)",
            "底层拥挤潮湿vs上层洁净空旷的垂直阶级",
        ],
        "masters": "Ridley Scott, Michael Mann, 今敏, 大友克洋",
        "reference_films": ["《银翼杀手》", "《银翼杀手2049》", "《攻壳机动队》", "《阿基拉》"],
    },

    "wuxia_martial_arts": {
        "cn": "武侠/功夫(写实向)",
        "visual_language": {
            "lighting": "自然光+实景光(灯笼/月光)、竹林/水面漫射柔光、高对比剪影",
            "composition": "对角线动势、留白的意境构图、人物与山水的比例(宗师气度)",
            "color": "水墨淡雅(文人武侠)或浓艳红金(类型武侠)、四季意境色彩",
            "shot_types": "全身动作清晰→手部/眼神极特写→远景意境的交替",
        },
        "choreography_principles": [
            "一招一式有交代(预备→发力→收势)",
            "动作与角色境界匹配(初学笨拙vs宗师飘逸)",
            "环境互动(借竹/借水/借桌椅)",
            "停顿即句读(动作间的呼吸)",
            "速度变化:常速→慢动作顶点→常速收招",
        ],
        "masters": "徐克, 袁和平, 王家卫(一代宗师), 李安(卧虎藏龙)",
        "reference_films": ["《一代宗师》", "《卧虎藏龙》", "《叶问》", "《黄飞鸿》系列"],
    },

    "psychological": {
        "cn": "心理/意识流",
        "visual_language": {
            "lighting": "主观化的非自然光(色温随心理变)、闪烁不稳、镜子中不同光",
            "composition": "镜面/反射的分裂构图、对称中的不对称异常、空间扭曲",
            "color": "心理色(抑郁灰/躁动红/恐惧青)、现实与幻觉的色调切换",
            "shot_types": "面部极特写(精神状态)→主观POV(扭曲视角)→超现实段落",
        },
        "techniques": [
            "不可靠叙述者的视觉暗示(画面与旁白矛盾)",
            "梦境/幻觉/回忆与现实的无缝切换(今敏式匹配剪辑)",
            "镜子/玻璃/水中的'另一个自己'",
            "时间错乱(钟表反向/重复同一时刻)",
            "物品/人的非逻辑出现(心理投射)",
            "焦距/景深的主观变化(清醒vs混乱)",
        ],
        "masters": "今敏, Bergman, Darren Aronofsky, Polanski, Fincher",
        "reference_films": ["《未麻的部屋》", "《搏击俱乐部》", "《黑天鹅》", "《禁闭岛》"],
    },

    "documentary_style": {
        "cn": "纪实/伪纪录片",
        "visual_language": {
            "lighting": "纯实景动机光、不补光、自然光变化(黄金时刻/阴天)",
            "composition": "不工整的纪实构图、主体偏离中心、画面边缘被裁切",
            "color": "未调色的真实色彩、或去饱和处理、低对比纪实质感",
            "shot_types": "手持跟拍为主、长焦偷拍感、偶尔zoom(发现感)",
        },
        "techniques": [
            "手持晃动制造在场感(Paul Greengrass)",
            "zoom in发现关键(新闻感)",
            "角色直视镜头/打破第四面墙(伪纪录片)",
            "完整保留动作与对话(不切)",
            "现场收音/环境音为主(非配音)",
            "improv即兴表演的真实感",
        ],
        "masters": "Paul Greengrass, Fernando Meirelles, Alfonso Cuarón(罗马), 柯文斯基",
        "reference_films": ["《科洛弗档案》", "《上帝之城》", "《女巫布莱尔》", "《办公室》"],
    },

    "noir": {
        "cn": "黑色电影/新黑色",
        "visual_language": {
            "lighting": "低调高对比、百叶窗切割面部、单点光源+大面积黑、底光偶尔",
            "composition": "框中框(被困)、倾斜荷兰角、阴影占据画面主体",
            "color": "黑白经典或冷蓝去饱和(新黑色)、霓虹点缀(赛博黑色)",
            "shot_types": "长焦偷窥感→面部明暗切割特写→阴雨湿街远景",
        },
        "themes_visuals": [
            "雨夜湿街的霓虹倒影",
            "百叶窗/栏杆的光影切割",
            "蛇蝎美人(femme fatale)的冷艳特写",
            "侦探VO旁白驱动的意识流",
            "迷宫般的城市空间(道德迷宫)",
        ],
        "masters": "Billy Wilder, Polanski, Coen Brothers, Fincher",
        "reference_films": ["《双重赔偿》", "《唐人街》", "《冰血暴》", "《七宗罪》"],
    },

    "musical": {
        "cn": "歌舞/音乐",
        "visual_language": {
            "lighting": "舞台化高饱和色彩、聚光灯、剧场光、歌舞段落的梦幻打光",
            "composition": "对称舞台构图、群舞的几何图案、双人舞的环绕调度",
            "color": "高饱和+情感化色块(欢快暖/忧郁冷)、段落色彩区分",
            "shot_types": "全身(舞蹈完整)→面部(情绪)→快切节拍",
        },
        "techniques": [
            "节拍器剪辑(每个cut卡在音乐节拍)",
            "长镜头跟拍走入歌舞场景(无缝进入)",
            "梦境段落与现实切换(音乐起=进入歌舞世界)",
            "群舞的精确几何调度(俯拍图案)",
            "速度变化:常速→慢动作顶点→常速(音乐高潮)",
        ],
        "masters": "Damien Chazelle, Gene Kelly, Busby Berkeley",
        "reference_films": ["《爱乐之城》", "《爆裂鼓手》", "《雨中曲》", "《芝加哥》"],
    },

    "survival": {
        "cn": "生存/求生",
        "visual_language": {
            "lighting": "极端自然光(暴风雪白/丛林绿/沙漠金)、火光为唯一夜晚光源",
            "composition": "人物渺小vs自然巨大的远景、孤立无援的负空间",
            "color": "去饱和的严酷色调、单色极端环境(白雪/黄沙/绿林)",
            "shot_types": "广角环境远景→面部特写(痛苦/坚毅)→POV(发现)",
        },
        "techniques": [
            "手持跟拍代入求生体验",
            "自然元素的拟人化敌意(风/水/野兽)",
            "极简叙事+极致身体性(受伤/饥饿/寒冷的可视化)",
            "长焦压缩孤独感、广角展现环境恐怖",
            "声音设计:呼吸/心跳/环境音代替配乐",
        ],
        "masters": "Alejandro Iñárritu, Alfonso Cuarón, Ridley Scott",
        "reference_films": ["《荒野猎人》", "《火星救援》", "《人类之子》", "《127小时》"],
    },

    "family_warmth": {
        "cn": "家庭温情",
        "visual_language": {
            "lighting": "暖色实景光(厨房/餐桌)、晨光/夕阳的柔和暖调、灯笼/烛光",
            "composition": "餐桌群像、低机位孩子视角、留白的日常呼吸",
            "color": "暖黄+柔绿+米白、低对比柔和、四季渐变",
            "shot_types": "中景日常→特写食物/手/表情→远景家的全貌",
        },
        "techniques": [
            "餐桌戏的群像调度(家庭权力微观)",
            "食物特写的温度(生活质感)",
            "季节标记时间流逝(花开/落叶/初雪)",
            "低机位代入孩子/老人视角",
            "固定长镜头让日常自然流淌(小津)",
            "代际构图的并置(老人与孩子同框)",
        ],
        "masters": "是枝裕和, 小津安二郎, 李安, 杨德昌",
        "reference_films": ["《小偷家族》", "《东京物语》", "《饮食男女》", "《一一》"],
    },

    "revenge": {
        "cn": "复仇",
        "visual_language": {
            "lighting": "低调暗调为主、复仇时刻的极端对比、受害者回忆的暖vs现实的冷",
            "composition": "对称对峙构图、垂直权力关系(俯仰)、框中框的困局",
            "color": "冷青/暗红/去饱和、复仇释放瞬间的红色渗入",
            "shot_types": "面部极特写(恨意)→对峙远景→暴力长镜头",
        },
        "techniques": [
            "复仇计划的视觉化(目标/路径/时机的蒙太奇)",
            "受害者与施害者的镜像构图(相似构图反差处境)",
            "延迟满足(铺垫越久释放越爽)",
            "暴力美学的长镜头(不切,逼观众直视)",
            "复仇完成后的空虚(慢拉/空镜/沉默)",
        ],
        "masters": "朴赞郁, Tarantino, Sergio Leone, Chan-wook",
        "reference_films": ["《老男孩》", "《杀死比尔》", "《西部往事》", "《复仇者之死》"],
    },
}


# ============================================================
# 类型片决策覆盖层 — 为每个类型补7维决策字段
# (保留原visual_language/camera_techniques/pacing, 叠加trigger/failure/measurement等)
# ============================================================
GENRE_DECISION = {
    "suspense_thriller": {
        "trigger": "悬疑/惊悚/心理恐怖/不可靠叙述/密室困局",
        "rationale": "悬疑≠惊吓。让观众知道桌下炸弹(悬念)比突然爆炸(惊吓)更有力。信息不对称是核心张力。",
        "failure_modes": ["靠jump scare而非悬念=廉价恐怖", "信息过早揭示=失悬念", "红鲱鱼过多=观众放弃", "密室无逻辑=失真"],
        "measurement": "观众应持续感到不安+对真相的好奇, 而非被吓一跳",
        "alternatives": ["horror(更恐怖少推理)", "noir(更黑色少悬念)"],
        "cross_refs": {"structure": "mystery_reveal", "director": "Hitchcock/Fincher/朴赞郁", "pacing": "慢→更慢→突然加速"},
    },
    "action_combat": {
        "trigger": "动作/打斗/追逐/爆炸/英雄战斗",
        "rationale": "动作戏=蓄力→爆发→顶点→余波的循环。地理一致性让观众始终知道谁在哪, 招式与角色性格匹配。",
        "failure_modes": ["剪辑过快看不清动作=shaky cam", "地理混乱=观众不知道谁在哪", "动作无情绪节奏=纯暴力", "无呼吸节点=疲劳"],
        "measurement": "动作清晰可辨+地理一致+情绪节奏+呼吸节点",
        "alternatives": ["wuxia_martial_arts(更飘逸武侠)", "war_epic(更规模战争)"],
        "cross_refs": {"structure": "save_the_cat", "director": "George Miller/吴宇森/成龙", "pacing": "蓄力→爆发→顶点→余波"},
    },
    "war_epic": {
        "trigger": "战争/史诗/历史宏大/个体在宏大战争中的命运",
        "rationale": "战争片=个人视角锚定+沉默比爆炸有力+日常细节的温暖。在宏大战争中始终跟着一个人。",
        "failure_modes": ["无个体锚定=纯战争机器", "爆炸过多=失沉默力量", "敌人去人性化=非黑即白", "无日常温暖=失人性"],
        "measurement": "有个人视角锚定+沉默留白+敌人人性时刻+日常细节",
        "alternatives": ["action_combat(更动作少史诗)", "survival(更个体少战争)"],
        "cross_refs": {"structure": "parallel_convergence", "director": "Spielberg/Nolan/雷德利·斯科特", "sound": "安静积蓄→震耳→寂静(耳鸣)"},
    },
    "mythology_fantasy": {
        "trigger": "神话/玄幻/奇幻/超自然世界/英雄史诗",
        "rationale": "奇幻=世界观建立+超自然光源+尺度对比。仙境全貌→灵力特写的极端对比, 天象变化反映大事件。",
        "failure_modes": ["世界观无逻辑=失信", "特效炫技无叙事=空洞", "尺度无对比=失神性", "材质超现实无细节=失真实"],
        "measurement": "世界观自洽+超自然光+尺度对比+材质细节",
        "alternatives": ["xianxia_cultivation(更修真)", "sci_fi(更科技)"],
        "cross_refs": {"structure": "hero_journey", "director": "Peter Jackson/张艺谋/徐克", "color": "金紫翠玄浓郁"},
    },
    "xianxia_cultivation": {
        "trigger": "修真/仙侠/境界突破/法术/前世今生",
        "rationale": "修真=境界可视化(气/灵力/破境/神通/剑气)+阵营色彩(仙光/妖光/魔光)。每N集一次境界突破作节奏锚点。",
        "failure_modes": ["境界无可视化=失爽感", "法术特效廉价=失仙气", "前世今生无回收=悬置", "色彩阵营混乱=失逻辑"],
        "measurement": "境界有可视化层次+法术有美学+前世今生有回收+色彩阵营清晰",
        "alternatives": ["wuxia_martial_arts(更写实武侠)", "mythology_fantasy(更神话)"],
        "cross_refs": {"structure": "hero_journey/buildup_payoff", "director": "徐克/张艺谋", "color": "仙白金青/魔黑红紫/妖绿橙"},
    },
    "romance_sweet": {
        "trigger": "言情/甜宠/爱情/都市情感/甜虐交替",
        "rationale": "甜宠=甜度递进不重复+反差萌+虐甜交替。每次甜必须比上次更进一步, 虐是甜的对照。",
        "failure_modes": ["甜度原地踏步=失糖", "虐无理由=为虐而虐", "反差萌无建立=突兀", "HE无障碍=廉价"],
        "measurement": "甜度递进+反差萌建立+虐甜交替+HE有障碍",
        "alternatives": ["family_warmth(更家庭)", "urban_modern(更都市)"],
        "cross_refs": {"structure": "emotional_rollercoaster/kishōtenketsu", "director": "王家卫/岩井俊二", "pacing": "甜度递升+虐甜交替"},
    },
    "comedy_humor": {
        "trigger": "喜剧/幽默/讽刺/荒诞/身体喜剧",
        "rationale": "喜剧=反应镜是节拍关键+笑点卡帧精确+固定机位让肢体喜剧完整。笑点=动作+反应。",
        "failure_modes": ["笑点不卡帧=死(差一帧)", "无反应镜=失节拍", "肢体喜剧切碎=失完整", "讽刺无温度=冷酷"],
        "measurement": "笑点卡帧精确+反应镜到位+肢体喜剧完整+讽刺有温度",
        "alternatives": ["noir(黑色幽默)", "satire(更讽刺)"],
        "cross_refs": {"structure": "save_the_cat/kishōtenketsu", "director": "Wes Anderson/卓别林/周星驰", "pacing": "笑点卡帧"},
    },
    "sci_fi": {
        "trigger": "科幻/未来/太空/科技/异星/赛博",
        "rationale": "科幻=材质暗示时代+界面暗示科技+尺度对比+声音设计(低频嗡鸣/真空寂静)。世界观真实感>情节。",
        "failure_modes": ["世界观无逻辑=失实感", "科技无限制=失悬念", "尺度无对比=失渺小", "解释过多=失奇观"],
        "measurement": "世界观自洽+材质/界面/尺度暗示+声音设计+奇观不解释",
        "alternatives": ["cyberpunk(更赛博)", "mythology_fantasy(更神话)"],
        "cross_refs": {"structure": "hero_journey/nonlinear", "director": "Villeneuve/Kubrick/雷德利·斯科特", "sound": "低频嗡鸣/真空寂静"},
    },
    "period_costume": {
        "trigger": "古装/宫廷/历史/时代剧/权谋",
        "rationale": "古装=服饰色彩暗示身份等级+建筑透视体现权力+季节变化标记时间+礼仪动作展示文化。烛光/月光/晨光是核心光源。",
        "failure_modes": ["服饰无等级逻辑=失实", "建筑透视无权力=失层次", "礼仪无文化=失真", "光源不合理=穿帮"],
        "measurement": "服饰有等级+建筑有权力层次+礼仪有文化+光源合理",
        "alternatives": ["wuxia_martial_arts(更武侠)", "family_warmth(更家庭)"],
        "cross_refs": {"structure": "classic_three_act/kishōtenketsu", "director": "张艺谋/李安/陈凯歌", "lighting": "烛光/月光/晨光"},
    },
    "horror": {
        "trigger": "恐怖/惊吓/超自然/心理恐怖/民俗恐怖",
        "rationale": "恐怖=看不到比看到更可怕+安静积蓄→突然冲击+最恐怖处反而安静。日常物品的恐怖化是核心。",
        "failure_modes": ["靠jump scare=廉价", "恐怖过多=脱敏", "最恐怖处不安静=失力量", "无日常锚点=失代入"],
        "measurement": "看不到>看到+安静积蓄+最恐怖处安静+日常恐怖化",
        "alternatives": ["suspense_thriller(更悬疑少惊吓)", "psychological(更心理)"],
        "cross_refs": {"structure": "descent_redemption", "director": "Ari Aster/Jordan Peele/中田秀夫", "sound": "安静积蓄→突然冲击→寂静(耳鸣)"},
    },
    "urban_modern": {
        "trigger": "都市/现代/当代/职场/都市孤独",
        "rationale": "都市=霓虹混合光+屏幕光映脸+玻璃反射双重自我+垂直阶级(高楼vs街道)。现代生活符号(手机/电梯/地铁)。",
        "failure_modes": ["都市符号堆砌=炫技", "无孤独内核=失都市感", "色彩无阶层=失层次", "屏幕光滥用=失真实"],
        "measurement": "霓虹混合光+玻璃反射+垂直阶级+现代符号+孤独内核",
        "alternatives": ["cyberpunk(更赛博)", "noir(更黑色)"],
        "cross_refs": {"structure": "kishōtenketsu/emotional_rollercoaster", "director": "王家卫/奉俊昊/Michael Mann", "color": "冷灰蓝+霓虹暖点缀"},
    },
    "pastoral_idyllic": {
        "trigger": "田园/文艺/自然/日常/小森林式治愈",
        "rationale": "田园=自然光+大量留白+四季标记+手工劳动特写+风吹动的生命感。日常琐事中有最深的诗意。",
        "failure_modes": ["无自然元素=失田园", "留白无主体=空洞", "四季无标记=失时间", "手工无细节=失温度"],
        "measurement": "自然光+留白有主体+四季标记+手工细节+生命感",
        "alternatives": ["family_warmth(更家庭)", "romance_sweet(更爱情)"],
        "cross_refs": {"structure": "kishōtenketsu", "director": "是枝裕和/Malick/侯孝贤", "sound": "风声/水声/虫鸣"},
    },
    "time_travel": {
        "trigger": "穿越/时空旅行/平行时间线/重生带着记忆",
        "rationale": "穿越=时代差异化布光+匹配构图对比+穿越者上帝视角的悬念+蝴蝶效应可视化。时代色温差异即叙事。",
        "failure_modes": ["时代无差异=失穿越感", "蝴蝶效应无逻辑=失真", "穿越者无上帝视角=失爽", "时代身份错位无喜/悲=浪费"],
        "measurement": "时代差异清晰+蝴蝶效应有逻辑+上帝视角+身份错位有戏",
        "alternatives": ["nonlinear(更碎片时间)", "sci_fi(更科技)"],
        "cross_refs": {"structure": "nonlinear/in_medias_res", "director": "Nolan/今敏/Zemeckis", "color": "时代色温差异"},
    },
    "cyberpunk": {
        "trigger": "赛博朋克/霓虹雨夜/巨型企业/义体/赛博黑色",
        "rationale": "赛博=霓虹为主光(紫粉青红)+雨夜反射+全息屏幕光+垂直阶级(底层潮湿vs上层洁净)。空气有质感(雨/雾/蒸汽)。",
        "failure_modes": ["霓虹过杂=混乱", "肤色染绿紫=失真", "无垂直阶级=失社会感", "雨夜滥用=廉价赛博"],
        "measurement": "霓虹有主色+肤色可辨+垂直阶级+空气质感+赛博社会感",
        "alternatives": ["sci_fi(更广义科幻)", "urban_modern(更都市)"],
        "cross_refs": {"structure": "descent_redemption/mystery_reveal", "director": "雷德利·斯科特/Michael Mann/今敏", "color": "紫粉青红霓虹+深黑"},
    },
    "wuxia_martial_arts": {
        "trigger": "武侠/功夫/写实向武术/宗师/江湖",
        "rationale": "武侠=一招一式有交代+动作与境界匹配+环境互动+停顿即句读+速度变化(常速→慢放顶点→常速收招)。意境>情节。",
        "failure_modes": ["动作无交代=shaky cam", "境界无匹配=失宗师", "无环境互动=失变化", "无停顿句读=失节奏"],
        "measurement": "动作有交代+境界匹配+环境互动+停顿句读+速度变化",
        "alternatives": ["action_combat(更爆裂)", "xianxia_cultivation(更修真)"],
        "cross_refs": {"structure": "hero_journey", "director": "徐克/袁和平/王家卫(一代宗师)", "color": "水墨淡雅或浓艳红金"},
    },
    "psychological": {
        "trigger": "心理/意识流/不可靠叙述/精神崩塌/幻觉",
        "rationale": "心理=主观化非自然光+镜面分裂构图+梦境与现实无缝切换(今敏式)+时间错乱。现实与虚构无边界。",
        "failure_modes": ["幻觉无逻辑=混乱", "不可靠叙述无暗示=欺瞒", "镜面滥用=炫技", "时间错乱无标记=迷失"],
        "measurement": "幻觉有逻辑+不可靠叙述有暗示+镜面有理由+时间错乱有标记",
        "alternatives": ["horror(更恐怖)", "suspense_thriller(更悬疑)"],
        "cross_refs": {"structure": "nonlinear/mystery_reveal", "director": "今敏/Bergman/Aronofsky/Polanski", "editing": "梦境现实匹配剪辑"},
    },
    "documentary_style": {
        "trigger": "纪实/伪纪录片/找到影像/伪纪录片(mockumentary)/真实感",
        "rationale": "纪实=纯实景动机光+不工整构图+手持晃动+完整保留动作+现场收音。真实感>制作精良。",
        "failure_modes": ["手持晃过大=晕", "构图过工整=失纪实", "剪辑切碎=失完整", "配音替代现场声=失真"],
        "measurement": "实景动机光+不工整构图+手持有度+动作完整+现场声",
        "alternatives": ["urban_modern(更都市但有风格)", "pastoral_idyllic(更田园纪实)"],
        "cross_refs": {"structure": "kishōtenketsu/parallel_convergence", "director": "Paul Greengrass/Meirelles/Cuarón", "sound": "现场收音+环境音"},
    },
    "noir": {
        "trigger": "黑色电影/新黑色/蛇蝎美人/道德迷宫/雨夜湿街",
        "rationale": "黑色=低调高对比+百叶窗切割面部+长焦偷窥+VO旁白驱动+迷宫城市。道德灰色地带是核心。",
        "failure_modes": ["低调无层次=死黑", "蛇蝎美人无魅力=失核心", "VO过多=说教", "迷宫无隐喻=失道德深度"],
        "measurement": "低调有层次+蛇蝎美人有魅力+VO有节制+迷宫有隐喻",
        "alternatives": ["suspense_thriller(更悬疑)", "cyberpunk(更赛博)"],
        "cross_refs": {"structure": "mystery_reveal/descent_redemption", "director": "Billy Wilder/Polanski/Coen", "lighting": "chiaroscuro+百叶窗"},
    },
    "musical": {
        "trigger": "歌舞/音乐/舞台化/梦幻段落/音乐驱动",
        "rationale": "歌舞=节拍器剪辑+长镜头走入歌舞+梦境段落切换+群舞几何调度+速度变化。音乐起=进入歌舞世界。",
        "failure_modes": ["节拍不卡=失律动", "歌舞无梦境切换=失魔力", "群舞无几何=失美感", "速度无变化=失高潮"],
        "measurement": "节拍卡帧+梦境切换+群舞几何+速度变化",
        "alternatives": ["comedy_humor(更喜剧)", "romance_sweet(更爱情)"],
        "cross_refs": {"structure": "classic_three_act/kishōtenketsu", "director": "Chazelle/Gene Kelly", "sound": "音乐驱动+节拍器剪辑"},
    },
    "survival": {
        "trigger": "生存/求生/个体vs自然/荒野/末世求生",
        "rationale": "生存=极端自然光+人物渺小vs自然巨大+极简叙事+身体性(受伤/饥饿/寒冷可视化)+呼吸/心跳代替配乐。",
        "failure_modes": ["无身体性=失求生感", "自然无拟人化=失敌意", "叙事过多=失极简", "配乐过多=失孤立"],
        "measurement": "极端自然光+渺小vs巨大+身体性+自然敌意+声音代替配乐",
        "alternatives": ["war_epic(更战争)", "action_combat(更动作)"],
        "cross_refs": {"structure": "classic_three_act/hero_journey", "director": "Iñárritu/Cuarón/雷德利·斯科特", "sound": "呼吸/心跳/环境音"},
    },
    "family_warmth": {
        "trigger": "家庭/温情/代际/餐桌戏/日常家庭",
        "rationale": "家庭=暖色实景光+餐桌群像(权力微观)+食物特写温度+低机位孩子视角+季节标记时间。无常即常。",
        "failure_modes": ["无餐桌群像=失家庭微观", "食物无特写=失温度", "无代际构图=失代际", "戏剧化过度=失日常"],
        "measurement": "暖色实景光+餐桌群像+食物特写+代际构图+日常感",
        "alternatives": ["pastoral_idyllic(更田园)", "romance_sweet(更爱情)"],
        "cross_refs": {"structure": "kishōtenketsu/descent_redemption", "director": "是枝裕和/小津/李安", "lighting": "暖色实景光"},
    },
    "revenge": {
        "trigger": "复仇/系统化复仇/延迟满足+密集释放/复仇美学",
        "rationale": "复仇=受害者与施害者镜像构图+延迟满足(铺垫越久释放越爽)+暴力美学长镜头+复仇完成后的空虚。让观众同情施暴者=最大冲击。",
        "failure_modes": ["复仇无延迟=失爽感", "暴力无美学=失质感", "复仇完成无空虚=失主题", "施害者无人性=失道德冲击"],
        "measurement": "镜像构图+延迟满足+暴力美学+完成空虚+施害者人性",
        "alternatives": ["action_combat(更动作)", "noir(更黑色)"],
        "cross_refs": {"structure": "buildup_payoff/descent_redemption", "director": "朴赞郁/Tarantino/Leone", "pacing": "延迟满足+密集释放"},
    },
}


def get_genre_with_decision(genre_key):
    """合并类型片基础信息 + 决策覆盖层(引擎调用)"""
    base = GENRE_PROFILES.get(genre_key, {})
    decision = GENRE_DECISION.get(genre_key, {})
    merged = dict(base)
    merged.update(decision)
    return merged

