# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V16.1.1-MERGED — 17 注册节点 (16 超级节点 + Final 别名) + 600 导演库
====================================================================
V15.0-MERGED = V14.3-MERGED (V14.2审计基线 + V14.1-clean合并 + 阶段1/2深化)
+ V15.0 AI 赋能升级:
  · 导演库扩容 534→600 (当代新锐/跨界/非西方 66 位真实导演, 17 维档案)
  · 风格融合引擎 (主0.6/次0.3/反0.1 确定性文本融合)
  · 直觉引擎 (确定性反常规镜头语法, 8 条规则均有真实作者电影依据)
  · 灵魂引擎 (创作者体验→物件/动作/沉默母题, 场景驱动零罐头句)
  · 多模态理解 (真实图像分析, 音视频诚实降级)
  · 共创引擎 (五阶段共创循环: 失败记忆/方向分支/门阵/精炼/预算收敛)
  · 反AI词表正则检测层 + 失败记忆 (Reflexion lessons.jsonl)

17 注册节点 (Core 驱动 + forceInput):
  1. DirectorMasterCore         — 起点 → 统一电影提示词 + 核心数据包
  2. DirectorMasterScript       — 剧本 46 模式
  3. DirectorMasterVibe         — 创意 23 模式
  4. DirectorMasterArt          — 美术 3 模式
  5. DirectorMasterSound        — 声音 4 模式
  6. DirectorMasterCinematic    — 分镜 63 模式 (+直觉风险档)
  7. DirectorMasterCharacters   — 角色 42 模式
  8. DirectorMasterAsset        — 资产 41 模式
  9. DirectorMasterSummary      — 终极汇总 3 路
 10. DirectorMasterRouter       — 通用 prompt 路由 (7 模型, H3 深度 IR)
 11. DirectorMasterVideoRouter  — 5 视频模型超级路由
 12. DirectorMasterArchive      — 归档 + 版本控制
 13. DirectorMasterCoCreator    — V15.0 AI 共创循环
 14. DirectorMasterSoul         — V15.0 灵魂引擎
 15. DirectorMasterIntuition    — V15.0 直觉引擎
 16. DirectorMasterFusion       — V15.0 风格融合
 17. DirectorMasterFinal        — DirectorMasterSummary 兼容别名

工作流: Core 节点 (forceInput 唯一入口) → 下游节点用 forceInput 接核心数据包。
自检: python doctor.py。
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

# === V15.0-MERGED: 4 个 AI 赋能节点 (共创/灵魂/直觉/融合) ===
from aggregator.v15_nodes import (DirectorMasterCoCreator, DirectorMasterSoul,
                                  DirectorMasterIntuition, DirectorMasterFusion)

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
    "DirectorMasterCoCreator": DirectorMasterCoCreator,
    "DirectorMasterSoul": DirectorMasterSoul,
    "DirectorMasterIntuition": DirectorMasterIntuition,
    "DirectorMasterFusion": DirectorMasterFusion,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DirectorMasterCore": "🎬 核心 [导演起点] → 统一电影提示词+核心数据包(11维+600导演库)",
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
    "DirectorMasterCoCreator": "🤝 共创 [V15.0 AI共创循环: 失败记忆/方向分支/门阵/精炼/预算收敛, 无端点确定性可运行]",
    "DirectorMasterSoul": "💠 灵魂 [V15.0 灵魂引擎: 创作者体验→物件/动作/沉默母题, 场景驱动零罐头]",
    "DirectorMasterIntuition": "⚡ 直觉 [V15.0 直觉引擎: 确定性反常规镜头语法, 风险分级 safe/bold/chaotic]",
    "DirectorMasterFusion": "🎨 融合 [V15.0 风格融合: 主0.6/次0.3/反0.1 确定性融合, 反风格突破指令]",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# =====================================================================
# V15.0-MERGED: 16 超级节点 + DirectorMasterFinal 别名 (共 17 注册)。
# 每个超级节点以下拉框聚合几十种模式, 能力全覆盖。
# V15.0 新增 3 个 AI 赋能节点 (共创/灵魂/直觉), 全部确定性可降级。
# V14 之前的 46 个 legacy 细粒度节点作为可选兼容层保留 (V16.0 修订: 恢复 V14.2 的兼容机制):
#   默认不注册 (避免节点选择器臃肿); 设环境变量 DIRECTORMASTER_LEGACY_NODES=1 恢复全部 legacy 节点。
#   (其中 mv_pro/picture_book_pro/comic_drama_pro 等引擎库同时被超级节点作为内部引擎接线。)
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
        print("[DirectorMaster] 兼容层部分旧模块加载失败 (不影响 16 超级节点):")
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

# 标记 V16.1.1-MERGED 版本 (V16.1.1: 三通道深度审计修复 — 安全/正确性/口径统一)
__version__ = "16.1.1"
__description__ = ("V15.0-MERGED = V14.3-MERGED + AI赋能升级。"
                   "导演库534→600(当代新锐/跨界/非西方66位真实导演17维); 风格融合(主0.6/次0.3/反0.1确定性); "
                   "直觉引擎(确定性反常规镜头语法8规则, 真实作者电影依据); 灵魂引擎(创作者体验→物件/动作/沉默母题, 零罐头); "
                   "多模态理解(真实图像分析, 音视频诚实降级); 共创引擎(五阶段循环: 失败记忆/方向分支/门阵/精炼/预算收敛, "
                   "基于Self-Refine/Reflexion/GoT/Best-of-N研究, 无端点确定性可运行); 反AI正则检测层。"
                   "新增4节点: CoCreator/Soul/Intuition/Fusion → 16超级节点+Final别名=17注册。"
                   "V16.0.1修订: 恢复46个legacy细粒度节点可选兼容层(DIRECTORMASTER_LEGACY_NODES=1 → 63节点, 0加载错误)。"
                   "V16.1输出AIGC化: 叙事编排引擎(正叙/倒叙结果先行/穿插倒叙/穿插乱叙/循环叙事 × 单线/双线/三线/POV, "
                   "确定性时序重排+时间线/线索图谱+导演批注+字幕位); 每镜七要素AIGC提示词(参考绑定/主体动作/空间/镜头/视觉/音频/约束, "
                   "Seedance2.5/Wan3.0官方手册范式)+首帧提示词+音频三轴声学; 短形态AIGC五段结构(核心主题/人物设定/氛围画质/运镜规则/画面内容+结尾克制+模型建议+自检); "
                   "去AI味文本质量层(空洞词具象翻译表/后缀去复读/元语言出清); 剧本/分镜/交付JSON三路全注入。"
                   "V16.1.0场景锚定: 输入场景(location/time/weather/objects)主导分镜生成, 修复随机池导致的场景脱节; "
                   "二级空间词+语义兜底+英文兜底保证无锚点输入也贴合; 单字关键词复合词守卫(上海/国家/江山不误判)。"
                   "V16.1.1审计修复: 版本库锁Windows进程探活只读化(不再误杀持锁ComfyUI实例)+token原子写入消除竞态窗口; "
                   "SSRF防护加固(IP钉扎直连消除DNS rebinding/TOCTOU, DNS失败fail-closed, ipaddress规范化黑名单覆盖IPv4映射/云metadata形态); "
                   "身体细节池重复键合并(8条细节找回); Cinematic核心时长真实继承; 节奏分类键名对齐; 死代码清扫; 弧位按比例判定; "
                   "POV切换按真实角色名; 口径统一(534→600文案/诊断6→7类/元数据17节点)。")
