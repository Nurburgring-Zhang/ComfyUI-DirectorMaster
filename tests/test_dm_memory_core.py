# -*- coding: utf-8 -*-
"""
批次4 WaveA builder-m1 — dm_memory 四域核心+脱敏 测试 (tests/test_dm_memory_core.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch4.md 验收口径):
  T0 模块常量与导出口径 (六分支枚举/已验证信号/1100 上限/阈值 0.8/SOP 三段键)
  T1 决策卡 schema 正负样本 (验收①)
  T2 决策卡纪律双向 (验收②): 未验证生成不入正面教训 + rejected 负面证据保留
     + add_card 拒绝路径 + list_cards 过滤 + cards.jsonl 追加写 + safe_project 布局
  T3 card_to_prompt ≤1100
  T4 偏好 schema 正负样本 (验收①)
  T5 偏好六分支各一用例 + bigram Jaccard + verify_counts 自校验 (验收③)
  T6 程序记忆 SOP 三段式 + explicit=True 才落盘纪律 (验收①)
  T7 风格圣经+系列档案 schema 正负样本 (验收①)
  T8 脱敏: 四类型正样本 + 白名单整词豁免 + 负样本不误伤
  T9 R1 修复回归: H1 入库前脱敏接线 (三写路径+永不致命降级) / M1 偏好库损坏自愈 /
     M3 safe_name 碰撞防护 / LOW-5 redaction 绕过面补齐
  T10 R2 修复回归: MED-1 偏好库二级结构损坏逐元素过滤 / MED-2 safe_name 大小写/
     尾点/保留名碰撞防护 (九模块) / LOW-3 永不致命边界 / LOW-5 误伤面收窄
纪律: 记忆存储一律 tempfile 目录, 全程零仓库内写入, 故不落证据 JSON
      (汇总以 PASS/FAIL 计数输出)。
退出码: 0 = 全部通过, 1 = 有失败。运行: python -X utf8 tests/test_dm_memory_core.py
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.dm_memory import (
    open_memory, schema, shot_cards, preference_store, procedure_memory, redaction,
)
from aggregator.dm_memory import (
    anchor_link, evolution, injection, retrieval, series_inherit, style_bible,
)

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


def make_memory(project="测试项目"):
    d = tempfile.mkdtemp(prefix="dm_mem_test_")
    TEMP_DIRS.append(d)
    return open_memory(d, project)


def mem_file(mem, *parts):
    return os.path.join(mem.out_dir, "dm_memory", *parts)


def raw_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln for ln in f.read().splitlines() if ln.strip()]


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 模块常量与导出口径")
    check("T0 六分支枚举精确钉死",
          schema.PREFERENCE_BRANCHES == ("added", "equivalent_skipped", "refined",
                                         "conflict_replaced", "invalid_removed", "oneoff_ignored"),
          f"got={schema.PREFERENCE_BRANCHES}")
    check("T0 已验证信号 = 用户确认/成片采用 (正面教训唯一来源)",
          schema.CARD_VERIFIED_SIGNALS == ("用户确认", "成片采用"),
          f"got={schema.CARD_VERIFIED_SIGNALS}")
    check("T0 card_to_prompt 上限 1100 / Jaccard 阈值 0.8",
          schema.CARD_PROMPT_MAX == 1100 and schema.PREFERENCE_JACCARD_THRESHOLD == 0.8)
    check("T0 SOP 三段键 use_when/procedure/exceptions 钉死",
          schema.PROCEDURE_REQUIRED_KEYS == ("use_when", "procedure", "exceptions"))
    check("T0 圣经诚实占位标记 LLM_DISTILL_PENDING + 蒸馏状态枚举",
          schema.BIBLE_DISTILL_PENDING == "LLM_DISTILL_PENDING"
          and schema.BIBLE_DISTILL_STATES == ("pending", "done"))
    check("T0 决策卡枚举齐备 (signal 4 值 / status 3 值 / rejected 必填被否方案)",
          schema.CARD_SIGNALS == ("用户确认", "成片采用", "生成", "用户纠正")
          and schema.CARD_STATUSES == ("candidate", "confirmed", "rejected"))

    # -----------------------------------------------------------------
    print("T1 决策卡 schema 正负样本 (验收①)")
    ok_card = {"标题": "镜3 夜景外景", "signal": "用户确认", "status": "confirmed",
               "方案": "低照度+烟雾机", "教训": "夜景优先低照度"}
    ok, errs = schema.validate_card(ok_card)
    check("T1 正样本: 完整 confirmed 卡通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "镜4", "signal": "生成", "status": "candidate"})
    check("T1 正样本: 最小 candidate 卡 (仅标题/signal/status) 通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "镜5", "signal": "用户纠正",
                                     "status": "rejected", "被否方案": "广角怼脸, 患者不适"})
    check("T1 正样本: rejected 卡带被否方案通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_card(["不是", "dict"])
    check("T1 负样本: 非 dict 拒绝", not ok and errs, f"errs={errs}")
    ok, errs = schema.validate_card({"signal": "生成", "status": "candidate"})
    check("T1 负样本: 缺标题拒绝且报错点名 标题", not ok and any("标题" in e for e in errs),
          f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "x", "signal": "不存在的信号", "status": "candidate"})
    check("T1 负样本: signal 越枚举拒绝", not ok and any("signal" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "x", "signal": "生成", "status": "待定"})
    check("T1 负样本: status 越枚举拒绝", not ok and any("status" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "x", "signal": "生成", "status": "rejected"})
    check("T1 负样本: rejected 缺被否方案拒绝 (负面证据纪律)", not ok
          and any("被否方案" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_card({"标题": "长" * 61, "signal": "生成", "status": "candidate"})
    check("T1 负样本: 标题超长 (>60) 拒绝", not ok and any("超长" in e for e in errs), f"errs={errs}")

    # -----------------------------------------------------------------
    print("T2 决策卡纪律双向 (验收②)")
    mem = make_memory("测试项目A")
    cid1, reason1 = shot_cards.add_card(mem, {"标题": "镜3 夜景外景", "signal": "生成",
                                              "status": "candidate", "方案": "低照度+烟雾机",
                                              "镜号": "S03"})
    check("T2 未验证生成卡可入库且获得 card_id (保留为待验证事实)",
          isinstance(cid1, str) and cid1.startswith("card-") and reason1 == "",
          f"cid={cid1} reason={reason1}")
    # R2 MED-2 后 <safe_project> 含 ASCII 字母时带 sha1 后缀 — 路径按 safe_name 渲染 (断言语义不变)
    cards_path = mem_file(mem, shot_cards._safe_name("测试项目A"), "cards.jsonl")
    check("T2 存储布局钉死 <out_dir>/dm_memory/<safe_project>/cards.jsonl",
          os.path.exists(cards_path), f"path={cards_path}")
    stored1 = shot_cards.list_cards(mem)[0]
    check("T2 方向A: 未验证生成 (生成×candidate) 不产生正面教训 (is_positive_lesson=False)",
          shot_cards.is_positive_lesson(stored1) is False)
    p1 = shot_cards.card_to_prompt(stored1)
    check("T2 方向A: 未验证卡 prompt 显式标注 不作正面教训 且不含 已验证",
          "未验证·不作正面教训" in p1 and "已验证" not in p1, f"p1={p1}")
    cid2, _ = shot_cards.add_card(mem, {"标题": "镜3 夜景外景 定稿", "signal": "用户确认",
                                        "status": "confirmed", "方案": "低照度+烟雾机",
                                        "教训": "夜景优先低照度"})
    stored2 = [c for c in shot_cards.list_cards(mem) if c["card_id"] == cid2][0]
    check("T2 方向B: 用户确认×confirmed 产生正面教训 (is_positive_lesson=True)",
          shot_cards.is_positive_lesson(stored2) is True)
    check("T2 方向B: 成片采用×confirmed 亦为正面教训 (枚举双向覆盖)",
          shot_cards.is_positive_lesson({"signal": "成片采用", "status": "confirmed"}) is True)
    cid_bad, reason_bad = shot_cards.add_card(mem, {"标题": "镜6", "signal": "用户纠正",
                                                    "status": "rejected"})
    check("T2 rejected 缺被否方案 → add_card 拒绝 (None+原因点名被否方案), 不落盘",
          cid_bad is None and "被否方案" in reason_bad, f"reason={reason_bad}")
    check("T2 拒绝后 cards.jsonl 行数不变 (仍是 2 行)", len(raw_lines(cards_path)) == 2)
    cid3, _ = shot_cards.add_card(mem, {"标题": "镜6 手持", "signal": "用户纠正",
                                        "status": "rejected", "方案": "手持长镜头",
                                        "被否方案": "手持过长致眩晕, 改稳定器缓推"})
    check("T2 rejected 卡带被否方案可入库 (负面证据保留)",
          isinstance(cid3, str), f"cid={cid3}")
    stored3 = [c for c in shot_cards.list_cards(mem) if c["card_id"] == cid3][0]
    check("T2 rejected 卡不产生正面教训", shot_cards.is_positive_lesson(stored3) is False)
    p3 = shot_cards.card_to_prompt(stored3)
    check("T2 rejected 卡 prompt 以负面证据呈现被否方案 (原文保留可注入)",
          "负面证据·被否方案:手持过长致眩晕" in p3 and "已否决" in p3, f"p3={p3}")
    cid_bad2, _ = shot_cards.add_card(mem, {"标题": "t", "signal": "假信号", "status": "candidate"})
    check("T2 schema 非法卡 add_card 拒绝不落盘", cid_bad2 is None and len(raw_lines(cards_path)) == 3)
    rej = shot_cards.list_cards(mem, {"status": "rejected"})
    check("T2 list_cards 过滤: status=rejected 恰 1 张 (负面证据可检索)",
          len(rej) == 1 and rej[0]["card_id"] == cid3, f"n={len(rej)}")
    check("T2 list_cards 过滤: 结构键 镜号=S03 恰 1 张",
          len(shot_cards.list_cards(mem, {"镜号": "S03"})) == 1)
    check("T2 list_cards 过滤: 复合条件 status+signal 恰 1 张; 无过滤全量 3 张",
          len(shot_cards.list_cards(mem, {"status": "confirmed", "signal": "用户确认"})) == 1
          and len(shot_cards.list_cards(mem)) == 3)
    lines = raw_lines(cards_path)
    check("T2 cards.jsonl 追加写: 3 行均合法 JSON 且顺序=插入序",
          [json.loads(ln)["card_id"] for ln in lines] == [cid1, cid2, cid3])
    mem_odd = make_memory('坏:名*字?')
    shot_cards.add_card(mem_odd, {"标题": "x", "signal": "生成", "status": "candidate"})
    # R1 MED-3: safe_name 信息丢失时追加短 sha1 后缀, 期望目录名经同一函数构造
    check("T2 safe_project 配方: 非法字符替换为 _ (+碰撞防护后缀) 后建目录",
          os.path.isdir(mem_file(mem_odd, shot_cards._safe_name('坏:名*字?'))),
          f"ls={os.listdir(mem_file(mem_odd))}")

    # -----------------------------------------------------------------
    print("T3 card_to_prompt ≤1100")
    long_card = {"card_id": "card-9999-deadbeef", "标题": "长方案卡", "signal": "用户确认",
                 "status": "confirmed", "方案": "详" * 3000, "教训": "结" * 1500}
    p = shot_cards.card_to_prompt(long_card)
    check("T3 超长卡 prompt ≤1100 且头部信息完整保留",
          len(p) <= 1100 and p.startswith("【决策卡 card-9999-deadbeef】长方案卡"), f"len={len(p)}")
    check("T3 超长截断带省略号 (非硬切半个字段后无标记)", p.endswith("…"), f"tail={p[-8:]}")
    short_card = {"card_id": "card-0001-aa", "标题": "短卡", "signal": "用户确认",
                  "status": "confirmed", "方案": "固定机位"}
    ps = shot_cards.card_to_prompt(short_card)
    check("T3 短卡 prompt 全字段完整且 <1100",
          len(ps) < 1100 and "方案:固定机位" in ps and "已验证" in ps, f"ps={ps}")
    check("T3 非 dict 输入诚实返回空串 (不炸)", shot_cards.card_to_prompt(None) == "")

    # -----------------------------------------------------------------
    print("T4 偏好 schema 正负样本 (验收①)")
    ok, errs = schema.validate_preference({"标题": "色调", "内容": "整体冷色调"})
    check("T4 正样本: 标题+内容 通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_preference({"标题": "色调"})
    check("T4 负样本: 缺内容拒绝且点名 内容", not ok and any("内容" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_preference({"标题": "t", "内容": "长" * 2001})
    check("T4 负样本: 内容超长 (>2000) 拒绝", not ok and any("超长" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_preference({"标题": "t", "内容": "c", "失效": "yes"})
    check("T4 负样本: 失效 非布尔拒绝", not ok and any("失效" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_preference("字符串")
    check("T4 负样本: 非 dict 拒绝", not ok and errs, f"errs={errs}")

    # -----------------------------------------------------------------
    print("T5 偏好六分支 + Jaccard + verify_counts (验收③)")
    mem2 = make_memory("偏好项目")
    b1 = preference_store.apply_preference(mem2, {"标题": "色调", "内容": "整体冷色调低饱和"})
    check("T5 分支1 added: 新偏好入库", b1 == "added", f"b={b1}")
    b2 = preference_store.apply_preference(mem2, {"标题": "色调", "内容": "整体冷色调低饱和。"})
    ents = preference_store._load_preferences(mem2)["entries"]
    check("T5 分支2 equivalent_skipped: 同标题+Jaccard≥0.8 跳过且存量零改动",
          b2 == "equivalent_skipped" and len(ents) == 1
          and ents[0]["内容"] == "整体冷色调低饱和", f"b={b2} ents={ents}")
    b3 = preference_store.apply_preference(mem2, {"标题": "色调",
                                                  "内容": "改用高对比冷色调, 夜景加重青蓝"})
    ents = preference_store._load_preferences(mem2)["entries"]
    check("T5 分支3 refined: 同标题+低相似 → 内容细化更新且 refined_count=1",
          b3 == "refined" and ents[0]["内容"].startswith("改用高对比")
          and ents[0]["refined_count"] == 1, f"b={b3} e0={ents[0]}")
    b4 = preference_store.apply_preference(mem2, {"标题": "色调", "内容": "禁止冷色调, 一律暖色调",
                                                  "冲突替换": True})
    ents = preference_store._load_preferences(mem2)["entries"]
    check("T5 分支4 conflict_replaced: 显式冲突标记 → 旧内容被替换且 replaced_count=1",
          b4 == "conflict_replaced" and ents[0]["内容"].startswith("禁止冷色调")
          and ents[0]["replaced_count"] == 1, f"b={b4} e0={ents[0]}")
    b5 = preference_store.apply_preference(mem2, {"标题": "色调", "内容": "x", "失效": True})
    ents = preference_store._load_preferences(mem2)["entries"]
    check("T5 分支5 invalid_removed: 失效指令删除存量且库空",
          b5 == "invalid_removed" and len(ents) == 0, f"b={b5} n={len(ents)}")
    b6 = preference_store.apply_preference(mem2, {"标题": "本镜", "内容": "这镜先试 4:3",
                                                  "signal": "一次性"})
    b6b = preference_store.apply_preference(mem2, {"标题": "本镜2", "内容": "临时偏好",
                                                   "一次性": True})
    check("T5 分支6 oneoff_ignored: 一次性信号 (signal=一次性 与 一次性=True) 均不落库",
          b6 == "oneoff_ignored" and b6b == "oneoff_ignored"
          and len(preference_store._load_preferences(mem2)["entries"]) == 0,
          f"b={b6}/{b6b}")
    b5m = preference_store.apply_preference(mem2, {"标题": "不存在的偏好", "内容": "x", "失效": True})
    check("T5 失效指令未命中 → 一次性消费 (oneoff_ignored), 不虚报删除",
          b5m == "oneoff_ignored")
    b7 = preference_store.apply_preference(mem2, {"标题": "画幅", "内容": "全片 2.39:1"})
    check("T5 删除后同标题可重新 added (独立生命周期)", b7 == "added")
    j1 = preference_store.bigram_jaccard("abcdefgh", "abcdefgh")
    j2 = preference_store.bigram_jaccard("abcdefgh", "ijklmnop")
    j3 = preference_store.bigram_jaccard("整体冷色调低饱和", "整体冷色调低饱和。")
    j4 = preference_store.bigram_jaccard("整体冷色调低饱和", "夜景手持跟拍节奏")
    check("T5 bigram Jaccard 单元: 全同=1.0 / 全异=0.0 / 追加句点=0.875≥0.8 / 无关<0.8",
          j1 == 1.0 and j2 == 0.0 and j3 >= 0.8 and j4 < 0.8,
          f"j={j1},{j2},{j3:.3f},{j4:.3f}")
    okc, drift = preference_store.verify_counts(mem2)
    check("T5 verify_counts: 六分支序列后计数自洽 (ok=True, drift={})",
          okc and drift == {}, f"drift={drift}")
    counts = preference_store._load_preferences(mem2)["counts"]
    check("T5 计数字段与分支轨迹一致: added=2 refined=1 conflict=1 invalid_removed=1 total=1",
          counts["added"] == 2 and counts["refined"] == 1 and counts["conflict_replaced"] == 1
          and counts["invalid_removed"] == 1 and counts["entries_total"] == 1, f"counts={counts}")
    prefs_path = mem_file(mem2, "偏好项目", "preferences.json")
    with open(prefs_path, "r", encoding="utf-8") as f:
        tampered = json.load(f)
    tampered["counts"]["added"] += 5
    okc, drift = preference_store.verify_counts(tampered)
    check("T5 verify_counts: 篡改 added → ok=False 且 drift 点名 added",
          not okc and "added" in drift, f"drift={drift}")
    tampered["counts"]["added"] -= 5
    tampered["entries"].append({"标题": "幽灵"})
    okc, drift = preference_store.verify_counts(tampered)
    check("T5 verify_counts: 篡改 entries → entries_total 漂移被发现",
          not okc and "entries_total" in drift, f"drift={drift}")
    before = len(preference_store._load_preferences(mem2)["entries"])
    raised = False
    try:
        preference_store.apply_preference(mem2, {"标题": "缺内容"})
    except ValueError:
        raised = True
    check("T5 schema 非法条目抛 ValueError 且库零改动",
          raised and len(preference_store._load_preferences(mem2)["entries"]) == before)
    check("T5 原子写无 .tmp 残留", not os.path.exists(prefs_path + ".tmp"))

    # -----------------------------------------------------------------
    print("T6 程序记忆 SOP 三段式 + explicit 落盘纪律")
    sop = {"use_when": "夜景外景需要人物面部可见",
           "procedure": "先 3200K 主光补面, 再雾机分层, 最后低照度底子光",
           "exceptions": "篝火场景跳过底子光, 以火光为唯一光源"}
    ok, errs = schema.validate_procedure(sop)
    check("T6 正样本: 三段齐全通过 (验收①程序记忆域)", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_procedure({"use_when": "x", "procedure": "y"})
    check("T6 负样本: 缺 exceptions 拒绝且点名", not ok and any("exceptions" in e for e in errs),
          f"errs={errs}")
    mem3 = make_memory("程序项目")
    w1, r1 = procedure_memory.upsert_procedure(mem3, "夜景布光", sop)
    check("T6 纪律: explicit=False → (False, 未写原因) 且零文件落盘",
          w1 is False and r1 and procedure_memory.load_procedures(mem3) == [],
          f"w={w1} r={r1}")
    w2, r2 = procedure_memory.upsert_procedure(mem3, "夜景布光", sop, explicit=True)
    procs = procedure_memory.load_procedures(mem3)
    check("T6 explicit=True → 落盘成功且 load 读回三段原文",
          w2 is True and r2 == "" and len(procs) == 1
          and procs[0]["use_when"] == sop["use_when"]
          and procs[0]["procedure"] == sop["procedure"]
          and procs[0]["exceptions"] == sop["exceptions"], f"w={w2} r={r2} n={len(procs)}")
    check("T6 存储布局钉死 procedures/<safe_topic>.json",
          os.path.exists(mem_file(mem3, "程序项目", "procedures", "夜景布光.json")))
    sop_bad = {"use_when": "x", "procedure": "y"}
    w3, r3 = procedure_memory.upsert_procedure(mem3, "坏SOP", sop_bad, explicit=True)
    check("T6 explicit=True 但 schema 非法 → 拒绝不落盘",
          w3 is False and "校验失败" in r3 and len(procedure_memory.load_procedures(mem3)) == 1,
          f"r={r3}")
    sop_v2 = dict(sop, exceptions="雨天禁用雾机 (湿度饱和失效)")
    w4, _ = procedure_memory.upsert_procedure(mem3, "夜景布光", sop_v2, explicit=True)
    procs = procedure_memory.load_procedures(mem3)
    check("T6 upsert 同 topic 覆盖更新 (仍 1 条, exceptions 已更新)",
          w4 is True and len(procs) == 1 and "雨天禁用" in procs[0]["exceptions"],
          f"n={len(procs)}")
    w5, _ = procedure_memory.upsert_procedure(mem3, "运镜/节奏:V2", sop, explicit=True)
    files = os.listdir(mem_file(mem3, "程序项目", "procedures"))
    check("T6 topic 非法字符走 safe_name 配方 (文件名无 \\/:*?\"<>|) 且可读回",
          w5 is True and len(files) == 2
          and not any(c in f for f in files for c in '\\/:*?"<>|'), f"files={files}")
    w6, r6 = procedure_memory.upsert_procedure(mem3, "  ", sop, explicit=True)
    check("T6 空 topic 拒绝未写", w6 is False and r6 and len(procedure_memory.load_procedures(mem3)) == 2)

    # -----------------------------------------------------------------
    print("T7 风格圣经+系列档案 schema 正负样本 (验收①)")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {"版本数": 3},
                                      "蒸馏段": "<!-- LLM_DISTILL_PENDING -->",
                                      "蒸馏状态": "pending"})
    check("T7 正样本: pending 圣经带诚实占位通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {},
                                      "蒸馏段": "冷色调, 手持", "蒸馏状态": "pending"})
    check("T7 负样本: pending 无占位标记 = 猜测 → 拒绝且点名 LLM_DISTILL_PENDING",
          not ok and any("LLM_DISTILL_PENDING" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {},
                                      "蒸馏段": "冷色调, 手持", "蒸馏状态": "done"})
    check("T7 正样本: done 状态无需占位", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "蒸馏段": "", "蒸馏状态": "pending"})
    check("T7 负样本: 缺脚本统计拒绝", not ok and any("脚本统计" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_bible("字符串")
    check("T7 负样本: 非 dict 拒绝", not ok and errs, f"errs={errs}")
    ok, errs = schema.validate_series({"worldview": "末世废土", "风格锚": "王家卫·冷色",
                                       "dna": ["{...}", {"维度": {}}]})
    check("T7 正样本: 系列档案 (worldview/风格锚/dna 列表) 通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_series({"worldview": "末世废土", "风格锚": "x", "dna": "不是列表"})
    check("T7 负样本: dna 非列表拒绝", not ok and any("dna" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_series({"风格锚": "x", "dna": []})
    check("T7 负样本: 缺 worldview 拒绝且点名", not ok and any("worldview" in e for e in errs),
          f"errs={errs}")
    ok, errs = schema.validate_series({"worldview": "w", "风格锚": "s", "dna": [123]})
    check("T7 负样本: dna 元素非 str/dict 拒绝", not ok and any("dna[0]" in e for e in errs),
          f"errs={errs}")

    # -----------------------------------------------------------------
    print("T8 脱敏 四类型 + 白名单豁免 + 负样本不误伤")
    clean, findings = redaction.redact("有问题联系 13812345678 处理")
    check("T8 手机号: 替换为 [手机号] 且 findings 类型化",
          clean == "有问题联系 [手机号] 处理"
          and findings == [{"type": "phone", "placeholder": "[手机号]"}], f"clean={clean}")
    clean, findings = redaction.redact("工单号 123456789012 共 12 位, 短号 1381234567")
    check("T8 手机号负样本: 12 位数字与 10 位短号不误伤",
          clean == "工单号 123456789012 共 12 位, 短号 1381234567" and findings == [],
          f"clean={clean}")
    clean, findings = redaction.redact("发送到 zhang.san+vip@example.com.cn 收")
    check("T8 邮箱: 替换为 [邮箱]", "[邮箱]" in clean and "zhang.san" not in clean
          and findings[0]["type"] == "email", f"clean={clean}")
    clean, findings = redaction.redact("符号 @ 以及 foo@bar 都不是完整邮箱")
    check("T8 邮箱负样本: 裸 @ 与无 TLD 不误伤", findings == [] and "foo@bar" in clean,
          f"clean={clean}")
    clean, findings = redaction.redact("密钥 sk-abcd1234abcd1234abcd 已泄露")
    check("T8 API-key (sk- 令牌): 替换为 [API密钥]",
          "[API密钥]" in clean and "abcd1234abcd" not in clean
          and findings[0]["type"] == "api_key", f"clean={clean}")
    clean, _ = redaction.redact("短令牌 sk-123 无需处理")
    check("T8 API-key 负样本: sk- 短令牌不误伤", "sk-123" in clean)
    clean, _ = redaction.redact('api_key = "0123456789abcdefXYZ"')
    check("T8 API-key (keyword:value): 值被替换而键名保留",
          "api_key" in clean and "[API密钥]" in clean and "0123456789abcdef" not in clean,
          f"clean={clean}")
    clean, _ = redaction.redact("token=abc123 太短不管")
    check("T8 API-key 负样本: 短 value 不误伤", "token=abc123" in clean)
    clean, _ = redaction.redact("请求头 Authorization: Bearer eyJhbGciOiJIUzI1NiIs")
    check("T8 API-key (Bearer 形态): 令牌替换",
          "[API密钥]" in clean and "eyJhbGciOiJIUzI1NiIs" not in clean, f"clean={clean}")
    clean, _ = redaction.redact(r"输出在 C:\Users\zhang\render\f.png 看")
    check("T8 盘符私有路径 (反斜杠): 替换为 [私有路径]",
          "[私有路径]" in clean and "zhang" not in clean, f"clean={clean}")
    clean, _ = redaction.redact("备用 C:/Users/li/v.mp4 也删")
    check("T8 盘符私有路径 (正斜杠): 同样替换",
          "[私有路径]" in clean and "li/v.mp4" not in clean, f"clean={clean}")
    clean, _ = redaction.redact("相对路径 输出/render/f.png 与公共盘 D:\\公共素材\\bg.mp4 保留")
    check("T8 路径负样本: 相对路径与非用户盘符路径不误伤",
          "输出/render/f.png" in clean and "D:\\公共素材\\bg.mp4" in clean, f"clean={clean}")
    t_wl = "邮箱 keep@ok.cn 与手机 13912345678 及备用 13800000000"
    clean, findings = redaction.redact(t_wl, whitelist=("keep@ok.cn", "13912345678"))
    check("T8 白名单整词豁免: 邮箱与指定手机保留, 未列手机仍脱敏",
          "keep@ok.cn" in clean and "13912345678" in clean and "[手机号]" in clean
          and len(findings) == 1, f"clean={clean} f={findings}")
    clean, _ = redaction.redact("邮箱 other@x.cn 泄露", whitelist=("keep@ok.cn",))
    check("T8 白名单不放水: 未列入白名单的同类敏感项照常脱敏",
          "[邮箱]" in clean and "other@x.cn" not in clean)
    multi = ("联系人 13812345678, 邮箱 a-b@c-d.cn, 密钥 sk-aaaa1111bbbb2222cccc, "
             r"日志在 C:\Users\nb\out.log")
    clean, findings = redaction.redact(multi)
    types = {f["type"] for f in findings}
    check("T8 混合文本: 四类型齐中且占位符齐全",
          types == {"phone", "email", "api_key", "private_path"} and len(findings) == 4
          and "[手机号]" in clean and "[邮箱]" in clean
          and "[API密钥]" in clean and "[私有路径]" in clean, f"types={types}")
    check("T8 混合文本: 原始敏感值零残留",
          all(x not in clean for x in ("13812345678", "a-b@c-d.cn",
                                       "sk-aaaa1111bbbb2222cccc", "nb\\out.log")),
          f"clean={clean}")
    plain = "第三场夜景改为手持跟拍, 节奏加快, 使用 85mm 镜头"
    clean, findings = redaction.redact(plain)
    check("T8 纯中文负样本: 逐字节不变 (零误伤)", clean == plain and findings == [])

    # -----------------------------------------------------------------
    print("T9 R1 修复回归: H1 入库脱敏接线 / M1 损坏自愈 / M3 碰撞防护 / LOW-5 绕过面")
    # ---- H1: add_card 落盘前脱敏, card 哈希在脱敏后计算 ----
    mem_s = make_memory("脱敏项目")
    secret_card = {"标题": "镜3", "signal": "用户确认", "status": "confirmed",
                   "方案": "部署用 api_key=sk-abcd1234abcd1234efgh",
                   "教训": "有问题联系 13812345678"}
    cid_s, reason_s = shot_cards.add_card(mem_s, secret_card)
    stored_s = [c for c in shot_cards.list_cards(mem_s) if c["card_id"] == cid_s][0]
    with open(mem_file(mem_s, "脱敏项目", "cards.jsonl"), "r", encoding="utf-8") as f:
        disk_s = f.read()
    check("T9 H1 add_card: 敏感值落盘前已脱敏 (盘上与读回均无原文, 占位符在库)",
          reason_s == "" and isinstance(cid_s, str)
          and "sk-abcd1234abcd1234efgh" not in disk_s and "13812345678" not in disk_s
          and "[API密钥]" in stored_s["方案"] and "[手机号]" in stored_s["教训"],
          f"cid={cid_s} stored={stored_s}")
    cid_s2, _ = shot_cards.add_card(mem_s, dict(secret_card))
    check("T9 H1 card 哈希在脱敏后计算: 同内容卡 digest 段一致 (脱敏确定性→哈希稳定)",
          cid_s.split("-")[-1] == cid_s2.split("-")[-1], f"{cid_s} vs {cid_s2}")
    struct_card = {"标题": "镜4", "signal": "生成", "status": "candidate",
                   "镜号": "S03", "seed": 12345, "备注": "邮箱 a@b.cn 反馈"}
    cid_t, _ = shot_cards.add_card(mem_s, struct_card)
    stored_t = [c for c in shot_cards.list_cards(mem_s) if c["card_id"] == cid_t][0]
    check("T9 H1 结构字段不碰 (镜号/seed/signal 原样), 文本键 (备注) 已脱敏 — 宁可漏脱不破坏结构",
          stored_t["镜号"] == "S03" and stored_t["seed"] == 12345
          and stored_t["signal"] == "生成" and "[邮箱]" in stored_t["备注"],
          f"stored={stored_t}")
    # ---- H1: 偏好与 SOP 写路径 ----
    preference_store.apply_preference(mem_s, {"标题": "发布渠道",
                                              "内容": "token=abcdefghijklmnopqr"})
    e0 = [e for e in preference_store._load_preferences(mem_s)["entries"]
          if e["标题"] == "发布渠道"][0]
    check("T9 H1 偏好内容落盘前脱敏 (键名保留/值替换, 原文零残留)",
          "abcdefghijklmnopqr" not in e0["内容"] and "[API密钥]" in e0["内容"]
          and e0["标题"] == "发布渠道", f"e0={e0}")
    b_s2 = preference_store.apply_preference(mem_s, {"标题": "发布渠道",
                                                     "内容": "token=abcdefghijklmnopqr"})
    check("T9 H1 脱敏口径判重一致: 同原文二次提交 → equivalent_skipped (去重键同口径)",
          b_s2 == "equivalent_skipped", f"b={b_s2}")
    w_s, _ = procedure_memory.upsert_procedure(mem_s, "客服SOP", {
        "use_when": "用户反馈", "procedure": "先联系 13912345678 确认",
        "exceptions": "无"}, explicit=True)
    p0 = [p for p in procedure_memory.load_procedures(mem_s) if p["topic"] == "客服SOP"][0]
    check("T9 H1 SOP 三段落盘前脱敏 (topic 定位键不碰)",
          w_s is True and "13912345678" not in json.dumps(p0, ensure_ascii=False)
          and "[手机号]" in p0["procedure"] and p0["topic"] == "客服SOP", f"p0={p0}")
    # ---- H1: 白名单透传 + 永不致命降级 ----
    wl_out = redaction.redact_free_text({"方案": "联系 13812345678"},
                                        whitelist=("13812345678",))
    check("T9 H1 whitelist 参数透传 redact_free_text (豁免项保留, 未列项照常脱敏)",
          wl_out["方案"] == "联系 13812345678"
          and redaction.redact_free_text({"方案": "联系 13812345678"})["方案"]
          == "联系 [手机号]", f"wl={wl_out}")
    old_re_email = redaction._RE_EMAIL
    try:
        redaction._RE_EMAIL = None  # 异常注入: redact 内部必抛
        err_nf = io.StringIO()
        with contextlib.redirect_stderr(err_nf):
            clean_nf, findings_nf = redaction.redact("邮箱 a@b.cn 与 13812345678")
        check("T9 H1 redact 内部异常 → 原文放行 + findings 空 + stderr 降级 (永不致命)",
              clean_nf == "邮箱 a@b.cn 与 13812345678" and findings_nf == []
              and "redaction 降级" in err_nf.getvalue(),
              f"clean={clean_nf!r} err={err_nf.getvalue()[:60]}")
        mem_nf = make_memory("降级项目")
        with contextlib.redirect_stderr(io.StringIO()):
            cid_nf, reason_nf = shot_cards.add_card(
                mem_nf, {"标题": "镜1", "signal": "生成", "status": "candidate",
                         "方案": "联系 13812345678"})
        check("T9 H1 脱敏降级不阻断入库: 卡按原文放行口径照常落盘",
              reason_nf == "" and bool(cid_nf)
              and shot_cards.list_cards(mem_nf)[0]["方案"] == "联系 13812345678",
              f"cid={cid_nf}")
    finally:
        redaction._RE_EMAIL = old_re_email
    # ---- M1: 偏好库损坏自愈 (截断/非法JSON/二进制 → 隔离 .corrupt + 空库继续) ----
    mem_c = make_memory("损坏项目")
    prefs_p = mem_file(mem_c, "损坏项目", "preferences.json")
    preference_store.apply_preference(mem_c, {"标题": "色调", "内容": "冷色调"})
    for tag, blob in [("截断", '{"entries": [{"标题": "色调", "内容"'),
                      ("非法JSON", "完全不是JSON"),
                      ("二进制", None)]:
        corrupt = blob.encode("utf-8") if blob is not None else b"\xff\x00\x9f\x00"
        with open(prefs_p, "wb") as f:
            f.write(corrupt)
        err_cap = io.StringIO()
        with contextlib.redirect_stderr(err_cap):
            b_c = preference_store.apply_preference(mem_c, {"标题": "新偏好", "内容": "暖色调"})
            ok_c, drift_c = preference_store.verify_counts(mem_c)
        with open(prefs_p + ".corrupt", "rb") as f:
            kept = f.read()
        check(f"T9 M1 偏好库[{tag}]损坏 → apply/verify 不崩 + 自愈空库继续可写",
              b_c == "added" and ok_c and drift_c == {} and not os.path.exists(prefs_p + ".tmp"),
              f"b={b_c} ok={ok_c} drift={drift_c}")
        check(f"T9 M1 偏好库[{tag}]损坏原件隔离 .corrupt (字节保全) + stderr 告警在案",
              kept == corrupt and "偏好库损坏" in err_cap.getvalue(),
              f"kept={kept[:16]!r} err={err_cap.getvalue()[:60]}")
    with open(prefs_p, "wb") as f:
        f.write(b"SECOND_CORRUPT")
    preference_store._load_preferences(mem_c)
    with open(prefs_p + ".corrupt", "rb") as f:
        kept2 = f.read()
    check("T9 M1 二次损坏 → .corrupt 覆盖为最新损坏件 (若已存在则覆盖)", kept2 == b"SECOND_CORRUPT")
    # ---- M3: safe_name 碰撞防覆写 (procedure topic / 跨域项目目录) ----
    mem_col = make_memory("碰撞项目")
    sop_col = {"use_when": "夜景", "procedure": "低照度", "exceptions": "篝火"}
    procedure_memory.upsert_procedure(mem_col, "夜景/布光", sop_col, explicit=True)
    procedure_memory.upsert_procedure(mem_col, "夜景:布光", sop_col, explicit=True)
    pdir_col = mem_file(mem_col, "碰撞项目", "procedures")
    files_col = sorted(os.listdir(pdir_col))
    check("T9 M3 topic 分隔符碰撞 → 两 topic 两文件 (不再静默覆写丢数据)",
          len(files_col) == 2 and len(procedure_memory.load_procedures(mem_col)) == 2,
          f"files={files_col}")
    procedure_memory.upsert_procedure(mem_col, "夜景/布光", sop_col, explicit=True)
    check("T9 M3 碰撞防护确定性: 同名原始输入恒同文件 (重写不增文件)",
          len(os.listdir(pdir_col)) == 2, f"n={len(os.listdir(pdir_col))}")
    long_a = "超长主题" + "甲" * 40
    long_b = "超长主题" + "甲" * 40 + "乙"
    procedure_memory.upsert_procedure(mem_col, long_a, sop_col, explicit=True)
    procedure_memory.upsert_procedure(mem_col, long_b, sop_col, explicit=True)
    check("T9 M3 >40 字符截断碰撞 → 截断同型两 topic 各自映射不同文件",
          len(os.listdir(pdir_col)) == 4
          and len(procedure_memory.load_procedures(mem_col)) == 4,
          f"n={len(os.listdir(pdir_col))}")
    mem_x = make_memory("分镜/项目:A")
    shot_cards.add_card(mem_x, {"标题": "x", "signal": "生成", "status": "candidate"})
    preference_store.apply_preference(mem_x, {"标题": "t", "内容": "c"})
    proj_dir_x = os.path.join(mem_x.out_dir, "dm_memory", shot_cards._safe_name("分镜/项目:A"))
    check("T9 M3 跨域同映射: 分隔符项目名下 cards/preferences 同目录 (读写一致)",
          os.path.isfile(os.path.join(proj_dir_x, "cards.jsonl"))
          and os.path.isfile(os.path.join(proj_dir_x, "preferences.json")),
          f"ls={os.listdir(os.path.join(mem_x.out_dir, 'dm_memory'))}")
    # ---- LOW-5: redaction 绕过面补齐 ----
    kv_cases = [("secret_key", "secret_key: abcdef1234567890"),
                ("api_token", "api_token: abcdef1234567890"),
                ("credentials", "credentials: abcdef1234567890"),
                ("auth", "auth: abcdef1234567890"),
                ("pwd", "pwd: abcdef1234567890"),
                ("密码", "密码: abcdef1234567890"),
                ("Bearer无空格", "Bearer:eyJhbGciOiJIUzI1NiIsInR5cCI6"),
                ("分隔符手机号-", "工单 138-1234-5678 归档"),
                ("分隔符手机号空格", "工单 138 1234 5678 归档"),
                ("嵌套dict str()", str({"cfg": {"password": "abcdefgh12345678"}}))]
    clean_map = {name: redaction.redact(text)[0] for name, text in kv_cases}
    check("T9 LOW-5 键名别名/Bearer无空格/分隔符手机号/嵌套 dict str() 全部命中脱敏",
          all(("[API密钥]" in c) or ("[手机号]" in c) for c in clean_map.values())
          and "abcdef1234567890" not in "".join(list(clean_map.values())[:6])
          and "eyJhbGciOiJIUzI1NiIs" not in clean_map["Bearer无空格"]
          and "138-1234-5678" not in clean_map["分隔符手机号-"]
          and "138 1234 5678" not in clean_map["分隔符手机号空格"]
          and "abcdefgh12345678" not in clean_map["嵌套dict str()"],
          f"map={clean_map}")
    check("T9 LOW-5 负样本不误伤: 短值/普通词/长数字串原样保留",
          redaction.redact("token=abc123 太短")[0] == "token=abc123 太短"
          and redaction.redact("bearer 令牌说明文字")[0] == "bearer 令牌说明文字"
          and redaction.redact("订单号 138123456789012345 不动")[0]
          == "订单号 138123456789012345 不动")

    # -----------------------------------------------------------------
    print("T10 R2 修复回归: MED-1 二级损坏过滤 / MED-2 safe_name 碰撞防护 / "
          "LOW-3 永不致命边界 / LOW-5 误伤面收窄")
    # ---- MED-1: 偏好库二级结构损坏 — 逐元素过滤, 不为单个坏元素隔离整个文件 ----
    mem_m1 = make_memory("M1二级损坏")
    prefs_m1 = mem_file(mem_m1, preference_store._safe_name("M1二级损坏"),
                        "preferences.json")
    os.makedirs(os.path.dirname(prefs_m1), exist_ok=True)
    good_m1 = {"标题": "夜戏", "内容": "夜景优先低照度", "signal": "用户偏好"}
    with open(prefs_m1, "w", encoding="utf-8") as f:
        json.dump({"schema_version": 1,
                   "entries": ["垃圾字符串", 42, None, good_m1],
                   "removed": [{"标题": "旧偏好", "内容": "x"}, "垃圾"],
                   "counts": "坏计数"}, f, ensure_ascii=False)
    err_m1 = io.StringIO()
    with contextlib.redirect_stderr(err_m1):
        branch_m1 = preference_store.apply_preference(
            mem_m1, {"标题": "日戏", "内容": "日戏优先控制光比"})
    check("T10 MED-1 entries 含非 dict 垃圾元素 → apply 不抛且正常入库 (added)",
          branch_m1 == "added", f"branch={branch_m1}")
    raw_m1 = json.load(open(prefs_m1, encoding="utf-8"))
    check("T10 MED-1 好条目存活+垃圾丢弃不隔离整文件 (无 .corrupt)",
          [e.get("标题") for e in raw_m1["entries"]] == ["夜戏", "日戏"]
          and all(isinstance(e, dict) for e in raw_m1["entries"])
          and not os.path.exists(prefs_m1 + ".corrupt"),
          f"entries={raw_m1['entries']}")
    check("T10 MED-1 stderr 告警在案 (丢弃计数 4 = entries 3 + removed 1) + counts 重置告警",
          "二级结构损坏" in err_m1.getvalue() and "4 个非 dict 元素" in err_m1.getvalue()
          and "counts 字段非 dict" in err_m1.getvalue(),
          f"stderr={err_m1.getvalue()[:260]!r}")
    check("T10 MED-1 计数重置后照常记账 (added=1) 且 verify_counts 不抛",
          raw_m1["counts"].get("added") == 1
          and isinstance(preference_store.verify_counts(mem_m1), tuple),
          f"counts={raw_m1['counts']}")

    # ---- MED-2: _safe_name 大小写/尾点/保留名碰撞防护 (九模块同源) ----
    check("T10 MED-2 Film ≠ film (NTFS 大小写折叠不再同目录)",
          shot_cards._safe_name("Film") != shot_cards._safe_name("film"))
    check("T10 MED-2 proj. ≠ proj (Windows 剥尾点碰撞防护)",
          shot_cards._safe_name("proj.") != shot_cards._safe_name("proj"))
    check("T10 MED-2 后缀 = 原始 raw 短 sha1 (确定性, 两遍同输出)",
          shot_cards._safe_name("Film")
          == "Film_" + hashlib.sha1(b"Film").hexdigest()[:8]
          and shot_cards._safe_name("proj.") == shot_cards._safe_name("proj."))
    check("T10 MED-2 CON 安全名不再裸保留名 (尾点/大小写同理避让)",
          shot_cards._safe_name("CON") != "CON"
          and not re.search(r"[. ]$", shot_cards._safe_name("proj. ")))
    mem_con = make_memory("CON")
    cid_con, reason_con = shot_cards.add_card(
        mem_con, {"标题": "保留名", "signal": "生成", "status": "candidate"})
    check("T10 MED-2 CON 项目 add_card 不抛 OSError 且落盘可读回",
          isinstance(cid_con, str) and cid_con.startswith("card-") and reason_con == ""
          and os.path.isfile(mem_file(mem_con, shot_cards._safe_name("CON"), "cards.jsonl")),
          f"cid={cid_con} reason={reason_con}")
    check("T10 MED-2 纯中文/纯数字仍零后缀 (零信息丢失不加盐)",
          shot_cards._safe_name("测试项目") == "测试项目"
          and shot_cards._safe_name("12345") == "12345")
    mods9 = (shot_cards, preference_store, procedure_memory, retrieval, injection,
             anchor_link, series_inherit, style_bible, evolution)
    names9 = {m._safe_name("Mixed案例X") for m in mods9}
    check("T10 MED-2 九模块 _safe_name 同源同映射 (同 project 恒同目录)",
          len(names9) == 1, f"names={names9}")
    mem_p2 = make_memory("路径对照P2")
    shot_cards.add_card(mem_p2, {"标题": "对照", "signal": "生成", "status": "candidate"})
    pdir_p2 = os.path.join(mem_p2.out_dir, "dm_memory", shot_cards._safe_name("路径对照P2"))
    check("T10 MED-2 各域 path helper 与 _safe_name 同映射 (cards/prefs/evolution 同目录)",
          os.path.isfile(os.path.join(pdir_p2, "cards.jsonl"))
          and preference_store._prefs_path(mem_p2)
          == os.path.join(pdir_p2, "preferences.json")
          and evolution.evolution_path(mem_p2.out_dir, "路径对照P2")
          == os.path.join(pdir_p2, "evolution.jsonl"),
          f"pdir={pdir_p2} ls={os.listdir(os.path.join(mem_p2.out_dir, 'dm_memory'))}")
    check("T10 MED-2 series_path 文件名基 = _safe_name(series_id)",
          os.path.basename(series_inherit.series_path(mem_p2.out_dir, "SeriesA"))
          == shot_cards._safe_name("SeriesA") + ".json")

    # ---- LOW-3: 永不致命边界 — str() 炸弹对象 / JSON 不可序列化字段 ----
    class _BoomStr:
        def __bool__(self):
            raise RuntimeError("bool 炸弹")

        def __str__(self):
            raise RuntimeError("str 炸弹")

    boom_l3 = _BoomStr()
    err_l3 = io.StringIO()
    with contextlib.redirect_stderr(err_l3):
        out_l3, find_l3 = redaction.redact(boom_l3)
    check("T10 LOW-3 redact(__str__/__bool__ 炸弹对象) 不抛且原样返回入参对象",
          out_l3 is boom_l3 and find_l3 == [],
          f"type={type(out_l3).__name__} stderr={err_l3.getvalue()[:80]!r}")
    mem_l3 = make_memory("L3对象卡")
    cid_l3, reason_l3 = shot_cards.add_card(
        mem_l3, {"标题": "对象卡", "signal": "生成", "status": "candidate",
                 "备注": b"\x00\x01"})
    check("T10 LOW-3 add_card(不可序列化字段) → (None, reason) 契约且零落盘",
          cid_l3 is None and bool(reason_l3)
          and not os.path.exists(mem_file(mem_l3, shot_cards._safe_name("L3对象卡"),
                                          "cards.jsonl")),
          f"cid={cid_l3!r} reason={reason_l3!r}")

    # ---- LOW-5: 误伤面收窄 (R2): 纯连字符值/无数字 bearer 词保留; 真实密钥仍命中 ----
    check("T10 LOW-5 纯连字符/纯标点值不再命中 (auth=-------------- 保留)",
          redaction.redact("auth=--------------")[0] == "auth=--------------")
    check("T10 LOW-5 bearer 后接无数字连字词不再命中 (普通散文保留)",
          redaction.redact("the bearer of-good-news-and-longer-words")[0]
          == "the bearer of-good-news-and-longer-words"
          and redaction.redact("bearer token-like-strings-appear-here")[0]
          == "bearer token-like-strings-appear-here")
    check("T10 LOW-5 真实密钥仍命中: sk- 前缀键/Bearer 数字型令牌/JWT",
          "[API密钥]" in redaction.redact("sk-proj-abc123XYZdef456ghi789")[0]
          and "[API密钥]" in redaction.redact("Bearer abcdef123456xyz789")[0]
          and "eyJhbGciOiJIUzI1NiIs"
          not in redaction.redact("Bearer:eyJhbGciOiJIUzI1NiIsInR5cCI6")[0])
    # [已知取舍] 值含数字且 ≥12 字符的普通词 (如 REAL_ESTATE_FUND_2024) 仍会被 KV
    # 规则命中 — 保持高召回优先, 与 R1 LOW-5 同口径, 不为罕见误伤放宽真实密钥面。


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    finally:
        for d in TEMP_DIRS:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\ndm_memory 四域核心+脱敏 测试结果: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
