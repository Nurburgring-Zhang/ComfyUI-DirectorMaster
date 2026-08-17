# ============================================================
# 绘本画风深度知识库 V1.0
# 每种画风 = 触发→原理→量化执行→失败模式→验收→替代→交叉
# 服务绘本模式/儿童内容模式的画风决策
# ============================================================

PICTURE_BOOK_STYLES = {
    "watercolor": {
        "cn": "水彩插画",
        "trigger": "童话/治愈/回忆/自然/温柔叙事/适合3-8岁",
        "rationale": "水彩的透明叠加+晕染=流动与不确定, 暗示梦境与回忆, 是绘本最经典的温柔载体。",
        "execution": {
            "technique": "湿画法(色彩在湿纸上自然晕染)/干画法(分层叠加)",
            "palette": "低饱和透明色+大量留白, 主色2-3+点缀1",
            "texture": "纸纹可见, 边缘柔和虚化, 水迹自然",
            "line": "淡铅笔稿或无线, 色块定义形体",
        },
        "failure_modes": ["颜色过杂=失透明感(≤3主色)", "覆盖太厚=失水彩透(变水粉)", "边缘过锐=失柔和(变数码)"],
        "measurement": "透明晕染感+纸纹可见+2-3主色留白, 观众读出温柔梦境",
        "alternatives": ["colored_pencil(更线条)", "pastel(更柔和粉感)"],
        "cross_refs": {"age": "3-8岁最佳", "genre": "童话/治愈", "lighting": "柔和散射光", "masters": "《小熊维尼》原著, 《活了100万次的猫》"},
    },
    "colored_pencil": {
        "cn": "彩铅手绘",
        "trigger": "日记感/质朴/手作温度/校园/成长回忆/适合6-12岁",
        "rationale": "彩铅的可见笔触+排线=手作温度与质朴, 笔触本身是情感载体, 适合日记式成长叙事。",
        "execution": {
            "technique": "排线(平行/交叉)/叠色(层层加深)/留白(纸的白)",
            "palette": "中等饱和, 6-10色铅笔, 可叠出丰富中间色",
            "texture": "纸纹+笔触清晰可见, 留白处显纸色",
            "line": "彩色线条定义形体, 线条本身有颜色情绪",
        },
        "failure_modes": ["笔触无方向=失温度(变平涂)", "颜色过满=失留白质朴", "线过细=失手作感"],
        "measurement": "可见笔触+排线有方向+留白质朴, 手作温度达成",
        "alternatives": ["watercolor(更晕染)", "pastel(更粉柔)"],
        "cross_refs": {"age": "6-12岁", "genre": "成长/日记", "line": "彩色线条是核心", "masters": "《彩色的诗》, 校园绘本"},
    },
    "claymation": {
        "cn": "黏土定格",
        "trigger": "立体玩具感/童趣/怪物奇幻/怪诞可爱/适合3-9岁",
        "rationale": "黏土的立体+指纹+笨拙=玩具感与童趣, 指纹是手工痕迹, 笨拙反而是可爱之源。",
        "execution": {
            "technique": "黏土塑形+定格拍摄/单帧立体插画",
            "palette": "高饱和纯色块, 块面分明",
            "texture": "黏土光泽+指纹可见+接缝自然",
            "lighting": "实拍布光, 柔和主光+轮廓分面",
        },
        "failure_modes": ["造型过精=失童趣(变CG)", "指纹接缝修平=失手工", "色彩过灰=失玩具感"],
        "measurement": "立体玩具感+指纹可见+笨拙可爱, 童趣达成",
        "alternatives": ["paper_cut(更平面)", "flat_vector(更几何)"],
        "cross_refs": {"age": "3-9岁", "genre": "童趣/怪物", "masters": "《小鸡快跑》, 《玛丽和马克思》"},
    },
    "flat_vector": {
        "cn": "扁平矢量",
        "trigger": "现代/极简/教育/科普/界面感/适合6-12岁+教学",
        "rationale": "扁平矢量的几何纯色+无多余细节=信息清晰, 适合教育科普与现代极简叙事。",
        "execution": {
            "technique": "矢量几何形+纯色块+无渐变(或极简渐变)",
            "palette": "高对比2-4纯色, 几何分明",
            "texture": "无纹理(纯色), 边缘锐利",
            "line": "无线或粗轮廓线",
        },
        "failure_modes": ["细节过多=失极简(变插画)", "色块无层次=失信息", "几何无设计=失现代感"],
        "measurement": "几何纯色+信息清晰+极简现代, 教育清晰度达成",
        "alternatives": ["paper_cut(更手作)", "colored_pencil(更温度)"],
        "cross_refs": {"age": "6-12岁教学", "genre": "教育/科普", "masters": "《理想国》绘本, UI插画风"},
    },
    "oil_painting": {
        "cn": "油画质感",
        "trigger": "古典/史诗/严肃文学/厚重情感/适合9-12岁+成人向绘本",
        "rationale": "油画的厚涂+笔触+层次=厚重与古典, 适合严肃文学与史诗情感, 是绘本中的'重'载体。",
        "execution": {
            "technique": "厚涂(impasto)/罩染(glazing)分层/直接画法",
            "palette": "古典暖褐金+深色背景, 饱和中等",
            "texture": "笔触厚可见, 布纹/木纹底",
            "lighting": "伦勃朗式明暗, 戏剧光",
        },
        "failure_modes": ["颜色过灰=失古典(变水彩)", "笔触过薄=失厚重", "题材过轻=失油画适配"],
        "measurement": "厚涂笔触+古典明暗+厚重情感, 古典史诗感达成",
        "alternatives": ["watercolor(更轻)", "ink_wash(更东方)"],
        "cross_refs": {"age": "9-12岁+成人", "genre": "古典/史诗", "lighting": "伦勃朗光", "masters": "《彼得与狼》油画绘本"},
    },
    "paper_cut": {
        "cn": "剪纸/拼贴",
        "trigger": "民间/民俗/节庆/平面装饰/东方/适合3-9岁",
        "rationale": "剪纸的负空间+对称+纯色=民间装饰美, 负空间(镂空)是剪纸的核心语言。",
        "execution": {
            "technique": "剪/刻+拼贴, 单色或多色纸层",
            "palette": "红/黑/白经典+民间彩色, 高对比",
            "texture": "纸边毛茬可见, 层叠阴影",
            "space": "负空间(镂空)与实体同等重要",
        },
        "failure_modes": ["镂空无设计=失负空间美", "对称过死=失灵动", "色过多=失剪纸纯度"],
        "measurement": "负空间设计+民间装饰美+对称灵动, 民俗感达成",
        "alternatives": ["flat_vector(更几何)", "ink_wash(更水墨)"],
        "cross_refs": {"age": "3-9岁", "genre": "民俗/节庆", "masters": "中国剪纸, 《桃花鱼》"},
    },
    "ink_wash": {
        "cn": "水墨",
        "trigger": "东方/诗性/写意/禅意/文人/适合6-12岁+东方文学",
        "rationale": "水墨的浓淡干湿+留白+写意=东方诗性与禅意, 留白是意境的核心, 写意胜工笔。",
        "execution": {
            "technique": "写意(浓淡墨)/工笔(细致)/泼墨(自由)",
            "palette": "墨黑白为主+淡彩(花青/赭石)点缀",
            "texture": "宣纸纹+墨晕+飞白(干笔)",
            "space": "大量留白=意境, 实体与留白同等",
        },
        "failure_modes": ["墨过满=失留白意境", "工笔过细=失写意", "加彩过多=失墨韵"],
        "measurement": "浓淡干湿+留白意境+写意, 东方诗性达成",
        "alternatives": ["watercolor(更西式)", "paper_cut(更民俗)"],
        "cross_refs": {"age": "6-12岁东方", "genre": "诗性/禅意", "masters": "《山水中国》, 熊亮水墨绘本"},
    },
    "pastel": {
        "cn": "粉彩/油画棒",
        "trigger": "梦幻/柔和/粉感/童真/适合0-6岁低幼",
        "rationale": "粉彩的柔和粉感+模糊边缘=梦幻与童真, 是低幼绘本最柔和的载体, 边缘模糊=安全感。",
        "execution": {
            "technique": "涂抹/晕擦/叠色(粉彩可混合)",
            "palette": "马卡龙低饱和粉柔色, 3-5色",
            "texture": "粉感颗粒可见, 纸纹融入",
            "edge": "边缘模糊柔和, 无锐线",
        },
        "failure_modes": ["边缘过锐=失粉柔(变数码)", "色过饱和=失马卡龙", "细节过多=失低幼柔和"],
        "measurement": "粉感颗粒+模糊边缘+马卡龙柔和, 低幼梦幻感达成",
        "alternatives": ["watercolor(更透明)", "colored_pencil(更线条)"],
        "cross_refs": {"age": "0-6岁低幼", "genre": "梦幻/童真", "masters": "《好饿的毛毛虫》粉彩感"},
    },
    "digital_cute": {
        "cn": "数码可爱(现代卡通)",
        "trigger": "现代儿童/萌系/明亮/表情夸张/适合3-9岁+数字原生",
        "rationale": "数码卡通的粗轮廓+夸张表情+明亮色=现代儿童审美, 表情夸张是可爱来源, 适合数字原生世代。",
        "execution": {
            "technique": "矢量/位图卡通, 粗黑轮廓+纯色填充",
            "palette": "高饱和明亮色, 对比强",
            "texture": "无纹理(纯色)或有简单渐变",
            "expression": "表情夸张放大, 头身比Q版(2-3头身)",
        },
        "failure_modes": ["轮廓过细=失萌(变插画)", "表情不夸张=失可爱", "色过灰=失明亮"],
        "measurement": "粗轮廓+夸张表情+明亮Q版, 现代萌感达成",
        "alternatives": ["claymation(更立体玩具)", "flat_vector(更几何教育)"],
        "cross_refs": {"age": "3-9岁", "genre": "现代儿童/萌系", "masters": "《小猪佩奇》, 《汪汪队》"},
    },
}


# 绘本叙事原则(7维决策)
PICTURE_BOOK_NARRATIVE = {
    "page_turn_suspense": {
        "cn": "翻页悬念",
        "trigger": "绘本每页结尾/引导孩子主动翻页",
        "rationale": "绘本的节奏单位是'页', 每页结尾留悬念=孩子主动翻页, 是绘本独有的交互。",
        "failure_modes": ["每页结尾无悬念=孩子停翻", "悬念过强=低幼不适", "翻页后无惊喜=失信"],
        "measurement": "每页结尾有翻页动力, 翻页后有惊喜",
        "alternatives": ["page_break_anticipation"],
        "cross_refs": {"pacing": "页=节奏单位", "interaction": "翻页是儿童交互"},
    },
    "visual_rhyme": {
        "cn": "视觉韵律(重复变奏)",
        "trigger": "绘本重复句式/视觉母题变奏",
        "rationale": "重复+变奏=儿童语言节奏, 重复给安全感, 变奏给惊喜, 是绘本节奏核心。",
        "failure_modes": ["重复无变奏=枯燥", "变奏过远=失节奏", "无重复=失儿童韵律"],
        "measurement": "重复句式有变奏, 儿童韵律感达成",
        "alternatives": ["page_turn_suspense"],
        "cross_refs": {"pacing": "重复变奏=绘本节奏", "language": "儿童语言节奏"},
    },
    "show_dont_tell_child": {
        "cn": "展示而非说教(儿童版)",
        "trigger": "绘本不说教/用画面传递道理",
        "rationale": "儿童反感说教, 用画面动作传递道理=孩子自然接受, 是绘本伦理核心。",
        "failure_modes": ["说教=孩子抵触", "道理过隐=孩子不懂", "无画面传递=失绘本性"],
        "measurement": "道理通过画面传递, 不说教, 孩子能懂",
        "alternatives": ["visual_metaphor"],
        "cross_refs": {"ethics": "不说教核心", "show_dont_tell": "绘本版"},
    },
}


def get_picture_book_style(style_key):
    """合并绘本画风基础信息(已是7维, 无需覆盖层)"""
    return PICTURE_BOOK_STYLES.get(style_key, {})
