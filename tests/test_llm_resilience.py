# -*- coding: utf-8 -*-
"""
V16.2.0 批次1 — LLM 链路健壮性故障注入测试 (真实 HTTP + 确定性状态机)
====================================================================
本地真实 HTTP 服务器 (f2_ai_track_e2e.py 同构模式) 脚本化故障模式,
pln_llm._clock / pln_llm._sleep 测试缝隙注入实现确定性状态机验证, 零外网。

V16.7.0 批次3 增补 (D1): T17 — detect_echo 回声照抄检测 + freeze_system 经济性冻结模式。

测试矩阵:
  T1  成功路径双形态 (choices / response) + call_ai 向后兼容 2 元组
  T2  429→503→200 指数退避重试 (真实 HTTP, 睡眠时长范围断言)
  T3  同端点模型降级 (显式降级链, 请求序列 A,A,B + 路由失败计数)
  T4  跨端点降级 (用户预设文件 + key_env 环境变量密钥解析 + port 感知匹配)
  T5  冷却后探测恢复 (3 次失败→fallback_active→61s→探测成功→primary_ok)
  T6  探测失败回落 (探测单次尝试→回落备用级→冷却重置→冷却内不再探测)
  T7  溢出两层压缩 (gentle 25% → aggressive 12.5%, 请求体递减 + 短文本诚实失败)
  T7b OVERFLOW 压缩耗尽后跨级 (备用级服务 + OVERFLOW 计入阈值)
  T8  上游截断 (finish_reason=length ×3 诚实报错 / 截断后恢复 / PROTOCOL / json_broken)
  T8f 终端类错误 (TRUNCATION/AUTH) 不计降级阈值、不跨级
  T8g 200 围栏 JSON 宽容解析抢救 (零拆分重试)
  T9  字段别名四级容错解析 (resolve_json_field, 含规范名大写查表)
  T10 宽容 JSON 解析 (json_loads_tolerant 围栏/尾逗号/噪声/失手诚实 None)
  T11 压缩确定性与保真 (头尾子串逐字校验 + 标记 + 短文本 None)
  T13 用户预设文件 (合法覆盖 / 坏 JSON / 坏结构 / 不存在)
  T14 SSRF 降级链级不回退 (169.254.x 链级跳过 + 事件留痕 + 规范化黑名单
      含 IPv4-mapped 与已废弃 IPv4 兼容 IPv6 形态)
  T15 状态机并发冒烟 (4 线程交叉读写无撕裂, 事件缓冲有界)
  T16 错误分类器语义 (状态码优先于溢出短语 / 30x 终端归类)
  T17 批次3 D1: detect_echo 回声检测 (命中/不命中/长度短路/阈值边界)
      + freeze_system 经济性冻结 (system 跨重试+跨调用逐字节一致 /
        动态信息外置 user 头 [RUN] 段且不在 system / 默认关闭行为零变化)

证据存档: tests/llm_resilience_results.json (随包发布)。
退出码: 0 = 全部通过, 1 = 有失败。
"""
import json
import os
import sys
import threading
import time as _time
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from http.server import BaseHTTPRequestHandler, HTTPServer

import pln_llm

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


def ok_body(content, finish="stop"):
    """OpenAI 兼容 200 响应体 (choices 形态)。"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                     "finish_reason": finish}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 7, "total_tokens": 10},
    }


class FakeLLMServer:
    """真实本地 HTTP 服务器。responder(info) -> (status, payload);
    payload 为 dict/list → JSON 序列化; str → 原样写出 (用于 200 非 JSON 测试)。
    handler 先 append 请求记录再调 responder, 故 responder 内 len(server.requests)
    包含当前这次请求 (当前请求序号 == len(server.requests))。"""

    def __init__(self):
        outer = self
        self.requests = []
        self.responder = lambda info: (200, ok_body("default"))

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length).decode("utf-8")
                try:
                    body = json.loads(raw)
                except Exception:
                    body = {}
                msgs = body.get("messages") or []
                info = {
                    "path": self.path,
                    "model": body.get("model"),
                    "system": msgs[0].get("content", "") if msgs else "",
                    "user": msgs[-1].get("content", "") if msgs else "",
                    "auth": self.headers.get("Authorization", ""),
                }
                outer.requests.append(info)
                status, payload = outer.responder(info)
                if isinstance(payload, (dict, list)):
                    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                else:
                    data = str(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.httpd.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}/v1/chat/completions"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def stop(self):
        try:
            self.httpd.shutdown()
        except Exception:
            pass


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


# ---- 测试缝隙注入: 确定性时钟 + 睡眠记录 (不引入任何第三方 mock 库) ----
ORIG_CLOCK = pln_llm._clock
ORIG_SLEEP = pln_llm._sleep
FAKE = FakeClock()
SLEEPS = []
pln_llm._clock = FAKE
pln_llm._sleep = lambda s: SLEEPS.append(s)

SERVERS = []


def new_server():
    s = FakeLLMServer()
    SERVERS.append(s)
    return s


def fresh():
    """每个测试前: 清睡眠记录 + 复位全部路由状态。"""
    SLEEPS.clear()
    pln_llm.reset_router_state()


try:
    # =================================================================
    print("T1 成功路径双形态 + call_ai 向后兼容")
    fresh()
    s1 = new_server()

    def t1_resp(info):
        if info["model"] == "m-choices":
            return 200, ok_body("pong-choices", finish="stop")
        return 200, {"response": "pong-response"}

    s1.responder = t1_resp
    text, err, meta = pln_llm.call_ai_ex(s1.url, "k", "m-choices", "sys", "ping", 0.1, 50, timeout=10)
    check("T1a choices 形态解析成功", text == "pong-choices" and err == "", f"err={err}")
    check("T1a finish_reason 透传", meta.get("finish_reason") == "stop", f"meta={meta.get('finish_reason')}")
    text2, err2, meta2 = pln_llm.call_ai_ex(s1.url, "k", "m-response", "sys", "ping", 0.1, 50, timeout=10)
    check("T1b response 形态解析成功", text2 == "pong-response" and err2 == "", f"err={err2}")
    r3, e3 = pln_llm.call_ai(s1.url, "k", "m-choices", "sys", "ping", 0.1, 50, timeout=10)
    check("T1c call_ai 7位置参数 2 元组兼容", r3 == "pong-choices" and e3 == "")

    # =================================================================
    print("T2 429→503→200 指数退避重试")
    fresh()
    s2 = new_server()

    def t2_resp(info):
        n = len(s2.requests)
        if n == 1:
            return 429, {"error": {"message": "rate limited"}}
        if n == 2:
            return 503, {"error": {"message": "service unavailable"}}
        return 200, ok_body("ok-after-retry")

    s2.responder = t2_resp
    text, err, meta = pln_llm.call_ai_ex(s2.url, "k", "m", "sys", "hello", 0.7, 100,
                                          timeout=10, max_retries_per_step=3)
    check("T2 三次请求后成功", text == "ok-after-retry" and err == "", f"err={err}")
    check("T2 请求数=3", len(s2.requests) == 3, f"n={len(s2.requests)}")
    check("T2 attempts 计 2 次非200", meta.get("attempts") == 2, f"attempts={meta.get('attempts')}")
    check("T2 两次退避睡眠且递增",
          len(SLEEPS) == 2 and 1.0 <= SLEEPS[0] < 2.0 and 2.0 <= SLEEPS[1] < 3.0,
          f"sleeps={SLEEPS}")

    # =================================================================
    print("T3 同端点模型降级 (显式降级链)")
    fresh()
    s3 = new_server()

    def t3_resp(info):
        if info["model"] == "modelA":
            return 500, {"error": {"message": "modelA boom"}}
        return 200, ok_body("served-by-B")

    s3.responder = t3_resp
    chain3 = [{"url": s3.url, "model": "modelA", "api_key": "k", "source": "primary"},
              {"url": s3.url, "model": "modelB", "api_key": "k", "source": "fallback_model"}]
    text, err, meta = pln_llm.call_ai_ex(s3.url, "k", "modelA", "sys", "hi", 0.5, 64, timeout=10,
                                         fallback_chain=chain3, max_retries_per_step=2)
    models_hit = [r["model"] for r in s3.requests]
    check("T3 请求序列 A,A,B", models_hit == ["modelA", "modelA", "modelB"], f"seq={models_hit}")
    check("T3 备用模型服务成功", text == "served-by-B" and err == "", f"err={err}")
    check("T3 fallback_used 且 meta 指向 B",
          meta.get("fallback_used") is True and meta.get("model") == "modelB",
          f"meta model={meta.get('model')}")
    st3 = pln_llm.get_router_status(s3.url)
    check("T3 主端点失败计数=1 (未达阈值不降级)",
          st3 is not None and st3["state"] == "primary_ok" and st3["consecutive_failures"] == 1,
          f"st={st3 and st3['state']}/{st3 and st3['consecutive_failures']}")

    # =================================================================
    print("T4 跨端点降级 (用户预设 + key_env + port 感知匹配)")
    fresh()
    s4a, s4b = new_server(), new_server()
    s4a.responder = lambda info: (500, {"error": {"message": "endpoint A down"}})
    s4b.responder = lambda info: (200, ok_body("served-by-endpoint-B"))

    tmpdir = tempfile.mkdtemp(prefix="dm_presets_")
    p_valid = os.path.join(tmpdir, "presets_valid.json")
    with open(p_valid, "w", encoding="utf-8") as f:
        json.dump({"presets": {"testprov": {
            "display": "TestProv",
            "match_hosts": [["127.0.0.1", s4a.port]],
            "key_env": "",
            "capabilities": {},
            "fallback_models": [],
            "lite_models": [],
            "fallback_endpoints": [{"url": s4b.url, "model": "m2", "key_env": "TEST_FB_KEY"}],
        }}}, f, ensure_ascii=False)

    merged4 = pln_llm.get_provider_presets(user_path=p_valid)
    pid4, preset4 = pln_llm.get_preset_for_url(s4a.url, presets=merged4)
    check("T4 port 感知预设匹配命中", pid4 == "testprov", f"pid={pid4}")
    pid4b, _ = pln_llm.get_preset_for_url(s4b.url, presets=merged4)
    check("T4 不同 port 不误匹配", pid4b is None, f"pid={pid4b}")

    os.environ["TEST_FB_KEY"] = "env-key-123"
    try:
        chain4 = pln_llm.build_fallback_chain(s4a.url, "main-key", "m1", presets=merged4)
        check("T4 降级链=主+跨端点", len(chain4) == 2 and chain4[1]["source"] == "fallback_endpoint",
              f"chain={[c['source'] for c in chain4]}")
        check("T4 key_env 环境变量密钥解析", chain4[1]["api_key"] == "env-key-123",
              f"key={chain4[1]['api_key']}")
        text, err, meta = pln_llm.call_ai_ex(s4a.url, "main-key", "m1", "sys", "hi", 0.5, 64,
                                             timeout=10, fallback_chain=chain4, max_retries_per_step=1)
        check("T4 跨端点降级成功", text == "served-by-endpoint-B" and meta.get("fallback_used") is True,
              f"err={err}")
        check("T4 备用端点收到 env 密钥",
              s4b.requests and s4b.requests[0]["auth"] == "Bearer env-key-123",
              f"auth={s4b.requests and s4b.requests[0]['auth']}")
    finally:
        del os.environ["TEST_FB_KEY"]

    chain4b = pln_llm.build_fallback_chain(s4a.url, "main-key", "m1", presets=merged4)
    check("T4 key_env 未设回退主密钥", chain4b[1]["api_key"] == "main-key",
          f"key={chain4b[1]['api_key']}")

    # =================================================================
    print("T5 冷却后探测恢复 (fallback_active → probing → primary_ok)")
    fresh()
    s5 = new_server()
    mode5 = {"a": "fail"}

    def t5_resp(info):
        if info["model"] == "A":
            if mode5["a"] == "fail":
                return 500, {"error": {"message": "A down"}}
            return 200, ok_body("primary-back")
        return 200, ok_body("fallback-b")

    s5.responder = t5_resp
    chain5 = [{"url": s5.url, "model": "A", "api_key": "k", "source": "primary"},
              {"url": s5.url, "model": "B", "api_key": "k", "source": "fallback_model"}]
    for i in range(pln_llm.FAILURE_THRESHOLD):
        t, e, m = pln_llm.call_ai_ex(s5.url, "k", "A", "sys", "x", 0.1, 16, timeout=10,
                                     fallback_chain=chain5, max_retries_per_step=1)
        assert t == "fallback-b" and not e, f"第{i+1}次调用应由备用级服务: err={e}"
    st5 = pln_llm.get_router_status(s5.url)
    check("T5 连续3次失败进入 fallback_active",
          st5 is not None and st5["state"] == "fallback_active", f"st={st5 and st5['state']}")

    FAKE.advance(pln_llm.FALLBACK_COOLDOWN_SECONDS + 1)
    mode5["a"] = "ok"
    base = len(s5.requests)
    t5_text, t5_err, t5_meta = pln_llm.call_ai_ex(s5.url, "k", "A", "sys", "x", 0.1, 16, timeout=10,
                                                  fallback_chain=chain5, max_retries_per_step=1)
    call4_models = [r["model"] for r in s5.requests[base:]]
    check("T5 冷却到期后探测主端点成功", t5_text == "primary-back" and t5_err == "", f"err={t5_err}")
    check("T5 探测仅 1 次请求直达主端点", call4_models == ["A"], f"seq={call4_models}")
    check("T5 recovered 标记", t5_meta.get("recovered") is True, f"meta={t5_meta}")
    st5b = pln_llm.get_router_status(s5.url)
    check("T5 状态恢复 primary_ok 且失败清零",
          st5b["state"] == "primary_ok" and st5b["consecutive_failures"] == 0,
          f"st={st5b['state']}/{st5b['consecutive_failures']}")
    ev5 = [e["event"] for e in st5b["events"]]
    check("T5 事件留痕 probing_start+probe_recovered",
          "probing_start" in ev5 and "probe_recovered" in ev5, f"events={ev5}")

    # =================================================================
    print("T6 探测失败回落 (单次探测→备用级→冷却重置)")
    fresh()
    s6 = new_server()
    s6.responder = lambda info: ((500, {"error": {"message": "A still down"}}) if info["model"] == "A"
                                 else (200, ok_body("fallback-b")))
    chain6 = [{"url": s6.url, "model": "A", "api_key": "k", "source": "primary"},
              {"url": s6.url, "model": "B", "api_key": "k", "source": "fallback_model"}]
    for _ in range(pln_llm.FAILURE_THRESHOLD):
        pln_llm.call_ai_ex(s6.url, "k", "A", "sys", "x", 0.1, 16, timeout=10,
                           fallback_chain=chain6, max_retries_per_step=1)
    FAKE.advance(pln_llm.FALLBACK_COOLDOWN_SECONDS + 1)
    base = len(s6.requests)
    t6_text, t6_err, t6_meta = pln_llm.call_ai_ex(s6.url, "k", "A", "sys", "x", 0.1, 16, timeout=10,
                                                  fallback_chain=chain6, max_retries_per_step=1)
    call_models = [r["model"] for r in s6.requests[base:]]
    check("T6 探测失败后回落备用级服务", t6_text == "fallback-b" and t6_meta.get("fallback_used") is True,
          f"err={t6_err}")
    check("T6 探测单次尝试即回落 (请求序列 A,B)", call_models == ["A", "B"], f"seq={call_models}")
    st6 = pln_llm.get_router_status(s6.url)
    ev6 = [e["event"] for e in st6["events"]]
    check("T6 探测失败回 fallback_active 且冷却重置",
          st6["state"] == "fallback_active" and "probe_failed" in ev6,
          f"st={st6['state']} events={ev6}")
    base = len(s6.requests)
    FAKE.advance(30)  # 冷却未到期
    pln_llm.call_ai_ex(s6.url, "k", "A", "sys", "x", 0.1, 16, timeout=10,
                       fallback_chain=chain6, max_retries_per_step=1)
    cooldown_models = [r["model"] for r in s6.requests[base:]]
    check("T6 冷却未到期不探测主端点 (直达备用级)", cooldown_models == ["B"], f"seq={cooldown_models}")

    # =================================================================
    print("T7 溢出两层压缩 (gentle → aggressive)")
    fresh()
    s7 = new_server()
    LONG_USER = ("父亲在厨房切菜, 女儿坐在桌边, 雨夜。" * 90)  # 1800 字符
    assert len(LONG_USER) == 1800

    def t7_resp(info):
        if len(s7.requests) <= 2:
            return 400, {"error": {"message": "maximum context length exceeded, please reduce"}}
        return 200, ok_body("compressed-ok")

    s7.responder = t7_resp
    text, err, meta = pln_llm.call_ai_ex(s7.url, "k", "m", "sys", LONG_USER, 0.5, 256, timeout=10)
    users = [r["user"] for r in s7.requests]
    check("T7 两次溢出压缩后第三次成功", text == "compressed-ok" and err == "", f"err={err}")
    check("T7 请求数=3 且无退避睡眠", len(users) == 3 and len(SLEEPS) == 0,
          f"n={len(users)} sleeps={len(SLEEPS)}")
    check("T7 meta compression=aggressive", meta.get("compression") == "aggressive",
          f"compression={meta.get('compression')}")
    check("T7 请求体严格递减 1800>918>468",
          len(users[0]) == 1800 and len(users[1]) == 918 and len(users[2]) == 468,
          f"lens={[len(u) for u in users]}")
    check("T7 压缩标记注入", pln_llm.COMPRESS_MARKER in users[1] and pln_llm.COMPRESS_MARKER in users[2])
    check("T7 gentle 头尾保真 (各 450 字符)",
          users[1].startswith(LONG_USER[:450] + "\n") and users[1].endswith("\n" + LONG_USER[-450:]))
    check("T7 aggressive 头尾保真 (各 225 字符)",
          users[2].startswith(LONG_USER[:225] + "\n") and users[2].endswith("\n" + LONG_USER[-225:]))

    fresh()
    s7b = new_server()
    s7b.responder = lambda info: (400, {"error": {"message": "maximum context length exceeded"}})
    text, err, meta = pln_llm.call_ai_ex(s7b.url, "k", "m", "sys", "短文本不可压", 0.5, 256, timeout=10)
    check("T7 短文本溢出诚实失败 (不伪造压缩)",
          text == "" and "已不可压缩" in err, f"err={err}")
    check("T7 短文本溢出仅 1 次请求", len(s7b.requests) == 1, f"n={len(s7b.requests)}")

    print("T7b OVERFLOW 压缩耗尽后跨级 (互审 M-3 补盲)")
    fresh()
    s7c = new_server()

    def t7b_resp(info):
        if info["model"] == "smallctx":
            return 400, {"error": {"message": "maximum context length exceeded"}}
        return 200, ok_body("bigctx-served")

    s7c.responder = t7b_resp
    chain7b = [{"url": s7c.url, "model": "smallctx", "api_key": "k", "source": "primary"},
               {"url": s7c.url, "model": "bigctx", "api_key": "k", "source": "fallback_model"}]
    text, err, meta = pln_llm.call_ai_ex(s7c.url, "k", "smallctx", "sys", LONG_USER, 0.5, 256,
                                         timeout=10, fallback_chain=chain7b, max_retries_per_step=3)
    models7b = [r["model"] for r in s7c.requests]
    check("T7b 压缩两层耗尽后跨级由备用级服务", text == "bigctx-served" and err == "", f"err={err}")
    check("T7b 请求序列 主级×3(原/轻/重) + 备用级×1",
          models7b == ["smallctx", "smallctx", "smallctx", "bigctx"], f"seq={models7b}")
    check("T7b levels_tried=2 且 fallback_used",
          meta.get("levels_tried") == 2 and meta.get("fallback_used") is True, f"meta={meta}")
    st7b = pln_llm.get_router_status(s7c.url)
    check("T7b OVERFLOW 计入降级阈值 (失败计数=1)",
          st7b is not None and st7b["consecutive_failures"] == 1, f"st={st7b}")

    # =================================================================
    print("T8 上游截断检测与拆分提示")
    fresh()
    s8a = new_server()
    s8a.responder = lambda info: (200, ok_body("半截输出……", finish="length"))
    text, err, meta = pln_llm.call_ai_ex(s8a.url, "k", "m", "sys", "请生成完整剧本", 0.5, 128, timeout=10)
    users = [r["user"] for r in s8a.requests]
    check("T8a 连续截断最终诚实报错", text == "" and "上游截断诊断" in err, f"err={err}")
    check("T8a 拆分提示重试上限 2 次", meta.get("split_hint_retries") == 2,
          f"retries={meta.get('split_hint_retries')}")
    check("T8a 共 3 次请求", len(users) == 3, f"n={len(users)}")
    check("T8a 重试请求注入 [SYSTEM] 拆分提示",
          "[SYSTEM]" not in users[0] and "[SYSTEM]" in users[1] and "[SYSTEM]" in users[2])
    st8a = pln_llm.get_router_status(s8a.url)
    check("T8a 截断不触发降级 (状态保持 primary_ok/零失败计数)",
          st8a is not None and st8a["state"] == "primary_ok" and st8a["consecutive_failures"] == 0,
          f"st={st8a}")
    ev8a = [e["event"] for e in st8a["events"]]
    check("T8a 拆分重试留痕于路由事件 (可观测性)", ev8a.count("split_hint_retry") == 2,
          f"events={ev8a}")

    fresh()
    s8b = new_server()

    def t8b_resp(info):
        if len(s8b.requests) == 1:
            return 200, ok_body("第一次被截断……", finish="length")
        return 200, ok_body("完整收尾版本")

    s8b.responder = t8b_resp
    text, err, meta = pln_llm.call_ai_ex(s8b.url, "k", "m", "sys", "请生成完整剧本", 0.5, 128, timeout=10)
    check("T8b 截断一次后注入提示恢复成功", text == "完整收尾版本" and err == "", f"err={err}")
    check("T8b split_hint_retries=1 且第二次请求含提示",
          meta.get("split_hint_retries") == 1 and "[SYSTEM]" in s8b.requests[1]["user"])

    fresh()
    s8c = new_server()
    s8c.responder = lambda info: (200, {"foo": "bar"})
    text, err, meta = pln_llm.call_ai_ex(s8c.url, "k", "m", "sys", "u", 0.5, 64, timeout=10)
    check("T8c 未知响应形态 PROTOCOL 诚实报错", text == "" and "未知响应形态" in err, f"err={err}")
    check("T8c PROTOCOL 仅 1 次请求不重试", len(s8c.requests) == 1)

    fresh()
    s8d = new_server()

    def t8d_resp(info):
        if len(s8d.requests) == 1:
            return 200, "这不是JSON{破碎的尾部"
        return 200, ok_body("恢复成功")

    s8d.responder = t8d_resp
    text, err, meta = pln_llm.call_ai_ex(s8d.url, "k", "m", "sys", "u", 0.5, 64, timeout=10)
    check("T8d 200 非 JSON 按截断处置并恢复", text == "恢复成功" and err == "", f"err={err}")
    check("T8d json_broken 注入拆分提示一次",
          meta.get("split_hint_retries") == 1 and "[SYSTEM]" in s8d.requests[1]["user"])

    fresh()
    s8e = new_server()
    s8e.responder = lambda info: (200, {"error": {"message": "invalid api key format"}})
    text, err, meta = pln_llm.call_ai_ex(s8e.url, "k", "m", "sys", "u", 0.5, 64, timeout=10)
    check("T8e 200 内嵌 error 对象 PROTOCOL 报错", text == "" and "API返回错误对象" in err, f"err={err}")

    print("T8f 终端类错误不计降级阈值 (互审 M-2 语义)")
    fresh()
    s8f = new_server()
    s8f.responder = lambda info: (200, ok_body("截断……", finish="length"))
    chain8f = [{"url": s8f.url, "model": "A", "api_key": "k", "source": "primary"},
               {"url": s8f.url, "model": "B", "api_key": "k", "source": "fallback_model"}]
    for _ in range(pln_llm.FAILURE_THRESHOLD):
        _t, _e, _m = pln_llm.call_ai_ex(s8f.url, "k", "A", "sys", "u", 0.5, 64, timeout=10,
                                        fallback_chain=chain8f, max_retries_per_step=3)
        assert not _t and "上游截断诊断" in _e, f"TRUNCATION 应诚实报错: {_e}"
    st8f = pln_llm.get_router_status(s8f.url)
    check("T8f 连续 3 次 TRUNCATION 不推入降级 (内容级问题)",
          st8f["state"] == "primary_ok" and st8f["consecutive_failures"] == 0, f"st={st8f}")
    check("T8f TRUNCATION 不跨级 (3 次调用全部仅主级服务)",
          len(s8f.requests) == 9 and all(r["model"] == "A" for r in s8f.requests),
          f"n={len(s8f.requests)}")

    fresh()
    s8f2 = new_server()
    s8f2.responder = lambda info: (401, {"error": {"message": "invalid api key"}})
    chain8f2 = [{"url": s8f2.url, "model": "A", "api_key": "k", "source": "primary"},
                {"url": s8f2.url, "model": "B", "api_key": "k", "source": "fallback_model"}]
    for _ in range(pln_llm.FAILURE_THRESHOLD):
        _t, _e, _m = pln_llm.call_ai_ex(s8f2.url, "k", "A", "sys", "u", 0.5, 64, timeout=10,
                                        fallback_chain=chain8f2, max_retries_per_step=3)
        assert not _t and _e, f"AUTH 应诚实报错: {_e}"
    st8f2 = pln_llm.get_router_status(s8f2.url)
    check("T8f 连续 3 次 AUTH 不推入降级 (配置级问题, 避免无意义重放)",
          st8f2["state"] == "primary_ok" and st8f2["consecutive_failures"] == 0, f"st={st8f2}")
    check("T8f AUTH 终端不重试不跨级 (3 次调用各 1 请求)", len(s8f2.requests) == 3,
          f"n={len(s8f2.requests)}")

    print("T8g 200 围栏 JSON 宽容抢救 (互审 L-5)")
    fresh()
    s8g = new_server()
    s8g.responder = lambda info: (200, "```json\n" + json.dumps(ok_body("fenced-ok"),
                                                                ensure_ascii=False) + "\n```")
    text, err, meta = pln_llm.call_ai_ex(s8g.url, "k", "m", "sys", "u", 0.5, 64, timeout=10)
    check("T8g 围栏包裹 JSON 被宽容解析抢救", text == "fenced-ok" and err == "", f"err={err}")
    check("T8g 抢救路径零拆分重试 (单次请求)",
          len(s8g.requests) == 1 and meta.get("split_hint_retries") == 0)

    # =================================================================
    print("T9 字段别名四级容错解析")
    check("T9 精确键命中", pln_llm.resolve_json_field({"title": "v"}, "title") == "v")
    check("T9 忽略大小写命中", pln_llm.resolve_json_field({"Title": "v2"}, "title") == "v2")
    check("T9 中文别名命中", pln_llm.resolve_json_field({"标题": "v3"}, "title") == "v3")
    check("T9 归一化键命中 (连字符/下划线)", pln_llm.resolve_json_field({"Shot-List": [1, 2]}, "shots") == [1, 2])
    check("T9 自定义别名命中", pln_llm.resolve_json_field({"自定义字段": 9}, "duration", aliases=["自定义字段"]) == 9)
    check("T9 规范名大写仍可查别名表 (互审 L-10)",
          pln_llm.resolve_json_field({"标题": "vt"}, "TITLE") == "vt")
    check("T9 未命中返回 default", pln_llm.resolve_json_field({"x": 1}, "title", default="D") == "D")
    check("T9 非 dict 输入返回 default", pln_llm.resolve_json_field([1, 2], "title", default="D") == "D")

    # =================================================================
    print("T10 宽容 JSON 解析")
    o, d = pln_llm.json_loads_tolerant('{"a": 1}')
    check("T10 直接解析", o == {"a": 1} and d == "")
    o, d = pln_llm.json_loads_tolerant('```json\n{"a": 2}\n```')
    check("T10 代码围栏剥离", o == {"a": 2} and d == "", f"diag={d}")
    o, d = pln_llm.json_loads_tolerant('{"a": 3,}')
    check("T10 尾逗号放宽", o == {"a": 3} and d == "", f"diag={d}")
    o, d = pln_llm.json_loads_tolerant('前置噪声文本 {"a": 4} 后置噪声')
    check("T10 配平结构提取", o == {"a": 4} and d == "", f"diag={d}")
    o, d = pln_llm.json_loads_tolerant('{"a": "\\" }')  # 尾部转义引号使配平扫描与抢救都失手
    check("T10 失手输入诚实返回 None 且诊断含抢救步骤",
          o is None and "外层结构提取后解析失败" in d, f"diag={d}")
    o, d = pln_llm.json_loads_tolerant("完全没有JSON的内容")
    check("T10 无结构诚实返回 None", o is None and d, f"diag={d}")
    o, d = pln_llm.json_loads_tolerant("")
    check("T10 空串诚实返回 None", o is None and d)
    o, d = pln_llm.json_loads_tolerant(None)
    check("T10 None 输入诚实返回 None", o is None and d)
    o, d = pln_llm.json_loads_tolerant([1, 2, 3])
    check("T10 非 str 可序列化对象直通", o == [1, 2, 3] and d == "")

    # =================================================================
    print("T11 压缩确定性与保真")
    src = "".join(f"段落{i}内容。" for i in range(200))  # > 400 字符
    g1 = pln_llm.compress_context_gentle(src)
    g2 = pln_llm.compress_context_gentle(src)
    a1 = pln_llm.compress_context_aggressive(src)
    check("T11 gentle 确定性 (两次结果逐字一致)", g1 == g2 and g1 is not None)
    check("T11 aggressive 严格更短", a1 is not None and len(a1) < len(g1) < len(src),
          f"lens={len(src)}/{len(g1)}/{len(a1)}")
    check("T11 压缩标记存在", pln_llm.COMPRESS_MARKER in g1 and pln_llm.COMPRESS_MARKER in a1)
    head_g = int(len(src) * 0.25)
    tail_g = int(len(src) * 0.25)
    check("T11 gentle 头尾逐字保真", g1.startswith(src[:head_g] + "\n") and g1.endswith("\n" + src[-tail_g:]))
    check("T11 短文本 (<400) 不可压返回 None",
          pln_llm.compress_context_gentle("短" * 399) is None
          and pln_llm.compress_context_aggressive("短" * 399) is None)
    check("T11 空输入返回 None", pln_llm.compress_context_gentle("") is None)

    # =================================================================
    print("T13 用户预设文件 (合法/坏JSON/坏结构/不存在)")
    p_override = os.path.join(tmpdir, "presets_override.json")
    with open(p_override, "w", encoding="utf-8") as f:
        json.dump({"presets": {
            "deepseek": {"fallback_models": ["deepseek-custom-x"]},
            "myhost": {"display": "MyHost", "match_hosts": [["api.myhost.example", None]],
                       "fallback_models": ["mh-1"]},
        }}, f, ensure_ascii=False)
    merged13 = pln_llm.get_provider_presets(user_path=p_override)
    check("T13 覆盖内置预设字段", merged13["deepseek"]["fallback_models"] == ["deepseek-custom-x"])
    check("T13 覆盖保留未改字段", merged13["deepseek"]["display"] == "DeepSeek")
    check("T13 新增自定义预设", "myhost" in merged13)
    pid13, _ = pln_llm.get_preset_for_url("https://api.myhost.example/v1/chat", presets=merged13)
    check("T13 自定义预设 host 匹配", pid13 == "myhost", f"pid={pid13}")

    p_bad = os.path.join(tmpdir, "presets_bad.json")
    with open(p_bad, "w", encoding="utf-8") as f:
        f.write("{这不是合法JSON")
    merged_bad = pln_llm.get_provider_presets(user_path=p_bad)
    check("T13 坏 JSON 文件降级为内置预设 (不崩溃)",
          len(merged_bad) == len(pln_llm.PROVIDER_PRESETS) and "deepseek" in merged_bad)

    p_bad2 = os.path.join(tmpdir, "presets_badstruct.json")
    with open(p_bad2, "w", encoding="utf-8") as f:
        json.dump({"presets": [1, 2, 3]}, f)
    merged_bad2 = pln_llm.get_provider_presets(user_path=p_bad2)
    check("T13 坏结构文件降级为内置预设", len(merged_bad2) == len(pln_llm.PROVIDER_PRESETS))

    merged_none = pln_llm.get_provider_presets(user_path=os.path.join(tmpdir, "not_exist.json"))
    check("T13 文件不存在返回内置预设", len(merged_none) == len(pln_llm.PROVIDER_PRESETS))

    builtin = pln_llm.get_provider_presets()
    check("T13 默认内置预设 ≥10 且 deepseek 备用模型真实",
          len(builtin) >= 10 and builtin["deepseek"]["fallback_models"] == ["deepseek-chat"],
          f"n={len(builtin)}")

    # =================================================================
    print("T14 SSRF 防护 (降级链级不回退)")
    fresh()
    s14 = new_server()
    s14.responder = lambda info: (500, {"error": {"message": "down"}})
    chain14 = [{"url": s14.url, "model": "m", "api_key": "k", "source": "primary"},
               {"url": "http://169.254.169.254/latest/meta-data/", "model": "m2",
                "api_key": "k", "source": "fallback_endpoint"}]
    text, err, meta = pln_llm.call_ai_ex(s14.url, "k", "m", "sys", "u", 0.5, 64, timeout=10,
                                         fallback_chain=chain14, max_retries_per_step=1)
    check("T14 云 metadata 链级被 SSRF 跳过且诚实失败", text == "" and err, f"err={err}")
    check("T14 meta 事件记录链级跳过",
          any(e.startswith("level1 SSRF校验失败已跳过") for e in meta.get("events", [])),
          f"events={meta.get('events')}")
    st14 = pln_llm.get_router_status(s14.url)
    ev14 = [e["event"] for e in (st14["events"] if st14 else [])]
    check("T14 路由事件留痕 level_skipped_ssrf", "level_skipped_ssrf" in ev14, f"events={ev14}")

    valid, verr, _ = pln_llm._validate_api_url("http://169.254.169.254/latest/meta-data/")
    check("T14 metadata IP 直接拒绝", valid is False and "SSRF" in verr, f"err={verr}")
    valid, verr, _ = pln_llm._validate_api_url("file:///etc/passwd")
    check("T14 非 http(s) 协议拒绝", valid is False and "协议" in verr, f"err={verr}")
    check("T14 IPv4-mapped 形态规范化拦截", pln_llm._is_blocked_ip("::ffff:a9fe:a9fe") is True)
    check("T14 AWS IMDS IPv6 拦截", pln_llm._is_blocked_ip("fd00:ec2::254") is True)
    check("T14 环回/私网/公网不误伤",
          pln_llm._is_blocked_ip("127.0.0.1") is False
          and pln_llm._is_blocked_ip("192.168.1.5") is False
          and pln_llm._is_blocked_ip("8.8.8.8") is False)
    check("T14 已废弃 IPv4 兼容 IPv6 形态拦截 (互审 L-9)",
          pln_llm._is_blocked_ip("::a9fe:a9fe") is True)
    check("T14 IPv4 兼容形态规范化为内嵌 IPv4",
          str(pln_llm._normalize_ip("::a9fe:a9fe")) == "169.254.169.254")

    # =================================================================
    print("T15 状态机并发冒烟 (互审 M-3 补盲: RLock 无撕裂)")
    fresh()
    import concurrent.futures
    _URL15 = "http://concurrency-selftest.local/v1"

    def _worker(i):
        for j in range(300):
            pln_llm._router_begin(_URL15, 2)
            pln_llm._router_record_failure(_URL15, "SERVER" if j % 2 else "TIMEOUT")
            pln_llm._router_event(_URL15, "worker", f"{i}-{j}")
            if j % 7 == 0:
                pln_llm._router_record_success(_URL15)
            pln_llm.get_router_status(_URL15)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as _ex:
        list(_ex.map(_worker, range(4)))
    st15 = pln_llm.get_router_status(_URL15)
    check("T15 4线程×300轮交叉无异常且状态合法",
          st15 is not None and st15["state"] in ("primary_ok", "fallback_active", "probing"),
          f"st={st15 and st15['state']}")
    check("T15 primary_ok 时失败计数必低于阈值",
          st15["state"] != "primary_ok" or st15["consecutive_failures"] < pln_llm.FAILURE_THRESHOLD,
          f"cf={st15['consecutive_failures']}")
    check("T15 事件环形缓冲有界 (≤64)", len(st15["events"]) <= 64, f"n={len(st15['events'])}")

    # =================================================================
    print("T16 错误分类器语义 (互审 L-1/L-2 修复后)")
    check("T16 429+溢出短语仍判 RATE_LIMIT (状态码优先)",
          pln_llm._classify_llm_failure(429, "maximum context length") == "RATE_LIMIT")
    check("T16 401+溢出短语仍判 AUTH",
          pln_llm._classify_llm_failure(401, "maximum context length") == "AUTH")
    check("T16 30x 禁重定向拒绝归 BAD_REQUEST (终端不重试)",
          pln_llm._classify_llm_failure(302, "") == "BAD_REQUEST")
    check("T16 400+溢出短语判 OVERFLOW (短语对 400/413 仍优先)",
          pln_llm._classify_llm_failure(400, "maximum context length") == "OVERFLOW")
    check("T16 503+溢出短语判 OVERFLOW (备用模型上下文可能更大)",
          pln_llm._classify_llm_failure(503, "上下文过长") == "OVERFLOW")

    # =================================================================
    print("T17 批次3 D1: detect_echo 回声检测 + freeze_system 经济性冻结模式")
    # ---- T17a-d: detect_echo 纯函数 (stdlib difflib, 无状态, 无需 HTTP) ----
    src_a = "夜色中的码头, 潮水拍打桩柱, 仓库灯在雾里晕开, 女人抱紧帆布包走向七号仓。" * 3
    mod_a = src_a.replace("女人", "少女", 1).replace("码头", "渡口", 1)
    hit_a, ratio_a = pln_llm.detect_echo(mod_a, src_a)
    check("T17a 改写后高相似判回声 (hit=True 且 ratio≥0.95)",
          hit_a is True and ratio_a >= 0.95, f"hit={hit_a} ratio={ratio_a}")

    src_b = ("清晨的菜市场人声鼎沸, 鱼贩掀开冰面, 白雾从泡沫箱里涌出来, "
             "穿驼色大衣的姑娘捏着零钱数了两遍, 摊主把一把小葱塞进她袋里没要钱。")
    other_b = ("废弃天文台的圆顶锈死在半开角度, 值夜的技术员用扳手敲了三下传动齿轮, "
               "投影仪残光扫过墙面的星图, 尘埃在光柱里缓慢翻滚如同倒放的雪。")
    hit_b, ratio_b = pln_llm.detect_echo(other_b, src_b)
    check("T17b 正常改写不判回声 (hit=False 且 ratio<0.95)",
          hit_b is False and ratio_b < 0.95, f"hit={hit_b} ratio={ratio_b}")

    big17 = "长镜头缓慢横移, " * 4000   # 36000 字符
    mid17 = "夜色压低天际线, " * 750    # 6750 字符 — 长度差 5.33 倍 (>4 倍)
    t0c = _time.perf_counter()
    hit_c, ratio_c = pln_llm.detect_echo(big17, mid17)
    dt_c = _time.perf_counter() - t0c
    bound_c = 2.0 * min(len(big17), len(mid17)) / (len(big17) + len(mid17))
    check("T17c 长度差>4倍大文本 O(1) 短路 (False + 相似比上界 + 亚秒级, 防大文本 O(n²))",
          hit_c is False and abs(ratio_c - bound_c) < 1e-12 and dt_c < 1.0,
          f"hit={hit_c} ratio={ratio_c} bound={bound_c} dt={dt_c:.4f}s")

    base20 = "ABCDEFGHIJKLMNOPQRST"
    echo20 = base20[:10] + "X" + base20[11:]  # 单字符替换 → 相似比恰为 0.95
    hit95, r95 = pln_llm.detect_echo(echo20, base20, threshold=0.95)
    hit_ov, r_ov = pln_llm.detect_echo(echo20, base20, threshold=0.951)
    check("T17d 阈值边界 (0.95 恰命中 / +微差 0.951 即不命中, ≥阈值判回声)",
          hit95 is True and abs(r95 - 0.95) < 1e-9 and hit_ov is False,
          f"hit95={hit95} r95={r95} hit_ov={hit_ov} r_ov={r_ov}")

    # ---- T17e-g: 冻结模式 (真实本地 HTTP, 链内重试 + 跨调用 + call_ai 透传) ----
    fresh()
    s17 = new_server()
    sys_static17 = "你是资深剧本医生, 只输出修订稿。\n遵循反AI词表与导演档案, 不解释。"
    run_line17 = "[RUN] 日期: 2026-08-31 | 种子: 42 | 工作流: T17冻结验证"
    sys_full17 = sys_static17 + "\n" + run_line17
    user17 = "请修订以下剧本初稿并保持章节结构。"
    n17 = {"calls": 0}

    def t17_resp(info):
        n17["calls"] += 1
        if n17["calls"] == 1:
            return 500, {"error": {"message": "transient"}}  # 首请求失败 → 触发链内重试
        return 200, ok_body("revised-ok")

    s17.responder = t17_resp
    ta, ea, ma = pln_llm.call_ai_ex(s17.url, "k", "m", sys_full17, user17, 0.3, 64, timeout=10,
                                    max_retries_per_step=3, freeze_system=True)
    tb, eb, mb = pln_llm.call_ai_ex(s17.url, "k", "m", sys_full17, user17, 0.3, 64, timeout=10,
                                    max_retries_per_step=3, freeze_system=True)
    tc2, ec2 = pln_llm.call_ai(s17.url, "k", "m", sys_full17, user17, 0.3, 64, timeout=10,
                               freeze_system=True)  # call_ai 关键字透传
    sys_reqs17 = [r["system"] for r in s17.requests]
    usr_reqs17 = [r["user"] for r in s17.requests]
    check("T17e 冻结 system 跨链内重试+两次 call_ai_ex+call_ai 透传逐字节一致 (纯静态前缀)",
          ta == "revised-ok" and tb == "revised-ok" and tc2 == "revised-ok"
          and len(sys_reqs17) == 4
          and sys_reqs17[0] == sys_reqs17[1] == sys_reqs17[2] == sys_reqs17[3] == sys_static17
          and ma.get("system_frozen") is True and ma.get("run_state_lines") == 1
          and mb.get("system_frozen") is True,
          f"errs={ea}/{eb}/{ec2} n={len(sys_reqs17)} "
          f"ma={ma.get('system_frozen')}/{ma.get('run_state_lines')}")

    check("T17f 动态信息整体外置 user 头部 [RUN] 段且不出现在任何 system 中",
          all(u == run_line17 + "\n\n" + user17 for u in usr_reqs17)
          and all(run_line17 not in s for s in sys_reqs17),
          f"users={[u[:30] for u in usr_reqs17]}")

    fresh()
    s17b = new_server()
    s17b.responder = lambda info: (200, ok_body("default-ok"))
    td, ed, md = pln_llm.call_ai_ex(s17b.url, "k", "m", sys_full17, user17, 0.3, 64, timeout=10)
    check("T17g 默认关闭行为与旧路径逐字节一致 (system/user 原样透传含 [RUN] 行, meta 无冻结键)",
          td == "default-ok" and len(s17b.requests) == 1
          and s17b.requests[0]["system"] == sys_full17
          and s17b.requests[0]["user"] == user17
          and "system_frozen" not in md and "run_state_lines" not in md,
          f"err={ed} req_system={s17b.requests[0]['system'][:30]!r}")

finally:
    # 恢复真实时钟/睡眠, 关停全部测试服务器
    pln_llm._clock, pln_llm._sleep = ORIG_CLOCK, ORIG_SLEEP
    for _s in SERVERS:
        _s.stop()

# ---- 证据存档 ----
RESULTS_DOC = {
    "suite": "test_llm_resilience",
    "version": "16.7.0",
    "timestamp": _time.strftime("%Y-%m-%d %H:%M:%S"),
    "pass": PASS,
    "fail": FAIL,
    "results": RESULTS,
}
OUT_JSON = os.path.join(HERE, "llm_resilience_results.json")
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(RESULTS_DOC, f, ensure_ascii=False, indent=2)

print(f"\nLLM 健壮性故障注入结果: {PASS} PASS / {FAIL} FAIL (证据: {OUT_JSON})")
sys.exit(1 if FAIL else 0)
