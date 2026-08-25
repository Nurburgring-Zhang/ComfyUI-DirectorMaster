# ============================================================
# 工具函数 — 文件扫描/过滤/解析/缓存/图片加载
# ============================================================
import os
import re
import random
import json
import threading
from datetime import datetime

import torch
import numpy as np
from PIL import Image


# [P2修复] 模块级锁 — 替代原来函数内每次新建的无效锁
_cache_lock = threading.Lock()

# 预编译正则表达式
_RE_SD_PARENS = re.compile(r'\(\([^)]*\)\)')
_RE_SD_BRACKETS = re.compile(r'\[\[[^\]]*\]\]')
_RE_SD_CURLY = re.compile(r'\{[^}]*\}')
_RE_CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
_RE_ASCII_ONLY = re.compile(r'[^\x00-\x7F]')
_RE_MULTISPACE = re.compile(r'\s+')

# 无生命关键词（用于智能过滤）
LIFELESS_KEYWORDS = [
    "产品", "商品", "静物", "物件", "物品", "陈列品",
    "食物", "菜肴", "菜品", "中餐", "西餐",
    "珠宝", "首饰", "戒指", "项链", "耳环",
    "家具", "沙发", "桌子", "椅子", "床", "柜子",
    "手机", "电脑", "显示器", "键盘", "鼠标",
    "汽车", "轿车", "鞋", "衣服", "服装",
    "花瓶", "杯子", "餐具",
    "化妆品", "护肤品", "口红", "香水",
    "product photo", "still life", "food photography",
]

# 白名单词（用于主体过滤）
WHITELIST_WORDS = [
    "人", "人物", "人像", "肖像", "女孩", "男孩", "女人", "男人",
    "美女", "帅哥", "少女", "仙女", "精灵", "天使",
    "公主", "王子", "女王", "国王", "骑士", "战士", "法师",
    "猫", "狗", "兔子", "鸟", "龙", "狮子", "老虎",
    "风景", "日落", "日出", "山脉", "海滩", "森林", "星空",
    "portrait", "woman", "man", "girl", "boy",
    "cat", "dog", "dragon", "lion", "tiger",
]

# 强主体信号（用于主体过滤器）
STRONG_SUBJECT_SIGNALS = {
    "少女", "少年", "女孩", "男孩", "女性", "男性", "女子", "男子",
    "女人", "男人", "模特", "人物", "人像", "肖像", "角色", "主角",
    "美女", "帅哥", "精灵", "天使", "公主", "王子", "女王", "国王",
    "新娘", "新郎", "婴儿", "孩童", "舞者", "歌手",
    "猫咪", "狗狗", "鸟儿", "兔子", "狐狸", "蝴蝶", "金鱼",
    "风景", "山水", "日落", "日出", "海滩", "森林", "山脉",
    "woman", "man", "girl", "boy", "portrait", "character",
    "cat", "dog", "bird", "dragon", "landscape", "sunset",
}


def parse_keywords(kw_str):
    """解析关键词字符串"""
    if not kw_str or not kw_str.strip():
        return []
    return [k.strip() for k in kw_str.split(",") if k.strip()]


def parse_tags(tag_str):
    """解析标签字符串"""
    if not tag_str or not tag_str.strip():
        return []
    return [t.strip() for t in tag_str.split(",") if t.strip()]


def scan_files(folder_path):
    """扫描文件夹中的提示词文件"""
    exts = (".txt", ".csv", ".md", ".jsonl")
    files = []
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file() and entry.name.lower().endswith(exts):
                files.append(entry.path)
    except (PermissionError, OSError):
        return []
    files.sort()
    return files


def file_has_tag(filepath, wanted_tags):
    """检查文件名是否包含标签"""
    fname = os.path.basename(filepath).lower()
    return any(tag.lower() in fname for tag in wanted_tags)


def load_lines(files, keywords, max_lines=0):
    """加载提示词文件中的所有行（兼容旧调用）"""
    return load_lines_cached(files, keywords, max_lines)


# [优化] 文件级缓存：基于 (path, mtime, size) 签名，避免重复磁盘 IO
_FILE_LINE_CACHE = {}
_FILE_CACHE_LOCK = threading.Lock()
_FILE_CACHE_MAX = 64  # 最多缓存 64 个文件


def _file_signature(fp):
    """生成文件签名 (mtime, size)，用于缓存失效检测"""
    try:
        st = os.stat(fp)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def _read_file_lines(fp):
    """读取文件全部清洗后的行（带缓存）"""
    sig = _file_signature(fp)
    if sig is None:
        return []
    cache_key = fp
    with _FILE_CACHE_LOCK:
        cached = _FILE_LINE_CACHE.get(cache_key)
        if cached and cached[0] == sig:
            return cached[1]
    # 真正读取
    MB = 50 * 1024 * 1024
    try:
        fsize = sig[1]
        if fsize > MB:
            raw = _stream_load(fp, 5000)
        else:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                raw = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    cleaned = []
    for line in raw:
        line = line.strip()
        if not line or line.startswith(("#", "//", "--")) or len(line) < 3:
            continue
        cleaned.append(line)
    # 写入缓存（LRU 简化：满了就清空）
    with _FILE_CACHE_LOCK:
        if len(_FILE_LINE_CACHE) >= _FILE_CACHE_MAX:
            _FILE_LINE_CACHE.clear()
        _FILE_LINE_CACHE[cache_key] = (sig, cleaned)
    return cleaned


def load_lines_cached(files, keywords, max_lines=0):
    """[优化] 加载提示词行 — 带文件级 mtime 缓存
    - 重复扫描相同文件 0 IO
    - 关键词过滤在缓存层之上做（缓存的是清洗后的全量行）
    """
    all_lines = []
    kws_lower = [kw.lower() for kw in (keywords or [])]
    for fp in files:
        cleaned = _read_file_lines(fp)
        for line in cleaned:
            if kws_lower and not any(kw in line.lower() for kw in kws_lower):
                continue
            all_lines.append({"text": line, "source": fp})
            if max_lines > 0 and len(all_lines) >= max_lines:
                return all_lines
    return all_lines


def compute_pool_signature(files):
    """计算文件池签名（用于检测目录是否变化，触发缓存失效）"""
    sigs = []
    for fp in files:
        s = _file_signature(fp)
        if s:
            sigs.append((fp, s[0], s[1]))
    return hash(tuple(sigs))


def _stream_load(fp, limit):
    """流式读取大文件前N行"""
    lines = []
    try:
        with open(fp, "r", encoding="utf-8", errors="replace") as f:
            for _ in range(limit):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
    except (OSError, UnicodeDecodeError):
        pass
    return lines


def smart_filter(lines):
    """智能过滤：保留有主体/非纯静物的行"""
    if not lines:
        return None
    filtered = []
    for entry in lines:
        text = entry["text"]
        has_subject = any(s in text for s in STRONG_SUBJECT_SIGNALS)
        if not has_subject:
            for body in ["长发", "短发", "手臂", "腿部", "站立", "行走",
                          "抚摸", "微笑", "凝视", "猫咪", "小狗"]:
                if body in text:
                    has_subject = True
                    break
            if not has_subject and "猫" in text and "猫粮" not in text:
                has_subject = True
        if has_subject:
            filtered.append(entry)
            continue
        if not any(kw in text for kw in LIFELESS_KEYWORDS):
            filtered.append(entry)
    if len(filtered) == len(lines):
        return None
    return filtered


def filter_by_subject(lines):
    """纯主体过滤"""
    if not lines:
        return []
    patterns = [
        "女性", "男性", "女人", "男人", "女孩", "男孩",
        "模特", "人物", "人像", "肖像", "角色", "主角",
        "美女", "帅哥", "精灵", "天使", "公主", "王子",
        "风景", "日落", "日出", "山脉", "海滩", "森林",
        "woman", "man", "girl", "boy", "portrait",
        "cat", "dog", "dragon", "landscape", "sunset",
    ]
    filtered = [e for e in lines if any(p in e["text"].lower() for p in patterns)]
    return filtered


def _make_rng(seed):
    """创建独立 RNG 实例。seed=0 表示真随机（基于时间+os）"""
    if seed and seed > 0:
        return random.Random(seed)
    # 真随机：用 os.urandom 提供高熵种子
    try:
        return random.Random(int.from_bytes(os.urandom(8), "big"))
    except Exception:
        return random.Random()


def _group_by_source(lines):
    """按 source 文件分组，用于「文件均衡」模式"""
    groups = {}
    for e in lines:
        groups.setdefault(e.get("source", ""), []).append(e)
    return groups


def pick_n_lines(lines, mode, loop_mode, count, folder_path, cache, seed=0):
    """从 lines 中选择 N 条。

    [深度优化版]
    - 独立 RNG（不污染全局 random），seed=0 真随机
    - 缓存自动失效（文件池签名变化时重置 idx/shuffled）
    - 批次内默认去重（一次抽 N 条互不重复，除非池子不够）
    - 完整支持的读取模式：
        随机抽取 / 顺序循环 / 洗牌遍历 / 权重随机 /
        等权随机 / 短文优先 / 长文优先 / 文件均衡
    - 完整支持的循环模式：
        无限循环 / 读完停止 / 历史不重复(50条) / 批次内不重复 / 重置循环位置

    参数:
        seed: 用户指定种子（>0 复现，=0 真随机）
    """
    if not lines:
        return [], cache

    cache_key = f"idx_{folder_path}"
    pool_sig = compute_pool_signature([e.get("source", "") for e in lines]) if lines else 0
    pool_sig_simple = hash(tuple(sorted(set(e["text"] for e in lines))))
    rng = _make_rng(seed)

    # 「重置循环位置」：清掉 idx/shuffled
    if loop_mode == "重置循环位置":
        with _cache_lock:
            cache.pop(cache_key, None)
            cache.pop(f"hist_{folder_path}", None)
        # 重置后按"无限循环+随机抽取"行为继续输出
        loop_mode = "无限循环"

    with _cache_lock:
        state = cache.get(cache_key, {})
        # 缓存签名校验：池变化则重置
        if state.get("pool_sig") != pool_sig_simple:
            state = {"pool_sig": pool_sig_simple}
        idx = state.get("idx", 0)
        shuffled_texts = state.get("shuffled_texts", None)

    chosen = []
    avail = list(lines)
    # 批次内不重复（默认开启）：除非用户明确选「无限循环」+「随机抽取」并允许重复
    batch_unique = True
    if loop_mode == "无限循环" and mode in ("随机抽取", "权重随机", "等权随机", "短文优先", "长文优先"):
        # 池子足够大时仍批次去重；池子比 count 小时允许重复
        batch_unique = len(avail) >= count

    def _pop(e):
        if batch_unique or loop_mode == "读完停止" or loop_mode == "历史不重复(50条)":
            try:
                avail.remove(e)
            except ValueError:
                pass

    if mode in ("随机抽取", "等权随机"):
        for _ in range(count):
            if not avail:
                break
            e = rng.choice(avail)
            chosen.append(e)
            _pop(e)

    elif mode == "顺序循环":
        for _ in range(count):
            if not avail:
                break
            chosen.append(avail[idx % len(avail)])
            idx += 1
            if loop_mode == "读完停止" and idx >= len(avail):
                break
        with _cache_lock:
            cache[cache_key] = {"idx": idx, "pool_sig": pool_sig_simple}

    elif mode == "洗牌遍历":
        # 用 text 作为持久化键（避免对象引用失效）
        text_to_entry = {e["text"]: e for e in avail}
        if shuffled_texts is None:
            shuffled_texts = list(text_to_entry.keys())
            rng.shuffle(shuffled_texts)
        # 过滤已不存在的条目
        shuffled_texts = [t for t in shuffled_texts if t in text_to_entry]
        for _ in range(count):
            if not shuffled_texts:
                if loop_mode == "读完停止":
                    break
                shuffled_texts = list(text_to_entry.keys())
                rng.shuffle(shuffled_texts)
            t = shuffled_texts.pop(0)
            chosen.append(text_to_entry[t])
        with _cache_lock:
            cache[cache_key] = {
                "idx": idx,
                "shuffled_texts": shuffled_texts,
                "pool_sig": pool_sig_simple,
            }

    elif mode == "权重随机":
        # 长文权重高（适合"信息密度"优先）
        weights = [max(len(e["text"]), 1) for e in avail]
        for _ in range(count):
            if not avail:
                break
            e = rng.choices(avail, weights=weights, k=1)[0]
            chosen.append(e)
            if batch_unique or loop_mode == "读完停止":
                i = avail.index(e)
                avail.pop(i)
                weights.pop(i)

    elif mode == "短文优先":
        # 短文本权重高（适合精炼标签优先）
        max_len = max((len(e["text"]) for e in avail), default=1)
        weights = [max(max_len - len(e["text"]) + 1, 1) for e in avail]
        for _ in range(count):
            if not avail:
                break
            e = rng.choices(avail, weights=weights, k=1)[0]
            chosen.append(e)
            if batch_unique or loop_mode == "读完停止":
                i = avail.index(e)
                avail.pop(i)
                weights.pop(i)

    elif mode == "长文优先":
        # 长文本极强权重（平方）
        weights = [max(len(e["text"]), 1) ** 2 for e in avail]
        for _ in range(count):
            if not avail:
                break
            e = rng.choices(avail, weights=weights, k=1)[0]
            chosen.append(e)
            if batch_unique or loop_mode == "读完停止":
                i = avail.index(e)
                avail.pop(i)
                weights.pop(i)

    elif mode == "文件均衡":
        # 跨文件均衡抽取：先轮询每个文件，再随机
        groups = _group_by_source(avail)
        file_keys = sorted(groups.keys())
        rng.shuffle(file_keys)
        # 轮询索引
        ptrs = {k: 0 for k in file_keys}
        i = 0
        guard = 0
        while len(chosen) < count and guard < count * len(file_keys) * 4:
            guard += 1
            if not file_keys:
                break
            k = file_keys[i % len(file_keys)]
            grp = groups.get(k, [])
            if grp:
                e = rng.choice(grp)
                chosen.append(e)
                if batch_unique or loop_mode == "读完停止":
                    grp.remove(e)
                    if not grp:
                        # 文件耗尽，移除
                        file_keys.remove(k)
                        i = max(0, i - 1)
            i += 1
        # 兜底：仍不足则全池随机补
        while len(chosen) < count and avail:
            remain = [e for e in avail if e not in chosen] if batch_unique else avail
            if not remain:
                break
            chosen.append(rng.choice(remain))

    else:
        # 未知模式 → 退化为随机抽取
        for _ in range(count):
            if not avail:
                break
            e = rng.choice(avail)
            chosen.append(e)
            _pop(e)

    return chosen, cache


def history_dedup(chosen, folder_path, cache, all_lines=None, seed=0, max_history=1000):
    """历史去重（默认1000条缓存）

    [深度优化]
    - 兜底逻辑：当 chosen 全部命中历史时，主动从 all_lines 中挑未历史条目补齐
    - 尽量保持 chosen 的长度与原请求一致（除非池子不足）
    - max_history: 历史保留上限（默认1000，远大于此前的50）
    """
    cache_key = f"hist_{folder_path}"
    rng = _make_rng(seed)
    target_n = len(chosen)
    with _cache_lock:
        hist = cache.get(cache_key, [])
        deduped = []
        used = set()
        for e in chosen:
            if e["text"] not in hist and e["text"] not in used:
                deduped.append(e)
                used.add(e["text"])
                hist.append(e["text"])
            if len(deduped) >= target_n:
                break
        # 兜底：还不够 → 从 all_lines 中找未历史/未本批的
        if all_lines is not None and len(deduped) < target_n:
            hist_set = set(hist)
            candidates = [e for e in all_lines if e["text"] not in hist_set and e["text"] not in used]
            rng.shuffle(candidates)
            for e in candidates:
                deduped.append(e)
                used.add(e["text"])
                hist.append(e["text"])
                if len(deduped) >= target_n:
                    break
        if len(hist) > max_history:
            hist = hist[-max_history:]
        cache[cache_key] = hist
    return deduped


def parse_ref_image_list(ref_list_str):
    """解析参考图列表JSON字符串"""
    if not ref_list_str or ref_list_str.strip() in ("", "[]"):
        return []
    try:
        items = json.loads(ref_list_str)
        if not isinstance(items, list):
            return []
        valid = []
        for item in items:
            if isinstance(item, dict) and "filename" in item:
                valid.append(item)
                if len(valid) >= 9:
                    break
        return valid
    except (json.JSONDecodeError, TypeError):
        return []


def load_ref_image_tensors(file_items):
    """从文件信息列表加载图片为IMAGE tensor，过滤>4096的"""
    if not file_items:
        return []
    tensors = []
    try:
        import folder_paths
        for item in file_items:
            try:
                filename = item.get("filename", "")
                subfolder = item.get("subfolder", "")
                img_type = item.get("type", "input")
                img_path = folder_paths.get_annotated_filepath(f"{filename} [input]")
                if not os.path.isfile(img_path):
                    input_dir = folder_paths.get_input_directory()
                    img_path = os.path.join(input_dir, filename)
                    if not os.path.isfile(img_path):
                        continue

                pil_img = Image.open(img_path).convert("RGB")
                w, h = pil_img.size
                if w > 4096 or h > 4096:
                    continue

                img_np = np.array(pil_img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np)[None,]  # (1, H, W, C)
                tensors.append(img_tensor)
                if len(tensors) >= 9:
                    break
            except Exception:
                continue
    except Exception:
        pass
    return tensors


def generate_negative_prompt(custom_negative, main_content):
    """生成负面提示词"""
    neg_base = [
        "ugly", "deformed", "blurry", "bad anatomy", "bad proportions",
        "extra limbs", "cloned face", "disfigured", "gross proportions",
        "malformed limbs", "missing arms", "missing legs", "extra arms",
        "extra legs", "fused fingers", "too many fingers", "long neck",
        "bad quality", "normal quality", "worst quality", "low quality",
        "lowres", "monochrome", "grayscale", "bad composition",
        "cropped", "watermark", "text", "signature", "logo", "nsfw",
    ]
    pos_text = (main_content or "").lower()
    if "hand" in pos_text or "手指" in pos_text or "手" in pos_text:
        neg_base.append("bad hands")
    if "face" in pos_text or "脸" in pos_text or "面部" in pos_text:
        neg_base.append("bad face")
    if "eye" in pos_text or "眼睛" in pos_text:
        neg_base.append("bad eyes")

    if custom_negative:
        custom = [c.strip() for c in custom_negative.split(",") if c.strip()]
        neg_base.extend(custom)

    seen = set()
    unique = []
    for n in neg_base:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return ", ".join(unique)


# ============================================================
# [深度优化] 历史落盘模块 — 按日期分卷的 JSONL 日志
# - 路径: <node_dir>/history_logs/YYYY-MM-DD.jsonl
# - 每行一条 JSON: {ts, date, output_id, batch_seq, folder, mode, loop, seed,
#                    index, text, source_file}
# - output_id 格式: YYYYMMDD_HHMMSS_<seed>_<batch_seq>_<index>
#   可作为"当天输出文件名"的稳定索引（与下游图片文件名对应）
# ============================================================

HISTORY_LOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "history_logs"
)
_LOG_LOCK = threading.Lock()
_LOG_DAILY_SEQ = {}  # {date_str: int} — 当天累计批次计数
_LOG_DAILY_SEQ_LOCK = threading.Lock()


def _today_str():
    return datetime.now().strftime("%Y-%m-%d")


def _today_log_path(date_str=None):
    if not date_str:
        date_str = _today_str()
    return os.path.join(HISTORY_LOG_DIR, f"{date_str}.jsonl")


def _next_batch_seq(date_str):
    """获取当天的下一个批次序号（从已有日志末尾恢复，避免重启清零）"""
    with _LOG_DAILY_SEQ_LOCK:
        if date_str in _LOG_DAILY_SEQ:
            _LOG_DAILY_SEQ[date_str] += 1
            return _LOG_DAILY_SEQ[date_str]
        # 首次访问：从磁盘恢复
        path = _today_log_path(date_str)
        last_seq = 0
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        try:
                            r = json.loads(line.strip())
                            seq = int(r.get("batch_seq", 0))
                            if seq > last_seq:
                                last_seq = seq
                        except Exception:
                            continue
            except OSError:
                pass
        _LOG_DAILY_SEQ[date_str] = last_seq + 1
        return _LOG_DAILY_SEQ[date_str]


def make_output_id(seed, batch_seq, index, ts=None):
    """生成稳定的输出索引 ID（与下游输出文件名可对应）

    格式: YYYYMMDD_HHMMSS_<seed>_<batch_seq>_<index>
    示例: 20260603_143022_42_7_1
    """
    if ts is None:
        ts = datetime.now()
    return "{date}_{seed}_{seq}_{idx}".format(
        date=ts.strftime("%Y%m%d_%H%M%S"),
        seed=int(seed) if seed else 0,
        seq=int(batch_seq),
        idx=int(index),
    )


def append_history_log(records):
    """把抽取记录追加到当天日志（线程安全 + 异常隔离）

    records: list[dict]，每个 dict 至少含 text；其他字段可由调用方注入
    返回写入的记录数
    """
    if not records:
        return 0
    try:
        with _LOG_LOCK:
            os.makedirs(HISTORY_LOG_DIR, exist_ok=True)
            path = _today_log_path()
            with open(path, "a", encoding="utf-8") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return len(records)
    except (OSError, TypeError, ValueError):
        return 0


def query_history_log(date_str=None, output_id=None, output_id_substr=None,
                      folder_path=None, text_substr=None, limit=200):
    """查询历史日志

    参数:
        date_str: YYYY-MM-DD，默认今天
        output_id: 精确匹配 output_id
        output_id_substr: output_id 子串匹配（用于按日期/seed/index 模糊查）
        folder_path: 精确匹配文件夹
        text_substr: 文本子串过滤
        limit: 最多返回多少条

    返回: list[dict]
    """
    if not date_str:
        date_str = _today_str()
    path = _today_log_path(date_str)
    if not os.path.isfile(path):
        return []
    results = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line.strip())
                except Exception:
                    continue
                if output_id and r.get("output_id") != output_id:
                    continue
                if output_id_substr and output_id_substr not in r.get("output_id", ""):
                    continue
                if folder_path and r.get("folder") != folder_path:
                    continue
                if text_substr and text_substr not in r.get("text", ""):
                    continue
                results.append(r)
                if len(results) >= limit:
                    break
    except OSError:
        return []
    return results


def list_history_dates():
    """列出已存在日志的所有日期（升序）"""
    if not os.path.isdir(HISTORY_LOG_DIR):
        return []
    dates = []
    try:
        for entry in os.scandir(HISTORY_LOG_DIR):
            if entry.is_file() and entry.name.endswith(".jsonl"):
                dates.append(entry.name[:-6])
    except OSError:
        return []
    dates.sort()
    return dates


def cleanup_old_logs(keep_days=90):
    """清理超过 keep_days 天的旧日志（可选维护）"""
    if not os.path.isdir(HISTORY_LOG_DIR):
        return 0
    today = datetime.now()
    removed = 0
    try:
        for entry in os.scandir(HISTORY_LOG_DIR):
            if not (entry.is_file() and entry.name.endswith(".jsonl")):
                continue
            try:
                d = datetime.strptime(entry.name[:-6], "%Y-%m-%d")
                if (today - d).days > keep_days:
                    os.remove(entry.path)
                    removed += 1
            except (ValueError, OSError):
                continue
    except OSError:
        return removed
    return removed
