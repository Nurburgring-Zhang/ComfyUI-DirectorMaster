# -*- coding: utf-8 -*-
"""修复 legacy 文件末尾 disabled NODE_CLASS_MAPPINGS/NODE_DISPLAY_NAME_MAPPINGS 块的语法错误。
问题: "# NODE_CLASS_MAPPINGS (disabled...) = {" 只注释了首行, 字典体未注释导致 SyntaxError。
修复: 把 disabled 块内的孤立字典行也注释掉。"""
import os, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = "."
fixed = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in ("__pycache__", ".git")]
    for f in fn:
        if not f.endswith(".py"):
            continue
        p = os.path.join(dp, f)
        with open(p, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        out = []
        in_block = False
        changed = False
        for line in lines:
            s = line.strip()
            if s.startswith("# NODE_CLASS_MAPPINGS (disabled") or \
               s.startswith("# NODE_DISPLAY_NAME_MAPPINGS (disabled"):
                in_block = True
                out.append(line)
                continue
            if in_block:
                # 字典体行: "X": ..., 或 "X": "..." 或 }
                if s == "}" or (s.startswith('"') and (s.endswith(",") or s.endswith('",'))):
                    out.append("# " + line)
                    changed = True
                    if s == "}":
                        in_block = False
                    continue
                elif s.startswith('"'):
                    out.append("# " + line)
                    changed = True
                    continue
                elif s == "":
                    out.append(line)
                    continue
                else:
                    in_block = False
                    out.append(line)
                    continue
            out.append(line)
        if changed:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(out) + "\n")
            fixed.append(p)

print("修复文件数:", len(fixed))
for p in fixed:
    print(" ", p)
