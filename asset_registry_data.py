# -*- coding: utf-8 -*-
"""
Phase 14 - 6 份核心文件 (Hell Grind 复刻)
================================================
Higgsfield Hell Grind 把整个生产流程压缩成 6 份文件。我们也建立同样的 6 份文件,
让 25 节点共享一个项目级"记忆"。

6 份文件 (The 6 Documents):
1. ASSET_REGISTRY  - 资产注册表 (角色/地点/道具, 标签+描述+参考图+状态版本+测试)
2. SCENE_MAP       - 场景地图 (固定地标/左右/距离/180° 轴线/光源方向)
3. ACTING_STATE    - 表演状态表 (5 支柱: 目标/障碍/代价/策略/转折)
4. SHOTLIST        - 分镜表 (镜号/时长/首帧/主要动作/台词/声音/资产)
5. VERSION_LOG     - 版本日志 (每版 prompt/唯一改动/生成结果/采用原因)
6. POST_ISSUE_LIST - 后期问题单 (手脸/文字/接缝/颜色/环境声/待补镜头)

这 6 份文件共同作用: 把创作者脑子里的项目记忆, 变成团队可读、模型可重载、失败可追溯的外部系统。

5 要素架构 (5 Elements):
- 数据         - 1161 部 + 63 导演 + 191 反 AI + 12 套理论 + 14 真实短剧
- 上下文缩略   - 类型/导演/主题/场景 1 句话
- Skill/Harness- 15 块刚性骨架 + 5 维意图 + 4 维美术 + 5 空间 + 5 沉默 + 6 份文件
- 经验矩阵     - Hell Grind 6 层生产系统 + 真实短剧实战
- AI 深度处理  - 反 AI 词表 + 10 铁律 + 4 轮迭代 + 11 维导演控制
"""

# ============================================================
# 1. ASSET_REGISTRY (资产注册表)
# ============================================================
ASSET_REGISTRY = {
    "schema": "asset_registry_v1",
    "description": "Higgsfield 风格资产注册表: 角色/地点/道具, 标签+描述+参考图+状态版本+测试",
    "characters": {
        "@roco": {
            "descriptor": "少年 16-18 岁, 中等偏瘦身材, 棕色卷发及肩, 左眉有竖疤, 穿深灰连帽衫配破旧牛仔裤, 双手大, 永远带一只旧帆布背包",
            "refs": {
                "face_closeup": "高对比人像, 中性灰背景, 平光, 真实毛孔, 眼睛带 catch-light",
                "front_full_no_head": "正面全身故意不带头部, 浅灰背景, 平光, 服装细节清晰",
                "back_full": "背面全身, 浅灰背景, 平光, 后颈/发型/包带/鞋底可见",
            },
            "states": {
                "@roco": "普通状态",
                "@roco_wet": "淋雨后, 衣服贴皮肤, 头发湿贴, 雨珠鼻尖",
                "@roco_blood": "受伤, 鼻血, 右肩有撕裂, 浅呼吸",
                "@roco_exhausted": "疲惫, 呼吸浅短, 右肩低, 眼神散",
                "@roco_determined": "坚定, 下颌绷紧, 眼神锁定目标, 身体前倾",
            },
            "voice": {
                "range": "tenor (男高音)",
                "timbre": "略带沙哑, 气息感重, 不饱满",
                "speed": "中速, 紧张时会加快",
                "accent": "伦敦东区街头口音",
                "habit": "语尾常带吞音, 'gonna'/'wanna'/'gotta'",
                "pressure_change": "压力下音量降低不升高, 句子变短变碎",
            },
            "behavior": {
                "walk_rhythm": "重心低, 步幅小, 鞋底拖地, 像随时准备闪",
                "hand_habit": "紧张时左手会下意识摸后颈, 右手插兜或握拳",
                "eye_movement": "扫描式, 看人先看手再看眼, 危险时斜视侧方",
                "stress_response": "后退半步, 肩膀抬高, 下颌绷紧, 不眨眼",
                "pre_break": "开始清嗓子, 反复吞咽, 视线飘到出口",
            },
        },
        "@jax": {
            "descriptor": "少女 16-18 岁, 高挑瘦, 黑色脏辫, 右耳 3 个耳钉, 穿破旧机车皮夹克, 紧身裤, 军靴",
            "refs": {
                "face_closeup": "人像特写, 灰背景, 平光, 真实毛孔, 眼神警觉带笑意",
                "front_full_no_head": "正面全身, 服装材质/破洞清晰",
                "back_full": "背面, 脏辫垂到肩胛, 皮夹克后背有喷漆 logo",
            },
            "states": {
                "@jax": "普通",
                "@jax_wet": "淋雨后, 皮夹克反光, 脏辫结块",
                "@jax_angry": "愤怒, 眼神锁定, 嘴唇抿紧, 拳头握",
                "@jax_laugh": "笑, 嘴咧开但眼不笑, 假笑",
            },
            "voice": {
                "range": "alto (女低音)",
                "timbre": "沙哑带烟熏感, 气流在喉部",
                "speed": "快, 抢话, 句子常被自己打断",
                "accent": "伦敦东区",
                "habit": "语气词 'yeah' 'nah' 'oi' 开头, 笑声短促",
                "pressure_change": "压力下反而说话更轻更慢, 变得危险",
            },
            "behavior": {
                "walk_rhythm": "大步流星, 头微仰, 像走在自己的地盘",
                "hand_habit": "说话时手比划多, 拍自己肚子, 推别人肩膀",
                "eye_movement": "直视, 不闪躲, 笑的时候眼不动",
                "stress_response": "身体前倾, 头歪, 下巴抬, 眼睛眯",
                "pre_break": "突然闭嘴, 手指点对方, 退后一步",
            },
        },
        "@rein": {
            "descriptor": "少女 16-18 岁, 娇小, 直发齐肩, 戴无框眼镜, 穿旧卫衣+格子裙+帆布鞋, 总抱平板电脑",
            "refs": {
                "face_closeup": "人像, 灰背景, 平光, 眼镜反射自然, 眼神冷静",
                "front_full_no_head": "正面, 卫衣口袋塞满小工具, 平板挂腰",
                "back_full": "背面, 直发整齐, 书包鼓鼓的",
            },
            "states": {
                "@rein": "普通",
                "@rein_focus": "专注, 眼镜反光, 手指快动, 嘴微张",
                "@rein_worried": "担忧, 咬下唇, 眼镜推上去, 视线散",
                "@rein_decisive": "决断, 眼镜摘下, 眼神直, 下颌收",
            },
            "voice": {
                "range": "soprano (女高音)",
                "timbre": "干净, 字正腔圆, 气息稳",
                "speed": "中速偏慢, 解释技术时快",
                "accent": "标准英音, 偶尔蹦出东区俚语",
                "habit": "说完会清嗓子, 句尾常带'right?'",
                "pressure_change": "压力下语速加快, 句子变长, 自相矛盾",
            },
            "behavior": {
                "walk_rhythm": "步子小, 视线在地面和设备之间跳",
                "hand_habit": "一直点平板, 推眼镜, 整理耳发",
                "eye_movement": "先看数据再看人, 听人时视线不离设备",
                "stress_response": "手按住平板不放, 身体缩, 眼神不定",
                "pre_break": "突然放下平板, 看着对方不说话",
            },
        },
        "@lulu": {
            "descriptor": "少年 12-14 岁, 瘦小, 红色卷发蓬松, 雀斑, 穿 oversized 卫衣, 脚踝外露",
            "refs": {
                "face_closeup": "人像, 雀斑清晰, 笑容大但眼怯",
                "front_full_no_head": "正面, 卫衣下垂到膝盖",
                "back_full": "背面, 红发蓬, 衣摆不规则",
            },
            "states": {
                "@lulu": "普通",
                "@lulu_scared": "害怕, 身体缩, 眼睛湿, 手抱头",
                "@lulu_brave": "勇敢, 下颌收, 站直, 眼神稳",
            },
            "voice": {
                "range": "treble (童声)",
                "timbre": "清脆但带气声",
                "speed": "紧张时飞快, 平静时慢",
                "accent": "伦敦东区",
                "habit": "句尾常带 'okay?' 'right?'",
                "pressure_change": "压力下变小声, 句尾上扬",
            },
            "behavior": {
                "walk_rhythm": "跑, 不走, 重心高, 脚尖着地",
                "hand_habit": "抓衣摆, 抱自己手臂, 拉红发",
                "eye_movement": "快速扫视, 锁定威胁后不移开",
                "stress_response": "缩, 蹲, 拉袖子",
                "pre_break": "哭, 但不出声, 眼泪大颗掉",
            },
        },
    },
    "antagonists": {
        "@demon_collector": {
            "descriptor": "反派, 40-50 岁, 极高瘦, 苍白皮肤, 黑色长风衣, 黑色皮手套, 眼睛无瞳孔",
            "refs": {
                "face_closeup": "无瞳孔, 眼白带血丝, 嘴角常带冷笑",
                "front_full_no_head": "风衣拖地, 身形如人",
                "back_full": "风衣后摆不规则, 像有东西在动",
            },
            "voice": {
                "range": "bass-baritone (男低音)",
                "timbre": "深, 沙砾, 慢, 计算, 永远平静",
                "speed": "慢, 每句之间留长间隙",
                "accent": "伦敦街头, 模糊国籍",
                "habit": "从不提高音量, 危险信号",
                "pressure_change": "无变化, 永远冷静",
            },
        },
    },
    "locations": {
        "@loc_training_room": {
            "descriptor": "地下训练室, 圆形硬垫, 黑石墙, 单一顶光",
            "states": {
                "@loc_training_room": "白天",
                "@loc_training_room_dusk": "黄昏, 顶光带橙",
                "@loc_training_room_dark": "夜晚, 仅门缝光",
            },
        },
        "@loc_corridor": {
            "descriptor": "长直走廊, 消防栓 frame-left, 电梯 frame-right",
            "states": {
                "@loc_corridor": "白天",
                "@loc_corridor_rain": "雨天, 远处撞击声",
            },
        },
        "@loc_altar_cliff": {
            "descriptor": "悬崖边祭坛, 圆形石盘, 血色地平线",
            "states": {
                "@loc_altar_cliff": "黄昏",
                "@loc_altar_cliff_dawn": "黎明, 血光更强",
            },
        },
    },
    "props": {
        "@crystal_arm": {"descriptor": "半透明晶甲, 从手腕延伸到肩, 内有流动光"},
        "@crystal_knight": {"descriptor": "晶甲骑士套装, 全身覆盖, 头盔带面甲"},
        "@crystal_sword": {"descriptor": "晶甲剑, 剑身透光, 刃口有缺口"},
        "@monster": {"descriptor": "怪物, 黑雾人形, 眼睛两团火"},
        "@monster3": {"descriptor": "怪物三代, 比 monster 更大, 背有骨刺"},
    },
}

# ============================================================
# 2. SCENE_MAP (场景地图)
# ============================================================
SCENE_MAP = {
    "schema": "scene_map_v1",
    "description": "Higgsfield 风格 GEO SPATIAL LAYOUT: 固定地标+左右+距离+180° 轴线+光源",
    "@loc_training_room": {
        "GEO SPATIAL LAYOUT (locked across every shot — pure spatial map)": [
            "— PLATFORM = raised circular training mat, 6m diameter, at room center",
            "— DOOR: frame-left, 8m from mat center, 1m wide, 2.5m tall",
            "— SMASHED MANNEQUINS: 5 of them, scattered at frame-right, 3m from mat",
            "— BENCH: 2m from mat, against the back wall",
            "— 180° AXIS: camera ALWAYS stays on DOOR side — it NEVER crosses to mannequin side",
            "— TOP-LIGHT: single 5000K hard light directly above mat, casts crisp shadow",
            "— BACK-LIGHTING: no back light, key from above only",
            "— CAMERA NEVER: crosses axis, tilts more than 15°, pans to mannequin wall",
        ],
        "initialization_shot": (
            "0.0-1.0s: Wide static shot. Mat empty. 5 mannequins visible at frame-right. "
            "Door at frame-left, closed. Hard top-light pools on mat. "
            "Camera is on door side, 6m back. No motion. 1 second of pure space."
        ),
        "visual_anchors": [
            "Door at frame-left",
            "Mannequins at frame-right",
            "Mat in center, lit from above",
        ],
    },
    "@loc_corridor": {
        "GEO SPATIAL LAYOUT": [
            "— CORRIDOR: 30m long, 2m wide, 3m tall",
            "— FIRE-EXTINGUISHER: frame-left wall, 5m from start",
            "— ELEVATOR: frame-right end, 25m from start",
            "— WINDOWS: along frame-left, every 4m, frosted",
            "— 180° AXIS: camera follows actors from behind, NEVER overtakes",
            "— KEY-LIGHT: from windows at frame-left, casts long shadows to frame-right",
            "— FLOOR: cracked concrete, scuffed, occasional puddle",
        ],
        "initialization_shot": (
            "0.0-1.0s: Static shot of empty corridor. Door at end. "
            "Window light rakes in from frame-left. Camera at one end. 1 second of pure space."
        ),
    },
    "@loc_altar_cliff": {
        "GEO SPATIAL LAYOUT": [
            "— PLATFORM = raised circular ritual stone disc, 4m diameter, at cliff edge",
            "— ALTAR-MONOLITH: at cliff edge, MID-RIGHT position relative to platform",
            "— RITUAL CENTER: CENTER-LEFT, ~3m from altar",
            "— 180° AXIS: camera ALWAYS stays on corpse-field side — it NEVER crosses the line",
            "— BACK-LIGHTING: crimson horizon glow from BEHIND platform, rim-lights silhouettes",
            "— CLIFF: 50m drop, no railing, edge 1m behind altar",
        ],
    },
}

# ============================================================
# 3. ACTING_STATE (表演状态表)
# ============================================================
ACTING_STATE = {
    "schema": "acting_state_v1",
    "5_PILLARS": {
        "WHAT": "角色想从对方那里得到什么 (The Goal)",
        "OBSTACLE": "什么在挡着他 (What's In The Way)",
        "COST": "失败会怎样 (What He Stands To Lose)",
        "STRATEGY": "他正在用什么方法 (His Current Approach)",
        "TURN": "什么让他改变策略 (What Will Make Him Change)",
    },
    "examples": {
        "ROCO_training_alone": {
            "scene": "@loc_training_room, 12s shot, ROCO drills alone",
            "WHAT": "在 JAX/REIN 进来前, 再完成一次 clean hit",
            "OBSTACLE": "右臂失控, 每次重击都会失控加剧",
            "COST": "如果被 JAX/REIN 看到失控, 就不能继续当组长",
            "STRATEGY": "用左臂的苦肉计压住右臂, 不让他们看出问题",
            "TURN": "门被推开的那一秒, 他必须立刻收起疲惫",
        },
        "JAX_REIN_corridor": {
            "scene": "@loc_corridor, 30s shot, JAX/REIN 走边说",
            "WHAT (JAX)": "让 REIN 放松, 边走边聊战绩",
            "WHAT (REIN)": "边走边算数据, 报告给老大",
            "OBSTACLE": "远处训练室传来撞击声",
            "COST (JAX)": "如果被 REIN 知道她已经听见, 就暴露她也害怕",
            "STRATEGY (JAX)": "继续说笑, 但笑容消失晚半拍",
            "STRATEGY (REIN)": "手指停一拍, 然后头才转",
            "TURN": "撞击声之后, 两人同时沉默, 但都不承认",
        },
    },
}

# ============================================================
# 4. SHOTLIST (分镜表)
# ============================================================
SHOTLIST_TEMPLATE = {
    "schema": "shotlist_v1",
    "columns": [
        "shot_id",          # 镜号
        "duration_sec",     # 时长
        "first_frame",      # 首帧描述
        "main_action",      # 主要动作
        "dialogue",         # 台词
        "sound",            # 声音/环境
        "assets_used",      # 用到的资产标签
        "camera",           # 摄影
        "lighting",         # 光线
        "constraints",      # 连续性约束
        "iteration",        # 当前迭代轮次
        "status",           # pending/shot/selected/dead
        "notes",            # 备注
    ],
    "example_row": {
        "shot_id": "S01_T01_R01_01",
        "duration_sec": 12.0,
        "first_frame": "Wide static. Training mat in center, 5 smashed mannequins frame-right, door frame-left. Hard top light.",
        "main_action": "ROCO drills alone, then door opens",
        "dialogue": "",
        "sound": "Fist impact, heavy breath, door creak",
        "assets_used": ["@roco", "@loc_training_room"],
        "camera": "Wide static 0-1s, then push-in slow to medium",
        "lighting": "Hard top-light 5000K from above only",
        "constraints": ["EXACT 3 characters if door opens", "camera NEVER crosses 180 axis"],
        "iteration": 3,
        "status": "selected",
        "notes": "v3 changed door-open to 2.5s instead of 4.0s — better timing",
    },
}

# ============================================================
# 5. VERSION_LOG (版本日志)
# ============================================================
VERSION_LOG_TEMPLATE = {
    "schema": "version_log_v1",
    "rule": "一次只改一个变量 (Higgsfield Rule 3)",
    "columns": [
        "version",          # v1, v2, v3 ...
        "shot_id",          # 对应镜号
        "diff",             # 唯一改动的行
        "why",              # 为什么改
        "result",           # 生成结果 (selected/rejected)
        "accept_reason",    # 选中原因
        "iter_count",       # 累计迭代次数
        "ten_fifteen_warning",  # 10-15 次是否触发简化
    ],
    "example": [
        {
            "version": "v3",
            "shot_id": "S01_T01_R01_01",
            "diff": "door-open at 2.5s (was 4.0s)",
            "why": "v2 had door opening too late, broke actor entrance rhythm",
            "result": "selected",
            "accept_reason": "JAX enters at right beat, ROCO catches her with eyes first",
            "iter_count": 3,
            "ten_fifteen_warning": False,
        },
    ],
}

# ============================================================
# 6. POST_ISSUE_LIST (后期问题单)
# ============================================================
POST_ISSUE_LIST_TEMPLATE = {
    "schema": "post_issue_list_v1",
    "description": "定剪后独立清理 pass: 手脸/文字/接缝/颜色/环境声/待补镜头",
    "categories": [
        "face_drift",       # 脸部漂移
        "hand_extra_finger",# 多指
        "boil_texture",     # 沸腾纹理
        "fake_text",        # 假字/招牌
        "color_mismatch",   # 调色不统一
        "audio_continuity", # 声音不连贯
        "missing_coverage", # 待补镜头
        "seam_jump",        # 接缝跳
    ],
    "example_issue": {
        "shot_id": "S02_T03_R01_05",
        "category": "hand_extra_finger",
        "severity": "high",  # high/medium/low
        "fix_priority": "face_and_hands_first",  # Higgsfield: 优先级: 脸和手
        "description": "ROCO's right hand has 6 fingers at 0:08.500 when picking up crystal",
        "fix_method": "rerun_with_modified_prompt",  # rerun / mask / paint / accept
        "fixed": False,
    },
}


def get_six_documents_summary():
    """6 份文件摘要 (用于注入到节点)"""
    return f"""
════════════════════════════════════════
【Higgsfield 6 份文件 (项目级记忆)】
════════════════════════════════════════

1. ASSET_REGISTRY (资产注册表):
   - {len(ASSET_REGISTRY['characters'])} 主角 + {len(ASSET_REGISTRY['antagonists'])} 反派 + {len(ASSET_REGISTRY['locations'])} 地点 + {len(ASSET_REGISTRY['props'])} 道具
   - 每角色 4 张图 (face/正面去头/背面 + 状态)
   - 每角色 5 维声音档案 + 5 维行为档案

2. SCENE_MAP (场景地图):
   - {len(SCENE_MAP)} 场景, 每场景 GEO SPATIAL LAYOUT + initialization_shot + 180° axis + visual_anchors

3. ACTING_STATE (表演状态表):
   - 5 支柱 (WHAT/OBSTACLE/COST/STRATEGY/TURN)
   - 永远不写情绪, 写行为

4. SHOTLIST (分镜表):
   - {len(SHOTLIST_TEMPLATE['columns'])} 列标准格式
   - 每行可追溯

5. VERSION_LOG (版本日志):
   - 一次只改一个变量
   - 10-15 次规则触发简化

6. POST_ISSUE_LIST (后期问题单):
   - {len(POST_ISSUE_LIST_TEMPLATE['categories'])} 类问题
   - 优先级: 脸和手先修

════════════════════════════════════════
"""


# ============================================================
# 7. L1-L7 七层 PROMPT 架构 (AIGC 影视全流程解析 第十章)
# ============================================================
L1_L7_ARCHITECTURE = {
    "schema": "l1_l7_prompt_architecture_v1",
    "description": "L1-L7 七层 Prompt 架构 — 把导演的创作意图分解为 AI 可执行的精确指令",
    "L1_意图与验收": {
        "purpose": "回答 '我为什么要拍这个镜头'",
        "formula": "本镜让观众 [理解/感受/发现] ……；通过 [一个主要可见事件] 完成；结束时观众应看到 ……",
        "key_principle": "AI 视频最容易被识别的'AI 感'之一是画面没有叙事目的。L1 确保每个镜头都有明确的叙事功能，这正是 AI 视频和人类导演作品的本质区别。",
        "example": "本镜让观众感受到 ROCO 的精疲力竭和隐忍；通过他的呼吸、下巴绷紧、鼻血流淌和目光移动完成；结束时观众应看到他在门打开的瞬间重新武装表情.",
    },
    "L2_资产与引用": {
        "purpose": "回答 '谁或什么出现？当前是什么状态？'",
        "formula": "[稳定资产ID @ 状态版本]；身份锁定[稳定特征]；当前状态[服装/伤势/湿度/携带物]；参考[ID]只继承[属性]，明确排除[构图/机位/光线/背景等]",
        "key_principle": "Do not use as a starting frame, do not inherit the composition, the angle or the grade. — 明确排除构图和角度的继承，让模型只继承'身份'和'纹理'，这样才能产生有变化的镜头序列。",
        "anti_ai": "L2 是消除'AI 参考图风格固化'的关键。",
    },
    "L3_空间与数量": {
        "purpose": "回答 '人物站在哪里？摄影机在哪里？空间关系是什么？'",
        "formula": "GEO SPATIAL LAYOUT + 地标 + 距离 + 180° AXIS + BACK-LIGHTING",
        "three_iron_laws": [
            "规则一：空间地图中只写空间事实，不写人物动作 (空间地图的职责是建立'舞台'，不是指导'表演')",
            "规则二：方向只从摄影机视角说 (使用 frame-left、frame-right，模型无法理解'角色的左边')",
            "规则三：位置挂地标+距离，不写相对位置 (写 'at the altar, three meters away'，而不是 'standing beside the altar')",
        ],
    },
    "L4_表演与物理": {
        "purpose": "回答 '角色在做什么？情感状态是什么？身体如何表现？'",
        "formula": "CHARACTER ACTING + ACTION TIMING + PHYSICS",
        "key_principle": "微动作的总和 = 情感。不是 'ROCO 很累'，而是 '下颌绷紧再松开两次'。AI 无法理解'累'的抽象概念，但可以执行'下颌绷紧两次'的具体指令。",
        "anti_ai_techniques": [
            "'ROCO 很累' → '下颌绷紧再松开两次'",
            "'ROCO 很愤怒' → '鼻血流到嘴唇，没有擦'",
            "'ROCO 很绝望' → '目光先看向破坏的人偶，再看向人'",
            "'ROCO 在强装镇定' → '门一开，他重新武装表情'",
        ],
        "7_活人感规则": [
            "分阶段眨眼: one lazy blink → DOUBLE-BLINK → HARD reset-blink",
            "视线先于头: 眼睛先到门口，头晚半拍",
            "微生命: 每 1-2 秒一个微事件 (呼吸/鼻翼/眉头)",
            "静止保持张力: 用'用力维持静止'，不用'nobody moves'",
            "反应先于台词: 听话的人半句就懂了，脸已先答",
            "重要事件后消化: 半秒消化再开口",
            "让手忙起来: 一边修东西/数东西/倒东西一边聊，最强重音是突然停下手里的活",
        ],
        "5_表演支柱": ["WHAT", "OBSTACLE", "COST", "STRATEGY", "TURN"],
        "20_情绪动作翻译": {
            "sad": "下颌松 / 视线掉 / 呼吸浅慢",
            "angry": "下颌咬 / 鼻翼张 / 拳握",
            "scared": "瞳孔大 / 呼吸快 / 身体僵",
            "happy": "颊部提 / 眼周收缩 / 嘴角拉",
            "surprise": "眉扬 / 上睑提 / 嘴张",
            "disgust": "上唇提 / 鼻翼皱 / 头偏",
            "contempt": "单侧嘴角提 / 视线下",
            "anxiety": "呼吸短 / 手指动 / 腿抖",
            "exhausted": "肩塌 / 眼皮沉 / 步拖",
            "determined": "下颌绷 / 眼锁 / 身倾",
            "love": "瞳孔扩 / 颊微红 / 嘴角松",
            "hatred": "眼睛窄 / 嘴紧 / 拳紧",
            "fear": "瞳孔大 / 面色白 / 后退",
            "hope": "眼睛亮 / 嘴角微提 / 身展",
            "despair": "眼神散 / 肩全塌 / 声失",
            "shame": "头低 / 眼神躲 / 脸红",
            "pride": "胸挺 / 视平 / 嘴角单侧",
            "envy": "视紧 / 咬唇 / 身紧",
            "relief": "肩松 / 呼长气 / 眼软",
            "shock": "全身僵 / 呼吸停 / 眼大",
        },
    },
    "L5_摄影与剪辑": {
        "purpose": "回答 '摄影机怎么动？镜头怎么切？'",
        "formula": "[起始构图：景别+角度] → [镜头运动类型+幅度+速度] → [结束构图] + OPTICS: [焦段]mm, T[光圈], [景深类型]",
        "focal_lengths": {
            "14mm": "广角: 失真、压迫、近距离恐惧",
            "24mm": "街拍、纪实、不稳定",
            "35mm": "标准、电影感、自然",
            "50mm": "人眼视角、亲密、中性",
            "85mm": "肖像、虚化、浪漫",
            "135mm+": "远距离、压缩、孤独",
        },
        "aperture_dof": {
            "T1.4-T2": "极浅景深、梦幻、突出主体",
            "T2.8": "电影浅景深、人物特写",
            "T4": "中景深、对话场景",
            "T8": "全景深、环境展示",
        },
    },
    "L6_声音与对白": {
        "purpose": "回答 '观众听到什么？'",
        "formula": "VOICE SIGNATURES + DIALOGUE + SILENCED + SFX LAYERS + CONTINUATION TAIL",
        "key_principle": "声音是电影的一半 (库斯杜力卡). 潜文本对白 6 技巧: 说反话/转移话题/言此意彼/沉默/动作/潜台词双重",
        "subtext_techniques": [
            "说反话: 角色说'没事'，实际崩溃",
            "转移话题: 角色用'你吃了吗'逃避问题",
            "言此意彼: 角色说'今天天气不错'实际是'我爱你'",
            "沉默潜文本: 角色不回答就是回答",
            "动作潜文本: 角色在'摸伤口' = '我没好'",
            "潜台词双重: 角色对 A 说话其实对 B 说",
        ],
    },
    "L7_风格约束": {
        "purpose": "回答 '哪些东西永远不变？'",
        "formula": "Style + Cinematography + Lighting + Color + Camera + Skin + Acting + Physics + Composition + Continuity + Technical + Audio 12 层",
        "key_principle": "Style Prefix 是'不变项'。一旦确定，所有镜头必须严格遵守。这是消除 AI 风格漂移的核心机制。",
    },
}


# ============================================================
# 8. 3 留白 + 3 运镜法则 (AIGC 影视全流程解析 第二章)
# ============================================================
WHITESPACE_CAMERA_LAWS = {
    "schema": "whitespace_camera_laws_v1",
    "description": "3 留白 + 3 运镜 — 消除 AI 味的核心创作方法",
    "3_留白技巧": {
        "时间留白": "延迟满足 (Delayed Gratification) — 观众的情绪是在等待中形成的。镜头不切，让观众在画面中等待，情绪在等待中累积。例: 角色在听到坏消息后 3 秒不反应，然后慢慢坐下。",
        "空间留白": "决定情绪的集中度 (Decide Emotional Concentration) — 主体在大空间里显得孤独，在小空间里显得压抑。例: 一个人站在巨大空旷的房间里，视觉上的留白传递心理上的孤独。",
        "叙事留白": "不把一切说尽 (Don't Say Everything) — 留给观众想象的空间。例: 镜头停在角色离开的画面，不交代他去了哪里；或者镜头只表现冲突的开头，不表现结果。",
    },
    "3_运镜法则": {
        "破坏首帧完成度": "让镜头去找画面，而非直接给出完美构图。镜头从模糊/偏移开始，然后'找到'主体，制造真实感。AI 视频最常见的'摆拍感'就是因为首帧太完美。",
        "引入非线性运动轨迹": "拒绝过度平滑的镜头运动。真实摄影机会有微抖、有犹豫、有加速减速。运镜曲线不是完美的正弦波，而是有'犹豫点'的非线性轨迹。",
        "制造响应延迟": "主体先发生动作，镜头再跟拍。例: 角色先转头，镜头 0.3-0.5 秒后才跟上，这种延迟让画面有了'摄影师在反应'的真实感，而不是预设的丝滑跟拍。",
    },
    "引用": [
        "Denis Villeneuve: '把镜头保持到远超寻常导演会切走的时刻之后'",
        "Christopher Nolan: '三小时道德辩论像惊悚片一样疾驰'",
        "黑泽明: '让电影的视觉、叙事、情绪和空间都做到极致清晰'",
        "Paul Thomas Anderson: '像小说家般取景与掌控节奏'",
        "奉俊昊: '把类型当作特洛伊木马，在同一场戏中从喜剧滑向恐怖'",
    ],
}


# ============================================================
# 9. 8 大顶级导演能力 + 42 环节映射 (AIGC 影视全流程解析 第二章 + 第三章)
# ============================================================
EIGHT_ABILITIES_MAP = {
    "schema": "eight_abilities_42_stages_v1",
    "description": "8 大顶级导演能力 → 42 环节映射 — 让 AI 导演系统达到世界顶级水平",
    "8_能力": {
        "AB1_叙事架构力": {
            "question": "故事如何在结构上承载情感？",
            "representatives": ["Paul Thomas Anderson", "Christopher Nolan", "奉俊昊", "Martin Scorsese"],
            "key_techniques": ["Save the Cat 15 节拍", "Hero's Journey 17/12 阶段", "McKee 7 大结构", "三幕剧结构", "情节点设计", "副线设计", "角色弧光追踪", "主题的视觉化呈现"],
            "ai_implementation": "叙事引擎：剧本分析、结构识别、弧光追踪、情节点标注",
            "42_环节覆盖": [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12],  # 创意孵化 5 + 剧本开发 7
        },
        "AB2_情感调度力": {
            "question": "观众应在什么时刻感受什么情绪？",
            "representatives": ["黑泽明", "库斯杜力卡", "奉俊昊", "斯皮尔伯格"],
            "key_techniques": ["情感图谱", "情感弧光", "微动作总和等于情感", "重要事件后消化", "7 活人感规则"],
            "ai_implementation": "情感引擎：情感目标→视觉参数映射词典",
            "42_环节覆盖": [5, 6, 8, 12, 16, 32, 35, 38],  # 视觉风格/对白/表演/剪辑/声音
        },
        "AB3_节奏控制力": {
            "question": "观众的注意力曲线如何被管理？",
            "representatives": ["Christopher Nolan", "Denis Villeneuve", "奉俊昊", "北野武"],
            "key_techniques": ["全片节奏曲线", "30s 场景单元 6 段", "加速-减速对比", "静止-爆发对比", "时间压缩/拉伸", "跳切/硬切/叠化", "留白", "呼吸节奏"],
            "ai_implementation": "节奏引擎：全片节奏曲线 + 场景节奏控制 + 镜头时长管理",
            "42_环节覆盖": [6, 11, 23, 25, 27, 28, 33, 34, 35],  # 剧本/分镜/Prompt/批量/衔接/完成度/剪辑
        },
        "AB4_视觉语言力": {
            "question": "构图/光影/色彩如何传递潜文本？",
            "representatives": ["Roger Deakins", "Emmanuel Lubezki", "杜可风", "Bradford Young"],
            "key_techniques": ["焦段×情感", "光圈×景深", "60:30:10 色彩法则", "9 维光影", "构图法则"],
            "ai_implementation": "视觉语言引擎：镜头语言参数化 + 12 层 Style Prefix",
            "42_环节覆盖": [5, 13, 14, 15, 16, 17, 25, 32, 37, 39],  # 视觉开发 5 + 镜头语言 + 表演 + 调色 + VFX
        },
        "AB5_表演指导力": {
            "question": "如何逼出数字演员生涯最佳的表演？",
            "representatives": ["Paul Thomas Anderson", "库斯杜力卡", "奉俊昊", "王家卫"],
            "key_techniques": ["FACS 12 基础表情单元", "5 表演支柱", "7 活人感规则", "20 种情绪动作翻译", "潜文本对白 6 技巧"],
            "ai_implementation": "表演引擎：FACS 12 + 5 支柱 + 7 活人感 + 20 情绪动作",
            "42_环节覆盖": [4, 8, 9, 13, 18, 21, 32],  # 角色/对白/弧光/角色视觉/资产/表演
        },
        "AB6_场面调度力": {
            "question": "空间如何被安排为叙事的舞台？",
            "representatives": ["Christopher Nolan", "Denis Villeneuve", "奉俊昊", "韦斯·安德森"],
            "key_techniques": ["GEO SPATIAL LAYOUT 三大铁律", "180° 轴线系统", "5 大空间逻辑", "6 大空间类型", "空间叙事顺序"],
            "ai_implementation": "空间引擎：GEO MAP + 180° 系统 + 5 空间逻辑 + 6 空间类型",
            "42_环节覆盖": [14, 19, 24, 25, 33, 36],  # 场景视觉/场景资产/空间地图/镜头语言/衔接
        },
        "AB7_审美判断力": {
            "question": "在多个候选中，哪个最符合叙事意图？",
            "representatives": ["Paul Thomas Anderson", "Yorgos Lanthimos", "Greta Gerwig"],
            "key_techniques": ["风格不脱离内容", "不完美制造真实感", "运镜 3 法则", "留白 3 技巧"],
            "ai_implementation": "审美引擎：候选评估矩阵 + 留白 3 技巧 + 运镜 3 法则",
            "42_环节覆盖": [11, 26, 29, 30, 31, 40],  # 定稿/审核/质检/选片/迭代/审片
        },
        "AB8_团队领导力": {
            "question": "多个智能体如何协同为统一意图服务？",
            "representatives": ["Peter Jackson", "Christopher Nolan", "Denis Villeneuve"],
            "key_techniques": ["11 阶段管线", "6 份文件项目级记忆", "5 大铁律"],
            "ai_implementation": "多智能体协调：智能体编排 + 工作流管理 + 项目记忆",
            "42_环节覆盖": [11, 22, 34, 40, 41, 42],  # 定稿/压力测试/完成度/审片/输出/归档
        },
    },
    "42_环节_8_阶段": {
        "阶段1_创意孵化": {"环节数": 5, "控制强度": "★★★★☆", "环节": [1, 2, 3, 4, 5]},
        "阶段2_剧本开发": {"环节数": 7, "控制强度": "★★★★★", "环节": [6, 7, 8, 9, 10, 11, 12]},
        "阶段3_视觉开发": {"环节数": 5, "控制强度": "★★★★☆", "环节": [13, 14, 15, 16, 17]},
        "阶段4_资产生产": {"环节数": 5, "控制强度": "★★★☆☆", "环节": [18, 19, 20, 21, 22]},
        "阶段5_预可视化": {"环节数": 4, "控制强度": "★★★★☆", "环节": [23, 24, 25, 26]},
        "阶段6_拍摄执行": {"环节数": 8, "控制强度": "★★★★★", "环节": [27, 28, 29, 30, 31, 32, 33, 34]},
        "阶段7_后期制作": {"环节数": 6, "控制强度": "★★★★☆", "环节": [35, 36, 37, 38, 39, 40]},
        "阶段8_交付分发": {"环节数": 2, "控制强度": "★★☆☆☆", "环节": [41, 42]},
    },
}


def get_six_documents_summary():
    """6 份文件摘要 (用于注入到节点) — Phase 14 升级版 (含 L1-L7 + 留白 + 8 能力)"""
    return f"""
════════════════════════════════════════
【Higgsfield 6 份文件 (项目级记忆)】
════════════════════════════════════════

1. ASSET_REGISTRY (资产注册表):
   - {len(ASSET_REGISTRY['characters'])} 主角 + {len(ASSET_REGISTRY['antagonists'])} 反派 + {len(ASSET_REGISTRY['locations'])} 地点 + {len(ASSET_REGISTRY['props'])} 道具
   - 每角色 4 张图 (face/正面去头/背面 + 状态)
   - 每角色 5 维声音档案 + 5 维行为档案

2. SCENE_MAP (场景地图):
   - {len(SCENE_MAP)} 场景, 每场景 GEO SPATIAL LAYOUT + initialization_shot + 180° axis + visual_anchors
   - 三大铁律: 只写空间不写动作 / 摄影机视角 frame-left / 地标+距离

3. ACTING_STATE (表演状态表):
   - 5 支柱 (WHAT/OBSTACLE/COST/STRATEGY/TURN)
   - 永远不写情绪, 写行为
   - 7 活人感规则 + 20 情绪动作翻译

4. SHOTLIST (分镜表):
   - {len(SHOTLIST_TEMPLATE['columns'])} 列标准格式
   - 每行可追溯

5. VERSION_LOG (版本日志):
   - 一次只改一个变量
   - 10-15 次规则触发简化

6. POST_ISSUE_LIST (后期问题单):
   - {len(POST_ISSUE_LIST_TEMPLATE['categories'])} 类问题
   - 优先级: 脸和手先修

════════════════════════════════════════
【7. L1-L7 七层 Prompt 架构】
════════════════════════════════════════
L1 意图与验收 — 本镜让观众 [感受] 通过 [事件] 完成
L2 资产与引用 — @角色@地点@道具, 明确排除构图继承
L3 空间与数量 — GEO SPATIAL LAYOUT + 三大铁律
L4 表演与物理 — 微动作总和等于情感 + 7 活人感 + 20 情绪
L5 摄影与剪辑 — 焦段×光圈×景深×运动+幅度+速度
L6 声音与对白 — 潜文本 6 技巧 + 声音尾音
L7 风格约束 — 12 层 Style Prefix 逐字粘贴

════════════════════════════════════════
【8. 3 留白 + 3 运镜法则 (消除 AI 味)】
════════════════════════════════════════
时间留白: 延迟满足
空间留白: 情绪集中度
叙事留白: 不说尽

运镜法则 1: 破坏首帧完成度
运镜法则 2: 引入非线性运动轨迹
运镜法则 3: 制造响应延迟

════════════════════════════════════════
【9. 8 大顶级导演能力 (L5 World-Class)】
════════════════════════════════════════
AB1 叙事架构力 — PTA / Nolan / 奉俊昊 / Scorsese
AB2 情感调度力 — 黑泽明 / 库斯杜力卡 / 奉俊昊 / 斯皮尔伯格
AB3 节奏控制力 — Nolan / Villeneuve / 奉俊昊 / 北野武
AB4 视觉语言力 — Roger Deakins / Lubezki / 杜可风 / Bradford Young
AB5 表演指导力 — PTA / 库斯杜力卡 / 奉俊昊 / 王家卫
AB6 场面调度力 — Nolan / Villeneuve / 奉俊昊 / 韦斯·安德森
AB7 审美判断力 — PTA / Lanthimos / Gerwig
AB8 团队领导力 — Peter Jackson / Nolan / Villeneuve

════════════════════════════════════════
"""


if __name__ == "__main__":
    import json
    print(get_six_documents_summary())
    print(f"\n6 份文件 + 3 新文档总字符: {len(json.dumps([ASSET_REGISTRY, SCENE_MAP, ACTING_STATE, SHOTLIST_TEMPLATE, VERSION_LOG_TEMPLATE, POST_ISSUE_LIST_TEMPLATE, L1_L7_ARCHITECTURE, WHITESPACE_CAMERA_LAWS, EIGHT_ABILITIES_MAP], ensure_ascii=False))}")
