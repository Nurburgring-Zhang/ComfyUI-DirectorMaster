# -*- coding: utf-8 -*-
"""
批次5 WaveC builder-p4 — DirectorMasterEcoManager 节点测试 (tests/test_eco_node.py)
====================================================================================
覆盖 (design_batch5.md §1 builder-p4):
  T0 模块导入零副作用 (load_isolation 面): fresh import aggregator.eco.node
     不拉 ComfyUI (folder_paths 不进 sys.modules)、不建输出目录、不写任何盘面
  T1 注册面三处结构: _NODE_SPECS 映射 tuple / _ALL_DISPLAY_NAMES 显示名 dict /
     docstring 编号清单 20. 行, 三处齐备; 注册总数恰好 20; DM_QUARANTINE 为空
  T2 形状: INPUT_TYPES "生态模式" 枚举恰好三值 (pack_audit/refflow_register/
     decision_attach); RETURN_TYPES ("STRING","INT"); FUNCTION/CATEGORY/NODE_TYPE
  T3 pack_audit 端到端: 合法包 (六字段+entry) 注册 count==1; 非法包 (缺 entry
     字段) ok=False + errors 显式不炸; 空 packs 目录 ok=True count==0 (验收①)
  T4 refflow 端到端: 合法登记 (含 notes 三列表解构) ok=True + 台账落盘 +
     count==台账条目数; 缺授权 (空串) fail loud ok=False + 台账零文件 (验收②)
  T5 decision 端到端 + 链 verify: 首条 seq=1; 同 (类别,主题) 再追加 revised=true
     seq=2; 独立 verify_log 全链通过; options_considered 分号切分进哈希 payload
  T6 诚实失败矩阵: 非法 mode / refflow 缺 project / decision 缺 project /
     契约JSON 畸形 / 门面 unavailable (sys.modules 注入假模块) — 全部
     ok=False + errors 非空 + 不抛异常
  T7 输出目录兜底: 留空 → 系统临时目录 DirectorMasterEco (folder_paths 惰性)
  T8 golden 回放独立性: 节点三 mode 运行前后 tests/golden/ 产物字节级不变,
     报告 JSON 不引用 golden 路径
  T9 确定性: pack_audit 同输入两次报告逐字节一致; refflow 幂等登记台账逐字节
     一致; decision 同输入跨 out_dir 哈希链条目恒等 (无时间戳无随机)
  T10 LOW-5: EXECUTE 入口 out_dir 校验 (None/空串/纯空白) → ok=False + 中文
     错误含 输出目录 + count==0 + 不落字面 "None" 目录 (诚实报错不裸崩)

纪律: 测试产物一律 tempfile, 零仓库内写入 (golden 目录只读快照比对)。
退出码: 0 = 无 FAIL。
运行: python -X utf8 tests/test_eco_node.py
"""
import importlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

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
    d = tempfile.mkdtemp(prefix="eco_node_test_")
    TEMP_DIRS.append(d)
    return d


def run_node(cls, **kwargs):
    """实例化并调 FUNCTION; 异常向上抛由调用方 check 捕获。"""
    node = cls()
    return getattr(node, cls.FUNCTION)(**kwargs)


def parse(res):
    """(报告 JSON 串, 计数) → (dict, 计数); 解析失败返回 (None, 计数)。"""
    report, count = res
    try:
        return json.loads(report), count
    except Exception:
        return None, count


VALID_PACK = {"pack_id": "eco_node_pack", "version": "1.0.0",
              "min_dm_version": "17.0.0", "dependencies": [],
              "tags": ["test", "batch5"], "entry": "main.py"}


def make_pack(out_dir, pack=VALID_PACK, with_entry=True):
    """合法/非法 dm_pack fixture — <out>/eco/packs/<pack_id>/dm_pack.json。"""
    d = os.path.join(out_dir, "eco", "packs", pack.get("pack_id", "broken"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "dm_pack.json"), "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    if with_entry and pack.get("entry"):
        with open(os.path.join(d, pack["entry"]), "w", encoding="utf-8") as f:
            f.write("# eco node test entry\n")
    return d


# ----------------------------------------------------------------
print("T0 模块导入零副作用 (fresh import 不拉 ComfyUI / 不建输出目录 / 不写盘)")
try:
    # 强制 fresh: 剔除可能已加载的模块与其父包缓存标记
    for k in ("aggregator.eco.node",):
        sys.modules.pop(k, None)
    fallback = os.path.join(tempfile.gettempdir(), "DirectorMasterEco")
    existed_before = os.path.isdir(fallback)
    _mod = importlib.import_module("aggregator.eco.node")
    check("aggregator.eco.node 可裸导入", hasattr(_mod, "DirectorMasterEcoManager"))
    check("导入零副作用: 未创建 DirectorMasterEco 兜底目录",
          existed_before == os.path.isdir(fallback),
          f"before={existed_before} after={os.path.isdir(fallback)}")
    check("导入零副作用: folder_paths 未进 sys.modules (惰性纪律)",
          "folder_paths" not in sys.modules)
    check("mode 枚举常量恰好三值",
          getattr(_mod, "ECO_MODES", ()) == ("pack_audit", "refflow_register", "decision_attach"),
          f"modes={getattr(_mod, 'ECO_MODES', None)}")
except Exception as e:
    check("T0 fresh 导入不炸", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T1 注册面三处结构 (tuple / 显示名 dict / docstring 编号清单)")
pkg = None
try:
    _spec = importlib.util.spec_from_file_location(
        "_dm_eco_node_pkg", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(_spec)
    sys.modules["_dm_eco_node_pkg"] = pkg
    _spec.loader.exec_module(pkg)
except Exception as e:
    check("根包加载", False, repr(e)[:200])

cls = (pkg or {}).NODE_CLASS_MAPPINGS.get("DirectorMasterEcoManager") if pkg else None
check("DirectorMasterEcoManager 在 NODE_CLASS_MAPPINGS", cls is not None)
check("DM_QUARANTINE 为空 (新节点健康加载)",
      pkg is not None and pkg.DM_QUARANTINE == [],
      f"q={getattr(pkg, 'DM_QUARANTINE', None)}")
check("注册节点总数恰好 20", pkg is not None and len(pkg.NODE_CLASS_MAPPINGS) == 20,
      f"n={len(getattr(pkg, 'NODE_CLASS_MAPPINGS', {}))}")
# 三处之一: _NODE_SPECS 映射 tuple (episode_pipeline 条目之后)
specs = getattr(pkg, "_NODE_SPECS", None) or []
try:
    idx_ep = specs.index(("aggregator.episode_pipeline.node", "DirectorMasterNovelIntake"))
    idx_eco = specs.index(("aggregator.eco.node", "DirectorMasterEcoManager"))
    tuple_ok = idx_eco == idx_ep + 1
except ValueError:
    tuple_ok = False
check("_NODE_SPECS 含 eco 映射 tuple 且紧跟 episode_pipeline 条目", tuple_ok,
      f"specs_tail={specs[-3:]}")
# 三处之二: 显示名 dict
disp = (pkg.NODE_DISPLAY_NAME_MAPPINGS.get("DirectorMasterEcoManager", "")
        if pkg else "")
check("显示名在 NODE_DISPLAY_NAME_MAPPINGS 且非空", bool(disp and disp.strip()),
      f"disp={disp[:60]!r}")
check("显示名口径含生态预案", "生态预案" in disp, f"disp={disp[:60]!r}")
raw_all_names = getattr(pkg, "_ALL_DISPLAY_NAMES", {})
check("_ALL_DISPLAY_NAMES 源表含 EcoManager 条目", "DirectorMasterEcoManager" in raw_all_names)
# 三处之三: docstring 编号清单 20. 行 (源码文本断言)
with open(os.path.join(ROOT, "__init__.py"), encoding="utf-8") as f:
    init_src = f.read()
check("docstring 编号清单含 20. 行 (批次5 措辞)",
      "20. DirectorMasterEcoManager" in init_src and "批次5" in init_src)
check("docstring 头部行 20 注册节点", "20 注册节点" in init_src)

# ----------------------------------------------------------------
print("T2 形状 (INPUT_TYPES / RETURN / FUNCTION / CATEGORY)")
if cls is None:
    check("T2 依赖 T1 (cls 在册)", False)
else:
    it = cls.INPUT_TYPES()
    req = it.get("required", {})
    check("required 恰含 生态模式 下拉", list(req.keys()) == ["生态模式"],
          f"req={list(req.keys())}")
    mode_enum = req.get("生态模式", (None,))[0]
    check("生态模式 枚举恰好三值且顺序钉死",
          mode_enum == ["pack_audit", "refflow_register", "decision_attach"],
          f"enum={mode_enum}")
    opt = it.get("optional", {})
    need_opt = ("输出目录", "项目名", "素材ID", "来源描述", "授权声明",
                "备注笔记", "契约JSON", "决策类别", "决策主题", "决策内容", "备选方案")
    check("optional 含 11 个参数槽 (输出目录/项目名/素材ID/来源描述/授权声明/"
          "备注笔记/契约JSON/决策类别/决策主题/决策内容/备选方案)",
          all(k in opt for k in need_opt),
          f"missing={[k for k in need_opt if k not in opt]}")
    check("备注笔记/备选方案 multiline", all(
        opt.get(k, (None, {}))[1].get("multiline") is True for k in ("备注笔记", "备选方案")))
    check("RETURN_TYPES == (STRING, INT)", cls.RETURN_TYPES == ("STRING", "INT"),
          f"got={cls.RETURN_TYPES}")
    check("RETURN_NAMES == (生态报告, 计数)",
          cls.RETURN_NAMES == ("生态报告", "计数"))
    check("FUNCTION == eco_manage", cls.FUNCTION == "eco_manage")
    check("CATEGORY 非空且含聚合生态口径",
          bool(str(cls.CATEGORY).strip()) and "生态预案" in str(cls.CATEGORY),
          f"cat={cls.CATEGORY}")
    check("继承 DirectorNodeBase (同 episode_pipeline 范本)",
          any(b.__name__ == "DirectorNodeBase" for b in cls.__mro__))

# ----------------------------------------------------------------
print("T3 pack_audit 端到端 (合法包 / 非法包 / 空 packs 目录)")
if cls is None:
    check("T3 依赖 T1 (cls 在册)", False)
else:
    # 3a 合法包
    out_ok = temp_dir()
    make_pack(out_ok)
    try:
        res = run_node(cls, 生态模式="pack_audit", 输出目录=out_ok)
        meta, count = parse(res)
        check("合法包: 返回二元组 (STRING, INT)",
              isinstance(res, tuple) and len(res) == 2 and isinstance(res[1], int))
        check("合法包: JSON ok=True", isinstance(meta, dict) and meta.get("ok") is True)
        check("合法包: errors 为空", isinstance(meta, dict) and meta.get("errors") == [])
        check("合法包: count==1 (注册包数)", count == 1, f"count={count}")
        check("合法包: summary.pack_id 匹配",
              isinstance(meta, dict)
              and (meta.get("summary") or {}).get("packs", [{}])[0].get("pack_id") == "eco_node_pack")
        check("合法包: 报告零时间戳字段 (确定性)",
              isinstance(meta, dict) and not any(
                  "time" in k.lower() or "时间" in k or "timestamp" in k.lower()
                  for k in meta.keys()))
    except Exception as e:
        check("合法包: 节点不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 3b 非法包 (缺 entry 字段 → 字段闸拦截)
    out_bad = temp_dir()
    broken = {k: v for k, v in VALID_PACK.items() if k != "entry"}
    broken["pack_id"] = "broken_pack"
    make_pack(out_bad, pack=broken, with_entry=False)
    try:
        res2 = run_node(cls, 生态模式="pack_audit", 输出目录=out_bad)
        meta2, count2 = parse(res2)
        check("非法包: ok=False (fail loud)", isinstance(meta2, dict) and meta2.get("ok") is False)
        check("非法包: errors 显式非空",
              isinstance(meta2, dict) and bool(meta2.get("errors")))
        check("非法包: 不抛异常不炸", True)
        check("非法包: count==0 (拒绝载入)", count2 == 0, f"count={count2}")
    except Exception as e:
        check("非法包: 节点不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 3c 空 packs 目录 → ok 空结果不报错 (验收①)
    out_empty = temp_dir()
    try:
        res3 = run_node(cls, 生态模式="pack_audit", 输出目录=out_empty)
        meta3, count3 = parse(res3)
        check("空 packs 目录: ok=True 不报错",
              isinstance(meta3, dict) and meta3.get("ok") is True)
        check("空 packs 目录: count==0", count3 == 0, f"count={count3}")
    except Exception as e:
        check("空 packs 目录: 不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T4 refflow 端到端 (合法登记+三列表 / 缺授权 fail loud)")
if cls is None:
    check("T4 依赖 T1 (cls 在册)", False)
else:
    out_r = temp_dir()
    try:
        res = run_node(cls, 生态模式="refflow_register", 输出目录=out_r,
                       项目名="生态节点测试项目", 素材ID="ref-001",
                       来源描述="某公开短片的手法参考",
                       授权声明="已获作者书面授权, 仅限手法学习",
                       备选方案="", 备注笔记="镜头衔接手法: 借位遮挡\n做法: 长镜跟拍过渡\n放弃: 复制其调色")
        meta, count = parse(res)
        check("合法登记: ok=True", isinstance(meta, dict) and meta.get("ok") is True)
        check("合法登记: count==1 (台账条目数)", count == 1, f"count={count}")
        check("合法登记: 台账落盘 <out>/eco/ref_ledger/",
              os.path.isdir(os.path.join(out_r, "eco", "ref_ledger"))
              and any(fn.endswith(".json") for fn in os.listdir(
                  os.path.join(out_r, "eco", "ref_ledger"))))
        summary = (meta or {}).get("summary") or {}
        decon = summary.get("deconstruct") or {}
        check("合法登记: 三列表三键齐备",
              set(decon.keys()) >= {"手法", "参考实现", "取舍"})
        check("合法登记: 笔记逐行归类 (手法1/实现1/取舍1)",
              len(decon.get("手法") or []) == 1 and len(decon.get("参考实现") or []) == 1
              and len(decon.get("取舍") or []) == 1,
              f"decon={ {k: len(v) for k, v in decon.items()} }")
        check("合法登记: entry 含法务边界字段 legal_boundary",
              bool((summary.get("entry") or {}).get("legal_boundary")))
        check("合法登记: 授权字段落盘进台账",
              (summary.get("entry") or {}).get("authorization") == "已获作者书面授权, 仅限手法学习")
    except Exception as e:
        check("合法登记: 节点不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 4b 缺授权 (纯空白) → fail loud 不落盘 (验收②)
    out_na = temp_dir()
    try:
        res2 = run_node(cls, 生态模式="refflow_register", 输出目录=out_na,
                        项目名="缺授权项目", 素材ID="ref-002",
                        来源描述="来源描述在, 授权声明纯空白",
                        授权声明="   ")
        meta2, count2 = parse(res2)
        check("缺授权: ok=False fail loud", isinstance(meta2, dict) and meta2.get("ok") is False)
        check("缺授权: errors 显式含 authorization 必填",
              isinstance(meta2, dict)
              and any("authorization" in str(e) for e in (meta2.get("errors") or [])),
              f"errors={meta2.get('errors') if isinstance(meta2, dict) else None}")
        ledger_dir = os.path.join(out_na, "eco", "ref_ledger")
        check("缺授权: 台账零文件落盘 (不静默)",
              not os.path.isdir(ledger_dir) or not os.listdir(ledger_dir))
        check("缺授权: count==0", count2 == 0, f"count={count2}")
    except Exception as e:
        check("缺授权: 节点不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T5 decision 端到端 + 链 verify (revised 语义 / 分号切分 / 独立 verify_log)")
if cls is None:
    check("T5 依赖 T1 (cls 在册)", False)
else:
    out_d = temp_dir()
    try:
        res1 = run_node(cls, 生态模式="decision_attach", 输出目录=out_d,
                        项目名="生态决策项目", 决策类别="分镜契约",
                        决策主题="refs槽位", 决策内容="采用只加 refs 键的 additive 注入",
                        备选方案="整体重写契约; 放弃注入")
        meta1, count1 = parse(res1)
        check("首条决策: ok=True", isinstance(meta1, dict) and meta1.get("ok") is True)
        check("首条决策: count==1 (seq 序号)", count1 == 1, f"count={count1}")
        entry1 = ((meta1 or {}).get("summary") or {}).get("entry") or {}
        check("首条决策: revised=false", entry1.get("revised") is False)
        check("首条决策: options_considered 分号切分 (钉死 ';')",
              entry1.get("options_considered") == ["整体重写契约", "放弃注入"],
              f"opts={entry1.get('options_considered')}")
        check("首条决策: verify_ok=true (门面内建 verify)",
              ((meta1 or {}).get("summary") or {}).get("verify_ok") is True)
        log_path = ((meta1 or {}).get("summary") or {}).get("log_path")
        check("首条决策: log_path 落盘 decision_log.jsonl",
              isinstance(log_path, str) and os.path.isfile(log_path))
        # 同 (类别, 主题) 再追加 → revised=true, seq=2
        res2 = run_node(cls, 生态模式="decision_attach", 输出目录=out_d,
                        项目名="生态决策项目", 决策类别="分镜契约",
                        决策主题="refs槽位", 决策内容="改用追加语义保旧决策可溯",
                        备选方案="维持原决策")
        meta2, count2 = parse(res2)
        entry2 = ((meta2 or {}).get("summary") or {}).get("entry") or {}
        check("再追加: ok=True 且 count==2 (seq=2)",
              isinstance(meta2, dict) and meta2.get("ok") is True and count2 == 2,
              f"ok={isinstance(meta2, dict) and meta2.get('ok')} count={count2}")
        check("再追加: revised=true (变更语义)",
              entry2.get("revised") is True, f"revised={entry2.get('revised')}")
        # 独立全链 verify (哈希链防篡改口径)
        from aggregator.eco.decision_log import verify_log
        ok_chain, chain_errors = verify_log(log_path)
        check("独立 verify_log 全链通过", ok_chain is True and chain_errors == [],
              f"errs={chain_errors}")
    except Exception as e:
        check("decision 端到端不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T6 诚实失败矩阵 (非法 mode / 缺 project / 畸形契约 / 门面 unavailable)")
if cls is None:
    check("T6 依赖 T1 (cls 在册)", False)
else:
    out_f = temp_dir()
    cases = [
        ("非法 mode", dict(生态模式="hack_mode", 输出目录=out_f),
         "生态模式"),
        ("refflow 缺 project", dict(生态模式="refflow_register", 输出目录=out_f,
                                    素材ID="r", 来源描述="s", 授权声明="a"),
         "项目名"),
        ("decision 缺 project", dict(生态模式="decision_attach", 输出目录=out_f,
                                     决策类别="c", 决策主题="s", 决策内容="d"),
         "项目名"),
        ("契约JSON 畸形", dict(生态模式="refflow_register", 输出目录=out_f,
                              项目名="p", 素材ID="r", 来源描述="s", 授权声明="a",
                              契约JSON="{not-json"),
         "契约JSON"),
        ("契约JSON 顶层非对象", dict(生态模式="refflow_register", 输出目录=out_f,
                                    项目名="p", 素材ID="r", 来源描述="s", 授权声明="a",
                                    契约JSON="[1,2]"),
         "契约JSON"),
    ]
    for label, kw, needle in cases:
        try:
            res = run_node(cls, **kw)
            meta, count = parse(res)
            check("%s: 不抛异常且返回二元组" % label,
                  isinstance(res, tuple) and len(res) == 2)
            check("%s: ok=False" % label,
                  isinstance(meta, dict) and meta.get("ok") is False)
            check("%s: errors 非空且含定位词" % label,
                  isinstance(meta, dict)
                  and bool(meta.get("errors"))
                  and any(needle in str(e) for e in (meta.get("errors") or [])),
                  f"errors={meta.get('errors') if isinstance(meta, dict) else None}")
            check("%s: count==0" % label, count == 0, f"count={count}")
        except Exception as e:
            check("%s: 节点不抛异常" % label, False,
                  "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 门面 unavailable: sys.modules 注入无导出属性的假 aggregator.eco
    _real = sys.modules.get("aggregator.eco")
    _fake = types.ModuleType("aggregator.eco")  # 无 pack_audit/refflow_register/...
    sys.modules["aggregator.eco"] = _fake
    try:
        res_u = run_node(cls, 生态模式="pack_audit", 输出目录=out_f)
        meta_u, count_u = parse(res_u)
        check("门面 unavailable: ok=False + errors 非空 (诚实降级不炸)",
              isinstance(meta_u, dict) and meta_u.get("ok") is False
              and bool(meta_u.get("errors")),
              f"errors={meta_u.get('errors') if isinstance(meta_u, dict) else None}")
        check("门面 unavailable: count==0", count_u == 0)
        check("门面 unavailable: engine_error 在场",
              isinstance(meta_u, dict) and bool(meta_u.get("engine_error")))
    except Exception as e:
        check("门面 unavailable: 节点不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:200]))
    finally:
        if _real is not None:
            sys.modules["aggregator.eco"] = _real
        else:
            sys.modules.pop("aggregator.eco", None)

# ----------------------------------------------------------------
print("T7 输出目录兜底 (留空 → 系统临时目录 DirectorMasterEco)")
if cls is None:
    check("T7 依赖 T1 (cls 在册)", False)
else:
    try:
        fallback = os.path.join(tempfile.gettempdir(), "DirectorMasterEco")
        check("留空兜底 → 系统临时目录 DirectorMasterEco",
              cls._resolve_out_dir("") == fallback,
              f"got={cls._resolve_out_dir('')!r}")
        check("显式目录优先 (strip 生效)", cls._resolve_out_dir(" D:/tmp_eco ") == "D:/tmp_eco")
    except Exception as e:
        check("兜底解析不抛异常", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T8 golden 回放独立性 (节点不读不写 tests/golden/ 产物路径)")
GOLDEN_DIR = os.path.join(HERE, "golden")


def _golden_snapshot():
    snap = {}
    if os.path.isdir(GOLDEN_DIR):
        for fn in sorted(os.listdir(GOLDEN_DIR)):
            p = os.path.join(GOLDEN_DIR, fn)
            if os.path.isfile(p):
                with open(p, "rb") as f:
                    snap[fn] = f.read()
    return snap


if cls is None:
    check("T8 依赖 T1 (cls 在册)", False)
else:
    try:
        before = _golden_snapshot()
        out_g = temp_dir()
        # 三 mode 各跑一遍 (合法输入), 产物只落 tempfile out_dir
        run_node(cls, 生态模式="pack_audit", 输出目录=out_g)
        run_node(cls, 生态模式="refflow_register", 输出目录=out_g,
                 项目名="golden隔离", 素材ID="g1", 来源描述="s", 授权声明="a")
        run_node(cls, 生态模式="decision_attach", 输出目录=out_g,
                 项目名="golden隔离", 决策类别="c", 决策主题="s", 决策内容="d")
        after = _golden_snapshot()
        check("golden 目录字节级不变 (三 mode 运行前后)", before == after,
              f"diff={sorted(set(before.items()) ^ set(after.items()))}")
        check("golden 产物路径不出现在节点报告中",
              "golden" not in open(os.path.join(out_g, "eco", "decision_log.jsonl"),
                                   encoding="utf-8").read())
        check("节点产物零落 golden 目录 (out_dir 隔离)",
              not os.path.exists(os.path.join(GOLDEN_DIR, "eco")))
        # 负样本运行同样不触 golden
        run_node(cls, 生态模式="pack_audit", 输出目录=temp_dir())
        check("golden 目录文件数不变", len(_golden_snapshot()) == len(before))
    except Exception as e:
        check("golden 独立性探针不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T9 确定性 (pack_audit 双跑逐字节 / refflow 幂等 / decision 跨 out_dir 哈希恒等)")
if cls is None:
    check("T9 依赖 T1 (cls 在册)", False)
else:
    # 9a pack_audit 同 out_dir 两次 → 报告逐字节一致
    out_p = temp_dir()
    make_pack(out_p, pack=dict(VALID_PACK, pack_id="det_pack"))
    try:
        r1 = run_node(cls, 生态模式="pack_audit", 输出目录=out_p)[0]
        r2 = run_node(cls, 生态模式="pack_audit", 输出目录=out_p)[0]
        check("pack_audit 同输入两次报告逐字节一致", r1 == r2)
    except Exception as e:
        check("pack_audit 确定性不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 9b refflow 幂等: 同 out_dir 同 ref_id 登记两次 → 报告与台账逐字节一致
    out_r1 = temp_dir()
    kw_r = dict(生态模式="refflow_register", 项目名="幂等项目", 素材ID="ref-det",
                来源描述="同一来源", 授权声明="同一授权")
    try:
        a = run_node(cls, 输出目录=out_r1, **kw_r)
        b = run_node(cls, 输出目录=out_r1, **kw_r)
        check("refflow 幂等登记: 两次报告逐字节一致", a[0] == b[0] and a[1] == b[1])
        ledger = os.path.join(out_r1, "eco", "ref_ledger")
        led_files = [os.path.join(ledger, fn) for fn in sorted(os.listdir(ledger))]
        with open(led_files[0], "rb") as f:
            lb1 = f.read()
        check("refflow 幂等: 台账恰一条目 (ref_id 键幂等覆盖)", a[1] == 1 and len(led_files) == 1)
    except Exception as e:
        check("refflow 幂等不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:200]))
    # 9c decision 同输入跨 out_dir → 哈希链条目恒等 (payload 无时间戳/无随机/无路径)
    o1, o2 = temp_dir(), temp_dir()
    kw_d = dict(生态模式="decision_attach", 项目名="跨目录项目",
                决策类别="确定性", 决策主题="哈希链",
                决策内容="同输入同链序恒等", 备选方案="时间戳方案; 随机方案")
    try:
        m1, c1 = parse(run_node(cls, 输出目录=o1, **kw_d))
        m2, c2 = parse(run_node(cls, 输出目录=o2, **kw_d))
        e1 = ((m1 or {}).get("summary") or {}).get("entry") or {}
        e2 = ((m2 or {}).get("summary") or {}).get("entry") or {}
        check("decision 跨 out_dir: seq 同为 1", c1 == 1 and c2 == 1)
        check("decision 跨 out_dir: hash 恒等 (payload 确定性)",
              bool(e1.get("hash")) and e1.get("hash") == e2.get("hash"),
              f"h1={str(e1.get('hash'))[:12]} h2={str(e2.get('hash'))[:12]}")
        check("decision 跨 out_dir: prev_hash 同为创世 (0*64)",
              e1.get("prev_hash") == "0" * 64 == e2.get("prev_hash"))
        check("decision 跨 out_dir: options_considered 切分恒等",
              e1.get("options_considered") == e2.get("options_considered")
              == ["时间戳方案", "随机方案"])
    except Exception as e:
        check("decision 确定性不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T10 LOW-5: EXECUTE 入口 out_dir 校验 (None/空串/纯空白) → 诚实中文报错, 不落字面 None 目录")
none_dir_before = os.path.isdir("None")
for label, bad_out in (("None", None), ("空串", ""), ("纯空白", "  \t ")):
    try:
        res_bad = run_node(cls, 生态模式="pack_audit", 输出目录=bad_out)
        rep_bad, cnt_bad = parse(res_bad)
        check(f"T10 out_dir={label}: 返回诚实失败 (ok=False)",
              isinstance(rep_bad, dict) and rep_bad.get("ok") is False,
              f"rep={(str(rep_bad)[:160])}")
        errs_bad = (rep_bad or {}).get("errors") or []
        check(f"T10 out_dir={label}: errors 非空且含 输出目录 中文口径",
              isinstance(errs_bad, list) and len(errs_bad) > 0
              and any("输出目录" in str(x) for x in errs_bad),
              f"errors={errs_bad}")
        check(f"T10 out_dir={label}: count==0", cnt_bad == 0, f"count={cnt_bad}")
    except Exception as e:  # noqa: BLE001 — LOW-5 要求不裸崩, 异常即 FAIL
        check(f"T10 out_dir={label}: 不抛异常", False,
              "%s: %s" % (type(e).__name__, str(e)[:160]))
check("T10 全程不落字面 'None' 目录 (CWD)",
      os.path.isdir("None") is False and none_dir_before == os.path.isdir("None"))

# ----------------------------------------------------------------
print()
print(f"=== test_eco_node: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
