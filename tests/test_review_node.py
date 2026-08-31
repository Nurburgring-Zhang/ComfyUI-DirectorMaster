# -*- coding: utf-8 -*-
"""
V16.7.0-MERGED 批次3 D6 — 独立审查引擎 + DirectorMasterReview 节点测试
====================================================================
不依赖 pytest:  python -X utf8 tests/test_review_node.py

覆盖 (design_batch3.md §6 D6 验收):
  1. 节点注册: DirectorMasterReview 入 _NODE_SPECS (黑盒 spec 加载 __init__.py),
     审查模式下拉恰好 3 个创作选项 (无 🎲 随机/全部/自动/无(默认) 伪选项),
     INPUT_TYPES/RETURN_TYPES/FUNCTION 完整, 显示名非空
  2. 确定性轨: 合法分镜 + brief → 13 项清单零 FAIL; 纯规则核对真实可用
  3. 编号报告: R-001 起连续编号, 每条 severity/item/证据字段完整, 报告关键段齐全
  4. 断点续跑 (CheckpointStore 真实落盘): 清内存重入已完成阶段跳过 (阶段产物
     从磁盘恢复且发现逐条一致); 输入变更自动失效重算; clear 后全重算;
     快速审查 → 全量审查 跨模式复用 completeness 阶段
  5. LLM 语义轨 (f2 式本地 OpenAI 兼容服务器, 真实 HTTP): 合格 JSON 发现合并
     (source=llm, R 编号接续); 服务器 500 → 诚实落回确定性轨; 不可解析输出丢弃
  6. 无法验证路径: 无 brief → C09/C10 显式标注; 纯文本产物 → 结构项显式标注;
     对比分镜缺基准 → X01 显式标注 (缺输入不猜测)
  7. 判例库: 在场时引用与自检问题清单; sys.modules 注入缺位 → 诚实降级不崩
  8. 对抗输入: 畸形 JSON/坏基准/非法 mode (ValueError) 不崩且诚实上报

退出码: 0 = 全部通过, 1 = 有失败
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import importlib.util

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.dirname(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

PASS, FAIL = 0, 0
RESULTS = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        RESULTS.append({"label": label, "ok": True})
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        RESULTS.append({"label": label, "ok": False, "detail": str(detail)[:300]})
        print(f"  [FAIL] {label} {detail}")


# ------------------------------------------------------------------ fixtures
def shot(n, dur, size, move, focus, sound, purpose, first, prompt, extra=None):
    d = {"镜号": n, "时长": dur, "景别": size, "运镜": move, "画面焦点": focus,
         "声音": sound, "转场": "硬切", "叙事目的": purpose,
         "首帧描述": first, "AIGC提示词": prompt}
    if extra:
        d.update(extra)
    return d


GOOD_SB = {
    "contract_version": 1, "分镜数": 4, "总时长秒": 16.0,
    "导演": "[电影] 王家卫", "情绪": "孤独", "画面模式": "电影工作室",
    "分镜表": [
        shot(1, "4.0s", "全景", "固定", "便利店霓虹", "雨声+环境底噪", "建立场景",
             "雨夜便利店门口全景", "雨夜便利店门口全景, 霓虹灯反射在湿漉漉的路面"),
        shot(2, 4.0, "特写", "跟拍", "女主角侧脸", "雨声渐强", "情绪铺垫",
             "便利店玻璃上的雨珠特写", "便利店玻璃上的雨珠特写, 女主角的倒影与霓虹光斑重叠, 雨夜"),
        shot(3, "4.0s", "中景", "推镜", "柜台物件", "收音机底噪", "物件叙事",
             "便利店柜台上的过期饭团", "便利店柜台上的过期饭团, 标签起泡, 雨夜灯光下女主角伸手"),
        shot(4, 4.0, "近景", "手持", "女主角回头", "雨声收束", "收束悬念",
             "女主角回头的近景", "女主角在便利店灯光下回头, 雨夜的玻璃门外空无一人"),
    ],
}
GOOD_TEXT = json.dumps(GOOD_SB, ensure_ascii=False)
BRIEF = {"_导演风格": "[电影] 王家卫", "_情绪基调": "孤独",
         "_场景描述": "雨夜的便利店, 女主角等着一个人", "_成片时长": 16.0,
         "_项目名": "审查测试"}

# 存在缺陷的产物: 镜数不符 (3 vs 4) + 镜2 缺 AIGC提示词 + 时长覆盖偏差 (Σ16 vs 声明20)
# + 手法连用 (镜1-镜2 同全景/固定) + 空洞词 + 元语言占位词 + 导演/情绪与 brief 不一致
BAD_SB = {
    "contract_version": 1, "分镜数": 3, "总时长秒": 20.0,
    "导演": "是枝裕和", "情绪": "温暖",
    "分镜表": [
        shot(1, "4.0s", "全景", "固定", "便利店霓虹", "雨声", "建立场景",
             "全景", "雨夜便利店门口全景, 史诗感拉满"),
        shot(2, "4.0s", "全景", "固定", "便利店货架", "雨声", "陈列物件",
             "货架特写", "货架陈列"),
        shot(3, "4.0s", "特写", "推镜", "女主角", "雨声", "情绪",
             "女主角近景", "女主角回头, 待补充镜头"),
        shot(4, "4.0s", "近景", "手持", "窗外", "雨声", "收束",
             "窗外雨景", "窗外雨夜"),
    ],
}
del BAD_SB["分镜表"][1]["AIGC提示词"]  # 镜2 缺必填核心字段 → C04 FAIL (证据=镜2·AIGC提示词)
BAD_TEXT = json.dumps(BAD_SB, ensure_ascii=False)

_TEXT_ARTIFACT = "第一场: 雨夜的便利店, 女主角等着一个人。\n她数着货架上的罐头, 等一句没说出口的话。"


def mk_store(tmp):
    from aggregator.pipeline_checkpoint import CheckpointStore
    return CheckpointStore(tmp)


def findings_of(r, item=None, sev=None, source=None):
    out = r["findings"]
    if item is not None:
        out = [f for f in out if f["item"] == item]
    if sev is not None:
        out = [f for f in out if f["severity"] == sev]
    if source is not None:
        out = [f for f in out if f.get("source") == source]
    return out


# ------------------------------------------------------------------ 1. 节点注册
print("=" * 66)
print("1. 节点注册 (黑盒 spec 加载 __init__.py, legacy 环境变量隔离)")
print("=" * 66)
os.environ.pop("DIRECTORMASTER_LEGACY_NODES", None)
try:
    spec = importlib.util.spec_from_file_location("_dm_review_test", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["_dm_review_test"] = pkg
    spec.loader.exec_module(pkg)
    check("DirectorMasterReview 在 NODE_CLASS_MAPPINGS (入 _NODE_SPECS)",
          "DirectorMasterReview" in pkg.NODE_CLASS_MAPPINGS)
    check("DirectorMasterReview 有非空中文显示名",
          bool((pkg.NODE_DISPLAY_NAME_MAPPINGS.get("DirectorMasterReview") or "").strip()))
    cls = pkg.NODE_CLASS_MAPPINGS["DirectorMasterReview"]
    it = cls.INPUT_TYPES()
    opts = [str(o) for o in it["required"]["审查模式"][0]]
    check("审查模式下拉恰好 3 个选项", opts == ["快速结构审查", "全量审查", "对比分镜"], f"opts={opts}")
    pseudo = [o for o in opts if ("🎲" in o or o.startswith("全部") or "自动" in o or o == "无(默认)")]
    check("无默认/自动/随机伪选项", not pseudo, f"pseudo={pseudo}")
    check("被审产物为必填 STRING (forceInput)",
          it["required"]["被审产物"][0] == "STRING" and it["required"]["被审产物"][1].get("forceInput") is True)
    check("RETURN_TYPES 为双 STRING (报告+JSON)", cls.RETURN_TYPES == ("STRING", "STRING"))
    check("FUNCTION review_build 可调用",
          callable(getattr(cls, cls.FUNCTION, None)))
    check("审查模式选项与 manifest creative 逐字一致",
          opts == json.load(open(os.path.join(ROOT, "tests", "mode_manifest.json"), encoding="utf-8"))
          ["nodes"]["DirectorMasterReview"]["creative"])
except Exception as e:
    check("节点注册段加载", False, repr(e))

from aggregator.review_engine import (
    review_artifacts, REVIEW_MODES, ITEM_IDS, ITEM_STAGE, MODE_STAGES,
    MODE_QUICK, MODE_FULL, MODE_COMPARE, PIPELINE_ID,
    DirectorMasterReview,
)

# ------------------------------------------------------------------ 2. 确定性轨
print("\n2. 确定性轨 (合法分镜 + brief → 全过)")
print("=" * 66)
tmp1 = tempfile.mkdtemp(prefix="dm_review_t1_")
try:
    store1 = mk_store(tmp1)
    r = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL, checkpoint_store=store1)
    check("合法分镜审查 ok=True (无 FAIL 级发现)", r["ok"] is True,
          f"fails={[f['id'] + f['message'][:40] for f in findings_of(r, sev='FAIL')]}")
    check("审查轨标注为确定性轨", "确定性轨" in r["track"] and "LLM" not in r["track"].split("（")[0])
    check("13 项清单全部可判且通过", r["summary"]["pass"] == 13,
          f"item_status={r['item_status']}")
    check("时长覆盖项通过 (Σ16.0 vs 声明 16.0)", r["item_status"]["C06"] == "pass")
    check("场景锚定项通过 (brief 锚词命中)", r["item_status"]["C09"] == "pass")
    check("分镜契约校验通过 (复用 storyboard_contract)", r["item_status"]["C02"] == "pass")
finally:
    shutil.rmtree(tmp1, ignore_errors=True)

# ------------------------------------------------------------------ 3. 编号报告
print("\n3. 编号报告结构 (R-001 起 + 证据字段)")
print("=" * 66)
tmp2 = tempfile.mkdtemp(prefix="dm_review_t2_")
try:
    r = review_artifacts(BAD_TEXT, brief=BRIEF, mode=MODE_FULL,
                         checkpoint_dir=tmp2, checkpoint_enabled=False)
    fs = r["findings"]
    ids = [f["id"] for f in fs]
    check("发现按 R-001 起连续编号",
          ids == ["R-%03d" % i for i in range(1, len(fs) + 1)], f"ids={ids[:12]}")
    check("每条发现 severity/item/message/source 齐全",
          all(f.get("severity") in ("FAIL", "WARN", "INFO") and f.get("item") and
              f.get("message") and f.get("source") in ("deterministic", "llm") for f in fs))
    check("每条发现携带证据字段 (shot/field 至少其一或全文)",
          all((f.get("shot") or f.get("field")) for f in fs))
    check("镜数不符被抓 (C03 FAIL, 3 vs 4)",
          any(f["item"] == "C03" and f["severity"] == "FAIL" and "3" in f["message"] and "4" in f["message"]
              for f in fs))
    check("时长覆盖偏差被抓 (C06 FAIL, 20 vs 16, ±1% 门槛)",
          any(f["item"] == "C06" and f["severity"] == "FAIL" and "20.00" in f["message"]
              for f in fs))
    check("字段缺失带镜级证据 (C04 FAIL 证据=镜2·AIGC提示词)",
          any(f["item"] == "C04" and f.get("shot") == "镜2" and f.get("field") == "AIGC提示词"
              for f in fs))
    check("相邻手法连用被抓 (C11 WARN, 镜1-镜2)",
          any(f["item"] == "C11" and f["severity"] == "WARN" and "镜1-镜2" in (f.get("shot") or "")
              for f in fs))
    check("空洞词被抓 (C13)", r["item_status"]["C13"] in ("warn", "fail"))
    check("元语言占位词被抓 (C12, 待补充)", r["item_status"]["C12"] == "warn")
    check("报告文本含编号行/无法验证段/结论行/检查点行",
          all(k in r["report"] for k in ("R-001", "结论:", "检查点:", "13 项清单核对")))
    check("报告结论=不通过 (存在 FAIL)", "不通过" in r["report"])
finally:
    shutil.rmtree(tmp2, ignore_errors=True)

# ------------------------------------------------------------------ 4. 断点续跑
print("\n4. CheckpointStore 断点续跑 (真实落盘, 清内存重入)")
print("=" * 66)
tmp3 = tempfile.mkdtemp(prefix="dm_review_t3_")
try:
    s_a = mk_store(tmp3)   # 实例 A (第一次运行后丢弃 — 模拟进程中断)
    r1 = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL, checkpoint_store=s_a)
    check("首跑三阶段全部现算",
          all(v["status"] == "computed" for v in r1["stages"].values()))
    check("检查点清单已落盘 (3 步, artifact_ref 在场)",
          len(mk_store(tmp3).steps(PIPELINE_ID)) == 3 and
          all(v.get("artifact_ref") for v in mk_store(tmp3).steps(PIPELINE_ID).values()),
          f"steps={list(mk_store(tmp3).steps(PIPELINE_ID))}")
    check("阶段产物文件真实写盘",
          all(os.path.isfile(os.path.join(tmp3, v["artifact_ref"]))
              for v in mk_store(tmp3).steps(PIPELINE_ID).values()))

    # 清内存重入: 全新 store 实例 + 全新调用 (无任何内存状态)
    s_b = mk_store(tmp3)
    r2 = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL, checkpoint_store=s_b)
    check("重入: 已完成阶段全部 skipped (done()=True 跳过)",
          all(v["status"] == "skipped" for v in r2["stages"].values()))
    check("重入: 各阶段发现数与首跑一致",
          all(r2["stages"][k]["findings"] == r1["stages"][k]["findings"] for k in r1["stages"]))
    check("重入: 发现清单逐条一致 (id/severity/item/message)",
          [(f["id"], f["severity"], f["item"], f["message"]) for f in r1["findings"]] ==
          [(f["id"], f["severity"], f["item"], f["message"]) for f in r2["findings"]])

    # 输入变更 → 该步失效重算
    r3 = review_artifacts(GOOD_TEXT.replace("16.0", "17.0"), brief=BRIEF,
                          mode=MODE_FULL, checkpoint_store=mk_store(tmp3))
    check("输入变更: 全部阶段失效重算 (hash 变更自动失效)",
          all(v["status"] == "computed" for v in r3["stages"].values()))

    # 跨模式复用: 快速审查只算 completeness; 随后全量审查应复用 completeness
    tmp4 = tempfile.mkdtemp(prefix="dm_review_t4_")
    try:
        rq = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_QUICK,
                              checkpoint_store=mk_store(tmp4))
        check("快速审查: 只跑 completeness 阶段",
              list(rq["stages"]) == ["completeness"] and rq["stages"]["completeness"]["status"] == "computed")
        rf = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL,
                              checkpoint_store=mk_store(tmp4))
        check("跨模式复用: 全量审查 completeness skipped, 其余现算",
              rf["stages"]["completeness"]["status"] == "skipped" and
              rf["stages"]["consistency"]["status"] == "computed" and
              rf["stages"]["coverage"]["status"] == "computed")
        n_cleared = mk_store(tmp4).clear(PIPELINE_ID)
        check("clear 清空检查点后全重算", n_cleared == 3 and
              all(v["status"] == "computed" for v in review_artifacts(
                  GOOD_TEXT, brief=BRIEF, mode=MODE_FULL,
                  checkpoint_store=mk_store(tmp4))["stages"].values()),
              f"cleared={n_cleared}")
    finally:
        shutil.rmtree(tmp4, ignore_errors=True)
finally:
    shutil.rmtree(tmp3, ignore_errors=True)

# ------------------------------------------------------------------ 5. LLM 语义轨 (f2 式本地服务器)
print("\n5. LLM 语义轨 (本地 OpenAI 兼容服务器, 真实 HTTP)")
print("=" * 66)
from http.server import BaseHTTPRequestHandler, HTTPServer

LLM_STATE = {"mode": "good", "requests": []}
LLM_GOOD = json.dumps({
    "findings": [
        {"item": "叙事连贯", "severity": "WARN", "shot": "镜2", "field": "AIGC提示词",
         "message": "镜2 的倒影意象与镜4 回头动作之间缺少过渡镜头"},
        {"item": "情绪传达", "severity": "INFO", "shot": None, "field": None,
         "message": "整体情绪基调与 brief 一致"},
    ], "cannot_verify": []}, ensure_ascii=False)


class LLMHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            body = {}
        msgs = body.get("messages") or []
        LLM_STATE["requests"].append({
            "model": body.get("model"),
            "system": (msgs[0] or {}).get("content", "") if msgs else "",
            "user": (msgs[-1] or {}).get("content", "") if len(msgs) > 1 else "",
        })
        if LLM_STATE["mode"] == "error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "review test server forced 500"}')
            return
        content = LLM_GOOD if LLM_STATE["mode"] == "good" else "这段输出不是 JSON。"
        resp = {"id": "chatcmpl-review-test", "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 100, "total_tokens": 110}}
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


server = HTTPServer(("127.0.0.1", 0), LLMHandler)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(0.2)
URL = f"http://127.0.0.1:{PORT}/v1/chat/completions"

tmp5 = tempfile.mkdtemp(prefix="dm_review_t5_")
try:
    # 5a. 合格 LLM 发现合并
    rl = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL,
                          api_url=URL, api_key="k", api_model="review-test-model",
                          checkpoint_store=mk_store(tmp5), checkpoint_enabled=False)
    check("LLM 语义轨完成 (llm.used=True, 真实 HTTP 往返)", rl["llm"]["used"] is True,
          f"note={rl['llm']['note']}")
    check("请求为干净上下文 (system 钉审查员身份, 不携带生成历史)",
          "独立产物审查员" in LLM_STATE["requests"][-1]["system"] and
          "你没有参与该产物的生成" in LLM_STATE["requests"][-1]["system"])
    check("user 携带产物与结构检查发现防重复段",
          "雨夜便利店" in LLM_STATE["requests"][-1]["user"] and
          "勿重复" in LLM_STATE["requests"][-1]["user"])
    llm_fs = findings_of(rl, source="llm")
    check("LLM 发现合并进报告 (source=llm, 2 条)", len(llm_fs) == 2)
    check("LLM 发现 severity 白名单归一 (INFO 保留)",
          any(f["severity"] == "INFO" and f["item"] == "情绪传达" for f in llm_fs))
    det_n = len(findings_of(rl, source="deterministic"))
    check("LLM 发现 R 编号接在确定性发现之后",
          all(int(f["id"].split("-")[1]) > det_n for f in llm_fs),
          f"llm_ids={[f['id'] for f in llm_fs]} det_n={det_n}")
    check("审查轨标注为 确定性+LLM 双轨", rl["track"] == "确定性轨 + LLM 语义轨")

    # 5b. 服务器 500 → 诚实落回确定性轨
    LLM_STATE["mode"] = "error"
    re5 = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL,
                           api_url=URL, api_key="k", api_model="m",
                           checkpoint_store=mk_store(tmp5), checkpoint_enabled=False)
    check("服务器 500: LLM 轨诚实失败 (used=False, 有 error)",
          re5["llm"]["used"] is False and bool(re5["llm"]["error"]))
    check("500 后审查仍完成且发现全部来自确定性轨",
          re5["summary"]["findings_total"] > 0 and
          all(f["source"] == "deterministic" for f in re5["findings"]))
    check("失败原因写入审查轨标注", "无 LLM 语义审查" in re5["track"])

    # 5c. 不可解析输出 → 丢弃不上报
    LLM_STATE["mode"] = "badjson"
    rj = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_FULL,
                          api_url=URL, api_key="k", api_model="m",
                          checkpoint_store=mk_store(tmp5), checkpoint_enabled=False)
    check("不可解析 LLM 输出被诚实丢弃 (不进发现, error 注明不可解析)",
          rj["llm"]["used"] is False and "不可解析" in (rj["llm"]["error"] or "") and
          all(f["source"] == "deterministic" for f in rj["findings"]))

    # 5d. 端点缺席 → 快速/对比模式不发起 LLM
    LLM_STATE["mode"] = "good"
    rn = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_QUICK,
                          api_url=URL, checkpoint_enabled=False)
    check("非全量审查模式不消费 LLM (快速模式带端点也无 LLM 调用)",
          rn["llm"]["used"] is False and len(findings_of(rn, source="llm")) == 0)
finally:
    server.shutdown()
    shutil.rmtree(tmp5, ignore_errors=True)

# ------------------------------------------------------------------ 6. 无法验证路径
print("\n6. 无法验证路径 (缺输入不猜测)")
print("=" * 66)
tmp6 = tempfile.mkdtemp(prefix="dm_review_t6_")
try:
    r = review_artifacts(GOOD_TEXT, brief=None, mode=MODE_FULL,
                         checkpoint_store=mk_store(tmp6), checkpoint_enabled=False)
    cv_items = {c["item"] for c in r["cannot_verify"]}
    check("无 brief: C09/C10 进无法验证", {"C09", "C10"} <= cv_items, f"cv={sorted(cv_items)}")
    check("无法验证条目带原因说明 (缺输入不猜测)",
          all(c.get("reason") for c in r["cannot_verify"]))
    check("报告含『无法验证』段且计数一致",
          ("无法验证 (%d 项" % len(r["cannot_verify"])) in r["report"])

    rt = review_artifacts(_TEXT_ARTIFACT, brief=BRIEF, mode=MODE_FULL,
                          checkpoint_store=mk_store(tmp6), checkpoint_enabled=False)
    tv_items = {c["item"] for c in rt["cannot_verify"]}
    check("纯文本产物: 结构项 (C02-C08/C11) 显式无法验证",
          {"C02", "C03", "C04", "C05", "C06", "C07", "C08", "C11"} <= tv_items,
          f"cv={sorted(tv_items)}")
    check("纯文本产物: C12/C13 仍在纯文本上真实扫描 (非无法验证)",
          "C12" not in tv_items and "C13" not in tv_items)

    rc = review_artifacts(GOOD_TEXT, brief=BRIEF, mode=MODE_COMPARE,
                          checkpoint_store=mk_store(tmp6), checkpoint_enabled=False)
    check("对比分镜缺基准: X01 无法验证且报告注明缺输入",
          any(c["item"] == "X01" and "未提供对比基准" in c["reason"] for c in rc["cannot_verify"]))
    check("对比分镜缺基准: 结论不伪造对比通过",
          all(f["item"] not in ("X01", "X02", "X03") or f["severity"] != "INFO"
              for f in findings_of(rc)))
finally:
    shutil.rmtree(tmp6, ignore_errors=True)

# ------------------------------------------------------------------ 7. 判例库
print("\n7. 判例库消费与缺位降级")
print("=" * 66)
tmp7 = tempfile.mkdtemp(prefix="dm_review_t7_")
try:
    rp = review_artifacts(BAD_TEXT, brief=BRIEF, mode=MODE_FULL,
                          checkpoint_store=mk_store(tmp7), checkpoint_enabled=False)
    check("判例库在场: 报告自检段标注就绪", rp["precedents"]["ready"] is True
          and "判例库 %d 条就绪" % rp["precedents"]["count"] in rp["report"],
          f"count={rp['precedents']['count']}")
    check("判例引用格式 R-xxx ↔ NP-yyy (真实消费 rule/self_check)",
          all(("↔ NP-" in c) for c in rp["precedents"]["cited"]) and
          ("自检问题清单" in rp["report"]))

    # 缺位降级: sys.modules 注入 None → import 失败 → 诚实标注不崩
    saved = sys.modules.pop("knowledge_base.quality_precedents", None)
    sys.modules["knowledge_base.quality_precedents"] = None
    try:
        rq7 = review_artifacts(BAD_TEXT, brief=BRIEF, mode=MODE_FULL,
                               checkpoint_store=mk_store(tmp7), checkpoint_enabled=False)
    finally:
        del sys.modules["knowledge_base.quality_precedents"]
        if saved is not None:
            sys.modules["knowledge_base.quality_precedents"] = saved
    check("判例库缺位: 引擎不崩且 precedents.ready=False",
          rq7["precedents"]["ready"] is False)
    check("判例库缺位: 报告诚实标注未就绪并跳过, 不编造 NP 引用",
          "判例库未就绪" in rq7["report"] and rq7["precedents"]["cited"] == [])
finally:
    shutil.rmtree(tmp7, ignore_errors=True)

# ------------------------------------------------------------------ 8. 对抗输入 + 节点级
print("\n8. 对抗输入与节点级行为")
print("=" * 66)
tmp8 = tempfile.mkdtemp(prefix="dm_review_t8_")
try:
    r8 = review_artifacts('{"分镜表": "不是数组", "分镜数": "x", "总时长秒": null}',
                          brief={"_场景描述": ""}, mode=MODE_FULL,
                          checkpoint_store=mk_store(tmp8), checkpoint_enabled=False)
    check("畸形分镜 JSON 不崩: 结构坏块被抓 (分镜表非数组)", r8["ok"] is False or
          any(f["item"] == "C02" for f in r8["findings"]))
    check("brief 场景为空: C09 无法验证而非误报 0% 锚定",
          any(c["item"] == "C09" for c in r8["cannot_verify"]))

    try:
        review_artifacts(GOOD_TEXT, mode="不存在的模式")
        check("非法 mode 抛 ValueError (诚实 API 契约)", False, "未抛")
    except ValueError:
        check("非法 mode 抛 ValueError (诚实 API 契约)", True)

    node = DirectorMasterReview()
    rep, meta = node.review_build(被审产物=GOOD_TEXT, 审查模式="全量审查",
                                  核心数据包=json.dumps(BRIEF, ensure_ascii=False))
    m = json.loads(meta)
    check("节点 review_build: 报告非空 + JSON 可解析", bool(rep.strip()) and m["ok"] is True)
    check("节点 review_build: 模式与 brief 正确传递", m["mode"] == "全量审查")

    rep2, meta2 = node.review_build(被审产物=BAD_TEXT, 审查模式="对比分镜",
                                    分镜JSON="{broken json!!")
    m2 = json.loads(meta2)
    check("节点坏基准不崩: 对比基准不可解析进无法验证",
          any(c["item"] == "X01" and "不可解析" in c["reason"] for c in m2["cannot_verify"]))

    rep3, meta3 = node.review_build(被审产物="", 审查模式="未知模式值")
    m3 = json.loads(meta3)
    check("节点未知模式值防御性落回首项 (不崩)", m3["mode"] == "快速结构审查" and
          "空输入" in m3["artifact_kind_text"])
    check("节点输出报告含编号发现 (空输入也诚实报 FAIL)", "R-001" in rep3)
finally:
    shutil.rmtree(tmp8, ignore_errors=True)

# ------------------------------------------------------------------ 汇总
doc = {"suite": "test_review_node", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
       "pass": PASS, "fail": FAIL, "results": RESULTS}
with open(os.path.join(HERE, "review_node_results.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 66)
print(f"独立审查引擎测试结果: {PASS} PASS / {FAIL} FAIL "
      f"(证据: tests/review_node_results.json)")
print("=" * 66)
sys.exit(1 if FAIL else 0)
