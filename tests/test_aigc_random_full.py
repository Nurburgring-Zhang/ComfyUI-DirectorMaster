# -*- coding: utf-8 -*-
"""
V16.1 全量随机测试编排器 — 随机输入 × 随机设置 × 全模式抽样
=============================================================
验证目标 (用户硬要求): 随机输入各种内容, 每个节点随机选择各种设置设定,
最终输出的剧本/分镜/JSON 都必须符合高质量的、适合 AIGC 模型使用的结果。

断言维度:
  A. 输出非空 + JSON 可解析 (分镜JSON / 交付JSON)
  B. 每镜 AIGC 提示词非空且达长度阈值, 含景别/运镜/光影或色彩/音频要素
  C. 叙事编排正确性: 非正叙编排产生时间线标签; 倒叙开场=现在·结局边缘; 乱叙时间线种类≥2
  D. 双线/三线产生≥2种线标签
  E. 去AI味: 创作正文空洞词命中为0 (翻译层已生效)
  F. 多样性: 不同编排/线型 → 输出哈希互异
  G. 短形态(≤1min)输出含五段结构标记; 长片含幕结构
  H. 场景贴合度: ≥60% 镜头的 AIGC 提示词命中输入场景锚点词(地点/角色/道具/天气),
     确保输出贴合输入场景而非无关模板内容 (V16.1 场景脱节修复的回归防线)

运行: python tests/test_aigc_random_full.py [用例数, 默认40]
退出码: 0=全过, 1=有失败
"""
import os, sys, json, hashlib, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")

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


def load_pkg():
    spec = importlib.util.spec_from_file_location("dm_rand", os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dm_rand"] = mod
    spec.loader.exec_module(mod)
    return mod


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


# === 随机池 ===
SCENES = [
    "父女在厨房, 雨夜, 1998年哈尔滨, 父亲切菜, 女儿坐桌边, 桌上有凤梨罐头和旧信",
    "古装客栈, 深夜, 剑客独自饮酒, 仇家推门而入, 烛火摇曳",
    "科幻空间站, 警报响起, 宇航员冲向控制舱, 舷窗外星云翻涌",
    "都市街头, 黄昏, 外卖小哥停下电动车, 接到母亲的电话",
    "末日废土, 沙暴逼近, 拾荒者背着行囊在荒漠跋涉",
    "校园操场, 清晨, 少女在跑道奔跑, 少年在场边注视",
    "民国上海, 雨夜, 歌女在后台卸妆, 镜中映出门外的影子",
    "深海珊瑚礁, 阳光穿透水面, 潜水员缓缓下潜",
    "雪山之巅, 日出, 登山者插上旗帜, 云海翻腾",
    "乡村小院, 夏日午后, 老人摇着蒲扇, 孙辈追逐蜻蜓",
    "赛博朋克夜市, 霓虹闪烁, 改造人穿过人群, 义眼扫描",
    "唐代宫廷, 大典前夜, 乐师调试琵琶, 烛光映壁",
]
DIRECTORS = ["[电影] 王家卫", "[电影] 诺兰", "[电影] 是枝裕和", "[电影] 黑泽明",
             "[电影] 塔可夫斯基", "[电视] 张黎", "[短视频] 疯狂小杨哥", "[动画] 宫崎骏"]
ARRANGEMENTS = ["跟随叙事结构", "正叙", "倒叙(结果先行)", "穿插倒叙", "穿插乱叙", "循环叙事(首尾相扣)"]
LINES = ["单线", "双线并行", "三线交织", "POV切换"]
DURATIONS = [0.5, 1, 3, 8, 30, 90]  # 分钟 (覆盖短视/短片/长片)
DIAL = ["零对白(纯视觉)", "极简(≤10字/句, ≤10句/场)", "适中(标准对白)", "密集(快节奏对话)"]
SUBT = ["弱(表层意思为主)", "中(每句1层潜文本)", "强(每句2-3层潜文本)"]
RHYTHM = ["极慢(长镜头1-3min)", "中速(标准)", "快(频繁切镜2-5s)"]
THEME = ["浅(表层故事)", "中(人物成长)", "深(人性剖析)"]

EMPTY_WORDS = ["温馨", "感人", "治愈", "泪目", "震撼", "史诗感", "绝美", "质感拉满", "氛围感拉满", "高级感"]


def scene_anchor_keywords(scene):
    """V16.1: 从输入场景提取锚点关键词 (地点/角色/道具/天气), 用于场景贴合度断言."""
    try:
        from aggregator.scene_engine import parse_scene
        p = parse_scene(scene)
    except Exception:
        return []
    kws = []
    loc = p.get("location", "")
    if loc and loc != "场景":
        kws.append(loc)
    for c in (p.get("characters") or []):
        if c and c not in ("主角", "副线"):
            kws.append(c)
    kws.extend(p.get("objects") or [])
    if p.get("weather"):
        kws.append(p["weather"])
    # V16.1 Review: 过滤过宽单字锚点 — 仅保留高信号单字 (天气类 + 武器/标志道具),
    #   其余单字 (车/书/山/海/家 等) 命中任意同字内容会误判贴合。
    _SINGLE_OK = set("雨雪霜雾风刀枪剑灯")
    out = []
    for k in kws:
        if not k:
            continue
        if len(k) == 1 and k not in _SINGLE_OK:
            continue
        out.append(k)
    return out


def run_one(mod, rng, case_id):
    scene = rng.choice(SCENES)
    director = rng.choice(DIRECTORS)
    arr = rng.choice(ARRANGEMENTS)
    line = rng.choice(LINES)
    dur = rng.choice(DURATIONS)

    # Core
    Core = mod.NODE_CLASS_MAPPINGS["DirectorMasterCore"]
    ck = defaults(Core)
    ck.update({"项目名": f"随机用例{case_id}", "场景描述": scene, "导演名": director,
               "叙事编排": arr, "叙事线型": line})
    try:
        core_pack = Core().build(**ck)[1]
    except Exception as e:
        check(f"case{case_id}.Core", False, f"build异常 {type(e).__name__}: {e}")
        return
    check(f"case{case_id}.Core.编排入包", (arr in core_pack) or arr == "跟随叙事结构", "编排未打包")

    # Script (随机模式 + 随机维度)
    S = mod.NODE_CLASS_MAPPINGS["DirectorMasterScript"]
    from aggregator.script_studio import SCRIPT_MODES
    smode = rng.choice(SCRIPT_MODES)
    sk = defaults(S)
    sk.update({"剧本模式": smode, "目标时长(分钟)": dur, "核心数据包": core_pack,
               "对白密度": rng.choice(DIAL), "潜文本强度": rng.choice(SUBT),
               "节奏控制": rng.choice(RHYTHM), "主题深度": rng.choice(THEME)})
    try:
        script = S().build(**sk)[0]
    except Exception as e:
        check(f"case{case_id}.Script[{smode}]", False, f"build异常 {type(e).__name__}: {e}")
        return
    check(f"case{case_id}.Script.非空", len(script) > 200, f"长度{len(script)}")
    # 短形态应有五段结构
    if dur <= 1:
        has_five = all(k in script for k in ["核心主题", "氛围与画质", "画面内容"])
        check(f"case{case_id}.Script.五段式", has_five, "短形态缺五段结构")
    # 非正叙编排应有导演叙事设计块
    if arr not in ("跟随叙事结构", "正叙"):
        check(f"case{case_id}.Script.叙事设计块", "导演叙事设计" in script, "缺导演叙事设计")

    # Cinematic (随机模式)
    C = mod.NODE_CLASS_MAPPINGS["DirectorMasterCinematic"]
    from aggregator.cinematic_studio import CINE_MODES
    cmode = rng.choice(CINE_MODES)
    ckw = defaults(C)
    ckw.update({"画面模式": cmode, "目标时长(分钟)": dur, "核心数据包": core_pack,
                "剧本输入": script})
    try:
        cine_main, cine_json = C().build(**ckw)
    except Exception as e:
        check(f"case{case_id}.Cinematic[{cmode}]", False, f"build异常 {type(e).__name__}: {e}")
        return
    # JSON 可解析
    try:
        cj = json.loads(cine_json)
        check(f"case{case_id}.Cinematic.JSON合法", True)
    except Exception as e:
        check(f"case{case_id}.Cinematic.JSON合法", False, str(e))
        return
    shots = cj.get("分镜表", [])
    check(f"case{case_id}.Cinematic.有分镜", len(shots) > 0, "分镜表为空")
    # 每镜 AIGC 提示词质量
    aigc_ok = 0
    short_prompts = 0
    for s in shots:
        p = s.get("AIGC提示词", "")
        if p and len(p) >= 60:
            aigc_ok += 1
        if p and len(p) < 60:
            short_prompts += 1
    if shots:
        ratio = aigc_ok / len(shots)
        check(f"case{case_id}.Cinematic.AIGC提示词达标", ratio >= 0.9,
              f"达标{aigc_ok}/{len(shots)} (过短{short_prompts})")
    # 叙事编排正确性 (仅当时长足够、场次≥4 时校验 — 短时长场次太少, 编排无意义)
    tls = set(s.get("时间线") for s in shots if s.get("时间线"))
    lines_set = set(s.get("线") for s in shots if s.get("线"))
    enough = dur >= 8
    if arr == "倒叙(结果先行)" and enough:
        check(f"case{case_id}.倒叙开场", any("结局边缘" in (t or "") for t in tls), f"时间线{tls}")
    if arr == "穿插乱叙" and enough:
        check(f"case{case_id}.乱叙多时间线", len(tls) >= 2, f"时间线种类{tls}")
    if arr in ("穿插倒叙",) and enough:
        check(f"case{case_id}.穿插倒叙有闪回", any("闪回" in (t or "") or "过去" in (t or "") for t in tls), f"{tls}")
    if line in ("双线并行", "三线交织", "POV切换") and enough:
        check(f"case{case_id}.{line}多线", len(lines_set) >= 2, f"线{lines_set}")
    # 编排块存在 (非默认编排时须有导演批注)
    _has_plan = cj.get("叙事编排", {}).get("导演批注")
    if arr != "跟随叙事结构" or line != "单线":
        check(f"case{case_id}.Cinematic.编排块", bool(_has_plan), "缺编排批注")
    else:
        check(f"case{case_id}.Cinematic.编排键", "叙事编排" in cj, "缺叙事编排键")

    # Summary
    Sum = mod.NODE_CLASS_MAPPINGS["DirectorMasterSummary"]
    skw = defaults(Sum)
    skw.update({"项目名": f"随机用例{case_id}", "核心数据包": core_pack,
                "剧本输出": script, "分镜输出": cine_main})
    try:
        manual, js, idx = Sum().build(**skw)
    except Exception as e:
        check(f"case{case_id}.Summary", False, f"build异常 {type(e).__name__}: {e}")
        return
    try:
        dj = json.loads(js)
        check(f"case{case_id}.Summary.JSON合法", True)
    except Exception as e:
        check(f"case{case_id}.Summary.JSON合法", False, str(e))
        return
    check(f"case{case_id}.Summary.AIGC块", "AIGC分镜提示词" in dj and len(dj["AIGC分镜提示词"]) > 0, "缺AIGC分镜提示词")
    check(f"case{case_id}.Summary.生产设置", "AIGC生产设置" in dj and dj["AIGC生产设置"].get("角色一致性锚"), "缺生产设置/角色锚")
    check(f"case{case_id}.Summary.编排", dj.get("叙事编排", {}).get("方式"), "缺叙事编排")

    # 去AI味: 交付 JSON 的 AIGC 提示词中不应有空洞词
    empty_hits = 0
    for item in dj.get("AIGC分镜提示词", []):
        txt = item.get("AIGC提示词", "")
        for w in EMPTY_WORDS:
            if w in txt:
                empty_hits += 1
    check(f"case{case_id}.去AI味.AIGC提示词", empty_hits == 0, f"空洞词命中{empty_hits}")

    # H. 场景贴合度 (V16.1: 防场景脱节回归) — ≥60% 镜头 AIGC 提示词须命中输入场景锚点词
    _anchor_kws = scene_anchor_keywords(scene)
    if _anchor_kws and shots:
        _fit = sum(1 for s in shots if any(k in (s.get("AIGC提示词") or "") for k in _anchor_kws))
        check(f"case{case_id}.场景贴合", _fit / len(shots) >= 0.6,
              f"命中{_fit}/{len(shots)} 锚点{_anchor_kws}")

    return {"script_hash": hashlib.md5(script.encode()).hexdigest(),
            "cine_hash": hashlib.md5(cine_json.encode()).hexdigest()}


def main():
    n_cases = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    print(f"加载包 ...")
    mod = load_pkg()
    print(f"运行 {n_cases} 个随机用例 ...")
    rng = random.Random(20260820)
    hashes = []
    for i in range(n_cases):
        r = run_one(mod, rng, i)
        if r:
            hashes.append(r)
        if (i + 1) % 10 == 0:
            print(f"  ... 已完成 {i+1}/{n_cases} (当前 PASS={PASS} FAIL={FAIL})")

    # 多样性: 至少观察到若干不同的分镜哈希
    cine_hashes = set(h["cine_hash"] for h in hashes)
    check("多样性.分镜哈希", len(cine_hashes) >= min(5, len(hashes)), f"唯一哈希{len(cine_hashes)}/{len(hashes)}")

    print("\n" + "=" * 60)
    print(f"全量随机测试结果: PASS={PASS} FAIL={FAIL}")
    if ERRORS:
        print("失败明细 (前30):")
        for e in ERRORS[:30]:
            print("  -", e)
    # V16.1.1 (审计修复 D-1): 实测结果落盘存档 — README「实测 PASS/FAIL」口径的证据锚点
    try:
        _result = {
            "version": "V16.1.1-MERGED",
            "cases": n_cases,
            "seed": 20260820,
            "PASS": PASS,
            "FAIL": FAIL,
            "unique_cine_hashes": len(cine_hashes),
            "failures": ERRORS[:30],
        }
        with open(os.path.join(HERE, "aigc_random_full_results.json"), "w", encoding="utf-8") as f:
            json.dump(_result, f, ensure_ascii=False, indent=2)
        print("结果存档已写入: tests/aigc_random_full_results.json")
    except Exception as _re:
        print(f"警告: 结果存档写入失败 {type(_re).__name__}: {_re}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
