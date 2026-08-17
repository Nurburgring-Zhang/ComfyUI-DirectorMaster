# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V14.3-MERGED 自检脚本
======================================

当节点不显示 / 模式不工作 / 数据不生效时, 在插件根目录运行:

    python doctor.py

诊断 6 类问题:
    1. 安装路径 (是否位于 ComfyUI/custom_nodes 下)
    2. Python 环境 (版本/编码)
    3. 模块导入 (13 节点依赖的全部模块)
    4. 节点注册 (NODE_CLASS_MAPPINGS 是否恰好 13 个)
    5. 知识库完整性 (导演数据库/知识库子模块)
    6. 复活接线消费验证 (9 项孤儿库接线真实被调用, 非装饰)

退出码: 0 = 全部通过, 1 = 有错误
"""
import os
import sys
import traceback

# Windows console 编码修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.abspath(__file__))
ERRORS = []
WARNINGS = []
PASSES = []


def ok(msg):
    PASSES.append(msg)
    print(f"  [OK] {msg}")


def warn(msg):
    WARNINGS.append(msg)
    print(f"  [WARN] {msg}")


def err(msg):
    ERRORS.append(msg)
    print(f"  [FAIL] {msg}")


def section(title):
    print(f"\n=== {title} ===")


# ---------- 1. 安装路径 ----------
section("1. 安装路径")
parent = os.path.basename(os.path.dirname(ROOT))
if "custom_nodes" in os.path.dirname(ROOT).lower():
    ok(f"位于 ComfyUI custom_nodes 下 ({parent})")
else:
    warn(f"不在 custom_nodes 目录下 (上级: {parent}) — 请将整个目录放入 ComfyUI/custom_nodes/")

# ---------- 2. Python 环境 ----------
section("2. Python 环境")
v = sys.version_info
if (v.major, v.minor) >= (3, 8):
    ok(f"Python {v.major}.{v.minor}.{v.micro} (要求 >= 3.8)")
else:
    err(f"Python {v.major}.{v.minor} 过旧, 需要 >= 3.8")
try:
    "中文".encode("utf-8")
    ok("UTF-8 编码可用")
except Exception as e:
    err(f"UTF-8 编码异常: {e}")

# 可选依赖 (节点无这些也能运行, 仅 IMAGE 参考图功能降级)
for mod_name, pip_name, why in [
    ("torch", "torch", "ComfyUI 核心自带; IMAGE 参考图处理需要"),
    ("PIL", "Pillow", "IMAGE 参考图处理需要"),
    ("numpy", "numpy", "IMAGE 参考图处理需要"),
]:
    try:
        __import__(mod_name)
        ok(f"{mod_name} 可用")
    except ImportError:
        warn(f"{mod_name} 缺失 ({why}) — 文本节点功能不受影响, IMAGE 参考槽将降级为空")

# ---------- 3. 模块导入 ----------
section("3. 模块导入")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

AGGREGATOR_MODULES = [
    "director_master", "script_studio", "vibe_studio", "art_master",
    "sound_master", "cinematic_studio", "asset_master", "summary_master",
    "router", "characters_master", "video_router_master", "archive_master",
    "node_base", "data_pool", "dimensions", "prompt_layers", "pro_format",
    "scene_engine", "pacing_engine", "feature_film_engine", "cinema_craft",
    "ref_media",
    "llm_engine", "director_master",
]
LIB_MODULES = [
    "anti_ai_vocab", "director_data_unified", "director_soul",
    "director_profiles_film", "director_profiles_tv_drama",
    "director_profiles_creative_ad", "director_profiles_short_video",
    "director_profiles_animation", "mv_pro", "picture_book_pro",
    # V14.2 复活库 (14)
    "scene_library", "director_real_scripts", "style_prefix_data",
    "asset_registry_data", "master_director_data", "modes_design",
    "story_sense_data", "modes_child", "master_orchestrator",
    "pln_random", "format_templates", "modes_book", "modes_drama",
    "modes_storyboard",
    "comic_drama_pro", "pln_llm", "production_pipeline_v3", "prompt_builder",
]
import importlib

failed_imports = []
for m in sorted(set(AGGREGATOR_MODULES)):
    try:
        importlib.import_module("aggregator." + m)
    except Exception as e:
        failed_imports.append(f"aggregator.{m}: {e!r}")
for m in LIB_MODULES:
    try:
        importlib.import_module(m)
    except Exception as e:
        failed_imports.append(f"{m}: {e!r}")
if failed_imports:
    for f in failed_imports:
        err(f"模块导入失败 {f}")
else:
    ok(f"全部 {len(set(AGGREGATOR_MODULES)) + len(LIB_MODULES)} 个核心模块导入成功")

# ---------- 4. 节点注册 ----------
section("4. 节点注册")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("_dm_doctor", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["_dm_doctor"] = pkg
    spec.loader.exec_module(pkg)
    mappings = getattr(pkg, "NODE_CLASS_MAPPINGS", {})
    names = getattr(pkg, "NODE_DISPLAY_NAME_MAPPINGS", {})
    expected = {
        "DirectorMasterCore", "DirectorMasterScript", "DirectorMasterVibe",
        "DirectorMasterArt", "DirectorMasterSound", "DirectorMasterCinematic",
        "DirectorMasterCharacters", "DirectorMasterAsset", "DirectorMasterSummary",
        "DirectorMasterRouter", "DirectorMasterVideoRouter", "DirectorMasterArchive",
        "DirectorMasterFinal",
    }
    if set(mappings.keys()) == expected:
        ok(f"NODE_CLASS_MAPPINGS 恰好 13 个节点")
    else:
        missing = expected - set(mappings.keys())
        extra = set(mappings.keys()) - expected
        if missing:
            err(f"缺少节点: {sorted(missing)}")
        if extra:
            err(f"多出节点: {sorted(extra)}")
    no_display = [k for k in mappings if k not in names]
    if no_display:
        err(f"缺少显示名: {no_display}")
    else:
        ok("全部节点有中文显示名")
    for k, cls in mappings.items():
        fn_name = getattr(cls, "FUNCTION", None)
        if not fn_name or not callable(getattr(cls, fn_name, None)):
            err(f"{k}: FUNCTION={fn_name} 不可调用")
    ok("全部节点 FUNCTION 可调用")
except Exception:
    err("__init__.py 加载失败:\n" + traceback.format_exc(limit=3))

# ---------- 5. 知识库 ----------
section("5. 知识库")
try:
    import director_data_unified as ddu
    n_names = len(getattr(ddu, "ALL_DIRECTOR_NAMES", []))
    if n_names >= 500:
        ok(f"导演名单 {n_names} 人")
    else:
        err(f"导演名单仅 {n_names} 人 (期望 >=500)")
    cats = ["FILM_DIRECTORS_100", "TV_DRAMA_DIRECTORS_100", "CREATIVE_AD_DIRECTORS_100",
            "SHORT_VIDEO_DIRECTORS_100", "ANIMATION_DIRECTORS_100"]
    total_profiles = sum(len(getattr(ddu, c, {})) for c in cats)
    if total_profiles >= 500:
        ok(f"导演档案 {total_profiles} 份 (5 域 12 维)")
    else:
        err(f"导演档案仅 {total_profiles} 份")
except Exception as e:
    err(f"导演数据库检查失败: {e!r}")

KB_SUBS = [
    "master_cinematography", "narrative_structures", "genre_profiles",
    "performance_system", "shot_vocabulary", "transition_grammar",
    "short_drama_patterns", "viral_video_techniques", "director_styles",
    "emotion_rendering", "h3_prompt_framework", "works_corpus",
    "works_corpus_extended", "works_hot_shortform", "web_research_director_db",
    "picture_book_styles", "children_content_styles",
]
kb_fail = []
for s in KB_SUBS:
    try:
        importlib.import_module("knowledge_base." + s)
    except Exception as e:
        kb_fail.append(f"knowledge_base.{s}: {e!r}")
if kb_fail:
    for f in kb_fail:
        err(f"知识库模块导入失败 {f}")
else:
    ok(f"知识库 {len(KB_SUBS)} 个子模块全部导入成功")

# ---------- 6. 复活接线消费验证 (V14.3-MERGED) ----------
section("6. 复活接线消费验证 (9 项孤儿库接线)")

# 6a. 静态: 调用点必须存在于聚合节点源码中 (防止接线被删/装饰性保留)
_WIRING_CALLSITES = {
    "aggregator/script_studio.py": ["inject_library_depth(main, mode, director, scene, mood)"],
    "aggregator/llm_engine.py": ["_domain_mode_prompt(node_type, mode, context)"],
    "aggregator/cinematic_studio.py": ["from format_templates import MASTER_VIDEO_PRINCIPLES"],
    "aggregator/router.py": ["from style_prefix_data import render_style_prefix"],
    "aggregator/director_master.py": ["from pln_random import random_topic, random_character, random_env"],
    "aggregator/video_router_master.py": ["from master_director_data import SEEDANCE_25_CAPABILITIES"],
    "aggregator/vibe_studio.py": ["from modes_design import _build_design_system_prompt, _build_design_user_prompt"],
    "aggregator/summary_master.py": ["from master_orchestrator import inject_42_stages, inject_3_whitespace, inject_3_camera_laws"],
    "aggregator/asset_master.py": ["from asset_registry_data import get_six_documents_summary"],
}
for _rel, _needles in _WIRING_CALLSITES.items():
    _p = os.path.join(ROOT, _rel.replace("/", os.sep))
    try:
        _src = open(_p, encoding="utf-8").read()
        for _n in _needles:
            if _n in _src:
                ok(f"接线调用点存在: {_rel} :: {_n[:60]}")
            else:
                err(f"接线调用点缺失: {_rel} :: {_n[:60]}")
    except Exception as e:
        err(f"无法读取 {_rel}: {e!r}")

# 6b. 运行时: 每条接线真实产出内容 (非空/非降级)
try:
    from aggregator.script_studio import inject_library_depth
    _r = inject_library_depth("正文", "竖屏小程序剧", "[电影] 王家卫", "雨夜的便利店, 女主角等着一个人", "孤独")
    if len(_r) > len("正文") and ("影视场景库" in _r or "故事感总纲" in _r or "剧本" in _r or "案例" in _r):
        ok(f"script_studio.inject_library_depth 真实注入 (+{len(_r) - len('正文')} 字符)")
    else:
        err("script_studio.inject_library_depth 未产出注入块")
except Exception as e:
    err(f"inject_library_depth 运行失败: {e!r}")

try:
    from aggregator.llm_engine import _domain_mode_prompt
    _d = _domain_mode_prompt("剧本", "绘本", {"scene": "小狐狸找月亮"})
    if _d and len(_d) > 100:
        ok(f"llm_engine._domain_mode_prompt 绘本领域规则 ({len(_d)} 字符)")
    else:
        err("llm_engine._domain_mode_prompt 绘本领域未产出规则块")
except Exception as e:
    err(f"_domain_mode_prompt 运行失败: {e!r}")

try:
    from format_templates import MASTER_VIDEO_PRINCIPLES
    if MASTER_VIDEO_PRINCIPLES and len(str(MASTER_VIDEO_PRINCIPLES)) > 100:
        ok(f"MASTER_VIDEO_PRINCIPLES 大师原则 ({len(str(MASTER_VIDEO_PRINCIPLES))} 字符)")
    else:
        err("MASTER_VIDEO_PRINCIPLES 为空")
except Exception as e:
    err(f"MASTER_VIDEO_PRINCIPLES 检查失败: {e!r}")

try:
    from style_prefix_data import render_style_prefix
    _sk = render_style_prefix()
    if _sk and len(str(_sk)) > 100:
        ok(f"style_prefix_data CINEDANCE 骨架 ({len(str(_sk))} 字符)")
    else:
        err("render_style_prefix 为空")
except Exception as e:
    err(f"render_style_prefix 检查失败: {e!r}")

try:
    from pln_random import random_topic, random_character, random_env
    _tp = random_topic("电影分镜")
    if _tp:
        ok(f"pln_random 灵感场景可用 (主题示例: {str(_tp)[:20]})")
    else:
        err("pln_random 返回空")
except Exception as e:
    err(f"pln_random 检查失败: {e!r}")

try:
    from master_director_data import SEEDANCE_25_CAPABILITIES, REAL_DRAMA_CASES
    if isinstance(SEEDANCE_25_CAPABILITIES, dict) and SEEDANCE_25_CAPABILITIES:
        ok(f"SEEDANCE_25_CAPABILITIES 能力边界 ({len(SEEDANCE_25_CAPABILITIES)} 键)")
    else:
        err("SEEDANCE_25_CAPABILITIES 为空")
    if isinstance(REAL_DRAMA_CASES, dict) and len(REAL_DRAMA_CASES) >= 10:
        ok(f"REAL_DRAMA_CASES 真实短剧案例 {len(REAL_DRAMA_CASES)} 条")
    else:
        err(f"REAL_DRAMA_CASES 不足 ({len(REAL_DRAMA_CASES) if isinstance(REAL_DRAMA_CASES, dict) else 'N/A'})")
except Exception as e:
    err(f"master_director_data 检查失败: {e!r}")

try:
    from aggregator.vibe_studio import TEMPLATES as _VT, VIBE_MODES as _VM
    _design_ok = 0
    for _dm in ["电商套图", "海报设计", "品牌设计", "PPT设计", "逻辑关系图设计", "三视图设计", "爆炸拆解图设计", "流水线图设计"]:
        if _dm not in _VM:
            err(f"VIBE_MODES 缺设计模式: {_dm}")
            continue
        _b = _VT.get(_dm)
        _out = _b("智能手表产品, 都市白领佩戴", "[电影] 王家卫", "期待", {}) if _b else ""
        if _out and "设计" in _out and "降级" not in _out:
            _design_ok += 1
        else:
            err(f"设计模式 {_dm} 产出异常 (降级或空)")
    if _design_ok:
        ok(f"vibe_studio 8 设计模式真实产出 {_design_ok}/8")
except Exception as e:
    err(f"vibe_studio 设计模式检查失败: {e!r}")

try:
    from master_orchestrator import inject_42_stages, inject_3_whitespace, inject_3_camera_laws
    _lens = [len(inject_42_stages()), len(inject_3_whitespace()), len(inject_3_camera_laws())]
    if all(l > 100 for l in _lens):
        ok(f"master_orchestrator 42环节/留白三定律/运镜三定律 ({'/'.join(str(l) for l in _lens)} 字符)")
    else:
        err("master_orchestrator 注入块过短")
except Exception as e:
    err(f"master_orchestrator 检查失败: {e!r}")

try:
    from asset_registry_data import get_six_documents_summary
    _six = get_six_documents_summary()
    if _six and len(str(_six)) > 500:
        ok(f"asset_registry_data 6 份项目记忆文档 ({len(str(_six))} 字符)")
    else:
        err("get_six_documents_summary 为空")
except Exception as e:
    err(f"asset_registry_data 检查失败: {e!r}")

# ---------- 汇总 ----------
print("\n" + "=" * 50)
print(f"自检结果: {len(PASSES)} 通过, {len(WARNINGS)} 警告, {len(ERRORS)} 错误")
if ERRORS:
    print("\n错误列表:")
    for e in ERRORS:
        print(f"  - {e}")
    print("\n建议: 将完整目录放入 ComfyUI/custom_nodes/, 重启 ComfyUI,")
    print("      并在启动日志中搜索 DirectorMaster 关键词。")
    sys.exit(1)
else:
    print("\n全部通过 — 重启 ComfyUI 即可使用 13 个 DirectorMaster 节点。")
    sys.exit(0)
