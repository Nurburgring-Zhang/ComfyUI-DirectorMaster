# -*- coding: utf-8 -*-
"""
V16.0 最终能力审计 (全新独立运行, 不复用历史结果)
回答四个问题:
  A. 🎲 随机是否真实多样、不重复 (30 轮全随机链路)
  B. 固定值是否保持确定性可复现
  C. AIGC 五模式 (文生/首帧/首尾帧/多参考图/参考视频) 是否真实判别+逐镜适配
  D. 零虚假扫描 + 质量硬指标
"""
import os, sys, json, re, hashlib, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

FAILS = []
def check(label, ok, detail=""):
    print(f"  [{'OK' if ok else 'FAIL'}] {label}" + (f" | {detail}" if detail else ""))
    if not ok:
        FAILS.append(label)

def load_pkg(name="dm_audit"):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def defaults(cls):
    it = cls.INPUT_TYPES()
    kw = {}
    for k, v in it.get("required", {}).items():
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], list):
            kw[k] = (v[1] or {}).get("default", v[0][0])
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

def md5(s):
    return hashlib.md5(str(s).encode("utf-8")).hexdigest()[:12]

PKG = load_pkg()
M = PKG.NODE_CLASS_MAPPINGS
from aggregator.node_base import parse_core_pack
from aggregator.director_master import DIR_NAMES

Core, Script, Cine = M["DirectorMasterCore"], M["DirectorMasterScript"], M["DirectorMasterCinematic"]
Router = M["DirectorMasterVideoRouter"]

print("=" * 72)
print("A. 30 轮全随机链路 (Core🎲导演 → Script🎲模式 → Cinematic🎲画面模式)")
print("=" * 72)
directors, script_fps, board_fps, modes_used = set(), set(), set(), set()
shot_grams, all_texts, grammar_combos = set(), [], set()
total_shots = 0
RND = "🎲 随机"
for i in range(30):
    ck = defaults(Core); ck["导演名"] = RND
    unified, core_pack = call(Core, ck)[:2]
    d = parse_core_pack(core_pack).get("_导演风格", "?")
    directors.add(d)
    sk = defaults(Script); sk["核心数据包"] = core_pack; sk["剧本模式"] = RND
    script = call(Script, sk)[0]
    script_fps.add(md5(script))
    nk = defaults(Cine); nk["核心数据包"] = core_pack; nk["画面模式"] = RND; nk["剧本输入"] = script
    main, json_str = call(Cine, nk)[:2]
    jd = json.loads(json_str)
    modes_used.add(jd.get("画面模式", "?"))
    shots = jd.get("分镜表", [])
    total_shots += len(shots)
    for s in shots:
        gram = "|".join(str(s.get(k, "")) for k in ("景别", "角度", "运镜", "焦段", "时长", "画面焦点"))
        shot_grams.add(md5(gram))
        grammar_combos.add(f"{s.get('景别','')}/{s.get('运镜','')}")
    board_fps.add(md5(json_str))
    all_texts += [unified, script, main, json_str]

check(f"30轮随机导演去重 ≥ 15 位", len(directors) >= 15, f"实际 {len(directors)} 位")
check(f"30轮剧本指纹全不重复", len(script_fps) == 30, f"唯一 {len(script_fps)}/30")
check(f"30轮分镜JSON指纹全不重复", len(board_fps) == 30, f"唯一 {len(board_fps)}/30")
check(f"画面模式覆盖 ≥ 15 种", len(modes_used) >= 15, f"实际 {len(modes_used)} 种")
dup_rate = 1 - len(shot_grams) / max(1, total_shots)
check(f"全维度镜头指纹重复率 < 15%", dup_rate < 0.15, f"{len(shot_grams)}/{total_shots} 唯一, 重复率 {dup_rate:.1%}")
check(f"景别×运镜语法组合 ≥ 25 种", len(grammar_combos) >= 25, f"实际 {len(grammar_combos)} 种")
check("导演库规模 ≥ 600 (600导演+商业别名条目)", len(DIR_NAMES) >= 600, f"实际 {len(DIR_NAMES)} 条目")
print("  抽样导演:", ", ".join(sorted(directors)[:8]), "...")

print("=" * 72)
print("B. 确定性 (固定导演+固定模式 两次运行逐字节一致)")
print("=" * 72)
def fixed_run():
    ck = defaults(Core); ck["导演名"] = "[电影] 王家卫"
    u, cp = call(Core, ck)[:2]
    sk = defaults(Script); sk["核心数据包"] = cp
    s = call(Script, sk)[0]
    nk = defaults(Cine); nk["核心数据包"] = cp; nk["剧本输入"] = s
    m, j = call(Cine, nk)[:2]
    return u, s, m, j
r1, r2 = fixed_run(), fixed_run()
for name, a, b in [("Core统一提示词", r1[0], r2[0]), ("Script剧本", r1[1], r2[1]),
                   ("Cinematic分镜文本", r1[2], r2[2]), ("Cinematic分镜JSON", r1[3], r2[3])]:
    check(f"{name} 两次一致", a == b)

print("=" * 72)
print("C. AIGC 五模式判别与逐镜适配")
print("=" * 72)
# 固定一条核心数据+分镜 供 Router 使用
ck = defaults(Core); ck["导演名"] = "[电影] 克里斯托弗·诺兰"
_u, cp = call(Core, ck)[:2]
sk = defaults(Script); sk["核心数据包"] = cp
_sb = call(Script, sk)[0]
nk = defaults(Cine); nk["核心数据包"] = cp; nk["剧本输入"] = _sb
_cine_main, _cine_json = call(Cine, nk)[:2]

cfgs = [
    ("文生视频",      {}),
    ("首帧生视频",    {"首帧图片": "assets/first_frame.png"}),
    ("首尾帧生视频",  {"首帧图片": "assets/first_frame.png", "尾帧图片": "assets/last_frame.png"}),
    ("多参考图生视频", {"首帧图片": "assets/first_frame.png", "角色正面参考": "assets/char_front.png",
                     "角色侧面参考": "assets/char_side.png"}),
    ("参考视频生视频", {"运动母版视频": "assets/motion_ref.mp4"}),
]
api_jsons = {}
for expect, extra in cfgs:
    rk = defaults(Router); rk["核心数据包"] = cp; rk["分镜脚本"] = _cine_main
    rk["目标视频模型"] = "全部生成"
    rk.update(extra)
    outs = call(Router, rk)
    meta = json.loads(outs[5])
    got = meta.get("AIGC生产模式", "?")
    check(f"Router 输入{sorted(extra.keys()) or ['无参考']} → 判别 {expect}", got == expect, f"实际 {got} | 依据 {meta.get('AIGC判别依据','')}")
    api_jsons[expect] = md5(outs[6])
check("5模式 API请求JSON 互不相同", len(set(api_jsons.values())) == 5, str(api_jsons))

# Cinematic 手动指定 5 模式 → 逐镜适配提示词
adapt_sets = {}
for mode in ["文生视频", "首帧生视频", "首尾帧生视频", "多参考图生视频", "参考视频生视频"]:
    nk2 = defaults(Cine); nk2["核心数据包"] = cp; nk2["剧本输入"] = _sb; nk2["AIGC生产模式"] = mode
    _m2, j2 = call(Cine, nk2)[:2]
    jd2 = json.loads(j2)
    shots2 = jd2.get("分镜表", [])
    adapts = [s.get("AIGC适配提示词", "") for s in shots2]
    check(f"Cinematic[{mode}] 每镜均有适配提示词", bool(shots2) and all(a.strip() for a in adapts),
          f"{sum(1 for a in adapts if a.strip())}/{len(shots2)} 镜")
    uniq = len(set(adapts))
    check(f"Cinematic[{mode}] 逐镜适配有差异(≥2种)", uniq >= 2, f"{uniq} 种")
    adapt_sets[mode] = md5("||".join(adapts))
check("5模式适配提示词集合互不相同", len(set(adapt_sets.values())) == 5)

print("=" * 72)
print("D. 零虚假扫描 + 质量硬指标")
print("=" * 72)
FORBID = ["mock", "stub", "placeholder", "todo:", "fixme", "占位", "模拟数据", "示例数据",
          "lorem", "待补充", "tbd", "fake", "编造"]
hits = []
for t in all_texts:
    low = t.lower()
    for w in FORBID:
        if w in low:
            hits.append(w)
check("30轮全部输出零虚假标记", not hits, f"命中: {sorted(set(hits))}")

# 质量硬指标: 每条分镜JSON结构完整
ck = defaults(Core)
_u, cp = call(Core, ck)[:2]
nk = defaults(Cine); nk["核心数据包"] = cp
_m, j = call(Cine, nk)[:2]
jd = json.loads(j)
shots = jd.get("分镜表", [])
ok_struct = bool(shots) and all(("景别" in s or "镜头" in s) and ("运镜" in s) for s in shots)
check("分镜表含景别/运镜字段", ok_struct, f"{len(shots)} 镜")
check("总时长秒 > 0", float(jd.get("总时长秒", 0)) > 0, f"{jd.get('总时长秒')}s")
_bare = {re.sub(r"^\[[^\]]*\]\s*", "", d).split(" (")[0].strip() for d in DIR_NAMES}
check("导演字段为真实导演", jd.get("导演", "") in _bare, jd.get("导演", ""))

print("=" * 72)
if FAILS:
    print(f"审计结论: {len(FAILS)} 项未通过 → {FAILS}")
    sys.exit(1)
print("审计结论: 全部通过 ✅")
