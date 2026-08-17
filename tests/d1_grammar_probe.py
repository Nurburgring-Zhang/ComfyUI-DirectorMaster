# -*- coding: utf-8 -*-
"""
V14.3 D1 验证 — Cinematic 同节奏簇镜头语法差异化
====================================================
同一核心数据包 (同场景/同导演) 下跑全部 63 Cinematic 模式:
  1. 全字段指纹 (整行) 唯一性
  2. 镜头语法子集指纹 (景别/运镜/焦段/时长) 唯一性  ← D1 目标
  3. 同簇 (同节奏签名) 组内语法指纹对比
退出码 0 = D1 达标
"""
import os, sys, hashlib, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.stdout.reconfigure(encoding="utf-8")

spec = importlib.util.spec_from_file_location("dm_d1", os.path.join(ROOT, "__init__.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["dm_d1"] = mod
spec.loader.exec_module(mod)
M = mod.NODE_CLASS_MAPPINGS


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


def call(cls, kw):
    inst = cls()
    res = getattr(inst, cls.FUNCTION)(**kw)
    if not isinstance(res, tuple):
        res = (res,)
    return res


# Core 默认包 (确定性)
core_cls = M["DirectorMasterCore"]
core_res = call(core_cls, defaults(core_cls))
core_pack = core_res[1]

cine = M["DirectorMasterCinematic"]
it = cine.INPUT_TYPES()
modes = it["required"]["画面模式"][0]
print(f"Cinematic 模式数: {len(modes)}")

SHOT_ROW = re.compile(r"^\s*(\d+)\s+\S")
_DUR_CELL = re.compile(r"^\d+(\.\d+)?s$")


def parse_rows(text):
    """返回 (full_blocks, gram_rows): full=每镜整块(含子行), gram=景别/运镜/焦段/时长列."""
    lines = str(text).splitlines()
    blocks = []
    gram_rows = []
    cur = None
    for ln in lines:
        m = SHOT_ROW.match(ln)
        cells = ln.split()
        if m and len(cells) >= 7 and _DUR_CELL.match(cells[6]):
            if cur is not None:
                blocks.append(cur)
            cur = [ln.rstrip()]
            # 镜号 阶段 类型阶段 景别 运镜 焦段 时长
            gram_rows.append(tuple(cells[3:7]))
        elif cur is not None and ln.strip():
            cur.append(ln.rstrip())
    if cur is not None:
        blocks.append(cur)
    return blocks, gram_rows


results = {}
for mode in modes:
    kw = defaults(cine)
    kw["画面模式"] = mode
    kw["核心数据包"] = core_pack
    res = call(cine, kw)
    main = res[0]
    blocks, gram_rows = parse_rows(main)
    full_fp = hashlib.md5(repr(blocks).encode("utf-8", "replace")).hexdigest()
    gram_fp = hashlib.md5(repr(gram_rows).encode("utf-8", "replace")).hexdigest()
    pm = re.search(r"节奏签名: ([^ |]+)", str(main))
    sig = pm.group(1) if pm else "?"
    results[mode] = {"full": full_fp, "gram": gram_fp, "sig": sig, "shots": len(blocks)}

full_set = set(r["full"] for r in results.values())
gram_set = set(r["gram"] for r in results.values())
print(f"全字段指纹唯一: {len(full_set)}/{len(results)}")
print(f"镜头语法指纹唯一: {len(gram_set)}/{len(results)}")

clusters = {}
for mode, r in results.items():
    clusters.setdefault(r["sig"], []).append(mode)
print(f"\n节奏簇数: {len(clusters)} (多成员簇 {sum(1 for v in clusters.values() if len(v) > 1)} 个)")

collisions = []
for sig, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
    if len(members) < 2:
        continue
    fps = {m: results[m]["gram"] for m in members}
    uniq = len(set(fps.values()))
    status = "OK" if uniq == len(members) else "COLLISION"
    print(f"  簇[{sig}] {len(members)}模式 语法唯一 {uniq}/{len(members)} {status}")
    if uniq != len(members):
        seen = {}
        for m, f in fps.items():
            seen.setdefault(f, []).append(m)
        for f, ms in seen.items():
            if len(ms) > 1:
                collisions.append((sig, ms))

if collisions:
    print("\n!!! 同簇语法指纹碰撞:")
    for sig, ms in collisions:
        print(f"  簇[{sig}]: {ms}")
    sys.exit(1)
print("\nD1 验证通过: 全部同簇模式镜头语法指纹唯一")
sys.exit(0)
