# -*- coding: utf-8 -*-
"""
批次7 WaveA builder-e2 — 钩子三指标 + LLM轨诚实降级 + dm_memory 桥 + 断点续跑 测试
(tests/test_episode_hooks.py)
====================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch7.md 验收口径, builder-e2 部分):
  T0 常量与导出口径 (阈值/窗口/门面惰性导出)
  T1 m1 悬念/未决 正负构造样本 (验收②)
  T2 m2 主角赌注/危机 正负构造样本, 显式主角 + 文本挖掘主角 (验收②)
  T3 m3 新信息揭示 正负构造样本 (验收②)
  T4 hook_check 只标记不阻断 + flags 显式 + 确定性双跑 (验收②)
  T5 LLM 轨诚实降级: 无凭据 unavailable / 不可达 degraded / 回声 / 截断 /
     成功只加注释字段且原文 span/text 逐字节不可变 (验收⑤)
  T6 memory_bridge: 落盘形状 + 脱敏 (R2 MED-4) + 全保护永不致命 +
     additive(既有 anchors.json 保留) (验收⑥)
  T7 pipeline 单元: safe_name 与 dm_memory 同配方对齐 + 碰撞落盘互不覆盖 /
     core_pack_seed 32字段 parse_core_pack 兼容 / pipeline_id=sha1[:16] /
     输入校验 fail loud (验收⑦⑤)
  T8 pipeline 端到端 (依赖 e1 splitter/ledger/anchors):
     产物 9 键 + 锚点回溯 + llm_track unavailable + additive 零漂移逐字节断言 (⑥)
     + 检查点跳过实测 mtime/重生成计数 + steps 记 ep_000.. 直证 + 先 mark_done
     前两集再重跑的中断模拟 (⑦) + fail loud 注入 (errors 不静默)
纪律: 测试产物一律 tempfile, 零仓库内写入; e1 模块缺席时 T8 逐用例显式标
      BLOCKED_BY_E1 (诚实计数, 不造 stub)。退出码: 0 = 无 FAIL (BLOCKED 不计)。
运行: python -X utf8 tests/test_episode_hooks.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aggregator.episode_pipeline import hooks as hooks_mod
from aggregator.episode_pipeline import llm_refine as lr
from aggregator.episode_pipeline import memory_bridge as mb
from aggregator.episode_pipeline import pipeline as pl
from aggregator.node_base import parse_core_pack

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
    d = tempfile.mkdtemp(prefix="ep_hooks_test_")
    TEMP_DIRS.append(d)
    return d


# e1 可用性探测 (只 import, 不读写其文件)
def _e1_available():
    try:
        from aggregator.episode_pipeline import splitter, ledger, anchors  # noqa: F401
        return True
    except Exception:
        return False


E1 = _e1_available()
_BLOCKED = []


def blocked(label):
    global PASS, FAIL
    _BLOCKED.append(label)
    print(f"  [BLOCKED_BY_E1] {label}")


def walk_bytes(root):
    """相对路径 -> 字节 的确定性快照 (零漂移断言用)。"""
    out = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            with open(p, "rb") as f:
                out[rel] = f.read()
    return out


def mtime_ns(path):
    return os.stat(path).st_mtime_ns


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 常量与导出口径")
    check("T0 阈值常量导出 HOOK_THRESHOLD_M1/M2/M3",
          hooks_mod.HOOK_THRESHOLD_M1 == 0.5 and hooks_mod.HOOK_THRESHOLD_M2 == 0.5
          and hooks_mod.HOOK_THRESHOLD_M3 == 0.5)
    check("T0 尾段窗口常量 HOOK_ENDING_WINDOW_CHARS=400",
          hooks_mod.HOOK_ENDING_WINDOW_CHARS == 400)
    check("T0 门面惰性导出 hook_metrics/hook_check/refine_available 可解析",
          callable(hooks_mod.hook_metrics) and callable(hooks_mod.hook_check)
          and callable(lr.refine_available) and callable(lr.refine_episode))
    try:
        import aggregator.episode_pipeline as ep_pkg
        check("T0 门面 __getattr__ 惰性导出 hook_metrics 同一函数",
              ep_pkg.hook_metrics is hooks_mod.hook_metrics)
    except Exception as exc:
        check("T0 门面 __getattr__ 惰性导出 hook_metrics 同一函数", False, str(exc))

    # -----------------------------------------------------------------
    print("T1 m1 悬念/未决 正负构造样本 (验收②)")
    m = hooks_mod.hook_metrics("他说完这句话，转身走进雨里。还有人活着吗？答案无人知晓。", {})
    check("T1 m1 正样本(问句+未决标记) 达标", m["m1_cliffhanger"] >= hooks_mod.HOOK_THRESHOLD_M1,
          f"got={m['m1_cliffhanger']}")
    m = hooks_mod.hook_metrics("灯忽然灭了，屋里没有人回答……", {})
    check("T1 m1 正样本(未决标记×2 含省略号收尾) 达标",
          m["m1_cliffhanger"] >= hooks_mod.HOOK_THRESHOLD_M1, f"got={m['m1_cliffhanger']}")
    m = hooks_mod.hook_metrics("他吃完了饭，收拾碗筷，然后上床睡觉。窗外一片安静。", {})
    check("T1 m1 负样本(平淡收尾) 未达标", m["m1_cliffhanger"] < hooks_mod.HOOK_THRESHOLD_M1,
          f"got={m['m1_cliffhanger']}")
    m = hooks_mod.hook_metrics("", {})
    check("T1 m1 空尾段 = 0", m["m1_cliffhanger"] == 0.0)

    # -----------------------------------------------------------------
    print("T2 m2 主角赌注/危机 正负构造样本 (验收②)")
    full = ("林照推开柴门，山风灌进来。林照回头看了一眼远处的火光，握紧了刀。"
            "村口的老槐树倒在血泊里，林照蹲下身，摸了摸树干上的刀痕，站起身。")
    ending_hit = "夜里三更，林照听见马蹄声——是追杀的人到了。"
    m = hooks_mod.hook_metrics(ending_hit, {"text": full})
    check("T2 m2 正样本(挖掘主角+危机词) 达标",
          m["m2_protagonist_stakes"] >= hooks_mod.HOOK_THRESHOLD_M2,
          f"got={m['m2_protagonist_stakes']}")
    m = hooks_mod.hook_metrics("夜里三更，林照听见马蹄声——追杀的人到了，他赌上了性命。",
                               {"text": full})
    check("T2 m2 强正样本(主角+危机+赌注) = 1.0",
          m["m2_protagonist_stakes"] == 1.0, f"got={m['m2_protagonist_stakes']}")
    m = hooks_mod.hook_metrics("深夜，山寨火起，喊杀声四面八方围拢过来。", {"text": full})
    check("T2 m2 负样本A(危机词但尾段无主角) 未达标",
          m["m2_protagonist_stakes"] < hooks_mod.HOOK_THRESHOLD_M2,
          f"got={m['m2_protagonist_stakes']}")
    m = hooks_mod.hook_metrics("林照把碗放下，吹熄了灯，屋里只剩呼吸声。", {"text": full})
    check("T2 m2 负样本B(主角在但无危机/赌注词) 未达标",
          m["m2_protagonist_stakes"] < hooks_mod.HOOK_THRESHOLD_M2,
          f"got={m['m2_protagonist_stakes']}")
    m = hooks_mod.hook_metrics("夜里三更，沈青听见马蹄声——是追杀的人到了。",
                               {"text": "无关文本", "主角": "沈青"})
    check("T2 m2 显式主角键(主角) 覆盖文本挖掘", m["m2_protagonist_stakes"] >= 0.5,
          f"got={m['m2_protagonist_stakes']}")
    m = hooks_mod.hook_metrics("夜里三更，Shen Qing 听见马蹄声——追杀的人到了。",
                               {"text": "x", "protagonist": "Shen Qing"})
    check("T2 m2 显式主角键(protagonist) 生效", m["m2_protagonist_stakes"] >= 0.5,
          f"got={m['m2_protagonist_stakes']}")

    # -----------------------------------------------------------------
    print("T3 m3 新信息揭示 正负构造样本 (验收②)")
    m = hooks_mod.hook_metrics("父亲留下来的铁盒终于打开了，原来里面是半张海图。", {})
    check("T3 m3 正样本(揭示标记×1) 达标", m["m3_new_reveal"] >= hooks_mod.HOOK_THRESHOLD_M3,
          f"got={m['m3_new_reveal']}")
    m = hooks_mod.hook_metrics("他终于说出了真相：原来当年那场大火另有其人。", {})
    check("T3 m3 强正样本(揭示标记×2) = 1.0", m["m3_new_reveal"] == 1.0,
          f"got={m['m3_new_reveal']}")
    m = hooks_mod.hook_metrics("两人默默把桌子擦干净，各自回房休息了。", {})
    check("T3 m3 负样本(无揭示标记) 未达标", m["m3_new_reveal"] < hooks_mod.HOOK_THRESHOLD_M3,
          f"got={m['m3_new_reveal']}")

    # -----------------------------------------------------------------
    print("T4 hook_check 只标记不阻断 + flags 显式 + 确定性双跑 (验收②)")
    strong_ep = {
        "ep_id": "ep_001", "title": "第一章 夜雨",
        "text": ("林照进了城，客栈里人声嘈杂。林照要了一碗面，慢慢吃完。"
                 "林照数了数铜钱，还差三文。掌柜的瞪了他一眼，林照把刀放在了桌上。"
                 "半夜，林照翻墙出城，身后火把连成了一条线。追兵到了。原来城门早被封死，"
                 "还有活路吗？他赌上性命翻上马背。"),
    }
    r1 = hooks_mod.hook_check(strong_ep)
    check("T4 强钩子分集 passed=True 且 flags 空",
          r1["passed"] is True and r1["flags"] == [], f"got={r1}")
    weak_ep = {"ep_id": "ep_002", "title": "第二章 白水",
               "text": "他吃完了饭，收拾碗筷，然后上床睡觉。屋里一片安静。"}
    r2 = hooks_mod.hook_check(weak_ep)
    check("T4 欠钩子分集 passed=False", r2["passed"] is False)
    check("T4 欠钩子 flags 逐指标显式 (m1/m2/m3 各一条)",
          len(r2["flags"]) == 3 and all(("m%d" % i) in r2["flags"][i - 1] for i in (1, 2, 3)),
          f"got={r2['flags']}")
    check("T4 只标记不阻断: 返回 dict 不抛错", isinstance(r2, dict) and "flags" in r2)
    for bad in (None, {}, {"text": 123}, {"text": None}, "不是dict"):
        try:
            rr = hooks_mod.hook_check(bad)
            ok = isinstance(rr, dict) and {"m1", "m2", "m3", "passed", "flags"} <= set(rr)
        except Exception:
            ok = False
        check(f"T4 异常输入 {type(bad).__name__!r} 不抛错只标记", ok)
    check("T4 确定性: 同输入双跑逐字节一致",
          json.dumps(hooks_mod.hook_check(strong_ep), sort_keys=True)
          == json.dumps(r1, sort_keys=True))

    # -----------------------------------------------------------------
    print("T5 LLM 轨诚实降级 + 原文不可变 (验收⑤)")
    check("T5 无凭据 unavailable", lr.refine_available("", "") is False
          and lr.refine_available(None, None) is False
          and lr.refine_available("http://x", "") is False)
    check("T5 有凭据 available", lr.refine_available("http://x", "sk-test") is True)
    ep0 = {"ep_id": "ep_001", "title": "第一章",
           "span": {"start": 0, "end": 10},
           "text": "0123456789"}
    snap0 = json.dumps(ep0, ensure_ascii=False, sort_keys=True)
    refined, status = lr.refine_episode(ep0, "", "", "")
    check("T5 无凭据 refine_episode → (None,'unavailable')",
          refined is None and status == "unavailable", f"got={status}")
    check("T5 无凭据调用后输入 episode 逐字节未变",
          json.dumps(ep0, ensure_ascii=False, sort_keys=True) == snap0)
    refined, status = lr.refine_episode(ep0, "http://127.0.0.1:1", "k", "")
    check("T5 不可达 api_url → degraded:<原因> (连接失败诚实标注)",
          refined is None and status.startswith("degraded"), f"got={status}")
    check("T5 不可达调用后输入 episode 逐字节未变",
          json.dumps(ep0, ensure_ascii=False, sort_keys=True) == snap0)

    good_json = json.dumps({"logline": "少年踏上寻母之路。",
                            "scenes": [{"标题": "雨夜出发", "摘要": "林照背起行囊"}]},
                           ensure_ascii=False)
    orig_call = lr._call_llm
    try:
        lr._call_llm = lambda a, k, m, s, u: (good_json, "")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 成功 → status='refined'", status == "refined", f"got={status}")
        check("T5 refined 只加注释字段 (logline/refined_scenes/llm_generated=True)",
              refined is not None and refined.get("llm_generated") is True
              and refined.get("logline") == "少年踏上寻母之路。"
              and isinstance(refined.get("refined_scenes"), list)
              and refined["refined_scenes"][0]["标题"] == "雨夜出发")
        check("T5 原文 span/text 逐字节不可变",
              refined["span"] == {"start": 0, "end": 10} and refined["text"] == "0123456789")
        check("T5 原 episode 对象未被污染 (无新增键)",
              json.dumps(ep0, ensure_ascii=False, sort_keys=True) == snap0
              and "logline" not in ep0)
        lr._call_llm = lambda a, k, m, s, u: (u, "")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 回声照抄提示词 → degraded:回声",
              refined is None and status.startswith("degraded:回声照抄提示词"),
              f"got={status}")
        lr._call_llm = lambda a, k, m, s, u: (ep0["text"], "")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 回声照抄原文 → degraded:回声(原文)",
              refined is None and status.startswith("degraded:回声照抄原文"),
              f"got={status}")
        lr._call_llm = lambda a, k, m, s, u: ('{"logline": "abc", "scenes": [{"标题": "x"', "")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 截断输出 → degraded:输出截断/JSON不可解析",
              refined is None and status.startswith("degraded:输出截断"),
              f"got={status}")
        lr._call_llm = lambda a, k, m, s, u: ('{"foo": 1}', "")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 结构不符 → degraded:响应缺少有效字段",
              refined is None and status.startswith("degraded:响应缺少"),
              f"got={status}")
        lr._call_llm = lambda a, k, m, s, u: ("", "HTTP 500: 注入错误")
        refined, status = lr.refine_episode(ep0, "http://x", "k", "m")
        check("T5 调用报错 → degraded:llm调用失败 透传原因",
              refined is None and status.startswith("degraded:llm调用失败")
              and "注入错误" in status, f"got={status}")
    finally:
        lr._call_llm = orig_call

    # -----------------------------------------------------------------
    print("T6 memory_bridge 全保护 + 脱敏 + additive (验收⑥)")
    check("T6 钉板主名 bridge_episodes 与别名 bridge 同一函数",
          mb.bridge is mb.bridge_episodes and callable(mb.bridge_episodes))
    d6 = temp_dir()
    products = [
        {"ep_id": "ep_001", "title": "第一章 夜雨",
         "text": "林照进城。", "hooks": {"passed": True}},
        {"ep_id": "ep_002", "title": "王总的电话是13812345678，有事_call。",
         "text": "林照出城。", "hooks": {"passed": False}},
    ]
    s6 = mb.bridge_episodes(d6, "测试项目", products, 3000)
    check("T6 bridge 状态 ok / links=2", s6["status"] == "ok" and s6["links"] == 2,
          f"got={s6}")
    series_file = os.path.join(d6, "dm_memory", "_series",
                               pl.safe_name("测试项目") + ".json")
    check("T6 系列档案落盘 <out>/dm_memory/_series/", os.path.isfile(series_file))
    anchors_file = os.path.join(d6, "dm_memory", pl.safe_name("测试项目"), "anchors.json")
    check("T6 锚点互链落盘 <out>/dm_memory/<project>/anchors.json",
          os.path.isfile(anchors_file))
    with open(anchors_file, "r", encoding="utf-8") as f:
        st = json.load(f)
    check("T6 anchors.json 含两集 ep_id 互链",
          "ep_001" in st.get("links", {}) and "ep_002" in st.get("links", {}),
          f"got={st.get('links')}")
    check("T6 link_card vid = 集产物相对引用",
          st["links"]["ep_001"] == ["episodes/ep_001.json"], f"got={st['links']}")
    with open(series_file, "r", encoding="utf-8") as f:
        sdoc = f.read()
    check("T6 series 自由文本脱敏 (R2 MED-4): 手机号 → [手机号] 占位",
          "13812345678" not in sdoc and "[手机号]" in sdoc)
    check("T6 series 集数结构键不脱敏", '"集数"' in sdoc)
    check("T6 injection_block 接线返回长度字段 (int ≥0)",
          isinstance(s6["injection_chars"], int) and s6["injection_chars"] >= 0)
    # 幂等: 重复 bridge 不炸且状态保持
    s6b = mb.bridge_episodes(d6, "测试项目", products, 3000)
    check("T6 重复 bridge 幂等 (去重互链, 状态 ok)",
          s6b["status"] == "ok" and s6b["links"] == 2, f"got={s6b}")

    # additive: 既有 anchors.json 的无关卡必须原样保留
    d6c = temp_dir()
    proj_dir = os.path.join(d6c, "dm_memory", pl.safe_name("既有项目"))
    os.makedirs(proj_dir, exist_ok=True)
    with open(os.path.join(proj_dir, "anchors.json"), "w", encoding="utf-8") as f:
        json.dump({"links": {"既有卡": ["v_0001"]}, "adaptive": {"last_prompt_at": None,
                   "last_seen_vids": []}, "out_of_window": {}}, f, ensure_ascii=False)
    mb.bridge_episodes(d6c, "既有项目", products, 3000)
    with open(os.path.join(proj_dir, "anchors.json"), "r", encoding="utf-8") as f:
        st2 = json.load(f)
    check("T6 additive: 既有卡保留 + 新增集互链并存",
          st2["links"].get("既有卡") == ["v_0001"] and "ep_001" in st2["links"],
          f"got={st2.get('links')}")

    # 全保护永不致命: out_dir 是一个"文件" / episodes 非法 / out_dir 缺失
    f6 = os.path.join(temp_dir(), "not_a_dir")
    with open(f6, "w", encoding="utf-8") as f:
        f.write("x")
    try:
        s6d = mb.bridge_episodes(f6, "项目", products, 3000)
        ok = isinstance(s6d, dict) and s6d["errors"] and s6d["status"] in ("partial", "unavailable")
    except Exception as exc:
        ok = False
        s6d = {"status": "?", "errors": [str(exc)]}
    check("T6 out_dir 为文件 → 记 errors 不抛错 (永不致命)", ok, f"got={s6d}")
    s6e = mb.bridge_episodes(None, "项目", products, 3000)
    check("T6 out_dir 缺失 → unavailable 零写入",
          s6e["status"] == "unavailable" and s6e["errors"], f"got={s6e}")
    s6f = mb.bridge_episodes(temp_dir(), "项目", [], 3000)
    check("T6 无分集 → skipped 诚实标注",
          s6f["status"] == "skipped" and s6f["errors"], f"got={s6f}")
    s6g = mb.bridge_episodes(temp_dir(), "项目", ["不是dict"], 3000)
    check("T6 非法分集元素 → 不抛错 (无可用 ep_id 则零互链)",
          isinstance(s6g, dict) and s6g["links"] == 0, f"got={s6g}")

    # -----------------------------------------------------------------
    print("T7 pipeline 单元: safe_name/core_pack_seed/pipeline_id/fail loud (⑤⑦)")
    try:
        from aggregator.dm_memory import series_inherit
        samples = ["测试项目", "MyProject", "尾点.", " trailing ", "a" * 50, "CON",
                   "含/斜杠:与*星号"]
        check("T7 safe_name 与 dm_memory._safe_name 同配方逐例对齐",
              all(pl.safe_name(s) == series_inherit._safe_name(s) for s in samples),
              f"got={[pl.safe_name(s) for s in samples]}")
    except Exception as exc:
        check("T7 safe_name 与 dm_memory._safe_name 同配方逐例对齐", False, str(exc))
    # 存储布局断言: safe_name 碰撞用例 (批次4 R2 MED-2) — 三个易碰撞名落盘互不覆盖
    trio = ["Project", "project", "project."]
    trio_dirs = [pl.safe_name(s) for s in trio]
    check("T7 safe_name 碰撞: Project/project/project. 三安全名互异",
          len(set(trio_dirs)) == 3, f"got={trio_dirs}")
    d7c = temp_dir()
    for s, dn in zip(trio, trio_dirs):
        pl._atomic_write_json(os.path.join(d7c, "episodes", dn, "proj.json"),
                              {"owner": s})
    ok_nc = True
    for s, dn in zip(trio, trio_dirs):
        try:
            with open(os.path.join(d7c, "episodes", dn, "proj.json"),
                      encoding="utf-8") as f:
                ok_nc = ok_nc and json.load(f).get("owner") == s
        except Exception:
            ok_nc = False
    check("T7 safe_name 碰撞落盘互不覆盖 (各目录内容原样, UTF-8 JSON 可解析)", ok_nc)
    check("T7 pipeline_id = sha1(text)[:16]",
          pl.pipeline_id_of("abc") == hashlib.sha1(b"abc").hexdigest()[:16])
    seed = pl._core_pack_seed({"text": "正文", "title": "第一章"}, "项目")
    check("T7 core_pack_seed 恰 32 字段", len(seed) == 32, f"got={len(seed)}")
    check("T7 core_pack_seed 无 _ai_api_key (密钥绝不入产物)",
          "_ai_api_key" not in seed and seed.get("_ai_api_url") == "")
    check("T7 core_pack_seed _随机种子 确定性正整数",
          isinstance(seed["_随机种子"], int) and seed["_随机种子"] > 0
          and seed["_随机种子"] == pl._core_pack_seed({"text": "正文", "title": "第一章"}, "项目")["_随机种子"])
    check("T7 core_pack_seed 下游消费键兼容 (parse_core_pack 往返一致)",
          parse_core_pack(json.dumps(seed, ensure_ascii=False)) == seed)
    check("T7 core_pack_seed 叙事编排/线型为下游缺省值 (零漂移)",
          seed["_叙事编排"] == "跟随叙事结构" and seed["_叙事线型"] == "单线")

    d7 = temp_dir()
    r = pl.run_intake(None, d7, "项目", 100)
    check("T7 fail loud: novel_text 非法 → ok=False + errors",
          r["ok"] is False and r["errors"], f"got={r.get('errors')}")
    r = pl.run_intake("正文" * 10, d7, "项目", 0)
    check("T7 fail loud: target_chars 非法 → ok=False + errors",
          r["ok"] is False and r["errors"], f"got={r.get('errors')}")
    r = pl.run_intake("正文" * 10, "", "项目", 100)
    check("T7 fail loud: out_dir 非法 → ok=False + errors",
          r["ok"] is False and r["errors"], f"got={r.get('errors')}")
    r = pl.run_intake("正文" * 10, d7, "", 100)
    check("T7 fail loud: project 非法 → ok=False + errors",
          r["ok"] is False and r["errors"], f"got={r.get('errors')}")
    _sn_bad = "坏\n名\x01项/目"
    _sn = pl.safe_name(_sn_bad)
    check("T7 safe_name 滤控制字符与路径符 (与 _UNSAFE_FILENAME_RE 对齐)",
          not any(c in _sn for c in "\n\x01\x7f/\\:*?\"<>|"))

    # -----------------------------------------------------------------
    print("T8 pipeline 端到端 (依赖 e1: splitter/ledger/anchors)")
    if not E1:
        for lb in ("T8.1 端到端小样本产物 9 键+锚点回溯",
                   "T8.2 无凭据→unavailable / 不可达→degraded + 产物不变 (⑤)",
                   "T8.3 additive 零漂移: 缺/有 dm_memory 产物逐字节不变 (⑥)",
                   "T8.4 断点续跑: 全量跳过/单集重算/损坏自愈 (⑦)",
                   "T8.5 fail loud 注入: 锚点回溯失败/账本残余/切分异常 (不静默)",
                   "T8.6 manifest 确定性 (无时间戳/绝对路径/记忆段)"):
            blocked(lb)
    else:
        from aggregator.episode_pipeline import anchors as anchors_mod
        from aggregator.episode_pipeline import splitter as splitter_mod
        from aggregator.episode_pipeline import ledger as ledger_mod

        def make_novel():
            parts = []
            for ci in (1, 2, 3):
                body = (
                    f"第{ci}章 夜行{ci}\n"
                    f"林照在第{ci}段山路上遇见了商队。林照数了数人数，一共十三人，为首的"
                    f"是个独眼汉子。林照低下头，装作检查马蹄铁，把匕首悄悄挪到了袖口。"
                    f"商队里有人认出了他，却在人群里一声不吭。林照抬头看天，云层压得很低。"
                    f"前方的哨卡灯火通明，盘查比往日严了三倍。林照把路引递过去，守卒来回"
                    f"打量了他两遍，忽然问他从哪条道上山。林照报了个假地名，守卒盯着他，"
                    f"手指在刀柄上敲了两下，最终还是挥手放行。林照牵马进哨卡时，听见身后"
                    f"有人低声说了句：就是他。林照没有回头。"
                )
                parts.append(body * 2)
            return "".join(parts)

        novel = make_novel()
        d8 = temp_dir()

        # --- T8.1 端到端小样本 ---
        r1 = pl.run_intake(novel, d8, "夜行项目", 800)
        check("T8.1 ok=True 无 errors", r1["ok"] is True and r1["errors"] == [],
              f"errs={r1['errors'][:3]}")
        check("T8.1 账本全量重算 ok", r1["ledger_summary"]["ok"] is True)
        n = len(r1["episodes"])
        check("T8.1 产出 ≥2 集", n >= 2, f"got={n}")
        ok_keys = all({"ep_id", "title", "span", "text", "anchors", "hooks",
                       "logline", "checkpoint_ref", "core_pack_seed"} == set(e)
                      for e in r1["episodes"])
        check("T8.1 每集产物恰 9 键", ok_keys)
        ok_span = all(e["text"] == novel[e["span"]["start"]:e["span"]["end"]]
                      for e in r1["episodes"])
        check("T8.1 span 切片与集文本逐字节一致", ok_span)
        tb_ok_all = all(anchors_mod.traceback(novel, e["anchors"])[0]
                        for e in r1["episodes"] if e["anchors"])
        check("T8.1 全部锚点回溯命中原文本", tb_ok_all)
        ok_hooks = all({"m1", "m2", "m3", "passed", "flags"} <= set(e["hooks"])
                       for e in r1["episodes"])
        check("T8.1 hooks 三指标形状齐备", ok_hooks)
        check("T8.1 无 LLM → logline 诚实留空",
              all(e["logline"] == "" for e in r1["episodes"]))
        check("T8.1 llm_track 无凭据 → unavailable",
              r1["llm_track"]["status"] == "unavailable"
              and r1["llm_track"]["enabled"] is False)
        check("T8.1 checkpoints pipeline_id = sha1(text)[:16]",
              r1["checkpoints"]["pipeline_id"] == hashlib.sha1(
                  novel.encode("utf-8")).hexdigest()[:16])
        manifest_path = os.path.join(d8, "episodes", pl.safe_name("夜行项目"),
                                     "manifest.json")
        check("T8.1 manifest.json 落盘", os.path.isfile(manifest_path))
        ck_manifest = os.path.join(d8, "dm_checkpoints")
        check("T8.1 dm_checkpoints/ 落盘", os.path.isdir(ck_manifest))

        # --- T8.2 LLM 轨诚实降级 (不可达端点) ---
        d8b = temp_dir()
        r2 = pl.run_intake(novel, d8b, "夜行项目", 800,
                           api_url="http://127.0.0.1:1", api_key="k")
        check("T8.2 不可达 api_url → llm_track 标 degraded (逐集 degraded 原因保留)",
              r2["llm_track"]["status"] == "degraded"
              and r2["llm_track"]["enabled"] is True
              and all(str(v).startswith("degraded")
                      for v in r2["llm_track"]["episodes"].values()),
              f"got={r2['llm_track']}")
        check("T8.2 整体 ok 不受 LLM 轨失败影响 (确定性轨完整)",
              r2["ok"] is True and len(r2["episodes"]) == n)
        same_products = all(
            json.dumps(a, ensure_ascii=False, sort_keys=True)
            == json.dumps(b, ensure_ascii=False, sort_keys=True)
            for a, b in zip(r1["episodes"], r2["episodes"]))
        check("T8.2 LLM 失败不改任何产物字段 (与无凭据跑逐字节一致)", same_products)

        # --- T8.2b 管线级 mock 正常回放 → refined (验收⑤(c), 零真连) ---
        d8h = temp_dir()
        good_pack = json.dumps({"logline": "少年夜行出关, 身份将暴露。",
                                "scenes": [{"标题": "哨卡盘查", "摘要": "守卒反复打量"}]},
                               ensure_ascii=False)
        orig_call2 = lr._call_llm
        try:
            lr._call_llm = lambda a, k, m, s, u: (good_pack, "")
            r2b = pl.run_intake(novel, d8h, "夜行项目", 800,
                                api_url="http://mock.local/replay", api_key="k")
        finally:
            lr._call_llm = orig_call2
        check("T8.2b mock 回放 → llm_track.status='refined'",
              r2b["llm_track"]["status"] == "refined"
              and all(v == "refined" for v in r2b["llm_track"]["episodes"].values()),
              f"got={r2b['llm_track']}")
        check("T8.2b 每集 logline 注释字段落产物 (来自 mock 响应)",
              all(e["logline"] == "少年夜行出关, 身份将暴露。" for e in r2b["episodes"]),
              f"got={[e['logline'] for e in r2b['episodes']][:2]}")
        check("T8.2b refine 前后每集 span/text 逐字节不变 (原文不可变铁律⑤)",
              all(a["span"] == b["span"] and a["text"] == b["text"]
                  for a, b in zip(r1["episodes"], r2b["episodes"])))
        check("T8.2b 产物仍恰 9 键 (LLM 只填注释字段值, 不增删键)",
              all(set(e) == {"ep_id", "title", "span", "text", "anchors", "hooks",
                             "logline", "checkpoint_ref", "core_pack_seed"}
                  for e in r2b["episodes"]))

        # --- T8.3 additive 零漂移 (⑥) ---
        d8a2 = temp_dir()   # 无 dm_memory 目录
        rA = pl.run_intake(novel, d8a2, "夜行项目", 800)
        d8b2 = temp_dir()   # 预置 dm_memory (既有 anchors.json + 他项目系列档案)
        proj_dir = os.path.join(d8b2, "dm_memory", pl.safe_name("夜行项目"))
        os.makedirs(proj_dir, exist_ok=True)
        with open(os.path.join(proj_dir, "anchors.json"), "w", encoding="utf-8") as f:
            json.dump({"links": {"既有卡": ["v_0001"]}, "adaptive": {"last_prompt_at": None,
                       "last_seen_vids": []}, "out_of_window": {}}, f, ensure_ascii=False)
        other_series = os.path.join(d8b2, "dm_memory", "_series",
                                    pl.safe_name("别的系列") + ".json")
        os.makedirs(os.path.dirname(other_series), exist_ok=True)
        with open(other_series, "w", encoding="utf-8") as f:
            json.dump({"worldview": "既有系列", "series_id": "别的系列"}, f, ensure_ascii=False)
        rB = pl.run_intake(novel, d8b2, "夜行项目", 800)
        snapA = walk_bytes(os.path.join(d8a2, "episodes"))
        snapB = walk_bytes(os.path.join(d8b2, "episodes"))
        check("T8.3 episodes/ 文件集合一致 (缺/有 dm_memory 两种前置)",
              sorted(snapA) == sorted(snapB),
              f"A={sorted(snapA)[:4]}... B={sorted(snapB)[:4]}...")
        diff = [k for k in snapA if snapA.get(k) != snapB.get(k)]
        check("T8.3 episodes/ 全部文件逐字节相同 (additive 零漂移硬断言)",
              not diff, f"diff={diff[:3]}")
        check("T8.3 dm_memory 缺席时桥照常执行 (A 跑后目录被建立, 产物零漂移)",
              os.path.isdir(os.path.join(d8a2, "dm_memory")))
        with open(os.path.join(proj_dir, "anchors.json"), "r", encoding="utf-8") as f:
            stB = json.load(f)
        check("T8.3 预置 anchors.json 既有卡保留 + 集互链新增",
              stB["links"].get("既有卡") == ["v_0001"] and len(stB["links"]) > 1)
        check("T8.3 memory 摘要两跑均 ok (诚实落记忆)",
              rA["memory"]["status"] == "ok" and rB["memory"]["status"] == "ok",
              f"A={rA['memory']['status']} B={rB['memory']['status']}")

        # --- T8.3b memory_bridge 内部故障注入 → 产物零漂移 (⑥, 记忆段永不致命) ---
        d8i = temp_dir()
        orig_bridge = mb.bridge_episodes
        try:
            def _boom_bridge(*a, **kw):
                raise RuntimeError("注入: memory_bridge 崩溃")
            mb.bridge_episodes = _boom_bridge
            rC = pl.run_intake(novel, d8i, "夜行项目", 800)
        finally:
            mb.bridge_episodes = orig_bridge
        snapC = walk_bytes(os.path.join(d8i, "episodes"))
        check("T8.3b bridge 崩溃注入 → run_intake 不炸, episodes/ 与正常跑逐字节一致",
              snapC == snapA,
              f"diff={[k for k in snapC if snapC.get(k) != snapA.get(k)][:3]}")
        check("T8.3b bridge 崩溃 → memory 摘要诚实记错误 (ok 不受记忆段影响)",
              bool(rC["memory"].get("errors")) and "memory_bridge" in str(rC["memory"]["errors"]),
              f"got={rC['memory']}")

        # --- T8.4 断点续跑 (⑦) ---
        d8c = temp_dir()
        rc1 = pl.run_intake(novel, d8c, "夜行项目", 800)
        ep_dir = os.path.join(d8c, "episodes", pl.safe_name("夜行项目"))
        ep_files = {e["ep_id"]: os.path.join(ep_dir, e["ep_id"] + ".json")
                    for e in rc1["episodes"]}
        mt1 = {k: mtime_ns(p) for k, p in ep_files.items()}
        body1 = {k: open(p, "rb").read() for k, p in ep_files.items()}
        rc2 = pl.run_intake(novel, d8c, "夜行项目", 800)
        check("T8.4 重跑全量命中: skipped=集数, regenerated=0",
              rc2["checkpoints"]["skipped"] == n and rc2["checkpoints"]["regenerated"] == 0,
              f"got={rc2['checkpoints']}")
        mt2 = {k: mtime_ns(p) for k, p in ep_files.items()}
        check("T8.4 跳过集产物 mtime 不变 (未重写)", mt1 == mt2)
        # 中断模拟: 删除单集产物 → 该集重算, 其余跳过
        victim = sorted(ep_files)[1] if n >= 2 else sorted(ep_files)[0]
        os.remove(ep_files[victim])
        rc3 = pl.run_intake(novel, d8c, "夜行项目", 800)
        check("T8.4 删除单集后重跑: 该集重算, 其余跳过",
              rc3["checkpoints"]["regenerated"] == 1
              and rc3["checkpoints"]["skipped"] == n - 1,
              f"got={rc3['checkpoints']}")
        check("T8.4 重算集产物字节与首跑一致 (确定性)",
              open(ep_files[victim], "rb").read() == body1[victim])
        check("T8.4 未删集 mtime 仍不变",
              all(mtime_ns(ep_files[k]) == mt1[k] for k in ep_files if k != victim))
        # 损坏自愈: 产物写坏 → 检查点命中但校验不过 → 重算
        victim2 = sorted(ep_files)[0]
        with open(ep_files[victim2], "w", encoding="utf-8") as f:
            f.write("{corrupted")
        rc4 = pl.run_intake(novel, d8c, "夜行项目", 800)
        check("T8.4 损坏产物诚实自愈重算 (检查点命中但校验不过)",
              rc4["checkpoints"]["regenerated"] >= 1
              and open(ep_files[victim2], "rb").read() == body1[victim2],
              f"got={rc4['checkpoints']}")
        # --- T8.4b 钉板口径直证 (⑦): steps 记 ep_000.. / done(pid,"ep_000") 为真 ---
        from aggregator.pipeline_checkpoint import CheckpointStore
        pid0 = rc1["checkpoints"]["pipeline_id"]
        store_b = CheckpointStore(os.path.join(d8c, "dm_checkpoints"))
        steps_snap = store_b.steps(pid0)
        check("T8.4b CheckpointStore.steps 记录 ep_000..ep_%03d (钉板口径)"
              % (n - 1),
              sorted(steps_snap) == ["ep_%03d" % i for i in range(n)],
              f"got={sorted(steps_snap)}")
        ih0 = pl._episode_input_hash(rc1["episodes"][0], "夜行项目", 800)
        check("T8.4b done(pipeline_id, 'ep_000', 同款输入指纹) 为真",
              store_b.done(pid0, "ep_000", ih0) is True)

        # --- T8.4c 中断模拟 (钉板口径): 清空清单后先 mark_done 前两集再重跑 ---
        store_c = CheckpointStore(os.path.join(d8c, "dm_checkpoints"))
        store_c.clear(pid0)
        for i in range(min(2, n)):
            ih_i = pl._episode_input_hash(rc1["episodes"][i], "夜行项目", 800)
            store_c.mark_done(pid0, "ep_%03d" % i, ih_i,
                              artifact_ref="%s.json" % rc1["episodes"][i]["ep_id"])
        rc6 = pl.run_intake(novel, d8c, "夜行项目", 800)
        check("T8.4c 先 mark_done 前两集再重跑: 恰跳过 2 集, 其余重算",
              rc6["checkpoints"]["skipped"] == min(2, n)
              and rc6["checkpoints"]["regenerated"] == n - min(2, n),
              f"got={rc6['checkpoints']}")
        check("T8.4c 重跑后全部集产物字节与一次跑完逐字节等价 (最终产物不劣化)",
              all(open(p, "rb").read() == body1[k] for k, p in ep_files.items()))

        # 输入变化 → 该集失效重算 (置尾: 不干扰上述字节等价断言)
        rc5 = pl.run_intake(novel + "新尾声。", d8c, "夜行项目", 800)
        check("T8.4 输入变化 → pipeline_id 变化 (检查点自然失效)",
              rc5["checkpoints"]["pipeline_id"] != rc1["checkpoints"]["pipeline_id"])

        # --- T8.5 fail loud 注入 (不静默丢) ---
        d8d = temp_dir()
        orig_tb = anchors_mod.traceback
        try:
            anchors_mod.traceback = lambda text, anchors: (False, [{"error": "注入失败"}])
            rf = pl.run_intake(novel, d8d, "夜行项目", 800)
        finally:
            anchors_mod.traceback = orig_tb
        check("T8.5 锚点回溯注入失败 → 整体 ok=False + errors 点名锚点段",
              rf["ok"] is False and any("锚点段失败" in e for e in rf["errors"]),
              f"errs={rf['errors'][:2]}")
        check("T8.5 失败集不写产物、不静默丢 (errors 显式列出)",
              len(rf["episodes"]) < n and len(rf["errors"]) >= 1)
        d8e = temp_dir()
        orig_cov = ledger_mod.verify_coverage
        try:
            ledger_mod.verify_coverage = lambda text, ledger: (False, ["注入: 未归类残余 7 字"])
            rg = pl.run_intake(novel, d8e, "夜行项目", 800)
        finally:
            ledger_mod.verify_coverage = orig_cov
        check("T8.5 账本残余注入 → ok=False + errors 含 覆盖账本",
              rg["ok"] is False and any("覆盖账本" in e for e in rg["errors"]),
              f"errs={rg['errors'][:2]}")
        check("T8.5 账本失败 → 零产物落盘 (fail loud 中止)",
              not os.path.isdir(os.path.join(d8e, "episodes")))
        d8f = temp_dir()
        orig_dc = splitter_mod.detect_chapters
        try:
            def _boom(text):
                raise RuntimeError("注入: 章节检测崩溃")
            splitter_mod.detect_chapters = _boom
            rh = pl.run_intake(novel, d8f, "夜行项目", 800)
        finally:
            splitter_mod.detect_chapters = orig_dc
        check("T8.5 切分异常注入 → ok=False + errors 含 章节检测失败",
              rh["ok"] is False and any("章节检测失败" in e for e in rh["errors"]),
              f"errs={rh['errors'][:2]}")

        # --- T8.6 manifest 确定性 ---
        m1_bytes = open(manifest_path, "rb").read()
        d8g = temp_dir()
        pl.run_intake(novel, d8g, "夜行项目", 800)
        mg_bytes = open(os.path.join(d8g, "episodes", pl.safe_name("夜行项目"),
                                     "manifest.json"), "rb").read()
        check("T8.6 两次全新跑 manifest 逐字节一致 (确定性/A-B 零漂移根基)",
              m1_bytes == mg_bytes)
        check("T8.6 manifest 不含时间戳/绝对路径字样",
              b"updated_at" not in mg_bytes and d8.encode("utf-8") not in mg_bytes)

    # -----------------------------------------------------------------
    print("")
    print(f"PASS={PASS} FAIL={FAIL} BLOCKED_BY_E1={len(_BLOCKED)}")
    if _BLOCKED:
        print("被 e1 缺席阻塞的用例:")
        for lb in _BLOCKED:
            print(f"  - {lb}")
    return 0 if FAIL == 0 else 1


def main():
    try:
        code = run_suite()
    finally:
        for d in TEMP_DIRS:
            shutil.rmtree(d, ignore_errors=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
