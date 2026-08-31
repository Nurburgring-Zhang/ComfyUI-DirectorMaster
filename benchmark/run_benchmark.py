# -*- coding: utf-8 -*-
"""
benchmark/run_benchmark.py — 固定任务 × 固定模型 × 逐请求记录 的基准 runner
============================================================================
方法论见 benchmark/README.md (三条硬规矩: 固定任务×固定模型 / 逐请求记录不估算 /
无真实端点诚实标注 MOCK)。仅 stdlib, Python >=3.8。

用法:
  真实端点: python benchmark/run_benchmark.py --endpoint https://host/v1/chat/completions \
                --model your-model --api-key-env MY_API_KEY --repeats 3
  本地验证: python benchmark/run_benchmark.py --mock --repeats 2
  错误通路: python benchmark/run_benchmark.py --mock --mock-mode error

退出码: 0 全部请求请求级成功 / 1 任一请求级失败 / 2 参数或环境错误。
usage tokens 从端点响应 usage 字段原样拉取; 缺失留空 (usage_present=False), 永不估算;
runner 不计算金额 (无价目表, 算钱即估算)。
"""
import os
import sys
import json
import time
import argparse
import threading
import urllib.request
import urllib.error
import statistics
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.stdout.reconfigure(encoding="utf-8")
BENCH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BENCH_DIR)

CSV_COLUMNS = ["run_id", "ts_utc", "mode", "task_id", "model", "request_no",
               "latency_ms", "http_status", "ok", "error",
               "prompt_tokens", "completion_tokens", "total_tokens", "usage_present",
               "content_chars", "checks_passed", "checks_total", "checks_detail",
               "content_head"]

# ----------------------------------------------------------------
# 内嵌 mock 服务器 (f2 式: tests/f2_ai_track_e2e.py 同款 http.server 模式) —
# 仅验证 runner 通路 (传输/解析/结构检查/CSV), 输出全部诚实标注 MOCK。
# ----------------------------------------------------------------
_MOCK_STATE = {"mode": "good", "requests": []}

_MOCK_MECHA = json.dumps({
    "分镜表": [
        {"镜号": 1, "景别": "大远景", "运镜": "固定", "焦段": "16mm", "时长": "2.5s",
         "画面焦点": "暴雨中的码头, 机甲战士的轮廓立在集装箱之间, 雨水顺着装甲往下淌"},
        {"镜号": 2, "景别": "全景", "运镜": "推", "焦段": "28mm", "时长": "2.0s",
         "画面焦点": "机甲抬臂, 能量护盾在掌心亮起一圈青白光弧, 雨点在光弧上炸开"},
        {"镜号": 3, "景别": "特写", "运镜": "手持", "焦段": "100mm", "时长": "1.5s",
         "画面焦点": "指节因用力在装甲接缝处发白, 护盾光把雨丝照成一条条亮线"},
        {"镜号": 4, "景别": "中景", "运镜": "环绕", "焦段": "35mm", "时长": "3.0s",
         "画面焦点": "护盾完全展开, 水幕从弧面滑落, 机甲在雨幕里站定"},
        {"镜号": 5, "景别": "远景", "运镜": "升降", "焦段": "24mm", "时长": "2.5s",
         "画面焦点": "镜头升高, 码头的灯一盏盏亮起, 护盾的青光是画面里唯一的光源"},
        {"镜号": 6, "景别": "近景", "运镜": "固定", "焦段": "85mm", "时长": "2.0s",
         "画面焦点": "机甲收盾, 肩甲上的雨水积成一线滴落, 呼吸声压过雨声"},
    ],
    "总时长秒": 13.5,
    "声音": "同期声: 暴雨砸击声、缆绳吱呀、能量低频嗡鸣 (不需要配乐)",
}, ensure_ascii=False)

_MOCK_AD = json.dumps({
    "分镜表": [
        {"镜号": 1, "景别": "特写", "运镜": "固定", "时长": "3.0s",
         "画面焦点": "哑光黑智能手表静置在系鞋带的长椅上, 表壳凝着晨跑后的水汽",
         "声音": "同期声: 跑鞋落地声由远及近、呼吸声"},
        {"镜号": 2, "景别": "近景", "运镜": "手持", "时长": "4.0s",
         "画面焦点": "跑步者抬腕看表, 拇指擦过表盘, 汗珠从手腕滑到表带",
         "声音": "同期声: 表冠旋钮的咔哒声、呼吸声"},
        {"镜号": 3, "景别": "中景", "运镜": "跟拍", "时长": "8.0s",
         "画面焦点": "长跑进入坡道, 步频变密, 手臂摆动带出手表的侧影",
         "声音": "同期声: 跑鞋落地声变密、风声"},
        {"镜号": 4, "景别": "特写", "运镜": "推", "时长": "3.0s",
         "画面焦点": "表冠被旋动一格, 哑光表壳上指纹留下又消失",
         "声音": "同期声: 表冠旋钮的咔哒声"},
        {"镜号": 5, "景别": "全景", "运镜": "环绕", "时长": "6.0s",
         "画面焦点": "跑步者在桥上放慢成步行, 双手撑膝, 抬腕看表上的心率弧线",
         "声音": "同期声: 桥下车流低噪、呼吸渐缓"},
        {"镜号": 6, "景别": "中景", "运镜": "固定", "时长": "5.0s",
         "画面焦点": "跑步者坐上桥栏背光处, 解开表带搭在膝上, 表盘朝向镜头之外",
         "声音": "同期声: 表带扣的轻响、远处的鸟叫"},
    ],
    "总时长秒": 29.0,
}, ensure_ascii=False)

_MOCK_SCREENPLAY = (
    "《凤梨》\n\n"
    "第一场 内景 老式居民楼厨房 夜 雨\n\n"
    "雨点敲在铁窗框上, 1998 年哈尔滨的夜混着煤烟味。父亲站在灶台前切菜, 刀与砧板的间隔越来越慢。"
    "女儿坐在桌边, 手指绕着一只凤梨罐头的标签, 标签起了泡, 过期十五年的黄印像一枚旧邮票。"
    "墙上的挂钟走针声比雨声还清楚。桌角压着一封信, 信纸泛黄, 折痕处裂开了。\n\n"
    "父亲(不抬头): 饿了吧。\n\n"
    "女儿: 不饿。\n\n"
    "沉默。收音机里放着老歌, 信号时好时坏, 父亲伸手把音量拧小半格。他把切好的菜拨进碗里, "
    "动作停了一下——他看见那封信, 没碰它, 只是把碗往女儿那边推了推。\n\n"
    "第二场 内景 老式居民楼厨房 夜 雨渐小\n\n"
    "女儿夹起一块凤梨, 放进父亲碗里。父亲的筷子停在半空, 半秒钟, 然后继续。"
    "窗外的霓虹在积水里倒映, 红的绿的, 像打翻的调色盘。水壶在炉子上响, 谁都没有去提。"
    "女儿把罐头拉到自己面前, 用起子撬开, 铁皮盖弹起的声音在安静的厨房里格外响。"
    "她叉起一块凤梨, 又放回罐头里。\n\n"
    "女儿: 爸, 它过期了。\n\n"
    "父亲(看着锅): 我知道。\n\n"
    "女儿: 那为什么还留着。\n\n"
    "父亲把火关了, 锅里的余温把最后一点水汽顶出来。他拿起那封信, 在桌角磕了磕, 磕平了卷起的角, "
    "又放回原处。雨停了, 屋檐还在滴水, 一滴, 一滴, 打在窗台的搪瓷盆里。\n\n"
    "女儿(起身, 收碗): 明天我把它扔了。\n\n"
    "父亲: 先放着吧。\n\n"
    "灯关了。黑暗里, 罐头和信在桌上留成一个轮廓。信最终有没有被打开, 罐头有没有被扔掉, "
    "都没有答案。留白交给观众。"
)


class _MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            body = {}
        _MOCK_STATE["requests"].append({"path": self.path, "model": body.get("model")})
        if _MOCK_STATE["mode"] == "error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "benchmark mock forced 500"}')
            return
        probe = json.dumps(body, ensure_ascii=False)
        if "机甲" in probe:
            content = _MOCK_MECHA
        elif "手表" in probe:
            content = _MOCK_AD
        else:
            content = _MOCK_SCREENPLAY
        usage = {"prompt_tokens": 128, "completion_tokens": max(1, len(content) // 3),
                 "total_tokens": 128 + max(1, len(content) // 3)}
        resp = {"id": "chatcmpl-bench-mock", "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                             "finish_reason": "stop"}],
                "usage": usage}
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


# ----------------------------------------------------------------
# HTTP 与解析
# ----------------------------------------------------------------

def _post_chat(endpoint, api_key, payload, timeout_s):
    """单次 chat/completions 请求。返回 (status:int, body:dict, err:str)。"""
    if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
        return 0, None, "endpoint 必须是 http(s) URL"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer %s" % api_key
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.getcode(), json.loads(raw), ""
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8", "replace")
        except Exception:
            raw = ""
        return int(e.code), None, "HTTP %s: %s" % (e.code, raw[:160])
    except Exception as e:  # 网络层失败: 请求级记 False, 不终止批次
        return 0, None, "%s: %s" % (type(e).__name__, e)


def _loads_json_loose(content):
    """宽容 JSON 提取 (剥代码围栏 / 首尾大括号截取)。返回 (data|None)。"""
    s = str(content or "").strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:]
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    i, j = s.find("{"), s.rfind("}")
    if 0 <= i < j:
        try:
            return json.loads(s[i:j + 1])
        except Exception:
            return None
    return None


def check_expected(content, expected):
    """期望结构检查 → (passed, total, detail_str)。只统计不抛; 判不了的不写。"""
    checks = []  # (label, ok)
    fmt = str((expected or {}).get("格式", "text")).lower()
    data = None
    if fmt == "json":
        data = _loads_json_loose(content)
        checks.append(("json可解析", data is not None))
    for k in (expected or {}).get("必含键", []) or []:
        checks.append(("必含键:%s" % k, isinstance(data, dict) and k in data))
    list_key = (expected or {}).get("列表键", "分镜表")
    items = data.get(list_key) if isinstance(data, dict) else None
    items = items if isinstance(items, list) else []
    for k in (expected or {}).get("每镜必含键", []) or []:
        checks.append(("每镜必含:%s" % k, bool(items) and all(
            isinstance(it, dict) and k in it for it in items)))
    min_shots = (expected or {}).get("最少镜数", 0) or 0
    if min_shots:
        checks.append(("最少镜数:%d" % min_shots, len(items) >= min_shots))
    min_chars = (expected or {}).get("最少字数", 0) or 0
    if min_chars:
        checks.append(("最少字数:%d" % min_chars, len(str(content or "")) >= min_chars))
    text_low = str(content or "").lower()
    for mk in (expected or {}).get("必含标记", []) or []:
        checks.append(("必含标记:%s" % mk, str(mk) in str(content or "")))
    for w in (expected or {}).get("禁含词", []) or []:
        checks.append(("禁含词:%s" % w, str(w).lower() not in text_low))
    passed = sum(1 for _, ok in checks if ok)
    detail = "; ".join("%s=%s" % (name, "P" if ok else "F") for name, ok in checks)
    return passed, len(checks), detail


# ----------------------------------------------------------------
# 运行编排
# ----------------------------------------------------------------

def _load_tasks(tasks_dir):
    out = []
    if not os.path.isdir(tasks_dir):
        return out
    for name in sorted(os.listdir(tasks_dir)):
        if not name.lower().endswith(".json"):
            continue
        try:
            with open(os.path.join(tasks_dir, name), "r", encoding="utf-8") as f:
                t = json.load(f)
            if isinstance(t, dict) and t.get("id") and t.get("messages"):
                out.append(t)
        except Exception as e:
            print("[benchmark] 任务文件损坏, 跳过 %s: %s: %s" % (name, type(e).__name__, e))
    return out


def main():
    ap = argparse.ArgumentParser(description="DirectorMaster benchmark runner (stdlib only)")
    ap.add_argument("--endpoint", default=os.environ.get("DM_BENCH_ENDPOINT", ""))
    ap.add_argument("--model", default="")
    ap.add_argument("--api-key-env", default="DM_BENCH_API_KEY",
                    help="存放密钥的环境变量名 (密钥本身不进命令行/CSV)")
    ap.add_argument("--tasks", default=os.path.join(BENCH_DIR, "tasks"))
    ap.add_argument("--out", default=os.path.join(BENCH_DIR, "results"))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--tag", default="")
    ap.add_argument("--mock", action="store_true", help="f2 式内嵌服务器, 验证 runner 通路 (输出标 MOCK)")
    ap.add_argument("--mock-mode", default="good", choices=["good", "error"])
    args = ap.parse_args()

    if args.repeats < 1:
        print("[benchmark] --repeats 必须 >=1")
        return 2
    mode = "MOCK" if args.mock else "REAL"
    if not args.mock:
        if not args.endpoint:
            print("[benchmark] 缺 --endpoint (或环境变量 DM_BENCH_ENDPOINT)。"
                  "无真实端点时请用 --mock 做本地通路验证, runner 不会假装跑过真实端点。")
            return 2
        if not args.model:
            print("[benchmark] 缺 --model (固定模型口径要求显式指定)。")
            return 2
    api_key = ""
    if not args.mock and args.api_key_env:
        api_key = os.environ.get(args.api_key_env, "")
        if not api_key:
            print("[benchmark] 环境变量 %s 未设置 (密钥不落盘, runner 拒绝无认证猜测)。"
                  "若端点允许匿名, 显式传 --api-key-env 置空名。" % args.api_key_env)
            return 2

    tasks = _load_tasks(args.tasks)
    if not tasks:
        print("[benchmark] 任务集为空: %s" % args.tasks)
        return 2

    server = None
    endpoint = args.endpoint
    if args.mock:
        _MOCK_STATE["mode"] = args.mock_mode
        server = HTTPServer(("127.0.0.1", 0), _MockHandler)
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        endpoint = "http://127.0.0.1:%d/v1/chat/completions" % port
        time.sleep(0.2)
        if not args.model:
            args.model = "mock-model"
        print("[benchmark] MOCK 服务器: %s (mode=%s)" % (endpoint, args.mock_mode))

    run_id = datetime.now(timezone.utc).strftime("b%Y%m%d%H%M%S")
    os.makedirs(args.out, exist_ok=True)
    safe_tag = "".join(c for c in (args.tag or args.model) if c.isalnum() or c in "-_")[:40] or "run"
    csv_path = os.path.join(args.out, "bench_%s_%s.csv" % (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), safe_tag))

    rows = []
    request_no = {}
    for task in tasks:
        payload = {"model": args.model, "messages": task["messages"]}
        payload.update(task.get("参数") or {})
        for rep in range(1, args.repeats + 1):
            request_no[task["id"]] = request_no.get(task["id"], 0) + 1
            t0 = time.time()
            status, body, err = _post_chat(endpoint, api_key, payload, args.timeout)
            latency_ms = int(round((time.time() - t0) * 1000))
            content = ""
            usage = {}
            if isinstance(body, dict):
                try:
                    content = body["choices"][0]["message"]["content"]
                except Exception:
                    content = ""
                u = body.get("usage")
                usage = u if isinstance(u, dict) else {}
            ok = bool(body) and not err and content != ""
            p_tok = usage.get("prompt_tokens", "")
            c_tok = usage.get("completion_tokens", "")
            t_tok = usage.get("total_tokens", "")
            if ok:
                passed, total, detail = check_expected(content, task.get("期望结构") or {})
            else:
                passed, total, detail = 0, 0, ""
            rows.append({
                "run_id": run_id, "ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "mode": mode, "task_id": task["id"], "model": args.model,
                "request_no": request_no[task["id"]],
                "latency_ms": latency_ms, "http_status": status,
                "ok": "1" if ok else "0", "error": (err or "").replace("\n", " ")[:200],
                "prompt_tokens": p_tok if p_tok != "" else "",
                "completion_tokens": c_tok if c_tok != "" else "",
                "total_tokens": t_tok if t_tok != "" else "",
                "usage_present": "1" if usage else "0",
                "content_chars": len(str(content)) if ok else 0,
                "checks_passed": passed, "checks_total": total,
                "checks_detail": detail, "content_head": str(content)[:64].replace("\n", " "),
            })
            print("  [%s] %s #%d %sms http=%s ok=%s checks=%d/%d%s"
                  % (mode, task["id"], request_no[task["id"]], latency_ms, status,
                     "1" if ok else "0", passed, total,
                     (" err=" + err[:80]) if err else ""))

    if server is not None:
        server.shutdown()

    # CSV 落盘 (逐请求一行, 列固定; 数值列原样写入, token 缺失留空=端点未返回, 不估算)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.write(",".join('"%s"' % c for c in CSV_COLUMNS) + "\n")
        for r in rows:
            f.write(",".join('"%s"' % str(r[c]).replace('"', '""') for c in CSV_COLUMNS) + "\n")

    # 摘要
    n_ok = sum(1 for r in rows if r["ok"] == "1")
    lat = [r["latency_ms"] for r in rows if r["ok"] == "1"]
    tok = [int(r["total_tokens"]) for r in rows if r.get("total_tokens") not in ("", None)]
    checks_p = sum(r["checks_passed"] for r in rows)
    checks_t = sum(r["checks_total"] for r in rows)
    print("\n" + "=" * 60)
    if mode == "MOCK":
        print("运行模式: MOCK (本地内嵌服务器 — 计量数字非真实端点账单, 仅验证 runner 通路)")
    else:
        print("运行模式: REAL (端点 %s)" % endpoint)
    print("任务 %d 个 × %d 次 = %d 请求, 请求级成功 %d/%d" % (len(tasks), args.repeats, len(rows), n_ok, len(rows)))
    if lat:
        print("延迟: p50=%dms 均值=%dms 最大=%dms" % (statistics.median(lat), statistics.mean(lat), max(lat)))
    if tok:
        print("usage total_tokens 合计: %d (取自端点 usage 字段, 未估算; 缺 usage 的请求留空)" % sum(tok))
    else:
        print("usage: 端点未返回 usage 字段 — 记账列全部留空 (usage_present=0), runner 未做任何估算")
    print("期望结构检查: %d/%d 项通过" % (checks_p, checks_t))
    print("CSV: %s (%d 行, mode 列=%s)" % (csv_path, len(rows), mode))
    print("=" * 60)
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
