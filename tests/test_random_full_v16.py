# -*- coding: utf-8 -*-
"""
V16.4 全量随机 + 叙事拓扑测试 — 高价值维度移植自 V16.6-AIGC 参考版, 适配本基座中文 schema
====================================================================
运行: python tests/test_random_full_v16.py
覆盖:
  1. 随机场景全管线零异常 + 输出非空 (Core → Script → Cinematic)
  2. 时长归一: 总时长误差 ≤ 8% (多时长档位)
  3. 多样性: 时长值 ≥ 3 种; 景别 ≥ 3 种; ≥60 镜时张力跨度 ≥ 4
  4. 反罐头: 相邻镜头焦点重复率 ≤ 15%
  5. 叙事拓扑: 波浪/反转/递进 meta 真实生成
  6. 复杂叙事结构端到端: 套层/罗生门/时间循环/环形 — 识别 + 每镜标签
  7. 正面内容零英文 AI 套话 (masterpiece/8K/HDR/...)
  8. 拓扑确定性: 同种子同场景两次运行 JSON 逐字节一致
退出码: 0 = 全部通过, 1 = 有失败
"""
import os, sys, json, random, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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
        ERRORS.append(f"{label} {detail}")
        print(f"  [FAIL] {label} {detail}")


def load_pkg(name="dm_v16"):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def defaults(cls):
    it = cls.INPUT_TYPES()
    kw = {}
    for sec in ("required", "optional"):
        for k, v in it.get(sec, {}).items():
            if isinstance(v, (list, tuple)) and v and isinstance(v[0], list):
                kw[k] = (v[1] or {}).get("default", v[0][0])
            elif isinstance(v, tuple) and v and v[0] == "STRING":
                kw[k] = (v[1] or {}).get("default", "")
            elif isinstance(v, tuple) and v and v[0] in ("INT", "FLOAT"):
                kw[k] = (v[1] or {}).get("default", 0)
            elif isinstance(v, tuple) and v and v[0] == "BOOLEAN":
                kw[k] = (v[1] or {}).get("default", False)
    return kw


PKG = load_pkg()
M = PKG.NODE_CLASS_MAPPINGS
Core, Script, Cine = M["DirectorMasterCore"], M["DirectorMasterScript"], M["DirectorMasterCinematic"]

SCENES = [
    ("深夜便利店, 店员发现货架上的商品每天都在减少", "悬疑", 30.0),
    ("婚礼前夜, 新娘在阳台遇见十年前的自己", "怀旧", 90.0),
    ("拆迁前的老胡同, 修表匠收到最后一块待修的表", "温暖", 15.0),
    ("深山护林站, 巡逻员发现雪地里有一行陌生脚印", "恐惧", 8.0),
    ("电竞馆后台, 替补选手在决赛前接到神秘电话", "紧张", 45.0),
    ("海岛灯塔, 守塔人三十年来的信件被海浪冲回", "释然", 115.0),
]

AI_CLICHES = ("masterpiece", "8K", "HDR", "cinematic lighting", "best quality",
              "highly detailed", "trending on artstation", "ultra detailed", "4K", "octane render")

print("=" * 66)
print("1-4. 随机场景全管线 (时长归一/多样性/反罐头/零套话)")
print("=" * 66)
random.seed(20260829)
for i, (scene, mood, minutes) in enumerate(SCENES):
    tag = f"S{i+1}"
    try:
        ck = defaults(Core)
        ck["场景描述"] = scene
        ck["情绪基调"] = mood
        ck["随机种子"] = random.getrandbits(31)
        unified, pack = Core().build(**ck)[:2]
        sk = defaults(Script)
        sk["核心数据包"] = pack
        sk["剧本模式"] = "🎲 随机"
        script = Script().build(**sk)[0]
        nk = defaults(Cine)
        nk["核心数据包"] = pack
        nk["剧本输入"] = script
        nk["画面模式"] = "🎲 随机"
        nk["目标时长(分钟)"] = minutes
        main, js = Cine().build(**nk)[:2]
    except Exception as e:
        check(f"{tag} 全管线零异常", False, f"{type(e).__name__}: {e}")
        continue
    check(f"{tag} 全管线零异常", True)
    check(f"{tag} 输出非空", bool(main.strip()) and bool(script.strip()) and bool(js.strip()))
    jd = json.loads(js)
    shots = jd.get("分镜表", [])
    check(f"{tag} 分镜JSON可解析+非空", isinstance(shots, list) and len(shots) >= 5, f"{len(shots)}镜")
    # 时长归一 ±8%
    total = float(jd.get("总时长秒", 0))
    budget = minutes * 60
    check(f"{tag} 时长归一≤8%", total > 0 and abs(total - budget) / budget <= 0.08,
          f"总{total:.0f}s / 预算{budget:.0f}s")
    durs = {str(s.get("时长", "")) for s in shots}
    check(f"{tag} 时长多样性≥3种", len(durs) >= 3, f"{len(durs)}种")
    sizes = {str(s.get("景别", "")) for s in shots}
    check(f"{tag} 景别多样性≥3种", len(sizes) >= 3, f"{len(sizes)}种")
    if len(shots) >= 60:
        tens = [float(s.get("拓扑张力", 5)) for s in shots]
        check(f"{tag} 张力跨度≥4", max(tens) - min(tens) >= 4, f"{max(tens)}-{min(tens)}")
    # 反罐头: 相邻焦点重复
    if len(shots) >= 10:
        dup = sum(1 for a, b in zip(shots, shots[1:])
                  if str(a.get("画面焦点", "")) == str(b.get("画面焦点", "")) and str(a.get("画面焦点", "")).strip())
        check(f"{tag} 相邻焦点重复率≤15%", dup / max(1, len(shots) - 1) <= 0.15, f"{dup}/{len(shots)-1}")
    # 拓扑 meta
    topo = jd.get("叙事拓扑", {})
    check(f"{tag} 叙事拓扑meta真实", isinstance(topo, dict) and topo.get("waves", 0) >= 1,
          f"waves={topo.get('waves')}")
    # 零英文 AI 套话 (排除禁用语境)
    hits = []
    for w in AI_CLICHES:
        for s in shots[:40]:
            txt = str(s.get("画面焦点", "")) + str(s.get("叙事目的", ""))
            low = txt.lower()
            if w.lower() in low and not any(neg in low for neg in ("禁用", "不用", "避免", "绝不", "negative", "禁止", "无")):
                hits.append(w)
                break
    check(f"{tag} 正面内容零AI套话", not hits, f"{hits}")

print("=" * 66)
print("5-6. 复杂叙事结构端到端")
print("=" * 66)
CX_CASES = [
    ("套层叙事", "深夜书房, 老人讲述戏中戏里的往事, 日记里的故事", 90.0, "框架"),
    ("罗生门", "审讯室, 一场各执一词的命案, 每个人的说法都不一样", 60.0, "视角版本"),
    ("时间循环", "清晨公寓, 男主困在同一天的循环里, 醒来又是同一天", 45.0, "次循环"),
    ("环形叙事", "火车站, 女人兜兜转转又回到原点, 结尾就是开头", 30.0, "环形闭环"),
]
for cx_name, scene, minutes, want in CX_CASES:
    ck = defaults(Core)
    ck["场景描述"] = scene
    ck["随机种子"] = 2026
    _, pack = Core().build(**ck)[:2]
    nk = defaults(Cine)
    nk["核心数据包"] = pack
    nk["目标时长(分钟)"] = minutes
    nk["复杂叙事结构"] = "自动"
    jd = json.loads(Cine().build(**nk)[1])
    topo = jd.get("叙事拓扑", {})
    check(f"复杂结构[{cx_name}]识别", topo.get("complex") == cx_name, f"实际={topo.get('complex')}")
    tags = [str(s.get("叙事标签", "")) for s in jd.get("分镜表", [])]
    check(f"复杂结构[{cx_name}]每镜标签", any(want in t for t in tags), f"want={want}")
    check(f"复杂结构[{cx_name}]标签覆盖>10镜", sum(1 for t in tags if t.strip()) > 10,
          f"{sum(1 for t in tags if t.strip())}镜有标签")

print("=" * 66)
print("7-8. 拓扑确定性 + 手动档")
print("=" * 66)
def topo_run(scene, minutes, cx, seed):
    ck = defaults(Core); ck["场景描述"] = scene; ck["随机种子"] = seed
    _, pack = Core().build(**ck)[:2]
    nk = defaults(Cine); nk["核心数据包"] = pack; nk["目标时长(分钟)"] = minutes; nk["复杂叙事结构"] = cx
    return Cine().build(**nk)[1]

j1 = topo_run("深夜手术室, 医生面对无法解释的心电图", 60, "自动", 777)
j2 = topo_run("深夜手术室, 医生面对无法解释的心电图", 60, "自动", 777)
check("同种子拓扑JSON逐字节一致", j1 == j2)
check("手动档[无]清空复杂结构", json.loads(topo_run("清晨公寓, 男主困在同一天的循环里, 醒来又是同一天", 45, "无", 5))["叙事拓扑"].get("complex") is None)

print("\n" + "=" * 50)
print(f"全量随机+拓扑测试: {PASS} PASS / {FAIL} FAIL")
if ERRORS:
    print("失败列表:")
    for e in ERRORS[:30]:
        print("  -", e)
sys.exit(1 if FAIL else 0)
