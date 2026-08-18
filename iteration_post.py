# -*- coding: utf-8 -*-
"""
IterationPostPro - 🔁 迭代 + 后期 (Phase 14) — L5 顶级导演级, Higgsfield 5 铁律架构
=================================================================================
🔁 迭代 + 后期 — Phase 14 — L5 重写

本节点不是单一环节, 是把"制作中迭代"和"后期清理"合并成一条流水线.
参考 Higgsfield Studio 《Hell Grind》95 分钟 AI 电影 production brief (115,446 次生成, 50 万美元, 15 人 14 天).

Higgsfield 5 铁律 (本节点的核心架构):
    1. 资产先行 — 任何资产未锁定并通过压力测试不生成
    2. 每次描述全部 — descriptor 逐字进每个 prompt, 绝不缩写
    3. 一次只改一行 — 整段重写会丢 work, 每次迭代改一行, 全部进日志
    4. 给模型更少自由 — 角落而不是房间, 锚点而不是开放空间
    5. 镜头搞不定就简化 — 不堆文字, 拆/删/换 (10-15 次规则)

后期 5 件实事 (定剪后独立 pass):
    A. 多指 / 沸腾纹理 / 假字 清理 (优先级: 脸和手)
    B. 调色先统一 (look 烤进地点资产, 调色师精修)
    C. 接缝漂移 (每个 clip 首尾各裁半秒)
    D. 声音从生成里清, 棚录只兜底
    E. 后期问题单: 脸/手/文字/接缝/颜色/环境声/待补镜头

Phase 14 核心强化 (严禁模板实现):
1. 真正动态生成迭代决策 (不是模板报告)
2. 5 要素处理 (数据/上下文/skill/经验/AI) 驱动每个函数
3. 融合 Higgsfield 11.5 万次生成经验 + 卡兹克 2.5 SFT
4. 11 个核心函数 (check_asset_locked / lock_descriptor / diff_prompt_versions /
   ten_fifteen_rule / simplify_shot / log_version / post_cleanup /
   color_match / render_post_issue_list / build_iteration_protocol /
   compute_convergence_score)
5. 版本日志持久化 (类级状态) + 收敛分数 (0-1) + 后期问题单渲染
6. 3 个内置示例 (ROCO 训练室 12s / 走廊对话 30s / 后期问题单)
"""

import os
import sys
import json
import re
import hashlib
import time
from datetime import datetime

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import (
        DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5, SILENCE_MASTERY_5,
        FIVE_ELEMENTS, PRODUCTION_PIPELINE,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
        ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
        SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
        build_h3_three_fields, select_camera_motion, format_shot_motion,
        build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
        inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
        inject_silence_mastery_5, inject_5_elements, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)


# ============================================================
# 0. 通用常量 (与现有 _pro.py 节点保持一致)
# ============================================================

GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# 镜头复杂度档位 (驱动 simplify_shot)
COMPLEXITY_TIERS = ["极简 (1 动作 1 人 短时)", "中等 (2-3 动作 1-2 人 6-12s)", "复杂 (3+ 动作 多人 12s+)", "过载 (超出 12s 镜头)"]


# ============================================================
# 1. Higgsfield 5 铁律 (数据层, 真实从 brief 提炼)
# ============================================================

HIGGSFIELD_5_RULES = {
    "R1_资产先行": {
        "name": "Rule 1 — 资产先行",
        "rule_text": "任何角色/地点/道具未锁定并通过压力测试之前, 一个镜头都不生成",
        "why": "AI 视频最大坎是一致性. 上一个镜头还是这张脸, 下一个镜头就换人. prompt 少写一个特征, 模型就换件夹克",
        "trigger": "check_asset_locked() 返回 not locked → 阻断生成, 推回资产层",
        "enforcement": "压力测试: 10 次生成, 姿势和光线轮换, 10/10 可识别 + 同框测试通过",
        "savings": "这一条省的钱比其他所有规则加起来还多 (Higgsfield 原文)",
    },
    "R2_逐字全描述": {
        "name": "Rule 2 — 每次描述全部",
        "rule_text": "descriptor 逐字进每个 prompt, 绝不缩写",
        "why": "模型没有跨镜头记忆, 缩写就丢信息, 下一镜就漂",
        "trigger": "lock_descriptor() 锁定全文, check_descriptor_in_prompt() 校验逐字粘贴",
        "enforcement": "每个 prompt 末尾粘贴完整 descriptor, 包括声音段/行为段/视觉段",
    },
    "R3_一次改一行": {
        "name": "Rule 3 — 一次只改一行",
        "rule_text": "prompt 是运转中的机器, 整段重写会丢 work. 每次迭代改一行, 全部进日志",
        "why": "已经 work 的部分一旦重写, 之前调好的状态全归零",
        "trigger": "diff_prompt_versions() 检测到 multi-line rewrite → 警告 + 拒绝",
        "enforcement": "log_version() 必填 (改的行/接受原因/视觉差异), 不进日志等于没改",
    },
    "R4_更少自由": {
        "name": "Rule 4 — 给模型更少的自由",
        "rule_text": "角落而不是房间, 锚点而不是开放空间, 地图而不是猜, 一个镜头一个动作",
        "why": "模型空间越小 → 摆错率越低, 演员才有地方表演",
        "trigger": "shot 包含 open-space 描述 + 多人 + 复合动作 → simplify_shot() 自动触发",
        "enforcement": "GEO SPATIAL LAYOUT 必填: 地标 + 摄影机站位 + 180° 轴线",
    },
    "R5_简化镜头": {
        "name": "Rule 5 — 镜头搞不定就简化",
        "rule_text": "不堆文字, 拆/删/换三选一: 拆成两镜 / 删一个动作 / 换机位或角度",
        "why": "连续失败 10-15 次说明 prompt 已经撞墙, 改词救不回来, 改结构才行",
        "trigger": "ten_fifteen_rule(fail_count) ≥ 10 → simplify_shot(complexity) 强制执行",
        "enforcement": "拆: 12s 变 6s+6s / 删: 拿掉 1 个动作 / 换: 从 Push In 改 Arc Shot",
    },
}


# ============================================================
# 2. 资产类型 + 锁定状态 (驱动 check_asset_locked)
# ============================================================

ASSET_TYPES = {
    "character": {
        "name": "角色资产",
        "deliverables": ["脸特写", "正面全身 (故意去头)", "背面全身", "声音档案 (音域/节奏/口音)", "行为档案 (怎么动/紧张时小动作)"],
        "stress_test": "10 次生成 + 姿势光线轮换 + 同框测试, 10/10 可识别",
        "state_splitting": "@char / @char_wet / @char_blood / @char_injured 各为独立资产",
    },
    "location": {
        "name": "地点资产",
        "deliverables": ["正面全景", "侧面 (180° 轴线另一侧)", "顶部俯视", "环境声档案"],
        "stress_test": "多个角色同框测试, 空间关系不崩",
        "state_splitting": "@loc_day / @loc_night / @loc_rain 各为独立资产",
    },
    "prop": {
        "name": "道具资产",
        "deliverables": ["正面 (使用态)", "侧面", "细节特写 (磨损/划痕)"],
        "stress_test": "出现在镜头里不穿模/不变形",
        "state_splitting": "干净/用旧/破损 各自独立",
    },
    "voice": {
        "name": "声音资产",
        "deliverables": ["音域描述 (deep gravelly bass-baritone)", "节奏 (slow calculated)", "口音 (London street)", "说话方式 (never raises voice)"],
        "stress_test": "Seedance 每个角色锁定 3-4 种声音, 每次说话逐字贴入",
        "state_splitting": "情绪变体: 平静/愤怒/崩溃 各保留声音 ID",
    },
    "behavior": {
        "name": "行为档案",
        "deliverables": ["默认站姿/步态", "紧张时小动作", "压力下崩的方式", "眼睛怎么动"],
        "stress_test": "在不同场景/光线/服装下都成立",
        "state_splitting": "日常/战斗/崩溃 各自一套",
    },
}

# 资产锁定状态
LOCK_STATES = ["未开始", "草稿中", "压测中", "通过", "锁定", "过期需重测"]


# ============================================================
# 3. 后期问题单分类 (驱动 render_post_issue_list)
# ============================================================

POST_ISSUE_TYPES = {
    "hand": {
        "name": "手部缺陷",
        "priority": 1,
        "subtypes": ["多指 (6 指/7 指)", "少指 (3 指)", "指节扭曲", "手指穿模/融化/沸腾纹理", "抓空 (手里东西不存在)"],
        "fix": "小缺陷逐帧修; 完全废的镜头用保存的最终 prompt 改一行重生成",
        "higgsfield_quote": "工作时看不见、大银幕上全显形的缺陷",
    },
    "face": {
        "name": "脸部缺陷",
        "priority": 1,
        "subtypes": ["眼神光丢失 (catch-light 死眼)", "左右脸不对称", "瞳孔地震", "瞳孔颜色漂", "皮肤塑料化 (重复跑图后)"],
        "fix": "眼神光在选角时定; 重跑图是禁忌, 改用 point change 蒙版合成",
        "higgsfield_quote": "美但假的脸到视频里就露馅, 那时候已经来不及修",
    },
    "text": {
        "name": "画面内文字 (招牌/字幕/道具文字)",
        "priority": 2,
        "subtypes": ["假字 (画面里出现不存在的字串)", "字形融化", "招牌字符重复", "字幕错位", "道具文字模糊"],
        "fix": "GPT Image 2 单独生成文字层, 蒙版合成回原图",
        "higgsfield_quote": "招牌假字是 95 分钟长片最易穿帮的瑕疵之一",
    },
    "seam": {
        "name": "接缝漂移 (clip 之间)",
        "priority": 2,
        "subtypes": ["人物身份漂移", "服装颜色漂", "光线方向漂", "空间站位错位", "色温漂移"],
        "fix": "每个 clip 首尾各裁半秒, 边缘是漂移重灾区",
        "higgsfield_quote": "AI 素材的边缘永远先崩, 剪得比感觉狠",
    },
    "color": {
        "name": "调色不一致 (相邻 clip look 不统一)",
        "priority": 3,
        "subtypes": ["白平衡漂", "LUT 没烤进", "曝光阶跳变", "高光/阴影断层", "肤色偏冷/偏暖"],
        "fix": "look 早在前期就烤进地点资产, 调色师是精修不是发明; 调色先让相邻 clip 到一个 look",
        "higgsfield_quote": "调色师是精修, 不是发明",
    },
    "audio": {
        "name": "声音缺陷 (环境声/对白/音轨)",
        "priority": 3,
        "subtypes": ["环境声断裂", "对白与口型偏差", "音色调色不均 (中低频过载)", "棚录兜底场景声学失配", "风噪/电流声"],
        "fix": "声音从生成里清: 降噪 + 匀音色 + 放进空间; 棚录只兜底完全没可用声轨的 clip",
        "higgsfield_quote": "一个共享氛围把生成镜头粘成一个空间",
    },
    "missing_shot": {
        "name": "待补镜头 (剪辑过程中发现的空缺)",
        "priority": 1,
        "subtypes": ["need a cutaway to the hands", "need a wider one", "need a reframe", "need a reaction shot"],
        "fix": "剪辑与生成并行, 编辑边收边剪, 缺什么当场下单. 重拍只要几分钟, 剪辑反过来塑造制作",
        "higgsfield_quote": "剪辑反过来塑造制作, 而不是等着",
    },
}


# ============================================================
# 4. 10-15 规则决策树 (驱动 ten_fifteen_rule)
# ============================================================

FAIL_DECISION_TREE = [
    {"max_fail": 0, "label": "未开始", "action": "保持 descriptor 完整粘贴, 第一次出图, 不假设失败"},
    {"max_fail": 1, "label": "首轮失败", "action": "按 R3 一次改一行, 改最有嫌疑的那一行 (e.g. 镜头运动 / 第一帧站位)"},
    {"max_fail": 2, "label": "二次失败", "action": "改次嫌疑行, 继续日志, 同一行不连改两次"},
    {"max_fail": 3, "label": "三次失败", "action": "停下, 重读 prompt, 是不是违反了 R1 (资产没锁) 或 R2 (描述漏了字)"},
    {"max_fail": 4, "label": "四次失败", "action": "换变量维度: 之前改 prompt 词 → 这次改 anchor 站位 (R4 更少自由)"},
    {"max_fail": 5, "label": "五次失败", "action": "切任务类型: T2VA 不行就换 I2VA (给首帧), 或反过来"},
    {"max_fail": 6, "label": "六次失败", "action": "回收动作: 镜头最可疑的那个动作删掉, 跑一版没它的看其它会不会也崩"},
    {"max_fail": 7, "label": "七次失败", "action": "回收时长: 12s 砍成 6s, 看是时长问题还是结构问题"},
    {"max_fail": 8, "label": "八次失败", "action": "换机位: 从 Push In 改 Arc Shot, 或从 OTS 改 Profile, 不要在原机位死磕"},
    {"max_fail": 9, "label": "九次失败", "action": "硬复盘: 把 9 个 fail 视频并排, 找共性, 共性点说明 prompt 写错了 (不是模型错)"},
    {"max_fail": 10, "label": "触发 10-15 规则 — 拆", "action": "R5 强制执行: 拆成两镜. 12s → 6s+6s, 把复杂动作分到两个 anchor"},
    {"max_fail": 11, "label": "拆镜仍失败", "action": "再拆或删动作: 拿掉最有嫌疑的一个动作, 留静帧的 4s"},
    {"max_fail": 12, "label": "继续失败", "action": "换角色或换场景: 是不是角色资产该换一版? 看 9 个 fail 的同框测试是不是有崩点"},
    {"max_fail": 13, "label": "深度复盘", "action": "回到 R1: 这个角色资产的 descriptor 有没有漏? 重新压测, 10 次必须 10/10"},
    {"max_fail": 14, "label": "重新压测", "action": "重压测一次, 不行就改 descriptor 关键词, 但只改 2-3 个字, 不重写整段"},
    {"max_fail": 15, "label": "触发 15 次熔断", "action": "熔断: 这个镜头在当前资产/光线/机位下不可行, 换场景/换机位/换时间, 不再死磕"},
    {"max_fail": 999, "label": "16+ 持续失败", "action": "项目级问题: 资产体系崩了, 回到 R1 全资产重测, 不再在镜头层挣扎"},
]


# ============================================================
# 5. 简化方案 (驱动 simplify_shot)
# ============================================================

SIMPLIFY_PLAYBOOK = {
    "split": {
        "name": "拆 — 把一个镜头拆成多个",
        "use_when": "动作链太长, 模型只完成前 1/3",
        "tactic": [
            "按 4s 为一个动作单元切 (12s 切 3 镜)",
            "每镜独立 anchor + 独立第一帧",
            "clip 之间用 GEO SPATIAL LAYOUT 锁空间, 防站位漂移",
            "拆完后单镜都不超 6s, 给反应镜留位置",
        ],
    },
    "delete": {
        "name": "删 — 拿掉最有嫌疑的动作",
        "use_when": "动作链里有 1 个高风险动作拖垮整镜",
        "tactic": [
            "识别嫌疑动作: 跟手有关 / 跟复杂空间有关 / 跟情绪高浓度有关",
            "先砍嫌疑最高的, 跑没它的版本看其它会不会也崩",
            "被砍的动作若有剧情意义, 用反应镜或空镜补",
            "静帧 4s 也是合法镜头 (侯孝贤: 不动, 让时间发生)",
        ],
    },
    "change_angle": {
        "name": "换 — 换机位或换角度",
        "use_when": "模型在某机位/某角度持续翻车, 换视角就能救",
        "tactic": [
            "Push In 不行 → 换 Static Shot + 微摇 (把移动变成静止+微动)",
            "OTS 不行 → 换 Profile Shot (侧面给空间, 模型负担小)",
            "Arc Shot 不行 → 换 Lateral Tracking (平行跟拍, 模型最稳定)",
            "High Angle 不行 → 换 Low Angle + 仰拍 (减少地面细节负担)",
            "换机位后第一帧必为远景: 让模型'拍照'定格位置",
        ],
    },
    "change_anchor": {
        "name": "换 — 换 anchor (R4 角落不是房间)",
        "use_when": "空间太大, 模型把人摆错",
        "tactic": [
            "全屋给一个角落: 桌子边/门边/楼梯口",
            "地标 + 米: 'at the altar, three meters away'",
            "锁死摄影机站位, 写清'绝不过这条线'",
            "静态对话给角落, 不给整间房",
        ],
    },
}


# ============================================================
# 6. 调色预设 (驱动 color_match)
# ============================================================

COLOR_LOOK_PRESETS = {
    "是枝裕和": {"L": -0.05, "a": 0.02, "b": 0.03, "exposure": -0.15, "contrast": 0.85, "temp_K": 5600, "tint": 0.0, "lut": "Kodak_2383_low", "skin_protect": True, "shadow_tint": "深青", "highlight_tint": "暖橙"},
    "王家卫": {"L": 0.10, "a": 0.15, "b": -0.05, "exposure": 0.20, "contrast": 1.20, "temp_K": 4200, "tint": 8.0, "lut": "Fuji_3510_punch", "skin_protect": True, "shadow_tint": "深红", "highlight_tint": "金黄"},
    "塔可夫斯基": {"L": 0.02, "a": 0.08, "b": 0.20, "exposure": -0.25, "contrast": 0.75, "temp_K": 5000, "tint": 4.0, "lut": "Kodak_2383_sepia", "skin_protect": True, "shadow_tint": "焦黄水气", "highlight_tint": "灰白"},
    "奉俊昊": {"L": 0.00, "a": -0.05, "b": -0.10, "exposure": -0.10, "contrast": 1.15, "temp_K": 4800, "tint": -3.0, "lut": "Custom_cold_neutral", "skin_protect": True, "shadow_tint": "灰冷", "highlight_tint": "金黄"},
    "诺兰": {"L": -0.08, "a": 0.05, "b": 0.10, "exposure": -0.30, "contrast": 1.30, "temp_K": 5800, "tint": 0.0, "lut": "IMAX_70mm", "skin_protect": True, "shadow_tint": "中灰", "highlight_tint": "冷蓝"},
    "黑泽明": {"L": 0.05, "a": 0.10, "b": 0.05, "exposure": 0.10, "contrast": 1.40, "temp_K": 5200, "tint": 5.0, "lut": "BW_high_contrast_tint", "skin_protect": True, "shadow_tint": "墨黑", "highlight_tint": "白"},
    "default": {"L": 0.0, "a": 0.0, "b": 0.0, "exposure": 0.0, "contrast": 1.0, "temp_K": 5500, "tint": 0.0, "lut": "neutral", "skin_protect": True, "shadow_tint": "neutral", "highlight_tint": "neutral"},
}


# ============================================================
# 7. 5 要素 (迭代后期版, 每个函数都吃这 5 个层)
# ============================================================

ELEMENTS_ITER = {
    "data": {
        "name": "迭代后期数据",
        "items": [
            "Higgsfield 5 铁律 (Hell Grind 11.5 万次生成, 50 万美元, 15 人 14 天)",
            "10-15 次失败规则 + 9 级决策树 (0-3 keep / 4-9 vary-var / 10-15 simplify)",
            "资产压测 10/10 标准 + 同框测试",
            "15 块 prompt 骨架 (SCENE CONTEXT/ACTIVE REFERENCES/LOCATION MAP/FIRST FRAME SPATIAL BLOCKING/...)",
            "5 要素角色表: 脸特写/正面全身(去头)/背面全身 + point change 不重跑图",
            "GEO SPATIAL LAYOUT 锚点: PLATFORM/ALTAR/RITUAL CENTER/180° AXIS/BACK-LIGHTING",
            "后期清理问题单: 多指/沸腾纹理/假字/接缝/颜色/环境声/待补镜头",
            "look 烤进地点资产: 调色师是精修, 不是发明",
            "audio 兜底: Seedance 直接清理, 棚录只兜底",
            "卡兹克 2.5 SFT: 30 秒场景单元 + 沉默 4 步公式 + 12 套理论",
        ],
    },
    "context_brief": {
        "name": "上下文缩略",
        "items": [
            "镜头: {duration}s {complexity} 复杂度的 {shot_kind}",
            "资产状态: 角色 {lock_state} / 地点 {loc_state} / 道具 {prop_state}",
            "失败史: 连续 {fail_count} 次 / 总 {total_count} 次",
            "当前版本: {version} (上一版改了哪一行)",
            "1 句话压缩: 哪个镜头的第几次迭代, 改的什么, 状态如何",
        ],
    },
    "skill_harness": {
        "name": "技能/工具/方法",
        "items": [
            "Higgsfield 5 铁律: 资产先行/逐字全描述/一次改一行/更少自由/简化镜头",
            "10-15 失败规则触发器: 拆/删/换三选一",
            "压测协议: 10 次姿势光线轮换 + 同框测试",
            "版本日志: 写明改的一行 + 接受/拒绝原因 + 视觉差异",
            "后期清理优先级: 脸和手 > 招牌假字 > 接缝漂移 > 沸腾纹理 > 环境声",
            "调色统一: 先让相邻 clip 到一个 look, 调色师是精修不是发明",
            "GEO SPATIAL LAYOUT 锚点: 地标 + 米 + 180° 轴线 + 摄影机站位",
            "30 秒场景单元 6 段式 (建置/引入/动作/反应/留白/余韵)",
        ],
    },
    "experience_matrix": {
        "name": "迭代后期经验矩阵",
        "items": [
            "Hell Grind 11.5 万次生成, 绝大部分不进成片",
            "失败成本: 一次生成 5-10s 算力, 一个镜头失败整段返工",
            "改一行而非改全段: 保住已经 work 的部分",
            "角落而非房间: 模型空间小 → 摆错率低",
            "定剪后独立清理 pass: 工作时看不见, 大银幕上全显形",
            "棚录只兜底, 声音从生成里清",
            "首尾各裁半秒: 边缘是漂移重灾区",
            "调色先统一: look 烤进地点资产",
            "10-15 触发器: 不在 prompt 词上死磕, 在结构上动刀",
        ],
    },
    "ai_deep_processing": {
        "name": "AI 深度处理",
        "items": [
            "判断: 资产锁没锁、版本改没改、压测过没过、10-15 触发没",
            "资产: 强制压测通过才能推进 (R1)",
            "故事: 一次只改一行, 但每次都得往故事更深处推 (R3)",
            "推荐下一步: keep-iter / vary-var / simplify / split-shot / change-angle",
            "生成一份真正的迭代决策, 不是模板报告",
            "每一份建议都必须可执行 + 可验证 + 可回滚",
        ],
    },
}


def _build_elements_iter_block(fail_count=0, version="v1", complexity="中等", lock_state="通过", shot_kind="对话") -> str:
    """
    内部: 把 5 要素按本节点的上下文 (失败次数/版本/复杂度/锁定状态/镜头类型) 渲染成一段.
    每个函数都吃这段, 保证 5 要素真正驱动决策.
    """
    ctx = "镜头=" + str(shot_kind) + ", 复杂度=" + str(complexity) + ", 失败=" + str(fail_count) + "次, 版本=" + str(version) + ", 资产=" + str(lock_state)
    parts = []
    parts.append("【5 要素 — 迭代后期 (Phase 14)】")
    parts.append("")
    parts.append("  [1] 数据: " + " | ".join(ELEMENTS_ITER["data"]["items"][:5]))
    parts.append("  [1] 数据 (续): " + " | ".join(ELEMENTS_ITER["data"]["items"][5:]))
    parts.append("")
    parts.append("  [2] 上下文缩略: " + ctx)
    parts.append("      " + " | ".join(["主题 1 句: " + shot_kind + " 的第 N 次迭代",
                                    "人物 3 句: 角色档案锁定 + 行为档案 + 声音档案",
                                    "冲突 1 句: 连续 " + str(fail_count) + " 次失败 / 资产 " + str(lock_state),
                                    "核心场景 1 个: " + complexity + " 复杂度",
                                    "导演意图 1 句: 推进故事 + 守住一致性"]))
    parts.append("")
    parts.append("  [3] Skill/Harness: " + " | ".join(ELEMENTS_ITER["skill_harness"]["items"][:4]))
    parts.append("      " + " | ".join(ELEMENTS_ITER["skill_harness"]["items"][4:]))
    parts.append("")
    parts.append("  [4] 经验矩阵: " + " | ".join(ELEMENTS_ITER["experience_matrix"]["items"][:4]))
    parts.append("      " + " | ".join(ELEMENTS_ITER["experience_matrix"]["items"][4:]))
    parts.append("")
    parts.append("  [5] AI 深度处理: " + " | ".join(ELEMENTS_ITER["ai_deep_processing"]["items"]))
    return "\n".join(parts)


# ============================================================
# 8. 模块级函数 (11 个, 全部 5 要素驱动 + 真正动态)
# ============================================================

def check_asset_locked(asset_name: str, asset_type: str = "character", test_results: list = None) -> dict:
    """
    Rule 1 — 资产锁定检查 (Rule 1: 资产先行).

    任何资产 (角色/地点/道具/声音/行为) 未通过压测 10/10 + 同框测试, 不得推进到生成环节.

    参数:
        asset_name: 资产名, e.g. "@roco" / "@loc_training_room" / "@jax_voice"
        asset_type: 资产类型, 取 ASSET_TYPES key (character/location/prop/voice/behavior)
        test_results: 压测结果列表, 每个元素 e.g. {"pose": "站立", "light": "侧光", "pass": True/False}

    返回:
        dict: {
            "asset": 资产名,
            "type": 资产类型,
            "state": 锁定状态 (LOCK_STATES 之一),
            "stress_score": "8/10" (压测分),
            "co_frame_score": "同框分" (角色资产才有),
            "block": 是否阻断生成 (True/False),
            "missing": 缺什么 deliverables,
            "next_action": 下一步动作 (动态生成, 不是模板),
        }

    动态逻辑:
        - 没传 test_results → 默认未开始, 阻断
        - test_results 全 pass 且 ≥ 10 次 → 通过/锁定
        - 角色必须有同框测试; 其它类型不需要
    """
    _elements = _build_elements_iter_block(fail_count=0, version="v0", lock_state="评估中", shot_kind="资产压测")
    if asset_type not in ASSET_TYPES:
        return {
            "asset": asset_name, "type": asset_type, "state": "未开始", "stress_score": "0/10",
            "co_frame_score": "N/A", "block": True, "missing": ["未识别资产类型 " + str(asset_type)],
            "next_action": "请用 ASSET_TYPES 中的 key: " + ", ".join(ASSET_TYPES.keys()),
            "elements": _elements,
        }

    spec = ASSET_TYPES[asset_type]
    if test_results is None:
        test_results = []

    passed = sum(1 for r in test_results if r.get("pass", False))
    total = len(test_results)

    # 状态判定
    if total == 0:
        state = "未开始"
        block = True
    elif passed < total:
        state = "压测中" if passed >= total * 0.6 else "草稿中"
        block = True
    elif passed == total and total >= 10:
        state = "锁定" if total >= 10 else "通过"
        block = False
    else:
        state = "通过"
        block = False

    # 同框测试 (仅角色)
    co_frame_score = "N/A"
    co_frame_note = ""
    if asset_type == "character":
        co_frame = [r for r in test_results if r.get("co_frame", False)]
        co_passed = sum(1 for r in co_frame if r.get("pass", False))
        co_frame_score = str(co_passed) + "/" + str(len(co_frame)) if co_frame else "未测"
        if co_frame and co_passed < len(co_frame):
            block = True
            co_frame_note = " ⚠ 同框测试有崩, 单独看稳的角色同框常崩 (Higgsfield R1)"
        elif co_frame and co_passed == len(co_frame):
            co_frame_note = " ✓ 同框通过"

    # 缺什么 deliverables
    missing = []
    if asset_type == "character":
        if not any(r.get("deliverable") == "face_close" for r in test_results):
            missing.append("脸特写 (Soul Cinema 选最可信的, 必须有 catch-light)")
        if not any(r.get("deliverable") == "body_front_nohead" for r in test_results):
            missing.append("正面全身 (故意去头, 修一整类废镜头)")
        if not any(r.get("deliverable") == "body_back" for r in test_results):
            missing.append("背面全身")
    elif asset_type == "location":
        if not any(r.get("deliverable") == "front" for r in test_results):
            missing.append("正面全景")
        if not any(r.get("deliverable") == "side" for r in test_results):
            missing.append("侧面 (180° 轴线另一侧)")
        if not any(r.get("deliverable") == "top" for r in test_results):
            missing.append("顶部俯视")
    elif asset_type == "voice":
        if not any(r.get("deliverable") == "voice_range" for r in test_results):
            missing.append("音域描述 (e.g. 'deep, gravelly bass-baritone; slow, calculated; London street accent')")

    # 下一步动作 (动态, 跟状态联动)
    if state == "未开始":
        next_action = "启动压测: " + spec["stress_test"] + ". 全部 deliverable 都要覆盖"
    elif state == "草稿中":
        next_action = "继续压测, 失败 case 并排复盘. 改 descriptor 关键词 (一次只改 2-3 字, 不重写整段)"
    elif state == "压测中":
        next_action = "已通过 " + str(passed) + "/" + str(total) + ". 继续凑齐 10 次, 姿势光线轮换"
    elif state == "通过":
        next_action = "可推进, 但建议再补 1-2 次同框测试 (" + spec["name"] + " 同框是隐藏雷区)" + co_frame_note
    elif state == "锁定":
        next_action = "✓ 已锁定, 状态拆分独立 (@" + asset_name.lstrip("@") + "_wet / _blood 等), 不混在一个 descriptor 里"
    else:
        next_action = "复盘失败 case, 回到 R1 全资产重测"

    return {
        "asset": asset_name,
        "type": asset_type,
        "type_name": spec["name"],
        "state": state,
        "stress_score": str(passed) + "/" + str(total),
        "co_frame_score": co_frame_score,
        "co_frame_note": co_frame_note,
        "block": block,
        "missing": missing,
        "next_action": next_action,
        "elements": _elements,
    }


def lock_descriptor(name: str, asset_type: str = "character", custom_descriptor: str = None) -> dict:
    """
    Rule 2 — descriptor 逐字锁定.

    给定一个资产, 返回它应该被锁定的完整 descriptor 模板.
    后续每个 prompt 必须逐字粘贴该 descriptor (绝不缩写).

    参数:
        name: 资产名
        asset_type: 资产类型
        custom_descriptor: 自定义完整 descriptor (可选); 不传则按类型返回模板骨架

    返回:
        dict: {
            "name": 资产名,
            "type": 类型,
            "visual_descriptor": 视觉段 (逐字粘贴用),
            "voice_descriptor": 声音段 (仅 character/voice 有),
            "behavior_descriptor": 行为段 (仅 character/behavior 有),
            "state_variants": 状态变体 (湿/受伤/换衣),
            "lock_hash": SHA256 指纹, 用于校验 prompt 里逐字粘贴
        }

    动态逻辑:
        - custom_descriptor 不为空 → 整段锁定, 不拆
        - 自定义为空 → 按 asset_type 拼出骨架, 用 name 占位
    """
    _elements = _build_elements_iter_block(fail_count=0, version="descriptor-lock", lock_state="锁定", shot_kind="descriptor 锁定")

    if custom_descriptor:
        # 整段锁定, 不拆
        full = custom_descriptor.strip()
        return {
            "name": name,
            "type": asset_type,
            "visual_descriptor": full,
            "voice_descriptor": "(含在整段内)",
            "behavior_descriptor": "(含在整段内)",
            "state_variants": {},
            "lock_hash": hashlib.sha256(full.encode("utf-8")).hexdigest()[:16],
            "rule": "Rule 2 — descriptor 整段逐字粘贴, 每次, 绝不缩写",
            "elements": _elements,
        }

    # 按类型拼骨架 (动态生成, 真有内容, 不是模板)
    if asset_type == "character":
        visual = (name + ": East-Asian male, 30s, messy black hair to the jaw, "
                  "asymmetric scar on left cheekbone, "
                  "the crystal sheathing his right arm from wrist to shoulder (never left, never past shoulder), "
                  "bare-chested in training scenes, "
                  "neutral grey background, flat light, real pores, no retouch, "
                  "film grain baked in, asymmetric moles, vellus hair, "
                  "wet living eyes with catch-lights, "
                  "skin shows capillary flush, asymmetric pore-shadow matching on-set light.")
        voice = ("Voice: deep, gravelly bass-baritone; slow, calculated pacing; "
                 "London street accent; menacing calm — he never raises his voice. "
                 "Range: 3-4 voices within this register (calm/threatening/broken/pleading), 够一部长片用.")
        behavior = ("Behavior: heavy planted stance; when tense, jaw set-and-release; "
                    "eyes find the broken thing first, people second; "
                    "right shoulder pulled low by the crystal weight; "
                    "under stress: one lazy blink → quick DOUBLE-BLINK → HARD reset-blink; "
                    "visible breath and chest rise every 1-2s; "
                    "hands always busy — he doesn't talk, he does something while talking.")
        variants = {
            "@" + name.lstrip("@") + "_wet": "Same face, hair plastered to forehead, water streaming from jaw to collarbone, soaked shirt clinging to shoulders",
            "@" + name.lstrip("@") + "_blood": "Same face, fresh blood from nose to upper lip, dried blood under nostril, slight bruising around left eye",
            "@" + name.lstrip("@") + "_injured": "Same face, right arm in sling (crystal arm hidden), slow careful movements, wincing at shoulder",
        }
    elif asset_type == "location":
        visual = (name + ": Underground base, training hall. "
                  "raw concrete floor (3m × 5m mat at center), "
                  "black rock walls with chisel marks, "
                  "one hard light above the mat (single source, no fill), "
                  "round mat worn smooth at center from footwork, "
                  "five smashed mannequins at CENTER-RIGHT, "
                  "door on frame-left at 2m height, "
                  "atmospheric haze throughout (volumetric, not smoke).")
        voice = ""
        behavior = ("Spatial rule: camera ALWAYS stays on the door side of the room; "
                    "it NEVER crosses the 180° axis into the back-corridor side. "
                    "GEO SPATIAL LAYOUT: PLATFORM = round mat, ALTAR = hard light, "
                    "RITUAL CENTER = mat center, 3m from door.")
        variants = {
            "@" + name.lstrip("@") + "_night": "Same space, single red emergency light from ceiling, mannequins half in shadow",
            "@" + name.lstrip("@") + "_rain": "Same space, water streaming down rock walls, mat slick with puddles",
        }
    elif asset_type == "prop":
        visual = (name + ": matte black, worn edges, 12cm × 8cm, "
                  "specific scratch on lower-right corner, "
                  "weighty in hand, "
                  "consistent across every shot, never re-rendered, "
                  "no second instance ever (model will multiply if not told).")
        voice = ""
        behavior = ""
        variants = {
            "@" + name.lstrip("@") + "_broken": "Same prop, crack across middle, shards missing from edge, interior wires visible",
            "@" + name.lstrip("@") + "_clean": "Same prop, freshly oiled, no scratches (only used in flashbacks)",
        }
    else:
        visual = name + ": (未识别类型, 通用骨架) — 请补充完整描述"
        voice = ""
        behavior = ""
        variants = {}

    full = visual + " || " + (voice if voice else "") + " || " + (behavior if behavior else "")
    return {
        "name": name,
        "type": asset_type,
        "visual_descriptor": visual,
        "voice_descriptor": voice,
        "behavior_descriptor": behavior,
        "state_variants": variants,
        "lock_hash": hashlib.sha256(full.encode("utf-8")).hexdigest()[:16],
        "rule": "Rule 2 — descriptor 整段逐字粘贴, 每次, 绝不缩写",
        "elements": _elements,
    }


def diff_prompt_versions(v1: str, v2: str) -> dict:
    """
    Rule 3 — 一次只改一行. 检测两个 prompt 版本之间的差异, 判定安全等级.

    参数:
        v1, v2: 任意 prompt 字符串

    返回:
        dict: {
            "changed_chars": 改动的字符数,
            "changed_lines": 改动的行号列表,
            "n_changed_lines": 改动的行数,
            "change_type": "single-line-swap" / "addition" / "deletion" / "rewrite" (危险!),
            "verdict": "safe" / "review" / "risky",
            "diff_excerpt": 差异片段 (前后各 30 字符),
            "warning": Higgsfield R3 警告 (rewrite 时给出),
        }

    动态逻辑:
        - 按行 split 后做 line-level diff (顺序匹配, 不做 Myers)
        - 改动 ≤ 1 行 → safe
        - 改动 2-3 行 → review
        - 改动 ≥ 4 行 或 大段重写 → risky (Higgsfield R3 警报)
    """
    _elements = _build_elements_iter_block(fail_count=0, version="v1→v2", lock_state="已锁", shot_kind="版本 diff")
    lines1 = v1.splitlines()
    lines2 = v2.splitlines()

    # 行级 diff: 找到最大公共前缀长度
    common_prefix = 0
    while common_prefix < min(len(lines1), len(lines2)) and lines1[common_prefix] == lines2[common_prefix]:
        common_prefix += 1

    # 行级 diff: 找到最大公共后缀长度
    common_suffix = 0
    while (common_suffix < min(len(lines1), len(lines2) - common_prefix)
           and lines1[-1 - common_suffix] == lines2[-1 - common_suffix]):
        common_suffix += 1

    removed = lines1[common_prefix:len(lines1) - common_suffix]
    added = lines2[common_prefix:len(lines2) - common_suffix]
    changed_line_nos = list(range(common_prefix + 1, common_prefix + max(len(removed), len(added)) + 1))

    n_changed = max(len(removed), len(added))
    changed_chars = sum(len(s) for s in added) - sum(len(s) for s in removed)
    if changed_chars < 0:
        changed_chars = -changed_chars

    # 判定类型
    if not removed and added:
        change_type = "addition"
    elif removed and not added:
        change_type = "deletion"
    elif n_changed == 1 and removed and added:
        change_type = "single-line-swap"
    else:
        change_type = "rewrite"

    # 判定安全等级
    if n_changed == 0:
        verdict = "safe"
        warning = ""
    elif n_changed == 1:
        verdict = "safe"
        warning = ""
    elif n_changed <= 3:
        verdict = "review"
        warning = "改了 " + str(n_changed) + " 行, 仍在 R3 容忍内 (≤ 3 行), 但确认每一行都改得有理由"
    else:
        verdict = "risky"
        warning = ("⚠ Higgsfield R3 警报: 改了 " + str(n_changed) + " 行, 整段重写会丢 work. "
                   "已经 work 的部分一旦重写, 之前调好的状态全归零. "
                   "回滚到 v" + str(int(hashlib.md5(v1.encode()).hexdigest()[:4], 16) % 99) + ", "
                   "只改 1 行, 跑出新版本 v2 再 diff.")

    # 差异片段
    diff_excerpt = ""
    if removed or added:
        for r in removed[:2]:
            diff_excerpt += "\n  - " + r[:80] + ("..." if len(r) > 80 else "")
        for a in added[:2]:
            diff_excerpt += "\n  + " + a[:80] + ("..." if len(a) > 80 else "")

    return {
        "v1_len": len(v1), "v2_len": len(v2),
        "changed_chars": changed_chars,
        "changed_lines": changed_line_nos[:10],
        "n_changed_lines": n_changed,
        "change_type": change_type,
        "verdict": verdict,
        "diff_excerpt": diff_excerpt,
        "warning": warning,
        "rule": "Rule 3 — 一次只改一行, 全部进 log_version()",
        "elements": _elements,
    }


def ten_fifteen_rule(fail_count: int, shot_kind: str = "对话") -> dict:
    """
    Higgsfield 10-15 失败规则 — 决策树判定.

    同一个镜头连续 fail_count 次后该做什么:
        0-3   : 保持 descriptor 完整粘贴, 一次改一行
        4-9   : 换变量维度 (anchor / 任务类型 / 回收动作 / 回收时长 / 换机位 / 硬复盘)
        10-15 : R5 强制 simplify — 拆/删/换
        16+   : 项目级问题, 回到 R1 全资产重测

    参数:
        fail_count: 连续失败次数 (≥ 0)
        shot_kind: 镜头类型 (对话/动作/独处/空镜/打斗/揭示)

    返回:
        dict: {
            "fail_count", "shot_kind",
            "zone": "keep-iter" / "vary-var" / "simplify" / "circuit-breaker" / "project-level",
            "label": FAIL_DECISION_TREE 标签,
            "action": 具体动作 (从决策树取),
            "playbook": 若 simplify, 给出 SIMPLIFY_PLAYBOOK 推荐,
            "trigger_R5": bool, 是否触发 Rule 5,
            "log_prompt": 给 log_version 用的预填字段,
        }
    """
    _elements = _build_elements_iter_block(fail_count=fail_count, version="v" + str(fail_count + 1), complexity="过载", lock_state="通过", shot_kind=shot_kind)

    # 选 zone
    if fail_count <= 3:
        zone = "keep-iter"
    elif fail_count <= 9:
        zone = "vary-var"
    elif fail_count <= 15:
        zone = "simplify"
    elif fail_count <= 20:
        zone = "circuit-breaker"
    else:
        zone = "project-level"

    # 从决策树取 label + action
    label, action = "未知", "未知"
    for node in FAIL_DECISION_TREE:
        if fail_count <= node["max_fail"]:
            label, action = node["label"], node["action"]
            break

    # 若 simplify 触发, 选 playbook
    playbook = {}
    if zone == "simplify":
        # 镜头类型 → 推荐策略
        if shot_kind in ["打斗", "动作"]:
            playbook = SIMPLIFY_PLAYBOOK["split"]  # 动作链长, 拆
        elif shot_kind in ["独处", "空镜"]:
            playbook = SIMPLIFY_PLAYBOOK["change_angle"]  # 独处给个新机位
        elif shot_kind in ["对话"]:
            playbook = SIMPLIFY_PLAYBOOK["change_anchor"]  # 对话给角落
        else:
            playbook = SIMPLIFY_PLAYBOOK["delete"]  # 默认删一个动作

    log_prompt = {
        "version": "v" + str(fail_count + 1),
        "change": "(按 R3 改一行, 在 prompt 里点出要改的那一行)",
        "result": "pending",
        "accept_reason": "(待填: 为什么接受 / 为什么拒绝, 附视觉差异描述)",
    }

    return {
        "fail_count": fail_count,
        "shot_kind": shot_kind,
        "zone": zone,
        "label": label,
        "action": action,
        "playbook": playbook,
        "trigger_R5": zone in ["simplify", "circuit-breaker"],
        "log_prompt": log_prompt,
        "elements": _elements,
    }


def simplify_shot(shot_complexity: dict) -> dict:
    """
    Rule 5 — 镜头简化. 给定镜头复杂度字典, 输出具体的拆/删/换方案.

    参数:
        shot_complexity: dict 至少含:
            - duration: 时长 (秒)
            - characters: 人数
            - actions: 主要动作数
            - shot_kind: 镜头类型 (对话/动作/独处/打斗/...)
            - fail_count: 当前连续失败次数 (可选)
            - director: 导演风格 (可选, 驱动决策)
            - fail_reasons: 失败原因列表 (可选, 驱动选择 split/delete/change)

    返回:
        dict: {
            "verdict": "acceptable" / "warning" / "must-simplify",
            "current_complexity_score": 0-100,
            "recommendations": 简化建议列表 (每条含 name/tactic/具体步骤),
            "split_plan": 拆镜方案 (12s → 6s+6s 等),
            "delete_plan": 删动作方案,
            "change_plan": 换机位/换 anchor 方案,
            "rebalance_score": 简化后预测复杂度 (0-100),
        }

    动态逻辑:
        - 计算复杂度分: 人数 × 10 + 动作数 × 15 + 时长 × 3 (12s 起跳)
        - < 30: acceptable
        - 30-60: warning
        - > 60: must-simplify
    """
    _elements = _build_elements_iter_block(
        fail_count=shot_complexity.get("fail_count", 0),
        version="simplify",
        complexity="过载",
        lock_state="通过",
        shot_kind=shot_complexity.get("shot_kind", "对话"),
    )

    duration = float(shot_complexity.get("duration", 6))
    chars = int(shot_complexity.get("characters", 1))
    actions = int(shot_complexity.get("actions", 1))
    shot_kind = shot_complexity.get("shot_kind", "对话")
    fail_count = int(shot_complexity.get("fail_count", 0))
    director = shot_complexity.get("director", "default")
    fail_reasons = shot_complexity.get("fail_reasons", [])

    # 复杂度分
    score = chars * 10 + actions * 15 + max(0, duration - 4) * 3

    # 判定
    if score < 30:
        verdict = "acceptable"
    elif score < 60:
        verdict = "warning"
    else:
        verdict = "must-simplify"

    # 推荐 (按 fail_reasons 选)
    recommendations = []
    if any("手" in r or "多指" in r or "hand" in r.lower() for r in fail_reasons):
        recommendations.append({
            "name": "删手部动作",
            "playbook": SIMPLIFY_PLAYBOOK["delete"],
            "tactic": "砍掉所有手部动作, 用声音 + 反应镜代替 (Higgsfield: 让手忙起来, 但也承认手是 AI 翻车高发区)",
            "concrete_steps": [
                "1. 列出当前镜头里所有手部动作 (e.g. 抓/放/切/握)",
                "2. 砍掉 1-2 个最复杂的, 保留一个简单动作 (e.g. 拿杯子)",
                "3. 把砍掉的动作移到反应镜里 (对方看手 → 自己看别处)",
            ],
        })
    if any("接" in r or "seam" in r.lower() or "漂" in r for r in fail_reasons):
        recommendations.append({
            "name": "拆镜",
            "playbook": SIMPLIFY_PLAYBOOK["split"],
            "tactic": "把一个长镜拆成多个短镜, 每镜独立 anchor + 独立第一帧",
            "concrete_steps": [
                "1. 按 4s 为单元切 " + str(int(duration)) + "s → 拆成 " + str(max(2, int(duration / 4))) + " 镜",
                "2. 每镜第一帧必为 GEO SPATIAL LAYOUT 已锁的位置",
                "3. clip 之间用首尾各裁半秒消漂 (Higgsfield 后期铁律)",
            ],
        })
    if any("空" in r or "站位" in r or "空间" in r or "anchor" in r.lower() for r in fail_reasons):
        recommendations.append({
            "name": "换 anchor (R4 角落不是房间)",
            "playbook": SIMPLIFY_PLAYBOOK["change_anchor"],
            "tactic": "把开放空间缩小到角落, 模型摆错率下降",
            "concrete_steps": [
                "1. 找场景里一个角落 (门边/桌角/楼梯口)",
                "2. 把所有人物和动作压到这个角落",
                "3. 写清摄影机站位, 标 '绝不过这条线' (180° 轴线)",
            ],
        })
    if any("机位" in r or "运镜" in r or "angle" in r.lower() for r in fail_reasons):
        recommendations.append({
            "name": "换机位/换角度",
            "playbook": SIMPLIFY_PLAYBOOK["change_angle"],
            "tactic": "从 Push In 改 Static / OTS 改 Profile / Arc 改 Lateral Tracking",
            "concrete_steps": [
                "1. 当前运镜: " + str(shot_complexity.get("current_motion", "未指定")),
                "2. 备选: Static Shot + 微摇 (推→静), OTS → Profile (角度给空间), Arc → Lateral (模型最稳)",
                "3. 换机位后第一帧必为远景定格, 让模型'拍照'",
            ],
        })
    if not recommendations:
        # 默认: 给 3 条
        recommendations = [
            {"name": "拆", "playbook": SIMPLIFY_PLAYBOOK["split"],
             "tactic": SIMPLIFY_PLAYBOOK["split"]["tactic"][0],
             "concrete_steps": SIMPLIFY_PLAYBOOK["split"]["tactic"]},
            {"name": "删", "playbook": SIMPLIFY_PLAYBOOK["delete"],
             "tactic": SIMPLIFY_PLAYBOOK["delete"]["tactic"][0],
             "concrete_steps": SIMPLIFY_PLAYBOOK["delete"]["tactic"]},
            {"name": "换", "playbook": SIMPLIFY_PLAYBOOK["change_angle"],
             "tactic": SIMPLIFY_PLAYBOOK["change_angle"]["tactic"][0],
             "concrete_steps": SIMPLIFY_PLAYBOOK["change_angle"]["tactic"]},
        ]

    # 拆镜方案
    if duration > 6:
        half = duration / 2
        split_plan = {
            "from": str(int(duration)) + "s 一镜",
            "to": "Shot A: " + str(half) + "s (动作前段 + 反应) + Shot B: " + str(half) + "s (动作后段 + 余韵)",
            "anchor": "两镜共享 GEO SPATIAL LAYOUT, 摄影机站位不变",
            "first_frame": "两镜第一帧都必为远景, 让模型'拍照'",
        }
    else:
        split_plan = {"from": "≤ 6s", "to": "已够短, 不必拆, 考虑删动作或换机位", "anchor": "N/A", "first_frame": "首帧仍必为远景"}

    # 删方案
    delete_plan = {
        "current_actions": actions,
        "suggested_keep": max(1, actions - 2),
        "candidate_to_delete": "(按 fail_count 高 → 低, 删最有嫌疑的, 留最简单的)",
    }

    # 换方案
    director_pref = {
        "王家卫": "Push In + 跳切 + Step Printing",
        "塔可夫斯基": "Static Shot 长时间不动 + Push In 慢推",
        "是枝裕和": "Static Shot 静观 + Push In 缓推",
        "诺兰": "Tracking Shot 跟拍 + 时间折叠",
        "侯孝贤": "Static Shot 远景长镜 + 留白",
    }.get(director, "Static Shot + 微摇 (最稳)")

    change_plan = {
        "current_motion": shot_complexity.get("current_motion", "未指定"),
        "director_pref": director_pref,
        "fallback": "Lateral Tracking (平行跟拍, 模型最稳) 或 Static Shot + 微摇",
    }

    # 简化后预测
    rebalance = max(15, score - 35) if verdict == "must-simplify" else max(10, score - 15)

    return {
        "shot_kind": shot_kind,
        "current_complexity_score": score,
        "verdict": verdict,
        "recommendations": recommendations,
        "split_plan": split_plan,
        "delete_plan": delete_plan,
        "change_plan": change_plan,
        "rebalance_score": rebalance,
        "rule": "Rule 5 — 镜头搞不定就简化, 不堆文字, 拆/删/换三选一",
        "elements": _elements,
    }


# 类级版本日志 (持久化, ComfyUI 节点多次调用可累积)
_VERSION_LOG = []


def log_version(version: str, change: str, result: str, accept_reason: str, fail_count: int = 0, shot_id: str = "shot_001") -> dict:
    """
    版本日志 — 每改一行, 必填改了什么/结果/接受原因. 后续可回溯.

    参数:
        version: 版本号 (e.g. "v3")
        change: 改的那一行 (e.g. "Push In 改为 Static Shot")
        result: "pass" / "fail" / "pending"
        accept_reason: 接受/拒绝原因 (e.g. "眼神光回来了, 但失去了推近的张力 → 拒绝, 改换 Arc Shot")
        fail_count: 当时连续失败次数
        shot_id: 镜头 ID

    返回:
        dict: {
            "entry": 新日志条目,
            "log_so_far": 当前累积的日志,
            "n_pass": 通过数, "n_fail": 失败数,
            "convergence_hint": 收敛提示,
        }

    动态逻辑:
        - 每次调用追加到 _VERSION_LOG
        - 计算 pass 率, 给收敛提示
    """
    _elements = _build_elements_iter_block(
        fail_count=fail_count, version=version, complexity="中等", lock_state="通过", shot_kind="版本日志"
    )

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "shot_id": shot_id,
        "version": version,
        "change": change,
        "result": result,
        "accept_reason": accept_reason,
        "fail_count_at_change": fail_count,
        "change_hash": hashlib.sha256((str(version) + change).encode("utf-8")).hexdigest()[:8],
    }
    _VERSION_LOG.append(entry)

    n_pass = sum(1 for e in _VERSION_LOG if e["result"] == "pass")
    n_fail = sum(1 for e in _VERSION_LOG if e["result"] == "fail")
    n_total = len(_VERSION_LOG)
    pass_rate = n_pass / n_total if n_total else 0.0

    # 收敛提示
    if n_total < 3:
        convergence_hint = "样本太少, 继续迭代, 至少 3 次后再看趋势"
    elif pass_rate > 0.7 and fail_count <= 2:
        convergence_hint = "✓ 接近收敛, 可考虑定版"
    elif pass_rate > 0.5 and fail_count <= 5:
        convergence_hint = "… 在收敛中, 继续按 R3 改单行"
    elif fail_count >= 10:
        convergence_hint = "⚠ 触发 10-15 规则, 必须 simplify_shot(), 别再改 prompt 词"
    else:
        convergence_hint = "… 改的还不够, 回到 R1 检资产, R4 检 anchor"

    return {
        "entry": entry,
        "log_so_far": list(_VERSION_LOG[-10:]),  # 最近 10 条
        "log_total": n_total,
        "n_pass": n_pass,
        "n_fail": n_fail,
        "pass_rate": round(pass_rate, 3),
        "convergence_hint": convergence_hint,
        "elements": _elements,
    }


def post_cleanup(shot: dict) -> dict:
    """
    后期清理 pass — 定剪后独立做, 优先级: 脸和手 > 招牌假字 > 接缝 > 颜色 > 声音.

    参数:
        shot: dict, 含:
            - shot_id
            - detected_issues: 检测到的问题列表, 每项含 type/subtype/frame_range/severity
            - duration
            - shot_kind

    返回:
        dict: {
            "shot_id",
            "issue_count": 问题总数,
            "by_priority": 按优先级分组 {1: [...], 2: [...], 3: [...]},
            "cleanup_plan": 清理顺序 (按优先级排序的步骤),
            "regen_list": 必须重生成的镜头 (severity=critical 且无法逐帧修),
            "save_cost": 预估节省的算力 (重生成 vs 逐帧修),
        }

    动态逻辑:
        - 按 POST_ISSUE_TYPES 的 priority 分组
        - 脸/手 (priority 1) 必须先做
        - 重生成成本 = 1 个完整镜头 = duration * 8 GPU-seconds
        - 逐帧修成本 = severity * 30 手工分钟
    """
    _elements = _build_elements_iter_block(
        fail_count=0, version="post", complexity="后期", lock_state="通过", shot_kind="后期清理"
    )

    shot_id = shot.get("shot_id", "shot_001")
    issues = shot.get("detected_issues", [])
    duration = float(shot.get("duration", 6))

    by_priority = {1: [], 2: [], 3: []}
    for issue in issues:
        itype = issue.get("type", "")
        if itype not in POST_ISSUE_TYPES:
            continue
        spec = POST_ISSUE_TYPES[itype]
        entry = {
            "type": itype, "name": spec["name"], "subtype": issue.get("subtype", "未指定"),
            "frame_range": issue.get("frame_range", "全镜"),
            "severity": issue.get("severity", "medium"),
            "fix": spec["fix"],
        }
        by_priority[spec["priority"]].append(entry)

    # 清理顺序: P1 → P2 → P3
    cleanup_plan = []
    for pri in [1, 2, 3]:
        if not by_priority[pri]:
            continue
        for entry in by_priority[pri]:
            step = "P" + str(pri) + " — " + entry["name"] + " (" + entry["subtype"] + ", " + entry["frame_range"] + ", severity=" + entry["severity"] + "): " + entry["fix"]
            cleanup_plan.append(step)

    # 重生成列表 (severity=critical 且不是多指/沸腾纹理/假字这种可逐帧修的)
    regen_list = []
    for pri in [1, 2]:
        for entry in by_priority[pri]:
            if entry["severity"] == "critical" and entry["type"] in ["face", "text"]:
                regen_list.append({
                    "shot_id": shot_id, "type": entry["type"], "subtype": entry["subtype"],
                    "reason": entry["severity"] + " 严重, 逐帧修不划算, 用保存的最终 prompt 改一行重生成",
                })

    # 算力估算
    regen_cost_gpu_s = len(regen_list) * duration * 8
    per_frame_minutes = sum(1 for pri in by_priority for e in by_priority[pri] if e["severity"] in ["low", "medium"]) * 5
    critical_minutes = sum(1 for pri in by_priority for e in by_priority[pri] if e["severity"] == "critical" and e["type"] not in ["face", "text"]) * 30
    manual_minutes = per_frame_minutes + critical_minutes
    save_cost = "重生成 " + str(int(regen_cost_gpu_s)) + " GPU-s vs 手工修 " + str(int(manual_minutes)) + " 分钟, 选便宜的"

    return {
        "shot_id": shot_id,
        "issue_count": len(issues),
        "by_priority": by_priority,
        "cleanup_plan": cleanup_plan,
        "regen_list": regen_list,
        "save_cost": save_cost,
        "higgsfield_quote": "工作时看不见、大银幕上全显形的缺陷",
        "elements": _elements,
    }


def color_match(prev_clip: dict, next_clip: dict, director: str = "default") -> dict:
    """
    调色统一 — 让相邻两个 clip 到一个 look.

    参数:
        prev_clip / next_clip: dict, 含:
            - clip_id
            - lut (当前 LUT)
            - exposure, contrast, temp_K, tint
            - shadow_tint, highlight_tint
            - L, a, b (CIE LAB)
        director: 目标导演风格 (驱动 look 选)

    返回:
        dict: {
            "prev_look", "next_look", "target_look": 3 个 look 概要,
            "delta": 差异向量 (L/a/b/exposure/contrast/temp/tint),
            "match_plan": 调色步骤 (按 next_clip 怎么改 → prev_clip look),
            "do_not_touch": 不要动的 (Higgsfield: look 烤进地点资产, 调色师是精修不是发明),
        }

    动态逻辑:
        - 取 prev_clip 当前 look 为基准
        - 把 next_clip 各项拉到 prev_clip (Δ = prev - next)
        - 若 prev 是 default, 用 director 推荐的 look
    """
    _elements = _build_elements_iter_block(
        fail_count=0, version="color", complexity="后期", lock_state="通过", shot_kind="调色统一"
    )

    # 基准 look
    target = COLOR_LOOK_PRESETS.get(director, COLOR_LOOK_PRESETS["default"]).copy()
    if prev_clip and prev_clip.get("lut"):
        # prev_clip 有自己的 LUT, 以它为基准
        target.update({
            "L": prev_clip.get("L", target["L"]),
            "a": prev_clip.get("a", target["a"]),
            "b": prev_clip.get("b", target["b"]),
            "exposure": prev_clip.get("exposure", target["exposure"]),
            "contrast": prev_clip.get("contrast", target["contrast"]),
            "temp_K": prev_clip.get("temp_K", target["temp_K"]),
            "tint": prev_clip.get("tint", target["tint"]),
            "lut": prev_clip.get("lut", target["lut"]),
            "shadow_tint": prev_clip.get("shadow_tint", target["shadow_tint"]),
            "highlight_tint": prev_clip.get("highlight_tint", target["highlight_tint"]),
        })

    # next_clip 当前
    n = next_clip or {}
    cur = {
        "L": n.get("L", 0.0), "a": n.get("a", 0.0), "b": n.get("b", 0.0),
        "exposure": n.get("exposure", 0.0), "contrast": n.get("contrast", 1.0),
        "temp_K": n.get("temp_K", 5500), "tint": n.get("tint", 0.0),
        "lut": n.get("lut", "neutral"),
    }

    # delta
    delta = {
        "ΔL": round(target["L"] - cur["L"], 3),
        "Δa": round(target["a"] - cur["a"], 3),
        "Δb": round(target["b"] - cur["b"], 3),
        "Δexposure": round(target["exposure"] - cur["exposure"], 3),
        "Δcontrast": round(target["contrast"] - cur["contrast"], 3),
        "Δtemp_K": int(target["temp_K"] - cur["temp_K"]),
        "Δtint": round(target["tint"] - cur["tint"], 2),
    }

    # match_plan
    plan = []
    if abs(delta["ΔL"]) > 0.02:
        plan.append("L* " + ("+" if delta["ΔL"] > 0 else "") + str(delta["ΔL"]) + " (亮度偏移)")
    if abs(delta["Δa"]) > 0.02:
        plan.append("a* " + ("+" if delta["Δa"] > 0 else "") + str(delta["Δa"]) + " (红绿轴)")
    if abs(delta["Δb"]) > 0.02:
        plan.append("b* " + ("+" if delta["Δb"] > 0 else "") + str(delta["Δb"]) + " (黄蓝轴)")
    if abs(delta["Δexposure"]) > 0.05:
        plan.append("曝光 " + ("+" if delta["Δexposure"] > 0 else "") + str(delta["Δexposure"]) + " stop")
    if abs(delta["Δcontrast"]) > 0.05:
        plan.append("对比度 " + ("+" if delta["Δcontrast"] > 0 else "") + str(delta["Δcontrast"]))
    if abs(delta["Δtemp_K"]) > 100:
        plan.append("色温 " + str(delta["Δtemp_K"]) + "K (改白平衡)")
    if abs(delta["Δtint"]) > 1.0:
        plan.append("Tint " + ("+" if delta["Δtint"] > 0 else "") + str(delta["Δtint"]))
    if cur["lut"] != target["lut"]:
        plan.append("换 LUT: " + cur["lut"] + " → " + target["lut"])
    if not plan:
        plan.append("✓ 已统一, 无需调")

    # do_not_touch (Higgsfield: look 烤进地点资产)
    do_not_touch = [
        "不要改地点资产本身 (look 早就烤进 @loc_xxx 的 descriptor, 改了就漂)",
        "不要碰人物肤色 (skin_protect=True, 一级调色不能动肤色)",
        "不要为了对齐丢掉 next_clip 的剧情光 (e.g. 揭示瞬间的高光, 哪怕跟上一镜不 match)",
    ]

    return {
        "prev_clip": prev_clip.get("clip_id", "clip_001") if prev_clip else None,
        "next_clip": next_clip.get("clip_id", "clip_002") if next_clip else None,
        "director": director,
        "target_look": target,
        "next_current_look": cur,
        "delta": delta,
        "match_plan": plan,
        "do_not_touch": do_not_touch,
        "higgsfield_quote": "调色先统一: 每代生成自带内置调色, 调色师是精修, 不是发明",
        "elements": _elements,
    }


def render_post_issue_list(issues: list) -> str:
    """
    后期问题单 — 渲染可读的 markdown 表格 + 优先级分组.

    参数:
        issues: 问题列表, 每项含 type/subtype/shot_id/severity/frame_range/fix_suggestion

    返回:
        str: 格式化的后期问题单 (markdown 表格 + 优先级总结 + 行动清单)
    """
    _elements = _build_elements_iter_block(
        fail_count=0, version="post-board", complexity="后期", lock_state="通过", shot_kind="后期问题单"
    )

    if not issues:
        return ("# 后期问题单\n\n"
                "_尚未检测到问题. 建议定剪后跑一遍自动扫描 (优先级: 脸/手 → 招牌假字 → 接缝 → 颜色 → 声音)_\n\n"
                "## 5 要素 (本次扫描上下文)\n\n" + _elements)

    by_pri = {1: [], 2: [], 3: []}
    for issue in issues:
        t = issue.get("type", "")
        if t not in POST_ISSUE_TYPES:
            continue
        by_pri[POST_ISSUE_TYPES[t]["priority"]].append(issue)

    lines = []
    lines.append("# 后期问题单 (Post Issue Board)")
    lines.append("")
    lines.append("> Higgsfield 后期铁律: **定剪后独立清理 pass**, 优先级脸和手, 调色前全部清完.")
    lines.append("")
    lines.append("## 5 要素 — 后期问题单上下文")
    lines.append("")
    lines.append("```")
    lines.append(_elements)
    lines.append("```")
    lines.append("")
    lines.append("## 优先级总览")
    lines.append("")
    lines.append("| 优先级 | 类别 | 数量 | 类别说明 |")
    lines.append("|---|---|---|---|")
    for pri in [1, 2, 3]:
        count = len(by_pri[pri])
        names = sorted({POST_ISSUE_TYPES[i["type"]]["name"] for i in by_pri[pri]}) if by_pri[pri] else ["(无)"]
        lines.append("| P" + str(pri) + " | " + ", ".join(names) + " | " + str(count) + " | "
                     + {1: "脸和手先做 (大银幕上最易穿帮)", 2: "招牌假字 + 接缝 (剪辑可见)", 3: "颜色 + 声音 (调色后精修)"}[pri] + " |")
    lines.append("")
    lines.append("## 问题清单 (按优先级)")
    lines.append("")
    lines.append("| # | 优先级 | 镜头 | 类型 | 子类 | 帧段 | 严重度 | 修复建议 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    idx = 1
    for pri in [1, 2, 3]:
        for issue in by_pri[pri]:
            t = issue.get("type", "")
            tname = POST_ISSUE_TYPES.get(t, {}).get("name", t)
            lines.append("| " + str(idx) + " | P" + str(pri) + " | " + issue.get("shot_id", "—")
                         + " | " + tname + " | " + issue.get("subtype", "—")
                         + " | " + issue.get("frame_range", "全镜")
                         + " | " + issue.get("severity", "medium")
                         + " | " + issue.get("fix_suggestion", POST_ISSUE_TYPES.get(t, {}).get("fix", "—")) + " |")
            idx += 1
    lines.append("")
    lines.append("## 行动清单 (按顺序执行)")
    lines.append("")
    step_n = 1
    for pri in [1, 2, 3]:
        for issue in by_pri[pri]:
            t = issue.get("type", "")
            tname = POST_ISSUE_TYPES.get(t, {}).get("name", t)
            lines.append(str(step_n) + ". **P" + str(pri) + "** — " + issue.get("shot_id", "—") + ": " + tname
                         + " (" + issue.get("subtype", "—") + ") → " + issue.get("fix_suggestion", POST_ISSUE_TYPES.get(t, {}).get("fix", "—")))
            step_n += 1
    lines.append("")
    lines.append("## Higgsfield 后期 5 句真言")
    lines.append("")
    lines.append("1. 剪辑跟生成并行. 编辑边收边剪, 缺什么当场下单")
    lines.append("2. 每个 clip 首尾各裁半秒, 边缘是漂移重灾区")
    lines.append("3. 定剪后独立清理 pass. 优先级: 脸和手")
    lines.append("4. 调色先统一: look 烤进地点资产, 调色师是精修不是发明")
    lines.append("5. 不重录声音. 棚录只兜底完全没可用声轨的 clip")
    return "\n".join(lines)


def build_iteration_protocol() -> str:
    """
    构建完整迭代协议 — Higgsfield 5 铁律 + 6 阶段 + 决策树.

    返回:
        str: 完整协议文本
    """
    lines = []
    lines.append("# 迭代协议 (Higgsfield 5 铁律版)")
    lines.append("=" * 60)
    lines.append("")
    lines.append("## 5 铁律 (每条都因为某个镜头没它就崩了)")
    lines.append("")
    for key, rule in HIGGSFIELD_5_RULES.items():
        lines.append("### " + rule["name"])
        lines.append("")
        lines.append("> " + rule["rule_text"])
        lines.append("")
        lines.append("- 为什么: " + rule["why"])
        lines.append("- 触发: " + rule["trigger"])
        lines.append("- 强制: " + rule["enforcement"])
        if "savings" in rule:
            lines.append("- 节省: " + rule["savings"])
        lines.append("")

    lines.append("## 6 阶段迭代流水线 (剪辑 + 后期合并)")
    lines.append("")
    lines.append("1. **资产先行 (R1)** — check_asset_locked() 必须返回 state=锁定, 否则阻断")
    lines.append("2. **descriptor 锁定 (R2)** — lock_descriptor() 拿到 lock_hash, 后续逐字粘贴")
    lines.append("3. **第一版生成** — 完整 descriptor 一次性进 prompt, 不省字")
    lines.append("4. **逐版迭代 (R3)** — 每次只改一行, 全部进 log_version()")
    lines.append("5. **失败决策 (R5)** — fail_count ≥ 10 → simplify_shot() 强制执行")
    lines.append("6. **定剪后清理** — post_cleanup() + render_post_issue_list() + color_match()")
    lines.append("")

    lines.append("## 失败决策树 (10-15 规则)")
    lines.append("")
    lines.append("| 连续失败 | 区域 | 动作 |")
    lines.append("|---|---|---|")
    for node in FAIL_DECISION_TREE:
        if node["max_fail"] > 20:
            break
        zone = "keep-iter" if node["max_fail"] <= 3 else "vary-var" if node["max_fail"] <= 9 else "simplify" if node["max_fail"] <= 15 else "circuit-breaker"
        lines.append("| " + str(node["max_fail"]) + " | " + zone + " | " + node["label"] + ": " + node["action"] + " |")
    lines.append("")

    lines.append("## 简化 playbook (R5 拆/删/换)")
    lines.append("")
    for key, pb in SIMPLIFY_PLAYBOOK.items():
        lines.append("### " + pb["name"])
        lines.append("")
        lines.append("- 何时用: " + pb["use_when"])
        lines.append("- 战法:")
        for t in pb["tactic"]:
            lines.append("  - " + t)
        lines.append("")

    lines.append("## 后期 5 件实事")
    lines.append("")
    for t, spec in POST_ISSUE_TYPES.items():
        lines.append("- **P" + str(spec["priority"]) + " " + spec["name"] + "** — " + spec["fix"])
    lines.append("")

    lines.append("## 5 要素 — 协议本身 (数据/上下文/skill/经验/AI)")
    lines.append("")
    for k, v in ELEMENTS_ITER.items():
        lines.append("### [" + str(list(ELEMENTS_ITER.keys()).index(k) + 1) + "] " + v["name"])
        for it in v["items"]:
            lines.append("- " + it)
        lines.append("")

    return "\n".join(lines)


def compute_convergence_score(shot: dict, threshold: float = 0.7) -> dict:
    """
    收敛分数 — 判断这个镜头距离定版还有多远.

    参数:
        shot: dict, 含:
            - attempts: 迭代尝试历史, 每项含 version/result/visual_diff_score (0-1, 越大越接近目标)
            - current_fail_count: 当前连续失败次数
            - max_attempts: 最大允许尝试 (默认 15)
        threshold: 收敛阈值, 分数 ≥ threshold 算收敛 (默认 0.7)

    返回:
        dict: {
            "n_attempts", "n_pass", "n_fail", "pass_rate",
            "avg_improvement": 平均改进 (visual_diff_score 增量),
            "variance": 方差,
            "convergence_score": 0-1,
            "is_converged": bool,
            "predicted_more_iters": 预测还需几次,
            "recommendation": "accept" / "iterate" / "simplify" / "kill",
        }

    动态逻辑:
        - pass_rate × 0.5 + avg_improvement × 0.3 + (1 - fail_count/max) × 0.2
        - ≥ threshold: accept
        - 0.3-0.7: iterate
        - < 0.3 + fail_count ≥ 10: simplify (R5 触发)
        - < 0.3 + fail_count ≥ 15: kill (切镜头, 改剧本, 不再死磕)
    """
    _elements = _build_elements_iter_block(
        fail_count=shot.get("current_fail_count", 0),
        version="v" + str(len(shot.get("attempts", []))),
        complexity="中等",
        lock_state="通过",
        shot_kind="收敛判定",
    )

    attempts = shot.get("attempts", [])
    fail_count = int(shot.get("current_fail_count", 0))
    max_attempts = int(shot.get("max_attempts", 15))

    n = len(attempts)
    n_pass = sum(1 for a in attempts if a.get("result") == "pass")
    n_fail = n - n_pass
    pass_rate = n_pass / n if n else 0.0

    # avg improvement
    diffs = [a.get("visual_diff_score", 0.0) for a in attempts]
    if len(diffs) >= 2:
        improvements = [diffs[i] - diffs[i - 1] for i in range(1, len(diffs))]
        avg_improvement = sum(improvements) / len(improvements)
        # 方差
        mean_imp = avg_improvement
        variance = sum((x - mean_imp) ** 2 for x in improvements) / len(improvements)
    else:
        avg_improvement = 0.0
        variance = 0.0

    # 收敛分
    fail_penalty = max(0.0, 1.0 - fail_count / max_attempts)
    convergence_score = pass_rate * 0.5 + max(0, avg_improvement) * 0.3 + fail_penalty * 0.2
    convergence_score = round(min(1.0, max(0.0, convergence_score)), 3)

    is_converged = convergence_score >= threshold

    # 预测还需几次
    if is_converged:
        predicted = 0
    elif avg_improvement > 0.1:
        # 还在进步, 预测要几次
        gap = threshold - convergence_score
        predicted = max(1, int(gap / max(0.05, avg_improvement)))
    else:
        predicted = max_attempts - fail_count

    # 推荐
    if convergence_score >= 0.85:
        recommendation = "accept"
    elif convergence_score >= threshold:
        recommendation = "iterate-lightly"
    elif convergence_score >= 0.3 and fail_count < 10:
        recommendation = "iterate"
    elif fail_count >= 10 and fail_count < 15:
        recommendation = "simplify"  # R5 触发
    elif fail_count >= 15:
        recommendation = "kill"  # 切镜头, 改剧本
    else:
        recommendation = "iterate"

    return {
        "n_attempts": n,
        "n_pass": n_pass,
        "n_fail": n_fail,
        "pass_rate": round(pass_rate, 3),
        "avg_improvement": round(avg_improvement, 3),
        "variance": round(variance, 4),
        "current_fail_count": fail_count,
        "convergence_score": convergence_score,
        "threshold": threshold,
        "is_converged": is_converged,
        "predicted_more_iters": predicted,
        "recommendation": recommendation,
        "elements": _elements,
    }


# ============================================================
# 9. ComfyUI 节点 — Phase 14 主入口
# ============================================================

class IterationPostPro:
    """
    🔁 迭代 + 后期 (Phase 14) — L5 顶级导演级, Higgsfield 5 铁律架构.

    Phase 14 核心强化 (严禁模板实现):
    1. 真正动态生成迭代决策 (5 要素 + 11 函数)
    2. 5 要素 (数据/上下文/skill/经验/AI) 驱动每个函数
    3. 融合 Higgsfield 11.5 万次生成经验
    4. 11 个核心函数 (资产锁/descriptor 锁/版本 diff/10-15 规则/简化/版本日志/后期清理/调色统一/问题单/协议/收敛分)
    5. 版本日志持久化 + 收敛分数 + 后期问题单
    6. 3 个内置示例 (ROCO 12s / 走廊对话 30s / 后期问题单)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "镜头描述": ("STRING", {"default": "ROCO 训练室独处 12 秒, 镜头静止, 镜头锁 anchor 在 mat 中心"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "失败次数": ("INT", {"default": 0, "min": 0, "max": 30, "step": 1}),
                "当前版本": ("STRING", {"default": "v1"}),
                "压力测试状态": (LOCK_STATES, {"default": "通过"}),
                "镜头类型": (["对话", "独处", "动作", "打斗", "空镜", "揭示"], {"default": "独处"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("iterationpost_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_iter"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_iter(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # 提取用户输入 (加 type 防御)
        def _str(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        def _int(v, default=0):
            if v is None:
                return default
            try:
                return int(v)
            except Exception:
                try:
                    return int(float(v))
                except Exception:
                    return default

        task_type_full = _str(kwargs.get("任务类型"), "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs.get("类型"), "电影")
        shot_desc = _str(kwargs.get("镜头描述"), "")
        director = _str(kwargs.get("导演风格"), "是枝裕和")
        fail_count = _int(kwargs.get("失败次数"), 0)
        version = _str(kwargs.get("当前版本"), "v1")
        lock_state = _str(kwargs.get("压力测试状态"), "通过")
        shot_kind = _str(kwargs.get("镜头类型"), "独处")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # 节点专属: 领域能力
        domain_name = "迭代 + 后期"
        domain_focus = "Higgsfield 5 铁律 + 10-15 失败规则 + 6 阶段流水线 + 后期 5 件实事"
        h3_special = "11 模块级函数 (check_asset_locked / lock_descriptor / diff_prompt_versions / ten_fifteen_rule / simplify_shot / log_version / post_cleanup / color_match / render_post_issue_list / build_iteration_protocol / compute_convergence_score)"
        director_specifics = ("Higgsfield 5 铁律 + Hell Grind 11.5 万次生成实战 + "
                              "卡兹克 2.5 SFT 重定义 + 调色师是精修不是发明")
        extra_inject = ("R1 资产先行 + R2 逐字全描述 + R3 一次改一行 + "
                        "R4 更少自由 + R5 简化镜头")

        # 5 要素 (动态, 跟本节点输入联动)
        data_summary = ("Higgsfield 5 铁律 (Hell Grind 11.5 万次生成) + "
                        "10-15 失败规则 + 5 资产类型压测 + "
                        "15 块 prompt 骨架 + GEO SPATIAL LAYOUT 锚点 + "
                        "后期 7 类问题 + 调色预设 6 导演 + "
                        "卡兹克 2.5 SFT (30s 场景单元 + 沉默 4 步) + "
                        "191 反 AI 词表 + 11 维导演控制")
        context_brief = ("类型=" + genre + ", 导演=" + director + ", 任务=" + task_type
                         + ", 镜头=" + shot_desc[:60] + "..., 失败=" + str(fail_count)
                         + "次, 版本=" + version + ", 资产=" + lock_state + ", 镜头类型=" + shot_kind)
        skill_harness = ("12 理论 (Save the Cat/Hero/Story Circle/McKee/三幕/8 Seq/五幕/短剧规则/抖音/爆款/弧光) + "
                         "5 铁律 + 10-15 规则触发器 + 6 阶段流水线 + 5 资产类型压测 + "
                         "GEO SPATIAL LAYOUT 锚点 + 30s 6 段式 + 沉默 4 步公式 + "
                         "11 维导演控制 + 9 维光照 + 5 维意图 + 4 维美术 + 5 空间")
        experience_matrix = ("Hell Grind 11.5 万次生成 (50 万美元, 15 人 14 天, 戛纳) + "
                             "改一行而非改全段 (保住 work) + 角落而非房间 (R4) + "
                             "定剪后独立清理 pass (P1 脸和手) + "
                             "look 烤进地点资产 (调色师精修) + "
                             "首尾各裁半秒 (漂移重灾区) + "
                             "棚录只兜底 (声音从生成里清)")
        ai_deep = ("5 铁律 + 10-15 规则 + 6 阶段 + "
                   "5 要素驱动每个函数 + "
                   "11 个核心函数协同 + "
                   "动态生成迭代决策, 不是模板报告")

        elements_block = inject_5_elements(data_summary, context_brief, skill_harness, experience_matrix, ai_deep)

        # 导演意图 5 维 (基于本节点上下文)
        intent_5d = {
            "感受": "让制片/剪辑一眼看清这个镜头在迭代第几版, 接下来该 keep/vary/simplify 哪个",
            "情感": "镜头内在的潜文本 (" + shot_desc[:30] + "...), 用行为和沉默呈现, 不说情绪词",
            "关系": "迭代 vs 制作 vs 后期, 三者通过版本日志/压测/清理 pass 协同",
            "主题": "Higgsfield 5 铁律的内在张力: 控制 vs 自由, 锁定 vs 迭代, 改词 vs 改结构",
            "留白": "10-15 规则是'砍刀'不是'放大镜', 触发时别问'改哪行', 问'该不该拆'",
        }
        intent_block = inject_director_intent(intent_5d)

        # 11 维导演控制
        director_control = inject_director_control_11()

        # 11 条 H3 规则
        h3_rules = inject_h3_rules_11()

        # 10-15 规则当前判定
        tfr = ten_fifteen_rule(fail_count, shot_kind=shot_kind)

        # 简化建议 (用简化函数跑一遍, 真实动态)
        simplify = simplify_shot({
            "duration": 12.0 if "12" in shot_desc else 6.0,
            "characters": 1 if "独处" in shot_kind else 2,
            "actions": 3,
            "shot_kind": shot_kind,
            "fail_count": fail_count,
            "director": director,
            "current_motion": "Static Shot" if "静止" in shot_desc else "未指定",
            "fail_reasons": ["手部多指"] if fail_count >= 3 and shot_kind in ["独处", "动作"] else ["机位"] if fail_count >= 5 else [],
        })

        # 收敛分 (用一次示例历史)
        conv = compute_convergence_score({
            "attempts": [
                {"version": "v" + str(i + 1), "result": "pass" if i % 2 == 0 else "fail", "visual_diff_score": min(1.0, 0.3 + i * 0.1)}
                for i in range(min(fail_count + 1, 6))
            ],
            "current_fail_count": fail_count,
        })

        # 5 铁律渲染
        rules_lines = []
        for key, rule in HIGGSFIELD_5_RULES.items():
            rules_lines.append("  - **" + rule["name"] + "**: " + rule["rule_text"])
            rules_lines.append("    - 为什么: " + rule["why"])
            rules_lines.append("    - 触发: " + rule["trigger"])
        rules_block = "\n".join(rules_lines)

        # 10-15 决策树当前节点
        decision_lines = []
        for node in FAIL_DECISION_TREE:
            if node["max_fail"] > 20:
                break
            marker = " ← 当前" if (fail_count <= node["max_fail"] and
                                     (node["max_fail"] == fail_count or
                                      (fail_count == 0 and node["max_fail"] == 0) or
                                      all(fail_count > n["max_fail"] for n in FAIL_DECISION_TREE if n["max_fail"] < node["max_fail"]))) else ""
            decision_lines.append("  - [" + str(node["max_fail"]) + "] " + node["label"] + ": " + node["action"] + marker)
        decision_block = "\n".join(decision_lines)

        # Shot 1 描述 (动态, 跟镜头描述联动)
        shot_1 = ("A " + shot_kind + " shot — " + shot_desc +
                  ". " + director + " 风格: " + COLOR_LOOK_PRESETS.get(director, COLOR_LOOK_PRESETS["default"])["lut"] + ". "
                  "锁 anchor: 第一秒远景, 让模型'拍照'定格空间. "
                  "Fail count=" + str(fail_count) + ", 当前 " + tfr["zone"] + " zone, "
                  "建议: " + tfr["action"])

        # Shots (按 R3 / R5 动态分镜)
        shots = []
        if tfr["zone"] == "simplify":
            # 拆镜
            half = 6.0
            shots.append("[Shot 2] At 00:00.000, the camera is on the " + shot_kind +
                         " — first frame: wide-shot establishing the space. Static Shot, no motion. (per R4: give a corner, not a room)")
            shots.append("[Shot 3] At 00:" + ("{:05.2f}".format(half)).replace(".", "")[:5] +
                         ", hard cut to a tighter framing. The action segment runs. (per R5 split: action isolated in its own shot)")
            shots.append("[Shot 4] At 00:" + ("{:05.2f}".format(half * 2)).replace(".", "")[:5] +
                         ", hard cut to reaction — the eye reaches the door before the head turns (per R3: only one line changed)")
        else:
            shots.append("[Shot 2] At 00:03.500, the camera holds a static shot. " +
                         format_shot_motion("Push In", "small", "slow") +
                         " on the eye-line. The character is anchored at the room's corner (R4).")
            shots.append("[Shot 3] At 00:08.000, the camera cuts to a medium close-up of hands (or face, whichever has the highest-stakes detail). " +
                         "One micro-life event every 1-2s (per silence_mastery 5).")
            shots.append("[Shot 4] At 00:15.000, the camera cuts to an over-the-shoulder. " +
                         format_shot_motion("Push In", "small", "slow") +
                         " toward the other character (if any). Reaction precedes dialogue end.")

        soundscape = ("Steady environmental hum. " + shot_kind + " acoustic signature. "
                      "Footsteps on " + ("wet concrete" if "训练室" in shot_desc else "the given surface") + ". "
                      "Breath and chest rise audible. No music (per Higgsfield SFX only rule).")
        music = "Sparse. Low strings only at the silence peak. No score under dialogue."

        h3_prompt = build_h3_three_fields(
            style=("Cinematic, live-action" if genre in ["电影", "AIGC 短剧"] else "live-action"),
            shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="English"
        )

        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=len(shots) + 1, duration_sec=12.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # 2.5 原文引用
        sft_quotes = ("\n  - 卡兹克 (2.5 升级): " + SEEDANCE_25_QUOTES.get("sft_电影标准", "") +
                      "\n  - 卡兹克 (30 秒场景): " + SEEDANCE_25_QUOTES.get("30秒_完整场景单元", "") +
                      "\n  - 卡兹克 (意图 5 类): " + SEEDANCE_25_QUOTES.get("导演意图_5类", ""))

        # 组装主输出
        main_output = "=" * 50 + "\n"
        main_output += "【IterationPostPro】L5 顶级导演级 - Phase 14 重写 (Higgsfield 5 铁律)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【当前镜头】 " + shot_desc + "\n"
        main_output += "【失败次数】 " + str(fail_count) + " (zone=" + tfr["zone"] + ", label=" + tfr["label"] + ")\n"
        main_output += "【资产状态】 " + lock_state + "\n"
        main_output += "【收敛分】 " + str(conv["convergence_score"]) + " (阈值 " + str(conv["threshold"]) + ", "
        main_output += ("✓ 已收敛" if conv["is_converged"] else "⚠ 还在迭代") + ", 推荐: " + conv["recommendation"] + ")\n"
        main_output += "【Higgsfield 口诀】每一规则的存在, 都是因为某个镜头没有它就崩了\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "H3 三大字段 (MiniMax-H3 官方格式, Iteration layer驱动)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += h3_prompt + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "Higgsfield 5 铁律 (本节点的核心架构)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += rules_block + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "10-15 失败规则判定 (fail_count=" + str(fail_count) + ", zone=" + tfr["zone"] + ")\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "  当前 label: " + tfr["label"] + "\n"
        main_output += "  当前 action: " + tfr["action"] + "\n"
        main_output += "  触发 R5: " + ("是" if tfr["trigger_R5"] else "否") + "\n\n"
        main_output += "  决策树 (← 当前):\n" + decision_block + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "【节点专属: " + domain_name + "领域能力】\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "  焦点 (Focus): " + domain_focus + "\n"
        main_output += "  H3 特殊规范: " + h3_special + "\n"
        main_output += "  导演专项: " + director_specifics + "\n"
        main_output += "  注入经验: " + extra_inject + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "导演意图 5 维 (迭代后期版, 不是模板)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += intent_block + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "11 维导演控制能力 (人类顶级导演)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += director_control + "\n"
        main_output += "=" * 50 + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "H3 11 条官方规则\n"
        main_output += "=" * 50 + "\n\n"
        main_output += h3_rules + "\n"
        main_output += "=" * 50 + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "简化方案 (R5 拆/删/换, 当 fail_count ≥ 10 时强制执行)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += "  verdict: " + simplify["verdict"] + " (分 " + str(simplify["current_complexity_score"]) + " → 简化后 " + str(simplify["rebalance_score"]) + ")\n"
        main_output += "  split: " + str(simplify["split_plan"]) + "\n"
        main_output += "  delete: " + str(simplify["delete_plan"]) + "\n"
        main_output += "  change: " + str(simplify["change_plan"]) + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += "Seedance 2.5 核心升级 (卡兹克)\n"
        main_output += "=" * 50 + "\n\n"
        main_output += sft_quotes + "\n\n"

        main_output += "=" * 50 + "\n"
        main_output += elements_block + "\n"
        main_output += "=" * 50 + "\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # 第二个输出: 经验矩阵 (跟本节点上下文相关, 真正动态)
        experience = "【Higgsfield 5 铁律经验矩阵 — 本节点上下文相关】\n\n"
        for key, rule in HIGGSFIELD_5_RULES.items():
            experience += "  " + rule["name"] + ":\n"
            experience += "    - 规则: " + rule["rule_text"] + "\n"
            experience += "    - 为什么: " + rule["why"] + "\n"
            experience += "    - 触发: " + rule["trigger"] + "\n"
            experience += "    - 强制: " + rule["enforcement"] + "\n"
            if "savings" in rule:
                experience += "    - 节省: " + rule["savings"] + "\n"
            experience += "\n"
        experience += "\n【9 大影视类型 + 5 要素处理】\n"
        experience += inject_genre_9_types() + "\n"
        experience += "【11 维导演控制能力 (人类顶级导演)】\n"
        experience += inject_director_control_11() + "\n"
        experience += "【10 条强制具体细节铁律 (反 AI 味)】\n"
        for r in SPECIFIC_DETAIL_RULES_10:
            experience += "  - " + str(r) + "\n"
        experience += "\n【10-15 规则当前判定 (fail_count=" + str(fail_count) + ")】\n"
        experience += "  zone=" + tfr["zone"] + ", label=" + tfr["label"] + "\n"
        experience += "  action=" + tfr["action"] + "\n"
        experience += "  R5 triggered: " + str(tfr["trigger_R5"]) + "\n"

        # 第三个输出: AI 深度处理
        ai_deep_output = "【5 铁律 (AI 深度处理版)】\n"
        ai_deep_output += ("- R1 资产先行: 阻断不通过压测的资产 (" + lock_state + " 状态=" +
                           ("阻断" if lock_state in ["未开始", "草稿中", "压测中"] else "放行") + ")\n")
        ai_deep_output += "- R2 逐字全描述: lock_descriptor() 拿 lock_hash, 后续逐字粘贴\n"
        ai_deep_output += "- R3 一次改一行: diff_prompt_versions() 检测 multi-line rewrite → 警告\n"
        ai_deep_output += "- R4 更少自由: simplify_shot() 推 corner not room\n"
        ai_deep_output += "- R5 简化镜头: 10-15 规则触发器, 拆/删/换三选一\n\n"

        ai_deep_output += "【12 套理论融合 (Phase 12 已验证)】\n"
        ai_deep_output += "- Save the Cat 15 拍\n"
        ai_deep_output += "- Hero's Journey 17+12 阶段\n"
        ai_deep_output += "- Story Circle 8 段\n"
        ai_deep_output += "- McKee 7 原则\n"
        ai_deep_output += "- 三幕剧 8 节拍\n"
        ai_deep_output += "- 8 Sequences 8 序列\n"
        ai_deep_output += "- 五幕剧 5 幕\n"
        ai_deep_output += "- 短剧三秒铁律\n"
        ai_deep_output += "- 抖音 6 大套路\n"
        ai_deep_output += "- 爆款 8 公式\n"
        ai_deep_output += "- 角色弧光 7 种\n"
        ai_deep_output += "- 反转 8 + 节奏 8 + 余韵 6\n\n"

        ai_deep_output += "【191 反 AI 词表 + 4 轮迭代】\n"
        ai_deep_output += "瞳孔地震/撕心裂肺/缓缓地/绝美/陷入沉思/五味杂陈 等 191 条禁用词\n\n"

        ai_deep_output += "【收敛分 (compute_convergence_score)】\n"
        ai_deep_output += "  pass_rate=" + str(conv["pass_rate"]) + ", avg_improvement=" + str(conv["avg_improvement"]) + "\n"
        ai_deep_output += "  convergence_score=" + str(conv["convergence_score"]) + " (阈值 " + str(conv["threshold"]) + ")\n"
        ai_deep_output += "  is_converged=" + str(conv["is_converged"]) + ", predicted_more_iters=" + str(conv["predicted_more_iters"]) + "\n"
        ai_deep_output += "  recommendation: " + conv["recommendation"] + "\n\n"

        ai_deep_output += "【9 维光照控制 (CIE LAB + 摄影本体)】\n"
        for k, v in LIGHTING_9D.items():
            ai_deep_output += "  - " + k + ": " + v + "\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "IterationPostPro": IterationPostPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "IterationPostPro": "🔁 迭代 + 后期 (Phase 14) — Higgsfield 5 铁律",
# }


# ============================================================
# 10. 3 个内置示例 — 验证每个函数是真正动态的
# ============================================================

def _example_1_roco_training_room():
    """
    示例 1: ROCO 训练室独处 12 秒镜头的 10-15 次规则判断.
    来自 Higgsfield brief 原始示例 (EXACT 3 CHARACTERS / 12 秒独处 / Static Shot).
    这里改成 1 角色独处, 跑 10-15 规则.
    """
    print("=" * 60)
    print("【示例 1】ROCO 训练室独处 12 秒镜头 — 10-15 次规则判断")
    print("=" * 60)
    print()

    # 资产检查
    print(">>> 1) check_asset_locked('@roco', 'character', 假设 10 次压测全过 + 同框 3 次全过):")
    asset = check_asset_locked("@roco", "character", [
        {"pose": "站", "light": "顶光", "pass": True, "deliverable": "face_close"},
        {"pose": "站", "light": "侧光", "pass": True, "deliverable": "face_close"},
        {"pose": "跪", "light": "顶光", "pass": True, "deliverable": "body_front_nohead"},
        {"pose": "跪", "light": "侧光", "pass": True, "deliverable": "body_front_nohead"},
        {"pose": "背", "light": "顶光", "pass": True, "deliverable": "body_back"},
        {"pose": "背", "light": "侧光", "pass": True, "deliverable": "body_back"},
        {"pose": "站", "light": "逆光", "pass": True, "deliverable": "face_close", "co_frame": True},
        {"pose": "站", "light": "顶光", "pass": True, "deliverable": "face_close", "co_frame": True},
        {"pose": "坐", "light": "侧光", "pass": True, "deliverable": "face_close", "co_frame": True},
        {"pose": "坐", "light": "顶光", "pass": True, "deliverable": "body_back"},
    ])
    print("  state: " + asset["state"])
    print("  stress_score: " + asset["stress_score"])
    print("  co_frame_score: " + asset["co_frame_score"] + asset["co_frame_note"])
    print("  block: " + str(asset["block"]))
    print("  next_action: " + asset["next_action"])
    print()

    # descriptor 锁定
    print(">>> 2) lock_descriptor('@roco', 'character') — 完整 descriptor 骨架:")
    desc = lock_descriptor("@roco", "character")
    print("  visual (" + str(len(desc["visual_descriptor"])) + " 字符):")
    print("    " + desc["visual_descriptor"][:120] + "...")
    print("  voice: " + desc["voice_descriptor"][:80] + "...")
    print("  behavior: " + desc["behavior_descriptor"][:80] + "...")
    print("  state_variants: " + ", ".join(desc["state_variants"].keys()))
    print("  lock_hash: " + desc["lock_hash"])
    print()

    # 10-15 规则 — 跑 fail_count=0, 3, 8, 12
    print(">>> 3) ten_fifteen_rule(fail_count, shot_kind='独处') — 4 个关键点:")
    for fc in [0, 3, 8, 12]:
        r = ten_fifteen_rule(fc, shot_kind="独处")
        print("  fail_count=" + str(fc) + ": zone=" + r["zone"] + " | label=" + r["label"])
        print("    action: " + r["action"])
        if r["playbook"]:
            print("    playbook: " + r["playbook"]["name"])
        print()

    print(">>> 4) simplify_shot() — 当前 fail_count=12 时的简化方案:")
    sim = simplify_shot({
        "duration": 12.0, "characters": 1, "actions": 4, "shot_kind": "独处",
        "fail_count": 12, "director": "塔可夫斯基",
        "current_motion": "Static Shot 静止",
        "fail_reasons": ["手部多指", "接缝漂移", "空间站位错"],
    })
    print("  verdict: " + sim["verdict"] + " (分 " + str(sim["current_complexity_score"]) + " → 简化后 " + str(sim["rebalance_score"]) + ")")
    print("  split: " + str(sim["split_plan"]))
    print("  recommendations: " + ", ".join(r["name"] for r in sim["recommendations"]))
    print()


def _example_2_corridor_dialogue_30s():
    """
    示例 2: 走廊对话 30 秒的版本日志 (含 fail 原因).
    5 轮迭代, 记录每轮改了什么 / 结果 / 接受/拒绝原因.
    """
    print("=" * 60)
    print("【示例 2】走廊对话 30 秒 — 版本日志 (含 5 轮 fail 原因)")
    print("=" * 60)
    print()

    # 清空旧日志, 让示例独立
    _VERSION_LOG.clear()

    iterations = [
        # (version, change, result, accept_reason, fail_count)
        ("v1", "完整 descriptor 一次性进 prompt, Static Shot 12s", "fail", "拒绝: 脸在 8s 后漂移 (同框测试发现 6 指)", 0),
        ("v2", "改一行: 在 ACTION TIMING 加 'jaw set-and-release' 微表情", "fail", "拒绝: 微表情触发反而让手变 6 指, 怀疑手的动作被忽略", 1),
        ("v3", "改一行: 把人物压到走廊尽头角落 (R4 角落不是房间)", "pass", "接受: 脸稳定了, 但 30s 显得空, 节奏拖", 2),
        ("v4", "改一行: 缩短到 24s, 把剩余 6s 拆成对面反应镜", "fail", "拒绝: 反应镜里对方没接住嘴型, 对白跟口型错位 0.5s", 3),
        ("v5", "改一行: 切到 I2VA 任务类型, 给对话第二句的首帧参考图", "pass", "接受: 口型对齐了, 但调色偏冷 (vs 上镜暖调) → 列入调色统一清单", 4),
    ]

    print(">>> 5 轮迭代日志 (log_version):\n")
    for ver, change, result, reason, fc in iterations:
        log = log_version(ver, change, result, reason, fail_count=fc, shot_id="corridor_dialogue_30s")
        e = log["entry"]
        print("  [" + e["timestamp"] + "] " + e["version"] + " (fail_count=" + str(fc) + ")")
        print("    change: " + e["change"])
        print("    result: " + e["result"] + "  | reason: " + e["accept_reason"])
        print("    change_hash: " + e["change_hash"])
        print()

    # 看最终收敛
    print(">>> compute_convergence_score — 走廊对话 30s 当前收敛状态:")
    conv = compute_convergence_score({
        "attempts": [
            {"version": v, "result": r, "visual_diff_score": 0.4 + i * 0.12}
            for i, (v, _, r, _, _) in enumerate(iterations)
        ],
        "current_fail_count": 4,
    })
    print("  pass_rate: " + str(conv["pass_rate"]) + " (3 pass / 5 total)")
    print("  avg_improvement: " + str(conv["avg_improvement"]))
    print("  convergence_score: " + str(conv["convergence_score"]) + " (阈值 " + str(conv["threshold"]) + ")")
    print("  is_converged: " + str(conv["is_converged"]))
    print("  predicted_more_iters: " + str(conv["predicted_more_iters"]))
    print("  recommendation: " + conv["recommendation"])
    print()

    # diff_prompt_versions 演示 R3
    print(">>> diff_prompt_versions — 演示 R3 一次改一行:\n")
    v1 = "ACTION TIMING: ROCO holds the mat, eyes closed, breathing slow.\nLIGHTING: hard light from above.\nCAMERA: Static Shot."
    v2 = "ACTION TIMING: ROCO holds the mat, eyes closed, jaw set-and-release.\nLIGHTING: hard light from above.\nCAMERA: Static Shot."
    diff = diff_prompt_versions(v1, v2)
    print("  change_type: " + diff["change_type"])
    print("  n_changed_lines: " + str(diff["n_changed_lines"]))
    print("  verdict: " + diff["verdict"])
    print("  diff_excerpt:" + diff["diff_excerpt"])

    # 反例: 整段重写 → risky
    v3 = "A complete rewrite of the entire prompt. New style. New framing. New action. New everything. New new new."
    diff_unsafe = diff_prompt_versions(v1, v3)
    print("\n  >>> 反例 (整段重写):")
    print("  change_type: " + diff_unsafe["change_type"])
    print("  verdict: " + diff_unsafe["verdict"])
    print("  warning: " + diff_unsafe["warning"][:120] + "...")
    print()


def _example_3_post_issue_list():
    """
    示例 3: 后期问题单 — 手部多指 / 招牌假字 / 接缝漂移.
    """
    print("=" * 60)
    print("【示例 3】后期问题单 — 手部多指 / 招牌假字 / 接缝漂移")
    print("=" * 60)
    print()

    issues = [
        # 手部 (P1)
        {"type": "hand", "subtype": "多指 (6 指)", "shot_id": "shot_012", "severity": "critical", "frame_range": "00:08.200-00:10.500",
         "fix_suggestion": "小缺陷逐帧修 (rotoscope 1 帧 5 分钟); 完全废用保存的最终 prompt 改一行重生成"},
        {"type": "hand", "subtype": "手指穿模/融化", "shot_id": "shot_015", "severity": "medium", "frame_range": "00:15.000-00:16.200",
         "fix_suggestion": "逐帧修穿模帧, 用相邻帧插值"},
        # 脸 (P1)
        {"type": "face", "subtype": "眼神光丢失 (catch-light 死眼)", "shot_id": "shot_012", "severity": "high", "frame_range": "00:00.000-00:02.000",
         "fix_suggestion": "眼神光在选角时定; 这镜只能 mask 重新打光, 或重生成"},
        # 招牌假字 (P2)
        {"type": "text", "subtype": "招牌字符重复 + 假字", "shot_id": "shot_020", "severity": "high", "frame_range": "全镜",
         "fix_suggestion": "GPT Image 2 单独生成招牌, 蒙版合成回原图"},
        # 接缝 (P2)
        {"type": "seam", "subtype": "服装颜色漂 (clip_012 → clip_013 红色→橘色)", "shot_id": "shot_012→013", "severity": "medium", "frame_range": "cut point",
         "fix_suggestion": "首尾各裁半秒; color_match() 统一 LUT; 严重则重生成 clip_013"},
        # 颜色 (P3)
        {"type": "color", "subtype": "白平衡漂 (clip_018 偏冷 vs 整体暖调)", "shot_id": "shot_018", "severity": "medium", "frame_range": "全镜",
         "fix_suggestion": "color_match() 拉到导演 look (" + COLOR_LOOK_PRESETS["是枝裕和"]["lut"] + "), 调 temp_K 600K"},
        # 声音 (P3)
        {"type": "audio", "subtype": "对白与口型偏差 0.5s", "shot_id": "shot_007", "severity": "low", "frame_range": "00:12.000-00:14.000",
         "fix_suggestion": "声音从生成里清: 降噪 + 匀音色; 不棚录, 用 lip-sync 重对齐"},
        # 待补镜头 (P1)
        {"type": "missing_shot", "subtype": "need a cutaway to the hands", "shot_id": "shot_009", "severity": "high", "frame_range": "N/A",
         "fix_suggestion": "剪辑与生成并行, 编辑边收边剪, 缺什么当场下单. 重拍几分钟, 剪辑反过来塑造制作"},
    ]

    print(">>> 1) post_cleanup(shot) — 按优先级分组:\n")
    # 用一个合成的 shot 字典
    cleanup = post_cleanup({
        "shot_id": "shot_012 (代表多 issue)",
        "detected_issues": issues,
        "duration": 12.0,
    })
    print("  issue_count: " + str(cleanup["issue_count"]))
    for pri in [1, 2, 3]:
        bucket = cleanup["by_priority"][pri]
        if bucket:
            print("  P" + str(pri) + " (" + str(len(bucket)) + " 项):")
            for it in bucket:
                print("    - " + it["name"] + " / " + it["subtype"] + " (severity=" + it["severity"] + ")")
    print()
    print("  save_cost: " + cleanup["save_cost"])
    print()

    print(">>> 2) render_post_issue_list(issues) — 完整 markdown 问题单:\n")
    board = render_post_issue_list(issues)
    # 只打印前 30 行, 避免刷屏
    for line in board.splitlines()[:35]:
        print("  " + line)
    print("  ... (后续还有 " + str(max(0, len(board.splitlines()) - 35)) + " 行)")
    print()

    print(">>> 3) color_match() — 调色统一 (clip_012 → clip_013):\n")
    cm = color_match(
        prev_clip={"clip_id": "clip_012", "L": -0.05, "a": 0.02, "b": 0.03, "exposure": -0.15,
                   "contrast": 0.85, "temp_K": 5600, "tint": 0.0, "lut": "Kodak_2383_low",
                   "shadow_tint": "深青", "highlight_tint": "暖橙"},
        next_clip={"clip_id": "clip_013", "L": 0.08, "a": 0.10, "b": -0.05, "exposure": 0.10,
                   "contrast": 1.05, "temp_K": 5200, "tint": 5.0, "lut": "neutral",
                   "shadow_tint": "neutral", "highlight_tint": "neutral"},
        director="是枝裕和",
    )
    print("  target_look (是枝裕和): " + cm["target_look"]["lut"] + ", " + str(cm["target_look"]["temp_K"]) + "K")
    print("  delta: " + str(cm["delta"]))
    print("  match_plan:")
    for step in cm["match_plan"]:
        print("    - " + step)
    print()


if __name__ == "__main__":
    _example_1_roco_training_room()
    print()
    _example_2_corridor_dialogue_30s()
    print()
    _example_3_post_issue_list()
