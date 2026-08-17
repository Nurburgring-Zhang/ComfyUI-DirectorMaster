# -*- coding: utf-8 -*-
"""
V14.3 F2 — AI 轨端到端验证 (真实 HTTP, 本地 OpenAI 兼容测试服务器)
====================================================================
测试服务器是测试基础设施; 被测代码 (pln_llm.call_ai / llm_engine.generate_native)
执行真实 HTTP 请求构造/发送/解析/质量门控/降级。

验证点:
  1. call_ai 真实 HTTP 往返 + OpenAI 格式解析
  2. generate_native 接受路径: 合格响应 → 清洗 → 返回
  3. 照抄检测: 服务器返回结构参考的拷贝 → 拒收 → 降级模板
  4. 长度门控: 服务器返回短文本 → 拒收 → 降级
  5. 服务器 500 → 重试耗尽 → 降级
  6. SSRF: 169.254.x 地址拒绝
  7. 领域规则注入: 绘本模式系统提示词含领域块
"""
import os, sys, json, threading, time
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from http.server import BaseHTTPRequestHandler, HTTPServer

STATE = {"mode": "good", "requests": []}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        STATE["requests"].append({
            "path": self.path,
            "model": body.get("model"),
            "system": (body.get("messages") or [{}])[0].get("content", "")[:2000],
            "user": (body.get("messages") or [{}, {}])[-1].get("content", "")[:500],
            "auth": self.headers.get("Authorization", ""),
        })
        if STATE["mode"] == "error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "test server forced 500"}')
            return
        if STATE["mode"] == "copy":
            # 照抄结构参考 → 应被 bigram 检测拒收
            content = OPEN_STRUCT_REF[:4000]
        elif STATE["mode"] == "short":
            content = "很短的回复。"
        else:
            content = GOOD_RESPONSE
        resp = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 100, "total_tokens": 110},
        }
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


# 合格响应: 原生创作, 长度充足, 含导演/场景关键词, 无 AI 套话, 与结构参考低重合
GOOD_RESPONSE = (
    "《沉默的凤梨》·王家卫视角 原生剧本\n\n"
    "第一场 内景 厨房 夜 雨\n"
    "雨点打在窗框上, 1998年哈尔滨的夜带着煤烟味。父亲站在灶台前切菜, 刀与砧板的间隔越来越慢。"
    "女儿坐在桌边, 手指绕着一只凤梨罐头的标签, 标签已经起泡, 过期十五年的黄印像一枚旧邮票。\n"
    "父亲(不抬头): 饿了吧。\n"
    "女儿: 不饿。\n"
    "沉默。收音机里放着老歌, 信号时好时坏。父亲把切好的菜拨进碗里, 动作停了一下——"
    "他看见桌角那封旧信, 信纸泛黄, 折痕处已经裂开。他没碰它, 只是把碗往女儿那边推了推。\n"
    "第二场 内景 厨房 夜 稍后\n"
    "女儿夹起一块凤梨, 放进父亲碗里。父亲的筷子停在半空, 半秒钟, 然后继续。"
    "窗外的霓虹在积水里倒映, 红的绿的, 像打翻的调色盘。雨没有要停的意思。\n"
    "【镜头】中景为主, 50mm, 光圈T2.0, 色温3200K; 逆光从窗外进来, 把两个人的轮廓勾出一层毛边。"
    "声音: 雨声+收音机底噪+筷子碰碗的轻响, 无配乐。\n"
    "【导演意图】观众应感到: 那些没说出口的话, 比说出口的更重。王家卫说: 沉默不是没有情绪, "
    "是情绪太满, 溢不出来, 只能压在动作底下。这场戏的每个物件都是时间的证物: 罐头是十五年前买的, "
    "信是写了没寄的, 收音机是修过三次没换的。人物不说想念, 但每个动作都是想念的形状。\n"
    "结尾不给答案: 信最终有没有被打开, 留给观众。把判断权交出去, 情绪才会留在观众身上。"
)

OPEN_STRUCT_REF = "结构参考占位文本A" * 200  # 会被测试替换为真实结构参考

server = HTTPServer(("127.0.0.1", 0), Handler)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(0.2)
URL = f"http://127.0.0.1:{PORT}/v1/chat/completions"
print(f"测试服务器: {URL}")

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


from pln_llm import call_ai
from aggregator.llm_engine import generate_native, _build_native_prompt

STRUCT_REF = (
    "【剧本结构参考】\n第一场 内景 厨房 夜\n父亲切菜, 女儿坐着。\n"
    "第二场 内景 厨房 夜 稍后\n两人沉默对坐。\n第三场 内景 厨房 深夜\n信被拿起又放下。\n"
    "【架构】三幕: 建立/对抗/解决。\n【角色弧】父亲从回避到面对; 女儿从等待到开口。"
)
CONTEXT = {"scene": "父女在厨房, 雨夜, 1998年哈尔滨, 父亲切菜, 女儿坐桌边, 桌上有凤梨罐头和旧信",
           "mood": "孤独", "intent": "没说出口的话最重"}

# 1. call_ai 真实往返
r, err = call_ai(URL, "test-key", "test-model", "系统", "用户消息", 0.7, 1024)
check("call_ai 真实HTTP往返", bool(r) and not err, f"err={err}")
check("请求带 Bearer 认证", STATE["requests"][-1]["auth"] == "Bearer test-key")
check("请求含 model 字段", STATE["requests"][-1]["model"] == "test-model")

# 2. generate_native 接受路径
STATE["mode"] = "good"
out = generate_native("剧本", "完整剧本", "王家卫", CONTEXT, URL, "k", "m", STRUCT_REF, iterate=False)
check("generate_native 合格响应被接受", out and "凤梨罐头" in out and out != STRUCT_REF)

# 3. 领域规则注入 (绘本)
sp = _build_native_prompt("剧本", "绘本", "王家卫", CONTEXT)
check("绘本领域规则注入系统提示词", "领域专属创作规则" in sp)
sp2 = _build_native_prompt("剧本", "完整剧本", "王家卫", CONTEXT)
check("非领域模式无领域块", "领域专属创作规则" not in sp2)

# 4. 照抄检测拒收
OPEN_STRUCT_REF = STRUCT_REF
STATE["mode"] = "copy"
out_copy = generate_native("剧本", "完整剧本", "王家卫", CONTEXT, URL, "k", "m", STRUCT_REF, iterate=False)
check("照抄结构参考被拒收→降级模板", out_copy == STRUCT_REF)

# 5. 长度门控拒收
STATE["mode"] = "short"
out_short = generate_native("剧本", "完整剧本", "王家卫", CONTEXT, URL, "k", "m", STRUCT_REF, iterate=False)
check("长度不足被拒收→降级模板", out_short == STRUCT_REF)

# 6. 服务器错误 → 降级
STATE["mode"] = "error"
out_err = generate_native("剧本", "完整剧本", "王家卫", CONTEXT, URL, "k", "m", STRUCT_REF, iterate=False)
check("服务器500重试耗尽→降级模板", out_err == STRUCT_REF)

# 7. SSRF 拒绝
r7, err7 = call_ai("http://169.254.169.254/latest/meta-data", "k", "m", "s", "u", 0.5, 100)
check("SSRF 169.254.x 拒绝", not r7 and "SSRF" in err7, f"err={err7}")

# 8. 迭代路径 (good 响应 + refine 调用)
STATE["mode"] = "good"
out_it = generate_native("剧本", "完整剧本", "王家卫", CONTEXT, URL, "k", "m", STRUCT_REF, iterate=True)
check("迭代路径可用(不崩)", bool(out_it))

server.shutdown()
print(f"\nF2 结果: {PASS} PASS / {FAIL} FAIL (服务器共收到 {len(STATE['requests'])} 个真实请求)")
sys.exit(1 if FAIL else 0)
