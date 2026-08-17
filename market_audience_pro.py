# -*- coding: utf-8 -*-
"""
MarketAudiencePro - 市场受众节点 (环节 36)
================================================
Phase 28 P1 - AIGC 影视全流程解析 补全节点

数据源 (Phase 28 联网研究):
- 2024/2025 中国电影市场及观众变化趋势报告 (中国电影家协会 + 灯塔研究院)
- 类型片市场分析 (豆丁网 40 页报告)
- 票房剖析资料
- 6 大观众偏好 (男/女/老/青/一二三线/网络平台)

核心能力:
- 8 大类型片受众画像
- 5 大档期策略
- 3 大市场定位 (头部/腰部/黑马)
- 4 维票房预测 (质量/演员/营销/档期)
- 5 维风险评估
- 受众-类型-档期-营销 4 维矩阵
"""
from __future__ import annotations

import json

try:
    from anti_ai_vocab import clean_anti_ai_text, inject_anti_ai_rules
    _HAS_ANTI_AI = True
except Exception:
    _HAS_ANTI_AI = False


# ============================================================
# 8 大类型片 + 受众画像 (基于 2024-2025 中国电影市场报告)
# ============================================================
GENRE_AUDIENCE_8 = {
    "动作": {
        "name_zh": "动作片",
        "primary_audience": "男性 18-45 岁, 一二线城市",
        "secondary_audience": "动作片爱好者, 漫改/特效片观众",
        "market_share": "类型片 TOP 4, 占票房 ~15%",
        "key_drivers": ["特效", "打斗", "速度", "英雄主义"],
        "examples": ["战狼", "速度与激情", "红海行动"],
        "best_release": "暑期档 / 春节档 / 国庆档",
        "risk": "中 (类型成熟, 依赖特效投入)",
    },
    "喜剧": {
        "name_zh": "喜剧片",
        "primary_audience": "女性 25-45 岁 + 男性 30-50 岁, 全线城市",
        "secondary_audience": "合家欢, 春节档观众",
        "market_share": "类型片 TOP 1, 占票房 ~20%",
        "key_drivers": ["笑点", "共鸣", "合家欢", "解压"],
        "examples": ["唐人街探案", "你好李焕英", "满江红"],
        "best_release": "春节档 / 暑期档",
        "risk": "低 (刚需类型, 受众广)",
    },
    "爱情": {
        "name_zh": "爱情片",
        "primary_audience": "女性 18-35 岁, 一二线城市",
        "secondary_audience": "情侣, 节日档观众",
        "market_share": "中腰部 ~8%",
        "key_drivers": ["情感共鸣", "CP", "颜值", "节日"],
        "examples": ["前任3", "后来的我们", "爱情神话"],
        "best_release": "情人节 / 七夕 / 520",
        "risk": "中 (依赖 CP 效应)",
    },
    "悬疑": {
        "name_zh": "悬疑/犯罪片",
        "primary_audience": "男性 25-45 岁 + 女性 25-40 岁, 一二线城市",
        "secondary_audience": "推理迷, 烧脑片观众",
        "market_share": "新晋头部 ~12%",
        "key_drivers": ["烧脑", "反转", "推理", "悬念"],
        "examples": ["唐人街探案", "无双", "消失的她"],
        "best_release": "暑期档 / 国庆档 / 贺岁档",
        "risk": "中 (依赖剧本质量)",
    },
    "科幻": {
        "name_zh": "科幻片",
        "primary_audience": "男性 18-40 岁, 一二线 + 高线市场",
        "secondary_audience": "科幻迷, 特效爱好者",
        "market_share": "潜力头部 ~10%",
        "key_drivers": ["世界观", "特效", "未来感", "硬核"],
        "examples": ["流浪地球", "疯狂的外星人", "上海堡垒"],
        "best_release": "春节档 / 暑期档",
        "risk": "高 (投入大, 受众窄)",
    },
    "动画": {
        "name_zh": "动画片",
        "primary_audience": "家庭 + 女性 18-35 岁 + 儿童",
        "secondary_audience": "二次元, IP 粉",
        "market_share": "现象级 ~18% (哪吒 2 等)",
        "key_drivers": ["IP", "视效", "合家欢", "情感"],
        "examples": ["哪吒之魔童闹海", "长安三万里", "姜子牙"],
        "best_release": "春节档 / 暑期档 / 儿童节",
        "risk": "中 (依赖 IP 和口碑)",
    },
    "战争": {
        "name_zh": "战争/历史片",
        "primary_audience": "男性 35-60 岁 + 红色观众, 全线城市",
        "secondary_audience": "主旋律, 爱国情怀",
        "market_share": "新主流 ~10%",
        "key_drivers": ["家国情怀", "历史", "英雄", "正能量"],
        "examples": ["长津湖", "我和我的祖国", "四渡"],
        "best_release": "国庆档 / 春节档 / 建军节",
        "risk": "中 (政策导向, 口碑关键)",
    },
    "现实主义": {
        "name_zh": "现实主义题材",
        "primary_audience": "女性 25-45 岁 + 男性 30-50 岁, 一二三线",
        "secondary_audience": "文艺片观众, 影迷",
        "market_share": "新增长点 ~8%",
        "key_drivers": ["社会议题", "小人物", "情感共鸣", "深度"],
        "examples": ["我不是药神", "我的姐姐", "人生大事"],
        "best_release": "暑期档 / 国庆档 / 春季档",
        "risk": "中 (依赖口碑)",
    },
}


# ============================================================
# 5 大档期策略
# ============================================================
RELEASE_PERIODS_5 = {
    "春节档": {
        "name_zh": "春节档 (2 月)",
        "duration": "7-15 天 (除夕-初七)",
        "competition": "高 (年度最热档期, 10+ 大片)",
        "best_genres": ["喜剧", "动画", "战争", "科幻"],
        "audience": "全家, 县城下沉市场, 合家欢",
        "box_office_share": "全年 ~25%",
        "strategy": "头部大片必争, 中小成本避让",
    },
    "暑期档": {
        "name_zh": "暑期档 (7-8 月)",
        "duration": "60 天",
        "competition": "中 (学生放假, 流量高峰)",
        "best_genres": ["动作", "喜剧", "科幻", "动画", "悬疑"],
        "audience": "年轻人 18-30 岁, 学生",
        "box_office_share": "全年 ~30%",
        "strategy": "类型片天堂, 中等大片必争",
    },
    "国庆档": {
        "name_zh": "国庆档 (10 月)",
        "duration": "7 天",
        "competition": "中 (主旋律窗口)",
        "best_genres": ["战争", "现实主义", "悬疑", "喜剧"],
        "audience": "合家欢, 主旋律观众, 县城市场",
        "box_office_share": "全年 ~12%",
        "strategy": "主旋律+合家欢, 中等大片",
    },
    "贺岁档": {
        "name_zh": "贺岁档 (12 月)",
        "duration": "30-45 天",
        "competition": "中 (圣诞+元旦)",
        "best_genres": ["喜剧", "悬疑", "爱情", "现实主义"],
        "audience": "年轻人 25-40 岁, 文艺观众",
        "box_office_share": "全年 ~10%",
        "strategy": "中等成本+口碑片",
    },
    "非档期": {
        "name_zh": "非档期 (3-6 月, 9 月, 11 月)",
        "duration": "分散",
        "competition": "低 (腰部空间大)",
        "best_genres": ["爱情 (情人节/七夕)", "悬疑", "现实主义", "小众文艺"],
        "audience": "一二线城市, 影迷",
        "box_office_share": "全年 ~23% (分线发行潜力)",
        "strategy": "腰部中低成本, 类型化精准定位",
    },
}


# ============================================================
# 3 大市场定位
# ============================================================
MARKET_POSITION_3 = {
    "头部": {
        "name_zh": "头部大片 (Blockbuster)",
        "investment": ">=3 亿",
        "box_office_target": ">=10 亿",
        "share_target": "TOP 3 头部 90% 市场份额",
        "strategies": [
            "IP 化 (改编/续集/系列)",
            "全明星阵容",
            "重金特效",
            "主流档期 (春节/暑期/国庆)",
            "全面营销覆盖",
        ],
        "examples": ["流浪地球2", "满江红", "战狼2"],
    },
    "腰部": {
        "name_zh": "腰部中成本 (Mid-budget)",
        "investment": "5000 万-3 亿",
        "box_office_target": "1-10 亿",
        "share_target": "类型片头部 (单类型 TOP 3)",
        "strategies": [
            "类型化精准 (悬疑/爱情/喜剧)",
            "中等档期 (贺岁/春季/非档期)",
            "社交媒体营销 (短视频/KOL)",
            "分众口碑发酵",
        ],
        "examples": ["消失的她", "长安三万里", "孤注一掷"],
    },
    "黑马": {
        "name_zh": "黑马逆袭 (Dark Horse)",
        "investment": "<=5000 万",
        "box_office_target": "1-5 亿 (逆袭)",
        "share_target": "口碑发酵, 长尾效应",
        "strategies": [
            "极致口碑 (豆瓣 8.0+)",
            "题材稀缺 (现实议题/创新类型)",
            "社交媒体自来水",
            "低投入高回报",
        ],
        "examples": ["给阿嬷的情书", "长安三万里 (初期)", "我不是药神"],
    },
}


# ============================================================
# 4 维票房预测评分
# ============================================================
def predict_box_office(genre="动作", period="暑期档", director_popularity=0.7,
                       cast_popularity=0.6, marketing_budget=0.5, quality_score=0.7,
                       position="腰部"):
    """
    票房预测 (启发式)

    Returns:
        dict {
            "score": 综合评分 0-1,
            "box_office_estimate": 票房预估 (亿),
            "risk_level": 风险等级,
            "recommendation": 建议,
        }
    """
    # 1. 类型基础分
    genre_info = GENRE_AUDIENCE_8.get(genre, GENRE_AUDIENCE_8["动作"])
    type_score = {
        "喜剧": 0.85, "动画": 0.80, "动作": 0.75, "悬疑": 0.70,
        "科幻": 0.65, "现实主义": 0.65, "战争": 0.60, "爱情": 0.55,
    }.get(genre, 0.7)

    # 2. 档期加分
    period_info = RELEASE_PERIODS_5.get(period, RELEASE_PERIODS_5["暑期档"])
    period_bonus = {
        "春节档": 0.20, "暑期档": 0.15, "国庆档": 0.10,
        "贺岁档": 0.05, "非档期": -0.10,
    }.get(period, 0)

    # 3. 5 维加权
    quality = quality_score * 0.35
    director_p = director_popularity * 0.20
    cast_p = cast_popularity * 0.15
    marketing = marketing_budget * 0.15
    type = type_score * 0.15

    total = quality + director_p + cast_p + marketing + type + period_bonus
    total = max(0.0, min(1.0, total))

    # 4. 票房预估 (基于定位)
    position_info = MARKET_POSITION_3.get(position, MARKET_POSITION_3["腰部"])
    if position == "头部":
        base_box = 10.0
    elif position == "腰部":
        base_box = 3.0
    else:
        base_box = 0.8
    box_office = base_box * (0.5 + total)

    # 5. 风险等级
    if total >= 0.7:
        risk = "低"
    elif total >= 0.5:
        risk = "中"
    else:
        risk = "高"

    # 6. 建议
    if total >= 0.8:
        rec = "强烈推荐 - 高质量 + 主流档期 + 合适类型"
    elif total >= 0.6:
        rec = "推荐 - 良好基础, 可推进"
    elif total >= 0.4:
        rec = "谨慎 - 需要优化某维度"
    else:
        rec = "风险高 - 建议重新评估"

    return {
        "score": round(total, 3),
        "box_office_estimate_yi": round(box_office, 2),
        "risk_level": risk,
        "recommendation": rec,
        "genre_info": genre_info,
        "period_info": period_info,
        "position_info": position_info,
    }


# ============================================================
# ComfyUI 节点
# ============================================================
class MarketAudiencePro:
    """
    市场受众 Pro 节点 - Phase 28 P1
    环节 36 - 受众画像 + 市场定位 + 票房预测

    自动赋予: 默认 动作+暑期档+腰部
    专项调整: 8 类型 + 5 档期 + 3 定位 + 5 维评分
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "类型": (list(GENRE_AUDIENCE_8.keys()) + ["auto"], {"default": "动作"}),
                "档期": (list(RELEASE_PERIODS_5.keys()) + ["auto"], {"default": "暑期档"}),
                "市场定位": (list(MARKET_POSITION_3.keys()) + ["auto"], {"default": "腰部"}),
            },
            "optional": {
                "导演知名度": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05}),
                "演员阵容": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.05}),
                "营销预算": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "质量评分": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("市场分析", "受众画像", "档期策略", "票房预测")
    FUNCTION = "analyze"
    CATEGORY = "Director/Market"

    def analyze(self, **kwargs):
        genre = kwargs.get("类型", "动作")
        if genre == "auto":
            genre = "动作"
        period = kwargs.get("档期", "暑期档")
        if period == "auto":
            period = "暑期档"
        position = kwargs.get("市场定位", "腰部")
        if position == "auto":
            position = "腰部"

        result = predict_box_office(
            genre=genre,
            period=period,
            director_popularity=kwargs.get("导演知名度", 0.7),
            cast_popularity=kwargs.get("演员阵容", 0.6),
            marketing_budget=kwargs.get("营销预算", 0.5),
            quality_score=kwargs.get("质量评分", 0.7),
            position=position,
        )

        # 1. 市场分析
        market = "【市场分析】\n类型: {} | 档期: {} | 定位: {}\n综合评分: {:.3f} | 风险: {}\n建议: {}\n预估票房: {:.1f} 亿".format(
            genre, period, position, result["score"], result["risk_level"],
            result["recommendation"], result["box_office_estimate_yi"]
        )

        # 2. 受众画像
        gi = result["genre_info"]
        audience = "【受众画像】\n主要: {}\n次要: {}\n市场份额: {}\n关键驱动: {}\n代表作品: {}\n风险等级: {}".format(
            gi["primary_audience"], gi["secondary_audience"], gi["market_share"],
            gi["key_drivers"], gi["examples"], gi["risk"]
        )

        # 3. 档期策略
        pi = result["period_info"]
        period_str = "【档期策略】\n档期: {} ({} 天)\n竞争: {}\n最佳类型: {}\n受众: {}\n票房占比: {}\n策略: {}".format(
            pi["name_zh"], pi["duration"], pi["competition"], pi["best_genres"],
            pi["audience"], pi["box_office_share"], pi["strategy"]
        )

        # 4. 票房预测 (JSON)
        forecast = json.dumps({
            "score": result["score"],
            "box_office_yi": result["box_office_estimate_yi"],
            "risk": result["risk_level"],
            "recommendation": result["recommendation"],
        }, ensure_ascii=False, indent=2)

        return (market, audience, period_str, forecast)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "MarketAudiencePro": MarketAudiencePro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "MarketAudiencePro": "📊 市场受众 Pro (环节36) — Phase 28 P1 / 8类型+5档期+3定位+4维评分",
# }
