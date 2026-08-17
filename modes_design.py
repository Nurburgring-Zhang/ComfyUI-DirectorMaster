# ============================================================
# modes_design.py V1.0 — 专业设计模式8种深度prompt builder
# 修复 _HAS_DESIGN_MODE=False 缺口, 真实实现8个设计模式
# 每个builder返回专家级system prompt(构图/布光/角度/材质/色彩/验收)
# ============================================================

# 8种设计模式
DESIGN_MODES = [
    "电商套图", "海报设计", "品牌设计", "PPT设计",
    "逻辑关系图设计", "三视图设计", "爆炸拆解图设计", "流水线图设计",
]


def _common_design_header(mode, topic, style, color_tone):
    return (
        f"你是世界顶级的{mode}设计师兼商业视觉总监。\n"
        f"设计主题: {topic}\n整体风格: {style} | 色彩基调: {color_tone}\n"
        f"输出要求: 饱满专业, 每张3-6句, 禁止抽象词用可见细节, 不写参数数值(mm/K)。\n"
    )


# ============================================================
# 1. 电商套图
# ============================================================
def _build_ecommerce_prompt(topic, character_desc, env_desc, count, style, color_tone,
                             product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("电商套图", topic, style, color_tone)
        + "【电商套图设计原则】\n"
        + "1. 套图逻辑: 主图(吸引点击)→细节图(材质/功能)→场景图(使用情境)→对比图(差异化)→信任图(认证/口碑), 一套覆盖购买决策全链\n"
        + "2. 主图铁律: 主体占画面60%+, 白底或纯色, 标题文字大且醒目, 第一眼抓住卖点\n"
        + "3. 细节图: 微距特写材质纹理/工艺/功能部件, 展现品质可信\n"
        + "4. 场景图: 真实使用情境, 人物与产品互动, 生活方式代入\n"
        + f"3. 产品材质: {product_material or '待定'} | 产品颜色: {product_color or '待定'}\n"
        + f"4. 拍摄角度: {shoot_angle or '多角度组图(正面/45度俯视/侧面特写/微距)'}\n"
        + f"5. 布光方案: {lighting_scheme or '柔光箱主光+补光+轮廓光(电商标准)'} — 暗部须有细节, 高光不过曝\n"
        + f"6. 背景类型: {bg_type or '纯色背景(主图)+场景实景(场景图)'}\n"
        + "7. 验收: 主图点击率优先(主体大+卖点清晰), 细节图品质可信, 场景图代入感强\n"
        + f"8. 主体描述: {(character_desc or '产品待定').rstrip()}\n"
        + f"9. 场景设定: {env_desc or '场景待定'}\n"
        + "请输出电商套图设计, 每张明确标注图位(主图/细节/场景/对比/信任)与设计要点。\n"
    )


# ============================================================
# 2. 海报设计
# ============================================================
def _build_poster_prompt(topic, character_desc, env_desc, count, style, color_tone,
                          product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("海报设计", topic, style, color_tone)
        + "【海报设计原则】\n"
        + "1. 视觉层级: 主视觉(最大)→主标题(次大)→副标题→正文→logo/落款, 层级清晰一眼读懂\n"
        + "2. 构图: 三分法/居中/对角线, 留白呼吸, 视觉重心明确\n"
        + "3. 主视觉: 一图胜千言, 抓住情绪/卖点/奇观, 不堆砌\n"
        + "4. 标题: 大字体, 粗体, 高对比, 6-12字以内, 一句记住\n"
        + "5. 色彩: 主色1+辅助1+点缀1, 情绪与品牌一致, 远距离可读\n"
        + f"6. 背景: {bg_type or '渐变/纹理/场景, 烘托不抢主'}\n"
        + "7. 验收: 3秒读懂核心信息+记住情绪, 远距离(5米)主视觉+标题可辨\n"
        + f"8. 主体: {(character_desc or '主视觉待定').rstrip()}\n"
        + f"9. 场景: {env_desc or '场景待定'}\n"
        + "请输出海报设计, 明确主视觉/标题层级/色彩方案/构图。\n"
    )


# ============================================================
# 3. 品牌设计
# ============================================================
def _build_brand_prompt(topic, character_desc, env_desc, count, style, color_tone,
                        product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("品牌设计", topic, style, color_tone)
        + "【品牌设计原则】\n"
        + "1. 品牌系统: Logo+标准色+标准字+辅助图形+应用规范, 一套统一系统\n"
        + "2. 品牌内核: 价值观/个性/承诺, 视觉是内核外化, 不是装饰\n"
        + "3. 标志设计: 简洁(3秒记住)+独特(行业辨识)+适配(缩放/单色/反白可用)\n"
        + "4. 标准色: 主色1+辅助2, 品牌情绪色, 跨场景一致\n"
        + "5. 辅助图形: 可延展的视觉母题, 应用到全触点\n"
        + "6. 应用规范: 名片/信封/包装/导视/数字, 统一系统\n"
        + "7. 验收: 品牌系统统一+内核外化+跨场景一致+3秒辨识\n"
        + f"8. 品牌主体: {(character_desc or '品牌待定').rstrip()}\n"
        + f"9. 品牌场景: {env_desc or '行业待定'}\n"
        + "请输出品牌设计系统, 明确内核/标志/标准色/辅助图形/应用规范。\n"
    )


# ============================================================
# 4. PPT设计
# ============================================================
def _build_ppt_prompt(topic, character_desc, env_desc, count, style, color_tone,
                      product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("PPT设计", topic, style, color_tone)
        + "【PPT设计原则】\n"
        + "1. 一页一观点: 每页一个核心信息, 不堆砌, 信息层级清晰\n"
        + "2. 视觉>文字: 图表/图标/图片>大段文字, 演讲是讲不是念\n"
        + "3. 留白: 大量留白呼吸, 主体占画面40-60%, 不挤\n"
        + "4. 一致性: 字体/配色/版式/图标风格全篇统一\n"
        + "5. 标题: 每页大标题(结论先行)+小标题(论点)\n"
        + "6. 图表: 数据用图表(柱/饼/线), 不用表格堆数字\n"
        + "7. 验收: 一页一观点+视觉为主+留白呼吸+全篇一致\n"
        + f"8. 主题: {topic}\n"
        + f"9. 内容: {(character_desc or '内容待定').rstrip()}\n"
        + "请输出PPT设计, 每页标注页位/标题/核心观点/视觉元素。\n"
    )


# ============================================================
# 5. 逻辑关系图设计
# ============================================================
def _build_logic_diagram_prompt(topic, character_desc, env_desc, count, style, color_tone,
                                product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("逻辑关系图设计", topic, style, color_tone)
        + "【逻辑关系图设计原则】\n"
        + "1. 逻辑清晰: 节点(概念)+连线(关系), 关系类型明确(因果/包含/并列/递进/反馈)\n"
        + "2. 层级: 自上而下/自左而右, 主干+分支, 层级分明\n"
        + "3. 节点: 概念简短(2-6字), 形状统一(圆/方/菱形按类型), 颜色分组\n"
        + "4. 连线: 箭头方向=因果, 线型(实/虚)=关系强度, 不交叉\n"
        + "5. 留白: 节点间距均匀, 不挤, 视觉流向清晰\n"
        + "6. 验收: 逻辑关系一眼读出+层级分明+无交叉混乱\n"
        + f"7. 主题: {topic}\n"
        + f"8. 逻辑主体: {(character_desc or '逻辑待定').rstrip()}\n"
        + "请输出逻辑关系图设计, 明确节点/连线/关系类型/层级。\n"
    )


# ============================================================
# 6. 三视图设计
# ============================================================
def _build_three_view_prompt(topic, character_desc, env_desc, count, style, color_tone,
                              product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("三视图设计", topic, style, color_tone)
        + "【三视图设计原则】\n"
        + "1. 三视图: 正视图(前)/侧视图(左或右)/俯视图(上), 三视角一致比例\n"
        + "2. 比例统一: 三视图同比例尺, 主体对齐(基准线)\n"
        + "3. 线条: 工业制图风格, 粗轮廓+细结构线, 标注尺寸(可选)\n"
        + "4. 细节: 三视角细节对应(同一部件三视角一致)\n"
        + "5. 材质标注: 可附材质/工艺说明\n"
        + "6. 验收: 三视角比例一致+细节对应+制图规范\n"
        + f"7. 产品: {(character_desc or '产品待定').rstrip()}\n"
        + f"8. 材质: {product_material or '待定'} | 颜色: {product_color or '待定'}\n"
        + "请输出三视图设计, 明确正视/侧视/俯视及比例细节。\n"
    )


# ============================================================
# 7. 爆炸拆解图设计
# ============================================================
def _build_exploded_view_prompt(topic, character_desc, env_desc, count, style, color_tone,
                                product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("爆炸拆解图设计", topic, style, color_tone)
        + "【爆炸拆解图设计原则】\n"
        + "1. 拆解逻辑: 沿装配轴爆炸展开, 部件按装配顺序分层, 层间距均匀\n"
        + "2. 部件完整: 所有部件拆解, 无遗漏, 部件编号对应BOM\n"
        + "3. 装配线: 虚线/引导线连接部件与装配位, 方向=装配方向\n"
        + "4. 视角: 等轴测/45度俯视最佳, 展现立体装配关系\n"
        + "5. 材质标注: 各部件材质/工艺, 颜色区分\n"
        + "6. 验收: 部件完整+装配顺序清晰+引导线+等轴测立体\n"
        + f"7. 产品: {(character_desc or '产品待定').rstrip()}\n"
        + f"8. 材质: {product_material or '待定'}\n"
        + "请输出爆炸拆解图设计, 明确装配轴/部件分层/引导线/编号。\n"
    )


# ============================================================
# 8. 流水线图设计
# ============================================================
def _build_pipeline_diagram_prompt(topic, character_desc, env_desc, count, style, color_tone,
                                    product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    return (
        _common_design_header("流水线图设计", topic, style, color_tone)
        + "【流水线图设计原则】\n"
        + "1. 流程方向: 左→右(横向)或上→下(纵向), 单向流向, 无回路(除非循环)\n"
        + "2. 工序节点: 每工序方框+工序名+时长/资源, 节点间距均匀\n"
        + "3. 连线: 箭头=流向, 实线=主流程, 虚线=支线/反馈\n"
        + "4. 瓶颈标注: 瓶颈工序高亮(色/形), 关键路径标红\n"
        + "5. 资源标注: 人/机/料/时, 工序下方对齐\n"
        + "6. 验收: 流程单向+工序完整+瓶颈标注+资源对齐\n"
        + f"7. 流水线主题: {topic}\n"
        + f"8. 工序: {(character_desc or '工序待定').rstrip()}\n"
        + "请输出流水线图设计, 明确工序节点/流向/瓶颈/资源。\n"
    )


# ============================================================
# Generic dispatchers (满足__init__._process_design_mode的3个API)
# ============================================================
_BUILDER_MAP = {
    "电商套图": _build_ecommerce_prompt,
    "海报设计": _build_poster_prompt,
    "品牌设计": _build_brand_prompt,
    "PPT设计": _build_ppt_prompt,
    "逻辑关系图设计": _build_logic_diagram_prompt,
    "三视图设计": _build_three_view_prompt,
    "爆炸拆解图设计": _build_exploded_view_prompt,
    "流水线图设计": _build_pipeline_diagram_prompt,
}


def _build_design_system_prompt(mode, topic, character_desc, env_desc, count, style, color_tone,
                                 product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
    """通用分发: 按mode调用对应builder"""
    builder = _BUILDER_MAP.get(mode)
    if not builder:
        return f"你是专业设计师。请为「{mode}」设计。主题: {topic}。"
    return builder(topic, character_desc, env_desc, count, style, color_tone,
                    product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images)


def _build_design_user_prompt(mode, topic, character_desc, env_desc, count, style, color_tone,
                               product_material, product_color, shoot_angle, lighting_scheme, bg_type):
    return (
        f"设计主题: {topic}\n"
        f"{'主体: ' + character_desc + chr(10) if character_desc else ''}"
        f"{'场景: ' + env_desc + chr(10) if env_desc else ''}"
        f"数量: {count}张 | 风格: {style} | 色彩: {color_tone}\n"
        f"请输出{mode}设计内容。\n"
    )


def _build_design_global_context(design_type, mode, topic, character_desc, env_desc, style, color_tone):
    return (
        f"\n【{design_type}总纲】\n"
        f"设计模式: {mode} | 主题: {topic}\n"
        f"风格: {style} | 色彩基调: {color_tone}\n"
        f"主体: {(character_desc or '待定').rstrip()}\n"
        f"场景: {env_desc or '待定'}\n"
    )
