# -*- coding: utf-8 -*-
"""
批次6 D3/D4/D6 — 角色 DNA 档 + 项目风格锚 + 机位锚 测试 (tests/test_character_dna.py)
====================================================================================
覆盖矩阵:
  T0  模块常量 (禁词表规模 / 8 维齐全 / 版本 / promptBlock 上限)
  T1  抽象词拒绝 (样本词进→剔除+记录; 长词优先不重复计数; 清洗后值零抽象词)
  T2  8 维齐全 + 零编造 (空输入→全部 未提供, promptBlock="")
  T3  promptBlock ≤200 (超长截断到合法长度; 只拼非 未提供 维)
  T4  外貌DNA_JSON 继承往返 (旧 DNA+新字段→合并正确; JSON 串往返; 非法输入诚实降级)
  T5  characters 7 路输出 (第 7 路含 DNA; 前 6 路顺序/名称零改动; 三视图/MIP 跨镜注入)
  T6  参考图模式 IP-Adapter 模板 + 三视图锚定 + MIP 卡 三输出含 DNA promptBlock
  T7  外貌DNA_JSON 节点级继承接线 (角色DNA档→外貌DNA_JSON 增量覆盖)
  T8  director 第 3 路输出 + core pack 含 _项目风格锚 (缺省串/空段跳过)
  T9  cinematic 分镜JSON 镜头含 机位锚 且同 seed 确定性; 张力族映射; _项目风格锚 贯通;
      空 core 缺键不炸不注入
  T10 DNA 构建确定性 (同输入逐字节同)

证据存档: tests/character_dna_results.json (固定字段, 无时间戳, 重跑字节稳定)。
退出码: 0 = 全部通过, 1 = 有失败。运行: python -X utf8 tests/test_character_dna.py
"""
import contextlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.character_dna import (
    ABSTRACT_WORDS, DNA_DIMENSIONS, DNA_VERSION, PROMPTBLOCK_MAX, NOT_PROVIDED,
    build_dna_profile, merge_dna_profile, load_dna_json, reject_abstract_words,
)
from aggregator.director_master import DirectorMasterCore, build_style_anchor
from aggregator.characters_master import DirectorMasterCharacters
from aggregator.cinematic_studio import DirectorMasterCinematic, _CAM_ANCHOR_FAMILIES, _derive_camera_anchor

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


def quiet_build(node, kw):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return node.build(**kw)


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 模块常量")
    check("T0 禁词表 ≥25 词且含规格样本词", len(ABSTRACT_WORDS) >= 25
          and {"美丽", "优雅", "神秘", "帅气", "好看", "漂亮", "高级", "惊艳", "有气质",
               "氛围感", "绝美", "清纯", "御姐", "大气", "慵懒", "清冷", "明媚", "沧桑",
               "成熟感", "少年感"} <= set(ABSTRACT_WORDS), f"n={len(ABSTRACT_WORDS)}")
    check("T0 8 维精确齐全 (眼型/脸型/发型/发色/肤色/体态/标志着装/气质锚)",
          DNA_DIMENSIONS == ("眼型", "脸型", "发型", "发色", "肤色", "体态", "标志着装", "气质锚"),
          f"dims={DNA_DIMENSIONS}")
    check("T0 dna_version=1 / promptBlock 上限 200 / 未提供哨兵",
          DNA_VERSION == 1 and PROMPTBLOCK_MAX == 200 and NOT_PROVIDED == "未提供")

    # -----------------------------------------------------------------
    print("T1 抽象词拒绝")
    p1 = build_dna_profile("老陈", "美丽优雅, 圆脸, 有气质, 单眼皮, 高级感", "神秘的工作服")
    check("T1 样本抽象词全部被剔除并记录 (含长词 有气质/高级感)",
          set(p1["抽象词"]) == {"美丽", "优雅", "有气质", "高级感", "神秘"}, f"got={p1['抽象词']}")
    check("T1 长词优先: 子词 气质/高级 不重复计数",
          "气质" not in p1["抽象词"] and "高级" not in p1["抽象词"], f"got={p1['抽象词']}")
    check("T1 具体词存活并映射: 眼型=单眼皮 脸型=圆脸",
          p1["维度"]["眼型"] == "单眼皮" and p1["维度"]["脸型"] == "圆脸", f"dims={p1['维度']}")
    check("T1 清洗后值与 promptBlock 零抽象词残留",
          not any(w in p1["promptBlock"] for w in p1["抽象词"])
          and not any(w in json.dumps(p1["维度"], ensure_ascii=False) for w in p1["抽象词"]),
          f"block={p1['promptBlock'][:60]}")
    check("T1 未命中维度如实 未提供 (发色/肤色)",
          p1["维度"]["发色"] == NOT_PROVIDED and p1["维度"]["肤色"] == NOT_PROVIDED,
          f"dims={p1['维度']}")
    cl, found = reject_abstract_words("漂亮又好看的人")
    check("T1 reject_abstract_words 直接调用同口径", set(found) == {"漂亮", "好看"} and "漂亮" not in cl,
          f"found={found} clean={cl}")

    # -----------------------------------------------------------------
    print("T2 8 维齐全 + 零编造")
    p2 = build_dna_profile("", "", "", "")
    check("T2 空输入 → 8 维全部 未提供", len(p2["维度"]) == 8
          and all(v == NOT_PROVIDED for v in p2["维度"].values()), f"dims={p2['维度']}")
    check("T2 空输入 → promptBlock="" 且 抽象词=[] (零编造)",
          p2["promptBlock"] == "" and p2["抽象词"] == [], f"block={p2['promptBlock']!r}")
    check("T2 形状钉死: 键集 == {dna_version, 维度, promptBlock, 抽象词}",
          set(p2.keys()) == {"dna_version", "维度", "promptBlock", "抽象词"}, f"keys={sorted(p2)}")

    # -----------------------------------------------------------------
    print("T3 promptBlock ≤200")
    rich_name = "陈" * 100
    p3 = build_dna_profile(rich_name,
                           "单眼皮, 双眼皮, 圆脸, 瓜子脸, 高颧骨, 高鼻梁, 眼窝深, 白皙, 麦色, 瘦削, 高挑, 驼背, 眯眼, 皱眉, 抱臂, 咬指甲",
                           "工作服, 制服, 西装, 旗袍, 风衣, 卫衣, 围巾, 手套, 眼镜, 马甲, 长裙, 连衣裙")
    full3 = ("陈" * 100 + ":" + ";".join(
        f"{d}:{p3['维度'][d]}" for d in DNA_DIMENSIONS if p3["维度"][d] != NOT_PROVIDED))
    segs3 = p3["promptBlock"].split(";")
    check("T3 超长 promptBlock ≤200 且段边界截断 (整段保留, 不切半维度值)",
          len(p3["promptBlock"]) <= PROMPTBLOCK_MAX and len(p3["promptBlock"]) < len(full3)
          and len(segs3) >= 2 and segs3[0].startswith("陈" * 100 + ":")
          and all(":" in s and s.split(":", 1)[0] in DNA_DIMENSIONS for s in segs3[1:]),
          f"len={len(p3['promptBlock'])} full={len(full3)}")
    check("T3 未提供 维不进 promptBlock", "发色:" not in p3["promptBlock"], f"block={p3['promptBlock'][:80]}")
    check("T3 全部命中维都进 promptBlock (多命中 '+' 连接)",
          "眼型:" in p3["promptBlock"] and "标志" in p3["promptBlock"]
          and "+" in p3["promptBlock"], f"block={p3['promptBlock'][:120]}")
    p3b = build_dna_profile("小李", "短发, 麦色", "工作服")
    check("T3 短 promptBlock 逐维拼装且 ≤200",
          0 < len(p3b["promptBlock"]) <= PROMPTBLOCK_MAX
          and "发型:短发" in p3b["promptBlock"] and "肤色:麦色" in p3b["promptBlock"]
          and "标志着装:工作服" in p3b["promptBlock"], f"block={p3b['promptBlock']}")

    # -----------------------------------------------------------------
    print("T4 外貌DNA_JSON 继承往返")
    base = build_dna_profile("老陈", "短发, 瘦削, 眼窝深", "工作服, 手套")
    new = build_dna_profile("小李", "马尾, 麦色, 神秘", "围巾")
    merged = merge_dna_profile(base, new, "小李")
    check("T4 新字段覆盖基座 (发型 短发→马尾, 肤色 未提供→麦色)",
          merged["维度"]["发型"] == "马尾" and merged["维度"]["肤色"] == "麦色",
          f"dims={merged['维度']}")
    check("T4 基座字段保留 (眼型=眼窝深, 体态=瘦削), 新覆盖维=围巾 (增量覆盖语义)",
          merged["维度"]["眼型"] == "眼窝深" and merged["维度"]["体态"] == "瘦削"
          and merged["维度"]["标志着装"] == "围巾", f"dims={merged['维度']}")
    check("T4 抽象词并集去重 (新角色 神秘 入账)", "神秘" in merged["抽象词"]
          and len(merged["抽象词"]) == len(set(merged["抽象词"])), f"got={merged['抽象词']}")
    check("T4 promptBlock 按合并后 8 维重算", "小李:" in merged["promptBlock"]
          and "发型:马尾" in merged["promptBlock"] and "眼型:眼窝深" in merged["promptBlock"],
          f"block={merged['promptBlock']}")
    rt = merge_dna_profile(load_dna_json(json.dumps(base, ensure_ascii=False))[0], new, "小李")
    check("T4 JSON 串往返合并结果一致", rt == merged, f"rt={rt['promptBlock'][:60]}")
    poll = {"dna_version": 1, "维度": {"眼型": "绝美神秘电眼", "脸型": "高级脸", "体态": "瘦削"},
            "promptBlock": "污染:眼型:绝美神秘电眼", "抽象词": []}
    pm = merge_dna_profile(poll, build_dna_profile("小李", "", ""), "小李")
    check("T4 污染基座不绕过禁词表/规则白名单 (非白名单维降 未提供, 白名单维保留)",
          pm["维度"]["眼型"] == NOT_PROVIDED and pm["维度"]["脸型"] == NOT_PROVIDED
          and pm["维度"]["体态"] == "瘦削", f"dims={pm['维度']}")
    check("T4 污染基座禁词零残留于 promptBlock 且命中入账 抽象词",
          not any(w in pm["promptBlock"] for w in ("神秘", "高级", "绝美"))
          and "神秘" in pm["抽象词"] and "高级" in pm["抽象词"],
          f"block={pm['promptBlock']!r} rej={pm['抽象词']}")
    e1, m1 = load_dna_json("不是JSON{{{")
    e2, m2 = load_dna_json("[1, 2]")
    e3, m3 = load_dna_json("")
    check("T4 非法/非dict/空 外貌DNA_JSON 诚实降级 (None+说明, 不伪造基座)",
          e1 is None and m1 and e2 is None and m2 and e3 is None and m3 == "",
          f"m1={m1} m2={m2}")
    check("T4 形状钉死: 合并产物键集一致", set(merged.keys()) == {"dna_version", "维度", "promptBlock", "抽象词"})

    # -----------------------------------------------------------------
    print("T5 characters 7 路输出 (前 6 路零改动 + 三视图/MIP 注入)")
    ccls = DirectorMasterCharacters
    check("T5 RETURN_TYPES 7 路 STRING (末位追加)",
          ccls.RETURN_TYPES == ("STRING",) * 7, f"got={ccls.RETURN_TYPES}")
    check("T5 RETURN_NAMES 前 6 路零改动 + 第 7 路 角色DNA档",
          ccls.RETURN_NAMES[:6] == ("角色圣经", "环境圣经", "服化道圣经", "三视图锚定", "MIP资产卡", "完整资产")
          and ccls.RETURN_NAMES[6] == "角色DNA档", f"names={ccls.RETURN_NAMES}")
    ck = defaults(ccls)
    ck.update({"节点模式": "角色设定", "角色名": "老陈",
               "角色外貌": "短发, 瘦削, 颧骨高, 眼窝深",
               "角色服装": "深蓝色工作服(褪色)"})
    out5 = quiet_build(ccls(), ck)
    dna5 = json.loads(out5[6])
    check("T5 返回 7 元组且第 7 路 JSON 含 DNA (dna_version/维度/promptBlock)",
          len(out5) == 7 and dna5.get("dna_version") == 1 and len(dna5.get("维度", {})) == 8
          and dna5.get("promptBlock"), f"n={len(out5)} dna={str(dna5)[:120]}")
    check("T5 第 7 路 DNA 规则映射正确 (眼型=眼窝深/脸型=高颧骨/发型=短发/体态=瘦削/标志着装=工作服)",
          dna5["维度"]["眼型"] == "眼窝深" and dna5["维度"]["脸型"] == "高颧骨"
          and dna5["维度"]["发型"] == "短发" and dna5["维度"]["体态"] == "瘦削"
          and dna5["维度"]["标志着装"] == "工作服", f"dims={dna5['维度']}")
    check("T5 前 6 路语义零漂移 (角色圣经非空/环境圣经空/三视图+MIP 锚定头)",
          out5[0].strip() and out5[1] == "" and out5[2] == ""
          and out5[3].startswith("【三视图锚定】") and "【MIP 资产卡】" in out5[4]
          and out5[5].strip(), f"head={out5[0][:24]}")
    check("T5 三视图锚定跨镜注入 DNA promptBlock", dna5["promptBlock"] in out5[3])
    check("T5 MIP 资产卡跨镜注入 DNA promptBlock", dna5["promptBlock"] in out5[4])

    # -----------------------------------------------------------------
    print("T6 参考图模式三输出注入")
    ck6 = defaults(ccls)
    ck6.update({"节点模式": "参考图", "角色名": "小李",
                "角色外貌": "马尾, 麦色, 单眼皮", "角色服装": "校服, 围巾"})
    out6 = quiet_build(ccls(), ck6)
    dna6 = json.loads(out6[6])
    check("T6 参考图模式 7 元组且三/四/五路为参考图卡", len(out6) == 7
          and out6[3] == out6[4] == out6[5] and out6[3].strip(), f"n={len(out6)}")
    check("T6 IP-Adapter 模板注入 DNA锚定 行", "DNA锚定:" in out6[3]
          and dna6["promptBlock"] in out6[3], f"head={out6[3][:80]}")
    check("T6 参考图卡含【角色 DNA 档】段与剔除词回报",
          "【角色 DNA 档】" in out6[3] and "神秘" not in out6[3].split("【角色 DNA 档】")[-1][:80],
          f"dna_section={out6[3].split('【角色 DNA 档】')[-1][:100]}")
    check("T6 三视图锚定/MIP 卡/完整资产 三输出均含 promptBlock (跨镜注入)",
          all(dna6["promptBlock"] in out6[i] for i in (3, 4, 5)),
          f"block={dna6['promptBlock'][:60]}")

    # -----------------------------------------------------------------
    print("T7 外貌DNA_JSON 节点级继承接线")
    ck7a = defaults(ccls)
    ck7a.update({"节点模式": "角色设定", "角色名": "老陈",
                 "角色外貌": "短发, 瘦削, 眼窝深", "角色服装": "工作服"})
    out7a = quiet_build(ccls(), ck7a)
    ck7b = defaults(ccls)
    ck7b.update({"节点模式": "角色设定", "角色名": "小李",
                 "角色外貌": "长发", "外貌DNA_JSON": out7a[6]})
    out7b = quiet_build(ccls(), ck7b)
    merged7 = json.loads(out7b[6])
    check("T7 角色 DNA 档→外貌DNA_JSON 增量覆盖 (新 发型=长发 覆盖, 基座 眼型/体态/着装 保留)",
          merged7["维度"]["发型"] == "长发"
          and merged7["维度"]["眼型"] == json.loads(out7a[6])["维度"]["眼型"]
          and merged7["维度"]["体态"] == "瘦削" and merged7["维度"]["标志着装"] == "工作服",
          f"dims={merged7['维度']}")
    check("T7 继承后 promptBlock 重算且 ≤200", 0 < len(merged7["promptBlock"]) <= 200
          and "发型:长发" in merged7["promptBlock"], f"block={merged7['promptBlock'][:80]}")
    ck7c = dict(ck7b)
    ck7c["外貌DNA_JSON"] = "{坏 JSON"
    out7c = quiet_build(ccls(), ck7c)
    dna7c = json.loads(out7c[6])
    check("T7 非法 外貌DNA_JSON 不炸节点, 7 路完整且 DNA 来自当前输入",
          len(out7c) == 7 and dna7c["维度"]["发型"] == "长发"
          and dna7c["维度"]["眼型"] == NOT_PROVIDED, f"n={len(out7c)}")

    # -----------------------------------------------------------------
    print("T8 director 第 3 路输出 + core pack 风格锚")
    check("T8 RETURN_TYPES 3 路 (末位追加 项目风格锚)",
          DirectorMasterCore.RETURN_TYPES == ("STRING", "STRING", "STRING")
          and DirectorMasterCore.RETURN_NAMES[2] == "项目风格锚"
          and DirectorMasterCore.RETURN_NAMES[:2] == ("统一电影提示词", "核心数据包"),
          f"names={DirectorMasterCore.RETURN_NAMES}")
    out8 = quiet_build(DirectorMasterCore(), defaults(DirectorMasterCore))
    pack8 = json.loads(out8[1])
    check("T8 返回 3 元组, 第 3 路非空且 == core pack._项目风格锚",
          len(out8) == 3 and out8[2] and pack8.get("_项目风格锚") == out8[2],
          f"anchor={out8[2]}")
    check("T8 缺省拼装 导演·视觉调性·年代", out8[2] == "王家卫·梦幻·90年代", f"anchor={out8[2]}")
    check("T8 空段跳过 + 全空缺省串",
          build_style_anchor("", "写实", "80年代") == "写实·80年代"
          and build_style_anchor("", "", "") == "未定导演·未定调性·未定年代",
          f"a={build_style_anchor('', '写实', '80年代')} b={build_style_anchor('', '', '')}")
    ck8b = defaults(DirectorMasterCore)
    ck8b.update({"导演名_自定义": "", "导演名": "[电影] 诺兰", "视觉调性": "冷色", "时间年代": "2010s"})
    out8b = quiet_build(DirectorMasterCore(), ck8b)
    check("T8 换导演/调性/年代 → 锚随输入确定性变化",
          out8b[2] == "诺兰·冷色·2010s" and json.loads(out8b[1])["_项目风格锚"] == "诺兰·冷色·2010s",
          f"anchor={out8b[2]}")

    # -----------------------------------------------------------------
    print("T9 cinematic 机位锚 + 风格锚贯通")
    def core_pack_with_seed(seed):
        ck9 = defaults(DirectorMasterCore)
        ck9["随机种子"] = seed
        return quiet_build(DirectorMasterCore(), ck9)[1]

    def cine_payload(core_pack, mode="电影工作室"):
        kw9 = defaults(DirectorMasterCinematic)
        kw9.update({"画面模式": mode, "目标时长(分钟)": 0.5,
                    "核心数据包": core_pack, "剧本输入": "△ 内景 厨房 夜 △ 父亲切菜"})
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            _m, js = DirectorMasterCinematic().build(**kw9)
        return js

    js9 = cine_payload(core_pack_with_seed(42))
    d9 = json.loads(js9)
    check("T9 每镜含非空 机位锚 (str)", len(d9["分镜表"]) > 0
          and all(isinstance(s.get("机位锚"), str) and s["机位锚"].strip() for s in d9["分镜表"]),
          f"n={len(d9['分镜表'])} first={d9['分镜表'][0].get('机位锚')}")
    _fam = {0: _CAM_ANCHOR_FAMILIES[0][1], 1: _CAM_ANCHOR_FAMILIES[1][1], 2: _CAM_ANCHOR_FAMILIES[2][1]}

    def fam_idx(t):
        return 0 if t <= 3 else (1 if t <= 6 else 2)

    check("T9 机位锚首段 ∈ 该镜张力对应机位族 (低张力→平/缓族, 高张力→俯拍/手持/急推族)",
          all(s["机位锚"].split("/")[0] in _fam[fam_idx(s["拓扑张力"])] for s in d9["分镜表"]),
          f"bad={[s['机位锚'] for s in d9['分镜表'] if s['机位锚'].split('/')[0] not in _fam[fam_idx(s['拓扑张力'])]][:3]}")
    check("T9 张力三档均有镜头覆盖 (映射可观测)", {fam_idx(s["拓扑张力"]) for s in d9["分镜表"]} >= {0, 2},
          f"fams={sorted({fam_idx(s['拓扑张力']) for s in d9['分镜表']})}")
    check("T9 同 seed 重跑 分镜JSON 逐字节确定", cine_payload(core_pack_with_seed(42)) == js9)
    d9b = json.loads(cine_payload(core_pack_with_seed(43)))
    check("T9 换 seed → 同张力族内确定性变体 (至少一镜机位锚变化)",
          any(a["机位锚"] != b["机位锚"] for a, b in zip(d9["分镜表"], d9b["分镜表"]))
          and all(fam_idx(b["拓扑张力"]) == fam_idx(a["拓扑张力"]) for a, b in zip(d9["分镜表"], d9b["分镜表"])),
          f"changed={sum(1 for a, b in zip(d9['分镜表'], d9b['分镜表']) if a['机位锚'] != b['机位锚'])}")
    check("T9 _项目风格锚 贯通: 分镜JSON 顶层 == core pack 值",
          d9.get("_项目风格锚") == json.loads(core_pack_with_seed(42))["_项目风格锚"]
          and d9.get("_项目风格锚"), f"payload={d9.get('_项目风格锚')}")
    js9_nc = cine_payload("")
    d9_nc = json.loads(js9_nc)
    check("T9 空 core: 缺键不炸, 不注入 _项目风格锚, 机位锚仍确定性派生",
          "_项目风格锚" not in d9_nc and len(d9_nc["分镜表"]) > 0
          and all(s.get("机位锚") for s in d9_nc["分镜表"])
          and cine_payload("") == js9_nc, f"keys={sorted(k for k in d9_nc if k.startswith('_'))}")
    check("T9 既有镜头键零删 (机位锚为纯增量)",
          all({"镜号", "景别", "运镜", "时长", "拓扑张力", "构图"} <= set(s.keys()) for s in d9["分镜表"]))

    # -----------------------------------------------------------------
    print("T10 DNA 构建确定性")
    a = build_dna_profile("老王", "圆脸, 单眼皮, 麦色, 驼背", "旗袍, 手套", "写实")
    b = build_dna_profile("老王", "圆脸, 单眼皮, 麦色, 驼背", "旗袍, 手套", "写实")
    check("T10 同输入 → DNA dict 逐字节一致", json.dumps(a, ensure_ascii=False, sort_keys=True)
          == json.dumps(b, ensure_ascii=False, sort_keys=True))
    check("T10 机位锚直接调用确定性 (同参同果, salt=None 零随机源)",
          _derive_camera_anchor(8, "全景", "手持", None, 3, "低照度")
          == _derive_camera_anchor(8, "全景", "手持", None, 3, "低照度")
          and _derive_camera_anchor(8, "全景", "手持", 12345, 3) != _derive_camera_anchor(2, "全景", "手持", 12345, 3))


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    _m_ver = re.search(r'version\s*=\s*"([^"]+)"',
                       open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read())
    results_doc = {
        "suite": "test_character_dna",
        "version": _m_ver.group(1) if _m_ver else "unknown",
        "pass": PASS,
        "fail": FAIL,
        "results": RESULTS,
    }
    out_json = os.path.join(HERE, "character_dna_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_doc, f, ensure_ascii=False, indent=2)
    print(f"\n角色 DNA 档/项目风格锚/机位锚 测试结果: {PASS} PASS / {FAIL} FAIL (证据: {out_json})")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
