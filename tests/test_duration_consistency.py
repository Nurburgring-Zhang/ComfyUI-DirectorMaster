# -*- coding: utf-8 -*-
"""
批次6 D2 — 4 模式时长口径一致性测试 (tests/test_duration_consistency.py)
=========================================================================
根因 (已两重闭合): _renorm_durations 旧第三步残差按比例摊回无下限钳制 + 残差整包倾倒
单个 big 镜 → 负时长 (E2E 四模式各 1 个: -5.5/-25.3/-5.6/-26.8s) → 契约 non-positive 拒收。
本套件钉死修复不变量。

覆盖矩阵:
  T1  合成 shots × 多 seed × 多预算: 无负值 / 每镜 ≥0.2 / sum(durs)==budget±0.1 (可达时)
  T2  禁止单镜整包倾倒 (大规模摊回后最大镜值有界, 旧实现曾达 17.2/29.7s 离群)
  T3  病态预算 (budget < 0.2×有效镜数) 诚实跳过: 原时长保留 / 返回 (0, total) / 绝不产负值
  T4  临界预算 budget == 0.2×N: 全镜贴地板 0.2 且 sum 精确命中
  T5  同 seed 确定性 (两次调用逐镜一致) + 张力极值/畸形输入鲁棒 (cur≤0 镜原样保留)
  T6  E2E 复验: cinematic_studio 真实 4 模式路径 (蒙太奇大师/一秒三闪/子弹时间/MV 慢镜)
      全输入链跑通, 断言分镜 JSON 无负时长 / 每镜 ≥0.2 / 总时长覆盖预算 /
      validate_storyboard 零诊断 (修复前此处 invalid-duration 必红)

自包含脚本 (纯标准库, 参照 tests/test_storyboard_contract.py 写法):
  python -X utf8 tests/test_duration_consistency.py
退出码: 0 = 全部通过, 1 = 有失败。
"""
import contextlib
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.plot_topology import _renorm_durations
from aggregator.storyboard_contract import validate_storyboard

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def _make_shots(n, pool, t_pool=None):
    shots = []
    for i in range(n):
        d = pool[i % len(pool)]
        t = (t_pool or [(i % 10) + 1])[i % len(t_pool or [1])]
        shots.append({"dur_sec": d, "dur": f"{d:.1f}s", "tension_level": t})
    return shots


def _durs(shots):
    return [s.get("dur_sec") for s in shots]


# 4 模式端到端实测分布 (b6_dur_repro/b6_renorm_repro 闭合口径): (镜数, 时长池)
MODE_CASES = {
    "蒙太奇大师": (3600, [3.0, 0.5, 1.2, 1.8, 2.4, 3.0, 0.6, 1.2, 1.6, 2.1, 2.8, 0.6,
                          1.2, 1.6, 2.3, 3.0]),
    "一秒三闪":   (11400, [0.4, 0.3, 1.2, 0.4, 0.4, 0.4, 0.3, 1.2, 0.4, 0.4, 0.6, 1.2,
                           0.4, 0.3]),
    "子弹时间":   (9000, [0.6, 0.5, 1.1, 0.6, 0.6, 0.6, 1.2, 0.6, 1.1, 0.5, 0.6, 1.2, 0.6]),
    "MV 慢镜":    (4800, [0.7, 1.8, 1.0, 1.5, 0.7, 2.1, 1.1, 1.4, 1.6, 2.3, 0.8, 1.9, 2.6,
                          1.3]),
}
SEEDS = (1, 42, 99, 7, 2026)


# =====================================================================
def run_synthetic():
    # -----------------------------------------------------------------
    print("T1 合成矩阵: 无负值 / 每镜 ≥0.2 / sum==budget±0.1")
    n_bad = 0
    for mode, (n, pool) in MODE_CASES.items():
        for seed in SEEDS:
            shots = _make_shots(n, pool)
            before_sum = sum(_durs(shots))
            changed, total = _renorm_durations(shots, 5400.0, seed)
            durs = [d for d in _durs(shots) if d is not None]
            neg = [d for d in durs if d <= 0]
            under = [d for d in durs if d < 0.2]
            drift = abs(sum(durs) - 5400.0)
            ok = (isinstance(changed, int) and abs(total - before_sum) < 1e-6
                  and not neg and not under and drift <= 0.1)
            if not ok:
                n_bad += 1
                print(f"    [BAD] {mode} seed={seed}: neg={neg[:3]} under={under[:3]} "
                      f"drift={drift:.3f} total={total} changed={changed}")
    check("T1 4 模式分布 × 5 seeds × budget=5400 全部满足不变量 (20 组)", n_bad == 0,
          f"bad={n_bad}")

    n_bad2 = 0
    for n, budget in ((8, 30.0), (24, 18.0), (50, 45.5), (120, 300.0), (7, 12.3)):
        for seed in SEEDS:
            shots = _make_shots(n, [1.0, 2.0, 3.0, 0.5, 4.0, 0.7, 2.5])
            _renorm_durations(shots, budget, seed)
            durs = [d for d in _durs(shots) if d is not None]
            if ([d for d in durs if d <= 0] or [d for d in durs if d < 0.2]
                    or abs(sum(durs) - budget) > 0.1):
                n_bad2 += 1
                print(f"    [BAD] n={n} budget={budget} seed={seed}: "
                      f"min={min(durs)} drift={abs(sum(durs) - budget):.3f}")
    check("T1 小/中规模 × 5 seeds × 5 预算 全部满足不变量 (25 组)", n_bad2 == 0,
          f"bad={n_bad2}")

    # -----------------------------------------------------------------
    print("T2 禁止单镜整包倾倒")
    dump_bad = []
    for mode, (n, pool) in MODE_CASES.items():
        cap = max(pool) + 2.0
        for seed in SEEDS:
            shots = _make_shots(n, pool)
            _renorm_durations(shots, 5400.0, seed)
            mx = max(d for d in _durs(shots) if d is not None)
            if mx > cap:
                dump_bad.append(f"{mode}/s{seed}: max={mx} cap={cap}")
    check("T2 大规模摊回后最大镜值有界 (≤ 时长池峰值+2s; 旧实现 17.2/29.7s 离群必红)",
          not dump_bad, f"bad={dump_bad[:3]}")

    # -----------------------------------------------------------------
    print("T3 病态预算诚实跳过")
    shots3 = _make_shots(10, [1.0])
    before3 = _durs(shots3)
    changed3, total3 = _renorm_durations(shots3, 1.5, 42)
    check("T3 budget 1.5 < 0.2×10 → 返回 (0, 原总时长)",
          (changed3, total3) == (0, 10.0), f"got=({changed3}, {total3})")
    check("T3 原时长逐镜保留 (零改写)", _durs(shots3) == before3,
          f"got={_durs(shots3)}")
    check("T3 无负值产出", all(d > 0 for d in _durs(shots3)))
    shots3b = _make_shots(6, [0.5])
    changed3b, total3b = _renorm_durations(shots3b, 1.0, 42)
    check("T3 budget 1.0 < 0.2×6=1.2 → 诚实跳过 (0, 3.0) 且原时长保留",
          (changed3b, total3b) == (0, 3.0) and _durs(shots3b) == [0.5] * 6,
          f"got=({changed3b}, {total3b}) durs={_durs(shots3b)}")

    # -----------------------------------------------------------------
    print("T4 临界预算 budget == 0.2×N")
    shots4 = _make_shots(10, [3.0], t_pool=[9])
    changed4, _t4 = _renorm_durations(shots4, 2.0, 42)
    durs4 = _durs(shots4)
    check("T4 全镜贴地板 0.2 且 sum 精确 == 2.0",
          all(d == 0.2 for d in durs4) and abs(sum(durs4) - 2.0) < 1e-9
          and changed4 == 10, f"durs={durs4} changed={changed4}")

    # -----------------------------------------------------------------
    print("T5 同 seed 确定性与鲁棒性")
    det_ok = True
    for mode, (n, pool) in MODE_CASES.items():
        a = _make_shots(n, pool)
        b = _make_shots(n, pool)
        _renorm_durations(a, 5400.0, 42)
        _renorm_durations(b, 5400.0, 42)
        if _durs(a) != _durs(b):
            det_ok = False
            print(f"    [BAD] {mode}: 同 seed 两次结果不一致")
    check("T5 同 seed 两次调用逐镜一致 (确定性, 4 模式 × 大规模)", det_ok)
    mix5 = [{"dur_sec": 2.0, "tension_level": 1},
            {"dur_sec": 0, "tension_level": 5},
            {"dur_sec": "坏值", "tension_level": 5},
            {"dur_sec": 6.0, "tension_level": 10},
            {"dur_sec": None, "tension_level": 5}]
    _renorm_durations(mix5, 8.0, 42)
    check("T5 cur≤0/畸形镜原样保留 (不参与摊回不产负值)",
          _durs(mix5)[1] == 0 and _durs(mix5)[2] == "坏值" and _durs(mix5)[4] is None
          and mix5[0]["dur_sec"] >= 0.2 and mix5[3]["dur_sec"] >= 0.2
          and abs(mix5[0]["dur_sec"] + mix5[3]["dur_sec"] - 8.0) <= 0.1,
          f"got={_durs(mix5)}")
    t15 = _make_shots(40, [1.0], t_pool=[1])
    t10 = _make_shots(40, [1.0], t_pool=[10])
    _renorm_durations(t15, 40.0, 42)
    _renorm_durations(t10, 40.0, 42)
    check("T5 张力极值 (全 1 / 全 10) 不变量仍成立",
          all(d >= 0.2 for d in _durs(t15)) and abs(sum(_durs(t15)) - 40.0) <= 0.1
          and all(d >= 0.2 for d in _durs(t10)) and abs(sum(_durs(t10)) - 40.0) <= 0.1)


# =====================================================================
def _load_pkg():
    spec = importlib.util.spec_from_file_location("dm_dur_consistency",
                                                  os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dm_dur_consistency"] = mod
    spec.loader.exec_module(mod)
    return mod


def _defaults(cls):
    it = cls.INPUT_TYPES()
    kw = {}
    for k, v in it.get("required", {}).items():
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], list):
            kw[k] = "Seedance 2.5" if k == "目标视频模型" else v[0][0]
        elif isinstance(v, tuple) and v and v[0] == "STRING":
            kw[k] = (v[1] or {}).get("default", "")
        elif isinstance(v, tuple) and v and v[0] in ("INT", "FLOAT"):
            kw[k] = (v[1] or {}).get("default", 0)
        elif isinstance(v, tuple) and v and v[0] == "BOOLEAN":
            kw[k] = (v[1] or {}).get("default", False)
    return kw


def _call(cls, kw):
    inst = cls()
    res = getattr(inst, cls.FUNCTION)(**kw)
    if isinstance(res, tuple) and len(res) == 2 and isinstance(res[1], dict) \
            and isinstance(res[0], tuple):
        res = res[0]
    if not isinstance(res, tuple):
        res = (res,)
    return res


def _dur_num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = v.strip().rstrip("sS秒")
        try:
            return float(t)
        except ValueError:
            return None
    return None


def run_e2e():
    print("T6 E2E 复验: cinematic_studio 真实 4 模式路径")
    mod = _load_pkg()
    M = mod.NODE_CLASS_MAPPINGS
    core_out = _call(M["DirectorMasterCore"], _defaults(M["DirectorMasterCore"]))
    core_pack = str(core_out[1])
    script = _call(M["DirectorMasterScript"],
                   {**_defaults(M["DirectorMasterScript"]), "核心数据包": core_pack})[0]

    for mode in ("蒙太奇大师", "一秒三闪", "子弹时间", "MV 慢镜"):
        kw = _defaults(M["DirectorMasterCinematic"])
        kw["核心数据包"] = core_pack
        kw["剧本输入"] = str(script)
        for k, v in M["DirectorMasterCinematic"].INPUT_TYPES()["required"].items():
            if isinstance(v, (list, tuple)) and v and isinstance(v[0], list) \
                    and mode in v[0]:
                kw[k] = mode
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            cine = _call(M["DirectorMasterCinematic"], kw)
        payload = json.loads(str(cine[1]))
        shots = payload.get("分镜表", [])
        durs = [_dur_num(s.get("时长")) for s in shots]
        bad = [d for d in durs if d is None or d <= 0]
        under = [d for d in durs if d is not None and d < 0.2]
        total_sec = payload.get("总时长秒")
        drift = abs(sum(d for d in durs if d is not None) - float(total_sec or 0))
        rep = validate_storyboard(payload)
        check(f"T6 {mode}: 分镜 {len(shots)} 个无负时长/无不可解析时长",
              len(shots) > 0 and not bad, f"bad={bad[:4]}")
        check(f"T6 {mode}: 每镜 ≥0.2s (地板)", not under, f"under={under[:4]}")
        check(f"T6 {mode}: sum(时长)==总时长秒±0.15 (总时长覆盖片长 "
              f"{total_sec})", drift <= 0.15, f"drift={drift:.3f}")
        check(f"T6 {mode}: validate_storyboard ok=True 零 errors (修复前 "
              f"invalid-duration 必红)",
              rep["ok"] is True and rep["errors"] == [],
              f"e={sorted(set(e['code'] for e in rep['errors']))[:6]}")


# =====================================================================
def main():
    try:
        run_synthetic()
    except Exception as e:
        check("合成套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    try:
        run_e2e()
    except Exception as e:
        check("E2E 套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    print(f"\n时长一致性测试结果: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
