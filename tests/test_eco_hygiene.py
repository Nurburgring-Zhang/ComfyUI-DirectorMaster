# -*- coding: utf-8 -*-
"""
批次5 WaveB builder-p3 — 批次7 移交 2 卫生项 测试
(tests/test_eco_hygiene.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch5.md 验收口径⑧ + review_b7_r2_adversarial.md
R2A-01 LOW / R2A-OBS-3 OBS 移交原文):
  T0 R2A-01 对齐探针: dm_memory 9 文件 _safe_name 与 pipeline.safe_name 同输入同输出
     (样本补齐批次7 T7 放空面: 控制字符 \x01/\x7f/\n、路径符、纯控制字符、空串、
     中文原样、超长 100 字截断+sha1 后缀、尾点、NTFS 大小写面、纯数字、None)
  T1 同输入两次恒等 (9 文件 + pipeline 全数)
  T2 R2A-01 探针6 正例复现: pipeline.safe_name('坏名\\x01项目') = '坏名_项目_a5b6d315'
     (含 "_" 替换且零 \\x01 残留) — dm_memory 侧修复后与 episodes/ 侧同映射
  T3 超长 100 字 → 截 40 + "_" + sha1[:8] 后缀结构断言
  T4 输出零非法字符残留 (基准字符类 [\x00-\\x1f\\x7f/\\\\:*?"<>|] 全集扫描)
  T5 R2A-OBS-3 死代码断言: ledger.py 源码零 "_RE_MARKER_PROBE" (含 aggregator 全目录
     grep 式扫描) + 失效 import re 清理闭环 + ledger 模块导入冒烟 (删除未伤模块)
  T6 R2A-04 (批次5 fixer-r2): .gitignore eco 段否定行锚定静态断言 — 含
     !eco/packs/** 与 !eco/packs/**/ref_ledger/ (第三方包入库面恢复, 后行优先)
纪律: 零仓库内写入, 零网络零 LLM。
退出码: 0 = 无 FAIL。运行: python -X utf8 tests/test_eco_hygiene.py
"""
import hashlib
import importlib
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


pipeline = importlib.import_module("aggregator.episode_pipeline.pipeline")
safe_name = pipeline.safe_name

# R2A-01 同款 9 处 (review_b7_r2_adversarial.md:36 全列), importlib 正常 import 后 getattr
DM_MODULES = [
    "series_inherit", "evolution", "anchor_link", "injection",
    "preference_store", "procedure_memory", "retrieval", "shot_cards",
    "style_bible",
]
dm_fns = {}
for m in DM_MODULES:
    mod = importlib.import_module("aggregator.dm_memory." + m)
    dm_fns[m] = getattr(mod, "_safe_name")
check("T-pre 9 文件 _safe_name 全部导入成功", len(dm_fns) == 9)

# 基准字符类 (pipeline.py:35 _UNSAFE_FILENAME_RE 同源), 用于零残留扫描
UNSAFE = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')

SAMPLES = [
    "坏名\x01项目",          # R2A-01 原始探针 (控制字符 \x01 → dm_memory OSError 面)
    "proj\nname\x7f",        # \n + DEL (\x7f)
    "C:\\bad\\path",         # 盘符路径
    "a/b*c?d",               # 路径符 + 通配符
    "\x01\x02\x03",          # 纯控制字符
    "",                      # 空串
    "纯中文项目名",           # 中文原样
    "长" * 50,               # 超长 100 字 → 截 40 + sha1 后缀
    "proj.",                 # Windows 剥尾 (尾点)
    "Project",               # NTFS 大小写折叠面
    "123",                   # 纯数字
    None,                    # 不炸
]

# ----------------------------------------------------------------
print("T0 R2A-01 对齐探针: 9 文件 _safe_name 与 pipeline.safe_name 同输入同输出")
for idx, s in enumerate(SAMPLES):
    want = safe_name(s)
    for m in DM_MODULES:
        got = dm_fns[m](s)
        check(f"T0[{idx}] {m}._safe_name({s!r}) == pipeline.safe_name",
              got == want, f"dm={got!r} pipeline={want!r}")

# ----------------------------------------------------------------
print("T1 同输入两次恒等 (确定性)")
for idx, s in enumerate(SAMPLES):
    check(f"T1[{idx}] pipeline 两次恒等 ({s!r})", safe_name(s) == safe_name(s))
    for m in DM_MODULES:
        check(f"T1[{idx}] {m} 两次恒等", dm_fns[m](s) == dm_fns[m](s))

# ----------------------------------------------------------------
print("T2 R2A-01 探针6 正例复现: '坏名\\x01项目' → '坏名_项目_a5b6d315'")
out = safe_name("坏名\x01项目")
check("T2 pipeline 输出 = 坏名_项目_a5b6d315 (R2A 报告实证值)",
      out == "坏名_项目_a5b6d315", f"实际 {out!r}")
check("T2 输出含 _ 替换", "_" in out)
check("T2 输出零 \\x01 残留", "\x01" not in out)
dm_out = dm_fns["series_inherit"]("坏名\x01项目")
check("T2 dm_memory 侧同输出 (R2A-01 分叉收敛)",
      dm_out == out, f"dm={dm_out!r} pipeline={out!r}")

# ----------------------------------------------------------------
print("T3 超长 100 字 → 截 40 + sha1 后缀结构")
long_in = "长" * 50
long_out = safe_name(long_in)
suffix = hashlib.sha1(long_in.encode("utf-8", errors="replace")).hexdigest()[:8]
check("T3 长度 = 40 + 1 + 8", len(long_out) == 49, f"实际 {len(long_out)}")
check("T3 前 40 字截断保留", long_out[:40] == "长" * 40)
check("T3 后缀 = 原始 raw sha1[:8]", long_out[41:] == suffix,
      f"实际 {long_out[41:]!r} 期望 {suffix!r}")
for m in DM_MODULES:
    check(f"T3 {m} 同结构", dm_fns[m](long_in) == long_out)

# ----------------------------------------------------------------
print("T4 输出零非法字符残留 (基准字符类全集扫描)")
for idx, s in enumerate(SAMPLES):
    got = safe_name(s)
    check(f"T4[{idx}] pipeline 输出零非法字符 ({s!r})", UNSAFE.search(got) is None,
          f"残留 {UNSAFE.search(got)!r}")
    for m in DM_MODULES:
        g = dm_fns[m](s)
        check(f"T4[{idx}] {m} 输出零非法字符", UNSAFE.search(g) is None,
              f"残留 {UNSAFE.search(g)!r}")

# ----------------------------------------------------------------
print("T5 R2A-OBS-3: ledger.py 死代码 _RE_MARKER_PROBE 删除断言")
ledger_path = os.path.join(ROOT, "aggregator", "episode_pipeline", "ledger.py")
with open(ledger_path, "r", encoding="utf-8") as f:
    ledger_src = f.read()
check("T5 ledger.py 源码零 _RE_MARKER_PROBE", "_RE_MARKER_PROBE" not in ledger_src)
check("T5 ledger.py 失效 import re 一并清理 (re 仅被死代码使用, 逐行核实)",
      "import re" not in ledger_src)
ledger_mod = importlib.import_module("aggregator.episode_pipeline.ledger")
check("T5 ledger 模块导入冒烟 (删除未伤模块)",
      callable(getattr(ledger_mod, "verify_coverage", None)))
ok5, err5 = ledger_mod.verify_coverage("正文甲正文乙",
                                       [{"start": 0, "end": 3, "category": "episode"},
                                        {"start": 3, "end": 6, "category": "episode"}])
check("T5 verify_coverage 功能冒烟 (MARKER_RES 路径无恙)", ok5 is True and err5 == [],
      f"{ok5} {err5}")

# grep 式全仓扫描 (aggregator 目录全部 .py, 排除 __pycache__)
hits = []
scan_root = os.path.join(ROOT, "aggregator")
for dirpath, dirnames, filenames in os.walk(scan_root):
    dirnames[:] = [d for d in dirnames if d != "__pycache__"]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                if "_RE_MARKER_PROBE" in f.read():
                    hits.append(fp)
        except Exception:
            continue
check("T5 aggregator 全目录扫描零 _RE_MARKER_PROBE 命中", hits == [],
      f"命中 {hits}")

# ----------------------------------------------------------------
print("T6 R2A-04: .gitignore eco 段否定行锚定 (第三方包入库面恢复)")
gi_path = os.path.join(ROOT, ".gitignore")
with open(gi_path, "r", encoding="utf-8") as f:
    gi_src = f.read()
check("T6 .gitignore 含否定行 !eco/packs/**", "!eco/packs/**" in gi_src)
check("T6 .gitignore 含否定行 !eco/packs/**/ref_ledger/",
      "!eco/packs/**/ref_ledger/" in gi_src)
check("T6 否定行位于 eco 忽略规则之后 (gitignore 后行规则优先恢复)",
      gi_src.index("dm_pack.json") < gi_src.index("!eco/packs/**")
      and gi_src.index("ref_ledger/") < gi_src.index("!eco/packs/**/ref_ledger/"))
check("T6 运行时忽略规则未被移除 (dm_pack.json / ref_ledger/ 仍在, 运行时产物照旧忽略)",
      "dm_pack.json" in gi_src and "ref_ledger/" in gi_src)

# ----------------------------------------------------------------
print()
print(f"=== test_eco_hygiene: PASS={PASS} FAIL={FAIL} ===")
sys.exit(0 if FAIL == 0 else 1)
