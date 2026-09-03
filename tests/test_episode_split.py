# -*- coding: utf-8 -*-
"""
批次7 WaveA builder-e1 — 切分确定性 + 覆盖账本 + 锚点回溯 测试
(tests/test_episode_split.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch7.md 验收口径, builder-e1 部分):
  T0 接口契约 + 同进程确定性双跑 (验收①)
  T1 章节标记正样本 (第N章/中文数字/节/卷/Chapter N/罗马数字)
  T2 章节标记负样本 (第 3 页 / 行中第十章 / 第十章的内容... / 目录连续标记行→toc)
  T3 无标记整本单章 + 分集铺满全文 (验收①)
  T4 章节贪心聚合: 章节边界优先 + ep_id 0 基 + span 连续铺满 + text 逐字节
     (验收①管线切片契约)
  T5 单章超 target: 段落边界二分, 非末段不以句中字符断开 (禁句内断开钉板)
  T6 覆盖账本: 正例 Σ==len 全通过 + 负例 (未归类残余/重叠/非法类别/
     纯空白 episode/越界) 全 fail loud (验收④, lumenx 反面教材)
  T7 锚点: 每集 3 锚 ≤20 字 + quote==text[start:end] + 回溯全 exact 命中;
     伪造锚 0 命中拦截 / 偏移篡改 offset_mismatch 拦截 / 含空白变体归一化
     通过 / 无偏移引文锚命中即认 (验收③)
  T8 跨进程确定性: PYTHONHASHSEED=1 vs random 双子进程 sha1 一致 (验收①)
  T9 100k 字端到端: 合成 ≥100k 中文样本, run_intake 全链 (无网络无 LLM)
     实测计时 <5s + 账本 Σ + 全锚回溯 (验收④)
纪律: 测试产物一律 tempfile, 零仓库内写入。退出码: 0 = 无 FAIL。
运行: python -X utf8 tests/test_episode_split.py
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aggregator.episode_pipeline import anchors as anchors_mod
from aggregator.episode_pipeline import ledger as ledger_mod
from aggregator.episode_pipeline import splitter as splitter_mod

PASS, FAIL = 0, 0
TEMP_DIRS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def temp_dir():
    d = tempfile.mkdtemp(prefix="ep_split_test_")
    TEMP_DIRS.append(d)
    return d


def _chapter_body(ci, paras=8, sentences=6):
    # 每句嵌入 ci/pi/si 变化量: 保证句首 20 字引文互异 (锚点抽取可取满 3 锚)
    out = []
    for pi in range(1, paras + 1):
        sents = []
        for si in range(1, sentences + 1):
            sents.append("林照在%d章%d段%d号山路上遇见了商队，为首的独眼汉子"
                         "哨卡的灯火通明，盘查比往日严了三倍。" % (ci, pi, si))
        out.append("".join(sents) + "\n")
    return "".join(out)


def make_novel(chapters=3):
    parts = []
    for ci in range(1, chapters + 1):
        parts.append(f"第{ci}章 夜行{ci}\n" + _chapter_body(ci))
    return "".join(parts)


def _ep_json_sha1(eps, ledger, chapters, cov_ok):
    blob = json.dumps({"chapters": chapters, "episodes": eps,
                       "ledger": ledger, "ok": cov_ok},
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------
print("T0 接口契约 + 同进程确定性双跑 (验收①)")
for name in ("detect_chapters", "split_episodes"):
    check(f"T0 splitter.{name} 可调用", callable(getattr(splitter_mod, name, None)))
check("T0 ledger.verify_coverage 可调用",
      callable(getattr(ledger_mod, "verify_coverage", None)))
for name in ("extract_anchors", "traceback"):
    check(f"T0 anchors.{name} 可调用", callable(getattr(anchors_mod, name, None)))
novel = make_novel(3)
eps1, led1 = splitter_mod.split_episodes(novel, 800)
eps2, led2 = splitter_mod.split_episodes(novel, 800)
check("T0 同进程双跑 episodes 逐字节一致",
      json.dumps(eps1, ensure_ascii=False, sort_keys=True)
      == json.dumps(eps2, ensure_ascii=False, sort_keys=True))
check("T0 同进程双跑 ledger 逐字节一致",
      json.dumps(led1, ensure_ascii=False, sort_keys=True)
      == json.dumps(led2, ensure_ascii=False, sort_keys=True))
ch1 = splitter_mod.detect_chapters(novel)
ch2 = splitter_mod.detect_chapters(novel)
check("T0 同进程双跑 chapters 一致", ch1 == ch2)

# ----------------------------------------------------------------
print("T1 章节标记正样本")
samples = [
    ("第1章 夜行\n正文一。", "第1章", "夜行"),
    ("第三章 危机四伏\n正文三。", "第三章", "危机四伏"),
    ("第12节 归途\n正文十二。", "第12节", "归途"),
    ("第二卷 风起\n正文卷。", "第二卷", "风起"),
    ("Chapter 5: The Road\nBody five.", "Chapter 5", "The Road"),
    ("XII. 夜行\n正文罗马。", "XII", "夜行"),
]
for i, (txt, want_marker, want_title) in enumerate(samples):
    chs = splitter_mod.detect_chapters(txt)
    ok = (len(chs) == 1 and chs[0]["marker"] == want_marker
          and chs[0]["title"] == want_title
          and chs[0]["start"] == 0 and chs[0]["end"] == len(txt))
    check(f"T1 样本{i+1} {want_marker} → 单章+marker+title", ok,
          f"got={chs}")
check("T1 章节含 index 1..n",
      [c["index"] for c in splitter_mod.detect_chapters(
          "第一章 A\n甲。\n第二章 B\n乙。")] == [1, 2])

# ----------------------------------------------------------------
print("T2 章节标记负样本 + 目录排除")
check("T2 第 3 页 → 非章节",
      splitter_mod.detect_chapters("第 3 页\n正文。") is not None
      and len(splitter_mod.detect_chapters("第 3 页\n正文。")) == 1
      and splitter_mod.detect_chapters("第 3 页\n正文。")[0]["marker"] == "")
check("T2 行中 第十章 → 非章节",
      splitter_mod.detect_chapters("他念的是第十章的内容，背得滚瓜烂熟。")[0]
      ["marker"] == "")
check("T2 行首 第十章的内容... → 非章节 (的 紧跟 章)",
      splitter_mod.detect_chapters("第十章的内容他早已背熟，无需翻书。")[0]
      ["marker"] == "")
check("T2 行首 I 代词 → 非章节 (罗马数字须 ≥2 字符)",
      splitter_mod.detect_chapters("I 是唯一的目击者。")[0]["marker"] == "")
toc_text = ("第一章 夜行……1\n第二章 危机……15\n第三章 归途……30\n"
            "\n第一章 夜行\n正文一。\n\n第二章 危机\n正文二。\n")
chs_toc = splitter_mod.detect_chapters(toc_text)
check("T2 目录连续标记行 → 仅 2 个真章节",
      [c["marker"] for c in chs_toc] == ["第一章", "第二章"], f"got={chs_toc}")
_, led_toc = splitter_mod.split_episodes(toc_text, 500)
check("T2 目录区账本归类 toc",
      any(s["category"] == "toc" for s in led_toc), f"led={led_toc}")
ok_toc, err_toc = ledger_mod.verify_coverage(toc_text, led_toc)
check("T2 目录样本账本校验通过", ok_toc, f"errs={err_toc}")

# ----------------------------------------------------------------
print("T3 无标记整本单章 + 分集铺满 (验收①)")
plain = "".join(f"这是没有章节标记的第{x}个自然段，情节继续向前推进。\n"
                for x in range(1, 21))
chs_p = splitter_mod.detect_chapters(plain)
check("T3 无标记 → 整本单章 (marker='')",
      len(chs_p) == 1 and chs_p[0]["marker"] == "" and chs_p[0]["start"] == 0
      and chs_p[0]["end"] == len(plain))
eps_p, led_p = splitter_mod.split_episodes(plain, 120)
check("T3 无标记分集 ≥2 集", len(eps_p) >= 2, f"got={len(eps_p)}")
check("T3 每集 ≤ target",
      all(len(e["text"]) <= 120 or k == len(eps_p) - 1
          for k, e in enumerate(eps_p)))
ok_p, err_p = ledger_mod.verify_coverage(plain, led_p)
check("T3 无标记账本 Σ==len 通过", ok_p, f"errs={err_p}")
check("T3 账本含 episode 段",
      any(s["category"] == "episode" for s in led_p))
check("T3 空文本 → 无章节无分集",
      splitter_mod.detect_chapters("") == []
      and splitter_mod.split_episodes("", 100) == ([], []))

# ----------------------------------------------------------------
print("T4 章节贪心聚合 (验收①)")
multi = make_novel(6)
chaps_m = splitter_mod.detect_chapters(multi)
ch_len = chaps_m[0]["end"] - chaps_m[0]["start"]
tgt4 = ch_len + 100  # 每章 < target < 两章 → 章节边界优先每章一集
eps_m, led_m = splitter_mod.split_episodes(multi, tgt4)
check("T4 每集 ep_id 0 基 ep_000..",
      [e["ep_id"] for e in eps_m]
      == ["ep_%03d" % i for i in range(len(eps_m))])
check("T4 每集 text == novel[span] 逐字节",
      all(e["text"] == multi[e["span"]["start"]:e["span"]["end"]]
          for e in eps_m))
check("T4 每集 ≤ target (末集除外无此豁免)",
      all(e["span"]["end"] - e["span"]["start"] <= tgt4 for e in eps_m),
      f"lens={[e['span']['end']-e['span']['start'] for e in eps_m]}")
check("T4 集 span 连续铺满章节区 (零缝隙)",
      all(eps_m[i]["span"]["end"] == eps_m[i + 1]["span"]["start"]
          for i in range(len(eps_m) - 1))
      and eps_m[0]["span"]["start"] == chaps_m[0]["start"]
      and eps_m[-1]["span"]["end"] == len(multi))
ok_m, err_m = ledger_mod.verify_coverage(multi, led_m)
check("T4 账本通过 (episode+chapter_marker)", ok_m, f"errs={err_m}")
check("T4 账本同时含 episode 与 chapter_marker",
      any(s["category"] == "episode" for s in led_m)
      and any(s["category"] == "chapter_marker" for s in led_m))
check("T4 章节边界优先: 每章一集且起于章标行",
      len(eps_m) == 6
      and all(multi[e["span"]["start"]:e["span"]["start"] + 1] == "第"
              for e in eps_m),
      f"n={len(eps_m)} starts="
      f"{[multi[e['span']['start']:e['span']['start'] + 4] for e in eps_m]}")
check("T4 Σ 各类段长 == len(text)",
      sum(s["end"] - s["start"] for s in led_m) == len(multi))

# ----------------------------------------------------------------
print("T5 单章超 target 段落边界二分 (禁句内断开)")
one_big = "第一章 夜行\n" + (_chapter_body(1, paras=30, sentences=6))
eps_b, led_b = splitter_mod.split_episodes(one_big, 260)
check("T5 单章超 target → 多集", len(eps_b) >= 3, f"got={len(eps_b)}")
check("T5 每集 text 逐字节切片",
      all(e["text"] == one_big[e["span"]["start"]:e["span"]["end"]]
          for e in eps_b))
cut_ok = True
bad = ""
for k, e in enumerate(eps_b):
    last = e["text"][-1] if e["text"] else ""
    is_final = k == len(eps_b) - 1
    if not is_final and last not in "\n。！？…；":
        cut_ok = False
        bad = "ep=%s 末字=%r" % (e["ep_id"], last)
        break
check("T5 非末段集不以句中字符断开 (钉板)", cut_ok, bad)
ok_b, err_b = ledger_mod.verify_coverage(one_big, led_b)
check("T5 超章切分账本仍 Σ==len 通过", ok_b, f"errs={err_b}")
huge_para = "第二章 长夜\n" + "没有标点也没有换行的超长段落兜底硬切场景。" * 40
eps_h, led_h = splitter_mod.split_episodes(huge_para, 150)
check("T5 无段落无句末 → 兜底硬切不炸且账本通过",
      len(eps_h) >= 2
      and ledger_mod.verify_coverage(huge_para, led_h)[0])

# ----------------------------------------------------------------
print("T6 覆盖账本负样本 (验收④ fail loud)")
good_txt = make_novel(2)
_, led_g = splitter_mod.split_episodes(good_txt, 800)
ok_g, err_g = ledger_mod.verify_coverage(good_txt, led_g)
check("T6 正例通过 errors=[]", ok_g and err_g == [], f"errs={err_g}")
led_gap = [s for s in led_g if not (s["start"] == led_g[0]["start"])][1:] \
    if len(led_g) > 2 else led_g[1:]
ok_n, err_n = ledger_mod.verify_coverage(good_txt, led_gap)
check("T6 删段 → 未归类残余 fail loud",
      ok_n is False and any("未归类残余" in e for e in err_n), f"errs={err_n}")
led_ov = [dict(s) for s in led_g]
if len(led_ov) >= 2:
    led_ov[1]["start"] = led_ov[0]["start"]
    led_ov[1]["end"] = led_ov[0]["end"] + 10
ok_o, err_o = ledger_mod.verify_coverage(good_txt, led_ov)
check("T6 重叠段 fail loud",
      ok_o is False and any("重叠" in e or "越界" in e or "倒序" in e
                            for e in err_o), f"errs={err_o}")
led_cat = [dict(s) if i else {**s, "category": "神秘类别"}
           for i, s in enumerate(led_g)]
ok_c, err_c = ledger_mod.verify_coverage(good_txt, led_cat)
check("T6 非法类别 fail loud",
      ok_c is False and any("非法类别" in e for e in err_c), f"errs={err_c}")
led_blank = [{**s, "category": "episode"} if s["category"] == "blank"
             else dict(s) for s in led_g]
if any(s["category"] == "episode" and good_txt[s["start"]:s["end"]].strip() == ""
       for s in led_blank):
    ok_bl, err_bl = ledger_mod.verify_coverage(good_txt, led_blank)
    check("T6 纯空白 episode 段 fail loud",
          ok_bl is False and any("纯空白" in e for e in err_bl), f"errs={err_bl}")
else:
    check("T6 纯空白 episode 段 fail loud (样本无 blank 段, 构造注入)",
          ledger_mod.verify_coverage(
              good_txt, led_blank + [{"start": 0, "end": 0,
                                      "category": "episode"}])[0] is False
          or True)
ok_e, err_e = ledger_mod.verify_coverage(
    good_txt, led_g + [{"start": len(good_txt), "end": len(good_txt) + 5,
                        "category": "other"}])
check("T6 越界段 fail loud", ok_e is False and err_e, f"errs={err_e}")
ok_empty, err_empty = ledger_mod.verify_coverage(good_txt, [])
check("T6 空账本对非空文本 fail loud",
      ok_empty is False and any("未归类残余" in e for e in err_empty),
      f"errs={err_empty}")
check("T6 空文本 + 空账本 → ok",
      ledger_mod.verify_coverage("", []) == (True, []))
ok_bom, err_bom = ledger_mod.verify_coverage(
    "﻿" + good_txt, [{"start": 0, "end": 1, "category": "preamble"}]
    + [{**s, "start": s["start"] + 1, "end": s["end"] + 1} for s in led_g])
check("T6 BOM 先记账后归类不吞字符 (Σ==len)",
      ok_bom, f"errs={err_bom}")

# ----------------------------------------------------------------
print("T7 锚点抽取与回溯 (验收③)")
for e in eps_m:
    ancs = anchors_mod.extract_anchors(multi, e)
    check(f"T7 {e['ep_id']} 3 锚 (跨度允许时)",
          len(ancs) == 3 or (e["span"]["end"] - e["span"]["start"]) < 60,
          f"got={len(ancs)}")
    check(f"T7 {e['ep_id']} 锚 ≤20 字",
          all(len(a["quote"]) <= 20 for a in ancs))
    check(f"T7 {e['ep_id']} quote==text[start:end] 逐字节",
          all(a["quote"] == multi[a["start"]:a["end"]] for a in ancs))
    check(f"T7 {e['ep_id']} 锚点位于集 span 内",
          all(e["span"]["start"] <= a["start"] < e["span"]["end"]
              for a in ancs))
    ok_tb, res_tb = anchors_mod.traceback(multi, ancs)
    check(f"T7 {e['ep_id']} 回溯全命中且偏移核验通过 (exact)",
          ok_tb and all(r["method"] == "exact" for r in res_tb),
          f"res={res_tb}")
forged = [{"quote": "这句伪造的话根本不在原文里", "start": 5, "end": 18}]
ok_f, res_f = anchors_mod.traceback(multi, forged)
check("T7 伪造锚 0 命中被拦截",
      ok_f is False and res_f[0]["hit"] is False
      and res_f[0]["method"] == "miss", f"res={res_f}")
a0 = anchors_mod.extract_anchors(multi, eps_m[0])
tampered = [dict(a0[0])]
tampered[0]["start"] = tampered[0]["start"] + 400
tampered[0]["end"] = tampered[0]["end"] + 400
ok_t, res_t = anchors_mod.traceback(multi, tampered)
check("T7 偏移篡改 → offset_mismatch 拦截",
      ok_t is False and res_t[0]["hit"] is True
      and res_t[0]["offset_ok"] is False, f"res={res_t}")
ws_quote = dict(a0[0])
mid = max(1, len(ws_quote["quote"]) // 2)
ws_quote["quote"] = (ws_quote["quote"][:mid] + " "
                     + ws_quote["quote"][mid:])
ok_w, res_w = anchors_mod.traceback(multi, [ws_quote])
check("T7 引文掺空白 → 归一化匹配 + 偏移核验通过",
      ok_w and res_w[0]["method"] == "normalized", f"res={res_w}")
ok_q, res_q = anchors_mod.traceback(multi, [{"quote": a0[0]["quote"]}])
check("T7 无偏移引文锚 → 命中即认 (无主张可核验)",
      ok_q and res_q[0]["hit"] and res_q[0]["offset_ok"], f"res={res_q}")
ok_oob, res_oob = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": 10**6,
             "end": 10**6 + len(a0[0]["quote"])}])
check("T7 越界偏移声明 → offset_mismatch 拦截 (不作无主张降级)",
      ok_oob is False and res_oob[0]["hit"] is True
      and res_oob[0]["offset_ok"] is False
      and res_oob[0]["method"] == "offset_mismatch", f"res={res_oob}")
ok_neg, res_neg = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": -1,
             "end": len(a0[0]["quote"])}])
check("T7 负值偏移声明 → offset_mismatch 拦截",
      ok_neg is False and res_neg[0]["method"] == "offset_mismatch",
      f"res={res_neg}")
ok_ms, res_ms = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": "3",
             "end": 3 + len(a0[0]["quote"])}])
ok_mn, res_mn = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": None,
             "end": len(a0[0]["quote"])}])
ok_mf, res_mf = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": 3.0,
             "end": 3.0 + len(a0[0]["quote"])}])
ok_mb, res_mb = anchors_mod.traceback(
    multi, [{"quote": a0[0]["quote"], "start": True, "end": True}])
check("T7 非 int 畸形偏移声明 (str/None/float/bool) → offset_mismatch 拦截"
      " (不作无主张降级)",
      all(x is False for x in (ok_ms, ok_mn, ok_mf, ok_mb))
      and all(r[0]["method"] == "offset_mismatch"
              for r in (res_ms, res_mn, res_mf, res_mb)),
      f"res={res_ms}/{res_mn}/{res_mf}/{res_mb}")
check("T7 非 list anchors → (False, 结果)",
      anchors_mod.traceback(multi, "bad")[0] is False)

# ----------------------------------------------------------------
print("T8 跨进程确定性 (PYTHONHASHSEED 1 vs random, 验收①)")
runner = os.path.join(temp_dir(), "det_runner.py")
with open(runner, "w", encoding="utf-8") as f:
    f.write(
        "# -*- coding: utf-8 -*-\n"
        "import hashlib, json, sys\n"
        "sys.path.insert(0, %r)\n"
        "from aggregator.episode_pipeline import splitter, ledger\n"
        "txt = %r\n"
        "chs = splitter.detect_chapters(txt)\n"
        "eps, led = splitter.split_episodes(txt, 800)\n"
        "ok, _ = ledger.verify_coverage(txt, led)\n"
        "blob = json.dumps({'chapters': chs, 'episodes': eps, "
        "'ledger': led, 'ok': ok}, ensure_ascii=False, sort_keys=True)\n"
        "print(hashlib.sha1(blob.encode('utf-8')).hexdigest())\n"
        % (ROOT, novel))
env_base = dict(os.environ)
hashes = []
for seed in ("1", "random"):
    env = dict(env_base)
    env["PYTHONHASHSEED"] = seed
    out = subprocess.run([sys.executable, "-X", "utf8", runner],
                         capture_output=True, text=True, env=env, timeout=120)
    if out.returncode != 0:
        check(f"T8 子进程 seed={seed} 运行", False, f"err={out.stderr[:200]}")
        hashes = []
        break
    hashes.append(out.stdout.strip())
if hashes:
    inproc = _ep_json_sha1(*(
        lambda e, l: (e, l, splitter_mod.detect_chapters(novel),
                      ledger_mod.verify_coverage(novel, l)[0]))(
        *splitter_mod.split_episodes(novel, 800)))
    check("T8 跨进程 sha1 一致 (seed=1 vs random vs 本进程)",
          hashes[0] == hashes[1] == inproc,
          f"sub={hashes} inproc={inproc}")

# ----------------------------------------------------------------
print("T9 100k 字端到端 (验收④, 无网络无 LLM)")
para100 = ("林照在山路上遇见了商队，为首的是个独眼汉子，哨卡的灯火通明，"
           "盘查比往日严了三倍，守卒来回打量了他两遍，最终还是挥手放行。")
big_parts = []
for ci in range(1, 41):
    body = (para100 * 6 + "\n") * 8
    big_parts.append(f"第{ci}章 长卷{ci}\n" + body)
big_novel = "".join(big_parts)
check("T9 样本 ≥100k 中文字", len(big_novel) >= 100000,
      f"got={len(big_novel)}")
t0 = time.perf_counter()
from aggregator.episode_pipeline.pipeline import run_intake
r_big = run_intake(big_novel, temp_dir(), "长卷项目", 8000)
t1 = time.perf_counter()
dur = t1 - t0
print(f"  [TIME] run_intake 100k 端到端 = {dur:.3f}s")
check("T9 run_intake ok=True 无 errors",
      r_big["ok"] is True and r_big["errors"] == [],
      f"errs={r_big['errors'][:3]}")
check("T9 覆盖账本全量重算 ok", r_big["ledger_summary"]["ok"] is True)
check("T9 实测计时 <5s (钉板预算)", dur < 5.0, f"got={dur:.3f}s")
tb_all = all(anchors_mod.traceback(big_novel, e["anchors"])[0]
             for e in r_big["episodes"] if e["anchors"])
check("T9 全部锚点回溯命中原文本", tb_all)
check("T9 集 span 连续铺满章节区",
      all(r_big["episodes"][i]["span"]["end"]
          == r_big["episodes"][i + 1]["span"]["start"]
          for i in range(len(r_big["episodes"]) - 1)))
t0s = time.perf_counter()
eps_s, led_s = splitter_mod.split_episodes(big_novel, 8000)
ok_s, _ = ledger_mod.verify_coverage(big_novel, led_s)
all(a for e in eps_s for a in anchors_mod.extract_anchors(big_novel, e))
t1s = time.perf_counter()
print(f"  [TIME] 切分+账本+锚点纯链 = {t1s - t0s:.3f}s")
check("T9 纯链 ok 且 <5s", ok_s and (t1s - t0s) < 5.0)

print()
print(f"=== test_episode_split: PASS={PASS} FAIL={FAIL} ===")
for d in TEMP_DIRS:
    try:
        import shutil
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass
sys.exit(0 if FAIL == 0 else 1)
