# -*- coding: utf-8 -*-
"""
Production Pipeline V3 — 影视全生产环节统一架构
==================================================

5 大要素标准 (每一环节都按这 5 要素处理):
1. 数据 (Data) - 原始素材/参考/案例
2. 上下文缩略 (Context Brief) - 浓缩的关键信息
3. Skill/Harness - 技能/工具/方法
4. 经验矩阵 (Experience Matrix) - 顶级导演实战经验
5. AI 深度处理 (AI Deep Processing) - 真正的智能处理

完整生产环节 (从立项到交付):
A. 前期 (Pre-production) 22 环节
B. 制作 (Production) 5 环节
C. 后期 (Post-production) 7 环节
D. 交付 (Delivery) 4 环节
E. 类型专项 (Type-specific) 5 环节

导演意图 5 维度 (附件核心):
- 感受意图 (观众看完应感到什么)
- 情感意图 (角色此刻应有何情感)
- 关系意图 (角色间关系如何)
- 主题意图 (本场承载主题的哪一面)
- 留白意图 (什么不该说, 让观众自己懂)
"""

# ============================================================
# 1. 5 大要素标准 - 每一环节的处理流程
# ============================================================

FIVE_ELEMENTS = {
    "data": {
        "name": "数据 (Data)",
        "description": "原始素材/参考/案例库, 提供处理对象",
        "sources": [
            "1161 部作品 director_view 14 维数据",
            "63 导演 12 维档案",
            "191 反 AI 词条",
            "12 套顶级理论数据集 (100+ 技法)",
            "40 句实战钩子库",
            "30 句反 AI 对白对",
            "12 角色原型 + 6 维深度",
            "15 位世界顶级导演真实剧本范本",
        ],
    },
    "context_brief": {
        "name": "上下文缩略 (Context Brief)",
        "description": "将数据浓缩为关键信息, 提供处理基础",
        "rules": [
            "主题一句话 (不是'关于XXX', 直接说XXX)",
            "人物 3 句话 (身份/欲望/需求)",
            "冲突 1 句话 (谁 vs 谁, 为何)",
            "核心场景 1 个 (用具体细节描述)",
            "导演意图 1 句话 (观众应该感到什么)",
        ],
    },
    "skill_harness": {
        "name": "Skill/Harness",
        "description": "技能/工具/方法, 提供处理能力",
        "tools": [
            "12 套理论: Save the Cat / Hero's Journey / Story Circle / McKee / 三幕剧 / 8 Sequences / 五幕剧 / 短剧三秒铁律 / 抖音套路 / 爆款公式 / 角色弧光 / 反转/节奏/余韵",
            "15 位导演真实剧本范本 (塔可夫斯基/王家卫/诺兰/小津/侯孝贤/是枝裕和/黑泽明/库布里克/伯格曼/贾樟柯/奉俊昊/李安/蔡明亮/李沧东/毕赣)",
            "30 句反 AI 对白 (真人写法 vs AI 套路)",
            "40 句实战钩子 (8 大类型各 5 句)",
            "5 要素处理流程 (每一环节都按 5 要素)",
        ],
    },
    "experience_matrix": {
        "name": "经验矩阵 (Experience Matrix)",
        "description": "顶级导演实战经验, 提供处理智慧",
        "principles": [
            "王家卫: 用物件代替心理, 短句, 时间戳",
            "塔可夫斯基: 时间即主角, 长镜头",
            "侯孝贤: 不动, 让时间发生, 自然光",
            "是枝裕和: 日常细节, 不评判",
            "黑泽明: 天气即情绪, 群戏调度",
            "诺兰: 结构即主题, 物理逻辑",
            "小津: 低位静态, 重复",
            "伯格曼: 脸特写, 沉默, 哲理对白",
            "蔡明亮: 超慢, 无对白, 城市角落",
            "李沧东: 底层, 道德困境, 不给答案",
            "毕赣: 长镜头, 诗化旁白, 时间折叠",
        ],
    },
    "ai_deep_processing": {
        "name": "AI 深度处理 (AI Deep Processing)",
        "description": "真正的智能处理, 不是模板拼接",
        "requirements": [
            "理解导演意图, 不只画面描述",
            "强制具体细节, 不用情绪形容词",
            "用沉默/留白表达情绪, 不用'陷入沉思'",
            "用物件代替心理",
            "用空间一致性建立可信度",
            "用美术质感建立基础",
            "用时间结构推进剧情",
            "反 AI 词表强制清洗",
            "多轮迭代 + 人工挑选",
        ],
    },
}

# ============================================================
# 2. 完整生产环节 (从立项到交付 43 环节)
# ============================================================

PRODUCTION_PIPELINE = {
    "A. 前期 (Pre-production)": {
        "1_concept_pitch": {
            "name": "概念立项 (Concept Pitch)",
            "description": "从一句话到一页, 让投资人/制片/团队明白这个项目",
            "key_questions": [
                "这是什么类型? 卖给谁?",
                "核心冲突是什么?",
                "为什么是现在? (时代性)",
                "为什么是我们? (独特性)",
            ],
            "deliverable": "Logline (一句话故事) + 一页大纲 + 视觉 mood board",
        },
        "2_genre_positioning": {
            "name": "类型定位 (Genre Positioning)",
            "description": "明确类型的 9 大维度 (剧作/情绪/视觉/节奏/受众/成本/平台/竞品/创新点)",
            "deliverable": "类型定位文档 9 维 + 竞品分析 + 差异化点",
        },
        "3_world_building": {
            "name": "世界设定 (World Building)",
            "description": "世界观/时代/地域/文化/物理规则/社会规则",
            "key_layers": [
                "物理世界: 地点/季节/天气/光线/声音/气味",
                "社会世界: 阶层/制度/法律/禁忌/潜规则",
                "文化世界: 宗教/语言/代际/地域/饮食",
                "心理世界: 主角/对手/盟友/中立者/旁观者",
            ],
            "deliverable": "世界设定 Bible",
        },
        "4_theme_philosophy": {
            "name": "主题哲学 (Theme Philosophy)",
            "description": "故事承载的终极问题, 是关于什么的'什么'",
            "philosophy_examples": [
                "失去的不可逆, 但记忆可以重建 (侯孝贤)",
                "时间不等人, 但人可以重新认识 (是枝裕和)",
                "权力是冷的, 但人是有温度的 (奉俊昊)",
                "孤独是人的本质 (伯格曼)",
            ],
            "deliverable": "主题哲学陈述 + 隐喻系统 + 象征系统",
        },
        "5_story_architecture": {
            "name": "故事架构 (Story Architecture)",
            "description": "用 12 套理论之一设计整体结构 (Save the Cat / Hero's Journey / Story Circle / 三幕剧 / 8 Sequences / 五幕剧)",
            "deliverable": "结构图 + 关键节拍 + 情绪曲线",
        },
        "6_character_bible": {
            "name": "角色 Bible (Character Bible)",
            "description": "12 原型 + 6 维深度 + 欲望 vs 需求",
            "deliverable": "主角/对手/盟友/中立者/旁观者的 Bible",
        },
        "7_character_arc": {
            "name": "角色弧光 (Character Arc)",
            "description": "7 大弧光之一, 用 Hero's Journey 12 阶段设计旅程",
            "deliverable": "角色弧光旅程图",
        },
        "8_script_body": {
            "name": "剧本正文 (Script Body)",
            "description": "场次/场景/对白/动作, 用反 AI 词表强制清洗",
            "deliverable": "完整剧本 (按集/按场/按镜)",
        },
        "9_director_intent": {
            "name": "导演意图 (Director Intent) - 附件核心",
            "description": "导演会怎么描述自己的意图, 不是'画面里有什么'",
            "5_dimensions": [
                "感受意图: 观众看完应感到什么",
                "情感意图: 角色此刻应有何情感",
                "关系意图: 角色间关系如何",
                "主题意图: 本场承载主题的哪一面",
                "留白意图: 什么不该说, 让观众自己懂",
            ],
            "deliverable": "每场戏的导演意图陈述",
        },
        "10_director_statement": {
            "name": "导演阐述 (Director Statement)",
            "description": "导演对整部电影/剧/短片的整体陈述",
            "deliverable": "导演阐述文档",
        },
        "11_art_direction": {
            "name": "美术指导 (Art Direction) - 附件核心",
            "description": "材质/光影/颜色/空间是基础, 一旦很差很难救",
            "key_layers": [
                "材质: 织物/金属/木质/石质/玻璃/皮肤的质感",
                "光影: 自然光/硬光/柔光/烛光/霓虹/月光/光比",
                "颜色: 主色调/辅色/对比色/情绪色/时代色",
                "空间: 室内/室外/开阔/压抑/温暖/冷峻",
            ],
            "deliverable": "美术指导 Bible + 参考图集 + 色彩 script",
        },
        "12_visual_concept": {
            "name": "视觉概念 (Visual Concept)",
            "description": "整部电影的视觉风格定义 (风格/灵感/参考)",
            "deliverable": "视觉概念板 + 关键场景概念图",
        },
        "13_sound_design": {
            "name": "声音设计 (Sound Design)",
            "description": "环境声/对白/音效/配乐/混音",
            "deliverable": "声音设计文档 + 声音 script",
        },
        "14_music_score": {
            "name": "音乐配乐 (Music Score)",
            "description": "配乐/主题曲/插曲, 推动情绪/揭示主题",
            "deliverable": "配乐 demo + 主题曲歌词 + 配乐时刻",
        },
        "15_storyboard": {
            "name": "分镜脚本 (Storyboard)",
            "description": "每场戏的镜头/景别/运动/光影/声音/表演/节奏/留白",
            "deliverable": "分镜图 + 镜头列表",
        },
        "16_cinematography": {
            "name": "镜头语言 (Cinematography)",
            "description": "景别/角度/运动/光圈/焦距/景深",
            "deliverable": "镜头语言指南",
        },
        "17_performance_direction": {
            "name": "表演指导 (Performance Direction)",
            "description": "角色的微表情/身体语言/潜文本/能量/节拍",
            "deliverable": "角色表演指南 + 关键场次指导",
        },
        "18_spatial_design": {
            "name": "空间设计 (Spatial Design) - 附件核心",
            "description": "人物/道具/场景之间关系可信",
            "key_rules": [
                "一个角色可以在同一空间里连续运动",
                "摄影机换一个角度, 模型依然知道人物/道具/场景之间关系",
                "空间稳定, 演员才有地方表演",
                "镜头愿意停下来, 观众才有时间看见表情",
                "人物在空间里的位置可信, 走近/远离/回头/躲避这些动作才会产生意义",
            ],
            "deliverable": "空间设计文档 + 空间参考图",
        },
        "19_costume_prop_set": {
            "name": "服化道 (Costume/Prop/Set)",
            "description": "服装/化妆/道具/场景, 时代感/角色感/真实性",
            "deliverable": "服化道 Bible",
        },
        "20_pacing_silence": {
            "name": "节奏与沉默 (Pacing & Silence) - 附件核心",
            "description": "铺垫/时长/沉默, 很多情绪恰恰发生在沉默的几分钟里",
            "key_rules": [
                "叙事, 很多时候讲究的是留白, 是那说不满的一寸",
                "可在一场戏里, 很多情绪和念想, 反而恰恰发生在沉默的几分钟里",
                "两个人可以先说一句话, 沉默几秒, 出现一个细微的表情变化, 然后让某个动作改变关系, 最后再给观众一点反应时间",
                "30 秒才能接近一个完整的场景单元",
                "几分钟的停顿, 看起来什么都没发生, 实际是情感的酝酿",
            ],
            "deliverable": "节奏曲线 + 沉默时刻标注",
        },
        "21_color_grading": {
            "name": "调色 (Color Grading)",
            "description": "主色/辅色/对比/色温/饱和度, 配合情绪和主题",
            "deliverable": "LUT 调色指南",
        },
        "22_vfx": {
            "name": "视觉特效 (VFX)",
            "description": "特效/合成/CG/降本, 真实感 vs 艺术性",
            "deliverable": "VFX 制作指南",
        },
    },
    "B. 制作 (Production)": {
        "23_aigc_storyboard": {
            "name": "AIGC 分镜生成 (AIGC Storyboard)",
            "description": "通过 ComfyUI 节点调用 AIGC 模型生成分镜图",
            "deliverable": "AIGC 分镜图集",
        },
        "24_aigc_character": {
            "name": "AIGC 角色生成 (AIGC Character)",
            "description": "角色一致性 + 多视角 + 表情变化",
            "deliverable": "角色参考图集 (多视角/多表情)",
        },
        "25_aigc_scene": {
            "name": "AIGC 场景生成 (AIGC Scene)",
            "description": "空间一致性 + 时代感 + 美术质感",
            "deliverable": "场景概念图集",
        },
        "26_aigc_shot": {
            "name": "AIGC 镜头生成 (AIGC Shot)",
            "description": "镜头 + 景别 + 运动 + 光影 + 表演",
            "deliverable": "AIGC 镜头视频",
        },
        "27_multi_modal_fusion": {
            "name": "多模态融合 (Multi-modal Fusion)",
            "description": "图/文/视频/音频的融合",
            "deliverable": "多模态资产",
        },
    },
    "C. 后期 (Post-production)": {
        "28_editing": {
            "name": "剪辑 (Editing)",
            "description": "剪辑点/节奏/声音/音乐配合",
            "deliverable": "粗剪/精剪/终剪",
        },
        "29_dubbing_subtitle": {
            "name": "配音字幕 (Dubbing/Subtitle)",
            "description": "配音/字幕/多语言",
            "deliverable": "配音版 + 字幕版",
        },
        "30_sound_mixing": {
            "name": "混音 (Sound Mixing)",
            "description": "对白/音效/配乐的平衡",
            "deliverable": "混音版",
        },
        "31_mastering": {
            "name": "母带 (Mastering)",
            "description": "整体响度/动态/平台适配",
            "deliverable": "母带版",
        },
        "32_color_final": {
            "name": "调色终版 (Color Grading Final)",
            "description": "全片调色一致性",
            "deliverable": "调色终版",
        },
        "33_vfx_compositing": {
            "name": "特效合成 (VFX Compositing)",
            "description": "特效合成/调色/VFX",
            "deliverable": "VFX 终版",
        },
        "34_quality_assurance": {
            "name": "质量审核 (QA)",
            "description": "技术审核 (色彩/声音/清晰度) + 内容审核 (剧情/对白/演技)",
            "deliverable": "QA 报告 + 修改意见",
        },
    },
    "D. 交付 (Delivery)": {
        "35_platform_adaptation": {
            "name": "平台适配 (Platform Adaptation)",
            "description": "ReelShort / DramaBox / 抖音 / 电影 / 剧集 各自规格",
            "deliverable": "多平台多规格版本",
        },
        "36_metadata": {
            "name": "元数据 (Metadata)",
            "description": "标题/简介/标签/封面/海报",
            "deliverable": "元数据文档",
        },
        "37_release_strategy": {
            "name": "发布策略 (Release Strategy)",
            "description": "预热/上线/付费点/更新节奏",
            "deliverable": "发布计划",
        },
        "38_analytics": {
            "name": "数据反馈 (Analytics)",
            "description": "留存/完播/付费/口碑/迭代",
            "deliverable": "数据报告 + 迭代方向",
        },
    },
    "E. 类型专项 (Type-specific)": {
        "39_mv": {
            "name": "MV 专项 (MV)",
            "description": "音乐视频/视觉化/剪辑/表演",
            "deliverable": "MV 终版",
        },
        "40_picture_book": {
            "name": "故事绘本 (Picture Book)",
            "description": "图文配合/分页/年龄层",
            "deliverable": "绘本 PDF / e-book",
        },
        "41_interactive_drama": {
            "name": "互动剧 (Interactive Drama)",
            "description": "分支选择/结局多/观众参与",
            "deliverable": "互动剧资产 + 决策树",
        },
        "42_realtime_interactive": {
            "name": "AIGC 实时互动剧 (Realtime Interactive)",
            "description": "实时 AIGC 生成 + 观众互动 + 沉浸感",
            "deliverable": "实时互动引擎 + AIGC 资源",
        },
        "43_short_drama": {
            "name": "短剧 (Short Drama)",
            "description": "ReelShort / DramaBox / 抖音短剧 1-2 分钟单集",
            "deliverable": "短剧集 + 付费点",
        },
    },
}


# ============================================================
# 3. 导演意图 5 维度详解
# ============================================================

DIRECTOR_INTENT_5D = {
    "1_感受意图 (Audience Feeling)": "观众看完应感到什么, 不是情节是什么, 是感受是什么",
    "2_情感意图 (Character Emotion)": "角色此刻应有何情感, 用具体细节呈现, 不用'陷入沉思'",
    "3_关系意图 (Relationship Dynamic)": "角色间关系在此刻如何, 用动作/距离/目光呈现",
    "4_主题意图 (Thematic Expression)": "本场承载主题的哪一面, 隐喻如何呈现",
    "5_留白意图 (What's Not Said)": "什么不该说, 让观众自己懂, 沉默的几分钟里发生什么",
}


# ============================================================
# 4. 美术质感 4 维
# ============================================================

ART_DIRECTION_4D = {
    "1_材质 (Material)": "织物/金属/木质/石质/玻璃/皮肤的质感, 粗/细/光/毛/旧/新",
    "2_光影 (Light & Shadow)": "自然光/硬光/柔光/烛光/霓虹/月光/光比, 高对比/低对比",
    "3_颜色 (Color)": "主色调/辅色/对比色/情绪色/时代色, 高饱和/低饱和/去色",
    "4_空间 (Space)": "室内/室外/开阔/压抑/温暖/冷峻, 前景/中景/背景",
}


# ============================================================
# 5. 空间一致性 5 规则
# ============================================================

SPATIAL_CONSISTENCY_5 = {
    "1_continuous_motion": "一个角色可以在同一空间里连续运动",
    "2_angle_change": "摄影机换一个角度, 模型依然知道人物/道具/场景之间关系",
    "3_space_stable": "空间稳定, 演员才有地方表演",
    "4_camera_stays": "镜头愿意停下来, 观众才有时间看见表情",
    "5_position_believable": "人物在空间里的位置可信, 走近/远离/回头/躲避这些动作才会产生意义",
}


# ============================================================
# 6. 留白/沉默 5 规则 (附件核心)
# ============================================================

SILENCE_MASTERY_5 = {
    "1_setup_needs_time": "影视需要铺垫, 需要时长, 需要沉默",
    "2_30s_minimum": "30 秒, 开始在整体上接近一个完整的场景单元",
    "3_micro_expression": "两个人可以先说一句话, 沉默几秒, 出现一个细微的表情变化, 然后让某个动作改变关系, 最后再给观众一点反应时间",
    "4_pause_emotion": "这几分钟的停顿, 看起来什么都没发生。可在一场戏里, 很多情绪和念想, 反而恰恰发生在沉默的几分钟里",
    "5_unsaid_remain": "叙事, 很多时候讲究的是留白, 是那说不满的一寸",
}


# ============================================================
# 7. 5 要素处理流程 (统一函数)
# ============================================================

def process_with_5_elements(stage: str, user_input: dict) -> dict:
    """5 要素统一处理流程"""
    return {
        "stage": stage,
        "data": "1161 部作品 + 63 导演 + 191 反 AI + 12 套理论",
        "context_brief": "见对应环节节点",
        "skill_harness": "12 套理论 + 15 导演 + 30 反 AI + 40 钩子",
        "experience_matrix": "15 位世界顶级导演实战经验",
        "ai_deep_processing": "反 AI 词表 + 4 轮迭代 + 人工挑选",
        "user_input": user_input,
    }


# ============================================================
# 8. 验证数据完整性
# ============================================================

if __name__ == "__main__":
    print("=== Production Pipeline V3 ===")
    print(f"5 大要素: {len(FIVE_ELEMENTS)} 要素")
    print(f"生产环节总数: {sum(len(v) for v in PRODUCTION_PIPELINE.values())}")
    for stage, stages in PRODUCTION_PIPELINE.items():
        print(f"  {stage}: {len(stages)} 环节")
    print(f"导演意图 5 维: {len(DIRECTOR_INTENT_5D)}")
    print(f"美术 4 维: {len(ART_DIRECTION_4D)}")
    print(f"空间一致性 5 规则: {len(SPATIAL_CONSISTENCY_5)}")
    print(f"留白/沉默 5 规则: {len(SILENCE_MASTERY_5)}")
