# ============================================================
# 世界级导演引擎 V2.0 — 知识库驱动 + 故事前文系统
# ============================================================
# 核心升级:
#   1. 知识库驱动: 从10个专业知识模块中实时查询最佳实践
#   2. 故事前文系统: 每个分镜输出前携带前面故事大纲(用户核心需求)
#   3. 导演风格引擎: 根据类型自动选取导演风格组合
#   4. 情感渲染引擎: 精确到表情/肢体/环境联动的情绪描述
#   5. 镜头语汇系统: 从镜头类型到心理效果的精确映射
# ============================================================
import os
import sys
import random

_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

from knowledge_base.master_cinematography import MASTER_CINEMATOGRAPHY
from knowledge_base.narrative_structures import NARRATIVE_STRUCTURES, SHORT_FORM_STRUCTURES
from knowledge_base.genre_profiles import GENRE_PROFILES
from knowledge_base.performance_system import PERFORMANCE_SYSTEM
from knowledge_base.short_drama_patterns import SHORT_DRAMA_PATTERNS
from knowledge_base.viral_video_techniques import VIRAL_VIDEO_TECHNIQUES
from knowledge_base.director_styles import DIRECTOR_STYLES
from knowledge_base.emotion_rendering import EMOTION_RENDERING
from knowledge_base.transition_grammar import TRANSITION_GRAMMAR
from knowledge_base.shot_vocabulary import SHOT_VOCABULARY


# ============================================================
# 风格映射: 用户选择 → 知识库genre_key
# ============================================================
STYLE_TO_GENRE = {
    "电影感": None,
    "古装风": "period_costume",
    "喜剧风": "comedy_humor",
    "言情风": "romance_sweet",
    "悬疑风": "suspense_thriller",
    "科幻风": "sci_fi",
    "奇幻风": "mythology_fantasy",
    "武侠风": "wuxia_martial_arts",
    "宫廷风": "period_costume",
    "都市风": "urban_modern",
    "民国风": "period_costume",
    "田园风": "pastoral_idyllic",
    "赛博风": "cyberpunk",
    "蒸汽朋克风": "sci_fi",
    "末日废土风": "survival",
    "校园风": "urban_modern",
    "职场风": "urban_modern",
    "家庭温情风": "family_warmth",
    "史诗正剧风": "war_epic",
    "文艺叙事风": "pastoral_idyllic",
    "黑色幽默风": "noir",
    "实验先锋风": "psychological",
    "纪录写实风": "documentary_style",
    "神话史诗风": "mythology_fantasy",
    "惊悚恐怖风": "horror",
    "动作爆裂风": "action_combat",
    "犯罪黑帮风": "noir",
    "历史传记风": "period_costume",
    "短视频创意风": None,
    "竖屏短剧风": None,
}

STYLE_TO_DIRECTORS = {
    "电影感": ["spielberg", "nolan", "fincher"],
    "古装风": ["zhang_yimou", "chen_kaige", "ang_lee"],
    "喜剧风": ["wes_anderson", "chaplin", "billy_wilder"],
    "言情风": ["wong_kar_wai", "ang_lee", "makoto_shinkai"],
    "悬疑风": ["hitchcock", "fincher", "park_chan_wook", "polanski"],
    "科幻风": ["villeneuve", "kubrick", "ridley_scott", "guo_fan"],
    "奇幻风": ["hayao_miyazaki", "guillermo_del_toro", "zhang_yimou"],
    "武侠风": ["tsui_hark", "john_woo", "ang_lee", "zhang_yimou"],
    "宫廷风": ["zhang_yimou", "chen_kaige", "park_chan_wook"],
    "都市风": ["wong_kar_wai", "bong_joon_ho", "michael_mann", "kore_eda"],
    "田园风": ["hayao_miyazaki", "kore_eda", "terrence_malick", "ozu"],
    "史诗正剧风": ["spielberg", "villeneuve", "david_lean", "coppola"],
    "黑色幽默风": ["coen_brothers", "tarantino", "bong_joon_ho"],
    "神话史诗风": ["zhang_yimou", "villeneuve", "david_lean"],
    "赛博风": ["ridley_scott", "michael_mann", "satoshi_kon"],
    "蒸汽朋克风": ["guillermo_del_toro", "wes_anderson"],
    "末日废土风": ["george_miller", "guo_fan", "alejandro_inarritu"],
    "校园风": ["makoto_shinkai", "kore_eda", "fernando_meirelles"],
    "职场风": ["michael_mann", "fincher", "bong_joon_ho"],
    "家庭温情风": ["kore_eda", "ozu", "ang_lee", "hayao_miyazaki"],
    "文艺叙事风": ["wong_kar_wai", "hou_hsiao_hsien", "tarkovsky", "kore_eda"],
    "实验先锋风": ["darren_aronofsky", "alejandro_inarritu", "satoshi_kon"],
    "纪录写实风": ["fernando_meirelles", "alfonso_cuaron", "brandon_li"],
    "民国风": ["wong_kar_wai", "ang_lee", "johnnie_to"],
    "惊悚恐怖风": ["kubrick", "ari_aster", "jordan_peele", "polanski"],
    "动作爆裂风": ["george_miller", "john_woo", "tsui_hark"],
    "犯罪黑帮风": ["scorsese", "coppola", "johnnie_to", "tarantino"],
    "历史传记风": ["spielberg", "ridley_scott", "pt_anderson", "chen_kaige"],
    "短视频创意风": ["zach_king", "sam_kolder", "brandon_li"],
    "竖屏短剧风": ["yan_xiaodi", "jiang_shiqi", "liu_xunzimo"],
}

# 类型片→导演推荐(IMDB类型经验证)
GENRE_TO_DIRECTORS = {
    "suspense_thriller": ["hitchcock", "fincher", "park_chan_wook", "polanski"],
    "action_combat": ["george_miller", "john_woo", "tsui_hark", "kurosawa"],
    "war_epic": ["spielberg", "villeneuve", "david_lean", "ridley_scott"],
    "mythology_fantasy": ["hayao_miyazaki", "guillermo_del_toro", "zhang_yimou"],
    "xianxia_cultivation": ["tsui_hark", "zhang_yimou", "chen_kaige"],
    "romance_sweet": ["wong_kar_wai", "ang_lee", "makoto_shinkai"],
    "comedy_humor": ["wes_anderson", "chaplin", "billy_wilder", "tarantino"],
    "sci_fi": ["villeneuve", "kubrick", "ridley_scott", "guo_fan"],
    "period_costume": ["zhang_yimou", "chen_kaige", "ang_lee"],
    "horror": ["kubrick", "ari_aster", "jordan_peele", "polanski"],
    "urban_modern": ["wong_kar_wai", "bong_joon_ho", "michael_mann"],
    "pastoral_idyllic": ["kore_eda", "hayao_miyazaki", "terrence_malick", "ozu"],
    "time_travel": ["nolan", "satoshi_kon", "robert_zemeckis"],
    "cyberpunk": ["ridley_scott", "michael_mann", "satoshi_kon"],
    "wuxia_martial_arts": ["tsui_hark", "john_woo", "ang_lee", "kurosawa"],
    "psychological": ["darren_aronofsky", "bergman", "polanski", "fincher"],
    "noir": ["billy_wilder", "polanski", "coen_brothers"],
    "musical": ["damien_chazelle"],
    "survival": ["alejandro_inarritu", "alfonso_cuaron", "ridley_scott"],
    "revenge": ["park_chan_wook", "tarantino", "sergio_leone"],
}


# ============================================================
# 导演→叙事结构亲和度(每位导演偏好的叙事方法)
# ============================================================
DIRECTOR_NARRATIVE_AFFINITY = {
    "tarantino": ["nonlinear", "in_medias_res"],          # 章节+打乱时间
    "nolan": ["nonlinear", "in_medias_res", "parallel_convergence"],  # 时间交叉
    "hitchcock": ["mystery_reveal", "classic_three_act"], # 悬疑揭秘
    "scorsese": ["descent_redemption"],                   # 男性沉沦救赎
    "spielberg": ["hero_journey", "save_the_cat"],        # 英雄之旅/商业节拍
    "kubrick": ["kishōtenketsu", "classic_three_act"],    # 起承转合/冷峻
    "wong_kar_wai": ["kishōtenketsu", "emotional_rollercoaster"],  # 情绪流
    "park_chan_wook": ["buildup_payoff", "mystery_reveal"],  # 复仇伏笔回收
    "bong_joon_ho": ["classic_three_act", "mystery_reveal"],  # 类型杂糅
    "villeneuve": ["mystery_reveal", "classic_three_act"],  # 沉浸揭秘
    "coen_brothers": ["kishōtenketsu", "descent_redemption"],  # 荒诞宿命
    "wes_anderson": ["kishōtenketsu", "save_the_cat"],    # 章节式起承转合
    "pt_anderson": ["descent_redemption", "nonlinear"],   # 雄心沉沦
    "fellini": ["kishōtenketsu", "nonlinear"],            # 梦境流
    "tarkovsky": ["kishōtenketsu"],                       # 诗性时间
    "bergman": ["kishōtenketsu", "descent_redemption"],  # 灵魂解剖
    "kurosawa": ["hero_journey", "classic_three_act"],   # 武士史诗
    "coppola": ["descent_redemption", "classic_three_act"],  # 家族悲剧
    "darren_aronofsky": ["descent_redemption", "emotional_rollercoaster"],  # 沉沦螺旋
    "alejandro_inarritu": ["nonlinear", "parallel_convergence"],  # 多线交织
    "alfonso_cuaron": ["classic_three_act", "kishōtenketsu"],
    "guillermo_del_toro": ["hero_journey", "kishōtenketsu"],  # 童话英雄
    "george_miller": ["classic_three_act", "hero_journey"],  # 极简公路史诗
    "damien_chazelle": ["classic_three_act", "descent_redemption"],  # 野心代价
    "jordan_peele": ["mystery_reveal", "buildup_payoff"],  # 社会悬疑
    "ari_aster": ["descent_redemption", "buildup_payoff"],  # 家族创伤
    "frank_darabont": ["classic_three_act", "hero_journey"],  # 希望救赎
    "robert_zemeckis": ["hero_journey", "classic_three_act"],
    "james_cameron": ["hero_journey", "classic_three_act"],
    "chen_kaige": ["kishōtenketsu", "classic_three_act"],  # 文化史诗
    "ang_lee": ["kishōtenketsu", "descent_redemption"],   # 克制
    "hou_hsiao_hsien": ["kishōtenketsu"],                 # 凝视历史
    "tsui_hark": ["hero_journey", "classic_three_act"],   # 武侠奇情
    "john_woo": ["hero_journey", "descent_redemption"],  # 英雄悲歌
    "johnnie_to": ["mystery_reveal", "classic_three_act"],  # 宿命对峙
    "kore_eda": ["kishōtenketsu", "descent_redemption"],  # 日常悲悯
    "satoshi_kon": ["nonlinear", "emotional_rollercoaster"],  # 梦境虚实
    "makoto_shinkai": ["kishōtenketsu", "emotional_rollercoaster"],
    "lee_changdong": ["mystery_reveal", "descent_redemption"],  # 燃烧追问
    "guo_fan": ["hero_journey", "classic_three_act"],     # 集体史诗
    "sergio_leone": ["buildup_payoff", "classic_three_act"],  # 对峙延迟
    "fernando_meirelles": ["nonlinear", "emotional_rollercoaster"],  # 贫民窟失控
    "polanski": ["mystery_reveal", "descent_redemption"],  # 幽闭恐惧
    "billy_wilder": ["classic_three_act", "mystery_reveal"],
    "orson_welles": ["nonlinear", "classic_three_act"],
    "john_ford": ["hero_journey", "classic_three_act"],
    "david_lean": ["hero_journey", "classic_three_act"],
    "ozu": ["kishōtenketsu"],
    "chaplin": ["classic_three_act", "kishōtenketsu"],
    "michael_mann": ["classic_three_act", "descent_redemption"],
    "terrence_malick": ["kishōtenketsu", "nonlinear"],
    "de_palma": ["mystery_reveal", "nonlinear"],
    # 新锐短剧/短视频: 快节奏反转为主
    "yan_xiaodi": ["short_drama_hook", "emotional_rollercoaster"],
    "liu_xunzimo": ["emotional_rollercoaster", "nonlinear"],
    "jiang_shiqi": ["emotional_rollercoaster", "kishōtenketsu"],
    "duanmu_rong": ["short_drama_hook", "buildup_payoff"],
    "zach_king": ["emotional_rollercoaster"],
    "sam_kolder": ["emotional_rollercoaster"],
    "brandon_li": ["kishōtenketsu", "classic_three_act"],
}

# 类型→叙事结构亲和度
GENRE_NARRATIVE_AFFINITY = {
    "suspense_thriller": ["mystery_reveal", "buildup_payoff"],
    "action_combat": ["save_the_cat", "classic_three_act"],
    "war_epic": ["parallel_convergence", "classic_three_act"],
    "mythology_fantasy": ["hero_journey", "classic_three_act"],
    "xianxia_cultivation": ["hero_journey", "buildup_payoff"],
    "romance_sweet": ["emotional_rollercoaster", "kishōtenketsu"],
    "comedy_humor": ["save_the_cat", "kishōtenketsu"],
    "sci_fi": ["hero_journey", "nonlinear"],
    "period_costume": ["classic_three_act", "kishōtenketsu"],
    "horror": ["descent_redemption", "buildup_payoff"],
    "urban_modern": ["kishōtenketsu", "emotional_rollercoaster"],
    "pastoral_idyllic": ["kishōtenketsu"],
    "time_travel": ["nonlinear", "in_medias_res"],
    "cyberpunk": ["descent_redemption", "mystery_reveal"],
    "wuxia_martial_arts": ["hero_journey", "classic_three_act"],
    "psychological": ["nonlinear", "mystery_reveal"],
    "documentary_style": ["kishōtenketsu", "parallel_convergence"],
    "noir": ["mystery_reveal", "descent_redemption"],
    "musical": ["classic_three_act", "kishōtenketsu"],
    "survival": ["classic_three_act", "hero_journey"],
    "family_warmth": ["kishōtenketsu", "descent_redemption"],
    "revenge": ["buildup_payoff", "descent_redemption"],
}

# 叙事功能→情绪映射(表演指导按情节推进需要,而非纯数值)
NARRATIVE_FUNC_EMOTION = {
    # 开场/建立
    "开场": "hope", "冷开场": "vengeful_calm", "建立世界观": "serenity",
    "建立": "serenity", "定场": "nostalgia",
    # 铺垫/暗线
    "铺垫": "suspicion", "暗线铺设": "guilt", "伏笔": "suspicion",
    "日常": "serenity", "背景": "nostalgia",
    # 触发/启程
    "触发": "hope", "召唤": "hope", "启程": "determination",
    "催化剂": "shock", "决定": "determination",
    # 发展/考验
    "发展": "anxiety", "考验": "fear", "上升": "hope",
    "蓄势": "anxiety", "积蓄": "anxiety",
    # 识破/发现
    "识破": "devastating_realization", "发现": "devastating_realization",
    "揭示": "devastating_realization", "真相": "devastating_realization",
    # 反转/转折
    "反转": "shock", "转折": "shock", "中点": "schadenfreude",
    "暴露": "guilt", "背叛": "guilt",
    # 冲突/对峙
    "冲突": "anger", "对峙": "anger", "对决": "tender_anger",
    "高潮": "anger", "决战": "tender_anger", "爆发": "anger",
    # 牺牲/失去
    "牺牲": "tender_grief", "失去": "despair", "沉沦": "despair",
    "低谷": "despair", "黑暗": "despair", "死亡": "tender_grief",
    # 重逢/救赎
    "重逢": "relief", "救赎": "hope", "重生": "hope",
    "觉醒": "hope", "胜利": "pride", "逆袭": "pride",
    # 余韵/收束
    "余韵": "nostalgia", "收束": "serenity", "结尾": "tender_grief",
    "余波": "tender_grief", "代价": "tender_grief",
    # 短剧专用
    "打脸": "pride", "爽点": "pride", "虐点": "tender_grief",
    "悬念": "suspicion", "悬崖": "anxiety",
}

# 中文叙事功能→情绪的模糊匹配(子串包含,优先长key)
_NARRATIVE_FUNC_EMOTION_SORTED = sorted(NARRATIVE_FUNC_EMOTION.items(), key=lambda kv: -len(kv[0]))

def _infer_emotion_from_func(narrative_func, default="determination"):
    """从叙事功能推断合适的情绪类型(子串匹配,优先长关键词)"""
    if not narrative_func:
        return default
    for keyword, emotion in _NARRATIVE_FUNC_EMOTION_SORTED:
        if keyword in narrative_func:
            return emotion
    return default


class StoryContextBuilder:
    """故事前文构建器 — 用户核心需求: 每个分镜输出前必须携带前面故事大纲"""

    def __init__(self, topic, character_desc, env_desc, total_shots):
        self.topic = topic
        self.character_desc = character_desc
        self.env_desc = env_desc
        self.total_shots = total_shots
        self.shot_summaries = []
        self.active_characters = set()
        self.current_scene = ""
        self.unresolved_tensions = []
        self.planted_foreshadows = []
        self.emotion_trajectory = []

    def record_shot(self, shot_index, summary_text, scene="", characters=None,
                    emotion_value=0.5, tension="", foreshadow=""):
        self.shot_summaries.append({
            "index": shot_index,
            "summary": summary_text,
            "scene": scene,
            "emotion": emotion_value,
        })
        if scene:
            self.current_scene = scene
        if characters:
            self.active_characters.update(characters)
        self.emotion_trajectory.append(emotion_value)
        if tension:
            self.unresolved_tensions.append(tension)
        if foreshadow:
            self.planted_foreshadows.append(foreshadow)

    def build_context_prefix(self, current_shot_index):
        """构建当前分镜的故事前文(核心功能)"""
        if current_shot_index == 0:
            return self._build_opening_context()
        return self._build_continuation_context(current_shot_index)

    def _build_opening_context(self):
        lines = [
            "【故事前文】",
            f"这是故事的第一个镜头。",
            f"故事主题: {self.topic}",
        ]
        if self.character_desc:
            lines.append(f"主要角色: {self.character_desc[:200]}")
        if self.env_desc:
            lines.append(f"世界设定: {self.env_desc[:200]}")
        lines.append(f"全片共{self.total_shots}个镜头，当前是开场第1镜。")
        lines.append("任务: 建立世界观、引入角色、设定基调。观众的第一印象决定是否继续观看。")
        return "\n".join(lines)

    def _build_continuation_context(self, current_idx):
        lines = ["【故事前文 — 确保叙事连续性】"]
        lines.append(f"全片{self.total_shots}镜，当前第{current_idx + 1}镜（进度{current_idx/self.total_shots:.0%}）")

        # 前面所有镜头的摘要
        if self.shot_summaries:
            lines.append("")
            lines.append("前面已发生的故事:")
            # 最近3个镜头给详细摘要，更早的给一句话
            early = self.shot_summaries[:-3] if len(self.shot_summaries) > 3 else []
            recent = self.shot_summaries[-3:]

            if early:
                early_summary = " → ".join(
                    s["summary"][:40] for s in early
                )
                lines.append(f"  [镜头1-{len(early)}概要] {early_summary}")

            for s in recent:
                lines.append(f"  [镜头{s['index']+1}] {s['summary']}")

        # 当前场景
        if self.current_scene:
            lines.append(f"\n当前场景: {self.current_scene}")

        # 活跃角色
        if self.active_characters:
            lines.append(f"在场角色: {', '.join(list(self.active_characters)[:5])}")

        # 未解决的悬念
        if self.unresolved_tensions:
            lines.append(f"\n待解决的悬念/冲突:")
            for t in self.unresolved_tensions[-3:]:
                lines.append(f"  - {t}")

        # 已埋伏笔
        if self.planted_foreshadows:
            lines.append(f"\n已埋设的伏笔(适时回收):")
            for f in self.planted_foreshadows[-3:]:
                lines.append(f"  - {f}")

        # 情绪轨迹
        if self.emotion_trajectory:
            trend = self._describe_emotion_trend()
            lines.append(f"\n情绪走势: {trend}")

        lines.append(f"\n要求: 本镜头必须与上述故事自然衔接，保持角色状态、场景、情绪的连续性。")
        return "\n".join(lines)

    def _describe_emotion_trend(self):
        if len(self.emotion_trajectory) < 2:
            return "刚刚开始"
        recent = self.emotion_trajectory[-3:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "情绪持续上升中 ↑"
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "情绪持续下降中 ↓"
        else:
            return "情绪波动起伏中 ↗↘"


class KnowledgeDirector:
    """知识库驱动的导演引擎 — 根据类型/风格/进度从知识库提取最佳实践"""

    def __init__(self, style, genre_key=None, director_keys=None):
        self.style = style
        self.genre_key = genre_key or STYLE_TO_GENRE.get(style)
        # 优先用显式传入的导演;否则按风格→类型双重查找
        self.director_keys = director_keys or STYLE_TO_DIRECTORS.get(style, [])
        if not self.director_keys and self.genre_key:
            self.director_keys = GENRE_TO_DIRECTORS.get(self.genre_key, [])
        self.genre_profile = GENRE_PROFILES.get(self.genre_key, {}) if self.genre_key else {}
        # 验证导演key是否在库中存在,过滤无效项
        valid = [k for k in self.director_keys if k in DIRECTOR_STYLES]
        self.director_keys = valid or self._fallback_directors()

    def _fallback_directors(self):
        """无匹配时回退到通用大师组合"""
        return ["spielberg", "nolan", "fincher"]

    def recommend_narrative_structure(self, is_short_form=False):
        """根据导演+类型推荐最契合的叙事结构(用户选'自动'时调用)"""
        # 收集导演偏好的结构(按出现频次排序)
        director_prefs = []
        for dk in self.director_keys:
            director_prefs.extend(DIRECTOR_NARRATIVE_AFFINITY.get(dk, []))
        # 类型偏好的结构
        genre_prefs = GENRE_NARRATIVE_AFFINITY.get(self.genre_key, []) if self.genre_key else []

        # 短剧/短视频 → 强制优先快节奏结构
        if is_short_form:
            short_prefs = ["short_drama_hook", "emotional_rollercoaster"]
            director_prefs = short_prefs + director_prefs
            genre_prefs = genre_prefs or ["short_drama_hook"]

        # 评分:导演命中+2, 类型命中+1 (导演风格优先,因为叙事方法契合导演是核心)
        from collections import Counter
        scores = Counter()
        for s in director_prefs:
            scores[s] += 2
        for s in genre_prefs:
            scores[s] += 1

        if not scores:
            return "classic_three_act"
        # 取最高分,且必须是有效结构key
        valid_keys = set(NARRATIVE_STRUCTURES.keys())
        ranked = [s for s, _ in scores.most_common() if s in valid_keys]
        return ranked[0] if ranked else "classic_three_act"

    def get_visual_language_guide(self):
        """获取当前类型的视觉语言指南(合并决策覆盖层)"""
        if not self.genre_key:
            return ""
        # 合并决策覆盖层(注入trigger/failure/measurement等)
        try:
            from knowledge_base.genre_profiles import get_genre_with_decision
            profile = get_genre_with_decision(self.genre_key)
        except Exception:
            profile = self.genre_profile
        if not profile:
            return ""
        vl = profile.get("visual_language", {})
        if not vl:
            return ""
        lines = ["【类型视觉语言 — 深度决策】"]
        if profile.get("trigger"):
            lines.append(f"  类型触发: {profile['trigger']}")
        if profile.get("rationale"):
            lines.append(f"  类型原理: {profile['rationale']}")
        for key, val in vl.items():
            lines.append(f"  {key}: {val}")
        if profile.get("failure_modes"):
            lines.append(f"  类型失败模式(避免): {'; '.join(profile['failure_modes'][:2])}")
        if profile.get("measurement"):
            lines.append(f"  类型验收: {profile['measurement']}")
        return "\n".join(lines)

    def set_directors(self, director_keys):
        """运行时切换导演选择(节点下拉框直接传入)"""
        valid = [k for k in director_keys if k in DIRECTOR_STYLES]
        self.director_keys = valid or self._fallback_directors()

    def get_director_style_guide(self):
        """获取导演风格提示(输出完整技法+原则+决策覆盖层)"""
        if not self.director_keys:
            return ""
        try:
            from knowledge_base.director_styles import get_director_with_decision
            _merge = get_director_with_decision
        except Exception:
            _merge = None
        lines = ["【导演风格参考集群 — 深度决策】"]
        guide = DIRECTOR_STYLES.get("style_application_guide", {})
        prompt_prefix = guide.get("prompt_style_prefix", {})
        # 最多融合2位导演风格
        for dk in self.director_keys[:2]:
            ds = DIRECTOR_STYLES.get(dk, {})
            if not ds:
                continue
            if _merge:
                ds = _merge(dk)
            lines.append(f"  ◆ {ds.get('cn', dk)} — {ds.get('signature', '')}")
            techniques = ds.get("visual_techniques", [])[:4]
            for t in techniques:
                lines.append(f"    · {t}")
            lines.append(f"    叙事原则: {ds.get('narrative_principle', '')}")
            if dk in prompt_prefix:
                lines.append(f"    风格关键词: {prompt_prefix[dk]}")
            # 决策覆盖层注入
            if ds.get("trigger"):
                lines.append(f"    适用场景: {ds['trigger']}")
            if ds.get("failure_modes"):
                lines.append(f"    风格失败模式(避免): {'; '.join(ds['failure_modes'][:2])}")
            if ds.get("measurement"):
                lines.append(f"    风格验收: {ds['measurement']}")
            if ds.get("alternatives"):
                lines.append(f"    相近导演: {'; '.join(ds['alternatives'])}")
        return "\n".join(lines)

    def get_camera_recommendation(self, intensity, emotion_value, progress, is_vertical=False):
        """从知识库获取运镜推荐(基于情绪强度+进度智能选择)"""
        movements = MASTER_CINEMATOGRAPHY.get("camera_movements", {})
        if intensity > 0.8:
            # 高能:激烈动态
            candidates = ["handheld", "whip_pan", "orbit", "fpv_drone"]
        elif intensity > 0.6:
            # 中高:推进/跟随
            candidates = ["tracking", "dolly", "push_in", "vertigo_shot"]
        elif intensity > 0.4:
            # 中:常规叙事运动
            candidates = ["push_in", "pan", "dolly", "slider"]
        elif emotion_value < 0.25:
            # 低落:沉静/疏离
            candidates = ["static", "pull_back", "crane"]
        else:
            # 默认:稳定叙事
            candidates = ["static", "push_in", "crane"]

        chosen = random.choice(candidates)
        info = movements.get(chosen, {})
        cam_cn = info.get("cn", chosen)
        # 深度schema: 优先返回trigger/rationale, 兼容旧的psychology字段
        rationale = info.get("rationale", "") or info.get("psychology", "")
        trigger = info.get("trigger", "")
        failure_modes = info.get("failure_modes", [])
        measurement = info.get("measurement", "")
        alternatives = info.get("alternatives", [])
        cross_refs = info.get("cross_refs", {})
        execution = info.get("execution", {})

        if is_vertical:
            # 竖屏过滤掉横摇类,强调纵向运动
            if chosen in ("whip_pan", "pan", "fpv_drone", "cable_cam"):
                candidates = ["push_in", "tilt", "crane", "jib_arm", "static"]
                chosen = random.choice(candidates)
                info = movements.get(chosen, {})
                cam_cn = info.get("cn", chosen)
                rationale = info.get("rationale", "") or info.get("psychology", "")
                trigger = info.get("trigger", "")
                failure_modes = info.get("failure_modes", [])
                measurement = info.get("measurement", "")
                alternatives = info.get("alternatives", [])
                cross_refs = info.get("cross_refs", {})
                execution = info.get("execution", {})
            cam_cn = f"竖屏{cam_cn}(以纵向运动为主)"

        return {
            "key": chosen, "cn": cam_cn, "rationale": rationale, "trigger": trigger,
            "failure_modes": failure_modes, "measurement": measurement,
            "alternatives": alternatives, "cross_refs": cross_refs, "execution": execution,
        }

    def get_transition_recommendation(self, shot_index, total_shots, scene_changed,
                                       emotion_delta, intensity):
        """从知识库获取转场推荐"""
        cuts = TRANSITION_GRAMMAR.get("cut_types", {})
        if shot_index == 0:
            return "淡入", "故事世界从虚无中浮现"
        if shot_index >= total_shots - 1:
            return "长叠化/淡出黑场", "余韵收束"
        if scene_changed:
            return "叠化", "空间过渡,情绪延续"
        if emotion_delta > 0.4:
            return "猛切/对比切", "极端情绪反差碰撞"
        if intensity > 0.8:
            return "硬切", "高能量快速推进"
        return "硬切", "叙事能量保持连贯"

    def get_performance_guide(self, emotion_key, intensity):
        """从表演系统获取微表情/肢体指导(基础+进阶情绪库)"""
        micro = PERFORMANCE_SYSTEM.get("micro_expressions", {})
        micro_adv = PERFORMANCE_SYSTEM.get("micro_expressions_advanced", {})
        # 基础情绪映射
        emotion_map = {
            "joy": "happiness", "sadness": "sadness", "anger": "anger",
            "fear": "fear", "love": "longing", "determination": "determination",
            "tenderness": "tenderness", "serenity": "serenity",
        }
        # 进阶情绪直接同名
        advanced_keys = list(micro_adv.keys())

        data = {}
        source = ""
        if emotion_key in emotion_map:
            mapped = emotion_map[emotion_key]
            data = micro.get(mapped, {})
            source = "基础"
        # 基础库未命中或为空 → 回退到进阶情绪库
        if not data and emotion_key in advanced_keys:
            data = micro_adv.get(emotion_key, {})
            source = "进阶"
        # 仍未命中 → 尝试进阶库的同义近邻
        if not data:
            synonym = {
                "joy": "hope", "sadness": "despair", "fear": "panic",
                "love": "tenderness", "determination": "pride",
            }.get(emotion_key)
            if synonym and synonym in advanced_keys:
                data = micro_adv.get(synonym, {})
                source = "进阶(近邻)"

        if not data:
            return ""

        # 合并PERFORMANCE_DECISION覆盖层(注入trigger/failure_modes/measurement)
        try:
            from knowledge_base.performance_system import PERFORMANCE_DECISION
            if emotion_key in PERFORMANCE_DECISION:
                dec = PERFORMANCE_DECISION[emotion_key]
                merged = dict(data)
                merged.update(dec)
                data = merged
        except Exception:
            pass

        if intensity > 0.7 and "prompt_description" in data:
            desc = data.get("prompt_description", "")
        elif "subtle_version" in data:
            desc = data.get("subtle_version", "")
        else:
            desc = data.get("prompt_description", "")
        body = data.get("body_language", "")
        lines = ["【表演指导 — 深度决策】"]
        if desc:
            lines.append(f"  面部({data.get('cn', emotion_key)}): {desc}")
        if body:
            lines.append(f"  肢体: {body}")
        if data.get("trigger"):
            lines.append(f"  情绪触发: {data['trigger']}")
        if data.get("failure_modes"):
            lines.append(f"  表演失败模式(避免): {'; '.join(data['failure_modes'][:2])}")
        if data.get("measurement"):
            lines.append(f"  表演验收: {data['measurement']}")
        return "\n".join(lines)

    def get_shot_duration_guide(self, emotion_key, intensity):
        """从镜头语汇获取时长建议"""
        guide = SHOT_VOCABULARY.get("shot_duration_guide", {})
        by_emotion = guide.get("by_emotion", {})
        if emotion_key in by_emotion:
            return by_emotion[emotion_key]
        if intensity > 0.8:
            return "1-3秒(高强度快切)"
        elif intensity > 0.5:
            return "3-5秒(中等节奏)"
        else:
            return "5-8秒(沉稳留白)"

    def get_composition_guide(self, intensity, emotion_value):
        """从摄影知识库获取构图建议"""
        compositions = MASTER_CINEMATOGRAPHY.get("composition", {})
        if intensity > 0.8:
            candidates = ["diagonal", "claustrophobic", "center_frame"]
        elif emotion_value < 0.3:
            candidates = ["negative_space", "frame_within_frame", "depth_layering"]
        elif emotion_value > 0.7:
            candidates = ["rule_of_thirds", "golden_ratio", "symmetry"]
        else:
            candidates = ["rule_of_thirds", "leading_lines", "depth_layering"]
        chosen = random.choice(candidates)
        comp = compositions.get(chosen, {})
        return comp.get("cn", chosen), comp.get("psychology", "")

    def get_lighting_recommendation(self, intensity, emotion_value, genre_key="", is_vertical=False):
        """从布光知识库获取深度布光建议(按情绪+类型智能选择)"""
        lighting = MASTER_CINEMATOGRAPHY.get("lighting", {})
        # 按情绪+强度+类型映射布光
        if emotion_value < 0.3:
            candidates = ["low_key", "chiaroscuro", "blue_hour"]
        elif emotion_value > 0.7 and intensity > 0.7:
            candidates = ["high_key", "golden_hour"]
        elif emotion_value > 0.6:
            candidates = ["golden_hour", "rembrandt"]
        else:
            candidates = ["three_point", "practical", "motivated"]
        # 类型修正
        if genre_key == "cyberpunk" or genre_key == "urban_modern":
            candidates = ["neon", "practical"] + candidates
        elif genre_key == "noir" or genre_key == "suspense_thriller":
            candidates = ["low_key", "chiaroscuro"] + candidates
        elif genre_key == "comedy_humor":
            candidates = ["high_key"] + candidates
        elif genre_key in ("pastoral_idyllic", "romance_sweet"):
            candidates = ["golden_hour", "high_key"] + candidates

        chosen = random.choice(candidates)
        info = lighting.get(chosen, {})
        if not info:
            return {}
        return {
            "key": chosen, "cn": info.get("cn", chosen),
            "trigger": info.get("trigger", ""),
            "rationale": info.get("rationale", ""),
            "execution": info.get("execution", {}),
            "failure_modes": info.get("failure_modes", []),
            "measurement": info.get("measurement", ""),
            "cross_refs": info.get("cross_refs", {}),
        }

    def get_short_drama_hook(self, shot_index, total_shots):
        """短剧专用: 获取开场钩子/悬崖技巧"""
        if shot_index == 0:
            hooks = SHORT_DRAMA_PATTERNS.get("opening_hooks", {})
            hook_type = random.choice(list(hooks.values()))
            tech = random.choice(hook_type.get("techniques", ["视觉冲击"]))
            return f"【开场钩子】{hook_type.get('cn', '')}: {tech} (必须在{hook_type.get('duration', '3秒')}内抓住观众)"
        if shot_index >= total_shots - 1:
            cliffs = SHORT_DRAMA_PATTERNS.get("cliffhanger_techniques", {})
            cliff = random.choice(list(cliffs.values()))
            return f"【结尾悬崖】{cliff.get('cn', '')}: {cliff.get('example', '')} 原理: {cliff.get('principle', '')}"
        return ""


class DirectorPromptBuilder:
    """导演级提示词构建器 — 整合知识库生成世界级system prompt"""

    def __init__(self, mode, style, color_tone, topic, character_desc, env_desc,
                 total_shots, camera_style="", is_vertical=False, director_keys=None,
                 narrative_structure="", short_drama_type="", audience_archetype="",
                 output_focus="分镜"):
        self.mode = mode
        self.style = style
        self.color_tone = color_tone
        self.topic = topic
        self.character_desc = character_desc
        self.env_desc = env_desc
        self.total_shots = total_shots
        self.camera_style = camera_style
        self.is_vertical = is_vertical or "竖屏" in (camera_style or "")
        self.narrative_structure = narrative_structure
        self.short_drama_type = short_drama_type
        self.audience_archetype = audience_archetype
        self.output_focus = output_focus  # 输出侧重: 分镜/角色/环境/故事/氛围/互动

        self.knowledge = KnowledgeDirector(style, director_keys=director_keys)
        self.context_builder = StoryContextBuilder(topic, character_desc, env_desc, total_shots)

        # 叙事结构自动适配: 用户未指定时,按导演+类型推荐最契合的结构
        is_short = self.is_vertical or "短剧" in mode
        if not self.narrative_structure:
            recommended = self.knowledge.recommend_narrative_structure(is_short_form=is_short)
            self.narrative_structure = recommended
            self._narrative_auto = True   # 标记是自动推荐的
        else:
            self._narrative_auto = False
        # prompt tier: full(完整4267字符决策上下文) / lean(精简~1500字符,适合小模型)
        self.prompt_mode = "full"

    def build_system_prompt(self, shot_index, beat_info, constraints_text=""):
        """构建世界级导演system prompt(按prompt_mode选full/lean)"""
        if self.prompt_mode == "lean":
            return self._build_lean_prompt(shot_index, beat_info, constraints_text)
        return self._build_full_prompt(shot_index, beat_info, constraints_text)

    def _build_lean_prompt(self, shot_index, beat_info, constraints_text=""):
        """精简prompt tier(~1500字符) — 适合小模型/低token预算, 保留最高信号决策字段"""
        sections = []
        # 1. 故事前文(精简: 只最近1镜摘要+场景+情绪走势)
        ctx = self.context_builder
        if shot_index == 0:
            sections.append(f"【故事前文】开场第1镜。主题:{self.topic[:60]}。任务:建立世界观+引入角色+定基调。")
        else:
            recent = ctx.shot_summaries[-1] if ctx.shot_summaries else None
            scene = f" 场景:{ctx.current_scene}" if ctx.current_scene else ""
            emo = self.context_builder._describe_emotion_trend() if ctx.emotion_trajectory else "刚开始"
            last = recent["summary"][:50] if recent else ""
            sections.append(f"【前文】第{shot_index+1}/{self.total_shots}镜。上一镜:{last}{scene}。情绪:{emo}。须连续衔接。")
        # 2. 导演风格关键词(1行, 从prompt_style_prefix)
        guide = DIRECTOR_STYLES.get("style_application_guide", {})
        prefix = guide.get("prompt_style_prefix", {})
        style_kws = "; ".join(prefix.get(dk, "") for dk in self.knowledge.director_keys[:2] if dk in prefix)
        if style_kws:
            sections.append(f"【导演风格】{style_kws}")
        # 2.5 [Phase 3] 决策层精简(关键决策单行)
        decision_layer = self._build_decision_layer()
        if decision_layer:
            # lean 模式只保留前 600 字符的最关键决策
            sections.append(f"【决策层摘要】\n{decision_layer[:600]}")
        # 3. 影视语言关键决策(每项1行)
        if beat_info:
            intensity = beat_info.get("intensity", 0.5)
            emo_val = beat_info.get("emotion_value", 0.5)
            cam = self.knowledge.get_camera_recommendation(intensity, emo_val, shot_index/max(self.total_shots,1), self.is_vertical)
            comp_cn, _ = self.knowledge.get_composition_guide(intensity, emo_val)
            light = self.knowledge.get_lighting_recommendation(intensity, emo_val, self.knowledge.genre_key, self.is_vertical)
            dur = self.knowledge.get_shot_duration_guide(self._infer_emotion(beat_info, shot_index), intensity)
            lines = [f"【影视语言】时长:{dur} | 运镜:{cam.get('cn','') if isinstance(cam,dict) else cam} | 构图:{comp_cn} | 布光:{light.get('cn','') if isinstance(light,dict) else ''} | 情绪:{beat_info.get('beat_name','')}({emo_val:.2f}) | 功能:{beat_info.get('narrative_func','')}"]
            sections.append("\n".join(lines))
        # 4. 表演情绪(1行)
        if beat_info:
            emo_key = self._infer_emotion(beat_info, shot_index)
            perf = self.knowledge.get_performance_guide(emo_key, beat_info.get("intensity",0.5))
            # 精简: 只取面部一行
            for ln in perf.split("\n"):
                if "面部" in ln:
                    sections.append(f"【表演】{ln.strip()}")
                    break
        # 5. 竖屏铁律(精简)
        if self.is_vertical:
            sections.append("【竖屏】主体纵轴中心+面部占70%+纵向运动+每10秒新信息。")
        # 6. 输出格式
        sections.append(f"输出第{shot_index+1}镜: 景别+时空锚定+画面(3-5句)+运镜+转场+时长+台词。纯文字无符号。")
        return "\n\n".join(sections)

    def _build_full_prompt(self, shot_index, beat_info, constraints_text=""):
        """完整prompt tier(4267字符完整决策上下文) — 适合大模型"""
        sections = []

        # 1. 故事前文(核心功能)
        story_context = self.context_builder.build_context_prefix(shot_index)
        sections.append(story_context)

        # 2. 导演身份
        sections.append(self._build_identity(shot_index))

        # 3. 类型视觉语言
        visual_guide = self.knowledge.get_visual_language_guide()
        if visual_guide:
            sections.append(visual_guide)

        # 4. 导演风格参考
        director_guide = self.knowledge.get_director_style_guide()
        if director_guide:
            sections.append(director_guide)

        # 4.5 叙事结构指导(若指定)
        if self.narrative_structure:
            struct_guide = self._build_narrative_structure_guide()
            if struct_guide:
                sections.append(struct_guide)

        # 4.6 短剧类型与受众指导(若指定)
        if self.short_drama_type or self.audience_archetype:
            sd_guide = self._build_short_drama_guide()
            if sd_guide:
                sections.append(sd_guide)

        # 4.7 [Phase 3] 决策层注入(真实接通 4 个被忽略的决策 dict)
        decision_layer = self._build_decision_layer()
        if decision_layer:
            sections.append(decision_layer)

        # 5. 当前镜头的影视语言指导
        sections.append(self._build_cinematography_guide(shot_index, beat_info))

        # 5.3 实证作品对标(概率匹配真实作品的情节/叙述/情感特征) — 仅full模式
        if self.prompt_mode != "lean":
            emp_ref = self._build_empirical_reference(shot_index, beat_info)
            if emp_ref:
                sections.append(emp_ref)

        # 5.4 创作技法对标(全网检索skill: 爆款元素/平台算法/黄金前N秒) — 仅full+短剧/短视频
        if self.prompt_mode != "lean" and (self.is_vertical or "短剧" in self.mode or "短视频" in self.mode):
            skills_ref = self._build_creation_skills_ref()
            if skills_ref:
                sections.append(skills_ref)

        # 5.5 张弛有度节奏指导(确保剧情推进有呼吸感)
        pacing_guide = self._build_pacing_guide(shot_index, beat_info)
        if pacing_guide:
            sections.append(pacing_guide)

        # 5.6 输出侧重维度指导(用户选output_focus时注入对应维度模块:角色/环境/故事/氛围/互动)
        if self.output_focus and self.output_focus != "分镜" and self.prompt_mode != "lean":
            # [Phase 4] 先注入真实差异化的 output_focus 权重调整
            focus_focus = self._build_output_focus_focus()
            if focus_focus:
                sections.append(focus_focus)
            # 再注入维度模块本身
            dim_guide = self._build_dimension_guide()
            if dim_guide:
                sections.append(dim_guide)

        # 6. 表演指导(按叙事功能推断情绪,而非纯数值)
        if beat_info:
            intensity = beat_info.get("intensity", 0.5)
            emotion_key = self._infer_emotion(beat_info, shot_index)
            perf_guide = self.knowledge.get_performance_guide(emotion_key, intensity)
            if perf_guide:
                sections.append(perf_guide)

        # 6.5 情感渲染技法指导(从emotion_rendering抽取how-to)
        emo_guide = self._build_emotion_rendering_guide(beat_info)
        if emo_guide:
            sections.append(emo_guide)

        # 6.6 短视频/短剧模式: 注入短视频技法(viral_video决策覆盖层)
        if self.is_vertical or "短剧" in self.mode or "短视频" in self.mode:
            viral_guide = self._build_viral_guide(shot_index)
            if viral_guide:
                sections.append(viral_guide)

        # 7. 短剧专用钩子
        if self.is_vertical or "短剧" in self.mode:
            hook = self.knowledge.get_short_drama_hook(shot_index, self.total_shots)
            if hook:
                sections.append(hook)

        # 8. 画面铁律
        sections.append(self._build_iron_rules())

        # 9. 连续性约束
        if constraints_text:
            sections.append(f"【连续性约束】\n{constraints_text}")

        # 10. 输出指令
        sections.append(self._build_output_instruction(shot_index))

        return "\n\n".join(sections)

    def build_header(self):
        """构建总纲头部"""
        vertical_note = "竖屏9:16垂直构图。" if self.is_vertical else ""
        return (
            f"{'短剧' if self.is_vertical else self.mode}总纲\n"
            f"整体视觉风格: {self.style}，色彩基调{self.color_tone}。{vertical_note}\n"
            f"角色物品设定:\n{(self.character_desc or '待定角色').replace(chr(10), ' ').rstrip()}\n"
            f"场景设定:\n{(self.env_desc or '待定场景').rstrip()}\n"
        )

    def record_shot_result(self, shot_index, ai_result, beat_info=None):
        """记录已生成的镜头,更新故事上下文"""
        summary = self._extract_summary(ai_result)
        scene = self._extract_field(ai_result, "分镜场景")
        characters_text = self._extract_field(ai_result, "角色特征")
        characters = [c.strip() for c in characters_text.split("、")[:5]] if characters_text else None
        emotion_val = beat_info.get("emotion_value", 0.5) if beat_info else 0.5

        self.context_builder.record_shot(
            shot_index, summary, scene=scene, characters=characters,
            emotion_value=emotion_val,
        )

    def _build_identity(self, shot_index):
        progress_pct = shot_index / max(self.total_shots, 1)
        phase = "开场建立" if progress_pct < 0.2 else \
                "发展推进" if progress_pct < 0.5 else \
                "高潮冲突" if progress_pct < 0.8 else "收束余韵"
        return (
            f"【身份】你是世界顶级的{self.mode}导演兼分镜大师。\n"
            f"当前: 第{shot_index+1}/{self.total_shots}镜 | 阶段: {phase} | 进度: {progress_pct:.0%}"
        )

    def _build_narrative_structure_guide(self):
        """从叙事结构知识库提取节拍表指导"""
        key = self.narrative_structure
        # 中文→key映射(与节点下拉框标签对齐)
        cn_to_key = {
            "经典三幕": "classic_three_act", "经典三幕式": "classic_three_act",
            "英雄之旅": "hero_journey",
            "救猫咪": "save_the_cat",
            "起承转合": "kishōtenketsu",
            "倒叙": "in_medias_res", "倒叙开场": "in_medias_res",
            "非线性": "nonlinear",
            "短剧钩子": "short_drama_hook", "短剧钩子结构": "short_drama_hook",
            "悬疑揭秘": "mystery_reveal",
            "平行交汇": "parallel_convergence",
            "情绪过山车": "emotional_rollercoaster",
            "伏笔回收": "buildup_payoff",
            "沉沦救赎": "descent_redemption",
        }
        struct_key = cn_to_key.get(key, key)
        struct = NARRATIVE_STRUCTURES.get(struct_key)
        if not struct:
            return ""
        # 合并决策覆盖层(注入trigger/failure/measurement等)
        try:
            from knowledge_base.narrative_structures import get_structure_with_decision
            struct = get_structure_with_decision(struct_key)
        except Exception:
            pass
        lines = ["【叙事结构指导 — 深度决策】"]
        auto_note = " (系统按导演+类型自动适配)" if getattr(self, "_narrative_auto", False) else ""
        lines.append(f"  结构: {struct.get('cn', key)}{auto_note} — {struct.get('description', '')}")
        # 深度决策字段注入
        if struct.get("trigger"):
            lines.append(f"  适用场景: {struct['trigger']}")
        if struct.get("rationale"):
            lines.append(f"  原理: {struct['rationale']}")
        # 解释为何契合当前导演风格
        affinity_reason = self._explain_narrative_affinity(struct_key)
        if affinity_reason:
            lines.append(f"  契合原因: {affinity_reason}")
        if struct.get("failure_modes"):
            lines.append(f"  失败模式(避免): {'; '.join(struct['failure_modes'][:2])}")
        if struct.get("measurement"):
            lines.append(f"  验收标准: {struct['measurement']}")
        lines.append(f"  情绪曲线: {struct.get('emotion_curve', '')}")
        beat_map = struct.get("beat_map", [])
        if beat_map:
            lines.append("  节拍表(根据当前进度定位当前节拍):")
            progress = 0.0
            for b in beat_map:
                pos = b['position']
                marker = " ◀当前" if self._is_current_beat(pos) else ""
                lines.append(f"    · {int(pos*100)}% {b['beat']}: {b['function']}{marker}")
        return "\n".join(lines)

    def _explain_narrative_affinity(self, struct_key):
        """解释为何此叙事结构契合当前导演/类型"""
        reasons = []
        for dk in self.knowledge.director_keys[:2]:
            ds = DIRECTOR_STYLES.get(dk, {})
            prefs = DIRECTOR_NARRATIVE_AFFINITY.get(dk, [])
            if struct_key in prefs:
                cn = ds.get("cn", dk)
                sig = ds.get("signature", "")[:15]
                reasons.append(f"{cn}偏好此结构({sig}…)")
        if self.knowledge.genre_key:
            g_prefs = GENRE_NARRATIVE_AFFINITY.get(self.knowledge.genre_key, [])
            if struct_key in g_prefs:
                gp = GENRE_PROFILES.get(self.knowledge.genre_key, {})
                reasons.append(f"{gp.get('cn','')}类型叙事传统契合")
        return "; ".join(reasons) if reasons else ""

    def _is_current_beat(self, beat_position):
        """粗略判断某节拍是否在当前进度附近(用于节拍表标记)"""
        # 由于没有精确进度,基于已生成镜头数推断
        if not self.context_builder.shot_summaries:
            return beat_position < 0.1
        progress = len(self.context_builder.shot_summaries) / max(self.total_shots, 1)
        return abs(beat_position - progress) <= 0.12

    def _build_short_drama_guide(self):
        """短剧类型与受众指导(合并决策覆盖层,注入trigger/failure/measurement)"""
        try:
            from knowledge_base.short_drama_patterns import get_short_drama_with_decision
            _merge_fn = get_short_drama_with_decision
        except Exception:
            _merge_fn = None
        lines = ["【短剧爆款指导 — 深度决策】"]
        # 类型公式
        if self.short_drama_type:
            formulas = SHORT_DRAMA_PATTERNS.get("narrative_formulas", {})
            cn_to_key = {
                "打脸逆袭": "face_slapping_cascade", "隐藏身份": "hidden_identity",
                "甜宠升级": "sweet_romance_escalation", "重生复仇": "revenge_rebirth",
                "悬崖修炼": "cliff_build",
            }
            fk = cn_to_key.get(self.short_drama_type, "")
            formula = formulas.get(fk, {})
            if _merge_fn and fk:
                formula = _merge_fn(fk)
            if formula:
                lines.append(f"  类型公式: {formula.get('cn', '')}")
                lines.append(f"  结构: {formula.get('structure', '')}")
                lines.append(f"  核心原则: {formula.get('key_principle', '')}")
                if formula.get("trigger"):
                    lines.append(f"  适用场景: {formula['trigger']}")
                if formula.get("failure_modes"):
                    lines.append(f"  失败模式(避免): {'; '.join(formula['failure_modes'][:2])}")
                if formula.get("measurement"):
                    lines.append(f"  验收标准: {formula['measurement']}")
        # 受众原型
        if self.audience_archetype:
            archetypes = SHORT_DRAMA_PATTERNS.get("audience_archetypes", {})
            cn_to_key = {
                "男频": "male_frequency", "女频": "female_frequency",
                "银发": "silver_hair", "知识型": "intellectual",
            }
            ak = cn_to_key.get(self.audience_archetype, "")
            arch = archetypes.get(ak, {})
            if _merge_fn and ak:
                arch = _merge_fn(ak)
            if arch:
                lines.append(f"  目标受众: {arch.get('cn', '')}")
                lines.append(f"  核心诉求: {arch.get('core_desire', '')}")
                lines.append(f"  满足公式: {arch.get('satisfaction_formula', '')}")
                if arch.get("failure_modes"):
                    lines.append(f"  受众失败模式(避免): {'; '.join(arch['failure_modes'][:2])}")
        # 竖屏铁律
        if self.is_vertical:
            rules = SHORT_DRAMA_PATTERNS.get("vertical_video_rules", {})
            pacing = rules.get("pacing", {})
            if pacing:
                lines.append(f"  竖屏节奏: 每{pacing.get('new_info_every', '10秒')}必新信息, "
                             f"每{pacing.get('mini_reversal_every', '15秒')}一反转, 零废帧")
        return "\n".join(lines)

    def _build_cinematography_guide(self, shot_index, beat_info):
        if not beat_info:
            return ""
        intensity = beat_info.get("intensity", 0.5)
        emotion_val = beat_info.get("emotion_value", 0.5)
        progress = beat_info.get("story_progress", shot_index / max(self.total_shots, 1))
        emotion_key = self._infer_emotion(beat_info, shot_index)

        cam_info = self.knowledge.get_camera_recommendation(
            intensity, emotion_val, progress, self.is_vertical)
        comp_cn, comp_psych = self.knowledge.get_composition_guide(intensity, emotion_val)
        duration = self.knowledge.get_shot_duration_guide(emotion_key, intensity)

        scene_changed = False
        emotion_delta = 0
        if self.context_builder.shot_summaries:
            last_emotion = self.context_builder.emotion_trajectory[-1] if self.context_builder.emotion_trajectory else 0.5
            emotion_delta = abs(emotion_val - last_emotion)
        trans_cn, trans_reason = self.knowledge.get_transition_recommendation(
            shot_index, self.total_shots, scene_changed, emotion_delta, intensity)

        cam_cn = cam_info.get("cn", "") if isinstance(cam_info, dict) else str(cam_info)
        lines = [
            "【影视语言指导 — 深度决策】",
            f"  推荐时长: {duration}",
            f"  推荐运镜: {cam_cn}",
        ]
        # 深度schema注入: trigger/rationale/execution/failure/measurement/alternatives
        if isinstance(cam_info, dict):
            if cam_info.get("trigger"):
                lines.append(f"  运镜触发条件: {cam_info['trigger']}")
            if cam_info.get("rationale"):
                lines.append(f"  运镜原理: {cam_info['rationale']}")
            exec_data = cam_info.get("execution", {})
            if exec_data:
                exec_str = self._pick_execution_speed(exec_data, intensity)
                if exec_str:
                    lines.append(f"  量化执行: {exec_str}")
            if cam_info.get("failure_modes"):
                lines.append(f"  失败模式(避免): {'; '.join(cam_info['failure_modes'][:2])}")
            if cam_info.get("measurement"):
                lines.append(f"  验收标准: {cam_info['measurement']}")
            if cam_info.get("alternatives"):
                lines.append(f"  替代方案: {'; '.join(cam_info['alternatives'])}")
            xref = cam_info.get("cross_refs", {})
            if xref:
                lines.append(f"  交叉影响: " + "; ".join(f"{k}→{v}" for k, v in xref.items()))
        lines.extend([
            f"  推荐构图: {comp_cn} — {comp_psych}",
            f"  推荐转场: {trans_cn} — {trans_reason}",
            f"  情绪节拍: {beat_info.get('beat_name', '未知')} "
            f"(情绪值{emotion_val:.2f}, 强度{intensity:.2f})",
            f"  叙事功能: {beat_info.get('narrative_func', '')}",
        ])
        # 布光深度决策注入
        genre_key = self.knowledge.genre_key or ""
        light_info = self.knowledge.get_lighting_recommendation(
            intensity, emotion_val, genre_key, self.is_vertical)
        if isinstance(light_info, dict) and light_info:
            lines.append(f"  推荐布光: {light_info.get('cn','')}")
            if light_info.get("trigger"):
                lines.append(f"  布光触发: {light_info['trigger']}")
            if light_info.get("rationale"):
                lines.append(f"  布光原理: {light_info['rationale']}")
            if light_info.get("failure_modes"):
                lines.append(f"  布光失败模式(避免): {'; '.join(light_info['failure_modes'][:2])}")
            if light_info.get("measurement"):
                lines.append(f"  布光验收: {light_info['measurement']}")
        recommended_shots = beat_info.get("recommended_shot_types", [])
        if recommended_shots:
            lines.append(f"  推荐景别: {'/'.join(recommended_shots)}")
        return "\n".join(lines)

    def _pick_execution_speed(self, exec_data, intensity):
        """按强度从execution的多个speed参数中选最匹配的"""
        if intensity > 0.8:
            for k in ("speed_shock", "speed_chaos", "speed_snap"):
                if k in exec_data:
                    return f"{k}: {exec_data[k]}"
        elif intensity > 0.5:
            for k in ("speed_normal", "speed_follow", "speed_reveal"):
                if k in exec_data:
                    return f"{k}: {exec_data[k]}"
        else:
            for k in ("speed_calm", "speed_sad", "speed_slow", "speed_smooth"):
                if k in exec_data:
                    return f"{k}: {exec_data[k]}"
        for k, v in exec_data.items():
            if k.startswith("speed_"):
                return f"{k}: {v}"
        # 无speed_键(如static/dolly类)→回退到首个量化字段
        for k, v in exec_data.items():
            return f"{k}: {v}"
        return ""

    def _infer_emotion(self, beat_info, shot_index):
        """智能情绪推断: 优先叙事功能 → 情绪数值 → 导演/类型语境"""
        # 1. 叙事功能关键词推断(最优先,符合情节推进需要)
        func = beat_info.get("narrative_func", "")
        emotion_from_func = _infer_emotion_from_func(func, default=None)
        if emotion_from_func:
            return emotion_from_func
        # 2. 退回情绪数值映射
        emotion_val = beat_info.get("emotion_value", 0.5)
        return self._map_emotion_key(emotion_val)

    def _build_pacing_guide(self, shot_index, beat_info):
        """张弛有度节奏系统 — 确保剧情推进有呼吸感,符合电影/短剧正常习惯"""
        if not beat_info:
            return ""
        total = max(self.total_shots, 1)
        progress = beat_info.get("story_progress", shot_index / total)
        intensity = beat_info.get("intensity", 0.5)
        emotion_val = beat_info.get("emotion_value", 0.5)
        func = beat_info.get("narrative_func", "")

        # 1. 识别当前节奏位置(蓄势/爆发/喘息/余韵/过渡)
        pace_phase = self._identify_pace_phase(progress, intensity, func, shot_index, total)

        # 2. 检测与前镜的强度关系,防止连续高潮无喘息
        tension_warning = ""
        if len(self.context_builder.emotion_trajectory) >= 2:
            recent_intensities = self.context_builder.emotion_trajectory[-2:]
            # 连续高强(>0.8) → 强制要求本镜降温
            if all(v > 0.8 for v in recent_intensities) and intensity > 0.7:
                tension_warning = ("⚠️ 前两镜已连续高强度,本镜必须降温留喘息——"
                                   "电影规律:两个高潮之间必须有缓冲,否则观众疲劳脱敏")
            # 连续低落 → 要求回升
            elif all(v < 0.25 for v in recent_intensities) and intensity < 0.3:
                tension_warning = ("⚠️ 连续低迷过久,本镜需注入一点张力或反差——"
                                   "避免全程沉闷,需一个小钩子回升注意力")

        # 3. 节奏节奏建议(时长/剪辑/音乐)
        rhythm_advice = self._pace_rhythm_advice(pace_phase, intensity)

        # 4. 类型/导演节奏特性
        genre_pace = self._genre_pacing_note()

        lines = ["【张弛有度节奏指导】"]
        lines.append(f"  当前节奏位: {pace_phase} (进度{progress:.0%}, 强度{intensity:.2f})")
        if rhythm_advice:
            lines.append(f"  节奏建议: {rhythm_advice}")
        if genre_pace:
            lines.append(f"  类型节奏特性: {genre_pace}")
        if tension_warning:
            lines.append(f"  {tension_warning}")
        # 短剧额外节奏铁律
        if self.is_vertical or "短剧" in self.mode:
            lines.append("  短剧铁律: 每10秒必新信息,每15-20秒一反转,零废帧,但反转间需留情绪垫")
        return "\n".join(lines)

    def _identify_pace_phase(self, progress, intensity, func, shot_index, total):
        """识别当前在张弛曲线上的位置"""
        func_text = func if func else ""
        # 按叙事功能直接判定(优先,最准确)
        if any(k in func_text for k in ["余韵", "收束", "结尾", "余波", "代价"]):
            return "余韵(高潮后沉淀,镜头变长,音乐渐弱)"
        if any(k in func_text for k in ["高潮", "决战", "对决", "爆发", "终极", "逆袭", "打脸"]) and intensity > 0.7:
            return "爆发(能量顶点,快切或慢动作顶点)"
        if any(k in func_text for k in ["反转", "转折", "中点", "揭示", "识破", "暴露", "背叛"]):
            return "拐点(预期被打破,短切+音效骤停)"
        if any(k in func_text for k in ["蓄势", "积蓄", "铺垫", "暗线", "悬念", "悬崖"]):
            return "蓄势(缓慢积累,镜头变长,音效渐强)"
        if any(k in func_text for k in ["开场", "冷开场", "建立", "定场", "建立世界观"]):
            return "开场(建立基调,节奏稳)"
        if any(k in func_text for k in ["喘息", "缓冲", "日常", "过渡段"]):
            return "喘息(高潮间缓冲,日常细节)"
        # 按进度+强度兜底推断
        if progress < 0.18:
            return "开场(建立基调,节奏稳)"
        if intensity > 0.8 and 0.4 < progress < 0.9:
            return "爆发(能量顶点)"
        if intensity < 0.3 and progress > 0.85:
            return "余韵(收束沉淀)"
        if intensity < 0.4:
            return "喘息(高潮间缓冲,日常细节)"
        return "过渡(推进叙事,中等节奏)"

    def _pace_rhythm_advice(self, phase, intensity):
        """根据节奏位给出剪辑/时长/音乐建议"""
        if "爆发" in phase:
            return "快切0.5-2s/镜冲向顶点,顶点用慢动作或帧冻结,配乐达到最强后骤停"
        if "蓄势" in phase:
            return "镜头5-8s变长,极缓推镜,环境音层叠渐强,配乐从无到有"
        if "拐点" in phase:
            return "硬切或猛切+音效骤停,短镜(1-2s)打碎预期,留一个长反应镜"
        if "余韵" in phase:
            return "长镜8-12s不切开,让观众消化,配乐渐弱至静默,缓拉至空旷"
        if "喘息" in phase:
            return "中镜3-5s,日常细节/幽默缓冲,配乐轻松,为下一波蓄势"
        if "开场" in phase:
            return "建立镜3-6s稳,定调,3秒内给一个视觉钩子抓住注意力"
        return "中镜3-5s推进,硬切为主,保持叙事能量"

    def _genre_pacing_note(self):
        """类型片的节奏特性提示"""
        g = self.knowledge.genre_key
        notes = {
            "suspense_thriller": "悬疑:慢→更慢→突然加速→爆发,信息不对称制造张力",
            "action_combat": "动作:蓄力(慢)→爆发(快)→顶点(慢放)→余波(归静)",
            "war_epic": "战争:宁静等待→混乱爆发→死寂(误以为安全)→再爆发→漫长余波",
            "romance_sweet": "甜宠:情绪递进不重复,甜度必须逐级上升,虐甜交替",
            "comedy_humor": "喜剧:笑点卡帧精确,反应镜是节拍关键,留反应时间",
            "horror": "恐怖:安静积蓄→突然冲击→最恐怖处反而是安静的",
            "revenge": "复仇:压得越深弹得越高,延迟满足+密集释放,完成后空虚",
            "mystery_reveal": "悬疑揭秘:层层剥洋葱,每次揭示后留消化镜",
        }
        return notes.get(g, "")

    def _build_empirical_reference(self, shot_index, beat_info):
        """实证作品对标: 概率匹配真实作品的情节/叙述/情感特征, 注入AI作实证锚点"""
        try:
            from knowledge_base.feature_matcher import query_from_engine, build_empirical_reference_section
        except Exception:
            try:
                from feature_matcher import query_from_engine, build_empirical_reference_section
            except Exception:
                return ""
        if not beat_info:
            return ""
        intensity = beat_info.get("intensity", 0.5)
        emotion_key = self._infer_emotion(beat_info, shot_index)
        query = query_from_engine(
            self.style, self.knowledge.genre_key, self.knowledge.director_keys,
            self.audience_archetype, self.is_vertical, intensity, emotion_key,
        )
        base = build_empirical_reference_section(query, top_k=2)
        # 追加富信息对标(用户要求的全部10维度: 故事推进/画面/镜头/运镜转场/叙事/氛围/节奏/剪辑/剧本/分镜)
        try:
            try:
                from knowledge_base.works_rich import build_rich_reference
            except ImportError:
                from works_rich import build_rich_reference
            rich = build_rich_reference(query.get("tags", []), top_k=1)
            if rich:
                base = (base + "\n" + rich) if base else rich
        except Exception:
            pass
        return base

    def _build_creation_skills_ref(self):
        """创作技法对标: 全网检索skill(爆款元素/平台算法/黄金前N秒)注入"""
        try:
            from knowledge_base.creation_skills import build_creation_skills_section
        except Exception:
            try:
                from creation_skills import build_creation_skills_section
            except Exception:
                return ""
        # 用风格/类型/受众构造query_tags
        from knowledge_base.feature_matcher import STYLE_TO_QUERY_TAGS
        tags = STYLE_TO_QUERY_TAGS.get(self.style, [])
        if self.audience_archetype:
            tags = tags + [self.audience_archetype]
        return build_creation_skills_section(tags, self.is_vertical, self.mode)

    def _build_dimension_guide(self):
        """输出侧重维度指导: 按output_focus注入对应维度模块(角色/环境/故事/氛围/互动)"""
        try:
            try:
                from knowledge_base.dimension_design import build_dimension_section
            except ImportError:
                from dimension_design import build_dimension_section
        except Exception:
            return ""
        # output_focus中文→英文维度key
        focus_map = {
            "角色设计": "character", "角色": "character",
            "环境设计": "environment", "环境": "environment",
            "故事情节": "story", "故事": "story",
            "画面氛围": "atmosphere", "氛围": "atmosphere",
            "互动交互": "interaction", "互动": "interaction",
        }
        dim_key = focus_map.get(self.output_focus, "")
        if not dim_key:
            return ""
        return build_dimension_section(dim_key)

    # ============================================================
    # Phase 3 改造: 决策层真实注入
    # 真实接通 DIRECTOR_DECISION / NARRATIVE_DECISION / DIRECTOR_PIPELINE
    # 把死数据变成对 prompt 的活指导
    # ============================================================
    def _build_decision_layer(self):
        """决策层真实注入 — 4 个被忽略的决策 dict 现在真实参与 prompt 构造"""
        parts = []

        # 1. DIRECTOR_DECISION: 导演决策覆盖层
        if self.knowledge.director_keys:
            try:
                from knowledge_base.director_styles import DIRECTOR_DECISION
            except ImportError:
                DIRECTOR_DECISION = {}
            for dk in self.knowledge.director_keys[:3]:
                d = DIRECTOR_DECISION.get(dk, {})
                if not d:
                    continue
                cn = DIRECTOR_STYLES.get(dk, {}).get("cn", dk)
                parts.append(f"【导演决策层 - {cn}】")
                if d.get("trigger"):
                    parts.append(f"  ▸ 触发条件/适用场景: {d['trigger']}")
                if d.get("failure_modes"):
                    fm = " / ".join(str(x) for x in d["failure_modes"][:3] if x)
                    if fm:
                        parts.append(f"  ▸ 必须避免的失败模式: {fm}")
                if d.get("measurement"):
                    parts.append(f"  ▸ 自检/验收标准: {d['measurement']}")
                if d.get("alternatives"):
                    alt = " / ".join(str(x) for x in d["alternatives"][:2] if x)
                    if alt:
                        parts.append(f"  ▸ 备选导演风格参考: {alt}")

        # 2. NARRATIVE_DECISION: 叙事结构决策层
        if self.narrative_structure:
            try:
                from knowledge_base.narrative_structures import NARRATIVE_DECISION
            except ImportError:
                NARRATIVE_DECISION = {}
            nd = NARRATIVE_DECISION.get(self.narrative_structure, {})
            if nd:
                parts.append(f"【叙事决策层 - {self.narrative_structure}】")
                # 保留 trigger/failure/measurement 三件套
                for k in ("trigger", "failure_modes", "measurement", "rationale", "alternatives", "structure_template"):
                    v = nd.get(k)
                    if not v:
                        continue
                    if isinstance(v, str):
                        parts.append(f"  ▸ {k}: {v}")
                    elif isinstance(v, list) and v:
                        parts.append(f"  ▸ {k}: {' / '.join(str(x) for x in v[:3])}")

        # 3. DIRECTOR_PIPELINE: 导演工作流速查
        if self.knowledge.director_keys:
            try:
                from knowledge_base.director_pipeline import DIRECTOR_PIPELINE, PIPELINE_QUICKREF
            except ImportError:
                DIRECTOR_PIPELINE = {}
                PIPELINE_QUICKREF = {}
            # PIPELINE_QUICKREF 是所有导演的速查表
            if PIPELINE_QUICKREF:
                parts.append("【导演工作流速查 - 所有导演共性】")
                for k in ("pre_production", "production_principles", "post_production", "key_metrics"):
                    v = PIPELINE_QUICKREF.get(k)
                    if v and isinstance(v, str):
                        parts.append(f"  ▸ {k}: {v[:200]}")
            # DIRECTOR_PIPELINE 是按导演分类的
            for dk in self.knowledge.director_keys[:2]:
                pipe = DIRECTOR_PIPELINE.get(dk, {})
                if pipe:
                    cn = DIRECTOR_STYLES.get(dk, {}).get("cn", dk)
                    parts.append(f"【导演工作流 - {cn}】")
                    for k, v in pipe.items():
                        if isinstance(v, str) and v:
                            parts.append(f"  ▸ {k}: {v[:200]}")

        # 4. STYLE_SUBDIVISIONS: 风格细分(用户选细分时注入)
        try:
            from knowledge_base.style_subdivisions import STYLE_SUBDIVISIONS, SUBDIVISION_TO_GENRE
        except ImportError:
            STYLE_SUBDIVISIONS = {}
            SUBDIVISION_TO_GENRE = {}
        # 1) 直接查 style 或 genre_key — value 是 dict
        style_sub_dict = STYLE_SUBDIVISIONS.get(self.style) or STYLE_SUBDIVISIONS.get(self.knowledge.genre_key or "", {})
        # 2) 查 SUBDIVISION_TO_GENRE 找映射到当前 genre 的所有子分类
        if not style_sub_dict and self.knowledge.genre_key:
            matched_subs = [sub for sub, gen in SUBDIVISION_TO_GENRE.items() if gen == self.knowledge.genre_key]
            if matched_subs:
                # 取第一个匹配的子分类作为代表
                first_match = matched_subs[0]
                style_sub_dict = STYLE_SUBDIVISIONS.get(first_match, {})
                if style_sub_dict:
                    style_sub_dict = dict(style_sub_dict, _matched_keys=" / ".join(matched_subs[:4]))
        if style_sub_dict:
            cn = style_sub_dict.get("cn", "")
            trigger = style_sub_dict.get("trigger", "")
            if cn:
                sub_label = style_sub_dict.get("_matched_keys", cn)
                parts.append(f"【风格细分 - {sub_label}】: {cn}")
            if trigger:
                parts.append(f"  ▸ 触发场景: {trigger}")

        return "\n".join(parts) if parts else ""

    # ============================================================
    # Phase 4 改造: output_focus 真实差异化
    # 6 个侧重维度真的让 prompt 结构和权重变化
    # ============================================================
    def _build_output_focus_focus(self):
        """输出侧重 真实差异化 — 6 维度各有专门指导,真改 prompt 结构和权重"""
        if not self.output_focus or self.output_focus in ("分镜", "分镜(默认)"):
            return ""

        # 6 个维度的真实差异化指导(非装饰)
        focus_specs = {
            "角色设计": {
                "title": "角色设计维度",
                "weight": [
                    "外貌(年龄/身高/体型/肤色/发型/标志特征)权重 ×3",
                    "服装(款式/材质/颜色/时代)权重 ×2",
                    "表情微动作(眼/嘴/手/肩)权重 ×3,占描述 50%",
                    "角色弧光变化贯穿全程,逐镜记录",
                    "角色间关系张力(1 句话)"
                ],
                "template": (
                    "每个分镜/页面按以下结构输出:\n"
                    "外貌特征: (年龄/身高/体型/肤色/发型/标志特征,仅在变化时输出)\n"
                    "服装细节: (款式/材质/颜色/时代,仅在变化时输出)\n"
                    "表情微动作: (眼/嘴/手/肩的可见变化)\n"
                    "心理状态: (通过肢体暗示,不直说情绪)\n"
                    "角色关系张力: (一句话)"
                ),
                "forbidden": ["禁止写角色动作叙事", "禁止笼统'表情复杂'", "禁止外观+动作混合输出"]
            },
            "环境设计": {
                "title": "环境设计维度",
                "weight": [
                    "空间结构(室内/室外/尺度/纵深)权重 ×3",
                    "建筑/地形/植被细节 ×2",
                    "光影氛围(光源/色温/方向/强度)权重 ×3",
                    "道具符号(时代/身份/剧情伏笔) ×2",
                    "环境与人物的关系(压迫/庇护/对比) ×2"
                ],
                "template": (
                    "每个分镜/页面按以下结构输出:\n"
                    "空间结构: (室内/室外/尺度/纵深/动线)\n"
                    "建筑/地形/植被: (具体类型/形态/材质)\n"
                    "光影氛围: (光源/色温/方向/强度/阴影)\n"
                    "道具符号: (时代/身份/剧情伏笔)\n"
                    "环境与人物: (压迫/庇护/对比)"
                ),
                "forbidden": ["禁止只写'美丽的风景'", "禁止忽略光影", "禁止人物描述喧宾夺主"]
            },
            "故事情节": {
                "title": "故事情节维度",
                "weight": [
                    "事件推进(起因/经过/结果)权重 ×3",
                    "冲突与反转(明/暗线)权重 ×3",
                    "伏笔/呼应/因果链 ×2",
                    "角色动机与决策依据 ×2",
                    "时间线与信息差 ×2"
                ],
                "template": (
                    "每个分镜/页面按以下结构输出:\n"
                    "事件: (这镜推进了什么情节)\n"
                    "冲突: (明/暗线冲突)\n"
                    "伏笔/呼应: (本镜埋伏/回收的线索)\n"
                    "动机: (角色为何这样做)\n"
                    "信息差: (观众知道但角色不知道/反之)"
                ),
                "forbidden": ["禁止纯静态画面", "禁止无冲突的过渡镜", "禁止忽略因果"]
            },
            "画面氛围": {
                "title": "画面氛围维度",
                "weight": [
                    "光影(冷暖/明暗/方向)权重 ×3",
                    "色调(主色/辅色/对比)权重 ×3",
                    "质感(胶片/数字/复古/赛博) ×2",
                    "情绪与画面对应(避免直白) ×2",
                    "留白与构图张力 ×2"
                ],
                "template": (
                    "每个分镜/页面按以下结构输出:\n"
                    "光影: (主光源/辅光/方向/强度/阴影形态)\n"
                    "色调: (主色 1-2 种/辅色/对比关系)\n"
                    "质感: (胶片颗粒/数字锐利/复古滤镜/赛博色调)\n"
                    "情绪映射: (用画面暗示情绪,不用情绪词)\n"
                    "构图: (中心/偏置/留白/视觉张力)"
                ),
                "forbidden": ["禁止情绪词直白", "禁止光影与情绪脱节", "禁止平面无层次"]
            },
            "互动交互": {
                "title": "互动交互维度",
                "weight": [
                    "钩子(前 3 秒抓人)权重 ×3",
                    "选择/分支/评论引导 ×3",
                    "情绪共振点(高光时刻) ×2",
                    "分享/转化/收藏触发 ×2",
                    "节奏(快/慢/转) ×2"
                ],
                "template": (
                    "每个分镜/页面按以下结构输出:\n"
                    "钩子: (本镜如何抓人/制造好奇)\n"
                    "选择点: (本镜是否留分支/评论引导)\n"
                    "情绪共振: (高光/反转/金句)\n"
                    "分享触发: (为何要转发/收藏)\n"
                    "节奏: (快/慢/转,前后节奏对比)"
                ),
                "forbidden": ["禁止无钩子开头", "禁止平淡无冲突", "禁止忽略情绪高点"]
            },
        }
        spec = focus_specs.get(self.output_focus, {})
        if not spec:
            return ""

        lines = [f"【输出侧重 - {spec['title']}】"]
        lines.append("权重调整:")
        for w in spec["weight"]:
            lines.append(f"  ★ {w}")
        lines.append("\n输出模板:")
        lines.append(spec["template"])
        if spec.get("forbidden"):
            lines.append("\n禁止项:")
            for f in spec["forbidden"]:
                lines.append(f"  ✗ {f}")
        return "\n".join(lines)


    def _build_emotion_rendering_guide(self, beat_info):
        """情感渲染技法指导(从EMOTION_RENDERING_DECISION抽取how-to, 接线非死数据)"""
        if not beat_info:
            return ""
        try:
            from knowledge_base.emotion_rendering import EMOTION_RENDERING_DECISION
        except Exception:
            return ""
        # 按叙事功能选2个最相关渲染技法
        func = beat_info.get("narrative_func", "")
        intensity = beat_info.get("intensity", 0.5)
        # 选技法: 高强度→rhythm_emotion/sound_emotion; 情感戏→externalization/substitution
        if intensity > 0.7:
            keys = ["sound_emotion", "rhythm_emotion"]
        elif "识破" in func or "揭示" in func or "反转" in func:
            keys = ["externalization", "substitution"]
        else:
            keys = ["externalization", "contrast_carrier"]
        lines = ["【情感渲染技法指导】"]
        for k in keys:
            d = EMOTION_RENDERING_DECISION.get(k, {})
            if not d:
                continue
            lines.append(f"  ◆ {k}: {d.get('trigger', '')}")
            if d.get("rationale"):
                lines.append(f"    原理: {d['rationale']}")
            if d.get("failure_modes"):
                lines.append(f"    失败模式(避免): {'; '.join(d['failure_modes'][:2])}")
            if d.get("measurement"):
                lines.append(f"    验收: {d['measurement']}")
        return "\n".join(lines)

    def _build_viral_guide(self, shot_index):
        """短视频技法指导(从VIRAL_VIDEO_DECISION抽取, 接线非死数据)"""
        try:
            from knowledge_base.viral_video_techniques import VIRAL_VIDEO_DECISION
        except Exception:
            return ""
        # 按shot位置选技法: 开场→pattern_interrupt/curiosity_gap; 中段→dopamine_loops; 全程→show_dont_tell
        total = max(self.total_shots, 1)
        progress = shot_index / total
        if progress < 0.2:
            keys = ["pattern_interrupt", "curiosity_gap"]
        elif progress < 0.8:
            keys = ["dopamine_loops", "show_dont_tell"]
        else:
            keys = ["show_dont_tell", "emotional_anchoring"]
        lines = ["【短视频技法指导】"]
        for k in keys:
            d = VIRAL_VIDEO_DECISION.get(k, {})
            if not d:
                continue
            lines.append(f"  ◆ {k}: {d.get('trigger', '')}")
            if d.get("rationale"):
                lines.append(f"    原理: {d['rationale']}")
            if d.get("failure_modes"):
                lines.append(f"    失败模式(避免): {'; '.join(d['failure_modes'][:2])}")
            if d.get("measurement"):
                lines.append(f"    验收: {d['measurement']}")
        return "\n".join(lines)

    def _build_iron_rules(self):
        rules = [
            "【画面铁律(必须遵守)】",
            "1. 禁止抽象词: 禁止'悲伤''紧张'等情绪词,只用可见的面部动作/肢体/环境来传递情绪",
            "2. 饱满叙事: 每镜3-6句,充分描写场景氛围和角色动态",
            "3. 镜头连续性: 角色位置、光线、道具必须与上一镜一致",
            "4. 禁止参数: 不写焦距mm、色温K等数值",
            "5. 时空锚定: 开头用'时间·空间'前缀(如'清晨·森林小屋厨房')",
            "6. 180度不越轴: 角色视线和站位方向保持一致",
            "7. 单镜凝固动作: 每镜只描述一个凝固的瞬间动作",
            "8. 风格统一: 角色外貌服装色彩基调所有镜头严格一致",
            "9. 对话框绑定角色: 多角色时明确指向",
            "10. 变化标注: 仅在场景/角色有大变化时输出变化描述",
        ]
        if self.is_vertical:
            rules.extend([
                "11. 竖屏构图: 主体始终在纵轴中心线,面部占比70%+(情感场景)",
                "12. 竖屏运镜: 以推拉/升降为主,禁止大幅度横摇",
            ])
        return "\n".join(rules)

    def _build_output_instruction(self, shot_index):
        return (
            f"请直接输出第{shot_index+1}个镜头的内容。只输出这一个镜头。\n"
            f"输出中不要包含**、-、#等符号标记。直接输出纯文字。\n"
            f"格式: 景别+时间空间锚定+画面描述(3-6句)+运镜+转场+时长+台词(如有)"
        )

    def _map_emotion_key(self, emotion_value):
        if emotion_value > 0.75:
            return "joy"
        elif emotion_value > 0.55:
            return "love"
        elif emotion_value > 0.4:
            return "determination"
        elif emotion_value > 0.25:
            return "sadness"
        else:
            return "fear"

    def _extract_summary(self, text):
        if not text:
            return "(AI调用失败)"
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        # 取前2行非空内容作为摘要
        summary_lines = []
        for line in lines[:5]:
            if not line.startswith(("景别", "运镜", "转场", "时长", "备注")):
                summary_lines.append(line)
            if len(summary_lines) >= 2:
                break
        return " ".join(summary_lines)[:120] if summary_lines else lines[0][:80] if lines else "未知"

    def _extract_field(self, text, field_name):
        if not text:
            return ""
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith(f"{field_name}：") or line.startswith(f"{field_name}:"):
                return line.split("：", 1)[-1].split(":", 1)[-1].strip()
        return ""
