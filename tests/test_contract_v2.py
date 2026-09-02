# -*- coding: utf-8 -*-
"""
批次6 D1 — 《DM 分镜 JSON 契约 v2》测试 (tests/test_contract_v2.py)
====================================================================
覆盖矩阵:
  T0  v2 版本声明 (STORYBOARD_CONTRACT_VERSION==2 / LEGAL_CONTRACT_VERSIONS==(1,2) /
      别名 CONTRACT_VERSION==2 / 诊断码 14 个)
  T1  v2 canonical 注册表 (CANON_TOP_KEYS 22 项含 锚定库/_项目风格锚; CANON_SHOT_KEYS 37 项含
      参考槽位/锚定/机位锚; 既有 19+32 键零删减)
  T2  v2 合法全量文档 (新键全带, 双射+库内+完整锚定 → ok 且零诊断, normalized 全保留)
  T3  slot-prompt-mismatch 正/负样本 (prompt 【参考@N】 标签集合 ↔ 参考槽位 集合双射)
  T4  slot-out-of-range 正/负样本 (库大小可得才判越界; 负数槽位; 库大小未知只查集合一致性)
  T5  anchor-invalid 正/负样本 (缺 首帧/尾帧 / 帧数≤0 / 帧数缺失 / bool / 非 dict;
      单通道不与 type-mismatch 双报)
  T6  v1 文件诊断零增量 (无新键 → 新码结构性不可触发; 既有错误码仍走原通道)
  T7  v1 零漂移 (golden fixture 真实 v1 文档照常 ok 且零诊断; normalized 版本头回显 1)
  T8  版本集合边界 (1/2 放行, 3/"1"/True/缺失 拒收口径不变)
  T9  attach_contract_version 语义 (缺失/非法 → 盖 1; 合法 1/2 原样保留)
  T10 新键类型通道 (参考槽位 非 list / 机位锚 非 str → type-mismatch; 新键不再进 extra)

自包含脚本 (纯标准库, 参照 tests/test_storyboard_contract.py 写法):
  python -X utf8 tests/test_contract_v2.py
退出码: 0 = 全部通过, 1 = 有失败。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.storyboard_contract import (
    STORYBOARD_CONTRACT_VERSION, CONTRACT_VERSION, LEGAL_CONTRACT_VERSIONS,
    DIAGNOSTIC_CODES, CANON_TOP_KEYS, CANON_SHOT_KEYS,
    attach_contract_version, validate_storyboard, self_check,
)

OLD_TOP_KEYS = ("contract_version", "分镜数", "总时长秒", "导演", "情绪", "画面模式",
                "故事理论", "叙事结构", "AIGC生产模式", "AIGC判别依据", "叙事编排",
                "情感曲线", "叙事元数据", "叙事拓扑", "场景实体", "设备美学包",
                "同期声枚举", "分镜表", "手法去重", "上游应用统计")
OLD_SHOT_KEYS = ("镜号", "阶段", "类型阶段", "景别", "角度", "运镜", "焦段", "时长",
                 "画面焦点", "声音", "转场", "叙事目的", "色彩", "光影", "材质", "氛围",
                 "情绪", "首帧描述", "情感强度", "线", "POV", "时间线", "银幕序", "时序位",
                 "构图", "叙事标签", "节奏手记", "拓扑张力",
                 "AIGC提示词", "首帧提示词", "音频描述", "AIGC适配提示词",
                 "start", "end")
OLD_CODES = ("missing-contract-version", "invalid-contract-version",
             "missing-shot-id", "duplicate-shot-id", "invalid-duration",
             "type-mismatch", "empty-shots", "relative-ref-unknown",
             "relative-ref-cycle", "deprecated-field", "unknown-field")
NEW_CODES = ("slot-out-of-range", "slot-prompt-mismatch", "anchor-invalid")

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def _codes(rep, which="errors"):
    return sorted(set(e["code"] for e in rep[which]))


def _has_code(rep, code, which="errors"):
    return any(e["code"] == code for e in rep[which])


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 v2 版本声明")
    check("T0 STORYBOARD_CONTRACT_VERSION == 2", STORYBOARD_CONTRACT_VERSION == 2,
          f"v={STORYBOARD_CONTRACT_VERSION}")
    check("T0 合法版本集合 LEGAL_CONTRACT_VERSIONS == (1, 2)",
          LEGAL_CONTRACT_VERSIONS == (1, 2), f"got={LEGAL_CONTRACT_VERSIONS}")
    check("T0 CONTRACT_VERSION 别名 == 2", CONTRACT_VERSION == 2, f"v={CONTRACT_VERSION}")
    check("T0 诊断码全集 14 个 = 旧 11 码 + 3 新码",
          len(DIAGNOSTIC_CODES) == 14
          and set(OLD_CODES) <= set(DIAGNOSTIC_CODES)
          and set(NEW_CODES) <= set(DIAGNOSTIC_CODES)
          and set(DIAGNOSTIC_CODES) == set(OLD_CODES) | set(NEW_CODES),
          f"codes={DIAGNOSTIC_CODES}")
    check("T0 self_check() 最小样例自检通过 (v2 样例)", self_check() is True)

    # -----------------------------------------------------------------
    print("T1 v2 canonical 注册表")
    check("T1 CANON_TOP_KEYS 22 项 (19 真实键 + contract_version + 批次6 锚定库 + 条件键 _项目风格锚)",
          len(CANON_TOP_KEYS) == 22 and "锚定库" in CANON_TOP_KEYS
          and "_项目风格锚" in CANON_TOP_KEYS,
          f"n={len(CANON_TOP_KEYS)}")
    check("T1 CANON_SHOT_KEYS 37 项 (32 真实键 + start/end + 批次6 三键)",
          len(CANON_SHOT_KEYS) == 37
          and {"参考槽位", "锚定", "机位锚"} <= set(CANON_SHOT_KEYS),
          f"n={len(CANON_SHOT_KEYS)}")
    check("T1 既有 v1 键零删减 (顶层 20 项 / 每镜 34 项全保留)",
          set(OLD_TOP_KEYS) <= set(CANON_TOP_KEYS)
          and set(OLD_SHOT_KEYS) <= set(CANON_SHOT_KEYS),
          f"top_diff={sorted(set(OLD_TOP_KEYS) - set(CANON_TOP_KEYS))} "
          f"shot_diff={sorted(set(OLD_SHOT_KEYS) - set(CANON_SHOT_KEYS))}")

    # -----------------------------------------------------------------
    print("T2 v2 合法全量文档")
    v2_full = {
        "contract_version": 2,
        "分镜数": 1, "总时长秒": 2.0, "导演": "王家卫", "情绪": "孤独",
        "画面模式": "电影工作室", "故事理论": "三幕剧", "叙事结构": "单线",
        "AIGC生产模式": "文生视频", "AIGC判别依据": "自动判别",
        "叙事编排": {"方式": "跟随叙事结构"}, "情感曲线": [6.2],
        "叙事元数据": [], "叙事拓扑": {}, "场景实体": {}, "设备美学包": {},
        "同期声枚举": "雨声",
        "锚定库": {"0": {"媒体": "asset://hero_v1", "类型": "角色参考"},
                   "1": {"媒体": "asset://kitchen_v1", "类型": "场景参考"}},
        "分镜表": [{
            "镜号": 1, "时长": "2.0s", "景别": "全景", "运镜": "缓推",
            "AIGC提示词": "雨夜厨房, 父亲切菜 【参考@0】 【参考@1】",
            "参考槽位": [0, 1],
            "锚定": {"首帧": "ff-9f2a", "尾帧": "ef-7c1d", "帧数": 48},
            "机位锚": "高机位俯拍/窗口侧逆光/缓推",
        }],
        "手法去重": {"镜数": 1, "违规数": 0}, "上游应用统计": {},
    }
    rep2 = validate_storyboard(v2_full)
    n2 = rep2["normalized"]["分镜表"][0]
    check("T2 全量 v2 文档 ok=True 且零 errors/warnings (双射+库内+完整锚定)",
          rep2["ok"] is True and rep2["errors"] == [] and rep2["warnings"] == [],
          f"e={_codes(rep2)} w={_codes(rep2, 'warnings')}")
    check("T2 normalized 版本头回显文档声明 (2)",
          rep2["normalized"]["contract_version"] == 2,
          f"cv={rep2['normalized']['contract_version']}")
    check("T2 顶层 锚定库 原样保留于 normalized (canonical, 非 extra)",
          rep2["normalized"].get("锚定库") == v2_full["锚定库"]
          and "extra" not in rep2["normalized"],
          f"top={sorted(rep2['normalized'])}")
    check("T2 每镜新三键原样保留 (参考槽位/锚定/机位锚)",
          n2.get("参考槽位") == [0, 1]
          and n2.get("锚定") == {"首帧": "ff-9f2a", "尾帧": "ef-7c1d", "帧数": 48}
          and n2.get("机位锚") == "高机位俯拍/窗口侧逆光/缓推",
          f"shot={sorted(n2)}")
    check("T2 派生时间轴不受新键影响 (start_s=0.0/end_s=2.0/duration_s=2.0)",
          n2.get("start_s") == 0.0 and n2.get("end_s") == 2.0 and n2.get("duration_s") == 2.0,
          f"got=({n2.get('start_s')},{n2.get('end_s')},{n2.get('duration_s')})")

    # -----------------------------------------------------------------
    print("T3 slot-prompt-mismatch 正/负样本")
    neg3 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "雨夜便利店 【参考@0】",
         "参考槽位": [1]}]})
    check("T3 负样本: 标签{0} ≠ 槽位{1} → slot-prompt-mismatch",
          _has_code(neg3, "slot-prompt-mismatch") and neg3["ok"] is False,
          f"e={_codes(neg3)}")
    check("T3 负样本 field 精确到 镜内键 分镜表[0].参考槽位",
          any(e["code"] == "slot-prompt-mismatch" and e["field"] == "分镜表[0].参考槽位"
              for e in neg3["errors"]), f"errs={neg3['errors']}")
    check("T3 负样本不误报越界 (无锚定库 → 库大小未知不判)",
          not _has_code(neg3, "slot-out-of-range"), f"e={_codes(neg3)}")
    pos3 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "雨夜便利店 【参考@0】",
         "参考槽位": [0]}]})
    check("T3 正样本: 标签{0} == 槽位{0} → 零新码",
          pos3["ok"] is True and not _has_code(pos3, "slot-prompt-mismatch"),
          f"e={_codes(pos3)}")
    dup3 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】 【参考@0】",
         "参考槽位": [0]}]})
    check("T3 集合语义: 重复标签去重后双射成立 → 零新码",
          dup3["ok"] is True and not _has_code(dup3, "slot-prompt-mismatch"),
          f"e={_codes(dup3)}")
    noprompt3 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "参考槽位": [0]}]})
    check("T3 负样本: 有槽位无 prompt 标签 → slot-prompt-mismatch (诚实缺口)",
          _has_code(noprompt3, "slot-prompt-mismatch"), f"e={_codes(noprompt3)}")

    # -----------------------------------------------------------------
    print("T4 slot-out-of-range 正/负样本")
    lib1 = {"0": {"媒体": "asset://a"}}
    neg4 = validate_storyboard({"contract_version": 2, "锚定库": lib1, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@3】", "参考槽位": [3]}]})
    check("T4 负样本: 库大小 1 而槽位 3 (双射成立) → 仅 slot-out-of-range",
          _has_code(neg4, "slot-out-of-range")
          and not _has_code(neg4, "slot-prompt-mismatch") and neg4["ok"] is False,
          f"e={_codes(neg4)}")
    neg4b = validate_storyboard({"contract_version": 2, "锚定库": lib1, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】", "参考槽位": [0, -1]}]})
    check("T4 负样本: 负数槽位 -1 → slot-out-of-range",
          _has_code(neg4b, "slot-out-of-range"), f"e={_codes(neg4b)}")
    pos4 = validate_storyboard({"contract_version": 2, "锚定库": lib1, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】", "参考槽位": [0]}]})
    check("T4 正样本: 槽位 0 ∈ [0, 1) → 零新码",
          pos4["ok"] is True and not _has_code(pos4, "slot-out-of-range"),
          f"e={_codes(pos4)}")
    unk4 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@99】", "参考槽位": [99]}]})
    check("T4 库大小未知 (无 锚定库) → 只查集合一致性, 不判越界, ok=True",
          unk4["ok"] is True and not _has_code(unk4, "slot-out-of-range")
          and not _has_code(unk4, "slot-prompt-mismatch"), f"e={_codes(unk4)}")
    badlib4 = validate_storyboard({"contract_version": 2, "锚定库": "不是字典",
                                   "分镜表": [
                                       {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@9】",
                                        "参考槽位": [9]}]})
    check("T4 锚定库非 dict → type-mismatch 且库大小未知不判越界",
          _has_code(badlib4, "type-mismatch")
          and not _has_code(badlib4, "slot-out-of-range"), f"e={_codes(badlib4)}")
    empty4 = validate_storyboard({"contract_version": 2, "锚定库": {}, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】", "参考槽位": [0]}]})
    check("T4 空锚定库 (大小 0) → 任何槽位越界",
          _has_code(empty4, "slot-out-of-range"), f"e={_codes(empty4)}")
    # R1 MED-4: 非整数槽位元素 — 库在场与否一律 slot-prompt-mismatch, 消息指明非法元素
    ill4 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】", "参考槽位": [0, "x"]}]})
    check("T4 负样本: 非整值槽位元素 (无库) → slot-prompt-mismatch 指明非法元素 (MED-4)",
          _has_code(ill4, "slot-prompt-mismatch") and ill4["ok"] is False
          and any("非整数槽位元素" in e.get("message", "") for e in ill4["errors"]),
          f"e={_codes(ill4)}")
    ill4b = validate_storyboard({"contract_version": 2, "锚定库": lib1, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】", "参考槽位": [0, True]}]})
    check("T4 负样本: bool 槽位元素 (有库) → slot-prompt-mismatch (MED-4)",
          _has_code(ill4b, "slot-prompt-mismatch"), f"e={_codes(ill4b)}")
    # R1 LOW-10: 稀疏键库大小 = 整数键最大值+1 (键 5 真实存在不误报)
    lib6 = {"0": {"媒体": "asset://a"}, "5": {"媒体": "asset://b"}}
    sp4 = validate_storyboard({"contract_version": 2, "锚定库": lib6, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】 【参考@5】", "参考槽位": [0, 5]}]})
    check("T4 稀疏键锚定库 {0,5} → 槽位 5 不误报越界 (库大小=max键+1, LOW-10)",
          sp4["ok"] is True and not _has_code(sp4, "slot-out-of-range"), f"e={_codes(sp4)}")

    # -----------------------------------------------------------------
    print("T5 anchor-invalid 正/负样本")
    for tag, anch in (("缺首帧", {"尾帧": "e", "帧数": 4}),
                      ("缺尾帧", {"首帧": "f", "帧数": 4}),
                      ("帧数为 0", {"首帧": "f", "尾帧": "e", "帧数": 0}),
                      ("帧数为负", {"首帧": "f", "尾帧": "e", "帧数": -2}),
                      ("帧数缺失", {"首帧": "f", "尾帧": "e"}),
                      ("帧数为 bool", {"首帧": "f", "尾帧": "e", "帧数": True}),
                      ("块为非 dict", "雨夜首帧")):
        rep5 = validate_storyboard({"contract_version": 2, "分镜表": [
            {"镜号": 1, "时长": 2.0, "锚定": anch}]})
        check(f"T5 负样本 ({tag}) → anchor-invalid",
              _has_code(rep5, "anchor-invalid") and rep5["ok"] is False,
              f"e={_codes(rep5)}")
    neg5c = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "锚定": "雨夜首帧"}]})
    check("T5 非 dict 锚定块单通道 anchor-invalid (不与 type-mismatch 双报)",
          _codes(neg5c) == ["anchor-invalid"], f"e={_codes(neg5c)}")
    pos5 = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "锚定": {"首帧": "f", "尾帧": "e", "帧数": 48}}]})
    check("T5 正样本: 完整锚定块 {首帧,尾帧,帧数>0} → 零新码",
          pos5["ok"] is True and not _has_code(pos5, "anchor-invalid"),
          f"e={_codes(pos5)}")

    # -----------------------------------------------------------------
    print("T6 v1 文件诊断零增量 (无新键 → 新码结构性不可触发)")
    v1_clean = {"contract_version": 1, "分镜表": [{"镜号": 1, "时长": 2.0}]}
    rep6a = validate_storyboard(v1_clean)
    check("T6 合法 v1 文件 ok=True 零 errors/warnings",
          rep6a["ok"] is True and rep6a["errors"] == [] and rep6a["warnings"] == [],
          f"e={_codes(rep6a)} w={_codes(rep6a, 'warnings')}")
    v1_tag = {"contract_version": 1, "分镜表": [
        {"镜号": 1, "时长": 2.0, "AIGC提示词": "x 【参考@0】 【参考@7】"}]}
    rep6b = validate_storyboard(v1_tag)
    check("T6 v1 文件带 prompt 标签但无 参考槽位/锚定库 → 零新码 (结构保障)",
          rep6b["ok"] is True and not (_codes(rep6b) and set(_codes(rep6b)) & set(NEW_CODES)),
          f"e={_codes(rep6b)}")
    v1_err = {"contract_version": 1, "分镜表": [{"镜号": 1, "时长": -5.5}]}
    rep6c = validate_storyboard(v1_err)
    check("T6 v1 既有错误仍走原通道 (invalid-duration), 无新码混入",
          _codes(rep6c) == ["invalid-duration"], f"e={_codes(rep6c)}")

    # -----------------------------------------------------------------
    print("T7 v1 零漂移 (golden fixture 真实 v1 文档)")
    golden_path = os.path.join(HERE, "golden", "golden_storyboard.json")
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_expect = json.load(f).get("expect") or {}
    rep7 = validate_storyboard(golden_expect)
    check("T7 golden v1 fixture (真实 20 顶层键/8 镜) validate ok=True 零 errors",
          rep7["ok"] is True and rep7["errors"] == [], f"e={_codes(rep7)}")
    check("T7 golden v1 fixture 零 warnings (无 unknown/deprecated 误报)",
          rep7["warnings"] == [], f"w={_codes(rep7, 'warnings')}")
    check("T7 golden v1 fixture normalized 版本头回显 1 (零漂移)",
          rep7["normalized"]["contract_version"] == 1,
          f"cv={rep7['normalized']['contract_version']}")
    review_fixture = json.dumps({
        "contract_version": 1, "分镜数": 2, "总时长秒": 8.0,
        "导演": "[电影] 王家卫", "情绪": "孤独", "画面模式": "电影工作室",
        "分镜表": [
            {"镜号": 1, "时长": "4.0s", "景别": "全景", "运镜": "固定",
             "画面焦点": "便利店霓虹", "声音": "雨声", "转场": "硬切",
             "叙事目的": "建立场景", "首帧描述": "雨夜便利店门口全景",
             "AIGC提示词": "雨夜便利店门口全景, 霓虹灯反射在湿漉漉的路面"},
            {"镜号": 2, "时长": 4.0, "景别": "特写", "运镜": "推镜",
             "画面焦点": "玻璃雨珠", "声音": "雨声渐弱", "转场": "叠化",
             "叙事目的": "情绪特写", "首帧描述": "玻璃雨珠特写",
             "AIGC提示词": "玻璃雨珠特写, 霓虹光斑缓慢滑落"}],
    })
    rep7b = validate_storyboard(json.loads(review_fixture))
    check("T7 Review 扫描用 v1 fixture (test_all_modes 同构) 照常 ok 零诊断",
          rep7b["ok"] is True and rep7b["errors"] == [] and rep7b["warnings"] == [],
          f"e={_codes(rep7b)} w={_codes(rep7b, 'warnings')}")

    # -----------------------------------------------------------------
    print("T8 版本集合边界")
    for tag, cv, want_ok in (("1", 1, True), ("2", 2, True),
                             ("3", 3, False), ("字符串", "1", False),
                             ("bool", True, False)):
        rep8 = validate_storyboard({"contract_version": cv,
                                    "分镜表": [{"镜号": 1, "时长": 1.0}]})
        bad = _has_code(rep8, "invalid-contract-version")
        check(f"T8 contract_version={tag!r} → {'放行' if want_ok else 'invalid-contract-version'}",
              bad == (not want_ok) and rep8["ok"] is want_ok, f"e={_codes(rep8)}")
    rep8m = validate_storyboard({"分镜表": [{"镜号": 1, "时长": 1.0}]})
    check("T8 缺失版本头 → missing-contract-version (口径不变)",
          _has_code(rep8m, "missing-contract-version")
          and not _has_code(rep8m, "invalid-contract-version"), f"e={_codes(rep8m)}")

    # -----------------------------------------------------------------
    print("T9 attach_contract_version 语义")
    d9a = {}
    check("T9 空对象 → 盖生产链兼容章 1", attach_contract_version(d9a) is d9a
          and d9a.get("contract_version") == 1, f"d={d9a}")
    d9b = {"contract_version": 2, "分镜表": []}
    _keys9 = list(d9b.keys())
    attach_contract_version(d9b)
    check("T9 已是合法 2 → 原样保留 (v2 产物自行声明, 键序不动)",
          d9b.get("contract_version") == 2 and list(d9b.keys()) == _keys9, f"d={d9b}")
    d9c = {"contract_version": 1}
    attach_contract_version(d9c)
    check("T9 已是合法 1 → 不动 (幂等)", d9c.get("contract_version") == 1)
    check("T9 非法值 (bool True / 3 / \"2\") → 覆盖为 1",
          attach_contract_version({"contract_version": True})["contract_version"] == 1
          and attach_contract_version({"contract_version": 3})["contract_version"] == 1
          and attach_contract_version({"contract_version": "2"})["contract_version"] == 1)
    keep9 = [1, 2]
    check("T9 非 dict 输入原样返回不抛", attach_contract_version(keep9) is keep9
          and attach_contract_version(None) is None)

    # -----------------------------------------------------------------
    print("T10 新键类型通道与 extra 语义")
    rep10a = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "参考槽位": "0,1"}]})
    check("T10 参考槽位 非 list → type-mismatch (且不触发 slot 新码)",
          _has_code(rep10a, "type-mismatch")
          and not _has_code(rep10a, "slot-prompt-mismatch")
          and not _has_code(rep10a, "slot-out-of-range"), f"e={_codes(rep10a)}")
    rep10b = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "机位锚": 123}]})
    check("T10 机位锚 非 str → type-mismatch",
          _has_code(rep10b, "type-mismatch")
          and any(e["field"] == "分镜表[0].机位锚" for e in rep10b["errors"]),
          f"e={_codes(rep10b)}")
    rep10c = validate_storyboard({"contract_version": 2, "分镜表": [
        {"镜号": 1, "时长": 2.0, "参考槽位": [0], "锚定": {"首帧": "f", "尾帧": "e",
                                                          "帧数": 1},
         "机位锚": "缓推", "自定义字段": "x"}]})
    unk10 = [w for w in rep10c["warnings"] if w["code"] == "unknown-field"]
    check("T10 v2 新键入 canonical 后不再进 extra (unknown-field 仅报真未知键)",
          len(unk10) == 1 and unk10[0]["field"] == "分镜表[0].自定义字段"
          and "extra" in rep10c["normalized"]["分镜表"][0]
          and "参考槽位" not in rep10c["normalized"]["分镜表"][0].get("extra", {}),
          f"w={[(w['field']) for w in unk10]}")


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    print(f"\n契约 v2 测试结果: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
