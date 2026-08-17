# ============================================================
# 儿童内容风格深度知识库 V1.0
# 年龄段细分 + 画风适配 + 叙事/伦理原则, 7维决策树
# 服务儿童内容模式(儿童视频/微动/绘本格式)
# ============================================================

CHILDREN_CONTENT_STYLES = {
    # ─── 年龄段细分(4档, 每档7维决策) ───
    "age_0_3": {
        "cn": "0-3岁低幼",
        "trigger": "0-3岁低幼内容/认知启蒙/感官发展",
        "rationale": "0-3岁认知=感官+重复+简单因果。极简主体+重复句式+高对比=安全感与认知建构。",
        "execution": {
            "complexity": "单一主体+单一动作, 无复杂情节",
            "language": "极短句(5-15字), 重复句式, 拟声词",
            "visual": "极简主体突出, 高对比色, 柔和边缘(pastel/watercolor)",
            "duration_per_unit": "3-8秒/单元(注意力短)",
            "pacing": "极慢, 重复为主, 无反转",
        },
        "failure_modes": ["情节复杂=超认知(孩子不懂)", "色过低对比=失注意", "句过长=失重复韵律", "时长过8秒=失注意"],
        "measurement": "孩子能跟随单一主体+重复句式, 注意力3-8秒/单元",
        "alternatives": ["age_3_6(更复杂)"],
        "cross_refs": {"style": "pastel/watercolor/flat", "genre": "认知启蒙", "masters": "《小熊宝宝》, 《蹦》"},
    },
    "age_3_6": {
        "cn": "3-6岁幼儿",
        "trigger": "3-6岁幼儿/简单情节/情感启蒙/社交入门",
        "rationale": "3-6岁=简单起承转合+情感识别。有清晰焦点+简单情节+情绪外化=情感与社交启蒙。",
        "execution": {
            "complexity": "简单起承转合(1主线), 清晰焦点",
            "language": "每页20-40字/每单元, 完整简单句",
            "visual": "画面丰富有焦点, 色彩活泼, 3-6主色",
            "duration_per_unit": "5-15秒/单元",
            "pacing": "中速, 有小波折小惊喜",
        },
        "failure_modes": ["多线索=超认知", "焦点不清=失注意", "情绪无外化=孩子不懂", "时长过15秒=失注意"],
        "measurement": "孩子能复述简单情节+识别情绪, 注意力5-15秒/单元",
        "alternatives": ["age_0_3(更简)", "age_6_9(更复杂)"],
        "cross_refs": {"style": "watercolor/colored_pencil/claymation/digital_cute", "genre": "情感启蒙", "masters": "《好饿的毛毛虫》, 《我爸爸》"},
    },
    "age_6_9": {
        "cn": "6-9岁学龄",
        "trigger": "6-9岁学龄/完整情节/价值观启蒙/独立阅读过渡",
        "rationale": "6-9岁=完整起承转合+价值观启蒙。细节丰富+多线索伏笔+角色弧光=独立阅读过渡。",
        "execution": {
            "complexity": "完整起承转合, 可2-3线索, 伏笔回收",
            "language": "每页30-60字/每单元30-60秒, 完整段落",
            "visual": "细节丰富, 写实或风格化, 多层信息",
            "duration_per_unit": "15-40秒/单元",
            "pacing": "中速偏快, 有完整波折高潮",
        },
        "failure_modes": ["情节过简=失学龄深度", "无伏笔=失阅读价值", "价值观说教=孩子抵触", "画风过幼=失适配"],
        "measurement": "孩子能理解完整情节+伏笔回收+价值观, 独立阅读过渡",
        "alternatives": ["age_3_6(更简)", "age_9_12(更深)"],
        "cross_refs": {"style": "colored_pencil/ink_wash/flat_vector", "genre": "成长/冒险", "masters": "《神奇树屋》, 《西游记》绘本"},
    },
    "age_9_12": {
        "cn": "9-12岁少年",
        "trigger": "9-12岁少年/复杂叙事/抽象主题/青春前奏",
        "rationale": "9-12岁=复杂叙事+抽象主题+角色弧光。写实或艺术风格+多线索+道德灰色=青春前奏。",
        "execution": {
            "complexity": "复杂叙事, 多线索交织, 道德灰色",
            "language": "每页50-100字/每单元40-90秒, 段落+对话",
            "visual": "写实或具艺术风格, 抽象象征",
            "duration_per_unit": "40-90秒/单元",
            "pacing": "完整节奏, 高潮+余韵",
        },
        "failure_modes": ["情节过简=失少年深度", "无道德灰色=失适配", "画风过幼=失尊重", "说教=少年抵触"],
        "measurement": "少年能理解复杂叙事+抽象主题+角色弧光",
        "alternatives": ["age_6_9(更简)"],
        "cross_refs": {"style": "ink_wash/oil_painting/colored_pencil", "genre": "成长/奇幻/现实", "masters": "《哈利波特》绘本版, 《草房子》"},
    },
    # ─── 儿童内容伦理/叙事原则(7维) ───
    "no_premature_anxiety": {
        "cn": "无过早焦虑(年龄适配恐惧)",
        "trigger": "儿童内容恐惧/危险元素处理",
        "rationale": "儿童恐惧须年龄适配: 低幼无真恐惧(用'消失'代'死亡'), 学龄可有可控恐惧, 少年可有复杂。过早焦虑=创伤。",
        "failure_modes": ["低幼出现死亡=创伤", "恐惧无胜利=失安全", "危险无成人介入(低幼)=失保护"],
        "measurement": "恐惧年龄适配, 有胜利/保护, 无过早焦虑",
        "alternatives": ["age_adapted_scary"],
        "cross_refs": {"ethics": "年龄适配核心", "horror": "儿童版恐惧处理"},
    },
    "positive_resolution": {
        "cn": "正向结局(希望收尾)",
        "trigger": "儿童内容结局/价值观传递",
        "rationale": "儿童内容结局须正向(希望/成长/和解), 给孩子安全感与价值观锚点, 非成人式开放/悲剧。",
        "failure_modes": ["开放/悲剧结局=孩子不安", "无成长=失教育", "和解无过程=失说服"],
        "measurement": "结局正向(希望/成长/和解), 有过程说服",
        "alternatives": ["open_ending(少年可用)"],
        "cross_refs": {"ethics": "正向结局核心", "narrative": "儿童弧光"},
    },
    "adult_as_anchor": {
        "cn": "成人作锚点(低幼)",
        "trigger": "0-6岁低幼危险场景/角色困境",
        "rationale": "低幼危险场景须有成人介入/保护作锚点, 给孩子安全感; 学龄后角色可自救。",
        "failure_modes": ["低幼无成人保护=失安全感", "角色自救过早(低幼)=失真实", "成人缺席=焦虑"],
        "measurement": "低幼危险有成人锚点, 学龄后角色可自救",
        "alternatives": ["character_self_rescue(学龄+)"],
        "cross_refs": {"ethics": "低幼安全核心", "age": "0-6岁必备"},
    },
    "repetition_with_variation": {
        "cn": "重复变奏(儿童语言节奏)",
        "trigger": "儿童内容语言/视觉节奏",
        "rationale": "重复给安全感, 变奏给惊喜, 是儿童语言与视觉节奏核心(与绘本visual_rhyme同源)。",
        "failure_modes": ["重复无变奏=枯燥", "变奏过远=失韵律", "无重复=失儿童节奏"],
        "measurement": "重复有变奏, 儿童韵律感达成",
        "alternatives": ["visual_rhyme(绘本版)"],
        "cross_refs": {"pacing": "儿童节奏核心", "language": "重复句式"},
    },
}


# 年龄段→画风适配矩阵
AGE_STYLE_MATRIX = {
    "0-3岁低幼": ["pastel", "watercolor", "flat_vector"],
    "3-6岁幼儿": ["watercolor", "colored_pencil", "claymation", "digital_cute"],
    "6-9岁学龄": ["colored_pencil", "ink_wash", "flat_vector", "watercolor"],
    "9-12岁少年": ["ink_wash", "oil_painting", "colored_pencil"],
}


def get_children_style(age_key):
    """获取年龄段风格决策"""
    return CHILDREN_CONTENT_STYLES.get(age_key, {})


def get_age_style_recommendations(age_cn):
    """年龄段→推荐画风(从picture_book_styles)"""
    return AGE_STYLE_MATRIX.get(age_cn, [])
