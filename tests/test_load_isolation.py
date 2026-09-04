# -*- coding: utf-8 -*-
"""
加载崩溃隔离真实机制测试 (T12, 批次1 起始) + 版本口径一致性 (动态三处校验, 随包版本自适应)
====================================================================
验证 __init__.py 的 load_node_classes 隔离加载机制是真实机制而非装饰:
  1. 真实注册表: 20 节点全部加载, DM_QUARANTINE 为空, 显示名全覆盖, Final 别名同源
  2. 故障注入: 坏模块 (phase=import) / 坏类名 (phase=getattr) 被隔离且不拖垮好节点
  3. 隔离条目结构完整 (target/error/phase)
  4. 版本口径: __version__ / pyproject.toml / README 三处动态一致 (升版只改三处源, 不改本测试)

__init__.py 通过 importlib spec 以独立模块名加载 (与 doctor 第 8 类诊断同法),
避免与 ComfyUI 运行时的包导入路径冲突。

证据存档: tests/load_isolation_results.json (随包发布)。
退出码: 0 = 全部通过, 1 = 有失败。
"""
import importlib.util
import json
import os
import sys
import time as _time

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

PASS, FAIL = 0, 0
RESULTS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        RESULTS.append({"label": label, "ok": True, "detail": str(detail)[:300]})
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        RESULTS.append({"label": label, "ok": False, "detail": str(detail)[:300]})
        print(f"  [FAIL] {label} {detail}")


EXPECTED_SUPER = [
    "DirectorMasterCore", "DirectorMasterScript", "DirectorMasterVibe",
    "DirectorMasterArt", "DirectorMasterSound", "DirectorMasterCinematic",
    "DirectorMasterAsset", "DirectorMasterSummary", "DirectorMasterRouter",
    "DirectorMasterCharacters", "DirectorMasterVideoRouter", "DirectorMasterArchive",
    "DirectorMasterCoCreator", "DirectorMasterSoul", "DirectorMasterIntuition",
    "DirectorMasterFusion", "DirectorMasterReview",
]

# legacy 兼容层由环境变量控制, 测试必须在默认 (不加载 legacy) 口径下进行
_LEGACY_ENV = os.environ.pop("DIRECTORMASTER_LEGACY_NODES", None)

try:
    spec = importlib.util.spec_from_file_location("_dm_pkg_under_test", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["_dm_pkg_under_test"] = pkg
    spec.loader.exec_module(pkg)

    # ---------------- 1. 真实注册表 ----------------
    print("1. 真实注册表 (默认口径)")
    mappings = pkg.NODE_CLASS_MAPPINGS
    check("注册节点恰好 20 个 (17 超级 + Final 别名 + 长篇接入 + 生态预案)", len(mappings) == 20, f"n={len(mappings)}")
    missing = [n for n in EXPECTED_SUPER if n not in mappings]
    check("17 个超级节点全部在册", not missing, f"missing={missing}")
    check("Final 别名在册", "DirectorMasterFinal" in mappings)
    check("隔离清单为空 (全部健康加载)", pkg.DM_QUARANTINE == [], f"q={pkg.DM_QUARANTINE}")
    check("Final 别名与 Summary 同源 (同一个类对象)",
          mappings.get("DirectorMasterFinal") is mappings.get("DirectorMasterSummary"))
    no_display = [k for k in mappings
                  if not (pkg.NODE_DISPLAY_NAME_MAPPINGS.get(k) or "").strip()]
    check("每个注册节点都有非空显示名", not no_display, f"missing={no_display}")
    check("__all__ 暴露隔离清单与加载函数",
          all(x in pkg.__all__ for x in ("NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS",
                                         "DM_QUARANTINE", "load_node_classes")))
    check("每个节点类具备 ComfyUI 必需属性",
          all(hasattr(c, "INPUT_TYPES") and hasattr(c, "RETURN_TYPES") and callable(getattr(c, "INPUT_TYPES", None))
              for c in mappings.values()))

    # ---------------- 2. 故障注入: 真实隔离机制 ----------------
    print("2. 故障注入 (坏模块/坏类名/好坏混排)")
    q1 = []
    r1 = pkg.load_node_classes(specs=[("aggregator.__definitely_not_exist__", "NoSuchNode")], quarantine=q1)
    check("坏模块: 返回空注册", r1 == {})
    check("坏模块: 入隔离且 phase=import",
          len(q1) == 1 and q1[0]["phase"] == "import" and "NoSuchNode" in q1[0]["target"],
          f"q={q1}")

    q2 = []
    r2 = pkg.load_node_classes(specs=[("aggregator.router", "DefinitelyMissingClass")], quarantine=q2)
    check("坏类名: 模块可导入但类缺失入隔离 phase=getattr",
          r2 == {} and len(q2) == 1 and q2[0]["phase"] == "getattr", f"q={q2}")

    q3 = []
    r3 = pkg.load_node_classes(specs=[
        ("aggregator.__definitely_not_exist__", "BadOne"),
        ("aggregator.router", "BadTwo"),
        ("aggregator.router", "DirectorMasterRouter"),
        ("aggregator.v15_nodes", ("DirectorMasterCoCreator", "DirectorMasterSoul")),
    ], quarantine=q3)
    check("好坏混排: 好节点不受坏邻居拖垮",
          set(r3) == {"DirectorMasterRouter", "DirectorMasterCoCreator", "DirectorMasterSoul"},
          f"loaded={sorted(r3)}")
    check("好坏混排: 两个坏目标分别以 import/getattr 入隔离",
          len(q3) == 2 and {e["phase"] for e in q3} == {"import", "getattr"}, f"q={q3}")
    check("隔离条目结构完整 (target/error/phase 三键)",
          all(set(e) == {"target", "error", "phase"} for e in q1 + q2 + q3))

    # 隔离机制不得污染真实注册表
    check("故障注入后真实注册表仍为 20 节点", len(pkg.NODE_CLASS_MAPPINGS) == 20)

    # ---------------- 3. 版本口径一致性 ----------------
    # V16.3: 动态三处一致性校验 (意图不变: __version__/pyproject/README 必须同版),
    #        不再硬编码具体版本号 — 升版本只需改三处源, 不必改测试。
    import re as _re_ver
    _ver = getattr(pkg, "__version__", None)
    print(f"3. 版本口径一致性 (三处 {_ver})")
    check("__version__ 存在且为 x.y.z 形态", isinstance(_ver, str) and _re_ver.fullmatch(r"\d+\.\d+\.\d+", _ver) is not None,
          f"v={_ver!r}")
    with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
        pyproject_text = f.read()
    _m_pyproject = _re_ver.search(r'version\s*=\s*"([^"]+)"', pyproject_text)
    check("pyproject.toml version 与 __version__ 一致", _m_pyproject is not None and _m_pyproject.group(1) == _ver,
          f"pyproject={_m_pyproject.group(1) if _m_pyproject else None} vs __version__={_ver}")
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        readme_text = f.read()
    check(f"README 标注 V{_ver}", f"V{_ver}" in readme_text)
    check(f"README 含 V{_ver} 版本历史小节", f"### V{_ver}" in readme_text)

finally:
    if _LEGACY_ENV is not None:
        os.environ["DIRECTORMASTER_LEGACY_NODES"] = _LEGACY_ENV
    sys.modules.pop("_dm_pkg_under_test", None)

RESULTS_DOC = {
    "suite": "test_load_isolation",
    "version": _ver,
    "timestamp": _time.strftime("%Y-%m-%d %H:%M:%S"),
    "pass": PASS,
    "fail": FAIL,
    "results": RESULTS,
}
OUT_JSON = os.path.join(HERE, "load_isolation_results.json")
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(RESULTS_DOC, f, ensure_ascii=False, indent=2)

print(f"\n加载隔离机制测试结果: {PASS} PASS / {FAIL} FAIL (证据: {OUT_JSON})")
sys.exit(1 if FAIL else 0)
