# -*- coding: utf-8 -*-
"""
批次3 D2 — 契约渲染层测试 (tests/test_contract_render.py)
==========================================================
覆盖矩阵:
  T0  常量与登记表 (RENDER_VERSION / MODEL_KEYS / ELEMENT_ORDER / FIELD_MAP 对齐)
  T1  基础渲染 (结构键 / meta 默认 GENERIC / 每镜 7 段全在 / 段序 = 七要素固定顺序 / 镜号保真)
  T2  确定性 (同输入两次逐字节 / deepcopy / JSON round-trip / raw 与 report 两形态文本一致)
  T3  model_key 路由 (三键两两互异 / SEEDANCE 能力表引用+时间戳锚+时间轴 / WAN 简洁美学标记 /
      GENERIC 兜底零专属标记 / 未知键与大小写诚实 ValueError)
  T4  坏输入诚实报错 (非 dict / 无契约头 / 缺分镜表 / 空分镜表 / 镜非 dict / 缺镜号 /
      报告 normalized=None)
  T5  extra 字段不渲染不炸 (镜内 extra / 顶层 extra)
  T6  真实 Cinematic 集成 (真 build 产物 → 渲染成功, 每镜 7 段全在, 镜数对齐)

证据存档: tests/contract_render_results.json (suite/version/pass/fail/results 固定字段,
version 动态读 pyproject, 无时间戳 → 重跑字节稳定)。
退出码: 0 = 全部通过, 1 = 有失败。
"""
import contextlib
import copy as _copy
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.contract_render import (
    RENDER_VERSION, MODEL_KEYS, DEFAULT_MODEL_KEY, ELEMENT_ORDER, FIELD_MAP,
    render_storyboard_prompts,
)
from aggregator.storyboard_contract import validate_storyboard, CANON_SHOT_KEYS

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


def _raises_value_error(fn):
    """fn() 抛 ValueError → 返回 (True, 异常消息); 其他/不抛 → (False, 说明)。"""
    try:
        fn()
    except ValueError as e:
        return True, str(e)
    except Exception as e:
        return False, "抛了非 ValueError: %s: %s" % (type(e).__name__, e)
    return False, "未抛异常"


def _texts(out):
    return [p["prompt_text"] for p in out["per_shot"]]


# =====================================================================
# 测试契约构造 (含相对引用/字符串镜号/extra 字段)
# =====================================================================
def _mk_shots():
    return [
        {"镜号": 1, "时长": "3.8s", "景别": "全景", "角度": "平视", "运镜": "缓推",
         "焦段": "35mm", "画面焦点": "父亲的手停在砧板上", "叙事目的": "建立空间",
         "构图": "三分法", "POV": "主角 POV", "时间线": "现在", "线": "A",
         "色彩": "冷灰", "光影": "低照度", "材质": "金属", "氛围": "压抑", "情绪": "孤独",
         "声音": "雨点砸在窗上", "音频描述": "音频: 雨声、刀碰砧板; 只保留同期声",
         "转场": "硬切", "首帧描述": "厨房夜景, 雨窗", "自定义X": "extra-绝不应渲染-42"},
        {"镜号": 2, "时长": 2.5, "start": {"ref": 1, "op": "+", "offset_s": 0},
         "景别": "特写", "角度": "俯拍", "运镜": "慢推", "焦段": "85mm",
         "画面焦点": "女儿的侧脸", "叙事目的": "情绪特写", "情绪": "孤独",
         "音频描述": "音频: 呼吸声; 只保留同期声"},
        {"镜号": "S3", "时长": 1.5, "景别": "中景", "角度": "平视", "运镜": "固定",
         "画面焦点": "桌上的凤梨罐头", "情绪": "怀旧"},
    ]


def _mk_contract():
    return {"contract_version": 1, "分镜数": 3, "总时长秒": 7.8, "导演": "王家卫",
            "情绪": "孤独", "画面模式": "电影工作室", "AIGC生产模式": "多参考图生视频",
            "分镜表": _mk_shots()}


def run_suite():
    # -----------------------------------------------------------------
    print("T0 常量与登记表")
    check("T0 RENDER_VERSION == 1", RENDER_VERSION == 1, f"v={RENDER_VERSION}")
    check("T0 MODEL_KEYS = 两真实键 + 通用兜底",
          MODEL_KEYS == ("SEEDANCE_25", "WAN_30", "GENERIC") and DEFAULT_MODEL_KEY == "GENERIC",
          f"keys={MODEL_KEYS} default={DEFAULT_MODEL_KEY}")
    check("T0 ELEMENT_ORDER 七要素固定顺序",
          ELEMENT_ORDER == ("参考绑定", "主体动作", "空间", "镜头", "视觉", "音频", "约束"),
          f"order={ELEMENT_ORDER}")
    check("T0 FIELD_MAP 7 要素键与 ELEMENT_ORDER 对齐 (逐字段映射登记)",
          tuple(FIELD_MAP.keys()) == ELEMENT_ORDER
          and FIELD_MAP["参考绑定"]["top"] == ("AIGC生产模式",)
          and FIELD_MAP["镜头"]["shot"] == ("景别", "角度", "焦段", "运镜", "转场",
                                            "duration_s", "start_s", "end_s"),
          f"map={sorted(FIELD_MAP)}")

    # -----------------------------------------------------------------
    print("T1 基础渲染 (raw contract 形态)")
    contract = _mk_contract()
    out = render_storyboard_prompts(contract)
    check("T1 返回结构 {per_shot, render_meta} 且 per_shot 3 条",
          set(out.keys()) == {"per_shot", "render_meta"} and len(out["per_shot"]) == 3,
          f"keys={sorted(out)} n={len(out['per_shot'])}")
    m = out["render_meta"]
    check("T1 meta 默认路由: model_key=GENERIC / source_form=raw_contract / "
          "shot_count=3 / contract_version=1 / deterministic=True",
          m["model_key"] == "GENERIC" and m["source_form"] == "raw_contract"
          and m["shot_count"] == 3 and m["contract_version"] == 1
          and m["deterministic"] is True and m["total_duration_s"] == 7.8,
          f"meta={m}")
    hdrs = ["【%s】" % e for e in ELEMENT_ORDER]
    all_have = all(all(h in t for h in hdrs) for t in _texts(out))
    check("T1 每镜 7 段头全在", all_have,
          f"missing={[h for t in _texts(out) for h in hdrs if h not in t][:4]}")
    order_ok = all(
        [t.find(h) for h in hdrs] == sorted(t.find(h) for h in hdrs)
        and all(t.find(h) >= 0 for h in hdrs)
        for t in _texts(out))
    check("T1 段头出现顺序 == 七要素固定顺序 (find 下标递增)", order_ok)
    check("T1 镜号保真保型 [1, 2, 'S3']",
          [p["镜号"] for p in out["per_shot"]] == [1, 2, "S3"],
          f"ids={[p['镜号'] for p in out['per_shot']]}")
    check("T1 结构化字段逐字段映射落地 (镜1 文本含 主体/景别/焦段/运镜/时长/色彩/音频/约束)",
          "主体: 父亲的手停在砧板上" in _texts(out)[0]
          and "景别: 全景" in _texts(out)[0] and "焦段: 35mm" in _texts(out)[0]
          and "运镜: 缓推" in _texts(out)[0] and "时长: 3.8s" in _texts(out)[0]
          and "色彩: 冷灰" in _texts(out)[0] and "音频: 雨声" in _texts(out)[0]
          and "无字幕/无水印" in _texts(out)[0],
          f"text0={_texts(out)[0][:200]}")

    # -----------------------------------------------------------------
    print("T2 确定性 (同输入逐字节)")
    out2 = render_storyboard_prompts(contract)
    check("T2 同 dict 两次渲染 → 全结果逐字节一致",
          json.dumps(out, ensure_ascii=False, sort_keys=True)
          == json.dumps(out2, ensure_ascii=False, sort_keys=True))
    out3 = render_storyboard_prompts(_copy.deepcopy(contract))
    check("T2 deepcopy 输入 → 渲染逐字节一致",
          json.dumps(out, ensure_ascii=False, sort_keys=True)
          == json.dumps(out3, ensure_ascii=False, sort_keys=True))
    out4 = render_storyboard_prompts(json.loads(json.dumps(contract)))
    check("T2 JSON round-trip 输入 → 渲染逐字节一致",
          json.dumps(out, ensure_ascii=False, sort_keys=True)
          == json.dumps(out4, ensure_ascii=False, sort_keys=True))
    rep = validate_storyboard(_mk_contract())
    out5 = render_storyboard_prompts(rep)
    check("T2 validate 报告形态与 raw 形态渲染文本一致 (同 normalize 同源)",
          [p["prompt_text"] for p in out5["per_shot"]] == _texts(out)
          and out5["render_meta"]["source_form"] == "validate_report"
          and out5["render_meta"]["contract_ok"] is True,
          f"form={out5['render_meta']['source_form']}")

    # -----------------------------------------------------------------
    print("T3 model_key 路由差异")
    o_seed = render_storyboard_prompts(contract, "SEEDANCE_25")
    o_wan = render_storyboard_prompts(contract, "WAN_30")
    o_gen = render_storyboard_prompts(contract, "GENERIC")
    t_seed, t_wan, t_gen = _texts(o_seed)[0], _texts(o_wan)[0], _texts(o_gen)[0]
    check("T3 同镜三键产出两两互异 (SEEDANCE/WAN/GENERIC)",
          t_seed != t_wan and t_seed != t_gen and t_wan != t_gen)
    from master_director_data import SEEDANCE_25_CAPABILITIES
    caps_core = SEEDANCE_25_CAPABILITIES.get("core_upgrades", {})
    check("T3 SEEDANCE: meta capabilities_version 只读引用能力表 version 且参数行含单镜时长上限",
          o_seed["render_meta"]["capabilities_version"] == SEEDANCE_25_CAPABILITIES.get("version")
          and o_seed["render_meta"]["capabilities_source"] == "master_director_data.SEEDANCE_25_CAPABILITIES"
          and ("单镜时长≤%s 秒" % ("%g" % float(caps_core["max_duration_single_shot"]))) in t_seed,
          f"ver={o_seed['render_meta']['capabilities_version']}")
    check("T3 SEEDANCE: 时间戳锚指令 + 相对引用时间轴 (镜2: 3.8-6.3s)",
          "秒级时间戳锚" in t_seed and "时间轴: 3.8-6.3s" in _texts(o_seed)[1],
          f"t1={_texts(o_seed)[1][:160]}")
    check("T3 WAN: 含 简洁动作 与 美学 侧重标记, 零能力表版本",
          "一镜一事" in t_wan and "美学关键词前置" in t_wan
          and o_wan["render_meta"]["capabilities_version"] is None
          and o_wan["render_meta"]["model_traits"] == ["中文提示词友好", "简洁动作", "强美学"],
          f"traits={o_wan['render_meta']['model_traits']}")
    check("T3 GENERIC: 零模型专属标记 (无秒级时间戳锚/无一镜一事) 且 traits 空表",
          "秒级时间戳锚" not in t_gen and "一镜一事" not in t_gen
          and o_gen["render_meta"]["model_traits"] == []
          and o_gen["render_meta"]["capabilities_version"] is None,
          f"t={t_gen[:120]}")
    ok_unk, msg_unk = _raises_value_error(
        lambda: render_storyboard_prompts(contract, "KLING_99"))
    check("T3 未知 model_key → 诚实 ValueError 且消息列出全部已知键",
          ok_unk and all(k in msg_unk for k in MODEL_KEYS), f"msg={msg_unk[:160]}")
    ok_cs, msg_cs = _raises_value_error(
        lambda: render_storyboard_prompts(contract, "seedance_25"))
    check("T3 键名大小写敏感 ('seedance_25' → ValueError 不静默兜底)", ok_cs, f"msg={msg_cs[:120]}")

    # -----------------------------------------------------------------
    print("T4 坏输入诚实报错")
    ok1, m1 = _raises_value_error(lambda: render_storyboard_prompts(["不是dict"]))
    check("T4 非 dict 输入 → ValueError (不抛裸 TypeError)", ok1, f"msg={m1[:120]}")
    ok2, m2 = _raises_value_error(lambda: render_storyboard_prompts({"分镜表": []}))
    check("T4 无 contract_version 且非报告 → ValueError", ok2, f"msg={m2[:120]}")
    ok3, m3 = _raises_value_error(
        lambda: render_storyboard_prompts({"contract_version": 1, "导演": "x"}))
    check("T4 缺 '分镜表' → ValueError", ok3 and "分镜表" in m3, f"msg={m3[:120]}")
    ok4, m4 = _raises_value_error(
        lambda: render_storyboard_prompts({"contract_version": 1, "分镜表": []}))
    check("T4 空分镜表 → ValueError", ok4 and "空" in m4, f"msg={m4[:120]}")
    ok5, m5 = _raises_value_error(
        lambda: render_storyboard_prompts({"contract_version": 1,
                                           "分镜表": [{"镜号": 1, "时长": 1.0}, "不是dict"]}))
    check("T4 镜非 dict → ValueError 定位到 分镜表[1]", ok5 and "分镜表[1]" in m5,
          f"msg={m5[:120]}")
    ok6, m6 = _raises_value_error(
        lambda: render_storyboard_prompts({"contract_version": 1,
                                           "分镜表": [{"时长": 1.0}]}))
    check("T4 镜缺有效镜号 → ValueError", ok6 and "镜号" in m6, f"msg={m6[:120]}")
    ok7, m7 = _raises_value_error(lambda: render_storyboard_prompts({"normalized": None}))
    check("T4 validate 报告 normalized=None → ValueError (不抛裸 AttributeError)", ok7,
          f"msg={m7[:120]}")
    ok8, m8 = _raises_value_error(lambda: render_storyboard_prompts(None))
    check("T4 None 输入 → ValueError", ok8, f"msg={m8[:120]}")

    # -----------------------------------------------------------------
    print("T5 extra 字段不渲染不炸")
    texts = _texts(render_storyboard_prompts(_mk_contract()))
    check("T5 镜内 extra 值绝不出现在任何渲染文本中",
          all("extra-绝不应渲染-42" not in t for t in texts))
    wide = {"contract_version": 1, "项目级扩展": {"anything": [1, 2, 3]},
            "分镜表": [{"镜号": 1, "时长": 1.0, "景别": "全景", "镜内扩展": "zzz-extra"}]}
    ok_wide, texts_wide = None, None
    try:
        texts_wide = _texts(render_storyboard_prompts(wide))
        ok_wide = True
    except Exception as e_w:
        ok_wide = False
        texts_wide = ["%s: %s" % (type(e_w).__name__, e_w)]
    check("T5 顶层/镜内未知键共存 → 不炸且未知值零渗出",
          ok_wide and len(texts_wide) == 1
          and all("zzz-extra" not in t and "anything" not in t for t in texts_wide),
          f"t={texts_wide[0][:120]}")

    # -----------------------------------------------------------------
    print("T6 真实 Cinematic 集成 (真 build 固定输入)")
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
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        _main_txt, cine_json = node.build(**BUILD_KWARGS)
    cine_data = json.loads(cine_json)
    real_out = render_storyboard_prompts(cine_data)
    real_texts = _texts(real_out)
    n_shots = len(cine_data["分镜表"])
    check("T6 真实产物渲染: per_shot 数 == 分镜数 且 meta.shot_count 对齐",
          len(real_texts) == n_shots and real_out["render_meta"]["shot_count"] == n_shots,
          f"n={len(real_texts)} shots={n_shots}")
    check("T6 真实产物每镜 7 段全在且顺序正确",
          all(all(h in t for h in hdrs)
              and [t.find(h) for h in hdrs] == sorted(t.find(h) for h in hdrs)
              for t in real_texts))
    check("T6 真实产物每镜键 ⊆ 契约 32 键且镜号保真",
          all(set(s.keys()) <= set(CANON_SHOT_KEYS) for s in cine_data["分镜表"])
          and [p["镜号"] for p in real_out["per_shot"]]
          == [s["镜号"] for s in cine_data["分镜表"]],
          f"diff={sorted(set(cine_data['分镜表'][0].keys()) - set(CANON_SHOT_KEYS))}")
    seed_real = render_storyboard_prompts(cine_data, "SEEDANCE_25")
    check("T6 真实产物 SEEDANCE 路由: 每镜含秒级时间戳锚或链断诚实留空 (零异常)",
          all(("秒级时间戳锚" in t) or ("时间轴" not in t)
              for t in _texts(seed_real)),
          f"meta={seed_real['render_meta']['capabilities_version']}")


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    _m_ver = re.search(r'version\s*=\s*"([^"]+)"',
                       open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read())
    results_doc = {
        "suite": "test_contract_render",
        "version": _m_ver.group(1) if _m_ver else "unknown",
        "pass": PASS,
        "fail": FAIL,
        "results": RESULTS,
    }
    out_json = os.path.join(HERE, "contract_render_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results_doc, f, ensure_ascii=False, indent=2)
    print(f"\n契约渲染层测试结果: {PASS} PASS / {FAIL} FAIL (证据: {out_json})")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
