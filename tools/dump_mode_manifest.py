# -*- coding: utf-8 -*-
"""
tools/dump_mode_manifest.py — 模式卡 manifest 单一事实源 (V16.3.0 批次2 / 设计 §1)
================================================================================
黑盒加载本包 (与 tests/test_load_isolation.py 同法: importlib spec + pop legacy 环境变量),
从 tests/test_all_modes.py 的 MODE_KEY 提取模式下拉口径锚点 (AST 解析, 不执行测试),
对全部模式节点逐个读取真实 INPUT_TYPES() 枚举, 按审计规则排除非创作选项后
落盘 tests/mode_manifest.json。

审计规则 (排除 = 非创作选项, 逐条给理由, 理由内附实现文件+分支证据):
  R1 判定类: "🎲 随机" — 运行时 random.choice() 改选其余创作模式, 无独立创作行为 (10 节点各 1)。
  R2 聚合/自动批量类: 选项产物是其同节点兄弟创作选项产物的机械组合 (拼接/全量批量),
      且均为下拉默认值 — Art"全部(...)" / Sound"全部(...)" / VideoRouter"全部生成" /
      Archive"自动保存全部资产"。
  R3 纯别名重复: 下拉内逐字重复项 — 出现即硬失败上报 (当前 258 个选项无重复)。

诚实阀门: 审计后 total_creative 与 README 口径不符时不凑数 — manifest 落盘真实数字,
stdout 显著打印审计差异, 由编排者裁决口径。

用法:
  python tools/dump_mode_manifest.py                  # 生成 tests/mode_manifest.json + 审计表
  python tools/dump_mode_manifest.py --verify [path]  # 重探针三方核对 (全过 exit 0)
  可选: --schema <p> / --template <p> (verify 时校验两文件存在且非空, 默认标准路径)

确定性: 输出不含时间戳; 枚举顺序 = live INPUT_TYPES 顺序; 节点顺序 = MODE_KEY 锚点顺序。
退出码: 0 = 通过 / 1 = 核对失败 / 2 = 环境性错误 (锚点缺失/枚举读取失败)。
"""
import argparse
import ast
import importlib.util
import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)
DEFAULT_MANIFEST = os.path.join(ROOT, "tests", "mode_manifest.json")
DEFAULT_SCHEMA = os.path.join(ROOT, "knowledge_base", "mode_cards", "SCHEMA.md")
DEFAULT_TEMPLATE = os.path.join(ROOT, "knowledge_base", "mode_cards", "_TEMPLATE.md")

FINAL_ALIAS = "DirectorMasterFinal"
EXPECTED_REGISTRY = 20   # 17 超级 + Final 别名 + 长篇接入 + 生态预案 (批次5: +DirectorMasterEcoManager)
EXPECTED_SUPER = 19      # 注册表减 Final 别名 = 17 超级 + 长篇接入 + 生态预案
README_CREATIVE_CLAIM = 247  # README "质量验证" 节的创作模式口径 (诚实阀门对账基准)
RANDOM_OPTION = "🎲 随机"

# 节点 → 聚合模块 (供排除理由引用, 与 __init__.py _NODE_SPECS 同源)
_NODE_MODULE = {
    "DirectorMasterScript": "aggregator/script_studio.py",
    "DirectorMasterVibe": "aggregator/vibe_studio.py",
    "DirectorMasterArt": "aggregator/art_master.py",
    "DirectorMasterSound": "aggregator/sound_master.py",
    "DirectorMasterCinematic": "aggregator/cinematic_studio.py",
    "DirectorMasterCharacters": "aggregator/characters_master.py",
    "DirectorMasterAsset": "aggregator/asset_master.py",
    "DirectorMasterRouter": "aggregator/router.py",
    "DirectorMasterVideoRouter": "aggregator/video_router_master.py",
    "DirectorMasterArchive": "aggregator/archive_master.py",
    "DirectorMasterReview": "aggregator/review_engine.py",
}

# R2 聚合/自动批量排除表: (节点, 选项) → 理由 (含实现文件+分支证据)
AGGREGATE_EXCLUSIONS = {
    ("DirectorMasterArt", "全部(美术指导+空间一致性+空间布局)"):
        "聚合/自动批量项: 下拉默认值; 输出为 美术指导+空间一致性+空间布局 3 个创作模式模板的"
        "依次拼接, 无独立创作内容 (aggregator/art_master.py build() 的 _ART_ALL 分支: 三模板相加)",
    ("DirectorMasterSound", "全部(声音设计+音乐配乐+声音层+沉默)"):
        "聚合/自动批量项: 下拉默认值; 输出为 声音设计+音乐配乐+声音层+沉默 4 个创作模式模板的"
        "依次拼接 (aggregator/sound_master.py _do_build() 的 _SND_ALL 分支: 四模板相加)",
    ("DirectorMasterVideoRouter", "全部生成"):
        "聚合/自动批量项: 下拉默认值; 全量批量通道 targets=全部 5 个视频模型, 产物为 5 个单模型"
        "创作选项的并集 (aggregator/video_router_master.py build(): if target==\"全部生成\": "
        "targets=VIDEO_ROUTER_MODES)",
    ("DirectorMasterArchive", "自动保存全部资产"):
        "聚合/自动批量项: 下拉默认值; 写盘资产集合 = 保存剧本+保存分镜+保存视频请求+保存制作手册 "
        "4 项的并集再加核心数据包 JSON (与 '版本提交' 共享同一集合, 仅少版本库提交), "
        "为节点默认自动通道而非独立创作模式 (aggregator/archive_master.py build(): "
        "mode in ('自动保存全部资产','版本提交') 分支)",
}


class AuditError(Exception):
    """环境性错误 (锚点/枚举/注册表结构不符合预期) → exit 2。"""


# ---------------------------------------------------------------- 锚点与加载
def get_mode_widgets(tests_dir=None):
    """从 tests/test_all_modes.py 的 MODE_KEY 提取 节点→模式下拉widget 锚点。

    AST 解析 (不执行测试代码); MODE_KEY 值为 (widget 名, 运行时参数) 元组,
    取首元素常量。返回 dict, 顺序 = 测试源码顺序 (10 对)。"""
    tests_dir = tests_dir or os.path.join(ROOT, "tests")
    path = os.path.join(tests_dir, "test_all_modes.py")
    if not os.path.exists(path):
        raise AuditError("锚点文件缺失: tests/test_all_modes.py")
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "MODE_KEY":
                    d = node.value
                    if not isinstance(d, ast.Dict):
                        raise AuditError("test_all_modes.py MODE_KEY 结构异常 (非字面 dict)")
                    out = {}
                    for k, v in zip(d.keys, d.values):
                        if (isinstance(k, ast.Constant) and isinstance(v, ast.Tuple)
                                and v.elts and isinstance(v.elts[0], ast.Constant)):
                            out[k.value] = v.elts[0].value
                    if len(out) != 11:
                        raise AuditError(f"MODE_KEY 锚点解析出 {len(out)} 对 (期望 11 个模式下拉)")
                    return out
    raise AuditError("test_all_modes.py 中未找到 MODE_KEY 锚点")


def load_registry():
    """黑盒加载 __init__.py (与 tests/test_load_isolation.py 同法)。

    返回 NODE_CLASS_MAPPINGS; legacy 兼容层不加载 (pop 环境变量)。"""
    os.environ.pop("DIRECTORMASTER_LEGACY_NODES", None)
    for p in (ROOT, os.path.dirname(ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(
        "_dm_manifest_probe", os.path.join(ROOT, "__init__.py"))
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["_dm_manifest_probe"] = pkg
    spec.loader.exec_module(pkg)
    return pkg.NODE_CLASS_MAPPINGS


def check_registry_shape(mappings):
    """校验 20 注册 / 19 超级 (含长篇接入+生态预案) / Final 别名同源; 返回超级类名集合。"""
    if len(mappings) != EXPECTED_REGISTRY:
        raise AuditError(f"注册表 {len(mappings)} 个节点 (期望 {EXPECTED_REGISTRY})")
    if mappings.get(FINAL_ALIAS) is not mappings.get("DirectorMasterSummary"):
        raise AuditError("DirectorMasterFinal 不是 DirectorMasterSummary 的同源别名")
    supers = set(mappings) - {FINAL_ALIAS}
    if len(supers) != EXPECTED_SUPER:
        raise AuditError(f"超级类 {len(supers)} 个 (期望 {EXPECTED_SUPER})")
    return supers


def live_options(mappings, node, widget):
    """读取某节点某模式下拉的 live 枚举 (真实 INPUT_TYPES, 顺序保持)。"""
    if node not in mappings:
        raise AuditError(f"节点 {node} 不在注册表中")
    it = mappings[node].INPUT_TYPES()
    req = it.get("required", {})
    if widget not in req:
        raise AuditError(f"{node} 的 INPUT_TYPES 无模式下拉 widget '{widget}'")
    entry = req[widget]
    if not entry or not isinstance(entry[0], (list, tuple)):
        raise AuditError(f"{node}.{widget} 枚举结构异常: {type(entry[0]).__name__}")
    return [str(o) for o in entry[0]]


# ---------------------------------------------------------------- 审计规则
def _random_reason(node):
    mod = _NODE_MODULE.get(node, "aggregator/<未知模块>")
    return (f"判定类非创作选项: 运行时 random.choice() 随机改选该节点其余创作模式, "
            f"自身无独立创作行为 ({mod} 模式分发分支 _R=\"{RANDOM_OPTION}\")")


def build_node_record(node, widget, options):
    """按审计规则把一个节点的 live 枚举拆成 creative + excluded (审计表)。"""
    if len(options) != len(set(options)):
        dupes = sorted({o for o in options if options.count(o) > 1})
        raise AuditError(f"{node}: 下拉出现逐字重复项 (R3 别名规则须人工审计): {dupes}")
    excluded = []
    for opt in options:
        if opt == RANDOM_OPTION:
            excluded.append({"option": opt, "reason": _random_reason(node)})
        elif (node, opt) in AGGREGATE_EXCLUSIONS:
            excluded.append({"option": opt, "reason": AGGREGATE_EXCLUSIONS[(node, opt)]})
    ex_set = {e["option"] for e in excluded}
    creative = [o for o in options if o not in ex_set]
    return {"widget": widget, "options": list(options),
            "creative": creative, "excluded": excluded}


def build_manifest(mappings=None):
    """构建完整 manifest dict (version/nodes/total_creative)。"""
    if mappings is None:
        mappings = load_registry()
    check_registry_shape(mappings)
    widgets = get_mode_widgets()
    nodes = {}
    for node, widget in widgets.items():
        nodes[node] = build_node_record(node, widget, live_options(mappings, node, widget))
    total = sum(len(rec["creative"]) for rec in nodes.values())
    return {"version": 1, "nodes": nodes, "total_creative": total}


# ---------------------------------------------------------------- 输出
def print_audit(manifest):
    nodes = manifest["nodes"]
    total = manifest["total_creative"]
    raw_total = sum(len(rec["options"]) for rec in nodes.values())
    ex_total = sum(len(rec["excluded"]) for rec in nodes.values())
    print("=" * 66)
    print("  模式卡 manifest 审计 (单一事实源: live INPUT_TYPES × 排除规则)")
    print("=" * 66)
    print(f"  {'节点':<28}{'widget':<10}{'options':>8}{'creative':>9}{'excluded':>9}")
    for node, rec in nodes.items():
        print(f"  {node:<28}{rec['widget']:<10}{len(rec['options']):>8}"
              f"{len(rec['creative']):>9}{len(rec['excluded']):>9}")
    print(f"  {'合计':<38}{raw_total:>8}{total:>9}{ex_total:>9}")
    print("-" * 66)
    for node, rec in nodes.items():
        for e in rec["excluded"]:
            print(f"  排除 [{node}] {e['option']}")
            print(f"         理由: {e['reason']}")
    print("-" * 66)
    print(f"  下拉枚举总数 {raw_total} (tests/test_all_modes.py 全模式回归口径 261)"
          f" → 排除 {ex_total} → total_creative = {total}")
    if total != README_CREATIVE_CLAIM:
        print()
        print("*" * 66)
        print(f"  ⚠ 诚实阀门触发: 审计后 total_creative = {total} != README 口径 "
              f"{README_CREATIVE_CLAIM} (差 {total - README_CREATIVE_CLAIM:+d})")
        print(f"  差异构成: {README_CREATIVE_CLAIM} = {raw_total} - 11×🎲随机 - 2×'全部(...)'拼接聚合"
              f" - 1×VideoRouter'全部生成' - 1×Archive'自动保存全部资产'")
        print("  (后两项为默认/自动批量通道, 产物为兄弟选项并集)。manifest 落盘真实数字, 不凑数;")
        print("  与 README 口径不符时由编排者裁决 (改文案或修订规则)。")
        print("*" * 66)


def write_manifest(manifest, path):
    """确定性落盘: 无时间戳, ensure_ascii=False, 2 空格缩进, 末尾换行。"""
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------- verify
def _check_docs(label, path, problems):
    if not os.path.exists(path):
        problems.append(f"{label} 文件缺失: {path}")
    elif not os.path.isfile(path):
        problems.append(f"{label} 路径不是文件: {path}")
    elif os.path.getsize(path) == 0:
        problems.append(f"{label} 文件为空: {path}")


def cmd_verify(manifest_path, schema_path, template_path):
    """重探针三方核对: live INPUT_TYPES × manifest × 审计规则重建 三方一致 + 文档件在场。"""
    problems = []
    print("=" * 66)
    print(f"  verify: {manifest_path}")
    print("=" * 66)

    # 1. manifest 存在且可解析
    if not os.path.exists(manifest_path):
        print("  [FAIL] manifest 不存在")
        return 1
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"  [FAIL] manifest 解析失败: {e!r}")
        return 1
    if manifest.get("version") != 1 or not isinstance(manifest.get("nodes"), dict):
        print("  [FAIL] manifest 结构异常 (version/nodes)")
        return 1
    print("  [OK] manifest 可解析 (version=1)")

    # 2. 重探针: 黑盒重新加载 + 锚点 + live 枚举重建
    try:
        mappings = load_registry()
        check_registry_shape(mappings)
        widgets = get_mode_widgets()
    except AuditError as e:
        print(f"  [FAIL] 重探针失败: {e}")
        return 1
    print(f"  [OK] 重探针: {EXPECTED_REGISTRY} 注册 / {EXPECTED_SUPER} 超级类 / Final 别名同源")

    # 3. 锚点一致性: manifest 节点集合与 widget 字段
    if set(manifest["nodes"]) != set(widgets):
        problems.append(f"manifest 节点集合 != 锚点集合: "
                        f"{sorted(set(manifest['nodes']) ^ set(widgets))}")
    for node, widget in widgets.items():
        rec = manifest["nodes"].get(node)
        if rec is not None and rec.get("widget") != widget:
            problems.append(f"{node}: manifest.widget={rec.get('widget')!r} != 锚点 {widget!r}")
    if not problems:
        print(f"  [OK] 节点集合与模式下拉 widget 与锚点一致 ({len(widgets)} 对)")

    # 4/5. 逐节点: live 枚举逐位一致 + 审计规则重建一致 + 分区计数
    total_live = 0
    for node, widget in widgets.items():
        rec = manifest["nodes"].get(node)
        if rec is None:
            continue
        try:
            opts = live_options(mappings, node, widget)
        except AuditError as e:
            problems.append(str(e))
            continue
        total_live += len(opts)
        if list(rec.get("options", [])) != opts:
            problems.append(f"{node}: manifest.options != live INPUT_TYPES 枚举 "
                            f"(manifest {len(rec.get('options', []))} vs live {len(opts)})")
            continue
        rebuilt = build_node_record(node, widget, opts)
        for key in ("widget", "options", "creative", "excluded"):
            if rec.get(key) != rebuilt[key]:
                problems.append(f"{node}: 字段 {key} 与审计规则重建结果不一致")
        creative, excluded = rec.get("creative", []), [e.get("option") for e in rec.get("excluded", [])]
        c_set, e_set = set(creative), set(excluded)
        if c_set & e_set:
            problems.append(f"{node}: creative 与 excluded 交集: {sorted(c_set & e_set)}")
        if c_set | e_set != set(opts) or len(creative) + len(excluded) != len(opts):
            problems.append(f"{node}: creative∪excluded != options (分区不完整)")
        if c_set - set(opts):
            problems.append(f"{node}: creative 含 live 枚举之外的项: {sorted(c_set - set(opts))}")
    _node_problems = [p for p in problems if p.split(":", 1)[0] in widgets]
    if not _node_problems:
        print(f"  [OK] {len(widgets)} 节点 live 枚举逐位一致 (合计 {total_live} 选项, 口径 261)"
              if total_live == 261 else
              f"  [OK] {len(widgets)} 节点 live 枚举逐位一致 (合计 {total_live} 选项)")

    # 6. 计数
    total_manifest = manifest.get("total_creative")
    total_rebuild = sum(len(rec.get("creative", [])) for rec in manifest["nodes"].values())
    if not isinstance(total_manifest, int) or total_manifest != total_rebuild:
        problems.append(f"total_creative={total_manifest} != Σcreative={total_rebuild}")
    else:
        print(f"  [OK] 计数一致: total_creative = {total_manifest}")

    # 7. 文档件在场且非空
    _check_docs("SCHEMA", schema_path, problems)
    _check_docs("TEMPLATE", template_path, problems)
    if not any(p.startswith("SCHEMA") or p.startswith("TEMPLATE") for p in problems):
        print(f"  [OK] SCHEMA/_TEMPLATE 在场且非空 ({schema_path} / {template_path})")

    # 结论 (诚实阀门提示)
    print("-" * 66)
    if problems:
        print(f"  verify 结果: {len(problems)} 项不一致:")
        for p in problems:
            print(f"    - {p}")
        print("  退出码 1")
        return 1
    print(f"  verify 结果: 全部通过 (exit 0); total_creative={total_manifest}"
          + ("" if total_manifest == README_CREATIVE_CLAIM else
             f" (诚实阀门: != README 口径 {README_CREATIVE_CLAIM}, 差异已在生成时审计上报)"))
    return 0


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="模式卡 manifest 单一事实源生成器 (生成 / --verify 三方核对)")
    ap.add_argument("--verify", nargs="?", const=DEFAULT_MANIFEST, default=None,
                    metavar="PATH",
                    help="核对模式: 重探针枚举与 manifest 三方核对 (默认路径 tests/mode_manifest.json)")
    ap.add_argument("--schema", default=DEFAULT_SCHEMA, help="SCHEMA.md 路径 (verify 校验在场非空)")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE, help="_TEMPLATE.md 路径 (verify 校验在场非空)")
    args = ap.parse_args(argv)

    if args.verify is not None:
        try:
            return cmd_verify(args.verify, args.schema, args.template)
        except Exception as e:  # 环境性错误兜底
            print(f"[dump_mode_manifest] verify 环境性错误: {e!r}")
            return 2

    # 生成模式
    try:
        mappings = load_registry()
        manifest = build_manifest(mappings)
    except AuditError as e:
        print(f"[dump_mode_manifest] 审计环境错误: {e}")
        return 2
    write_manifest(manifest, DEFAULT_MANIFEST)
    print_audit(manifest)
    print(f"\n  manifest 已写入: {DEFAULT_MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
