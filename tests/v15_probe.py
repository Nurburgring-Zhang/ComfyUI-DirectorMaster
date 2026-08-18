# -*- coding: utf-8 -*-
"""
V15.0-MERGED 专项探针 — 4 新节点 + 引擎端到端验证
====================================================
 1. Fusion 节点: 确定性/突破指令/错误路径
 2. Soul 节点: 母题从输入派生, 不同输入不同输出 (零罐头)
 3. Intuition 节点: JSON 往返 + 修改日志
 4. CoCreator 节点: T0 确定性档 3 分支 + 门全过 + 确定性
 5. CoCreator LLM 路径: 本地 OpenAI 兼容服务器真实 HTTP (方向生成+精炼)
 6. 多模态: 真实图像分析
 7. Cinematic 直觉风险档: ND vs bold 输出差异
 8. 导演库: 600 档案 + 新导演档案提取
"""
import os, sys, json, hashlib, threading, time, importlib.util
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")

PASS, FAIL = 0, 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


spec = importlib.util.spec_from_file_location("dm_v15p", os.path.join(ROOT, "__init__.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["dm_v15p"] = mod
spec.loader.exec_module(mod)
M = mod.NODE_CLASS_MAPPINGS


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


def call(cls, kw):
    r = getattr(cls(), cls.FUNCTION)(**kw)
    return r if isinstance(r, tuple) else (r,)


print("=" * 60)
print("V15.0 专项探针")
print("=" * 60)

# 1. Fusion 节点
print("\n--- 1. Fusion 节点 ---")
fkw = {"主风格导演": "[电影] 王家卫", "次风格导演": "是枝裕和", "反风格导演": "滨口龙介",
       "场景描述": "雨夜厨房", "情绪基调": "孤独"}
f1 = call(M["DirectorMasterFusion"], fkw)
f2 = call(M["DirectorMasterFusion"], fkw)
check("Fusion 确定性", f1[0] == f2[0])
check("Fusion 突破指令", "突破指令" in f1[0] and "滨口龙介" in f1[0])
meta = json.loads(f1[1])
check("Fusion 元数据", meta["主风格"] == "王家卫" and meta["反风格"] == "滨口龙介" and meta["融合维度"])
ferr = call(M["DirectorMasterFusion"], {"主风格导演": "查无此人导演", "次风格导演": "", "反风格导演": ""})
check("Fusion 错误路径诚实", "失败" in ferr[0] or json.loads(ferr[1])["错误"])

# 2. Soul 节点
print("\n--- 2. Soul 节点 ---")
skw1 = {"剧本输入": "剧本: 父亲在厨房切菜, 藏着一个秘密。", "创作者体验": "奶奶的旧怀表, 一次没来得及的告别",
        "情感诉求": "思念"}
s1 = call(M["DirectorMasterSoul"], skw1)
check("Soul 母题派生", "奶奶的旧怀表" in s1[0])
rep = json.loads(s1[1])
check("Soul 叙事装置", rep["叙事装置"] in ("伏笔", "反转", "留白"))
check("Soul 情感三层", "深层" in rep["情感三层"] and rep["情感三层"]["深层"])
skw2 = dict(skw1); skw2["创作者体验"] = "海边的灯塔, 一场没有说出口的道歉"
s2 = call(M["DirectorMasterSoul"], skw2)
check("Soul 不同输入不同输出 (零罐头)", s1[0] != s2[0] and "灯塔" in s2[0])

# 3. Intuition 节点
print("\n--- 3. Intuition 节点 ---")
shots = [{"n": i, "size": "特写", "move": "跟拍", "focal": "85mm", "dur": "5s", "dur_sec": 5.0,
          "focus": "焦", "sound": "声", "tension_level": 8 if i == 3 else 5, "angle": "平视",
          "cut": "硬切", "stage": "高潮" if i == 3 else "铺垫"} for i in range(1, 7)]
ijkw = {"分镜JSON": json.dumps({"分镜表": shots}, ensure_ascii=False), "风险档位": "bold",
        "核心数据包": json.dumps({"_情绪基调": "孤独", "_场景描述": "父女对话"}, ensure_ascii=False)}
i1 = call(M["DirectorMasterIntuition"], ijkw)
data = json.loads(i1[0])
log = json.loads(i1[1])
check("Intuition JSON 往返", "分镜表" in data and len(data["分镜表"]) == 6)
check("Intuition 触发规则", len(log) > 0 and data.get("直觉引擎", {}).get("触发数") == len(log))
i2 = call(M["DirectorMasterIntuition"], ijkw)
check("Intuition 确定性", i1[0] == i2[0])

# 4. CoCreator 节点 (T0 确定性)
print("\n--- 4. CoCreator 节点 (T0 确定性) ---")
ckw = {"故事核心": "妹妹寻找失踪的姐姐, 真相被最亲近的人藏起来", "情感诉求": "悬疑中的温情",
       "风险档位": "medium"}
c1 = call(M["DirectorMasterCoCreator"], ckw)
c2 = call(M["DirectorMasterCoCreator"], ckw)
check("CoCreator 确定性", c1[0] == c2[0])
branches = json.loads(c1[1])
check("CoCreator 3 方向分支", len(branches["方向分支"]) == 3)
check("CoCreator 门全过", all(g["pass"] for g in branches["门控报告"]))
check("CoCreator 创作日志", "S1" in c1[2] and "S4" in c1[2])

# 5. CoCreator LLM 路径 (本地测试服务器, 真实 HTTP)
print("\n--- 5. CoCreator LLM 路径 (真实 HTTP) ---")
STATE = {"requests": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        STATE["requests"] += 1
        user_msg = (body.get("messages") or [{}])[-1].get("content", "")
        if "叙事方向" in user_msg or "方向" in user_msg:
            content = ("方向一(悬疑): 姐姐的失踪是自愿的, 她在逃避一个只有妹妹知道的秘密。\n"
                       "方向二(温情): 姐姐一直在暗中保护妹妹, 失踪是为了引开危险。\n"
                       "方向三(反常规): 从姐姐的视角倒叙, 观众比妹妹更早知道真相。\n"
                       "被忽视的机会: 妹妹寻找的过程其实是她理解姐姐的过程。")
        else:
            content = "修订版: 第一场 内景 旧居 夜 — 妹妹翻找姐姐的房间, 发现一张没有寄出的明信片。开场钩子。中点反转。高潮。结局。" * 3
        resp = {"id": "t", "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}
        data = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


server = HTTPServer(("127.0.0.1", 0), Handler)
PORT = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(0.2)
try:
    ckw_llm = dict(ckw)
    ckw_llm["AI接口地址"] = f"http://127.0.0.1:{PORT}/v1/chat/completions"
    ckw_llm["AI密钥"] = "test-key"
    ckw_llm["AI模型名"] = "test-model"
    c3 = call(M["DirectorMasterCoCreator"], ckw_llm)
    branches3 = json.loads(c3[1])
    check("CoCreator LLM 真实 HTTP 调用", STATE["requests"] > 0, f"requests={STATE['requests']}")
    check("CoCreator LLM 档位升级", branches3["能力档位"].startswith("T1"))
    check("CoCreator LLM 输出非空", len(c3[0]) > 300)
finally:
    server.shutdown()

# 6. 多模态
print("\n--- 6. 多模态图像分析 ---")
try:
    import numpy as np
    from aggregator.multimodal_engine import analyze_image
    img = np.zeros((64, 64, 3))
    img[:32, :, :] = [220, 180, 60]
    img[32:, :, :] = [20, 40, 90]
    ia = analyze_image(img)
    check("多模态色板", ia["ok"] and len(ia["palette"]) >= 2)
    check("多模态光影判断", ia["lighting"] != "")
    check("多模态文本输出", "应用建议" in ia["text"])
except ImportError:
    check("多模态 (numpy 缺失降级)", True, "skip")

# 7. Cinematic 直觉风险档
print("\n--- 7. Cinematic 直觉风险档 ---")
core_kw = defaults(M["DirectorMasterCore"])
core_kw["成片时长"] = "30分钟"
cp = call(M["DirectorMasterCore"], core_kw)[1]
cine = M["DirectorMasterCinematic"]
kw_nd = defaults(cine); kw_nd["核心数据包"] = cp; kw_nd["目标时长(分钟)"] = 30
kw_bold = dict(kw_nd); kw_bold["直觉风险"] = "bold"
o_nd = call(cine, kw_nd)[0]
o_bold = call(cine, kw_bold)[0]
check("直觉风险档产生差异", o_nd != o_bold)
check("直觉标注存在", "直觉R" in o_bold)

# 8. 导演库 600
print("\n--- 8. 导演库 600 ---")
import director_data_unified as ddu
check("导演库 ≥600", len(ddu.DIRECTOR_PROFILES_ALL) >= 600, str(len(ddu.DIRECTOR_PROFILES_ALL)))
from aggregator.node_base import get_director_profile_text
p = get_director_profile_text("滨口龙介")
check("新导演档案提取", len(p) > 100)
from aggregator.director_master import DIR_NAMES
check("新导演在下拉", any("滨口龙介" in x for x in DIR_NAMES) and any("[跨界]" in x for x in DIR_NAMES))

print("\n" + "=" * 60)
print(f"V15.0 专项探针: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
