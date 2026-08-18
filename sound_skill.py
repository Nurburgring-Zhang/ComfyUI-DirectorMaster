# -*- coding: utf-8 -*-
"""
SoundSkill — 🔊 声音层专家 (Node 集群节点)
====================================================
来源: Higgsfield Studio 公开的 Hell Grind production brief + 自身 Phase 13 沉淀
权威: 声音是角色资产 / AUDIO 块刚性骨架 / SFX only 不生成音乐 / 跨片段连续性

Higgsfield 关键经验 (直接抄进节点):
1. 声音是角色资产 — 音域/音色/语速/口音/呼吸/压力变化 全部锁死
2. AUDIO 块架构: 声音描述符 + 逐字台词 + 身体动作 + 面部反应 (固定四段)
3. 台词固定结构: 声音+情绪 → 引号里台词 → 身体动作 → 面部反应
4. 没台词的人明确保持沉默 (写在 prompt 里: "remain silent")
5. 跨片段: 上一句尾音/呼吸/手部颤抖进新镜头 (CONTINUITY_TAIL)
6. SFX only. No music. (音乐留给后期; "生成音轨" 只会挡剪辑的路)
7. 后期不重录声音: Seedance 对口型台词直接从生成里清理, 降噪/匀音色/放进空间
8. Style Prefix 收尾: "Live-action. NON-IP. 16:9. 12s. SFX only. NO CGI. Cinematic."

Node 集群角色 (与 node cluster_*.py 互锁):
- 与 spatial_layout 同步: 剪辑点 = 声音尾巴接入点
- 与 acting_skill 同步: 表演的呼吸/颤抖是声音连续性的物理基础
- 与 spatial_layout 同步: GEO SPATIAL LAYOUT 决定 4 层声音的方位
- 与 asset_registry 同步: 角色资产 = 视觉 + 声音 双契约
- 与 iteration_post 同步: 后期声音清理是"六层生产系统"的第六层

5 要素架构 (每个函数驱动):
1. 数据 (Data): 50 美元电影 brief + 115446 次生成 + 6 层生产系统
2. 上下文缩略 (Context Brief): scene / speakers / prev_clip / emotion
3. Skill/Harness: voice registry + dialogue grammar + silence rules + continuity
4. 经验矩阵 (Experience Matrix): 6 文件系统 + 5 铁律 + Hell Grind 4 主角
5. AI 深度处理: 动态生成, 不是模板; 5 要素作为推理路径

3 个 Hell Grind 示例 (内嵌, 可直接调用 demo_*):
- 反派示例: Voice: deep, gravelly bass-baritone; slow, calculated pacing;
           London street accent; menacing calm — he never raises his voice.
- JAX 对话: 动作区不放台词, AUDIO 区只放引号里的那一句
- 走廊环境音: 走廊空气声/两组脚步声/平板轻触声/远处撞击声

设计原则 (5 条铁律 + 声音专项):
1. 资产先行 - 声音也锁, 不锁不开机
2. 每次都描述全部 - voice descriptor 逐字进 prompt, 绝不缩写
3. 一次只改一行 - 修改声音要写日志
4. 给模型更少的自由 - 声音比画面更敏感, 必须给死
5. 镜头搞不定, 就简化镜头 - 声音同样适用: 拆/删/换
"""

import os
import sys
import json
import re
import time
from typing import Dict, List, Optional, Tuple, Any

# === 5 要素注入依赖 (与 Phase 13 节点同源) ===
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import SILENCE_MASTERY_5
    from prompt_builder import (
        inject_5_elements, inject_silence_mastery_5, inject_director_intent,
        inject_director_control_11, inject_h3_rules_11, inject_genre_9_types,
    )
    _HAS_AI_DEPS = True
except Exception as _e:
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(_e)


# =============================================================================
#  全局常量 - 5 要素中的 Skill/Harness 沉淀
# =============================================================================

# 1. AUDIO 块语法 (Higgsfield 官方, 4 段刚性结构)
AUDIO_BLOCK_GRAMMAR = """AUDIO (SFX only — no music in this slot):
— VOICE DESCRIPTOR for {speaker}: {voice_descriptor}
— DIALOGUE: {emotion}, {line}
— BODY ACTION while speaking: {body_action}
— FACE REACTION after line: {face_reaction}
— SILENCE_RULE: every other character present in this shot remains silent.
  No ad-libs. No "uhm". No second line. Only the line in quotes is spoken."""

# 2. SFX only 强制项 (brief 原话, 收尾标签)
SFX_ONLY_RULE = "Live-action. NON-IP. 16:9. {duration}s. SFX only. NO CGI. Cinematic."

# 3. 4 层声音景观 (Higgsfield 的 6 层生产系统中的第四层 - 声音层细分)
SOUNDSCAPE_4_LAYERS = {
    "1_空气层 (air)": "封闭空间的固有共振; HVAC 嗡鸣; 雨敲窗; 远处的街道底噪; "
                     "在房间里不同位置听, 这一层略有差异 (corner / center / doorway)",
    "2_脚步层 (footstep)": "角色在地面上行走的具体声音; 鞋底材质 + 地面材质 + "
                          "步速 + 承重; 走廊里两组脚步要可分; 上楼要听出楼层",
    "3_环境动作层 (ambient_action)": "门开/关/锁; 平板触屏/键盘敲击; 物件拿起/放下; "
                                    "纸页翻动; 液体倒入/倒出; 衣物摩擦",
    "4_远景层 (distant)": "远处的人声碎片; 警报/警笛; 撞击/爆炸; 雷声; "
                         "直升机; 远处的车流/动物叫声; 与画面内声音形成深度感",
}

# 4. 声音连续性 (CONTINUITY_TAIL) 模板
CONTINUITY_TAIL_CATEGORIES = {
    "1_尾音进新镜": "上一句最后一个音节的余韵, 跨剪辑点继续延伸 0.5-1.5 秒",
    "2_呼吸进新镜": "上一镜的呼吸节律, 在新镜头第一秒仍可听见; 切点呼吸不归零",
    "3_手部颤抖进新镜": "上一镜里手部动作的尾势, 新镜接住 (手中物轻微晃动/手指末梢抖动)",
    "4_环境延音进新镜": "环境音的尾巴 (尾音/混响/衰减), 在新镜里保持同一空间感",
    "5_情绪余韵进新镜": "上一镜的沉重情绪, 在新镜头由沉默 + 微表情承接, 不立刻归零",
}

# 5. 沉默 6 类 (从 silence_mastery_pro 复用, 配 4 步公式)
SILENCE_6_MOMENTS = {
    "1_对白前停顿": "角色开口前, 停 2-5 秒, 让观众等他说话, 制造期待",
    "2_对白间沉默": "两个对白之间, 停 3-10 秒, 让观众消化上一句, 准备下一句",
    "3_动作后停顿": "重要动作后 (打/吻/摔/抱), 停 5-30 秒, 让观众感受动作的重量",
    "4_眼神对视": "两人对视, 停 5-20 秒, 不说话, 让眼睛说一切",
    "5_空镜/留白": "场景之间, 用空镜 (10-30 秒), 让观众感受时间流逝/空间转换",
    "6_完全沉默": "整场戏不说话, 只有动作, 高级写法 (蔡明亮/王家卫)",
}

SILENCE_4_STEP_FORMULA = """沉默剧本 4 步公式 (声音层):
1. 角色 A 说一句话 (5-10 字) → AUDIO 块只放这一句
   ↓ 停 2-5 秒 (对白前停顿)
2. 出现一个细微的表情变化 (面部肌肉工作, 不出声)
   ↓ 停 3-10 秒 (对白间沉默)
3. 某个动作改变关系 (走近/远离/转身/拿起/放下) → 物件声进 AUDIO
   ↓ 停 5-15 秒 (动作后停顿)
4. 给观众一点反应时间 (沉默 + 远景音 + 空气)
   ↓ 继续下一场戏 (CONTINUITY_TAIL 接住)"""

# 6. 压力下声音变化 (5 种, 来自 ACTING skill 的"压力轴")
PRESSURE_VOICE_CHANGES = {
    "calm_baseline": "基线声音, 稳定呼吸, 节奏均匀, 音量中等",
    "pressure_rise": "压力下, 语速加快 10-20%, 音高上升半音, 句末上扬",
    "pressure_drop": "压力下, 音量下降 30%, 语速变慢, 句子更短, 尾音被吞掉",
    "pressure_break": "临界点, 声带紧绷, 偶尔破音, 喘息可闻, 句子被打断",
    "pressure_aftermath": "崩溃后, 声音空洞, 气息长, 句与句之间停顿 2-3 倍",
}

# 7. AUDIO 块反 AI 规则 (Higgsfield 原文 + Phase 14 沉淀)
AUDIO_ANTI_AI_RULES = [
    "动作区不写台词 - 台词只在 AUDIO 块, 写在引号里, 全场戏就这一句",
    "不要 'uhm' / 'uh' / 'ah' / 'er' 之类的填充音 - 写在 prompt 里 = 模型一定加",
    "没台词的人明确写 'remains silent, no ad-libs' - 默认模型会让人抢话",
    "身体动作里不要 'laughs bitterly' / 'sighs deeply' - 这是声音, 放 AUDIO 块",
    "面部反应只写肌肉, 不写情绪词 - 'corner of mouth twitches' 优于 'he smiles sadly'",
    "voice descriptor 一旦锁定, 逐字粘贴 - 缩写一次, 模型就开始漂",
    "压力变化用肌肉物理 (jaw set / breath held / swallow visible), 不写 'gets angry'",
    "跨镜头台词尾巴要写进新镜第一秒, 否则接缝会假",
    "SFX 写具体物, 不写情绪: 'plastic tray on metal' 优于 'sound of food'",
    "远景音必须有时间/距离锚: 'a siren two blocks away, 8 seconds ago and fading'",
]

# 8. Hell Grind 4 主角 + 1 反派的预置声音档案 (从 brief 反推)
HELL_GRIND_VOICE_PRESETS = {
    "ROCO": {
        "range": "low tenor, sits around D2-G3",
        "timbre": "husky, slightly hoarse from training; breath always audible at phrase ends",
        "speed": "slow to medium, pauses 0.5-1.2s between phrases; never rushes",
        "accent": "London East End, soft consonants, swallows the 'h'",
        "breath": "audible inhale before any line longer than 4 words; chest breath",
        "pressure": "under pressure: pitch drops half-step, pace slows further, "
                    "jaw sets and releases twice before speaking",
        "descriptor": "low husky tenor, slow deliberate pace, London East End accent, "
                     "audible chest breath, dry and grounded — he never raises his voice to shout",
    },
    "JAX": {
        "range": "bright tenor, A3-E4",
        "timbre": "youthful, clear, with a smile in the voice even when serious",
        "speed": "fast, 25% quicker than ROCO; sentence fragments; rarely finishes",
        "accent": "London cockney, glottal stops on 't' endings",
        "breath": "shallow, quick, often caught mid-word; out of breath from running",
        "pressure": "under pressure: pitch rises, speed doubles, words pile up; "
                    "voice cracks at emotional peaks",
        "descriptor": "bright youthful tenor, fast and restless pace, London cockney "
                     "glottal stops, shallow breath, defensive edge — smiles when scared",
    },
    "REIN": {
        "range": "alto, F3-D5",
        "timbre": "cool, dry, almost flat affect; words are precise, no warmth added",
        "speed": "measured, even, every word has equal weight; pauses for effect",
        "accent": "neutral London, RP-leaning but not posh; consonants clipped",
        "breath": "quiet, controlled, breath is heard only between paragraphs",
        "pressure": "under pressure: speed stays the same, but the jaw tightens, "
                    "vowel sounds shorten, words get clipped shorter",
        "descriptor": "cool precise alto, measured even pace, neutral RP-leaning London, "
                     "controlled breath, clinical — she controls the room by not reacting",
    },
    "LULU": {
        "range": "mezzo-soprano, G3-C5",
        "timbre": "warm, slightly breathy, edges of vibrato in sustained vowels",
        "speed": "medium, follows the listener, mirrors their pace then slows",
        "accent": "London mixed, soft, occasional estuary glide on 'a' vowels",
        "breath": "long, audible exhale before hard truths; sighs when words fail",
        "pressure": "under pressure: voice wavers, breath shortens, words trail off, "
                    "long silences replace sentences",
        "descriptor": "warm breathy mezzo, medium pace, soft London mixed accent, "
                     "long audible sighs, fragile — she carries her feelings in the breath",
    },
    "ANTAGONIST": {
        "range": "bass-baritone, A1-E3",
        "timbre": "deep, gravelly, with a permanent low rumble under the speech",
        "speed": "slow, calculated, every word placed; never rushed",
        "accent": "London street, hardened, glottal on emphasis",
        "breath": "deep, slow, breath heard but never gasping; controlled menace",
        "pressure": "under pressure: voice gets quieter, not louder; pauses stretch; "
                    "the lower the pressure seems, the more dangerous he is",
        "descriptor": "deep, gravelly bass-baritone; slow, calculated pacing; "
                     "London street accent; menacing calm — he never raises his voice",
    },
}

# 9. AUDIO 块选词白名单 (避免歧义, 给模型精确锚点)
AUDIO_BLOCK_VOCAB = {
    "breath_sounds": [
        "audible inhale", "caught breath", "held breath", "long exhale",
        "sharp intake", "soft sigh", "controlled nasal breath", "gasping",
        "breath hitch", "shallow rapid breath", "deep chest breath",
    ],
    "voice_textures": [
        "husky", "gravelly", "breathy", "raspy", "clear", "thin", "thick",
        "metallic", "hollow", "warm", "cold", "flat", "round", "nasal",
        "throaty", "strained", "relaxed", "tense", "creaky", "smooth",
    ],
    "foley_objects": [
        "plastic tray on metal table", "leather shoe on concrete", "rubber sole on wet tile",
        "tablet screen tap (glass on glass)", "fingers on paper", "lighter flick",
        "metal key in lock", "door hinge (slow, oiled)", "soda can crack open",
        "phone buzz on wood", "zipper pull", "fabric rustle (cotton)",
        "glass set down (soft, no slam)", "knife on cutting board (dull)",
        "umbrella open (spring + fabric)", "match strike + ignite",
    ],
    "distant_sounds": [
        "siren two blocks away, 8 seconds ago and fading",
        "helicopter overhead, distant but present for 3 seconds",
        "distant car crash, glass and crumple, 1 second after the line",
        "thunder 4 seconds after the lightning",
        "crowd murmur in a stadium far off",
        "train horn, 1 long, 1 short, 6 seconds out",
        "dog bark, single, then silence",
        "elevator ding 3 floors down",
    ],
}

# 10. 后期处理参数 (从 brief 原文反推, 给后期环节的接口)
POST_PROCESS_PIPELINE = {
    "1_降噪": "FFT-based noise reduction; -18dB gate; preserve breath frequencies "
              "(< 200Hz chest, 200-500Hz mouth); remove 50/60Hz hum + 8kHz hiss",
    "2_匀音色": "spectral match reference voice print (formant alignment 80-3000Hz); "
                "preserve natural sibilance, de-ess only above 6kHz",
    "3_空间化": "convolution reverb with location IR (training room: 1.8s decay, "
               "concrete walls); pan to GEO SPATIAL LAYOUT; -3dB per doubling of distance",
    "4_对话清晰度": "center dialogue channel; -6dB side env; broadcast LUFS -16; "
                   "true peak below -1.5dBTP",
    "5_连续环境底噪": "shared room tone: 8 seconds of base ambience, looped across all "
                    "clips in the same location; crossfade 200ms at every edit point",
    "6_音乐后叠": "music layered LAST on top of the unified SFX bed; "
                "never re-record dialogue; only ADR if Seedance's take is unrecoverable",
}


# =============================================================================
#  内部状态 - 声音注册表 (进程内, 可被 ComfyUI 节点调度)
# =============================================================================

class VoiceRegistry:
    """
    角色声音档案注册表 - 声音也是角色资产 (Higgsfield 第一原则)
    -------------------------------------------------------------
    每个角色的声音一旦注册, 后续每个 prompt 都从这张表里逐字粘贴。
    不缩写, 不漂移, 不二次发明。
    """

    def __init__(self):
        self._registry: Dict[str, Dict[str, str]] = {}
        self._history: List[Dict[str, Any]] = []  # 注册/修改日志
        self._load_presets()

    def _load_presets(self):
        """加载 Hell Grind 4 主角 + 反派 预置"""
        for name, voice in HELL_GRIND_VOICE_PRESETS.items():
            self._registry[name] = voice

    def register(self, name: str, voice_range: str, timbre: str, speed: str,
                 accent: str, breath: str, pressure: str,
                 descriptor: Optional[str] = None) -> Dict[str, str]:
        """
        注册一个角色的声音档案 - 5 要素驱动:
        1. 数据: 6 维声音特征 (音域/音色/语速/口音/呼吸/压力)
        2. 上下文缩略: 角色名作为 key
        3. Skill/Harness: 6 维字段固定结构
        4. 经验矩阵: descriptor 字段直接喂给 prompt
        5. AI 深度处理: 自动从 6 维推导出可用的 descriptor, 不写也能用
        """
        # 5 要素: AI 深度处理 - 若没给 descriptor, 自动从 6 维组装
        if not descriptor:
            descriptor = (
                f"{voice_range}; {timbre}; {speed}; {accent}; {breath}; "
                f"under pressure: {pressure}"
            )

        record = {
            "range": voice_range,
            "timbre": timbre,
            "speed": speed,
            "accent": accent,
            "breath": breath,
            "pressure": pressure,
            "descriptor": descriptor,
            "registered_at": time.time(),
        }
        self._registry[name] = record
        self._history.append({
            "action": "register",
            "name": name,
            "ts": time.time(),
            "snapshot": dict(record),
        })
        return record

    def get(self, name: str) -> Optional[Dict[str, str]]:
        return self._registry.get(name)

    def descriptor(self, name: str) -> str:
        """5 要素: 经验矩阵 - 直接给出可粘贴的 descriptor"""
        v = self._registry.get(name)
        if not v:
            return f"[VOICE UNREGISTERED: {name}]"
        return v["descriptor"]

    def list_names(self) -> List[str]:
        return list(self._registry.keys())

    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def pressure_variant(self, name: str, pressure_level: str) -> str:
        """5 要素: AI 深度处理 - 在压力下, 声音如何变 (5 种)"""
        v = self._registry.get(name)
        if not v:
            return ""
        base = v["descriptor"]
        variant = PRESSURE_VOICE_CHANGES.get(pressure_level, "")
        if not variant:
            return base
        return f"{base} | pressure level '{pressure_level}': {variant}"


# 全局单例 (ComfyUI 节点之间共享)
VOICE_REGISTRY = VoiceRegistry()


# =============================================================================
#  5 要素: 数据 + 上下文缩略 工具
# =============================================================================

HELL_GRIND_DATA_SUMMARY = (
    "Higgsfield Hell Grind 95分钟AI电影: 50万美元预算 / 15人团队 / 14天集中生成期 / "
    "115,446次生成 / 95:06成片 / 2026戛纳市场展映 / WSJ+Variety+BBC 报道 / "
    "工具栈: Seedance 2.0 + Soul Cinema + Nano Banana Pro + Seedream 4.5 + GPT Image 2 / "
    "附件: CINEDANCE skill (writer/auditor/workbench) + ACTING skill + LIRA skill / "
    "6层生产系统: 资产/空间/表演/声音/迭代/后期 / 5条铁律 / 11阶段管线"
)

HELL_GRIND_SKILL_HARNESS = (
    "AUDIO块4段刚性结构 (voice+emotion→quoted line→body action→face reaction) / "
    "声音注册表 (音域/音色/语速/口音/呼吸/压力) 6维 / "
    "沉默6类 + 4步公式 / "
    "4层声音景观 (空气/脚步/环境动作/远景) / "
    "CONTINUITY_TAIL 5类 (尾音/呼吸/颤抖/环境延音/情绪余韵) / "
    "SFX only 强制项 (no music in AUDIO) / "
    "压力下5种声音变化 / "
    "后期6步声音处理 (降噪/匀音色/空间化/对话清晰度/连续环境底噪/音乐后叠)"
)

HELL_GRIND_EXPERIENCE_MATRIX = (
    "声音是角色资产 (与视觉资产并列) / "
    "没台词的人明确保持沉默 (写在prompt) / "
    "跨镜头接缝: 上一句尾音/呼吸/颤抖 进新镜第一秒 / "
    "反AI规则10条 (no 'uhm' / 动作区不写台词 / 面部只写肌肉不写情绪) / "
    "后期不重录声音 - Seedance对口型台词直接清理 / "
    "音乐留在后期, 不在生成音轨里 / "
    "Pressure axis: 同一descriptor在calm/pressure_rise/pressure_drop/pressure_break/"
    "pressure_aftermath之间切换, voice print不变"
)


def _make_5_elements_block(scene_context: Dict[str, Any],
                           prev_clip_summary: str = "") -> str:
    """
    5 要素统一注入器 - 每个声音层函数都先过这一关
    5 要素:
    1. 数据: 数据集 + brief 原话
    2. 上下文缩略: scene/speakers/emotion/prev_clip
    3. Skill/Harness: 本节点的能力清单
    4. 经验矩阵: 直接可抄的实战经验
    5. AI 深度处理: 怎么用 5 要素动态推理
    """
    scene = scene_context.get("scene", "")
    speakers = scene_context.get("speakers", [])
    emotion = scene_context.get("emotion", "neutral, grounded")
    director = scene_context.get("director", "Higgsfield / Hell Grind reference")

    data_summary = HELL_GRIND_DATA_SUMMARY
    context_brief = (
        f"scene={scene[:60]}; speakers={','.join(speakers) if speakers else 'n/a'}; "
        f"emotion={emotion}; director={director}; "
        f"prev_clip={prev_clip_summary[:60] if prev_clip_summary else 'none (opening)'}"
    )
    skill_harness = HELL_GRIND_SKILL_HARNESS
    experience_matrix = HELL_GRIND_EXPERIENCE_MATRIX
    ai_deep = (
        "5 要素作为推理路径: 数据定锚 (Hell Grind 是经过 115K 次生成验证的成片系统) → "
        "上下文缩略确认本镜头参数 (谁说/对谁说/什么情绪) → "
        "Skill/Harness 锁定 4 段 AUDIO 块语法和声音注册表 → "
        "经验矩阵套用 5 条铁律 + 沉默 4 步公式 + CONTINUITY_TAIL 5 类 → "
        "AI 深度处理: 不是模板拼接, 是把场景的具体人/事/情代入, 5 要素一起推理"
    )

    if _HAS_AI_DEPS:
        try:
            return inject_5_elements(
                data_summary, context_brief, skill_harness,
                experience_matrix, ai_deep,
            )
        except Exception:
            pass

    # 退化路径: 手工拼
    return (
        "【5 要素 - 声音层】\n"
        f"  数据: {data_summary}\n"
        f"  上下文: {context_brief}\n"
        f"  Harness: {skill_harness}\n"
        f"  经验: {experience_matrix}\n"
        f"  AI 深度: {ai_deep}\n"
    )


# =============================================================================
#  核心 10 函数
# =============================================================================

def register_voice(name: str, voice_range: str, timbre: str, speed: str,
                   accent: str, breath: str, pressure: str,
                   descriptor: Optional[str] = None) -> Dict[str, str]:
    """
    函数 1: register_voice
    -------------------------------------------------------------
    目的: 注册一个角色的声音档案到全局 VOICE_REGISTRY。

    5 要素驱动:
    - 数据: 6 维声音特征 (音域/音色/语速/口音/呼吸/压力)
    - 上下文: 角色名作为 key, 在 prompt 里逐字粘贴
    - Harness: 注册后所有 prompt 调用 descriptor() 拿到粘贴文本
    - 经验: Hell Grind 4 主角 + 反派预置, 可直接覆盖
    - AI 深度: 不传 descriptor 也行, 自动从 6 维组装

    参数:
        name:       角色名 (e.g. "ROCO", "JAX", "反派")
        voice_range: 音域 (e.g. "low tenor, D2-G3")
        timbre:     音色 (e.g. "husky, slightly hoarse")
        speed:      语速 (e.g. "slow to medium, pauses 0.5-1.2s")
        accent:     口音 (e.g. "London East End, soft consonants")
        breath:     呼吸特征 (e.g. "audible chest breath before long lines")
        pressure:   压力下变化 (e.g. "pitch drops, pace slows")
        descriptor: 完整描述符 (可选; 不传则自动组装)

    返回:
        注册的档案 dict, 含 6 维 + descriptor + registered_at

    示例:
        register_voice(
            "ROCO", "low tenor, D2-G3", "husky, breathy",
            "slow to medium", "London East End",
            "audible chest breath", "pitch drops, jaw sets"
        )
    """
    return VOICE_REGISTRY.register(
        name, voice_range, timbre, speed, accent, breath, pressure, descriptor
    )


def get_voice_descriptor(name: str) -> str:
    """
    函数 2: get_voice_descriptor
    -------------------------------------------------------------
    目的: 取一个角色的完整 descriptor, 直接粘贴进 AUDIO 块。

    5 要素驱动:
    - 数据: 注册表里的 descriptor 字段
    - 上下文: 不带场景信息, 只带角色身份
    - Harness: 一旦注册, descriptor 是唯一真相源
    - 经验: Higgsfield 原话 - "descriptor 逐字进每个 prompt, 绝不缩写"
    - AI 深度: 若角色未注册, 返回带 [UNREGISTERED] 标记, 强制先注册

    参数:
        name: 角色名

    返回:
        完整 voice descriptor 字符串, 直接可用

    示例:
        get_voice_descriptor("ROCO")
        # -> "low husky tenor, slow deliberate pace, London East End accent,
        #     audible chest breath, dry and grounded — he never raises his voice to shout"
    """
    return VOICE_REGISTRY.descriptor(name)


def build_dialogue_block(speaker: str, emotion: str, line: str,
                         body_action: str, face_reaction: str) -> str:
    """
    函数 3: build_dialogue_block
    -------------------------------------------------------------
    目的: 按 Higgsfield 4 段刚性结构, 组装一个 AUDIO 块。

    5 要素驱动:
    - 数据: AUDIO_BLOCK_GRAMMAR 4 段结构
    - 上下文: 谁说 / 什么情绪 / 引号里的台词 / 身体动作 / 面部反应
    - Harness: 动作区不放台词 (反 AI 规则 1)
    - 经验: 没台词的人明确保持沉默 (本块自带 SILENCE_RULE 段)
    - AI 深度: 面部反应要写肌肉不写情绪 (反 AI 规则 5)

    参数:
        speaker:       说话者 (e.g. "JAX") - 必须在注册表里
        emotion:       情绪 (e.g. "angry", "tired"; 但不直接用, 改写为动作)
        line:          引号里的台词 (e.g. "把门打开。")
        body_action:   说话时的身体动作 (e.g. "his right hand rises to the door")
        face_reaction: 面部反应 (e.g. "the corner of his mouth twitches once")

    返回:
        完整的 AUDIO 块字符串, 可直接粘贴到 prompt

    示例:
        build_dialogue_block(
            "JAX", "defensive", "I'm not afraid of you.",
            "his right hand stays on the door handle, knuckles whitening",
            "his jaw sets once, releases, then his eyes narrow half a second"
        )
    """
    # 5 要素: 数据 - 自动从注册表取 voice descriptor
    voice_descriptor = get_voice_descriptor(speaker)
    if voice_descriptor.startswith("[VOICE UNREGISTERED"):
        # 5 要素: AI 深度 - 未注册时, 用占位但仍能渲染, 提醒注册
        voice_descriptor = (
            f"[UNREGISTERED - please call register_voice('{speaker}', ...)] "
            f"emotion: {emotion}"
        )

    # 5 要素: 经验矩阵 - 反 AI 规则 5, 面部反应里把情绪词过滤
    # (若用户传了 "he smiles sadly" 这种, 提示但不强制改)
    face_cleaned = face_reaction
    if _HAS_AI_DEPS:
        try:
            face_cleaned = clean_anti_ai_text(face_reaction)
        except Exception:
            pass

    # 5 要素: AI 深度 - body action 不能含台词, 验一遍
    if any(token in body_action.lower() for token in [
        '"', '“', '”', ':', 'says', 'speaks', 'whispers', 'shouts'
    ]):
        # 触发反 AI 规则 1, 警告但不阻断 (留给人)
        body_cleaned = "[WARNING: body action contains dialogue cues] " + body_action
    else:
        body_cleaned = body_action

    # 4 段刚性结构
    block = AUDIO_BLOCK_GRAMMAR.format(
        speaker=speaker,
        voice_descriptor=voice_descriptor,
        emotion=emotion,
        line=line,
        body_action=body_cleaned,
        face_reaction=face_cleaned,
    )
    return block


def enforce_silence(silent_characters: List[str]) -> str:
    """
    函数 4: enforce_silence
    -------------------------------------------------------------
    目的: 当一群人在场, 只有部分人有台词, 把没台词的人明确写为沉默。

    5 要素驱动:
    - 数据: Higgsfield 原文 "没台词的人明确保持沉默"
    - 上下文: 在场角色名单
    - Harness: SILENCE_RULE 段在 AUDIO 块里强制声明
    - 经验: 反 AI 规则 3 - 模型默认会让人抢话/加 "uhm", 必须写死
    - AI 深度: 沉默不写 = 模型随机加声; 沉默写具体 = 模型守住

    参数:
        silent_characters: 没有台词的角色名列表 (e.g. ["REIN", "LULU"])

    返回:
        SILENCE_RULE 块, 可追加到任意 AUDIO 块下方

    示例:
        enforce_silence(["REIN", "LULU"])
        # -> "SILENCE_RULE: REIN, LULU remain silent. No ad-libs. No 'uhm'.
        #     No second line. Only JAX's quoted line is spoken.
        #     REIN: jaw tight, eyes stay on JAX, no sound.
        #     LULU: hand stays on the tablet, breath held, no sound."
    """
    if not silent_characters:
        return "SILENCE_RULE: (no other characters in this shot)"

    # 5 要素: AI 深度 - 给每个沉默角色一个具体身体指令, 不只是 "remains silent"
    # 沉默也要有身体工作, 才有"活人感"
    silent_lines = []
    for ch in silent_characters:
        # 默认沉默身体的 3 选 1
        default_silent_body = [
            f"jaw tightens once, no sound",
            f"breath held, no audible exhale",
            f"eyes stay on {silent_characters[0] if silent_characters else 'speaker'}, no words",
        ]
        # 取第一条作为基础 (注册表若有, 用注册表的呼吸特征)
        v = VOICE_REGISTRY.get(ch)
        if v and v.get("breath"):
            silent_lines.append(
                f"{ch}: {v['breath']}, no speech. jaw set, breath controlled."
            )
        else:
            silent_lines.append(
                f"{ch}: {default_silent_body[0]}, no speech. {default_silent_body[2]}."
            )

    silence_rule = (
        "SILENCE_RULE: " + ", ".join(silent_characters) + " remain silent. "
        "No ad-libs. No 'uhm'. No 'uh'. No second line. "
        "Only the quoted line in this block is spoken by anyone in this shot.\n"
        + "\n".join("  " + s for s in silent_lines)
    )
    return silence_rule


def build_continuity_tail(prev_clip: Dict[str, Any]) -> str:
    """
    函数 5: build_continuity_tail
    -------------------------------------------------------------
    目的: 从上一镜提取声音尾巴, 让新镜第一秒接住, 缝合剪辑缝。

    5 要素驱动:
    - 数据: 上一镜的 voice_print + last_breath + last_tremor + ambient_tail
    - 上下文: prev_clip 字典 (last_line / last_breath / last_tremor / ambient / emotion)
    - Harness: CONTINUITY_TAIL 5 类选 1-3 类组合
    - 经验: Higgsfield - "上一句的尾音/呼吸/手部颤抖进入新镜第一秒"
    - AI 深度: 接缝假 = 两个 clip 像两条不同视频拼起来; 接缝真 = 上一秒的事没结束

    参数:
        prev_clip: dict, 含以下字段 (按可用性动态选):
            - last_line:      上一镜的台词字符串 (e.g. "I'm not afraid of you.")
            - last_breath:    上一镜结尾的呼吸描述 (e.g. "long exhale")
            - last_tremor:    上一镜结尾的手/身体颤抖 (e.g. "right hand still shaking")
            - ambient_tail:   上一镜的环境音尾巴 (e.g. "siren still fading, 2s left")
            - emotion_after:  上一镜结尾的情绪状态 (e.g. "tense")

    返回:
        CONTINUITY_TAIL 块, 写在本镜第一秒

    示例:
        build_continuity_tail({
            "last_line": "I'm not afraid of you.",
            "last_breath": "held breath, then a sharp exhale",
            "last_tremor": "right hand on door, knuckles white",
            "ambient_tail": "siren 2 blocks, fading for 3 more seconds",
            "emotion_after": "defensive, fragile"
        })
    """
    # 5 要素: 数据 - 5 类 CONTINUITY_TAIL 至少选 2 类, 缝合才稳
    tail_parts = []
    used = []

    # 1. 尾音进新镜
    if prev_clip.get("last_line"):
        # 把最后一句的尾音描述化 (不复读台词, 只描述声音物理)
        last_words = prev_clip["last_line"].rstrip(".!? ").split()[-3:]
        tail_words = " ".join(last_words)
        tail_parts.append(
            f"TAIL 0.0-1.5s — the tail of '{tail_words}' still rings in the air; "
            f"it does NOT cut at the edit point"
        )
        used.append("1_尾音进新镜")

    # 2. 呼吸进新镜
    if prev_clip.get("last_breath"):
        tail_parts.append(
            f"TAIL 0.0-1.2s — {prev_clip['last_breath']} from the previous shot "
            f"continues into the first second of this one; breath does NOT reset"
        )
        used.append("2_呼吸进新镜")

    # 3. 手部颤抖进新镜
    if prev_clip.get("last_tremor"):
        tail_parts.append(
            f"TAIL 0.5-2.0s — {prev_clip['last_tremor']} carries over; "
            f"the tremor is still visible in the new framing"
        )
        used.append("3_手部颤抖进新镜")

    # 4. 环境延音进新镜
    if prev_clip.get("ambient_tail"):
        tail_parts.append(
            f"AMBIENT TAIL 0.0-3.0s — {prev_clip['ambient_tail']}; "
            f"the room is the same room, the air does NOT cut"
        )
        used.append("4_环境延音进新镜")

    # 5. 情绪余韵进新镜
    if prev_clip.get("emotion_after"):
        tail_parts.append(
            f"EMOTION TAIL 0.0-2.0s — the {prev_clip['emotion_after']} from the "
            f"previous shot is still in the body; the new character enters carrying it"
        )
        used.append("5_情绪余韵进新镜")

    if not tail_parts:
        return "CONTINUITY_TAIL: (no prev_clip info; this is the opening shot)"

    # 5 要素: 经验矩阵 - 5 铁律第 1 条"资产先行"的延展
    # 声音连续性 = 跨镜头的资产契约
    header = (
        f"CONTINUITY_TAIL ({len(used)} of 5 categories active: {', '.join(used)}):\n"
    )
    return header + "\n".join("  " + p for p in tail_parts)


def build_sfx_only_rule(duration_sec: float = 12.0,
                        aspect: str = "16:9") -> str:
    """
    函数 6: build_sfx_only_rule
    -------------------------------------------------------------
    目的: 把 "SFX only. No music." 写成强制项, 贴到 prompt 收尾。

    5 要素驱动:
    - 数据: brief 原话 "SFX only. No music. (音乐属于后期)"
    - 上下文: 时长 + 画幅
    - Harness: 收尾标签固定格式
    - 经验: 5 铁律第 4 条 "给模型更少的自由" - SFX only 就是给声音更少自由
    - AI 深度: 写了 SFX only = 模型不会加 bgm; 不写 = 模型会加电子氛围

    参数:
        duration_sec: 镜头时长 (秒)
        aspect: 画幅 (e.g. "16:9", "2.39:1")

    返回:
        收尾强制项字符串

    示例:
        build_sfx_only_rule(12.0, "16:9")
        # -> "Live-action. NON-IP. 16:9. 12.0s. SFX only. NO CGI. Cinematic.
        #     Audio: Environmental SFX only. No music. No subtitles.
        #     Music is added in post, never in the generation audio."
    """
    # 5 要素: AI 深度 - 把 brief 原文多版本拼齐, 防御性更强
    rule = (
        f"Live-action. NON-IP. {aspect}. {duration_sec}s. SFX only. NO CGI. Cinematic.\n"
        f"Audio: Environmental SFX only. No music. No subtitles. No bgm. No diegetic score.\n"
        f"Music is added in post, never in the generation audio."
    )
    return rule


def build_soundscape(air: str, footstep: str, ambient_action: str,
                     distant: str) -> str:
    """
    函数 7: build_soundscape
    -------------------------------------------------------------
    目的: 4 层声音景观组装, 给一个镜头/一场戏的环境音底。

    5 要素驱动:
    - 数据: SOUNDSCAPE_4_LAYERS 4 类 (空气/脚步/环境动作/远景)
    - 上下文: 4 类各一段描述, 每段 1-2 句
    - Harness: 每类固定层位, 顺序不可乱
    - 经验: 反 AI 规则 9 - "SFX 写具体物, 不写情绪"
    - AI 深度: 4 层互不重叠, 一起覆盖低/中/高/远 4 个频段

    参数:
        air:           空气层 - 封闭空间固有共振, HVAC, 雨敲窗, 街道底噪
        footstep:      脚步层 - 鞋底+地面+步速+承重
        ambient_action: 环境动作层 - 门/键盘/物件/液体
        distant:       远景层 - 远处人声碎片, 警报, 撞击, 雷

    返回:
        4 层声音景观字符串, 直接进 H3 overall_soundscape 字段

    示例:
        build_soundscape(
            "concrete training room, low HVAC hum at 60Hz, 1.8s reverb tail",
            "two pairs of feet: ROCO barefoot on mat (soft pad), JAX trainers on concrete (rubber scuff)",
            "tablet taps on a metal bench; a soda can crack open; a lighter flick",
            "siren 2 blocks away, 8s ago and fading; a single dog bark, then silence"
        )
    """
    # 5 要素: 经验矩阵 - 反 AI 规则 9, 每层都验一下"是否写了具体物"
    def _concretize(layer_name: str, desc: str) -> str:
        # 若描述太抽象, 加一个 hint
        abstract_tokens = ["ambient", "atmosphere", "mood", "feel", "sense"]
        if any(t in desc.lower() for t in abstract_tokens):
            return (
                f"[HINT: '{layer_name}' should name a specific object or action, "
                f"not an abstract mood]\n  " + desc
            )
        return desc

    air_c = _concretize("air", air)
    footstep_c = _concretize("footstep", footstep)
    ambient_action_c = _concretize("ambient_action", ambient_action)
    distant_c = _concretize("distant", distant)

    soundscape = (
        "SOUNDSCAPE — 4 layers (low → high → far):\n"
        f"  1. AIR: {air_c}\n"
        f"  2. FOOTSTEP: {footstep_c}\n"
        f"  3. AMBIENT ACTION: {ambient_action_c}\n"
        f"  4. DISTANT: {distant_c}\n"
        "Layer hierarchy rule: AIR is the floor; DISTANT is the ceiling; "
        "FOOTSTEP and AMBIENT ACTION are mid-band, must be separable in the mix."
    )
    return soundscape


def render_audio_prompt(scene_context: Dict[str, Any]) -> str:
    """
    函数 8: render_audio_prompt
    -------------------------------------------------------------
    目的: 把一个场景的全部声音层, 组装成完整的 AUDIO prompt block。

    5 要素驱动:
    - 数据: 上面所有函数 + 5 要素 + Higgsfield brief
    - 上下文: scene_context = {
        "scene": str, "speakers": [str], "emotion": str, "director": str,
        "active_speaker": str, "line": str, "body_action": str,
        "face_reaction": str, "silent_characters": [str],
        "prev_clip": dict, "soundscape_4_layers": {air, footstep, ambient_action, distant},
        "duration_sec": float, "aspect": str
      }
    - Harness: AUDIO 块 (4段) + 沉默规则 + CONTINUITY_TAIL + SOUNDSCAPE + SFX_ONLY
    - 经验: brief 原话 + 反 AI 规则 10 条
    - AI 深度: 5 要素一起推理, 动态组装, 不是模板

    返回:
        完整 AUDIO prompt 块字符串, 可粘贴到 prompt_builder 的 overall_soundscape 字段

    示例:
        render_audio_prompt({
            "scene": "training room, ROCO alone, JAX and REIN enter",
            "speakers": ["JAX"], "silent_characters": ["REIN"],
            "active_speaker": "JAX", "emotion": "defensive, quick",
            "line": "We've got food.",
            "body_action": "JAX holds two trays at chest height, doesn't move closer",
            "face_reaction": "his jaw sets once, releases; his eyes flick to ROCO's crystal arm",
            "prev_clip": {
                "last_line": "...", "last_breath": "held breath",
                "last_tremor": "ROCO's right hand trembling",
                "ambient_tail": "HVAC hum continues",
                "emotion_after": "tense, exhausted"
            },
            "soundscape_4_layers": {
                "air": "concrete training room, 1.8s reverb",
                "footstep": "two pairs of trainers on concrete, slowing as they reach the mat",
                "ambient_action": "tray plastic creak; REIN's tablet screen tap",
                "distant": "siren 3 blocks, fading"
            },
            "duration_sec": 12.0, "aspect": "16:9"
        })
    """
    # === 5 要素: 数据 - 上下文缩略 ===
    scene = scene_context.get("scene", "")
    speakers = scene_context.get("speakers", [])
    silent_chars = scene_context.get("silent_characters", [])
    active_speaker = scene_context.get("active_speaker", speakers[0] if speakers else "")
    emotion = scene_context.get("emotion", "neutral")
    line = scene_context.get("line", "")
    body_action = scene_context.get("body_action", "")
    face_reaction = scene_context.get("face_reaction", "")
    prev_clip = scene_context.get("prev_clip", {}) or {}
    s4 = scene_context.get("soundscape_4_layers", {}) or {}
    duration = scene_context.get("duration_sec", 12.0)
    aspect = scene_context.get("aspect", "16:9")
    director = scene_context.get("director", "Higgsfield / Hell Grind reference")

    # 5 要素: AI 深度 - 把上下文喂给 5 要素注入器
    five_e = _make_5_elements_block(
        {"scene": scene, "speakers": speakers, "emotion": emotion, "director": director},
        prev_clip_summary=str(prev_clip)[:120],
    )

    # 1. CONTINUITY_TAIL (新镜第一秒)
    continuity = build_continuity_tail(prev_clip) if prev_clip else "CONTINUITY_TAIL: (opening shot, no tail)"

    # 2. SOUNDSCAPE 4 层
    if s4 and all(k in s4 for k in ("air", "footstep", "ambient_action", "distant")):
        soundscape = build_soundscape(s4["air"], s4["footstep"],
                                      s4["ambient_action"], s4["distant"])
    else:
        soundscape = (
            "SOUNDSCAPE — 4 layers (auto-minimal):\n"
            "  1. AIR: location-specific room tone, low ambient hum\n"
            "  2. FOOTSTEP: per character's shoe on the surface\n"
            "  3. AMBIENT ACTION: any object touched in the shot\n"
            "  4. DISTANT: at least one far-field sound for depth\n"
            "  [HINT: provide soundscape_4_layers in scene_context for richer result]"
        )

    # 3. AUDIO 块 (4 段刚性结构)
    if active_speaker and line:
        audio_block = build_dialogue_block(
            active_speaker, emotion, line, body_action, face_reaction
        )
    else:
        audio_block = (
            "AUDIO (no dialogue this shot — character is silent or non-speaking):\n"
            "— VOICE DESCRIPTOR: (no speech this shot)\n"
            "— DIALOGUE: N/A\n"
            "— BODY ACTION: " + (body_action or "[fill in body action]") + "\n"
            "— FACE REACTION: " + (face_reaction or "[fill in face reaction]") + "\n"
            "— SILENCE_RULE: all characters present remain silent this shot."
        )

    # 4. SILENCE_RULE (没台词的人)
    silence_rule = enforce_silence(silent_chars)

    # 5. SFX ONLY 收尾
    sfx_rule = build_sfx_only_rule(duration, aspect)

    # === 5 要素: 经验矩阵 - 反 AI 规则 10 条 ===
    anti_ai = "\n".join(f"  - {r}" for r in AUDIO_ANTI_AI_RULES)

    # 完整组装
    full = (
        "=" * 60 + "\n"
        + "PHASE 14 SOUND SKILL — AUDIO PROMPT BLOCK\n"
        + "=" * 60 + "\n\n"
        + five_e + "\n\n"
        + "─" * 60 + "\n"
        + "PART 1 — CONTINUITY_TAIL (new shot's first 0-3s)\n"
        + "─" * 60 + "\n"
        + continuity + "\n\n"
        + "─" * 60 + "\n"
        + "PART 2 — SOUNDSCAPE 4 LAYERS (low → high → far)\n"
        + "─" * 60 + "\n"
        + soundscape + "\n\n"
        + "─" * 60 + "\n"
        + "PART 3 — AUDIO BLOCK (4-segment rigid grammar)\n"
        + "─" * 60 + "\n"
        + audio_block + "\n\n"
        + "─" * 60 + "\n"
        + "PART 4 — SILENCE_RULE (no-ad-libs enforcement)\n"
        + "─" * 60 + "\n"
        + silence_rule + "\n\n"
        + "─" * 60 + "\n"
        + "PART 5 — AUDIO ANTI-AI RULES (10 rules from Hell Grind)\n"
        + "─" * 60 + "\n"
        + anti_ai + "\n\n"
        + "─" * 60 + "\n"
        + "PART 6 — SFX-ONLY CLOSING TAG (强制项)\n"
        + "─" * 60 + "\n"
        + sfx_rule + "\n"
        + "=" * 60 + "\n"
    )

    # 5 要素: AI 深度 - 用 Phase 13 的反 AI 词表再洗一次
    if _HAS_AI_DEPS:
        try:
            full = clean_anti_ai_text(full)
        except Exception:
            pass

    return full


def post_process_audio(raw_audio: Dict[str, Any]) -> Dict[str, Any]:
    """
    函数 9: post_process_audio
    -------------------------------------------------------------
    目的: 给后期环节的接口, 描述 Seedance 生成音轨的清理流程。

    5 要素驱动:
    - 数据: POST_PROCESS_PIPELINE 6 步 (从 brief 原文反推)
    - 上下文: raw_audio 字典 (含 dialogue / sfx / ambient / location_ir / lufs_target)
    - Harness: 6 步固定顺序
    - 经验: brief 原话 - "不重录声音, Seedance对口型台词直接从生成里清理"
    - AI 深度: 每步给具体参数, 后期可执行; 不重写音频, 只清理

    参数:
        raw_audio: dict, 含以下字段 (按可用性动态选):
            - dialogue_take: Seedance 生成的对口型台词文件路径
            - sfx_take: 同上, 拟音轨
            - ambient_take: 同上, 环境底噪
            - location_ir: convolution reverb 的 impulse response 文件路径
            - voice_print_ref: 角色声音的 reference print (用于匀音色)
            - lufs_target: 响度目标 (默认 -16 broadcast)
            - true_peak_dbtp: true peak 上限 (默认 -1.5)

    返回:
        后期处理 plan dict, 含每步的具体操作和参数

    示例:
        post_process_audio({
            "dialogue_take": "/seedance/roco_dlg_001.wav",
            "sfx_take": "/seedance/roco_sfx_001.wav",
            "ambient_take": "/seedance/room_tone_001.wav",
            "location_ir": "/ir/training_room_1.8s.wav",
            "voice_print_ref": "ROCO",
            "lufs_target": -16,
            "true_peak_dbtp": -1.5
        })
    """
    # 5 要素: 数据 - 6 步固定
    plan = {
        "step_1_denoise": {
            "tool": "FFT-based noise reduction",
            "params": {
                "noise_gate_db": -18,
                "preserve_freq_bands": {
                    "chest_breath_below_hz": 200,
                    "mouth_sound_hz": "200-500",
                    "hum_removal_hz": [50, 60],
                    "hiss_removal_hz": 8000,
                },
            },
            "input": raw_audio.get("dialogue_take", "[Seedance dialogue WAV]"),
            "output": "[denoised dialogue WAV, breath preserved]",
        },
        "step_2_timbre_match": {
            "tool": "spectral formant alignment",
            "params": {
                "match_band_hz": "80-3000",
                "preserve_natural_sibilance": True,
                "de_ess_threshold_hz": 6000,
            },
            "reference": raw_audio.get("voice_print_ref", "ROCO (registered)"),
            "output": "[timbre-normalized dialogue, voice print stable across clips]",
        },
        "step_3_spatialization": {
            "tool": "convolution reverb",
            "params": {
                "ir_file": raw_audio.get("location_ir", "[location-matched IR]"),
                "decay_seconds": 1.8,
                "distance_rolloff_db_per_doubling": -3,
            },
            "pan_reference": "GEO SPATIAL LAYOUT (from spatial_layout)",
            "output": "[dialogue placed in 3D space, pan matches camera frame]",
        },
        "step_4_dialogue_clarity": {
            "tool": "center channel + side ducking",
            "params": {
                "dialogue_pan": "center",
                "env_side_reduction_db": -6,
                "lufs_target": raw_audio.get("lufs_target", -16),
                "true_peak_dbtp": raw_audio.get("true_peak_dbtp", -1.5),
            },
            "output": "[broadcast-ready dialogue bus]",
        },
        "step_5_shared_room_tone": {
            "tool": "loop + crossfade",
            "params": {
                "ambient_take": raw_audio.get("ambient_take", "[8s room tone]"),
                "loop_seconds": 8,
                "crossfade_ms": 200,
            },
            "output": "[continuous room tone across all clips in this location]",
        },
        "step_6_music_layered_last": {
            "tool": "music over SFX bed",
            "params": {
                "music_source": "[composed or licensed, NOT from Seedance]",
                "duck_under_dialogue_db": -8,
            },
            "warning": "Music is layered LAST. Never re-record dialogue. "
                      "Only ADR if Seedance's take is unrecoverable.",
            "output": "[final mix: SFX bed + dialogue + music]",
        },
    }

    # 5 要素: AI 深度 - 给一个简短的执行总结
    plan["execution_summary"] = (
        f"6 步后期处理 plan 已生成: input = {raw_audio.get('dialogue_take', 'n/a')}; "
        f"voice ref = {raw_audio.get('voice_print_ref', 'n/a')}; "
        f"output target: broadcast LUFS {raw_audio.get('lufs_target', -16)}; "
        f"音乐后叠 (per Higgsfield brief)"
    )
    return plan


def get_voice_consistency_check(name: str, prev_clip: Dict[str, Any]) -> Dict[str, Any]:
    """
    函数 10: get_voice_consistency_check
    -------------------------------------------------------------
    目的: 跨镜头的自检 - 本镜的声音是否真的接住了上一镜。

    5 要素驱动:
    - 数据: CONTINUITY_TAIL 5 类 + 声音注册表
    - 上下文: 角色名 + prev_clip dict
    - Harness: 自检 = 5 铁律第 1 条 "资产先行" 的延展
    - 经验: 115K 次生成的教训 - 接缝假是最常见的废镜头
    - AI 深度: 给出可量化的"接缝真度"评分, 不用人耳

    参数:
        name: 角色名
        prev_clip: 上一镜的 dict (同 build_continuity_tail 的输入)

    返回:
        自检 dict, 含:
            - voice_locked: bool (声音档案是否已注册)
            - descriptor_used: str (本镜应粘贴的 descriptor)
            - tail_categories_active: list (本镜接住了几个 CONTINUITY_TAIL)
            - consistency_score: float 0-1 (1.0 = 完美接缝)
            - warnings: list of str (问题清单)

    示例:
        get_voice_consistency_check("JAX", {
            "last_line": "I'm not afraid of you.",
            "last_breath": "held breath, sharp exhale",
            "last_tremor": "knuckles white on door",
            "ambient_tail": "siren fading",
            "emotion_after": "defensive"
        })
    """
    # 5 要素: 数据 - 声音档案检查
    v = VOICE_REGISTRY.get(name)
    voice_locked = v is not None
    descriptor = v["descriptor"] if v else f"[UNREGISTERED: {name}]"

    # 5 要素: 经验矩阵 - 接住几类 CONTINUITY_TAIL
    tail_categories_active = []
    if prev_clip.get("last_line"):
        tail_categories_active.append("1_尾音进新镜")
    if prev_clip.get("last_breath"):
        tail_categories_active.append("2_呼吸进新镜")
    if prev_clip.get("last_tremor"):
        tail_categories_active.append("3_手部颤抖进新镜")
    if prev_clip.get("ambient_tail"):
        tail_categories_active.append("4_环境延音进新镜")
    if prev_clip.get("emotion_after"):
        tail_categories_active.append("5_情绪余韵进新镜")

    # 5 要素: AI 深度 - 可量化评分
    # 满分 1.0, 5 维各 0.2
    n_active = len(tail_categories_active)
    continuity_score = min(n_active / 3.0, 1.0)  # 至少 3 类才算接缝真
    voice_score = 1.0 if voice_locked else 0.0
    # 综合: 声音锁定 (40%) + 接缝 (60%)
    consistency_score = round(voice_score * 0.4 + continuity_score * 0.6, 2)

    warnings = []
    if not voice_locked:
        warnings.append(
            f"[CRITICAL] {name} 未注册声音档案. "
            f"调用 register_voice({name}, ...) 否则模型会随机给声音."
        )
    if n_active < 2:
        warnings.append(
            f"[HIGH] 仅 {n_active} 类 CONTINUITY_TAIL 接住, "
            f"建议 ≥ 3 类 (尾音+呼吸+颤抖) 才能缝合."
        )
    if prev_clip.get("last_line") and not prev_clip.get("last_breath"):
        warnings.append(
            "[MEDIUM] 上一镜有台词但本镜没接呼吸, 接缝处会有 '呼吸归零' 的假感."
        )
    if not prev_clip:
        warnings.append("[INFO] 无 prev_clip, 这是开场镜头, 不用接缝.")

    return {
        "voice_locked": voice_locked,
        "descriptor_used": descriptor,
        "tail_categories_active": tail_categories_active,
        "consistency_score": consistency_score,
        "warnings": warnings,
    }


# =============================================================================
#  3 个 Hell Grind 示例 (来自 brief + 反推)
# =============================================================================

def demo_antagonist_voice() -> str:
    """
    示例 1: 反派示例 - Voice: deep, gravelly bass-baritone; slow, calculated
            pacing; London street accent; menacing calm — he never raises his voice.

    来源: Higgsfield brief 原文, 反派声音档案
    """
    # 5 要素: 注册
    register_voice(
        "ANTAGONIST",
        voice_range="bass-baritone, A1-E3",
        timbre="deep, gravelly, with a permanent low rumble under the speech",
        speed="slow, calculated, every word placed; never rushed",
        accent="London street, hardened, glottal on emphasis",
        breath="deep, slow, breath heard but never gasping; controlled menace",
        pressure=(
            "under pressure: voice gets quieter, not louder; pauses stretch; "
            "the lower the pressure seems, the more dangerous he is"
        ),
    )

    # 5 要素: AI 深度 - 把 brief 原话 descriptor 直接落地
    VOICE_REGISTRY._registry["ANTAGONIST"]["descriptor"] = (
        "deep, gravelly bass-baritone; slow, calculated pacing; "
        "London street accent; menacing calm — he never raises his voice"
    )

    # 5 要素: 经验矩阵 - 用这套声音生成一个 AUDIO 块示例
    audio = build_dialogue_block(
        speaker="ANTAGONIST",
        emotion="menacing calm, no raise in volume",
        line="Boys. I have been waiting.",
        body_action=(
            "he stands at the doorway, weight on the back foot, "
            "right hand resting on the door frame, not gripping"
        ),
        face_reaction=(
            "the corner of his mouth rises 2mm, no teeth; "
            "one slow blink; eyes stay on the crystal arm"
        ),
    )
    return audio


def demo_jax_dialogue_no_line_in_action() -> str:
    """
    示例 2: JAX 对话 - 动作区不放台词, AUDIO 区只放引号里的那一句

    来源: Higgsfield AUDIO 块规则 - "每个人只说引号里的那句; 没台词的人全程沉默"
    """
    # JAX 已在 HELL_GRIND_VOICE_PRESETS 里预置, 直接取
    jax_descriptor = get_voice_descriptor("JAX")

    # 关键演示: 动作区只有身体动作, 0 个引号, 0 个台词词
    action_block = (
        "[Shot 3] At 00:08.000, the camera holds a medium shot on JAX as he\n"
        "enters the training room. ACTION TIMING:\n"
        "  0.0-1.0s — JAX stops at the door, both trays held at chest height\n"
        "  1.0-3.5s — his eyes find ROCO's crystal arm, stay there\n"
        "  3.5-4.0s — his jaw sets once, releases\n"
        "  4.0-5.0s — his right thumb taps the plastic tray twice, no words yet\n"
        "  5.0-5.8s — he speaks the AUDIO line below, only line in this shot\n"
        "  5.8-6.5s — a quick DOUBLE-BLINK, then eyes flick to REIN\n"
        "\n"
        "  *** NO DIALOGUE IN THIS ACTION BLOCK ***\n"
        "  *** AUDIO BLOCK BELOW IS THE ONLY PLACE JAX SPEAKS ***\n"
        "\n"
    )

    audio_block = build_dialogue_block(
        speaker="JAX",
        emotion="defensive, quick, trying to sound normal",
        line="We've got food.",
        body_action=(
            "JAX holds two trays at chest height, doesn't move closer; "
            "his right thumb stops tapping the plastic"
        ),
        face_reaction=(
            "his jaw sets once, releases; his eyes flick to ROCO's crystal arm "
            "and stay half a second too long"
        ),
    )

    # 没台词的人明确沉默
    silence = enforce_silence(["ROCO", "REIN"])

    # 收尾
    sfx = build_sfx_only_rule(duration_sec=6.5, aspect="16:9")

    return (
        f"=== DEMO 2: JAX 对话 - 动作区不放台词 ===\n\n"
        f"  voice descriptor (auto from registry):\n    {jax_descriptor}\n\n"
        f"  ACTION BLOCK (NO dialogue):\n{action_block}\n"
        f"  AUDIO BLOCK (only place JAX speaks):\n{audio_block}\n\n"
        f"  SILENCE_RULE (ROCO and REIN remain silent):\n{silence}\n\n"
        f"  SFX-ONLY TAG:\n{sfx}\n"
    )


def demo_corridor_soundscape() -> str:
    """
    示例 3: 走廊环境音 - 走廊空气声/两组脚步声/平板轻触声/远处撞击声

    来源: 4 层声音景观标准配置
    """
    soundscape = build_soundscape(
        air=(
            "underground corridor, concrete walls 3m apart, 2.4s reverb tail, "
            "HVAC hum at 80Hz under everything, faint fluorescent buzz at 100Hz"
        ),
        footstep=(
            "two pairs: ROCO barefoot (soft pad, slower, 1 step/sec), "
            "JAX trainers on concrete (rubber scuff, 1.6 steps/sec, "
            "slightly out of sync with REIN's boots)"
        ),
        ambient_action=(
            "REIN's tablet screen tap (glass on glass, 3 quick taps, then hold); "
            "a soda can crack open from JAX; a door hinge (oiled, slow) "
            "closing 6m behind them"
        ),
        distant=(
            "a distant metal impact (locker slam) 2 corridors away, "
            "8 seconds after ROCO pauses; "
            "a single dog bark from the surface, very far, no echo"
        ),
    )

    # 4 层验真 (反 AI 规则 9: 写具体物)
    sfx = build_sfx_only_rule(duration_sec=12.0, aspect="2.39:1")

    # CONTINUITY_TAIL 示例
    tail = build_continuity_tail({
        "last_line": "We've got food.",
        "last_breath": "JAX's held breath releasing",
        "last_tremor": "the soda can in JAX's left hand, lid still vibrating",
        "ambient_tail": "HVAC hum carries over, same 80Hz",
        "emotion_after": "defensive, scanning",
    })

    return (
        f"=== DEMO 3: 走廊环境音 - 4 层声音景观 ===\n\n"
        f"  {soundscape}\n\n"
        f"  CONTINUITY_TAIL (incoming shot, first 3s):\n{tail}\n\n"
        f"  SFX-ONLY TAG:\n{sfx}\n"
    )


# =============================================================================
#  ComfyUI 节点封装 (Node 集群标准接口)
# =============================================================================

class SoundSkill:
    """
    Sound layer层专家节点 - 集群 ComfyUI 入口
    --------------------------------------------------------
    集群内角色: 负责 prompt 的声音层, 与 camera / acting / space / assets / post
               5 个节点互锁, 共同组成 node cluster。

    输入: 场景上下文 dict + prev_clip dict
    输出: 3 个字符串 - audio_prompt / experience_matrix / ai_deep_processing
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "场景描述": ("STRING", {
                    "default": "Hell Grind 训练室, ROCO 独处, JAX 和 REIN 推门进入, "
                              "手里端着食物, ROCO 转身",
                    "multiline": True,
                }),
                "说话角色名": ("STRING", {"default": "JAX"}),
                "情绪基调": ("STRING", {"default": "defensive, quick, trying to sound normal"}),
                "台词": ("STRING", {"default": "We've got food."}),
                "身体动作": ("STRING", {
                    "default": "JAX 双手举着塑料餐盘在胸口高度, 不再往前走; "
                              "右手拇指停在餐盘上不再敲",
                }),
                "面部反应": ("STRING", {
                    "default": "他的下颌咬紧一次, 松开; 眼睛瞟了一眼 ROCO 的晶体臂 "
                              "多停了半秒",
                }),
                "沉默角色名": ("STRING", {"default": "ROCO, REIN"}),
                "空气层": ("STRING", {
                    "default": "地下训练室, 混凝土墙 3m 间距, 2.4s 混响尾巴, "
                              "HVAC 80Hz 嗡鸣",
                }),
                "脚步层": ("STRING", {
                    "default": "两组脚步: ROCO 赤脚在训练垫上 (软垫, 慢, 1 步/秒), "
                              "JAX 训练鞋在混凝土上 (橡胶蹭地, 1.6 步/秒)",
                }),
                "环境动作层": ("STRING", {
                    "default": "REIN 平板触屏声 (玻璃对玻璃, 3 次轻点); "
                              "JAX 拉开一罐汽水; 6m 外一扇门上链 (上过油, 慢)",
                }),
                "远景层": ("STRING", {
                    "default": "远处金属撞击声 (柜子砰) 隔两条走廊; "
                              "地表一只狗叫, 很远, 没回声",
                }),
                "镜头时长秒": ("FLOAT", {"default": 12.0, "min": 0.5, "max": 60.0}),
                "画幅": (["16:9", "2.39:1", "4:3", "1:1", "9:16"], {"default": "16:9"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "上一镜_最后一句": ("STRING", {"default": ""}),
                "上一镜_最后呼吸": ("STRING", {"default": ""}),
                "上一镜_最后颤抖": ("STRING", {"default": ""}),
                "上一镜_环境延音": ("STRING", {"default": ""}),
                "上一镜_情绪余韵": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("sound_audio_prompt", "sound_experience_matrix", "sound_ai_deep_processing")
    FUNCTION = "build_sound"
    CATEGORY = "PromptLibrary/Node 集群"

    def build_sound(self, **kwargs):
        # type 防御
        def _s(v, default=""):
            if v is None:
                return default
            if isinstance(v, (list, tuple)):
                return str(v[0]) if v else default
            return str(v)

        scene = _s(kwargs.get("场景描述"), "")
        speaker = _s(kwargs.get("说话角色名"), "JAX")
        emotion = _s(kwargs.get("情绪基调"), "")
        line = _s(kwargs.get("台词"), "")
        body = _s(kwargs.get("身体动作"), "")
        face = _s(kwargs.get("面部反应"), "")
        silent_chars_str = _s(kwargs.get("沉默角色名"), "")
        silent_chars = [c.strip() for c in silent_chars_str.split(",") if c.strip()]

        air = _s(kwargs.get("空气层"), "")
        foot = _s(kwargs.get("脚步层"), "")
        ambient = _s(kwargs.get("环境动作层"), "")
        distant = _s(kwargs.get("远景层"), "")
        duration = float(kwargs.get("镜头时长秒") or 12.0)
        aspect = _s(kwargs.get("画幅"), "16:9")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))

        # 上一镜字段 (optional)
        prev_clip = {}
        if kwargs.get("上一镜_最后一句"):
            prev_clip["last_line"] = _s(kwargs.get("上一镜_最后一句"))
        if kwargs.get("上一镜_最后呼吸"):
            prev_clip["last_breath"] = _s(kwargs.get("上一镜_最后呼吸"))
        if kwargs.get("上一镜_最后颤抖"):
            prev_clip["last_tremor"] = _s(kwargs.get("上一镜_最后颤抖"))
        if kwargs.get("上一镜_环境延音"):
            prev_clip["ambient_tail"] = _s(kwargs.get("上一镜_环境延音"))
        if kwargs.get("上一镜_情绪余韵"):
            prev_clip["emotion_after"] = _s(kwargs.get("上一镜_情绪余韵"))

        # 组装 scene_context
        scene_context = {
            "scene": scene,
            "speakers": [speaker] + silent_chars,
            "emotion": emotion,
            "director": "Higgsfield / Hell Grind reference",
            "active_speaker": speaker,
            "line": line,
            "body_action": body,
            "face_reaction": face,
            "silent_characters": silent_chars,
            "prev_clip": prev_clip,
            "soundscape_4_layers": {
                "air": air, "footstep": foot,
                "ambient_action": ambient, "distant": distant,
            },
            "duration_sec": duration,
            "aspect": aspect,
        }

        # 主体: 完整 AUDIO prompt
        main_output = render_audio_prompt(scene_context)

        # 输出 2: 经验矩阵
        experience = (
            "【Sound layer层 - 经验矩阵】\n\n"
            "Higgsfield Hell Grind 6 层生产系统 - 第四层 (声音):\n"
            "  - 声音是角色资产 (与视觉资产并列)\n"
            "  - 音域/音色/语速/口音/呼吸/压力 6 维\n"
            "  - AUDIO 块 4 段刚性结构 (voice+emotion→quoted line→body action→face reaction)\n"
            "  - 没台词的人明确保持沉默 (写在 prompt)\n"
            "  - 跨镜头接缝: 尾音/呼吸/颤抖/环境延音/情绪余韵 进新镜第一秒\n"
            "  - 4 层声音景观 (空气/脚步/环境动作/远景)\n"
            "  - 6 步后期处理 (降噪/匀音色/空间化/对话清晰度/连续环境底噪/音乐后叠)\n"
            "  - SFX only - 音乐属于后期\n\n"
            "5 条铁律 (声音层适用):\n"
            "  1. 资产先行 - 声音也锁, 不锁不开机\n"
            "  2. 每次都描述全部 - voice descriptor 逐字粘贴\n"
            "  3. 一次只改一行 - 修改声音要写日志\n"
            "  4. 给模型更少的自由 - 声音比画面更敏感, 必须给死\n"
            "  5. 镜头搞不定, 就简化镜头 - 拆/删/换\n\n"
            "3 个 Hell Grind 实战示例:\n"
            "  1. 反派示例: bass-baritone, slow calculated, London street, menacing calm\n"
            "  2. JAX 对话: 动作区 0 台词, AUDIO 块 1 句\n"
            "  3. 走廊环境音: 4 层声音景观 (空气/脚步/平板/远处撞击)\n\n"
            "声音连续性自检 (consistency_score):\n"
            + str(get_voice_consistency_check(speaker, prev_clip)) + "\n"
        )

        # 输出 3: AI 深度处理
        ai_deep = (
            "【Sound layer层 - AI 深度处理】\n\n"
            "5 要素架构作为推理路径:\n"
            "  1. 数据: 50 美元电影 brief + 115,446 次生成 + 6 层生产系统\n"
            "  2. 上下文缩略: scene / speakers / emotion / prev_clip\n"
            "  3. Skill/Harness: voice registry + AUDIO 4 段语法 + 沉默规则 + CONTINUITY_TAIL\n"
            "  4. 经验矩阵: 6 文件系统 + 5 铁律 + Hell Grind 4 主角声音档案\n"
            "  5. AI 深度: 不是模板拼接, 是把场景具体人/事/情代入\n\n"
            "10 条反 AI 规则 (声音层):\n"
            + "\n".join(f"  - {r}" for r in AUDIO_ANTI_AI_RULES) + "\n\n"
            "6 步后期处理 pipeline:\n"
            + "\n".join(f"  - {k}: {(v.get('tool', '?') if isinstance(v, dict) else str(v)[:80])}" for k, v in POST_PROCESS_PIPELINE.items()) + "\n\n"
            "压力下 5 种声音变化:\n"
            + "\n".join(f"  - {k}: {v}" for k, v in PRESSURE_VOICE_CHANGES.items()) + "\n"
        )

        if anti_ai_on and _HAS_AI_DEPS:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        return (main_output, experience, ai_deep)


# =============================================================================
#  ComfyUI 节点注册
# =============================================================================

# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "SoundSkill": SoundSkill,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "SoundSkill": "🔊 Sound层专家 (Higgsfield AUDIO 块架构)",
# }


# =============================================================================
#  自测入口 (本文件可直接 python sound_skill.py 跑, 输出 3 个 demo)
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Sound layer层专家 - 3 个 Hell Grind 示例")
    print("=" * 60 + "\n")

    print("\n--- DEMO 1: 反派示例 (Voice descriptor) ---")
    print(demo_antagonist_voice())

    print("\n--- DEMO 2: JAX 对话 (动作区不放台词) ---")
    print(demo_jax_dialogue_no_line_in_action())

    print("\n--- DEMO 3: 走廊环境音 (4 层声音景观) ---")
    print(demo_corridor_soundscape())

    print("\n--- 自检: get_voice_consistency_check(JAX, prev_clip) ---")
    print(get_voice_consistency_check("JAX", {
        "last_line": "We've got food.",
        "last_breath": "JAX's held breath releasing",
        "last_tremor": "the soda can in JAX's left hand, lid still vibrating",
        "ambient_tail": "HVAC hum carries over, same 80Hz",
        "emotion_after": "defensive, scanning",
    }))

    print("\n" + "=" * 60)
    print("完成. 注册的角色:", VOICE_REGISTRY.list_names())
    print("=" * 60 + "\n")
