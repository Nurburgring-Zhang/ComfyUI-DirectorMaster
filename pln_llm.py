# ============================================================
# LLM 调用封装 — AI请求/翻译/重试
# ------------------------------------------------------------
# V16.2.0 批次1 (LLM 链路健壮性加固, 思路借鉴 openclacky 独立重写):
#   · provider 预设注册表 (PROVIDER_PRESETS 内置 10 预设 + llm_presets.user.json 覆盖)
#   · 三态降级状态机 (primary_ok / fallback_active / probing, 冷却后探测恢复)
#   · 错误分类 + 溢出两层压缩 (gentle 25% / aggressive 12.5%)
#   · 上游截断检测 + [SYSTEM] 拆分提示重试 (每次调用最多 2 次)
#   · 字段别名四级容错解析 + 宽容 JSON 解析
#   · 测试缝隙: _clock/_sleep 可覆写, call_ai_ex 返回 meta
# 向后兼容: call_ai 保持 7 位置参数签名; 仅 stdlib, 零第三方依赖。
# ============================================================
import json
import os
import re
import socket
import ssl
import sys
import threading
import http.client
import ipaddress
import urllib.request
import urllib.error
import urllib.parse
import time as _time
import random
from collections import deque


# V16.2.0 测试缝隙: 状态机/退避使用的时钟与睡眠函数。
# 生产代码通过模块全局名引用 (调用时解析), 测试可覆写 pln_llm._clock / pln_llm._sleep
# 实现确定性故障注入, 不引入任何第三方 mock 库。
_clock = _time.monotonic
_sleep = _time.sleep


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """V13.5 SSRF加固: 禁止跟随重定向 (防止 http://host → 302 → 169.254.169.254 云metadata)."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"禁止重定向(SSRF防护): {code}", headers, fp)


# V16.1.1 审计修复 M-3: 云 metadata 端点清单 — 永不是合法 LLM 端点 (显式拦, 不依赖网段推断)
_METADATA_IPS = {
    "169.254.169.254",   # AWS / GCP / Azure / Oracle / DigitalOcean metadata
    "fd00:ec2::254",     # AWS IMDS IPv6
}


def _normalize_ip(ip_str):
    """规范化 IP: 解包 IPv4-mapped IPv6 (::ffff:a9fe:a9fe → 169.254.169.254)
    与已废弃的 IPv4 兼容 IPv6 形态 (::a9fe:a9fe, V16.2.0 互审修复 L-9 纵深防御).
    非法返回 None."""
    try:
        ip = ipaddress.ip_address(str(ip_str).strip().strip("[]").split("%")[0])
        if isinstance(ip, ipaddress.IPv6Address):
            if ip.ipv4_mapped is not None:
                return ip.ipv4_mapped
            v = int(ip)
            if v != 0 and v >> 32 == 0:
                # ::a.b.c.d 形态 (RFC 4291 已废弃, 现代协议栈不路由) — 解包低 32 位再判黑
                return ipaddress.IPv4Address(v & 0xFFFFFFFF)
        return ip
    except (ValueError, TypeError):
        return None


def _is_blocked_ip(ip_str):
    """判断是否为禁止访问的 IP (link-local/云metadata). 环回与私网放行(本地/内网LLM合法).
    V16.1.1 审计修复 M-3: ipaddress 规范化后判定, 覆盖 ::ffff:a9fe:a9fe 十六进制写法、
    fd00:ec2::254 (AWS IMDS IPv6) 等旧字符串黑名单漏掉的形态。"""
    ip = _normalize_ip(ip_str)
    if ip is None:
        return False  # 非 IP 字面量由 URL 校验层处理
    if ip.is_link_local:
        return True
    if str(ip) in _METADATA_IPS:
        return True
    return False


def _validate_api_url(api_url):
    """校验API URL协议+主机, 防SSRF (协议/主机/link-local与云metadata IP).
    V16.1.1 审计修复 M-2: DNS 解析失败 → 拒绝 (fail-closed, 不再放行交由连接阶段);
    返回全部安全候选 IP 供连接层直连复用, 消除 校验时解析A/连接时解析B 的 TOCTOU 面。
    V16.1.1 审计修复 H1 (二轮对抗审核发现): 全部返回路径统一为 3 元组;
    V16.1.1 审计修复 M-A1: 候选 IP 取全部非黑名单地址 (去重保序), 连接层按序故障切换。

    返回: (valid, err_msg, candidate_ips)  — candidate_ips 为去重后的安全 IP 字符串列表
    """
    if not api_url:
        return False, "API地址为空", []
    try:
        parsed = urllib.parse.urlparse(api_url)
        if parsed.scheme not in ('http', 'https'):
            return False, f"不支持的URL协议: {parsed.scheme}，仅支持 http/https", []
        if not parsed.hostname:
            return False, "URL缺少主机名", []
        # 解析主机名 → IP, 拒绝 link-local/云metadata (环回/私网放行)
        host = parsed.hostname
        default_port = 443 if parsed.scheme == "https" else 80
        try:
            infos = socket.getaddrinfo(host, parsed.port or default_port, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            # V16.1.1: fail-closed — DNS 解析失败即拒绝 (旧实现放行, 连接阶段二次解析可落到被禁IP)
            return False, f"DNS解析失败, 拒绝连接(SSRF防护 fail-closed): {str(host)[:80]}", []
        if not infos:
            return False, "DNS未返回任何地址, 拒绝连接(SSRF防护)", []
        candidates = []
        for info in infos:
            ip = info[4][0]
            if _is_blocked_ip(ip):
                return False, f"禁止访问内网保留地址(SSRF防护): {ip}", []
            if ip not in candidates:
                candidates.append(ip)
        if not candidates:
            return False, "DNS未返回任何可用地址, 拒绝连接(SSRF防护)", []
        return True, "", candidates
    except Exception as e:
        return False, f"URL格式错误: {str(e)[:100]}", []


class _PinnedHTTPConnection(http.client.HTTPConnection):
    """V16.1.1 审计修复 M-2: 直连校验阶段解析出的 IP, 连接阶段零 DNS —
    消除 DNS rebinding (校验时良性IP, 连接时指向 169.254.169.254) 的二次解析面。
    V16.1.1 审计修复 M-A1: 接受候选 IP 列表, connect() 按序故障切换
    (双栈环境下首记录不可达时不再把 3 次重试耗死在同一 IP)。"""

    def __init__(self, host, port=None, *, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 pinned_ips=None, **kwargs):
        super().__init__(host, port, timeout=timeout, **kwargs)
        self._pinned_ips = list(pinned_ips or [])

    def _connect_targets(self):
        # V16.1.1 审计修复 L-B2: 钉扎集为空即拒绝连接 (fail-closed) —
        # 禁止回退到二次 DNS 解析, 否则 SSRF 钉扎保证形同虚设
        if not self._pinned_ips:
            raise OSError("IP 钉扎集为空, 拒绝连接 (SSRF 防护 fail-closed)")
        return self._pinned_ips

    def connect(self):
        last_err = None
        for target in self._connect_targets():
            try:
                self.sock = socket.create_connection((target, self.port), self.timeout)
                return
            except OSError as e:
                last_err = e
        raise last_err if last_err is not None else OSError("无可用连接目标")


class _PinnedHTTPSConnection(_PinnedHTTPConnection):
    default_port = 443

    def connect(self):
        last_err = None
        for target in self._connect_targets():
            try:
                raw = socket.create_connection((target, self.port), self.timeout)
            except OSError as e:
                last_err = e
                continue
            try:
                ctx = ssl.create_default_context()
                # TLS 证书仍按原始主机名校验 (server_hostname), 只是 TCP 直连已验证的 IP
                self.sock = ctx.wrap_socket(raw, server_hostname=self.host)
                return
            except Exception as e:
                try:
                    raw.close()
                except Exception:
                    pass
                last_err = e
        raise last_err if last_err is not None else OSError("无可用连接目标")


def _pinned_opener(pinned_ips):
    """构建 禁重定向 + IP 钉扎 + 显式无代理 的 opener (每次调用新建, 无全局可变状态).
    V16.1.1 审计修复 L-B1: ProxyHandler({}) 显式禁用环境代理 —
    防止 HTTP(S)_PROXY 把请求导向代理而绕过 IP 钉扎 (钉扎语义=直连已验证IP)。"""

    class _PinnedHTTPHandler(urllib.request.HTTPHandler):
        def http_open(self, req):
            return self.do_open(_PinnedHTTPConnection, req, pinned_ips=pinned_ips)

    class _PinnedHTTPSHandler(urllib.request.HTTPSHandler):
        def https_open(self, req):
            return self.do_open(_PinnedHTTPSConnection, req, pinned_ips=pinned_ips)

    return urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                       _NoRedirectHandler(), _PinnedHTTPHandler(), _PinnedHTTPSHandler())


# =====================================================================
# V16.2.0 批次1 §1.1 — provider 预设注册表
# =====================================================================
# 诚实纪律: capabilities 只标注有公开文档支撑的能力, 不确定的一律保守标 False;
# 模型谱系更新快的厂商 (minimax/siliconflow/openrouter) 不内置过时的具体模型名,
# fallback_models 留空由 llm_presets.user.json 覆盖; 本地运行时 (ollama/lmstudio)
# 模型清单完全由用户本地决定, 同样留空。
PROVIDER_PRESETS = {
    "openai": {
        "display": "OpenAI",
        "match_hosts": [("api.openai.com", None)],
        "key_env": "OPENAI_API_KEY",
        "capabilities": {"prompt_cache": True, "image_input": True, "video_input": False, "stream": True},
        "fallback_models": ["gpt-4o-mini"],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "deepseek": {
        "display": "DeepSeek",
        "match_hosts": [("api.deepseek.com", None)],
        "key_env": "DEEPSEEK_API_KEY",
        "capabilities": {"prompt_cache": True, "image_input": False, "video_input": False, "stream": True},
        "fallback_models": ["deepseek-chat"],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "moonshot": {
        "display": "Moonshot (Kimi)",
        "match_hosts": [("api.moonshot.cn", None)],
        "key_env": "MOONSHOT_API_KEY",
        "capabilities": {"prompt_cache": False, "image_input": True, "video_input": False, "stream": True},
        "fallback_models": ["moonshot-v1-8k"],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "zhipu-glm": {
        "display": "智谱 GLM",
        "match_hosts": [("open.bigmodel.cn", None)],
        "key_env": "ZHIPU_API_KEY",
        "capabilities": {"prompt_cache": False, "image_input": True, "video_input": False, "stream": True},
        "fallback_models": ["glm-4-flash"],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "dashscope": {
        "display": "阿里云百炼 DashScope (OpenAI 兼容模式)",
        "match_hosts": [("dashscope.aliyuncs.com", None)],
        "key_env": "DASHSCOPE_API_KEY",
        "capabilities": {"prompt_cache": False, "image_input": True, "video_input": False, "stream": True},
        "fallback_models": ["qwen-plus", "qwen-turbo"],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "minimax": {
        "display": "MiniMax",
        "match_hosts": [("api.minimaxi.com", None), ("api.minimax.chat", None)],
        "key_env": "MINIMAX_API_KEY",
        "capabilities": {"prompt_cache": False, "image_input": False, "video_input": False, "stream": True},
        # 模型谱系更新快, 不内置过时清单 — 用 llm_presets.user.json 覆盖
        "fallback_models": [],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "siliconflow": {
        "display": "硅基流动 SiliconFlow",
        "match_hosts": [("api.siliconflow.cn", None), ("api.siliconflow.com", None)],
        "key_env": "SILICONFLOW_API_KEY",
        # 托管开源模型清单随时变动, 能力视所托管模型而定, 保守标注
        "capabilities": {"prompt_cache": False, "image_input": False, "video_input": False, "stream": True},
        "fallback_models": [],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "openrouter": {
        "display": "OpenRouter",
        "match_hosts": [("openrouter.ai", None)],
        "key_env": "OPENROUTER_API_KEY",
        # 聚合网关, 能力完全取决于所选模型, 保守标注
        "capabilities": {"prompt_cache": False, "image_input": False, "video_input": False, "stream": True},
        "fallback_models": [],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "ollama": {
        "display": "Ollama (本地)",
        "match_hosts": [("127.0.0.1", 11434), ("localhost", 11434)],
        "key_env": "",
        # 本地模型清单由用户决定, 不内置
        "capabilities": {"prompt_cache": False, "image_input": False, "video_input": False, "stream": True},
        "fallback_models": [],
        "lite_models": [],
        "fallback_endpoints": [],
    },
    "lmstudio": {
        "display": "LM Studio (本地)",
        "match_hosts": [("127.0.0.1", 1234), ("localhost", 1234)],
        "key_env": "",
        "capabilities": {"prompt_cache": False, "image_input": False, "video_input": False, "stream": True},
        "fallback_models": [],
        "lite_models": [],
        "fallback_endpoints": [],
    },
}

_PRESETS_CACHE = None


def _package_root():
    return os.path.dirname(os.path.abspath(__file__))


def _load_user_presets(path=None):
    """读取用户预设文件 (默认: 包根 llm_presets.user.json, 可选文件)。
    结构: {"presets": {preset_id: {字段...}}}。
    坏文件 → stderr 警告, 返回 {} 不阻断内置预设。"""
    p = path or os.path.join(_package_root(), "llm_presets.user.json")
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        sys.stderr.write(f"[DirectorMaster] llm_presets.user.json 解析失败, 忽略用户预设: {e!r}\n")
        return {}
    presets = data.get("presets") if isinstance(data, dict) else None
    if not isinstance(presets, dict):
        sys.stderr.write("[DirectorMaster] llm_presets.user.json 结构应为 {\"presets\": {...}}, 忽略用户预设\n")
        return {}
    return presets


def _merge_presets(overrides):
    merged = {}
    for pid, preset in PROVIDER_PRESETS.items():
        merged[pid] = dict(preset)
    for pid, override in (overrides or {}).items():
        if not isinstance(override, dict):
            continue
        if pid in merged:
            merged[pid] = {**merged[pid], **override}
        else:
            merged[pid] = dict(override)
    return merged


def get_provider_presets(user_path=None):
    """返回 内置预设 + 用户覆盖 的合并结果。
    user_path=None 时读默认位置并进程内缓存; 显式传路径 (测试/诊断) 不走缓存。
    注意 (V16.2.0 互审 L-7): 缓存路径返回的是进程级共享引用, 调用方必须只读,
    不得原地修改返回值 (会污染缓存); 需要改动请先 dict() 拷贝。"""
    global _PRESETS_CACHE
    if user_path is not None:
        return _merge_presets(_load_user_presets(user_path))
    if _PRESETS_CACHE is None:
        _PRESETS_CACHE = _merge_presets(_load_user_presets(None))
    return _PRESETS_CACHE


def reload_provider_presets():
    """清缓存并重读用户预设文件 (用户修改 llm_presets.user.json 后可调用)。"""
    global _PRESETS_CACHE
    _PRESETS_CACHE = None
    return get_provider_presets()


def get_preset_for_url(api_url, presets=None):
    """按 host 后缀 + port 匹配预设。返回 (preset_id, preset) 或 (None, None)。
    多个预设同时命中时取 host 后缀最长者 (更具体)。"""
    try:
        parsed = urllib.parse.urlparse(api_url)
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except Exception:
        return None, None
    if not host:
        return None, None
    presets = presets if presets is not None else get_provider_presets()
    best_id, best_len = None, -1
    for pid, preset in presets.items():
        if not isinstance(preset, dict):
            continue
        for entry in preset.get("match_hosts") or []:
            try:
                suffix, want_port = entry
            except Exception:
                continue
            if not isinstance(suffix, str):
                continue
            if want_port is not None and port != want_port:
                continue
            s = suffix.lower()
            if host == s or host.endswith("." + s):
                if len(s) > best_len:
                    best_id, best_len = pid, len(s)
    if best_id is not None:
        return best_id, presets[best_id]
    return None, None


def build_fallback_chain(api_url, api_key, model_name, presets=None):
    """构建降级步骤链: 主调用 → 同端点备用模型 (fallback_models + lite_models) → 跨端点 (fallback_endpoints)。
    每步: {"url", "model", "api_key", "source"}; source ∈ primary/fallback_model/fallback_endpoint。
    跨端点 key_env: 环境变量有值则用之, 否则回退主调 api_key (同厂商多端点常见共用密钥)。"""
    chain = [{"url": api_url, "model": model_name, "api_key": api_key, "source": "primary"}]
    _pid, preset = get_preset_for_url(api_url, presets=presets)
    if not preset:
        return chain
    seen = {(api_url, model_name)}
    for m in list(preset.get("fallback_models") or []) + list(preset.get("lite_models") or []):
        if not m or not isinstance(m, str) or m == model_name or (api_url, m) in seen:
            continue
        seen.add((api_url, m))
        chain.append({"url": api_url, "model": m, "api_key": api_key, "source": "fallback_model"})
    for ep in preset.get("fallback_endpoints") or []:
        if isinstance(ep, str):
            ep = {"url": ep}
        if not isinstance(ep, dict):
            continue
        u = ep.get("url")
        if not u or not isinstance(u, str):
            continue
        m = ep.get("model") or model_name
        if (u, m) in seen:
            continue
        kenv = ep.get("key_env") or preset.get("key_env") or ""
        key = os.environ.get(kenv) if kenv else None
        chain.append({"url": u, "model": m, "api_key": key or api_key, "source": "fallback_endpoint"})
        seen.add((u, m))
    return chain


# =====================================================================
# V16.2.0 批次1 §1.2 — 三态降级状态机 (primary_ok / fallback_active / probing)
# =====================================================================
FAILURE_THRESHOLD = 3          # 主端点连续可重试类失败 N 次 → 进入 fallback_active (后续调用直接走备用级)
                               # 仅 _THRESHOLD_CLASSES 计入; 内容/配置级错误 (AUTH/BAD_REQUEST/
                               # PROTOCOL/TRUNCATION) 换端点同样失败, 不计阈值 (见 _THRESHOLD_CLASSES)
FALLBACK_COOLDOWN_SECONDS = 60.0  # fallback_active 冷却时长; 到期后下一次调用先探测主端点

_ROUTER_STATE = {}
_ROUTER_LOCK = threading.RLock()


def _ensure_router_state(api_url):
    with _ROUTER_LOCK:
        st = _ROUTER_STATE.get(api_url)
        if st is None:
            st = {"state": "primary_ok", "consecutive_failures": 0,
                  "last_state_change": _clock(), "events": deque(maxlen=64)}
            _ROUTER_STATE[api_url] = st
        return st


def _router_event(api_url, event, detail=""):
    try:
        st = _ensure_router_state(api_url)
        with _ROUTER_LOCK:
            st["events"].append({"t": _clock(), "event": event, "detail": str(detail)[:200]})
    except Exception:
        pass  # 事件记录失败不得影响主调用


def _router_begin(api_url, chain_len):
    """决定本次调用从哪一级开始。返回 (start_level, probe_mode)。
    fallback_active 且冷却到期 → 转 probing, 先单次探测主端点。"""
    if chain_len <= 1:
        return 0, False
    st = _ensure_router_state(api_url)
    with _ROUTER_LOCK:
        if st["state"] == "primary_ok":
            return 0, False
        now = _clock()
        if st["state"] == "fallback_active":
            if now - st["last_state_change"] >= FALLBACK_COOLDOWN_SECONDS:
                st["state"] = "probing"
                st["last_state_change"] = now
                st["events"].append({"t": now, "event": "probing_start", "detail": ""})
                return 0, True
            return 1, False
        # probing (理论上的同调用重入; 或探测因链级校验被跳过而滞留时的保护)
        # 滞留保护: probing 超过一个冷却周期仍未落定 → 强制回落 fallback_active,
        # 防止状态机永久卡在 probing (如探测期间 level0 二次校验瞬时失败被跳过)
        if now - st["last_state_change"] >= FALLBACK_COOLDOWN_SECONDS:
            st["state"] = "fallback_active"
            st["last_state_change"] = now
            st["events"].append({"t": now, "event": "probing_timeout_fallback", "detail": ""})
            return 1, False
        return 0, True


def _router_record_failure(api_url, err_class):
    st = _ensure_router_state(api_url)
    with _ROUTER_LOCK:
        now = _clock()
        if st["state"] == "probing":
            st["state"] = "fallback_active"
            st["last_state_change"] = now
            st["events"].append({"t": now, "event": "probe_failed", "detail": str(err_class)[:60]})
        elif st["state"] == "primary_ok":
            st["consecutive_failures"] += 1
            if st["consecutive_failures"] >= FAILURE_THRESHOLD:
                st["state"] = "fallback_active"
                st["last_state_change"] = now
                st["events"].append({"t": now, "event": "fallback_activated",
                                     "detail": f"连续 {st['consecutive_failures']} 次失败"})


def _router_record_success(api_url):
    """主端点 (level 0) 成功。返回先前状态 (供调用方判定 recovered)。"""
    st = _ensure_router_state(api_url)
    with _ROUTER_LOCK:
        prior = st["state"]
        st["state"] = "primary_ok"
        st["consecutive_failures"] = 0
        if prior != "primary_ok":
            st["events"].append({"t": _clock(),
                                 "event": "probe_recovered" if prior == "probing" else "primary_restored",
                                 "detail": ""})
        return prior


def get_router_status(api_url):
    """查询某主端点的路由状态 (None = 从未记录)。事件列表为拷贝。"""
    with _ROUTER_LOCK:
        st = _ROUTER_STATE.get(api_url)
        if st is None:
            return None
        return {"state": st["state"], "consecutive_failures": st["consecutive_failures"],
                "last_state_change": st["last_state_change"], "events": list(st["events"])}


def reset_router_state(api_url=None):
    """复位路由状态 (api_url=None 清全部)。测试与运维入口。"""
    with _ROUTER_LOCK:
        if api_url is None:
            _ROUTER_STATE.clear()
        else:
            _ROUTER_STATE.pop(api_url, None)


# =====================================================================
# V16.2.0 批次1 §1.3 — 错误分类 + 溢出两层压缩
# =====================================================================
OVERFLOW_PHRASES = (
    # OpenAI / 通用英文
    "maximum context length", "context_length_exceeded", "context length",
    "prompt is too long", "range of input length", "input is too long",
    "too many tokens", "token limit", "context window", "request too large",
    # 中文服务商
    "上下文过长", "超出上下文", "输入过长", "长度超过限制", "超过上下文长度",
)

# 错误类别语义:
#   OVERFLOW    — 上下文/输入超长: 先压缩重试, 仍溢出可跨级 (备用模型上下文可能更大)
#   AUTH        — 401/403 配置级错误: 不重试不跳级, 诚实报错 (换端点也是错)
#   RATE_LIMIT  — 429: 退避重试
#   SERVER      — 5xx: 退避重试
#   BAD_REQUEST — 30x 禁重定向拒绝 / 其余 4xx: 不重试不跳级
#   CONNECTION/TIMEOUT/UNKNOWN — 退避重试
#   PROTOCOL/TRUNCATION — 内容级问题 (200 响应形态异常), 不触发跨级降级
def _classify_llm_failure(code, body):
    # V16.2.0 互审修复 L-1: 401/403/429 的状态码语义优先于溢出短语 —
    # 防止 429 TPM 限流报文含 "token limit" 类短语被误判 OVERFLOW 而丢失退避
    if code in (401, 403):
        return "AUTH"
    if code == 429:
        return "RATE_LIMIT"
    low = (body or "").lower()
    for p in OVERFLOW_PHRASES:
        if p in low:
            return "OVERFLOW"
    if code == 413:
        return "OVERFLOW"
    if code in (500, 502, 503, 504):
        return "SERVER"
    if code == 408:
        return "TIMEOUT"
    # V16.2.0 互审修复 L-2: 30x 为禁重定向 opener 的确定性拒绝结果,
    # 重试无意义 → 归 BAD_REQUEST 终端类 (不再落入 UNKNOWN 被退避重试)
    if code is not None and 300 <= code < 400:
        return "BAD_REQUEST"
    if code is not None and 400 <= code < 500:
        return "BAD_REQUEST"
    if code is None:
        if "timeout" in low or "timed out" in low or "超时" in low:
            return "TIMEOUT"
        return "CONNECTION"
    return "UNKNOWN"


COMPRESS_MARKER = "[…中段内容已省略(长度压缩)]"
_MIN_COMPRESSIBLE_LEN = 400  # 短于此长度的 user 消息不可压 (压了也没有收益)


def _compress_middle(text, head_ratio, tail_ratio):
    n = len(text)
    head = int(n * head_ratio)
    tail = int(n * tail_ratio)
    if head <= 0 or tail <= 0 or head + tail >= n:
        return None
    return text[:head] + "\n" + COMPRESS_MARKER + "\n" + text[n - tail:]


def compress_context_gentle(user_message):
    """一层压缩: 保留 user 消息头尾各 25% (system 不动)。不可压返回 None。确定性纯函数。"""
    if not user_message or len(user_message) < _MIN_COMPRESSIBLE_LEN:
        return None
    return _compress_middle(user_message, 0.25, 0.25)


def compress_context_aggressive(user_message):
    """二层压缩: 保留 user 消息头尾各 12.5%。不可压返回 None。确定性纯函数。"""
    if not user_message or len(user_message) < _MIN_COMPRESSIBLE_LEN:
        return None
    return _compress_middle(user_message, 0.125, 0.125)


# =====================================================================
# V16.2.0 批次1 §1.4 — 上游截断检测与拆分提示
# =====================================================================
# 设计说明 (V16.2.0 互审 L-4 固化): 拆分提示按累加式注入 (cur_user += hint),
# 两次重试后 user 消息含两份提示 — 有意为之 (渐进强调, 上界固定 +2 份, 不失控)。
_SPLIT_HINT = ("\n\n[SYSTEM] 注意: 你上一次的输出被上游截断。请压缩输出: 把内容精简为最核心的完整版本, "
               "总长度控制在约 {max_tokens} token 以内; 可以减少细节, 但必须保证结构完整收尾, 不要输出到一半就停。")


def _interpret_200(result):
    """解释 200 响应体。返回 (text, verdict, detail); verdict ∈ OK/TRUNCATED/PROTOCOL。
    OK 时 detail 为 finish_reason (可空); TRUNCATED/PROTOCOL 时 detail 为诊断说明。"""
    if isinstance(result, str):
        s = result.strip()
        if s:
            return s, "OK", ""
        return "", "TRUNCATED", "响应为空字符串"
    if not isinstance(result, dict):
        return "", "PROTOCOL", f"API返回非对象结构: {str(result)[:80]}"
    if "choices" in result:
        choices = result.get("choices")
        if not isinstance(choices, list) or len(choices) == 0:
            return "", "TRUNCATED", "choices 为空列表"
        c = choices[0] if isinstance(choices[0], dict) else {}
        msg = c.get("message") if isinstance(c.get("message"), dict) else {}
        content = msg.get("content") or c.get("text") or ""
        content = content if isinstance(content, str) else str(content)
        finish = c.get("finish_reason") or ""
        if finish == "length":
            return "", "TRUNCATED", "finish_reason=length (输出在上游被截断)"
        if content.strip():
            return content.strip(), "OK", finish
        return "", "TRUNCATED", "choices[0] 内容为空"
    if "response" in result:
        r = result.get("response")
        r = r if isinstance(r, str) else (str(r) if r is not None else "")
        if r.strip():
            return r.strip(), "OK", ""
        return "", "TRUNCATED", "response 字段为空"
    if "error" in result:
        return "", "PROTOCOL", f"API返回错误对象: {str(result.get('error'))[:120]}"
    return "", "PROTOCOL", f"未知响应形态(无choices/response字段): {str(result)[:120]}"


# =====================================================================
# V16.2.0 批次1 §1.5 — 字段别名四级容错 + 宽容 JSON 解析
# =====================================================================
def normalize_key(key):
    """别名匹配归一化: 去空白/连字符/下划线 + 小写。"""
    return re.sub(r"[\s\-_]+", "", str(key)).lower()


# 中英别名表: canonical → 别名列表 (覆盖 LLM 交付 JSON 常见字段漂移)
DM_FIELD_ALIASES = {
    "title": ["标题", "片名", "题目", "name", "headline"],
    "content": ["内容", "正文", "body", "text", "text_content"],
    "shots": ["镜头", "分镜", "镜头列表", "分镜列表", "shot_list", "shotlist", "storyboard"],
    "scenes": ["场景", "场次", "场景列表", "scene_list"],
    "script": ["剧本", "脚本", "screenplay"],
    "prompt": ["提示词", "正向提示词", "positive_prompt", "positive"],
    "negative_prompt": ["反向提示词", "负向提示词", "negative", "neg_prompt"],
    "duration": ["时长", "持续时间", "dur", "length"],
    "summary": ["摘要", "总结", "概要", "简介"],
    "director": ["导演", "director_name"],
}


def resolve_json_field(obj, canonical, default=None, aliases=None):
    """四级字段解析: ① 精确键 → ② 忽略大小写 → ③ 别名表 (忽略大小写) → ④ 归一化键。
    任一级命中即返回对应值; 全部未命中返回 default。非 dict 输入直接返回 default。"""
    if not isinstance(obj, dict):
        return default
    if canonical in obj:
        return obj[canonical]
    low = str(canonical).lower()
    for k, v in obj.items():
        if str(k).lower() == low:
            return v
    # V16.2.0 互审修复 L-10: 别名表按规范名小写查表 (canonical 大小写不敏感)
    alias_set = list(DM_FIELD_ALIASES.get(low, [])) + list(aliases or [])
    if alias_set:
        alias_lows = {str(a).lower() for a in alias_set}
        for k, v in obj.items():
            if str(k).lower() in alias_lows:
                return v
        norm_targets = {normalize_key(canonical)} | {normalize_key(a) for a in alias_set}
        for k, v in obj.items():
            if normalize_key(k) in norm_targets:
                return v
    return default


def _extract_balanced(text, open_ch, close_ch):
    """从首个 open_ch 起按括号深度 (识别字符串边界) 提取配平子串; 不配平 (截断) 返回 None。"""
    start = text.find(open_ch)
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return None


_FENCE_RE = re.compile(r"```[a-zA-Z]*\s*(.*?)```", re.DOTALL)


def json_loads_tolerant(text):
    """宽容 JSON 解析: 直接解析 → 剥代码围栏 → 提取最外层配平结构 → 去尾逗号放宽 → 截断抢救。
    返回 (obj|None, 诊断字符串)。成功时诊断为空串。"""
    if text is None:
        return None, "输入为 None"
    if not isinstance(text, str):
        try:
            json.dumps(text)
            return text, ""
        except Exception:
            return None, f"不可 JSON 序列化对象: {type(text).__name__}"
    s = text.strip()
    if not s:
        return None, "空字符串"
    steps = []
    try:
        return json.loads(s), ""
    except Exception as e1:
        steps.append(f"直接解析失败: {str(e1)[:80]}")
    # 剥代码围栏 (含未闭合围栏)
    candidates = []
    m = _FENCE_RE.search(s)
    if m:
        candidates.append(m.group(1).strip())
    if s.startswith("```"):
        body = s.split("\n", 1)[1] if "\n" in s else ""
        body = re.sub(r"```.*$", "", body, flags=re.DOTALL).strip()
        if body and body not in candidates:
            candidates.append(body)
    for cand in candidates:
        try:
            return json.loads(cand), ""
        except Exception as e2:
            steps.append(f"围栏内解析失败: {str(e2)[:80]}")
    base = candidates[0] if candidates else s
    # 提取最外层配平结构 ({ 优先于 [, 取最先出现者)
    i_obj, i_arr = base.find("{"), base.find("[")
    if i_obj == -1 and i_arr == -1:
        return None, "; ".join(steps + ["未找到 JSON 对象/数组"])
    if i_obj != -1 and (i_arr == -1 or i_obj < i_arr):
        o, c = "{", "}"
    else:
        o, c = "[", "]"
    cand2 = _extract_balanced(base, o, c)
    if cand2 is None:
        # 截断抢救: 从首个开括号截到最后一个闭括号
        first, last = base.find(o), base.rfind(c)
        if first != -1 and last > first:
            cand2 = base[first:last + 1]
    if cand2:
        try:
            return json.loads(cand2), ""
        except Exception as e3:
            steps.append(f"外层结构提取后解析失败: {str(e3)[:80]}")
        relaxed = re.sub(r",\s*([}\]])", r"\1", cand2)
        try:
            return json.loads(relaxed), ""
        except Exception as e4:
            steps.append(f"去尾逗号后仍失败: {str(e4)[:80]}")
    return None, "; ".join(steps)


# =====================================================================
# V16.2.0 批次1 §1.6 — 请求执行核心 (call_ai_ex / call_ai)
# =====================================================================
_RETRYABLE_CLASSES = ("RATE_LIMIT", "SERVER", "CONNECTION", "TIMEOUT", "UNKNOWN")
# 内容/配置级错误: 不触发跨级降级 (换端点解决不了内容问题与配置错误)
_TERMINAL_CLASSES = ("AUTH", "BAD_REQUEST", "PROTOCOL", "TRUNCATION")
# V16.2.0 互审修复 M-2/L-3: 计入降级阈值的失败类别 = 可重试类 + OVERFLOW
# (备用模型上下文可能更大, OVERFLOW 保留计数)。终端类失败换端点同样失败,
# 不计阈值 — 与 FAILURE_THRESHOLD 注释和 _TERMINAL_CLASSES 语义对齐。单一真相源。
_THRESHOLD_CLASSES = _RETRYABLE_CLASSES + ("OVERFLOW",)


def _request_once(step_url, opener, api_key, model_name, system_prompt, user_message,
                  temperature, max_tokens, timeout):
    """单次真实 HTTP 请求。返回 (kind, payload, http_code, err):
    kind ∈ ok(200且JSON解析成功, payload=解析结果) / json_broken(200但非JSON) /
           http_error(非200, payload=响应体片段) / conn_error(连接层, payload=原因)。"""
    try:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        payload = {
            "model": model_name or "default",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(step_url, data=data, headers=headers, method="POST")
        # V13.5: 禁重定向 opener (SSRF防护); V16.1.1: IP 钉扎 — 连接直连校验阶段解析的 IP
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            body = ""
        return "http_error", body, e.code, f"HTTP {e.code}: {body}"
    except urllib.error.URLError as e:
        reason = str(e.reason)[:100] if getattr(e, "reason", None) else "未知"
        return "conn_error", reason, None, f"连接失败: {reason}"
    except (socket.timeout, TimeoutError):
        return "conn_error", "timeout", None, "请求超时"
    except Exception as e:
        return "conn_error", str(e)[:100], None, f"错误: {str(e)[:100]}"
    try:
        return "ok", json.loads(raw), 200, ""
    except Exception:
        # V16.2.0 互审修复 L-5: 200 非裸 JSON 时先用宽容解析抢救
        # (如上游返回 ```json 围栏包裹的合法 JSON) — 解析成功按 OK 处置,
        # 失败才进截断流程。_interpret_200 仍会校验结构形态。
        rescued, _diag = json_loads_tolerant(raw)
        if rescued is not None:
            return "ok", rescued, 200, ""
        return "json_broken", raw[:200], 200, f"上游返回非JSON: {raw[:80]!r}"


def _execute_level(step, opener, system_prompt, user_message, temperature, max_tokens,
                   timeout, max_retries, meta):
    """执行单个链级: 退避重试 + 溢出两层压缩 + 截断拆分重试。返回 (text, err, err_class)。
    预算: 可重试失败最多 max_retries 次; 压缩与拆分重试另计 (硬上限 max_retries+4 次请求)。"""
    primary = meta.get("_primary") or step.get("url")
    orig_user = user_message
    cur_user = user_message
    compression_stage = 0
    split_retries = 0
    retryable_failures = 0
    total_requests = 0
    hard_cap = max_retries + 4
    last_err, last_class = "", "UNKNOWN"
    while total_requests < hard_cap:
        total_requests += 1
        kind, payload, code, err = _request_once(
            step.get("url"), opener, step.get("api_key"), step.get("model"),
            system_prompt, cur_user, temperature, max_tokens, timeout)
        if kind == "ok":
            text, verdict, detail = _interpret_200(payload)
            if verdict == "OK":
                meta["finish_reason"] = detail or None
                return text, "", "OK"
            if verdict == "TRUNCATED":
                if split_retries < 2:
                    split_retries += 1
                    meta["split_hint_retries"] = split_retries
                    cur_user = cur_user + _SPLIT_HINT.format(max_tokens=max_tokens)
                    _router_event(primary, "split_hint_retry", detail)
                    continue
                return "", f"上游截断诊断: {detail} (已注入拆分提示重试 {split_retries} 次仍被截断)", "TRUNCATION"
            return "", detail, "PROTOCOL"
        if kind == "json_broken":
            # HTTP 200 但非 JSON — 典型为输出中途被截断, 按截断流程处置
            if split_retries < 2:
                split_retries += 1
                meta["split_hint_retries"] = split_retries
                cur_user = cur_user + _SPLIT_HINT.format(max_tokens=max_tokens)
                _router_event(primary, "split_hint_retry", "json_broken")
                continue
            return "", f"上游截断诊断: 200 响应不是合法 JSON ({str(payload)[:60]!r}), 疑似输出被截断", "TRUNCATION"
        # 非 200 / 连接层错误
        cls = _classify_llm_failure(code, str(payload))
        meta["attempts"] = meta.get("attempts", 0) + 1
        if cls == "OVERFLOW":
            nxt = None
            if compression_stage == 0:
                nxt = compress_context_gentle(orig_user)
                if nxt is not None:
                    compression_stage = 1
                    meta["compression"] = "gentle"
            elif compression_stage == 1:
                nxt = compress_context_aggressive(orig_user)
                if nxt is not None:
                    compression_stage = 2
                    meta["compression"] = "aggressive"
            if nxt is not None:
                cur_user = nxt
                _router_event(primary, "overflow_compress", meta["compression"])
                continue
            return "", err + " (上下文溢出且输入已不可压缩)", "OVERFLOW"
        if cls in ("AUTH", "BAD_REQUEST"):
            return "", err, cls  # 配置级错误: 不重试不跳级, 诚实返回
        # 可重试类: 指数退避 + 抖动
        last_err, last_class = err, cls
        retryable_failures += 1
        if retryable_failures >= max_retries:
            return "", last_err, last_class
        _sleep((2 ** (retryable_failures - 1)) + random.uniform(0, 1))
    return "", last_err or "重试预算耗尽", last_class


def call_ai_ex(api_url, api_key, model_name, system_prompt, user_message, temperature, max_tokens,
               timeout=300, fallback_chain=None, max_retries_per_step=3, enable_recovery=True):
    """增强版 LLM 调用。返回 (result_text, error_text, meta)。

    meta 键: url/model (最终服务级), levels_tried, attempts, fallback_used, recovered,
             compression (None/gentle/aggressive), split_hint_retries, finish_reason, events。

    参数:
        timeout: 单次请求超时秒数。
        fallback_chain: 显式降级链 (None = 按 provider 预设自动构建)。
        max_retries_per_step: 每链级可重试失败上限。
        enable_recovery: False 时禁用自动降级链构建 (仅主调用)。
    """
    meta = {"url": api_url, "model": model_name, "levels_tried": 0, "attempts": 0,
            "fallback_used": False, "recovered": False, "compression": None,
            "split_hint_retries": 0, "finish_reason": None, "events": []}
    if not api_url:
        return "", "API地址为空", meta

    # [P3修复] URL协议校验，防止SSRF; V16.1.1 审计修复 M-2: 校验阶段选定安全IP候选
    valid, err_msg, _pinned_primary = _validate_api_url(api_url)
    if not valid:
        return "", err_msg, meta

    if fallback_chain is None:
        if enable_recovery:
            chain = build_fallback_chain(api_url, api_key, model_name)
        else:
            chain = [{"url": api_url, "model": model_name, "api_key": api_key, "source": "primary"}]
    else:
        chain = [dict(s) for s in fallback_chain if isinstance(s, dict) and s.get("url")]
        if not chain:
            chain = [{"url": api_url, "model": model_name, "api_key": api_key, "source": "primary"}]
    primary = chain[0].get("url") or api_url
    meta["_primary"] = primary

    # V13.5: 明文HTTP传密钥警告 (localhost 本地LLM除外)
    try:
        _p = urllib.parse.urlparse(api_url)
        if api_key and _p.scheme == "http" and _p.hostname not in ("127.0.0.1", "localhost", "::1"):
            sys.stderr.write(f"[DirectorMaster] 警告: API密钥经明文HTTP传输({_p.hostname}), 建议改用 https\n")
    except Exception:
        pass

    start_level, probe_mode = _router_begin(primary, len(chain))
    last_err = ""
    for level in range(start_level, len(chain)):
        step = chain[level]
        meta["levels_tried"] = level + 1
        # V16.2.0: 降级端点同样必须通过 SSRF 校验 (fail-closed, 与主端点同权)
        # 互审修复 L-8: level0 且 URL 与入口一致时复用入口已验证的安全候选 IP,
        # 不再二次 DNS 解析 (省去重复时延, 消除重校验窗口)
        if level == 0 and step.get("url") == api_url and _pinned_primary:
            valid_s, err_s, pinned_s = True, "", _pinned_primary
        else:
            valid_s, err_s, pinned_s = _validate_api_url(step.get("url"))
        if not valid_s:
            _router_event(primary, "level_skipped_ssrf", f"level{level}: {err_s}")
            meta["events"].append(f"level{level} SSRF校验失败已跳过: {err_s}")
            # 互审修复 M-1: level0 校验被跳过同样记一次主端点失败 —
            # 防止探测期校验瞬时失败绕过路由记录导致状态机滞留 probing
            if level == 0:
                _router_record_failure(primary, "CONNECTION")
            last_err = last_err or err_s
            continue
        opener = _pinned_opener(pinned_s)
        retries = 1 if (probe_mode and level == start_level) else max_retries_per_step
        text, err_l, cls = _execute_level(step, opener, system_prompt, user_message,
                                          temperature, max_tokens, timeout, retries, meta)
        if text and not err_l:
            if level == start_level and level == 0:
                prior = _router_record_success(primary)
                if prior in ("probing", "fallback_active"):
                    meta["recovered"] = True
            if level > 0:
                meta["fallback_used"] = True
                _router_event(primary, f"level{level}_served", str(step.get("model"))[:60])
            meta["url"] = step.get("url")
            meta["model"] = step.get("model")
            meta.pop("_primary", None)
            return text, "", meta
        # 本级失败
        if len(chain) > 1:
            # 互审修复 M-2: 仅阈值类失败 (可重试类 + OVERFLOW) 计入降级计数;
            # AUTH/BAD_REQUEST/PROTOCOL/TRUNCATION 换端点同样失败, 不计阈值
            if level == 0 and cls in _THRESHOLD_CLASSES:
                _router_record_failure(primary, cls)
            _router_event(primary, f"level{level}_failed", f"{cls}: {str(err_l)[:120]}")
        if cls in _TERMINAL_CLASSES:
            meta.pop("_primary", None)
            return "", err_l, meta  # 内容/配置级错误: 诚实报错, 不跨级
        last_err = err_l
    meta.pop("_primary", None)
    return "", last_err or "全部降级链级失败", meta


def call_ai(api_url, api_key, model_name, system_prompt, user_message, temperature, max_tokens,
            timeout=300, fallback_chain=None, max_retries_per_step=3, enable_recovery=True):
    """调用AI API（OpenAI兼容格式），带指数退避重试+抖动。
    V16.2.0: 增加三态降级状态机 / 溢出压缩 / 截断检测 / provider 预设降级链。
    保持 V16.1.1 的 7 位置参数签名完全向后兼容 (新参数均为关键字可选)。

    返回:
        tuple: (result_text, error_text)
            - 成功时: (结果文本, "")
            - 失败时: ("", 错误描述)
    """
    text, err, _meta = call_ai_ex(api_url, api_key, model_name, system_prompt, user_message,
                                  temperature, max_tokens, timeout=timeout,
                                  fallback_chain=fallback_chain,
                                  max_retries_per_step=max_retries_per_step,
                                  enable_recovery=enable_recovery)
    return text, err


def translate_prompt(text, direction, api_url, api_key, model_name, temperature, max_tokens):
    """翻译提示词"""
    if not text or not api_url:
        return ""

    prefixes = {
        "中译英": "将以下中文翻译成英文",
        "英译中": "将以下英文翻译成中文",
        "日译中": "将以下日文翻译成中文",
    }
    prefix = prefixes.get(direction, prefixes["中译英"])
    sys_p = "You are a professional translator. Output only the translated text."
    user_msg = f"{prefix}，只输出翻译结果：\n\n{text}"

    result, _ = call_ai(api_url, api_key, model_name, sys_p, user_msg, temperature, max_tokens)
    return result
