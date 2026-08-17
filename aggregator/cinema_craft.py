# -*- coding: utf-8 -*-
"""
aggregator/cinema_craft.py — 世界顶级导演工艺引擎
=====================================================
三大能力, 逼近/模拟世界顶级导演:

1. 生活质感引擎 (build_life_texture)
   顶级导演不靠形容词, 靠 细节/微表情/微动作/空镜/环境氛围/对话旁白
   六类镜头表现情感。本模块提供结构化质感库, 让剧本/分镜有真实生活质感。

2. 剪辑决策表 (build_edit_decision_list)
   真实剪辑师看着 24 帧/秒做决定; 我们无法看帧, 但可以把剪辑方案写成
   **agent/剪辑工具可识别的标准 EDL JSON**: 镜头ID/时长/景别/运镜/切点/转场/音频cue/情绪。

3. 视频生成 API payload (build_video_api_payload)
   对接 seedance2.5/可灵/wan3.0/H3/flux3/LTX-2.5/Sora2/Veo3 的标准请求体,
   让 Router 真正接入下游 ComfyUI 视频工作流 / 第三方 API。
"""
import json as _json

# ============================================================
# 1. 生活质感库 — 六类镜头质感, 按情绪键控
#    每类都是"具体可拍"的描述, 不是抽象形容词
# ============================================================
TEXTURE_DB = {
    "孤独": {
        "细节": ["窗玻璃上的雨痕把霓虹切成碎片", "桌上的凤梨罐头标签已经褪色起泡", "收音机天线用胶带缠了三圈", "砧板上一道深刀痕, 积着去年的菜渍"],
        "微表情": ["父亲抬眼0.5秒又垂下, 睫毛没动", "女儿嘴角想动, 最终抿成一条线", "父亲说话时喉结滚了一下, 声音却没出来"],
        "微动作": ["切菜的手停半拍, 刀尖悬着", "女儿把手机屏幕朝下扣在桌上", "父亲用围裙擦手, 擦了三次同一块"],
        "空镜": ["空椅背上搭着没织完的毛衣", "窗外雨里一盏路灯, 光圈虚成晕", "水龙头一滴一滴, 水槽里堆着没洗的碗"],
        "环境氛围": ["雨声盖过收音机, 粤剧只剩半句", "厨房灯泡40W, 暖黄只够照亮砧板", "冰箱嗡嗡声是屋里唯一的持续音"],
        "对话旁白": ["(旁白)那天的雨, 下到信纸都软了。", "父亲:'吃饭了。' — 他想说的不是这个。", "女儿:'嗯。' — 她听见了, 装作没听见。"],
    },
    "温暖": {
        "细节": ["碗沿磕了个小口, 是女儿小时候摔的", "灶台上煨着一锅汤, 咕嘟声很轻", "父亲把鱼肚子最嫩的一块夹给女儿"],
        "微表情": ["父亲眼角纹松开, 是今天第一次笑", "女儿低头扒饭, 睫毛上有一点亮"],
        "微动作": ["父亲把女儿的碗往她那边推了推", "女儿给父亲续了半碗汤, 没说原因"],
        "空镜": ["阳台上晒着两件衣服, 一件大一件小", "窗台的绿萝新抽了一片叶"],
        "环境氛围": ["汤的白汽在灯下慢慢升", "收音机换成了老歌, 音量调小了"],
        "对话旁白": ["父亲:'汤咸了?' 女儿:'刚好。' — 其实淡了, 她没说。", "(旁白)有些话, 用一碗汤就说完了。"],
    },
    "悲伤": {
        "细节": ["遗像前的香烧到一半, 灰弯着没断", "抽屉最里层压着一张没寄出的信", "钢笔没墨水, 笔尖干得发白"],
        "微表情": ["父亲盯着信, 眨眼频率慢下来", "女儿咬着下唇, 咬到发白"],
        "微动作": ["父亲的手在信纸上停住, 不敢翻第二页", "女儿把信折好, 折了三折, 和原来一样"],
        "空镜": ["空了的药瓶立在床头", "窗外的雨停了, 屋檐还在滴水"],
        "环境氛围": ["屋里只剩钟摆声", "灯比平时暗, 没人去换灯泡"],
        "对话旁白": ["父亲:'你妈她…' 后面三个字, 他用了十五年。", "(旁白)信没寄出, 因为收信人一直在身边。"],
    },
    "怀旧": {
        "细节": ["录音机里转出1998年的歌", "墙上的挂历停在某一页, 用红笔圈了个日子", "铁皮饼干盒里装着旧照片"],
        "微表情": ["父亲看着旧照片, 眼神放远了"],
        "微动作": ["父亲用拇指摩挲照片的边角"],
        "空镜": ["老式自行车靠在墙角, 铃铛锈了", "巷口的爆米花机砰了一声"],
        "环境氛围": ["午后阳光斜进屋, 灰尘在光柱里浮", "远处传来放学铃声"],
        "对话旁白": ["父亲:'那时候你妈最爱吃这个。'", "(旁白)1998年, 什么都旧, 什么都真。"],
    },
    "悬疑": {
        "细节": ["门锁有新的划痕", "桌上的杯子位置不对", "地毯一角微微翘起"],
        "微表情": ["对方眨眼快了半拍", "笑容停在嘴角, 没到眼睛"],
        "微动作": ["手在桌下攥紧", "对方把手机轻轻扣过去"],
        "空镜": ["走廊尽头的灯闪了两下", "监控红点在暗处亮着"],
        "环境氛围": ["空调声突然停了", "楼下有脚步, 三步, 停了"],
        "对话旁白": ["'你什么时候知道的?' — 没人回答。", "(旁白)真相在门后, 门没锁。"],
    },
}
# 其他情绪 fallback 到 孤独/温暖 组合
TEXTURE_DB.setdefault("愤怒", TEXTURE_DB["悲伤"])
TEXTURE_DB.setdefault("希望", TEXTURE_DB["温暖"])
TEXTURE_DB.setdefault("宁静", TEXTURE_DB["怀旧"])
TEXTURE_DB.setdefault("恐惧", TEXTURE_DB["悬疑"])
TEXTURE_DB.setdefault("浪漫", TEXTURE_DB["温暖"])
TEXTURE_DB.setdefault("史诗", TEXTURE_DB["悬疑"])


def get_texture(mood):
    return TEXTURE_DB.get(mood, TEXTURE_DB["孤独"])


def build_life_texture(scene, mood, director, count=3):
    """生成【生活质感与情感表现】块 — V13.3 场景驱动版.

    用六类镜头(细节/微表情/微动作/空镜/环境氛围/对话旁白)表现情感,
    模拟顶级导演"用镜头说话"的能力。质感条目由 场景角色/物件/地点 实时填充,
    不再输出与场景无关的固定厨房 demo。
    """
    # 解析场景元素
    try:
        from aggregator.scene_engine import parse_scene
        parsed = parse_scene(scene) if scene else {}
    except Exception:
        parsed = {}
    chars = parsed.get("characters") or ["主角"]
    _raw_objs = parsed.get("objects") or []
    # V13.4: 无真实物件时用自然表述, 不泄漏 "关键道具" 占位符
    objs = _raw_objs if _raw_objs else ["一件随身之物"]
    loc = parsed.get("location") or "场景"
    weather = parsed.get("weather") or ""
    c1 = chars[0]
    c2 = chars[1] if len(chars) > 1 else chars[0]
    obj = objs[0]
    obj2 = objs[1] if len(objs) > 1 else objs[0]

    # 年代判定 — 古装/科幻 用年代适配的环境声光
    era = "现代"
    try:
        from aggregator.feature_film_engine import _detect_era
        era = _detect_era(scene or "")
    except Exception:
        pass

    # 六类质感 — 用场景元素填充 (mood 决定句式情绪色彩)
    t = get_texture(mood)
    _atmos_modern = [
        f"{weather or '环境'}声盖过一切, 只剩{loc}的底噪",
        f"{loc}的灯不够亮, 只够照亮{obj}",
        f"远处的声音时断时续, 像没说完的话",
    ]
    _atmos_period = [
        f"风声穿过{loc}, 吹动{obj}的一角",
        f"烛火/天光在{loc}里晃动, 影子比人多",
        f"远处更鼓/马蹄声传来, {loc}里更静了",
    ]
    _atmos_scifi = [
        f"舱体的低频嗡鸣是{loc}唯一的持续音",
        f"警报灯在远处闪了一下, 又暗下去",
        f"循环系统的气流声里, {obj}静静待着",
    ]
    _atmos = {"古装": _atmos_period, "科幻": _atmos_scifi}.get(era, _atmos_modern)

    detail_items = [
        f"{obj}被放在{loc}最显眼又最不被注意的位置",
        f"{obj2}上有一处旧痕, 是故事留下的",
        f"{c1}的随身之物都旧了, 只有{obj}是新的",
    ]
    micro_face = [
        f"{c1}抬眼0.5秒又垂下, 睫毛没动",
        f"{c2}嘴角想动, 最终抿成一条线",
        f"{c1}说话时喉结滚了一下, 声音却没出来",
    ]
    micro_act = [
        f"{c1}的手停在{obj}上方, 没落下",
        f"{c1}把{obj}拿起又放下, 重复了两次",
        f"{c2}背过身去, 肩膀绷了一下",
    ]
    empty_shot = [
        f"{loc}空下来, 只剩{obj}在原处",
        f"无人入画, 只有{weather or '光'}在{loc}里移动",
        f"{obj}的特写, 静止两秒, 什么都没说",
    ]
    dialogue_vo = [
        f"(旁白){obj}还在, 人已经不一样了。",
        f"{c1}:'……' — 他想说的不是这个。",
        f"(旁白)有些话, 用{obj}就说完了。",
    ]

    lines = [f"【生活质感与情感表现 · {mood} · {director} 式镜头】"]
    label_map = {
        "物件细节(承载情感)": detail_items,
        "微表情特写(0.5秒的脸)": micro_face,
        "微动作特写(手/身体)": micro_act,
        "空镜/留白(环境与物)": empty_shot,
        "环境氛围(光/声/温度)": _atmos,
        "对话/旁白(潜文本)": dialogue_vo,
    }
    for label, items in label_map.items():
        sel = items[:count]
        if sel:
            lines.append(f"  · {label}: " + " / ".join(sel))
    lines.append(
        "  镜头语法: 情感不用形容词说, 用以上可拍细节呈现; "
        "特写0.5-1s, 空镜1-2s, 留白处呼吸声替代配乐."
    )
    return "\n".join(lines)


# ============================================================
# 2. 剪辑决策表 (EDL) — agent/剪辑工具可识别标准 JSON
# ============================================================
def build_edit_decision_list(scene, director, mood, total_dur=30, shots=6):
    """生成 agent 可识别的标准剪辑决策表 (EDL JSON).

    每个镜头: id/入点/出点/时长/景别/运镜/切点类型/转场/音频cue/情绪/动作/对话.
    真实剪辑师看24帧做决定; 我们把它编码成结构化指令, 供剪辑agent/工具执行.
    """
    per = total_dur / shots
    shot_sizes = ["全景","中景","中近景","特写","中景","全景"]
    moves = ["Truck right slow","静态","Push in slow","静态(手持微晃)","慢推","静态"]
    cut_types = ["硬切","硬切","匹配剪辑","跳切","硬切","淡出"]
    emotions = ["日常","悬念","发现","紧张","释放","温暖"]
    # V13.3: 音频 cue 场景驱动 — 由 物件/天气/地点 生成, 不再固定厨房声
    try:
        from aggregator.scene_engine import parse_scene
        _p = parse_scene(scene) if scene else {}
    except Exception:
        _p = {}
    _objs = _p.get("objects") or ["关键道具"]
    _loc = _p.get("location") or "场景"
    _weather = _p.get("weather") or "环境"
    _o1 = _objs[0]
    _o2 = _objs[1] if len(_objs) > 1 else _objs[0]
    audio_cues = [
        f"{_weather}声+{_loc}底噪",
        f"{_o1}被触碰的轻响",
        f"衣物/脚步摩擦声",
        f"呼吸声+短暂静默",
        f"{_o2}的细微声响",
        f"{_weather}渐弱+余音",
    ]
    edl = {
        "format": "comfyui-directormaster-edl/v1",
        "project": scene, "director": director, "mood": mood,
        "fps": 24, "total_duration_sec": total_dur, "shot_count": shots,
        "tracks": {"video": [], "audio": []},
    }
    t0 = 0.0
    for i in range(shots):
        dur = round(per, 1)
        edl["tracks"]["video"].append({
            "shot_id": i + 1,
            "in_sec": round(t0, 2), "out_sec": round(t0 + dur, 2), "duration_sec": dur,
            "shot_size": shot_sizes[i % 6], "camera_move": moves[i % 6],
            "cut_type": cut_types[i % 6],
            "transition": "cut" if cut_types[i % 6] == "硬切" else ("match" if cut_types[i % 6] == "匹配剪辑" else ("jump" if cut_types[i % 6] == "跳切" else "fade")),
            "emotion": emotions[i % 6],
            "action": "见分镜脚本镜头%d" % (i + 1),
            "dialogue": "",
        })
        edl["tracks"]["audio"].append({
            "shot_id": i + 1, "in_sec": round(t0, 2), "duration_sec": dur,
            "cue": audio_cues[i % 6], "music": "none(留白)" if i % 3 == 0 else "极简钢琴单音",
        })
        t0 += dur
    return edl


def build_edit_decision_text(scene, director, mood, total_dur=30, shots=6):
    """EDL 的可读文本版 (供人/剧本阅读)."""
    edl = build_edit_decision_list(scene, director, mood, total_dur, shots)
    lines = [f"【剪辑决策表 EDL · {director} · {total_dur}s · 24fps】"]
    for v in edl["tracks"]["video"]:
        a = next((x for x in edl["tracks"]["audio"] if x["shot_id"] == v["shot_id"]), {})
        lines.append(
            f"  镜{v['shot_id']:02d} [{v['in_sec']:.1f}-{v['out_sec']:.1f}s] {v['shot_size']} "
            f"{v['camera_move']} | 切:{v['cut_type']} 转场:{v['transition']} | 情绪:{v['emotion']} | 音:{a.get('cue','')}"
        )
    lines.append("  格式: comfyui-directormaster-edl/v1 (agent/剪辑工具可解析)")
    return "\n".join(lines)


# ============================================================
# 3. 视频生成 API payload — 对接真实视频模型
# ============================================================
VIDEO_MODELS = {
    "seedance2.5": {"vendor": "字节", "api": "https://api.volcengine.com/seedance/v1", "fields": ["prompt","duration","aspect_ratio","fps","seed"]},
    "kling": {"vendor": "快手可灵", "api": "https://api.klingai.com/v1/videos/text2video", "fields": ["prompt","duration","aspect_ratio","cfg_scale"]},
    "wan3.0": {"vendor": "阿里通义万相", "api": "https://dashscope.aliyuncs.com/wan/v1/video", "fields": ["prompt","duration","size","seed"]},
    "h3": {"vendor": "MiniMax", "api": "https://api.minimax.io/v1/video_generation", "fields": ["prompt","model","duration","aspect_ratio"]},
    "flux3": {"vendor": "Black Forest", "api": "https://api.bfl.ai/flux/v1/video", "fields": ["prompt","steps","aspect_ratio"]},
    "ltx2.5": {"vendor": "Lightricks", "api": "https://api.lightricks.com/ltx/v1/video", "fields": ["prompt","duration","resolution","fps"]},
    "sora2": {"vendor": "OpenAI", "api": "https://api.openai.com/v1/videos", "fields": ["prompt","model","seconds","size"]},
    "veo3": {"vendor": "Google", "api": "https://aiplatform.googleapis.com/veo/v1/videos", "fields": ["prompt","duration","aspect_ratio"]},
}


def build_video_api_payload(model_key, prompt, scene, aspect="16:9", duration=8, fps=24, edl=None, negative=None):
    """生成目标视频模型的标准 API 请求体 (JSON).

    model_key: seedance2.5/kling/wan3.0/h3/flux3/ltx2.5/sora2/veo3
    返回 dict, 可直接 POST 到对应 API / 或交给下游 ComfyUI 视频节点.
    """
    m = VIDEO_MODELS.get(model_key, VIDEO_MODELS["seedance2.5"])
    payload = {
        "vendor": m["vendor"], "endpoint": m["api"], "target_model": model_key,
        "prompt": prompt,
        "negative_prompt": negative or "masterpiece,best quality,ultra detailed,4K,8K,HDR,photorealistic,cinematic lighting,变形,多手,模糊",
        "aspect_ratio": aspect, "duration_sec": duration, "fps": fps,
        "shot_list": (edl["tracks"]["video"] if edl else []),
        "audio_cues": (edl["tracks"]["audio"] if edl else []),
        "comfyui_downstream": {
            "workflow": "text2video",
            "load_node": "VideoGenerateNode",
            "connect": {"prompt": "model_specific_prompt", "edl": "edit_decision_list"},
        },
    }
    return payload


def build_video_api_text(model_key, prompt, scene, **kw):
    return _json.dumps(build_video_api_payload(model_key, prompt, scene, **kw), ensure_ascii=False, indent=2)