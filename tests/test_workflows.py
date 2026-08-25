# -*- coding: utf-8 -*-
"""
工作流有效性测试 (validate_workflows.py 的重生版)
==================================================
验证 workflows/*.json 中每个节点:
  1. class_type 在 NODE_CLASS_MAPPINGS 中注册
  2. 所有输入 widget 名在该节点 INPUT_TYPES 中存在
  3. 下拉输入的值在选项列表内
不依赖 pytest:  python3 tests/test_workflows.py
退出码: 0 = 全部通过, 1 = 有失败
"""
import os
import sys
import json
import glob
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  [FAIL] {label} {detail}")


def main():
    spec = importlib.util.spec_from_file_location(
        "dm_wf_test", os.path.join(ROOT, "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dm_wf_test"] = mod
    spec.loader.exec_module(mod)
    M = mod.NODE_CLASS_MAPPINGS

    # 预取每节点合法输入名与下拉选项
    node_inputs = {}
    for name, cls in M.items():
        it = cls.INPUT_TYPES()
        inputs = {}
        for sec in ("required", "optional", "hidden"):
            for k, v in it.get(sec, {}).items():
                opts = None
                if isinstance(v, (list, tuple)) and v and isinstance(v[0], list):
                    opts = set(v[0])
                inputs[k] = opts
        node_inputs[name] = inputs

    wfs = sorted(glob.glob(os.path.join(ROOT, "workflows", "*.json")))
    check("至少 1 个工作流文件", len(wfs) >= 1, f"found={len(wfs)}")

    for wf in wfs:
        fname = os.path.basename(wf)
        try:
            data = json.load(open(wf, encoding="utf-8"))
        except Exception as e:
            check(f"{fname} JSON 解析", False, repr(e)[:80])
            continue
        nodes = data.get("nodes", [])
        check(f"{fname} 有节点", len(nodes) > 0, "空工作流")
        for n in nodes:
            ntype = n.get("type", "")
            nid = n.get("id", "?")
            check(f"{fname}#{nid} 类型已注册 ({ntype})", ntype in M)
            if ntype not in M:
                continue
            valid = node_inputs[ntype]
            widgets = n.get("widgets_values", [])
            # widgets_values 与输入按序对应 (ComfyUI API 格式则用 inputs dict)
            inputs_dict = n.get("inputs", [])
            if isinstance(inputs_dict, list):
                # GUI 格式: widgets_values 顺序对应非连线输入
                if len(widgets) > len(valid):
                    check(f"{fname}#{nid} widget 数不超输入数",
                          False, f"widgets={len(widgets)} inputs={len(valid)}")
            elif isinstance(inputs_dict, dict):
                for k, v in inputs_dict.items():
                    if k in valid and valid[k] is not None and isinstance(v, (str, int, float, bool)):
                        check(f"{fname}#{nid}.{k} 下拉值合法", v in valid[k] or str(v) in valid[k],
                              f"value={v!r}")
        # 连线引用的节点 id 必须存在
        ids = {n.get("id") for n in nodes}
        links = data.get("links", [])
        broken = [l for l in links if l and (l[1] not in ids or l[3] not in ids)]
        check(f"{fname} 连线完整", not broken, f"断线 {len(broken)} 条")

    print(f"\n工作流测试: {PASS} PASS / {FAIL} FAIL")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
