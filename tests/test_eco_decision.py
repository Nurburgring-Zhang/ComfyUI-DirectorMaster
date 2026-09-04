# -*- coding: utf-8 -*-
"""
批次5 WaveB builder-p3 — decision_log append-only 决策审计轨 测试
(tests/test_eco_decision.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch5.md 验收口径⑤⑥⑦, builder-p3 部分):
  T0 接口契约 (四函数 + 条目钉死 8 键无时间戳 + options_considered None→[] + 非法类型 fail loud)
  T1 追加 3 条 → verify ok + replay 长度 3 + 创世 prev_hash/链序接龙/seq 连续 + 独立重算哈希一致 (验收⑤)
  T2 append-only: 每次追加后文件字节前缀逐字节一致 (纯追加, 不改写不删除) (验收⑤)
  T3 变更语义: 同 (category,subject) 再追加 → revised=true + 旧条目 decision 移入 options_considered + 旧条目保留不动 (验收⑥)
  T4 篡改负样本: 首/中/末条 decision 字段改写 → verify 三次全部 ok=False 且 errors 非空 (验收⑤)
  T5 损坏行 (非 JSON) / seq 断裂 (删中间行) 负样本 → verify ok=False (verify 行为面强化)
  T6 空文件/文件不存在 → (True, []) 空链合法; replay → []
  T7 跨文件确定性: 同链状态同输入 → 哈希逐字节一致 (无时间戳/随机/locale)
  T8 version_store 只读挂接: bridge dict 字段正确 + attach 前后 store 既有快照行为不变 (验收⑦)
  T9 聚合门面 decision_attach 端到端 (追加→verify→挂接, eco/__init__ 惰性导出冒烟)
  T10 MED-2 哈希覆盖缺口修复: 篡改历史条目 revised / 注入未知字段 → verify_log FAIL
  T11 LOW-2 空 category/subject/decision 各自被拒 (中文 ValueError) + 零落盘
  T12 MED-1 真并发 (subprocess 双子进程同时追加) → 零丢条目 + 全链 verify PASS
  T13 MED-3 门面 decision_attach 带 store+snapshot_name → dm_versions_bridge.json 真实落盘可读
  T14 R2A-01 同进程多线程压测 (ThreadPoolExecutor 4 线程 × 5 次追加同一 JSONL)
      → 20 条零丢失 + JSONL 逐行完整可解析 (无撕裂写) + 全链 verify PASS
纪律: 测试产物一律 tempfile, 零仓库内写入, 零网络零 LLM, 互斥锁零使用。
退出码: 0 = 无 FAIL。运行: python -X utf8 tests/test_eco_decision.py
"""
import concurrent.futures
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aggregator.eco import decision_log as dl

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
    d = tempfile.mkdtemp(prefix="eco_decision_test_")
    TEMP_DIRS.append(d)
    return d


def expected_hash(prev_hash, entry):
    """独立重算 (不 import 被测私有 helper): 验证写入配方与钉板配方一致。
    MED-2 冻结配方: payload 覆盖除 seq/prev_hash/hash 三字段外的全部业务内容
    (含 revised 与任何未知/未来新增字段)。"""
    payload = json.dumps(
        {k: v for k, v in entry.items() if k not in ("seq", "prev_hash", "hash")},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()


def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()


def tamper_line(log_path, line_index, field="decision", value="被篡改的决策"):
    """读文件改指定行 (1 行内 json 重写, 同序列化配方) 后整体重写 — 模拟篡改。"""
    lines = read_bytes(log_path).decode("utf-8").split("\n")
    obj = json.loads(lines[line_index])
    obj[field] = value
    lines[line_index] = json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with open(log_path, "wb") as f:
        f.write("\n".join(lines).encode("utf-8"))


ENTRY_KEYS = sorted(["seq", "prev_hash", "hash", "category", "subject",
                     "decision", "options_considered", "revised"])


# ----------------------------------------------------------------
print("T0 接口契约: 四函数 + 条目 8 键 + options_considered 归一")
for fn in ("append_entry", "verify_log", "replay", "attach_to_version"):
    check(f"T0 {fn} 可导入", callable(getattr(dl, fn, None)))

d0 = temp_dir()
p0 = os.path.join(d0, "eco", "decision_log.jsonl")
e0 = dl.append_entry(p0, "分镜", "镜号口径", "以秒表数计", options_considered=None)
check("T0 条目字段恰为钉死 8 键 (无时间戳/无不确定字段)",
      sorted(e0.keys()) == ENTRY_KEYS, f"实际 {sorted(e0.keys())}")
check("T0 options_considered=None → []", e0["options_considered"] == [])
check("T0 首条 revised=False", e0["revised"] is False)
check("T0 创世条 prev_hash='0'*64", e0["prev_hash"] == "0" * 64)
try:
    dl.append_entry(os.path.join(d0, "x.jsonl"), "c", "s", "d",
                    options_considered="不是列表")
    check("T0 options_considered 非列表 fail loud", False, "未抛 ValueError")
except ValueError:
    check("T0 options_considered 非列表 fail loud", True)

# ----------------------------------------------------------------
print("T1 追加 3 条 → verify ok + replay 长度 3 + 链序/seq 断言 (验收⑤)")
d1 = temp_dir()
p1 = os.path.join(d1, "decision_log.jsonl")
inputs = [
    ("架构", "存储布局", "eco 目录三段式", ["平铺单文件", "sqlite"]),
    ("分镜", "镜号口径", "以秒表数计", None),
    ("合规", "授权边界", "authorization/source 必填", ["口头约定"]),
]
for cat, sub, dec, opts in inputs:
    dl.append_entry(p1, cat, sub, dec, options_considered=opts)
ok, errors = dl.verify_log(p1)
check("T1 verify_log ok", ok is True, f"errors={errors}")
check("T1 verify_log errors 空", errors == [])
replayed = dl.replay(p1)
check("T1 replay 长度 3", len(replayed) == 3, f"实际 {len(replayed)}")
check("T1 seq 连续 1..3", [e["seq"] for e in replayed] == [1, 2, 3])
check("T1 创世 prev_hash", replayed[0]["prev_hash"] == "0" * 64)
check("T1 prev_hash 接龙",
      all(replayed[i]["prev_hash"] == replayed[i - 1]["hash"] for i in (1, 2)))
check("T1 逐条独立重算哈希一致",
      all(e["hash"] == expected_hash(e["prev_hash"], e)
          for e in replayed))
check("T1 条目字段恰 8 键", all(sorted(e.keys()) == ENTRY_KEYS for e in replayed))

# ----------------------------------------------------------------
print("T2 append-only: 追加前后文件字节前缀逐字节一致")
d2 = temp_dir()
p2 = os.path.join(d2, "decision_log.jsonl")
dl.append_entry(p2, "A", "甲", "决策一")
prev_bytes = read_bytes(p2)
dl.append_entry(p2, "B", "乙", "决策二")
mid_bytes = read_bytes(p2)
check("T2 第一次追加后前缀一致",
      mid_bytes[:len(prev_bytes)] == prev_bytes and len(mid_bytes) > len(prev_bytes))
dl.append_entry(p2, "C", "丙", "决策三")
final_bytes = read_bytes(p2)
check("T2 第二次追加后前缀一致",
      final_bytes[:len(mid_bytes)] == mid_bytes and len(final_bytes) > len(mid_bytes))
check("T2 新内容为纯追加 (旧 3 行原样)",
      final_bytes.decode("utf-8").count("\n") == 3)

# ----------------------------------------------------------------
print("T3 变更语义: 同 (category,subject) → revised + 旧条目保留 (验收⑥)")
d3 = temp_dir()
p3 = os.path.join(d3, "decision_log.jsonl")
r1 = dl.append_entry(p3, "架构", "缓存策略", "LRU 512")
r2 = dl.append_entry(p3, "架构", "缓存策略", "LRU 1024")
r3 = dl.append_entry(p3, "架构", "缓存策略", "LFU 256", options_considered=["备选X"])
check("T3 首条 revised=False", r1["revised"] is False)
check("T3 二次追加 revised=True", r2["revised"] is True)
check("T3 旧条目 decision 移入 options_considered",
      r2["options_considered"] == ["LRU 512"], f"实际 {r2['options_considered']}")
check("T3 三次追加 revised=True + 最近旧决策在前 + 调用方备选在后",
      r3["revised"] is True and r3["options_considered"] == ["LRU 1024", "备选X"],
      f"实际 {r3['options_considered']}")
chain = dl.replay(p3)
check("T3 旧条目 decision 保留不动 (append-only)",
      [e["decision"] for e in chain] == ["LRU 512", "LRU 1024", "LFU 256"])
ok3, err3 = dl.verify_log(p3)
check("T3 变更链 verify ok", ok3 is True, f"errors={err3}")

# ----------------------------------------------------------------
print("T4 篡改负样本: 首/中/末条 decision 改写 → verify 三次全拦截 (验收⑤)")
d4 = temp_dir()
src = os.path.join(d4, "clean.jsonl")
for i in range(3):
    dl.append_entry(src, "cat%d" % i, "sub%d" % i, "原决策%d" % i)
check("T4 篡改前基准 verify ok", dl.verify_log(src)[0] is True)
for label, idx in (("首条", 0), ("中间条", 1), ("末条", 2)):
    tgt = os.path.join(d4, "tampered_%d.jsonl" % idx)
    shutil.copyfile(src, tgt)
    before = dl.verify_log(tgt)
    tamper_line(tgt, idx, field="decision", value="被篡改的决策")
    after = dl.verify_log(tgt)
    check(f"T4 篡改{label}前 ok=True", before == (True, []))
    check(f"T4 篡改{label}后 ok=False", after[0] is False, f"实际 {after[0]}")
    check(f"T4 篡改{label}后 errors 非空", len(after[1]) > 0, "errors 为空")
    check(f"T4 篡改{label}后报哈希不符且定位第 {idx + 1} 行",
          any("哈希不符" in m and ("第 %d 行" % (idx + 1)) in m for m in after[1]),
          f"errors={after[1]}")

# ----------------------------------------------------------------
print("T5 损坏行/seq 断裂负样本 (verify 行为面强化)")
d5 = temp_dir()
p5 = os.path.join(d5, "broken.jsonl")
for i in range(3):
    dl.append_entry(p5, "c%d" % i, "s%d" % i, "决策%d" % i)
raw5 = read_bytes(p5).decode("utf-8")
lines5 = raw5.split("\n")
with open(os.path.join(d5, "nonjson.jsonl"), "wb") as f:
    f.write(("\n".join([lines5[0], "这不是{合法JSON", lines5[2], ""]).encode("utf-8")))
ok5a, err5a = dl.verify_log(os.path.join(d5, "nonjson.jsonl"))
check("T5 非 JSON 行 → ok=False + errors 定位行号",
      ok5a is False and len(err5a) > 0 and "第 2 行" in err5a[0], f"{ok5a} {err5a}")
with open(os.path.join(d5, "gap.jsonl"), "wb") as f:
    f.write(("\n".join([lines5[0], lines5[2], ""])).encode("utf-8"))
ok5b, err5b = dl.verify_log(os.path.join(d5, "gap.jsonl"))
check("T5 删中间行 → seq 断裂 ok=False",
      ok5b is False and any("seq 断裂" in m for m in err5b), f"{ok5b} {err5b}")

# ----------------------------------------------------------------
print("T6 空文件/不存在 → (True, []) 空链合法")
d6 = temp_dir()
missing = os.path.join(d6, "nope.jsonl")
check("T6 文件不存在 verify (True, [])", dl.verify_log(missing) == (True, []))
empty = os.path.join(d6, "empty.jsonl")
with open(empty, "wb"):
    pass
check("T6 空文件 verify (True, [])", dl.verify_log(empty) == (True, []))
check("T6 不存在 replay → []", dl.replay(missing) == [])
check("T6 空文件 replay → []", dl.replay(empty) == [])

# ----------------------------------------------------------------
print("T7 跨文件确定性: 同链状态同输入 → 哈希逐字节一致 (无时间戳/随机)")
pa = os.path.join(temp_dir(), "a.jsonl")
pb = os.path.join(temp_dir(), "b.jsonl")
ea1 = dl.append_entry(pa, "同一类别", "同一主题", "同一决策", options_considered=["同备选"])
eb1 = dl.append_entry(pb, "同一类别", "同一主题", "同一决策", options_considered=["同备选"])
check("T7 同输入同链状态 hash 一致", ea1["hash"] == eb1["hash"],
      f"{ea1['hash']} vs {eb1['hash']}")
check("T7 hash 为 64 位十六进制",
      len(ea1["hash"]) == 64 and all(c in "0123456789abcdef" for c in ea1["hash"]))
ea2 = dl.append_entry(pa, "同一类别", "同一主题", "改判决策")
eb2 = dl.append_entry(pb, "同一类别", "同一主题", "改判决策")
check("T7 变更条 hash 亦一致 (revised 链确定性)", ea2["hash"] == eb2["hash"])

# ----------------------------------------------------------------
print("T8 version_store 只读挂接: bridge 字段正确 + store 行为不变 (验收⑦)")
from aggregator.version_store import open_store

d8 = temp_dir()
p8 = os.path.join(d8, "eco", "decision_log.jsonl")
for i in range(2):
    dl.append_entry(p8, "挂接类别%d" % i, "挂接主题%d" % i, "挂接决策%d" % i)
store = open_store(d8, "挂接测试项目")
vid = store.commit("版本一", {"剧本": ("script.txt", "剧情内容甲")})
before_log = store.log(20)
before_head = store.data.get("head")
before_versions = json.dumps(store.data.get("versions"), sort_keys=True,
                             ensure_ascii=False)
before_blobs = json.dumps(store.data.get("blobs"), sort_keys=True,
                          ensure_ascii=False)
before_summary = store.summary()

bridge = dl.attach_to_version(store, "head", p8)
check("T8 bridge dict 字段正确",
      bridge == {"snapshot": "head", "log_ref": p8, "entries": 2},
      f"实际 {bridge}")
check("T8 head 指向未变", store.data.get("head") == before_head == vid)
check("T8 store.log 不变", store.log(20) == before_log)
check("T8 store.versions 数据不变",
      json.dumps(store.data.get("versions"), sort_keys=True,
                 ensure_ascii=False) == before_versions)
check("T8 store.blobs 数据不变",
      json.dumps(store.data.get("blobs"), sort_keys=True,
                 ensure_ascii=False) == before_blobs)
check("T8 store.summary 不变", store.summary() == before_summary)
bridge2 = dl.attach_to_version(store, vid, p8)
check("T8 以 version_id 挂接同样成立", bridge2["snapshot"] == vid
      and bridge2["entries"] == 2)
bp = os.path.join(d8, "eco", "dm_versions_bridge.json")
bridge3 = dl.attach_to_version(store, "head", p8, bridge_path=bp)
with open(bp, "r", encoding="utf-8") as f:
    on_disk = json.load(f)
check("T8 bridge_path 落盘回读一致", on_disk == bridge3)
try:
    dl.attach_to_version(store, "不存在的快照", p8)
    check("T8 快照不存在 fail loud", False, "未抛 ValueError")
except ValueError:
    check("T8 快照不存在 fail loud", True)

# ----------------------------------------------------------------
print("T9 聚合门面 decision_attach 端到端 (惰性导出冒烟)")
from aggregator.eco import decision_attach

d9 = temp_dir()
r9a = decision_attach(d9, "端到端", "口径A", "决定A", options_considered=["备选1"])
check("T9 门面首轮 ok", r9a.get("ok") is True, f"实际 {r9a}")
check("T9 门面 log_path 落 eco 布局",
      r9a.get("log_path", "").replace("\\", "/").endswith("eco/decision_log.jsonl"))
r9b = decision_attach(d9, "端到端", "口径A", "决定B")
check("T9 门面二轮 revised 语义", r9b.get("ok") is True
      and r9b.get("entry", {}).get("revised") is True)
store9 = open_store(d9, "端到端项目")
store9.commit("v9", {"手册": ("m.txt", "内容")})
r9c = decision_attach(d9, "端到端", "口径A", "决定C",
                      store=store9, snapshot_name="head")
check("T9 门面挂接段返回 bridge", isinstance(r9c.get("bridge"), dict)
      and r9c["bridge"]["snapshot"] == "head"
      and r9c["bridge"]["entries"] == 3, f"实际 {r9c.get('bridge')}")

# ----------------------------------------------------------------
print("T10 MED-2 哈希覆盖缺口修复: 篡改 revised / 注入未知字段 → verify FAIL (链不可伪造)")
d10 = temp_dir()
p10 = os.path.join(d10, "decision_log.jsonl")
for i in range(2):
    dl.append_entry(p10, "med2类别%d" % i, "med2主题%d" % i, "med2决策%d" % i)
check("T10 篡改前基准 verify ok", dl.verify_log(p10) == (True, []))
# 10a 篡改历史条目 revised 字段 → FAIL
t_rev = os.path.join(d10, "tamper_revised.jsonl")
shutil.copyfile(p10, t_rev)
tamper_line(t_rev, 0, field="revised", value=True)
ok_rev, err_rev = dl.verify_log(t_rev)
check("T10 篡改 revised → ok=False", ok_rev is False, f"实际 {ok_rev}")
check("T10 篡改 revised → errors 非空且定位第 1 行哈希不符",
      len(err_rev) > 0 and any("哈希不符" in m and "第 1 行" in m for m in err_rev),
      f"errors={err_rev}")
# 10b 历史条目注入未知字段 → FAIL
t_unk = os.path.join(d10, "inject_unknown.jsonl")
shutil.copyfile(p10, t_unk)
lines_unk = read_bytes(t_unk).decode("utf-8").split("\n")
obj_unk = json.loads(lines_unk[1])
obj_unk["未来新增字段"] = "注入值"
lines_unk[1] = json.dumps(obj_unk, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
with open(t_unk, "wb") as f:
    f.write("\n".join(lines_unk).encode("utf-8"))
ok_unk, err_unk = dl.verify_log(t_unk)
check("T10 注入未知字段 → ok=False", ok_unk is False, f"实际 {ok_unk}")
check("T10 注入未知字段 → errors 定位第 2 行哈希不符",
      len(err_unk) > 0 and any("哈希不符" in m and "第 2 行" in m for m in err_unk),
      f"errors={err_unk}")

# ----------------------------------------------------------------
print("T11 LOW-2: 空 category/subject/decision 各自被拒 (中文 ValueError)")
p11 = os.path.join(temp_dir(), "low2.jsonl")
for label, args, field in (
    ("空 category", ("   ", "主题", "决策"), "category"),
    ("空 subject", ("类别", "", "决策"), "subject"),
    ("空 decision", ("类别", "主题", " \t "), "decision"),
    ("None decision", ("类别", "主题", None), "decision"),
):
    try:
        dl.append_entry(p11, *args)
        check(f"T11 {label} 拒绝 (ValueError)", False, "未抛异常")
    except ValueError as exc:
        check(f"T11 {label} 拒绝 (ValueError)", True)
        check(f"T11 {label} 中文错误含字段名+必填",
              field in str(exc) and "必填" in str(exc), f"msg={exc}")
check("T11 全部被拒后日志零落盘 (空链合法)", dl.verify_log(p11) == (True, []))

# ----------------------------------------------------------------
print("T12 MED-1 真并发: 双 subprocess 同时追加同一 JSONL → 零丢条目 + verify PASS")
_CHILD_DL_SRC = '''# -*- coding: utf-8 -*-
import json, os, sys, time
ROOT, LOG, TAG, BARRIER, N = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
sys.path.insert(0, ROOT)
from aggregator.eco import decision_log as dl
deadline = time.time() + 60
while not os.path.exists(BARRIER):  # 屏障: 父进程写文件后双子进程同时开写
    if time.time() > deadline:
        sys.exit(3)
    time.sleep(0.005)
exhausted = 0
for i in range(N):
    done = False
    for _attempt in range(20):  # 子进程级重试 (库内 3 轮冲突 fail loud 后的兜底)
        try:
            dl.append_entry(LOG, "并发类别", "子%s条目%d" % (TAG, i),
                            "决策内容%s-%d" % (TAG, i))
            done = True
            break
        except RuntimeError as exc:
            if "并发写入冲突" not in str(exc):
                exhausted += 1
                break
    if not done:
        exhausted += 1
print(json.dumps({"tag": TAG, "conflict_exhausted": exhausted}))
sys.exit(0 if exhausted == 0 else 4)
'''
d12 = temp_dir()
p12 = os.path.join(d12, "eco", "decision_log.jsonl")
barrier12 = os.path.join(d12, "go.barrier")
child12 = os.path.join(d12, "eco_decision_child.py")
with open(child12, "w", encoding="utf-8") as f:
    f.write(_CHILD_DL_SRC)
procs12 = [subprocess.Popen(
    [sys.executable, "-X", "utf8", child12, ROOT, p12, tag, barrier12, "10"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=tempfile.gettempdir()) for tag in ("A", "B")]
with open(barrier12, "w", encoding="utf-8") as f:
    f.write("go")
outs12 = []
for pr in procs12:
    so, se = pr.communicate(timeout=180)
    outs12.append((pr.returncode, so.decode("utf-8", "replace"),
                   se.decode("utf-8", "replace")))
check("T12 双子进程正常退出 (退出码 0, 无永久 fail-loud)",
      all(rc == 0 for rc, _, _ in outs12),
      f"rets={[o[0] for o in outs12]} stderr={[o[2][-160:] for o in outs12]}")
check("T12 子进程零冲突耗尽 (乐观重试全部收敛)",
      all(json.loads(o[1].strip().splitlines()[-1])["conflict_exhausted"] == 0
          for o in outs12 if o[1].strip()),
      f"outs={[o[1][-160:] for o in outs12]}")
entries12 = dl.replay(p12)
check("T12 台账恰 20 条 (双进程各 10 条零丢失)",
      len(entries12) == 20, f"n={len(entries12)}")
tags12 = [e["subject"][:2] for e in entries12]
check("T12 子A/子B 条目各 10 (两进程条目全在)",
      tags12.count("子A") == 10 and tags12.count("子B") == 10,
      f"tags={ {t: tags12.count(t) for t in set(tags12)} }")
ok12, err12 = dl.verify_log(p12)
check("T12 并发后全链 verify PASS", ok12 is True and err12 == [], f"errors={err12}")

# ----------------------------------------------------------------
print("T13 MED-3 门面 decision_attach 桥文件真实落盘 (dm_versions_bridge.json)")
d13 = temp_dir()
store13 = open_store(d13, "桥文件项目")
store13.commit("v13", {"锚": ("a.txt", "内容甲")})
r13 = decision_attach(d13, "桥接", "快照桥", "决定桥",
                      store=store13, snapshot_name="head")
check("T13 门面挂接 ok", r13.get("ok") is True, f"got={r13}")
bp13 = os.path.join(d13, "eco", "dm_versions_bridge.json")
check("T13 dm_versions_bridge.json 真实落盘 <out>/eco/", os.path.isfile(bp13),
      f"bridge={r13.get('bridge')}")
try:
    with open(bp13, "r", encoding="utf-8") as f:
        disk13 = json.load(f)
    check("T13 桥文件内容可读且与返回 bridge 一致",
          disk13 == r13.get("bridge") and disk13.get("snapshot") == "head",
          f"disk={disk13}")
    check("T13 桥文件 entries 与链长一致", disk13.get("entries") == 1,
          f"entries={disk13.get('entries')}")
except Exception as e:
    check("T13 桥文件读取", False, "%s: %s" % (type(e).__name__, str(e)[:200]))

# ----------------------------------------------------------------
print("T14 R2A-01 同进程多线程压测: 4 线程 × 5 次追加同一 JSONL → 20 条全在 + verify PASS")
d14 = temp_dir()
p14 = os.path.join(d14, "eco", "decision_log.jsonl")


def _t14_worker(tag):
    """线程体: 串行追加 5 条 (subject 各线程各异, 不触发 revised 语义); 库内
    3 轮乐观冲突 fail loud 后由线程级有界兜底重试 (与 T12 子进程重试同款语义,
    耗尽计数绝不静默吞)。"""
    exhausted = 0
    for i in range(5):
        done = False
        for _attempt in range(20):
            try:
                dl.append_entry(p14, "线程并发", "线%s条目%d" % (tag, i),
                                "线程决策%s-%d" % (tag, i))
                done = True
                break
            except RuntimeError:
                continue  # 冲突/瞬时占用均属可重试: 有界兜底 (20 轮耗尽 → exhausted)
        if not done:
            exhausted += 1
    return exhausted


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool14:
    futs14 = [pool14.submit(_t14_worker, t) for t in ("甲", "乙", "丙", "丁")]
    exhaust14 = [f.result() for f in futs14]
check("T14 四线程零兜底耗尽 (乐观重试全部收敛)", all(x == 0 for x in exhaust14),
      f"exhausted={exhaust14}")
entries14 = dl.replay(p14)
check("T14 台账恰 20 条 (4 线程 × 5 零丢失)", len(entries14) == 20, f"n={len(entries14)}")
count14 = {t: sum(1 for e in entries14 if e.get("subject", "").startswith("线%s条目" % t))
           for t in ("甲", "乙", "丙", "丁")}
check("T14 各线程条目全在 (每线程恰 5, 零覆盖)", all(v == 5 for v in count14.values()),
      f"计数={count14}")
ok14, err14 = dl.verify_log(p14)
check("T14 并发后全链 verify PASS", ok14 is True and err14 == [], f"errors={err14}")
with open(p14, "rb") as f:
    raw14 = f.read()
lines14 = [x for x in raw14.decode("utf-8").split("\n") if x.strip()]
parse_ok14, parsed14 = True, []
for x in lines14:
    try:
        parsed14.append(json.loads(x))
    except ValueError:
        parse_ok14 = False
check("T14 JSONL 逐行完整可解析 (无撕裂写)",
      parse_ok14 and len(parsed14) == 20, f"n={len(parsed14)} parse_ok={parse_ok14}")

# ----------------------------------------------------------------
print()
print(f"=== test_eco_decision: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
