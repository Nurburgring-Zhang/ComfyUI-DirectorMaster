# -*- coding: utf-8 -*-
"""
批次4 WaveB builder-m3 — 风格圣经+进化钩子+信任注入 测试 (tests/test_dm_memory_bible.py)
==========================================================================================
覆盖矩阵 (冻结设计 .acs/design_batch4.md 验收口径):
  T0 常量: 信任序 TRUST_ORDER 钉死 / 门面 trust_order 同源 / 进化白名单 4 信号 / 阈值 3
  T1 验收① 风格圣经+系列 schema 正负样本 (m1 validate_bible/validate_series)
  T2 build_bible_skeleton 采证确定性: 版本数/最优版本/时长分布/景别频次 + LLM_DISTILL_PENDING
     诚实占位 + 落盘布局 <out>/dm_memory/<safe>/bible.md + 重跑逐字节稳定 + 空库/缺档诚实未采证
     + render_bible_prompt (pending 不猜测 / done 回填)
  T3 验收⑤ should_store 4 信号白名单 (进度/临时状态不存不记, 口径统一 failure_memory)
  T4 验收⑤ maybe_reflect: 阈值 3 提议 / 提议后计数窗口重置 (reflect 与 auto-create 互斥) /
     同输入同输出确定性 / evolution.jsonl 落盘布局与事件流 / 非白名单零落盘
  T5 验收⑤ 异常注入永不致命: 坏句柄/None/非句柄/缺 out_dir → None; 主流程返回值不受影响;
     损坏 jsonl 自愈
  T6 注入: 重申节奏 round_no=1..6 (remind_every=5) 注入/空段行为 / 信任序头 /
     只注入正面教训卡 (未验证+rejected 零出现) / pending 圣经不产风格约束 / 卡上限 /
     只读纪律 (缺目录零创建零写盘) / 确定性
  T7 additive 零漂移硬断言: cinematic_studio 分镜输出 — 缺 dm_memory 目录逐字节不变
     (含到节奏但缺目录变体); 记忆在场且到节奏 → main 恰好追加 "\n\n"+注入段, JSON 恒零漂移
  T8 接线配套: resolve_out_dir 环境变量优先+降级 / project_rounds 版本轮次口径
  T9 R1 修复回归: 注入消费端对损坏存储容错 (M2 读侧口径的下游)
  T10 R2 修复回归: MED-3 evolution.jsonl 二进制容错 (损坏行跳过告警/阈值记账可达/
     写路径自愈重写全合法)
纪律: 记忆/版本库一律 tempfile 目录, 测试全程零仓库内写入。
退出码: 0 = 全部通过, 1 = 有失败。运行: python -X utf8 tests/test_dm_memory_bible.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator.dm_memory import (
    open_memory, schema, shot_cards, style_bible, evolution, injection,
)
from aggregator.version_store import open_store
from aggregator.pro_format import format_shot_table
from aggregator.cinematic_studio import DirectorMasterCinematic

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


def make_out(prefix="dm_b3_"):
    d = tempfile.mkdtemp(prefix=prefix)
    TEMP_DIRS.append(d)
    return d


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


def _shot(n, size, dur, move="固定"):
    return {"n": n, "stage": "建立", "stage_name": "开场", "size": size, "angle": "平拍",
            "move": move, "focal": "50mm", "dur": dur, "focus": "父亲切菜的手部特写",
            "sound": "切菜声", "cut": "硬切", "purpose": "交代动作"}


def _commit_version(out_dir, store, name, shots=None, score=None):
    files = {}
    if shots is not None:
        text = format_shot_table("王家卫", "孤独", shots)
        fname = f"{name}_分镜.txt"
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(text)
        files["分镜"] = (fname, text)
    files["剧本"] = ("剧本.txt", f"{name} 剧本内容")
    return store.commit(name=name, files=files,
                        scores={"total": score} if score is not None else {})


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =====================================================================
def run_suite():
    # -----------------------------------------------------------------
    print("T0 常量与信任序")
    check("T0 TRUST_ORDER 精确钉死 (列表 + 顺序)",
          injection.TRUST_ORDER == ["当前工作流参数", "用户当前指令", "记忆卡", "历史版本"],
          f"got={injection.TRUST_ORDER}")
    import aggregator.dm_memory as dm_pkg
    check("T0 门面 trust_order 与 injection.TRUST_ORDER 同源",
          tuple(injection.TRUST_ORDER) == dm_pkg.trust_order, f"facade={dm_pkg.trust_order}")
    check("T0 进化白名单 4 信号钉死 + 阈值 3",
          evolution.STORE_SIGNALS == ("明确决策", "新持久上下文", "用户纠正", "用户偏好")
          and evolution.REFLECT_THRESHOLD == 3, f"got={evolution.STORE_SIGNALS}")
    check("T0 圣经占位标记与 m1 schema 同源",
          style_bible.BIBLE_DISTILL_PENDING == schema.BIBLE_DISTILL_PENDING == "LLM_DISTILL_PENDING"
          and style_bible.BIBLE_FILENAME == "bible.md")

    # -----------------------------------------------------------------
    print("T1 风格圣经+系列 schema 正负样本 (验收①)")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {"版本数": 3},
                                      "蒸馏段": "<!-- LLM_DISTILL_PENDING -->",
                                      "蒸馏状态": "pending"})
    check("T1 正样本: pending 圣经带诚实占位通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {},
                                      "蒸馏段": "冷色调, 手持", "蒸馏状态": "pending"})
    check("T1 负样本: pending 无占位 = 猜测 → 拒绝且点名 LLM_DISTILL_PENDING",
          not ok and any("LLM_DISTILL_PENDING" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "蒸馏段": "", "蒸馏状态": "pending"})
    check("T1 负样本: 缺脚本统计拒绝且点名", not ok and any("脚本统计" in e for e in errs),
          f"errs={errs}")
    ok, errs = schema.validate_bible({"项目": "测试片", "脚本统计": {},
                                      "蒸馏段": "冷色调, 手持", "蒸馏状态": "done"})
    check("T1 正样本: done 状态无需占位通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_bible("字符串")
    check("T1 负样本: 非 dict 拒绝", not ok and errs, f"errs={errs}")
    ok, errs = schema.validate_series({"worldview": "末世废土", "风格锚": "王家卫·冷色",
                                       "dna": ["{...}", {"维度": {}}]})
    check("T1 正样本: 系列档案 (worldview/风格锚/dna 列表) 通过", ok and errs == [], f"errs={errs}")
    ok, errs = schema.validate_series({"worldview": "末世废土", "风格锚": "x", "dna": "不是列表"})
    check("T1 负样本: 系列 dna 非列表拒绝", not ok and any("dna" in e for e in errs), f"errs={errs}")
    ok, errs = schema.validate_series({"风格锚": "x", "dna": []})
    check("T1 负样本: 缺 worldview 拒绝且点名", not ok and any("worldview" in e for e in errs),
          f"errs={errs}")

    # -----------------------------------------------------------------
    print("T2 build_bible_skeleton 采证确定性")
    out = make_out()
    store = open_store(out, "圣经项目")
    _commit_version(out, store, "v1", shots=[_shot(1, "全景", "0.8s"), _shot(2, "特写", "2.5s")],
                    score=0.5)
    _commit_version(out, store, "v2", shots=[_shot(1, "全景", "4.0s"), _shot(2, "中景", "7s")],
                    score=0.9)
    _commit_version(out, store, "v3", shots=None, score=0.7)
    bible = style_bible.build_bible_skeleton(out, "圣经项目", store)
    check("T2 返回 dict 且过 m1 validate_bible (蒸馏 pending)",
          isinstance(bible, dict) and schema.validate_bible(bible)[0]
          and bible["蒸馏状态"] == "pending", f"b={str(bible)[:120]}")
    check("T2 蒸馏段诚实占位 LLM_DISTILL_PENDING (不猜测)",
          "LLM_DISTILL_PENDING" in bible["蒸馏段"], f"dist={bible['蒸馏段']}")
    md_path = style_bible.bible_path(out, "圣经项目")
    check("T2 落盘布局钉死 <out>/dm_memory/<safe_project>/bible.md", os.path.isfile(md_path),
          f"path={md_path}")
    st = bible["脚本统计"]
    check("T2 采证: 版本数=3 / 分镜存档镜数=4 / 最优版本=v2(total=0.9)",
          st["版本数"] == 3 and st["分镜存档镜数"] == 4
          and st["最优版本"] == {"名称": "v2", "总分": 0.9}, f"stats={st}")
    check("T2 采证: 时长分布四桶精确 (≤1s×1, 1-3s×1, 3-5s×1, >5s×1)",
          st["时长分布"] == {"≤1s": 1, "1-3s": 1, "3-5s": 1, ">5s": 1}, f"dist={st['时长分布']}")
    check("T2 采证: 景别频次精确 (全景×2, 中景×1, 特写×1)",
          st["景别频次"] == {"全景": 2, "中景": 1, "特写": 1}, f"sizes={st['景别频次']}")
    md1 = _read(md_path)
    style_bible.build_bible_skeleton(out, "圣经项目", store)
    check("T2 重跑逐字节稳定 (确定性骨架, 无时间戳)", _read(md_path) == md1)
    check("T2 md 含统计与占位且无 .tmp 残留",
          "版本数: 3" in md1 and "LLM_DISTILL_PENDING" in md1
          and not os.path.exists(md_path + ".tmp"))
    p = style_bible.render_bible_prompt(bible)
    check("T2 render_bible_prompt: pending 状态只报采证事实+待蒸馏标注 (零编造风格结论)",
          p.startswith("【项目风格圣经 · 圣经项目】") and "版本数=3" in p and "景别频次" in p
          and "待蒸馏回填" in p and "不猜测" in p, f"p={p[:120]}")
    done_bible = dict(bible, 蒸馏状态="done", 蒸馏段="- 冷色调低饱和\n- 手持跟拍为主")
    pd = style_bible.render_bible_prompt(done_bible)
    check("T2 render_bible_prompt: done 回填 → 风格约束逐行呈现",
          "风格约束 (蒸馏回填)" in pd and "- 冷色调低饱和" in pd and "- 手持跟拍为主" in pd,
          f"p={pd[:120]}")
    check("T2 render_bible_prompt: 校验不过 → \"\" (诚实降级)",
          style_bible.render_bible_prompt({"项目": "x", "蒸馏段": "猜的", "蒸馏状态": "pending"}) == ""
          and style_bible.render_bible_prompt(None) == "")
    out_empty = make_out()
    bible_e = style_bible.build_bible_skeleton(out_empty, "空项目", open_store(out_empty, "空项目"))
    check("T2 空版本库: 诚实 未采证 说明 + 仍过校验 (零编造)",
          bible_e["脚本统计"]["版本数"] == 0
          and "未采证" in bible_e["脚本统计"].get("采证说明", "")
          and schema.validate_bible(bible_e)[0], f"stats={bible_e['脚本统计']}")
    out_lost = make_out()
    store_lost = open_store(out_lost, "丢档项目")
    store_lost.commit(name="v1", files={"分镜": ("丢失_分镜.txt", "内容未落盘"),
                                        "剧本": ("a.txt", "x")})
    bible_l = style_bible.build_bible_skeleton(out_lost, "丢档项目", store_lost)
    check("T2 分镜存档文件缺失 → 该版本诚实跳过不炸 (镜数 0 + 未采证说明)",
          bible_l["脚本统计"]["版本数"] == 1 and bible_l["脚本统计"]["分镜存档镜数"] == 0
          and "未采证" in bible_l["脚本统计"].get("采证说明", ""),
          f"stats={bible_l['脚本统计']}")

    # -----------------------------------------------------------------
    print("T3 should_store 4 信号白名单 (验收⑤, 口径统一 failure_memory)")
    check("T3 白名单 4 信号全 True",
          all(evolution.should_store(s) for s in
              ("明确决策", "新持久上下文", "用户纠正", "用户偏好")))
    check("T3 进度/临时状态/一次性/本轮 一律 False (不存不记)",
          not any(evolution.should_store(s) for s in
                  ("进度", "临时状态", "一次性", "本轮", "临时", "完成 3 镜")))
    check("T3 未知信号/空串/非字符串 一律 False",
          not evolution.should_store("随便什么") and not evolution.should_store("")
          and not evolution.should_store(None) and not evolution.should_store(42)
          and not evolution.should_store(["用户纠正"]))

    # -----------------------------------------------------------------
    print("T4 maybe_reflect 阈值/互斥/确定性/落盘 (验收⑤)")
    mem = open_memory(make_out(), "进化项目")
    plans = [evolution.maybe_reflect(mem, "用户纠正") for _ in range(6)]
    check("T4 第 1/2 次 → None (未达阈值 3)", plans[0] is None and plans[1] is None,
          f"p={plans[:2]}")
    check("T4 第 3 次 → reflect plan (action/signal/同类计数/阈值)",
          plans[2] == {"action": "reflect", "signal": "用户纠正", "同类计数": 3, "阈值": 3},
          f"p={plans[2]}")
    check("T4 第 4/5 次 → None (提议后计数窗口重置 — reflect 与 auto-create 互斥窗口)",
          plans[3] is None and plans[4] is None, f"p={plans[3:5]}")
    check("T4 第 6 次 → 再提议 (新窗口满 3)", plans[5] == plans[2], f"p={plans[5]}")
    check("T4 异类信号独立计数 (用户偏好 ×2 不提议)",
          evolution.maybe_reflect(mem, "用户偏好") is None
          and evolution.maybe_reflect(mem, "用户偏好") is None)
    evo_path = evolution.evolution_path(mem.out_dir, "进化项目")
    check("T4 落盘布局钉死 <out>/dm_memory/<safe_project>/evolution.jsonl",
          os.path.isfile(evo_path), f"path={evo_path}")
    events = [json.loads(ln) for ln in _read(evo_path).splitlines() if ln.strip()]
    check("T4 事件流: 6×signal(用户纠正) + 2×reflect + 2×signal(用户偏好), 全部合法 JSON",
          [e["event"] for e in events] == ["signal"] * 3 + ["reflect"] + ["signal"] * 3
          + ["reflect"] + ["signal"] * 2, f"events={[e['event'] for e in events]}")
    check("T4 reflect 事件与 plan 同计数 (同类计数=3) 且 ts 在场 (日志口径同 failure_memory)",
          all(e.get("同类计数") == 3 for e in events if e["event"] == "reflect")
          and all(e.get("ts") for e in events), f"events={events[:2]}")

    mem_b = open_memory(make_out(), "进化项目")
    plans_b = [evolution.maybe_reflect(mem_b, "用户纠正") for _ in range(3)]
    events_b = [json.loads(ln) for ln in _read(evolution.evolution_path(mem_b.out_dir, "进化项目"))
                .splitlines() if ln.strip()]
    strip_ts = lambda es: [{k: v for k, v in e.items() if k != "ts"} for e in es]
    check("T4 确定性: 同输入同输出 — 两套独立环境 plan 序列逐项相等",
          plans_b == plans[:3], f"b={plans_b} a={plans[:3]}")
    check("T4 确定性: 事件流 (去 ts) 逐条相等",
          strip_ts(events_b) == strip_ts(events[:4]), f"b={strip_ts(events_b)}")

    mem_c = open_memory(make_out(), "非白名单项目")
    path_c = evolution.evolution_path(mem_c.out_dir, "非白名单项目")
    r = [evolution.maybe_reflect(mem_c, s) for s in ("进度", "临时状态", "一次性", "进度")]
    check("T4 非白名单信号 → 全 None 且零落盘 (进度/临时状态不存不记)",
          all(x is None for x in r) and not os.path.exists(path_c), f"r={r}")

    # -----------------------------------------------------------------
    print("T5 异常注入永不致命 (验收⑤)")
    class BadHandle:
        project = "x"

        @property
        def out_dir(self):
            raise RuntimeError("boom")

    check("T5 out_dir 抛异常句柄 → None (异常吞掉)",
          evolution.maybe_reflect(BadHandle(), "用户纠正") is None)
    check("T5 None/42/{}/缺 out_dir dict → 全 None",
          all(evolution.maybe_reflect(m, "用户纠正") is None
              for m in (None, 42, {}, {"project": "无目录"})))
    mem_d = open_memory(make_out(), "字典项目")
    d3 = [evolution.maybe_reflect({"out_dir": mem_d.out_dir, "project": "字典项目"}, "用户纠正")
          for _ in range(3)]
    check("T5 dict 形态 memory 句柄等价可用 (第 3 次提议)",
          d3[0] is None and d3[2] == {"action": "reflect", "signal": "用户纠正",
                                      "同类计数": 3, "阈值": 3}, f"d3={d3}")

    def main_flow(m):
        evolution.maybe_reflect(m, "用户纠正")   # 钩子
        evolution.maybe_reflect(m, "进度")       # 钩子
        return "OK"

    check("T5 主流程返回值不受钩子异常影响 (验收⑤异常注入口径)",
          main_flow(BadHandle()) == "OK" and main_flow(None) == "OK")
    mem_e = open_memory(make_out(), "损坏项目")
    path_e = evolution.evolution_path(mem_e.out_dir, "损坏项目")
    os.makedirs(os.path.dirname(path_e), exist_ok=True)
    with open(path_e, "w", encoding="utf-8") as f:
        f.write("不是JSON{{{\n[1, 2]\n{\"event\": \"signal\", \"signal\": \"用户纠正\"}\n\n")
    rc = [evolution.maybe_reflect(mem_e, "用户纠正") for _ in range(2)]
    lines_e = [ln for ln in _read(path_e).splitlines() if ln.strip()]
    check("T5 损坏 jsonl 自愈: 坏行跳过计数正确 (存量 1 + 新 2 = 第 3 次提议) 且重写后全为合法 JSON",
          rc[0] is None and rc[1] is not None
          and all(isinstance(json.loads(ln), dict) for ln in lines_e), f"rc={rc}")
    check("T5 injection_block 坏输入 → \"\" (None/非句柄/坏轮次)",
          injection.injection_block(None, 5) == "" and injection.injection_block(42, 5) == ""
          and injection.injection_block(mem_e, "abc") == "")

    # -----------------------------------------------------------------
    print("T6 injection_block 重申节奏 + 正面教训过滤")
    mem_f = open_memory(make_out(), "节奏项目")
    proj_dir = os.path.join(mem_f.out_dir, "dm_memory", "节奏项目")
    os.makedirs(proj_dir)
    with open(os.path.join(proj_dir, "bible.md"), "w", encoding="utf-8") as f:
        f.write("# 项目风格圣经 — 节奏项目\n\n## 脚本统计 (确定性采证)\n- 版本数: 5\n\n"
                "## 蒸馏段 (LLM 蒸馏回填区)\n- 冷色调低饱和青蓝夜景约束\n- 手持跟拍优先约束\n\n"
                "## 采证口径\n- 数据来源: 测试夹具\n")
    _, _ = shot_cards.add_card(mem_f, {"标题": "确认卡·夜景低照度记忆方案", "signal": "用户确认",
                                       "status": "confirmed", "方案": "低照度+烟雾机",
                                       "教训": "夜景优先低照度"})
    _, _ = shot_cards.add_card(mem_f, {"标题": "候选卡·手持长镜头记忆", "signal": "生成",
                                       "status": "candidate", "方案": "手持长镜头"})
    _, _ = shot_cards.add_card(mem_f, {"标题": "否决卡·广角怼脸记忆", "signal": "用户纠正",
                                       "status": "rejected", "被否方案": "广角怼脸致不适"})
    blocks = {r: injection.injection_block(mem_f, r, 5) for r in range(1, 7)}
    check("T6 round_no=1..4,6 (remind_every=5) → \"\" (未到节奏)",
          all(blocks[r] == "" for r in (1, 2, 3, 4, 6)), f"lens={ {r: len(b) for r, b in blocks.items()} }")
    b5 = blocks[5]
    check("T6 round_no=5 → 注入段出现且含信任序头 (顺序钉死)",
          b5 and "【记忆注入 · 第 5 轮 (每 5 轮重申)】" in b5
          and "信任序: 当前工作流参数 > 用户当前指令 > 记忆卡 > 历史版本" in b5, f"b5={b5[:120]}")
    check("T6 重申段含圣经风格约束原文",
          "【风格约束 (项目风格圣经)】" in b5 and "冷色调低饱和青蓝夜景约束" in b5
          and "手持跟拍优先约束" in b5, f"b5={b5[:200]}")
    check("T6 只注入正面教训卡: 已验证卡全文在, 候选/否决卡零出现",
          "【正面教训记忆卡 (仅已验证)】" in b5 and "确认卡·夜景低照度记忆方案" in b5
          and "低照度+烟雾机" in b5 and "候选卡" not in b5 and "否决卡" not in b5
          and "未验证·不作正面教训" not in b5, f"b5={b5}")
    check("T6 round_no=10 (10%5==0) → 再重申, 第 10 轮标注",
          "第 10 轮" in injection.injection_block(mem_f, 10, 5))
    check("T6 remind_every=3 → 第 3 轮注入/第 4 轮空; remind_every=0 与 round 0 → 恒空",
          injection.injection_block(mem_f, 3, 3) != ""
          and injection.injection_block(mem_f, 4, 3) == ""
          and injection.injection_block(mem_f, 5, 0) == ""
          and injection.injection_block(mem_f, 0, 5) == "")
    check("T6 确定性: 同输入同输出 (逐字节)",
          injection.injection_block(mem_f, 5, 5) == b5)
    mem_g = open_memory(make_out(), "pending项目")
    pd = os.path.join(mem_g.out_dir, "dm_memory", "pending项目")
    os.makedirs(pd)
    with open(os.path.join(pd, "bible.md"), "w", encoding="utf-8") as f:
        f.write("## 蒸馏段 (LLM 蒸馏回填区)\n<!-- LLM_DISTILL_PENDING -->\n")
    check("T6 pending 圣经 (无卡) → 到节奏仍 \"\" (不把占位当风格结论)",
          injection.injection_block(mem_g, 5, 5) == "")
    _, _ = shot_cards.add_card(mem_g, {"标题": "确认卡·pending项目", "signal": "成片采用",
                                       "status": "confirmed", "方案": "固定机位"})
    b5g = injection.injection_block(mem_g, 5, 5)
    check("T6 pending 圣经 + 已验证卡 → 只出卡不出风格约束, 占位零出现",
          "确认卡·pending项目" in b5g and "风格约束" not in b5g
          and "LLM_DISTILL_PENDING" not in b5g, f"b5g={b5g}")
    mem_h = open_memory(make_out(), "上限项目")
    for i in range(7):
        _, _ = shot_cards.add_card(mem_h, {"标题": f"确认卡{i}·上限", "signal": "用户确认",
                                           "status": "confirmed", "方案": f"方案{i}"})
    b5h = injection.injection_block(mem_h, 5, 5)
    check("T6 卡上限: 7 张已验证卡只注入最近 5 张 (注入段有界)",
          b5h.count("【决策卡 ") == 5 and "确认卡6·上限" in b5h and "确认卡0·上限" not in b5h,
          f"n={b5h.count('【决策卡 ')}")
    out_bare = make_out()
    check("T6 缺 dm_memory 目录 → \"\" 且只读纪律 (零目录创建零写盘)",
          injection.injection_block(open_memory(out_bare, "裸项目"), 5, 5) == ""
          and not os.path.exists(os.path.join(out_bare, "dm_memory"))
          and os.listdir(out_bare) == [], f"ls={os.listdir(out_bare)}")

    # -----------------------------------------------------------------
    print("T7 additive 零漂移硬断言 (cinematic_studio 分镜提示词面)")
    PROJ = "记忆接线项目"

    def core_pack():
        return json.dumps({"_项目名": PROJ, "_随机种子": 42,
                           "_场景描述": "父女在厨房, 雨夜, 父亲切菜, 女儿坐桌边"},
                          ensure_ascii=False)

    def cine_build():
        kw = defaults(DirectorMasterCinematic)
        kw.update({"画面模式": "电影工作室", "目标时长(分钟)": 0.5,
                   "核心数据包": core_pack(), "剧本输入": "△ 内景 厨房 夜 △ 父亲切菜"})
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return DirectorMasterCinematic().build(**kw)

    _old_env = os.environ.pop("DM_MEMORY_DIR", None)
    try:
        empty = make_out()
        os.environ["DM_MEMORY_DIR"] = empty
        main0, json0 = cine_build()
        main0b, json0b = cine_build()
        check("T7 基线 (无记忆): 同输入重跑逐字节一致 + 记忆段缺席",
              main0 == main0b and json0 == json0b and "记忆注入" not in main0,
              f"eq={main0 == main0b}")
        rounds_only = make_out()
        st_ro = open_store(rounds_only, PROJ)
        for i in range(5):
            st_ro.commit(name=f"v{i+1}", files={"剧本": ("a.txt", f"内容{i}")})
        check("T8 轮次口径: 版本库 5 次提交 → project_rounds=5 (每轮归档提交=1 轮)",
              injection.project_rounds(rounds_only, PROJ) == 5
              and injection.project_rounds(empty, PROJ) == 0)
        os.environ["DM_MEMORY_DIR"] = rounds_only
        main1, json1 = cine_build()
        check("T7 缺 dm_memory 目录 (虽到节奏) → 分镜文本+JSON 逐字节不变 (硬断言)",
              main1 == main0 and json1 == json0, f"eq={main1 == main0}")
        pos = make_out()
        st_pos = open_store(pos, PROJ)
        for i in range(5):
            st_pos.commit(name=f"v{i+1}", files={"剧本": ("a.txt", f"内容{i}")})
        pos_dir = os.path.join(pos, "dm_memory", PROJ)
        os.makedirs(pos_dir)
        with open(os.path.join(pos_dir, "bible.md"), "w", encoding="utf-8") as f:
            f.write("# 项目风格圣经 — 记忆接线项目\n\n## 蒸馏段 (LLM 蒸馏回填区)\n"
                    "- 冷色调低饱和青蓝夜景约束\n- 手持跟拍优先约束\n\n## 采证口径\n- 测试夹具\n")
        mem_pos = open_memory(pos, PROJ)
        _, _ = shot_cards.add_card(mem_pos,
                                   {"标题": "确认卡·夜景低照度记忆方案", "signal": "用户确认",
                                    "status": "confirmed", "方案": "低照度+烟雾机",
                                    "教训": "夜景优先低照度"})
        _, _ = shot_cards.add_card(mem_pos,
                                   {"标题": "候选卡·手持长镜头记忆", "signal": "生成",
                                    "status": "candidate", "方案": "手持长镜头"})
        os.environ["DM_MEMORY_DIR"] = pos
        main2, json2 = cine_build()
        seg = injection.injection_block(open_memory(pos, PROJ), 5)
        check("T7 记忆在场且到节奏 → 注入段非空且 main 恰好=基线+\"\\n\\n\"+注入段 (additive 唯一增量)",
              seg and main2 == main0 + "\n\n" + seg,
              f"seg_len={len(seg)} eq={main2 == main0 + chr(10) * 2 + seg}")
        check("T7 分镜 JSON 输出恒零漂移 (接线只动文本面)",
              json2 == json0)
        check("T7 注入段内容可观测: 信任序/风格约束/已验证卡在, 候选卡与占位零出现",
              "记忆注入" in main2 and "冷色调低饱和青蓝夜景约束" in main2
              and "确认卡·夜景低照度记忆方案" in main2
              and "候选卡" not in main2 and "LLM_DISTILL_PENDING" not in main2)
    finally:
        if _old_env is None:
            os.environ.pop("DM_MEMORY_DIR", None)
        else:
            os.environ["DM_MEMORY_DIR"] = _old_env

    # -----------------------------------------------------------------
    print("T8 resolve_out_dir 解析口径")
    tmp_ok = make_out()
    _old = os.environ.pop("DM_MEMORY_DIR", None)
    try:
        os.environ["DM_MEMORY_DIR"] = tmp_ok
        check("T8 环境变量指向已存在目录 → 原样返回",
              injection.resolve_out_dir() == tmp_ok)
        os.environ["DM_MEMORY_DIR"] = os.path.join(tmp_ok, "不存在的目录")
        r_fb = injection.resolve_out_dir()
        check("T8 环境变量指向不存在目录 → 诚实降级 fallback (非该路径)",
              r_fb != os.path.join(tmp_ok, "不存在的目录") and isinstance(r_fb, str))
        os.environ.pop("DM_MEMORY_DIR", None)
        r_dft = injection.resolve_out_dir()
        check("T8 环境变量未设 → fallback 链返回非空目录字符串",
              isinstance(r_dft, str) and r_dft != "")
    finally:
        if _old is None:
            os.environ.pop("DM_MEMORY_DIR", None)
        else:
            os.environ["DM_MEMORY_DIR"] = _old

    # -----------------------------------------------------------------
    print("T9 R1 修复回归: 注入消费端对损坏存储容错 (M2 读侧口径的下游)")
    mem_brk = open_memory(make_out(), "容错项目")
    proj_brk = os.path.join(mem_brk.out_dir, "dm_memory", "容错项目")
    os.makedirs(proj_brk)
    with open(os.path.join(proj_brk, "bible.md"), "w", encoding="utf-8") as f:
        f.write("## 蒸馏段 (LLM 蒸馏回填区)\n- 冷色调低饱和青蓝夜景约束\n")
    with open(os.path.join(proj_brk, "cards.jsonl"), "wb") as f:
        f.write(b"\x00\x01\xff\xfe\x80binary garbage\n")
    blk_brk = injection.injection_block(mem_brk, 5)
    check("T9 cards.jsonl 二进制损坏 → 注入段只剩风格约束、卡段诚实缺席、不崩",
          bool(blk_brk) and "冷色调低饱和青蓝夜景约束" in blk_brk
          and "【正面教训记忆卡" not in blk_brk, f"blk={blk_brk[:80]!r}")
    with open(os.path.join(proj_brk, "bible.md"), "wb") as f:
        f.write(b"\xff\x00\x9f binary bible")
    _, _ = shot_cards.add_card(mem_brk, {"标题": "确认卡·容错", "signal": "用户确认",
                                         "status": "confirmed", "方案": "低照度"})
    blk_brk2 = injection.injection_block(mem_brk, 5)
    check("T9 bible.md 二进制损坏 → 风格约束诚实缺席、卡段仍在且损坏卡行被跳过、不崩",
          bool(blk_brk2) and "确认卡·容错" in blk_brk2 and "风格约束" not in blk_brk2,
          f"blk={blk_brk2[:80]!r}")
    check("T9 损坏注入消费零漂移口径: 任何异常不逃逸 (injection_block 恒 str)",
          isinstance(blk_brk, str) and isinstance(blk_brk2, str))

    # -----------------------------------------------------------------
    print("T10 R2 修复回归: MED-3 evolution.jsonl 二进制容错 (损坏行跳过+阈值记账可达+写路径自愈)")
    mem_evo = open_memory(make_out(), "进化容错")
    evo_path = evolution.evolution_path(mem_evo.out_dir, "进化容错")
    os.makedirs(os.path.dirname(evo_path), exist_ok=True)
    with open(evo_path, "wb") as f:  # 二进制坏行 + 两条合法 signal 行 (同类已计 2 次)
        f.write(b"\x00\x01\xff\xfe\x80broken binary line\n")
        f.write('{"event": "signal", "signal": "明确决策", "同类计数": 1, "ts": "t1"}\n'
                .encode("utf-8"))
        f.write('{"event": "signal", "signal": "明确决策", "同类计数": 2, "ts": "t2"}\n'
                .encode("utf-8"))
    err_evo = io.StringIO()
    with contextlib.redirect_stderr(err_evo):
        plan_evo = evolution.maybe_reflect(mem_evo, "明确决策")
    check("T10 MED-3 二进制坏行+合法行共存: 阈值记账不被损坏锁死 (2 存量+1 → 第 3 次出 plan)",
          isinstance(plan_evo, dict) and plan_evo.get("action") == "reflect"
          and plan_evo.get("同类计数") == 3 and plan_evo.get("阈值") == 3,
          f"plan={plan_evo}")
    check("T10 MED-3 损坏行跳过 stderr 告警在案 (计数=1)",
          "evolution.jsonl 有 1 行损坏" in err_evo.getvalue(),
          f"stderr={err_evo.getvalue()[:160]!r}")
    with open(evo_path, "rb") as f:
        lines_evo = [ln for ln in f.read().splitlines() if ln.strip()]
    parsed_evo = []
    for ln in lines_evo:
        try:
            parsed_evo.append(json.loads(ln.decode("utf-8")))
        except Exception:
            parsed_evo.append(None)
    check("T10 MED-3 损坏后 append 成功: 重写后全为合法 JSON 且存量合法行保留",
          all(e is not None for e in parsed_evo) and len(parsed_evo) == 4
          and sum(1 for e in parsed_evo if e.get("event") == "signal") == 3
          and sum(1 for e in parsed_evo if e.get("event") == "reflect") == 1,
          f"n={len(parsed_evo)} events={[e.get('event') if e else None for e in parsed_evo]}")
    plan_evo2 = evolution.maybe_reflect(mem_evo, "明确决策")
    check("T10 MED-3 已提议后计数窗口重置: 第 4 次同类不再立即出 plan",
          plan_evo2 is None, f"plan2={plan_evo2}")


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    finally:
        for d in TEMP_DIRS:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\ndm_memory 风格圣经+进化钩子+信任注入 测试结果: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
