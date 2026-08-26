# ============================================================
# LLM 调用封装 — AI请求/翻译/重试
# ============================================================
import json
import socket
import ssl
import http.client
import ipaddress
import urllib.request
import urllib.error
import urllib.parse
import time as _time
import random


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
    """规范化 IP: 解包 IPv4-mapped IPv6 (::ffff:a9fe:a9fe → 169.254.169.254). 非法返回 None."""
    try:
        ip = ipaddress.ip_address(str(ip_str).strip().strip("[]").split("%")[0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            return ip.ipv4_mapped
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



def call_ai(api_url, api_key, model_name, system_prompt, user_message, temperature, max_tokens):
    """调用AI API（OpenAI兼容格式），带指数退避重试+抖动
    
    返回:
        tuple: (result_text, error_text)
            - 成功时: (结果文本, "")
            - 失败时: ("", 错误描述)
    """
    if not api_url:
        return "", "API地址为空"

    # [P3修复] URL协议校验，防止SSRF; V16.1.1 审计修复 M-2: 校验阶段选定安全IP候选, 连接直连这些IP
    valid, err_msg, pinned_ips = _validate_api_url(api_url)
    if not valid:
        return "", err_msg
    _opener = _pinned_opener(pinned_ips)

    last_error = ""
    # V13.5: 明文HTTP传密钥警告 (localhost 本地LLM除外)
    try:
        _p = urllib.parse.urlparse(api_url)
        if api_key and _p.scheme == "http" and _p.hostname not in ("127.0.0.1", "localhost", "::1"):
            import sys as _sw
            _sw.stderr.write(f"[DirectorMaster] 警告: API密钥经明文HTTP传输({_p.hostname}), 建议改用 https\n")
    except Exception:
        pass
    for attempt in range(3):
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

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
            # V13.5: 禁重定向 opener (SSRF防护); V16.1.1: IP 钉扎 — 连接直连校验阶段解析的 IP
            with _opener.open(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            if "choices" in result and isinstance(result["choices"], list) and len(result["choices"]) > 0:
                c = result["choices"][0]
                msg = c.get("message") if isinstance(c, dict) else None
                msg = msg if isinstance(msg, dict) else {}
                content = msg.get("content") or c.get("text") or ""
                content = content if isinstance(content, str) else str(content)
                return content.strip(), ""

            elif "response" in result:
                return str(result["response"]).strip(), ""

            return "", f"API格式异常: {str(result)[:200]}"

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_error = f"HTTP {e.code}: {body}"

            if e.code in (429, 502, 503, 504) and attempt < 2:
                # 指数退避 + 抖动
                delay = (2 ** attempt) + random.uniform(0, 1)
                _time.sleep(delay)
                continue
            return "", last_error

        except urllib.error.URLError as e:
            reason = str(e.reason)[:100] if e.reason else "未知"
            last_error = f"连接失败: {reason}"
            if attempt < 2:
                delay = (2 ** attempt) + random.uniform(0, 1)
                _time.sleep(delay)
                continue
            return "", last_error

        except Exception as e:
            last_error = f"错误: {str(e)[:100]}"
            if attempt < 2:
                _time.sleep(1)
                continue
            return "", last_error

    return "", last_error


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
