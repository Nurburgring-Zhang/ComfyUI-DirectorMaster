# -*- coding: utf-8 -*-
"""
ComfyUI-DirectorMaster V16.3.0 自检脚本
======================================

当节点不显示 / 模式不工作 / 数据不生效时, 在插件根目录运行:

    python doctor.py

诊断 9 类问题:
    1. 安装路径 (是否位于 ComfyUI/custom_nodes 下)
    2. Python 环境 (版本/编码)
    3. 模块导入 (18 节点依赖的全部模块)
    4. 节点注册 (NODE_CLASS_MAPPINGS 是否恰好 18 个)
    5. 知识库完整性 (导演数据库/知识库子模块)
    6. 复活接线消费验证 (9 项孤儿库接线真实被调用, 非装饰)
    7. V15.0 引擎运行时消费验证 (融合/直觉/灵魂/多模态/共创/反AI)
    8. V16.2.0 加载隔离与 LLM 容错 (隔离清单/预设注册表/三态路由/别名容错)
    9. 模式卡与分镜契约一致性 (manifest 三方对账 / 模式卡索引 sync 校验 / 分镜 JSON 契约 v1)

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
    "style_fusion", "intuition_engine", "soul_engine", "multimodal_engine",
    "failure_memory", "cocreator_engine", "v15_nodes",
    # V16.1 叙事编排引擎 + AIGC 提示词构建器 + AIGC 适配器
    "narrative_arrangement", "aigc_prompt_builder", "aigc_adapter",
    # V16.4 情节拓扑引擎
    "plot_topology",
    # V16.7 批次3 D6 独立审查引擎
    "review_engine",
]
LIB_MODULES = [
    "anti_ai_vocab", "director_data_unified",
    "director_profiles_film", "director_profiles_tv_drama",
    "director_profiles_creative_ad", "director_profiles_short_video",
    "director_profiles_animation", "mv_pro", "picture_book_pro",
    # V14.2 复活库 (14)
    "scene_library", "director_real_scripts", "style_prefix_data",
    "asset_registry_data", "master_director_data", "modes_design",
    "story_sense_data", "modes_child", "master_orchestrator",
    "pln_random", "format_templates", "modes_book", "modes_drama",
    "modes_storyboard",
    "comic_drama_pro", "pln_llm",
    # V15.0-MERGED 引擎与数据
    "director_profiles_extended",
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
        "DirectorMasterCoCreator", "DirectorMasterSoul", "DirectorMasterIntuition",
        "DirectorMasterFusion", "DirectorMasterReview",
        "DirectorMasterFinal",
    }
    if set(mappings.keys()) == expected:
        ok(f"NODE_CLASS_MAPPINGS 恰好 18 个节点 (17 超级 + Final 别名)")
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

# ---------- 7. V15.0 引擎运行时消费验证 ----------
section("7. V15.0 引擎运行时消费验证")
try:
    import director_data_unified as _ddu
    if len(_ddu.DIRECTOR_PROFILES_ALL) >= 600:
        ok(f"导演库扩容 {len(_ddu.DIRECTOR_PROFILES_ALL)} 档案 (≥600)")
    else:
        err(f"导演库仅 {len(_ddu.DIRECTOR_PROFILES_ALL)} 档案 (<600)")
except Exception as e:
    err(f"导演库扩容检查失败: {e!r}")

try:
    from aggregator.style_fusion import fuse_styles
    _fr = fuse_styles("[电影] 王家卫", "是枝裕和", "滨口龙介", scene="雨夜厨房", mood="孤独")
    if _fr["text"] and not _fr["error"] and _fr["break_directive"]:
        ok("风格融合引擎 (主/次/反 + 突破指令)")
    else:
        err(f"风格融合异常: {_fr.get('error') or '突破指令缺失'}")
except Exception as e:
    err(f"风格融合检查失败: {e!r}")

try:
    from aggregator.intuition_engine import apply_intuition
    _shots = [{"n": i, "size": "特写", "move": "跟拍", "focal": "85mm", "dur": "5s",
               "dur_sec": 5.0, "focus": "焦", "sound": "声", "tension_level": 8 if i == 3 else 5,
               "angle": "平视", "cut": "硬切"} for i in range(1, 7)]
    _m, _log = apply_intuition(_shots, mood="孤独", scene="父女对话", risk_level="bold", seed="doctor")
    _m2, _ = apply_intuition(_shots, mood="孤独", scene="父女对话", risk_level="bold", seed="doctor")
    if _log and _m == _m2:
        ok(f"直觉引擎 (触发 {len(_log)} 条规则, 确定性)")
    else:
        err("直觉引擎触发为空或非确定性")
except Exception as e:
    err(f"直觉引擎检查失败: {e!r}")

try:
    from aggregator.soul_engine import inject_soul
    _sr = inject_soul("剧本: 父亲藏着一个秘密。", creator_experience="奶奶的旧怀表, 一次没来得及的告别",
                      emotional_intent="思念", scene="厨房, 旧信", objects=["旧信"], characters=["父亲"])
    if _sr["fragments"] and "奶奶的旧怀表" in str(_sr["fragments"]):
        ok("灵魂引擎 (母题从创作者体验派生, 零罐头)")
    else:
        err("灵魂引擎母题未从输入派生")
except Exception as e:
    err(f"灵魂引擎检查失败: {e!r}")

try:
    import numpy as _np
    from aggregator.multimodal_engine import analyze_image
    _img = _np.zeros((32, 32, 3)); _img[:16, :, :] = [200, 50, 50]
    _ia = analyze_image(_img)
    if _ia["ok"] and _ia["palette"]:
        ok("多模态图像分析 (真实计算)")
    else:
        err(f"多模态分析失败: {_ia.get('error')}")
except ImportError:
    warn("numpy 不可用 — 多模态图像分析降级 (不影响其他功能)")
except Exception as e:
    err(f"多模态检查失败: {e!r}")

try:
    import tempfile as _tf, shutil as _sh
    from aggregator.cocreator_engine import co_create
    _tmp = _tf.mkdtemp(prefix="dm_doctor_cc_")
    try:
        _cc = co_create("妹妹寻找失踪的姐姐, 真相被藏起来", emotional_intent="悬疑中的温情",
                        mood="悬疑", store_dir=_tmp)
        if _cc["chosen"] and len(_cc["directions"]) == 3 and all(g["pass"] for g in _cc["gate_report"]):
            ok(f"共创引擎 (T0确定性档, 3方向分支, 门全过, 选定[{_cc['chosen']}])")
        else:
            err("共创引擎分支/门控异常")
    finally:
        _sh.rmtree(_tmp, ignore_errors=True)
except Exception as e:
    err(f"共创引擎检查失败: {e!r}")

try:
    from anti_ai_vocab import count_regex_hits
    _n, _ = count_regex_hits("综上所述, 在这个故事中, 时光荏苒")
    if _n >= 2:
        ok(f"反AI正则检测层 (命中 {_n} 处)")
    else:
        err("反AI正则检测层未命中")
except Exception as e:
    err(f"反AI正则检测检查失败: {e!r}")

# ---------- 8. V16.2.0 加载隔离与 LLM 容错 ----------
section("8. V16.2.0 加载隔离与 LLM 容错")

# 预载包模块 (与第 4 节同一 spec 模式), 供 8a/8b 读取 DM_QUARANTINE / load_node_classes
_pkg16 = None
try:
    import importlib.util as _ilu16
    _spec16 = _ilu16.spec_from_file_location("_dm_doctor_s8", os.path.join(ROOT, "__init__.py"))
    _pkg16 = _ilu16.module_from_spec(_spec16)
    sys.modules["_dm_doctor_s8"] = _pkg16
    _spec16.loader.exec_module(_pkg16)
except Exception as e:
    err(f"__init__.py 加载失败, 无法做隔离检查: {e!r}")

# 8a. 加载隔离清单必须为空 (全部 17 超级节点健康加载)
if _pkg16 is not None:
    try:
        _q = getattr(_pkg16, "DM_QUARANTINE", None)
        if _q is None:
            err("DM_QUARANTINE 不存在 (__init__.py 非 V16.2.0 结构)")
        elif not _q:
            ok("加载隔离清单为空 (17 超级节点全部健康加载)")
        else:
            for _qi in _q:
                err(f"节点被隔离: {_qi.get('target')} [{_qi.get('phase')}] {_qi.get('error')}")
    except Exception as e:
        err(f"隔离清单检查失败: {e!r}")

# 8b. load_node_classes 独立机制: 真实重新加载并核对 16 类
if _pkg16 is not None:
    try:
        _lnc = getattr(_pkg16, "load_node_classes", None)
        if _lnc is None:
            err("load_node_classes 不存在 (__init__.py 非 V16.2.0 结构)")
        else:
            _loaded = _lnc()
            _expected16 = {
                "DirectorMasterCore", "DirectorMasterScript", "DirectorMasterVibe",
                "DirectorMasterArt", "DirectorMasterSound", "DirectorMasterCinematic",
                "DirectorMasterCharacters", "DirectorMasterAsset", "DirectorMasterSummary",
                "DirectorMasterRouter", "DirectorMasterVideoRouter", "DirectorMasterArchive",
                "DirectorMasterCoCreator", "DirectorMasterSoul", "DirectorMasterIntuition",
                "DirectorMasterFusion", "DirectorMasterReview",
            }
            if set(_loaded.keys()) == _expected16:
                ok("load_node_classes 隔离加载机制正常 (17/17 类)")
            else:
                err(f"load_node_classes 结果异常: 缺 {sorted(_expected16 - set(_loaded))} 多 {sorted(set(_loaded) - _expected16)}")
            # 隔离分支真实可用: 故意传一个不存在的模块, 应进隔离而非崩溃
            _iso_q = []
            _iso_loaded = _lnc(specs=[("aggregator.__definitely_not_exist__", "X")], quarantine=_iso_q)
            if _iso_loaded == {} and len(_iso_q) == 1 and _iso_q[0]["phase"] == "import":
                ok("load_node_classes 故障隔离分支真实生效 (坏模块入隔离不崩溃)")
            else:
                err(f"load_node_classes 故障隔离分支异常: loaded={_iso_loaded} q={_iso_q}")
    except Exception as e:
        err(f"load_node_classes 检查失败: {e!r}")

# 8c. provider 预设注册表 (内置 10 预设)
try:
    import pln_llm as _pl
    _presets = _pl.get_provider_presets()
    if isinstance(_presets, dict) and len(_presets) >= 8:
        ok(f"provider 预设注册表 {len(_presets)} 个 (含 openai/deepseek/ollama/...)")
    else:
        err(f"provider 预设注册表异常: {len(_presets) if isinstance(_presets, dict) else type(_presets)}")
    # 预设 → URL 匹配 + 降级链构建真实可用
    _pid, _preset = _pl.get_preset_for_url("https://api.deepseek.com/v1/chat/completions")
    _chain = _pl.build_fallback_chain("https://api.deepseek.com/v1/chat/completions", "k", "deepseek-reasoner")
    if _pid == "deepseek" and len(_chain) >= 2 and _chain[0]["source"] == "primary":
        ok(f"预设匹配+降级链构建真实可用 (deepseek, 链长 {len(_chain)})")
    else:
        err(f"预设匹配/降级链异常: pid={_pid} chain={len(_chain)}")
except Exception as e:
    err(f"provider 预设注册表检查失败: {e!r}")

# 8d. 三态降级状态机 (确定性, 无网络)
try:
    import pln_llm as _pl
    _pl.reset_router_state()
    _url = "http://router-selftest.local/v1"
    for _ in range(_pl.FAILURE_THRESHOLD):
        _pl._router_record_failure(_url, "SERVER")
    _st = _pl.get_router_status(_url)
    if _st and _st["state"] == "fallback_active":
        ok(f"三态状态机: 连续 {_pl.FAILURE_THRESHOLD} 次失败 → fallback_active")
    else:
        err(f"三态状态机异常: {_st}")
    _prior = _pl._router_record_success(_url)
    _st2 = _pl.get_router_status(_url)
    if _st2["state"] == "primary_ok" and _st2["consecutive_failures"] == 0 and _prior == "fallback_active":
        ok("三态状态机: 主端点成功 → primary_ok (清零)")
    else:
        err(f"三态状态机恢复异常: {_st2}")
    _pl.reset_router_state()
except Exception as e:
    err(f"三态状态机检查失败: {e!r}")

# 8e. 错误分类 + 溢出两层压缩 (确定性)
try:
    import pln_llm as _pl
    if _pl._classify_llm_failure(429, "") == "RATE_LIMIT" and \
       _pl._classify_llm_failure(401, "") == "AUTH" and \
       _pl._classify_llm_failure(400, "maximum context length exceeded") == "OVERFLOW":
        ok("错误分类器 (429→RATE_LIMIT / 401→AUTH / 溢出短语→OVERFLOW)")
    else:
        err("错误分类器异常")
    _long = "分镜内容占位文本。" * 200  # >400 字符
    _g = _pl.compress_context_gentle(_long)
    _a = _pl.compress_context_aggressive(_long)
    if _g and _a and len(_a) < len(_g) < len(_long) and \
       _pl.COMPRESS_MARKER in _g and _pl.COMPRESS_MARKER in _a:
        ok(f"溢出两层压缩 (gentle {len(_g)} < 原文 {len(_long)}, aggressive {len(_a)})")
    else:
        err("溢出压缩异常")
    if _pl.compress_context_gentle("短") is None:
        ok("短文本不可压 (返回 None, 不伪造)")
    else:
        err("短文本压缩应返回 None")
except Exception as e:
    err(f"错误分类/压缩检查失败: {e!r}")

# 8f. 别名容错 + 宽容 JSON
try:
    import pln_llm as _pl
    _r1 = _pl.resolve_json_field({"shots": [1, 2]}, "shots")
    _r2 = _pl.resolve_json_field({"镜头": [3]}, "shots")
    _r3 = _pl.resolve_json_field({"shot_list": [4]}, "shots")
    _r4 = _pl.resolve_json_field({"nothing": 0}, "shots", default="D")
    if _r1 == [1, 2] and _r2 == [3] and _r3 == [4] and _r4 == "D":
        ok("字段别名四级容错 (精确/中文/别名/default)")
    else:
        err(f"别名容错异常: {_r1} {_r2} {_r3} {_r4}")
    _j1, _d1 = _pl.json_loads_tolerant('```json\n{"a": 1,}\n```')
    _j2, _d2 = _pl.json_loads_tolerant('{"b": 2} 尾部噪声')
    if _j1 == {"a": 1} and _j2 == {"b": 2}:
        ok("宽容 JSON 解析 (代码围栏+尾逗号 / 尾部噪声)")
    else:
        err(f"宽容 JSON 异常: {_j1} {_j2}")
except Exception as e:
    err(f"别名容错/宽容JSON检查失败: {e!r}")

# ---------- 9. 模式卡与分镜契约一致性 (V16.3.0 批次2) ----------
section("9. 模式卡与分镜契约一致性")

# 9a. manifest 单一事实源在场且可解析 (缺失 = ERR)
_manifest9 = None
_manifest_path9 = os.path.join(ROOT, "tests", "mode_manifest.json")
if not os.path.exists(_manifest_path9):
    err("mode_manifest.json 缺失 (tests/mode_manifest.json) — 模式卡单一事实源未建立")
else:
    try:
        import json as _json9
        with open(_manifest_path9, encoding="utf-8") as _f9:
            _manifest9 = _json9.load(_f9)
        if (_manifest9.get("version") != 1 or not isinstance(_manifest9.get("nodes"), dict)
                or not isinstance(_manifest9.get("total_creative"), int)):
            err("mode_manifest.json 结构异常 (version/nodes/total_creative)")
            _manifest9 = None
        else:
            ok(f"mode_manifest.json 可解析 (total_creative={_manifest9['total_creative']})")
    except Exception as e:
        err(f"mode_manifest.json 解析失败: {e!r}")
        _manifest9 = None

# 9b. manifest 枚举 vs live INPUT_TYPES 三方核对 (10 个模式下拉逐位比对)
_widgets9 = None
try:
    from tools.dump_mode_manifest import get_mode_widgets as _get_widgets9
    _widgets9 = _get_widgets9()
except Exception as e:
    err(f"锚点工具不可用 (tools/dump_mode_manifest.py): {e!r}")
if _manifest9 is not None and _widgets9 is not None:
    if _pkg16 is None:
        try:
            import importlib.util as _ilu9
            _spec9 = _ilu9.spec_from_file_location("_dm_doctor_s9", os.path.join(ROOT, "__init__.py"))
            _pkg16 = _ilu9.module_from_spec(_spec9)
            sys.modules["_dm_doctor_s9"] = _pkg16
            _spec9.loader.exec_module(_pkg16)
        except Exception as e:
            err(f"节点包加载失败, 无法做 manifest 枚举核对: {e!r}")
    if _pkg16 is not None:
        try:
            _mism9 = []
            _mnodes9 = _manifest9["nodes"]
            if set(_mnodes9) != set(_widgets9):
                _mism9.append(f"节点集合不一致: {sorted(set(_mnodes9) ^ set(_widgets9))}")
            for _n9, _w9 in _widgets9.items():
                _cls9 = _pkg16.NODE_CLASS_MAPPINGS.get(_n9)
                _rec9 = _mnodes9.get(_n9)
                if _cls9 is None or _rec9 is None:
                    _mism9.append(f"{_n9}: 节点或 manifest 记录缺失")
                    continue
                _live9 = [str(o) for o in _cls9.INPUT_TYPES()["required"][_w9][0]]
                if _live9 != list(_rec9.get("options", [])):
                    _mism9.append(f"{_n9}: 枚举与 manifest 不一致 "
                                  f"(live {len(_live9)} 项 vs manifest {len(_rec9.get('options', []))} 项)")
            if _mism9:
                for _m in _mism9:
                    err(f"manifest 枚举核对失败: {_m}")
            else:
                ok("manifest 枚举 == live INPUT_TYPES (%d 节点三方一致)" % len(_widgets9))
        except Exception as e:
            err(f"manifest 枚举核对异常: {e!r}")

# 9c. 模式卡目录 ↔ manifest 对账 (内嵌复用 tools/sync_mode_index 校验逻辑)
_cards_root9 = os.path.join(ROOT, "knowledge_base", "mode_cards")
_card_count9 = 0
if os.path.isdir(_cards_root9):
    for _slug9 in os.listdir(_cards_root9):
        _sd9 = os.path.join(_cards_root9, _slug9)
        if os.path.isdir(_sd9):
            _card_count9 += sum(1 for _f9 in os.listdir(_sd9)
                                if _f9.lower().endswith(".md")
                                and os.path.isfile(os.path.join(_sd9, _f9)))
if _manifest9 is not None:
    _total9 = _manifest9.get("total_creative")
    if _card_count9 == 0:
        warn(f"模式卡待建({_card_count9}/{_total9}) — Wave B 撰写中, 不影响其他诊断")
    else:
        try:
            from tools.sync_mode_index import run_validation as _run_val9
            _res9 = _run_val9(ROOT)
            if _res9["ok"]:
                ok(f"模式卡 {_card_count9}/{_total9} 与 manifest 对账一致 (sync 校验通过)")
            else:
                for _v9 in _res9["violations"][:10]:
                    err(f"模式卡对账违例: {_v9}")
                if len(_res9["violations"]) > 10:
                    err(f"模式卡对账违例共 {len(_res9['violations'])} 项 "
                        f"(仅列前 10; 完整清单: python tools/sync_mode_index.py --check)")
        except Exception as e:
            err(f"sync 校验逻辑调用失败: {e!r}")

# 9d. 分镜 JSON 契约 v1 (并行 builder 交付物; 未就绪 = WARN 不拦诊断)
try:
    from aggregator.storyboard_contract import (STORYBOARD_CONTRACT_VERSION as _sbv9,
                                                self_check as _sbself9)
except Exception as e:
    warn(f"分镜契约模块未就绪 (并行 builder 撰写中): {type(e).__name__}: {e}")
else:
    try:
        _sb_ok9 = _sbself9()
    except Exception as e:
        err(f"分镜契约自检异常 (self_check 约定永不抛): {e!r}")
    else:
        if _sbv9 in (1, 2) and _sb_ok9 is True:
            ok(f"分镜 JSON 契约 (STORYBOARD_CONTRACT_VERSION={_sbv9}, "
               "合法最小样例过 validate_storyboard 且相对时间拓扑解析正确)")
        else:
            err(f"分镜契约断言失败: version={_sbv9!r}, self_check={_sb_ok9!r}")

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
    print("\n全部通过 — 重启 ComfyUI 即可使用 18 个 DirectorMaster 节点。")
    sys.exit(0)
