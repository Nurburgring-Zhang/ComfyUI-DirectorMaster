# -*- coding: utf-8 -*-
"""
批次4 builder-m2 — dm_memory 检索/锚点互链/系列继承 测试 (tests/test_dm_memory_retrieve.py)
==========================================================================================
覆盖矩阵:
  T0 检索召回 (验收⑥): 构造中文语料 → 查询 → 正确命中断言 → 注入段含记忆内容原文
  T1 双通道检索: 结构键精确过滤 (镜号/项目/状态, 别名互通) + 未知键诚实报错 + 同输入同输出确定性
  T2 选型钉板: 无 DM_EMBED_MODEL / 指向不存在文件 → detect None + backend_status 诚实降级文案 (非报错); 默认 wordfreq
  T3 数据层直读: cards.jsonl 缺文件按空 / 坏行空行诚实跳过
  T4 系列继承 (验收⑦): 系列档案落盘 → 继承到新项目 → 记录含 source_series/inherited_at/fingerprints (指纹逐字节核对)
  T5 DNA 校验管线 (验收⑦/R1 MED-3): 含抽象词的负样本维度被拒, 诚实跳过并记录原因
  T6 adaptive 阈值: <5 新版本且 <24h 不提示; ≥5 新版本 或 ≥24h 才提示
  T7 窗口外报缺不删: 锚点 vid 出 store.log 窗口 → out_of_window 标记保留, 锚点不删
  T8 R1 修复回归: M2 cards 读取二进制容错 (损坏行跳过/合法行消费/写不锁死)
     + M3 series_id 碰撞防覆写 (两 id 两档案/确定性)
  T9 R2 修复回归: MED-4 系列档案入库脱敏 (自由文本递归/结构键不碰/幂等)
     + LOW-1 幽灵卡软过滤 (伪 JSON 坏行两读侧跳过/不进索引)
退出码: 0 = 全部通过, 1 = 有失败。运行: python -X utf8 tests/test_dm_memory_retrieve.py
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from aggregator import version_store
from aggregator.character_dna import NOT_PROVIDED, build_dna_profile
from aggregator.dm_memory import anchor_link, open_memory, retrieval, series_inherit, shot_cards

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def _write_cards(out_dir, project, cards, extra_lines=()):
    path = retrieval.cards_path(out_dir, project)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
        for ln in extra_lines:
            f.write(ln + "\n")


_CORPUS = [
    {"card_id": "c_kitchen", "title": "深夜厨房场景用暖色灯光, 蒸汽模糊窗玻璃",
     "status": "approved", "signal": "用户确认", "anchors": ["v1"],
     "镜号": "SC01", "project": "夜市"},
    {"card_id": "c_street", "title": "雨夜街头霓虹反射, 手持跟拍长镜头",
     "status": "approved", "signal": "成片采用", "anchors": ["v2"],
     "镜号": "SC02", "project": "夜市"},
    {"card_id": "c_school", "title": "白天教室自然光, 固定机位平拍",
     "status": "candidate", "signal": "生成", "anchors": [],
     "镜号": "SC03", "project": "校园"},
    {"card_id": "c_rejected", "title": "夜市厨房改用冷蓝色调方案",
     "status": "rejected", "signal": "用户纠正", "anchors": [], "被否方案": "冷蓝色调",
     "镜号": "SC04", "project": "夜市"},
]


# =====================================================================
def run_suite():
    tmp = tempfile.mkdtemp(prefix="dm_mem_t_")
    try:
        # -------------------------------------------------------------
        print("T0 检索召回 (验收⑥)")
        out0, proj0 = os.path.join(tmp, "t0"), "夜市项目"
        _write_cards(out0, proj0, _CORPUS)
        idx = retrieval.WordFreqIndex()
        for c in retrieval.load_cards(out0, proj0):
            idx.add(c)
        hits = idx.query("深夜厨房 灯光", top_k=3)
        check("T0 中文语料查询正确命中 (top1=厨房决策卡)",
              bool(hits) and hits[0]["doc_id"] == "c_kitchen",
              f"hits={[h['doc_id'] for h in hits]}")
        check("T0 命中分值>0 且压过干扰卡",
              hits[0]["score"] > 0 and (len(hits) < 2 or hits[0]["score"] > hits[1]["score"]),
              f"scores={[h['score'] for h in hits]}")
        seg = "\n".join(str(h["doc"].get("title", "")) for h in hits)
        check("T0 注入段含记忆内容原文",
              "深夜厨房场景用暖色灯光, 蒸汽模糊窗玻璃" in seg, f"seg={seg[:80]}")
        check("T0 命中携带完整原卡 (结构键/状态在 doc 内)",
              hits[0]["doc"].get("镜号") == "SC01" and hits[0]["doc"].get("status") == "approved",
              f"doc={hits[0]['doc'] if hits else None}")
        check("T0 无关查询零命中 (不硬凑)", idx.query("外星舰队决战") == [], )

        # -------------------------------------------------------------
        print("T1 双通道检索")
        r1 = idx.query("", filters={"镜号": "SC02"})
        check("T1 结构键精确过滤 镜号", [h["doc_id"] for h in r1] == ["c_street"],
              f"got={[h['doc_id'] for h in r1]}")
        r2 = idx.query("厨房", filters={"状态": "rejected"})
        check("T1 字面×结构双通道 (状态=rejected 且含 厨房)",
              [h["doc_id"] for h in r2] == ["c_rejected"], f"got={[h['doc_id'] for h in r2]}")
        r3 = idx.query("", filters={"project": "夜市"})
        check("T1 英文别名键互通 (project→项目)",
              sorted(h["doc_id"] for h in r3) == ["c_kitchen", "c_rejected", "c_street"],
              f"got={sorted(h['doc_id'] for h in r3)}")
        raised = False
        try:
            idx.query("x", {"作者": "张三"})
        except ValueError:
            raised = True
        check("T1 未知结构键诚实报错 (不静默空结果)", raised)
        idx_b = retrieval.WordFreqIndex()
        for c in _CORPUS:
            idx_b.add(c)
        a = idx.query("深夜厨房 灯光", top_k=5)
        b = idx_b.query("深夜厨房 灯光", top_k=5)
        check("T1 同输入同输出确定性 (两独立索引逐字节一致)",
              json.dumps(a, ensure_ascii=False, sort_keys=True)
              == json.dumps(b, ensure_ascii=False, sort_keys=True))
        check("T1 重复查询结果稳定",
              json.dumps(idx.query("深夜厨房 灯光", top_k=5), ensure_ascii=False, sort_keys=True)
              == json.dumps(a, ensure_ascii=False, sort_keys=True))

        # -------------------------------------------------------------
        print("T2 选型钉板 (嵌入档诚实探测)")
        saved_env = os.environ.pop("DM_EMBED_MODEL", None)
        try:
            idx_w, st_w = retrieval.make_index()
            check("T2 默认选型 wordfreq 主档",
                  st_w == "wordfreq" and isinstance(idx_w, retrieval.WordFreqIndex),
                  f"status={st_w}")
            _i, st_ne = retrieval.make_index(prefer_embedding=True)
            check("T2 无 DM_EMBED_MODEL → 诚实降级文案 (非报错)",
                  st_ne.startswith("wordfreq (embedding unavailable:") and "未设置" in st_ne,
                  f"status={st_ne}")
            check("T2 条件不满足 → detect_embedding_provider 为 None",
                  retrieval.detect_embedding_provider() is None)
            os.environ["DM_EMBED_MODEL"] = os.path.join(tmp, "no_such", "model.onnx")
            check("T2 模型路径不存在 → detect 仍 None",
                  retrieval.detect_embedding_provider() is None)
            _i2, st_nf = retrieval.make_index(prefer_embedding=True)
            check("T2 模型文件不存在 → 降级文案标注原因",
                  st_nf.startswith("wordfreq (embedding unavailable:") and "不存在" in st_nf,
                  f"status={st_nf}")
            check("T2 降级仍返回可用词频主档 (不是伪造嵌入档)",
                  isinstance(_i2, retrieval.WordFreqIndex))
        finally:
            if saved_env is None:
                os.environ.pop("DM_EMBED_MODEL", None)
            else:
                os.environ["DM_EMBED_MODEL"] = saved_env

        # -------------------------------------------------------------
        print("T3 数据层直读 cards.jsonl")
        out3 = os.path.join(tmp, "t3")
        _write_cards(out3, "p3",
                     [{"card_id": "a", "title": "一"}, {"card_id": "b", "title": "二"}],
                     extra_lines=["{{{坏行", ""])
        got = retrieval.load_cards(out3, "p3")
        check("T3 坏行/空行诚实跳过, 好数据完整保序",
              [c["card_id"] for c in got] == ["a", "b"], f"got={got}")
        check("T3 缺文件按空处理 (不报错)",
              retrieval.load_cards(os.path.join(tmp, "nope"), "p3") == [])

        # -------------------------------------------------------------
        print("T4 系列继承 (验收⑦)")
        out4 = os.path.join(tmp, "t4")
        good = build_dna_profile("老陈", "单眼皮, 短发, 瘦削", "工作服")
        good_entry = dict(good)
        good_entry["角色名"] = "老陈"
        polluted = {"dna_version": 1,
                    "维度": {"眼型": "绝美神秘电眼", "发型": "马尾",
                             "体态": "瘦削", "脸型": "高级脸"},
                    "promptBlock": "污染:眼型:绝美神秘电眼", "抽象词": [],
                    "角色名": "污染角色"}
        payload = {"worldview": "九十年代南方小城, 潮湿闷热, 老巷与夜市",
                   "风格锚": "王家卫·霓虹·手持",
                   "dna": [good_entry, polluted]}
        series_inherit.upsert_series(out4, "ser-01", payload)
        sdir = os.path.join(out4, "dm_memory", "_series")
        files = os.listdir(sdir) if os.path.isdir(sdir) else []
        check("T4 系列档案落盘 _series/<safe>.json",
              len(files) == 1 and files[0].endswith(".json"), f"files={files}")
        with open(os.path.join(sdir, files[0]), "r", encoding="utf-8") as f:
            on_disk = json.load(f)
        check("T4 系列档案内容含 series_id 与 dna 列表",
              on_disk.get("series_id") == "ser-01" and len(on_disk.get("dna", [])) == 2,
              f"disk={str(on_disk)[:120]}")
        rec = series_inherit.inherit_to_project(out4, "ser-01", "新项目A")
        check("T4 追溯记录含来源系列", rec["source_series"] == "ser-01",
              f"rec={str(rec)[:120]}")
        check("T4 追溯记录含继承时间戳",
              bool(re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", rec["inherited_at"])),
              f"at={rec['inherited_at']}")
        check("T4 指纹逐字节可核对 (worldview)",
              rec["fingerprints"].get("worldview")
              == hashlib.sha256(payload["worldview"].encode("utf-8")).hexdigest(),
              f"fps={sorted(rec['fingerprints'])}")
        check("T4 指纹逐字节可核对 (风格锚)",
              rec["fingerprints"].get("风格锚")
              == hashlib.sha256(payload["风格锚"].encode("utf-8")).hexdigest())
        inh = {d["角色名"]: d["profile"] for d in rec["dna"]}
        check("T4 合法 DNA 维度经管线继承保留",
              inh["老陈"]["维度"]["眼型"] == "单眼皮"
              and inh["老陈"]["维度"]["标志着装"] == "工作服",
              f"dims={inh.get('老陈', {}).get('维度')}")
        check("T4 DNA 指纹 = 校验管线产出内容指纹",
              rec["fingerprints"].get("dna:老陈")
              == hashlib.sha256(json.dumps(inh["老陈"], ensure_ascii=False,
                                           sort_keys=True).encode("utf-8")).hexdigest())
        raised = False
        try:
            series_inherit.inherit_to_project(out4, "缺系列", "x")
        except ValueError:
            raised = True
        check("T4 缺系列档案诚实报错 (不伪造空继承)", raised)

        # -------------------------------------------------------------
        print("T5 DNA 校验管线: 抽象词负样本 (R1 MED-3)")
        pz = inh["污染角色"]
        check("T5 抽象词维度被校验管线拒为 未提供",
              pz["维度"]["眼型"] == NOT_PROVIDED and pz["维度"]["脸型"] == NOT_PROVIDED,
              f"dims={pz['维度']}")
        check("T5 具体词维度不被连坐",
              pz["维度"]["发型"] == "马尾" and pz["维度"]["体态"] == "瘦削",
              f"dims={pz['维度']}")
        check("T5 命中禁词入账 抽象词",
              "神秘" in pz["抽象词"] and "绝美" in pz["抽象词"] and "高级" in pz["抽象词"],
              f"rej={pz['抽象词']}")
        check("T5 禁词零残留于继承产物维度",
              not any(w in json.dumps(pz["维度"], ensure_ascii=False)
                      for w in ("神秘", "绝美", "高级")),
              f"dims={pz['维度']}")
        eye = [s for s in rec["skipped"] if s["角色名"] == "污染角色" and s["维度"] == "眼型"]
        check("T5 跳过维度记录原因 (拒抽象词 + 原值)",
              len(eye) == 1 and "拒抽象词" in eye[0]["原因"]
              and eye[0]["原始值"] == "绝美神秘电眼", f"skip={eye}")
        check("T5 跳过原因覆盖全部被拒维 (眼型/脸型)",
              {s["维度"] for s in rec["skipped"] if s["角色名"] == "污染角色"}
              == {"眼型", "脸型"},
              f"skipped={rec['skipped']}")
        check("T5 继承 promptBlock 重算且 ≤200",
              0 < len(pz["promptBlock"]) <= 200, f"block={pz['promptBlock']}")

        # -------------------------------------------------------------
        print("T6 adaptive 阈值")
        out6, proj6 = os.path.join(tmp, "t6"), "adaptiveP"
        store6 = version_store.open_store(out6, proj6)
        mem6 = open_memory(out6, proj6)
        for i in range(3):
            store6.commit(f"第{i}版", {"剧本": (f"s{i}.txt", "剧情内容" * 20)})
        r1 = anchor_link.sync_check(mem6, store6)
        check("T6 首次对账 3 新版本 <5 → 不提示",
              r1["new_versions"] == 3 and r1["should_prompt"] is False, f"r1={r1}")
        check("T6 无锚点时 stale 为空", r1["stale_cards"] == [])
        for i in range(3, 5):
            store6.commit(f"第{i}版", {"剧本": (f"s{i}.txt", "剧情内容" * 20)})
        r2 = anchor_link.sync_check(mem6, store6)
        check("T6 自上次提示新版本达 5 → 提示",
              r2["new_versions"] == 5 and r2["should_prompt"] is True, f"r2={r2}")
        a6 = anchor_link.anchors_path(out6, proj6)
        with open(a6, "r", encoding="utf-8") as f:
            st6 = json.load(f)
        check("T6 提示时刻已记录 (adaptive 状态落盘)",
              isinstance(st6.get("adaptive", {}).get("last_prompt_at"), int),
              f"adaptive={st6.get('adaptive')}")
        r3 = anchor_link.sync_check(mem6, store6)
        check("T6 提示后 <5 新版本且 <24h → 不再提示",
              r3["new_versions"] == 0 and r3["should_prompt"] is False, f"r3={r3}")
        st6["adaptive"]["last_prompt_at"] -= 25 * 3600 * 1000  # 回拨 25h
        with open(a6, "w", encoding="utf-8") as f:
            json.dump(st6, f, ensure_ascii=False)
        r4 = anchor_link.sync_check(mem6, store6)
        check("T6 距上次提示 ≥24h → 再次提示",
              r4["should_prompt"] is True and r4["new_versions"] == 0, f"r4={r4}")

        # -------------------------------------------------------------
        print("T7 窗口外报缺不删")
        out7, proj7 = os.path.join(tmp, "t7"), "窗口P"
        store7 = version_store.open_store(out7, proj7)
        mem7 = open_memory(out7, proj7)
        vids7 = [store7.commit(f"n{i}", {"剧本": (f"n{i}.txt", "版本数据" * 30)})
                 for i in range(22)]  # 超过 MAX_VERSIONS=20 → 最老版本出窗
        anchor_link.link_card(mem7, "冷卡", vids7[0])
        anchor_link.link_card(mem7, "新卡", vids7[-1])
        check("T7 link_card 幂等去重保序",
              anchor_link.link_card(mem7, "新卡", vids7[-1]) == [vids7[-1]])
        r7 = anchor_link.sync_check(mem7, store7)
        check("T7 出窗 vid 计入 out_of_window 报缺",
              vids7[0] in r7["out_of_window"].get("冷卡", []), f"oow={r7['out_of_window']}")
        check("T7 stale_cards 报缺且不含在窗卡",
              "冷卡" in r7["stale_cards"] and "新卡" not in r7["stale_cards"],
              f"stale={r7['stale_cards']}")
        with open(anchor_link.anchors_path(out7, proj7), "r", encoding="utf-8") as f:
            st7 = json.load(f)
        check("T7 锚点保留不删 (出窗 vid 仍在互链)",
              vids7[0] in st7["links"]["冷卡"], f"links={st7['links']}")
        check("T7 出窗标记落盘",
              st7["out_of_window"].get("冷卡") == [vids7[0]],
              f"oow={st7['out_of_window']}")
        check("T7 在窗锚点不误报",
              not st7["out_of_window"].get("新卡"), f"oow={st7['out_of_window']}")

        # -------------------------------------------------------------
        print("T8 R1 修复回归: M2 cards 读取二进制容错 + M3 series_id 碰撞防护")
        out8 = os.path.join(tmp, "t8")
        _write_cards(out8, "p8",
                     [{"card_id": "good1", "title": "夜景低照度"},
                      {"card_id": "good2", "title": "手持跟拍"}])
        path8 = retrieval.cards_path(out8, "p8")
        with open(path8, "ab") as f:  # 追加一行非法 UTF-8 字节 + 一行合法卡
            f.write(b"\xff\xfe\x00\x9f binary garbage\n")
            f.write('{"card_id": "good3", "title": "雾机分层"}\n'.encode("utf-8"))
        got8 = retrieval.load_cards(out8, "p8")
        check("T8 M2 load_cards: 二进制行降级跳过, 合法行 (含损坏后追加行) 照常消费",
              [c["card_id"] for c in got8] == ["good1", "good2", "good3"],
              f"got={[c['card_id'] for c in got8]}")
        mem8 = open_memory(out8, "p8")
        check("T8 M2 list_cards: 同一二进制行不崩且跳过 (读侧同口径)",
              [c["card_id"] for c in shot_cards.list_cards(mem8)]
              == ["good1", "good2", "good3"])
        cid8, reason8 = shot_cards.add_card(mem8, {"标题": "追加卡", "signal": "用户确认",
                                                   "status": "confirmed", "方案": "低照度"})
        check("T8 M2 损坏不锁写: add_card 照常追加并可读回",
              reason8 == "" and bool(cid8)
              and any(c["card_id"] == cid8 for c in shot_cards.list_cards(mem8)),
              f"cid={cid8}")
        # 整文件二进制损坏: 三读取方全不崩, 写路径自愈 (追加后合法行可消费)
        out8b = os.path.join(tmp, "t8b")
        mem8b = open_memory(out8b, "p8b")
        shot_cards.add_card(mem8b, {"标题": "x", "signal": "生成", "status": "candidate"})
        # R2 MED-2 后 <safe_project> 含 ASCII 字母时带 sha1 后缀 — 路径按 safe_name 渲染 (断言语义不变)
        p8b = os.path.join(out8b, "dm_memory", shot_cards._safe_name("p8b"), "cards.jsonl")
        with open(p8b, "wb") as f:
            f.write(b"\x00\x01\xff\xfe\x80binary")
        n8b, cid8b, n8c, exc8b = -1, None, -1, None
        try:
            n8b = len(shot_cards.list_cards(mem8b))
            cid8b, _ = shot_cards.add_card(mem8b, {"标题": "y", "signal": "生成",
                                                   "status": "candidate"})
            n8c = len(retrieval.load_cards(out8b, "p8b"))
        except Exception as e:  # noqa: BLE001 — 回归断言: 不应有任何异常逃逸
            exc8b = e
        check("T8 M2 整文件二进制损坏: list/add/load 全不崩且损坏行跳过 (0 存活)",
              exc8b is None and n8b == 0, f"exc={exc8b} n_list={n8b}")
        check("T8 M2 整文件二进制损坏: 写路径自愈 — 追加后合法行照常消费",
              bool(cid8b) and n8c == 1, f"cid={cid8b} n_load={n8c}")
        # M3: series_id 碰撞防覆写
        out8s = os.path.join(tmp, "t8s")
        series_inherit.upsert_series(out8s, "系/列A", {"worldview": "w", "风格锚": "s",
                                                       "dna": []})
        series_inherit.upsert_series(out8s, "系:列A", {"worldview": "w2", "风格锚": "s2",
                                                       "dna": []})
        sdir8 = os.path.join(out8s, "dm_memory", "_series")
        files8 = sorted(os.listdir(sdir8))
        check("T8 M3 series_id 分隔符碰撞 → 两 id 两档案文件 (不再静默覆写)",
              len(files8) == 2, f"files={files8}")
        rec8a = series_inherit.inherit_to_project(out8s, "系/列A", "项目甲")
        rec8b = series_inherit.inherit_to_project(out8s, "系:列A", "项目乙")
        check("T8 M3 两系列档案各自可继承且内容不串档",
              rec8a["worldview"] == "w" and rec8b["worldview"] == "w2",
              f"a={rec8a['worldview']} b={rec8b['worldview']}")
        check("T8 M3 碰撞防护确定性: 同一原始 id 恒映射同一路径",
              series_inherit.series_path(out8s, "系/列A")
              == series_inherit.series_path(out8s, "系/列A"))

        # -------------------------------------------------------------
        print("T9 R2 修复回归: MED-4 系列档案入库脱敏 + LOW-1 幽灵卡软过滤")
        # ---- MED-4: upsert_series 自由文本脱敏 (worldview/风格锚/dna 内嵌套 str) ----
        out9 = os.path.join(tmp, "t9")
        pii9 = {"worldview": "世界观: 联系 zhangsan@example.com 复盘",
                "风格锚": "风格: 密钥 sk-proj-abc123XYZdef456ghi789 勿外传",
                "dna": [{"维度": "色彩", "值": "补光可联系 13812345678"},
                        "纯文本 dna 元素 password: abcdef12345678"],
                "镜头数": 42, "状态": "active"}
        series_inherit.upsert_series(out9, "PII系列", pii9)
        s9 = series_inherit.series_path(out9, "PII系列")
        with open(s9, "r", encoding="utf-8") as f:
            raw9 = f.read()
        doc9 = json.loads(raw9)
        check("T9 MED-4 worldview/风格锚 PII 落盘零残留且占位符在",
              "zhangsan@example.com" not in raw9 and "[邮箱]" in doc9["worldview"]
              and "sk-proj-abc123XYZdef456ghi789" not in raw9
              and "[API密钥]" in doc9["风格锚"],
              f"worldview={doc9['worldview']!r} 风格锚={doc9['风格锚']!r}")
        check("T9 MED-4 dna 内嵌套 str 逐元素脱敏 (dict/list 混合) 且长度不变",
              "13812345678" not in json.dumps(doc9["dna"], ensure_ascii=False)
              and "[手机号]" in doc9["dna"][0]["值"]
              and "abcdef12345678" not in raw9 and "[API密钥]" in doc9["dna"][1]
              and len(doc9["dna"]) == 2,
              f"dna={doc9['dna']}")
        check("T9 MED-4 结构键不碰 (数字/枚举原样) + 元数据齐备",
              doc9["镜头数"] == 42 and doc9["状态"] == "active"
              and doc9["series_id"] == "PII系列" and bool(doc9.get("updated_at")),
              f"doc9={doc9}")
        doc9b = series_inherit.upsert_series(out9, "PII系列", pii9)
        sdir9 = os.path.join(out9, "dm_memory", "_series")
        check("T9 MED-4 幂等 upsert: 同输入同文件且内容 (除 updated_at) 一致",
              os.listdir(sdir9) == [os.path.basename(s9)]
              and {k: v for k, v in doc9b.items() if k != "updated_at"}
              == {k: v for k, v in doc9.items() if k != "updated_at"},
              f"files={os.listdir(sdir9)}")
        # ---- LOW-1: 幽灵卡软过滤 (decode(errors=replace) 把坏行"修复"成合法 JSON) ----
        out9g = os.path.join(tmp, "t9g")
        _write_cards(out9g, "p9g", [{"card_id": "g1", "title": "正常卡"}])
        p9g = retrieval.cards_path(out9g, "p9g")
        with open(p9g, "ab") as f:  # 幽灵行: 替换解码后恰为合法 JSON, 缺卡片标识字段
            f.write(b'\n{"\xff\xab": 1, "note": "leak-probe"}\n')
        err9g = io.StringIO()
        with contextlib.redirect_stderr(err9g):
            got9g = retrieval.load_cards(out9g, "p9g")
            mem9g = open_memory(out9g, "p9g")
            listed9g = shot_cards.list_cards(mem9g)
        check("T9 LOW-1 幽灵行两读侧均跳过 (stderr 告警), 合法行不受影响",
              [c["card_id"] for c in got9g] == ["g1"]
              and [c["card_id"] for c in listed9g] == ["g1"]
              and err9g.getvalue().count("疑似幽灵卡") == 2,
              f"got={got9g} listed={listed9g} stderr={err9g.getvalue()[:120]!r}")
        idx9g = retrieval.WordFreqIndex()
        for c in got9g:
            idx9g.add(c)
        check("T9 LOW-1 幽灵行不进检索索引 (leak-probe 零命中)",
              idx9g.query("leak-probe") == [], f"hits={idx9g.query('leak-probe')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =====================================================================
def main():
    try:
        run_suite()
    except Exception as e:
        check("套件意外异常 (不应发生)", False, f"{type(e).__name__}: {e}")
    print(f"\ndm_memory 检索/锚点/继承 测试结果: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
