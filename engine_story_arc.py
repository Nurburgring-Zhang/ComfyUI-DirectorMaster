# ============================================================
# 故事结构引擎 — 将25个故事感总纲变为可计算的结构化数据
# ============================================================
# 核心能力：
#   1. 解析故事感总纲为结构化的节拍序列
#   2. 对给定镜头序号，精确计算其所属节拍和情绪状态
#   3. 生成镜头间的连续性约束
# ============================================================
import random
import re
import math
import os
import sys

# 确保模块搜索路径包含本目录（ComfyUI不自动添加）
_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

from story_sense_data import STORY_SENSE_LIBRARY


# ============================================================
# 情绪映射字典 — 将中文情绪词映射为数值(0.0恐惧-1.0高涨)
# ============================================================
EMOTION_MAP = {
    # 积极情绪
    "高兴": 0.85, "快乐": 0.85, "开心": 0.82, "兴奋": 0.88, "激动": 0.90,
    "温暖": 0.75, "幸福": 0.85, "满足": 0.72, "释然": 0.65,
    "希望": 0.70, "期待": 0.68, "惊喜": 0.80, "欢乐": 0.85,
    "感动": 0.70,  # [P0修复] 移除原重复定义的"感动"键
    # 中性
    "平稳": 0.50, "安稳": 0.48, "平静": 0.45, "日常": 0.50, "普通": 0.50,
    "好奇": 0.55, "新鲜": 0.55, "平淡": 0.45, "仪式感": 0.52,
    # 消极
    "悲伤": 0.20, "难过": 0.22, "失落": 0.25, "绝望": 0.05, "恐惧": 0.10,
    "紧张": 0.30, "焦虑": 0.28, "挫败": 0.18, "愤怒": 0.25, "挣扎": 0.22,
    "孤独": 0.20, "无助": 0.12, "心痛": 0.18, "压抑": 0.15, "灰暗": 0.12,
    "消沉": 0.18, "低落": 0.20, "脆弱": 0.22, "害怕": 0.15, "不安": 0.30,
    "怀疑": 0.25, "崩溃": 0.08, "泪水": 0.20, "苦涩": 0.22,
    # 过渡情绪
    "坚持": 0.45, "倔强": 0.48, "努力": 0.55, "尝试": 0.50,
    "突破": 0.72, "起飞": 0.78, "爆发": 0.80,
    "微光": 0.38, "重新": 0.45, "缓冲": 0.42,
    # 复合情绪
    "犹豫": 0.35, "思念": 0.30, "怀念": 0.35, "共鸣": 0.65,
}

# ============================================================
# 中文情绪词 → 英文标签映射
# ============================================================
EMOTION_EN_MAP = {
    "暖": "warm", "温暖": "warm", "感动": "touched", "美好": "beautiful",
    "释然": "relieved", "开阔": "open", "温柔": "gentle", "淡然": "peaceful",
    "继续": "continuing", "传递": "passing_on", "前行": "moving_on",
    "笑": "laughing", "希望在": "hopeful",
    "悲伤": "sad", "难过": "sad", "绝望": "desperate", "恐惧": "terrified",
    "紧张": "tense", "愤怒": "angry", "孤独": "lonely", "压抑": "oppressed",
    "心痛": "heartbroken", "失落": "lost",
}

# ============================================================
# 景别数值 — 用于交替检测
# ============================================================
SHOT_TYPE_PRIORITY = {
    "极远景": 1, "远景": 2, "全景": 3, "中景": 4,
    "近景": 5, "特写": 6, "极特写": 7,
}

SHOT_TYPE_NAMES = [
    "极远景", "远景", "全景", "中景", "近景", "特写", "极特写",
]


# ============================================================
# 大师级影视语言指导引擎 — CinematographyDirector
# ============================================================
# 设计理念（参考 Walter Murch、Roger Deakins、Thelma Schoonmaker 的剪辑理论）：
#   - 时长 = 叙事功能：定场给足呼吸，高潮快速切割，低谷留白沉思
#   - 运镜 = 心理语言：静止=旁观，缓推=亲密/压迫，手持=混乱/真实
#   - 转场 = 叙事语法：硬切=能量延续，叠化=时间流逝，淡出=章节终结
# ============================================================
class CinematographyDirector:
    """根据故事节拍计算大师级时长/运镜/转场推荐"""
    
    # pace → 时长范围（秒）
    PACE_DURATION = {
        "slow":   (5, 10),   # 沉思/留白/情感低谷
        "medium": (3, 6),    # 常规叙事
        "fast":   (1, 3),    # 高潮/紧张/快切
    }
    
    # 节拍阶段 → 时长精调（progress, pace, base_duration, ref_film）
    BEAT_STAGE_DURATION = [
        # (progress_max, pace, (min, max), 影视参考)
        (0.15, "medium", (5, 8),  "开场定场，《银翼杀手2049》式沉稳建立情境"),
        (0.35, "medium", (3, 6),  "张力上升期，渐进缩短暗示不安"),
        (0.55, "medium", (4, 8),  "中段铺陈，让情感沉淀"),
        (0.70, "slow",   (6, 10), "转折前最低点，《肖申克》雨中伸臂前的沉默"),
        (0.85, "fast",   (1, 3),  "高潮快剪，《疯狂的麦克斯》追车节奏"),
        (1.01, "slow",   (5, 10), "收束余韵，《花样年华》结尾缓慢走廊"),
    ]
    
    # intensity 阈值 → (pace, 运镜推荐, 心理效果)
    CAMERA_BY_INTENSITY = [
        (0.25, "slow",   "固定机位 / 极缓拉远",      "孤独、渺小、旁观感"),
        (0.45, "medium", "缓慢推轨 / 轻微摇镜",       "渐进亲密、好奇探索"),
        (0.65, "medium", "跟拍 / 平稳移轨",           "陪伴感、流畅叙事"),
        (0.85, "fast",   "手持微晃 / 快速推拉",       "紧迫、混乱、临场感"),
        (1.01, "fast",   "急推特写 / 360°环绕",      "极致情绪、高潮释放"),
    ]
    
    @staticmethod
    def get_duration_range(pace, intensity, progress):
        """根据 pace + 节拍阶段计算时长范围(秒)。
        
        参数:
            pace: "slow"/"medium"/"fast"
            intensity: 0.0-1.0 视觉强度
            progress: 0.0-1.0 故事进度
        返回:
            (min_sec, max_sec) 时长范围
        """
        # 优先按节拍阶段精调
        for prog_max, stage_pace, dur_range, _ref in CinematographyDirector.BEAT_STAGE_DURATION:
            if progress < prog_max:
                # 高情绪强度时缩短时长（视觉冲击需要快切）
                if intensity > 0.85 and dur_range[0] > 1:
                    return (max(1, dur_range[0] - 1), max(2, dur_range[1] - 2))
                return dur_range
        # fallback
        return CinematographyDirector.PACE_DURATION.get(pace, (3, 6))
    
    @staticmethod
    def get_camera_directive(intensity, pace, user_style=""):
        """根据 intensity 推荐运镜，叠加用户偏好。
        
        返回:
            (camera_text, reason) 运镜文本 + 心理效果
        """
        # 用户偏好覆盖
        user_override_map = {
            "稳重固定镜头": ("固定机位 / 微推", "用户指定稳重风格，配合内在情绪流动"),
            "流畅运动":     ("平稳移轨 / 跟拍", "用户指定流畅运动，营造叙事感"),
            "手持纪实":     ("手持微晃 / 跟拍", "用户指定手持，强化真实临场感"),
            "炫酷动感":     ("急推 / 环绕 / 旋转", "用户指定动感，释放视觉冲击"),
            "竖屏固定机位为主": ("竖屏固定机位 / 微推拉", "竖屏构图，主体居中"),
            "竖屏流畅运动":     ("竖屏纵向升降 / 前后推拉", "竖屏运动，强化纵深"),
        }
        if user_style in user_override_map:
            return user_override_map[user_style]
        
        # 根据 intensity 自动选择
        for thresh, _pace, cam_text, reason in CinematographyDirector.CAMERA_BY_INTENSITY:
            if intensity < thresh:
                return (cam_text, reason)
        return ("固定机位", "中性叙事")
    
    @staticmethod
    def get_transition(current_beat, prev_beat, scene_changed=False,
                       is_first_shot=False, is_last_shot=False,
                       cross_beat=False, emotion_delta=0.0):
        """根据节拍关系和场景变化计算转场。
        
        返回:
            (transition_text, reason)
        """
        # 首镜：从虚无淡入
        if is_first_shot:
            return ("淡入", "从虚无中进入故事世界，建立第一印象")
        
        # 末镜：长叠化或淡出
        if is_last_shot:
            return ("长叠化 / 淡出黑场", "余韵收束，让情绪在画面消散中沉淀")
        
        # 跨节拍 + 情绪跳跃大 → 章节断点
        if cross_beat and emotion_delta > 0.35:
            return ("淡出→淡入", "跨节拍情绪反差大，制造章节感的心理断点")
        
        # 跨节拍 + 情绪相近 → 匹配剪辑
        if cross_beat and emotion_delta <= 0.35:
            return ("匹配剪辑", "节拍切换但情绪延续，用主题/形状/动作匹配呼应")
        
        # 高潮→收束（高强度 → 低强度）
        if prev_beat and prev_beat.intensity > 0.75 and current_beat.intensity < 0.5:
            return ("长叠化 / 白闪", "高潮余韵的视觉消散，让能量缓慢释放")
        
        # 同节拍 + 换场景 → 叠化
        if scene_changed:
            return ("叠化", "空间过渡但情绪延续，柔化场景切换")
        
        # 同节拍 + 同场景 → 硬切
        return ("硬切", "保持叙事能量不断，画面节奏紧凑")
    
    @staticmethod
    def build_block(cinematography, cumulative_seconds=None, total_estimated=None):
        """生成注入 prompt 的影视语言指导文本块。
        
        参数:
            cinematography: get_beat_for_shot 返回的 cinematography 子字典
            cumulative_seconds: 累计已生成镜头时长（秒），可选
            total_estimated: 预估总片长（秒），可选
        返回:
            可直接拼接到 system prompt 的多行字符串
        """
        lines = ["【大师级影视语言指导】"]
        dur_hint = cinematography.get("duration_hint", "3-6秒")
        cam = cinematography.get("camera_movement", "固定机位")
        cam_reason = cinematography.get("camera_reason", "")
        trans = cinematography.get("transition", "硬切")
        trans_reason = cinematography.get("transition_reason", "")
        
        lines.append(f"▸ 推荐时长：{dur_hint}（请严格按此范围设置「时长」字段）")
        lines.append(f"▸ 推荐运镜：{cam}（{cam_reason}）")
        lines.append(f"▸ 推荐转场：{trans}（{trans_reason}）")
        
        if cumulative_seconds is not None:
            mm = int(cumulative_seconds // 60)
            ss = int(cumulative_seconds % 60)
            time_str = f"{mm}分{ss:02d}秒" if mm > 0 else f"{ss}秒"
            if total_estimated:
                tmm = int(total_estimated // 60)
                tss = int(total_estimated % 60)
                total_str = f"{tmm}分{tss:02d}秒" if tmm > 0 else f"{tss}秒"
                lines.append(f"▸ 时间线：累计约 {time_str} / 预估总长 {total_str}")
            else:
                lines.append(f"▸ 时间线：累计约 {time_str}")
        return "\n".join(lines)


class StoryBeat:
    """一个叙事节拍 — 包含情绪值、节奏、视觉强度、叙事功能、影视语言指导"""
    
    def __init__(self, name, emotion_value, pace, intensity, narrative_func,
                 duration_range=None, camera_style=None):
        self.name = name
        self.emotion_value = emotion_value  # 0.0-1.0
        self.pace = pace                    # "slow" / "medium" / "fast"
        self.intensity = intensity          # 0.0-1.0 视觉冲击力
        self.narrative_func = narrative_func  # 文本描述
        # 影视语言字段（由 CinematographyDirector 计算）
        self.duration_range = duration_range or CinematographyDirector.PACE_DURATION.get(pace, (3, 6))
        self.camera_style = camera_style or ""
    
    def to_dict(self):
        return {
            "name": self.name,
            "emotion": self.emotion_value,
            "pace": self.pace,
            "intensity": self.intensity,
            "narrative_func": self.narrative_func,
            "duration_range": self.duration_range,
            "camera_style": self.camera_style,
        }


class StoryArc:
    """故事弧 — 解析总纲并计算每个镜头的节拍位置"""
    
    def __init__(self, sense_text):
        """
        从故事感总纲文本中解析出结构化的故事弧
        
        sense_text: 一条完整的【故事感总纲N：XXX】文本
        """
        self.sense_text = sense_text
        self.beats = self._parse_beats()
        self.emotion_curve = [b.emotion_value for b in self.beats]
    
    def _parse_beats(self):
        """解析总纲文本为结构化的节拍序列"""
        text = self.sense_text
        
        # 提取标题
        title_match = re.search(r'【故事感总纲\d+：([^】]+)】', text)
        self.title = title_match.group(1) if title_match else "未知"
        
        # 提取一句话核心
        core_match = re.search(r'一句话核心：([^\n]+)', text)
        self.core = core_match.group(1).strip() if core_match else ""
        
        # 提取情感节奏行
        rhythm_match = re.search(r'情感节奏：([^\n]+)', text)
        rhythm_text = rhythm_match.group(1).strip() if rhythm_match else ""
        
        # 解析情感节奏
        beats = []
        if rhythm_text:
            parts = rhythm_text.split("→")
            for i, part in enumerate(parts):
                part = part.strip()
                # 格式如 "开场-平稳" 或 "开场-压抑微痛"
                segments = part.split("-", 1)
                beat_name = segments[0].strip() if len(segments) > 0 else f"节拍{i+1}"
                emotion_words = segments[1].strip() if len(segments) > 1 else "中性"
                
                # 计算情绪值
                emotion_val = self._emotion_to_value(emotion_words)
                
                # 根据位置确定节奏和强度
                total = len(parts)
                progress = i / max(total - 1, 1)
                
                if progress < 0.15:
                    pace = "medium"
                    intensity = 0.3 + emotion_val * 0.4
                elif progress < 0.35:
                    pace = "medium"
                    intensity = 0.4 + emotion_val * 0.3
                elif progress < 0.55:
                    pace = "slow" if emotion_val < 0.3 else "medium"
                    intensity = 0.3 + emotion_val * 0.3
                elif progress < 0.7:
                    pace = "slow"
                    intensity = 0.2 + emotion_val * 0.2
                elif progress < 0.85:
                    pace = "fast"
                    intensity = 0.6 + emotion_val * 0.4
                else:
                    pace = "slow"
                    intensity = 0.4 + emotion_val * 0.4
                
                beat = StoryBeat(
                    name=beat_name,
                    emotion_value=emotion_val,
                    pace=pace,
                    intensity=min(intensity, 1.0),
                    narrative_func=emotion_words,
                    duration_range=CinematographyDirector.get_duration_range(pace, min(intensity, 1.0), progress),
                    camera_style=CinematographyDirector.get_camera_directive(min(intensity, 1.0), pace, "")[0],
                )
                beats.append(beat)
        
        # 提取情节结构步骤
        self.story_steps = self._extract_story_steps()
        
        return beats
    
    def _extract_story_steps(self):
        """提取情节结构的步骤描述
        
        [P0修复] 原正则 r'\\d+\\.\\s*(.+?)(?::|$)' 只能匹配半角冒号，
        但故事感总纲使用的是全角冒号 '：'（U+FF1A），导致步骤解析全部失败。
        修复为同时匹配半角冒号 ':' 和全角冒号 '：'。
        """
        steps = []
        for line in self.sense_text.split('\n'):
            line = line.strip()
            # 同时匹配半角冒号(:)和全角冒号(：)
            match = re.match(r'\d+\.\s*(.+?)(?:[:：]|$)', line)
            if match:
                steps.append(match.group(1).strip())
        return steps
    
    def _emotion_to_value(self, word_text):
        """将中文情绪描述转为数值"""
        words = word_text.split("/")
        values = []
        for w in words:
            w = w.strip()
            if w in EMOTION_MAP:
                values.append(EMOTION_MAP[w])
            else:
                # 拆字匹配
                for key, val in EMOTION_MAP.items():
                    if key in w:
                        values.append(val)
                        break
                else:
                    values.append(0.5)  # 默认中性
        if values:
            return sum(values) / len(values)
        return 0.5
    
    def get_beat_for_shot(self, shot_index, total_shots):
        """
        计算第N个镜头所属的节拍
        
        返回:
            dict: {name, emotion, pace, intensity, narrative_func, beat_progress}
        """
        if not self.beats or total_shots <= 0:
            return self._default_beat()
        
        progress = shot_index / max(total_shots, 1)
        beat_idx = min(int(progress * len(self.beats)), len(self.beats) - 1)
        beat = self.beats[beat_idx]
        
        # 节拍内的进度（用于微调）
        beat_start = beat_idx / len(self.beats)
        beat_end = (beat_idx + 1) / len(self.beats)
        if beat_end - beat_start > 0:
            beat_progress = (progress - beat_start) / (beat_end - beat_start)
        else:
            beat_progress = 0.5
        
        # 如果是倒数几个beat，标记为"结尾阶段"
        is_final = (beat_idx >= len(self.beats) - 2)
        
        # 推荐的景别（根据情绪和强度）
        recommended_shot_types = self._recommend_shot_type(beat, beat_idx, shot_index)
        
        # 情绪描述（中文转英文标签）
        emotion_tags = self._emotion_tags(beat.narrative_func)
        
        # 影视语言指导（时长/运镜/转场）
        dur = beat.duration_range
        dur_hint = f"{dur[0]}-{dur[1]}秒"
        camera_text, camera_reason = CinematographyDirector.get_camera_directive(
            beat.intensity, beat.pace, "")
        # 转场：根据是否为首镜/末镜/节拍边界来决定
        is_first = (shot_index == 0)
        is_last = (shot_index >= total_shots - 1)
        # 判断是否跨节拍（用前一镜头的 beat_idx 对比）
        prev_beat_idx = min(int(max(shot_index - 1, 0) / max(total_shots, 1) * len(self.beats)), len(self.beats) - 1)
        cross_beat = (prev_beat_idx != beat_idx) and (shot_index > 0)
        emotion_delta = abs(beat.emotion_value - self.beats[prev_beat_idx].emotion_value) if cross_beat else 0
        transition, trans_reason = CinematographyDirector.get_transition(
            beat, self.beats[prev_beat_idx] if cross_beat else beat,
            scene_changed=False, is_first_shot=is_first, is_last_shot=is_last,
            cross_beat=cross_beat, emotion_delta=emotion_delta,
        )
        
        cinematography = {
            "duration_hint": dur_hint,
            "duration_range": dur,
            "camera_movement": camera_text,
            "camera_reason": camera_reason,
            "transition": transition,
            "transition_reason": trans_reason,
        }
        
        return {
            "beat_name": beat.name,
            "beat_index": beat_idx,
            "total_beats": len(self.beats),
            "beat_progress": beat_progress,
            "story_progress": progress,
            "emotion_value": beat.emotion_value,
            "emotion_tags": emotion_tags,
            "pace": beat.pace,
            "intensity": beat.intensity,
            "narrative_func": beat.narrative_func,
            "is_final": is_final,
            "recommended_shot_types": recommended_shot_types,
            "cinematography": cinematography,
            "constraints": {
                "no_abstract_words": True,
                "use_visible_description": True,
                "emotion_target": beat.emotion_value,
            }
        }
    
    def _recommend_shot_type(self, beat, beat_idx, shot_index):
        """根据节拍推荐合适的景别"""
        intensity = beat.intensity
        
        if intensity < 0.25:
            return ["远景", "全景"]  # 低强度用远景表现孤独/渺小
        elif intensity < 0.45:
            return ["全景", "中景"]  # 中低强度
        elif intensity < 0.65:
            return ["中景", "近景"]  # 中等强度
        elif intensity < 0.85:
            return ["近景", "特写"]  # 高强度用近景/特写
        else:
            return ["特写", "极特写"]  # 极致情绪
    
    def _emotion_tags(self, func_text):
        """将情绪描述转为英文标签"""
        tags = []
        for cn, en in EMOTION_EN_MAP.items():
            if cn in func_text:
                tags.append(en)
        if not tags:
            tags.append("neutral")
        return tags
    
    def _default_beat(self):
        return {
            "beat_name": "开场",
            "beat_index": 0,
            "total_beats": 1,
            "beat_progress": 0.5,
            "story_progress": 0.0,
            "emotion_value": 0.5,
            "emotion_tags": ["neutral"],
            "pace": "medium",
            "intensity": 0.5,
            "narrative_func": "开场建立情境",
            "is_final": False,
            "recommended_shot_types": ["全景", "中景"],
            "constraints": {"no_abstract_words": True, "use_visible_description": True, "emotion_target": 0.5},
        }
    
    def to_text(self, shot_index=None, total_shots=None):
        """生成用于prompt的总纲文本"""
        text_parts = [self.sense_text]
        
        if shot_index is not None and total_shots is not None:
            beat = self.get_beat_for_shot(shot_index, total_shots)
            text_parts.append(
                f"\n【当前镜头叙事信息】\n"
                f"这是第{shot_index+1}/{total_shots}个镜头\n"
                f"当前故事节拍：{beat['beat_name']}（第{beat['beat_index']+1}/{beat['total_beats']}段）\n"
                f"情绪目标：{beat['emotion_value']:.2f}（{', '.join(beat['emotion_tags'])}）\n"
                f"节奏：{beat['pace']} | 视觉强度：{beat['intensity']:.2f}\n"
                f"叙事功能：{beat['narrative_func']}\n"
                f"推荐景别：{'/'.join(beat['recommended_shot_types'])}\n"
            )
            if beat['is_final']:
                text_parts.append("【注意】这是结尾阶段的镜头，画面应具有收束感和余韵。\n")
        
        return "\n".join(text_parts)


class ShotConstraints:
    """镜头连续性约束 — 在逐镜头生成时维护状态"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.shot_count = 0
        self.last_shot_type = None
        self.shot_type_history = []
        self.last_duration = None
        self.duration_history = []      # [新增] 时长历史
        self.total_duration = 0.0       # [新增] 累计总时长（秒）
        self.last_camera = None
        self.camera_history = []        # [新增] 运镜历史
        self.last_transition = None
        self.transition_history = []    # [新增] 转场历史
        self.last_characters = ""
        self.last_scene = ""
        self.scene_history = []         # [新增] 场景历史，用于检测场景切换
    
    def record_shot(self, shot_data):
        """记录一个已生成的镜头数据"""
        self.shot_count += 1
        if isinstance(shot_data, dict):
            st = shot_data.get("shot_type")
            if st:
                self.shot_type_history.append(st)
                self.last_shot_type = st
            
            dur = shot_data.get("duration")
            if dur:
                try:
                    dur_val = float(dur)
                    self.last_duration = dur_val
                    self.duration_history.append(dur_val)
                    self.total_duration += dur_val
                except (ValueError, TypeError):
                    pass
            
            cam = shot_data.get("camera")
            if cam:
                self.last_camera = cam
                self.camera_history.append(cam)
            
            trans = shot_data.get("transition")
            if trans:
                self.last_transition = trans
                self.transition_history.append(trans)
            
            chars = shot_data.get("characters")
            if chars:
                self.last_characters = chars
            
            scene = shot_data.get("scene")
            if scene:
                self.last_scene = scene
                self.scene_history.append(scene)
    
    def is_scene_changed(self, current_scene_text=""):
        """根据最新记录判断是否发生场景变化"""
        if not self.scene_history:
            return False
        if not current_scene_text:
            return False
        # 简单字面差异：若新场景文本不为空且与最后一次记录差异大，则视为切换
        last = self.scene_history[-1]
        return current_scene_text.strip() != last.strip()
    
    def get_constraints_text(self):
        """生成对下一镜头的约束文本"""
        parts = []
        
        # 景别交替约束
        recent = self.shot_type_history[-3:]
        if len(recent) >= 3 and len(set(recent)) == 1:
            parts.append(f"【景别警告】最近3个镜头都是{recent[0]}，下一个镜头必须更换为不同的景别。")
        elif len(recent) >= 2 and len(set(recent)) == 1:
            parts.append(f"【提示】最近2个镜头都是{recent[0]}，建议下一个镜头切换景别。")
        
        # 时长节奏警告：连续3镜时长差异 < 1秒 → 节奏过于均匀
        recent_dur = self.duration_history[-3:]
        if len(recent_dur) >= 3:
            d_max = max(recent_dur)
            d_min = min(recent_dur)
            if (d_max - d_min) < 1.0:
                parts.append(
                    f"【节奏警告】近3个镜头时长过于均匀（{recent_dur}），"
                    f"建议下一个镜头使用明显不同的时长，制造节奏对比（短促紧张 vs 沉稳留白）。"
                )
        
        # 运镜交替警告：连续2镜相同运镜
        recent_cam = self.camera_history[-2:]
        if len(recent_cam) >= 2 and recent_cam[0] == recent_cam[1]:
            parts.append(
                f'【运镜提示】最近2个镜头运镜都是"{recent_cam[0]}"，'
                f"建议下一镜更换运镜方式（如固定→推/拉、推→摇、跟拍→静止），增加视觉变化。"
            )
        
        # 转场重复警告
        recent_trans = self.transition_history[-3:]
        if len(recent_trans) >= 3 and len(set(recent_trans)) == 1:
            parts.append(
                f'【转场提示】最近3个镜头转场都是"{recent_trans[0]}"，'
                f"建议变换转场方式（硬切/叠化/淡入淡出/匹配剪辑）以丰富叙事语法。"
            )
        
        # 时长参考
        if self.last_duration:
            parts.append(f"【参考】上一个镜头时长为{self.last_duration}秒。")
        
        # 运镜参考
        if self.last_camera:
            parts.append(f'【参考】上一个镜头运镜方式为"{self.last_camera}"。')
        
        # 转场参考
        if self.last_transition:
            parts.append(f'【参考】上一个镜头转场为"{self.last_transition}"。')
        
        # 时间线显示
        if self.total_duration > 0:
            mm = int(self.total_duration // 60)
            ss = int(self.total_duration % 60)
            time_str = f"{mm}分{ss:02d}秒" if mm > 0 else f"{ss}秒"
            parts.append(f"【时间线】已生成{self.shot_count}个镜头，累计约 {time_str}。")
        
        # 角色一致性
        if self.last_characters:
            parts.append(f"【角色一致性】上一个镜头的角色描述：{self.last_characters[:100]}。本镜头需保持角色外貌、服装、状态一致，除非有明确的变化交代。")
        
        # 场景连续性
        if self.last_scene:
            parts.append(f"【场景连续性】上一个镜头的场景：{self.last_scene[:100]}。场景变化时请明确标注。")
        
        return "\n".join(parts)
    
    def get_shot_index_display(self):
        return f"第{self.shot_count+1}个镜头"


class PromptSegmenter:
    """输出分割器 — 将一批镜头的输出切分为独立的段"""
    
    SEGMENT_SEPARATOR = "===SEGMENT_BREAK==="
    SHOT_SEPARATOR = "===SHOT_SEPARATOR==="
    
    @classmethod
    def join_outputs(cls, segments):
        """将多个独立输出拼接为一个批次"""
        return cls.SEGMENT_SEPARATOR.join(segments)
    
    @classmethod
    def split_output(cls, combined_text):
        """将批次输出拆分为独立段"""
        if not combined_text:
            return []
        parts = combined_text.split(cls.SEGMENT_SEPARATOR)
        return [p.strip() for p in parts if p.strip()]
