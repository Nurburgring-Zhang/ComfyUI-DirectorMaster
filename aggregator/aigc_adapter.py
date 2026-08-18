# -*- coding: utf-8 -*-
"""
V16.0 需求4: AIGC 视频生产适配引擎
====================================
自动判别 AIGC 视频生产模式, 并按模式适配分镜/提示词输出结构。

生产模式 (基于可用输入自动判别):
  文生视频 (T2V)      : 无任何参考 → 需完整场景描述
  首帧生视频 (I2V)     : 仅首帧 → 首帧锚定 + 运动描述
  首尾帧生视频 (FL2V)  : 首帧+尾帧 → 首尾帧锚定 + 中间运动
  多参考图生视频 (RefI2V): 角色/环境/道具参考图 → 参考锁定 + 运动
  参考视频生视频 (V2V) : 参考视频 → 运动迁移

判别优先级: 参考视频 > 首尾帧 > 多参考图 > 首帧 > 文生
"""

# 生产模式常量
MODE_T2V = "文生视频"
MODE_I2V = "首帧生视频"
MODE_FL2V = "首尾帧生视频"
MODE_REF_I2V = "多参考图生视频"
MODE_V2V = "参考视频生视频"

PRODUCTION_MODES = [MODE_T2V, MODE_I2V, MODE_FL2V, MODE_REF_I2V, MODE_V2V]


def detect_production_mode(has_first=False, has_last=False,
                           has_ref_images=False, has_ref_video=False,
                           ref_image_count=0):
    """自动判别 AIGC 视频生产模式.

    优先级: 参考视频 > 首尾帧 > 多参考图 > 首帧 > 文生
    返回: (mode_name, confidence_basis)
    """
    has_first = bool(has_first)
    has_last = bool(has_last)
    has_ref_video = bool(has_ref_video)
    try:
        ref_image_count = int(ref_image_count or 0)
    except Exception:
        ref_image_count = 0
    has_ref_images = bool(has_ref_images) or ref_image_count > 0

    if has_ref_video:
        return MODE_V2V, "有参考视频 → 运动迁移"
    if has_first and has_last:
        return MODE_FL2V, "有首帧+尾帧 → 首尾帧锚定"
    if has_ref_images and ref_image_count >= 1:
        if has_first:
            return MODE_REF_I2V, f"首帧+{ref_image_count}参考图 → 参考锁定+运动"
        return MODE_REF_I2V, f"{ref_image_count}参考图 → 参考锁定+运动"
    if has_first:
        return MODE_I2V, "仅首帧 → 首帧锚定+运动"
    return MODE_T2V, "无参考 → 完整场景描述"


# 每种生产模式的输出适配指引 (告诉下游模型/用户该模式需要什么)
MODE_GUIDANCE = {
    MODE_T2V: {
        "说明": "文生视频: 无参考素材, 提示词必须完整描述 场景/主体/动作/光影/风格/运镜, 信息密度最高",
        "提示词要求": "完整场景描述 + 主体外观 + 动作 + 光影 + 风格 + 运镜, 全部写入提示词",
        "分镜字段重点": ["画面焦点", "景别", "运镜", "光影", "色彩", "风格"],
        "无需": "首帧/尾帧/参考图",
    },
    MODE_I2V: {
        "说明": "首帧生视频: 首帧已给定, 提示词聚焦 首帧之后的运动/演变, 不重复描述首帧已有内容",
        "提示词要求": "首帧锚定 + 运动描述 + 演变方向; 避免与首帧冲突的描述",
        "分镜字段重点": ["运镜", "动作", "演变", "画面焦点"],
        "无需": "重复首帧已有的场景/主体静态描述",
    },
    MODE_FL2V: {
        "说明": "首尾帧生视频: 首帧+尾帧已给定, 提示词聚焦 首帧到尾帧之间的运动轨迹/过渡",
        "提示词要求": "首帧锚定 + 尾帧锚定 + 中间运动轨迹 + 过渡方式",
        "分镜字段重点": ["运镜", "动作", "过渡", "首尾帧一致性"],
        "无需": "首尾帧已有的静态描述",
    },
    MODE_REF_I2V: {
        "说明": "多参考图生视频: 角色/环境/道具参考图锁定外观, 提示词聚焦 动作/运镜/情节, 外观交给参考图",
        "提示词要求": "参考图锁定(角色/环境/道具) + 动作 + 运镜 + 情节; 外观由参考图保证一致",
        "分镜字段重点": ["参考图绑定", "动作", "运镜", "画面焦点"],
        "无需": "重复参考图已有的外观描述",
    },
    MODE_V2V: {
        "说明": "参考视频生视频: 参考视频提供运动/节奏, 提示词聚焦 风格迁移/内容替换, 保留原运动",
        "提示词要求": "参考视频运动迁移 + 风格/内容替换描述; 保留原视频运动节奏",
        "分镜字段重点": ["运动迁移", "风格替换", "节奏保留"],
        "无需": "重新设计运镜 (沿用参考视频)",
    },
}


def get_mode_guidance(mode):
    """返回生产模式的适配指引文本."""
    g = MODE_GUIDANCE.get(mode)
    if not g:
        return ""
    lines = [f"【AIGC 生产模式: {mode}】", f"  {g['说明']}", f"  提示词要求: {g['提示词要求']}"]
    if g.get("分镜字段重点"):
        lines.append(f"  分镜字段重点: {' / '.join(g['分镜字段重点'])}")
    if g.get("无需"):
        lines.append(f"  无需: {g['无需']}")
    return "\n".join(lines)


def adapt_shot_for_mode(shot, mode):
    """按生产模式适配单个镜头的描述, 返回适配后的 focus/提示词.

    shot: dict (含 focus/景别/运镜/光影 等字段)
    mode: 生产模式
    返回: 适配后的镜头提示词字符串
    """
    if not isinstance(shot, dict):
        return str(shot)
    focus = str(shot.get("focus") or shot.get("画面焦点") or "")
    size = str(shot.get("size") or shot.get("景别") or "")
    move = str(shot.get("move") or shot.get("运镜") or "")
    focal = str(shot.get("focal") or shot.get("焦段") or "")
    dur = str(shot.get("dur") or shot.get("时长") or "")

    if mode == MODE_T2V:
        # 文生: 完整描述
        return (f"{focus} | 景别:{size} 运镜:{move} 焦段:{focal} 时长:{dur} | "
                f"完整场景描述(无参考, 信息密度最高)")
    elif mode == MODE_I2V:
        return (f"[首帧锚定] 首帧之后的运动: {focus} | 运镜:{move} 时长:{dur} | "
                f"不重复首帧已有内容, 聚焦运动演变")
    elif mode == MODE_FL2V:
        return (f"[首尾帧锚定] 首帧→尾帧运动轨迹: {focus} | 运镜:{move} 时长:{dur} | "
                f"描述首尾帧之间的过渡, 保持首尾帧一致")
    elif mode == MODE_REF_I2V:
        return (f"[参考图锁定] 动作/运镜: {focus} | 运镜:{move} 时长:{dur} | "
                f"外观由参考图锁定, 聚焦动作与情节")
    elif mode == MODE_V2V:
        return (f"[参考视频迁移] 保留原运动, 风格/内容替换: {focus} | 时长:{dur} | "
                f"沿用参考视频运动节奏")
    return focus


def build_aigc_block(mode, shots, scene="", director=""):
    """构建 AIGC 生产适配块 (注入分镜输出), 含生产模式判别 + 每镜适配.

    返回: 文本块
    """
    lines = [
        "═" * 50,
        f"【AIGC 视频生产适配 · 生产模式: {mode}】",
        get_mode_guidance(mode),
        "",
    ]
    if shots:
        lines.append("每镜 AIGC 适配提示词:")
        for s in shots[:60]:  # 限制输出量
            n = s.get("n") or s.get("镜号") or ""
            adapted = adapt_shot_for_mode(s, mode)
            lines.append(f"  镜{n}: {adapted}")
    return "\n".join(lines)
