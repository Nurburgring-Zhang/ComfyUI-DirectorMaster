# -*- coding: utf-8 -*-
"""
V16.7 批次3 B2 — 手法去重校验 + 卖点映射 测试 (design_batch3.md §8 / D8)
==========================================================================
运行: python tests/test_mode_dedup.py
被测 (aggregator/cinematic_studio.py additive 两段, 纯增量不改既有键):
  A. check_technique_dedup — 连续重复手法拦截 / 分散放行 / 复合词取主词 /
     连续段合并 / 只诊断不改写 / 空与畸形输入
  B. build_selling_point_map + render_selling_point_block — 全文命中 /
     显式分段 AND / 复合词切分 AND / 未覆盖返工提示 / 分隔符解析 / 渲染形态
  C. 节点集成 — 无卖点输入段缺席 / 有输入段出现 / additive 键存在性与
     既有键零增删 / 分镜表零改写 / 逐字节确定性 / 一票否决词零命中
退出码: 0 = 全部通过, 1 = 有失败
"""
import os
import sys
import json
import copy
import importlib.util

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0
ERRORS = []

# ten_rounds T10 一票否决词表 (同口径, 供 C 组扫描复用)
VETO = ["TODO", "FIXME", "placeholder", "占位符", "lorem", "masterpiece",
        "best quality", "ultra detailed", "8K", "HDR"]


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        ERRORS.append(f"{label} {detail}")
        print(f"  [FAIL] {label} {detail}")


def load_pkg(name="dm_dedup"):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


from aggregator.cinematic_studio import (check_technique_dedup, build_selling_point_map,
                                         render_selling_point_block, _split_selling_points)


def _shot(n, move, comp="", focus="", purpose=""):
    return {"n": n, "move": move, "composition": comp, "focus": focus,
            "size": "中景", "purpose": purpose}


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
    res = getattr(cls(), cls.FUNCTION)(**kw)
    return res if isinstance(res, tuple) else (res,)


print("=" * 66)
print("A. check_technique_dedup — 手法去重校验")
print("=" * 66)

# A1 连续 3 镜同运镜 → 1 条违规 (段合并), 连续镜数 3
r1 = check_technique_dedup([_shot(1, "固定"), _shot(2, "固定"), _shot(3, "固定"), _shot(4, "跟拍")])
check("A1 连续3镜同运镜→1条(段合并)", r1["违规数"] == 1 and len(r1["运镜违规"]) == 1
      and r1["运镜违规"][0]["连续镜数"] == 3 and r1["运镜违规"][0]["连续镜号"] == [1, 2, 3],
      json.dumps(r1["运镜违规"], ensure_ascii=False))

# A2 交替运镜 → 零违规
r2 = check_technique_dedup([_shot(1, "固定"), _shot(2, "跟拍"), _shot(3, "环绕")])
check("A2 分散手法放行", r2["违规数"] == 0 and r2["运镜违规"] == [] and r2["构图违规"] == [],
      json.dumps(r2, ensure_ascii=False)[:120])

# A3 断续同运镜 (不连续) → 零违规
r3 = check_technique_dedup([_shot(1, "固定"), _shot(2, "跟拍"), _shot(3, "固定")])
check("A3 非连续同运镜不违规", r3["违规数"] == 0, str(r3["违规数"]))

# A4 复合词取首段主词: 快切+推拉 与 快切 连续 → 命中 '快切'
r4 = check_technique_dedup([_shot(1, "快切+推拉"), _shot(2, "快切"), _shot(3, "跟拍")])
check("A4 复合词取主词拦截", r4["违规数"] == 1 and r4["运镜违规"][0]["手法"] == "快切",
      json.dumps(r4["运镜违规"], ensure_ascii=False))

# A5 连续 2 镜同构图模板 → 构图违规 1 条
r5 = check_technique_dedup([_shot(1, "推", "三分法构图"), _shot(2, "拉", "三分法构图")])
check("A5 连续同构图模板拦截", len(r5["构图违规"]) == 1 and r5["构图违规"][0]["手法"] == "三分法构图"
      and r5["违规数"] == 1, json.dumps(r5["构图违规"], ensure_ascii=False))

# A6 构图分散 → 零违规
r6 = check_technique_dedup([_shot(1, "推", "三分法构图"), _shot(2, "拉", "对角线构图")])
check("A6 分散构图放行", r6["违规数"] == 0, str(r6["违规数"]))

# A7 报告结构: 五个报告键 + 每条违规五字段
r7 = check_technique_dedup([_shot(1, "固定"), _shot(2, "固定")])
check("A7 报告键齐全", all(k in r7 for k in ("校验口径", "镜数", "违规数", "运镜违规", "构图违规")),
      str(sorted(r7.keys())))
v7 = (r7["运镜违规"] or r7["构图违规"])[0]
check("A7b 违规条目字段齐全", all(k in v7 for k in ("类型", "手法", "连续镜号", "连续镜数", "区间")),
      str(sorted(v7.keys())))

# A8 只诊断不改写: 输入 shots 深拷贝前后一致
shots8 = [_shot(1, "固定", "三分法构图", "雨中的码头"), _shot(2, "固定", "三分法构图", "机甲转身")]
snap8 = copy.deepcopy(shots8)
check_technique_dedup(shots8)
check("A8 只读不改写 (shots 零变更)", shots8 == snap8, "shots 被修改")

# A9 空列表 / 单镜 / 非法元素 不崩且口径诚实
r9a = check_technique_dedup([])
r9b = check_technique_dedup([_shot(1, "固定")])
r9c = check_technique_dedup([None, _shot(2, "固定"), None, _shot(4, "固定")])
check("A9 空/单镜/畸形输入不崩", r9a["镜数"] == 0 and r9a["违规数"] == 0
      and r9b["镜数"] == 1 and r9b["违规数"] == 0 and r9c["违规数"] == 1,
      f"{r9a['违规数']}/{r9b['违规数']}/{r9c['违规数']}")

print("=" * 66)
print("B. build_selling_point_map + render_selling_point_block")
print("=" * 66)

# B1 分隔符解析 (逗号/顿号/分号/换行) + 去重保序
pts = _split_selling_points("机甲, 暴雨、护盾；暴雨\n父女和解, 机甲")
check("B1 分隔符解析+去重保序", pts == ["机甲", "暴雨", "护盾", "父女和解"], str(pts))

# B2 全文命中
sp = [_shot(1, "固定", focus="暴雨中的码头, 机甲静立"), _shot(2, "跟拍", focus="厨房的灯")]
m2 = build_selling_point_map("暴雨", sp)
check("B2 全文命中", len(m2) == 1 and m2[0]["覆盖"] is True and m2[0]["命中镜号"] == [1]
      and m2[0]["首镜"] == 1, json.dumps(m2, ensure_ascii=False))

# B3 显式分段 AND (两段同镜承载)
m3 = build_selling_point_map("暴雨 码头", sp)
check("B3 显式分段AND命中", m3[0]["覆盖"] is True and m3[0]["命中镜号"] == [1],
      json.dumps(m3, ensure_ascii=False))

# B4 复合词切分 AND (机甲变身 = 机甲+变身)
m4 = build_selling_point_map("机甲变身", [_shot(1, "推", focus="机甲正要变身, 液压声")])
check("B4 复合词切分命中", m4[0]["覆盖"] is True and m4[0]["命中镜号"] == [1],
      json.dumps(m4, ensure_ascii=False))

# B5 未覆盖 → 返工提示
m5 = build_selling_point_map("父女和解", sp)
check("B5 未覆盖给返工提示", m5[0]["覆盖"] is False and m5[0]["命中镜号"] == [] and m5[0]["首镜"] == 0
      and "漏拍" in m5[0].get("返工提示", "") and "返工" in m5[0].get("返工提示", ""),
      json.dumps(m5, ensure_ascii=False))

# B6 空输入 / 空镜头 → []
check("B6 空输入/空shots缺席", build_selling_point_map("", sp) == []
      and build_selling_point_map("暴雨", []) == []
      and build_selling_point_map("  , , 、 ", sp) == [], "缺席语义破坏")

# B7 命中镜号取镜头自身 n (非列表下标)
m7 = build_selling_point_map("暴雨", [_shot(101, "固定", focus="暴雨"), _shot(102, "拉")])
check("B7 镜号取自镜头n", m7[0]["命中镜号"] == [101] and m7[0]["首镜"] == 101,
      json.dumps(m7, ensure_ascii=False))

# B8 渲染段形态: 标题头 + 覆盖行 + 未命中行 + 覆盖统计
blk = render_selling_point_block(m2 + m5)
check("B8 渲染段含标题/未命中/统计", blk.startswith("【卖点映射】") and "未命中" in blk
      and "漏拍=返工提示" in blk and "覆盖: 1/2" in blk, blk[:160])
check("B8b 空映射渲染缺席", render_selling_point_block([]) == "", "空映射应返回空串")

print("=" * 66)
print("C. 节点集成 (真实引擎, additive 面)")
print("=" * 66)
PKG = load_pkg()
M = PKG.NODE_CLASS_MAPPINGS
Core, Cine = M["DirectorMasterCore"], M["DirectorMasterCinematic"]
ck = defaults(Core)
ck["场景描述"] = "女机甲战士在暴雨码头开启能量护盾"
_, core_pack = call(Core, ck)[:2]

cine_kw = defaults(Cine)
cine_kw["核心数据包"] = core_pack
cine_kw["目标时长(分钟)"] = 0.5

main0, js0 = call(Cine, cine_kw)[:2]
kw1 = dict(cine_kw)
kw1["卖点清单"] = "机甲变身, 暴雨, 父女和解"
main1, js1 = call(Cine, kw1)[:2]
main2, js2 = call(Cine, kw1)[:2]
jd0, jd1 = json.loads(js0), json.loads(js1)

# C1 无卖点输入 → 段与 JSON 键双缺席
check("C1 无输入段缺席", "【卖点映射】" not in main0 and "卖点映射" not in jd0, "缺席语义破坏")

# C2 有输入 → 段出现 + JSON 键为非空列表 + 条目键齐全
sp1 = jd1.get("卖点映射", [])
check("C2 有输入段出现", "【卖点映射】" in main1 and isinstance(sp1, list) and len(sp1) >= 3,
      f"{('【卖点映射】' in main1)}/{len(sp1)}")
check("C2b 映射条目键齐全", all(all(k in e for k in ("卖点", "命中镜号", "首镜", "覆盖")) for e in sp1),
      json.dumps(sp1[:1], ensure_ascii=False)[:160])

# C3 实体卖点 (暴雨) 真实承载; 编外卖点 (父女和解) 诚实未覆盖
by_name = {e["卖点"]: e for e in sp1}
check("C3 场景实体卖点命中", by_name.get("暴雨", {}).get("覆盖") is True,
      json.dumps(by_name.get("暴雨", {}), ensure_ascii=False)[:120])
check("C3b 编外卖点未覆盖返工", by_name.get("父女和解", {}).get("覆盖") is False
      and "漏拍" in by_name.get("父女和解", {}).get("返工提示", ""),
      json.dumps(by_name.get("父女和解", {}), ensure_ascii=False)[:160])

# C4 手法去重键存在且结构完整
dd = jd1.get("手法去重")
check("C4 手法去重键存在+结构", isinstance(dd, dict)
      and all(k in dd for k in ("校验口径", "镜数", "违规数", "运镜违规", "构图违规"))
      and dd.get("镜数") == len(jd1.get("分镜表", [])),
      json.dumps({k: dd.get(k) for k in ("镜数", "违规数")}, ensure_ascii=False) if dd else "missing")

# C5 additive 键零增删: 键集 = 基线 ∪ {手法去重} (∪ {卖点映射}); 契约必需键全在
base_keys = set(jd0.keys())
check("C5 键集零增删(无输入)", base_keys | {"手法去重"} == set(jd0.keys())
      and "卖点映射" not in jd0, str(sorted(base_keys))[:200])
check("C5b 键集零增删(有输入)", set(jd1.keys()) == base_keys | {"卖点映射"}
      if "卖点映射" not in jd0 else set(jd1.keys()) - {"卖点映射"} == base_keys,
      str(sorted(set(jd1.keys()) ^ base_keys)))
must = ("contract_version", "分镜表", "总时长秒", "场景实体", "叙事拓扑", "设备美学包", "同期声枚举")
check("C5c 契约必需键全在", all(k in jd1 for k in must), str([k for k in must if k not in jd1]))

# C6 分镜表零改写: 去重/映射段不触碰既有镜头键
check("C6 分镜表与基线逐镜一致", jd0["分镜表"] == jd1["分镜表"], "分镜表被 additive 段改写")

# C7 逐字节确定性
check("C7 同输入逐字节确定", js1 == js2 and main1 == main2, "存在非确定性")

# C8 一票否决词零命中 (卖点清单干净时)
hits = [v for v in VETO if v.lower() in main1.lower()]
check("C8 输出无一票否决词", not hits, str(hits))

print("=" * 66)
print("D. 判例库冻结接口 (knowledge_base.quality_precedents, B1 消费方)")
print("=" * 66)
from knowledge_base.quality_precedents import list_precedents

prec = list_precedents()
# D1 ≥12 条且全部 ok (字段完整率 100%)
check("D1 判例≥12条且零错误条目", len(prec) >= 12 and all(p.get("ok") for p in prec),
      f"{len(prec)} 条, 错误 {[p['file'] + ':' + p['error'] for p in prec if not p.get('ok')]}")
# D2 id 序列 NP-001 起, 唯一且符合口径
ids = [p["id"] for p in prec]
check("D2 id NP-001 起唯一", len(set(ids)) == len(ids) and ids[0] == "NP-001"
      and all(i.startswith("NP-") for i in ids), str(ids[:4]))
# D3 冻结键完整: id/rule/precedent/self_check/evidence_ref 全非空 str
check("D3 冻结键完整", all(all(isinstance(p.get(k), str) and p.get(k).strip()
                               for k in ("id", "rule", "precedent", "self_check", "evidence_ref"))
                           for p in prec), "存在空冻结键")

print("\n" + "=" * 50)
print(f"手法去重+卖点映射 测试: {PASS} PASS / {FAIL} FAIL")
if ERRORS:
    print("失败列表:")
    for e in ERRORS[:30]:
        print("  -", e)
sys.exit(1 if FAIL else 0)
