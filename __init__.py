# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V14.3-MERGED — 13 注册节点 (12 超级节点 + Final 别名) + 534 导演库
====================================================================
V14.3-MERGED = V14.2 审计基线 (全部 P0 修复/模式坍缩根治/结构节拍归位)
+ V14.1-clean 分叉的 9 项孤儿库复活接线 (场景库/大师DNA/故事感/儿童/案例/领域规则/
  大师原则/CINEDANCE骨架/灵感场景/Seedance能力/8设计模式/42环节/6文档)
+ 阶段1 输出质量深化 (D1 同簇镜头语法差异化 / D2 形态骨架+执行层 / D3 互动剧分支树 /
  D4 版本存储工程化) + 阶段2 体验一致性 (E1 浮点清零 / E2 时长覆盖±1%)。

13 注册节点 (Core 驱动 + forceInput):
  1. DirectorMasterCore         — 起点 → 统一电影提示词 + 核心数据包
  2. DirectorMasterScript       — 剧本 46 模式 (长片/短剧/短视频/动漫/绘本/MV/广告/纪录片/互动剧/钩子/对白/角色弧)
  3. DirectorMasterVibe         — 创意 23 模式 (概念/主题/世界/服化道/表演/VFX/MV/调色/剪辑/QA/绘本/互动/漫剧/市场受众分析/8设计模式)
  4. DirectorMasterArt          — 美术 3 模式 (美术指导/空间一致性/空间布局)
  5. DirectorMasterSound        — 声音 4 模式 (声音设计/音乐/声音层/沉默)
  6. DirectorMasterCinematic    — 分镜 63 模式 (电影工作室/节奏大师/短剧/动漫/绘本/MV/广告/纪录片分镜)
  7. DirectorMasterCharacters   — 角色 42 模式 (角色/环境/服化道/参考图 → 6路输出)
  8. DirectorMasterAsset        — 资产 41 模式 (角色/环境/服化道/HellGrind资产库 → IP-Adapter/参考图锁定)
  9. DirectorMasterSummary      — 终极汇总 3 路 (完整制作手册/JSON交付包/项目索引)
 10. DirectorMasterRouter       — 通用 prompt 路由 (7 目标模型, H3 深度 IR 5 模式 + EDL)
 11. DirectorMasterVideoRouter  — 5 视频模型超级路由 (Seedance/LTX/Wan/Hailuo/Sora)
 12. DirectorMasterArchive      — 归档 (真实写盘 + 磁盘持久化版本控制 + TXT/JSON/MD/HTML 格式多选)
 13. DirectorMasterFinal        — DirectorMasterSummary 兼容别名

工作流: Core 节点 (forceInput 唯一入口) → 下游节点用 forceInput 接核心数据包。
46 个 legacy 细粒度节点默认不注册, 设 DIRECTORMASTER_LEGACY_NODES=1 可恢复全部 59 节点。
自检: python doctor.py (6 类诊断含复活接线消费验证)。
"""
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PARENT = _os.path.dirname(_HERE)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
if _PARENT not in _sys.path:
    _sys.path.insert(0, _PARENT)

# === Core 节点 (继承 V9.5) ===
from aggregator.director_master import DirectorMasterCore

# === 7 个 V9.5 强力 master (8 模式剧本 / 14 模式创意 / 3 美术 / 4 声音 / 5 分镜 / 3 资产 / 终极汇总) ===
from aggregator.script_studio import DirectorMasterScript
from aggregator.vibe_studio import DirectorMasterVibe
from aggregator.art_master import DirectorMasterArt
from aggregator.sound_master import DirectorMasterSound
from aggregator.cinematic_studio import DirectorMasterCinematic
from aggregator.asset_master import DirectorMasterAsset
from aggregator.summary_master import DirectorMasterSummary
from aggregator.router import DirectorMasterRouter

# === 2 个 V12.6 扩展节点 ===
from aggregator.characters_master import DirectorMasterCharacters
from aggregator.video_router_master import DirectorMasterVideoRouter

# === V13 合并: 补回 V9.5 归档节点 (真实写盘) ===
from aggregator.archive_master import DirectorMasterArchive

NODE_CLASS_MAPPINGS = {
    "DirectorMasterCore": DirectorMasterCore,
    "DirectorMasterScript": DirectorMasterScript,
    "DirectorMasterVibe": DirectorMasterVibe,
    "DirectorMasterArt": DirectorMasterArt,
    "DirectorMasterSound": DirectorMasterSound,
    "DirectorMasterCinematic": DirectorMasterCinematic,
    "DirectorMasterCharacters": DirectorMasterCharacters,
    "DirectorMasterAsset": DirectorMasterAsset,
    "DirectorMasterSummary": DirectorMasterSummary,
    "DirectorMasterRouter": DirectorMasterRouter,
    "DirectorMasterVideoRouter": DirectorMasterVideoRouter,
    "DirectorMasterArchive": DirectorMasterArchive,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DirectorMasterCore": "🎬 核心 [导演起点] → 统一电影提示词+核心数据包(11维+534导演库)",
    "DirectorMasterScript": "📖 剧本 [46 模式: 长片/短剧/短视频/动漫/绘本/MV/广告/纪录片/互动剧/钩子/对白/角色弧]",
    "DirectorMasterVibe": "💡 创意 [23 模式: 概念/主题/世界/服化道/表演/VFX/MV/调色/剪辑/QA/绘本/互动/漫剧/市场受众/8设计]",
    "DirectorMasterArt": "🎨 美术 [3 模式: 美术指导/空间一致性/空间布局]",
    "DirectorMasterSound": "🔊 声音 [4 模式: 声音设计/音乐/声音层/沉默]",
    "DirectorMasterCinematic": "🎬 分镜 [63 模式: 电影工作室/节奏大师/短剧/动漫/绘本/MV/广告/纪录片分镜]",
    "DirectorMasterCharacters": "🎭 角色 [42 模式: 角色/环境/服化道/参考图 → 6路输出]",
    "DirectorMasterAsset": "🎭 资产 [41 模式: 角色/环境/服化道/HellGrind资产库 → IP-Adapter/参考图锁定]",
    "DirectorMasterSummary": "🏆 终极汇总 [终点] → 完整制作手册+JSON交付包+项目索引 (3路)",
    "DirectorMasterRouter": "🎬 路由 [7 模型: H3(深度IR 5模式)/Seedance/Wan/Sora/Veo/短剧/通用 → 视频API]",
    "DirectorMasterVideoRouter": "🎥 视频路由 [5 模型并行: Seedance/LTX/Wan/Hailuo/Sora → 5路+元数据]",
    "DirectorMasterArchive": "📦 归档 [真实写盘+版本控制: 剧本/分镜/视频请求/制作手册 → output目录, 可回滚/对比/选优]",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# =====================================================================
# V14-FINAL: 节点收敛 — 默认注册 12 超级节点 + DirectorMasterFinal 别名 (共 13)。
# 每个超级节点以下拉框聚合几十种模式, 能力全覆盖。
# 46 个 legacy 细粒度节点默认不再注册 (避免节点选择器臃肿)。
# 注: 超级节点实际接线 3 个 legacy 引擎 (mv_pro/picture_book_pro/comic_drama_pro),
#     其余能力由新引擎 (feature_film_engine/scene_engine/pacing_engine 等) 承接。
# 如需兼容旧工作流, 设环境变量 DIRECTORMASTER_LEGACY_NODES=1 重新注册全部 59 节点。
# =====================================================================
_REGISTER_LEGACY_NODES = _os.environ.get("DIRECTORMASTER_LEGACY_NODES", "0") == "1"
_LEGACY_MODULES = [
    "acting_skill", "aesthetic_judgment_pro", "art_direction_pro", "asset_registry",
    "character_arc_pro", "cinematic_studio", "cleanup_pass_pro", "color_grading_pro",
    "comic_drama_pro", "concept_pitch_pro", "costume_prop_set_pro", "dialogue_master_pro",
    "director_intent_pro", "director_mastery", "director_mastery_v2", "director_soul",
    "director_storyboard_pro", "editing_pro", "format_output_pro", "h3_context_ir_node",
    "hook_master_pro", "interactive_drama_pro", "iteration_post", "market_audience_pro",
    "music_score_pro", "mv_pro", "performance_direction_pro", "picture_book_pro",
    "project_archive_pro", "quality_assurance_pro", "script_architecture_pro",
    "script_body_pro", "shot_selection_pro", "silence_mastery_pro", "sound_design_pro",
    "sound_skill", "spatial_consistency_pro", "spatial_layout", "style_guide_pro",
    "theme_philosophy_pro", "thirty_sec_six_act", "universal_director_prompt_node",
    "version_control_pro", "vertical_short_drama_pro", "vfx_pro", "world_building_pro",
]
_NODE_ATTRS = ("INPUT_TYPES", "RETURN_TYPES", "FUNCTION", "CATEGORY")
LEGACY_LOAD_ERRORS = []
import importlib.util as _importlib_util
if _REGISTER_LEGACY_NODES:
    for _mn in _LEGACY_MODULES:
        _path = _os.path.join(_HERE, _mn + ".py")
        if not _os.path.exists(_path):
            continue
        _uniq = "_dm_legacy_" + _mn
        try:
            _spec = _importlib_util.spec_from_file_location(_uniq, _path)
            _mod = _importlib_util.module_from_spec(_spec)
            _sys.modules[_uniq] = _mod
            _spec.loader.exec_module(_mod)
        except Exception as _e:
            LEGACY_LOAD_ERRORS.append((_mn, repr(_e)))
            continue
        for _name in dir(_mod):
            if _name.startswith("_") or _name in NODE_CLASS_MAPPINGS:
                continue
            _cls = getattr(_mod, _name)
            if not isinstance(_cls, type) or getattr(_cls, "__module__", "") != _uniq:
                continue
            if all(hasattr(_cls, _a) for _a in _NODE_ATTRS) and callable(getattr(_cls, "INPUT_TYPES")):
                NODE_CLASS_MAPPINGS[_name] = _cls
    if LEGACY_LOAD_ERRORS:
        print("[DirectorMaster] 兼容层部分旧模块加载失败 (不影响 12 超级节点):")
        for _mn, _err in LEGACY_LOAD_ERRORS:
            print("  - {}: {}".format(_mn, _err))

# V13.4 (D1.3): 为全部 legacy 节点补中文显示名 — 保证每个注册节点都有显示名
_LEGACY_DISPLAY_NAMES = {
    "ActingSkill": "🎭 表演技能 [5支柱/眨眼/视线/微动作]",
    "AestheticJudgmentPro": "🎨 审美判断 [8原则+导演风格]",
    "ArtDirectionPro": "🖼️ 美术指导 [色彩/光影/材质/构图]",
    "ArtDirectionProNode": "🖼️ 美术指导v2 [色彩/光影/材质/构图]",
    "AssetRegistry": "📦 资产登记 [Hell Grind 资产库]",
    "CharacterArcPro": "🧭 角色弧光 [12原型+7弧+Want/Need]",
    "CinematicStudio": "🎬 电影工作室 [分镜/景别/运镜]",
    "CleanupPassPro": "🧹 清理通道 [去AI套话/重复/模板]",
    "ColorGradingPro": "🎨 调色 [60-30-10+光影9D]",
    "ComicDramaPro": "📚 漫剧分镜 [分格/对话框/拟声词]",
    "ConceptPitchPro": "💡 概念立项 [一句话概念/卖点]",
    "CostumePropSetPro": "👗 服化道 [服装/化妆/道具]",
    "DialogueMasterPro": "💬 对白大师 [极简潜文本对白]",
    "DirectorIntentPro": "🎯 导演意图 [观众应感到]",
    "DirectorMasteryNode": "🧠 导演精通 [情感融合+调色]",
    "DirectorSoulNode": "✨ 导演灵魂 [10维灵魂参数]",
    "DirectorStoryboardPro": "🎞️ 导演分镜 [镜头+灵魂注入]",
    "EditingPro": "✂️ 剪辑 [切点/转场/节奏]",
    "FormatOutputPro": "📄 格式化输出 [多格式排版]",
    "H3ContextIRNode": "🔗 H3上下文IR [多模态检索]",
    "HookMasterPro": "🪝 钩子大师 [前3秒钩子+套路]",
    "InteractiveDramaPro": "🎮 互动剧 [分支/选择/汇合]",
    "IterationPostPro": "🔁 迭代优化 [反馈改进]",
    "MarketAudiencePro": "📊 市场受众 [定位/卖点]",
    "MusicScorePro": "🎵 音乐配乐 [BPM/情感曲线]",
    "MvPro": "🎤 MV导演 [节拍/七段结构]",
    "PerformanceDirectionPro": "🎭 表演指导 [内在动作/视线]",
    "PictureBookPro": "📖 绘本 [分页/年龄适配/画面]",
    "ProjectArchivePro": "🗂️ 项目归档 [版本/资产]",
    "QualityAssurancePro": "✅ 质量QA [检查清单]",
    "ScriptArchitecturePro": "🏗️ 剧本架构 [三幕/节拍]",
    "ScriptBodyPro": "📝 剧本正文 [场次/对白]",
    "ShotSelectionPro": "🎯 选片决策 [候选评估]",
    "SilenceMasteryPro": "🤫 沉默大师 [留白/静默]",
    "SoundDesignPro": "🔊 声音设计 [4层声景]",
    "SoundSkill": "🔉 声音技能 [环境/拟音/沉默]",
    "SpatialConsistencyPro": "📐 空间一致性 [轴线/位置]",
    "SpatialLayout": "🗺️ 空间布局 [场景锚点]",
    "StyleGuidePro": "🎨 风格指南 [调色口诀/色板]",
    "ThemePhilosophyPro": "🧘 主题哲学 [8导演+隐喻]",
    "ThirtySecSixAct": "⏱️ 30秒6段 [短视频结构]",
    "UniversalDirectorPromptNode": "🌐 通用导演提示词 [多模型]",
    "VersionControlPro": "🔖 版本控制 [迭代记录]",
    "VerticalShortDramaPro": "📱 竖屏短剧 [钩子/卡点/灵魂]",
    "VfxPro": "💥 VFX特效 [克制原则]",
    "WorldBuildingPro": "🌍 世界设定 [时空/规则]",
}
for _k, _v in _LEGACY_DISPLAY_NAMES.items():
    if _k in NODE_CLASS_MAPPINGS:
        NODE_DISPLAY_NAME_MAPPINGS.setdefault(_k, _v)
# 兜底: 仍无显示名的注册节点, 用类名生成
for _k in NODE_CLASS_MAPPINGS:
    NODE_DISPLAY_NAME_MAPPINGS.setdefault(_k, _k)

# V13 修复 (A-03): 旧工作流引用的 DirectorMasterFinal 已改名 DirectorMasterSummary — 加别名兼容
NODE_CLASS_MAPPINGS.setdefault("DirectorMasterFinal", DirectorMasterSummary)
NODE_DISPLAY_NAME_MAPPINGS.setdefault("DirectorMasterFinal", "🏆 终极汇总 [终点·DirectorMasterSummary 别名]")

# 标记 V14.3-MERGED 版本
__version__ = "14.3.0"
__description__ = ("V14.3-MERGED = V14.2审计基线 + V14.1-clean分叉合并 + 阶段1/2深化。"
                   "合并: 9项孤儿库复活接线真实消费 (120场景库/15大师DNA/25故事感/儿童适配/14真实案例进剧本; "
                   "绘本/短剧/分镜领域规则进LLM系统提示词; 大师影视语言原则进分镜; CINEDANCE 15块骨架进路由; "
                   "空场景pln_random灵感生成; Seedance 2.5能力边界; 8设计模式修复参数缺失静默降级后真实产出; "
                   "42环节+留白三定律+运镜三定律进手册; Higgsfield 6文档进资产) + doctor.py/tests 移植。"
                   "阶段1: D1同节奏簇景别/运镜/焦段指纹63/63唯一; D2形态骨架+执行层, 同档期形态正文相似度0.91→0.27-0.56; "
                   "D3互动剧可解析分支树(8节点/2选择点/3结局/零悬空); D4版本存储blob去重+gzip+裁剪, 15轮9.7KB回滚逐字节。"
                   "阶段2: E1浮点伪影清零(情感强度/张力/节拍表); E2长镜类时长覆盖-2.78%→全模式±1%内(90/120min实测)。")
