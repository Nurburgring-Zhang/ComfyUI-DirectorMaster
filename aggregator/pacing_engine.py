# -*- coding: utf-8 -*-
"""
V12.6 v9: 节奏引擎 (Pacing Engine) — 世界顶级导演的镜头语言
=========================================================
覆盖 15+ 节奏风格, 从 0.3s 一秒三闪到 180s 一镜到底:

  快闪类 (cutting, 0.3-1s):
    1. 一秒三闪 (one_sec_three)       — 0.3s × 3 镜, 情绪爆发/嗨爆/MV 高潮
    2. 抖音超快 (tiktok_hyper)        — 0.5-1s × N 镜, 短视频/快剪
    3. 子弹时间 (bullet_time)         — 0.5-2s 360° 静止环绕, 动作凝固
    4. 蒙太奇 (montage)               — 0.5-3s × 8-20 镜, 时间压缩/抒情

  长镜类 (long_take, 30-180s):
    5. 固定长镜 (long_take_static)    — 30-90s 单镜, 侯孝贤/是枝裕和 式
    6. 游走长镜 (long_take_walk)      — 60-180s 跟拍/斯坦尼康, 拉赞纽斯/贝拉·塔尔
    7. 对话长镜 (long_take_dialogue)  — 30-90s 双人中景, 李安/阿巴斯
    8. 一镜到底 (one_shot)            — 300-600s 整段不切, 俄罗斯方舟式

  慢镜类 (slow_motion):
    9. 慢镜高光 (slow_motion)         — 1-3s 实际 5-10s 慢放, 王家卫/诺兰
   10. 极慢抒情 (ultra_slow)          — 1-2s 实际 15-30s 慢放, 泰伦斯·马力克

  特殊类 (special):
   11. 定格 (freeze_frame)            — 1-3s 单帧延长, 港片高潮
   12. 延时摄影 (time_lapse)          — 0.5-2s 压缩, 宫崎骏/是枝裕和
   13. POV 主观 (pov_subjective)      — 1-3s 角色视角
   14. 航拍 (aerial_sweep)            — 5-15s 升/降, 诺兰《盗梦空间》开场

  类型专属 (genre_specific):
   15. 车戏分镜 (car_chase)           — 1-3s 跟拍, 速度感/危险感
   16. 枪战分镜 (gunfight)            — 0.5-2s 手持快切, 吴宇森/迈克尔·曼
   17. 演唱会纪录 (concert_doc)       — 5-15s 跟拍+航拍, 怀斯曼式
   18. MV 慢镜 (mv_slow_motion)       — 1-5s 慢镜 + 跳切, 大卫·芬奇/Mark Romanek
   19. 舞蹈编排 (dance_choreography)  — 1-3s 多机位切换, 法哈蒂/毕赣
"""
import hashlib as _hashlib


def _normalize_director(director):
    """V12.6 v13: pacing 引擎本地版本, 11 派别归一化. 与 feature_film_engine 同源."""
    if not director:
        return "default"
    if any(k in director for k in ["王家卫", "Wong Kar-wai", "wong", "kar-wai"]):
        return "王家卫"
    if any(k in director for k in ["侯孝贤", "Hou Hsiao-hsien", "hou"]):
        return "侯孝贤"
    if any(k in director for k in ["是枝裕和", "Koreeda", "koreeda"]):
        return "是枝裕和"
    if any(k in director for k in ["李安", "Ang Lee", "ang lee"]):
        return "李安"
    if any(k in director for k in ["贾樟柯", "Jia Zhangke", "zhangke"]):
        return "贾樟柯"
    if any(k in director for k in ["诺兰", "Nolan", "nolan", "Christopher"]):
        return "诺兰"
    if any(k in director for k in ["塔可夫斯基", "Tarkovsky", "tarkovsky", "Andrei"]):
        return "塔可夫斯基"
    if any(k in director for k in ["希区柯克", "Hitchcock", "hitchcock", "Alfred"]):
        return "希区柯克"
    if any(k in director for k in ["黑泽明", "Kurosawa", "kurosawa", "Akira"]):
        return "黑泽明"
    if any(k in director for k in ["库布里克", "Kubrick", "kubrick", "Stanley"]):
        return "库布里克"
    return "default"


# ============================================================
# 15+ 节奏风格池 — 每种定义 (镜头序列模板, 适用场景, 大师参考)
# ============================================================
PACING_STYLES = {
    # === 快闪类 (0.3-1s) ===
    "一秒三闪": {
        "category": "快闪",
        "description": "0.3s × 3 镜 = 0.9s, 配合音乐节拍, 情绪爆发/嗨爆场面",
        "masters": ["王家卫 (《旺角卡门》)", "吴宇森 (《英雄本色》)", "诺兰 (《盗梦空间》梦境)"],
        "use_cases": ["情绪爆发顶点", "动作高潮", "MV 高潮段", "嗨爆场面", "高潮瞬间", "心理冲击"],
        "shot_sequence": [
            # 一秒三闪 = 3 镜 × 0.3s + 1s 收束
            {"n": 1, "size": "大特写", "move": "固定", "focal": "85mm", "angle": "平视", "cut": "硬切", "dur": 0.3,
             "focus_tpl": "{c1}的眼, 瞳孔收缩", "sound_tpl": "心悸一拍",
             "pacing_intent": "0.3s 极致瞬间 — 表情/情绪的爆破点"},
            {"n": 2, "size": "特写", "move": "快推", "focal": "50mm", "angle": "侧45", "cut": "硬切", "dur": 0.3,
             "focus_tpl": "{c1}的动作(拳/吻/泪), 凝固一瞬", "sound_tpl": "动作声一拍",
             "pacing_intent": "0.3s 动作爆发 — 物理动作的最快点"},
            {"n": 3, "size": "中景", "move": "快摇", "focal": "35mm", "angle": "平视", "cut": "跳切", "dur": 0.3,
             "focus_tpl": "环境/对手反应, 0.3s 闪", "sound_tpl": "环境音一拍",
             "pacing_intent": "0.3s 闪后 — 切换视角, 速度感的延续"},
            {"n": 4, "size": "全景", "move": "拉远", "focal": "24mm", "angle": "平视", "cut": "叠化", "dur": 1.0,
             "focus_tpl": "拉远, 让观众回过神, 1s 收束", "sound_tpl": "环境音回归",
             "pacing_intent": "1s 收束 — 让观众从 0.3s 三连击中回过神"},
        ],
    },
    "抖音超快": {
        "category": "快闪",
        "description": "0.5-1s 镜 × 10+ 镜, 短视频快剪, 视觉密度爆炸",
        "masters": ["陈星汉", "苹果广告", "抖音爆款 MCN", "PewDiePie"],
        "use_cases": ["抖音短视频", "广告片", "30s 高密度", "产品展示", "嗨爆预告"],
        "shot_sequence": [
            {"n": 1, "size": "大特写", "move": "快推", "focal": "85mm", "angle": "平视", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "产品/角色眼睛, 第一印象", "sound_tpl": "节拍重音一拍", "pacing_intent": "0.5s 钩子 — 让观众停下来"},
            {"n": 2, "size": "中近景", "move": "跟拍", "focal": "35mm", "angle": "平视", "cut": "跳切", "dur": 0.7,
             "focus_tpl": "{c1}的动作, 0.7s 一个动作", "sound_tpl": "动作声+节拍", "pacing_intent": "0.7s 动作 — 推进"},
            {"n": 3, "size": "特写", "move": "快切", "focal": "50mm", "angle": "侧45", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "物件/细节, 0.5s 闪", "sound_tpl": "物件声一拍", "pacing_intent": "0.5s 物件闪"},
            {"n": 4, "size": "中景", "move": "推近", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 0.8,
             "focus_tpl": "{c1}表情变化, 0.8s 推", "sound_tpl": "情绪音", "pacing_intent": "0.8s 表情推"},
            {"n": 5, "size": "全景", "move": "环绕", "focal": "24mm", "angle": "平视", "cut": "硬切", "dur": 1.0,
             "focus_tpl": "环境/动作全景, 1s 展示", "sound_tpl": "音乐高潮一拍", "pacing_intent": "1s 节奏高点"},
            {"n": 6, "size": "近景", "move": "跳切", "focal": "50mm", "angle": "平视", "cut": "跳切", "dur": 0.6,
             "focus_tpl": "{c1}对话/反应, 0.6s", "sound_tpl": "对白+节拍", "pacing_intent": "0.6s 对话节拍"},
            {"n": 7, "size": "特写", "move": "快推", "focal": "85mm", "angle": "俯拍", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "关键物件特写, 0.5s", "sound_tpl": "物件声", "pacing_intent": "0.5s 物件闪"},
            {"n": 8, "size": "中景", "move": "推", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 0.7,
             "focus_tpl": "{c1}动作继续, 0.7s", "sound_tpl": "动作+节拍", "pacing_intent": "0.7s 动作"},
            {"n": 9, "size": "全景", "move": "拉远", "focal": "24mm", "angle": "平视", "cut": "硬切", "dur": 0.8,
             "focus_tpl": "拉远, 准备结束, 0.8s", "sound_tpl": "音乐渐弱", "pacing_intent": "0.8s 收束"},
            {"n": 10, "size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "淡出", "dur": 1.0,
             "focus_tpl": "{c1}最后表情, 1s 收束", "sound_tpl": "环境音回归+心跳", "pacing_intent": "1s 收束 — 让观众回过神"},
        ],
    },
    "子弹时间": {
        "category": "快闪",
        "description": "0.5-2s 360° 静止环绕, 物体/角色凝固一瞬, 角度变换",
        "masters": ["沃卓斯基姐妹 (《黑客帝国》)", "迈克尔·贝 (《终结者2》T-1000)", "周杰伦 MV"],
        "use_cases": ["子弹/刀光时刻", "动作高潮", "MV 凝固", "舞蹈定格"],
        "shot_sequence": [
            {"n": 1, "size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "子弹/刀的起点, 0.5s 静止开始", "sound_tpl": "完全静默",
             "pacing_intent": "0.5s 凝固起点 — 观众的注意力完全锁死"},
            {"n": 2, "size": "特写", "move": "环绕慢移", "focal": "85mm", "angle": "环绕 90°", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "环绕角色, 90° 视角变化, 0.5s", "sound_tpl": "环境音极慢",
             "pacing_intent": "0.5s 环绕 90° — 让观众看到平时看不到的角度"},
            {"n": 3, "size": "中近景", "move": "环绕慢移", "focal": "50mm", "angle": "环绕 180°", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "环绕 180°, 0.5s", "sound_tpl": "环境音",
             "pacing_intent": "0.5s 环绕 180° — 完全不同的视角"},
            {"n": 4, "size": "全景", "move": "环绕快", "focal": "24mm", "angle": "环绕 360°", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "360° 全景, 0.5s", "sound_tpl": "风/空气声",
             "pacing_intent": "0.5s 360° — 空间感彻底建立"},
            {"n": 5, "size": "中景", "move": "慢速恢复", "focal": "50mm", "angle": "平视", "cut": "叠化", "dur": 1.0,
             "focus_tpl": "时间恢复, 1s 收束", "sound_tpl": "环境音回归",
             "pacing_intent": "1s 收束 — 时间恢复正常流速"},
        ],
    },
    "蒙太奇": {
        "category": "快闪",
        "description": "0.5-3s 镜 × 8-20 镜, 时间压缩/抒情/交代, 爱森斯坦/普多夫金",
        "masters": ["爱森斯坦 (《战舰波将金号》)", "普多夫金 (《母亲》)", "莱昂内 (西部片)"],
        "use_cases": ["时间跨越", "训练/成长", "情感积累", "叙事压缩"],
        "shot_sequence": [
            {"n": i, "size": ["大特写", "特写", "中近景", "中景", "全景"][i % 5],
             "move": ["固定", "推", "跟拍", "固定", "拉"][i % 5],
             "focal": ["85mm", "50mm", "35mm", "50mm", "24mm"][i % 5],
             "angle": "平视", "cut": "硬切", "dur": [0.5, 1.0, 1.5, 2.0, 2.5][i % 5],
             "focus_tpl": "蒙太奇第{idx}镜 — 阶段性瞬间, 0.5-2.5s",
             "sound_tpl": "音乐渐强 + 拟音", "pacing_intent": "蒙太奇瞬间, 时间压缩/抒情推进"}
            for i in range(1, 11)  # 10 镜蒙太奇, 每镜 0.5-2.5s
        ],
    },
    # === 长镜类 (30-180s) ===
    "固定长镜": {
        "category": "长镜",
        "description": "30-90s 单镜不切, 固定机位, 让时间真实流动, 侯孝贤/是枝裕和",
        "masters": ["侯孝贤 (《悲情城市》)", "是枝裕和 (《步履不停》)", "小津安二郎 (《东京物语》)"],
        "use_cases": ["日常记录", "情感积蓄", "真实感", "无剪辑艺术"],
        "shot_sequence": [
            {"n": 1, "size": "中景", "move": "固定 (30-90s)", "focal": "50mm", "angle": "平视", "cut": "无切", "dur": 60.0,
             "focus_tpl": "{c1}在{location}中, 一段真实时间, 60s 不切, 让时间流动, 让观众'住在'这一分钟里",
             "sound_tpl": "环境音(完整) + 偶尔的拟音 + 留白, 不配乐, 让真实感沉淀",
             "pacing_intent": "60s 真实时间 — 观众坐在'侯孝贤的椅子'上, 看真实生活展开"},
        ],
    },
    "游走长镜": {
        "category": "长镜",
        "description": "60-180s 跟拍/斯坦尼康 360° 调度, 一镜到底穿越多个空间, 拉赞纽斯/贝拉·塔尔",
        "masters": ["贝拉·塔尔 (《都柏林 147min 一镜》)", "拉赞纽斯 (《大事件》开场 7min)", "陈可辛 (《投名状》)"],
        "use_cases": ["群戏调度", "空间穿越", "高光时刻", "技术展示"],
        "shot_sequence": [
            {"n": 1, "size": "中景", "move": "斯坦尼康跟拍 (60-180s)", "focal": "35mm", "angle": "环绕", "cut": "无切", "dur": 120.0,
             "focus_tpl": "从 {location} 起点 跟拍 {c1} 走/跑/做, 120s 一镜穿越多个空间, 调度 5-15 个角色, 贝拉·塔尔式",
             "sound_tpl": "现场同期声 (含脚步/对话/环境) + 偶尔音乐进入, 真实感极致",
             "pacing_intent": "120s 调度长镜 — 让观众'住在这一镜里', 看完整事件"},
        ],
    },
    "对话长镜": {
        "category": "长镜",
        "description": "30-90s 双人中景, 一镜不切, 完整对话/沉默, 李安/阿巴斯",
        "masters": ["阿巴斯·基亚罗斯塔米 (《樱桃的滋味》)", "李安 (《饮食男女》)", "王家卫 (《花样年华》走廊)"],
        "use_cases": ["深度对话", "情感对峙", "潜台词", "两人关系"],
        "shot_sequence": [
            {"n": 1, "size": "中景双人对切", "move": "固定 (30-90s)", "focal": "50mm", "angle": "平视/微微过肩", "cut": "无切", "dur": 60.0,
             "focus_tpl": "{c1} 和 {c2} 对坐/并排, 60s 不切, 一整段对话/沉默, 李安/阿巴斯式, 让观众'坐在旁边'",
             "sound_tpl": "完整对话 + 留白 + 呼吸, 偶尔环境音, 不配乐, 让语言本身的重量显现",
             "pacing_intent": "60s 完整对话/沉默 — 时间不被剪辑, 关系不被剪碎"},
        ],
    },
    "一镜到底": {
        "category": "长镜",
        "description": "300-600s 整段不切, 整部电影/段落一镜, 俄罗斯方舟式极限",
        "masters": ["亚历山大·索科洛夫 (《俄罗斯方舟》96min 整段)", "塞巴斯蒂安·席佩尔 (《维多利亚》140min)"],
        "use_cases": ["电影整体", "哲学", "技术极限", "舞台剧感"],
        "shot_sequence": [
            {"n": 1, "size": "全景到中景", "move": "穿越 (300-600s)", "focal": "35mm", "angle": "环绕调度", "cut": "无切", "dur": 480.0,
             "focus_tpl": "整段 8 分钟一镜, 穿越多个时代/空间, 480s 不切, 索科洛夫/席佩尔式, 观众的注意力全在调度",
             "sound_tpl": "完整时空, 同期声 + 音乐进入 + 时代切换音, 不切",
             "pacing_intent": "480s 一镜到底 — 观众的呼吸和电影同步, 极致沉浸"},
        ],
    },
    # === 慢镜类 ===
    "慢镜高光": {
        "category": "慢镜",
        "description": "1-3s 实际 5-10s 慢放, 高光时刻, 王家卫/诺兰",
        "masters": ["王家卫 (《重庆森林》)", "诺兰 (《盗梦空间》)", "扎克·施奈德 (《300 勇士》)"],
        "use_cases": ["情感高潮", "动作凝固", "诗意瞬间", "MV 高潮"],
        "shot_sequence": [
            {"n": 1, "size": "中景", "move": "慢速环绕", "focal": "50mm", "angle": "环绕 360°", "cut": "叠化", "dur": 2.0,
             "focus_tpl": "1/8 慢镜, 2s 实际 = 16s 慢放, 王家卫式, 让瞬间变成永恒",
             "sound_tpl": "音乐+呼吸+心跳, 慢节奏, 慢放到 1/4 速度",
             "pacing_intent": "2s 慢镜 — 1/8 速度, 让观众'住在这一刻'"},
        ],
    },
    "极慢抒情": {
        "category": "慢镜",
        "description": "1-2s 实际 15-30s 慢放, 自然/空镜, 泰伦斯·马力克/塔可夫斯基",
        "masters": ["泰伦斯·马力克 (《天堂之日》)", "塔可夫斯基 (《乡愁》)", "阿彼察邦·韦拉斯哈古"],
        "use_cases": ["自然空镜", "时间流逝", "诗意", "梦境"],
        "shot_sequence": [
            {"n": 1, "size": "大远景", "move": "固定", "focal": "14mm", "angle": "平视", "cut": "叠化", "dur": 1.5,
             "focus_tpl": "自然/天空/水面, 1.5s 实际 = 30s 慢放, 1/20 速度, 马力克式",
             "sound_tpl": "风/水/光, 自然音, 旁白进入",
             "pacing_intent": "1.5s 极慢 — 1/20 速度, 让时间'溶解'"},
        ],
    },
    # === 特殊类 ===
    "定格": {
        "category": "特殊",
        "description": "1-3s 单帧延长, 凝固动作/画面, 港片高潮/漫画感",
        "masters": ["吴宇森 (《英雄本色》)", "北野武", "昆汀·塔伦蒂诺"],
        "use_cases": ["高潮瞬间", "漫画感", "动作凝固", "经典瞬间"],
        "shot_sequence": [
            {"n": 1, "size": "特写", "move": "固定", "focal": "85mm", "angle": "平视", "cut": "定格", "dur": 2.0,
             "focus_tpl": "{c1} 的动作/表情, 凝固 2s, 港片高潮式, 让'瞬间'变成'永远'",
             "sound_tpl": "音乐骤停 + 一拍静默 + 慢放, 时间被拉长",
             "pacing_intent": "2s 定格 — 时间的'暂停键'"},
        ],
    },
    "延时摄影": {
        "category": "特殊",
        "description": "0.5-2s 压缩 1 小时/1 天/1 年, 宫崎骏/是枝裕和",
        "masters": ["宫崎骏 (《起风了》)", "是枝裕和 (《步履不停》)", "雅克·贝汉 (《迁徙的鸟》)"],
        "use_cases": ["时间流逝", "季节变换", "城市变化", "生命循环"],
        "shot_sequence": [
            {"n": 1, "size": "全景", "move": "固定", "focal": "24mm", "angle": "平视", "cut": "叠化", "dur": 1.5,
             "focus_tpl": "0.5s 镜头 = 1 天, 时间被压缩, 宫崎骏/雅克·贝汉式",
             "sound_tpl": "音乐渐强 + 时间音 (钟/光/季节), 旁白可进入",
             "pacing_intent": "1.5s 延时 — 1 个月被压缩到 1 秒"},
        ],
    },
    "POV 主观": {
        "category": "特殊",
        "description": "1-3s 角色视角, 让观众'成为'角色, 德·帕尔玛/索德伯格",
        "masters": ["布莱恩·德·帕尔玛 (《疤面煞星》)", "索德伯格 (《十一罗汉》)", "GTA 游戏视角"],
        "use_cases": ["恐怖", "主观沉浸", "游戏感", "动作"],
        "shot_sequence": [
            {"n": 1, "size": "中近景", "move": "手持跟拍", "focal": "35mm", "angle": "POV", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "{c1} 的视角, 看到 {c2} / 物件 / 环境, 2s 主观",
             "sound_tpl": "{c1} 呼吸+心跳+环境, 让观众'住在角色里'",
             "pacing_intent": "2s POV — 观众的眼睛 = 角色的眼睛"},
        ],
    },
    "航拍": {
        "category": "特殊",
        "description": "5-15s 升/降/穿越, 诺兰《盗梦空间》开场/《权游》",
        "masters": ["诺兰 (《盗梦空间》巴黎折叠)", "HBO《权游》", "Dji 无人机时代"],
        "use_cases": ["地理感", "史诗", "城市", "自然奇观"],
        "shot_sequence": [
            {"n": 1, "size": "大远景", "move": "航拍升降", "focal": "14mm", "angle": "俯拍/斜拍", "cut": "叠化", "dur": 10.0,
             "focus_tpl": "从 5m 升到 500m, 10s, 看到整个 {location} 的全貌, 诺兰式",
             "sound_tpl": "风+环境音+音乐渐强, 史诗感",
             "pacing_intent": "10s 航拍 — 观众'飞'过整个场景"},
        ],
    },
    # === 类型专属 ===
    "车戏分镜": {
        "category": "类型",
        "description": "1-3s 跟拍/跟焦/广角, 速度感/危险感/速度+方向感",
        "masters": ["迈克尔·曼 (《盗火线》)", "尼古拉斯·温丁·雷弗恩 (《亡命驾驶》)", "吴宇森"],
        "use_cases": ["追车", "飙车", "快速通过", "危险"],
        "shot_sequence": [
            {"n": 1, "size": "中近景", "move": "跟拍", "focal": "35mm", "angle": "侧拍", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "车外, 跟拍 {c1} 驾驶, 2s 速度感", "sound_tpl": "引擎+风+轮胎尖叫", "pacing_intent": "2s 跟车"},
            {"n": 2, "size": "特写", "move": "手持", "focal": "24mm", "angle": "车内 POV", "cut": "硬切", "dur": 1.5,
             "focus_tpl": "车内, {c1} 的脸/方向盘, 1.5s", "sound_tpl": "引擎+心跳", "pacing_intent": "1.5s 车内"},
            {"n": 3, "size": "全景", "move": "摇镜", "focal": "24mm", "angle": "后拍", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "车外后拍, 2s", "sound_tpl": "引擎+风", "pacing_intent": "2s 后拍"},
            {"n": 4, "size": "特写", "move": "固定", "focal": "50mm", "angle": "仪表盘", "cut": "硬切", "dur": 1.0,
             "focus_tpl": "仪表盘指针红区, 1s", "sound_tpl": "警报", "pacing_intent": "1s 仪表"},
            {"n": 5, "size": "远景", "move": "航拍", "focal": "14mm", "angle": "俯拍", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "航拍, 3s 整段追逐", "sound_tpl": "音乐高潮", "pacing_intent": "3s 航拍"},
        ],
    },
    "枪战分镜": {
        "category": "类型",
        "description": "0.5-2s 手持快切/跳切, 紧张/暴烈/混乱, 吴宇森/迈克尔·曼",
        "masters": ["吴宇森 (《喋血双雄》)", "迈克尔·曼 (《盗火线》)", "朴赞郁 (《老男孩》)"],
        "use_cases": ["枪战", "搏击", "暴烈", "紧张"],
        "shot_sequence": [
            {"n": 1, "size": "大特写", "move": "固定", "focal": "85mm", "angle": "平视", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "扳机扣下, 0.5s 极快", "sound_tpl": "枪响一拍", "pacing_intent": "0.5s 扳机"},
            {"n": 2, "size": "中近景", "move": "手持快切", "focal": "35mm", "angle": "平视", "cut": "跳切", "dur": 0.8,
             "focus_tpl": "{c1} 开火, 0.8s 手持晃", "sound_tpl": "枪声+后坐力", "pacing_intent": "0.8s 开火"},
            {"n": 3, "size": "特写", "move": "快推", "focal": "50mm", "angle": "侧45", "cut": "硬切", "dur": 0.5,
             "focus_tpl": "弹壳弹出, 0.5s 极快", "sound_tpl": "弹壳声", "pacing_intent": "0.5s 弹壳"},
            {"n": 4, "size": "中景", "move": "手持甩镜", "focal": "24mm", "angle": "荷兰角", "cut": "跳切", "dur": 0.7,
             "focus_tpl": "对手中弹, 0.7s 甩镜", "sound_tpl": "中弹声", "pacing_intent": "0.7s 中弹"},
            {"n": 5, "size": "全景", "move": "甩镜", "focal": "24mm", "angle": "荷兰角", "cut": "硬切", "dur": 1.0,
             "focus_tpl": "环境混乱, 1s", "sound_tpl": "环境+回声", "pacing_intent": "1s 环境"},
        ],
    },
    "演唱会纪录": {
        "category": "类型",
        "description": "5-15s 跟拍+航拍+大特写, 怀斯曼式/马利克式, 让观众'在现场'",
        "masters": ["弗雷德里克·怀斯曼 (《波士顿市政厅》)", "泰伦斯·马力克", "PJ 哈维 (专辑)"],
        "use_cases": ["演唱会", "舞台", "音乐节", "现场感"],
        "shot_sequence": [
            {"n": 1, "size": "大远景", "move": "航拍", "focal": "14mm", "angle": "俯拍", "cut": "叠化", "dur": 8.0,
             "focus_tpl": "航拍, 8s 整个场馆/万人", "sound_tpl": "音乐+万人欢呼", "pacing_intent": "8s 航拍"},
            {"n": 2, "size": "中景", "move": "斯坦尼康跟拍", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 6.0,
             "focus_tpl": "跟拍 {c1} 表演, 6s", "sound_tpl": "现场音乐+呼吸", "pacing_intent": "6s 跟拍"},
            {"n": 3, "size": "大特写", "move": "固定", "focal": "100mm", "angle": "平视", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "手/弦/鼓, 3s 特写", "sound_tpl": "乐器+放大", "pacing_intent": "3s 手部特写"},
            {"n": 4, "size": "中景", "move": "环绕", "focal": "35mm", "angle": "环绕", "cut": "硬切", "dur": 5.0,
             "focus_tpl": "环绕 360°, 5s", "sound_tpl": "音乐高潮", "pacing_intent": "5s 环绕"},
            {"n": 5, "size": "特写", "move": "推", "focal": "85mm", "angle": "平视", "cut": "硬切", "dur": 4.0,
             "focus_tpl": "{c1} 表情, 4s 推到最近", "sound_tpl": "音乐+表情", "pacing_intent": "4s 表情"},
        ],
    },
    "MV 慢镜": {
        "category": "类型",
        "description": "1-5s 慢镜 + 跳切, 大卫·芬奇/Mark Romanek, 视觉+音乐同步",
        "masters": ["大卫·芬奇", "Mark Romanek", "Hype Williams", "泰勒·斯威夫特 MV"],
        "use_cases": ["MV", "广告", "高光时刻", "视觉重击"],
        "shot_sequence": [
            {"n": 1, "size": "特写", "move": "慢推", "focal": "85mm", "angle": "平视", "cut": "跳切", "dur": 2.0,
             "focus_tpl": "1/4 慢镜, {c1} 表情, 2s", "sound_tpl": "音乐节拍一拍", "pacing_intent": "2s 慢镜"},
            {"n": 2, "size": "中景", "move": "环绕慢", "focal": "50mm", "angle": "环绕", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "环绕 360°, 3s", "sound_tpl": "音乐节拍二拍", "pacing_intent": "3s 环绕"},
            {"n": 3, "size": "大特写", "move": "固定", "focal": "100mm", "angle": "俯拍", "cut": "跳切", "dur": 1.5,
             "focus_tpl": "细节, 1.5s 跳切", "sound_tpl": "音乐+节拍", "pacing_intent": "1.5s 跳切"},
            {"n": 4, "size": "全景", "move": "拉远", "focal": "24mm", "angle": "平视", "cut": "硬切", "dur": 4.0,
             "focus_tpl": "拉远, 4s", "sound_tpl": "音乐高潮", "pacing_intent": "4s 拉远"},
        ],
    },
    "舞蹈编排": {
        "category": "类型",
        "description": "1-3s 多机位切换, 法哈蒂/毕赣, 群戏/舞步同步",
        "masters": ["法哈蒂 (《一次别离》)", "毕赣 (《路边野餐》)", "Pina Bausch (皮娜·鲍什)"],
        "use_cases": ["舞蹈", "群戏", "仪式", "节拍"],
        "shot_sequence": [
            {"n": 1, "size": "全景", "move": "固定", "focal": "35mm", "angle": "平视", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "全景, 3s 群戏/舞步", "sound_tpl": "音乐+脚步", "pacing_intent": "3s 群戏"},
            {"n": 2, "size": "中景", "move": "跟拍", "focal": "50mm", "angle": "平视", "cut": "硬切", "dur": 2.0,
             "focus_tpl": "跟拍 {c1}, 2s", "sound_tpl": "音乐+动作", "pacing_intent": "2s 跟拍"},
            {"n": 3, "size": "特写", "move": "固定", "focal": "85mm", "angle": "俯拍", "cut": "硬切", "dur": 1.5,
             "focus_tpl": "脚/手, 1.5s 细节", "sound_tpl": "脚步+节拍", "pacing_intent": "1.5s 脚部"},
            {"n": 4, "size": "全景", "move": "环绕", "focal": "24mm", "angle": "环绕", "cut": "硬切", "dur": 3.0,
             "focus_tpl": "环绕, 3s 收束", "sound_tpl": "音乐高潮", "pacing_intent": "3s 环绕"},
        ],
    },
}


# ============================================================
# V12.6 v13: 节奏风格 — 按 story_function 动态查表 (替代 V12 按 (act, scene_index) 35 场硬编码)
# 关键: 不再有"场 18 = 中点 = 一秒三闪" 这种位置绑定, 而是按"中点"这个 story_function 自动选
#       不同 story_theory 的中点/触发/灵魂黑夜 等都用同表, 不再被场次位置绑架
# ============================================================
# story_function 关键词 → 推荐节奏
STORY_FUNC_PACING = {
    # 建立类 — 长镜/对话长镜 (世界顶级导演开场都是长镜)
    "建立": "固定长镜",
    "开场": "固定长镜",
    "平凡世界": "固定长镜",
    "起": "对话长镜",
    "主题": "对话长镜",
    "铺垫": "蒙太奇",
    "新世界": "固定长镜",
    "乐趣": "蒙太奇",
    # 冲突/转折类 — 快剪/抖音超快/慢镜高光
    "触发": "抖音超快",
    "催化": "抖音超快",
    "中点": "一秒三闪",
    "敌人": "抖音超快",
    "逼近": "抖音超快",
    "压力": "抖音超快",
    "失去": "一秒三闪",
    "反转": "一秒三闪",
    "对决": "子弹时间",
    "牺牲": "慢镜高光",
    # 安静/留白/情绪 — 极慢/长镜
    "灵魂的黑夜": "极慢抒情",
    "黑夜": "极慢抒情",
    "决定": "对话长镜",
    "承诺": "对话长镜",
    "发现": "固定长镜",
    "转折": "固定长镜",
    "准备": "蒙太奇",
    # 高潮/收束类 — 极致密度 / 极慢
    "高潮": "一秒三闪",
    "终局": "子弹时间",
    "集结": "蒙太奇",
    "合": "对话长镜",
    "解决": "固定长镜",
    "收束": "极慢抒情",
    "结尾": "固定长镜",
    "尾声": "极慢抒情",
    "升华": "极慢抒情",
    "副线": "固定长镜",
    "深化": "对话长镜",
    "情节点": "蒙太奇",
    # B 故事/副线
    "B 故事": "对话长镜",
    "副线发展": "蒙太奇",
}


# Director override — 王家卫/侯孝贤/塔可夫斯基倾向长镜/慢镜; 诺兰/希区柯克倾向快剪/蒙太奇
DIRECTOR_PACING_BIAS = {
    "王家卫": {"慢镜": 1.5, "长镜": 1.4, "快剪": 0.5, "蒙太奇": 0.7},
    "侯孝贤": {"慢镜": 1.6, "长镜": 1.5, "快剪": 0.4, "蒙太奇": 0.6},
    "是枝裕和": {"慢镜": 1.2, "长镜": 1.3, "快剪": 0.6, "蒙太奇": 0.8},
    "李安": {"慢镜": 1.0, "长镜": 1.2, "快剪": 0.9, "蒙太奇": 1.0},
    "贾樟柯": {"慢镜": 0.8, "长镜": 1.0, "快剪": 0.9, "蒙太奇": 1.3},
    "诺兰": {"慢镜": 0.6, "长镜": 0.8, "快剪": 1.4, "蒙太奇": 1.2},
    "塔可夫斯基": {"慢镜": 1.8, "长镜": 1.6, "快剪": 0.3, "蒙太奇": 0.5},
    "希区柯克": {"慢镜": 0.7, "长镜": 0.9, "快剪": 1.3, "蒙太奇": 1.4},
    "黑泽明": {"慢镜": 1.0, "长镜": 0.8, "快剪": 1.2, "蒙太奇": 1.2},
    "库布里克": {"慢镜": 1.1, "长镜": 1.2, "快剪": 0.9, "蒙太奇": 1.0},
    "default": {"慢镜": 1.0, "长镜": 1.0, "快剪": 1.0, "蒙太奇": 1.0},
}


def _classify_pacing(pacing_style):
    """把节奏风格归类到大类: 慢镜/长镜/快剪/蒙太奇"""
    if pacing_style in ("极慢抒情", "慢镜高光", "子弹时间", "一镜到底", "游走长镜", "极慢抒情", "极慢抒情"):
        return "慢镜"
    if pacing_style in ("固定长镜", "对话长镜", "POV 主观", "航拍大师", "延时摄影", "定格凝固"):
        return "长镜"
    if pacing_style in ("一秒三闪", "抖音超快", "MV 慢镜", "车戏分镜", "枪战分镜", "演唱会纪录"):
        return "快剪"
    if pacing_style in ("蒙太奇", "舞蹈编排"):
        return "蒙太奇"
    return "长镜"


def get_pacing_for_scene(story_function="", act=1, scene_index=1, director="default", default="对话长镜"):
    """V12.6 v13: 根据 story_function + act + director 动态推荐节奏.
    流程:
      1. 按 story_function 关键词查 STORY_FUNC_PACING → 基础节奏
      2. 用 director bias 调整 (王家卫/塔可夫斯基等倾向长镜/慢镜)
      3. 兜底: 按 act 比例 (act 1 偏长镜, act 2 偏快剪, act 3 偏收束长镜)
    """
    # 1. 基础节奏: 按 story_function 关键词查表
    base = None
    for kw, pacing in STORY_FUNC_PACING.items():
        if kw in story_function:
            base = pacing
            break

    # 2. director 调整: 查对应类别的偏置, 决定是否替换
    director_key = _normalize_director(director) if director else "default"
    if director_key not in DIRECTOR_PACING_BIAS:
        director_key = "default"
    bias = DIRECTOR_PACING_BIAS[director_key]

    # 3. 如果 base 已找到, 但 director 强烈倾向于别类 (>1.3 阈值), 替换
    if base:
        base_class = _classify_pacing(base)
        # 找 director 偏置最大的类别
        sorted_classes = sorted(bias.items(), key=lambda x: x[1], reverse=True)
        top_class, top_bias = sorted_classes[0]
        # 如果 base 不在 top, 且 top 偏置 >= 1.3, 替换
        if base_class != top_class and top_bias >= 1.3:
            # 映射类别 → 具体节奏
            class_to_pacing = {
                "慢镜": "极慢抒情",
                "长镜": "固定长镜",
                "快剪": "蒙太奇",
                "蒙太奇": "蒙太奇",
            }
            return class_to_pacing[top_class]
        return base

    # 4. 兜底: 全部 STORY_FUNC_PACING 随机选 (替代 V12 按 act 比例)
    if not STORY_FUNC_PACING:
        return default
    fallback_pool = list(STORY_FUNC_PACING.values())
    return fallback_pool[hash((act, scene_index)) % len(fallback_pool)]


def expand_pacing_shots(pacing_style, scene, c1, c2, location, weather, obj_str, scene_shot_n, all_shots, shots_target=8, mode_seed=""):
    """根据节奏风格展开为具体镜头列表.
    V12.6 v9: 按 shots_target 重复模板, 并按场戏时长比例缩放每镜 dur, 让总秒数 cover 场戏时长.
    mode_seed: V14.2 — 模式名种子, 偏移模板起点并折入每镜哈希, 让同节奏模式产出相异镜头序列.
    返回: list of dict (shot 数据)
    """
    if pacing_style not in PACING_STYLES:
        pacing_style = "对话长镜"
    style = PACING_STYLES[pacing_style]
    seq = style["shot_sequence"]
    if not seq:
        return []

    # 场戏时长 (从 scene dict 读) — V14.3 (审查P2防御): 负/零/非法值消毒
    try:
        duration_min = max(0.1, float(scene.get("duration_min", 3.0) or 3.0))
    except Exception:
        duration_min = 3.0
    target_total_dur = duration_min * 60.0

    # 原始模板的 dur 总和 (按 shots_target / len(seq) 重复)
    repeat_count = max(1, shots_target // len(seq) + 1)
    total_template_dur = sum(s.get("dur", 1.0) for s in seq) * (shots_target / len(seq))
    # 缩放因子: 让总秒数 ≈ 场戏时长
    if total_template_dur > 0:
        scale = target_total_dur / total_template_dur
    else:
        scale = 1.0

    # V14.2: 模式种子 → 模板起点偏移 (同节奏不同模式从序列不同位置起步)
    import hashlib as _hl_ms
    _tpl_off = int(_hl_ms.md5(str(mode_seed).encode("utf-8", errors="replace")).hexdigest(), 16) % len(seq) if mode_seed else 0

    # 调整镜头数 (按 shots_target 重复/截断)
    # V14.3 E2: 先算全部缩放时长 → 截断 → 若有缺口按比例归一化 (保相对节奏, 覆盖场戏时长)
    scaled_durs = []
    tpl_refs = []
    for i in range(shots_target):
        tpl_idx = (i + _tpl_off) % len(seq)
        tpl = dict(seq[tpl_idx])  # copy
        # 按比例缩放 dur — V14.3 E2: 30s 上限仅约束短镜模板;
        # 长镜模板 (原生 dur ≥30s, 如 固定长镜60s/斯坦尼康120s/穿越480s) 放宽到 600s,
        # 否则长镜类被截到 30s 导致总时长无法 cover 场戏 (90min -2.78% 根因)。
        native_dur = tpl.get("dur", 1.0)
        scaled_dur = round(native_dur * scale, 1)
        upper = 30.0 if native_dur < 30.0 else 600.0
        scaled_dur = max(0.3, min(upper, scaled_dur))
        scaled_durs.append(scaled_dur)
        tpl_refs.append(tpl)
    _sum_dur = sum(scaled_durs)
    if _sum_dur > 0 and abs(_sum_dur - target_total_dur) > 0.5:
        _fix = target_total_dur / _sum_dur
        scaled_durs = [max(0.3, round(d * _fix, 1)) for d in scaled_durs]
    expanded = []
    for i in range(shots_target):
        tpl = tpl_refs[i]
        tpl["dur"] = scaled_durs[i]
        # 计算 shot_n
        shot_n = scene_shot_n + len(expanded)
        expanded.append(_make_pacing_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, pacing_style, i, mode_seed))
    return expanded


# ============================================================
# V14.3-MERGED D1: 同节奏簇镜头语法差异化 —
#   同一 pacing 簇内的不同模式, 景别/运镜/焦段/角度 也产出相异序列。
#   原则: 只在"同功能档/同族"内做确定性替换 (真实导演选镜差异),
#         不改变时长/叙事功能; 签名运镜 (环绕慢移/斯坦尼康/穿越等) 不参与变体。
# ============================================================

# 焦段同档替代池 (同透视功能的真实镜头选择)
_FOCAL_VARIANTS = {
    "14mm": ["14mm", "12mm", "15mm", "16mm"],
    "24mm": ["24mm", "21mm", "25mm", "27mm"],
    "35mm": ["35mm", "32mm", "28mm", "40mm"],
    "50mm": ["50mm", "45mm", "43mm", "58mm"],
    "85mm": ["85mm", "75mm", "90mm", "100mm"],
    "100mm": ["100mm", "105mm", "90mm", "135mm"],
}

# 运镜同族同义池 — 仅列出的通用运镜参与变体, 未列出 (签名运镜) 恒定
_MOVE_VARIANTS = {
    "固定": ["固定", "锁定机位", "静止机位"],
    "快推": ["快推", "急推", "快速推近"],
    "推近": ["推近", "缓推", "慢速推近"],
    "推": ["推", "缓推", "微推"],
    "拉远": ["拉远", "后拉", "缓慢拉远"],
    "快摇": ["快摇", "急摇", "快速横摇"],
    "摇镜": ["摇镜", "横摇", "缓摇"],
    "跟拍": ["跟拍", "跟移", "侧跟"],
    "手持跟拍": ["手持跟拍", "手持跟移", "肩扛跟拍"],
    "手持": ["手持", "手持微晃", "肩扛"],
    "环绕": ["环绕", "弧形环绕", "弧线移动"],
    "航拍升降": ["航拍升降", "升降镜头", "吊臂升降"],
    "航拍": ["航拍", "高空航拍", "航拍下压"],
}

# 景别档位 (用于 ±1 档覆盖偏好偏移)
_SIZE_ORDER = ["大远景", "远景", "全景", "中景", "中近景", "近景", "特写", "大特写"]

# 角度微变体 (仅对最常见的"平视"做微俯仰差异)
_ANGLE_VARIANTS = {
    "平视": ["平视", "平视·微仰5°", "平视·微俯5°"],
}


def _grammar_variant(value, field, shot_n, pacing_style, mode_seed):
    """V14.3 D1: 按 mode_seed+shot_n 确定性地把镜头语法字段换到同档/同族变体.

    仅当 mode_seed 非空时生效; 未登记的值原样返回 (签名值保护)。
    """
    if not mode_seed or not value or not isinstance(value, str):
        return value
    import hashlib as _hl_gv
    if field == "focal":
        pool = _FOCAL_VARIANTS.get(value.strip())
    elif field == "move":
        pool = _MOVE_VARIANTS.get(value.strip())
    elif field == "angle":
        pool = _ANGLE_VARIANTS.get(value.strip())
    else:
        pool = None
    if not pool or len(pool) < 2:
        return value
    pick = int(_hl_gv.md5(f"{pacing_style}_{shot_n}_{field}_{mode_seed}".encode("utf-8", "replace")).hexdigest(), 16)
    return pool[pick % len(pool)]


def _size_coverage_shift(size_value, shot_n, pacing_style, mode_seed, idx):
    """V14.3 D1: 每模式的覆盖偏好 — 对 1/3 镜头做 ±1 档景别偏移 (真实导演选镜习惯).

    仅对单一标准景别生效; 复合景别 (中景双人对切/全景到中景/list) 原样返回。
    bias=0 的模式完全不变。
    """
    if not mode_seed or not isinstance(size_value, str) or size_value not in _SIZE_ORDER:
        return size_value
    import hashlib as _hl_cs
    bias = (int(_hl_cs.md5(f"covbias_{pacing_style}_{mode_seed}".encode("utf-8", "replace")).hexdigest(), 16) % 3) - 1
    if bias == 0 or idx % 3 != 0:
        return size_value
    pos = _SIZE_ORDER.index(size_value) + bias
    pos = max(0, min(len(_SIZE_ORDER) - 1, pos))
    return _SIZE_ORDER[pos]


def _make_pacing_shot(shot_n, scene, tpl, c1, c2, location, weather, obj_str, all_shots, pacing_style, idx, mode_seed=""):
    """V12.6 v10: 生成一个具体镜头 dict, 加 5 个深度字段 (director_note/actor_note/visual_design/sound_design/edit_intent).
    mode_seed: V14.2 — 模式名种子, 折入各哈希选择, 让同节奏模式产出相异的焦点/声音/状态。
               V14.3 D1 — 并驱动景别/运镜/焦段/角度的同档变体, 让同节奏簇镜头语法也相异。
    """
    # V12.6 v10: focus 用具体物件 + 身体细节 (不再纯模板拼接)
    primary_obj = obj_str.split("、")[0] if obj_str else "关键道具"
    secondary_obj = obj_str.split("、")[1] if obj_str and len(obj_str.split("、")) > 1 else ""
    # 物件细节 (按 idx 微变, 让叠化长镜组每镜略不同)
    obj_variants = {
        "凤梨罐头": [
            "凤梨罐头标签起泡, 过期十五年的黄印",
            "凤梨罐头被人拿起又放下, 标签上多了一枚指纹",
            "凤梨罐头在灯光下反光, 像是藏了一封信",
        ],
        "旧信": [
            "信纸泛黄, 笔迹模糊, 折痕处已经裂开",
            "信纸被风掀起一角, 露出第二页的笔迹",
            "信被人合上, 但折痕还在, 说明被读过多遍",
        ],
        "钢笔": [
            "钢笔没墨水, 笔尖干涸, 笔帽上刻着两个字",
            "钢笔被握在手里, 但没动, 像是不敢写",
            "钢笔放在桌上, 笔尖朝向门口, 像在等人",
        ],
    }
    obj_pool = obj_variants.get(primary_obj)
    if not obj_pool:
        # V13.3: 通用物件多模板变体 (替代单一"被光线照出细节"导致的 852 次复读)
        obj_pool = [
            f"{primary_obj}被光线照出细节",
            f"{primary_obj}静静待在原处, 像等了很久",
            f"{primary_obj}上有一处使用过的痕迹",
            f"{primary_obj}的位置没变, 但意义变了",
            f"{primary_obj}入了画, 没人先碰它",
            f"{primary_obj}与周围格格不入, 又理所当然",
        ]
    import hashlib as _hl
    obj_idx = int(_hl.md5(f"{shot_n}_{primary_obj}_{mode_seed}".encode()).hexdigest(), 16) % len(obj_pool)
    obj_detail = obj_pool[obj_idx]
    # pacing_intent 模板内容 (用 tpl 里的 focus_tpl)
    pacing_intent_text = tpl["focus_tpl"].format(
        location=location, c1=c1, c2=c2, idx=idx + 1
    )
    # V13.3: 解析 "(A/B/C)" 未决选择 — 按种子确定性选一项, 不再把占位符带进成片
    import re as _re_ph
    def _resolve_choice(m):
        opts = [o for o in m.group(1).split("/") if o.strip()]
        if not opts:
            return ""
        pick = int(_hl.md5(f"{shot_n}_{m.group(0)}_{mode_seed}".encode()).hexdigest(), 16) % len(opts)
        return opts[pick]
    pacing_intent_text = _re_ph.sub(r"\(([^()]*?/[^()]*?)\)", _resolve_choice, pacing_intent_text)
    # 叠化长镜组每镜加入"时间切片"信息
    time_slice_hint = ""
    if pacing_style in ("固定长镜", "对话长镜", "游走长镜"):
        # idx 0 = 开始, idx 1 = 中段, idx 2+ = 收束
        if idx == 0:
            time_slice_hint = "开始切片: 物件先于人物出现。"
        elif idx == 1:
            time_slice_hint = "中段切片: 人物进入, 但动作被时间稀释。"
        else:
            time_slice_hint = "收束切片: 人物没动, 物件被光移动。"
    # V13.3: 状态后缀变体池 (替代恒定"被时间困住")
    _state_suffixes = [
        f"{c1}在场, 但被时间困住",
        f"{c1}在场, 呼吸比动作先泄露",
        f"{c1}在场, 像一句没说出口的话",
        f"{c1}在场, 把情绪压在动作底下",
        f"{c1}在场, 眼神比身体先到",
        f"{c1}在场, 沉默比台词更响",
    ]
    _suf_idx = int(_hl.md5(f"{shot_n}_state_{mode_seed}".encode()).hexdigest(), 16) % len(_state_suffixes)
    focus = f"{location}{weather or ''}。{obj_detail}。{pacing_intent_text}。{_state_suffixes[_suf_idx]}。{time_slice_hint}"
    sound = tpl["sound_tpl"].format(
        location=location, c1=c1, c2=c2
    )

    # 故事阶段 — V12.6 v13: 按 phase 关键词查表 (替代 V12 act+scene_index 硬编码)
    # phase 是 generate_feature_scenes 已经按 story_function 计算好的, 直接用
    phase = scene.get("phase", "建置")
    act = scene.get("act", 1)
    scene_num = scene.get("scene_num", 1)
    story_func = scene.get("story_function", "") or ""

    # 9 阶段字典 (扩展到含序章/中点/留白/主题升华)
    STAGE_MAP = {
        "序章": "序章", "建立": "建立", "建置": "建立", "铺垫": "铺垫", "中点": "中点",
        "转折": "转折", "高潮": "高潮", "留白": "留白", "收束": "收束", "解决": "收束",
        "对抗": "转折", "上升动作": "铺垫", "主题升华": "主题升华", "尾声": "主题升华",
    }
    stage = STAGE_MAP.get(phase, None)

    if not stage:
        # 兜底: 按 story_function 关键词查表
        if any(k in story_func for k in ["建置", "建立", "起", "开场", "主题", "平凡", "铺垫", "副线"]):
            stage = "建立"
        elif any(k in story_func for k in ["上升", "转", "新世界", "试炼", "乐趣"]):
            stage = "铺垫"
        elif any(k in story_func for k in ["中点", "决定", "触发", "催化", "敌人", "压力", "高潮", "对决", "牺牲", "终局", "合", "解决", "收束", "结尾"]):
            stage = "高潮"
        else:
            # 终极兜底: 按 STAGE_ORDER 9 阶段均匀分布
            from scene_engine import STAGE_ORDER
            pos = scene_num / 35.0
            stage_idx = min(int(pos * len(STAGE_ORDER)), len(STAGE_ORDER) - 1)
            stage = STAGE_ORDER[stage_idx]

    # 张力等级
    tension = scene.get("tension_level", 5)
    stage_emotion = {
        1: "日常/平静", 2: "平静/从容", 3: "微妙变化/暗流",
        4: "紧张积累", 5: "暗涌", 6: "冲突/震惊",
        7: "对峙/爆发", 8: "决战场面/震撼", 9: "情感最高点/灵魂黑夜", 10: "爆发/极致/燃烧"
    }.get(tension, "日常/平静")

    color_progression = {
        1: "中性色调", 2: "暖色调(自然)", 3: "略暖", 4: "色彩偏移(微冷)",
        5: "冷色侵入", 6: "冷色调/高对比", 7: "高对比红/黑", 8: "极致对比(明暗)",
        9: "色彩最饱和", 10: "极致色彩(饱和拉满)"
    }
    light_progression = {
        1: "漫射光(阴天)", 2: "顺光/自然光", 3: "侧顺光", 4: "阴影增加",
        5: "光源不稳定", 6: "侧光/逆光(戏剧性)", 7: "底光/顶光", 8: "强光/逆光剪影",
        9: "暖光最强", 10: "戏剧性光影(顶光/底光)"
    }
    material_progression = {
        1: "日常材质", 2: "自然材质(棉/木/石)", 3: "温暖材质(木/棉)", 4: "质感变粗糙",
        5: "金属反光出现", 6: "冷硬材质(金属/玻璃/混凝土)", 7: "尖锐材质",
        8: "冲突材质(铁/血/火)", 9: "肌肤/泪/温暖材质", 10: "极致质感(汗水/血/泪/火花)"
    }
    atmosphere_progression = {
        1: "日常/从容", 2: "平和/自然/温暖", 3: "期待/即将变化", 4: "压抑/积累",
        5: "不安/预兆", 6: "紧张/压迫/失衡", 7: "危险/失控", 8: "震撼/失重",
        9: "情感燃烧", 10: "爆发/极致/燃烧"
    }

    # === V12.6 v10: 5 个深度字段 ===
    import hashlib as _hl
    seed = f"{shot_n}_{pacing_style}_{c1}_{idx}"
    # director_note (按 pacing_style 选) - 池子扩到 8+ 个, 避免重复
    director_notes_by_pacing = {
        "固定长镜": [
            "固定机位 60s, 让'日常'成为'重量', 观众住在'侯孝贤的椅子'上",
            "远景 + 自然光 + 留白, 不切镜, 沉默=台词",
            "不抢戏, 让时间'流过'画面, 观众'看到'一切都是'发生'",
            "边缘构图: 主体在画面 1/3, 中央留给日常物件(凤梨罐头), 让'留白'成为'内容'",
            "不强调情绪, 让'生活的重量'自己出现, 侯孝贤式'看见而不说'",
            "窗框/门框/楼梯: 边缘构图, 主体在角落, 让'框'成为'看'",
            "无配乐, 同期声为主, 让'真实'成为'艺术'",
            "重复: 同一空间连续 30s, 每次'什么都没发生', 但'一切都在发生'",
        ],
        "对话长镜": [
            "对坐中景 60s 不切, 让'吃饭'承载所有",
            "手部特写: 夹菜/放下/再夹, 每次动作有不同含义",
            "过肩镜头: 从父肩看女, 父不知道女在看自己",
            "中近景 60s, 让'沉默'成为'对话'",
            "李安式: 饭桌 = 战场, 筷子 = 武器, 一顿饭打完一场仗",
            "不正面演'想', 用'吃不下'/'夹不住' 让'情绪'可见",
            "用对话节奏 (3s 沉默 + 5s 沉默) 让'等待'成为'内容'",
            "从不切镜, 让观众'住在饭桌旁' 1 分钟, 体会到'家'的重量",
        ],
        "蒙太奇": [
            "0.5-3s 镜快速切换, 时间压缩/抒情, 爱森斯坦式隐喻",
            "用物件(凤梨罐头)替代叙事, 让'看到'成为'理解'",
            "平行蒙太奇: 父切菜 ↔ 女翻信, 同一时间不同空间, 让'等待'成为'张力'",
            "理性蒙太奇: 凤梨罐头(15年) ↔ 现在的凤梨(新鲜), 隐喻'时间从未走'",
            "抒情蒙太奇: 15 年的日常切片(切菜/倒水/擦桌), 让'15年'压缩为 5s",
            "交叉剪辑: 父做饭 ↔ 女儿上学, 让'15 年的牺牲'可见",
        ],
        "一秒三闪": [
            "0.3s × 3 镜, 让'瞬间'成为'永恒', 王家卫式嗨爆",
            "三连击: 表情/动作/环境, 一秒三闪, 情绪爆破点",
            "王家卫式: 三镜表情/动作/环境, 让'情绪的爆破'可见",
            "吴宇森式: 慢镜 + 三连击 + 慢放, 让'瞬间的暴力'成为'诗意'",
            "诺兰式: 三镜意识流, 让'想法'比'动作'更快",
            "0.3-0.3-0.3-1.0s 三闪+收束, 王家卫《旺角卡门》开场式",
            "三镜=开始/动作/反应, 让'1秒' = '整场戏的精华'",
            "三闪 = '看到' '做' '结果', 1 秒 = 完整叙事",
        ],
        "抖音超快": [
            "0.5-1s 快剪, 视觉密度爆炸, 抖音爆款 MCN 式",
            "快切 + 跳切, 让观众的眼睛跟不上节奏, 但停不下来",
            "0.5s 钩子 + 1s 推进 + 1s 收束, 抖音爆款 3 秒法则",
            "快剪 + 节拍同步, 让音乐+画面=沉浸",
            "信息密度爆炸, 让观众'刷'完才意识到'刚看了什么'",
            "5s 钩子 + 10s 推进 + 5s 收束, 让'短视频'也是'完整故事'",
            "0.5s × 20 镜 = 10s, 让'信息'成为'节奏'",
        ],
        "子弹时间": [
            "0.5s 360° 静止环绕, 让'时间'在'瞬间'里溶解",
            "沃卓斯基姐妹式: 时间凝固, 观众看到平时看不到的角度",
            "0.5s × 4 环绕 + 1s 收束 = 2.5s, 《黑客帝国》开场式",
            "子弹穿过镜头的瞬间 = 5 镜 360° 静止, 让'时间'可被'看'",
            "陈可辛/迈克尔·贝式: 静止 = '看见'平时看不到的细节",
        ],
        "慢镜高光": [
            "慢镜 1/8, 让'瞬间'变成'永恒', 王家卫/诺兰式",
            "1/8 速度: 16s 实际拍摄 = 2s 镜头时长, 慢放到极致",
            "王家卫《重庆森林》: 慢镜 + 重复, 让'时间'成为'诗'",
            "诺兰《盗梦空间》: 1/8 慢镜 + 静止时间, 让'梦' = '现实'",
            "慢镜 1/8 + 1s 切回正常, 让'对比'成为'冲击'",
        ],
        "极慢抒情": [
            "1.5s 实际 = 30s 慢放, 1/20 速度, 马力克/塔可夫斯基式",
            "让时间'溶解', 观众住在'永恒'里",
            "1/20 速度: 水滴/光斑/树叶飘动, 1.5s = 真实 30s",
            "塔可夫斯基《乡愁》: 慢镜 + 水/火, 让'时间'成为'宗教'",
            "马力克《天堂之日》: 慢镜 + 旁白 + 自然, 让'时间'成为'神'",
        ],
        "车戏分镜": [
            "跟拍 + 跟焦 + 广角, 速度感/危险感, 迈克尔·曼式",
            "《盗火线》开场: 跟拍 + 仪表盘 + 后视镜, 3 镜组合 = 速度感",
            "车内 POV + 车外跟拍, 4 镜组合 = 危险感",
            "音速 + 引擎 + 漂移, 让'速度'成为'主角'",
        ],
        "枪战分镜": [
            "0.5-2s 手持快切, 吴宇森/迈克尔·曼式紧张",
            "《英雄本色》: 慢镜 + 白鸽 + 枪响, 让'暴力' = '诗意'",
            "手持 + 跳切 + 弹壳特写, 5 镜组合 = 暴烈",
            "扳机/枪口/中弹/倒地, 1s 内 4 镜 = 真实",
        ],
        "default": [
            f"{pacing_style}·{tpl.get('pacing_intent', '')}",
        ],
    }
    director_pool = director_notes_by_pacing.get(pacing_style, director_notes_by_pacing["default"])
    dn_idx = int(_hl.md5((seed + "_dn").encode()).hexdigest(), 16) % len(director_pool)
    director_note = director_pool[dn_idx]

    # actor_note
    actor_pool = [
        "保持呼吸自然, 不抢情绪, 让'日常'成为'重量'",
        "眼睛不看镜头, 不看对手, 看'不在场的人'",
        "手可以微动, 但身体不动, 让'静'承担一切",
        "呼吸先沉一下, 让观众'听到'角色在想什么",
        "眼神从对手移开, 看一个不在场的位置, 让'拒绝'成为姿态",
        "眼眶湿, 但不要落泪, 让观众'以为'在落泪",
        "嘴角微动, 不说话, 沉默=台词",
        "屏住呼吸 3 秒, 然后慢慢呼出, 不抢节奏",
    ]
    an_idx = int(_hl.md5((seed + "_an").encode()).hexdigest(), 16) % len(actor_pool)
    actor_note = actor_pool[an_idx]

    # visual_design
    primary_obj = obj_str.split("、")[0] if obj_str else "关键道具"
    visual_design = f"光:{light_progression.get(tension, '漫射光')} | 色:{color_progression.get(tension, '中性色调')} | 材质:{material_progression.get(tension, '日常材质')} | 焦点:{primary_obj} | 构图:{tpl.get('size', '中景')}{tpl.get('focal', '50mm')}"

    # sound_design (4 层)
    sidx = int(_hl.md5((seed + "_sd").encode()).hexdigest(), 16)
    ambient_pct = 30 + (sidx % 30)
    foley_pct = 10 + (sidx // 10 % 20)
    music_pct = (sidx // 100 % 20)
    silence_pct = max(0, 100 - ambient_pct - foley_pct - music_pct)
    sound_design = f"环境{ambient_pct}% + 拟音{foley_pct}% + 音乐{music_pct}% + 留白{silence_pct}%"

    # edit_intent
    edit_pool = [
        "承接上一镜, 用身体细节延展情绪, 不抢节奏",
        "用具体物件 (凤梨罐头) 替代台词, 让'沉默'成为'台词'",
        "用反射/剪影让'想'成为'看', 不直接演'想'",
        "在动作前留 0.5s 静默, 让'即将'成为'正在'",
        "切到物件特写, 让'看到'成为'感受'",
        "切到空镜, 让'人不在'成为'人在想'",
        "用微表情替代对白, 让'嘴不动'成为'心在动'",
    ]
    ei_idx = int(_hl.md5((seed + "_ei").encode()).hexdigest(), 16) % len(edit_pool)
    edit_intent = edit_pool[ei_idx]

    # V14.3 D1: 镜头语法模式签名变体 (景别覆盖偏好 + 运镜/焦段/角度同档变体)
    _raw_size = tpl.get("size", "中景") if isinstance(tpl.get("size"), str) else tpl["size"][idx % len(tpl["size"])]
    _out_size = _size_coverage_shift(_raw_size, shot_n, pacing_style, mode_seed, idx)
    _out_move = _grammar_variant(tpl.get("move", "固定"), "move", shot_n, pacing_style, mode_seed)
    _out_focal = _grammar_variant(tpl.get("focal", "50mm"), "focal", shot_n, pacing_style, mode_seed)
    _out_angle = _grammar_variant(tpl.get("angle", "平视"), "angle", shot_n, pacing_style, mode_seed)

    return {
        "n": shot_n,
        "scene": scene_num,
        "act": act,
        "size": _out_size,
        "angle": _out_angle,
        "move": _out_move,
        "focal": _out_focal,
        "dur": f"{tpl.get('dur', 5.0)}s",
        "dur_sec": tpl.get("dur", 5.0),
        "focus": focus,
        "sound": sound,
        "sound_design": sound_design,  # V12.6 v10
        "cut": tpl.get("cut", "硬切"),
        "purpose": tpl.get("pacing_intent", f"推进{scene.get('story_function', '剧情')}"),
        "note": f"{pacing_style}·{tpl.get('pacing_intent', '')}",
        "director_note": director_note,  # V12.6 v10
        "actor_note": actor_note,  # V12.6 v10
        "visual_design": visual_design,  # V12.6 v10
        "edit_intent": edit_intent,  # V12.6 v10
        "stage": stage,
        "stage_name": stage,
        "stage_emotion": stage_emotion,
        "stage_color": color_progression.get(tension, "中性色调"),
        "stage_light": light_progression.get(tension, "漫射光(阴天)"),
        "stage_material": material_progression.get(tension, "日常材质"),
        "stage_atmosphere": atmosphere_progression.get(tension, "日常/从容"),
        "stage_rhythm": pacing_style,
        "story_function": scene.get("story_function", "推进"),
        "tension_level": tension,
        "location": location,
        "weather": scene.get("weather", ""),
        "time": scene.get("time", ""),
        "ie": scene.get("ie", "内"),
        "obj_carrying": scene.get("obj_carrying", ""),
        "subtext": scene.get("subtext", ""),
        "phase": phase,
        "pacing_style": pacing_style,
    }


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    import sys
    print("="*60)
    print("Pacing Engine 自检")
    print("="*60)
    print(f"\n节奏风格数: {len(PACING_STYLES)}")
    for name, info in PACING_STYLES.items():
        print(f"  {name} ({info['category']}): {info['description'][:50]}...")
        print(f"    大师: {info['masters'][:2]}")
        print(f"    序列镜数: {len(info['shot_sequence'])}")
        durs = [s.get('dur', 0) for s in info['shot_sequence']]
        print(f"    时长范围: {min(durs)}s - {max(durs)}s")
    print(f"\n35 场戏节奏分布 (按 story_function 动态生成):")
    for sf, pacing in list(STORY_FUNC_PACING.items())[:35]:
        print(f"  {sf}: {pacing}")
