# -*- coding: utf-8 -*-
"""
tools/sync_mode_index.py — 模式卡目录校验 + 索引生成 (V16.3.0 批次2 / 设计 §3)
==============================================================================
零第三方依赖 (仅 stdlib); frontmatter 手写解析, 禁 yaml。

卡目录映射 (固定 10 目录 ↔ 10 个有模式下拉的注册节点):
  script→DirectorMasterScript      cinematic→DirectorMasterCinematic
  vibe→DirectorMasterVibe          art→DirectorMasterArt
  sound→DirectorMasterSound        characters→DirectorMasterCharacters
  asset→DirectorMasterAsset        router→DirectorMasterRouter
  video_router→DirectorMasterVideoRouter
  archive→DirectorMasterArchive

扫描 knowledge_base/mode_cards/<slug>/*.md; 根下 SCHEMA.md/_TEMPLATE.md/INDEX.md/index.json
不算卡, 其余根级 md/json 文件 = 违例 (卡必须位于 <slug>/ 子目录)。

校验 (违例逐条列出, 有违例 exit 1):
  · frontmatter 可解析 + 必填字段齐全 (mode_id/node/name/one_liner/applicable/intensity/style_tags;
    aliases 可空); 未知键 = 违例 (键集封闭, 见 SCHEMA.md)
  · mode_id 全局唯一且 ascii-kebab
  · name ∈ 该节点 manifest.creative 逐字匹配 (对账基准 tests/mode_manifest.json)
  · node ∈ 目录映射表; 卡放错目录 (frontmatter node != 目录归属) = 违例
  · 孤儿卡 (node/name 不在 manifest) 与缺卡 (manifest 有枚举无卡文件) 都硬失败
  · intensity ∈ low|medium|high|adaptive

产出 (确定性: 固定节点顺序 + mode_id 排序, 无时间戳):
  knowledge_base/mode_cards/INDEX.md  (按节点表: mode_id|name|one_liner|intensity|style_tags)
  knowledge_base/mode_cards/index.json ({"total":N,"nodes":{<节点>:{"count":n,"mode_ids":[...]}}})

模式:
  python tools/sync_mode_index.py                       # 全量校验 + 写 INDEX.md/index.json
  python tools/sync_mode_index.py --check --root <repo> # 只验不写 + 现有索引逐字节漂移比对 (漂移 exit 1)
  python tools/sync_mode_index.py --node <Node> (可重复) # 子集校验 (缺卡检查限定该节点), 不写索引
  --schema <p> / --template <p>                          # 文档自检路径覆盖 (默认标准路径):
                                                         #   SCHEMA 文档化全部必填键;
                                                         #   _TEMPLATE 演示 frontmatter 能被自身规则解析
退出码: 0 = 通过 / 1 = 有违例或漂移。
"""
import argparse
import json
import os
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)

# 卡目录 slug → 注册节点 (顺序固定, 供 INDEX/index.json 确定性输出)
CATALOG = {
    "script": "DirectorMasterScript",
    "cinematic": "DirectorMasterCinematic",
    "vibe": "DirectorMasterVibe",
    "art": "DirectorMasterArt",
    "sound": "DirectorMasterSound",
    "characters": "DirectorMasterCharacters",
    "asset": "DirectorMasterAsset",
    "router": "DirectorMasterRouter",
    "video_router": "DirectorMasterVideoRouter",
    "archive": "DirectorMasterArchive",
}
NODE_TO_SLUG = {v: k for k, v in CATALOG.items()}

ROOT_ARTIFACTS = {"SCHEMA.md", "_TEMPLATE.md", "INDEX.md", "index.json"}
REQUIRED_KEYS = ("mode_id", "node", "name", "one_liner", "applicable", "intensity", "style_tags")
OPTIONAL_KEYS = ("aliases",)
KNOWN_KEYS = set(REQUIRED_KEYS) | set(OPTIONAL_KEYS)
INTENSITY_VALUES = ("low", "medium", "high", "adaptive")
MODE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ONE_LINER_MAX = 40          # SCHEMA.md 口径; 超长记 advisory (writer 纪律, 非硬门)
BODY_H2_SECTIONS = ("意图", "核心手法", "参数表", "已知坑", "节点映射")
PARAM_ROWS_WITH_ARGS = 3    # 有参模式参数表数据行下限
PARAM_ROWS_NO_ARGS = 2      # 无参模式覆盖节点级共享参数下限


class CardFormatError(Exception):
    """单卡 frontmatter 结构性不可解析。"""


# ---------------------------------------------------------------- frontmatter 手写解析
def _strip_quotes(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("\"", "'"):
        return s[1:-1]
    return s


def _split_inline_list(inner):
    """按顶层逗号切内联列表项 (跟踪 []/() 深度与引号)。"""
    items, buf, depth, quote = [], [], 0, None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("\"", "'"):
            quote = ch
            buf.append(ch)
        elif ch in "[(":
            depth += 1
            buf.append(ch)
        elif ch in "])":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "," and depth == 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        items.append("".join(buf))
    return items


def _parse_value(raw):
    """标量逐字 (去引号) / 内联列表 [a, b] / 空 → ""。"""
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_strip_quotes(x.strip()) for x in _split_inline_list(inner)]
    return _strip_quotes(s)


def parse_frontmatter(text, origin):
    """手写 frontmatter 解析: 首行 --- 起, 下一条 --- 止; 之后为正文。

    返回 (fields: dict, body: str)。结构不符 → CardFormatError (调用方计违例)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise CardFormatError(f"{origin}: 缺 frontmatter (文件须以 --- 开头)")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise CardFormatError(f"{origin}: frontmatter 未闭合 (缺第二条 ---)")
    fields = {}
    for ln in lines[1:end]:
        if not ln.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", ln)
        if not m:
            raise CardFormatError(f"{origin}: frontmatter 行无法解析: {ln.strip()!r}")
        fields[m.group(1)] = _parse_value(m.group(2))
    body = "\n".join(lines[end + 1:])
    return fields, body


def extract_demo_frontmatter(text):
    """提取文档中第一个演示 frontmatter 块 (--- ... --- 且含 mode_id:) — 供 _TEMPLATE 自检。"""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() != "---":
            continue
        block = []
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == "---":
                if any(l.startswith("mode_id:") for l in block):
                    return block
                break
            block.append(lines[j])
    return None


# ---------------------------------------------------------------- 卡收集与校验
def _is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, list):
        return len(v) == 0 or any(not str(x).strip() for x in v)
    return False


def collect_card_files(cards_root, violations):
    """返回 [(slug, path)]; 同时登记目录级违例 (未知目录/根级未登记文件)。"""
    cards = []
    if not os.path.isdir(cards_root):
        violations.append(f"卡目录不存在: {cards_root} (knowledge_base/mode_cards)")
        return cards
    for name in sorted(os.listdir(cards_root)):
        p = os.path.join(cards_root, name)
        if os.path.isfile(p):
            if name in ROOT_ARTIFACTS:
                continue
            if name.lower().endswith((".md", ".json")):
                violations.append(f"根目录未登记文件 (卡必须位于 <slug>/ 子目录): {name}")
            continue
        if name not in CATALOG:
            has_md = any(f.lower().endswith(".md") for f in os.listdir(p)
                         if os.path.isfile(os.path.join(p, f)))
            if has_md:
                violations.append(f"未知卡目录 slug '{name}' (不在目录映射表: "
                                  f"{', '.join(sorted(CATALOG))})")
            continue
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            if os.path.isfile(fp) and f.lower().endswith(".md"):
                cards.append((name, fp))
    return cards


def validate_card(slug, path, manifest_nodes, violations, advisories,
                  seen_mode_ids, seen_node_name):
    """校验单卡 frontmatter 与正文红线; 返回规范化卡 dict (违例卡返回 None)。"""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        violations.append(f"{path}: 读取失败 {e!r}")
        return None
    try:
        fields, body = parse_frontmatter(text, path)
    except CardFormatError as e:
        violations.append(str(e))
        return None

    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    ok = True
    # 键集封闭 + 必填齐全
    unknown = sorted(set(fields) - KNOWN_KEYS)
    if unknown:
        violations.append(f"{rel}: 未知 frontmatter 键 {unknown} (键集封闭, 见 SCHEMA.md)")
        ok = False
    for k in REQUIRED_KEYS:
        if k not in fields:
            violations.append(f"{rel}: 缺必填字段 {k}")
            ok = False
        elif _is_empty(fields[k]):
            violations.append(f"{rel}: 必填字段 {k} 为空")
            ok = False
    if not ok:
        return None

    mode_id, node, name = fields["mode_id"], fields["node"], fields["name"]
    one_liner = fields["one_liner"]
    applicable = fields["applicable"]
    intensity = fields["intensity"]
    style_tags = fields["style_tags"]

    # mode_id: ascii-kebab + 全局唯一
    if not isinstance(mode_id, str) or not MODE_ID_RE.match(mode_id):
        violations.append(f"{rel}: mode_id '{mode_id}' 不符合 ascii-kebab "
                          f"(^[a-z0-9]+(-[a-z0-9]+)*$)")
        ok = False
    if mode_id in seen_mode_ids:
        violations.append(f"{rel}: mode_id '{mode_id}' 全局重复 (已在 "
                          f"{seen_mode_ids[mode_id]})")
        ok = False
    else:
        seen_mode_ids[mode_id] = rel

    # node: ∈ 目录映射表 + 卡放对目录
    if node not in NODE_TO_SLUG:
        violations.append(f"{rel}: node '{node}' 不在目录映射表 ({len(CATALOG)} 个注册节点)")
        ok = False
    elif NODE_TO_SLUG[node] != slug:
        violations.append(f"{rel}: 卡放错目录 — frontmatter node='{node}' 应位于 "
                          f"{NODE_TO_SLUG[node]}/, 实际在 {slug}/")
        ok = False

    # intensity 枚举
    if intensity not in INTENSITY_VALUES:
        violations.append(f"{rel}: intensity '{intensity}' 不在 "
                          f"{list(INTENSITY_VALUES)}")
        ok = False

    # name: ∈ 该节点 manifest.creative 逐字匹配 → 否则孤儿卡
    mnode = manifest_nodes.get(node) if isinstance(manifest_nodes, dict) else None
    creative = mnode.get("creative", []) if isinstance(mnode, dict) else []
    if (node, name) in seen_node_name:
        violations.append(f"{rel}: (node,name)=('{node}','{name}') 重复卡 "
                          f"(已在 {seen_node_name[(node, name)]})")
        ok = False
    else:
        seen_node_name[(node, name)] = rel
    if node in manifest_nodes and name not in creative:
        violations.append(f"{rel}: 孤儿卡 — ('{node}', '{name}') 不在 manifest.creative 枚举 "
                          f"(逐字匹配失败; 若确属新选项须先重跑 tools/dump_mode_manifest.py)")
        ok = False
    elif node not in manifest_nodes:
        violations.append(f"{rel}: 孤儿卡 — node '{node}' 不在 manifest.nodes 中")
        ok = False

    # 正文红线 (advisory 级: WaveC 互审硬审, sync 不越权硬拦)
    h2 = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("## ")]
    missing_sections = [s for s in BODY_H2_SECTIONS if f"## {s}" not in h2]
    if missing_sections:
        advisories.append(f"{rel}: 正文缺 H2 节 {missing_sections} (质量红线, 拒收级)")
    param_rows = _count_param_rows(body)
    need = PARAM_ROWS_NO_ARGS if "## 参数表" in h2 and param_rows == 0 else PARAM_ROWS_WITH_ARGS
    if "## 参数表" in h2 and param_rows < need:
        advisories.append(f"{rel}: 参数表数据行 {param_rows} < 下限 {need} "
                          f"(有参≥{PARAM_ROWS_WITH_ARGS} / 无参≥{PARAM_ROWS_NO_ARGS})")
    if isinstance(one_liner, str) and len(one_liner) > ONE_LINER_MAX:
        advisories.append(f"{rel}: one_liner {len(one_liner)} 字 > {ONE_LINER_MAX} (SCHEMA 口径)")
    for cell in ([one_liner] + list(style_tags) + list(applicable)):
        if isinstance(cell, str) and "|" in cell:
            advisories.append(f"{rel}: 字段值含 '|' (INDEX 表格列将转义渲染): {cell[:30]}")

    if not ok:
        return None
    return {"slug": slug, "path": rel, "mode_id": mode_id, "node": node, "name": name,
            "one_liner": one_liner, "intensity": intensity,
            "style_tags": list(style_tags), "applicable": list(applicable),
            "aliases": list(fields.get("aliases") or [])}


def _count_param_rows(body):
    """## 参数表 节内的表格数据行数 (排除表头与分隔行)。"""
    rows = 0
    in_sec = False
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            if in_sec:
                break
            in_sec = (s == "## 参数表")
            continue
        if in_sec and s.startswith("|"):
            core = s.strip("|").strip()
            if core and not re.match(r"^[-: ]+$", core):
                rows += 1
    return max(0, rows - 1)  # 减表头行


# ---------------------------------------------------------------- 索引产出 (确定性)
def _md_cell(s):
    return str(s).replace("|", "\\|")


def build_index_md(cards, total_creative):
    lines = [
        "# DirectorMaster 模式卡索引",
        "",
        "> 自动生成: tools/sync_mode_index.py — 勿手改。重新生成: `python tools/sync_mode_index.py`",
        f"> 对账基准: tests/mode_manifest.json (total_creative={total_creative})",
        "",
    ]
    for slug, node in CATALOG.items():
        node_cards = sorted([c for c in cards if c["node"] == node], key=lambda c: c["mode_id"])
        have = len(node_cards)
        expect = len(node_cards)  # 完整索引在通过校验后生成, 缺卡不会走到这里
        lines.append(f"## {node} (目录: {slug}) — 卡 {have}/{expect}")
        lines.append("")
        lines.append("| mode_id | name | one_liner | intensity | style_tags |")
        lines.append("|---|---|---|---|---|")
        for c in node_cards:
            lines.append("| " + " | ".join([
                _md_cell(c["mode_id"]), _md_cell(c["name"]), _md_cell(c["one_liner"]),
                _md_cell(c["intensity"]), _md_cell(", ".join(c["style_tags"])),
            ]) + " |")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def build_index_json(cards, total_creative):
    nodes = {}
    for slug, node in CATALOG.items():
        ids = sorted(c["mode_id"] for c in cards if c["node"] == node)
        nodes[node] = {"count": len(ids), "mode_ids": ids}
    doc = {"total": len(cards), "nodes": nodes, "total_creative": total_creative}
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


# ---------------------------------------------------------------- 校验主流程
def load_manifest(manifest_path, violations):
    if not os.path.exists(manifest_path):
        violations.append(f"对账基准缺失: {manifest_path} "
                          f"(先运行 python tools/dump_mode_manifest.py 生成)")
        return None
    try:
        with open(manifest_path, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as e:
        violations.append(f"manifest 解析失败: {manifest_path}: {e!r}")
        return None
    if m.get("version") != 1 or not isinstance(m.get("nodes"), dict):
        violations.append(f"manifest 结构异常 (version/nodes): {manifest_path}")
        return None
    return m


def selfcheck_docs(schema_path, template_path):
    """文档件自检: SCHEMA 文档化全部必填键; _TEMPLATE 演示块能被自身 frontmatter 规则解析。"""
    problems = []
    schema_text = template_text = None
    if not os.path.isfile(schema_path) or os.path.getsize(schema_path) == 0:
        problems.append(f"SCHEMA 文件缺失或为空: {schema_path}")
    else:
        with open(schema_path, encoding="utf-8") as f:
            schema_text = f.read()
    if not os.path.isfile(template_path) or os.path.getsize(template_path) == 0:
        problems.append(f"TEMPLATE 文件缺失或为空: {template_path}")
    else:
        with open(template_path, encoding="utf-8") as f:
            template_text = f.read()
    if schema_text is not None:
        for k in REQUIRED_KEYS:
            if k not in schema_text:
                problems.append(f"SCHEMA.md 未文档化必填字段 '{k}'")
    if template_text is not None:
        demo = extract_demo_frontmatter(template_text)
        if demo is None:
            problems.append("_TEMPLATE.md 未找到演示 frontmatter 块 (--- mode_id: ... ---)")
        else:
            keys = set()
            for ln in demo:
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", ln)
                if m:
                    keys.add(m.group(1))
            missing = [k for k in REQUIRED_KEYS if k not in keys]
            if missing:
                problems.append(f"_TEMPLATE.md 演示 frontmatter 缺必填键 {missing}")
            unknown = sorted(keys - KNOWN_KEYS)
            if unknown:
                problems.append(f"_TEMPLATE.md 演示 frontmatter 含规则外键 {unknown}")
    return problems


def run_validation(root=None, node_scope=None, manifest_path=None,
                   schema_path=None, template_path=None):
    """校验卡目录 ↔ manifest 一致性 (可复用入口, doctor 第 9 类调用)。

    node_scope: None=全量; 否则为节点名集合 (缺卡检查限定该范围, 孤儿/坏卡仍全局失败)。
    返回 dict(ok, violations, advisories, card_count, total_creative, cards)。"""
    root = os.path.abspath(root or ROOT)
    manifest_path = manifest_path or os.path.join(root, "tests", "mode_manifest.json")
    schema_path = schema_path or os.path.join(root, "knowledge_base", "mode_cards", "SCHEMA.md")
    template_path = template_path or os.path.join(root, "knowledge_base", "mode_cards", "_TEMPLATE.md")
    cards_root = os.path.join(root, "knowledge_base", "mode_cards")

    violations, advisories = [], []
    manifest = load_manifest(manifest_path, violations)
    manifest_nodes = manifest["nodes"] if manifest else {}
    total_creative = manifest.get("total_creative") if manifest else None

    # manifest 完整性: 单一事实源必须覆盖全部 10 个模式下拉节点
    if manifest is not None:
        for node in CATALOG.values():
            if node not in manifest_nodes:
                violations.append(f"manifest.nodes 缺少节点 '{node}' "
                                  f"(单一事实源须覆盖全部 10 个模式下拉节点; "
                                  f"重跑 tools/dump_mode_manifest.py 刷新)")

    violations.extend(selfcheck_docs(schema_path, template_path))

    cards_files = collect_card_files(cards_root, violations)
    seen_mode_ids, seen_node_name, cards = {}, {}, []
    for slug, fp in cards_files:
        c = validate_card(slug, fp, manifest_nodes, violations, advisories,
                          seen_mode_ids, seen_node_name)
        if c:
            cards.append(c)

    # 缺卡检查 (node_scope 限定; manifest 缺节点的完整性问题已在上面报过, 此处跳过)
    scope = sorted(node_scope) if node_scope else sorted(CATALOG.values())
    missing_by_node = {}
    for node in scope:
        mnode = manifest_nodes.get(node)
        if not isinstance(mnode, dict):
            continue
        have = {c["name"] for c in cards if c["node"] == node}
        missing = [opt for opt in mnode.get("creative", []) if opt not in have]
        if missing:
            missing_by_node[node] = missing
            slug = NODE_TO_SLUG[node]
            for opt in missing:
                violations.append(f"缺卡: {node} / {opt} (目录 {slug}/{opt} 待建, "
                                  f"name 须与下拉枚举逐字一致)")
    card_count = len(cards_files)
    ok = not violations
    return {"ok": ok, "violations": violations, "advisories": advisories,
            "card_count": card_count, "total_creative": total_creative,
            "cards": cards, "missing_by_node": missing_by_node}


def index_drift(root, cards, total_creative):
    """现有 INDEX.md/index.json 与将生成内容逐字节比对; 返回漂移问题列表。"""
    cards_root = os.path.join(os.path.abspath(root), "knowledge_base", "mode_cards")
    problems = []
    for fname, content in (("INDEX.md", build_index_md(cards, total_creative)),
                           ("index.json", build_index_json(cards, total_creative))):
        p = os.path.join(cards_root, fname)
        if not os.path.exists(p):
            problems.append(f"索引文件缺失: knowledge_base/mode_cards/{fname} "
                            f"(先运行一次写入模式生成)")
            continue
        with open(p, "rb") as f:
            actual = f.read()
        if actual != content.encode("utf-8"):
            problems.append(f"索引漂移: knowledge_base/mode_cards/{fname} 与重算结果逐字节不一致 "
                            f"(重跑写入模式刷新)")
    return problems


def print_report(res, root, drift=None):
    nodes_line = " / ".join(
        f"{node} {len(res['missing_by_node'].get(node, []))}缺"
        for node in sorted(CATALOG.values()))
    print("=" * 66)
    print(f"  sync_mode_index 校验报告 (root={root})")
    print("=" * 66)
    print(f"  卡文件: {res['card_count']} / manifest.total_creative: {res['total_creative']}")
    if res["total_creative"] is not None:
        print(f"  逐节点: {nodes_line}")
    if res["advisories"]:
        print(f"  advisories ({len(res['advisories'])}):")
        for a in res["advisories"]:
            print(f"    ~ {a}")
    if res["violations"]:
        print(f"  违例 ({len(res['violations'])}):")
        for v in res["violations"]:
            print(f"    ! {v}")
    if drift:
        print(f"  漂移 ({len(drift)}):")
        for d in drift:
            print(f"    ! {d}")
    print("-" * 66)
    if res["violations"] or drift:
        print("  结果: FAIL (exit 1)")
        return 1
    print("  结果: PASS (exit 0)")
    return 0


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description="模式卡目录校验 + 索引生成 (零 yaml 依赖)")
    ap.add_argument("--check", action="store_true",
                    help="只验不写, 并对现有 INDEX.md/index.json 逐字节漂移比对")
    ap.add_argument("--node", action="append", default=[], metavar="Node",
                    help="子集校验节点 (可重复; 缺卡检查限定该节点; 不写索引)")
    ap.add_argument("--root", default=ROOT, help="仓库根 (默认为 tools/ 上级)")
    ap.add_argument("--manifest", default=None, help="manifest 路径覆盖 (默认 tests/mode_manifest.json)")
    ap.add_argument("--schema", default=None, help="SCHEMA.md 路径覆盖")
    ap.add_argument("--template", default=None, help="_TEMPLATE.md 路径覆盖")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    res = run_validation(root, node_scope=set(args.node) or None,
                         manifest_path=args.manifest, schema_path=args.schema,
                         template_path=args.template)

    write = not args.check and not args.node
    drift = None
    if args.check and not args.node and res["ok"]:
        drift = index_drift(root, res["cards"], res["total_creative"])

    if write and res["ok"]:
        cards_root = os.path.join(root, "knowledge_base", "mode_cards")
        for fname, content in (("INDEX.md", build_index_md(res["cards"], res["total_creative"])),
                               ("index.json", build_index_json(res["cards"], res["total_creative"]))):
            with open(os.path.join(cards_root, fname), "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
        print(f"  索引已写入: {os.path.join(cards_root, 'INDEX.md')} / index.json")

    return print_report(res, root, drift)


if __name__ == "__main__":
    sys.exit(main())
