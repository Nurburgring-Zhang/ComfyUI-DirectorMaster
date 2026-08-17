# -*- coding: utf-8 -*-
"""
Phase 14 - 15 块刚性骨架 (Higgsfield Hell Grind CINEDANCE 复刻)
================================================
Hell Grind 的 prompt 是"刚性骨架, 不是自由发挥" — 15 块, 每块有固定职责。
我们也建立 15 块, 让所有节点在生成 prompt 时都有标准结构。

15 块刚性骨架:
1.  SCENE CONTEXT   - 头行必须是 "EXACT N CHARACTERS — NO DUPLICATES"
2.  ACTIVE REFERENCES- 角色和地点标签
3.  LOCATION MAP    - GEO SPATIAL LAYOUT
4.  FIRST FRAME AND SPATIAL BLOCKING - 第一帧谁站哪
5.  FORMAT MODE     - 单镜/硬切/时长/实时
6.  OPTICS          - 镜头和焦点计划
7.  CAMERA          - 摄影机怎么动, 以及它绝不动什么
8.  ACTION TIMING   - 动作逐秒拆
9.  PHYSICS         - 重量, 接触, 惯性
10. LIGHTING        - 单一光源逻辑
11. AUDIO           - 声音描述符 + 逐字台词
12. CHARACTER ACTING- 5 支柱 + 身体行为
13. STYLE           - Style Prefix, 逐字粘贴
14. QUALITY         - 细节和稳定性要求
15. POSITIVE CONSTRAINTS - 数量/人数限制

+ 第 16 块: STYLE PREFIX (12 层技术底座, 来自小互分析)
  - Style / Cinematography / Lighting / Color / Camera / Skin
  - Acting / Physics / Composition / Continuity / Technical / Audio
"""

# ============================================================
# 15 块刚性骨架 (Higgsfield CINEDANCE)
# ============================================================
FIFTEEN_BLOCKS = [
    {
        "id": 1,
        "name": "SCENE CONTEXT",
        "purpose": "头行必须是 'EXACT N CHARACTERS — NO DUPLICATES'",
        "template": """SCENE CONTEXT
EXACT {n_characters} CHARACTERS — NO DUPLICATES: {character_list}. {location_descriptor}, {time_of_day}. {one_line_summary}. One continuous {duration}s shot, no cuts.""",
        "rules": [
            "EXACT N CHARACTERS 是硬性约束, 防止模型克隆人物",
            "EXACTLY ONE X, NEVER render a second one (家具/道具也要禁)",
            "Live-action. NON-IP. 16:9. {duration}s. SFX only. NO CGI. Cinematic.",
            "Write in present tense. Short sentences.",
        ],
    },
    {
        "id": 2,
        "name": "ACTIVE REFERENCES",
        "purpose": "角色和地点标签, 注明每个引用的角色",
        "template": """ACTIVE REFERENCES
{character_refs}
{location_refs}
{props_refs}""",
        "rules": [
            "@{char_name} for character reference — {descriptor_for_this_shot}",
            "@{loc_name} for location reference — take only the space and the texture: {key_features}. Do not use as a starting frame, do not inherit the composition, the angle or the grade.",
        ],
    },
    {
        "id": 3,
        "name": "LOCATION MAP",
        "purpose": "GEO SPATIAL LAYOUT — 场景的固定平面图",
        "template": """GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):
{spatial_landmarks}
— 180° AXIS: camera ALWAYS stays on {axis_side} side — it NEVER crosses the line.
— BACK-LIGHTING: {light_direction}""",
        "rules": [
            "方向用 frame-left/frame-right + 米数, 不用 hero's left",
            "位置挂地标 + 米: 'at the altar, three meters away'",
            "摄影机站哪边, 绝不过哪条线, 所有剪辑才在一条轴上",
        ],
    },
    {
        "id": 4,
        "name": "FIRST FRAME AND SPATIAL BLOCKING",
        "purpose": "第一秒谁站哪, 让模型拍照定格位置",
        "template": """FIRST FRAME AND SPATIAL BLOCKING
0.0-1.0s: Wide static shot. {everyone_at_position}. {light_state}. Camera on {camera_side}, {distance}m back. No motion. 1 second of pure space.""",
        "rules": [
            "第一秒永远是全景: 无台词无动作, 让模型拍照定格",
            "删掉这一秒, 角色就开始换位",
            "小 hack: 这一秒里让谁蹦一个短词 (如 'hm'), Seedance 更容易当独立镜头处理",
        ],
    },
    {
        "id": 5,
        "name": "FORMAT MODE",
        "purpose": "单镜还是硬切, 时长, 实时",
        "template": """FORMAT MODE
- {format_type}  # continuous / hard-cut
- Duration: {duration}s
- Frame rate: {fps}fps
- Aspect ratio: 16:9
- Real-time: {real_time}""",
        "rules": [
            "单镜头 (one continuous) 适合 12-30s 戏",
            "硬切 (hard-cut) 适合 30s+ 长戏, 但要 GEO 锁死空间",
        ],
    },
    {
        "id": 6,
        "name": "OPTICS",
        "purpose": "镜头和焦点计划",
        "template": """OPTICS
- Lens: {lens_type}  # 35mm anamorphic / 50mm spherical / 85mm portrait
- Focal plane: {focal_target}
- Depth of field: {dof}
- Filter: {filter}  # Black Pro-Mist 1/4 / IRND / none""",
        "rules": [
            "Physical cine lens, 180° shutter motion blur (24fps)",
            "focal target 是角色眼平面, 不是胸口",
        ],
    },
    {
        "id": 7,
        "name": "CAMERA",
        "purpose": "摄影机怎么动, 以及它绝不动什么",
        "template": """CAMERA
- Movement: {camera_motion}  # Push In with small amplitude at slow speed
- Subject framing: {framing}
- NEVER: {never_moves}  # 摄影机绝不做的事""",
        "rules": [
            "镜头运动 = 类型 + with small/large amplitude + at slow/fast speed",
            "NEVER crosses 180° axis, NEVER tilts more than 15°",
        ],
    },
    {
        "id": 8,
        "name": "ACTION TIMING",
        "purpose": "动作逐秒拆, 每节拍最多三句话",
        "template": """ACTION TIMING
{beat_start}-{beat_end}s — {single_action}. {body_anchor}. {what_changes}.
{beat_start2}-{beat_end2}s — {single_action2}. {body_anchor2}. {what_changes2}.""",
        "rules": [
            "每节拍最多三句话",
            "一个节拍超载, 模型直接糊成一团",
            "复杂动作从生成的第一帧直接开始 (不要 'walk to the door, raise arm')",
        ],
    },
    {
        "id": 9,
        "name": "PHYSICS",
        "purpose": "重量, 接触, 惯性",
        "template": """PHYSICS
- Mass has real weight
- Correct contact shadows
- No floating props
- {specific_physics_constraint}""",
        "rules": [
            "Gravity and inertia respected",
            "No floating props",
        ],
    },
    {
        "id": 10,
        "name": "LIGHTING",
        "purpose": "单一光源逻辑, 从哪来",
        "template": """LIGHTING
- Key light: {key_light}  # from sky and windows only / contre-jour backlight
- Color temperature: {temp}  # 5000K / 3200K / 2700K
- Atmosphere: {atmosphere}  # haze / dust / smoke / clean
- Shadow: {shadow_direction}""",
        "rules": [
            "Natural light only — contre-jour backlight, camera on shadow side",
            "Key light from sky and windows only",
        ],
    },
    {
        "id": 11,
        "name": "AUDIO",
        "purpose": "声音描述符和逐字台词, 只环境音",
        "template": """AUDIO
- Voice signatures: {voice_descriptors}
- Dialogue: {dialogue_in_quotes}  # Only the line in quotes. No extra words.
- Silenced characters: {silenced}  # 这些人必须保持沉默
- Soundscape layers: {sfx_layers}
- Continuation tail: {prev_clip_tail}  # 上一句尾音进这镜第一秒
- NO MUSIC (留后期)""",
        "rules": [
            "台词固定结构: 声音+情绪 → 引号里的台词 → 身体动作 → 面部反应",
            "没台词的人必须保持安静",
            "SFX only. No music. No subtitles.",
        ],
    },
    {
        "id": 12,
        "name": "CHARACTER ACTING",
        "purpose": "5 支柱 + 身体行为, 永远不写情绪",
        "template": """CHARACTER ACTING
{actor_name} — emotional state: {visible_state}. What he wants: {goal}. What he is hiding: {secret}. Dominant body rhythm: {rhythm}. Visible habits in this beat: {habits}. What changes across the shot: {change}.""",
        "rules": [
            "不写 'sad' 'angry' 'shocked' — 写 '下颌绷紧' '鼻翼动' '视线先到门口'",
            "5 支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN",
            "INNER 内心独白: 每一段动作配一行未说出口的内心",
        ],
    },
    {
        "id": 13,
        "name": "STYLE",
        "purpose": "Style Prefix, 逐字粘贴 (12 层技术底座)",
        "template": """{style_prefix}""",  # 见 STYLE_PREFIX
        "rules": [
            "Style Prefix 逐字粘贴, 全文不能改",
        ],
    },
    {
        "id": 14,
        "name": "QUALITY",
        "purpose": "细节和稳定性要求",
        "template": """QUALITY
- Cinematic, live-action — no 3D render, no game engine, no game-cutscene aesthetic
- Film-grain texture
- Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow matching on-set light
- Wet living eyes with catch-lights
- Visible breath and chest rise
- 24fps smooth motion. Film-grain detail. No jitter""",
        "rules": [
            "皮肤纹理是基础, 错了后面很难救",
        ],
    },
    {
        "id": 15,
        "name": "POSITIVE CONSTRAINTS",
        "purpose": "数量和人数限制, 写成'画面里有什么'",
        "template": """POSITIVE CONSTRAINTS
- Exactly {n} people, no one else
- Exactly {prop_count} {prop_name}, never re-rendered as intact, never multiplied
- {other_quantitative_constraints}""",
        "rules": [
            "模型爱加人和克隆家具, 必须在 prompt 里给禁令",
            "EXACTLY ONE mannequin, NEVER render a second one",
        ],
    },
]

# ============================================================
# STYLE PREFIX (12 层技术底座, 来自 Hell Grind 4 万条提示词统计)
# ============================================================
STYLE_PREFIX = """Style: Cinematic, live-action — no 3D render, no game engine, no game-cutscene aesthetic.
Cinematography: floating immersive camera that lives with the actors; natural motivated light; painterly composed frames, strong silhouettes against the light.
Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric haze throughout. Key light from sky and windows only.
Color: 60:30:10 — dominant / secondary / accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow matching on-set light.
Acting: Hollywood — micro-pauses before reactions, precise eye-line, wet living eyes with catch-lights, visible breath and chest rise.
Physics: Gravity and inertia respected — mass has real weight, correct contact shadows. No floating props.
Composition: Rule of thirds + golden ratio. Every person moving from frame one.
Continuity: Characters, props, environment identical across every cut. No identity drift.
Technical: 24fps smooth motion. Film-grain detail. No jitter.
Audio: Environmental SFX only. No music. No subtitles."""


def build_skeleton_prompt(blocks: dict) -> str:
    """根据 15 块内容拼装完整 prompt"""
    out = []
    for block in FIFTEEN_BLOCKS:
        key = block["name"]
        if key in blocks:
            out.append(blocks[key])
    return "\n\n".join(out)


def render_style_prefix() -> str:
    """渲染 12 层 Style Prefix (Style/Cinematography/Lighting/Color/Camera/Skin/Acting/Physics/Composition/Continuity/Technical/Audio)"""
    return STYLE_PREFIX


def get_skeleton_summary() -> str:
    """15 块骨架摘要"""
    return f"""
════════════════════════════════════════
【Higgsfield 15 块刚性骨架 (CINEDANCE)】
════════════════════════════════════════

1.  SCENE CONTEXT           — "EXACT N CHARACTERS — NO DUPLICATES"
2.  ACTIVE REFERENCES        — @角色 + @地点 + @道具
3.  LOCATION MAP             — GEO SPATIAL LAYOUT + 180° axis
4.  FIRST FRAME              — 1 秒全景让 AI 认路
5.  FORMAT MODE              — 单镜/硬切/时长
6.  OPTICS                   — 镜头和焦点
7.  CAMERA                   — 摄影机怎么动 + 绝不动什么
8.  ACTION TIMING            — 逐秒拆, 每节拍 ≤3 句
9.  PHYSICS                  — 重量 + 接触 + 惯性
10. LIGHTING                 — 单一光源
11. AUDIO                    — 声音 + 台词 + 沉默 + 尾音
12. CHARACTER ACTING         — 5 支柱 + 行为
13. STYLE                    — 12 层技术底座
14. QUALITY                  — 细节 + 稳定性
15. POSITIVE CONSTRAINTS     — 数量约束

每条 prompt 结尾逐字粘贴 STYLE PREFIX。

════════════════════════════════════════
"""


if __name__ == "__main__":
    print(get_skeleton_summary())
    print(f"\nStyle Prefix 长度: {len(STYLE_PREFIX)} 字符")
    print(f"15 块总模板长度: {sum(len(b['template']) for b in FIFTEEN_BLOCKS)} 字符")
