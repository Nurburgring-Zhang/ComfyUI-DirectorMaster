# -*- coding: utf-8 -*-
"""
批次7 WaveB builder-e3 — DirectorMasterNovelIntake 节点测试 (tests/test_episode_node.py)
====================================================================================
覆盖:
  T1 注册: 类在 NODE_CLASS_MAPPINGS 且 DM_QUARANTINE 为空; 显示名在
     NODE_DISPLAY_NAME_MAPPINGS 且非空
  T2 形状: INPUT_TYPES 必含 required "小说原文" (forceInput); RETURN_TYPES/
     RETURN_NAMES/FUNCTION/CATEGORY 非空
  T3 运行时: 2-3 章小小说 → 实例化调 FUNCTION → 结果[0] 报告含集数与 ok;
     结果[1] JSON 解析 ok=True 且 episodes ≥1; 产物目录 <out_dir>/episodes/ 存在
  T4 诚实失败: 空小说原文 → json ok=False、errors 非空、报告含诚实上报标记,
     节点不抛异常不崩
  T5 输出目录兜底: 输出目录留空 → 裸环境落系统临时目录 DirectorMasterIntake
     (folder_paths 惰性导入, 顶层不触 ComfyUI)
纪律: 测试产物一律 tempfile, 零仓库内写入。退出码: 0 = 无 FAIL。
运行: python -X utf8 tests/test_episode_node.py
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASS, FAIL = 0, 0
TEMP_DIRS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def temp_dir():
    d = tempfile.mkdtemp(prefix="ep_node_test_")
    TEMP_DIRS.append(d)
    return d


def make_novel(chapters=3):
    parts = []
    for ci in range(1, chapters + 1):
        body = "".join(
            "林照在%d章%d段山路上遇见了商队，为首的独眼汉子盘查比往日严了三倍，"
            "最终挥手放行。\n" % (ci, pi)
            for pi in range(1, 5))
        parts.append(f"第{ci}章 夜行{ci}\n" + body)
    return "".join(parts)


# ----------------------------------------------------------------
print("T1 注册 (NODE_CLASS_MAPPINGS / DM_QUARANTINE / 显示名)")
# 与 test_load_isolation 同法: spec_from_file_location 加载根 __init__.py
# (模拟 ComfyUI loader, 无 ComfyUI 环境), 避免包导入路径冲突
pkg = None
try:
    _spec = importlib.util.spec_from_file_location(
        "_dm_ep_node_pkg", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(_spec)
    sys.modules["_dm_ep_node_pkg"] = pkg
    _spec.loader.exec_module(pkg)
except Exception as e:
    check("根包加载", False, repr(e)[:200])
cls = (pkg or {}).NODE_CLASS_MAPPINGS.get("DirectorMasterNovelIntake") if pkg else None
check("DirectorMasterNovelIntake 在 NODE_CLASS_MAPPINGS", cls is not None)
check("DM_QUARANTINE 为空 (新节点健康加载)",
      pkg is not None and pkg.DM_QUARANTINE == [],
      f"q={getattr(pkg, 'DM_QUARANTINE', None)}")
disp = (pkg.NODE_DISPLAY_NAME_MAPPINGS.get("DirectorMasterNovelIntake", "")
        if pkg else "")
check("显示名在 NODE_DISPLAY_NAME_MAPPINGS 且非空", bool(disp and disp.strip()),
      f"disp={disp[:60]!r}")
check("显示名口径含长篇接入", "长篇接入" in disp, f"disp={disp[:60]!r}")

# ----------------------------------------------------------------
print("T2 形状 (INPUT_TYPES / RETURN / FUNCTION / CATEGORY)")
if cls is None:
    check("T2 依赖 T1 (cls 在册)", False)
else:
    it = cls.INPUT_TYPES()
    req = it.get("required", {})
    check("required 必含 小说原文", "小说原文" in req)
    check("小说原文 为 STRING multiline forceInput",
          req.get("小说原文", ("",))[0] == "STRING"
          and req.get("小说原文", (None, {}))[1].get("multiline") is True
          and req.get("小说原文", (None, {}))[1].get("forceInput") is True)
    opt = it.get("optional", {})
    check("optional 含 项目名/每集目标字数/输出目录/AI接口地址",
          all(k in opt for k in ("项目名", "每集目标字数", "输出目录", "AI接口地址")))
    tgt = opt.get("每集目标字数", (None, {}))
    check("每集目标字数 INT default 8000 min 200",
          tgt[0] == "INT" and tgt[1].get("default") == 8000
          and tgt[1].get("min") == 200)
    check("RETURN_TYPES == (STRING, STRING)",
          cls.RETURN_TYPES == ("STRING", "STRING"))
    check("RETURN_NAMES == (接入报告, 管线JSON)",
          cls.RETURN_NAMES == ("接入报告", "管线JSON"))
    check("FUNCTION == novel_intake", cls.FUNCTION == "novel_intake")
    check("CATEGORY 非空", bool(str(cls.CATEGORY).strip()))
    check("NODE_TYPE == 长篇接入", getattr(cls, "NODE_TYPE", "") == "长篇接入")

# ----------------------------------------------------------------
print("T3 运行时 (2-3 章小小说 → FUNCTION → 报告+JSON+产物目录)")
if cls is None:
    check("T3 依赖 T1 (cls 在册)", False)
else:
    node = cls()
    out_dir = temp_dir()
    novel3 = make_novel(3)
    try:
        res = getattr(node, cls.FUNCTION)(
            小说原文=novel3, 项目名="节点测试项目",
            每集目标字数=400, 输出目录=out_dir)
        check("返回二元组", isinstance(res, tuple) and len(res) == 2)
        report, js = str(res[0]), res[1]
        check("报告含 ok 状态", "ok" in report)
        check("报告含集数/分集清单", "集数" in report and "分集清单" in report)
        check("报告含 ep_000 首集", "ep_000" in report)
        try:
            meta = json.loads(js)
        except Exception as e:
            meta = None
            check("JSON 可解析", False, repr(e)[:120])
        if isinstance(meta, dict):
            check("JSON ok=True", meta.get("ok") is True)
            check("JSON episodes ≥1", len(meta.get("episodes") or []) >= 1,
                  f"n={len(meta.get('episodes') or [])}")
            check("JSON errors 为空", meta.get("errors") == [])
            check("JSON 覆盖账本 ok",
                  (meta.get("ledger_summary") or {}).get("ok") is True)
            eps = meta.get("episodes") or []
            check("每集产物 9 键齐全",
                  eps and all(
                      all(k in e for k in ("ep_id", "title", "span", "text",
                                           "anchors", "hooks", "logline",
                                           "checkpoint_ref", "core_pack_seed"))
                      for e in eps))
            check("锚点回溯逐字节 (int 偏移, quote==原文[start:end], 锚点落在集 span 内)",
                  all(isinstance(a.get("start"), int) and isinstance(a.get("end"), int)
                      and novel3[a["start"]:a["end"]] == a["quote"]
                      and e["span"]["start"] <= a["start"] < e["span"]["end"]
                      for e in eps for a in e["anchors"]))
        else:
            check("JSON ok=True", False, "meta 非 dict")
        check("产物目录 <out_dir>/episodes/ 存在",
              os.path.isdir(os.path.join(out_dir, "episodes")))
        proj_files = []
        proj_root = os.path.join(out_dir, "episodes")
        for d in os.listdir(proj_root):
            proj_files = os.listdir(os.path.join(proj_root, d))
        check("产物含 manifest.json + 集产物",
              "manifest.json" in proj_files
              and any(f.endswith(".json") and f != "manifest.json"
                      for f in proj_files),
              f"files={proj_files}")
    except Exception as e:
        check("运行时不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T4 诚实失败 (空小说原文 → ok=False + errors 非空, 不崩)")
if cls is None:
    check("T4 依赖 T1 (cls 在册)", False)
else:
    node2 = cls()
    out_dir2 = temp_dir()
    try:
        res2 = getattr(node2, cls.FUNCTION)(
            小说原文="", 项目名="空输入测试", 每集目标字数=400, 输出目录=out_dir2)
        check("空输入不抛异常 (返回二元组)",
              isinstance(res2, tuple) and len(res2) == 2)
        rep2, js2 = str(res2[0]), res2[1]
        check("报告含诚实上报标记", "诚实上报" in rep2 and "不伪造" in rep2)
        try:
            meta2 = json.loads(js2)
        except Exception:
            meta2 = None
        check("JSON 可解析", isinstance(meta2, dict))
        check("JSON ok=False", isinstance(meta2, dict) and meta2.get("ok") is False)
        check("JSON errors 非空",
              isinstance(meta2, dict) and bool(meta2.get("errors")))
        check("JSON engine_error 存在",
              isinstance(meta2, dict) and bool(meta2.get("engine_error")))
        check("JSON episodes 为空 (未伪造分集)",
              isinstance(meta2, dict) and meta2.get("episodes") == [])
    except Exception as e:
        check("空输入节点不崩", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T5 输出目录兜底 (输出目录留空 → 临时目录 DirectorMasterIntake)")
if cls is None:
    check("T5 依赖 T1 (cls 在册)", False)
else:
    fallback = os.path.join(tempfile.gettempdir(), "DirectorMasterIntake")
    try:
        resolved = cls._resolve_out_dir("")
        check("留空兜底 → 系统临时目录 DirectorMasterIntake",
              resolved == fallback, f"got={resolved!r}")
        check("显式目录优先", cls._resolve_out_dir(" D:/tmp_x ") == "D:/tmp_x")
        node3 = cls()
        res3 = getattr(node3, cls.FUNCTION)(
            小说原文=make_novel(1), 项目名="兜底测试", 每集目标字数=400,
            输出目录="")
        rep3 = str(res3[0])
        check("兜底路径可运行且报告含兜底目录", "DirectorMasterIntake" in rep3)
        check("兜底产物目录已落盘", os.path.isdir(
            os.path.join(fallback, "episodes")))
    except Exception as e:
        check("兜底路径不崩", False, "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 清理兜底目录 (tempfile 纪律)
    try:
        shutil.rmtree(fallback, ignore_errors=True)
    except Exception:
        pass
    check("模块顶层未导入 folder_paths (惰性纪律)",
          "folder_paths" not in sys.modules)

# ----------------------------------------------------------------
print()
print(f"=== test_episode_node: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
