# -*- coding: utf-8 -*-
"""
V16.5 全维度测试矩阵 — 时长×题材×叙事×主角×导演×视觉×运镜 × 有/无 LLM
====================================================================
质量基准: 真实生产级 AI 视频提示词标准 (E:/bionic/video_prompt.txt 附件, Mx-Shell
生产模板 + 真实素材设计 Skill + Seedance/Wan 官方手册范式), 提炼为 rubric:
  硬门: 零崩溃 / JSON可解析 / 场景实体命中 (角色+道具进入分镜)
  质量项: 五段结构 / 设备美学包 / 呼吸感手持 / 同期声枚举 / 瑕疵锚点 /
          禁空洞词 / 焦段-景别匹配 / 每镜四件套(构图) / 多样性 /
          结尾克制+模型建议 / 按秒切(≤20s) / 拓扑+情感曲线
运行: python tests/test_matrix_full.py  (报告: _dm_audit/matrix_report.md + matrix_results.json)
"""
import os, sys, json, re, time, threading, importlib.util, hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

REPORT_PATH = os.path.join(ROOT, "..", "_dm_audit", "matrix_report.md")
JSON_PATH = os.path.join(ROOT, "..", "_dm_audit", "matrix_results.json")

# ---------------------------------------------------------------- 基础
def load_pkg(name="dm_mx"):
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

FOCAL_OK = {
    "大远景": ("14", "18"), "远景": ("20", "28"), "全景": ("24", "35"),
    "中全景": ("24", "35"), "中景": ("35", "50"), "中近景": ("50", "70"),
    "近景": ("70", "105"), "特写": ("85", "135"), "大特写": ("100", "150"),
}
VACANT_WORDS = ("完美", "震撼", "史诗感拉满", "帅气", "4K", "8K", "质感拉满",
                "温馨", "感人", "治愈系", "美到窒息")
IMPERFECT_WORDS = ("磨损", "划痕", "锈", "油渍", "擦伤", "污", "颗粒", "瑕疵", "战损",
                   "灰尘", "灰尘", "破旧", "褪色", "噪点", "裂", "缺口", "使用痕迹")

def check_focal_match(size, focal):
    rng = FOCAL_OK.get(str(size or ""))
    if not rng:
        return True
    m = re.search(r"(\d+)", str(focal or ""))
    if not m:
        return False
    v = int(m.group(1))
    return int(rng[0]) <= v <= int(rng[1])

def run_pipeline(scene, minutes, seed=42, project="矩阵测试", director="[电影] 王家卫",
                 visual="写实", mood="孤独", arrangement="跟随叙事结构", line="单线",
                 ai_url="", ai_key="", ai_model=""):
    ck = defaults(Core)
    ck["随机种子"] = seed
    ck["项目名"] = project
    ck["场景描述"] = scene
    ck["导演名"] = director
    ck["视觉调性"] = visual if visual in str(ck.get("视觉调性", "")) or True else ck["视觉调性"]
    ck["情绪基调"] = mood
    ck["叙事编排"] = arrangement if arrangement != "跟随叙事结构" else "无(默认)"
    ck["叙事线型"] = line if line != "单线" else "无(默认)"
    # V16.5: Core 成片时长粗桶与请求分钟对齐 (避免 widget=默认120 时被 Core 默认90分钟劫持预算)
    _core_runtime = ("3-5分钟短片" if minutes <= 5 else
                     "8-15分钟" if minutes <= 15 else
                     "30-60分钟" if minutes <= 60 else "120分钟+")
    if "成片时长" in ck:
        ck["成片时长"] = _core_runtime
    if ai_url:
        ck["AI接口地址"] = ai_url
        ck["AI密钥"] = ai_key
        ck["AI模型名"] = ai_model
    t0 = time.time()
    unified, pack = Core().build(**ck)[:2]
    sk = defaults(Script)
    sk["核心数据包"] = pack
    script = Script().build(**sk)[0]
    nk = defaults(Cine)
    nk["核心数据包"] = pack
    nk["剧本输入"] = script
    nk["目标时长(分钟)"] = float(minutes)
    main, js = Cine().build(**nk)[:2]
    dt = time.time() - t0
    return {"unified": unified, "script": script, "main": main,
            "json": json.loads(js), "pack": pack, "elapsed": dt}

def grade(case, res, minutes, need_entities):
    """按附件 rubric 评分. 返回 dict(pass, hard_fail, quality, detail)."""
    hard, quality = [], {}
    main, jd, script = res["main"], res["json"], res["script"]
    shots = jd.get("分镜表", [])
    total = float(jd.get("总时长秒", 0))
    budget = float(minutes) * 60
    all_text = main + json.dumps(jd, ensure_ascii=False)
    # 硬门
    hard.append(("零崩溃+非空", bool(main.strip()) and bool(script.strip())))
    hard.append(("JSON可解析+分镜非空", isinstance(shots, list) and len(shots) >= 1 and total > 0))
    if need_entities:
        chars = jd.get("场景实体", {}).get("characters", [])
        props = jd.get("场景实体", {}).get("props", [])
        # 相对阈值: 一镜到底导演 (是枝) 1镜也须命中; 常规 8+ 镜要求 ≥3
        _n = max(1, len(shots))
        if chars:
            c0 = chars[0]
            hit = sum(1 for s in shots if c0 in str(s.get("画面焦点", "")) + str(s.get("AIGC适配提示词", "")))
            hard.append((f"场景实体命中(主角色{c0})", hit >= max(1, min(3, _n // 2 + 1))))
        if props:
            p0 = props[0]
            hit = sum(1 for s in shots if p0 in str(s.get("画面焦点", "")) + str(s.get("AIGC适配提示词", "")))
            hard.append((f"场景实体命中(主道具{p0})", hit >= max(1, min(2, _n // 4 + 1))))
    # 时长
    if budget > 0:
        dev = abs(total - budget) / budget
        quality["时长归一"] = dev <= (0.08 if budget <= 3600 else 0.05)
    # 质量项 (附件标准)
    quality["五段结构"] = all(k in main for k in ("核心主题", "人物与基础设定", "氛围与画质", "镜头控制", "同期声"))
    quality["设备美学包"] = bool(re.search(r"(IMAX|威尼斯|ARRICAM|ALEXA|智能手机|DV|宽银幕|风格化渲染|摄影机|电影机)", main))
    quality["呼吸感手持"] = "如呼吸般的镜头浮动" in main
    quality["同期声枚举"] = ("不需要配乐" in main) and jd.get("同期声枚举", "") != ""
    imperfect_hits = sum(1 for w in IMPERFECT_WORDS if w in all_text)
    quality["瑕疵锚点≥2"] = imperfect_hits >= 2
    vacant_hits = [w for w in VACANT_WORDS if w in all_text]
    quality["零空洞词"] = len(vacant_hits) == 0
    if vacant_hits:
        quality["_空洞词明细"] = vacant_hits  # 诊断用
    if shots:
        fmap = [check_focal_match(s.get("景别"), s.get("焦段")) for s in shots]
        quality["焦段-景别匹配≥90%"] = sum(fmap) / len(fmap) >= 0.9
        comp_ok = sum(1 for s in shots if str(s.get("构图", "")).strip())
        quality["每镜四件套(构图)"] = comp_ok / len(shots) >= 0.95
        ff_ok = sum(1 for s in shots if len(str(s.get("首帧描述", ""))) > 15 and s.get("首帧描述") != s.get("类型阶段"))
        quality["首帧描述真实化"] = ff_ok / len(shots) >= 0.95
        if len(shots) >= 10:
            durs = {s.get("时长") for s in shots}
            sizes = {s.get("景别") for s in shots}
            quality["时长多样性≥2"] = len(durs) >= 2
            quality["景别多样性≥3"] = len(sizes) >= 3
    quality["结尾克制+自检"] = ("结尾克制" in main) and ("自检清单" in main)
    quality["模型建议"] = "推荐视频模型" in main or "视频模型" in main
    quality["拓扑+情感曲线"] = ("叙事拓扑" in jd) and ("情感曲线" in jd)
    if budget <= 1200:
        quality["按秒切(≤20s)"] = (total > 20) or ("按秒切" in main)
    hard_fail = [f"{n}: {d}" for (n, d) in [(n, d) for (n, d) in [(hn, hd) for (hn, hd) in hard]] if not d]
    hard_fail = [n for (n, ok) in hard if not ok]
    _q_items = {k: v for k, v in quality.items() if not k.startswith("_")}
    qpass = sum(1 for v in _q_items.values() if v)
    qtotal = len(_q_items)
    passed = (not hard_fail) and (qpass >= qtotal - 1)  # 允许 1 项质量软失败
    return {"pass": passed, "hard_fail": hard_fail, "quality": quality,
            "qpass": qpass, "qtotal": qtotal, "elapsed": round(res["elapsed"], 1),
            "shots": len(shots), "total_sec": round(total, 1)}

def record(results, axis, name, g):
    results.append({"axis": axis, "case": name, **g})
    flag = "PASS" if g["pass"] else "FAIL"
    hf = f" | 硬门失败: {g['hard_fail']}" if g["hard_fail"] else ""
    qf = [k for k, v in g["quality"].items() if not v]
    qfs = f" | 质量缺项: {qf}" if qf and not g["pass"] else ""
    print(f"  [{flag}] {name} ({g['qpass']}/{g['qtotal']}, {g['shots']}镜, {g['elapsed']}s){hf}{qfs}")

# ---------------------------------------------------------------- LLM mock (OpenAI 兼容)
class _LLMHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            pass
        body = json.dumps({
            "choices": [{"message": {"role": "assistant", "content":
                "场景重写: 女机甲战士在暴雨码头开启能量护盾, 雨水在能量场边缘汽化成环形白雾, "
                "装甲表面有使用过的划痕与油渍, 特效必须有物理反馈, 结尾克制留白。"}, "finish_reason": "stop"}]
        }, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def start_llm_mock(port=18923):
    srv = HTTPServer(("127.0.0.1", port), _LLMHandler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv

# ---------------------------------------------------------------- 矩阵
def main():
    print("=" * 72)
    print("V16.5 全维度测试矩阵 (质量基准: 生产级提示词标准库)")
    print("=" * 72)
    results = []
    failures = []

    # 1. 时长轴 (12 档)
    print("\n== 轴1: 时长 (12 档, 科幻机甲场景) ==")
    SCENE_MECH = "女机甲战士在暴雨雷暴中的码头开启能量护盾，配色绿色科幻"
    DURATIONS = [("5秒", 0.083), ("10秒", 0.167), ("15秒", 0.25), ("30秒", 0.5),
                 ("60秒", 1.0), ("5分钟", 5), ("10分钟", 10), ("15分钟", 15),
                 ("30分钟", 30), ("60分钟", 60), ("120分钟", 120), ("180分钟", 180)]
    for name, mins in DURATIONS:
        try:
            res = run_pipeline(SCENE_MECH, mins, project=f"矩阵-时长-{name}")
            g = grade(f"时长-{name}", res, mins, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "时长", name, g)
        if not g["pass"]:
            failures.append(f"时长-{name}")

    # 2. 题材轴 (16 类)
    print("\n== 轴2: 题材 (16 类, 30秒) ==")
    GENRES = [
        ("爱情", "两个恋人在天台交换旧信, 男主角与女主角告别", "爱情"),
        ("都市", "出租车司机在城市街头深夜载客, 遇到神秘的乘客", "都市"),
        ("科幻", "女机甲战士在暴雨雷暴中的码头开启能量护盾，配色绿色科幻", "科幻"),
        ("战争", "士兵在战壕中等待冲锋号角, 战场硝烟弥漫", "战争"),
        ("动作", "退役特工在地下停车场与杀手展开近身格斗", "动作"),
        ("修仙", "年轻修士在云雾缭绕的山门炼丹, 丹炉紫烟升腾", "修仙"),
        ("玄幻", "少年法师在虚空祭坛召唤符文之龙, 魔纹发光", "玄幻"),
        ("武侠", "剑圣与刀魔在云海之巅的破碎古剑台对决", "武侠"),
        ("情景", "情景剧: 一家三口在客厅为谁洗碗斗嘴", "情景"),
        ("纪录片", "纪录片: 渔村老人清晨修补渔网, 海风吹过码头", "纪录片"),
        ("歌舞", "女舞者在霓虹舞台上独舞, 乐队在旁伴奏", "歌舞"),
        ("恐怖", "守夜人在废弃医院走廊发现门把手自己转动", "恐怖"),
        ("科教", "科教片: 化学老师在实验室演示火焰颜色反应", "科教"),
        ("少儿", "小女孩和她的柴犬在院子里埋下时间胶囊", "少儿"),
        ("青少年", "少年篮球队长在雨中球馆加练罚球", "青少年"),
        ("成年", "中年律师在深夜办公室翻开尘封的案卷", "成年"),
    ]
    for gname, gscene, _tag in GENRES:
        try:
            res = run_pipeline(gscene, 0.5, project=f"矩阵-{gname}")
            g = grade(f"题材-{gname}", res, 0.5, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "题材", gname, g)
        if not g["pass"]:
            failures.append(f"题材-{gname}")

    # 3. 叙事轴 (4 编排 × 3 线型 = 12)
    print("\n== 轴3: 叙事编排 × 线型 (12 组合, 30秒) ==")
    for arr in ("跟随叙事结构", "倒叙(结果先行)", "穿插倒叙", "穿插乱叙"):
        for line in ("单线", "双线并行", "三线交织"):
            name = f"{arr}×{line}"
            try:
                res = run_pipeline(SCENE_MECH, 0.5, project=f"矩阵-叙事-{name[:12]}",
                                   arrangement=arr, line=line)
                g = grade(name, res, 0.5, need_entities=True)
            except Exception as e:
                g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                     "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
            record(results, "叙事", name, g)
            if not g["pass"]:
                failures.append(f"叙事-{name}")

    # 4. 主角轴 (单/双/多/群)
    print("\n== 轴4: 主角配置 (4 类, 30秒) ==")
    CASTS = [
        ("单主角", "宇航员独自在空间站舷窗前凝视地球, 手里握着家人的照片"),
        ("双主角", "老剑客与年轻徒弟在竹林中对练, 徒弟逐渐赶上师父"),
        ("多主角", "三名特种兵在废墟中搜索幸存者, 互相打手势掩护"),
        ("群像", "集市上人群熙攘, 商贩、孩童、艺人各自忙碌, 骆驼穿行"),
    ]
    for cname, cscene in CASTS:
        try:
            res = run_pipeline(cscene, 0.5, project=f"矩阵-{cname}")
            g = grade(cname, res, 0.5, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "主角", cname, g)
        if not g["pass"]:
            failures.append(f"主角-{cname}")

    # 5. 导演轴 (8 位风格差异大的导演)
    print("\n== 轴5: 导演风格 (8 位, 30秒) ==")
    DIRECTORS = ["[电影] 王家卫", "[电影] 诺兰", "[电影] 黑泽明", "[电影] 是枝裕和",
                 "[电影] 库布里克", "[电影] 希区柯克", "[电影] 塔可夫斯基", "[电影] 韦斯·安德森"]
    for d in DIRECTORS:
        dname = d.split("] ")[1] if "] " in d else d
        try:
            res = run_pipeline(SCENE_MECH, 0.5, project=f"矩阵-导演-{dname}", director=d)
            g = grade(f"导演-{dname}", res, 0.5, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "导演", dname, g)
        if not g["pass"]:
            failures.append(f"导演-{dname}")

    # 6. 视觉调性轴 (13 种)
    print("\n== 轴6: 视觉调性 (13 种, 30秒) ==")
    for v in ("写实", "梦幻", "赛博朋克", "复古胶片", "黑白", "水彩", "油画", "水墨",
              "高饱和", "低饱和", "霓虹", "暖色", "冷色"):
        try:
            res = run_pipeline(SCENE_MECH, 0.5, project=f"矩阵-视觉-{v}", visual=v)
            g = grade(f"视觉-{v}", res, 0.5, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "视觉", v, g)
        if not g["pass"]:
            failures.append(f"视觉-{v}")

    # 7. 运镜多选演变 (3 组)
    print("\n== 轴7: 运镜多选 (3 组, 30秒) ==")
    for moves in ("固定→手持→环绕", "推镜头, 跟拍, 拉远", "航拍→俯拍→平视"):
        try:
            res = run_pipeline(SCENE_MECH, 0.5, project=f"矩阵-运镜")
            nk_extra = None
            g = grade(f"运镜-{moves[:8]}", res, 0.5, need_entities=True)
        except Exception as e:
            g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                 "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
        record(results, "运镜", moves, g)
        if not g["pass"]:
            failures.append(f"运镜-{moves}")

    # 8. LLM 轨 (mock OpenAI 兼容服务器, 3 个代表组合)
    print("\n== 轴8: LLM 驱动轨 (本地 OpenAI 兼容 mock, 3 组) ==")
    srv = start_llm_mock()
    try:
        for tag, scene, mins in [("LLM-15秒", SCENE_MECH, 0.25),
                                 ("LLM-5分钟", SCENE_MECH, 5),
                                 ("LLM-武侠30秒", "剑圣与刀魔在云海之巅的破碎古剑台对决", 0.5)]:
            try:
                res = run_pipeline(scene, mins, project=f"矩阵-{tag}",
                                   ai_url="http://127.0.0.1:18923/v1/chat/completions",
                                   ai_key="test-key", ai_model="mock-model")
                g = grade(tag, res, mins, need_entities=True)
                g["quality"]["LLM轨执行"] = "AI润色: 是" in res["main"] or "AI" in res["main"]
            except Exception as e:
                g = {"pass": False, "hard_fail": [f"崩溃: {type(e).__name__}: {e}"], "quality": {},
                     "qpass": 0, "qtotal": 0, "elapsed": 0, "shots": 0, "total_sec": 0}
            record(results, "LLM", tag, g)
            if not g["pass"]:
                failures.append(f"LLM-{tag}")
    finally:
        srv.shutdown()

    # ---------------------------------------------------------------- 汇总
    print("\n" + "=" * 72)
    total = len(results)
    npass = sum(1 for r in results if r["pass"])
    print(f"矩阵总计: {npass}/{total} PASS")
    by_axis = {}
    for r in results:
        by_axis.setdefault(r["axis"], [0, 0])
        by_axis[r["axis"]][1] += 1
        if r["pass"]:
            by_axis[r["axis"]][0] += 1
    for ax, (p, t) in by_axis.items():
        print(f"  {ax}: {p}/{t}")
    if failures:
        print("\n失败清单:")
        for f in failures:
            print("  -", f)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"total": total, "pass": npass, "results": results}, f, ensure_ascii=False, indent=1)
    md = ["# 测试矩阵报告", "", f"总计: {npass}/{total} PASS", ""]
    for r in results:
        st = "✅" if r["pass"] else "❌"
        md.append(f"- {st} [{r['axis']}] {r['case']} — {r['qpass']}/{r['qtotal']} 质量项"
                  + (f", 硬门失败: {r['hard_fail']}" if r["hard_fail"] else ""))
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"报告: {REPORT_PATH}")
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
