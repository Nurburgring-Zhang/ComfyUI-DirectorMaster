# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V16.0-MERGED — 17 注册节点 (16 超级节点 + Final 别名) + 600 导演库
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
# V14 之前的 46 个 legacy 细粒度节点及其注册机制已在 V14.3 彻底移除
# (其中 mv_pro/picture_book_pro/comic_drama_pro 等引擎库仍作为内部引擎被超级节点接线)。
# =====================================================================

# 兜底: 仍无显示名的注册节点, 用类名生成
for _k in NODE_CLASS_MAPPINGS:
    NODE_DISPLAY_NAME_MAPPINGS.setdefault(_k, _k)

# V13 修复 (A-03): 旧工作流引用的 DirectorMasterFinal 已改名 DirectorMasterSummary — 加别名兼容
NODE_CLASS_MAPPINGS.setdefault("DirectorMasterFinal", DirectorMasterSummary)
NODE_DISPLAY_NAME_MAPPINGS.setdefault("DirectorMasterFinal", "🏆 终极汇总 [终点·DirectorMasterSummary 别名]")

# 标记 V15.0-MERGED 版本
__version__ = "16.0.0"
__description__ = ("V15.0-MERGED = V14.3-MERGED + AI赋能升级。"
                   "导演库534→600(当代新锐/跨界/非西方66位真实导演17维); 风格融合(主0.6/次0.3/反0.1确定性); "
                   "直觉引擎(确定性反常规镜头语法8规则, 真实作者电影依据); 灵魂引擎(创作者体验→物件/动作/沉默母题, 零罐头); "
                   "多模态理解(真实图像分析, 音视频诚实降级); 共创引擎(五阶段循环: 失败记忆/方向分支/门阵/精炼/预算收敛, "
                   "基于Self-Refine/Reflexion/GoT/Best-of-N研究, 无端点确定性可运行); 反AI正则检测层。"
                   "新增4节点: CoCreator/Soul/Intuition/Fusion → 16超级节点+Final别名=17注册。")
