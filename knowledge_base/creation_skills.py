# -*- coding: utf-8 -*-
# ============================================================
# 短剧/影视/短视频 创作技法库 V1.0 (全网检索skill整合)
# ============================================================
# 来源: 全网检索(抖音运营指南/新榜短剧榜/短视频爆款拆解/主流媒体黄金前N秒)
# 真实技法(非虚构), 7维决策树, 服务引擎创作指导
# ============================================================

CREATION_SKILLS = {

    # ========================================================
    # 一、短视频6大爆款元素(2026全网拆解上千条爆款)
    # ========================================================
    "save_money": {
        "cn": "帮用户省钱(爆款元素1)",
        "trigger": "实用省钱/薅羊毛/智商税/不同预算怎么选",
        "rationale": "省钱是人类最底层本能需求,经济越不确定这条越灵,2026第一流量密码。",
        "execution": {
            "keyword_roots": ["花小钱办大事","薅羊毛","捡漏","智商税","不该交的小钱","不同预算怎么选"],
            "format": "实用清单+价格对比+真实体验",
            "hook": "开头直给'这X样东西千万别买'",
        },
        "failure_modes": ["省钱无具体=空泛", "硬广=失信", "价格无对比=失说服"],
        "measurement": "观众收藏+转发(实用价值驱动),非单纯点赞",
        "alternatives": ["avoid_pit(更避坑)"],
        "cross_refs": {"platform": "全平台", "engagement": "实用价值=收藏转发"},
    },
    "avoid_pit": {
        "cn": "帮用户避坑(爆款元素2)",
        "trigger": "避坑/最后悔/不能买/最差/四大傻",
        "rationale": "试错成本升高,用户更想避坑而非种草,讲最差/会后悔=竖耳听。",
        "execution": {
            "keyword_roots": ["智商税","不能买","最容易贬值","最后悔","四大傻","最冤"],
            "format": "避坑清单+反面案例+真实后悔",
            "hook": "开头'这3样千万别在网上买'",
        },
        "failure_modes": ["避坑无具体=空吓", "无真实案例=失说服", "过激=失公允"],
        "measurement": "观众评论'我也踩过'=共鸣互动",
        "alternatives": ["save_money(更省钱)"],
        "cross_refs": {"engagement": "避坑>种草", "interaction": "评论区共鸣"},
    },
    "label_match": {
        "cn": "戳用户标签(爆款元素3)",
        "trigger": "星座/MBTI/地域/新手小白/第一次/预算有限",
        "rationale": "人对'与自己有关'的信息极度敏感,大脑潜意识瞬间识别'是不是关于我'。",
        "execution": {
            "keyword_roots": ["星座","MBTI","地域","新手小白","第一次xxx","预算有限"],
            "format": "身份标签+该身份痛点+解决方案",
            "hook": "开头'INFP最不适合的5种工作'",
        },
        "failure_modes": ["标签无共鸣=失识别", "讲你想讲非用户想听=失焦", "标签过泛=失精准"],
        "measurement": "观众'这说的不就是我'=停留+关注转化",
        "alternatives": ["contrast(更反差)"],
        "cross_refs": {"engagement": "身份共鸣=关注转化", "retention": "标签驱动停留"},
    },
    "ride_hot_traffic": {
        "cn": "借势蹭流量(爆款元素4)",
        "trigger": "热点/名人/名企/名校/天花板级别",
        "rationale": "借势是获流量最快方式,热度在时发天然有人看,但转粉率偏低须做成系列沉淀。",
        "execution": {
            "keyword_roots": ["热点事件","名人","名企","名校","天花板级别"],
            "format": "蹭热点+系列化沉淀(蹭完做成系列)",
            "hook": "开头绑定热点名人",
        },
        "failure_modes": ["蹭完就跑=转粉率低", "蹭无系列=失沉淀", "蹭过时热点=失效"],
        "measurement": "热点期流量+系列沉淀后的关注转化",
        "alternatives": ["contrast(更反差)"],
        "cross_refs": {"engagement": "蹭流量转粉须系列化", "retention": "系列沉淀"},
    },
    "make_contrast": {
        "cn": "制造反差(爆款元素5)",
        "trigger": "before-after反差/前期穷后期逆袭/极端对比",
        "rationale": "反差=最直接的视觉/情绪冲击,前期越惨后期越爽,反差越大效果越强。",
        "execution": {
            "keyword_roots": ["before-after","前期后期","逆袭","极端对比"],
            "format": "前期(穷/惨/弱)→后期(逆袭/强/美),反差越大",
            "hook": "开头给前期惨状or后期成果",
        },
        "failure_modes": ["反差不够大=失冲击", "前期无铺垫=失弹", "后期无爽点=失释放"],
        "measurement": "反差冲击+完播率(想知道怎么逆袭的)",
        "alternatives": ["label_match(更标签)"],
        "cross_refs": {"engagement": "反差=完播驱动", "pacing": "前期慢后期快"},
    },

    # ========================================================
    # 二、平台算法逻辑(全网检索抖音/快手/视频号差异)
    # ========================================================
    "douyin_algo": {
        "cn": "抖音算法逻辑",
        "trigger": "抖音首发/抢公域流量/3秒钩子定生死",
        "rationale": "抖音=内容分发赛马场,新内容推给小批标签用户,数据好续推大池,差停。抢初始点击率+完播率是核心。",
        "execution": {
            "core": "抢初始流量池点击率+完播率",
            "3s_hook": "开头3秒勾住(决定70%去留)",
            "pacing": "节奏快,每帧传递信息",
            "ending": "结尾留互动点(评论/关注)",
            "tag_accuracy": "标签准=推对人(比投流重要)",
        },
        "failure_modes": ["开头慢铺垫=完播率<10%", "标签不准=推错人", "无互动点=失互动率"],
        "measurement": "初始池完播率+点击率高=续推大流量池",
        "alternatives": ["kuaishou_algo(老铁)", "videoaccount_algo(社交)"],
        "cross_refs": {"platform": "抖音", "retention": "3秒钩子+完播率"},
    },
    "videoaccount_algo": {
        "cn": "视频号算法逻辑",
        "trigger": "视频号首发/微信社交裂变/转发为王",
        "rationale": "视频号天生微信社交属性,粉丝点赞转发→好友也刷到=社交裂变buff,流量来自社交推荐。",
        "execution": {
            "core": "社交裂变(转发>点赞)",
            "social": "粉丝转发→好友看到=裂变",
            "content": "适合银发/家庭温情/有共鸣(易转发表态)",
            "trigger": "朋友圈顺手点进",
        },
        "failure_modes": ["无社交货币=不转发", "内容过冷=失温情共鸣", "无身份认同=失表态"],
        "measurement": "转发率(社交裂变)>点赞,适合温情共鸣内容",
        "alternatives": ["douyin_algo(公域)", "kuaishou_algo(老铁)"],
        "cross_refs": {"platform": "视频号", "engagement": "转发=社交裂变核心"},
    },
    "kuaishou_algo": {
        "cn": "快手算法逻辑",
        "trigger": "快手首发/老铁经济/真实感>精致",
        "rationale": "快手=老铁文化,真实感>精致,关注转化权重高,粉丝是私域资产,粘性为王。",
        "execution": {
            "core": "老铁粘性(关注转化权重高)",
            "realism": "真实感>制作精良",
            "community": "评论区/直播=私域社群",
            "trust": "人设信任>内容炫技",
        },
        "failure_modes": ["过精致=失老铁真实感", "无人设=失信任", "无社群=失粘性"],
        "measurement": "关注转化率(老铁粘性)+直播互动",
        "alternatives": ["douyin_algo(公域)", "videoaccount_algo(社交)"],
        "cross_refs": {"platform": "快手", "engagement": "关注转化+私域粘性"},
    },

    # ========================================================
    # 三、黄金前N秒(主流媒体爆款拆解)
    # ========================================================
    "golden_shock_open": {
        "cn": "黄金前N秒震撼开场",
        "trigger": "新闻/主流媒体/震撼画面开场/前N秒抓人",
        "rationale": "前N秒(3-5秒)震撼画面=快速抓住注意力,人民日报/央视等主流媒体最爱用,是新闻类爆款核心。",
        "execution": {
            "types": ["震撼类(练兵/灾难/反常画面)", "反差类(预期违背)", "悬念类(信息缺口)", "情绪类(直接催泪)"],
            "timing": "前3-5秒必须发生",
            "sync": "同期声+震撼画面同步",
        },
        "failure_modes": ["震撼无同期声=失冲击", "震撼与主题无关=失焦点", "震撼后无内容=完播崩"],
        "measurement": "前N秒震撼+同期声,完播率>50%",
        "alternatives": ["make_contrast(更反差)", "save_money(更实用)"],
        "cross_refs": {"platform": "主流媒体/抖音", "retention": "前N秒定生死"},
    },

    # ========================================================
    # 四、人设IP打造(全网检索爆款账号规律)
    # ========================================================
    "persona_ip": {
        "cn": "人设IP打造",
        "trigger": "持续涨粉/账号辨识度/垂直IP/粉丝粘性",
        "rationale": "人设=持续运营保障,鲜明人设=刷到就知道你专注什么(垂直度),记忆点=涨粉变现法宝。",
        "execution": {
            "vertical": "垂直领域(只做一个领域)",
            "consistent": "风格统一(有辨识度)",
            "persona": "你是谁+能提供什么价值(人设三问)",
            "series": "系列化沉淀(蹭流量做成系列)",
        },
        "failure_modes": ["无垂直度=失辨识", "风格不统一=失记忆", "无人设三问=失价值", "蹭完不沉淀=失粉"],
        "measurement": "刷到3秒识别=垂直人设立住,粉丝粘性高",
        "alternatives": ["douyin_algo(算法)"],
        "cross_refs": {"retention": "人设=关注转化保障", "engagement": "人设信任=变现"},
    },

    # ========================================================
    # 五、短剧精品化趋势(全网检索2025年度榜)
    # ========================================================
    "premium_shortdrama": {
        "cn": "短剧精品化",
        "trigger": "短剧精品化/电视剧级班底/单集成本50万+/豆瓣入榜",
        "rationale": "短剧告别野蛮生长进入精细耕作,专业演员+优质剧本+精良制作=出圈关键,百亿播放成头部新门槛。",
        "execution": {
            "production": "电视剧级班底+专业打光镜头语言",
            "actor": "传统长剧演员+短剧达人跨界(刘晓庆/倪虹洁)",
            "script": "现实主义温情>狗血(家里家外模式)",
            "rating": "豆瓣入榜(评分体系建立)",
        },
        "failure_modes": ["狗血=失口碑", "非专业班底=失质感", "无现实根基=失共鸣"],
        "measurement": "豆瓣评分+百亿播放+口碑出圈",
        "alternatives": ["face_slapping_cascade(传统爽剧)"],
        "cross_refs": {"platform": "抖音/红果", "trend": "精品化2025"},
    },
}


def get_creation_skill(skill_key):
    """获取创作技法"""
    return CREATION_SKILLS.get(skill_key, {})


def build_creation_skills_section(query_tags, is_vertical, mode):
    """构建创作技法章节(按query_tags匹配注入)"""
    lines = ["【创作技法对标(全网检索skill)】"]
    # 按竖屏+模式+标签匹配技法
    injected = []
    if is_vertical or "短剧" in mode or "短视频" in mode:
        # 短视频/短剧: 注入爆款元素+平台算法
        tag_to_skill = {
            "省钱": "save_money", "实用": "save_money", "避坑": "avoid_pit",
            "身份": "label_match", "标签": "label_match", "星座": "label_match",
            "热点": "ride_hot_traffic", "反差": "make_contrast", "逆袭": "make_contrast",
        }
        for tag, sk in tag_to_skill.items():
            if any(tag in t for t in query_tags) and sk not in injected:
                s = CREATION_SKILLS.get(sk, {})
                if s:
                    lines.append(f"  ◆ {s.get('cn','')}: {s.get('rationale','')[:50]}")
                    if s.get("failure_modes"):
                        lines.append(f"    失败模式: {'; '.join(s['failure_modes'][:2])}")
                    injected.append(sk)
    # 平台算法(竖屏默认抖音,银发默认视频号)
    algo = "douyin_algo"
    if any("银发" in t or "家庭" in t for t in query_tags):
        algo = "videoaccount_algo"
    if not injected:  # 无匹配则至少给平台算法
        s = CREATION_SKILLS.get(algo, {})
        if s:
            lines.append(f"  ◆ {s.get('cn','')}: {s.get('rationale','')[:50]}")
    if not injected and not lines[1:]:
        return ""
    return "\n".join(lines) if len(lines) > 1 else ""
