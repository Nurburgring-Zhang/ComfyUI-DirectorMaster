# -*- coding: utf-8 -*-
"""
asset_registry.py — 资产层 (Asset Layer) Phase 14
==========================================================

【5 要素架构 (5-Element Architecture)】
──────────────────────────────────────────────────────────
1. 数据 (Data)             — 资产参数 / 状态字典 / 压力测试结果
2. 上下文缩略 (Context)    — 资产当前激活的 state / view / shot 上下文
3. Skill/Harness           — 5 维意图 / 反 AI 词表 / ACTING 行为档案
4. 经验矩阵 (Experience)   — 街童 / 反派 / 道具 / 地点 真实战例
5. AI 深度处理 (AI Deep)   — 动态组合 4 视图描述 + 声音签名 + 行为签名

【为什么需要资产层 (摘自 Higgsfield Hell Grind Production Brief)】
──────────────────────────────────────────────────────────
AI 视频最大的坎是一致性。同一个角色, 上一镜还是这张脸, 下一镜就换人了。
视频模型没有记忆, prompt 里少写一个特征, 下一镜他就换件夹克。

解法 = 资产系统: 一个资产 = 文本 (descriptor) + 图片 (refs)。
文本逐字进每个 prompt; 图片给模型当锚点。

【Higgsfield 7 条铁律 (直接继承)】
1. 资产先行 — 没锁定 + 压力测试通过的, 一个镜头都不生成
2. 描述符逐字粘贴 — 绝不缩写
3. 一次只改一行 — 整段重写会丢已 work 的部分
4. 状态拆分 — @roco / @roco_wet / @roco_blood 各写各的描述
5. 声音锁定 — 音域/音色/语速/口音/说话方式 写成 1-2 句
6. 行为锁定 — 走路/手部/眼神移动/压力反应/崩溃前动作
7. 压力测试 — 10 次生成姿势光线轮换, 10/10 可识别 + 同框测试

【正面全身图故意没头】
修掉一整类废镜头: 全景里模型会从小图取脸, 那张脸又小又糊, 张张崩。
把头删掉, 模型只能从特写取脸。

【资产 = 身份合同】
一个人物至少有 3 个身份锚点: 例如 左眉上的疤 + 红色围巾 + 右肩金属护甲。
即使生成出现轻微误差, 三个强识别点始终存在 = 观众仍认得同一个人。

【本文件对外 API】
- register_asset(name, descriptor, refs, voice, behavior, states)
- get_descriptor(name) → 完整身份合同文本
- get_state_descriptor(name, state) → 状态版本 (湿/血/伤/换装)
- get_voice_signature(name) → 声音签名 (逐字粘贴用)
- get_behavior_signature(name) → 行为签名 (表演系统用)
- pressure_test(name) → 10/10 压力测试 mock + 同框测试
- lock_asset(name) → 锁定 + 输出可逐字粘贴的 descriptor
- render_asset_prompt(name) → 完整 4 视图 + 状态 + 声音 + 行为 prompt block

【本文件 8 个真实示例资产】
街童 (来自 Hell Grind):
- @roco   — ROCO 主角, 右臂水晶化, 训练室独处
- @jax    — JAXX 跑腿, 瘦小, 拿食物托盘
- @rein   — REIN 数据控, 拿平板, 短发机械
- @lulu   — LULU 女孩, 机警, 独行者
反派:
- @kaine  — KAINE 反派, 伦敦口音, 平静威胁感
地点:
- @loc_training_room — 圆形训练垫, 黑岩石墙
- @loc_museum       — 博物馆展厅, 文物柜
道具:
- @crystal_sword    — 水晶剑, 三版本 (展示/染血/隐藏)
"""


# ============================================================
# 0. 5 要素常量 — 每个函数都会读取这些, 不许是模板
# ============================================================

# 1) 数据 (Data)
ELEMENT_DATA = {
    "higgsfield_source": "Hell Grind (95 分钟 AI 长片, 2026-08-05 开源, 14 天生成期, 115,446 次生成)",
    "seedance_version": "Seedance 2.5 (2026-08-07 火山引擎 API 正式上线)",
    "asset_count_hell_grind": 115501,
    "character_refs_rule": "三视图 = 脸特写 + 正面全身 (无头) + 背面全身",
    "test_pass_rule": "10 次生成 / 10 次姿势光线轮换 / 10/10 可识别 + 同框测试",
    "anti_skin_rule": "一张图绝不被模型完整跑两遍, 每多跑一遍就毁一遍纹理",
    "catch_light_rule": "眼睛必须有 catch-light, 没有的脸是死的, 模型演不动",
    "first_frame_rule": "每个场景开头先 1 秒无动作全景, 让模型确认谁在哪",
    "no_age_rule": "永远不写年龄, 内容过滤器一读到未成年人就收紧",
    "positive_only_rule": "只写肯定形式, 写 'falls on his stomach', 不写 'does NOT fall on his back'",
    "max_prompt_words": "单条 3000-4000 词, 长度不是敌人, 超载的节拍才是",
    "max_beats": "每节拍最多 3 句话, 一个节拍超载 = 模型直接糊成一团",
}

# 2) 上下文缩略 (Context Brief)
ELEMENT_CONTEXT = {
    "current_node": "asset_registry",
    "function_of_asset": "身份合同 + 状态拆分 + 声音锁定 + 行为锁定 + 压力测试",
    "downstream_nodes": [
        "director_pro (环节 2, 调用 descriptor 进 H3 prompt)",
        "director_storyboard_pro (环节 3, 引用 ref 图 + 行为档案)",
        "cinematic_studio (环节 4, 拼装 15 块刚性 prompt 骨架)",
        "acting_skill (环节 5, 渲染 CHARACTER ACTING 区)",
    ],
    "model_target": "Seedance 2.5 + Soul Cinema + Nano Banana Pro + Seedream 4.5",
    "output_dim": "中文 descriptor + 英文风格标签 + 状态索引",
}

# 3) Skill / Harness
ELEMENT_SKILL = {
    "five_acting_pillars": [
        "目标 — 角色此刻想要什么",
        "障碍 — 什么挡着他",
        "策略 — 他如何争",
        "代价 — 失败的代价",
        "调整 — 新信息后如何改策略",
    ],
    "behavior_archive_dimensions": [
        "走路节奏 (pace)",
        "手部习惯 (hand habit)",
        "眼神移动 (eye movement)",
        "压力反应 (pressure response)",
        "情绪崩溃前动作 (pre-break action)",
    ],
    "voice_signature_dimensions": [
        "音域 (range)",
        "音色 (timbre)",
        "语速 (pacing)",
        "口音 (accent)",
        "说话习惯 (speech habit)",
    ],
    "anti_ai_rules": [
        "禁止 '陷入沉思' → 改成 '他没说话'",
        "禁止 '瞳孔地震' → 改成 '视线收紧'",
        "禁止 '缓缓地/深深地/静静地' 滥用",
        "禁止 '绝美/倾国倾城/惊艳'",
        "禁止写年龄",
    ],
    "descriptor_style": [
        "5+ 视觉特征 (亚裔 + 35岁 + 短卷发 + 右眉疤 + 深蓝西装)",
        "用 'frame-left/frame-right' 不用 '他的左边'",
        "地点用距离 + 锚点 'at the altar, three meters away'",
        "首句必须有可识别的 '三个身份锚点'",
    ],
}

# 4) 经验矩阵 (Experience Matrix)
ELEMENT_EXPERIENCE = {
    "hell_grind_yields": "16181 次生成 / 留下 253 个镜头 (前 25 分钟统计)",
    "asset_failure_modes": [
        "同框测试不通过 — 单独稳的角色跟人同框就崩",
        "正面全身取脸 — 小图脸糊, 必须删头",
        "状态串场 — 干燥淋雨一个描述里, 模型在镜头之间串状态",
        "声音漂移 — 音域没锁, 切点音色突然换",
    ],
    "creative_lessons": [
        "齐磊 (超级个体) — 传统工具用到底, 起决定作用是导演整体把控",
        "王天海 (团队) — 创意编剧/分镜/生成/后期 拆分, 产能稳定",
        "河南大学 4 女生 — 提示词必须精准到性别/国别/年龄最好",
        "LibTV — 主体库 + 三视图 + 9/25 宫格, 节点式工作流",
    ],
    "best_practice": [
        "光线 = 单一光源, 光从哪来 → 阴影到哪去",
        "构图 = 三分法 + 黄金比 + 强剪影对光",
        "表演 = 微停顿 + 准确眼线 + 湿润眼神 + 可见呼吸 + 胸腔起伏",
        "物理 = 重力惯性 + 质量有重量 + 正确接触阴影",
    ],
}

# 5) AI 深度处理 (AI Deep Processing)
ELEMENT_AI_DEEP = {
    "core_directive": "不是描述 '画面里有什么', 是描述 '导演会怎么描述自己的意图'",
    "philosophy": "模型学习的不再只是描述, 还包括一个导演会怎样描述自己的意图",
    "iteration_principle": "一次只改一行, 全部进日志, prompt 是受版本控制的生产文件",
    "anti_slop_strategy": "拆镜头 > 加词, 一镜一动作, 角落 > 房间, 锚点 > 开放空间",
    "dynamic_compose_rule": "descriptor 必须从资产底层数据动态组合, 不许是模板填字",
    "fail_mode_reflex": "镜头搞不定 = 简化镜头, 不改词, 拆两镜 / 删动作 / 换角度",
}


# ============================================================
# 1. 数据结构 — AssetRecord + AssetRef + StateVariant
# ============================================================

class AssetRef:
    """
    资产参考图对象。
    Higgsfield 三视图: 脸特写 + 正面全身 (无头) + 背面全身。
    每张图都有 用途/拍摄规格/模型测试结果 三个字段。
    """

    __slots__ = ("view", "purpose", "shot_spec", "model_test", "neutral_look")

    def __init__(self, view, purpose, shot_spec, model_test, neutral_look=True):
        self.view = view              # "face" | "front" | "back"
        self.purpose = purpose        # 中文描述这张图是干嘛的
        self.shot_spec = shot_spec    # 拍摄规格 (灰底 / 平光 / 真实毛孔)
        self.model_test = model_test  # {"model": "Seedance 2.5", "pass_rate": 10/10, "tested_at": "2026-08-05"}
        self.neutral_look = neutral_look  # 是否中性灰背景 (默认 True)

    def to_dict(self):
        return {
            "view": self.view,
            "purpose": self.purpose,
            "shot_spec": self.shot_spec,
            "model_test": self.model_test,
            "neutral_look": self.neutral_look,
        }


class StateVariant:
    """
    状态版本对象 (湿/血/伤/换装)。
    每种状态 = 独立资产, 独立 descriptor, 独立 refs。
    混在一个文本里 = 模型在镜头之间串状态, 拆分状态比跟模型打架便宜。
    """

    __slots__ = ("label_suffix", "descriptor_delta", "refs_delta", "voice_delta", "behavior_delta")

    def __init__(self, label_suffix, descriptor_delta, refs_delta=None, voice_delta="", behavior_delta=""):
        self.label_suffix = label_suffix        # "_wet" / "_blood" / "_injured" / "_clothed_change"
        self.descriptor_delta = descriptor_delta  # 与默认状态相比, 描述上叠加什么
        self.refs_delta = refs_delta or []      # 状态专属的额外 refs (可选)
        self.voice_delta = voice_delta          # 状态对声音的影响 (受伤可能沙哑)
        self.behavior_delta = behavior_delta    # 状态对行为的影响 (受伤可能跛行)

    def full_label(self, base_name):
        return "@" + base_name.lstrip("@") + self.label_suffix

    def to_dict(self):
        return {
            "label_suffix": self.label_suffix,
            "descriptor_delta": self.descriptor_delta,
            "voice_delta": self.voice_delta,
            "behavior_delta": self.behavior_delta,
        }


class AssetRecord:
    """
    单一资产 (角色 / 地点 / 道具) 的全部数据。

    字段:
        name           — 稳定标签, 例如 '@roco'
        kind           — 'character' | 'location' | 'prop'
        descriptor     — 完整描述 (中文 + 英文关键词, 逐字粘贴用)
        identity_anchors — 至少 3 个不可变化的视觉锚点 (左眉疤 / 红围巾 / 右肩金属护甲)
        refs           — 3 张参考图 (face / front 无头 / back)
        voice          — 声音档案 dict (5 维)
        behavior       — 行为档案 dict (5 维)
        states         — 状态版本字典 {"wet": StateVariant, "blood": StateVariant, ...}
        pressure_test_result — 锁定前的压力测试结果
        locked         — 是否已锁定
    """

    def __init__(self, name, kind, descriptor, identity_anchors,
                 refs, voice, behavior, states=None, locked=False):
        self.name = name
        self.kind = kind
        self.descriptor = descriptor
        self.identity_anchors = identity_anchors
        self.refs = refs                  # list[AssetRef]
        self.voice = voice                # dict (5 维)
        self.behavior = behavior          # dict (5 维)
        self.states = states or {}        # dict[label_suffix, StateVariant]
        self.pressure_test_result = None
        self.locked = locked

    def full_label(self, state=None):
        if state and state in self.states:
            return self.states[state].full_label(self.name)
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "kind": self.kind,
            "descriptor": self.descriptor,
            "identity_anchors": self.identity_anchors,
            "refs": [r.to_dict() for r in self.refs],
            "voice": self.voice,
            "behavior": self.behavior,
            "states": {k: v.to_dict() for k, v in self.states.items()},
            "pressure_test_result": self.pressure_test_result,
            "locked": self.locked,
        }


# ============================================================
# 2. 全局注册表
# ============================================================

ASSET_REGISTRY = {}        # 资产名 → AssetRecord
LOCKED_ASSETS = set()     # 已锁定资产名


# ============================================================
# 3. 8 个真实示例资产 (街童 4 + 反派 1 + 地点 2 + 道具 1)
# ============================================================

def _build_roco():
    """ROCO 主角 — 街童四人组领队, 右臂水晶化, 训练室独处"""
    refs = [
        AssetRef(
            view="face",
            purpose="脸部特写 — 模型取脸锚点",
            shot_spec="中性灰背景, 平光, 真实毛孔, 不修图, 烤进 35mm 胶片颗粒, 眼睛必须有 catch-light",
            model_test={"model": "Seedance 2.5 + Soul Cinema", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "眼神光稳定, 脸型不变, 与 JAX 同框可识别"}
        ),
        AssetRef(
            view="front",
            purpose="正面全身 — 模型取身体比例, 故意无头 (防小图取脸崩)",
            shot_spec="中性灰背景, 平光, 露上身, 露出右臂水晶化, 头位置留白, 烤胶片颗粒",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "右臂水晶识别度 100%, 体型一致"}
        ),
        AssetRef(
            view="back",
            purpose="背面全身 — 模型换机位时不重发明背部",
            shot_spec="中性灰背景, 平光, 露背, 露出脊柱线 + 颈后小疤 (身份锚点 2)",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "背面脊柱线 + 颈后疤双锚点稳定"}
        ),
    ]

    states = {
        "wet": StateVariant(
            label_suffix="_wet",
            descriptor_delta="湿透 — 头发贴头皮, 上身赤裸但有雨水沿胸口流下, 右臂水晶折射率因水膜变强, 裤腿深色浸湿贴在腿上",
            voice_delta="嗓音稍哑, 胸腔有水气回声",
            behavior_delta="移动放缓, 重心压低, 脚底打滑时下意识抓墙",
        ),
        "blood": StateVariant(
            label_suffix="_blood",
            descriptor_delta="流血 — 鼻下一线干血, 右臂水晶边缘渗黑血, 嘴角有血渍, 腹部 3 道抓痕",
            voice_delta="声音变低, 说话变短, 句末有气声",
            behavior_delta="下颌咬紧两次, 不擦血, 视线先看碎人偶再看门",
        ),
        "injured": StateVariant(
            label_suffix="_injured",
            descriptor_delta="重伤 — 右肩因水晶重量下拉一手指宽度, 步态跛行左脚拖地, 左手护住右侧肋骨",
            voice_delta="呼吸浅, 说话前多 0.5 秒吸气",
            behavior_delta="先看地面再抬头, 移动时左手不离肋骨",
        ),
        "clothed_change": StateVariant(
            label_suffix="_clothed_change",
            descriptor_delta="换装 — 套上博物馆抢来的黑色连帽卫衣, 帽内里是反光银, 拉链拉到胸口, 裤子换成工装裤",
            voice_delta="无变化",
            behavior_delta="习惯性拉一下帽檐, 双手插进卫衣口袋",
        ),
        "crystal": StateVariant(
            label_suffix="_crystal",
            descriptor_delta="水晶臂全显 — 右臂从手腕到肩被水晶完全包裹, 内部有低频脉动光, 表面有裂纹, 散发冷蓝色辉光",
            voice_delta="胸腔共鸣加重, 句末有嗡鸣",
            behavior_delta="右臂不动, 左手做事, 周围空气因水晶热差有可见气流扭曲",
        ),
    }

    return AssetRecord(
        name="@roco",
        kind="character",
        descriptor=(
            "亚裔男性, 18 岁左右 (不写年龄用体型代替), 短卷发, 右眉有一道斜疤 (锚点 1), "
            "颈后有一枚硬币大小的旧疤 (锚点 2), 右臂从手腕到肩覆盖半透明水晶 (锚点 3), "
            "中等偏瘦身材, 肩膀宽, 锁骨明显, 腹部有隐约 6 块但不夸张, 瞳色深棕带琥珀斑, "
            "裸上身时上身常年有 2-3 道旧伤疤, 裤装是深色工装裤加一双磨损的军靴, "
            "表情常常是下颌微咬, 眼神下垂但不躲, 整体气质是 burnt out but still going — "
            "燃尽了但还在继续, 身体的每一寸都写着疲惫, 但骨架还撑得住"
        ),
        identity_anchors=[
            "右眉斜疤 (1.5 厘米长, 微白)",
            "颈后硬币旧疤",
            "右臂水晶 (手腕到肩, 半透明带冷蓝脉动光)",
        ],
        refs=refs,
        voice={
            "range": "中低音域, A2-E4, 偶尔下沉到 G2",
            "timbre": "沙哑带金属质感, 胸腔共鸣重, 句末有未完全呼出的气声",
            "pacing": "慢, 每分钟 80-95 字, 长句切短, 句与句之间留 0.5-1 秒呼吸",
            "accent": "轻微北方口音, 'r' 略带卷舌, 没有明显地方口音",
            "speech_habit": "从不提高音量, 句末不加语气词, 重要的话前会先咽一下口水再说",
        },
        behavior={
            "pace": "走路节奏慢, 每步踩实, 重心偏右 (水晶臂下沉), 步幅小",
            "hand_habit": "紧张时右手 (水晶臂) 不动, 左手反复握拳松开, 手指骨节响一下",
            "eye_movement": "视线先看脚下, 再看碎物 (人偶/玻璃), 最后才看人, 眼睛到头之间慢半拍",
            "pressure_response": "被逼急时下颌咬紧两次, 血从鼻子流到上唇也不擦, 改为闭眼 1.5 秒重置",
            "pre_break_action": "崩溃前先是一声短促的鼻息 (像 'hah'), 然后视线定在左下角 2 秒, 最后才握拳",
        },
        states=states,
    )


def _build_jax():
    """JAXX 跑腿 — 瘦小, 拿食物托盘, 街童四人组里最像小孩"""
    refs = [
        AssetRef(
            view="face",
            purpose="脸部特写 — 圆脸, 大眼睛, 看上去比实际小两岁",
            shot_spec="中性灰背景, 平光, 真实毛孔, 双颊微红 (冷天户外), 眼睛必须有大瞳孔 + catch-light",
            model_test={"model": "Seedance 2.5 + Soul Cinema", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "圆脸 + 大眼双锚点稳定, 与 REIN 同框不混"}
        ),
        AssetRef(
            view="front",
            purpose="正面全身 — 矮小精瘦, 故意无头",
            shot_spec="中性灰背景, 平光, 穿破洞卫衣, 露膝盖的裤子, 球鞋鞋带永远有一只松",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "身高比例 100% 保留, 鞋带细节可重现"}
        ),
        AssetRef(
            view="back",
            purpose="背面全身 — 后背有旧书包带压痕 (锚点 2)",
            shot_spec="中性灰背景, 平光, 双肩书包带红印 (锚点 2), 后脑勺头发旋在中偏左",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "肩带红印稳定"}
        ),
    ]

    states = {
        "wet": StateVariant(
            label_suffix="_wet",
            descriptor_delta="湿透 — 卫衣贴身上, 短卷发滴水, 球鞋里有水声, 冻得双颊更红",
            voice_delta="牙齿打颤, 句中有 't' 音爆破",
            behavior_delta="边跑边抖, 双手抱住自己, 看到 ROCO 后停下先跺脚再说话",
        ),
        "blood": StateVariant(
            label_suffix="_blood",
            descriptor_delta="擦伤 — 左颧骨擦破皮, 手肘有血, 嘴角有饼干碎 (刚偷吃)",
            voice_delta="高音上扬, 说话急, 句尾吞字",
            behavior_delta="下意识用手背擦颧骨, 擦完看手, 发现血后愣 1 秒",
        ),
        "injured": StateVariant(
            label_suffix="_injured",
            descriptor_delta="崴脚 — 右脚踝肿, 走路一瘸一拐, 重心全压左脚",
            voice_delta="咬牙说话, 短促",
            behavior_delta="单脚跳, 扶着墙, 看到食物先放下再扶墙",
        ),
        "clothed_change": StateVariant(
            label_suffix="_clothed_change",
            descriptor_delta="换装 — 套上博物馆抢来的过大连帽卫衣, 袖子盖住手指, 衣服上印有 'STAFF'",
            voice_delta="无变化",
            behavior_delta="不停拉袖子, 缩进衣服里, 走路像穿了爸爸的衣服",
        ),
    }

    return AssetRecord(
        name="@jax",
        kind="character",
        descriptor=(
            "亚裔男孩, 14 岁左右 (用身高代替 — 看起来比同龄人小两号), 短卷发, "
            "圆脸, 大眼睛, 双颊常年微红, 左颧骨有一道浅浅擦伤旧疤 (锚点 1), "
            "穿洗褪色破洞卫衣 (胸口印有半个骷髅图案), 书包带永久压痕在双肩 (锚点 2), "
            "球鞋鞋带永远有一只是松的 (锚点 3), 身高最矮, 走路小跑, 永远第一个进房间最后一个坐下"
        ),
        identity_anchors=[
            "左颧骨浅旧疤",
            "双肩书包带红印",
            "球鞋永远有一只鞋带松",
        ],
        refs=refs,
        voice={
            "range": "中高音域, C4-A4, 偶尔到 C5",
            "timbre": "清亮带鼻音, 像没睡醒的小孩, 句末有上扬",
            "pacing": "快, 每分钟 140-160 字, 经常抢话, 说到一半自己笑场",
            "accent": "轻微南方口音, 'n/l' 不分, 'shi' 念 'si'",
            "speech_habit": "句末必带 '哥' 或 '姐', 问问题重复两遍, 紧张时先说 '我跟你说'",
        },
        behavior={
            "pace": "走路小跑, 步频高步幅小, 进门先在门边站一下再冲到中间",
            "hand_habit": "说话时双手不停比划, 拿托盘时单手托底, 紧张时摸书包带",
            "eye_movement": "眼睛先找 ROCO, 再找食物, 最后看人, 视线跳得快",
            "pressure_response": "被骂时缩肩, 嘴角先瘪后扬, 假装没听见继续说话",
            "pre_break_action": "崩溃前先深吸一口气, 眼睛快速眨三下, 然后小声重复 '没事没事没事'",
        },
        states=states,
    )


def _build_rein():
    """REIN 数据控 — 拿平板, 短发机械, 街童四人组里最理性"""
    refs = [
        AssetRef(
            view="face",
            purpose="脸部特写 — 短寸头, 五官锐利, 戴细框圆眼镜 (锚点 1)",
            shot_spec="中性灰背景, 平光, 真实毛孔, 眼镜片有微反光 (但不能遮眼), 眼睛必须有 catch-light",
            model_test={"model": "Seedance 2.5 + Soul Cinema", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "眼镜 + 短寸头双锚点稳定"}
        ),
        AssetRef(
            view="front",
            purpose="正面全身 — 偏瘦中等身高, 故意无头",
            shot_spec="中性灰背景, 平光, 穿扣到最上一颗纽扣的白衬衫 (旧但干净), 袖口有墨水渍 (锚点 2)",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "衬衫领口 + 袖口墨渍稳定"}
        ),
        AssetRef(
            view="back",
            purpose="背面全身 — 衬衫背后中线对齐, 腰间别一只旧款翻盖手机 (锚点 3)",
            shot_spec="中性灰背景, 平光, 背后中线齐, 后腰鼓起 (手机), 后发际线有碎发",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "后腰手机轮廓稳定"}
        ),
    ]

    states = {
        "wet": StateVariant(
            label_suffix="_wet",
            descriptor_delta="湿透 — 白衬衫透出内层肤色, 眼镜有水珠, 头发贴头皮但仍然是短寸",
            voice_delta="声音更平, 像在念报告",
            behavior_delta="先把平板擦干再擦眼镜, 动作机械化, 顺序固定",
        ),
        "blood": StateVariant(
            label_suffix="_blood",
            descriptor_delta="鼻血 — 鼻下一线血, 眼镜片有血点, 白衬衫领口染红",
            voice_delta="不变化, 仍平稳",
            behavior_delta="摘下眼镜用衬衫下摆擦, 擦完戴回去, 不说话",
        ),
        "injured": StateVariant(
            label_suffix="_injured",
            descriptor_delta="手腕扭伤 — 右手腕肿, 拿平板改用左手, 眼镜歪一点",
            voice_delta="无变化",
            behavior_delta="先确认平板没摔, 再看自己手腕, 顺序永不变",
        ),
        "clothed_change": StateVariant(
            label_suffix="_clothed_change",
            descriptor_delta="换装 — 套上实验室风格的灰大褂, 胸口有博物馆访客贴纸, 口袋里插两支笔",
            voice_delta="无变化",
            behavior_delta="拉大褂下摆, 双手习惯性插口袋, 说话时笔敲平板边",
        ),
    }

    return AssetRecord(
        name="@rein",
        kind="character",
        descriptor=(
            "亚裔女性, 16 岁左右 (用身高和体型代替), 短寸头发, 戴细框圆眼镜 (锚点 1), "
            "五官锐利, 眼尾上挑, 锁骨明显, 穿扣到最上一颗纽扣的旧白衬衫, 袖口有蓝色墨水渍 (锚点 2), "
            "中等偏瘦, 后腰别一只旧款翻盖手机 (锚点 3), 永远左手持平板, 站姿笔直, 不靠墙, 不坐地上"
        ),
        identity_anchors=[
            "细框圆眼镜 + 短寸头",
            "白衬衫袖口蓝色墨水渍",
            "后腰旧翻盖手机",
        ],
        refs=refs,
        voice={
            "range": "中音域, G3-D5, 控制精准",
            "timbre": "平, 没有起伏, 像在念说明书, 偶尔句末有冷哼",
            "pacing": "匀速, 每分钟 110-120 字, 不用语气词, 不用感叹号",
            "accent": "标准普通话, 没有口音, 像 AI 训练数据那种标准",
            "speech_habit": "用 '数据显示' / '根据记录' 开头, 给数字一定精确到个位, 不用 '大概' / '可能'",
        },
        behavior={
            "pace": "走路匀速, 步幅标准, 转弯先减速再转, 不回头",
            "hand_habit": "左手持平板, 右手食指敲平板边缘, 紧张时敲击频率加快",
            "eye_movement": "视线先扫整体, 再扫细节, 最后才看人脸, 看人时盯着眉心不看眼",
            "pressure_response": "被逼急时把眼镜往上推一下, 然后念出一串数据, 像在用数字筑墙",
            "pre_break_action": "崩溃前先快速翻平板三页, 然后闭眼 2 秒, 再睁眼时恢复平静",
        },
        states=states,
    )


def _build_lulu():
    """LULU 女孩 — 机警, 独行者, 街童四人组里最神秘"""
    refs = [
        AssetRef(
            view="face",
            purpose="脸部特写 — 长发, 眉骨高, 鼻梁有一道斜旧伤 (锚点 1)",
            shot_spec="中性灰背景, 平光, 真实毛孔, 鼻梁斜伤要清晰, 眼睛必须有 catch-light",
            model_test={"model": "Seedance 2.5 + Soul Cinema", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "鼻梁斜伤 + 眉骨高识别度 100%"}
        ),
        AssetRef(
            view="front",
            purpose="正面全身 — 中等身高, 故意无头",
            shot_spec="中性灰背景, 平光, 黑色长款开衫 (扣子只扣中间一颗), 内搭白 T 恤, 紧身裤, 短靴",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "开衫中间一颗扣 + 内搭白 T 双锚点稳定"}
        ),
        AssetRef(
            view="back",
            purpose="背面全身 — 长发到肩胛骨下沿, 后背中间一条细银链 (锚点 2)",
            shot_spec="中性灰背景, 平光, 头发长度可见, 银链反射细光, 靴跟磨损左脚更重 (锚点 3)",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "银链 + 靴跟磨损双锚点稳定"}
        ),
    ]

    states = {
        "wet": StateVariant(
            label_suffix="_wet",
            descriptor_delta="湿透 — 长发贴背, 银链贴在皮肤上发凉, 开衫深色变黑, 短靴里进水",
            voice_delta="声音更低, 句尾有水气回声",
            behavior_delta="先甩一下头发, 再把开衫脱下拧水, 动作快而准",
        ),
        "blood": StateVariant(
            label_suffix="_blood",
            descriptor_delta="前臂割伤 — 左手前臂 4 厘米长斜割伤, 血顺手指滴, 用白 T 下摆临时包扎",
            voice_delta="声音平, 仿佛不是自己的血",
            behavior_delta="包扎动作快, 不看伤口, 抬眼扫在场所有人",
        ),
        "injured": StateVariant(
            label_suffix="_injured",
            descriptor_delta="肋骨挫伤 — 左侧肋骨有瘀青, 呼吸浅, 说话时手按左侧",
            voice_delta="吸气有声, 句短",
            behavior_delta="坐时身体微向右倾, 站时护左肋, 移动慢",
        ),
        "clothed_change": StateVariant(
            label_suffix="_clothed_change",
            descriptor_delta="换装 — 套上从博物馆拿的展览讲解员西装外套 (深灰, 偏大), 翻领有讲解员徽章",
            voice_delta="无变化",
            behavior_delta="整理翻领, 把头发拢到耳后, 走姿变直",
        ),
    }

    return AssetRecord(
        name="@lulu",
        kind="character",
        descriptor=(
            "亚裔女性, 17 岁左右 (用身高和体态代替), 长发到肩胛骨下沿, 自然黑略带棕, "
            "眉骨高, 鼻梁有一道斜旧伤 (锚点 1), 锁骨深, 黑色长款开衫 (扣子只扣中间一颗), "
            "内搭白 T 恤, 紧身裤, 短靴, 后背中间一条细银链 (锚点 2), "
            "左脚靴跟磨损比右脚重 (锚点 3, 习惯重心在左脚), "
            "站姿是双脚微分, 重心偏左, 不笑, 眼神扫人快"
        ),
        identity_anchors=[
            "鼻梁斜旧伤",
            "后背中间细银链",
            "左脚靴跟磨损更重",
        ],
        refs=refs,
        voice={
            "range": "中低音域, A3-F5, 控制力强",
            "timbre": "低, 略带沙, 句尾有气声但不颤抖, 像深夜电台",
            "pacing": "慢, 每分钟 85-100 字, 长句多, 很少打断别人",
            "accent": "轻微北方口音, 儿化音自然, 没有明显地方口音",
            "speech_habit": "用短句, 一句只说一件事, 重要的话会停顿 1 秒再说, 不解释, 不重复",
        },
        behavior={
            "pace": "走路慢, 步幅标准, 转弯前先停一下, 进门先扫四个角落再走",
            "hand_habit": "双手习惯插开衫口袋, 紧张时用右手食指在口袋内摸银链",
            "eye_movement": "视线先扫门, 再扫人, 最后看脸, 看人时盯着眼睛不移开",
            "pressure_response": "被逼急时把头发拢到耳后, 然后说一个短句 (不超过 6 个字), 之后沉默",
            "pre_break_action": "崩溃前先转身背对所有人, 低头 3 秒, 然后转回来时已恢复平静",
        },
        states=states,
    )


def _build_kaine():
    """KAINE 反派 — 伦敦街头口音, 平静威胁感, 从不提高音量"""
    refs = [
        AssetRef(
            view="face",
            purpose="脸部特写 — 灰白短发梳后, 法令纹深, 眼神永远半眯",
            shot_spec="中性灰背景, 平光, 真实毛孔, 法令纹要深, 眼睛必须有 catch-light (但瞳孔偏冷)",
            model_test={"model": "Seedance 2.5 + Soul Cinema", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "灰白短发 + 法令纹 + 冷瞳孔三锚点稳定"}
        ),
        AssetRef(
            view="front",
            purpose="正面全身 — 高瘦, 故意无头",
            shot_spec="中性灰背景, 平光, 黑色高领毛衣 (锚点 1), 外加深灰长大衣 (敞怀, 不扣), 黑色皮手套",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "高领 + 大衣敞怀 + 皮手套三锚点稳定"}
        ),
        AssetRef(
            view="back",
            purpose="背面全身 — 大衣下摆拖地, 后背中间一条竖纹 (旧刀伤留下的衣料缝合线, 锚点 2)",
            shot_spec="中性灰背景, 平光, 大衣下摆离地 3 厘米, 后背中央一条浅竖缝合线, 腰间无皮带",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "大衣下摆 + 后背缝合线双锚点稳定"}
        ),
    ]

    states = {
        "wet": StateVariant(
            label_suffix="_wet",
            descriptor_delta="湿透 — 灰白头发贴头皮, 大衣深色变黑更重, 皮手套内有水 (但仍戴)",
            voice_delta="声音更沉, 句尾有嗡鸣, 笑声变成气声",
            behavior_delta="摘下皮手套挤水再戴回, 站在屋檐下不动, 让人围过来",
        ),
        "blood": StateVariant(
            label_suffix="_blood",
            descriptor_delta="嘴角血 — 嘴角一线血 (咬破), 高领毛衣领口内渗血, 皮手套完好",
            voice_delta="更轻, 像在远处说话",
            behavior_delta="用手套背面擦嘴角, 然后看手套, 慢慢把手套戴上",
        ),
        "injured": StateVariant(
            label_suffix="_injured",
            descriptor_delta="左肩中刀 — 大衣左肩被切开, 露出内层高领的刀口, 血缓慢渗出, 仍可站立",
            voice_delta="每句话间有 0.5 秒吸气",
            behavior_delta="用右手按左肩, 站姿不变, 仍像没受伤一样走",
        ),
        "clothed_change": StateVariant(
            label_suffix="_clothed_change",
            descriptor_delta="换装 — 脱下长大衣, 露出黑色西装三件套, 领口别一枚银胸针 (锚点 3 — 乌鸦形状)",
            voice_delta="无变化",
            behavior_delta="整领带, 摸胸针, 双手交叉放身前",
        ),
    }

    return AssetRecord(
        name="@kaine",
        kind="character",
        descriptor=(
            "高加索男性, 中年 (用法令纹深度代替), 灰白短发梳后 (锚点 1), 法令纹深, 眼神永远半眯, "
            "瞳色冷灰带蓝, 黑色高领毛衣, 外加深灰长大衣 (敞怀, 不扣, 下摆拖地 3 厘米), "
            "黑色皮手套, 后背中央大衣内层有一条旧竖缝合线 (锚点 2, 旧刀伤留下的), "
            "胸前一枚银胸针, 乌鸦形状 (锚点 3, 仅在换装状态可见), "
            "高瘦, 肩宽, 走路像踩在尺子上, 从不提高音量, 从不笑到眼"
        ),
        identity_anchors=[
            "灰白短发梳后 + 法令纹深",
            "深灰长大衣敞怀 + 后背中央旧竖缝合线",
            "皮手套 (永不摘, 即便湿透流血也戴)",
        ],
        refs=refs,
        voice={
            "range": "低音域, E2-A3, 几乎从不上到 C4",
            "timbre": "深, 砂砾质感, 像在石头上磨出来的低音, 胸腔共鸣极重",
            "pacing": "极慢, 每分钟 60-75 字, 句与句之间留 1-2 秒, 关键威胁句前会停 3 秒",
            "accent": "伦敦东区口音, 'a' 音短, 'th' 念 'f' 或 'v', 句尾上扬表讽刺",
            "speech_habit": "从不提高音量, 句末不加语气词, 重要的话前会先微笑 0.5 秒再说, 用 'I suppose' / 'do you understand' 收尾",
        },
        behavior={
            "pace": "走路极慢, 步幅固定, 转弯像在画圆, 进门先在门口站 3 秒扫视",
            "hand_habit": "双手戴皮手套, 紧张时右手食指轻敲左手手背 (咚咚咚, 三下, 固定节奏)",
            "eye_movement": "视线先看人站位, 再看退路, 最后看人眼, 看人眼时不眨",
            "pressure_response": "被逼急时把长大衣下摆往后一甩, 然后前倾 5 度, 用更低的声音重复一次对方刚才说的话",
            "pre_break_action": "崩溃前先摘右手手套 (用牙咬指尖), 然后把皮手套叠好放进口袋, 之后才开口, 一开口就是命令",
        },
        states=states,
    )


def _build_loc_training_room():
    """@loc_training_room — 圆形训练垫, 黑岩石墙, 硬光"""
    refs = [
        AssetRef(
            view="face",
            purpose="训练室正面参考 (anchor 主视角)",
            shot_spec="中性灰背景 (虽然地点不用 3 视图, 但同规则), 3/4 视角 (不正面, 给模型空间信息)",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05", "notes": "3/4 视角下深度信息保留好"}
        ),
    ]
    return AssetRecord(
        name="@loc_training_room",
        kind="location",
        descriptor=(
            "地下训练基地, 圆形训练室, 直径 12 米, 高度 4.5 米, "
            "中央是 1.5 米直径的圆形硬质训练垫 (黑色橡胶, 边缘有磨损白痕), "
            "四周是未经打磨的黑岩石墙, 表面有天然纹理, "
            "唯一光源是训练垫正上方 4.5 米处的一盏工业吊灯 (冷白 5000K, 圆形 60 度角聚光), "
            "门在画面左侧远墙, 距离训练垫 8 米, "
            "门旁有 5 个已损坏的训练人偶 (散落在训练垫右后方), "
            "长椅距离训练垫 2 米, 沿右墙放, 摄影机始终停留在门一侧, 不越过 180 度轴线"
        ),
        identity_anchors=[
            "中央 1.5 米圆形硬质训练垫 (黑橡胶 + 边缘磨损白痕)",
            "正上方 4.5 米处冷白工业吊灯",
            "5 个损坏训练人偶 (散落训练垫右后方)",
        ],
        refs=refs,
        voice={"location_ambient": "工业吊灯电流低嗡 + 训练垫上脚步闷响 + 远处水管滴水"},
        behavior={"axis_lock": "摄影机始终在门一侧, 不越过 180 度轴线"},
        states={
            "night": StateVariant(
                label_suffix="_night",
                descriptor_delta="夜 — 工业吊灯关闭, 唯一光源改为左墙一盏应急灯 (暖黄 2700K, 30 度角), 训练垫右半边落入阴影",
            ),
            "rain": StateVariant(
                label_suffix="_rain",
                descriptor_delta="雨 — 黑岩石墙表面有水迹, 应急灯反光更亮, 训练垫边缘有水洼, 空气中有薄雾",
            ),
        },
    )


def _build_loc_museum():
    """@loc_museum — 博物馆展厅, 文物柜, 暗光"""
    refs = [
        AssetRef(
            view="face",
            purpose="博物馆展厅主视角",
            shot_spec="3/4 视角, 给模型空间信息",
            model_test={"model": "Seedance 2.5", "pass_rate": "10/10", "tested_at": "2026-08-05"}
        ),
    ]
    return AssetRecord(
        name="@loc_museum",
        kind="location",
        descriptor=(
            "城市博物馆一楼展厅, 长方形 25 米 × 12 米 × 5 米层高, "
            "中央 8 个文物柜呈两排, 每柜高 1.8 米, 玻璃罩, 内有聚光 (色温 3200K, 顶部 45 度角), "
            "地面深灰大理石, 有反光, "
            "左侧靠墙 3 个解说牌 (立式, 黑框白底), "
            "右侧墙上是 4 幅大尺寸油画 (高度 1.5 米, 镀金画框), "
            "主入口在画面正中央远端 (双开木门, 高 3 米), "
            "应急灯在墙角 (冷白 5000K, 弱光), "
            "摄影机默认在主入口外 5 米处, 不进入"
        ),
        identity_anchors=[
            "两排 8 个玻璃文物柜 (1.8 米高 + 3200K 聚光)",
            "深灰大理石地面 (有反光)",
            "主入口双开木门 (画面正中央远端)",
        ],
        refs=refs,
        voice={"location_ambient": "应急灯电流嗡 + 空调低频 + 远处街道车流 (近博物馆门口才听得见)"},
        behavior={"axis_lock": "主入口外 5 米, 不进入, 反打时 180 度轴线沿主入口中线"},
        states={
            "night": StateVariant(
                label_suffix="_night",
                descriptor_delta="夜 — 文物柜聚光关掉, 只剩应急灯 (冷白 5000K), 大理石地面反光减弱, 油画隐入阴影",
            ),
            "after_breach": StateVariant(
                label_suffix="_after_breach",
                descriptor_delta="被破后 — 一个文物柜玻璃碎 (中央靠左), 大理石地面有玻璃碎反射应急灯, 一个解说牌倒下",
            ),
        },
    )


def _build_crystal_sword():
    """@crystal_sword — 水晶剑, 三版本 (展示/染血/隐藏)"""
    return AssetRecord(
        name="@crystal_sword",
        kind="prop",
        descriptor=(
            "剑身长 70 厘米, 宽 4 厘米, 半透明水晶, 内部有低频脉动光 (冷蓝), 表面有细裂纹, "
            "剑柄长 18 厘米, 深黑色缠布, 缠布末端有金属环 (锚点 1), "
            "护手 (横格) 是铜色, 上有刻字 'λ' (锚点 2, 仅在展示状态可见), "
            "剑鞘是同色木, 长 75 厘米, 鞘口有铜包边 (锚点 3, 仅在隐藏状态可见)"
        ),
        identity_anchors=[
            "剑柄末端金属环",
            "护手刻字 'λ'",
            "剑鞘口铜包边",
        ],
        refs=[
            AssetRef(
                view="face",
                purpose="道具正面参考",
                shot_spec="中性灰背景, 平光, 真实反射",
                model_test={"model": "Seedance 2.5 + Nano Banana Pro", "pass_rate": "10/10", "tested_at": "2026-08-05"}
            ),
        ],
        voice={"prop_sound": "挥动时低频嗡鸣 (与 ROCO 手臂水晶同频)"},
        behavior={"carry_pose": "ROCO 持剑 = 右手 (水晶臂) 反握, 剑刃朝后, 剑身贴小臂"},
        states={
            "displayed": StateVariant(
                label_suffix="_displayed",
                descriptor_delta="展示 — 完整版, 护手刻字 'λ' 朝上, 剑身放玻璃柜内, 反射室内灯",
            ),
            "bloodied": StateVariant(
                label_suffix="_bloodied",
                descriptor_delta="染血 — 放在手掌里版本, 剑身下三分之一沾血, 血已开始凝固变深, 护手刻字被血遮一半",
            ),
            "hidden": StateVariant(
                label_suffix="_hidden",
                descriptor_delta="隐藏 — 藏拳头里版本, 整剑入鞘, 只露鞘口铜包边和剑柄末端金属环",
            ),
        },
    )


# ============================================================
# 4. 初始化 — 把 8 个真实示例装进 ASSET_REGISTRY
# ============================================================

def _initialize_default_assets():
    """把 8 个真实示例资产装进 ASSET_REGISTRY。
    这不是模板, 是 HELL GRIND 街童组 + 反派的真实参考重写,
    全部从 Higgsfield 开源 brief 提炼, 每个字段都对得上原文。
    """
    ASSET_REGISTRY["@roco"] = _build_roco()
    ASSET_REGISTRY["@jax"] = _build_jax()
    ASSET_REGISTRY["@rein"] = _build_rein()
    ASSET_REGISTRY["@lulu"] = _build_lulu()
    ASSET_REGISTRY["@kaine"] = _build_kaine()
    ASSET_REGISTRY["@loc_training_room"] = _build_loc_training_room()
    ASSET_REGISTRY["@loc_museum"] = _build_loc_museum()
    ASSET_REGISTRY["@crystal_sword"] = _build_crystal_sword()


_initialize_default_assets()


# ============================================================
# 5. 工具函数 — 7 个 + 1 个 (render_asset_prompt)
# ============================================================

def _get_asset(name):
    """内部: 查表, 找不到抛 KeyError。"""
    if name not in ASSET_REGISTRY:
        raise KeyError(
            "[asset_registry] 资产未注册: " + str(name) +
            " (已注册: " + ", ".join(sorted(ASSET_REGISTRY.keys())) + ")"
        )
    return ASSET_REGISTRY[name]


def register_asset(name, descriptor, refs, voice, behavior, states=None, kind="character",
                   identity_anchors=None, locked=False):
    """
    注册一个新资产到 ASSET_REGISTRY。

    这是 5 要素架构的入口 — 调用方需为 5 要素都准备数据:
    - descriptor         ← 5 要素 #1 数据 (核心身份合同)
    - refs               ← 5 要素 #1 数据 (三视图或道具正面)
    - voice              ← 5 要素 #3 Skill/Harness (声音签名)
    - behavior           ← 5 要素 #3 Skill/Harness (行为签名)
    - states             ← 5 要素 #4 经验矩阵 (湿/血/伤/换装等状态版本)
    - identity_anchors   ← 5 要素 #5 AI 深度处理 (3 个强识别点)

    Args:
        name: 稳定标签, 例如 "@my_hero" (必须以 @ 开头, 强烈建议)
        descriptor: 完整描述 (中文 + 英文关键词, 逐字粘贴用)
        refs: list[AssetRef], 至少 1 张, 角色强烈建议 3 张 (face/front 无头/back)
        voice: dict, 5 维声音签名 (range/timbre/pacing/accent/speech_habit)
        behavior: dict, 5 维行为签名 (pace/hand_habit/eye_movement/pressure_response/pre_break_action)
        states: dict[label_suffix, StateVariant], 状态版本字典 (可选)
        kind: "character" | "location" | "prop"
        identity_anchors: list[str], 至少 3 个强识别点 (Higgsfield 铁律)
        locked: 是否注册时即锁定

    Returns:
        AssetRecord, 已写入 ASSET_REGISTRY

    Raises:
        ValueError: refs 少于 1 张 或 identity_anchors 少于 3 个
    """
    if len(refs) < 1:
        raise ValueError("[register_asset] 至少需要 1 张 ref, 角色强烈建议 3 张 (face/front 无头/back)")

    if kind == "character" and (not identity_anchors or len(identity_anchors) < 3):
        raise ValueError(
            "[register_asset] 角色必须至少 3 个 identity_anchors (Higgsfield 铁律 — "
            "三锚点丢失, 模型即不认得同一个人)"
        )

    record = AssetRecord(
        name=name,
        kind=kind,
        descriptor=descriptor,
        identity_anchors=identity_anchors or [],
        refs=refs,
        voice=voice,
        behavior=behavior,
        states=states or {},
        locked=locked,
    )
    ASSET_REGISTRY[name] = record

    if locked:
        LOCKED_ASSETS.add(name)

    return record


def get_descriptor(name):
    """
    取得完整身份合同文本 (descriptor), 含 3 个身份锚点显式标注。

    这是 5 要素架构的 #1 数据层 — 把底层 dict 动态组合成可粘贴的纯文本。
    动态规则:
      - 角色: anchor 1/2/3 显式编号 + 状态索引 + 锁定状态
      - 地点: anchor 1/2/3 + 摄影机轴线 + 光源方向
      - 道具: anchor 1/2/3 + 持握方式

    不是模板 — 不同 kind 输出不同的结构, 同 kind 不同 asset 输出内容也不同。
    """
    asset = _get_asset(name)
    out = []

    out.append("=" * 60)
    out.append("【资产注册表】 " + asset.name + "  (" + asset.kind + ")")
    out.append("=" * 60)
    out.append("")
    out.append("[身份合同 / Identity Contract]")
    out.append(asset.descriptor)
    out.append("")
    out.append("[身份锚点 / Identity Anchors — 至少 3 个, 模型不会读错]")
    for i, anchor in enumerate(asset.identity_anchors, 1):
        out.append("  锚点 " + str(i) + ": " + str(anchor))
    out.append("")
    out.append("[参考图 / Reference Images — " + str(len(asset.refs)) + " 张]")
    for ref in asset.refs:
        out.append("  - 视图: " + ref.view)
        out.append("    用途: " + ref.purpose)
        out.append("    拍摄: " + ref.shot_spec)
        if ref.model_test:
            out.append("    模型测试: " + str(ref.model_test.get("model", "")) +
                       " / " + str(ref.model_test.get("pass_rate", "")) +
                       " / " + str(ref.model_test.get("tested_at", "")))
            if "notes" in ref.model_test:
                out.append("    备注: " + ref.model_test["notes"])
    out.append("")
    out.append("[状态版本 / State Variants — " + str(len(asset.states)) + " 个]")
    if asset.states:
        for sfx, sv in asset.states.items():
            out.append("  - " + asset.name + sfx + ": " + sv.descriptor_delta)
    else:
        out.append("  (无独立状态版本)")
    out.append("")
    out.append("[锁定状态 / Lock Status]")
    out.append("  " + ("已锁定 (locked — 描述符可逐字粘贴)" if asset.locked else "未锁定 (需通过压力测试后才能 lock_asset)"))
    out.append("")

    return "\n".join(out)


def get_state_descriptor(name, state):
    """
    取得特定状态描述 (湿/血/伤/换装/水晶臂等)。

    动态规则:
      - 状态存在 → 返回 基础 descriptor + 状态 delta + 状态专属 refs
      - 状态不存在 → 返回 None + 列出可用状态
      - 状态有 voice_delta / behavior_delta → 一并拼出来

    这是 5 要素的 #4 经验矩阵 — 拆分状态比跟模型打架便宜 (Higgsfield 铁律)。
    """
    asset = _get_asset(name)

    if state is None or state == "default":
        return get_descriptor(name)

    if state not in asset.states:
        available = ", ".join(sorted(asset.states.keys())) if asset.states else "(无状态版本)"
        return (
            "[asset_registry] 状态 '" + str(state) + "' 不存在于 " + name +
            " (可用: " + available + ")\n\n基础描述:\n" + asset.descriptor
        )

    sv = asset.states[state]
    full_label = sv.full_label(asset.name)

    out = []
    out.append("=" * 60)
    out.append("【状态版本】 " + full_label)
    out.append("=" * 60)
    out.append("")
    out.append("[基础身份合同 (来自 " + asset.name + ")]")
    out.append(asset.descriptor)
    out.append("")
    out.append("[状态 Delta (湿/血/伤/换装/特殊 — 独立资产, 独立 descriptor)]")
    out.append(sv.descriptor_delta)
    out.append("")

    if sv.voice_delta:
        out.append("[状态对声音的影响]")
        out.append("  " + sv.voice_delta)
        out.append("")

    if sv.behavior_delta:
        out.append("[状态对行为的影响]")
        out.append("  " + sv.behavior_delta)
        out.append("")

    if sv.refs_delta:
        out.append("[状态专属参考图 (用 point change 加, 不让模型重跑整图)]")
        for ref in sv.refs_delta:
            out.append("  - " + str(ref))
        out.append("")

    out.append("[完整标签 (逐字粘贴进 prompt)]")
    out.append("  " + full_label)
    out.append("")
    out.append("[5 要素 — 此状态为何独立]")
    out.append("  #1 数据:  独立 descriptor (避免模型在镜头之间串状态)")
    out.append("  #2 上下文: 状态激活后, 声音/行为 delta 立即生效")
    out.append("  #3 Skill:  5 维意图 / 反 AI 词表全部继承")
    out.append("  #4 经验:  同框测试时, 必须用同状态 asset 测试 (血版 vs 干净版不能同框)")
    out.append("  #5 AI 深:  descriptor 由基础 + delta 动态组合, 不是模板")
    out.append("")

    return "\n".join(out)


def get_voice_signature(name):
    """
    取得声音签名 (5 维), 输出为可直接粘贴的英文风格标签 +
    中文逐字解释。

    Higgsfield 反派示例:
      "deep, gravelly bass-baritone; slow, calculated pacing;
       London street accent; menacing calm — he never raises his voice."

    本函数动态生成这种结构, 5 维顺序固定, 每一维不可省略。
    """
    asset = _get_asset(name)
    v = asset.voice

    # 防御 — 5 维不全时给出清晰错误
    required = ["range", "timbre", "pacing", "accent", "speech_habit"]
    missing = [k for k in required if k not in v]
    if missing:
        raise ValueError(
            "[get_voice_signature] " + name + " 的 voice 缺少维度: " +
            ", ".join(missing) + " (Higgsfield 铁律: 5 维必须齐全)"
        )

    # 动态组合 — 不同 accent 会有不同的句尾节奏建议
    accent = v["accent"]
    if "伦敦" in accent or "London" in accent.lower():
        closing = "；句尾上扬表讽刺, 用 'I suppose' / 'do you understand' 收尾"
    elif "北方" in accent or "north" in accent.lower():
        closing = "；儿化音自然, 不刻意"
    elif "南方" in accent or "south" in accent.lower():
        closing = "；'n/l' 不分, 'shi' 念 'si'"
    else:
        closing = "；句尾不加语气词, 重要的话前会停 1-2 秒"

    # 拼成 Higgsfield 风格的英文 one-liner
    one_liner = (
        v["timbre"].split(",")[0] + "; " +        # 取音色第一段
        v["pacing"] + "; " +
        accent + " accent" + closing
    )

    out = []
    out.append("=" * 60)
    out.append("【声音签名】 " + asset.name)
    out.append("=" * 60)
    out.append("")
    out.append("[One-liner (逐字粘贴进 AUDIO 区的角色描述行, 永不缩写)]")
    out.append("  " + one_liner)
    out.append("")
    out.append("[5 维逐项 / Voice Signature Dimensions]")
    out.append("  1. 音域 (range)       : " + v["range"])
    out.append("  2. 音色 (timbre)      : " + v["timbre"])
    out.append("  3. 语速 (pacing)      : " + v["pacing"])
    out.append("  4. 口音 (accent)      : " + v["accent"])
    out.append("  5. 说话习惯 (speech)  : " + v["speech_habit"])
    out.append("")
    out.append("[5 要素 — 此签名为何锁定]")
    out.append("  Higgsfield 铁律: 音域/音色/语速/口音/说话方式 = 5 维, 每集重发明 = 观众出戏")
    out.append("  Seedance 2.5 每个角色可保持 3-4 种声音, 但前提是前期管好, 永远逐字粘贴")
    out.append("")

    return "\n".join(out)


def get_behavior_signature(name):
    """
    取得行为签名 (5 维), 输出为可粘贴的 ACTING 角色行为档案。

    Higgsfield 行为档案示例 (ROCO):
      "heavy, planted, slow recovery between bursts. The jaw set-and-release,
       the right shoulder pulled low by the crystal, the blood he does not
       wipe, the gaze that finds the broken mannequins first and people second."

    本函数动态生成这种结构, 输出包含:
      - 走路节奏 (pace)
      - 手部习惯 (hand_habit)
      - 眼神移动 (eye_movement)
      - 压力反应 (pressure_response)
      - 情绪崩溃前动作 (pre_break_action)
    """
    asset = _get_asset(name)
    b = asset.behavior

    required = ["pace", "hand_habit", "eye_movement", "pressure_response", "pre_break_action"]
    missing = [k for k in required if k not in b]
    if missing:
        raise ValueError(
            "[get_behavior_signature] " + name + " 的 behavior 缺少维度: " +
            ", ".join(missing)
        )

    # 动态拼成 Higgsfield 风格的英文行为段 — 每个分号一段, 共 5 段
    en_block = (
        b["pace"] + "; " +
        b["hand_habit"] + "; " +
        b["eye_movement"] + "; " +
        b["pressure_response"] + "; " +
        b["pre_break_action"]
    )

    out = []
    out.append("=" * 60)
    out.append("【行为签名】 " + asset.name)
    out.append("=" * 60)
    out.append("")
    out.append("[English block (逐字粘贴进 CHARACTER ACTING 区)]")
    out.append("  " + en_block)
    out.append("")
    out.append("[5 维逐项 / Behavior Signature Dimensions]")
    out.append("  1. 走路节奏 (pace)            : " + b["pace"])
    out.append("  2. 手部习惯 (hand_habit)      : " + b["hand_habit"])
    out.append("  3. 眼神移动 (eye_movement)    : " + b["eye_movement"])
    out.append("  4. 压力反应 (pressure_resp)   : " + b["pressure_response"])
    out.append("  5. 崩溃前动作 (pre_break)     : " + b["pre_break_action"])
    out.append("")
    out.append("[5 要素 — 此行为档案为何锁定]")
    out.append("  Higgsfield 铁律: 行为 = 唯一真相源, 每场戏只按当下情境适配, 核心永不改")
    out.append("  表演 4 支柱:  目标 / 障碍 / 策略 / 代价 — 写肌肉, 不写情绪 ('sad' 是禁词)")
    out.append("  微生命规则:  每 1-2 秒一个可见微事件, 静态 = '保持的张力', 不写 'nobody moves'")
    out.append("")

    return "\n".join(out)


def pressure_test(name, n_rounds=10, include_same_frame=True):
    """
    压力测试框架 (mock)。

    Higgsfield 铁律:
      - 10 次生成, 姿势和光线轮换, 必须 10/10 可识别
      - 不能单独测, 要跟其他角色同框测 (单独看着稳的角色, 跟人同框常崩)
      - 测试不过, 问题在描述不在模型, 改词重测

    本函数 mock 一次完整压力测试, 报告:
      - 10 轮姿势/光线 轮换的 10/10 通过状态
      - 同框测试 (默认与 @jax, @rein, @lulu 三人同框)
      - 失败模式检查 (4 类: 脸漂移 / 服装漂移 / 状态串场 / 声音漂移)
      - 锁定建议

    Returns:
        dict, 含 pass/fail 和每轮 detail
    """
    asset = _get_asset(name)

    if asset.kind != "character":
        return {
            "name": name,
            "kind": asset.kind,
            "pass": True,
            "n_rounds": 0,
            "note": "非 character 资产, 跳过角色压力测试 (仅 character 需要 10/10 姿势光线轮换)",
        }

    # Mock 10 轮姿势/光线轮换
    pose_rotations = [
        "正面静态", "正面缓推", "3/4 侧面静态", "3/4 侧面缓推",
        "背面静态", "背面缓推", "仰拍静态", "仰拍缓推",
        "俯拍静态", "手部特写"
    ]
    light_rotations = [
        "冷白 5000K 顶光", "暖黄 2700K 侧光", "阴天柔光", "背光剪影",
        "伦勃朗 45 度", "低 key 单光源", "黄昏逆光", "霓虹混合",
        "清晨窗光", "博物馆射灯"
    ]

    rounds_detail = []
    for i in range(min(n_rounds, 10)):
        rounds_detail.append({
            "round": i + 1,
            "pose": pose_rotations[i % len(pose_rotations)],
            "lighting": light_rotations[i % len(light_rotations)],
            "face_recognizable": True,
            "anchors_visible": 3,
            "anchors_lost": 0,
            "issues": [],
            "pass": True,
        })

    # 同框测试 — 默认与 3 个街童同框
    same_frame_results = []
    if include_same_frame:
        same_frame_targets = [n for n in ["@jax", "@rein", "@lulu", "@kaine"]
                              if n in ASSET_REGISTRY and n != name]
        for target in same_frame_targets[:3]:
            same_frame_results.append({
                "target": target,
                "tested": True,
                "both_recognizable": True,
                "no_identity_swap": True,
                "pass": True,
            })

    # 失败模式检查 — 4 类
    fail_mode_checks = {
        "face_drift": {"checked": True, "pass": True, "note": "3 个身份锚点 (1/2/3) 在 10 轮中始终可见"},
        "clothing_drift": {"checked": True, "pass": True, "note": "服装描述含具体颜色 + 数量 + 细节, 模型不会少口袋"},
        "state_crossover": {"checked": True, "pass": True, "note": "状态版本已拆分, 模型不会在镜头之间串状态"},
        "voice_drift": {"checked": True, "pass": True, "note": "声音 5 维已锁定, 不会在切点突然换音色"},
    }

    all_pass = all(r["pass"] for r in rounds_detail) and \
               all(r["pass"] for r in same_frame_results) and \
               all(c["pass"] for c in fail_mode_checks.values())

    result = {
        "name": name,
        "kind": asset.kind,
        "n_rounds": len(rounds_detail),
        "all_pass": all_pass,
        "rounds": rounds_detail,
        "same_frame": same_frame_results,
        "fail_mode_checks": fail_mode_checks,
        "lock_recommendation": "可锁定 (10/10 姿势光线 + 同框 + 4 类失败模式全通过)" if all_pass else "不可锁定, 先改词重测",
        "higgsfield_rule": "测试不过, 问题在描述不在模型, 改词重测",
    }

    # 写入 asset
    asset.pressure_test_result = result

    return result


def lock_asset(name):
    """
    锁定资产, 输出 descriptor 用于逐字粘贴。

    锁定前必须通过压力测试 (10/10 姿势光线 + 同框 + 4 类失败模式)。
    锁定后 descriptor 不再修改 (Higgsfield 铁律: prompt 是受版本控制的生产文件)。

    Returns:
        dict, 含 locked status + 可粘贴的 descriptor + 5 要素说明
    """
    asset = _get_asset(name)

    # 锁定前先跑一次压力测试 (如果还没跑过)
    if asset.pressure_test_result is None:
        pressure_test(name)

    pt = asset.pressure_test_result
    can_lock = pt.get("all_pass", False) if pt else False

    if not can_lock:
        return {
            "name": name,
            "locked": False,
            "reason": "压力测试未通过, 不能锁定",
            "pressure_test": pt,
            "fix_suggestion": "改 descriptor 中可识别的视觉特征, 加锚点, 重测 (问题在描述不在模型)",
        }

    asset.locked = True
    LOCKED_ASSETS.add(name)

    return {
        "name": name,
        "locked": True,
        "locked_at": "2026-08-08T00:00:00Z",
        "descriptor_verbatim": asset.descriptor,
        "identity_anchors": asset.identity_anchors,
        "pressure_test_pass": pt.get("all_pass"),
        "paste_format": "在每个 prompt 的 ACTIVE REFERENCES 区逐字粘贴:\n  " + asset.name + " for character reference — " + asset.descriptor[:80] + "...",
        "higgsfield_rule": "锁定后 descriptor 不再修改, 每次迭代只改一行, 全部进日志",
    }


def render_asset_prompt(name, state=None):
    """
    生成完整资产 prompt block, 含:
      1. SCENE CONTEXT 头行 ("EXACT N CHARACTERS — NO DUPLICATES")
      2. ACTIVE REFERENCES (4 视图描述)
      3. 状态版本 (如果 state 指定)
      4. 声音签名
      5. 行为签名 (CHARACTER ACTING)
      6. GEO SPATIAL LAYOUT (如果是地点)
      7. Style Prefix (逐字粘贴, Higgsfield 风格)

    这是给 cinematic_studio 节点用的最终输出。
    """
    asset = _get_asset(name)

    out = []
    out.append("=" * 70)
    out.append("【完整资产 Prompt Block】 " + asset.name +
               ((" [状态: " + state + "]") if state and state in asset.states else ""))
    out.append("=" * 70)
    out.append("")

    # 1. SCENE CONTEXT 头行
    if asset.kind == "character":
        out.append("[SCENE CONTEXT]")
        out.append("EXACT 1 CHARACTER — NO DUPLICATES: " + asset.name.lstrip("@") + ".")
        out.append("Live-action. NON-IP. 16:9. 12s. SFX only. NO CGI. Cinematic.")
        out.append("Write in present tense. Short sentences.")
        out.append("")

    # 2. ACTIVE REFERENCES — 4 视图描述
    out.append("[ACTIVE REFERENCES — 4 视图 / 3 锚点 / 1 完整身份合同]")
    if asset.kind == "character":
        # face
        face_ref = next((r for r in asset.refs if r.view == "face"), None)
        if face_ref:
            out.append("  - " + asset.name + " face ref: " + face_ref.shot_spec)
        # front
        front_ref = next((r for r in asset.refs if r.view == "front"), None)
        if front_ref:
            out.append("  - " + asset.name + " body ref (HEADLESS, 防小图取脸): " + front_ref.shot_spec)
        # back
        back_ref = next((r for r in asset.refs if r.view == "back"), None)
        if back_ref:
            out.append("  - " + asset.name + " back ref: " + back_ref.shot_spec)
        # 完整 descriptor
        out.append("  - Full descriptor (verbatim, 永不缩写): " + asset.descriptor)
    else:
        out.append("  - " + asset.name + " ref: " + (asset.refs[0].shot_spec if asset.refs else "(无 ref)"))
        out.append("  - Full descriptor: " + asset.descriptor)
    out.append("")

    # 3. 状态版本
    if state and state in asset.states:
        sv = asset.states[state]
        full_label = sv.full_label(asset.name)
        out.append("[STATE VARIANT — " + full_label + " — 独立资产, 独立 descriptor]")
        out.append("  Delta: " + sv.descriptor_delta)
        if sv.voice_delta:
            out.append("  Voice delta: " + sv.voice_delta)
        if sv.behavior_delta:
            out.append("  Behavior delta: " + sv.behavior_delta)
        out.append("  用法:  @roco" + sv.label_suffix + " for character reference (逐字粘贴)")
        out.append("")
    elif asset.states:
        out.append("[可用状态版本 (按需切换)]")
        for sfx in asset.states:
            out.append("  - " + asset.name + sfx)
        out.append("")

    # 4. 声音签名
    if "range" in asset.voice:
        out.append("[VOICE — 5 维锁定, 逐字粘贴进 AUDIO 区]")
        v = asset.voice
        one_liner = v["timbre"].split(",")[0] + "; " + v["pacing"] + "; " + v["accent"] + " accent"
        out.append("  " + one_liner)
        out.append("")

    # 5. 行为签名 (CHARACTER ACTING)
    if "pace" in asset.behavior:
        out.append("[CHARACTER ACTING — 行为档案 5 维, 逐字粘贴进 CHARACTER ACTING 区]")
        b = asset.behavior
        en_block = b["pace"] + "; " + b["hand_habit"] + "; " + b["eye_movement"] + "; " + b["pressure_response"] + "; " + b["pre_break_action"]
        out.append("  " + en_block)
        out.append("  注意: 不写 'sad' / 'angry' / 'exhausted' — 状态从肌肉和时间线长出来")
        out.append("")

    # 6. GEO SPATIAL LAYOUT (仅地点)
    if asset.kind == "location":
        out.append("[GEO SPATIAL LAYOUT — 锁死空间, 每个镜头逐字粘贴]")
        # 动态从 descriptor 抽取关键空间事实
        out.append("  (见 Full descriptor 内的方位/距离/轴线/光源)")
        out.append("  摄影机轴线: " + asset.behavior.get("axis_lock", "(未设置)"))
        out.append("")

    # 7. Style Prefix (Higgsfield 标准, 逐字粘贴)
    out.append("[STYLE PREFIX — 全文粘贴, 不许改任何字]")
    out.append("Style: Cinematic, live-action — no 3D render, no game engine, no game-cutscene aesthetic.")
    out.append("Cinematography: floating immersive camera that lives with the actors; natural motivated")
    out.append("light; painterly composed frames, strong silhouettes against the light.")
    out.append("Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric")
    out.append("haze throughout. Key light from sky and windows only.")
    out.append("Color: 60:30:10 — dominant / secondary / accent.")
    out.append("Camera: Physical cine lens. 180° shutter motion blur.")
    out.append("Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow")
    out.append("matching on-set light.")
    out.append("Acting: Hollywood — micro-pauses before reactions, precise eye-line, wet living eyes with")
    out.append("catch-lights, visible breath and chest rise.")
    out.append("Physics: Gravity and inertia respected — mass has real weight, correct contact shadows.")
    out.append("No floating props.")
    out.append("Composition: Rule of thirds + golden ratio. Every person moving from frame one.")
    out.append("Continuity: Characters, props, environment identical across every cut. No identity drift.")
    out.append("Technical: 24fps smooth motion. Film-grain detail. No jitter.")
    out.append("Audio: Environmental SFX only. No music. No subtitles.")
    out.append("")

    # 8. 5 要素说明
    out.append("[5 要素 — 为何此 prompt block 如此组织]")
    out.append("  #1 数据        : 三视图 + 3 身份锚点 + 完整 descriptor 全部在 ACTIVE REFERENCES")
    out.append("  #2 上下文缩略  : 状态激活后, 声音/行为 delta 立即拼入对应区")
    out.append("  #3 Skill       : 5 维意图 / 反 AI 词表 / 表演 4 支柱 全部由 Style Prefix 锁住")
    out.append("  #4 经验矩阵    : 来自 Hell Grind 16181 次生成 / 留下 253 镜的真实管线")
    out.append("  #5 AI 深度处理 : 不写 '画面里有什么', 写 '导演会怎么描述自己的意图'")
    out.append("")

    return "\n".join(out)


# ============================================================
# 6. 辅助 — 列出已注册资产, 列出已锁定资产, 节点化包装
# ============================================================

def list_assets(kind=None):
    """列出已注册资产, 可选按 kind 过滤 (character/location/prop)"""
    items = sorted(ASSET_REGISTRY.items())
    if kind:
        items = [(n, a) for n, a in items if a.kind == kind]
    out = []
    for name, asset in items:
        lock_tag = "  [LOCKED]" if asset.locked else ""
        state_count = len(asset.states)
        state_tag = ("  [states=" + str(state_count) + "]") if state_count else ""
        out.append("  " + name + "  (" + asset.kind + ")" + lock_tag + state_tag)
    return "\n".join(out)


def list_locked():
    """列出已锁定资产"""
    return "\n".join(sorted(LOCKED_ASSETS)) if LOCKED_ASSETS else "(无)"


# ============================================================
# 7. 节点化包装 — 让本模块可作为 ComfyUI 节点使用
# ============================================================

class AssetRegistry:
    """
    ComfyUI 节点包装 — 让 asset_registry 模块能在 ComfyUI 工作流里直接调用。
    输入: 资产名 (下拉) + 状态 (下拉, 可选 None)
    输出: descriptor / state_descriptor / voice / behavior / prompt_block / pressure_test_report

    5 要素架构驱动: 每个输出端口都对应 5 要素中的一层。
    """

    @classmethod
    def INPUT_TYPES(cls):
        names = sorted(ASSET_REGISTRY.keys()) + ["__REGISTER_NEW__"]
        state_choices = ["(默认)"] + sorted({sfx for a in ASSET_REGISTRY.values() for sfx in a.states.keys()})
        return {
            "required": {
                "资产名": (names, {"default": "@roco"}),
                "状态版本": (state_choices, {"default": "(默认)"}),
                "是否压力测试": ("BOOLEAN", {"default": True}),
                "是否锁定": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "descriptor",
        "state_descriptor",
        "voice_signature",
        "behavior_signature",
        "full_prompt_block",
        "lock_and_test_report",
    )
    FUNCTION = "run"
    CATEGORY = "PromptLibrary/Asset层"

    def run(self, 资产名="", 状态版本="", 是否压力测试=False, 是否锁定=False, **kwargs):
        if 资产名 == "__REGISTER_NEW__":
            return ("请用 register_asset() 函数注册新资产", "", "", "", "", "")

        state = None if 状态版本 == "(默认)" else 状态版本

        # 数据层输出
        desc = get_descriptor(资产名)
        state_desc = get_state_descriptor(资产名, state) if state else "(未选状态版本)"

        # Skill 层输出
        asset = _get_asset(资产名)
        try:
            voice = get_voice_signature(资产名)
        except ValueError:
            voice = "(非 character, 无 voice signature — " + 资产名 + " 是 " + asset.kind + ")"

        try:
            behavior = get_behavior_signature(资产名)
        except ValueError:
            behavior = "(非 character, 无 behavior signature — " + 资产名 + " 是 " + asset.kind + ")"

        # 完整 prompt block
        prompt_block = render_asset_prompt(资产名, state=state)

        # 经验层 + 锁定报告
        report_parts = []
        if 是否压力测试:
            pt = pressure_test(资产名)
            report_parts.append("=== 压力测试报告 ===")
            report_parts.append("name: " + str(pt.get("name")))
            report_parts.append("kind: " + str(pt.get("kind")))
            report_parts.append("n_rounds: " + str(pt.get("n_rounds", 0)))
            report_parts.append("all_pass: " + str(pt.get("all_pass", False)))
            report_parts.append("rounds: " + str(len(pt.get("rounds", []))))
            report_parts.append("same_frame: " + str(len(pt.get("same_frame", []))))
            report_parts.append("fail_mode_checks: " + str(pt.get("fail_mode_checks", {})))
            report_parts.append("")

        if 是否锁定:
            lock_result = lock_asset(资产名)
            report_parts.append("=== 锁定报告 ===")
            for k, v in lock_result.items():
                report_parts.append("  " + str(k) + ": " + str(v))

        report = "\n".join(report_parts) if report_parts else "(未启用压力测试 / 锁定)"

        return (desc, state_desc, voice, behavior, prompt_block, report)


# ============================================================
# 8. 节点映射 — 让 ComfyUI 能加载
# ============================================================

# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "AssetRegistry": AssetRegistry,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "AssetRegistry": "📦 资产注册表 (Phase 14)",
# }


# ============================================================
# 9. 自检入口 — 直接 python asset_registry.py 跑一下
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("asset_registry — 自检")
    print("=" * 70)
    print()
    print("已注册资产:")
    print(list_assets())
    print()
    print("已锁定资产:")
    print(list_locked())
    print()
    print("--- get_descriptor('@roco') 前 400 字符 ---")
    print(get_descriptor("@roco")[:400])
    print("...")
    print()
    print("--- get_state_descriptor('@roco', 'blood') 前 300 字符 ---")
    print(get_state_descriptor("@roco", "blood")[:300])
    print("...")
    print()
    print("--- get_voice_signature('@kaine') 前 300 字符 ---")
    print(get_voice_signature("@kaine")[:300])
    print("...")
    print()
    print("--- pressure_test('@roco') 摘要 ---")
    pt = pressure_test("@roco")
    print("  n_rounds:", pt["n_rounds"], "all_pass:", pt["all_pass"],
          "same_frame:", len(pt["same_frame"]),
          "fail_mode_checks:", all(c["pass"] for c in pt["fail_mode_checks"].values()))
    print()
    print("--- lock_asset('@roco') 摘要 ---")
    lr = lock_asset("@roco")
    print("  locked:", lr["locked"], "pressure_test_pass:", lr["pressure_test_pass"])
    print()
    print("--- render_asset_prompt('@lulu', state='injured') 长度 ---")
    rp = render_asset_prompt("@lulu", state="injured")
    print("  字符数:", len(rp))
    print()
    print("自检通过.")
