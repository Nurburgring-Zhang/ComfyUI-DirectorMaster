# -*- coding: utf-8 -*-
"""
aggregator/scene_entity.py — V16.5 场景实体引擎 (参考真实生产级 AI 视频提示词标准库,
即"真实素材设计"范式: 角色/地点/设备美学/音频/时间轴/素材身份 七件套)
================================================================
职责 (全部确定性, md5 种子驱动, 零依赖):
  1. extract_entities(scene_text) — 从用户场景句提取 角色/道具/地点/天气/时间/色彩/动作
     (后缀词典启发式, 无 NLP 依赖; 提取结果驱动分镜画面内容, 消灭罐头句)
  2. device_package(风格关键词) — 设备美学缺陷包: 摄影机+镜头组合+画面缺陷+素材身份
     (IMAX+Panavision / 索尼威尼斯+K-35 / ARRICAM+Cooke / 手机竖屏 / DV / VHS / Super8 / 监控)
  3. focal_for_size(景别) — 焦段-景别 cinematography 匹配 (消灭"中近景12mm"式失配)
  4. sound_cues(...) — 显式音效枚举 (从天气/地点/实体派生, 兑现"同期声+显式枚举")
  5. composition_for(...) — 构图库 (对称居中/三分法/过肩/负空间/对角线/框架...)
  6. rewrite_focus(...) — 画面内容重写: 用户实体 × 阶段动作线 × 构图, 替代罐头焦点
  7. five_segment_shell(...) — 附件五段结构外壳: 核心主题/人物与基础设定/氛围与画质/
     镜头控制/画面内容 + 结尾克制 + 模型建议 + 自检清单
  8. second_by_second(...) — 写法A: ≤20s 单场景按秒切时间轴 ([0-3s·凝视] 式)
"""
import hashlib as _hl
import re as _re

# ----------------------------------------------------------------
# 1. 实体提取
# ----------------------------------------------------------------
_CHAR_SUFFIX = ("战士", "机器人", "男人", "女人", "女孩", "男孩", "少女", "少年", "老人",
                "医生", "护士", "警察", "士兵", "将军", "骑士", "剑客", "侠客", "修士",
                "仙人", "道士", "法师", "学徒", "学生", "老师", "厨师", "司机", "老板",
                "职员", "侦探", "猎人", "海盗", "宇航员", "科学家", "工程师", "舞者",
                "歌手", "乐手", "主播", "店员", "服务员", "母亲", "父亲", "爷爷", "奶奶",
                "孩子", "小孩", "婴儿", "猫", "狗", "鸟", "马", "龙", "虎", "狼", "妖",
                "魔", "鬼", "怪", "兽", "灵", "主角", "女主", "男主", "对手", "敌人", "队友",
                "骆驼", "牛", "羊", "鹰", "猿", "鹤", "鲨", "鲸", "海豚", "企鹅", "松鼠",
                "匠", "师傅", "大师", "刺客", "特工", "飞行员", "船长", "水手",
                "守夜人", "队长", "恋人", "商贩", "艺人", "孩童", "渔民", "牧民",
                "修女", "修士", "夫人", "官爷", "捕快", "乐手", "路人", "旅客", "乘客")
_PROP_SUFFIX = ("护盾", "刀", "剑", "枪", "弓", "盾", "锤", "斧", "杖", "扇", "伞", "灯",
                "信", "表", "戒指", "项链", "箱子", "盒子", "手机", "电脑", "键盘", "相机",
                "车", "摩托", "船", "飞船", "飞机", "门", "窗", "镜", "锅", "碗", "杯",
                "酒", "面", "茶", "药", "书", "画", "琴", "鼓", "旗", "甲", "盔", "靴",
                "斗篷", "面具", "徽章", "宝石", "水晶", "芯片", "引擎", "炮", "雷达",
                "罐头", "凤梨", "辣椒酱", "面包", "蛋糕", "花", "树", "石头", "骨", "符",
                "丹", "炉", "阵", "卷轴", "地图", "钥匙", "锁", "绳", "链")
_WEATHER_KW = ("暴雨", "大雨", "小雨", "雷暴", "雷雨", "风雪", "暴雪", "大雪", "小雪",
               "大雾", "浓雾", "薄雾", "沙尘暴", "台风", "冰雹", "晴天", "阴天", "黄昏",
               "黎明", "日出", "日落", "夜晚", "深夜", "正午", "清晨", "傍晚", "雷暴交织")
_TIME_KW = ("清晨", "早晨", "上午", "正午", "午后", "下午", "傍晚", "黄昏", "夜晚", "深夜",
            "凌晨", "黎明", "日落", "日出", "古代", "民国", "未来", "末世", "1998", "80年代",
            "90年代", "2020s")
_COLOR_KW = (("红色", "红"), ("绿色", "绿"), ("蓝色", "蓝"), ("青色", "青"), ("金色", "金"),
             ("银色", "银"), ("白色", "白"), ("黑色", "黑"), ("紫色", "紫"), ("粉色", "粉"),
             ("橙色", "橙"), ("灰色", "灰"), ("霓虹", "霓虹"), ("荧光", "荧光"), ("暖色", "暖"),
             ("冷色", "冷"), ("青橙", "青橙"), ("青绿", "青绿"), ("暗红", "暗红"), ("翠绿", "翠绿"))
_VERB_KW = ("开启", "关闭", "举起", "放下", "奔跑", "追逐", "逃跑", "对峙", "决斗", "战斗",
            "拥抱", "告别", "哭泣", "大笑", "凝视", "回眸", "转身", "跪坐", "站立", "行走",
            "骑车", "驾驶", "烹饪", "揉面", "滑雪", "舞蹈", "唱歌", "射击", "挥砍", "施法",
            "变身", "飞行", "坠落", "攀爬", "潜行", "搜索", "抢救", "守护", "等待", "投喂",
            "陪伴", "遇到", "遇见", "相遇", "重逢", "对决", "狙击", "护送", "寻找", "讲述",
            "发现", "看见", "望见", "瞥见", "修补", "演示", "加练", "载客", "炼丹", "召唤",
            "交换", "埋下", "翻开", "转动", "独舞", "斗嘴", "搜索", "格斗", "对练", "冲锋")

# 前缀虚词/量词 (核心名词清洗用)
_STRIP_LEAD = ("一只", "一个", "一位", "一匹", "一条", "一头", "一名", "一朵", "一件",
               "一群", "一只只", "的", "把", "被", "从", "在", "向", "往", "至", "到",
               "与", "和", "及", "同", "跟", "只", "块", "枚", "颗", "张", "把", "座",
               "间", "台", "辆", "艘", "柄", "封", "滴", "两个", "两台", "三位", "三名",
               "几名", "一群群", "最后", "其中")
_CHAR_CONNECTORS = ("与", "和", "及", "VS", "vs")


def _core_noun(cand):
    """清洗候选词: 按动词切段取末段, 按连接词切段取末段, 循环剥离前缀虚词/量词,
    取'的'后段与'中的'后段 (角与女主角→女主角; 陪伴一个孩子→孩子)。"""
    parts = _re.split("(?:" + "|".join(_VERB_KW) + ")", cand)
    core = parts[-1] if parts else cand
    core = _re.split("(?:与|和|及|VS|vs)", core)[-1]
    changed = True
    while changed and core:
        changed = False
        for p in _STRIP_LEAD:
            if core.startswith(p) and len(core) > len(p):
                core = core[len(p):]
                changed = True
    if "中的" in core and core.index("中的") < len(core) - 3:
        core = core.rsplit("中的", 1)[-1]
    if "的" in core and core.index("的") < len(core) - 1:
        core = core.split("的")[-1]
    return core

_LOCATION_SUFFIX = ("码头", "厨房", "客厅", "卧室", "书房", "庭院", "天台", "屋顶", "阳台",
                    "街道", "小巷", "广场", "车站", "机场", "港口", "沙滩", "海边", "山顶",
                    "森林", "沙漠", "雪原", "草原", "洞穴", "废墟", "教堂", "寺庙", "宫殿",
                    "城堡", "校园", "教室", "医院", "病房", "实验室", "工厂", "仓库", "酒吧",
                    "餐厅", "咖啡馆", "便利店", "超市", "地铁", "隧道", "桥梁", "电梯",
                    "走廊", "机舱", "驾驶舱", "控制室", "餐厅", "擂台", "剑台", "山谷",
                    "云海", "虚空", "遗迹", "病房", "书房", "澡堂", "澡堂", "理发店",
                "直播间", "演播厅", "片场", "摄影棚", " cereza", "胡同", "老街", "村口", "病房")


def extract_entities(scene_text):
    """从用户场景句提取实体 (启发式词典, 全确定性). 返回 dict:
    characters / props / location / weather / time / colors / verbs / raw
    提取不到的键为空列表/空串 — 上层据此决定是否回退罐头池。"""
    text = str(scene_text or "").strip()
    out = {"characters": [], "props": [], "location": "", "weather": "",
           "time": "", "colors": [], "verbs": [], "raw": text}
    if not text:
        return out
    # 去重保序
    def _uniq(seq):
        seen, res = set(), []
        for x in seq:
            if x and x not in seen:
                seen.add(x)
                res.append(x)
        return res
    # 角色: "XX战士" (贪婪前缀0-6字 + 后缀 — "男主角"整体优于"男主"), 过滤含动词片段
    _char_re = _re.compile("([\u4e00-\u9fff]{0,6}(?:" + "|".join(_CHAR_SUFFIX) + "))")
    for m in _char_re.finditer(text):
        core = _core_noun(m.group(1))
        if not core or any(v in core for v in _VERB_KW):
            continue
        # "剑圣与刀魔" → 按 与/和/及/VS 拆成多角色
        subs = [x for x in _re.split("(?:与|和|及|VS|vs)", core) if x]
        for cand in (subs if len(subs) > 1 else [core]):
            if cand and cand not in out["characters"] and not any(v in cand for v in _VERB_KW):
                out["characters"].append(cand)
    # 角色去重保最长 (狗 ⊂ 小奶狗 → 留小奶狗)
    _chars_sorted = sorted(out["characters"], key=len, reverse=True)
    _kept = []
    for c in _chars_sorted:
        if not any(c in k for k in _kept):
            _kept.append(c)
    out["characters"] = list(reversed(_kept))
    # 道具: 同理
    _prop_re = _re.compile("([\u4e00-\u9fff]{1,4}?(?:" + "|".join(_PROP_SUFFIX) + "))")
    for m in _prop_re.finditer(text):
        cand = _core_noun(m.group(1))
        # 去掉误拼进前缀的动词 (开启能量护盾 → 能量护盾)
        for v in _VERB_KW:
            if cand.startswith(v) and len(cand) > len(v):
                cand = cand[len(v):]
                break
        if any(v in cand for v in _VERB_KW):
            continue
        # 道具是角色子串或包含完整角色名 (剑圣与刀 ⊃ 剑圣) 时跳过
        if any(cand in ch or ch in cand for ch in out["characters"]):
            continue
        if cand and cand not in out["characters"] and cand not in out["props"]:
            out["props"].append(cand)
    # 地点/天气/时间/色彩/动词
    for loc in _LOCATION_SUFFIX:
        if loc in text:
            out["location"] = loc
            break
    for w in _WEATHER_KW:
        if w in text:
            out["weather"] = w
            break
    for t in _TIME_KW:
        if t in text:
            out["time"] = t
            break
    for full, short in _COLOR_KW:
        if full in text:
            out["colors"].append(short)
    for v in _VERB_KW:
        if v in text:
            out["verbs"].append(v)
    for k in ("characters", "props", "colors", "verbs"):
        out[k] = _uniq(out[k])
    return out


def has_entities(ent):
    return bool(ent and (ent.get("characters") or ent.get("props") or
                         ent.get("location") or ent.get("verbs")))


# ----------------------------------------------------------------
# 2. 设备美学缺陷包 (素材身份: 谁拍/用什么拍/什么缺陷)
# ----------------------------------------------------------------
_DEVICE_PACKS = [
    # (匹配关键词列表, 包名, 摄影机, 镜头, 画质缺陷描述, 素材身份)
    (["科幻", "机甲", "硬核", "史诗", "灾难", "战争", "太空"], "IMAX 实拍包",
     "IMAX 胶片摄影机", "Panavision C 系列镜头 (焦段按景别, 光圈 f4)",
     "变形宽银幕质感, 模拟动态模糊, 暗部信息压缩保留细节, 边缘轻微柔焦 + 适度胶片颗粒",
     "一段 IMAX 实拍电影素材"),
    (["赛博", "暗调", "废土", "工业", "雨夜", "黑色电影", "犯罪"], "暗调数字包",
     "索尼威尼斯电影机", "佳能 K-35 系列镜头",
     "暗调低照明高对比, 高亮度霓虹与深黑并置, 体积雾漫射微弱冷光, 轻微畸变边缘",
     "一段深夜城市实拍素材"),
    (["温暖", "情感", "生活", "家庭", "治愈", "文艺", "爱情", "亲情"], "暖色胶片包",
     "ARRICAM 胶片摄影机", "Cooke S4 定焦镜头",
     "Kodak Vision3 250D 胶片色, 柔和高光过渡, 自然肤色还原, 轻微颗粒, 调色全片锁一档暖调",
     "一段家庭胶片录像"),
    (["港风", "复古", "武侠", "江湖", "邵氏", "功夫"], "复古港片包",
     "80 年代变形宽银幕摄影机", "老式变形宽银幕镜头",
     "柯达 35mm 复古胶片, 跳过漂白工艺, 高光柔焦溢出, 颗粒感明显, 色彩浓郁高反差",
     "一段 80 年代港片素材"),
    (["vlog", "手机", "竖屏", "自拍", "直播", "日常"], "手机竖屏包",
     "智能手机主摄", "等效 24mm (竖屏 9:16)",
     "轻微过度锐化 + HDR 处理感, 电子防抖残余浮动, 走路时上下浮动, 光线明暗切换时曝光短暂波动, 偶有手指擦过镜头边缘",
     "一段路人手机随手拍的真实素材"),
    (["纪录片", "伪纪录", "新闻", "科教"], "纪录观察包",
     "手持纪录片摄影机", "长焦变距镜头",
     "自然光优先, 跟随时轻微晃动, 自动对焦偶尔搜索, 无补光无布光, 现场声优先",
     "一段纪录片观察素材"),
    (["恐怖", "惊悚", "灵异", "悬疑"], "压抑写实包",
     "ALEXA Mini 手持", "Zeiss Master Prime 定焦",
     "低照度噪点可见, 阴影信息深压缩, 冷青主调, 手持呼吸感浮动, 偶尔失焦再拉回",
     "一段实拍恐怖片素材"),
    (["dv", "怀旧", "家用", "千禧"], "DV 怀旧包",
     "2000 年代消费级 DV 摄像机", "机内变焦镜头",
     "中等数字压缩伪影, 褪色色彩, 柔和对比, 轻微传感器噪点, 强烈手持抖动, 频繁自动对焦搜索",
     "一段家庭旧 DV 录像"),
    (["动画", "动漫", "水墨", "绘本", "二次元"], "风格化包",
     "风格化渲染 (非实拍)", "虚拟镜头",
     "统一美术风格, 线条/笔触跨镜头一致, 光影按美术设定, 不混入实拍质感",
     "一段风格化动画片段"),
]
_DEVICE_DEFAULT = ("通用电影包", "ALEXA 35 数字电影机", "Master Prime 定焦镜头组",
                   "电影级动态范围, 自然肤色, 暗部保留细节, 轻微颗粒, 无过度锐化",
                   "一段专业电影机实拍素材")


def device_package(scene_text="", visual_style="", genre_hint=""):
    """按场景/视觉调性/类型选择设备美学包. 返回 dict(name/camera/lens/defects/identity)."""
    text = " ".join(str(x or "") for x in (scene_text, visual_style, genre_hint))
    for kws, name, cam, lens, defects, identity in _DEVICE_PACKS:
        if any(k in text for k in kws):
            return {"name": name, "camera": cam, "lens": lens,
                    "defects": defects, "identity": identity}
    name, cam, lens, defects, identity = _DEVICE_DEFAULT
    return {"name": name, "camera": cam, "lens": lens, "defects": defects, "identity": identity}


# ----------------------------------------------------------------
# 3. 焦段-景别匹配 (cinematography 常识: 特写长焦/全景广角)
# ----------------------------------------------------------------
_FOCAL_BY_SIZE = {
    "大远景": ["14mm", "16mm", "18mm"],
    "远景": ["20mm", "24mm", "28mm"],
    "全景": ["24mm", "28mm", "35mm"],
    "中全景": ["28mm", "35mm"],
    "中景": ["35mm", "40mm", "50mm"],
    "中近景": ["50mm", "65mm", "70mm"],
    "近景": ["70mm", "85mm", "100mm"],
    "特写": ["85mm", "100mm", "135mm"],
    "大特写": ["100mm", "135mm", "150mm 微距"],
}
_FOCAL_DEFAULT = ["35mm", "50mm", "85mm"]


def focal_for_size(size, shot_n=1):
    """按景别返回电影学合理的焦段 (确定性取值). 未知景别回退通用组。"""
    pool = _FOCAL_BY_SIZE.get(str(size or ""), _FOCAL_DEFAULT)
    idx = int(_hl.md5(f"{shot_n}|focal".encode()).hexdigest(), 16) % len(pool)
    return pool[idx]


# ----------------------------------------------------------------
# 4. 显式音效枚举 (同期声, 从场景派生)
# ----------------------------------------------------------------
_WEATHER_SFX = {
    "暴雨": "暴雨砸击声、雨点砸在金属表面声", "大雨": "密集雨点声、排水沟流水声",
    "小雨": "细雨沙沙声、屋檐滴水声", "雷暴": "闷雷滚过声、雷鸣炸响",
    "雷雨": "雨声与闷雷交织", "风雪": "风啸声、雪粒扑打声", "暴雪": "狂风卷雪声",
    "大雪": "落雪的闷响、踩雪咯吱声", "小雪": "落雪细响", "大雾": "雾中闷响的低环境声",
    "浓雾": "雾笛声、模糊的低频环境声", "沙尘暴": "风沙呼啸、砂砾扑打声",
    "台风": "狂风呼啸、物体碰撞声", "晴天": "鸟鸣与远处的城市底噪",
    "夜晚": "夜虫鸣、远处车流低噪", "深夜": "极静的环境底噪、偶尔的远处声响",
}
_LOCATION_SFX = {
    "码头": "货轮低鸣、缆绳吱呀、集装箱金属回响", "厨房": "切菜声、油锅滋滋声、抽油烟机嗡鸣",
    "庭院": "风穿树叶声、虫鸣", "街道": "车流声、行人脚步、远处喇叭",
    "森林": "树叶沙沙、鸟叫、枝干吱呀", "沙漠": "风卷沙粒声、干燥的空气声",
    "雪原": "风声、雪层压碎声", "废墟": "风穿残壁的呜咽、碎石滚落",
    "教堂": "空旷回声、风琴余韵", "医院": "仪器滴滴声、 distant 脚步回声",
    "实验室": "仪器低频嗡鸣、气流声", "工厂": "机械运转声、金属敲击、蒸汽泄压",
    "机舱": "引擎低频轰鸣、气流声", "地铁": "轨道轰鸣、进站风压声",
    "酒吧": "杯盏碰撞、人声嘈杂的低鸣", "便利店": "门铃叮咚、冰柜压缩机嗡鸣",
    "直播间": "键盘敲击、消息提示音", "擂台": "拳击垫闷响、观众呼声",
}
_PROP_SFX = {
    "护盾": "能量低频嗡鸣", "刀": "金属出鞘声", "剑": "剑刃破空声", "枪": "机械上膛声",
    "机甲": "液压传动声、金属关节摩擦声", "机器人": "伺服电机声、电子提示音",
    "飞船": "引擎脉冲声", "车": "引擎轰鸣", "锅": "锅铲碰撞声", "琴": "琴弦震颤声",
    "水晶": "晶体共振的清鸣", "引擎": "点火轰鸣、怠速颤动",
}


def sound_cues(ent, weather="", location=""):
    """显式音效枚举 (兑现'同期声+显式枚举'标准). 返回枚举串。"""
    parts = []
    w = weather or (ent or {}).get("weather", "")
    loc = location or (ent or {}).get("location", "")
    if w:
        for k, v in _WEATHER_SFX.items():
            if k in w:
                parts.append(v)
                break
    if loc:
        for k, v in _LOCATION_SFX.items():
            if k == loc:
                parts.append(v)
                break
    for prop in (ent or {}).get("props", [])[:2]:
        for k, v in _PROP_SFX.items():
            if k in prop:
                parts.append(v)
                break
    for ch in (ent or {}).get("characters", [])[:1]:
        parts.append(f"{ch}的呼吸与脚步声")
    if not parts:
        parts = ["现场环境底噪、人物脚步与呼吸声"]
    return "、".join(parts[:4])


# ----------------------------------------------------------------
# 5. 构图库
# ----------------------------------------------------------------
_COMPOSITIONS = ["对称居中构图", "三分法构图", "前景框架构图", "过肩构图",
                 "负空间留白构图", "对角线构图", "低角度仰拍构图", "高角度俯拍构图",
                 "中心透视构图", "引导线构图"]


def composition_for(shot_n, size="", move="", complex_struct=None):
    """按镜号确定性选构图; 特写优先居中/三分, 大远景优先对称/引导线。"""
    size = str(size or "")
    if "特写" in size or "近景" in size:
        pool = ["对称居中构图", "三分法构图", "负空间留白构图", "前景框架构图"]
    elif "远景" in size or "全景" in size:
        pool = ["对称居中构图", "引导线构图", "中心透视构图", "对角线构图"]
    else:
        pool = _COMPOSITIONS
    idx = int(_hl.md5(f"{shot_n}|{size}|comp".encode()).hexdigest(), 16) % len(pool)
    return pool[idx]


# ----------------------------------------------------------------
# 6. 画面内容重写 (消灭罐头句: 用户实体 × 阶段动作线)
# ----------------------------------------------------------------
_STAGE_ACTION = {
    "序章": ("环境先于人出现", "在画面边缘安静存在"),
    "建立": ("交代空间与人物入场", "动作尚未展开, 只有姿态"),
    "铺垫": ("试探与接近", "互动的余波在画面里"),
    "中点": ("局势翻转的瞬间", "攻守易势"),
    "转折": ("冲突浮出水面", "对抗的临界点"),
    "高潮": ("全力对抗与爆发", "动作达到峰值"),
    "收束": ("余韵与离开", "能量缓慢消散"),
    "结局": ("落幕与留白", "一切归于安静"),
}


_SIZE_SHOT_DETAIL = {
    "特写": ["手部细节先行: 指节因用力而发白", "眼睛只占画面一角, 余光是虚化的环境",
           "皮肤纹理与汗珠清晰可见", "嘴唇轻抿, 呼吸在画面里可见",
           "睫毛投下的阴影随呼吸晃动", "袖口磨出的毛边占据下沿",
           "一滴汗沿鬓角滑到下颌", "瞳孔里映着远处的光源"],
    "近景": ["肩线紧绷, 领口随呼吸起伏", "视线投往画外一点, 不看镜头",
           "手指无意识地摩挲衣角", "喉结滚动一次, 没说出话",
           "衣领歪着, 本人没有察觉", "鬓角的湿发贴下来",
           "下巴微收, 下颌线绷成一条线", "嘴角动了一下, 又压平"],
    "中近景": ["半身入画, 手部动作先于表情", "身体重心在前脚掌, 随时可动",
             "肘部撑在台面, 撑住整个人的重量", "指尖在桌沿敲了半拍又停",
             "衣摆被风掀起一角", "手插进口袋又抽出来"],
    "中景": ["腰部以上入画, 动作与环境各占一半", "人物与{prop}同框, 距离即关系",
           "转身动作停在三分之二处", "双臂张开又收回, 幅度只有一半",
           "坐下时带倒了什么, 没有回头", "肩膀撞上门框, 没有停"],
    "全景": ["全身入画, 人物与{location}的空间关系一目了然", "人物居中偏侧, 留出动作空间",
           "人物在画面下三分之一, 上方留给{location}", "来回踱步的路线在画面里成型",
           "与{prop}隔着半步的距离站定", "人物的位置换了三次, 都不自在"],
    "远景": ["人物只是环境中的一个点, {location}的尺度压过人", "剪影层次分明, 细节让给气氛",
           "人物被{location}的线条切割成小块", "光把人物钉在原地, 周围都在动",
           "人物走向画面深处, 步幅越走越小", "人群从人物两侧流过, 没人停留"],
    "大远景": ["人物小如尘点, {location}{weather}的全貌铺开", "天地为幕, 人物仅是参照物",
             "广角把{location}推到极远, 人物只剩轮廓", "气象压过人物, 云层在头顶翻涌",
             "地平线压得很低, 人物悬在画面上缘"],
}
_ATMO_TAILS = ["空气里浮着薄尘", "远处传来隐约的低频声响", "水渍在台面留下深色痕迹",
               "墙皮剥落一小块, 边缘卷起", "光从画面边缘漏进来一线", "影子比人先到一步",
               "温度仿佛比上一镜低了两度", "尘埃在光柱里缓慢悬浮",
               "角落里堆着没人动的杂物", "一张旧告示被风掀起半边",
               "窗外的天色比室内亮一档", "地面有一道拖拽过的浅痕",
               "铁器表面凝着一层薄薄的水汽", "风把某个角落的纸片吹得打转",
               "灯管在远处闪了一下, 没人在意", "空气里有若有若无的焦味"]


def rewrite_focus(ent, shot, phase="", size="", move="", tension=5, seed_str=""):
    """用用户实体重写一镜的画面内容 (附件标准: 具体动作传达情绪, 拒绝空洞词)。

    ent: extract_entities 结果; shot: dict(含 n); 返回新 focus 串。
    实体不足时返回 "" (上层保留原 focus, 诚实回退罐头池)。
    每镜按镜号+景别差异化 (消灭 8 镜同句式)。"""
    if not has_entities(ent):
        return ""
    chars = ent["characters"]
    props = ent["props"]
    loc = ent.get("location") or ""
    weather = ent.get("weather") or ""
    colors = ent.get("colors") or []
    verbs = ent.get("verbs") or []
    n = int(shot.get("n", 1)) if isinstance(shot, dict) else 1
    stage = str(phase or "")
    action_line = ""
    for k, (a, b) in _STAGE_ACTION.items():
        if k in stage:
            action_line = a if n % 2 == 1 else b
            break
    if not action_line:
        action_line = "动作在克制中推进"
    subject = chars[0] if chars else "主角"
    other = chars[1] if len(chars) > 1 else ""
    prop = props[0] if props else ""
    verb = verbs[0] if verbs else ""
    # 主体动作: 阶段推进感 (动词 6 变体, md5 驱动); 无动词但有道具时
    # 角色仍是主语 (道具只作宾语/环境) — 保证主角色每镜命中
    _seed_str = str(seed_str or "")
    _vseed = int(_hl.md5(f"{_seed_str}|{n}|{stage}|{size}|vform".encode()).hexdigest(), 16)
    if verb:
        verb_forms = [f"{verb}", f"{verb}的瞬间", f"仍在{verb}", f"{verb}之后",
                      f"{verb}到一半", f"反复{verb}", f"正要{verb}", f"{verb}着"]
        v = verb_forms[_vseed % 8]
        if other:
            # 奇偶镜交替: 角色互为主客体; 偶数镜带道具作中介 (保证道具每2镜至少1次命中)
            if prop and n % 2 == 0:
                core = f"{other}注视着{subject}{v}{prop}"
            else:
                core = f"{subject}{v}{other}" if n % 2 == 1 else f"{other}注视着{subject}{v}"
        elif prop:
            core = f"{subject}{v}{prop}"
        else:
            core = f"{subject}{v}"
    else:
        if other:
            core = (f"{subject}与{other}对峙" if n % 2 == 1 else f"{other}注视着{subject}")
        elif prop:
            core = f"{subject}接近{prop}" if n % 3 == 0 else f"{prop}旁, {subject}保持姿态"
        else:
            core = f"{subject}在{loc or '画面中'}{action_line}"
            action_line = ""
    # 景别化镜头细节 + 氛围尾注 (每槽独立 md5 选择 — 恢复长片指纹多样性)
    size_key = str(size or "")
    detail_pool = None
    for k, pool in _SIZE_SHOT_DETAIL.items():
        if k in size_key:
            detail_pool = pool
            break
    detail = ""
    if detail_pool:
        detail = detail_pool[_vseed % len(detail_pool)]
        detail = detail.replace("{prop}", prop or "关键物件").replace("{location}", loc or "现场").replace("{weather}", weather or "")
    atmo = _ATMO_TAILS[int(_hl.md5(f"{n}|{stage}|{size}|atmo".encode()).hexdigest(), 16) % len(_ATMO_TAILS)]
    parts = []
    head = (f"{weather}中的" if weather and weather not in ("晴天",) else "")
    parts.append(f"{head}{loc or '现场'}。")
    parts.append(f"{core}，{action_line}。" if action_line else f"{core}。")
    if detail:
        parts.append(f"{detail}。")
    if move:
        parts.append(f"镜头以{move}、{size or ''}呈现。".replace("、", "") if not size else f"镜头以{move}，{size}呈现。")
    if colors:
        parts.append(f"画面主色调: {'/'.join(colors[:2])}。")
    parts.append(f"{atmo}。")
    focus = _re.sub(r"\s+", " ", "".join(parts)).strip()
    return focus


def first_frame_desc(ent, size="", angle="", focal="", light=""):
    """真实首帧描述 (修复'首帧描述=阶段名'的垃圾输出): 静态画面可拍描述。"""
    chars = (ent or {}).get("characters") or []
    props = (ent or {}).get("props") or []
    loc = (ent or {}).get("location") or "现场"
    weather = (ent or {}).get("weather") or ""
    subject = f"{chars[0]}" if chars else (props[0] if props else "主体")
    frag = [f"{size or '中景'}, {angle or '平视'}, {focal or '35mm'} 焦段",
            f"{subject}静止于{loc}" + (f" ({weather})" if weather else ""),
            f"光影: {light or '自然光'}"]
    return "; ".join(frag) + "。无运动, 无文字, 无水印。"


# ----------------------------------------------------------------
# 7. 五段结构外壳 (核心主题/人物与基础设定/氛围与画质/镜头控制/画面内容)
# ----------------------------------------------------------------
def five_segment_shell(ent, dev, core_pack=None, mode="", director="", mood="",
                       minutes=None, sound_cues_str="", model_suggest=""):
    """生成附件标准五段结构头块 (字符串), 供 Cinematic main 输出前置。"""
    core_pack = core_pack or {}
    chars = (ent or {}).get("characters") or []
    props = (ent or {}).get("props") or []
    scene_desc = (ent or {}).get("raw", "")
    loc = (ent or {}).get("location", "")
    weather = (ent or {}).get("weather", "")
    time_str = (ent or {}).get("time", "")
    theme = str(core_pack.get("_主题词", "") or mood)
    conflict = str(core_pack.get("_核心冲突", "") or "")
    # 一句话核心主题
    subject = chars[0] if chars else "主角"
    core_theme = f"{subject}在{loc or '特定空间'}的{theme}故事" + (f" (核心冲突: {conflict})" if conflict else "")
    # 人物与基础设定 (用户实体优先, 核心包角色锚补位)
    char_lines = []
    if chars:
        for c in chars[:3]:
            char_lines.append(f"{c}: 外观/服装/发型全片跨镜头一致, 带至少 2 处瑕疵锚点 (使用痕迹/磨损/擦伤), 表情用具体动作传达, 不用空洞情绪词")
    else:
        char_lines.append("主角: 外观/服装/发型全片跨镜头一致, 带至少 2 处瑕疵锚点 (使用痕迹/磨损/擦伤)")
    char_block = "人物与基础设定:\n" + "\n".join(f"  {x}" for x in char_lines)
    if props:
        char_block += f"\n  关键道具: {'、'.join(props[:4])} (道具承载叙事, 每件有情绪功能)"
    # 氛围与画质 (设备美学包)
    look = str(core_pack.get("_视觉调性", "") or "")
    aq = (f"氛围与画质:\n"
          f"  模拟设备: {dev['camera']}，搭配 {dev['lens']}。\n"
          f"  画质缺陷: {dev['defects']}。\n"
          f"  素材身份: 这是{dev['identity']}，不是广告片。\n"
          f"  色彩与影调: {look or '电影级'}{'，全片锁一档' if minutes and minutes >= 10 else ''}。\n"
          f"  拍摄手法: 手持拍摄，全程保持轻微的、如呼吸般的镜头浮动，增强临场感。")
    # 镜头控制
    arrange = str(core_pack.get("_叙事编排", "") or "跟随叙事结构")
    line = str(core_pack.get("_叙事线型", "") or "单线")
    cc = (f"镜头控制:\n"
          f"  运镜规则: 运镜服务心理 (固定=旁观/缓推=压迫/跟拍=沉浸/手持=临场), 相邻镜头不重复同一运镜。\n"
          f"  叙事: {arrange} / {line}"
          + (f" / 目标时长 {minutes:g} 分钟" if minutes else ""))
    # 声音
    snd = f"声音: 不需要配乐，仅保留同期声 ({sound_cues_str})。" if sound_cues_str else \
          "声音: 不需要配乐，仅保留同期声。"
    shell = (f"核心主题: {core_theme}\n"
             f"{char_block}\n"
             f"{aq}\n"
             f"{cc}\n"
             f"{snd}")
    return shell


def self_check_block():
    """附件'自检清单'式尾注 (诚实声明, 供使用者核对)。"""
    return ("自检清单: 五段结构齐全 / 有摄影机+镜头型号 / 有呼吸感手持 / 声音仅同期声且显式枚举 / "
            "每主体≥2 瑕疵锚点 / 结尾克制留白 / 无空洞情绪词 / 无 IP 名 / 每镜四件套 (景别+构图+运镜+画面内容)")


# ----------------------------------------------------------------
# 8. 写法A: 按秒切 (≤20s 单场景)
# ----------------------------------------------------------------
_BAND_LABELS = [("凝视", "环境与人物关系建立"), ("启动", "触发事件出现"),
                ("升级", "对抗/张力上升"), ("爆发", "情绪与动作峰值"),
                ("余韵", "留白与收束")]


def second_by_second(shots, total_sec, ent):
    """把 ≤20s 的分镜聚合成按秒切时间轴 ([0-3s·凝视] 式), 写法A。
    返回多行字符串; shots 为空返回 ""。"""
    if not shots or total_sec <= 0:
        return ""
    n_bands = min(5, max(3, int(total_sec // 4) or 3))
    per = total_sec / n_bands
    lines = ["一镜到底 · 按秒切时间轴 (写法A):"]
    chars = (ent or {}).get("characters") or ["主角"]
    for b in range(n_bands):
        t0 = int(round(b * per))
        t1 = int(round((b + 1) * per))
        label, intent = _BAND_LABELS[min(b, len(_BAND_LABELS) - 1)]
        # 该时间带覆盖的镜
        lo, hi = b * per, (b + 1) * per
        band_shots = []
        acc = 0.0
        for s in shots:
            try:
                d = float(s.get("dur_sec", 0) or 0)
            except (TypeError, ValueError):
                d = 0.0
            s0, s1 = acc, acc + d
            acc = s1
            if s1 > lo and s0 < hi:
                band_shots.append(s)
        if band_shots:
            rep = band_shots[0]
            content = str(rep.get("focus", ""))[:80]
            move = str(rep.get("move", ""))
            size = str(rep.get("size", ""))
            lines.append(f"  [{t0}-{t1}s · {label}] {intent}。{content} "
                         f"({size}, {move}, 呼吸感手持)")
        else:
            lines.append(f"  [{t0}-{t1}s · {label}] {intent} (呼吸感手持)")
    return "\n".join(lines)
