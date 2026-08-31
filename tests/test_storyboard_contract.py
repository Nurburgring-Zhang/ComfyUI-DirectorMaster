# -*- coding: utf-8 -*-
"""
批次2 — 《DM 分镜 JSON 契约 v1》契约测试 (tests/test_storyboard_contract.py)
=============================================================================
覆盖矩阵:
  T1  合法最小结构 (ok + 派生 start_s/end_s/duration_s)
  T2  合法全量结构 (14 顶层 + 28 每镜 canonical 全保留)
  T3  contract_version 注入与幂等 (空对象/已有1/非法值覆盖/非dict安全)
  T4  legacy 键映射 + deprecated-field 警告
  T5  相对引用字典形态 {"ref","op","offset_s"} (start_s/end_s 计算值断言)
  T6  相对引用字符串形态 "<shot_id>±<float>s" (含字符串镜号引用)
  T7  未知引用 relative-ref-unknown (回退链式)
  T8  环检测 relative-ref-cycle (A→B→A, 有界完成)
  T9  重复 shot_id
  T10 缺失 shot_id
  T11 invalid-duration (坏字符串/负数/零/bool + 合法三形态)
  T12 empty-shots (空表 / 缺失分镜表)
  T13 unknown-field 警告 + 值保留 normalized.extra (顶层/镜内/排序确定)
  T14 type-mismatch (版本头/分镜表/镜对象/数值字段)
  T15 宽容解析 parse_storyboard_json (围栏/噪声尾逗号/截断→None 不抛)
  T16 normalize 确定性 (键序打乱 → 输出逐字节一致)
  T17 真实 Cinematic 集成 (真 build + 固定输入 → contract_version==1 且 validate ok,
      顶层键集合 == 接线前真实结构 + contract_version)
  T18 接线前后对比 (git show HEAD 快照动态 import 旧版 → 差异=仅新增 contract_version,
      分镜文本逐字一致; 临时文件落 scratch/系统临时目录, 不进仓库)
  T19 接线诚实上报 (注入不一致 → stderr 告警且节点不失败; 校验器抛异常 → 降级告警
      且节点不失败; 真实产物零误报)
  T20 前镜时长断裂链式传递 (M-1 回归: start_s=None 加法守卫 → 不抛异常/无
      internal-error/诚实链断 end_s=None/警告零新增)

证据存档: tests/storyboard_contract_results.json (固定字段, 无时间戳, 重跑字节稳定)。
退出码: 0 = 全部通过, 1 = 有失败。
"""
import contextlib
import copy as _copy
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.storyboard_contract import (
    STORYBOARD_CONTRACT_VERSION, CONTRACT_VERSION, DIAGNOSTIC_CODES,
    CANON_TOP_KEYS, CANON_SHOT_KEYS, DERIVED_KEYS,
    attach_contract_version, validate_storyboard, parse_storyboard_json, self_check,
)

PASS, FAIL = 0, 0
RESULTS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        RESULTS.append({"label": label, "ok": True, "detail": str(detail)[:300]})
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        RESULTS.append({"label": label, "ok": False, "detail": str(detail)[:300]})
        print(f"  [FAIL] {label} {detail}")


def _codes(rep, which="errors"):
    return sorted(set(e["code"] for e in rep[which]))


def _has_code(rep, code, which="errors"):
    return any(e["code"] == code for e in rep[which])


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 契约头常量")
    check("T0 STORYBOARD_CONTRACT_VERSION == 1", STORYBOARD_CONTRACT_VERSION == 1,
          f"v={STORYBOARD_CONTRACT_VERSION}")
    check("T0 CONTRACT_VERSION 别名 == 1 (doctor 口径)", CONTRACT_VERSION == 1,
          f"v={CONTRACT_VERSION}")
    check("T0 诊断码全集 11 个且含环/未知引用/废弃/未知键",
          len(DIAGNOSTIC_CODES) == 11
          and {"relative-ref-cycle", "relative-ref-unknown", "deprecated-field",
               "unknown-field", "duplicate-shot-id", "invalid-duration",
               "empty-shots", "type-mismatch", "missing-contract-version",
               "invalid-contract-version", "missing-shot-id"} <= set(DIAGNOSTIC_CODES),
          f"codes={DIAGNOSTIC_CODES}")
    check("T0 self_check() 最小样例自检通过", self_check() is True)

    # -----------------------------------------------------------------
    print("T1 合法最小结构")
    rep1 = validate_storyboard({"contract_version": 1,
                                "分镜表": [{"镜号": 1, "时长": "3s"}]})
    n1 = rep1["normalized"]["分镜表"][0]
    check("T1 ok=True 且零 errors", rep1["ok"] is True and rep1["errors"] == [],
          f"rep={_codes(rep1)}")
    check("T1 零 warnings", rep1["warnings"] == [], f"w={rep1['warnings']}")
    check("T1 首镜派生 start_s=0.0 / end_s=3.0",
          n1["start_s"] == 0.0 and n1["end_s"] == 3.0, f"got=({n1['start_s']},{n1['end_s']})")
    check("T1 派生 duration_s=3.0 (时长数值化)", n1["duration_s"] == 3.0,
          f"got={n1['duration_s']}")
    check("T1 normalized 顶层含 contract_version 且 normalized['分镜表'] 存在",
          rep1["normalized"]["contract_version"] == 1
          and isinstance(rep1["normalized"]["分镜表"], list))
    check("T1 derived 三键齐备", set(DERIVED_KEYS) <= set(n1.keys()), f"keys={sorted(n1)}")

    # -----------------------------------------------------------------
    print("T2 合法全量结构 (19 顶层 + 32 每镜 canonical, 含 V16.4/V16.5 增量键与批次3 手法去重)")
    full_shot = {k: v for k, v in {
        "镜号": 1, "阶段": "建置", "类型阶段": "开场", "景别": "全景", "角度": "平视",
        "运镜": "缓推", "焦段": "35mm", "时长": "3.8s", "画面焦点": "父亲的手",
        "声音": "环境底噪", "转场": "硬切", "叙事目的": "建立空间", "色彩": "冷灰",
        "光影": "低照度", "材质": "金属", "氛围": "压抑", "情绪": "孤独",
        "首帧描述": "厨房夜景", "情感强度": 6.2, "线": "A", "POV": "主角 POV",
        "时间线": "现在", "银幕序": 1, "时序位": 1, "构图": "三分法",
        "叙事标签": "波浪上行", "节奏手记": "呼吸感手持", "拓扑张力": 6,
        "AIGC提示词": "prompt-body",
        "首帧提示词": "ff-body", "音频描述": "audio-body", "AIGC适配提示词": "adapt-body",
    }.items()}
    full = {"contract_version": 1, "分镜数": 1, "总时长秒": 3.8, "导演": "王家卫",
            "情绪": "孤独", "画面模式": "电影工作室", "故事理论": "三幕剧",
            "叙事结构": "单线", "AIGC生产模式": "文生视频", "AIGC判别依据": "自动判别",
            "叙事编排": {"方式": "跟随叙事结构", "字幕位": []}, "情感曲线": [6.2],
            "叙事元数据": [{"line": "A", "pov": "全知", "timeline": "现在"}],
            "叙事拓扑": {"结构": "波浪式", "反转点": []}, "场景实体": {"角色": []},
            "设备美学包": {"摄影机": "ARRICAM"}, "同期声枚举": "雨声, 缆绳吱呀",
            "分镜表": [full_shot],
            "手法去重": {"校验口径": "同一运镜词/构图模板不得连续两镜当镜头主角",
                         "镜数": 1, "违规数": 0, "运镜违规": [], "构图违规": []},
            "上游应用统计": {"剧本": "已应用"}}
    rep2 = validate_storyboard(full)
    n2 = rep2["normalized"]["分镜表"][0]
    check("T2 全量结构 ok=True 且零 errors/warnings",
          rep2["ok"] is True and rep2["errors"] == [] and rep2["warnings"] == [],
          f"e={_codes(rep2)} w={_codes(rep2, 'warnings')}")
    check("T2 32 个每镜 canonical 键全保留于 normalized",
          set(full_shot.keys()) <= set(n2.keys()),
          f"missing={sorted(set(full_shot.keys()) - set(n2.keys()))}")
    check("T2 19 顶层键全保留 (含 contract_version 与批次3 手法去重)",
          set(CANON_TOP_KEYS) <= set(rep2["normalized"].keys()),
          f"missing={sorted(set(CANON_TOP_KEYS) - set(rep2['normalized'].keys()))}")
    check("T2 手法去重 dict 原样保留于 normalized 顶层 (批次3 增量键入注册表, 非 extra)",
          rep2["normalized"].get("手法去重") == full["手法去重"],
          f"got={rep2['normalized'].get('手法去重')!r:.120}")
    check("T2 数值字段类型原样保留 (情感强度 float / 银幕序 int)",
          n2["情感强度"] == 6.2 and n2["银幕序"] == 1)

    # -----------------------------------------------------------------
    print("T3 contract_version 注入与幂等")
    d3a = {}
    r1_ = attach_contract_version(d3a)
    check("T3 空对象注入 contract_version=1 且返回原对象",
          r1_ is d3a and d3a.get("contract_version") == 1)
    attach_contract_version(d3a)
    attach_contract_version(d3a)
    check("T3 幂等: 重复注入值仍 1 且不新增键", d3a.get("contract_version") == 1
          and len(d3a) == 1, f"d3a={d3a}")
    d3b = {"contract_version": 1, "分镜表": []}
    _keys_before = list(d3b.keys())
    attach_contract_version(d3b)
    check("T3 已有合法 1 → 不动 (键序不变)",
          list(d3b.keys()) == _keys_before and d3b["contract_version"] == 1)
    d3c = attach_contract_version({"contract_version": 2})
    d3d = attach_contract_version({"contract_version": True})
    check("T3 非法值 (2 / bool True) 盖章覆盖为 1",
          d3c["contract_version"] == 1 and d3d["contract_version"] == 1,
          f"c={d3c} d={d3d}")
    keep = [1, 2]
    check("T3 非 dict 输入原样返回不抛", attach_contract_version(keep) is keep
          and attach_contract_version(None) is None)

    # -----------------------------------------------------------------
    print("T4 legacy 键映射 + deprecated 警告")
    rep4 = validate_storyboard({"contract_version": 1, "shots": [
        {"shot_id": "S1", "duration_s": 2.5, "transition": "硬切"}]})
    n4 = rep4["normalized"]["分镜表"][0]
    dep4 = [w for w in rep4["warnings"] if w["code"] == "deprecated-field"]
    check("T4 4 条 deprecated-field 警告 (shots/shot_id/duration_s/transition)",
          len(dep4) == 4, f"w={[(w['field']) for w in dep4]}")
    check("T4 ok=True (legacy 仅为警告不阻断)", rep4["ok"] is True)
    check("T4 映射后 镜号='S1' / 时长=2.5 / 转场='硬切'",
          n4["镜号"] == "S1" and n4["时长"] == 2.5 and n4["转场"] == "硬切",
          f"n4={n4}")
    check("T4 normalized 中旧键不再残留",
          "shot_id" not in n4 and "duration_s" not in str(sorted(set(n4) - set(DERIVED_KEYS) - {"extra"}))
          and "shots" not in rep4["normalized"], f"top={sorted(rep4['normalized'])}")
    check("T4 legacy 派生时间轴正确 (start_s=0.0/end_s=2.5)",
          n4["start_s"] == 0.0 and n4["end_s"] == 2.5)

    # -----------------------------------------------------------------
    print("T5/T6 相对引用两形态")
    rel_shots = [
        {"镜号": 1, "时长": "3.0s"},
        {"镜号": 2, "时长": 2.0, "start": {"ref": 1, "op": "+", "offset_s": 1.5}},
        {"镜号": "S3", "时长": 1.0, "start": "2-0.5s"},
        {"镜号": 4, "时长": 0.5, "start": "S3+1s"},
    ]
    rep5 = validate_storyboard({"contract_version": 1, "分镜表": rel_shots})
    n5 = rep5["normalized"]["分镜表"]
    check("T5 混合两形态 ok=True 零 errors", rep5["ok"] is True and rep5["errors"] == [],
          f"e={_codes(rep5)}")
    check("T5 字典形态: 镜2 start = 镜1 end + 1.5 = 4.5", n5[1]["start_s"] == 4.5,
          f"got={n5[1]['start_s']}")
    check("T5 字典形态: 镜2 end = start + dur = 6.5", n5[1]["end_s"] == 6.5,
          f"got={n5[1]['end_s']}")
    check("T5 '-' 偏移: 镜3 start = 镜2 end - 0.5 = 6.0", n5[2]["start_s"] == 6.0,
          f"got={n5[2]['start_s']}")
    check("T6 字符串形态 '2-0.5s' 与字典形态等值 (镜3=6.0)", n5[2]["start_s"] == 6.0)
    check("T6 字符串镜号引用 'S3+1s': 镜4 start = S3 end + 1 = 8.0",
          n5[3]["start_s"] == 8.0, f"got={n5[3]['start_s']}")
    check("T6 无显式 start 的镜1 仍链式 (0.0) 且镜4 end=start+dur=8.5",
          n5[0]["start_s"] == 0.0 and n5[3]["end_s"] == 8.5,
          f"got=({n5[0]['start_s']},{n5[3]['end_s']})")

    # -----------------------------------------------------------------
    print("T7 未知引用")
    rep7 = validate_storyboard({"contract_version": 1, "分镜表": [
        {"镜号": 1, "时长": 3.0},
        {"镜号": 2, "时长": 1.0, "start": {"ref": 99, "op": "+", "offset_s": 2}}]})
    check("T7 relative-ref-unknown 进 errors", _has_code(rep7, "relative-ref-unknown"),
          f"e={_codes(rep7)}")
    check("T7 ok=False", rep7["ok"] is False)
    n7 = rep7["normalized"]["分镜表"]
    check("T7 未知引用镜回退链式 (start=3.0/end=4.0)",
          n7[1]["start_s"] == 3.0 and n7[1]["end_s"] == 4.0,
          f"got=({n7[1]['start_s']},{n7[1]['end_s']})")

    # -----------------------------------------------------------------
    print("T8 环检测 (a→b→a)")
    rep8 = validate_storyboard({"contract_version": 1, "分镜表": [
        {"镜号": "A", "时长": 1.0, "start": {"ref": "B", "op": "+", "offset_s": 0}},
        {"镜号": "B", "时长": 1.0, "start": {"ref": "A", "op": "+", "offset_s": 0}}]})
    check("T8 relative-ref-cycle 进 errors", _has_code(rep8, "relative-ref-cycle"),
          f"e={_codes(rep8)}")
    n8 = rep8["normalized"]["分镜表"]
    check("T8 环内镜回退链式 (A start=0.0, B start=1.0)",
          n8[0]["start_s"] == 0.0 and n8[1]["start_s"] == 1.0,
          f"got=({n8[0]['start_s']},{n8[1]['start_s']})")
    check("T8 有界完成且 normalized 完整 (不抛异常/不死循环)",
          isinstance(rep8["normalized"], dict) and len(rep8["normalized"]["分镜表"]) == 2)

    # -----------------------------------------------------------------
    print("T9/T10 镜号缺失与重复")
    rep9 = validate_storyboard({"contract_version": 1, "分镜表": [
        {"镜号": 1, "时长": 1.0}, {"镜号": 1, "时长": 1.0}, {"镜号": "1", "时长": 1.0}]})
    dups = [e for e in rep9["errors"] if e["code"] == "duplicate-shot-id"]
    check("T9 duplicate-shot-id 报告 2 次重复 (int/str 同一镜号口径)",
          len(dups) == 2, f"dups={[(e['value'], e['message']) for e in dups]}")
    check("T9 重复报告指向首次出现下标 分镜表[0]",
          all("分镜表[0]" in e["message"] for e in dups),
          f"msgs={[e['message'] for e in dups]}")
    rep10 = validate_storyboard({"contract_version": 1, "分镜表": [
        {"时长": 1.0}, {"镜号": 2, "时长": 1.0}]})
    miss10 = [e for e in rep10["errors"] if e["code"] == "missing-shot-id"]
    check("T10 missing-shot-id 报于缺失镜 (仅 1 条, 不误伤后续镜)",
          len(miss10) == 1 and "分镜表[0]" in miss10[0]["field"],
          f"miss={miss10}")

    # -----------------------------------------------------------------
    print("T11 invalid-duration")
    base = {"contract_version": 1, "分镜表": [{"镜号": 1, "时长": "3.8s"},
                                              {"镜号": 2, "时长": 2},
                                              {"镜号": 3, "时长": 0.5}]}
    rep11 = validate_storyboard(base)
    check("T11 合法三形态 (\"3.8s\"/int/float) 零错误且 duration_s 正确",
          rep11["ok"] is True
          and [s["duration_s"] for s in rep11["normalized"]["分镜表"]] == [3.8, 2.0, 0.5],
          f"e={_codes(rep11)}")
    for bad, tag in (("abc", "坏字符串"), (-1, "负数"), (0, "零"), (True, "bool")):
        repb = validate_storyboard({"contract_version": 1,
                                    "分镜表": [{"镜号": 1, "时长": bad}]})
        check(f"T11 invalid-duration ({tag}: {bad!r})",
              _has_code(repb, "invalid-duration") and not _has_code(repb, "type-mismatch"),
              f"e={_codes(repb)}")

    # -----------------------------------------------------------------
    print("T12 empty-shots")
    rep12a = validate_storyboard({"contract_version": 1, "分镜表": []})
    check("T12 空分镜表 → empty-shots 且 ok=False",
          _has_code(rep12a, "empty-shots") and rep12a["ok"] is False)
    rep12b = validate_storyboard({"contract_version": 1})
    check("T12 缺失分镜表 → type-mismatch (非 empty-shots)",
          _has_code(rep12b, "type-mismatch") and not _has_code(rep12b, "empty-shots"),
          f"e={_codes(rep12b)}")

    # -----------------------------------------------------------------
    print("T13 unknown-field 警告 + extra 保留")
    rep13 = validate_storyboard({"contract_version": 1, "project": "夜曲",
                                 "分镜表": [{"镜号": 1, "时长": 1.0, "自定义字段": "v2"}]})
    unk13 = [w for w in rep13["warnings"] if w["code"] == "unknown-field"]
    check("T13 顶层+镜内 unknown-field 各 1 条警告", len(unk13) == 2,
          f"w={[(w['field']) for w in unk13]}")
    check("T13 顶层值保留 normalized.extra (project='夜曲')",
          rep13["normalized"].get("extra", {}).get("project") == "夜曲",
          f"extra={rep13['normalized'].get('extra')}")
    check("T13 镜内值保留镜内 extra",
          rep13["normalized"]["分镜表"][0]["extra"].get("自定义字段") == "v2")
    rep13b = validate_storyboard({"contract_version": 1, "zz": 1, "aa": 2,
                                  "分镜表": [{"镜号": 1, "时长": 1.0}]})
    check("T13 extra 键排序确定 (aa 在 zz 前)",
          list(rep13b["normalized"]["extra"].keys()) == ["aa", "zz"],
          f"keys={list(rep13b['normalized']['extra'].keys())}")

    # -----------------------------------------------------------------
    print("T14 type-mismatch")
    rep14a = validate_storyboard({"contract_version": "1", "分镜表": []})
    check("T14 字符串版本头 → invalid-contract-version",
          _has_code(rep14a, "invalid-contract-version"), f"e={_codes(rep14a)}")
    rep14b = validate_storyboard({"contract_version": 1, "分镜表": "x"})
    check("T14 分镜表非列表 → type-mismatch", _has_code(rep14b, "type-mismatch"))
    rep14c = validate_storyboard({"contract_version": 1, "分镜表": ["不是字典"]})
    check("T14 镜非 dict → type-mismatch 且 normalized 原样保留",
          _has_code(rep14c, "type-mismatch")
          and rep14c["normalized"]["分镜表"] == ["不是字典"])
    rep14d = validate_storyboard({"contract_version": 1, "分镜表": [
        {"镜号": 1, "时长": 1.0, "情感强度": "高"}]})
    check("T14 数值字段收字符串 → type-mismatch (field 精确到镜内键)",
          _has_code(rep14d, "type-mismatch")
          and any(e["field"] == "分镜表[0].情感强度" for e in rep14d["errors"]),
          f"e={[(e['field']) for e in rep14d['errors']]}")
    rep14e = validate_storyboard({"contract_version": 1, "分镜表": [
        {"镜号": 1, "时长": 1.0, "start": "1++x"}]})
    check("T14 畸形相对表达式 → type-mismatch (不抛异常)",
          _has_code(rep14e, "type-mismatch")
          and not _has_code(rep14e, "relative-ref-unknown"), f"e={_codes(rep14e)}")

    # -----------------------------------------------------------------
    print("T15 宽容解析 parse_storyboard_json")
    obj15a, w15a = parse_storyboard_json("```json\n{\"contract_version\": 1, \"分镜表\": []}\n```")
    check("T15 围栏 JSON 抢救为 dict 且零警告",
          isinstance(obj15a, dict) and obj15a.get("contract_version") == 1 and w15a == [],
          f"r={obj15a} w={w15a}")
    obj15b, w15b = parse_storyboard_json("模型前置噪声 {\"a\": [1,2,]} 尾随噪声")
    check("T15 前后噪声+尾逗号抢救", obj15b == {"a": [1, 2]} and w15b == [],
          f"r={obj15b}")
    try:
        obj15c, w15c = parse_storyboard_json("{\"contract_version\": 1, \"分镜表\": [{\"镜号\": 1")
        trunc_ok = obj15c is None and len(w15c) == 1
    except Exception as e15:  # pragma: no cover
        trunc_ok = False
        w15c = [str(e15)]
    check("T15 截断文本 → (None, 1 条诊断) 永不抛", trunc_ok, f"w={w15c}")
    obj15d, w15d = parse_storyboard_json(None)
    obj15e, w15e = parse_storyboard_json("纯文本无JSON")
    check("T15 None/纯文本 → (None, 非空诊断)",
          obj15d is None and len(w15d) == 1 and obj15e is None and len(w15e) == 1,
          f"d={w15d} e={w15e}")
    check("T15 围栏产物可直接进 validate_storyboard",
          validate_storyboard(obj15a)["ok"] is False
          and _has_code(validate_storyboard(obj15a), "empty-shots"))

    # -----------------------------------------------------------------
    print("T16 normalize 确定性")
    da = {"contract_version": 1, "分镜数": 1,
          "分镜表": [{"镜号": 1, "时长": 1.0, "zz": 1, "aa": 2}]}
    db = {"分镜数": 1, "分镜表": [{"zz": 1, "时长": 1.0, "aa": 2, "镜号": 1}],
          "contract_version": 1}
    ra, rb = validate_storyboard(da), validate_storyboard(db)
    ja = json.dumps(ra["normalized"], ensure_ascii=False, sort_keys=False)
    jb = json.dumps(rb["normalized"], ensure_ascii=False, sort_keys=False)
    check("T16 键序打乱 → normalized 输出逐字节一致", ja == jb, f"a={ja[:120]} b={jb[:120]}")
    ra2 = validate_storyboard(_copy.deepcopy(da))
    check("T16 同输入重复校验 → 输出逐字节一致 (含 errors/warnings)",
          json.dumps(ra, ensure_ascii=False, sort_keys=True)
          == json.dumps(ra2, ensure_ascii=False, sort_keys=True))

    # -----------------------------------------------------------------
    print("T17-T19 真实 Cinematic 集成")
    from aggregator.cinematic_studio import DirectorMasterCinematic
    BUILD_KWARGS = {
        "画面模式": "电影工作室", "启用反AI规则": True,
        "景别偏好": "无(默认)", "运镜风格": "无(默认)", "焦段偏好": "无(默认)",
        "构图法则": "无(默认)", "剪辑节奏": "无(默认)", "运镜风格_多选": "",
        "核心数据包": "", "剧本输入": "△ 内景 厨房 夜 △ 父亲切菜 女儿抬头",
        "创意输入": "", "美术输入": "", "声音输入": "", "角色输入": "", "资产输入": "",
        "目标时长(分钟)": 0.5, "节奏风格": "无(默认)", "直觉风险": "无(默认)",
        "叙事编排": "无(默认)", "叙事线型": "无(默认)", "AIGC生产模式": "自动判别",
    }
    node = DirectorMasterCinematic()
    _err_clean = io.StringIO()
    with contextlib.redirect_stderr(_err_clean), contextlib.redirect_stdout(io.StringIO()):
        new_main, new_json = node.build(**BUILD_KWARGS)
    new_data = json.loads(new_json)
    check("T17 产物 JSON 含 contract_version == 1",
          new_data.get("contract_version") == 1, f"cv={new_data.get('contract_version')}")
    rep17 = validate_storyboard(new_data)
    check("T17 真实产物 validate ok=True 零 errors",
          rep17["ok"] is True and rep17["errors"] == [], f"e={_codes(rep17)}")
    check("T17 真实产物零 warnings (无 unknown/deprecated 误报)",
          rep17["warnings"] == [], f"w={_codes(rep17, 'warnings')}")
    check("T17 顶层键集合 == 真实 19 键 + contract_version (零漂移, 含 V16.4/V16.5 增量键与批次3 手法去重)",
          set(new_data.keys()) == set(CANON_TOP_KEYS),
          f"diff={sorted(set(new_data.keys()) ^ set(CANON_TOP_KEYS))}")
    check("T17 每镜键集合 ⊆ 真实 32 键 (start/end 表达式键非必填)",
          set(new_data["分镜表"][0].keys()) <= set(CANON_SHOT_KEYS)
          and len(new_data["分镜表"]) > 0,
          f"diff={sorted(set(new_data['分镜表'][0].keys()) - set(CANON_SHOT_KEYS))}")
    check("T17 分镜文本输出存在且非空 (与 JSON 二元组形态不变)",
          isinstance(new_main, str) and len(new_main) > 1000,
          f"head={new_main[:16]}")  # detail 不落 len(main): 真实 build 文本长度跨进程有既有微差, 证据须零漂移
    check("T17 接线 clean 路径 stderr 零契约告警 (诚实上报不误报)",
          "分镜契约" not in _err_clean.getvalue(), f"stderr={_err_clean.getvalue()[:200]}")

    # T18 接线前后对比: git show HEAD 快照动态 import (临时文件不进仓库)
    print("T18 接线前后对比 (HEAD 快照)")
    try:
        _p = subprocess.run(["git", "show", "HEAD:aggregator/cinematic_studio.py"],
                            cwd=ROOT, capture_output=True, timeout=60)
        snap_src = _p.stdout.decode("utf-8", errors="replace") if _p.returncode == 0 else None
    except Exception:
        snap_src = None
    pre_wiring = bool(snap_src) and "storyboard_contract" not in snap_src
    if pre_wiring:
        snap_dir = os.environ.get("DM_SCRATCH_DIR") or tempfile.gettempdir()
        snap_path = os.path.join(snap_dir, "_dm_head_snapshot_cinematic_studio.py")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(snap_src)
        spec = importlib.util.spec_from_file_location(
            "aggregator._dm_head_snapshot_cine", snap_path)
        old_mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = old_mod
        spec.loader.exec_module(old_mod)
        old_node = old_mod.DirectorMasterCinematic()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            old_main, old_json = old_node.build(**BUILD_KWARGS)
        old_data = json.loads(old_json)
        check("T18 接线前快照产物无 contract_version 键",
              "contract_version" not in old_data)
        check("T18 新旧顶层键差 == 仅 {contract_version}",
              set(new_data.keys()) - set(old_data.keys()) == {"contract_version"}
              and set(old_data.keys()) - set(new_data.keys()) == set(),
              f"add={sorted(set(new_data.keys()) - set(old_data.keys()))} "
              f"del={sorted(set(old_data.keys()) - set(new_data.keys()))}")
        stripped = {k: v for k, v in new_data.items() if k != "contract_version"}
        check("T18 剥离 contract_version 后新旧数据深度相等 (值零变化)",
              stripped == old_data)
        old_shot_keys = set().union(*[set(s.keys()) for s in old_data["分镜表"]])
        new_shot_keys = set().union(*[set(s.keys()) for s in new_data["分镜表"]])
        check("T18 每镜键集合接线前后一致 (零新增零删除)",
              old_shot_keys == new_shot_keys,
              f"diff={sorted(old_shot_keys ^ new_shot_keys)}")
        check("T18 分镜文本输出逐字一致 (main 零变化)", new_main == old_main,
              f"equal={new_main == old_main}")
    else:
        check("T18 HEAD 已含接线或 git 不可用 → 降级为结构断言 (产物含契约头且结构完整)",
              new_data.get("contract_version") == 1 and "分镜表" in new_data,
              f"pre_wiring={pre_wiring}")

    # T19 接线诚实上报 (monkeypatch 侧带校验)
    print("T19 接线诚实上报")
    import aggregator.storyboard_contract as _sc
    _orig_validate = _sc.validate_storyboard
    try:
        def _fake_invalid(d):
            return {"ok": False, "errors": [{"code": "duplicate-shot-id",
                                             "field": "分镜表[1].镜号", "value": 1,
                                             "message": "测试注入"}], "warnings": []}
        _sc.validate_storyboard = _fake_invalid
        _err_incons = io.StringIO()
        with contextlib.redirect_stderr(_err_incons), contextlib.redirect_stdout(io.StringIO()):
            _m_inc, _j_inc = node.build(**BUILD_KWARGS)
        _inc_data = json.loads(_j_inc)
        check("T19 注入不一致 → stderr 诚实上报含固定前缀与诊断码",
              "[DirectorMaster] 分镜契约校验发现内部不一致" in _err_incons.getvalue()
              and "duplicate-shot-id" in _err_incons.getvalue(),
              f"stderr={_err_incons.getvalue()[:200]}")
        check("T19 注入不一致 → 节点仍正常返回完整产物 (绝不失败节点)",
              _inc_data.get("contract_version") == 1 and len(_inc_data.get("分镜表", [])) > 0
              and len(_m_inc) > 1000)

        def _boom(d):
            raise RuntimeError("boom")
        _sc.validate_storyboard = _boom
        _err_boom = io.StringIO()
        with contextlib.redirect_stderr(_err_boom), contextlib.redirect_stdout(io.StringIO()):
            _m_boom, _j_boom = node.build(**BUILD_KWARGS)
        _boom_data = json.loads(_j_boom)
        check("T19 校验器自身异常 → stderr 降级告警 (不外溢)",
              "[DirectorMaster] 分镜契约校验降级" in _err_boom.getvalue(),
              f"stderr={_err_boom.getvalue()[:200]}")
        check("T19 校验器异常 → 节点仍正常返回 (含契约头)",
              _boom_data.get("contract_version") == 1
              and isinstance(_boom_data.get("分镜表"), list))
    finally:
        _sc.validate_storyboard = _orig_validate
    check("T19 monkeypatch 恢复后真实产物校验 ok (无副作用泄漏)",
          validate_storyboard(json.loads(new_json))["ok"] is True)

    # -----------------------------------------------------------------
    print("T20 前镜时长断裂链式传递 (M-1 回归: start_s=None 加法守卫)")
    _exc20, rep20 = None, None
    try:
        rep20 = validate_storyboard({"contract_version": 1, "分镜表": [
            {"镜号": 1, "时长": "abc"}, {"镜号": 2, "时长": 2}]})
    except Exception as e20:  # pragma: no cover
        _exc20 = e20
    _errs20 = sorted(set(e["code"] for e in rep20["errors"])) if rep20 is not None else ["<exc>"]
    check("T20 最小复现 (镜1坏时长→镜2链断) 不抛异常", _exc20 is None, f"exc={_exc20!r}")
    _inv20 = [e for e in (rep20["errors"] if rep20 is not None else [])
              if e["code"] == "invalid-duration"]
    check("T20 镜1 invalid-duration 报于 分镜表[0].时长",
          len(_inv20) == 1 and _inv20[0]["field"] == "分镜表[0].时长", f"inv={_inv20}")
    check("T20 全部 error 码 ∈ 11 码集合 (无 internal-error 兜底)",
          _errs20 != ["<exc>"] and set(_errs20) <= set(DIAGNOSTIC_CODES), f"e={_errs20}")
    _n20 = (rep20 or {}).get("normalized")
    _shots20 = (_n20 or {}).get("分镜表") or []
    check("T20 normalized 非 None 且镜2 end_s=None (诚实链断)",
          _n20 is not None and len(_shots20) == 2 and _shots20[1].get("end_s") is None,
          f"shots={len(_shots20)} shot2={_shots20[1] if len(_shots20) == 2 else '?'}")
    _w20 = _codes(rep20, "warnings") if rep20 is not None else []
    check("T20 warnings 零新增 (无意外警告项)",
          rep20 is not None and rep20["warnings"] == [], f"w={_w20}")


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    _m_ver = re.search(r'version\s*=\s*"([^"]+)"',
                       open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read())
    results_doc = {
        "suite": "test_storyboard_contract",
        "version": _m_ver.group(1) if _m_ver else "unknown",
        "pass": PASS,
        "fail": FAIL,
        "results": RESULTS,
    }
    out_json = os.path.join(HERE, "storyboard_contract_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_doc, f, ensure_ascii=False, indent=2)
    print(f"\n分镜契约 v1 测试结果: {PASS} PASS / {FAIL} FAIL (证据: {out_json})")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
