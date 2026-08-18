# -*- coding: utf-8 -*-
"""
Phase 17 - 导演灵魂节点 (Director Soul Node)
================================================
L5+ 顶级导演级 + AIGC 影视全流程解析 + 情感矩阵 + 灵魂维度

核心设计哲学:
- AI 不会有真正的"灵魂" (个人、欲望、创伤、叛逆)
- 但可以用情感矩阵 + 融合算法 + 灵魂维度来**极限模拟**顶级导演的"灵魂"
- 让所有其他节点能接收灵魂注入

核心组成:
1. EMOTION_MATRIX_60 - 60+ 种情感完整定义 (基于 Plutchik + Izard + Geneva + Barrett)
2. EMOTION_FUSION_7 - 7 大情感融合公式 (单情感 / 双情感 / 多情感 + 不同比例)
3. SOUL_DIMENSIONS_10 - 10 大灵魂维度 (创造力/想象力/艺术表达/镜头语言/氛围掌控/精神状态/灵感/叛逆/怀疑/突破)
4. SOUL_STATE - 当前灵魂状态 (灵感指数/疲劳指数/叛逆指数/怀疑指数)
5. SOUL_OUTPUT - 注入到所有其他节点的格式

参考理论:
- Plutchik's Wheel of Emotions (1980) - 8 基础情感 + 强度 + 二元组合
- Izard 10 基础情感 (1977)
- Geneva Emotion Wheel (GEW) - 4 维情感
- Barrett 建构情绪理论 (2006) - 情绪是大脑在情境和先验下建构的
- Lazarus 认知-评价理论
- Russell 环形模型 (Valence-Arousal 2D)
"""

import os
import sys
import json
import random
import math
import hashlib

# ============================================================
# 0. 联网检索数据加载 (Phase 35.5 - 35 导演 + 100 场景)
# ============================================================
_WEB_DB_LOADED = False
_WEB_DIRECTOR_PROFILES = {}
_WEB_SCENE_DATABASE = []
_WEB_QUOTES = []
_WEB_FACTS = []
_WEB_SIX_DIM = {}

# Phase 36.2: MiniMax-H3 prompt 框架 (5 模式 + camera 3D + Ref2VA 6 段)
_H3_FRAMEWORK_LOADED = False
try:
    from knowledge_base.h3_prompt_framework import (
        H3_MODES,
        H3_REF2VA_SECTIONS,
        CAMERA_MOTION_TYPES,
        RETENTION_MARKERS_VISIBLE,
        RETENTION_MARKERS_AUDIO,
        H3_REFERENCE_LABELS,
        H3_ADDON_INJECTION_PLAN,
        H3_OFFICIAL_SKILLS_SUMMARY,
        render_camera_motion as _h3_render_camera,
        select_h3_mode as _h3_select_mode,
    )
    _H3_FRAMEWORK_LOADED = True
except Exception:
    pass

try:
    from knowledge_base.web_research_director_db import (
        DIRECTOR_PROFILES as _WEB_DIRECTOR_PROFILES,
        SCENE_DATABASE as _WEB_SCENE_DATABASE,
        DIRECTOR_QUOTES as _WEB_QUOTES,
        INDUSTRY_FACTS as _WEB_FACTS,
        DIRECTOR_SIX_DIM as _WEB_SIX_DIM,
    )
    _WEB_DB_LOADED = True
except Exception:
    try:
        from web_research_director_db import (
            DIRECTOR_PROFILES as _WEB_DIRECTOR_PROFILES,
            SCENE_DATABASE as _WEB_SCENE_DATABASE,
            DIRECTOR_QUOTES as _WEB_QUOTES,
            INDUSTRY_FACTS as _WEB_FACTS,
            DIRECTOR_SIX_DIM as _WEB_SIX_DIM,
        )
        _WEB_DB_LOADED = True
    except Exception:
        pass

# ============================================================
# 1. EMOTION_MATRIX_60 - 60+ 种情感完整定义
# ============================================================
# 基于 Plutchik 8 基础情感 + 3 强度级别 + 复合二元 + Izard 10 基础 + 复杂情感
EMOTION_MATRIX_60 = {
    # ===== 8 基础情感 (Plutchik) × 3 强度 = 24 种 =====
    # 1. Joy (喜悦) - 极性正
    "joy_serenity": {
        "name": "Serenity 安宁",
        "category": "Joy",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "内心平静, 波澜不惊, 微笑而不动声色",
        "visual_signs": "微微上扬嘴角, 呼吸平稳, 眼神温和不闪烁",
        "voice_signs": "语速中速, 音调中等, 没有起伏",
        "facial_au": "AU12 (轻微嘴角上扬)",
        "inner_monologue": "这一刻, 我选择不打扰这份安宁",
        "color_palette": "淡蓝, 浅米, 雾白",
        "music_tempo": "60-70 BPM, 钢琴单音",
        "director_examples": "是枝裕和《步履不停》 - 全家聚餐, 安宁的午后",
    },
    "joy_pleasure": {
        "name": "Pleasure 愉悦",
        "category": "Joy",
        "intensity": 0.6,
        "polarity": "positive",
        "arousal": "medium",
        "description": "发自内心的满足和快乐",
        "visual_signs": "明显笑容, 眼睛眯起, 身体微微前倾",
        "voice_signs": "语速略快, 音调高, 有自然停顿的笑声",
        "facial_au": "AU6+AU12 (杜兴式微笑)",
        "inner_monologue": "这一刻值得被记住",
        "color_palette": "暖黄, 浅粉, 蜜桃",
        "music_tempo": "80-100 BPM, 弦乐轻快",
        "director_examples": "宫崎骏《龙猫》 - 姐妹俩在田野奔跑",
    },
    "joy_ecstasy": {
        "name": "Ecstasy 狂喜",
        "category": "Joy",
        "intensity": 1.0,
        "polarity": "positive",
        "arousal": "high",
        "description": "极致的高潮, 失去自我控制",
        "visual_signs": "大笑, 身体完全放松, 手臂张开",
        "voice_signs": "语速极快, 音调极高, 笑声不断",
        "facial_au": "AU6+AU12+AU25+AU26 (全开笑)",
        "inner_monologue": "这一刻我是完整的",
        "color_palette": "金黄, 朱红, 鲜橙",
        "music_tempo": "120-150 BPM, 鼓点密集",
        "director_examples": "PTA《不羁夜》 - 色情业黄金时代的派对高潮",
    },
    # 2. Trust (信任) - 极性正
    "trust_acceptance": {
        "name": "Acceptance 接纳",
        "category": "Trust",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "接受现状, 没有防备",
        "visual_signs": "身体放松, 双手自然垂放, 没有紧张动作",
        "voice_signs": "语速慢, 音调平, 没有抑扬",
        "facial_au": "AU1+AU2 (眉毛自然)",
        "inner_monologue": "我不需要解释, 你也不需要",
        "color_palette": "米白, 浅灰绿, 燕麦",
        "music_tempo": "50-60 BPM, 大提琴",
        "director_examples": "王家卫《花样年华》 - 走廊里的擦肩而过",
    },
    "trust_admiration": {
        "name": "Admiration 仰慕",
        "category": "Trust",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对他人由衷的尊重和欣赏",
        "visual_signs": "眼睛注视对方, 微微点头, 嘴角上扬",
        "voice_signs": "音调略高, 语速正常, 偶尔停顿表示尊重",
        "facial_au": "AU1+AU2+AU12",
        "inner_monologue": "这个人值得我学习",
        "color_palette": "暖金, 灰蓝, 米色",
        "music_tempo": "70-80 BPM, 小提琴独奏",
        "director_examples": "斯皮尔伯格《林肯》 - 林肯看麦克白",
    },
    "trust_surrender": {
        "name": "Surrender 臣服",
        "category": "Trust",
        "intensity": 1.0,
        "polarity": "positive",
        "arousal": "high",
        "description": "完全交出控制权, 极致信任",
        "visual_signs": "身体完全放松, 闭眼, 双手打开",
        "voice_signs": "语速极慢, 音调低, 完全柔软",
        "facial_au": "AU43 (闭眼) + AU1+AU2 (无防备)",
        "inner_monologue": "我把自己完全交给你",
        "color_palette": "柔白, 浅金, 淡粉",
        "music_tempo": "40-50 BPM, 风铃",
        "director_examples": "塔可夫斯基《飞向太空》 - 宇宙中的彻底静谧",
    },
    # 3. Fear (恐惧) - 极性负
    "fear_timidity": {
        "name": "Timidity 胆怯",
        "category": "Fear",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "隐约的不安, 怕被注意",
        "visual_signs": "肩膀微缩, 视线躲避, 身体语言收缩",
        "voice_signs": "音量小, 语速慢, 经常停顿",
        "facial_au": "AU4 (眉间皱)",
        "inner_monologue": "也许没人注意到我",
        "color_palette": "灰紫, 暗蓝, 苍白",
        "music_tempo": "50-60 BPM, 弦乐低吟",
        "director_examples": "伯格曼《假面》 - 伊丽莎白在派对角落",
    },
    "fear_apprehension": {
        "name": "Apprehension 忧虑",
        "category": "Fear",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "medium",
        "description": "对未来的明确担忧",
        "visual_signs": "咬唇, 手指搓动, 眼神不定",
        "voice_signs": "语速不规律, 经常重复, 音调颤抖",
        "facial_au": "AU4+AU5+AU7+AU20 (焦虑组合)",
        "inner_monologue": "接下来会发生什么",
        "color_palette": "深绿, 冷蓝, 铁灰",
        "music_tempo": "70-80 BPM, 渐强弦乐",
        "director_examples": "希区柯克《后窗》 - 杰夫发现真相",
    },
    "fear_terror": {
        "name": "Terror 恐惧",
        "category": "Fear",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的惊恐, 完全失去理性",
        "visual_signs": "瞳孔放大, 嘴张, 全身僵硬, 脸色苍白",
        "voice_signs": "尖叫, 语速失控, 音调极高",
        "facial_au": "AU1+AU2+AU5+AU20+AU26 (恐惧全开)",
        "inner_monologue": "完了完了完了",
        "color_palette": "血红, 漆黑, 惨白",
        "music_tempo": "150+ BPM, 失谐弦乐",
        "director_examples": "波兰斯基《罗斯玛丽的婴儿》 - 罗斯玛丽看到孩子",
    },
    # 4. Surprise (惊讶) - 极性中性
    "surprise_uncertainty": {
        "name": "Uncertainty 困惑",
        "category": "Surprise",
        "intensity": 0.3,
        "polarity": "neutral",
        "arousal": "low",
        "description": "不确定发生了什么的瞬间",
        "visual_signs": "眉毛微抬, 头微倾, 眼睛微眯",
        "voice_signs": "音调上扬, 语速变慢, 经常\"嗯?\"",
        "facial_au": "AU1+AU2 (轻微扬眉)",
        "inner_monologue": "等等, 这是什么",
        "color_palette": "雾灰, 浅紫, 米白",
        "music_tempo": "50-60 BPM, 不和谐音",
        "director_examples": "林奇《穆赫兰道》 - Betty 醒来",
    },
    "surprise_astonishment": {
        "name": "Astonishment 惊讶",
        "category": "Surprise",
        "intensity": 0.7,
        "polarity": "neutral",
        "arousal": "high",
        "description": "明确感到出乎意料",
        "visual_signs": "眼睛睁大, 嘴微张, 身体后仰",
        "voice_signs": "音量增大, 语速变快, 经常\"啊!\"",
        "facial_au": "AU1+AU2+AU5B+AU26 (惊讶全开)",
        "inner_monologue": "这不可能!",
        "color_palette": "亮白, 鲜红, 鲜蓝",
        "music_tempo": "突然的强音",
        "director_examples": "诺兰《记忆碎片》 - Lenny 找到照片",
    },
    "surprise_amazement": {
        "name": "Amazement 惊异",
        "category": "Surprise",
        "intensity": 1.0,
        "polarity": "positive/neutral",
        "arousal": "high",
        "description": "面对伟大或神秘的敬畏",
        "visual_signs": "眼睛极亮, 嘴张, 双手举起, 后退半步",
        "voice_signs": "语速极慢, 经常无言, 偶发\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU26 (震撼全开)",
        "inner_monologue": "这是真的存在吗",
        "color_palette": "金色, 极光色, 紫红",
        "music_tempo": "全乐队爆发",
        "director_examples": "维伦纽瓦《降临》 - 第一次看到外星人文字",
    },
    # 5. Sadness (悲伤) - 极性负
    "sadness_gloominess": {
        "name": "Gloominess 阴郁",
        "category": "Sadness",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "淡淡的忧伤, 没有原因的失落",
        "visual_signs": "眉下垂, 嘴角下垂, 视线下移",
        "voice_signs": "音调低, 语速慢, 经常停顿",
        "facial_au": "AU1+AU4+AU15 (悲伤三件套)",
        "inner_monologue": "不知道为什么, 有点难过",
        "color_palette": "灰蓝, 暗紫, 阴沉",
        "music_tempo": "40-50 BPM, 钢琴低音",
        "director_examples": "王家卫《重庆森林》 - 何志武在电话亭旁",
    },
    "sadness_sorrow": {
        "name": "Sorrow 悲痛",
        "category": "Sadness",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "medium",
        "description": "明确的失去带来的痛苦",
        "visual_signs": "眼眶湿润, 嘴唇紧抿, 身体蜷缩",
        "voice_signs": "音调颤抖, 经常哽咽, 句子碎裂",
        "facial_au": "AU1+AU4+AU7+AU15+AU17 (悲痛全开)",
        "inner_monologue": "为什么是他 / 为什么是她",
        "color_palette": "深蓝灰, 阴雨色, 苍白",
        "music_tempo": "30-40 BPM, 大提琴低吟",
        "director_examples": "是枝裕和《步履不停》 - 黄昏散步, 想起长子",
    },
    "sadness_grief": {
        "name": "Grief 悲恸",
        "category": "Sadness",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的失去, 不可承受的痛",
        "visual_signs": "哭, 全身颤抖, 身体折叠, 失语",
        "voice_signs": "无声, 哭到失声, 反复抽泣",
        "facial_au": "AU1+AU4+AU7+AU15+AU17+AU43 (全开)",
        "inner_monologue": "再也回不来了",
        "color_palette": "漆黑, 极暗蓝, 阴影",
        "music_tempo": "停止, 只有呼吸声",
        "director_examples": "PTA《魅影缝匠》 - Reynolds 在餐厅崩溃",
    },
    # 6. Disgust (厌恶) - 极性负
    "disgust_dislike": {
        "name": "Dislike 反感",
        "category": "Disgust",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "轻微的不喜欢, 距离感",
        "visual_signs": "嘴角微撇, 鼻翼微皱, 视线偏移",
        "voice_signs": "音调平, 经常叹气",
        "facial_au": "AU9 (轻微上唇提)",
        "inner_monologue": "我不太想接近",
        "color_palette": "灰绿, 暗黄, 浊色",
        "music_tempo": "60-70 BPM, 慢板",
        "director_examples": "伯格曼《沉默》 - 姐妹俩的疏离",
    },
    "disgust_revulsion": {
        "name": "Revulsion 反感",
        "category": "Disgust",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "明确的排斥和不适",
        "visual_signs": "后仰, 遮脸, 身体退缩",
        "voice_signs": "呕吐反射, 音调升高",
        "facial_au": "AU9+AU15+AU17 (厌恶组合)",
        "inner_monologue": "这太恶心了",
        "color_palette": "恶心的黄绿, 浊紫",
        "music_tempo": "不和谐音",
        "director_examples": "PTA《血色将至》 - Daniel 第一次看到矿井",
    },
    "disgust_loathing": {
        "name": "Loathing 憎恶",
        "category": "Disgust",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的厌恶, 道德层面的强烈排斥",
        "visual_signs": "嘴歪, 眼寒, 全身紧绷, 准备攻击",
        "voice_signs": "音量极高, 音调尖锐, 颤抖",
        "facial_au": "AU9+AU15+AU16+AU17+AU26 (全开)",
        "inner_monologue": "我要让这个人付出代价",
        "color_palette": "毒绿, 焦黑, 病态黄",
        "music_tempo": "失谐重音",
        "director_examples": "奉俊昊《寄生虫》 - 金基泽看朴社长",
    },
    # 7. Anger (愤怒) - 极性负
    "anger_annoyance": {
        "name": "Annoyance 烦恼",
        "category": "Anger",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "轻度的不耐烦, 没有爆发",
        "visual_signs": "眉头微皱, 嘴角下撇, 视线躲避",
        "voice_signs": "音调略高, 经常叹气",
        "facial_au": "AU4+AU17 (皱眉 + 嘴角下)",
        "inner_monologue": "我不想被打扰",
        "color_palette": "暗橙, 浊黄",
        "music_tempo": "70 BPM, 烦躁弦乐",
        "director_examples": "王家卫《阿飞正传》 - 旭仔被拒绝后",
    },
    "anger_frustration": {
        "name": "Frustration 挫败",
        "category": "Anger",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "明确感到挫败, 但未完全爆发",
        "visual_signs": "咬牙, 拳握, 鼻翼张, 视线锁定",
        "voice_signs": "语速快, 音调高, 经常咬字",
        "facial_au": "AU4+AU5+AU7+AU17+AU23 (愤怒组合)",
        "inner_monologue": "我一定要做到",
        "color_palette": "红橙, 暗红",
        "music_tempo": "100 BPM, 鼓点重",
        "director_examples": "诺兰《黑暗骑士》 - 蝙蝠侠追小丑",
    },
    "anger_fury": {
        "name": "Fury 暴怒",
        "category": "Anger",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的愤怒, 失去理性",
        "visual_signs": "吼, 摔物, 攻击, 全身通红",
        "voice_signs": "咆哮, 音调极高, 完全失控",
        "facial_au": "AU4+AU5+AU7+AU17+AU23+AU26+AU27 (全开)",
        "inner_monologue": "我要毁了一切",
        "color_palette": "血红, 漆黑, 火焰色",
        "music_tempo": "失谐重击",
        "director_examples": "芬奇《七宗罪》 - Pitt 看到冰箱里",
    },
    # 8. Anticipation (期待) - 极性正
    "anticipation_interest": {
        "name": "Interest 兴趣",
        "category": "Anticipation",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "对某事的轻微好奇",
        "visual_signs": "眉毛微抬, 头微前倾, 眼神专注",
        "voice_signs": "音调略高, 语速略快",
        "facial_au": "AU1+AU2 (抬眉)",
        "inner_monologue": "我有点想知道",
        "color_palette": "浅黄, 暖白",
        "music_tempo": "70 BPM, 轻快",
        "director_examples": "诺兰《盗梦空间》 - Cobb 看陀螺",
    },
    "anticipation_expectation": {
        "name": "Expectation 期待",
        "category": "Anticipation",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "明确的期待感, 关注未来",
        "visual_signs": "身体前倾, 眼睛睁大, 嘴角微扬",
        "voice_signs": "语速加快, 音调升高, 经常追问",
        "facial_au": "AU1+AU2+AU5+AU12 (期待组合)",
        "inner_monologue": "快了, 快了",
        "color_palette": "暖橙, 鲜黄, 浅红",
        "music_tempo": "90 BPM, 渐强",
        "director_examples": "诺兰《信条》 - 主角理解时间逆转",
    },
    "anticipation_vigilance": {
        "name": "Vigilance 警觉",
        "category": "Anticipation",
        "intensity": 1.0,
        "polarity": "neutral",
        "arousal": "high",
        "description": "极度警觉, 准备应对威胁",
        "visual_signs": "眼睛扫描环境, 全身紧绷, 准备行动",
        "voice_signs": "语速极快, 音调高, 简短的命令式",
        "facial_au": "AU1+AU2+AU4+AU5+AU7 (警觉全开)",
        "inner_monologue": "准备行动",
        "color_palette": "冷蓝, 银白, 警戒橙",
        "music_tempo": "120 BPM, 紧张鼓点",
        "director_examples": "诺兰《敦刻尔克》 - 飞行员在驾驶舱",
    },
    # ===== Izard 10 基础情感 (扩展 Plutchik) =====
    "interest": {
        "name": "Interest 兴趣",
        "category": "Izard",
        "intensity": 0.5,
        "polarity": "positive",
        "arousal": "medium",
        "description": "主动的探索欲, 注意力集中",
        "visual_signs": "眉毛微抬, 眼睛明亮, 头前倾",
        "voice_signs": "音调升高, 语速加快",
        "facial_au": "AU1+AU2+AU7 (兴趣组合)",
        "inner_monologue": "我想了解更多",
        "color_palette": "亮黄, 浅绿",
        "music_tempo": "80 BPM, 好奇弦乐",
        "director_examples": "塔可夫斯基《镜子》 - 探索童年",
    },
    "shyness": {
        "name": "Shyness 羞怯",
        "category": "Izard",
        "intensity": 0.5,
        "polarity": "negative",
        "arousal": "medium",
        "description": "被注意时的不自在",
        "visual_signs": "视线下移, 身体微缩, 脸红",
        "voice_signs": "音量小, 语速慢, 经常中断",
        "facial_au": "AU1+AU2+AU20 (羞怯组合)",
        "inner_monologue": "我宁愿不被看到",
        "color_palette": "淡粉, 苍白",
        "music_tempo": "60 BPM, 轻柔",
        "director_examples": "伯格曼《芬妮与亚历山大》 - 孩子们",
    },
    "guilt": {
        "name": "Guilt 愧疚",
        "category": "Izard",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "对做过的事的内疚",
        "visual_signs": "视线下移, 身体蜷缩, 不敢看人",
        "voice_signs": "音量小, 经常道歉, 句子断",
        "facial_au": "AU1+AU4+AU15 (内疚组合)",
        "inner_monologue": "我不该那样做",
        "color_palette": "暗灰, 阴绿",
        "music_tempo": "40 BPM, 钢琴单音",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲独白",
    },
    "contempt": {
        "name": "Contempt 轻蔑",
        "category": "Izard",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "low",
        "description": "从道德/智识层面的优越感俯视",
        "visual_signs": "单侧嘴角上扬, 视线俯视",
        "voice_signs": "音调平, 经常用\"哼\"开头",
        "facial_au": "AU12R (单侧嘴角上扬) + AU14",
        "inner_monologue": "你不配",
        "color_palette": "暗金, 浊紫",
        "music_tempo": "50 BPM, 单音",
        "director_examples": "斯科塞斯《华尔街之狼》 - Belfort 看客户",
    },
    "shame": {
        "name": "Shame 羞耻",
        "category": "Izard",
        "intensity": 0.8,
        "polarity": "negative",
        "arousal": "high",
        "description": "暴露后的强烈自我否定",
        "visual_signs": "头低垂, 想消失, 脸通红",
        "voice_signs": "完全失语, 或者极小声",
        "facial_au": "AU1+AU4+AU20+AU52 (羞耻组合)",
        "inner_monologue": "我应该消失",
        "color_palette": "血红色 (脸部) + 灰色 (背景)",
        "music_tempo": "30 BPM, 完全安静",
        "director_examples": "布努埃尔《泯灭天使》 - 上流社会的崩溃",
    },
    "pride": {
        "name": "Pride 骄傲",
        "category": "Izard",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对自己的成就感",
        "visual_signs": "胸挺, 头高, 视线平视",
        "voice_signs": "音调高, 语速正常, 坚定",
        "facial_au": "AU12+AU53+AU58 (骄傲组合)",
        "inner_monologue": "我做到了",
        "color_palette": "金, 深红, 皇家蓝",
        "music_tempo": "100 BPM, 雄壮弦乐",
        "director_examples": "PTA《不羁夜》 - Dirk 完成电影",
    },
    # ===== 5 大复杂情感 (复合) =====
    "love": {
        "name": "Love 爱",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "positive",
        "arousal": "medium",
        "description": "Joy + Trust 二元组合, 深层依恋",
        "visual_signs": "注视对方时瞳孔扩张, 嘴角自然上扬, 身体微微前倾",
        "voice_signs": "音调柔和, 语速放慢, 经常停顿",
        "facial_au": "AU6+AU12+AU1+AU2 (爱的微表情)",
        "inner_monologue": "我愿意为你做任何事",
        "color_palette": "暖金 + 浅粉, 玫瑰金",
        "music_tempo": "60-80 BPM, 弦乐 + 钢琴",
        "director_examples": "王家卫《花样年华》 - 周慕云与苏丽珍",
        "fusion": "Joy + Trust",
    },
    "hate": {
        "name": "Hate 恨",
        "category": "Complex",
        "intensity": 0.95,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anger + Fear 二元组合, 极致敌意",
        "visual_signs": "眼睛冰冷, 嘴紧, 全身僵硬",
        "voice_signs": "完全冰冷, 经常沉默",
        "facial_au": "AU4+AU5+AU7+AU17+AU24 (恨的组合)",
        "inner_monologue": "我要让你付出代价",
        "color_palette": "漆黑, 血红, 死灰",
        "music_tempo": "50 BPM, 不和谐音",
        "director_examples": "PTA《血色将至》 - Plainview 杀 Eli",
        "fusion": "Anger + Fear",
    },
    "awe": {
        "name": "Awe 敬畏",
        "category": "Complex",
        "intensity": 0.9,
        "polarity": "positive",
        "arousal": "high",
        "description": "Fear + Surprise 二元组合, 面对伟大的震撼",
        "visual_signs": "眼睛极大, 嘴张, 后退半步, 双手举起",
        "voice_signs": "语速极慢, 经常无言, 偶发\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU26+AU27 (敬畏全开)",
        "inner_monologue": "这超越了语言",
        "color_palette": "金色, 极光色, 紫红, 圣光",
        "music_tempo": "全乐队 + 和声",
        "director_examples": "维伦纽瓦《降临》 - Louise 看外星文字",
        "fusion": "Fear + Surprise",
    },
    "aggressiveness": {
        "name": "Aggressiveness 攻击性",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anger + Anticipation 二元组合, 准备攻击",
        "visual_signs": "身体前倾, 拳紧, 鼻翼张, 视线锁定",
        "voice_signs": "音调高, 攻击性语速, 经常咆哮",
        "facial_au": "AU4+AU5+AU7+AU17+AU23+AU26 (攻击组合)",
        "inner_monologue": "先发制人",
        "color_palette": "血红, 黑, 攻击橙",
        "music_tempo": "120 BPM, 失谐鼓点",
        "director_examples": "希区柯克《精神病患者》 - Norman 戴母亲面具",
        "fusion": "Anger + Anticipation",
    },
    "optimism": {
        "name": "Optimism 乐观",
        "category": "Complex",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "Anticipation + Joy 二元组合, 期待好事",
        "visual_signs": "眼睛明亮, 嘴角自然上扬, 身体放松",
        "voice_signs": "语速略快, 音调高, 经常用未来时",
        "facial_au": "AU6+AU12+AU1+AU2+AU5 (乐观组合)",
        "inner_monologue": "明天会更好",
        "color_palette": "浅金, 暖白, 浅蓝",
        "music_tempo": "80 BPM, 轻快弦乐",
        "director_examples": "宫崎骏《哈尔的移动城堡》 - 苏菲变年轻后",
        "fusion": "Anticipation + Joy",
    },
    "disapproval": {
        "name": "Disapproval 反对",
        "category": "Complex",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "medium",
        "description": "Surprise + Sadness 二元组合, 失望",
        "visual_signs": "嘴角下撇, 摇头, 视线回避",
        "voice_signs": "音调低, 经常用\"但是\"",
        "facial_au": "AU1+AU4+AU15 (反对组合)",
        "inner_monologue": "我不认同",
        "color_palette": "灰蓝, 暗紫",
        "music_tempo": "60 BPM, 低音",
        "director_examples": "斯科塞斯《基督最后的诱惑》 - 宗教审判",
        "fusion": "Surprise + Sadness",
    },
    "remorse": {
        "name": "Remorse 悔恨",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "negative",
        "arousal": "low",
        "description": "Sadness + Disgust 二元组合, 对自己行为的痛",
        "visual_signs": "眼眶湿润, 全身蜷缩, 头低",
        "voice_signs": "经常说\"我错了\"",
        "facial_au": "AU1+AU4+AU15+AU17 (悔恨组合)",
        "inner_monologue": "我多希望时光倒流",
        "color_palette": "深蓝, 灰紫, 苍白",
        "music_tempo": "30 BPM, 大提琴低吟",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲的独白",
        "fusion": "Sadness + Disgust",
    },
    # ===== 10 种状态情感 (Plutchik 之外的更复杂组合) =====
    "loneliness": {
        "name": "Loneliness 孤独",
        "category": "State",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "渴望连接但无连接的状态",
        "visual_signs": "身体蜷缩, 视线远眺, 经常独自一人",
        "voice_signs": "经常沉默, 偶发自言自语",
        "facial_au": "AU1+AU4+AU15+AU43 (孤独组合)",
        "inner_monologue": "有谁在听吗",
        "color_palette": "冷蓝, 苍白, 灰",
        "music_tempo": "40 BPM, 单音钢琴",
        "director_examples": "塔可夫斯基《镜子》 - 独居的母亲",
    },
    "longing": {
        "name": "Longing 思念",
        "category": "State",
        "intensity": 0.7,
        "polarity": "mixed",
        "arousal": "medium",
        "description": "对远方的人/物的深刻思念",
        "visual_signs": "凝视远方, 手抚旧物, 眼有泪光",
        "voice_signs": "音调柔, 经常说远方的人名",
        "facial_au": "AU1+AU2+AU4+AU15+AU43 (思念组合)",
        "inner_monologue": "如果他在就好了",
        "color_palette": "暖黄, 雾蓝, 金光",
        "music_tempo": "50-60 BPM, 大提琴 + 钢琴",
        "director_examples": "王家卫《春光乍泄》 - 黎耀辉在瀑布前",
    },
    "bittersweet": {
        "name": "Bittersweet 苦乐参半",
        "category": "State",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Joy + Sadness 同时存在",
        "visual_signs": "微笑时眼角有泪, 笑声变轻",
        "voice_signs": "经常停顿, 句子在结尾时变轻",
        "facial_au": "AU6+AU12+AU1+AU4+AU15 (矛盾组合)",
        "inner_monologue": "如果我快乐的时候你在就好了",
        "color_palette": "金 + 蓝, 暖白 + 冷灰",
        "music_tempo": "60 BPM, 大调小调交替",
        "director_examples": "是枝裕和《步履不停》 - 母亲去世后父亲做天妇罗",
        "fusion": "Joy + Sadness",
    },
    "nostalgia": {
        "name": "Nostalgia 怀旧",
        "category": "State",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "对过去的温暖回忆, 略带忧伤",
        "visual_signs": "抚摸旧物, 看老照片, 微笑而眼神遥远",
        "voice_signs": "经常说\"那时候...\"",
        "facial_au": "AU1+AU2+AU6+AU12+AU15 (怀旧组合)",
        "inner_monologue": "那时候一切都简单",
        "color_palette": "褪色暖色, 暖黄, 复古蓝",
        "music_tempo": "60 BPM, 复古钢琴",
        "director_examples": "王家卫《花样年华》 - 60 年代的香港",
    },
    "tension": {
        "name": "Tension 紧张",
        "category": "State",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anticipation + Fear 同时存在, 等待坏事",
        "visual_signs": "咬指甲, 全身紧绷, 视线锁定",
        "voice_signs": "音调不稳, 语速快, 经常屏气",
        "facial_au": "AU4+AU5+AU7+AU20+AU23 (紧张组合)",
        "inner_monologue": "希望不要发生",
        "color_palette": "冷蓝, 紧张红, 阴影",
        "music_tempo": "100 BPM, 紧张弦乐渐强",
        "director_examples": "希区柯克《惊魂记》 - 浴室场景",
        "fusion": "Anticipation + Fear",
    },
    "tenderness": {
        "name": "Tenderness 温柔",
        "category": "State",
        "intensity": 0.6,
        "polarity": "positive",
        "arousal": "low",
        "description": "对脆弱的事物的保护性温柔",
        "visual_signs": "动作轻柔, 声音放低, 眼神温柔",
        "voice_signs": "音调极低极柔, 经常用昵称",
        "facial_au": "AU1+AU2+AU12+AU41 (温柔组合)",
        "inner_monologue": "我来保护你",
        "color_palette": "暖粉, 浅金, 柔白",
        "music_tempo": "50 BPM, 钢琴 + 弦乐轻奏",
        "director_examples": "是枝裕和《奇迹》 - 父母对孩子的温柔",
    },
    "relief": {
        "name": "Relief 如释重负",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "长期压力后的突然释放",
        "visual_signs": "全身放松, 长呼气, 微笑浮现",
        "voice_signs": "语速变慢, 音量降低, 经常\"啊...\"",
        "facial_au": "AU1+AU2+AU12+AU24 (释然组合)",
        "inner_monologue": "终于过去了",
        "color_palette": "暖白, 浅蓝, 柔和",
        "music_tempo": "60 BPM, 渐慢",
        "director_examples": "诺兰《盗梦空间》 - Cobb 见到孩子",
    },
    "despair": {
        "name": "Despair 绝望",
        "category": "State",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "low",
        "description": "完全失去希望, 比悲伤更深",
        "visual_signs": "眼神失焦, 全身瘫软, 不愿动",
        "voice_signs": "完全失语, 或者极小声",
        "facial_au": "AU1+AU4+AU15+AU17+AU43 (绝望组合)",
        "inner_monologue": "已经没有任何意义了",
        "color_palette": "深灰, 死蓝, 苍白",
        "music_tempo": "20 BPM, 只有呼吸声",
        "director_examples": "塔可夫斯基《牺牲》 - 主人公的献祭",
    },
    "hope": {
        "name": "Hope 希望",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "在黑暗中看到光明的状态",
        "visual_signs": "眼睛亮, 嘴角自然上扬, 身体微微挺",
        "voice_signs": "音调升高, 经常用未来时",
        "facial_au": "AU1+AU2+AU5+AU12 (希望组合)",
        "inner_monologue": "总会有办法的",
        "color_palette": "暖金, 浅黄, 晨曦",
        "music_tempo": "70 BPM, 渐强轻快",
        "director_examples": "宫崎骏《千与千寻》 - 千寻找到工作",
    },
    "gratitude": {
        "name": "Gratitude 感恩",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "对他人善意的深刻感谢",
        "visual_signs": "双手交握, 微微鞠躬, 眼神真诚",
        "voice_signs": "音调柔, 经常说\"谢谢\"",
        "facial_au": "AU1+AU2+AU6+AU12 (感恩组合)",
        "inner_monologue": "我真的很幸运",
        "color_palette": "暖金, 米白, 淡蓝",
        "music_tempo": "50 BPM, 大提琴 + 钢琴",
        "director_examples": "是枝裕和《比海更深》 - 母子重逢",
    },
    "wonder": {
        "name": "Wonder 惊奇",
        "category": "State",
        "intensity": 0.8,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对世界/生命奥秘的惊叹",
        "visual_signs": "凝视, 身体前倾, 表情混合惊讶+喜悦",
        "voice_signs": "语速慢, 经常\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU12 (惊奇组合)",
        "inner_monologue": "这真神奇",
        "color_palette": "金, 紫, 极光色",
        "music_tempo": "70 BPM, 渐强",
        "director_examples": "宫崎骏《天空之城》 - 看到飞行石",
    },
    # ===== 12 种复杂情感 (Phase 17.3 补充) =====
    # 东方特有情感 (中式美学)
    "yuan": {
        "name": "Yuan 怨 (中式幽怨)",
        "category": "Complex Eastern",
        "intensity": 0.75,
        "polarity": "negative",
        "arousal": "low",
        "description": "中式特有的幽怨, 委屈但不说, 久久不散",
        "visual_signs": "眉下垂, 嘴角下撇但克制, 眼神幽怨, 经常独自一人",
        "voice_signs": "音调低, 语速慢, 经常停顿, 经常说\"没什么\"",
        "facial_au": "AU1+AU4+AU15+AU17 (幽怨组合)",
        "inner_monologue": "我又能说什么呢",
        "color_palette": "暗蓝灰, 黛色, 烟雨色",
        "music_tempo": "40 BPM, 古琴/二胡",
        "director_examples": "王家卫《花样年华》 - 苏丽珍的旗袍背影",
    },
    "chouchang": {
        "name": "Chouchang 惆怅 (中式惆怅)",
        "category": "Complex Eastern",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "对失去/不可追的淡淡惆怅",
        "visual_signs": "远眺, 轻叹, 偶尔摇头",
        "voice_signs": "经常长叹, 语速极慢",
        "facial_au": "AU1+AU4+AU15+AU43 (惆怅组合)",
        "inner_monologue": "时光不等人",
        "color_palette": "暮色, 远山蓝, 暖灰",
        "music_tempo": "30 BPM, 笛子",
        "director_examples": "侯孝贤《悲情城市》 - 远望山景",
    },
    "ji": {
        "name": "Ji 寂 (中式寂静)",
        "category": "Complex Eastern",
        "intensity": 0.5,
        "polarity": "mixed",
        "arousal": "low",
        "description": "不只是孤独, 是宇宙性的寂静, 与天地合一",
        "visual_signs": "完全静坐, 呼吸极慢, 眼神深远",
        "voice_signs": "完全失语, 偶发极轻叹息",
        "facial_au": "AU1+AU2+AU43+AU47 (寂的组合)",
        "inner_monologue": "无",
        "color_palette": "水墨, 留白, 单色",
        "music_tempo": "10 BPM, 只有风声",
        "director_examples": "侯孝贤《刺客聂隐娘》 - 山中静坐",
    },
    "chou": {
        "name": "Chou 愁 (中式愁绪)",
        "category": "Complex Eastern",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "对家国/时事的深沉忧愁",
        "visual_signs": "眉头紧锁, 远眺, 经常抚摸旧物",
        "voice_signs": "音调低沉, 经常长叹",
        "facial_au": "AU1+AU4+AU15 (愁绪组合)",
        "inner_monologue": "国将何如",
        "color_palette": "铁灰, 暮色, 衰草色",
        "music_tempo": "20 BPM, 古琴",
        "director_examples": "侯孝贤《悲情城市》 - 林家客厅",
    },
    # 复杂矛盾情感
    "bittersweet_pain": {
        "name": "Bittersweet Pain 甜蜜的痛苦",
        "category": "Complex Paradox",
        "intensity": 0.8,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Joy + Sadness 矛盾融合, 快乐与痛苦并存",
        "visual_signs": "微笑时眼角有泪, 笑声变轻, 身体微微颤抖",
        "voice_signs": "句子结尾变轻, 经常欲言又止",
        "facial_au": "AU6+AU12+AU1+AU4+AU15+AU43 (矛盾组合)",
        "inner_monologue": "如果这一刻能停止就好了",
        "color_palette": "金 + 蓝, 暖光 + 冷阴影",
        "music_tempo": "50 BPM, 大调小调交替",
        "director_examples": "是枝裕和《步履不停》 - 母亲去世后父亲做天妇罗",
        "fusion": "Joy + Sadness",
    },
    "warm_regret": {
        "name": "Warm Regret 温暖的遗憾",
        "category": "Complex Paradox",
        "intensity": 0.7,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Trust + Sadness 矛盾, 遗憾中带温暖",
        "visual_signs": "抚摸旧物, 微笑回忆, 偶尔眼角湿",
        "voice_signs": "经常说\"那时候...\"",
        "facial_au": "AU6+AU12+AU1+AU4+AU15+AU43 (温暖遗憾)",
        "inner_monologue": "如果当时能多陪你一会儿",
        "color_palette": "暖金, 复古蓝, 旧照片色",
        "music_tempo": "60 BPM, 复古钢琴",
        "director_examples": "王家卫《一代宗师》 - 叶问看宫二照片",
        "fusion": "Trust + Sadness",
    },
    "hopeless_hope": {
        "name": "Hopeless Hope 绝望的希望",
        "category": "Complex Paradox",
        "intensity": 0.85,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Sadness + Anticipation 矛盾, 绝望中还有期待",
        "visual_signs": "眼神混合绝望和希望, 嘴角在笑和不笑之间",
        "voice_signs": "句子破碎, 经常说\"也许...\"",
        "facial_au": "AU1+AU4+AU15+AU17+AU5 (绝望希望)",
        "inner_monologue": "也许...不会的",
        "color_palette": "暗金, 蓝灰, 黎明前",
        "music_tempo": "60 BPM, 渐强渐弱",
        "director_examples": "诺兰《星际穿越》 - 库珀看墨菲",
        "fusion": "Sadness + Anticipation",
    },
    "love_hate": {
        "name": "Love-Hate 爱到深处的恨",
        "category": "Complex Paradox",
        "intensity": 0.95,
        "polarity": "mixed",
        "arousal": "high",
        "description": "Love + Hate 极矛盾, 极致爱恨交织",
        "visual_signs": "看对方时眼睛混合柔情和凶光, 手握紧又松开",
        "voice_signs": "温柔和咆哮交替, 经常突然沉默",
        "facial_au": "AU6+AU12+AU4+AU17+AU26 (爱恨交织)",
        "inner_monologue": "我恨你, 但我离不开你",
        "color_palette": "血红 + 玫红, 黑金",
        "music_tempo": "50-100 BPM 剧烈变化, 不和谐音",
        "director_examples": "PTA《魅影缝匠》 - Reynolds 看 Alma",
        "fusion": "Love + Hate",
    },
    # 哲学性情感
    "lucid_despair": {
        "name": "Lucid Despair 清醒的绝望",
        "category": "Complex Philosophical",
        "intensity": 0.95,
        "polarity": "negative",
        "arousal": "low",
        "description": "完全清醒地意识到绝望, 没有自我欺骗",
        "visual_signs": "眼神完全清醒但失焦, 嘴角极轻微苦笑",
        "voice_signs": "音调完全平, 没有起伏, 经常说\"我知道\"",
        "facial_au": "AU1+AU4+AU15+AU17+AU53 (清醒绝望)",
        "inner_monologue": "我看得很清楚, 这就是结局",
        "color_palette": "无色, 苍白, 灰",
        "music_tempo": "20 BPM, 单音大提琴",
        "director_examples": "塔可夫斯基《牺牲》 - 主人公献祭前",
    },
    "awed_fear": {
        "name": "Awed Fear 敬畏的恐惧",
        "category": "Complex Philosophical",
        "intensity": 0.85,
        "polarity": "mixed",
        "arousal": "high",
        "description": "Fear + Awe 矛盾, 面对伟大的恐惧和敬畏并存",
        "visual_signs": "后退半步但眼睛无法离开, 身体颤抖但不跑",
        "voice_signs": "语速极慢, 经常沉默, 偶发极轻的声音",
        "facial_au": "AU1+AU2+AU5+AU20+AU26+AU27 (敬畏恐惧)",
        "inner_monologue": "这太伟大了, 让我害怕",
        "color_palette": "极光, 神光, 深紫, 银",
        "music_tempo": "全乐队 + 和声 + 低音",
        "director_examples": "维伦纽瓦《降临》 - Louise 第一次看到外星人",
        "fusion": "Fear + Awe",
    },
    "tender_contradiction": {
        "name": "Tender Contradiction 矛盾的温柔",
        "category": "Complex Paradox",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "Joy + Sadness + Trust 三元, 温柔中带忧伤",
        "visual_signs": "轻轻抚摸, 眼神温柔但含泪",
        "voice_signs": "音调极柔, 句子经常未完成",
        "facial_au": "AU1+AU2+AU6+AU12+AU15 (矛盾温柔)",
        "inner_monologue": "我多希望这一刻能永远",
        "color_palette": "暖白, 浅金, 暮色",
        "music_tempo": "50 BPM, 钢琴 + 弦乐",
        "director_examples": "是枝裕和《步履不停》 - 母亲最后的散步",
        "fusion": "Joy + Sadness + Trust",
    },
    "perfect_regret": {
        "name": "Perfect Regret 完美的遗憾",
        "category": "Complex Philosophical",
        "intensity": 0.9,
        "polarity": "negative",
        "arousal": "low",
        "description": "Joy + Sadness 极致融合, 已经做到最好但还是失去",
        "visual_signs": "已经完成, 但眼神中无光",
        "voice_signs": "完全平静, 经常用过去时",
        "facial_au": "AU1+AU2+AU4+AU12+AU15+AU17+AU53 (完美遗憾)",
        "inner_monologue": "我已经做了所有能做的",
        "color_palette": "极淡蓝, 苍白金, 暮雪",
        "music_tempo": "30 BPM, 大提琴 + 钢琴",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲的独白",
        "fusion": "Joy + Sadness",
    },
}


# ============================================================
# 2. EMOTION_FUSION_7 - 7 大情感融合公式
# ============================================================
EMOTION_FUSION_7 = {
    "F1_单情感主导": {
        "name": "Single Emotion Dominant",
        "description": "整场戏只有一种情感, 这是最常见的 70% 场景",
        "weight_distribution": "100% single",
        "scenarios": "大多数普通场景, 单一明确情绪",
        "director_examples": "王家卫《重庆森林》- 何志武独白 (loneliness 100%)",
    },
    "F2_双情感主次融合": {
        "name": "Dual Emotion Primary-Secondary",
        "description": "两种情感, 一种主导 (70%) + 一种次要 (30%)",
        "weight_distribution": "70% primary + 30% secondary",
        "scenarios": "角色有表层和内层, 表面平静内心激动, 这是 25% 场景",
        "director_examples": "《情感价值》- 父亲表面平静 (acceptance 70%) 内里悔恨 (remorse 30%)",
    },
    "F3_双情感对等融合": {
        "name": "Dual Emotion Equal",
        "description": "两种情感对等 (50/50), 矛盾并存",
        "weight_distribution": "50% + 50%",
        "scenarios": "角色内心矛盾, 这是 20% 场景",
        "director_examples": "《花样年华》- 压抑欲望 (tenderness 50% + repression 50%)",
    },
    "F4_三情感递进融合": {
        "name": "Triple Emotion Progressive",
        "description": "三种情感, 随场景递进",
        "weight_distribution": "20% + 30% + 50% (随时间变化)",
        "scenarios": "角色经历情感变化, 这是 10% 场景",
        "director_examples": "《步履不停》- 兴趣→关切→悔恨",
    },
    "F5_矛盾情感爆炸": {
        "name": "Contradictory Explosion",
        "description": "两种极端矛盾情感同时达到峰值",
        "weight_distribution": "50% + 50% (intensity 1.0 + 1.0)",
        "scenarios": "角色在极端压力下情感崩溃, 5% 场景",
        "director_examples": "奉俊昊《寄生虫》- 朴社长在地下室的绝望 (disgust 100% + fear 100% 矛盾)",
    },
    "F6_复合情绪三角": {
        "name": "Compound Emotion Triangle",
        "description": "三种情感形成稳定复合体",
        "weight_distribution": "33% + 33% + 33%",
        "scenarios": "复杂心理状态, 2% 场景",
        "director_examples": "PTA《魅影缝匠》- Reynolds 复杂情感 (love 33% + obsession 33% + control 33%)",
    },
    "F7_情感转化": {
        "name": "Emotional Transformation",
        "description": "情感在场景内发生根本性转化",
        "weight_distribution": "100% emotion_A → 100% emotion_B",
        "scenarios": "情感转折点, 1% 场景, 但最重要",
        "director_examples": "《泰坦尼克号》- Jack 死时 Rose 从 love 100% → grief 100%",
    },
}


# ============================================================
# 3. SOUL_DIMENSIONS_10 - 10 大灵魂维度
# ============================================================
SOUL_DIMENSIONS_10 = {
    "D1_创造力": {
        "name": "Creativity 创造力",
        "description": "突破常规的联想能力, 把不相关的事物组合成新的意义",
        "low": "完全照搬已有模式, 产出'安全'但平庸的作品",
        "high": "能在寻常中看到不寻常, 产出'反预期'但'本该如此'的作品",
        "expression": "新隐喻 / 跨类比 / 反转预期 / 解构经典",
        "director_examples": "PTA 用石油和牛奶做权力隐喻 / 奉俊昊用楼梯做阶层隐喻",
    },
    "D2_想象力": {
        "name": "Imagination 想象力",
        "description": "在头脑中构建尚未存在的事物的能力",
        "low": "只能处理已经存在的素材",
        "high": "能在头脑中构建完整的虚构世界 (角色/空间/历史/物理规则)",
        "expression": "世界观构建 / 角色前史 / 平行宇宙 / 时间旅行 / 梦境",
        "director_examples": "维伦纽瓦构建 Arrakis 沙丘世界 / 林奇构建 Twin Peaks",
    },
    "D3_艺术表达力": {
        "name": "Artistic Expression 艺术表达力",
        "description": "用具体的艺术形式承载抽象情感的能力",
        "low": "用形容词表达 (美/丑/好/坏)",
        "high": "用具体的视觉/声音/动作表达抽象情感 (用一根头发表达爱情)",
        "expression": "物件代替心理 / 微动作代替情绪 / 视觉象征 / 声音隐喻",
        "director_examples": "王家卫用凤梨罐头代替时间 / 库斯杜力卡用沉默代替悲伤",
    },
    "D4_镜头语言技巧": {
        "name": "Camera Language Skill 镜头语言技巧",
        "description": "用摄影机运动/焦段/构图控制观众的眼睛和情感",
        "low": "所有镜头都中景 + 平稳",
        "high": "每个镜头都有独特的镜头语言服务于叙事和情感",
        "expression": "焦段变化 / 运动设计 / 构图引导 / 视角选择 / 镜头长度",
        "director_examples": "Roger Deakins 用景深构图 / Lubezki 用长镜头 + 自然光",
    },
    "D5_画面氛围掌控": {
        "name": "Visual Atmosphere Control 画面氛围掌控",
        "description": "用光线/色彩/质感营造情绪的能力",
        "low": "所有场景光线都一样",
        "high": "每个场景都有独特的光影氛围服务于情感",
        "expression": "60:30:10 色彩 / 9 维光影 / 质感选择 / 天气影响",
        "director_examples": "泰伦斯·马力克《天堂之日》 - 黄金时刻光 / 格雷厄姆《灯塔》 - 黑白高压",
    },
    "D6_精神状态": {
        "name": "Mental State 精神状态",
        "description": "导演创作时当下的精神状态, 影响所有决策",
        "states": ["清醒 (lucid)", "梦幻 (dreamy)", "焦虑 (anxious)", "平静 (serene)", "狂热 (manic)", "疲惫 (exhausted)", "激进 (radical)", "保守 (conservative)"],
        "impact": "不同精神状态导致完全不同的镜头选择",
        "director_examples": "PTA 《不羁夜》 - 70 年代迷幻精神状态 / 塔可夫斯基《镜子》 - 梦游精神状态",
    },
    "D7_灵感时刻": {
        "name": "Inspiration Moment 灵感时刻",
        "description": "在创作中突然涌现的『突然知道怎么拍』的瞬间",
        "manifestations": [
            "突然改变镜头角度",
            "突然改变色调",
            "突然加一个不相关的细节",
            "突然改变剪辑节奏",
            "突然改变演员调度",
        ],
        "frequency": "伟大导演每部片有 5-20 个真正的灵感时刻",
        "director_examples": "诺兰《盗梦空间》火车冲入街道 / 奉俊昊《寄生虫》暴雨倒流楼梯",
    },
    "D8_叛逆度": {
        "name": "Rebelliousness 叛逆度",
        "description": "打破规则的勇气和意愿",
        "low": "严格遵守行业规则",
        "high": "在关键时刻敢于打破一切规则",
        "manifestations": [
            "拒绝传统三幕剧结构",
            "拒绝给观众明确答案",
            "拒绝商业大团圆",
            "拒绝美化主角",
            "拒绝 happy ending",
        ],
        "director_examples": "林奇《穆赫兰道》 - 完全无解释 / 安哲罗普洛斯《永恒与一日》 - 完全非线性",
    },
    "D9_自我怀疑": {
        "name": "Self-Doubt 自我怀疑",
        "description": "对自己作品的不安, 推动反复修改",
        "low": "拍完就发布",
        "high": "反复重拍, 反复质疑自己的选择, 直到最后一刻",
        "manifestations": [
            "反复重写剧本",
            "反复重拍同一场景",
            "反复重剪",
            "发布前仍在修改",
        ],
        "director_examples": "泰伦斯·马力克 反复重剪 / 库布里克 反复重拍",
    },
    "D10_突破勇气": {
        "name": "Breakthrough Courage 突破勇气",
        "description": "在压力下做出真正创新的选择",
        "low": "选择安全的方案",
        "high": "选择真正创新但风险巨大的方案",
        "manifestations": [
            "选择非专业演员",
            "选择实验性叙事结构",
            "选择困难的主题",
            "选择不商业的结尾",
        ],
        "director_examples": "诺兰用 IMAX 拍《黑暗骑士》/ 奉俊昊《寄生虫》全非线性",
    },
}


# ============================================================
# 3.5 EMOTION_ALIASES - 情感别名映射 (兼容用户直觉输入)
# ============================================================
# 用户/节点的合理输入可能是基础情感 (fear) 或裸子词 (apprehension) 或复合 (loneliness)
# 我们把所有合理别名映射到 EMOTION_MATRIX_60 中的具体 key
# 中等强度子词作为默认 (apprehension/sorrow/pleasure 等)
EMOTION_ALIASES = {
    # ===== Plutchik 8 基础情感 → 中等强度子词 =====
    "fear":         "fear_apprehension",
    "joy":          "joy_pleasure",
    "trust":        "trust_admiration",
    "surprise":     "surprise_astonishment",
    "sadness":      "sadness_sorrow",
    "disgust":      "disgust_revulsion",
    "anger":        "anger_frustration",
    "anticipation": "anticipation_expectation",
    # ===== 24 子词裸名 → 完整 key (中等强度优先) =====
    "timidity":     "fear_timidity",
    "apprehension": "fear_apprehension",
    "terror":       "fear_terror",
    "serenity":     "joy_serenity",
    "pleasure":     "joy_pleasure",
    "ecstasy":      "joy_ecstasy",
    "acceptance":   "trust_acceptance",
    "admiration":   "trust_admiration",
    "surrender":    "trust_surrender",
    "uncertainty":  "surprise_uncertainty",
    "astonishment": "surprise_astonishment",
    "amazement":    "surprise_amazement",
    "gloominess":   "sadness_gloominess",
    "sorrow":       "sadness_sorrow",
    "grief":        "sadness_grief",
    "dislike":      "disgust_dislike",
    "revulsion":    "disgust_revulsion",
    "loathing":     "disgust_loathing",
    "annoyance":    "anger_annoyance",
    "frustration":  "anger_frustration",
    "fury":         "anger_fury",
    "interest_emotion": "anticipation_interest",
    "interest_emo": "anticipation_interest",
    "expectation":  "anticipation_expectation",
    "vigilance":    "anticipation_vigilance",
    # ===== Izard 6 扩展 - 已直接是 key, 但兼容 snake/camel =====
    "guilt":        "guilt",
    "shame":        "shame",
    "pride":        "pride",
    "contempt":     "contempt",
    "shyness":      "shyness",
    "interest":     "interest",
    # ===== 常见中文情感到英文 key =====
    "孤独":         "loneliness",
    "寂寞":         "loneliness",
    "思念":         "longing",
    "渴望":         "longing",
    "焦虑":         "tension",
    "紧张":         "tension",
    "温柔":         "tenderness",
    "柔情":         "tenderness",
    "怀旧":         "nostalgia",
    "惆怅":         "chouchang",
    "寂":           "ji",
    "愁":           "chou",
    "怨":           "yuan",
    "恐惧":         "fear_apprehension",
    "害怕":         "fear_timidity",
    "喜悦":         "joy_pleasure",
    "快乐":         "joy_pleasure",
    "高兴":         "joy_pleasure",
    "悲伤":         "sadness_sorrow",
    "痛苦":         "sadness_grief",
    "愤怒":         "anger_frustration",
    "憎恨":         "hate",
    "爱":           "love",
    "信任":         "trust_admiration",
    "希望":         "hope",
    "绝望":         "despair",
    "感激":         "gratitude",
    "惊奇":         "surprise_astonishment",
    "震惊":         "surprise_amazement",
    "厌恶":         "disgust_revulsion",
    "反感":         "disgust_dislike",
    "期待":         "anticipation_expectation",
    "警觉":         "anticipation_vigilance",
    "内疚":         "guilt",
    "羞耻":         "shame",
    "骄傲":         "pride",
    "轻蔑":         "contempt",
    "害羞":         "shyness",
    "兴味":         "interest",
    "释然":         "relief",
    "宽慰":         "relief",
    "温暖遗憾":     "warm_regret",
    "清醒绝望":     "lucid_despair",
    "敬畏恐惧":     "awed_fear",
    "矛盾温柔":     "tender_contradiction",
    "完美遗憾":     "perfect_regret",
    "甜蜜痛苦":     "bittersweet_pain",
    "绝望希望":     "hopeless_hope",
    "爱恨交织":     "love_hate",
}


def _resolve_emotion_aliases(emotion_keys: list) -> list:
    """解析情感别名 - 基础情感/裸子词/中文 → EMOTION_MATRIX_60 key"""
    resolved = []
    for k in emotion_keys:
        if k in EMOTION_MATRIX_60:
            resolved.append(k)
        elif k in EMOTION_ALIASES:
            target = EMOTION_ALIASES[k]
            # 防止别名指向不存在的 key
            if target in EMOTION_MATRIX_60:
                resolved.append(target)
            else:
                # 别名指向无效 key, 跳过
                pass
        # 都不在 - 跳过 (不要让单个错误拖垮整个融合)
    return resolved


# ============================================================
# 4. SOUL_FUSION_ENGINE - 情感融合引擎
# ============================================================
def fuse_emotions(emotion_keys: list, weights: list = None, mode: str = "auto"):
    """
    情感融合引擎 - 核心算法
    input: 情感 key 列表 + 权重 (可选) + 模式 (F1-F7)
    output: 融合后的完整情感档案

    Phase 17.1 增强: 自动解析情感别名 (fear→fear_apprehension, 恐惧→fear_apprehension, etc.)
    """
    if not emotion_keys:
        return None
    # Phase 17.1: 别名解析 - 让用户/节点能用直觉输入 (fear, 恐惧, etc.)
    emotion_keys = _resolve_emotion_aliases(emotion_keys)

    # 验证情感存在
    valid_emotions = [k for k in emotion_keys if k in EMOTION_MATRIX_60]
    if not valid_emotions:
        return None

    # 自动推断模式
    n = len(valid_emotions)
    if mode == "auto":
        if n == 1:
            mode = "F1_单情感主导"
        elif n == 2 and weights is None:
            mode = "F3_双情感对等融合"  # 50/50 默认
        elif n == 2 and weights is not None:
            mode = "F2_双情感主次融合"
        elif n == 3:
            mode = "F4_三情感递进融合"
        elif n >= 4:
            mode = "F6_复合情绪三角"
        else:
            mode = "F1_单情感主导"

    # 默认权重
    if weights is None:
        if mode == "F1_单情感主导":
            weights = [1.0]
        elif mode == "F2_双情感主次融合":
            weights = [0.7, 0.3]
        elif mode == "F3_双情感对等融合":
            weights = [0.5, 0.5]
        elif mode == "F4_三情感递进融合":
            weights = [0.2, 0.3, 0.5]
        elif mode == "F5_矛盾情感爆炸":
            weights = [0.5, 0.5]
        elif mode == "F6_复合情绪三角":
            weights = [1/3] * min(3, n)
            valid_emotions = valid_emotions[:3]
        elif mode == "F7_情感转化":
            weights = [1.0, 1.0]
    # 归一化权重
    total = sum(weights)
    if total > 0:
        weights = [w / total for w in weights]

    # 融合每个字段
    fused = {
        "fusion_mode": mode,
        "emotions": valid_emotions,
        "weights": weights,
        "name": "",
        "category": "Fused",
        "intensity": 0.0,
        "polarity": "neutral",
        "arousal": "medium",
        "description": "",
        "visual_signs": "",
        "voice_signs": "",
        "facial_au": "",
        "inner_monologue": "",
        "color_palette": "",
        "music_tempo": "",
        "director_examples": "",
    }

    for i, ekey in enumerate(valid_emotions):
        emo = EMOTION_MATRIX_60[ekey]
        w = weights[i] if i < len(weights) else 1.0 / len(valid_emotions)

        if not fused["name"]:
            fused["name"] = emo["name"]
        else:
            fused["name"] += f" + {emo['name']}"

        # 加权平均数值
        fused["intensity"] += emo["intensity"] * w

        # 极性: 加权投票
        p = emo["polarity"]
        if p not in ["positive", "negative", "neutral", "mixed"]:
            p = "neutral"
        # 简单累积 (后续可以更复杂)

        # 文本字段: 加权拼接
        if emo.get("description"):
            fused["description"] += f"[{w*100:.0f}%] {emo['description']} "
        if emo.get("visual_signs"):
            fused["visual_signs"] += f"[{w*100:.0f}%] {emo['visual_signs']} "
        if emo.get("voice_signs"):
            fused["voice_signs"] += f"[{w*100:.0f}%] {emo['voice_signs']} "
        if emo.get("facial_au"):
            fused["facial_au"] += f"[{w*100:.0f}%] {emo['facial_au']} "
        if emo.get("inner_monologue"):
            fused["inner_monologue"] += f"[{w*100:.0f}%] {emo['inner_monologue']} "
        if emo.get("color_palette"):
            fused["color_palette"] += f"[{w*100:.0f}%] {emo['color_palette']} "
        if emo.get("music_tempo"):
            fused["music_tempo"] += f"[{w*100:.0f}%] {emo['music_tempo']} "
        if emo.get("director_examples"):
            fused["director_examples"] += f"[{w*100:.0f}%] {emo['director_examples']} "

    # 极性综合判断
    pos_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] == "positive")
    neg_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] == "negative")
    mixed_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] in ["mixed", "neutral"])
    if pos_w > neg_w + mixed_w:
        fused["polarity"] = "positive"
    elif neg_w > pos_w + mixed_w:
        fused["polarity"] = "negative"
    elif mixed_w > 0.3:
        fused["polarity"] = "mixed (矛盾情感)"
    else:
        fused["polarity"] = "neutral"

    # arousal 综合
    high_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["arousal"] == "high")
    low_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["arousal"] == "low")
    if high_w > low_w:
        fused["arousal"] = "high"
    elif low_w > high_w:
        fused["arousal"] = "low"
    else:
        fused["arousal"] = "medium"

    return fused


# ============================================================
# 4.5 SOUL_INJECT_SIMPLE - 统一灵魂注入接口 (Phase 17.1 简化版)
# ============================================================
# 给所有节点用 - 自动处理:
#   1. 8 基础情感 alias 解析 (fear/joy/... → 子词)
#   2. 中文情感词 alias
#   3. 缺失值 fallback
#   4. 灵魂状态动态计算
#   5. 完整注入字符串拼装
# 子 agent 接入时只调这一个函数即可, 不用关心底层细节
DEFAULT_SOUL_DIMS = {
    "creativity": 0.85,
    "imagination": 0.85,
    "artistic_expression": 0.85,
    "camera_skill": 0.85,
    "atmosphere_control": 0.85,
    "mental_state": "lucid-dreamy",
    "inspiration": 0.85,
    "rebelliousness": 0.70,
    "self_doubt": 0.50,
    "breakthrough_courage": 0.85,
}


def _make_fallback_fused(emotion_keys, scene_weight=0.5):
    """当 fuse_emotions 失败时构造最小可用 fused dict"""
    n = len(emotion_keys) if emotion_keys else 1
    return {
        "name": "默认情感 " + " + ".join(emotion_keys or ["neutral"]),
        "emotions": emotion_keys or ["loneliness"],
        "weights": [1.0 / n] * n,
        "fusion_mode": "default",
        "intensity": float(scene_weight),
        "polarity": "neutral",
        "arousal": "medium",
        "description": "默认情感 fallback (子 agent 应该显式传入有效情感)",
        "visual_signs": "无特殊表现",
        "voice_signs": "无特殊表现",
        "facial_au": "无特殊表现",
        "inner_monologue": "",
        "color_palette": "中性灰",
        "music_tempo": "60 BPM",
        "director_examples": "",
    }


def soul_inject_simple(
    primary="auto",          # 主导情感 (支持 8 基础 / 24 子词 / 中文 / 60 复合)
    scene_weight=0.5,        # 场景权重 0-1
    director="",             # 导演风格
    secondary=None,          # 次要情感列表
    fusion_mode="auto",      # F1-F7 / auto
    story_intensity=None,    # 故事强度 (默认 = scene_weight)
    scene_progress=0.5,      # 场景进度 0-1
    soul_dims=None,          # 10 维度 dict (None=默认)
    scene_context="",        # 场景描述
):
    """
    统一灵魂注入接口 (Phase 17.1)
    ---
    子节点接入灵魂的标准入口. 一个函数搞定所有兼容问题.

    Returns:
        injection_str, fused_emotion, soul_state, soul_dims

    Example:
        >>> inj, fused, state, dims = soul_inject_simple(
        ...     primary="fear", scene_weight=0.95, director="诺兰"
        ... )
        >>> "Apprehension" in fused["name"]
        True
    """
    if story_intensity is None:
        story_intensity = scene_weight

    # 1. 构造情感列表
    emotion_keys = []
    if primary and primary != "auto":
        emotion_keys.append(primary)
    if secondary:
        for s in secondary:
            if s and s != "none" and s != "auto":
                emotion_keys.append(s)
    if not emotion_keys:
        emotion_keys = ["loneliness", "longing"]  # 默认 fallback

    # 2. 融合 (fuse_emotions 内部已做 alias 解析)
    fused = fuse_emotions(emotion_keys, None, fusion_mode)
    if not fused:
        fused = _make_fallback_fused(emotion_keys, scene_weight)

    # 3. 灵魂状态动态计算
    try:
        soul_state = compute_soul_state(story_intensity, scene_progress)
    except Exception:
        soul_state = {
            "inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
            "rebelliousness": 0.6, "mental_state": "lucid-dreamy",
        }

    # 4. 灵魂维度
    if soul_dims is None:
        soul_dims = dict(DEFAULT_SOUL_DIMS)

    # 5. 拼装完整注入 (复用 build_soul_injection, 但 force 传入我们的融合结果)
    try:
        injection = build_soul_injection(
            story_emotion_keys=emotion_keys,
            story_weights=None,
            fusion_mode=fusion_mode,
            director=director or "默认",
            scene_context=scene_context,
        )
    except Exception:
        # 兜底: 自己拼一个简版
        injection = (
            "【灵魂注入】\n"
            "主导情感: " + str(fused.get("name", "")) + "\n"
            "强度: " + str(fused.get("intensity", 0.5)) + "\n"
            "极性: " + str(fused.get("polarity", "")) + "\n"
            "导演: " + str(director or "默认") + "\n"
        )

    # 6. Phase 17.7: 真实灵感时刻 (8 大导演 32 个真实电影)
    try:
        moments = get_inspiration_moments(fused, director or "", count=2)
        if moments:
            injection = injection + format_inspiration_moments(moments)
    except Exception:
        pass

    return injection, fused, soul_state, soul_dims


# ============================================================
# 5. SOUL_OUTPUT - 灵魂注入格式 (供其他节点使用)
# ============================================================
def build_soul_injection(
    story_emotion_keys: list = None,
    story_weights: list = None,
    fusion_mode: str = "auto",
    director: str = "王家卫",
    scene_context: str = "",
    soul_dims_override: dict = None,
):
    """
    构建导演灵魂注入 - 供所有其他节点使用
    """
    # 1. 情感融合 (容错: 即使输入不在 60 情感表内也至少返回一个默认)
    try:
        fused_emotion = fuse_emotions(story_emotion_keys or ["loneliness"], story_weights, fusion_mode)
    except Exception:
        fused_emotion = None
    if not fused_emotion:
        # 回退: 通用默认情感
        fused_emotion = {
            "fusion_mode": "F1_单情感主导",
            "emotions": ["loneliness"],
            "weights": [1.0],
            "name": "Loneliness 孤独",
            "category": "Fused",
            "intensity": 0.7,
            "polarity": "negative",
            "arousal": "low",
            "description": "[100%] 渴望连接但无连接的状态",
            "visual_signs": "[100%] 身体蜷缩, 视线远眺, 经常独自一人",
            "voice_signs": "[100%] 经常沉默, 偶发自言自语",
            "facial_au": "[100%] AU1+AU4+AU15+AU43 (孤独组合)",
            "inner_monologue": "[100%] 有谁在听吗",
            "color_palette": "[100%] 冷蓝, 苍白, 灰",
            "music_tempo": "[100%] 40 BPM, 单音钢琴",
            "director_examples": "[100%] 塔可夫斯基《镜子》 - 独居的母亲",
        }

    # 2. 灵魂状态 (基于故事情感 + 导演风格)
    _seed_str = f"{director}:{scene_context}:{fusion_mode}:{','.join(story_emotion_keys or [])}"
    _seed = int(hashlib.md5(_seed_str.encode()).hexdigest()[:8], 16)
    _rng = random.Random(_seed)
    soul_state = {
        "current_inspiration_index": round(_rng.uniform(0.6, 0.95), 2),
        "current_fatigue_index": round(_rng.uniform(0.2, 0.6), 2),
        "current_doubt_index": round(_rng.uniform(0.4, 0.8), 2),
        "current_rebelliousness_index": round(_rng.uniform(0.5, 0.9), 2),
        "current_mental_state": "lucid-dreamy",
    }

    # 3. 灵魂维度 (基于导演)
    _defaults = {
        "creativity": 0.85, "imagination": 0.85, "artistic_expression": 0.85,
        "camera_skill": 0.85, "atmosphere_control": 0.85,
        "mental_state": "lucid-dreamy", "inspiration": 0.85,
        "rebelliousness": 0.70, "self_doubt": 0.50, "breakthrough_courage": 0.80,
    }
    if soul_dims_override:
        _defaults.update(soul_dims_override)
    soul_dimensions = _defaults

    # 4. 灵魂输出
    injection = f"""════════════════════════════════════════
【导演灵魂注入 (Director Soul Injection)】
════════════════════════════════════════

【1. 情感核心】
主导情感: {fused_emotion['name']}
融合模式: {fused_emotion['fusion_mode']}
融合情感: {' + '.join(fused_emotion['emotions'])}
权重: {[f'{w:.2f}' for w in fused_emotion['weights']]}
强度: {fused_emotion['intensity']:.2f}
极性: {fused_emotion['polarity']}
唤醒度: {fused_emotion['arousal']}

【2. 情感表达】
- 视觉表现: {fused_emotion['visual_signs'][:500]}
- 声音表现: {fused_emotion['voice_signs'][:300]}
- 面部肌肉: {fused_emotion['facial_au'][:300]}
- 内心独白: {fused_emotion['inner_monologue'][:300]}

【3. 艺术氛围】
- 色彩: {fused_emotion['color_palette'][:300]}
- 音乐: {fused_emotion['music_tempo'][:300]}

【4. 灵魂状态 (Soul State)】
灵感指数: {soul_state['current_inspiration_index']}
疲劳指数: {soul_state['current_fatigue_index']}
怀疑指数: {soul_state['current_doubt_index']}
叛逆指数: {soul_state['current_rebelliousness_index']}
精神状态: {soul_state['current_mental_state']}

【5. 灵魂维度 (10 Dimensions)】
创造力: {soul_dimensions['creativity']}
想象力: {soul_dimensions['imagination']}
艺术表达: {soul_dimensions['artistic_expression']}
镜头技巧: {soul_dimensions['camera_skill']}
氛围掌控: {soul_dimensions['atmosphere_control']}
精神状态: {soul_dimensions['mental_state']}
灵感时刻: {soul_dimensions['inspiration']}
叛逆度: {soul_dimensions['rebelliousness']}
自我怀疑: {soul_dimensions['self_doubt']}
突破勇气: {soul_dimensions['breakthrough_courage']}

【6. 导演视角】
{director} 的灵魂签名:
- 不写情绪, 写可观察行为 (PTA)
- 让沉默比台词更有力 (库斯杜力卡)
- 用空间叙事 (诺兰)
- 用物件代替心理 (王家卫)
- 用微动作总和等于情感 (L4 表演层)
- 3 留白 + 3 运镜法则 (AIGC 文档)

════════════════════════════════════════
导演: {director}
场景: {scene_context[:100]}
注入模式: SOUL_INJECTION_V1
════════════════════════════════════════
"""
    return injection


# ============================================================
# 6. SOUL_STATE - 当前灵魂状态 (动态变化)
# ============================================================
def compute_soul_state(story_intensity: float = 0.5, scene_progress: float = 0.0):
    """
    计算当前灵魂状态 (基于故事强度和场景进度)
    scene_progress: 0.0 (开场) → 1.0 (结尾)
    """
    # 灵感指数: 开头低, 中间高, 结尾中等
    inspiration = 0.3 + 0.7 * math.exp(-((scene_progress - 0.4) ** 2) / 0.1)

    # 疲劳指数: 随时间累积
    fatigue = min(0.95, 0.1 + scene_progress * 0.85)

    # 怀疑指数: 故事强度越大, 怀疑越低
    doubt = max(0.2, 0.8 - story_intensity * 0.6)

    # 叛逆指数: 故事强度越大, 越可能打破规则
    rebelliousness = min(0.95, 0.4 + story_intensity * 0.5)

    return {
        "inspiration": round(inspiration, 2),
        "fatigue": round(fatigue, 2),
        "doubt": round(doubt, 2),
        "rebelliousness": round(rebelliousness, 2),
        "mental_state": "lucid" if doubt < 0.5 else "anxious-dreamy",
    }


# ============================================================
# 7. SCENE_WEIGHT_INFERENCE - 场景自动权重推断
# ============================================================
SCENE_TYPE_PATTERNS = {
    "key_climax": {
        "patterns": ["高潮", "climax", "决战", "对质", "真相", "爆发", "死亡", "分离"],
        "emotion_count": 2,
        "weight_dist": "50/50",
        "fusion_mode": "F5_矛盾情感爆炸",
        "intensity_boost": 1.3,
        "rationale": "关键场景需要矛盾情感的极致张力",
    },
    "transitional": {
        "patterns": ["过渡", "走路", "等待", "日常", "工作", "吃饭"],
        "emotion_count": 1,
        "weight_dist": "100%",
        "fusion_mode": "F1_单情感主导",
        "intensity_boost": 0.8,
        "rationale": "过渡场景用单情感保持节奏",
    },
    "inner_monologue": {
        "patterns": ["独白", "独处", "回忆", "想象", "内心", "梦境", "monologue", "dream"],
        "emotion_count": 2,
        "weight_dist": "70/30",
        "fusion_mode": "F2_双情感主次融合",
        "intensity_boost": 0.9,
        "rationale": "内心场景是表层 + 内层的双情感",
    },
    "ensemble": {
        "patterns": ["群戏", "聚餐", "会议", "派对", "战争", "ensemble", "group"],
        "emotion_count": 3,
        "weight_dist": "33/33/33",
        "fusion_mode": "F6_复合情绪三角",
        "intensity_boost": 1.1,
        "rationale": "群戏需要多个角色情感的复合",
    },
    "transition_moment": {
        "patterns": ["转折", "转变", "觉醒", "领悟", "决定", "turning", "moment"],
        "emotion_count": 2,
        "weight_dist": "100%→100%",
        "fusion_mode": "F7_情感转化",
        "intensity_boost": 1.5,
        "rationale": "转折点是情感转化的关键时刻",
    },
}


def infer_scene_weights(scene_description: str, scene_progress: float = 0.0, story_intensity: float = 0.5):
    """
    场景自动权重推断 - 根据场景描述自动选择融合公式和情感数量
    """
    if not scene_description:
        return {
            "scene_type": "transitional",
            "emotion_count": 1,
            "fusion_mode": "F1_单情感主导",
            "default_emotion": "loneliness",
            "default_weight": 1.0,
            "intensity_boost": 0.8,
        }

    desc_lower = scene_description.lower()

    # 匹配场景类型
    matched_type = "transitional"
    matched_score = 0
    for scene_type, config in SCENE_TYPE_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern.lower() in desc_lower:
                if len(pattern) > matched_score:
                    matched_type = scene_type
                    matched_score = len(pattern)
                break

    config = SCENE_TYPE_PATTERNS[matched_type]

    # 根据场景进度调整
    progress_boost = 1.0
    if scene_progress > 0.7:
        progress_boost = 1.2  # 结尾加强
    elif scene_progress < 0.2:
        progress_boost = 0.8  # 开场稍弱

    # 根据故事强度调整
    intensity_boost = config["intensity_boost"] * story_intensity * progress_boost

    # 根据融合模式决定默认权重
    if config["weight_dist"] == "100%":
        default_weight = 1.0
        default_emotion = "loneliness"
    elif config["weight_dist"] == "70/30":
        default_weight = 0.7
        default_emotion = "loneliness"
    elif config["weight_dist"] == "50/50":
        default_weight = 0.5
        default_emotion = "tension"
    elif config["weight_dist"] == "33/33/33":
        default_weight = 0.33
        default_emotion = "tension"
    elif config["weight_dist"] == "100%→100%":
        default_weight = 1.0
        default_emotion = "despair"
    else:
        default_weight = 1.0
        default_emotion = "loneliness"

    return {
        "scene_type": matched_type,
        "emotion_count": config["emotion_count"],
        "fusion_mode": config["fusion_mode"],
        "default_emotion": default_emotion,
        "default_weight": default_weight,
        "intensity_boost": round(intensity_boost, 2),
        "rationale": config["rationale"],
    }


# ============================================================
# 8. INSPIRATION_MOMENT - 灵感时刻注入器
# ============================================================
INSPIRATION_MOMENTS = {
    "camera": [
        "突然切换焦段: 35mm 切 85mm, 压缩空间",
        "突然切换视角: 从正面切到俯视, 强调渺小",
        "突然切到主观镜头: 视角从角色切换到角色",
        "突然推近到极特写: 整个画面被眼睛占满",
    ],
    "color": [
        "突然切换色温: 暖色 5600K 切冷色 3200K",
        "突然去饱和: 整个画面瞬间变成黑白",
        "突然加红: 全部色调偏向血红",
        "突然加青: 全部色调偏向青绿, 像监视器",
    ],
    "composition": [
        "突然切对称构图: 之前松散现在绝对居中",
        "突然打破三分法: 主体偏离到画面边缘",
        "突然框中框: 用窗户/门/镜子制造框架",
        "突然消失构图: 留白占满 80%",
    ],
    "rhythm": [
        "突然静止: 之前 3 秒一切换, 突然 15 秒静止",
        "突然跳切: 不连续的两镜直接硬切",
        "突然倒放: 关键瞬间倒放一遍",
        "突然加速: 升格 60fps 切到正常 24fps",
    ],
    "detail": [
        "突然插入不相关细节: 桌上突然多一支烟, 没人点燃",
        "突然特写某个东西: 一滴水 / 一只蚂蚁 / 一根头发",
        "突然声音: 没有画面的环境音先出现 2 秒",
        "突然消失: 角色突然走出画面, 留 5 秒空镜",
    ],
}


def generate_inspiration_moment(seed: int = None, current_progress: float = 0.0):
    """
    生成灵感时刻 - 在场景中突然改变镜头/色彩/构图/节奏
    """
    rng = random.Random(seed) if seed is not None else random

    # 灵感时刻的触发概率: 5-20% (基于场景进度)
    trigger_prob = 0.05 + 0.15 * math.sin(current_progress * math.pi)

    if rng.random() > trigger_prob:
        return None

    # 随机选择灵感时刻类型
    moment_type = rng.choice(list(INSPIRATION_MOMENTS.keys()))
    moment_content = rng.choice(INSPIRATION_MOMENTS[moment_type])

    return {
        "type": moment_type,
        "content": moment_content,
        "trigger_prob": round(trigger_prob, 2),
        "context": f"在 scene_progress={current_progress:.2f} 时触发",
    }


# ============================================================
# 6.5 INSPIRATION_DB - 8 大导演真实灵感时刻数据库 (Phase 17.7)
# ============================================================
# 32 个真实电影中的具体灵感时刻 - 替代凭空编写的灵感时刻
# 让节点输出"像活着的导演在思考", 而不是"规则集在套用"
INSPIRATION_DB = [
    # ===== 王家卫 Wong Kar-wai (5) =====
    {"导演": "王家卫", "别名": ["WKW", "Wong Kar-wai", "王家卫 (Wong Kar-wai)"],
     "作品": "《花样年华》", "场景": "0:32:15 走廊擦肩",
     "情感核心": "loneliness + longing", "镜头技术": "慢镜头 60fps + 浅景深 + 主观 + 老歌同步",
     "技术原因": "慢动作让时间有重量,观众跟着角色停顿", "灵魂维度": "D3 艺术表达 0.97, D4 镜头 0.95",
     "Prompt 片段": "慢动作让时间成为主角,60fps 让观众的呼吸跟着角色停顿,走廊的长镜头让孤独与思念同步累积"},
    {"导演": "王家卫", "别名": ["WKW", "Wong Kar-wai", "王家卫 (Wong Kar-wai)"],
     "作品": "《重庆森林》", "场景": "0:18:00 凤梨罐头独白",
     "情感核心": "loneliness", "镜头技术": "特写 + 主观独白 + 倒计时",
     "技术原因": "把过期的爱具象化为过期的罐头,物件代替心理", "灵魂维度": "D2 想象力 0.97, D3 艺术表达 0.95",
     "Prompt 片段": "让物件代替心理——凤梨罐头的保质期就是爱情的保质期"},
    {"导演": "王家卫", "别名": ["WKW", "Wong Kar-wai", "王家卫 (Wong Kar-wai)"],
     "作品": "《春光乍泄》", "场景": "1:42:30 伊瓜苏瀑布缺席",
     "情感核心": "warm_regret + lucid_despair", "镜头技术": "彩色黑白切换 + 主观 + 大全景",
     "技术原因": "缺席的瀑布 = 缺席的恋人,在场的孤独比独处更痛", "灵魂维度": "D1 创造力 0.92, D7 灵感 0.95",
     "Prompt 片段": "让重要的事缺席——约定一起来瀑布,只到了一个人,这种在场孤独比独处更痛"},
    {"导演": "王家卫", "别名": ["WKW", "Wong Kar-wai", "王家卫 (Wong Kar-wai)"],
     "作品": "《一代宗师》", "场景": "1:25:00 火车站月台",
     "情感核心": "tenderness + remorse", "镜头技术": "蒸汽 + 长焦压缩 + 慢动作 + 老歌",
     "技术原因": "蒸汽模糊视线=模糊未来,长焦压缩空间=拉近心理距离", "灵魂维度": "D3 艺术表达 0.98",
     "Prompt 片段": "蒸汽是天然的留白——看得见身形,看不见脸,听得见声音,记不住具体话"},
    {"导演": "王家卫", "别名": ["WKW", "Wong Kar-wai", "王家卫 (Wong Kar-wai)"],
     "作品": "《堕落天使》", "场景": "0:48:00 深夜火锅",
     "情感核心": "loneliness + bittersweet", "镜头技术": "9.8mm 鱼眼 + 手持 + 强对比",
     "技术原因": "鱼眼扭曲世界=杀手内心扭曲但被热腾腾火锅软化", "灵魂维度": "D1 创造力 0.95, D8 叛逆 0.85",
     "Prompt 片段": "9.8mm 鱼眼不是炫技——是世界观的变形,杀手眼中的世界应该是扭曲的"},
    # ===== 诺兰 Christopher Nolan (5) =====
    {"导演": "诺兰", "别名": ["NOLAN", "Christopher Nolan", "诺兰", "Nolan"],
     "作品": "《盗梦空间》", "场景": "0:35:00 巴黎咖啡馆爆破",
     "情感核心": "fear + awe", "镜头技术": "6 个月实拍 + 旋转走廊 + IMAX + 弦乐",
     "技术原因": "真实爆破制造物理感,布料烟水无法伪造", "灵魂维度": "D1 创造力 0.98, D4 镜头 0.97",
     "Prompt 片段": "6 个月实拍一个 30 秒镜头,这是诺兰对真实感的偏执,CG 永远做不出布料着火时的物理细节"},
    {"导演": "诺兰", "别名": ["NOLAN", "Christopher Nolan", "诺兰", "Nolan"],
     "作品": "《记忆碎片》", "场景": "全片 黑白彩色交叉",
     "情感核心": "tension + loneliness", "镜头技术": "极简剪辑 + 时间反推 + 物件特写",
     "技术原因": "颜色当时间标记,观众自己拼图,共情主角", "灵魂维度": "D1 创造力 0.97, D2 想象力 0.96",
     "Prompt 片段": "不用旁白解释——让颜色和剪辑顺序本身成为叙事,观众是拼图者,不是被喂答案的"},
    {"导演": "诺兰", "别名": ["NOLAN", "Christopher Nolan", "诺兰", "Nolan"],
     "作品": "《黑暗骑士》", "场景": "0:51:00 小丑递笔",
     "情感核心": "fear + awed_fear", "镜头技术": "极特写 + 慢升格 + 留白",
     "技术原因": "升格让日常动作变成命运传递,观众屏息", "灵魂维度": "D3 艺术表达 0.95, D7 灵感",
     "Prompt 片段": "把日常动作(递笔)用升格拍成命运的交接,动作没变,时间感变了"},
    {"导演": "诺兰", "别名": ["NOLAN", "Christopher Nolan", "诺兰", "Nolan"],
     "作品": "《星际穿越》", "场景": "2:42:00 书架后的手",
     "情感核心": "hopeless_hope", "镜头技术": "微观尺度 + 时间叠加 + 沉默 30 秒",
     "技术原因": "没有对白,用触碰的物理动作表达父女无法触碰的痛", "灵魂维度": "D2 想象力 0.99",
     "Prompt 片段": "五维空间不是炫技——是父女之间永远错过的时间的视觉化"},
    {"导演": "诺兰", "别名": ["NOLAN", "Christopher Nolan", "诺兰", "Nolan"],
     "作品": "《信条》", "场景": "1:15:00 子弹倒回",
     "情感核心": "awe + tension", "镜头技术": "实拍倒放 + 物理引擎同步 + IMAX",
     "技术原因": "真实倒拍比 CGI 更信,布料烟水细节无法伪造", "灵魂维度": "D1 创造力 0.96, D4 镜头 0.98",
     "Prompt 片段": "诺兰的真实感偏执:观众能感觉到时间的物理重量,即使剧情违反物理"},
    # ===== 奉俊昊 Bong Joon-ho (3) =====
    {"导演": "奉俊昊", "别名": ["Bong Joon-ho", "奉俊昊"],
     "作品": "《寄生虫》", "场景": "1:47:00 暴雨倒流楼梯",
     "情感核心": "fear + despair", "镜头技术": "升降 + 慢动作 + 大雨 + 红蓝灯",
     "技术原因": "升降让下降成为上升的反面,阶层坠落,镜头是审判视角", "灵魂维度": "D1 创造力 0.97",
     "Prompt 片段": "暴雨倒流楼梯=阶层倒流的视觉化,每个人的方向不同但水流同向"},
    {"导演": "奉俊昊", "别名": ["Bong Joon-ho", "奉俊昊"],
     "作品": "《母亲》", "场景": "1:35:00 巴士顶端的舞",
     "情感核心": "tenderness + despair", "镜头技术": "远景 + 静止 + 突然音乐",
     "技术原因": "静止让母亲的舞成为全社会之上的母亲,远景让个体=全体", "灵魂维度": "D3 艺术表达 0.96",
     "Prompt 片段": "静止=永恒,远景=全民,巴上舞=母爱的视觉化"},
    {"导演": "奉俊昊", "别名": ["Bong Joon-ho", "奉俊昊"],
     "作品": "《雪国列车》", "场景": "全片 车厢推进",
     "情感核心": "tension", "镜头技术": "单一方向运镜 + 越前越暗 + 工业感",
     "技术原因": "用车厢作为社会隐喻,不可逆的方向感", "灵魂维度": "D2 想象力 0.95",
     "Prompt 片段": "用空间隐喻社会,镜头方向=阶层方向,光=资源"},
    # ===== 黑泽明 (3) =====
    {"导演": "黑泽明", "别名": ["Akira Kurosawa", "黑泽明"],
     "作品": "《七武士》", "场景": "1:55:00 雨中决战",
     "情感核心": "fury + awed_fear", "镜头技术": "三镜头同步 + 群戏调度 + 雨声",
     "技术原因": "三镜头=三视角,共情每个武士的勇气", "灵魂维度": "D6 场面调度 0.99",
     "Prompt 片段": "群戏的最高境界:每一个武士的死,都是单独的悲剧,雨是共同的见证"},
    {"导演": "黑泽明", "别名": ["Akira Kurosawa", "黑泽明"],
     "作品": "《罗生门》", "场景": "全片 雨",
     "情感核心": "disgust + loneliness", "镜头技术": "雨作为真相难辨的视觉化",
     "技术原因": "雨洗不掉谎言,罗生门下的雨=真相无法被证实的隐喻", "灵魂维度": "D2 想象力 0.98",
     "Prompt 片段": "用天气作为哲学命题的视觉化——雨是真相的试金石,洗不掉,却让它更脏"},
    {"导演": "黑泽明", "别名": ["Akira Kurosawa", "黑泽明"],
     "作品": "《乱》", "场景": "1:40:00 城堡废墟",
     "情感核心": "lucid_despair + perfect_regret", "镜头技术": "远景 + 静止 + 烧色滤镜",
     "技术原因": "烧色把金色辉煌变成血色废墟,一个家族=人类历史", "灵魂维度": "D3 艺术表达 0.99",
     "Prompt 片段": "调色即哲学——同一个城堡,黄=王朝,红=废墟,让色彩说话"},
    # ===== 是枝裕和 (3) =====
    {"导演": "是枝裕和", "别名": ["Hirokazu Kore-eda", "是枝裕和", "Koreeda"],
     "作品": "《步履不停》", "场景": "0:25:00 长子忌日",
     "情感核心": "warm_regret + tenderness", "镜头技术": "日常节奏 + 饭桌长镜 + 母亲做菜特写",
     "技术原因": "长镜头让饭桌无言成为千言万语,母亲做菜=一生的爱", "灵魂维度": "D3 艺术表达 0.97",
     "Prompt 片段": "饭桌长镜=家庭伦理,做菜的母亲=一生的爱,没有一句话但所有情绪都在"},
    {"导演": "是枝裕和", "别名": ["Hirokazu Kore-eda", "是枝裕和", "Koreeda"],
     "作品": "《小偷家族》", "场景": "1:38:00 海边烟花",
     "情感核心": "tenderness + bittersweet_pain", "镜头技术": "听不到烟花声,只有海浪 + 6 个家人的脸",
     "技术原因": "听不到=看不到=他们的家也是想象中的", "灵魂维度": "D3 艺术表达 0.98",
     "Prompt 片段": "重要的东西可以缺席——烟花升空但我们听不到,家人在但我们看不见,想象=真实"},
    {"导演": "是枝裕和", "别名": ["Hirokazu Kore-eda", "是枝裕和", "Koreeda"],
     "作品": "《无人知晓》", "场景": "全片 4 个孩子",
     "情感核心": "loneliness + hope", "镜头技术": "孩子视角 + 长时间固定",
     "技术原因": "用孩子的身高拍世界=世界的巨大=儿童的脆弱", "灵魂维度": "D3 艺术表达 0.96",
     "Prompt 片段": "用身高拍世界——孩子眼里的世界是巨大的,世界越大,孩子越小"},
    # ===== 塔可夫斯基 (3) =====
    {"导演": "塔可夫斯基", "别名": ["Andrei Tarkovsky", "塔可夫斯基", "Tarkovsky"],
     "作品": "《乡愁》", "场景": "1:50:00 烛光",
     "情感核心": "lucid_despair + hope", "镜头技术": "长镜头 8 分钟 + 固定 + 烛光",
     "技术原因": "8 分钟的缓慢=信仰的重量,烛光的微颤=人的希望", "灵魂维度": "D5 氛围 0.99",
     "Prompt 片段": "塔可夫斯基的长镜头:不是时间慢,是你必须为这一刻停下来"},
    {"导演": "塔可夫斯基", "别名": ["Andrei Tarkovsky", "塔可夫斯基", "Tarkovsky"],
     "作品": "《镜子》", "场景": "全片 黑白彩色切换",
     "情感核心": "nostalgia + loneliness", "镜头技术": "颜色作为时间标记",
     "技术原因": "记忆的颜色是褪色的(黑白),现在的颜色是浓烈的(彩色)", "灵魂维度": "D2 想象力 0.98",
     "Prompt 片段": "颜色=时间——记忆没有颜色,现实才有,让观众看见时间的颜色"},
    {"导演": "塔可夫斯基", "别名": ["Andrei Tarkovsky", "塔可夫斯基", "Tarkovsky"],
     "作品": "《潜行者》", "场景": "0:40:00 三人进入区",
     "情感核心": "tension + awe", "镜头技术": "雨 + 湿镜头 + 长镜",
     "技术原因": "区=心灵的未知,长镜=探索的缓慢", "灵魂维度": "D5 氛围 0.99",
     "Prompt 片段": "未知需要慢——每走一步都是恐惧,慢镜头让恐惧有节奏"},
    # ===== 侯孝贤 (3) =====
    {"导演": "侯孝贤", "别名": ["Hou Hsiao-hsien", "侯孝贤"],
     "作品": "《刺客聂隐娘》", "场景": "0:55:00 山中静坐",
     "情感核心": "ji + yuan", "镜头技术": "远景固定 + 自然光 + 蝉鸣",
     "技术原因": "山中静坐=内心世界,大远景=心胸宽广,不动=思考", "灵魂维度": "D5 氛围 0.98",
     "Prompt 片段": "中式意境——画面要有气,远景的山要有势,静坐的人要有定,三者合一"},
    {"导演": "侯孝贤", "别名": ["Hou Hsiao-hsien", "侯孝贤"],
     "作品": "《悲情城市》", "场景": "0:15:00 林家客厅",
     "情感核心": "chou + loneliness", "镜头技术": "固定中景 + 听不清的对白",
     "技术原因": "固定镜头让时代压下来,对白听不清=时代的嘈杂", "灵魂维度": "D5 氛围 0.97",
     "Prompt 片段": "时代压在画面上——固定镜头让历史有重量,听不清的对白让时代有距离"},
    {"导演": "侯孝贤", "别名": ["Hou Hsiao-hsien", "侯孝贤"],
     "作品": "《海上花》", "场景": "全片 室内长镜",
     "情感核心": "tenderness + bittersweet_pain", "镜头技术": "摄影机在室内自由移动",
     "技术原因": "长镜=时光,在花楼的时光是凝固的", "灵魂维度": "D4 镜头 0.96",
     "Prompt 片段": "长镜在室内是流动的诗——摄影机的轨迹=情感的轨迹,每个角落=每个人的命运"},
    # ===== 大卫·芬奇 (3) =====
    {"导演": "大卫·芬奇", "别名": ["David Fincher", "大卫·芬奇", "大衛·芬奇"],
     "作品": "《七宗罪》", "场景": "1:55:00 what's in the box",
     "情感核心": "awe + fear + revulsion", "镜头技术": "快速正反打 + 弱光 + 蓝绿色调",
     "技术原因": "弱光=真相被遮蔽,蓝绿=死亡与抑郁", "灵魂维度": "D5 氛围 0.98",
     "Prompt 片段": "用光影表达看不见的恶——弱光=真相,蓝绿=心理疾病"},
    {"导演": "大卫·芬奇", "别名": ["David Fincher", "大卫·芬奇", "大衛·芬奇"],
     "作品": "《搏击俱乐部》", "场景": "0:35:00 肥皂",
     "情感核心": "disgust + awe", "镜头技术": "特写 + 静态 + 慢镜",
     "技术原因": "偷来的脂肪=偷来的人生,肥皂=净化=自我救赎", "灵魂维度": "D2 想象力 0.97",
     "Prompt 片段": "用物件隐喻心理——脂肪/肥皂/自我,偷来=反叛,净化=救赎"},
    {"导演": "大卫·芬奇", "别名": ["David Fincher", "大卫·芬奇", "大衛·芬奇"],
     "作品": "《社交网络》", "场景": "0:18:00 赛艇",
     "情感核心": "loneliness + frustration", "镜头技术": "手持 + 4K 锐利 + 快剪",
     "技术原因": "4K 锐利=哈佛的残酷,手持=扎克伯格的不安", "灵魂维度": "D4 镜头 0.96",
     "Prompt 片段": "4K 是清晰度即残酷——观众看见毛孔,世界没有滤镜,手持有在场感"},
]


def get_inspiration_moments(fused_emotion, director, count=3):
    """
    Phase 17.7: 根据灵魂融合结果和导演, 匹配真实灵感时刻
    让输出"像活着的导演在思考", 而不是"规则集在套用"

    Args:
        fused_emotion: fuse_emotions() 返回值 (含 name/emotions/intensity/polarity/arousal)
        director: 导演风格字符串 (如 "王家卫" / "诺兰")
        count: 返回灵感时刻数量

    Returns:
        灵感时刻列表 [{导演, 作品, 场景, 情感核心, 镜头技术, Prompt 片段}, ...]
    """
    if not fused_emotion:
        return []

    primary = (fused_emotion.get("name", "") or "").lower()
    primary_zh = fused_emotion.get("name", "")  # 中文名

    # 情感匹配关键词
    emo_keywords = [
        "loneliness", "fear", "warm_regret", "tension", "lucid_despair",
        "tenderness", "disgust", "remorse", "awe", "longing", "nostalgia",
        "ji", "yuan", "chou", "awed_fear", "bittersweet", "perfect_regret",
        "hopeless_hope", "frustration", "revulsion", "fury",
    ]

    matches = []
    seen_keys = set()  # 避免重复
    for im in INSPIRATION_DB:
        # 导演匹配 (别名/子串)
        dir_match = False
        aliases = im.get("别名", []) + [im["导演"]]
        for alias in aliases:
            if alias and (alias in director or director in alias):
                dir_match = True
                break
        if not dir_match:
            continue

        # 情感匹配
        emo_match = False
        im_emo = im.get("情感核心", "").lower()
        for k in emo_keywords:
            if k in im_emo or k in primary:
                emo_match = True
                break

        if emo_match:
            key = (im["导演"], im["作品"], im["场景"])
            if key not in seen_keys:
                seen_keys.add(key)
                matches.append(im)

    # 按导演优先 + 情感匹配度排序
    return matches[:count]


def format_inspiration_moments(moments):
    """
    Phase 17.7: 把灵感时刻列表格式化为 prompt 字符串
    """
    if not moments:
        return ""

    lines = ["\n【灵感时刻参考 - 真实电影中的具体镜头 (Phase 17.7)】"]
    for i, im in enumerate(moments, 1):
        lines.append(
            "\n  " + str(i) + ". " + im["导演"] + " - " + im["作品"] + " - " + im["场景"] + "\n"
            "     情感核心: " + im["情感核心"] + "\n"
            "     镜头技术: " + im["镜头技术"] + "\n"
            "     Prompt 片段: " + im["Prompt 片段"]
        )
    return "\n".join(lines) + "\n"


# 兼容引用
_HAS_EMOTION_DATA = True


# ============================================================
# 7. DirectorSoulNode - ComfyUI 节点
# ============================================================
def _extract_5d_specifics(scene: str, director: str = "") -> dict:
    """
    Phase 35.6 5 维具体化智能解析
    从场景描述提取: 时代 / 地点 / 品牌 / 数字 / 物件
    每维 1-3 个具体词,兜底默认
    严禁模板化
    """
    if not scene:
        scene = ""
    import re as _re5d
    result = {
        "era": [],      # 时代
        "location": [], # 地点
        "brand": [],    # 品牌
        "numbers": [],  # 数字
        "objects": [],  # 物件
        "raw_5d_summary": "",
    }
    # 时代
    era_patterns = [
        (r"(19[789]\d|20[012]\d)\s*年", "year_4digit"),
        (r"(90|80|70|60) 年代", "decade_zh"),
        (r"清末|民国|建国|文革|改革开放|千禧|911|非典|新冠", "era_event"),
    ]
    for pat, _ in era_patterns:
        matches = _re5d.findall(pat, scene)
        for m in matches[:2]:
            result["era"].append(str(m))

    # 地点
    loc_patterns = [
        (r"[\u4e00-\u9fff]{2,4}(市|区|县|镇|村|街|路|弄|巷|胡同)", "loc_zh"),
        (r"(哈尔滨|北京|上海|广州|深圳|成都|重庆|西安|武汉|南京|杭州|苏州|天津|香港|澳门|台北)", "city_zh"),
        (r"(美国|英国|法国|德国|意大利|西班牙|俄罗斯|日本|韩国|印度|巴黎|伦敦|纽约|东京|首尔|柏林|罗马|莫斯科)", "country_zh"),
    ]
    for pat, _ in loc_patterns:
        matches = _re5d.findall(pat, scene)
        for m in matches[:2]:
            m_str = str(m).strip()
            if m_str and m_str not in result["location"]:
                result["location"].append(m_str)

    # 品牌
    brand_patterns = [
        (r"(雪花|青岛|燕京|百威|喜力|茅台|五粮液|剑南春)", "beer_liquor_zh"),
        (r"(奔驰|宝马|奥迪|丰田|本田|大众|桑塔纳|红旗|比亚迪|特斯拉)", "car_zh"),
        (r"(Apple|iPhone|Samsung|Huawei|小米|华为|诺基亚|摩托罗拉)", "phone_zh"),
        (r"(Chanel|Dior|Hermes|Gucci|Prada|LV|Montblanc|Parker|万宝龙|派克)", "luxury_zh"),
    ]
    for pat, _ in brand_patterns:
        matches = _re5d.findall(pat, scene)
        for m in matches[:2]:
            m_str = str(m).strip()
            if m_str and m_str not in result["brand"]:
                result["brand"].append(m_str)

    # 数字 (年代/日期/价格/数量)
    num_patterns_with_format = [
        (r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", "{0}年{1}月{2}日"),
        (r"(?<!\d)(\d{1,2})\s*月\s*(\d{1,2})\s*日(?!\d)", "{0}月{1}日"),
        (r"(?<!\d)(\d+)\s*([元块毛刀分公斤米厘])", "{0}{1}"),
        (r"(?<!\d)(\d+)\s*(秒|分|小时)", "{0}{1}"),
    ]
    for pat, fmt in num_patterns_with_format:
        matches = _re5d.findall(pat, scene)
        for m in matches[:3]:
            if isinstance(m, tuple):
                parts = [str(x).strip() for x in m if x]
                try:
                    m_str = fmt.format(*parts)
                except (IndexError, KeyError):
                    m_str = "".join(parts)
            else:
                m_str = str(m).strip()
            if m_str and m_str not in result["numbers"]:
                result["numbers"].append(m_str)

    # 物件 (高频物件词)
    obj_keywords = [
        "钢笔", "圆珠笔", "铅笔", "毛笔", "打字机", "键盘", "鼠标",
        "烟", "打火机", "烟灰缸", "酒杯", "咖啡杯", "茶壶", "茶杯", "暖瓶",
        "信", "信纸", "信封", "明信片", "邮票", "便签",
        "相框", "相册", "照片", "画", "镜子", "钟表", "挂历", "日历",
        "钥匙", "锁", "门", "门牌", "窗", "窗帘", "窗台",
        "沙发", "椅子", "桌子", "床", "柜子", "书架", "地毯",
        "收音机", "电视", "磁带", "CD", "黑胶", "耳机", "大哥大", "BP机", "寻呼机",
        "戒指", "项链", "手表", "耳环", "手镯",
    ]
    for kw in obj_keywords:
        if kw in scene and len(result["objects"]) < 4:
            result["objects"].append(kw)

    # 兜底: 任何 1 维为空,用导演时代风格默认
    director_default = {
        "王家卫": {"era": ["1966"], "location": ["香港"], "brand": ["Montblanc"], "numbers": ["2046"], "objects": ["凤梨罐头"]},
        "诺兰": {"era": ["2014"], "location": ["巴黎"], "brand": ["奔驰"], "numbers": ["3"], "objects": ["陀螺"]},
        "PTA": {"era": ["1972"], "location": ["洛杉矶"], "brand": ["Chevrolet"], "numbers": ["70"], "objects": ["摄影机"]},
        "奉俊昊": {"era": ["2019"], "location": ["首尔"], "brand": ["现代"], "numbers": ["半地下"], "objects": ["手机"]},
        "毕赣": {"era": ["2018"], "location": ["凯里"], "brand": ["VCD"], "numbers": ["42 分钟"], "objects": ["手电筒"]},
    }
    default = director_default.get(director, director_default["王家卫"])
    for k in ["era", "location", "brand", "numbers", "objects"]:
        if not result[k]:
            result[k] = default.get(k, [])[:1]

    # 5 维摘要
    result["raw_5d_summary"] = " | ".join([
        f"时代:{','.join(result['era'])}",
        f"地点:{','.join(result['location'])}",
        f"品牌:{','.join(result['brand'])}",
        f"数字:{','.join(result['numbers'])}",
        f"物件:{','.join(result['objects'])}",
    ])
    return result


def _build_soul_addons(
    fused: dict,
    director: str,
    director_sig: str,
    soul_dims: dict,
    soul_state: dict,
    scene: str,
    story_intensity: float,
    scene_progress: float,
) -> str:
    """
    生成 14 个下游节点 addon 段 (Phase 35 真正实施)
    每段基于灵魂 kwargs 动态生成具体可操作指令
    下游节点 parse 自己的 addon 段彻底匹配

    14 段对应 14 个 Production 节点:
    EDITING / PERFORMANCE / SILENCE / COLOR / WORLDBUILDING / THEME / ART / SPATIAL
    SOUND / MUSIC / INTENT / STORYBOARD / CHARACTER / QA
    """
    # === Phase 35.5: 35 导演 + 100 场景 lookup ===
    # 导演档案 (35 位, 含具体风格/技法/反 AI 警告)
    director_profile = {}
    if _WEB_DB_LOADED:
        director_profile = _WEB_DIRECTOR_PROFILES.get(director, {})

    # 场景 lookup (100 场景数据库)
    matched_scene = None
    if _WEB_DB_LOADED and scene:
        scene_lower = scene.lower() if isinstance(scene, str) else ""
        # 优先按关键词匹配
        for s in _WEB_SCENE_DATABASE:
            sname = s.get("name", "")
            if sname and sname in scene:
                matched_scene = s
                break
        # 没匹配上用第一个作为默认
        if not matched_scene and _WEB_SCENE_DATABASE:
            matched_scene = _WEB_SCENE_DATABASE[0]

    # 5 维具体化 (Phase 35.6)
    specs5d = _extract_5d_specifics(scene, director)

    emo_name = fused.get("name", "孤独")
    emo_intensity = fused.get("intensity", 0.5)
    emo_polarity = fused.get("polarity", "neutral")
    emo_arousal = fused.get("arousal", "medium")
    visual = fused.get("visual_signs", "")[:200]
    voice = fused.get("voice_signs", "")[:150]
    inner = fused.get("inner_monologue", "")[:150]
    palette = fused.get("color_palette", "")[:120]
    music_t = fused.get("music_tempo", "")[:120]
    facial = fused.get("facial_au", "")[:120]
    desc = fused.get("description", "")[:200]
    examples = fused.get("director_examples", "")[:150]

    creative = soul_dims.get("creativity", 0.85)
    imagination = soul_dims.get("imagination", 0.85)
    artistic = soul_dims.get("artistic_expression", 0.85)
    camera = soul_dims.get("camera_skill", 0.85)
    atmosphere = soul_dims.get("atmosphere_control", 0.85)

    inspiration = soul_state.get("inspiration", 0.85)
    fatigue = soul_state.get("fatigue", 0.30)
    doubt = soul_state.get("doubt", 0.50)
    rebellious = soul_state.get("rebelliousness", 0.70)

    # 导演标志性 8 维 (Phase 35.5: 35 导演, 用 director_data_unified 统一中枢 + 默认 10 兜底)
    try:
        from director_data_unified import DIRECTOR_PROFILES_ALL as _UNIFIED_PROFILES
        director_8d = {}
        for name, prof in _UNIFIED_PROFILES.items():
            director_8d[name] = {
                "镜头": prof.get("镜头", "未指定"),
                "光线": prof.get("光", "未指定"),
                "节奏": prof.get("节奏", "未指定"),
                "声音": prof.get("声音", "未指定"),
                "色彩": prof.get("色彩", "未指定"),
                "构图": prof.get("构图", "未指定"),
                "表演": prof.get("表演", "未指定"),
                "剪辑": prof.get("节奏", "未指定"),
            }
    except Exception:
        director_8d = {
            "王家卫": {"镜头": "抽帧+慢镜头 1/8+手持微晃", "光线": "霓虹+暖黄路灯+雨夜反光", "节奏": "60s 慢节奏+重复 2 次+时间戳", "声音": "环境音>台词+粤语+探戈", "色彩": "蓝绿+暗红+琥珀+过曝", "构图": "走廊+镜子+门缝+雨刷", "表演": "极简手势+不解释+眼神漂移", "剪辑": "跳切+闪回+定格 3 秒"},
            "诺兰": {"镜头": "IMAX+长焦+客观视角", "光线": "自然光为主+冷色+高对比", "节奏": "递进+倒计时+交叉剪辑", "声音": "Hans Zimmer 低频+心跳+钟表", "色彩": "冷蓝+灰+暖黄关键色", "构图": "对称+地标+大远景", "表演": "克制+坚毅+眼神锁定", "剪辑": "非线性+双线交叉+悬疑"},
            "PTA": {"镜头": "长焦 85mm+浅景深+慢推", "光线": "70s 暖黄+窗光+烟雾", "节奏": "慢板+渐进+长时间呼吸", "声音": "环境音>台词+时代金曲", "色彩": "琥珀+橘红+暖黄+棕", "构图": "中景+双人+封闭空间", "表演": "可观察行为+不解释+身体语言", "剪辑": "长镜头+不切+渐入渐出"},
            "奉俊昊": {"镜头": "固定机位+对称+精确调度", "光线": "冷暖对比+身份隐喻光", "节奏": "类型节奏+突然变调+反转", "声音": "现实音+精准爆点+类型音乐", "色彩": "冷暖阶层对比+垂直调度", "构图": "楼梯+门+窗+身份位置", "表演": "群戏+同场多情绪+隐忍", "剪辑": "精确切点+突然静默+反差"},
            "黑泽明": {"镜头": "群戏+天气+远景+史诗", "光线": "天气即角色+极致清晰+云层", "节奏": "群戏调度+多线交叉+缓慢推进", "声音": "风+雨+鼓+号角", "色彩": "黑白色调为主+强烈对比", "构图": "三镜头法+群像+动作剪影", "表演": "极致克制+武士道+命运感", "剪辑": "动态切+叠化+慢推"},
            "库斯杜力卡": {"镜头": "手提+近景+面部特写", "光线": "巴洛克暖光+油画感+反差", "节奏": "不规则+突然静默+长呼吸", "声音": "小提琴+手风琴+寂静", "色彩": "油画金+深红+赭石+琥珀", "构图": "脸部特写+粗粝+动物+酒", "表演": "酒鬼+夸张+悲喜剧+自毁", "剪辑": "突然跳切+超现实+动画插入"},
            "塔可夫斯基": {"镜头": "超长镜头+固定+微移", "光线": "水+火+烛+自然光+潮湿", "节奏": "慢+呼吸+水滴+诗", "声音": "水滴+风+钟+呼吸+钢琴", "色彩": "湿+雾+褐色+蓝灰+光柱", "构图": "风景+水+火+肖像+门", "表演": "极少台词+眼神+空间+时间", "剪辑": "超长+不切+时间流逝"},
            "伯格曼": {"镜头": "脸特写+正反打+中景", "光线": "斯堪的纳维亚冷光+阴影", "节奏": "戏剧化+对白+独白+静默", "声音": "沉默>台词+脚步+呼吸", "色彩": "黑白+灰+冷色+偶尔暖色", "构图": "脸部+镜子+门+空椅", "表演": "内心戏+自我对话+心理剧", "剪辑": "静态切+反打+静默"},
            "李安": {"镜头": "饭桌+家庭+东西方", "光线": "家庭暖光+自然窗光+冷暖对比", "节奏": "家庭代际+饭桌+缓慢推进", "声音": "家庭对话+沉默+文化冲突", "色彩": "东方青+西方暖+冷暖对比", "构图": "饭桌+对坐+代际错位", "表演": "压抑+爆发+东西方", "剪辑": "家庭戏+饭桌+仪式感"},
            "约阿希姆·提尔": {"镜头": "固定+长镜头+房子视角", "光线": "北欧光+低角度+窗光", "节奏": "慢+生活流+家庭代际", "声音": "环境音+家+童年+沉默", "色彩": "北欧白+米+灰+淡蓝+暖", "构图": "家+门+窗+楼梯+童年空间", "表演": "克制+不解释+童年+父母", "剪辑": "长镜头+家庭+代际+闪回"},
        }
    # 联网数据库 35 导演兜底 (覆盖默认)
    if _WEB_DB_LOADED and director not in director_8d and director in _WEB_DIRECTOR_PROFILES:
        profile = _WEB_DIRECTOR_PROFILES[director]
        techniques = profile.get("techniques", [])
        # 用 techniques 推断 8 维
        tech_text = " | ".join(techniques) if techniques else "无具体技法"
        director_8d[director] = {
            "镜头": techniques[0] if techniques else "未指定",
            "光线": techniques[1] if len(techniques) > 1 else "未指定",
            "节奏": techniques[2] if len(techniques) > 2 else "未指定",
            "声音": techniques[3] if len(techniques) > 3 else "未指定",
            "色彩": techniques[4] if len(techniques) > 4 else "未指定",
            "构图": tech_text[:50],
            "表演": profile.get("core_style", "未指定")[:50],
            "剪辑": tech_text[50:100] if len(tech_text) > 50 else "未指定",
        }

    d8d = director_8d.get(director, director_8d["王家卫"])

    # 14 段生成
    out = "\n\n" + "═" * 40 + "\n【14 个下游节点 addon 段 — 灵魂注入分发】\n" + "═" * 40 + "\n"

    # 2. PERFORMANCE_ADDON (用 100 场景数据库)
    out += f"""
===EDITING_ADDON===
供 EditingPro 解析 (剪辑节奏)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name} (强度 {emo_intensity:.2f}, {emo_polarity}, {emo_arousal})
- 导演剪辑: {d8d['节奏']} ({director} 标志性)
- 切点策略_{director}: 每镜头长度随情感强度变化, 强度 < 0.4 用长镜头 (8-15s), 强度 0.4-0.7 用中切 (3-6s), 强度 > 0.7 用快切 (1-2s) 或跳切
- 关键节点: 故事强度 {story_intensity:.2f} 决定 4 段剪辑曲线, 场景进度 {scene_progress:.2f} 决定留白比例
- 长镜头: 在 {emo_name} 极致时刻用 1 个 12-30s 固定机位长镜头, 由 {director} 的{d8d['节奏']} 决定
- 跳切_{director}: {rebellious:.2f} 叛逆指数决定跳切频率, > 0.7 用抽帧跳切, < 0.4 用叠化, {director} 偏好{d8d['剪辑']}
- 反 AI: 不许用模板化的"快速剪辑营造紧张感", 要根据 {director} 的 {emo_name} 情感曲线定制
- 导演签名: {director_sig}
===END_EDITING_ADDON===
"""

    # 2. PERFORMANCE_ADDON
    # 12 AU 动态扩展 (基于 emo_intensity + 情感类别的真实 FACS 组合, 严禁硬编码)
    if emo_intensity > 0.7:
        # 高强度情感: 12 AU 全开
        au_set = f"AU1(额肌)+AU2(眉外侧)+AU4(皱眉)+AU5(上睑)+AU6(颧大肌/真笑)+AU7(眼睑紧)+AU9(鼻翼提)+AU12(嘴角上扬)+AU15(嘴角下)+AU17(颏肌)+AU20(嘴角外拉)+AU26(下颌下垂)"
        body_count = "5+3+2+1=11"
    elif emo_intensity > 0.4:
        # 中强度: 6-8 个核心 AU
        if "Joy" in emo_name or "Trust" in emo_name:
            au_set = f"AU1+AU2+AU6+AU12 ({emo_name} 核心组, 含真笑) + AU7(眼睑紧)"
            body_count = "3+2+1+1=7"
        elif "Fear" in emo_name or "Surprise" in emo_name:
            au_set = f"AU1+AU2+AU5+AU26 ({emo_name} 眼/嘴组) + AU4(皱眉)"
            body_count = "2+2+2+1=7"
        elif "Sadness" in emo_name:
            au_set = f"AU1+AU4+AU15 ({emo_name} 悲伤三件套) + AU17+AU7"
            body_count = "2+2+1+1=6"
        elif "Anger" in emo_name or "Disgust" in emo_name:
            au_set = f"AU4+AU5+AU7+AU17 ({emo_name} 紧绷组) + AU9+AU23"
            body_count = "3+2+1+1=7"
        else:
            au_set = f"AU1+AU2+AU12 ({emo_name} 期待组) + AU5+AU7"
            body_count = "2+2+2+1=7"
    else:
        # 低强度: 3-4 个微妙 AU
        if "Joy" in emo_name:
            au_set = f"AU12 ({emo_name} 微上扬) + AU6 弱化"
        elif "Sadness" in emo_name or "Fear" in emo_name:
            au_set = f"AU4 ({emo_name} 轻皱眉) + AU1 微沉"
        else:
            au_set = f"AU1+AU2 ({emo_name} 抬眉) + AU4 弱化"
        body_count = "1+1+1+0=3"

    # 微动作 + 身体词随情感强度变化
    if emo_intensity > 0.7:
        micro_actions = f"5 拍手/抓握/拍桌 + 3 急/喘/屏息 + 2 视线扫视/盯 + 1 后仰/前倾"
        body_words_required = f"≥8 身体词 (含摔/推/扯/砸/颤/缩 + 喘/吼/哑 + 瞪/扫/盯/移 + 抖/硬/僵)"
    elif emo_intensity > 0.4:
        micro_actions = f"3 握/翻/触 + 2 浅/匀/长呼 + 1 看/扫 + 1 微倾/靠"
        body_words_required = f"≥5 身体词 (含手部动作 + 呼吸节奏 + 视线变化)"
    else:
        micro_actions = f"1 轻触/微动 + 1 慢呼/吸 + 1 视线漂移 + 0 无姿态变化"
        body_words_required = f"≥3 身体词 (含微手势 + 呼吸 + 视线)"

    # 反 AI 例随导演变化
    director_anti_ai = {
        "王家卫": "不要'眼神坚定', 要'她用拇指在杯沿反复摩挲, 频率 0.6Hz, 持续 8 秒, 不看对方'",
        "诺兰": "不要'眼里闪烁决心', 要'他停下咀嚼 1.2 秒, 然后用舌尖推上颚, 像在吞咽什么'",
        "PTA": "不要'表情复杂', 要'她左手无名指轻微抽动 3 次, 间隔 0.4 秒, 右手完全不动'",
        "奉俊昊": "不要'尴尬地笑', 要'父亲耳朵微红 0.3cm, 但眼神仍看别处, 嘴咬住下唇 1 秒'",
        "黑泽明": "不要'愤怒地握拳', 要'他手指从剑柄上慢慢松 1.5 秒, 然后退后半步, 不说话'",
        "塔可夫斯基": "不要'陷入回忆', 要'她的手停在水面, 水滴从指尖落, 间隔 0.8 秒, 共 3 次'",
        "伯格曼": "不要'沉默表达痛苦', 要'她嘴唇微张 0.5 秒, 像要说什么, 但只有呼吸声 1.2 秒'",
        "库斯杜力卡": "不要'醉醺醺地笑', 要'他拿起酒杯又放下, 共 3 次, 每次间隔 4 秒'",
        "李安": "不要'含蓄地表达', 要'她把筷子放下, 但手没离开, 等 3 秒对方说话才完全松开'",
        "约阿希姆·提尔": "不要'若有所思', 要'她在窗边看 14 秒, 第 8 秒时手指在玻璃上画半圆, 收回'",
    }
    anti_ai_text = director_anti_ai.get(director, director_anti_ai["王家卫"])

    out += f"""
===PERFORMANCE_ADDON===
供 PerformanceDirectionPro 解析 (表演指导)
- 主导情感: {emo_name} (强度 {emo_intensity:.2f})
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 面部肌肉 (FACS) - 动态情感组: {facial}
- 身体语言: {visual}
- 声音/台词: {voice}
- 内心独白: {inner}
- 导演表演风格: {d8d['表演']}
- 12 AU 组合 (动态基于 {emo_name} 强度 {emo_intensity:.2f}): {au_set}
- 微动作总和 (情感强度驱动): {micro_actions}
- 身体词丰富度: {body_words_required}
- 反 AI 例 ({director} 风格): {anti_ai_text}
- 场景特定表演指令: 在 {scene[:30] if scene else '当前场景'} 环境中, 表演应呼应环境 (例: 雨夜厨房 → 雨刷节奏 1Hz 影响呼吸)
===END_PERFORMANCE_ADDON===
"""

    # 3. SILENCE_ADDON
    out += f"""
===SILENCE_ADDON===
供 SilenceMasteryPro 解析 (沉默/留白)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 留白比例: 场景进度 {scene_progress:.2f} 决定, 结尾阶段 (progress > 0.8) 留白 60%, 中段 30%, 开头 10%
- 沉默类型: 4 选 1 (物理沉默/情绪沉默/戏剧沉默/电影沉默)
- 物理沉默: 环境音消失, 只有呼吸/钟表/水滴
- 情绪沉默: 角色不回应, 视线漂移, 不离开场景
- 戏剧沉默: 关键台词前的 3-5 秒留白, 制造张力
- 电影沉默: 黑场 + 字幕 + 极简声音
- 导演留白: {d8d['节奏']} + 导演签名 {director_sig}
- 3 留白法则: 时间留白 (4-8s) + 空间留白 (空镜头) + 叙事留白 (信息差)
- 反 AI: 不许"陷入沉默"等空话, 要具体"她把咖啡杯放在桌上, 杯底与木桌接触声 0.3 秒, 然后 8 秒无对白"
===END_SILENCE_ADDON===
"""

    # 4. COLOR_ADDON
    out += f"""
===COLOR_ADDON===
供 ColorGradingPro 解析 (调色)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 色彩倾向: {palette}
- 调色板: {director} 风格 = {d8d['色彩']}
- 对比度: 强度 {emo_intensity:.2f} → 低强度 (0.3) 走低对比+柔光, 中强度 (0.5) 中对比, 高强度 (0.8) 高对比+硬光
- 色温: {emo_polarity} 极性 → 负极性偏冷 (-200K ~ -500K), 正极性偏暖 (+200K ~ +500K)
- LUT 风格: 选自 {director} 标志性调色 (例: 王家卫 = 蓝绿琥珀+过曝, 诺兰 = 冷蓝+高对比)
- 调色禁忌: 不用纯黑阴影, 至少 10% 蓝灰细节, 高光不爆
- 反 AI: 不许"温暖色调", 要"色温 4200K, 饱和度 -15, 蓝绿阴影, 琥珀高光, 暗角 -0.3"
===END_COLOR_ADDON===
"""

    # 5. WORLDBUILDING_ADDON (用 100 场景数据库 + 5 维具体化)
    scene_atmos = matched_scene.get("atmosphere", "")[:100] if matched_scene else ""
    scene_details = matched_scene.get("details", []) if matched_scene else []
    scene_ref = matched_scene.get("reference", "")[:50] if matched_scene else ""
    scene_name = matched_scene.get("name", "")[:30] if matched_scene else "未匹配"
    details_text = " + ".join(scene_details[:3]) if scene_details else "无具体细节"
    out += f"""
===WORLDBUILDING_ADDON===
供 WorldBuildingPro 解析 (世界设定)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 时代: 故事强度 {story_intensity:.2f} 决定, 高强度用动荡时代 (战乱/剧变), 低强度用日常时代
- 地点: {scene[:80] if scene else '未指定'}
- 100 场景库匹配: {scene_name} (参考: {scene_ref})
- 场景氛围 (联网): {scene_atmos}
- 场景细节 (联网): {details_text}
- 物理细节: 5 维度 (时代/地点/品牌/数字/物件), 每维度至少 2 个具体细节
- 5 维具体化 (智能解析): {specs5d['raw_5d_summary']}
- 时代命中: {','.join(specs5d['era'])}
- 地点命中: {','.join(specs5d['location'])}
- 品牌命中: {','.join(specs5d['brand'])}
- 数字命中: {','.join(specs5d['numbers'])}
- 物件命中: {','.join(specs5d['objects'])}
- 导演世界观: {director} = {director_sig}
- 空间隐喻: {d8d['构图']} 体现导演空间哲学
- 反 AI: 不许"90 年代小镇", 要"1998 年哈尔滨道里区, 雪花啤酒玻璃瓶, 桑塔纳 2000 黑色, 大哥大, 11 月 7 日已供暖"
===END_WORLDBUILDING_ADDON===
"""

    # 6. THEME_ADDON
    out += f"""
===THEME_ADDON===
供 ThemePhilosophyPro 解析 (主题哲学)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 主题深度: 灵魂维度 艺术表达 {artistic:.2f} 决定, > 0.9 哲学深度, 0.7-0.9 心理学深度, 0.5-0.7 社会学深度
- 核心命题: 从 {director} 标志性主题提取 (例: 王家卫 = 时间/记忆/错过的爱情, 诺兰 = 时间/自由/牺牲)
- 潜文本: 1 句不能明说的潜台词, 例子: "他/她不再回头不是因为不想, 是因为回头就回不去了"
- 哲学对照: 借鉴 1 个真实哲学概念 (例: 柏格森时间/海德格尔存在/老子无为)
- 主题层次: 表面冲突 (人物目标) + 深层冲突 (内心) + 哲学冲突 (存在)
- 反 AI: 不许"探讨人生意义", 要"用老子'逝者如斯夫'对照男主角时间焦虑, 用 5 个具体意象 (钟表/日历/落叶/雪/河流) 落实"
===END_THEME_ADDON===
"""

    # 7. ART_ADDON
    out += f"""
===ART_ADDON===
供 ArtDirectionPro 解析 (美术指导)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 导演美术: {d8d['构图']} + {d8d['色彩']}
- 场景陈设: 至少 3 个时代特定物件, 2 个隐喻物件, 1 个"破旧"物件 (有故事的旧物)
- 光线设计: {d8d['光线']}
- 美术色调: {palette}
- 时代质感: 1998 年质感 = 桑塔纳 + 雪花啤酒 + 老式挂历 + 搪瓷杯 + 棕色皮质沙发
- 美术隐喻: 每个物件都承载主题 (例: 挂历 = 时间流逝, 搪瓷杯 = 父辈记忆)
- 反 AI: 不许"90 年代风格", 要"1998 年哈尔滨典型家装: 棕色皮质沙发 (有 3 处裂痕) + 牡丹牌电视 + 雪花啤酒玻璃瓶 (瓶身有水珠) + 老式挂历 (停在 11 月) + 搪瓷杯 (杯底发黄)"
===END_ART_ADDON===
"""

    # 8. SPATIAL_ADDON
    out += f"""
===SPATIAL_ADDON===
供 SpatialConsistencyPro 解析 (空间一致性)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 空间布局: {d8d['构图']}
- 阶层隐喻: 奉俊昊风格, 垂直空间 (楼上楼下/楼梯/电梯) = 阶层
- 时间空间一致性: 5 维 (空间位移 + 物件位置 + 人物位置 + 光线方向 + 季节)
- 视线匹配: 角色 A 看角色 B 的方向必须前后一致 (180 度规则 / 30 度规则)
- 空间隐喻: {director} 标志性空间 (例: 王家卫 = 走廊/镜子/门缝, 诺兰 = 楼梯/旋转走廊/城市地标)
- 物件固定: 关键物件在场景内位置不变 (除非剧情需要)
- 反 AI: 不许"保持空间一致", 要"男主在窗边 (西侧), 女主在门口 (东侧), 距离 3.5 米, 中间隔茶几和暖瓶, 镜头轴线保持 180 度"
===END_SPATIAL_ADDON===
"""

    # 9. SOUND_ADDON
    out += f"""
===SOUND_ADDON===
供 SoundDesignPro 解析 (声音设计)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 主导情感: {emo_name}
- 声音策略: {d8d['声音']}
- 环境音层: 3 层 (远景/中景/近景), 例: 雨声 (远) + 时钟滴答 (中) + 咖啡呼吸 (近)
- 同期声 vs 后期: 强度 {emo_intensity:.2f} 决定, 高强度用同期声增加真实感, 低强度用后期强化情绪
- 关键声音: 至少 3 个标志性声音 (例: 王家卫 = 时钟滴答+雨声+探戈+粤语)
- 静默时刻: 静音 > 5 秒的时机选择, 在情感极值处
- 声音反 AI: 不许"环境音营造氛围", 要"33 层声音设计: 远景 (城市低频 + 远处车流) + 中景 (雨刷节奏 1Hz + 时钟滴答) + 近景 (咖啡杯触桌 0.3s + 呼吸 0.8s/次)"
===END_SOUND_ADDON===
"""

    # 10. MUSIC_ADDON
    out += f"""
===MUSIC_ADDON===
供 MusicScorePro 解析 (音乐配乐)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 音乐策略: {d8d['声音']} + {music_t}
- 配乐风格: {director} 标志性配乐 (例: 王家卫 = 探戈/爵士/粤语老歌, 诺兰 = Hans Zimmer 低频, 塔可夫斯基 = Bach/古典/极简)
- 配乐时机: 4 选 1 (先于画面 / 同时 / 后于 / 缺失), 缺失选项留给 4 段 (塔可夫斯基风格)
- 主题音: 1 个核心动机, 3-5 音符, 出现 3-5 次
- 静音: 在情感极值处停 5-10 秒, 制造"留白"
- 反 AI: 不许"钢琴配乐烘托悲伤", 要"只有 1 个钢琴单音, 出现 3 次, 每次在角色沉默时, 频率 C4 → E4 → G4"
===END_MUSIC_ADDON===
"""

    # 11. INTENT_ADDON
    out += f"""
===INTENT_ADDON===
供 DirectorIntentPro 解析 (导演意图)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 4 类意图: 情感意图 ({emo_name}) + 主题意图 ({director} 主题) + 节奏意图 ({d8d['节奏']}) + 视觉意图 ({d8d['构图']})
- 潜文本: 1 句不能明说
- 观众应感到: 1 个具体情感词 (例: "心酸", "释然", "窒息")
- 导演意图强度: 故事强度 {story_intensity:.2f}
- 灵魂状态: 灵感 {inspiration:.2f} | 怀疑 {doubt:.2f} | 叛逆 {rebellious:.2f} → 决定导演是否"反类型"
- 反 AI: 不许"让观众感动", 要"让观众在第 17 分钟, 看见父亲手抖着点烟时, 自己不自觉也摸自己的手"
===END_INTENT_ADDON===
"""

    # 12. STORYBOARD_ADDON
    out += f"""
===STORYBOARD_ADDON===
供 DirectorStoryboardPro 解析 (分镜)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 30s 6 段: 起 (0-5s) / 承 (5-10s) / 转 (10-15s) / 合 (15-20s) / 高 (20-25s) / 余 (25-30s)
- 镜头数: 6 段 = 8-12 个镜头, 平均 2.5-3.7s/镜头
- 关键镜头: 高潮段必须有 1 个 12s+ 长镜头
- 运动: {d8d['镜头']}
- 光线: {d8d['光线']}
- 构图: {d8d['构图']}
- 6 段任务: 起 (建立) / 承 (冲突) / 转 (反转) / 合 (深化) / 高 (爆发) / 余 (留白)
- 反 AI: 不许"特写表现情绪", 要"第 23 秒: 固定机位 14s, 男主背影站在窗前, 雨刷 1Hz 节奏, 突然停 1 拍, 然后加速 1.5Hz"
===END_STORYBOARD_ADDON===
"""

    # 13. CHARACTER_ADDON
    out += f"""
===CHARACTER_ADDON===
供 CharacterArcPro 解析 (角色弧光)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 主导情感: {emo_name}
- 主角情感起点: {emo_name} (强度 {emo_intensity:.2f})
- 主角情感终点: 必须变化, 强度偏移 > 0.3 或情感类别切换
- 弧光类型: 4 选 1 (正弧/负弧/平弧/循环弧)
- 正弧: 主角从缺陷到完整 (例: 孤独 → 接纳)
- 负弧: 主角从完整到缺陷 (例: 信任 → 背叛)
- 平弧: 主角坚持自我, 不改变
- 循环弧: 主角经历完整变化后又回到起点
- 5 维角色塑造: 欲望 + 恐惧 + 创伤 + 防御 + 突破
- 灵魂状态映射: 灵感 {inspiration:.2f} → 角色觉醒时刻
- 反 AI: 不许"主角成长", 要"主角在第 17 分钟放下酒杯, 手指从紧握到松开 (3 秒过程), 标志从防御到开放"
===END_CHARACTER_ADDON===
"""

    # 14. QA_ADDON
    out += f"""
===QA_ADDON===
供 QualityAssurancePro 解析 (质量QA)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name}
- 主导情感: {emo_name}
- 6 维校验: 反 AI 味 / 反机械控制 / 微表情 / 留白 / 氛围 / 叙事逻辑 / 故事线 / 情节严谨
- 反 AI 词表: 191 词, 必须 0 命中 (常用 AI 套话)
- 反机械控制: 5 个导演签名元素必须至少 3 个出现
- 微表情: 至少 8 个身体词 (手/肩/眼/呼吸/步态)
- 留白: 至少 1 个 5s+ 留白时刻
- 氛围: 至少 3 个感官细节 (视觉/听觉/触觉/嗅觉/味觉)
- 叙事逻辑: 7.5 段自检 (因果链/动机链/反转/因果词/情绪因果/时间连续/空间一致/物件因果)
- 故事线: 12 套理论至少 1 个被激活 (Save the Cat/Hero's Journey/McKee)
- 情节严谨: 5 维具体化 (时代/地点/品牌/数字/物件) 各至少 2 个
- 总分: 100 分制, 必须 > 90 才能通过
- 反 AI: 不许"画面精美, 故事感人", 要"得分 92/100, 其中反 AI 味 18/20, 叙事逻辑 14/15, 故事线 13/15, 情节严谨 14/15, 微表情 9/10, 留白 8/10, 氛围 9/10, 反机械控制 7/10"
===END_QA_ADDON===
"""

    # 15. H3_ADDON (Phase 36.2: MiniMax-H3 框架整合到 DirectorSoulNode)
    # 把 H3 5 模式 + camera 3D + Ref2VA 6 段 + 13 导演映射注入到 14 段下游
    h3_camera_phrase = ""
    if _H3_FRAMEWORK_LOADED:
        h3_camera_phrase = _h3_render_camera(director)

    out += f"""
===H3_ADDON===
供 H3ContextIRNode 解析 (MiniMax-H3 prompt framework)
- 场景锚点: {scene[:80] if scene else '未指定场景'}
- 主导情感: {emo_name} (强度 {emo_intensity:.2f}, {emo_polarity})
- H3 模式选择 (基于用户输入): T2VA / I2VA / FL2VA / L2VA / Ref2VA
  - 默认 T2VA (纯文本) - 由 H3ContextIRNode.user_intent 决定
  - 有首帧图: I2VA
  - 有首尾帧图: FL2VA
  - 有尾帧图: L2VA
  - 有完整 reference (图片+视频+音频): Ref2VA
- H3 导演镜头调度 (3D 拆解): {h3_camera_phrase if h3_camera_phrase else 'Push in with small amplitude at slow speed'}
  - 来源: {director} 标志性 8 维 → H3 camera 13 motion types × 3 amplitudes × 3 speeds
  - 真实 3 维: motion type (e.g. Truck Right) + amplitude (with small/large) + speed (at slow/fast)
- H3 visual style 7 选 1: Cinematic / live-action / 2D-animated / 3D CG / claymation / watercolor / vintage film
  - 基于 {director} 默认: Cinematic (主流), 3D CG (宫崎骏/皮克斯), live-action (王家卫/诺兰)
- H3 reference labels 4 选: <Subject N> / <Picture N> / <Video N> / <Audio N>
  - {director} 角色: <Subject 1> = 主角, <Subject 2+> = 配角/物件/环境
- H3 dialogue 格式: <d>[Language] ...</d>
  - {target_language_hint(director)} 对白格式
- H3 shot cut 5 措辞: "the camera cuts to" / "the shot cuts to" / "the shot transitions to" / "the shot changes to" / "the shot switches to"
- H3 cut timestamp: [Shot 2] At 00:03.500, the camera cuts to ... (MM:SS.mmm 严格递增)
- H3 voiceover 规则: "S1 says in an off-screen voiceover: <d>...</d> while his lips remain completely closed"
- H3 cross-cut dialogue: <scenetrans> 标记 + "continues seamlessly across the cut"
- H3 truncated: <cutoff> 标记 + "ends with the dialogue being cut off"
- H3 on-screen text: 双引号包裹, 保留原文 (例: red neon sign reading "营业中" glows above the doorway)
- H3 overall_soundscape 1-4 句: 环境音 + 物理动作音 + 非语言人声, 排除对白/歌声/剧情音乐
- H3 non_diegetic_music 1-3 句: 乐器 + 速度 + 节奏 + 动态变化, 排除抽象情绪词
- H3 Ref2VA 6 段顺序: subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music
- H3 retention markers (visible): fully_preserved / partially_preserved / attribute_transfer / weak_reference
- H3 retention markers (audio): fully_copy / partially_copy / reference / weak_reference
- H3 5 模式示例完整 Prompt 输出 (Base / I2VA / FL2VA / L2VA / Ref2VA 5 cases 全部按 H3 框架)
- H3 9 官方 SKILL 可参考: {H3_OFFICIAL_SKILLS_SUMMARY.get('h3-prompt-writing', '') if _H3_FRAMEWORK_LOADED else 'h3-prompt-writing'}
- H3 skill 工作流: project brief → story outline → character cards → scene cards → shot table → storyboard → video-model choice → single-shot clips → assembly → BGM → QC
- H3 quality 标准: 11 种语言稳定支持 (Arabic/Chinese/English/French/German/Italian/Japanese/Korean/Portuguese/Russian/Spanish)
- H3 限制: 输出 4-15s, 短边 768px, 24 FPS, 32kHz stereo
- 灵魂状态映射: 灵感 {inspiration:.2f} → 镜头流动感, 疲劳 {fatigue:.2f} → 长镜头比例, 怀疑 {doubt:.2f} → 留白比例, 叛逆 {rebellious:.2f} → 跳切频率
- 反 AI: 不许"按 H3 框架生成", 要"H3 mode = T2VA, Camera motion = Push in with small amplitude at slow speed, <d>[English] ...</d> 在 Shot 1 末, overall_soundscape 描述雨 + footsteps, non_diegetic_music = Sparse piano at slow tempo"
- 导演签名: {director_sig}
===END_H3_ADDON===
"""

    out += "\n" + "═" * 40 + "\n【14+1 addon 段结束 — 含 H3 整合】\n" + "═" * 40 + "\n"
    return out


def target_language_hint(director: str) -> str:
    """导演 → H3 对白语言提示"""
    cn_directors = ["王家卫", "张艺谋", "姜文", "侯孝贤", "杜琪峰", "陈凯歌", "贾樟柯", "蔡明亮", "毕赣", "李安", "是枝裕和", "宫崎骏", "北野武", "朴赞郁", "黑泽明", "小津安二郎"]
    if director in cn_directors:
        return "Chinese (Mandarin/Cantonese 视导演)"
    return "English (国际通用)"


class DirectorSoulNode:
    """导演灵魂节点 - 单独节点, 注入到所有其他节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 情感选择 (单情感/双情感/多情感) ===
                "主导情感": (["auto"] + list(EMOTION_MATRIX_60.keys()), {"default": "loneliness"}),
                "次要情感_1": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_2": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_3": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_4": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),

                # === 融合模式 ===
                "融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合", "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"], {"default": "auto"}),

                # === 主导情感权重 ===
                "主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 灵魂维度 ===
                "创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 灵魂状态 ===
                "灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "疲劳指数": ("FLOAT", {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05}),
                "怀疑指数": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.05}),
                "叛逆指数": ("FLOAT", {"default": 0.70, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 导演视角 (Phase 35.5: 35 导演, 联网数据库) ===
                "导演": (["王家卫", "诺兰", "PTA", "奉俊昊", "黑泽明", "库斯杜力卡", "塔可夫斯基", "伯格曼", "王家卫_1980", "约阿希姆·提尔", "李安", "王家卫+侯孝贤", "张艺谋", "姜文", "贾樟柯", "毕赣", "蔡明亮", "杜琪峰", "陈凯歌", "是枝裕和", "宫崎骏", "小津安二郎", "北野武", "朴赞郁", "阿巴斯", "安哲罗普洛斯", "贝拉·塔尔", "文德斯", "林奇", "塔伦蒂诺", "安东尼奥尼", "费里尼", "希区柯克", "库布里克", "戈达尔", "维伦纽瓦", "热内", "法哈蒂", "肯·洛奇"], {"default": "王家卫"}),

                # === 场景上下文 ===
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨", "multiline": True}),

                # === 故事强度 (影响灵魂状态) ===
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 场景进度 ===
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "soul_injection",           # 完整灵魂注入字符串 (供其他节点使用)
        "fused_emotion",            # 融合情感档案
        "emotion_dimensions",       # 情感强度 + 极性 + 唤醒度
        "soul_dimensions",          # 10 灵魂维度
        "soul_state",               # 当前灵魂状态
        "director_signature",       # 导演签名
        "scene_prompt_addon",       # 场景 prompt 增强
        "h3_alignment_addon",       # H3 三大字段增强
    )

    FUNCTION = "build_soul"
    CATEGORY = "PromptLibrary/Phase17 灵魂"

    def build_soul(self, **kwargs):
        # 1. 收集情感
        emotion_keys = []
        if kwargs.get("主导情感") and kwargs["主导情感"] != "auto":
            emotion_keys.append(kwargs["主导情感"])
        for i in range(1, 5):
            key = f"次要情感_{i}"
            val = kwargs.get(key, "none")
            if val and val != "none":
                emotion_keys.append(val)

        # 2. 收集权重
        weights = [kwargs.get("主导权重", 1.0)]
        # 剩余权重按平均分配
        if len(emotion_keys) > 1:
            remaining = 1.0 - weights[0]
            n_remaining = len(emotion_keys) - 1
            for _ in range(n_remaining):
                weights.append(remaining / n_remaining)

        # 3. 融合情感
        fused = fuse_emotions(
            emotion_keys,
            weights,
            kwargs.get("融合模式", "auto"),
        )
        if not fused:
            fused = fuse_emotions(["loneliness"], [1.0], "F1_单情感主导")

        # 4. 灵魂维度
        soul_dims = {
            "creativity": kwargs.get("创造力", 0.85),
            "imagination": kwargs.get("想象力", 0.85),
            "artistic_expression": kwargs.get("艺术表达", 0.85),
            "camera_skill": kwargs.get("镜头技巧", 0.85),
            "atmosphere_control": kwargs.get("氛围掌控", 0.85),
        }

        # 5. 灵魂状态
        soul_state = {
            "inspiration": kwargs.get("灵感指数", 0.85),
            "fatigue": kwargs.get("疲劳指数", 0.30),
            "doubt": kwargs.get("怀疑指数", 0.50),
            "rebelliousness": kwargs.get("叛逆指数", 0.70),
        }

        # 6. 导演签名
        director = kwargs.get("导演", "王家卫")
        director_signatures = {
            "王家卫": "用物件代替心理, 时间戳, 60s 慢节奏",
            "诺兰": "时间结构即主题, 史诗感, IMAX 客观",
            "PTA": "用可观察行为代替情绪, 70s 迷幻, 慢推长焦",
            "奉俊昊": "用空间做阶层隐喻, 类型当特洛伊木马, 同场多情绪",
            "黑泽明": "天气即角色, 极致清晰, 群戏调度",
            "库斯杜力卡": "少说话, 沉默即情感, 塞尔维亚乡愁",
            "塔可夫斯基": "时间即主角, 长镜头, 诗意朦胧",
            "伯格曼": "脸特写, 沉默, 心理剧",
            "王家卫_1980": "王家卫早期, 短片, 实验性",
            "约阿希姆·提尔": "从房子视角叙事, 家庭代际, 北欧光",
            "李安": "饭桌戏, 东西方文化张力, 父亲",
            "王家卫+侯孝贤": "长镜头+少台词+物件, 东方美学",
        }
        director_sig = director_signatures.get(director, "")

        # 7. 完整灵魂注入
        soul_injection = build_soul_injection(
            emotion_keys,
            weights,
            kwargs.get("融合模式", "auto"),
            director,
            kwargs.get("场景描述", ""),
            soul_dims_override=soul_dims,
        )

        # 8. 场景 prompt 增强 (供 concept_pitch / director_intent 等使用)
        scene_prompt_addon = f"""
[灵魂融合层注入]
主导情感: {fused['name']} (强度 {fused['intensity']:.2f}, 极性 {fused['polarity']})
视觉锚点: {fused['visual_signs'][:200]}
声音锚点: {fused['voice_signs'][:200]}
内心独白: {fused['inner_monologue'][:200]}
色彩倾向: {fused['color_palette'][:150]}
音乐倾向: {fused['music_tempo'][:150]}
导演签名: {director_sig}
导演灵魂: 创造 {soul_dims['creativity']:.2f} | 想象 {soul_dims['imagination']:.2f} | 艺术 {soul_dims['artistic_expression']:.2f}
灵感: {soul_state['inspiration']:.2f} | 怀疑: {soul_state['doubt']:.2f} | 叛逆: {soul_state['rebelliousness']:.2f}
[灵魂融合层结束]
"""

        # 9. H3 三大字段增强
        h3_addon = f"""
INTEGRATED_MULTIMODAL_DESCRIPTION 灵魂增强:
[Emotion Anchor] {fused['name']} ({fused['polarity']}, intensity {fused['intensity']:.2f})
[Visual] {fused['visual_signs'][:150]}
[Voice] {fused['voice_signs'][:100]}
[Color] {fused['color_palette'][:100]}

OVERALL_SOUNDSCAPE 灵魂增强:
{', '.join([fused['voice_signs'][:80], fused['music_tempo'][:80]])}

NON_DIEGETIC_MUSIC 灵魂增强:
[Music Style: {fused['music_tempo'][:120]}]
"""

        # === 14 个下游节点 addon 段 (Phase 35 真正实施,非纸面) ===
        # 每个 addon 段是具体可操作的指令,基于灵魂 kwargs 动态生成
        # 下游节点 parse 自己的 addon 段彻底匹配,不是纸面
        soul_addons = _build_soul_addons(
            fused=fused,
            director=director,
            director_sig=director_sig,
            soul_dims=soul_dims,
            soul_state=soul_state,
            scene=kwargs.get("场景描述", ""),
            story_intensity=kwargs.get("故事强度", 0.5),
            scene_progress=kwargs.get("场景进度", 0.0),
        )

        # 输出
        soul_inj_str = soul_injection + soul_addons
        fused_str = json.dumps(fused, ensure_ascii=False, indent=2)
        emotion_dims_str = f"intensity={fused['intensity']:.2f} | polarity={fused['polarity']} | arousal={fused['arousal']}"
        soul_dims_str = " | ".join([f"{k}={v:.2f}" for k, v in soul_dims.items()])
        soul_state_str = " | ".join([f"{k}={v:.2f}" for k, v in soul_state.items()])
        director_sig_str = f"导演: {director} | 签名: {director_sig}"

        return (
            soul_inj_str,
            fused_str,
            emotion_dims_str,
            soul_dims_str,
            soul_state_str,
            director_sig_str,
            scene_prompt_addon,
            h3_addon,
        )


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "DirectorSoulNode": DirectorSoulNode,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "DirectorSoulNode": "🎭 导演灵魂节点 (Phase 17 灵魂)",
# }


if __name__ == "__main__":
    # 测试情感融合
    print("=" * 60)
    print("情感矩阵测试 (60 种情感)")
    print("=" * 60)
    print(f"  情感总数: {len(EMOTION_MATRIX_60)}")
    for i, (k, v) in enumerate(EMOTION_MATRIX_60.items()):
        if i < 3:
            print(f"  - {k}: {v['name']} ({v['category']}, intensity {v['intensity']}, {v['polarity']})")

    print("\n" + "=" * 60)
    print("情感融合测试 (F1-F7)")
    print("=" * 60)
    for i, (k, v) in enumerate(EMOTION_FUSION_7.items()):
        print(f"  {k}: {v['name']} - {v['scenarios']}")

    # 测试 F3 双情感对等融合
    fused = fuse_emotions(["loneliness", "longing"], [0.5, 0.5], "F3_双情感对等融合")
    if fused:
        print(f"\n  融合结果: {fused['name']}")
        print(f"  intensity: {fused['intensity']:.2f}, polarity: {fused['polarity']}")
        print(f"  description: {fused['description'][:200]}")

    # 测试灵魂注入
    print("\n" + "=" * 60)
    print("导演灵魂注入测试")
    print("=" * 60)
    inj = build_soul_injection(
        ["loneliness", "longing"],
        [0.5, 0.5],
        "F3_双情感对等融合",
        "王家卫",
        "父女在厨房, 雨夜"
    )
    print(inj[:2000])
    print(f"\n总长度: {len(inj)} 字符")
