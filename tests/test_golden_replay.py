# -*- coding: utf-8 -*-
"""
批次3 D3 — golden 回放测试 (tests/test_golden_replay.py)
==========================================================
两组 fixtures (tests/golden/):
  golden_storyboard.json — 固定种子 42 + 固定输入 → 真实 Cinematic 产物结构快照
                           (链: DirectorMasterCore → DirectorMasterScript → DirectorMasterCinematic,
                            核心数据包 _随机种子=42 全链种子)
  golden_aigc.json       — 同链 DirectorMasterSummary 交付包 AIGC 提示词结构快照
                           (AIGC分镜提示词 / AIGC生产设置 / 叙事编排)

比对口径 (设计 §3):
  结构逐字段 (递归 walk: 键集合/列表长度/标量精确) + 关键文本锚 (前 64 字符) +
  镜数/总时长精确; 文本全文不比 (防无关抖动假红), 结构漂移零容忍。

再生成 (唯一允许重写 fixtures 的方式):
  python tests/test_golden_replay.py --regen     # 先打印与现有 fixture 的 diff 摘要, 再重写

断言 ≥15; 退出码 0 = 全部通过; 常规运行绝不写盘 (fixtures 只读)。
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

GOLDEN_DIR = os.path.join(HERE, "golden")
STORYBOARD_FIXTURE = os.path.join(GOLDEN_DIR, "golden_storyboard.json")
AIGC_FIXTURE = os.path.join(GOLDEN_DIR, "golden_aigc.json")

FIXTURE_VERSION = 1
SEED = 42
ANCHOR_LEN = 64  # 关键文本锚: 前 64 字符

# 固定输入 (全链确定性基线; 核心包 _随机种子=42 驱动下游全部 🎲 派生)
FIXED_INPUTS = {
    "项目名": "金样回放",
    "随机种子": 42,
    "场景描述": "父女在厨房, 雨夜, 1998年哈尔滨, 父亲切菜, 女儿坐桌边, 桌上有凤梨罐头和旧信",
    "导演名": "[电影] 王家卫",
    "叙事编排": "正叙",
    "叙事线型": "单线",
    "目标时长(分钟)": 0.5,
    "画面模式": "电影工作室",
}
CHAIN_NODES = ["DirectorMasterCore", "DirectorMasterScript",
               "DirectorMasterCinematic", "DirectorMasterSummary"]

PASS, FAIL = 0, 0
FAILURES = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        FAILURES.append(f"{label} {detail}")
        print(f"  [FAIL] {label} {detail}")


# =====================================================================
# 真实链构建 (与 tests/test_aigc_random_full.py 同一 load/defaults 调用方式)
# =====================================================================
def load_pkg():
    spec = importlib.util.spec_from_file_location("dm_golden", os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dm_golden"] = mod
    spec.loader.exec_module(mod)
    return mod


def defaults(cls):
    it = cls.INPUT_TYPES()
    kw = {}
    for k, v in it.get("required", {}).items():
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], list):
            kw[k] = v[0][0]
        elif isinstance(v, tuple) and v and v[0] == "STRING":
            kw[k] = (v[1] or {}).get("default", "")
        elif isinstance(v, tuple) and v and v[0] in ("INT", "FLOAT"):
            kw[k] = (v[1] or {}).get("default", 0)
        elif isinstance(v, tuple) and v and v[0] == "BOOLEAN":
            kw[k] = (v[1] or {}).get("default", False)
    return kw


def run_chain(mod):
    """固定输入真实链: Core(种子42) → Script → Cinematic → Summary。
    返回 (cine_main 文本, cine_data dict, summary_data dict)。全程静默重定向。"""
    Core = mod.NODE_CLASS_MAPPINGS["DirectorMasterCore"]
    ck = defaults(Core)
    ck.update({k: v for k, v in FIXED_INPUTS.items() if k not in ("目标时长(分钟)", "画面模式")})
    _, core_pack, _style_anchor = Core().build(**ck)

    S = mod.NODE_CLASS_MAPPINGS["DirectorMasterScript"]
    sk = defaults(S)
    sk.update({"目标时长(分钟)": FIXED_INPUTS["目标时长(分钟)"], "核心数据包": core_pack})
    script = S().build(**sk)[0]

    C = mod.NODE_CLASS_MAPPINGS["DirectorMasterCinematic"]
    ckw = defaults(C)
    ckw.update({"画面模式": FIXED_INPUTS["画面模式"],
                "目标时长(分钟)": FIXED_INPUTS["目标时长(分钟)"],
                "核心数据包": core_pack, "剧本输入": script})
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        cine_main, cine_json = C().build(**ckw)

    Sum = mod.NODE_CLASS_MAPPINGS["DirectorMasterSummary"]
    skw = defaults(Sum)
    skw.update({"项目名": FIXED_INPUTS["项目名"], "核心数据包": core_pack,
                "剧本输出": script, "分镜输出": cine_main})
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        _manual, sum_json, _idx = Sum().build(**skw)

    return cine_main, json.loads(cine_json), json.loads(sum_json)


# =====================================================================
# 比对口径: 结构逐字段 + 文本前 64 字符锚 (全文不比)
# =====================================================================
def prune(obj):
    """长文本 (>64 字符) → 前 64 字符锚 + '…'; 其余原样 (标量/短文本精确)。"""
    if isinstance(obj, dict):
        return dict((k, prune(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return [prune(v) for v in obj]
    if isinstance(obj, str):
        return obj if len(obj) <= ANCHOR_LEN else obj[:ANCHOR_LEN] + "…"
    return obj


def structural_diff(got, want, path="$"):
    """递归结构比对 → diff 列表 (类型/键集合/列表长度/标量与锚精确)。"""
    diffs = []
    if type(got) is not type(want):
        diffs.append("%s: 类型 %s != %s" % (path, type(got).__name__, type(want).__name__))
        return diffs
    if isinstance(want, dict):
        for k in sorted(set(want) | set(got)):
            if k not in want:
                diffs.append("%s.%s: 多出键" % (path, k))
            elif k not in got:
                diffs.append("%s.%s: 缺失键" % (path, k))
            else:
                diffs.extend(structural_diff(got[k], want[k], "%s.%s" % (path, k)))
    elif isinstance(want, list):
        if len(got) != len(want):
            diffs.append("%s: 列表长度 %d != %d" % (path, len(got), len(want)))
        for i in range(min(len(got), len(want))):
            diffs.extend(structural_diff(got[i], want[i], "%s[%d]" % (path, i)))
    else:
        if got != want:
            diffs.append("%s: %r != %r" % (path, str(got)[:80], str(want)[:80]))
    return diffs


def _md5_text(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _md5_file(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _fixture_inputs():
    ins = dict(FIXED_INPUTS)
    ins["剧本输入来源"] = "DirectorMasterScript (核心包 _随机种子=42 种子驱动)"
    return ins


def build_fixtures(mod):
    """跑真实链 → 两组 fixture dict (expect 为 prune 后结构快照)。"""
    cine_main, cine_data, sum_data = run_chain(mod)
    sb = {
        "fixture": "golden_storyboard",
        "fixture_version": FIXTURE_VERSION,
        "regen": "python tests/test_golden_replay.py --regen (显式再生成, 打印 diff 摘要后才重写)",
        "chain": CHAIN_NODES[:3],
        "seed": SEED,
        "generator": "DirectorMasterCinematic.build",
        "inputs": _fixture_inputs(),
        "cine_main_md5": _md5_text(cine_main),
        "expect": prune(cine_data),
    }
    aigc = {
        "fixture": "golden_aigc",
        "fixture_version": FIXTURE_VERSION,
        "regen": "python tests/test_golden_replay.py --regen (显式再生成, 打印 diff 摘要后才重写)",
        "chain": CHAIN_NODES,
        "seed": SEED,
        "generator": "DirectorMasterSummary.build (AIGC分镜提示词/AIGC生产设置/叙事编排)",
        "inputs": _fixture_inputs(),
        "expect": {
            "AIGC分镜提示词": prune(sum_data.get("AIGC分镜提示词", [])),
            "AIGC生产设置": prune(sum_data.get("AIGC生产设置", {})),
            "叙事编排": prune(sum_data.get("叙事编排", {})),
            "item_count": len(sum_data.get("AIGC分镜提示词", [])),
            "shot_count": len(sum_data.get("分镜表", [])),
        },
    }
    return sb, aigc


def write_fixtures(sb, aigc):
    if not os.path.isdir(GOLDEN_DIR):
        os.makedirs(GOLDEN_DIR)
    for path, doc in ((STORYBOARD_FIXTURE, sb), (AIGC_FIXTURE, aigc)):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


# =====================================================================
# --regen: 显式再生成 (先打印 diff 摘要, 才允许重写 fixtures)
# =====================================================================
def regen():
    print("== golden fixtures 再生成 (显式 --regen) ==")
    mod = load_pkg()
    sb, aigc = build_fixtures(mod)
    for path, doc in ((STORYBOARD_FIXTURE, sb), (AIGC_FIXTURE, aigc)):
        name = os.path.basename(path)
        if os.path.exists(path):
            old = _load_json(path)
            diffs = structural_diff(prune(doc["expect"]), old.get("expect"))
            print("-- %s 与现有 fixture diff 摘要: %d 项" % (name, len(diffs)))
            for d in diffs[:10]:
                print("   *", d)
            if len(diffs) > 10:
                print("   ... 其余 %d 项省略" % (len(diffs) - 10))
            if not diffs:
                print("   (与现有 fixture 零结构差异 — 版本/输入口径漂移才需重写)")
        else:
            print("-- %s 不存在, 首次生成" % name)
    write_fixtures(sb, aigc)
    print("已重写: %s / %s" % (os.path.relpath(STORYBOARD_FIXTURE, ROOT),
                              os.path.relpath(AIGC_FIXTURE, ROOT)))
    print("镜数=%s 总时长=%s AIGC条目=%s" % (
        sb["expect"].get("分镜数"), sb["expect"].get("总时长秒"),
        aigc["expect"]["item_count"]))
    sys.exit(0)


# =====================================================================
# 回放套件 (≥15 断言; 常规运行零写盘)
# =====================================================================
def run_suite():
    print("T0 fixtures 存在性与口径")
    check("T0 golden_storyboard.json 存在且可解析, fixture 名与版本正确",
          os.path.exists(STORYBOARD_FIXTURE) is True
          and _load_json(STORYBOARD_FIXTURE).get("fixture") == "golden_storyboard"
          and _load_json(STORYBOARD_FIXTURE).get("fixture_version") == FIXTURE_VERSION,
          "缺失则运行 python tests/test_golden_replay.py --regen")
    check("T0 golden_aigc.json 存在且可解析, fixture 名与版本正确",
          os.path.exists(AIGC_FIXTURE) is True
          and _load_json(AIGC_FIXTURE).get("fixture") == "golden_aigc"
          and _load_json(AIGC_FIXTURE).get("fixture_version") == FIXTURE_VERSION)
    sb_fx = _load_json(STORYBOARD_FIXTURE)
    aigc_fx = _load_json(AIGC_FIXTURE)
    check("T0 链与种子口径: 链=Core→Script→Cinematic(→Summary), seed=42",
          sb_fx.get("chain") == CHAIN_NODES[:3] and sb_fx.get("seed") == SEED
          and aigc_fx.get("chain") == CHAIN_NODES and aigc_fx.get("seed") == SEED,
          f"chain={sb_fx.get('chain')} seed={sb_fx.get('seed')}")
    check("T0 fixture 固定输入与当前 FIXED_INPUTS 逐字段一致 (fixtures↔代码零错配)",
          sb_fx.get("inputs") == _fixture_inputs() and aigc_fx.get("inputs") == _fixture_inputs(),
          f"fx={sb_fx.get('inputs')}")
    md5_before = (_md5_file(STORYBOARD_FIXTURE), _md5_file(AIGC_FIXTURE))

    print("T1 重放真实链")
    mod = load_pkg()
    from aggregator.storyboard_contract import CANON_SHOT_KEYS
    cine_main, cine_data, sum_data = run_chain(mod)
    check("T1 重放: 分镜表非空且每镜键 ⊆ 契约 35 键",
          len(cine_data.get("分镜表", [])) > 0
          and all(set(s.keys()) <= set(CANON_SHOT_KEYS) for s in cine_data["分镜表"]),
          f"n={len(cine_data.get('分镜表', []))} "
          f"diff={sorted(set(cine_data['分镜表'][0].keys()) - set(CANON_SHOT_KEYS))}")
    check("T1 重放产物与 fixture expect 结构逐字段零 diff (结构漂移零容忍)",
          structural_diff(prune(cine_data), sb_fx.get("expect")) == [],
          f"diffs={structural_diff(prune(cine_data), sb_fx.get('expect'))[:5]}")

    print("T2 精确口径 (镜数/总时长/顶层键)")
    check("T2 镜数精确一致",
          len(cine_data["分镜表"]) == len(sb_fx["expect"]["分镜表"])
          and cine_data.get("分镜数") == sb_fx["expect"].get("分镜数"),
          f"got={len(cine_data['分镜表'])} want={len(sb_fx['expect']['分镜表'])}")
    check("T2 总时长秒精确一致",
          cine_data.get("总时长秒") == sb_fx["expect"].get("总时长秒"),
          f"got={cine_data.get('总时长秒')} want={sb_fx['expect'].get('总时长秒')}")
    check("T2 顶层键集合精确一致",
          set(cine_data.keys()) == set(sb_fx["expect"].keys()),
          f"diff={sorted(set(cine_data.keys()) ^ set(sb_fx['expect'].keys()))}")
    check("T2 contract_version == 1 (生产链 v1 兼容章; v2 产物自行声明 2)",
          cine_data.get("contract_version") == 1 and sb_fx["expect"].get("contract_version") == 1)
    check("T2 文本锚口径: 首镜 AIGC提示词 前 64 字符锚与 fixture 逐字符一致",
          (cine_data["分镜表"][0]["AIGC提示词"][:ANCHOR_LEN] + "…")
          == sb_fx["expect"]["分镜表"][0]["AIGC提示词"]
          and len(sb_fx["expect"]["分镜表"][0]["AIGC提示词"]) == ANCHOR_LEN + 1,
          f"anchor={sb_fx['expect']['分镜表'][0]['AIGC提示词'][:32]}...")

    print("T3 golden_aigc 重放")
    aigc_fresh = {
        "AIGC分镜提示词": prune(sum_data.get("AIGC分镜提示词", [])),
        "AIGC生产设置": prune(sum_data.get("AIGC生产设置", {})),
        "叙事编排": prune(sum_data.get("叙事编排", {})),
        "item_count": len(sum_data.get("AIGC分镜提示词", [])),
        "shot_count": len(sum_data.get("分镜表", [])),
    }
    check("T3 AIGC 结构逐字段零 diff",
          structural_diff(aigc_fresh, aigc_fx.get("expect")) == [],
          f"diffs={structural_diff(aigc_fresh, aigc_fx.get('expect'))[:5]}")
    check("T3 AIGC 提示词条数 == 分镜数 (精确)",
          aigc_fresh["item_count"] == aigc_fresh["shot_count"] == len(cine_data["分镜表"]),
          f"items={aigc_fresh['item_count']} shots={aigc_fresh['shot_count']}")
    check("T3 AIGC生产设置 键集合齐全 (生产模式/画幅/角色一致性锚/全局负面约束/推荐模型)",
          {"生产模式", "画幅", "推荐时长", "角色一致性锚", "全局负面约束", "推荐模型"}
          <= set(aigc_fresh["AIGC生产设置"].keys()),
          f"keys={sorted(aigc_fresh['AIGC生产设置'].keys())}")
    check("T3 首镜 AIGC提示词 锚逐字符一致 (七要素文本锚)",
          (sum_data["AIGC分镜提示词"][0]["AIGC提示词"][:ANCHOR_LEN] + "…")
          == aigc_fx["expect"]["AIGC分镜提示词"][0]["AIGC提示词"])

    print("T4 确定性基线与守卫")
    _m2, cine_data_2, sum_data_2 = run_chain(mod)
    check("T4 同进程二次链跑: Cinematic 产物 md5 一致 (全链确定性基线)",
          json.dumps(cine_data, ensure_ascii=False, sort_keys=True)
          == json.dumps(cine_data_2, ensure_ascii=False, sort_keys=True))
    check("T4 同进程二次链跑: Summary AIGC 结构一致",
          json.dumps(aigc_fresh, ensure_ascii=False, sort_keys=True)
          == json.dumps({
              "AIGC分镜提示词": prune(sum_data_2.get("AIGC分镜提示词", [])),
              "AIGC生产设置": prune(sum_data_2.get("AIGC生产设置", {})),
              "叙事编排": prune(sum_data_2.get("叙事编排", {})),
              "item_count": len(sum_data_2.get("AIGC分镜提示词", [])),
              "shot_count": len(sum_data_2.get("分镜表", []))},
              ensure_ascii=False, sort_keys=True))

    print("T5 比较器与口径自检 (不是摆设)")
    mutated = json.loads(json.dumps(sb_fx["expect"]))
    mutated["分镜表"][0]["景别"] = "特写"  # 篡改一个短文本字段
    check("T5 篡改结构字段 → 比较器报 diff (比较器有效性)",
          structural_diff(mutated, sb_fx["expect"]) != [])
    long_txt = "长" * 200
    check("T5 prune 口径: 长文本截为 64 字符锚, 短文本原样保留",
          prune(long_txt) == "长" * ANCHOR_LEN + "…" and prune("短") == "短")
    check("T5 常规运行零写盘: 套件前后 fixture 文件 md5 不变",
          (_md5_file(STORYBOARD_FIXTURE), _md5_file(AIGC_FIXTURE)) == md5_before)


# =====================================================================
def main():
    if "--regen" in sys.argv:
        regen()
        return
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    print(f"\ngolden 回放结果: {PASS} PASS / {FAIL} FAIL")
    if FAILURES:
        print("失败明细:")
        for f_ in FAILURES[:10]:
            print("  -", f_[:200])
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
