# -*- coding: utf-8 -*-
# ============================================================
# 细分风格深度知识库 V1.0
# 补全 genre_profiles 未深的细分风格: 蒸汽朋克/末日废土/民国/校园/职场/赛博黑色/
# 仙侠细分/武侠细分/谍战/律政/医疗/美食/运动/音乐MV 等, 7维决策树
# ============================================================

STYLE_SUBDIVISIONS = {
    # ─── 时代/风格细分 ───
    "steampunk": {
        "cn": "蒸汽朋克",
        "trigger": "维多利亚蒸汽时代/齿轮机械/黄铜质感/复古未来/工业革命美学",
        "rationale": "蒸汽朋克=维多利亚美学+齿轮机械+黄铜+蒸汽, 是'复古的未来'——用旧技术想象新世界, 机械可见即美感。",
        "execution": {
            "palette": "黄铜金+深棕+暗红+煤烟灰, 金属氧化绿",
            "texture": "齿轮/铆钉/蒸汽/铜锈/皮革, 机械外露",
            "lighting": "煤气灯暖黄+蒸汽朦胧+工厂硬光",
            "prop": "齿轮机械/蒸汽飞艇/黄铜护目镜/发条装置",
        },
        "failure_modes": ["机械元素堆砌无叙事=炫技", "色调过暗=失黄铜质感", "无维多利亚服饰=失时代感", "蒸汽滥用=失真实"],
        "measurement": "黄铜齿轮机械美学+维多利亚时代+蒸汽朦胧, 复古未来感达成",
        "alternatives": ["cyberpunk(更数字未来)", "sci_fi(更现代)"],
        "cross_refs": {"genre": "科幻/冒险", "period": "维多利亚", "color": "黄铜金+棕", "masters": "《天空上尉柯罗伊》, 《雨果》"},
    },
    "post_apocalypse": {
        "cn": "末日废土",
        "trigger": "文明毁灭后/资源匮乏/人vs废墟/生存法则/末世公路",
        "rationale": "废土=文明废墟+资源稀缺+人性考验。废墟是叙事材料, 稀缺驱动冲突, 人性在极限暴露。",
        "execution": {
            "palette": "去饱和黄沙+锈红+灰+偶尔绿(生机), 沙尘漫天",
            "texture": "废墟/锈蚀/破败/拼装武器/防毒面具",
            "lighting": "烈日硬光+沙尘散射+篝火夜景",
            "prop": "拼装载具/防毒面具/水壶/破旧武器",
        },
        "failure_modes": ["废墟无叙事=空景堆砌", "资源不稀缺=失生存张力", "人性不极限=失废土内核", "色调无去饱和=失荒凉"],
        "measurement": "废墟叙事+资源稀缺+人性极限+去饱和荒凉, 废土感达成",
        "alternatives": ["survival(更个体)", "war_epic(更战争)"],
        "cross_refs": {"genre": "末世/生存", "color": "去饱和黄沙", "masters": "《疯狂的麦克斯》系列, 《辐射》"},
    },
    "republic_era": {
        "cn": "民国风",
        "trigger": "民国时期/旧上海/新旧交替/乱世儿女/旗袍洋装",
        "rationale": "民国=新旧交替的时代, 旗袍洋装+洋房弄堂+战乱背景, 是东方与西方、传统与现代的碰撞期。",
        "execution": {
            "palette": "暖黄旧照片+墨绿+暗红+旗袍色, 做旧质感",
            "texture": "旗袍/中山装/洋房/弄堂/留声机/黄包车",
            "lighting": "暖黄旧光+煤气灯+旗袍逆光",
            "prop": "留声机/黄包车/旗袍/怀表/旧报纸",
        },
        "failure_modes": ["无时代符号=失民国", "色调过新=失旧质感", "无新旧冲突=失时代内核", "旗袍滥用=失叙事"],
        "measurement": "旗袍洋装+洋房弄堂+暖黄旧光+新旧冲突, 民国感达成",
        "alternatives": ["period_costume(更古)", "urban_modern(更现代)"],
        "cross_refs": {"genre": "民国/年代", "color": "暖黄做旧", "masters": "《花样年华》《色戒》《少帅你老婆又跑了》短剧"},
    },
    "campus": {
        "cn": "校园风",
        "trigger": "校园/青春/成长/初恋/校园霸凌/升学",
        "rationale": "校园=青春的容器, 校服+教室+操场+暗恋, 是成长与初恋的视觉化, 阳光是核心情绪。",
        "execution": {
            "palette": "明亮蓝白校服+绿操场+暖阳, 清新高饱和",
            "texture": "校服/课本/黑板/操场/单车/书包",
            "lighting": "自然阳光+dappled树影+逆光发丝",
            "prop": "校服/课本/单车/情书/校牌",
        },
        "failure_modes": ["无校服校园=失青春", "色调过暗=失阳光", "无成长弧=失校园意义", "成年化=失纯真"],
        "measurement": "校服校园+阳光清新+成长初恋弧, 青春感达成",
        "alternatives": ["urban_modern(更都市)", "romance_sweet(更甜)"],
        "cross_refs": {"genre": "青春/校园", "color": "明亮蓝白绿", "masters": "《那些年》《你的名字》《盛夏芬德拉》短剧"},
    },
    "workplace": {
        "cn": "职场风",
        "trigger": "职场/办公室/商战/职业伦理/打工人",
        "rationale": "职场=现代人生存场, 西装格子间+权力游戏+职业伦理, 是现代人在体制中的挣扎与跃升。",
        "execution": {
            "palette": "冷蓝灰+玻璃+西装黑, 专业冷调",
            "texture": "格子间/玻璃/西装/电脑/咖啡",
            "lighting": "荧光灯冷白+屏幕光映脸+办公室硬光",
            "prop": "西装/电脑/咖啡/工牌/PPT",
        },
        "failure_modes": ["无办公室符号=失职场", "色调过暖=失冷峻", "无权力游戏=失张力", "悬浮不真实=失代入"],
        "measurement": "格子间+冷蓝+权力游戏+职业伦理, 职场感达成",
        "alternatives": ["urban_modern(更都市)", "noir(更黑色)"],
        "cross_refs": {"genre": "职场/都市", "color": "冷蓝灰", "masters": "《社交网络》《穿Prada的女魔头》《朝阳似我》短剧"},
    },
    "cyber_noir": {
        "cn": "赛博黑色",
        "trigger": "赛博朋克+黑色电影/霓虹雨夜/蛇蝎美人/AI操控",
        "rationale": "赛博黑色=赛博朋克+黑色电影, 霓虹雨夜的蛇蝎美人与AI操控, 是科技异化下的道德迷宫。",
        "execution": {
            "palette": "霓虹紫粉青+深黑+雨夜反射, 高饱和暗调",
            "texture": "霓虹/雨/玻璃/义体/全息",
            "lighting": "霓虹为主光+底光+屏幕光映脸",
            "prop": "义体/全息/霓虹招牌/雨伞",
        },
        "failure_modes": ["霓虹过杂=失黑色", "无蛇蝎美人=失黑色核心", "无AI操控=失赛博", "肤色失真=失质感"],
        "measurement": "霓虹暗调+蛇蝎美人+AI操控+雨夜反射, 赛博黑色感达成",
        "alternatives": ["cyberpunk(更赛博)", "noir(更黑色)"],
        "cross_refs": {"genre": "赛博/黑色", "color": "霓虹紫粉青", "masters": "《银翼杀手》《攻壳机动队》"},
    },
    # ─── 类型细分(深化genre_profiles) ───
    "xianxia_realm": {
        "cn": "仙侠细分(境界体系)",
        "trigger": "仙侠修真/境界突破/法天象地/天劫飞升",
        "rationale": "仙侠细分=境界可视化体系(练气→筑基→金丹→元婴→化神→法天象地), 每境界有专属视觉, 突破是节奏锚点。",
        "execution": {
            "realm_visual": "练气(涟漪)→筑基(光圈)→金丹(丹纹)→元婴(小人影)→化神(法相)→法天象地(巨大法相)",
            "breakthrough": "天劫(雷劫云)+天象异变(花开/星辰移位)+突破光柱",
            "palette": "仙白金青/魔黑红紫/妖绿橙, 境界越高越纯",
            "technique": "剑气(纯粹线条)/法术(粒子符文)/神通(地形改变)",
        },
        "failure_modes": ["境界无可视层级=失爽感", "突破无天象=失仙气", "色彩阵营混乱=失逻辑", "前世今生无回收=悬置"],
        "measurement": "境界有可视化层级+突破天象+阵营色彩+前世回收, 仙侠体系感达成",
        "alternatives": ["wuxia_martial_arts(更写实)", "mythology_fantasy(更神话)"],
        "cross_refs": {"genre": "仙侠/修真", "vfx": "境界粒子/法相", "masters": "《诛仙》《云渺》短剧系列"},
    },
    "wuxia_jianghu": {
        "cn": "武侠细分(江湖体系)",
        "trigger": "江湖门派/侠义精神/兵器谱/江湖恩怨",
        "rationale": "武侠细分=江湖门派体系+侠义精神+兵器谱, 是武侠的社会学与伦理学, 非单纯打斗。",
        "execution": {
            "school": "少林(刚猛)/武当(柔)/峨眉(灵)/丐帮(民间)/魔教(邪)",
            "weapon": "刀(霸道)/剑(君子)/枪(战场)/暗器(诡)/掌(内力)",
            "palette": "水墨淡雅(文人)或浓艳红金(类型), 江湖气",
            "technique": "一招一式有交代+停顿句读+环境互动",
        },
        "failure_modes": ["无门派体系=失江湖", "兵器无性格=失兵器谱", "无侠义=失武侠魂", "动作无交代=shaky"],
        "measurement": "门派体系+兵器性格+侠义精神+招式交代, 江湖体系感达成",
        "alternatives": ["xianxia_realm(更仙侠)", "action_combat(更动作)"],
        "cross_refs": {"genre": "武侠", "director": "徐克/袁和平", "masters": "《黄飞鸿》《笑傲江湖》《一代宗师》"},
    },
    "spy_espionage": {
        "cn": "谍战/特工",
        "trigger": "谍战/潜伏/双面身份/情报战/冷战",
        "rationale": "谍战=双面身份+情报不对称+信任游戏, 是身份与忠诚的极限考验, 每个细节都是线索。",
        "execution": {
            "palette": "冷灰蓝+暗红(危险)+做旧, 低调暗调",
            "texture": "风衣/帽子/密码本/电台/旧地图",
            "lighting": "低调高对比+百叶窗切割+底光",
            "technique": "细节即线索(物件/眼神/台词双关)+交叉剪辑情报线",
        },
        "failure_modes": ["双面身份无张力=失谍战", "线索无回收=失伏笔", "无信任游戏=失伦理", "色调过亮=失暗调"],
        "measurement": "双面身份张力+线索回收+信任游戏+暗调, 谍战感达成",
        "alternatives": ["noir(更黑色)", "suspense_thriller(更悬疑)"],
        "cross_refs": {"genre": "谍战/悬疑", "director": "杜琪峰/王家卫(东邪西毒)", "masters": "《风声》《色戒》《潜伏》"},
    },
    "legal_drama": {
        "cn": "律政/法庭",
        "trigger": "法庭/律师/案件/法律伦理/正义程序",
        "rationale": "律政=法庭辩论+案件推理+法律伦理, 是正义程序的视觉化, 法庭是冲突的仪式化场域。",
        "execution": {
            "palette": "深木色+黑袍+白衬衫, 庄重冷调",
            "texture": "法袍/法槌/卷宗/西装/法庭",
            "lighting": "法庭顶光+证人席硬光+陪审团暗",
            "technique": "法庭正反打辩论+证据特写+反转证人",
        },
        "failure_modes": ["无法庭仪式=失律政", "辩论无逻辑=失推理", "无法律伦理=失深度", "无反转=失张力"],
        "measurement": "法庭仪式+辩论逻辑+法律伦理+反转, 律政感达成",
        "alternatives": ["spy_espionage(更谍战)", "noir(更黑色)"],
        "cross_refs": {"genre": "律政/剧情", "masters": "《十二怒汉》《造雨人》《legal high》"},
    },
    "medical_drama": {
        "cn": "医疗/医务",
        "trigger": "医院/医生/生死/医疗伦理/急诊",
        "rationale": "医疗=生死场+医疗伦理+急诊紧张, 是生死的日常化, 手术室是生死仪式场域。",
        "execution": {
            "palette": "医院白+手术绿+血红点缀+冷蓝",
            "texture": "白大褂/手术器械/监护仪/病床",
            "lighting": "手术室无影灯白+急诊冷蓝+病房暖",
            "technique": "手术特写+监护仪音+生死交叉剪辑",
        },
        "failure_modes": ["无医疗细节=失真实", "无生死伦理=失深度", "无急诊紧张=失张力", "色调无医院白=失医疗"],
        "measurement": "医疗细节+生死伦理+急诊紧张+医院白, 医疗感达成",
        "alternatives": ["survival(更生存)", "legal_drama(更律政)"],
        "cross_refs": {"genre": "医疗/剧情", "masters": "《豪斯医生》《白色巨塔》《浪漫医生》"},
    },
    "food_culinary": {
        "cn": "美食/料理",
        "trigger": "美食/料理/厨房/食物治愈/匠人",
        "rationale": "美食=食物特写治愈+料理过程+匠人精神, 食物是情感载体, 料理是仪式。",
        "execution": {
            "palette": "暖食色+厨房暖光+食材鲜艳",
            "texture": "食材/锅具/蒸汽/切工/摆盘",
            "lighting": "厨房暖光+食物特写柔光+蒸汽",
            "technique": "食物微距特写+切工慢放+蒸汽+摆盘",
        },
        "failure_modes": ["无食物特写=失美食", "无料理过程=失匠人", "色调过冷=失治愈", "无情感=失食物意义"],
        "measurement": "食物特写+料理过程+暖色治愈+情感, 美食感达成",
        "alternatives": ["pastoral_idyllic(更田园)", "family_warmth(更家庭)"],
        "cross_refs": {"genre": "美食/治愈", "masters": "《小森林》《饮食男女》《舌尖》"},
    },
    "sports": {
        "cn": "运动/竞技",
        "trigger": "运动/比赛/竞技/团队/逆袭夺冠",
        "rationale": "运动=竞技动态+团队羁绊+逆袭弧光, 比赛是冲突的仪式化, 训练是成长蒙太奇。",
        "execution": {
            "palette": "赛场高饱和+队服色+草场/球场",
            "texture": "队服/球鞋/汗水/赛场",
            "lighting": "赛场强光+汗水反光+观众席",
            "technique": "运动多机位+慢放顶点+训练蒙太奇+观众反应",
        },
        "failure_modes": ["无竞技动态=失运动", "无团队羁绊=失情感", "无逆袭弧=失成长", "无训练蒙太奇=失节奏"],
        "measurement": "竞技动态+团队羁绊+逆袭弧+训练蒙太奇, 运动感达成",
        "alternatives": ["action_combat(更动作)", "campus(更校园)"],
        "cross_refs": {"genre": "运动/竞技", "masters": "《摔跤吧爸爸》《排球少年》《绝杀》"},
    },
    "music_mv": {
        "cn": "音乐/MV",
        "trigger": "音乐/MV/歌舞/音乐驱动/舞台",
        "rationale": "音乐MV=音乐驱动视觉+节拍剪辑+梦幻段落, 是音乐与影像的共谋, 节拍是剪辑律。",
        "execution": {
            "palette": "随音乐情绪, 高饱和或单色段落",
            "texture": "乐器/舞台/灯光/服装",
            "lighting": "舞台聚光+霓虹+梦幻打光",
            "technique": "节拍器剪辑+长镜头走入+群舞几何+速度变化",
        },
        "failure_modes": ["节拍不卡=失律动", "无梦幻段落=失魔力", "无群舞几何=失美感", "无速度变化=失高潮"],
        "measurement": "节拍卡帧+梦幻段落+群舞几何+速度变化, MV感达成",
        "alternatives": ["musical(更歌舞)", "romance_sweet(更爱情)"],
        "cross_refs": {"genre": "音乐/MV", "director": "Chazelle/Sam Kolder", "masters": "《爱乐之城》MV, Sam Kolder"},
    },
}


# 细分风格→genre映射(引擎查询时用)
SUBDIVISION_TO_GENRE = {
    "steampunk": "sci_fi", "post_apocalypse": "survival", "republic_era": "period_costume",
    "campus": "urban_modern", "workplace": "urban_modern", "cyber_noir": "cyberpunk",
    "xianxia_realm": "xianxia_cultivation", "wuxia_jianghu": "wuxia_martial_arts",
    "spy_espionage": "suspense_thriller", "legal_drama": "noir", "medical_drama": "survival",
    "food_culinary": "pastoral_idyllic", "sports": "action_combat", "music_mv": "musical",
}


def get_style_subdivision(style_key):
    """获取细分风格决策"""
    return STYLE_SUBDIVISIONS.get(style_key, {})


def list_subdivisions():
    """列出所有细分风格"""
    return [(k, v.get("cn", "")) for k, v in STYLE_SUBDIVISIONS.items()]
