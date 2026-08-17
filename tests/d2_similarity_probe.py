# -*- coding: utf-8 -*-
"""
V14.3 D2 验证 — 同档期形态模式正文相似度 <0.7
================================================
对同档期形态模式对, 同输入跑 Script 节点, 计算正文 bigram 相似度。
验收: 全部形态对相似度 <0.7 (审计基线: 创意玩法 vs 爆火反转 = 0.91)。
"""
import os, sys, importlib.util, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.stdout.reconfigure(encoding="utf-8")

spec = importlib.util.spec_from_file_location("dm_d2", os.path.join(ROOT, "__init__.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["dm_d2"] = mod
spec.loader.exec_module(mod)
M = mod.NODE_CLASS_MAPPINGS


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


def bigram_sim(a, b):
    a, b = str(a), str(b)
    if len(a) < 4 or len(b) < 4:
        return 0.0
    sa = set(a[i:i+2] for i in range(len(a) - 1))
    sb = set(b[i:i+2] for i in range(len(b) - 1))
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


core_cls = M["DirectorMasterCore"]
core_pack = call(core_cls, defaults(core_cls))[1]

script = M["DirectorMasterScript"]

# 同档期形态对 (审计点名的 + 同族同档期)
PAIRS = [
    ("创意玩法短视频", "爆火反转短视频"),
    ("创意玩法短视频", "搞笑整蛊短视频"),
    ("爆火反转短视频", "情感共鸣短视频"),
    ("脑洞剧情短视频", "情感共鸣短视频"),
    ("脑洞剧情短视频", "搞笑整蛊短视频"),
    ("番剧动漫剧本", "热血动漫剧本"),
    ("番剧动漫剧本", "校园动漫剧本"),
    ("校园动漫剧本", "奇幻冒险动漫剧本"),
    ("绘本故事脚本", "睡前故事脚本"),
    ("睡前故事脚本", "儿童教育动画脚本"),
    ("MV音乐短片脚本", "广告宣传片脚本"),
    ("广告宣传片脚本", "品牌故事片脚本"),
    ("人物纪录片脚本", "社会纪录片脚本"),
    ("婚礼/活动脚本", "Vlog脚本"),
    ("课程教学脚本", "Vlog脚本"),
    ("互动剧分支剧本", "沉浸式戏剧脚本"),
]

SCENE = "雨夜的老书店, 店主整理旧书, 一个女孩来找一本绝版诗集"

outputs = {}
modes_needed = sorted(set(m for p in PAIRS for m in p))
for mode in modes_needed:
    kw = defaults(script)
    kw["剧本模式"] = mode
    kw["场景描述"] = SCENE
    kw["核心数据包"] = core_pack
    try:
        out = call(script, kw)[0]
    except Exception as e:
        print(f"[ERROR] {mode}: {type(e).__name__} {e}")
        out = ""
    outputs[mode] = out

def body_of(out):
    """剧本正文 = 【剧本架构】附录之前的部分 (架构/角色弧为项目级共享块, 非正文)."""
    s = str(out)
    idx = s.find("【剧本架构】")
    if idx > 0:
        s = s[:idx]
    return s


print(f"{'模式对':40s} 相似度   判定")
fails = []
for a, b in PAIRS:
    sim = bigram_sim(body_of(outputs[a]), body_of(outputs[b]))
    ok = sim < 0.7
    if not ok:
        fails.append((a, b, sim))
    print(f"{a} vs {b:12s} {sim:.3f}   {'OK' if ok else 'FAIL'}")

print()
if fails:
    print(f"D2 未达标: {len(fails)} 对相似度 >=0.7")
    sys.exit(1)
print("D2 验证通过: 全部同档期形态对正文相似度 <0.7")
sys.exit(0)
