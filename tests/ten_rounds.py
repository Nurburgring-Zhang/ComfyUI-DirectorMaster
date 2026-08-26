# -*- coding: utf-8 -*-
"""
V16.1.1-MERGED 十轮全量测试编排器
================================
T1  部署运行: doctor 7类 + 17节点加载 + 工作流JSON
T2  全量功能使用: 258 模式全执行 + 逐节点唯一性统计 (277 断言)
T3  数据聚合: 14+ 数据源真实消费验证
T4  能力增强: 9 项复活接线注入出现率
T5  功能维度矩阵: 多输入×多模式 确定性/降级/结构
T6  逻辑通畅性: Core→6维上游→Cinematic→Summary→Archive 全链路
T7  数据流转全链路: 归档写盘+版本全操作+逐字节回滚
T8  AI驱动: f2_ai_track_e2e 套件
T9  全管线/工作流/IO: 工作流校验 + 全下拉遍历 + 确定性
T10 输出质量最严质检: 结构硬指标+一票否决+覆盖+浮点
"""
import os, sys, json, re, time, hashlib, tempfile, shutil, subprocess, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

RESULTS = {}


def record(round_id, label, ok, detail=""):
    RESULTS.setdefault(round_id, []).append((label, ok, detail))
    print(f"  [{'OK' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail and not ok else ""))


def load_pkg(name="dm_ten"):
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


def run_script(path, timeout=900):
    p = subprocess.run([sys.executable, "-X", "utf8", path], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("=" * 70)
print("T1 部署运行")
print("=" * 70)
rc, out = run_script(os.path.join(ROOT, "doctor.py"))
record("T1", "doctor.py 7类自检", rc == 0, out[-300:])
mod = load_pkg("dm_t1")
record("T1", "默认加载 17 节点", len(mod.NODE_CLASS_MAPPINGS) == 17, str(len(mod.NODE_CLASS_MAPPINGS)))
bad_contract = [n for n, c in mod.NODE_CLASS_MAPPINGS.items()
                if not getattr(c, "RETURN_TYPES", None) or not callable(getattr(c, getattr(c, "FUNCTION", ""), None))]
record("T1", "RETURN/FUNCTION 契约", not bad_contract, str(bad_contract))
rc, out = run_script(os.path.join(ROOT, "tests", "test_workflows.py"))
record("T1", "工作流 JSON 有效性", rc == 0, out[-200:])

print("=" * 70)
print("T2 全量功能使用 (258 模式 · 277 断言)")
print("=" * 70)
rc, out = run_script(os.path.join(ROOT, "tests", "test_all_modes.py"))
record("T2", "全模式回归 277 断言", rc == 0, out[-300:])

print("=" * 70)
print("T3 数据聚合 (真实消费)")
print("=" * 70)
M = mod.NODE_CLASS_MAPPINGS
core_kw = defaults(M["DirectorMasterCore"])
core_pack = call(M["DirectorMasterCore"], core_kw)[1]
# 形态模式 (走 _build_full_screenplay 骨架+执行层) → 场景库/故事感/案例 注入
s_kw = defaults(M["DirectorMasterScript"]); s_kw["剧本模式"] = "爆火反转短视频"; s_kw["核心数据包"] = core_pack
script_out = call(M["DirectorMasterScript"], s_kw)[0]
record("T3", "故事感/场景库 进形态剧本",
       ("故事感总纲" in script_out or "影视场景库" in script_out or "结构任务" in script_out))
# 大师DNA → 导演匹配时注入
s_kw2 = defaults(M["DirectorMasterScript"]); s_kw2["剧本模式"] = "完整长片剧本"; s_kw2["核心数据包"] = core_pack
core_kw_wkw = defaults(M["DirectorMasterCore"]); core_kw_wkw["导演名"] = "[电影] 王家卫"
cp2 = call(M["DirectorMasterCore"], core_kw_wkw)[1]
s_kw2["核心数据包"] = cp2
script_out2 = call(M["DirectorMasterScript"], s_kw2)[0]
record("T3", "15大师DNA 进王家卫剧本", "王家卫" in script_out2 and len(script_out2) > 3000)
# 领域规则 → LLM 提示词 (离线验证 _domain_mode_prompt)
from aggregator.llm_engine import _domain_mode_prompt
d1 = _domain_mode_prompt("剧本", "绘本", {"scene": "小狐狸"})
d2 = _domain_mode_prompt("剧本", "竖屏短剧", {"scene": "都市"})
d3 = _domain_mode_prompt("分镜", "分镜", {"scene": "雨夜"})
record("T3", "绘本/短剧/分镜 领域规则块", bool(d1) and bool(d2) and bool(d3))
# 8 设计模式真实产出
from aggregator.vibe_studio import TEMPLATES as VT, VIBE_MODES as VM
design_ok = 0
for dm in ["电商套图", "海报设计", "品牌设计", "PPT设计", "逻辑关系图设计", "三视图设计", "爆炸拆解图设计", "流水线图设计"]:
    o = VT[dm]("智能手表, 都市白领", "王家卫", "期待", {})
    if o and "降级" not in o and len(o) > 200:
        design_ok += 1
record("T3", "8 设计模式真实产出", design_ok == 8, f"{design_ok}/8")
# Seedance 能力边界
vr_kw = defaults(M["DirectorMasterVideoRouter"]); vr_out = call(M["DirectorMasterVideoRouter"], vr_kw)
meta_str = vr_out[5] if len(vr_out) > 5 else "{}"
try:
    meta = json.loads(meta_str)
    caps = meta.get("Seedance能力边界", {})
    record("T3", "Seedance 2.5 能力边界", bool(caps.get("版本") or caps.get("单镜最大秒")), str(caps)[:80])
except Exception as e:
    record("T3", "Seedance 2.5 能力边界", False, repr(e))
# 42环节/三定律 进手册
cine_kw = defaults(M["DirectorMasterCinematic"]); cine_kw["核心数据包"] = core_pack
cine_out = call(M["DirectorMasterCinematic"], cine_kw)[0]
sm_kw = defaults(M["DirectorMasterSummary"]); sm_kw["核心数据包"] = core_pack; sm_kw["分镜输入"] = cine_out
manual = call(M["DirectorMasterSummary"], sm_kw)[0]
record("T3", "42环节+三定律 进制作手册", "42" in manual and ("留白" in manual and "运镜" in manual))
# 6 文档进资产
a_kw = defaults(M["DirectorMasterAsset"]); a_kw["核心数据包"] = core_pack
asset_out = call(M["DirectorMasterAsset"], a_kw)[0]
record("T3", "Higgsfield 6文档 进资产", "Higgsfield" in asset_out or "ASSET_REGISTRY" in asset_out)
# 空场景灵感生成
c_kw = defaults(M["DirectorMasterCore"]); c_kw["场景描述"] = ""; c_kw["项目名"] = "灵感测试A"
c_out_a = call(M["DirectorMasterCore"], c_kw)
c_kw_b = defaults(M["DirectorMasterCore"]); c_kw_b["场景描述"] = ""; c_kw_b["项目名"] = "灵感测试A"
c_out_b = call(M["DirectorMasterCore"], c_kw_b)
record("T3", "空场景灵感生成(确定性)", c_out_a[0] == c_out_b[0] and len(c_out_a[0]) > 100)

print("=" * 70)
print("T4 能力增强 (复活接线注入出现率)")
print("=" * 70)
record("T4", "MASTER_VIDEO_PRINCIPLES 进分镜", "大师级影视语言原则" in cine_out)
r_kw = defaults(M["DirectorMasterRouter"]); r_kw["核心数据包"] = core_pack
router_out = call(M["DirectorMasterRouter"], r_kw)[0]
record("T4", "CINEDANCE 骨架 进路由", "CINEDANCE" in router_out)
record("T4", "形态骨架 进短视频剧本", "结构任务" in script_out)
record("T4", "执行层 进短视频剧本", "短视频镜头执行" in script_out)
s_kw3 = defaults(M["DirectorMasterScript"]); s_kw3["剧本模式"] = "互动剧分支剧本"; s_kw3["核心数据包"] = core_pack
it_out = call(M["DirectorMasterScript"], s_kw3)[0]
record("T4", "互动剧分支树 可解析", "分支树 JSON" in it_out)
# V16.1.1 M2: 真实解析分支树 JSON — 结构完整性 + 零悬空引用 (审计修复)
try:
    _bt_seg = it_out.split("【分支树 JSON (可解析)】", 1)[1]
    _bt_obj, _ = json.JSONDecoder().raw_decode(_bt_seg[_bt_seg.index("{"):])
    _bt_ids = {n["id"] for n in _bt_obj["nodes"]}
    _bt_choices = [n for n in _bt_obj["nodes"] if n.get("type") == "choice"]
    _bt_dangling = []
    for _bt_n in _bt_obj["nodes"]:
        for _bt_o in (_bt_n.get("options") or []):
            if _bt_o.get("target") not in _bt_ids:
                _bt_dangling.append(f"{_bt_n['id']}->{_bt_o.get('target')}")
        if _bt_n.get("next") and _bt_n["next"] not in _bt_ids:
            _bt_dangling.append(f"{_bt_n['id']}.next->{_bt_n['next']}")
    _bt_st = _bt_obj.get("stats", {})
    _bt_ok = (_bt_st.get("choice_points") == 2 and len(_bt_choices) == 2
              and all(len(n.get("options") or []) >= 2 for n in _bt_choices)
              and _bt_st.get("endings") == 3
              and set(_bt_obj.get("endings") or []) == {"E1", "E2", "E3"}
              and not _bt_dangling)
    record("T4", "分支树 结构完整零悬空", _bt_ok,
           f"choice={_bt_st.get('choice_points')} endings={_bt_st.get('endings')} dangling={_bt_dangling[:3]}")
except Exception as e:
    record("T4", "分支树 结构完整零悬空", False, repr(e))

print("=" * 70)
print("T5 功能维度矩阵 (多输入×确定性×降级)")
print("=" * 70)
SCENES = ["父女在厨房, 雨夜, 1998年哈尔滨, 桌上有凤梨罐头和旧信",
          "武侠: 雪夜客栈, 剑客与老板娘, 一柄断剑",
          "科幻: 2140年火星基地, AI管理员与最后一名人类",
          "校园: 夏天教室, 毕业前最后一天, 一台旧相机"]
det_ok, exec_ok = 0, 0
for sc in SCENES:
    ck = defaults(M["DirectorMasterCore"]); ck["场景描述"] = sc
    cpk = call(M["DirectorMasterCore"], ck)[1]
    for mode in ["完整长片剧本", "竖屏小程序剧", "绘本故事脚本"]:
        k1 = defaults(M["DirectorMasterScript"]); k1["剧本模式"] = mode; k1["核心数据包"] = cpk
        o1 = call(M["DirectorMasterScript"], k1)[0]
        o2 = call(M["DirectorMasterScript"], k1)[0]
        exec_ok += 1 if (o1 and len(o1) > 500) else 0
        det_ok += 1 if o1 == o2 else 0
record("T5", "4场景×3模式 执行成功", exec_ok == 12, f"{exec_ok}/12")
record("T5", "4场景×3模式 完全确定性", det_ok == 12, f"{det_ok}/12")
# 降级: 缺失核心数据包
k_no = defaults(M["DirectorMasterScript"]); k_no["剧本模式"] = "完整长片剧本"
try:
    o_no = call(M["DirectorMasterScript"], k_no)[0]
    record("T5", "无核心包降级不崩", bool(o_no))
except Exception as e:
    record("T5", "无核心包降级不崩", False, repr(e))

print("=" * 70)
print("T6 逻辑通畅性 (全链路 6 维融入)")
print("=" * 70)
ck = defaults(M["DirectorMasterCore"])
cpk = call(M["DirectorMasterCore"], ck)[1]
up = {}
for node, key in [("DirectorMasterScript", "剧本输入"), ("DirectorMasterVibe", "创意输入"),
                  ("DirectorMasterArt", "美术输入"), ("DirectorMasterSound", "声音输入"),
                  ("DirectorMasterCharacters", "角色输入"), ("DirectorMasterAsset", "资产输入")]:
    kw = defaults(M[node]); kw["核心数据包"] = cpk
    up[key] = call(M[node], kw)[0]
cine_kw = defaults(M["DirectorMasterCinematic"]); cine_kw["核心数据包"] = cpk
cine_kw.update(up)
cine_full = call(M["DirectorMasterCinematic"], cine_kw)
m6 = re.search(r"6维融入: (\d)/6", cine_full[0])
record("T6", "Cinematic 6维融入 6/6", bool(m6) and m6.group(1) == "6", m6.group(0) if m6 else "未找到")
sm_kw = defaults(M["DirectorMasterSummary"]); sm_kw["核心数据包"] = cpk
sm_kw["剧本输入"] = up["剧本输入"]; sm_kw["分镜输入"] = cine_full[0]
sm_out = call(M["DirectorMasterSummary"], sm_kw)
record("T6", "Summary 手册+JSON+索引 3路", len(sm_out) >= 3 and all(x for x in sm_out[:3]))
try:
    jd = json.loads(sm_out[1])
    record("T6", "JSON交付包 分镜来源标注", "分镜表来源" in json.dumps(jd, ensure_ascii=False))
except Exception as e:
    record("T6", "JSON交付包解析", False, repr(e))

print("=" * 70)
print("T7 数据流转全链路 (归档+版本全操作)")
print("=" * 70)
tmpdir = tempfile.mkdtemp(prefix="dm_t7_")
try:
    from aggregator.version_store import VersionStore
    st = VersionStore(tmpdir, "T7项目")
    v1 = st.commit("初稿", {"剧本": ("s1.txt", "第一版剧本内容" * 200)}, scores={"total": 0.5})
    v2 = st.commit("修订", {"剧本": ("s2.txt", "第二版剧本内容" * 220), "分镜": ("c2.txt", "分镜" * 300)}, scores={"total": 0.8})
    st.set_state(v2, "APPROVED")
    st.tag(v2, "gold")
    d = st.diff(v1, v2)
    record("T7", "commit/state/tag/diff", d is not None and st.get(v2)["state"] == "APPROVED")
    nv, restored = st.rollback("gold", write=True)
    rb_ok = os.path.isfile(os.path.join(tmpdir, "s2.txt")) and len(restored) == 2
    h = hashlib.sha256(open(os.path.join(tmpdir, "s2.txt"), encoding="utf-8", newline="").read().encode()).hexdigest()
    record("T7", "回滚逐字节", rb_ok and h == st.get(v2)["files"]["剧本"]["sha256"])
    best = st.best("total")
    record("T7", "最优版本选择", best and best[0][1]["id"] == v2)
    record("T7", "版本库体积", os.path.getsize(st.path) < 2 * 1024 * 1024, f"{os.path.getsize(st.path)}B")
    # V16.1.1 M3: 并发提交零丢失 — 8线程×2提交 (进程内路径锁+跨进程文件锁串行化) (审计修复)
    import threading as _t7_th
    _t7_base = len(st.log(limit=50))
    _t7_vids, _t7_errs = [], []
    _t7_guard = _t7_th.Lock()

    def _t7_worker(ti):
        try:
            for ci in range(2):
                content = f"并发内容-{ti}-{ci}" * 120
                vid = st.commit(f"并发{ti}-{ci}", {"剧本": (f"cc_{ti}_{ci}.txt", content)})
                with _t7_guard:
                    _t7_vids.append((vid, hashlib.sha256(content.encode()).hexdigest()))
        except Exception as _e7:
            with _t7_guard:
                _t7_errs.append(repr(_e7))

    _t7_ts = [_t7_th.Thread(target=_t7_worker, args=(i,)) for i in range(8)]
    for t in _t7_ts:
        t.start()
    for t in _t7_ts:
        t.join()
    st2 = VersionStore(tmpdir, "T7项目")  # 新实例从盘上重载, 验证持久化后的真实状态
    _t7_log = st2.log(limit=50)
    _t7_lost = [vid for vid, _ in _t7_vids if st2.get(vid) is None]
    _t7_bad = [vid for vid, sha in _t7_vids
               if st2.get(vid) and st2.get(vid)["files"]["剧本"]["sha256"] != sha]
    record("T7", "并发8线程×2提交零丢失",
           not _t7_errs and len(_t7_vids) == 16 and len(_t7_log) == _t7_base + 16
           and not _t7_lost and not _t7_bad,
           f"提交{len(_t7_vids)}/16 历史{len(_t7_log)}/{_t7_base + 16} 丢失{len(_t7_lost)} sha异常{len(_t7_bad)} 错误{_t7_errs[:1]}")
finally:
    shutil.rmtree(tmpdir)

print("=" * 70)
print("T8 AI驱动 (真实HTTP端到端)")
print("=" * 70)
rc, out = run_script(os.path.join(ROOT, "tests", "f2_ai_track_e2e.py"))
record("T8", "AI轨 11 断言", rc == 0, out[-300:])

print("=" * 70)
print("T9 全管线/工作流/IO (下拉全遍历+确定性)")
print("=" * 70)
rc, out = run_script(os.path.join(ROOT, "tests", "test_workflows.py"))
record("T9", "工作流校验", rc == 0, out[-200:])
# 全下拉遍历: Script 叙事结构 × Cinematic 节奏风格 抽样遍历
script_cls = M["DirectorMasterScript"]
story_opts = script_cls.INPUT_TYPES()["required"]["叙事结构"][0]
exec_n, fail_n = 0, 0
for opt in story_opts:
    if opt in ("无(默认)", "🎲 随机"):
        continue
    kw = defaults(script_cls); kw["剧本模式"] = "完整长片剧本"; kw["叙事结构"] = opt; kw["核心数据包"] = cpk
    try:
        o = call(script_cls, kw)[0]
        exec_n += 1
        if not o or len(o) < 500:
            fail_n += 1
    except Exception:
        fail_n += 1
record("T9", f"叙事结构 {exec_n} 选项全执行", fail_n == 0, f"{fail_n}失败")
cine_cls = M["DirectorMasterCinematic"]
pacing_opts = cine_cls.INPUT_TYPES()["optional"]["节奏风格"][0]
exec_n2, fail_n2 = 0, 0
for opt in pacing_opts:
    if opt in ("无(默认)", "🎲 随机"):
        continue
    kw = defaults(cine_cls); kw["核心数据包"] = cpk; kw["节奏风格"] = opt
    try:
        o = call(cine_cls, kw)[0]
        exec_n2 += 1
        if not o or len(o) < 500:
            fail_n2 += 1
    except Exception:
        fail_n2 += 1
record("T9", f"节奏风格 {exec_n2} 选项全执行", fail_n2 == 0, f"{fail_n2}失败")

print("=" * 70)
print("T10 输出质量最严质检")
print("=" * 70)
# 结构硬指标: 三幕剧/救猫咪/英雄之旅 120min
def beat_positions(script_text):
    """从剧本正文找 中点/黑夜/高潮 的场次位置占比."""
    body = script_text[:script_text.find("【剧本架构】")] if "【剧本架构】" in script_text else script_text
    scenes = re.findall(r"^(INT\.|EXT\.|内景|外景|场\d+|第\d+场)", body, re.M)
    n = max(1, len(scenes))
    pos = {}
    lines = body.splitlines()
    # 生成器两种写法并存: "灵魂黑夜" / "灵魂的黑夜" (不同理论表), 须稳健匹配
    pats = {"中点": re.compile("中点"), "灵魂黑夜": re.compile(r"灵魂的?黑夜"), "高潮": re.compile("高潮")}
    for key, pat in pats.items():
        for i, ln in enumerate(lines):
            if pat.search(ln):
                pos[key] = i / max(1, len(lines))
                break
    return pos, n


# 期望区间来自 2026-08 实测 (确定性引擎, 留 ±0.06 余量):
#   三幕剧(经典)        中点0.483 高潮0.838            (经典三幕无独立黑夜拍)
#   救猫咪15拍          中点0.483 黑夜0.681 高潮0.76
#   三幕剧(变体)        中点0.525 黑夜0.760 高潮0.797
#   英雄之旅12阶段      中点0.483 黑夜0.681 高潮0.838
for theory, expect in [("三幕剧(经典)", {"中点": (0.35, 0.62), "高潮": (0.72, 0.97)}),
                       ("救猫咪15拍(Blake Snyder)", {"中点": (0.35, 0.62), "灵魂黑夜": (0.62, 0.75), "高潮": (0.72, 0.97)}),
                       ("三幕剧(变体)", {"中点": (0.40, 0.68), "灵魂黑夜": (0.70, 0.82), "高潮": (0.70, 0.95)}),
                       ("英雄之旅12阶段(Campbell)", {"中点": (0.35, 0.62), "灵魂黑夜": (0.62, 0.75), "高潮": (0.72, 0.97)})]:
    kw = defaults(script_cls); kw["剧本模式"] = "完整长片剧本"; kw["叙事结构"] = theory; kw["核心数据包"] = cpk
    o = call(script_cls, kw)[0]
    pos, n = beat_positions(o)
    ok = True
    detail = []
    for k, (lo, hi) in expect.items():
        v = pos.get(k)
        detail.append(f"{k}={v}")
        if v is None or not (lo <= v <= hi):
            ok = False
    record("T10", f"结构硬指标 {theory}", ok, ", ".join(detail))
# 一票否决扫描: 占位符/测试词/AI套话 (规则定义行本身必须枚举禁词, 不算命中)
VETO = ["TODO", "FIXME", "placeholder", "占位符", "lorem", "masterpiece", "best quality", "ultra detailed", "8K", "HDR"]


def _rule_line(ln):
    return any(k in ln for k in ("禁用", "反AI套话", "ANTI_AI", "反AI规则", "反AI词"))


veto_hits = []
for name, txt in [("script", script_out2), ("cine", cine_full[0]), ("manual", manual)]:
    for ln in str(txt).splitlines():
        if _rule_line(ln):
            continue
        for v in VETO:
            if v.lower() in ln.lower():
                veto_hits.append(f"{name}:{v}:{ln.strip()[:40]}")
record("T10", "一票否决扫描 (占位/AI套话)", not veto_hits, str(veto_hits[:5]))
# 浮点伪影
pat = re.compile(r"\d+\.\d{3,}")
fl = len(pat.findall(cine_full[0])) + len(pat.findall(cine_full[1])) + len(pat.findall(manual))
record("T10", "浮点伪影清零", fl == 0, f"{fl}处")
# 时长覆盖 (默认90min核心包)
jd2 = json.loads(cine_full[1])
total_dur = float(jd2.get("总时长秒", 0))
target = 90 * 60
dev = abs(total_dur - target) / target
record("T10", "时长覆盖 ±1%", dev <= 0.01, f"{total_dur:.0f}s dev={dev*100:.2f}%")
# D1/D2 探针
rc1, out1 = run_script(os.path.join(ROOT, "tests", "d1_grammar_probe.py"))
record("T10", "D1 同簇镜头语法唯一", rc1 == 0, out1[-200:])
rc2, out2 = run_script(os.path.join(ROOT, "tests", "d2_similarity_probe.py"))
record("T10", "D2 形态正文相似度<0.7", rc2 == 0, out2[-200:])

# ============ 汇总 ============
print("\n" + "=" * 70)
print("十轮全量测试汇总")
print("=" * 70)
total_ok = total_fail = 0
for rnd in sorted(RESULTS):
    oks = sum(1 for _, ok, _ in RESULTS[rnd] if ok)
    fails = sum(1 for _, ok, _ in RESULTS[rnd] if not ok)
    total_ok += oks; total_fail += fails
    print(f"{rnd}: {oks} PASS / {fails} FAIL")
    for label, ok, detail in RESULTS[rnd]:
        if not ok:
            print(f"    ✗ {label}: {detail[:200]}")
print(f"\n总计: {total_ok} PASS / {total_fail} FAIL")
with open(os.path.join(HERE, "ten_round_results.json"), "w", encoding="utf-8") as f:
    json.dump({r: [{"label": l, "ok": o, "detail": d} for l, o, d in v] for r, v in RESULTS.items()},
              f, ensure_ascii=False, indent=1)
sys.exit(1 if total_fail else 0)
