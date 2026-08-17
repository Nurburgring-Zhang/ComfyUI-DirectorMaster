# -*- coding: utf-8 -*-
"""
VfxPro - VFX特效专家节点 (环节 33) — L5 导演级深度重写
====================================================
VFX = Visual Effects (视觉特效)

真正的VFX专家节点, 不是复制粘贴模板:
1. VFX类型决策树: 粒子(火/烟/雨/雪/火花) + 流体(水/血/油) + 破碎(玻璃/混凝土/金属) + 光效(魔法/科技/自然)
2. 物理正确性检查: 重力/碰撞响应/无悬浮元素/材质受力行为
3. 导演VFX哲学: 诺兰(实拍优先) vs 沃卓斯基(子弹时间) vs 扎克(速度渐变) vs del Toro(有机VFX)
4. 合成工作流: 前景->中景->背景->粒子层->光效层 的分层描述
5. 质量指标: 分辨率/渲染通道/噪声阈值
"""

import os
import sys
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import (
        DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5, SILENCE_MASTERY_5,
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

# Phase 17.6: 灵魂注入
try:
    from director_soul import soul_inject_simple, EMOTION_MATRIX_60
    _HAS_SOUL = True
except Exception:
    _HAS_SOUL = False

# 导演数据中枢
try:
    from director_data_unified import (
        DIRECTOR_PROFILES_35, DIRECTOR_PROFILES_ALL, get_director_profile, SCENE_DATABASE_100, QUOTES_30,
        get_director, get_scene,
    )
    _HAS_DIRECTOR_DATA = True
except Exception:
    _HAS_DIRECTOR_DATA = False


GENRE_TYPES = ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]
DIRECTORS_20 = ["塔可夫斯基", "王家卫", "诺兰", "小津安二郎", "侯孝贤", "是枝裕和", "黑泽明", "库布里克", "伯格曼", "贾樟柯", "奉俊昊", "李安", "蔡明亮", "李沧东", "毕赣", "Vince Gilligan", "大衛·芬奇", "周星驰", "Papi酱", "诺兰_短剧版"]
TASK_TYPES = ["T2VA (文生视频, 无参考图)", "I2VA (图生视频, 1 张首帧)", "FL2VA (首尾帧, 2 张)", "L2VA (尾帧, 1 张)"]

# ============================================================
# VFX 类型决策树 (5大类, 每类含子系统参数)
# ============================================================
VFX_DECISION_TREE = {
    "粒子 (Particle)": {
        "fire": {
            "desc": "火焰粒子系统",
            "params": "color_temp=1800-6500K, turbulence=0.3-0.8, ember_count=50-500, flame_height=0.5-3m",
            "physics": "热气上升 buoyancy, 火焰根部蓝(高温)->尖端橙红(低温), 烟从火焰顶部脱离",
            "common_error": "AI常画出均匀橙色火焰, 缺少蓝色根部和不规则闪烁",
            "sound_design": "low crackle + occasional pop + wind interaction",
        },
        "smoke": {
            "desc": "烟雾粒子系统",
            "params": "density=0.1-0.9, dissipation_rate=2-15s, wind_speed=0-5m/s, color=white/gray/black",
            "physics": "烟先上升(热), 逐渐横移(风), 最终消散(扩散). 密度随距离源头递减",
            "common_error": "AI烟雾太均匀, 缺少湍流中的涡旋和撕裂",
            "sound_design": "near-silent, but camera can hear fire source",
        },
        "rain": {
            "desc": "雨粒子系统",
            "params": "angle=0-30deg_from_vertical, intensity=light/medium/heavy/torrential, splash_radius=2-8mm",
            "physics": "终端速度9m/s, 雨滴5mm以上分裂, 落地溅射高度=落速函数, 积水反射",
            "common_error": "AI雨粒大小均匀, 忽略风向导致的倾斜角度",
            "sound_design": "individual drops on surfaces -> merged white noise at high intensity",
        },
        "snow": {
            "desc": "雪粒子系统",
            "params": "drift_angle=0-45deg, accumulation_rate=0.5-5cm/h, melt_speed_on_skin=2-5s",
            "physics": "雪花飘落速度1-2m/s, 受微风扰动做布朗运动, 落地后积累(不弹跳)",
            "common_error": "AI雪花旋转太规律, 缺少乱流导致的不规则路径",
            "sound_design": "near-silent fall, soft crunch underfoot, muffled ambience",
        },
        "sparks": {
            "desc": "火花粒子系统",
            "params": "velocity=5-20m/s, lifespan=0.3-2s, bounce_coefficient=0.3-0.6, color=orange-white",
            "physics": "抛物线轨迹, 碰撞地面后反弹(能量衰减), 越小越快熄灭",
            "common_error": "AI火花轨迹太直, 缺少重力弧线和碰撞后的方向变化",
            "sound_design": "sharp metallic ping, diminishing tinkle",
        },
    },
    "流体 (Fluid)": {
        "water": {
            "desc": "水流体模拟",
            "params": "surface_tension=0.072N/m, viscosity=1cP, foam_threshold=velocity>2m/s",
            "physics": "受重力驱动, 表面张力导致弯月面, 高速碰撞产生飞溅和泡沫, IOR=1.33",
            "common_error": "AI水面太光滑, 缺少微波纹(capillary waves)和飞溅碎片",
            "sound_design": "splash calibrated to volume: drip/pour/crash/roar",
        },
        "blood": {
            "desc": "血液流体模拟",
            "params": "viscosity=3-4cP(新鲜)->10+cP(凝固中), coagulation_onset=30-120s, splatter_pattern=arterial/drip/smear",
            "physics": "比水粘3-4倍, 鲜红(含氧)->暗红(脱氧), 干燥后边缘先变暗, 中心保持湿润更久",
            "common_error": "AI血液太鲜艳(番茄汁质感), 缺少粘稠流动和凝固过程",
            "sound_design": "wet impact, drip-drip rhythm on hard surface",
        },
        "oil": {
            "desc": "油类流体模拟",
            "params": "iridescence=thin_film_interference, flow_rate=slow(high_viscosity), surface=hydrophobic",
            "physics": "虹彩薄膜干涉(角度变色), 高粘度慢流, 不与水混合(浮在水面)",
            "common_error": "AI油的虹彩太规律, 缺少厚度变化导致的色带不均",
            "sound_design": "thick sluggish flow, no splash, quiet displacement",
        },
    },
    "破碎 (Destruction)": {
        "glass": {
            "desc": "玻璃破碎模拟",
            "params": "fracture_pattern=radial+concentric, shard_size=1mm-50mm, refraction_per_shard=IOR1.5",
            "physics": "径向裂纹从冲击点辐射, 同心圆裂纹连接径向裂纹, 碎片有棱角(非圆形), 每片折射光线",
            "common_error": "AI玻璃碎片太均匀, 缺少大小差异和冲击点附近的粉碎区",
            "sound_design": "initial crack -> cascade of tinkling shards -> settling silence",
        },
        "concrete": {
            "desc": "混凝土破碎模拟",
            "params": "dust_volume=impact_energy*0.3, rebar_bend_angle=15-45deg, chunk_size=fist-to-boulder",
            "physics": "先裂(应力线), 再碎(块状脱落), 钢筋露出并弯曲, 大量粉尘(灰色)",
            "common_error": "AI混凝土碎得太干净, 缺少粉尘云和钢筋暴露",
            "sound_design": "deep thud + cracking + rumble of falling debris + dust hiss",
        },
        "metal": {
            "desc": "金属变形/破碎模拟",
            "params": "deformation=plastic_yield->fracture, spark_generation=friction_based, fragment_velocity=high",
            "physics": "金属先变形(弯曲/凹陷)再断裂, 断裂面有金属光泽, 摩擦产生火花",
            "common_error": "AI金属碎得像陶瓷(脆断), 缺少弯曲变形阶段",
            "sound_design": "screech of bending metal + impact ring + spark crackle",
        },
    },
    "光效 (Light FX)": {
        "magic": {
            "desc": "魔法光效",
            "params": "glow_radius=0.5-3m, particle_trail_length=0.5-2s, color_shift=hue_rotate_30deg/s",
            "physics": "非物理: 但需要内在逻辑一致性, 如'蓝=冰/紫=暗/金=圣'",
            "common_error": "AI魔法光效太均匀发光, 缺少中心亮->边缘暗的衰减梯度",
            "sound_design": "ethereal hum + crystalline chime + subsonic pulse",
        },
        "technology": {
            "desc": "科技光效 (全息/扫描线/闪烁)",
            "params": "hologram_opacity=0.3-0.7, scan_line_spacing=2-5px, flicker_frequency=50-60Hz",
            "physics": "全息: 半透明+边缘色差+偶尔闪烁/刷新; 扫描: 从上到下或从左到右",
            "common_error": "AI全息图太实体化, 缺少透明度变化和边缘RGB分离",
            "sound_design": "electronic hum + data chirp + occasional static burst",
        },
        "natural": {
            "desc": "自然光效 (丁达尔/极光/闪电)",
            "params": "god_rays: sun_angle=15-30deg + atmospheric_dust; aurora: altitude=100-300km + solar_wind; lightning: duration=0.1-0.5s + branch_count=3-12",
            "physics": "丁达尔: 光被粒子散射, 需要可见灰尘/雾; 极光: 太阳风激发高层大气, 绿(氧100km)/红(氧200km)/紫(氮); 闪电: 主通道+分支, 从云到地或云到云",
            "common_error": "AI丁达尔光线太均匀, 缺少灰尘密度变化导致的强弱不一",
            "sound_design": "god_rays: silence (visual only); aurora: none; lightning: crack-boom with distance delay",
        },
    },
    "合成 (Compositing)": {
        "layer_stack": {
            "desc": "合成分层工作流",
            "params": "foreground(character) -> midground(props/set) -> background(sky/environment) -> particle_layer -> light_fx_layer",
            "physics": "每层独立深度, 近层遮挡远层, 粒子层在所有实体层之上但在光效层之下",
            "common_error": "AI合成时前后景深度不一致, 粒子穿过实体物体",
            "sound_design": "each layer contributes to sound mix independently",
        },
        "matte_painting": {
            "desc": "数字绘景",
            "params": "resolution=min_4K, perspective_match=camera_lens_data, atmosphere=depth_fog_gradient",
            "physics": "远处物体: 色彩饱和度降低, 对比度降低, 偏蓝(大气散射)",
            "common_error": "AI绘景与实拍前景的透视消失点不一致",
            "sound_design": "distant ambient matched to painted environment",
        },
    },
}

# ============================================================
# 物理正确性检查清单
# ============================================================
PHYSICS_CHECKLIST = {
    "gravity": {
        "realistic": "9.8 m/s^2, terminal velocity for objects, parabolic projectile paths",
        "stylized": "scaled to 50-150% of real gravity for dramatic effect",
        "exaggerated": "200-500% or near-zero for cartoon/anime physics",
        "rule": "CRITICAL: no floating elements without explicit anti-gravity justification",
    },
    "collision": {
        "response": "equal and opposite force, deformation proportional to material softness",
        "debris_scatter": "radial from impact point, velocity decreases with mass, small pieces travel further",
        "rule": "every collision produces: deformation + sound + secondary particles (dust/sparks/splash)",
    },
    "material_under_force": {
        "brittle": "glass/ceramic/ice: crack pattern -> shatter -> no deformation before break",
        "ductile": "metal/plastic: deform (bend/stretch) -> neck -> fracture at weakest point",
        "soft": "flesh/cloth/rubber: deform elastically, return to shape (or not), no shattering",
        "rule": "material response must match its real-world category",
    },
    "anti_float": {
        "desc": "严格反悬浮规则: 除非有明确的力(磁力/风力/魔法)支撑, 所有物体必须受重力约束",
        "check": "review each frame: is anything floating without justification?",
        "fix": "add shadow underneath, add support structure, or add force field visual",
    },
    "scale_consistency": {
        "desc": "VFX元素的大小必须与环境一致",
        "check": "particle size vs human reference, explosion radius vs building scale",
        "rule": "use human figure or known object as scale reference in every VFX shot",
    },
}

# ============================================================
# 导演VFX哲学
# ============================================================
DIRECTOR_VFX_PHILOSOPHY = {
    "诺兰": {
        "principle": "实拍优先, CGI只用在不可能实拍的地方, 且必须让观众分不出来",
        "method": "先用微缩模型/实际爆破, 再用CGI增强细节, 从不用纯CGI替代可实拍内容",
        "signature_vfx": "时间操控(慢动作/快进混剪), 实拍旋转走廊(《盗梦空间》), 真实爆炸(《信条》翻转747)",
        "restraint": "VFX应该是隐形的: 观众不应该注意到VFX的存在",
        "anti_pattern": "拒绝: 纯CGI环境, 过度粒子效果, 任何'看起来像CGI'的东西",
    },
    "沃卓斯基": {
        "principle": "VFX是叙事语言, 不是装饰, 每个VFX都有哲学含义",
        "method": "子弹时间=时间的主观性; 数字雨=现实的代码本质; 虚拟摄像机=超越物理限制",
        "signature_vfx": "bullet time(120台相机环形阵列+插值), virtual camera(完全CG环境中自由运动), code rain",
        "restraint": "VFX可以夸张, 但必须服务于'什么是真实'这个核心问题",
        "anti_pattern": "拒绝: 无意义的炫技, 与主题无关的特效场面",
    },
    "扎克·斯奈德": {
        "principle": "速度渐变(speed ramp)是情绪的控制器: slow->fast->slow",
        "method": "300fps超慢动作捕捉动作高光->正常速度推进->再次慢动作强调结果",
        "signature_vfx": "speed ramp, desaturated color palette(近黑白+单色强调), 粒子化的血/沙",
        "restraint": "慢动作不是因为'酷', 是因为这一刻值得观众仔细看",
        "anti_pattern": "拒绝: 均匀速度的动作, 没有节奏变化的打斗",
    },
    "吉尔莫·德尔·托罗": {
        "principle": "VFX的最高境界是让不存在的生物看起来有生命",
        "method": "先做实体模型(确保触感/重量/光响应), 再用CGI让它动起来",
        "signature_vfx": "有机生物设计(《潘神的迷宫》眼手怪), 机甲质感(《环太平洋》), 水下生物光(《水形物语》)",
        "restraint": "每个怪物都有解剖学逻辑: 骨骼/肌肉/皮肤层次",
        "anti_pattern": "拒绝: 没有重量感的CGI生物, 太光滑/太完美的数字角色",
    },
    "是枝裕和": {
        "principle": "几乎不用VFX, 真实即最好的特效",
        "method": "如果需要雨: 等真正下雨; 如果需要光: 等自然光到位",
        "signature_vfx": "无 (这本身就是一种VFX哲学: 节制)",
        "restraint": "VFX = 0 是最高境界, 真实世界的不完美就是最好的视觉效果",
        "anti_pattern": "拒绝: 任何可被观众察觉的人工干预",
    },
    "黑泽明": {
        "principle": "自然力(雨/风/火)是最好的VFX, 用规模感创造史诗感",
        "method": "真实火箭燃烧箭矢, 人工造雨(消防车), 大量临时演员创造群像",
        "signature_vfx": "暴雨中的战斗(《七武士》), 烈焰城堡(《乱》), 梦境色彩(《梦》)",
        "restraint": "VFX的核心是规模, 不是精细度",
        "anti_pattern": "拒绝: 小气的特效, 看起来像是在省预算",
    },
    "王家卫": {
        "principle": "VFX是时间的视觉化: step-printing, 曝光拖影, 颜色偏移",
        "method": "光学效果(滤镜/曝光控制)优先于数字VFX, 霓虹反射=城市的呼吸",
        "signature_vfx": "step-printing(跳帧重复=时间凝滞), 霓虹反射在雨水中的色彩溶解, 慢动作+失焦",
        "restraint": "VFX只服务于时间感和孤独感的表达",
        "anti_pattern": "拒绝: 爆炸/战斗/任何'大场面'VFX",
    },
    "奉俊昊": {
        "principle": "VFX减到最低, 只在叙事绝对需要时使用(如怪物)",
        "method": "《汉江怪物》: CGI怪物在实景中, 确保光影与环境完全匹配",
        "signature_vfx": "写实CGI生物(与实景无缝融合), 大规模环境增强(列车/地下室延伸)",
        "restraint": "VFX越少越好, 但用的时候必须无缝",
        "anti_pattern": "拒绝: 过度CGI环境, 'Marvel式'全绿幕制作",
    },
}

# ============================================================
# 复杂度等级定义
# ============================================================
COMPLEXITY_LEVELS = {
    "L1_简单": {
        "desc": "单一VFX类型, 无交互, 短时间",
        "example": "一缕烟从烟囱升起; 窗外下雨",
        "render_budget": "单层粒子, 无模拟, 实时可渲染",
        "shot_count": "1-2 shots with VFX",
    },
    "L2_中等": {
        "desc": "2种VFX类型交互, 中等持续时间",
        "example": "雨天街道上的霓虹灯反射; 蜡烛火焰在风中摇曳产生烟",
        "render_budget": "2-3层粒子, 简单流体, 近实时",
        "shot_count": "3-4 shots with VFX",
    },
    "L3_复杂": {
        "desc": "多种VFX类型交互+环境影响",
        "example": "暴风雨中房屋部分坍塌, 碎片+雨+闪电+尘土",
        "render_budget": "多层粒子+流体+刚体模拟, 非实时",
        "shot_count": "5-8 shots with VFX",
    },
    "L4_极复杂": {
        "desc": "全场景VFX+角色交互+物理模拟",
        "example": "水下战斗+气泡+光线折射+水面波纹+角色头发/衣物流体",
        "render_budget": "全流体模拟+布料+毛发+光线追踪, 长时间渲染",
        "shot_count": "8-15 shots with VFX",
    },
    "L5_电影级": {
        "desc": "顶级电影VFX: 多系统耦合+照片级真实",
        "example": "城市级别破碎+海啸+火灾+救援+人群+天气系统",
        "render_budget": "全物理模拟+Monte Carlo光追+数万核渲染, 每帧数小时",
        "shot_count": "15+ shots with VFX, continuous VFX presence",
    },
}

# ============================================================
# 合成工作流 (分层描述模板)
# ============================================================
COMPOSITING_LAYERS = {
    "foreground": {
        "content": "角色/主体",
        "render_passes": ["beauty", "diffuse", "specular", "SSS", "shadow", "AO"],
        "rule": "主体必须有完整的光照通道, 用于与VFX层的光照匹配",
    },
    "midground": {
        "content": "道具/近景环境",
        "render_passes": ["beauty", "shadow", "reflection", "AO"],
        "rule": "中景物体的反射必须包含VFX元素(火光反射在金属道具上)",
    },
    "background": {
        "content": "远景/天空/绘景",
        "render_passes": ["beauty", "depth", "atmosphere"],
        "rule": "背景通过 depth fog 与前景分离, 大气散射导致远处偏蓝",
    },
    "particle_layer": {
        "content": "粒子系统(火/烟/雨/雪/碎片)",
        "render_passes": ["beauty", "alpha", "motion_vector", "depth"],
        "rule": "粒子层必须有正确的深度排序, 近处粒子遮挡远处物体, 远处粒子被近处物体遮挡",
    },
    "light_fx_layer": {
        "content": "光效/辉光/体积光/镜头光晕",
        "render_passes": ["beauty", "alpha", "glow"],
        "rule": "光效层在最顶部, 使用additive blend, 不遮挡但影响整体色调",
    },
}


class VfxPro:
    """
    VFX特效专家节点 (环节 33) — L5 导演级
    真正的VFX设计系统: 特效类型决策树 + 物理正确性 + 导演VFX哲学 + 合成工作流
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "任务类型": (TASK_TYPES, {"default": "T2VA (文生视频, 无参考图)"}),
                "类型": (["自动"] + GENRE_TYPES, {"default": "电影"}),
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边"}),
                "导演风格": (DIRECTORS_20, {"default": "是枝裕和"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望, 说不清但有重量"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸, 想靠近又怕伤害"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机 / 缝纫机"}),
                "关键参考片": ("STRING", {"default": "《花样年华》色调 / 《一一》节奏 / 《步履不停》家庭"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),

                # === Phase 17.6 灵魂注入 ===
                "灵魂_主导情感": (["auto"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "auto"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_次要情感": (["none"] + (sorted(EMOTION_MATRIX_60.keys()) if _HAS_SOUL else ["loneliness"]), {"default": "none"}),
                "灵魂_融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
                                  "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"],
                                 {"default": "auto"}),

                # === VFX 专属字段 ===
                "特效类型": (["粒子 (Particle)", "流体 (Fluid)", "破碎 (Destruction)", "光效 (Light FX)", "合成 (Compositing)", "无特效", "auto"], {"default": "auto"}),
                "物理精度": (["写实 (Physically Accurate)", "风格化 (Stylized)", "夸张 (Exaggerated)", "auto"], {"default": "auto"}),
                "复杂度": (["L1_简单", "L2_中等", "L3_复杂", "L4_极复杂", "L5_电影级", "auto"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("vfxpro_h3_prompt", "experience_matrix", "ai_deep_processing")
    FUNCTION = "build_vfx"
    CATEGORY = "PromptLibrary/L5 导演级"

    def build_vfx(self, **kwargs):
        if not _HAS_AI_DEPS:
            return ("未加载: " + _AI_DEPS_ERROR, "", "")

        # 提取用户输入
        _str = lambda kwargs_ref, k, d="": str(kwargs_ref.get(k, d)) if kwargs_ref.get(k) is not None else d

        task_type_full = _str(kwargs, "任务类型", "T2VA (文生视频, 无参考图)")
        task_type = task_type_full.split(" ")[0]
        genre = _str(kwargs, "类型", "电影")
        scene = _str(kwargs, "场景描述", "")
        director = _str(kwargs, "导演风格", "是枝裕和")
        mood = _str(kwargs, "情绪基调", "")
        subtext = _str(kwargs, "潜文本_情感", "")
        intent_feel = _str(kwargs, "导演意图_观众应感到", "")
        props_raw = _str(kwargs, "关键道具", "")
        ref_films = _str(kwargs, "关键参考片", "")
        anti_ai_on = bool(kwargs.get("启用反AI规则", True))
        vfx_type_choice = _str(kwargs, "特效类型", "auto")
        physics_choice = _str(kwargs, "物理精度", "auto")
        complexity_choice = _str(kwargs, "复杂度", "auto")

        # ----------------------------------------------------------
        # 1. 查询导演真实档案 (director_data_unified)
        # ----------------------------------------------------------
        director_profile = {}
        director_scenes = []
        if _HAS_DIRECTOR_DATA:
            director_profile = get_director(director)
            for s in SCENE_DATABASE_100:
                if s.get("director") == director:
                    director_scenes.append(s)

        dir_color = director_profile.get("色彩", "自然色调")
        dir_light = director_profile.get("光", "自然光")
        dir_mood = director_profile.get("情绪", "中性")

        # ----------------------------------------------------------
        # 2. VFX类型自动推断 (从场景描述中检测VFX关键词)
        # ----------------------------------------------------------
        if vfx_type_choice == "auto":
            vfx_keyword_map = {
                "粒子 (Particle)": ["火", "烟", "雨", "雪", "火花", "fire", "smoke", "rain", "snow", "sparks", "灰烬", "尘", "蜡烛"],
                "流体 (Fluid)": ["水", "血", "油", "海", "河", "泪", "water", "blood", "flood", "wave", "ocean", "泥"],
                "破碎 (Destruction)": ["破碎", "爆炸", "坍塌", "碎", "裂", "break", "explode", "collapse", "shatter", "摧毁"],
                "光效 (Light FX)": ["魔法", "光", "闪电", "极光", "全息", "magic", "glow", "lightning", "hologram", "霓虹"],
                "合成 (Compositing)": ["合成", "绿幕", "绘景", "composite", "CG", "CGI"],
            }
            vfx_type_choice = "无特效"  # default to no VFX
            combined_text = scene + " " + mood + " " + props_raw
            for vfx_label, kws in vfx_keyword_map.items():
                for kw in kws:
                    if kw in combined_text:
                        vfx_type_choice = vfx_label
                        break
                if vfx_type_choice != "无特效":
                    break
            # 如果场景有'雨'字, 默认粒子
            if vfx_type_choice == "无特效" and "雨" in scene:
                vfx_type_choice = "粒子 (Particle)"

        # ----------------------------------------------------------
        # 3. 物理精度自动推断 (基于导演和类型)
        # ----------------------------------------------------------
        if physics_choice == "auto":
            physics_map = {
                "诺兰": "写实 (Physically Accurate)",
                "是枝裕和": "写实 (Physically Accurate)",
                "奉俊昊": "写实 (Physically Accurate)",
                "黑泽明": "写实 (Physically Accurate)",
                "周星驰": "夸张 (Exaggerated)",
                "宫崎骏": "风格化 (Stylized)",
                "毕赣": "风格化 (Stylized)",
                "王家卫": "风格化 (Stylized)",
            }
            physics_choice = physics_map.get(director, "写实 (Physically Accurate)")
            # 短视频/MV 更风格化
            if genre in ("短视频", "AIGC 短视频", "MV"):
                physics_choice = "风格化 (Stylized)"
            elif genre == "故事绘本":
                physics_choice = "夸张 (Exaggerated)"

        # ----------------------------------------------------------
        # 4. 复杂度自动推断
        # ----------------------------------------------------------
        if complexity_choice == "auto":
            if vfx_type_choice == "无特效":
                complexity_choice = "L1_简单"
            elif genre in ("电影",):
                complexity_choice = "L3_复杂"
            elif genre in ("AIGC 短剧", "短视频", "AIGC 短视频"):
                complexity_choice = "L2_中等"
            else:
                complexity_choice = "L2_中等"

        complexity_data = COMPLEXITY_LEVELS.get(complexity_choice, COMPLEXITY_LEVELS["L2_中等"])

        # ----------------------------------------------------------
        # 5. 获取VFX子系统详情
        # ----------------------------------------------------------
        vfx_category = VFX_DECISION_TREE.get(vfx_type_choice, {})
        # 从场景描述中匹配具体VFX子类型
        detected_subtypes = []
        if vfx_category:
            for subtype_key, subtype_data in vfx_category.items():
                # 简单关键词匹配
                check_words = subtype_key.split("_") + [subtype_key]
                for cw in check_words:
                    if cw in scene.lower() or cw in mood.lower() or cw in props_raw.lower():
                        detected_subtypes.append((subtype_key, subtype_data))
                        break
            # 如果没有匹配到, 取第一个子类型
            if not detected_subtypes and vfx_category:
                first_key = list(vfx_category.keys())[0]
                detected_subtypes.append((first_key, vfx_category[first_key]))

        # 场景中的'雨'-> rain 子类型
        if vfx_type_choice == "粒子 (Particle)" and not detected_subtypes:
            if "雨" in scene:
                detected_subtypes.append(("rain", vfx_category.get("rain", {})))
            elif "火" in scene or "蜡烛" in scene:
                detected_subtypes.append(("fire", vfx_category.get("fire", {})))
            else:
                detected_subtypes.append(("rain", vfx_category.get("rain", {})))

        # ----------------------------------------------------------
        # 6. 导演VFX哲学
        # ----------------------------------------------------------
        director_vfx_data = DIRECTOR_VFX_PHILOSOPHY.get(director, {
            "principle": "VFX服务叙事, 不喧宾夺主",
            "method": "根据场景需要选择最克制的VFX方案",
            "signature_vfx": "导演风格决定VFX的存在感",
            "restraint": "VFX越少越好, 每一帧都要有存在的理由",
            "anti_pattern": "拒绝: 无叙事功能的纯视觉炫技",
        })

        # ----------------------------------------------------------
        # 7. 物理精度参数选择
        # ----------------------------------------------------------
        gravity_mode = "realistic"
        if "写实" in physics_choice:
            gravity_mode = "realistic"
        elif "风格化" in physics_choice:
            gravity_mode = "stylized"
        elif "夸张" in physics_choice:
            gravity_mode = "exaggerated"
        gravity_data = PHYSICS_CHECKLIST["gravity"][gravity_mode]

        # ----------------------------------------------------------
        # 8. 构建 H3 三字段 prompt (VFX版)
        # ----------------------------------------------------------
        style_choices = {
            "电影": "Cinematic, live-action, 35mm film grain",
            "AIGC 短剧": "Cinematic, live-action, high emotional rhythm",
            "短视频": "live-action, high saturation, direct",
            "MV": "Cinematic, music video, dolly shot",
            "故事绘本": "watercolor, soft palette",
            "互动剧": "Cinematic, live-action, immersive",
        }
        style = style_choices.get(genre, "Cinematic, live-action")

        # 导演镜头运动 (VFX场景专用)
        director_motion_map = {
            "诺兰": "Tracking Shot following the action, IMAX wide frame capturing full VFX scale",
            "是枝裕和": "Static Shot, the rain falls naturally outside the window, camera does not dramatize",
            "王家卫": "Push In with step-printing, VFX is the neon rain reflection, not explosions",
            "黑泽明": "Wide Shot epic scale, practical rain + practical fire, camera holds steady",
            "周星驰": "Quick Cut between exaggerated VFX gags, then hold on reaction shot",
            "奉俊昊": "Static to slow Push In, VFX creature enters frame naturally, no fanfare",
            "塔可夫斯基": "Static Shot ultra-long, watching rain collect in a puddle for 30 seconds",
            "毕赣": "Arc Shot continuous, VFX elements (rain/fog) exist in the periphery of the long take",
        }
        director_motion_pref = director_motion_map.get(director, "Static Shot + medium pace")

        # VFX子类型描述
        vfx_shot_desc = ""
        vfx_sound_desc = ""
        if detected_subtypes:
            primary_vfx = detected_subtypes[0]
            vfx_name = primary_vfx[0]
            vfx_data = primary_vfx[1]
            if isinstance(vfx_data, dict):
                vfx_shot_desc = (
                    "VFX element: " + vfx_name + " (" + vfx_data.get("desc", "") + "). "
                    + "Parameters: " + vfx_data.get("params", "") + ". "
                    + "Physics: " + vfx_data.get("physics", "") + "."
                )
                vfx_sound_desc = vfx_data.get("sound_design", "ambient integration")
            else:
                vfx_shot_desc = "VFX element: " + vfx_name + "."
                vfx_sound_desc = "ambient integration"
        else:
            vfx_shot_desc = "No VFX elements required. Natural scene."
            vfx_sound_desc = "natural ambient only"

        # Shot 1: 建立场景 + VFX环境
        shot_1 = (
            "a medium-wide shot establishes " + scene + ". "
            + director_motion_pref + ". "
            + vfx_shot_desc + " "
            + "Gravity mode: " + gravity_data + ". "
            + "Director VFX principle: " + director_vfx_data["principle"] + ". "
            + "The director intends: " + intent_feel + "."
        )

        # Build shots with VFX integration
        first_prop = props_raw.split(" / ")[0] if " / " in props_raw else props_raw
        last_prop = props_raw.split(" / ")[-1] if " / " in props_raw else props_raw

        shots = []

        # Shot 2: VFX元素引入 (物理正确)
        shots.append(
            "[Shot 2] At 00:04.000, " + format_shot_motion("Push In", "small", "slow")
            + " as the VFX element enters the frame. "
            + "Physics checklist: " + PHYSICS_CHECKLIST["anti_float"]["desc"] + ". "
            + "Complexity: " + complexity_choice + " (" + complexity_data["desc"] + "). "
            + "Common AI error to avoid: " + (detected_subtypes[0][1].get("common_error", "generic VFX") if detected_subtypes and isinstance(detected_subtypes[0][1], dict) else "none") + "."
        )

        # Shot 3: VFX与角色交互
        shots.append(
            "[Shot 3] At 00:09.000, the VFX element interacts with the character. "
            + "Material under force: " + PHYSICS_CHECKLIST["material_under_force"]["soft"] + ". "
            + "The " + first_prop + " responds to the VFX element (moved/lit/wet/damaged). "
            + "The character's face reveals " + subtext + "."
        )

        # Shot 4: VFX高潮 (导演风格处理)
        shots.append(
            "[Shot 4] At 00:15.000, VFX reaches peak intensity. "
            + "Director approach: " + director_vfx_data["method"] + ". "
            + "Anti-pattern: " + director_vfx_data["anti_pattern"] + ". "
            + "The " + mood + " is carried by the VFX rhythm, not by dialogue."
        )

        # Shot 5: VFX余波 + 合成层检查
        shots.append(
            "[Shot 5] At 00:22.000, VFX subsides. "
            + "Compositing layer check: foreground (character) intact, midground (" + first_prop + ") shows VFX aftermath, "
            + "background consistent with " + dir_color + " palette. "
            + "Particle layer properly depth-sorted. Light FX layer additive blend."
        )

        # Shot 6: 静寂 + 情感落点
        shots.append(
            "[Shot 6] At 00:27.000, static shot holds for 3 seconds. "
            + "All VFX elements have settled. The " + last_prop + " remains visible. "
            + "The silence after VFX is where " + intent_feel + ". End of shot."
        )

        soundscape = (
            "VFX sound: " + vfx_sound_desc + ". "
            + "Ambient: " + (director_scenes[0].get("sound", "environment") if director_scenes else "environment") + ". "
            + "Foley: character reaction sounds (breath catch, fabric rustle). "
            + "Rule: VFX sound intensity matches visual intensity, never louder."
        )
        music = (
            "Score responds to VFX rhythm: builds during VFX peak, drops to silence after. "
            + "Director-specific: " + director_profile.get("声音", "ambient") + "."
        )

        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese"
        )

        # 对齐指令
        alignment = build_alignment_instruction(task_type, n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # ----------------------------------------------------------
        # 9. 灵魂注入 (Phase 17.6)
        # ----------------------------------------------------------
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_scene_weight = float(kwargs.get("灵魂_场景权重", 0.5))
        soul_secondary_raw = kwargs.get("灵魂_次要情感", "none")
        soul_secondary = [soul_secondary_raw] if soul_secondary_raw and soul_secondary_raw not in ("none", "auto") else None
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")
        soul_header = ""
        if _HAS_SOUL:
            try:
                inj, fused, soul_state, soul_dims = soul_inject_simple(
                    primary=soul_primary,
                    scene_weight=soul_scene_weight,
                    secondary=soul_secondary,
                    fusion_mode=soul_fusion_mode,
                    scene_context=scene,
                )
                soul_header = (
                    "【灵魂核心 - VFX 特效驱动 (Phase 17.6)】\n"
                    "主导情感: " + str(fused.get("name", "")) + "\n"
                    "情感强度: " + "{:.2f}".format(float(fused.get("intensity", 0.5))) + "\n"
                    "情感极性: " + str(fused.get("polarity", "neutral")) + "\n"
                    "唤醒度: " + str(fused.get("arousal", "medium")) + "\n"
                    "════════════════════════════════════\n\n"
                )
            except Exception:
                soul_header = ""

        # ----------------------------------------------------------
        # 10. 组装主输出
        # ----------------------------------------------------------
        main_output = "=" * 60 + "\n"
        main_output += soul_header
        main_output += "【VfxPro】VFX特效专家节点 - L5 导演级\n"
        main_output += "=" * 60 + "\n\n"
        main_output += "【任务类型】 " + task_type + " (" + genre + ")\n"
        main_output += "【导演风格】 " + director + "\n"
        main_output += "【特效类型】 " + vfx_type_choice + "\n"
        main_output += "【物理精度】 " + physics_choice + "\n"
        main_output += "【复杂度】 " + complexity_choice + " - " + complexity_data["desc"] + "\n\n"

        # 导演档案
        if director_profile:
            main_output += "=" * 60 + "\n"
            main_output += "导演真实档案 (director_data_unified 35导演8维)\n"
            main_output += "=" * 60 + "\n"
            main_output += "  色彩: " + dir_color + "\n"
            main_output += "  光: " + dir_light + "\n"
            main_output += "  情绪: " + dir_mood + "\n"
            main_output += "  标志物件: " + director_profile.get("物件", "通用") + "\n\n"

        # 导演VFX哲学
        main_output += "=" * 60 + "\n"
        main_output += "导演VFX哲学 (" + director + ")\n"
        main_output += "=" * 60 + "\n"
        main_output += "  原则: " + director_vfx_data["principle"] + "\n"
        main_output += "  方法: " + director_vfx_data["method"] + "\n"
        main_output += "  标志VFX: " + director_vfx_data["signature_vfx"] + "\n"
        main_output += "  克制: " + director_vfx_data["restraint"] + "\n"
        main_output += "  禁忌: " + director_vfx_data["anti_pattern"] + "\n\n"

        # VFX决策树详情
        if detected_subtypes:
            main_output += "=" * 60 + "\n"
            main_output += "VFX决策树: 检测到的子系统\n"
            main_output += "=" * 60 + "\n"
            for st_name, st_data in detected_subtypes:
                if isinstance(st_data, dict):
                    main_output += "  [" + st_name + "] " + st_data.get("desc", "") + "\n"
                    main_output += "    参数: " + st_data.get("params", "") + "\n"
                    main_output += "    物理: " + st_data.get("physics", "") + "\n"
                    main_output += "    AI常见错误: " + st_data.get("common_error", "") + "\n"
                    main_output += "    声音设计: " + st_data.get("sound_design", "") + "\n"
            main_output += "\n"

        # 物理正确性检查
        main_output += "=" * 60 + "\n"
        main_output += "物理正确性检查清单\n"
        main_output += "=" * 60 + "\n"
        main_output += "  重力模式: " + gravity_mode + " -> " + gravity_data + "\n"
        main_output += "  碰撞响应: " + PHYSICS_CHECKLIST["collision"]["response"] + "\n"
        main_output += "  碎片散射: " + PHYSICS_CHECKLIST["collision"]["debris_scatter"] + "\n"
        main_output += "  反悬浮: " + PHYSICS_CHECKLIST["anti_float"]["desc"] + "\n"
        main_output += "  尺度一致: " + PHYSICS_CHECKLIST["scale_consistency"]["desc"] + "\n\n"

        # 合成工作流
        main_output += "=" * 60 + "\n"
        main_output += "合成工作流 (5层分层)\n"
        main_output += "=" * 60 + "\n"
        for layer_name, layer_data in COMPOSITING_LAYERS.items():
            passes_str = ", ".join(layer_data["render_passes"])
            main_output += "  [" + layer_name + "] " + layer_data["content"] + "\n"
            main_output += "    渲染通道: " + passes_str + "\n"
            main_output += "    规则: " + layer_data["rule"] + "\n"
        main_output += "\n"

        # H3 prompt
        main_output += "=" * 60 + "\n"
        main_output += "H3 三大字段 (VFX定制版)\n"
        main_output += "=" * 60 + "\n\n"
        main_output += h3_prompt + "\n\n"

        # 反 AI
        if anti_ai_on:
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ----------------------------------------------------------
        # 11. 第二输出: 经验矩阵
        # ----------------------------------------------------------
        experience = "【导演VFX哲学矩阵 (8位导演)】\n\n"
        for d_name, d_data in DIRECTOR_VFX_PHILOSOPHY.items():
            experience += "  " + d_name + ": " + d_data["principle"] + "\n"

        experience += "\n【VFX类型决策树 (5大类)】\n"
        for cat_name, cat_data in VFX_DECISION_TREE.items():
            sub_names = ", ".join(cat_data.keys())
            experience += "  " + cat_name + ": " + sub_names + "\n"

        experience += "\n【复杂度等级 (5级)】\n"
        for lvl_name, lvl_data in COMPLEXITY_LEVELS.items():
            experience += "  " + lvl_name + ": " + lvl_data["example"] + "\n"

        experience += "\n【合成分层工作流 (5层)】\n"
        for layer_name, layer_data in COMPOSITING_LAYERS.items():
            experience += "  " + layer_name + ": " + layer_data["content"] + "\n"

        experience += "\n【物理正确性 (5项检查)】\n"
        for check_name in PHYSICS_CHECKLIST.keys():
            experience += "  - " + check_name + "\n"

        experience += "\n【导演场景数据 (匹配 " + director + ")】\n"
        for ds in director_scenes[:5]:
            experience += "  - " + ds.get("scene", "") + ": " + ds.get("object", "") + " | " + ds.get("color", "") + "\n"

        # ----------------------------------------------------------
        # 12. 第三输出: AI 深度处理
        # ----------------------------------------------------------
        ai_deep_output = "【VFX AI 深度处理指令】\n\n"

        ai_deep_output += "【1. VFX物理正确性执行指令】\n"
        ai_deep_output += "  - 重力: " + gravity_data + "\n"
        ai_deep_output += "  - 每个VFX粒子/流体/碎片都必须服从重力(除非有反重力叙事理由)\n"
        ai_deep_output += "  - 碰撞: 每次碰撞必须产生 = 变形 + 声音 + 次级粒子\n"
        ai_deep_output += "  - 材质: 脆性(玻璃)裂而不弯, 韧性(金属)弯而不裂, 软性(布)变形不碎\n\n"

        ai_deep_output += "【2. VFX AI常见错误清单 (必须避免)】\n"
        if detected_subtypes:
            for st_name, st_data in detected_subtypes:
                if isinstance(st_data, dict):
                    ai_deep_output += "  [" + st_name + "] " + st_data.get("common_error", "N/A") + "\n"
        ai_deep_output += "  [通用] 不允许VFX元素穿透实体物体\n"
        ai_deep_output += "  [通用] 不允许无来源的光效(每个光必须有发光体)\n"
        ai_deep_output += "  [通用] 不允许VFX元素的尺度与环境不一致\n"
        ai_deep_output += "  [通用] 不允许均匀分布的粒子(真实物理总是不均匀的)\n\n"

        ai_deep_output += "【3. 合成层深度排序规则】\n"
        for layer_name, layer_data in COMPOSITING_LAYERS.items():
            ai_deep_output += "  " + layer_name + ": " + layer_data["rule"] + "\n"
        ai_deep_output += "\n"

        ai_deep_output += "【4. 导演VFX克制原则】\n"
        ai_deep_output += "  原则: " + director_vfx_data["restraint"] + "\n"
        ai_deep_output += "  禁忌: " + director_vfx_data["anti_pattern"] + "\n"
        ai_deep_output += "  检查: 每一帧VFX都问'如果去掉这个VFX, 叙事是否受损?' 如果不受损, 去掉它.\n\n"

        ai_deep_output += "【5. 反AI具体细节铁律 (VFX版)】\n"
        ai_deep_output += "  - 不写'火焰熊熊燃烧', 写'火焰根部蓝色1800K, 向上过渡到橙红2500K, 高度1.2m, 每0.3秒一次湍流扰动'\n"
        ai_deep_output += "  - 不写'碎片四处飞溅', 写'玻璃径向裂纹从冲击点辐射, 最大碎片4cm落在2m外, 粉碎区半径15cm'\n"
        ai_deep_output += "  - 不写'雨很大', 写'雨滴以12度角倾斜(西北风3级), 落地溅射高度6mm, 积水深度0.5cm且在增长'\n"
        ai_deep_output += "  - 不写'光效很酷', 写'丁达尔光线从窗户45度角射入, 因空气中灰尘密度不均匀而出现3-4条亮度不等的光束'\n\n"

        ai_deep_output += "【6. 质量指标】\n"
        ai_deep_output += "  - 分辨率: 复杂度 " + complexity_choice + " -> " + complexity_data.get("render_budget", "standard") + "\n"
        ai_deep_output += "  - 渲染通道: beauty + diffuse + specular + shadow + AO + depth + motion_vector + alpha\n"
        ai_deep_output += "  - 噪声阈值: 写实模式 < 0.01 noise per pixel; 风格化可接受 < 0.05\n"
        ai_deep_output += "  - 帧率: 24fps (电影) / 30fps (电视/短剧) / 60fps (互动剧)\n"

        return (main_output, experience, ai_deep_output)


# NODE_CLASS_MAPPINGS (disabled - internal library only) = {
#     "VfxPro": VfxPro,
# }

# NODE_DISPLAY_NAME_MAPPINGS (disabled) = {
#     "VfxPro": "✨ VFX (环节 33) — L5 重写",
# }
