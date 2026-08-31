# -*- coding: utf-8 -*-
"""
V16.7-MERGED D4 测试 — 产物检查点 CheckpointStore (断点续跑/失效重算/线程安全)
================================================================
不依赖 pytest:  python -X utf8 tests/test_pipeline_checkpoint.py
覆盖 (design_batch3.md §4 D4 验收):
  1. done/mark_done/clear 接口冻结签名行为 (存在且 hash 相同=跳过, hash 变化=失效)
  2. 中断恢复实测: 跑两步 → 模拟清空内存重入 → 已完成步跳过/未完成步重算/hash 变更步重算/clear 后全重算
  3. 清单落盘确定性 (无时间戳字段, 同状态逐字节一致) + 持久化跨实例
  4. 路径消毒白名单 (穿越/分隔符/空值 ValueError, 中文名可用)
  5. 线程安全 (8 线程并发 mark_done/done 零丢失)
  6. artifact_ref 往返 + step_done 别名 + steps() 快照
退出码: 0 = 全部通过, 1 = 有失败
"""
import os
import sys
import json
import shutil
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0
ERRORS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        ERRORS.append("%s %s" % (label, detail))
        print("  [FAIL] %s %s" % (label, detail))


from aggregator.pipeline_checkpoint import CheckpointStore  # noqa: E402


def test_basic_and_persistence(root):
    pid = "断点续跑管线"
    s1 = CheckpointStore(root)
    check("初始done未知步为False", s1.done(pid, "step1", "h1") is False)
    check("mark_done返回None", s1.mark_done(pid, "step1", "h1", artifact_ref="r1.json") is None)
    check("hash相同done为True", s1.done(pid, "step1", "h1") is True)
    # 跨实例持久化 (模拟清空内存重入)
    s2 = CheckpointStore(root)
    check("重入后done仍True(持久化)", s2.done(pid, "step1", "h1") is True)
    check("重入后hash不同done为False", s2.done(pid, "step1", "h1-NEW") is False)
    snap = s2.steps(pid)
    check("steps快照含artifact_ref",
          snap.get("step1", {}).get("artifact_ref") == "r1.json"
          and snap.get("step1", {}).get("input_hash") == "h1")
    # 覆盖旧记录 (hash 失效 → mark_done 重算后生效)
    s2.mark_done(pid, "step1", "h1-NEW", artifact_ref="r1b.json")
    check("hash变更重算后done为True", s2.done(pid, "step1", "h1-NEW") is True)
    check("旧hash失效", s2.done(pid, "step1", "h1") is False)
    check("artifact_ref已覆盖", s2.steps(pid)["step1"]["artifact_ref"] == "r1b.json")
    # hash 不匹配时旧记录保留至覆盖 (done 只读); artifact_ref 可清回 None
    s2.mark_done(pid, "step1", "h1-NEW2")
    check("artifact_ref可清回None", s2.steps(pid)["step1"]["artifact_ref"] is None)
    # step_done 别名与 done 行为一致
    check("step_done别名一致", s2.step_done(pid, "step1", "h1-NEW2") is True
          and s2.step_done(pid, "step1", "X") is False)
    # clear
    s2.mark_done(pid, "step2", "h2")
    n = s2.clear(pid)
    check("clear返回清除步数", n == 2)
    check("clear后全重算", s2.done(pid, "step1", "h1-NEW2") is False
          and s2.done(pid, "step2", "h2") is False)
    check("clear后清单文件已删", not os.path.isfile(s2.manifest_path(pid)))
    check("clear不存在管线返回0", s2.clear("不存在管线X") == 0)
    # 管线隔离
    s2.mark_done("管线A", "s", "hA")
    check("管线B不受A影响", CheckpointStore(root).done("管线B", "s", "hA") is False)
    check("管线A自身仍True", s2.done("管线A", "s", "hA") is True)


def test_interrupt_recovery(root):
    """中断恢复实测 (design §4 验收原文): 跑两步 → 清空内存重入 → 跳过/重算/clear."""
    pid = "中断恢复实测"
    s1 = CheckpointStore(root)
    s1.mark_done(pid, "完整性审查", "hashA1")
    s1.mark_done(pid, "一致性审查", "hashA2")
    # —— 模拟进程崩溃: 全新实例 (内存为空, 仅磁盘) ——
    s2 = CheckpointStore(root)
    check("中断恢复:已完成步1跳过", s2.done(pid, "完整性审查", "hashA1") is True)
    check("中断恢复:已完成步2跳过", s2.done(pid, "一致性审查", "hashA2") is True)
    check("中断恢复:未完成步重算", s2.done(pid, "覆盖审查", "hashA3") is False)
    s2.mark_done(pid, "覆盖审查", "hashA3", artifact_ref="review_r3.json")
    check("中断恢复:补跑后跳过", s2.done(pid, "覆盖审查", "hashA3") is True)
    # 输入 hash 变更 → 该步失效重算
    check("hash变更步失效", s2.done(pid, "完整性审查", "hashA1-变更") is False)
    s2.mark_done(pid, "完整性审查", "hashA1-变更")
    check("hash变更步重算后生效", s2.done(pid, "完整性审查", "hashA1-变更") is True)
    # clear → 全部重算
    n = s2.clear(pid)
    check("clear步数=3", n == 3)
    check("clear后步1重算", s2.done(pid, "完整性审查", "hashA1-变更") is False)
    check("clear后步2重算", s2.done(pid, "一致性审查", "hashA2") is False)
    check("clear后步3重算", s2.done(pid, "覆盖审查", "hashA3") is False)


def test_manifest_determinism(root1, root2):
    """清单确定性: 无时间戳字段; 两个独立 store 同操作序列 → 逐字节一致."""
    for root in (root1, root2):
        s = CheckpointStore(root)
        s.mark_done("确定性管线", "步骤乙", "hash2", artifact_ref="b.json")
        s.mark_done("确定性管线", "步骤甲", "hash1", artifact_ref="a.json")
    p1 = CheckpointStore(root1).manifest_path("确定性管线")
    p2 = CheckpointStore(root2).manifest_path("确定性管线")
    raw1 = open(p1, encoding="utf-8").read()
    raw2 = open(p2, encoding="utf-8").read()
    check("清单逐字节一致", raw1 == raw2)
    data = json.loads(raw1)
    check("清单固定字段无时间戳",
          set(data.keys()) == {"schema", "pipeline_id", "steps"}
          and set(data["steps"]["步骤甲"].keys()) == {"input_hash", "artifact_ref"})
    check("清单无时间戳键名", "时间" not in raw1 and "timestamp" not in raw1
          and "time" not in raw1.lower())
    k_first, k_second = sorted(data["steps"].keys())  # sort_keys 按 Unicode 码点序
    check("steps按sort_keys排序",
          raw1.index('"%s"' % k_first) < raw1.index('"%s"' % k_second)
          and list(data["steps"].keys()) == sorted(data["steps"].keys()))


def test_path_sanitization(root):
    s = CheckpointStore(root)
    bad = [("a/b", "分隔符"), ("..\\x", "反斜杠"), ("..", "双点"),
           ("a:b", "盘符"), ('a"b', "保留字符")]
    # 控制字符单独构造 (源码内不直写 \x00)
    for val, tag in bad:
        try:
            s.done(val, "s", "h")
            check("消毒拒绝-%s" % tag, False, "(未抛错)")
        except ValueError:
            check("消毒拒绝-%s" % tag, True)
    try:
        s.done("pi\x00d", "s", "h")
        check("消毒拒绝-控制字符", False, "(未抛错)")
    except ValueError:
        check("消毒拒绝-控制字符", True)
    for args, tag in [((None, "s", "h"), "None"), ((123, "s", "h"), "非str"),
                      (("  ", "s", "h"), "空白"), (("p", "", "h"), "step空"),
                      (("p", "s", ""), "hash空")]:
        try:
            s.done(*args)
            check("消毒拒绝-%s" % tag, False, "(未抛错)")
        except ValueError:
            check("消毒拒绝-%s" % tag, True)
    try:
        s.mark_done("p", "s", "h", artifact_ref=123)
        check("消毒拒绝-artifact_ref非str", False, "(未抛错)")
    except ValueError:
        check("消毒拒绝-artifact_ref非str", True)
    # 中文名可用且文件名安全
    s.mark_done("我的电影项目二次修订", "步骤", "h")
    mp = s.manifest_path("我的电影项目二次修订")
    check("中文管线可落盘", os.path.isfile(mp))
    check("文件名仅安全字符", all(
        ("0" <= c <= "9") or ("A" <= c <= "Z") or ("a" <= c <= "z") or c in "_x" or c == "-" or c == "."
        for c in os.path.basename(mp)))
    # Windows 保留名转义
    s.mark_done("CON", "s", "h")
    check("Windows保留名加前缀", os.path.basename(s.manifest_path("CON")).startswith("p_CON"))
    # 超长 id → 截断+hash 后缀, 仍可用
    long_pid = "超长" * 100
    s.mark_done(long_pid, "s", "h")
    check("超长管线可落盘", os.path.isfile(s.manifest_path(long_pid))
          and len(os.path.basename(s.manifest_path(long_pid))) <= 120 + len(".checkpoint.json"))


def test_thread_safety(root):
    pid = "并发管线"
    s = CheckpointStore(root)
    errs = []

    def worker(ti):
        try:
            for ci in range(3):
                s.mark_done(pid, "步骤%d-%d" % (ti, ci), "h%d-%d" % (ti, ci))
                s.done(pid, "步骤%d-0" % ti, "h%d-0" % ti)
        except Exception as e:  # noqa: BLE001
            errs.append(repr(e))

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    check("并发零异常", not errs, "; ".join(errs[:2]))
    snap = s.steps(pid)
    check("并发24步零丢失", len(snap) == 24)
    # 新实例从盘上重载, 验证持久化后的真实状态
    snap2 = CheckpointStore(root).steps(pid)
    check("并发后盘上状态一致", snap2 == snap)
    # 清单文件可解析 (原子写未损坏)
    try:
        json.loads(open(s.manifest_path(pid), encoding="utf-8").read())
        check("并发后清单合法JSON", True)
    except Exception as e:
        check("并发后清单合法JSON", False, repr(e))


def main():
    tmp1 = tempfile.mkdtemp(prefix="dm_ckpt_1_")
    tmp2 = tempfile.mkdtemp(prefix="dm_ckpt_2_")
    tmp3 = tempfile.mkdtemp(prefix="dm_ckpt_3_")
    tmp4 = tempfile.mkdtemp(prefix="dm_ckpt_4_")
    tmp5 = tempfile.mkdtemp(prefix="dm_ckpt_5_")
    try:
        print("--- 基础接口/持久化/隔离 ---")
        test_basic_and_persistence(tmp1)
        print("--- 中断恢复实测 ---")
        test_interrupt_recovery(tmp2)
        print("--- 清单确定性 ---")
        test_manifest_determinism(tmp3, tmp4)
        print("--- 路径消毒 ---")
        test_path_sanitization(tmp5)
        print("--- 线程安全 ---")
        test_thread_safety(tmp5)
    finally:
        for d in (tmp1, tmp2, tmp3, tmp4, tmp5):
            shutil.rmtree(d, ignore_errors=True)
    print("\n" + "=" * 60)
    print("  结果: %d PASS / %d FAIL" % (PASS, FAIL))
    if ERRORS:
        for e in ERRORS[:20]:
            print("  -", e)
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
