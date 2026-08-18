# -*- coding: utf-8 -*-
"""
Phase 17 - DirectorIntentPro v2 (灵魂注入版)
================================================
世界顶级导演的意图设计 - 完整接入 DirectorSoulNode 灵魂注入

5 大维度:
1. 感受意图 - 观众看完应感到什么
2. 情感意图 - 角色此刻应有何情感
3. 关系意图 - 角色间关系如何
4. 主题意图 - 本场承载主题的哪一面
5. 留白意图 - 什么不该说, 让观众自己懂

核心设计哲学:
- **不写情绪, 写可观察行为** (PTA)
- **让沉默比台词更有力** (库斯杜力卡)
- **用空间叙事** (诺兰)
- **用物件代替心理** (王家卫)
- **不写画面里有什么, 写导演会怎样描述自己的意图** (附件核心)

整合 5 要素:
1. 数据层: 1161 部 + 63 导演 + 191 反 AI + 12 套 + 14 真实短剧 + 48 情感 + 7 融合 + 60 灵魂情感
2. 上下文缩略层: 灵魂 + 类型 + 主题 + 场景
3. Skill/Harness 层: 灵魂融合公式 + 5 维意图生成
4. 经验矩阵层: 真实电影案例 (8 顶级导演 + 15 真实意图样本)
5. AI 深度处理: 反 AI + 10 铁律 + 灵魂深度处理

11 维导演控制:
空镜 / 留白 / 氛围渲染 / 悬疑 / 多线 / 反转 / 高潮 / 余韵 / 推进节奏 / 感情控制 / 角色塑造

3 留白 + 3 运镜:
3 留白: 物件留白 / 时间留白 / 沉默留白
3 运镜: 推近 / 后拉 / 横移

8 大顶级导演灵魂签名:
王家卫 / 诺兰 / PTA / 奉俊昊 / 黑泽明 / 库斯杜力卡 / 塔可夫斯基 / 约阿希姆·提尔

15 导演真实意图样本 (DIRECTOR_INTENT_SAMPLES):
深度应用, 每次根据灵魂动态调整

H3 三大字段 (供下游节点对接):
integrated_multimodal_description + overall_soundscape + non_diegetic_music
"""

import os
import sys
import json
import random
import math

# ============================================================
# 安全字符串工具
# ============================================================
def _str(value, default=""):
    """安全字符串转换, 处理 None / 非字符串 / 字节"""
    if value is None:
        return default
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return value.decode("utf-8", errors="replace")
    return str(value)


# ============================================================
# 模块依赖 (优雅降级)
# ============================================================
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    from production_pipeline_v3 import DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SILENCE_MASTERY_5, SPATIAL_CONSISTENCY_5
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)
    DIRECTOR_INTENT_5D = {}
    ART_DIRECTION_4D = {}
    SILENCE_MASTERY_5 = {}
    SPATIAL_CONSISTENCY_5 = {}

try:
    from director_soul import (
        EMOTION_MATRIX_60, EMOTION_FUSION_7, SOUL_DIMENSIONS_10,
        fuse_emotions, build_soul_injection, compute_soul_state,
    )
    _HAS_SOUL = True
except Exception as _soul_err:
    _HAS_SOUL = False
    _SOUL_ERROR = str(_soul_err)
    EMOTION_MATRIX_60 = {}
    EMOTION_FUSION_7 = {}
    SOUL_DIMENSIONS_10 = {}


# ============================================================
# 8 大顶级导演灵魂签名 (核心 - 不只是标签, 是直接驱动生成)
# ============================================================
DIRECTOR_SOUL_SIGNATURES_8 = {
    "王家卫": {
        "name_en": "Wong Kar-wai",
        "signature": "用物件代替心理, 时间戳, 60s 慢节奏, 60% 留白, 时间即情敌",
        "higher_archetype": "记忆与错失 - 时间是敌人, 距离是爱",
        "visual_grammar": "手摇摄影 + 抽帧 + 慢门 + 60s 慢镜头, 浅景深, 偏色 (青绿/红/金)",
        "time_logic": "非线性, 闪前, 时间戳锚定 ('2024 年 4 月 16 日下午 3 点 03 分')",
        "object_metaphor": "凤梨罐头 / 船票 / 手表 / 雨伞 / 高跟鞋 / 路灯 / 电话亭",
        "silence_form": "短句 + 大段沉默, 一句话能撑起 30 秒, 沉默即台词",
        "horizon": "都市边缘, 走廊, 楼梯间, 出租车后座, 霓虹与雾",
        "inner_speech": "第一人称独白, 时间即主角, 等待即情感",
    },
    "诺兰": {
        "name_en": "Christopher Nolan",
        "signature": "时间结构即主题, 史诗感, IMAX 客观镜头, 物理空间极致精确",
        "higher_archetype": "认知与时间 - 真实与感知的边界, 记忆的不可靠",
        "visual_grammar": "IMAX 70mm + 24p + 长焦压缩 + 极少切镜, 对称 + 透视消失点",
        "time_logic": "非线性, 双线/三线交叉, 物理可解释的时间机制",
        "object_metaphor": "陀螺 / 怀表 / 信件 / 火车 / 建筑平面图 / 磁带",
        "silence_form": "物理空间沉默, 留白即张力, 一秒能撑起一分钟",
        "horizon": "城市天际线, 雪山, 海, 失重空间, 建筑内部走廊",
        "inner_speech": "无内心独白, 用建筑和动作说心理",
    },
    "PTA": {
        "name_en": "Paul Thomas Anderson",
        "signature": "用可观察行为代替情绪, 70s 迷幻, 慢推长焦, 权力即主题",
        "higher_archetype": "权力与家庭 - 父权崩塌 / 资本吞噬 / 控制与被控制",
        "visual_grammar": "慢推长焦 (Cooke S4) + 70s 暖黄 + 浅景深 + 凝视镜头",
        "time_logic": "线性 + 70s 风格, 偶尔章节卡 (1, 2, 3, 4...)",
        "object_metaphor": "石油 / 牛奶 / 水 / 钻头 / 录音带 / 黑胶 / 钢琴",
        "silence_form": "凝视沉默, 一个眼神 5 秒, 沉默即权力宣判",
        "horizon": "70s 洛杉矶, 油田, 录音棚, 山区别墅, 教堂",
        "inner_speech": "不写内心, 写可观察行为 (手的位置, 呼吸的节奏)",
    },
    "奉俊昊": {
        "name_en": "Bong Joon-ho",
        "signature": "用空间做阶层隐喻, 类型当特洛伊木马, 同场多情绪, 楼梯即命运",
        "higher_archetype": "阶层与气味 - 上下楼梯, 贫富, 不可逾越的边界",
        "visual_grammar": "固定镜头 + 纵深调度 + 类型片语法 (悬疑/惊悚) + 雨夜",
        "time_logic": "线性, 但有大量'回旋' (回到前一场, 换视角重看)",
        "object_metaphor": "楼梯 / 石头 / 桃子 / 雨水 / 廉价香水 / 穷人的衣服 / 假证书",
        "silence_form": "雨声沉默, 一场雨撑起 10 分钟, 沉默即不平等",
        "horizon": "首尔半山别墅, 地下防空洞, 楼梯间, 雨天街道",
        "inner_speech": "无内心独白, 用阶层气味 (CK 香水 / 廉价洗衣粉) 暗示",
    },
    "黑泽明": {
        "name_en": "Akira Kurosawa",
        "signature": "天气即角色, 极致清晰, 群戏调度, 道德困境无答案",
        "higher_archetype": "道德与自然 - 雨雪风雷, 人在天地间的渺小",
        "visual_grammar": "三镜头法 + 多机位群戏 + 自然光 + 极致清晰 + 仰俯调度",
        "time_logic": "线性 + 偶尔闪回 (罗生门式), 道德事件驱动",
        "object_metaphor": "雨 / 雪 / 雾 / 风 / 剑 / 扇子 / 镜子 / 鸟",
        "silence_form": "天气沉默, 一阵风能撑起一分钟, 沉默即道德审判",
        "horizon": "战国, 雨, 泥路, 寺庙, 雨中的城堡, 雪山",
        "inner_speech": "极少独白, 用动作和天气说话",
    },
    "库斯杜力卡": {
        "name_en": "Emir Kusturica",
        "signature": "少说话, 沉默即情感, 塞尔维亚乡愁, 疯癫与诗",
        "higher_archetype": "乡愁与狂欢 - 吉普赛式狂欢, 失序中的诗意",
        "visual_grammar": "手持 + 远景 + 群戏调度 + 巴洛克调度 (满画面 + 多焦平面)",
        "time_logic": "非线性 + 现实/梦境/回忆混用, 跳接",
        "object_metaphor": "动物 (鸡/马/猪) / 婚礼 / 葬礼 / 酒 / 音乐 / 河",
        "silence_form": "动物沉默, 一只鸡走过能撑起 30 秒, 沉默即乡愁",
        "horizon": "塞尔维亚村庄, 河边, 麦田, 婚礼, 葬礼",
        "inner_speech": "极简对白, 大段沉默, 让动物和音乐说话",
    },
    "塔可夫斯基": {
        "name_en": "Andrei Tarkovsky",
        "signature": "时间即主角, 长镜头, 诗意朦胧, 物质即记忆",
        "higher_archetype": "时间与记忆 - 物质是记忆的容器, 火/水/风是时间的形态",
        "visual_grammar": "长镜头 (1-7 分钟) + 自然光 + 慢推 + 诗意朦胧 + 黑白/彩色切换",
        "time_logic": "非线性, 时间折叠, 梦境/现实/记忆三位一体",
        "object_metaphor": "水 / 火 / 风 / 蜡烛 / 旧照片 / 镜中映像 / 童年房间",
        "silence_form": "长沉默, 物质沉默 (一滴水能撑 2 分钟), 沉默即时间的重量",
        "horizon": "俄罗斯乡村, 沼泽, 旧屋, 火, 雨, 童年",
        "inner_speech": "诗化旁白, 哲学性独白, 时间即主角",
    },
    "约阿希姆·提尔": {
        "name_en": "Joachim Trier",
        "signature": "从房子视角叙事, 家庭代际, 北欧光, 安静中藏风暴",
        "higher_archetype": "代际与房间 - 房子是角色, 代际是命运, 沉默是爱",
        "visual_grammar": "长焦 + 自然光 + 60% 留白 + 中远景 + 安静构图",
        "time_logic": "线性 + 偶尔章节卡 + 极慢推进",
        "object_metaphor": "房子 / 窗户 / 镜子 / 钢琴 / 旧书 / 父亲的椅子",
        "silence_form": "房间沉默, 一间空房能撑 2 分钟, 沉默即代际",
        "horizon": "奥斯陆公寓, 夏日别墅, 街角咖啡馆, 山路",
        "inner_speech": "极少独白, 用房子和房间说话",
    },
}


# ============================================================
# 15 导演真实意图样本 (深度应用)
# ============================================================
DIRECTOR_INTENT_SAMPLES = {
    "塔可夫斯基": "我希望在每一秒里, 感受到时间本身的重量。",
    "王家卫": "我希望观众看完这场戏, 不知道他们是不是爱上了。",
    "诺兰": "我希望通过这个时间结构, 让观众在结尾感到时间才是真正的主角。",
    "侯孝贤": "我希望通过沉默, 让观众听见风听见海听见这个人的心。",
    "是枝裕和": "我希望这场吃饭戏, 让观众感到这就是家。",
    "黑泽明": "我希望这场雨, 让观众感到大自然也是角色。",
    "伯格曼": "我希望观众在主角的脸上, 看到他自己。",
    "小津": "我希望通过低位静态镜头, 让观众感到时间是循环的。",
    "蔡明亮": "我希望通过 5 分钟不动, 让观众感到自己也在场。",
    "李沧东": "我希望观众在结尾感到道德困境没有答案。",
    "库布里克": "我希望通过对称构图, 让观众感到失衡。",
    "毕赣": "我希望通过时间折叠, 让观众分不清现在和过去。",
    "贾樟柯": "我希望通过流行歌, 让观众感到时代。",
    "奉俊昊": "我希望通过楼梯空间, 让观众感到阶层。",
    "李安": "我希望通过饭桌戏, 让观众感到文化冲突。",
    "PTA": "我希望通过沉默, 让观众感到权力正在转移。",
    "库斯杜力卡": "我希望通过动物, 让观众感到这是故乡。",
    "约阿希姆·提尔": "我希望通过一扇窗, 让观众感到整个家庭的命运。",
}


# ============================================================
# 11 维导演控制 (结合灵魂动态)
# ============================================================
DIRECTOR_CONTROL_11 = {
    "1_空镜 (Empty Shot)": "无台词 / 无人物 / 只有空间或物件, 让空间成为叙事",
    "2_留白 (Negative Space)": "声音/画面/对白中的'无', 用缺席表达在场",
    "3_氛围渲染 (Atmosphere)": "光线/色彩/质感/声音共同营造的情绪场",
    "4_悬疑 (Suspense)": "信息差 + 时间差 + 空间差造成的紧张",
    "5_多线 (Multi-thread)": "并行/交叉/回旋的多重叙事线",
    "6_反转 (Reversal)": "认知/期待/道德/时间的突然翻转",
    "7_高潮 (Climax)": "积累的爆点, 一场戏能改变所有关系",
    "8_余韵 (Aftertaste)": "结尾后, 观众还在咀嚼的东西",
    "9_推进节奏 (Pacing)": "快/慢/停顿的节奏设计, 时间即语言",
    "10_感情控制 (Emotion Control)": "压抑/释放/反讽/共鸣的感情曲线",
    "11_角色塑造 (Character Building)": "通过可观察行为建立角色, 不写内心",
}


# ============================================================
# 3 留白类型
# ============================================================
SILENCE_TYPES_3 = {
    "1_物件留白 (Object Silence)": "用一个物件代替一段心理, 让物件说话, 心理沉默",
    "2_时间留白 (Time Silence)": "用一个停顿代替一段对白, 让时间流逝, 关系变化",
    "3_沉默留白 (Voice Silence)": "用一段安静代替一段台词, 让观众听见呼吸",
}


# ============================================================
# 3 运镜核心
# ============================================================
CAMERA_MOTION_3 = {
    "1_推近 (Push In)": "摄影机向角色推进, 揭示内心, 强调关系, 凝聚张力",
    "2_后拉 (Pull Out)": "摄影机远离角色, 揭示空间, 抽离情感, 拉远距离",
    "3_横移 (Track/Pan)": "摄影机平行于角色, 平行观察, 时间流逝, 关系不变",
}


# ============================================================
# 权力动态词典 (用于关系意图)
# ============================================================
POWER_DYNAMICS = {
    "PTAPower": {
        "type": "压迫-反抗",
        "physical_distance": "近 (1 米内)",
        "eye_contact": "压迫方长凝视, 反抗方躲避",
        "scene_archetype": "质问 / 审讯 / 餐桌冲突 / 商业谈判",
    },
    "WKWMemory": {
        "type": "靠近-错过",
        "physical_distance": "中 (2-5 米)",
        "eye_contact": "想看却不敢, 错过是常态",
        "scene_archetype": "重逢 / 离别 / 错过的走廊 / 电话亭",
    },
    "NolanTime": {
        "type": "追逐-错过",
        "physical_distance": "远 (5+ 米)",
        "eye_contact": "想接近, 物理上被阻止",
        "scene_archetype": "追逐 / 失重 / 时间错位 / 倒带",
    },
    "BongClass": {
        "type": "上下-不可逾越",
        "physical_distance": "楼梯纵向 (高/低差)",
        "eye_contact": "向下俯视或向上仰望",
        "scene_archetype": "楼梯 / 门 / 电梯 / 暴雨倒流",
    },
    "KurosawaWeather": {
        "type": "渺小-命运",
        "physical_distance": "远景 (群像)",
        "eye_contact": "面对自然, 道德抉择时",
        "scene_archetype": "雨 / 雪 / 战 / 道德审判",
    },
    "KusturicaChaos": {
        "type": "狂欢-失序",
        "physical_distance": "群像 (10+ 人)",
        "eye_contact": "混乱中的偶然相视",
        "scene_archetype": "婚礼 / 葬礼 / 酒醉 / 动物闯入",
    },
    "TarkovskyMaterial": {
        "type": "在场-缺席",
        "physical_distance": "中 (3 米)",
        "eye_contact": "看着不在场的人/物/记忆",
        "scene_archetype": "旧屋 / 镜子 / 童年房间 / 火/水/风",
    },
    "TrierRoom": {
        "type": "代际-传承",
        "physical_distance": "同屋 (2-3 米)",
        "eye_contact": "回避, 偶尔对视即爆点",
        "scene_archetype": "饭桌 / 客厅 / 卧室 / 父子独处",
    },
}


# ============================================================
# 感受意图词典 (由灵魂 polarity 决定)
# ============================================================
FEELING_TONE_BY_POLARITY = {
    "positive": {
        "headline": "让观众感到被温暖/治愈/释然/被看见",
        "wrong_to_avoid": "廉价煽情, 强行 happy ending, 滥用特写哭戏",
        "right_target": "用一个具体细节让观众自己感到 (凤梨罐头的保质期, 一封未寄出的信)",
        "delivery_principle": "用克制表达温暖, 让观众自己感到暖, 不是告诉他们暖",
    },
    "negative": {
        "headline": "让观众感到心酸/沉重/刺痛/被剥离",
        "wrong_to_avoid": "强行眼泪, 撕心裂肺, 瞳孔地震, 撕心裂肺的喊叫",
        "right_target": "用一个未说出口的细节让观众感到 (筷子的停顿, 窗外越下越大的雨, 一根未点燃的烟)",
        "delivery_principle": "压抑比爆发更重, 让沉默比台词更有力",
    },
    "mixed (矛盾情感)": {
        "headline": "让观众感到矛盾/复杂/难以言说/苦乐参半",
        "wrong_to_avoid": "强行解读, 二元化, 给答案, happy ending 或 sad ending",
        "right_target": "用同时存在的两种情绪让观众感到复杂 (微笑时眼角有泪, 笑声变轻, 一句'再见'既是告别也是开始)",
        "delivery_principle": "让观众说不清感受, 但久久不忘",
    },
    "neutral": {
        "headline": "让观众感到被见证/陪伴/安静/在场",
        "wrong_to_avoid": "强行催泪, 强行笑, 强行戏剧化",
        "right_target": "用一个普通的瞬间让观众感到永恒 (吃一碗面, 看一场雨, 走过一条路)",
        "delivery_principle": "日常即永恒, 平凡即深刻, 见证即情感",
    },
}


# ============================================================
# 留白意图词典 (由融合模式决定)
# ============================================================
SILENCE_BY_FUSION_MODE = {
    "F1_单情感主导": {
        "form": "单一沉默",
        "principle": "一种情感, 一种沉默, 一种呼吸",
        "duration_principle": "沉默占场景 30-40%, 单一情绪 5-8 秒停顿",
        "micro_event": "一个动作 (放下筷子, 看向窗外) 撑起 3-5 秒",
    },
    "F2_双情感主次融合": {
        "form": "表里沉默",
        "principle": "表面沉默 + 内心翻涌, 主 70% 表 + 次 30% 里",
        "duration_principle": "表沉默 2 秒, 里沉默 5 秒, 一句话一停顿",
        "micro_event": "嘴上平静 (acceptance 70%) + 手指在桌子下颤抖 (remorse 30%)",
    },
    "F3_双情感对等融合": {
        "form": "矛盾沉默",
        "principle": "两种情感对峙, 50/50, 一句话的轻重变化",
        "duration_principle": "对话节奏变慢, 每句前 3-5 秒, 一句'再见'撑 10 秒",
        "micro_event": "想拥抱却没拥抱, 想离开却没离开, 微笑时眼角有泪",
    },
    "F4_三情感递进融合": {
        "form": "时间沉默",
        "principle": "情感随时间变化, 沉默也随时间变化",
        "duration_principle": "开头 2 秒, 中段 5 秒, 结尾 10 秒, 时间越长沉默越重",
        "micro_event": "开头: 主动说话 → 中段: 偶尔说话 → 结尾: 沉默到底",
    },
    "F5_矛盾情感爆炸": {
        "form": "极端沉默",
        "principle": "两种极端矛盾同时达到峰值, 沉默即爆炸前夜",
        "duration_principle": "极长沉默 (30 秒+), 然后一句话/一个动作爆裂, 然后再次沉默",
        "micro_event": "一个动作 (摔门, 摔杯, 拥抱) 撑起 30 秒, 然后瞬间无声",
    },
    "F6_复合情绪三角": {
        "form": "多层沉默",
        "principle": "三种情感同时存在, 沉默是多种情感的叠加",
        "duration_principle": "沉默中混杂三个层次的呼吸, 难以分辨是哪个情感在说话",
        "micro_event": "三件事同时发生 (看表, 叹气, 抚旧物), 每件撑 5 秒, 叠加成 15 秒",
    },
    "F7_情感转化": {
        "form": "转化沉默 (最大留白)",
        "principle": "情感在场景内发生根本性转化, 沉默即转化的瞬间",
        "duration_principle": "沉默占场景 60-80%, 极长的空镜, 极长的凝视",
        "micro_event": "一个转身撑起 30 秒, 一个远去的背影撑 1 分钟, 镜头在空房间里停 1 分钟",
    },
}


# ============================================================
# 主题意图词典 (由 higher_archetype 决定)
# ============================================================
THEME_BY_ARCHETYPE = {
    "memory": "时间与错失 - 我们在时间中错过的, 比得到的更多",
    "time": "时间的结构 - 时间不是线性的, 是认知的",
    "power": "权力与崩塌 - 父权/资本/控制的崩塌瞬间",
    "class": "阶层与气味 - 不可逾越的边界, 上下楼梯, 贫富差距",
    "weather": "道德与自然 - 人在天地间的渺小, 道德困境无答案",
    "chaos": "乡愁与狂欢 - 失序中的诗意, 塞尔维亚的乡愁",
    "material": "时间与记忆 - 物质是记忆的容器, 火/水/风是时间的形态",
    "generation": "代际与传承 - 房子是角色, 代际是命运",
}


# ============================================================
# 动态生成函数 - 5 维意图
# ============================================================
def _build_feeling_intent(soul_fused, scene, char_a, char_b, director):
    """动态生成感受意图 (由 soul polarity 决定基调)"""
    polarity = soul_fused.get("polarity", "neutral")
    tone = FEELING_TONE_BY_POLARITY.get(polarity, FEELING_TONE_BY_POLARITY["neutral"])
    intensity = soul_fused.get("intensity", 0.5)
    arousal = soul_fused.get("arousal", "medium")
    visual_signs = soul_fused.get("visual_signs", "")
    color_palette = soul_fused.get("color_palette", "")

    # 动态选取具体的"对"与"错" (基于强度)
    if intensity > 0.8:
        intensity_label = "极致的"
        wrong_specific = "用力过猛, 让观众在情感上'被按头'"
    elif intensity > 0.5:
        intensity_label = "明确的"
        wrong_specific = "贴标签式煽情, 用'感人''催泪'形容"
    else:
        intensity_label = "淡淡的"
        wrong_specific = "用力过猛, 让观众在情绪上'被按头'"

    arousal_note = ""
    if arousal == "high":
        arousal_note = "高唤醒度下, 让观众的心跳与角色同频"
    elif arousal == "low":
        arousal_note = "低唤醒度下, 让观众的心率慢慢降下来"
    else:
        arousal_note = "中唤醒度下, 让观众的情绪慢慢浮上来"

    director_sig = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("signature", "导演灵魂")

    # 动态的具体细节
    specific_detail_choices = [
        "凤梨罐头的过期日",
        "一根未点燃的烟",
        "窗外越下越大的雨",
        "一张未寄出的信",
        "桌上的半杯凉茶",
        "门口那双穿旧了的鞋",
        "时钟走过的 30 秒",
        "碗里剩下的半口饭",
        "镜子里多出的皱纹",
        "一个未完成的拥抱",
    ]
    if visual_signs:
        # 从 visual_signs 提取关键物件
        specific_detail = visual_signs[:50] if visual_signs else specific_detail_choices[0]
    else:
        specific_detail = specific_detail_choices[0]

    # 头行动态生成
    headline = tone["headline"]
    wrong = tone["wrong_to_avoid"]
    right = tone["right_target"]
    delivery = tone["delivery_principle"]

    out = """【1. 感受意图 - 观众应感到】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基调: {intensity_label}{headline}

不是让观众「知道」这个感受, 而是让观众「感到」这个感受。
唤醒度: {arousal} → {arousal_note}

应该做到:
  ✓ {right}
  ✓ 用一个具体细节 (例如 {specific_detail}) 代替"感人"二字
  ✓ {delivery}

导演灵魂: {director_sig}

这一场的视觉锚点 (来自灵魂融合):
  色彩: {color_palette}
  视觉: {visual_signs_short}

具体节奏建议:
  - 整场戏的节奏/音效/表演都为这个感受服务
  - 不是用 BGM 强行催, 而是用沉默的重量
  - 不是用特写强行按, 而是用一个动作的停留
  - 让观众在看完后 5 分钟 / 5 小时 / 5 天还在想
""".format(
        intensity_label=intensity_label,
        headline=headline,
        arousal=arousal,
        arousal_note=arousal_note,
        wrong=wrong,
        wrong_specific=wrong_specific,
        right=right,
        specific_detail=specific_detail,
        delivery=delivery,
        director_sig=director_sig,
        color_palette=color_palette[:120] if color_palette else "未指定",
        visual_signs_short=visual_signs[:120] if visual_signs else "未指定",
    )
    return out


def _build_emotion_intent(soul_fused, char_a, char_b, director):
    """动态生成情感意图 (由 visual_signs/voice_signs/facial_au 决定)"""
    visual_signs = soul_fused.get("visual_signs", "")
    voice_signs = soul_fused.get("voice_signs", "")
    facial_au = soul_fused.get("facial_au", "")
    inner_monologue = soul_fused.get("inner_monologue", "")
    intensity = soul_fused.get("intensity", 0.5)
    emotion_name = soul_fused.get("name", "未指定")

    # 动态生成角色身体语言 (避免模板, 拼接灵魂字段)
    body_part_a = "手"
    body_part_b = "眼"
    if "肩膀" in visual_signs:
        body_part_a = "肩膀"
    elif "嘴" in visual_signs:
        body_part_a = "嘴"
    elif "手" in visual_signs:
        body_part_a = "手"
    if "视线" in visual_signs:
        body_part_b = "视线"
    elif "眼睛" in visual_signs:
        body_part_b = "眼睛"
    elif "眼" in visual_signs:
        body_part_b = "眼"

    # 动态生成微动作 (根据强度 + 唤醒度)
    if intensity > 0.7:
        micro_action_a = "微微颤抖 / 收紧 / 握拳"
        micro_action_b = "眼眶湿润 / 瞳孔放大 / 嘴角下撇"
    elif intensity > 0.4:
        micro_action_a = "微停 / 停顿 / 手指轻敲"
        micro_action_b = "眉毛微抬 / 视线下移 / 嘴角微动"
    else:
        micro_action_a = "自然垂下 / 不动 / 呼吸平稳"
        micro_action_b = "眼睛温和 / 嘴角自然 / 呼吸平缓"

    # 动态生成微表情
    micro_expression_b = facial_au[:80] if facial_au else "眉毛微动 (AU1+AU2)"

    # 内部独白
    inner_a = inner_monologue[:100] if inner_monologue else "这一刻, 我选择不说"
    inner_b = inner_monologue[:100] if inner_monologue else "如果他/她知道就好了"

    # 导演视角 (higher_archetype 决定内/外的选择)
    archetype = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("higher_archetype", "")
    if "PTA" in director or "PTA" in str(archetype) or "权力" in archetype:
        director_view = "PTA 视角: 不写情绪, 写可观察行为 (手的位置, 呼吸的节奏, 视线的方向)"
    elif "王家卫" in director or "记忆" in archetype:
        director_view = "王家卫视角: 用物件代替心理, 时间戳代替情绪标签"
    elif "诺兰" in director or "时间" in archetype:
        director_view = "诺兰视角: 用物理空间代替心理, 用建筑结构说话"
    elif "塔可夫斯基" in director or "记忆" in archetype or "物质" in archetype:
        director_view = "塔可夫斯基视角: 物质即记忆, 一滴水能撑 2 分钟, 让物质说话"
    else:
        director_view = "导演视角: 不写内心独白, 写观众能'看见'的东西"

    out = """【2. 情感意图 - 角色应有】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

主导情感: {emotion_name} (强度 {intensity:.2f})

{char_a} 应该感受到什么:
  - 身体: {body_part_a}会{micro_action_a}
  - 眼睛: {body_part_b}会{micro_expression_b}
  - 内心: {inner_a}
  - 嘴上: 什么都不说 (让观众通过具体细节读懂)

{char_b} 应该感受到什么:
  - 身体: {body_part_b}会{micro_action_b}
  - 眼神: {body_part_b}会{micro_expression_b}
  - 内心: {inner_b}
  - 嘴上: 什么都不说 (让观众通过具体细节读懂)

灵魂融合层的情感特征:
  - 视觉: {visual_signs_short}
  - 声音: {voice_signs_short}
  - 面部肌肉: {facial_au_short}
  - 内心独白: {inner_short}

{director_view}

应该做到:
  ✓ 用可观察行为代替情绪 (PTA 原则)
  ✓ 用物件代替心理 (王家卫原则)
  ✓ 用沉默代替台词 (库斯杜力卡原则)
  ✓ 整场戏的表演都服务于一个微动作
""".format(
        emotion_name=emotion_name,
        intensity=intensity,
        char_a=char_a or "角色 A",
        char_b=char_b or "角色 B",
        body_part_a=body_part_a,
        micro_action_a=micro_action_a,
        micro_action_b=micro_action_b,
        body_part_b=body_part_b,
        micro_expression_b=micro_expression_b,
        inner_a=inner_a,
        inner_b=inner_b,
        visual_signs_short=visual_signs[:200] if visual_signs else "未指定",
        voice_signs_short=voice_signs[:150] if voice_signs else "未指定",
        facial_au_short=facial_au[:120] if facial_au else "未指定",
        inner_short=inner_monologue[:120] if inner_monologue else "未指定",
        director_view=director_view,
    )
    return out


def _build_relationship_intent(soul_fused, char_a, char_b, scene, director):
    """动态生成关系意图 (由 higher_archetype 决定权力动态)"""
    archetype = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("higher_archetype", "")
    # 根据 archetype 决定 power dynamic
    power = None
    for k, v in POWER_DYNAMICS.items():
        if any(keyword in archetype for keyword in ["记忆", "错失", "时间", "情敌", "WKW", "Memory"]):
            power = POWER_DYNAMICS["WKWMemory"]
            break
        elif any(keyword in archetype for keyword in ["权力", "家庭", "父权", "PTA", "Power"]):
            power = POWER_DYNAMICS["PTAPower"]
            break
        elif any(keyword in archetype for keyword in ["认知", "时间", "Nolan", "Time"]):
            power = POWER_DYNAMICS["NolanTime"]
            break
        elif any(keyword in archetype for keyword in ["阶层", "气味", "Bong", "Class"]):
            power = POWER_DYNAMICS["BongClass"]
            break
        elif any(keyword in archetype for keyword in ["道德", "自然", "Kurosawa", "Weather"]):
            power = POWER_DYNAMICS["KurosawaWeather"]
            break
        elif any(keyword in archetype for keyword in ["乡愁", "狂欢", "Kusturica", "Chaos"]):
            power = POWER_DYNAMICS["KusturicaChaos"]
            break
        elif any(keyword in archetype for keyword in ["物质", "记忆", "Tarkovsky", "Material"]):
            power = POWER_DYNAMICS["TarkovskyMaterial"]
            break
        elif any(keyword in archetype for keyword in ["代际", "传承", "Trier", "Room"]):
            power = POWER_DYNAMICS["TrierRoom"]
            break

    if power is None:
        # 默认 - 看导演名
        if "王家卫" in director:
            power = POWER_DYNAMICS["WKWMemory"]
        elif "诺兰" in director:
            power = POWER_DYNAMICS["NolanTime"]
        elif "PTA" in director:
            power = POWER_DYNAMICS["PTAPower"]
        elif "奉俊昊" in director:
            power = POWER_DYNAMICS["BongClass"]
        elif "黑泽明" in director:
            power = POWER_DYNAMICS["KurosawaWeather"]
        elif "库斯杜力卡" in director:
            power = POWER_DYNAMICS["KusturicaChaos"]
        elif "塔可夫斯基" in director:
            power = POWER_DYNAMICS["TarkovskyMaterial"]
        elif "约阿希姆" in director or "提尔" in director:
            power = POWER_DYNAMICS["TrierRoom"]
        else:
            power = POWER_DYNAMICS["WKWMemory"]

    # 动态生成"谁 vs 谁" + "权力动态"
    power_type = power["type"]
    physical_distance = power["physical_distance"]
    eye_contact = power["eye_contact"]
    scene_archetype = power["scene_archetype"]

    # 动态生成目光次数 (基于权力动态)
    if "压迫" in power_type or "渺小" in power_type:
        eye_a_to_b = "5 次 (凝视)"
        eye_b_to_a = "0-1 次 (躲避)"
    elif "靠近" in power_type or "同屋" in power_type:
        eye_a_to_b = "3-4 次 (想看但克制)"
        eye_b_to_a = "3-4 次 (想看但克制)"
    elif "追逐" in power_type:
        eye_a_to_b = "8+ 次 (想接近)"
        eye_b_to_a = "1-2 次 (身体抗拒)"
    elif "上下" in power_type:
        eye_a_to_b = "垂直 (向下俯视)"
        eye_b_to_a = "垂直 (向上仰望)"
    elif "狂欢" in power_type:
        eye_a_to_b = "2-3 次 (混乱中偶然)"
        eye_b_to_a = "2-3 次 (混乱中偶然)"
    elif "在场" in power_type:
        eye_a_to_b = "看不在场的人/物"
        eye_b_to_a = "看不在场的人/物"
    else:
        eye_a_to_b = "3-4 次"
        eye_b_to_a = "3-4 次"

    out = """【3. 关系意图 - 此刻是谁 vs 谁】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{char_a} vs {char_b}

权力动态 (由导演灵魂决定): {power_type}
  - 物理距离: {physical_distance}
  - 目光方向: {eye_contact}
  - 场景原型: {scene_archetype}

不对等的目光:
  - {char_a}看{char_b}的次数: {eye_a_to_b}
  - {char_b}看{char_a}的次数: {eye_b_to_a}

这种不对等, 是他们此刻关系的最直接具象。

导演灵魂的隐喻系统:
  - 物件隐喻: {object_metaphor}
  - 空间原型: {horizon}

{scene_phrase}

整场戏没有一句"我爱你"或"我恨你", 但观众看完会相信:

  他们{relation_implication}。

应该做到:
  ✓ 用物理距离说心理距离
  ✓ 用目光次数说权力动态
  ✓ 用物件的位置说关系状态
  ✓ 整场戏的调度都为这个关系服务
""".format(
        char_a=char_a or "角色 A",
        char_b=char_b or "角色 B",
        power_type=power_type,
        physical_distance=physical_distance,
        eye_contact=eye_contact,
        scene_archetype=scene_archetype,
        eye_a_to_b=eye_a_to_b,
        eye_b_to_a=eye_b_to_a,
        object_metaphor=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("object_metaphor", "未指定"),
        horizon=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("horizon", "未指定"),
        scene_phrase=("场景: " + scene) if scene else "场景: 未指定",
        relation_implication="的关系比台词说的更深",
    )
    return out


def _build_theme_intent(soul_fused, scene, theme_hint, director):
    """动态生成主题意图 (由 higher_archetype 决定)"""
    archetype = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("higher_archetype", "")

    # 决定主题原型
    theme_archetype = ""
    if "记忆" in archetype or "错失" in archetype:
        theme_archetype = "time"
    elif "认知" in archetype or "时间结构" in archetype:
        theme_archetype = "time"
    elif "权力" in archetype or "家庭" in archetype or "父权" in archetype:
        theme_archetype = "power"
    elif "阶层" in archetype or "气味" in archetype:
        theme_archetype = "class"
    elif "道德" in archetype or "自然" in archetype:
        theme_archetype = "weather"
    elif "乡愁" in archetype or "狂欢" in archetype:
        theme_archetype = "chaos"
    elif "物质" in archetype or "时间与记忆" in archetype:
        theme_archetype = "material"
    elif "代际" in archetype or "传承" in archetype:
        theme_archetype = "generation"
    elif "王家卫" in director:
        theme_archetype = "memory"
    elif "诺兰" in director:
        theme_archetype = "time"
    elif "PTA" in director:
        theme_archetype = "power"
    elif "奉俊昊" in director:
        theme_archetype = "class"
    elif "黑泽明" in director:
        theme_archetype = "weather"
    elif "库斯杜力卡" in director:
        theme_archetype = "chaos"
    elif "塔可夫斯基" in director:
        theme_archetype = "material"
    elif "约阿希姆" in director or "提尔" in director:
        theme_archetype = "generation"
    else:
        theme_archetype = "memory"

    theme_text = THEME_BY_ARCHETYPE.get(theme_archetype, THEME_BY_ARCHETYPE["memory"])

    # 决定承载主题的"面"
    # F1 单情感 → 主题的"面 1"
    # F7 情感转化 → 主题的"面 2" (转化面)
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    if "F7" in fusion_mode:
        thematic_facet = "转化面 (本场是主题的'before/after'分界线)"
    elif "F4" in fusion_mode:
        thematic_facet = "递进面 (本场是主题发展的中间点)"
    elif "F5" in fusion_mode:
        thematic_facet = "矛盾面 (本场是主题的极端表达)"
    elif "F3" in fusion_mode:
        thematic_facet = "对峙面 (本场是主题的两难时刻)"
    elif "F6" in fusion_mode:
        thematic_facet = "复合面 (本场是主题的多层叠加)"
    else:
        thematic_facet = "核心面 (本场是主题的初次呈现)"

    # 决定象征元素 (动态)
    symbolic_choices = {
        "memory": ["凤梨罐头", "过期照片", "未寄出的信", "老电话", "船票", "雨伞"],
        "time": ["怀表", "陀螺", "沙漏", "磁带", "照片", "时钟"],
        "power": ["石油", "水", "钻头", "录音带", "黑胶", "钢琴"],
        "class": ["楼梯", "石头", "桃子", "雨水", "廉价香水", "假证书"],
        "weather": ["雨", "雪", "雾", "风", "剑", "镜子"],
        "chaos": ["动物", "婚礼", "葬礼", "酒", "音乐", "河"],
        "material": ["水", "火", "风", "蜡烛", "旧照片", "童年房间"],
        "generation": ["房子", "窗户", "镜子", "钢琴", "旧书", "父亲的椅子"],
    }
    symbolic_element = symbolic_choices.get(theme_archetype, symbolic_choices["memory"])[0]
    if soul_fused.get("visual_signs"):
        # 尝试从 visual_signs 提取元素
        vs = soul_fused.get("visual_signs", "")
        for elem in sum(symbolic_choices.values(), []):
            if elem in vs:
                symbolic_element = elem
                break

    out = """【4. 主题意图 - 本场承载主题的哪一面】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

主题原型: {theme_text}
承载面: {thematic_facet}
象征元素: {symbolic_element}

本场是主题的{thematic_facet_short}, 观众看完应该隐隐感到, 但说不清楚。

就像 {director} 的电影, 看完几个月后才突然明白那场戏是什么意思。

主题的隐喻系统:
  - 物件: {symbolic_element}
  - 空间: {horizon}
  - 时间: {time_logic}

应该做到:
  ✓ 用 {symbolic_element} 承担主题的呈现
  ✓ 整场戏的每一个细节都为主题服务
  ✓ 主题是"隐隐感到", 不是"明确告知"
  ✓ 让观众在看完后自己去琢磨
""".format(
        theme_text=theme_text,
        thematic_facet=thematic_facet,
        thematic_facet_short=thematic_facet.split("面")[0] + "面" if "面" in thematic_facet else "核心面",
        symbolic_element=symbolic_element,
        director=director,
        horizon=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("horizon", "未指定"),
        time_logic=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("time_logic", "未指定"),
    )
    return out


def _build_silence_intent(soul_fused, n_lines, silence_min, pause_sec, char_a, char_b, director):
    """动态生成留白意图 (由 fusion_mode 决定)"""
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    silence_form_data = SILENCE_BY_FUSION_MODE.get(fusion_mode, SILENCE_BY_FUSION_MODE["F1_单情感主导"])
    form = silence_form_data["form"]
    principle = silence_form_data["principle"]
    duration_principle = silence_form_data["duration_principle"]
    micro_event = silence_form_data["micro_event"]

    # 动态生成沉默的具体事件 (基于 F7 必最大留白)
    if "F7" in fusion_mode:
        actual_silence_min = max(silence_min, 8)
        silence_intro = "【F7 情感转化 - 必有最大留白】"
        silence_principle_extra = "F7 是情感转化场, 沉默即转化的瞬间, 必须有 60-80% 的沉默比例"
    else:
        actual_silence_min = silence_min
        silence_intro = "【普通留白 - 由融合模式决定】"
        silence_principle_extra = ""

    # 动态生成沉默中的微事件 (基于导演的 silence_form)
    director_silence_form = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("silence_form", "")
    if "王家卫" in director:
        micro_silence_events = [
            "他说'我走了', 停 5 秒, 走出门, 镜头留在空房间里 30 秒",
            "两个人同时看表, 30 秒, 谁都不说话",
            "烟灰缸里的烟烧到手指, 5 秒, 谁都没提醒",
        ]
    elif "库斯杜力卡" in director:
        micro_silence_events = [
            "一只鸡走过两个人中间, 5 秒, 谁都没动",
            "酒洒在桌上, 流下来, 10 秒, 谁都没擦",
            "远处的狗叫, 两个人同时停下动作, 5 秒",
        ]
    elif "塔可夫斯基" in director:
        micro_silence_events = [
            "一滴水从天花板落下, 2 分钟, 镜头跟到底",
            "风吹动窗帘, 30 秒, 房间里没人",
            "一根蜡烛烧到底, 1 分钟, 镜头不动",
        ]
    elif "约阿希姆" in director or "提尔" in director:
        micro_silence_events = [
            "窗外的光线慢慢移动, 1 分钟, 房间里两个人不说话",
            "父亲看着一把空椅子, 30 秒",
            "钢琴盖打开, 没人弹, 20 秒",
        ]
    elif "诺兰" in director:
        micro_silence_events = [
            "走廊的尽头, 一个人走远, 30 秒",
            "墙上的钟, 时间倒流的瞬间, 5 秒",
            "电梯门关上, 1 分钟, 没人按楼层",
        ]
    elif "PTA" in director:
        micro_silence_events = [
            "一个人在 5 米外看着另一个人, 30 秒",
            "一根钻头的声音, 1 分钟, 没人说话",
            "一杯水从桌面滚落, 5 秒, 慢镜头",
        ]
    elif "奉俊昊" in director:
        micro_silence_events = [
            "两个人在不同楼梯上对视, 30 秒",
            "雨声, 1 分钟, 镜头在两个人的鞋之间切",
            "门铃响, 10 秒, 谁都不开",
        ]
    elif "黑泽明" in director:
        micro_silence_events = [
            "雨突然停了, 30 秒, 两个人看着窗外",
            "风把门吹开, 10 秒, 没人关",
            "远处的雷, 5 秒, 镜头摇到天上",
        ]
    else:
        micro_silence_events = [
            "{char_a}的筷子停了一下, {char_b}看了窗外, 窗外的雨声变大了".format(char_a=char_a or "父亲", char_b=char_b or "女儿"),
            "桌上的茶杯冒着热气, 5 秒, 没人喝",
            "时钟走过 30 秒, 1 分钟, 没人说话",
        ]

    # 拼接
    if director_silence_form:
        director_silence_note = "导演的沉默形式: {dsf}".format(dsf=director_silence_form)
    else:
        director_silence_note = "导演的沉默形式: 默认为日常沉默"

    out = """【5. 留白意图 - 什么不该说】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{silence_intro}
留白形式: {form}
原则: {principle}
时长原则: {duration_principle}
{silence_principle_extra}

这场戏有 {n_lines} 句对白, 但真正的情感发生在 {actual_silence_min} 分钟的沉默里。

每句对白前停 {pause_sec} 秒。

沉默的几分钟里, 发生什么:
  - {micro_event}
  - {micro_silence_event_1}
  - {micro_silence_event_2}
  - {micro_silence_event_3}

{director_silence_note}

应该做到:
  ✓ 沉默即台词, 沉默即情感, 沉默即关系
  ✓ 微事件撑起沉默 (一个动作, 一个眼神, 一个物件)
  ✓ 整场戏的沉默节奏都为关系服务
  ✓ 让观众在沉默中"听见"没说出口的话

这就是那说不满的一寸。
""".format(
        silence_intro=silence_intro,
        form=form,
        principle=principle,
        duration_principle=duration_principle,
        silence_principle_extra=silence_principle_extra,
        n_lines=n_lines,
        actual_silence_min=actual_silence_min,
        pause_sec=pause_sec,
        micro_event=micro_event,
        micro_silence_event_1=micro_silence_events[0] if micro_silence_events else "未指定",
        micro_silence_event_2=micro_silence_events[1] if len(micro_silence_events) > 1 else "未指定",
        micro_silence_event_3=micro_silence_events[2] if len(micro_silence_events) > 2 else "未指定",
        director_silence_note=director_silence_note,
    )
    return out


# ============================================================
# 灵魂融合层
# ============================================================
def _build_soul_fusion_section(soul_fused, soul_dims, soul_state, director):
    """生成灵魂融合层 - 完整数据"""
    if not soul_fused:
        return ""

    out = """════════════════════════════════════════
【灵魂融合层 (Soul Fusion Layer)】
════════════════════════════════════════

【主导情感 + 融合】
  主导情感: {name}
  融合模式: {fusion_mode}
  融合情感: {emotions_str}
  权重: {weights_str}
  强度: {intensity:.2f}
  极性: {polarity}
  唤醒度: {arousal}

【情感表现层】
  视觉: {visual_signs}
  声音: {voice_signs}
  面部肌肉: {facial_au}
  内心独白: {inner_monologue}
  色彩: {color_palette}
  音乐倾向: {music_tempo}

【灵魂维度 10】
  创造力: {creativity:.2f} | 想象力: {imagination:.2f} | 艺术表达: {artistic_expression:.2f}
  镜头技巧: {camera_skill:.2f} | 氛围掌控: {atmosphere_control:.2f}
  灵感时刻: {inspiration:.2f} | 叛逆度: {rebelliousness:.2f}
  自我怀疑: {self_doubt:.2f} | 突破勇气: {breakthrough_courage:.2f}

【灵魂状态 (Soul State)】
  灵感指数: {inspiration_state:.2f}
  疲劳指数: {fatigue_state:.2f}
  怀疑指数: {doubt_state:.2f}
  叛逆指数: {rebelliousness_state:.2f}
  精神状态: {mental_state}

【导演灵魂签名】
  导演: {director}
  签名: {signature}
  高级原型: {higher_archetype}
  物件隐喻: {object_metaphor}
  时间逻辑: {time_logic}
""".format(
        name=soul_fused.get("name", "未指定"),
        fusion_mode=soul_fused.get("fusion_mode", "未指定"),
        emotions_str=" + ".join(soul_fused.get("emotions", [])),
        weights_str=str([round(w, 2) for w in soul_fused.get("weights", [])]),
        intensity=soul_fused.get("intensity", 0.5),
        polarity=soul_fused.get("polarity", "neutral"),
        arousal=soul_fused.get("arousal", "medium"),
        visual_signs=(soul_fused.get("visual_signs", "") or "")[:300],
        voice_signs=(soul_fused.get("voice_signs", "") or "")[:200],
        facial_au=(soul_fused.get("facial_au", "") or "")[:200],
        inner_monologue=(soul_fused.get("inner_monologue", "") or "")[:200],
        color_palette=(soul_fused.get("color_palette", "") or "")[:200],
        music_tempo=(soul_fused.get("music_tempo", "") or "")[:200],
        creativity=soul_dims.get("creativity", 0.85),
        imagination=soul_dims.get("imagination", 0.85),
        artistic_expression=soul_dims.get("artistic_expression", 0.85),
        camera_skill=soul_dims.get("camera_skill", 0.85),
        atmosphere_control=soul_dims.get("atmosphere_control", 0.85),
        inspiration=soul_dims.get("inspiration", 0.85),
        rebelliousness=soul_dims.get("rebelliousness", 0.70),
        self_doubt=soul_dims.get("self_doubt", 0.50),
        breakthrough_courage=soul_dims.get("breakthrough_courage", 0.85),
        inspiration_state=soul_state.get("inspiration", 0.85),
        fatigue_state=soul_state.get("fatigue", 0.30),
        doubt_state=soul_state.get("doubt", 0.50),
        rebelliousness_state=soul_state.get("rebelliousness", 0.70),
        mental_state=soul_state.get("mental_state", "lucid-dreamy"),
        director=director,
        signature=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("signature", "未指定"),
        higher_archetype=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("higher_archetype", "未指定"),
        object_metaphor=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("object_metaphor", "未指定"),
        time_logic=DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("time_logic", "未指定"),
    )
    return out


# ============================================================
# 5 要素架构
# ============================================================
def _build_5_elements_section(soul_fused, scene, char_a, char_b, theme_hint, relation_hint, emotion_hint, silence_min):
    """5 要素架构 - 真实数据/上下文/Skill/经验矩阵/AI 深度处理"""
    out = """════════════════════════════════════════
【5 要素架构 (5 Elements Architecture)】
════════════════════════════════════════

【1. 数据层 (Data Layer)】
  - 1161 部作品 director_view 14 维档案
  - 63 导演 12 维深度档案
  - 191 条反 AI 禁用词表
  - 12 套理论 (Save the Cat / Hero's Journey / Story Circle / McKee / 三幕剧 / 8 Sequences / 五幕剧 / 短剧三秒铁律 / 抖音套路 / 爆款公式 / 角色弧光 / 反转节奏余韵)
  - 14 部真实短剧案例
  - 48 情感矩阵
  - 7 大情感融合公式 (F1-F7)
  - 60+ 灵魂情感 (Plutchik + Izard + Geneva + Barrett 复合)
  - 10 大灵魂维度
  - 灵魂状态 (灵感/疲劳/怀疑/叛逆)
  - 8 大顶级导演灵魂签名
  - 15 位导演真实意图样本

【2. 上下文缩略层 (Context Abbreviation)】
  - 灵魂: {emotion_name} ({polarity}, 强度 {intensity:.2f})
  - 类型: {scene_type_guess}
  - 主题: {theme_phrase}
  - 关系: {relation_phrase}
  - 情感: {emotion_phrase}
  - 场景: {scene_phrase}
  - 角色: {char_a} / {char_b}
  - 沉默: {silence_min} 分钟

【3. Skill/Harness 层 (导演意图生成引擎)】
  - 灵魂融合公式: 5 维意图根据灵魂 polarity / higher_archetype / fusion_mode 动态生成
  - 感受意图 ← emotional_polarity
  - 情感意图 ← visual_signs + voice_signs + facial_au
  - 关系意图 ← higher_archetype → power dynamic
  - 主题意图 ← higher_archetype → thematic facet
  - 留白意图 ← fusion_mode → silence form (F7 必最大留白)
  - 30 句反 AI 对白 + 40 句实战钩子
  - 沉默/留白 5 规则 (附件核心)

【4. 经验矩阵层 (Experience Matrix)】
  - 王家卫: 物件代替心理, 时间戳, 60s 慢节奏
  - 诺兰: 时间结构即主题, 史诗感, IMAX 客观
  - PTA: 用可观察行为代替情绪, 70s 迷幻, 慢推长焦
  - 奉俊昊: 用空间做阶层隐喻, 类型当特洛伊木马, 同场多情绪
  - 黑泽明: 天气即角色, 极致清晰, 群戏调度
  - 库斯杜力卡: 少说话, 沉默即情感, 塞尔维亚乡愁
  - 塔可夫斯基: 时间即主角, 长镜头, 诗意朦胧
  - 约阿希姆·提尔: 从房子视角叙事, 家庭代际, 北欧光
  - 侯孝贤: 不动, 让时间发生
  - 是枝裕和: 日常细节, 不评判
  - 伯格曼: 脸特写, 沉默, 心理剧
  - 小津: 低位静态, 重复
  - 蔡明亮: 超慢, 无对白
  - 李沧东: 不给答案
  - 毕赣: 时间折叠
  - 贾樟柯: 流行歌标记时代
  - 李安: 饭桌戏
  - 库布里克: 对称

【5. AI 深度处理 (AI Deep Processing)】
  - 反 AI 词表 191 条已内部应用 (不输出具体词表)
  - 10 铁律强制应用 (SPECIFIC_DETAIL_RULES)
  - 沉默/留白 5 规则强制应用 (SILENCE_MASTERY_5)
  - 灵魂深度处理: emotional_polarity → 感受基调; visual_signs → 情感表现; fusion_mode → 留白节奏
  - 4 轮迭代 + 人工挑选 + LLM 反馈循环
  - 不描述"画面里有什么", 描述"导演会怎么描述自己的意图"
  - 用物件代替心理, 用沉默代替台词, 用空间代替时间
""".format(
        emotion_name=soul_fused.get("name", "未指定"),
        polarity=soul_fused.get("polarity", "neutral"),
        intensity=soul_fused.get("intensity", 0.5),
        scene_type_guess="对话/重逢/离别/日常" if not scene else "已指定",
        theme_phrase=theme_hint or "未指定",
        relation_phrase=relation_hint or "未指定",
        emotion_phrase=emotion_hint or "未指定",
        scene_phrase=scene or "未指定",
        char_a=char_a or "角色 A",
        char_b=char_b or "角色 B",
        silence_min=silence_min,
    )
    return out


# ============================================================
# 灵魂深度处理层
# ============================================================
def _build_soul_deep_processing_section(soul_fused, soul_dims, soul_state, director, char_a, char_b, scene):
    """灵魂深度处理 - 60+ 情感 + 10 维度 + 灵魂状态 + 深度分析"""
    intensity = soul_fused.get("intensity", 0.5)
    arousal = soul_fused.get("arousal", "medium")
    polarity = soul_fused.get("polarity", "neutral")
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    emotions = soul_fused.get("emotions", [])
    weights = soul_fused.get("weights", [])

    # 60+ 情感深度拆解
    emotion_detail_lines = []
    for i, ekey in enumerate(emotions[:5]):
        if _HAS_SOUL and ekey in EMOTION_MATRIX_60:
            emo = EMOTION_MATRIX_60[ekey]
            w = weights[i] if i < len(weights) else 0.0
            emotion_detail_lines.append("""  ── {idx}. {name} (权重 {w:.2f}, intensity {ei:.2f}, {ep}, {ea})
     类别: {cat}
     描述: {desc}
     视觉: {vs}
     声音: {vcs}
     面部肌肉: {au}
     内心独白: {im}
     色彩: {cp}
     音乐: {mt}
     导演案例: {de}""".format(
                idx=i+1,
                name=emo.get("name", ekey),
                w=w,
                ei=emo.get("intensity", 0.5),
                ep=emo.get("polarity", ""),
                ea=emo.get("arousal", ""),
                cat=emo.get("category", ""),
                desc=emo.get("description", ""),
                vs=(emo.get("visual_signs", "") or "")[:120],
                vcs=(emo.get("voice_signs", "") or "")[:80],
                au=(emo.get("facial_au", "") or "")[:80],
                im=(emo.get("inner_monologue", "") or "")[:80],
                cp=(emo.get("color_palette", "") or "")[:80],
                mt=(emo.get("music_tempo", "") or "")[:80],
                de=(emo.get("director_examples", "") or "")[:100],
            ))

    emotion_details = "\n\n".join(emotion_detail_lines) if emotion_detail_lines else "  (无情感细节)"

    # 10 维度深度分析
    dims_analysis = []
    for k, label in [
        ("creativity", "D1 创造力"),
        ("imagination", "D2 想象力"),
        ("artistic_expression", "D3 艺术表达力"),
        ("camera_skill", "D4 镜头语言技巧"),
        ("atmosphere_control", "D5 画面氛围掌控"),
    ]:
        v = soul_dims.get(k, 0.85)
        if v > 0.9:
            desc = "极高 (突破常规, 反预期但本该如此)"
        elif v > 0.75:
            desc = "高 (高于平均, 有鲜明个人特色)"
        elif v > 0.5:
            desc = "中等 (稳定输出, 不出错)"
        else:
            desc = "低 (照搬已有模式, 安全但平庸)"
        dims_analysis.append("  - {label}: {v:.2f} → {desc}".format(label=label, v=v, desc=desc))

    # 灵魂状态分析
    inspiration = soul_state.get("inspiration", 0.85)
    fatigue = soul_state.get("fatigue", 0.30)
    doubt = soul_state.get("doubt", 0.50)
    rebelliousness = soul_state.get("rebelliousness", 0.70)

    state_analysis = """  灵感指数: {ins:.2f} → {ins_d}
  疲劳指数: {fat:.2f} → {fat_d}
  怀疑指数: {dou:.2f} → {dou_d}
  叛逆指数: {reb:.2f} → {reb_d}
  精神状态: {ms}""".format(
        ins=inspiration,
        fat=fatigue,
        dou=doubt,
        reb=rebelliousness,
        ins_d="灵感爆发, 大胆创新" if inspiration > 0.8 else "灵感稳定, 正常输出" if inspiration > 0.5 else "灵感枯竭, 保守稳定",
        fat_d="极度疲劳, 后期需要大量重剪" if fatigue > 0.7 else "适度疲劳, 状态真实" if fatigue > 0.3 else "精力充沛, 准备充分",
        dou_d="高度怀疑, 反复重剪, 余韵更长" if doubt > 0.7 else "适度怀疑, 反复打磨" if doubt > 0.4 else "确信, 一次性拍完",
        reb_d="极致叛逆, 完全打破规则" if rebelliousness > 0.8 else "敢于突破, 偶尔打破" if rebelliousness > 0.5 else "遵守规则, 类型片化",
        ms=soul_state.get("mental_state", "lucid-dreamy"),
    )

    # 灵魂融合公式
    if "F1" in fusion_mode:
        fusion_formula = "单情感: 整场戏只有一种情感, 占 100% (常见于简单场景)"
    elif "F2" in fusion_mode:
        fusion_formula = "主次: 70% 主 + 30% 次, 表面 vs 内心"
    elif "F3" in fusion_mode:
        fusion_formula = "对等: 50/50, 矛盾并存, 角色内心矛盾"
    elif "F4" in fusion_mode:
        fusion_formula = "递进: 20% + 30% + 50%, 随时间变化"
    elif "F5" in fusion_mode:
        fusion_formula = "矛盾爆炸: 50%+50% intensity 1.0+1.0, 极端压力下崩溃"
    elif "F6" in fusion_mode:
        fusion_formula = "复合三角: 33%+33%+33%, 复杂心理状态"
    elif "F7" in fusion_mode:
        fusion_formula = "情感转化: 100%A → 100%B, 1% 场景但最重要 (必有最大留白)"
    else:
        fusion_formula = fusion_mode

    out = """════════════════════════════════════════
【灵魂深度处理 (Soul Deep Processing)】
════════════════════════════════════════

【A. 主导情感 + 融合公式】
  主导: {emotion_name} ({polarity}, 强度 {intensity:.2f}, {arousal})
  融合模式: {fusion_mode}
  融合公式: {fusion_formula}
  融合情感: {emotions_str}
  权重: {weights_str}

【B. 60+ 情感矩阵深度拆解 (用于本场戏)】
{emotion_details}

【C. 10 灵魂维度深度分析 (用于本场戏)】
{dims_analysis_str}
  ── D6 精神状态: {mental_state}
  ── D7 灵感时刻指数: {ins:.2f} (本场会有 1-3 个真正的灵感时刻)
  ── D8 叛逆度: {reb:.2f} (本场是否会打破规则)
  ── D9 自我怀疑: {dou:.2f} (本场是否会反复重拍)
  ── D10 突破勇气: {bc:.2f} (本场是否敢做困难选择)

【D. 灵魂状态深度分析】
{state_analysis}

【E. 灵魂如何驱动 5 维意图】

【E1 感受意图 ← 极性 {polarity}】
  - positive → 让观众感到温暖/治愈/释然
  - negative → 让观众感到心酸/沉重/刺痛
  - mixed → 让观众感到矛盾/复杂/苦乐参半
  - neutral → 让观众感到被见证/陪伴/安静

【E2 情感意图 ← 视觉+声音+面部肌肉+内心独白】
  - 从 visual_signs 提取身体语言
  - 从 voice_signs 提取声音设计
  - 从 facial_au 提取面部表情
  - 从 inner_monologue 提取潜文本

【E3 关系意图 ← higher_archetype → 权力动态】
  - 王家卫 (memory) → 靠近-错过
  - 诺兰 (time) → 追逐-错过
  - PTA (power) → 压迫-反抗
  - 奉俊昊 (class) → 上下-不可逾越
  - 黑泽明 (weather) → 渺小-命运
  - 库斯杜力卡 (chaos) → 狂欢-失序
  - 塔可夫斯基 (material) → 在场-缺席
  - 约阿希姆·提尔 (room) → 代际-传承

【E4 主题意图 ← higher_archetype → 主题原型】
  - 本场是主题的 {thematic_facet}

【E5 留白意图 ← fusion_mode → 留白形式】
  - F7 必最大留白 (60-80%)
  - F1 单一沉默 (30-40%)
  - F3 矛盾沉默 (对峙)
  - F5 极端沉默 (爆炸前夜)
  - 其它按比例

【F. 灵魂 × 角色 × 场景 三维交叉】

场景: {scene_phrase}
角色 A: {char_a_phrase}
角色 B: {char_b_phrase}

在 {scene} 这个场景里, {char_a} 和 {char_b} 相遇, 他们的灵魂是:
  主导: {emotion_name}
  极性: {polarity}
  强度: {intensity:.2f}
  唤醒度: {arousal}

这意味着:
  1. 他们的身体会有 {intensity_label} 的反应
  2. 他们的对话会有 {silence_label} 的留白
  3. 他们的关系会呈现 {power_type} 的权力动态
  4. 他们的关系会承载主题的 {thematic_facet} 一面
  5. 他们之间会有 {silence_form} 的沉默

【G. 反 AI 深度处理 (10 铁律 + 191 词表)】
  - 灵魂驱动一切, 不依赖任何 AI 模板
  - 用可观察行为代替情绪 (PTA 原则)
  - 用物件代替心理 (王家卫原则)
  - 用沉默代替台词 (库斯杜力卡原则)
  - 用空间代替时间 (诺兰原则)
  - 用天气代替情绪 (黑泽明原则)
  - 用物质代替记忆 (塔可夫斯基原则)
  - 用房子代替代际 (提尔原则)
  - 用阶层代替气味 (奉俊昊原则)
  - 用动物代替乡愁 (库斯杜力卡原则)
  - 反 AI 词表 191 条已内部应用 (不输出具体词表)
  - 10 铁律强制应用 (具体细节优先)
  - 沉默/留白 5 规则强制应用 (附件核心)
""".format(
        emotion_name=soul_fused.get("name", "未指定"),
        polarity=polarity,
        intensity=intensity,
        arousal=arousal,
        fusion_mode=fusion_mode,
        fusion_formula=fusion_formula,
        emotions_str=" + ".join(emotions) if emotions else "未指定",
        weights_str=str([round(w, 2) for w in weights]),
        emotion_details=emotion_details,
        dims_analysis_str="\n".join(dims_analysis),
        mental_state=soul_state.get("mental_state", "lucid-dreamy"),
        ins=inspiration,
        reb=rebelliousness,
        dou=doubt,
        bc=soul_dims.get("breakthrough_courage", 0.85),
        state_analysis=state_analysis,
        thematic_facet="核心面" if "F1" in fusion_mode else "递进面" if "F4" in fusion_mode else "矛盾面" if "F3" in fusion_mode or "F5" in fusion_mode else "转化面" if "F7" in fusion_mode else "复合面" if "F6" in fusion_mode else "核心面",
        scene_phrase=scene or "未指定",
        char_a_phrase=char_a or "角色 A",
        char_b_phrase=char_b or "角色 B",
        scene=scene or "未指定",
        char_a=char_a or "角色 A",
        char_b=char_b or "角色 B",
        intensity_label="明显" if intensity > 0.7 else "微妙" if intensity > 0.4 else "极淡",
        silence_label="极大 (60-80%)" if "F7" in fusion_mode else "中等 (40-50%)" if "F5" in fusion_mode else "标准 (30-40%)",
        power_type="压迫-反抗" if director == "PTA" else "靠近-错过" if director == "王家卫" else "追逐-错过" if director == "诺兰" else "上下-不可逾越" if director == "奉俊昊" else "渺小-命运" if director == "黑泽明" else "狂欢-失序" if director == "库斯杜力卡" else "在场-缺席" if director == "塔可夫斯基" else "代际-传承" if "约阿希姆" in director or "提尔" in director else "依导演决定",
        silence_form="F7 最大留白 (60-80%)" if "F7" in fusion_mode else "F5 极端沉默 (50%)" if "F5" in fusion_mode else "F3 矛盾沉默 (40-50%)" if "F3" in fusion_mode else "F1 单一沉默 (30-40%)",
    )
    return out


# ============================================================
# 11 维导演控制
# ============================================================
def _build_11_control_section(soul_fused, soul_dims, soul_state, director, scene):
    """11 维导演控制 (结合灵魂)"""
    intensity = soul_fused.get("intensity", 0.5)
    arousal = soul_fused.get("arousal", "medium")
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    rebelliousness = soul_dims.get("rebelliousness", 0.70)
    self_doubt = soul_dims.get("self_doubt", 0.50)
    doubt_state = soul_state.get("doubt", 0.50)
    inspiration_state = soul_state.get("inspiration", 0.85)

    # 动态决定各维度的强度
    if intensity > 0.7:
        climax_strength = "本场是高潮, 全部维度拉满"
    else:
        climax_strength = "本场是铺垫, 大部分维度保持克制"

    if arousal == "high":
        pacing_note = "节奏快切, 紧张推进, 运镜变化频繁"
    elif arousal == "low":
        pacing_note = "节奏慢推, 大量留白, 运镜极少变化"
    else:
        pacing_note = "节奏均衡, 慢切 + 偶尔快切, 运镜正常"

    if rebelliousness > 0.7:
        reversal_note = "本场敢打破规则, 反转和余韵都会更狠"
    else:
        reversal_note = "本场遵守规则, 反转和余韵都更克制"

    if doubt_state > 0.6:
        aftertaste_note = "怀疑指数高, 余韵会更长更复杂"
    else:
        aftertaste_note = "怀疑指数低, 余韵会更直接"

    out = """════════════════════════════════════════
【11 维导演控制 (11-D Director Control) - 结合灵魂】
════════════════════════════════════════

【1. 空镜 (Empty Shot)】
  灵魂应用: 视觉锚点 {visual_short} → 设计 2-3 个空镜
  本场空镜: 30 秒无对白 / 走廊 / 窗外 / 一张桌子

【2. 留白 (Negative Space)】
  灵魂应用: 融合模式 {fusion_mode} → 决定留白节奏
  本场留白: {silence_min} 分钟, 比例 30-50%
  留白形式: {silence_form}

【3. 氛围渲染 (Atmosphere)】
  灵魂应用: 色彩 {color_short} + 唤醒度 {arousal} → 决定光线/色彩
  本场氛围: 灵魂状态决定光线软硬 + 音乐密度
  具体: 60/30/10 色彩 + 9 维光影 (按导演签名)

【4. 悬疑 (Suspense)】
  灵魂应用: 怀疑指数 {doubt_state:.2f} → 决定悬疑密度
  本场悬疑: 信息差 + 时间差 + 空间差, 避免强行反转

【5. 多线 (Multi-thread)】
  灵魂应用: 灵魂维度想象力 {imagination:.2f} → 决定多线复杂度
  本场多线: 主线 + 1-2 副线 + 时间折叠 (按导演)

【6. 反转 (Reversal)】
  {reversal_note}
  本场反转: 认知/期待/道德/时间的突然翻转 (按导演)

【7. 高潮 (Climax)】
  {climax_strength}
  本场高潮: 积累的爆点, 一场戏能改变所有关系

【8. 余韵 (Aftertaste)】
  {aftertaste_note}
  本场余韵: 结尾后, 观众还在咀嚼的东西

【9. 推进节奏 (Pacing)】
  {pacing_note}
  本场节奏: 1-3 个快切 + 5-8 个慢推 + 1-2 个长镜头

【10. 感情控制 (Emotion Control)】
  灵魂应用: 极性 {polarity} → 决定感情曲线
  本场感情: 压抑 (40%) + 释放 (30%) + 反讽 (30%) (按导演)

【11. 角色塑造 (Character Building)】
  灵魂应用: 面部肌肉 {facial_short} → 决定表演方向
  本场角色: 通过可观察行为建立, 不写内心 (PTA 原则)
  具体: 1-2 个核心微动作 + 1 个反常动作 + 1 个沉默时刻
""".format(
        visual_short=(soul_fused.get("visual_signs", "") or "")[:80],
        fusion_mode=fusion_mode,
        silence_min=soul_fused.get("intensity", 0.5) * 5,
        silence_form="物件留白 + 时间留白 + 沉默留白 (按导演)",
        color_short=(soul_fused.get("color_palette", "") or "")[:80],
        arousal=arousal,
        doubt_state=doubt_state,
        imagination=soul_dims.get("imagination", 0.85),
        reversal_note=reversal_note,
        climax_strength=climax_strength,
        aftertaste_note=aftertaste_note,
        pacing_note=pacing_note,
        polarity=soul_fused.get("polarity", "neutral"),
        facial_short=(soul_fused.get("facial_au", "") or "")[:80],
    )
    return out


# ============================================================
# 3 留白 + 3 运镜
# ============================================================
def _build_3silence_3motion_section(soul_fused, director, scene):
    """3 留白 + 3 运镜 - 全部应用, 结合灵魂状态"""
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    arousal = soul_fused.get("arousal", "medium")

    # 3 留白
    if "F7" in fusion_mode:
        silence1 = "本场主用「沉默留白」(F7 必最大留白, 60-80%)"
        silence2 = "辅助「时间留白」(长空镜 1-2 分钟, 镜头停驻)"
        silence3 = "偶尔「物件留白」(一个物件代替一段心理)"
    elif "F5" in fusion_mode:
        silence1 = "本场主用「沉默留白」(F5 矛盾爆炸前后必须有)"
        silence2 = "辅助「物件留白」(一个动作撑起 30 秒)"
        silence3 = "偶尔「时间留白」(镜头在空间里停 10 秒)"
    else:
        silence1 = "本场主用「物件留白」(一个凤梨罐头代替一段心理, 王家卫式)"
        silence2 = "辅助「时间留白」(一个停顿代替一段对白, 时长即情感)"
        silence3 = "偶尔「沉默留白」(一段安静代替一段台词)"

    # 3 运镜
    director_motion_style = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("visual_grammar", "")
    if "王家卫" in director:
        motion1 = "本场主用「推近」(60s 慢推, 揭示内心)"
        motion2 = "辅助「后拉」(镜头在两个人之间拉远, 距离感)"
        motion3 = "偶尔「横移」(手摇摄影, 60s 慢节奏)"
    elif "诺兰" in director:
        motion1 = "本场主用「推近」(长焦压缩 + 慢推, 凝视)"
        motion2 = "辅助「后拉」(IMAX 全景, 史诗感)"
        motion3 = "偶尔「横移」(长焦平行, 时间流逝)"
    elif "PTA" in director:
        motion1 = "本场主用「推近」(慢推长焦, 凝视 5 秒)"
        motion2 = "辅助「横移」(70s 平行, 时间凝固)"
        motion3 = "偶尔「后拉」(揭示权力空间)"
    elif "奉俊昊" in director:
        motion1 = "本场主用「后拉」(固定镜头 + 纵深调度, 揭示阶层)"
        motion2 = "辅助「横移」(楼梯上的纵向调度)"
        motion3 = "偶尔「推近」(特写脸 + 雨声)"
    elif "黑泽明" in director:
        motion1 = "本场主用「横移」(多机位群戏 + 极清晰)"
        motion2 = "辅助「推近」(道德凝视)"
        motion3 = "偶尔「后拉」(人在天地间)"
    elif "库斯杜力卡" in director:
        motion1 = "本场主用「横移」(手持 + 群戏 + 巴洛克调度)"
        motion2 = "辅助「推近」(混乱中的凝视)"
        motion3 = "偶尔「后拉」(狂欢中的远景)"
    elif "塔可夫斯基" in director:
        motion1 = "本场主用「推近」(长镜头 1-7 分钟, 物质即记忆)"
        motion2 = "辅助「后拉」(空间揭示)"
        motion3 = "偶尔「横移」(诗意朦胧)"
    elif "约阿希姆" in director or "提尔" in director:
        motion1 = "本场主用「推近」(长焦 + 安静 + 中远景)"
        motion2 = "辅助「后拉」(从房间拉远到整栋楼)"
        motion3 = "偶尔「横移」(北欧光平行观察)"
    else:
        motion1 = "本场主用「推近」(揭示内心)"
        motion2 = "辅助「后拉」(揭示空间)"
        motion3 = "偶尔「横移」(时间流逝)"

    out = """════════════════════════════════════════
【3 留白 + 3 运镜 (3 Silences + 3 Camera Motions)】
════════════════════════════════════════

【3 留白 (全部应用, 结合灵魂)】
  1. {silence1}
     - {s1_desc}
     - 1_物件留白: 用一个物件代替一段心理, 让物件说话
     - 2_时间留白: 用一个停顿代替一段对白, 让时间流逝
     - 3_沉默留白: 用一段安静代替一段台词, 让观众听见呼吸

  2. {silence2}
  3. {silence3}

【3 运镜 (全部应用, 结合灵魂)】
  1. {motion1}
     - 1_推近 (Push In): 摄影机向角色推进, 揭示内心, 强调关系, 凝聚张力
     - 2_后拉 (Pull Out): 摄影机远离角色, 揭示空间, 抽离情感, 拉远距离
     - 3_横移 (Track/Pan): 摄影机平行于角色, 平行观察, 时间流逝, 关系不变

  2. {motion2}
  3. {motion3}

导演的视觉语法: {director_motion_style}
灵魂唤醒度: {arousal} (决定运镜速度)
""".format(
        silence1=silence1,
        silence2=silence2,
        silence3=silence3,
        s1_desc="本场 60% 以上的时间都是沉默, 沉默即情感",
        motion1=motion1,
        motion2=motion2,
        motion3=motion3,
        director_motion_style=director_motion_style[:150] if director_motion_style else "未指定",
        arousal=arousal,
    )
    return out


# ============================================================
# 8 顶级导演灵魂签名 + 15 真实意图样本
# ============================================================
def _build_directors_section(director, soul_fused):
    """8 顶级导演灵魂签名 + 15 真实意图样本 - 深度应用"""
    # 当前导演的完整签名
    primary = DIRECTOR_SOUL_SIGNATURES_8.get(director, {})

    # 8 顶级导演签名应用
    sigs = []
    for i, (d, sig) in enumerate(DIRECTOR_SOUL_SIGNATURES_8.items(), 1):
        marker = "★ 当前" if d == director else "  "
        sigs.append("""{marker} {i}. {d} ({name_en})
     签名: {signature}
     高级原型: {higher_archetype}
     物件隐喻: {object_metaphor}""".format(
            marker=marker,
            i=i,
            d=d,
            name_en=sig.get("name_en", ""),
            signature=sig.get("signature", ""),
            higher_archetype=sig.get("higher_archetype", ""),
            object_metaphor=sig.get("object_metaphor", ""),
        ))

    sigs_text = "\n\n".join(sigs)

    # 15 真实意图样本
    samples = []
    for i, (d, intent) in enumerate(DIRECTOR_INTENT_SAMPLES.items(), 1):
        marker = "★ 当前" if d == director else "  "
        samples.append("{marker} {i:>2}. {d:<10}: {intent}".format(marker=marker, i=i, d=d, intent=intent))
    samples_text = "\n".join(samples)

    out = """════════════════════════════════════════
【8 大顶级导演灵魂签名 (8 Top Director Soul Signatures)】
════════════════════════════════════════

{sigs_text}

════════════════════════════════════════
【15 导演真实意图样本 (15 Director Real Intent Samples)】
════════════════════════════════════════

{samples_text}

当前导演 ({director}) 的核心意图:
  {primary_intent}
""".format(
        sigs_text=sigs_text,
        samples_text=samples_text,
        director=director,
        primary_intent=DIRECTOR_INTENT_SAMPLES.get(director, "我希望通过这场戏, 让观众感到灵魂的重量"),
    )
    return out


# ============================================================
# H3 三大字段
# ============================================================
def _build_h3_section(soul_fused, scene, char_a, char_b, director):
    """H3 三大字段 - integrated_multimodal_description + overall_soundscape + non_diegetic_music"""
    visual_signs = soul_fused.get("visual_signs", "")
    voice_signs = soul_fused.get("voice_signs", "")
    color_palette = soul_fused.get("color_palette", "")
    music_tempo = soul_fused.get("music_tempo", "")
    intensity = soul_fused.get("intensity", 0.5)
    arousal = soul_fused.get("arousal", "medium")
    fusion_mode = soul_fused.get("fusion_mode", "F1_单情感主导")
    archetype = DIRECTOR_SOUL_SIGNATURES_8.get(director, {}).get("higher_archetype", "")

    # INTEGRATED_MULTIMODAL_DESCRIPTION
    imd = """[Integrated Multimodal Description]
[Emotion Anchor] {emotion_name} ({polarity}, intensity {intensity:.2f}, {fusion_mode})
[Scene] {scene}
[Characters] {char_a} and {char_b}
[Visual] {visual_signs}
[Voice/Audio] {voice_signs}
[Color Palette] {color_palette}
[Atmosphere] {archetype}
[Director Signature] {director}
[Lighting] {arousal}-arousal, {lighting_desc}
[Camera] {camera_desc}
[Composition] 60/30/10 color rule + 9-dim light + 3 motions (push/pull/track)""".format(
        emotion_name=soul_fused.get("name", "未指定"),
        polarity=soul_fused.get("polarity", "neutral"),
        intensity=intensity,
        fusion_mode=fusion_mode,
        scene=scene or "未指定",
        char_a=char_a or "角色 A",
        char_b=char_b or "角色 B",
        visual_signs=visual_signs[:300] if visual_signs else "未指定",
        voice_signs=voice_signs[:200] if voice_signs else "未指定",
        color_palette=color_palette[:200] if color_palette else "未指定",
        archetype=archetype,
        director=director,
        arousal=arousal,
        lighting_desc="低对比, 自然光, 暖色" if arousal == "low" else "高对比, 硬光, 冷色" if arousal == "high" else "中对比, 混合光, 中性",
        camera_desc="长镜头 + 慢推" if "塔可夫斯基" in director else "手持 + 慢推" if "PTA" in director else "固定 + 纵深" if "奉俊昊" in director else "60s 慢推" if "王家卫" in director else "IMAX + 长焦" if "诺兰" in director else "导演特定",
    )

    # OVERALL_SOUNDSCAPE
    os_text = """[Overall Soundscape]
[Ambient] {ambient}
[Foley] {foley}
[Silence Ratio] {silence_ratio}%
[Dialogue] {dialogue_density} (low/medium/high)
[Emotion] {emotion_in_sound}
[Director Sound Style] {director_sound}""".format(
        ambient="雨声 + 抽油烟机 + 麻将" if "雨" in str(scene) else "环境白噪音 + 风声 + 远处车流" if "街头" in str(scene) else "室内: 钟表 + 脚步 + 关门 + 椅子" if "室内" in str(scene) or "厨房" in str(scene) else "依场景动态生成",
        foley="筷子碰撞 + 热水壶 + 烟头" if "厨房" in str(scene) else "脚步 + 门 + 钥匙" if "街头" in str(scene) else "依场景动态生成",
        silence_ratio=70 if "F7" in fusion_mode else 50 if "F5" in fusion_mode else 30,
        dialogue_density="low" if intensity > 0.7 else "medium" if intensity > 0.4 else "high",
        emotion_in_sound=(voice_signs or "")[:100],
        director_sound="王家卫: 流行歌 + 钟表 + 雨" if "王家卫" in director else "诺兰: Hans Zimmer 史诗" if "诺兰" in director else "PTA: 70s 摇滚 + 收音机" if "PTA" in director else "塔可夫斯基: 自然音 + Bach" if "塔可夫斯基" in director else "奉俊昊: 雨声 + 弦乐" if "奉俊昊" in director else "导演特定",
    )

    # NON_DIEGETIC_MUSIC
    ndm = """[Non-Diegetic Music]
[Style] {music_style}
[Tempo] {music_tempo}
[Key] {key}
[Instrumentation] {instrumentation}
[Emotion Arc] {emotion_arc}
[Volume] {volume}
[When to Start/Stop] {start_stop}""".format(
        music_style=music_tempo[:100] if music_tempo else "依场景动态生成",
        music_tempo=music_tempo[:100] if music_tempo else "60-100 BPM",
        key="minor" if soul_fused.get("polarity") in ["negative", "mixed (矛盾情感)"] else "major" if soul_fused.get("polarity") == "positive" else "modal",
        instrumentation="钢琴 + 大提琴" if arousal == "low" else "弦乐 + 鼓" if arousal == "high" else "弦乐 + 钢琴",
        emotion_arc="渐强 → 高潮 → 渐弱" if intensity > 0.7 else "稳定 → 渐变" if intensity > 0.4 else "安静 → 缓慢浮现",
        volume="低 (20-40%)" if arousal == "low" else "中 (40-70%)" if arousal == "medium" else "高 (70-100%)",
        start_stop="开场即入, 结尾渐弱" if "F7" in fusion_mode else "中段进入, 高潮时停止" if "F5" in fusion_mode else "依场景动态生成",
    )

    out = """════════════════════════════════════════
【H3 三大字段 (H3 Three Fields) - 供下游节点对接】
════════════════════════════════════════

INTEGRATED_MULTIMODAL_DESCRIPTION
────────────────────────────────
{imd}

OVERALL_SOUNDSCAPE
────────────────────────────────
{os_text}

NON_DIEGETIC_MUSIC
────────────────────────────────
{ndm}
""".format(imd=imd, os_text=os_text, ndm=ndm)
    return out


# ============================================================
# 主类 - DirectorIntentPro v2 (灵魂注入版)
# ============================================================
class DirectorIntentPro:
    """
    导演意图节点 v2 - 完整接入 DirectorSoulNode 灵魂注入
    核心: 不是描述"画面里有什么", 而是描述"导演会怎样描述自己的意图"
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 场景 ===
                "场景类型": (["对话", "独处", "追逐", "吃饭", "睡觉", "工作", "生日", "婚礼", "葬礼", "重逢", "离别", "其他"], {"default": "对话"}),
                "场景描述": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨",
                    "multiline": False,
                }),

                # === 2. 角色 ===
                "角色A": ("STRING", {
                    "default": "父亲, 50 岁, 国企下岗",
                    "multiline": False,
                }),
                "角色B": ("STRING", {
                    "default": "女儿, 22 岁, 大三学生",
                    "multiline": False,
                }),

                # === 3. 5 维度 (用户输入) ===
                "感受意图_观众应感到": ("STRING", {
                    "default": "既心酸又释然, 既有遗憾又有温暖",
                    "multiline": True,
                }),
                "情感意图_角色应有": ("STRING", {
                    "default": "想表达爱但说不出口, 想道歉但拉不下脸",
                    "multiline": True,
                }),
                "关系意图_此刻是": ("STRING", {
                    "default": "5 年没见, 彼此陌生但血缘还在",
                    "multiline": True,
                }),
                "主题意图_承载": ("STRING", {
                    "default": "失去的不可逆, 但记忆可以重建",
                    "multiline": True,
                }),
                "留白意图_什么不该说": ("STRING", {
                    "default": "父亲从来不说'我想你', 女儿从来不说'我原谅你'",
                    "multiline": True,
                }),

                # === 4. 沉默参数 ===
                "实际对白数": ("INT", {"default": 8, "min": 0, "max": 50, "step": 1}),
                "沉默时长分钟": ("INT", {"default": 3, "min": 0, "max": 30, "step": 1}),
                "每句对白前停顿秒数": ("INT", {"default": 2, "min": 0, "max": 10, "step": 1}),

                # === 5. 灵魂注入 (Phase 17 灵魂融合) ===
                "灵魂_主导情感": (["auto"] + list(EMOTION_MATRIX_60.keys()) if EMOTION_MATRIX_60 else ["auto", "loneliness", "love", "sadness", "hate", "longing", "tension", "bittersweet"], {"default": "auto"}),
                "灵魂_次要情感_1": (["none"] + list(EMOTION_MATRIX_60.keys()) if EMOTION_MATRIX_60 else ["none", "loneliness", "love", "sadness", "hate", "longing", "tension", "bittersweet"], {"default": "none"}),
                "灵魂_次要情感_2": (["none"] + list(EMOTION_MATRIX_60.keys()) if EMOTION_MATRIX_60 else ["none", "loneliness", "love", "sadness", "hate", "longing", "tension", "bittersweet"], {"default": "none"}),
                "灵魂_次要情感_3": (["none"] + list(EMOTION_MATRIX_60.keys()) if EMOTION_MATRIX_60 else ["none", "loneliness", "love", "sadness", "hate", "longing", "tension", "bittersweet"], {"default": "none"}),
                "灵魂_次要情感_4": (["none"] + list(EMOTION_MATRIX_60.keys()) if EMOTION_MATRIX_60 else ["none", "loneliness", "love", "sadness", "hate", "longing", "tension", "bittersweet"], {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合", "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"], {"default": "auto"}),
                "灵魂_主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 6. 灵魂维度 5 ===
                "灵魂_创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 7. 灵魂状态 4 ===
                "灵魂_灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_疲劳指数": ("FLOAT", {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_怀疑指数": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_叛逆指数": ("FLOAT", {"default": 0.70, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 8. 故事强度 + 场景进度 (影响灵魂状态) ===
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 9. 导演风格 (15 + 8 顶级) ===
                "导演风格": (["王家卫", "诺兰", "PTA", "奉俊昊", "黑泽明", "库斯杜力卡", "塔可夫斯基", "约阿希姆·提尔", "侯孝贤", "是枝裕和", "伯格曼", "小津", "蔡明亮", "李沧东", "库布里克", "毕赣", "贾樟柯", "李安"], {"default": "是枝裕和"}),

                # === 10. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("intent_statement", "director_intent_samples", "anti_ai_cleaned")
    FUNCTION = "build_intent"
    CATEGORY = "PromptLibrary/Phase17 灵魂意图"

    def build_intent(self, **kwargs):
        # ==========================================
        # 1. 解析用户输入
        # ==========================================
        scene_type = _str(kwargs.get("场景类型", "对话"), "对话")
        scene = _str(kwargs.get("场景描述", ""), "")
        char_a = _str(kwargs.get("角色A", ""), "")
        char_b = _str(kwargs.get("角色B", ""), "")

        # 兼容不同字段名 (测试用)
        feeling = _str(
            kwargs.get("感受意图_观众应感到", "")
            or kwargs.get("感受意图", "")
            or kwargs.get("感受", ""),
            ""
        )
        emotion = _str(
            kwargs.get("情感意图_角色应有", "")
            or kwargs.get("情感意图_角色应感到", "")
            or kwargs.get("情感意图", "")
            or kwargs.get("情感", ""),
            ""
        )
        relation = _str(
            kwargs.get("关系意图_此刻是", "")
            or kwargs.get("关系意图", "")
            or kwargs.get("关系", ""),
            ""
        )
        theme = _str(
            kwargs.get("主题意图_承载", "")
            or kwargs.get("主题意图", "")
            or kwargs.get("主题", ""),
            ""
        )
        silence = _str(
            kwargs.get("留白意图_什么不该说", "")
            or kwargs.get("留白意图", "")
            or kwargs.get("留白", ""),
            ""
        )

        try:
            n_lines = int(kwargs.get("实际对白数", 8) or 8)
        except Exception:
            n_lines = 8
        try:
            silence_min = int(kwargs.get("沉默时长分钟", 3) or 3)
        except Exception:
            silence_min = 3
        try:
            pause_sec = int(kwargs.get("每句对白前停顿秒数", 2) or 2)
        except Exception:
            pause_sec = 2

        director = _str(kwargs.get("导演风格", "是枝裕和"), "是枝裕和")
        if not director or director == "auto":
            director = "是枝裕和"

        # ==========================================
        # 2. 灵魂注入 - 解析情感 keys + 权重 + 模式
        # ==========================================
        soul_emotion_keys = []
        primary = _str(kwargs.get("灵魂_主导情感", "auto"), "auto")
        if primary and primary not in ["auto", "none", ""]:
            soul_emotion_keys.append(primary)
        for i in range(1, 5):
            key = "灵魂_次要情感_{0}".format(i)
            val = _str(kwargs.get(key, "none"), "none")
            if val and val not in ["none", "auto", ""]:
                soul_emotion_keys.append(val)

        soul_weights = [float(kwargs.get("灵魂_主导权重", 1.0) or 1.0)]
        if len(soul_emotion_keys) > 1:
            remaining = max(0.0, 1.0 - soul_weights[0])
            n_remaining = len(soul_emotion_keys) - 1
            for _ in range(n_remaining):
                soul_weights.append(remaining / n_remaining if n_remaining else 0.0)

        soul_mode = _str(kwargs.get("灵魂_融合模式", "auto"), "auto")

        # ==========================================
        # 3. 计算灵魂融合
        # ==========================================
        if _HAS_SOUL and soul_emotion_keys:
            try:
                soul_fused = fuse_emotions(soul_emotion_keys, soul_weights, soul_mode)
            except Exception:
                soul_fused = None
        else:
            soul_fused = None

        if not soul_fused:
            # 兜底: 根据 director 决定默认融合
            default_emotions = {
                "王家卫": "longing",
                "诺兰": "anticipation_vigilance",
                "PTA": "tension",
                "奉俊昊": "disgust_loathing",
                "黑泽明": "tension",
                "库斯杜力卡": "bittersweet",
                "塔可夫斯基": "loneliness",
                "约阿希姆·提尔": "remorse",
                "是枝裕和": "tenderness",
                "侯孝贤": "loneliness",
                "伯格曼": "sadness_gloominess",
                "小津": "joy_serenity",
                "蔡明亮": "loneliness",
                "李沧东": "sadness_sorrow",
                "库布里克": "fear_apprehension",
                "毕赣": "longing",
                "贾樟柯": "nostalgia",
                "李安": "tenderness",
            }
            default_key = default_emotions.get(director, "loneliness")
            if _HAS_SOUL:
                try:
                    soul_fused = fuse_emotions([default_key], [1.0], "F1_单情感主导")
                except Exception:
                    soul_fused = {
                        "name": "Loneliness 孤独",
                        "fusion_mode": "F1_单情感主导",
                        "emotions": [default_key],
                        "weights": [1.0],
                        "intensity": 0.7,
                        "polarity": "negative",
                        "arousal": "low",
                        "description": "渴望连接但无连接的状态",
                        "visual_signs": "身体蜷缩, 视线远眺, 经常独自一人",
                        "voice_signs": "经常沉默, 偶发自言自语",
                        "facial_au": "AU1+AU4+AU15+AU43",
                        "inner_monologue": "有谁在听吗",
                        "color_palette": "冷蓝, 苍白, 灰",
                        "music_tempo": "40 BPM, 单音钢琴",
                    }
            else:
                soul_fused = {
                    "name": "Loneliness 孤独",
                    "fusion_mode": "F1_单情感主导",
                    "emotions": [default_key],
                    "weights": [1.0],
                    "intensity": 0.7,
                    "polarity": "negative",
                    "arousal": "low",
                    "description": "渴望连接但无连接的状态",
                    "visual_signs": "身体蜷缩, 视线远眺",
                    "voice_signs": "经常沉默",
                    "facial_au": "AU1+AU4+AU15+AU43",
                    "inner_monologue": "有谁在听吗",
                    "color_palette": "冷蓝, 苍白, 灰",
                    "music_tempo": "40 BPM",
                }

        # ==========================================
        # 4. 灵魂维度 + 灵魂状态
        # ==========================================
        soul_dims = {
            "creativity": float(kwargs.get("灵魂_创造力", 0.85) or 0.85),
            "imagination": float(kwargs.get("灵魂_想象力", 0.85) or 0.85),
            "artistic_expression": float(kwargs.get("灵魂_艺术表达", 0.85) or 0.85),
            "camera_skill": float(kwargs.get("灵魂_镜头技巧", 0.85) or 0.85),
            "atmosphere_control": float(kwargs.get("灵魂_氛围掌控", 0.85) or 0.85),
            "inspiration": float(kwargs.get("灵魂_灵感指数", 0.85) or 0.85),
            "rebelliousness": float(kwargs.get("灵魂_叛逆指数", 0.70) or 0.70),
            "self_doubt": float(kwargs.get("灵魂_怀疑指数", 0.50) or 0.50),
            "breakthrough_courage": 0.85,
        }

        story_intensity = float(kwargs.get("故事强度", 0.5) or 0.5)
        scene_progress = float(kwargs.get("场景进度", 0.0) or 0.0)

        soul_state = {
            "inspiration": float(kwargs.get("灵魂_灵感指数", 0.85) or 0.85),
            "fatigue": float(kwargs.get("灵魂_疲劳指数", 0.30) or 0.30),
            "doubt": float(kwargs.get("灵魂_怀疑指数", 0.50) or 0.50),
            "rebelliousness": float(kwargs.get("灵魂_叛逆指数", 0.70) or 0.70),
            "mental_state": "lucid" if float(kwargs.get("灵魂_怀疑指数", 0.50) or 0.50) < 0.5 else "anxious-dreamy",
        }

        # ==========================================
        # 5. 动态生成 5 维意图
        # ==========================================
        feeling_intent = _build_feeling_intent(soul_fused, scene, char_a, char_b, director)
        emotion_intent = _build_emotion_intent(soul_fused, char_a, char_b, director)
        relationship_intent = _build_relationship_intent(soul_fused, char_a, char_b, scene, director)
        theme_intent = _build_theme_intent(soul_fused, scene, theme, director)
        silence_intent = _build_silence_intent(soul_fused, n_lines, silence_min, pause_sec, char_a, char_b, director)

        # ==========================================
        # 6. 灵魂融合层
        # ==========================================
        soul_fusion_section = _build_soul_fusion_section(soul_fused, soul_dims, soul_state, director)

        # ==========================================
        # 7. 5 要素架构
        # ==========================================
        five_elements_section = _build_5_elements_section(
            soul_fused, scene, char_a, char_b, theme, relation, emotion, silence_min
        )

        # ==========================================
        # 7.5 灵魂深度处理 (Phase 17 核心)
        # ==========================================
        soul_deep_section = _build_soul_deep_processing_section(
            soul_fused, soul_dims, soul_state, director, char_a, char_b, scene
        )

        # ==========================================
        # 8. 11 维导演控制
        # ==========================================
        control_11_section = _build_11_control_section(soul_fused, soul_dims, soul_state, director, scene)

        # ==========================================
        # 9. 3 留白 + 3 运镜
        # ==========================================
        three_silence_motion = _build_3silence_3motion_section(soul_fused, director, scene)

        # ==========================================
        # 10. 8 顶级导演 + 15 真实意图样本
        # ==========================================
        directors_section = _build_directors_section(director, soul_fused)

        # ==========================================
        # 11. H3 三大字段
        # ==========================================
        h3_section = _build_h3_section(soul_fused, scene, char_a, char_b, director)

        # ==========================================
        # 12. 拼接完整意图陈述
        # ==========================================
        statement = """【{scene_type} - 导演意图陈述 (灵魂注入版)】

场景: {scene}
角色: {char_a} / {char_b}
导演灵魂: {director}
主导情感: {emotion_name} ({polarity}, 强度 {intensity:.2f})
融合模式: {fusion_mode}

════════════════════════════════════════
【5 大维度导演意图 - 灵魂驱动】
════════════════════════════════════════

{feeling_intent}

{emotion_intent}

{relationship_intent}

{theme_intent}

{silence_intent}

════════════════════════════════════════
【用户输入的 5 维意图 (作为补充)】
════════════════════════════════════════

- 感受: {feeling}
- 情感: {emotion}
- 关系: {relation}
- 主题: {theme}
- 留白: {silence}

════════════════════════════════════════

{soul_fusion_section}

{five_elements_section}

{soul_deep_section}

{control_11_section}

{three_silence_motion}

{directors_section}

{h3_section}

════════════════════════════════════════
【核心哲学: 导演会怎么描述自己的意图】
════════════════════════════════════════

不是描述"画面里有什么", 而是描述"导演会怎么描述自己的意图"。

- 我希望观众看到这个镜头以后会难过。
- 我希望这个角色看起来在笑, 眼神里却有一点犹豫。
- 我希望两个人之间的沉默, 成为推动剧情的一部分。

附件核心: 5 维意图 + 沉默/留白 5 规则 + 191 反 AI 词表 + 灵魂融合
""".format(
            scene_type=scene_type,
            scene=scene or "未指定",
            char_a=char_a or "角色 A",
            char_b=char_b or "角色 B",
            director=director,
            emotion_name=soul_fused.get("name", "未指定"),
            polarity=soul_fused.get("polarity", "neutral"),
            intensity=soul_fused.get("intensity", 0.5),
            fusion_mode=soul_fused.get("fusion_mode", "未指定"),
            feeling_intent=feeling_intent,
            emotion_intent=emotion_intent,
            relationship_intent=relationship_intent,
            theme_intent=theme_intent,
            silence_intent=silence_intent,
            feeling=feeling or "(由灵魂融合层动态生成)",
            emotion=emotion or "(由灵魂融合层动态生成)",
            relation=relation or "(由灵魂融合层动态生成)",
            theme=theme or "(由灵魂融合层动态生成)",
            silence=silence or "(由灵魂融合层动态生成)",
            soul_fusion_section=soul_fusion_section,
            five_elements_section=five_elements_section,
            soul_deep_section=soul_deep_section,
            control_11_section=control_11_section,
            three_silence_motion=three_silence_motion,
            directors_section=directors_section,
            h3_section=h3_section,
        )

        # ==========================================
        # 13. 15 导演意图样本 (第二输出) - 大幅扩展
        # ==========================================
        # 真实电影案例 (用于每个导演的深度分析)
        DIRECTOR_CASE_STUDIES = {
            "王家卫": [
                ("《花样年华》(2000)", "走廊里的擦肩而过, 60s 慢镜头, 时间戳, 两个人都不说话"),
                ("《重庆森林》(1994)", "何志武独白, 凤梨罐头的保质期, 0.01 秒的接近"),
                ("《春光乍泄》(1997)", "黎耀辉在瀑布前, 思念是物理的远"),
                ("《一代宗师》(2013)", "叶问的'念念不忘, 必有回响', 时间即情敌"),
            ],
            "诺兰": [
                ("《盗梦空间》(2010)", "火车冲入街道, 物理空间即主题, 陀螺的悬念"),
                ("《记忆碎片》(2000)", "倒叙, 照片, 失忆的主角, 时间即敌人"),
                ("《黑暗骑士》(2008)", "小丑的双船实验, 道德困境无答案"),
                ("《信条》(2020)", "时间逆转, 物理可解释的时间机制"),
            ],
            "PTA": [
                ("《血色将至》(2007)", "石油和牛奶, 慢推长焦, 父权崩塌"),
                ("《魅影缝匠》(2017)", "Reynolds 在餐厅崩溃, 凝视 5 秒, 控制与被控制"),
                ("《不羁夜》(1997)", "70s 迷幻, 派对高潮, 录音棚里的凝视"),
                ("《木兰花》(1999)", "多线叙事, 蛙雨, 父女重逢"),
            ],
            "奉俊昊": [
                ("《寄生虫》(2019)", "楼梯即命运, 暴雨倒流, 廉价香水的气味"),
                ("《雪国列车》(2013)", "列车即阶层, 不可逾越的边界"),
                ("《杀人回忆》(2003)", "雨夜, 凝视, 道德困境"),
                ("《母亲》(2009)", "母爱, 误杀, 雨"),
            ],
            "黑泽明": [
                ("《七武士》(1954)", "雨, 群戏调度, 多机位"),
                ("《罗生门》(1950)", "道德困境, 同一个事件 4 个视角"),
                ("《乱》(1985)", "天气即角色, 莎士比亚改编"),
                ("《梦》(1990)", "8 个梦, 每个梦都是道德寓言"),
            ],
            "库斯杜力卡": [
                ("《地下》(1995)", "塞尔维亚的乡愁, 动物, 失序中的诗意"),
                ("《黑猫白猫》(1998)", "婚礼, 狂欢, 吉普赛"),
                ("《爸爸去出差》(1985)", "童年视角, 父亲的缺席"),
            ],
            "塔可夫斯基": [
                ("《飞向太空》(1972)", "宇宙的彻底静谧, 长镜头 7 分钟"),
                ("《镜子》(1975)", "时间即主角, 童年的房间"),
                ("《牺牲》(1986)", "献祭, 火, 风的形态"),
                ("《乡愁》(1983)", "一滴水能撑 2 分钟"),
            ],
            "约阿希姆·提尔": [
                ("《情感价值》(2025)", "房子视角, 家庭代际, 父亲的椅子"),
                ("《世界上最糟糕的人》(2021)", "代际, 迷茫, 北欧光"),
                ("《八月三十一日》(2011)", "一天, 整部电影, 安静中藏风暴"),
                ("《奥斯陆, 8月31日》(2011)", "北欧光, 安静"),
            ],
        }

        samples_output_lines = []
        samples_output_lines.append("════════════════════════════════════════")
        samples_output_lines.append("【15 导演真实意图样本 - 灵魂驱动版 v2】")
        samples_output_lines.append("════════════════════════════════════════")
        samples_output_lines.append("")
        samples_output_lines.append("当前导演: {0}".format(director))
        samples_output_lines.append("当前主导情感: {0}".format(soul_fused.get("name", "未指定")))
        samples_output_lines.append("当前极性: {0}".format(soul_fused.get("polarity", "neutral")))
        samples_output_lines.append("当前强度: {0:.2f}".format(soul_fused.get("intensity", 0.5)))
        samples_output_lines.append("当前融合模式: {0}".format(soul_fused.get("fusion_mode", "未指定")))
        samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 1 部分: 15 导演真实意图样本 (DIRECTOR_INTENT_SAMPLES)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        samples_output_lines.append("说明: 15 位导演的'自我描述', 即他们会怎么描述自己的创作意图。")
        samples_output_lines.append("这是从 60+ 导演访谈、幕后纪录片、剧本注释中提炼的'灵魂语录'。")
        samples_output_lines.append("")
        for i, (d, intent) in enumerate(DIRECTOR_INTENT_SAMPLES.items(), 1):
            marker = "★ 当前" if d == director else "  "
            samples_output_lines.append("{0} {1:>2}. {2:<12}: {3}".format(marker, i, d, intent))
        samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 2 部分: 18 导演灵魂签名 (含 8 大顶级)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        for i, (d, sig) in enumerate(DIRECTOR_SOUL_SIGNATURES_8.items(), 1):
            marker = "★ 当前" if d == director else "  "
            samples_output_lines.append("{0} {1}. {2} ({3})".format(marker, i, d, sig.get("name_en", "")))
            samples_output_lines.append("   签名: {0}".format(sig.get("signature", "")))
            samples_output_lines.append("   高级原型: {0}".format(sig.get("higher_archetype", "")))
            samples_output_lines.append("   物件隐喻: {0}".format(sig.get("object_metaphor", "")))
            samples_output_lines.append("   时间逻辑: {0}".format(sig.get("time_logic", "")))
            samples_output_lines.append("   视觉语法: {0}".format(sig.get("visual_grammar", "")))
            samples_output_lines.append("   沉默形式: {0}".format(sig.get("silence_form", "")))
            samples_output_lines.append("   空间原型: {0}".format(sig.get("horizon", "")))
            samples_output_lines.append("   内心独白风格: {0}".format(sig.get("inner_speech", "")))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 3 部分: 真实电影案例研究 (Case Studies)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        samples_output_lines.append("每个导演的 2-4 部代表作品 + 关键场景的导演意图解读。")
        samples_output_lines.append("这些案例直接驱动 5 维意图的生成。")
        samples_output_lines.append("")
        for d, cases in DIRECTOR_CASE_STUDIES.items():
            marker = "★ 当前" if d == director else "  "
            samples_output_lines.append("{0} {1} 的代表作品:".format(marker, d))
            for film, scene in cases:
                samples_output_lines.append("   • {0}".format(film))
                samples_output_lines.append("     关键场景: {0}".format(scene))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 4 部分: 8 顶级导演 × 11 维控制 交叉矩阵")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        samples_output_lines.append("每个导演的 11 维控制的'偏好设定', 用于驱动 5 维意图。")
        samples_output_lines.append("")
        # 简化版 11 维矩阵
        matrix_11 = {
            "空镜": {"王家卫": "60s 慢推空镜", "诺兰": "建筑全景", "PTA": "凝视 5 秒", "奉俊昊": "雨景", "黑泽明": "天气", "库斯杜力卡": "动物", "塔可夫斯基": "物质 (水/火/风)", "约阿希姆·提尔": "房间"},
            "留白": {"王家卫": "60% 沉默", "诺兰": "物理空间沉默", "PTA": "凝视沉默", "奉俊昊": "雨声沉默", "黑泽明": "天气沉默", "库斯杜力卡": "动物沉默", "塔可夫斯基": "物质沉默", "约阿希姆·提尔": "房间沉默"},
            "氛围": {"王家卫": "60s 暖黄 + 抽帧", "诺兰": "IMAX 客观", "PTA": "70s 暖黄 + 长焦", "奉俊昊": "雨夜 + 纵深", "黑泽明": "天气 + 极清晰", "库斯杜力卡": "巴洛克调度", "塔可夫斯基": "诗意朦胧", "约阿希姆·提尔": "北欧光"},
            "悬疑": {"王家卫": "错过悬念", "诺兰": "物理悬念", "PTA": "权力悬念", "奉俊昊": "阶层悬念", "黑泽明": "道德悬念", "库斯杜力卡": "混乱悬念", "塔可夫斯基": "存在悬念", "约阿希姆·提尔": "代际悬念"},
            "多线": {"王家卫": "时间多线", "诺兰": "结构多线", "PTA": "角色多线", "奉俊昊": "空间多线", "黑泽明": "群像多线", "库斯杜力卡": "群像 + 时间", "塔可夫斯基": "意识多线", "约阿希姆·提尔": "代际多线"},
            "反转": {"王家卫": "无反转 (错过即反转)", "诺兰": "结构反转", "PTA": "权力反转", "奉俊昊": "类型反转", "黑泽明": "道德反转", "库斯杜力卡": "混乱反转", "塔可夫斯基": "时间反转", "约阿希姆·提尔": "代际反转"},
            "高潮": {"王家卫": "60s 慢推到极致", "诺兰": "IMAX 全景高潮", "PTA": "凝视爆发", "奉俊昊": "空间爆发", "黑泽明": "天气高潮", "库斯杜力卡": "狂欢高潮", "塔可夫斯基": "物质高潮", "约阿希姆·提尔": "房间高潮"},
            "余韵": {"王家卫": "长余韵 (几个月)", "诺兰": "结构余韵", "PTA": "权力余韵", "奉俊昊": "阶层余韵", "黑泽明": "道德余韵", "库斯杜力卡": "乡愁余韵", "塔可夫斯基": "时间余韵", "约阿希姆·提尔": "代际余韵"},
            "节奏": {"王家卫": "极慢", "诺兰": "史诗节奏", "PTA": "70s 节奏", "奉俊昊": "类型节奏", "黑泽明": "群像节奏", "库斯杜力卡": "狂欢节奏", "塔可夫斯基": "长镜头节奏", "约阿希姆·提尔": "北欧节奏"},
            "感情": {"王家卫": "压抑 + 释放", "诺兰": "认知 + 震撼", "PTA": "凝视 + 爆发", "奉俊昊": "压抑 + 阶层爆发", "黑泽明": "道德 + 自然", "库斯杜力卡": "狂欢 + 乡愁", "塔可夫斯基": "物质 + 记忆", "约阿希姆·提尔": "代际 + 安静"},
            "角色": {"王家卫": "物件 + 时间戳", "诺兰": "建筑 + 行为", "PTA": "可观察行为", "奉俊昊": "空间 + 气味", "黑泽明": "天气 + 道德", "库斯杜力卡": "动物 + 狂欢", "塔可夫斯基": "物质 + 记忆", "约阿希姆·提尔": "房间 + 代际"},
        }
        for dim, dim_map in matrix_11.items():
            samples_output_lines.append("【{dim}】".format(dim=dim))
            for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
                marker = "★" if d == director else " "
                samples_output_lines.append("  {0} {1:<10}: {2}".format(marker, d, dim_map.get(d, "默认")))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 5 部分: 当前导演的深度灵魂解读")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        if director in DIRECTOR_SOUL_SIGNATURES_8:
            sig = DIRECTOR_SOUL_SIGNATURES_8[director]
            samples_output_lines.append("★ 导演: {0} ({1})".format(director, sig.get("name_en", "")))
            samples_output_lines.append("")
            samples_output_lines.append("  核心签名: {0}".format(sig.get("signature", "")))
            samples_output_lines.append("  高级原型: {0}".format(sig.get("higher_archetype", "")))
            samples_output_lines.append("  视觉语法: {0}".format(sig.get("visual_grammar", "")))
            samples_output_lines.append("  时间逻辑: {0}".format(sig.get("time_logic", "")))
            samples_output_lines.append("  物件隐喻: {0}".format(sig.get("object_metaphor", "")))
            samples_output_lines.append("  沉默形式: {0}".format(sig.get("silence_form", "")))
            samples_output_lines.append("  空间原型: {0}".format(sig.get("horizon", "")))
            samples_output_lines.append("  内心独白风格: {0}".format(sig.get("inner_speech", "")))
            samples_output_lines.append("")
            samples_output_lines.append("  真实电影案例:")
            for film, scene in DIRECTOR_CASE_STUDIES.get(director, []):
                samples_output_lines.append("    • {0}".format(film))
                samples_output_lines.append("      关键场景: {0}".format(scene))
            samples_output_lines.append("")
            samples_output_lines.append("  真实意图样本:")
            samples_output_lines.append("    \"{0}\"".format(DIRECTOR_INTENT_SAMPLES.get(director, "")))
            samples_output_lines.append("")
            # 当前灵魂如何与导演灵魂交叉
            samples_output_lines.append("  当前灵魂 × 导演灵魂 交叉分析:")
            samples_output_lines.append("    主导情感: {0}".format(soul_fused.get("name", "未指定")))
            samples_output_lines.append("    极性: {0}".format(soul_fused.get("polarity", "neutral")))
            samples_output_lines.append("    强度: {0:.2f}".format(soul_fused.get("intensity", 0.5)))
            samples_output_lines.append("    融合模式: {0}".format(soul_fused.get("fusion_mode", "未指定")))
            samples_output_lines.append("")
            samples_output_lines.append("  交叉点:")
            samples_output_lines.append("    - {0} 的物件隐喻 vs 当前情感: {1}".format(
                director, sig.get("object_metaphor", "")))
            samples_output_lines.append("    - {0} 的沉默形式 vs 当前情感: {1}".format(
                director, sig.get("silence_form", "")))
            samples_output_lines.append("    - {0} 的时间逻辑 vs 当前情感: {1}".format(
                director, sig.get("time_logic", "")))
            samples_output_lines.append("    - {0} 的空间原型 vs 当前情感: {1}".format(
                director, sig.get("horizon", "")))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 6 部分: 3 留白 + 3 运镜 - 8 导演偏好")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        silence_motion_pref = {
            "王家卫": {"物件留白": "凤梨罐头代替时间", "时间留白": "60s 慢镜头", "沉默留白": "一句话撑 30 秒", "推近": "60s 慢推, 揭示内心", "后拉": "走廊里拉远", "横移": "手摇摄影, 60s"},
            "诺兰": {"物件留白": "陀螺代替真伪", "时间留白": "倒叙空白", "沉默留白": "物理空间沉默", "推近": "长焦压缩 + 凝视", "后拉": "IMAX 全景, 史诗感", "横移": "长焦平行, 时间流逝"},
            "PTA": {"物件留白": "石油代替权力", "时间留白": "凝视 5 秒", "沉默留白": "凝视即沉默", "推近": "慢推长焦, 凝视 5 秒", "后拉": "揭示权力空间", "横移": "70s 平行, 时间凝固"},
            "奉俊昊": {"物件留白": "石头代替阶层", "时间留白": "雨声沉默", "沉默留白": "雨声沉默 10 分钟", "推近": "特写脸 + 雨声", "后拉": "固定 + 纵深, 阶层", "横移": "楼梯上的纵向"},
            "黑泽明": {"物件留白": "天气代替情绪", "时间留白": "雨突然停了", "沉默留白": "天气沉默 30 秒", "推近": "道德凝视", "后拉": "人在天地间", "横移": "多机位群戏"},
            "库斯杜力卡": {"物件留白": "动物代替乡愁", "时间留白": "鸡走过 5 秒", "沉默留白": "动物沉默", "推近": "混乱中的凝视", "后拉": "狂欢中的远景", "横移": "手持 + 群戏 + 巴洛克"},
            "塔可夫斯基": {"物件留白": "物质代替记忆", "时间留白": "一滴水 2 分钟", "沉默留白": "物质沉默", "推近": "长镜头 1-7 分钟", "后拉": "空间揭示", "横移": "诗意朦胧"},
            "约阿希姆·提尔": {"物件留白": "房子代替代际", "时间留白": "空房间 2 分钟", "沉默留白": "房间沉默", "推近": "长焦 + 安静", "后拉": "从房间到整栋楼", "横移": "北欧光平行"},
        }
        for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
            marker = "★" if d == director else " "
            samples_output_lines.append("{0} {1}:".format(marker, d))
            for k, v in silence_motion_pref.get(d, {}).items():
                samples_output_lines.append("    {0}: {1}".format(k, v))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 7 部分: 8 导演的灵魂维度分布 (1-10 评分)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        # 灵魂维度 × 8 导演 矩阵
        director_dims_matrix = {
            "王家卫": {"创造力": 9.5, "想象力": 9.0, "艺术表达": 10.0, "镜头技巧": 8.5, "氛围掌控": 9.5, "叛逆度": 8.0, "自我怀疑": 7.0, "突破勇气": 8.0},
            "诺兰": {"创造力": 8.0, "想象力": 9.5, "艺术表达": 7.5, "镜头技巧": 9.5, "氛围掌控": 9.0, "叛逆度": 6.0, "自我怀疑": 5.0, "突破勇气": 9.0},
            "PTA": {"创造力": 9.5, "想象力": 8.0, "艺术表达": 9.5, "镜头技巧": 9.5, "氛围掌控": 9.0, "叛逆度": 7.5, "自我怀疑": 8.0, "突破勇气": 8.5},
            "奉俊昊": {"创造力": 9.0, "想象力": 8.5, "艺术表达": 8.5, "镜头技巧": 9.0, "氛围掌控": 9.0, "叛逆度": 8.5, "自我怀疑": 6.0, "突破勇气": 9.0},
            "黑泽明": {"创造力": 9.0, "想象力": 8.0, "艺术表达": 9.0, "镜头技巧": 9.5, "氛围掌控": 9.5, "叛逆度": 5.5, "自我怀疑": 4.0, "突破勇气": 7.0},
            "库斯杜力卡": {"创造力": 9.0, "想象力": 9.5, "艺术表达": 9.0, "镜头技巧": 8.0, "氛围掌控": 9.0, "叛逆度": 8.5, "自我怀疑": 5.0, "突破勇气": 8.5},
            "塔可夫斯基": {"创造力": 9.5, "想象力": 9.5, "艺术表达": 10.0, "镜头技巧": 9.0, "氛围掌控": 9.5, "叛逆度": 9.0, "自我怀疑": 8.5, "突破勇气": 9.5},
            "约阿希姆·提尔": {"创造力": 8.5, "想象力": 8.0, "艺术表达": 9.0, "镜头技巧": 8.5, "氛围掌控": 9.0, "叛逆度": 6.0, "自我怀疑": 7.0, "突破勇气": 7.0},
        }
        # 输出表头
        header = "  维度       "
        for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
            header += "{0:<8}".format(d[:6])
        samples_output_lines.append(header)
        samples_output_lines.append("  " + "─" * 80)
        for dim in ["创造力", "想象力", "艺术表达", "镜头技巧", "氛围掌控", "叛逆度", "自我怀疑", "突破勇气"]:
            row = "  {0:<10}".format(dim)
            for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
                v = director_dims_matrix.get(d, {}).get(dim, 8.0)
                row += "{0:<8}".format("{:.1f}".format(v))
            samples_output_lines.append(row)
        samples_output_lines.append("")
        samples_output_lines.append("  说明: 8 顶级导演的灵魂维度评分 (1-10), 用于驱动 5 维意图的深度。")
        samples_output_lines.append("  每个导演的'灵魂签名'是其维度的'风格化'表达。")
        samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 8 部分: 8 导演的 60+ 情感使用频率")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        # 60+ 情感 × 8 导演 使用频率
        emotion_freq = {
            "王家卫": {"loneliness": 0.95, "longing": 0.90, "bittersweet": 0.85, "nostalgia": 0.80, "tenderness": 0.70, "joy_serenity": 0.40, "sadness_sorrow": 0.60, "remorse": 0.50},
            "诺兰": {"tension": 0.95, "anticipation_vigilance": 0.90, "fear_apprehension": 0.80, "loneliness": 0.40, "surprise_astonishment": 0.70, "anger_frustration": 0.50, "hope": 0.40},
            "PTA": {"tension": 0.90, "disgust_revulsion": 0.80, "hate": 0.70, "anger_fury": 0.60, "sadness_grief": 0.60, "fear_apprehension": 0.50, "contempt": 0.85, "pride": 0.60},
            "奉俊昊": {"tension": 0.90, "disgust_loathing": 0.85, "fear_apprehension": 0.70, "anger_frustration": 0.80, "contempt": 0.75, "shame": 0.50},
            "黑泽明": {"tension": 0.85, "fear_terror": 0.70, "anger_fury": 0.70, "sadness_grief": 0.65, "awe": 0.60, "guilt": 0.55},
            "库斯杜力卡": {"bittersweet": 0.90, "joy_ecstasy": 0.85, "sadness_sorrow": 0.80, "tenderness": 0.70, "longing": 0.75, "nostalgia": 0.80},
            "塔可夫斯基": {"loneliness": 0.95, "longing": 0.85, "nostalgia": 0.80, "awe": 0.75, "despair": 0.70, "tenderness": 0.60, "remorse": 0.65},
            "约阿希姆·提尔": {"tenderness": 0.90, "bittersweet": 0.85, "remorse": 0.80, "nostalgia": 0.75, "loneliness": 0.60, "guilt": 0.70, "shyness": 0.55},
        }
        # 输出表头
        emotion_keys_used = list(set([k for d in emotion_freq.values() for k in d.keys()]))
        emotion_keys_used = sorted(emotion_keys_used)
        header = "  情感         "
        for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
            header += "{0:<6}".format(d[:4])
        samples_output_lines.append(header)
        samples_output_lines.append("  " + "─" * 60)
        for emo in emotion_keys_used:
            row = "  {0:<13}".format(emo[:11])
            for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
                v = emotion_freq.get(d, {}).get(emo, 0.0)
                if v > 0:
                    row += "{0:<6}".format("{:.1f}".format(v))
                else:
                    row += "{0:<6}".format("-")
            samples_output_lines.append(row)
        samples_output_lines.append("")
        samples_output_lines.append("  说明: 8 顶级导演的 60+ 情感使用频率 (0-1), 用于驱动情感意图。")
        samples_output_lines.append("  例如: 王家卫 95% 用 loneliness, 90% 用 longing。")
        samples_output_lines.append("  当前导演 ({0}) 主导情感 ({1}) 的使用频率: {2}".format(
            director,
            soul_fused.get("name", "未指定"),
            emotion_freq.get(director, {}).get(soul_fused.get("emotions", ["loneliness"])[0] if soul_fused.get("emotions") else "loneliness", 0.5),
        ))
        samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 9 部分: 当前导演的'灵魂 vs 主导情感'深度交叉")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        current_emo = soul_fused.get("emotions", ["loneliness"])
        if current_emo:
            current_emo_key = current_emo[0]
            current_freq = emotion_freq.get(director, {}).get(current_emo_key, 0.5)
            current_intensity = soul_fused.get("intensity", 0.5)
            samples_output_lines.append("  主导情感: {0}".format(soul_fused.get("name", "未指定")))
            samples_output_lines.append("  情感 key: {0}".format(current_emo_key))
            samples_output_lines.append("  {0} 对该情感的使用频率: {1:.2f}".format(director, current_freq))
            samples_output_lines.append("  当前强度: {0:.2f}".format(current_intensity))
            samples_output_lines.append("")
            if current_freq > 0.7:
                cross_analysis = "高度契合: {0} 经常使用 {1}, 本场戏是他的'主场'".format(director, current_emo_key)
            elif current_freq > 0.4:
                cross_analysis = "中等契合: {0} 偶尔使用 {1}, 本场戏需要刻意经营".format(director, current_emo_key)
            else:
                cross_analysis = "低度契合: {0} 极少使用 {1}, 本场戏需要重新定义".format(director, current_emo_key)
            samples_output_lines.append("  交叉分析: {0}".format(cross_analysis))
            samples_output_lines.append("")
            # 给出建议
            if current_freq > 0.7 and current_intensity > 0.6:
                suggestion = "建议: 大胆使用 {0} 的标准手法, 例如 {1}".format(
                    director, silence_motion_pref.get(director, {}).get("物件留白", "默认"))
            elif current_freq > 0.4:
                suggestion = "建议: 结合 {0} 的偏好, 例如 {1}".format(
                    director, silence_motion_pref.get(director, {}).get("时间留白", "默认"))
            else:
                suggestion = "建议: 重新定义 {0} 的标准手法, 创造新的语言".format(director)
            samples_output_lines.append("  {0}".format(suggestion))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 10 部分: 8 导演的'关键场景模型' (Key Scene Patterns)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        key_scene_patterns = {
            "王家卫": [
                "走廊擦肩: 两个人在走廊擦肩, 60s 慢镜头, 谁都不说话",
                "凤梨罐头: 一句'不知道从什么时候开始, 任何东西都有日期', 罐头代替时间",
                "电话亭: 何志武在电话亭旁, 雨, 0.01 秒的接近",
                "高跟鞋: 一双高跟鞋走过走廊, 脚步声撑 30 秒",
            ],
            "诺兰": [
                "陀螺: 结尾陀螺是否倒下, 时间即敌人",
                "倒叙: 倒叙 + 黑白彩色切换, 时间即认知",
                "建筑: 走廊的尽头, 一个人走远, 30 秒",
                "IMAX 全景: 山, 雪, 海, 人在天地间",
            ],
            "PTA": [
                "凝视 5 秒: Daniel 看 Eli, 慢推长焦, 凝视撑 5 秒",
                "石油: 钻头喷出石油, 权力即液体",
                "录音棚: 一根录音带, 控制即声音",
                "钢琴: Reynolds 在钢琴前崩溃, 凝视爆发",
            ],
            "奉俊昊": [
                "楼梯: 两个人在不同楼梯上对视, 30 秒, 阶层即高度",
                "雨: 一场雨撑 10 分钟, 雨声沉默",
                "门铃: 门铃响, 10 秒, 谁都不开",
                "桃子: 桃子代替阶层, 穷人吃不起",
            ],
            "黑泽明": [
                "雨: 雨突然停了, 30 秒, 道德悬念",
                "剑: 武士拔剑的瞬间, 群戏调度",
                "镜子: 镜中的自己, 道德审判",
                "鸟: 一群鸟飞过, 命运即天气",
            ],
            "库斯杜力卡": [
                "动物: 一只鸡走过两个人中间, 5 秒",
                "婚礼: 婚礼上的混乱, 巴洛克调度",
                "酒: 酒洒在桌上, 流下来, 10 秒",
                "葬礼: 葬礼上的动物, 乡愁即死亡",
            ],
            "塔可夫斯基": [
                "水滴: 一滴水从天花板落下, 2 分钟, 长镜头",
                "蜡烛: 一根蜡烛烧到底, 1 分钟, 镜头不动",
                "火: 火从木头燃起, 30 秒, 物质即记忆",
                "童年: 童年房间, 长镜头, 时间即主角",
            ],
            "约阿希姆·提尔": [
                "窗: 窗外的光线移动, 1 分钟, 北欧光",
                "椅子: 父亲看着空椅子, 30 秒",
                "钢琴: 钢琴盖打开, 没人弹, 20 秒",
                "房子: 整栋楼拉远, 代际即空间",
            ],
        }
        for d, patterns in key_scene_patterns.items():
            marker = "★" if d == director else " "
            samples_output_lines.append("{0} {1} 的关键场景模型:".format(marker, d))
            for p in patterns:
                samples_output_lines.append("    • {0}".format(p))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 11 部分: 8 导演的'反 AI 风格特征' (Style Anti-AI)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        # 每个导演的'反 AI 风格' 是什么
        director_anti_ai = {
            "王家卫": "不用形容词, 用时间戳 (2024 年 4 月 16 日下午 3 点 03 分); 不用情绪, 用物件 (凤梨罐头); 不用 happy ending, 用错过",
            "诺兰": "不用情绪化, 用物理 (时间机制); 不用解释, 用结构; 不用 happy ending, 用真相",
            "PTA": "不用情绪化, 用可观察行为 (手的位置, 呼吸的节奏); 不用 happy ending, 用崩塌",
            "奉俊昊": "不用阶级斗争对白, 用空间 (楼梯); 不用情绪化, 用气味 (香水); 不用 happy ending, 用倒流",
            "黑泽明": "不用情绪化, 用天气 (雨/雪/风); 不用 happy ending, 用道德困境无答案",
            "库斯杜力卡": "不用情绪化, 用动物 (鸡/马/猪); 不用 happy ending, 用狂欢中的死亡",
            "塔可夫斯基": "不用情绪化, 用物质 (水/火/风); 不用 happy ending, 用时间即主角",
            "约阿希姆·提尔": "不用情绪化, 用房子 (空房间); 不用 happy ending, 用代际传承",
        }
        for d in DIRECTOR_SOUL_SIGNATURES_8.keys():
            marker = "★" if d == director else " "
            samples_output_lines.append("{0} {1}:".format(marker, d))
            samples_output_lines.append("    {0}".format(director_anti_ai.get(d, "默认")))
            samples_output_lines.append("")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("第 12 部分: 8 导演的'反 AI 词表' (Anti-AI Vocabulary)")
        samples_output_lines.append("─" * 60)
        samples_output_lines.append("")
        # 每个导演绝对不用的词
        anti_ai_vocab = {
            "王家卫": ["撕心裂肺", "五味杂陈", "绝美", "心中暗道", "缓缓", "陷入沉思", "缓缓地", "缓缓走向"],
            "诺兰": ["感人", "催泪", "煽情", "狗血", "虐恋", "撕心裂肺", "缓缓", "温柔地说"],
            "PTA": ["感动", "绝美", "缓缓", "心中暗道", "陷入沉思", "撕心裂肺", "温柔地", "轻轻地说"],
            "奉俊昊": ["感人", "绝美", "缓缓", "撕心裂肺", "温柔地", "轻轻地说", "陷入沉思"],
            "黑泽明": ["感人", "催泪", "撕心裂肺", "缓缓", "绝美", "陷入沉思", "心中暗道"],
            "库斯杜力卡": ["感人", "撕心裂肺", "缓缓", "绝美", "陷入沉思", "温柔地"],
            "塔可夫斯基": ["感人", "催泪", "撕心裂肺", "缓缓", "绝美", "陷入沉思", "心中暗道"],
            "约阿希姆·提尔": ["撕心裂肺", "缓缓", "绝美", "陷入沉思", "心中暗道", "温柔地", "轻轻地说"],
        }
        for d, vocab in anti_ai_vocab.items():
            marker = "★" if d == director else " "
            samples_output_lines.append("{0} {1} (禁用): {2}".format(marker, d, ", ".join(vocab)))
        samples_output_lines.append("")
        samples_output = "\n".join(samples_output_lines)

        # ==========================================
        # 14. 反 AI 清洗样本 (第三输出)
        # ==========================================
        if not _HAS_ANTI_AI:
            cleaned = "反 AI 模块未加载: " + _ANTI_AI_ERROR
        else:
            test_intent = "{0}陷入深深的沉思, 看着{1}绝美的脸庞, 撕心裂肺地喊了一声: 我想你。\n{2}心中暗道, 看着窗外, 眼角滑落泪水, 缓缓地转过头。".format(
                char_a or "父亲",
                char_b or "女儿",
                char_b or "女儿",
            )
            cleaned = clean_anti_ai_text(test_intent)

        # ==========================================
        # 15. 应用反 AI 规则
        # ==========================================
        if _HAS_ANTI_AI and kwargs.get("启用反AI规则", True):
            try:
                statement = inject_anti_ai_rules(statement)
            except Exception:
                pass

        # ==========================================
        # 16. 返回
        # ==========================================
        return (statement, samples_output, cleaned)


# ============================================================
# 节点注册
# ============================================================
# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "DirectorIntentPro": DirectorIntentPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "DirectorIntentPro": "🎯 导演意图 v2 (Phase 17 灵魂注入版)",
# }


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 17 - 导演意图 v2 (灵魂注入版) 测试")
    print("=" * 60)
    node = DirectorIntentPro()
    out = node.build_intent(
        场景类型="重逢",
        场景描述="父女在婚礼, 12 年未见",
        角色A="父亲 60 岁, 下岗工人",
        角色B="女儿 30 岁, 律师",
        感受意图_观众应感到="复杂, 难说清",
        情感意图_角色应有="想哭但不能哭",
        关系意图_此刻是="既想靠近又怕伤害",
        主题意图_承载="亲情的不可言说",
        留白意图_什么不该说="想说的话永远没说完",
        实际对白数=12,
        沉默时长分钟=5,
        每句对白前停顿秒数=3,
        灵魂_主导情感="longing",
        灵魂_次要情感_1="remorse",
        灵魂_次要情感_2="tenderness",
        灵魂_融合模式="F3_双情感对等融合",
        导演风格="王家卫",
        启用反AI规则=True,
    )
    print("\n输出 0 (intent_statement) 长度: {0}".format(len(out[0])))
    print("输出 1 (director_intent_samples) 长度: {0}".format(len(out[1])))
    print("输出 2 (anti_ai_cleaned) 长度: {0}".format(len(out[2])))
    print("\n--- intent_statement 前 3000 字符 ---")
    print(out[0][:3000])
    print("\n--- director_intent_samples ---")
    print(out[1][:2000])
