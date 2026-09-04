# -*- coding: utf-8 -*-
"""
批次4 builder-m2 — dm_memory 检索 (aggregator/dm_memory/retrieval.py)
====================================================================
选型钉板 (设计 §2, 实测 2026-09-02): 检索主档 = WordFreqIndex (字符 bigram +
BM25 式 TF-IDF 打分, 纯 stdlib, 同输入同输出确定性, 中文友好, 离线零依赖);
嵌入档 = 可选 provider, 准入 = onnxruntime 可导入 且 环境变量 DM_EMBED_MODEL
指向本地存在的模型文件, 二者齐备才启用, 否则诚实降级并在 backend_status 标注
原因 — 绝不伪造语义向量, 绝不静默假装嵌入档存在。
双通道检索 (Toonflow"双嵌入"思想转译): 字面通道 (bigram BM25) + 结构键精确
过滤 (镜号/项目/状态)。
决策卡数据按存储布局数据层直读 <out_dir>/dm_memory/<safe_project>/cards.jsonl
(UTF-8 JSONL, 每行一 JSON 对象, 缺文件按空), 不 import m1 域模块。
"""
import json
import math
import os
import re
import sys
from abc import abstractmethod
from typing import Protocol

# 同源配方 + R1 MED-3/R2 MED-2 碰撞防护 (仅 dm_memory 层, version_store 不含此防护):
# ① 替换/strip/截断发生信息丢失, ② 安全名含 ASCII 字母 (NTFS 大小写折叠),
# ③ 以 ./空格结尾 (Windows 剥尾) — 任一命中即追加原名短 sha1 后缀 (sha1 基于原始
# raw, 确定性), 与写侧 (shot_cards/preference_store/procedure_memory 等) 同一映射。
def _safe_name(s):
    import hashlib
    raw = str(s or "")
    base = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "_", raw or "项目")
    safe = base.strip()[:40] or "项目"
    if ((safe != (raw or "项目")) or re.search(r"[A-Za-z]", safe)
            or safe[-1:] in (".", " ")):
        safe = safe + "_" + hashlib.sha1(
            raw.encode("utf-8", errors="replace")).hexdigest()[:8]
    return safe


# 结构键 (设计 §1 钉死: 镜号/项目/状态) + 决策卡英文键别名互通
_STRUCT_ALIASES = {
    "镜号": ("镜号", "shot", "shot_no", "shot_id"),
    "项目": ("项目", "project"),
    "状态": ("状态", "status"),
}
_ALL_STRUCT_KEYS = frozenset(k for keys in _STRUCT_ALIASES.values() for k in keys) | {
    "card_id", "doc_id", "id"}

_RUN_RE = re.compile(r"[A-Za-z0-9]+|[\u3400-\u4dbf\u4e00-\u9fff]+")


def _struct_of(doc):
    out = {}
    for canon, keys in _STRUCT_ALIASES.items():
        for k in keys:
            v = doc.get(k)
            if v is not None and str(v).strip():
                out[canon] = str(v)
                break
    return out


def _doc_text(doc):
    # 字面通道文本 = 字符串值拼接 (排除结构键与 id 键, 双通道分离)
    return " ".join(str(v) for k, v in doc.items()
                    if isinstance(v, str) and v.strip() and k not in _ALL_STRUCT_KEYS)


def _tokenize(text):
    """ASCII 词元 (小写) + CJK 字符 bigram (单字 run 保留一元)。确定性。"""
    toks = []
    for m in _RUN_RE.finditer(str(text or "")):
        run = m.group(0)
        if run.isascii():
            toks.append(run.lower())
        elif len(run) == 1:
            toks.append(run)
        else:
            toks.extend(run[i:i + 2] for i in range(len(run) - 1))
    return toks


def _apply_struct_filter(structs, filters):
    if not filters:
        return list(range(len(structs)))
    norm = {}
    for k, v in dict(filters).items():
        canon = next((c for c, keys in _STRUCT_ALIASES.items() if k in keys), None)
        if canon is None:
            raise ValueError(f"不支持的结构过滤键: {k} (仅限 镜号/项目/状态)")
        norm[canon] = str(v)
    return [i for i, st in enumerate(structs)
            if all(st.get(c) == val for c, val in norm.items())]


def cards_path(out_dir, project):
    # 存储布局 (设计 §3): <out_dir>/dm_memory/<safe_project>/cards.jsonl — m1 写, 本模块读
    return os.path.join(str(out_dir), "dm_memory", _safe_name(project), "cards.jsonl")


def _looks_like_card(obj):
    """幽灵卡软过滤 (R2 LOW-1): errors="replace" 可把二进制坏行"修复"成合法 JSON,
    这类行缺卡片标识字段 — 与 shot_cards 同口径: 至少含 signal/标题/title/card_id
    之一才建索引 (防止 U+FFFD 键的坏行入检索)。"""
    return any(k in obj for k in ("signal", "标题", "title", "card_id"))


def load_cards(out_dir, project):
    """数据层直读决策卡 (UTF-8 JSONL): 缺文件按空, 坏行/空行诚实跳过。
    二进制容错 (R1 MED-2): 非法 UTF-8 字节行降级为占位后走 json 跳过逻辑 —
    损坏行跳过、合法行照常消费, 建索引路径不被损坏锁死。
    幽灵卡软过滤 (R2 LOW-1): decode 后恰为合法 JSON 的坏行 (缺卡片标识字段) 跳过
    并 stderr 告警计数, 不进检索索引。"""
    path = cards_path(out_dir, project)
    if not os.path.isfile(path):
        return []
    cards = []
    ghosts = 0
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            if not _looks_like_card(obj):  # 幽灵卡: 缺 signal/标题/title/card_id 之一
                ghosts += 1
                continue
            cards.append(obj)
    if ghosts:
        try:
            sys.stderr.write(
                f"[DirectorMaster] cards.jsonl 有 {ghosts} 行疑似幽灵卡 (缺卡片标识字段), "
                f"已跳过: {path}\n")
        except Exception:
            pass
    return cards


class MemoryIndex(Protocol):
    """检索索引协议 (设计 §1 钉死: add/query 双方法)。"""

    @abstractmethod
    def add(self, doc: dict) -> str: ...
    @abstractmethod
    def query(self, text: str, filters: dict | None = None, top_k: int = 5) -> list[dict]: ...


class WordFreqIndex:
    """检索主档: 字符 bigram + BM25 式 TF-IDF (k1=1.5, b=0.75), 纯 stdlib 确定性。
    query 命中形状: {"doc_id", "score", "doc"(原卡)} — 注入段可直接取原文。"""

    _K1 = 1.5
    _B = 0.75

    def __init__(self):
        self._docs = []   # {"id", "doc", "struct", "tf", "len"}
        self._df = {}     # token -> 出现该词元的文档数

    def add(self, doc):
        if not isinstance(doc, dict):
            raise ValueError("add(doc) 需为 dict")
        doc_id = str(doc.get("card_id") or doc.get("doc_id") or doc.get("id")
                     or f"doc_{len(self._docs)}")
        toks = _tokenize(_doc_text(doc))
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        self._docs.append({"id": doc_id, "doc": dict(doc), "struct": _struct_of(doc),
                           "tf": tf, "len": len(toks)})
        for t in tf:
            self._df[t] = self._df.get(t, 0) + 1
        return doc_id

    def _score(self, q_toks, d, avgdl):
        n = len(self._docs)
        score = 0.0
        for t in q_toks:
            f = d["tf"].get(t)
            if not f:
                continue
            df = self._df.get(t, 0)
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            dl_norm = (d["len"] / avgdl) if avgdl > 0 else 0.0
            score += idf * (f * (self._K1 + 1.0)) / (
                f + self._K1 * (1.0 - self._B + self._B * dl_norm))
        return score

    def query(self, text, filters=None, top_k=5):
        cands = _apply_struct_filter([d["struct"] for d in self._docs], filters)
        q_toks = _tokenize(text)
        if q_toks:
            n = len(self._docs)
            avgdl = (sum(d["len"] for d in self._docs) / n) if n else 0.0
            hits = []
            for i in cands:
                s = self._score(q_toks, self._docs[i], avgdl)
                if s > 0.0:
                    hits.append((i, s))
        else:
            hits = [(i, 0.0) for i in cands]
        hits.sort(key=lambda x: (-x[1], x[0]))  # 分数降序, 同分按入库序 — 确定性
        out = []
        for i, s in hits[: max(0, int(top_k))]:
            d = self._docs[i]
            out.append({"doc_id": d["id"], "score": round(s, 6), "doc": dict(d["doc"])})
        return out


class OnnxEmbedIndex:
    """嵌入档 (非默认路径): 本地 ONNX 模型真实推理产生句向量, 余弦排序。
    诚实前置: 模型文件旁必须存在 vocab.txt (BERT 词表) 才能确定性分词 —
    缺失即构造失败 (由 make_index 诚实降级), 绝不用伪造分词/伪向量充数。"""

    MAX_SEQ = 512

    def __init__(self, model_path):
        import numpy as np  # onnxruntime 伴随依赖, 仅本非默认路径触达
        import onnxruntime as ort  # 惰性 import (选型钉板: 不在默认路径)
        self._np = np
        vocab_path = os.path.join(os.path.dirname(os.path.abspath(model_path)), "vocab.txt")
        if not os.path.isfile(vocab_path):
            raise RuntimeError(f"嵌入模型旁缺少 vocab.txt, 无法诚实分词: {vocab_path}")
        self._vocab = {}
        with open(vocab_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                tok = line.rstrip("\n")
                if tok and tok not in self._vocab:
                    self._vocab[tok] = i
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        self._sess = ort.InferenceSession(model_path, sess_options=opts,
                                          providers=["CPUExecutionProvider"])
        self._in_names = {x.name for x in self._sess.get_inputs()}
        extra = self._in_names - {"input_ids", "attention_mask", "token_type_ids"}
        if extra:
            raise RuntimeError(f"嵌入模型输入超出可诚实构造范围: {sorted(extra)}")
        self._out_name = self._sess.get_outputs()[0].name
        self._ids, self._docs, self._structs, self._vecs = [], [], [], []
        self._embed("dm_memory 嵌入档构造自检")  # 构造期真实推理, 失败即诚实构造失败

    def _wordpiece(self, word, unk):
        v = self._vocab
        if word in v:
            return [v[word]]
        out, start = [], 0
        while start < len(word):
            end, pick = len(word), None
            while end > start:
                cand = word[start:end] if start == 0 else "##" + word[start:end]
                if cand in v:
                    pick, start = v[cand], end
                    break
                end -= 1
            if pick is None:
                return [unk]
            out.append(pick)
        return out

    def _encode(self, text):
        unk = self._vocab.get("[UNK]", 0)
        cls, sep = self._vocab.get("[CLS]", unk), self._vocab.get("[SEP]", unk)
        pieces = []
        for m in _RUN_RE.finditer(str(text or "")):
            word = m.group(0).lower() if m.group(0).isascii() else m.group(0)
            pieces.extend(self._wordpiece(word, unk))
            if len(pieces) >= self.MAX_SEQ - 2:
                break
        pieces = pieces[: self.MAX_SEQ - 2]
        return [cls] + pieces + [sep], [1] * (len(pieces) + 2)

    def _embed(self, text):
        np = self._np
        ids, mask = self._encode(text)
        feed = {}
        if "input_ids" in self._in_names:
            feed["input_ids"] = np.asarray([ids], dtype=np.int64)
        if "attention_mask" in self._in_names:
            feed["attention_mask"] = np.asarray([mask], dtype=np.int64)
        if "token_type_ids" in self._in_names:
            feed["token_type_ids"] = np.zeros((1, len(ids)), dtype=np.int64)
        out = np.asarray(self._sess.run([self._out_name], feed)[0], dtype=np.float64)
        if out.ndim == 3:  # (batch, seq, hidden) → mask 平均池化
            m = np.asarray(mask, dtype=np.float64)[None, :, None]
            pooled = (out * m).sum(axis=1) / max(float(m.sum()), 1e-9)
            vec = pooled[0]
        elif out.ndim == 2:
            vec = out[0]
        else:
            raise RuntimeError(f"嵌入模型输出形状不可解释: {out.shape}")
        norm = float((vec * vec).sum() ** 0.5) or 1.0
        return [float(x / norm) for x in vec]

    def add(self, doc):
        if not isinstance(doc, dict):
            raise ValueError("add(doc) 需为 dict")
        doc_id = str(doc.get("card_id") or doc.get("doc_id") or doc.get("id")
                     or f"doc_{len(self._docs)}")
        self._docs.append(dict(doc))
        self._structs.append(_struct_of(doc))
        self._vecs.append(self._embed(_doc_text(doc)))
        self._ids.append(doc_id)
        return doc_id

    def query(self, text, filters=None, top_k=5):
        cands = _apply_struct_filter(self._structs, filters)
        if str(text or "").strip():
            q = self._embed(str(text))
            scored = [(i, float(sum(a * b for a, b in zip(q, self._vecs[i]))))
                      for i in cands]
        else:
            scored = [(i, 0.0) for i in cands]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [{"doc_id": self._ids[i], "score": round(s, 6), "doc": dict(self._docs[i])}
                for i, s in scored[: max(0, int(top_k))]]


def _probe_embedding():
    """嵌入档准入探测: onnxruntime 可导入 且 DM_EMBED_MODEL 指向存在的本地模型文件。
    返回 (info|None, 不可用原因) — 任一条件不满足即 None, 绝不伪造探测结果。"""
    model = os.environ.get("DM_EMBED_MODEL", "").strip()
    if not model:
        return None, "环境变量 DM_EMBED_MODEL 未设置"
    if not os.path.isfile(model):
        return None, f"环境变量 DM_EMBED_MODEL 指向的文件不存在: {model}"
    try:
        import onnxruntime  # 惰性 import — 仅探测, 不在默认路径
    except Exception as e:
        return None, f"onnxruntime 不可导入: {type(e).__name__}"
    return {"runtime": "onnxruntime", "model": model,
            "runtime_version": str(getattr(onnxruntime, "__version__", "") or "")}, ""


def detect_embedding_provider():
    """嵌入 provider 探测: 二条件齐备返回 dict, 任一不满足返回 None。"""
    info, _ = _probe_embedding()
    return info


def make_index(prefer_embedding=False):
    """选型入口 -> (index, backend_status)。
    backend_status ∈ {"wordfreq", "onnx:<model>",
                      "wordfreq (embedding unavailable: <reason>)"} — 如实标注。"""
    if not prefer_embedding:
        return WordFreqIndex(), "wordfreq"
    info, reason = _probe_embedding()
    if info is not None:
        try:
            return OnnxEmbedIndex(info["model"]), f"onnx:{info['model']}"
        except Exception as e:
            return WordFreqIndex(), (f"wordfreq (embedding unavailable: "
                                     f"嵌入档初始化失败: {type(e).__name__}: {e})")
    return WordFreqIndex(), f"wordfreq (embedding unavailable: {reason})"
