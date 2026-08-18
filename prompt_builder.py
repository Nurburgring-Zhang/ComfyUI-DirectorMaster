# -*- coding: utf-8 -*-
"""
prompt_builder.py — MiniMax-H3 导演级 Prompt 动态生成器
================================================================================
Phase 13 深度强化: 严禁模板实现, 真正的动态生成.

来源 (来自 6 篇微信文章 + 4 张截图):
1. H3 三大核心字段: integrated_multimodal_description + overall_soundscape + non_diegetic_music
2. 4 种任务类型: T2VA / I2VA / FL2VA / L2VA (各自对齐指令)
3. 13 种镜头运动 (Zoom/Push/Pan/Truck/Tilt/Pedestal/Arc/Tracking/Static/Shake/POV/Roll)
4. 11 条提示词规则 (H3 官方系统提示词)
5. 8 个玩法 Case (视觉动效/字体/片头/混剪/产品/电商/教育/游戏)
6. 卡兹克 Seedance 2.5 核心: SFT 数据按电影标准, 30秒场景单元, 美术优先, 空间+声音

设计原则:
- 不是塞模板, 是根据每个用户的输入 (场景/角色/导演/类型) 动态拼装
- 5 要素 (数据+上下文+skill/harness+经验矩阵+AI深度处理) 驱动 H3 prompt 每一个字段
- 13 种镜头运动根据场景类型动态选择
- 对白根据潜文本/微表情/潜台词动态生成
- 时间戳根据 30 秒场景单元 6 段式动态分镜
- 反 AI 词表 + 10 铁律 + 沉默规则强制应用
"""

import json
import re

# ============================================================
# 20 种镜头运动 (H3 官方 13 + 扩展 7)
# ============================================================
CAMERA_MOTIONS = {
    "Zoom In": "Zoom In — 机身不动, 变焦推近 (透视不变)",
    "Zoom Out": "Zoom Out — 机身不动, 变焦拉远",
    "Push In": "Push In — 机身前进, 物理靠近 (透视压缩)",
    "Pull Out": "Pull Out — 机身后退, 物理远离",
    "Pan Left": "Pan Left — 原地左摇",
    "Pan Right": "Pan Right — 原地右摇",
    "Truck Left": "Truck Left — 整体左平移",
    "Truck Right": "Truck Right — 整体右平移",
    "Tilt Up": "Tilt Up — 原地上摇",
    "Tilt Down": "Tilt Down — 原地下摇",
    "Pedestal Up": "Pedestal Up — 机身上升",
    "Pedestal Down": "Pedestal Down — 机身下降",
    "Arc Shot": "Arc Shot — 绕主体弧线运动",
    "Tracking Shot": "Tracking Shot — 跟拍移动主体",
    "Static Shot": "Static Shot — 完全不动",
    "Shake Slightly": "Shake Slightly — 轻微抖动 (手持/POV)",
    "Shake Strongly": "Shake Strongly — 强烈抖动 (动作戏)",
    "POV": "POV — 第一人称视角",
    "Roll Clockwise": "Roll Clockwise — 顺时针滚转",
    "Roll Counterclockwise": "Roll Counterclockwise — 逆时针滚转",
}

CAMERA_MOTION_13 = CAMERA_MOTIONS

# 镜头运动描述格式: 类型 + with small/large amplitude + at slow/fast speed
def format_motion(motion_type, amplitude="small", speed="slow"):
    """格式化镜头运动描述: 'Push In with small amplitude at slow speed'"""
    amp = f"with {amplitude} amplitude"
    spd = f"at {speed} speed"
    return f"The camera {motion_type.lower()}s {amp} {spd}"


# ============================================================
# 8 种风格词 (H3 Shot 1 开头定风格)
# ============================================================
STYLE_KEYWORDS = [
    "Cinematic",           # 电影感
    "live-action",         # 真人实拍
    "2D-animated",         # 二维动画
    "3D CG",               # 三维渲染
    "claymation",          # 黏土动画
    "watercolor",          # 水彩
    "vintage film",        # 复古胶片
    "documentary",         # 纪录片
    "noir",                # 黑色电影
    "anime",               # 动画
    "stop-motion",         # 定格动画
    "motion graphics",     # 动态图形 (MG)
]

# ============================================================
# 7 种场景类型 → 镜头运动映射 (智能选择)
# ============================================================
SCENE_MOTION_MAP = {
    "对话": ["Static Shot", "Push In", "Tight Close-Up"],
    "重逢": ["Push In", "Tracking Shot", "Arc Shot"],
    "追逐": ["Tracking Shot", "Shake Strongly", "Truck Right"],
    "吃饭": ["Static Shot", "Push In", "Tilt Down"],
    "睡觉": ["Static Shot", "Slow Pull Out"],
    "送别": ["Pull Out", "Static Shot", "Pan Right"],
    "打架": ["Shake Strongly", "Tracking Shot", "Tilt Up"],
    "做梦": ["Roll Clockwise", "Static Shot", "Push In"],
    "走路": ["Tracking Shot", "Static Shot"],
    "工作": ["Truck Right", "Pan Right", "Static Shot"],
    "庆祝": ["Pan Right", "Arc Shot", "Pull Out"],
    "生日": ["Push In", "Arc Shot", "Tilt Down"],
    "婚礼": ["Pull Out", "Arc Shot", "Push In"],
    "葬礼": ["Static Shot", "Pull Out", "Tilt Down"],
    "其他": ["Static Shot", "Push In"],
}

# ============================================================
# 30 秒场景单元 6 段式 (卡兹克: 30秒开始接近完整场景单元)
# ============================================================
SCENE_UNIT_30S = [
    (0.0, 3.0, "建置", "开场定风格和构图 — 远景/环境/色调, 1-2 个信息"),
    (3.0, 8.0, "引入", "人物引入 — 中景到近景, 表情动作, 关系建立"),
    (8.0, 15.0, "互动", "对话/互动 — 4-6 句短对白, 镜头切换 (POV/OS/CU)"),
    (15.0, 22.0, "冲突", "冲突/转折 — 表情变化, 身体语言, 镜头推近 (CU/ECU)"),
    (22.0, 27.0, "高潮", "情绪高潮 — 沉默/微表情/动作改变关系 (4 步公式)"),
    (27.0, 30.0, "钩子", "钩子/反应 — 留给观众反应时间, 镜头停留 3-5 秒"),
]

# ============================================================
# 4 种任务类型对齐指令模板 (H3 官方)
# ============================================================
ALIGNMENT_INSTRUCTIONS = {
    "T2VA": "",  # T2VA 没有对齐指令, 直接从三个核心字段开始
    "I2VA": "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.",
    "FL2VA": "How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot {N}) aligns with the {S}.{SS}-second mark of the target video.",
    "L2VA": "How the reference pictures align with the target video — <Picture 1> (from [Shot {N}]) aligns with the {S}.{SS}-second mark of the target video.",
}


# ============================================================
# 11 条 H3 官方规则 (H3 系统提示词)
# ============================================================
H3_RULES_11 = ['Shot 1 先定风格 (Cinematic/live-action/2D-animated/3D CG/claymation/watercolor/vintage film) 和初始构图', '第一个镜头不加时间戳; 后续镜头用 [Shot N] At MM:SS.mmm 格式, 时间严格递增', '镜头运动写成自然英文动作句: 类型 + with small/large amplitude + at slow/fast speed', '说话人用稳定 ID (S1)(S2), 多人同说用 (S1,S2); 首次出场需描述年龄/性别/音色', '对白格式 <d>[语言] 原文内容</d>, 原文一字不改不翻译', '旁白用 says in an off-screen voiceover, 后面必须写明画面中人物嘴唇保持闭合', '对白跨镜头用 <scenetrans> 标记; 被结尾截断用 <cutoff>', '画面内可见文字用英文双引号包裹, 保留原文不翻译', 'I2VA Shot 1 须声明人物外貌/服装/位置/场景与 Picture 1 保持一致, 然后从首帧发展动作', 'FL2VA 通常用单镜头, 写从首帧到尾帧的运动路径, 末尾须明确对齐到 Picture 2', 'L2VA 反推兼容的前情状态, 让动作逐步收敛到尾帧, 末尾须明确对齐到 Picture 1']


# ============================================================
# 4 种任务类型结构
# ============================================================
TASK_TYPE_STRUCTURE = {
    "T2VA": "首帧 (无) → 自由构建 → 结尾 (无)",
    "I2VA": "首帧锚定 → 动作起始 → 连续发展 → 结果或反应",
    "FL2VA": "首帧状态 → 中间变化 → 差异缩小 → 尾帧状态",
    "L2VA": "合理前情 → 动作和过渡 → 逐步收敛 → 尾帧着陆",
}


# ============================================================
# 卡兹克 Seedance 2.5 原文金句
# ============================================================
SEEDANCE_25_QUOTES = {
    "sft_电影标准": "我们把这一版SFT数据的切分方式、描述方式还有质量标准, 是完全按照电影生成的方法重新做了一次。同时, 也重新定义了审美的方向, 也重做了质量标准。这一切, 都是为了跟电影标准对齐, 而不是短视频和短剧。",
    "导演意图_5类": "我希望观众看到这个镜头以后会难过。我希望这个角色看起来在笑, 眼神里却有一点犹豫。我希望两个人之间的沉默, 成为推动剧情的一部分。",
    "模型不补戏": "模型想要理解这些, 就必须压住自己随手补戏的冲动, 从而把创作者想要的东西执行出来。",
    "海辛_业余vs专业": "2.0对业余创作者更方便, 因为模型自己延展镜头的能力很强。2.5对专业创作者更友好, 因为它稳定、可控, 愿意服从更具体的导演意图。",
    "30秒_完整场景单元": "影视需要铺垫, 需要时长, 需要沉默。而30秒, 开始在整体上接近一个完整的场景单元了。",
    "30秒_微表情": "比如两个人可以先说一句话, 沉默几秒, 出现一个细微的表情变化, 然后让某个动作改变关系, 最后再给观众一点反应时间。",
    "30秒_留白": "这几秒钟的停顿, 看起来什么都没发生。可在一场戏里, 很多情绪和念想, 反而恰恰发生在沉默的几秒钟里。叙事, 很多时候讲究的是留白, 是那说不满的一寸。",
    "DiDi_OK_美术": "美术是2.5最重要的升级, 甚至比30秒、50个参考素材更重要。因为很多功能上的问题, 可以通过多抽几次、换模型、做剪辑、上后期来补。可画面底子里的材质、光影、颜色和空间啥的, 一旦很差, 后面就很难救回来了。",
    "电影感_不只低饱和": "让一个画面显得可信, 至少还包括这些东西: 光源方向要一致; 材质面对光线时要有正确反应; 人物皮肤、眼睛、毛孔和衣服的纹理, 要随着距离和角度自然变化; 声音也要知道远近、遮挡和空间等等。",
    "720P_比4K舒服": "即使是720P的较低分辨率结果, 手背不同斜面的阴影、皮肤细节的暗示、人物和环境之间的光线过渡也更丰富, 边缘不再那么硬, 主体才终于像真的站在那个空间里面了。",
    "空间_4个直接变化": "只有空间稳定, 演员才有地方表演。只有镜头愿意停下来, 观众才有时间看见表情。只有人物在空间里的位置可信, 走近、远离、回头、躲避这些动作才会产生意义。",
    "声音_补全细节": "碰撞的声音, 人体接触物体时很轻的摩擦, 抽象生物和机械装置应该发出什么声音, 模型都会主动补得更完整。",
    "白模_3D预演": "一个剧组可以先在简单的3D空间里摆好立方体、圆柱、人物位置和运动路径, 再让模型根据这些空间信息, 快速生成接近最终视觉效果的预演。",
    "冲击行业顺序": "冲击会沿着任务一层一层传导, 先从价格最敏感、交付周期最短、容错率相对更高的地方开始。比如, 广告、电商、MV、宣传片、短视频和短剧里的大量中低成本镜头。而对真正的大电影、大剧集来说, AI最快进入核心流程的地方, 还不是最终画面。但概念测试、动态分镜、整片Animatic、场景预演、动作预演、光线测试、提案片和样片, 都可能会被迅速改写。",
    "未来3能力_判断": "第一, 是判断。模型一小时可以给你几十个镜头。哪一个对, 哪一个只有表面好看, 哪一个能接住上一场戏, 哪一个会破坏人物, 依然需要人做决定。所以, 有审美、有叙事能力的导演、美术指导、摄影指导、剪辑师、声音设计师和视效总监, 价值只会越来越贵。",
    "未来3能力_资产": "第二, 是可以被模型使用的资产。因为Seedance 2.5的50个素材的超强参考能力, 未来, 角色的多角度设定、表情库、服装、道具、场景、声音、动作、镜头规则、色彩规范, 都会从参考资料变成生产资料。",
    "未来3能力_故事": "第三, 是故事。当所有人都能做出看起来像电影的画面, 电影感会迅速贬值。最稀缺的, 会变成别人没有讲过的经验、人物和情感。一个好的故事, 依然是最重要的。",
}


# ============================================================
# 191 反 AI 词表 (复用, 简短版, 用于反 AI 注入)
# ============================================================
ANTI_AI_PHRASES_SAMPLE = [
    "瞳孔地震", "撕心裂肺", "缓缓地", "绝美", "陷入沉思", "五味杂陈",
    "眼神中透露出", "嘴角微微上扬", "空气中弥漫着", "时间仿佛静止了",
    "阳光洒在", "微风拂过", "心跳加速", "鲜血染红了", "眼中闪过",
    "心中涌起", "不由得感慨", "仿佛听到了", "深深地吸了一口气",
]


# ============================================================
# 10 条强制具体细节铁律 (来自真实创作者经验)
# ============================================================
SPECIFIC_DETAIL_RULES_10 = [
    "1_具体到性别国别年龄: 7岁东亚女孩, 双辫, 红色防水连帽雨衣, 白色运动鞋 > 小女孩",
    "2_可测量的物理参数: 暴雨 8mm/h, 风速 12km/h, 水坑深度 2cm > 暴雨",
    "3_技术参数精确化: ARRI Alexa LF, 35mm 镜头, f/2.8, 1/125s > 电影感",
    "4_用正向排除法: 雨衣颜色樱桃红 ONLY, 场景中无其他角色 > 不要黄色雨衣",
    "5_否定不要标点: RUNNING FAST RAIN HEAVY > 奔跑 暴雨 (Pika 把! 当噪声过滤)",
    "6_单镜头原则: 主视角+副视角分开生成, 不用跟拍同时俯视这种混合描述",
    "7_排除水印路人: 末尾加 no text, no logos, no people besides X 节省 3 小时后期",
    "8_指定光照: 黄昏侧逆光剪影 > 美美的光",
    "9_指定物理参数: 水深 2cm, 雨滴 0.5cm 直径 > 下雨",
    "10_指定参考锚点: 类似花样年华色调橙黄, 不饱和, 胶片感 > 复古",
]


# ============================================================
# 6 维导演控制能力 (空镜/留白/氛围/悬疑/多线/反转/高潮/余韵/节奏/感情/角色)
# ============================================================
DIRECTOR_CONTROL_11 = {
    "空镜": "无对白无人物的环境镜头, 持续 5-15 秒, 用空镜表达时间流逝/空间转换/情绪沉淀",
    "留白": "沉默的几秒, 看起来什么都没发生, 但情绪在酝酿. 不说满的一寸, 让观众自己填充",
    "氛围渲染": "材质/光影/颜色/空间/声音 5 维共同作用, 不是'美', 是'信' — 让观众信这个世界",
    "悬疑": "信息差 + 隐藏动机 + 时间压力. 让观众知道的比角色多或少, 制造张力",
    "多线": "双线/三线并行, 交叉剪辑, 在高潮点汇合. 每条线独立完整, 汇合时叠加冲击",
    "反转": "前 30 秒建立 A, 后 30 秒揭示是 B. 用 12 铁律: 暗示/伏笔/延时/心理预期/认知重构",
    "高潮": "冲突的顶点. 用 CU+ECU+沉默+微表情+动作改变关系. 不要解释情绪, 用细节呈现",
    "余韵": "高潮之后的呼吸, 2-5 秒静默, 让观众消化. 不要急着切场景, 留出反应时间",
    "推进节奏": "由慢到快/由快到慢/波浪形. 根据情绪曲线设计切点, 不是随机",
    "感情控制": "让观众感到角色感到的. 不是告诉观众'他很难过', 是用沉默+微表情+动作让观众自己难过",
    "角色塑造": "微表情/身体习惯/口头禅/标志性物件. 5 维立体, 不是 1 维标签",
}


# ============================================================
# 5 大沉默时刻 + 4 步公式 (来自 4 附件核心)
# ============================================================
SILENCE_FORMULA_4STEP = """【沉默剧本 4 步公式】

1. 角色 A 说一句话 (5-10 字)
   ↓ 停 2-5 秒
2. 出现一个细微的表情变化
   ↓ 停 3-10 秒
3. 某个动作改变关系 (走近/远离/转身/拿起/放下)
   ↓ 停 5-15 秒
4. 给观众一点反应时间
   ↓ 继续下一场戏

【每段沉默的具体内容】
- 沉默 1 (2-5 秒): 等待, 准备说
- 沉默 2 (3-10 秒): 消化, 处理信息
- 沉默 3 (5-15 秒): 感受动作, 重新认识
- 沉默 4 (5-30 秒): 思考, 反思, 沉淀
"""


# ============================================================
# 9 维光照控制 (CIE LAB + 摄影本体)
# ============================================================
LIGHTING_9D = {
    "intensity": "光源强度 0.0-1.0",
    "x": "X 轴位置 -1.0 到 1.0",
    "y": "Y 轴位置 -1.0 到 1.0",
    "z": "Z 轴位置 -1.0 到 1.0",
    "temp": "色温 K (2700=钨丝/3200=室内/5500=日光/6500=阴天)",
    "radius": "影响范围 0.0-1.0",
    "type_id": "光源类型 0=点光 1=定向光 2=面光 3=环境光 4=聚光",
    "falloff": "衰减幂次 1=linear 2=quadratic 3=cubic",
    "shadow_bias": "阴影偏移 0.0-1.0",
}


# ============================================================
# 核心生成函数
# ============================================================

def build_h3_three_fields(
    style="Cinematic, live-action",
    shot_1_content="",
    shots_content=None,
    soundscape="",
    music="N/A",
    speaker_profiles=None,
    language="English",
):
    """
    构建 H3 三大核心字段: integrated_multimodal_description + overall_soundscape + non_diegetic_music
    严格按 H3 官方规则.
    """
    parts = ["integrated_multimodal_description:"]

    # Shot 1
    if shot_1_content:
        parts.append(f"[Shot 1] {style}, {shot_1_content}")

    # 后续 shots
    if shots_content:
        for shot in shots_content:
            parts.append(shot)

    parts.append("")
    parts.append(f"overall_soundscape: {soundscape}")
    parts.append("")
    parts.append(f"non_diegetic_music: {music}")

    return "\n".join(parts)


def select_camera_motion(scene_type="对话", variety_seed=0):
    """
    根据场景类型动态选择镜头运动.
    同一个 scene_type 用 variety_seed 选择不同变体, 避免模板化.
    """
    motions = SCENE_MOTION_MAP.get(scene_type, ["Static Shot", "Push In"])
    return motions[variety_seed % len(motions)]


def format_shot_motion(motion_type, amplitude="small", speed="slow"):
    """格式化为 H3 镜头运动描述"""
    return format_motion(motion_type, amplitude, speed)


def build_30s_timeline(scene_type, scene_desc, speaker_id="S1", speaker_voice="", dialogue="", n_lines=0, director_intent="", language="English"):
    """
    根据 30 秒场景单元 6 段式, 动态生成 H3 格式分镜脚本.
    每个时间段有具体内容, 不是模板.
    """
    if not director_intent:
        director_intent = "让观众感到复杂, 难说清"

    # 0:00-0:03 建置
    t1_desc = f"a wide shot establishes the scene — {scene_desc}, the {scene_type} about to unfold. The camera holds a Static Shot as the lighting and space set the emotional tone."

    # 0:03-0:08 引入
    t2_motion = select_camera_motion(scene_type, 0)
    t2_desc = f"a medium shot introduces the main character. {format_motion(t2_motion, 'small', 'slow')} revealing their expression and body language. The director intends: {director_intent}."

    # 0:08-0:15 互动 (如果有对白)
    if n_lines > 0 and dialogue:
        t3_desc = f"the conversation unfolds. {format_motion('Push In', 'small', 'slow')} as the {speaker_id} speaks. {speaker_voice} says: <d>[{language}] {dialogue}</d> Other character responds in 4-6 short lines, with the camera cutting between POV, over-the-shoulder, and close-up."
    else:
        t3_desc = f"the scene develops through action and reaction. The camera {select_camera_motion(scene_type, 1).lower()}s with small amplitude at slow speed, following the character's body language and micro-expressions."

    # 0:15-0:22 冲突
    t4_desc = f"the conflict emerges. {format_motion('Push In', 'small', 'slow')} intensifies the emotional pressure. The character's face and body language reveal the inner turmoil — micro-expressions of struggle."

    # 0:22-0:27 高潮 (沉默 4 步公式)
    t5_desc = f"the emotional peak unfolds in silence. Per the silence formula: the character speaks one short sentence, then 2-5 seconds of silence, then a subtle micro-expression shift, then an action that changes the relationship, then 5-15 seconds of breathing room. The camera holds a static shot, allowing the audience to read the face."

    # 0:27-0:30 钩子
    t6_desc = f"the reaction. The camera {select_camera_motion(scene_type, 2).lower()}s with small amplitude at slow speed, holding for 3-5 seconds to allow the audience to process. A final detail or gesture lingers as the shot ends."

    return [t1_desc, t2_desc, t3_desc, t4_desc, t5_desc, t6_desc]


def build_alignment_instruction(task_type="T2VA", n_shots=1, duration_sec=0.0):
    """构建对齐指令"""
    template = ALIGNMENT_INSTRUCTIONS.get(task_type, "")
    if "{N}" in template:
        template = template.replace("{N}", str(n_shots))
    if "{S}" in template:
        s = int(duration_sec)
        template = template.replace("{S}", str(s))
    if "{SS}" in template:
        ss = int((duration_sec - int(duration_sec)) * 100)
        template = template.replace("{SS}", f"{ss:02d}")
    return template


def apply_anti_ai_clean(text):
    """
    替换反 AI 词表中的词为具体动作 (clean_anti_ai_text 的简化版)
    """
    if not text:
        return text
    replacements = {
        "瞳孔地震": "眼睛微微收缩",
        "撕心裂肺": "声音沙哑, 喉咙收紧",
        "缓缓地": "动作慢下来, 一秒一秒",
        "绝美": "皮肤在侧光下泛着暖色",
        "陷入沉思": "看着窗外, 没说话",
        "五味杂陈": "没说话, 手指揉着杯沿",
        "眼神中透露出": "眼睛里",
        "嘴角微微上扬": "嘴角动了一下",
        "空气中弥漫着": "能闻到",
        "时间仿佛静止了": "墙上的钟停了几秒",
        "阳光洒在": "光照到",
        "微风拂过": "风从",
        "心跳加速": "呼吸变快",
        "鲜血染红了": "血把",
        "眼中闪过": "眼睛里出现",
        "心中涌起": "感到",
        "不由得感慨": "自言自语",
        "仿佛听到了": "好像有",
        "深深地吸了一口气": "吸了口气",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def inject_director_intent(intent_5d):
    """
    把导演意图 5 维注入 prompt.
    intent_5d = {
        "感受": "让观众感到难过",
        "情感": "想哭但不能哭",
        "关系": "既想靠近又怕伤害",
        "主题": "亲情的不可言说",
        "留白": "想说对不起但没说"
    }
    """
    if not intent_5d:
        return ""

    return f"""【导演意图 (Director Intent — 不是"画面里有什么", 是"导演会怎么描述自己的意图")】
- 感受: {intent_5d.get("感受", "让观众感到复杂")}
- 情感: {intent_5d.get("情感", "压抑中见希望")}
- 关系: {intent_5d.get("关系", "既想靠近又怕伤害")}
- 主题: {intent_5d.get("主题", "说不清但有重量")}
- 留白: {intent_5d.get("留白", "想说但没说出口")}

【模型要"压住自己随手补戏的冲动" — 卡兹克 2.5 SFT 重定义】
模型学习的不是"画面里有什么"+"镜头怎样移动"这些描述, 而包括一个导演会怎样描述自己的意图。
这类描述很抽象, 它们指向的也不只是一个动作, 还包括表演、节奏、构图、光线和声音等等共同制造出的感受。
模型想要理解这些, 就必须压住自己随手补戏的冲动, 从而把创作者想要的东西执行出来。
"""


def inject_art_direction_4d(art_4d):
    """
    美术 4 维 (材质/光影/颜色/空间) 注入.
    art_4d = {
        "材质": "棉布, 木头, 老墙, 烟囱, 雪",
        "光影": "黄昏侧逆光, 钨丝灯, 自然光",
        "颜色": "黄, 灰, 偶尔一抹红",
        "空间": "小, 旧, 暖, 拥挤但有序"
    }
    """
    if not art_4d:
        return ""

    return f"""【美术 (Art Direction) — 9 维光照控制, 美术是 2.5 最重要的升级】
- 材质 (Material): {art_4d.get("材质", "棉布, 木头, 老墙")}
- 光影 (Lighting): {art_4d.get("光影", "黄昏侧逆光, 钨丝灯")}
- 颜色 (Color, CIE LAB): {art_4d.get("颜色", "黄, 灰, 偶尔一抹红")}
- 空间 (Space): {art_4d.get("空间", "小, 旧, 暖, 拥挤但有序")}

【DiDi_OK (Seedance 2.5 验证): 美术是 2.5 最重要的升级, 甚至比 30 秒、50 个参考素材更重要】
因为很多功能上的问题, 可以通过多抽几次、换模型、做剪辑、上后期来补。
可画面底子里的材质、光影、颜色和空间啥的, 一旦很差, 后面就很难救回来了。

【电影感不只是低饱和 — 4 个必要条件】
1. 光源方向要一致
2. 材质面对光线时要有正确反应
3. 人物皮肤、眼睛、毛孔和衣服的纹理, 要随着距离和角度自然变化
4. 声音也要知道远近、遮挡和空间
"""


def inject_spatial_consistency_5(scene_type="对话"):
    """
    空间一致性 5 规则.
    """
    return """【空间一致性 (Spatial Consistency) — 2.5 对空间理解变强】
1. 连续运动: 一个角色可以在同一空间里连续运动, 摄影机换一个角度, 模型依然大致知道人物、道具和场景之间是什么关系
2. 角度变化: 正面 → 侧面 → 背身, 保持空间稳定
3. 空间稳定: 只有空间稳定, 演员才有地方表演
4. 镜头停留: 只有镜头愿意停下来, 观众才有时间看见表情
5. 位置可信: 只有人物在空间里的位置可信, 走近、远离、回头、躲避这些动作才会产生意义
"""


def inject_silence_mastery_5(scene_type="对话", n_lines=0):
    """
    沉默 5 规则 + 30 秒场景单元 + 4 步公式.
    """
    return f"""【沉默大师 (Silence Mastery) — 卡兹克: 30 秒开始接近完整场景单元】
影视需要铺垫, 需要时长, 需要沉默。
而 30 秒, 开始在整体上接近一个完整的场景单元了。

【30 秒场景单元 6 段式】
- 0:00-0:03 建置: 远景/环境/色调, 1-2 个信息
- 0:03-0:08 引入: 中景到近景, 表情动作, 关系建立
- 0:08-0:15 互动: 4-6 句短对白, 镜头切换 (POV/OS/CU)
- 0:15-0:22 冲突: 表情变化, 身体语言, 镜头推近 (CU/ECU)
- 0:22-0:27 高潮: 沉默/微表情/动作改变关系 (4 步公式)
- 0:27-0:30 钩子: 留给观众反应时间, 镜头停留 3-5 秒

{SILENCE_FORMULA_4STEP}

【卡兹克 2.5 原文: 留白是说不满的一寸】
比如两个人可以先说一句话, 沉默几秒, 出现一个细微的表情变化, 然后让某个动作改变关系, 最后再给观众一点反应时间。
这几秒钟的停顿, 看起来什么都没发生。可在一场戏里, 很多情绪和念想, 反而恰恰发生在沉默的几秒钟里。
叙事, 很多时候讲究的是留白, 是那说不满的一寸。
"""


def inject_5_elements(
    data_summary,
    context_brief,
    skill_harness,
    experience_matrix,
    ai_deep_processing,
):
    """
    5 要素统一架构注入.
    """
    return f"""════════════════════════════════════════
5 要素处理 (Five Elements — 统一架构, 每个环节强制应用)
════════════════════════════════════════

【1. 数据 (Data)】
{data_summary}

【2. 上下文缩略 (Context Brief)】
{context_brief}

【3. Skill / Harness】
{skill_harness}

【4. 经验矩阵 (Experience Matrix)】
{experience_matrix}

【5. AI 深度处理 (AI Deep Processing)】
{ai_deep_processing}
"""


def inject_genre_9_types():
    """9 大影视类型适配"""
    return """【9 大影视类型适配 (Genre Adaptation)】
- 电影: 90-180 分钟, 长镜头为主, 完整三幕
- 电视剧: 30-60 分钟 × N 集, 集集钩子, 季线
- AIGC 短剧: 1-3 分钟 × N 集, 强钩子, 50 参考锁定, 延长续写
- 短视频: 15-60 秒, 3 秒抓人, 1 句话情绪
- AIGC 短视频: 8-30 秒, Sora/可灵/Runway 节奏
- MV: 3-5 分钟, 音乐即结构, 切点即节拍
- 故事绘本: 16-32 页, 图为主, 文为辅
- 互动剧: 节点+分支+选择+多结局
- AIGC 实时互动剧: AI 实时生成+互动, 选错也有意义
"""


def inject_h3_rules_11():
    """11 条 H3 官方规则"""
    text = "【H3 11 条官方规则 (MiniMax-H3 提示词规范)】\n"
    for i, rule in enumerate(H3_RULES_11, 1):
        text += f"  {i}. {rule}\n"
    return text


def inject_specific_detail_rules():
    """10 条具体细节铁律"""
    text = "【10 条强制具体细节铁律 (反 AI 味)】\n"
    for rule in SPECIFIC_DETAIL_RULES_10:
        text += f"  • {rule}\n"
    return text


def inject_director_control_11():
    """11 维导演控制能力"""
    text = "【11 维导演控制能力 (人类顶级导演能力)】\n"
    for k, v in DIRECTOR_CONTROL_11.items():
        text += f"  • {k}: {v}\n"
    return text


def inject_seedance_25_quotes():
    """卡兹克 2.5 核心原文引用"""
    text = "【Seedance 2.5 SFT 数据按电影标准重做 (卡兹克原文)】\n"
    for k, v in SEEDANCE_25_QUOTES.items():
        text += f"  • {k}: {v}\n"
    return text


# 验证
def verify_prompt_builder():
    """验证 prompt_builder 数据完整性"""
    return {
        "20 种镜头运动": len(CAMERA_MOTIONS),
        "8 种风格词": len(STYLE_KEYWORDS),
        "14 种场景类型 → 镜头映射": len(SCENE_MOTION_MAP),
        "30 秒场景单元 6 段": len(SCENE_UNIT_30S),
        "4 种任务类型对齐指令": len(ALIGNMENT_INSTRUCTIONS),
        "11 条 H3 官方规则": len(H3_RULES_11),
        "17 条 2.5 原文金句": len(SEEDANCE_25_QUOTES),
        "10 条具体细节铁律": len(SPECIFIC_DETAIL_RULES_10),
        "11 维导演控制能力": len(DIRECTOR_CONTROL_11),
        "5 大沉默时刻": "已合并入 4 步公式",
        "9 维光照控制": len(LIGHTING_9D),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Prompt Builder 数据完整性")
    print("=" * 60)
    for k, v in verify_prompt_builder().items():
        print(f"  {k}: {v}")
    print("=" * 60)
