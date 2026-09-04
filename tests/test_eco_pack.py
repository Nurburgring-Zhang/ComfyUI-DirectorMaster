# -*- coding: utf-8 -*-
"""
批次5 WaveA builder-p1 — dm_pack 包注册表 测试
(tests/test_eco_pack.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch5.md 验收口径①, builder-p1 部分):
  T0 接口契约 (load_pack/semver_ok/register_packs/CURRENT_DM_VERSION + 门面惰性导出)
  T1 合法包载入 + 六字段回读 (依赖满足对 + eco 根目录形态经 packs 子目录下钻)
  T2 负样本1: 缺 entry 字段 → errors 显式列出且拒绝载入 (验收①)
  T3 负样本2: min_dm_version="99.0.0" 版本不兼容 → 拒绝载入 (验收①)
  T4 负样本3: dependencies 指向未注册包 → 拒绝载入, 同场合规包照常注册 (验收①)
  T5 附加负样本: pack_id 冲突 → 先到先得, 重复包拒绝
  T6 附加负样本: 非 semver 串 ("abc") → 诚实拦截拒绝载入
  T7 entry 文件不存在 → 注册层拦截 (字段闸放行, 文件闸拦截)
  T8 空目录/目录不存在 → ok 空结果不报错 (验收①)
  T9 确定性: 同输入两次调用结果逐字节一致 (排序显式 key)
  T10 semver_ok 三段数值比较单元 (等值/低于/高于/预发布前缀/非 semver)
纪律: 测试产物一律 tempfile, 零仓库内写入, 零网络零 LLM。退出码: 0 = 无 FAIL。
运行: python -X utf8 tests/test_eco_pack.py
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aggregator.eco import pack_registry as reg_mod

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
    d = tempfile.mkdtemp(prefix="eco_pack_test_")
    TEMP_DIRS.append(d)
    return d


VALID_FIELDS = {
    "pack_id": "demo-pack",
    "version": "1.0.0",
    "min_dm_version": "16.0.0",
    "dependencies": [],
    "tags": ["分镜", "参考"],
    "entry": "entry.py",
}


def make_pack(root, pack_id, *, overrides=None, drop_fields=(), with_entry=True,
              layout="packs"):
    """在 root 下落一个包目录 (UTF-8 显式编码), 返回包目录路径。

    layout="packs": <root>/packs/<pack_id>/  (doctor 默认扫描形态)
    layout="eco":   <root>/eco/packs/<pack_id>/  (聚合门面 eco 根形态)
    """
    base = os.path.join(root, layout) if layout == "packs" else os.path.join(root, "eco", "packs")
    d = os.path.join(base, pack_id)
    os.makedirs(d, exist_ok=True)
    if with_entry:
        with open(os.path.join(d, "entry.py"), "w", encoding="utf-8") as f:
            f.write("# dm_pack entry stub: %s\n" % pack_id)
    fields = dict(VALID_FIELDS)
    fields["pack_id"] = pack_id
    if overrides:
        fields.update(overrides)
    for k in drop_fields:
        fields.pop(k, None)
    with open(os.path.join(d, "dm_pack.json"), "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2, sort_keys=True)
    return d


def blob(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


# ----------------------------------------------------------------
print("T0 接口契约 + 门面惰性导出")
for name in ("load_pack", "semver_ok", "register_packs"):
    check(f"T0 pack_registry.{name} 可调用", callable(getattr(reg_mod, name, None)))
check("T0 CURRENT_DM_VERSION == '17.1.0'", getattr(reg_mod, "CURRENT_DM_VERSION", None) == "17.1.0")
check("T0 REQUIRED_FIELDS 六字段钉死",
      tuple(getattr(reg_mod, "REQUIRED_FIELDS", ()))
      == ("pack_id", "version", "min_dm_version", "dependencies", "tags", "entry"))
import aggregator.eco as eco_mod
check("T0 门面惰性导出 register_packs 接到本模块",
      eco_mod.register_packs is reg_mod.register_packs)

# ----------------------------------------------------------------
print("T1 合法包载入 + 六字段回读 (依赖满足)")
root = temp_dir()
make_pack(root, "dep-core")
make_pack(root, "demo-pack", overrides={"dependencies": ["dep-core"]})
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T1 ok=True 且 errors 空", r["ok"] is True and r["errors"] == [], blob(r["errors"]))
check("T1 两包注册 (排序显式 key 按 pack_id)",
      [p["pack_id"] for p in r["packs"]] == ["demo-pack", "dep-core"])
demo = next((p for p in r["packs"] if p["pack_id"] == "demo-pack"), {})
check("T1 六字段回读正确",
      demo.get("version") == "1.0.0" and demo.get("min_dm_version") == "16.0.0"
      and demo.get("dependencies") == ["dep-core"] and demo.get("tags") == ["分镜", "参考"]
      and demo.get("entry") == "entry.py")
check("T1 pack_dir 回读指向真实包目录",
      os.path.isdir(demo.get("pack_dir", ""))
      and os.path.basename(demo.get("pack_dir", "")) == "demo-pack")
root2 = temp_dir()
make_pack(root2, "demo-pack", layout="eco")
r2 = reg_mod.register_packs([os.path.join(root2, "eco")])
check("T1 eco 根形态 (经 packs 子目录下钻) 同样载入",
      r2["ok"] is True and [p["pack_id"] for p in r2["packs"]] == ["demo-pack"])

# ----------------------------------------------------------------
print("T2 负样本1: 缺 entry 字段")
root = temp_dir()
make_pack(root, "no-entry", drop_fields=("entry",))
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T2 ok=False 且拒绝载入", r["ok"] is False and r["packs"] == [])
check("T2 errors 显式点名 entry",
      len(r["errors"]) == 1 and "entry" in r["errors"][0] and "缺少必填字段" in r["errors"][0],
      blob(r["errors"]))
lp, lerrs = reg_mod.load_pack(os.path.join(root, "packs", "no-entry"))
check("T2 load_pack 直查同为 (None, 显式错误)", lp is None and len(lerrs) == 1 and "entry" in lerrs[0])

# ----------------------------------------------------------------
print("T3 负样本2: min_dm_version='99.0.0' 版本不兼容")
root = temp_dir()
make_pack(root, "future-pack", overrides={"min_dm_version": "99.0.0"})
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T3 ok=False 且拒绝载入", r["ok"] is False and r["packs"] == [])
check("T3 errors 显式点名版本不兼容",
      len(r["errors"]) == 1 and "版本不兼容" in r["errors"][0] and "99.0.0" in r["errors"][0],
      blob(r["errors"]))

# ----------------------------------------------------------------
print("T4 负样本3: dependencies 指向未注册包")
root = temp_dir()
make_pack(root, "ghost-dep", overrides={"dependencies": ["ghost-pack"]})
make_pack(root, "healthy-pack")
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T4 ok=False (registry 级 fail loud)", r["ok"] is False)
check("T4 ghost-dep 被拒且 errors 点名 ghost-pack",
      all(p["pack_id"] != "ghost-dep" for p in r["packs"])
      and len(r["errors"]) == 1 and "ghost-pack" in r["errors"][0] and "依赖未注册包" in r["errors"][0],
      blob(r["errors"]))
check("T4 同场合规包 healthy-pack 照常注册",
      [p["pack_id"] for p in r["packs"]] == ["healthy-pack"])

# ----------------------------------------------------------------
print("T5 附加负样本: pack_id 冲突")
root = temp_dir()
make_pack(root, "twin-pack")
make_pack(root, "twin-pack-inner")
# 两个不同目录名、同一 pack_id
_twin2 = os.path.join(root, "packs", "twin-pack-inner")
with open(os.path.join(_twin2, "dm_pack.json"), "r", encoding="utf-8") as f:
    _fields = json.load(f)
_fields["pack_id"] = "twin-pack"
with open(os.path.join(_twin2, "dm_pack.json"), "w", encoding="utf-8") as f:
    json.dump(_fields, f, ensure_ascii=False, indent=2, sort_keys=True)
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T5 仅先到者注册 (恰好 1 包)",
      r["ok"] is False and len(r["packs"]) == 1 and r["packs"][0]["pack_id"] == "twin-pack")
check("T5 errors 显式点名 pack_id 冲突",
      len(r["errors"]) == 1 and "pack_id 冲突" in r["errors"][0] and "twin-pack" in r["errors"][0],
      blob(r["errors"]))

# ----------------------------------------------------------------
print("T6 附加负样本: 非 semver 串")
root = temp_dir()
make_pack(root, "bad-ver", overrides={"min_dm_version": "abc"})
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T6 ok=False 且拒绝载入 (诚实拦截)", r["ok"] is False and r["packs"] == [])
check("T6 errors 显式点名版本不兼容",
      len(r["errors"]) == 1 and "版本不兼容" in r["errors"][0] and "abc" in r["errors"][0],
      blob(r["errors"]))

# ----------------------------------------------------------------
print("T7 entry 文件不存在 (字段闸放行, 注册层文件闸拦截)")
root = temp_dir()
make_pack(root, "lost-entry", with_entry=False)
lp, lerrs = reg_mod.load_pack(os.path.join(root, "packs", "lost-entry"))
check("T7 load_pack 字段闸放行 (entry 是文件级事实)", lp is not None and lerrs == [])
r = reg_mod.register_packs([os.path.join(root, "packs")])
check("T7 注册层拒绝且 errors 点名 entry 文件不存在",
      r["ok"] is False and r["packs"] == [] and len(r["errors"]) == 1
      and "entry 文件不存在" in r["errors"][0], blob(r["errors"]))

# ----------------------------------------------------------------
print("T8 空目录 / 目录不存在 → ok 空结果不报错")
root = temp_dir()
empty_packs = os.path.join(root, "packs")
os.makedirs(empty_packs, exist_ok=True)
r = reg_mod.register_packs([empty_packs])
check("T8 空目录 ok=True packs=[] errors=[]",
      r == {"ok": True, "packs": [], "errors": []})
r = reg_mod.register_packs([os.path.join(root, "definitely-not-here")])
check("T8 目录不存在 ok=True packs=[] errors=[]",
      r == {"ok": True, "packs": [], "errors": []})
check("T8 None 搜索目录同样空载 ok", reg_mod.register_packs(None) == {"ok": True, "packs": [], "errors": []})

# ----------------------------------------------------------------
print("T9 确定性: 同输入两次调用结果逐字节一致")
root = temp_dir()
make_pack(root, "b-pack")
make_pack(root, "a-pack", overrides={"dependencies": ["b-pack"]})
make_pack(root, "c-pack", overrides={"min_dm_version": "17.1.0"})
search = [os.path.join(root, "packs")]
r1 = reg_mod.register_packs(search)
r2 = reg_mod.register_packs(search)
check("T9 两次调用 registry 逐字节一致", blob(r1) == blob(r2))
check("T9 packs 序显式 key (pack_id 升序)",
      [p["pack_id"] for p in r1["packs"]] == ["a-pack", "b-pack", "c-pack"])

# ----------------------------------------------------------------
print("T10 semver_ok 三段数值比较单元")
cases = [
    ("16.0.0", "17.1.0", True, "低于当前"),
    ("17.1.0", "17.1.0", True, "等值"),
    ("17.2.0", "17.1.0", False, "minor 高于当前"),
    ("18.0.0", "17.1.0", False, "major 高于当前"),
    ("17.1.1", "17.1.0", False, "patch 高于当前"),
    ("17.1.0-rc1", "17.1.0", True, "预发布段取前缀"),
    ("abc", "17.1.0", False, "非 semver 串"),
    ("1.2", "17.1.0", False, "两段不认"),
    ("1.2.3.4", "17.1.0", False, "四段不认"),
    ("1.x.3", "17.1.0", False, "非数值段不认"),
    ("", "17.1.0", False, "空串不认"),
]
for mn, cu, want, why in cases:
    check(f"T10 semver_ok({mn!r}, {cu!r}) == {want} ({why})", reg_mod.semver_ok(mn, cu) is want)

# ----------------------------------------------------------------
print()
print(f"=== test_eco_pack: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        import shutil
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
