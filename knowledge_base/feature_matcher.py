# -*- coding: utf-8 -*-
# ============================================================
# 概率特征匹配引擎 V1.0
# ============================================================
# 把新项目特征 与 语料库作品 做概率匹配,
# 返回 top-K 最相似的真实作品 + 其情节/叙述/情感特征(注入AI作实证对标)
#
# 匹配维度(加权):
#   1. matchable_tags 标签重叠 (Jaccard, 权重最高)
#   2. genre 类型匹配 (重叠数)
#   3. target_audience 受众匹配
#   4. type 作品类型匹配 (电影/短剧/短视频)
#   5. vertical 竖屏匹配
#   6. intensity_avg 强度数值距离 (越近越高分)
#   7. emotion_dominant 情绪主调匹配
# 输出: [{work, score(0-1), matched_dims, features_to_inject}]
# ============================================================

try:
    from knowledge_base.works_corpus import WORKS_CORPUS, get_work, get_all_works
except ImportError:
    from works_corpus import WORKS_CORPUS, get_work, get_all_works


def _jaccard(a, b):
    """Jaccard相似度"""
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    inter = sa & sb
    return len(inter) / len(sa | sb)


def _normalize_intensity(emotion_curve):
    """从emotion_curve估算平均强度(0-1)"""
    if not emotion_curve:
        return 0.5
    return sum(emotion_curve) / len(emotion_curve)


def match_works(query, top_k=3):
    """
    概率特征匹配: query → top-K 最相似作品

    query字段(可选, 缺省用默认):
      type: 电影/短剧/短视频
      genres: [list]
      style: 风格key(映射genre)
      directors: [director keys]
      audience: 受众key(男频/女频/银发/知识型/全年龄/成人/家庭/...)
      vertical: bool
      intensity: 0-1 (估算或从beat)
      emotion: emotion_dominant关键词
      tags: 额外matchable_tags(从风格/叙事功能推断)
    """
    q_type = query.get("type", "")
    q_genres = set(query.get("genres", []))
    q_directors = set(query.get("directors", []))
    q_audience = query.get("audience", "")
    q_vertical = query.get("vertical", None)
    q_intensity = query.get("intensity", None)
    q_emotion = query.get("emotion", "")
    q_tags = set(query.get("tags", []))

    results = []
    for w in get_all_works():
        score = 0.0
        matched = []

        # 1. matchable_tags Jaccard (权重0.35) — 最重要
        w_tags = set(w.get("matchable_tags", []))
        tag_sim = _jaccard(q_tags, w_tags) if q_tags else 0.0
        # 也考虑query genres是否命中作品tags
        genre_in_tags = len(q_genres & w_tags) / max(len(q_genres), 1) if q_genres else 0
        tag_score = max(tag_sim, genre_in_tags * 0.7) * 0.35
        score += tag_score
        if tag_sim > 0 or genre_in_tags > 0:
            matched.append(f"标签/类型({tag_sim:.2f})")

        # 2. genre 直接重叠 (权重0.15)
        w_genres = set(w.get("genre", []))
        genre_overlap = len(q_genres & w_genres)
        genre_score = min(genre_overlap * 0.15, 0.15)
        score += genre_score
        if genre_overlap:
            matched.append(f"genre({genre_overlap})")

        # 3. director 命中 (权重0.15) — 导演匹配是强信号
        w_dir = w.get("director", "")
        if w_dir in q_directors:
            score += 0.15
            matched.append(f"导演{w_dir}")

        # 4. target_audience 匹配 (权重0.10)
        w_aud = w.get("target_audience", "")
        if q_audience and q_audience in w_aud:
            score += 0.10
            matched.append(f"受众{q_audience}")
        elif q_audience and any(k in w_aud for k in [q_audience]):
            score += 0.05
            matched.append(f"受众近似")

        # 5. type 匹配 (权重0.10)
        if q_type and w.get("type") == q_type:
            score += 0.10
            matched.append(f"类型{q_type}")

        # 6. vertical 匹配 (权重0.05)
        if q_vertical is not None and w.get("vertical") == q_vertical:
            score += 0.05
            matched.append("竖屏")

        # 7. intensity 数值距离 (权重0.05)
        if q_intensity is not None:
            w_int = w.get("features", {}).get("intensity_avg", _normalize_intensity(w.get("emotion_curve", [])))
            dist = abs(q_intensity - w_int)
            int_score = max(0, 0.05 - dist * 0.05)
            score += int_score
            if dist < 0.2:
                matched.append(f"强度近({w_int:.2f})")

        # 8. emotion_dominant 关键词 (权重0.05)
        w_emo = w.get("features", {}).get("emotion_dominant", "")
        if q_emotion and (q_emotion in w_emo or any(k in w_emo for k in [q_emotion])):
            score += 0.05
            matched.append(f"情绪{q_emotion}")

        results.append({
            "work_id": w.get("id") or w.get("work_id", ""),
            "work_cn": w.get("cn") or w.get("title_cn") or w.get("title", ""),
            "work_type": w.get("type") or (w.get("genre", ["未分类"])[0] if w.get("genre") else "未分类"),
            "score": round(score, 3),
            "matched_dims": matched,
            "director": w.get("director") or w.get("director_display", ""),
            "plot_pattern": w.get("plot_pattern", ""),
            "narrative_structure": w.get("narrative_structure", ""),
            "pacing": w.get("pacing", ""),
            "opening_hook": w.get("opening_hook", ""),
            "key_techniques": w.get("key_techniques", []),
            "features": w.get("features", {}),
            "matchable_tags": w.get("matchable_tags", []),
        })

    # 按score降序, 取top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def build_empirical_reference_section(query, top_k=2):
    """构建实证对标章节(注入AI提示): 返回文本"""
    matches = match_works(query, top_k=top_k)
    if not matches or matches[0]["score"] < 0.05:
        return ""
    lines = ["【实证作品对标(概率匹配)】"]
    for m in matches:
        conf = m["score"]
        lines.append(
            f"  ◆ {m['work_cn']}({m['work_type']}, 导:{m['director']}) "
            f"匹配置信:{conf:.0%} — {';'.join(m['matched_dims'][:3])}"
        )
        f = m["features"]
        lines.append(f"    情节推进: {m['plot_pattern']}")
        lines.append(f"    叙述特征: {f.get('narrative_style','')}")
        lines.append(f"    情感特征: {f.get('emotion_signature','')}")
        lines.append(f"    节奏: {m['pacing']}")
        if m["key_techniques"]:
            lines.append(f"    标志技法: {', '.join(m['key_techniques'][:4])}")
    lines.append("  要求: 借鉴对标作品的情节推进/叙述/情感特征, 但不抄袭, 融入本故事。")
    return "\n".join(lines)


# 风格→query特征 转换辅助(引擎调用时构造query)
STYLE_TO_QUERY_TAGS = {
    "悬疑风": ["悬疑", "犯罪", "黑暗", "精确", "去饱和", "成人"],
    "科幻风": ["科幻", "沉浸", "规模", "敬畏", "粒子", "几何"],
    "武侠风": ["武侠", "飘逸", "竹林", "克制", "意境", "国际"],
    "言情风": ["爱情", "错过", "霓虹", "浅景深", "独白", "女性"],
    "甜宠风": ["甜宠", "甜度递增", "竖屏", "女频", "反差萌", "暖色"],
    "赛博风": ["赛博", "霓虹", "雨夜", "紫色", "阶级", "成人"],
    "末世废土风": ["末世", "动作", "橙黄", "女性英雄", "居中对称", "成人"],
    "家庭温情风": ["家庭", "温情", "暖色", "日常", "食物", "银发"],
    "神话史诗风": ["史诗", "色彩段落", "群体", "对称", "极远渺小", "国际"],
    "田园风": ["田园", "黄金时刻", "留白", "手工", "自然", "治愈"],
}


def query_from_engine(style, genre_key, director_keys, audience, is_vertical, intensity, emotion_key):
    """从引擎当前配置构造query(供build_system_prompt调用)"""
    tags = set(STYLE_TO_QUERY_TAGS.get(style, []))
    # genre_key 补tags
    genre_tag_map = {
        "suspense_thriller": ["悬疑", "惊悚", "黑暗"],
        "action_combat": ["动作", "爆裂", "成人"],
        "war_epic": ["战争", "史诗", "成人", "历史"],
        "mythology_fantasy": ["奇幻", "神话", "冒险"],
        "xianxia_cultivation": ["仙侠", "修真", "飘逸"],
        "romance_sweet": ["爱情", "甜宠", "女性"],
        "comedy_humor": ["喜剧", "幽默"],
        "sci_fi": ["科幻", "未来"],
        "period_costume": ["古装", "宫廷", "权力"],
        "horror": ["恐怖", "心理", "成人"],
        "urban_modern": ["都市", "霓虹", "孤独"],
        "pastoral_idyllic": ["田园", "自然", "治愈"],
        "cyberpunk": ["赛博", "霓虹", "雨夜"],
        "wuxia_martial_arts": ["武侠", "飘逸", "竹林"],
        "psychological": ["心理", "镜子", "梦境"],
        "noir": ["黑色", "犯罪", "雨夜"],
        "revenge": ["复仇", "暴力美学", "成人"],
        "family_warmth": ["家庭", "温情", "日常"],
    }
    tags |= set(genre_tag_map.get(genre_key, []))
    # 受众
    aud_map = {
        "男频": "男性", "女频": "女性", "银发": "银发", "知识型": "成人",
    }
    q_audience = aud_map.get(audience, "")
    # type: 竖屏+短剧 → 短剧/短视频; 否则电影
    q_type = ""
    if is_vertical:
        q_type = "短剧"
    return {
        "type": q_type,
        "genres": list(genre_tag_map.get(genre_key, [])),
        "directors": director_keys or [],
        "audience": q_audience,
        "vertical": is_vertical,
        "intensity": intensity,
        "emotion": emotion_key,
        "tags": list(tags),
    }
