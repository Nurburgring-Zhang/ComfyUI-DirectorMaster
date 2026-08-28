# -*- coding: utf-8 -*-
"""
① DirectorMasterCore — 起点·核心总控
=====================================
2 输出: 统一电影提示词 + 核心数据包.
11 能力块 (灵魂+审美+风格+意图+提示词+签名+反AI+维度+8原则+色板+元数据) 折入核心数据包 JSON.
AI 配置打包进核心数据包, 下游连接即继承.
"""
import os as _os, sys as _sys, json as _json
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _PARENT not in _sys.path: _sys.path.insert(0, _PARENT)
if _HERE not in _sys.path: _sys.path.insert(0, _HERE)

from aggregator.node_base import DirectorNodeBase, parse_core_pack, resolve_ai_config, match_director_fuzzy, parse_multi_select
from aggregator.narrative_arrangement import ARRANGEMENT_MODES, NARRATIVE_LINE_MODES

# 导演分类
CATS = ["电影","电视","广告","短视频","动画","全部"]
try:
    from director_data_unified import DIRECTOR_PROFILES_ALL
    from director_profiles_film import FILM_DIRECTORS_100
    from director_profiles_tv_drama import TV_DRAMA_DIRECTORS_100
    from director_profiles_creative_ad import CREATIVE_AD_DIRECTORS_100
    from director_profiles_short_video import SHORT_VIDEO_DIRECTORS_100
    from director_profiles_animation import ANIMATION_DIRECTORS_100
    DIR_NAMES = (sorted([f"[电影] {n}" for n in FILM_DIRECTORS_100])
                 + sorted([f"[电视] {n}" for n in TV_DRAMA_DIRECTORS_100])
                 + sorted([f"[广告] {n}" for n in CREATIVE_AD_DIRECTORS_100])
                 + sorted([f"[短视频] {n}" for n in SHORT_VIDEO_DIRECTORS_100])
                 + sorted([f"[动画] {n}" for n in ANIMATION_DIRECTORS_100]))
    # V14.3 E5: 补全有档案但不在 5 域下拉的导演 (36 位大师: 王家卫/诺兰/黑泽明/宫崎骏…)
    #   下拉 = 档案全集, 不再只能靠模糊搜索触达。
    # V14.3 (审查P2修复): 动画大师按域贴 [动画] 前缀, 其余 [电影]。
    # V15.0-MERGED: 扩容池按池域前缀 (当代新锐→[电影], 跨界→[跨界], 非西方→[世界])。
    _ANIMATION_MASTERS = {"今敏", "宫崎骏", "押井守", "新海诚", "高畑勋", "大友克洋"}
    try:
        from director_profiles_extended import DIRECTORS_EXTENDED as _V15_EXT
    except ImportError:
        _V15_EXT = {}
    _POOL_TAG = {"当代新锐": "电影", "跨界": "跨界", "非西方": "世界"}

    def _tag_for(name):
        if name in _ANIMATION_MASTERS:
            return "动画"
        if name in _V15_EXT:
            return _POOL_TAG.get(_V15_EXT[name].get("pool", ""), "电影")
        return "电影"

    _in_dropdown = set(x.split("] ", 1)[1] for x in DIR_NAMES if "] " in x)
    _extra = sorted(set(DIRECTOR_PROFILES_ALL.keys()) - _in_dropdown)
    DIR_NAMES += [f"[{_tag_for(n)}] {n}" for n in _extra]
    DIR_NAMES = sorted(set(DIR_NAMES))
    if "[电影] 王家卫" in DIR_NAMES:
        DIR_NAMES.remove("[电影] 王家卫")
    DIR_NAMES = ["[电影] 王家卫"] + DIR_NAMES
except Exception:
    DIR_NAMES = ["[电影] 王家卫"]

SOUL_PRESETS = {"无(默认)":"","悲伤":"[灵魂注入]\n主导情感: 悲伤\n融合模式: 主导\n主导权重: 0.9\n创造力=0.9,想象力=0.9,艺术表达=0.95,镜头技巧=0.85,氛围掌控=0.9,灵感=0.8,疲劳=0.5,怀疑=0.6,叛逆=0.7,突破=0.85\n故事强度=0.8,场景进度=0.0",
    "孤独":"[灵魂注入]\n主导情感: 孤独\n融合模式: 主导\n主导权重: 0.95\n创造力=0.9,想象力=0.9,艺术表达=0.9,镜头技巧=0.9,氛围掌控=0.95,灵感=0.85,疲劳=0.4,怀疑=0.5,叛逆=0.8,突破=0.85\n故事强度=0.7,场景进度=0.0",
    "温暖":"[灵魂注入]\n主导情感: 温暖\n融合模式: 主导\n主导权重: 0.85\n创造力=0.85,想象力=0.85,艺术表达=0.9,镜头技巧=0.8,氛围掌控=0.9,灵感=0.9,疲劳=0.3,怀疑=0.3,叛逆=0.5,突破=0.8\n故事强度=0.6,场景进度=0.0",
    "怀旧":"[灵魂注入]\n主导情感: 怀旧\n融合模式: 平衡\n主导权重: 0.8\n创造力=0.85,想象力=0.9,艺术表达=0.9,镜头技巧=0.85,氛围掌控=0.9,灵感=0.85,疲劳=0.4,怀疑=0.5,叛逆=0.6,突破=0.75\n故事强度=0.7,场景进度=0.0",
    "愤怒":"[灵魂注入]\n主导情感: 愤怒\n融合模式: 主导\n主导权重: 0.95\n创造力=0.85,想象力=0.8,艺术表达=0.9,镜头技巧=0.85,氛围掌控=0.85,灵感=0.9,疲劳=0.5,怀疑=0.4,叛逆=0.95,突破=0.9\n故事强度=0.9,场景进度=0.0",
    "希望":"[灵魂注入]\n主导情感: 希望\n融合模式: 主导\n主导权重: 0.85\n创造力=0.9,想象力=0.95,艺术表达=0.9,镜头技巧=0.85,氛围掌控=0.85,灵感=0.95,疲劳=0.3,怀疑=0.3,叛逆=0.7,突破=0.9\n故事强度=0.85,场景进度=0.0",
    "史诗":"[灵魂注入]\n主导情感: 史诗\n融合模式: 平衡\n主导权重: 0.9\n创造力=0.95,想象力=0.95,艺术表达=0.9,镜头技巧=0.95,氛围掌控=0.95,灵感=0.9,疲劳=0.4,怀疑=0.3,叛逆=0.8,突破=0.95\n故事强度=0.95,场景进度=0.0",
    "悬疑":"[灵魂注入]\n主导情感: 悬疑\n融合模式: 主导\n主导权重: 0.9\n创造力=0.9,想象力=0.9,艺术表达=0.85,镜头技巧=0.9,氛围掌控=0.95,灵感=0.85,疲劳=0.4,怀疑=0.8,叛逆=0.7,突破=0.85\n故事强度=0.8,场景进度=0.1",
    "浪漫":"[灵魂注入]\n主导情感: 浪漫\n融合模式: 主导\n主导权重: 0.85\n创造力=0.9,想象力=0.95,艺术表达=0.95,镜头技巧=0.85,氛围掌控=0.9,灵感=0.9,疲劳=0.3,怀疑=0.3,叛逆=0.6,突破=0.8\n故事强度=0.7,场景进度=0.0",
    "宁静":"[灵魂注入]\n主导情感: 宁静\n融合模式: 主导\n主导权重: 0.8\n创造力=0.85,想象力=0.85,艺术表达=0.9,镜头技巧=0.8,氛围掌控=0.95,灵感=0.85,疲劳=0.3,怀疑=0.3,叛逆=0.4,突破=0.7\n故事强度=0.5,场景进度=0.0",
    "恐惧":"[灵魂注入]\n主导情感: 恐惧\n融合模式: 主导\n主导权重: 0.95\n创造力=0.85,想象力=0.9,艺术表达=0.85,镜头技巧=0.9,氛围掌控=0.95,灵感=0.8,疲劳=0.5,怀疑=0.7,叛逆=0.6,突破=0.85\n故事强度=0.85,场景进度=0.1",
}
SOUL_NAMES = list(SOUL_PRESETS.keys())

PARAM_PRESETS = {
    "默认(无覆盖)":"",
    # === V12.6 v13: 20 派别 ===
    "王家卫·城市孤独":'{"主导情感":"孤独","融合模式":"主导","主导权重":0.95,"创造力":0.9,"想象力":0.9,"艺术表达":0.95,"镜头技巧":0.9,"氛围掌控":0.95,"灵感指数":0.85,"叛逆指数":0.8,"调色风格":"梦幻","意图类型":"情感冲击","观众应感到":"城市孤独与时间流逝"}',
    "侯孝贤·长焦远景":'{"主导情感":"怀旧","融合模式":"主导","主导权重":0.9,"创造力":0.9,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.95,"氛围掌控":0.9,"灵感指数":0.85,"叛逆指数":0.6,"调色风格":"自然","意图类型":"诗意沉浸","观众应感到":"时间里的沉默与远望"}',
    "是枝裕和·家庭日常":'{"主导情感":"温暖","融合模式":"主导","主导权重":0.85,"创造力":0.9,"想象力":0.85,"艺术表达":0.95,"镜头技巧":0.85,"氛围掌控":0.9,"灵感指数":0.9,"叛逆指数":0.6,"调色风格":"暖色","意图类型":"情感冲击","观众应感到":"家庭与生命的温柔"}',
    "李安·文化冲突":'{"主导情感":"复杂","融合模式":"平衡","主导权重":0.85,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.9,"氛围掌控":0.9,"灵感指数":0.9,"叛逆指数":0.7,"调色风格":"对比","意图类型":"情感冲击","观众应感到":"理性与情感的撕扯"}',
    "贾樟柯·县城时代":'{"主导情感":"怀旧","融合模式":"平衡","主导权重":0.85,"创造力":0.9,"想象力":0.9,"艺术表达":0.95,"镜头技巧":0.85,"氛围掌控":0.9,"灵感指数":0.85,"叛逆指数":0.8,"调色风格":"灰调","意图类型":"时代纪录","观众应感到":"县城与时代的裹挟"}',
    "诺兰·叙事结构":'{"主导情感":"悬疑","融合模式":"平衡","主导权重":0.9,"创造力":0.95,"想象力":0.9,"艺术表达":0.85,"镜头技巧":0.95,"氛围掌控":0.85,"灵感指数":0.95,"叛逆指数":0.85,"调色风格":"冷色","意图类型":"叙事冲击","观众应感到":"时间与记忆的迷宫"}',
    "塔可夫斯基·诗意长镜":'{"主导情感":"宁静","融合模式":"主导","主导权重":0.85,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.95,"氛围掌控":0.95,"灵感指数":0.9,"叛逆指数":0.7,"调色风格":"暖色","意图类型":"诗意沉浸","观众应感到":"诗意与精神的流动"}',
    "希区柯克·悬念":'{"主导情感":"悬疑","融合模式":"主导","主导权重":0.95,"创造力":0.9,"想象力":0.85,"艺术表达":0.85,"镜头技巧":0.95,"氛围掌控":0.95,"灵感指数":0.85,"叛逆指数":0.8,"调色风格":"黑白","意图类型":"悬念冲击","观众应感到":"被偷窥的紧张"}',
    "黑泽明·史诗动态":'{"主导情感":"史诗","融合模式":"平衡","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.9,"镜头技巧":0.95,"氛围掌控":0.9,"灵感指数":0.95,"叛逆指数":0.85,"调色风格":"暖色","意图类型":"叙事冲击","观众应感到":"动与静的史诗张力"}',
    "库布里克·严谨对称":'{"主导情感":"悬疑","融合模式":"主导","主导权重":0.95,"创造力":0.95,"想象力":0.95,"艺术表达":0.9,"镜头技巧":0.95,"氛围掌控":0.95,"灵感指数":0.9,"叛逆指数":0.95,"调色风格":"冷色","意图类型":"叙事冲击","观众应感到":"秩序与失控的张力"}',
    "奉俊昊·类型混搭":'{"主导情感":"悬疑","融合模式":"平衡","主导权重":0.9,"创造力":0.95,"想象力":0.9,"艺术表达":0.9,"镜头技巧":0.9,"氛围掌控":0.9,"灵感指数":0.9,"叛逆指数":0.95,"调色风格":"冷色","意图类型":"类型反转","观众应感到":"阶级与人性的冲击"}',
    "贝拉·塔尔·一镜长跑":'{"主导情感":"压抑","融合模式":"主导","主导权重":0.95,"创造力":0.9,"想象力":0.9,"艺术表达":0.95,"镜头技巧":0.95,"氛围掌控":0.95,"灵感指数":0.8,"叛逆指数":0.9,"调色风格":"灰调","意图类型":"沉浸冲击","观众应感到":"世界末日般的延续"}',
    "阿巴斯·对话留白":'{"主导情感":"宁静","融合模式":"主导","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.85,"氛围掌控":0.95,"灵感指数":0.9,"叛逆指数":0.5,"调色风格":"自然","意图类型":"诗意对话","观众应感到":"生活的形而上"}',
    "泰伦斯·马力克·自然诗":'{"主导情感":"宁静","融合模式":"主导","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.9,"氛围掌控":0.95,"灵感指数":0.95,"叛逆指数":0.5,"调色风格":"金色","意图类型":"自然诗意","观众应感到":"光与存在的赞歌"}',
    "大卫·林奇·超现实":'{"主导情感":"恐惧","融合模式":"主导","主导权重":0.95,"创造力":0.95,"想象力":0.95,"艺术表达":0.9,"镜头技巧":0.85,"氛围掌控":0.95,"灵感指数":0.95,"叛逆指数":0.95,"调色风格":"诡异","意图类型":"超现实冲击","观众应感到":"梦与现实的边界崩塌"}',
    "奉俊昊·奉式反转":'{"主导情感":"愤怒","融合模式":"平衡","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.9,"镜头技巧":0.9,"氛围掌控":0.9,"灵感指数":0.95,"叛逆指数":0.95,"调色风格":"冷暖","意图类型":"社会冲击","观众应感到":"阶层的撞击"}',
    "陈凯歌·史诗古典":'{"主导情感":"史诗","融合模式":"主导","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.9,"氛围掌控":0.95,"灵感指数":0.9,"叛逆指数":0.75,"调色风格":"古色","意图类型":"古典史诗","观众应感到":"中国历史的回响"}',
    "宫崎骏·动画诗意":'{"主导情感":"希望","融合模式":"主导","主导权重":0.9,"创造力":0.95,"想象力":0.95,"艺术表达":0.95,"镜头技巧":0.85,"氛围掌控":0.9,"灵感指数":0.95,"叛逆指数":0.7,"调色风格":"梦幻","意图类型":"童心诗意","观众应感到":"童心与世界的和解"}',
    "朴赞郁·暴力美学":'{"主导情感":"愤怒","融合模式":"主导","主导权重":0.95,"创造力":0.9,"想象力":0.9,"艺术表达":0.9,"镜头技巧":0.95,"氛围掌控":0.85,"灵感指数":0.9,"叛逆指数":0.95,"调色风格":"高对比","意图类型":"暴力美学","观众应感到":"暴力的诗意与残酷"}',
    "是枝裕和·死亡家庭":'{"主导情感":"悲伤","融合模式":"主导","主导权重":0.85,"创造力":0.9,"想象力":0.85,"艺术表达":0.95,"镜头技巧":0.85,"氛围掌控":0.95,"灵感指数":0.85,"叛逆指数":0.5,"调色风格":"低饱和","意图类型":"家庭哀歌","观众应感到":"家庭中的死亡与告别"}',
}
PARAM_NAMES = list(PARAM_PRESETS.keys())

# V16.0 需求1: Core 属性下拉选项常量 (供 INPUT_TYPES 与 build 随机解析共用)
_RND = "🎲 随机"
CORE_YEAR_OPTS = ["现代","80年代","90年代","2000s","2010s","2020s","未来","架空/奇幻","历史(1900前)"]
CORE_SEASON_OPTS = ["春","夏","秋","冬","不明"]
CORE_CULTURE_OPTS = ["中国都市","中国乡镇","日韩","欧美","拉丁","中东","北欧","东南亚","其他"]
CORE_PLATFORM_OPTS = ["院线长片","流媒体","短视频","竖屏短剧","广告/MV","电视连续剧","网络剧","实验短片"]
CORE_AUDIENCE_OPTS = ["全年龄","年轻向(15-30)","25-45岁都市","中老年","合家欢","文艺向","二次元","垂类(科幻/悬疑/古装)"]
CORE_BUDGET_OPTS = ["独立低成本","中等制作","商业大片","A+级(亿元+)","低成本爆款"]
CORE_RUNTIME_OPTS = ["3-5分钟短片","8-15分钟","30-60分钟","90分钟","120分钟+","系列(总60+)"]
CORE_ASPECT_OPTS = ["2.39:1 宽银幕","1.85:1 院线","16:9 流媒体","9:16 竖屏","1:1 方形","4:3 经典","2:1 现代宽屏"]
CORE_CONFLICT_OPTS = ["爱","复仇","救赎","成长","生存","家庭","自由","身份","孤独","战争","阶级","欲望"]
CORE_THEME_OPTS = ["孤独","爱","希望","绝望","救赎","成长","寻找","失去","自由","时间","记忆","死亡"]
CORE_MOOD_OPTS = ["孤独","温暖","悲伤","愤怒","希望","史诗","悬疑","浪漫","宁静","恐惧","怀旧","喜剧"]
CORE_VISUAL_OPTS = ["写实","梦幻","赛博朋克","复古胶片","黑白","水彩","油画","水墨","高饱和","低饱和","霓虹","暖色","冷色"]
CORE_SUBTEXT_OPTS = ["无","弱","中","强","极强(字字有潜文本)"]
CORE_PROMISE_OPTS = ["感动落泪","爆笑","震撼","治愈","深度思考","烧脑反转","肾上腺素","沉浸诗意","余味悠长"]


class DirectorMasterCore(DirectorNodeBase):
    """V12.6 起点节点 — 世界级导演总控. 32 输入参数 + 2 输出 (统一电影提示词 + 核心数据包)."""
    NODE_TYPE = "核心"

    @classmethod
    def INPUT_TYPES(cls):
        # V12.6 v7 fix: 所有下拉框加 "无(默认)" 首项 (兼容老版本 saved workflow 错配)
        _NO_DEFAULT = "无(默认)"
        return {"required": {
            "项目名": ("STRING", {"default": "沉默的凤梨",
                "tooltip": "★ 项目名称 → 写入所有下游输出头部"}),
            "随机种子": ("INT", {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True,
                "tooltip": "🎲 随机引擎: 0 = 每次执行真随机 (OS熵; 前端 randomize 控件每次排队自动换新种子); >0 = 固定种子完全可复现。本节点与全部下游节点的 🎲 随机选项均由它驱动"}),
            "导演名": (DIR_NAMES + [_RND], {"default": "[电影] 王家卫",
                "tooltip": "★ 600 导演库, 选导演即锁定其风格档案; 🎲 随机 = 由随机种子驱动选一位导演 (种子0每次运行换导演, 固定种子可复现)"}),
            "导演名_自定义": ("STRING", {"default": "",
                "tooltip": "可选. 填写后覆盖下拉, 支持 600 导演模糊搜索"}),
            "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998年哈尔滨, 父亲切菜, 女儿坐桌边, 桌上有凤梨罐头和旧信", "multiline": True,
                "tooltip": "★ 核心场景, 1-3 句话"}),
            "时间年代": ([_NO_DEFAULT,_RND]+CORE_YEAR_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 时间年代 → 决定服化道/语言习惯/视觉风格"}),
            "季节": ([_NO_DEFAULT,_RND]+CORE_SEASON_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 季节 → 决定光影/色彩/环境音"}),
            "地区文化": ([_NO_DEFAULT,_RND]+CORE_CULTURE_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 地区文化 → 决定空间/服化道/语言风格"}),
            "平台媒介": ([_NO_DEFAULT,_RND]+CORE_PLATFORM_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 平台 → 决定叙事节奏/视觉规格/市场卖点"}),
            "目标受众": ([_NO_DEFAULT,_RND]+CORE_AUDIENCE_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 受众 → 决定情感浓度/节奏/对白密度"}),
            "预算级别": ([_NO_DEFAULT,_RND]+CORE_BUDGET_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 预算 → 决定调度规模/特效/场景数"}),
            "成片时长": ([_NO_DEFAULT,_RND]+CORE_RUNTIME_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 时长 → 决定场次/节奏/情节点数"}),
            "画幅比例": ([_NO_DEFAULT,_RND]+CORE_ASPECT_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 画幅 → 决定构图法则/视觉重量"}),
            "核心冲突": ([_NO_DEFAULT,_RND]+CORE_CONFLICT_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 核心冲突 → 决定三幕结构的对抗轴"}),
            "主题词": ([_NO_DEFAULT,_RND]+CORE_THEME_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 主题词 → 决定潜台词/意象系统"}),
            "情绪基调": ([_NO_DEFAULT,_RND]+CORE_MOOD_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 情绪 → 注入灵魂预设 (10 维参数)"}),
            "视觉调性": ([_NO_DEFAULT,_RND]+CORE_VISUAL_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 视觉调性 → 决定色彩/光影/材质"}),
            "潜文本强度": ([_NO_DEFAULT,_RND]+CORE_SUBTEXT_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 潜文本 → 决定对白/动作/物件的隐藏意义密度"}),
            "观众承诺": ([_NO_DEFAULT,_RND]+CORE_PROMISE_OPTS, {"default": _NO_DEFAULT,
                "tooltip": "★ 观众承诺 → 决定全片情绪走向"}),
            "对标作品": ("STRING", {"default": "《饮食男女》×《花样年华》×《小偷家族》", "multiline": True,
                "tooltip": "★ 对标作品 → 用户/创作者直接给出, 覆盖 Vibe 输出"}),
            "关键道具": ("STRING", {"default": "凤梨罐头(过期15年), 旧信(泛黄, 妈妈字迹), 钢笔(没墨水), 收音机", "multiline": True,
                "tooltip": "★ 物件 → 叙事载体, 每件承载一个情感功能"}),
            "潜文本_情感": ("STRING", {"default": "父亲用切菜掩盖情绪; 女儿用沉默回应", "multiline": True,
                "tooltip": "★ 潜文本描述 → 注入对白/动作的隐藏情感层"}),
            "启用反AI规则": ("BOOLEAN", {"default": True,
                "tooltip": "★ 禁用 masterpiece/8K/HDR/cinematic lighting 等 AI 套话"}),
            "导演意图_观众应感到": ("STRING", {"default": "心酸却温暖, 说不出口的爱, 留白中见深情", "multiline": True,
                "tooltip": "★ 导演对观众的最终情感指令"}),
        }, "optional": {
            "情绪基调_演变": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ V13.2 多选: 情绪随情节推进演变, 用 逗号/箭头 分隔, 顺序即叙事顺序。例: '压抑→爆发→释然' — 第一幕压抑, 高潮爆发, 结尾释然。留空 = 用上方单选情绪基调贯穿全片"}),
            "视觉调性_混合": ("STRING", {"default": "", "multiline": True,
                "tooltip": "★ V13.2 多选: 多种视觉调性混合/演变, 用 逗号/箭头 分隔。例: '写实→梦幻' 或 '复古胶片, 霓虹'。留空 = 用上方单选视觉调性"}),
            "叙事编排": ([_NO_DEFAULT, _RND] + [m for m in ARRANGEMENT_MODES if m != "跟随叙事结构"], {
                "default": _NO_DEFAULT,
                "tooltip": "★ V16.1 叙事编排 — 打包进核心数据包, 下游剧本/分镜节点继承。正叙/倒叙(结果先行)/穿插倒叙/穿插乱叙/循环叙事。留空=跟随叙事结构"}),
            "叙事线型": ([_NO_DEFAULT, _RND] + [m for m in NARRATIVE_LINE_MODES if m != "单线"], {
                "default": _NO_DEFAULT,
                "tooltip": "★ V16.1 叙事线型 — 打包进核心数据包, 下游继承。双线并行/三线交织/POV切换。留空=单线"}),
            "参数预设": (["默认(无覆盖)", _RND] + PARAM_NAMES, {"default": "默认(无覆盖)",
                "tooltip": "可选. 选导演级预设 (王家卫/诺兰/塔可夫斯基/是枝裕和/奉俊昊/库布里克/黑泽明); 🎲 随机"}),
            "高级参数JSON": ("STRING", {"default": "", "multiline": True,
                "tooltip": "高级参数 JSON, 覆盖预设"}),
            "灵魂预设": (["无(默认)", _RND] + SOUL_NAMES, {"default": "无(默认)",
                "tooltip": "选情绪→自动注入 10 维灵魂参数; 🎲 随机"}),
            "灵魂注入_自定义": ("STRING", {"default": "", "multiline": True,
                "tooltip": "自定义灵魂注入 (创造力=0.9, 想象力=0.85, ...)"}),
            "AI接口地址": ("STRING", {"default": "",
                "tooltip": "★ 唯一 AI 配置入口. 填写后打包进核心数据包, 10 个下游节点 0 AI 字段自动继承"}),
            "AI密钥": ("STRING", {"default": ""}),
            "AI模型名": ("STRING", {"default": "gpt-4o",
                "tooltip": "gpt-4o/qwen-max/deepseek-chat/glm-4 等"}),
        }}

    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("统一电影提示词","核心数据包")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/聚合/起点"

    def build(self, **kwargs):
        import re as _re
        import random as _rng_mod
        # V16.3: 🎲 随机引擎统一由 随机种子 输入驱动, 修复 V16.1 "同输入恒定输出"导致的随机名不副实
        #   (final_capability_audit 4 项失败的根因):
        #   0 = 每次执行 OS 熵真随机 (诚实随机; 前端 randomize 控件每次排队换新种子值,
        #       IS_CHANGED 输入哈希随之变化 → 触发真实重算);
        #   >0 = 该值即种子, 同输入完全可复现 (保留 V16.1 的可复现能力, 显式可选)。
        _seed_in = kwargs.get("随机种子", 0)
        try:
            _seed_in = int(_seed_in)
        except (TypeError, ValueError):
            _seed_in = 0
        if _seed_in > 0:
            _seed_val = _seed_in % (2 ** 31)
        else:
            _seed_val = _rng_mod.SystemRandom().getrandbits(31)
        _rng = _rng_mod.Random(_seed_val)

        # 提取全部 32 字段 (V12.6 v7 fix2: "无(默认)" 映射到 V9.5 默认值)
        # V16.0 需求1: _resolve 支持 🎲 随机 — 传入 options 时随机选一个真实值
        def _resolve(v, default, options=None):
            if v == "🎲 随机" and options:
                real = [o for o in options if o not in ("无(默认)", "🎲 随机", "", "默认(无覆盖)")]
                if real:
                    return _rng.choice(real)
                return default
            if v == "无(默认)" or not v: return default
            return v
        project = _resolve(kwargs.get("项目名"), "未命名项目")
        scene = kwargs.get("场景描述","")
        # V14.3-MERGED: 场景留空 → pln_random 按项目名确定性种子生成灵感场景 (复活接线)
        if not str(scene).strip():
            try:
                import random as _rnd_c
                import hashlib as _hl_c
                from pln_random import random_topic, random_character, random_env
                _seed = int(_hl_c.md5(str(project).encode("utf-8", "replace")).hexdigest(), 16) % (2 ** 32)
                _st = _rnd_c.getstate()
                _rnd_c.seed(_seed)
                _tp = random_topic("电影分镜")
                scene = f"{random_character('电影分镜', _tp)}, 主题: {_tp}, 环境: {random_env('电影分镜', _tp)}"
                _rnd_c.setstate(_st)
            except Exception:
                scene = "主角在雨夜的街头, 霓虹灯倒映在积水中"
        mood = _resolve(kwargs.get("情绪基调"), "孤独", CORE_MOOD_OPTS)
        intent = _resolve(kwargs.get("导演意图_观众应感到"), "")
        anti_ai = kwargs.get("启用反AI规则",True)
        # V13.2: 多选/演变序列 — 留空则用单选值贯穿全片
        mood_arc = parse_multi_select(kwargs.get("情绪基调_演变", ""), default=mood)
        year = _resolve(kwargs.get("时间年代"), "90年代", CORE_YEAR_OPTS)
        season = _resolve(kwargs.get("季节"), "冬", CORE_SEASON_OPTS)
        culture = _resolve(kwargs.get("地区文化"), "中国都市", CORE_CULTURE_OPTS)
        platform = _resolve(kwargs.get("平台媒介"), "院线长片", CORE_PLATFORM_OPTS)
        audience = _resolve(kwargs.get("目标受众"), "25-45岁都市", CORE_AUDIENCE_OPTS)
        budget = _resolve(kwargs.get("预算级别"), "中等制作", CORE_BUDGET_OPTS)
        runtime = _resolve(kwargs.get("成片时长"), "90分钟", CORE_RUNTIME_OPTS)
        aspect = _resolve(kwargs.get("画幅比例"), "1.85:1 院线", CORE_ASPECT_OPTS)
        conflict = _resolve(kwargs.get("核心冲突"), "家庭", CORE_CONFLICT_OPTS)
        theme = _resolve(kwargs.get("主题词"), "孤独", CORE_THEME_OPTS)
        visual = _resolve(kwargs.get("视觉调性"), "梦幻", CORE_VISUAL_OPTS)
        visual_arc = parse_multi_select(kwargs.get("视觉调性_混合", ""), default=visual)
        subtext_strength = _resolve(kwargs.get("潜文本强度"), "强", CORE_SUBTEXT_OPTS)
        promise = _resolve(kwargs.get("观众承诺"), "感动落泪", CORE_PROMISE_OPTS)
        ref_films = kwargs.get("对标作品","")
        props = kwargs.get("关键道具","")
        subtext_desc = kwargs.get("潜文本_情感","")
        mode = "标准"

        # V16.1: 叙事编排 + 叙事线型 (打包进核心数据包, 下游继承)
        _ARRANGE_OPTS = [m for m in ARRANGEMENT_MODES if m != "跟随叙事结构"]
        _LINE_OPTS = [m for m in NARRATIVE_LINE_MODES if m != "单线"]
        narrative_arrangement = _resolve(kwargs.get("叙事编排"), "跟随叙事结构", _ARRANGE_OPTS)
        narrative_line = _resolve(kwargs.get("叙事线型"), "单线", _LINE_OPTS)

        # 导演选择 (V16.0 需求1: 支持 🎲 随机; V16.1 改用确定性种子)
        custom = (kwargs.get("导演名_自定义") or "").strip()
        if custom:
            director = match_director_fuzzy(custom)
        else:
            dname = kwargs.get("导演名","[电影] 王家卫")
            if dname == "🎲 随机":
                dname = _rng.choice(DIR_NAMES)
            director = dname.split("] ",1)[1] if "] " in dname else dname

        # 灵魂注入 (V16.0 需求1: 灵魂预设支持 🎲 随机; V16.1 改用确定性种子)
        raw_soul = (kwargs.get("灵魂注入_自定义") or "").strip()
        if not raw_soul:
            _soul_preset = kwargs.get("灵魂预设","无(默认)")
            if _soul_preset == "🎲 随机":
                _soul_preset = _rng.choice([s for s in SOUL_NAMES if s != "无(默认)"])
            raw_soul = SOUL_PRESETS.get(_soul_preset,"")
        # 解析灵魂注入
        soul_vals = {}
        if raw_soul:
            for line in raw_soul.split("\n"):
                m = _re.match(r"(\S+)=([\d.]+)", line)
                if m:
                    soul_vals[m.group(1)] = float(m.group(2))
                    continue
                m = _re.match(r"(\S+):\s*(.+)", line)
                if m:
                    soul_vals[m.group(1)] = m.group(2).strip()

        # 参数预设 (V16.0 需求1: 支持 🎲 随机; V16.1 改用确定性种子)
        _param_preset = kwargs.get("参数预设","默认(无覆盖)")
        if _param_preset == "🎲 随机":
            _param_preset = _rng.choice([p for p in PARAM_NAMES if p != "默认(无覆盖)"])
        param_json = PARAM_PRESETS.get(_param_preset,"")
        extra = {}
        if param_json:
            try: extra = _json.loads(param_json)
            except Exception as _e_pp:
                # V16.1.1 审计修复 L-8: 不再静默吞 JSON 解析错误
                _sys.stderr.write("[DirectorMaster] 参数预设JSON解析失败, 回落默认: {}\n".format(str(_e_pp)[:100]))
        user_json = kwargs.get("高级参数JSON","")
        if user_json:
            try: extra.update(_json.loads(user_json))
            except Exception as _e_uj:
                _sys.stderr.write("[DirectorMaster] 高级参数JSON解析失败, 回落默认: {}\n".format(str(_e_uj)[:100]))

        # 构建 10 维参数
        c = extra.get("创造力", soul_vals.get("创造力",0.85))
        im = extra.get("想象力", soul_vals.get("想象力",0.85))
        ae = extra.get("艺术表达", soul_vals.get("艺术表达",0.85))
        cs = extra.get("镜头技巧", soul_vals.get("镜头技巧",0.85))
        ac = extra.get("氛围掌控", soul_vals.get("氛围掌控",0.85))
        insp = extra.get("灵感指数", soul_vals.get("灵感",soul_vals.get("灵感指数",0.85)))
        fat = extra.get("疲劳指数", soul_vals.get("疲劳",soul_vals.get("疲劳指数",0.3)))
        dbt = extra.get("怀疑指数", soul_vals.get("怀疑",soul_vals.get("怀疑指数",0.5)))
        reb = extra.get("叛逆指数", soul_vals.get("叛逆",soul_vals.get("叛逆指数",0.7)))
        brk = extra.get("突破勇气", soul_vals.get("突破",soul_vals.get("突破勇气",0.85)))
        story = extra.get("故事强度", soul_vals.get("故事强度",0.5))
        progress = extra.get("场景进度", soul_vals.get("场景进度",0.0))
        dominant = extra.get("主导情感", soul_vals.get("主导情感","auto"))
        fusion = extra.get("融合模式", soul_vals.get("融合模式","auto"))
        weight = extra.get("主导权重", soul_vals.get("主导权重",1.0))
        color = extra.get("调色风格","梦幻")
        intent_type = extra.get("意图类型","情感冲击")
        feel = extra.get("观众应感到", intent)

        # 灵魂注入串
        soul_text = (
            f"[灵魂注入]\n主导情感: {dominant}\n"
            f"次要情感: none, none, none, none\n融合模式: {fusion}\n主导权重: {weight}\n"
            f"10 灵魂维度: 创造力={c}, 想象力={im}, 艺术表达={ae}, 镜头技巧={cs}, "
            f"氛围掌控={ac}, 灵感={insp}, 疲劳={fat}, 怀疑={dbt}, 叛逆={reb}, 突破={brk}\n"
            f"灵魂状态: 故事强度={story}, 场景进度={progress}\n导演: {director}"
        )

        # 审美判断
        aesthetic = (
            f"【8原则审美判断】\n导演: {director}\n场景: {scene}\n色调: {color}\n"
            f"1.主体明确: 场景核心人物/道具清晰\n2.光影层次: 9D光影设计\n"
            f"3.色彩节制: 60-30-10配比\n4.构图张力: 9构图法则\n"
            f"5.情绪留白: 留白比例30%\n6.节奏控制: 导演风格节奏\n"
            f"7.细节真实: 物件/材质/年代具体\n8.反AI: 禁用AI套话"
        )

        # 风格指南
        style = (
            f"【风格指南】\n导演体系: {director}\n调色风格: {color}\n"
            f"色彩口诀: 60%主色+30%辅色+10%点缀色\n"
            f"配色方案: 互补色\n包含调色口诀: 是\n包含调色盘: 是"
        )

        # 导演意图
        director_intent = f"【导演意图】\n类型: {intent_type}\n观众应感到: {feel}\n场景: {scene}"

        # 统一电影提示词 — 32 字段全量打包
        # V13.2: 多选演变弧 — 多值时在提示词中显式呈现叙事演变
        mood_arc_line = ""
        if len(mood_arc) > 1:
            mood_arc_line = f"情绪演变弧: {' → '.join(mood_arc)} (按叙事进度推进)\n"
        visual_arc_line = ""
        if len(visual_arc) > 1:
            visual_arc_line = f"视觉调性混合: {' + '.join(visual_arc)}\n"

        prompt = (
            f"【统一电影提示词】项目: {project}\n导演: {director}\n"
            f"场景: {scene}\n年代: {year} / 季节: {season} / 地区: {culture}\n"
            f"平台: {platform} | 受众: {audience} | 预算: {budget} | 时长: {runtime} | 画幅: {aspect}\n"
            f"情绪: {mood} | 核心冲突: {conflict} | 主题: {theme} | 视觉: {visual} | 潜文本: {subtext_strength}\n"
            f"{mood_arc_line}{visual_arc_line}"
            f"观众承诺: {promise} | 观众应感到: {intent}\n"
            f"对标: {ref_films}\n"
            f"关键道具: {props}\n"
            f"潜文本: {subtext_desc}\n"
            f"=== 灵魂参数 ===\n{soul_text}\n"
            f"=== 导演要求 ===\n"
            f"1. 以 {director} 的导演风格创作 ({year} {culture})\n"
            f"2. 情绪基调: {mood}, 核心冲突: {conflict}, 主题: {theme}\n"
            f"3. 受众: {audience}, 平台: {platform}, 时长: {runtime}\n"
            f"4. 视觉: {visual}, 潜文本强度: {subtext_strength}\n"
            f"5. 物件: {props}\n"
            f"6. 观众应感到: {intent}\n"
            f"7. 用五感细节, 禁用AI套话\n"
        )

        # 导演签名
        sig = f"【导演签名】{director} — {year} {season} {culture} | {color}调色 | {visual}视觉 | {aspect} | 反AI清理"

        # 反AI清理后
        cleaned = f"【反AI清理后】\n{prompt}\n(已移除: masterpiece/best quality/ultra detailed/4K/8K/HDR/cinematic lighting)"

        # 灵魂维度
        dims = f"创造力={c}, 想象力={im}, 艺术表达={ae}, 镜头技巧={cs}, 氛围掌控={ac}, 灵感={insp}, 疲劳={fat}, 怀疑={dbt}, 叛逆={reb}, 突破={brk}"

        # 8原则
        principles = "8原则基础评分: 主体明确/光影层次/色彩节制/构图张力/情绪留白/节奏控制/细节真实/反AI"

        # 色板
        palette = f"色板: 60-30-10 ({visual} 视觉, {color} 调色)"

        # 注入导演 12 维档案到统一电影提示词 (世界级导演能力)
        prompt += self._director_block(director)

        # AI 增强统一电影提示词
        api_url = (kwargs.get("AI接口地址") or "").strip()
        api_key = (kwargs.get("AI密钥") or "").strip()
        ai_model = (kwargs.get("AI模型名") or "").strip()
        if api_url:
            prompt = self._ensure_ai_output(prompt,
                {"node_type":"核心","mode":mode,"director":director,"scene":scene,"mood":mood,
                 "intent":intent,"year":year,"platform":platform,"audience":audience,
                 "conflict":conflict,"theme":theme,"visual":visual,"promise":promise},
                api_url, api_key, ai_model)

        # 核心数据包: 全部 32 字段折进, 单线分发给所有下游 (V12.6 强化版)
        core_pack = _json.dumps({
            # === 11 个 V12.6 核心能力块 ===
            "灵魂注入_整合": soul_text, "审美判断": aesthetic, "风格指南": style,
            "导演意图": director_intent, "统一电影提示词": prompt, "导演签名": sig,
            "反AI清理后": cleaned, "灵魂维度": dims, "8原则评分": principles, "色板": palette,
            "对标作品解析": ref_films,
            # === V12.6 新增 13 个导演级字段 (32 字段全量) ===
            "_项目名": project,
            "_场景描述": scene, "_导演风格": director, "_启用反AI规则": anti_ai,
            "_情绪基调": mood, "_情绪演变弧": mood_arc, "_导演意图_观众应感到": intent,
            "_时间年代": year, "_季节": season, "_地区文化": culture,
            "_平台媒介": platform, "_目标受众": audience, "_预算级别": budget,
            "_成片时长": runtime, "_画幅比例": aspect,
            "_核心冲突": conflict, "_主题词": theme, "_视觉调性": visual, "_视觉调性弧": visual_arc,
            "_潜文本强度": subtext_strength, "_观众承诺": promise,
            "_对标作品": ref_films, "_关键道具": props, "_潜文本_情感": subtext_desc,
            # === V16.1 叙事编排 (下游剧本/分镜节点继承) ===
            "_叙事编排": narrative_arrangement, "_叙事线型": narrative_line,
            # === V16.3 随机引擎种子 (下游全部 🎲 随机由它派生, 固定种子时全链可复现) ===
            "_随机种子": _seed_val,
            # === AI 配置 (★ 用户唯一 AI 入口) ===
            "_ai_api_url": api_url, "_ai_api_key": api_key, "_ai_api_model": ai_model,
        }, ensure_ascii=False)

        return (prompt, core_pack)