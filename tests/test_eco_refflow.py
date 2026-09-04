# -*- coding: utf-8 -*-
"""
批次5 WaveA builder-p2 — 参考素材流: 授权边界 + 三列表 + refs 注入零漂移 测试
(tests/test_eco_refflow.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch5.md 验收口径, builder-p2 部分):
  T0 接口契约 + eco 门面 refflow_register 端到端 (合法/负样本各一)
  T1 授权边界负样本: 缺 source / 缺 authorization / 双缺 (None/空串/纯空白) →
     全部 ok=False + errors 显式 + ref_ledger 目录零文件落盘 (验收②)
  T2 合法登记: 台账存在 / JSON 可回读 / LEGALESE 边界字段 / ref_id 幂等覆盖 /
     分项目分文件 / safe_project 碰撞后缀 (验收②)
  T3 三列表: 混合笔记逐行归类 + 无法归类行落取舍 + 空白行丢弃 + 三列齐备
     且逐条非空 + str/list 双输入一致 (验收③)
  T4 refs 注入零漂移: 既有键逐字节深比对 (shots/slots/schema_version) + 既有
     refs 追加不去重 + 空列表零漂移不加键 (验收④)
  T5 确定性: 同输入两次登记台账逐字节一致 + 同 out_dir 重登记幂等 + deconstruct/
     inject 双跑一致 (无随机/无时间戳)
  T6 谱系源登记 anchor_lineage: JSONL 追加 / ts 无时间戳 / lineage_kind 对齐
     asset_master 词汇 / asset_id 回退 ref_id / 跨目录逐字节一致
  T7 LOW-1: 空 ref_id (None/空串/纯空白) → 中文 ValueError 拒绝 + 台账零落盘
  T8 LOW-3: inject_refs refs 类型校验 (str/元组/含非 dict 项) → 中文 ValueError
     拒绝且 contract 逐字节零漂移
  T9 MED-1 真并发: 双 subprocess 同时 register_ref 同一台账 → 20 条目零丢失 +
     JSON 可回读 (乐观并发写收口)
  T10 R2A-01 同进程多线程压测 (ThreadPoolExecutor 4 线程 × 5 次 register_ref
     同一台账) → 20 条目零丢失 + JSON 完整可解析 (无撕裂写)
纪律: 测试产物一律 tempfile, 零网络零 LLM 零仓库内写入。退出码: 0 = 无 FAIL。
运行: python -X utf8 tests/test_eco_refflow.py
"""
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aggregator.eco import ref_flow as rf

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
    d = tempfile.mkdtemp(prefix="eco_refflow_test_")
    TEMP_DIRS.append(d)
    return d


def jd(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def ledger_dir(out_dir):
    return os.path.join(out_dir, "eco", "ref_ledger")


def ledger_files(out_dir):
    d = ledger_dir(out_dir)
    if not os.path.isdir(d):
        return None  # 目录未创建
    return os.listdir(d)


def read_ledger(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


SRC = "公开预告片 (官方发布渠道)"
AUTH = "授权声明: 仅限手法学习与结构参考, 禁止复制表达"


# ----------------------------------------------------------------
print("T0 接口契约 + eco 门面 refflow_register 端到端")
for name in ("register_ref", "deconstruct", "inject_refs", "anchor_lineage"):
    check(f"T0 ref_flow.{name} 可调用", callable(getattr(rf, name, None)))
check("T0 LEGALESE 为非空字符串", isinstance(rf.LEGALESE, str) and rf.LEGALESE.strip() != "")
check("T0 LEGALESE 含 '只学手法'", "只学手法" in rf.LEGALESE)
check("T0 LEGALESE 含 '不复制表达'", "不复制表达" in rf.LEGALESE)
check("T0 谱系 kind 常量为非空字符串",
      isinstance(rf.LINEAGE_KIND_REF_SOURCE, str) and rf.LINEAGE_KIND_REF_SOURCE.strip() != "")
from aggregator.eco import refflow_register  # 门面惰性导出 (禁改, 只消费)
check("T0 门面 refflow_register 可调用", callable(refflow_register))
out0 = temp_dir()
fr = refflow_register(out0, "F-1", "官方预告片", "授权仅限学习", "门面项目",
                      notes="手法：跳切\n随意一行", contract={"schema_version": "2.0"})
check("T0 门面合法登记 ok", fr.get("ok") is True, f"got={fr}")
check("T0 门面 deconstruct 三键齐备",
      isinstance(fr.get("deconstruct"), dict) and set(fr["deconstruct"]) == {"手法", "参考实现", "取舍"})
check("T0 门面 deconstruct 手法列命中", fr.get("deconstruct", {}).get("手法") == ["手法：跳切"])
check("T0 门面 contract 注入 refs", (fr.get("contract", {}).get("refs") or [{}])[0].get("ref_id") == "F-1")
check("T0 门面台账文件落盘", os.path.isfile(os.path.join(
    ledger_dir(out0), rf._safe_name("门面项目") + ".json")))
fv = refflow_register(temp_dir(), "F-2", None, None, "门面项目")
check("T0 门面负样本 ok=False", fv.get("ok") is False)
check("T0 门面负样本 errors 显式", bool(fv.get("errors")))

# ----------------------------------------------------------------
print("T1 授权边界负样本: 缺 source / 缺 authorization / 双缺 → 零落盘 (验收②)")
NEG_CASES = [
    ("缺 source(None)", None, AUTH),
    ("缺 source(空串)", "", AUTH),
    ("缺 source(纯空白)", "   \t ", AUTH),
    ("缺 authorization(None)", SRC, None),
    ("缺 authorization(空串)", SRC, ""),
    ("缺 authorization(纯空白)", SRC, " \n "),
    ("双缺(None/None)", None, None),
    ("双缺(空串/空串)", "", ""),
    ("双缺(空串/None)", "", None),
]
for label, s, a in NEG_CASES:
    out = temp_dir()
    r = rf.register_ref(out, "R-NEG", s, a, "项目A")
    files = ledger_files(out)
    check(f"T1 {label} ok=False", r.get("ok") is False, f"got={r}")
    check(f"T1 {label} errors 显式", isinstance(r.get("errors"), list) and len(r["errors"]) > 0)
    check(f"T1 {label} ref_ledger 零文件落盘", files is None or files == [], f"files={files}")

# ----------------------------------------------------------------
print("T2 合法登记: 台账存在 + JSON 回读 + LEGALESE 字段 + ref_id 幂等覆盖 (验收②)")
out2 = temp_dir()
r1 = rf.register_ref(out2, "R-001", SRC, AUTH, "测试项目")
check("T2 登记 ok=True", r1.get("ok") is True, f"got={r1}")
lp = r1.get("ledger_path", "")
check("T2 台账文件存在 <out>/eco/ref_ledger/<safe_project>.json",
      os.path.isfile(lp) and os.path.basename(os.path.dirname(lp)) == "ref_ledger",
      f"path={lp}")
check("T2 纯中文项目名无碰撞后缀", os.path.basename(lp) == "测试项目.json", f"got={os.path.basename(lp)}")
data = read_ledger(lp)
check("T2 台账 JSON 可回读为对象", isinstance(data, dict))
check("T2 ref_id 为键", "R-001" in data)
rec = data.get("R-001", {})
check("T2 条目含 LEGALESE 边界字段 (legal_boundary)", rec.get("legal_boundary") == rf.LEGALESE)
check("T2 条目 source/authorization 回读一致",
      rec.get("source") == SRC and rec.get("authorization") == AUTH)
check("T2 条目 project 回读一致", rec.get("project") == "测试项目")
r1b = rf.register_ref(out2, "R-001", "新的来源描述", AUTH, "测试项目")
check("T2 重复 ref_id 再登记 ok=True", r1b.get("ok") is True)
data2 = read_ledger(lp)
check("T2 幂等覆盖: 仍单条目", len(data2) == 1, f"n={len(data2)}")
check("T2 幂等覆盖: source 已更新", data2["R-001"]["source"] == "新的来源描述")
rf.register_ref(out2, "R-002", SRC, AUTH, "测试项目")
data3 = read_ledger(lp)
check("T2 不同 ref_id 各成条目", set(data3) == {"R-001", "R-002"})
rf.register_ref(out2, "R-003", SRC, AUTH, "另一个项目")
check("T2 分项目分文件", os.path.isfile(os.path.join(
    ledger_dir(out2), rf._safe_name("另一个项目") + ".json")))
check("T2 原项目台账不受新项目影响", set(read_ledger(lp)) == {"R-001", "R-002"})
lp_ascii = rf.register_ref(out2, "R-004", SRC, AUTH, "my proj")["ledger_path"]
check("T2 ASCII 项目名带 sha1 碰撞后缀",
      os.path.basename(lp_ascii) == rf._safe_name("my proj") + ".json"
      and os.path.basename(lp_ascii) != "my proj.json",
      f"got={os.path.basename(lp_ascii)}")
r_kw = rf.register_ref(out2, "R-005", SRC, AUTH, "测试项目",
                       手法=["匹配剪辑"], 谱系锚="asset_9")
check("T2 **kw 扩展字段透传进条目 (三列表/谱系锚)",
      read_ledger(lp).get("R-005", {}).get("手法") == ["匹配剪辑"]
      and read_ledger(lp)["R-005"].get("谱系锚") == "asset_9")
check("T2 kw 登记返回 ok", r_kw.get("ok") is True)
r_m = rf.register_ref(out2, "R-006", SRC, AUTH, "测试项目",
                      media_kwargs={"参考图": "D:/refs/x.png"},
                      media_img_key="参考图_IMAGE", media_path_key="参考图", media_tag="R-006")
check("T2 media 槽位经 resolve_ref 口径解析 (路径回退)",
      read_ledger(lp).get("R-006", {}).get("media_ref") == "D:/refs/x.png")
check("T2 media 控制键不透传进条目",
      "media_kwargs" not in read_ledger(lp).get("R-006", {}))

# ----------------------------------------------------------------
print("T3 三列表: 逐行归类 + 无法归类落取舍 + 空白丢弃 + 三列齐备逐条非空 (验收③)")
NOTES = (
    "手法：匹配剪辑转场衔接情绪\n"
    "Technique: 30 度轴线越轴规则\n"
    "参考实现：LUT 叠冷调 + 颗粒 8%\n"
    "做法：先铺底噪再进主旋律\n"
    "How to ramp: 速度坡道先缓后急\n"
    "取舍：放弃一镜到底, 改多机位覆盖\n"
    "tradeoff: 渲染时间换降噪质量\n"
    "放弃慢门实拍, 改固定机位\n"
    "这行没有归类关键词, 兜底落取舍\n"
    "\n"
    "   \n"
    "\t\n"
)
d1 = rf.deconstruct(NOTES)
check("T3 三键齐备且不多不少", set(d1) == {"手法", "参考实现", "取舍"})
check("T3 手法列 (含 手法/technique)", len(d1["手法"]) == 2, f"got={d1['手法']}")
check("T3 参考实现列 (含 实现/做法/how)", len(d1["参考实现"]) == 3, f"got={d1['参考实现']}")
check("T3 取舍列 (取舍/放弃/tradeoff + 兜底)", len(d1["取舍"]) == 4, f"got={d1['取舍']}")
check("T3 空白行丢弃 (总条数==非空行数 9)",
      sum(len(v) for v in d1.values()) == 9)
check("T3 逐条非空", all(isinstance(x, str) and x.strip() for v in d1.values() for x in v))
check("T3 中文关键词行原样保留", "手法：匹配剪辑转场衔接情绪" in d1["手法"])
d2 = rf.deconstruct(NOTES.splitlines())
check("T3 list[str] 输入与 str 逐字节一致", jd(d1) == jd(d2))
d3 = rf.deconstruct([])
check("T3 空输入三列齐备且为空", set(d3) == {"手法", "参考实现", "取舍"}
      and all(len(v) == 0 for v in d3.values()))
d4 = rf.deconstruct("   \n\t\n")
check("T3 纯空白输入三列齐备且为空", all(len(v) == 0 for v in d4.values())
      and set(d4) == {"手法", "参考实现", "取舍"})

# ----------------------------------------------------------------
print("T4 refs 注入零漂移: 既有键逐字节深比对 + 追加不去重 + 空列表不加键 (验收④)")
contract = {
    "schema_version": "2.0",
    "shots": [{"shot_id": "S01", "duration": 3.5}, {"shot_id": "S02", "duration": 2.0}],
    "slots": {"slot_a": {"camera": "推", "lens": "35mm"}},
}
before = jd(contract)
out = rf.inject_refs(contract, [{"ref_id": "R-001"}, {"ref_id": "R-002"}])
check("T4 refs 键新增", "refs" in out)
check("T4 refs 内容为注入条目 (不去重)",
      out["refs"] == [{"ref_id": "R-001"}, {"ref_id": "R-002"}])
check("T4 既有键逐字节不变 (深比对)",
      jd({k: out[k] for k in contract}) == before)
check("T4 键集恰为既有键 + refs", set(out) == set(contract) | {"refs"})
check("T4 输入 contract 未被改写 (无 refs 键, 全文逐字节)",
      "refs" not in contract and jd(contract) == before)
c2 = {"schema_version": "2.0", "refs": [{"ref_id": "A"}]}
c2_before = jd(c2)
out2_ = rf.inject_refs(c2, [{"ref_id": "B"}, {"ref_id": "A"}])
check("T4 既有 refs 键追加不去重 (3 条)",
      out2_["refs"] == [{"ref_id": "A"}, {"ref_id": "B"}, {"ref_id": "A"}])
check("T4 既有 refs 追加后其余键逐字节不变",
      jd({k: v for k, v in out2_.items() if k != "refs"})
      == jd({k: v for k, v in c2.items() if k != "refs"}))
check("T4 原 refs 列表对象不改写", c2["refs"] == [{"ref_id": "A"}] and jd(c2) == c2_before)
c3 = {"shots": []}
before3 = jd(c3)
out3 = rf.inject_refs(c3, [])
check("T4 空列表: 输出与输入逐字节相同", jd(out3) == before3)
check("T4 空列表: 不加键", "refs" not in out3 and set(out3) == set(c3))
c4 = {"refs": [{"ref_id": "A"}]}
before4 = jd(c4)
out4 = rf.inject_refs(c4, [])
check("T4 空列表 + 既有 refs: 逐字节零漂移", jd(out4) == before4 and out4["refs"] == [{"ref_id": "A"}])

# ----------------------------------------------------------------
print("T5 确定性: 同输入两次登记台账逐字节一致 + 重登记幂等 + 双跑一致")
outa, outb = temp_dir(), temp_dir()
pa = rf.register_ref(outa, "R-100", SRC, AUTH, "确定性项目")["ledger_path"]
pb = rf.register_ref(outb, "R-100", SRC, AUTH, "确定性项目")["ledger_path"]
with open(pa, "rb") as f:
    ba = f.read()
with open(pb, "rb") as f:
    bb = f.read()
check("T5 跨目录同输入台账逐字节一致", ba == bb)
with open(pa, "rb") as f:
    b0 = f.read()
rf.register_ref(outa, "R-100", SRC, AUTH, "确定性项目")
with open(pa, "rb") as f:
    b1 = f.read()
check("T5 同 out_dir 重登记内容幂等 (逐字节)", b0 == b1)
check("T5 deconstruct 双跑逐字节一致", jd(rf.deconstruct(NOTES)) == jd(rf.deconstruct(NOTES)))
ca, cb = {"schema_version": "2.0", "shots": [1]}, {"schema_version": "2.0", "shots": [1]}
check("T5 inject_refs 双跑逐字节一致",
      jd(rf.inject_refs(ca, [{"ref_id": "X"}])) == jd(rf.inject_refs(cb, [{"ref_id": "X"}])))

# ----------------------------------------------------------------
print("T6 谱系源登记 anchor_lineage: JSONL 追加 + ts 无时间戳 + 词汇对齐 + asset_id 回退")
lin = temp_dir()
e1 = {"ref_id": "R-001", "asset_id": "asset_9"}
r1 = rf.anchor_lineage(e1, lin)
check("T6 返回 ok=True", r1.get("ok") is True)
lpath = r1.get("lineage_path", "")
check("T6 JSONL 文件落盘", os.path.isfile(lpath))
with open(lpath, "r", encoding="utf-8") as f:
    rows1 = [json.loads(x) for x in f.read().splitlines() if x.strip()]
check("T6 追加恰一行", len(rows1) == 1)
row = rows1[0]
check("T6 行含 ref_id", row.get("ref_id") == "R-001")
check("T6 ts 不写时间戳 (恒 None)", row.get("ts", "missing") is None)
check("T6 lineage_kind 对齐 asset_master 词汇风格 (参考源)",
      row.get("lineage_kind") == rf.LINEAGE_KIND_REF_SOURCE)
check("T6 asset_id 取显式值", row.get("asset_id") == "asset_9")
r2 = rf.anchor_lineage({"ref_id": "R-002"}, lin)
with open(lpath, "r", encoding="utf-8") as f:
    rows2 = [json.loads(x) for x in f.read().splitlines() if x.strip()]
check("T6 追加两行", len(rows2) == 2)
check("T6 asset_id 缺失回退 ref_id", rows2[1].get("asset_id") == "R-002")
check("T6 全部行无时间戳", all(r.get("ts", "missing") is None for r in rows2))
lin2 = temp_dir()
rf.anchor_lineage(e1, lin2)
rf.anchor_lineage({"ref_id": "R-002"}, lin2)
with open(os.path.join(lin2, rf.LINEAGE_FILENAME), "rb") as f:
    bb2 = f.read()
with open(lpath, "rb") as f:
    bb1 = f.read()
check("T6 跨目录同输入逐字节一致", bb1 == bb2)

# ----------------------------------------------------------------
print("T7 LOW-1: 空 ref_id (None/空串/纯空白) → 中文 ValueError 拒绝 + 台账零落盘")
out7 = temp_dir()
for label, bad_id in (("None", None), ("空串", ""), ("纯空白", "   \t ")):
    caught = None
    try:
        rf.register_ref(out7, bad_id, SRC, AUTH, "项目T7")
    except ValueError as exc:
        caught = str(exc)
    except Exception as exc:  # noqa: BLE001 — 类型错也算失败, 记录类型名
        caught = "WRONG-TYPE:%s" % type(exc).__name__
    check(f"T7 {label} ref_id 被拒 (ValueError)",
          caught is not None and not caught.startswith("WRONG-TYPE"),
          f"got={caught!r}")
    check(f"T7 {label} ref_id 中文错误含 ref_id+必填",
          caught is not None and "ref_id" in caught and "必填" in caught,
          f"got={caught!r}")
files7 = ledger_files(out7)
check("T7 全部被拒后 ref_ledger 零文件落盘", files7 is None or files7 == [],
      f"files={files7}")

# ----------------------------------------------------------------
print("T8 LOW-3: inject_refs refs 类型校验 (str/元组/含非 dict 项) → 中文 ValueError + contract 零漂移")
contract8 = {"schema_version": "2.0", "shots": [1, 2], "slots": {"a": 1}}
snap8 = jd(contract8)
for label, bad_refs in (("str", "不是列表"), ("元组", ({"ref_id": "X"},)),
                        ("含非 dict 项", [{"ref_id": "X"}, "坏项"])):
    caught = None
    try:
        rf.inject_refs(contract8, bad_refs)
    except ValueError as exc:
        caught = str(exc)
    except Exception as exc:  # noqa: BLE001
        caught = "WRONG-TYPE:%s" % type(exc).__name__
    check(f"T8 refs={label} 被拒 (ValueError)",
          caught is not None and not caught.startswith("WRONG-TYPE"),
          f"got={caught!r}")
    if label == "含非 dict 项":
        check("T8 refs=含非 dict 项 中文错误含 dict+项定位",
              caught is not None and "dict" in caught and "项非 dict" in caught,
              f"got={caught!r}")
    else:
        check(f"T8 refs={label} 中文错误含 list/dict 口径",
              caught is not None and "list" in caught and "dict" in caught,
              f"got={caught!r}")
    check(f"T8 refs={label} 拒绝后 contract 逐字节零漂移", jd(contract8) == snap8)
ok8 = rf.inject_refs(contract8, [{"ref_id": "R-T8"}])
check("T8 合法 list[dict] 照常注入 (回归不破)", ok8.get("refs") == [{"ref_id": "R-T8"}])
check("T8 合法注入后既有键原样", ok8.get("shots") == [1, 2] and ok8.get("schema_version") == "2.0")

# ----------------------------------------------------------------
print("T9 MED-1 真并发: 双 subprocess 同时 register_ref 同一台账 → 20 条目零丢失")
_CHILD_RF_SRC = r'''
import json, os, sys, time
sys.path.insert(0, sys.argv[1])
from aggregator.eco import ref_flow as rf
out_dir, tag, barrier, n = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
while not os.path.exists(barrier):
    time.sleep(0.005)
SRC = "公开预告片 (官方发布渠道)"
AUTH = "授权声明: 仅限手法学习与结构参考, 禁止复制表达"
ok, exhausted = 0, 0
for i in range(n):
    rid = "%s-%d" % (tag, i)
    for _attempt in range(20):
        try:
            r = rf.register_ref(out_dir, rid, SRC, AUTH, "并发项目")
            if r.get("ok"):
                ok += 1
                break
        except RuntimeError as exc:
            if "并发写入冲突" in str(exc):
                continue
            raise
        except PermissionError:
            continue
    else:
        exhausted += 1
print(json.dumps({"tag": tag, "ok": ok, "exhausted": exhausted}))
'''
out9 = temp_dir()
child9_dir = temp_dir()
child9_path = os.path.join(child9_dir, "rf_concurrent_child.py")
with open(child9_path, "w", encoding="utf-8") as f:
    f.write(_CHILD_RF_SRC)
barrier9 = os.path.join(child9_dir, "go.barrier")
if os.path.exists(barrier9):
    os.remove(barrier9)
procs9 = []
for k in range(2):
    procs9.append(subprocess.Popen(
        [sys.executable, "-X", "utf8", child9_path, ROOT, out9, "子%s" % "AB"[k],
         barrier9, "10"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"))
time.sleep(0.4)
open(barrier9, "w").close()
reports9 = []
for p in procs9:
    out9_s, err9_s = p.communicate(timeout=120)
    check("T9 子进程正常退出 (退出码 0)", p.returncode == 0, f"err={err9_s[-300:]}")
    if p.returncode == 0:
        reports9.append(json.loads(out9_s.strip().splitlines()[-1]))
check("T9 子进程零冲突耗尽 (乐观重试全部收敛)",
      all(r.get("exhausted") == 0 for r in reports9), f"reports={reports9}")
ledger9 = os.path.join(ledger_dir(out9), rf._safe_name("并发项目") + ".json")
check("T9 台账 JSON 可回读 (解析无误)", os.path.isfile(ledger9))
data9 = read_ledger(ledger9) if os.path.isfile(ledger9) else {}
want9 = set("子%s-%d" % ("AB"[k], i) for k in range(2) for i in range(10))
check("T9 台账恰 20 条目 (双进程各 10 零丢失)", len(data9) == 20, f"n={len(data9)}")
check("T9 两子进程 ref_id 全在 (零覆盖)", set(data9) == want9,
      f"missing={sorted(want9 - set(data9))[:6]}")

# ----------------------------------------------------------------
print("T10 R2A-01 同进程多线程压测: 4 线程 × 5 次 register_ref 同一台账 → 20 条目全在")
out10 = temp_dir()


def _t10_worker(tag):
    """线程体: 串行登记 5 条 (同项目同台账, ref_id 各线程各异); 库内 3 轮乐观
    冲突 fail loud 后由线程级有界兜底重试 (与 T9 子进程重试同款语义, 耗尽计数
    绝不静默吞)。"""
    exhausted = 0
    for i in range(5):
        rid = "线%s-%d" % (tag, i)
        done = False
        for _attempt in range(20):
            try:
                if rf.register_ref(out10, rid, SRC, AUTH, "线程并发项目").get("ok"):
                    done = True
                    break
            except RuntimeError:
                continue  # 冲突/瞬时占用均属可重试: 有界兜底 (20 轮耗尽 → exhausted)
        if not done:
            exhausted += 1
    return exhausted


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool10:
    futs10 = [pool10.submit(_t10_worker, t) for t in ("甲", "乙", "丙", "丁")]
    exhaust10 = [f.result() for f in futs10]
check("T10 四线程零兜底耗尽 (乐观重试全部收敛)", all(x == 0 for x in exhaust10),
      f"exhausted={exhaust10}")
ledger10 = os.path.join(ledger_dir(out10), rf._safe_name("线程并发项目") + ".json")
check("T10 台账 JSON 文件落盘", os.path.isfile(ledger10))
data10, parse_err10 = {}, None
try:
    data10 = read_ledger(ledger10)
except Exception as exc:  # noqa: BLE001 — 撕裂/损坏记为断言失败 (不裸崩)
    parse_err10 = "%s: %s" % (type(exc).__name__, str(exc)[:160])
check("T10 台账 JSON 完整可解析 (无撕裂写)", parse_err10 is None, f"err={parse_err10}")
want10 = set("线%s-%d" % (t, i) for t in ("甲", "乙", "丙", "丁") for i in range(5))
check("T10 台账恰 20 条目 (4 线程 × 5 零丢失)", len(data10) == 20, f"n={len(data10)}")
check("T10 各线程 ref_id 全在 (零覆盖)", set(data10) == want10,
      f"missing={sorted(want10 - set(data10))[:6]}")
check("T10 逐条含 LEGALESE 授权边界字段 (并发写不丢法务边界)",
      all(data10[k].get("legal_boundary") == rf.LEGALESE for k in data10))

# ----------------------------------------------------------------
print()
print(f"=== test_eco_refflow: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
